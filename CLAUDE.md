# CLAUDE.md

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

根據任務類型選擇工作流程（**遵循憲法第 VII 條 MVP 原則**）：

### 🆕 新功能開發（完整 speckit 流程）
1. `/speckit.specify [描述]` - 建立功能規格（遵循憲法 II、III 條）
2. `/speckit.plan` - 生成實作計畫（遵循憲法 I、IV 條）
3. `/speckit.tasks` - 生成任務清單（遵循憲法 VII 條 MVP）
4. `/speckit.implement` - 執行實作（遵循所有憲法原則）
5. `/speckit.analyze` - 一致性檢查（遵循憲法 VIII 條）

### 📝 現有功能修改
- **小型修改**：傳統流程（Accept Edits On）
- **大型重構**：考慮啟用 speckit 流程
- **必須遵循**：憲法第 III 條（三問法則）決策

### 🐛 Bug 修復
- **流程**：規格檢查 → 快速除錯 → 修復 → 測試
- **必須遵循**：
  - 憲法第 VI 條（測試驅動穩定性）
  - **檢查相關 spec 需求**（確保修復符合原始設計）

### ❓ 規格澄清
- `/speckit.clarify` - 識別規格不足並提問（最多 5 個關鍵問題）

---

## speckit 指令參考

### 規格開發階段
- **`/speckit.specify [描述]`** - 從自然語言建立功能規格（spec.md）
- **`/speckit.clarify`** - 識別規格不足（最多 5 個問題）
- **`/speckit.constitution`** - 建立/更新專案憲章

### 實作規劃階段
- **`/speckit.plan`** - 生成設計文件
  - `research.md`（決策與理由）
  - `data-model.md`（資料結構）
  - `contracts/`（API 契約）
  - `quickstart.md`（快速開始）
- **`/speckit.tasks`** - 從 plan.md 生成可執行任務清單（tasks.md）

### 執行與驗證階段
- **`/speckit.implement`** - 執行 tasks.md 中的所有任務（自動背景測試）
- **`/speckit.analyze`** - 跨文件一致性檢查
  - spec.md ↔ plan.md ↔ tasks.md 同步檢查
  - 憲法原則遵循檢查
- **`/speckit.checklist`** - 為當前功能生成自訂檢查清單

### 規格資料夾結構
```
specs/[功能分支]/
├── spec.md                  ← 功能規格（需求）
├── research.md              ← 技術研究與決策
├── data-model.md            ← 資料結構設計
├── plan.md                  ← 實作規劃
├── tasks.md                 ← 任務清單（可執行）
├── quickstart.md            ← 快速開始指南
├── contracts/               ← API 契約
│   ├── platform-interface.md
│   ├── util-interface.md
│   └── config-schema.md
└── checklists/
    └── requirements.md      ← 品質檢查清單
```

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
4. `docs/06-api-reference/cdp_protocol_reference.md` - CDP 協議完整參考（NoDriver 深入）⭐
5. `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API（優先）
6. `docs/02-development/coding_templates.md` - 程式寫法範本

### 🔍 除錯問題
**按順序查閱**：
1. `docs/02-development/structure.md` - 查找函數定義
2. `docs/06-api-reference/cdp_protocol_reference.md` - CDP 協議參考（推薦深入閱讀）⭐
3. `docs/06-api-reference/nodriver_api_guide.md` - NoDriver API（推薦）
4. `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法論
5. `docs/08-troubleshooting/README.md` - 修復記錄索引

### 🧪 執行測試
1. `docs/07-testing-debugging/testing_execution_guide.md` - 標準測試流程
2. `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法

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
