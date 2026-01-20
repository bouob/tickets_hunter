# util.py 共用函式完整分析

**檔案路徑**：`src/util.py`
**總行數**：約 2442 行
**總函式數**：62 個

---

## 一、函式分類索引

### 1. 關鍵字匹配與選擇邏輯（8 個函式）⭐ 核心

| 函式名稱 | 行號 | 重要性 | 說明 |
|---------|------|--------|------|
| `is_text_match_keyword()` | - | **極高** | 核心匹配函式，支援 AND 邏輯（空格分隔） |
| `get_matched_blocks_by_keyword()` | 1366 | **極高** | 根據關鍵字過濾元素列表 |
| `get_matched_blocks_by_keyword_item_set()` | - | 高 | 單一關鍵字組匹配 |
| `is_row_match_keyword()` | 1426 | 高 | 檢查列文字是否符合關鍵字 |
| `reset_row_text_if_match_keyword_exclude()` | 1460 | 中 | 檢查是否符合排除關鍵字 |
| `get_target_index_by_mode()` | 1342 | **極高** | 根據 mode 計算目標索引（**新增**） |
| `get_target_item_from_matched_list()` | 1341 | **極高** | 從匹配列表中取得目標項目 |
| `t_or_f()` | - | 低 | 字串轉布林值 |

### 2. 字串處理與格式化（12 個函式）

| 函式名稱 | 重要性 | 說明 |
|---------|--------|------|
| `remove_html_tags()` | **高** | 移除 HTML 標籤（頻繁用於區域匹配） |
| `find_between()` | 高 | 提取兩個字串之間的內容 |
| `format_keyword_string()` | **高** | 關鍵字格式化（僅移除全形空格） |
| `format_quota_string()` | 中 | 統一括號符號為【】 |
| `full2half()` | 中 | 全形轉半形 |
| `format_keyword_for_display()` | 高 | JSON → GUI 顯示格式 |
| `format_config_keyword_for_json()` | **高** | GUI 輸入 → JSON 儲存格式 |
| `convert_string_to_pattern()` | 中 | 將字串轉換為正則表達式 |
| `format_question_string()` | 中 | 標準化驗證碼問題文字 |
| `find_continuous_number()` | 中 | 提取連續數字 |
| `find_continuous_text()` | 中 | 提取連續英數字 |
| `find_continuous_pattern()` | 中 | 通用連續字元提取 |

### 3. 驗證碼答案推測（9 個函式）

| 函式名稱 | 重要性 | 說明 |
|---------|--------|------|
| `get_answer_list_from_question_string()` | **高** | 從問題字串推測答案 |
| `get_answer_list_by_question()` | **高** | 綜合猜測答案 |
| `guess_answer_list_from_multi_options()` | 高 | 從多選題猜測答案列表 |
| `guess_answer_list_from_symbols()` | 中 | 從符號格式猜測答案 |
| `guess_answer_list_from_hint()` | 高 | 從提示猜測答案列表 |
| `get_offical_hint_string_from_symbol()` | 中 | 從符號中提取官方提示 |
| `guess_tixcraft_question()` | 高 | TixCraft 特定驗證碼推測 |
| `get_answer_list_from_user_guess_string()` | 中 | 載入使用者自訂答案 |
| `check_answer_keep_symbol()` | 低 | 檢查答案是否需保留符號 |

### 4. 其他類別（簡要）

- **中文數字處理**：5 個函式
- **加解密與安全**：3 個函式（sx, decryptMe, encryptMe）
- **檔案與路徑管理**：5 個函式
- **系統與環境檢測**：3 個函式
- **Discord Webhook**：3 個函式
- **Cloudflare Turnstile**：2 個函式
- **KKTIX 專用**：3 個函式
- **NoDriver 專用**：1 個函式（parse_nodriver_result）

---

## 二、核心函式使用頻率

### 極高頻使用（所有平台核心）

1. **`format_keyword_string()`** - 關鍵字格式化（日期/區域/價格）
2. **`is_text_match_keyword()`** - 關鍵字匹配引擎
3. **`get_target_index_by_mode()`** - 選擇模式邏輯 ⭐ 新增
4. **`remove_html_tags()`** - HTML 清理
5. **`get_app_root()`** - 路徑管理
6. **`parse_nodriver_result()`** - NoDriver 資料解析

### 高頻使用（平台特定）

7. **`get_matched_blocks_by_keyword()`** - 區域/票價過濾
8. **`get_answer_list_from_question_string()`** - 驗證碼推測
9. **`format_config_keyword_for_json()`** - 設定存取
10. **`verify_cf_with_templates()`** - Cloudflare 驗證

---

## 三、主程式中可替換的邏輯

### 3.1 已使用 util 函式但可能未統一的情況

**`reset_row_text_if_match_keyword_exclude()`** - 23 處調用
- 功能單一，返回布林值
- **建議增強**：返回匹配的排除關鍵字（除錯用）

### 3.2 主程式重複實作但 util 已有的邏輯

**問題**：部分平台直接實作選擇模式邏輯，未使用 `get_target_item_from_matched_list()`

**已解決**：透過新增 `get_target_index_by_mode()` 統一 8 處重複代碼

---

## 四、建議新增函式

### 4.1 `parse_keyword_string_to_array(keyword_string)`

**目的**：統一關鍵字解析邏輯（替代 25 處 `json.loads`）

```python
def parse_keyword_string_to_array(keyword_string):
    """
    將關鍵字字串解析為陣列

    輸入: '"VIP","1樓 搖滾區"'
    輸出: ["VIP", ["1樓", "搖滾區"]]
    """
    if not keyword_string or not keyword_string.strip():
        return []

    try:
        keyword_array = json.loads("[" + keyword_string + "]")
        return keyword_array
    except json.JSONDecodeError:
        return [keyword_string.strip()]
```

### 4.2 `match_keyword_with_text(keyword_item, text, match_mode="AND")`

**目的**：統一 AND/OR 邏輯判斷（替代 11+ 處重複邏輯）

```python
def match_keyword_with_text(keyword_item, text, match_mode="AND", show_debug=False):
    """
    匹配關鍵字與文字

    Args:
        keyword_item: 單一關鍵字或關鍵字列表
        text: 待匹配文字
        match_mode: "AND" 或 "OR"
        show_debug: 是否顯示除錯訊息

    Returns:
        (is_match, match_details)
    """
    if isinstance(keyword_item, str):
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
        is_match = all(match_results.values())
    else:  # OR
        is_match = any(match_results.values())

    return is_match, match_results
```

---

## 五、重要常數

```python
CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"

CONST_KEYWORD_DELIMITER = ';'      # 新分隔符（Issue #23）
```

---

## 六、修改風險評估

| 函式 | 影響範圍 | 風險等級 |
|------|---------|---------|
| `is_text_match_keyword()` | 所有平台日期/區域選擇 | **極高** |
| `get_target_index_by_mode()` | 所有選擇邏輯 | **極高** |
| `format_config_keyword_for_json()` | 設定存取 | 高 |
| `parse_nodriver_result()` | NoDriver 平台 | 高 |
| `guess_answer_list_from_*()` | 驗證碼系統 | 中 |
