**Chrome DevTools MCP 整合指南**
**最後更新**: 2025-12-07

---

# Chrome DevTools MCP 整合指南

> **目標**: 建立 NoDriver 跨平台自動化測試的標準方法，透過 Claude Code 實現即時除錯、API 檢查與網路監控。

## 概述

Chrome DevTools MCP 讓 Claude Code 可以透過 Chrome DevTools Protocol (CDP) 與瀏覽器互動，功能包括：

- 即時頁面快照與截圖
- 網路請求檢查（API 呼叫、回應內容）
- Console 訊息監控
- JavaScript 執行
- DOM 元素互動

---

## 快速參考

### 可用 MCP 工具

| 工具 | 用途 | 常見使用場景 |
|------|------|--------------|
| `navigate_page` | 開啟網址 | 導航到測試頁面 |
| `take_snapshot` | 擷取 DOM 結構 | 除錯元素選擇器 |
| `take_screenshot` | 截圖 | 視覺驗證 |
| `evaluate_script` | 執行 JavaScript | 測試選擇器邏輯 |
| `list_network_requests` | 列出網路請求 | API 端點檢查 |
| `get_network_request` | 取得請求詳情 | 檢查請求/回應內容 |
| `list_console_messages` | 列出 Console 訊息 | 除錯 JavaScript 錯誤 |
| `fill` | 輸入文字 | 表單測試 |
| `click` | 點擊元素 | 按鈕互動 |

### 連接模式

| 模式 | 設定方式 | 最適用於 |
|------|----------|----------|
| **獨立模式** | 預設 `.mcp.json` | 獨立測試、API 探索 |
| **連接模式** | `--browserUrl` | NoDriver 工作階段除錯 |

---

## 模式一：獨立模式（建議用於測試）

此模式下，MCP 開啟獨立的 Puppeteer 瀏覽器，與 NoDriver 分離。適合用於：
- API 端點探索
- 頁面結構分析
- 實作前的選擇器測試
- 平台特定行為研究

### 設定

`.mcp.json`（預設）：
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

### 使用流程

1. **開啟測試頁面**
```
使用 navigate_page 開啟 https://tixcraft.com/activity/game/xxx
```

2. **擷取 DOM 結構**
```
使用 take_snapshot 取得頁面元素與 UID
```

3. **檢查網路請求**
```
使用 list_network_requests 查看所有 API 呼叫
使用 get_network_request 搭配 reqid 查看請求/回應詳情
```

4. **測試選擇器**
```
使用 evaluate_script 測試選擇器邏輯：
() => document.querySelectorAll('.btn-primary').length
```

---

## 模式二：分離啟動模式（推薦）

此模式下，先獨立啟動固定端口的 Chrome，再讓 NoDriver 連接到該瀏覽器。

### 優點

- **固定端口 9222**：`.mcp.json` 設定一次後永久有效
- **無需重啟 Claude Code**：只需首次設定時重啟
- **Chrome 可長時間運行**：NoDriver 可多次重連
- **登入狀態保留**：使用獨立 profile

### 快速啟動流程

**步驟 1**：啟動固定端口的 Chrome
```bash
scripts/start_chrome_debug.bat
```

**步驟 2**：啟動 NoDriver 連接到該 Chrome
```bash
python src/nodriver_tixcraft.py --input src/settings.json --mcp_connect 9222
```

### 重新連接（Chrome 關閉後）

```bash
# 1. 重新啟動 Chrome
scripts/start_chrome_debug.bat

# 2. 重新連接 MCP（無需重啟 Claude Code）
/mcp reconnect chrome-devtools
```

### `.mcp.json` 設定

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browserUrl",
        "http://127.0.0.1:9222"
      ]
    }
  }
}
```

---

## 模式三：動態端口模式（舊版）

此模式下，NoDriver 啟動新瀏覽器並使用動態隨機端口。使用 `--mcp_debug` 命令列參數即可啟用。

### 重要：NoDriver 的動態端口限制

**NoDriver 設計限制**：NoDriver 使用動態 CDP 端口。

這是因為 NoDriver 的 `browser.py:357-361` 將 `Config(host, port)` 設計為「連接到已存在瀏覽器」的模式，而非「使用指定端口啟動新瀏覽器」。

### 快速啟動：使用 /mcpstart 指令

執行 `/mcpstart` Claude command 可自動完成所有設定步驟：

```bash
# 在 Claude Code 中執行
/mcpstart
```

**Claude 會自動執行以下步驟**：
1. 清除閒置檔案
2. 啟動 NoDriver（使用 `--mcp_debug` 參數）
3. 從 `.temp/mcp_port.txt` 讀取實際端口
4. 自動更新 `.mcp.json` 中的端口設定
5. 提示使用者重啟 Claude Code

**端口檔案位置**：`.temp/mcp_port.txt`（由 NoDriver 自動產生）

---

### 手動啟動流程（備用方式）

如需手動操作，工作流程如下：
1. 啟動 NoDriver 時加上 `--mcp_debug` 參數
2. 從輸出中取得**實際端口號碼**（或讀取 `.temp/mcp_port.txt`）
3. 更新 `.mcp.json` 中的端口設定
4. 重啟 Claude Code 以套用新設定

### 步驟一：使用 --mcp_debug 參數啟動 NoDriver

```bash
# 啟用 MCP 除錯模式
python src/nodriver_tixcraft.py --input src/settings.json --mcp_debug

# 結合其他參數
python src/nodriver_tixcraft.py --input src/settings.json --mcp_debug \
    --homepage "https://kktix.com" \
    --date_keyword "12/25"
```

啟動時會顯示：
```
[MCP DEBUG] Mode enabled - actual port will be shown after browser starts
[MCP DEBUG] Browser started on actual port: 58210
[MCP DEBUG] Update .mcp.json with: --browserUrl http://127.0.0.1:58210
```

**注意**：上面的 `58210` 是範例，每次啟動的端口都不同。

### 步驟二：更新 MCP 設定

根據實際輸出的端口號碼，更新 `.mcp.json`：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browserUrl",
        "http://127.0.0.1:58210"
      ]
    }
  }
}
```

⚠️ **每次 NoDriver 重新啟動後都需要更新此端口！**

### 步驟三：重啟 Claude Code

修改 MCP 設定後，需要重啟 Claude Code 以重新載入。

### 使用流程

1. **啟動 NoDriver**（在終端機執行，加上 `--mcp_debug` 參數）
```bash
python -u src/nodriver_tixcraft.py --input src/settings.json --mcp_debug
```

2. **等待瀏覽器開啟並記錄端口**
   - NoDriver 會啟動 Chrome 並使用動態端口
   - 終端機會顯示實際端口號碼，例如：`[MCP DEBUG] Browser started on actual port: 58210`
   - 複製此端口號碼

3. **更新 `.mcp.json` 並重啟 Claude Code**
   - 將端口號碼更新到 `.mcp.json` 的 `--browserUrl` 參數
   - 重啟 Claude Code 以載入新設定

4. **在 Claude Code 中使用 MCP 工具**
```
使用 list_pages 確認連接成功
使用 take_snapshot 查看目前頁面狀態
使用 take_screenshot 截取頁面截圖
使用 list_network_requests 監控 API 呼叫
使用 evaluate_script 執行 JavaScript
```

### 限制

- NoDriver 與 MCP 共用同一個瀏覽器實例
- 某些操作可能衝突（例如兩者同時嘗試點擊同一元素）
- 建議：用於觀察/除錯，避免主動操作

---

## 自動化測試工作流程

### 使用命令列參數快速測試

NoDriver 支援命令列參數覆蓋 settings.json：

```bash
# 覆蓋日期關鍵字
python nodriver_tixcraft.py --input settings.json --date_keyword "12/25"

# 覆蓋區域關鍵字
python nodriver_tixcraft.py --input settings.json --area_keyword "搖滾區"

# 覆蓋自動選擇模式
python nodriver_tixcraft.py --input settings.json --date_auto_select_mode "from top to bottom"

# 組合覆蓋
python nodriver_tixcraft.py --input settings.json \
    --date_keyword "12/25" \
    --area_keyword "VIP" \
    --ticket_number 2
```

### 可用命令列參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `--input` | 設定檔路徑（必要） | `--input settings.json` |
| `--homepage` | 覆蓋首頁網址 | `--homepage https://tixcraft.com/...` |
| `--ticket_number` | 覆蓋票數 | `--ticket_number 2` |
| `--headless` | 無頭模式 | `--headless true` |
| `--date_keyword` | 覆蓋日期關鍵字 | `--date_keyword "12/25"` |
| `--date_auto_select_mode` | 覆蓋日期選擇模式 | `--date_auto_select_mode "random"` |
| `--area_keyword` | 覆蓋區域關鍵字 | `--area_keyword "搖滾區"` |
| `--area_auto_select_mode` | 覆蓋區域選擇模式 | `--area_auto_select_mode "center"` |
| `--browser` | 覆蓋瀏覽器類型 | `--browser chrome` |
| `--window_size` | 視窗大小 | `--window_size 1920x1080` |
| `--proxy_server` | 代理伺服器 | `--proxy_server 127.0.0.1:8080` |
| `--mcp_debug` | MCP 除錯模式（動態端口） | `--mcp_debug` |
| `--mcp_connect` | 連接到已存在的 Chrome（固定端口） | `--mcp_connect 9222` |

### 使用 settings.json 啟用 MCP 除錯

除了命令列參數外，也可以在 `settings.json` 中啟用 MCP 除錯：

```json
{
  "advanced": {
    "mcp_debug_port": 1
  }
}
```

**設定值說明**：
- `0` = 停用 MCP 除錯（預設）
- 大於 `0` = 啟用 MCP 除錯模式

⚠️ **注意**：由於 NoDriver 的設計限制，這個設定值只是「啟用標記」。實際端口會是動態的，需要在瀏覽器啟動後從輸出中取得。

**優先順序**：命令列參數 `--mcp_debug` > `settings.json` 中的 `mcp_debug_port`

### 各平台測試網址

```bash
# TixCraft
--homepage "https://tixcraft.com/activity/game/xxx"

# iBon
--homepage "https://ticket.ibon.com.tw/activities/xxx"

# KKTIX
--homepage "https://kktix.com/events/xxx"

# TicketPlus
--homepage "https://ticketplus.com.tw/activity/xxx"

# KHAM
--homepage "https://kham.com.tw/application/xxx"

# FamiTicket
--homepage "https://www.famiticket.com.tw/..."

# Cityline（香港）
--homepage "https://www.cityline.com/..."
```

---

## API 檢查工作流程

### 擷取網路流量

1. **導航到目標頁面**
```
使用 navigate_page 開啟票務頁面
```

2. **執行操作**（例如：選擇日期、點擊按鈕）
```
使用 click 搭配元素 UID
```

3. **列出最近請求**
```
使用 list_network_requests 搭配 resourceTypes: ["xhr", "fetch"]
```

4. **檢查特定請求**
```
使用 get_network_request 搭配 reqid 查看：
- 請求 URL
- 請求標頭
- 回應狀態
- 回應內容（如果可用）
```

### 常見需監控的 API 端點

| 平台 | 端點模式 | 用途 |
|------|----------|------|
| TixCraft | `/ticket/area/*` | 區域可用性檢查 |
| TixCraft | `/ticket/verify/*` | 驗證碼驗證 |
| iBon | `/api/activities/*` | 活動資料 |
| KKTIX | `/events/*/registrations` | 報名 API |
| TicketPlus | `/api/ticket/*` | 票券選擇 |

---

## Claude Code 使用範例

### 範例一：測試日期選擇邏輯

```
1. 導航到 TixCraft 活動頁面
2. 使用 take_snapshot 查看可用日期
3. 使用 evaluate_script 測試日期匹配：
   () => {
     const dates = document.querySelectorAll('button.btn-default');
     return Array.from(dates).map(d => d.textContent);
   }
4. 使用 click 點擊特定日期
5. 監控網路請求查看票務 API 呼叫
```

### 範例二：除錯區域選擇

```
1. 導航到區域選擇頁面
2. 使用 take_snapshot 分析區域結構
3. 使用 evaluate_script 測試選擇器：
   () => {
     return document.querySelectorAll('[class*="area"]').length;
   }
4. 使用 list_console_messages 檢查 JavaScript 錯誤
```

### 範例三：API 回應分析

```
1. 導航到目標頁面
2. 使用 list_network_requests 篩選 xhr/fetch 請求
3. 找到票務可用性的 API 呼叫
4. 使用 get_network_request 查看：
   - 回應格式（JSON 結構）
   - 錯誤訊息
   - 可用座位數
```

---

## 疑難排解

### MCP 連接問題

| 問題 | 原因 | 解決方案 |
|------|------|----------|
| "Failed to connect to browser" | 端口被佔用 | 清理端口（見下方說明） |
| "Failed to connect" | 瀏覽器未執行 | 先啟動 NoDriver |
| "Connection refused" | 端口錯誤 | 檢查 Config 中的 port 設定 |
| "No pages found" | 瀏覽器崩潰 | 重啟 NoDriver |

### 端口衝突（最常見問題）

NoDriver 現在會自動檢測端口衝突並顯示警告：
```
[MCP DEBUG] WARNING: Port 9222 is already in use!
[MCP DEBUG] Try: netstat -ano | findstr :9222
[MCP DEBUG] Or use different port: --mcp_debug 9223
```

**解決方法 1：清理端口**
```bash
# Windows - 檢查什麼程式正在使用端口 9222
netstat -ano | findstr :9222

# 終止該程序
taskkill /F /PID <pid>

# 或關閉所有 Chrome 實例
taskkill /F /IM chrome.exe
```

**解決方法 2：使用不同端口**
```bash
# 使用命令列參數
python src/nodriver_tixcraft.py --input src/settings.json --mcp_debug 9223
```

或在 `settings.json` 中設定：
```json
{
  "advanced": {
    "mcp_debug_port": 9223
  }
}
```

然後更新 `.mcp.json`：
```json
"args": ["chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9223"]
```

**解決方法 3：重啟 Claude Code**
MCP 設定變更後需要重啟 Claude Code 以重新載入 `.mcp.json`。

### 快照逾時

如果 `take_snapshot` 逾時：
1. 檢查頁面是否完全載入
2. 改用 `take_screenshot` 進行視覺檢查
3. 如果頁面載入較慢，增加逾時時間

---

## 最佳實踐

### 1. 先使用獨立模式

從獨立模式開始：
- 了解頁面結構
- 測試選擇器
- 探索 API 端點

然後切換到連接模式：
- 即時除錯
- 工作階段狀態檢查

### 2. 使用命令列參數快速測試

不要修改 `settings.json`，改用命令列參數：
```bash
python nodriver_tixcraft.py --input settings.json --date_keyword "測試"
```

### 3. 定期監控網路以偵測 API 變更

平台 API 經常變動，定期使用 `list_network_requests`：
- 偵測新 API 端點
- 監控回應格式變更
- 追蹤認證需求變化

### 4. 結合日誌輸出分析

同時使用 MCP 與日誌檔案分析：
```bash
# 終端機 1：執行 NoDriver 並輸出日誌
python -u nodriver_tixcraft.py --input settings.json > .temp/test_output.txt 2>&1

# Claude Code：使用 MCP 即時檢查
使用 take_snapshot、list_network_requests 等工具

# 終端機 2：檢查日誌
grep "[DATE KEYWORD]" .temp/test_output.txt
```

---

## 相關文件

- [測試執行指南](./testing_execution_guide.md) - 標準測試執行方法
- [除錯方法論](./debugging_methodology.md) - Shadow DOM 與背景測試
- [NoDriver API 指南](../06-api-reference/nodriver_api_guide.md) - NoDriver API 參考
- [CDP 協議參考](../06-api-reference/cdp_protocol_reference.md) - Chrome DevTools Protocol

---

**更新日期**: 2025-12-07
**作者**: Claude Code Assistant
