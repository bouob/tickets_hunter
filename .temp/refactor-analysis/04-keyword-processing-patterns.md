# 關鍵字處理代碼分析

**分析檔案**：`src/nodriver_tixcraft.py`
**關鍵字相關代碼**：200+ 處

---

## 一、關鍵字解析位置（`json.loads` 模式）

找到 **25 處**使用相同的 JSON 解析模式：

| 行號 | 平台/功能 | 代碼片段 |
|------|----------|----------|
| 1649 | KKTIX 日期 | `json.loads("[" + date_keyword + "]")` |
| 3770 | TicketMaster 日期 | `json.loads("[" + date_keyword + "]")` |
| 3921 | TicketMaster 區域 | `json.loads("[" + area_keyword + "]")` |
| 4778 | TixCraft 日期 | `json.loads("[" + date_keyword + "]")` |
| 5037 | TixCraft 區域 | `json.loads("[" + area_keyword + "]")` |
| 5463 | TixCraft 區域2 | `json.loads("[" + area_keyword + "]")` |
| 6783 | TixCraft 票價 | `json.loads("[" + original_keyword + "]")` |
| 7049 | TixCraft 排除 | `json.loads("[" + keyword_exclude + "]")` |
| 8869 | iBon 區域 | `json.loads("[" + area_keyword_raw + "]")` |
| 9746 | iBon 日期 | `json.loads("[" + date_keyword + "]")` |
| 10669 | UrbtIx 日期 | `json.loads("[" + date_keyword + "]")` |
| 11016 | FamiTicket 日期 | `json.loads("[" + date_keyword + "]")` |
| 16508 | Cityline 日期 | `json.loads("[" + date_keyword + "]")` |
| 17346 | Cityline 區域 | `json.loads("[" + area_keyword + "]")` |
| 17982 | UDN 日期 | `json.loads("[" + date_keyword + "]")` |
| 18066 | UDN 日期2 | `json.loads("[" + date_keyword + "]")` |
| 18176 | UDN 區域 | `json.loads("[" + area_keyword + "]")` |
| 18740 | UDN 排除 | `json.loads("[" + keyword_exclude_str + "]")` |
| 22988 | HKTicketing 區域 | `json.loads("[" + area_keyword_item + "]")` |
| 23921 | HKTicketing 日期 | `json.loads("[" + date_keyword + "]")` |
| 24064 | HKTicketing 區域2 | `json.loads("[" + area_keyword_item + "]")` |

---

## 二、AND/OR 邏輯處理模式比較

### 模式 A：JSON 陣列 + 字串/列表判斷（最常見）

**使用平台**：KKTIX 日期、TicketMaster 日期、TixCraft 日期、Cityline 日期

```python
if isinstance(keyword_item_set, str):
    # OR logic: single keyword
    is_match = normalized_keyword in normalized_session_text
elif isinstance(keyword_item_set, list):
    # AND logic: all keywords must match
    match_results = [kw in normalized_session_text for kw in normalized_keywords]
    is_match = all(match_results)
```

**出現位置**：行 1667-1675、3788-3795、4796-4803、16525-16532

---

### 模式 B：空格分隔 = AND（KKTIX 區域專用）

```python
# Parse area keywords (space-separated = AND logic)
kktix_area_keyword_array = [kw.strip() for kw in kktix_area_keyword.split(' ') if kw.strip()]
is_match_area = all(kw in row_text for kw in kktix_area_keyword_array)
```

**特徵**：
- 輸入格式：`"VIP 搖滾區"` = 2 個 AND 關鍵字
- 僅支援 AND 邏輯（無 OR 選項）
- **獨特設計**：不同於其他平台的 JSON 陣列模式

---

### 模式 C：JSON 陣列 + 空格分隔（TixCraft/UDN 區域）

```python
area_keyword_array = json.loads("[" + area_keyword + "]")

for keyword_index, area_keyword_item in enumerate(area_keyword_array):
    # 空格分隔 = AND
    keyword_parts = area_keyword_item.split(' ')
    is_match = all(kw in row_text for kw in keyword_parts)
```

**特徵**：
- 外層：JSON 陣列分隔多組關鍵字（OR 邏輯）
- 內層：空格分隔單組關鍵字（AND 邏輯）
- 格式：`["VIP 1樓", "搖滾區 站票"]` = 兩組 OR，每組內 AND

---

## 三、不一致性問題

### 3.1 相同邏輯，不同實作方式

| 功能 | 模式 A | 模式 C | 模式 E |
|------|--------|--------|--------|
| **輸入格式** | JSON 字串/列表混合 | JSON 陣列 + 空格分隔 | JSON 陣列 |
| **AND 判斷** | `isinstance(list)` | `split(' ')` | 不支援 |
| **OR 判斷** | 陣列迭代 | 陣列迭代 | 陣列迭代 |
| **代碼行數** | ~30 行 | ~50 行 | ~15 行 |

### 3.2 平台特定的獨特邏輯

**KKTIX 區域（模式 B）**：
- 僅支援空格分隔的 AND 邏輯
- 無法使用多組關鍵字（無 OR 選項）
- 與其他平台差異最大

**TicketMaster 區域（特殊增強）**：
```python
# Enhanced parsing for comma-separated keywords
if len(area_keyword_array) == 1 and isinstance(area_keyword_array[0], str):
    single_keyword = area_keyword_array[0]
    if ',' in single_keyword:
        area_keyword_array = [kw.strip() for kw in single_keyword.split(',')]
```

---

## 四、建議共用函式

### 4.1 `parse_keyword_string_to_array()`

**目的**：統一關鍵字解析邏輯

```python
def parse_keyword_string_to_array(keyword_string):
    """
    將關鍵字字串解析為陣列

    輸入: '"VIP","1樓 搖滾區"'
    輸出: ["VIP", "1樓 搖滾區"]
    """
    if not keyword_string or not keyword_string.strip():
        return []

    try:
        return json.loads("[" + keyword_string + "]")
    except json.JSONDecodeError:
        return [keyword_string.strip()]
```

**替代位置**：25 處 `json.loads("[" + keyword + "]")` 模式

---

### 4.2 `match_keyword_with_text()`

**目的**：統一 AND/OR 邏輯判斷

```python
def match_keyword_with_text(keyword_item, text, match_mode="AND", show_debug=False):
    """
    匹配關鍵字與文字

    Args:
        keyword_item: 單一關鍵字（字串）或關鍵字組（列表/空格分隔）
        text: 待匹配文字
        match_mode: "AND" 或 "OR"

    Returns:
        (is_match, match_details)
    """
    # 處理空格分隔的 AND 邏輯
    if isinstance(keyword_item, str) and ' ' in keyword_item:
        keywords = keyword_item.split(' ')
    elif isinstance(keyword_item, str):
        keywords = [keyword_item]
    elif isinstance(keyword_item, list):
        keywords = keyword_item
    else:
        return False, {}

    normalized_text = format_keyword_string(text)
    match_results = {}

    for kw in keywords:
        formatted_kw = format_keyword_string(kw)
        kw_match = formatted_kw in normalized_text
        match_results[kw] = kw_match

    if match_mode == "AND":
        is_match = all(match_results.values()) if match_results else False
    else:  # OR
        is_match = any(match_results.values()) if match_results else False

    return is_match, match_results
```

**替代位置**：11+ 處重複邏輯

---

### 4.3 `match_keyword_array_with_early_return()`

**目的**：統一早期返回模式（first match wins）

```python
def match_keyword_array_with_early_return(keyword_array, text_list, match_mode="AND", show_debug=False):
    """
    早期返回模式的關鍵字匹配

    Returns:
        (keyword_index, text_index, matched_keyword)
    """
    for keyword_index, keyword_item in enumerate(keyword_array):
        for text_index, text in enumerate(text_list):
            is_match, details = match_keyword_with_text(keyword_item, text, match_mode)
            if is_match:
                return keyword_index, text_index, keyword_item

    return -1, -1, None
```

**替代位置**：KKTIX、TicketMaster、TixCraft、Cityline 等 10+ 處

---

## 五、重構優先級

### 階段 1：核心匹配邏輯抽象（高優先級）

1. 新增 `parse_keyword_string_to_array()` 到 util.py
2. 新增 `match_keyword_with_text()` 到 util.py
3. 新增 `match_keyword_array_with_early_return()` 到 util.py

**預期效益**：
- 消除 30+ 處重複代碼
- 統一 AND/OR 邏輯處理
- 降低未來維護成本

### 階段 2：排除關鍵字增強（中優先級）

改進 `reset_row_text_if_match_keyword_exclude()` 返回值：
- 目前：返回布林值
- 建議：返回 (is_excluded, matched_keyword)

### 階段 3：平台統一（低優先級）

統一 KKTIX 區域關鍵字格式為 JSON 陣列（向後相容考量）
