# 平台實作參考：FunOne Tickets

**文件說明**：FunOne Tickets (趣活) 平台的完整實作參考，涵蓋 Cookie 認證、OCR 驗證碼、即時票務狀態更新、售罄偵測等技術實作指南。
**最後更新**：2026-03-05

---

## 平台概述

**平台名稱**：FunOne Tickets (趣活)
**網站**：`tickets.funone.io`
**市場地位**：台灣新興票務平台
**主要業務**：演唱會、音樂活動、展覽
**完成度**：92% ✅ (11/12 Stages)
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 完整的 12 階段購票流程支援
- Cookie 認證（ticket_session）注入機制
- OCR 圖形驗證碼自動辨識
- 即時票務狀態更新按鈕（WebSocket）
- 售罄偵測與自動重新整理
- 完整的錯誤處理與自動重載機制

⚠️ **挑戰**：
- OCR 驗證碼需要辨識模型支援
- 多步驟購票流程（活動詳情 → 票種選擇 → 數量 → 驗證碼 → 結帳）
- 需要手動取得 ticket_session Cookie
- 即將開賣/排隊等待頁面需特殊處理

### 特殊機制

1. **Cookie 認證**
   - 使用 CDP `network.set_cookie` 注入 `ticket_session`
   - 於 `goto_homepage` 階段注入，與 TixCraft/iBon 相同模式
   - 設定鍵：`accounts.funone_session_cookie`

2. **即時票務狀態更新**
   - 頁面提供「即時票務更新」按鈕
   - 透過 WebSocket 取得最新庫存狀態
   - 自動點擊更新按鈕以重新整理票況

3. **售罄偵測與自動重新整理**
   - 偵測所有票種是否已售罄
   - 售罄時自動點擊重新整理按鈕
   - 可設定最大重試次數

4. **OCR 驗證碼**
   - 圖形驗證碼自動擷取（base64）
   - 支援 OCR 辨識填入
   - 辨識失敗時自動重新載入驗證碼圖片

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_funone_main()` | 25057 | 主控制流程（URL 路由 + 頁面狀態機）|
| Stage 2 | `nodriver_funone_inject_cookie()` | 23375 | Cookie 注入（ticket_session）|
| Stage 2 | `nodriver_funone_check_login_status()` | 23413 | 登入狀態檢查 |
| Stage 2 | `nodriver_funone_verify_login()` | 23431 | 登入驗證 |
| Stage 3 | `nodriver_funone_close_popup()` | 23455 | 關閉彈窗/Cookie 同意框 |
| Stage 3 | `nodriver_funone_detect_step()` | 24673 | 偵測購票流程步驟（1~5）|
| Stage 4 | `nodriver_funone_date_auto_select()` | 23557 | 場次/日期自動選擇 |
| Stage 5 | `nodriver_funone_area_auto_select()` | 23761 | 票種區域自動選擇 |
| Stage 5 | `nodriver_funone_check_sold_out()` | 23977 | 售罄偵測 |
| Stage 5 | `nodriver_funone_click_refresh_button()` | 24154 | 即時票務狀態更新按鈕點擊 |
| Stage 6 | `nodriver_funone_assign_ticket_number()` | 24210 | 票數設定 |
| Stage 7 | `nodriver_funone_captcha_handler()` | 24401 | 驗證碼處理主函式 |
| Stage 7 | `nodriver_funone_reload_captcha()` | 24564 | 重新載入驗證碼圖片 |
| Stage 7 | `nodriver_funone_ocr_captcha()` | 24595 | OCR 辨識驗證碼並填入 |
| Stage 9 | `nodriver_funone_ticket_agree()` | 24761 | 同意條款勾選 |
| Stage 10 | `nodriver_funone_order_submit()` | 24841 | 訂單送出 |
| Stage 12 | `nodriver_funone_auto_reload()` | 24895 | 錯誤自動重新載入 |
| Stage 12 | `nodriver_funone_error_handler()` | 25027 | 錯誤處理 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## 12 階段實作摘要

| 階段 | 名稱 | 狀態 | 說明 |
|------|------|------|------|
| 1 | 環境初始化 | ✅ 完成 | 由 `cli()` / 主程式進入點處理 |
| 2 | 身份驗證 | ✅ 完成 | Cookie 注入 + 登入狀態驗證 |
| 3 | 頁面監控 | ✅ 完成 | URL 路由 + 頁面狀態機 + 彈窗關閉 |
| 4 | 日期選擇 | ✅ 完成 | 場次/日期自動選擇（活動詳情頁）|
| 5 | 區域選擇 | ✅ 完成 | 票種區域選擇 + 售罄偵測 + 自動重新整理 |
| 6 | 票數設定 | ✅ 完成 | 票數自動設定 |
| 7 | CAPTCHA | ✅ 完成 | OCR 圖形驗證碼辨識 + 重新載入 |
| 8 | 表單填寫 | ⚠️ 未實作 | 需手動填寫購票人資訊 |
| 9 | 條款同意 | ✅ 完成 | 自動勾選同意條款 |
| 10 | 訂單送出 | ✅ 完成 | 自動點擊送出按鈕 |
| 11 | 排隊/付款 | ✅ 完成 | 等待頁面偵測（purchase_waiting_jump）|
| 12 | 錯誤處理 | ✅ 完成 | 自動重新載入 + 錯誤分類處理 |

**完成度**：11/12 階段 = 92%

---

## 頁面類型與 URL 路由

FunOne 的 `_main()` 依據 URL 判斷頁面類型：

| 頁面類型 | URL 模式 | 處理邏輯 |
|---------|---------|---------|
| `HOME` | `https://tickets.funone.io` | 驗證登入狀態 |
| `LOGIN` | `/login` | 等待手動登入 |
| `MEMBER` | `/member` | 會員頁面 |
| `ACTIVITY_DETAIL` | `/activity/activity_detail/` | 場次選擇 → 區域選擇 |
| `WAITING` | `/purchase_waiting_jump/` | 排隊等待 |
| `TICKET_FLOW` | 其他 tickets.funone.io 路徑 | 步驟偵測 → 對應處理 |

---

## 狀態字典（funone_dict）

`funone_dict` 全域字典管理整個購票流程的狀態追蹤：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `is_session_selecting` | bool | 場次選擇中 |
| `is_ticket_selecting` | bool | 票種選擇中 |
| `played_sound_ticket` | bool | 已播放購票成功音效 |
| `fail_list` | list | 已失敗的答案/嘗試 |
| `reload_count` | int | 重新載入計數 |
| `ocr_retry_count` | int | OCR 重試計數 |
| `last_page_type` | str | 上次頁面類型（去重用）|

---

## 已知問題與解決方案

### 1. Cookie 過期
**問題**：`ticket_session` Cookie 有效期有限，過期後需重新取得。
**解決方案**：定期更新 `settings.json` 中的 `funone_session_cookie` 值。

### 2. OCR 辨識率
**問題**：圖形驗證碼辨識率可能不穩定。
**解決方案**：內建自動重新載入驗證碼機制，辨識失敗時自動換圖重試。

### 3. 表單填寫未自動化
**問題**：Stage 8（購票人資訊表單）尚未自動化。
**解決方案**：目前需手動填寫，待後續版本補強。

---

## 設定建議

```json
{
  "homepage": "https://tickets.funone.io/activity/activity_detail/XXXXX",
  "accounts": {
    "funone_session_cookie": "<your_ticket_session_cookie>"
  },
  "ticket_number": 2,
  "date_auto_select": {
    "enable": true,
    "date_keyword": ""
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": ""
  },
  "ocr_captcha": {
    "enable": true
  }
}
```

---

## 相關文件

- 📋 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - FunOne 函數索引
- 📖 [Stage 7: 驗證碼處理機制](../../03-mechanisms/07-captcha-handling.md) - OCR 驗證碼詳解

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2026-03 | 初版：FunOne 完整實作參考文件 |
