---
description: "根據可用的設計產物，將現有任務轉換為可執行、依相依性排序的 GitHub issues。"
model: opus
tools: ['github/github-mcp-server/issue_write']
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## 使用者輸入

```text
$ARGUMENTS
```

您 **必須** 在繼續之前考量使用者輸入（如非空白）。

## 大綱

1. 從儲存庫根目錄執行 `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`，並解析 FEATURE_DIR 和 AVAILABLE_DOCS 清單。所有路徑必須為絕對路徑。對於參數中的單引號（如 "I'm Groot"），使用跳脫語法：例如 'I'\''m Groot'（或盡可能使用雙引號："I'm Groot"）。
1. 從執行的腳本中，擷取 **tasks** 的路徑。
1. 執行以下指令取得 Git remote：

```bash
git config --get remote.origin.url
```

**僅在 REMOTE 是 GITHUB URL 時才繼續下一步驟**

1. 對於清單中的每個任務，使用 GitHub MCP 伺服器在代表 Git remote 的儲存庫中建立新的 issue。

**在任何情況下絕對不要在與 REMOTE URL 不匹配的儲存庫中建立 issues**
