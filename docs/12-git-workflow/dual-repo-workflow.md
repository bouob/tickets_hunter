# 雙 Repo 維護工作流程

本文件說明如何同時維護公開 repo (origin) 和私人 repo (private) 的完整工作流程。

---

## 📋 目錄

- [Repo 角色定義](#repo-角色定義)
- [工作流程總覽](#工作流程總覽)
- [日常開發流程](#日常開發流程)
- [發布流程](#發布流程)
- [機敏檔案管理](#機敏檔案管理)
- [緊急修復流程](#緊急修復流程)
- [常見問題排解](#常見問題排解)

---

## Repo 角色定義

### Origin（公開 Repo）

- **URL**: `https://github.com/bouob/tickets_hunter.git`
- **用途**: 公開發布、開源分享、Release 下載
- **內容**: 僅包含程式碼、公開文件（README、CHANGELOG等）
- **限制**: 絕對不包含機敏檔案（開發文件、內部設定等）

### Private（私人 Repo）

- **URL**: `https://github.com/bouob/private-tickets-hunter.git`（範例）
- **用途**: 主力開發、完整文件、內部協作
- **內容**: 包含所有內容（程式碼 + 機敏檔案）
- **特性**: 作為開發的單一真相來源（Single Source of Truth）

---

## 工作流程總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                      雙 Repo 維護流程圖                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  日常開發階段    │
│  (Private Repo) │
└────────┬────────┘
         │
         ├─► /gsave          自動分離公開/機敏檔案為不同 commits
         │                   - 公開 commit（標準格式）
         │                   - 機敏 commit（🔒 PRIVATE 標記）
         │
         ├─► /gpush          推送公開 commits 到 private repo
         │                   - 識別 PRIVATE 標記跳過機敏 commits
         │                   - 僅推送公開 commits
         │
         ├─► /privatepush    推送機敏 commits 到 private repo
         │                   - 優先推送現有 PRIVATE commits
         │                   - 回退：手動建立機敏 commit（git add -f）
         │
         └─► 持續開發...
                 │
                 │ 完成階段性開發
                 ▼
┌─────────────────┐
│   發布階段      │
│  (Public Repo)  │
└────────┬────────┘
         │
         ├─► /publicpr       建立 PR 到 origin（自動過濾機敏 commits）
         │    ├─ 掃描 commits
         │    ├─ 識別 PRIVATE 標記（優先，高效能）
         │    ├─ 檔案掃描（回退，向下相容）
         │    ├─ Cherry-pick 公開 commits
         │    └─ 建立 PR
         │
         ├─► Code Review
         │
         ├─► Merge PR
         │
         └─► Release 🎉
```

---

## 日常開發流程

### 標準流程（推薦）

```bash
# Step 1: 修改檔案（程式碼 + 內部文件）
# 編輯 src/nodriver_ticketplus.py（新功能）
# 編輯 docs/02-development/structure.md（內部文件）
# 編輯 CLAUDE.md（開發規範）

# Step 2: 自動分離提交
/gsave
# 執行流程：
# 1. 分析變更檔案
# 2. 自動排除 .gitignore 中的檔案
# 3. 分離公開與機敏檔案
# 4. 建立兩個 commits：
#    ✨ feat(nodriver): add feature X（公開）
#    📝 docs(private): update internal docs（機敏，🔒 PRIVATE 標記）

# Step 3: 推送公開 commits
/gpush
# 執行流程：
# 1. 檢查本地 commits
# 2. 識別 PRIVATE 標記 → 跳過機敏 commit
# 3. 過濾 .gitignore 檔案
# 4. 推送公開 commits 到 private main

# Step 4: 推送機敏 commits
/privatepush
# 執行流程：
# 1. 檢測未推送的 PRIVATE commits
# 2. 直接推送機敏 commits 到 private main

# 結果：private repo 包含完整變更（公開 + 機敏）
```

### 簡化流程（僅公開檔案）

```bash
# 情境：僅修改程式碼，無內部文件變更

# Step 1: 修改程式碼
# 編輯 src/nodriver_tixcraft.py
# 編輯 tests/test_tixcraft.py

# Step 2: 提交
/gsave
# → 建立 1 個公開 commit

# Step 3: 推送
/gpush
# → 推送公開 commit 到 private

# 無需執行 /privatepush（無機敏檔案變更）
```

### 手動機敏檔案推送

```bash
# 情境：僅修改內部文件，未使用 /gsave

# Step 1: 手動編輯機敏檔案
# 編輯 docs/02-development/structure.md
# 編輯 CLAUDE.md

# Step 2: 直接推送
/privatepush
# 執行流程：
# 1. 檢測無現有 PRIVATE commits
# 2. 詢問是否手動建立 PRIVATE commit
# 3. 使用 git add -f 強制加入
# 4. 建立並推送 PRIVATE commit
```

---

## 發布流程

### 階段性發布到公開 Repo

```bash
# 情境：完成 TicketPlus 支援，準備發布到公開 repo

# Step 1: 確認 private repo 已包含所有變更
git status
# 確保工作目錄乾淨

# Step 2: 使用 /publicpr 建立 PR 到 origin
/publicpr

# 執行流程：
# 1. 確認目標 repo (origin)
# 2. 掃描未推送的 commits
#    範例輸出：
#    ✅ 找到 8 個 commits
#    ⚠️ 發現 3 個 commits 包含機敏檔案（已排除）：
#      - abc1234 docs: update development guide
#      - def5678 chore: update CLAUDE.md
#      - ghi9012 feat: add spec for new feature
#    ✅ 剩餘 5 個有效 commits 將被推送
#
# 3. 預覽檔案變更（排除機敏檔案）
# 4. 確認推送？y
# 5. 建立臨時分支: public-sync-2025-11-07-1430
# 6. Cherry-pick 5 個有效 commits
# 7. 推送到 origin
# 8. 建立 PR: https://github.com/bouob/tickets_hunter/pull/123

# Step 3: Code Review
# 在 GitHub 上檢查 PR 內容

# Step 4: Merge PR
# 使用 GitHub UI 或 gh CLI merge

# Step 5: Release
# 在 origin repo 建立 Release
```

### 預覽模式（推薦）

```bash
# 先預覽不實際推送
/publicpr --dry-run

# 輸出範例：
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 Commit 掃描結果
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ 找到 8 個 commits
# ⚠️ 發現 3 個 commits 包含機敏檔案（已排除）
# ✅ 剩餘 5 個有效 commits 將被推送
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 檔案變更預覽
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 新增檔案 (2):
#   + src/nodriver_ticketplus.py
#   + tests/test_ticketplus.py
# 修改檔案 (5):
#   ~ src/chrome_tixcraft.py
#   ~ README.md
#   ~ CHANGELOG.md
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 Dry-run 模式，不執行實際推送
```

---

## 機敏檔案管理

### 機敏檔案清單

以下檔案/目錄被視為機敏檔案，**不會**出現在公開 repo 中：

```
.claude/          - Claude 自動化設定（slash commands、hooks）
CLAUDE.md         - 專案開發規範、內部指引
docs/             - 技術文件和開發指南
.specify/         - 規格模板和指令碼（speckit 相關）
specs/            - 功能規格和設計文件
FAQ/              - 常見問題解答（可能包含內部資訊）
```

### .gitignore 設定

確保 `.gitignore` 包含以下規則：

```gitignore
# 機敏檔案
.claude/
CLAUDE.md
/docs/
.specify/
specs/
FAQ/

# 測試相關
MAXBOT_INT28_IDLE.txt
src/MAXBOT_INT28_IDLE.txt
.temp/

# 環境相關
.env
*.log
```

### 機敏檔案的自動保護

1. **`/gsave` 指令**：
   - 自動讀取 `.gitignore`
   - 排除被忽略的檔案
   - 僅提交應該版控的檔案

2. **`/gpush` 指令**：
   - 檢查 commits 中的檔案
   - 過濾包含被忽略檔案的 commits
   - 僅推送乾淨的 commits

3. **`/publicpr` 指令**：
   - 掃描每個 commit 的檔案清單
   - 自動排除包含機敏檔案的 commits
   - 使用 cherry-pick 確保 history 乾淨

### 手動檢查方法

```bash
# 檢查當前工作目錄中的機敏檔案
git status --ignored

# 檢查最近 commits 是否包含機敏檔案
git log --name-only -5 | grep -E "(.claude/|docs/|CLAUDE.md|.specify/|specs/|FAQ/)"

# 檢查公開 repo 是否已包含機敏檔案
git clone https://github.com/bouob/tickets_hunter.git temp-check
cd temp-check
ls -la .claude/ docs/ 2>/dev/null && echo "⚠️ 機敏檔案存在！" || echo "✅ 安全"
```

---

## 緊急修復流程

### 情境：公開 repo 發現嚴重 bug，需要立即修復

#### 選項 1：在 Private Repo 修復後發布（推薦）

```bash
# 1. 在 private repo 修復 bug
git checkout -b hotfix/critical-bug
# 編輯檔案修復 bug
/gsave
git checkout main
git merge hotfix/critical-bug

# 2. 立即發布到 origin
/publicpr

# 3. Merge PR（可使用 fast-forward）
gh pr merge --squash
```

#### 選項 2：直接在 Origin 修復（不推薦）

```bash
# 1. Clone origin repo
git clone https://github.com/bouob/tickets_hunter.git origin-hotfix
cd origin-hotfix

# 2. 修復 bug
git checkout -b hotfix/critical-bug
# 編輯檔案修復 bug
git commit -m "fix: resolve critical bug"

# 3. 建立 PR 到 origin
gh pr create --title "Hotfix: Critical Bug" --base main

# 4. Merge PR
gh pr merge --squash

# 5. 同步回 private repo
cd /path/to/private-repo
git fetch origin
git merge origin/main
```

**注意**：選項 2 會導致 private 和 origin 的 history 不一致，需要手動同步。

---

## 常見問題排解

### 問題 1：不小心推送機敏檔案到 Origin

**症狀**：
```bash
git log origin/main --name-only | grep "CLAUDE.md"
# 輸出：CLAUDE.md
```

**解決方案**：

1. **立即從 origin 刪除檔案**
   ```bash
   git checkout origin/main
   git rm CLAUDE.md docs/ -r
   git commit -m "chore: remove sensitive files"
   git push origin main
   ```

2. **清理 Git History（如果已提交多個版本）**
   ```bash
   # 使用 git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch CLAUDE.md docs/ -r" \
     --prune-empty --tag-name-filter cat -- --all

   # 強制推送
   git push origin --force --all
   git push origin --force --tags
   ```

3. **通知協作者**
   ```
   ⚠️ 重要通知：origin repo 的 history 已被重寫

   請所有協作者執行：
   1. git fetch origin
   2. git reset --hard origin/main
   ```

### 問題 2：/publicpr 沒有找到有效 commits

**症狀**：
```
⚠️ 沒有可推送的 commits！
所有 commits 都包含機敏檔案。
```

**原因**：所有未推送的 commits 都包含機敏檔案變更

**解決方案**：

1. **檢查 commits 清單**
   ```bash
   git log origin/main..HEAD --name-only
   ```

2. **手動分離程式碼和機敏檔案**
   ```bash
   # 回到分離點
   git reset --soft origin/main

   # 分批提交
   git add src/ tests/ README.md CHANGELOG.md
   git commit -m "feat: add new feature"

   git add docs/ CLAUDE.md
   git commit -m "docs: update internal docs"
   ```

3. **重新執行 /publicpr**
   ```bash
   /publicpr
   # 現在應該能找到有效 commits
   ```

### 問題 3：Cherry-pick 衝突

**症狀**：
```
⚠️ Cherry-pick 失敗: abc1234 feat: add feature X
衝突檔案：
  - src/chrome_tixcraft.py
```

**解決方案**：

1. **手動解決衝突**
   ```bash
   # 編輯衝突檔案
   vim src/chrome_tixcraft.py

   # 標記為已解決
   git add src/chrome_tixcraft.py

   # 繼續 cherry-pick
   git cherry-pick --continue
   ```

2. **重新執行 /publicpr**
   ```bash
   # /publicpr 會從中斷點繼續
   ```

### 問題 4：Private 和 Origin 的 History 分歧

**症狀**：
```bash
git log origin/main..private/main --oneline | wc -l
# 輸出：50+  （差異過大）
```

**原因**：長期未同步，或直接在 origin 修改

**解決方案**：

1. **定期同步**（推薦）
   ```bash
   # 每週執行一次
   /publicpr
   ```

2. **強制對齊**（危險，僅在必要時使用）
   ```bash
   # 在 private repo
   git fetch origin
   git checkout -b sync-origin
   git reset --hard origin/main

   # 挑選 private 的獨有 commits
   git cherry-pick [commit-range]

   # 測試無誤後
   git checkout main
   git reset --hard sync-origin
   ```

### 問題 5：gh CLI 未安裝或未登入

**症狀**：
```
command not found: gh
```

**解決方案**：

1. **安裝 gh CLI**
   ```bash
   # Windows (Scoop)
   scoop install gh

   # Windows (Chocolatey)
   choco install gh

   # macOS
   brew install gh

   # Linux
   # 參考：https://cli.github.com/
   ```

2. **登入 GitHub**
   ```bash
   gh auth login
   # 選擇 GitHub.com
   # 選擇 HTTPS
   # 跟隨提示完成驗證
   ```

3. **驗證登入狀態**
   ```bash
   gh auth status
   ```

---

## 最佳實踐

### 1. 頻繁提交，集中推送

```bash
# ✅ 推薦
/gsave  # 小改動 1
/gsave  # 小改動 2
/gsave  # 小改動 3
/gpush  # 統一推送（可選擇合併）

# ❌ 不推薦
# 累積大量變更後一次提交（難以追蹤）
```

### 2. 定期同步到公開 Repo

```bash
# 建議頻率：
# - 每週一次：小型更新
# - 每月一次：重大功能
# - 隨時：緊急修復

# 避免：
# - 累積數月才同步（造成巨大 PR）
```

### 3. 保持 .gitignore 最新

```bash
# 每次新增機敏檔案時：
# 1. 更新 .gitignore
# 2. 測試 /gsave 是否正確排除
# 3. 測試 /publicpr 是否正確過濾
```

### 4. 使用 Dry-run 模式

```bash
# 發布前先預覽
/publicpr --dry-run

# 確認無誤後再執行
/publicpr
```

### 5. 記錄發布歷史

```bash
# 在 CHANGELOG.md 中記錄每次公開發布
# 範例：
## [v2025.11.07] - 2025-11-07

### Public Release
- Released to origin repo via PR #123
- Added TicketPlus support
- Fixed OCR timeout issues

### Private Only (Not Released)
- Updated internal development docs
- Added new spec templates
```

---

## 指令速查表

| 指令 | 用途 | 推送目標 | 處理邏輯 |
|------|------|----------|----------|
| `/gsave` | 提交變更 | 本地 | 自動分離公開/機敏為不同 commits |
| `/gpush` | 推送公開 commits | private | 識別 PRIVATE 標記跳過機敏 commits |
| `/privatepush` | 推送機敏 commits | private | 優先推送現有 PRIVATE commits |
| `/publicpr` | 建立 PR 到公開 repo | origin | 識別 PRIVATE 標記過濾機敏 commits |

---

## 工作流程檢查清單

### 日常開發

- [ ] 修改程式碼
- [ ] 執行 `/gsave` 提交變更
- [ ] 執行 `/gpush` 推送到 private
- [ ] 如有機敏檔案更新，執行 `/privatepush`

### 發布準備

- [ ] 確認所有變更已推送到 private
- [ ] 執行 `/publicpr --dry-run` 預覽
- [ ] 檢查過濾結果是否正確
- [ ] 確認沒有機敏檔案被包含

### 實際發布

- [ ] 執行 `/publicpr` 建立 PR
- [ ] 在 GitHub 檢查 PR 內容
- [ ] 進行 Code Review
- [ ] Merge PR 到 origin/main
- [ ] 建立 Release（如需要）
- [ ] 更新 CHANGELOG.md

---

## 延伸閱讀

- **指令詳細說明**：
  - `.claude/commands/gsave.md`
  - `.claude/commands/gpush.md`
  - `.claude/commands/privatepush.md`
  - `.claude/commands/publicpr.md`

- **專案規範**：
  - `CLAUDE.md` - 開發規範（私人檔案）
  - `.specify/memory/constitution.md` - 專案憲章（私人檔案）

- **Git 文件**：
  - [Git Cherry-pick](https://git-scm.com/docs/git-cherry-pick)
  - [Git Filter-branch](https://git-scm.com/docs/git-filter-branch)
  - [GitHub CLI](https://cli.github.com/)

---

**最後更新**：2025-11-07
**維護者**：專案團隊
**版本**：v1.0
