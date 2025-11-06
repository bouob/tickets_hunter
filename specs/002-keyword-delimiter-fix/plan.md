# 實作計畫：關鍵字分隔符號改善

**功能分支**：`002-keyword-delimiter-fix`
**建立日期**：2025-10-25
**狀態**：規劃中

---

## 摘要

針對 GitHub Issue #23 的關鍵字分隔符號問題，將逗號（`,`）改為分號（`;`）以避免與金額千位分隔符號衝突。此改善涵蓋所有平台（TixCraft、KKTIX、TicketPlus、iBon、KHAM）的日期與區域關鍵字處理邏輯。

**預計工作量**：2-4 小時
**風險等級**：低（僅修改關鍵字解析邏輯）
**向後相容性**：需要（提供警告訊息）

---

## 技術堆疊

### 語言與框架
- **Python 3.10+**
- **NoDriver**（主要）
- **Undetected ChromeDriver**（舊版）

### 相關模組
- `src/nodriver_tixcraft.py`：主要實作檔案
- `src/util.py`：工具函式
- `src/settings.json`：設定檔範本

### 測試工具
- 手動測試（實際平台）
- 單元測試（pytest，選用）

---

## 架構設計

### 1. 關鍵字解析層

#### 新增常數定義
```python
# src/util.py 或 src/nodriver_tixcraft.py 開頭
CONST_KEYWORD_DELIMITER = ';'  # 新分隔符號
CONST_KEYWORD_DELIMITER_OLD = ','  # 舊分隔符號（用於偵測）
```

#### 新增關鍵字解析函式
```python
def parse_keyword_string(keyword_str, config_dict):
    """
    解析關鍵字字串，支援分號分隔與 JSON 陣列格式

    Args:
        keyword_str: 關鍵字字串（例如："3,280;2,680" 或 ["3,280", "2,680"]）
        config_dict: 設定字典（用於取得 verbose 設定）

    Returns:
        list: 關鍵字陣列
    """
    show_debug = config_dict["advanced"].get("verbose", False)

    # 情況 1：已經是 list（JSON 陣列格式）
    if isinstance(keyword_str, list):
        return keyword_str

    # 情況 2：空字串
    if not keyword_str or not keyword_str.strip():
        return []

    # 情況 3：包含分號（新格式）
    if CONST_KEYWORD_DELIMITER in keyword_str:
        return [kw.strip() for kw in keyword_str.split(CONST_KEYWORD_DELIMITER) if kw.strip()]

    # 情況 4：包含逗號但無分號（舊格式，顯示警告）
    if CONST_KEYWORD_DELIMITER_OLD in keyword_str:
        if show_debug:
            print(f"[WARNING] 偵測到舊格式的關鍵字設定")
            print(f"[WARNING] 當前設定: \"{keyword_str}\"")
            print(f"[WARNING] 建議格式: \"{keyword_str.replace(',', ';')}\"")
            print(f"[WARNING] 或使用 JSON 陣列: {json.dumps([kw.strip() for kw in keyword_str.split(',') if kw.strip()])}")
        return [kw.strip() for kw in keyword_str.split(CONST_KEYWORD_DELIMITER_OLD) if kw.strip()]

    # 情況 5：單一關鍵字（無分隔符號）
    return [keyword_str.strip()]
```

---

### 2. 平台整合層

#### 修改位置

##### A. TixCraft（參考標準實作）
**檔案**：`src/nodriver_tixcraft.py`
**函式**：`nodriver_tixcraft_area_auto_select`（行 2455）

**當前邏輯**：
```python
area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
# ...
try:
    area_keyword_array = json.loads("[" + area_keyword + "]")
except:
    area_keyword_array = []
```

**修改後邏輯**：
```python
area_keyword = config_dict["area_auto_select"]["area_keyword"]
area_keyword_array = parse_keyword_string(area_keyword, config_dict)
```

##### B. TicketPlus
**檔案**：`src/nodriver_tixcraft.py`
**函式 1**：`nodriver_ticketplus_unified_select`（行 4079）
**函式 2**：`nodriver_ticketplus_order_expansion_auto_select`（行 4631）

**當前邏輯**（函式 1，行 4117）：
```javascript
const keywordArray = keyword.split(' ');  // JavaScript 中
```

**修改後邏輯**：
```python
# Python 端先解析，再傳遞到 JavaScript
area_keyword_array = parse_keyword_string(area_keyword, config_dict)
area_keyword_item = area_keyword_array[0] if area_keyword_array else ""
```

##### C. KKTIX
**檔案**：`src/nodriver_tixcraft.py`
**函式**：`nodriver_kktix_travel_price_list`（行 680）

**當前邏輯**：
```python
# 需要檢查當前實作
```

**修改後邏輯**：
```python
kktix_area_keyword_array = parse_keyword_string(kktix_area_keyword, config_dict)
```

##### D. iBon
**檔案**：`src/nodriver_tixcraft.py`
**函式**：相關區域選擇函式（需檢查）

---

### 3. 設定層

#### settings.json 格式更新

**舊格式**：
```json
{
  "area_auto_select": {
    "area_keyword": "3,280,2,680"
  }
}
```

**新格式（方案 1：分號）**：
```json
{
  "area_auto_select": {
    "area_keyword": "3,280;2,680"
  }
}
```

**新格式（方案 2：JSON 陣列）**：
```json
{
  "area_auto_select": {
    "area_keyword": ["3,280", "2,680"]
  }
}
```

---

## 實作順序

### Phase 1：基礎設施（30 分鐘）
1. 在 `src/util.py` 或 `src/nodriver_tixcraft.py` 開頭定義常數
2. 實作 `parse_keyword_string` 函式
3. 撰寫單元測試（選用）

### Phase 2：平台整合（1-2 小時）
1. 修改 TixCraft 關鍵字解析（行 2455-2492）
2. 修改 TicketPlus 關鍵字解析（行 4079-4278）
3. 修改 KKTIX 關鍵字解析（行 680+）
4. 修改 iBon 關鍵字解析（需檢查）
5. 修改 KHAM 關鍵字解析（需檢查）

### Phase 3：文件更新（30 分鐘）
1. 更新 README.md
2. 更新 docs/01-getting-started/setup.md
3. 更新 specs/001-ticket-automation-system/contracts/config-schema.md
4. 更新 specs/001-ticket-automation-system/quickstart.md

### Phase 4：測試與驗證（30-60 分鐘）
1. 測試新格式（分號）
2. 測試 JSON 陣列格式
3. 測試舊格式（驗證警告訊息）
4. 每個平台至少測試一次

---

## 測試策略

### 單元測試範例

```python
def test_parse_keyword_string():
    config = {"advanced": {"verbose": False}}

    # 測試新格式（分號）
    assert parse_keyword_string("3,280;2,680", config) == ["3,280", "2,680"]

    # 測試 JSON 陣列
    assert parse_keyword_string(["3,280", "2,680"], config) == ["3,280", "2,680"]

    # 測試舊格式（逗號）
    assert parse_keyword_string("A區,B區", config) == ["A區", "B區"]

    # 測試單一關鍵字
    assert parse_keyword_string("3,280", config) == ["3,280"]

    # 測試空字串
    assert parse_keyword_string("", config) == []
    assert parse_keyword_string("  ", config) == []
```

### 整合測試

**測試 A：TicketPlus 價格關鍵字**
```json
{
  "homepage": "https://ticketplus.com.tw/activity/077604571cf54a0abfd1541fed0eaa05",
  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "area_keyword": "3,280;2,680"
  }
}
```
**預期結果**：先嘗試匹配「3,280」，若無則嘗試「2,680」

**測試 B：TixCraft 區域關鍵字**
```json
{
  "homepage": "https://tixcraft.com/activity/detail/...",
  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "area_keyword": "搖滾A區;搖滾B區"
  }
}
```
**預期結果**：先嘗試匹配「搖滾A區」，若無則嘗試「搖滾B區」

---

## 風險評估

### 低風險
- ✅ 僅修改關鍵字解析邏輯
- ✅ 不影響其他功能模組
- ✅ 向後相容性良好

### 需注意事項
- ⚠️ 測試時需確認所有平台都正確使用新解析函式
- ⚠️ 文件更新必須完整，避免使用者困惑
- ⚠️ 警告訊息需清楚明瞭

---

## 向後相容性策略

### 階段 1：軟性遷移（目前版本）
- 舊格式仍可運作
- 顯示警告訊息建議更新
- 提供清楚的新格式範例

### 階段 2：強制遷移（未來版本，選用）
- 舊格式觸發錯誤
- 停止執行並要求使用者更新設定

---

## 文件更新清單

1. **README.md**
   - 更新關鍵字範例
   - 新增遷移指引

2. **docs/01-getting-started/setup.md**
   - 更新設定檔範例
   - 說明新分隔符號用法

3. **specs/001-ticket-automation-system/contracts/config-schema.md**
   - 更新 area_keyword 描述
   - 更新 date_keyword 描述
   - 更新 keyword_exclude 描述
   - 新增範例

4. **specs/001-ticket-automation-system/quickstart.md**
   - 更新所有平台的設定範例

5. **CHANGELOG.md**
   - 新增版本更新記錄
   - 標註為 Breaking Change（如果強制遷移）

---

## 成功標準驗證

### SC-001：關鍵字正確解析
- [ ] 分號分隔的關鍵字 100% 正確解析
- [ ] JSON 陣列格式 100% 正確解析
- [ ] 單元測試通過（10+ 測試案例）

### SC-002：平台相容性
- [ ] TixCraft 測試通過
- [ ] KKTIX 測試通過
- [ ] TicketPlus 測試通過
- [ ] iBon 測試通過
- [ ] KHAM 測試通過

### SC-003：向後相容性
- [ ] 舊格式觸發警告訊息
- [ ] 舊格式仍可運作
- [ ] 警告訊息包含正確的新格式範例

### SC-004：文件完整性
- [ ] 所有文件使用新格式
- [ ] grep 搜尋無殘留舊格式範例
- [ ] CHANGELOG.md 已更新

---

## 參考資料

- **相關 Issue**：GitHub Issue #23
- **憲法原則**：`.specify/memory/constitution.md`（第 II 條：資料結構優先）
- **TixCraft 參考實作**：`src/nodriver_tixcraft.py:2455-2670`
- **設定檔 Schema**：`specs/001-ticket-automation-system/contracts/config-schema.md`
