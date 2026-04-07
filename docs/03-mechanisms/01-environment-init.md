# 機制 01：環境初始化 (Stage 1)

**文件說明**：說明搶票自動化系統的環境初始化機制，包含設定載入、瀏覽器啟動與網路封鎖
**最後更新**：2026-03-06

---

## 概述

環境初始化是整個自動化購票系統的第一個階段。系統透過 `cli()` → `main()` 進入點，依序完成：設定載入、瀏覽器啟動、Cookie 注入、網路封鎖與視窗調整。

**核心目標**：建立穩定的 ZenDriver 瀏覽器環境，確保後續階段可順利運作。

**優先度**：🔴 P1 - 核心流程，必須完成

---

## 機制流程

### 1. 程式進入點與設定載入

#### 1.1 CLI 參數解析

`cli()` (行 26289) 使用 `argparse` 解析命令列參數，支援以下覆寫項：

| 參數 | 用途 | 範例 |
|------|------|------|
| `--input` | 指定 settings.json 路徑 | `--input src/settings.json` |
| `--homepage` | 覆寫首頁 URL | `--homepage https://tixcraft.com/...` |
| `--ticket_number` | 覆寫票數 | `--ticket_number 2` |
| `--headless` | 無頭模式 | `--headless True` |
| `--browser` | 瀏覽器類型 | `--browser chrome` |
| `--mcp_debug` | MCP 除錯模式 | `--mcp_debug 9222` |
| `--mcp_connect` | 連線既有 Chrome | `--mcp_connect 9222` |

`cli()` 最終呼叫 `uc.loop().run_until_complete(main(args))` 啟動非同步主流程。

#### 1.2 設定檔載入

`get_config_dict(args)` (行 89) 負責：

1. 讀取 `settings.json` 並以 `json.load()` 解析
2. 呼叫 `settings.migrate_config()` 進行版本遷移
3. 將 CLI 參數覆寫至 `config_dict` 對應路徑
4. 特殊處理：headless 模式下自動啟用 OCR

**實作位置**：`src/nodriver_tixcraft.py` 行 89-138

### 2. 瀏覽器啟動

#### 2.1 Chrome 可用性檢查

`get_extension_config()` (行 20399) 在啟動前先確認 Chrome 是否可用：

```python
chrome_path = chrome_downloader.ensure_chrome_available(download_dir=webdriver_dir)
```

若系統未安裝 Chrome，嘗試自動下載；下載失敗則拋出 `FileNotFoundError`。

#### 2.2 ZenDriver 瀏覽器參數

`get_nodriver_browser_args()` (行 20345) 回傳經過 Cloudflare 驗證的啟動參數清單：

**核心參數**（約 30 項）：
- 效能優化：`--disable-animations`, `--disable-background-networking`, `--disable-smooth-scrolling`
- 隱私保護：`--disable-sync`, `--disable-translate`, `--no-pings`
- 穩定性：`--disable-breakpad`, `--disable-component-update`, `--disable-dev-shm-usage`
- 語系設定：`--lang=zh-TW`
- 反偵測：`--no-first-run`, `--no-default-browser-check`

**專家模式**（`CLOUDFLARE_ENABLE_EXPERT_MODE = False`，行 82）：
啟用時額外加入 `--no-sandbox` 與 `--disable-web-security`，可增強繞過能力但提高被偵測風險。

**實作位置**：`src/nodriver_tixcraft.py` 行 20345-20397

#### 2.3 Config 組裝與瀏覽器啟動

`get_extension_config()` (行 20399) 組裝 `zendriver.Config` 物件，支援三種模式：

| 模式 | 觸發條件 | 行為 |
|------|---------|------|
| MCP Connect | `--mcp_connect` | 連線既有 Chrome，不啟動新瀏覽器 |
| MCP Debug | `--mcp_debug` | 正常啟動，事後輸出實際 CDP port |
| 一般模式 | 預設 | 自動啟動 Chrome 並管理生命週期 |

`main()` (行 26021) 中的啟動流程：

1. `get_extension_config()` → 組裝 Config
2. `nodriver_overwrite_prefs(conf)` → 覆寫 Chrome Preferences（關閉密碼管理、通知、翻譯等）
3. `driver = await uc.start(conf)` → 啟動瀏覽器
4. `nodriver_goto_homepage()` → 導航至首頁並注入 Cookie
5. `nodrver_block_urls()` → 啟用網路封鎖
6. `nodriver_resize_window()` → 調整視窗大小

**實作位置**：`src/nodriver_tixcraft.py` 行 26021-26074

### 3. 網路封鎖清單

`nodrver_block_urls()` (行 20450) 透過 CDP `network.set_blocked_ur_ls()` 封鎖不必要的網路請求，分為三類：

**追蹤與分析腳本**（永遠封鎖）：
- Google Analytics / Tag Manager / Syndication
- Facebook Pixel（不影響 FB 登入）
- Clarity、Rollbar、Smartlook、Appier 等第三方追蹤
- Twitter / YouTube 嵌入

**平台廣告腳本**：
- Ticketmaster: `adblock.js`, `ads.js`
- 注意：Cityline 的 `others.min.js` **不可封鎖**（購買按鈕依賴此檔案）

**選擇性封鎖**（由設定控制）：
- `hide_some_image` 啟用時：封鎖字型檔案（woff/ttf）、活動圖片、favicon
- `block_facebook_network` 啟用時：封鎖所有 facebook.com 與 fbcdn.net 請求

**實作位置**：`src/nodriver_tixcraft.py` 行 20450-20543

### 4. 暫停機制

系統透過 `MAXBOT_INT28_IDLE.txt` (行 49) 檔案實現暫停：

- `check_and_handle_pause()` (行 7406)：檢查暫停檔案是否存在
- 檔案存在 → 主迴圈跳過所有平台邏輯，僅執行 KKTIX 暫停登入
- 檔案刪除 → 自動恢復執行

**進階暫停輔助函式** (行 7412-7445)：
- `sleep_with_pause_check()` — 延遲前檢查暫停
- `evaluate_with_pause_check()` — JS 執行前檢查暫停

### 5. 設定熱更新

`reload_config()` (行 20666) 在主迴圈中持續監控 `settings.json` 的修改時間，當檔案變更時自動重新載入以下欄位：

`ticket_number`, `date_auto_select`, `area_auto_select`, `keyword_exclude`, `ocr_captcha`, `tixcraft`, `kktix`, `cityline`, `refresh_datetime`, `contact`, `date_auto_fallback`, `area_auto_fallback`

### 6. 時間戳與 OCR 初始化

`main()` 中的其他初始化：

- **全域時間戳**：當 `show_timestamp` 啟用時，覆寫 `builtins.print` 為帶時間前綴的版本 (行 26024-26031)
- **OCR 初始化**：載入 `ddddocr` 模型，設定辨識範圍為小寫字母 (行 26093-26103)
- **定時開搶閘門**：`check_refresh_datetime_gate()` 在指定時刻前阻擋所有平台搶票邏輯，時間到達後立即重載頁面並放行

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `src/nodriver_tixcraft.py` | 主程式，包含所有初始化邏輯 |
| `src/settings.py` | 設定預設值與遷移邏輯 |
| `src/util.py` | 共用工具函式（`get_app_root` 等） |
| `src/chrome_downloader.py` | Chrome 自動下載 |
| `src/settings.json` | 使用者設定檔（不進版控） |

---

## 故障排除

### Chrome 找不到
**症狀**：`FileNotFoundError: Could not find or download Chrome browser`
**原因**：系統未安裝 Chrome 且自動下載失敗
**解法**：手動安裝 Chrome，或檢查 `src/webdriver/` 目錄權限

### ZenDriver 連線失敗
**症狀**：`Failed to connect to browser`
**原因**：前一個瀏覽器實例未正確關閉、port 衝突
**解法**：關閉殘留的 Chrome 程序後重試

### 網路封鎖導致功能異常
**症狀**：特定平台按鈕無法點擊或頁面不完整
**原因**：封鎖清單誤擋了平台必要的腳本
**解法**：檢查 `nodrver_block_urls()` 中的清單，確認未封鎖必要資源
