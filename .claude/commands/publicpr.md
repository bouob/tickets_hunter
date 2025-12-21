---
description: "從私人 repo 建立安全 PR 到公開 repo，自動過濾機敏檔案"
model: opus
allowed-tools: ["Bash", "Read", "Grep", "AskUserQuestion"]
---

## 使用者輸入

```text
$ARGUMENTS
```

---

# 公開 Repo PR 建立指令

從 private repo 建立 PR 到 origin repo，自動過濾機敏檔案。使用**版本號比對**判斷是否需要發布，永遠使用 **Squash Merge** 策略。

## 機敏檔案清單（自動過濾）

```
.claude/          - Claude 自動化設定
CLAUDE.md         - 專案開發規範
docs/             - 技術文件和指南
.specify/         - 規格模板和指令碼
specs/            - 功能規格和設計文件
.temp/            - 臨時測試資料
src/assets/model/ - OCR 模型檔案
```

## 進階選項

- `--dry-run`: 預覽模式
- `--base-branch=<branch>`: 指定基礎分支（預設：main）
- `--auto-merge`: 建立 PR 後自動設定 auto-merge

---

## 執行流程

### 步驟 0 - 前置檢查

1. `git remote -v` 確認存在 `origin` 和 `private`
2. 顯示目標 URL，詢問「確認目標 repo 正確？(y/n)」

### 步驟 1 - 取得最新狀態

```bash
git fetch origin && git fetch private
```

### 步驟 1.5 - 版本比對

```bash
ORIGIN_VERSION=$(git show origin/main:src/nodriver_tixcraft.py | grep "CONST_APP_VERSION" | head -1)
LOCAL_VERSION=$(grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1)
```

- **版本相同** → 提示執行 `/gupdate`，結束
- **版本不同** → 繼續 Squash Merge 流程

### 步驟 2 - 分析檔案變更

```bash
SENSITIVE_PATTERNS=".claude/|^docs/|^CLAUDE.md|^.specify/|^specs/|^.temp/|^src/assets/model/"
git diff origin/main..HEAD --name-status | grep -Ev "$SENSITIVE_PATTERNS"
```

顯示：新增/修改/刪除檔案統計，詢問「確認推送？(y/n)」

### 步驟 3 - 建立臨時分支

```bash
git checkout -b public-sync-YYYY-MM-DD-HHmm origin/main
git stash push -m "Temp stash for publicpr"  # 如有本地變更
```

### 步驟 4 - 複製檔案變更

```bash
CLEAN_FILES=$(git diff origin/main..HEAD --name-only | grep -Ev "$SENSITIVE_PATTERNS")
echo "$CLEAN_FILES" | while read file; do
  STATUS=$(git diff origin/main..main --name-status | grep "$file" | awk '{print $1}')
  if [ "$STATUS" = "D" ]; then
    git rm "$file"
  else
    git checkout main -- "$file"
    git add "$file"
  fi
done
```

### 步驟 5 - 建立 Squash Commit

從 CHANGELOG 提取功能摘要：
```bash
VERSION=$(grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | grep -oP '"\K[^"]+')
FEATURE_SUMMARY=$(sed -n "/^## $VERSION/,/^## /p" CHANGELOG.md | grep "^- " | head -1 | sed 's/^- //')
git commit -m "chore(release): $VERSION updates - $FEATURE_SUMMARY"
```

### 步驟 6 - 推送並建立 PR

```bash
git push origin public-sync-YYYY-MM-DD-HHmm
git stash pop  # 還原暫存
```

**PR 標題**（英文）：`chore(release): [version] updates - [feature summary]`

**PR 描述**（繁體中文）：
```markdown
## 變更摘要
本次發布使用 Squash Merge 合併了 {time_range} 的所有更新。

### 主要變更
- 新功能: {count} 項
- 錯誤修復: {count} 項

## 統計資訊
- 原始 Commits: {total_commits} 個
- 機敏 Commits: {private_commits} 個（已排除）
- 檔案變更: {files_changed} 個

## 重要提醒
- Public repo 只包含 1 個 squash commit
- Private repo 保留完整 commits
- **發布後不要從 public 拉回變更到 private**（單向流程）
```

建立 PR：
```bash
gh pr create --repo origin --base main --head [branch-name] --title "[標題]" --body "[描述]"
```

如果指定 `--auto-merge`：
```bash
gh pr merge --auto --squash [PR-URL]
```

### 步驟 7 - 清理

1. `git checkout main`
2. 詢問是否刪除臨時分支
3. 顯示 PR URL

---

## 執行約束

**必須確認**：目標 Repo、檔案變更

**自動中止**：版本相同、沒有變更、使用者回覆 n、Git 執行失敗

---

## 重要說明

- 永遠使用 **Squash Merge**（雙庫 history 獨立）
- 發布後**不要從 public 拉回變更**（單向流程）
- PR 描述繁體中文，標題英文

$ARGUMENTS
