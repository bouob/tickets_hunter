# 12-Stage 搶票機制文件索引

**文件說明**：提供 12 階段搶票自動化機制的完整索引與導覽，便於查找相關文件
**最後更新**：2025-11-27

---

## 文件結構

```
docs/03-mechanisms/
├── README.md                    ← 本文件（索引與導覽）
│
├── 01-environment-init.md       Stage 1:  環境初始化
├── 02-authentication.md         Stage 2:  身份認證
├── 03-page-monitoring.md        Stage 3:  頁面監控 + 版面偵測 (v2.0+)
├── 04-date-selection.md         Stage 4:  日期選擇
├── 05-area-selection.md         Stage 5:  區域選擇
├── 06-ticket-count.md           Stage 6:  票數設定
├── 07-captcha-handling.md       Stage 7:  驗證碼處理 + 自動答題 (v2.0+)
├── 08-form-filling.md           Stage 8:  表單填寫 + 實名認證 (v2.0+)
├── 09-terms-agreement.md        Stage 9:  同意條款
├── 10-order-submit.md           Stage 10: 訂單送出
├── 11-queue-payment.md          Stage 11: 排隊付款
├── 12-error-handling.md         Stage 12: 錯誤處理
│
└── 13-active-polling-pattern.md 跨階段: Active Polling 主動輪詢機制 ✅ NEW

✅ = 已完成詳細文件化
```

---

## 概述

本目錄包含**搶票自動化系統的 12 個核心機制**的詳細技術文件。每個 Stage 代表購票流程中的一個關鍵階段,從環境初始化到錯誤處理,完整覆蓋整個自動化流程。

**文件特色**：
- **清晰的流程圖**：每個機制都有 ASCII 流程圖說明
- **實際程式碼片段**：20-60 行關鍵程式碼,含詳細註解
- **平台差異對照**：5 平台（KKTIX, TixCraft, iBon, TicketPlus, KHAM）完整比較
- **實作檢查清單**：新平台開發時的完整 checklist
- **FAQ 常見問題**：實務經驗與疑難排解

---

## 12-Stage 完整流程

```
┌────────────────────────────────────────────────────────────────┐
│                       搶票自動化 12 階段流程                      │
└────────────────────────────────────────────────────────────────┘

 [1. 環境初始化] → [2. 身份驗證] → [3. 頁面監控]
       ↓                ↓              ↓
 ═══════════════════════════════════════════════════════════
 │                    核心購票流程（已文件化）                │
 ═══════════════════════════════════════════════════════════
       ↓                ↓              ↓
 [4. 日期選擇] → [5. 區域選擇] → [6. 票數設定]
   ✅ 完成         ✅ 完成           待文件化
       ↓                ↓              ↓
 [7. 驗證碼處理] → [8. 表單填寫] → [9. 同意條款]
   ✅ 完成          待文件化         待文件化
       ↓                ↓              ↓
 [10. 訂單送出] → [11. 排隊付款] → [12. 錯誤處理]
   待文件化         待文件化         待文件化
```

---

## 已完成的機制文件（3/12）

### ✅ Stage 4: 日期選擇機制

**文件**：[04-date-selection.md](./04-date-selection.md)

**核心技術**：
- Early Return Pattern（優先級驅動關鍵字匹配）
- Conditional Fallback（條件回退機制）
- Shadow DOM Penetration（iBon - DOMSnapshot）

**主要範例平台**：TixCraft

**適用場景**：
- 實作新平台的日期選擇功能
- 了解 Feature 003: Keyword Priority Fallback
- 學習 Shadow DOM 處理技術

**關鍵程式碼片段**：
- Early Return Pattern (TixCraft, Line 2759-2807)
- Conditional Fallback (TixCraft, Line 2863-2876)
- DOMSnapshot 日期選擇 (iBon, Line 5860-6142)

---

### ✅ Stage 5: 區域選擇機制

**文件**：[05-area-selection.md](./05-area-selection.md)

**核心技術**：
- Early Return Pattern（關鍵字優先匹配）
- Conditional Fallback（智能回退）
- keyword_exclude（排除關鍵字過濾）
- Ticket Availability Check（票數檢查）

**主要範例平台**：TixCraft

**適用場景**：
- 實作新平台的區域選擇功能
- 了解 AND/OR 邏輯關鍵字匹配
- 學習票數可用性檢查機制

**關鍵程式碼片段**：
- Early Return Pattern (TixCraft, Line 3048-3061)
- Conditional Fallback (TixCraft, Line 3079-3094)
- keyword_exclude 過濾 (TixCraft, Line 3194-3197)
- AND 邏輯支援 (TixCraft, Line 3206-3231)

---

### ✅ Stage 7: 驗證碼處理機制

**文件**：[07-captcha-handling.md](./07-captcha-handling.md)

**核心技術**：
- ddddocr OCR 引擎（圖形驗證碼辨識）
- 問答匹配引擎（KKTIX 問答式驗證碼）
- 自動答題機制（KKTIX, v2.0+）
- fail_list 機制（避免重複錯誤答案）
- 人類化延遲（隨機延遲模擬真人）

**主要範例平台**：KKTIX（問答式 + 自動答題）+ TixCraft（OCR）

**適用場景**：
- 實作圖形驗證碼 OCR 辨識
- 實作問答式驗證碼處理
- 實作自動答題功能（v2.0+）
- 了解 Shadow DOM 驗證碼圖片擷取

**關鍵程式碼片段**：
- 問答式驗證碼 (KKTIX, Line 1171-1330)
- Canvas OCR 擷取 (TixCraft, Line 3737-3770)
- Shadow DOM 驗證碼 (iBon, Line 9643-9730)

---

## 待文件化的機制（9/12）

以下機制已完成實作,但尚未撰寫詳細文件:

### Stage 1: 環境初始化
- NoDriver 瀏覽器啟動
- 設定檔載入與驗證
- 代理伺服器設定

### Stage 2: 身份驗證
- Cookie 登入（TixCraft）
- 帳號密碼登入（KKTIX, iBon）
- 自動登入檢測

### Stage 3: 頁面監控
- 即將開賣頁面自動重載（TixCraft）
- 售罄檢測
- 頁面狀態監控
- 版面自動偵測（TicketPlus, v2.0+）

### Stage 6: 票數設定
- 票數輸入欄位填寫
- 票數驗證
- Angular 事件觸發（iBon）

### Stage 8: 表單填寫
- 個人資料自動填寫
- 自訂問題答案匹配
- 必填欄位驗證
- 實名認證處理（FamiTicket, iBon, v2.0+）

### Stage 9: 同意條款處理
- 自動勾選同意條款
- 特殊對話框處理（TicketPlus）
- 實名制卡片接受

### Stage 10: 訂單確認與送出
- 訂單資訊驗證
- 送出按鈕點擊
- 音效通知

### Stage 11: 排隊與付款
- 排隊狀態監控（Cityline）
- 付款頁面處理
- 超時重試

### Stage 12: 錯誤處理與重試
- 全域錯誤處理
- 重試策略
- 錯誤日誌記錄

**注意**：以上機制的完整規格請參考 [12-Stage 標準文件](../02-development/ticket_automation_standard.md)

---

## 平台參考實作

除了機制文件外,我們也提供**平台特定的參考實作文件**,展示每個平台的獨特設計：

### KKTIX 參考實作

**文件**：[kktix-reference.md](../03-implementation/platform-examples/kktix-reference.md)

**平台特色**：
- **問答式驗證碼**：最具挑戰性的驗證碼類型
- **價格列表模式**：兩階段區域選擇（價格表 + 票數輸入）
- **fail_list 機制**：智能答案選擇避免重複錯誤

**推薦閱讀**：
- 實作問答式驗證碼處理
- 了解價格列表模式的區域選擇
- 學習 fail_list 機制設計

---

### iBon 參考實作

**文件**：[ibon-reference.md](../03-implementation/platform-examples/ibon-reference.md)

**平台特色**：
- **closed Shadow DOM**：最具技術挑戰性的 DOM 結構
- **DOMSnapshot 平坦化**：突破 Shadow DOM 限制的關鍵技術
- **Angular SPA**：單頁應用程式事件觸發

**推薦閱讀**：
- 學習 DOMSnapshot API 完整應用
- 了解 closed Shadow DOM 處理方案
- 掌握 Angular 事件觸發技巧

---

## 文件使用指南

### 新平台開發流程

1. **閱讀 12-Stage 標準**
   - 文件：`docs/02-development/ticket_automation_standard.md`
   - 了解每個階段的標準流程

2. **參考已完成的機制文件**
   - Stage 4: 日期選擇
   - Stage 5: 區域選擇
   - Stage 7: 驗證碼處理

3. **參考相似平台的實作**
   - 問答式驗證碼 → 參考 KKTIX
   - Shadow DOM → 參考 iBon
   - 標準流程 → 參考 TixCraft

4. **使用實作檢查清單**
   - 每個機制文件都包含完整 checklist
   - 逐項檢查確保功能完整

### 文件閱讀優先順序

**初次接觸專案**：
1. [12-Stage 標準](../02-development/ticket_automation_standard.md) - 了解完整流程
2. [Stage 4: 日期選擇](./04-date-selection.md) - 學習核心機制
3. [Stage 5: 區域選擇](./05-area-selection.md) - 理解關鍵字匹配
4. [KKTIX 參考實作](../03-implementation/platform-examples/kktix-reference.md) - 完整範例

**開發新平台**：
1. [12-Stage 標準](../02-development/ticket_automation_standard.md) - 確認功能需求
2. 相關機制文件（Stage 4, 5, 7）- 實作細節
3. 相似平台參考實作 - 程式碼範例
4. [程式碼結構分析](../02-development/structure.md) - 函數索引

**除錯問題**：
1. [除錯方法論](../04-testing-debugging/debugging_methodology.md) - 系統化除錯
2. 相關機制文件 FAQ - 常見問題
3. [疑難排解索引](../05-troubleshooting/README.md) - 已知問題解決方案

---

## 核心設計原則

所有機制文件遵循以下設計原則：

### 1. Early Return Pattern（優先級驅動）

**核心理念**：關鍵字按優先級排列,第一個匹配立即停止。

**應用階段**：Stage 4（日期選擇）、Stage 5（區域選擇）

**優勢**：
- 確保優先級較高的選項先被選中
- 避免掃描所有選項後再選擇
- 符合使用者的直覺期望

**詳細說明**：[Feature 003: Keyword Priority Fallback](../../specs/003-keyword-priority-fallback/implementation-guide.md)

---

### 2. Conditional Fallback（條件回退）

**核心理念**：關鍵字失敗時,根據使用者設定決定是否回退到 auto_select_mode。

**設定開關**：
- `date_auto_fallback`（日期選擇）
- `area_auto_fallback`（區域選擇）

**模式**：
- **嚴格模式**（false, 預設）：不自動選擇,等待手動介入
- **自動模式**（true）：回退到 auto_select_mode 選擇

**應用階段**：Stage 4（日期選擇）、Stage 5（區域選擇）

**詳細說明**：各機制文件的「條件回退機制」章節

---

### 3. Active Polling Pattern（主動輪詢）

**核心理念**：刷新冷卻期間持續偵測，不錯過快速出現的機會。

**傳統問題**：
```
[reload] ──────── 8s sleep ────────→ [check]
                     ↑
               票出現但沒偵測到
```

**Active Polling 解決方案**：
```
[reload] → [0.2s check] → [0.2s check] → ... → [found!]
                  ↑
            立即偵測並處理
```

**關鍵參數**：
- 輪詢間隔：0.2 秒
- 輪詢次數：`interval * 5`（自動計算）
- 最快反應時間：0.2 秒（相比傳統 8 秒，提升 **40x**）

**應用階段**：Stage 4（日期選擇）、Stage 5（區域選擇）

**詳細說明**：[13-active-polling-pattern.md](./13-active-polling-pattern.md)

---

### 4. 設定驅動開發

**核心理念**：所有行為由 `settings.json` 控制,使用者友善。

**設定層級**：
```json
{
  "date_auto_select": { "enable": true, "mode": "random" },  // Stage 4
  "area_auto_select": { "enable": true, "area_keyword": "" }, // Stage 5
  "ocr_captcha": { "enable": true, "beta": true },           // Stage 7
  "kktix": { "auto_press_next_step_button": true }           // 平台特定
}
```

**優勢**：
- 無需修改程式碼即可調整行為
- 支援多種購票策略
- 使用者可輕鬆實驗不同設定

---

## 跨文件導航

### 核心文件

- 📖 [12-Stage 標準](../02-development/ticket_automation_standard.md) - 完整流程規範
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 函數索引
- 📋 [開發指南](../02-development/development_guide.md) - 開發規範
- 📋 [程式碼範本](../02-development/coding_templates.md) - 寫法範本

### API 參考

- 📋 [NoDriver API 指南](../03-api-reference/nodriver_api_guide.md) - NoDriver 完整參考
- 📋 [CDP 協議參考](../03-api-reference/cdp_protocol_reference.md) - Chrome DevTools Protocol
- 📋 [ddddocr API 指南](../03-api-reference/ddddocr_api_guide.md) - OCR 引擎

### 測試與除錯

- 🧪 [測試執行指南](../04-testing-debugging/testing_execution_guide.md) - 標準測試流程
- 🐛 [除錯方法論](../04-testing-debugging/debugging_methodology.md) - 系統化除錯

### 疑難排解

- 🔧 [疑難排解索引](../05-troubleshooting/README.md) - 已知問題解決方案
- 🔧 [iBon NoDriver 修復](../05-troubleshooting/ibon_nodriver_fixes_2025-10-03.md) - iBon 特定問題

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2025-11 | 初版：建立機制文件索引 |
| | | ✅ Stage 4: 日期選擇機制 |
| | | ✅ Stage 5: 區域選擇機制 |
| | | ✅ Stage 7: 驗證碼處理機制 |
| | | ✅ KKTIX 參考實作 |
| | | ✅ iBon 參考實作 |
| v2.0 | 2025-11-27 | 新增 v2.0 子功能說明 |
| | | 🆕 Stage 3: 版面自動偵測（TicketPlus）|
| | | 🆕 Stage 7: 自動答題機制（KKTIX）|
| | | 🆕 Stage 8: 實名認證處理（FamiTicket, iBon）|

**未來計畫**：
- Stage 1-3: 前置階段機制文件
- Stage 6, 8-12: 後續階段機制文件
- TixCraft 參考實作
- TicketPlus 參考實作
- KHAM 參考實作

---

## 貢獻指南

### 撰寫新機制文件

**文件模板**：參考 `04-date-selection.md` 的結構

**必須包含的章節**：
1. **概述**：目的、輸入、輸出、關鍵技術
2. **核心流程**：ASCII 流程圖（5-6 步驟）
3. **關鍵程式碼片段**：3-5 個片段（20-60 行）
4. **平台實作差異**：對照表格（5 平台）
5. **實作檢查清單**：6-8 大類,25+ 檢查項目
6. **FAQ 常見問題**：4-6 個問題
7. **相關文件**：交叉引用
8. **版本歷史**：變更記錄

**程式碼片段規範**：
- 20-60 行（不超過一個螢幕）
- 包含關鍵邏輯,省略細節
- 標註行號（Line xxx-xxx）
- 中文註解說明關鍵步驟

### 更新現有文件

**小幅更新**（錯字修正、補充說明）：
- 直接修改文件
- 更新「版本歷史」區塊

**重大變更**（新增功能、架構調整）：
- 更新相關程式碼片段
- 更新平台實作差異表
- 新增 FAQ 問題（如適用）
- 更新版本號（v1.x → v2.0）

---

**最後更新**：2025-11-27（v2.0）
**維護者**：Tickets Hunter 開發團隊
