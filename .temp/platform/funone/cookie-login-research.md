# FunOne Tickets Cookie 登入研究報告

**研究日期**：2026-01-12
**網站**：https://tickets.funone.io/
**狀態**：研究完成，尚未實作

---

## 1. 網站基本資訊

| 項目 | 內容 |
|------|------|
| 網站名稱 | FunOne Tickets |
| 網址 | https://tickets.funone.io/ |
| 後端框架 | Laravel (PHP 8.1.32) |
| 伺服器 | nginx/1.20.1 |
| 登入方式 | 手機號碼 + OTP 驗證碼 |

---

## 2. Cookie 分析

### 2.1 登入相關 Cookies

| Cookie | 用途 | HttpOnly | 登入必要性 |
|--------|------|----------|-----------|
| `ticket_session` | Session ID，識別登入身份 | ✅ Yes | ✅ **必要** |
| `XSRF-TOKEN` | CSRF 防護 Token | ❌ No | ❌ 非必要（自動生成） |
| `login_phone` | 記錄登入手機號碼 | ❌ No | ❌ 非必要 |
| `lock_vcode_login` | 驗證碼鎖定時間戳 | ❌ No | ❌ 非必要 |

### 2.2 分析用 Cookies（可忽略）

| Cookie | 用途 |
|--------|------|
| `_ga` | Google Analytics |
| `_ga_PQLWB0NV7Z` | Google Analytics |
| `_clck` | Microsoft Clarity |
| `_clsk` | Microsoft Clarity |
| `_fbp` | Facebook Pixel |

---

## 3. Cookie 快速登入測試結果

### 3.1 測試方法

1. 開啟新瀏覽器，訪問網站（未登入狀態）
2. 清除所有 cookies
3. 只注入 `ticket_session` cookie
4. 重新整理頁面檢查登入狀態

### 3.2 測試結果

```
[RESULT] SUCCESS - Logged in! Cookie login works with ticket_session only!
```

**結論**：只需要 `ticket_session` 即可完成 Cookie 快速登入，不需要其他 cookies。

---

## 4. 實作規格

### 4.1 Cookie 屬性

```
Name:     ticket_session
Domain:   tickets.funone.io
Path:     /
HttpOnly: true
Secure:   false
SameSite: Lax
Expires:  24 小時
```

### 4.2 NoDriver 注入範例

```python
import nodriver as uc
import nodriver.cdp as cdp

# 使用 CDP 設定 HTTP-only cookie
await page.send(cdp.network.set_cookie(
    name="ticket_session",
    value="<用戶的 session 值>",
    domain="tickets.funone.io",
    path="/",
    secure=False,
    http_only=True
))
```

### 4.3 Cookie 值格式

Cookie 值為 URL-encoded 的 JSON，解碼後結構如下：

```json
{
  "iv": "<base64 初始向量>",
  "value": "<base64 加密值>",
  "mac": "<HMAC 簽章>",
  "tag": ""
}
```

這是 Laravel 標準的加密 cookie 格式。

---

## 5. 網站特性

### 5.1 登入流程

1. 用戶輸入手機號碼（支援多國碼）
2. 發送 OTP 驗證碼到手機
3. 用戶輸入驗證碼
4. 伺服器驗證後建立 session
5. 設定 `ticket_session` cookie（HTTP-only）

### 5.2 支援的手機國碼

```javascript
countryCodeList: {
  "886": "Taiwan",
  "81": "Japan",
  "82": "South Korea",
  "852": "Hong Kong",
  "66": "Thailand",
  "63": "Philippines",
  "65": "Singapore",
  "60": "Malaysia",
  "86": "China",
  "853": "Macau",
  "84": "Vietnam"
}
```

### 5.3 購票系統

- 使用 WebSocket 進行即時票務操作
- 多個 WebSocket 伺服器端點（負載平衡）
- 支援信用卡付款和全家 FamiPort 付款
- 取票方式：電子票、現場取票、郵寄、全家取票

---

## 6. 開發建議

### 6.1 Cookie 管理

1. **取得 Cookie**：用戶手動登入後，使用 `browser.cookies.get_all()` 取得 `ticket_session`
2. **儲存 Cookie**：將 cookie 值儲存到 settings.json 或獨立檔案
3. **注入 Cookie**：啟動時使用 CDP `network.set_cookie` 注入
4. **更新機制**：cookie 有效期 24 小時，需提醒用戶定期更新

### 6.2 注意事項

- `ticket_session` 是 HTTP-only，無法透過 JavaScript 讀取/設定
- 必須使用 CDP 命令操作
- XSRF-TOKEN 會在每次請求時自動更新，不需要手動管理
- Session 過期後需要重新登入取得新的 cookie

---

## 7. 測試腳本

測試腳本位置：`test_funone_cookie.py`

使用方式：
```bash
python test_funone_cookie.py
```

腳本會：
1. 開啟瀏覽器訪問 FunOne
2. 清除所有 cookies
3. 注入指定的 `ticket_session`
4. 檢查是否成功登入

---

## 8. 參考資料

- 網站首頁：https://tickets.funone.io/
- 登入頁面：https://tickets.funone.io/login
- 會員中心：https://tickets.funone.io/member（需登入）

---

## 更新紀錄

| 日期 | 內容 |
|------|------|
| 2026-01-12 | 初次研究，確認 cookie 快速登入可行 |
| 2026-01-12 | 新增 NoDriver 技術評估報告 |
