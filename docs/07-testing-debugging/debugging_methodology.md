# 除錯方法論 - NoDriver 背景測試與 Shadow DOM 除錯指南

## 概述

本文件記錄了針對 NoDriver 平台的完整除錯方法論，特別是 Shadow DOM 相關問題的背景測試流程。此方法論基於 ibon disabled button 問題的實際解決經驗而建立。

## 目錄

1. [背景測試執行流程](#背景測試執行流程)
2. [Shadow DOM 除錯工具架構](#shadow-dom-除錯工具架構)
3. [除錯工具開發模式](#除錯工具開發模式)
4. [常見問題解決模式](#常見問題解決模式)
5. [除錯工具函數索引](#除錯工具函數索引)
6. [實際除錯案例研究](#實際除錯案例研究)

---

## 背景測試執行流程

### 1. 建立背景測試程序

**基本命令格式：**
```bash
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter\src"
python nodriver_tixcraft.py --input settings.json &
```

**命令列參數覆蓋設定（除錯用）：**
```bash
# 測試特定區域關鍵字
python nodriver_tixcraft.py --input settings.json --area_keyword "搖滾區" &

# 測試不同選擇模式
python nodriver_tixcraft.py --input settings.json --area_auto_select_mode "from bottom to top" &

# 組合測試：日期 + 區域
python nodriver_tixcraft.py --input settings.json --date_keyword "12/25" --area_keyword "VIP" &
```

**關鍵要點：**
- 使用 `&` 讓程序在背景執行
- 確保 `settings.json` 中 `webdriver_type` 設定為 `"nodriver"`
- 程序會持續運行並產生除錯日誌
- **命令列參數會覆蓋設定檔**，方便快速測試不同設定而不需修改 settings.json

### 2. 監控背景程序

**使用 BashOutput 工具：**
```bash
# 檢查程序狀態和新輸出
BashOutput(bash_id="程序ID")
```

**監控重點：**
- 程序執行狀態 (running/killed)
- 除錯標籤輸出 (`[NATIVE]`, `[JS SHADOW]`, `[CDP]`)
- 錯誤訊息和異常情況
- 元素搜尋結果和狀態

### 3. 程序終止和日誌分析

**程序終止：**
- 程序會自動重複執行除錯循環
- 可使用 `KillShell` 手動終止
- 觀察日誌中的重複模式

**日誌分析要點：**
- 搜尋成功/失敗的模式
- 元素狀態變化 (enabled/disabled)
- Unicode 編碼錯誤
- JavaScript 執行結果

---

## Shadow DOM 除錯工具架構

### 核心除錯函數

#### 1. `debug_shadow_dom_structure()`

**位置：** `nodriver_tixcraft.py:6815-6984`

**功能：**
- 完整分析 Shadow DOM 結構
- 使用 CDP (Chrome DevTools Protocol) 深度搜尋
- 穿透 closed shadowRoot
- 產生詳細的 DOM 結構報告

**主要特徵：**
```python
async def debug_shadow_dom_structure(tab, target_text="線上購票"):
    # CDP DOM 方法整合
    # 遞迴搜尋 Shadow DOM
    # 元素狀態檢測
    # 詳細日誌輸出
```

#### 2. `compare_search_methods()`

**位置：** `nodriver_tixcraft.py:6998-7251`

**功能：**
- 比較多種元素搜尋方法
- NoDriver native vs CDP vs JavaScript
- 搜尋結果一致性驗證
- 方法效能分析

**搜尋策略比較：**
- `tab.find()` - NoDriver 原生方法
- CDP DOM methods - Chrome DevTools Protocol
- JavaScript execution - 直接在頁面執行

#### 3. 整合搜尋流程

**在 `search_purchase_buttons_with_cdp()` 中整合：**
- 主要搜尋邏輯
- 除錯工具調用
- 多策略後備方案
- 結果驗證機制

---

## 除錯工具開發模式

### 除錯標籤系統

#### `[NATIVE]` 標籤 - NoDriver 原生搜尋
```
[NATIVE] Starting NoDriver native search for: 線上購票
[NATIVE] Enhanced tab.find() with disabled filtering for text: '線上購票'
[NATIVE] Found element on attempt 1: <button disabled="disabled"...>
[NATIVE] Is disabled: True
[NATIVE] Element on attempt 1 is disabled, trying to find next one
```

**監控要點：**
- 元素查找成功率
- disabled 狀態檢測
- 重試機制執行
- 最終點擊結果

#### `[JS SHADOW]` 標籤 - JavaScript Shadow DOM 搜尋
```
[JS SHADOW] Starting enhanced JavaScript Shadow DOM search...
[JS SHADOW] Enhanced JavaScript search failed: attempted relative import
```

**監控要點：**
- JavaScript 執行狀態
- Shadow DOM 穿透結果
- 錯誤訊息分析
- 元素發現數量

#### `[CDP]` 標籤 - Chrome DevTools Protocol
```
All CDP methods failed: 'cp950' codec can't encode character '\u274c'
```

**監控要點：**
- CDP 方法執行狀態
- Unicode 編碼問題
- DOM 節點遍歷結果
- 元素屬性擷取

### 多策略搜尋架構

```
1. NoDriver native search (`tab.find()`)
   ↓ (如果失敗或找到 disabled 元素)
2. CDP DOM methods (深度搜尋)
   ↓ (如果失敗)
3. JavaScript Shadow DOM penetration
   ↓ (如果失敗)
4. Enhanced JavaScript execution
```

---

## 常見問題解決模式

### 1. Unicode 編碼錯誤

**問題表現：**
```
'cp950' codec can't encode character '\u274c' in position 0: illegal multibyte sequence
```

**解決方案：**
- 移除除錯輸出中的 emoji 字符
- 使用純文字替代特殊符號
- 調整 Python 編碼設定

**程式碼範例：**
```python
# 避免在 Windows cp950 環境下使用 emoji
debug_message = f"Element found: {element_text}"  # 不使用 ✅ 等符號
```

### 2. Disabled 按鈕檢測和過濾

**問題表現：**
```
[NATIVE] Found element: <button disabled="disabled" class="btn btn-pink btn-buy">
[NATIVE] Is disabled: True
```

**解決策略：**
- 實作 disabled 屬性檢測
- 建立重試機制尋找 enabled 按鈕
- 記錄所有找到的按鈕狀態

**實作方法：**
```python
async def is_element_disabled(element):
    try:
        disabled_attr = await element.get_attribute('disabled')
        return disabled_attr is not None
    except:
        return False
```

### 3. Element 序列化問題

**問題表現：**
```
JavaScript search failed: object of type 'ExceptionDetails' has no len()
```

**解決方案：**
- 避免直接傳遞 Element 物件到 JavaScript
- 使用元素的字串表示或屬性
- 實作安全的元素序列化方法

### 4. Angular 應用程式載入時機

**問題表現：**
```
Waiting 0.95 seconds for Angular app to fully load...
```

**最佳實作：**
- 實作動態等待時間
- 檢測 Angular 應用程式初始化狀態
- 使用多次嘗試機制

---

## 除錯工具函數索引

### 主要函數位置

| 函數名稱 | 檔案位置 | 功能描述 |
|---------|----------|----------|
| `debug_shadow_dom_structure()` | `nodriver_tixcraft.py:6815-6984` | Shadow DOM 完整分析 |
| `compare_search_methods()` | `nodriver_tixcraft.py:6998-7251` | 多方法搜尋比較 |
| `search_purchase_buttons_with_cdp()` | `nodriver_tixcraft.py:主要搜尋函數` | 整合搜尋流程 |
| `search_and_click_with_nodriver_native()` | `nodriver_tixcraft.py:原生搜尋` | NoDriver 原生方法 |

### 輔助函數

| 函數名稱 | 功能描述 |
|---------|----------|
| `is_element_disabled()` | 檢測元素 disabled 狀態 |
| `safe_element_string()` | 安全的元素字串轉換 |
| `wait_for_angular_load()` | Angular 載入等待 |

### 除錯設定

**啟用除錯模式：**
```python
show_debug_message = config_dict["advanced"].get("verbose", False)
```

**除錯等級：**
- `verbose: true` - 完整除錯輸出
- `verbose: false` - 僅基本日誌

---

## 實際除錯案例研究

### 案例：ibon Disabled Button 問題

#### 問題描述
- ibon 購票頁面有兩個購票按鈕
- `tab.find()` 總是找到第一個 (disabled) 按鈕
- 需要找到第二個 (enabled) 按鈕

#### 問題分析流程

**步驟 1：初始問題發現**
```
Found 2 purchase buttons
Found 0 enabled buttons out of 2 total
No enabled buttons found
```

**步驟 2：建立除錯工具**
- 實作 `debug_shadow_dom_structure()` 進行深度分析
- 建立多策略搜尋比較系統
- 加入詳細的元素狀態記錄

**步驟 3：背景測試執行**
```bash
cd tickets_hunter/src
python nodriver_tixcraft.py --input settings.json &
```

**步驟 4：持續監控和分析**
- 使用 `BashOutput` 監控執行結果
- 分析重複執行模式
- 識別問題的根本原因

#### 發現的關鍵資訊

**按鈕結構分析：**
```html
<!-- 第一個按鈕 (disabled) -->
<button disabled="disabled" class="btn btn-pink btn-buy ng-tns-c57-1 ng-star-inserted">線上購票</button>

<!-- 第二個按鈕 (enabled) -->
<button class="btn btn-pink btn-buy ng-tns-c57-1 ng-star-inserted">線上購票</button>
```

**搜尋行為分析：**
- `tab.find()` 使用 DOM 順序搜尋
- 總是返回第一個匹配的元素
- 需要實作 disabled 過濾機制

#### 解決方案實作

**Enhanced Native Search with Disabled Filtering：**
```python
async def search_with_disabled_filtering(tab, text, max_attempts=5):
    for attempt in range(1, max_attempts + 1):
        element = await tab.find(text, timeout=1)
        if element:
            is_disabled = await is_element_disabled(element)
            if not is_disabled:
                return element
            else:
                print(f"[NATIVE] Element on attempt {attempt} is disabled, trying to find next one")
        else:
            break
    return None
```

#### 結果驗證

**背景測試執行結果：**
```
[NATIVE] Found element on attempt 1: <button disabled="disabled"...>
[NATIVE] Is disabled: True
[NATIVE] Element on attempt 1 is disabled, trying to find next one
[NATIVE] Found element on attempt 2: <button disabled="disabled"...>
[NATIVE] Is disabled: True
...
[NATIVE] Successfully clicked element via native method
```

**關鍵學習：**
1. `tab.find()` 在某些情況下有限制
2. 需要建立多層次的後備搜尋策略
3. 背景測試是發現間歇性問題的有效方法
4. 詳細的除錯日誌對問題分析至關重要

---

## 使用建議

### 何時使用背景測試

1. **間歇性問題** - 問題不是每次都出現
2. **時間敏感問題** - 需要長時間觀察的問題
3. **複雜 DOM 結構** - Shadow DOM 或動態載入內容
4. **多策略驗證** - 需要比較不同搜尋方法的效果

### 除錯工具開發最佳實作

1. **漸進式開發** - 從簡單的日誌開始，逐步增加複雜度
2. **標籤化輸出** - 使用清楚的標籤 (`[NATIVE]`, `[CDP]`, `[JS SHADOW]`)
3. **狀態追蹤** - 記錄元素的詳細狀態資訊
4. **錯誤處理** - 妥善處理 Unicode 和序列化問題

### 效能考量

1. **除錯模式切換** - 在生產環境中關閉詳細除錯
2. **資源使用** - 背景測試可能消耗較多系統資源
3. **日誌管理** - 定期清理除錯日誌檔案

---

## 未來改進方向

1. **自動化測試集成** - 將除錯工具整合到自動化測試流程
2. **視覺化除錯** - 建立 DOM 結構的視覺化工具
3. **效能監控** - 加入搜尋方法的效能比較
4. **智能錯誤恢復** - 根據錯誤類型自動選擇最佳策略

---

## Spec 驅動除錯方法

### 何時檢查 Spec

在以下情況務必檢查規格：

1. **功能異常**：行為與預期不符時
   - 例：日期選擇無法使用關鍵字匹配，直接進入自動模式
2. **測試失敗**：修復後測試仍失敗
   - 例：修復後元素互動成功率沒有達到 95% 標準
3. **設計決策**：不確定應該使用哪種策略
   - 例：不知道是否應該實作三層回退策略
4. **新平台支援**：實作新平台時的功能檢查清單

### Spec 檢查流程

#### 步驟 1：定位相關功能
- 識別問題屬於 12 階段中的哪一階段（見 `ticket_automation_standard.md`）
- 例：日期選擇問題 → 階段 4

#### 步驟 2：查閱功能需求
- 打開 `specs/001-ticket-automation-system/spec.md`
- 搜尋「功能需求」區塊
- 找到相關 FR 編號（例：FR-014 到 FR-019 為日期選擇）
- 確認修復符合所有相關需求

#### 步驟 3：驗證成功標準
- 在 `spec.md` 中搜尋「成功標準」區塊
- 找到相關 SC 編號（例：SC-002 為關鍵字匹配 90% 成功率）
- 確認修復後能達到標準
- 必要時設計測試來驗證成功標準

#### 步驟 4：檢查設計原則
- 打開 `spec.md` 中的「核心設計原則」區塊
- **配置驅動架構**：settings.json 是否可配置？
- **三層回退策略**：是否完整？（關鍵字 → 模式 → 手動）
- **函數分解原則**：函數是否遵循單一職責？

#### 步驟 5：檢查平台特定考量
- 在 `spec.md` 中搜尋「平台特定考量」區塊
- 確認修復未破壞該平台的特殊處理
- 例：iBon Shadow DOM、TicketPlus 展開面板

### Spec 檢查範例 1：日期選擇關鍵字無法匹配

**問題**：ibon 日期選擇關鍵字無法匹配，程式直接使用自動模式

**Spec 檢查**：
1. **FR-017**: "系統必須使用配置的關鍵字匹配日期，並支援多個分號分隔的關鍵字"
   - 檢查點：是否支援分號分隔的多關鍵字？
2. **FR-018**: "系統必須在關鍵字不匹配時回退到基於模式的選擇"
   - 檢查點：是否實作了回退邏輯？是否使用 auto_select_mode？
3. **SC-002**: "系統在可用時成功選擇使用者的第一選擇日期和區域（目標：基於關鍵字匹配的 90% 成功率）"
   - 檢查點：修復後關鍵字匹配成功率是否達到 90%？

**修正方向**：
- 檢查關鍵字匹配邏輯（區分大小寫？支援部分匹配？）
- 檢查 context 提取（是否正確提取日期與活動名稱？）
- 檢查回退邏輯（auto_select_mode 支援哪些模式？）
- 驗證修復後的成功率

### Spec 檢查範例 2：元素互動失敗

**問題**：年代售票票種選擇找不到按鈕，導致無法進入座位選擇

**Spec 檢查**：
1. **FR-020**: "系統必須偵測區域選擇佈局類型"（對應票種選擇）
   - 檢查點：是否正確偵測了頁面元素？
2. **FR-021**: "系統必須取得所有可用區域選項及定價和可用性資訊"
   - 檢查點：是否正確提取按鈕文字與 disabled 狀態？
3. **SC-005**: "系統透過回退策略（JavaScript 點擊、CDP）成功處理瀏覽器元素互動失敗，成功率達 95%"
   - 檢查點：是否實作多層次的搜尋策略（Native → CDP → JavaScript）？

**修正方向**：
- 實作 CDP DOMSnapshot 方法作為主要搜尋策略
- 檢查 NoDriver Element 序列化問題
- 確保文字提取時處理空白節點
- 實作多策略 fallback 架構
- 測試結果驗證成功率達 95%

### Spec 檢查範例 3：設計原則檢查

**問題**：想新增一個直接在程式碼中設定票數的功能

**設計原則檢查**：
1. **配置驅動架構**（核心設計原則）
   - ❌ 不應：在程式碼中硬編碼票數
   - ✅ 應該：透過 settings.json `ticket_number` 設定

2. **三層回退策略**（核心設計原則）
   - ✅ 應該：實作「使用者設定 → 預設值 → 手動選擇」的回退
   - 確保在無法自動設定時有優雅的降級方案

3. **函數分解原則**（核心設計原則）
   - 票數選擇邏輯應該是獨立函數
   - 不應混雜在主流程中
   - 應該可獨立測試

**修正方向**：
- 使用 `config_dict["ticket_number"]` 讀取設定
- 實作完整的回退策略
- 確保函數職責單一

### 快速檢查清單（除錯時用）

```markdown
□ 這個問題屬於 12 階段中的哪一階段？
□ 相關的 FR 編號是什麼？（功能需求）
□ 相關的 SC 編號是什麼？（成功標準）
□ 修復後能達到該成功標準嗎？
□ 修復是否遵循三層回退策略？
□ 修復是否使用 settings.json 配置？
□ 相關平台有特殊處理需求嗎？
□ 函數職責是否單一？
□ 測試計畫是什麼？
```

---

*最後更新：2025-10-16*
*基於 ibon disabled button 除錯經驗建立*
*Spec 驅動除錯方法新增於 2025-10-16*