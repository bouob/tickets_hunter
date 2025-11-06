---
description: 根據可用的設計產物，為該功能產生一份可執行、依相依性（dependency）排序的 tasks.md。
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 用戶輸入

```text
$ARGUMENTS
```

在繼續執行前，您**必須**考慮用戶輸入（若非空）。

## 大綱

1. **設定**：從 repo 根目錄執行 `{SCRIPT}`，並解析 FEATURE_DIR 及 AVAILABLE_DOCS 清單。所有路徑必須為絕對路徑。對於引數中如 "I'm Groot" 這類帶有單引號的內容，請使用跳脫語法：例如 'I'\''m Groot'（或若可行則用雙引號："I'm Groot"）。

2. **載入設計文件**：從 FEATURE_DIR 讀取：
   - **必要**：plan.md（技術堆疊、函式庫、結構）、spec.md（用戶故事及其優先順序）
   - **選用**：data-model.md（實體）、contracts/（API endpoint）、research.md（決策）、quickstart.md（測試情境）
   - 注意：並非所有專案都具備上述所有文件。請依現有文件產生任務。

3. **執行任務產生工作流程**：
   - 載入 plan.md 並擷取技術堆疊、函式庫、專案結構
   - 載入 spec.md 並擷取用戶故事及其優先順序（P1、P2、P3 等）
   - 若有 data-model.md：擷取實體並對應到用戶故事
   - 若有 contracts/：將 API endpoint 對應到用戶故事
   - 若有 research.md：擷取決策以產生設定任務
   - 依用戶故事產生任務（詳見下方「任務產生規則」）
   - 產生顯示用戶故事完成順序的相依性（dependency）圖
   - 為每個用戶故事建立可並行執行的範例
   - 驗證任務完整性（每個用戶故事皆有所需任務，且可獨立測試）

4. **產生 tasks.md**：以 `.specify/templates/tasks-template.md` 為結構，內容包含：
   - 從 plan.md 取得正確的功能名稱
   - Phase 1：設定任務（專案初始化）
   - Phase 2：基礎任務（所有用戶故事的阻斷前置作業）
   - Phase 3+：每個用戶故事一個階段（依 spec.md 的優先順序）
   - 每個階段包含：故事目標、獨立測試標準、測試（如有需求）、實作任務
   - 最終階段：優化與橫向議題
   - 所有任務必須遵循嚴格的檢查清單格式（詳見下方「任務產生規則」）
   - 每個任務需明確標示檔案路徑
   - 相依性區段，顯示用戶故事完成順序
   - 每個用戶故事的並行執行範例
   - 實作策略區段（先 MVP（最小可行性產品），逐步交付）

5. **報告**：輸出產生的 tasks.md 路徑及摘要：
   - 任務總數
   - 各用戶故事的任務數
   - 已識別的並行機會
   - 各用戶故事的獨立測試標準
   - 建議的 MVP（最小可行性產品）範圍（通常僅為 User Story 1）
   - 格式驗證：確認**所有**任務皆符合檢查清單格式（核取方塊、ID、標籤、檔案路徑）

任務產生的上下文：{ARGS}

產生的 tasks.md 應可立即執行——每個任務須具體明確，使大型語言模型 (LLM) 能在無額外上下文下完成。

## 任務產生規則

**關鍵**：任務**必須**依用戶故事組織，以利獨立實作與測試。

**測試為選用**：僅當功能規格說明明確要求，或用戶要求採用 TDD（測試優先）方法時，才產生測試任務。

### 檢查清單格式（必須）

每個任務**必須**嚴格遵循以下格式：

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**格式組成要素**：

1. **核取方塊**：一律以 `- [ ]`（Markdown 核取方塊）起始
2. **任務 ID**：依執行順序遞增編號（T001、T002、T003...）
3. **[P] 標記**：僅在任務可並行執行時加入（不同檔案、且無未完成任務的相依性）
4. **[Story] 標籤**：僅限 User Story 階段任務必須加上
   - 格式：[US1]、[US2]、[US3] 等（對應 spec.md 中的 user story）
   - Setup 階段：不加 story 標籤
   - Foundational 階段：不加 story 標籤  
   - User Story 階段：必須加上 story 標籤
   - Polish 階段：不加 story 標籤
5. **描述**：明確的動作說明，並標註精確的檔案路徑

**範例**：

- ✅ 正確：`- [ ] T001 Create project structure per implementation plan`
- ✅ 正確：`- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正確：`- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正確：`- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 錯誤：`- [ ] Create User model`（缺少 ID 與 Story 標籤）
- ❌ 錯誤：`T001 [US1] Create model`（缺少核取方塊）
- ❌ 錯誤：`- [ ] [US1] Create User model`（缺少任務 ID）
- ❌ 錯誤：`- [ ] T001 [US1] Create model`（缺少檔案路徑）

### 任務組織方式

1. **依 User Stories（spec.md）為主進行組織**：
   - 每個 user story（P1、P2、P3...）各自成為一個階段
   - 將所有相關元件對應到該 story：
     - 該 story 需要的 models
     - 該 story 需要的 services
     - 該 story 需要的 endpoints/UI
     - 若有測試需求：針對該 story 的測試
   - 標註 story 之間的相依性（大多數 story 應為獨立）

2. **依 Contracts**：
   - 將每個 contract/endpoint → 對應到其所屬的 user story
   - 若有測試需求：每個 contract → contract 測試任務 [P]，於該 story 階段的實作前執行

3. **依 Data Model**：
   - 將每個 entity 對應到需要它的 user story
   - 若 entity 服務多個 story：放在最早需要的 story 或 Setup 階段
   - 關聯性 → 在適當的 story 階段建立 service 層任務

4. **依 Setup/Infrastructure**：
   - 共用基礎設施 → 放在 Setup 階段（Phase 1）
   - 基礎/阻擋性任務 → 放在 Foundational 階段（Phase 2）
   - 特定 story 的 setup → 放在該 story 階段

### 階段結構

- **Phase 1**：Setup（專案初始化）
- **Phase 2**：Foundational（阻擋性前置作業——必須在 user stories 前完成）
- **Phase 3 以上**：依優先順序執行 User Stories（P1、P2、P3...）
  - 每個 story 內部順序：測試（如有需求）→ Models → Services → Endpoints → 整合
  - 每個階段都應該是完整、可獨立測試的增量
- **最終階段**：Polish 與跨階段關注事項


