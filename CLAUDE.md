# CLAUDE.md v2.0（優化版本）

**專案**：Tickets Hunter - 多平台搶票自動化系統
**版本**：v2.1
**最後更新**：2025-12-23

---

## 🚀 Quick Reference（速查表）

### 最常見任務快速路徑

#### 🐛 Bug 修復（3 步驟）
1. **檢查規格**：`docs/05-validation/README.md`（索引）→ `specs/.../spec.md`（FR-xxx, SC-xxx）
2. **定位函數**：`docs/02-development/structure.md`
3. **執行測試**：`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`

#### ✨ 新增功能（3 步驟）
1. **查閱標準**：`docs/02-development/ticket_automation_standard.md`（12 階段定義）
2. **查找機制**：`docs/03-mechanisms/README.md`（12 階段詳細索引）
3. **編寫代碼**：`docs/02-development/coding_templates.md`

#### 📝 文件更新（3 步驟）
1. **同步代碼**：憲法第 VIII 條（文件與代碼同步）
2. **記錄變更**：`docs/10-project-tracking/accept_changelog.md`
3. **一致性檢查**：`/speckit.analyze`（speckit 專案）

### 關鍵指令速查

| 任務 | 指令 | 說明 |
|------|------|------|
| 清除敏感設定 | `/gdefault` | 清除本地敏感設定檔案 |
| 更新版本號 | `/gupdate` | 更新專案版本日期 |
| 生成 CHANGELOG | `/gchange` | 根據未推送 commits 生成變更日誌 |
| 提交變更 | `/gsave` | 自動分離公開/機敏檔案 |
| 推送代碼 | `/gpush` | 推送所有 commits 到私人庫 |
| 發布 PR | `/publicpr` | 建立 PR 到公開庫（僅發布時） |
| 建立 Release | `/publicrelease` | 建立 Release Tag 並觸發 Actions |
| 快速測試 | `timeout 30 python -u src/...` | 30 秒快速測試 |
| MCP 即時除錯 | `/mcpstart` | 啟動 Chrome 除錯模式（固定端口 9222） |
| 規格分析 | `/speckit.analyze` | 跨產物一致性檢查 |
| Speckit 同步 | `/speckit.sync` | 從 GitHub 同步 speckit 並中文化 |
| 除錯診斷 | `/debug` | 專業除錯工具（Spec + 憲法） |
| 尋找重複 issues | `/dedupe` | 尋找相似的 GitHub issues |
| 分析 issues | `/review-issues` | 分析開啟的 issues 並提供建議 |

### 緊急除錯 5 步驟

1. **讀取錯誤**：`.temp/test_output.txt`
2. **檢查規格**：`docs/05-validation/README.md`（索引）→ FR-xxx, SC-xxx
3. **查找 API**：`docs/06-api-reference/nodriver_api_guide.md`
4. **搜尋案例**：`docs/08-troubleshooting/README.md`
5. **啟用日誌**：請使用者在「進階設定」啟用「輸出除錯訊息」

### MCP 即時除錯（Chrome DevTools 連接）

透過 MCP 連接 Chrome 瀏覽器，可即時操作頁面、檢查網路請求、執行 JavaScript。

**相關檔案**：
- 設定檔：`.mcp.json`（Chrome DevTools MCP 設定，固定端口 9222）
- 詳細指南：`docs/07-testing-debugging/mcp_integration_guide.md`

**啟動流程**：
```bash
# 執行 /mcpstart 指令
/mcpstart

# Claude 會詢問運行模式：
# 1. 測試 NoDriver 設定 - 透過 NoDriver 執行 settings.json
# 2. 直接開啟網頁 - 僅啟動 Chrome，手動瀏覽
```

**重新連接**：
如果連接斷開，使用 `/mcp reconnect chrome-devtools` 即可重新連接（無需重啟 Claude Code）。

**常用 MCP 工具**：
| 工具 | 用途 |
|------|------|
| `mcp__chrome-devtools__take_snapshot` | 擷取 DOM 結構 |
| `mcp__chrome-devtools__take_screenshot` | 截圖 |
| `mcp__chrome-devtools__list_network_requests` | 檢查 API 呼叫 |
| `mcp__chrome-devtools__evaluate_script` | 執行 JavaScript |
| `mcp__chrome-devtools__click` | 點擊元素 |
| `mcp__chrome-devtools__navigate_page` | 導航到指定 URL |

**注意**：使用固定端口 9222，`.mcp.json` 無需每次更新。Chrome 使用獨立 profile，登入狀態會保留。

---

## 🧭 任務類型自動判斷

### 識別關鍵詞 → 工作流程

| 用戶提及 | 任務類型 | 優先查閱 | 工作流程 |
|----------|----------|----------|----------|
| "修復"、"錯誤"、"bug" | **Bug 修復** | Spec → structure.md → troubleshooting | 快速除錯流程 |
| "新增"、"實作"、"開發" | **新功能** | 12-Stage Standard → mechanisms | 開發流程 |
| "文檔"、"說明"、"註解" | **文件更新** | documentation_workflow.md | 文件同步流程 |
| "測試"、"驗證" | **測試執行** | testing_execution_guide.md | 測試流程 |
| "優化"、"重構" | **代碼改進** | 憲法第 III 條（三問法則） | 三問決策 |
| "規格"、"設計" | **規格驅動** | speckit 工作流程 | speckit 流程 |

### 平台識別 → 特定指南

| 提及平台 | 優先查閱 | 特殊考量 |
|----------|----------|----------|
| **TixCraft** | `structure.md` TixCraft 區塊 | Cookie 登入、即將開賣頁面 |
| **iBon** | `shadow_dom_pierce_guide.md` | Shadow DOM、Angular SPA |
| **KKTIX** | `structure.md` KKTIX 區塊 | 排隊處理、價格清單 |
| **TicketPlus** | `structure.md` TicketPlus 區塊 | 展開面板、實名對話框 |
| **KHAM** | `structure.md` KHAM 區塊 | 自動座位切換 |
| **FamiTicket** | NoDriver 實作參考 | 全家網票務流程 |
| **Cityline** | NoDriver 實作參考 | 香港城市電腦售票 |

---

## 📜 憲法（行為紅線）

**位置**：`.specify/memory/constitution.md` | **版本**：2.0.0

憲法定義**不可違反的行為規則**，不限制思考方式。

### 7 大行為規範（速記）

| 原則 | 類型 | 核心要點 |
|------|------|----------|
| **I. 技術架構** | MUST | NoDriver > UC > Selenium |
| **II. 共用庫保護** | MUST | util.py 改動需跨平台/跨 Driver 分析 |
| **III. 設定驅動** | MUST | settings.json 控制所有可配置行為 |
| **IV. 程式碼安全** | MUST | 禁 emoji in .py、禁硬寫敏感資訊 |
| **V. Git 工作流程** | MUST | /gsave 提交、雙 Repo 安全 |
| **VI. 測試驗證** | SHOULD | 核心修改應有測試驗證 |
| **VII. 文件同步** | SHOULD | 程式碼變更應同步文件 |

**MUST**：無例外，違反阻擋合併
**SHOULD**：允許例外，需記錄理由

**詳細規範**：查詢 `.specify/memory/constitution.md`

---

## 🎯 開發策略：NoDriver First

**遵循憲法第 I 條**：`.specify/memory/constitution.md`

**優先順序**：
1. **NoDriver** - 推薦（預設、最佳反偵測）
2. **UC (Undetected Chrome)** - 舊版回退（需要繞過偵測時）
3. **Selenium** - 標準場景（測試環境）

**平台維護策略**：
- NoDriver 版本：接受新功能開發 + Bug 修復
- Chrome Driver 版本：僅嚴重錯誤修復（進入維護模式）

**設定檔**：`settings.json` (`webdriver_type` 欄位)

---

## 📚 文件導航與常見問題

### 🆕 初次接手專案
1. `docs/01-getting-started/setup.md` - 環境設定
2. `docs/01-getting-started/project_overview.md` - 了解架構
3. `docs/02-development/structure.md` - 程式結構
4. `docs/07-testing-debugging/testing_execution_guide.md` - 執行測試

### 按任務類型查找

#### 🐛 除錯問題（Bug Fixing）
- **函數定位** → `docs/02-development/structure.md` ⭐
- **規格驗證** → `docs/05-validation/spec-validation-matrix.md`
- **程式碼對照** → `docs/05-validation/fr-to-code-mapping.md`
- **NoDriver API** → `docs/06-api-reference/nodriver_api_guide.md` ⭐
- **CDP 協議** → `docs/06-api-reference/cdp_protocol_reference.md` ⭐
- **除錯方法** → `docs/07-testing-debugging/debugging_methodology.md` ⭐
- **修復記錄** → `docs/08-troubleshooting/README.md` ⭐
- **Issues FAQ** → `docs/10-project-tracking/issues-faq-tracking.md` ⭐ 新增

#### 🏗️ 開發新功能（Feature Development）
- **12 階段標準** → `docs/02-development/ticket_automation_standard.md` ⭐
- **開發規範** → `docs/02-development/development_guide.md`
- **現有實作** → `docs/02-development/structure.md`
- **日期選擇** → `docs/03-mechanisms/04-date-selection.md`
- **區域選擇** → `docs/03-mechanisms/05-area-selection.md`
- **驗證碼處理** → `docs/03-mechanisms/07-captcha-handling.md`
- **程式範本** → `docs/02-development/coding_templates.md`

#### 🌐 特定技術（Specialized Topics）
- **Shadow DOM** → `docs/06-api-reference/shadow_dom_pierce_guide.md` ⭐
- **選擇器優化** → `docs/06-api-reference/nodriver_selector_analysis.md`
- **驗證碼辨識** → `docs/06-api-reference/ddddocr_api_guide.md`
- **Chrome API** → `docs/06-api-reference/chrome_api_guide.md`


#### 🧪 測試與除錯（Testing & Debugging）
- **測試執行** → `docs/07-testing-debugging/testing_execution_guide.md` ⭐
- **除錯方法** → `docs/07-testing-debugging/debugging_methodology.md` ⭐
- **邏輯流程圖** → `docs/02-development/logic_flowcharts.md`

#### 📦 部署與發布（Deployment）
- **CHANGELOG 指南** → `docs/10-project-tracking/changelog_guide.md` ⭐
- **Git 工作流程** → `docs/12-git-workflow/dual-repo-workflow.md` ⭐

#### 📋 專案追蹤（Project Tracking）
- **待辦事項** → `docs/10-project-tracking/todo.md` ⭐
- **Issues FAQ** → `docs/10-project-tracking/issues-faq-tracking.md` ⭐
- **自動執行記錄** → `docs/10-project-tracking/accept_changelog.md` ⭐
- **CHANGELOG 指南** → `docs/10-project-tracking/changelog_guide.md`

<details>
<summary>📖 完整開發架構文件樹（點擊展開）</summary>

### 開發架構（新平台必讀）
```
docs/02-development/ticket_automation_standard.md  ← 12 階段標準
    ↓
docs/02-development/structure.md  ← 實作分析 + 評分
    ↓
docs/02-development/development_guide.md  ← 開發規範
```

### 所有核心文件
- `docs/02-development/structure.md` - 函數索引 ⭐
- `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API ⭐
- `docs/06-api-reference/chrome_api_guide.md` - Chrome/UC 參考
- `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法論 ⭐
- `docs/07-testing-debugging/testing_execution_guide.md` - 測試指南 ⭐
- `docs/08-troubleshooting/README.md` - 疑難排解索引 ⭐
- `docs/10-project-tracking/todo.md` - 待辦事項清單 ⭐
- `docs/10-project-tracking/changelog_guide.md` - CHANGELOG 指南 ⭐
- `docs/10-project-tracking/issues-faq-tracking.md` - Issues FAQ 追蹤 ⭐
- `docs/10-project-tracking/accept_changelog.md` - 自動執行記錄 ⭐
- `docs/02-development/coding_templates.md` - 程式範本
- `docs/02-development/documentation_workflow.md` - 文件維護流程

</details>

---

## 🔗 Git 工作流程

### ⚠️ Git 推送安全規則（NON-NEGOTIABLE）

**核心原則**：
- ✅ **強制使用 `/gsave` 建立 commit**（包含 AI 自動模式）
- ❌ **嚴禁使用 `git commit` 手動提交**
- ✅ **只推送到私人庫**（`private`）
- ❌ **嚴禁直接推送到公開庫**（`origin`）
- ⚠️ **不從公開庫拉回變更**（單向流程，避免破壞 private history）

**Repo 位址**：
- 私人庫：`https://github.com/bouob/private-tickets-hunter.git` (remote: `private`)
- 公開庫：`https://github.com/bouob/tickets_hunter.git` (remote: `origin`)

### 標準工作流程

```bash
/gsave          # 1. 提交變更（自動分離公開/機敏檔案）
/gpush          # 2. 推送所有 commits 到私人庫
/publicpr       # 3. 建立 PR 到公開庫（僅發布時）
                #    - commits > 10 自動建議 Squash Merge
                #    - 節省 95% 時間，避免 cherry-pick 衝突
                # ⚠️ 發布後不拉回（單向流程）
```

### 指令說明

| 指令 | 目標 | 用途 | 過濾規則 | 注意事項 |
|------|------|------|----------|----------|
| `/gpush` | `private/main` | 推送所有 commits | 不過濾，完整備份 | - |
| `/publicpr` | `origin` (via PR) | 正式發布 | 自動過濾機敏檔案 | commits > 10 建議 Squash |

### 錯誤與正確範例

**錯誤範例**（嚴格禁止）：
- ❌ `git commit -m "..."` - 手動提交，必須使用 `/gsave`
- ❌ `git push origin main` - 可能洩露機敏資料
- ❌ `git push` - 預設 remote 可能錯誤
- ❌ 直接推送到 origin - 必須使用 `/publicpr`
- ❌ `git pull origin main` - 會破壞 private history（單向流程）

**正確範例**：
- ✅ `/gsave` - 建立 commit（唯一合法方式）
- ✅ `/gpush` - 推送所有 commits 到私人庫
- ✅ `/publicpr` - 建立 PR 發布（自動選擇 Squash/Cherry-pick）
- ✅ `git cherry-pick <commit>` - 緊急情況從 origin 挑選修復

**詳細說明**：`docs/12-git-workflow/dual-repo-workflow.md` ⭐

---

## 🚨 快速除錯指南

### 除錯檢查清單
1. ✅ **檢查規格**：`docs/05-validation/README.md`（索引入口）
   - FR-xxx（功能需求）
   - SC-xxx（成功標準）
2. ✅ **確認 WebDriver**：讀取 `settings.json` 確認 `webdriver_type`
3. ✅ **查閱 API**：`docs/06-api-reference/nodriver_api_guide.md`（優先）
4. ✅ **搜尋案例**：`docs/08-troubleshooting/README.md`
5. ✅ **查閱 Issues FAQ**：`docs/10-project-tracking/issues-faq-tracking.md` ⭐ 新增
   - 按平台分類的常見問題
   - 已解決 Issues 的解決方案彙整
6. ✅ **啟用詳細日誌**：請使用者在「進階設定」啟用「輸出除錯訊息」
7. ✅ **MCP 即時除錯**：`docs/07-testing-debugging/mcp_integration_guide.md` ⭐
   - 使用 `--mcp_debug` 參數啟動 NoDriver
   - 透過 MCP 工具即時觀察頁面狀態

### Spec 檢查項目（除錯時必讀）

**檢查路徑**：`docs/05-validation/README.md` → `specs/001-ticket-automation-system/`

#### 1. 功能需求（FR-xxx）
- 確保修復符合原始功能需求
- 例：FR-017（日期關鍵字匹配）、FR-058（錯誤分類）
- 搜尋「功能需求」區塊

#### 2. 成功標準（SC-xxx）
- 驗證修復達到可測量的目標
- 例：SC-002（90% 關鍵字成功率）、SC-005（95% 元素互動成功率）
- 搜尋「成功標準」區塊

#### 3. 核心設計原則
- 配置驅動架構（settings.json 控制所有行為）
- 三層回退策略（關鍵字 → 模式 → 手動）
- 函數分解原則（單一職責、可組合性）

#### 4. 平台特定考量
- **TixCraft**: Cookie 登入、即將開賣頁面
- **iBon**: Shadow DOM、Angular SPA
- **KKTIX**: 排隊處理、價格清單
- **TicketPlus**: 展開面板、實名對話框

#### 5. 假設與約束
- 瀏覽器版本（Chrome 90+）
- 記憶體限制（<500MB）

**實務範例**：
- **問題**：ibon 日期選擇關鍵字無法匹配
- **Spec 檢查**：
  - FR-017: 支援多關鍵字、逗號分隔？
  - FR-018: 是否實作回退到 auto_select_mode？
  - SC-002: 90% 成功率是否達成？
- **修正方向**：確保關鍵字匹配邏輯、回退邏輯、auto_select_mode 支援

---

## 🧪 快速測試

### 測試前置要求
**重要**：測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即進入暫停狀態。

### NoDriver 快速測試指令

**Git Bash**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -rf src/__pycache__ && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**Windows CMD**：
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && rmdir /S /Q src\__pycache__ 2>nul && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

> **注意**：清除 `__pycache__` 確保 Python 載入最新修改的程式碼，避免使用舊的快取。

### 檢查測試輸出

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

### 驗證重點
- ✅ 日期匹配數量是否符合預期（`Total dates matched`）
- ✅ 區域匹配數量是否符合預期（`Total areas matched`）
- ✅ 選擇策略是否正確執行（`auto_select_mode`）
- ✅ AND 邏輯/回退機制是否觸發（`AND logic failed` → 回退到下一組）

**詳細指南**：
- 邏輯流程圖：`docs/02-development/logic_flowcharts.md`
- 測試執行指南：`docs/07-testing-debugging/testing_execution_guide.md` ⭐

---

## 📐 程式碼規範

**遵循憲法『程式碼品質標準』**：`.specify/memory/constitution.md`

### Emoji 使用規範（NON-NEGOTIABLE）
- **✅ 允許**：Emoji 僅限 `*.md` 文件中使用
- **❌ 禁止**：`*.py`、`*.js` 中禁止 emoji
- **❌ 禁止**：print()、console.log() 輸出中禁止 emoji
- **原因**：emoji 導致 Windows cp950 編碼錯誤（會導致程式崩潰）

**正確範例**：`print("[SUCCESS] 操作成功")`
**錯誤範例**：`print("✅ 操作成功")`

### 其他規範
詳細規範請查詢：`.specify/memory/constitution.md`
- 暫停機制
- 安全性原則
- Code Review 標準

---

## 🗣️ 使用者溝通規範（NON-NEGOTIABLE）

**核心原則**：回應使用者時，使用「使用者名稱（UI 顯示）」而非「技術名稱（JSON key）」。

### 快速對照（常用）

| 技術名稱 | 使用者名稱 | 使用範例 |
|----------|-----------|----------|
| `verbose: true` | 輸出除錯訊息 | 「請啟用『輸出除錯訊息』選項」 |
| `ocr_captcha.enable` | OCR（啟用） | 「請啟用『OCR 自動辨識驗證碼』」 |
| `ocr_captcha.force_submit` | 自動送出 | 「請啟用『自動送出』」 |
| `headless` | 無圖形界面模式 | 「請關閉『無圖形界面模式』」 |
| `date_auto_fallback` | 日期自動遞補 | 「請啟用『日期自動遞補』」 |
| `area_auto_fallback` | 區域自動遞補 | 「請啟用『區域自動遞補』」 |
| `settings.json` | 設定檔 | 「請檢查設定檔」 |
| `nodriver` | NoDriver 模式 | 「目前使用 NoDriver 模式」 |

### 回應範例

**錯誤**（技術導向）：
> 請將 `settings.json` 中的 `advanced.verbose` 設為 `true`

**正確**（使用者導向）：
> 請在設定介面的「進階設定」中，找到「輸出除錯訊息」選項並打勾啟用

### 完整對照表
詳細對照請查詢：`docs/11-reference/settings-terminology.md`

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
- `.specify/memory/` - speckit 系統文件與憲法
- 相關 slash commands: `/speckit.*`

---

## 📋 專案追蹤目錄（docs/10-project-tracking）

此目錄包含專案進度追蹤、問題記錄與變更日誌相關文件。

### 文件說明

| 文件 | 用途 | 更新時機 |
|------|------|----------|
| `todo.md` | 待辦事項清單、開發策略、平台進度 | 功能開發/問題修復時 |
| `accept_changelog.md` | Accept Edits On 模式下的自動化記錄 | 自動執行模式時 |
| `issues-faq-tracking.md` | 已解決 Issues 的解決方案彙整 | 關閉 Issue 後 |
| `changelog_guide.md` | CHANGELOG 編寫規範（使用者視角） | 參考文件 |

### Accept Edits On 模式記錄要求

**當使用者啟用 Accept Edits On 模式進行自動化工作時**：

1. **記錄位置**：`docs/10-project-tracking/accept_changelog.md`
2. **記錄規則**：只新增不刪除
3. **記錄格式**：
```markdown
## YYYY.MM.DD

### [類型]([範圍]): [摘要]

**分支**：[分支名稱]

**變更摘要**：
[簡述本次變更的目的與範圍]

**實作內容**：
1. [具體實作項目 1]
2. [具體實作項目 2]
...

**遵循規範**：
- 憲法第 X 條 (原則名稱)
...

**程式碼位置**：`src/xxx.py` (行 XXXX-XXXX)
```

4. **記錄時機**：
   - 完成一個功能模組後
   - 修復重大問題後
   - 進行架構變更後

### 待辦事項更新

**在以下情況更新 `todo.md`**：
- 發現新問題或需求時
- 完成某項功能後（標記 ✅）
- 使用者回報問題時（新增追蹤項目）
- 評估新平台支援時

---

## 💡 使用原則

- ❌ 不要在 CLAUDE.md 重複 docs 內容
- ✅ 指向對應 docs 文件
- ✅ CLAUDE.md 只保留索引、核心原則、快速指令

---
- 當我說出檢查紀錄 代表要求你檢查logs.txt
