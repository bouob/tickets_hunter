---
description: "推送公開 commits 到私人 repo"
allowed-tools: ["Bash"]
model: sonnet
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 推送公開 Commits 到私人 Repo

推送本地公開 commits 到私人倉庫 (private remote)，自動跳過機敏檔案 commits。

**目標**: `private` remote（私人 repo）
**推送內容**: 僅公開 commits（自動過濾 PRIVATE 標記）
**機敏檔案**: 使用 `/privatepush` 單獨推送

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

### 步驟 1 - 分析與過濾 Commits

**檢查本地 commits**:
```bash
git log private/main..HEAD --oneline
```

**過濾規則**（依序執行）:

1. **識別 PRIVATE 標記**（優先）
   - 檢查 commit 訊息: `🔒 PRIVATE COMMIT` 或 `FILTER MARKER FOR /publicpr`
   - 若包含 → 跳過此 commit（留給 `/privatepush`）

2. **檢查 .gitignore 檔案**（一般 commits）
   - 讀取 `.gitignore` 規則
   - 比對 commit 變更檔案
   - 過濾包含被忽略檔案的 commits

**顯示過濾結果**:
```
🔍 分析 commits...
✅ 找到 5 個 commits
🔒 跳過 1 個 PRIVATE commit
⚠️ 過濾 1 個包含 .gitignore 檔案的 commit
✅ 剩餘 3 個公開 commits 將被推送
```

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

### 步驟 4 - Release Tag（可選）

**詢問**: 「是否建立 Release Tag？(y/n/skip)」

**流程**（若選擇 y）:
1. 提取版本號: `CONST_APP_VERSION`
2. 格式化 tag: `v2025.11.04`
3. 提取 CHANGELOG 內容
4. 建立 annotated tag: `git tag -a v2025.11.04 -m "[message]"`
5. 推送 tag: `git push private main --tags`

---

## ⚠️ 執行約束

### 必須確認的步驟

1. **推送確認**: 必須使用者明確回覆 "y"
2. **Force 推送**: 需三次確認
3. **Tag 建立**: 需最終確認

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
# → 過濾: 跳過 Commit 2（PRIVATE 標記）
# → 推送: 僅 Commit 1 到 private

/privatepush
# → 推送: Commit 2 到 private
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
- `/privatepush` - 推送機敏檔案
- `/publicpr` - 建立 PR 到公開 repo
- `/gupdate` - 更新版本號
- `/gchange` - 更新 CHANGELOG

---

## 延伸閱讀

- **工作流程**: `docs/11-git-workflow/dual-repo-workflow.md`
- **專案憲章**: `.specify/memory/constitution.md` 第 IX 條
- **Git 提交規範**: [Conventional Commits](https://www.conventionalcommits.org/)

$ARGUMENTS
