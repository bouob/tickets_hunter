# 資料模型：KKTIX 自動答題功能（NoDriver 版本）

**日期**：2025-11-03
**分支**：`004-kktix-auto-answer`
**目的**：定義核心實體、關係、驗證規則與狀態轉換

---

## 核心實體

### 1. 驗證問題（Captcha Question）

**描述**：代表 KKTIX 頁面上的自訂驗證問題

**欄位**：

| 欄位名稱 | 資料類型 | 必填 | 描述 | 範例 |
|---------|---------|------|------|------|
| `question_text` | `str` | ✅ | 完整問題文本（含中英文） | "請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)" |
| `input_selector` | `str` | ✅ | 輸入框的 CSS 選擇器 | "div.custom-captcha-inner > div > div > input" |
| `detected_at` | `float` | ✅ | 偵測時間戳（Unix timestamp） | 1730620800.0 |
| `is_input_available` | `bool` | ✅ | 輸入框是否可用（非 disabled/readOnly） | `True` |

**不變性約束**：
- `question_text` 不可為空字串
- `input_selector` 必須為有效的 CSS 選擇器
- `detected_at` 必須為正數

**狀態轉換**：
```
[Not Detected] → [Detected] → [Answered] → [Verified/Failed]
     ↓              ↓            ↓              ↓
  (無問題)      (已偵測)      (已填寫)   (驗證成功/失敗)
```

---

### 2. 答案清單（Answer List）

**描述**：候選答案的有序集合，由用戶定義或自動推測產生

**欄位**：

| 欄位名稱 | 資料類型 | 必填 | 描述 | 範例 |
|---------|---------|------|------|------|
| `answers` | `list[str]` | ✅ | 答案字串陣列（按優先順序排列） | `["20250620", "2025-06-20", "2025/06/20"]` |
| `source` | `str` | ✅ | 答案來源（`"user_defined"` / `"auto_guessed"`） | `"auto_guessed"` |
| `generated_at` | `float` | ✅ | 產生時間戳 | 1730620801.5 |
| `total_count` | `int` | ✅ | 總答案數量（唯讀） | 3 |

**不變性約束**：
- `answers` 不可包含空字串
- `answers` 不可包含重複項目（需去重）
- `source` 只能是 `"user_defined"` 或 `"auto_guessed"`
- `total_count` 必須等於 `len(answers)`

**資料關聯**：
- 優先使用 `user_defined` 來源的答案
- `auto_guessed` 來源僅在 `auto_guess_options` 啟用且無用戶定義答案時產生

---

### 3. 失敗清單（Fail List）

**描述**：記錄已嘗試但驗證失敗的答案字串，避免重複嘗試

**欄位**：

| 欄位名稱 | 資料類型 | 必填 | 描述 | 範例 |
|---------|---------|------|------|------|
| `failed_answers` | `list[str]` | ✅ | 已失敗的答案字串 | `["20250620", "2025-06-20"]` |
| `failure_count` | `int` | ✅ | 失敗次數（唯讀） | 2 |

**不變性約束**：
- `failed_answers` 不可包含重複項目
- `failure_count` 必須等於 `len(failed_answers)`
- 失敗清單隨 session 清除（不持久化）

**操作方法**：
- **新增失敗答案**：`failed_answers.append(answer)` 並確保不重複
- **檢查是否失敗過**：`answer in failed_answers`
- **重設清單**：僅在新 session 開始時

---

### 4. 配置項（Configuration）

**描述**：控制自動答題功能的配置參數

**欄位**：

| 欄位名稱 | 資料類型 | 必填 | 預設值 | 描述 |
|---------|---------|------|--------|------|
| `auto_guess_options` | `bool` | ✅ | `false` | 是否啟用自動推測答案 |
| `user_guess_string` | `str` | ❌ | `""` | 用戶預先定義的答案字串（逗號分隔） |
| `verbose` | `bool` | ✅ | `false` | 是否輸出 Debug 資訊 |

**不變性約束**：
- `user_guess_string` 可為空字串（代表無預定義答案）
- `user_guess_string` 格式：逗號分隔，如 `"答案A,答案B,答案C"`

**讀取路徑**：
- `config_dict["advanced"]["auto_guess_options"]`
- `config_dict["advanced"]["user_guess_string"]`
- `config_dict["advanced"]["verbose"]`

---

## 實體關係圖

```
┌─────────────────────┐
│  Configuration      │
│  (settings.json)    │
└──────────┬──────────┘
           │ controls
           ↓
┌─────────────────────┐       generates      ┌─────────────────────┐
│  Captcha Question   │─────────────────────→│   Answer List       │
│  (question_text)    │                      │   (answers[])       │
└──────────┬──────────┘                      └──────────┬──────────┘
           │                                            │
           │ fills with                                 │ filters by
           ↓                                            ↓
┌─────────────────────┐       records        ┌─────────────────────┐
│  Input Element      │←─────────────────────│   Fail List         │
│  (input field)      │       failure         │   (failed_answers[])│
└─────────────────────┘                      └─────────────────────┘
```

**關係說明**：
1. **Configuration → Answer List**：配置控制答案來源（user_defined / auto_guessed）
2. **Captcha Question → Answer List**：問題文本用於推測答案（若啟用 auto_guess）
3. **Answer List → Fail List**：答案嘗試後若失敗則加入失敗清單
4. **Fail List → Answer List**：過濾時跳過已失敗的答案

---

## 狀態轉換圖

### 答題流程狀態機

```
┌─────────────┐
│   IDLE      │ (初始狀態：無驗證問題)
└──────┬──────┘
       │ detect_question()
       ↓
┌─────────────┐
│  DETECTED   │ (已偵測問題)
└──────┬──────┘
       │ generate_answers()
       ↓
┌─────────────┐
│ READY       │ (答案已準備)
└──────┬──────┘
       │ fill_answer()
       ↓
┌─────────────┐
│ ANSWERED    │ (已填寫答案)
└──────┬──────┘
       │ verify()
       ↓
┌─────────────┐     ┌─────────────┐
│  SUCCESS    │     │   FAILED    │
└─────────────┘     └──────┬──────┘
                           │ retry?
                           ↓
                    ┌─────────────┐
                    │  EXHAUSTED  │ (所有答案已嘗試)
                    └─────────────┘
```

**狀態說明**：
- **IDLE**：無驗證問題偵測到
- **DETECTED**：問題已偵測，等待產生答案
- **READY**：答案已準備，可填寫
- **ANSWERED**：答案已填寫，等待驗證
- **SUCCESS**：驗證成功，流程結束
- **FAILED**：驗證失敗，記錄至 fail_list
- **EXHAUSTED**：所有候選答案已嘗試且失敗，停止自動填寫

**合法轉換**：
- `IDLE → DETECTED`（偵測到問題）
- `DETECTED → READY`（答案產生成功）
- `DETECTED → IDLE`（無法產生答案）
- `READY → ANSWERED`（填寫答案）
- `ANSWERED → SUCCESS`（驗證成功）
- `ANSWERED → FAILED`（驗證失敗）
- `FAILED → READY`（有其他候選答案）
- `FAILED → EXHAUSTED`（無其他候選答案）

**非法轉換**（需防範）：
- `IDLE → ANSWERED`（跳過偵測）
- `DETECTED → SUCCESS`（跳過填寫）
- `EXHAUSTED → READY`（已窮盡但繼續嘗試）

---

## 驗證規則

### 輸入驗證

1. **問題文本驗證**：
   - 不可為空字串
   - 長度 >= 10 字元（合理問題長度）
   - 可包含中英文、數字、標點符號

2. **答案字串驗證**：
   - 不可為空字串
   - 不可包含換行符（`\n`、`\r`）
   - 長度 <= 200 字元（合理答案長度）

3. **配置驗證**：
   - `auto_guess_options` 必須為布林值
   - `user_guess_string` 為字串類型（可為空）
   - `verbose` 必須為布林值

### 業務規則驗證

1. **答案選擇規則**：
   - 優先使用用戶定義答案（`user_guess_string`）
   - 若無用戶答案且 `auto_guess_options` 啟用，則自動推測
   - 跳過 `fail_list` 中的答案
   - 若所有答案皆失敗，停止自動填寫

2. **重試規則**：
   - 同一答案不可重複嘗試
   - 失敗後必須記錄至 `fail_list`
   - 重試前必須檢查 `fail_list`

3. **安全規則**：
   - 填寫答案前必須檢查輸入框可用性（非 disabled/readOnly）
   - 必須觸發 DOM 事件（`input`、`change`、`blur`）確保前端識別
   - 必須加入人類化延遲（0.3-1.0 秒隨機）

---

## 資料流程

### 完整資料流程圖

```
1. [使用者配置] → settings.json
                      ↓
2. [系統啟動] → 讀取 config_dict
                      ↓
3. [頁面載入] → 偵測驗證問題 → Captcha Question
                      ↓
4. [產生答案] → (A) user_guess_string? → Answer List (user_defined)
                      ↓ (否)
                 (B) auto_guess_options? → util.get_answer_list_from_question_string()
                      ↓
                    Answer List (auto_guessed)
                      ↓
5. [過濾答案] → 移除 fail_list 中的答案 → Filtered Answer List
                      ↓
6. [填寫答案] → 選擇第一個候選答案 → 填入 input element
                      ↓
7. [驗證結果] → (成功) → 流程結束
                      ↓ (失敗)
8. [記錄失敗] → 答案加入 fail_list → 回到步驟 5
```

---

## 資料儲存

### 記憶體中（Runtime）

- **fail_list**：`list[str]`（隨 session 清除）
- **answer_list**：`list[str]`（每次問題重新產生）
- **question_text**：`str`（每次偵測更新）

### 檔案系統（Persistent）

- **問題記錄**：`src/question.txt`（透過 `write_question_to_file()`）
  - 格式：純文字
  - 用途：除錯與分析
  - 覆寫模式（每次新問題覆寫舊記錄）

### 配置檔案

- **settings.json**：`src/settings.json`
  - `advanced.auto_guess_options`
  - `advanced.user_guess_string`
  - `advanced.verbose`

---

## 資料模型總結

| 實體 | 資料類型 | 生命週期 | 儲存位置 |
|------|---------|---------|---------|
| Captcha Question | Object | Session | Memory |
| Answer List | `list[str]` | Per Question | Memory |
| Fail List | `list[str]` | Session | Memory |
| Configuration | Object | Application | `settings.json` |
| Question Log | Text | Persistent | `src/question.txt` |

---

**版本**：1.0
**審查狀態**：待審查
**下一步**：產生 API 契約（`contracts/`）
