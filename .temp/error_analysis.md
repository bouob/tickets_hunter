# 「'list' object has no attribute 'get'」錯誤分析報告

## 問題根源

在 FamiTicket 的日期選擇和區域選擇流程中，存在**類型不匹配**問題：

### 1. FamiTicket 日期選擇（nodriver_tixcraft.py 第 17279-17282 行）

```python
# formated_area_list 中存儲的是字典，不是 DOM 元素
formated_area_list.append({
    "idx": idx,
    "text": row_text
})
```

**預期的調用流程：**
- `nodriver_tixcraft.py:17303` 調用 `util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)`
- 返回一個字典: `{"idx": idx, "text": row_text}`
- 然後在 17313-17315 行正確調用 `.get("idx")` 和 `.get("text", "")`

### 2. 但在 util.py 中的問題

`util.py:1366-1378` 中的 `get_matched_blocks_by_keyword()` 函數調用了：

```python
matched_blocks = get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, 
                                                        keyword_item_set, formated_area_list)
```

然後在 `util.py:1289-1339` 中的 `get_matched_blocks_by_keyword_item_set()` 函數存在問題：

```python
# 第 1302 行 - 錯誤！formated_area_list 中的 row 是字典，不是 DOM 元素
row_html = row.get_attribute('innerHTML')  # ❌ 字典沒有 .get_attribute() 方法
```

這是**舊代碼遺留**，原本是為了處理 DOM 元素，但在 FamiTicket 日期選擇中被傳入了字典列表。

### 3. FamiTicket 區域選擇（nodriver_tixcraft.py 第 17479-17489 行）

相同的問題也出現在區域選擇中：

```python
for area_item in formated_area_list:
    area_text = area_item.get("text", "")  # ✅ 這裡正確地假設 area_item 是字典
```

然後調用：

```python
matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, 
                                                    date_keyword, formated_area_list)
```

同樣的 `util.py:1302` 會出錯。

---

## 錯誤在哪裡出現

**具體位置：**
- **文件:** `src/util.py`
- **函數:** `get_matched_blocks_by_keyword_item_set()`
- **行號:** 1302
- **代碼:** `row_html = row.get_attribute('innerHTML')`

**錯誤場景：**
當以下條件同時滿足時：
1. 從 `nodriver_fami_date_auto_select()` 或 `nodriver_fami_area_auto_select()` 調用
2. 傳入的 `formated_area_list` 包含字典元素（`{"idx": ..., "text": ...}`）
3. 並且 `date_keyword` 或 `area_keyword_item` 不為空（會觸發關鍵字匹配）
4. 進入 `util.get_matched_blocks_by_keyword()` → `get_matched_blocks_by_keyword_item_set()`
5. 嘗試調用 `row.get_attribute()` 在字典上 → 報錯

---

## 呼叫堆疊分析

### FamiTicket 日期選擇堆疊

```
nodriver_tixcraft.py:17297
├─ util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)
│  └─ util.get_matched_blocks_by_keyword_item_set(..., formated_area_list)  [第 1375 行]
│     └─ row.get_attribute('innerHTML')  [第 1302 行] ❌ ERROR: 'dict' object has no attribute 'get_attribute'
```

### FamiTicket 區域選擇堆疊

```
nodriver_tixcraft.py:17506
├─ util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, area_keyword_item, formated_area_list)
│  └─ util.get_matched_blocks_by_keyword_item_set(..., formated_area_list)  [第 1375 行]
│     └─ row.get_attribute('innerHTML')  [第 1302 行] ❌ ERROR
```

---

## 相關代碼位置清單

### 主要調用位置

| 文件 | 行號 | 函數 | 說明 |
|------|------|------|------|
| nodriver_tixcraft.py | 17279-17282 | nodriver_fami_date_auto_select | 建立字典格式的 formated_area_list |
| nodriver_tixcraft.py | 17297 | nodriver_fami_date_auto_select | 調用 util.get_matched_blocks_by_keyword |
| nodriver_tixcraft.py | 17303 | nodriver_fami_date_auto_select | 調用 util.get_target_item_from_matched_list |
| nodriver_tixcraft.py | 17313-17315 | nodriver_fami_date_auto_select | 正確地在字典上調用 .get() |
| nodriver_tixcraft.py | 17487-17489 | nodriver_fami_area_auto_select | 遍歷字典格式的 formated_area_list |
| nodriver_tixcraft.py | 17506 | nodriver_fami_area_auto_select | 調用 util.get_matched_blocks_by_keyword |
| nodriver_tixcraft.py | 17508 | nodriver_fami_area_auto_select | 調用 util.get_target_item_from_matched_list |
| nodriver_tixcraft.py | 17522-17523 | nodriver_fami_area_auto_select | 正確地在字典上調用 .get() |

### 有問題的函數定義

| 文件 | 行號 | 函數 | 問題 |
|------|------|------|------|
| util.py | 1289-1339 | get_matched_blocks_by_keyword_item_set | 第 1302 行嘗試在字典上調用 .get_attribute() |
| util.py | 1366-1378 | get_matched_blocks_by_keyword | 調用有問題的函數 |
| util.py | 1341-1363 | get_target_item_from_matched_list | 從列表中選擇元素（本身沒問題） |

---

## CLICK 函數相關問題

除了上述主要問題，在 `nodriver_tixcraft.py` 的 CLICK 函數中還有另一個潛在問題：

**第 8074 行（click_button_via_javascript 函數）:**

```python
const targetClasses = "{target_button.get('classes', '')}";
```

❌ 這個 f-string 在 Python 代碼中，如果 `target_button` 是列表而不是字典，會報錯：
`'list' object has no attribute 'get'`

但這個函數（`click_button_via_cdp`、`click_button_via_javascript` 等）目前在代碼中**未被使用**（沒有找到調用點）。

---

## 修復建議

### 方案 A：修改 util.py 以支持字典（推薦）

修改 `get_matched_blocks_by_keyword_item_set()` 函數，添加類型檢查：

```python
def get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, keyword_item_set, formated_area_list):
    matched_blocks = []
    for row in formated_area_list:
        row_text = ""
        
        # 檢查 row 是字典還是 DOM 元素
        if isinstance(row, dict):
            # 新格式：字典 (FamiTicket 使用)
            row_text = row.get("text", "")
        else:
            # 舊格式：DOM 元素
            try:
                row_html = row.get_attribute('innerHTML')
                row_text = remove_html_tags(row_html)
            except Exception as exc:
                break
        
        # ... 後續邏輯保持不變
```

### 方案 B：將 FamiTicket 的 formated_area_list 改為存儲元素

改變 nodriver_tixcraft.py 第 17279-17282 行，存儲元素而不是字典。

**缺點：** 會改變現有的設計和測試邏輯。

---

## 驗證清單

- [ ] 在 FamiTicket 日期選擇中測試，確保有關鍵字匹配時不出錯
- [ ] 在 FamiTicket 區域選擇中測試，確保有關鍵字匹配時不出錯
- [ ] 測試 `get_target_item_from_matched_list()` 返回的是字典時能正確調用 `.get()`
- [ ] 檢查其他平台的相同函數是否也存在類似問題

