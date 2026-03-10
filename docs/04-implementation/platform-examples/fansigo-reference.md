# 平台實作參考：FANSI GO

**文件說明**：FANSI GO 平台的完整實作參考，涵蓋 Next.js SPA 架構、Cookie 認證、tab.evaluate() DOM 操作等技術實作指南。
**最後更新**：2026-03-05

---

## 平台概述

**平台名稱**：FANSI GO
**網站**：`go.fansi.me`
**市場地位**：台灣新興票務平台
**主要業務**：演唱會、音樂活動
**完成度**：58% ✅ (7/12 Stages)
**難度級別**：⭐⭐ (中等)

---

## 平台特性

### 核心特點
✅ **優勢**：
- Next.js SPA 架構，結構相對現代化
- 購票流程簡潔（活動頁 → 場次頁 → 結帳）
- 無驗證碼機制
- Cookie 認證（FansiAuthInfo）注入簡單

⚠️ **挑戰**：
- Next.js SPA 頁面導致 NoDriver `query_selector_all()` 失效
- 必須使用 `tab.evaluate()`（直接 JS 執行）操作 DOM
- 點擊連結時 Next.js 可能開啟新分頁
- 表單填寫、條款同意、錯誤處理等階段尚未實作

### 特殊機制

1. **tab.evaluate() 為主要 DOM 操作方式**
   - NoDriver 的 `query_selector_all()` 在 Next.js SPA 頁面上會失敗
   - 所有 DOM 查詢與操作統一使用 `tab.evaluate()` 執行 JavaScript
   - 這是 FANSI GO 與其他平台最大的技術差異

2. **直接導航取代點擊**
   - 使用 `tab.get()` 直接導航至目標 URL
   - 避免 Next.js 路由攔截導致開啟新分頁的問題

3. **URL 正則表達式路由**
   - 使用 `FANSIGO_URL_PATTERNS` 字典定義 URL 模式
   - 透過 `get_fansigo_page_type()` 輔助函式判斷頁面類型

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_fansigo_main()` | 25939 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_fansigo_inject_cookie()` | 25397 | Cookie 注入（FansiAuthInfo）|
| Stage 4 | `nodriver_fansigo_date_auto_select()` | 25569 | 場次/日期自動選擇 |
| Stage 4 | `nodriver_fansigo_get_shows()` | 25434 | 取得所有可用場次 |
| Stage 4 | `nodriver_fansigo_click_show()` | 25523 | 導航至場次頁面 |
| Stage 5 | `nodriver_fansigo_area_auto_select()` | 25737 | 區域/票種自動選擇 |
| Stage 5 | `nodriver_fansigo_get_sections()` | 25664 | 取得所有可用票區 |
| Stage 6 | `nodriver_fansigo_assign_ticket_number()` | 25839 | 票數設定 |
| Stage 10 | `nodriver_fansigo_click_checkout()` | 25892 | 點擊結帳按鈕 |
| Util | `get_fansigo_page_type()` | 25376 | URL 頁面類型判斷 |
| Util | `is_fansigo_url()` | 25369 | 是否為 FANSI GO URL |
| Const | `FANSIGO_URL_PATTERNS` | 25361 | URL 正則表達式模式 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## 12 階段實作摘要

| 階段 | 名稱 | 狀態 | 說明 |
|------|------|------|------|
| 1 | 環境初始化 | ✅ 完成 | 由 `cli()` / 主程式進入點處理 |
| 2 | 身份驗證 | ✅ 完成 | FansiAuthInfo Cookie 注入 |
| 3 | 頁面監控 | ✅ 完成 | URL 正則路由 + 頁面類型偵測 |
| 4 | 日期選擇 | ✅ 完成 | 場次列表取得 + 關鍵字匹配 + 直接導航 |
| 5 | 區域選擇 | ✅ 完成 | 票區列表取得 + 關鍵字匹配 |
| 6 | 票數設定 | ✅ 完成 | tab.evaluate() 設定票數 |
| 7 | CAPTCHA | ⬜ 不適用 | 平台目前無驗證碼機制 |
| 8 | 表單填寫 | ❌ 未實作 | 待補充 |
| 9 | 條款同意 | ❌ 未實作 | 待補充 |
| 10 | 訂單送出 | ✅ 完成 | 點擊結帳按鈕 |
| 11 | 排隊/付款 | ❌ 未實作 | 結帳頁面到達後停止自動化 |
| 12 | 錯誤處理 | ❌ 未實作 | 待補充 |

**完成度**：7/12 階段 = 58%（Stage 7 不適用不計入分母）

---

## 頁面類型與 URL 路由

FANSI GO 使用正則表達式匹配 URL 來判斷頁面類型：

| 頁面類型 | URL 模式 | 處理邏輯 |
|---------|---------|---------|
| `event` | `go.fansi.me/events/(\d+)` | 取得場次列表 → 關鍵字匹配 → 導航 |
| `show` | `go.fansi.me/tickets/show/(\d+)` | 票區選擇 → 票數設定 → 結帳 |
| `checkout` | `go.fansi.me/tickets/payment/checkout/` | 停止自動化，播放音效 |
| `order_result` | `go.fansi.me/tickets/payment/orderresult/` | 停止自動化，播放音效 |
| `unknown` | 其他 | 無動作 |

---

## 狀態字典（fansigo_dict）

`fansigo_dict` 全域字典管理購票流程狀態：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `is_cookie_injected` | bool | Cookie 是否已注入 |
| `played_sound_ticket` | bool | 已播放購票成功音效 |
| `last_page_type` | str | 上次頁面類型（去重用）|
| `qty_set_url` | str | 已設定票數的 URL（避免重複設定）|

---

## 已知問題與解決方案

### 1. NoDriver query_selector 失效
**問題**：Next.js SPA 頁面上，NoDriver 的 `query_selector_all()` 無法正確取得 DOM 元素。
**解決方案**：所有 DOM 操作統一使用 `tab.evaluate()` 執行 JavaScript，繞過 NoDriver 的 DOM 查詢限制。

### 2. Next.js 連結開啟新分頁
**問題**：點擊場次連結時，Next.js 路由可能開啟新瀏覽器分頁而非頁面內導航。
**解決方案**：使用 `tab.get(href)` 直接導航至目標 URL，而非模擬點擊。

### 3. 未實作的階段
**問題**：Stage 8（表單填寫）、Stage 9（條款同意）、Stage 11（排隊/付款）、Stage 12（錯誤處理）尚未實作。
**解決方案**：目前到達結帳頁面後停止自動化，需手動完成後續步驟。待後續版本補強。

---

## 設定建議

```json
{
  "homepage": "https://go.fansi.me/events/12345",
  "accounts": {
    "fansigo_cookie": "<your_FansiAuthInfo_cookie>"
  },
  "ticket_number": 2,
  "date_auto_select": {
    "enable": true,
    "date_keyword": ""
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": ""
  }
}
```

---

## 相關文件

- 📋 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - FANSI GO 函數索引
- 📖 [NoDriver API 指南](../../06-api-reference/nodriver_api_guide.md) - tab.evaluate() 用法

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2026-03 | 初版：FANSI GO 完整實作參考文件 |
