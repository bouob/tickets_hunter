# 資料模型設計：Ticketmaster.com NoDriver 遷移

**專案**: Tickets Hunter - 多平台搶票自動化系統
**功能**: Ticketmaster.com NoDriver 平台遷移
**版本**: 1.0.0
**建立日期**: 2025-11-15
**相關規格**: `spec.md`

---

## 目錄

1. [設計原則](#設計原則)
2. [核心實體](#核心實體)
3. [實體關聯圖](#實體關聯圖)
4. [資料驗證規則](#資料驗證規則)
5. [狀態轉換](#狀態轉換)

---

## 設計原則

本資料模型設計遵循專案憲章第 II 條「資料結構優先」原則：

1. **結構決定一切** - 資料結構設計先於實作
2. **不變性約束** - 明確定義欄位的合法值與驗證規則
3. **最小化狀態** - 避免冗餘資料，單一真實來源
4. **可測試性** - 資料結構設計便於單元測試

---

## 核心實體

### 1. 演出場次 (Event Date)

代表單一演出的日期與時間資訊，對應 Ticketmaster.com 活動頁面中的可選擇場次。

**實體定義**：

```python
@dataclass
class EventDate:
    """演出場次實體"""

    # 主鍵
    event_id: str                    # 演出唯一識別碼（從 URL 或 DOM 提取）

    # 核心欄位
    date_text: str                   # 日期文字（例："2025-12-25" 或 "Christmas Special"）
    event_name: str                  # 演出名稱（例："Taylor Swift - Eras Tour"）
    availability_status: str         # 可用狀態："available" | "sold_out" | "coming_soon"
    see_tickets_link: Optional[str]  # "See Tickets" 連結 URL

    # 額外資訊（選填）
    venue_name: Optional[str] = None      # 場館名稱
    event_time: Optional[str] = None      # 演出時間（若頁面提供）
    price_range: Optional[str] = None     # 票價範圍（若頁面提供）

    # 元資訊
    matched_keywords: List[str] = field(default_factory=list)  # 匹配到的關鍵字
    dom_element_index: Optional[int] = None  # DOM 元素索引（用於定位）
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `event_id` | `str` | 是 | - | 演出唯一識別碼，用於追蹤與定位 |
| `date_text` | `str` | 是 | - | 從 DOM 提取的日期文字，用於關鍵字匹配 |
| `event_name` | `str` | 是 | - | 演出名稱，用於關鍵字匹配與日誌輸出 |
| `availability_status` | `str` | 是 | - | 可用狀態，決定是否可選擇此場次 |
| `see_tickets_link` | `Optional[str]` | 否 | `None` | 購票連結，若為 `None` 則該場次不可選擇 |
| `venue_name` | `Optional[str]` | 否 | `None` | 場館名稱，用於關鍵字匹配（若設定檔支援） |
| `event_time` | `Optional[str]` | 否 | `None` | 演出時間，用於時間關鍵字匹配（若設定檔支援） |
| `price_range` | `Optional[str]` | 否 | `None` | 票價範圍，用於價格篩選（若設定檔支援） |
| `matched_keywords` | `List[str]` | 否 | `[]` | 記錄匹配到的關鍵字，用於除錯 |
| `dom_element_index` | `Optional[int]` | 否 | `None` | DOM 元素索引，用於精確定位點擊目標 |

**實體關聯**：
- **1:N** 與 Configuration - 一個 Configuration 可匹配多個 EventDate
- **1:1** 與 DOM 元素 - 每個 EventDate 對應頁面中一個 `div.accordion-wrapper > div` 元素

**資料來源**：`#list-view > div > div.event-listing > div.accordion-wrapper > div`

---

### 2. 座位區域 (Zone)

代表可供選擇的座位區塊，對應 Ticketmaster.com 座位選擇頁面中的 `zone_info` JavaScript 變數。

**實體定義**：

```python
@dataclass
class Zone:
    """座位區域實體"""

    # 主鍵
    zone_id: str                     # 區域唯一識別碼（例："zone_1", "zone_2"）

    # 核心欄位（來自 zone_info JSON）
    area_status: str                 # 區域狀態："AVAILABLE" | "UNAVAILABLE"
    group_name: str                  # 區域名稱（例："VIP區", "一般區"）
    description: str                 # 區域描述（例："最佳視野", "受限視野"）
    ticket_price: str                # 票價（字串格式，例："3500"）

    # 額外資訊（選填）
    price_currency: str = "TWD"      # 貨幣單位
    seat_count: Optional[int] = None # 剩餘座位數（若 API 提供）

    # 元資訊
    matched_keywords: List[str] = field(default_factory=list)  # 匹配到的關鍵字
    excluded_keywords: List[str] = field(default_factory=list) # 排除的關鍵字
    match_priority: int = 0          # 匹配優先級（用於多組關鍵字回退）
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `zone_id` | `str` | 是 | - | 區域唯一識別碼，對應 zone_info 的鍵值 |
| `area_status` | `str` | 是 | - | 區域狀態，必須為 "AVAILABLE" 或 "UNAVAILABLE" |
| `group_name` | `str` | 是 | - | 區域名稱，用於關鍵字匹配 |
| `description` | `str` | 是 | - | 區域描述，用於關鍵字匹配與排除 |
| `ticket_price` | `str` | 是 | - | 票價（字串格式），用於價格篩選 |
| `price_currency` | `str` | 否 | `"TWD"` | 貨幣單位，預設為新台幣 |
| `seat_count` | `Optional[int]` | 否 | `None` | 剩餘座位數，若 API 不提供則為 None |
| `matched_keywords` | `List[str]` | 否 | `[]` | 記錄匹配到的關鍵字，用於除錯 |
| `excluded_keywords` | `List[str]` | 否 | `[]` | 記錄排除的關鍵字，用於除錯 |
| `match_priority` | `int` | 否 | `0` | 匹配優先級，數字越小優先級越高 |

**實體關聯**：
- **1:N** 與 Configuration - 一個 Configuration 可匹配多個 Zone
- **1:1** 與 zone_info JSON - 每個 Zone 對應 zone_info 中的一個物件

**資料來源**：從 `#mapSelectArea` 元素的 `innerHTML` 中提取 JavaScript 變數 `zone`

**zone_info JSON 範例**：

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [
      {
        "ticketPrice": "3500"
      }
    ]
  },
  "zone_2": {
    "areaStatus": "UNAVAILABLE",
    "groupName": "一般區",
    "description": "標準座位",
    "price": [
      {
        "ticketPrice": "1500"
      }
    ]
  }
}
```

---

### 3. 設定檔項目 (Configuration)

控制自動化行為的參數，來源為 `settings.json`。

**實體定義**：

```python
@dataclass
class TicketmasterConfig:
    """Ticketmaster 自動化設定"""

    # 日期選擇設定
    date_auto_select_enable: bool                # 是否啟用日期自動選擇
    date_keyword: str                            # 日期關鍵字（逗號分隔）
    auto_select_mode: str                        # 選擇模式："from top to bottom" | "from bottom to top" | "random"
    pass_date_is_sold_out: bool                  # 是否跳過已售罄場次

    # 區域選擇設定
    area_auto_select_enable: bool                # 是否啟用區域自動選擇
    area_keyword: str                            # 區域關鍵字（JSON 陣列格式）
    area_exclude_keyword: Optional[str] = None   # 排除關鍵字（逗號分隔）

    # 票數設定
    ticket_number: int = 1                       # 購票張數

    # 驗證碼設定
    ocr_captcha_enable: bool = False             # 是否啟用 OCR 驗證碼辨識

    # 促銷碼設定
    promo_code: Optional[str] = None             # 促銷碼（若有）

    # 進階設定
    verbose: bool = False                        # 是否啟用詳細日誌
    auto_reload_coming_soon_page: bool = False   # 是否自動重載「即將開賣」頁面

    # 回退策略
    area_keyword_fallback_enable: bool = True    # 是否啟用區域關鍵字回退機制
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 | 對應 FR |
|---------|------|------|--------|------|---------|
| `date_auto_select_enable` | `bool` | 是 | - | 是否啟用日期自動選擇 | FR-001 |
| `date_keyword` | `str` | 是 | - | 日期關鍵字，多組以逗號分隔 | FR-001 |
| `auto_select_mode` | `str` | 是 | - | 選擇策略（由上到下/由下到上/隨機） | FR-001 |
| `pass_date_is_sold_out` | `bool` | 是 | - | 是否跳過已售罄場次 | FR-003 |
| `area_auto_select_enable` | `bool` | 是 | - | 是否啟用區域自動選擇 | FR-005 |
| `area_keyword` | `str` | 是 | - | 區域關鍵字（JSON 陣列格式） | FR-005, FR-006 |
| `area_exclude_keyword` | `Optional[str]` | 否 | `None` | 排除關鍵字（逗號分隔） | spec.md User Story 2 |
| `ticket_number` | `int` | 否 | `1` | 購票張數 | FR-008 |
| `ocr_captcha_enable` | `bool` | 否 | `False` | 是否啟用 OCR 驗證碼辨識 | FR-011 |
| `promo_code` | `Optional[str]` | 否 | `None` | 促銷碼 | FR-010 |
| `verbose` | `bool` | 否 | `False` | 是否啟用詳細日誌 | FR-015 |
| `auto_reload_coming_soon_page` | `bool` | 否 | `False` | 是否自動重載「即將開賣」頁面 | research.md 函數 1 |
| `area_keyword_fallback_enable` | `bool` | 否 | `True` | 是否啟用區域關鍵字回退機制 | FR-006 |

**實體關聯**：
- **1:1** 與 settings.json - 從 settings.json 載入並驗證

**資料來源**：`settings.json` 檔案

---

### 4. 失敗記錄 (Failure List)

記錄已嘗試但失敗的項目（如促銷碼、驗證碼答案），用於避免重複嘗試相同失敗的操作。

**實體定義**：

```python
@dataclass
class FailureRecord:
    """失敗記錄實體"""

    # 主鍵
    record_id: str                   # 記錄唯一識別碼（UUID）

    # 核心欄位
    failure_type: str                # 失敗類型："promo_code" | "captcha_answer" | "area_selection" | "date_selection"
    failed_value: str                # 失敗的值（例：錯誤的促銷碼）
    timestamp: str                   # 失敗時間（ISO 8601 格式）

    # 額外資訊
    error_message: Optional[str] = None  # 錯誤訊息
    retry_count: int = 0                 # 重試次數
    platform: str = "ticketmaster"       # 平台名稱
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `record_id` | `str` | 是 | - | 記錄唯一識別碼（UUID v4） |
| `failure_type` | `str` | 是 | - | 失敗類型，必須為合法的類型值 |
| `failed_value` | `str` | 是 | - | 失敗的具體值 |
| `timestamp` | `str` | 是 | - | 失敗時間（ISO 8601 格式） |
| `error_message` | `Optional[str]` | 否 | `None` | 錯誤訊息，用於除錯 |
| `retry_count` | `int` | 否 | `0` | 重試次數，用於防止無限重試 |
| `platform` | `str` | 否 | `"ticketmaster"` | 平台名稱，用於跨平台區分 |

**實體關聯**：
- **N:1** 與 Configuration - 多個 FailureRecord 可能與同一個 Configuration 相關

**資料持久化**：記憶體中維護，程序結束時清除（不持久化到檔案）

**使用場景**（對應 FR）：
- **促銷碼失敗記錄** - FR-010: 記錄失敗的促銷碼避免重複嘗試
- **驗證碼答案失敗記錄** - spec.md User Story 4: 記錄失敗的驗證碼答案

---

## 實體關聯圖

```
┌─────────────────────────────┐
│     Configuration           │
│  (settings.json)            │
│                             │
│  - date_keyword             │
│  - area_keyword             │
│  - ticket_number            │
│  - promo_code               │
│  - ...                      │
└──────────┬──────────────────┘
           │
           │ 1
           │
           │ N
     ┌─────┴──────┐
     │            │
     ▼            ▼
┌──────────┐  ┌──────────┐
│EventDate │  │  Zone    │
│          │  │          │
│-event_id │  │-zone_id  │
│-date_text│  │-group_name│
│-status   │  │-status   │
└──────────┘  └──────────┘
     │            │
     │ N          │ N
     │            │
     ▼            ▼
┌─────────────────────────┐
│   FailureRecord         │
│                         │
│  - record_id            │
│  - failure_type         │
│  - failed_value         │
│  - timestamp            │
└─────────────────────────┘
```

**關聯說明**：

1. **Configuration → EventDate** (1:N)
   - 一個 Configuration 可匹配多個 EventDate
   - EventDate 的 `matched_keywords` 欄位記錄匹配來源

2. **Configuration → Zone** (1:N)
   - 一個 Configuration 可匹配多個 Zone
   - Zone 的 `matched_keywords` 欄位記錄匹配來源

3. **EventDate/Zone → FailureRecord** (N:N 間接關聯)
   - 當選擇失敗時建立 FailureRecord
   - FailureRecord 的 `failure_type` 欄位區分失敗來源

---

## 資料驗證規則

### 1. EventDate 驗證規則

**來源**: spec.md FR-002, FR-003

```python
def validate_event_date(event: EventDate) -> bool:
    """驗證 EventDate 實體的合法性"""

    # 規則 1: availability_status 必須為合法值
    valid_statuses = ["available", "sold_out", "coming_soon"]
    if event.availability_status not in valid_statuses:
        raise ValueError(f"Invalid availability_status: {event.availability_status}")

    # 規則 2: 若 availability_status 為 "available"，則 see_tickets_link 必須存在
    if event.availability_status == "available" and not event.see_tickets_link:
        raise ValueError("Available events must have see_tickets_link")

    # 規則 3: date_text 不得為空字串
    if not event.date_text or event.date_text.strip() == "":
        raise ValueError("date_text cannot be empty")

    # 規則 4: event_name 不得為空字串
    if not event.event_name or event.event_name.strip() == "":
        raise ValueError("event_name cannot be empty")

    return True
```

### 2. Zone 驗證規則

**來源**: spec.md FR-005

```python
def validate_zone(zone: Zone) -> bool:
    """驗證 Zone 實體的合法性"""

    # 規則 1: area_status 必須為 "AVAILABLE" 或 "UNAVAILABLE"
    valid_statuses = ["AVAILABLE", "UNAVAILABLE"]
    if zone.area_status not in valid_statuses:
        raise ValueError(f"Invalid area_status: {zone.area_status}")

    # 規則 2: group_name 不得為空字串
    if not zone.group_name or zone.group_name.strip() == "":
        raise ValueError("group_name cannot be empty")

    # 規則 3: ticket_price 必須為正數字串
    try:
        price = float(zone.ticket_price)
        if price < 0:
            raise ValueError("ticket_price must be non-negative")
    except ValueError:
        raise ValueError(f"Invalid ticket_price format: {zone.ticket_price}")

    # 規則 4: zone_id 必須符合 "zone_X" 格式（X 為數字）
    if not zone.zone_id.startswith("zone_"):
        raise ValueError(f"Invalid zone_id format: {zone.zone_id}")

    return True
```

### 3. Configuration 驗證規則

**來源**: spec.md FR-001, FR-005, FR-008, 憲法第 V 條

```python
def validate_ticketmaster_config(config: TicketmasterConfig) -> bool:
    """驗證 TicketmasterConfig 實體的合法性"""

    # 規則 1: auto_select_mode 必須為合法值
    valid_modes = ["from top to bottom", "from bottom to top", "random"]
    if config.auto_select_mode not in valid_modes:
        raise ValueError(f"Invalid auto_select_mode: {config.auto_select_mode}")

    # 規則 2: 若啟用日期自動選擇，則 date_keyword 不得為空
    if config.date_auto_select_enable and not config.date_keyword:
        raise ValueError("date_keyword is required when date_auto_select_enable is True")

    # 規則 3: 若啟用區域自動選擇，則 area_keyword 不得為空
    if config.area_auto_select_enable and not config.area_keyword:
        raise ValueError("area_keyword is required when area_auto_select_enable is True")

    # 規則 4: ticket_number 必須 >= 1
    if config.ticket_number < 1:
        raise ValueError("ticket_number must be at least 1")

    # 規則 5: area_keyword 必須為合法 JSON 陣列格式
    if config.area_keyword:
        try:
            area_keyword_list = json.loads(config.area_keyword)
            if not isinstance(area_keyword_list, list):
                raise ValueError("area_keyword must be a JSON array")
        except json.JSONDecodeError:
            raise ValueError("Invalid area_keyword JSON format")

    return True
```

### 4. FailureRecord 驗證規則

**來源**: spec.md FR-010

```python
def validate_failure_record(record: FailureRecord) -> bool:
    """驗證 FailureRecord 實體的合法性"""

    # 規則 1: failure_type 必須為合法值
    valid_types = ["promo_code", "captcha_answer", "area_selection", "date_selection"]
    if record.failure_type not in valid_types:
        raise ValueError(f"Invalid failure_type: {record.failure_type}")

    # 規則 2: failed_value 不得為空字串
    if not record.failed_value or record.failed_value.strip() == "":
        raise ValueError("failed_value cannot be empty")

    # 規則 3: timestamp 必須為合法 ISO 8601 格式
    try:
        datetime.fromisoformat(record.timestamp)
    except ValueError:
        raise ValueError(f"Invalid timestamp format: {record.timestamp}")

    # 規則 4: retry_count 必須 >= 0
    if record.retry_count < 0:
        raise ValueError("retry_count cannot be negative")

    return True
```

---

## 狀態轉換

### 1. EventDate 狀態轉換圖

```
┌──────────────┐
│ coming_soon  │ ──[開賣時間到達]──> ┌──────────┐
└──────────────┘                     │available │
                                     └─────┬────┘
                                           │
                                           │ [售罄]
                                           ▼
                                     ┌──────────┐
                                     │sold_out  │
                                     └──────────┘
```

**狀態說明**：

- **coming_soon**: 演出尚未開賣，無法購買
- **available**: 演出可購買，有 `see_tickets_link`
- **sold_out**: 演出已售罄，無法購買

**狀態轉換規則**：

1. `coming_soon` → `available`: 當開賣時間到達時自動轉換（由 Ticketmaster 伺服器控制）
2. `available` → `sold_out`: 當所有座位售罄時轉換（由 Ticketmaster 伺服器控制）
3. **不可逆**: `sold_out` 不會轉換回 `available`（除非 Ticketmaster 釋放退票）

**對應功能需求**：
- FR-003: 系統應跳過 `sold_out` 狀態的場次（若 `pass_date_is_sold_out` 為 `True`）

---

### 2. Zone 狀態轉換圖

```
┌──────────┐
│AVAILABLE │ ──[所有座位售罄]──> ┌─────────────┐
└──────────┘                     │UNAVAILABLE  │
                                 └─────────────┘
```

**狀態說明**：

- **AVAILABLE**: 區域可選擇，有座位可供購買
- **UNAVAILABLE**: 區域不可選擇，已售罄或不開放

**狀態轉換規則**：

1. `AVAILABLE` → `UNAVAILABLE`: 當所有座位售罄時轉換（由 Ticketmaster 伺服器控制）
2. **不可逆**: `UNAVAILABLE` 不會轉換回 `AVAILABLE`（除非 Ticketmaster 釋放退票）

**對應功能需求**：
- FR-005: 系統應過濾 `areaStatus == "UNAVAILABLE"` 的區域

---

### 3. FailureRecord 生命週期

```
[操作失敗事件]
      │
      ▼
┌─────────────┐
│  建立記錄   │ ── record_id, failed_value, timestamp
└──────┬──────┘
       │
       │ [記憶體中儲存]
       ▼
┌─────────────┐
│  檢查重試   │ ── retry_count++
└──────┬──────┘
       │
       │ [達到最大重試次數或程序結束]
       ▼
┌─────────────┐
│  銷毀記錄   │
└─────────────┘
```

**生命週期規則**：

1. **建立時機**: 當操作失敗時（例：促銷碼無效、驗證碼錯誤）
2. **檢查時機**: 在嘗試相同操作前檢查 `failed_value` 是否已存在於 FailureRecord
3. **銷毀時機**: 程序結束時清除（不持久化到檔案）

**對應功能需求**：
- FR-010: 記錄失敗的促銷碼避免重複嘗試

---

## 附錄：實體映射表

### EventDate 對應到 spec.md

| 欄位 | 對應 FR | 說明 |
|------|---------|------|
| `availability_status` | FR-002, FR-003 | 決定是否可選擇場次 |
| `see_tickets_link` | FR-002 | 過濾包含 "See Tickets" 的場次 |
| `matched_keywords` | FR-001 | 記錄匹配到的日期關鍵字 |
| `dom_element_index` | FR-002 | 用於定位 CSS 選擇器元素 |

### Zone 對應到 spec.md

| 欄位 | 對應 FR | 說明 |
|------|---------|------|
| `area_status` | FR-005 | 排除 "UNAVAILABLE" 的區域 |
| `group_name` | FR-005 | 用於區域關鍵字匹配 |
| `description` | FR-005 | 用於區域關鍵字匹配與排除 |
| `ticket_price` | FR-005 | 組合區域文字進行匹配 |
| `match_priority` | FR-006 | 支援多組關鍵字回退機制 |

### Configuration 對應到 spec.md

| 欄位 | 對應 FR | 說明 |
|------|---------|------|
| `date_auto_select_enable` | FR-001 | 控制日期自動選擇功能 |
| `area_auto_select_enable` | FR-005 | 控制區域自動選擇功能 |
| `pass_date_is_sold_out` | FR-003 | 控制跳過售罄場次 |
| `area_keyword` | FR-005, FR-006 | 支援多組關鍵字與回退 |
| `verbose` | FR-015 | 控制詳細日誌輸出 |

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**維護者**: Tickets Hunter 開發團隊
**相關文件**:
- 功能規格：`spec.md`
- 函數介面：`contracts/function-interface.md`
- JSON Schema：`contracts/zone-info-schema.md`
