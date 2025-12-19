---
description: "從 GitHub spec-kit 同步最新範本與指令，支援版本檢查、差異分析、更新與中文化。"
model: opus
handoffs:
  - label: Analyze After Sync
    agent: speckit.analyze
    prompt: Run consistency analysis after sync
    send: true
---

## 使用者輸入

```text
$ARGUMENTS
```

## 大綱

您正在執行 speckit 同步指令，用於從 GitHub spec-kit upstream (`github/spec-kit`) 同步最新的範本與指令。

### 支援的操作模式

| 模式 | 說明 | 範例 |
|------|------|------|
| `check`（預設）| 僅檢查版本差異，不修改檔案 | `/speckit.sync check` |
| `diff` | 顯示詳細的檔案差異 | `/speckit.sync diff` |
| `update` | 更新檔案（不執行中文化） | `/speckit.sync update` |
| `full` | 完整同步（更新 + 中文化） | `/speckit.sync full` |

---

## 執行步驟

### 1. 初始化

1. 解析 `$ARGUMENTS` 決定操作模式：
   - 空白或 `check` → 版本檢查模式
   - `diff` → 差異分析模式
   - `update` → 更新模式
   - `full` → 完整同步模式

2. 讀取 `.specify/sync-metadata.json`：
   ```bash
   cat .specify/sync-metadata.json
   ```
   記錄：
   - `upstream.last_synced.version` - 上次同步版本
   - `upstream.last_synced.date` - 上次同步日期
   - `protected_files` - 受保護檔案清單
   - `file_tracking` - 檔案追蹤狀態

### 2. 版本檢查（所有模式）

1. 執行版本檢查腳本：
   ```powershell
   .specify/scripts/powershell/sync-speckit.ps1 -Action check-version -OutputFormat json
   ```

2. 解析 JSON 輸出，取得：
   - `upstream.latest_version` - 最新版本號
   - `upstream.release_date` - 發布日期
   - `upstream.latest_commit` - 最新 commit
   - `local.last_synced_version` - 本地同步版本

3. 比較版本並輸出報告：

   ```markdown
   ## Speckit 同步狀態報告

   **Upstream 資訊**
   - 儲存庫：github/spec-kit
   - 最新版本：[latest_version]
   - 發布日期：[release_date]
   - 最新提交：[latest_commit]

   **本地資訊**
   - 上次同步版本：[last_synced_version]
   - 上次同步日期：[last_synced_date]
   - 在地化版本：[localization_version]

   **狀態**：[有可用更新 / 已是最新版本]
   ```

4. 如果模式是 `check`，到此結束並輸出建議行動。

### 3. 差異分析（diff/update/full 模式）

1. 取得 upstream 檔案清單：
   ```powershell
   .specify/scripts/powershell/sync-speckit.ps1 -Action list-files -OutputFormat json
   ```

2. 對每個 upstream 檔案，比較本地版本：

   **檔案對應關係**：

   | Upstream 路徑 | 本地路徑 |
   |--------------|---------|
   | `templates/spec-template.md` | `.specify/templates/spec-template.md` |
   | `templates/plan-template.md` | `.specify/templates/plan-template.md` |
   | `templates/tasks-template.md` | `.specify/templates/tasks-template.md` |
   | `templates/checklist-template.md` | `.specify/templates/checklist-template.md` |
   | `templates/agent-file-template.md` | `.specify/templates/agent-file-template.md` |
   | `templates/commands/specify.md` | `.claude/commands/speckit.specify.md` |
   | `templates/commands/clarify.md` | `.claude/commands/speckit.clarify.md` |
   | `templates/commands/plan.md` | `.claude/commands/speckit.plan.md` |
   | `templates/commands/tasks.md` | `.claude/commands/speckit.tasks.md` |
   | `templates/commands/implement.md` | `.claude/commands/speckit.implement.md` |
   | `templates/commands/analyze.md` | `.claude/commands/speckit.analyze.md` |
   | `templates/commands/checklist.md` | `.claude/commands/speckit.checklist.md` |
   | `templates/commands/constitution.md` | `.claude/commands/speckit.constitution.md` |
   | `templates/commands/taskstoissues.md` | `.claude/commands/speckit.taskstoissues.md` |
   | `memory/constitution.md` | `.specify/memory/constitution.md` (**受保護**) |

3. 分類變更：
   - **新增**：upstream 有但本地沒有的檔案
   - **修改**：兩邊都有但 hash 不同的檔案
   - **受保護**：在 `protected_files` 清單中的檔案（僅提示，不更新）

4. 輸出差異報告：

   ```markdown
   ### 檔案差異分析

   | 狀態 | 檔案 | 說明 |
   |------|------|------|
   | 新增 | templates/vscode-settings.json | upstream 新增檔案 |
   | 修改 | templates/spec-template.md | 內容有變更 |
   | 受保護 | memory/constitution.md | 專案特定憲法，不同步 |

   **摘要**：
   - 新增：X 個檔案
   - 修改：Y 個檔案
   - 受保護：Z 個檔案
   ```

5. 如果模式是 `diff`，到此結束。

### 4. 衝突偵測（update/full 模式）

1. 檢查受保護檔案：
   - 讀取 `sync-metadata.json` 中的 `protected_files`
   - 如果 upstream 有更新，僅輸出提示訊息，不更新

2. 檢查本地自訂修改：
   - 比較 `file_tracking` 中的 `local_hash` 與目前檔案 hash
   - 如果不同，表示本地有自訂修改，標記為潛在衝突

3. 輸出衝突報告：

   ```markdown
   ### 衝突檢測

   **受保護檔案**（不會被更新）：
   - `.specify/memory/constitution.md` - 專案特定憲法

   **本地修改**（需確認是否覆蓋）：
   - [列出有本地修改的檔案]

   ⚠️ 執行更新將覆蓋上述「本地修改」的檔案。
   是否繼續？建議先執行 `/speckit.sync diff` 確認變更。
   ```

4. 詢問使用者確認（如有衝突）。

### 5. 更新執行（update/full 模式）

1. **建立備份**：
   ```powershell
   .specify/scripts/powershell/sync-speckit.ps1 -Action backup -SourceDir ".specify/templates"
   .specify/scripts/powershell/sync-speckit.ps1 -Action backup -SourceDir ".claude/commands"
   ```

2. **下載並更新檔案**：

   對每個需要更新的檔案：
   ```powershell
   .specify/scripts/powershell/sync-speckit.ps1 -Action download -File "[upstream_path]" -OutputFormat json
   ```

   將下載的內容寫入對應的本地路徑。

3. **更新 metadata**：

   更新 `.specify/sync-metadata.json`：
   - `upstream.last_synced.version` = 最新版本
   - `upstream.last_synced.date` = 今天日期
   - `upstream.last_synced.commit` = 最新 commit
   - `file_tracking.[file].upstream_hash` = 下載檔案的 hash
   - `file_tracking.[file].local_hash` = 更新後的 hash
   - `file_tracking.[file].last_sync` = 今天日期

   新增 `sync_history` 記錄：
   ```json
   {
     "date": "[ISO 8601 日期]",
     "from_version": "[舊版本]",
     "to_version": "[新版本]",
     "files_updated": [數量],
     "files_added": [數量],
     "conflicts_resolved": 0
   }
   ```

4. 如果模式是 `update`，到此結束並輸出更新報告。

### 6. 中文化（full 模式）

1. 對每個新增或更新的檔案執行中文化：

2. **中文化策略**：

   **翻譯範圍**：
   - ✅ 翻譯：指令 `description:` 欄位
   - ✅ 翻譯：Markdown 區塊標題（`##`、`###`）
   - ✅ 翻譯：說明文字和步驟描述
   - ✅ 翻譯：表格中的說明欄位
   - ❌ 保留英文：程式碼區塊（```）內容
   - ❌ 保留英文：變數名稱、檔案路徑
   - ❌ 保留英文：YAML frontmatter 的 key（只翻譯 value）
   - ❌ 保留英文：技術術語（見下方）

   **技術術語對照表**（從 `sync-metadata.json` 的 `terminology` 欄位讀取）：

   | 英文 | 中文 |
   |------|------|
   | specification | 規格 |
   | template | 範本 |
   | checklist | 檢查清單 |
   | implementation | 實作 |
   | requirement | 需求 |
   | user story | 使用者故事 |
   | acceptance criteria | 驗收標準 |
   | functional requirement | 功能需求 |
   | success criteria | 成功標準 |
   | data model | 資料模型 |
   | contract | 契約 |
   | validation | 驗證 |
   | clarification | 釐清 |
   | handoff | 切換 |

   **保留英文的術語**（不翻譯）：
   - Git 相關：commit, branch, merge, push, pull, PR
   - 程式概念：function, class, module, API, CLI, JSON, YAML
   - 框架名稱：NoDriver, Selenium, pytest, PowerShell
   - 專有名詞：Claude, GitHub, spec-kit

   **翻譯品質標準**：
   1. 使用繁體中文（台灣語感）
   2. 禁止使用簡體中文
   3. 禁止使用中國大陸用語（例：「文檔」→「文件」、「視頻」→「影片」）
   4. 保持技術準確性
   5. 句式自然流暢

3. **更新中文化狀態**：

   更新 `file_tracking.[file].status` = `"localized"`

### 7. 報告輸出

輸出完整的同步報告：

```markdown
## Speckit 同步完成報告

**同步資訊**
- 同步時間：[日期時間]
- 版本變更：[舊版本] → [新版本]
- 操作模式：[check/diff/update/full]

### 變更摘要

| 類型 | 數量 |
|------|------|
| 新增檔案 | X |
| 更新檔案 | Y |
| 中文化檔案 | Z |
| 跳過（受保護）| N |

### 詳細變更清單

**新增的檔案**：
- [列出新增檔案]

**更新的檔案**：
- [列出更新檔案]

**中文化的檔案**：
- [列出中文化檔案]

**受保護的檔案**（未更新）：
- `.specify/memory/constitution.md` - 專案特定憲法

### 備份資訊

備份已建立於：`.specify/backup/[timestamp]/`

### 後續建議

1. 執行 `/speckit.analyze` 檢查一致性
2. 審查中文化內容是否準確
3. 如需還原，可從備份目錄複製檔案
```

---

## 受保護檔案政策

以下檔案永不被 upstream 覆蓋：

| 檔案 | 原因 |
|------|------|
| `.specify/memory/constitution.md` | 專案特定憲法（Tickets Hunter） |
| `.specify/sync-metadata.json` | 本地同步狀態 |

當 upstream 的受保護檔案有更新時，僅輸出提示訊息：

```markdown
⚠️ **受保護檔案有 upstream 更新**

`.specify/memory/constitution.md` 在 upstream 有變更。
由於此檔案為專案特定憲法，不會自動更新。

如需參考 upstream 變更，請執行：
```powershell
.specify/scripts/powershell/sync-speckit.ps1 -Action download -File "memory/constitution.md"
```
```

---

## 錯誤處理

### GitHub API 限制

如果遇到 API 速率限制錯誤：

```markdown
⚠️ **GitHub API 速率限制**

您已達到 GitHub API 的請求限制（60 次/小時，未認證）。

**解決方案**：
1. 等待 1 小時後重試
2. 使用 `GITHUB_TOKEN` 環境變數提高限制
3. 使用離線模式（僅顯示快取的版本資訊）
```

### 網路連線失敗

```markdown
⚠️ **網路連線失敗**

無法連線到 GitHub。請檢查網路連線後重試。

**離線資訊**（來自快取）：
- 上次同步版本：[version]
- 上次同步日期：[date]
```

---

## 一般指南

### 使用建議

1. **定期檢查**：建議每週執行 `/speckit.sync check` 檢查是否有更新
2. **謹慎更新**：更新前先執行 `/speckit.sync diff` 確認變更內容
3. **保留備份**：更新會自動建立備份，可隨時還原
4. **中文化審查**：`full` 模式執行後，建議人工審查翻譯品質

### 還原步驟

如需還原到之前的版本：

1. 找到備份目錄：`.specify/backup/[timestamp]/`
2. 複製需要還原的檔案到對應位置
3. 更新 `sync-metadata.json` 的相關欄位

### 自訂術語

如需新增或修改術語翻譯：

1. 編輯 `.specify/sync-metadata.json`
2. 在 `terminology` 欄位新增或修改對應關係
3. 下次執行 `/speckit.sync full` 時會使用新的術語表
