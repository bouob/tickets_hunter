# 機制 03：頁面監控 (Stage 3)

**文件說明**：說明搶票系統的主迴圈結構、URL 路由分派與各平台頁面監控機制
**最後更新**：2026-03-06

---

## 概述

頁面監控是主迴圈的核心，系統以 50ms 間隔持續輪詢當前 URL，根據 URL 中的平台網域與路徑特徵，分派至對應平台的 `_main` 函式處理。每個平台的 `_main` 函式再依 URL 路徑將請求路由至對應的 12 階段處理器。

**核心目標**：即時偵測頁面變化並分派至正確的階段處理器。

**優先度**：🔴 P1 - 核心流程，時間敏感

---

## 主迴圈結構

### 迴圈入口

`main()` (行 26116) 中的 `while True` 迴圈是整個系統的心跳：

```
while True:
    await asyncio.sleep(0.05)               # 50ms 輪詢間隔
    config_dict = await reload_config()     # 熱更新設定
    url = await nodriver_current_url()      # 取得當前 URL
    check_and_handle_pause()               # 暫停檢查
    check_refresh_datetime_gate()          # 定時開搶閘門
    detect_cloudflare_challenge()          # Cloudflare 偵測
    -> URL 路由分派至各平台 _main()
```

**實作位置**：`src/nodriver_tixcraft.py` 行 26116-26288

### URL 取得機制

`nodriver_current_url()` (行 20556) 透過 `tab.js_dumps('window.location.href')` 取得當前頁面 URL。若瀏覽器連線中斷（WebSocket 500、WinError 1225 等），設定 `is_quit_bot = True` 終止程式。

### 迴圈前置處理

每次迴圈在進入平台路由前，依序執行：

1. **設定熱更新** (行 26119)：`reload_config()` 監控 `settings.json` 修改時間
2. **URL 變化偵測** (行 26154-26160)：URL 改變時印出新 URL、寫入 `MAXBOT_LAST_URL.txt`、重置 Cloudflare 狀態
3. **暫停處理** (行 26162-26167)：暫停中僅處理 KKTIX 登入，其餘跳過
4. **Cloudflare 偵測** (行 26169-26185)：URL 變化時檢測 Cloudflare 挑戰頁面，最多重試 3 次

---

## URL 路由分派

主迴圈根據 URL 中的網域關鍵字，將請求分派至對應平台的 `_main` 函式：

| URL 特徵 | 分派目標 | 行號 |
|----------|---------|------|
| `kktix.c` | `nodriver_kktix_main()` | 26188 |
| `tixcraft.com` / `indievox.com` / `ticketmaster.` | `nodriver_tixcraft_main()` | 26208 |
| `famiticket.com` | `nodriver_famiticket_main()` | 26220 |
| `ibon.com` | `nodriver_ibon_main()` | 26223 |
| `kham.com.tw` / `ticket.com.tw` / `tickets.udnfunlife.com` | `nodriver_kham_main()` | 26236 |
| `ticketplus.com` | `nodriver_ticketplus_main()` | 26240 |
| `urbtix.hk` | (保留，未實作) | 26259 |
| `cityline.com` | `nodriver_cityline_main()` | 26263 |
| `hkticketing.com` / `galaxymacau.com` / `ticketek.com` | `nodriver_hkticketing_main()` | 26273 |
| `tickets.funone.io` | `nodriver_funone_main()` | 26277 |
| `go.fansi.me` | `nodriver_fansigo_main()` | 26281 |
| `facebook.com/login.php` | `nodriver_facebook_main()` | 26286 |

**平台家族**：部分平台共用相同的後端邏輯：
- **TixCraft 家族**：tixcraft.com、indievox.com、ticketmaster.sg/com 共用 `nodriver_tixcraft_main()`
- **KHAM 家族**：kham.com.tw、ticket.com.tw、tickets.udnfunlife.com 共用 `nodriver_kham_main()`
- **Softix 家族**：hkticketing.com、galaxymacau.com、ticketek.com 共用 `nodriver_hkticketing_main()`

---

## 平台內 URL 路由（以 TixCraft 為例）

`nodriver_tixcraft_main()` (行 5878) 展示了典型的平台內 URL 路由結構：

| URL 路徑特徵 | 對應階段 | 處理函式 |
|-------------|---------|---------|
| `/activity/detail/` | Stage 3 → 4 | `nodriver_tixcraft_redirect()` — 重導至日期頁 |
| `/activity/game/` | Stage 4 日期選擇 | `nodriver_tixcraft_date_auto_select()` |
| `/artist/` (ticketmaster) | Stage 4 日期選擇 | `nodriver_ticketmaster_date_auto_select()` |
| `/ticket/area/` | Stage 5 區域選擇 | `nodriver_tixcraft_area_auto_select()` |
| `/ticket/verify/` | Stage 7 驗證碼 | `nodriver_tixcraft_verify()` |
| `/ticket/check-captcha/` | Stage 7 驗證碼 (TM) | `nodriver_ticketmaster_captcha()` |
| `/ticket/ticket/` | Stage 6 票數設定 | `nodriver_tixcraft_ticket_main()` |
| `/ticket/checkout` | Stage 10 訂單送出 | checkout 處理 |

**實作位置**：`src/nodriver_tixcraft.py` 行 5878-6123

### KKTIX 路由

`nodriver_kktix_main()` (行 2657) 的路由：

| URL 路徑特徵 | 對應階段 | 說明 |
|-------------|---------|------|
| `/users/sign_in?` | Stage 2 | 自動登入 |
| `#/booking` | Stage 5 | 座位選擇頁 |
| `/registrations/new` | Stage 5-9 | 購票主頁面（選票、同意條款、送出） |

---

## 狀態管理

### 平台狀態字典

每個平台維護一個全域字典追蹤狀態，以 `tixcraft_dict` 為例 (行 5955-5973)：

| 欄位 | 用途 |
|------|------|
| `fail_list` | 已嘗試失敗的選項（避免重複選取） |
| `start_time` / `done_time` | 計時用 |
| `area_retry_count` | 區域選擇重試次數（超過 900 次冷卻） |
| `alert_handler_registered` | 避免重複註冊 alert handler |
| `sold_out_cooldown_until` | 售完冷卻時間戳 |
| `captcha_alert_detected` | 驗證碼錯誤標記 |

### 全域 Alert Handler

各平台在 `_main` 首次呼叫時註冊 CDP `JavascriptDialogOpening` handler (如行 5977-5983)，自動處理彈窗：

- **售完提示**：自動關閉並進入冷卻延遲
- **驗證碼錯誤**：標記 `captcha_alert_detected` 供重試邏輯使用
- **危險確認框**（KKTIX）：偵測「取消」「不保留」等關鍵字時拒絕而非接受
- **暫停中**：不自動處理，讓使用者手動操作

---

## 定時重新整理

`check_refresh_datetime_gate()` 在 `refresh_datetime` 設定的目標時間到達前，阻擋所有平台搶票邏輯（持續倒數顯示）；時間到達後立即重新載入頁面並放行平台路由。最後 2 秒切換為 `time.perf_counter()` busy-wait，達到毫秒級精準觸發。格式：`YYYY/MM/DD HH:MM:SS`，空值表示停用。

---

## 購票完成處理

當平台 `_main` 函式回傳 `True`（購票完成），主迴圈：

1. 印出完成訊息（如 `"TixCraft ticket purchase completed"`）
2. 設定 `is_quit_bot = False` — 不結束程式，讓多開實例可獨立運作
3. 不自動建立暫停檔案

**實作位置**：行 26189-26257（各平台的完成處理）

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `src/nodriver_tixcraft.py` | 主迴圈與所有平台 `_main` 函式 |
| `src/util.py` | `create_debug_logger()`、`is_text_match_keyword()` 等共用函式 |

**各平台 `_main` 函式位置**：

| 函式 | 行號 |
|------|------|
| `nodriver_kktix_main()` | 2657 |
| `nodriver_tixcraft_main()` | 5878 |
| `nodriver_ticketplus_main()` | 7948 |
| `nodriver_famiticket_main()` | 9002 |
| `nodriver_ibon_main()` | 12763 |
| `nodriver_cityline_main()` | 14537 |
| `nodriver_kham_main()` | 16011 |
| `nodriver_hkticketing_main()` | 23131 |
| `nodriver_funone_main()` | 25057 |
| `nodriver_fansigo_main()` | 25939 |

---

## 故障排除

### 無法偵測 URL 變化
**症狀**：主迴圈卡在同一個 URL
**原因**：`js_dumps` 在 alert 開啟時會被阻塞
**解法**：確認 alert handler 已正確註冊；檢查 `nodriver_current_url()` 的錯誤訊息

### Cloudflare 無限重試
**症狀**：反覆出現 `[CLOUDFLARE] Challenge page detected`
**原因**：超過 3 次失敗後已停止重試，等待 URL 變化才會重置
**解法**：手動在瀏覽器中完成 Cloudflare 驗證，或檢查反偵測參數

### 購票完成後程式未停止
**症狀**：購票成功後程式繼續運行
**原因**：設計如此 — 為了支援多開實例獨立運作，不自動暫停
**解法**：這是預期行為；如需停止，手動建立 `MAXBOT_INT28_IDLE.txt`
