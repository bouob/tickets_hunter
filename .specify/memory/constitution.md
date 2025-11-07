# Tickets Hunter 憲章

<!--
SYNC IMPACT REPORT
==================
版本變更：1.0.0 → 1.0.1
修改類型：PATCH（文件結構澄清與補充）
修改日期：2025-10-28

本次更新內容：
- 補充憲章第 VIII 條文件結構中缺失的目錄（docs/11-refactoring/）
- 補充實際存在但憲章未列出的 API 參考文件
- 補充實際存在但憲章未列出的開發文件
- 釐清文件結構與實際專案狀態的一致性

需同步更新的模板文件：
✅ plan-template.md - 已包含「專案憲章檢查」區塊參考
✅ spec-template.md - 已包含「憲章合規聲明」區塊
✅ tasks-template.md - 已包含「憲章原則映射」說明
✅ constitution.md - 本次更新

修訂歷史：
- v1.0.1 (2025-10-28): 文件結構澄清與補充
- v1.0.0 (2025-10-19): 首次通過，建立 9 大核心原則
-->

## 核心原則

### I. NoDriver First（技術架構優先性）

本專案採用 **NoDriver 優先級策略**。任何平台實作或功能開發，必須遵循以下優先順序：

1. **NoDriver**（推薦、預設）- 最強反偵測能力，是所有新功能的首選
2. **Undetected Chrome (UC)**（舊版回退）- 需要額外反偵測能力時的備選
3. **Selenium/Chrome WebDriver**（維護模式）- 僅限嚴重錯誤修復

**強制規則**：
- 新功能開發必須首先在 NoDriver 版本實作（`nodriver_tixcraft.py`）
- Chrome 版本（`chrome_tixcraft.py`）已進入維護模式，僅接受安全補丁與嚴重錯誤修復
- 若 NoDriver 版本不支援某平台，必須明確文件化理由，並納入 `README.md` 平台支援狀態表

**遵循檢查**：設定檔 `settings.json` 的 `webdriver_type` 欄位控制使用中的引擎。任何改變須更新相關文件。

---

### II. 資料結構優先（設計先於實作）

**不可協商的規則**：設計優先於實作；好的資料結構讓特殊情況消失；結構決定一切。

任何功能開發必須遵循以下流程：

1. **資料結構設計** - 在編寫任何程式碼前，必須在 `specs/[###-feature]/data-model.md` 中明確定義：
   - 核心實體與欄位
   - 實體間的關係
   - 不變性約束
   - 合法狀態轉移圖

2. **API 契約定義** - 必須在 `specs/[###-feature]/contracts/` 中定義所有介面：
   - 函數簽章與文件
   - 配置 schema（JSON schema 格式）
   - 輸入/輸出驗證規則

3. **實作檢查** - 實作必須完全符合資料結構定義，不得隨意偏離

**強制工具**：
- 配置驗證透過 JSON schema (`contracts/config-schema.md`)
- 平台介面驗證透過契約檔案 (`contracts/platform-interface.md`)
- 工具函式介面驗證透過契約檔案 (`contracts/util-interface.md`)

**失敗情境**：若實作過程中發現資料結構不足，必須立即回溯至 data-model.md 修訂，不得直接修改實作代碼繞過設計。

---

### III. 三問法則（決策守門人）

任何架構決策、功能修改、或重構，在執行前**必須**通過以下三個關鍵問題的審視：

1. **「是核心問題嗎？」** - 判斷此改動是否解決核心搶票流程的關鍵問題
   - 若否，應先聚焦核心功能（遵循 VII. MVP 原則）
   - 若是，進行第二問

2. **「有更簡單的方法嗎？」** - 判斷是否存在更簡潔的替代方案（遵循 YAGNI 原則）
   - 複雜度應有正當理由記錄在 spec 或計畫文件中
   - 若有更簡單方法，優先採用

3. **「會破壞相容性嗎？」** - 判斷改動是否影響既有平台、API、或使用者配置
   - 不得無故破壞相容性
   - 若必須破壞，需在 CHANGELOG 記錄遷移指南（依據 `docs/10-project-tracking/changelog_guide.md`）

**決策記錄**：三問法則的審視過程應記錄在對應的規格或計畫文件中。PR 評審時強制檢查此三問的回答。

---

### IV. 單一職責與可組合性（函數設計原則）

**函數設計原則**：每個函數必須有單一、明確的職責。複雜邏輯應分解為可組合的小函數。

**強制規則**：
- 函數名稱必須準確描述其職責（動詞 + 對象格式，如 `extract_date_keyword()` 而非 `process()`)
- 函數體長度建議 <50 行，超過應考慮分解
- 每個函數應有清晰的輸入驗證、邊界情況處理、與錯誤回報
- 依賴注入優先於全域狀態：優先傳遞參數而非讀取全域變數

**平台模組設計**：
- 每個平台實作（`tixcraft_*`、`kktix_*` 等）應是獨立可測試的模組
- 共用邏輯應提取至 `util.py`，透過明確的介面暴露（定義在 `contracts/util-interface.md`)
- 平台特定的複雜邏輯必須在 `specs/001-ticket-automation-system/spec.md` 的「平台特定考量」區塊記錄

**測試性**：函數設計必須便於單獨測試，不依賴外部狀態或副作用（純函數優先）。

---

### V. 設定驅動開發（使用者友善設計）

**終極原則**：所有可配置的行為都必須驅動自 `settings.json`，不得硬寫在程式碼中。

**強制規則**：

1. **配置架構**：
   - 主設定檔：`src/settings.json`
   - 配置 schema：`specs/001-ticket-automation-system/contracts/config-schema.md`（JSON schema 格式）
   - 多設定檔支援：`src/config_launcher.json`（用於快速切換）

2. **允許配置的項目**（不完整列表，新增功能時應評估是否納入）：
   - 平台選擇：`webdriver_type`（NoDriver / UC / Selenium）
   - 日期/時間關鍵字：`date_keyword`、`time_keyword`
   - 區域選擇：`area_keyword`
   - 票數選擇：`ticket_count`
   - 驗證碼辨識：`ocr_enable`
   - Debug 模式：`verbose`、`headless`
   - 高級選項：`advanced` 物件

3. **不得硬寫的項目**：
   - 平台 URL、CSS 選擇器（應在平台模組中定義常數，不在 settings.json）
   - 功能開關（除非使用者明確希望動態切換，否則應在程式邏輯中實作）
   - 實驗性功能啟用標誌（若非給使用者，應使用程式碼常數或環境變數）

4. **配置驗證**：所有讀取的配置必須透過 JSON schema 驗證，拒絕無效配置並提供清晰錯誤訊息

**新功能決策**：開發新功能時，先問「使用者是否需要動態控制此行為？」若答案為「是」，必須加入 settings.json 配置。

---

### VI. 測試驅動穩定性（品質守門人）

**不可協商的規則**：核心功能修改或新功能開發，必須有對應的測試驗證，且測試必須通過。

**測試層級**：

1. **單元測試**（Unit Tests）
   - 針對 `util.py` 中的共用函式（日期解析、區域選擇、OCR 等）
   - 位置：`tests/test_util.py`
   - 必須覆蓋邊界情況（空值、異常輸入、特殊字元等）

2. **整合測試**（Integration Tests）
   - 針對平台特定的完整流程（登入 → 選票 → 購票）
   - 位置：`tests/integration/test_[platform]_flow.py`
   - 應使用錄製的 HTTP 回應 (fixtures)，避免真實網站依賴

3. **回歸測試**（Regression Tests）
   - 自動化測試套件，於每次提交前執行
   - 位置：`.github/workflows/` 或 `scripts/run_tests.sh`
   - 失敗時阻止 merge

**測試執行**：
- 快速測試指令：`cd tickets_hunter && timeout 30 python -u nodriver_tixcraft.py --input src/settings.json`（見 CLAUDE.md 快速測試指令）
- 完整測試套件：`pytest tests/ -v`（若已配置 pytest）
- 新增平台時必須新增對應的集成測試

**品質門檻**：
- 核心路徑（日期選擇、票數選擇、購票流程）必須有 >70% 程式碼覆蓋率
- 新增功能必須附帶測試，測試必須通過
- 若無法編寫測試（例如需要真實網站互動），必須在 PR 中詳細文件化手動測試步驟

---

### VII. MVP 原則（最小可行產品優先）

**核心策略**：優先完整實作最小可行的核心流程，再逐步擴展至邊界情況與優化。

**應用方式**：

1. **功能優先級分類**：
   - **P1 (MVP)**：必須實作的核心功能（日期選擇、票數選擇、購票流程）
   - **P2**：重要特性（OCR 驗證碼、多設定檔、多平台）
   - **P3**：錦上添花（效能最佳化、進階報告、UI 美化）

2. **開發流程**：
   - 新功能先實作 P1 user stories，確保端對端流程可工作
   - 每個 P1 story 應是獨立可測、獨立可演示的最小單位
   - 通過 P1 story 測試後，再開發 P2 與 P3

3. **規格寫法**：規格文件（`spec.md`）中的 user stories 必須按優先級排序，P1 story 必須能獨立實作

4. **部署**：每個完成的 MVP 可獨立發佈，無需等待所有功能完成

**反面例子（禁止）**：不得「為了追求完美而無限延遲發佈」；寧可先發佈基礎版本，後續迭代改善。

---

### VIII. 文件與代碼同步（知識傳承）

**原則**：文件是代碼的一部分，必須同步維護。過時的文件比沒有文件更糟糕。

**文件結構**：

```
tickets_hunter/
├── README.md                           # 使用者導讀（維護 platform support table）
├── CONTRIBUTING.md                     # 貢獻指南
├── LEGAL_NOTICE.md                     # 法律聲明
├── docs/
│   ├── 01-getting-started/
│   │   ├── setup.md                   # 環境安裝
│   │   └── project_overview.md        # 專案概述
│   ├── 02-development/
│   │   ├── structure.md               # 程式結構與函數索引
│   │   ├── development_guide.md       # 開發規範
│   │   ├── ticket_automation_standard.md # 12 階段標準
│   │   ├── coding_templates.md        # 程式寫法範本
│   │   ├── documentation_workflow.md  # 文件維護流程
│   │   ├── logic_flowcharts.md        # 邏輯流程圖
│   │   ├── sound_notification_system.md # 聲音通知系統
│   │   ├── ticket_seat_selection_algorithm.md # 座位選擇演算法
│   │   ├── ibon_nodriver_vs_chrome_comparison.md # iBon 引擎比較
│   │   ├── kham_nodriver_vs_chrome_comparison.md # KHAM 引擎比較
│   │   ├── kktix_nodriver_vs_chrome_comparison.md # KKTIX 引擎比較
│   │   ├── ticketplus_nodriver_vs_chrome_comparison.md # TicketPlus 引擎比較
│   │   ├── tixcraft_family_nodriver_vs_chrome_comparison.md # TixCraft 家族引擎比較
│   │   └── README.md                  # 開發文件索引
│   ├── 03-api-reference/
│   │   ├── nodriver_api_guide.md      # NoDriver API（推薦）
│   │   ├── chrome_api_guide.md        # Chrome/UC 參考
│   │   ├── selenium_api_guide.md      # Selenium 參考
│   │   ├── ddddocr_api_guide.md       # OCR API
│   │   ├── cdp_protocol_reference.md  # CDP 協議完整參考（推薦深入閱讀）
│   │   ├── shadow_dom_pierce_guide.md # Shadow DOM 穿透指南
│   │   └── nodriver_selector_analysis.md # NoDriver 選擇器分析
│   ├── 04-testing-debugging/
│   │   ├── testing_execution_guide.md # 測試流程
│   │   ├── debugging_methodology.md   # 除錯方法論
│   │   └── reports/                   # 測試報告（自動生成）
│   ├── 05-troubleshooting/
│   │   ├── README.md                  # 問題索引
│   │   └── [platform]_*.md            # 平台特定問題
│   ├── 06-deployment/
│   │   └── pyinstaller_packaging_guide.md # 打包指南
│   ├── 07-project-tracking/
│   │   ├── changelog_guide.md         # CHANGELOG 維護指南
│   │   ├── accept_changelog.md        # 編輯歷史（自動生成）
│   │   ├── todo.md                    # 開發進度追蹤
│   │   ├── analyze-*.md               # 分析報告（自動生成）
│   │   └── debug-*.md                 # 除錯報告（自動生成）
│   ├── 08-refactoring/
│   │   ├── README.md                  # 重構索引
│   │   └── directory_restructuring_plan.md # 目錄重構計畫
│   └── README.md                      # 文件導航總覽
├── specs/
│   └── 001-ticket-automation-system/
│       ├── spec.md                    # 功能需求規格
│       ├── plan.md                    # 實作計畫
│       ├── research.md                # 技術研究
│       ├── data-model.md              # 資料結構設計
│       ├── quickstart.md              # 快速開始
│       ├── contracts/
│       │   ├── config-schema.md       # 配置 schema
│       │   ├── platform-interface.md  # 平台介面
│       │   └── util-interface.md      # 工具函式介面
│       └── checklists/
│           └── requirements.md        # 品質檢查清單
├── CLAUDE.md                           # Claude Code 專案指引（索引與快速指令）
└── .specify/memory/constitution.md     # 本檔案（專案憲章）
```

**同步規則**：

1. **每個文件的擁有者職責**：
   - `spec.md` 維護者：確保功能需求與實作代碼一致
   - `structure.md` 維護者：每當新增/刪除函數時同步更新
   - `README.md` 維護者：每當新增平台或功能時同步更新 platform support table
   - `CHANGELOG.md` 維護者：每個 PR merge 時記錄改動

2. **同步檢查清單**（PR 評審必檢）：
   - 程式碼改動是否對應 spec 中的需求？
   - 是否新增/修改了函數？若是，已更新 `structure.md` 嗎？
   - 是否新增平台支援？若是，已更新 `README.md` 嗎？
   - 是否修改了配置 schema？若是，已更新 `config-schema.md` 嗎？
   - 是否涉及 breaking changes？若是，已在 CHANGELOG 記錄遷移指南嗎？

3. **過時文件清理**：
   - 每季度檢查一次 `docs/08-troubleshooting/` 是否有過期的問題記錄
   - 移除平台不再支援時相應的文件
   - 標記實驗性功能以避免誤導

**強制工具**：commit 前強制執行 `/speckit.analyze` 檢查文件一致性（若使用 speckit 工作流）。

---

### IX. Git 提交規範與工作流程（版本控制紀律）

**提交訊息規範**：

所有提交必須遵循 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <subject>
<blank line>
<body>
<blank line>
<footer>
```

**Type 列表**（英文，不接受中文）：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `refactor`: 重構（非功能改動）
- `test`: 測試相關
- `perf`: 效能改善
- `chore`: 構建、相依性等維護工作
- `ci`: CI/CD 配置

**Scope**（可選但推薦）：
- 平台名稱：`tixcraft`、`kktix`、`ibon` 等
- 模組名稱：`ocr`、`util`、`config`、`nodriver_engine` 等

**Subject 規則**：
- 命令式語氣（"add" 而非 "added"）
- 首字母小寫
- 不加句號
- 限制在 50 個字符以內

**範例**：
```
feat(nodriver): add auto-scrolling for shadow DOM elements

Implemented smooth scrolling to element before clicking in NoDriver engine
to handle deeply nested Shadow DOM structures in iBon platform.

Closes #123
```

**提交工具**（推薦使用）：
- 使用 `/gsave` 指令自動生成規範化提交訊息
- `/gsave` 會自動分離公開檔案與機敏檔案為不同 commits（參見「雙 Repo 維護」區塊）

**分支策略**：
- 主線：`main`（生產發佈）
- 功能分支：`feat/[###-feature-name]`（對應 spec 的功能編號）
- 修復分支：`fix/[issue-number]-[description]`
- 文件分支：`docs/[description]`

**PR 評審守則**：
- 每個 PR 必須通過自動化測試
- 提交訊息必須遵循本規範
- PR 本身應链接相關 issues 或 spec 文件
- 檢查是否遵循前述所有 8 條原則（I-VIII）

**雙 Repo 維護**（重要）：

本專案採用雙 repo 架構：
- **Private Repo**（主力開發庫）：包含所有程式碼與機敏檔案（.claude/, docs/, CLAUDE.md, .specify/, specs/, FAQ/）
- **Origin Repo**（公開發布庫）：僅包含公開程式碼，不含機敏檔案

**自動分離機制**：
- `/gsave` 指令會自動將變更分離為兩個 commits：
  - **公開檔案 commit**：標準 commit 訊息（可推送到公開 repo）
  - **機敏檔案 commit**：帶有 `🔒 PRIVATE COMMIT` 標記（僅推送到私人 repo）

**標記格式**（機敏檔案 commit）：
```
📝 docs(private): update internal documentation

🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

Files modified:
  - .claude/commands/gpush.md
  - docs/02-development/structure.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FILTER MARKER FOR /publicpr ⚠️
Private file patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, FAQ/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**優勢**：
- 天然區分公開/機敏 commits，Git history 一目了然
- `/publicpr` 可透過 `FILTER MARKER` 快速識別並跳過機敏 commits
- 降低誤推機敏資料到公開 repo 的風險
- 符合憲法第 IV 條「單一職責原則」

詳細工作流程參考：`docs/11-git-workflow/dual-repo-workflow.md`

---

## 代碼品質標準

### Emoji 使用規範（不可協商）

**絕對禁止**：在 Python (`.py`)、JavaScript (`.js`) 等程式碼中使用 emoji。

**原因**：emoji 字符在 Windows cp950 編碼下會導致程式崩潰或亂碼。

**允許的用途**：Emoji 僅限於 Markdown 文檔（`.md`）中作為視覺輔助。

**程式碼中的正確做法**：
```python
# ✅ 正確
print("[SUCCESS] 購票成功")
logger.error("[ERROR] 選票失敗")

# ❌ 禁止
print("✅ 購票成功")
logger.error("❌ 選票失敗")
```

### 暫停機制（Pause Mechanism）

搶票系統涉及自動化網站互動，需要內建「暫停」機制以避免濫用或法律風險。

**強制要求**：
- 每次購票流程前必須提示使用者確認（stdout 訊息或 UI 對話框）
- 若使用者在 5 秒內未確認，應自動退出程序
- 所有自動化操作應有清晰的日誌輸出，便於審計
- 支援 Ctrl+C 優雅中止

**實作位置**：`util.py` 中的 `pause_before_checkout()` 或類似函數。

### 安全性原則

1. **認證資訊**：禁止在代碼或版本控制中硬寫密碼、API 金鑰等敏感資訊
   - 必須讀取自環境變數或外部配置檔
   - `.gitignore` 必須排除 `settings.json`、`.env` 等敏感檔案

2. **用戶隱私**：不得蒐集或上傳使用者個人資訊
   - 日誌中不得包含帳號、密碼、身份證號等
   - Cookie 與 session 資訊應在進程結束時清理

3. **代碼審查**（Code Review）：
   - 涉及敏感操作（登入、支付、個人資訊）的改動必須由社群審查
   - 明確記錄風險評估

---

## 治理機制

### 憲章的法律地位

本憲章為 Tickets Hunter 專案的最高指導原則。所有開發工作、決策與評審都必須遵循本憲章。

**違反本憲章的行為包括但不限於**：
- 提交未通過測試的代碼（違反 VI. 測試驅動穩定性）
- 硬寫配置值而非讀取自 settings.json（違反 V. 設定驅動開發）
- 忽視資料結構設計直接開發（違反 II. 資料結構優先）
- 新功能選擇 Chrome 版本而非 NoDriver（違反 I. NoDriver First）
- 提交未同步的文件（違反 VIII. 文件與代碼同步）

### 修訂流程

本憲章可因應專案發展而修訂。修訂流程：

1. **提案階段**：在 GitHub Issues 中提出修訂建議，包含修訂理由與影響分析
2. **社群討論**：至少等待 7 天以收集反饋
3. **核准**：維護者確認後進行修訂
4. **版本遞增**：依語意化版本控制 (Semantic Versioning)
   - MAJOR：刪除或重新定義原則（破壞相容性）
   - MINOR：新增原則或原則的大幅擴充
   - PATCH：澄清、措辭修正、錯別字
5. **遷移計畫**：MAJOR 版本必須提供遷移指南

### 版本政策

- **當前版本**：1.0.0（首次通過）
- **發佈節奏**：隨 Tickets Hunter 版本發佈（見 `README.md` 版本欄）
- **長期支援**：所有 MAJOR 版本保留最少 12 個月的支援期

### 合規審查

**定期審查**（每季度）：
- 檢查代碼庫是否遵循本憲章
- 列舉違反情況並提出改進計畫
- 更新 `docs/10-project-tracking/accept_changelog.md` 記錄審查結果

---

## 核心文件引用

執行階段開發指引請參閱以下文件（按查詢優先級）：

1. **規格與計畫**：`specs/001-ticket-automation-system/spec.md` + `plan.md`
2. **開發規範**：`docs/02-development/development_guide.md` + `ticket_automation_standard.md`
3. **API 參考**：`docs/06-api-reference/nodriver_api_guide.md`（優先）
4. **程式結構**：`docs/02-development/structure.md`
5. **除錯指南**：`docs/07-testing-debugging/debugging_methodology.md`
6. **快速指令**：`CLAUDE.md`（Claude Code 專用）

---

**版本**：1.0.1 | **通過日期**：2025-10-19 | **最後修訂**：2025-10-28
