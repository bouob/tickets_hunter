---
description: "在公開 repo PR merge 後建立 Release Tag 並觸發 GitHub Actions"
model: sonnet
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 公開 Repo Release 建立指令

在 PR merge 到公開 repo (origin) 後，建立 Release Tag 並觸發 GitHub Actions 自動打包發布。

---

## 🎯 指令目的

此指令專門處理雙 repo 維護流程中的最後階段：
- **前提**：PR 已經 merge 到 origin/main
- **功能**：
  1. 切換到 origin/main 分支
  2. 提取當前版本號
  3. 從 CHANGELOG.md 提取 release notes
  4. 建立 annotated tag
  5. 推送 tag 到 origin
  6. 觸發 GitHub Actions 自動打包

---

## 📋 工作流程概覽

```
┌────────────────────────────────────────────────────────────┐
│                  完整發布流程                              │
└────────────────────────────────────────────────────────────┘

Step 1: /publicpr
  ├─ 建立 PR 到 origin
  └─ PR URL: https://github.com/bouob/tickets_hunter/pull/123

Step 2: Code Review & Merge
  ├─ 在 GitHub 進行 Code Review
  ├─ 審核通過後 Merge PR
  └─ PR #123 merged into main ✅

Step 3: /publicrelease  ← 此指令
  ├─ 切換到 origin/main
  ├─ Pull 最新變更
  ├─ 提取版本號 (例如：2025.11.07)
  ├─ 建立 tag: v2025.11.07
  ├─ 推送 tag 到 origin
  └─ 觸發 GitHub Actions 🚀

Step 4: GitHub Actions 自動執行
  ├─ 偵測到新 tag
  ├─ 執行建置流程
  ├─ 打包 Windows/macOS/Linux 版本
  ├─ 建立 GitHub Release
  └─ 上傳 Release Assets ✅

Step 5: Release 完成 🎉
  └─ 使用者可下載：https://github.com/bouob/tickets_hunter/releases/tag/v2025.11.07
```

---

## 🚨 執行前提

### 必須滿足以下條件

1. **PR 已 Merge**：
   ```bash
   # 檢查 PR 狀態
   gh pr view [PR-number] --json state
   # 輸出：{"state":"MERGED"}
   ```

2. **origin/main 包含最新變更**：
   ```bash
   # 檢查 origin/main 的最新 commit
   git log origin/main -1
   ```

3. **版本號已更新**：
   ```bash
   # 檢查 CONST_APP_VERSION
   grep "CONST_APP_VERSION" src/nodriver_tixcraft.py
   # 輸出：CONST_APP_VERSION = "2025.11.07"
   ```

4. **CHANGELOG.md 已更新**：
   ```bash
   # 檢查是否有對應版本的區塊
   grep "## \[2025.11.07\]" CHANGELOG.md
   ```

---

## 📝 執行流程

### 步驟 0 - 前置檢查

#### A. 檢查當前 Repo

- 執行 `git remote -v` 檢查 remote 設定
- 確認當前在正確的 repo 目錄

#### B. 提示執行時機

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 /publicrelease 執行時機
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

此指令應在以下條件滿足後執行：
✅ PR 已 merge 到 origin/main
✅ 版本號已更新 (CONST_APP_VERSION)
✅ CHANGELOG.md 已更新

⚠️ 如果 PR 尚未 merge，請先完成 Code Review 和 Merge。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### C. 確認執行

- **明確詢問**：「PR 已 merge 完成，確定要建立 Release Tag？(y/n)」
- **僅當使用者回覆 "y" 時**：繼續執行

### 步驟 1 - 切換到 Origin Main

#### A. 檢查本地 origin Remote

- 執行 `git remote get-url origin`
- 確認 URL 為公開 repo

#### B. Fetch 並切換分支

- 執行 `git fetch origin`
- 執行 `git checkout origin/main` 或建立追蹤分支：
  ```bash
  git checkout -B release-temp origin/main
  ```

#### C. 確認最新狀態

- 執行 `git log -1` 顯示最新 commit
- 確認這是剛 merge 的 PR commit

### 步驟 2 - 提取版本號

#### A. 從 CONST_APP_VERSION 提取

- 執行以下指令提取版本號：
  ```bash
  # 優先順序：
  # 1. src/nodriver_tixcraft.py
  # 2. src/chrome_tixcraft.py
  # 3. src/config_launcher.py

  VERSION=$(grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | \
            grep -oP '"\K[^"]+' | head -1)
  ```

#### B. 驗證版本號格式

- 格式檢查：`YYYY.MM.DD`
- 範例：`2025.11.07`

#### C. 生成 Tag 名稱

- 格式：`v{VERSION}`
- 範例：`v2025.11.07`

#### D. 顯示版本資訊

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 版本資訊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

當前版本號: 2025.11.07
Tag 名稱: v2025.11.07

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 步驟 3 - 檢查 Tag 是否已存在

#### A. 檢查本地 Tag

- 執行 `git tag -l "v${VERSION}"`

#### B. 檢查遠端 Tag

- 執行 `git ls-remote --tags origin "refs/tags/v${VERSION}"`

#### C. 處理已存在的 Tag

- **如果 Tag 已存在**：
  ```
  ⚠️ Tag v2025.11.07 已存在！

  請選擇處理方式：
  [1] 取消操作（建議）
  [2] 刪除舊 tag 並重新建立（危險）
  [3] 使用新的版本號

  請輸入選項 (1/2/3):
  ```

- **選擇 [1]**：結束執行
- **選擇 [2]**：
  ```bash
  git tag -d v2025.11.07
  git push origin :refs/tags/v2025.11.07
  # 繼續建立新 tag
  ```
- **選擇 [3]**：詢問新的版本號並重新執行步驟 2

### 步驟 4 - 提取 CHANGELOG 內容

#### A. 讀取 CHANGELOG.md

- 檢查檔案是否存在：
  ```bash
  if [ ! -f "CHANGELOG.md" ]; then
    echo "⚠️ CHANGELOG.md 不存在，將使用預設 release notes"
  fi
  ```

#### B. 提取對應版本的區塊

- 搜尋模式：
  ```bash
  # 搜尋版本號區塊
  sed -n '/## \[2025.11.07\]/,/## \[/p' CHANGELOG.md | \
    sed '$ d' | tail -n +2
  ```

#### C. 清理格式

- 移除多餘的空行
- 保留 markdown 格式（標題、列表、連結等）

#### D. 如果未找到對應版本

- 使用預設 release notes：
  ```markdown
  ## Release v2025.11.07

  此版本包含以下更新：
  - 詳細變更請查看 commit history

  完整資訊請參考專案文件。
  ```

### 步驟 5 - 預覽 Tag 資訊

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Tag 預覽
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tag Name: v2025.11.07
Target: origin/main (abc1234)

Tag Message:
───────────────────────────────────────
## [2025.11.07] - 2025-11-07

### Added
- TicketPlus platform support with full automation
- Auto seat selection for ibon platform

### Fixed
- OCR timeout issues in high-load scenarios
- Date keyword matching edge cases

### Improved
- Error handling for network failures
- Logging clarity for debugging

───────────────────────────────────────

此 tag 將被推送到：
https://github.com/bouob/tickets_hunter.git

推送後將觸發 GitHub Actions 自動建置 Release。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 步驟 6 - 確認建立 Tag

- **明確詢問**：「確認建立此 Release Tag？(y/n)」
- **僅當使用者回覆 "y" 時**：繼續執行

### 步驟 7 - 建立 Annotated Tag

#### A. 建立 Tag

- 執行 `git tag -a v${VERSION} -m "${TAG_MESSAGE}"`
- 使用 `-a` 建立 annotated tag（包含完整 metadata）

#### B. 驗證 Tag 建立

- 執行 `git tag -l -n9 v${VERSION}` 顯示 tag 資訊

### 步驟 8 - 推送 Tag 到 Origin

#### A. 推送 Tag

- 執行 `git push origin v${VERSION}`

#### B. 顯示推送結果

```
✅ Tag 推送成功！

Tag: v2025.11.07
Remote: origin
URL: https://github.com/bouob/tickets_hunter.git
```

### 步驟 9 - 觸發 GitHub Actions

#### A. 檢查 Workflow 檔案

- 檢查 `.github/workflows/` 中是否有 release workflow
- 常見檔名：`release.yml`、`build.yml`

#### B. 顯示 GitHub Actions 資訊

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 GitHub Actions 已觸發
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow 將自動開始執行：
https://github.com/bouob/tickets_hunter/actions

預計執行時間：10-30 分鐘（視建置複雜度）

完成後 Release 將出現在：
https://github.com/bouob/tickets_hunter/releases/tag/v2025.11.07

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### C. 可選：監控 Workflow 狀態

- 執行 `gh run list --workflow=release.yml --limit=1`
- 顯示最新 workflow run 的狀態

### 步驟 10 - 清理與還原

#### A. 切換回原始分支

- 執行 `git checkout main`（或原始分支）

#### B. 刪除臨時分支（如果有）

- 執行 `git branch -D release-temp`

#### C. 同步 Tag 到 Private Repo（可選）

- **詢問**：「是否將 tag 同步到 private repo？(y/n)」
- **選擇 y**：
  ```bash
  git push private v2025.11.07
  ```

### 步驟 11 - 顯示完成訊息

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Release 建立完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tag: v2025.11.07
Status: ✅ Pushed to origin

下一步：
1. 監控 GitHub Actions:
   https://github.com/bouob/tickets_hunter/actions

2. 檢查 Release（約 10-30 分鐘後）:
   https://github.com/bouob/tickets_hunter/releases/tag/v2025.11.07

3. 驗證下載連結是否正常

4. 發布公告（如需要）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ⚠️ 執行約束

### 必須確認的步驟

1. **PR 已 Merge 確認**：必須使用者明確確認 PR 已完成
2. **Tag 建立確認**：必須使用者確認 tag 資訊無誤
3. **Tag 推送確認**：推送前需最終確認

### 自動中止條件

- PR 尚未 merge
- 版本號格式錯誤
- Tag 已存在（選擇取消時）
- 使用者在任何確認步驟回覆 "n"
- Git 指令執行失敗

---

## 🔧 進階選項

- `--version=<version>`: 手動指定版本號（覆蓋 CONST_APP_VERSION）
- `--tag-name=<name>`: 手動指定 tag 名稱（覆蓋預設格式）
- `--no-sync-private`: 不同步 tag 到 private repo
- `--dry-run`: 預覽模式，不執行實際 tag 建立和推送
- `--force`: 強制覆蓋已存在的 tag（⚠️ 危險操作）

---

## 📚 使用場景

### 場景 1：標準 Release 流程

```bash
# 完整流程範例

# Step 1: 開發完成，建立 PR
/publicpr
# PR URL: https://github.com/bouob/tickets_hunter/pull/123

# Step 2: 在 GitHub 進行 Code Review
# - 檢查程式碼
# - 通過 CI 檢查
# - Merge PR

# Step 3: 建立 Release Tag
/publicrelease

執行流程：
1. 確認 PR 已 merge？y
2. 切換到 origin/main
3. 提取版本號：2025.11.07
4. 提取 CHANGELOG 內容
5. 預覽 Tag 資訊
6. 確認建立 Tag？y
7. 建立 tag: v2025.11.07
8. 推送到 origin
9. GitHub Actions 觸發 ✅
10. 同步到 private？y

# Step 4: 監控 GitHub Actions
# 訪問：https://github.com/bouob/tickets_hunter/actions

# Step 5: Release 完成
# 訪問：https://github.com/bouob/tickets_hunter/releases/tag/v2025.11.07
```

### 場景 2：預覽模式

```bash
# 先預覽不實際建立 tag
/publicrelease --dry-run

執行流程：
1-5. （同場景 1）
6. 🔍 Dry-run 模式，不執行實際 tag 建立
```

### 場景 3：手動指定版本號

```bash
# 覆蓋 CONST_APP_VERSION
/publicrelease --version=2025.11.08

執行流程：
1. 確認 PR 已 merge？y
2. 使用手動指定版本號：2025.11.08
3. Tag 名稱：v2025.11.08
4-10. （繼續正常流程）
```

---

## 🛡️ 安全特性

### Tag 重複檢查

- **本地檢查**：防止覆蓋本地已存在的 tag
- **遠端檢查**：防止覆蓋遠端已存在的 tag
- **衝突處理**：提供取消、刪除舊 tag、使用新版本號等選項

### 多層確認

- **PR Merge 確認**：確保 PR 已完成
- **Tag 資訊確認**：預覽後確認
- **推送確認**：推送前最終確認

### Annotated Tag

- 使用 `-a` 建立 annotated tag（而非 lightweight tag）
- 包含完整 metadata：
  - Tagger 資訊
  - Tag 日期
  - Tag message（從 CHANGELOG 提取）

---

## 💡 使用建議

### 完整發布流程建議

```
私人開發階段（Private Repo）：
1. /gsave      → 提交變更
2. /gpush      → 推送到 private
3. 持續開發    → 重複 1-2

準備發布階段：
4. /gupdate    → 更新版本號
5. /gchange    → 更新 CHANGELOG
6. /gsave      → 提交版本號和 CHANGELOG
7. /gpush      → 推送到 private

公開發布階段（Public Repo）：
8. /publicpr   → 建立 PR 到 origin
9. Code Review → 在 GitHub 審核
10. Merge PR   → 合併到 origin/main

Release 階段：
11. /publicrelease → 建立 Release Tag
12. 監控 Actions   → 等待自動建置
13. 驗證 Release   → 檢查下載連結
14. 發布公告       → 通知使用者
```

### 何時使用此指令

- ✅ PR 已經 merge 到 origin/main
- ✅ 準備建立正式 Release
- ✅ 需要觸發 GitHub Actions 自動打包

### 何時不使用此指令

- ❌ PR 尚未 merge（應等待 Code Review 完成）
- ❌ 僅推送程式碼不需要 Release（使用 `/publicpr`）
- ❌ 測試版本或 beta 版本（考慮使用 pre-release）

---

## 🔧 故障排除

### 問題 1：Tag 已存在

**症狀**：
```
⚠️ Tag v2025.11.07 已存在！
```

**解決方案**：

1. **檢查是否已發布**
   ```bash
   gh release view v2025.11.07
   # 如果已發布，應使用新版本號
   ```

2. **刪除舊 tag（僅在必要時）**
   ```bash
   git tag -d v2025.11.07
   git push origin :refs/tags/v2025.11.07
   # 重新執行 /publicrelease
   ```

3. **使用新版本號**
   ```bash
   /publicrelease --version=2025.11.08
   ```

### 問題 2：CHANGELOG.md 未找到對應版本

**症狀**：
```
⚠️ 在 CHANGELOG.md 中未找到 v2025.11.07 的區塊
```

**解決方案**：

1. **手動編輯 CHANGELOG.md**
   ```bash
   # 新增版本區塊
   ## [2025.11.07] - 2025-11-07
   ### Added
   - New features...
   ```

2. **使用預設 release notes**
   ```bash
   # /publicrelease 會自動使用預設訊息
   ```

### 問題 3：GitHub Actions 未觸發

**症狀**：
```
Tag 推送成功，但 GitHub Actions 沒有執行
```

**原因**：

1. Workflow 檔案不存在或配置錯誤
2. Workflow 觸發條件不匹配

**解決方案**：

1. **檢查 Workflow 檔案**
   ```bash
   cat .github/workflows/release.yml
   # 確認 on.push.tags 配置正確
   ```

2. **Workflow 範例**
   ```yaml
   name: Release Build
   on:
     push:
       tags:
         - 'v*'  # 匹配所有 v 開頭的 tag
   ```

3. **手動觸發 Workflow**
   ```bash
   gh workflow run release.yml
   ```

### 問題 4：權限不足

**症狀**：
```
error: failed to push some refs to 'https://github.com/bouob/tickets_hunter.git'
```

**原因**：沒有推送 tag 的權限

**解決方案**：

1. **檢查 Git 認證**
   ```bash
   git config credential.helper
   gh auth status
   ```

2. **重新認證**
   ```bash
   gh auth login
   git config --global credential.helper manager
   ```

---

## 📚 延伸閱讀

- **工作流程文件**：`docs/11-git-workflow/dual-repo-workflow.md`
- **配對指令**：
  - `/publicpr`（建立 PR）
  - `/gpush`（推送到 private）
  - `/gchange`（更新 CHANGELOG）
- **GitHub 文件**：
  - [Creating Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
  - [GitHub Actions](https://docs.github.com/en/actions)
  - [Git Tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

---

**最後更新**：2025-11-07
**版本**：v1.0

$ARGUMENTS
