# P0 重構實作設計

**建立日期**：2025-12-18
**狀態**：✅ Phase 7 - 已完成

---

## 一、設計決策摘要

### Q1-Q5 決策結果

| 問題 | 選項 | 說明 |
|------|------|------|
| Q1 | A | 保留 Cloudflare 特殊邏輯（L439-444） |
| Q2 | A | 移除 `force_show_debug` 死代碼 |
| Q3 | A | 替換所有 11 處直接索引存取 |
| Q4 | B | 僅基礎回退（返回空陣列） |
| Q5 | B | 漸進式替換（17 處先行） |

---

## 二、函式設計

### 2.1 `get_debug_mode(config_dict)`

**目的**：統一 debug 模式讀取，避免 KeyError

**設計**：
```python
def get_debug_mode(config_dict):
    """
    Safely read debug mode setting from config.

    Consolidates 6 different access patterns found in codebase:
    - Pattern 1: config_dict["advanced"]["verbose"] (HIGH RISK - KeyError)
    - Pattern 2: config_dict["advanced"].get("verbose", False)
    - Pattern 3: config_dict.get("advanced", {}).get("verbose", False) (SAFEST)

    Args:
        config_dict: Configuration dictionary

    Returns:
        bool: Debug mode status, defaults to False

    Example:
        # Before (6 different patterns, 80+ locations):
        show_debug_message = config_dict["advanced"]["verbose"]

        # After (unified):
        show_debug_message = get_debug_mode(config_dict)
    """
    try:
        return config_dict.get("advanced", {}).get("verbose", False)
    except:
        return False
```

**位置**：`util.py` Line ~1410（`get_target_item_from_matched_list()` 之後）

**替換範圍**：
- 11 處直接索引存取（Q3 決定替換）
- 95 處 `.get()` 存取（逐步替換）
- **排除**：L439-444 Cloudflare 特殊邏輯（Q1 決定保留）

---

### 2.2 `parse_keyword_string_to_array(keyword_string)`

**目的**：統一關鍵字字串解析

**設計**：
```python
def parse_keyword_string_to_array(keyword_string):
    """
    Parse keyword string to array using JSON format.

    Expected input format: '"keyword1","keyword2"' or '"keyword1 sub1","keyword2"'
    Inner space = AND logic, outer comma = OR logic.

    This function only handles parsing. For custom fallback logic,
    check the return value and implement fallback at call site.

    Args:
        keyword_string: Comma-separated quoted keywords

    Returns:
        list: Parsed keywords, or empty list on failure

    Example:
        parse_keyword_string_to_array('"VIP","1樓"') -> ["VIP", "1樓"]
        parse_keyword_string_to_array('"VIP 搖滾區"') -> ["VIP 搖滾區"]
        parse_keyword_string_to_array('') -> []
        parse_keyword_string_to_array('invalid') -> []

    Note:
        For locations requiring custom fallback (e.g., comma split, semicolon split),
        implement fallback at call site:

        keywords = parse_keyword_string_to_array(keyword)
        if not keywords:
            keywords = [kw.strip() for kw in keyword.split(',') if kw.strip()]
    """
    if not keyword_string or not keyword_string.strip():
        return []
    try:
        return json.loads("[" + keyword_string + "]")
    except:
        return []
```

**位置**：`util.py` Line ~1420（`get_debug_mode()` 之後）

**替換範圍**（Q5 漸進式）：

**第一批（17 處）**：
| 行號 | 平台 | 原有回退 | 替換方式 |
|------|------|---------|---------|
| 5037 | TixCraft 區域 | `[]` | 直接替換 |
| 5463 | TixCraft 區域2 | `[]` | 直接替換 |
| 10669 | iBon 日期 Pierce | `[]` | 直接替換 |
| 11016 | iBon 日期 DOM | `[]` | 直接替換 |
| 17346 | KHAM 區域 | `[]` | 直接替換 |
| 9746 | FamiTicket 日期 | 逗號分割 | 替換 + 保留回退 |
| 22988 | HKTicketing 區域 | 逗號分割 | 替換 + 保留回退 |
| 23921 | HKTicketing 日期2 | 逗號分割 | 替換 + 保留回退 |
| 24064 | HKTicketing 區域2 | 逗號分割 | 替換 + 保留回退 |

**第二批（可安全替換 + 移除後處理/回退）- 5 處**：

| 行號 | 平台 | 原有處理 | 動作 | 理由 |
|------|------|---------|------|------|
| 3921 | TicketMaster 區域 | 逗號再分割 | 替換 + 移除後處理 | GUI 已標準化格式 |
| 8857 | TicketPlus 區域 | 原始值回退 | 替換 + 移除回退 | GUI 已標準化格式 |
| 17948 | UDN 日期 | `format_keyword_string` | 替換 + 移除後處理 | 無全形空格問題 |
| 18032 | UDN 日期2 | `format_keyword_string` | 替換 + 移除後處理 | 無全形空格問題 |
| 18142 | UDN 區域 | `format_keyword_string` | 替換 + 移除後處理 | 無全形空格問題 |

**第三批（需額外評估）- 5 處**：
- L1649, L3770, L4778, L6771, L16479（無本地 try-except，外層已包裹）

**不替換 - 2 處**：
- L7037, L18706（3 級回退：JSON → 分號 → 單一值，支援 Issue #23）

---

## 三、實作順序

### Step 1：新增函式到 util.py
1. 新增 `get_debug_mode()`
2. 新增 `parse_keyword_string_to_array()`

### Step 2：替換 get_debug_mode（高風險位置優先）
1. 替換 11 處直接索引存取
2. 驗證無 KeyError

### Step 3：替換 parse_keyword_string_to_array（第一批）
1. 替換 5 處無回退位置
2. 替換 4 處逗號分割位置（保留自訂回退）

### Step 4：更新已有重複代碼
- `util.py:1413-1416` 已有相同模式，改為調用新函式

---

## 四、相容性保證

### get_debug_mode
- 輸入：任意 dict（包括空 dict、None）
- 輸出：bool
- 錯誤處理：捕獲所有異常，返回 False

### parse_keyword_string_to_array
- 輸入：任意字串（包括空字串、None、無效 JSON）
- 輸出：list
- 錯誤處理：捕獲所有異常，返回 []
- **不破壞**：現有自訂回退邏輯可在 call site 保留

---

## 五、測試驗證

### 單元測試案例

```python
# get_debug_mode
assert get_debug_mode({}) == False
assert get_debug_mode({"advanced": {}}) == False
assert get_debug_mode({"advanced": {"verbose": True}}) == True
assert get_debug_mode({"advanced": {"verbose": False}}) == False
assert get_debug_mode(None) == False  # Edge case

# parse_keyword_string_to_array
assert parse_keyword_string_to_array("") == []
assert parse_keyword_string_to_array(None) == []
assert parse_keyword_string_to_array('"VIP"') == ["VIP"]
assert parse_keyword_string_to_array('"VIP","1樓"') == ["VIP", "1樓"]
assert parse_keyword_string_to_array('"VIP 搖滾區"') == ["VIP 搖滾區"]
assert parse_keyword_string_to_array('invalid') == []
assert parse_keyword_string_to_array('["VIP"]') == []  # 已有括號，應失敗
```

---

## 六、實作完成報告

**完成日期**：2025-12-18

### 6.1 新增函式

| 函式 | 位置 | 狀態 |
|------|------|------|
| `get_debug_mode()` | `util.py:1411-1436` | ✅ 已新增 |
| `parse_keyword_string_to_array()` | `util.py:1439-1474` | ✅ 已新增 |

### 6.2 替換統計

| 項目 | 數量 | 狀態 |
|------|------|------|
| `get_debug_mode` 替換 | 28 處 | ✅ 已完成 |
| `parse_keyword_string_to_array` 第一批 | 9 處 | ✅ 已完成 |
| `parse_keyword_string_to_array` 第二批 | 5 處 | ✅ 已完成 |
| 第三批（需額外評估） | 5 處 | ⏸️ 暫緩 |
| 不替換（3 級回退） | 2 處 | ❌ 保留原邏輯 |

### 6.3 保留項目

| 項目 | 原因 |
|------|------|
| L439-444 Cloudflare 特殊邏輯 | Q1 決定：保留 OR debug mode 邏輯 |
| L7037, L18706（3 級回退） | 支援 Issue #23 分號分隔符，需保留 |

### 6.4 第二批替換詳情

**MCP 測試結論**（2025-12-18）：
- 年代售票、UDN、TixCraft 均無全形空格
- `format_keyword_string()` 為歷史遺留代碼，可安全移除
- GUI `format_config_keyword_for_json()` 已標準化所有輸入格式
- 回退機制有潛在 bug（如 `3,280` 會被解析為 `[3, 280]`）

| 行號 | 移除項目 | 預期效果 |
|------|---------|---------|
| 3921 | 逗號再分割回退 | 減少 ~5 行 |
| 8857 | 原始值回退 | 減少 ~3 行 |
| 17948 | `format_keyword_string()` | 減少 ~2 行 |
| 18032 | `format_keyword_string()` | 減少 ~2 行 |
| 18142 | `format_keyword_string()` | 減少 ~2 行 |

### 6.5 語法驗證

```
util.py syntax OK
nodriver_tixcraft.py syntax OK
```

### 6.6 節省代碼行數

- `get_debug_mode`: 28 處 × 1 行 = 28 行更安全
- `parse_keyword_string_to_array`: 9 處 × ~5 行 = ~45 行節省
- **總計**: ~73 行代碼簡化

