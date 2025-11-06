# 文件維護工作流程

> **目標**：規範文件更新流程，確保文件與代碼同步，降低維護成本

## 自動更新規則

**新功能實作完成後，Claude 必須自動更新以下文件：**

### 1. structure.md - 平台實作狀態更新
- **新平台**：加入完整函數樹狀圖與行號索引
- **現有平台**：更新函數行號與實作狀態
- **功能完整度評分**：根據 ticket_automation_standard.md 評分
- **實作狀態表**：更新完成度標記

### 2. todo.md - 待辦事項狀態更新
- 標記已實作功能為完成 ✅
- 新增實作過程中發現的技術債務
- 調整優先度分類

### 3. coding_templates.md - 範本優化更新
- 僅在發現通用性改善時更新
- 保持平台無關性原則

### 4. ticket_automation_standard.md - 標準架構更新（謹慎）
- **僅在以下情況更新**：
  - 發現新的通用功能模組
  - 設定項目有重大變更
  - 函式拆分原則需要補充
- **禁止頻繁修改**：此為標準定義文件，需保持穩定性

## 更新時機

### 觸發自動更新的情況
- **實作新平台完整支援**
- **修復核心功能問題**
- **重構影響多個平台的共用代碼**

### 不觸發更新的情況
- 小幅度程式碼調整
- 單純的 bug 修復
- 註釋或格式化變更

## 權限範圍

### ✅ Claude 可自動更新 (無需詢問用戶)
- **僅限以下文件**：
  - `/docs/todo.md`
  - `/docs/structure.md`
- **更新內容**：
  - 實作完成後的狀態更新
  - todo 項目狀態標記變更
  - 發現的技術債務記錄

### ❌ 禁止自動更新 (需要用戶確認)
- **`settings.json` 或設定相關檔案**
- **新增全新的文件檔案**
- **修改現有文件結構**

## 文件間依賴關係

### 核心架構文件（新增）
```
ticket_automation_standard.md （標準定義）
    ↓ 定義 12 階段功能架構
structure.md （實作分析）
    ↓ 對照標準架構評分
development_guide.md （開發規範）
    ↓ 提供檢查清單與拆分原則
```

### 完整依賴關係圖
```
CLAUDE.md (主文件)
├─ 引用 → /docs/ticket_automation_standard.md （核心標準）
├─ 引用 → /docs/development_guide.md
├─ 引用 → /docs/project_overview.md
├─ 引用 → /docs/structure.md
└─ 引用 → 除錯與測試指南系列（NoDriver 優先）
    ├─ nodriver_api_guide.md （推薦優先）
    ├─ chrome_api_guide.md
    ├─ selenium_api_guide.md
    ├─ debugging_methodology.md
    └─ testing_execution_guide.md （測試執行標準）

ticket_automation_standard.md
└─ 獨立文件，定義標準架構（其他文件引用此文件）

structure.md
├─ 引用 → ticket_automation_standard.md （評分標準）
└─ 被引用 → development_guide.md, CLAUDE.md

development_guide.md
├─ 引用 → ticket_automation_standard.md （功能檢查清單）
├─ 引用 → structure.md （函數架構參考）
├─ 引用 → coding_templates.md
└─ 引用 → API 指南系列

project_overview.md
├─ 引用 → ticket_automation_standard.md （架構關聯圖）
├─ 引用 → development_guide.md
├─ 引用 → structure.md
└─ 引用 → setup.md
```

## 更新檢查清單

### 實作新平台後必須檢查
- [ ] **structure.md** - 新增平台函數索引與行號
- [ ] **structure.md** - 根據 ticket_automation_standard.md 評分（100 分制）
- [ ] **structure.md** - 更新平台實作對照表
- [ ] **todo.md** - 標記已完成的 todo 項目
- [ ] **development_guide.md** - 檢查是否需要補充新的實作範例

### 實作新功能後必須檢查
- [ ] 是否影響函數行號 (更新 structure.md)
- [ ] 是否完成 todo 項目 (更新 todo.md)
- [ ] 是否發現技術債務 (記錄到 todo.md)
- [ ] 是否有更好的實作範本 (評估是否更新 coding_templates.md)

### 標準架構變更檢查（謹慎）
- [ ] **ticket_automation_standard.md** - 是否發現新的通用功能模組？
- [ ] **ticket_automation_standard.md** - settings.json 是否新增設定項目？
- [ ] **ticket_automation_standard.md** - 函式拆分原則是否需要補充？
- [ ] **注意**：此文件為標準定義，變更需審慎評估影響範圍

### 文件連結檢查
- [ ] 所有相對路徑連結可正常存取
- [ ] 文件間交叉引用正確
- [ ] 範例程式碼與實際實作一致
- [ ] 新增的文件已加入 CLAUDE.md 參考清單

## 版本控制原則

### 文件版本標記
```markdown
---
**更新日期**: YYYY-MM-DD
**適用版本**: TicketsHunter v2025.09.xx
**相關文件**: [連結清單]
```

### 重大變更記錄
- **架構變更**：記錄到 update.md
- **API 變更**：更新對應 API 指南
- **新平台支援**：更新 structure.md（含評分）
- **標準架構變更**：更新 ticket_automation_standard.md（謹慎處理）

## 文件更新優先度

### 高優先度（必須立即更新）
1. **structure.md** - 新平台實作或函數行號變更
2. **todo.md** - 功能完成狀態標記
3. **CLAUDE.md** - 新增核心文件時更新引用

### 中優先度（階段性更新）
4. **development_guide.md** - 發現新的最佳實踐
5. **coding_templates.md** - 通用範本改善
6. **API 指南系列** - API 使用方式變更
7. **testing_execution_guide.md** - 測試執行指令更新

### 低優先度（審慎評估後更新）
8. **ticket_automation_standard.md** - 標準架構定義變更
9. **project_overview.md** - 系統架構重大變更

## 質量保證

### 文件質量標準
1. **完整性**：涵蓋所有必要資訊
2. **準確性**：與程式碼實作一致
3. **時效性**：及時反映最新狀況
4. **可用性**：易於查找和理解

### 自動檢查項目
- 連結有效性
- 程式碼範例語法正確
- 文件結構完整
- 交叉引用準確

---

**更新日期**: 2025-10-28
**相關文件**: [標準功能定義](./ticket_automation_standard.md) | [函數結構](./structure.md) | [開發規範](./development_guide.md) | [專案概覽](./project_overview.md)