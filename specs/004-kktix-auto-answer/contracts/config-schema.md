# 配置 Schema：KKTIX 自動答題功能

**日期**：2025-11-03
**分支**：`004-kktix-auto-answer`
**目的**：定義 `settings.json` 中與自動答題功能相關的配置項目

---

## JSON Schema 定義

### 完整 Schema（針對本功能）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "KKTIX Auto-Answer Configuration",
  "description": "配置 KKTIX 自動答題功能的行為",
  "type": "object",
  "properties": {
    "advanced": {
      "type": "object",
      "properties": {
        "auto_guess_options": {
          "type": "boolean",
          "default": false,
          "description": "是否啟用自動推測答案功能（當無用戶預定義答案時）"
        },
        "user_guess_string": {
          "type": "string",
          "default": "",
          "pattern": "^[^\\r\\n]*$",
          "maxLength": 1000,
          "description": "用戶預定義的答案字串（逗號分隔，例如：\"答案A,答案B,答案C\"）"
        },
        "verbose": {
          "type": "boolean",
          "default": false,
          "description": "是否輸出詳細 Debug 資訊（包含問題文本、答案清單、失敗記錄）"
        }
      },
      "required": ["auto_guess_options", "verbose"]
    }
  },
  "required": ["advanced"]
}
```

---

## 配置項目詳細說明

### 1. `auto_guess_options`

**類型**：`boolean`
**預設值**：`false`
**必填**：✅

**描述**：
控制是否啟用自動推測答案功能。當啟用時，若 `user_guess_string` 為空或無匹配答案，系統會呼叫 `util.get_answer_list_from_question_string()` 自動從問題文本推測答案。

**使用時機**：
- **啟用**（`true`）：使用者希望系統自動處理驗證問題，無需手動輸入答案
- **禁用**（`false`，預設）：使用者希望手動輸入答案，或僅使用預定義答案

**影響範圍**：
- 影響 `nodriver_kktix_reg_captcha()` 函數中的答案產生邏輯（line 1206-1208）
- 不影響 `user_guess_string` 的優先權（用戶定義答案始終優先）

**風險提示**：
- 啟用後可能答錯驗證問題（若推測邏輯無法處理特定問題類型）
- 建議先在測試環境中驗證推測準確率後再啟用

**範例**：
```json
{
  "advanced": {
    "auto_guess_options": true
  }
}
```

---

### 2. `user_guess_string`

**類型**：`string`
**預設值**：`""`（空字串）
**必填**：❌

**描述**：
用戶預先定義的答案字串。支援多個答案，以逗號（`,`）分隔。系統會優先使用此欄位的答案，若全部失敗才會嘗試自動推測（需啟用 `auto_guess_options`）。

**格式要求**：
- **分隔符**：逗號（`,`）
- **禁止字元**：換行符（`\r`、`\n`）
- **最大長度**：1000 字元
- **範例**：`"答案A,答案B,答案C"`

**使用場景**：
1. **已知答案**：使用者事先知道驗證問題的正確答案
2. **多個候選答案**：使用者提供多個可能正確的答案（系統按順序嘗試）
3. **覆蓋自動推測**：即使啟用 `auto_guess_options`，此欄位的答案仍優先使用

**優先順序**：
```
user_guess_string (優先) > auto_guess_options (次要) > 不填寫 (手動)
```

**範例**：
```json
{
  "advanced": {
    "user_guess_string": "SUNSET,落日飛車,Sunset Rollercoaster"
  }
}
```

**空字串行為**：
- 若 `user_guess_string` 為空且 `auto_guess_options` 啟用，則自動推測
- 若 `user_guess_string` 為空且 `auto_guess_options` 禁用，則保留輸入框空白（需手動輸入）

---

### 3. `verbose`

**類型**：`boolean`
**預設值**：`false`
**必填**：✅

**描述**：
控制是否輸出詳細的 Debug 資訊至終端。啟用後，系統會輸出問題文本、推測答案清單、失敗記錄等資訊，方便使用者診斷問題。

**輸出內容**（當 `verbose = true` 時）：
```python
print("inferred_answer_string:", inferred_answer_string)
print("question_text:", question_text)
print("answer_list:", answer_list)
print("fail_list:", fail_list)
```

**範例輸出**：
```
inferred_answer_string: SUNSET
question_text: 落日飛車的英文團名是 _ _ _ _ _ _ Rollercoaster (請輸入六個半形「大寫」英文字)。
answer_list: ['SUNSET', 'Sunset Rollercoaster']
fail_list: []
```

**使用時機**：
- **開發測試**：驗證答案推測邏輯是否正確
- **問題診斷**：檢查為何答題失敗
- **日常使用**：建議禁用（減少終端輸出）

**範例**：
```json
{
  "advanced": {
    "verbose": true
  }
}
```

---

## 配置範例

### 範例 1：完全自動模式

```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "",
    "verbose": false
  }
}
```

**說明**：啟用自動推測，無預定義答案，不輸出 Debug 資訊。適合一般使用者。

---

### 範例 2：預定義答案優先模式

```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "SUNSET,落日飛車",
    "verbose": false
  }
}
```

**說明**：優先使用預定義答案 `["SUNSET", "落日飛車"]`，若全部失敗則自動推測其他答案。

---

### 範例 3：僅使用預定義答案模式

```json
{
  "advanced": {
    "auto_guess_options": false,
    "user_guess_string": "20250620,2025-06-20",
    "verbose": false
  }
}
```

**說明**：僅使用預定義答案，禁用自動推測。若答案錯誤則停止嘗試。

---

### 範例 4：Debug 模式

```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "測試答案",
    "verbose": true
  }
}
```

**說明**：啟用 Debug 輸出，方便檢查答題邏輯是否正確運作。

---

## 配置驗證規則

### 必填欄位驗證

```python
def validate_config(config_dict: dict) -> bool:
    """驗證配置是否符合 schema 要求"""
    required_fields = ["advanced"]
    for field in required_fields:
        if field not in config_dict:
            raise ValueError(f"Missing required field: {field}")

    advanced = config_dict["advanced"]
    required_advanced_fields = ["auto_guess_options", "verbose"]
    for field in required_advanced_fields:
        if field not in advanced:
            raise ValueError(f"Missing required field: advanced.{field}")

    return True
```

### 類型驗證

```python
def validate_types(config_dict: dict) -> bool:
    """驗證配置項目的資料類型"""
    advanced = config_dict["advanced"]

    if not isinstance(advanced["auto_guess_options"], bool):
        raise TypeError("auto_guess_options must be boolean")

    if "user_guess_string" in advanced and not isinstance(advanced["user_guess_string"], str):
        raise TypeError("user_guess_string must be string")

    if not isinstance(advanced["verbose"], bool):
        raise TypeError("verbose must be boolean")

    return True
```

### 格式驗證

```python
def validate_format(config_dict: dict) -> bool:
    """驗證配置項目的格式要求"""
    advanced = config_dict["advanced"]

    if "user_guess_string" in advanced:
        user_string = advanced["user_guess_string"]

        # 檢查是否包含換行符
        if '\r' in user_string or '\n' in user_string:
            raise ValueError("user_guess_string cannot contain newline characters")

        # 檢查長度
        if len(user_string) > 1000:
            raise ValueError("user_guess_string exceeds maximum length (1000 characters)")

    return True
```

---

## 配置讀取範例

### Python 實作

```python
def read_config(config_path: str = "src/settings.json") -> dict:
    """讀取並驗證配置檔案"""
    import json

    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)

    # 驗證配置
    validate_config(config_dict)
    validate_types(config_dict)
    validate_format(config_dict)

    return config_dict

def get_auto_guess_enabled(config_dict: dict) -> bool:
    """取得 auto_guess_options 配置值"""
    return config_dict.get("advanced", {}).get("auto_guess_options", False)

def get_user_answers(config_dict: dict) -> list[str]:
    """取得並解析 user_guess_string"""
    user_string = config_dict.get("advanced", {}).get("user_guess_string", "")
    if not user_string:
        return []

    # 分割逗號分隔的字串
    answers = [ans.strip() for ans in user_string.split(',')]
    # 移除空字串
    answers = [ans for ans in answers if ans]
    return answers
```

---

## 相容性考量

### 向後相容性

**現有配置**：
- 若現有 `settings.json` 未包含 `auto_guess_options`，則預設為 `false`
- 若現有 `settings.json` 未包含 `user_guess_string`，則預設為 `""`
- 若現有 `settings.json` 已有這些欄位，則使用現有值

**遷移策略**：
- 無需遷移腳本（預設值已涵蓋舊版配置）
- 使用者可選擇性啟用新功能

### 錯誤處理

**配置錯誤時的行為**：
1. **類型錯誤**：記錄警告並使用預設值
2. **格式錯誤**：記錄警告並忽略該欄位
3. **必填欄位缺失**：記錄錯誤並使用預設值

**範例**：
```python
try:
    auto_guess = config_dict["advanced"]["auto_guess_options"]
except KeyError:
    print("[WARNING] auto_guess_options not found, using default: False")
    auto_guess = False
```

---

## Schema 總結表

| 配置項目 | 類型 | 預設值 | 必填 | 描述 |
|---------|------|--------|------|------|
| `advanced.auto_guess_options` | `boolean` | `false` | ✅ | 啟用自動推測答案 |
| `advanced.user_guess_string` | `string` | `""` | ❌ | 用戶預定義答案（逗號分隔） |
| `advanced.verbose` | `boolean` | `false` | ✅ | 輸出 Debug 資訊 |

---

**版本**：1.0
**審查狀態**：待審查
**下一步**：產生 quickstart.md（快速開始指南）
