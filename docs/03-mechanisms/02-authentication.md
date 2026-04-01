# 機制 02：身份認證 (Stage 2)

**文件說明**：說明搶票系統各平台的登入機制，包含 Cookie 注入、帳密登入與 OAuth 流程
**最後更新**：2026-03-06

---

## 概述

身份認證在 `nodriver_goto_homepage()` (行 751) 中啟動：系統根據 `homepage` URL 判斷目標平台，若設定中有對應帳號則自動導向登入頁面，同時注入預設的 Session Cookie。

**核心目標**：在進入主迴圈前完成認證，讓後續購票操作擁有必要的登入狀態。

**優先度**：🟡 P2 - 重要但非核心流程（部分平台無需登入即可購票）

---

## 認證方式分類

系統支援三種認證方式，依平台特性選用：

| 認證方式 | 適用平台 | 優勢 | 限制 |
|---------|---------|------|------|
| CDP Cookie 注入 | TixCraft 系、iBon、FunOne | 最快，無需互動 | Cookie 會過期 |
| 帳號密碼自動填寫 | KKTIX、FamiTicket、KHAM、Cityline | 無需手動取得 Cookie | 部分需人工處理驗證碼 |
| Facebook OAuth | Cityline | 支援第三方登入 | 需 FB 帳密 |

---

## Cookie 注入流程（CDP）

### TixCraft 系列

`nodriver_goto_homepage()` (行 820-919) 處理 TixCraft 家族（tixcraft.com、indievox.com、ticketmaster.sg/com）的 Cookie 注入。

**Cookie 名稱依網域不同**：

| 網域 | Cookie 名稱 | Cookie Domain |
|------|------------|---------------|
| tixcraft.com | `TIXUISID` | `.tixcraft.com` |
| indievox.com | `IVUISID` | `www.indievox.com` |
| ticketmaster.sg | `TIXPUISID` | `ticketmaster.sg` |
| ticketmaster.com | `TIXUISID` | `.ticketmaster.com` |

**注入步驟**：
1. 刪除舊的 SID 與 Session Cookie（避免衝突）
2. 透過 `cdp.network.set_cookie()` 設定新 Cookie（`secure=True`, `http_only=True`）
3. 驗證 Cookie 是否設定成功（讀取所有 Cookie 比對）
4. 若 CDP 方式失敗，回退至 `driver.cookies.set_all()` 方法

**設定來源**：`config_dict["accounts"]["tixcraft_sid"]`

**實作位置**：`src/nodriver_tixcraft.py` 行 820-919

### iBon

`nodriver_ibon_login()` (行 8094) 使用 CDP 注入 `ibonqware` Cookie：

```
Cookie: ibonqware
Domain: .ibon.com.tw
Secure: True, HttpOnly: True
```

函式會驗證 Cookie 內容是否包含必要欄位（`mem_id`, `mem_email`, `huiwanTK`, `ibonqwareverify`），並在設定後透過 `driver.cookies.get_all()` 確認寫入成功。

特殊處理：`tour.ibon.com.tw` 需要先訪問 `ticket.ibon.com.tw` 完成 OAuth 取得 `_at_e` token (行 920-961)。

**實作位置**：`src/nodriver_tixcraft.py` 行 8094-8151

### FunOne

行 965-999 注入 `ticket_session` Cookie 至 `tickets.funone.io` 網域，注入後自動重新載入頁面以套用。

**設定來源**：`config_dict["accounts"]["funone_session_cookie"]`

---

## 帳號密碼登入

### KKTIX

`nodriver_kktix_signin()` (行 644) 處理 KKTIX 登入：

1. 從 URL 解析 `back_to` 參數取得登入後的跳轉目標
2. 填寫 `#user_login`（帳號）與 `#user_password`（密碼）
3. 點擊 `input[type="submit"][value="登入"]` 按鈕
4. 智慧輪詢：每 0.3 秒檢查 URL 是否離開 `/users/sign_in`，最多等待 10 秒
5. 登入完成後，若停留在首頁/使用者頁面，自動跳轉至 `back_to` 目標

**觸發時機**：主迴圈偵測到 URL 含 `/users/sign_in?` 時，以及 `nodriver_goto_homepage()` 中自動將首頁改為 `CONST_KKTIX_SIGN_IN_URL` (行 764)。

**實作位置**：`src/nodriver_tixcraft.py` 行 644-737

### FamiTicket

`nodriver_fami_login()` (行 8153) 處理全家售票登入：

1. 檢查帳號 (`#usr_act`) 與密碼 (`#usr_pwd`) 欄位是否已有值
2. 使用 ZenDriver `send_keys` 填寫（非 JS 直接賦值，模擬真人輸入）
3. 點擊 `button#btnLogin`
4. 等待 URL 變化確認登入成功（最多 10 秒）

**設定來源**：`config_dict["accounts"]["fami_account"]` / `fami_password`
**實作位置**：`src/nodriver_tixcraft.py` 行 8153-8248

### KHAM / ticket.com.tw / UDN

`nodriver_kham_login()` (行 14685) 處理 KHAM 系列登入，特點是需要 OCR 驗證碼：

1. 填寫 `#ACCOUNT`（帳號）與密碼欄位
2. 使用 `ddddocr` OCR 辨識驗證碼圖片
3. 填入驗證碼並送出

UDN 為半自動登入：程式填寫帳密，但 reCAPTCHA 圖片驗證需使用者手動完成。

**實作位置**：`src/nodriver_tixcraft.py` 行 14685-14734

### Cityline

`nodriver_cityline_login()` (行 13751) 採用半自動策略：

1. 自動填寫 Email 至 `input[type="text"]`
2. 提示使用者手動輸入密碼與驗證碼
3. 監控登入按鈕（`button.login-btn.submit-btn`）的 `disabled` 屬性
4. 按鈕啟用後自動點擊送出

**實作位置**：`src/nodriver_tixcraft.py` 行 13751-13800

### TicketPlus

`nodriver_ticketplus_account_auto_fill()` (行 6364) 的流程：

1. 檢查 Cookie 中是否已有 `user` Cookie（`nodriver_ticketplus_is_signin()`，行 6349）
2. 若未登入，點擊帳號圖示開啟登入表單
3. 呼叫 `nodriver_ticketplus_account_sign_in()` 填寫帳密並送出

**實作位置**：`src/nodriver_tixcraft.py` 行 6349-6414

---

## Facebook OAuth

`nodriver_facebook_login()` (行 328) 處理透過 Facebook 登入的平台（如 Cityline）：

1. 填寫 `#email`（帳號）與 `#pass`（密碼）
2. 模擬 Enter 鍵送出（使用 CDP `input_.dispatch_key_event`）
3. 等待 2 秒供 OAuth 跳轉完成

**觸發時機**：主迴圈偵測到 URL 為 `https://www.facebook.com/login.php?` 時 (行 26285-26287)。

**實作位置**：`src/nodriver_tixcraft.py` 行 328-348

---

## 首頁導向與認證整合

`nodriver_goto_homepage()` (行 751) 是認證的統一入口，負責將各平台導向正確的登入 URL：

| 平台 | 觸發條件 | 登入 URL 常數 |
|------|---------|--------------|
| KKTIX | `kktix.c` in homepage + 有帳號 | `CONST_KKTIX_SIGN_IN_URL` (行 57) |
| FamiTicket | `famiticket.com` + 有帳號 | `CONST_FAMI_SIGN_IN_URL` (行 53) |
| KHAM | `kham.com` + 有帳號 | `CONST_KHAM_SIGN_IN_URL` (行 56) |
| ticket.com.tw | `ticket.com.tw` + 有帳號 | `CONST_TICKET_SIGN_IN_URL` (行 58) |
| UDN | `udnfunlife.com` + 有帳號 | `CONST_UDN_SIGN_IN_URL` (行 59) |
| URBTIX | `urbtix.hk` + 有帳號 | `CONST_URBTIX_SIGN_IN_URL` (行 60) |
| Cityline | `cityline.com` + 有帳號 | `CONST_CITYLINE_SIGN_IN_URL` (行 52) |
| HKTicketing | `hkticketing.com` + 有帳號 | Type01/Type02 兩種 (行 54-55) |
| TicketPlus | `ticketplus.com.tw` + 有帳號 | 導向首頁 `ticketplus.com.tw/` |

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `src/nodriver_tixcraft.py` | 所有登入函式的實作 |
| `src/settings.py` | 帳號欄位定義（`get_default_config` 中的 `accounts` 區塊） |

---

## 故障排除

### Cookie 認證失敗
**症狀**：Cookie 注入後仍被要求登入
**原因**：Cookie 過期、格式錯誤、或平台更新了 Cookie 名稱
**解法**：重新從瀏覽器取得最新 Cookie 值，確認 Cookie 名稱與網域正確

### 帳號密碼登入失敗
**症狀**：帳密填寫後頁面無反應或提示錯誤
**原因**：帳密錯誤、帳號鎖定、驗證碼辨識失敗
**解法**：先手動登入確認帳號狀態，檢查 OCR 模型準確率

### tour.ibon.com.tw 登入異常
**症狀**：Cookie 注入成功但 tour.ibon 頁面仍未登入
**原因**：未先訪問 ticket.ibon.com.tw 完成 OAuth
**解法**：確認 `nodriver_goto_homepage()` 中的 tour.ibon 特殊處理流程正確執行
