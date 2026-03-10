# 機制 10：訂單送出 (Stage 10)

**文件說明**：說明搶票系統的訂單送出機制，包含各平台確認按鈕定位、條款勾選與送出成功偵測
**最後更新**：2026-03-06

---

## 概述

訂單送出是購票流程中的最後關鍵步驟。系統需要定位提交按鈕、勾選同意條款、點擊提交，並透過 URL 變化或頁面內容偵測送出是否成功。

**核心目標**：成功送出訂單，進入付款或確認階段。

**優先度**：🔴 P1 - 核心流程，直接決定購票成功

---

## 訂單送出的通用流程

```
勾選同意條款 → 定位提交按鈕 → 檢查按鈕可用性 → 點擊送出 → 偵測結果頁面
```

所有平台在送出前都會：
1. 以 JS 評估按鈕是否 `disabled` 且 `offsetParent !== null`（可見）
2. 點擊後透過 URL 變化或頁面關鍵字偵測是否成功
3. 成功時播放音效並發送 Discord / Telegram 通知（`send_discord_notification` / `send_telegram_notification`，行 159-185）

---

## 各平台的送出按鈕定位方式

### KKTIX — `nodriver_kktix_confirm_order_button()` (行 2971)

- 選擇器：`div.form-actions a.btn-primary`
- 透過 JS 檢查 `!button.disabled && button.offsetParent !== null`
- 點擊前需先完成 KKTIX 特有的 `#/booking` 座位確認流程（`nodriver_kktix_booking_main`，行 2920）

### TicketPlus — `nodriver_ticketplus_confirm()` (行 7551)

- 先勾選同意條款（`nodriver_ticketplus_ticket_agree`）
- 主選擇器：`button.v-btn.primary`，備選：`button[type="submit"]`
- 同樣以 IIFE 檢查按鈕可用性後點擊

### HKTicketing Type02 — `nodriver_hkticketing_type02_confirm_order()` (行 22644)

四步驟流程：
1. 選擇取票方式（QRcode / 二維碼）
2. 點擊同意 checkbox（SVG icon `#icon-weixuanzhong` → `#icon-xuanzhong`）
3. 點擊彈窗中的「同意」按鈕
4. 點擊送出按鈕（「分配座位」）

### FunOne — `nodriver_funone_order_submit()` (行 24841)

- 透過 JS 遍歷所有 `button` 和 `input[type="submit"]`
- 比對按鈕文字：「立即購買」、「確認」、「送出」、「提交」等
- 以 `window.getComputedStyle` 確認按鈕可見且未禁用

### FANSI GO — `nodriver_fansigo_click_checkout()` (行 25892)

- 透過 JS 遍歷按鈕，比對關鍵字陣列：`["checkout","submit","buy","next","取得訂單","結帳","購買","下一步"]`
- 使用 `util.parse_nodriver_result()` 解析回傳值

### Tour iBon — `nodriver_tour_ibon_checkout()` (行 12629)

- 先自動填寫姓名與電話（從 `config_dict["contact"]` 讀取）
- 勾選同意條款後送出表單

### Cityline — `nodriver_cityline_check_shopping_basket()` (行 14283)

- 偵測 URL 包含 `/shoppingBasket` 來判斷成功加入購物車
- 不直接點擊送出按鈕，而是偵測頁面狀態變化

---

## 送出後的成功偵測

各平台透過不同方式偵測訂單是否送出成功：

| 平台 | 成功偵測方式 | 關鍵程式碼位置 |
|------|-------------|---------------|
| TixCraft | URL 包含 `/ticket/checkout` | 行 6137-6160 |
| KKTIX | `#/booking` 頁面出現 | 行 2731 |
| TicketPlus | URL 包含 `/confirm/` 或 `/confirmseat/` | 行 7716-7717 |
| HKTicketing | URL 包含 `#/generateSeat` | 行 23257-23261 |
| Cityline | URL 包含 `/shoppingBasket` | 行 14294 |
| KHAM | 進入結帳頁面 | 行 17516-17518 |
| iBon | 頁面偵測（checkout alert） | 行 13717-13722 |

---

## 成功通知機制

訂單偵測成功後，系統執行以下動作（僅執行一次，以 `played_sound_order` 旗標控制）：

1. **播放音效**：若 `advanced.play_sound.order` 為 true，呼叫 `play_sound_while_ordering()`
2. **Discord 通知**：`send_discord_notification(config_dict, "order", platform_name)` (行 159)
3. **Telegram 通知**：`send_telegram_notification(config_dict, "order", platform_name)` (行 172)
4. **Headless 模式**：自動開啟瀏覽器顯示結帳頁面（TixCraft 行 6144-6148, KHAM 行 17529-17534）

---

## 訂單失敗處理

### TicketPlus 訂單失敗彈窗 — `nodriver_ticketplus_accept_order_fail()` (行 7393)

- 偵測 `div[role="dialog"]` 中的失敗訊息
- 自動點擊確認按鈕關閉彈窗，讓主流程繼續重試

---

## 相關文件

- 條款同意機制：`docs/03-mechanisms/09-terms-agreement.md`
- 排隊與付款：`docs/03-mechanisms/11-queue-payment.md`
- 錯誤處理：`docs/03-mechanisms/12-error-handling.md`
