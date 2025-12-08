# 任務：Discord Webhook 通知

**輸入**：來自 `/specs/009-discord-webhook/` 的設計文件
**先決條件**：plan.md、spec.md、research.md、data-model.md、contracts/

**測試**：本功能規格中未明確要求自動化測試，僅需手動測試驗證。

**組織**：任務按使用者故事分組，以實現每個故事的獨立實作和測試。

---

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務屬於哪個使用者故事（例如，US1、US2、US3）
- 在描述中包含確切的檔案路徑

---

## 使用者故事摘要

| 故事 | 標題 | 優先順序 | 說明 |
|------|------|----------|------|
| **US1** | 購票成功即時通知 | P1 | 系統在找到票券/訂單成功時發送 Discord 通知 |
| **US2** | 在網頁設定介面填入 Webhook URL | P1 | 使用者在 settings.html 設定 webhook URL |
| **US3** | 通知失敗不影響搶票 | P2 | 靜默處理錯誤，不中斷主流程 |

---

## 階段 1：基礎（Webhook 核心函數）

**目的**：建立 Webhook 發送核心函數，這是所有使用者故事的阻擋先決條件

**此階段完成條件**：三個 webhook 函數在 util.py 中實作完成

- [x] T001 在 `src/util.py` 新增 `build_discord_message(stage, platform_name)` 函數，根據階段和平台名稱生成訊息內容
- [x] T002 在 `src/util.py` 新增 `send_discord_webhook(webhook_url, stage, platform_name, timeout=3.0)` 同步發送函數
- [x] T003 在 `src/util.py` 新增 `send_discord_webhook_async(webhook_url, stage, platform_name, timeout=3.0)` 非同步包裝函數

**檢查點**：Webhook 核心函數準備就緒——現在可以開始使用者故事實作

---

## 階段 2：使用者故事 2 - 在網頁設定介面填入 Webhook URL（優先順序：P1）

**目標**：使用者可在 settings.html 網頁介面填入 Discord Webhook URL 並儲存

**獨立測試**：
1. 開啟 settings.html 頁面
2. 在「進階設定」Tab 找到 Discord Webhook URL 欄位
3. 填入測試 URL 並儲存
4. 重新載入頁面，確認 URL 已保留
5. 檢查 settings.json 確認欄位已寫入

### 使用者故事 2 的實作

- [x] T004 [US2] 在 `src/settings.json` 的 `advanced` 區塊新增 `discord_webhook_url` 欄位（預設空字串）
- [x] T005 [US2] 在 `src/www/settings.html` 的進階設定 Tab（play_sound 設定後方）新增 Discord Webhook URL 輸入欄位
- [x] T006 [US2] 在 `src/www/settings.js` 新增 `discord_webhook_url` 元素宣告
- [x] T007 [US2] 在 `src/www/settings.js` 的 `load_settings_to_form()` 函數新增 webhook URL 載入邏輯
- [x] T008 [US2] 在 `src/www/settings.js` 的 `save_changes_to_dict()` 函數新增 webhook URL 儲存邏輯

**檢查點**：使用者故事 2 完成——設定介面可正常儲存和載入 webhook URL

---

## 階段 3：使用者故事 1 - 購票成功即時通知（優先順序：P1）[MVP]

**目標**：系統在找到票券（Stage 1）和訂單成功（Stage 2）時自動發送 Discord 通知

**獨立測試**：
1. 設定有效的 Discord Webhook URL
2. 執行搶票流程
3. 在找到票券時，Discord 頻道收到「找到票券」通知
4. 在進入結帳頁面時，Discord 頻道收到「訂單成功」通知
5. 同一階段不會重複發送通知

### 使用者故事 1 的實作

**TixCraft 平台整合**：
- [x] T009 [US1] 在 `src/nodriver_tixcraft.py` TixCraft Stage 1 觸發點（票券頁面）整合 webhook 呼叫
- [x] T010 [US1] 在 `src/nodriver_tixcraft.py` TixCraft Stage 2 觸發點（結帳頁面）整合 webhook 呼叫

**iBon 平台整合**：
- [x] T011 [P] [US1] 在 `src/nodriver_tixcraft.py` iBon Stage 1 觸發點（購買按鈕點擊）整合 webhook 呼叫
- [x] T012 [P] [US1] 在 `src/nodriver_tixcraft.py` iBon Stage 2 觸發點（結帳頁面）整合 webhook 呼叫

**KKTIX 平台整合**：
- [x] T013 [P] [US1] 在 `src/nodriver_tixcraft.py` KKTIX Stage 1 觸發點（選票成功）整合 webhook 呼叫
- [x] T014 [P] [US1] 在 `src/nodriver_tixcraft.py` KKTIX Stage 2 觸發點（確認頁面）整合 webhook 呼叫

**其他平台整合**：
- [x] T015 [P] [US1] 在 `src/nodriver_tixcraft.py` KHAM Stage 2 觸發點整合 webhook 呼叫
- [x] T016 [P] [US1] 在 `src/nodriver_tixcraft.py` Cityline Stage 1 觸發點整合 webhook 呼叫
- [x] T017 [P] [US1] 在 `src/nodriver_tixcraft.py` HKTicketing Stage 1 和 Stage 2 觸發點整合 webhook 呼叫
- [x] T018 [P] [US1] 在 `src/nodriver_tixcraft.py` TicketPlus Stage 2 觸發點整合 webhook 呼叫

**檢查點**：使用者故事 1 完成——所有平台通知觸發點已整合

---

## 階段 4：使用者故事 3 - 通知失敗不影響搶票（優先順序：P2）

**目標**：確保 Webhook 發送失敗時不影響主搶票流程

**獨立測試**：
1. 設定無效的 Webhook URL（如 `https://invalid.url/test`）
2. 執行搶票流程
3. 確認搶票流程正常完成（不因 webhook 錯誤而中斷）
4. 開啟 verbose 模式，確認錯誤有記錄到日誌

### 使用者故事 3 的實作

> **注意**：此故事的需求已在 T002、T003 的錯誤處理邏輯中實作。此階段為驗證任務。

- [x] T019 [US3] 驗證 `send_discord_webhook()` 在網路超時時返回 False 而非拋出異常
- [x] T020 [US3] 驗證 `send_discord_webhook()` 在無效 URL 時返回 False 而非拋出異常
- [x] T021 [US3] 驗證 `send_discord_webhook_async()` 使用 daemon 執行緒，程式結束時自動清理
- [x] T022 [US3] 驗證 verbose 模式啟用時，錯誤訊息有正確輸出到日誌

**檢查點**：使用者故事 3 完成——錯誤處理機制驗證通過

---

## 階段 5：收尾與跨領域關注點

**目的**：文件更新和最終驗證

- [x] T023 [P] 更新 `docs/02-development/structure.md` 新增 webhook 相關函數文件
- [x] T024 [P] 執行 quickstart.md 中的設定步驟驗證功能完整性
- [x] T025 手動測試完整流程：設定 URL → 搶票 → 收到通知

---

## 相依性與執行順序

### 階段相依性

```
階段 1（基礎）
    ↓
階段 2（US2：設定介面）  ←──┐
    ↓                      │  可平行
階段 3（US1：通知整合）  ←──┘
    ↓
階段 4（US3：錯誤處理驗證）
    ↓
階段 5（收尾）
```

### 使用者故事相依性

- **US2（設定介面）**：依賴階段 1 完成（需要 settings.json 有 webhook_url 欄位）
- **US1（通知整合）**：依賴階段 1 完成（需要 webhook 函數）+ US2 完成（需要讀取設定）
- **US3（錯誤處理）**：依賴 US1 完成（需要實際觸發點來驗證）

### 每個階段內的順序

- **階段 1**：T001 → T002 → T003（循序，因 T002 依賴 T001，T003 依賴 T002）
- **階段 2**：T004 → T005/T006 [P] → T007/T008 [P]
- **階段 3**：T009 → T010 → 其餘 [P] 任務可平行
- **階段 4**：T019-T022 可平行驗證
- **階段 5**：T023/T024 [P] → T025

### 平行機會

- **階段 2**：T005（HTML）和 T006（JS 宣告）可平行
- **階段 3**：不同平台的整合任務可平行（T011-T018 標記 [P]）
- **階段 4**：所有驗證任務可平行
- **階段 5**：文件更新和 quickstart 驗證可平行

---

## 平行範例：使用者故事 1 平台整合

```bash
# 基礎階段完成後，可同時啟動不同平台的整合任務：
Task: "在 src/nodriver_tixcraft.py iBon Stage 1 觸發點整合 webhook 呼叫"
Task: "在 src/nodriver_tixcraft.py KKTIX Stage 1 觸發點整合 webhook 呼叫"
Task: "在 src/nodriver_tixcraft.py KHAM Stage 2 觸發點整合 webhook 呼叫"
Task: "在 src/nodriver_tixcraft.py Cityline Stage 1 觸發點整合 webhook 呼叫"
```

---

## 實作策略

### MVP 優先（推薦）

1. 完成階段 1：基礎（Webhook 核心函數）
2. 完成階段 2：使用者故事 2（設定介面）
3. 完成階段 3 的 TixCraft 部分（T009、T010）
4. **停止並驗證**：使用 TixCraft 測試完整流程
5. 如驗證通過，繼續其他平台整合

### 增量交付

1. 完成基礎 + US2 → 設定介面可用
2. 新增 US1 TixCraft → 手動測試 → 最小可用版本
3. 新增 US1 其他平台 → 擴展支援範圍
4. 完成 US3 驗證 → 確保穩定性
5. 收尾 + 文件 → 完整版本

---

## 任務統計

| 項目 | 數量 |
|------|------|
| **總任務數** | 25 |
| **階段 1（基礎）** | 3 |
| **階段 2（US2）** | 5 |
| **階段 3（US1）** | 10 |
| **階段 4（US3）** | 4 |
| **階段 5（收尾）** | 3 |
| **可平行任務 [P]** | 12 |
| **MVP 最小任務數** | 8（T001-T010） |

---

## 註記

- 所有檔案路徑為相對於專案根目錄
- 主要修改檔案：`util.py`、`nodriver_tixcraft.py`、`settings.html`、`settings.js`、`settings.json`
- 不需要新增任何新檔案
- 建議在每個階段完成後提交一次
- 手動測試需要實際 Discord Webhook URL
