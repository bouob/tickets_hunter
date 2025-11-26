---
description: "使用計畫模板（plan template）執行實作規劃工作流程，以產生設計產物。"
model: opus
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
---

## 使用者輸入

```text
$ARGUMENTS
```

您 **必須** 在繼續之前考量使用者輸入（如非空白）。

## 大綱

1. **設定**：從儲存庫根目錄執行 `.specify/scripts/powershell/setup-plan.ps1 -Json`，並解析 JSON 以取得 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH。對於參數中的單引號（如 "I'm Groot"），使用跳脫語法：例如 'I'\''m Groot'（或盡可能使用雙引號："I'm Groot"）。

2. **載入環境**：讀取 FEATURE_SPEC 和 `.specify/memory/constitution.md`。載入 IMPL_PLAN 模板（已複製）。

3. **執行計畫工作流程**：依循 IMPL_PLAN 模板中的結構：
   - 填寫技術環境（將未知標記為「需要釐清」）
   - 從憲法填寫憲法檢查區塊
   - 評估關卡（如違規未合理化則報錯）
   - 階段 0：產生 research.md（解決所有需要釐清的項目）
   - 階段 1：產生 data-model.md、contracts/、quickstart.md
   - 階段 1：透過執行代理腳本更新代理環境
   - 設計後重新評估憲法檢查

4. **停止並報告**：指令在階段 2 規劃後結束。報告分支、IMPL_PLAN 路徑和產生的產物。

## 階段

### 階段 0：大綱與研究

1. **從上方技術環境擷取未知項目**：
   - 對於每個「需要釐清」→ 研究任務
   - 對於每個相依性 → 最佳實務任務
   - 對於每個整合 → 模式任務

2. **產生並分派研究代理**：

   ```text
   對於技術環境中的每個未知項目：
     任務："研究 {unknown} 用於 {feature context}"
   對於每個技術選擇：
     任務："尋找 {tech} 在 {domain} 的最佳實務"
   ```

3. **整合發現** 到 `research.md`，使用格式：
   - 決策：[選擇了什麼]
   - 理由：[為什麼選擇]
   - 考慮的替代方案：[還評估了什麼]

**輸出**：research.md，所有「需要釐清」已解決

### 階段 1：設計與契約

**先決條件：** `research.md` 完成

1. **從功能規格擷取實體** → `data-model.md`：
   - 實體名稱、欄位、關係
   - 來自需求的驗證規則
   - 狀態轉換（如適用）

2. **從功能需求產生 API 契約**：
   - 對於每個使用者動作 → 端點
   - 使用標準 REST/GraphQL 模式
   - 輸出 OpenAPI/GraphQL 結構描述到 `/contracts/`

3. **代理環境更新**：
   - 執行 `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
   - 這些腳本偵測正在使用哪個 AI 代理
   - 更新適當的代理特定環境檔案
   - 僅從目前計畫新增新技術
   - 在標記之間保留手動新增的內容

**輸出**：data-model.md、/contracts/*、quickstart.md、代理特定檔案

## 關鍵規則

- 使用絕對路徑
- 關卡失敗或未解決的釐清時報錯
