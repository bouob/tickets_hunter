# 機制 06：票數設定 (Stage 6)

**文件說明**：說明搶票系統的票數設定機制、數量選擇方式與配置驅動策略
**最後更新**：2026-03-06

---

## 概述

票數設定是確定使用者希望購買的票券數量。系統需要在購票表單中輸入或選擇購票數量，通常在選擇日期和座位區域之後進行。

**核心目標**：正確設定購票數量，符合使用者配置和平台限制。

**優先度**：🟡 P2 - 重要流程

**設定鍵**：`ticket_number`（預設值 `2`，定義於 `settings.py` 行 106）

---

## 核心實作：`nodriver_ticket_number_select_fill()`

所有基於 `<select>` 下拉選單的平台共用此函式（行 5113-5187）。流程如下：

1. **定位 select 元素** — 優先使用 `select_id`（由 `getElementById` 精確定位），否則回退到 `.mobile-select` 或 `select[id*="TicketForm_ticketPrice_"]`
2. **設定 value** — 透過 JavaScript 在 `<option>` 中尋找 `value === ticket_number` 且非 disabled、非售完的選項
3. **觸發 change 事件** — `select.dispatchEvent(new Event('change', {bubbles: true}))` 確保前端框架更新
4. **Fallback 機制** — 若目標票數不可用，自動選擇最大可用數量（而非硬編碼為 1）

售完判定關鍵字：`["選購一空", "已售完", "Sold out", "No tickets available", "空席なし", "完売した"]`

---

## 各平台實作方式

| 平台 | 函式名稱 | 行號 | 票數設定方式 | 特殊邏輯 |
|------|----------|------|-------------|----------|
| TixCraft | `nodriver_tixcraft_assign_ticket_number` | 5189 | `<select>` 下拉選單 | 支援票種關鍵字篩選，先選票種再設數量 |
| TixCraft (填入) | `nodriver_ticket_number_select_fill` | 5113 | 共用 `<select>` 設定 | Fallback 至最大可用數量 |
| KKTIX | `nodriver_kktix_assign_ticket_number` | 1268 | `<input>` 文字框 | JS 直接設定 `input.value`，觸發 Angular `$apply()` |
| iBon | `nodriver_ibon_ticket_number_auto_select` | 10791 | `<select>` 下拉選單 | CDP 等待 select 載入，支援新舊兩種表格格式 |
| Ticketmaster | `nodriver_ticketmaster_assign_ticket_number` | 3987 | `<select>` 下拉選單 | 設定後自動點擊 `#autoMode` 按鈕 |
| FamiTicket | `nodriver_fami_ticket_select` | 8789 | `<select>` 下拉選單 | 票數設定整合於票種選擇流程中 |
| TicketPlus | `nodriver_ticketplus_unified_select` | 6749 | 平台自訂 UI | 透過統一選擇函式處理 |
| FunOne | `nodriver_funone_assign_ticket_number` | 24210 | `<input>` + `+` 按鈕 | 遍歷輸入框找匹配票種，用 JS 操作 |
| FanSiGo | `nodriver_fansigo_assign_ticket_number` | 25839 | `+` 按鈕點擊 | React 18 批次更新問題，每次點擊間隔 0.2 秒 |

---

## 平台關鍵差異

### TixCraft — 票種關鍵字匹配（行 5189-5441）

TixCraft 的票頁可能有多個 `<select>`（對應不同票種/價位）。系統先根據 `area_keyword` 篩選目標票種，再對該 select 設定票數：

- 透過父元素 `<tr>` 中的 `<h4>` 或 `<td class="fcBlue">` 提取票種名稱
- 支援排除關鍵字（`keyword_exclude`）
- 單一票種時自動選擇
- 所有票種售完時回傳失敗，觸發頁面重新載入（行 5508-5518）

### KKTIX — Angular 雙向綁定（行 1268-1407）

KKTIX 使用 `<input>` 文字框而非 `<select>`。設定流程：

- 查找 `div.display-table-row input` 或 `div.ticket-item input.number-step-input-core`
- 清空後寫入 `ticket_number`
- 必須觸發 `input`、`change`、`blur` 三個事件
- 若偵測到 Angular，額外呼叫 `scope.$apply()` 確保模型同步

### FanSiGo — React 狀態批次更新（行 25839-25890）

React 18 會將同步的多次 `setState` 合併為一次更新。因此不能在單一 JS 執行中點擊 N 次 `+` 按鈕，必須：

- 每次 `tab.evaluate()` 只點擊一次 `+` 按鈕
- 每次點擊之間等待 0.2 秒讓 React 完成狀態更新
- 迴圈 `target_count` 次完成票數設定

---

## 常見問題

### 問題 1：Select 元素尚未載入

**症狀**：找不到票數選擇器，函式提前返回

**原因**：頁面 JavaScript 尚未初始化完成（特別是 Angular/Vue SPA）

**解決方式**：
- TixCraft 使用 `tab.wait_for()` 智慧等待選擇器出現（行 5202-5205）
- iBon 使用 `setInterval` 輪詢最多 15 次（每 100ms，行 10817-10840）

### 問題 2：目標票數選項不存在

**症狀**：使用者設定 `ticket_number: 4` 但 select 中最多只到 2

**解決方式**：`nodriver_ticket_number_select_fill` 自動 Fallback 至最大可用選項（行 5157-5173）

### 問題 3：已設定的票數被重複設定

**症狀**：每次迴圈都重新設定票數，造成頁面閃動

**解決方式**：TixCraft 使用狀態標記 `tixcraft_dict[ticket_state_key]` 記錄已設定狀態（行 5467-5473），KKTIX 檢查 `input.value !== "0"` 後跳過（行 1344-1364）

---

## 成功標準

**SC-003: 票數選擇成功率** >= 95%
- 系統正確設定票數的次數 / 總嘗試次數

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-028 | 票數設定 | ✅ 實作 |
| FR-029 | 數量限制驗證 | ✅ 實作 |

---

## 更新日期

- **2026-03**: 補充核心實作內容、各平台差異表格與常見問題
- **2025-11**: 初始文件建立
