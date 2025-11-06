# 功能規格說明: KKTIX 自動答題功能（NoDriver 版本）

**功能分支**: `004-kktix-auto-answer`
**建立日期**: 2025-11-03
**狀態**: 草稿
**輸入**: 用戶描述: "新功能 這原本是在 chrome driver裡面的 但是現在 nodriver還沒實作 kktix在 nodriver裡面有一個 自動猜測問題的功能 需要實作到 nodriver版本的 kktix上 設計時需要參考的資料有 logs.txt 這看起來有抓到問題 但不會回答問題 問題QA元素需要參考 kktix-sunset-qa.html"

## 憲章合規聲明

本功能規格遵循專案憲章（`.specify/memory/constitution.md`）中的以下原則：

- **I. NoDriver First**: 本功能專注於 NoDriver 版本實作，符合技術優先級策略
- **II. 資料結構優先**: 將在 plan 階段明確定義問答資料結構與 API 契約
- **III. 三問法則**:
  - **是核心問題嗎？** 是。自動答題是 KKTIX 搶票流程中防止被驗證碼阻擋的關鍵功能
  - **有更簡單的方法嗎？** 無。Chrome Driver 已有成熟實作，應複用既有邏輯而非重新設計
  - **會破壞相容性嗎？** 否。這是新增功能，不改變現有 API 或配置結構
- **V. 設定驅動開發**: 遵循現有 `auto_guess_options` 配置欄位控制功能啟用
- **VIII. 文件與代碼同步**: 需同步更新 `docs/06-api-reference/nodriver_api_guide.md`

## 用戶情境與測試

### User Story 1 - 自動偵測並回答 KKTIX 驗證問題 (Priority: P1)

當用戶在 KKTIX 平台上搶票時，系統會自動偵測頁面上的驗證問題，並根據問題內容自動推測並填寫答案，讓用戶無需手動介入即可通過驗證步驟。

**優先級說明**: 這是核心功能。KKTIX 平台常用自訂問題作為防機器人手段，若無法自動回答，用戶將被卡在驗證頁面而錯失搶票時機。此功能直接決定 NoDriver 版本在 KKTIX 平台的可用性。

**獨立測試方式**: 可透過載入實際 KKTIX 活動頁面（含驗證問題），檢查系統是否自動偵測問題文本、推測答案、並填寫至輸入框，完成整個自動答題流程。可使用 `.temp/kktix-sunset-qa.html` 作為測試案例。

**驗收情境**:

1. **假設** 用戶配置中已啟用 `auto_guess_options` 且訪問含有自訂驗證問題的 KKTIX 活動頁面，**當** 系統偵測到驗證問題（例如："請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)"），**則** 系統應從 `util.get_answer_list_from_question_string()` 推測可能答案並自動填入輸入框

2. **假設** 用戶未提供 `user_guess_string` 配置（無預先定義答案），**當** 系統偵測到問題且 `auto_guess_options` 啟用，**則** 系統應嘗試從問題文本中推測答案（如日期格式、特定關鍵字等）

3. **假設** 系統嘗試填寫答案但第一次失敗（答案錯誤），**當** 系統再次偵測到相同問題，**則** 系統應將失敗答案加入 `fail_list` 並嘗試下一個候選答案

4. **假設** 用戶在 `settings.json` 或 `answer.txt` 中預先定義了答案字串，**當** 系統偵測到問題，**則** 系統應優先使用用戶定義的答案而非自動推測

---

### User Story 2 - 答案重試與失敗記錄 (Priority: P2)

當系統填寫的答案被判定為錯誤時，系統會記錄該答案至失敗清單，並在下次遇到相同問題時跳過已失敗的答案，嘗試其他候選答案。

**優先級說明**: 提升成功率。某些問題可能有多個合理答案（如日期可能有多種格式），重試機制能增加自動通過驗證的機率。

**獨立測試方式**: 可透過模擬多次答題流程，檢查系統是否正確維護 `fail_list` 並在重試時跳過已失敗的答案。

**驗收情境**:

1. **假設** 系統第一次填寫答案 "20250620" 但被驗證失敗，**當** 系統下次遇到相同問題，**則** 系統應將 "20250620" 加入 `fail_list` 並嘗試其他候選答案（如 "2025-06-20"）

2. **假設** 系統已嘗試所有候選答案且全部失敗，**當** 系統再次偵測到問題，**則** 系統應停止自動填寫並保留輸入框為空（避免無限錯誤嘗試）

---

### User Story 3 - Debug 資訊輸出與問題記錄 (Priority: P3)

當 `verbose` 模式啟用時，系統會輸出詳細的問題文本、推測答案清單、以及失敗記錄，方便用戶除錯和分析。同時將問題文本寫入檔案供後續分析。

**優先級說明**: 輔助除錯。有助於用戶理解系統行為和診斷問題，但不影響核心功能運作。

**獨立測試方式**: 可透過啟用 `verbose` 模式並檢查終端輸出與檔案記錄是否包含預期資訊。

**驗收情境**:

1. **假設** 用戶啟用 `verbose` 模式，**當** 系統偵測到驗證問題，**則** 系統應在終端輸出問題文本（`question_text`）、推測答案清單（`answer_list`）、以及失敗記錄（`fail_list`）

2. **假設** 系統偵測到新的驗證問題，**當** 執行答題流程，**則** 系統應呼叫 `write_question_to_file()` 將問題文本寫入檔案（如 `question.txt`）供後續分析

---

### 邊界情境

- **問題文本過長或包含特殊字元**：系統應能正確解析並處理包含換行、HTML 標籤、或多語言文本的問題
- **無法推測答案**：當 `auto_guess_options` 啟用但系統無法從問題推測任何合理答案時，`answer_list` 應為空，系統應保留輸入框為空（不填寫錯誤內容）
- **輸入框不存在或被禁用**：系統應能偵測輸入框狀態（`disabled`、`readOnly`），若輸入框不可用則跳過填寫
- **答案格式要求嚴格**：如問題要求「半形大寫英文」或「西元年月日格式」，系統應嘗試符合格式要求（依賴 `util.py` 中的格式化邏輯）
- **網路延遲或頁面未載入完成**：系統應等待頁面元素載入完成（使用 NoDriver 的等待機制）再嘗試填寫答案

## 需求

### 功能性需求

- **FR-001**: 系統必須能偵測 KKTIX 頁面上的自訂驗證問題（透過 `div.custom-captcha-inner p` 選擇器）
- **FR-002**: 系統必須能提取驗證問題的完整文本（包含中英文及格式要求）
- **FR-003**: 系統必須支援兩種答案來源：(1) 用戶預先定義的答案字串（`user_guess_string` 或 `answer.txt`），(2) 自動從問題推測的答案（透過 `util.get_answer_list_from_question_string()`）
- **FR-004**: 系統必須能在用戶啟用 `auto_guess_options` 配置時，自動呼叫答案推測函數
- **FR-005**: 系統必須能自動填寫推測的答案至驗證問題輸入框（`div.custom-captcha-inner > div > div > input`）
- **FR-006**: 系統必須維護一個失敗答案清單（`fail_list`），記錄已嘗試但驗證失敗的答案
- **FR-007**: 系統必須在選擇下一個答案時，跳過已存在於 `fail_list` 中的答案
- **FR-008**: 系統必須支援人類化填寫行為，包含隨機延遲（0.3-1.0 秒）和逐字輸入模擬
- **FR-009**: 系統必須在 `verbose` 模式下輸出問題文本、答案清單、以及失敗記錄至終端
- **FR-010**: 系統必須呼叫 `write_question_to_file()` 將問題文本寫入檔案供後續分析
- **FR-011**: 系統必須能偵測輸入框的可用性狀態（`disabled`、`readOnly`），若不可用則跳過填寫
- **FR-012**: 系統必須在填寫答案後觸發適當的 DOM 事件（`input`、`change`、`blur`），確保前端框架（如 Angular）能正確識別輸入

### 主要實體

- **驗證問題（Captcha Question）**: 代表 KKTIX 頁面上的自訂驗證問題，包含問題文本（`question_text`）和對應的答案輸入框
- **答案清單（Answer List）**: 由用戶定義或自動推測產生的候選答案集合，按優先順序排列
- **失敗清單（Fail List）**: 記錄已嘗試但驗證失敗的答案字串，用於避免重複嘗試相同錯誤答案

## 成功標準

### 可衡量成果

- **SC-001**: 當 KKTIX 頁面存在驗證問題時，系統能在 3 秒內偵測並提取問題文本（95% 情況下）
- **SC-002**: 當用戶啟用 `auto_guess_options` 且問題可推測答案時，系統能產生至少 1 個候選答案（80% 情況下）
- **SC-003**: 當答案推測成功時，系統能在 2 秒內完成答案填寫（包含人類化延遲）
- **SC-004**: 當答案驗證失敗時，系統能正確記錄至 `fail_list` 並在下次跳過該答案（100% 情況下）
- **SC-005**: 系統不會因答題流程失敗而導致整個 KKTIX 搶票流程中斷（0% 崩潰率）
- **SC-006**: 在 `verbose` 模式下，用戶能在終端看到完整的問題分析資訊（問題文本、答案清單、失敗記錄），方便除錯

## 範圍與限制

### 包含範圍

- NoDriver 版本的 KKTIX 自動答題功能實作
- 複用現有 `util.py` 中的答案推測邏輯（`get_answer_list_from_question_string()`、`get_answer_list_from_user_guess_string()`）
- 整合現有 `fail_list` 機制與重試邏輯
- 支援現有配置欄位（`auto_guess_options`、`user_guess_string`）

### 排除範圍

- Chrome Driver 版本的修改或增強（已進入維護模式）
- 新的驗證碼類型支援（如圖形驗證碼、reCAPTCHA）
- 新的配置欄位或 UI 介面（使用現有 `settings.json` 配置）
- 機器學習或 NLP 技術來推測答案（使用現有規則式推測邏輯）

## 假設與約束

### 假設

- **ASM-001**: 現有 `util.get_answer_list_from_question_string()` 函數在 NoDriver 環境下可正常運作（無 WebDriver 依賴）
- **ASM-002**: KKTIX 驗證問題的 DOM 結構與選擇器保持穩定（`div.custom-captcha-inner`）
- **ASM-003**: 用戶已正確配置 `settings.json` 中的 `auto_guess_options` 欄位（預設值為啟用或禁用需查閱現有配置 schema）
- **ASM-004**: NoDriver 的 `tab.evaluate()` 方法能正確執行 JavaScript 並回傳結果

### 約束

- **CON-001**: 必須遵循憲章第 I 條（NoDriver First），不得同步修改 Chrome Driver 版本
- **CON-002**: 必須使用現有 `util.py` 函數，避免重複實作答案推測邏輯（遵循憲章第 IV 條：單一職責與可組合性）
- **CON-003**: 不得破壞現有 KKTIX 搶票流程的其他步驟（日期選擇、區域選擇、座位選擇等）
- **CON-004**: 必須在 `verbose` 模式下提供充足的 Debug 資訊，方便問題診斷（遵循憲章第 VI 條：測試驅動穩定性）
- **CON-005**: 程式碼中不得包含 emoji（遵循專案編碼規範，避免 Windows cp950 錯誤）

## 相依性

### 外部相依

- **DEP-001**: `util.get_answer_list_from_question_string()` - 答案推測核心邏輯
- **DEP-002**: `util.get_answer_list_from_user_guess_string()` - 讀取用戶定義答案
- **DEP-003**: `write_question_to_file()` - 問題記錄函數（需確認是否已存在）
- **DEP-004**: NoDriver `tab.evaluate()` - JavaScript 執行與 DOM 操作
- **DEP-005**: `settings.json` 配置結構 - `auto_guess_options`、`user_guess_string`、`verbose` 欄位

### 內部相依

- **DEP-006**: 現有 `nodriver_kktix_reg_captcha()` 函數 - 需擴充以支援自動答題
- **DEP-007**: 現有 `fail_list` 機制 - 需整合至新流程

## 參考資料

### 技術參考

- 現有實作：`src/chrome_tixcraft.py` - Chrome Driver 版本的 KKTIX 答題邏輯（參考 line 6792-6820）
- 工具函數：`src/util.py` - `get_answer_list_from_question_string()` 等推測邏輯
- NoDriver API：`docs/06-api-reference/nodriver_api_guide.md`
- 專案憲章：`.specify/memory/constitution.md`

### 測試案例

- 問題文本範例：`.temp/logs.txt` - 實際 KKTIX 問題偵測記錄
- HTML 結構參考：`.temp/kktix-sunset-qa.html` - KKTIX 驗證頁面 DOM 結構

## 未來考量

### 潛在擴充

- **FUT-001**: 支援更複雜的問題類型（如數學運算、邏輯推理）
- **FUT-002**: 加入答案成功率統計，優化推測邏輯
- **FUT-003**: 支援多語言問題解析（目前主要為中英混合）
- **FUT-004**: 整合外部知識庫或 API 來查詢特定問題答案（如活動日期、團體名稱）

### 已知限制

- **LIM-001**: 答案推測基於規則式邏輯，無法處理高度語義化或需外部知識的問題（如「落日飛車的英文團名是？」需預先知道答案）
- **LIM-002**: 若 KKTIX 更改 DOM 結構或驗證機制，需手動更新選擇器
- **LIM-003**: 多次答案錯誤可能觸發 KKTIX 的風控機制（如 IP 封鎖或驗證升級）

---

**規格版本**: 1.0
**最後更新**: 2025-11-03
**審查狀態**: 待審查
