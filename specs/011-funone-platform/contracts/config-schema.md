# 設定檔契約：FunOne Tickets 平台支援

**分支**：`011-funone-platform` | **日期**：2026-01-13 | **規格**：[spec.md](../spec.md)

## 1. settings.json 結構

### 1.1 新增欄位

在 `advanced` 區塊新增以下欄位：

```json
{
  "advanced": {
    "funone_session_cookie": ""
  }
}
```

### 1.2 欄位定義

#### funone_session_cookie

| 屬性 | 值 |
|------|-----|
| **類型** | `string` |
| **預設值** | `""` |
| **必要性** | 登入時必要 |
| **說明** | FunOne 的 `ticket_session` Cookie 值 |
| **UI 名稱** | FunOne Session Cookie |
| **UI 位置** | 進階設定 |

**取得方式**：
1. 使用瀏覽器登入 FunOne
2. 開啟開發者工具 > Application > Cookies
3. 複製 `ticket_session` 的值

**格式範例**：
```
eyJpdiI6Ik...（URL-encoded JSON）
```

### 1.3 共用欄位對照

| 欄位 | UI 名稱 | FunOne 用途 |
|------|---------|-------------|
| `homepage` | 網址 | FunOne 活動連結 |
| `ticket_number` | 預設票數 | 預設購票張數 |
| `area_keyword` | 票種關鍵字 | 票種篩選 |
| `area_keyword_exclude` | 排除關鍵字 | 票種排除 |
| `date_keyword` | 場次關鍵字 | 場次篩選 |
| `pass_date_is_sold_out` | 略過售罄場次 | 場次選擇 |
| `area_auto_select_mode` | 選擇模式 | 票種選擇策略 |

## 2. 設定載入邏輯

### 2.1 Cookie 取得邏輯

```python
def get_funone_session_cookie(config_dict: dict) -> str:
    """
    取得 FunOne session cookie

    Returns:
        Cookie 值，若未設定則回傳空字串
    """
    return config_dict.get('advanced', {}).get('funone_session_cookie', '')
```

## 3. URL 識別

### 3.1 FunOne 域名

```python
FUNONE_DOMAINS = [
    'tickets.funone.io',
    'funone.io'
]
```

### 3.2 路由判斷

```python
def is_funone_url(url: str) -> bool:
    """判斷是否為 FunOne URL"""
    return any(domain in url for domain in FUNONE_DOMAINS)
```

## 4. 驗證規則

### 4.1 funone_session_cookie 驗證

| 規則 | 說明 |
|------|------|
| 非空檢查 | 登入前必須設定 |
| 格式檢查 | 應為 URL-encoded 字串 |
| 有效性檢查 | 透過 `/Member/CheckToken` API 驗證 |

## 5. UI 整合建議

### 5.1 設定畫面

```
進階設定
├── FunOne Session Cookie [文字輸入框]
│   └── 說明：從瀏覽器複製 ticket_session Cookie 值
```

### 5.2 錯誤訊息

| 情境 | 訊息 |
|------|------|
| Cookie 未設定 | 「請先設定 FunOne Session Cookie」 |
| Cookie 過期 | 「FunOne Session 已過期，請重新登入並更新 Cookie」 |

## 6. 範例設定

### 6.1 完整設定範例

```json
{
  "homepage": "https://tickets.funone.io/activity/activity_detail/abc123",
  "ticket_number": 4,
  "area_keyword": "A區,B區",
  "date_keyword": "19:30,晚場",
  "pass_date_is_sold_out": true,
  "area_auto_select_mode": "from_top_to_bottom",
  "advanced": {
    "funone_session_cookie": "eyJpdiI6Ik..."
  }
}
```

### 6.2 最小設定範例

```json
{
  "homepage": "https://tickets.funone.io/activity/activity_detail/abc123",
  "ticket_number": 2,
  "advanced": {
    "funone_session_cookie": "eyJpdiI6Ik..."
  }
}
```
