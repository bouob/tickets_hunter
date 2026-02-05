# 實作任務：FANSI GO 平台支援

**功能分支**：`012-fansigo-platform`
**建立日期**：2026-02-05
**規格文件**：[spec.md](./spec.md) | [plan.md](./plan.md) | [research.md](./research.md)

---

## 任務總覽

| 階段 | 任務數 | 優先級 | 預估複雜度 |
|------|--------|--------|------------|
| Phase 0: 設定與常數 | 3 | P0 | 低 |
| Phase 1: US1 基礎自動化 | 5 | P1 | 中 |
| Phase 2: US2 多場次選擇 | 3 | P1 | 中 |
| Phase 3: US3 Cookie 登入 | 3 | P2 | 低 |
| Phase 4: US4 追蹤器封鎖 | 2 | P3 | 低 |
| Phase 5: 整合與測試 | 3 | P1 | 中 |

**總任務數**：19

---

## Phase 0: 設定與常數

### T0.1: 新增 FANSI GO URL 模式識別

**優先級**：P0（前置任務）
**預估複雜度**：低
**相依性**：無

**描述**：
在 `nodriver_tixcraft.py` 或 `util.py` 新增 FANSI GO 網址模式識別常數和函數。

**實作細節**：
```python
# URL 模式常數
FANSIGO_URL_PATTERNS = {
    "domain": r"go\.fansi\.me",
    "event_page": r"go\.fansi\.me/events/(\d+)",
    "show_page": r"go\.fansi\.me/tickets/show/(\d+)",
    "checkout_page": r"go\.fansi\.me/tickets/payment/checkout/",
    "order_result": r"go\.fansi\.me/tickets/payment/orderresult/",
}

def is_fansigo_url(url: str) -> bool:
    """檢查是否為 FANSI GO 網址"""
    return bool(re.search(FANSIGO_URL_PATTERNS["domain"], url))

def get_fansigo_page_type(url: str) -> str:
    """取得 FANSI GO 頁面類型"""
    # 返回: "event", "show", "checkout", "order_result", "unknown"
```

**驗收標準**：
- [ ] URL 模式正確識別所有 FANSI GO 頁面類型
- [ ] `is_fansigo_url()` 正確回傳 True/False
- [ ] `get_fansigo_page_type()` 正確回傳頁面類型

---

### T0.2: 新增 fansigo_cookie 設定項（後端）

**優先級**：P0（前置任務）
**預估複雜度**：低
**相依性**：無
**對應需求**：FR-010

**描述**：
在 `settings.py` 新增 `fansigo_cookie` 設定項，支援 FansiAuthInfo Cookie 值。

**重要**：與其他平台 cookie 設定保持一致，放在 `accounts` 區塊（非 `advanced`）。

**實作細節**：
```python
# 在 accounts 區塊新增預設值（與 ibonqware, funone_session_cookie 同層級）
"accounts": {
    ...
    "fansigo_cookie": "",  # FansiAuthInfo Cookie 值
}
```

**驗收標準**：
- [ ] 設定項正確讀取和寫入
- [ ] 空值時不影響其他功能
- [ ] 設定檔向後相容
- [ ] 設定路徑與其他平台 cookie 一致（accounts 區塊）

---

### T0.3: 新增 fansigo_cookie 前端 UI

**優先級**：P0（前置任務）
**預估複雜度**：低
**相依性**：T0.2
**對應需求**：FR-010

**描述**：
在 `settings.html` 和 `settings.js` 新增 FANSI GO Cookie 輸入欄位。

**實作細節**：

**settings.html**（在 FunOne cookie 區塊後新增）：
```html
<div class="row mb-3">
  <label for="fansigo_cookie" class="col-sm-2 col-form-label">FANSI GO cookie (FansiAuthInfo)</label>
  <div class="col-sm-10 col-lg-8 col-xl-6">
    <input class="form-control" id="fansigo_cookie" value="" />
  </div>
</div>
```

**settings.js**：
```javascript
// 1. 宣告 DOM 元素（約第 65 行附近）
const fansigo_cookie = document.querySelector('#fansigo_cookie');

// 2. 載入設定值（約第 262 行附近）
fansigo_cookie.value = settings.accounts.fansigo_cookie || '';

// 3. 儲存設定值（約第 509 行附近）
settings.accounts.fansigo_cookie = fansigo_cookie.value;

// 4. 註冊欄位名稱（約第 630 行附近）
"fansigo_cookie",
```

**驗收標準**：
- [ ] UI 欄位正確顯示於設定頁面
- [ ] 輸入值正確儲存到 settings.json
- [ ] 頁面載入時正確顯示已儲存的值
- [ ] 欄位標籤使用「FANSI GO cookie (FansiAuthInfo)」

---

## Phase 1: US1 基礎購票自動化

### T1.1: 實作 fansigo_ticket_main 主流程

**優先級**：P1
**預估複雜度**：中
**相依性**：T0.1
**對應需求**：FR-001, FR-002

**描述**：
實作 FANSI GO 購票主流程函數，作為整個平台的入口點。

**實作細節**：
```python
async def fansigo_ticket_main(driver, url: str, config_dict: dict) -> bool:
    """FANSI GO 購票主流程

    流程：
    1. 檢查頁面類型
    2. 若為活動頁 → 選擇場次
    3. 若為購票頁 → 選擇票種、設定數量
    4. 檢查是否到達付款頁面
    5. 停止自動化
    """
    page_type = get_fansigo_page_type(url)

    if page_type == "event":
        # 選擇場次
        result = await fansigo_date_auto_select(driver, url, config_dict)
        if not result:
            return False

    if page_type in ("event", "show"):
        # 選擇票種
        result = await fansigo_area_auto_select(driver, url, config_dict)
        if not result:
            return False

        # 設定票數
        result = await fansigo_assign_ticket_number(driver, config_dict)
        if not result:
            return False

    # 檢查是否到達付款頁面
    if page_type == "checkout":
        await play_sound_notification(config_dict, "ticket")
        return True  # 停止自動化

    return True
```

**驗收標準**：
- [ ] 正確識別頁面類型並執行對應流程
- [ ] 活動頁自動導向購票頁
- [ ] 購票頁正確執行票種選擇和數量設定
- [ ] 付款頁面停止自動化並播放音效

---

### T1.2: 實作 fansigo_area_auto_select 票種選擇

**優先級**：P1
**預估複雜度**：中
**相依性**：T0.1
**對應需求**：FR-003, FR-004

**描述**：
實作票種自動選擇功能，支援關鍵字匹配和狀態過濾。

**實作細節**：
```python
async def fansigo_area_auto_select(driver, url: str, config_dict: dict) -> bool:
    """票種自動選擇

    設定來源：
    - config_dict["area_auto_select"]["enable"]
    - config_dict["area_auto_select"]["area_keyword"]
    - config_dict["area_auto_select"]["mode"]
    - config_dict["area_auto_fallback"]
    - config_dict["keyword_exclude"]
    """
    if not config_dict.get("area_auto_select", {}).get("enable", True):
        return True

    # 取得所有票種
    sections = await get_all_area_options(driver)

    # 過濾已售完/未開賣
    available_sections = [s for s in sections if s["status"] == "on_sale"]

    # 套用排除關鍵字
    exclude_keywords = config_dict.get("keyword_exclude", "")
    if exclude_keywords:
        available_sections = apply_exclude_keywords(available_sections, exclude_keywords)

    # 關鍵字匹配
    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "")
    matched = match_area_by_keyword(available_sections, area_keyword)

    if matched:
        return await click_area_element(driver, matched)

    # 遞補策略
    if config_dict.get("area_auto_fallback", False):
        mode = config_dict.get("area_auto_select", {}).get("mode", "from top to bottom")
        return await fallback_select_by_mode(driver, available_sections, mode)

    return False  # 無匹配且不遞補
```

**頁面選擇器**：
```python
# 票種列表
AREA_LIST_SELECTOR = "list"
AREA_ITEM_SELECTOR = "listitem[level='1']"

# 票種名稱（heading level 3）
AREA_NAME_SELECTOR = "heading[level='3']"

# 票種價格
AREA_PRICE_SELECTOR = "generic:has-text('NT')"

# 狀態標示
STATUS_ON_SALE = "hotSelling"      # ★ 熱賣中
STATUS_COMING = "coming"           # ⏱︎ 即將開賣
STATUS_ENDED = "ended"             # ☹︎ 你已太晚
```

**驗收標準**：
- [ ] 正確取得所有票種選項
- [ ] 過濾非可購買狀態（未開賣、已結束、售完）
- [ ] 關鍵字匹配支援多關鍵字（分號分隔）
- [ ] 排除關鍵字正確運作
- [ ] 遞補策略依 mode 設定執行

---

### T1.3: 實作 fansigo_assign_ticket_number 票數設定

**優先級**：P1
**預估複雜度**：低
**相依性**：T1.2
**對應需求**：FR-005

**描述**：
實作票數設定功能，使用 +/- 按鈕式介面。

**實作細節**：
```python
async def fansigo_assign_ticket_number(driver, config_dict: dict) -> bool:
    """設定購票張數

    設定來源：
    - config_dict["ticket_number"]
    """
    target_count = config_dict.get("ticket_number", 1)

    # 取得目前選擇的票種的數量選擇器
    plus_button = await driver.find("button:has-text('+')")

    # 點擊 + 按鈕指定次數
    for _ in range(target_count):
        await plus_button.click()
        await asyncio.sleep(0.1)

    # 驗證數量
    count_display = await driver.find("paragraph", near=plus_button)
    actual_count = int(await count_display.get_text())

    return actual_count == target_count
```

**驗收標準**：
- [ ] 正確點擊 + 按鈕設定數量
- [ ] 驗證最終數量與設定一致
- [ ] 處理剩餘票數不足的情況

---

### T1.4: 實作付款頁面偵測與停止

**優先級**：P1
**預估複雜度**：低
**相依性**：T1.1
**對應需求**：FR-006

**描述**：
偵測是否到達付款頁面，並停止自動化流程。

**實作細節**：
```python
async def detect_checkout_page(driver, url: str) -> bool:
    """檢查是否到達付款頁面"""
    if re.search(FANSIGO_URL_PATTERNS["checkout_page"], url):
        return True

    # 備用：檢查頁面元素
    payment_method = await driver.find("heading:has-text('付款方式')", timeout=1)
    return payment_method is not None

async def stop_at_checkout(driver, config_dict: dict) -> bool:
    """到達付款頁面時停止並通知"""
    # 播放音效
    await play_sound_notification(config_dict, "ticket")

    # 記錄日誌
    print("[FANSI GO] 已到達付款頁面，自動化停止")

    return True
```

**驗收標準**：
- [ ] 正確偵測付款頁面 URL
- [ ] 播放成功音效通知使用者
- [ ] 不進行任何付款操作

---

### T1.5: 實作錯誤處理與重試機制

**優先級**：P1
**預估複雜度**：中
**相依性**：T1.1
**對應需求**：FR-010

**描述**：
實作錯誤處理機制，支援常見錯誤類型的偵測與重試。

**實作細節**：
```python
async def fansigo_error_handler(driver, error: Exception, config_dict: dict) -> bool:
    """錯誤處理

    錯誤類型：
    - sold_out: 票券已售完
    - cloudflare: Cloudflare 驗證
    - network: 網路錯誤
    - timeout: 超時
    """
    error_type = detect_error_type(error)

    if error_type == "sold_out":
        print("[FANSI GO] 票券已售完")
        return False

    if error_type == "cloudflare":
        print("[FANSI GO] 偵測到 Cloudflare 驗證，請手動完成")
        await asyncio.sleep(10)  # 等待使用者完成驗證
        return True  # 繼續執行

    if error_type == "network":
        print("[FANSI GO] 網路錯誤，重試中...")
        await asyncio.sleep(2)
        return True  # 重試

    return False

def detect_error_type(error: Exception) -> str:
    """偵測錯誤類型"""
    error_str = str(error).lower()

    if "sold out" in error_str or "sold_out" in error_str:
        return "sold_out"
    if "cloudflare" in error_str or "challenge" in error_str:
        return "cloudflare"
    if "network" in error_str or "connection" in error_str:
        return "network"
    if "timeout" in error_str:
        return "timeout"

    return "unknown"
```

**驗收標準**：
- [ ] 正確偵測各類錯誤
- [ ] Cloudflare 驗證時等待使用者介入
- [ ] 網路錯誤時自動重試
- [ ] 售完時停止並通知

---

## Phase 2: US2 多場次選擇

### T2.1: 實作 fansigo_date_auto_select 場次選擇

**優先級**：P1
**預估複雜度**：中
**相依性**：T0.1
**對應需求**：FR-007

**描述**：
實作多場次自動選擇功能，支援關鍵字匹配。

**實作細節**：
```python
async def fansigo_date_auto_select(driver, url: str, config_dict: dict) -> bool:
    """場次自動選擇

    設定來源：
    - config_dict["date_auto_select"]["enable"]
    - config_dict["date_auto_select"]["date_keyword"]
    - config_dict["date_auto_select"]["mode"]
    - config_dict["date_auto_fallback"]

    頁面結構：
    - 場次以連結列表呈現
    - 每個連結包含：場次名稱、日期時間、場地、地址
    """
    if not config_dict.get("date_auto_select", {}).get("enable", True):
        return True

    # 檢查是否為活動頁面
    if not re.search(FANSIGO_URL_PATTERNS["event_page"], url):
        return True  # 非活動頁面，跳過場次選擇

    # 取得所有場次
    shows = await get_all_date_options(driver)

    if len(shows) == 0:
        return False

    if len(shows) == 1:
        # 單一場次，直接點擊
        return await click_show_element(driver, shows[0])

    # 多場次，使用關鍵字匹配
    date_keyword = config_dict.get("date_auto_select", {}).get("date_keyword", "")
    matched = match_date_by_keyword(shows, date_keyword)

    if matched:
        return await click_show_element(driver, matched)

    # 遞補策略
    if config_dict.get("date_auto_fallback", False):
        mode = config_dict.get("date_auto_select", {}).get("mode", "from top to bottom")
        return await fallback_select_by_mode(driver, shows, mode)

    return False
```

**驗收標準**：
- [ ] 正確取得所有場次選項
- [ ] 單一場次時直接選擇
- [ ] 多場次時使用關鍵字匹配
- [ ] 遞補策略正確執行

---

### T2.2: 實作場次資訊解析

**優先級**：P1
**預估複雜度**：低
**相依性**：T2.1

**描述**：
解析場次連結中的資訊，供關鍵字匹配使用。

**實作細節**：
```python
async def get_all_date_options(driver) -> list:
    """取得所有場次選項

    返回格式：
    [
        {
            "element": <element>,
            "text": "高雄場 KAOHSIUNG 2026/02/07 19:00 LIVE WAREHOUSE",
            "name": "高雄場 KAOHSIUNG",
            "datetime": "2026/02/07 19:00",
            "venue": "LIVE WAREHOUSE"
        },
        ...
    ]
    """
    # 找到場次列表
    show_links = await driver.find_all("link", near="請選擇活動場次進行購買")

    shows = []
    for link in show_links:
        text = await link.get_text()
        shows.append({
            "element": link,
            "text": text,
            "name": parse_show_name(text),
            "datetime": parse_show_datetime(text),
            "venue": parse_show_venue(text),
        })

    return shows

def parse_show_name(text: str) -> str:
    """解析場次名稱"""
    # 範例：「高雄場 KAOHSIUNG 2026/02/07 19:00 LIVE WAREHOUSE」
    # 取「高雄場 KAOHSIUNG」
    match = re.match(r"^(.+?)\s+\d{4}/", text)
    return match.group(1) if match else text

def parse_show_datetime(text: str) -> str:
    """解析日期時間"""
    match = re.search(r"(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})", text)
    return match.group(1) if match else ""

def parse_show_venue(text: str) -> str:
    """解析場地名稱"""
    match = re.search(r"\d{2}:\d{2}\s+(.+?)(?:\s+\d{3}|$)", text)
    return match.group(1) if match else ""
```

**驗收標準**：
- [ ] 正確解析場次名稱
- [ ] 正確解析日期時間
- [ ] 正確解析場地名稱

---

### T2.3: 實作場次關鍵字匹配

**優先級**：P1
**預估複雜度**：低
**相依性**：T2.2

**描述**：
實作場次關鍵字匹配邏輯，支援多種匹配模式。

**實作細節**：
```python
def match_date_by_keyword(shows: list, keyword_string: str) -> dict:
    """依關鍵字匹配場次

    匹配優先級：
    1. 完整匹配場次名稱
    2. 部分匹配場次名稱
    3. 匹配日期
    4. 匹配場地名稱

    支援多關鍵字（分號分隔），依序嘗試
    """
    if not keyword_string:
        return None

    keywords = split_keywords(keyword_string)

    for keyword in keywords:
        # 嘗試各種匹配方式
        for show in shows:
            if match_fuzzy(show["text"], keyword):
                return show

    return None

def split_keywords(keyword_string: str) -> list:
    """分割關鍵字字串"""
    return [k.strip() for k in keyword_string.split(";") if k.strip()]

def match_fuzzy(text: str, keyword: str) -> bool:
    """模糊匹配"""
    return keyword.lower() in text.lower()
```

**驗收標準**：
- [ ] 支援城市名稱匹配（「高雄」「台北」）
- [ ] 支援日期匹配（「02/07」「2026/02/08」）
- [ ] 支援場地名稱匹配（「WAREHOUSE」「Pipe」）
- [ ] 多關鍵字依序優先匹配

---

## Phase 3: US3 Cookie 登入

### T3.1: 實作 fansigo_login 登入函數

**優先級**：P2
**預估複雜度**：低
**相依性**：T0.2
**對應需求**：FR-008

**描述**：
實作 Cookie 登入功能。

**實作細節**：
```python
async def fansigo_login(driver, config_dict: dict) -> bool:
    """FANSI GO Cookie 登入

    設定來源：
    - config_dict["accounts"]["fansigo_cookie"]
    """
    cookie_value = config_dict.get("accounts", {}).get("fansigo_cookie", "")

    if not cookie_value:
        print("[FANSI GO] 未設定 Cookie，以訪客身份繼續")
        return True

    # 注入 Cookie
    result = await inject_fansigo_cookie(driver, cookie_value)

    if result:
        # 驗證登入狀態
        return await verify_login_success(driver)

    return False
```

**驗收標準**：
- [ ] 正確注入 FansiAuthInfo Cookie
- [ ] 驗證登入狀態
- [ ] 無 Cookie 時以訪客身份繼續

---

### T3.2: 實作 Cookie 注入

**優先級**：P2
**預估複雜度**：低
**相依性**：T3.1

**描述**：
實作 Cookie 注入邏輯。

**實作細節**：
```python
async def inject_fansigo_cookie(driver, cookie_value: str) -> bool:
    """注入 FansiAuthInfo Cookie

    Cookie 格式：
    - 名稱：FansiAuthInfo
    - 值：URL Encoded JSON
    - Domain：go.fansi.me
    - Path：/
    """
    try:
        await driver.cookies.set({
            "name": "FansiAuthInfo",
            "value": cookie_value,
            "domain": "go.fansi.me",
            "path": "/",
        })
        return True
    except Exception as e:
        print(f"[FANSI GO] Cookie 注入失敗: {e}")
        return False
```

**驗收標準**：
- [ ] Cookie 正確設定到 go.fansi.me 域名
- [ ] 處理注入失敗的情況

---

### T3.3: 實作登入狀態驗證

**優先級**：P2
**預估複雜度**：低
**相依性**：T3.2

**描述**：
驗證 Cookie 登入是否成功。

**實作細節**：
```python
async def verify_login_success(driver) -> bool:
    """驗證登入狀態

    檢查方式：
    - 頁面是否顯示「我的票劵」連結
    """
    try:
        my_tickets = await driver.find("link:has-text('我的票劵')", timeout=3)
        return my_tickets is not None
    except:
        return False

async def check_login_status(driver) -> bool:
    """檢查當前登入狀態"""
    return await verify_login_success(driver)
```

**驗收標準**：
- [ ] 正確偵測「我的票劵」元素
- [ ] 登入成功返回 True
- [ ] 未登入返回 False

---

## Phase 4: US4 追蹤器封鎖

### T4.1: 定義封鎖清單

**優先級**：P3
**預估複雜度**：低
**相依性**：無
**對應需求**：FR-009

**描述**：
定義 FANSI GO 平台的追蹤器封鎖清單。

**實作細節**：
```python
FANSIGO_BLOCK_DOMAINS = [
    # Google Analytics / Tag Manager
    "googletagmanager.com",
    "analytics.google.com",
    "stats.g.doubleclick.net",
    "google.com.tw/ads",
    "google.com/ads",

    # Smartlook
    "smartlook.com",
    "web-sdk.smartlook.com",
]

FANSIGO_ALLOW_DOMAINS = [
    # 主站
    "go.fansi.me",
    "api.fansi.me",

    # 支付
    "checkout.payments.91app.com",

    # Cloudflare（必須保留）
    "cdn-cgi",
    "challenges.cloudflare.com",
]
```

**驗收標準**：
- [ ] 封鎖清單包含所有追蹤器域名
- [ ] 不封鎖清單包含必要服務
- [ ] Cloudflare 相關域名不被封鎖

---

### T4.2: 實作請求攔截

**優先級**：P3
**預估複雜度**：中
**相依性**：T4.1

**描述**：
實作 NoDriver CDP 請求攔截，封鎖追蹤器請求。

**實作細節**：
```python
async def setup_fansigo_request_interception(driver) -> bool:
    """設定 FANSI GO 請求攔截

    使用 NoDriver CDP 的 Fetch domain
    """
    async def request_paused_handler(event):
        request_url = event["request"]["url"]

        # 檢查是否需要封鎖
        should_block = any(
            domain in request_url
            for domain in FANSIGO_BLOCK_DOMAINS
        )

        # 檢查是否在允許清單
        should_allow = any(
            domain in request_url
            for domain in FANSIGO_ALLOW_DOMAINS
        )

        if should_block and not should_allow:
            # 封鎖請求
            await driver.execute_cdp_cmd("Fetch.failRequest", {
                "requestId": event["requestId"],
                "errorReason": "BlockedByClient"
            })
        else:
            # 繼續請求
            await driver.execute_cdp_cmd("Fetch.continueRequest", {
                "requestId": event["requestId"]
            })

    # 啟用 Fetch domain
    await driver.execute_cdp_cmd("Fetch.enable", {
        "patterns": [{"urlPattern": "*"}]
    })

    # 註冊事件處理器
    driver.add_cdp_listener("Fetch.requestPaused", request_paused_handler)

    return True
```

**驗收標準**：
- [ ] 正確封鎖追蹤器請求
- [ ] 不影響正常頁面載入
- [ ] 不封鎖付款相關請求

---

## Phase 5: 整合與測試

### T5.1: 整合到主程式迴圈

**優先級**：P1
**預估複雜度**：中
**相依性**：Phase 1, 2, 3, 4

**描述**：
將 FANSI GO 功能整合到 `nodriver_tixcraft.py` 主程式迴圈。

**實作細節**：
```python
# 在主程式迴圈中加入 FANSI GO 處理
async def main_loop(driver, config_dict):
    url = await driver.current_url()

    # 檢查是否為 FANSI GO 網址
    if is_fansigo_url(url):
        # 設定請求攔截（首次）
        if not fansigo_interception_setup:
            await setup_fansigo_request_interception(driver)
            fansigo_interception_setup = True

        # 執行 Cookie 登入（首次）
        if not fansigo_logged_in:
            await fansigo_login(driver, config_dict)
            fansigo_logged_in = True

        # 執行購票主流程
        await fansigo_ticket_main(driver, url, config_dict)
        return

    # 其他平台處理...
```

**驗收標準**：
- [ ] FANSI GO 網址正確進入專屬流程
- [ ] 不影響其他平台功能
- [ ] 狀態正確管理（登入、攔截設定）

---

### T5.2: 建立單元測試

**優先級**：P1
**預估複雜度**：中
**相依性**：Phase 1, 2, 3

**描述**：
建立 FANSI GO 功能的單元測試。

**實作細節**：
```python
# tests/unit/test_fansigo.py

import pytest
from src.nodriver_tixcraft import (
    is_fansigo_url,
    get_fansigo_page_type,
    match_date_by_keyword,
    match_area_by_keyword,
    split_keywords,
)

class TestFansigoUrlPatterns:
    def test_is_fansigo_url_event_page(self):
        assert is_fansigo_url("https://go.fansi.me/events/590002") == True

    def test_is_fansigo_url_show_page(self):
        assert is_fansigo_url("https://go.fansi.me/tickets/show/150006") == True

    def test_is_fansigo_url_other_site(self):
        assert is_fansigo_url("https://tixcraft.com/event/123") == False

    def test_get_page_type_event(self):
        assert get_fansigo_page_type("https://go.fansi.me/events/590002") == "event"

    def test_get_page_type_show(self):
        assert get_fansigo_page_type("https://go.fansi.me/tickets/show/150006") == "show"

class TestKeywordMatching:
    def test_split_keywords_single(self):
        assert split_keywords("VIP") == ["VIP"]

    def test_split_keywords_multiple(self):
        assert split_keywords("VIP;雙日;單日") == ["VIP", "雙日", "單日"]

    def test_match_date_by_city(self):
        shows = [
            {"text": "高雄場 KAOHSIUNG 2026/02/07"},
            {"text": "台北場 TAIPEI 2026/02/08"},
        ]
        result = match_date_by_keyword(shows, "高雄")
        assert result["text"].startswith("高雄場")

    def test_match_area_by_keyword(self):
        areas = [
            {"name": "雙日預售票", "status": "on_sale"},
            {"name": "限量雙日VIP優先票", "status": "on_sale"},
        ]
        result = match_area_by_keyword(areas, "VIP")
        assert "VIP" in result["name"]
```

**驗收標準**：
- [ ] URL 模式測試覆蓋所有情況
- [ ] 關鍵字匹配測試覆蓋主要場景
- [ ] 測試通過率 100%

---

### T5.3: 更新文件

**優先級**：P1
**預估複雜度**：低
**相依性**：Phase 1, 2, 3, 4

**描述**：
更新專案文件，包含 FANSI GO 平台支援說明。

**更新清單**：
- [ ] `docs/02-development/structure.md`：新增 FANSI GO 相關函數
- [ ] `docs/01-guides/user-guide.md`：新增 FANSI GO 使用說明
- [ ] `README.md`：新增 FANSI GO 到支援平台列表

**驗收標準**：
- [ ] structure.md 包含所有新增函數
- [ ] 使用說明清楚易懂
- [ ] README 更新支援平台列表

---

## 任務相依圖

```
T0.1 ──┬──► T1.1 ──┬──► T1.4 ──► T5.1
       │           │
       │           └──► T1.5
       │
       ├──► T1.2 ──► T1.3
       │
       └──► T2.1 ──► T2.2 ──► T2.3

T0.2 ──► T3.1 ──► T3.2 ──► T3.3

T4.1 ──► T4.2

T5.1 ◄── All above
     │
     └──► T5.2 ──► T5.3
```

---

## 驗收檢查清單

### 功能驗收

- [ ] **US1**：可從活動頁完成基礎購票流程
- [ ] **US2**：多場次活動可依關鍵字選擇
- [ ] **US3**：Cookie 登入正常運作
- [ ] **US4**：追蹤器請求被封鎖

### 品質驗收

- [ ] 所有單元測試通過
- [ ] 無 .py 檔案包含 emoji
- [ ] 文件已同步更新
- [ ] 程式碼符合專案風格

### 相容性驗收

- [ ] 不影響現有平台功能
- [ ] 設定檔向後相容
- [ ] Windows/Linux/macOS 皆可執行
