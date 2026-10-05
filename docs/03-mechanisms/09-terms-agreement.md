# 機制 09：同意條款 (Stage 9)

**文件說明**：說明搶票系統的條款同意機制、自動勾選策略與各平台差異
**最後更新**：2026-06-10

---

## 概述

在送出訂單前，大多數平台都要求使用者同意服務條款。系統需要自動偵測並勾選這些條款 checkbox，以確保訂單可以成功送出。

**核心目標**：自動偵測並勾選所有必要的條款 checkbox，確保訂單提交不被阻擋。

**優先度**：🟡 P2 - 法律合規性重要

---

## 核心實作：Checkbox 勾選工具函式

系統提供三個層級的 checkbox 勾選函式，各平台依需求選用：

### `nodriver_check_checkbox()`（`src/nodriver_common.py`）

通用版本，透過 JavaScript 操作 checkbox：

1. **尋找目標 checkbox** — 使用 `document.querySelectorAll(select_query)` 取得所有比對元素
2. **過濾「記住密碼」checkbox** — 檢查 id/name/className/label 是否包含 `remember`、`記得`、`記住`、`密碼` 等關鍵字，避免誤操作
3. **檢查勾選狀態** — 若 `checkbox.checked` 為 true，直接回傳成功
4. **嘗試點擊** — 呼叫 `checkbox.click()`，若失敗則 fallback 直接設定 `checkbox.checked = true`

### `nodriver_check_checkbox_enhanced()`（`src/nodriver_common.py`）

增強版本，專為 TixCraft 設計，使用精確的 CSS 選擇器（如 `#TicketForm_agree`）定位單一 checkbox，配合 DebugLogger 輸出操作結果。

### `nodriver_force_check_checkbox()`（`src/nodriver_common.py`）

強制版本，接受已取得的 checkbox 元素物件，直接操作而非透過選擇器尋找。用於需要精確控制目標元素的情境。

---

## 各平台條款同意實作

| 平台 | 函式名稱 | 檔案 | 選擇器 / 方式 | 特殊邏輯 |
|------|----------|------|--------------|----------|
| TixCraft | `nodriver_tixcraft_ticket_main_agree` | `platforms/tixcraft.py` | `#TicketForm_agree` | 最多重試 3 次，使用 enhanced 版本 |
| KKTIX | 整合於 `nodriver_kktix_confirm_order_button` | `platforms/kktix.py` | 提交前隱含勾選 | 由確認按鈕流程處理 |
| iBon | `nodriver_ibon_ticket_agree` | `platforms/ibon.py` | `#agreen:not(:checked)` | 最多重試 3 次 |
| iBon (不相鄰座位) | `nodriver_ibon_allow_not_adjacent_seat` | `platforms/ibon.py` | `div.not-consecutive input[type="checkbox"]` | 允許不相鄰座位的額外 checkbox |
| TicketPlus | `nodriver_ticketplus_ticket_agree` | `platforms/ticketplus.py` | `input[type="checkbox"]` 全部 | 走訪所有 checkbox，支援 JS fallback |
| TicketPlus (實名制) | `nodriver_ticketplus_accept_realname_card` | `platforms/ticketplus.py` | `div.v-dialog button.primary` | 彈出視窗按鈕點擊 |
| FamiTicket | 整合於 `nodriver_fami_ticket_select` | `platforms/famiticket.py` | `.ts-note__check` | 勾選兩個注意事項 checkbox |
| FunOne | `nodriver_funone_ticket_agree` | `platforms/funone.py` | 自訂 `.checkbox_block` | 支援自訂 div checkbox 和標準 input checkbox |

---

## 平台關鍵差異

### TixCraft — 簡單精確勾選（`nodriver_tixcraft_ticket_main_agree`）

TixCraft 的條款 checkbox 使用固定 ID `#TicketForm_agree`，是最單純的實作：

- 使用 `nodriver_check_checkbox_enhanced()` 精確定位
- 最多重試 3 次，失敗時記錄警告
- 在 `nodriver_tixcraft_ticket_main()` 中，不論票數是否已設定都會呼叫此函式，確保 checkbox 一定被勾選

### TicketPlus — 全走訪 + JS Fallback（`nodriver_ticketplus_ticket_agree`）

TicketPlus 的條款 checkbox 沒有固定選擇器，系統走訪頁面上所有 `input[type="checkbox"]`：

- 逐一檢查 `el.checked` 狀態
- 未勾選時先嘗試 `checkbox.click()`（ZenDriver 原生點擊）
- 若點擊後仍未勾選，fallback 至 JavaScript：設定 `checkbox.checked = true` 並觸發 `change` 事件
- 額外處理實名制彈出視窗（`nodriver_ticketplus_accept_realname_card`）

### FunOne — 自訂 Checkbox 元件（`nodriver_funone_ticket_agree`）

FunOne 不使用標準 `<input type="checkbox">`，而是自訂 `<div class="checkbox">` 元件：

- 先搜尋 `.checkbox_block .checkbox` 或 `div.checkbox` 元素
- 勾選狀態由父元素的 `active` class 決定，而非 `checked` 屬性
- 若自訂 checkbox 找不到，fallback 至標準 `input[type="checkbox"]`
- 標準 checkbox 需檢查附近文字是否包含「同意」、「條款」、「agree」、「terms」等關鍵字，避免勾選無關 checkbox

### iBon — 不相鄰座位同意（`nodriver_ibon_allow_not_adjacent_seat`）

iBon 除了基本條款同意外，還有「允許不相鄰座位」的特殊 checkbox：

- 選擇器為 `div.not-consecutive > div.custom-control > span > input[type="checkbox"]:not(:checked)`
- 使用 `:not(:checked)` 偽類確保只操作未勾選的 checkbox
- 最多重試 3 次

### FamiTicket — 整合於票種選擇流程（`nodriver_fami_ticket_select`）

FamiTicket 的條款勾選不是獨立階段，而是整合在 `nodriver_fami_ticket_select()` 中：

- 票數選擇後、提交前，一次勾選所有 `.ts-note__check` checkbox
- 使用 JavaScript 走訪並呼叫 `cb.click()`

---

## 共通設計模式

### 重試機制

TixCraft 和 iBon 都採用最多 3 次的重試迴圈：

```
for i in range(3):
    is_finish = await nodriver_check_checkbox(...)
    if is_finish:
        break
```

這是因為 checkbox 可能在第一次點擊時因頁面動畫或 JavaScript 攔截而失敗。

### 「記住密碼」過濾

`nodriver_check_checkbox()` 內建過濾邏輯，避免誤勾選登入頁面的「記住密碼」checkbox。這對使用通用 `input[type="checkbox"]` 選擇器的平台特別重要。

### JS Fallback 策略

所有勾選函式都採用兩層策略：
1. 先嘗試 `checkbox.click()` — 模擬真實使用者行為
2. 失敗時直接設定 `checkbox.checked = true` — 繞過可能的點擊攔截

---

## 常見問題

### 問題 1：Checkbox 點擊後未勾選

**症狀**：`click()` 執行成功但 `checked` 狀態未改變

**原因**：某些前端框架（如 Vue/React）攔截了原生 click 事件，或 checkbox 由 JavaScript 控制

**解決方式**：使用 JS fallback 直接設定 `checked = true` 並觸發 `change` 事件（TicketPlus 實作）

### 問題 2：彈出視窗條款未處理

**症狀**：條款同意完成但頁面仍無法進入下一步

**原因**：平台顯示了額外的彈出視窗（如 TicketPlus 實名制卡片）

**解決方式**：TicketPlus 額外呼叫 `nodriver_ticketplus_accept_realname_card()` 和 `nodriver_ticketplus_accept_other_activity()` 處理彈出視窗

### 問題 3：過度勾選

**症狀**：誤勾選了「電子報訂閱」或「記住密碼」等非必要 checkbox

**解決方式**：使用精確的 CSS 選擇器（如 `#TicketForm_agree`）或內建的「記住密碼」過濾邏輯。FunOne 額外檢查附近文字是否包含條款相關關鍵字。

---

## 成功標準

**SC-006: 條款同意成功率** >= 98%
- 系統正確同意所有必填條款的次數 / 總嘗試次數

**SC-009: 錯誤恢復能力** >= 90%
- 條款同意過程中遭遇錯誤時的恢復成功率

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-040 | 自動同意條款 | ✅ 實作 |
| FR-041 | 條款驗證 | ✅ 實作 |

---

## 更新日期

- **2026-03**: 補充核心實作內容、各平台差異與共通設計模式
- **2025-11**: 初始文件建立
