# 實作計畫：[功能]

**分支**：`[###-feature-name]` | **日期**：[日期] | **規格**：[連結]
**輸入**：來自 `/specs/[###-feature-name]/spec.md` 的功能規格

**注意**：此模板由 `/speckit.plan` 指令填入。請參閱 `.specify/templates/commands/plan.md` 以取得執行工作流程。

## 摘要

[從功能規格擷取：主要需求 + 來自研究的技術方法]

## 技術環境

<!--
  需要操作：將此區塊中的內容替換為專案的技術細節。
  此處的結構以建議性質呈現，以引導迭代過程。
-->

**語言/版本**：[例如，Python 3.11、Swift 5.9、Rust 1.75 或需要釐清]
**主要相依性**：[例如，FastAPI、UIKit、LLVM 或需要釐清]
**儲存**：[如適用，例如，PostgreSQL、CoreData、檔案或不適用]
**測試**：[例如，pytest、XCTest、cargo test 或需要釐清]
**目標平台**：[例如，Linux 伺服器、iOS 15+、WASM 或需要釐清]
**專案類型**：[單一/網頁/行動裝置 - 決定原始碼結構]
**效能目標**：[領域特定，例如，1000 req/s、10k lines/sec、60 fps 或需要釐清]
**限制**：[領域特定，例如，<200ms p95、<100MB 記憶體、離線可用 或需要釐清]
**規模/範圍**：[領域特定，例如，10k 使用者、1M LOC、50 畫面 或需要釐清]

## 憲法檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

[根據憲法檔案決定的關卡]

## 專案結構

### 文件（此功能）

```text
specs/[###-feature]/
├── plan.md              # 此檔案（/speckit.plan 指令輸出）
├── research.md          # 階段 0 輸出（/speckit.plan 指令）
├── data-model.md        # 階段 1 輸出（/speckit.plan 指令）
├── quickstart.md        # 階段 1 輸出（/speckit.plan 指令）
├── contracts/           # 階段 1 輸出（/speckit.plan 指令）
└── tasks.md             # 階段 2 輸出（/speckit.tasks 指令 - 非由 /speckit.plan 建立）
```

### 原始碼（儲存庫根目錄）
<!--
  需要操作：將下方的佔位符樹狀結構替換為此功能的具體佈局。
  刪除未使用的選項，並以真實路徑（例如，apps/admin、packages/something）
  展開所選結構。交付的計畫不得包含選項標籤。
-->

```text
# [如未使用則移除] 選項 1：單一專案（預設）
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [如未使用則移除] 選項 2：網頁應用程式（偵測到「frontend」+「backend」時）
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

# [如未使用則移除] 選項 3：行動裝置 + API（偵測到「iOS/Android」時）
api/
└── [同上方 backend]

ios/ 或 android/
└── [平台特定結構：功能模組、UI 流程、平台測試]
```

**結構決策**：[記錄所選結構並參考上方擷取的實際目錄]

## 複雜度追蹤

> **僅在憲法檢查有需要合理化的違規時填寫**

| 違規 | 為何需要 | 較簡單替代方案被拒絕的原因 |
|------|----------|---------------------------|
| [例如，第 4 個專案] | [當前需求] | [為何 3 個專案不足] |
| [例如，Repository 模式] | [具體問題] | [為何直接 DB 存取不足] |
