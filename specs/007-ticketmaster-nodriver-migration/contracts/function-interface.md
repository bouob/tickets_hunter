# 函數介面契約：Ticketmaster.com NoDriver 遷移

**專案**: Tickets Hunter - 多平台搶票自動化系統
**功能**: Ticketmaster.com NoDriver 平台遷移
**版本**: 1.0.0
**建立日期**: 2025-11-15
**相關規格**: `spec.md`, `research.md`

---

## 目錄

1. [契約設計原則](#契約設計原則)
2. [核心函數介面](#核心函數介面)
3. [輔助函數介面](#輔助函數介面)
4. [錯誤處理規範](#錯誤處理規範)
5. [測試規範](#測試規範)

---

## 契約設計原則

本契約設計遵循專案憲章第 IV 條「單一職責與可組合性」原則：

1. **單一職責** - 每個函數只做一件事
2. **依賴注入** - 優先傳遞參數而非讀取全域變數
3. **明確契約** - 清晰的前置條件、後置條件與例外
4. **可測試性** - 純函數優先，副作用明確記錄

---

## 核心函數介面

### 1. ticketmaster_date_auto_select()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:1274-1395`
**對應需求**: FR-001, FR-002, FR-003

#### 函數簽章

```python
async def ticketmaster_date_auto_select(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict
) -> bool:
    """
    在 Ticketmaster.com 的活動頁面自動選擇符合關鍵字的演出日期。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（活動頁面）
        config: 設定字典，必須包含:
            - config["date_auto_select"]["enable"]: bool
            - config["date_auto_select"]["date_keyword"]: str
            - config["area_auto_select"]["mode"]: str
            - config["tixcraft"]["pass_date_is_sold_out"]: bool
            - config["advanced"]["verbose"]: bool
            - config["kktix"]["auto_reload_coming_soon_page"]: bool

    Returns:
        bool: 成功選擇並點擊日期連結則返回 True，否則返回 False

    Raises:
        ValueError: config 參數缺少必要欄位
        RuntimeError: 頁面結構異常或元素定位失敗
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例，用於分頁管理 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例，必須已導航至活動頁面 |
| `config` | `dict` | 是 | 設定字典（來自 settings.json） |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `bool` | 成功選擇並點擊日期連結則返回 `True`，否則返回 `False` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至 Ticketmaster.com 的活動頁面（URL 包含 `/artist/`）
2. 頁面已完全載入（DOM 元素可查詢）
3. `config["date_auto_select"]["enable"]` 為 `True`
4. `config["date_auto_select"]["date_keyword"]` 不為空字串

#### 後置條件 (Postconditions)

1. 若成功匹配日期：
   - 點擊對應的 "See Tickets" 連結
   - 頁面導航至座位選擇頁面（URL 包含 `/ticket/area/`）
   - 若出現新分頁，已切換回主分頁並關閉新分頁
2. 若匹配失敗且 `auto_reload_coming_soon_page` 為 `True`：
   - 頁面已重新整理
3. 若 `verbose` 為 `True`：
   - 輸出日期匹配摘要日誌（包含匹配數量、選擇目標）

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#list-view > div > div.event-listing > div.accordion-wrapper > div`
2. **頁面導航**: 點擊日期連結後導航至新頁面
3. **分頁管理**: 若出現新分頁，關閉新分頁並切換回主分頁
4. **日誌輸出**: 根據 `verbose` 設定輸出日誌

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `ValueError` | `config` 缺少必要欄位 | 檢查 settings.json 配置 |
| `RuntimeError` | 頁面結構異常（無法找到日期列表容器） | 檢查頁面 URL 是否正確 |

#### 演算法流程

```python
1. 檢查 config["date_auto_select"]["enable"]，若為 False 則直接返回 False
2. 使用 tab.query_selector_all() 查詢所有日期區塊
3. 遍歷每個日期區塊：
   a. 使用 element.get_html() 取得 innerHTML
   b. 檢查是否包含 "See Tickets"，若無則跳過
   c. 若 pass_date_is_sold_out 為 True，檢查是否包含售罄關鍵字，若有則跳過
   d. 使用 util.get_matched_blocks_by_keyword() 匹配日期關鍵字
   e. 將匹配的日期區塊加入候選列表
4. 若候選列表為空：
   a. 若 auto_reload_coming_soon_page 為 True，執行 tab.reload()
   b. 返回 False
5. 使用 util.get_target_item_from_matched_list() 根據 auto_select_mode 選擇目標日期
6. 使用 target_element.query_selector('a') 找到 "See Tickets" 連結
7. 使用 link.click() 點擊連結
8. 若 len(driver.tabs) > 1：
   a. 關閉所有非主分頁（driver.tabs[1:]）
   b. 切換回主分頁（driver.tabs[0].activate()）
9. 返回 True
```

#### 測試案例

**測試 1: 成功匹配單一日期**

```python
# Given
config = {
    "date_auto_select": {"enable": True, "date_keyword": "2025-12-25"},
    "area_auto_select": {"mode": "from top to bottom"},
    "tixcraft": {"pass_date_is_sold_out": False},
    "advanced": {"verbose": True}
}
# 頁面包含一個日期 "2025-12-25" 且狀態為 "See Tickets"

# When
result = await ticketmaster_date_auto_select(driver, tab, config)

# Then
assert result == True
assert "/ticket/area/" in tab.url  # 已導航至座位選擇頁面
```

**測試 2: 跳過售罄場次**

```python
# Given
config = {
    "date_auto_select": {"enable": True, "date_keyword": "2025-12-25"},
    "area_auto_select": {"mode": "from top to bottom"},
    "tixcraft": {"pass_date_is_sold_out": True},
    "advanced": {"verbose": True}
}
# 頁面包含一個日期 "2025-12-25" 但狀態為 "Sold out"

# When
result = await ticketmaster_date_auto_select(driver, tab, config)

# Then
assert result == False  # 跳過售罄場次，無匹配結果
```

---

### 2. get_ticketmaster_target_area()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:1516-1596`
**對應需求**: FR-005, FR-006

#### 函數簽章

```python
def get_ticketmaster_target_area(
    config: dict,
    zone_info: dict,
    area_keyword_list: list
) -> list:
    """
    從 zone_info 字典中根據關鍵字匹配可用的座位區域。

    注意: 此函數為純函數（無副作用），不需要 async。

    Args:
        config: 設定字典，必須包含:
            - config["advanced"]["verbose"]: bool
        zone_info: zone_info 字典（從頁面提取的 JSON 資料）
        area_keyword_list: 區域關鍵字列表（例: ["VIP", "搖滾區"]）

    Returns:
        list: 匹配的區域 ID 列表（例: ["zone_1", "zone_3"]）

    Raises:
        ValueError: zone_info 格式不合法或 area_keyword_list 為空
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `config` | `dict` | 是 | 設定字典（僅用於 verbose 日誌） |
| `zone_info` | `dict` | 是 | zone_info 字典，格式見 `zone-info-schema.md` |
| `area_keyword_list` | `list` | 是 | 區域關鍵字列表，每個元素為一個關鍵字字串 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `list` | 匹配的區域 ID 列表（例: `["zone_1", "zone_3"]`），若無匹配則返回空列表 `[]` |

#### 前置條件 (Preconditions)

1. `zone_info` 為合法的字典格式（符合 `zone-info-schema.md`）
2. `area_keyword_list` 不為空列表
3. `zone_info` 中至少有一個區域物件

#### 後置條件 (Postconditions)

1. 返回的區域列表中所有區域的 `areaStatus` 都為 `"AVAILABLE"`
2. 返回的區域列表按 zone_info 原始順序排列

#### 副作用 (Side Effects)

1. **無副作用** - 純函數，僅進行資料處理與匹配

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `ValueError` | `zone_info` 格式不合法（缺少必要欄位） | 檢查 `zone_info` 提取邏輯 |
| `ValueError` | `area_keyword_list` 為空列表 | 檢查設定檔 `area_keyword` 配置 |

#### 演算法流程

```python
1. 初始化空的匹配列表 matched_zones = []
2. 遍歷 zone_info 的每個鍵值對 (zone_id, zone_data):
   a. 檢查 zone_data["areaStatus"]，若為 "UNAVAILABLE" 則跳過
   b. 組合區域文字: area_text = f"{zone_data['groupName']} {zone_data['description']} {zone_data['price'][0]['ticketPrice']}"
   c. 使用 util.format_keyword_string() 格式化關鍵字
   d. 使用 util.get_matched_blocks_by_keyword() 匹配關鍵字
   e. 若匹配成功，將 zone_id 加入 matched_zones
3. 返回 matched_zones
```

#### 測試案例

**測試 1: 成功匹配單一區域**

```python
# Given
zone_info = {
    "zone_1": {
        "areaStatus": "AVAILABLE",
        "groupName": "VIP區",
        "description": "最佳視野",
        "price": [{"ticketPrice": "3500"}]
    },
    "zone_2": {
        "areaStatus": "UNAVAILABLE",
        "groupName": "一般區",
        "description": "標準座位",
        "price": [{"ticketPrice": "1500"}]
    }
}
area_keyword_list = ["VIP"]

# When
result = get_ticketmaster_target_area(config, zone_info, area_keyword_list)

# Then
assert result == ["zone_1"]
```

**測試 2: 排除 UNAVAILABLE 區域**

```python
# Given
zone_info = {
    "zone_1": {
        "areaStatus": "UNAVAILABLE",
        "groupName": "VIP區",
        "description": "最佳視野",
        "price": [{"ticketPrice": "3500"}]
    }
}
area_keyword_list = ["VIP"]

# When
result = get_ticketmaster_target_area(config, zone_info, area_keyword_list)

# Then
assert result == []  # UNAVAILABLE 區域應被排除
```

---

### 3. ticketmaster_area_auto_select()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:1665-1720`
**對應需求**: FR-005, FR-006

#### 函數簽章

```python
async def ticketmaster_area_auto_select(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict,
    zone_info: dict
) -> bool:
    """
    在 Ticketmaster.com 的座位選擇頁面自動選擇符合關鍵字的座位區域。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（座位選擇頁面）
        config: 設定字典，必須包含:
            - config["area_auto_select"]["enable"]: bool
            - config["area_auto_select"]["area_keyword"]: str (JSON array)
            - config["area_auto_select"]["mode"]: str
            - config["advanced"]["verbose"]: bool
        zone_info: zone_info 字典（從頁面提取的 JSON 資料）

    Returns:
        bool: 成功選擇區域則返回 True，否則返回 False

    Raises:
        ValueError: config 參數缺少必要欄位或 zone_info 格式不合法
        RuntimeError: JavaScript 執行失敗
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例，必須在座位選擇頁面 |
| `config` | `dict` | 是 | 設定字典 |
| `zone_info` | `dict` | 是 | zone_info 字典 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `bool` | 成功執行 `areaTicket()` JavaScript 函數則返回 `True`，否則返回 `False` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至座位選擇頁面（URL 包含 `/ticket/area/`）
2. 頁面已完全載入（JavaScript 變數 `areaTicket()` 可用）
3. `config["area_auto_select"]["enable"]` 為 `True`
4. `zone_info` 為合法的字典格式

#### 後置條件 (Postconditions)

1. 若成功匹配區域：
   - 執行 JavaScript `areaTicket("<zone_id>", "map");`
   - 頁面可能導航至票務頁面或等待使用者確認
2. 若匹配失敗：
   - 返回 `False`，不執行任何操作

#### 副作用 (Side Effects)

1. **JavaScript 執行**: 執行 `areaTicket("<zone_id>", "map");` 觸發座位選擇
2. **頁面可能導航**: 執行 JavaScript 後頁面可能自動導航
3. **日誌輸出**: 根據 `verbose` 設定輸出日誌

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `ValueError` | `config` 缺少必要欄位 | 檢查 settings.json 配置 |
| `RuntimeError` | JavaScript 執行失敗（`areaTicket` 函數不存在） | 檢查頁面是否為座位選擇頁面 |

#### 演算法流程

```python
1. 檢查 config["area_auto_select"]["enable"]，若為 False 則返回 False
2. 解析 config["area_auto_select"]["area_keyword"] 為 JSON 陣列
3. 遍歷每組關鍵字（實作回退機制）：
   a. 調用 get_ticketmaster_target_area(config, zone_info, area_keyword_list)
   b. 若返回非空列表：
      i. 使用 util.get_target_item_from_matched_list() 根據 mode 選擇目標區域
      ii. 執行 JavaScript: tab.evaluate(f'areaTicket("{target_zone_id}", "map");')
      iii. 返回 True
   c. 若返回空列表，繼續下一組關鍵字
4. 若所有關鍵字組都無匹配，返回 False
```

#### 測試案例

**測試 1: 成功匹配並選擇區域**

```python
# Given
config = {
    "area_auto_select": {
        "enable": True,
        "area_keyword": '["VIP"]',
        "mode": "from top to bottom"
    },
    "advanced": {"verbose": True}
}
zone_info = {
    "zone_1": {
        "areaStatus": "AVAILABLE",
        "groupName": "VIP區",
        "description": "最佳視野",
        "price": [{"ticketPrice": "3500"}]
    }
}

# When
result = await ticketmaster_area_auto_select(driver, tab, config, zone_info)

# Then
assert result == True
# 驗證 JavaScript 'areaTicket("zone_1", "map");' 已被執行
```

**測試 2: 回退到第二組關鍵字**

```python
# Given
config = {
    "area_auto_select": {
        "enable": True,
        "area_keyword": '["超級VIP", "VIP"]',  # 第一組無匹配，回退到第二組
        "mode": "from top to bottom"
    },
    "advanced": {"verbose": True}
}
zone_info = {
    "zone_1": {
        "areaStatus": "AVAILABLE",
        "groupName": "VIP區",
        "description": "最佳視野",
        "price": [{"ticketPrice": "3500"}]
    }
}

# When
result = await ticketmaster_area_auto_select(driver, tab, config, zone_info)

# Then
assert result == True  # 第二組關鍵字成功匹配
```

---

### 4. ticketmaster_parse_zone_info()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:5808-5862`
**對應需求**: FR-004

#### 函數簽章

```python
async def ticketmaster_parse_zone_info(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict
) -> Optional[dict]:
    """
    從 Ticketmaster.com 座位選擇頁面的 #mapSelectArea 元素中提取並解析 zone_info JSON 資料。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（座位選擇頁面）
        config: 設定字典，必須包含:
            - config["advanced"]["verbose"]: bool

    Returns:
        Optional[dict]: 成功解析則返回 zone_info 字典，失敗則返回 None

    Raises:
        RuntimeError: 無法找到 #mapSelectArea 元素
        json.JSONDecodeError: JSON 解析失敗
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例 |
| `config` | `dict` | 是 | 設定字典 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `Optional[dict]` | 成功解析則返回 zone_info 字典，失敗則返回 `None` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至座位選擇頁面（URL 包含 `/ticket/area/`）
2. 頁面中存在 `#mapSelectArea` 元素

#### 後置條件 (Postconditions)

1. 若成功解析：
   - 返回的 zone_info 字典符合 `zone-info-schema.md` 格式
2. 若解析失敗：
   - 返回 `None`
   - 若 `verbose` 為 `True`，輸出錯誤日誌

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#mapSelectArea` 元素
2. **JavaScript 執行**: 使用 `tab.evaluate()` 提取 `zone` 變數或 innerHTML
3. **日誌輸出**: 根據 `verbose` 設定輸出日誌

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `RuntimeError` | 無法找到 `#mapSelectArea` 元素 | 檢查頁面 URL 是否為座位選擇頁面 |
| `json.JSONDecodeError` | JSON 解析失敗（格式錯誤） | 檢查提取的字串是否包含有效 JSON |

#### 演算法流程

```python
1. 使用 tab.evaluate() 嘗試直接取得 JavaScript 變數 zone:
   ```javascript
   (function() {
       if (typeof zone !== 'undefined') {
           return zone;
       }
       return null;
   })();
   ```
2. 若步驟 1 成功且返回非空字典，返回該字典
3. 否則，回退到字串提取方法：
   a. 使用 tab.query_selector('#mapSelectArea') 定位元素
   b. 使用 element.get_attribute('innerHTML') 取得 innerHTML
   c. 字串分割提取 JSON:
      - 開始標記: "var zone ="
      - 結束標記: "fieldImageType"
   d. 清理字串（移除尾部逗號與換行符）
   e. 使用 json.loads() 解析 JSON
4. 若所有方法都失敗，返回 None
```

#### 測試案例

**測試 1: 成功從 JavaScript 變數提取**

```python
# Given
# 頁面 JavaScript 中存在全域變數 zone

# When
result = await ticketmaster_parse_zone_info(driver, tab, config)

# Then
assert result is not None
assert "zone_1" in result
assert result["zone_1"]["areaStatus"] in ["AVAILABLE", "UNAVAILABLE"]
```

**測試 2: 回退到字串提取方法**

```python
# Given
# 頁面 JavaScript 中 zone 為局部變數，但 #mapSelectArea innerHTML 包含 zone 資料

# When
result = await ticketmaster_parse_zone_info(driver, tab, config)

# Then
assert result is not None  # 字串提取方法成功
```

---

### 5. ticketmaster_get_ticketPriceList()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:5864-5908`
**對應需求**: FR-007

#### 函數簽章

```python
async def ticketmaster_get_ticketPriceList(
    tab: nodriver.Tab,
    config: dict
) -> Optional[nodriver.Element]:
    """
    等待頁面載入完成後取得 #ticketPriceList 表格元素。

    Args:
        tab: 當前 Tab 實例（票務頁面）
        config: 設定字典，必須包含:
            - config["advanced"]["verbose"]: bool

    Returns:
        Optional[nodriver.Element]: 成功找到 #ticketPriceList 則返回元素，否則返回 None

    Raises:
        RuntimeError: 等待超時（超過 10 秒）
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例 |
| `config` | `dict` | 是 | 設定字典 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `Optional[nodriver.Element]` | 成功找到 `#ticketPriceList` 則返回元素，否則返回 `None` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至票務頁面（URL 包含 `/ticket/area/`）
2. 頁面可能正在載入（存在 `#loadingmap` 元素）

#### 後置條件 (Postconditions)

1. 若成功找到 `#ticketPriceList`：
   - `#loadingmap` 元素已消失（頁面載入完成）
   - 返回的元素可用於票數設定
2. 若超時：
   - 拋出 `RuntimeError`

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#ticketPriceList` 與 `#loadingmap` 元素
2. **等待邏輯**: 使用 JavaScript Promise 實作條件等待（最多 10 秒）

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `RuntimeError` | 等待超時（超過 10 秒） | 檢查頁面載入狀態或網路連線 |

#### 演算法流程

```python
1. 使用 JavaScript Promise 實作條件等待:
   ```javascript
   return new Promise((resolve) => {
       let retryCount = 0;
       const maxRetries = 50;  // 10 秒 (50 * 200ms)

       function checkElement() {
           const element = document.querySelector('#ticketPriceList');
           const loadingElement = document.querySelector('#loadingmap');

           if (element && !loadingElement) {
               resolve({ success: true, found: true });
               return;
           }

           if (retryCount < maxRetries) {
               retryCount++;
               setTimeout(checkElement, 200);
           } else {
               resolve({ success: false, error: "Timeout" });
           }
       }

       checkElement();
   });
   ```
2. 若返回 { success: true, found: true }，使用 tab.query_selector('#ticketPriceList') 取得元素
3. 若返回 { success: false }，拋出 RuntimeError
```

#### 測試案例

**測試 1: 成功找到 ticketPriceList**

```python
# Given
# 頁面包含 #ticketPriceList 且 #loadingmap 已消失

# When
result = await ticketmaster_get_ticketPriceList(tab, config)

# Then
assert result is not None
assert result.tag_name == "table"  # 驗證為 table 元素
```

---

### 6. ticketmaster_assign_ticket_number()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:5910-5977`
**對應需求**: FR-008, FR-009

#### 函數簽章

```python
async def ticketmaster_assign_ticket_number(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict
) -> bool:
    """
    在票務頁面的 #ticketPriceList 表格中設定購票張數並點擊 #autoMode 按鈕。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（票務頁面）
        config: 設定字典，必須包含:
            - config["ticket_number"]: int
            - config["advanced"]["verbose"]: bool

    Returns:
        bool: 成功設定票數並點擊按鈕則返回 True，否則返回 False

    Raises:
        ValueError: config["ticket_number"] < 1
        RuntimeError: 無法找到 select 元素或 #autoMode 按鈕
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例 |
| `config` | `dict` | 是 | 設定字典 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `bool` | 成功設定票數並點擊按鈕則返回 `True`，否則返回 `False` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至票務頁面
2. 頁面包含 `#ticketPriceList` 表格與 `select` 元素
3. `config["ticket_number"]` >= 1

#### 後置條件 (Postconditions)

1. 若成功設定票數：
   - `select` 元素的值已設定為 `config["ticket_number"]`
   - `#autoMode` 按鈕已點擊
   - 頁面可能導航至下一步驟（驗證碼或付款頁面）

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#ticketPriceList` 與 `select` 元素
2. **JavaScript 執行**: 使用 JavaScript 設定 `select` 值並觸發 `change` 事件
3. **元素點擊**: 點擊 `#autoMode` 按鈕
4. **頁面可能導航**: 點擊按鈕後頁面可能自動導航

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `ValueError` | `config["ticket_number"]` < 1 | 檢查 settings.json 配置 |
| `RuntimeError` | 無法找到 `select` 元素 | 檢查頁面是否為票務頁面 |

#### 演算法流程

```python
1. 調用 ticketmaster_get_ticketPriceList(tab, config) 取得表格
2. 若表格為 None，返回 False
3. 使用 table.query_selector('select') 定位下拉選單
4. 若 select 為 None，返回 False
5. 使用 JavaScript 設定 select 值:
   ```javascript
   const targetText = config["ticket_number"];
   const options = el.options;
   for (let i = 0; i < options.length; i++) {
       if (options[i].text === targetText.toString()) {
           el.selectedIndex = i;
           el.dispatchEvent(new Event('change', { bubbles: true }));
           return true;
       }
   }
   return false;
   ```
6. 若設定成功，使用 tab.query_selector('#autoMode') 定位按鈕
7. 使用 button.click() 點擊按鈕
8. 返回 True
```

#### 測試案例

**測試 1: 成功設定票數為 2**

```python
# Given
config = {"ticket_number": 2, "advanced": {"verbose": True}}
# 頁面包含 select 元素且有選項 "1", "2", "3"

# When
result = await ticketmaster_assign_ticket_number(driver, tab, config)

# Then
assert result == True
# 驗證 select.selectedIndex 已設定為 "2"
```

---

### 7. ticketmaster_promo()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:1937-1939`
**對應需求**: FR-010

#### 函數簽章

```python
async def ticketmaster_promo(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict,
    promo_code_fail_list: list
) -> list:
    """
    在促銷碼頁面填寫促銷碼並提交。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（促銷碼頁面）
        config: 設定字典，必須包含:
            - config["advanced"]["verbose"]: bool
        promo_code_fail_list: 已失敗的促銷碼列表

    Returns:
        list: 更新後的失敗促銷碼列表

    Raises:
        RuntimeError: 無法找到 #promoBox 元素
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例 |
| `config` | `dict` | 是 | 設定字典 |
| `promo_code_fail_list` | `list` | 是 | 已失敗的促銷碼列表 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `list` | 更新後的失敗促銷碼列表 |

#### 前置條件 (Preconditions)

1. `tab` 已導航至促銷碼頁面
2. 頁面包含 `#promoBox` 輸入框

#### 後置條件 (Postconditions)

1. 若促銷碼有效：
   - 促銷碼已填寫並提交
   - 頁面導航至下一步驟
2. 若促銷碼無效：
   - 失敗的促銷碼加入 `promo_code_fail_list`

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#promoBox` 元素
2. **文字輸入**: 填寫促銷碼
3. **表單提交**: 提交促銷碼表單
4. **頁面可能導航**: 提交後頁面可能自動導航

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `RuntimeError` | 無法找到 `#promoBox` 元素 | 檢查頁面是否為促銷碼頁面 |

#### 演算法流程

```python
1. 調用 tixcraft_input_check_code(driver, tab, config, "#promoBox", promo_code_fail_list)
2. 返回更新後的 fail_list
```

---

### 8. ticketmaster_captcha()

**位置**: `nodriver_tixcraft.py` (待實作)
**來源**: `chrome_tixcraft.py:5979-6016`
**對應需求**: FR-011

#### 函數簽章

```python
async def ticketmaster_captcha(
    driver: nodriver.Browser,
    tab: nodriver.Tab,
    config: dict,
    ocr: Optional[object],
    captcha_browser: Optional[object]
) -> bool:
    """
    在驗證碼頁面勾選同意條款並處理驗證碼（手動或 OCR）。

    Args:
        driver: NoDriver Browser 實例
        tab: 當前 Tab 實例（驗證碼頁面）
        config: 設定字典，必須包含:
            - config["ocr_captcha"]["enable"]: bool
            - config["advanced"]["verbose"]: bool
        ocr: OCR 物件（若啟用 OCR）
        captcha_browser: Captcha Browser 物件（若啟用 OCR）

    Returns:
        bool: 成功處理驗證碼則返回 True，否則返回 False

    Raises:
        RuntimeError: 無法找到 #TicketForm_agree 元素
    """
```

#### 參數說明

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `driver` | `nodriver.Browser` | 是 | NoDriver Browser 實例 |
| `tab` | `nodriver.Tab` | 是 | 當前 Tab 實例 |
| `config` | `dict` | 是 | 設定字典 |
| `ocr` | `Optional[object]` | 否 | OCR 物件（若啟用 OCR） |
| `captcha_browser` | `Optional[object]` | 否 | Captcha Browser 物件 |

#### 回傳值

| 類型 | 說明 |
|------|------|
| `bool` | 成功處理驗證碼則返回 `True`，否則返回 `False` |

#### 前置條件 (Preconditions)

1. `tab` 已導航至驗證碼頁面（URL 包含 `/ticket/check-captcha/`）
2. 頁面包含 `#TicketForm_agree` 勾選框

#### 後置條件 (Postconditions)

1. `#TicketForm_agree` 勾選框已勾選
2. 若啟用 OCR：
   - OCR 已嘗試辨識驗證碼並填寫
3. 若未啟用 OCR：
   - 驗證碼輸入框已聚焦，等待手動輸入

#### 副作用 (Side Effects)

1. **DOM 查詢**: 查詢 `#TicketForm_agree` 元素
2. **勾選框點擊**: 勾選同意條款
3. **OCR 辨識**: 若啟用 OCR，執行驗證碼辨識
4. **文字輸入**: 填寫驗證碼

#### 拋出的例外 (Exceptions)

| 例外類型 | 觸發條件 | 處理建議 |
|---------|---------|---------|
| `RuntimeError` | 無法找到 `#TicketForm_agree` 元素 | 檢查頁面是否為驗證碼頁面 |

#### 演算法流程

```python
1. 使用 check_checkbox(tab, '#TicketForm_agree') 勾選同意條款（重試 2 次）
2. 若 config["ocr_captcha"]["enable"] 為 False:
   a. 調用 tixcraft_keyin_captcha_code(tab) 聚焦驗證碼輸入框
   b. 返回 False
3. 若 config["ocr_captcha"]["enable"] 為 True:
   a. 循環最多 99 次:
      i. 調用 tixcraft_auto_ocr(driver, tab, config, ocr, captcha_browser)
      ii. 若表單已提交或 URL 改變，跳出循環
   b. 返回 True
```

---

## 輔助函數介面

### 1. check_checkbox()

**位置**: `nodriver_tixcraft.py` (待實作或重用現有)
**說明**: 勾選指定的勾選框元素，支援重試機制

#### 函數簽章

```python
async def check_checkbox(
    tab: nodriver.Tab,
    selector: str,
    max_retries: int = 2
) -> bool:
    """
    勾選指定的勾選框元素。

    Args:
        tab: 當前 Tab 實例
        selector: CSS 選擇器
        max_retries: 最大重試次數

    Returns:
        bool: 成功勾選則返回 True，否則返回 False
    """
```

---

## 錯誤處理規範

### 錯誤分類

1. **配置錯誤** (`ValueError`)
   - 原因: settings.json 配置缺少必要欄位或格式錯誤
   - 處理: 在函數入口驗證配置，拋出 `ValueError` 並提供清晰的錯誤訊息
   - 範例: `ValueError("config missing required field: date_auto_select.enable")`

2. **頁面結構錯誤** (`RuntimeError`)
   - 原因: 無法找到預期的 DOM 元素或 JavaScript 變數
   - 處理: 拋出 `RuntimeError` 並記錄元素選擇器
   - 範例: `RuntimeError("Failed to locate element: #mapSelectArea")`

3. **JSON 解析錯誤** (`json.JSONDecodeError`)
   - 原因: zone_info JSON 格式不合法
   - 處理: 捕獲例外，記錄原始字串，返回 `None`
   - 範例: 在 `ticketmaster_parse_zone_info()` 中 try-except 包裹 `json.loads()`

4. **網路錯誤** (`TimeoutError`)
   - 原因: 頁面載入超時或網路連線失敗
   - 處理: 設定合理的超時時間（10 秒），拋出 `RuntimeError`
   - 範例: 在 `ticketmaster_get_ticketPriceList()` 中實作超時邏輯

### 錯誤日誌格式

**遵循 FR-015**：所有錯誤必須記錄清晰的日誌

```python
# 範例 1: 元素定位失敗
if not element:
    if config["advanced"]["verbose"]:
        print(f"[ERROR] Failed to locate element: {selector}")
    raise RuntimeError(f"Failed to locate element: {selector}")

# 範例 2: JSON 解析失敗
try:
    zone_info = json.loads(zone_string)
except json.JSONDecodeError as e:
    if config["advanced"]["verbose"]:
        print(f"[ERROR] JSON parse failed: {e}")
        print(f"[DEBUG] Raw string: {zone_string[:200]}...")
    return None
```

---

## 測試規範

### 測試層級

1. **單元測試**（Unit Tests）
   - 測試純函數（如 `get_ticketmaster_target_area()`）
   - 不需要 NoDriver Browser 實例
   - 使用 mock 資料（zone_info, config）

2. **整合測試**（Integration Tests）
   - 測試包含 NoDriver 互動的函數（如 `ticketmaster_date_auto_select()`）
   - 使用錄製的 HTML 頁面（fixtures）
   - 驗證 DOM 查詢與 JavaScript 執行

3. **端對端測試**（E2E Tests）
   - 測試完整的搶票流程（日期選擇 → 區域選擇 → 票數設定）
   - 使用真實的 Ticketmaster.com 頁面（測試環境）
   - 驗證每個步驟的頁面導航

### 測試覆蓋率目標

**遵循憲法第 VI 條**：核心功能必須有 >70% 程式碼覆蓋率

- **P1 函數** (MVP): 覆蓋率 >80%
  - `ticketmaster_date_auto_select()`
  - `ticketmaster_area_auto_select()`
  - `ticketmaster_assign_ticket_number()`

- **P2 函數**: 覆蓋率 >60%
  - `ticketmaster_parse_zone_info()`
  - `ticketmaster_get_ticketPriceList()`

- **P3 函數**: 覆蓋率 >40%
  - `ticketmaster_promo()`
  - `ticketmaster_captcha()`

### 測試案例模板

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_ticketmaster_date_auto_select_success():
    """測試成功匹配並選擇日期"""
    # Given
    driver = Mock()
    tab = AsyncMock()
    config = {
        "date_auto_select": {"enable": True, "date_keyword": "2025-12-25"},
        "area_auto_select": {"mode": "from top to bottom"},
        "tixcraft": {"pass_date_is_sold_out": False},
        "advanced": {"verbose": True}
    }

    # Mock DOM elements
    # ... (設定 mock 資料)

    # When
    result = await ticketmaster_date_auto_select(driver, tab, config)

    # Then
    assert result == True
    tab.query_selector_all.assert_called_once()
```

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**維護者**: Tickets Hunter 開發團隊
**相關文件**:
- 功能規格：`spec.md`
- 技術研究：`research.md`
- 資料模型：`data-model.md`
- JSON Schema：`zone-info-schema.md`
