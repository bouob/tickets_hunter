# ibon 多出票券數量除錯分析報告

**分析日期**：2025-10-18
**分析工具**：/speckit.debug
**問題簡稱**：ibon-multiple-tickets
**嚴重性**：P1（高）- 影響購票正確性

---

## 問題概述

| 項目 | 內容 |
|------|------|
| **問題現象** | 設定檔中只配置 `ticket_number: 1`，但在結帳頁面 (UTK0206) 顯示 **2 張票券**，總金額 $11,600（2 × 5,800） |
| **功能階段** | 階段 6（票券數量選擇）→ 階段 10（訂單確認） |
| **涉及平台** | iBon (NoDriver 版本) |
| **涉及 URL** | https://orders.ibon.com.tw/application/UTK02/UTK0201_001.aspx?PERFORMANCE_ID=B0A4TTSS&GROUP_ID=10&PERFORMANCE_PRICE_AREA_ID=B0A4TTTP |
| **相關檔案** | - `src/nodriver_tixcraft.py:10587` (`nodriver_ibon_ticket_number_auto_select`) - `manual_logs.txt` 行 109-116 - `ibon-UTK0201_001.html` (座位/數量頁) - `ibon-UTK0206.html` (結帳頁) |

### 時序分析

1. **行 109-116 (logs)**: 票券數量選擇
   ```
   NoDriver ibon_ticket_number_auto_select started
   ticket_number: 1
   Ticket number selection result: {'success': False, 'error': 'No ticket SELECT found'}
   [TICKET] Failed: No ticket SELECT found

   NoDriver ibon_ticket_number_auto_select started
   ticket_number: 1
   Ticket number selection result: {'success': True, 'set_value': '1'}
   [TICKET] Set to: 1
   ```
   - **第一次嘗試失敗**：找不到 SELECT 元素
   - **第二次嘗試成功**：成功設定為 1

2. **行 140 (logs)**: 最終結帳頁面
   ```
   https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
   Reached checkout page - ticket purchase successful!
   ```

3. **HTML 分析** (`ibon-UTK0206.html`)：
   - 結帳頁面顯示 **2 張票券**，各 $5,800
   - 總計：$11,600（應該是 $5,800）
   - 兩張票分別是：
     - 座位 D04排-21號，福利套組
     - 座位 D05排-20號，福利套組

---

## Spec 檢查結果

### 相關功能需求

| 需求 ID | 需求內容 | 符合度 | 分析 |
|---------|---------|--------|------|
| **FR-027** | 系統必須偵測票券數量輸入類型（下拉選單、文字框、加減按鈕、價格清單） | ✅ | 成功偵測到 `table.rwdtable select.form-control-sm` |
| **FR-028** | 系統必須將票券數量設為 settings.json 配置的值 | ❌ | 設定為 1，但結帳顯示 2 張 |
| **FR-030** | 系統必須在繼續前驗證票券數量設定正確 | ❌ | 無驗證邏輯，設定完成後直接提交 |

### 相關成功標準

| 標準 ID | 標準內容 | 目標 | 現狀 | 達標？ |
|---------|---------|------|------|-------|
| **SC-006** | 票券數量設定成功率 90% 以上 | 90% | ~50%（第一次失敗，第二次成功，但最終結果錯誤） | ❌ |

### 核心設計原則檢查

| 原則 | 檢查項目 | 結果 | 備註 |
|------|---------|------|------|
| **配置驅動架構** | 票券數量是否從 `config_dict["ticket_number"]` 讀取 | ✅ | 正確讀取配置值 1 |
| **三層回退策略** | 是否實作回退 (找不到 SELECT → 重試 → 失敗時降級) | ⚠️ | 有重試，但無降級邏輯 |
| **設定驗證** | 是否驗證最終設定值與配置一致 | ❌ | **缺失**：無驗證邏輯 |

---

## 根因分析

### 主要原因：**第一次票券數量選擇失敗，座位被"雙選"**

**假說**：
1. **首次進入 UTK0201_001 頁面時** (行 109-112)
   - 頁面剛載入，DOM 結構未完全穩定
   - `nodriver_ibon_ticket_number_auto_select()` 查詢 SELECT 元素失敗
   - 並未進行票券數量設定
   - 系統繼續進行驗證碼流程

2. **座位被"重複選擇"的機制**：
   - iBon 的 UTK0201 頁面有兩層選擇邏輯：
     1. **HTML SELECT 元素**：控制每個區域的購買數量
     2. **座位映射邏輯**：後端根據前端請求進行座位自動分配
   - 當票券數量 SELECT 未設定時，系統可能使用**預設值或前一次的值**
   - 後端自動分配座位時，分配了 2 張座位

3. **為什麼第一次失敗**：
   - 檢查 HTML (行 106)：
     ```html
     <select name="ctl00$ContentPlaceHolder1$DataGrid$ctl02$AMOUNT_DDL"
             id="ctl00_ContentPlaceHolder1_DataGrid_ctl02_AMOUNT_DDL"
             class="form-control form-control-sm">
       <option value="0">0</option>
       <option value="1">1</option>
       <option value="2">2</option>
       <option value="3">3</option>
       <option value="4">4</option>
     </select>
     ```
   - **分析**：這是 **ASP.NET 格式**的 SELECT，不是 `table.rwdtable select.form-control-sm`
   - 代碼在行 10611 查詢 `table.rwdtable select.form-control-sm`，找不到
   - 在行 10614-10615 回退到 `table.table select[name*="AMOUNT_DDL"]`
   - 但此時可能頁面還未完全載入，SELECT 被 Shadow DOM 或其他 DOM 障礙隱藏

### 次要原因：**缺少設定驗證與重試邏輯**

1. **無驗證邏輯**：
   - 函數返回 `is_ticket_number_assigned = True`，但未確認實際 SELECT 值是否改變
   - 沒有讀回 SELECT 元素的當前值進行驗證

2. **無強制重試**：
   - 在主程序中，第一次失敗後沒有主動重試
   - 系統直接進行驗證碼流程

3. **無頁面穩定性檢查**：
   - 沒有等待 DOM 完全穩定後再執行 SELECT 操作
   - 只使用固定延遲 (行 10598)

---

## 憲法合規性檢查

### 違反項目（P0/P1/P2）

| 原則 | 項目 | 嚴重性 | 說明 |
|------|------|--------|------|
| **V. 設定驅動開發** | 配置值與實際執行值不一致 | **P1** | 配置 `ticket_number: 1`，但購票數量為 2。用戶無法控制購買數量。 |
| **VI. 測試驅動穩定性** | 缺少設定驗證測試 | **P1** | 無法檢驗設定是否生效，導致購票結果錯誤 |
| **III. 三問法則** | "有更簡單的方法嗎？" 未應用 | **P2** | 回退策略過於複雜，且失敗時無降級機制 |

### 通過項目

- ✅ **I. NoDriver First**：正確使用 NoDriver 版本
- ✅ **II. 資料結構優先**：正確讀取 `config_dict["ticket_number"]`
- ✅ **IV. 單一職責**：函數職責清晰（票券數量選擇）

---

## 代碼結構與定位檢查

### 函數定位

| 函數 | 檔案:行號 | 狀態 | 完整度 |
|------|----------|------|--------|
| `nodriver_ibon_ticket_number_auto_select` | `src/nodriver_tixcraft.py:10587` | ✅ 存在 | 核心邏輯完整，但缺驗證 |
| Chrome 版本 `ibon_ticket_number_auto_select` | `src/chrome_tixcraft.py:4688` | ✅ 存在 | 可作為參考實作 |

### 功能完整度

根據 `structure.md`，iBon NoDriver 平台的完整度評分：
- ✅ 區域選擇：完整
- ✅ 座位分配：完整
- ⚠️ **票券數量選擇**：部分完整（缺驗證邏輯）

### 相似問題搜尋

在 `debugging_methodology.md` 的常見問題中：
- 類似問題：「元素查詢失敗後無重試」
- 建議解決方案：「增加 DOM 穩定性檢查 + 驗證邏輯」

---

## 已知問題與解決方案比對

### 常見問題檢查清單

| 問題 | 檢查項目 | 結果 | 備註 |
|------|---------|------|------|
| **DOM 元素序列化** | SELECT 元素是否在 Shadow DOM 中 | ⚠️ | HTML 顯示 SELECT 在普通 DOM 中，但首次查詢失敗 |
| **頁面載入時機** | 是否等待 Angular 載入完成 | ❌ | 無 Angular 等待邏輯（iBon 是 Angular SPA） |
| **查詢選擇器組合** | 是否使用多個備選查詢器 | ✅ | 有 2 個備選查詢器，但順序可能有問題 |
| **Disabled 按鈕檢測** | 是否過濾 disabled 元素 | ✅ | 無相關邏輯（選擇框不應被 disabled） |

### **已驗證的解決方案**

對應 Chrome 版本 (`ibon_ticket_number_auto_select` 行 4688)：
```python
# Chrome 版本的成功模式
- 嘗試通過 XPath 找 SELECT
- 多重選擇器備選方案
- 設定值後進行驗證
```

**但 NoDriver 版本缺少**：
- ❌ 設定後的驗證讀回
- ❌ 失敗時的重試邏輯
- ❌ DOM 穩定性等待

---

## 跨平台與版本檢查

### Chrome vs NoDriver 版本差異

| 功能 | Chrome 版本 | NoDriver 版本 | 差異 |
|------|-----------|-------------|------|
| SELECT 查詢 | 使用 Selenium Select | 使用 JavaScript evaluate | 不同方式 |
| 驗證邏輯 | 有讀回驗證 | ❌ **無驗證** | **差異點** |
| 重試邏輯 | 失敗時重試 | 無主動重試 | **差異點** |
| 頁面等待 | 使用 WebDriverWait | 固定延遲 | 不同強度 |

### 依賴關係與相容性

- ✅ 不影響其他平台：此修復僅影響 iBon 平台
- ✅ 不影響其他功能：票券數量選擇是獨立邏輯
- ✅ 無迴圈依賴：無相關

---

## 嚴重性與優先度評估

### 嚴重性判斷

- **P1（高優先度）**：
  - 違反 **FR-028**（票券數量必須符合配置）
  - 直接導致 **購票結果錯誤**（購了 2 張而非 1 張）
  - 影響 **所有 iBon 平台的購票**
  - 無法達到 **SC-006**（90% 成功率）

### 優先度排序

1. **P0（立即）**：增加設定驗證邏輯
2. **P1（高）**：增加 DOM 穩定性等待
3. **P1（高）**：增加失敗重試機制
4. **P2（中）**：與 Chrome 版本同步

---

## 修復建議

### 優先級 P0 修復（必須）

#### **修復 1：增加設定驗證邏輯**

**涉及檔案**：`src/nodriver_tixcraft.py:10587`

**修復方向**：
在設定 SELECT 值後，立即讀回驗證設定是否生效

**具體建議**：
```python
# 行 10646-10654 之後新增
// 在設定值之後新增驗證邏輯：
// ✅ 設定 SELECT 值
select.value = "{ticket_number}";
select.dispatchEvent(new Event('change', {{bubbles: true}}));

// 新增：讀回驗證
const finalValue = select.value;
if (finalValue !== "{ticket_number}") {{
    return {{success: false, error: "Value verification failed"}};
}}
return {{success: true, set_value: "{ticket_number}", verified: true}};
```

**相關 Spec**：FR-028, FR-030
**相關憲法**：V. 設定驅動開發、VI. 測試驅動穩定性
**優先級理由**：無驗證導致購票數量錯誤，影響用戶體驗

---

#### **修復 2：改進 DOM 穩定性檢查**

**涉及檔案**：`src/nodriver_tixcraft.py:10587`

**修復方向**：
等待 SELECT 元素確實存在後再進行操作

**具體建議**：
```python
# 在行 10608 之前新增等待邏輯
try:
    # 等待 SELECT 元素載入完成
    result = await tab.evaluate('''
        () => {
            return new Promise((resolve) => {
                const checkSelect = setInterval(() => {
                    let select = document.querySelector('table.rwdtable select.form-control-sm') ||
                                 document.querySelector('table.table select[name*="AMOUNT_DDL"]');
                    if (select) {
                        clearInterval(checkSelect);
                        resolve(true);
                    }
                }, 100);
                setTimeout(() => {
                    clearInterval(checkSelect);
                    resolve(false);
                }, 3000); // 最多等待 3 秒
            });
        }
    ''')
except Exception:
    pass
```

**相關 Spec**：FR-027（偵測類型）
**相關憲法**：III. 三問法則（更簡單方法）
**優先級理由**：解決首次失敗的根本原因

---

### 優先級 P1 修復（重要）

#### **修復 3：增加主程序重試邏輯**

**涉及檔案**：`src/nodriver_tixcraft.py:11189, 11778, 11862, 11997`

**修復方向**：
當票券數量選擇失敗時，進行重試

**具體建議**：
```python
# 在所有呼叫 nodriver_ibon_ticket_number_auto_select 的位置
# 改為：
for retry in range(3):  # 最多重試 3 次
    is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)
    if is_ticket_number_assigned:
        break
    if retry < 2:
        await asyncio_sleep_with_pause_check(config_dict, 0.5)  # 等待 500ms 後重試
```

**相關 Spec**：FR-060（重試策略）
**相關憲法**：VI. 測試驅動穩定性
**優先級理由**：提高穩定性，應對網路延遲

---

#### **修復 4：與 Chrome 版本功能同步**

**涉及檔案**：
- NoDriver：`src/nodriver_tixcraft.py:10587`
- Chrome：`src/chrome_tixcraft.py:4688`

**修復方向**：
檢查 Chrome 版本是否有額外邏輯，同步到 NoDriver

**參考實作**：
Chrome 版本的驗證邏輯可作為參考

**相關 Spec**：FR-028, FR-030
**相關憲法**：I. NoDriver First（完整功能奇偶性）

---

### 優先級 P2 修復（改進）

#### **修復 5：增加詳細日誌**

**涉及檔案**：`src/nodriver_tixcraft.py:10587`

**修復方向**：
增加更詳細的日誌，幫助後續除錯

**具體建議**：
```python
# 在驗證步驟中新增日誌
if show_debug_message:
    print(f"[TICKET DEBUG] Final SELECT value: {result_parsed.get('set_value')}")
    print(f"[TICKET DEBUG] Verification passed: {result_parsed.get('verified')}")
```

---

## 測試計畫

### 測試對象

| 項目 | 內容 |
|------|------|
| **函數** | `nodriver_ibon_ticket_number_auto_select` (src/nodriver_tixcraft.py:10587) |
| **平台** | iBon (NoDriver) |
| **階段** | 階段 6（票券數量）→ 階段 10（訂單確認） |

### 驗證標準（根據 SC-006）

- [ ] **基準測試**：票券數量設定成功率達 90% 以上
  - 執行 10 次自動化流程
  - 檢查每次結帳頁面顯示的票券數量是否與配置相符

- [ ] **驗證邏輯測試**：設定驗證無誤
  - 設定 `ticket_number: 1`，驗證結帳頁顯示 1 張
  - 設定 `ticket_number: 2`，驗證結帳頁顯示 2 張
  - 設定 `ticket_number: 3`，驗證結帳頁顯示 3 張

- [ ] **極限測試**：處理邊界情況
  - 設定數量超過可用數量時，是否正確降級
  - 首次選擇失敗時，是否正確重試

- [ ] **回歸測試**：不破壞其他功能
  - ✅ 座位選擇：確保仍能正確選擇座位
  - ✅ 驗證碼：確保驗證碼流程不受影響
  - ✅ 其他平台：確保 TixCraft/KKTIX 等不受影響

### 測試步驟

1. **環境準備**
   ```bash
   cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter"
   # 設定 settings.json: ticket_number = 1
   ```

2. **執行自動化**
   ```bash
   python -u nodriver_tixcraft.py --input src/settings.json
   ```

3. **驗證結果**
   - 檢查 `manual_logs.txt` 中的日誌
   - 檢查最終結帳頁面 HTML 的票券數量
   - 驗證 `is_ticket_number_assigned` 返回值

4. **分析日誌**
   ```bash
   grep -i "ticket_number\|TICKET" manual_logs.txt
   grep -i "success\|failed\|error" manual_logs.txt
   ```

### 迴歸測試清單

- [ ] iBon 平台其他流程（區域選擇、座位選擇）
- [ ] TixCraft 平台票券選擇
- [ ] KKTIX 平台票券選擇
- [ ] 其他平台的票券選擇邏輯

---

## 文件更新需求

- [ ] `docs/02-development/structure.md` - 更新 iBon 平台完整度評分
- [ ] `docs/08-troubleshooting/ibon_nodriver_fixes_*.md` - 記錄此次修復
- [ ] `docs/06-api-reference/nodriver_api_guide.md` - 更新 SELECT 元素查詢最佳實踐
- [ ] `docs/07-testing-debugging/debugging_methodology.md` - 記錄此類問題的通用解決方案
- [ ] `CHANGELOG.md` - 版本記錄（修復完成後）

---

## 相關資源

### Spec 檢查深入閱讀

- `specs/001-ticket-automation-system/spec.md` - 行 181-186（FR-027~030）
- 成功標準區塊：SC-006（票券數量設定 90% 成功率）

### 憲法相關條款

- `.specify/memory/constitution.md` - 原則 V、VI、III

### 代碼定位

- `src/nodriver_tixcraft.py:10587` - 主要函數
- `src/nodriver_tixcraft.py:11189, 11778, 11862, 11997` - 呼叫位置
- `src/chrome_tixcraft.py:4688` - Chrome 版本參考實作

### 除錯方法論

- `docs/07-testing-debugging/debugging_methodology.md` - Line 389-510 (Spec 驅動除錯)

---

## 建議的下一步

### 立即行動（P0 修復）

1. **實作修復 1**：增加設定驗證邏輯
   - 在 `src/nodriver_tixcraft.py:10646` 之後新增讀回驗證
   - 確保設定值與實際 SELECT 值一致

2. **實作修復 2**：改進 DOM 穩定性檢查
   - 在 `src/nodriver_tixcraft.py:10608` 之前新增等待邏輯
   - 等待 SELECT 元素確實存在後再操作

### 短期行動（P1 修復）

3. **實作修復 3**：增加主程序重試邏輯
   - 修改所有呼叫位置（行 11189, 11778, 11862, 11997）
   - 實作 3 次重試機制

4. **執行測試計畫**
   - 基準測試：10 次執行驗證成功率
   - 驗證邏輯測試：不同數量的配置測試
   - 迴歸測試：確保其他功能不受影響

### 長期改進（P2 修復）

5. **同步 Chrome 版本**
   - 比較兩個版本的差異
   - 確保功能奇偶性

6. **文件更新**
   - 更新 troubleshooting 文件
   - 記錄此類問題的解決方案

---

## 根本原因總結

```
問題鏈：
1. DOM 未穩定 → SELECT 查詢失敗 (首次)
2. 票券數量未設定 → 系統使用預設值或前值
3. 後端自動分配座位 → 分配 2 張座位
4. 無驗證邏輯 → 未發現設定失敗
5. 無重試邏輯 → 不能恢復

根本原因：設計缺陷
- 缺少設定驗證（違反 FR-030）
- 缺少失敗重試（違反 FR-060）
- 缺少 DOM 穩定性檢查（違反最佳實踐）
```

---

## 結論

此問題屬於 **設計缺陷導致的功能不完整**，而非個別 bug：

1. **設定驗證缺失** - 無法確認設定是否生效
2. **重試邏輯缺失** - 網路延遲導致首次失敗無法恢復
3. **DOM 穩定性檢查缺失** - 過於樂觀地假設 DOM 已準備好

**修復優先度**：根據 MVP 原則和憲法第 VI 條（測試驅動穩定性），建議立即實作 P0 和 P1 修復，確保票券數量設定的正確性和穩定性。

---

*分析完成時間*：2025-10-18 12:00 UTC+8
*分析工具*：/speckit.debug v1.0
*相關憲法版本*：1.1.0
*相關規格版本*：spec.md (2025-10-16 建立)
