**文件說明**：TixCraft 平台的完整實作參考，包含平台特性分析、技術實作指南、常見問題與已驗證的解決方案。

**最後更新**：2025-11-12

---

# 平台實作參考：TixCraft

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
- 可能使用進階選擇界面
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

3. **Cookie 認證**
   - `tixcraft_sessionid` 是主要 Cookie
   - 有效期 30 天
   - 刷新頁面後應檢查是否仍有效

---

## 12 階段實作指南

### Stage 1: 環境初始化
**狀態**：✅ 完全實作

**TixCraft 特定步驟**：
```python
# 1. 平台識別
if 'tixcraft.com' in url:
    platform = 'tixcraft'

# 2. Cookie 注入 (如有)
if cookies:
    await inject_cookies(page, cookies['tixcraft'])

# 3. 導航並驗證
await page.goto(config['url'])
await verify_page_loaded(page)
```

**常見問題**：
- Cookie 過期 → 重新取得並更新
- 頁面未完全加載 → 增加等待時間

---

### Stage 2-3: 身份認證 + 頁面監控
**狀態**：✅ 完全實作

**TixCraft 特點**：
- Cookie 通常有效，無需重新登入
- 頁面加載相對快速
- 監控按鈕變化（從禁用到可用）

**關鍵監控點**：
```python
# 監控「選擇」按鈕
select_btn = await page.query_selector('[id*="select"]')
if await select_btn.is_enabled():
    print("Ticket released!")
```

---

### Stage 4-5: 日期 + 區域選擇
**狀態**：✅ 完全實作 (已優化 Feature 003 - 早期返回)

**TixCraft 特點**：
- 支援多個日期/座位區域
- 可能需要點擊「展開」查看隱藏選項
- 支援 AND 邏輯與條件回退

**範例選擇器**：
```python
date_selector = '.date-item'
area_selector = '.area-option'
```

---

### Stage 6: 票數設定
**狀態**：✅ 完全實作

**TixCraft 實現**：
- 通常使用 `<input type="number">`
- 某些活動可能有動態限制
- 總金額實時更新

---

### Stage 7: 驗證碼處理
**狀態**：✅ 完全實作

**TixCraft 特點**：
- 不是所有活動都需要驗證碼
- 使用 DDDOcr 進行 OCR 識別

---

### Stage 8-9: 表單填寫 + 同意條款
**狀態**：✅ 實作 / 🔄 部分實作

**TixCraft 實現**：
- 購買人信息欄位相對簡單
- 有「同意服務條款」複選框

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
   - 檢測：嘗試進行操作，若被導向登入頁
   - 處理：提示使用者更新 Cookie

2. **庫存已售完** → 無票可買
   - 檢測：頁面訊息或無可選選項
   - 處理：停止並報告

3. **網路超時** → 暫時性問題
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
1. 訪問 https://tixcraft.com
2. 登入您的帳號
3. F12 開啟開發者工具 → Application → Cookies
4. 複製 `tixcraft_sessionid` 的值
5. 粘貼到 `settings.json`

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

如果排隊超時，可調整 `monitor_timeout` 設定。

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
| 條款複選框 | `input[name="agreeTerms"]` | 必須勾選 |

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
- 驗證矩陣：`docs/05-validation/spec-validation-matrix.md`
- 平台檢查清單：`docs/05-validation/platform-checklist.md`
- 代碼對應表：`docs/05-validation/fr-to-code-mapping.md`

---

## 最後更新

**日期**：2025-11
**版本**：1.0
**狀態**：✅ 可用於生產環境

