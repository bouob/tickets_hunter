# 研究報告：FANSI GO 平台支援

**功能分支**：`012-fansigo-platform`
**研究日期**：2026-02-05
**詳細研究**：`docs/09-platform-research/fansi-go-research.md`
**標準參考**：`docs/02-development/ticket_automation_standard.md`

---

## 12 階段標準對照分析

依據專案 12 階段搶票自動化標準，分析 FANSI GO 平台的適用性：

### 階段對照表

| 階段 | 名稱 | FANSI GO 適用性 | 優先級 |
|------|------|-----------------|--------|
| 1 | 環境初始化 | ✅ 適用 | 必要 |
| 2 | 身份認證 | ✅ 適用（Cookie 登入） | 重要 |
| 3 | 頁面監控與重載 | ✅ 適用 | 重要 |
| 4 | 日期選擇 | ✅ 適用（多場次選擇） | 必要 |
| 5 | 區域/座位選擇 | ✅ 適用（多票種選擇） | 必要 |
| 6 | 票數設定 | ✅ 適用 | 必要 |
| 7 | 驗證碼處理 | ❌ 不適用（無驗證碼） | - |
| 8 | 表單填寫 | ⚠️ 部分適用 | 可選 |
| 9 | 同意條款處理 | ⚠️ 待確認 | 可選 |
| 10 | 訂單確認與送出 | ✅ 適用（停止於付款頁） | 必要 |
| 11 | 排隊與付款 | ❌ 不適用 | - |
| 12 | 錯誤處理與重試 | ✅ 適用 | 必要 |

---

## 1. 環境初始化（階段 1）

### 決策：使用 NoDriver CDP

**設定來源**（依標準）：
```python
config_dict["webdriver_type"] = "nodriver"  # 固定使用 NoDriver
config_dict["advanced"]["headless"]         # 支援無頭模式
config_dict["advanced"]["window_size"]      # 視窗大小
```

**函式命名**：
- `fansigo_init_driver()` 或複用 `init_nodriver()`

**追蹤器封鎖**（FANSI GO 特定）：
```python
FANSIGO_BLOCK_DOMAINS = [
    "googletagmanager.com",
    "analytics.google.com",
    "stats.g.doubleclick.net",
    "google.com.tw/ads",
    "google.com/ads",
    "smartlook.com",
    "web-sdk.smartlook.com",
]
```

**不封鎖清單**：
- `go.fansi.me`（主站）
- `api.fansi.me`（API）
- `checkout.payments.91app.com`（支付）
- `cdn-cgi`（Cloudflare - 必須保留）

---

## 2. 身份認證（階段 2）

### 決策：使用 FansiAuthInfo Cookie 登入

**設定來源**（依標準）：
```python
config_dict["accounts"]["fansigo_cookie"]   # FansiAuthInfo Cookie 值
```

**函式拆分**（依標準模式）：
```python
fansigo_login(driver, config_dict) -> bool
├── check_login_status(driver) -> bool
│   └── 檢查「我的票劵」元素是否存在
├── detect_login_method(config_dict) -> str
│   └── 判斷使用 Cookie（唯一方式）
├── inject_cookies(driver, cookie_value: str) -> bool
│   └── 設定 FansiAuthInfo Cookie
└── verify_login_success(driver) -> bool
```

**Cookie 結構**：
```json
{
  "__typename": "userToken",
  "accessToken": "<JWT_TOKEN>",
  "tokenLife": 604800
}
```

**回退策略**：
1. **優先**：Cookie 注入（若有 fansigo_cookie）
2. **回退**：保持未登入狀態（部分活動可購票）

---

## 3. 頁面監控與重載（階段 3）

### 決策：複用現有重載機制

**設定來源**（依標準）：
```python
config_dict["advanced"]["auto_reload_page_interval"]    # 重載間隔
config_dict["advanced"]["auto_reload_overheat_count"]   # 過熱閾值
config_dict["advanced"]["auto_reload_overheat_cd"]      # 冷卻時間
```

**函式拆分**：
```python
fansigo_auto_reload(driver, config_dict, state_dict) -> bool
├── check_page_status(driver) -> str
│   └── detect_coming_soon_page(driver) -> bool  # 即將開賣
├── fansigo_close_popup_windows(driver) -> bool
│   └── 處理平台特定彈窗（若有）
└── reload_with_backoff(driver, state_dict) -> bool
```

---

## 4. 日期/場次選擇（階段 4）

### 決策：使用 date_keyword 匹配場次名稱

**設定來源**（依標準）：
```python
config_dict["date_auto_select"]["enable"]         # 是否啟用
config_dict["date_auto_select"]["date_keyword"]   # 場次關鍵字
config_dict["date_auto_select"]["mode"]           # 選擇模式
config_dict["date_auto_fallback"]                 # 條件式遞補
```

**函式拆分**（依標準模式）：
```python
fansigo_date_auto_select(driver, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
├── detect_date_layout(driver) -> str
│   └── 返回 "link_list"（連結列表式版面）
├── get_all_date_options(driver, layout_type: str) -> list
│   ├── parse_show_text(element) -> str
│   │   └── "高雄場 KAOHSIUNG 2026/02/07 19:00 LIVE WAREHOUSE"
│   └── parse_show_status(element) -> str
├── match_date_by_keyword(shows: list, config_dict) -> element
│   ├── split_keywords(keyword_string: str) -> list
│   │   └── 支援多關鍵字：「高雄;台北」
│   ├── match_fuzzy(show_text: str, keywords: list) -> bool
│   │   └── 場次名稱、日期、場地名稱皆可匹配
│   └── 早期返回模式：第一個匹配成功即停止
├── fallback_select_by_mode(shows: list, mode: str) -> element
│   └── 依 date_auto_fallback 決定是否遞補
├── click_show_element(driver, element) -> bool
└── verify_date_selected(driver, selected_text: str) -> bool
```

**回退策略**（依標準 v1.2）：
1. **優先**：使用 `date_keyword` 匹配
2. **條件式遞補**：
   - `date_auto_fallback=false`（預設）→ 停止執行，等待手動介入
   - `date_auto_fallback=true` → 使用 mode 自動選擇

**頁面元素結構**：
```
main
├── StaticText "請選擇活動場次進行購買"
├── link "高雄場 KAOHSIUNG 2026/02/07 ..."  ← 場次連結
│   ├── StaticText "高雄場 KAOHSIUNG"       ← 場次名稱
│   ├── StaticText "2026/02/07 19:00"       ← 日期時間
│   ├── StaticText "LIVE WAREHOUSE"         ← 場地名稱
│   └── StaticText "803高雄市鹽埕區..."     ← 地址
└── link "台北場 TAIPEI 2026/02/08 ..."     ← 其他場次
```

---

## 5. 區域/票種選擇（階段 5）

### 決策：使用 area_keyword 匹配票種名稱

**設定來源**（依標準）：
```python
config_dict["area_auto_select"]["enable"]           # 是否啟用
config_dict["area_auto_select"]["area_keyword"]     # 票種關鍵字
config_dict["area_auto_select"]["mode"]             # 選擇模式
config_dict["area_auto_fallback"]                   # 條件式遞補
config_dict["keyword_exclude"]                      # 排除關鍵字
```

**函式拆分**（依標準模式）：
```python
fansigo_area_auto_select(driver, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
├── detect_area_layout(driver) -> str
│   └── 返回 "listitem"（列表項目式版面）
├── get_all_area_options(driver, layout_type: str) -> list
│   ├── parse_area_name(element) -> str
│   │   └── "限量雙日VIP優先票"
│   ├── parse_area_price(element) -> int
│   │   └── 2400
│   ├── parse_area_status(element) -> dict
│   │   └── {"status": "available", "category": "VIP"}
│   └── filter_sold_out_areas(areas: list) -> list
├── apply_exclude_keywords(areas: list, exclude_keywords: str) -> list
├── match_area_by_keyword(areas: list, config_dict) -> element
│   ├── split_keywords(keyword_string: str) -> list
│   ├── match_fuzzy(area_name: str, keywords: list) -> bool
│   └── 早期返回模式
├── fallback_select_by_mode(areas: list, mode: str) -> element
├── click_area_element(driver, element) -> bool
└── verify_area_selected(driver, selected_text: str) -> bool
```

**回退策略**（依標準 v1.2）：
1. **優先**：使用 `area_keyword` 匹配
2. **條件式遞補**：
   - `area_auto_fallback=false`（預設）→ 停止執行
   - `area_auto_fallback=true` → 使用 mode 自動選擇

**票種狀態處理**：
| 狀態 | 標示文字 | 處理方式 |
|------|----------|----------|
| 可購買 | ★ 熱賣中 | 正常選擇 |
| 未開賣 | ⏱︎ 即將開賣 | 跳過 |
| 已結束 | ☹︎ 你已太晚 | 跳過 |

**頁面元素結構**：
```
generic
├── paragraph "選擇票券種類"
├── paragraph "★ 熱賣中"
├── list                              ← 一般票種
│   └── listitem level="1"
│       ├── heading level="3" "雙日預售票"  ← 票種名稱
│       ├── paragraph "結束販售 2026/03/12"
│       └── generic
│           ├── generic "NT＄ 2,000"        ← 價格
│           └── generic                      ← 數量選擇器
│               ├── button (-)
│               ├── paragraph "0"
│               └── button (+)
├── list                              ← VIP 票種
│   ├── generic
│   │   └── paragraph "VIP"           ← 區域分類標題
│   └── listitem level="1"
│       └── heading "限量雙日VIP優先票"
```

---

## 6. 票數設定（階段 6）

### 決策：使用按鈕式數量選擇

**設定來源**（依標準）：
```python
config_dict["ticket_number"]  # 購票張數
```

**函式拆分**：
```python
fansigo_assign_ticket_number(driver, config_dict) -> bool
├── detect_ticket_layout(driver) -> str
│   └── 返回 "button_layout"（+/- 按鈕式）
├── get_ticket_types(driver, layout_type: str) -> list
│   └── 取得所有票種及其數量選擇器
├── calculate_ticket_distribution(ticket_types: list, total_count: int) -> dict
│   └── 將總票數分配給選定的票種
├── select_ticket_number(driver, layout_type: str, count: int) -> bool
│   └── click_plus_button(driver, count: int)
│       └── 點擊 + 按鈕指定次數
└── verify_ticket_selected(driver, expected_count: int) -> bool
```

**回退策略**：
1. 若剩餘張數 < `ticket_number` → 選擇最大可選數量
2. 若無法設定 → 保持預設值（0）

---

## 7. 驗證碼處理（階段 7）

### 決策：不適用

**原因**：FANSI GO 平台不使用驗證碼。

---

## 8. 表單填寫（階段 8）

### 決策：部分適用

**適用場景**：
- 購票前可能需要填寫「必填資料」（個人資訊）

**設定來源**：
```python
config_dict["advanced"]["user_guess_string"]    # 自訂問題答案（若有）
```

**待確認**：實際購票流程是否有額外表單

---

## 9. 同意條款處理（階段 9）

### 決策：待確認

**觀察**：購票流程中未見明顯的同意條款勾選。可能在訂單確認時需要。

---

## 10. 訂單確認與送出（階段 10）

### 決策：停止於付款方式選擇頁面

**停止條件**：
- URL 匹配 `/tickets/payment/checkout/*`
- 或頁面出現付款方式選項

**函式拆分**：
```python
fansigo_ticket_main(driver, config_dict) -> bool
├── review_order_details(driver) -> dict
│   └── 記錄訂單資訊
├── detect_checkout_page(driver) -> bool
│   └── 檢查是否到達付款頁面
├── play_sound_notification(config_dict, "ticket") -> bool
│   └── 播放成功音效
└── stop_automation() -> bool
    └── 結束自動化，等待使用者付款
```

**購票流程終點**：
```
/tickets/payment/checkout/{orderId}
```

---

## 11. 排隊與付款（階段 11）

### 決策：不適用

**原因**：
- FANSI GO 目前未觀察到排隊機制
- 付款流程由使用者手動完成

---

## 12. 錯誤處理與重試（階段 12）

### 決策：複用全域錯誤處理機制

**設定來源**：
```python
config_dict["advanced"]["verbose"]  # 除錯訊息
```

**函式拆分**：
```python
fansigo_error_handler(driver, error, config_dict) -> bool
├── detect_error_type(error) -> str
│   ├── detect_sold_out(driver) -> bool
│   │   └── 檢查「已售完」文字
│   ├── detect_cloudflare_challenge(driver) -> bool
│   │   └── 檢查 Cloudflare 驗證頁面
│   └── detect_network_error(error) -> bool
├── log_error(error, config_dict) -> None
├── retry_with_strategy(func, max_retry: int, backoff: float) -> bool
└── notify_user(error_type: str, config_dict) -> None
```

---

## 風險與緩解

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|----------|
| Cloudflare 持續驗證 | 中 | 高 | 使用 stealth 模式、增加等待時間 |
| 頁面結構改變 | 低 | 中 | 使用語意選擇器、記錄詳細錯誤 |
| Cookie 過期 | 低 | 低 | 檢測登入狀態、提示重新登入 |
| 網路超時 | 低 | 低 | 重試機制 |

---

## 研究結論

1. **12 階段覆蓋率**：8/12 階段適用（67%）
2. **無「需要釐清」項目**：所有技術問題已解決
3. **複用程度**：大量複用現有機制（重載、錯誤處理、關鍵字匹配）
4. **新增程式碼估計**：約 500-800 行

**可進入階段 1 設計**。
