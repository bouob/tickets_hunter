---
description: "分析開啟狀態的 GitHub issues，整理相似問題並提供處理建議"
model: Opus
allowed-tools: ["Bash", "Task"]
---

# Review GitHub Issues

分析 Tickets Hunter 專案的 GitHub issues，自動處理常見問題並生成分析報告。

## 執行流程

### 階段 0：快速過濾
跳過已有 `duplicate`/`wontfix` 標籤、含 `[Resolved]`/`[Fixed]` 標題、或已有 bot 處理留言的 issues。

### 階段 1：抓取 Open Issues
```bash
gh issue list --state open --limit 100 --json number,title,body,labels,createdAt,updatedAt,author,url
```
檢查評論中的關鍵詞：「已解決」「修好」「沒問題」「已修復」「無法重現」

### 階段 1.5：檢查 Owner 回覆狀態（重要）
對每個 Open Issue 執行：
```bash
gh issue view <n> --json comments
```

**Owner 回覆關鍵詞檢測**（author.login = "bouob"）：

| 關鍵詞模式 | 狀態標記 | 自動動作 |
|-----------|---------|----------|
| 「下個版本」「下次 release」「已修正」「已修復」「已處理」 | 🔧 待發布 | 自動關閉 + 留言（範本 9） |
| 「請補充」「請提供」「需要更多資訊」 | ⏳ 等待回覆 | 無動作，標記在報告中 |
| 「無法重現」「無法複製」 | ❓ 待確認 | 無動作，標記在報告中 |
| 「已知問題」「known issue」 | 📌 已知問題 | 無動作，標記在報告中 |
| 「不會修復」「wontfix」「won't fix」 | ❌ 不修復 | 自動關閉 + 加標籤 |

**自動關閉條件**：
- Owner 回覆包含「下個版本修正」「已修正待發布」等關鍵詞
- Issue 尚未關閉
- 動作：關閉 issue 並留言通知使用者等待下次 release

### 階段 2：檢查 Closed Issues 新回覆
```bash
gh issue list --state closed --limit 100 --json number,title,body,labels,closedAt,updatedAt,author,url,comments
```
條件：`updatedAt > closedAt` 且最後評論非 bot

### 階段 3-4：自動處理

| 檢查項目 | 條件 | 動作 |
|---------|------|------|
| 標題不明確 | 含 `<請描述問題>` 等模板值 | 自動修正標題（不通知） |
| 版本未提供 | Bug issue 無版本號 | 留言提醒 → 3天後關閉 |
| 必填欄位缺失 | Bug issue 缺「票務平台」或「目標網址」 | 留言提醒 → 3天後關閉 |
| 標籤錯誤 | 內容與標籤不符 | 自動修正 bug↔enhancement |
| 重複問題 | 相同平台+相似描述 | 關閉並引用原 issue |

**必填欄位判斷**：
- 票務平台：需有具體名稱（TixCraft/KKTIX/iBon/TicketPlus/KHAM/FamiTicket/Ticketmaster/Cityline），非 `[TixCraft/ibon/KKTIX]` 預設值
- 目標網址：需有有效 URL（含 http:// 或 https://）

**標籤判斷**：
- Bug：標題含 `[BUG]`、body 含「🐛 Bug 描述」、描述功能異常
- Enhancement：標題含 `[FEATURE]`、body 含「🚀 功能需求」、描述新功能

### 階段 5：分析分組
按平台（TixCraft/KKTIX/iBon 等）和功能模組（登入/驗證碼/選擇等）分組，評估優先度。

## 輸出格式

```
### ⚠️ 需重新開啟（置頂，若有）
#123 - 標題 | 關閉:日期 | 最後回覆:日期 | 建議: gh issue reopen 123

### 📊 Issues 總覽
總數/Bug/功能請求/待處理/已跳過/自動處理統計

### 🔧 Owner 已回覆（按狀態分類）

#### 待發布修正（將自動關閉）
| # | 標題 | Owner 回覆摘要 | 回覆日期 | 動作 |
|---|------|---------------|---------|------|
| #123 | xxx | 「下個版本修正」 | 12/09 | 🔒 自動關閉 |

#### ⏳ 等待使用者回覆
| # | 標題 | Owner 詢問內容 | 回覆日期 | 等待天數 |
|---|------|--------------|---------|---------|
| #456 | xxx | 「請補充版本號」 | 12/08 | 2 天 |

#### ❓ 待確認問題
| # | 標題 | Owner 回覆 | 建議 |
|---|------|----------|------|
| #789 | xxx | 「無法重現」 | 等待回覆或關閉 |

### 🔥 高優先度（無 Owner 回覆）
分組列出：#編號 - 摘要 | 平台 | 影響 | 狀態 | 建議

### ⚠️ 中優先度 / 💡 低優先度
同上格式

### 🔧 已自動處理
- 標題修正：#123: "舊" → "新"
- 重複關閉：#456 (重複 #123)
- 必填提醒：#789 - 缺少欄位
- 標籤修正：#101: enhancement → bug
- 待發布關閉：#101 - Owner 已確認下版本修正

### ✅ 已解決/已修復（無需處理）
### 🔗 可能重複（需手動確認）
### 📋 處理建議順序
```

## 回應範本

使用 `issue-reply` skill 的標準模板回覆，確保格式一致。

### 模板對應表

| 場景 | 模板檔案 | 變數 | 動作 |
|------|---------|------|------|
| 已在版本中修正 | `templates/fixed.md` | `{{version}}`, `{{summary}}` | `gh issue close` |
| 確認修正，待發布 | `templates/pending-release.md` | 無 | `gh issue close` |
| 請求補充資訊 | `templates/missing-info.md` | `{{fields}}` | `gh issue comment` |
| 未補充資訊關閉 | `templates/missing-info-close.md` | `{{reason}}` | `gh issue close` |
| 重複問題 | `templates/duplicate.md` | `{{original}}` | `gh issue close` |

### 使用方式

1. 從 `.claude/skills/issue-reply/templates/` 讀取模板
2. 將 `{{variable}}` 替換為實際值
3. 使用 `gh issue comment` 或 `gh issue close --comment` 發送

### 模板原則

- 簡潔：不透露技術細節
- 行動導向：告訴使用者下一步該做什麼
- 統一簽名：所有模板結尾為 `---\n*Claude Code*`

## 技術參考

### GitHub CLI 命令
```bash
# 列出 issues
gh issue list --state open/closed --limit 100 --json number,title,body,labels,...

# 查看單一 issue 的評論（含 author 資訊）
gh issue view <n> --json comments,author,createdAt,updatedAt

# 編輯 issue
gh issue edit <n> --title "新標題"
gh issue edit <n> --remove-label "X" --add-label "Y"

# 關閉 issue（使用範本 9）
gh issue close <n> --comment "$(cat <<'EOF'
**此問題已確認並將在下個版本修正**
請等待下次 Release 發布後更新至最新版本。
發布時會在 [Releases](https://github.com/bouob/tickets_hunter/releases) 頁面公告。
若更新後問題仍存在，請開啟新 issue 回報。
---
*Claude Code*
EOF
)"

# 其他命令
gh issue comment <n> --body "..."
gh search issues "關鍵字" --repo bouob/tickets_hunter --state open
```

### Owner 回覆檢測邏輯
```
對於每個 Open Issue:
1. 取得評論列表
2. 過濾 author.login == "bouob" 的評論
3. 檢查最後一則 owner 評論的內容：
   - 匹配「下個版本」「已修正」→ 自動關閉
   - 匹配「請補充」「請提供」→ 標記等待回覆
   - 匹配「無法重現」→ 標記待確認
4. 計算等待天數 = 今天 - owner 回覆日期
```

## 優先度標準
- **高**：核心搶票功能、多人回報
- **中**：特定平台、使用者體驗
- **低**：文件、UI 優化
