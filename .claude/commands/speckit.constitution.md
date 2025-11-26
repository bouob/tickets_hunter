---
description: "透過互動模式 (Interactive mode) 或提供的原則輸入，建立或更新專案憲章，並確保所有相依的模板保持同步。"
model: opus
handoffs:
  - label: Build Specification
    agent: speckit.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## 使用者輸入

```text
$ARGUMENTS
```

您 **必須** 在繼續之前考量使用者輸入（如非空白）。

## 大綱

您正在更新位於 `.specify/memory/constitution.md` 的專案憲法。此檔案是一個**模板**，包含方括號中的佔位符標記（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。您的工作是 (a) 收集/導出具體值，(b) 精確填寫模板，以及 (c) 將任何修訂傳播到相依的產物。

依循此執行流程：

1. 載入位於 `.specify/memory/constitution.md` 的現有憲法模板。
   - 識別形式為 `[ALL_CAPS_IDENTIFIER]` 的每個佔位符標記。
   **重要**：使用者可能需要比模板中使用的更少或更多的原則。如果指定了數量，請尊重——依循通用模板。您將相應地更新文件。

2. 收集/導出佔位符的值：
   - 如果使用者輸入（對話）提供了值，使用它。
   - 否則從現有的儲存庫環境推斷（README、docs、先前的憲法版本如有嵌入）。
   - 對於治理日期：`RATIFICATION_DATE` 是最初採用日期（如果未知則詢問或標記 TODO），`LAST_AMENDED_DATE` 是今天（如果有變更），否則保持先前的。
   - `CONSTITUTION_VERSION` 必須根據語意化版本規則遞增：
     - MAJOR：不向後相容的治理/原則移除或重新定義。
     - MINOR：新增原則/區塊或實質擴展的指導。
     - PATCH：釐清、措辭、錯字修正、非語意性細化。
   - 如果版本升級類型不明確，在最終確定前提出理由。

3. 草擬更新的憲法內容：
   - 用具體文字取代每個佔位符（不留下括號標記，除非是專案選擇尚未定義的故意保留模板槽——明確說明任何保留的理由）。
   - 保留標題層級，一旦取代後可移除註解，除非它們仍提供釐清指導。
   - 確保每個原則區塊：簡潔的名稱行、擷取不可協商規則的段落（或條目清單）、如不明顯則有明確的理由。
   - 確保治理區塊列出修訂程序、版本控制政策和合規審查預期。

4. 一致性傳播檢查清單（將先前的檢查清單轉換為主動驗證）：
   - 讀取 `.specify/templates/plan-template.md`，確保任何「憲法檢查」或規則與更新的原則對齊。
   - 讀取 `.specify/templates/spec-template.md` 以確保範圍/需求對齊——如果憲法新增/移除強制區塊或限制則更新。
   - 讀取 `.specify/templates/tasks-template.md`，確保任務分類反映新增或移除的原則驅動任務類型（例如，可觀察性、版本控制、測試紀律）。
   - 讀取 `.specify/templates/commands/*.md` 中的每個指令檔案（包括此檔案），驗證當需要通用指導時沒有過時的參考（如僅限 CLAUDE 的代理特定名稱）。
   - 讀取任何執行階段指導文件（例如，`README.md`、`docs/quickstart.md`，或代理特定指導檔案如存在）。更新已變更原則的參考。

5. 產生同步影響報告（在更新後作為 HTML 註解前置於憲法檔案頂部）：
   - 版本變更：舊 → 新
   - 修改的原則清單（如重新命名：舊標題 → 新標題）
   - 新增的區塊
   - 移除的區塊
   - 需要更新的模板（✅ 已更新 / ⚠ 待處理）及檔案路徑
   - 後續 TODO（如有任何佔位符故意延後）。

6. 最終輸出前的驗證：
   - 沒有剩餘的未解釋括號標記。
   - 版本行與報告相符。
   - 日期為 ISO 格式 YYYY-MM-DD。
   - 原則是聲明式、可測試的，且沒有模糊語言（「should」→ 在適當處用 MUST/SHOULD 理由取代）。

7. 將完成的憲法寫回 `.specify/memory/constitution.md`（覆寫）。

8. 輸出最終摘要給使用者：
   - 新版本和升級理由。
   - 任何標記為需手動後續處理的檔案。
   - 建議的提交訊息（例如，`docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式與風格需求：

- 使用與模板完全相同的 Markdown 標題（不要降級/升級層級）。
- 包裝長理由行以保持可讀性（理想 <100 字元），但不要用尷尬的斷行強制執行。
- 區塊之間保持單一空白行。
- 避免結尾空白。

如果使用者提供部分更新（例如，僅一個原則修訂），仍然執行驗證和版本決策步驟。

如果缺少關鍵資訊（例如，批准日期確實未知），插入 `TODO(<FIELD_NAME>): explanation` 並在同步影響報告的延後項目下包含。

不要建立新模板；始終操作現有的 `.specify/memory/constitution.md` 檔案。
