---
description: "只推送機敏檔案到私人 repo"
model: haiku
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 推送機敏檔案到私人 Repo

推送機敏檔案（內部文件、設定）到私人倉庫，確保不洩露到公開 repo。

**目標**: `private` remote（私人 repo）
**推送內容**: 機敏檔案 commits（帶 🔒 PRIVATE 標記）

---

## ⚠️ 機敏檔案清單

以下檔案**僅推送到私人 repo**：

```
.claude/          - Claude 自動化設定
CLAUDE.md         - 專案開發規範
docs/             - 技術文件和指南
.specify/         - 規格模板和指令碼
specs/            - 功能規格和設計文件
FAQ/              - 常見問題解答
```

---

## 📝 執行流程

### 步驟 1 - 檢測 PRIVATE Commits

**優先檢查**: 是否有未推送的 PRIVATE commits

```bash
# 檢查本地 commits
git log private/main..HEAD --oneline

# 過濾 PRIVATE commits
git log private/main..HEAD --format=%B | grep "🔒 PRIVATE COMMIT"
```

**兩種模式**:

**模式 A - 推送現有 PRIVATE commits**（優先）:
- 檢測到未推送的 PRIVATE commits
- 直接推送這些 commits
- 無需重新 commit

**模式 B - 手動建立 PRIVATE commit**（回退）:
- 無現有 PRIVATE commits
- 使用 `git add -f` 強制加入機敏檔案
- 建立新的 PRIVATE commit

### 步驟 2 - 執行推送

**模式 A 流程**:
```
✅ 找到 1 個未推送的 PRIVATE commit
📝 Commit: docs(private): update internal documentation

詢問: 「確定推送此 PRIVATE commit 到 private repo？(y/N)」
執行: git push private main
```

**模式 B 流程**:
```
⚠️ 無未推送的 PRIVATE commits

詢問: 「是否手動建立 PRIVATE commit？(y/n)」

若選擇 y:
1. 強制加入機敏檔案
   git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ FAQ/

2. 建立 PRIVATE commit
   git commit -m "📝 docs(private): update private documentation

   🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

   Files modified:
     - [列出變更檔案]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚠️  FILTER MARKER FOR /publicpr ⚠️
   Private file patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, FAQ/
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

3. 推送到 private
   git push private main
```

### 步驟 3 - 驗證推送結果

```bash
# 顯示最近 commits
git log --oneline -3

# 顯示分支追蹤
git branch -vv | grep main

# 確認推送成功
✅ 機敏檔案推送完成！
```

---

## ⚠️ 安全機制

### URL 驗證（必須通過）

執行前必須驗證 private remote URL:

```bash
# 顯示 private remote URL
git remote get-url private

# 預期 URL（擇一）:
✓ https://github.com/bouob/private-tickets-hunter.git
✓ git@github.com:victor/private-tickets-hunter.git

詢問: 「確認目標 URL 正確無誤？(y/N)」
若回覆 N → 取消推送
```

### 最終確認

所有推送前必須明確確認:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  最終確認：即將推送機敏檔案
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

推送目標: https://github.com/bouob/private-tickets-hunter.git
分支: main

機敏檔案列表:
  ✓ .claude/
  ✓ CLAUDE.md
  ✓ docs/
  ✓ .specify/
  ✓ specs/
  ✓ FAQ/

安全保證:
  ✓ 只推送到私人 repo (private remote)
  ✓ 不會推送到公開 repo (origin)
  ✓ 公開 repo 受 .gitignore 保護

最終確認: 執行推送？(y/N)
```

---

## 💡 使用場景

### 場景 1: /gsave 後推送（推薦）

```bash
# 修改程式碼 + 內部文件
/gsave
# → 建立 2 個 commits:
#    Commit 1: ✨ feat(nodriver): add feature X (公開)
#    Commit 2: 📝 docs(private): update docs (機敏)

/gpush
# → 推送 Commit 1 到 private

/privatepush
# → 檢測到 Commit 2（PRIVATE 標記）
# → 推送 Commit 2 到 private
```

### 場景 2: 手動修改機敏檔案

```bash
# 手動編輯 docs/02-development/structure.md
# 手動編輯 CLAUDE.md

/privatepush
# → 無現有 PRIVATE commits
# → 詢問是否手動建立
# → 使用 git add -f + commit + push
```

### 場景 3: 補推遺漏的機敏檔案

```bash
# 忘記推送 .claude/ 變更

/privatepush
# → 檢測機敏檔案變更
# → 建立 PRIVATE commit
# → 推送到 private
```

---

## 🚨 故障排除

### 問題 1: Private Remote 未設定

**症狀**: `fatal: 'private' does not appear to be a 'git' repository`

**解決方案**:
```bash
git remote add private https://github.com/bouob/private-tickets-hunter.git
```

### 問題 2: 推送失敗（認證錯誤）

**症狀**: `fatal: Authentication failed`

**解決方案**:
```bash
# 檢查 remote URL
git remote -v

# 確認 GitHub 認證（SSH key 或 token）
git remote set-url private https://github.com/bouob/private-tickets-hunter.git
```

### 問題 3: 誤推到公開 repo

**症狀**: 機敏檔案被推送到 origin

**緊急恢復**:
```bash
# 1. 移除最後一個 commit
git reset --soft HEAD~1

# 2. 移除機敏檔案
git rm --cached .claude/ docs/ .specify/ specs/ FAQ/ CLAUDE.md

# 3. 重新提交（不含機敏檔案）
git commit -m "docs: remove sensitive files from public repo"

# 4. 強制推送（小心使用！）
git push origin main --force-with-lease

# 5. 聯絡 GitHub 支援清除 push 歷史
```

---

## 📚 相關指令

- `/gsave` - 提交變更（自動分離公開/機敏）
- `/gpush` - 推送公開 commits
- `/publicpr` - 建立 PR 到公開 repo
- `/gdefault` - 清除本地敏感設定

---

## 檢查清單

執行 `/privatepush` 之前:

- [ ] 確認在正確的專案目錄（`tickets_hunter/`）
- [ ] 確認 private remote 已設定（`git remote -v`）
- [ ] 確認 private remote 指向正確的私人 repo
- [ ] 確認沒有未提交的公開代碼變更
- [ ] 檢查是否有新的機敏檔案需要推送
- [ ] 再次確認推送目標是 `private`，不是 `origin`

---

## 延伸閱讀

- **工作流程**: `docs/11-git-workflow/dual-repo-workflow.md`
- **專案憲章**: `.specify/memory/constitution.md` 第 IX 條

$ARGUMENTS
