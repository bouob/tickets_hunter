# Stage 4: 日期選擇機制

## 概述

**目的**：從可用日期列表中選擇目標演出日期
**輸入**：日期關鍵字（支援 AND/OR 邏輯）+ 選擇模式
**輸出**：選定的日期 + 點擊購票按鈕
**關鍵技術**：
- **Early Return Pattern**（早期返回模式）：優先級驅動的關鍵字匹配
- **Conditional Fallback**（條件回退）：智能回退機制
- **Shadow DOM Penetration**（Shadow DOM 穿透）：處理 closed Shadow DOM

---

## 核心流程（標準模式）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 取得所有可用日期列表                                      │
│    ├─ 標準 DOM 查詢（TixCraft, KKTIX, TicketPlus, KHAM）    │
│    └─ DOMSnapshot 平坦化（iBon - closed Shadow DOM）        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 過濾不可用選項                                           │
│    ├─ 售罄選項（pass_date_is_sold_out）                    │
│    ├─ Disabled 按鈕                                         │
│    └─ 排除關鍵字（keyword_exclude）                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 關鍵字優先匹配（Early Return Pattern）                   │
│    ├─ 嘗試關鍵字 #1 → 成功？[是] → 立即停止 ✓              │
│    ├─ 嘗試關鍵字 #2 → 成功？[是] → 立即停止 ✓              │
│    ├─ 嘗試關鍵字 #3 → 成功？[是] → 立即停止 ✓              │
│    └─ 所有關鍵字失敗 → 觸發條件回退 ↓                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 條件回退機制（Feature 003）                              │
│    ├─ [date_auto_fallback = true]  → 使用 auto_select_mode │
│    │   ├─ "from top to bottom" → 選第一個                  │
│    │   ├─ "from bottom to top" → 選最後一個                │
│    │   ├─ "center" → 選中間                                │
│    │   └─ "random" → 隨機選擇                              │
│    └─ [date_auto_fallback = false] → 等待手動介入（嚴格模式）│
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 點擊目標日期按鈕                                          │
│    ├─ NoDriver: CDP dispatchMouseEvent                      │
│    ├─ NoDriver fallback: JavaScript click()                 │
│    └─ Chrome: element.click()                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 關鍵程式碼片段

### 1. Early Return Pattern（關鍵字優先匹配）

**範例來源**：TixCraft (`nodriver_tixcraft.py:2759-2807`)

```python
# Feature 003: Early return pattern - iterate keywords in priority order
matched_blocks = []
target_row_found = False
keyword_matched_index = -1

try:
    import json
    import re
    keyword_array = json.loads("[" + date_keyword + "]")

    # T005: Start checking keywords log
    if show_debug_message:
        print(f"[DATE KEYWORD] Start checking keywords in order: {keyword_array}")
        print(f"[DATE KEYWORD] Total keyword groups: {len(keyword_array)}")

    # NEW: Iterate keywords in priority order (early return)
    for keyword_index, keyword_item_set in enumerate(keyword_array):
        if show_debug_message:
            print(f"[DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

        # Check all rows for this keyword
        for i, row_text in enumerate(formated_area_list_text):
            normalized_row_text = re.sub(r'\s+', ' ', row_text)
            is_match = False

            if isinstance(keyword_item_set, str):
                # OR logic: single keyword
                normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
                is_match = normalized_keyword in normalized_row_text
            elif isinstance(keyword_item_set, list):
                # AND logic: all keywords must match
                normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
                match_results = [kw in normalized_row_text for kw in normalized_keywords]
                is_match = all(match_results)

            if is_match:
                # T006: Keyword matched - IMMEDIATELY select and stop
                matched_blocks = [formated_area_list[i]]
                target_row_found = True
                keyword_matched_index = keyword_index
                if show_debug_message:
                    print(f"[DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                    print(f"[DATE SELECT] Selected date: {row_text[:80]} (keyword match)")
                break  # ⭐ Early Return - 立即停止檢查其他行

        if target_row_found:
            # EARLY RETURN: Stop checking further keywords
            break  # ⭐ Early Return - 立即停止嘗試後續關鍵字

    # T007: All keywords failed log
    if not target_row_found:
        if show_debug_message:
            print(f"[DATE KEYWORD] All keywords failed to match")

except Exception as e:
    if show_debug_message:
        print(f"[DATE KEYWORD] Parsing error: {e}")
    matched_blocks = []
```

**關鍵設計理念**：
- 關鍵字按優先級排列（第 1 個最優先）
- 一旦匹配成功，**立即停止**，不再嘗試後續關鍵字
- 避免「掃描所有關鍵字再選擇」的舊邏輯
- **T005-T007 標記**：TixCraft 的完整除錯日誌實作

---

### 2. 條件回退機制（Feature 003）

**範例來源**：TixCraft (`nodriver_tixcraft.py:2863-2876`)

```python
# T018-T020: NEW - Conditional fallback based on date_auto_fallback switch
if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and \
   formated_area_list is not None and len(formated_area_list) > 0:
    if date_auto_fallback:
        # T018: Fallback enabled - use auto_select_mode
        if show_debug_message:
            print(f"[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            print(f"[DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
        matched_blocks = formated_area_list  # 使用所有可用選項
    else:
        # T019: Fallback disabled - strict mode (do not select anything)
        if show_debug_message:
            print(f"[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            print(f"[DATE SELECT] Waiting for manual intervention")
        return False  # 嚴格模式：不選擇，返回失敗，等待手動介入

# T020: Handle case when formated_area_list is empty or None (all options excluded)
if formated_area_list is None or len(formated_area_list) == 0:
    if show_debug_message:
        print(f"[DATE FALLBACK] No available options after exclusion")
    return False
```

**設計決策**：
- **預設值**：`date_auto_fallback = false`（嚴格模式）
- **嚴格模式**（false）：關鍵字失敗時**不自動選擇**，避免誤購不想要的場次
- **自動模式**（true）：關鍵字失敗時，回退到 `auto_select_mode` 選擇可用選項

---

### 3. AND/OR 邏輯支援

**設定格式**：
```json
{
  "date_auto_select": {
    "date_keyword": "\"10/03\",\"10/04\",\"10/05\""  // OR 邏輯（逗號分隔）
  }
}
```

**AND 邏輯範例**（空格分隔）：
```json
{
  "date_auto_select": {
    "date_keyword": "\"10/03 週六\",\"10/04 週日\""  // "10/03" AND "週六"
  }
}
```

**關鍵字解析**（`implementation-guide.md` 標準）：
```python
# Parse keywords - support multiple formats:
# 1. "keyword1,keyword2,keyword3" (with outer quotes)
# 2. keyword1,keyword2,keyword3 (without quotes)
# 3. "\"keyword1\",\"keyword2\"" (JSON array format)

import json
keyword_array = json.loads("[" + date_keyword + "]")

# Example results:
# Input: "\"10/03\",\"10/04\",\"10/05\""
# Output: ["10/03", "10/04", "10/05"]  # OR logic

# Input: "\"10/03 週六\",\"10/04 週日\""
# Output: [["10/03", "週六"], ["10/04", "週日"]]  # AND logic within each
```

---

### 4. Shadow DOM 穿透（iBon 專用）

**範例來源**：iBon (`nodriver_tixcraft.py:5860-6142`)

```python
async def nodriver_ibon_date_auto_select(tab, config_dict):
    """
    使用 DOMSnapshot 平坦化策略穿透 closed Shadow DOM
    """
    # Step 1: Capture DOM snapshot (flattens Shadow DOM)
    dom_snapshot_result = await tab.send(nodriver.cdp.dom_snapshot.capture_snapshot(
        computed_styles=[]
    ))

    # Step 2: Parse flattened document
    documents = dom_snapshot_result[0]  # DocumentSnapshot list
    strings = dom_snapshot_result[1]    # String table

    # Step 3: Find date buttons using flattened DOM
    for doc in documents:
        layout = doc.layout
        for idx, node_id in enumerate(layout.node_index):
            # Extract node attributes from flattened structure
            node_name = strings[layout.styles[idx][0]] if layout.styles else None

            if node_name and 'date-button' in node_name:
                # Found date button in closed Shadow DOM
                backend_node_id = layout.backend_node_id[idx]
                # Click using CDP...
```

**為什麼需要 DOMSnapshot？**
- iBon 使用 **closed Shadow DOM**（`shadowRoot.mode = 'closed'`）
- 標準 DOM API 無法訪問
- DOMSnapshot 將 Shadow DOM **平坦化**為單一文檔結構
- 可直接查詢和操作 Shadow DOM 內部元素

---

## 平台實作差異

| 平台 | 選擇器類型 | Shadow DOM | 特殊處理 | 函數名稱 | 完成度 |
|------|-----------|-----------|---------|---------|--------|
| **KKTIX** | Table rows | ❌ 無 | 支援 register_status 區域 | `nodriver_kktix_presale_home()` | 100% ✅ |
| **TixCraft** | Button list | ❌ 無 | 檢查 `data-href` 屬性 | `nodriver_tixcraft_date_auto_select()` | 95% ⚠️ |
| **iBon** | Button list | ✅ Closed | **DOMSnapshot 平坦化**策略 | `nodriver_ibon_date_auto_select()` | 100% ✅ |
| **TicketPlus** | Expansion panel | ❌ 無 | 需先展開 date 面板 | `nodriver_ticketplus_date_auto_select()` | 100% ✅ |
| **KHAM** | Table rows | ❌ 無 | 支援 3 域名變體 (kham/ticket/udn) | `nodriver_kham_date_auto_select()` | 100% ✅ |

**程式碼位置**（`nodriver_tixcraft.py`）：
- **TixCraft**: Line 2660 (`nodriver_tixcraft_date_auto_select`, 主要參考範例) ⭐
- KKTIX: Line ~700-900 (`nodriver_kktix_presale_home`)
- iBon: Line 5860 (282 行，Shadow DOM 最複雜範例)
- TicketPlus: Line 2210 (`nodriver_ticketplus_date_auto_select`)
- KHAM: Line 12200-12462 (`nodriver_kham_date_auto_select`)

---

## 實作檢查清單

- [ ] **關鍵字邏輯**
  - [ ] 支援 AND 邏輯（空格分隔）
  - [ ] 支援 OR 邏輯（逗號/分號分隔）
  - [ ] 實作 Early Return Pattern
  - [ ] 關鍵字優先級遞減匹配

- [ ] **條件回退機制（Feature 003）**
  - [ ] 實作 `date_auto_fallback` 開關
  - [ ] 嚴格模式（false）：不自動選擇
  - [ ] 自動模式（true）：回退到 `auto_select_mode`

- [ ] **過濾機制**
  - [ ] 過濾已售罄選項（`pass_date_is_sold_out`）
  - [ ] 過濾 disabled 按鈕
  - [ ] 套用排除關鍵字（`keyword_exclude`）

- [ ] **選擇模式支援**
  - [ ] `from top to bottom`（從第一個）
  - [ ] `from bottom to top`（從最後一個）
  - [ ] `center`（中間）
  - [ ] `random`（隨機）

- [ ] **除錯輸出**
  - [ ] Verbose 模式除錯訊息
  - [ ] 關鍵字匹配日誌
  - [ ] 回退觸發日誌

- [ ] **錯誤處理**
  - [ ] 無可用日期時的處理
  - [ ] 點擊失敗時的重試機制
  - [ ] 異常捕獲與日誌

---

## 常見問題 (FAQ)

### Q1: 為什麼需要 Early Return Pattern？

**A**: 確保**優先級較高的關鍵字先被匹配**。

**舊邏輯問題**（已棄用）：
```python
# ❌ 舊邏輯：掃描所有關鍵字，收集所有匹配，再選一個
for keyword in ["10/03", "10/04", "10/05"]:
    if keyword matches:
        matched_list.append(...)  # 可能同時匹配多個
# 最後從 matched_list 選一個（無法保證優先級）
```

**新邏輯優勢**：
```python
# ✅ 新邏輯：依序嘗試，第一個成功立即停止
for keyword in ["10/03", "10/04", "10/05"]:
    if keyword matches:
        select_immediately()
        break  # 立即停止，不嘗試後續關鍵字
```

**實務案例**：
- 使用者設定：`"\"10/03 週六\",\"10/04 週日\",\"任意日期\""`
- 期望：優先選 10/03，其次 10/04，最後才考慮其他
- Early Return 確保：一旦 10/03 可用，立即選擇，不會因為「任意日期」匹配更多而選錯

---

### Q2: 條件回退什麼時候觸發？

**A**: 當**所有關鍵字都無法匹配**時，根據 `date_auto_fallback` 設定決定行為。

**觸發條件**：
```python
if matched_blocks is None or len(matched_blocks) == 0:
    if len(date_keyword) > 0:
        # 有設定關鍵字，但都沒匹配 → 觸發條件回退
```

**行為**：
1. **`date_auto_fallback = false`（預設）**：
   - 返回 `False`
   - 不選擇任何日期
   - 等待使用者手動介入
   - **用途**：避免誤購不想要的場次

2. **`date_auto_fallback = true`**：
   - 使用 `auto_select_mode` 從可用選項中選擇
   - 自動完成購票流程
   - **用途**：「只要能買到票就好」的場景

---

### Q3: 如何處理 closed Shadow DOM（iBon）？

**A**: 使用 **DOMSnapshot API** 將 Shadow DOM 平坦化。

**問題**：
- iBon 使用 `closed` Shadow DOM
- 標準 API 無法訪問：`element.shadowRoot === null`

**解決方案**：
```python
# Step 1: Capture DOM snapshot (includes Shadow DOM)
dom_snapshot = await tab.send(nodriver.cdp.dom_snapshot.capture_snapshot())

# Step 2: Shadow DOM is now "flattened" into documents structure
documents = dom_snapshot[0]
strings = dom_snapshot[1]  # String table for attribute values

# Step 3: Search flattened structure for elements
for doc in documents:
    for node in doc.layout.node_index:
        # Can now access elements inside closed Shadow DOM
```

**優勢**：
- 一次性獲取整個 DOM 結構（包括所有 Shadow DOM）
- 不需要逐層打開 Shadow Root
- 支援 `closed` 模式的 Shadow DOM

---

### Q4: 關鍵字格式如何設定？

**A**: 支援多種格式，統一由關鍵字解析邏輯處理。

**格式 1：JSON 陣列格式（推薦）**
```json
{
  "date_keyword": "\"10/03\",\"10/04\",\"10/05\""
}
```

**格式 2：不帶引號（兼容舊版）**
```json
{
  "date_keyword": "10/03,10/04,10/05"
}
```

**格式 3：AND 邏輯（空格分隔）**
```json
{
  "date_keyword": "\"10/03 週六\",\"10/04 週日\""
}
```
解析後：`[["10/03", "週六"], ["10/04", "週日"]]`

**解析邏輯**（見 `implementation-guide.md`）：
```python
import json

# Remove outer quotes if present
keyword_clean = date_keyword.strip()
if keyword_clean.startswith('"') and keyword_clean.endswith('"'):
    keyword_clean = keyword_clean[1:-1]

# Parse as JSON array
keyword_array = [
    kw.strip().strip('"').strip("'")
    for kw in keyword_clean.split(',')
    if kw.strip()
]

# Support AND logic (space-separated within keyword)
for i, kw in enumerate(keyword_array):
    if ' ' in kw:
        keyword_array[i] = kw.split()  # Convert to list for AND logic
```

---

## 相關文件

- 📋 [Feature 003: Keyword Priority Fallback](../../specs/003-keyword-priority-fallback/implementation-guide.md) - 完整實作指南
- 📊 [規格驗證矩陣](../04-validation/spec-validation-matrix.md) - FR-017, FR-018, FR-019
- 🔧 [KKTIX 參考實作](../03-implementation/platform-examples/kktix-reference.md)
- 🔧 [iBon 參考實作](../03-implementation/platform-examples/ibon-reference.md) - Shadow DOM 範例
- 📖 [12-Stage 標準](../02-development/ticket_automation_standard.md) - 完整 12 階段流程
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 函數位置索引

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本日期選擇邏輯 |
| v1.1 | 2025-10 | 新增 AND/OR 邏輯支援 |
| **v1.2** | **2025-11** | **Feature 003: Early Return + Conditional Fallback** |

**v1.2 重大變更**：
- ✅ 實作 Early Return Pattern（優先級驅動）
- ✅ 實作條件回退機制（`date_auto_fallback` 開關）
- ✅ 預設改為嚴格模式（避免誤購）
- ✅ 統一所有平台的關鍵字解析邏輯
