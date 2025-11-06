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

## 執行推送

確認以下操作：

1. **檢查本地變更** - 確保私人檔案已正確修改
2. **強制加入私人檔案** - 覆蓋 `.gitignore` 規則
3. **提交變更** - 使用清晰的提交訊息
4. **推送到私人 repos** - 只推送到 `private` remote

### 執行命令

```bash
cd "$(git rev-parse --show-toplevel)"

echo "=== 私人檔案推送流程 ==="
echo ""
echo "1️⃣ 檢查本地變更..."
git status

echo ""
echo "2️⃣ 強制加入私人檔案..."
git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ FAQ/

echo ""
echo "3️⃣ 提交變更..."
git commit -m "docs: update private documentation and configuration" || echo "⚠️ 無新變更需要提交"

echo ""
echo "4️⃣ 推送到私人 repos..."
git push private main

echo ""
echo "✅ 私人檔案推送完成！"
echo ""
echo "驗證："
git log --oneline -3
```

---

## 注意事項

### 避免推送到公開 repos

**永遠不要執行這些命令推送私人檔案到公開 repos：**

```bash
# ❌ 不要這樣做
git push origin main                    # 會跳過私人檔案
git push                                # 預設推送可能包含私人檔案

# ✅ 應該這樣做
git push private main                   # 只推送到私人 repos
git push origin main                    # 推送公開程式碼到公開 repos
```

### Remote 設定檢查

```bash
# 確認兩個 remote 都已設定
git remote -v

# 應該顯示：
# origin    https://github.com/bouob/tickets_hunter.git (fetch/push)
# private   https://github.com/bouob/private-tickets-hunter.git (fetch/push)
```

---

## 故障排除

### 問題：檔案未被加入

**解決方案：** 檢查 `.gitignore` 是否阻止了這些檔案

```bash
git check-ignore -v .claude/ docs/ specs/
```

### 問題：推送失敗

**解決方案：** 確認私人 repos 的認證

```bash
git remote -v
# 如果 URL 不正確，重新設定：
git remote set-url private https://github.com/bouob/private-tickets-hunter.git
```

### 問題：推送了敏感檔案到公開 repos

**緊急恢復：**

```bash
# 移除最後一個 commit（謹慎使用！）
git reset --soft HEAD~1
git push origin main --force-with-lease

# 然後聯絡 GitHub 支援刪除推送歷史
```

---

## 檢查清單

在執行 `/privatepush` 之前：

- [ ] 確認在正確的專案目錄
- [ ] 確認沒有未提交的公開代碼變更
- [ ] 確認私人 repos remote 已設定
- [ ] 檢查是否有新的私人檔案需要推送
- [ ] 確認提交訊息清晰明確

---

## 相關命令

- `/gpush` - 推送公開代碼到公開 repos
- `/gsave` - 保存並提交所有變更
- `/gdefault` - 清除本地敏感設定

