**文件說明**：Git 推送安全規則的詳細說明，涵蓋核心規則、違反後果、正確做法與案例教學。

**最後更新**：2025-11-12

---

# Git 推送安全規則（詳細說明）

**文檔版本**: v1.0
**重要性**: 🚨 CRITICAL - NON-NEGOTIABLE

---

## 📋 文檔目的

本文檔從 CLAUDE.md 遷移出來，提供 Git 推送安全規則的詳細說明。

**CLAUDE.md 連結**：在 CLAUDE.md 中只保留核心要點，詳細說明在此文檔。

---

## ⚠️ 核心安全原則（NON-NEGOTIABLE）

### 最高規則

**所有 push 操作只能推送到私人庫**：
- 私人庫位址：`https://github.com/bouob/private-tickets-hunter.git` (remote: `private`)
- 公開庫位址：`https://github.com/bouob/tickets_hunter.git` (remote: `origin`)
- **嚴格禁止**直接推送到公開庫（`origin`）

### 為什麼需要這個規則？

1. **防止機敏資料洩露**
   - `.claude/` 目錄包含內部指令和設定
   - `docs/` 包含開發流程和私密資訊
   - `specs/` 包含詳細的規格文件
   - 某些 commits 包含測試資料或 API keys

2. **分離公開與私密內容**
   - 公開 repo（tickets_hunter）：只包含可公開的程式碼
   - 私人 repo（private-tickets-hunter）：包含所有內容

3. **安全的發布流程**
   - 使用 `/publicpr` 創建 PR 到公開庫
   - 自動過濾機敏檔案
   - Review 後再 merge

---

## 🔧 推送指令詳細說明

### 1. `/gpush` - 推送一般 commits

**目標**: `private/main`
**用途**: 推送公開程式碼變更（但仍推到私人庫）

**自動過濾規則**:
- 排除帶有 🔒 PRIVATE 標記的 commits
- 只推送一般代碼變更

**使用時機**:
- 修改了 `src/` 下的程式碼
- 更新了 `README.md`、`requirements.txt` 等公開文件
- 修復了 Bug

**指令執行流程**:
```bash
# 1. 檢查當前分支
git branch --show-current

# 2. 檢查未推送的 commits
git log private/main..HEAD --oneline

# 3. 過濾掉 PRIVATE commits
# 4. 推送到 private/main
git push private main
```

**預期輸出**:
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
...
To https://github.com/bouob/private-tickets-hunter.git
   abc1234..def5678  main -> main
```

---

### 2. `/privatepush` - 推送機敏檔案 commits

**目標**: `private/main`
**用途**: 推送 `.claude/`, `docs/`, `specs/` 等機敏檔案

**過濾規則**:
- 只推送帶 🔒 PRIVATE 標記的 commits
- 確保機敏檔案不會混入公開 repo

**使用時機**:
- 更新了 `.claude/` 下的 slash commands
- 修改了 `docs/` 下的開發文件
- 更新了 `specs/` 規格文件
- 更新了 `settings.json` 範例

**指令執行流程**:
```bash
# 1. 檢查 PRIVATE commits
git log --grep="🔒 PRIVATE" private/main..HEAD --oneline

# 2. 推送到 private/main
git push private main
```

**識別 PRIVATE commits**:
```bash
# PRIVATE commits 格式範例
🔒 PRIVATE: update slash command /speckit.analyze
🔒 PRIVATE: add constitution.md updates
🔒 PRIVATE: update docs/02-development/structure.md
```

---

### 3. `/publicpr` - 建立 PR 到公開庫

**目標**: `origin`（透過 PR）
**用途**: 正式發布到公開 repo

**自動過濾規則**:
- 排除 `.claude/` 目錄
- 排除 `docs/` 目錄（除了公開文件）
- 排除 `specs/` 目錄
- 排除帶 🔒 PRIVATE 標記的 commits
- 排除 `settings.json`（保留 `settings.json.example`）

**使用時機**:
- 完成一個重要功能，準備發布
- 修復了影響用戶的 Bug
- 更新了版本號，準備 Release

**指令執行流程**:
```bash
# 1. 創建發布分支（如果不存在）
git checkout -b release/vX.Y.Z

# 2. 過濾機敏檔案
# （使用 .gitignore 或手動移除）

# 3. 推送到 origin（創建 PR 分支）
git push origin release/vX.Y.Z

# 4. 使用 gh CLI 創建 PR
gh pr create --title "Release vX.Y.Z" --body "..." --base main --head release/vX.Y.Z
```

**PR 檢查清單**:
- [ ] 確認沒有 `.claude/` 文件
- [ ] 確認沒有 `docs/` 私密文件
- [ ] 確認沒有 `specs/` 文件
- [ ] 確認沒有 `settings.json`（只有 `settings.json.example`）
- [ ] 確認 commit 訊息沒有 🔒 PRIVATE 標記
- [ ] 確認 CHANGELOG.md 已更新
- [ ] 確認版本號已更新

---

## ❌ 嚴格禁止的操作

### 禁止指令列表

1. **`git push origin main`**
   - ❌ 直接推送到公開庫
   - 🚨 可能洩露機敏資料

2. **`git push`**（沒有指定 remote）
   - ❌ 預設 remote 可能是 origin
   - 🚨 風險：可能推送到錯誤的 repo

3. **`git push -f origin`**（force push 到公開庫）
   - ❌ 強制推送到公開庫
   - 🚨 可能覆蓋正確的歷史

4. **直接推送到 origin（任何分支）**
   - ❌ 繞過 PR 流程
   - 🚨 失去 Review 機會

### 錯誤範例與後果

| 錯誤指令 | 後果 | 修正方法 |
|----------|------|----------|
| `git push origin main` | 機敏檔案洩露到公開庫 | 立即 revert，重新 push |
| `git push` | 可能推送到錯誤的 repo | 檢查 `git remote -v`，刪除錯誤的推送 |
| `git push -f origin` | 覆蓋公開庫歷史 | 通知團隊，恢復正確歷史 |

---

## ✅ 正確的工作流程範例

### 日常開發流程

```bash
# 1. 修改代碼
vim src/nodriver_tixcraft.py

# 2. 提交變更（使用 /gsave）
/gsave

# 輸入 commit message（會自動分離公開/機敏檔案）
# 範例輸出：
# [1/2] 🔓 PUBLIC: fix date selection logic
# [2/2] 🔒 PRIVATE: update docs/02-development/structure.md

# 3. 推送公開 commits（使用 /gpush）
/gpush

# 4. 推送機敏 commits（使用 /privatepush）
/privatepush

# 5. 驗證推送成功
git log private/main..HEAD
# (應該沒有未推送的 commits)
```

### 發布流程

```bash
# 1. 確保所有變更已提交並推送到私人庫
/gsave
/gpush
/privatepush

# 2. 更新版本號和 CHANGELOG
vim src/version.py
vim CHANGELOG.md

# 3. 提交版本更新
/gsave

# 4. 創建 PR 到公開庫（使用 /publicpr）
/publicpr

# 輸入 PR 標題和描述
# 範例：
# Title: Release v2.5.0 - Add NoDriver support for FamiTicket
# Body: (自動生成的 CHANGELOG 摘要)

# 5. Review PR，確認沒有機敏檔案

# 6. Merge PR

# 7. 創建 Release Tag
/publicrelease
```

---

## 🔍 驗證與檢查

### 推送前檢查清單

**每次推送前必須檢查**：

```bash
# 1. 檢查當前分支
git branch --show-current

# 2. 檢查 remote 設定
git remote -v
# 預期輸出：
# origin  https://github.com/bouob/tickets_hunter.git (fetch)
# origin  https://github.com/bouob/tickets_hunter.git (push)
# private https://github.com/bouob/private-tickets-hunter.git (fetch)
# private https://github.com/bouob/private-tickets-hunter.git (push)

# 3. 檢查未推送的 commits
git log private/main..HEAD --oneline

# 4. 檢查是否有機敏檔案變更
git diff private/main..HEAD --name-only | grep -E "^\.claude/|^docs/|^specs/"

# 5. 檢查 commit 訊息
git log private/main..HEAD --pretty=format:"%s"
```

### 推送後驗證

```bash
# 1. 驗證推送到正確的 remote
git log private/main -1 --oneline

# 2. 檢查 GitHub（私人庫）
# 瀏覽器打開：https://github.com/bouob/private-tickets-hunter

# 3. 確認沒有推送到公開庫（除非使用 /publicpr）
# 瀏覽器打開：https://github.com/bouob/tickets_hunter
# (最新 commit 應該是上次發布的 commit)
```

---

## 🚨 緊急情況處理

### 情況 1：不小心推送到公開庫

**症狀**：
- 執行了 `git push origin main`
- 機敏檔案出現在公開庫

**緊急處理步驟**：

```bash
# 1. 立即 revert 最後一次推送（如果剛推送）
git revert HEAD
git push origin main

# 2. 或者強制回退（如果還沒有人 pull）
git reset --hard HEAD~1
git push -f origin main

# 3. 檢查洩露的機敏資料
# - API keys
# - 密碼
# - 內部文件

# 4. 如果洩露了敏感資料
# - 立即更換 API keys
# - 更新密碼
# - 通知相關人員

# 5. 清理 Git 歷史（如果機敏資料已在歷史中）
git filter-branch --tree-filter 'rm -f path/to/sensitive/file' HEAD
git push -f origin main
```

### 情況 2：推送到錯誤的 remote

**症狀**：
- 執行了 `git push` 但不確定推送到哪裡

**處理步驟**：

```bash
# 1. 檢查推送歷史
git reflog

# 2. 檢查當前 remote 設定
git remote -v

# 3. 檢查預設 remote
git config --get remote.pushDefault

# 4. 如果推送到錯誤的 remote，回退
git push -f <wrong-remote> <branch>:refs/heads/<branch>~1

# 5. 重新推送到正確的 remote
/gpush  # 或 /privatepush
```

### 情況 3：commit 訊息標記錯誤

**症狀**：
- 公開 commit 被標記為 🔒 PRIVATE
- 或者機敏 commit 被標記為 🔓 PUBLIC

**處理步驟**：

```bash
# 1. 修改最後一次 commit 訊息
git commit --amend

# 2. 更新 commit 訊息標記
# 修改為正確的 🔓 PUBLIC 或 🔒 PRIVATE

# 3. 如果已經推送，強制更新
git push -f private main

# 4. 如果是多個 commits，使用 rebase
git rebase -i HEAD~N
# 在編輯器中，將需要修改的 commit 標記為 'reword'
# 保存後逐個修改 commit 訊息
```

---

## 📚 相關文件

- **CLAUDE.md** - 核心要點和快速參考
- **docs/12-git-workflow/dual-repo-workflow.md** - 雙 Repo 工作流程
- **docs/10-project-tracking/changelog_guide.md** - CHANGELOG 指南

---

## 🔐 安全檢查表（每次發布前）

**發布前必須確認**：

- [ ] 所有變更已提交到私人庫
- [ ] CHANGELOG.md 已更新
- [ ] 版本號已更新
- [ ] 沒有 `.claude/` 文件
- [ ] 沒有 `docs/` 私密文件
- [ ] 沒有 `specs/` 文件
- [ ] 沒有 `settings.json`（只有 `settings.json.example`）
- [ ] 所有 commit 訊息都是英文
- [ ] 沒有 🔒 PRIVATE 標記的 commits
- [ ] 測試已通過
- [ ] PR 已創建並 Review

---

## 💡 最佳實踐建議

1. **永遠使用 slash commands**
   - 使用 `/gsave`、`/gpush`、`/privatepush`、`/publicpr`
   - 避免直接使用 `git push`

2. **定期檢查 remote 設定**
   ```bash
   git remote -v
   ```

3. **設定 Git 別名（可選）**
   ```bash
   git config alias.pushprivate "push private main"
   git config alias.checkremote "remote -v"
   ```

4. **使用 pre-push hook（可選）**
   ```bash
   # .git/hooks/pre-push
   #!/bin/bash
   # 檢查是否推送到 origin
   if [[ "$1" == *"tickets_hunter.git"* ]]; then
     echo "ERROR: Direct push to public repo is forbidden!"
     echo "Use /publicpr instead."
     exit 1
   fi
   ```

5. **定期備份私人庫**
   ```bash
   git clone --mirror https://github.com/bouob/private-tickets-hunter.git
   ```

---

## 📞 問題與支援

如果遇到 Git 推送問題：

1. 查閱本文檔的「緊急情況處理」區塊
2. 查閱 `docs/12-git-workflow/dual-repo-workflow.md`
3. 使用 `/debug` 指令診斷問題
4. 聯繫專案維護者

---

**最後更新**: 2025-11-09
**維護者**: Project Team
**狀態**: ACTIVE
