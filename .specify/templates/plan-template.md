# 實作計畫：[FEATURE]

**分支**：`[###-feature-name]` | **日期**：[DATE] | **規格**：[link]  
**輸入**：來自 `/specs/[###-feature-name]/spec.md` 的功能規格說明

**注意**：本範本由 `/speckit.plan` 指令填寫。執行流程請參見 `.specify/templates/commands/plan.md`。

## 摘要

[摘錄自功能規格說明：主要需求 + 研究所得技術方案]

## 技術上下文 (Technical Context)

<!--
  需要執行的動作：請將本區內容替換為本專案的技術細節。
  此結構僅作為建議，協助引導後續的迭代流程。
-->

**語言/版本**：[例如：Python 3.11、Swift 5.9、Rust 1.75 或 NEEDS CLARIFICATION]  
**主要相依性 (dependency)**：[例如：FastAPI、UIKit、LLVM 或 NEEDS CLARIFICATION]  
**儲存方式**：[如適用，例：PostgreSQL、CoreData、檔案或 N/A]  
**測試**：[例如：pytest、XCTest、cargo test 或 NEEDS CLARIFICATION]  
**目標平台**：[例如：Linux server、iOS 15+、WASM 或 NEEDS CLARIFICATION]  
**專案類型**：[single/web/mobile - 決定原始碼結構]  
**效能目標**：[領域相關，例如：1000 req/s、10k lines/sec、60 fps 或 NEEDS CLARIFICATION]  
**限制條件**：[領域相關，例如：<200ms p95、<100MB 記憶體、可離線運作或 NEEDS CLARIFICATION]  
**規模/範圍**：[領域相關，例如：1 萬用戶、100 萬行程式碼、50 個畫面或 NEEDS CLARIFICATION]

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

[依據憲章檔案所決定的檢查點]

## 專案結構

### 文件（本功能）

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### 原始碼（repository 根目錄）
<!--
  需要採取行動：請將下方的占位目錄樹替換為此功能的實際目錄結構。
  刪除未使用的選項，並以實際路徑（例如：apps/admin、packages/something）擴充所選結構。
  交付的計畫中不得包含 Option 標籤。
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**結構決策**： [記錄所選擇的結構，並引用上方所擷取的實際目錄]

## 複雜度追蹤

*僅在專案憲章檢查（Constitution Check）有違規且必須說明時填寫*

| 違規項目 | 為何需要 | 為何拒絕更簡單的替代方案 |
|----------|----------|--------------------------|
| [例如：第 4 個專案] | [目前需求] | [為何 3 個專案不夠] |
| [例如：Repository pattern] | [具體問題] | [為何直接存取資料庫不夠] |

