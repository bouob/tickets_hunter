---
description: "啟動 MCP 除錯模式，支援兩種運行模式"
allowed-tools: ["Bash", "Read", "Edit", "AskUserQuestion"]
model: sonnet
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# MCP 除錯模式啟動

此指令用於啟動 Chrome 除錯模式並設定 MCP 連接。使用固定端口 9222，無需每次重啟 Claude Code。

## 執行流程

### 步驟 1：詢問運行模式

使用 `AskUserQuestion` 工具詢問使用者要執行的模式：

**選項 1：測試 NoDriver 設定**
- 啟動 Chrome（如尚未運行）
- 透過 NoDriver 連接並執行 settings.json 設定
- 適合測試搶票流程、驗證設定

**選項 2：直接開啟網頁**
- 僅啟動 Chrome（如尚未運行）
- 不執行 NoDriver，手動瀏覽網頁
- 適合檢查頁面結構、手動測試

### 步驟 2：檢查 Chrome 是否已運行

```bash
netstat -ano | findstr :9222
```

如果端口 9222 沒有監聽，執行步驟 3 啟動 Chrome。
如果已經在監聽，跳過步驟 3。

### 步驟 3：啟動 Chrome（如需要）

```bash
scripts/start_chrome_debug.bat
```

等待 3 秒讓 Chrome 完全啟動。

### 步驟 4：根據選擇的模式執行

#### 如果選擇「測試 NoDriver 設定」：

```bash
cd "D:/Desktop/bouob-TicketHunter(MaxBot)/tickets_hunter"
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
python -u src/nodriver_tixcraft.py --input src/settings.json --mcp_connect 9222
```

#### 如果選擇「直接開啟網頁」：

不需要執行額外指令，Chrome 已經準備好。
可以使用 MCP 工具直接操作瀏覽器。

### 步驟 5：確認 MCP 連接

驗證 `.mcp.json` 端口設定為 9222：
```json
"--browserUrl",
"http://127.0.0.1:9222"
```

如果設定正確，MCP 工具即可使用。

---

## MCP 重新連接

如果 Chrome 關閉或連接斷開，使用以下指令重新連接（無需重啟 Claude Code）：

```
/mcp reconnect chrome-devtools
```

## 常用 MCP 工具

| 工具 | 用途 |
|------|------|
| `mcp__chrome-devtools__take_snapshot` | 擷取 DOM 結構 |
| `mcp__chrome-devtools__take_screenshot` | 截圖 |
| `mcp__chrome-devtools__list_network_requests` | 檢查 API 呼叫 |
| `mcp__chrome-devtools__evaluate_script` | 執行 JavaScript |
| `mcp__chrome-devtools__click` | 點擊元素 |
| `mcp__chrome-devtools__navigate_page` | 導航到指定 URL |

## 注意事項

- 使用獨立 Chrome profile，登入狀態會保留
- Chrome 136+ 不允許預設 profile 進行遠程除錯，必須使用 `--user-data-dir`
- 端口固定為 9222，`.mcp.json` 無需每次更新

---

## 資源管理

使用完 MCP 除錯功能後，執行 `/mcpstop` 釋放資源：
- 關閉除錯模式的 Chrome（釋放約 200-400 MB 記憶體）
- 端口 9222 釋放
- MCP server 進入待機狀態（資源佔用極小，約 20-30 MB）

## 相關指令

| 指令 | 用途 |
|------|------|
| `/mcpstop` | 停止 MCP 除錯模式 |
| `/mcp-sync` | 同步官方 MCP 更新 |

## 進階文檔

查閱 Chrome DevTools Skill 獲取完整工具參考：`.claude/skills/chrome-devtools-skill/`
