# 資料模型：關鍵字優先選擇與條件式自動遞補

**功能**: 關鍵字優先選擇與條件式自動遞補
**建立日期**: 2025-10-31
**版本**: 1.0

## 概述

本功能主要涉及設定檔（settings.json）的擴展，新增兩個布林欄位以控制遞補行為。此外，需定義關鍵字匹配與遞補的狀態流轉邏輯。

---

## 核心實體

### 1. Configuration（設定檔）

**用途**: 儲存使用者的搶票偏好設定，包含關鍵字清單、遞補開關、排序規則等。

**欄位**:

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `date_keyword` | String | 否 | `""` | 日期關鍵字清單，以分號分隔（如 "11/16;11/17;11/18"） |
| `area_keyword` | String | 否 | `""` | 區域關鍵字清單，以分號分隔（如 "搖滾區A;VIP區"） |
| `date_auto_fallback` | Boolean | 否 | `false` | **新增欄位** - 當所有日期關鍵字都未匹配時，是否觸發自動遞補 |
| `area_auto_fallback` | Boolean | 否 | `false` | **新增欄位** - 當所有區域關鍵字都未匹配時，是否觸發自動遞補 |
| `date_select_order` | String | 否 | `"from_top_to_bottom"` | 日期遞補時的排序規則（可選值：`"from_top_to_bottom"`, `"from_bottom_to_top"`, `"random"`） |
| `area_select_order` | String | 否 | `"from_top_to_bottom"` | 區域遞補時的排序規則（可選值：`"from_top_to_bottom"`, `"from_bottom_to_top"`, `"random"`） |

**驗證規則**:

1. `date_keyword` 和 `area_keyword` 若非空字串，必須為分號分隔的格式
2. `date_auto_fallback` 和 `area_auto_fallback` 必須為布林值（true/false）
3. `date_select_order` 和 `area_select_order` 必須為合法的排序規則字串

**關聯**:

- Configuration 是獨立實體，不直接關聯其他實體
- 由 settings.py / settings_old.py 負責載入與儲存

---

### 2. KeywordMatchResult（關鍵字匹配結果）

**用途**: 表示關鍵字匹配過程的結果狀態。

**欄位**:

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `matched` | Boolean | 是 | 是否有關鍵字匹配成功 |
| `matched_keyword` | String/Null | 否 | 匹配成功的關鍵字內容（若 `matched=false` 則為 null） |
| `matched_index` | Integer/Null | 否 | 匹配成功的關鍵字索引（從 0 開始，若 `matched=false` 則為 null） |
| `selected_option` | String/Null | 否 | 最終選擇的選項內容（日期或區域的文字描述） |
| `is_fallback` | Boolean | 是 | 最終選擇是否來自遞補邏輯 |

**狀態定義**:

1. **完全匹配（Full Match）**:
   - `matched = true`
   - `matched_keyword` 和 `matched_index` 不為 null
   - `selected_option` = 匹配的選項
   - `is_fallback = false`

2. **遞補選擇（Fallback Selection）**:
   - `matched = false`
   - `matched_keyword` 和 `matched_index` = null
   - `selected_option` = 根據排序規則選擇的選項
   - `is_fallback = true`

3. **未選擇（No Selection）**:
   - `matched = false`
   - `matched_keyword` 和 `matched_index` = null
   - `selected_option` = null
   - `is_fallback = false`（遞補功能停用）

**驗證規則**:

1. 若 `matched = true`，則 `matched_keyword` 和 `matched_index` 不得為 null
2. 若 `matched = false` 且 `is_fallback = true`，則 `selected_option` 不得為 null
3. 若 `matched = false` 且 `is_fallback = false`，則 `selected_option` 必須為 null

---

## 狀態轉換圖

### 關鍵字匹配與遞補流程

```
[Start] 開始關鍵字匹配
   |
   v
[Iterate Keywords] 依序檢查關鍵字清單
   |
   |---> [Keyword Matched?] 第 N 個關鍵字匹配？
   |        |
   |        |--(Yes)--> [State: Full Match] 立即選擇，停止檢查
   |        |              - matched = true
   |        |              - matched_index = N
   |        |              - is_fallback = false
   |        |              |
   |        |              v
   |        |           [End] 完成選擇
   |        |
   |        |--(No)--> [More Keywords?] 還有更多關鍵字？
   |                      |
   |                      |--(Yes)--> 繼續迭代（回到 Iterate Keywords）
   |                      |
   |                      |--(No)--> [All Keywords Failed] 所有關鍵字都未匹配
   |                                    |
   |                                    v
   |                                 [Check Fallback Flag] 檢查遞補開關
   |                                    |
   |                                    |--(true)--> [State: Fallback Selection] 觸發遞補邏輯
   |                                    |              - matched = false
   |                                    |              - is_fallback = true
   |                                    |              - 根據 select_order 選擇
   |                                    |              |
   |                                    |              v
   |                                    |           [End] 完成選擇（遞補）
   |                                    |
   |                                    |--(false)--> [State: No Selection] 不執行遞補
   |                                                   - matched = false
   |                                                   - is_fallback = false
   |                                                   - selected_option = null
   |                                                   |
   |                                                   v
   |                                                [End] 等待處理
```

---

## 資料不變性約束

### 約束 1：關鍵字順序不可變

**描述**: 使用者設定的關鍵字清單順序代表優先順序，系統不得任意調整順序。

**驗證方式**: 關鍵字解析後應保持原始順序，第一個關鍵字索引為 0，第二個為 1，以此類推。

---

### 約束 2：遞補開關的語意一致性

**描述**: `date_auto_fallback` 和 `area_auto_fallback` 僅控制「全部未匹配」時的遞補行為，不影響關鍵字匹配邏輯。

**驗證方式**: 即使遞補開關為 false，關鍵字匹配邏輯仍應正常執行。遞補開關僅在所有關鍵字都未匹配時檢查。

---

### 約束 3：狀態轉換的單向性

**描述**: 一旦進入 "Full Match" 狀態，不得回退或進入其他狀態。

**驗證方式**: 匹配成功後立即返回結果，不再執行後續檢查或遞補邏輯。

---

## 設定檔範例

### 範例 1：啟用遞補（預設行為）

```json
{
  "homepage": "https://tixcraft.com",
  "date_keyword": "11/16;11/17;11/18",
  "area_keyword": "搖滾區A;VIP區",
  "date_auto_fallback": true,
  "area_auto_fallback": true,
  "date_select_order": "from_top_to_bottom",
  "area_select_order": "from_top_to_bottom"
}
```

**行為說明**:
- 若 "11/16", "11/17", "11/18" 都不存在，則根據 `date_select_order` 自動選擇可用日期
- 若 "搖滾區A", "VIP區" 都不存在，則根據 `area_select_order` 自動選擇可用區域

---

### 範例 2：停用遞補（嚴格匹配模式）

```json
{
  "homepage": "https://tixcraft.com",
  "date_keyword": "11/16;11/17",
  "area_keyword": "搖滾區A",
  "date_auto_fallback": false,
  "area_auto_fallback": false,
  "date_select_order": "from_top_to_bottom",
  "area_select_order": "from_top_to_bottom"
}
```

**行為說明**:
- 若 "11/16", "11/17" 都不存在，系統不自動選擇任何日期，保持等待
- 若 "搖滾區A" 不存在，系統不自動選擇任何區域，保持等待

---

### 範例 3：混合模式（日期啟用遞補，區域停用遞補）

```json
{
  "homepage": "https://kktix.com",
  "date_keyword": "11/16",
  "area_keyword": "VIP區;一般區",
  "date_auto_fallback": true,
  "area_auto_fallback": false,
  "date_select_order": "from_top_to_bottom",
  "area_select_order": "random"
}
```

**行為說明**:
- 若 "11/16" 不存在，則自動選擇第一個可用日期
- 若 "VIP區", "一般區" 都不存在，則不自動選擇區域（嚴格模式）

---

## 遷移策略

### 舊版設定檔相容性

**問題**: 舊版設定檔沒有 `date_auto_fallback` 和 `area_auto_fallback` 欄位。

**解決方案**:

1. **載入時檢查**:
   ```python
   if 'date_auto_fallback' not in config:
       config['date_auto_fallback'] = False  # 預設嚴格模式

   if 'area_auto_fallback' not in config:
       config['area_auto_fallback'] = False  # 預設嚴格模式
   ```

2. **儲存時保留**:
   - 新版本儲存設定檔時，必須包含這兩個欄位
   - 確保下次載入時不需要再次補充預設值

**驗證**:
- 舊設定檔升級後，啟用嚴格模式（因為預設值為 false），僅選擇關鍵字匹配的選項，避免誤搶不想要的場次

---

## 與其他模組的介面

### settings.py / settings_old.py

**職責**: 負責設定檔的載入、驗證、儲存。

**必須實作的功能**:

1. **載入時提供預設值**:
   - 若 `date_auto_fallback` 不存在，預設為 `false`
   - 若 `area_auto_fallback` 不存在，預設為 `false`

2. **驗證布林類型**:
   - 確保這兩個欄位為布林值，不接受字串 "true"/"false"

3. **儲存時同步**:
   - 確保設定頁面（settings.html）修改的值正確寫入設定檔

### nodriver_tixcraft.py

**職責**: 實作日期與區域選擇的核心邏輯。

**必須實作的功能**:

1. **關鍵字優先匹配**:
   - 依序檢查關鍵字清單，第一個匹配立即選擇並返回

2. **條件式遞補**:
   - 所有關鍵字都未匹配時，檢查對應的遞補開關
   - 若開關為 true，根據 select_order 執行遞補邏輯
   - 若開關為 false，返回 null 或進入錯誤處理流程

3. **日誌輸出**:
   - 記錄關鍵字檢查過程（英文訊息）
   - 記錄遞補觸發或停用的狀態

### settings.html

**職責**: 提供 UI 介面讓使用者調整遞補開關。

**必須實作的功能**:

1. **新增核取方塊**:
   - 在「日期自動點選」區塊新增「日期自動遞補」核取方塊（對應 `date_auto_fallback`）
   - 在「區域自動點選」區塊新增「區域自動遞補」核取方塊（對應 `area_auto_fallback`）

2. **預設狀態**:
   - 首次載入時，兩個核取方塊應為未勾選狀態（預設 false）

3. **同步儲存**:
   - 勾選/取消勾選後，點擊「儲存」按鈕應正確寫入設定檔

---

## 測試資料範例

### 測試案例 1：第一個關鍵字匹配

**輸入**:
- 關鍵字清單：`["11/16", "11/17", "11/18"]`
- 頁面可用選項：`["11/16", "11/19"]`
- `date_auto_fallback`: `true`

**預期輸出**:
```json
{
  "matched": true,
  "matched_keyword": "11/16",
  "matched_index": 0,
  "selected_option": "11/16",
  "is_fallback": false
}
```

---

### 測試案例 2：第二個關鍵字匹配

**輸入**:
- 關鍵字清單：`["11/16", "11/17", "11/18"]`
- 頁面可用選項：`["11/17", "11/19"]`
- `date_auto_fallback`: `true`

**預期輸出**:
```json
{
  "matched": true,
  "matched_keyword": "11/17",
  "matched_index": 1,
  "selected_option": "11/17",
  "is_fallback": false
}
```

---

### 測試案例 3：全部未匹配，遞補啟用

**輸入**:
- 關鍵字清單：`["11/16", "11/17"]`
- 頁面可用選項：`["11/18", "11/19"]`
- `date_auto_fallback`: `true`
- `date_select_order`: `"from_top_to_bottom"`

**預期輸出**:
```json
{
  "matched": false,
  "matched_keyword": null,
  "matched_index": null,
  "selected_option": "11/18",
  "is_fallback": true
}
```

---

### 測試案例 4：全部未匹配，遞補停用

**輸入**:
- 關鍵字清單：`["11/16", "11/17"]`
- 頁面可用選項：`["11/18", "11/19"]`
- `date_auto_fallback`: `false`

**預期輸出**:
```json
{
  "matched": false,
  "matched_keyword": null,
  "matched_index": null,
  "selected_option": null,
  "is_fallback": false
}
```

---

## 總結

本資料模型定義了關鍵字優先選擇與條件式遞補功能的核心實體、欄位、驗證規則及狀態轉換邏輯。所有設計決策皆基於「簡潔性」、「向後相容性」及「符合需求」三大原則。下一階段將根據此資料模型產生 API contracts。
