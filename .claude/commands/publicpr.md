---
description: "從私人 repo 建立安全 PR 到公開 repo，自動過濾機敏檔案"
model: sonnet
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 公開 Repo PR 建立指令

安全地從私人 repo (private) 建立 Pull Request 到公開 repo (origin)，自動過濾機敏檔案和 commits。

---

## 🎯 指令目的

此指令專門處理雙 repo 維護流程中的發布階段：
- **來源**：private repo (私人開發庫)
- **目標**：origin repo (公開發布庫)
- **核心功能**：自動過濾機敏檔案，確保公開 repo 不包含私人內容

---

## ⚠️ 重要說明：雙庫獨立架構

由於公開庫使用 **Squash Merge** 策略，公開庫和私人庫的 **commit history 完全獨立**：

- **公開庫**：每次發布只有 1 個 squash commit
- **私人庫**：保留完整的 commit history
- **Commit ID 永遠不同**：這是正常的，不是錯誤

因此，本指令使用**版本號比對**（`CONST_APP_VERSION`）而非 commit 比對來判斷是否需要發布。

---

## 🚨 安全機制

### 機敏檔案清單

以下檔案/目錄會被自動過濾，**不能**出現在公開 PR 中：

```
.claude/          - Claude 自動化設定
CLAUDE.md         - 專案開發規範
docs/             - 技術文件和指南
.specify/         - 規格模板和指令碼
specs/            - 功能規格和設計文件
FAQ/              - 常見問題解答
.temp/            - 臨時測試資料（HTML/JS 網頁內容）
```

### 多層確認機制

1. **URL 驗證**：確認目標 remote 是公開 repo
2. **Commit 掃描**：顯示將推送的 commits 清單
3. **檔案檢查**：顯示即將推送的檔案變更（排除機敏檔案）
4. **最終確認**：要求使用者明確確認推送

---

## 🔧 進階選項

- `--dry-run`: 預覽模式，僅顯示分析結果不執行實際推送
- `--base-branch=<branch>`: 指定基礎分支（預設：main）
- `--auto-merge`: 建立 PR 後自動設定 auto-merge（需通過 CI）
- `--force`: 跳過所有確認（⚠️ 危險操作，不建議使用）

**注意**: 本指令永遠使用 Squash Merge 策略，不再支援 Cherry-pick（因雙庫 history 獨立）。

---

## 📝 執行流程

### 步驟 0 - 前置檢查

#### A. 驗證 Git Remote 設定

- 執行 `git remote -v` 檢查 remote 設定
- 確認存在 `origin` 和 `private` 兩個 remote
- 提取 origin 的 URL

#### B. 確認目標 Remote

- 顯示目標 URL：
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋 目標 Repo 確認
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  目標 Remote: origin
  目標 URL: https://github.com/bouob/tickets_hunter.git

  ⚠️ 此操作將推送到公開 repo！
  請確認以上 URL 為正確的公開 repo。
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- **明確詢問**：「確認目標 repo 正確？(y/n)」
- **僅當使用者回覆 "y" 時**：繼續執行

### 步驟 1 - 取得最新狀態

- 執行 `git fetch origin` 取得公開 repo 最新狀態
- 執行 `git fetch private` 取得私人 repo 最新狀態
- 比較兩個 repo 的差異

### 步驟 1.5 - 版本比對與策略選擇 ⭐ 改善

#### A. 比對版本號（優先）

**重要**: 由於雙庫 commit history 獨立，使用版本號比對而非 commit 比對

```bash
# 取得公開庫版本
ORIGIN_VERSION=$(git show origin/main:src/nodriver_tixcraft.py | grep "CONST_APP_VERSION" | head -1)

# 取得本地版本
LOCAL_VERSION=$(grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1)

# 比對版本
if [ "$ORIGIN_VERSION" = "$LOCAL_VERSION" ]; then
    echo "版本相同，無需發布"
    exit 0
fi
```

#### B. 顯示版本比對結果

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 版本比對結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

公開庫版本: 2025.11.12.1
本地版本: 2025.11.19

需要發布: ✅ 是

策略: Squash Merge（雙庫獨立 history）

說明：
- 公開庫和私人庫的 commit history 完全獨立
- 每次發布都是建立新的 squash commit
- 這是正常的工作流程，不是錯誤
- ⚠️ 發布後不要從 public 拉回變更到 private（單向流程）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### C. 版本相同時的處理

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 版本比對結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

公開庫版本: 2025.11.19
本地版本: 2025.11.19

需要發布: ❌ 否（版本相同）

如果確實有需要發布的變更，請先執行：
  /gupdate  -> 更新版本號

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### D. 策略說明

本指令**永遠使用 Squash Merge**，原因：
- 公開庫和私人庫的 commit history 完全獨立
- Cherry-pick 會因為 commit ID 不同而永遠失敗
- Squash Merge 直接比對檔案差異，避免 history 問題

### 步驟 2 - 掃描並過濾 Commits（Cherry-pick 模式）

#### A. 列出所有未推送的 Commits

- 執行 `git log origin/main..HEAD --oneline` 顯示本地領先的 commits
- 顯示 commits 數量和摘要

#### B. 檢查每個 Commit 是否包含機敏檔案

**方法 1：識別 PRIVATE 標記（優先，高效能）**
- 執行 `git log --format=%B [commit-hash] -1` 取得 commit 訊息
- 檢查是否包含 "🔒 PRIVATE COMMIT" 或 "FILTER MARKER FOR /publicpr"
- 如果包含 → 立即標記為機敏 commit，跳過檔案掃描

**方法 2：檔案清單掃描（回退方法）**
- 對於沒有 PRIVATE 標記的 commits：
  - 執行 `git show --name-only [commit-hash]` 取得檔案清單
  - 比對機敏檔案清單（`.claude/`, `docs/`, `CLAUDE.md`, `.specify/`, `specs/`, `FAQ/`, `.temp/`）
  - 過濾掉包含機敏檔案的 commits

**為什麼需要兩種方法？**
- 方法 1：處理新版 `/gsave` 產生的 commits（已標記）
- 方法 2：處理舊版 commits 或手動 commits（未標記）
- 確保向下相容，不遺漏任何機敏檔案

#### C. 顯示過濾結果

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Commit 掃描結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 找到 8 個 commits
⚠️ 發現 3 個 commits 包含機敏檔案（已排除）：
  - abc1234 🔒 docs(private): update internal documentation [PRIVATE 標記識別]
  - def5678 chore: update CLAUDE.md [檔案掃描識別]
  - ghi9012 feat: add spec for new feature [檔案掃描識別]

✅ 剩餘 5 個有效 commits 將被推送：
  - jkl3456 ✨ feat(ticketplus): add TicketPlus support
  - mno7890 🐛 fix(ocr): resolve OCR timeout issue
  - pqr1234 ♻️ refactor(util): improve error handling
  - stu5678 ✅ test: add integration tests
  - vwx9012 📝 docs(readme): update README

過濾效能：
  - 3 個透過 PRIVATE 標記快速識別（無需檔案掃描）
  - 0 個需要檔案掃描回退

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### D. 檢查是否有可推送的 Commits

- **如果沒有有效 commits**：
  ```
  ⚠️ 沒有可推送的 commits！

  可能原因：
  1. 所有 commits 都包含機敏檔案
  2. 已經與 origin/main 同步

  請檢查並確認。
  ```
  - 結束執行

### 步驟 3-Squash - Squash Merge 執行流程 ⭐ 新增

**適用條件**: 當步驟 1.5 選擇 Squash Merge 策略時

#### A. 分析檔案變更（不掃描 commits）

**重要**: Squash 模式不需要逐一掃描 commits，直接分析整體檔案變更

- 執行 `git diff origin/main..HEAD --name-status` 取得所有檔案變更
- 過濾機敏檔案：
  ```bash
  # 排除機敏檔案清單
  SENSITIVE_PATTERNS=".claude/|^docs/|^CLAUDE.md|^.specify/|^specs/|^FAQ/|^.temp/"

  # 過濾檔案變更
  git diff origin/main..HEAD --name-status | \
    grep -Ev "$SENSITIVE_PATTERNS"
  ```

#### B. 顯示檔案變更統計

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Squash Merge - 檔案變更預覽
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

版本更新: 2025.11.12.1 → 2025.11.19
Squash 策略: 合併為 1 個 commit

將推送以下乾淨檔案變更：

新增檔案 (2):
  + src/nodriver_ticketplus.py
  + tests/test_ticketplus.py

修改檔案 (11):
  ~ src/chrome_tixcraft.py
  ~ src/nodriver_tixcraft.py
  ~ README.md
  ~ CHANGELOG.md
  ~ package.json

刪除檔案 (1):
  - src/deprecated_module.py

總計：14 個檔案變更

⚠️ 已自動排除機敏檔案：
  - .claude/ (設定檔)
  - docs/ (內部文件)
  - CLAUDE.md (開發規範)
  - .specify/ (規格模板)
  - specs/ (功能規格)
  - .temp/ (測試資料)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### C. 確認推送

- **明確詢問**：「確認使用 Squash Merge 推送這些變更到公開 repo？(y/n)」
- **僅當使用者回覆 "y" 時**：繼續執行

#### D. 建立臨時分支並複製檔案

- 生成分支名稱：`public-sync-YYYY-MM-DD-HHmm`
- 建立分支：`git checkout -b [branch-name] origin/main`
- Stash 本地變更（如果有）：`git stash push -m "Temp stash for publicpr"`

#### E. 使用 git diff 複製變更

**方法**: 直接複製檔案差異，避免 cherry-pick 衝突

```bash
# 1. 切換回原始分支
git checkout main

# 2. 取得乾淨檔案清單（排除機敏檔案）
CLEAN_FILES=$(git diff origin/main..HEAD --name-only | \
  grep -Ev "(.claude/|^docs/|^CLAUDE.md|^.specify/|^specs/|^FAQ/|^.temp/)")

# 3. 切換到臨時分支
git checkout public-sync-YYYY-MM-DD-HHmm

# 4. 逐個檔案複製變更
echo "$CLEAN_FILES" | while read file; do
  # 檢查檔案狀態
  STATUS=$(git diff origin/main..main --name-status | grep "$file" | awk '{print $1}')

  if [ "$STATUS" = "D" ]; then
    # 刪除檔案
    git rm "$file"
  else
    # 新增或修改檔案
    git checkout main -- "$file"
    git add "$file"
  fi
done
```

#### F. 建立 Squash Commit

- 生成 commit 訊息（英文，Conventional Commits 格式）：
  ```bash
  COMMIT_MSG="chore(release): sync public repo with $(date +%Y-%m-%d) updates

  - Original commits: {total_commits}
  - Squashed into single commit for cleaner history
  - Automatically filtered sensitive files

  Files changed: {files_changed}
  "
  ```

- 執行 commit：
  ```bash
  git commit -m "$COMMIT_MSG"
  ```

#### G. 推送到 Origin

- 執行 `git push origin [branch-name]`
- 顯示推送結果

```
✅ Squash commit 推送成功！

分支: public-sync-2025-11-12-0322
Commit: 0face0e chore(release): sync public repo with 2025-11-12 updates
Remote: origin
URL: https://github.com/bouob/tickets_hunter.git
```

#### H. Stash 還原（如果有）

- 執行 `git stash pop` 還原暫存的本地變更

---

### 步驟 3 - 顯示檔案變更預覽（Cherry-pick 模式）

#### A. 收集所有有效 Commits 的檔案變更

- 對每個有效 commit 執行 `git show --stat [commit-hash]`
- 彙整所有變更的檔案清單
- 移除重複檔案

#### B. 顯示變更摘要

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 檔案變更預覽
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

將推送以下檔案變更：

新增檔案 (2):
  + src/nodriver_ticketplus.py
  + tests/test_ticketplus.py

修改檔案 (5):
  ~ src/chrome_tixcraft.py
  ~ src/nodriver_tixcraft.py
  ~ README.md
  ~ CHANGELOG.md
  ~ .gitignore

刪除檔案 (1):
  - src/deprecated_module.py

總計：8 個檔案變更

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### C. 確認推送

- **明確詢問**：「確認推送這些變更到公開 repo？(y/n)」
- **僅當使用者回覆 "y" 時**：繼續執行

### 步驟 4 - 建立臨時分支

#### A. 生成分支名稱

- 格式：`public-sync-YYYY-MM-DD-HHmm`
- 範例：`public-sync-2025-11-07-1430`

#### B. 建立並切換分支

- 執行 `git checkout -b [branch-name] origin/main`
- 基於 `origin/main` 建立新分支（確保乾淨的 history）

### 步驟 5 - Cherry-pick 有效 Commits

#### A. 依序 Cherry-pick

- 對每個有效 commit 執行 `git cherry-pick [commit-hash]`
- 顯示進度：
  ```
  🔄 Cherry-picking commits...

  [1/5] ✅ jkl3456 feat: add TicketPlus support
  [2/5] ✅ mno7890 fix: resolve OCR timeout issue
  [3/5] ✅ pqr1234 refactor: improve error handling
  [4/5] ✅ stu5678 test: add integration tests
  [5/5] ✅ vwx9012 docs: update README

  ✅ 所有 commits cherry-pick 完成！
  ```

#### B. 處理 Cherry-pick 衝突

- **如果發生衝突**：
  ```
  ⚠️ Cherry-pick 失敗: pqr1234 refactor: improve error handling

  衝突檔案：
    - src/chrome_tixcraft.py

  請選擇處理方式：
  [1] 手動解決衝突後繼續
  [2] 跳過此 commit
  [3] 中止操作
  ```
- **選擇 [1]**：暫停執行，等待使用者手動解決衝突後執行 `git cherry-pick --continue`
- **選擇 [2]**：執行 `git cherry-pick --skip`，繼續下一個 commit
- **選擇 [3]**：執行 `git cherry-pick --abort`，回到原始分支，清理臨時分支

### 步驟 6 - 推送到 Origin

#### A. 推送臨時分支

- 執行 `git push origin [branch-name]`
- 顯示推送進度

#### B. 推送成功確認

```
✅ 推送成功！

分支：public-sync-2025-11-07-1430
Remote: origin
URL: https://github.com/bouob/tickets_hunter.git
```

### 步驟 7 - 建立 Pull Request

#### A. 生成 PR 標題和描述

**PR 標題格式**（英文）：
```
chore(release): sync public repo with [date] updates
```

**範例**：
- `chore(release): sync public repo with 2025-11-08 updates`
- `chore(release): sync public repo with Nov 8, 2025 updates`

**PR 描述格式**（繁體中文，標題可用 emoji，內容不用）：

**格式 1 - Squash Merge 模式**（commits > 10 時使用）：
```markdown
## 📋 變更摘要

本次發布使用 Squash Merge 合併了 {time_range} 的所有更新。

### 主要變更
[從最近 20 個 commits 自動提取類別摘要]

- 新功能: {count} 項
  - 新增 TicketPlus 平台支援
  - 新增自動座位選擇
- 錯誤修復: {count} 項
  - 修正 OCR 超時問題
  - 修正日期關鍵字匹配
- 重構: {count} 項
  - 改善錯誤處理機制

---

## 📊 統計資訊

- **原始 Commits**: {total_commits} 個
- **機敏 Commits**: {private_commits} 個（已排除）
- **Squash 策略**: 合併為 1 個 commit
- **檔案變更**: {files_changed} 個
  - 新增: {added} 個
  - 修改: {modified} 個
  - 刪除: {deleted} 個

---

## ✅ 檢查清單

- [x] 已排除機敏檔案（.claude/, docs/, CLAUDE.md 等）
- [x] 使用 Squash Merge 簡化 history
- [x] Private repo 保留完整 commit 記錄
- [ ] 待 CI 檢查通過
- [ ] 待 Code Review

---

## ⚠️ 重要提醒

- Public repo 只包含 1 個 squash commit
- Private repo 保留完整 {total_commits} 個 commits
- 兩個 repo 的 history 完全獨立（這是正常的）
- **發布後不要從 public 拉回變更到 private**（單向流程）

---

## 🔗 相關連結

- 完整變更記錄：查看 private repo 的 CHANGELOG.md
- 技術文件：（僅私人 repo 可見）
```

**格式 2 - Cherry-pick 模式**（commits ≤ 10 時使用）：
```markdown
## 📋 變更摘要

本次發布包含以下更新：

### 新功能
- 新增 TicketPlus 平台支援

### 錯誤修復
- 修正 OCR 超時問題

### 重構
- 改善錯誤處理機制

### 測試
- 新增整合測試

### 文件
- 更新 README

---

## 📊 統計資訊

- **Commits**: 5 個
- **檔案變更**: 8 個
- **新增檔案**: 2 個
- **修改檔案**: 5 個
- **刪除檔案**: 1 個

---

## ✅ 檢查清單

- [x] 已排除機敏檔案（.claude/, docs/, CLAUDE.md 等）
- [x] 已通過本地測試
- [ ] 待 CI 檢查通過
- [ ] 待 Code Review

---

## 🔗 相關連結

- 完整變更記錄：查看 CHANGELOG.md
- 技術文件：（僅私人 repo 可見）
```

#### B. 建立 PR

- 執行 `gh pr create --repo origin --base main --head [branch-name] --title "[標題]" --body "[描述]"`
- **自動 Merge 處理**（如果指定 `--auto-merge`）：
  - 設定 auto-merge：`gh pr merge --auto --squash [PR-URL]`
  - 顯示提示：「PR 已設定自動合併，待 CI 通過後將自動 merge」

#### C. 顯示 PR 資訊

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pull Request 已建立！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PR URL: https://github.com/bouob/tickets_hunter/pull/123
分支: public-sync-2025-11-07-1430

請檢查 PR 內容並確認無誤後進行 merge。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 步驟 8 - 清理與還原

#### A. 切換回原始分支

- 執行 `git checkout main`（或原始分支）

#### B. 詢問是否清理臨時分支

- **詢問**：「PR 已建立。是否刪除本地臨時分支？(y/n)」
- **選擇 y**：執行 `git branch -D [branch-name]`
- **選擇 n**：保留臨時分支

#### C. 顯示完成訊息

```
✅ 操作完成！

下一步：
1. 檢查 PR: https://github.com/bouob/tickets_hunter/pull/123
2. 確認 CI 檢查通過
3. 進行 Code Review
4. Merge PR 到 main
```

---

## ⚠️ 執行約束

### 必須確認的步驟

1. **目標 Repo 確認**：必須使用者明確確認目標 URL
2. **檔案變更確認**：必須使用者確認推送的檔案清單
3. **衝突處理**：發生衝突時必須使用者選擇處理方式

### 自動中止條件

- 沒有有效 commits 可推送
- 使用者在任何確認步驟回覆 "n"
- Cherry-pick 發生無法自動解決的衝突（選擇中止時）
- Git 指令執行失敗

---

## 📚 使用場景

### 場景 1：標準發布流程（推薦）

```bash
# 在 private repo 完成開發
gsave -> 提交多個 commits（包含程式碼和機敏檔案）
gpush -> 推送到 private repo
gupdate -> 更新版本號（如需要）

# 準備發布到公開 repo
publicpr

執行流程：
1. 確認目標 repo: origin (https://github.com/bouob/tickets_hunter.git)
2. 取得最新狀態
3. 版本比對：
   - 公開庫版本: 2025.11.12.1
   - 本地版本: 2025.11.19
   - 需要發布: ✅ 是
4. 分析檔案變更：
   - 過濾機敏檔案
   - 顯示 11 個乾淨檔案變更
5. 確認推送？y
6. 建立臨時分支: public-sync-2025-11-19-0100
7. 複製檔案變更
8. 建立 squash commit
9. 推送到 origin
10. 建立 PR: https://github.com/bouob/tickets_hunter/pull/115
11. 清理臨時分支

結果：
- Public repo: 1 個 squash commit
- Private repo: 保留完整 commit history
- 雙庫 history 完全獨立（正常現象）
```

### 場景 2：版本相同時

```bash
publicpr

執行流程：
1. 確認目標 repo: origin
2. 版本比對：
   - 公開庫版本: 2025.11.19
   - 本地版本: 2025.11.19
   - 需要發布: ❌ 否（版本相同）
3. 提示使用 /gupdate 更新版本號
4. 結束
```

### 場景 3：預覽模式

```bash
# 先預覽不實際推送
publicpr --dry-run

執行流程：
1. 確認目標 repo: origin
2. 版本比對並顯示結果
3. 顯示完整檔案變更分析
4. 🔍 Dry-run 模式，不執行實際推送
```

---

## 🛡️ 安全特性

### 機敏檔案防護

- **自動檢測**：掃描每個 commit 的檔案清單
- **自動過濾**：排除包含機敏檔案的 commits
- **清楚提示**：顯示被排除的 commits 和原因

### History 清理

- **乾淨基礎**：基於 `origin/main` 建立新分支
- **Cherry-pick**：僅挑選有效 commits，不帶入機敏 history
- **獨立 History**：臨時分支與 private repo 的 history 完全隔離

### 多層確認

- **URL 驗證**：防止推送到錯誤 repo
- **檔案預覽**：確認推送內容無誤
- **衝突處理**：提供多種處理選項

---

## 💡 使用建議

### 建議的工作流程

```
開發階段（private repo）：
1. gsave      -> 提交變更（包含程式碼和機敏檔案）
2. gpush      -> 推送到 private repo
3. 持續開發   -> 重複步驟 1-2

發布階段（public repo）：
4. publicpr   -> 建立 PR 到 origin（自動過濾機敏檔案）
5. Code Review
6. Merge PR
7. Release
```

### 何時使用此指令

- ✅ 完成階段性開發，準備發布到公開 repo
- ✅ 需要將私人 repo 的程式碼同步到公開 repo
- ✅ 確保公開 repo 不包含機敏檔案

### 何時不使用此指令

- ❌ 日常開發推送（請使用 `/gpush` 推送到 private）
- ❌ 私人檔案更新（請使用 `/privatepush`）
- ❌ 緊急修復需要直接推送到 origin（需要手動處理）

---

## 🔧 故障排除

### 問題 1：沒有有效 commits

**原因**：所有 commits 都包含機敏檔案

**解決方案**：
1. 檢查是否有純程式碼的 commits
2. 考慮手動分離程式碼和機敏檔案的變更
3. 重新提交純程式碼的 commits

### 問題 2：Cherry-pick 衝突

**原因**：origin/main 與 private repo 的程式碼有衝突

**解決方案**：
1. 選擇手動解決衝突
2. 編輯衝突檔案
3. 執行 `git add [檔案]`
4. 執行 `git cherry-pick --continue`
5. 重新執行 `/publicpr`

### 問題 3：PR 建立失敗

**原因**：gh CLI 未安裝或未登入

**解決方案**：
1. 安裝 gh CLI: https://cli.github.com/
2. 登入 GitHub: `gh auth login`
3. 重新執行 `/publicpr`

---

## 📚 延伸閱讀

- **工作流程文件**：`docs/11-git-workflow/dual-repo-workflow.md`
- **配對指令**：`/gpush`（推送到 private）、`/privatepush`（強制推送機敏檔案）
- **專案憲章**：`.specify/memory/constitution.md`（第 IX 條：Git 提交規範）

$ARGUMENTS
