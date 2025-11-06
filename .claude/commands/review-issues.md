# Review GitHub Issues 指令

請分析當前專案（Tickets Hunter）的 **開啟狀態（open）** GitHub issues，整理相似問題並提供處理建議。

## 執行步驟

1. **抓取並檢查開啟狀態的 issues**
   - 使用 `gh issue list --state open --limit 100 --json number,title,body,labels,createdAt,author,url` 抓取當前倉庫的 **open issues**
   - 對每個 issue，使用 `gh issue view <issue_number> --json comments` 抓取評論，檢查是否有使用者回覆表示：
     - 已解決（如「已經修好」、「更新後沒問題」、「已解決」）
     - 已修復（如「新版本已修復」、「已在 X 版本修正」）
     - 無法重現（如「無法重現」、「不知道怎麼重現」）
   - **不檢查已關閉（closed）的 issues**
   - 如果無法取得倉庫資訊，請提示使用者確認是否在正確的 Git 專案目錄中

2. **預先檢查與自動處理**
   - **空白 issue**：body 為空或僅包含模板文字 → 標註「建議關閉」
   - **標題不明確**：標題包含 `<請描述問題>` 等 → 標註「待澄清」
   - **資訊不足**：Bug report 缺少必要欄位 → 標註「資訊不足」
   - **重複問題**：相同平台、相同錯誤或高度相似 → 標註「重複」
   - **已解決問題**：評論中有使用者確認已解決 → 標註「已回報解決」
   - **已修復問題**：CHANGELOG.md 或評論中已記錄修正 → 標註「已修復」

3. **分析與分組**
   - 根據問題描述和標題，將相似的 issues 分組
   - 識別重複或高度相關的問題
   - 評估每個問題的影響範圍和嚴重性
   - **重點**：只分析 open 狀態的 issues，但在報告中標註已解決的 issues

## 輸出格式

### 📊 Issues 總覽
- 總數量：X 個 open issues
- 分類統計：Bug (X) | 功能請求 (X) | 其他 (X)
- **待處理**：X 個（排除「已解決」、「已修復」的 issues）

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

### ✅ 已解決/已修復的 Issues（無需處理）

- **#XXX** - [問題摘要] - 已回報解決於 [日期]
- **#YYY** - [問題摘要] - 已在版本 [X.Y.Z] 修復

---

### 🔗 重複問題
- #111 與 #222 重複 - [問題摘要]
- 建議：合併為單一 issue

---

### 📋 處理建議順序
1. [分組 X] - [原因]
2. [分組 Y] - [原因]
3. ...

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

## 特別注意

- **僅分析開啟狀態（open）的 issues**，但在報告中清楚標註已解決的 issues
- 標注哪些問題可能已在最新版本中修復（檢查 CHANGELOG.md）
- 識別需要更多資訊才能處理的 issues
- 提供「快速勝利」的問題（容易修復且影響大）
- **評論檢查**：若評論過多（>10 條），可只檢查最新 5 條評論和原 issue 提交者的評論

## 輸出要求

- 使用繁體中文
- 提供清晰的 issue 編號（如 #123）
- 簡潔的摘要（每個問題 1-2 句話）
- 可操作的建議
- 避免使用 emoji（除了章節標題）
- **提醒**：分析結果包含開啟狀態的 issues，但已解決的 issues 在報告中單獨列出

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

## 自動處理規則

執行 `/review-issues` 時自動檢查並標註：

### 1. 空白 Issue
- **條件**：body 為空或僅包含模板預設文字
- **動作**：在分析報告中標註「建議使用範本 2 關閉」
- **不主動關閉**，等待使用者確認

### 2. 標題不明確
- **條件**：標題包含 `<請描述問題>`、`<請描述功能需求>` 等
- **動作**：在分析報告中標註「標題不明確」
- **不主動回應**

### 3. 資訊不足
- **條件**：Bug report 缺少錯誤訊息、平台、重現步驟
- **動作**：在分析報告中標註「資訊不足，建議請使用者補充」
- **不主動回應**

### 4. 重複問題
- **條件**：相同平台、相同錯誤或高度相似描述
- **動作**：在分析報告中標註重複 issue 編號
- **不主動回應**（由使用者決定是否關閉）

### 5. 已修正問題
- **條件**：CHANGELOG.md 中已記錄修正或評論中有「已在 X 版本修復」
- **動作**：在分析報告中標註「已在 X 版本修復，建議使用範本 1 關閉」
- **不主動關閉**，等待使用者確認

### 6. 已解決問題（新增）
- **條件**：評論中有原 issue 提交者確認「已解決」、「修好」、「沒問題」等
- **動作**：在分析報告中標註「已回報解決於 [日期]」，單獨列在「已解決」區塊
- **不主動關閉**，等待使用者確認（可由維護者判斷是否自動關閉）

### 7. 無法重現（新增）
- **條件**：評論中有「無法重現」、「不知道怎麼重現」等
- **動作**：在分析報告中標註「無法重現」，可考慮使用範本 3 關閉
- **不主動回應**，等待使用者確認
