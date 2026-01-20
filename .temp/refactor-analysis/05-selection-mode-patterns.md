# 選擇模式（Selection Mode）使用分析

**分析範圍**：全平台選擇模式實作
**選擇模式總使用次數**：50+ 處

---

## 一、選擇模式常數定義

### 定義位置（4 個檔案）

| 檔案 | 行號 | 用途 |
|------|------|------|
| `src/settings.py` | 58-61 | 設定檔使用的常數 |
| `src/util.py` | 17-20 | 共用工具常數 |
| `src/nodriver_tixcraft.py` | 103-107 | NoDriver 主程式常數 |
| `src/chrome_tixcraft.py` | 115-118 | Chrome Driver 主程式常數 |

### 選擇模式值

```python
CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"  # 預設
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
```

---

## 二、實作模式分類

### 模式 A：直接 4 分支實作（最常見 - 已優化）

**原本出現次數**：至少 8 處
**目前狀態**：已重構為 `util.get_target_index_by_mode()`

```python
# 舊代碼（重複 8 處）
if auto_select_mode == "random":
    target = random.choice(matched)
elif auto_select_mode == "from bottom to top":
    target = matched[-1]
elif auto_select_mode == "center":
    target = matched[len(matched) // 2]
else:  # from top to bottom (default)
    target = matched[0]

# 新代碼（統一調用）
target_index = util.get_target_index_by_mode(len(matched), auto_select_mode)
target = matched[target_index]
```

**已重構位置**：
- UDN 日期（行 18053）
- UDN 場次（行 18134）
- UDN 區域（行 18273）
- iBon 日期模式（行 9373）
- iBon 日期 Pierce（行 10741）
- iBon 日期 Shadow DOM（行 11094）
- FamiTicket 日期（行 9775）
- FamiTicket 區域（行 9976）

---

### 模式 B：使用 util 工具函數

**出現次數**：至少 10+ 處（Chrome Driver 為主）

```python
target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
```

**位置**：
- Chrome Driver 各平台的日期/區域選擇
- NoDriver 部分平台（TixCraft、HKTicketing）

---

### 模式 C：提前終止（Early Exit）

**出現次數**：至少 15 處

```python
if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
    break  # 只需要第一個匹配結果
```

**位置**：
- KKTIX（行 1005）
- TixCraft（行 5343）
- HKTicketing Type 1（行 23089）
- HKTicketing Type 2（行 24009）
- Chrome Driver 多處

---

### 模式 D：JavaScript 注入實作

**出現次數**：3 處（TicketPlus 專用）

```javascript
switch(mode) {
    case 'from top to bottom': return 0;
    case 'from bottom to top': return count - 1;
    case 'center': return Math.floor(count / 2);
    case 'random': return Math.floor(Math.random() * count);
}
```

---

## 三、各平台使用狀況

| 平台 | 日期選擇 | 區域選擇 | 實作模式 | 狀態 |
|------|---------|---------|---------|------|
| **TixCraft** | ✓ | ✓ | B + C | 已標準化 |
| **KKTIX** | ✓ | ✓ | C | 已標準化 |
| **iBon** | ✓ | ✓ | A → 已重構 | ✅ 已優化 |
| **FamiTicket** | ✓ | ✓ | A → 已重構 | ✅ 已優化 |
| **UDN** | ✓ | ✓ | A → 已重構 | ✅ 已優化 |
| **TicketPlus** | ✓ | ✓ | D (JS) | 特殊實作 |
| **HKTicketing** | ✓ | ✓ | B + C | 已標準化 |
| **KHAM** | ✓ | ✓ | B | 已標準化 |

---

## 四、已完成的重構

### 新增函式：`util.get_target_index_by_mode()`

**位置**：`src/util.py:1342`

```python
def get_target_index_by_mode(list_length, auto_select_mode):
    """Calculate target index based on selection mode."""
    if list_length <= 0:
        return None

    # Normalize mode format: convert underscore to space
    mode = auto_select_mode.replace('_', ' ') if auto_select_mode else ""

    if mode == CONST_FROM_BOTTOM_TO_TOP:
        return list_length - 1
    elif mode == CONST_CENTER:
        return list_length // 2
    elif mode == CONST_RANDOM:
        return random.randint(0, list_length - 1)
    else:  # CONST_FROM_TOP_TO_BOTTOM or default
        return 0
```

### 特殊處理

**FamiTicket 格式相容**：
- 問題：FamiTicket 使用 `from_bottom_to_top`（底線）
- 解決：`mode.replace('_', ' ')` 標準化

---

## 五、文件更新

### 已更新：`docs/03-mechanisms/README.md`

新增「Selection Mode Standard」章節：
- 標準使用方式
- 禁止事項
- 相關 API 參考

---

## 六、剩餘工作

### 中優先級：常數使用統一

**問題**：部分代碼使用字串字面量而非常數

```python
# 應該使用（最佳實踐）
if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:

# 實際使用（部分位置）
elif auto_select_mode == "from bottom to top":
```

**建議**：逐步替換為常數比較

### 低優先級：提前終止邏輯統一

**建議新增工具函式**：

```python
def should_break_on_first_match(mode):
    """檢查是否應在第一個匹配後終止"""
    return mode in [CONST_FROM_TOP_TO_BOTTOM, "from top to bottom"]
```

**替代位置**：15+ 處提前終止邏輯
