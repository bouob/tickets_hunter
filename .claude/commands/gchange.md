---
description: 根據未推送的 commits 自動生成 CHANGELOG.md（PR 前使用）
argument-hint: [count] (可選：分析最近幾個 commits，預設分析所有未推送的)
model: haiku
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git show:*), Bash(git status:*), Bash(git fetch:*), Bash(git rev-list:*), Bash(date:*), Bash(Get-Date:*), Read, Edit, Write, Grep, AskUserQuestion
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

**參數處理邏輯**：
- 空白或 `all` → 分析所有未推送的 commits（預設，適合 PR 前使用）
- 數字 N → 分析最近 N 個 commits（例如：`10` 表示最近 10 個）

---

# 智慧 Changelog 生成器 📝

## 🎯 使用場景

本指令專為「累積多個 commits 後統一推送 PR」的工作流程設計：

1. 本地開發累積多個 commits
2. 推送 PR 前執行 `/gchange` 自動生成 CHANGELOG
3. **預覽並確認**生成的內容
4. 使用 `/gsave` 提交，再用 `/gpush` 推送

## ⚠️ 重要提醒

**本指令僅更新 CHANGELOG.md 檔案內容，不會自動執行 git commit**

- ✅ 允許：編輯或創建 CHANGELOG.md 檔案
- ❌ 禁止：執行 `git add`、`git commit`、`git push` 等任何 git 寫入操作
- 📝 完成後：由使用者決定是否提交變更

---

## 📋 執行流程

### 第一階段：前置檢查

**1. 工作目錄驗證**
- 檢查當前是否在專案根目錄（包含 `.git/` 和 `CHANGELOG.md`）

**2. Git 狀態分析**
```bash
git fetch origin  # 獲取遠端最新狀態（不更動本地）
git status        # 檢查工作目錄狀態
git rev-list --count origin/main..HEAD  # 計算未推送的 commits
```

**3. 決定分析範圍**
- **預設**：分析所有未推送的 commits（`origin/main..HEAD`）
- **指定數量**：分析最近 N 個 commits（`HEAD~N..HEAD`）

**錯誤處理**：
- 如果沒有未推送的 commits → 提示使用者並結束
- 如果 CHANGELOG.md 不存在 → 自動創建新檔案
- 如果 git fetch 失敗 → 提示檢查網路連線

### 第二階段：Commit 分析與機敏資料過濾

**分析目標 commits**
- **預設**：`git log origin/main..HEAD --no-merges`
- **指定數量**：`git log HEAD~N..HEAD --no-merges`

**🔒 機敏資料過濾（自動執行）**

**必須排除的 Commits（優先檢查）**：
1. **PRIVATE 標記識別**
   - Commit 訊息包含 `🔒 PRIVATE COMMIT`
   - Commit 訊息包含 `FILTER MARKER FOR /publicpr`
   - Scope 為 `(private)` 的 commits（如 `docs(private):`）

2. **機敏檔案變更檢測**
   - 使用 `git show <commit> --name-only` 檢查變更檔案
   - 排除僅修改以下路徑的 commits：
     - `.claude/` - Claude 自動化設定
     - `CLAUDE.md` - 專案開發規範
     - `docs/` - 技術文件和指南
     - `.specify/` - 規格模板和指令碼
     - `specs/` - 功能規格和設計文件
     - `FAQ/` - 常見問題解答
     - `.temp/` - 臨時測試資料

3. **混合 Commits 處理**
   - 如果 commit 同時包含公開和機敏檔案變更
   - **僅提取公開檔案的變更說明**
   - 在 CHANGELOG 中不提及機敏檔案的修改

**過濾後顯示**：
```
🔍 Commit 分析結果:
  ✅ 共 10 個 commits
  🔒 跳過 3 個 PRIVATE commits
  ✅ 將分析 7 個公開 commits
```

**Commit 訊息智慧解析（僅公開 commits）**

**🎯 核心分類（優先生成）：**
- ✨ **新功能 (feat)** - 新增功能、平台支援、重要改善
- 🐛 **Bug 修復 (fix)** - 問題修正、錯誤處理、穩定性改善

**📋 次要分類（選擇性）：**
- 📝 **文件更新 (docs)** - 使用者文件、指南改善（僅公開文件）
- 🔧 **配置變更 (chore)** - 設定檔調整、工具更新
- 💄 **UI/樣式 (style)** - 介面優化、視覺改善
- ♻️ **重構 (refactor)** - 程式碼重構（僅當影響使用者時才記錄）
- ⚡ **效能改善 (perf)** - 速度提升、資源優化

### 第三階段：CHANGELOG 內容生成

**版本標題**：
```markdown
## YYYY.MM.DD
```

**🌟 推薦格式（精簡列點式）**

這是**最推薦**的格式，簡潔明瞭：

```markdown
## 2025.11.03

- 新增 KKTIX 驗證問題即時偵測功能
- 修復 KKTIX 字典檔案答案解析錯誤
- 改善 iBon 平台日期與區域選擇速度
- 新增 TixCraft 售罄智慧偵測
```

**📋 進階格式（詳細分類式）**

適合**重大版本更新**或有多個相關改動時使用：

```markdown
## 2025.11.03

### 🆕 新功能

- 新增 KKTIX 驗證問題即時偵測
- 整合六大搜尋引擎（Google、Bing、Perplexity 等）

### 🐛 Bug 修復

- 修復字典答案解析錯誤
- 修正分隔符號說明
```

**格式選擇原則**：
- ✅ **預設使用精簡格式**（日常更新）
- ✅ **大版本使用詳細格式**（重大功能更新）
- ✅ 由使用者在「預覽與確認」階段決定是否調整

**🎯 使用者視角寫作原則**

**重要**：詳細規範請參考 `docs/10-project-tracking/changelog_guide.md`

**核心原則**：
- ✅ **精簡為主**：每條變更控制在一行內，避免冗長說明
- ✅ 寫「使用者能做什麼」，不寫「程式怎麼做的」
- ❌ **嚴格禁止**：函數名稱、程式碼位置、測試結果
- ⚠️ **盡量避免**：過多技術術語（CDP、DOM、API、演算法等）
- ✅ **允許使用**：平台名稱、使用者可見功能、效能改善描述

**格式要求**：
- ✅ **推薦精簡列點式**：一條變更一行（如：`- 新增功能描述`）
- ⚠️ **避免過度格式化**：不使用粗體、冒號、詳細解釋（除非重大更新）
- ✅ **保持簡潔**：每條描述 10-20 字為佳

### 第三階段.5：預覽與確認（新增）

**在更新 CHANGELOG.md 前，執行以下步驟**：

1. **顯示完整預覽**
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📋 生成的 CHANGELOG 內容預覽
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [顯示完整生成的 CHANGELOG 條目]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

2. **詢問使用者確認**
   使用 AskUserQuestion 工具詢問：
   ```
   是否需要調整生成的 CHANGELOG 內容？

   選項：
   - proceed: 內容正確，繼續更新 CHANGELOG.md
   - edit: 需要調整，暫停執行讓我手動編輯
   - regenerate: 重新生成（提供調整建議）
   ```

3. **處理使用者回應**
   - **proceed**：繼續執行第四階段，更新 CHANGELOG.md
   - **edit**：暫停執行，顯示訊息：
     ```
     ⏸️ 已暫停執行

     請手動編輯生成的內容後，可選擇：
     1. 直接編輯 CHANGELOG.md（推薦）
     2. 調整 commit 訊息後重新執行 /gchange

     完成編輯後，使用 /gsave 提交變更
     ```
   - **regenerate**：詢問使用者需要調整的方向，然後重新生成內容

### 第四階段：更新 CHANGELOG.md

**🔝 累積式更新原則**
- **保留歷史** - 絕不修改或覆蓋舊版本條目
- **頂部插入** - 新版本條目插入到 "# Changelog" 標題下方
- **時間順序** - 最新版本在最上方，舊版本按時間倒序排列

**執行步驟**
1. 讀取現有 CHANGELOG.md（如果存在）
2. 生成今日版本條目（使用當前日期 `YYYY.MM.DD`）
3. 插入到檔案頂部（在 `# Changelog` 下方）
4. 保留所有舊條目（不修改任何歷史內容）

**完成確認**
```
✅ CHANGELOG.md 已更新

新版本條目已插入到頂部：
- 版本：2025.11.04
- 變更項目：5 項

請使用 /gsave 提交變更
```

---

## ⚙️ 使用範例

### 範例 1：分析所有未推送的 commits（推薦）
```bash
/gchange
```
**說明**：適合在推送 PR 前使用，自動分析所有本地累積的 commits

### 範例 2：分析最近 10 個 commits
```bash
/gchange 10
```
**說明**：只分析最近 10 個 commits

### 範例 3：分析所有未推送的 commits（明確指定）
```bash
/gchange all
```
**說明**：與預設行為相同

---

## 🔗 發布工作流程

建議的完整發布流程：

```bash
# 1. 更新版本號（如需要）
/gupdate

# 2. 生成 CHANGELOG（含預覽確認）
/gchange

# 3. 確認內容無誤（自動詢問）
# 選擇 proceed 或 edit

# 4. 提交所有變更
/gsave

# 5. 推送到遠端（如需要）
/gpush
```

---

## 🔒 安全特性

- ✅ **唯讀同步** - 使用 `git fetch` 僅獲取遠端狀態
- ✅ **保護本地** - 絕不執行可能更動本地檔案的 git 命令
- ✅ **實際差異** - 基於真實的 git 差異進行分析
- ✅ **智慧分類** - 自動識別變更類型和重要程度
- ✅ **歷史保護** - 絕不修改 CHANGELOG 的舊版本條目
- ✅ **預覽確認** - 更新前必須經過使用者確認
- 🔒 **機敏資料過濾** - 自動排除 PRIVATE commits 和機敏檔案變更

---

## 📚 延伸閱讀

- **詳細寫作規範**：`docs/10-project-tracking/changelog_guide.md`
- **配對指令**：`/gupdate`（更新版本號）、`/gsave`（提交變更）、`/gpush`（推送到遠端）

**💡 核心優勢**：
- 專為「累積 commits 後推 PR」的工作流程設計
- 自動轉換技術性 commit 為使用者友善的描述
- **預覽確認機制**：更新前可檢查並調整內容
- 完全保護歷史記錄，僅插入新條目
- **自動過濾機敏資料**：排除 PRIVATE commits 和內部文件變更

$ARGUMENTS
