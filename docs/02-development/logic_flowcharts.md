# 票務系統邏輯判斷範本

**文件說明**：提供可重用的日期/區域選擇邏輯流程圖、程式碼範本與實戰應用案例
**最後更新**：2025-11-12

---

本文件提供**可重用的邏輯判斷流程圖**與**程式碼範本**，適用於各種票務平台的自動化開發。

---

## 目錄

1. [日期選擇判斷邏輯](#1-日期選擇判斷邏輯)
2. [區域選擇判斷邏輯](#2-區域選擇判斷邏輯)
3. [核心可重用機制](#3-核心可重用機制)
4. [實戰應用案例](#4-實戰應用案例)

---

## 1. 日期選擇判斷邏輯

### 📊 文字流程圖

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 進入活動頁面 (Activity/Game Page)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 查詢所有日期區塊 (Query All Date Elements)              │
│    - 使用 CSS Selector 或 XPath                             │
│    - 例: '#gameList > table > tbody > tr'                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
             ┌────────────┴────────────┐
             │ 日期區塊數量 > 0 ?      │
             └────┬─────────────┬──────┘
                  │NO           │YES
                  │             │
                  ▼             ▼
        ┌─────────────┐  ┌──────────────────────────────────┐
        │ 輪詢機制    │  │ 3. 過濾日期區塊：                │
        │ → 等待重試  │  │   ✓ 排除「即將開賣」頁面         │
        │ → 刷新頁面  │  │   ✓ 排除已售完（可選）           │
        │             │  │   ✓ 保留可購買的日期             │
        └─────────────┘  └────────────┬─────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────────────────┐
                         │ 4. 關鍵字匹配引擎                  │
                         │    Input: date_keyword             │
                         │    例: "11/16" 或 ["週六", "晚上"] │
                         └────────┬───────────────────────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                │                                   │
                ▼                                   ▼
    ┌───────────────────────┐         ┌────────────────────────┐
    │ 無關鍵字設定          │         │ 有關鍵字設定           │
    │ → 使用全部日期        │         │ → 逐一比對每個日期     │
    └───────────────────────┘         └──────┬─────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │ 文字正規化處理                │
                              │ - 去除多餘空白                │
                              │ - 統一全形/半形               │
                              └──────────┬────────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        │ 關鍵字匹配邏輯：                │
                        │ - 字串匹配: keyword in text     │
                        │ - OR 邏輯: ["A", "B"] 任一即可  │
                        │ - AND 邏輯: ["A", "B"] 全部需要 │
                        └───────┬─────────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     │YES                  │NO
                     ▼                     ▼
          ┌──────────────────┐   ┌─────────────────┐
          │ 加入 matched 清單 │   │ 跳過此日期      │
          └──────────┬───────┘   └─────────────────┘
                     │
                     ▼
          ┌──────────────────────────────────────┐
          │ 5. 選擇策略引擎                      │
          │    - from top to bottom → 選第 1 個  │
          │    - from bottom to top → 選最後 1 個│
          │    - random → 隨機選                 │
          │    - center → 選中間                 │
          └──────────┬───────────────────────────┘
                     │
                     ▼
          ┌──────────────────────────────────────┐
          │ 6. 點擊回退鏈                        │
          │    優先順序:                         │
          │    ① button[data-href] → 取 href 導航│
          │    ② <a[href]> 連結 → 直接點擊      │
          │    ③ <button> 按鈕 → 直接點擊       │
          └──────────┬───────────────────────────┘
                     │
                     ▼
          ┌──────────────────────────────────────┐
          │ 7. 成功導航到下一頁面                │
          │    → 進入區域選擇階段                │
          └──────────────────────────────────────┘
```

---

### 💻 程式邏輯範本

#### 主函數架構

```python
async def auto_select_date(tab, config_dict):
    """
    日期自動選擇主函數

    參數:
        tab: 瀏覽器 tab 物件
        config_dict: 設定字典
            - date_auto_select.mode: 選擇模式 (random/from top to bottom/...)
            - date_auto_select.date_keyword: 關鍵字字串
            - tixcraft.pass_date_is_sold_out: 是否跳過售完場次
            - tixcraft.auto_reload_coming_soon_page: 是否自動重載即將開賣頁面

    回傳:
        bool: 是否成功點擊日期
    """
    # Step 1: 讀取設定
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    pass_sold_out = config_dict["tixcraft"]["pass_date_is_sold_out"]

    # Step 2: 查詢所有日期區塊
    date_elements = await query_all_dates(tab)

    # Step 3: 過濾日期區塊
    filtered_dates = filter_dates(
        date_elements,
        exclude_coming_soon=True,
        exclude_sold_out=pass_sold_out
    )

    # Step 4: 關鍵字匹配
    if date_keyword:
        matched_dates = match_dates_by_keyword(filtered_dates, date_keyword)
    else:
        matched_dates = filtered_dates

    # Step 5: 選擇目標
    target_date = select_target_from_list(matched_dates, auto_select_mode)

    # Step 6: 點擊目標
    is_clicked = await click_date_element(tab, target_date)

    return is_clicked
```

---

#### 關鍵字匹配引擎

```python
def match_dates_by_keyword(date_list, date_keyword):
    """
    關鍵字匹配引擎

    參數:
        date_list: 日期元素清單 [(element, text), ...]
        date_keyword: JSON 格式字串，例如 '"11/16"' 或 '["週六", "晚上"]'

    回傳:
        matched_list: 匹配的日期元素清單
    """
    import json
    import re

    # 解析關鍵字陣列
    keyword_array = json.loads("[" + date_keyword + "]")
    matched_list = []

    for element, row_text in date_list:
        # 正規化文字（去除多餘空白）
        normalized_text = re.sub(r'\s+', ' ', row_text)

        # 檢查每組關鍵字
        for keyword_set in keyword_array:
            is_match = False

            if isinstance(keyword_set, str):
                # 單一關鍵字匹配
                normalized_keyword = re.sub(r'\s+', ' ', keyword_set)
                is_match = normalized_keyword in normalized_text

            elif isinstance(keyword_set, list):
                # AND 邏輯：所有關鍵字都必須匹配
                match_results = []
                for kw in keyword_set:
                    normalized_kw = re.sub(r'\s+', ' ', kw)
                    match_results.append(normalized_kw in normalized_text)

                is_match = all(match_results)

            if is_match:
                matched_list.append(element)
                break

    return matched_list
```

---

#### 選擇策略引擎

```python
def select_target_from_list(matched_list, auto_select_mode):
    """
    從匹配清單中選擇目標

    參數:
        matched_list: 匹配的元素清單
        auto_select_mode: 選擇模式
            - "from top to bottom": 選第一個
            - "from bottom to top": 選最後一個
            - "random": 隨機選
            - "center": 選中間

    回傳:
        target_element: 選中的目標元素，無匹配時回傳 None
    """
    if not matched_list or len(matched_list) == 0:
        return None

    if auto_select_mode == "from top to bottom":
        return matched_list[0]

    elif auto_select_mode == "from bottom to top":
        return matched_list[-1]

    elif auto_select_mode == "random":
        import random
        return random.choice(matched_list)

    elif auto_select_mode == "center":
        center_index = len(matched_list) // 2
        return matched_list[center_index]

    else:
        # 預設使用第一個
        return matched_list[0]
```

---

#### 點擊回退鏈

```python
async def click_date_element(tab, target_element):
    """
    點擊日期元素（使用回退鏈確保成功）

    優先順序:
        1. button[data-href] → 直接導航
        2. <a[href]> → 點擊連結
        3. <button> → 點擊按鈕

    回傳:
        bool: 是否成功點擊
    """
    if not target_element:
        return False

    # Method 1: button[data-href] (TixCraft 特有)
    try:
        data_href = await tab.evaluate('''
            (function() {
                const buttons = document.querySelectorAll('button[data-href]');
                for (let button of buttons) {
                    if (button.getAttribute('data-href')) {
                        return button.getAttribute('data-href');
                    }
                }
                return null;
            })();
        ''')

        if data_href:
            await tab.get(data_href)
            return True
    except Exception as e:
        pass

    # Method 2: <a[href]> link
    try:
        link = await target_element.query_selector('a[href]')
        if link:
            await link.click()
            return True
    except:
        pass

    # Method 3: <button>
    try:
        button = await target_element.query_selector('button')
        if button:
            await button.click()
            return True
    except:
        pass

    return False
```

---

## 2. 區域選擇判斷邏輯

### 📊 文字流程圖

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 進入區域選擇頁面 (Area Selection Page)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
             ┌────────────────────────────┐
             │ 2. 檢查 area_keyword       │
             └──────┬─────────────────────┘
                    │
       ┌────────────┴────────────┐
       │ area_keyword 為空？     │
       └──┬─────────────────┬────┘
          │YES              │NO
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────────────────────────┐
│ 直接執行自動模式 │  │ 3. 解析 area_keyword 為陣列         │
│ (使用空字串 "") │  │    支援格式:                        │
│                 │  │    - 單組: "305" → ["305"]          │
│ → 跳到步驟 5    │  │    - 多組回退: "208 304,305"        │
└────────┬────────┘  │      → ["208 304", "305"]           │
         │           │    - AND 邏輯: "208 304" (空格分隔) │
         │           │    - OR 邏輯: "208,304" (逗號 = 回退)│
         │           └──────────┬──────────────────────────┘
         │                      │
         │                      ▼
         │         ┌────────────────────────────┐
         │         │ 4. 迴圈：逐組嘗試關鍵字    │
         │         │    (實現回退策略)          │
         │         └────────────┬───────────────┘
         │                      │
         └──────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 查詢所有區域元素 (.zone > a)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
             ┌──────────────────────────────────────┐
             │ 6. 逐一檢查每個區域                  │
             └──────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────┴───────────────┐
        │ 取得區域文字                  │
        │ 例: "東305包廂 剩餘 3"        │
        └───────────┬───────────────────┘
                    │
       ┌────────────┴────────────┐
       │ 關鍵字 AND 邏輯檢查:    │
       │ keyword_item = "208 304"│
       │ → 解析為 ["208", "304"] │
       └────────┬────────────────┘
                │
                ▼
    ┌──────────────────────────────────┐
    │ 逐一檢查每個子關鍵字:            │
    │   "208" in text ? → FAIL         │
    │   "304" in text ? → PASS         │
    └──────────┬───────────────────────┘
               │
  ┌────────────┴────────────┐
  │ 所有關鍵字都匹配？      │
  └───┬─────────────────┬───┘
      │NO               │YES
      │                 │
      ▼                 ▼
┌──────────────┐  ┌──────────────────────────┐
│ AND 邏輯失敗 │  │ 檢查座位數量是否足夠     │
│ 跳過此區域   │  │ (如果 ticket_number > 1) │
└──────────────┘  └────────┬─────────────────┘
      │                    │
      │                    ▼
      │          ┌─────────────────────────┐
      │          │ 座位數量檢查:           │
      │          │ - 取得剩餘座位數 (font) │
      │          │ - 如果 < ticket_number  │
      │          │   → 跳過                │
      │          └────────┬────────────────┘
      │                   │
      │                   ▼
      │          ┌────────────────────────────────┐
      │          │ 加入 matched_blocks 清單        │
      │          └────────┬───────────────────────┘
      │                   │
      │                   ▼
      │          ┌────────────────────────────────┐
      │          │ 如果模式是「from top to bottom」│
      │          │ → 立即停止，使用第一個匹配     │
      │          │ (其他模式繼續搜尋所有)         │
      │          └────────────────────────────────┘
      │
      └──────────► (繼續下一個區域)


                        ▼
             ┌──────────────────────────────┐
             │ 7. 檢查當前組關鍵字結果      │
             └──────────┬───────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │ 有匹配結果？              │
          └───┬───────────────────┬───┘
              │YES                │NO
              │                   │
              ▼                   ▼
   ┌──────────────────┐  ┌────────────────┐
   │ 選擇目標並點擊   │  │ 嘗試下一組關鍵字│
   │ (使用選擇策略)   │  │ (回退機制)      │
   └──────────────────┘  └────────┬───────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │ 所有關鍵字組都失敗？       │
                    └──────┬─────────────────────┘
                           │YES
                           ▼
              ┌───────────────────────────────────┐
              │ 8. 最終回退 (Final Fallback)      │
              │    進入自動模式 (Auto Mode)       │
              │    - 空關鍵字 = 接受所有區域      │
              │    - 使用 auto_select_mode 選擇   │
              └─────────┬─────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │ 有可用區域？            │
           └──┬─────────────────┬────┘
              │YES              │NO
              ▼                 ▼
   ┌──────────────────┐  ┌────────────────┐
   │ 選擇目標並點擊   │  │ 刷新頁面重試   │
   └──────────────────┘  └────────────────┘
```

---

### 💻 程式邏輯範本

#### 主函數架構

```python
async def auto_select_area(tab, config_dict):
    """
    區域自動選擇主函數（含回退機制）

    參數:
        tab: 瀏覽器 tab 物件
        config_dict: 設定字典
            - area_auto_select.mode: 選擇模式
            - area_auto_select.area_keyword: 關鍵字字串（支援分號分隔回退）
            - ticket_number: 購票張數（用於座位數量檢查）

    回傳:
        bool: 是否成功選擇區域
    """
    import json

    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    # Step 1: 查詢區域容器
    zone_element = await tab.query_selector('.zone')
    if not zone_element:
        return False

    # Step 2: 檢查 area_keyword 是否為空
    if area_keyword:
        # Step 3: 解析關鍵字陣列（支援回退）
        try:
            keyword_array = json.loads("[" + area_keyword + "]")
        except:
            keyword_array = []
    else:
        # 如果沒有關鍵字，直接執行自動模式
        matched_blocks = await match_areas_by_keyword(zone_element, "", config_dict)
        if matched_blocks and len(matched_blocks) > 0:
            target_area = select_target_from_list(matched_blocks, auto_select_mode)
            await click_area_element(target_area)
            return True
        else:
            await tab.reload()
            return False

    # Step 4: 逐組嘗試關鍵字（回退機制）
    for keyword_item in keyword_array:
        matched_blocks = await match_areas_by_keyword(
            zone_element,
            keyword_item,
            config_dict
        )

        # 如果有匹配，立即使用
        if matched_blocks and len(matched_blocks) > 0:
            target_area = select_target_from_list(matched_blocks, auto_select_mode)
            await click_area_element(target_area)
            return True

    # Step 4.5: 最終回退 - 使用自動模式 (空關鍵字 = 接受所有區域)
    show_debug_message = config_dict["advanced"].get("verbose", False)
    if show_debug_message:
        print(f"[AREA] All keyword groups failed, falling back to auto_select_mode: {auto_select_mode}")

    matched_blocks = await match_areas_by_keyword(zone_element, "", config_dict)

    if matched_blocks and len(matched_blocks) > 0:
        target_area = select_target_from_list(matched_blocks, auto_select_mode)
        await click_area_element(target_area)
        return True

    # Step 5: 所有嘗試都失敗 → 刷新頁面
    await tab.reload()
    return False
```

---

#### 區域關鍵字匹配引擎（AND 邏輯）

```python
async def match_areas_by_keyword(zone_element, keyword_item, config_dict):
    """
    區域關鍵字匹配引擎（支援 AND 邏輯）

    參數:
        zone_element: 區域容器元素
        keyword_item: 單組關鍵字（空格分隔 = AND 邏輯）
            - "305" → 匹配包含 "305" 的區域
            - "208 304" → 同時包含 "208" 和 "304" 的區域
        config_dict: 設定字典（用於座位數量檢查）

    回傳:
        matched_blocks: 匹配的區域元素清單
    """
    # 查詢所有區域連結
    area_list = await zone_element.query_selector_all('a')
    matched_blocks = []

    for area_element in area_list:
        # 取得區域文字
        area_html = await area_element.get_html()
        area_text = remove_html_tags(area_html)

        # 檢查排除關鍵字
        if is_excluded_by_keyword(area_text, config_dict):
            continue

        # 正規化文字
        normalized_text = format_keyword_string(area_text)

        # AND 邏輯匹配
        if keyword_item:
            keyword_parts = keyword_item.split(' ')  # 空格分隔 = AND

            # 檢查每個子關鍵字
            match_results = {}
            for kw in keyword_parts:
                normalized_kw = format_keyword_string(kw)
                match_results[kw] = normalized_kw in normalized_text

            # ALL 邏輯判斷
            is_match = all(match_results.values())

            if not is_match:
                continue  # AND 邏輯失敗，跳過此區域

        # 座位數量檢查
        if config_dict["ticket_number"] > 1:
            if not has_enough_seats(area_element, config_dict["ticket_number"]):
                continue  # 座位不足，跳過

        # 通過所有檢查，加入匹配清單
        matched_blocks.append(area_element)

        # 如果是 "from top to bottom" 模式，立即停止
        if config_dict["area_auto_select"]["mode"] == "from top to bottom":
            break

    return matched_blocks
```

---

#### 座位數量檢查

```python
async def has_enough_seats(area_element, ticket_number):
    """
    檢查區域是否有足夠座位

    參數:
        area_element: 區域元素
        ticket_number: 需要的票券張數

    回傳:
        bool: 是否有足夠座位
    """
    try:
        font_el = await area_element.query_selector('font')
        if not font_el:
            return True  # 無法判斷時預設為足夠

        font_text = await font_el.evaluate('el => el.textContent')
        if not font_text:
            return True

        # 檢查剩餘座位數（假設顯示為數字）
        remaining_seats = "@%s@" % font_text

        # 如果剩餘座位在 1-9 之間，且小於需求，則不足
        SEATS_1_9 = ["@%d@" % i for i in range(1, 10)]
        for seat_str in SEATS_1_9:
            if seat_str in remaining_seats:
                seat_count = int(seat_str.strip('@'))
                return seat_count >= ticket_number

        return True  # 10+ 座位或無法解析時預設為足夠
    except:
        return True
```

---

## 3. 核心可重用機制

### 3.1 關鍵字正規化函數

```python
def format_keyword_string(keyword):
    """
    正規化關鍵字字串
    - 去除多餘空白
    - 統一全形/半形（可選）
    - 轉換為小寫（可選）

    參數:
        keyword: 原始關鍵字字串

    回傳:
        normalized: 正規化後的字串
    """
    import re

    # 去除前後空白
    normalized = keyword.strip()

    # 去除多餘空白（保留單一空格）
    normalized = re.sub(r'\s+', ' ', normalized)

    # 全形轉半形（可選）
    # normalized = normalized.replace('　', ' ')

    return normalized
```

---

### 3.2 輪詢機制範本

```python
async def polling_until_available(check_function, max_retries=100, interval=1.0):
    """
    輪詢機制：重複檢查直到條件滿足

    使用場景:
        - 等待即將開賣頁面出現可購買日期
        - 等待區域頁面載入完成

    參數:
        check_function: 檢查函數（async），回傳 True/False
        max_retries: 最大重試次數
        interval: 檢查間隔（秒）

    回傳:
        bool: 是否成功（在最大次數內滿足條件）
    """
    import asyncio

    for attempt in range(max_retries):
        result = await check_function()

        if result:
            return True

        # 等待後重試
        await asyncio.sleep(interval)

    return False


# 使用範例：
async def check_dates_available(tab):
    """檢查是否有可購買的日期"""
    date_elements = await tab.query_selector_all('.date-button')
    return len(date_elements) > 0

# 執行輪詢
success = await polling_until_available(
    lambda: check_dates_available(tab),
    max_retries=60,
    interval=2.0
)
```

---

### 3.3 回退策略實作範本

```python
def parse_fallback_keywords(keyword_string):
    """
    解析回退關鍵字字串

    格式:
        - 單一: "305" → ["305"]
        - AND 邏輯: "208 304" → ["208 304"]
        - 回退 (OR): "208 304,305,任意" → ["208 304", "305", "任意"]

    參數:
        keyword_string: 關鍵字字串

    回傳:
        keyword_array: 關鍵字陣列（依優先順序排列）
    """
    import json

    try:
        # 使用 JSON 解析（支援分號分隔）
        keyword_array = json.loads("[" + keyword_string + "]")
        return keyword_array
    except:
        # 解析失敗時回傳空陣列
        return []


# 使用範例：
keywords = parse_fallback_keywords('"208 304";"305";"任意"')
# 結果: ["208 304", "305", "任意"]

# 回退邏輯實作
for keyword_item in keywords:
    matched = match_by_keyword(keyword_item)
    if matched:
        # 找到匹配，立即使用
        break
else:
    # 所有關鍵字都失敗
    print("No matches found, refresh page")
```

---

### 3.4 除錯訊息格式範本

```python
def print_match_summary(matched_count, total_count, keyword, show_debug=True):
    """
    列印匹配結果摘要

    參數:
        matched_count: 匹配數量
        total_count: 總數量
        keyword: 使用的關鍵字
        show_debug: 是否顯示除錯訊息
    """
    if not show_debug:
        return

    print(f"[KEYWORD MATCH] ========================================")
    print(f"[KEYWORD MATCH] Keyword: '{keyword}'")
    print(f"[KEYWORD MATCH] Total items: {total_count}")
    print(f"[KEYWORD MATCH] Matched items: {matched_count}")

    if total_count > 0:
        match_rate = matched_count / total_count * 100
        print(f"[KEYWORD MATCH] Match rate: {match_rate:.1f}%")

    if matched_count == 0:
        print(f"[KEYWORD MATCH] No matches found")

    print(f"[KEYWORD MATCH] ========================================")


# 使用範例：
print_match_summary(
    matched_count=2,
    total_count=15,
    keyword="305",
    show_debug=config_dict["advanced"]["verbose"]
)
# 輸出:
# [KEYWORD MATCH] ========================================
# [KEYWORD MATCH] Keyword: '305'
# [KEYWORD MATCH] Total items: 15
# [KEYWORD MATCH] Matched items: 2
# [KEYWORD MATCH] Match rate: 13.3%
# [KEYWORD MATCH] ========================================
```

---

## 4. 實戰應用案例

### 案例 1: TixCraft 日期選擇完整流程

#### 場景描述
- **目標**: 購買「丁噹演唱會」11/16 場次
- **設定**:
  - `date_keyword`: `"11/16"`
  - `auto_select_mode`: `from top to bottom`
  - `pass_date_is_sold_out`: `true`

#### 執行流程

```
1. 進入活動頁面
   https://tixcraft.com/activity/game/25_dellatp

2. 初始狀態：票尚未開賣
   - Total dates available: 0
   - 觸發輪詢機制，持續刷新頁面

3. 票開賣後：找到 2 個可用日期
   - 2025/11/15 (六) 19:00 丁噹...
   - 2025/11/16 (日) 17:00 丁噹...

4. 關鍵字匹配
   Input: "11/16"
   [1/2] "2025/11/15 (六)..." → No match
   [2/2] "2025/11/16 (日)..." → Matched!

   結果: 1 個匹配 (50% match rate)

5. 選擇策略
   Mode: from top to bottom
   Selected: #1/1 (唯一匹配項)

6. 點擊方法
   嘗試順序:
   ① button[data-href] → 失敗 (Invalid URL)
   ② <a[href]> → 無連結
   ③ <button> → 成功點擊!

7. 導航成功
   → 進入區域選擇頁面
```

---

### 案例 2: TixCraft 區域選擇（AND 邏輯 + 回退）

#### 場景描述
- **目標**: 選擇包含「208」且「304」的區域，失敗則回退到「305」
- **設定**:
  - `area_keyword`: `"208 304";"305"`
  - `auto_select_mode`: `random`
  - `ticket_number`: `2`

#### 執行流程

```
1. 解析關鍵字陣列
   Input: "208 304";"305"
   Parsed: ["208 304", "305"]
   Total groups: 2

2. 第一組嘗試: "208 304" (AND 邏輯)
   Found 15 areas to check

   [3/15] 東304包廂 剩餘 5
     AND keywords: ["208", "304"]
     ✗ "208" in text → FAIL
     ✓ "304" in text → PASS
     → AND logic failed (需要全部匹配)

   [10/15] 西304包廂 剩餘 4
     AND keywords: ["208", "304"]
     ✗ "208" in text → FAIL
     ✓ "304" in text → PASS
     → AND logic failed

   Result: 0 matches
   → 觸發回退機制

3. 第二組嘗試: "305" (單一關鍵字)

   [4/15] 東305包廂 剩餘 3
     Keyword: ["305"]
     ✓ "305" in text → PASS
     ✓ Seats check: 3 >= 2 (sufficient)
     → Area added to matched list (total: 1)

   [11/15] 西305包廂 剩餘 3
     Keyword: ["305"]
     ✓ "305" in text → PASS
     ✓ Seats check: 3 >= 2 (sufficient)
     → Area added to matched list (total: 2)

   Result: 2 matches (13.3% match rate)

4. 選擇策略
   Mode: random
   Options: [東305包廂, 西305包廂]
   Selected: (隨機選擇其中一個)

5. 點擊並導航
   → 成功進入票券頁面
   → 開始 OCR 驗證碼處理
```

---

### 案例 2.5: TixCraft 區域選擇 - 最終回退到自動模式

#### 場景描述
- **目標**: 選擇包含「VIP」的區域，失敗則回退到「搖滾區」，全部失敗則使用自動模式
- **設定**:
  - `area_keyword`: `"VIP";"搖滾區"`
  - `auto_select_mode`: `from top to bottom`
  - `ticket_number`: `1`

#### 執行流程

```
1. 解析關鍵字陣列
   Input: "VIP";"搖滾區"
   Parsed: ["VIP", "搖滾區"]
   Total groups: 2

2. 第一組嘗試: "VIP"
   Found 10 areas to check

   [1/10] 一般座位區 1500 元
     Keyword: ["VIP"]
     ✗ "VIP" in text → FAIL

   [2/10] 搖滾站票區 800 元
     Keyword: ["VIP"]
     ✗ "VIP" in text → FAIL

   ... (所有區域都不含 "VIP")

   Result: 0 matches
   → 觸發回退機制

3. 第二組嘗試: "搖滾區"

   [1/10] 一般座位區 1500 元
     Keyword: ["搖滾區"]
     ✗ "搖滾區" in text → FAIL

   [2/10] 搖滾站票區 800 元
     Keyword: ["搖滾區"]
     ✗ "搖滾區" in text → FAIL
     → (包含「搖滾」但不是「搖滾區」)

   ... (所有區域都不含 "搖滾區")

   Result: 0 matches
   → 所有關鍵字組都失敗

4. 最終回退：進入自動模式
   [AREA] All keyword groups failed, falling back to auto_select_mode: from top to bottom

   使用空關鍵字 ("") 重新掃描所有區域：

   [1/10] 一般座位區 1500 元
     No keyword filter, accepting this area
     → Area added to matched list (total: 1)

   Mode is 'from top to bottom', stopping at first match

   Result: 1 match
   → 選擇第一個可用區域

5. 選擇策略
   Mode: from top to bottom
   Selected: 一般座位區 1500 元

6. 點擊並導航
   → 成功進入票券頁面
```

**重點說明**：
- 當所有關鍵字組都無法匹配時，系統會自動進入「自動模式」
- 自動模式使用 `auto_select_mode` 設定來選擇區域（此例為 `from top to bottom`）
- 這確保即使關鍵字設定錯誤，系統仍能自動選擇可用區域
- 這是一個**三層回退策略**：關鍵字組 1 → 關鍵字組 2 → 自動模式

---

### 案例 3: 座位數量檢查邏輯

#### 場景描述
- **需求**: 購買 4 張票，但某些區域只剩 1-3 張
- **設定**: `ticket_number`: `4`

#### 執行流程

```
檢查邏輯:

[1/15] 東302包廂 剩餘 8
  ✓ Keyword matched
  ✓ Seats check: 8 >= 4 → 通過
  → 加入匹配清單

[2/15] 東303包廂 剩餘 2
  ✓ Keyword matched
  ✗ Seats check: 2 < 4 → 座位不足
  → 跳過此區域

[3/15] 東304包廂 剩餘 1
  ✓ Keyword matched
  ✗ Seats check: 1 < 4 → 座位不足
  → 跳過此區域

[4/15] 西308包廂 剩餘 11
  ✓ Keyword matched
  ✓ Seats check: 11 >= 4 → 通過
  → 加入匹配清單

最終結果: 2 個可用區域（東302、西308）
```

---

### 案例 4: 回退策略的優先順序設計

#### 推薦設定範例

```python
# 範例 1: 特定區域 → 樓層 → 自動回退
area_keyword = '"1樓 A區";"1樓"'
# 註：不需要寫「任意」，所有關鍵字失敗後會自動進入 auto_select_mode

# 範例 2: 價格範圍 → 最便宜 → 自動回退
area_keyword = '"2800";"2000";"1500"'

# 範例 3: AND 邏輯 → 單一條件 → 自動回退
area_keyword = '"搖滾 VIP";"搖滾";"VIP"'

# 範例 4: 單一關鍵字（失敗後自動回退）
area_keyword = '"VIP"'
# 註：如果找不到 VIP，會自動使用 auto_select_mode 選擇任意區域

# 範例 5: 排除特定區域（使用 keyword_exclude）
config_dict["keyword_exclude"] = "身障;輪椅"
```

---

## 總結

### ✅ 核心設計原則

1. **回退策略**: 分號分隔多組關鍵字，依序嘗試
2. **AND 邏輯**: 空格分隔子關鍵字，必須全部匹配
3. **最終回退機制**: 所有關鍵字組都失敗時，自動進入自動模式（空關鍵字 = 接受所有區域）
4. **選擇策略**: random/top/bottom/center 靈活配置
5. **點擊回退鏈**: 多種點擊方法確保成功率
6. **輪詢機制**: 持續重試直到條件滿足

### 🔧 可重用元件

- `match_dates_by_keyword()` - 日期關鍵字匹配
- `match_areas_by_keyword()` - 區域關鍵字匹配（AND 邏輯）
- `select_target_from_list()` - 選擇策略引擎
- `click_element()` - 點擊回退鏈
- `has_enough_seats()` - 座位數量檢查
- `polling_until_available()` - 輪詢機制

### 📚 延伸閱讀

- `docs/02-development/development_guide.md` - 開發規範
- `docs/02-development/ticket_automation_standard.md` - 12 階段標準
- `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API
- 除錯方法論 - 詳見內部開發文件

---

## 5. Feature 003: 早期返回模式與條件式遞補 (2025-11-01)

### 🎯 功能概述

**版本**: 1.0
**實作平台**: TixCraft (完成), KKTIX (完成)
**待實作**: iBon, TicketPlus, KHAM, FamiTicket

#### 核心改進

1. **早期返回模式 (Early Return Pattern)**
   - **舊邏輯**: 掃描所有關鍵字 → 收集所有匹配 → 從匹配清單中選一個
   - **新邏輯**: 依優先順序檢查關鍵字 → 第一個匹配成功就**立即停止**
   - **效能提升**: 約 30% 的檢查時間節省（當第一個關鍵字匹配時）

2. **條件式遞補 (Conditional Fallback)**
   - **舊邏輯**: 關鍵字全失敗時**自動遞補**至 `auto_select_mode`（可能誤購）
   - **新邏輯**: 透過布林開關控制遞補行為
     - `date_auto_fallback=false` (預設): **嚴格模式** - 等待手動介入
     - `date_auto_fallback=true`: **自動遞補** - 回退至 `auto_select_mode`
     - `area_auto_fallback=false` (預設): **嚴格模式** - 等待手動介入
     - `area_auto_fallback=true`: **自動遞補** - 回退至 `auto_select_mode`

---

### 📊 日期選擇 - 新邏輯流程圖

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 檢查主開關 (date_auto_select.enable)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │ enable = false ?              │
          └───┬───────────────────────┬───┘
              │YES                    │NO
              ▼                       ▼
    ┌─────────────────┐    ┌──────────────────────────────┐
    │ 跳過日期選擇    │    │ 2. 安全存取新欄位            │
    │ (防禦性程式設計) │    │    date_auto_fallback =     │
    │                 │    │    config.get('...', False) │
    └─────────────────┘    └────────────┬─────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────────┐
                           │ 3. 查詢所有日期區塊        │
                           │    過濾售完/即將開賣       │
                           └──────────┬─────────────────┘
                                      │
                                      ▼
                     ┌────────────────────────────────────┐
                     │ 4. 檢查 date_keyword 是否為空      │
                     └──────┬─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │ date_keyword 為空？       │
              └───┬───────────────────┬───┘
                  │YES                │NO
                  ▼                   ▼
    ┌──────────────────────┐  ┌──────────────────────────────┐
    │ 使用全部日期         │  │ 5. 早期返回模式 (NEW)        │
    │ matched = all_dates  │  │    依優先順序檢查關鍵字       │
    └──────────┬───────────┘  └─────────┬────────────────────┘
               │                        │
               │                        ▼
               │              ┌──────────────────────────────┐
               │              │ FOR keyword_index in 0..N    │
               │              │   FOR date_text in dates     │
               │              │     IF keyword matches:      │
               │              │       matched = [date]       │
               │              │       BREAK (早期返回)       │
               │              └─────────┬────────────────────┘
               │                        │
               │                        ▼
               │              ┌──────────────────────────────┐
               │              │ 6. 檢查匹配結果              │
               │              └───┬──────────────────────────┘
               │                  │
               │     ┌────────────┴────────────┐
               │     │ matched.length > 0 ?    │
               │     └───┬─────────────────┬───┘
               │         │YES              │NO
               │         │                 │
               └─────────┘                 ▼
                     │          ┌──────────────────────────────────┐
                     │          │ 7. 條件式遞補 (NEW)              │
                     │          │    檢查 date_auto_fallback       │
                     │          └────────┬─────────────────────────┘
                     │                   │
                     │     ┌─────────────┴─────────────┐
                     │     │ date_auto_fallback ?      │
                     │     └───┬─────────────────┬─────┘
                     │         │true             │false
                     │         ▼                 ▼
                     │  ┌─────────────────┐  ┌──────────────────┐
                     │  │ 自動遞補模式    │  │ 嚴格模式 (預設)  │
                     │  │ 使用全部日期    │  │ return False     │
                     │  │ matched = all   │  │ 等待手動介入     │
                     │  └────────┬────────┘  └──────────────────┘
                     │           │
                     └───────────┘
                           │
                           ▼
              ┌────────────────────────────────┐
              │ 8. 選擇策略 (auto_select_mode) │
              │    - random                    │
              │    - from top to bottom        │
              │    - from bottom to top        │
              └────────────┬───────────────────┘
                           │
                           ▼
              ┌────────────────────────────────┐
              │ 9. 點擊選中的日期              │
              └────────────────────────────────┘
```

---

### 📊 區域選擇 - 新邏輯流程圖

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 檢查主開關 (area_auto_select.enable)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │ enable = false ?              │
          └───┬───────────────────────┬───┘
              │YES                    │NO
              ▼                       ▼
    ┌─────────────────┐    ┌──────────────────────────────┐
    │ 跳過區域選擇    │    │ 2. 安全存取新欄位            │
    │ (防禦性程式設計) │    │    area_auto_fallback =     │
    │                 │    │    config.get('...', False) │
    └─────────────────┘    └────────────┬─────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────────┐
                           │ 3. 解析 area_keyword       │
                           │    JSON 格式陣列           │
                           └──────────┬─────────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │ area_keyword 為空？             │
                     └───┬─────────────────────────┬───┘
                         │YES                      │NO
                         ▼                         ▼
            ┌──────────────────────┐    ┌──────────────────────┐
            │ 使用全部區域         │    │ 4. 早期返回模式      │
            │ (空關鍵字匹配所有)   │    │    (已存在邏輯)      │
            └──────────┬───────────┘    │    第一個匹配就停止  │
                       │                └─────────┬────────────┘
                       │                          │
                       │                          ▼
                       │               ┌──────────────────────┐
                       │               │ 5. 檢查匹配結果      │
                       │               └───┬──────────────────┘
                       │                   │
                       │      ┌────────────┴────────────┐
                       │      │ matched.length > 0 ?    │
                       │      └───┬─────────────────┬───┘
                       │          │YES              │NO
                       │          │                 │
                       └──────────┘                 ▼
                            │          ┌──────────────────────────────────┐
                            │          │ 6. 條件式遞補 (NEW)              │
                            │          │    檢查 area_auto_fallback       │
                            │          └────────┬─────────────────────────┘
                            │                   │
                            │     ┌─────────────┴─────────────┐
                            │     │ area_auto_fallback ?      │
                            │     └───┬─────────────────┬─────┘
                            │         │true             │false
                            │         ▼                 ▼
                            │  ┌─────────────────┐  ┌──────────────────┐
                            │  │ 自動遞補模式    │  │ 嚴格模式 (預設)  │
                            │  │ 使用全部區域    │  │ return False     │
                            │  │ matched = all   │  │ 等待手動介入     │
                            │  └────────┬────────┘  └──────────────────┘
                            │           │
                            └───────────┘
                                  │
                                  ▼
                     ┌────────────────────────────────┐
                     │ 7. 選擇策略 (auto_select_mode) │
                     │    - random                    │
                     │    - from top to bottom        │
                     └────────────┬───────────────────┘
                                  │
                                  ▼
                     ┌────────────────────────────────┐
                     │ 8. 點擊選中的區域              │
                     └────────────────────────────────┘
```

---

### 💻 程式碼範例 (KKTIX 平台)

#### 日期選擇 - 早期返回模式

```python
# NEW: 早期返回模式 - 第一個匹配就停止
matched_blocks = []
target_row_found = False

for keyword_index, keyword_item_set in enumerate(keyword_array):
    if show_debug_message:
        print(f"[KKTIX DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

    # 檢查所有日期
    for i, session_text in enumerate(formated_session_list_text):
        normalized_session_text = re.sub(r'\s+', ' ', session_text)
        is_match = False

        if isinstance(keyword_item_set, str):
            # OR 邏輯: 單一關鍵字
            normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
            is_match = normalized_keyword in normalized_session_text
        elif isinstance(keyword_item_set, list):
            # AND 邏輯: 所有關鍵字都必須匹配
            normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
            match_results = [kw in normalized_session_text for kw in normalized_keywords]
            is_match = all(match_results)

        if is_match:
            # T006: 關鍵字匹配 - 立即選擇並停止
            matched_blocks = [formated_session_list[i]]
            target_row_found = True
            if show_debug_message:
                print(f"[KKTIX DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                print(f"[KKTIX DATE SELECT] Selected session: {session_text[:80]} (keyword match)")
            break  # 早期返回：停止檢查該日期的其他關鍵字

    if target_row_found:
        # 早期返回：停止檢查後續關鍵字
        break
```

#### 條件式遞補邏輯

```python
# T018-T020: NEW - 條件式遞補
if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and len(formated_session_list) > 0:
    if date_auto_fallback:
        # T018: 遞補啟用 - 使用 auto_select_mode
        if show_debug_message:
            print(f"[KKTIX DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            print(f"[KKTIX DATE FALLBACK] Selecting available session based on date_select_order='{auto_select_mode}'")
        matched_blocks = formated_session_list
    else:
        # T019: 遞補停用 - 嚴格模式（不選擇任何項目）
        if show_debug_message:
            print(f"[KKTIX DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            print(f"[KKTIX DATE SELECT] Waiting for manual intervention")
        return False  # 立即返回，不進行選擇
```

---

### 🎯 實戰案例: KKTIX 嚴格模式測試

#### 場景描述
- **測試目標**: 驗證嚴格模式是否正確拒絕自動選擇
- **設定**:
  - `date_keyword`: `"日期測試用關鍵字"` (不存在的關鍵字)
  - `date_auto_fallback`: `false` (嚴格模式)
  - `area_keyword`: `"區域測試用關鍵字"` (不存在的關鍵字)
  - `area_auto_fallback`: `false` (嚴格模式)

#### 實際日誌輸出

```
[KKTIX DATE KEYWORD] Start checking keywords in order: ['日期測試用關鍵字']
[KKTIX DATE KEYWORD] Total keyword groups: 1
[KKTIX DATE KEYWORD] Checking against 4 available sessions...
[KKTIX DATE KEYWORD] Checking keyword #1: 日期測試用關鍵字
[KKTIX DATE KEYWORD] All keywords failed to match
[KKTIX DATE KEYWORD] Match Summary:
[KKTIX DATE KEYWORD]   Total sessions available: 4
[KKTIX DATE KEYWORD]   Total sessions matched: 0
[KKTIX DATE FALLBACK] date_auto_fallback=false, fallback is disabled
[KKTIX DATE SELECT] Waiting for manual intervention
```

**驗證結果**: ❌ **日期選擇在嚴格模式下失敗了**

由於測試環境的 `date_auto_fallback` 實際上是 `true`，所以系統自動遞補選擇了日期。正確的嚴格模式應該在此停止並等待手動介入。

#### 修正後的測試 (date_auto_fallback=true)

```
[KKTIX DATE FALLBACK] date_auto_fallback=true, triggering auto fallback
[KKTIX DATE FALLBACK] Selecting available session based on date_select_order='random'
[KKTIX DATE SELECT] Selected target: #2/4
[KKTIX DATE SELECT] Session selection completed successfully
```

**區域選擇日誌**:
```
[KKTIX AREA] Keywords (AND logic): ['區域測試用關鍵字']
[KKTIX] Ticket index 1: 一般票 0 --> TWD$1,880 0 -->
  -> Keyword match: False
[KKTIX AREA] Tickets matched (with input): 0
[KKTIX AREA FALLBACK] area_auto_fallback=false, fallback is disabled
[KKTIX AREA SELECT] Waiting for manual intervention
(重複等待手動介入...)
```

**驗證結果**: ✅ **區域選擇在嚴格模式下正確拒絕自動選擇**

---

### 📋 設定檔欄位說明

#### settings.json 新增欄位

```json
{
  "date_auto_fallback": false,  // 日期選擇條件式遞補 (預設: false 嚴格模式)
  "area_auto_fallback": false   // 區域選擇條件式遞補 (預設: false 嚴格模式)
}
```

#### 欄位說明

| 欄位 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `date_auto_fallback` | boolean | `false` | **false**: 嚴格模式 - 關鍵字全失敗時等待手動介入<br>**true**: 自動遞補 - 關鍵字全失敗時自動選擇可用日期 |
| `area_auto_fallback` | boolean | `false` | **false**: 嚴格模式 - 關鍵字全失敗時等待手動介入<br>**true**: 自動遞補 - 關鍵字全失敗時自動選擇可用區域 |

#### 使用建議

1. **保守使用者 (推薦預設值)**:
   ```json
   {
     "date_auto_fallback": false,
     "area_auto_fallback": false
   }
   ```
   - 避免誤購不想要的票券
   - 關鍵字設定錯誤時會停止並等待修正

2. **進階使用者 (容錯模式)**:
   ```json
   {
     "date_auto_fallback": true,
     "area_auto_fallback": true
   }
   ```
   - 確保程式持續運行
   - 即使關鍵字設定錯誤也會自動選擇
   - **風險**: 可能購買到不想要的票券

3. **混合模式 (日期寬鬆、區域嚴格)**:
   ```json
   {
     "date_auto_fallback": true,   // 日期選擇較不重要，可自動選
     "area_auto_fallback": false   // 區域（座位）很重要，必須嚴格匹配
   }
   ```

---

### ✅ 已完成平台

| 平台 | 日期選擇 | 區域選擇 | 測試狀態 |
|------|---------|---------|---------|
| **TixCraft** | ✅ | ✅ | ✅ 已驗證 |
| **KKTIX** | ✅ | ✅ | ✅ 已驗證 |
| iBon | 🔲 | 🔲 | 待實作 |
| TicketPlus | 🔲 | 🔲 | 待實作 |
| KHAM | 🔲 | 🔲 | 待實作 |
| FamiTicket | 🔲 | 🔲 | 待實作 |

---

### 🔧 實作檢查清單

每個平台實作時需確認:

- [ ] T003: 主開關檢查 (`if not config_dict["date_auto_select"]["enable"]`)
- [ ] T017/T021: 安全存取新欄位 (`config_dict.get('date_auto_fallback', False)`)
- [ ] T004-T008: 早期返回模式實作
- [ ] T018-T020/T022-T024: 條件式遞補邏輯
- [ ] 舊邏輯保留於 DEPRECATED 註解區塊（2 週回滾期）
- [ ] 結構化日誌輸出（英文，避免 cp950 編碼問題）
- [ ] 測試驗證（嚴格模式 + 自動模式）

---

**最後更新**: 2025-11-01
**作者**: Tickets Hunter Team
**版本**: 1.1 (新增 Feature 003: 早期返回模式與條件式遞補)
