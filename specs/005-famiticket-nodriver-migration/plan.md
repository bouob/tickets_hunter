# 實作計畫：FamiTicket NoDriver 遷移

**分支**：`005-famiticket-nodriver-migration` | **日期**：2025-11-04 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/005-famiticket-nodriver-migration/spec.md` 的功能規格說明

**注意**：本範本由 `/speckit.plan` 指令填寫。執行流程請參見 `.specify/templates/commands/plan.md`。

## 摘要

本計畫旨在將 FamiTicket (全家網) 票務自動化功能從 Chrome/Selenium 引擎遷移至 NoDriver 引擎，以符合專案憲法第 I 條（NoDriver First）原則。遷移範圍包括完整的票務自動化流程：帳號密碼登入、日期/區域選擇、驗證問題處理、自動補票功能。

**核心技術方案**：
- **API 遷移**：將所有函數從同步（Selenium）轉換為非同步（NoDriver async/await）
- **元素互動**：優先使用 CDP (Chrome DevTools Protocol) 取代 JavaScript 執行
- **元素搜尋**：採用 Pierce 方法（`cdp.dom.perform_search()`）支援 Shadow DOM 穿透
- **自動補票**：重用現有 TixCraft NoDriver 的 auto-reload 模式，當日期列表為空時自動重新載入頁面
- **設定相容**：完全重用現有 `settings.json` 結構，無需新增 FamiTicket 專屬欄位

**參考實作**：
- Chrome 版本：`src/chrome_tixcraft.py` (lines 3141-6400, FamiTicket 函數群)
- NoDriver 模式：`src/nodriver_tixcraft.py` (TixCraft/KKTIX 實作模式)

## 技術上下文 (Technical Context)

**語言/版本**：Python 3.10.11
**主要相依性 (dependency)**：
- nodriver (Chrome DevTools Protocol wrapper)
- asyncio (非同步 I/O 框架)
- json (設定檔解析)
- 現有工具函數：`util.py` (format_keyword_string、guess_tixcraft_question、fill_common_verify_form 等)

**儲存方式**：
- 設定檔：`src/settings.json` (JSON 格式)
- 暫存資料：記憶體狀態（fail_list、formated_area_list 等）
- 測試輸出：`.temp/test_output.txt`

**測試**：
- 背景測試：30 秒 timeout 執行（`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`）
- 輸出驗證：檢查 `.temp/test_output.txt` 中的日誌訊息（`grep` 關鍵字）
- 手動測試：真實 FamiTicket 頁面測試（登入、日期選擇、區域選擇流程）

**目標平台**：
- Windows 10/11（主要）
- Linux（次要）
- MacOS ARM（次要，需處理 ddddocr 相容性問題）

**專案類型**：single（單一專案，自動化腳本）

**效能目標**：
- 日期列表掃描：< 2 秒（符合 SC-002）
- 區域列表掃描：< 2 秒（符合 SC-003）
- 登入操作：< 5 秒
- 自動補票間隔：使用者可配置（`auto_reload_page_interval`，建議 5-30 秒）

**限制條件**：
- 記憶體：< 500MB（遵循專案假設）
- CPU：單核心使用，無多線程需求
- 網路：需要穩定網路連線，支援網路中斷錯誤處理
- 瀏覽器：Chrome 90+（NoDriver 要求）

**規模/範圍**：
- 8 個核心函數需遷移
- 約 500-800 行程式碼（基於 Chrome 版本規模估算）
- 6 個 URL 路由模式（登入頁、活動頁、首頁等）
- 5 個主要 CSS 選擇器（帳號、密碼、購買按鈕、日期列表、區域列表）

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

### ✅ I. NoDriver First（技術架構優先性）
- **通過**：本遷移將 FamiTicket 從 Chrome/Selenium 遷移至 NoDriver
- **證明**：FR-030 到 FR-035 明確要求使用 NoDriver API（async/await、CDP、Pierce 方法）
- **Chrome 版本狀態**：遷移完成後進入維護模式（僅嚴重錯誤修復）

### ✅ II. 資料結構優先（設計先於實作）
- **通過**：spec.md 已定義主要實體（登入憑證、日期列表、區域列表、驗證答案字典、fail_list、自動補票設定）
- **後續步驟**：Phase 1 將產生 `data-model.md` 詳細定義每個實體的欄位與關係
- **契約定義**：Phase 1 將產生 `contracts/function-signatures.md` 與 `contracts/config-schema.md`

### ✅ III. 三問法則（決策守門人）
- **是核心問題嗎？** 是。FamiTicket 是台灣主要票務平台，NoDriver 版本缺失影響使用者體驗
- **有更簡單方法嗎？** 否。無法避免遷移，Chrome 版本已進入維護模式
- **會破壞相容性嗎？** 否。重用現有 `settings.json` 結構，使用者僅需切換 `webdriver_type`

### ✅ IV. 單一職責與可組合性（函數設計原則）
- **通過**：每個函數有單一職責（FR-036 列出 6 個核心函數，各司其職）
- **函數命名**：遵循 `nodriver_fami_*` 命名規範（FR-039 要求）
- **可組合性**：`nodriver_famiticket_main()` 作為協調器，組合其他小函數（FR-037）

### ✅ V. 設定驅動開發（使用者友善設計）
- **通過**：所有行為由 `settings.json` 控制（FR-026 到 FR-029）
- **無新增欄位**：重用現有 `tixcraft.*` 與 `advanced.*` 設定
- **切換方式**：使用者僅需修改 `webdriver_type` 欄位即可切換引擎

### ✅ VI. 測試驅動穩定性（品質守門人）
- **通過**：SC-007 要求所有函數通過 30 秒背景測試
- **測試方法**：詳見「技術上下文 > 測試」區塊
- **實際測試**：遷移完成後必須在真實 FamiTicket 頁面測試（spec.md 假設第 1 條）

### ✅ VII. MVP 原則（最小可行產品優先）
- **通過**：spec.md 的 User Stories 按優先級排序（P1: 登入/日期/區域/驗證，P2: 自動補票）
- **獨立測試**：每個 P1 story 可獨立測試與演示
- **完整流程優先**：確保核心購票流程完整可用，再優化邊界情況

### ✅ VIII. 文件與代碼同步（知識傳承）
- **通過**：本計畫（plan.md）與 spec.md 保持同步
- **後續更新**：遷移完成後將更新 `docs/02-development/structure.md` 與 `docs/10-project-tracking/accept_changelog.md`（spec.md 原則 VIII 聲明）

### ✅ IX. Git 提交規範與工作流程（版本控制紀律）
- **通過**：將使用 `gsave` 指令提交，commit 訊息採用 Conventional Commits 格式
- **分支**：已建立功能分支 `005-famiticket-nodriver-migration`
- **範例 commit 訊息**："feat(nodriver): migrate FamiTicket from Chrome to NoDriver"

**✅ 憲章檢查結果：全部通過，可進入 Phase 0 研究階段**

## 專案結構

### 文件（本功能）

```
specs/005-famiticket-nodriver-migration/
├── spec.md              # 功能規格說明（已完成）
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── function-signatures.md
│   └── config-schema.md
├── checklists/
│   └── requirements.md  # 品質檢查清單（已完成）
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### 原始碼（repository 根目錄）

```
tickets_hunter/
├── src/
│   ├── nodriver_tixcraft.py   # NoDriver 主程式（修改目標）
│   │                          # - 新增 FamiTicket 函數群（nodriver_fami_*）
│   │                          # - 解除 line 16841-16842 註解
│   ├── chrome_tixcraft.py     # Chrome 版本（參考來源）
│   │                          # - FamiTicket 函數群（lines 3141-6400）
│   ├── util.py                # 共用工具函數（重用）
│   │                          # - format_keyword_string()
│   │                          # - guess_tixcraft_question()
│   │                          # - fill_common_verify_form()
│   ├── settings.json          # 設定檔（無需修改）
│   └── config_launcher.json   # 多設定檔（無需修改）
├── .temp/
│   └── test_output.txt        # 測試輸出（自動生成）
├── docs/
│   ├── 02-development/
│   │   ├── structure.md       # 函數索引（需更新）
│   │   └── tixcraft_family_nodriver_vs_chrome_comparison.md
│   ├── 06-api-reference/
│   │   ├── nodriver_api_guide.md   # NoDriver API 參考
│   │   └── cdp_protocol_reference.md # CDP 協議參考
│   └── 10-project-tracking/
│       └── accept_changelog.md  # 變更記錄（需更新）
└── specs/
    └── 005-famiticket-nodriver-migration/  # 本功能規格
```

**結構決策**：採用 **Option 1: Single project**（預設）

**理由**：
- Tickets Hunter 是單一 Python 自動化腳本專案
- 所有原始碼集中在 `src/` 目錄下
- NoDriver 與 Chrome 版本共存於同一個檔案（`src/nodriver_tixcraft.py` 與 `src/chrome_tixcraft.py`）
- 共用工具函數位於 `src/util.py`，避免重複程式碼

**修改範圍**：
- **主要修改**：`src/nodriver_tixcraft.py`（新增 8 個 FamiTicket 函數，約 500-800 行）
- **次要修改**：`docs/02-development/structure.md`（新增函數索引）
- **次要修改**：`docs/10-project-tracking/accept_changelog.md`（記錄變更）

## 複雜度追蹤

*僅在專案憲章檢查（Constitution Check）有違規且必須說明時填寫*

**✅ 無違規項目**

本計畫完全遵循專案憲章的所有 9 大原則，無需額外說明或例外處理。所有決策均符合憲章要求：
- NoDriver First：完全遵循
- 資料結構優先：spec.md 已定義實體，Phase 1 將產生詳細設計
- 三問法則：已通過核心問題、簡單性、相容性檢查
- 其他原則：全部符合（詳見上方「專案憲章檢查」區塊）

---

## Phase 0: 研究與決策 (Research)

本階段旨在解決技術上下文中的所有 NEEDS CLARIFICATION 項目，並研究最佳實踐。

**研究任務清單**：

由於技術上下文已明確定義（無 NEEDS CLARIFICATION 項目），本階段主要聚焦於：

1. **NoDriver API 最佳實踐研究**
   - 任務：研究 NoDriver 元素搜尋策略（Pierce vs DOMSnapshot）
   - 目的：選擇最適合 FamiTicket 的元素搜尋方法
   - 參考：`docs/06-api-reference/nodriver_api_guide.md`

2. **CDP 點擊策略研究**
   - 任務：研究 CDP `dispatch_mouse_event` vs JavaScript `element.click()` 的反偵測效果
   - 目的：確保 FamiTicket 不會被偵測為機器人
   - 參考：`docs/06-api-reference/cdp_protocol_reference.md`

3. **Chrome 版本邏輯分析**
   - 任務：深入分析 Chrome FamiTicket 函數的邏輯（lines 3141-6400）
   - 目的：了解關鍵字匹配、回退機制、錯誤處理的實作細節
   - 來源：`src/chrome_tixcraft.py`

4. **現有 NoDriver 模式分析**
   - 任務：研究 TixCraft/KKTIX NoDriver 實作模式
   - 目的：重用成功的設計模式與程式碼結構
   - 來源：`src/nodriver_tixcraft.py` (TixCraft/KKTIX 函數)

**輸出**：✅ `research.md`（已完成）

### 研究結果總結

**Phase 0 已完成**，詳細技術決策記錄於 [research.md](./research.md)

**關鍵決策**：

| 技術項目 | 選擇方案 | 信心等級 |
|---------|---------|---------|
| 元素搜尋 | Pierce 方法 (`cdp.dom.perform_search`) | ⭐⭐⭐ 高 |
| 元素點擊 | CDP `dispatch_mouse_event()` | ⭐⭐⭐ 高 |
| 表單輸入 | NoDriver `element.send_keys()` | ⭐⭐⭐ 高 |
| 頁面導航 | `await tab.get(url)` | ⭐⭐⭐ 高 |
| 自動補票 | 重用 TixCraft 模式 + FamiTicket 特定邏輯 | ⭐⭐ 中 |
| 錯誤處理 | try-except + 布林返回值 | ⭐⭐⭐ 高 |

**風險評估**：

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| FamiTicket 更改頁面結構 | 低 | 高 | 使用彈性選擇器，詳細記錄於 contracts/ |
| NoDriver 反偵測失敗 | 低 | 中 | 已採用 CDP 真實點擊，若仍失敗則回退至 JavaScript |
| 自動補票過於頻繁導致 IP 封鎖 | 中 | 高 | 建議使用者設定合理間隔（5-30 秒） |
| 非同步程式碼複雜度增加 | 低 | 低 | 參考現有 TixCraft/KKTIX 模式 |

---

## Phase 1: 設計與契約 (Design & Contracts)

本階段基於 Phase 0 的研究結果，產生詳細的資料模型、API 契約與快速開始指南。

### 產出清單

✅ **所有 Phase 1 產出已完成**

#### 1.1 資料模型設計

**檔案**：[data-model.md](./data-model.md)

**內容**：定義 6 個核心實體

| 實體名稱 | 用途 | 關鍵欄位 |
|---------|------|---------|
| FamiTicket 登入憑證 | 存放帳號密碼 | account, password |
| 日期列表 | 存放可選日期 | date_text, area_text, button_text, is_available, node_id |
| 區域列表 | 存放可選區域 | area_name, area_html, is_disabled, node_id |
| 驗證問題答案字典 | 存放驗證問題答案 | question, answer, confidence |
| 錯誤答案清單 (fail_list) | 追蹤錯誤答案 | wrong_answers (array) |
| 自動補票設定 | 控制自動補票行為 | enable, interval, last_url |

**設計原則**：
- 所有實體欄位均對應 settings.json 或 Chrome 版本邏輯
- 無新增資料結構，完全重用現有模式
- 欄位命名遵循 Python PEP 8 規範

#### 1.2 函數簽章契約

**檔案**：[contracts/function-signatures.md](./contracts/function-signatures.md)

**內容**：定義 8 個核心函數簽章

| 函數名稱 | 職責 | 回傳值 |
|---------|------|--------|
| `nodriver_famiticket_main()` | URL 路由協調器 | bool |
| `nodriver_fami_login()` | 帳號密碼登入 | bool |
| `nodriver_fami_activity()` | 點擊「立即購買」按鈕 | bool |
| `nodriver_fami_date_auto_select()` | 日期選擇 + 自動補票 | bool |
| `nodriver_fami_area_auto_select()` | 區域選擇（AND/OR 邏輯） | bool |
| `nodriver_fami_verify()` | 驗證問題處理 | tuple[bool, list] |
| `nodriver_fami_date_to_area()` | 日期 → 區域流程協調 | bool |
| `nodriver_fami_home_auto_select()` | 首頁入口處理 | bool |

**設計原則**：
- 所有函數遵循 async/await 模式（FR-030）
- 所有函數接受 `show_debug_message` 參數（FR-038）
- 所有函數返回布林值（除 verify 返回 tuple）（FR-038）
- 函數命名遵循 `nodriver_fami_*` 規範（FR-039）

#### 1.3 設定檔結構契約

**檔案**：[contracts/config-schema.md](./contracts/config-schema.md)

**內容**：記錄 FamiTicket 使用的現有設定欄位（無新增）

**核心欄位**：

| 欄位路徑 | 類型 | 必填 | 用途 |
|---------|------|------|------|
| `webdriver_type` | string | ✅ | 引擎選擇（必須為 "nodriver"） |
| `advanced.fami_account` | string | ✅ | FamiTicket 帳號 |
| `advanced.fami_password_plaintext` | string | ✅ | FamiTicket 密碼 |
| `date_auto_select.mode` | string | ❌ | 日期選擇策略 |
| `date_auto_select.date_keyword` | string | ❌ | 日期關鍵字（OR 邏輯） |
| `area_auto_select.mode` | string | ❌ | 區域選擇策略 |
| `area_auto_select.area_keyword` | string | ❌ | 區域關鍵字（OR 邏輯） |
| `area_auto_select.area_keyword_and` | array | ❌ | 區域關鍵字（AND 邏輯） |
| `tixcraft.auto_reload_coming_soon_page` | boolean | ❌ | 啟用自動補票 |
| `advanced.auto_reload_page_interval` | number | ❌ | 自動補票間隔（秒） |
| `advanced.auto_guess_options` | boolean | ❌ | 啟用驗證問題自動猜測 |
| `advanced.verbose` | boolean | ❌ | 啟用除錯訊息 |

**設計原則**：
- 完全重用現有欄位（FR-026）
- 無新增 FamiTicket 專屬欄位（FR-027）
- 使用者僅需修改 `webdriver_type` 即可切換引擎

#### 1.4 快速開始指南

**檔案**：[quickstart.md](./quickstart.md)

**內容**：5 分鐘快速測試流程

**核心步驟**：
1. 修改 `settings.json`（2 分鐘）
2. 執行 30 秒背景測試（30 秒）
3. 驗證測試結果（1 分鐘）
4. 真實頁面手動測試（選填）
5. 切換回 Chrome 版本（選填）

**測試指令**（Git Bash）：
```bash
cd /d/Desktop/bouob-TicketHunter\(MaxBot\)/tickets_hunter
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
echo "" > .temp/test_output.txt
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**驗證方法**：
```bash
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

---

## Phase 2: 實作規劃 (Implementation Plan)

本階段定義實作步驟與順序，確保遵循相依性與 MVP 原則。

### 實作策略

**遵循憲法第 VII 條（MVP 原則）**：優先完成核心流程，確保每個 P1 User Story 可獨立測試。

**實作順序**（按相依性排序）：

#### Step 1：基礎函數與工具（無相依性）

**目標**：建立可重用的基礎元件

**任務清單**：
1. **新增 `nodriver_click_element()` 工具函數**
   - 位置：`src/nodriver_tixcraft.py`（與其他 NoDriver 工具函數同區塊）
   - 功能：CDP 點擊（優先）+ element.click()（備用）
   - 參考：`research.md` 中的 CDP 點擊策略
   - 相依性：無

2. **新增 `nodriver_search_element()` 工具函數**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：Pierce 方法元素搜尋
   - 參考：TixCraft NoDriver 實作模式
   - 相依性：無

3. **驗證現有工具函數可用性**
   - 確認 `util.py` 中的 `format_keyword_string()`、`guess_tixcraft_question()`、`fill_common_verify_form()` 可正常呼叫
   - 相依性：無

#### Step 2：登入功能（P1 User Story 1）

**目標**：實作帳號密碼登入（FR-001 至 FR-009）

**任務清單**：
4. **實作 `nodriver_fami_login()`**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：偵測登入頁面（URL 包含 `/Home/User/SignIn`）、填寫帳號密碼、提交表單
   - CSS 選擇器：`#usr_act`（帳號）、`#usr_pwd`（密碼）
   - 參考：`src/chrome_tixcraft.py` line 6302（`fami_login()`）
   - 相依性：Step 1 的工具函數
   - 測試方法：真實 FamiTicket 登入頁面測試
   - 成功標準：SC-001（95% 登入成功率）

#### Step 3：活動頁面入口（P1 User Story 1）

**目標**：實作活動頁面「立即購買」按鈕點擊（FR-006 至 FR-009）

**任務清單**：
5. **實作 `nodriver_fami_activity()`**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：偵測活動頁面（URL 包含 `/Home/Activity/Info/`）、點擊「立即購買」按鈕
   - CSS 選擇器：`button.btn-buy`（參考 Chrome 版本）
   - 參考：`src/chrome_tixcraft.py` line 3336（`fami_activity()`）
   - 相依性：Step 1 的點擊工具函數
   - 測試方法：真實 FamiTicket 活動頁面測試

6. **實作 `nodriver_fami_home_auto_select()`**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：處理首頁入口（`/Home/Activity`）
   - 參考：Chrome 版本 `fami_home()` 邏輯
   - 相依性：Step 1 的工具函數
   - 測試方法：真實 FamiTicket 首頁測試

#### Step 4：日期選擇（P1 User Story 2）

**目標**：實作日期關鍵字匹配與自動選擇（FR-010 至 FR-015）

**任務清單**：
7. **實作 `nodriver_fami_date_auto_select()`（不含自動補票）**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：
     - 掃描日期列表（CSS: `table.session__list > tbody > tr`）
     - 提取日期文字、區域文字、購買按鈕
     - 關鍵字匹配（OR 邏輯，使用 `format_keyword_string()`）
     - 回退至 `auto_select_mode`（若無匹配）
   - 參考：`src/chrome_tixcraft.py` line 3380（`fami_date_auto_select()`）
   - 相依性：Step 1 的工具函數、`util.py` 的 `format_keyword_string()`
   - 測試方法：
     - 30 秒背景測試（驗證日期匹配數量）
     - 真實 FamiTicket 日期選擇頁面測試
   - 成功標準：SC-002（90% 日期列表掃描成功率，< 2 秒）

#### Step 5：區域選擇（P1 User Story 3）

**目標**：實作區域關鍵字匹配（AND/OR 邏輯）與自動選擇（FR-016 至 FR-021）

**任務清單**：
8. **實作 `nodriver_fami_area_auto_select()`**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：
     - 掃描區域列表（CSS: `div > a.area`）
     - 過濾已停用區域（class 包含 `"area disabled"`）
     - AND 邏輯匹配（`area_keyword_and`，所有關鍵字必須同時存在）
     - OR 邏輯匹配（`area_keyword`，任一關鍵字匹配）
     - 回退至 `auto_select_mode`（若無匹配）
   - 參考：`src/chrome_tixcraft.py` line 3514（`fami_area_auto_select()`）
   - 相依性：Step 1 的工具函數、`util.py` 的 `format_keyword_string()`
   - 測試方法：
     - 30 秒背景測試（驗證區域匹配數量、AND 邏輯正確性）
     - 真實 FamiTicket 區域選擇頁面測試
   - 成功標準：SC-003（90% 區域列表掃描成功率，< 2 秒）

#### Step 6：流程協調器（P1 完整流程）

**目標**：整合日期 → 區域流程（FR-034）

**任務清單**：
9. **實作 `nodriver_fami_date_to_area()`**
   - 位置：`src/nodriver_tixcraft.py`
   - 功能：協調日期選擇 → 區域選擇流程（呼叫 `nodriver_fami_date_auto_select()` 與 `nodriver_fami_area_auto_select()`）
   - 參考：TixCraft NoDriver 的協調器模式
   - 相依性：Step 4、Step 5 的函數
   - 測試方法：真實 FamiTicket 完整購票流程測試

#### Step 7：驗證問題處理（P1 User Story 4）

**目標**：實作驗證問題偵測與自動填寫（FR-022 至 FR-025）

**任務清單**：
10. **實作 `nodriver_fami_verify()`**
    - 位置：`src/nodriver_tixcraft.py`
    - 功能：
      - 偵測驗證輸入框（CSS: `#verifyPrefAnswer`）
      - 呼叫 `fill_common_verify_form()` 工具函數（重用 `util.py`）
      - 支援自動猜測（`auto_guess_options: true`）
      - 追蹤錯誤答案（`fail_list`）
    - 參考：`src/chrome_tixcraft.py` line 3298（`fami_verify()`）
    - 相依性：Step 1 的工具函數、`util.py` 的 `fill_common_verify_form()`、`guess_tixcraft_question()`
    - 測試方法：
      - 模擬驗證頁面測試（若有測試環境）
      - 真實 FamiTicket 驗證問題測試（遇到時）
    - 成功標準：SC-004（95% 驗證問題處理成功率）

#### Step 8：主函數路由器（整合所有功能）

**目標**：實作 URL 路由協調器（FR-037）

**任務清單**：
11. **實作 `nodriver_famiticket_main()`**
    - 位置：`src/nodriver_tixcraft.py`
    - 功能：
      - 根據 URL 模式分派至對應函數
      - `/Home/User/SignIn` → `nodriver_fami_login()`
      - `/Home/Activity/Info/` → `nodriver_fami_activity()`
      - `/Home/Activity` → `nodriver_fami_home_auto_select()`
      - 日期選擇頁面 → `nodriver_fami_date_to_area()`
      - 驗證頁面 → `nodriver_fami_verify()`
    - 參考：TixCraft NoDriver 的 `nodriver_tixcraft_main()` 模式
    - 相依性：Step 2 至 Step 7 的所有函數
    - 測試方法：
      - 30 秒背景測試（驗證 URL 路由正確性）
      - 真實 FamiTicket 完整流程測試

12. **解除 NoDriver 主循環中的 FamiTicket 註解**
    - 位置：`src/nodriver_tixcraft.py` line 16841-16842
    - 修改：
      ```python
      # 修改前：
      if 'famiticket.com' in url:
          #fami_dict = famiticket_main(driver, url, config_dict, fami_dict)
          pass

      # 修改後：
      if 'famiticket.com' in url:
          await nodriver_famiticket_main(tab, url, config_dict)
      ```
    - 相依性：Step 8 的 `nodriver_famiticket_main()` 已實作
    - 測試方法：30 秒背景測試（驗證程式成功進入 FamiTicket 流程）

#### Step 9：自動補票功能（P2 User Story 5）

**目標**：實作自動補票功能（FR-028、FR-029）

**任務清單**：
13. **在 `nodriver_fami_date_auto_select()` 中新增自動補票邏輯**
    - 位置：`src/nodriver_tixcraft.py`（修改 Step 4 的函數）
    - 功能：
      - 當日期列表為空（`formated_area_list` 為 None 或長度為 0）且 `auto_reload_coming_soon_page: true`
      - 等待 `auto_reload_page_interval` 秒
      - 使用 `await tab.get(last_activity_url)` 返回活動頁面（FamiTicket 特定邏輯）
    - 參考：
      - `src/chrome_tixcraft.py` line 3498-3510（Chrome 版本自動補票邏輯）
      - `src/nodriver_tixcraft.py` TixCraft NoDriver 自動補票模式（但改用 `tab.get()` 而非 `tab.reload()`）
    - 相依性：Step 4 的 `nodriver_fami_date_auto_select()` 已實作
    - 測試方法：
      - 模擬「即將開賣」頁面測試（日期列表為空）
      - 驗證自動重新載入行為
      - 檢查 `auto_reload_page_interval` 間隔是否正確
    - 成功標準：SC-008（重新載入間隔可配置）、SC-006（30 秒背景測試通過，無死循環）

#### Step 10：除錯與優化

**目標**：優化除錯訊息與錯誤處理

**任務清單**：
14. **新增除錯訊息（show_debug_message）**
    - 位置：所有 FamiTicket 函數
    - 功能：
      - 日期匹配訊息（`[DATE KEYWORD] Matched keyword: "xxx"`）
      - 區域匹配訊息（`[AREA KEYWORD] AND logic: ["xxx", "yyy"]`）
      - 選擇結果訊息（`[DATE SELECT] Selected date: "xxx"`）
      - 錯誤訊息（`[ERROR] Element not found: #usr_act`）
    - 參考：TixCraft NoDriver 的除錯訊息格式
    - 相依性：所有 Step 1-9 的函數
    - 測試方法：啟用 `verbose: true`，檢查 `.temp/test_output.txt` 中的訊息

15. **錯誤處理與回退機制**
    - 位置：所有 FamiTicket 函數
    - 功能：
      - try-except 包裹所有 CDP 操作
      - 返回布林值（簡化狀態管理）
      - 備用方案（如 CDP 點擊失敗 → element.click()）
    - 參考：`research.md` 中的非同步錯誤處理模式
    - 相依性：所有 Step 1-9 的函數
    - 測試方法：
      - 模擬元素搜尋失敗
      - 模擬網路中斷
      - 驗證程式是否正常返回 False（而非崩潰）

### 實作檢查點

**每個 Step 完成後必須檢查**：

- [ ] 程式碼通過 30 秒背景測試（SC-006、SC-007）
- [ ] 函數簽章符合 `contracts/function-signatures.md`
- [ ] 設定檔欄位符合 `contracts/config-schema.md`
- [ ] 資料結構符合 `data-model.md`
- [ ] 除錯訊息格式一致（`[DATE KEYWORD]`、`[AREA SELECT]` 等）
- [ ] 錯誤處理完整（try-except + 布林返回值）
- [ ] 憲法原則遵循（NoDriver First、單一職責、設定驅動）

---

## Phase 3: 測試與驗證 (Testing & Validation)

本階段定義測試方法與驗證標準，確保遷移品質。

### 測試策略

**遵循憲法第 VI 條（測試驅動穩定性）**：核心修改必須實測。

#### 測試層級

**Level 1：單元測試（背景測試）**

**目的**：驗證程式邏輯正確性，無崩潰、無死循環

**方法**：
1. 刪除暫停檔案（`MAXBOT_INT28_IDLE.txt`）
2. 執行 30 秒 timeout 測試：
   ```bash
   timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
   ```
3. 驗證輸出：
   ```bash
   grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt
   grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
   grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
   ```

**通過標準**：
- ✅ 程式執行 30 秒後自動終止（無死循環）
- ✅ 無崩潰錯誤（無 Python traceback）
- ✅ 日期匹配邏輯正確執行（`Total dates matched` 數量符合預期）
- ✅ 區域匹配邏輯正確執行（`Total areas matched` 數量符合預期）
- ✅ AND 邏輯正確觸發（若設定 `area_keyword_and`）
- ✅ 回退機制正確觸發（若無匹配 → 使用 `auto_select_mode`）

**測試頻率**：每個 Step 完成後必須執行

---

**Level 2：整合測試（真實頁面測試）**

**目的**：驗證實際票務流程，確保反偵測能力

**前提條件**：
- FamiTicket 帳號與密碼已準備好
- 選擇一個即將開賣或已開賣的活動
- `settings.json` 中的 `homepage` 設定為活動 URL

**測試情境**：

##### 情境 1：登入流程測試

**步驟**：
1. 清空 cookies（確保未登入狀態）
2. 執行程式：`python -u src/nodriver_tixcraft.py --input src/settings.json`
3. 觀察自動登入流程

**驗證項目**：
- [ ] 程式成功偵測登入頁面（URL 包含 `/Home/User/SignIn`）
- [ ] 自動填寫帳號（輸入框 `#usr_act` 正確填寫）
- [ ] 自動填寫密碼（輸入框 `#usr_pwd` 正確填寫）
- [ ] 自動提交表單（密碼輸入框設定 submit=True）
- [ ] 登入成功（導向至 FamiTicket 首頁或活動頁面）

**通過標準**：SC-001（95% 登入成功率）

---

##### 情境 2：日期選擇測試（關鍵字匹配）

**步驟**：
1. 修改 `settings.json`：
   ```json
   {
     "date_auto_select": {
       "date_keyword": "2025-11-10,週六"
     }
   }
   ```
2. 執行程式，觀察日期選擇流程
3. 檢查 `.temp/test_output.txt`：
   ```bash
   grep "\[DATE KEYWORD\]" .temp/test_output.txt
   ```

**驗證項目**：
- [ ] 程式成功掃描日期列表（CSS: `table.session__list > tbody > tr`）
- [ ] 關鍵字匹配正確（包含「2025-11-10」或「週六」的日期被選中）
- [ ] 若無匹配 → 回退至 `auto_select_mode`（選擇第一個可用日期）
- [ ] 自動點擊「立即購買」按鈕
- [ ] 頁面導航至區域選擇頁面

**通過標準**：SC-002（90% 日期列表掃描成功率，< 2 秒）

---

##### 情境 3：區域選擇測試（AND 邏輯）

**步驟**：
1. 修改 `settings.json`：
   ```json
   {
     "area_auto_select": {
       "area_keyword_and": [
         ["搖滾區", "不含柱"],
         ["VIP", "前排"]
       ]
     }
   }
   ```
2. 執行程式，觀察區域選擇流程
3. 檢查 `.temp/test_output.txt`：
   ```bash
   grep "\[AREA KEYWORD\]" .temp/test_output.txt
   ```

**驗證項目**：
- [ ] 程式成功掃描區域列表（CSS: `div > a.area`）
- [ ] 過濾已停用區域（class 包含 `"area disabled"` 的區域被跳過）
- [ ] AND 邏輯正確執行（選擇同時包含「搖滾區」**且**「不含柱」的區域）
- [ ] 若第一組關鍵字無匹配 → 嘗試下一組（「VIP」**且**「前排」）
- [ ] 若所有組都無匹配 → 回退至 `area_keyword`（OR 邏輯）
- [ ] 自動點擊區域連結
- [ ] 頁面導航至購票頁面或驗證頁面

**通過標準**：SC-003（90% 區域列表掃描成功率，< 2 秒）

---

##### 情境 4：驗證問題測試

**步驟**：
1. 執行程式，等待遇到驗證問題頁面
2. 觀察驗證問題處理流程
3. 檢查 `.temp/test_output.txt`：
   ```bash
   grep "verify\|question" .temp/test_output.txt
   ```

**驗證項目**：
- [ ] 程式成功偵測驗證輸入框（CSS: `#verifyPrefAnswer`）
- [ ] 呼叫 `fill_common_verify_form()` 工具函數
- [ ] 若 `auto_guess_options: true` → 自動猜測答案
- [ ] 追蹤錯誤答案（`fail_list` 正確更新）
- [ ] 自動提交驗證答案

**通過標準**：SC-004（95% 驗證問題處理成功率）

---

##### 情境 5：自動補票測試

**步驟**：
1. 修改 `settings.json`：
   ```json
   {
     "tixcraft": {
       "auto_reload_coming_soon_page": true
     },
     "advanced": {
       "auto_reload_page_interval": 5.0
     }
   }
   ```
2. 選擇一個「即將開賣」的活動（日期列表為空）
3. 執行程式，觀察自動補票流程
4. 檢查 `.temp/test_output.txt`：
   ```bash
   grep "reload\|coming soon" .temp/test_output.txt
   ```

**驗證項目**：
- [ ] 程式偵測日期列表為空（`formated_area_list` 為 None 或長度為 0）
- [ ] 觸發自動補票邏輯（`auto_reload_coming_soon_page: true`）
- [ ] 等待 `auto_reload_page_interval` 秒（5.0 秒）
- [ ] 使用 `await tab.get(last_activity_url)` 返回活動頁面
- [ ] 重複掃描日期列表（直到有可用日期或 30 秒 timeout）
- [ ] 無死循環（程式在 30 秒後自動終止）

**通過標準**：
- SC-006（30 秒背景測試通過，無崩潰、無死循環）
- SC-008（重新載入間隔可配置，實測間隔符合設定值）

---

**Level 3：壓力測試（選填）**

**目的**：驗證長時間運行穩定性

**方法**：
1. 執行程式 1 小時（模擬搶票等待期）
2. 監控記憶體使用量（必須 < 500MB）
3. 監控 CPU 使用率（避免過高）
4. 檢查程式是否正常運行（無崩潰）

**通過標準**：
- ✅ 記憶體使用量 < 500MB（遵循專案假設）
- ✅ 無記憶體洩漏（記憶體使用量穩定）
- ✅ 無崩潰或異常終止

---

### 驗收檢查清單

**遷移完成後必須檢查**（遵循憲法所有 9 大原則）：

#### 功能完整性

- [ ] 所有 5 個 User Stories（P1 + P2）已實作
- [ ] 所有 39 個功能需求（FR-001 至 FR-039）已滿足
- [ ] 所有 10 個成功標準（SC-001 至 SC-010）已達成

#### 程式碼品質

- [ ] 所有函數遵循 async/await 模式（FR-030）
- [ ] 所有函數命名遵循 `nodriver_fami_*` 規範（FR-039）
- [ ] 所有函數返回布林值（FR-038）
- [ ] 所有函數接受 `show_debug_message` 參數（FR-038）
- [ ] 錯誤處理完整（try-except + 布林返回值）
- [ ] 除錯訊息格式一致（`[DATE KEYWORD]`、`[AREA SELECT]` 等）

#### 憲法遵循

- [ ] ✅ I. NoDriver First：FamiTicket 已遷移至 NoDriver
- [ ] ✅ II. 資料結構優先：所有實體定義於 `data-model.md`
- [ ] ✅ III. 三問法則：已通過核心問題、簡單性、相容性檢查
- [ ] ✅ IV. 單一職責與可組合性：每個函數職責單一，可組合
- [ ] ✅ V. 設定驅動開發：所有行為由 `settings.json` 控制
- [ ] ✅ VI. 測試驅動穩定性：所有函數通過 30 秒背景測試與真實頁面測試
- [ ] ✅ VII. MVP 原則：P1 User Stories 優先完成，可獨立測試
- [ ] ✅ VIII. 文件與代碼同步：已更新 `structure.md` 與 `accept_changelog.md`
- [ ] ✅ IX. Git 提交規範：使用 `/gsave` 指令，commit 訊息採用 Conventional Commits 格式

#### 文件完整性

- [ ] `docs/02-development/structure.md` 已新增 FamiTicket NoDriver 函數索引
- [ ] `docs/10-project-tracking/accept_changelog.md` 已記錄變更
- [ ] `specs/005-famiticket-nodriver-migration/` 目錄下所有文件已完成
- [ ] README 或使用者指南已更新（若需要）

#### 效能與穩定性

- [ ] 日期列表掃描 < 2 秒（SC-002）
- [ ] 區域列表掃描 < 2 秒（SC-003）
- [ ] 登入操作 < 5 秒
- [ ] 記憶體使用量 < 500MB
- [ ] 30 秒背景測試通過（SC-006、SC-007）
- [ ] 真實頁面測試通過（所有情境）

---

## 下一步行動

**Phase 1 已完成**，接下來執行：

1. **執行 `/speckit.tasks`**：產生依相依性排序的 `tasks.md`（基於本 plan.md 的 Phase 2 實作規劃）
2. **執行 `/speckit.implement`**：依序執行 `tasks.md` 中的所有任務（Step 1 至 Step 15）
3. **執行 `/speckit.analyze`**：檢查 spec.md ↔ plan.md ↔ tasks.md 的一致性
4. **更新專案文件**：`structure.md` 與 `accept_changelog.md`
5. **提交變更**：使用 `/gsave` 指令（不要主動 commit，等待使用者確認）

---

## 附錄：參考文件索引

### 專案憲法與規範

- [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - 專案憲法（9 大原則）
- [docs/02-development/development_guide.md](../../docs/02-development/development_guide.md) - 開發規範
- [docs/02-development/ticket_automation_standard.md](../../docs/02-development/ticket_automation_standard.md) - 12 階段標準

### API 參考

- [docs/06-api-reference/nodriver_api_guide.md](../../docs/06-api-reference/nodriver_api_guide.md) - NoDriver API 完整參考
- [docs/06-api-reference/cdp_protocol_reference.md](../../docs/06-api-reference/cdp_protocol_reference.md) - CDP 協議參考
- [docs/06-api-reference/chrome_api_guide.md](../../docs/06-api-reference/chrome_api_guide.md) - Chrome/UC 參考

### 測試與除錯

- [docs/07-testing-debugging/testing_execution_guide.md](../../docs/07-testing-debugging/testing_execution_guide.md) - 測試執行指南
- [docs/07-testing-debugging/debugging_methodology.md](../../docs/07-testing-debugging/debugging_methodology.md) - 除錯方法論
- [docs/08-troubleshooting/README.md](../../docs/08-troubleshooting/README.md) - 疑難排解索引

### 本功能規格

- [spec.md](./spec.md) - 功能規格說明
- [research.md](./research.md) - 技術研究與決策
- [data-model.md](./data-model.md) - 資料模型設計
- [quickstart.md](./quickstart.md) - 快速開始指南
- [contracts/function-signatures.md](./contracts/function-signatures.md) - 函數簽章契約
- [contracts/config-schema.md](./contracts/config-schema.md) - 設定檔結構契約
- [checklists/requirements.md](./checklists/requirements.md) - 品質檢查清單

---

**文件維護**：
- 創建日期：2025-11-04
- 最後更新：2025-11-04
- 維護者：speckit workflow (`/speckit.plan` command)
- 狀態：✅ Phase 0 & Phase 1 complete, ready for Phase 2 (`/speckit.tasks`)

