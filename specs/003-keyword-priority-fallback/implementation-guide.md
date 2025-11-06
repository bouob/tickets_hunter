# 實作指南 (Implementation Guide)
## 功能 003：關鍵字優先匹配與條件式遞補

**版本**: 1.0
**建立日期**: 2025-10-31
**目標受眾**: 開發者、維護者

---

## 📋 目錄

1. [概述](#概述)
2. [已完成示範：TixCraft 日期選擇](#已完成示範tixcraft-日期選擇)
3. [實作模式總結](#實作模式總結)
4. [TixCraft 區域選擇實作指南](#tixcraft-區域選擇實作指南)
5. [其他平台遷移指南](#其他平台遷移指南)
6. [UI 實作指南](#ui-實作指南)
7. [測試程序](#測試程序)
8. [常見問題](#常見問題)

---

## 概述

### 功能目標
實作「早期返回模式」與「條件式遞補」兩大核心機制：
- **早期返回模式**: 第一個關鍵字匹配成功時立即停止檢查後續關鍵字（節省約 30% 檢查時間）
- **條件式遞補**: 透過布林開關控制當所有關鍵字失敗時的行為（嚴格模式 vs 自動遞補）

### 核心設計原則
1. **嚴格模式預設** (`false`): 避免誤購不想要的票券
2. **向後相容**: 使用 `.get()` 安全存取新欄位
3. **程式碼保留**: 舊版邏輯保留於註解區塊（2 週回滾期）
4. **結構化日誌**: 英文日誌避免 Windows cp950 編碼問題
5. **防禦性程式設計**: 主開關檢查於函數入口

### 已完成工作
- ✅ **T001-T002**: 配置檔案擴充（`settings.py`, `settings_old.py`）
- ✅ **T003-T009**: TixCraft 日期選擇早期返回邏輯（示範實作）
- ✅ **T017-T020**: TixCraft 日期選擇條件式遞補邏輯（示範實作）
- ✅ **T010-T016**: TixCraft 區域選擇早期返回邏輯
- ✅ **T021-T024**: TixCraft 區域選擇條件式遞補邏輯
- ✅ **T025-T035**: UI 控制項（Web + Desktop）

### 待辦工作
- 🔲 其他平台（KKTIX, iBon, TicketPlus, KHAM, FamiTicket）
- 🔲 **T036-T040**: 測試與文件更新

---

## 已完成示範：TixCraft 日期選擇

### 檔案位置
`src/nodriver_tixcraft.py` → 函數 `nodriver_tixcraft_date_auto_select`

### 關鍵修改點

#### 1. 主開關檢查（防禦性程式設計）
```python
# T003: Check main switch (defensive programming)
if not config_dict["date_auto_select"]["enable"]:
    if show_debug_message:
        print("[DATE SELECT] Main switch is disabled, skipping date selection")
    return False
```

#### 2. 安全存取新欄位（向後相容）
```python
# T017: Safe access for new field
date_auto_fallback = config_dict.get('date_auto_fallback', False)
```

#### 3. 早期返回模式（核心邏輯）
```python
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
            # T006: Keyword matched log - IMMEDIATELY select and stop
            matched_blocks = [formated_area_list[i]]
            target_row_found = True
            keyword_matched_index = keyword_index
            if show_debug_message:
                print(f"[DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                print(f"[DATE SELECT] Selected date: {row_text[:80]} (keyword match)")
            break

    if target_row_found:
        # EARLY RETURN: Stop checking further keywords
        break

# T007: All keywords failed log
if not target_row_found:
    if show_debug_message:
        print(f"[DATE KEYWORD] All keywords failed to match")
```

#### 4. 條件式遞補邏輯
```python
# T018-T020: NEW - Conditional fallback based on date_auto_fallback switch
# IMPORTANT: Check for None first to avoid TypeError when no options available
if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and formated_area_list is not None and len(formated_area_list) > 0:
    if date_auto_fallback:
        # T018: Fallback enabled - use auto_select_mode
        if show_debug_message:
            print(f"[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            print(f"[DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
        matched_blocks = formated_area_list
    else:
        # T019: Fallback disabled - strict mode (do not select anything)
        if show_debug_message:
            print(f"[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            print(f"[DATE SELECT] Waiting for manual intervention")
        return False  # Return immediately without selection

# T020: Handle case when formated_area_list is empty or None (all options excluded)
if formated_area_list is None or len(formated_area_list) == 0:
    if show_debug_message:
        print(f"[DATE FALLBACK] No available options after exclusion")
    return False
```

#### 5. 舊版程式碼保留（回滾支援）
```python
# DEPRECATED (T008): Old logic - scan all keywords and collect matches
# Will be removed after 2 weeks (2025-11-14)
"""
# OLD LOGIC - DEPRECATED - DO NOT USE
# This logic scanned ALL keywords and collected all matches, then selected one
# NEW logic (above) uses early return: first match wins immediately
[... 完整舊版邏輯保留於此 ...]
"""
```

---

## 實作模式總結

### 五步驟實作模式（適用於所有函數）

#### Step 1: 主開關檢查（入口防禦）
```python
# Check main switch at function entry
if not config_dict["<feature>_auto_select"]["enable"]:
    if show_debug_message:
        print("[<PREFIX> SELECT] Main switch is disabled, skipping selection")
    return False
```

#### Step 2: 安全存取新欄位（向後相容）
```python
# Safe access for new config field (backward compatibility)
<feature>_auto_fallback = config_dict.get('<feature>_auto_fallback', False)
```

#### Step 3: 早期返回模式（優先匹配）
```python
# Iterate keywords in priority order (early return on first match)
for keyword_index, keyword_item_set in enumerate(keyword_array):
    if show_debug_message:
        print(f"[<PREFIX> KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

    for i, row_text in enumerate(<list_text>):
        normalized_row_text = re.sub(r'\s+', ' ', row_text)
        is_match = False

        if isinstance(keyword_item_set, str):
            # OR logic
            normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
            is_match = normalized_keyword in normalized_row_text
        elif isinstance(keyword_item_set, list):
            # AND logic
            normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
            match_results = [kw in normalized_row_text for kw in normalized_keywords]
            is_match = all(match_results)

        if is_match:
            matched_blocks = [<original_list>[i]]
            target_row_found = True
            keyword_matched_index = keyword_index
            if show_debug_message:
                print(f"[<PREFIX> KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                print(f"[<PREFIX> SELECT] Selected item: {row_text[:80]}")
            break

    if target_row_found:
        # EARLY RETURN: Stop checking further keywords
        break

# Log when all keywords fail
if not target_row_found:
    if show_debug_message:
        print(f"[<PREFIX> KEYWORD] All keywords failed to match")
```

#### Step 4: 條件式遞補邏輯
```python
# Conditional fallback based on <feature>_auto_fallback switch
# IMPORTANT: Check for None first to avoid TypeError when no options available
if matched_blocks is not None and len(matched_blocks) == 0 and <keyword> and <available_list> is not None and len(<available_list>) > 0:
    if <feature>_auto_fallback:
        # Fallback enabled
        if show_debug_message:
            print(f"[<PREFIX> FALLBACK] <feature>_auto_fallback=true, triggering auto fallback")
            print(f"[<PREFIX> FALLBACK] Selecting based on <select_order>='{auto_select_mode}'")
        matched_blocks = <available_list>
    else:
        # Fallback disabled (strict mode)
        if show_debug_message:
            print(f"[<PREFIX> FALLBACK] <feature>_auto_fallback=false, fallback is disabled")
            print(f"[<PREFIX> SELECT] Waiting for manual intervention")
        return False

# Handle empty or None available list
if <available_list> is None or len(<available_list>) == 0:
    if show_debug_message:
        print(f"[<PREFIX> FALLBACK] No available options after exclusion")
    return False
```

#### Step 5: 保留舊版邏輯（DEPRECATED 註解）
```python
# DEPRECATED (T008): Old logic - [brief description]
# Will be removed after 2 weeks (YYYY-MM-DD)
"""
# OLD LOGIC - DEPRECATED - DO NOT USE
[... 完整複製舊版邏輯到此處 ...]
"""
```

### 日誌訊息標準前綴
| 功能類型 | 日期選擇 | 區域選擇 | 票價選擇 |
|---------|---------|---------|---------|
| 關鍵字檢查 | `[DATE KEYWORD]` | `[AREA KEYWORD]` | `[PRICE KEYWORD]` |
| 選擇行為 | `[DATE SELECT]` | `[AREA SELECT]` | `[PRICE SELECT]` |
| 遞補行為 | `[DATE FALLBACK]` | `[AREA FALLBACK]` | `[PRICE FALLBACK]` |

---

## TixCraft 區域選擇實作指南

### 目標函數
`src/nodriver_tixcraft.py` → 函數 `nodriver_tixcraft_area_auto_select`

### 任務清單
- **T010**: 主開關檢查
- **T011**: 安全存取 `area_auto_fallback`
- **T012**: 實作早期返回模式
- **T013-T015**: 結構化日誌（關鍵字檢查、匹配成功、全部失敗）
- **T016**: 保留舊版邏輯於 DEPRECATED 註解
- **T021**: 安全存取欄位（重複 T011，可合併）
- **T022-T024**: 條件式遞補邏輯

### 實作步驟

#### 步驟 1: 定位函數
```bash
# 使用 Grep 工具搜尋函數定義
grep "def nodriver_tixcraft_area_auto_select" src/nodriver_tixcraft.py -n
```

#### 步驟 2: 閱讀現有邏輯
```bash
# 讀取函數完整內容（假設從第 X 行開始）
# 使用 Read 工具並指定 offset 和 limit
```

**關鍵變數映射**（與日期選擇對照）：
| 日期選擇變數 | 區域選擇變數 | 說明 |
|-------------|-------------|------|
| `formated_area_list` | `area_list` | 可用選項列表 |
| `formated_area_list_text` | `area_list_text` | 選項文字列表（用於匹配） |
| `date_keyword` | `area_keyword` | 關鍵字字串 |
| `date_auto_fallback` | `area_auto_fallback` | 遞補開關 |
| `date_select_order` | `area_select_order` | 選擇順序（random/from_top/from_bottom） |
| `[DATE KEYWORD]` | `[AREA KEYWORD]` | 日誌前綴 |

#### 步驟 3: 應用五步驟模式

**T010: 主開關檢查**（參考日期選擇 T003）
```python
# T010: Check main switch (defensive programming)
if not config_dict.get("area_auto_select", {}).get("enable", False):
    if show_debug_message:
        print("[AREA SELECT] Main switch is disabled, skipping area selection")
    return False
```

**T011: 安全存取新欄位**（參考日期選擇 T017）
```python
# T011: Safe access for new field
area_auto_fallback = config_dict.get('area_auto_fallback', False)
```

**T012-T015: 早期返回模式 + 結構化日誌**（參考日期選擇 T004-T007）
```python
# T012: Implement early return pattern
# T013: Log when checking keywords
# T014: Log when keyword matches
# T015: Log when all keywords fail

# NEW: Iterate keywords in priority order (early return)
for keyword_index, keyword_item_set in enumerate(keyword_array):
    if show_debug_message:
        print(f"[AREA KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

    # Check all rows for this keyword
    for i, row_text in enumerate(area_list_text):
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
            # T014: Keyword matched log - IMMEDIATELY select and stop
            matched_blocks = [area_list[i]]
            area_target_row_found = True  # 注意：區域選擇可能使用不同變數名
            if show_debug_message:
                print(f"[AREA KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                print(f"[AREA SELECT] Selected area: {row_text[:80]} (keyword match)")
            break

    if area_target_row_found:
        # EARLY RETURN: Stop checking further keywords
        break

# T015: All keywords failed log
if not area_target_row_found:
    if show_debug_message:
        print(f"[AREA KEYWORD] All keywords failed to match")
```

**T016: 保留舊版邏輯**（參考日期選擇 T008）
```python
# DEPRECATED (T016): Old logic - scan all keywords and collect matches
# Will be removed after 2 weeks (2025-11-14)
"""
# OLD LOGIC - DEPRECATED - DO NOT USE
# [... 將現有的關鍵字匹配邏輯完整複製到此處 ...]
"""
```

**T021-T024: 條件式遞補邏輯**（參考日期選擇 T017-T020）
```python
# T021: Safe access (if not already done in T011)
# T022-T024: Conditional fallback based on area_auto_fallback switch

if len(matched_blocks) == 0 and area_keyword and area_list and len(area_list) > 0:
    if area_auto_fallback:
        # T022: Fallback enabled - use area_select_order
        if show_debug_message:
            print(f"[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
            print(f"[AREA FALLBACK] Selecting available area based on area_select_order='{area_select_order}'")
        matched_blocks = area_list
    else:
        # T023: Fallback disabled - strict mode (do not select anything)
        if show_debug_message:
            print(f"[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            print(f"[AREA SELECT] Waiting for manual intervention")
        return False  # Return immediately without selection

# T024: Handle case when area_list is empty (all options excluded)
if not area_list or len(area_list) == 0:
    if show_debug_message:
        print(f"[AREA FALLBACK] No available options after exclusion")
    return False
```

#### 步驟 4: 驗證修改
```python
# 檢查修改後的函數是否：
# 1. 保留了所有原始功能（排除邏輯、隨機選擇等）
# 2. 正確處理 async/await 語法
# 3. 日誌前綴統一使用 [AREA KEYWORD], [AREA SELECT], [AREA FALLBACK]
# 4. 變數名稱與原函數一致（area_target_row_found 等）
```

---

## 其他平台遷移指南

### 平台函數對照表

| 平台 | 檔案 | 日期選擇函數 | 區域選擇函數 |
|------|------|-------------|-------------|
| TixCraft | `nodriver_tixcraft.py` | `nodriver_tixcraft_date_auto_select` | `nodriver_tixcraft_area_auto_select` |
| KKTIX | `nodriver_kktix.py` | `nodriver_kktix_date_auto_select` | `nodriver_kktix_area_auto_select` |
| iBon | `nodriver_ibon.py` | `nodriver_ibon_date_auto_select` | `nodriver_ibon_area_auto_select` |
| TicketPlus | `nodriver_ticketplus.py` | `nodriver_ticketplus_date_auto_select` | `nodriver_ticketplus_area_auto_select` |
| KHAM | `nodriver_kham.py` | `nodriver_kham_date_auto_select` | `nodriver_kham_area_auto_select` |
| FamiTicket | `nodriver_famiticket.py` | （待確認函數名稱） | （待確認函數名稱） |

### 通用實作流程

#### 1. 定位目標函數
```bash
# 搜尋日期選擇函數
grep "def.*date.*auto.*select" src/nodriver_<platform>.py -i -n

# 搜尋區域選擇函數
grep "def.*area.*auto.*select" src/nodriver_<platform>.py -i -n
```

#### 2. 分析現有邏輯
**必須確認的關鍵點**：
- ✅ 關鍵字變數名稱（`date_keyword` / `area_keyword`）
- ✅ 選項列表變數名稱（可能是 `formated_list`, `option_list`, `available_items` 等）
- ✅ 配置路徑（`config_dict["date_auto_select"]` vs `config_dict.get("date_auto_select", {})`）
- ✅ 日誌變數名稱（`show_debug_message` vs `verbose`）
- ✅ 回傳值類型（`True/False` vs `selected_element` vs `None`）

#### 3. 應用五步驟模式
參考「實作模式總結」章節，替換對應的：
- `<feature>`: `date` 或 `area`
- `<PREFIX>`: `DATE` 或 `AREA`
- `<list_text>`: 平台特定的文字列表變數
- `<original_list>`: 平台特定的選項列表變數
- `<keyword>`: 平台特定的關鍵字變數
- `<select_order>`: 平台特定的排序模式變數

#### 4. 平台特定考量

**KKTIX**:
- 排隊處理：確保早期返回邏輯不干擾排隊偵測
- 價格列表：可能需要額外處理 `ticket_price` 關鍵字匹配

**iBon**:
- Shadow DOM：確認元素選擇邏輯是否使用 CDP 協議
- Angular SPA：注意動態載入的選項可能需要額外等待

**TicketPlus**:
- 展開面板：確保在面板展開後才執行關鍵字匹配
- 實名對話框：早期返回可能需要處理額外的確認步驟

**KHAM**:
- 自動座位切換：確認早期返回不會跳過座位類型選擇

**FamiTicket**:
- 待確認平台特定邏輯

### 測試檢查清單（每個平台）
- [ ] 關鍵字匹配成功時立即停止（早期返回）
- [ ] 支援 AND 邏輯（空格分隔多個關鍵字）
- [ ] 支援 OR 邏輯（逗號分隔多組關鍵字）
- [ ] `<feature>_auto_fallback=false` 時拒絕遞補（嚴格模式）
- [ ] `<feature>_auto_fallback=true` 時根據 `<select_order>` 遞補
- [ ] 舊版配置檔案（無新欄位）可正常運作（向後相容）
- [ ] 日誌輸出清晰且無 emoji（避免 cp950 編碼錯誤）

---

## UI 實作指南

### Web UI (settings.html)

#### 目標檔案
`src/settings.html`

#### 任務清單
- **T025**: 新增日期遞補 Checkbox（`date_auto_fallback`）
- **T026**: 新增日期遞補 Tooltip 說明
- **T027**: 新增區域遞補 Checkbox（`area_auto_fallback`）
- **T028**: 新增區域遞補 Tooltip 說明

#### 實作步驟

##### Step 1: 定位插入位置
搜尋現有的日期/區域選擇 UI 區塊：
```bash
# 搜尋日期選擇相關的 HTML
grep "date_auto_select" src/settings.html -A 5 -B 5

# 搜尋區域選擇相關的 HTML
grep "area_auto_select" src/settings.html -A 5 -B 5
```

**建議插入位置**：緊接在 `date_auto_select` / `area_auto_select` 的啟用 Checkbox 之後

##### Step 2: HTML 結構範本
```html
<!-- T025: Date Auto Fallback Checkbox -->
<div class="form-check">
  <input
    class="form-check-input"
    type="checkbox"
    id="date_auto_fallback"
    name="date_auto_fallback"
  >
  <label class="form-check-label" for="date_auto_fallback">
    日期自動遞補 (Date Auto Fallback)
    <span
      class="badge bg-secondary"
      data-bs-toggle="tooltip"
      data-bs-placement="top"
      title="當所有日期關鍵字都未匹配時，是否根據 date_select_order 自動選擇可用日期。預設為 false（嚴格模式）。"
    >
      ?
    </span>
  </label>
</div>

<!-- T027: Area Auto Fallback Checkbox -->
<div class="form-check">
  <input
    class="form-check-input"
    type="checkbox"
    id="area_auto_fallback"
    name="area_auto_fallback"
  >
  <label class="form-check-label" for="area_auto_fallback">
    區域自動遞補 (Area Auto Fallback)
    <span
      class="badge bg-secondary"
      data-bs-toggle="tooltip"
      data-bs-placement="top"
      title="當所有區域關鍵字都未匹配時，是否根據 area_select_order 自動選擇可用區域。預設為 false（嚴格模式）。"
    >
      ?
    </span>
  </label>
</div>
```

**注意事項**：
- `id` 和 `name` 必須與配置檔案欄位名稱完全一致
- **不要**加 `checked` 屬性（預設為 `false`）
- Tooltip 文字應包含：功能說明 + 預設值 + 行為差異

##### Step 3: JavaScript 載入邏輯
在 `settings.html` 的 JavaScript 區塊中，找到載入配置的函數（通常是 `loadSettings()` 或類似名稱）：

```javascript
// T025-T028: Load new checkbox values
function loadSettings(config) {
  // ... existing code ...

  // Date auto fallback (default: false)
  if (config.hasOwnProperty('date_auto_fallback')) {
    document.getElementById('date_auto_fallback').checked = config.date_auto_fallback;
  }

  // Area auto fallback (default: false)
  if (config.hasOwnProperty('area_auto_fallback')) {
    document.getElementById('area_auto_fallback').checked = config.area_auto_fallback;
  }

  // ... existing code ...
}
```

##### Step 4: JavaScript 儲存邏輯
在儲存配置的函數中（通常是 `saveSettings()` 或表單提交事件）：

```javascript
function saveSettings() {
  var config = {};
  // ... existing code ...

  // T025-T028: Save new checkbox values
  config.date_auto_fallback = document.getElementById('date_auto_fallback').checked;
  config.area_auto_fallback = document.getElementById('area_auto_fallback').checked;

  // ... existing code ...
}
```

##### Step 5: Tooltip 初始化
確保 Bootstrap Tooltip 已初始化（通常在 `$(document).ready()` 或 `DOMContentLoaded` 事件中）：

```javascript
// Initialize all tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});
```

---

### Desktop UI (settings_old.py - tkinter)

#### 目標檔案
`src/settings_old.py`

#### 任務清單
- **T029**: 新增日期遞補 Checkbutton（`date_auto_fallback`）
- **T030**: 新增日期遞補 Tooltip
- **T031**: 新增日期遞補多語系翻譯（繁中/簡中/英文/日文）
- **T032**: 新增區域遞補 Checkbutton（`area_auto_fallback`）
- **T033**: 新增區域遞補 Tooltip
- **T034**: 新增區域遞補多語系翻譯（繁中/簡中/英文/日文）
- **T035**: 更新 `sync_json_to_ui()` 和 `sync_ui_to_json()` 函數

#### 實作步驟

##### Step 1: 定位插入位置
搜尋現有的日期/區域選擇 UI 區塊：
```bash
# 搜尋日期選擇相關的 tkinter Checkbutton
grep "date_auto_select" src/settings_old.py -A 10 -B 5

# 搜尋區域選擇相關的 tkinter Checkbutton
grep "area_auto_select" src/settings_old.py -A 10 -B 5
```

##### Step 2: 新增 Checkbutton 變數（類別屬性）
在 `SettingsUI` 類別的 `__init__` 方法中，找到其他 Checkbutton 變數的定義位置（例如 `self.date_auto_select_enable`），新增：

```python
# T029: Date auto fallback Checkbutton variable
self.date_auto_fallback = BooleanVar(value=False)

# T032: Area auto fallback Checkbutton variable
self.area_auto_fallback = BooleanVar(value=False)
```

##### Step 3: 建立 Checkbutton UI 元件
在建立 UI 的區塊中（通常在 `create_widgets()` 或類似方法），緊接在對應的 `date_auto_select` / `area_auto_select` Checkbutton 之後：

```python
# T029: Date auto fallback Checkbutton
self.date_auto_fallback_cb = Checkbutton(
    <parent_frame>,  # 使用與 date_auto_select 相同的父容器
    text=self.translate['date_auto_fallback'],
    variable=self.date_auto_fallback,
    bg=CONST_EASYCARD_THEME_BACKGROUND_COLOR
)
self.date_auto_fallback_cb.grid(row=<next_row>, column=0, sticky=W, padx=10, pady=5)

# T030: Date auto fallback Tooltip
ToolTip(self.date_auto_fallback_cb, msg=self.translate['date_auto_fallback_tooltip'])

# T032: Area auto fallback Checkbutton
self.area_auto_fallback_cb = Checkbutton(
    <parent_frame>,  # 使用與 area_auto_select 相同的父容器
    text=self.translate['area_auto_fallback'],
    variable=self.area_auto_fallback,
    bg=CONST_EASYCARD_THEME_BACKGROUND_COLOR
)
self.area_auto_fallback_cb.grid(row=<next_row>, column=0, sticky=W, padx=10, pady=5)

# T033: Area auto fallback Tooltip
ToolTip(self.area_auto_fallback_cb, msg=self.translate['area_auto_fallback_tooltip'])
```

**注意事項**：
- `<parent_frame>`: 查看現有 `date_auto_select` Checkbutton 的父容器
- `<next_row>`: 遞增行號（例如現有為 `row=5`，則新增為 `row=6`）
- `CONST_EASYCARD_THEME_BACKGROUND_COLOR`: 專案的背景色常數

##### Step 4: 新增多語系翻譯（T031, T034）
在 `settings_old.py` 中搜尋翻譯字典（通常是 `CONST_TRANSLATE` 或類似變數）：

```python
CONST_TRANSLATE = {
    'zh_tw': {
        # ... existing translations ...
        'date_auto_fallback': '日期自動遞補',
        'date_auto_fallback_tooltip': '當所有日期關鍵字都未匹配時，是否根據「日期選擇順序」自動選擇可用日期。\n預設為「否」（嚴格模式），避免誤購不想要的票券。',
        'area_auto_fallback': '區域自動遞補',
        'area_auto_fallback_tooltip': '當所有區域關鍵字都未匹配時，是否根據「區域選擇順序」自動選擇可用區域。\n預設為「否」（嚴格模式），避免誤購不想要的票券。',
    },
    'zh_cn': {
        # ... existing translations ...
        'date_auto_fallback': '日期自动递补',
        'date_auto_fallback_tooltip': '当所有日期关键字都未匹配时，是否根据「日期选择顺序」自动选择可用日期。\n默认为「否」（严格模式），避免误购不想要的票券。',
        'area_auto_fallback': '区域自动递补',
        'area_auto_fallback_tooltip': '当所有区域关键字都未匹配时，是否根据「区域选择顺序」自动选择可用区域。\n默认为「否」（严格模式），避免误购不想要的票券。',
    },
    'en_us': {
        # ... existing translations ...
        'date_auto_fallback': 'Date Auto Fallback',
        'date_auto_fallback_tooltip': 'When all date keywords fail to match, should the system automatically select an available date based on \"Date Select Order\"?\nDefault: No (strict mode) to avoid purchasing unwanted tickets.',
        'area_auto_fallback': 'Area Auto Fallback',
        'area_auto_fallback_tooltip': 'When all area keywords fail to match, should the system automatically select an available area based on \"Area Select Order\"?\nDefault: No (strict mode) to avoid purchasing unwanted tickets.',
    },
    'ja_jp': {
        # ... existing translations ...
        'date_auto_fallback': '日付自動フォールバック',
        'date_auto_fallback_tooltip': 'すべての日付キーワードが一致しない場合、「日付選択順序」に基づいて利用可能な日付を自動的に選択しますか？\nデフォルト：いいえ（厳格モード）、望まないチケットの購入を避けるため。',
        'area_auto_fallback': 'エリア自動フォールバック',
        'area_auto_fallback_tooltip': 'すべてのエリアキーワードが一致しない場合、「エリア選択順序」に基づいて利用可能なエリアを自動的に選択しますか？\nデフォルト：いいえ（厳格モード）、望まないチケットの購入を避けるため。',
    }
}
```

##### Step 5: 更新同步函數（T035）

**5.1 更新 `sync_json_to_ui()` 函數**（從配置檔案載入到 UI）
```python
def sync_json_to_ui(self, config_dict):
    # ... existing code ...

    # T035: Sync new fields from JSON to UI
    if 'date_auto_fallback' in config_dict:
        self.date_auto_fallback.set(config_dict['date_auto_fallback'])
    else:
        self.date_auto_fallback.set(False)  # Default value

    if 'area_auto_fallback' in config_dict:
        self.area_auto_fallback.set(config_dict['area_auto_fallback'])
    else:
        self.area_auto_fallback.set(False)  # Default value

    # ... existing code ...
```

**5.2 更新 `sync_ui_to_json()` 函數**（從 UI 儲存到配置檔案）
```python
def sync_ui_to_json(self):
    config_dict = {}
    # ... existing code ...

    # T035: Sync new fields from UI to JSON
    config_dict['date_auto_fallback'] = self.date_auto_fallback.get()
    config_dict['area_auto_fallback'] = self.area_auto_fallback.get()

    # ... existing code ...
    return config_dict
```

##### Step 6: 驗證 UI 修改
- [ ] Checkbutton 在對應的日期/區域選擇區塊中顯示
- [ ] 預設狀態為未勾選（`False`）
- [ ] Tooltip 顯示正確的說明文字
- [ ] 切換語言時翻譯正確更新
- [ ] 儲存配置後，重新開啟設定介面時保留勾選狀態

---

## 測試程序

### 自動化測試（背景執行）

#### 測試前準備
```bash
# 刪除暫停標記檔案（CRITICAL）
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt

# 清空測試輸出檔案
echo "" > .temp/test_output.txt
```

#### NoDriver 版本測試指令（Git Bash）
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

#### NoDriver 版本測試指令（Windows CMD）
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

### 日誌驗證指令

#### 檢查日期選擇邏輯
```bash
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]\|\[DATE FALLBACK\]" .temp/test_output.txt
```

**預期輸出範例**（早期返回模式）：
```
[DATE KEYWORD] Checking keyword #1: 2025-11-01
[DATE KEYWORD] Keyword #1 matched: '2025-11-01'
[DATE SELECT] Selected date: 2025-11-01 (六) 19:30 (keyword match)
```

**預期輸出範例**（全部失敗 + 嚴格模式）：
```
[DATE KEYWORD] Checking keyword #1: 無效關鍵字
[DATE KEYWORD] Checking keyword #2: 另一個無效關鍵字
[DATE KEYWORD] All keywords failed to match
[DATE FALLBACK] date_auto_fallback=false, fallback is disabled
[DATE SELECT] Waiting for manual intervention
```

**預期輸出範例**（全部失敗 + 遞補模式）：
```
[DATE KEYWORD] Checking keyword #1: 無效關鍵字
[DATE KEYWORD] All keywords failed to match
[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback
[DATE FALLBACK] Selecting available date based on date_select_order='from_top'
[DATE SELECT] Selected date: 2025-11-05 (三) 14:00 (fallback)
```

#### 檢查區域選擇邏輯
```bash
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]\|\[AREA FALLBACK\]" .temp/test_output.txt
```

### 手動測試場景（T037-T039）

#### T037: 早期返回模式驗證
**測試配置**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-11-01,2025-11-02,2025-11-03"
  },
  "date_auto_fallback": false
}
```

**測試步驟**：
1. 前往測試票券頁面（確保有多個日期選項）
2. 確保第一個關鍵字（2025-11-01）存在於選項中
3. 執行腳本並檢查日誌

**驗證點**：
- [ ] 日誌顯示 `Checking keyword #1`
- [ ] 日誌顯示 `Keyword #1 matched`
- [ ] 日誌**不顯示** `Checking keyword #2`（早期返回成功）
- [ ] 最終選擇的日期為 2025-11-01

#### T038: 條件式遞補驗證（嚴格模式）
**測試配置**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "無效關鍵字1,無效關鍵字2"
  },
  "date_auto_fallback": false,
  "date_select_order": "from_top"
}
```

**測試步驟**：
1. 前往測試票券頁面
2. 確保關鍵字不存在於任何選項中
3. 執行腳本並檢查日誌

**驗證點**：
- [ ] 日誌顯示 `All keywords failed to match`
- [ ] 日誌顯示 `date_auto_fallback=false, fallback is disabled`
- [ ] 日誌顯示 `Waiting for manual intervention`
- [ ] 腳本返回 `False`，未選擇任何日期

#### T039: 條件式遞補驗證（遞補模式）
**測試配置**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "無效關鍵字1,無效關鍵字2"
  },
  "date_auto_fallback": true,
  "date_select_order": "from_top"
}
```

**測試步驟**：
1. 前往測試票券頁面
2. 確保關鍵字不存在於任何選項中
3. 執行腳本並檢查日誌

**驗證點**：
- [ ] 日誌顯示 `All keywords failed to match`
- [ ] 日誌顯示 `date_auto_fallback=true, triggering auto fallback`
- [ ] 日誌顯示 `Selecting available date based on date_select_order='from_top'`
- [ ] 腳本成功選擇第一個可用日期（根據 `date_select_order`）

### AND 邏輯驗證（T009 已支援）
**測試配置**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-11-01 19:30"
  }
}
```

**驗證點**：
- [ ] 只匹配同時包含「2025-11-01」和「19:30」的選項
- [ ] 日誌顯示 AND 邏輯判斷過程

---

## 常見問題

### Q1: 為什麼預設值是 `false` 而不是 `true`？
**A**: 嚴格模式（`false`）是為了避免誤購不想要的票券。根據 spec.md 的核心設計原則：
> "預設為嚴格模式（不自動遞補），避免誤購不符合期望的票券"

使用者應主動啟用遞補功能，而非被動退出。

### Q2: 舊版配置檔案（無新欄位）會出錯嗎？
**A**: 不會。所有程式碼都使用 `.get('date_auto_fallback', False)` 安全存取，當欄位不存在時自動使用預設值 `False`。

### Q3: 為什麼要保留舊版邏輯於註解中？
**A**: 遵循 constitution.md 的「回滾支援」原則：
- 新功能可能有未預見的 bug
- 2 週內可快速回滾（取消註解舊邏輯，註解新邏輯）
- 2 週後（2025-11-14）如無問題則刪除 DEPRECATED 區塊

### Q4: 日誌為什麼必須使用英文？
**A**: Windows 系統預設編碼為 cp950，中文/emoji 會導致 `UnicodeEncodeError`。專案規範要求：
- ✅ 日誌：純英文
- ✅ Tooltip/UI：多語系翻譯
- ❌ 禁止：emoji 於 `.py` 檔案中

### Q5: 早期返回模式會影響效能嗎？
**A**: 正面影響。根據 spec.md 的效能分析：
- **舊版邏輯**：掃描所有關鍵字 → 收集所有匹配 → 選擇一個
- **新版邏輯**：逐個檢查關鍵字 → 第一個匹配立即停止
- **效能提升**：平均節省約 30% 檢查時間（當第一個關鍵字匹配時達到最佳）

### Q6: 如何驗證 AND 邏輯是否正確？
**A**: 使用空格分隔關鍵字（例如 `"2025-11-01 19:30"`），檢查日誌：
```
[DATE KEYWORD] Checking keyword #1: ['2025-11-01', '19:30']
```
確保所有子關鍵字都在 `normalized_row_text` 中匹配。

### Q7: UI Tooltip 不顯示怎麼辦？
**A**:
- **Web UI**: 檢查 Bootstrap 版本是否支援 `data-bs-toggle`（Bootstrap 5+），確認 Tooltip 已初始化
- **Desktop UI**: 檢查 `ToolTip` 類別是否已正確 import（通常從 `tkinterweb` 或自定義模組）

### Q8: 如何測試多平台實作？
**A**:
1. 先測試 TixCraft（已有示範實作）
2. 使用相同的測試配置檔案（只改 `webdriver_type`）
3. 逐平台驗證日誌輸出格式
4. 檢查平台特定邏輯（排隊處理、Shadow DOM 等）

### Q9: 如果函數返回值類型不同怎麼辦？
**A**: 部分平台函數可能返回元素物件而非 `True/False`。修改時需要注意：
- 早期返回：`return selected_element`（成功）
- 嚴格模式拒絕：`return None` 或 `return False`（失敗）
- 保持與原函數一致的返回值類型

### Q10: 實作完成後需要更新哪些文件？
**A**: 根據 tasks.md：
- **T036**: 更新 `CHANGELOG.md`（記錄新功能）
- **T040**: 更新 `docs/02-development/structure.md`（新增函數修改說明）
- **選擇性**: 更新平台特定的 troubleshooting 文件（如有新的已知問題）

### Q11: 為什麼條件檢查需要先檢查 `is not None`？
**A**: **重要 Bug 修正**（2025-10-31 發現）：當頁面沒有任何選項時，`matched_blocks` 和 `formated_area_list` 可能被初始化為 `None` 而非空列表 `[]`。

**錯誤範例**（會拋出 `TypeError: object of type 'NoneType' has no len()`）：
```python
if len(matched_blocks) == 0 and date_keyword and formated_area_list and len(formated_area_list) > 0:
```

**正確寫法**（先檢查 `is not None`）：
```python
if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and formated_area_list is not None and len(formated_area_list) > 0:
```

**技術細節**：
- 在函數開頭，變數可能被初始化為 `None`（例如：`matched_blocks = None`）
- 只有當 `area_list` 存在時，`formated_area_list` 才會被設為空列表 `[]`
- 當測試頁面沒有任何日期/區域選項時，這些變數會保持為 `None`
- 直接對 `None` 執行 `len()` 會拋出 `TypeError`

**測試場景**：
- 空頁面（沒有任何選項）
- 所有選項都被排除（`reset_row_text_if_match_keyword_exclude` 全部過濾）
- 頁面載入失敗（`area_list` 為 `None`）

**修正位置**（TixCraft 示範實作）：
- `nodriver_tixcraft.py` 第 2742 行（條件式遞補檢查）
- `nodriver_tixcraft.py` 第 2757 行（空列表處理）

---

## 附錄

### A. 相關文件連結
- **功能規格**: `specs/003-keyword-priority-fallback/spec.md`
- **實作計畫**: `specs/003-keyword-priority-fallback/plan.md`
- **資料模型**: `specs/003-keyword-priority-fallback/data-model.md`
- **任務清單**: `specs/003-keyword-priority-fallback/tasks.md`
- **專案憲法**: `.specify/memory/constitution.md`
- **配置 Schema**: `specs/003-keyword-priority-fallback/contracts/config-schema.md`

### B. 程式碼審查檢查清單
實作完成後，使用以下檢查清單進行自我審查：

#### 程式碼品質
- [ ] 主開關檢查位於函數入口
- [ ] 使用 `.get()` 安全存取新欄位
- [ ] 早期返回邏輯正確實作（第一個匹配立即停止）
- [ ] 支援 AND 邏輯（空格分隔）
- [ ] 支援 OR 邏輯（逗號分隔）
- [ ] 條件式遞補邏輯正確實作（`true` vs `false`）
- [ ] 舊版邏輯完整保留於 DEPRECATED 註解
- [ ] 日誌使用結構化前綴（`[<PREFIX> KEYWORD]` 等）
- [ ] 日誌為純英文（無 emoji）
- [ ] 變數名稱與原函數一致

#### 向後相容性
- [ ] 舊版配置檔案（無新欄位）可正常運作
- [ ] 預設值為 `false`（嚴格模式）
- [ ] 不影響現有功能（排除邏輯、隨機選擇等）

#### UI 實作（如適用）
- [ ] Checkbox ID/name 與配置欄位一致
- [ ] 預設狀態為未勾選
- [ ] Tooltip 顯示正確
- [ ] 多語系翻譯完整（繁中/簡中/英文/日文）
- [ ] `sync_json_to_ui()` 和 `sync_ui_to_json()` 已更新

#### 測試驗證
- [ ] 早期返回測試通過（第一個關鍵字匹配）
- [ ] 嚴格模式測試通過（`false` 拒絕遞補）
- [ ] 遞補模式測試通過（`true` 觸發遞補）
- [ ] AND 邏輯測試通過
- [ ] 日誌輸出符合規範

### C. Git 提交規範
根據 constitution.md 第 IX 條，提交訊息應遵循：

**格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**範例提交訊息**（TixCraft 日期選擇）：
```
feat(tixcraft): implement early return and conditional fallback for date selection

- Add main switch check at function entry (T003)
- Implement early return pattern: stop at first keyword match (T004)
- Add structured logging with [DATE KEYWORD], [DATE SELECT], [DATE FALLBACK] prefixes (T005-T007)
- Preserve old logic in DEPRECATED comment for 2-week rollback window (T008)
- Implement conditional fallback based on date_auto_fallback switch (T017-T020)
- Use safe access pattern .get('date_auto_fallback', False) for backward compatibility

Related: specs/003-keyword-priority-fallback
```

**範例提交訊息**（UI 實作）：
```
feat(ui): add date_auto_fallback and area_auto_fallback checkboxes

- Add date_auto_fallback checkbox in settings.html with tooltip (T025-T026)
- Add area_auto_fallback checkbox in settings.html with tooltip (T027-T028)
- Add checkbuttons in settings_old.py (tkinter) (T029, T032)
- Add tooltips for desktop UI (T030, T033)
- Add multilingual translations (zh_tw, zh_cn, en_us, ja_jp) (T031, T034)
- Update sync_json_to_ui() and sync_ui_to_json() (T035)

Related: specs/003-keyword-priority-fallback
```

### D. 快速參考卡

#### 配置欄位
| 欄位名稱 | 類型 | 預設值 | 說明 |
|---------|------|--------|------|
| `date_auto_fallback` | `boolean` | `false` | 日期關鍵字全部失敗時是否自動遞補 |
| `area_auto_fallback` | `boolean` | `false` | 區域關鍵字全部失敗時是否自動遞補 |

#### 日誌前綴對照表
| 功能 | 關鍵字檢查 | 選擇行為 | 遞補行為 |
|------|-----------|---------|---------|
| 日期 | `[DATE KEYWORD]` | `[DATE SELECT]` | `[DATE FALLBACK]` |
| 區域 | `[AREA KEYWORD]` | `[AREA SELECT]` | `[AREA FALLBACK]` |
| 票價 | `[PRICE KEYWORD]` | `[PRICE SELECT]` | `[PRICE FALLBACK]` |

#### 關鍵函數對照表（TixCraft）
| 功能 | 函數名稱 | 關鍵字變數 | 選項列表變數 |
|------|---------|-----------|------------|
| 日期選擇 | `nodriver_tixcraft_date_auto_select` | `date_keyword` | `formated_area_list` |
| 區域選擇 | `nodriver_tixcraft_area_auto_select` | `area_keyword` | `area_list` |

---

## 結語

本實作指南提供了完整的模式範本與實作步驟，讓開發者可以獨立完成剩餘的 29 個任務（T010-T040）。核心原則：

1. **遵循示範模式**: TixCraft 日期選擇已提供完整實作參考
2. **五步驟標準流程**: 主開關 → 安全存取 → 早期返回 → 條件遞補 → 保留舊版
3. **平台特定調整**: 根據各平台特性調整變數名稱與邏輯細節
4. **測試驅動驗證**: 使用結構化日誌驗證每個功能點
5. **文件同步更新**: 完成後更新 CHANGELOG.md 與 structure.md

如有疑問，請參考：
- **技術細節**: `spec.md`, `plan.md`, `contracts/config-schema.md`
- **憲法規範**: `.specify/memory/constitution.md`
- **除錯方法**: `docs/04-testing-debugging/debugging_methodology.md`

**預估工時**（參考）：
- TixCraft 區域選擇（T010-T024）: 2-3 小時
- 其他 5 個平台（每平台 2 功能）: 10-15 小時
- UI 實作（Web + Desktop）: 3-4 小時
- 測試與文件更新: 2-3 小時
- **總計**: 約 17-25 小時

祝實作順利！
