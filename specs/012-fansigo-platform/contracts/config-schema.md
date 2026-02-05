# 設定檔結構：FANSI GO 平台支援

**功能分支**：`012-fansigo-platform`
**建立日期**：2026-02-05

---

## 設定項目

### 基礎設定（複用現有）

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| homepage | `config_dict["homepage"]` | str | "" | FANSI GO 活動/購票頁網址 |
| ticket_number | `config_dict["ticket_number"]` | int | 1 | 購票張數 |

### 場次選擇設定（複用現有）

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| enable | `config_dict["date_auto_select"]["enable"]` | bool | true | 是否啟用場次自動選擇 |
| date_keyword | `config_dict["date_auto_select"]["date_keyword"]` | str | "" | 場次關鍵字（如「高雄」「台北」） |
| mode | `config_dict["date_auto_select"]["mode"]` | str | "from top to bottom" | 選擇模式 |

### 票種選擇設定（複用現有）

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| enable | `config_dict["area_auto_select"]["enable"]` | bool | true | 是否啟用票種自動選擇 |
| area_keyword | `config_dict["area_auto_select"]["area_keyword"]` | str | "" | 票種關鍵字（如「VIP」「雙日」） |
| mode | `config_dict["area_auto_select"]["mode"]` | str | "from top to bottom" | 選擇模式 |

### 條件式遞補設定（複用現有 v1.2）

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| date_auto_fallback | `config_dict["date_auto_fallback"]` | bool | false | 場次關鍵字失敗時是否自動遞補 |
| area_auto_fallback | `config_dict["area_auto_fallback"]` | bool | false | 票種關鍵字失敗時是否自動遞補 |
| keyword_exclude | `config_dict["keyword_exclude"]` | str | "" | 排除關鍵字（分號分隔） |

### FANSI GO 專屬設定（新增）

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| fansigo_cookie | `config_dict["accounts"]["fansigo_cookie"]` | str | "" | FansiAuthInfo Cookie 值 |

**注意**：與其他平台 cookie（`ibonqware`, `funone_session_cookie`, `tixcraft_sid`）保持一致，放在 `accounts` 區塊。

---

## URL 模式識別

```python
FANSIGO_URL_PATTERNS = {
    "event_page": r"go\.fansi\.me/events/(\d+)",
    "show_page": r"go\.fansi\.me/tickets/show/(\d+)",
    "checkout_page": r"go\.fansi\.me/tickets/payment/checkout/",
    "order_result": r"go\.fansi\.me/tickets/payment/orderresult/",
}
```

---

## 使用範例

### 範例 1：購買普通隊長高雄場 VIP 票

```json
{
  "homepage": "https://go.fansi.me/events/590002",
  "ticket_number": 2,
  "date_auto_select": {
    "enable": true,
    "date_keyword": "高雄",
    "mode": "from top to bottom"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP",
    "mode": "from top to bottom"
  },
  "advanced": {
    "fansigo_cookie": "%7B%22__typename%22%3A%22userToken%22%2C%22accessToken%22%3A%22eyJ...%22%2C%22tokenLife%22%3A604800%7D"
  }
}
```

### 範例 2：購買野地晃晃雙日預售票

```json
{
  "homepage": "https://go.fansi.me/tickets/show/150006",
  "ticket_number": 1,
  "area_auto_select": {
    "enable": true,
    "area_keyword": "雙日預售",
    "mode": "from top to bottom"
  }
}
```

### 範例 3：多關鍵字優先級設定

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "台北;高雄;台中"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP;雙日;單日"
  },
  "keyword_exclude": "限量;抽選"
}
```

---

## 設定驗證規則

### homepage
- 必須為有效的 URL
- 必須匹配 `go.fansi.me` 域名
- 必須為活動頁或購票頁

### ticket_number
- 必須為正整數
- 建議範圍：1-10

### date_keyword / area_keyword
- 可為空（使用 mode 自動選擇）
- 多關鍵字使用分號分隔
- 關鍵字順序決定優先級

### fansigo_cookie
- 可為空（不登入）
- 若非空，必須為 URL Encoded JSON 格式
- 必須包含有效的 JWT accessToken
