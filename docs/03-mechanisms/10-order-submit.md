# 機制 10：訂單送出 (Stage 10)

**文件說明**：說明搶票系統的訂單送出機制，包含各平台確認按鈕定位、條款勾選、送出成功偵測與送出後防重入
**最後更新**：2026-09-21

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
3. 成功時播放音效並傳送 Discord / Telegram 通知（`send_discord_notification` / `send_telegram_notification`，`src/nodriver_common.py`）

---

## 各平台的送出按鈕定位方式

### KKTIX — `nodriver_kktix_confirm_order_button()`（`platforms/kktix.py`）

- 選擇器：`div.form-actions a.btn-primary`
- 透過 JS 檢查 `!button.disabled && button.offsetParent !== null`
- 點擊前需先完成 KKTIX 特有的 `#/booking` 座位確認流程（`nodriver_kktix_booking_main`）

### TicketPlus — `nodriver_ticketplus_confirm()`（`platforms/ticketplus.py`）

- 先勾選同意條款（`nodriver_ticketplus_ticket_agree`）
- 主選擇器：`button.v-btn.primary`，備選：`button[type="submit"]`
- 同樣以 IIFE 檢查按鈕可用性後點擊

### HKTicketing Type02 — `nodriver_hkticketing_type02_confirm_order()`（`platforms/hkticketing.py`）

四步驟流程：
1. 選擇取票方式（QRcode / QR 碼）
2. 點擊同意 checkbox（SVG icon `#icon-weixuanzhong` → `#icon-xuanzhong`）
3. 點擊彈出視窗中的「同意」按鈕
4. 點擊送出按鈕（「分配座位」）

### FunOne — `nodriver_funone_order_submit()`（`platforms/funone.py`）

- 透過 JS 走訪所有 `button` 和 `input[type="submit"]`
- 比對按鈕文字：「立即購買」、「確認」、「送出」、「提交」等
- 以 `window.getComputedStyle` 確認按鈕可見且未停用

### FANSI GO — `nodriver_fansigo_click_checkout()`（`platforms/fansigo.py`）

- 透過 JS 走訪按鈕，比對關鍵字陣列：`["checkout","submit","buy","next","取得訂單","結帳","購買","下一步"]`
- 使用 `util.parse_nodriver_result()` 解析回傳值

### Tour iBon — `nodriver_tour_ibon_checkout()`（`platforms/ibon.py`）

- 先自動填寫姓名與電話（從 `config_dict["contact"]` 讀取）
- 勾選同意條款後送出表單

### Cityline — `nodriver_cityline_check_shopping_basket()`（`platforms/cityline.py`）

- 偵測 URL 包含 `/shoppingBasket` 來判斷成功加入購物車
- 不直接點擊送出按鈕，而是偵測頁面狀態變化

---

## 送出後的成功偵測

各平台透過不同方式偵測訂單是否送出成功：

| 平台 | 成功偵測方式 | 關鍵程式碼位置 |
|------|-------------|---------------|
| TixCraft | URL 包含 `/ticket/checkout` | `platforms/tixcraft.py` |
| KKTIX | `#/booking` 頁面出現 | `platforms/kktix.py` |
| TicketPlus | URL 包含 `/confirm/` 或 `/confirmseat/` | `platforms/ticketplus.py` |
| HKTicketing | URL 包含 `#/generateSeat` | `platforms/hkticketing.py` |
| Cityline | URL 包含 `/shoppingBasket` | `platforms/cityline.py` |
| KHAM | 進入結帳頁面 | `platforms/kham.py` |
| iBon | 頁面偵測（checkout alert） | `platforms/ibon.py` |

---

## 送出後防重入（跨平台通用模式）

送出按鈕點下去之後，表單 POST 的導航還沒完成，瀏覽器仍停在舊 URL，但頁面的 JS 往往已經把
票種列、按鈕等元素清掉。此時主迴圈若再跑一圈，會在一個「已經送出、正在離開」的頁面上重新
判斷狀態——**結果一律是誤判**：看起來像售罄、像沒選到票、像表單沒填。

更危險的是誤判後的補救動作。若補救是 `tab.reload()`，重整一個 POST 結果頁會讓瀏覽器跳出
**原生對話框**（表單重新送出確認，或購票表單的 `beforeunload`）。原生對話框會**阻塞所有 JS
執行**，主迴圈從此讀不到頁面狀態，整個流程卡死——而訂單其實已經成功保留。

實際案例：FunOne 2026-09-21 實測，訂單已保留（頁面到 `purchase_fill_form`），但 bot 誤判
售罄 → 重整 → 原生對話框 → `js_dumps timed out`。

### 防護模式

兩層，缺一不可。

**第一層：送出冷卻（主要防護）**

在 `_state` 記錄「在哪一頁送出、何時送出」，下一圈進入該階段時先檢查。以 **URL 相符 + 時間
未過期** 雙重界定：

```python
# 模組層級常數
CONST_{PLATFORM}_SUBMIT_COOLDOWN = 5.0

# _state 初始化
"order_submitted_url": "",
"order_submitted_time": 0,

# 送出成功時記錄（在呼叫端，因為送出函式本身不知道當下 URL）
submitted = await nodriver_{platform}_order_submit(tab, config_dict)
if submitted:
    _state["order_submitted_url"] = url
    _state["order_submitted_time"] = time.time()

# 進入該階段前檢查
if (_state.get("order_submitted_url") == url
        and time.time() - _state.get("order_submitted_time", 0)
        < CONST_{PLATFORM}_SUBMIT_COOLDOWN):
    await tab.sleep(0.3)
    return tab
```

**務必用會過期的冷卻，不要用布林旗標。** 布林旗標一旦設上就沒有回頭路——送出失敗、頁面被
打回、使用者手動操作，任何一種情況都會讓 bot 永久停擺。URL 相符保證頁面真的導航走之後防護
自動失效；時間上限保證最壞情況下也必然解除。

**第二層：reload 前確認頁面（防守縱深）**

即使冷卻過期或漏設，也不該重整一個已經離開的頁面：

```python
live_url = await nodriver_current_url_safe(tab)
if _is_past_ticket_selection(live_url):
    debug.log("[{PLATFORM}] Page already moved on, skipping reload")
else:
    await tab.reload()
```

`nodriver_current_url_safe(tab)`（`src/nodriver_common.py`）在導航途中會回空字串而不是拋錯，
正適合這個判斷。FunOne 另有既有先例可參考：`nodriver_funone_auto_reload` 在 reload 前檢查
URL 是否為 `purchase_waiting_jump` / `purchase_fill_form`，是就直接 return。

**述詞用 blocklist，不要用 allowlist。** 列出「已經送出、不可碰」的頁面，而不是列出「可以重整」
的頁面。原因：有些階段的頁面是靠 DOM 特徵判定的，URL 形式未知；allowlist 會把那些階段的
正常送出一併擋掉。未知 URL 放行等於維持現狀行為，風險較低。

### 把守衛寫成純述詞，讓它可被測試

把判斷抽成 module-level 純函式（無 I/O、無 `tab`），主流程只負責餵值：

```python
def _is_submit_cooldown(url, submitted_url, submitted_time, now):
    if not submitted_url or submitted_url != url:
        return False
    return (now - submitted_time) < CONST_{PLATFORM}_SUBMIT_COOLDOWN
```

這樣就能寫 Layer 3 測試（`tests/platform_logic/`），不需要瀏覽器。既有先例：
`tixcraft._should_leave_dialog_to_user` 由 `tests/platform_logic/test_tixcraft_dialog_guard.py`
測試；FunOne 的兩個述詞由 `test_funone_submit_guard.py` 測試。

**「平台邏輯無法單元測試」只適用於綁定即時瀏覽器狀態的完整流程**，純決策邏輯抽出來就能測。

### 戳記寫在送出函式內部，不要寫在呼叫端

若平台有多個送出入口（例如 step 1 與 step 2 各一），把記錄寫進送出函式本身，兩條路徑自動
同時覆蓋，少一處遺漏風險。函式內以 `nodriver_current_url_safe` 重讀即時 URL，不要信任呼叫端
傳進來的——呼叫端拿到的可能正是那個過時的 URL。

### 冷卻時間怎麼抓

取決於該平台送出 POST 的實際往返時間，從 log 量：送出的時間戳到 URL 真正變更的時間戳。

| 平台 | 常數 | 值 |
|------|------|-----|
| KKTIX | `CONST_KKTIX_NEXT_BUTTON_COOLDOWN` | 1.5 秒 |
| FunOne | `CONST_FUNONE_SUBMIT_COOLDOWN` | 5.0 秒 |

寧可長一點。冷卻期間 bot 只是多等幾百毫秒，代價遠小於卡死整輪。

### 是否需要顯式清除

多數情況不用——URL 失配與時間上限已經構成雙重出口。

例外是「送出失敗需要立刻重試」的場景。KKTIX 在失敗彈窗（`alert_needs_reload`、
`dismiss_failure_modal`）路徑會把兩個鍵清零，讓下一圈立即動作而不必等冷卻結束
（`platforms/kktix.py`）。若平台的重試本來就有 `auto_reload_page_interval` 節奏，就不需要。

### 已套用的平台

| 平台 | 狀態 | 備註 |
|------|------|------|
| KKTIX | ✅ | `next_button_pressed_url` / `next_button_pressed_time` |
| FunOne | ✅ | `order_submitted_url` / `order_submitted_time`，含第二層 reload 檢查 |
| 其他 | 未套用 | 新增平台或遇到同類症狀時比照辦理 |

**判斷是否需要**：該平台的送出之後，主迴圈會不會在同一個 URL 上重跑同一階段？若會，且該階段
失敗時有 `tab.reload()` 或重新送出的動作，就需要這個防護。

---

## 成功通知機制

訂單偵測成功後，系統執行以下動作（僅執行一次，以 `played_sound_order` 旗標控制）：

1. **播放音效**：若 `advanced.play_sound.order` 為 true，呼叫 `play_sound_while_ordering()`
2. **Discord 通知**：`send_discord_notification(config_dict, "order", platform_name)`
3. **Telegram 通知**：`send_telegram_notification(config_dict, "order", platform_name)`
4. **Headless 模式**：自動開啟瀏覽器顯示結帳頁面（TixCraft、KHAM）

---

## 訂單失敗處理

### TicketPlus 訂單失敗彈出視窗 — `nodriver_ticketplus_accept_order_fail()`（`platforms/ticketplus.py`）

- 偵測 `div[role="dialog"]` 中的失敗訊息
- 自動點擊確認按鈕關閉彈出視窗，讓主流程繼續重試

---

## 相關文件

- 條款同意機制：`docs/03-mechanisms/09-terms-agreement.md`
- 排隊與付款：`docs/03-mechanisms/11-queue-payment.md`
- 錯誤處理：`docs/03-mechanisms/12-error-handling.md`
