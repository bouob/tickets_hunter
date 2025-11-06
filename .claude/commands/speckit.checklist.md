---
description: 根據用戶需求，為當前功能產生自訂檢查清單。
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 檢查清單用途：「英文需求的單元測試」

**關鍵概念**：檢查清單是**需求撰寫的單元測試**——它們用來驗證在特定領域中，需求的品質、清晰度與完整性。

**不是用於驗證/測試**：
- ❌ 不是「驗證按鈕點擊是否正確」
- ❌ 不是「測試錯誤處理是否有效」
- ❌ 不是「確認 API 回傳 200」
- ❌ 不是檢查程式碼/實作是否符合規格

**用於需求品質驗證**：
- ✅「所有卡片類型是否都有定義視覺階層需求？」（完整性）
- ✅「『醒目顯示』是否以具體尺寸/位置量化？」（清晰度）
- ✅「所有互動元件的 hover 狀態需求是否一致？」（一致性）
- ✅「是否有定義鍵盤導覽的無障礙需求？」（覆蓋範圍）
- ✅「規格是否定義 logo 圖片載入失敗時的處理方式？」（邊界情境）

**比喻**：如果你的規格說明是用英文寫的程式碼，檢查清單就是它的單元測試套件。你是在測試需求是否撰寫良好、完整、無歧義且可供實作——而不是測試實作本身是否可行。

## 用戶輸入

```text
$ARGUMENTS
```

你在執行前**必須**考慮用戶輸入（若非空）。

## 執行步驟

1. **初始化**：於 repo 根目錄執行 `{SCRIPT}`，並解析 JSON 以取得 FEATURE_DIR 與 AVAILABLE_DOCS 清單。
   - 所有檔案路徑必須為絕對路徑。
   - 若參數中有單引號（如 "I'm Groot"），請使用跳脫語法：例如 `'I'\''m Groot'`（或若可行則用雙引號："I'm Groot"）。

2. **釐清意圖（動態）**：動態產生最多三個初步情境釐清問題（不得使用預設問題庫）。這些問題**必須**：
   - 根據用戶表述及從規格/計劃/任務中萃取的訊號動態生成
   - 僅詢問會實質影響檢查清單內容的資訊
   - 若在 `$ARGUMENTS` 已明確，則可個別跳過
   - 以精確為優先，不追求廣度

   生成演算法：
   1. 萃取訊號：功能領域關鍵字（如 auth、latency、UX、API）、風險指標（如 "critical"、"must"、"compliance"）、利害關係人提示（如 "QA"、"review"、"security team"）、明確交付物（如 "a11y"、"rollback"、"contracts"）。
   2. 將訊號聚類為最多 4 個候選重點領域，按相關性排序。
   3. 若未明確，判斷可能的目標對象與時機（作者、審查者、QA、發佈）。
   4. 偵測缺失面向：範圍廣度、深度/嚴謹度、風險重點、排除邊界、可衡量的驗收標準。
   5. 依下列典型問題類型擇一組成問題：
      - 範圍細化（例："此需求是否應涵蓋與 X、Y 的整合 touchpoint，或僅限於本地模組正確性？"）
      - 風險優先排序（例："這些潛在風險領域中，哪些需要強制設置 gating 檢查？"）
      - 深度校準（例："這是一份輕量 pre-commit sanity list，還是正式 release gate？"）
      - 目標對象定位（例："這份檢查清單僅作者自用，還是 PR review 時同儕共用？"）
      - 邊界排除（例："本輪是否需明確排除效能調校項目？"）
      - 情境類型缺口（例："未偵測到復原流程——rollback/部分失敗路徑是否在範圍內？"）

   問題格式規則：
   - 若有選項，請產生簡潔表格，欄位為：Option | Candidate | Why It Matters
   - 最多僅列 A–E 五個選項；若自由回答更清楚則省略表格
   - 絕不要求用戶重述已說明內容
   - 避免臆測分類（不得幻想）。若不確定，請明確詢問："請確認 X 是否屬於範圍內。"

   若無法互動時的預設值：
   - 深度：標準
   - 目標對象：若與程式碼相關則為 Reviewer (PR)；否則為作者
   - 重點：前兩個最相關領域

   輸出問題時請標註 Q1/Q2/Q3。回答後，若仍有兩個以上情境類型（Alternate / Exception / Recovery / Non-Functional domain）不明確，可再追問最多兩個精準後續問題（Q4/Q5），每題附一句理由（如："復原路徑風險未解決"）。總問題數不得超過五題。若用戶明確拒絕追問，則不得升級追問。

3. **理解用戶需求**：結合 `$ARGUMENTS` 與釐清問題的答案：
   - 推導檢查清單主題（如 security、review、deploy、ux）
   - 彙整用戶明確指定的 must-have 項目
   - 將重點選擇對應到分類架構
   - 從規格/計劃/任務中推斷缺失上下文（**不得幻想**）

4. **載入功能上下文**：自 FEATURE_DIR 讀取：
   - spec.md：功能需求與範圍
   - plan.md（如有）：技術細節、相依性
   - tasks.md（如有）：實作任務

   **上下文載入策略**：
   - 僅載入與當前重點領域相關的必要部分（避免整檔貼出）
   - 長段落優先摘要為精簡情境/需求條列
   - 採用漸進式揭露：僅在偵測到缺口時再補充檢索
   - 若原始文件龐大，請產生中繼摘要條目，勿直接嵌入原文

5. **產生檢查清單** - 建立「需求單元測試」：
   - 若 `FEATURE_DIR/checklists/` 目錄不存在，請建立
   - 產生唯一檢查清單檔名：
     - 以領域為基礎，使用簡短描述性名稱（如 `ux.md`、`api.md`、`security.md`）
     - 格式：`[domain].md` 
     - 若檔案已存在，則附加於現有檔案
   - 條目編號自 CHK001 依序遞增
   - 每次 `/speckit.checklist` 執行皆建立新檔案（**絕不覆蓋**現有檢查清單）

   **核心原則 - 測試需求本身，不測試實作**：
   每一檢查清單條目**必須**檢驗「需求本身」是否具備：
   - **完整性**：所有必要需求是否齊全？
   - **明確性**：需求是否無歧義且具體？
   - **一致性**：需求間是否相互對齊？
   - **可衡量性**：需求是否可客觀驗證？
   - **覆蓋性**：所有情境/邊界案例是否涵蓋？

   **分類結構** - 依需求品質面向分組條目：
   - **需求完整性**（所有必要需求是否有文件記載？）
   - **需求明確性**（需求是否具體明確、無歧義？）
   - **需求一致性**（需求間是否無衝突？）
   - **驗收標準品質**（成功標準是否可衡量？）
   - **情境覆蓋性**（所有流程/案例是否涵蓋？）
   - **邊界案例覆蓋性**（邊界條件是否有定義？）
   - **非功能性需求**（效能、安全、無障礙等是否有明確規範？）
   - **相依性與假設**（是否有文件記載並驗證？）
   - **歧義與衝突**（哪些地方需要釐清？）

   **如何撰寫檢查清單條目 -「英文單元測試」**：

   ❌ **錯誤範例**（測試實作）：
   - "Verify landing page displays 3 episode cards"
   - "Test hover states work on desktop"
   - "Confirm logo click navigates home"

   ✅ **正確範例**（測試需求品質）：
   - "Are the exact number and layout of featured episodes specified?" [Completeness]
   - "Is 'prominent display' quantified with specific sizing/positioning?" [Clarity]
   - "Are hover state requirements consistent across all interactive elements?" [Consistency]
   - "Are keyboard navigation requirements defined for all interactive UI?" [Coverage]
   - "Is the fallback behavior specified when logo image fails to load?" [Edge Cases]
   - "Are loading states defined for asynchronous episode data?" [Completeness]
   - "Does the spec define visual hierarchy for competing UI elements?" [Clarity]

   **條目結構**：
   每一條目應遵循以下格式：
   - 以問題形式檢查需求品質
   - 聚焦於規格/計劃**已寫**（或未寫）內容
   - 於括號內標註品質面向 [Completeness/Clarity/Consistency/…]
   - 檢查現有需求時引用規格章節 `[Spec §X.Y]`
   - 檢查缺漏需求時使用 `[Gap]` 標記

   **各品質面向範例**：

   完整性：
   - "Are error handling requirements defined for all API failure modes? [Gap]"
   - "Are accessibility requirements specified for all interactive elements? [Completeness]"
   - "Are mobile breakpoint requirements defined for responsive layouts? [Gap]"

   明確性：
   - "Is 'fast loading' quantified with specific timing thresholds? [Clarity, Spec §NFR-2]"
   - "Are 'related episodes' selection criteria explicitly defined? [Clarity, Spec §FR-5]"
   - "Is 'prominent' defined with measurable visual properties? [Ambiguity, Spec §FR-4]"

   一致性：
   - "Do navigation requirements align across all pages? [Consistency, Spec §FR-10]"
   - "Are card component requirements consistent between landing and detail pages? [Consistency]"

   覆蓋性：
   - "Are requirements defined for zero-state scenarios (no episodes)? [Coverage, Edge Case]"
   - "Are concurrent user interaction scenarios addressed? [Coverage, Gap]"
   - "Are requirements specified for partial data loading failures? [Coverage, Exception Flow]"

   可衡量性：
   - "Are visual hierarchy requirements measurable/testable? [Acceptance Criteria, Spec §FR-1]"
   - "Can 'balanced visual weight' be objectively verified? [Measurability, Spec §FR-2]"

   **情境分類與覆蓋性**（聚焦於需求品質）：
   - 檢查是否有主流程、替代流程、例外/錯誤流程、復原流程、非功能性情境的需求
   - 每個情境類型皆應詢問：「[情境類型] 需求是否完整、明確且一致？」
   - 若缺少該情境類型：「[情境類型] 需求是有意排除還是遺漏？[Gap]」
   - 若有狀態變動，請納入韌性/rollback：「遷移失敗時 rollback 需求是否有定義？[Gap]」

   **可追溯性需求**：
   - 最低要求：80% 以上條目**必須**包含至少一個可追溯性引用
   - 每條目應引用：規格章節 `[Spec §X.Y]`，或使用標記：`[Gap]`、`[Ambiguity]`、`[Conflict]`、`[Assumption]`
   - 若無 ID 系統：「是否已建立需求與驗收標準的 ID 編碼方案？[Traceability]」

   **揭露並解決問題**（需求品質問題）：
   針對需求本身提出問題：
   - 歧義：「'fast' 一詞是否有具體量化指標？[Ambiguity, Spec §NFR-1]」
   - 衝突：「§FR-10 與 §FR-10a 的導覽需求是否衝突？[Conflict]」
   - 假設：「'podcast API 永遠可用' 這一假設是否已驗證？[Assumption]」
   - 相依性：「外部 podcast API 需求是否有文件記載？[Dependency, Gap]」
   - 定義缺漏：「'visual hierarchy' 是否有可衡量的定義？[Gap]」

   **內容整併**：
   - 軟性上限：若原始候選條目超過 40 條，請依風險/影響力優先排序
   - 合併重複或近似條目（檢查同一需求面向）
   - 若低影響邊界案例超過 5 條，請合併為一條：「需求是否涵蓋邊界案例 X、Y、Z？[Coverage]」

   **🚫 絕對禁止** - 下列寫法會變成實作測試而非需求測試：
   - ❌ 任何以 "Verify"、"Test"、"Confirm"、"Check" + 實作行為開頭的條目
   - ❌ 涉及程式碼執行、用戶操作、系統行為的描述
   - ❌ "Displays correctly"、"works properly"、"functions as expected"
   - ❌ "Click"、"navigate"、"render"、"load"、"execute"
   - ❌ 測試案例、測試計畫、QA 流程
   - ❌ 實作細節（frameworks、API、演算法）

   **✅ 必須遵循的寫法** - 這些才是測試需求品質：
   - ✅ "Are [需求類型] defined/specified/documented for [情境]?"
   - ✅ "Is [模糊詞] quantified/clarified with specific criteria?"
   - ✅ "Are requirements consistent between [A 節] and [B 節]?"
   - ✅ "Can [需求] be objectively measured/verified?"
   - ✅ "Are [邊界案例/情境] addressed in requirements?"
   - ✅ "Does the spec define [缺漏面向]?"

6. **結構參考**：依照 `templates/checklist-template.md` 之標準模板產生檢查清單，包含標題、meta 區、分類標題及 ID 格式。若模板不可用，請使用：H1 標題、用途/建立者 meta 行、`##` 分類區塊，內容為 `- [ ] CHK### <requirement item>` 條目，ID 全域遞增自 CHK001 起。

7. **報告**：輸出建立之檢查清單完整路徑、條目數，並提醒用戶每次執行皆會產生新檔案。摘要說明：
   - 選定重點領域
   - 深度層級
   - 角色/時機
   - 已納入的用戶明確指定 must-have 項目

**重要**：每次 `/speckit.checklist` 指令執行都會以簡短描述性名稱建立檢查清單檔案，除非檔案已存在。這樣可：

- 產生多種不同類型檢查清單（如 `ux.md`、`test.md`、`security.md`）
- 檔名簡潔易記，明確標示檢查清單用途
- 於 `checklists/` 資料夾中方便識別與瀏覽

為避免雜亂，請使用描述性類型，並於完成後清理過時檢查清單。

## 檢查清單類型與範例條目

**UX 需求品質檢查清單：** `ux.md`

範例條目（測試需求本身，**非**實作）：
- "Are visual hierarchy requirements defined with measurable criteria? [Clarity, Spec §FR-1]"
- "Is the number and positioning of UI elements explicitly specified? [Completeness, Spec §FR-1]"
- "Are interaction state requirements (hover, focus, active) consistently defined? [Consistency]"
- "Are accessibility requirements specified for all interactive elements? [Coverage, Gap]"
- "Is fallback behavior defined when images fail to load? [Edge Case, Gap]"
- "Can 'prominent display' be objectively measured? [Measurability, Spec §FR-4]"

**API 需求品質檢查清單：** `api.md`

範例條目：
- "Are error response formats specified for all failure scenarios? [Completeness]"
- "Are rate limiting requirements quantified with specific thresholds? [Clarity]"
- "Are authentication requirements consistent across all endpoints? [Consistency]"
- "Are retry/timeout requirements defined for external dependencies? [Coverage, Gap]"
- "Is versioning strategy documented in requirements? [Gap]"

**效能需求品質檢查清單：** `performance.md`

範例條目：
- "Are performance requirements quantified with specific metrics? [Clarity]"
- "Are performance targets defined for all critical user journeys?

```markdown
- [ ] CHK001 - Verify landing page displays 3 episode cards [Spec §FR-001]
- [ ] CHK002 - Test hover states work correctly on desktop [Spec §FR-003]
- [ ] CHK003 - Confirm logo click navigates to home page [Spec §FR-010]
- [ ] CHK004 - Check that related episodes section shows 3-5 items [Spec §FR-005]
```

**✅ 正確 - 這些測試需求品質良好：**

```markdown
- [ ] CHK001 - Are the number and layout of featured episodes explicitly specified? [Completeness, Spec §FR-001]
- [ ] CHK002 - Are hover state requirements consistently defined for all interactive elements? [Consistency, Spec §FR-003]
- [ ] CHK003 - Are navigation requirements clear for all clickable brand elements? [Clarity, Spec §FR-010]
- [ ] CHK004 - Is the selection criteria for related episodes documented? [Gap, Spec §FR-005]
- [ ] CHK005 - Are loading state requirements defined for asynchronous episode data? [Gap]
- [ ] CHK006 - Can "visual hierarchy" requirements be objectively measured? [Measurability, Spec §FR-001]
```

**主要差異：**
- 錯誤：測試系統是否正確運作
- 正確：測試需求是否正確撰寫
- 錯誤：行為驗證
- 正確：需求品質驗證
- 錯誤：「它有做 X 嗎？」
- 正確：「X 是否被明確規範？」

