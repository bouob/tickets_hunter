# 函數簽章契約：KKTIX 自動答題功能

**日期**：2025-11-03
**分支**：`004-kktix-auto-answer`
**目的**：定義所有涉及函數的介面契約

---

## 核心函數

### 1. `nodriver_kktix_reg_captcha()` - 驗證碼處理主函數

**檔案**：`src/nodriver_tixcraft.py`
**行數**：1172-1350（約）
**修改範圍**：啟用 `auto_guess_options` 邏輯分支（line 1206-1208）

**函數簽章**：
```python
async def nodriver_kktix_reg_captcha(
    tab: nodriver.Tab,
    config_dict: dict,
    fail_list: list[str],
    registrationsNewApp_div: Optional[Any]
) -> tuple[list[str], bool, bool]:
    """
    處理 KKTIX 驗證碼問題（包含自動答題）

    Args:
        tab: NoDriver tab 物件
        config_dict: 配置字典（含 advanced.auto_guess_options）
        fail_list: 失敗答案清單
        registrationsNewApp_div: Angular 根元素（NoDriver 環境下不使用）

    Returns:
        tuple[list[str], bool, bool]: (fail_list, is_question_popup, button_clicked_in_captcha)
            - fail_list: 更新後的失敗答案清單
            - is_question_popup: 是否偵測到問題
            - button_clicked_in_captcha: 是否點擊了按鈕

    Raises:
        無（所有錯誤均捕獲並記錄）
    """
```

**修改點**：
- Line 1206-1208：啟用自動推測邏輯
  ```python
  if len(answer_list) == 0:
      if config_dict["advanced"]["auto_guess_options"]:
          answer_list = util.get_answer_list_from_question_string(None, question_text)
  ```

**前置條件**：
- `tab` 已載入 KKTIX 活動頁面
- `config_dict` 包含有效配置
- `fail_list` 為空清單或包含先前失敗的答案

**後置條件**：
- 若偵測到問題且有答案，則填寫答案至輸入框
- 失敗的答案已加入 `fail_list`
- 問題文本已寫入 `question.txt`

---

## 工具函數（複用自 `util.py`）

### 2. `util.get_answer_list_from_user_guess_string()` - 讀取用戶定義答案

**檔案**：`src/util.py`
**行數**：1465-1493

**函數簽章**：
```python
def get_answer_list_from_user_guess_string(
    config_dict: dict,
    CONST_MAXBOT_ANSWER_ONLINE_FILE: str
) -> list[str]:
    """
    從配置與檔案讀取用戶預定義的答案清單

    Args:
        config_dict: 配置字典（含 advanced.user_guess_string）
        CONST_MAXBOT_ANSWER_ONLINE_FILE: 線上答案檔案路徑（如 "answer.txt"）

    Returns:
        list[str]: 答案清單（去重且合併本地與線上答案）

    Raises:
        無（讀取失敗時回傳空清單）
    """
```

**資料來源優先順序**：
1. `config_dict["advanced"]["user_guess_string"]`（本地配置）
2. `CONST_MAXBOT_ANSWER_ONLINE_FILE`（檔案系統）

**回傳格式**：
- 逗號分隔的字串被解析為 JSON 陣列
- 範例：`"答案A,答案B"` → `["答案A", "答案B"]`

---

### 3. `util.get_answer_list_from_question_string()` - 自動推測答案

**檔案**：`src/util.py`
**行數**：1813-1950（約）

**函數簽章**：
```python
def get_answer_list_from_question_string(
    registrationsNewApp_div: Optional[Any],
    captcha_text_div_text: str
) -> list[str]:
    """
    根據問題文本自動推測可能的答案

    Args:
        registrationsNewApp_div: WebElement（NoDriver 環境下傳 None）
        captcha_text_div_text: 問題文本（完整字串）

    Returns:
        list[str]: 推測的答案清單（按可能性排序）

    Raises:
        無（推測失敗時回傳空清單）
    """
```

**推測邏輯**（規則式）：
1. **引號內文字**：`「答案」` → `["答案"]`
2. **括號內文字**：`【答案】` → `["答案"]`
3. **日期格式**：`"例如20250620"` → `["20250620", "2025-06-20", "2025/06/20"]`
4. **數字轉換**：`「三」` → `["3"]`
5. **關鍵字匹配**：問題包含特定關鍵字時返回預定義答案

**前置條件**：
- `captcha_text_div_text` 不為空字串
- 問題文本包含足夠資訊供推測

**後置條件**：
- 回傳清單不包含空字串
- 回傳清單去重（無重複答案）

---

### 4. `write_question_to_file()` - 記錄問題至檔案

**檔案**：`src/nodriver_tixcraft.py`
**行數**：178-181

**函數簽章**：
```python
def write_question_to_file(question_text: str) -> None:
    """
    將問題文本寫入檔案供後續分析

    Args:
        question_text: 問題文本字串

    Returns:
        None

    Raises:
        IOError: 檔案寫入失敗時（捕獲並忽略）
    """
```

**檔案路徑**：`src/question.txt`（由 `CONST_MAXBOT_QUESTION_FILE` 常數定義）

**寫入模式**：覆寫（每次新問題覆寫舊記錄）

**呼叫時機**：偵測到驗證問題後立即呼叫（line 1202）

---

## DOM 操作函數（NoDriver）

### 5. `tab.evaluate()` - JavaScript 執行

**來源**：NoDriver 內建 API

**使用方式**：
```python
result = await tab.evaluate('''
    (function() {
        const input = document.querySelector('div.custom-captcha-inner > div > div > input');
        if (!input) {
            return { success: false, error: "Input not found" };
        }

        input.focus();
        input.value = "答案";
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();

        return { success: true, value: input.value };
    })();
''')
```

**回傳格式**：
- 成功：`{"success": true, "value": "填寫的答案"}`
- 失敗：`{"success": false, "error": "錯誤訊息"}`

**DOM 事件觸發順序**：
1. `focus()` - 聚焦輸入框
2. `input` event - 模擬打字
3. `change` event - 值改變事件
4. `blur()` - 失焦

---

## 配置讀取函數

### 6. 配置讀取路徑

**來源**：`settings.json` → `config_dict`

**讀取方式**：
```python
auto_guess_enabled = config_dict["advanced"]["auto_guess_options"]
user_answers = config_dict["advanced"]["user_guess_string"]
debug_mode = config_dict["advanced"]["verbose"]
```

**型別檢查**：
```python
assert isinstance(auto_guess_enabled, bool), "auto_guess_options must be boolean"
assert isinstance(user_answers, str), "user_guess_string must be string"
assert isinstance(debug_mode, bool), "verbose must be boolean"
```

---

## 錯誤處理契約

### 錯誤處理原則

1. **所有錯誤均捕獲**：避免答題流程失敗導致搶票中斷
2. **優雅降級**：無法推測答案時回傳空清單，不拋出異常
3. **Debug 輸出**：`verbose` 模式下輸出詳細錯誤資訊

### 錯誤處理範例

```python
try:
    answer_list = util.get_answer_list_from_question_string(None, question_text)
except Exception as exc:
    if config_dict["advanced"]["verbose"]:
        print(f"[ERROR] Failed to guess answers: {exc}")
    answer_list = []
```

---

## 測試契約

### 單元測試需求

**測試函數**：`util.get_answer_list_from_question_string()`

**測試案例**：
```python
def test_guess_date_format():
    question = "請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)"
    answers = util.get_answer_list_from_question_string(None, question)
    assert "20250620" in answers, "Should extract date from example"

def test_empty_question():
    answers = util.get_answer_list_from_question_string(None, "")
    assert answers == [], "Empty question should return empty list"

def test_user_defined_priority():
    config = {"advanced": {"user_guess_string": "答案A,答案B"}}
    answers = util.get_answer_list_from_user_guess_string(config, "")
    assert answers == ["答案A", "答案B"], "Should parse user answers"
```

### 整合測試需求

**測試場景**：完整答題流程

**測試步驟**：
1. 載入 `.temp/kktix-sunset-qa.html` 至 NoDriver
2. 呼叫 `nodriver_kktix_reg_captcha()`
3. 驗證 `answer_list` 非空
4. 驗證答案已填入輸入框
5. 驗證問題已寫入 `question.txt`

**成功標準**：
- 答案推測成功率 >= 80%（SC-002）
- 填寫時間 <= 2 秒（SC-003）
- 無崩潰或異常拋出（SC-005）

---

## 契約總結表

| 函數 | 輸入 | 輸出 | 副作用 | 錯誤處理 |
|------|------|------|--------|---------|
| `nodriver_kktix_reg_captcha()` | tab, config_dict, fail_list, div | (fail_list, is_popup, clicked) | 填寫輸入框、寫入檔案 | 捕獲所有異常 |
| `get_answer_list_from_user_guess_string()` | config_dict, file_path | `list[str]` | 讀取檔案 | 回傳空清單 |
| `get_answer_list_from_question_string()` | None, question_text | `list[str]` | 無 | 回傳空清單 |
| `write_question_to_file()` | question_text | None | 寫入檔案 | 捕獲 IOError |
| `tab.evaluate()` | JavaScript code | `dict` | DOM 操作 | NoDriver 內建處理 |

---

**版本**：1.0
**審查狀態**：待審查
**下一步**：產生配置 schema (`config-schema.md`)
