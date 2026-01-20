# FunOne Tickets NoDriver 技術評估報告

**評估日期**：2026-01-12
**網站**：https://tickets.funone.io/
**狀態**：新平台，尚未實作
**評估結果**：**建議實作**

---

## 1. 評估摘要

| 項目 | 評估結果 |
|------|----------|
| 實作難度 | **低** |
| Cookie 快速登入 | **可行** (已驗證) |
| 反爬蟲機制 | **無** |
| 驗證碼 | **圖形驗證碼** (購票時) |
| WebSocket | **有** (購票流程) |
| 優先建議 | **高** - 適合作為新平台範例 |

---

## 2. 網站技術架構

### 2.1 後端技術

| 項目 | 內容 |
|------|------|
| 框架 | Laravel (PHP 8.1.32) |
| 伺服器 | nginx/1.20.1 |
| CDN | Google Cloud |
| 認證方式 | Session Cookie (Laravel 加密) |

### 2.2 前端技術

- SPA (Single Page Application) 架構
- 響應式設計
- 支援多語言 (繁中、英、日、韓)

---

## 3. 認證機制分析

### 3.1 登入方式

| 方式 | 說明 |
|------|------|
| 手機 OTP | 主要登入方式，手機號碼 + 簡訊驗證碼 |
| QPP 掃碼 | QR Code 掃碼登入 (替代方案) |

**無傳統帳號密碼登入**

### 3.2 Session 管理

| Cookie | 用途 | HttpOnly | 必要性 |
|--------|------|----------|--------|
| `ticket_session` | Session ID | Yes | **必要** |
| `XSRF-TOKEN` | CSRF 防護 | No | 自動生成 |
| `_token` | Laravel CSRF | - | 自動管理 |

### 3.3 Cookie 快速登入 (已驗證)

```python
# NoDriver 注入範例
import nodriver.cdp as cdp

await page.send(cdp.network.set_cookie(
    name="ticket_session",
    value="<session_value>",
    domain="tickets.funone.io",
    path="/",
    secure=False,
    http_only=True
))
```

**結論**：只需 `ticket_session` 即可完成登入，無需其他 cookies。

---

## 4. 頁面結構分析 (MCP 實測)

### 4.1 首頁結構

**URL**: `https://tickets.funone.io/`

```
banner
  link "logo"
  link "最新消息" / "常見問題" / "探索活動"
  textbox "搜尋"
  link "登入/註冊"
精彩活動
  button "精選活動" / "即將開賣"
  link [活動卡片] -> activity_detail/{activityId}
最新消息
contentinfo (頁尾)
```

### 4.2 活動詳情頁

**URL**: `https://tickets.funone.io/activity/activity_detail/{activityId}`

```
banner
活動圖片 + 標題 + 日期 + 票價 + 主辦單位
navigation: 活動資訊 / 購票方式 / 取票方式 / 退票方式 / 注意事項
活動場次選擇 (日期 + 時間 + 場地)
button "下一步" -> 觸發登入檢查
```

### 4.3 登入頁面

**URL**: `https://tickets.funone.io/login?redirectPath=...`

```
手機號碼
  combobox [國碼選擇] (預設 +886 Taiwan)
  textbox "0912345678"
  button "發送" (發送 OTP)
簡訊驗證碼
  textbox "請輸入簡訊驗證碼"
  button "登入"
掃描 QRcode 登入 (QPP)
```

---

## 5. 購票流程分析

### 5.1 流程步驟

```
1. 首頁 -> 選擇活動
2. 活動詳情 -> 選擇場次 -> 點擊「下一步」
3. 登入檢查 (未登入 -> 登入頁)
4. 選票頁面 -> 選擇票種 + 張數 + 驗證碼
5. 確認訂單
6. 付款 (信用卡 / 全家 FamiPort)
7. 完成訂單 -> 取票序號
```

### 5.2 關鍵操作點

| 步驟 | 操作 | 難度 |
|------|------|------|
| 場次選擇 | 點擊日期/時間 | 低 |
| 票種選擇 | 選擇票種 + 張數 | 低 |
| 驗證碼 | 圖形驗證碼輸入 | **中** (需人工) |
| 付款 | 信用卡 3D 驗證 | **中** (需人工) |

---

## 6. API 結構

### 6.1 已識別 API

| API | 方法 | 用途 |
|-----|------|------|
| `/Member/CheckToken` | POST | 檢查登入狀態 |
| `/api/ApiTicket/GetModelActiveInfoList` | POST | 取得活動資訊 |
| `/Ticket/GetArrangeActiveList` | POST | 取得票券清單 |
| `/api/ApiFront/GetNowTime` | POST | 取得伺服器時間 |
| `/ThirdParty/QPPGetTokenNoMemberId` | POST | QPP 掃碼登入 |

### 6.2 認證 Headers

```
x-xsrf-token: <XSRF-TOKEN cookie value>
x-requested-with: XMLHttpRequest
Content-Type: application/json
```

### 6.3 CSRF Token

- Laravel 標準 CSRF 機制
- Request Body 包含 `_token` 欄位
- 自動從頁面取得，無需手動處理

---

## 7. WebSocket 分析

### 7.1 用途

- 即時票務操作（選位、鎖票）
- 購票流程中使用

### 7.2 特點

- 多個 WebSocket 伺服器端點（負載平衡）
- 需在購票流程中維持連線

---

## 8. 實作建議

### 8.1 建議實作的函數

| 函數名稱 | 功能 | 複雜度 |
|----------|------|--------|
| `funone_main` | 主控制函數，URL 路由 | 低 |
| `funone_inject_cookie` | Cookie 快速登入 | 低 |
| `funone_activity_detail` | 活動詳情頁處理 | 低 |
| `funone_select_session` | 場次選擇 | 低 |
| `funone_select_ticket` | 票種/張數選擇 | 中 |
| `funone_captcha_handler` | 驗證碼處理 | 中 |

### 8.2 不建議自動化的功能

- OTP 登入（需要實際手機接收驗證碼）
- 付款流程（信用卡 3D 驗證）

### 8.3 設定檔建議

```json
{
  "advanced": {
    "funone_session_cookie": "",
    "funone_auto_select_ticket_type": "",
    "funone_ticket_number": 2
  }
}
```

---

## 9. 與 Urbtix 對比

| 項目 | FunOne | Urbtix |
|------|--------|--------|
| Cookie 快速登入 | **可行** | 不建議 |
| 反爬蟲機制 | 無 | Tencent WAF |
| 驗證碼 | 購票時 | 登入時 |
| 認證複雜度 | 低 | 高 |
| 實作難度 | **低** | 中 |
| WebSocket | 有 | 無 |

---

## 10. 風險評估

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| Session 過期 (24hr) | 中 | 提醒用戶定期更新 Cookie |
| 圖形驗證碼 | 低 | 保留人工介入 |
| WebSocket 斷線 | 中 | 自動重連機制 |
| 高流量售罄 | 低 | 快速選票邏輯 |

---

## 11. 實作優先級

**建議**：**高優先級**

**原因**：
1. Cookie 快速登入已驗證可行
2. 無複雜反爬蟲機制
3. 頁面結構清晰，選擇器穩定
4. Laravel 標準架構，API 可預測
5. 適合作為新平台開發範例

---

## 12. 參考資料

- Cookie 研究報告：`.temp/funone/cookie-login-research.md`
- 測試腳本：`.temp/funone/test_funone_cookie.py`
- NoDriver API：`docs/06-api-reference/nodriver_api_guide.md`
- 12 階段標準：`docs/02-development/ticket_automation_standard.md`

---

## 更新紀錄

| 日期 | 內容 |
|------|------|
| 2026-01-12 | 初次技術評估 |
| 2026-01-12 | MCP 實測頁面結構 |
| 2026-01-12 | API 分析完成 |
