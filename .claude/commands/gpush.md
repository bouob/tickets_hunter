---
description: "檢查並推送累積的 Git commits 到遠端倉庫"
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# Git 推送確認指令

處理本地累積的 commits 並推送到遠端 main 分支。

---

## 📜 Git 提交規範（遵循專案憲章第 IX 條）

**完整規範請參考**：`.specify/memory/constitution.md` 第 IX 條

### 提交訊息格式（混合格式）

```
emoji type(scope): subject

body (optional)

footer (optional)
```

**範例**：
```
✨ feat(nodriver): add auto-scrolling for shadow DOM elements

Implemented smooth scrolling to element before clicking in NoDriver engine.

- Add auto_scroll_before_click function (新增滾動至元素函數)
- Handle deeply nested Shadow DOM structures (處理深層嵌套 Shadow DOM)
```

### Type 列表（常用）

| Type | Emoji | 說明 |
|------|-------|------|
| `feat` | ✨ | 新功能 |
| `fix` | 🐛 | 錯誤修復 |
| `docs` | 📝 | 文件更新 |
| `refactor` | ♻️ | 重構 |
| `chore` | 🔧 | 維護工作 |
| `ci` | 👷 | CI/CD 配置 |

**完整清單與 Scope 建議**：參考憲法文件

### Subject 規則

- ✅ 使用命令式語氣（"add" 而非 "added"）
- ✅ 首字母小寫，不加句號
- ✅ 限制在 50 個字符以內

---

## 🚨 重要提醒

### 安全提醒
**執行前建議先執行 `/gdefault` 清除本地敏感設定檔案**，避免將測試資料推送到遠端。

### 語言規範（與 `/gsave` 一致）
- ✅ **主題行使用混合格式** - emoji + type(scope): subject（英文）
- ✅ **描述可中英文並列** - 英文在前，中文註解在括號內
- 💡 **範例**：`✨ feat(nodriver): add feature X (新增功能 X)`

---

## 🔧 進階選項

- `--strategy=<mode>`: 指定推送策略 (auto/direct/pr/clean/squash/force)
- `--force-clean`: 強制建立乾淨分支（無歷史問題）
- `--auto-merge`: 自動合併相關 commits
- `--auto-merge-pr`: 建立 PR 後自動設定 auto-merge（需通過 CI）
- `--force`: 強制推送，忽略分支保護（⚠️ 危險操作）
- `--dry-run`: 預覽模式，不執行實際推送

---

## 📝 執行流程

### 前置檢查 1 - 版本號確認

- **執行檢查**：顯示所有檔案中的當前版本號
  ```bash
  echo "=== 當前版本號 ==="
  grep "CONST_APP_VERSION" src/chrome_tixcraft.py | head -1
  grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1
  grep "CONST_APP_VERSION" src/config_launcher.py | head -1
  grep "版本.*TicketsHunter" README.md | head -1
  ```
- **詢問**：「當前版本號是否已更新為最新日期？(y/n/skip)」
  - **y**：繼續執行
  - **n**：提示「請先執行 /gupdate 更新版本號」，結束流程
  - **skip**：顯示警告，繼續執行

### 前置檢查 2 - CHANGELOG 確認

- **詢問**：「是否已執行 /gchange 更新 CHANGELOG.md？(y/n/skip)」
  - **y**：繼續執行
  - **n**：提示「請先執行 /gchange 更新 CHANGELOG.md」，結束流程
  - **skip**：顯示警告，繼續執行

**建議工作流程**：
```bash
1. /gupdate       # 更新版本號
2. /gchange       # 更新 CHANGELOG
3. /gsave         # 提交變更
4. /gpush         # 推送到遠端
```

### 步驟 0 - 預先檢測

- 掃描歷史 merge commits 並評估影響
- 檢查分支保護規則的具體限制
- 分析本地 commits 的推送可行性
- 自動評估最佳推送策略並提供建議
- **如果使用 `--dry-run` 選項**：在此步驟停止並顯示完整分析報告

### 步驟 1 - 檢查分支保護狀態

- 執行 `git push origin main --dry-run` 測試推送權限
- **如果推送被拒絕**（分支保護啟用），提供選擇：
  ```
  🚨 偵測到分支保護規則！請選擇處理方式：
  [1] 使用 PR 工作流程（建議）
  [2] Force 推送（危險，忽略保護）
  [3] 取消操作
  請輸入選項 (1/2/3):
  ```
- **如果推送可行**，繼續直接推送流程

### 步驟 2 - 分析本地狀態

- 執行 `git status` 查看本地分支狀態
- 執行 `git log origin/main..HEAD --oneline` 顯示本地領先的 commits

### 步驟 2.5 - 檢查並過濾 .gitignore 檔案

- 讀取 `.gitignore` 檔案內容，解析忽略規則
- 執行 `git log origin/main..HEAD --name-only` 取得所有變更檔案清單
- 比對變更檔案與 .gitignore 規則
- **過濾掉包含被忽略檔案的 commits**
- 顯示過濾結果：
  ```
  🔍 檢查 .gitignore 規則...
  ✅ 找到 5 個 commits
  ⚠️ 發現 2 個 commits 包含被忽略的檔案（已排除）
  ✅ 剩餘 3 個有效 commits 將被處理
  ```

**智慧檔案分離**：
- 如果 commit 同時包含應提交檔案和被忽略檔案：
  - 自動拆分該 commit
  - 僅保留應該提交的檔案變更
  - 提示：「Commit xyz9012 已自動分離，移除被忽略的檔案」

### 步驟 2.6 - Commit 合併詢問

- 檢查本地 commits 數量，如果超過 2 個提供合併選項
- **詢問**：「發現 N 個 commits，是否要合併為統整的 commit 一次推送？(y/n/skip)」
  - **y**: 合併所有 commits 為統整 commit（參考 gsave 方法重新分析 diff）
  - **n**: 跳過合併，維持原有 commits
  - **skip**: 直接進入推送流程

### 步驟 2.7 - 合併執行方法（選擇 y 時）

**合併流程**：
- 記錄當前 HEAD commit hash（用於可能的回滾）
- 執行 `git reset --soft origin/main` 回到遠端版本
- **🔒 安全保證**：`--soft` 確保工作目錄和暫存區檔案完全不變，可隨時回滾

**重新分析與統整**：
- 執行 `git diff --staged` 查看所有累積的變更
- 分析變更檔案的類型和性質
- 根據變更內容自動分類（feat/fix/docs/chore 等）
- 生成結構化的統整 commit 訊息：
  ```
  🎯 [Type] Concise English subject line

  - Key change point 1 in English (關鍵變更點 1)
  - Key change point 2 in English (關鍵變更點 2)
  ```
- 執行 `git commit` 並顯示新的 commit 結構供確認

**統整訊息策略**：
- 遵循混合格式（emoji + type(scope): subject）
- 識別共同主題，生成精煉標題
- 提取每個 commit 的關鍵改動點（雙語描述）
- 最多保留 5-7 個關鍵點（避免訊息過長）

### 步驟 3 - 檢查遠端同步

- 執行 `git fetch` 取得最新遠端狀態
- 檢查是否有衝突或需要合併的變更

### 步驟 4 - 顯示推送預覽

- 顯示即將推送的 commit 列表與變更摘要
- 確認目標分支為 main
- 清楚列出所有變更內容

### 步驟 5 - 智慧推送決策

#### A. 直接推送模式（分支未保護）

- **明確詢問**：「確定要推送這些 commits 到 main 分支嗎？請回覆 y 或 N」
- **停止執行，等待使用者回覆**
- **僅當使用者明確回覆 "y" 時**：執行 `git push origin main`

#### B. PR 工作流程（分支已保護，選擇 [1]）

- 顯示將建立的 feature branch 和 PR 資訊
- **明確詢問**：「將建立 PR。確定要建立 feature branch 並推送嗎？請回覆 y 或 N」
- **僅當使用者明確回覆 "y" 時**：
  - 建立 feature branch：`feature/auto-commits-YYYY-MM-DD-HHmm`
  - 推送到 feature branch：`git push origin feature-branch`
  - **自動生成詳細 PR 文件**（遵循 CONTRIBUTING.md 模板）：
    - **PR 標題與描述使用繁體中文**
    - 分析所有 commits 生成變更摘要
    - 列出修改檔案和技術細節
    - 自動生成測試檢查清單
  - 建立 PR：`gh pr create --title "[中文標題]" --body "[中文描述]"`
  - **自動 Merge 處理**（如果指定 `--auto-merge-pr`）：
    - 設定 auto-merge：`gh pr merge --auto --squash [PR-URL]`
    - 監控 CI 狀態：持續檢查 GitHub Actions
    - 自動合併：通過 CI 後自動 squash merge
    - 清理分支：merge 後自動刪除 feature branch

#### C. Force 推送模式（選擇 [2]）

- 使用 `git push --force-with-lease origin main` 強制推送
- ⚠️ **極度危險**：可能覆蓋其他人的變更
- 必須三次確認才能執行
- 建議使用 `--force-with-lease` 而非 `--force` 確保安全性

#### D. 取消操作（選擇 [3]）

- 顯示「已取消推送操作」訊息並結束

### 步驟 5.5 - Release Tag 建立選項

在推送確認後，詢問是否為本次推送建立 Release Tag。

**A. 提取當前版本號**
- 從 CONST_APP_VERSION 提取版本號（例如：「2025.11.04」）
- 格式化為 tag 名稱：v{VERSION}（例如：v2025.11.04）

**B. 詢問使用者**
```
🏷️  是否為本次推送建立 Release Tag？(y/n/skip)
  y    - 建立 release tag（觸發 GitHub Actions 自動打包發布）
  n    - 不建立 tag，繼續推送
  skip - 略過詢問，繼續推送

請輸入選擇：
```

**C. Tag 建立流程（若選擇 y）**

1. **確認 Tag 名稱**：顯示建議的 tag 名稱，允許使用者自訂
2. **提取 CHANGELOG 內容**：
   - 讀取 CHANGELOG.md 檔案
   - 搜尋對應版本的區塊
   - 提取變更內容並清理格式
3. **預覽 Tag 資訊**：
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📋 Tag 預覽
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Tag Name: v2025.11.04

   Tag Message:
   ───────────────────────────────────────
   [從 CHANGELOG.md 提取的內容]
   ───────────────────────────────────────
   ```
4. **最終確認**：詢問「確認建立此 tag？(y/n)」
5. **建立 Annotated Tag**：執行 `git tag -a v2025.11.04 -m "[訊息]"`
6. **推送包含 Tag**：
   - 直接推送：`git push origin main --tags`
   - PR 推送：在建立 PR 後執行 `git push origin --tags`
7. **提示後續動作**：
   ```
   🚀 Tag v2025.11.04 已建立並推送！

   GitHub Actions 將自動開始建置 Release：
   https://github.com/{repo}/actions

   完成後 Release 將出現在：
   https://github.com/{repo}/releases/tag/v2025.11.04
   ```

### 步驟 6 - 執行結果處理

- **直接推送成功**：顯示遠端倉庫的最新狀態
- **PR 建立成功**：顯示 PR URL 和合併說明
- **PR 自動合併完成**：顯示最終 merge 結果和分支清理狀態
- **Force 推送成功**：顯示強制推送結果和警告訊息
- **如果使用者回覆 "N"**：顯示「已取消推送」訊息

---

## ⚠️ 執行約束

- **直接推送**：需要使用者明確確認 "y"，否則取消
- **PR 推送**：分支保護啟用時也需要使用者明確確認 "y"，否則取消
- **Force 推送**：需要三次明確確認 "FORCE-YES"，並顯示巨大警告
- **必須等待**使用者的明確回應
- **預設行為**：任何推送都必須經過使用者明確確認

---

## 📚 使用場景

### 場景 1：累積多個 commits 後統一推送（含合併）

```bash
# 使用 gsave 累積多個 commits
gsave -> 🐛 Fix OCR timeout (選擇 N)
gsave -> 🐛 Fix OCR image processing (選擇 N)
gsave -> ✨ Add platform support (選擇 N)

# 使用 gpush 統一推送
gpush -> 發現 3 個 commits -> 詢問是否合併 -> 選擇 y

合併流程：
1. git reset --soft origin/main（本地檔案不變）
2. git diff --staged（分析所有累積變更）
3. 自動產生統整訊息：
   ✨ feat: implement platform support and fix OCR issues

   - Add new platform integration with config support (新增平台整合與配置支援)
   - Fix OCR timeout handling for long-running tasks (修正 OCR 超時處理)
   - Improve OCR image processing error handling (改善 OCR 圖片處理錯誤處理)

4. git commit（執行統整提交）

-> 檢查分支保護 -> 選擇推送方式：
  - 無保護：確定推送？y -> git push origin main -> 完成
  - 有保護：[1] -> 建立 feature branch -> 推送 -> 建立 PR
```

### 場景 2：分支保護時的 PR 工作流程

```bash
gpush
-> 檢查分支保護狀態...
-> 🚨 偵測到分支保護規則！請選擇處理方式：
   [1] 使用 PR 工作流程（建議）
   [2] Force 推送（危險，忽略保護）
   [3] 取消操作
   請輸入選項 (1/2/3): 1

-> 將建立 PR。確定要建立 feature branch 並推送嗎？請回覆 y 或 N: y
-> 建立 feature branch: feature/auto-commits-2024-01-15-1430
-> 推送到 feature branch...
-> 建立 PR: "✨ feat: Add TicketPlus support and fix OCR issues"
-> ✅ PR 已建立: https://github.com/bouob/tickets_hunter/pull/123
```

### 場景 3：自動 Merge PR 流程

```bash
gpush --auto-merge-pr
-> 檢查分支保護狀態...
-> 將建立 PR 並設定自動合併。確定要建立 feature branch 並推送嗎？y
-> 建立 feature branch...
-> 生成 CONTRIBUTING.md 格式的 PR 文件...
-> 建立 PR: "✨ feat: Add platform support"
-> 設定 auto-merge: squash merge 模式
-> 🔄 監控 CI 狀態...
-> ✅ 所有檢查通過！
-> 🎉 PR 自動合併完成
-> 🧹 清理 feature branch
-> ✅ 推送流程完成！
```

---

## 🛡️ 安全特性

### 推送安全
- **雙重確認**：顯示詳細資訊後再次詢問
- **衝突檢測**：推送前檢查遠端變更
- **回滾選項**：可選擇取消推送保留本地狀態
- **狀態透明**：清楚顯示推送前後的倉庫狀態

### 合併安全
- **檔案不變保證**：使用 `git reset --soft` 確保本地檔案完全不變
- **暫存區保留**：所有 commits 的變更保留在暫存區
- **回滾保護**：記錄原始 HEAD，可隨時復原
- **智慧分析**：重新執行 `git diff --staged` 分析所有累積變更
- **使用者控制**：每個決策都需要明確確認

---

## 💡 使用建議

**配合 gsave 指令使用**：實現「小步提交，自動合併，批量推送」的工作流程。

### 建議的工作流程
1. **開發階段**：使用 `gsave` 頻繁提交小改動
2. **整理階段**：使用 `gpush` 合併相關 commits
3. **推送階段**：統一推送到遠端 main 分支

### 合併策略建議

**統整合併模式（推薦）**：
- 選擇 **y**：將所有 commits 重新分析並合併為統整的 commit
  - 適合：完成階段性功能或修復後的統一推送

**保留原始 commits 模式**：
- 選擇 **n** 或 **skip**：維持所有原始 commits
  - 適合：需要保留完整開發脈絡的情況

---

## 🔧 策略模式使用範例

```bash
# 自動評估並選擇最佳策略
gpush --strategy=auto

# 強制使用乾淨分支（避免歷史問題）
gpush --force-clean

# 預覽模式（檢查不執行）
gpush --dry-run

# 自動合併模式
gpush --auto-merge

# 自動 PR 合併模式
gpush --auto-merge-pr

# Force 推送模式（極度危險）
gpush --force
```

---

## 📝 語言規範總結

**Commit 與 PR 訊息語言標準**：

### ✅ Commit 訊息規範（與 `/gsave` 一致）
- **主題行使用英文** - emoji + type(scope): subject（符合國際標準）
- **描述可中英文並列** - 英文在前，中文註解在括號內
- 格式：`English description (中文說明)`
- 保留 emoji 前綴，簡潔扼要，50 字元內

### ✅ PR 標題與描述規範
- **標題與描述使用繁體中文**
- 目的：團隊協作使用母語更清楚易懂
- 包含完整的變更摘要、檔案清單、測試項目等

### 📋 適用場景
- ✅ Commit 訊息：合併 commits 產生的統整訊息、Squash merge 的最終 commit
- ✅ PR 文件：PR 標題和描述使用繁體中文

---

## 📚 延伸閱讀

- **專案憲章**：`.specify/memory/constitution.md`（第 IX 條：Git 提交規範）
- **配對指令**：`/gsave`（產生 commit 訊息）、`/gdefault`（清除敏感設定）
- **Conventional Commits**：https://www.conventionalcommits.org/

$ARGUMENTS
