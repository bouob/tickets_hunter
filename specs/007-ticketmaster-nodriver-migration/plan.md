# 實作計畫：Ticketmaster.com NoDriver 平台遷移

**分支**：`007-ticketmaster-nodriver-migration` | **日期**：2025-11-15 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/007-ticketmaster-nodriver-migration/spec.md` 的功能規格說明

**注意**：本範本由 `/speckit.plan` 指令填寫。執行流程請參見 `.specify/templates/commands/plan.md`。

## 摘要

本功能旨在將 Ticketmaster.com 平台的搶票自動化功能從 Chrome Driver (Selenium/UC) 遷移至 NoDriver 引擎,遵循專案憲法第 I 條「NoDriver First」原則。核心工作包括:

1. **日期自動選擇** (P1) - 在藝人活動頁面(`/artist/`)自動識別並點選符合關鍵字的演出場次
2. **座位區域選擇** (P1) - 在座位選擇頁面(`/ticket/area/`)解析 zone_info 並自動選擇符合條件的座位區域
3. **票數設定** (P2) - 在票務頁面自動設定購買張數並填寫促銷碼
4. **驗證碼處理** (P3) - 自動勾選條款並整合 OCR 驗證碼辨識

**技術策略**: 將現有 Chrome Driver 版本的 8 個核心函數遷移至 NoDriver,使用 CDP (Chrome DevTools Protocol) API 替代 Selenium API,確保與 Tixcraft 家族其他平台的程式碼隔離。

## 技術上下文 (Technical Context)

**語言/版本**：Python 3.8+（專案需求,支援 async/await 語法）
**主要相依性 (dependency)**：
- NoDriver（CDP-based 瀏覽器自動化,專案主力引擎）
- ddddocr（驗證碼辨識,若啟用 OCR 功能）
- 現有 util 模組（關鍵字匹配、格式化、選擇邏輯等共用工具）

**儲存方式**：
- 設定檔: `settings.json`（使用者配置,遵循憲法第 V 條「設定驅動開發」）
- 失敗記錄: 記憶體內暫存（促銷碼、驗證碼答案等,避免重複嘗試）
- 日誌輸出: stdout/檔案（由 `config["advanced"]["verbose"]` 控制）

**測試**：
- 快速測試: `timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`
- 整合測試: 手動驗證（需訪問真實 Ticketmaster.com 頁面,暫無 fixtures）
- 單元測試: pytest（針對 util 工具函數,如關鍵字匹配邏輯）

**目標平台**：Windows/Linux/macOS（Chrome/Chromium 瀏覽器,透過 NoDriver 控制）

**專案類型**：Single project（CLI 自動化工具）

**效能目標**：
- 整體流程耗時不超過原 Chrome Driver 版本的 110%（SC-003）
- 日期匹配成功率 ≥90%（SC-001）
- zone_info JSON 解析成功率 ≥95%（SC-002）

**限制條件**：
- 跨平台隔離度 100%（不影響 Tixcraft 家族其他平台,SC-004）
- 除錯日誌可理解性協助率 ≥85%（SC-005）
- 記憶體使用 <500MB（專案整體假設）

**規模/範圍**：
- 遷移函數: 8 個核心函數（見「包含在此功能中」區塊）
- 支援頁面: 3 個關鍵 URL 路徑（/artist/, /ticket/area/, /ticket/check-captcha/）
- 程式碼量: 約 300-500 行（參考 Chrome 版本規模）

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

### I. NoDriver First（技術架構優先性）
✅ **符合** - 本功能明確以 NoDriver 為首選引擎,所有實作均基於 CDP API
✅ **符合** - Chrome Driver 版本僅作為參考,不接受新功能開發
✅ **符合** - 將在 README.md 中更新 Ticketmaster.com 的 NoDriver 支援狀態

### II. 資料結構優先（設計先於實作）
✅ **已完成** - Phase 0 已研究並記錄 zone_info JSON 的完整資料結構（見 research.md）
✅ **已完成** - Phase 1 已產生 data-model.md,定義核心實體（演出場次、座位區域、設定項、失敗記錄）
✅ **已完成** - Phase 1 已產生 contracts/,定義函數介面與配置 schema（function-interface.md, zone-info-schema.md）

### III. 三問法則（決策守門人）

**第一問：「是核心問題嗎？」**
✅ **是** - 日期選擇與座位選擇是搶票流程的核心環節,缺少無法完成自動化

**第二問：「有更簡單的方法嗎？」**
✅ **已選最簡方案** - 直接遷移現有邏輯,避免過度重構
✅ **已選最簡方案** - 優先使用 ticketPriceList 表格,失敗後回退到 zone_info 解析（見 spec.md 邊界情境）

**第三問：「會破壞相容性嗎？」**
✅ **不會** - 不修改 settings.json schema（沿用現有配置欄位）
✅ **不會** - 透過 domain_name 判斷確保不影響其他 Tixcraft 家族平台
✅ **不會** - 不改變現有 util 工具函數的介面

### IV. 單一職責與可組合性（函數設計原則）
✅ **符合** - 每個遷移函數有明確職責（例：`ticketmaster_date_auto_select()` 僅處理日期選擇）
✅ **符合** - 複雜邏輯分解為小函數（例：`ticketmaster_parse_zone_info()` 專門負責 JSON 解析）
✅ **符合** - 共用邏輯使用 util.py 工具函數（`get_matched_blocks_by_keyword()` 等）

### V. 設定驅動開發（使用者友善設計）
✅ **符合** - 所有行為由 settings.json 控制（日期關鍵字、區域關鍵字、票數、OCR 啟用等）
✅ **符合** - 不在程式碼中硬寫配置值
✅ **符合** - 設定項已在 spec.md 的「功能相依性」區塊明確記錄

### VI. 測試驅動穩定性（品質守門人）
⚠️ **待完成** - Phase 2 需實作測試驗證（手動測試步驟需文件化）
⚠️ **風險** - Ticketmaster.com 需要真實頁面測試,無法使用 fixtures（已在 spec.md 風險 1 記錄）
✅ **符合** - util 工具函數已有單元測試覆蓋（假設現有測試涵蓋關鍵字匹配邏輯）

### VII. MVP 原則（最小可行產品優先）
✅ **符合** - User Story 已按優先級分類（P1: 日期/區域選擇, P2: 票數設定, P3: 驗證碼）
✅ **符合** - P1 故事可獨立測試（見 spec.md 的「獨立測試方式」）
✅ **符合** - 排除非核心功能（自動登入、圖形座位圖視覺化、排隊與付款深度自動化）

### VIII. 文件與代碼同步（知識傳承）
✅ **符合** - spec.md 已詳細記錄功能需求與成功標準
✅ **已完成** - Phase 1 已產生 quickstart.md
⚠️ **待完成** - 實作後需更新 `docs/02-development/structure.md`（新增函數索引）
⚠️ **待完成** - 實作後需更新 `README.md`（Ticketmaster.com 支援狀態）

### IX. Git 提交規範與工作流程（版本控制紀律）
✅ **符合** - 使用 `/gsave` 指令建立 commits
✅ **符合** - 分支命名遵循規範（`007-ticketmaster-nodriver-migration`）
✅ **符合** - 提交訊息將遵循 Conventional Commits 格式（feat(nodriver): ...）
✅ **符合** - 機敏檔案（docs/, specs/, CLAUDE.md）將透過 `/privatepush` 分離推送

### 代碼品質標準
✅ **符合** - 程式碼中不使用 emoji（僅限 Markdown 文件）
✅ **符合** - 沿用現有暫停機制（假設 util.py 已實作 `pause_before_checkout()`）
✅ **符合** - 不蒐集用戶個人資訊,日誌中不包含敏感資料

### 檢查點總結（Phase 1 設計完成後更新）
- **通過項目**: 26 項 ✅（+4 項，Phase 0/1 完成）
- **待完成項目**: 3 項 ⚠️（Phase 2 實作與文件更新）
- **風險項目**: 1 項（測試需依賴真實網站,已在 spec 記錄緩解措施）
- **阻斷項目**: 0 項 ❌

**結論**:
- ✅ Phase 0 研究階段已完成（research.md）
- ✅ Phase 1 設計階段已完成（data-model.md, contracts/, quickstart.md）
- ✅ 通過 Constitution Check,可進入 Phase 2 實作階段（使用 `/speckit.tasks` 與 `/speckit.implement`）

## 專案結構

### 文件（本功能）

```
specs/007-ticketmaster-nodriver-migration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (pending)
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   ├── function-interface.md    # 8 個核心函數的介面定義
│   ├── config-schema.md         # Ticketmaster 特定配置項（若有新增）
│   └── zone-info-schema.md      # zone_info JSON 的結構定義
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### 原始碼（repository 根目錄）

```
tickets_hunter/
├── src/
│   ├── nodriver_tixcraft.py         # 主流程（需整合 Ticketmaster 特定 URL 路徑判斷）
│   ├── util.py                      # 共用工具函數（關鍵字匹配、格式化、選擇邏輯）
│   ├── settings.json                # 使用者配置檔（不修改 schema,沿用現有欄位）
│   └── (新增 Ticketmaster 函數於 nodriver_tixcraft.py 或獨立模組)
│
├── tests/
│   ├── unit/
│   │   └── test_util.py             # util 工具函數測試（現有）
│   └── integration/
│       └── test_ticketmaster_flow.py # Ticketmaster 整合測試（Phase 2 新增）
│
├── docs/
│   ├── 02-development/
│   │   └── structure.md             # 需更新：新增 Ticketmaster 函數索引
│   ├── 06-api-reference/
│   │   └── nodriver_api_guide.md    # 參考文件（現有）
│   └── 08-troubleshooting/
│       └── ticketmaster_*.md        # 問題排解記錄（實作後新增）
│
└── README.md                        # 需更新：Ticketmaster.com 支援狀態
```

**結構決策**：
- **Single project 結構** - 專案為 CLI 自動化工具,不涉及前後端分離
- **函數組織** - Ticketmaster 函數直接新增至 `nodriver_tixcraft.py`,與現有 Tixcraft/KKTIX/iBon 函數並列（透過 domain_name 判斷隔離）
- **替代方案** - 若 `nodriver_tixcraft.py` 檔案過長（>1000 行）,可考慮提取至獨立模組 `nodriver_ticketmaster.py`,但需評估是否違反「YAGNI 原則」（目前程式碼量估計 300-500 行,暫不需要）

## 複雜度追蹤

*僅在專案憲章檢查（Constitution Check）有違規且必須說明時填寫*

| 違規項目 | 為何需要 | 為何拒絕更簡單的替代方案 |
|----------|----------|--------------------------|
| 無 | - | - |

**說明**: 本功能完全符合憲章原則,無複雜度違規需要說明。主要風險在於測試需依賴真實網站（已在 spec.md 風險 1 記錄緩解措施）。
