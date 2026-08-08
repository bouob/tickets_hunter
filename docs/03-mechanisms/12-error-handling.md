# 機制 12：錯誤處理 (Stage 12)

**文件說明**：說明搶票系統的錯誤分類、重試策略與各平台特殊錯誤處理機制
**最後更新**：2026-06-10

---

## 概述

錯誤處理貫穿整個購票流程。系統需要識別錯誤類型，決定重試或放棄，並在適當時機通知使用者。主要透過 `try/except` 包覆關鍵操作，搭配 CDP 事件處理器攔截 JavaScript alert。

**核心目標**：在不中斷主流程的前提下，最大化錯誤恢復能力。

**優先度**：🔴 P1 - 系統穩定性基礎

---

## 錯誤分類

### 1. 售完 / 庫存錯誤

最常見的業務邏輯錯誤，各平台偵測方式不同。

**TixCraft 售完偵測**（`src/platforms/tixcraft.py`，alert 處理器）：

透過 CDP `JavascriptDialogOpening` 事件處理器攔截 alert：
- 售完關鍵字：`['售完', '已售完', '選購一空', 'sold out', 'no tickets']`
- 偵測到售完後設定冷卻時間戳 `sold_out_cooldown_until`（Issue #188）
- 冷卻期間依 `auto_reload_page_interval` 設定等待後重試

**TixCraft 日期頁面售完過濾**（`nodriver_tixcraft_date_auto_select`）：

售完文字清單：`["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]`
當 `pass_date_is_sold_out` 啟用時，自動跳過售完場次的列。

**iBon 售完偵測** — `nodriver_ibon_check_sold_out()`（`src/platforms/ibon.py`）：

透過 JS 檢查 `#ticket-info` 元素是否包含「已售完」文字。

**iBon 票頁面售完偵測** — `nodriver_ibon_check_sold_out_on_ticket_page()`：

更精細的偵測，在票數選擇頁面確認是否所有票種都已售完。搭配 `nodriver_ibon_wait_for_select_elements()` 等待頁面載入，避免誤判。

**KKTIX 售完偵測**（`src/platforms/kktix.py`）：

關鍵字清單：`['暫無票', '已售完', 'Sold Out', 'sold out', '完売']`

### 2. Alert 對話框處理

系統透過 CDP 事件處理器自動攔截 JavaScript alert。

**TixCraft 全域 alert 處理器**（`nodriver_tixcraft_main` 內註冊）：

- 以 `cdp.page.JavascriptDialogOpening` 事件註冊
- 分類處理：驗證碼錯誤（標記 `captcha_alert_detected`）、售完（設定冷卻）
- 關閉 alert 使用重試機制（最多 3 次，每次間隔 0.1 秒）
- 處理 CDP -32602 錯誤（dialog 已被其他處理器關閉）

**iBon 全域 alert 處理器**（`nodriver_ibon_main` 內註冊）：

- 跳過暫停狀態（讓使用者手動處理）
- 跳過結帳頁面（重要 alert 不自動關閉）
- 同樣使用 3 次重試機制關閉 alert

### 3. 頁面載入與網路錯誤

**HKTicketing 錯誤頁面偵測**（`src/platforms/hkticketing.py`）：

偵測 SQL Server 錯誤、HTTP 5xx、Gateway Timeout 等伺服器錯誤：
```
"HTTP Error 500", "HTTP Error 503", "504 Gateway Time-out", "502 Bad Gateway",
"Server Error in '/' Application", "System.Data.SqlClient.Sql"
```
偵測到後透過 `nodriver_hkticketing_url_redirect()` 重導回入口頁面。

**HKTicketing 403 處理**：

在入口頁面偵測到 `Access denied (403)` 或 `Current session has been terminated` 時，自動刷新頁面。

### 4. Cloudflare 挑戰

獨立的重試機制 — `handle_cloudflare_challenge()`（`src/nodriver_common.py`）：
- 最大重試次數：`CLOUDFLARE_MAX_RETRY = 3`（定義於 `src/nodriver_common.py`）
- 遞增等待：基礎等待時間 + `retry_count * 2` 秒
- 詳見 `docs/03-mechanisms/15-cloudflare-turnstile.md`

### 5. WebSocket 靜默斷線（silent-but-count）

`nodriver_current_url()`（`src/nodriver_common.py`）把 CDP 例外分成三類，
由純函式 `classify_url_error()` 判定：

| 類別 | 常數 | 行為 |
|------|------|------|
| 結束程式 | `CONST_URL_EXIT_ERROR_STRINGS` | 設 `is_quit_bot`，主迴圈收掉瀏覽器 |
| 靜默 | `CONST_URL_SILENT_ERROR_STRINGS` | 不印例外，但**計數** |
| 其他 | — | 照常印出並記錄 `[URL DIAG]` |

`no close frame received or sent` 屬靜默類。它在頁面導航或分頁關閉時本來就會出現一兩次，
所以不能每次都印。但它同時也是**連線已死**的樣子：URL 永遠取回空字串，
主迴圈 `len(url) == 0` 就 `continue`，於是 bot 既不工作也不退出，無限空轉。

計數機制讓這個狀態可見而不吵：

- 連續第 `CONST_URL_SILENT_ERROR_REPORT_THRESHOLD`（15）次時 `print()` 一次 `[URL ERROR]`
- 之後每 `CONST_URL_SILENT_ERROR_REPORT_INTERVAL`（50）次重報一次
- 一旦成功取得非空 URL 即歸零，並記錄 `[URL DIAG] websocket recovered after N silent errors`
- 主迴圈的 `[URL DIAG] empty url` 節流訊息會附上 `silent_ws_errors=N`，兩條訊息可交叉對照

閾值取 15 的依據：主迴圈約每 50ms 輪詢一次，15 次代表已經接近一秒完全讀不到 URL，
遠超過任何正常導航的瞬時抖動。

**刻意不做的兩件事**：不自動重連（重建 tab/browser 連線動到共用基礎設施，且難以測試，
可能引入比原問題更難查的不穩定），也不加進結束清單（搶票中途自行退出的代價太高）。
使用者看到訊息後自行決定何時重啟。

**預期中的副作用**：使用者手動關閉分頁後，計數會持續累積並每 50 次重報一次。
這是設計如此——目的就是提示該重啟了——不是新的缺陷。

---

## 重試策略

### 固定次數重試

大部分平台操作使用固定次數重試：

| 場景 | 最大次數 | 間隔 | 程式碼位置 |
|------|---------|------|-----------|
| Cloudflare 挑戰 | 3 次 | 遞增（3 + retry * 2 秒） | `nodriver_common.py`（handle_cloudflare_challenge） |
| KKTIX 按鈕點擊 | 3 次 | 固定重試 | `platforms/kktix.py` |
| Alert 關閉 | 3 次 | 0.1 秒 | `platforms/tixcraft.py`（alert 處理器） |
| 驗證碼填寫 | max_retries | 逐次重試 | `platforms/kktix.py` |

### 冷卻時間戳重試（TixCraft）

TixCraft 售完偵測使用非阻塞式冷卻機制：
- 不在 alert 處理器中 sleep（event handler 不阻塞主迴圈）
- 改為設定 `sold_out_cooldown_until` 時間戳
- 主迴圈在冷卻期間跳過操作

### 區域重試計數器（TixCraft）

`area_retry_count`（`platforms/tixcraft.py` 的 `_state`）：
- 選票區域每次嘗試失敗 +1
- 達到 60*15（15 分鐘）次後重置
- 短期內連續失敗 10 次後也重置，防止無限循環

### 自動刷新頁面

當選票失敗時，依 `auto_reload_page_interval` 設定自動刷新：
- `interval = 0`：立即刷新
- `interval > 0`：等待 N 秒後刷新
- 透過 `tab.reload()` 重新載入頁面

---

## 狀態字典初始化

每個平台在主迴圈開始時初始化狀態字典，用於追蹤錯誤與重試狀態。關鍵欄位：

- `fail_list`：已嘗試失敗的區域/項目清單（TixCraft、iBon）
- `area_retry_count`：區域重試計數（TixCraft）
- `captcha_alert_detected`：驗證碼錯誤旗標（TixCraft）
- `sold_out_cooldown_until`：售完冷卻時間戳（TixCraft）
- `queue_it_enter_time`：Queue-IT 進入時間（iBon）
- `alert_handler_registered`：Alert 處理器註冊旗標（iBon）

各平台的狀態字典為模組層級 `_state` dict（位於各自的 `src/platforms/*.py`）。

---

## 通用錯誤處理模式

整個程式碼庫中錯誤處理遵循一致的模式：

1. **try/except 包覆所有 DOM 操作**：每個 `tab.evaluate()`、`tab.query_selector()` 都有 except
2. **靜默失敗不中斷流程**：大部分 except 回傳 False 或 None，讓主迴圈繼續
3. **關鍵操作才記錄日誌**：使用 `debug.log()` 而非 `print()`，由 verbose 設定控制
4. **一次性日誌**：使用旗標（如 `submit_notfound`、`waiting_page_logged`）避免重複輸出

---

## 暫停機制

`check_and_handle_pause()`（`src/nodriver_common.py`）檢查暫停檔是否存在：
- 暫停檔路徑由 `util.get_instance_state_path()` 解析，**per-instance 隔離**：default 實例用根目錄 `MAXBOT_INT28_IDLE.txt`，具名實例用 `instances/<id>/MAXBOT_INT28_IDLE.txt`，暫停一個實例不會影響其他實例
- 檔案存在 → 暫停所有自動化操作
- 搭配 `sleep_with_pause_check()`、`asyncio_sleep_with_pause_check()` 等包裝函式（同檔）
- 在排隊監控迴圈中也支援暫停
- 詳見 [17-multi-instance.md](./17-multi-instance.md)

---

## 相關文件

- 訂單送出：`docs/03-mechanisms/10-order-submit.md`
- 排隊與付款：`docs/03-mechanisms/11-queue-payment.md`
- Cloudflare Turnstile：`docs/03-mechanisms/15-cloudflare-turnstile.md`
- DebugLogger 規格：`docs/04-implementation/debug-logger-spec.md`
