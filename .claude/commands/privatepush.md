---
description: "推送私人檔案到私人 repos，避免推送到公開 repos"
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 私人檔案推送指令

強制推送私人檔案（文件、設定、規格）到私人 repos，確保不會意外洩露到公開 repos。

---

## ⚠️ 私人檔案清單

**以下目錄和檔案僅推送到私人 repos：**

```
.claude/          - Claude 自動化設定
CLAUDE.md         - 專案開發規範
docs/             - 技術文件和指南
.specify/         - 規格模板和指令碼
specs/            - 功能規格和設計文件
FAQ/              - 常見問題解答
```

**重要警告：** 這些檔案包含：
- 內部開發流程和工具設定
- 專案架構和技術決策
- 私人功能規格
- 可能的敏感資訊

---

## 📋 前置條件檢查

在執行推送前，必須確認以下設定：

### 1. Private Remote 已設定

```bash
git remote get-url private
# 應該顯示：https://github.com/bouob/private-tickets-hunter.git
# 或 SSH：git@github.com:victor/private-tickets-hunter.git
```

**如果未設定，執行：**

```bash
# HTTPS 版本（推薦）
git remote add private https://github.com/bouob/private-tickets-hunter.git

# SSH 版本
git remote add private git@github.com:victor/private-tickets-hunter.git
```

### 2. 確認兩個 Remote 都已設定

```bash
git remote -v

# 應該顯示：
# origin    https://github.com/bouob/tickets_hunter.git (fetch)
# origin    https://github.com/bouob/tickets_hunter.git (push)
# private   https://github.com/bouob/private-tickets-hunter.git (fetch)
# private   https://github.com/bouob/private-tickets-hunter.git (push)
```

---

## 🔐 執行推送 (安全模式)

### 完整流程（包含多層驗證）

```bash
cd "$(git rev-parse --show-toplevel)"

echo "=== 私人檔案推送流程 ==="
echo ""
echo "🔐 安全檢查開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 0️⃣ 驗證 private remote 設定
echo "0️⃣ 驗證 private remote 設定..."
if ! git remote get-url private > /dev/null 2>&1; then
  echo "❌ 錯誤：private remote 未設定！"
  echo ""
  echo "請先執行以下命令設定私人 repos："
  echo "  git remote add private https://github.com/bouob/private-tickets-hunter.git"
  echo ""
  echo "或如果使用 SSH："
  echo "  git remote add private git@github.com:victor/private-tickets-hunter.git"
  exit 1
fi

PRIVATE_URL=$(git remote get-url private)
echo "✅ private remote 已設定"
echo "   URL: $PRIVATE_URL"
echo ""

# 🔐 關鍵檢查：驗證目標 URL（必須通過）
echo "🔐 驗證私人 repos 目標..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  關鍵確認：驗證推送目標"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "檢測到的私人 repos URL："
echo "  $PRIVATE_URL"
echo ""
echo "預期的私人 repos URL："
echo "  ✓ https://github.com/bouob/private-tickets-hunter.git"
echo "  ✓ git@github.com:victor/private-tickets-hunter.git"
echo ""
echo "❌❌❌ 如果 URL 不符合上述任何一個，請勿繼續！❌❌❌"
echo ""
read -p "確認目標 URL 正確無誤？(y/N) " url_confirm
if [[ ! "$url_confirm" =~ ^[Yy]$ ]]; then
  echo ""
  echo "❌ URL 驗證失敗！已取消推送"
  echo ""
  echo "檢查當前 remote 設定："
  echo "  git remote -v"
  echo ""
  echo "修正 remote URL："
  echo "  git remote set-url private <正確的URL>"
  exit 1
fi

echo ""
echo "✅ 目標 URL 驗證通過 - 可以繼續"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣ 檢查本地變更..."
git status

echo ""
echo "2️⃣ 強制加入私人檔案..."
echo "   ⚠️  將會推送以下敏感檔案到私人 repos："
echo "   - .claude/     (Claude 自動化設定)"
echo "   - CLAUDE.md    (開發規範文件)"
echo "   - docs/        (技術文件和指南)"
echo "   - .specify/    (規格模板和指令碼)"
echo "   - specs/       (功能設計規格)"
echo "   - FAQ/         (常見問題解答)"
echo ""
git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ FAQ/

echo ""
echo "3️⃣ 提交變更..."
git commit -m "docs: update private documentation and configuration" || echo "⚠️ 無新變更需要提交"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  最終確認：即將推送敏感檔案"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "推送目標："
echo "  Remote：$PRIVATE_URL"
echo "  分支：main (設定追蹤)"
echo ""
echo "敏感檔案列表："
echo "  ✓ .claude/"
echo "  ✓ CLAUDE.md"
echo "  ✓ docs/"
echo "  ✓ .specify/"
echo "  ✓ specs/"
echo "  ✓ FAQ/"
echo ""
echo "安全保證："
echo "  ✓ 只推送到私人 repos (private remote)"
echo "  ✓ 不會推送到公開 repos (origin)"
echo "  ✓ 公開 repos 受 .gitignore 保護"
echo ""
read -p "最終確認：執行推送？(y/N) " final_confirm
if [[ ! "$final_confirm" =~ ^[Yy]$ ]]; then
  echo ""
  echo "❌ 已取消推送"
  exit 0
fi

echo ""
echo "4️⃣ 推送到私人 repos..."
git push -u private main

echo ""
echo "✅ 私人檔案推送完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "驗證推送結果"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "最近 commits："
git log --oneline -3
echo ""
echo "分支追蹤設定："
git branch -vv | grep main
echo ""
echo "✅ 推送成功！"
```

---

## 快速推送（已驗證設定後）

如果你已經確認 private remote 設定無誤，可以簡化版本：

```bash
git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ FAQ/
git commit -m "docs: update private documentation and configuration" || true
git push -u private main
```

---

## 注意事項

### ✅ 應該執行的命令

```bash
git push private main                   # 只推送到私人 repos
git push -u private main                # 設定追蹤並推送
git push origin main                    # 推送公開程式碼到公開 repos
```

### ❌ 不要執行

```bash
git push                                # 預設可能推送到 origin 或 private
git push origin main                    # 絕不推送私人檔案到公開 repos（已由 .gitignore 防護）
git push origin --all                   # 推送所有分支，包括私人內容
```

---

## 故障排除

### 問題 1：Remote 未設定

**症狀：** 執行時出現 `fatal: 'private' does not appear to be a 'git' repository`

**解決方案：**

```bash
git remote add private https://github.com/bouob/private-tickets-hunter.git
```

### 問題 2：推送失敗（認證錯誤）

**症狀：** 出現 `fatal: Authentication failed`

**解決方案：**

```bash
# 檢查 remote URL
git remote -v

# 確認 GitHub 認證已設定（SSH key 或 token）
# 或使用正確的 HTTPS URL 與認證
git remote set-url private https://github.com/bouob/private-tickets-hunter.git
```

### 問題 3：推送了敏感檔案到公開 repos

**症狀：** 私人檔案被推送到 origin

**緊急恢復：**

```bash
# 1. 移除最後一個 commit
git reset --soft HEAD~1

# 2. 移除敏感檔案
git rm --cached .claude/ docs/ .specify/ specs/ FAQ/ CLAUDE.md

# 3. 重新提交（不含敏感檔案）
git commit -m "docs: remove sensitive files from public repo"

# 4. 強制推送（小心使用！）
git push origin main --force-with-lease

# 5. 聯絡 GitHub 支援清除 push 歷史
```

---

## 檢查清單

執行 `/privatepush` 之前：

- [ ] 確認在正確的專案目錄（`tickets_hunter/`）
- [ ] 確認 private remote 已設定（`git remote -v`）
- [ ] 確認 private remote 指向正確的私人 repos
- [ ] 確認沒有未提交的公開代碼變更
- [ ] 檢查是否有新的私人檔案需要推送
- [ ] 確認提交訊息清晰明確
- [ ] 再次確認推送目標是 `private`，不是 `origin`

---

## 相關命令

- `/gpush` - 推送公開代碼到公開 repos
- `/gsave` - 保存並提交所有變更
- `/gdefault` - 清除本地敏感設定
- `/gchange` - 生成 CHANGELOG

---

## 設定持久化

如果想自動追蹤 private 分支，可以一次性執行：

```bash
# 設定 main 分支追蹤 private/main
git branch -u private/main main

# 驗證
git branch -vv
# 應該顯示：main -> private/main
```

這樣下次推送時，可以直接用 `git push` 而不用指定 remote。
