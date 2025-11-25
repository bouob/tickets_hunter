# zone_info JSON Schema：Ticketmaster.com NoDriver 遷移

**專案**: Tickets Hunter - 多平台搶票自動化系統
**功能**: Ticketmaster.com NoDriver 平台遷移
**版本**: 1.0.0
**建立日期**: 2025-11-15
**相關規格**: `spec.md`, `research.md`

---

## 目錄

1. [JSON Schema 定義](#json-schema-定義)
2. [欄位說明](#欄位說明)
3. [驗證規則](#驗證規則)
4. [範例資料](#範例資料)
5. [提取方法](#提取方法)
6. [錯誤處理](#錯誤處理)

---

## JSON Schema 定義

本 schema 定義了 Ticketmaster.com 座位選擇頁面中 `zone_info` JavaScript 變數的結構。

### 標準 JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/bouob/tickets_hunter/specs/007-ticketmaster-nodriver-migration/contracts/zone-info-schema.json",
  "title": "Ticketmaster zone_info Schema",
  "description": "Ticketmaster.com 座位區域資訊的 JSON schema",
  "type": "object",
  "patternProperties": {
    "^zone_[0-9]+$": {
      "type": "object",
      "required": ["areaStatus", "groupName", "description", "price"],
      "properties": {
        "areaStatus": {
          "type": "string",
          "enum": ["AVAILABLE", "UNAVAILABLE"],
          "description": "區域可用狀態"
        },
        "groupName": {
          "type": "string",
          "minLength": 1,
          "description": "區域名稱（例：VIP區、一般區）"
        },
        "description": {
          "type": "string",
          "description": "區域描述（例：最佳視野、受限視野）"
        },
        "price": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["ticketPrice"],
            "properties": {
              "ticketPrice": {
                "type": "string",
                "pattern": "^[0-9]+(\\.[0-9]{1,2})?$",
                "description": "票價（字串格式，例：3500 或 3500.00）"
              }
            }
          },
          "description": "票價陣列（通常只有一個元素）"
        }
      },
      "additionalProperties": true
    }
  },
  "minProperties": 1,
  "additionalProperties": false
}
```

---

## 欄位說明

### 根物件

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `zone_[N]` | `object` | 是 | 座位區域物件，鍵值必須符合 `zone_[數字]` 格式 |

**驗證規則**：
- 根物件必須至少包含一個 `zone_[N]` 物件
- 鍵值必須符合正則表達式 `^zone_[0-9]+$`
- 不允許額外的鍵值（除了 `zone_[N]` 格式之外）

---

### Zone 物件

每個 `zone_[N]` 物件代表一個座位區域，必須包含以下欄位：

#### 1. areaStatus（區域狀態）

| 屬性 | 值 |
|------|---|
| **類型** | `string` |
| **必填** | 是 |
| **合法值** | `"AVAILABLE"` 或 `"UNAVAILABLE"` |
| **說明** | 區域可用狀態，決定是否可選擇此區域 |

**業務邏輯**：
- `"AVAILABLE"`: 區域可選擇，有座位可供購買
- `"UNAVAILABLE"`: 區域不可選擇，已售罄或不開放

**對應功能需求**: FR-005（系統必須根據 areaStatus 狀態排除 "UNAVAILABLE" 區域）

---

#### 2. groupName（區域名稱）

| 屬性 | 值 |
|------|---|
| **類型** | `string` |
| **必填** | 是 |
| **最小長度** | 1 字符 |
| **說明** | 區域名稱，用於關鍵字匹配 |

**範例值**：
- `"VIP區"`
- `"搖滾區"`
- `"一般區"`
- `"身障區"`

**對應功能需求**: FR-005（區域名稱用於關鍵字匹配）

---

#### 3. description（區域描述）

| 屬性 | 值 |
|------|---|
| **類型** | `string` |
| **必填** | 是 |
| **說明** | 區域描述，用於關鍵字匹配與排除 |

**範例值**：
- `"最佳視野"`
- `"標準座位"`
- `"受限視野"`
- `"站立區"`

**對應功能需求**:
- FR-005（區域描述用於關鍵字匹配）
- spec.md User Story 2（排除關鍵字功能）

---

#### 4. price（票價陣列）

| 屬性 | 值 |
|------|---|
| **類型** | `array` |
| **必填** | 是 |
| **最小長度** | 1 個元素 |
| **說明** | 票價陣列，通常只包含一個票價物件 |

**元素格式**：

```json
{
  "ticketPrice": "3500"
}
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 格式 | 說明 |
|---------|------|------|------|------|
| `ticketPrice` | `string` | 是 | `^[0-9]+(\.[0-9]{1,2})?$` | 票價（字串格式），可包含小數點 |

**範例值**：
- `"3500"` - 整數票價
- `"3500.00"` - 包含小數的票價
- `"1500.50"` - 包含小數的票價

**對應功能需求**: FR-005（票價用於區域文字匹配）

---

### 額外欄位（Optional）

**允許額外欄位**: 是

JSON Schema 中 `additionalProperties: true` 表示允許額外欄位，這是為了支援 Ticketmaster 可能新增的欄位（例如：剩餘座位數、座位類型等）。

**範例額外欄位**：
```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [{"ticketPrice": "3500"}],
    "seatCount": 50,          // 額外欄位：剩餘座位數
    "seatType": "reserved"    // 額外欄位：座位類型
  }
}
```

**處理策略**：
- 必要欄位（required fields）必須存在且合法
- 額外欄位可選擇性使用，不影響核心功能
- 若未來需要使用額外欄位，應更新此 schema

---

## 驗證規則

### 1. 根物件驗證

```python
def validate_zone_info_root(zone_info: dict) -> bool:
    """驗證 zone_info 根物件"""

    # 規則 1: 必須為字典類型
    if not isinstance(zone_info, dict):
        raise TypeError("zone_info must be a dictionary")

    # 規則 2: 必須至少包含一個 zone
    if len(zone_info) == 0:
        raise ValueError("zone_info must contain at least one zone")

    # 規則 3: 所有鍵值必須符合 "zone_[數字]" 格式
    import re
    zone_pattern = re.compile(r"^zone_[0-9]+$")
    for key in zone_info.keys():
        if not zone_pattern.match(key):
            raise ValueError(f"Invalid zone key format: {key}")

    return True
```

---

### 2. Zone 物件驗證

```python
def validate_zone_object(zone_id: str, zone_data: dict) -> bool:
    """驗證單一 zone 物件"""

    # 規則 1: 必須包含所有必要欄位
    required_fields = ["areaStatus", "groupName", "description", "price"]
    for field in required_fields:
        if field not in zone_data:
            raise ValueError(f"Zone {zone_id} missing required field: {field}")

    # 規則 2: areaStatus 必須為合法值
    valid_statuses = ["AVAILABLE", "UNAVAILABLE"]
    if zone_data["areaStatus"] not in valid_statuses:
        raise ValueError(
            f"Zone {zone_id} has invalid areaStatus: {zone_data['areaStatus']}"
        )

    # 規則 3: groupName 不得為空字串
    if not zone_data["groupName"] or zone_data["groupName"].strip() == "":
        raise ValueError(f"Zone {zone_id} has empty groupName")

    # 規則 4: description 必須為字串
    if not isinstance(zone_data["description"], str):
        raise TypeError(f"Zone {zone_id} description must be a string")

    # 規則 5: price 必須為陣列且至少有一個元素
    if not isinstance(zone_data["price"], list) or len(zone_data["price"]) == 0:
        raise ValueError(f"Zone {zone_id} price must be a non-empty array")

    # 規則 6: price[0] 必須包含 ticketPrice
    if "ticketPrice" not in zone_data["price"][0]:
        raise ValueError(f"Zone {zone_id} price[0] missing ticketPrice")

    # 規則 7: ticketPrice 必須為合法的數字字串
    ticket_price = zone_data["price"][0]["ticketPrice"]
    import re
    price_pattern = re.compile(r"^[0-9]+(\.[0-9]{1,2})?$")
    if not price_pattern.match(ticket_price):
        raise ValueError(
            f"Zone {zone_id} has invalid ticketPrice format: {ticket_price}"
        )

    return True
```

---

### 3. 完整驗證函數

```python
import re
from typing import Dict, Any

def validate_zone_info(zone_info: dict) -> bool:
    """
    完整驗證 zone_info JSON 資料。

    Args:
        zone_info: zone_info 字典

    Returns:
        bool: 驗證通過返回 True

    Raises:
        TypeError: 資料類型錯誤
        ValueError: 資料格式或內容錯誤
    """

    # 步驟 1: 驗證根物件
    validate_zone_info_root(zone_info)

    # 步驟 2: 驗證每個 zone 物件
    for zone_id, zone_data in zone_info.items():
        validate_zone_object(zone_id, zone_data)

    return True
```

**使用範例**：

```python
try:
    validate_zone_info(zone_info)
    print("[SUCCESS] zone_info validation passed")
except (TypeError, ValueError) as e:
    print(f"[ERROR] zone_info validation failed: {e}")
```

---

## 範例資料

### 範例 1: 完整的 zone_info（多個區域）

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野，靠近舞台",
    "price": [
      {
        "ticketPrice": "3500"
      }
    ]
  },
  "zone_2": {
    "areaStatus": "AVAILABLE",
    "groupName": "搖滾區",
    "description": "站立區，熱鬧氛圍",
    "price": [
      {
        "ticketPrice": "2500"
      }
    ]
  },
  "zone_3": {
    "areaStatus": "UNAVAILABLE",
    "groupName": "一般區",
    "description": "標準座位",
    "price": [
      {
        "ticketPrice": "1500"
      }
    ]
  },
  "zone_4": {
    "areaStatus": "AVAILABLE",
    "groupName": "身障區",
    "description": "無障礙座位",
    "price": [
      {
        "ticketPrice": "1500"
      }
    ]
  }
}
```

**驗證結果**: 通過

**匹配情境**（對應 spec.md User Story 2）：
- 關鍵字 `"VIP"` → 匹配 `zone_1`
- 關鍵字 `"搖滾"` → 匹配 `zone_2`
- 關鍵字 `"一般"` → 跳過（areaStatus 為 UNAVAILABLE）
- 排除關鍵字 `"受限"` → 不影響任何區域

---

### 範例 2: 最小有效 zone_info（單一區域）

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "一般區",
    "description": "",
    "price": [
      {
        "ticketPrice": "1000"
      }
    ]
  }
}
```

**驗證結果**: 通過

**說明**:
- `description` 可為空字串（允許但不建議）
- 僅包含一個 zone 物件

---

### 範例 3: 包含小數票價

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "早鳥區",
    "description": "早鳥優惠價",
    "price": [
      {
        "ticketPrice": "2499.50"
      }
    ]
  }
}
```

**驗證結果**: 通過

**說明**: `ticketPrice` 支援小數點（最多兩位）

---

### 範例 4: 包含額外欄位

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [
      {
        "ticketPrice": "3500",
        "currency": "TWD",
        "taxIncluded": true
      }
    ],
    "seatCount": 50,
    "seatType": "reserved",
    "sectionNumber": "A1"
  }
}
```

**驗證結果**: 通過

**說明**:
- `price[0]` 包含額外欄位 `currency` 和 `taxIncluded`
- zone 物件包含額外欄位 `seatCount`, `seatType`, `sectionNumber`
- 額外欄位不影響驗證（`additionalProperties: true`）

---

### 範例 5: 無效的 zone_info（錯誤範例）

#### 錯誤 1: 缺少必要欄位

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區"
    // 缺少 "description" 和 "price"
  }
}
```

**驗證結果**: 失敗
**錯誤訊息**: `Zone zone_1 missing required field: description`

---

#### 錯誤 2: areaStatus 值不合法

```json
{
  "zone_1": {
    "areaStatus": "SOLD_OUT",  // 應為 "AVAILABLE" 或 "UNAVAILABLE"
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [{"ticketPrice": "3500"}]
  }
}
```

**驗證結果**: 失敗
**錯誤訊息**: `Zone zone_1 has invalid areaStatus: SOLD_OUT`

---

#### 錯誤 3: ticketPrice 格式錯誤

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [
      {
        "ticketPrice": "3,500"  // 包含逗號，不符合格式
      }
    ]
  }
}
```

**驗證結果**: 失敗
**錯誤訊息**: `Zone zone_1 has invalid ticketPrice format: 3,500`

---

#### 錯誤 4: zone 鍵值格式錯誤

```json
{
  "vip_zone": {  // 應為 "zone_1", "zone_2" 等
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [{"ticketPrice": "3500"}]
  }
}
```

**驗證結果**: 失敗
**錯誤訊息**: `Invalid zone key format: vip_zone`

---

## 提取方法

### 來源位置

**HTML 位置**: `#mapSelectArea` 元素的 `innerHTML`

**JavaScript 變數**: `var zone = {...};`

---

### 方法 1: JavaScript Evaluate（推薦）

**優點**:
- 直接取得 JavaScript 物件，自動轉換為 Python 字典
- 避免字串處理的複雜性與錯誤風險

**程式碼**:

```python
async def extract_zone_info_via_evaluate(tab: nodriver.Tab) -> Optional[dict]:
    """使用 tab.evaluate() 直接取得 zone 變數"""

    zone_info = await tab.evaluate('''
        (function() {
            // 嘗試存取全域變數 zone
            if (typeof zone !== 'undefined') {
                return zone;
            }

            // 若 zone 是局部變數，回退到 DOM 提取
            const el = document.querySelector('#mapSelectArea');
            if (!el) return null;

            const html = el.innerHTML;
            const match = html.match(/var zone = ({[\\s\\S]*?});/);
            if (!match) return null;

            try {
                return JSON.parse(match[1]);
            } catch (e) {
                console.error("JSON parse failed:", e);
                return null;
            }
        })();
    ''')

    return zone_info
```

**對應函數**: `ticketmaster_parse_zone_info()` (research.md 函數 4)

---

### 方法 2: 字串提取與解析（回退方案）

**優點**:
- 若 `zone` 為局部變數無法直接存取，字串提取仍可工作
- 容錯性較高

**程式碼**:

```python
import json
import re

async def extract_zone_info_via_string_parsing(
    tab: nodriver.Tab
) -> Optional[dict]:
    """使用字串分割提取 zone_info"""

    # 步驟 1: 定位 #mapSelectArea 元素
    mapSelectArea = await tab.query_selector('#mapSelectArea')
    if not mapSelectArea:
        raise RuntimeError("Cannot find #mapSelectArea element")

    # 步驟 2: 取得 innerHTML
    mapSelectArea_html = await mapSelectArea.get_attribute('innerHTML')
    if not mapSelectArea_html:
        return None

    # 步驟 3: 檢查是否包含 "var zone ="
    if "var zone =" not in mapSelectArea_html:
        return None

    # 步驟 4: 字串分割提取 JSON
    try:
        zone_string = mapSelectArea_html.split("var zone =")[1]
        zone_string = zone_string.split("fieldImageType")[0]

        # 步驟 5: 清理字串（移除尾部逗號與換行符）
        zone_string = zone_string.strip()
        if zone_string.endswith("\n"):
            zone_string = zone_string[:-1]
        zone_string = zone_string.strip()
        if zone_string.endswith(","):
            zone_string = zone_string[:-1]

        # 步驟 6: 解析 JSON
        zone_info = json.loads(zone_string)
        return zone_info

    except (IndexError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to parse zone_info: {e}")
        print(f"[DEBUG] Raw HTML snippet: {mapSelectArea_html[:200]}...")
        return None
```

**對應函數**: `ticketmaster_parse_zone_info()` (research.md 函數 4)

---

### 提取流程圖

```
┌───────────────────────────┐
│ 1. 嘗試 JavaScript 存取   │
│    tab.evaluate('zone')   │
└───────────┬───────────────┘
            │
            ├─ 成功 → 返回 zone_info
            │
            └─ 失敗 ↓
┌───────────────────────────┐
│ 2. 字串提取               │
│    #mapSelectArea innerHTML│
└───────────┬───────────────┘
            │
            ├─ 找到 "var zone =" → 提取 JSON
            │
            └─ 未找到 → 返回 None
┌───────────────────────────┐
│ 3. JSON 解析              │
│    json.loads()           │
└───────────┬───────────────┘
            │
            ├─ 成功 → 返回 zone_info
            │
            └─ 失敗 → 返回 None
```

---

## 錯誤處理

### 常見錯誤情境

#### 錯誤 1: 無法找到 #mapSelectArea 元素

**原因**:
- 頁面不是座位選擇頁面
- 頁面尚未完全載入

**處理策略**:
```python
mapSelectArea = await tab.query_selector('#mapSelectArea')
if not mapSelectArea:
    if config["advanced"]["verbose"]:
        print("[ERROR] Cannot find #mapSelectArea element")
        print(f"[DEBUG] Current URL: {tab.url}")
    raise RuntimeError("Cannot find #mapSelectArea element")
```

---

#### 錯誤 2: JSON 解析失敗（包含尾部逗號）

**原因**:
- JavaScript 允許 trailing comma，但 Python `json.loads()` 不允許

**範例錯誤資料**:
```javascript
var zone = {
  "zone_1": {...},
  "zone_2": {...},
};  // 尾部逗號
```

**處理策略**:
```python
# 移除尾部逗號
zone_string = zone_string.strip()
if zone_string.endswith(","):
    zone_string = zone_string[:-1]
```

---

#### 錯誤 3: JSON 解析失敗（包含換行符）

**原因**:
- HTML 中的 JavaScript 可能包含換行符

**範例錯誤資料**:
```javascript
var zone = {
  "zone_1": {...},
  "zone_2": {...}
}
;
```

**處理策略**:
```python
# 移除尾部換行符
zone_string = zone_string.strip()
if zone_string.endswith("\n"):
    zone_string = zone_string[:-1]
```

---

#### 錯誤 4: zone_info 為空物件

**原因**:
- 該場次沒有座位區域可選擇
- 頁面資料載入失敗

**處理策略**:
```python
zone_info = await extract_zone_info_via_evaluate(tab)
if not zone_info or len(zone_info) == 0:
    if config["advanced"]["verbose"]:
        print("[WARNING] zone_info is empty")
    return None
```

---

### 錯誤日誌範例

**情境**: JSON 解析失敗

```python
try:
    zone_info = json.loads(zone_string)
except json.JSONDecodeError as e:
    if config["advanced"]["verbose"]:
        print(f"[ERROR] JSON parse failed: {e}")
        print(f"[DEBUG] Raw zone_string (first 200 chars): {zone_string[:200]}...")
        print(f"[DEBUG] Raw zone_string (last 50 chars): ...{zone_string[-50:]}")
    return None
```

**輸出範例**:
```
[ERROR] JSON parse failed: Expecting property name enclosed in double quotes: line 1 column 234 (char 233)
[DEBUG] Raw zone_string (first 200 chars): {"zone_1":{"areaStatus":"AVAILABLE","groupName":"VIP區","description":"最佳視野","price":[{"ticketPrice":"3500"}]},"zone_2":{"areaStatus":"UNAVAILABLE","groupNam...
[DEBUG] Raw zone_string (last 50 chars): ...e":[{"ticketPrice":"1500"}]},
```

---

## 附錄：與 spec.md 的對應關係

| Schema 欄位 | 對應 FR | 說明 |
|------------|---------|------|
| `areaStatus` | FR-005 | 系統必須根據 areaStatus 狀態排除 "UNAVAILABLE" 區域 |
| `groupName` | FR-005 | 區域名稱用於關鍵字匹配 |
| `description` | FR-005 | 區域描述用於關鍵字匹配 |
| `price[0].ticketPrice` | FR-005 | 票價用於組合區域文字進行匹配 |
| zone_info 根物件 | FR-004 | 系統必須能解析 zone_info JavaScript 變數 |

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**維護者**: Tickets Hunter 開發團隊
**相關文件**:
- 功能規格：`spec.md`
- 技術研究：`research.md`
- 資料模型：`data-model.md`
- 函數介面：`function-interface.md`
