---
description: "分析開啟狀態的 GitHub issues，整理相似問題並提供處理建議"
model: sonnet
allowed-tools: ["Bash", "Task"]
---

# Review GitHub Issues 指令

請分析當前專案（Tickets Hunter）的 GitHub issues，整理相似問題並提供處理建議。

## 執行流程

### 階段 0：提早終止檢查（快速過濾）

在開始分析前，快速過濾明顯無需分析的 issues：

**跳過分析的條件**：
- 已有 `duplicate` 標籤
- 已有 `wontfix` 標籤
- 已有「此問題與 #xxx 重複」的 bot 留言（包含 `Claude Code` 簽名）
- 標題包含 `[Resolved]` 或 `[Fixed]`

**實作方式**：
```bash
gh issue list --state open --limit 100 --json number,title,labels,comments
```

對每個 issue 檢查：
1. `labels` 欄位是否包含 `duplicate` 或 `wontfix`
2. `title` 是否包含 `[Resolved]` 或 `[Fixed]`
3. `comments` 是否包含 bot 留言（檢查是否有「Claude Code」簽名且內容含「重複」）

若符合任一條件，記錄到「已跳過」清單，不進行後續分析。

---

### 階段 1：抓取並檢查開啟狀態的 issues

1. **抓取 open issues**
   ```bash
   gh issue list --state open --limit 100 --json number,title,body,labels,createdAt,updatedAt,author,url
   ```

2. **對每個 issue 檢查評論**
   ```bash
   gh issue view <issue_number> --json comments
   ```

   搜尋關鍵詞：
   - 已解決：「已經修好」、「更新後沒問題」、「已解決」、「修好」、「沒問題」
   - 已修復：「新版本已修復」、「已在 X 版本修正」、「已修復」
   - 無法重現：「無法重現」、「不知道怎麼重現」、「無法復現」

3. **評論檢查優化**
   - 優先檢查原 issue 提交者的最新評論
   - 若評論過多（>10 條），僅檢查最新 5 條 + 原提交者評論
   - 標註解決日期（若評論中有提及）

---

### 階段 2：抓取已關閉但有新回覆的 issues（新增）

**目的**：追蹤關閉後使用者又回覆的 issues，避免遺漏

1. **抓取 closed issues**
   ```bash
   gh issue list --state closed --limit 100 --json number,title,body,labels,closedAt,updatedAt,author,url,comments
   ```

2. **檢查關閉後是否有新回覆**

   判斷邏輯：
   - `updatedAt > closedAt`（更新時間晚於關閉時間）
   - 最後一條評論不是 bot 留言（不包含「Claude Code」簽名）
   - 最後一條評論是原 issue 提交者或其他使用者的回覆

3. **記錄需重新開啟的 issues**

   記錄資訊：
   - Issue 編號和標題
   - 關閉時間
   - 最後回覆時間和作者
   - 回覆內容摘要（最後一條評論的前 100 字元）

---

### 階段 3：預先檢查與自動處理

對所有 open issues 進行以下檢查：

1. **空白 issue**：body 為空或僅包含模板文字 → 標註「建議關閉」
2. **標題不明確**：標題包含 `<請描述問題>`、`<請描述功能需求>` 等 → **自動修正標題**
3. **資訊不足**：Bug report 缺少必要欄位 → 標註「資訊不足」
4. **重複問題**：相同平台、相同錯誤或高度相似 → **自動關閉並引用原 issue**
5. **已解決問題**：評論中有使用者確認已解決 → 標註「已回報解決」
6. **已修復問題**：CHANGELOG.md 或評論中已記錄修正 → 標註「已修復」

---

### 階段 4：自動標題修正（新增）

**觸發條件**：
- 標題包含 `<請描述問題>`、`<請描述功能需求>` 或其他模板預設值
- 且 body 內容完整（不是空白或僅模板）

**執行步驟**：

1. **使用 Task agent 生成新標題**

   Agent 任務：
   - 分析 issue body
   - 提取平台名稱（TixCraft、KKTIX、iBon、TicketPlus、KHAM、FamiTicket 等）
   - 提取問題類型（登入、驗證碼、日期選擇、區域選擇、自動暫停等）
   - 提取關鍵錯誤或需求描述

   生成格式：
   ```
   [平台] 簡短問題描述
   ```

   範例：
   - `[TixCraft] NoDriver 自動刷新無效`
   - `[KKTIX] 登入後立即自動暫停`
   - `[iBon] SID Cookie 無法登入`
   - `[功能請求] 支援 FamiTicket 平台`

   限制：
   - 標題最多 60 字元
   - 簡潔明確，避免冗詞

2. **自動修改標題**
   ```bash
   gh issue edit <issue_number> --title "新標題"
   ```

3. **不通知使用者**
   - 按使用者需求，修改標題後**不**在 issue 中留言

4. **記錄到報告**
   - 在「已自動處理」區塊列出修改的標題
   - 格式：`#123: "[舊標題]" → "[新標題]"`

---

### 階段 5：重複 issue 自動處理（新增）

**參考 `/dedupe` 指令的實作方式**

**執行步驟**：

1. **提取平台關鍵字**（借鏡 `/dedupe`）

   定義 5 大平台的搜尋關鍵字：

   | 平台 | 搜尋關鍵字 |
   |------|-----------|
   | **TixCraft** | `"TixCraft"`, `"拓元"`, `"SID"`, `"Google 登入"`, `"驗證碼"` |
   | **KKTIX** | `"KKTIX"`, `"崩潰"`, `"crash"`, `"場次選擇"`, `"驗證問題"` |
   | **iBon** | `"iBon"`, `"Shadow DOM"`, `"Angular"`, `"Cookie"`, `"日期選擇"` |
   | **TicketPlus** | `"TicketPlus"`, `"遠大"`, `"關鍵字"`, `"自動遞補"`, `"價位"` |
   | **NoDriver** | `"NoDriver"`, `"CDP"`, `"反偵測"`, `"AttributeError"`, `"to_json"` |

2. **使用 Task agent 搜尋重複 issues**

   Agent 任務（平行執行）：
   - 為每個 issue 提取關鍵字（平台 + 問題類型 + 錯誤訊息片段）
   - 使用 `gh search issues` 搜尋相似 issues
   - 過濾誤報（語義比對，判斷是否真正重複）

   搜尋命令範例：
   ```bash
   gh search issues "TixCraft 登入" --repo bouob/tickets_hunter --state open
   gh search issues "KKTIX 自動暫停" --repo bouob/tickets_hunter --state open
   ```

3. **判斷重複邏輯**

   符合以下條件視為重複：
   - 相同平台
   - 相同問題類型（登入、驗證碼、選擇等）
   - 問題描述高度相似（透過 agent 語義判斷）
   - 其中一個 issue 創建時間較早（作為原 issue）

4. **自動關閉並引用原 issue**

   對於識別為重複的 issues：

   a. **自動判斷使用者語言**（參考 `/dedupe`）
      - 檢查 title 或 body 是否包含中文字元 → 使用繁體中文範本
      - 否則使用英文範本

   b. **留言並關閉**
      ```bash
      gh issue close <duplicate_issue_number> --reason "not planned" --comment "留言內容"
      ```

   **繁體中文範本**：
   ```markdown
   此問題與 #<原issue編號> 重複，已自動關閉。

   請至原 issue 追蹤進度：
   <原issue連結>

   ---
   *Claude Code*
   ```

   **English Template**：
   ```markdown
   This issue is a duplicate of #<original_issue_number> and has been automatically closed.

   Please track progress at the original issue:
   <original_issue_link>

   ---
   *Claude Code*
   ```

5. **記錄到報告**
   - 在「已自動處理 > 自動關閉重複」區塊列出
   - 格式：`#456 (重複 #123) - 問題摘要`

---

### 階段 6：分析與分組

- 根據問題描述和標題，將相似的 issues 分組
- 識別重複或高度相關的問題
- 評估每個問題的影響範圍和嚴重性
- **重點**：只分析 open 狀態的 issues，但在報告中標註已解決的 issues

---

## 輸出格式

### ⚠️ 需重新開啟（已關閉但有新回覆）**← 新增，置頂**

以下 issues 已關閉但使用者有新回覆，建議重新開啟：

1. **#123** - TixCraft 登入問題
   - 關閉時間：2025-11-05
   - 最後回覆：2025-11-07 (作者: user123)
   - 回覆摘要：「問題仍存在，更新後還是無法登入...」
   - 建議：`gh issue reopen 123`

2. **#145** - KKTIX 驗證碼辨識失敗
   - 關閉時間：2025-11-06
   - 最後回覆：2025-11-08 (作者: user456)
   - 回覆摘要：「我補充了完整錯誤訊息...」
   - 建議：`gh issue reopen 145`

**若無此類 issues，則省略此區塊**

---

### 📊 Issues 總覽

- 總數量：X 個 open issues
- 分類統計：Bug (X) | 功能請求 (X) | 其他 (X)
- **待處理**：X 個（排除「已解決」、「已修復」的 issues）
- **已跳過分析**：X 個（已標記為 duplicate/wontfix 或已有處理留言）
- **自動處理**：標題修正 (X) | 重複關閉 (X)

---

### 🔥 高優先度（需立即處理）

#### 分組 1：[相似問題主題]
- **#123** - 問題標題摘要
  - 平台：TixCraft / iBon / KKTIX 等
  - 影響：核心功能 / 輔助功能
  - 狀態：待處理 / 已回報解決 / 已修復
  - 相關 issue：#456, #789
  - 建議：[簡短處理建議]

#### 分組 2：[相似問題主題]
- ...

---

### ⚠️ 中優先度（重要但非緊急）

#### 分組 3：[相似問題主題]
- **#234** - 問題標題摘要
  - 平台：...
  - 影響：...
  - 狀態：...

---

### 💡 低優先度（優化建議）

#### 分組 4：[相似問題主題]
- **#345** - 問題標題摘要

---

### 🔧 已自動處理 **← 新增**

#### 自動修正標題
以下 issues 的標題已自動修正（標題不明確但內容完整）：

1. **#XXX**: `[BUG] <請描述問題>` → `[TixCraft] NoDriver 自動刷新無效`
2. **#YYY**: `[FEATURE] <請描述功能需求>` → `[功能請求] 支援 FamiTicket 平台`

#### 自動關閉重複
以下 issues 已自動關閉為重複問題：

1. **#456** (重複 #123) - TixCraft 登入問題 - 已留言並引用原 issue
2. **#789** (重複 #234) - KKTIX 驗證碼問題 - 已留言並引用原 issue

**若無自動處理項目，則省略此區塊**

---

### ✅ 已解決/已修復的 Issues（無需處理）

- **#XXX** - [問題摘要] - 已回報解決於 [日期]
- **#YYY** - [問題摘要] - 已在版本 [X.Y.Z] 修復

---

### 🔗 重複問題（需手動確認）

以下 issues 可能重複，但需手動確認後再處理：

- #111 與 #222 可能重複 - [問題摘要]
- 建議：人工比對後決定是否合併

**註**：明確重複的 issues 已在「已自動處理」區塊自動關閉

---

### 📋 處理建議順序

1. [分組 X] - [原因]
2. [分組 Y] - [原因]
3. ...

---

## 分析原則

1. **優先度評估標準**
   - 高：影響核心搶票功能、多人回報、資料遺失風險
   - 中：影響特定平台、使用者體驗問題、效能問題
   - 低：文件修正、UI 優化、小型改進建議

2. **相似度判斷**
   - 相同平台的相同類型問題（如多個 iBon OCR 問題）
   - 相同根本原因但不同表現形式
   - 功能請求的重疊部分

3. **分組邏輯**
   - 按平台分組（TixCraft、KKTIX、iBon、TicketPlus 等）
   - 按功能模組分組（登入、驗證碼、日期選擇、區域選擇等）
   - 按問題類型分組（Bug、功能請求、文件、配置）

4. **評論解析**
   - 搜尋關鍵詞：「已解決」「修好」「沒問題」「已修復」「已在 X 版本」「無法重現」「不知道怎麼重現」
   - 優先檢查原 issue 提交者的最新評論
   - 標註解決日期（若評論中有提及）

---

## 特別注意

- **僅分析開啟狀態（open）的 issues**，但在報告中清楚標註已解決的 issues
- **額外檢查已關閉（closed）的 issues**，識別關閉後有新回覆的情況
- 標注哪些問題可能已在最新版本中修復（檢查 CHANGELOG.md）
- 識別需要更多資訊才能處理的 issues
- 提供「快速勝利」的問題（容易修復且影響大）
- **評論檢查**：若評論過多（>10 條），可只檢查最新 5 條評論和原 issue 提交者的評論
- **提早終止**：跳過已明確標記為 duplicate/wontfix 或已有處理留言的 issues
- **自動處理**：
  - 標題不明確但內容完整 → 自動修正標題，不通知
  - 明確重複 → 自動關閉並引用原 issue
- **暫不新增標籤**：按使用者需求，保持手動管理標籤（不自動新增 platform:xxx 或 priority:xxx）

---

## 輸出要求

- 使用繁體中文
- 提供清晰的 issue 編號（如 #123）
- 簡潔的摘要（每個問題 1-2 句話）
- 可操作的建議
- 避免使用 emoji（除了章節標題）
- **提醒**：分析結果包含開啟狀態的 issues，但已解決的 issues 在報告中單獨列出
- **新增**：「需重新開啟」區塊置頂顯示，「已自動處理」區塊在中間位置

---

## 回應範本

**重要原則**：
- **僅在關閉 issue 時才回復**，其他情況不主動發送 comment
- 僅提供繁體中文和英文範本
- 簡潔直入重點，無招呼用語和感謝詞
- 結尾加上 `---\n*Claude Code*` 簽名

### 範本 1：問題已修正（關閉 issue）

**繁體中文**：
```
**此問題已在 [版本號] 修正**

[簡述修正內容]

**請更新並檢查**：
- 確認版本 >= [版本號]
- [具體設定或檢查項目]

若更新後仍有問題，請開啟新 issue 並提供完整錯誤日誌。

---
*Claude Code*
```

**English**：
```
**Fixed in version [version]**

[Brief description of the fix]

**Please update and verify**:
- Ensure version >= [version]
- [Specific configuration items]

If the issue persists, please open a new issue with complete error logs.

---
*Claude Code*
```

---

### 範本 2：空白或資訊不足（關閉 issue）

**繁體中文**：
```
**此 issue 缺少必要資訊（標題不明確或內容為空）**

若需協助，請開啟新 issue 並提供：
1. 清楚的問題描述或功能需求
2. 重現步驟（bug）或使用場景（功能請求）
3. 預期行為 vs 實際行為
4. 基本資訊（OS、Python 版本、平台）

---
*Claude Code*
```

**English**：
```
**This issue lacks necessary information (unclear title or empty content)**

If you need assistance, please open a new issue with:
1. Clear problem description or feature request
2. Steps to reproduce (bug) or use case (feature)
3. Expected vs actual behavior
4. Basic info (OS, Python version, platform)

---
*Claude Code*
```

---

### 範本 3：無法重現且長時間無回應（關閉 issue）

**繁體中文**：
```
**無法在最新版本（[版本號]）重現此問題，且長時間無回應**

若問題仍存在，請開啟新 issue 並提供：
1. 最新版本號
2. 完整錯誤日誌
3. 詳細重現步驟

---
*Claude Code*
```

**English**：
```
**Unable to reproduce in latest version ([version]), and no response for extended period**

If the issue persists, please open a new issue with:
1. Latest version number
2. Complete error logs
3. Detailed reproduction steps

---
*Claude Code*
```

---

### 範本 4：重複問題（自動關閉）**← 新增**

**繁體中文**：
```
此問題與 #[原issue編號] 重複，已自動關閉。

請至原 issue 追蹤進度：
[原issue連結]

---
*Claude Code*
```

**English**：
```
This issue is a duplicate of #[original_issue_number] and has been automatically closed.

Please track progress at the original issue:
[original_issue_link]

---
*Claude Code*
```

---

## 自動處理規則

執行 `/review-issues` 時自動檢查並執行：

### 1. 提早終止（新增）
- **條件**：已有 `duplicate`/`wontfix` 標籤，或已有 bot 處理留言，或標題含 `[Resolved]`/`[Fixed]`
- **動作**：跳過分析，記錄到「已跳過」清單

### 2. 空白 Issue
- **條件**：body 為空或僅包含模板預設文字
- **動作**：在分析報告中標註「建議使用範本 2 關閉」
- **不主動關閉**，等待使用者確認

### 3. 標題不明確（改良）
- **條件**：標題包含 `<請描述問題>`、`<請描述功能需求>` 等，且 body 內容完整
- **動作**：**自動修正標題**（使用 Task agent 生成），**不通知使用者**
- 記錄到「已自動處理 > 自動修正標題」區塊

### 4. 資訊不足
- **條件**：Bug report 缺少錯誤訊息、平台、重現步驟
- **動作**：在分析報告中標註「資訊不足，建議請使用者補充」
- **不主動回應**

### 5. 重複問題（改良）
- **條件**：相同平台、相同錯誤或高度相似描述（透過平台關鍵字搜尋 + agent 語義判斷）
- **動作**：**自動關閉並留言引用原 issue**（使用範本 4）
- 記錄到「已自動處理 > 自動關閉重複」區塊

### 6. 已修正問題
- **條件**：CHANGELOG.md 中已記錄修正或評論中有「已在 X 版本修復」
- **動作**：在分析報告中標註「已在 X 版本修復，建議使用範本 1 關閉」
- **不主動關閉**，等待使用者確認

### 7. 已解決問題
- **條件**：評論中有原 issue 提交者確認「已解決」、「修好」、「沒問題」等
- **動作**：在分析報告中標註「已回報解決於 [日期]」，單獨列在「已解決」區塊
- **不主動關閉**，等待使用者確認

### 8. 無法重現
- **條件**：評論中有「無法重現」、「不知道怎麼重現」等
- **動作**：在分析報告中標註「無法重現」，可考慮使用範本 3 關閉
- **不主動回應**，等待使用者確認

### 9. 關閉後回覆（新增）
- **條件**：issue 已關閉，但 `updatedAt > closedAt` 且最後一條評論不是 bot
- **動作**：在分析報告中單獨列出「需重新開啟」區塊（置頂）
- **不主動重開**，提供 `gh issue reopen` 命令建議

---

## Agent 協作架構

```
主 Agent (review-issues)
   ↓
├── Agent 1: 提早終止檢查（快速過濾無效 issues）
├── Agent 2: 分析 open issues（現有功能）
├── Agent 3: 分析 closed issues（檢查關閉後回覆）
├── Agent 4: 標題生成（為不明確標題生成新標題）
└── Agent 5: 重複判斷（平台關鍵字搜尋 + 語義比對）
```

---

## 技術實作細節

### 使用的 GitHub CLI 命令

```bash
# 1. 查詢 open issues（含標籤和評論，用於提早終止檢查）
gh issue list --state open --limit 100 --json number,title,body,labels,createdAt,updatedAt,author,url,comments

# 2. 查詢 closed issues（檢查關閉後回覆）
gh issue list --state closed --limit 100 --json number,title,body,labels,closedAt,updatedAt,author,url,comments

# 3. 查看單一 issue 評論
gh issue view <number> --json comments

# 4. 自動修改標題
gh issue edit <number> --title "新標題"

# 5. 自動關閉重複 issue
gh issue close <number> --reason "not planned" --comment "此問題與 #xxx 重複..."

# 6. 重新開啟 issue（提供給使用者手動執行）
gh issue reopen <number>

# 7. 搜尋相似 issues（重複判斷）
gh search issues "TixCraft 登入" --repo bouob/tickets_hunter --state open
```

### 平台關鍵字清單（用於重複判斷）

| 平台 | 搜尋關鍵字 |
|------|-----------|
| **TixCraft** | `"TixCraft"`, `"拓元"`, `"SID"`, `"Google 登入"`, `"驗證碼"` |
| **KKTIX** | `"KKTIX"`, `"崩潰"`, `"crash"`, `"場次選擇"`, `"驗證問題"` |
| **iBon** | `"iBon"`, `"Shadow DOM"`, `"Angular"`, `"Cookie"`, `"日期選擇"` |
| **TicketPlus** | `"TicketPlus"`, `"遠大"`, `"關鍵字"`, `"自動遞補"`, `"價位"` |
| **NoDriver** | `"NoDriver"`, `"CDP"`, `"反偵測"`, `"AttributeError"`, `"to_json"` |
| **KHAM** | `"KHAM"`, `"寬宏"`, `"座位"`, `"自動選位"` |
| **FamiTicket** | `"FamiTicket"`, `"全家"`, `"登入"`, `"驗證"` |

---

## 預期效益

1. **減少人工負擔**：自動修正標題、自動關閉重複 issues
2. **避免遺漏**：追蹤關閉後的回覆，確保使用者問題不被忽略
3. **提升效率**：提早終止機制減少 30-50% 無效分析
4. **改善體驗**：報告結構更清晰，優先顯示需處理項目

---

## 執行範例

```bash
# 在專案目錄執行
/review-issues
```

**預期輸出**：
- 完整的分析報告（Markdown 格式）
- 「需重新開啟」區塊（若有）置頂顯示
- 「已自動處理」區塊列出自動修正的標題和關閉的重複 issues
- 三層優先度分組
- 處理建議順序

**自動執行的操作**：
- 修正不明確的標題（不通知）
- 關閉明確重複的 issues（留言引用原 issue）

**需手動確認的操作**：
- 重新開啟關閉後有回覆的 issues
- 關閉已解決/已修復的 issues
- 關閉空白或資訊不足的 issues
