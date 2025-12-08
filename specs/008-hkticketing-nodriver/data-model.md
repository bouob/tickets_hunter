# 資料模型：HKTicketing NoDriver 遷移

**功能**：008-hkticketing-nodriver
**日期**：2025-11-27
**狀態**：完成

## 核心實體

### 1. hkticketing_dict（狀態字典）

**用途**：儲存 HKTicketing 平台的運行時狀態

```python
hkticketing_dict = {
    "is_date_submiting": bool,     # 日期是否正在提交中
    "fail_list": List[str],        # 密碼嘗試失敗清單
    "played_sound_ticket": bool,   # 票券音效是否已播放
    "played_sound_order": bool     # 訂單音效是否已播放
}
```

**欄位說明**：

| 欄位 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `is_date_submiting` | bool | False | 防止重複點擊購買按鈕 |
| `fail_list` | List[str] | [] | 記錄已嘗試過的密碼，避免重複嘗試 |
| `played_sound_ticket` | bool | False | 進入票券選擇頁面時播放音效 |
| `played_sound_order` | bool | False | 進入訂單確認頁面時播放音效 |

**狀態轉移**：

```
初始狀態
    │
    ▼
is_date_submiting = False
    │
    ├─► 日期選擇成功 ─► is_date_submiting = True
    │                       │
    │                       ├─► 進入票券頁面 ─► played_sound_ticket = True
    │                       │
    │                       └─► 離開日期頁面 ─► is_date_submiting = False
    │
    └─► 密碼輸入失敗 ─► fail_list.append(password)
```

### 2. config_dict（設定字典）

**用途**：從 settings.json 讀取的使用者設定

**HKTicketing 相關設定路徑**：

```python
# 日期選擇設定
config_dict["date_auto_select"]["enable"]       # bool: 是否啟用日期自動選擇
config_dict["date_auto_select"]["date_keyword"] # str: 日期關鍵字
config_dict["date_auto_select"]["mode"]         # str: 選擇模式

# 區域選擇設定
config_dict["area_auto_select"]["enable"]       # bool: 是否啟用區域自動選擇
config_dict["area_auto_select"]["area_keyword"] # str: 區域關鍵字
config_dict["area_auto_select"]["mode"]         # str: 選擇模式

# Fallback 遞補設定（Feature 003）
config_dict["date_auto_fallback"]               # bool: 日期關鍵字全失敗時是否自動遞補（預設 False）
config_dict["area_auto_fallback"]               # bool: 區域關鍵字全失敗時是否自動遞補（預設 False）

# 排除關鍵字
config_dict["keyword_exclude"]                  # str: 排除關鍵字（分號分隔）

# 票數設定
config_dict["ticket_number"]                    # int: 購票張數

# 帳號設定
config_dict["advanced"]["hkticketing_account"]           # str: HKTicketing 帳號
config_dict["advanced"]["hkticketing_password_plaintext"] # str: 明文密碼
config_dict["advanced"]["hkticketing_password"]          # str: 加密密碼

# 其他設定
config_dict["tixcraft"]["auto_reload_coming_soon_page"]  # bool: 是否自動重載即將開賣頁面
config_dict["advanced"]["auto_reload_page_interval"]     # float: 重載間隔（秒）
config_dict["advanced"]["user_guess_string"]             # str: 密碼猜測字串
config_dict["advanced"]["verbose"]                       # bool: 詳細日誌模式
config_dict["advanced"]["play_sound"]["ticket"]          # bool: 是否播放票券音效
config_dict["advanced"]["play_sound"]["order"]           # bool: 是否播放訂單音效
```

---

## 頁面類型識別

### URL 模式對照表

| 頁面類型 | URL 模式 | 對應函數 |
|----------|----------|----------|
| 登入頁面 | `hkticketing.com/Secure/ShowLogin.aspx` 或 `hkticketing.com/Membership/Login.aspx` | `nodriver_hkticketing_login` |
| 活動頁面 | `shows/show.aspx?` | `nodriver_hkticketing_date_auto_select` |
| 票券選擇頁面 | `/events/` + `/performances/` + `/tickets` | `nodriver_hkticketing_performance` |
| 座位圖頁面 | `/events/` + `/performances/` + `/seatmap` | `nodriver_hkticketing_go_to_payment` |
| 排隊頁面 | `queue.hkticketing.com` | `nodriver_hkticketing_url_redirect` |
| 錯誤頁面 | `detection.aspx` 或 `busy_galaxy` | `nodriver_hkticketing_content_refresh` |

### 支援網站

| 網站 | 域名 | 特殊處理 |
|------|------|----------|
| HKTicketing | `premier.hkticketing.com` | 標準流程 |
| Galaxy Macau | `ticketing.galaxymacau.com` | 無取票方式選擇 |
| Ticketek Australia | `ticketek.com.au` | 不同的入口 URL |

---

## CSS 選擇器對照表

### 登入頁面

| 元素 | CSS 選擇器 |
|------|------------|
| 帳號輸入框 | `div.loginContentContainer > input.borInput` |
| 密碼輸入框 | `div.loginContentContainer > input[type="password"]` |

### 日期選擇頁面

| 元素 | CSS 選擇器 |
|------|------------|
| 日期下拉選單 | `#p` |
| 日期選項 | `#p > option` |
| 購買按鈕 | `#buyButton > input` |
| 密碼輸入框 | `#entitlementPassword > div > div > div > div > input[type='password']` |

### 票券選擇頁面

| 元素 | CSS 選擇器 |
|------|------------|
| 票價區域列表 | `#ticketSelectorContainer > ul > li` |
| 票數下拉選單 | `select.shortSelect` |
| 取票方式選單 | `#selectDeliveryType` |
| 下一步按鈕 | `#continueBar > div.chooseTicketsOfferDiv > button` |
| 頁尾（捲動目標）| `#wrapFooter` |

### 座位圖頁面

| 元素 | CSS 選擇器 |
|------|------------|
| 前往付款按鈕 | `#goToPaymentButton` |

### Cookie 彈窗

| 元素 | CSS 選擇器 |
|------|------------|
| 關閉按鈕 | `#closepolicy_new` |

### 機器人檢測

| 元素 | CSS 選擇器 |
|------|------------|
| 檢測 iframe | `#main-iframe` |

---

## 錯誤訊息清單

### 需要重定向的錯誤訊息

```python
content_retry_string_list = [
    "Access Denied",
    "Service Unavailable",
    "The service is unavailable",
    "HTTP Error 500",
    "HTTP Error 503",
    "504 Gateway Time-out",
    "502 Bad Gateway",
    "An error occurred while processing your request",
    "The network path was not found",
    "Could not open a connection to SQL Server",
    "Hi fans, you're in the queue to",
    "We will check for the next available purchase slot",
    "please stay on this page and do not refresh",
    "Please be patient and wait a few minutes before trying again",
    "Server Error in '/' Application",
    "The target principal name is incorrect",
    "Cannot generate SSPI context",
    "System.Data.SqlClient.Sql",
    "System.ComponentModel.Win32Exception",
    "Your attempt to access the web site has been blocked by",
    "This request was blocked by"
]
```

### 需要重定向的 URL 模式

```python
redirect_url_list = [
    'queue.hkticketing.com/hotshow.html',
    '.com/detection.aspx?rt=',
    '/busy_galaxy.',
    '/hot0.ticketek.com.au/',  # 到 hot19
]
```

---

## 關係圖

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              settings.json                                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌───────────┐  │
│  │ date_auto_select│ │ area_auto_select│ │    advanced     │ │ fallback  │  │
│  │   - enable      │ │   - enable      │ │ - hkticketing_* │ │ settings  │  │
│  │   - date_keyword│ │   - area_keyword│ │ - verbose       │ │           │  │
│  │   - mode        │ │   - mode        │ │ - play_sound    │ │           │  │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └─────┬─────┘  │
└───────────┼───────────────────┼───────────────────┼───────────────┼─────────┘
            │                   │                   │               │
            ▼                   ▼                   ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              config_dict                                     │
│                     (載入到記憶體的設定字典)                                  │
│                                                                              │
│  date_auto_fallback ──► 日期關鍵字全失敗時是否自動遞補（預設 False）          │
│  area_auto_fallback ──► 區域關鍵字全失敗時是否自動遞補（預設 False）          │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           hkticketing_dict                                   │
│  (運行時狀態追蹤)                                                            │
│                                                                              │
│  is_date_submiting ──► 控制日期提交流程                                      │
│  fail_list ──────────► 追蹤密碼嘗試歷史                                      │
│  played_sound_* ────► 控制音效播放                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Fallback 邏輯流程圖

```
關鍵字匹配流程
     │
     ▼
┌─────────────────────────────┐
│   嘗試所有關鍵字組匹配       │
└──────────────┬──────────────┘
               │
        匹配成功？
       ╱        ╲
     是          否
     │           │
     ▼           ▼
┌─────────┐  ┌────────────────────────┐
│選擇匹配 │  │ 檢查 auto_fallback 設定│
│的項目   │  └───────────┬────────────┘
└─────────┘              │
                   fallback=true?
                  ╱            ╲
                是              否
                │               │
                ▼               ▼
    ┌───────────────────┐  ┌─────────────────┐
    │ 使用 auto_select  │  │ 停止選擇流程     │
    │ _mode 自動遞補    │  │（嚴格模式）      │
    └───────────────────┘  └─────────────────┘
```
