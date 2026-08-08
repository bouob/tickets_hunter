# 機制 02：身份認證 (Stage 2)

**文件說明**：說明搶票系統各平台的登入機制，包含 Cookie 注入、帳密登入與 OAuth 流程
**最後更新**：2026-06-10

---

## 概述

身份認證在 `nodriver_goto_homepage()`（`src/nodriver_tixcraft.py`）中啟動：系統根據 `homepage` URL 判斷目標平台，若設定中有對應帳號則自動導向登入頁面，同時注入預設的 Session Cookie。

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

`nodriver_goto_homepage()` 處理 TixCraft 家族（tixcraft.com、indievox.com、ticketmaster.sg/com）的 Cookie 注入。

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

**實作位置**：`src/nodriver_tixcraft.py`（nodriver_goto_homepage）

### iBon

`nodriver_ibon_login()` 使用 CDP 注入 `ibonqware` Cookie：

```
Cookie: ibonqware
Domain: .ibon.com.tw
Secure: True, HttpOnly: True
```

函式會驗證 Cookie 內容是否包含必要欄位（`mem_id`, `mem_email`, `huiwanTK`, `ibonqwareverify`），並在設定後透過 `driver.cookies.get_all()` 確認寫入成功。

特殊處理：`tour.ibon.com.tw` 需要先訪問 `ticket.ibon.com.tw` 完成 OAuth 取得 `_at_e` token（`nodriver_goto_homepage()` 內處理）。

**實作位置**：`src/platforms/ibon.py`（nodriver_ibon_login）

### FunOne

`nodriver_goto_homepage()` 注入 `ticket_session` Cookie 至 `tickets.funone.io` 網域，注入後自動重新載入頁面以套用。

**設定來源**：`config_dict["accounts"]["funone_session_cookie"]`

---

## 帳號密碼登入

### KKTIX

`nodriver_kktix_signin()` 處理 KKTIX 登入：

1. 從 URL 解析 `back_to` 參數取得登入後的跳轉目標
2. 填寫 `#user_login`（帳號）與 `#user_password`（密碼）
3. 點擊送出按鈕（選擇器降級鏈，見下）
4. 智慧輪詢：每 0.3 秒檢查 URL 是否離開 `/users/sign_in`，最多等待 10 秒
5. 登入完成後，若停留在首頁/使用者頁面，自動跳轉至 `back_to` 目標

**觸發時機**：主迴圈偵測到 URL 含 `/users/sign_in?` 時，以及 `nodriver_goto_homepage()` 中自動將首頁改為 `CONST_KKTIX_SIGN_IN_URL`。

**實作位置**：`src/platforms/kktix.py`（nodriver_kktix_signin）

#### 登入前置關卡（三道，皆早於填表）

登入路徑上有三個會讓「帳密沒被填寫」的關卡，全都不是帳密本身的問題：

| 關卡 | 偵測 | 行為 |
|------|------|------|
| Cloudflare 等候室 | `nodriver_kktix_check_queue_page`（`#cf-time`）| 直接返回不填表。頁面會自我刷新，**禁止手動 reload** |
| 訪客彈窗「立刻成為 KKTIX 會員」| `nodriver_kktix_check_guest_modal`（`#guestModal`）| 點 `button[data-dismiss="modal"]` 關閉 |
| 排隊後掉成訪客 session | `nodriver_kktix_redirect_to_signin_if_guest`（`li.not-signed-in:not(.hidden)`）| 導回 sign_in 頁，跳過本輪 |

另有一道不在程式控制內：**Cloudflare challenge 會攔截登入表單的提交**。
症狀是送出按鈕確實被點到，但 URL 始終停在 `/users/sign_in`，直到 challenge 被解掉為止。
此時 log 會先出現 `[KKTIX SIGNIN] Login timeout after 10s; 0/33 URL checks failed`
（`0/33` 表示 websocket 正常，純粹是頁面沒跳轉），隨後才出現 `[CLOUDFLARE] Challenge page detected`。

#### 送出按鈕的選擇器降級鏈

送出按鈕曾以中文 `value="登入"` 綁定，非繁中 locale 會靜默失敗（找不到就什麼都不做，也不留 log）。
現改為依序嘗試並回報實際命中者：

```
form#new_user input[type="submit"]
form[action*="sign_in"] input[type="submit"]
input[type="submit"][value="登入"]
button[type="submit"]
```

命中時記錄 `[KKTIX SIGNIN] Submit clicked via <selector>`；全部落空則記錄候選數量並提前返回，
不再對一個註定失敗的表單空等 10 秒。

#### 診斷輸出的語意

| 訊息 | 意義 |
|------|------|
| `#user_login not found; page may be a queue room, a Cloudflare challenge, or already signed in` | 欄位不存在。舊版此處靜默跳過，看起來就像「不填帳密」|
| `URL check failed (attempt N/33): ...` | 輪詢第一次失敗（只印一次，避免洗版）|
| `Login timeout after 10s; X/33 URL checks failed, last error: ...` | 逾時彙總。`X=0` 代表連線正常、純粹沒跳轉；`X` 接近 33 代表 websocket 有問題 |

#### 帳號啟用門檻

`is_kktix_account_configured()` 是「帳號是否已設定」的**唯一判定**（去空白後非空）。

過去三處各判各的：主迴圈用 `> 0` 決定要不要把首頁改寫成登入頁，
`nodriver_kktix_signin` 用 `> 4` 決定要不要填表，訪客導回用 `<= 4`。
1–4 字的帳號因此會被送到一個永遠不會被填寫的登入頁，表現就是 bot 停在登入畫面不動。
新增呼叫點時務必沿用此函式，不要重新寫長度判斷。

### FamiTicket

`nodriver_fami_login()` 處理全家售票登入：

1. 檢查帳號 (`#usr_act`) 與密碼 (`#usr_pwd`) 欄位是否已有值
2. 使用 ZenDriver `send_keys` 填寫（非 JS 直接賦值，模擬真人輸入）
3. 點擊 `button#btnLogin`
4. 等待 URL 變化確認登入成功（最多 10 秒）

**設定來源**：`config_dict["accounts"]["fami_account"]` / `fami_password`
**實作位置**：`src/platforms/famiticket.py`（nodriver_fami_login）

### KHAM / ticket.com.tw / UDN

`nodriver_kham_login()` 處理 KHAM 系列登入，特點是需要 OCR 驗證碼：

1. 填寫 `#ACCOUNT`（帳號）與密碼欄位
2. 使用 `ddddocr` OCR 辨識驗證碼圖片
3. 填入驗證碼並送出

UDN 為半自動登入：程式填寫帳密，但 reCAPTCHA 圖片驗證需使用者手動完成。

**實作位置**：`src/platforms/kham.py`（nodriver_kham_login）

### Cityline

`nodriver_cityline_login()` 採用半自動策略：

1. 自動填寫 Email 至 `input[type="text"]`
2. 提示使用者手動輸入密碼與驗證碼
3. 監控登入按鈕（`button.login-btn.submit-btn`）的 `disabled` 屬性
4. 按鈕啟用後自動點擊送出

**實作位置**：`src/platforms/cityline.py`（nodriver_cityline_login）

### TicketPlus

`nodriver_ticketplus_account_auto_fill()` 的流程：

1. 檢查 Cookie 中是否已有 `user` Cookie（`nodriver_ticketplus_is_signin()`）
2. 若未登入，點擊帳號圖示開啟登入表單
3. 呼叫 `nodriver_ticketplus_account_sign_in()` 填寫帳密並送出

**實作位置**：`src/platforms/ticketplus.py`（nodriver_ticketplus_is_signin、nodriver_ticketplus_account_auto_fill）

---

## Facebook OAuth

`nodriver_facebook_login()` 處理透過 Facebook 登入的平台（如 Cityline）：

1. 填寫 `#email`（帳號）與 `#pass`（密碼）
2. 模擬 Enter 鍵送出（使用 CDP `input_.dispatch_key_event`）
3. 等待 2 秒供 OAuth 跳轉完成

**觸發時機**：主迴圈偵測到 URL 為 `https://www.facebook.com/login.php?` 時。

**實作位置**：`src/platforms/facebook.py`（nodriver_facebook_login）

---

## 首頁導向與認證整合

`nodriver_goto_homepage()` 是認證的統一入口，負責將各平台導向正確的登入 URL：

| 平台 | 觸發條件 | 登入 URL 常數 |
|------|---------|--------------|
| KKTIX | `kktix.c` in homepage + 有帳號 | `CONST_KKTIX_SIGN_IN_URL` |
| FamiTicket | `famiticket.com` + 有帳號 | `CONST_FAMI_SIGN_IN_URL` |
| KHAM | `kham.com` + 有帳號 | `CONST_KHAM_SIGN_IN_URL` |
| ticket.com.tw | `ticket.com.tw` + 有帳號 | `CONST_TICKET_SIGN_IN_URL` |
| UDN | `udnfunlife.com` + 有帳號 | `CONST_UDN_SIGN_IN_URL` |
| URBTIX | `urbtix.hk` + 有帳號 | `CONST_URBTIX_SIGN_IN_URL` |
| Cityline | `cityline.com` + 有帳號 | `CONST_CITYLINE_SIGN_IN_URL` |
| HKTicketing | `hkticketing.com` + 有帳號 | Type01/Type02 兩種 |
| TicketPlus | `ticketplus.com.tw` + 有帳號 | 導向首頁 `ticketplus.com.tw/` |

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `src/nodriver_tixcraft.py` | 認證統一入口（`nodriver_goto_homepage`、Cookie 注入、登入 URL 常數） |
| `src/platforms/*.py` | 各平台登入函式（`nodriver_kktix_signin`、`nodriver_ibon_login` 等） |
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

### KKTIX 看起來沒有自動填入帳密
**症狀**：畫面停在登入頁，帳密欄位是空的，log 只有 `nodriver_kktix_signin:` 一行
**原因**：多數情況不是填寫失敗，而是根本沒走到填寫——見上方「登入前置關卡」三道。
先看 log 有沒有 `#user_login not found`（欄位不存在）或 `No clickable submit button found`（按鈕沒找到）。
**解法**：確認是否卡在 CF 等候室或 challenge；帳號長度 1–4 字者請確認已升級至含
`is_kktix_account_configured` 的版本

### Bot 不動也不結束，log 只有 [URL DIAG] empty url 反覆出現
**症狀**：畫面停住，終端機每 2 秒印一次 `[URL DIAG] empty url, skipping dispatch`，
且 `silent_ws_errors` 持續增加
**原因**：CDP websocket 已中斷。`no close frame received or sent` 原本被歸類為正常關閉而靜默，
主迴圈取不到 URL 就跳過所有平台分派，形成既不工作也不退出的空轉
**解法**：連續 15 次後會出現 `[URL ERROR] Browser connection lost`，依提示關閉瀏覽器並重啟程式。
細節見 `12-error-handling.md`

### tour.ibon.com.tw 登入異常
**症狀**：Cookie 注入成功但 tour.ibon 頁面仍未登入
**原因**：未先訪問 ticket.ibon.com.tw 完成 OAuth
**解法**：確認 `nodriver_goto_homepage()` 中的 tour.ibon 特殊處理流程正確執行
