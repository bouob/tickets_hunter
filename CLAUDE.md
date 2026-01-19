# CLAUDE.md v4.0

**專案**：Tickets Hunter - 多平台搶票自動化系統
**最後更新**：2026-01-19

---

## 🎯 快速決策（WHAT）

### 任務分流表

| 任務特徵 | 建議路徑 | 說明 |
|----------|----------|------|
| 單一 Bug 修復 | 直接修復 | 參考 `workflows/bug-fix.md` |
| 跨模組功能 | `/speckit.specify` | 完整規格流程 |
| 新平台開發 | `/speckit.specify` | 參考 `workflows/new-platform.md` |
| 簡單功能新增 | 直接實作 | 影響 < 3 檔案 |
| UI/UX 改進 | `/mcpstart` | MCP 即時除錯 |

### speckit 決策矩陣

| 條件 | 使用 speckit? |
|------|---------------|
| 影響 > 3 個檔案 | ✅ 是 |
| 涉及多平台 | ✅ 是 |
| 新增 API/協議 | ✅ 是 |
| 單檔 Bug 修復 | ❌ 否 |
| 設定項調整 | ❌ 否 |

### 8 大行為紅線（索引）

| 原則 | 類型 | 核心要點 |
|------|------|----------|
| **I. 技術架構** | MUST | NoDriver > UC > Selenium |
| **II. 共用庫保護** | MUST | util.py 改動觸發 Hook 警告 |
| **III. 設定驅動** | MUST | settings.json 控制所有行為 |
| **IV. 程式碼安全** | MUST | .py 禁 emoji（Hook 強制） |
| **V. Git 工作流程** | MUST | /gsave 提交（Hook 強制） |
| **VI. 測試驗證** | SHOULD | 核心修改應有測試 |
| **VII. 文件同步** | SHOULD | 程式碼變更同步文件 |
| **VIII. 測試紀律** | MUST/SHOULD | 測試失敗必修正 |

**詳細規範**：`.specify/memory/constitution.md`

---

## 🔧 執行規範（HOW）

### Git 工作流程

```bash
/gsave          # 1. 提交變更（自動過濾機敏檔案）
/gpush          # 2. 推送到私人庫
/publicpr       # 3. 建立 PR 到公開庫
```

| 操作 | 允許 | 禁止 |
|------|------|------|
| 提交 | `/gsave` | `git commit` |
| 推送 | `private` remote | `origin` remote |

**Repo 位址**：
- 私人庫：`private` → `bouob/private-tickets-hunter`
- 公開庫：`origin` → `bouob/tickets_hunter`

### speckit 完整流程

```
/speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement → /speckit.analyze
```

| 階段 | 產出 | 用途 |
|------|------|------|
| specify | spec.md | 功能規格 |
| plan | plan.md | 設計方案 |
| tasks | tasks.md | 執行任務 |
| implement | 程式碼 | 實作 |
| analyze | 報告 | 一致性檢查 |

### 使用者溝通規範

**核心原則**：使用「UI 名稱」而非「技術名稱」

| 錯誤 | 正確 |
|------|------|
| 設定 `advanced.verbose` 為 `true` | 在「進階設定」啟用「輸出除錯訊息」 |
| 修改 `settings.json` | 調整相關設定選項 |

**對照表**：`.claude/skills/ticket-dev-skill/reference/settings-quick-ref.md`

### 程式碼規範

| 規範 | .py 檔案 | .md 檔案 |
|------|----------|----------|
| Emoji | ❌ 禁止 | ✅ 允許 |
| 原因 | Windows cp950 編碼 | - |

### 快速測試

```bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

---

## 📚 參考索引（REFERENCE）

### 關鍵指令

| 任務 | 指令 |
|------|------|
| 提交變更 | `/gsave` |
| 推送代碼 | `/gpush` |
| 發布 PR | `/publicpr` |
| MCP 除錯 | `/mcpstart` / `/mcpstop` |
| 規格分析 | `/speckit.analyze` |

### 核心文件

| 類別 | 文件 |
|------|------|
| 12 階段標準 | `docs/02-development/ticket_automation_standard.md` |
| 函數索引 | `docs/02-development/structure.md` |
| 機制詳解 | `docs/03-mechanisms/README.md` |
| NoDriver API | `docs/06-api-reference/nodriver_api_guide.md` |
| 疑難排解 | `docs/08-troubleshooting/README.md` |

### Skill 導航

| Skill | 用途 |
|-------|------|
| `ticket-dev-skill` | 12 階段開發標準 |
| `chrome-devtools-skill` | MCP 瀏覽器除錯 |
| `issue-reply` | GitHub Issue 回覆 |

### 工作流程文件

| 任務 | 文件 |
|------|------|
| Bug 修復 | `workflows/bug-fix.md` |
| 新功能 | `workflows/new-feature.md` |
| 新平台 | `workflows/new-platform.md` |

### MCP 常用工具

| 工具 | 用途 |
|------|------|
| `take_snapshot` | 擷取 DOM |
| `take_screenshot` | 截圖 |
| `list_network_requests` | 檢查 API |

### 專案追蹤

| 文件 | 用途 |
|------|------|
| `docs/10-project-tracking/todo.md` | 待辦事項 |
| `docs/10-project-tracking/accept_changelog.md` | 變更記錄 |

---

## 🛡️ Hooks 強制執行

本專案使用 Hooks 強制執行關鍵規則：

| Hook | 觸發條件 | 行為 |
|------|----------|------|
| util-protection | 編輯 `util.py` | 顯示跨平台分析警告 |
| emoji-check | 編輯 `*.py` | 阻止 emoji 寫入 |
| git-commit-block | 執行 `git commit` | 阻止，要求使用 `/gsave` |

**Hook 腳本位置**：`.claude/hooks/`

---

## 💡 原則

- 不在 CLAUDE.md 重複 docs 內容
- 指向對應 docs 或 Skill
- CLAUDE.md 只保留強制規則與索引

---

- 當我說出「檢查紀錄」代表要求你檢查 `.temp/logs.txt`
