# 機制 11：排隊與付款 (Stage 11)

**文件說明**：說明搶票系統的排隊機制（Queue-IT、平台內建排隊）與付款頁面偵測策略
**最後更新**：2026-03-06

---

## 概述

訂單送出後，部分平台會進入排隊等待或付款流程。系統需要偵測排隊狀態、等待排隊結束，並確認進入結帳/付款頁面。

**核心目標**：正確偵測並等待排隊結束，不干擾付款頁面。

**優先度**：🔴 P1 - 核心流程

---

## 排隊機制分類

### 1. 第三方排隊 — Queue-IT（iBon）

iBon 使用第三方 Queue-IT 服務，URL 包含 `queue-it.net`。

**偵測與等待邏輯**（行 12825-12838）：

- 進入排隊：URL 包含 `queue-it.net` 時記錄 `queue_it_enter_time` 時間戳
- 等待排隊：直接 `return False` 讓主迴圈繼續輪詢，不執行任何頁面操作
- 離開排隊：URL 不再包含 `queue-it.net` 時，計算等待時間並重置時間戳

```
進入 queue-it.net → 記錄時間 → 每次輪詢 return False（不操作）→ URL 變化 → 排隊結束
```

### 2. 平台內建排隊 — TicketPlus

TicketPlus 使用 Vue.js 實作的頁面內排隊機制。

**排隊偵測** — `nodriver_ticketplus_check_queue_status()` (行 7473)：

透過 JS 評估偵測多種排隊指標：
- **關鍵字偵測**：「排隊購票中」、「請稍候」、「請勿離開」、「正在處理」等 9 個中文關鍵字
- **遮罩層偵測**：`.v-overlay__scrim` 元素 opacity 為 1 或 display 非 none
- **對話框偵測**：`.v-dialog` 內文包含「排隊」或「請稍候」

**排隊監控迴圈**（行 7700-7746）：

```
偵測到排隊 → 進入 while True 迴圈 → 每 5-10 秒隨機間隔檢查
→ URL 含 /confirm/ 或 /confirmseat/ → 跳出排隊
→ check_queue_status 回傳 False → 排隊結束
```

重要設計：
- 隨機等待 5-10 秒防止固定頻率被偵測（`random.uniform(5.0, 10.0)`）
- 僅在 URL 變化時輸出日誌，避免重複訊息
- 支援暫停機制（`check_and_handle_pause()`）

### 3. 外部排隊頁面 — HKTicketing

HKTicketing 使用多種排隊/重導頁面。

**排隊 URL 模式**（行 20742-20749）：

```python
HKTICKETING_REDIRECT_URL_LIST = [
    'queue.hkticketing.com/hotshow.html',
    '.com/detection.aspx?rt=',
    '/busy_galaxy.',
    '/hot0.ticketek.com.au/' ... '/hot19.ticketek.com.au/'  # 動態生成 20 個
]
```

**重導處理** — `nodriver_hkticketing_url_redirect()` (行 22972)：

偵測到排隊 URL 後，自動導回 `entry-hotshow.hkticketing.com/` 或對應的 galaxymacau / ticketek 首頁，並依 `auto_reload_page_interval` 設定等待後重試。

**錯誤頁面關鍵字**（行 20710-20738）：

系統偵測多種伺服器錯誤與排隊文字，包含：
- SQL Server 錯誤、HTTP 500/502/503/504
- `"Hi fans, you're in the queue to"`（英文排隊頁面）
- `"please stay on this page and do not refresh"`

### 4. 等待頁面 — FunOne

FunOne 使用自動重導的等待頁面（行 25170-25175）。

- 偵測 `page_type == "WAITING"` 時不執行任何操作
- 僅記錄一次日誌（`waiting_page_logged` 旗標）
- 等待平台自動重導到購票頁面

---

## 付款頁面偵測

系統**不自動進行付款操作**，而是偵測到付款/結帳頁面後：

1. 播放訂單音效通知使用者
2. 發送 Discord / Telegram 通知
3. Headless 模式下自動開啟瀏覽器視窗

各平台的付款頁面判斷方式：

| 平台 | 判斷條件 | 行號 |
|------|---------|------|
| TixCraft | URL 含 `/ticket/checkout` | 6137 |
| TicketPlus | URL 含 `/confirm/` 或 `/confirmseat/` | 7716 |
| HKTicketing Type02 | URL 含 `#/generateSeat` | 23257 |
| Cityline | URL 含 `/shoppingBasket` | 14294 |
| KHAM | 進入結帳頁面 | 17516 |
| iBon | checkout 頁面偵測 | 13717 |

---

## 設計原則

1. **不干擾排隊**：排隊期間不操作頁面，避免被踢出
2. **隨機間隔**：檢查頻率加入隨機性，降低自動化偵測風險
3. **僅通知不付款**：系統不自動填寫信用卡或完成付款，保障使用者安全
4. **一次性通知**：`played_sound_order` 旗標確保通知只觸發一次

---

## 相關文件

- 訂單送出：`docs/03-mechanisms/10-order-submit.md`
- 錯誤處理：`docs/03-mechanisms/12-error-handling.md`
- Cloudflare Turnstile：`docs/03-mechanisms/15-cloudflare-turnstile.md`
