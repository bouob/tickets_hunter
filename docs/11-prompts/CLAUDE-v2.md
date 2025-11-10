# CLAUDE.md v2.0（優化版本）

**專案**：Tickets Hunter - 多平台搶票自動化系統
**版本**：v2.0
**最後更新**：2025-11-09

---

## 🚀 Quick Reference（速查表）

### 最常見任務快速路徑

#### 🐛 Bug 修復（3 步驟）
1. **檢查規格**：`specs/001-ticket-automation-system/spec.md`（查找 FR-xxx, SC-xxx）
2. **定位函數**：`docs/02-development/structure.md`
3. **執行測試**：`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`

#### ✨ 新增功能（3 步驟）
1. **查閱標準**：`docs/02-development/ticket_automation_standard.md`（12 階段）
2. **參考機制**：`docs/03-mechanisms/`（日期/區域/驗證碼）
3. **編寫代碼**：`docs/02-development/coding_templates.md`

#### 📝 文件更新（3 步驟）
1. **同步代碼**：憲法第 VIII 條（文件與代碼同步）
2. **記錄變更**：`docs/10-project-tracking/accept_changelog.md`
3. **一致性檢查**：`/speckit.analyze`（speckit 專案）

### 關鍵指令速查

| 任務 | 指令 | 說明 |
|------|------|------|
| 提交變更 | `/gsave` | 自動分離公開/機敏檔案 |
| 推送代碼 | `/gpush` | 推送公開代碼到私人庫 |
| 推送機敏 | `/privatepush` | 推送文檔/設定到私人庫 |
| 發布 | `/publicpr` | 建立 PR 到公開庫（僅發布時） |
| 快速測試 | `timeout 30 python -u src/...` | 30 秒快速測試 |
| 規格分析 | `/speckit.analyze` | 跨產物一致性檢查 |
| 除錯診斷 | `/debug` | 專業除錯工具（Spec + 憲法） |

### 緊急除錯 5 步驟

1. **讀取錯誤**：`.temp/test_output.txt`
2. **檢查規格**：`specs/001-ticket-automation-system/spec.md`（FR-xxx, SC-xxx）
3. **查找 API**：`docs/06-api-reference/nodriver_api_guide.md`
4. **搜尋案例**：`docs/08-troubleshooting/README.md`
5. **啟用日誌**：`config_dict["advanced"]["verbose"] = True`

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

## 📜 憲法與核心原則

**最高指導原則**：`.specify/memory/constitution.md`

所有開發工作**必須**：
1. 查詢憲法中的相關原則
2. 嚴格遵循憲法規範
3. 違反憲法的行為必須拒絕

### 9 大核心原則（速記）

| 原則 | 關鍵字 | 核心要點 |
|------|--------|----------|
| **I. NoDriver First** | 技術優先級 | NoDriver > UC > Selenium |
| **II. 資料結構優先** | 設計先行 | 結構決定一切 |
| **III. 三問法則** | 決策守門 | 核心？簡單？相容？ |
| **IV. 單一職責** | 函數設計 | 小函數組合 |
| **V. 設定驅動** | 使用者友善 | settings.json 控制所有行為 |
| **VI. 測試驅動** | 品質守門 | 核心修改必須實測 |
| **VII. MVP 原則** | 優先級 | 最小可行產品優先 |
| **VIII. 文件同步** | 知識傳承 | 文件是代碼一部分 |
| **IX. Git 規範** | 版本控制 | 英文主題行、gsave 指令 |

**使用方式**：
- 開發前：查詢相關原則（例：重構 → 查第 III 條三問法則）
- 代碼審查：對照憲法標準
- 違反憲法：必須拒絕

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

#### 🎫 平台特定問題（Platform-Specific）
- **ibon Cookie** → `docs/08-troubleshooting/ibon_cookie_troubleshooting.md`
- **ibon NoDriver 座位** → `docs/08-troubleshooting/ibon_nodriver_fixes_2025-10-03.md`
- **MacOS ARM 環境** → `docs/08-troubleshooting/ddddocr_macos_arm_installation.md`
- **編碼錯誤 (cp950)** → 檢查程式碼中是否使用 emoji（禁止）

#### 🧪 測試與除錯（Testing & Debugging）
- **測試執行** → `docs/07-testing-debugging/testing_execution_guide.md` ⭐
- **除錯方法** → `docs/07-testing-debugging/debugging_methodology.md` ⭐
- **邏輯流程圖** → `docs/02-development/logic_flowcharts.md`

#### 📦 部署與發布（Deployment）
- **打包指南** → `docs/09-deployment/pyinstaller_packaging_guide.md`
- **CHANGELOG 指南** → `docs/10-project-tracking/changelog_guide.md` ⭐
- **Git 工作流程** → `docs/12-git-workflow/dual-repo-workflow.md` ⭐

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
- `docs/10-project-tracking/changelog_guide.md` - CHANGELOG 指南 ⭐
- `docs/02-development/coding_templates.md` - 程式範本
- `docs/02-development/documentation_workflow.md` - 文件維護流程

</details>

---

## 🔗 Git 工作流程

### ⚠️ Git 推送安全規則（NON-NEGOTIABLE）

**核心原則**：
- ✅ **只推送到私人庫**（`private`）
- ❌ **嚴禁直接推送到公開庫**（`origin`）

**Repo 位址**：
- 私人庫：`https://github.com/bouob/private-tickets-hunter.git` (remote: `private`)
- 公開庫：`https://github.com/bouob/tickets_hunter.git` (remote: `origin`)

### 標準工作流程

```bash
/gsave          # 1. 提交變更（自動分離公開/機敏檔案）
/gpush          # 2. 推送公開代碼到私人庫
/privatepush    # 3. 推送機敏檔案到私人庫
/publicpr       # 4. 建立 PR 到公開庫（僅發布時）
```

### 指令說明

| 指令 | 目標 | 用途 | 過濾規則 |
|------|------|------|----------|
| `/gpush` | `private/main` | 推送公開代碼 | 自動過濾 PRIVATE commits |
| `/privatepush` | `private/main` | 推送機敏檔案 | 只推送 🔒 PRIVATE 標記 |
| `/publicpr` | `origin` (via PR) | 正式發布 | 自動過濾機敏檔案 |

### 錯誤與正確範例

**錯誤範例**（嚴格禁止）：
- ❌ `git push origin main` - 可能洩露機敏資料
- ❌ `git push` - 預設 remote 可能錯誤
- ❌ 直接推送到 origin - 必須使用 `/publicpr`

**正確範例**：
- ✅ `/gpush` - 推送一般 commits
- ✅ `/privatepush` - 推送機敏 commits
- ✅ `/publicpr` - 建立 PR 發布

**詳細說明**：`docs/12-git-workflow/dual-repo-workflow.md` ⭐

---

## 🔧 Accept Edits On 工作流程

### 核心流程
1. **完成功能修改** → 符合所有憲法規範（遵循 constitution.md）
2. **自動執行背景測試** → 30 秒 timeout，輸出至 `.temp/test_output.txt`
3. **分析測試結果** → 失敗時觸發文件檢查模式
4. **[強制] 記錄完成項目** → `docs/10-project-tracking/accept_changelog.md`
5. **[speckit 專案] 一致性檢查** → 執行 `/speckit.analyze`（如適用）
6. **驗證記錄完成** → 檢查點
7. **標記 todo 完成**
8. **查找下一個 todo** → `docs/10-project-tracking/todo.md`

### 文件檢查模式（測試失敗時）
0. **檢查 Spec**：`specs/001-ticket-automation-system/spec.md` + `plan.md`
   - 功能需求（FR-xxx）：確保修復符合原始設計
   - 成功標準（SC-xxx）：驗證修復達到可測量目標
1. 讀取 API 指南（根據 `webdriver_type`）
2. 查詢憲法相關原則（`.specify/memory/constitution.md`）
3. 搜尋專案文件（structure.md、debugging_methodology.md、troubleshooting/）
4. 搜尋網路資料（可選）
5. 綜合分析與修正

---

## 🚨 快速除錯指南

### 除錯檢查清單
1. ✅ **檢查規格**：`specs/001-ticket-automation-system/spec.md`
   - FR-xxx（功能需求）
   - SC-xxx（成功標準）
2. ✅ **確認 WebDriver**：讀取 `settings.json` 確認 `webdriver_type`
3. ✅ **查閱 API**：`docs/06-api-reference/nodriver_api_guide.md`（優先）
4. ✅ **搜尋案例**：`docs/08-troubleshooting/README.md`
5. ✅ **啟用詳細日誌**：`config_dict["advanced"]["verbose"] = True`

### Spec 檢查項目（除錯時必讀）

**檢查路徑**：`specs/001-ticket-automation-system/`

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
- **KHAM**: 自動座位切換

#### 5. 假設與約束
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

## 🧪 快速測試

### 測試前置要求
**重要**：測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即進入暫停狀態。

### NoDriver 快速測試指令

**Git Bash**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**Windows CMD**：
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

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

## 💡 使用原則

- ❌ 不要在 CLAUDE.md 重複 docs 內容
- ✅ 指向對應 docs 文件
- ✅ CLAUDE.md 只保留索引、核心原則、快速指令

---

## 📋 v2.0 版本更新日誌

### 主要改進
1. ✅ 新增「Quick Reference」速查表（最常用資訊前置）
2. ✅ 增強「任務類型自動判斷」（關鍵詞 → 工作流程）
3. ✅ 精簡 Git 工作流程（詳細內容指向 docs/）
4. ✅ 合併「文件導航」與「常見問題索引」（減少重複）
5. ✅ 優化憲法遵循聲明（表格化、更清晰）
6. ✅ 使用摺疊區塊減少滾動（完整文件樹摺疊）
7. ✅ 增加平台識別表（FamiTicket、Cityline）

### 量化效果
- **文檔長度**：從 399 行減少到 ~350 行（-12%）
- **決策效率**：增加任務類型自動判斷表
- **快速查找**：新增速查表，預期從 30 秒降低到 5 秒

### 向後兼容
- ✅ 保留所有原有區塊
- ✅ 只調整順序和格式
- ✅ 所有文檔路徑不變
