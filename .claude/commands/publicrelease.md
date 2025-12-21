---
description: "在公開 repo PR merge 後建立 Release Tag 並觸發 GitHub Actions"
model: opus
allowed-tools: ["Bash", "Read", "Grep", "AskUserQuestion"]
---

## 使用者輸入

```text
$ARGUMENTS
```

---

# 公開 Repo Release 建立指令

在 PR merge 到 origin/main 後，建立 Release Tag 並觸發 GitHub Actions 自動打包發布。

## 進階選項

- `--version=<version>`: 手動指定版本號
- `--dry-run`: 預覽模式
- `--skip-wait`: 跳過監視打包狀態
- `--timeout=<minutes>`: 監視超時時間（預設 10 分鐘）

---

## 執行流程

### 步驟 0 - 前置檢查

1. `git remote -v` 確認 remote 設定
2. 詢問「PR 已 merge 完成，確定要建立 Release Tag？(y/n)」

### 步驟 1 - 切換到 Origin Main

```bash
git fetch origin
git checkout -B release-temp origin/main
git log -1  # 確認是剛 merge 的 commit
```

### 步驟 2 - 提取版本號

```bash
VERSION=$(grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | grep -oP '"\K[^"]+' | head -1)
# 格式：YYYY.MM.DD（例如：2025.11.07）
```

### 步驟 3 - 檢查 Tag 是否已存在

```bash
git ls-remote --tags origin "refs/tags/v${VERSION}*"
```

**如果 Tag 已存在**，自動使用修訂版本號：
- 基礎版本：`2025.11.12`
- 第一次重發：`2025.11.12.1`
- 第二次重發：`2025.11.12.2`

### 步驟 4 - 提取 CHANGELOG 內容

```bash
sed -n '/## 2025.11.07/,/## /p' CHANGELOG.md | sed '$ d' | tail -n +2
```

如果未找到，使用預設 release notes。

### 步驟 5 - 預覽並確認

顯示 Tag 預覽（Tag Name、Target、Message），詢問「確認建立此 Release Tag？(y/n)」

### 步驟 6 - 建立 Tag

```bash
TAG_MESSAGE="Release ${VERSION}"
git tag -a v${VERSION} -m "${TAG_MESSAGE}"
```

### 步驟 7 - 推送 Tag

```bash
git push origin v${VERSION}
```

### 步驟 8 - 監視打包狀態

等待 GitHub Actions 開始（10-15 秒），每 30 秒檢查一次：

```bash
RUN_ID=$(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run view $RUN_ID --json status,conclusion
```

**打包成功** → 執行：
```bash
gh release edit v${VERSION} --draft=false --prerelease --latest=false
```

**打包失敗** → 顯示錯誤日誌連結

**超時** → 提示手動檢查

如果使用 `--skip-wait`，跳過此步驟並提示手動發布指令。

### 步驟 9 - 清理

```bash
git checkout main
git branch -D release-temp
```

顯示完成訊息和 Release 連結。

---

## 執行約束

**必須確認**：PR 已 Merge、Tag 資訊

**自動中止**：PR 未 merge、版本號格式錯誤、使用者回覆 n、Git 執行失敗

---

## 重要說明

- Tag 僅存在於 public repo（不同步回 private）
- Tag message 使用英文：`Release ${VERSION}`
- 打包完成後自動發布為 **Pre-release**

$ARGUMENTS
