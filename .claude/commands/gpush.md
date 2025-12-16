---
description: "推送所有 commits 到私人 repo（完整備份）"
allowed-tools: ["Bash", "Read", "Grep", "AskUserQuestion"]
model: opus
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 推送所有 Commits 到私人 Repo

推送本地所有 commits 到私人倉庫 (private remote)，不過濾任何內容。

**目標**: `private` remote（私人 repo）

**推送內容**:
- ✅ **所有 commits**（包括公開代碼、內部文件、機敏內容）
- ✅ 不跳過任何 commit
- 📝 Private repo 是完整備份，包含專案所有歷史記錄

**與 `/publicpr` 的區別**:
- `/gpush` → `private` repo（推送**所有**內容，完整備份）
- `/publicpr` → `origin` 公開 repo（嚴格過濾機敏內容）

---

## 🔧 選項

- `--dry-run`: 預覽模式
- `--auto-merge`: 合併多個 commits
- `--force`: 強制推送（⚠️ 危險）

---

## 📝 執行流程

### 前置檢查

**建議工作流程**:
```bash
/gupdate  # 更新版本號
/gchange  # 更新 CHANGELOG
/gsave    # 提交變更（自動分離公開/機敏）
/gpush    # 推送公開 commits
```

1. **版本號確認**: 檢查 `CONST_APP_VERSION` 是否已更新
2. **CHANGELOG 確認**: 詢問是否已執行 `/gchange`

### 步驟 1 - 檢查待推送 Commits

**檢查本地 commits**:
```bash
git log private/main..HEAD --oneline
```

**顯示分析結果**:
```
🔍 分析 commits...
✅ 找到 7 個 commits（包括公開、內部文件、機敏內容）
📤 將推送所有 commits 到 private repo
```

**注意**: `/gpush` 不進行任何過濾，所有 commits 都會推送到私人庫。

### 步驟 2 - Commit 合併（可選）

**觸發條件**: 超過 2 個 commits

**詢問**: 「是否合併為單一 commit？(y/n)」
- **y**: 使用 `git reset --soft private/main` + 重新 commit
- **n**: 維持原有 commits

### 步驟 3 - 推送確認

**檢查分支保護**:
```bash
git push private main --dry-run
```

**推送選項**:

1. **直接推送**（無保護）
   - 詢問: 「確定推送到 private main？(y/N)」
   - 執行: `git push private main`

2. **PR 工作流程**（有保護）
   - 建立 feature branch: `feature/auto-commits-YYYY-MM-DD`
   - 推送並建立 PR
   - 選項 `--auto-merge-pr`: 自動設定 auto-merge

3. **Force 推送**（⚠️ 危險）
   - 需三次確認
   - 執行: `git push --force-with-lease private main`

---

## ⚠️ 執行約束

### 必須確認的步驟

1. **推送確認**: 必須使用者明確回覆 "y"
2. **Force 推送**: 需三次確認

### 自動中止條件

- 使用者回覆 "N" 或 "n"
- 版本號未更新（選擇 "n"）
- CHANGELOG 未更新（選擇 "n"）
- 分支保護衝突（選擇取消）

---

## 💡 範例

### 標準推送流程

```bash
# 情境：修改了 src/nodriver_tixcraft.py 和 README.md

/gsave
# → 建立 1 個公開 commit（src/, README.md）

/gpush
# → 分析: 找到 1 個公開 commit
# → 推送到 private main
```

### 混合檔案推送流程

```bash
# 情境：修改了程式碼 + 內部文件

/gsave
# → 建立 2 個 commits:
#    Commit 1: ✨ feat(nodriver): add feature X
#    Commit 2: 📝 docs(private): update internal docs

/gpush
# → 分析: 找到 2 個 commits
# → 推送: 所有 2 個 commits 到 private（不過濾）
```

### 合併推送流程

```bash
# 情境：累積了 5 個小 commits

/gpush --auto-merge
# → 分析: 找到 5 個公開 commits
# → 詢問: 是否合併？
# → 合併為單一 commit
# → 推送到 private
```

---

## 📚 相關指令

- `/gsave` - 提交變更（自動分離公開/機敏）
- `/publicpr` - 建立 PR 到公開 repo（會過濾機敏內容）
- `/publicrelease` - 建立 Release Tag 到公開 repo（PR merge 後使用）
- `/gupdate` - 更新版本號
- `/gchange` - 更新 CHANGELOG

---

## 延伸閱讀

- **工作流程**: `docs/11-git-workflow/dual-repo-workflow.md`
- **專案憲章**: `.specify/memory/constitution.md` 第 IX 條
- **Git 提交規範**: [Conventional Commits](https://www.conventionalcommits.org/)

$ARGUMENTS
