# API 合約：設定檔結構

**功能**: 關鍵字優先選擇與條件式自動遞補
**建立日期**: 2025-10-31
**版本**: 1.0

## 概述

本合約定義關鍵字優先選擇與條件式自動遞補功能所需的設定檔結構擴展。規範新增欄位的結構、類型、驗證規則及預設值。

---

## 設定檔結構擴展

### 新增頂層欄位

#### 1. `date_auto_fallback`

**類型**: `boolean`

**用途**: 控制當所有日期關鍵字都未匹配時，是否觸發自動遞補選擇。

**預設值**: `false`

**驗證規則**:
- 必須為布林值（`true` 或 `false`）
- 不可為 `null` 或其他類型

**行為**:
- `true`: 所有日期關鍵字都未匹配時，系統根據 `date_select_order` 自動選擇可用日期
- `false`: 所有日期關鍵字都未匹配時，系統不自動選擇任何日期，等待手動介入（嚴格模式，預設）

---

#### 2. `area_auto_fallback`

**類型**: `boolean`

**用途**: 控制當所有區域關鍵字都未匹配時，是否觸發自動遞補選擇。

**預設值**: `false`

**驗證規則**:
- 必須為布林值（`true` 或 `false`）
- 不可為 `null` 或其他類型

**行為**:
- `true`: 所有區域關鍵字都未匹配時，系統根據 `area_select_order` 自動選擇可用區域
- `false`: 所有區域關鍵字都未匹配時，系統不自動選擇任何區域，等待手動介入

---

## 完整設定範例

### 範例 1：預設行為（遞補啟用）

```json
{
  "homepage": "https://tixcraft.com",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16;11/17;11/18",
    "mode": "from_top_to_bottom"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "搖滾區A;VIP區",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": false,
  "area_auto_fallback": false
}
```

**預期行為**:
- 系統依序檢查日期關鍵字："11/16" → "11/17" → "11/18"
- 若 "11/16" 匹配，立即選擇並停止
- 若三個關鍵字都失敗，自動選擇第一個可用日期（由上而下）
- 區域關鍵字邏輯相同

---

### 範例 2：嚴格模式（遞補停用）

```json
{
  "homepage": "https://tixcraft.com",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16;11/17",
    "mode": "from_top_to_bottom"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "搖滾區A",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": false,
  "area_auto_fallback": false
}
```

**預期行為**:
- 系統依序檢查日期關鍵字："11/16" → "11/17"
- 若 "11/16" 匹配，立即選擇並停止
- 若兩個關鍵字都失敗，**不自動選擇任何日期**，等待使用者操作
- 區域關鍵字邏輯相同

---

### 範例 3：混合模式（日期遞補啟用，區域嚴格模式）

```json
{
  "homepage": "https://kktix.com",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16",
    "mode": "from_top_to_bottom"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP區;一般區",
    "mode": "random"
  },
  "date_auto_fallback": true,
  "area_auto_fallback": false
}
```

**預期行為**:
- 若 "11/16" 日期關鍵字失敗，自動選擇第一個可用日期
- 若兩個區域關鍵字（"VIP區"、"一般區"）都失敗，**不自動選擇任何區域**

---

## 與既有欄位的關係

### 相關欄位（無需變更）

新增的布林欄位與既有設定協同運作：

| 既有欄位 | 用途 | 關係 |
|---------|------|------|
| `date_auto_select.enable` | 日期自動選擇的主開關 | 必須為 `true` 才會進行關鍵字檢查 |
| `date_auto_select.date_keyword` | 分號分隔的日期關鍵字 | 定義匹配的優先順序 |
| `date_auto_select.mode` | 遞補時的選擇順序 | 僅在 `date_auto_fallback=true` 且所有關鍵字都失敗時使用 |
| `area_auto_select.enable` | 區域自動選擇的主開關 | 必須為 `true` 才會進行關鍵字檢查 |
| `area_auto_select.area_keyword` | 分號分隔的區域關鍵字 | 定義匹配的優先順序 |
| `area_auto_select.mode` | 遞補時的選擇順序 | 僅在 `area_auto_fallback=true` 且所有關鍵字都失敗時使用 |

### 互動邏輯

```
[主開關] date_auto_select.enable = true/false
    |
    |--(false)--> 完全不進行日期選擇
    |
    |--(true)--> [關鍵字匹配] 依序檢查 date_keyword
                    |
                    |--(匹配成功)--> 立即選擇，停止檢查
                    |
                    |--(全部失敗)--> [遞補開關] date_auto_fallback
                                          |
                                          |--(true)--> 使用 date_select_order 進行遞補
                                          |
                                          |--(false)--> 不選擇，等待
```

---

## 向後相容性 / 遷移策略

### 情境：首次執行或重置

**條件**: `settings.json` 不存在，或使用者點擊「還原預設值」按鈕。

**行為**:
1. 系統呼叫 `get_default_config()` 函數
2. 產生包含所有預設值的完整設定字典
3. 寫入 `settings.json`

**新欄位的預設值**:
```python
config_dict["date_auto_fallback"] = True
config_dict["area_auto_fallback"] = True
```

### 情境：既有使用者（舊版設定檔）

**條件**: 使用者擁有不包含新欄位的既有 `settings.json`。

**行為**:
1. 核心搶票模組照常載入設定檔
2. 存取新欄位時使用安全存取模式：
   ```python
   date_auto_fallback = config_dict.get('date_auto_fallback', False)
   area_auto_fallback = config_dict.get('area_auto_fallback', False)
   ```
3. 下次使用者透過 UI 儲存設定時，完整設定（包含新欄位）會被寫入

**無破壞性變更**:
- 預設值 `false` 啟用嚴格模式（關鍵字失敗時不自動遞補，避免誤搶不想要的場次）
- 舊版設定檔可正常運作，不會產生錯誤

---

## 實作需求

### 針對 `settings.py` / `settings_old.py`

**1. 更新 `get_default_config()` 函數**:

在函數中新增以下程式碼：

```python
def get_default_config():
    config_dict = {}

    # ... 既有欄位 ...

    # 新增：關鍵字優先遞補功能的欄位
    config_dict["date_auto_fallback"] = False
    config_dict["area_auto_fallback"] = False

    return config_dict
```

**位置**: 在既有的日期/區域自動選擇設定之後，進階設定之前。

---

**2. 無需變更驗證邏輯**:

UI（settings.html）會自動將核取方塊值處理為布林類型，無需額外驗證邏輯。

---

### 針對 `nodriver_tixcraft.py` / `chrome_tixcraft.py`

**1. 安全存取模式**:

存取新設定欄位時，永遠使用 `.get()` 並提供預設值：

```python
# 日期選擇邏輯範例
date_auto_fallback = config_dict.get('date_auto_fallback', True)

if date_auto_fallback:
    # 根據 date_select_order 觸發遞補選擇
    selected_date = select_date_by_order(available_dates, date_select_order)
else:
    # 不遞補，返回 None 或記錄警告
    print("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
    selected_date = None
```

**2. 日誌訊息（英文）**:

```python
# 當所有關鍵字都失敗
print("[DATE KEYWORD] All keywords failed to match")

# 檢查遞補開關
if date_auto_fallback:
    print(f"[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
    print(f"[DATE FALLBACK] Selecting available date based on date_select_order='{date_select_order}'")
    # ... 執行遞補選擇 ...
    print(f"[DATE SELECT] Selected date: {selected_date} (fallback)")
else:
    print("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
    print("[DATE SELECT] Waiting for manual intervention")
```

---

### 針對 `settings.html`

**1. 在對應區塊新增核取方塊**:

**日期自動遞補核取方塊**（在「日期自動點選」區塊內）:

```html
<div class="form-check">
  <input class="form-check-input" type="checkbox" id="date_auto_fallback">
  <label class="form-check-label" for="date_auto_fallback">
    日期自動遞補
  </label>
  <small class="form-text text-muted">
    當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉）
  </small>
</div>
```

**區域自動遞補核取方塊**（在「區域自動點選」區塊內）:

```html
<div class="form-check">
  <input class="form-check-input" type="checkbox" id="area_auto_fallback">
  <label class="form-check-label" for="area_auto_fallback">
    區域自動遞補
  </label>
  <small class="form-text text-muted">
    當所有區域關鍵字都未匹配時，是否自動選擇可用區域
  </small>
</div>
```

**2. JavaScript 載入/儲存邏輯**:

**從設定載入**:
```javascript
// 從設定載入核取方塊狀態（預設 false）
document.getElementById('date_auto_fallback').checked =
  config.date_auto_fallback !== undefined ? config.date_auto_fallback : false;

document.getElementById('area_auto_fallback').checked =
  config.area_auto_fallback !== undefined ? config.area_auto_fallback : false;
```

**儲存至設定**:
```javascript
// 儲存核取方塊狀態至設定
config.date_auto_fallback = document.getElementById('date_auto_fallback').checked;
config.area_auto_fallback = document.getElementById('area_auto_fallback').checked;
```

---

## 驗證規則總結

### 類型驗證

| 欄位 | 類型 | 允許的值 | 無效範例 |
|-----|------|---------|---------|
| `date_auto_fallback` | boolean | `true`, `false` | `"true"` (字串), `1` (數字), `null` |
| `area_auto_fallback` | boolean | `true`, `false` | `"false"` (字串), `0` (數字), `null` |

### 業務邏輯驗證

1. **主開關相依性**:
   - `date_auto_fallback` 僅在 `date_auto_select.enable = true` 時生效
   - `area_auto_fallback` 僅在 `area_auto_select.enable = true` 時生效

2. **關鍵字清單相依性**:
   - 遞補邏輯僅在關鍵字清單非空且全部失敗時觸發
   - 若關鍵字清單為空，直接套用既有的 `mode` 選擇邏輯

3. **無跨欄位衝突**:
   - `date_auto_fallback` 和 `area_auto_fallback` 各自獨立
   - 可獨立啟用/停用，互不影響

---

## 邊界情境

### 情境 1：空白關鍵字清單

**設定**:
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": false
}
```

**行為**:
- 因關鍵字清單為空，系統跳過關鍵字匹配
- 直接使用 `mode` 選擇日期
- `date_auto_fallback` 開關在此情境下**被忽略**

---

### 情境 2：主開關停用

**設定**:
```json
{
  "date_auto_select": {
    "enable": false,
    "date_keyword": "11/16",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": true
}
```

**行為**:
- 完全不進行日期選擇（主開關關閉）
- `date_auto_fallback` 開關在此情境下**被忽略**

---

### 情境 3：舊版設定檔缺少欄位

**設定**（舊版）:
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16",
    "mode": "from_top_to_bottom"
  }
}
```

**行為**:
- 程式碼使用 `config_dict.get('date_auto_fallback', False)` → 返回 `False`
- 系統啟用嚴格模式（僅選擇關鍵字匹配的選項，避免誤搶）

---

## 測試需求

### 單元測試案例

**測試 1：預設值**
- 驗證 `get_default_config()` 包含 `date_auto_fallback=false` 和 `area_auto_fallback=false`

**測試 2：安全存取**
- 載入不含新欄位的設定
- 驗證 `.get('date_auto_fallback', False)` 返回 `False`

**測試 3：UI 核取方塊狀態**
- 載入 `date_auto_fallback=false` 的設定
- 驗證核取方塊未勾選
- 切換核取方塊並儲存
- 驗證設定檔包含 `"date_auto_fallback": true`（勾選後）

**測試 4：遞補行為**
- 設定 `date_auto_fallback=true`，所有關鍵字失敗
- 驗證遞補選擇發生
- 設定 `date_auto_fallback=false`，所有關鍵字失敗
- 驗證不發生選擇

---

## 總結

本合約定義關鍵字優先選擇與條件式自動遞補功能的設定檔結構擴展。核心設計決策：

1. **兩個獨立的布林欄位**於頂層
2. **預設值 `false`**（嚴格模式）以確保使用者安全（避免誤搶不想要的場次）
3. **安全存取模式** `.get()` 供既有使用者使用
4. **無破壞性變更**於既有設定檔結構
5. **明確的驗證規則**與邊界情境處理

所有實作模組必須遵循本合約以確保一致性與正確性。
