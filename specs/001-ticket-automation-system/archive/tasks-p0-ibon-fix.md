---
description: "P0 修復任務清單 - ibon 票券數量多選問題"
---

# Tasks: ibon 票券數量多選 P0 修復

**功能分支**：`001-ticket-automation-system`
**修復名稱**：ibon 票券數量多選問題 (P0)
**基於**：debug-20251018-ibon-multiple-tickets.md
**目標**：修復用戶故事 6 的配置驅動行為 (FR-028, FR-030)

---

## 概述

本任務清單針對 **ibon NoDriver 平台的票券數量設定失敗** 問題，該問題導致用戶配置 1 張票但購票結果為 2 張。

**根本原因**：
1. 首次 DOM 查詢失敗導致票券數量未設定
2. 缺少設定驗證邏輯
3. 無重試機制且缺少 DOM 穩定性檢查

**修復策略**（MVP 優先）：
- **P0.1**：增加設定驗證邏輯（確保配置值生效）
- **P0.2**：改進 DOM 穩定性檢查（解決首次查詢失敗）
- **P0.3**：增加主程序重試機制（應對暫時性失敗）
- **P0.4**：完整測試驗證（確保修復有效）

**相關檔案**：
- 核心函數：`src/nodriver_tixcraft.py:10587` (`nodriver_ibon_ticket_number_auto_select`)
- 測試資料：`.temp/manual_logs.txt`, `.history/.temp/ibon-UTK0201_001_*.html`
- 規格參考：`specs/001-ticket-automation-system/spec.md` (FR-027~030, SC-006)
- 憲法檢查：`.specify/memory/constitution.md` (原則 V, VI, III)

---

## Phase 1: 分析與準備

**目標**：建立修復基礎，確保所有相關檔案已識別並理解

- [x] T001 讀取核心函數 `src/nodriver_tixcraft.py:10587-10686`，理解當前票券數量選擇邏輯
- [x] T002 檢查 Chrome 版本參考實作 `src/chrome_tixcraft.py:4688-4800`，對比兩版本差異
- [x] T003 驗證規格需求，確認 FR-028 (票券數量必須設為配置值) 和 FR-030 (驗證設定正確) 的定義
- [x] T004 檢查所有呼叫位置 (`src/nodriver_tixcraft.py:11245, 11834, 11918, 12053`)，列出需要修改的地點
- [x] T005 確認當前測試數據，驗證 `.temp/manual_logs.txt` 中首次失敗和設定邏輯

**檢查點**：所有檔案已定位，修復點已識別

---

## Phase 2: 修復 P0.1 - 增加設定驗證邏輯

**目標**：實現 FR-030（在繼續前驗證票券數量設定正確）

**獨立測試**：執行修復後檢查日誌，確認設定驗證通過且無誤

### 實作任務

- [x] T006 在 `src/nodriver_tixcraft.py:10646-10654` 之後新增設定驗證邏輯
  - 設定 SELECT 值後，立即讀回驗證實際值是否改變
  - 若驗證失敗，返回 `{success: false, error: "Value verification failed"}`
  - 若驗證成功，返回 `{success: true, set_value: "...", verified: true}`

- [x] T007 更新函數返回值解析邏輯 (行 10658-10678)
  - 檢查 `verified` 標籤，確認驗證已執行
  - 新增驗證失敗的錯誤消息輸出
  - 更新 debug 日誌格式，顯示驗證狀態

- [x] T008 [P] 更新所有呼叫位置的錯誤處理 (`src/nodriver_tixcraft.py:11245, 11834, 11918, 12053`)
  - 確認 `is_ticket_number_assigned` 返回值的含義
  - 準備在下一階段新增重試邏輯

**驗證標準**：
- ✅ 日誌中顯示 `[TICKET] Set to: 1` 之後有 `[TICKET] Verified: true`
- ✅ 設定失敗時日誌顯示 `[TICKET] Verification failed: Value mismatch`
- ✅ 無拼寫錯誤或語法錯誤，程式碼可執行

**檢查點**：設定驗證邏輯已實裝，驗證流程可運作

---

## Phase 3: 修復 P0.2 - 改進 DOM 穩定性檢查

**目標**：解決首次 DOM 查詢失敗的根本原因，實現 FR-027（偵測票券數量輸入類型）

**獨立測試**：首次進入 UTK0201_001 頁面時，SELECT 查詢成功率達 95% 以上

### 實作任務

- [x] T009 在 `src/nodriver_tixcraft.py:10608` 之前新增 DOM 穩定性等待邏輯
  - 新增 JavaScript 代碼，等待 SELECT 元素確實存在
  - 最多等待 3 秒，檢查間隔 100ms
  - 若超時，返回失敗訊息而非拋出異常

- [x] T010 優化查詢選擇器順序 (行 10610-10616)
  - 分析兩個查詢器的優先級，確定最常用的在前
  - 新增第三個備選查詢器：`document.querySelector('select.form-control-sm')`
  - 新增 debug 日誌，記錄使用了哪個查詢器

- [x] T011 增加頁面載入完成檢查
  - 檢查 Angular 是否載入完成 (iBon 使用 Angular SPA)
  - 檢查 Shadow DOM 是否已渲染
  - 新增 debug 日誌，記錄頁面狀態

**驗證標準**：
- ✅ 日誌顯示 `[TICKET] Found SELECT element: table.rwdtable select.form-control-sm`（或其他查詢器）
- ✅ 首次嘗試成功，無需重試
- ✅ 即使頁面載入慢，也能在 3 秒內完成查詢

**檢查點**：DOM 穩定性檢查已實裝，首次查詢成功率提升

---

## Phase 4: 修復 P0.3 - 增加主程序重試機制（指數退避）

**目標**：實現 FR-060（重試策略），提高穩定性

**獨立測試**：第一次票券選擇失敗時，自動重試並最終成功

### 實作任務

- [x] T012 在 `src/nodriver_tixcraft.py:11245` 首次呼叫位置實裝指數退避重試邏輯
  - 改為 3 次重試迴圈
  - 使用指數退避：0.5s → 1.0s → 2.0s (delay = 0.5 * 2^(attempt-1))
  - 成功時立即跳出迴圈

- [x] T013 [P] 在 `src/nodriver_tixcraft.py:11834` 呼叫位置實裝重試邏輯 (同 T012)

- [x] T014 [P] 在 `src/nodriver_tixcraft.py:11918` 呼叫位置實裝重試邏輯 (同 T012)

- [x] T015 [P] 在 `src/nodriver_tixcraft.py:12053` 呼叫位置實裝重試邏輯 (同 T012)

- [x] T016 新增重試日誌輸出 (所有位置)
  - 記錄重試次數：`[TICKET RETRY] Attempt 1/3 failed, waiting 0.5s (exponential backoff)`
  - 記錄最終結果：`[TICKET RETRY] Success after 2 attempts`

**驗證標準**：
- ✅ 日誌中顯示重試過程（例如 `Attempt 1/3 failed, retrying...`）
- ✅ 所有 4 個呼叫位置都使用相同的重試邏輯
- ✅ 最多重試 3 次，無無限迴圈

**檢查點**：重試機制已實裝，所有呼叫位置已更新

---

## Phase 5: 功能驗證與測試

**目標**：確保修復有效且不破壞其他功能，達成 SC-006（90% 成功率）

**獨立測試**：執行完整的 ibon 購票流程，驗證票券數量正確

### 測試任務

- [ ] T017 [P] 準備測試環境
  - 設定 `settings.json`: `ticket_number: 1`
  - 準備測試 URL (ibon 活動頁)
  - 清空日誌檔案

- [ ] T018 [P] 準備測試資料收集
  - 建立測試檢查清單：設定值、最終票券數量、驗證結果
  - 準備截圖位置：`src/webdriver/` 目錄

- [ ] T019 執行基準測試 (前置條件：T017 完成)
  - 執行 1 次自動化流程
  - 記錄日誌輸出
  - 驗證結帳頁顯示票券數量正確
  - **預期結果**：日誌顯示 `[TICKET] Set to: 1` 和 `[TICKET] Verified: true`

- [ ] T020 執行驗證邏輯測試 (前置條件：T019 通過)
  - 測試不同數量設定：1, 2, 3 張
  - 每個數量執行 1 次流程
  - 驗證結帳頁顯示與設定一致

- [ ] T021 執行重試測試 (前置條件：T020 通過)
  - 人為造成網路延遲 (調整頁面載入延遲)
  - 驗證是否觸發重試邏輯
  - 確認最終仍能成功設定

- [ ] T022 執行迴歸測試
  - 測試其他 iBon 流程：區域選擇、座位選擇、驗證碼
  - 測試其他平台：TixCraft, KKTIX (確保無破壞)
  - 驗證無新的錯誤訊息

**驗證標準**（SC-006：90% 成功率）：
- ✅ 設定 1 張時，結帳頁顯示 1 張（成功率 100%）
- ✅ 設定 2 張時，結帳頁顯示 2 張（成功率 100%）
- ✅ 重試測試中，最多重試 2 次後成功
- ✅ 無新的迴歸 bug

**檢查點**：修復有效，未破壞現有功能

---

## Phase 6: 代碼審查與文件更新

**目標**：確保代碼品質和文件同步

### 審查任務

- [ ] T023 代碼審查：檢查修復代碼風格
  - 符合專案 Python 編碼規範
  - 無硬編碼業務邏輯
  - 錯誤處理完整
  - 無 emoji（Python 代碼中禁止）

- [ ] T024 檢查憲法合規性 (`.specify/memory/constitution.md`)
  - ✅ V. 設定驅動開發：配置值與實際執行值一致
  - ✅ VI. 測試驅動穩定性：有驗證和重試邏輯
  - ✅ III. 三問法則：修復簡潔且不破壞相容性

- [ ] T025 檢查規格符合性
  - ✅ FR-027：偵測票券數量輸入類型（改進）
  - ✅ FR-028：票券數量設為配置值（修復）
  - ✅ FR-030：驗證票券數量設定正確（新增）
  - ✅ SC-006：票券數量設定 90% 成功率（達成）

### 文件更新任務

- [ ] T026 [P] 更新 `docs/02-development/structure.md`
  - 更新 iBon NoDriver 平台完整度評分
  - 新增函數註解：`nodriver_ibon_ticket_number_auto_select` (改進內容)

- [ ] T027 [P] 建立或更新 `docs/05-troubleshooting/ibon_nodriver_ticket_selection.md`
  - 記錄此次修復的背景
  - 記錄症狀和解決方案
  - 包含日誌範例

- [ ] T028 [P] 更新 `docs/04-testing-debugging/debugging_methodology.md`
  - 在常見問題區塊新增「SELECT 元素查詢失敗」
  - 記錄此類問題的通用解決方案

- [ ] T029 更新 `CHANGELOG.md`
  - 新增條目：修復 ibon 票券數量選擇
  - 記錄版本號和日期
  - 參考此修復的 GitHub issue（如有）

- [ ] T030 [P] 同步 git 提交資訊
  - 按照 `.specify/memory/constitution.md` IX 原則準備 commit message
  - 主題行：使用英文，描述修復內容
  - 格式：`[bugfix] ibon: fix ticket number selection validation`

**驗證標準**：
- ✅ 代碼無風格問題
- ✅ 符合所有憲法原則
- ✅ 符合所有規格需求
- ✅ 文件已更新

**檢查點**：代碼審查通過，文件已同步

---

## Phase 7: 交付與總結

**目標**：完成修復並準備交付

### 交付任務

- [ ] T031 建立修復總結報告
  - 複製 `docs/07-project-tracking/debug-20251018-ibon-multiple-tickets.md` 內容
  - 新增修復執行記錄：執行時間、測試結果、遇到的問題
  - 新增性能指標：修復前後的成功率對比

- [ ] T032 準備版本更新
  - 更新版本號（如 CONST_APP_VERSION）
  - 記錄修復的里程碑

- [ ] T033 執行最終迴歸測試
  - 完整執行 ibon 購票流程 1 次
  - 測試其他平台 (TixCraft, KKTIX) 各 1 次
  - 確認無新問題

- [ ] T034 提交修復
  - 按照 commit message 規範進行 git commit
  - 使用 `/gsave` 命令提交（如果適用）

**驗證標準**：
- ✅ 修復報告已建立
- ✅ 所有迴歸測試通過
- ✅ git commit 已提交

**檢查點**：修復已完成並交付

---

## 依賴關係圖

```
Phase 1 (分析)
     ↓
Phase 2 (設定驗證) → Phase 3 (DOM穩定性) → Phase 4 (重試機制)
     ↓                    ↓                      ↓
Phase 5 (測試驗證) ←────────────────────────────→
     ↓
Phase 6 (代碼審查)
     ↓
Phase 7 (交付)
```

**關鍵路徑**：
1. T001-T005：基礎分析
2. T006-T008：設定驗證（先決條件）
3. T009-T011：DOM 穩定性（並行可選）
4. T012-T016：重試機制（並行可選）
5. T017-T022：功能測試（依序執行，驗證修復）
6. T023-T030：代碼審查和文件
7. T031-T034：交付

---

## 並行執行策略

### 可並行的任務組合

#### 並行組 1：代碼修復 (Phase 2-4)
```bash
# Phase 2 執行中
T006-T008: 設定驗證邏輯

# 並行 Phase 3
T009-T011: DOM 穩定性檢查

# 並行 Phase 4
T012-T015: 所有呼叫位置的重試邏輯
T016: 重試日誌
```

#### 並行組 2：測試準備 (Phase 5)
```bash
T017: 準備測試環境
T018: 準備測試資料
T019: 執行基準測試 (依序)
```

#### 並行組 3：文件更新 (Phase 6)
```bash
T026: structure.md 更新
T027: troubleshooting 文件建立
T028: debugging_methodology 更新
T029: CHANGELOG 更新 (依序，在 T030 前)
T030: git commit 準備
```

### 實際執行時間估計

| 階段 | 任務數 | 順序任務 | 並行時間 | 估計時間 |
|------|--------|---------|--------|---------|
| Phase 1 | 5 | 5 | 1 | ~30 分鐘 |
| Phase 2 | 3 | 3 | 1 | ~20 分鐘 |
| Phase 3 | 3 | 1 | 2 | ~25 分鐘 |
| Phase 4 | 5 | 1 | 4 | ~30 分鐘 |
| Phase 5 | 6 | 2 | 2 | ~60 分鐘 (含測試等待) |
| Phase 6 | 8 | 2 | 3 | ~40 分鐘 |
| Phase 7 | 4 | 2 | 1 | ~30 分鐘 |
| **總計** | **34** | **16** | **14** | **~3.5 小時** |

---

## 任務總結

### 按優先度

| 優先度 | 任務 | 數量 |
|--------|------|------|
| **P0** | 核心修復 (T006-T016) | 11 |
| **P1** | 測試驗證 (T017-T022) | 6 |
| **P2** | 文件更新 (T023-T030) | 8 |
| **P3** | 交付 (T031-T034) | 4 |
| **總計** | | **34** |

### 按相關檔案

| 檔案 | 任務 |
|------|------|
| `src/nodriver_tixcraft.py` | T006, T007, T009, T010, T011, T012, T013, T014, T015, T016 (10 項) |
| `src/chrome_tixcraft.py` | T002 (參考) |
| `docs/` | T026, T027, T028, T029 (4 項) |
| `CHANGELOG.md` | T029 |
| `.git/` | T030, T034 |
| 測試相關 | T017, T018, T019, T020, T021, T022 (6 項) |

### 成功標準

✅ **修復完成標準**：
- [ ] 所有 P0 修復實裝完成 (T006-T016)
- [ ] 測試驗證全部通過 (T019-T022)
- [ ] 代碼審查通過 (T023-T025)
- [ ] 文件同步完成 (T026-T030)
- [ ] git commit 已提交 (T030, T034)

✅ **品質標準**：
- [ ] 票券數量設定成功率 ≥ 90% (SC-006)
- [ ] 無新的迴歸 bug
- [ ] 代碼符合風格規範
- [ ] 憲法所有原則符合

---

## 使用說明

### 執行任務

1. **開始修復**：按順序完成 Phase 1 (分析) 的所有任務
2. **並行開發**：Phase 2-4 的修復可按順序或部分並行
3. **驗證修復**：Phase 5 的測試必須順序執行
4. **最終化**：Phase 6-7 按順序執行

### 標記進度

使用核取方塊標記已完成任務：
```markdown
- [x] T001 已完成
- [ ] T002 未開始
```

### 遇到問題

如修復過程中遇到問題，參考：
- 原始 debug 報告：`docs/07-project-tracking/debug-20251018-ibon-multiple-tickets.md`
- 規格文件：`specs/001-ticket-automation-system/spec.md`
- 憲法：`.specify/memory/constitution.md`

---

**任務清單版本**：1.0
**生成日期**：2025-10-18
**相關 Debug 報告**：debug-20251018-ibon-multiple-tickets.md
