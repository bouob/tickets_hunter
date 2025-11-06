---
description: 透過互動模式 (Interactive mode) 或提供的原則輸入，建立或更新專案憲章，並確保所有相依的模板保持同步。
---

## 用戶輸入

```text
$ARGUMENTS
```

你在繼續操作前，**必須**考慮用戶輸入（如非空）。

## 大綱

你正在更新位於 `/memory/constitution.md` 的專案憲章（project constitution）。此檔案為一份模板（TEMPLATE），內含以方括號標示的占位符（placeholder token），例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`。你的工作是：(a) 收集或推導具體值，(b) 精確填入模板，(c) 將任何修訂同步至相依的產物。

請依照以下執行流程（Execution Flow）操作：

1. 載入現有的專案憲章模板（constitution template），路徑為 `/memory/constitution.md`。
   - 辨識所有形式為 `[ALL_CAPS_IDENTIFIER]` 的占位符（placeholder token）。
   **重要**：用戶可能要求的原則（principle）數量與模板不同，若有指定數量，請尊重該需求，並依據通用模板進行。你將相應地更新文件。

2. 收集／推導占位符的具體值：
   - 若用戶輸入（對話）已提供值，請直接採用。
   - 否則，從現有 repository 上下文（如 README、文件、嵌入的先前憲章版本）推導。
   - 關於治理日期（governance dates）：`RATIFICATION_DATE` 為最初通過日期（original adoption date），如未知請詢問或標記 TODO；`LAST_AMENDED_DATE` 若有變更則為今日，否則維持原值。
   - `CONSTITUTION_VERSION` 必須依語意化版本控制（Semantic Versioning）規則遞增：
     * MAJOR：治理或原則有不相容的移除或重新定義。
     * MINOR：新增原則／章節，或大幅擴充指引。
     * PATCH：釐清、措辭、錯字修正、非語意性微調。
   - 若版本遞增類型有歧義，請先提出推論理由再定案。

3. 草擬更新後的專案憲章內容：
   - 用具體文字取代所有占位符（不應剩下任何方括號 token，除非專案明確選擇保留的模板欄位—請明確說明保留原因）。
   - 保留標題階層，註解在被取代後可移除，除非仍具釐清作用。
   - 確保每個原則（Principle）章節：有簡明名稱、段落（或條列）描述不可協商的規則，如理由不明顯需明確說明。
   - 確保治理章節（Governance）：列出修訂程序、版本政策、合規審查預期。

4. 一致性同步檢查清單（將先前檢查清單轉為主動驗證）：
   - 閱讀 `/templates/plan-template.md`，確保所有「專案憲章檢查（Constitution Check）」或規則與更新後原則一致。
   - 閱讀 `/templates/spec-template.md`，檢查範疇／需求一致性—若憲章增減強制章節或限制，請同步更新。
   - 閱讀 `/templates/tasks-template.md`，確保任務分類反映新增或移除的原則驅動任務類型（如 observability、versioning、testing discipline）。
   - 閱讀 `/templates/commands/*.md` 下每個指令檔（包括本檔案），確認無過時引用（如僅限 agent 專屬名稱 CLAUDE，需改為通用指引）。
   - 閱讀所有執行時指引文件（如 `README.md`、`docs/quickstart.md`，或 agent 專屬指引檔），同步更新原則相關引用。

5. 產出同步影響報告（Sync Impact Report）：（更新後於憲章檔案頂部以 HTML 註解形式加入）
   - 版本變更：舊版 → 新版
   - 修改的原則清單（如有更名：舊標題 → 新標題）
   - 新增章節
   - 移除章節
   - 需同步更新的模板（✅ 已更新 / ⚠ 待處理），附檔案路徑
   - 若有占位符刻意延後處理，列入後續 TODO

6. 輸出前驗證：
   - 不得有未解釋的方括號 token。
   - 版本行需與報告一致。
   - 日期皆採用 ISO 格式 YYYY-MM-DD。
   - 原則必須具宣告性、可測試，且避免模糊語言（如 "should" → 視情況改為 MUST/SHOULD 並附理由）。

7. 將完成的憲章覆寫寫回 `/memory/constitution.md`。

8. 向用戶輸出最終摘要，內容包含：
   - 新版本號與遞增理由
   - 任何需人工後續處理的檔案
   - 建議的 commit message（如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）

格式與風格要求：
- Markdown 標題需與模板完全一致（不得升降階）。
- 長理由行請適度換行以保可讀性（理想 <100 字），但勿為換行而破壞語意。
- 各章節間僅保留一個空白行。
- 不得有行尾多餘空白。

若用戶僅提供部分更新（如僅修訂一條原則），仍需執行驗證與版本決策步驟。

如有關鍵資訊缺失（如通過日期確實未知），請插入 `TODO(<FIELD_NAME>): explanation`，並於同步影響報告的延後項目中列出。

請勿建立新模板；僅操作現有 `/memory/constitution.md` 檔案。

