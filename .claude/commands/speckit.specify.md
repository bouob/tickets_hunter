---
description: 根據自然語言的功能描述，建立或更新功能規格說明。
model: sonnet
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## 用戶輸入

```text
$ARGUMENTS
```

你在繼續執行前，**必須**考慮用戶輸入（若非空）。

## 大綱

用戶在觸發訊息中的 `/speckit.specify` 之後所輸入的文字**即為**功能描述。請假設在本次對話中你始終可以取得該功能描述，即使下方出現了 `{ARGS}` 也一樣。除非用戶輸入的指令為空，否則不要要求用戶重複輸入。

根據該功能描述，請依下列步驟執行：

1. **產生一個簡潔的短名稱**（2-4 個單字）作為分支名稱：
   - 分析功能描述，萃取最具意義的關鍵字
   - 建立一個能夠掌握功能核心的 2-4 字短名稱
   - 儘可能使用「動作-名詞」格式（例如："add-user-auth"、"fix-payment-bug"）
   - 保留技術術語與縮寫（如 OAuth2、API、JWT 等）
   - 保持簡潔，但要足夠具描述性，讓人一眼能理解功能內容
   - 範例：
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. 從 repo 根目錄執行 `{SCRIPT}` 腳本，**並帶入短名稱參數**，解析其 JSON 輸出以取得 BRANCH_NAME 與 SPEC_FILE。所有檔案路徑皆須為絕對路徑。

   **重要事項**：

   - 將你在步驟 1 產生的短名稱參數附加到 `{SCRIPT}` 指令後
   - Bash：`--short-name "your-generated-short-name"`
   - PowerShell：`-ShortName "your-generated-short-name"`
   - 若參數中有單引號（如 "I'm Groot"），請使用跳脫語法：例如 'I'\''m Groot'（或若可行則用雙引號："I'm Groot"）
   - 你只能執行此腳本一次
   - JSON 會作為終端機輸出提供——請務必參考該輸出以取得你所需的實際內容

3. 載入 `templates/spec-template.md` 以了解所需章節。

4. 遵循以下執行流程：

    1. 從輸入中解析用戶描述  
       若為空：錯誤 "No feature description provided"
    2. 從描述中萃取關鍵概念  
       辨識：參與者（actors）、動作（actions）、資料（data）、限制條件（constraints）
    3. 對於不明確之處：
       - 根據上下文與業界標準做出合理推測
       - 僅在下列情況標記 [NEEDS CLARIFICATION: 具體問題]：
         - 此選擇會顯著影響功能範圍或用戶體驗
         - 存在多種合理解讀且影響不同
         - 無合理預設值可用
       - **限制：最多僅可有 3 個 [NEEDS CLARIFICATION] 標記**
       - 依影響程度排序釐清事項：範圍 > 安全/隱私 > 用戶體驗 > 技術細節
    4. 填寫 User Scenarios & Testing 章節  
       若無明確用戶流程：錯誤 "Cannot determine user scenarios"
    5. 產生功能性需求（Functional Requirements）  
       每項需求皆須可測試  
       對於未明確說明之細節，請採用合理預設值（並於 Assumptions 章節記錄假設）
    6. 定義成功標準（Success Criteria）  
       建立可衡量、與技術無關的成果  
       同時包含量化指標（時間、效能、數量）與質化指標（用戶滿意度、任務完成度）  
       每項標準皆須可在不依賴實作細節下驗證
    7. 辨識主要實體（Key Entities，若涉及資料）
    8. 回傳：SUCCESS（spec 已可進行規劃）

5. 使用模板結構將規格內容寫入 SPEC_FILE，將各段落的占位符替換為根據功能描述（參數）推導出的具體內容，同時保留章節順序與標題。

6. **規格品質驗證**：撰寫初版規格後，請依下列品質標準進行驗證：

   a. **建立規格品質檢查清單**：於 `FEATURE_DIR/checklists/requirements.md` 依檢查清單模板結構產生一份檢查清單檔案，內容包含以下驗證項目：
   
      ```markdown
      # 規格品質檢查清單：[功能名稱]

      **目的**：在進入規劃階段前驗證規格的完整性與品質
      **建立日期**：[日期]
      **功能**：[連結至 spec.md]

      ## 內容品質

      - [ ] 無實作細節（語言、框架、APIs）
      - [ ] 專注於使用者價值與業務需求
      - [ ] 以非技術利害關係人為對象撰寫
      - [ ] 所有必填章節已完成

      ## 需求完整性

      - [ ] 無任何 [NEEDS CLARIFICATION] 標記殘留
      - [ ] 需求可測試且明確無歧義
      - [ ] 成功標準可量測
      - [ ] 成功標準與技術無關（無實作細節）
      - [ ] 所有驗收情境已定義
      - [ ] 邊界情境已識別
      - [ ] 範圍明確界定
      - [ ] 相依性與假設已識別

      ## 功能就緒度

      - [ ] 所有功能需求都有明確的驗收標準
      - [ ] 使用者情境涵蓋主要流程
      - [ ] 功能符合成功標準中定義的可量測成果
      - [ ] 無實作細節洩漏至規格中

      ## 備註

      - 標記為未完成的項目需要在執行 `/speckit.clarify` 或 `/speckit.plan` 前更新規格
      ```
   
   b. **執行驗證檢查（Run Validation Check）**：根據每一項檢查清單（checklist）條目審查規格（spec）：
      - 對每一項目，判斷其是否通過或未通過
      - 紀錄發現的具體問題（引用相關規格說明段落）
   
   c. **處理驗證結果（Handle Validation Results）**：
      
      - **若所有項目皆通過**：標記檢查清單為完成，並進入步驟 6
      
      - **若有項目未通過（不含 [NEEDS CLARIFICATION] 標記）**：
        1. 列出未通過的項目及具體問題
        2. 更新規格以解決每一項問題
        3. 重新執行驗證，直到所有項目通過（最多 3 次循環）
        4. 若 3 次循環後仍有未通過項目，請於檢查清單備註中紀錄剩餘問題，並提醒用戶
      
      - **若仍有 [NEEDS CLARIFICATION] 標記存在**：
        1. 從規格中擷取所有 `[NEEDS CLARIFICATION: ...]` 標記
        2. **數量限制檢查（LIMIT CHECK）**：若標記超過 3 個，僅保留 3 個最關鍵者（依範圍／安全性／使用者體驗影響排序），其餘部分請根據合理推測補足
        3. 對於每一個需釐清事項（最多 3 個），以以下格式向用戶呈現選項：
        
           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
           ```
        
        4. **重要 - 表格格式化**：請確保 Markdown 表格格式正確：
           - 使用一致的間距，並對齊豎線（pipes）
           - 每個儲存格內容前後都要有空格：`| Content |` 而不是 `|Content|`
           - 標題分隔線必須至少有 3 個破折號：`|--------|`
           - 測試表格在 Markdown 預覽中能正確顯示
        5. 問題請依序編號（Q1、Q2、Q3，最多 3 題）
        6. 所有問題請一次性全部呈現，然後再等待回覆
        7. 等待使用者針對所有問題回覆其選擇（例如："Q1: A, Q2: Custom - [details], Q3: B"）
        8. 依據使用者選擇或提供的答案，將每個 [NEEDS CLARIFICATION] 標記替換掉
        9. 所有釐清事項解決後，請重新執行驗證

   d. **更新檢查清單**：每次驗證迭代後，請將目前的通過/未通過狀態更新至檢查清單檔案

7. 回報完成情況，包含分支名稱、規格檔案路徑、檢查清單結果，以及是否已準備好進入下一階段（`/speckit.clarify` 或 `/speckit.plan`）。

**注意：** 腳本會自動建立並切換到新分支，並在寫入前初始化規格檔案。

## 一般指引

## 快速指引

- 著重於使用者**需要什麼（WHAT）**以及**為什麼（WHY）**。
- 避免描述如何實作（不涉及技術堆疊、API、程式碼結構）。
- 內容是寫給業務相關人員，而非開發者。
- 請勿在規格內嵌入任何檢查清單。檢查清單將由其他指令產生。

### 各區塊要求

- **必要區塊**：每個功能都必須完成
- **選用區塊**：僅在與功能相關時納入
- 若某區塊不適用，請直接刪除（不要留 "N/A"）

### 給 AI 產生時的指引

當根據用戶提示建立此規格時：

1. **做出合理推測**：運用上下文、產業標準及常見模式來填補資訊空白
2. **記錄假設**：將合理預設記錄於 Assumptions（假設）區塊
3. **限制釐清事項**：最多僅能有 3 個 [NEEDS CLARIFICATION] 標記——僅用於以下關鍵決策：
   - 會顯著影響功能範圍或使用者體驗
   - 存在多種合理解釋且影響不同
   - 無法推論出合理預設值
4. **釐清事項優先順序**：功能範圍 > 資安/隱私 > 使用者體驗 > 技術細節
5. **以測試者角度思考**：每個模糊的需求都應該無法通過「可測試且明確」的檢查清單項目
6. **常見需釐清的區域**（僅在無合理預設時）：
   - 功能範圍與邊界（包含/排除哪些使用情境）
   - 使用者類型與權限（若有多種合理但互斥的解釋）
   - 資安/合規需求（若具法律或財務重大意義）

**合理預設範例**（遇到這些請勿再詢問）：

- 資料保留：依該領域產業標準
- 效能目標：除非特別說明，採用標準 Web/行動應用預期
- 錯誤處理：以對使用者友善並有適當備援為原則
- 驗證方式：Web 應用預設為 session-based 或 OAuth2
- 整合模式：除非特別說明，預設為 RESTful API

### 成功標準指引

成功標準必須：

1. **可衡量**：包含明確指標（時間、百分比、數量、比率）
2. **與技術無關**：不得提及框架、語言、資料庫或工具
3. **以使用者為中心**：以使用者/業務成果為主，不描述系統內部運作
4. **可驗證**：無需了解實作細節即可測試/驗證

**良好範例**：

- 「使用者可在 3 分鐘內完成結帳」
- 「系統可支援 10,000 名同時使用者」
- 「95% 搜尋在 1 秒內回傳結果」
- 「任務完成率提升 40%」

**不良範例**（過於實作導向）：

- 「API 回應時間低於 200ms」（太技術性，請改為「使用者能即時看到結果」）
- 「資料庫可處理 1000 TPS」（屬於實作細節，請改用面向使用者的指標）
- 「React 元件渲染效率高」（特定框架）
- 「Redis 快取命中率超過 80%」（特定技術）

