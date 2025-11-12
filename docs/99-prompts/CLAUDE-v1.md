**文件說明**：CLAUDE.md 的舊版本（v1.0），作為版本歷史與參考檔案保留。

**最後更新**：2025-11-12

---

# CLAUDE.md (v1.0)

專案：Tickets Hunter - 多平台搶票自動化系統

---

## 憲法遵循聲明

**最高指導原則**：`.specify/memory/constitution.md`

所有開發工作**必須**：
1. 查詢憲法中的相關原則
2. 嚴格遵循憲法規範
3. 違反憲法的行為必須拒絕

**9 大核心原則**（必須查詢憲法詳細內容）：
- **I. NoDriver First** - 技術架構優先性（NoDriver > UC > Selenium）
- **II. 資料結構優先** - 設計先於實作（結構決定一切）
- **III. 三問法則** - 決策守門人（核心？簡單？相容？）
- **IV. 單一職責與可組合性** - 函數設計原則（小函數組合）
- **V. 設定驅動開發** - 使用者友善設計（settings.json 控制所有行為）
- **VI. 測試驅動穩定性** - 品質守門人（核心修改必須實測）
- **VII. MVP 原則** - 最小可行產品優先（完整核心流程優先）
- **VIII. 文件與代碼同步** - 知識傳承（文件是代碼一部分）
- **IX. Git 提交規範與工作流程** - 版本控制紀律（英文主題行、gsave 指令）

詳細規範請查詢：`.specify/memory/constitution.md`

---

## 工作模式決策樹

### 📝 一般開發流程（日常使用）

**適用場景**：日常開發、小型功能、Bug 修復

- **小型功能開發**：Accept Edits On 模式直接開發
- **Bug 修復**：規格檢查 → 快速除錯 → 修復 → 測試
- **代碼重構**：遵循憲法第 III 條（三問法則）決策

**必須遵循**：
- 憲法規範（`.specify/memory/constitution.md`）
- 測試驅動穩定性（憲法第 VI 條）
- 文件與代碼同步（憲法第 VIII 條）

### 🏗️ 重大功能開發（speckit 規格驅動）

**適用場景**：
- 跨多個模組的大型功能
- 需要詳細設計文件的複雜功能
- 多人協作的專案

**流程**：查看「speckit 工作流程」區塊（文件後段）

---

## 🎯 開發策略：NoDriver First

**遵循憲法第 I 條**：查詢 `.specify/memory/constitution.md` 詳細規範

**優先順序**：
1. **NoDriver** - 推薦（預設、最佳反偵測）
2. **UC (Undetected Chrome)** - 舊版回退（需要繞過偵測時）
3. **Selenium** - 標準場景（測試環境）

**平台維護策略**：
- NoDriver 版本：接受新功能開發 + Bug 修復
- Chrome Driver 版本：僅嚴重錯誤修復（進入維護模式）

**設定檔**：`settings.json` (`webdriver_type` 欄位)

---

## 📚 文件導航

### 🆕 初次接手專案
1. `docs/01-getting-started/setup.md` - 環境設定
2. `docs/01-getting-started/project_overview.md` - 了解架構
3. `docs/02-development/structure.md` - 程式結構
4. `docs/07-testing-debugging/testing_execution_guide.md` - 執行測試

### 🚀 開發新功能
**按順序查閱**：
1. `docs/02-development/development_guide.md` - 開發規範
2. `docs/02-development/ticket_automation_standard.md` - 12 階段標準
3. `docs/02-development/structure.md` - 現有實作參考
4. `docs/03-mechanisms/` - 12 階段機制文件 ⭐
   - `04-date-selection.md` - 日期選擇機制（含代碼片段）
   - `05-area-selection.md` - 區域選擇機制（含代碼片段）
   - `07-captcha-handling.md` - 驗證碼處理機制（含代碼片段）
5. `docs/06-api-reference/cdp_protocol_reference.md` - CDP 協議完整參考（NoDriver 深入）⭐
6. `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API（優先）
7. `docs/06-api-reference/nodriver_selector_analysis.md` - 選擇器優化指南
8. `docs/02-development/coding_templates.md` - 程式寫法範本

### 🔍 除錯問題
**按順序查閱**：
1. `docs/02-development/structure.md` - 查找函數定義
2. `docs/05-validation/` - 規格驗證與程式碼對照 ⭐
   - `spec-validation-matrix.md` - 追蹤 FR 實作狀態
   - `platform-checklist.md` - 評估平台完成度
   - `fr-to-code-mapping.md` - 快速找到程式碼位置
3. `docs/06-api-reference/cdp_protocol_reference.md` - CDP 協議參考（推薦深入閱讀）⭐
4. `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API（推薦）
5. `docs/06-api-reference/shadow_dom_pierce_guide.md` - Shadow DOM 穿透指南（ibon 必讀）⭐
6. `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法論
7. `docs/08-troubleshooting/README.md` - 修復記錄索引

### 🧪 執行測試
1. `docs/07-testing-debugging/testing_execution_guide.md` - 標準測試流程
2. `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法

### 🔗 Git 與發布工作流程
1. `docs/12-git-workflow/dual-repo-workflow.md` - 雙 Repo 維護指南 ⭐
   - 日常開發流程（/gsave → /gpush → /privatepush）
   - 發布流程（/publicpr 到公開 Repo）
   - 機敏檔案管理
   - 常見問題排解

**⚠️ Git 推送安全規則（NON-NEGOTIABLE）**：

**核心原則**：
- ✅ **強制使用 `/gsave` 建立 commit**（包含 AI 自動模式）
- ❌ **嚴禁使用 `git commit` 手動提交**
- ✅ **所有 push 操作只能推送到私人庫**（`private`）
- ❌ **嚴格禁止直接推送到公開庫**（`origin`）

**Repo 位址**：
- 私人庫：`https://github.com/bouob/private-tickets-hunter.git` (remote: `private`)
- 公開庫：`https://github.com/bouob/tickets_hunter.git` (remote: `origin`)

**推送指令用途**：
1. **`/gpush`** - 推送一般 commits 到私人庫
   - 目標：`private/main`
   - 用途：推送公開程式碼變更（但仍推到私人庫）
   - 自動過濾 PRIVATE commits

2. **`/privatepush`** - 推送機敏檔案 commits 到私人庫
   - 目標：`private/main`
   - 用途：推送 `.claude/`, `docs/`, `specs/` 等機敏檔案
   - 只推送帶 🔒 PRIVATE 標記的 commits

3. **`/publicpr`** - 建立 PR 到公開庫（唯一合法的公開庫推送方式）
   - 目標：`origin` (透過 PR)
   - 用途：正式發布到公開 repo
   - 自動過濾機敏檔案，僅推送公開代碼

**正確流程**：
```bash
/gsave          # 提交變更（自動分離公開/機敏檔案）
/gpush          # 推送公開 commits 到私人庫
/privatepush    # 推送機敏 commits 到私人庫
/publicpr       # 建立 PR 到公開庫（發布時使用）
```

**錯誤範例**（嚴格禁止）：
- ❌ `git commit -m "..."` - 手動提交，必須使用 `/gsave`
- ❌ `git push origin main` - 直接推送到公開庫，可能洩露機敏資料
- ❌ `git push` - 預設 remote 可能錯誤
- ❌ 直接推送到 origin - 必須使用 `/publicpr`

**正確範例**：
- ✅ `/gsave` - 建立 commit（唯一合法方式）
- ✅ `/gpush` - 推送一般 commits
- ✅ `/privatepush` - 推送機敏 commits
- ✅ `/publicpr` - 建立 PR 發布到公開庫

---

## 🔧 Accept Edits On 工作流程

### 核心流程
1. **完成功能修改** → 符合所有憲法規範（遵循 constitution.md）
2. **自動執行背景測試** → 30 秒 timeout，輸出至 `.temp/test_output.txt`
3. **分析測試結果** → 失敗時觸發文件檢查模式
4. **[強制] 使用 `/gsave` 提交變更** → 自動分離公開/機敏檔案，確保 commit 品質
5. **[強制] 記錄完成項目** → `docs/10-project-tracking/accept_changelog.md`
6. **[speckit 專案] 一致性檢查** → 執行 `/speckit.analyze`（如適用）
7. **驗證記錄完成** → 檢查點
8. **標記 todo 完成**
9. **查找下一個 todo** → `docs/10-project-tracking/todo.md`

### 文件檢查模式（測試失敗時）
0. **檢查 Spec**（新增）：`specs/001-ticket-automation-system/spec.md` + `plan.md`
   - 功能需求（FR-xxx）：確保修復符合原始設計
   - 成功標準（SC-xxx）：驗證修復達到可測量目標
1. 讀取 API 指南（根據 `webdriver_type`）
2. 查詢憲法相關原則（`.specify/memory/constitution.md`）
3. 搜尋專案文件（structure.md、debugging_methodology.md、troubleshooting/）
4. 搜尋網路資料（可選）
5. 綜合分析與修正

---

## 🚨 快速除錯

**檢查清單**：
1. ✅ 檢查功能規格：`specs/001-ticket-automation-system/spec.md`
   - 查找相關的功能需求（FR-xxx）
   - 查找相關的成功標準（SC-xxx）
2. ✅ 讀取 `settings.json` 確認 `webdriver_type`
3. ✅ 查閱 `docs/06-api-reference/nodriver_api_guide.md`（優先）
4. ✅ 檢查 `docs/08-troubleshooting/README.md`
5. ✅ 啟用 Debug：`config_dict["advanced"]["verbose"] = True`

---

## 📋 Spec 檢查指南（除錯時必讀）

**檢查路徑**：`specs/001-ticket-automation-system/`

**除錯時必查項目**：

### 1. 功能需求（FR-xxx）
確保修復符合原始功能需求
- 例：FR-017（日期關鍵字匹配）、FR-058（錯誤分類）
- 在 `spec.md` 中搜尋「功能需求」區塊

### 2. 成功標準（SC-xxx）
驗證修復達到可測量的目標
- 例：SC-002（90% 關鍵字成功率）、SC-005（95% 元素互動成功率）
- 在 `spec.md` 中搜尋「成功標準」區塊

### 3. 核心設計原則
確保修復遵循設計原則（在 `spec.md` 中的「核心設計原則」區塊）
- 配置驅動架構（settings.json 控制所有行為）
- 三層回退策略（關鍵字 → 模式 → 手動）
- 函數分解原則（單一職責、可組合性）

### 4. 平台特定考量
檢查平台特定的實作細節（在 `spec.md` 中的「平台特定考量」區塊）
- TixCraft: Cookie 登入、即將開賣頁面
- iBon: Shadow DOM、Angular SPA
- KKTIX: 排隊處理、價格清單
- TicketPlus: 展開面板、實名對話框
- KHAM: 自動座位切換

### 5. 假設與約束
確認修復在技術與法律約束範圍內
- 瀏覽器版本（Chrome 90+）
- 記憶體限制（<500MB）
- 法律合規性（個人使用，禁止商業黃牛）

**實務範例**：
- **問題**：ibon 日期選擇關鍵字無法匹配
- **Spec 檢查**：
  - FR-017: 支援多關鍵字、逗號分隔？
  - FR-018: 是否實作回退到 auto_select_mode？
  - SC-002: 90% 成功率是否達成？
- **修正方向**：確保關鍵字匹配邏輯、回退邏輯、auto_select_mode 支援

---

## 🧪 快速測試指令

**重要**：測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即進入暫停狀態。

**NoDriver 版本**（Git Bash）：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && echo "" > .temp/test_output.txt && timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**NoDriver 版本**（Windows CMD）：
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

**關鍵修正**：檔案路徑必須加上 `src/` 前綴
- ✅ 正確：`python -u src/nodriver_tixcraft.py --input src/settings.json`
- ❌ 錯誤：`python -u nodriver_tixcraft.py --input src/settings.json`（檔案在 src/ 目錄下）

**檢查輸出（驗證程式邏輯）**：

```bash
# 1. 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 2. 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 3. 檢查關鍵流程節點
grep "Match Summary\|Selected target\|clicked\|navigat" .temp/test_output.txt

# 4. 快速檢查錯誤（輔助）
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

**驗證重點**：
- ✅ 日期匹配數量是否符合預期（`Total dates matched`）
- ✅ 區域匹配數量是否符合預期（`Total areas matched`）
- ✅ 選擇策略是否正確執行（`auto_select_mode`）
- ✅ AND 邏輯/回退機制是否觸發（`AND logic failed` → 回退到下一組）

**詳細邏輯流程圖**：查看 `docs/02-development/logic_flowcharts.md`
**詳細測試指南**：查看 `docs/07-testing-debugging/testing_execution_guide.md`

---

## 📋 常見問題索引

### 🚨 技術問題
- **CDP 協議查詢** → `docs/06-api-reference/cdp_protocol_reference.md`
- **CDP 點擊失敗** → `docs/06-api-reference/chrome_api_guide.md`
- **Shadow DOM** → `docs/07-testing-debugging/debugging_methodology.md`
- **NoDriver API** → `docs/06-api-reference/nodriver_api_guide.md`

### 📊 規格與驗證問題
- **FR 實作狀態查詢** → `docs/05-validation/spec-validation-matrix.md`
- **平台功能完整性** → `docs/05-validation/platform-checklist.md`
- **快速定位函數位置** → `docs/05-validation/fr-to-code-mapping.md`

### 🏗️ 新平台開發流程
- **12-Stage 機制文件** → `docs/03-mechanisms/README.md`
- **日期選擇實作** → `docs/03-mechanisms/04-date-selection.md`
- **區域選擇實作** → `docs/03-mechanisms/05-area-selection.md`
- **驗證碼處理實作** → `docs/03-mechanisms/07-captcha-handling.md`

### 🌐 Shadow DOM & 選擇器
- **Shadow DOM 穿透** → `docs/06-api-reference/shadow_dom_pierce_guide.md`
- **選擇器優化** → `docs/06-api-reference/nodriver_selector_analysis.md`

### 🎫 平台問題
- **ibon Cookie** → `docs/08-troubleshooting/ibon_cookie_troubleshooting.md`
- **ibon NoDriver 座位選擇** → `docs/08-troubleshooting/ibon_nodriver_fixes_2025-10-03.md`
- **驗證碼辨識** → `docs/06-api-reference/ddddocr_api_guide.md`

### 💻 環境問題
- **MacOS ARM** → `docs/08-troubleshooting/ddddocr_macos_arm_installation.md`
- **編碼錯誤 (cp950)** → 檢查程式碼中是否使用 emoji

**完整索引** → `docs/08-troubleshooting/README.md`

---

## 📐 程式碼規範

**遵循憲法『程式碼品質標準』**：查詢 `.specify/memory/constitution.md` 詳細規範

### Emoji 使用規範 (NON-NEGOTIABLE)
- **✅ 允許**：Emoji 僅限 `*.md` 文件中使用
- **❌ 禁止**：`*.py`、`*.js` 中禁止 emoji
- **❌ 禁止**：print()、console.log() 輸出中禁止 emoji
- **原因**：emoji 導致 Windows cp950 編碼錯誤（會導致程式崩潰）

**正確範例**：`print("[SUCCESS] 操作成功")`
**錯誤範例**：`print("✅ 操作成功")`

### 其他規範
詳細規範請查詢：`.specify/memory/constitution.md`（暫停機制、安全性原則、Code Review 標準等）

---

## 🏗️ speckit 工作流程（規格驅動開發）

**使用時機**：僅限重大功能開發、跨模組功能、多人協作專案

### 完整流程
1. `/speckit.specify [描述]` - 建立功能規格
2. `/speckit.clarify` - 澄清規格不足（可選）
3. `/speckit.plan` - 生成實作計畫
4. `/speckit.tasks` - 生成任務清單
5. `/speckit.implement` - 執行實作
6. `/speckit.analyze` - 一致性檢查

### 詳細說明
完整的 speckit 指令說明、規格資料夾結構、使用範例，請查閱：
- `.specify/memory/` - speckit 系統文件與憲法
- 相關 slash commands: `/speckit.*`

---

## 📚 核心文件索引

### 開發架構（新平台必讀）
```
docs/02-development/ticket_automation_standard.md  ← 12 階段標準
    ↓
docs/02-development/structure.md  ← 實作分析 + 評分
    ↓
docs/02-development/development_guide.md  ← 開發規範
```

### 除錯文件
- `docs/02-development/structure.md` - 函數索引 ⭐
- `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API ⭐（推薦）
- `docs/06-api-reference/chrome_api_guide.md` - Chrome/UC 參考
- `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法論 ⭐
- `docs/07-testing-debugging/testing_execution_guide.md` - 測試指南 ⭐

### 疑難排解
- `docs/08-troubleshooting/README.md` - 索引 ⭐
- `docs/08-troubleshooting/ibon_*.md` - ibon 特定問題

### 其他
- `docs/09-deployment/pyinstaller_packaging_guide.md` - 打包指南
- `docs/10-project-tracking/changelog_guide.md` - CHANGELOG 指南 ⭐
- `docs/02-development/coding_templates.md` - 程式範本
- `docs/02-development/documentation_workflow.md` - 文件維護流程

---

## 💡 使用原則

- ❌ 不要在 CLAUDE.md 重複 docs 內容
- ✅ 指向對應 docs 文件
- ✅ CLAUDE.md 只保留索引、核心原則、快速指令
