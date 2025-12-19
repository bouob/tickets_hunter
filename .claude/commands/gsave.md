---
description: "產生英文 emoji 版 Git commit 訊息並提交變更"
model: opus
allowed-tools: ["Bash", "Read", "Grep"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---
# 自動產生英文 emoji Git commit 訊息並提交

---

## 📜 Git 提交規範（遵循專案憲章第 IX 條）

本指令遵循專案憲章的 Git 提交規範，詳見：`.specify/memory/constitution.md`

### 提交訊息格式

```
emoji type(scope): subject

body (optional)
```

### Type 列表

| Type | Emoji | 說明 |
|------|-------|------|
| `feat` | ✨ | 新功能 |
| `fix` | 🐛 | 錯誤修復 |
| `docs` | 📝 | 文件更新 |
| `refactor` | ♻️ | 重構 |
| `perf` | ⚡ | 效能改善 |
| `chore` | 🔧 | 維護工作 |

### Scope 清單

**平台**：`tixcraft`, `kktix`, `ibon`, `ticketplus`, `kham`, `famiticket`, `cityline`, `hkticketing`

**模組**：`nodriver`, `ocr`, `util`, `config`, `webhook`, `ui`

**其他**：`ci`, `build`, `release`, `private`

---

## ⚠️ 重要提醒

**執行前建議先執行 `/gdefault`** 清除本地敏感設定檔案。

**版本更新請使用 `/gupdate`**，本指令不處理版本號。

---

## 執行步驟

### 1. 檢查 .gitignore 並排除忽略檔案

- 讀取 `.gitignore` 檔案內容
- 執行 `git status --porcelain` 取得所有變更檔案
- 過濾掉 `.gitignore` 中的忽略檔案（settings.json、*.log 等）
- 如果所有變更都被忽略，提示無檔案需要提交

### 2. 分離公開與機敏檔案

**機敏檔案清單**：
```
.claude/          - Claude 自動化設定
CLAUDE.md         - 專案開發規範
docs/             - 技術文件和指南
.specify/         - 規格模板和指令碼
specs/            - 功能規格和設計文件
.temp/            - 臨時測試資料
```

**分離規則**：
- **公開檔案**：src/, README.md, CHANGELOG.md, .github/, guide/, build_scripts/ 等
- **機敏檔案**：上述清單中的檔案

**分組策略**：
- 同時有公開和機敏檔案 → 建立 2 個 commits
- 只有公開檔案 → 建立 1 個 commit
- 只有機敏檔案 → 建立 1 個 commit（PRIVATE 標記）

### 3. 產生 commit 訊息

**3.1 公開檔案 Commit**（標準格式）：
```
✨ feat(nodriver): implement auto ticket selection

- Add date selection function
- Add area selection function
```

**3.2 機敏檔案 Commit**（PRIVATE 標記）：
```
📝 docs(private): update internal documentation

🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

Files modified:
  - .claude/commands/gsave.md
  - docs/02-development/structure.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FILTER MARKER FOR /publicpr ⚠️
Private patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, .temp/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. 執行提交

**4.1 先提交公開檔案**（如果有）：
```bash
git add [公開檔案清單]
git commit -m "[標準訊息]"
```

**4.2 後提交機敏檔案**（如果有）：
```bash
git add -f .claude/ CLAUDE.md docs/ .specify/ specs/ .temp/
git commit -m "[PRIVATE 標記訊息]"
```

**提交順序重要性**：
- ✅ 先公開後機敏：方便 `/publicpr` cherry-pick
- ✅ 機敏檔案獨立：便於識別和過濾

---

## Commit 訊息範例

### 情境：同時修改程式碼和文件

```bash
# 變更檔案：
# - src/nodriver_tixcraft.py  (公開)
# - docs/structure.md         (機敏)
```

**Commit #1（公開）**：
```
🐛 fix(nodriver): clear legacy SID cookie before setting TIXUISID

- Delete both SID and TIXUISID before setting new cookie
- Fix login conflict issue for upgraded users
```

**Commit #2（機敏）**：
```
📝 docs(private): update structure documentation

🔒🔒🔒 PRIVATE COMMIT - DO NOT PUSH TO PUBLIC REPO 🔒🔒🔒

Files modified:
  - docs/02-development/structure.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FILTER MARKER FOR /publicpr ⚠️
Private patterns: .claude/, docs/, CLAUDE.md, .specify/, specs/, .temp/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 標準工作流程

```bash
/gdefault       # 1. 清除敏感設定
/gupdate        # 2. 更新版本（如需要）
/gsave          # 3. 分離提交（最多 2 commits）
/gpush          # 4. 推送到私人庫
```

---

## 📚 相關指令

- `/gdefault` - 清除敏感設定檔案
- `/gupdate` - 更新版本號
- `/gpush` - 推送到私人庫
- `/publicpr` - 建立 PR 到公開庫

$ARGUMENTS
