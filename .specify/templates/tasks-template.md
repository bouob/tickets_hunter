---
description: "功能實作任務清單範本"
---

# 任務： [FEATURE NAME]

**輸入**：來自 `/specs/[###-feature-name]/` 的設計文件  
**前置需求**：plan.md（必填）、spec.md（若有 user stories 必填）、research.md、data-model.md、contracts/

**測試**：下方範例包含測試任務。測試為「選填」——僅在功能規格說明中明確要求時才需包含。

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（如 US1、US2、US3）
- 描述中請包含精確的檔案路徑

## 路徑命名慣例
- **單一專案**：`src/`、`tests/` 於 repository 根目錄
- **Web app**：`backend/src/`、`frontend/src/`
- **Mobile**：`api/src/`、`ios/src/` 或 `android/src/`
- 下方路徑預設為單一專案——請依 plan.md 結構調整

<!-- 
  ============================================================================
  重要說明：下方任務僅為「範例任務」，僅供說明用途。
  
  /speckit.tasks 指令「必須」根據下列來源產生實際任務，取代這些範例內容：
  - 來自 spec.md 的 user stories（含其優先順序 P1、P2、P3...）
  - 來自 plan.md 的功能需求
  - 來自 data-model.md 的實體
  - 來自 contracts/ 的 endpoint
  
  任務必須依 user story 分組，使每個 story 可：
  - 獨立實作
  - 獨立測試
  - 作為 MVP（最小可行性產品）增量交付
  
  請勿在產生的 tasks.md 檔案中保留這些範例任務。
  ============================================================================
-->

## 階段一：初始化（共用基礎設施）

**目的**：專案初始化與基本結構建立

- [ ] T001 依實作計畫建立專案結構
- [ ] T002 使用 [language] 初始化專案並安裝 [framework] 相依套件
- [ ] T003 [P] 設定 lint 與程式碼格式化工具

---

## 階段二：基礎建設（阻斷性前置需求）

**目的**：所有 user story 開始前「必須」完成的核心基礎設施

**⚠️ 關鍵**：本階段未完成前，不得開始任何 user story 實作

基礎建設任務範例（請依專案調整）：

- [ ] T004 設定資料庫 schema 與遷移框架
- [ ] T005 [P] 實作驗證/授權（authentication/authorization）框架
- [ ] T006 [P] 設定 API 路由與 middleware 架構
- [ ] T007 建立所有 stories 依賴的基礎 models/entities
- [ ] T008 設定錯誤處理與日誌（logging）基礎設施
- [ ] T009 設定環境變數（environment configuration）管理

**檢查點**：基礎設施就緒——user story 實作可開始平行進行

---

## 階段三：User Story 1 - [標題] (Priority: P1) 🎯 MVP

**目標**：[簡述此 user story 交付內容]

**獨立測試**：[如何單獨驗證此 story 功能]

### User Story 1 測試（選填——僅在有明確測試需求時）⚠️

**注意：請先撰寫這些測試，並確保在實作前測試會失敗**

- [ ] T010 [P] [US1] 針對 [endpoint] 的 contract test，路徑：tests/contract/test_[name].py
- [ ] T011 [P] [US1] 針對 [user journey] 的整合測試（integration test），路徑：tests/integration/test_[name].py

### User Story 1 實作

- [ ] T012 [P] [US1] 在 src/models/[entity1].py 建立 [Entity1] model
- [ ] T013 [P] [US1] 在 src/models/[entity2].py 建立 [Entity2] model
- [ ] T014 [US1] 在 src/services/[service].py 實作 [Service]（依賴 T012, T013）
- [ ] T015 [US1] 在 src/[location]/[file].py 實作 [endpoint/feature]
- [ ] T016 [US1] 加入驗證與錯誤處理
- [ ] T017 [US1] 為 User Story 1 操作加入日誌

**檢查點**：此時 User Story 1 應可完全獨立運作並可測試

---

## 階段四：User Story 2 - [標題] (Priority: P2)

**目標**：[簡述此 user story 交付內容]

**獨立測試**：[如何單獨驗證此 story 功能]

### User Story 2 測試（選填——僅在有明確測試需求時）⚠️

- [ ] T018 [P] [US2] 針對 [endpoint] 的 contract test，路徑：tests/contract/test_[name].py
- [ ] T019 [P] [US2] 針對 [user journey] 的整合測試（integration test），路徑：tests/integration/test_[name].py

### User Story 2 實作

- [ ] T020 [P] [US2] 在 src/models/[entity].py 建立 [Entity] model
- [ ] T021 [US2] 在 src/services/[service].py 實作 [Service]
- [ ] T022 [US2] 在 src/[location]/[file].py 實作 [endpoint/feature]
- [ ] T023 [US2] 若有需要，與 User Story 1 元件整合（integration）

**檢查點**：此時 User Story 1 與 2 均應能獨立運作

---

## 階段五：User Story 3 - [標題] (Priority: P3)

**目標**：[簡述此 user story 交付內容]

**獨立測試**：[如何單獨驗證此 story 功能]

### User Story 3 測試（選填——僅在有明確測試需求時）⚠️

- [ ] T024 [P] [US3] 針對 [endpoint] 的 contract test，路徑：tests/contract/test_[name].py
- [ ] T025 [P] [US3] 針對 [user journey] 的整合測試（integration test），路徑：tests/integration/test_[name].py

### User Story 3 實作

- [ ] T026 [P] [US3] 在 src/models/[entity].py 建立 [Entity] model
- [ ] T027 [US3] 在 src/services/[service].py 實作 [Service]
- [ ] T028 [US3] 在 src/[location]/[file].py 實作 [endpoint/feature]

**檢查點**：所有 user stories 均應可獨立運作

---

[如有更多 user story，請依相同格式新增階段]

---

## 階段 N：優化與橫向議題

**目的**：影響多個 user story 的改善項目

- [ ] TXXX [P] 在 docs/ 更新文件
- [ ] TXXX 程式碼清理與重構
- [ ] TXXX 全體效能優化
- [ ] TXXX [P] 額外單元測試（若有需求）於 tests/unit/
- [ ] TXXX 強化安全性
- [ ] TXXX 執行 quickstart.md 驗證

---

## 相依性（dependency）與執行順序

### 階段相依性

- **初始化（階段一）**：無相依性——可立即開始
- **基礎建設（階段二）**：依賴初始化完成——阻斷所有 user story
- **User Stories（階段三起）**：皆依賴基礎建設完成
  - User stories 可平行進行（如人力允許）
  - 或依優先順序（P1 → P2 → P3）依序進行
- **優化（最終階段）**：依賴所有目標 user story 完成

### User Story 相依性

- **User Story 1（P1）**：基礎建設（階段二）完成後可開始——不依賴其他 stories
- **User Story 2（P2）**：基礎建設（階段二）完成後可開始——可與 US1 整合（integration），但應可獨立測試
- **User Story 3（P3）**：基礎建設（階段二）完成後可開始——可與 US1/US2 整合（integration），但應可獨立測試

### 每個 User Story 內部

- 測試（如有）必須先撰寫，且在實作前應為失敗狀態
- 先建立 models，再實作 services
- services 完成後再實作 endpoints
- 先完成核心實作，再進行整合（integration）
- 完成一個 story 才能進入下一個優先順序

### 平行作業機會

- 所有標記 [P] 的初始化任務可平行執行
- 所有標記 [P] 的基礎建設任務（階段二）可平行執行
- 基礎建設完成後，所有 user story 可平行啟動（如團隊人力允許）
- 每個 user story 內所有標記 [P] 的測試可平行執行
- 同一 story 內標記 [P] 的 models 可平行開發
- 不同 user story 可由不同成員平行進行

---

## 平行作業範例：User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1）

1. 完成階段 1：Setup
2. 完成階段 2：基礎建設（關鍵－會阻擋所有 User Story）
3. 完成階段 3：User Story 1
4. **停止並驗證**：獨立測試 User Story 1
5. 若已準備好則部署／展示

### 漸進式交付

1. 完成 Setup + 基礎建設 → 基礎已就緒
2. 加入 User Story 1 → 獨立測試 → 部署／展示（MVP！）
3. 加入 User Story 2 → 獨立測試 → 部署／展示
4. 加入 User Story 3 → 獨立測試 → 部署／展示
5. 每個 User Story 都能在不破壞前一個 User Story 的情況下增加價值

### 團隊平行開發策略

若有多位開發者：

1. 團隊共同完成 Setup + 基礎建設
2. 基礎建設完成後：
   - 開發者 A：User Story 1
   - 開發者 B：User Story 2
   - 開發者 C：User Story 3
3. 各 User Story 可獨立完成並整合

---

## 備註

- [P] 任務 = 不同檔案，無相依性（dependency）
- [Story] 標籤可將任務對應到特定 User Story，方便追蹤
- 每個 User Story 都應能獨立完成與測試
- 實作前請先確認測試會失敗
- 每完成一個任務或邏輯群組就提交（commit）
- 可在任何檢查點（checkpoint）停止，獨立驗證 User Story
- 請避免：任務描述模糊、同檔案衝突、跨 User Story 的相依性（dependency）導致無法獨立



