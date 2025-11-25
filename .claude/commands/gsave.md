---
description: "產生英文 emoji 版 Git commit 訊息並提交變更"
model: Opus
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---
# 自動產生英文 emoji Git commit 訊息並提交

---

## 📜 Git 提交規範（遵循專案憲章第 IX 條）

本指令遵循專案憲章的 Git 提交規範，詳見：`.specify/memory/constitution.md`

### 提交訊息格式（混合格式）

**標準格式**：
```
emoji type(scope): subject

body (optional)

footer (optional)
```

**範例**：
```
✨ feat(nodriver): add auto-scrolling for shadow DOM elements

Implemented smooth scrolling to element before clicking in NoDriver engine
to handle deeply nested Shadow DOM structures in iBon platform.

- Add auto_scroll_before_click function (新增滾動至元素函數)
- Handle deeply nested Shadow DOM structures (處理深層嵌套 Shadow DOM)

Closes #123
```

### Type 列表（必須使用其中之一）

| Type | Emoji | 說明 | 範例 |
|------|-------|------|------|
| `feat` | ✨ | 新功能 | `✨ feat(kktix): add queue detection` |
| `fix` | 🐛 | 錯誤修復 | `🐛 fix(ibon): handle shadow DOM access` |
| `docs` | 📝 | 文件更新 | `📝 docs(api): update nodriver guide` |
| `refactor` | ♻️ | 重構 | `♻️ refactor(util): extract date parsing logic` |
| `test` | ✅ | 測試相關 | `✅ test(ocr): add edge case tests` |
| `perf` | ⚡ | 效能改善 | `⚡ perf(nodriver): optimize selector performance` |
| `chore` | 🔧 | 維護工作 | `🔧 chore(deps): update dependencies` |
| `ci` | 👷 | CI/CD 配置 | `👷 ci: add automated testing workflow` |

### Scope 清單（推薦但不強制）

**平台相關**：`tixcraft`, `kktix`, `ibon`, `ticketplus`, `kham`, `urbtix`, `cityline`, `teamear`, `indievox`

**模組相關**：`ocr`, `util`, `config`, `nodriver`, `AI`, `selenium`

**其他**：`ci`, `build`, `docs`, `test`, `release`

**智慧推薦**：本指令會根據修改的檔案自動推薦 scope，但您可自行調整或省略。

### Subject 規則

- ✅ 使用命令式語氣（"add" 而非 "added"）
- ✅ 首字母小寫
- ✅ 不加句號
- ✅ 限制在 50 個字符以內

---

## ⚠️ 重要提醒

**執行此指令前，建議先執行 `/gdefault` 清除本地敏感設定檔案**，避免將測試資料或敏感資訊提交到 Git。

**🌍 Commit 訊息語言規範**：
- **主題行使用混合格式**：emoji + type(scope): subject（英文）
- **描述可中英文並列**：英文在前，中文註解在括號內
- 範例格式：`✨ feat(nodriver): add feature (新增功能)`

## 🔧 進階選項：
- `--squash`: 將所有變更合併為單一 commit
- `--smart`: 智慧分類並自動合併相關變更
- `--check`: 僅檢查狀態，不執行提交
- `--force-clean`: 強制建立乾淨的 commit（避免歷史問題）

請按照以下步驟處理 Git 變更：

1. **自動更新版本號**：
   - 檢查是否有新的功能實作或重大變更
   - 根據變更類型自動更新版本號：
     - **✨ 新功能 (feat)**：次版本號 +1 (例如 2025.09.18 → 2025.09.19)
     - **🐛 重大修復 (fix)**：修訂版本號 +1 (例如 2025.09.18 → 2025.09.18.1)
     - **📝 文件/配置 (docs/chore)**：維持原版本號
   - 自動更新所有檔案中的 `CONST_APP_VERSION`：
     - `src/chrome_tixcraft.py`
     - `src/nodriver_tixcraft.py`
     - `src/settings.py`
     - `src/settings_old.py`
     - `src/config_launcher.py`
     - `README.md`
     - `src/www/settings.html`
   - 在 commit 訊息中標註版本更新
   - README.md 中的版本日期 '**⚡ 版本**：Tickets Hunter (2025.09.28)'

2. **智慧檢測（新增）**：
   - 掃描歷史是否包含 merge commits
   - 檢查是否有分支保護規則相關問題
   - 評估最佳提交策略並提供建議
   - 如果使用 `--check` 選項，在此步驟停止並顯示建議

3. **檢查 .gitignore 並排除忽略檔案**：
   - 讀取 `.gitignore` 檔案內容，解析忽略規則
   - 執行 `git status --porcelain` 取得所有變更檔案清單
   - 過濾掉 `.gitignore` 中定義的忽略檔案（如 settings.json、*.log 等）
   - 只處理應該納入版本控制的檔案變更
   - 如果所有變更都被忽略，提示使用者無檔案需要提交

4. **分析目前狀態**：
   - 執行 `git status` 查看變更檔案
   - 執行 `git diff --staged` 或 `git diff` 查看具體變更內容
   - 顯示過濾後的有效變更檔案清單

5. **智慧分類變更（新增）**：
   **如果使用 `--smart` 選項**：
   - 自動分析檔案變更的性質和關聯性
   - 智慧分組相關的變更（如同一功能的多個檔案）
   - 建議最佳的 commit 分組策略

   **如果使用 `--squash` 選項**：
   - 將所有變更合併為單一邏輯性 commit
   - 自動產生包含所有變更的綜合訊息

6. **分離公開與機敏檔案（核心邏輯）**：

   **機敏檔案清單定義**：
   ```
   .claude/          - Claude 自動化設定
   CLAUDE.md         - 專案開發規範
   docs/             - 技術文件和指南
   .specify/         - 規格模板和指令碼
   specs/            - 功能規格和設計文件
   FAQ/              - 常見問題解答
   .temp/            - 臨時測試資料（HTML/JS 網頁內容）
   ```

   **分離流程**：
   - 讀取所有變更檔案清單（已過濾 .gitignore）
   - 依據機敏檔案清單，將檔案分為兩組：
     - **公開檔案組**：src/, tests/, README.md, CHANGELOG.md 等程式碼和公開文件
     - **機敏檔案組**：上述機敏檔案清單中的檔案

   **分組策略**：
   - 如果同時有公開和機敏檔案變更 → 建立兩個 commits
   - 如果只有公開檔案變更 → 建立一個 commit（標準流程）
   - 如果只有機敏檔案變更 → 建立一個 commit（標記為 PRIVATE）

6.1. **分析公開檔案變更並分類**：
   對公開檔案組進行分類（如果有）：
   - 檢查所有公開檔案的類型和變更性質
   - 根據變更目的將檔案歸類到相同類別（feat, fix, docs, refactor 等）
   - 相同類別的變更將合併為單一 commit
   - 不同類別的變更將建立多個 commits

6.2. **分析機敏檔案變更**：
   對機敏檔案組進行分析（如果有）：
   - 統計機敏檔案變更數量
   - 列出所有機敏檔案路徑
   - 準備建立 PRIVATE 標記的 commit

6.5. **智慧 scope 推薦**：
   根據修改的檔案路徑，自動推薦合適的 scope（遵循憲章第 IX 條）：

   **公開檔案 scope 推薦規則**：
   - 修改 `src/nodriver_*.py` → 推薦 scope: `nodriver` 或 `nodriver_engine`
   - 修改 `src/*_tixcraft.py` → 推薦 scope: `tixcraft`
   - 修改 `src/*_kktix.py` → 推薦 scope: `kktix`
   - 修改 `src/*_ibon.py` → 推薦 scope: `ibon`
   - 修改 `src/*_ticketplus.py` → 推薦 scope: `ticketplus`
   - 修改 `src/*_kham.py` → 推薦 scope: `kham`
   - 修改 `src/util.py` → 推薦 scope: `util`
   - 修改 `src/settings.py` 或 `src/config_*.py` → 推薦 scope: `config`
   - 修改 `.github/workflows/*` → 推薦 scope: `ci`
   - 修改多個平台檔案 → 推薦 scope: `core` 或留空

   **機敏檔案固定使用 scope: `private`**：
   - 所有機敏檔案變更統一使用 `docs(private):` 或 `chore(private):`
   - 不需要細分 scope，因為這些檔案不會推送到公開 repo

   **注意**：scope 為推薦值，可以手動調整或省略。Scope 應加在 type 後面，格式為 `type(scope):`。

7. **產生 emoji commit 訊息**：
   **語言規範：混合格式（emoji + type(scope): subject）**

   根據變更類型選擇適合的 emoji 與 type（遵循憲章第 IX 條）：
   - ✨ `feat` - New feature (新功能)
   - 🐛 `fix` - Bug fix (錯誤修復)
   - 📝 `docs` - Documentation update (文件更新)
   - ♻️ `refactor` - Code refactoring (重構)
   - ✅ `test` - Test related (測試相關)
   - ⚡ `perf` - Performance improvement (效能改善)
   - 🔧 `chore` - Maintenance work (維護工作)
   - 👷 `ci` - CI/CD configuration (CI/CD 配置)

   **7.1 公開檔案 Commit 訊息格式**（標準格式）：
   ```
   ✨ feat(nodriver): implement auto ticket selection

   - Add nodriver_tixcraft_date_auto_select function (新增日期自動選擇函數)
   - Add async/await support for ticket selection logic (加入異步支援)
   - Integrate new functions into main workflow (整合至主流程)
   ```

   **7.2 機敏檔案 Commit 訊息格式**（帶 PRIVATE 標記）：
   ```
   📝 docs(private): update internal documentation

   🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

   This commit contains sensitive/internal files that should ONLY
   exist in the private repository.

   Files modified:
     - .claude/commands/gupdate.md
     - docs/02-development/structure.md
     - CLAUDE.md

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚠️  FILTER MARKER FOR /publicpr ⚠️
   Private file patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, FAQ/, .temp/
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

   **關鍵設計**：
   - 🔒 符號和 "PRIVATE COMMIT" 文字：視覺警告
   - "DO NOT PUSH TO PUBLIC REPO"：明確指令
   - 檔案清單：便於審查
   - "FILTER MARKER FOR /publicpr"：供自動化工具識別
   - 分隔線：增強視覺區分

8. **預覽變更**：

   **8.1 顯示分離結果摘要**：
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📋 檔案分離結果
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   公開檔案 (3 個):
     ✓ src/nodriver_tixcraft.py
     ✓ tests/test_tixcraft.py
     ✓ README.md

   機敏檔案 (2 個):
     🔒 .claude/commands/gupdate.md
     🔒 docs/02-development/structure.md

   將建立 2 個 commits：
     1. 公開檔案 commit (標準格式)
     2. 機敏檔案 commit (PRIVATE 標記)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

   **8.2 顯示 Commits 預覽**：
   - 按順序顯示所有即將建立的 commits（公開 → 機敏）
   - 完整顯示：Emoji + Type(scope): Subject + Body + 影響檔案
   - 機敏檔案 commit 會明確標示 🔒 PRIVATE 標記

   **8.3 詢問使用者**：
   「📝 檢視上述 commits，是否需要調整？(y/n/skip)」

   **8.4 編輯模式（若選擇 y）**：
   1. 選擇要編輯的 Commits（例如：1,3,5 或 all）
   2. 逐一編輯：Type, Scope, Subject, Body
   3. 完成後總預覽並最終確認

   **8.5 直接提交（若選擇 n 或 skip）**：
   - 使用自動產生的訊息，直接進入 Step 9

9. **執行分離提交**：

   **9.1 先提交公開檔案 commits**（如果有）：
   - 按類別依序建立 commits（feat, fix, docs 等）
   - 使用標準 commit 訊息格式
   - 執行流程：
     ```bash
     git add [公開檔案清單]
     git commit -m "[標準訊息]"
     ```
   - 顯示提交成功訊息

   **9.2 後提交機敏檔案 commit**（如果有）：
   - 使用 `git add -f` 強制加入機敏檔案（繞過 .gitignore）
   - 使用帶有 🔒 PRIVATE 標記的 commit 訊息
   - 執行流程：
     ```bash
     git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ FAQ/
     git commit -m "[PRIVATE 標記訊息]"
     ```
   - 顯示 🔒 PRIVATE COMMIT 提交成功訊息

   **9.3 智慧提交策略**（進階選項）：
   - **一般模式**：依序執行上述 9.1 → 9.2 流程
   - **`--force-clean` 模式**：建立不含歷史問題的乾淨提交
   - **`--squash` 模式**：將公開檔案合併為單一 commit，機敏檔案仍獨立

   **提交順序重要性**：
   - ✅ 先公開後機敏：確保公開 commits 在 history 前面，方便 `/publicpr` cherry-pick
   - ✅ 機敏檔案獨立：便於識別和過濾
   - ✅ 清晰的視覺區分：commit log 一目了然

## Commit 訊息格式範例（主題英文，描述可雙語）

### 分離提交範例（推薦模式）：

**情境：同時修改程式碼和內部文件**

```bash
# 變更檔案：
# - src/nodriver_tixcraft.py  (公開)
# - tests/test_tixcraft.py     (公開)
# - docs/02-development/structure.md  (機敏)
# - .claude/commands/gupdate.md (機敏)

# /gsave 會自動分離為兩個 commits：
```

**Commit #1（公開檔案）：**
```
✨ feat(nodriver): implement auto ticket selection

- Add nodriver_tixcraft_date_auto_select function (新增日期自動選擇函數)
- Add async/await support for ticket selection logic (加入異步支援)
- Integrate new functions into main workflow (整合至主流程)

影響檔案：
  M src/nodriver_tixcraft.py
  A tests/test_tixcraft.py
```

**Commit #2（機敏檔案）：**
```
📝 docs(private): update internal documentation

🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

This commit contains sensitive/internal files that should ONLY
exist in the private repository.

Files modified:
  - docs/02-development/structure.md (更新函數索引)
  - .claude/commands/gupdate.md (更新指令說明)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FILTER MARKER FOR /publicpr ⚠️
Private file patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, FAQ/, .temp/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

影響檔案：
  M docs/02-development/structure.md
  M .claude/commands/gupdate.md
```

---

### 傳統分類提交範例（向下相容）：

**設定檔類變更（多個 settings.json）：**
```
🔧 chore(config): optimize default settings and path configurations

- Restore auto_reload_page_interval to 5 seconds (恢復刷新間隔為 5 秒)
- Restore window_size to 600x1024 (恢復視窗大小)
- Fix CONST_EXCLUDE_DEFAULT spacing (修正關鍵字間距)
```

**功能實作類變更（多個 .py 檔案）：**
```
✨ feat(nodriver): implement nodriver version auto ticket selection

- Add nodriver_tixcraft_date_auto_select function (新增日期自動選擇函數)
- Add nodriver_tixcraft_area_auto_select function (新增區域自動選擇函數)
- Add async/await support for all ticket selection logic (加入異步支援)
```

**文件類變更（僅公開文件，如 README）：**
```
📝 docs(readme): update documentation for new src/ directory structure

- Update execution commands to use 'cd tickets_hunter/src' pattern (更新執行指令路徑)
- Reorganize project structure diagram (重組專案架構圖)
- Simplify Python module table (簡化模組說明表格)
```

**修復類變更（多個相關檔案）：**
```
🐛 fix(tixcraft): fix ticket selection and OCR handling issues

- Fix dropdown selection logic in chrome_tixcraft.py (修正下拉選單邏輯)
- Improve OCR error handling in util.py (改善 OCR 錯誤處理)
- Update selector strategies for modern web elements (更新選擇器策略)
```

## 工作流程優勢

### 自動分離公開與機敏檔案（新功能）
- **天然區分**：Commit history 天然區分公開/機敏，一目了然
- **自動過濾**：`/publicpr` 可直接識別 🔒 PRIVATE 標記跳過機敏 commits
- **降低風險**：減少誤推機敏資料到公開 repo 的風險
- **視覺警告**：🔒 符號和分隔線提供強烈視覺提示
- **單一職責**：符合憲法第 IV 條，一個 commit 只做一件事

### 邏輯化版本控制
- **類別分組**：相同性質的變更合併為單一 commit
- **語意清晰**：每個 commit 代表一個完整的功能或修復
- **減少雜訊**：避免過多細碎的 commit 影響歷史可讀性
- **智慧過濾**：自動排除 .gitignore 中的敏感檔案和設定檔

### 分類提交範例流程
```bash
# 假設有 7 個檔案變更
gsave -> 讀取 .gitignore -> 過濾忽略檔案 -> 分析後歸類為 2 個類別：
  filtered out: settings.json, *.log, chrome_profile/ (被 .gitignore 忽略)
  commit 1: ♻️ Refactor tixcraft date selection logic (1 個 .py 檔案)
  commit 2: 📝 Update command documentation (1 個 .md 檔案)
```

### 清晰的版本歷史
- **邏輯性提交**：每個 commit 包含完整的功能變更
- **易於審查**：相關檔案的變更集中在同一 commit
- **協作友善**：團隊成員容易理解每個變更的完整脈絡

## 錯誤處理與自動修復

### 常見問題自動處理：

1. **含有 merge commits**：
   - 自動偵測歷史中的 merge commits
   - 建議使用 `--force-clean` 避免推送問題
   - 提供 squash 重建選項

2. **分支保護相關**：
   - 預先檢查可能的推送限制
   - 建議適當的提交策略
   - 提醒後續 使用 /gpush 時的注意事項

3. **大量檔案變更**：
   - 自動建議使用 `--smart` 進行智慧分組
   - 避免產生過多細碎的 commits

### 智慧模式使用範例：

```bash
# 智慧分類多個相關變更
gsave --smart
-> 自動分組：UI改善、Bug修復、文件更新

# 合併為單一 commit（適合功能完成）
gsave --squash
-> 產生：🚀 Complete user authentication system

# 檢查模式（預覽不執行）
gsave --check
-> 顯示：建議使用 --force-clean 避免歷史問題

# 強制乾淨提交（避免歷史問題）
gsave --force-clean
-> 建立：不含 merge commits 的乾淨提交
```

## 📌 語言規範總結

**Commit 訊息語言規範**：
- ✅ **主題行使用混合格式** - emoji + type(scope): subject（英文）
- ✅ **描述（Body）可中英文並列** - 英文在前，中文註解在括號內
- 💡 **範例格式**：`✨ feat(nodriver): add feature X (新增功能 X)`
- 🎯 **目的**：兼顧國際標準（Conventional Commits）與團隊溝通效率

---

## 📚 延伸閱讀

- **專案憲章**：`.specify/memory/constitution.md`（第 IX 條：Git 提交規範與工作流程）
- **Conventional Commits 規範**：https://www.conventionalcommits.org/
- **專案開發指引**：`CLAUDE.md`（Git 工作流程章節）
- **配對指令**：`/gupdate`（更新版本）、`/gdefault`（清除敏感設定）

$ARGUMENTS