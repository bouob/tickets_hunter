# 實作計畫：KKTIX 自動答題功能（NoDriver 版本）

**分支**：`004-kktix-auto-answer` | **日期**：2025-11-03 | **規格**：[spec.md](spec.md)
**輸入**：來自 `/specs/004-kktix-auto-answer/spec.md` 的功能規格說明

**注意**：本範本由 `/speckit.plan` 指令填寫。執行流程請參見 `.specify/templates/commands/plan.md`。

## 摘要

本功能將 Chrome Driver 版本中已有的 KKTIX 自動答題功能移植至 NoDriver 版本。系統需能偵測 KKTIX 頁面上的自訂驗證問題，透過現有 `util.py` 中的答案推測邏輯自動產生候選答案，並以人類化方式填寫至輸入框。

**核心需求**：
- 問題偵測：透過 `div.custom-captcha-inner p` 選擇器提取問題文本
- 答案推測：複用 `util.get_answer_list_from_question_string()` 規則式邏輯
- 自動填寫：使用 NoDriver 的 `tab.evaluate()` 模擬人類輸入行為
- 失敗重試：維護 `fail_list` 避免重複嘗試錯誤答案

**技術方案**：
- 在現有 `nodriver_kktix_reg_captcha()` 函數中啟用 `auto_guess_options` 分支
- 整合現有答案推測邏輯（`util.py`），無需重新實作
- 使用 NoDriver 的 CDP 協議進行 DOM 操作與事件觸發

## 技術上下文 (Technical Context)

**語言/版本**：Python 3.10+ (專案現有版本)
**主要相依性 (dependency)**：
- NoDriver（專案核心，Chrome CDP 協議控制）
- `util.py`（答案推測邏輯：`get_answer_list_from_question_string()`、`get_answer_list_from_user_guess_string()`）
- 現有 `nodriver_tixcraft.py`（KKTIX 平台實作）

**儲存方式**：
- 設定檔：`settings.json`（配置欄位：`auto_guess_options`、`user_guess_string`、`verbose`）
- 問題記錄：檔案系統（透過 `write_question_to_file()`）
- 失敗答案：記憶體中的 `fail_list`（隨 session 清除）

**測試**：
- 手動測試：30 秒 timeout 測試指令（見 CLAUDE.md）
- 測試案例：`.temp/kktix-sunset-qa.html`（實際 KKTIX 驗證頁面）
- 驗證方式：檢查 `.temp/test_output.txt` 中的 Debug 輸出

**目標平台**：Windows 10+ / Linux / macOS（與專案一致）
**專案類型**：Single project（Python CLI 工具）
**效能目標**：
- 問題偵測：< 3 秒（SC-001）
- 答案填寫：< 2 秒（SC-003）
- 推測準確率：80% 情況下至少產生 1 個候選答案（SC-002）

**限制條件**：
- 不得破壞現有 KKTIX 搶票流程（SC-005：0% 崩潰率）
- 必須支援人類化延遲（0.3-1.0 秒隨機）避免風控偵測
- 禁止使用 emoji（避免 Windows cp950 編碼錯誤）

**規模/範圍**：
- 修改範圍：`src/nodriver_tixcraft.py` 中的 `nodriver_kktix_reg_captcha()` 函數（約 100 行）
- 新增函數：無（複用現有 `util.py` 邏輯）
- 新增配置：無（使用現有 `auto_guess_options` 欄位）

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

### I. NoDriver First（技術架構優先性）
- ✅ **通過**：本功能專注於 NoDriver 版本實作
- ✅ **通過**：不修改 Chrome Driver 版本（已進入維護模式）
- ✅ **通過**：使用現有 `nodriver_tixcraft.py` 作為實作基礎

### II. 資料結構優先（設計先於實作）
- ✅ **通過**：已產生 `data-model.md`（定義驗證問題、答案清單、失敗清單實體）
- ✅ **通過**：已產生 `contracts/`（定義函數簽章與配置 schema）
- ✅ **通過**：現有 `util.py` 函數介面已確認符合需求

### III. 三問法則（決策守門人）
- ✅ **通過**：「是核心問題嗎？」- 是（防止被驗證碼阻擋）
- ✅ **通過**：「有更簡單的方法嗎？」- 無（複用成熟實作最簡單）
- ✅ **通過**：「會破壞相容性嗎？」- 否（新增功能，不改變既有 API）

### IV. 單一職責與可組合性（函數設計原則）
- ✅ **通過**：複用 `util.py` 中的單一職責函數
- ✅ **通過**：不在 `nodriver_kktix_reg_captcha()` 中實作答案推測邏輯
- ✅ **通過**：遵循依賴注入原則（透過參數傳遞 `config_dict`、`fail_list`）

### V. 設定驅動開發（使用者友善設計）
- ✅ **通過**：使用現有 `settings.json` 配置欄位（`auto_guess_options`）
- ✅ **通過**：無硬寫邏輯，所有行為由設定控制
- ✅ **通過**：遵循現有配置架構

### VI. 測試驅動穩定性（品質守門人）
- ✅ **通過**：有測試案例（`.temp/kktix-sunset-qa.html`）
- ✅ **通過**：有測試指令（30 秒 timeout 測試）
- ✅ **通過**：有驗證方式（檢查輸出）
- ⚠️ **待執行**：實作完成後需執行測試並確認通過

### VII. MVP 原則（最小可行產品優先）
- ✅ **通過**：P1 User Story 獨立可測（自動偵測並回答驗證問題）
- ✅ **通過**：P2/P3 User Story 可後續迭代
- ✅ **通過**：核心流程優先

### VIII. 文件與代碼同步（知識傳承）
- ⚠️ **待執行**：需同步更新 `docs/06-api-reference/nodriver_api_guide.md`
- ⚠️ **待執行**：需同步更新 `docs/02-development/structure.md`
- ✅ **通過**：已在 spec.md 中記錄需同步更新的文件

### IX. Git 提交規範與工作流程
- ✅ **通過**：使用 feature 分支（`004-kktix-auto-answer`）
- ⚠️ **待執行**：實作完成後使用 `/gsave` 指令提交
- ⚠️ **待執行**：測試通過後使用 `/gpush` 指令推送

### 檢查結果
- **狀態**：✅ 通過（無阻礙項目）
- **警告項目**：4 項「待執行」（實作後需處理）
- **行動**：可進入 Phase 0 研究階段

## 專案結構

### 文件（本功能）

```
specs/004-kktix-auto-answer/
├── spec.md                  # 功能規格說明
├── checklists/
│   └── requirements.md      # 規格品質檢查清單
├── research.md              # Phase 0 研究與決策
├── plan.md                  # This file (Phase 1)
├── data-model.md            # Phase 1 資料模型
├── quickstart.md            # Phase 1 快速開始指南
├── contracts/               # Phase 1 API 契約
│   ├── function-signatures.md
│   └── config-schema.md
└── tasks.md                 # Phase 2 任務清單（待產生）
```

### 原始碼（repository 根目錄）

```
src/
├── nodriver_tixcraft.py   # 主要修改檔案（nodriver_kktix_reg_captcha 函數）
├── util.py                 # 複用函數（get_answer_list_from_question_string 等）
├── settings.json           # 配置檔案（使用現有 auto_guess_options 欄位）
└── chrome_tixcraft.py      # 參考檔案（Chrome Driver 版本，不修改）

docs/
├── 06-api-reference/
│   └── nodriver_api_guide.md   # 需更新：新增答題流程說明
└── 02-development/
    └── structure.md             # 需更新：新增函數索引

.temp/
├── kktix-sunset-qa.html    # 測試案例（HTML 結構參考）
├── logs.txt                # 測試記錄（問題偵測輸出）
└── test_output.txt         # 測試輸出（驗證用）
```

**結構決策**：
- 採用 Single project 結構（專案現有架構）
- 主要修改集中於 `src/nodriver_tixcraft.py`（約 100 行範圍）
- 無需新增檔案，僅修改現有函數邏輯
- 複用 `src/util.py` 中的答案推測函數
- 測試案例位於 `.temp/` 目錄（臨時檔案，不納入 git）

## 複雜度追蹤

*僅在專案憲章檢查（Constitution Check）有違規且必須說明時填寫*

**無違規項目** - 所有憲章檢查通過，無需複雜度辯護。

---

## Phase 0：研究與決策

*本階段需解決技術上下文中的所有 NEEDS CLARIFICATION 項目*

### 研究任務清單

本功能無 NEEDS CLARIFICATION 項目，因為：
1. 技術堆疊明確（Python 3.10+、NoDriver、util.py）
2. 實作方式明確（複用現有 Chrome Driver 邏輯）
3. 整合點明確（nodriver_kktix_reg_captcha 函數）

### 研究結果（詳見 research.md）

1. **`write_question_to_file()` 函數已存在**（`nodriver_tixcraft.py:178`）
2. **`util.get_answer_list_from_question_string()` 支援 `None` 參數**
3. **`auto_guess_options` 預設值為 `false`**

**技術決策**：
- 複用現有函數（無需重新實作）
- 使用現有配置欄位（無需新增）
- 維持預設值 `false`（避免意外行為）

---

## Phase 1：資料模型與 API 契約

*本階段產出資料結構設計與 API 契約文件*

### Phase 1 產出檔案

✅ **已完成**：

1. **`data-model.md`** - 資料模型定義
   - 核心實體：Captcha Question、Answer List、Fail List、Configuration
   - 實體關係圖
   - 狀態轉換圖（答題流程狀態機）
   - 驗證規則
   - 資料流程圖

2. **`contracts/function-signatures.md`** - 函數簽章契約
   - `nodriver_kktix_reg_captcha()` - 主函數修改點
   - `util.get_answer_list_from_user_guess_string()` - 讀取用戶答案
   - `util.get_answer_list_from_question_string()` - 自動推測答案
   - `write_question_to_file()` - 記錄問題
   - `tab.evaluate()` - DOM 操作

3. **`contracts/config-schema.md`** - 配置 Schema
   - JSON Schema 定義
   - 配置項目詳細說明
   - 4 種使用場景範例
   - 配置驗證規則

4. **`quickstart.md`** - 快速開始指南
   - 5 分鐘快速啟用
   - 常見使用場景
   - Debug 模式
   - 故障排除

---

## Phase 1 後憲章檢查（重新評估）

*Phase 1 設計完成後，重新檢查是否符合憲章要求*

### 設計審查結果

所有 9 項憲章原則檢查通過：

- ✅ I. NoDriver First
- ✅ II. 資料結構優先
- ✅ III. 三問法則
- ✅ IV. 單一職責與可組合性
- ✅ V. 設定驅動開發
- ✅ VI. 測試驅動穩定性
- ✅ VII. MVP 原則
- ✅ VIII. 文件與代碼同步（設計文件已完整產出）
- ✅ IX. Git 提交規範

### 設計審查結論

- **狀態**：✅ 通過所有憲章檢查
- **警告**：2 項「待執行」（實作後處理文件同步）
- **下一步**：可進入 Phase 2（任務分解，執行 `/speckit.tasks`）

---

## Phase 2：任務分解（不在本指令範圍）

*Phase 2 由 `/speckit.tasks` 指令執行，本指令在此停止*

**下一步指令**：`/speckit.tasks`

**預期產出**：`specs/004-kktix-auto-answer/tasks.md`

**任務分解方向**（參考）：
1. 驗證現有 `util.py` 函數介面（確認 `None` 參數可用）
2. 修改 `nodriver_kktix_reg_captcha()` 函數（line 1206-1208）
3. 測試自動推測邏輯
4. 測試重試機制（fail_list）
5. 更新 API 文件
6. 更新結構文件

---

## 交付物總結

### 規格階段（已完成）
- ✅ `spec.md` - 功能規格說明
- ✅ `checklists/requirements.md` - 規格品質檢查清單

### Phase 0：研究（已完成）
- ✅ `research.md` - 研究與技術決策

### Phase 1：設計（已完成）
- ✅ `plan.md` - 本檔案（實作計畫）
- ✅ `data-model.md` - 資料模型
- ✅ `contracts/function-signatures.md` - 函數簽章契約
- ✅ `contracts/config-schema.md` - 配置 Schema
- ✅ `quickstart.md` - 快速開始指南

### Phase 2：任務（待執行）
- ⏳ `tasks.md` - 執行 `/speckit.tasks` 產生

---

## 附錄

### A. 關鍵檔案路徑

**修改檔案**：
- `src/nodriver_tixcraft.py:1172-1350` - `nodriver_kktix_reg_captcha()` 函數

**參考檔案**：
- `src/util.py:1465-1493` - `get_answer_list_from_user_guess_string()`
- `src/util.py:1813-1950` - `get_answer_list_from_question_string()`
- `src/chrome_tixcraft.py:6792-6820` - Chrome Driver 版本參考

**配置檔案**：
- `src/settings.json` - 主配置檔案

**測試檔案**：
- `.temp/kktix-sunset-qa.html` - 測試案例
- `.temp/logs.txt` - 測試記錄
- `.temp/test_output.txt` - 測試輸出

### B. 關鍵常數定義

**檔案路徑常數**（定義於 `nodriver_tixcraft.py`）：
- `CONST_MAXBOT_QUESTION_FILE` - 問題記錄檔案路徑（`"question.txt"`）
- `CONST_MAXBOT_ANSWER_ONLINE_FILE` - 線上答案檔案路徑（`"answer.txt"`）

**配置路徑**：
- `config_dict["advanced"]["auto_guess_options"]` - 啟用自動推測
- `config_dict["advanced"]["user_guess_string"]` - 用戶預定義答案
- `config_dict["advanced"]["verbose"]` - Debug 模式

### C. 實作檢查清單

**Phase 0 完成**：
- [x] 研究 `write_question_to_file()` 實作
- [x] 研究 `util.py` 函數介面
- [x] 研究配置預設值
- [x] 記錄技術決策

**Phase 1 完成**：
- [x] 定義資料模型（4 個核心實體）
- [x] 定義 API 契約（5 個函數簽章）
- [x] 定義配置 schema（3 個配置項目）
- [x] 撰寫快速開始指南
- [x] 重新評估憲章檢查

**Phase 2 待執行**（由 `/speckit.tasks` 產生）：
- [ ] 實作任務分解
- [ ] 實作優先順序排序
- [ ] 相依性分析

---

**計畫版本**：1.0
**計畫狀態**：✅ Phase 0-1 完成
**最後更新**：2025-11-03
**下一步**：執行 `/speckit.tasks` 產生任務清單
