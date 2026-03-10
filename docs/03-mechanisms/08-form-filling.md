# 機制 08：表單填寫 (Stage 8)

**文件說明**：說明搶票系統的表單填寫機制、驗證問題答案填入與驗證碼表單處理流程
**最後更新**：2026-03-06

---

## 概述

表單填寫是購票過程中的關鍵階段。在本系統中，Stage 8 主要處理兩類表單：
1. **驗證問題表單** — 主辦方設定的文字問答（最常見）
2. **驗證碼輸入表單** — OCR 辨識結果的填寫與提交

**核心目標**：自動偵測表單類型、填入正確答案並提交，為訂單送出做準備。

**關鍵技術**：
- **答案推論**：從 `auto_guess_options` 自動猜測或從使用者預設答案填入
- **驗證碼 OCR**：辨識圖形驗證碼後自動填入（與 Stage 7 CAPTCHA 緊密關聯）
- **失敗重試**：維護 `fail_list` 追蹤錯誤答案，避免重複提交

**優先度**：🔴 P1 - 核心流程，直接影響購票成功

---

## 核心流程：驗證問題填寫

### 通用填寫函式 `nodriver_fill_verify_form()`（行 4400）

此函式為 TixCraft 系平台的通用驗證表單處理器，流程如下：

1. **偵測輸入框** — 用 `document.querySelector(input_text_css)` 檢查輸入欄位是否存在
2. **比對現有值** — 若輸入框已有值且與目標答案相同，跳過填寫
3. **清空後填入** — 先 `input.value = ""`，再寫入答案，觸發 `input` 和 `change` 事件
4. **提交表單** — 根據 `submit_by_enter` 參數，以 Enter 鍵或點擊提交按鈕送出

### 答案來源優先順序

系統依以下順序嘗試取得答案：

1. **使用者預設答案** — `CONST_MAXBOT_ANSWER_ONLINE_FILE` 外部檔案
2. **自動猜測** — 當 `auto_guess_options` 啟用時，呼叫 `util.get_answer_list_from_question_string()` 或 `util.guess_tixcraft_question()` 從題目文字推導
3. **fail_list 過濾** — 已失敗的答案不再重複使用

---

## 各平台表單填寫實作

| 平台 | 函式名稱 | 行號 | 填寫內容 | 特殊機制 |
|------|----------|------|----------|----------|
| TixCraft | `nodriver_fill_verify_form` | 4400 | 驗證問題答案 | 支援 Enter 鍵或按鈕提交 |
| TixCraft | `nodriver_tixcraft_keyin_captcha_code` | 5520 | 圖形驗證碼 | OCR 辨識後填入 |
| KKTIX | 整合於 `nodriver_kktix_assign_ticket_number` | 1433 | 驗證問題答案 | 人類化延遲 0.3-1 秒，模擬逐字輸入 |
| iBon | `nodriver_ibon_fill_verify_form` | 12122 | 驗證問題答案 | 支援雙輸入框模式（多題） |
| iBon | `nodriver_ibon_keyin_captcha_code` | 11289 | 圖形驗證碼 | OCR 辨識後填入 |
| FamiTicket | `nodriver_fami_verify` | 8301 | 驗證問題答案 | 使用 `#verifyPrefAnswer` 選擇器 |
| KHAM | `nodriver_kham_keyin_captcha_code` | 15309 | 圖形驗證碼 | OCR 辨識後填入 |
| TicketPlus | `nodriver_ticketplus_account_auto_fill` | 6364 | 登入帳號資訊 | 帳號密碼自動填入登入表單 |

---

## 平台關鍵差異

### KKTIX — 人類化填寫與 Angular 整合（行 1433-1512）

KKTIX 的驗證問題出現在票種選擇頁面。填寫流程：

- 偵測 `div.custom-captcha-inner > div > div > input` 輸入框
- 模擬人類打字：逐字寫入 `input.value += answer[i]`，每字觸發 `input` 事件
- 填寫前加入 0.3-1 秒隨機延遲，填寫後 0.5-1.2 秒再點擊按鈕
- 問題文字寫入檔案（`write_question_to_file`），供使用者查看

### iBon — 雙輸入框模式（行 12122-12241）

iBon 驗證表單可能同時出現兩個輸入框（例如同時填寫身分證與手機號碼）：

- 檢查 `form_input_count`，若為 2 且 `answer_list` 長度 >= 2，啟用多欄位模式
- 使用 `json.dumps()` 安全序列化答案避免 JS 注入
- 分別填入第一和第二個輸入框，觸發事件後點擊提交按鈕

### FamiTicket — 獨立驗證頁面（行 8301-8397）

FamiTicket 的驗證問題出現在獨立頁面（非彈窗）：

- 選擇器為 `#verifyPrefAnswer`
- 填入答案後模擬 Enter 鍵提交，或直接 `form.submit()`
- 驗證成功判斷：等待 0.5 秒後檢查 `#verifyPrefAnswer` 是否仍存在
  - 仍存在 = 答案錯誤，加入 `fail_list`
  - 消失 = 驗證通過，頁面已跳轉

### TicketPlus — 登入表單自動填寫（行 6364-6414）

TicketPlus 的表單填寫集中在登入階段而非購票階段：

- 從 `config_dict["accounts"]["ticketplus_account"]` 讀取帳號
- 先嘗試點擊全螢幕模式的登入按鈕，失敗則嘗試 RWD 模式
- 呼叫 `nodriver_ticketplus_account_sign_in()` 填入帳密
- 使用全域變數 `is_filled_ticketplus_singin_form` 避免重複填寫

---

## 問題文字紀錄機制

所有平台的驗證問題文字都會透過 `write_question_to_file()`（行 144-147）寫入檔案，讓使用者能在外部查看當前題目：

- 呼叫 `util.write_string_to_file(target_path, question_text)` 寫入磁碟
- 搭配 `auto_guess_options` 設定自動推論答案

---

## 常見問題

### 問題 1：驗證問題答案錯誤導致無限迴圈

**症狀**：系統反覆提交相同的錯誤答案

**解決方式**：所有平台都維護 `fail_list`，已提交失敗的答案不會再次使用。當所有答案耗盡時，系統等待使用者介入。

### 問題 2：輸入框 value 設定但前端框架未更新

**症狀**：填入值後提交，平台回報欄位為空

**解決方式**：填入值後必須觸發 `input` 和 `change` 事件。KKTIX 額外需要 `blur` 事件和 Angular `$apply()`。

### 問題 3：動態生成的表單欄位

**症狀**：選擇器找不到目標欄位

**解決方式**：使用 `tab.wait_for()` 或 `setInterval` 輪詢等待欄位出現後再操作。

---

## 成功標準

**SC-008: 表單填寫成功率** >= 95%
- 系統正確填寫表單欄位的次數 / 總嘗試次數

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-035 | 驗證問題自動填寫 | ✅ 實作 |
| FR-036 | 表單驗證 | ✅ 實作 |

---

## 更新日期

- **2026-03**: 補充核心實作內容、各平台差異與填寫機制說明
- **2025-11**: 初始文件建立
