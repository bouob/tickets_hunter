# CLAUDE.md v3.0（精簡版）

**專案**：Tickets Hunter - 多平台搶票自動化系統
**版本**：v3.0
**最後更新**：2026-01-05

---

## 📜 憲法（行為紅線）

**位置**：`.specify/memory/constitution.md` | **版本**：3.0.0

憲法定義**不可違反的行為規則**，不限制思考方式。

### 8 大行為規範（速記）

| 原則 | 類型 | 核心要點 |
|------|------|----------|
| **I. 技術架構** | MUST | NoDriver > UC > Selenium |
| **II. 共用庫保護** | MUST | util.py 改動需跨平台/跨 Driver 分析 |
| **III. 設定驅動** | MUST | settings.json 控制所有可配置行為 |
| **IV. 程式碼安全** | MUST | 禁 emoji in .py、禁硬寫敏感資訊 |
| **V. Git 工作流程** | MUST | /gsave 提交、雙 Repo 安全、提交前測試 |
| **VI. 測試驗證** | SHOULD | 核心修改應有測試驗證 |
| **VII. 文件同步** | SHOULD | 程式碼變更應同步文件、新 API 更新文件 |
| **VIII. 測試紀律** | MUST/SHOULD | 新功能寫測試、測試失敗必修正、重構不破壞測試 |

**MUST**：無例外，違反阻擋合併
**SHOULD**：允許例外，需記錄理由

**詳細規範**：查詢 `.specify/memory/constitution.md`

---

## 🛡️ util.py 跨平台分析規則（NON-NEGOTIABLE）

**觸發條件**：任何涉及 `util.py` 或 `nodriver_util.py` 的修改

### 強制執行流程

**修改前必須啟動 Agent 進行分析**：

```
當修改 util.py 或 nodriver_util.py 時：
1. 使用 Task tool (subagent_type=Explore) 搜尋所有呼叫點
2. 分析每個平台的使用方式
3. 確認修改不會破壞任何平台
4. 列出影響範圍報告
```

### 關鍵共用函式清單

| 函式 | 用途 | 影響平台 |
|------|------|----------|
| `get_target_index_by_mode()` | 計算目標索引 | 全平台 |
| `get_target_item_from_matched_list()` | 取得目標物件 | 全平台 |
| `get_debug_mode()` | 安全讀取 debug 設定 | 全平台 |
| `parse_keyword_string_to_array()` | 解析關鍵字字串 | 全平台 |

### 修改前檢查清單

- [ ] 啟動 Explore Agent 搜尋所有呼叫點
- [ ] 確認 TixCraft 相容性
- [ ] 確認 iBon 相容性（Shadow DOM）
- [ ] 確認 KKTIX 相容性
- [ ] 確認 TicketPlus 相容性
- [ ] 確認 KHAM 相容性
- [ ] 確認 FamiTicket 相容性
- [ ] 確認 Cityline 相容性
- [ ] 確認 UDN 相容性

### 違規後果

**未經分析直接修改 util.py**：
- 可能導致多個平台同時失效
- 回滾困難（影響範圍不明）
- 違反憲法第 II 條

---

## 🚀 Quick Reference（速查表）

### 開發工作流程

**詳細流程請參考 Skill**：`.claude/skills/ticket-dev-skill/`

| 任務類型 | Skill 工作流程 |
|----------|----------------|
| Bug 修復 | `workflows/bug-fix.md` |
| 新增功能 | `workflows/new-feature.md` |
| 新平台開發 | `workflows/new-platform.md` |

### 關鍵指令速查

| 任務 | 指令 | 說明 |
|------|------|------|
| 提交變更 | `/gsave` | 自動分離公開/機敏檔案 |
| 推送代碼 | `/gpush` | 推送所有 commits 到私人庫 |
| 發布 PR | `/publicpr` | 建立 PR 到公開庫 |
| MCP 即時除錯 | `/mcpstart` | 啟動 Chrome 除錯模式 |
| 停止 MCP 除錯 | `/mcpstop` | 關閉 Chrome 除錯模式 |
| 規格分析 | `/speckit.analyze` | 跨產物一致性檢查 |

### 快速測試

**測試前必須刪除** `MAXBOT_INT28_IDLE.txt`

```bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

---

## 🔗 Git 工作流程（NON-NEGOTIABLE）

### 核心原則

- ✅ **強制使用 `/gsave` 建立 commit**
- ❌ **嚴禁使用 `git commit` 手動提交**
- ✅ **只推送到私人庫**（`private`）
- ❌ **嚴禁直接推送到公開庫**（`origin`）

### 標準流程

```bash
/gsave          # 1. 提交變更
/gpush          # 2. 推送到私人庫
/publicpr       # 3. 建立 PR 到公開庫（僅發布時）
```

### Repo 位址

- 私人庫：`https://github.com/bouob/private-tickets-hunter.git` (remote: `private`)
- 公開庫：`https://github.com/bouob/tickets_hunter.git` (remote: `origin`)

**詳細說明**：`docs/12-git-workflow/dual-repo-workflow.md`

---

## 📐 程式碼規範（NON-NEGOTIABLE）

### Emoji 使用規範

- **✅ 允許**：Emoji 僅限 `*.md` 文件中使用
- **❌ 禁止**：`*.py`、`*.js` 中禁止 emoji
- **❌ 禁止**：print()、console.log() 輸出中禁止 emoji
- **原因**：emoji 導致 Windows cp950 編碼錯誤

**正確**：`print("[SUCCESS] 操作成功")`
**錯誤**：`print("✅ 操作成功")`

---

## 🗣️ 使用者溝通規範（NON-NEGOTIABLE）

**核心原則**：回應使用者時，使用「UI 名稱」而非「技術名稱」。

**錯誤**：請將 `settings.json` 中的 `advanced.verbose` 設為 `true`
**正確**：請在「進階設定」中，啟用「輸出除錯訊息」選項

**完整對照表**：`.claude/skills/ticket-dev-skill/reference/settings-quick-ref.md`

---

## 🎯 開發策略：NoDriver First

**優先順序**：
1. **NoDriver** - 推薦（預設、最佳反偵測）
2. **UC (Undetected Chrome)** - 舊版回退
3. **Selenium** - 標準場景

**平台維護策略**：
- NoDriver 版本：接受新功能開發 + Bug 修復
- Chrome Driver 版本：僅嚴重錯誤修復（維護模式）

---

## 📚 文件導航

### 核心文件

| 類別 | 文件 |
|------|------|
| **12 階段標準** | `docs/02-development/ticket_automation_standard.md` |
| **函數索引** | `docs/02-development/structure.md` |
| **機制詳解** | `docs/03-mechanisms/README.md` |
| **NoDriver API** | `docs/06-api-reference/nodriver_api_guide.md` |
| **疑難排解** | `docs/08-troubleshooting/README.md` |

### Skill 導航

| Skill | 用途 |
|-------|------|
| `ticket-dev-skill` | 12 階段開發標準與工作流程 |
| `chrome-devtools-skill` | MCP 瀏覽器除錯 |
| `issue-reply` | GitHub Issue 回覆模板 |

---

## 🔧 MCP 即時除錯

```bash
/mcpstart    # 啟動
/mcpstop     # 停止
```

**常用工具**：
- `mcp__chrome-devtools__take_snapshot` - 擷取 DOM
- `mcp__chrome-devtools__take_screenshot` - 截圖
- `mcp__chrome-devtools__list_network_requests` - 檢查 API

**詳細指南**：`.claude/skills/chrome-devtools-skill/SKILL.md`

---

## 🏗️ speckit 工作流程

**使用時機**：重大功能開發、跨模組功能

```
/speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement → /speckit.analyze
```

---

## 📋 專案追蹤

| 文件 | 用途 |
|------|------|
| `docs/10-project-tracking/todo.md` | 待辦事項清單 |
| `docs/10-project-tracking/accept_changelog.md` | 自動執行記錄 |
| `docs/10-project-tracking/issues-faq-tracking.md` | Issues FAQ |

### Accept Edits On 模式

記錄位置：`docs/10-project-tracking/accept_changelog.md`
記錄時機：完成功能模組、修復重大問題、架構變更後

---

## 💡 使用原則

- ❌ 不要在 CLAUDE.md 重複 docs 內容
- ✅ 指向對應 docs 文件或 Skill
- ✅ CLAUDE.md 只保留強制規則與快速索引

---

- 當我說出「檢查紀錄」代表要求你檢查 `.temp/logs.txt`
