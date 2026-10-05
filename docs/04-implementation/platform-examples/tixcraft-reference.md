# 平台實作參考：TixCraft

**文件說明**：TixCraft 平台的完整實作參考，包含平台特性分析、技術實作指南、常見問題與已驗證的解決方案。
**最後更新**：2025-12-02

---

## 平台概述

**平台名稱**：TixCraft
**市場地位**：台灣最大票務平台
**主要業務**：演唱會、戲劇、運動賽事、展覽
**完成度**：84.4% (54/64 FR)
**難度級別**：⭐⭐ (中等)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 直接頁面導航，無複雜排隊機制
- 相對穩定的 HTML 結構
- 多種支付方式
- Cookie 認證有效期長 (30 天)

⚠️ **挑戰**：
- 某些活動有排隊機制（FIFO 排隊）
- 可能使用進階選擇介面
- JavaScript 執行可能需要
- 某些動態元素需要監控

### 特殊機制

1. **展開面板** (Accordion)
   - 某些活動在日期/座位選擇中使用展開面板
   - 需要先點擊展開才能看到選項
   - 選擇器可能隨展開/關閉而變化

2. **排隊機制** (部分活動)
   - 高人氣活動可能進入排隊頁面
   - URL 變為 `/queue`
   - 需要等待進入購票頁面

3. **區域選擇後的等待狀態**
   - 點擊區域後，頁面可能顯示等待訊息
   - **重要**：出現以下訊息時應等待，不應重整頁面

   | 等待訊息 | 說明 |
   |---------|------|
   | `請稍後，並避免進行任何操作` | 系統處理中，等待轉跳 |
   | `即將前往結帳，請勿進行任何操作` | 即將進入結帳頁面 |
   | `即將轉跳，請稍後` | 頁面轉跳中 |

   - 這些訊息通常伴隨 overlay 遮罩層
   - 等待完成後會自動跳轉至下一頁（如 `/ticket/ticket/`）

4. **Cookie 認證**
   - `tixcraft_sessionid` 是主要 Cookie
   - 有效期 30 天
   - 刷新頁面後應檢查是否仍有效

---

## 12 階段實作指南

### Stage 1: 環境初始化
**狀態**：✅ 完全實作

**TixCraft 特定步驟**：

環境初始化由主檔與共用模組負責，平台模組不參與。實際流程：

```python
# src/nodriver_tixcraft.py
# 1. URL 路由識別（main() 的 while True 內）
if 'tixcraft.com' in url:
    is_quit_bot = await nodriver_tixcraft_main(tab, url, config_dict, ocr, Captcha_Browser)

# 2. Cookie 注入：拓元靠 SID / TIXUISID，於平台模組內以 CDP 寫入
#    設定來源 config_dict["accounts"]["tixcraft_sid"]

# 3. 導向起始頁
await nodriver_goto_homepage(tab, config_dict)
```

**常見問題**：
- Cookie 過期 → 重新取得並更新 `tixcraft_sid`
- 拓元刻意不做自動登入，靠 chrome profile 保持 session

---

### Stage 2-3: 身份認證 + 頁面監控
**狀態**：✅ 完全實作

**TixCraft 特點**：
- Cookie 通常有效，無需重新登入
- 頁面載入相對快速
- 監控按鈕變化（從停用到可用）

**關鍵監控點**：
```python
# 監控「選擇」按鈕（zendriver 用 tab，元素無 is_enabled()，
# 改查 disabled 屬性或直接嘗試點擊）
select_btn = await tab.query_selector('[id*="select"]')
if select_btn and not select_btn.attrs.get('disabled'):
    debug.log("Ticket released!")
```

---

### Stage 4-5: 日期 + 區域選擇
**狀態**：✅ 完全實作 (已最佳化 Feature 003 - 早期返回)

**TixCraft 特點**：
- 支援多個日期/座位區域
- 可能需要點擊「展開」檢視隱藏選項
- 支援 AND 邏輯與條件回退

**範例選擇器**：
```python
date_selector = '.date-item'
area_selector = '.area-option'
```

---

### Stage 6: 票數設定
**狀態**：✅ 完全實作

**TixCraft 實作**：
- 通常使用 `<input type="number">`
- 某些活動可能有動態限制
- 總金額即時更新

---

### Stage 7: 驗證碼處理
**狀態**：✅ 完全實作

**TixCraft 特點**：
- 不是所有活動都需要驗證碼
- 使用 DDDOcr 進行 OCR 識別

---

### Stage 8-9: 表單填寫 + 同意條款
**狀態**：✅ 實作 / 🔄 部分實作

**TixCraft 實作**：
- 購買人信息欄位相對簡單
- 有「同意服務條款」核取方塊

**表單選擇器**：
```python
name_input = 'input[name="buyerName"]'
email_input = 'input[name="buyerEmail"]'
terms_checkbox = 'input[name="agreeTerms"]'
```

---

### Stage 10-11: 訂單送出 + 排隊
**狀態**：✅ 實作 / 🔄 部分實作

**TixCraft 流程**：
1. 點擊「確認購買」按鈕
2. 若進入排隊 → 等待進入頁面
3. 進入支付頁面 → 完成支付

**支付方式**：
- 信用卡（透過綠界）
- Apple Pay/Google Pay
- 銀行轉帳

---

### Stage 12: 錯誤處理
**狀態**：✅ 實作

**常見錯誤**：
1. **Cookie 過期** → 無法進行購票
   - 偵測：嘗試進行操作，若被導向登入頁
   - 處理：提示使用者更新 Cookie

2. **庫存已售完** → 無票可買
   - 偵測：頁面訊息或無可選選項
   - 處理：停止並報告

3. **網路逾時** → 暫時性問題
   - 處理：自動重試 (最多 3 次)

---

## 配置範例

```json
{
  "url": "https://tixcraft.com/activity/xxx",
  "webdriver_type": "nodriver",
  "ticket_account": {
    "tixcraft": {
      "email": "your@email.com",
      "password": "password",
      "cookies": {
        "tixcraft_sessionid": "your-session-id"
      }
    }
  },
  "date_auto_select": {
    "enable": true,
    "keywords": ["10/15"],
    "mode": "top_down"
  },
  "area_auto_select": {
    "enable": true,
    "keywords": ["一般席"],
    "exclude_keywords": ["輪椅"],
    "mode": "top_down"
  },
  "ticket_count": 2,
  "advanced": {
    "verbose": true,
    "headless": true
  }
}
```

---

## 常見問題與解決方案

### Q1: Cookie 如何取得？

**步驟**：
1. 存取 https://tixcraft.com
2. 登入您的帳號
3. F12 開啟開發者工具 → Application → Cookies
4. 複製 `tixcraft_sessionid` 的值
5. 貼上到 `settings.json`

### Q2: 為什麼選擇失敗？

**常見原因**：
- 選擇器已失效（HTML 更新）→ 更新選擇器
- 選項已售完 → 手動嘗試確認
- 選項需要展開 → 先點擊展開按鈕

### Q3: 如何處理排隊？

**系統已自動處理**：
1. 偵測進入排隊頁面
2. 自動等待
3. 進入購票頁面後繼續

如果排隊逾時，可調整 `monitor_timeout` 設定。

### Q4: 能否自動填寫支付信息？

**不建議**。因為：
- 安全風險（信用卡信息）
- 平台可能有額外驗證
- 不符合使用者期望

**推薦做法**：
- 系統自動進行至支付頁面
- 使用者手動完成支付
- 系統監控支付完成

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 日期選項 | `.date-item` | 點擊後選擇 |
| 座位區域 | `.area-option` | 根據活動而異 |
| 票數輸入 | `input[type="number"]` | 設定數量 |
| 確認按鈕 | `button[id*="confirm"]` | 提交訂單 |
| 條款核取方塊 | `input[name="agreeTerms"]` | 必須勾選 |

---

## 測試檢查清單

- [ ] 環境變數正確設定
- [ ] Cookie 有效且未過期
- [ ] 日期選擇正常運作
- [ ] 座位區域選擇正常運作
- [ ] 票數設定無誤
- [ ] 表單填寫完整
- [ ] 訂單成功送出
- [ ] 付款完成

---

## 相關文件

- 機制文件：`docs/03-mechanisms/[01-12].md`
- 12 階段標準：`docs/02-development/ticket_automation_standard.md`
- 函式索引：`docs/02-development/structure.md`

---

## 最後更新

**日期**：2025-11
**版本**：1.0
**狀態**：✅ 可用於生產環境

