# 設定讀取模式分析

**分析檔案**：`src/nodriver_tixcraft.py`
**config_dict 存取總數**：470+ 次

---

## 一、重複的設定讀取模式

### 1.1 `show_debug_message` 變數設定（高度重複）

**統計數據**：
- 直接存取 `config_dict["advanced"]["verbose"]`：28 次
- 使用 `.get()` 安全存取：50+ 次
- 混合式存取：5 次

**六種不一致的存取模式**：

```python
# 模式 1: 直接存取（可能拋出 KeyError）
show_debug_message = config_dict["advanced"]["verbose"]

# 模式 2: 單層 .get() 安全存取
show_debug_message = config_dict["advanced"].get("verbose", False)

# 模式 3: 雙層 .get() 最安全存取
show_debug_message = config_dict.get("advanced", {}).get("verbose", False)

# 模式 4: 條件檢查 + 直接存取
show_debug_message = config_dict["advanced"]["verbose"] if config_dict else False

# 模式 5: 複合邏輯（OR 運算）
show_debug_message = config_dict["advanced"].get("verbose", False) or force_show_debug

# 模式 6: 硬編碼開發切換
show_debug_message = True  # debug
show_debug_message = False  # online
if config_dict["advanced"]["verbose"]:
    show_debug_message = True
```

**問題**：
- **不一致性**：6 種不同的存取模式，維護困難
- **風險**：模式 1 可能因缺少 key 導致 KeyError

---

### 1.2 日期選擇設定讀取（30+ 處）

**典型重複代碼區塊**：
```python
# 在 20+ 個函式中重複出現此模式
if not config_dict["date_auto_select"]["enable"]:
    if show_debug_message:
        print("[DATE SELECT] Main switch is disabled")
    return False

auto_select_mode = config_dict["date_auto_select"]["mode"]
date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
date_auto_fallback = config_dict.get('date_auto_fallback', False)
```

**不一致的存取模式**：
- **模式 1**：直接存取（大多數函式）
- **模式 2**：`.get().get()` 安全存取（TicketMaster）
- **模式 3**：混合式（FamiTicket）

---

### 1.3 區域選擇設定讀取（25+ 處）

**典型重複代碼區塊**：
```python
if not config_dict["area_auto_select"]["enable"]:
    if show_debug_message:
        print("[AREA SELECT] Main switch is disabled")
    return False

area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
auto_select_mode = config_dict["area_auto_select"]["mode"]
area_auto_fallback = config_dict.get('area_auto_fallback', False)
```

---

## 二、平台一致性比較

| 平台 | show_debug | date_keyword | area_keyword | 一致性 |
|------|------------|--------------|--------------|--------|
| KKTIX | `.get()` ✓ | 直接存取 ✗ | 直接存取 ✗ | 中 |
| TixCraft | `.get()` ✓ | 直接存取 ✗ | 直接存取 ✗ | 中 |
| TicketPlus | `.get()` ✓ | 直接存取 ✗ | N/A | 中 |
| TicketMaster | `.get().get()` ✓✓ | `.get().get()` ✓✓ | `.get().get()` ✓✓ | **高** |
| FamiTicket | `.get()` ✓ | 混合式 ⚠ | 混合式 ⚠ | 低 |
| iBon | `.get()` ✓ | 直接存取 ✗ | 直接存取 ✗ | 中 |

**圖例**：
- ✓ = 使用安全的 `.get()` 方法
- ✓✓ = 使用雙層 `.get()` 最安全
- ✗ = 直接存取（可能 KeyError）
- ⚠ = 混合式存取

---

## 三、建議封裝函式

### 3.1 `get_debug_mode(config_dict)`

**影響範圍**：80+ 處可替換

```python
def get_debug_mode(config_dict):
    """安全讀取 debug 模式設定"""
    try:
        return config_dict.get("advanced", {}).get("verbose", False)
    except:
        return False
```

### 3.2 `get_date_select_config(config_dict)`

**影響範圍**：30+ 處可替換

```python
def get_date_select_config(config_dict):
    """讀取日期選擇相關設定"""
    date_config = config_dict.get("date_auto_select", {})
    return {
        'enable': date_config.get("enable", True),
        'mode': date_config.get("mode", "from top to bottom"),
        'date_keyword': date_config.get("date_keyword", "").strip(),
        'fallback': config_dict.get('date_auto_fallback', False)
    }
```

### 3.3 `get_area_select_config(config_dict)`

**影響範圍**：25+ 處可替換

```python
def get_area_select_config(config_dict):
    """讀取區域選擇相關設定"""
    area_config = config_dict.get("area_auto_select", {})
    return {
        'enable': area_config.get("enable", True),
        'mode': area_config.get("mode", "from top to bottom"),
        'area_keyword': area_config.get("area_keyword", "").strip(),
        'fallback': config_dict.get('area_auto_fallback', False)
    }
```

### 3.4 `check_auto_select_enabled(config_dict, select_type)`

**影響範圍**：35+ 處可替換

```python
def check_auto_select_enabled(config_dict, select_type, show_debug=False):
    """檢查自動選擇功能是否啟用"""
    config_key = f"{select_type}_auto_select"
    is_enabled = config_dict.get(config_key, {}).get("enable", True)

    if not is_enabled and show_debug:
        print(f"[{select_type.upper()} SELECT] Main switch is disabled")

    return is_enabled
```

---

## 四、重構影響估算

| 改進項目 | 受影響行數 | 函式數量 | 風險等級 | 預估工時 |
|---------|-----------|---------|---------|---------|
| 統一 debug 讀取 | 80+ | 50+ | 低 | 2h |
| 統一日期設定讀取 | 90+ | 30+ | 中 | 4h |
| 統一區域設定讀取 | 75+ | 25+ | 中 | 4h |
| 統一帳號讀取 | 30+ | 10+ | 低 | 1h |
| 統一 enable 檢查 | 70+ | 35+ | 低 | 2h |
| **總計** | **345+** | **150+** | - | **13h** |

---

## 五、行動建議

### P0 - 立即修復（低風險高效益）

1. **新增 `get_debug_mode()` 函式**
2. 替換所有 `show_debug_message` 讀取（80+ 處）

### P1 - 短期改善

3. **新增 `get_date_select_config()` 函式**
4. **新增 `get_area_select_config()` 函式**
5. 逐步替換核心函式

### P2 - 長期優化

6. 設計 `ConfigHelper` 類別
7. 重構所有平台函式
