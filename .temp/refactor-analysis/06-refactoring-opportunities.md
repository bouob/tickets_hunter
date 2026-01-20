# 重構機會彙整與優先級排序

**分析日期**：2025-12-18
**分析範圍**：util.py + nodriver_tixcraft.py 交叉比對

---

## 一、重構機會總覽

### 已完成 ✅

| 項目 | 狀態 | 效益 |
|------|------|------|
| 選擇模式 4 分支邏輯 | ✅ 已完成 | 8 處統一為 1 個函式 |

### 待執行（依優先級）

| 優先級 | 項目 | 出現次數 | 預估節省行數 | 風險 |
|--------|------|----------|--------------|------|
| **P0** | `get_debug_mode()` | 80+ | 160+ | 低 |
| **P0** | `parse_keyword_string_to_array()` | 25 | 75+ | 低 |
| **P1** | `get_date_select_config()` | 30+ | 90+ | 中 |
| **P1** | `get_area_select_config()` | 25+ | 75+ | 中 |
| **P1** | `match_keyword_with_text()` | 11+ | 110+ | 中 |
| **P2** | `check_auto_select_enabled()` | 35+ | 70+ | 低 |
| **P2** | 常數使用統一 | 多處 | - | 低 |
| **P3** | `ConfigHelper` 類別 | 全平台 | 200+ | 高 |

---

## 二、P0 優先級詳細說明

### 2.1 `get_debug_mode(config_dict)` - 立即可實作

**問題**：80+ 處使用 6 種不同方式讀取 debug 模式

**現況**：
```python
# 6 種不一致的存取模式
show_debug_message = config_dict["advanced"]["verbose"]
show_debug_message = config_dict["advanced"].get("verbose", False)
show_debug_message = config_dict.get("advanced", {}).get("verbose", False)
# ... 等等
```

**建議實作**：
```python
# 新增到 util.py
def get_debug_mode(config_dict):
    """安全讀取 debug 模式設定"""
    try:
        return config_dict.get("advanced", {}).get("verbose", False)
    except:
        return False
```

**替換範例**：
```python
# 舊
show_debug_message = config_dict["advanced"].get("verbose", False)

# 新
show_debug_message = util.get_debug_mode(config_dict)
```

**效益**：
- 統一存取模式
- 防止 KeyError
- 一處修改全域生效

---

### 2.2 `parse_keyword_string_to_array(keyword)` - 立即可實作

**問題**：25 處重複的 JSON 解析模式

**現況**：
```python
keyword_array = json.loads("[" + date_keyword + "]")
keyword_array = json.loads("[" + area_keyword + "]")
# 重複 25 次
```

**建議實作**：
```python
# 新增到 util.py
def parse_keyword_string_to_array(keyword_string):
    """將關鍵字字串解析為陣列"""
    if not keyword_string or not keyword_string.strip():
        return []
    try:
        return json.loads("[" + keyword_string + "]")
    except json.JSONDecodeError:
        return [keyword_string.strip()]
```

**替換範例**：
```python
# 舊
keyword_array = json.loads("[" + date_keyword + "]")

# 新
keyword_array = util.parse_keyword_string_to_array(date_keyword)
```

**效益**：
- 統一錯誤處理
- 消除重複代碼
- 支援空字串防護

---

## 三、P1 優先級詳細說明

### 3.1 `get_date_select_config(config_dict)` - 短期實作

**問題**：30+ 處重複的日期設定讀取區塊

**現況重複代碼**：
```python
if not config_dict["date_auto_select"]["enable"]:
    return False
auto_select_mode = config_dict["date_auto_select"]["mode"]
date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
date_auto_fallback = config_dict.get('date_auto_fallback', False)
```

**建議實作**：
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

### 3.2 `match_keyword_with_text()` - 短期實作

**問題**：11+ 處重複的 AND/OR 匹配邏輯

**建議實作**：見 `04-keyword-processing-patterns.md`

---

## 四、風險評估與緩解策略

### 低風險項目（P0）

| 項目 | 風險 | 緩解策略 |
|------|------|---------|
| `get_debug_mode()` | 幾乎無 | 直接替換 |
| `parse_keyword_string_to_array()` | 低 | 保持相同輸出格式 |

### 中風險項目（P1）

| 項目 | 風險 | 緩解策略 |
|------|------|---------|
| `get_date_select_config()` | 設定結構變更 | 返回 dict 保持彈性 |
| `match_keyword_with_text()` | 匹配邏輯差異 | 完整單元測試 |

### 高風險項目（P3）

| 項目 | 風險 | 緩解策略 |
|------|------|---------|
| `ConfigHelper` 類別 | 全平台影響 | 漸進式遷移 |

---

## 五、實作順序建議

### 第一週：P0 項目

1. 新增 `get_debug_mode()` 到 util.py
2. 替換 10 個核心函式（測試驗證）
3. 新增 `parse_keyword_string_to_array()` 到 util.py
4. 替換 5 個核心函式（測試驗證）

### 第二週：P0 完成 + P1 開始

5. 完成剩餘 P0 替換（70+ 處）
6. 新增 `get_date_select_config()` 到 util.py
7. 新增 `get_area_select_config()` 到 util.py
8. 替換 10 個核心函式（測試驗證）

### 第三週：P1 完成

9. 完成剩餘 P1 替換
10. 新增 `match_keyword_with_text()` 到 util.py
11. 全平台測試驗證

---

## 六、可能需要更新的文件

根據分析結果，以下文件可能需要更新：

### docs/03-mechanisms/

- `04-date-selection.md` - 新增 config 讀取標準
- `05-area-selection.md` - 新增 config 讀取標準
- `README.md` - 新增關鍵字解析標準

### docs/02-development/

- `structure.md` - 新增 util 函式說明
- `coding_templates.md` - 更新範本使用新函式

### docs/06-api-reference/

- 可能需要新增 `util_api_guide.md`

---

## 七、測試策略

### 單元測試（必須）

```python
# test_util.py
def test_get_debug_mode():
    assert get_debug_mode({}) == False
    assert get_debug_mode({"advanced": {"verbose": True}}) == True
    assert get_debug_mode({"advanced": {}}) == False

def test_parse_keyword_string_to_array():
    assert parse_keyword_string_to_array("") == []
    assert parse_keyword_string_to_array('"VIP"') == ["VIP"]
    assert parse_keyword_string_to_array('"VIP","1樓"') == ["VIP", "1樓"]
```

### 整合測試（建議）

- 每個平台至少執行一次完整流程測試
- 驗證日期/區域選擇功能正常
- 驗證關鍵字匹配功能正常

---

## 八、結論

### 立即可執行

1. **`get_debug_mode()`** - 80+ 處，低風險，高效益
2. **`parse_keyword_string_to_array()`** - 25 處，低風險，高效益

### 短期可執行

3. **`get_date_select_config()`** - 30+ 處，中風險，高效益
4. **`get_area_select_config()`** - 25+ 處，中風險，高效益

### 總預估效益

- **節省代碼行數**：500+ 行
- **統一存取模式**：6 種 → 1 種
- **維護成本降低**：一處修改全域生效
