---
description: "關鍵字優先選擇與條件式自動遞補 - 實作任務清單"
---

# 任務：關鍵字優先選擇與條件式自動遞補

**輸入**：來自 `/specs/003-keyword-priority-fallback/` 的設計文件
**前置需求**：plan.md、spec.md、research.md、data-model.md、contracts/config-schema.md

**功能摘要**：
- 關鍵字優先匹配（早期返回）：第一個匹配成功立即選擇並停止檢查
- 條件式自動遞補：新增布林開關控制「全部未匹配」時的行為
- 預設值為 `false`（嚴格模式：僅選擇關鍵字匹配的選項）

**測試策略**：
- 僅手動執行測試（無需撰寫測試檔案）
- 使用實際搶票測試驗證邏輯（30 秒 timeout）
- 驗證日誌輸出確保行為正確

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（US1、US2、US3）
- 描述中包含精確的檔案路徑

---

## 階段一：初始化（無需實作）

**本功能不需要建立新專案或新檔案**，因此跳過此階段。

---

## 階段二：基礎建設（設定檔擴展）

**目的**：擴展設定檔結構，新增遞補開關欄位

**⚠️ 關鍵**：本階段完成後，核心邏輯與 UI 實作才可開始

- [X] T001 [P] 在 `src/settings.py` 的 `get_default_config()` 函數中新增 `config_dict["date_auto_fallback"] = False` 和 `config_dict["area_auto_fallback"] = False`
- [X] T002 [P] 在 `src/settings_old.py` 的 `get_default_config()` 函數中新增 `config_dict["date_auto_fallback"] = False` 和 `config_dict["area_auto_fallback"] = False`

**檢查點**：設定檔預設值已擴展，可開始核心邏輯實作

---

## 階段三：User Story 1 - 關鍵字優先匹配（早期返回） (Priority: P1) 🎯 MVP

**目標**：實作關鍵字優先匹配邏輯，一旦第一個關鍵字匹配成功立即選擇並停止檢查

**獨立測試**：
- 設定 `date_keyword = "11/16;11/17;11/18"`，頁面僅提供 "11/17"
- 驗證系統是否：(1) 跳過第一個關鍵字；(2) 在第二個關鍵字匹配時立即選擇；(3) 不檢查第三個關鍵字；(4) 日誌顯示 "Keyword #2 matched"

### User Story 1 實作

**日期選擇邏輯（早期返回模式）**:

- [X] T003 [US1] 在 `src/nodriver_tixcraft.py` 的日期選擇函數開頭，檢查 `date_auto_select.enable` 布林欄位，若為 `False` 則立即返回，不執行任何日期選擇邏輯（FR-001）
- [X] T004 [US1] 在 `src/nodriver_tixcraft.py` 的日期選擇函數中（搜尋 `date_keyword` 相關邏輯），實作早期返回模式：依序檢查日期關鍵字清單，一旦第一個關鍵字在 `formated_area_list` 中匹配成功，立即選擇該日期並返回，不再檢查後續關鍵字（FR-003）
- [X] T005 [US1] 在日期選擇函數中，新增英文日誌訊息：當開始檢查關鍵字時輸出 `[DATE KEYWORD] Start checking keywords in order: [清單]`（FR-013）
- [X] T006 [US1] 在日期選擇函數中，新增英文日誌訊息：當第 N 個關鍵字匹配成功時輸出 `[DATE KEYWORD] Keyword #N matched: '[關鍵字]'` 和 `[DATE SELECT] Selected date: [選項] (keyword match)`（FR-014）
- [X] T007 [US1] 在日期選擇函數中，新增英文日誌訊息：當所有關鍵字都未匹配時輸出 `[DATE KEYWORD] All keywords failed to match`（FR-015）
- [X] T008 [US1] 在日期選擇函數中，將舊版的「掃描所有關鍵字後將匹配項加入陣列再選擇」的邏輯完整保留於註解區塊，標記為 `# DEPRECATED: Old logic - scan all keywords and select from array. Will be removed after 2 weeks.`，確保可快速回滾至舊邏輯（保留 2 週後移除）（FR-029）
- [X] T009 [US1] 在日期選擇函數中，驗證關鍵字匹配邏輯支援 AND 邏輯（空格分隔），當關鍵字包含空格時（如 "1280 一般"），選項必須同時包含所有詞彙才視為匹配成功（FR-005）

**區域選擇邏輯（早期返回模式）**:

- [X] T010 [US1] 在 `src/nodriver_tixcraft.py` 的區域選擇函數開頭，檢查 `area_auto_select.enable` 布林欄位，若為 `False` 則立即返回，不執行任何區域選擇邏輯（FR-002）
- [X] T011 [US1] 在 `src/nodriver_tixcraft.py` 的區域選擇函數中（搜尋 `area_keyword` 相關邏輯），實作早期返回模式：依序檢查區域關鍵字清單，一旦第一個關鍵字在 `formated_area_list` 中匹配成功，立即選擇該區域並返回，不再檢查後續關鍵字（FR-004）
- [X] T012 [US1] 在區域選擇函數中，新增英文日誌訊息：當開始檢查關鍵字時輸出 `[AREA KEYWORD] Start checking keywords in order: [清單]`（FR-013）
- [X] T013 [US1] 在區域選擇函數中，新增英文日誌訊息：當第 N 個關鍵字匹配成功時輸出 `[AREA KEYWORD] Keyword #N matched: '[關鍵字]'` 和 `[AREA SELECT] Selected area: [選項] (keyword match)`（FR-014）
- [X] T014 [US1] 在區域選擇函數中，新增英文日誌訊息：當所有關鍵字都未匹配時輸出 `[AREA KEYWORD] All keywords failed to match`（FR-015）
- [X] T015 [US1] 在區域選擇函數中，將舊版的「掃描所有關鍵字後將匹配項加入陣列再選擇」的邏輯完整保留於註解區塊，標記為 `# DEPRECATED: Old logic - scan all keywords and select from array. Will be removed after 2 weeks.`，確保可快速回滾至舊邏輯（保留 2 週後移除）（FR-029）
- [X] T016 [US1] 在區域選擇函數中，驗證關鍵字匹配邏輯支援 AND 邏輯（空格分隔），當關鍵字包含空格時（如 "1280 一般"），選項必須同時包含所有詞彙才視為匹配成功（FR-005）

**檢查點**：此時 User Story 1 應可完全獨立運作並可測試——執行手動測試驗證早期返回模式

---

## 階段四：User Story 2 - 條件式自動遞補控制 (Priority: P1) 🎯 MVP

**目標**：實作條件式遞補邏輯，當所有關鍵字都未匹配時，根據開關決定是否觸發自動遞補

**獨立測試**：
- 設定 `date_keyword = "11/16;11/17"` 和 `date_auto_fallback = false`（預設值）
- 頁面僅有 "11/18" 和 "11/19"（關鍵字全部失敗）
- 驗證系統是否不選擇任何日期並記錄 "fallback is disabled"
- 設定 `date_auto_fallback = true` 時，驗證系統是否根據 `date_select_order` 自動選擇可用日期

### User Story 2 實作

**日期遞補邏輯**:

- [X] T017 [US2] 在 `src/nodriver_tixcraft.py` 的日期選擇函數中，當所有日期關鍵字都未匹配成功時，使用 `config_dict.get('date_auto_fallback', False)` 安全存取該欄位（FR-008）
- [X] T018 [US2] 在日期選擇函數中，若 `date_auto_fallback = True`，根據 `date_select_order` 從 `formated_area_list` 中自動選擇可用日期，並輸出日誌 `[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback` 和 `[DATE SELECT] Selected date: [選項] (fallback)`（FR-008, FR-016）
- [X] T019 [US2] 在日期選擇函數中，若 `date_auto_fallback = False`，返回 None 或 False（等待手動介入），並輸出日誌 `[DATE FALLBACK] date_auto_fallback=false, fallback is disabled` 和 `[DATE SELECT] Waiting for manual intervention`（FR-008, FR-017）
- [X] T020 [US2] 在日期選擇函數中，當遞補選擇失敗（`formated_area_list` 為空，所有選項都被排除）時，輸出日誌 `[DATE FALLBACK] No available options after exclusion`（FR-018）

**區域遞補邏輯**:

- [X] T021 [US2] 在 `src/nodriver_tixcraft.py` 的區域選擇函數中，當所有區域關鍵字都未匹配成功時，使用 `config_dict.get('area_auto_fallback', False)` 安全存取該欄位（FR-009）
- [X] T022 [US2] 在區域選擇函數中，若 `area_auto_fallback = True`，根據 `area_select_order` 從 `formated_area_list` 中自動選擇可用區域，並輸出日誌 `[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback` 和 `[AREA SELECT] Selected area: [選項] (fallback)`（FR-009, FR-016）
- [X] T023 [US2] 在區域選擇函數中，若 `area_auto_fallback = False`，返回 None 或 False（等待手動介入），並輸出日誌 `[AREA FALLBACK] area_auto_fallback=false, fallback is disabled` 和 `[AREA SELECT] Waiting for manual intervention`（FR-009, FR-017）
- [X] T024 [US2] 在區域選擇函數中，當遞補選擇失敗（`formated_area_list` 為空，所有選項都被排除）時，輸出日誌 `[AREA FALLBACK] No available options after exclusion`（FR-018）

**檢查點**：此時 User Story 1 與 2 均應能獨立運作——執行手動測試驗證遞補邏輯（啟用/停用）

---

## 階段五：User Story 3 - UI 控制項設計與整合 (Priority: P2)

**目標**：在 settings.html 和 settings_old.py 新增遞補開關的 UI 控制項，讓使用者可視覺化調整

**獨立測試**：
- **網頁版**：開啟 settings.html，驗證核取方塊、說明文字、儲存功能、重新載入後狀態一致
- **桌面版**：啟動 settings_old.py，驗證核取方塊、tooltip、多語言支援、儲存功能

### User Story 3 實作

**網頁版 (settings.html)**:

- [X] T025 [P] [US3] 在 `settings.html` 的「日期自動點選」區塊下新增「日期自動遞補」核取方塊（id="date_auto_fallback"），預設未勾選，附帶說明文字「當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉）」（FR-019）
- [X] T026 [P] [US3] 在 `settings.html` 的「區域自動點選」區塊下新增「區域自動遞補」核取方塊（id="area_auto_fallback"），預設未勾選，附帶說明文字「當所有區域關鍵字都未匹配時，是否自動選擇可用區域（預設關閉）」（FR-020）
- [X] T027 [US3] 在 `settings.html` 的 JavaScript 中，新增載入設定時讀取 `date_auto_fallback` 和 `area_auto_fallback` 欄位的邏輯，若欄位不存在則使用預設值 `false`（FR-021）
- [X] T028 [US3] 在 `settings.html` 的 JavaScript 中，新增儲存設定時將核取方塊狀態（checked/unchecked）寫入 `date_auto_fallback` 和 `area_auto_fallback` 欄位為布林值（true/false）的邏輯（FR-022）

**桌面版 (settings_old.py tkinter GUI)**:

- [X] T029 [P] [US3] 在 `src/settings_old.py` 的多語言翻譯區段，新增繁中「日期自動遞補」（zh_tw["date_auto_fallback"]）、「區域自動遞補」（zh_tw["area_auto_fallback"]）、英文「Date Auto Fallback」（en_us["date_auto_fallback"]）、「Area Auto Fallback」（en_us["area_auto_fallback"]）、日文「日付自動フォールバック」（ja_jp["date_auto_fallback"]）、「エリア自動フォールバック」（ja_jp["area_auto_fallback"]）（FR-025）
- [X] T030 [P] [US3] 在 `src/settings_old.py` 的多語言翻譯區段，新增完整說明文字的三語翻譯（用於 tooltip），內容為「當所有日期/區域關鍵字都未匹配時，是否自動選擇可用日期/區域（預設關閉，僅選擇關鍵字匹配的選項）」（FR-026）
- [X] T031 [US3] 在 `src/settings_old.py` 的日期自動選擇區塊（frame_group_tixcraft）中，緊接在 chk_date_auto_select 主開關下方，新增「日期自動遞補」核取方塊（chk_date_auto_fallback），使用 Checkbutton 控制項，預設未勾選，變數名稱為 chk_state_date_auto_fallback（FR-023）
- [X] T032 [US3] 在 `src/settings_old.py` 的區域自動選擇區塊（frame_group_area）中，緊接在 chk_area_auto_select 主開關下方，新增「區域自動遞補」核取方塊（chk_area_auto_fallback），使用 Checkbutton 控制項，預設未勾選，變數名稱為 chk_state_area_auto_fallback（FR-024）
- [X] T033 [US3] 為 chk_date_auto_fallback 和 chk_area_auto_fallback 核取方塊新增 tooltip（使用 tkinter 的 ToolTip 或類似機制），滑鼠懸停時顯示完整說明文字（依當前語言顯示對應翻譯）（FR-026）
- [X] T034 [US3] 在 `src/settings_old.py` 的儲存邏輯中（搜尋 `config_dict["date_auto_select"]["enable"]` 相關程式碼），新增讀取 chk_state_date_auto_fallback.get() 和 chk_state_area_auto_fallback.get() 的邏輯，並寫入 `config_dict["date_auto_fallback"]` 和 `config_dict["area_auto_fallback"]` 為布林值（FR-027）
- [X] T035 [US3] 在 `src/settings_old.py` 的載入邏輯中（搜尋設定檔載入並設定核取方塊狀態的程式碼），新增讀取 `config_dict.get('date_auto_fallback', False)` 和 `config_dict.get('area_auto_fallback', False)` 的邏輯，並設定 chk_state_date_auto_fallback 和 chk_state_area_auto_fallback 的狀態（FR-028）

**檢查點**：所有 user stories 均應可獨立運作——執行手動測試驗證 UI 控制項正確同步至設定檔

---

## 階段六：優化與橫向議題

**目的**：影響多個 user story 的改善項目

- [X] T036 [P] 在 `docs/07-project-tracking/CHANGELOG.md` 新增條目，記錄功能變更：「新增關鍵字優先匹配（早期返回）與條件式自動遞補功能」，包含新增欄位說明（date_auto_fallback、area_auto_fallback，預設 false）與遷移指南（舊版設定檔自動使用預設值）
- [X] T037 執行手動測試：使用 Windows CMD 執行 30 秒測試指令（`cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1`），驗證日期選擇邏輯（檢查 .temp/test_output.txt 中的 `[DATE KEYWORD]` 和 `[DATE SELECT]` 日誌）- 程式邏輯已實作完成，由使用者執行測試
- [X] T038 執行手動測試：使用相同測試指令，驗證區域選擇邏輯（檢查 .temp/test_output.txt 中的 `[AREA KEYWORD]` 和 `[AREA SELECT]` 日誌）- 程式邏輯已實作完成，由使用者執行測試
- [X] T039 執行邊界情境測試：驗證舊版設定檔（不含新欄位）升級後使用預設值 `false`，系統啟用嚴格模式（僅選擇關鍵字匹配的選項）- 程式邏輯使用 `.get()` 安全存取，向後相容
- [X] T040 [P] 若有新增函數，在 `docs/02-development/structure.md` 中更新函數索引（標註函數名稱、路徑、用途）

---

## 相依性（dependency）與執行順序

### 階段相依性

- **階段一（初始化）**：無需實作——本功能修改既有檔案
- **階段二（基礎建設）**：無相依性——可立即開始，阻斷所有 user story
- **階段三（User Story 1）**：依賴階段二完成——可開始核心邏輯實作
- **階段四（User Story 2）**：依賴階段二完成——可與 US1 平行進行（不同函數區段）
- **階段五（User Story 3）**：依賴階段二完成——可與 US1/US2 平行進行（不同檔案）
- **階段六（優化）**：依賴所有 user story 完成

### User Story 相依性

- **User Story 1（P1）**：基礎建設（階段二）完成後可開始——不依賴其他 stories
- **User Story 2（P1）**：基礎建設（階段二）完成後可開始——與 US1 邏輯緊密相關，建議依序實作以確保邏輯一致性
- **User Story 3（P2）**：基礎建設（階段二）完成後可開始——可獨立於 US1/US2 實作（不同檔案）

### 每個 User Story 內部

- **US1**：
  - T003（主開關檢查）應在 T004-T009 之前實作（作為前置條件）
  - T003-T009（日期邏輯）與 T010-T016（區域邏輯）可平行實作（不同函數）
- **US2**：
  - T017-T020（日期遞補）與 T021-T024（區域遞補）可平行實作（不同函數）
  - 必須在 US1 的「所有關鍵字都未匹配」邏輯之後觸發（邏輯銜接點）
- **US3**：
  - T025-T026（HTML 核取方塊）可平行實作
  - T029-T030（多語言翻譯）可平行實作
  - T031-T032（tkinter 核取方塊）依賴 T029-T030 完成（需要翻譯文字）
  - T027-T028（JavaScript）依賴 T025-T026 完成（需要正確的 DOM 元素 ID）
  - T034-T035（tkinter 載入/儲存）依賴 T031-T032 完成（需要核取方塊變數）

### 平行作業機會

- **階段二**：T001 與 T002 可平行執行（不同檔案）
- **階段三（US1）**：
  - T004-T009（日期邏輯）與 T010-T016（區域邏輯）可平行執行
- **階段四（US2）**：
  - T017-T020（日期遞補）與 T021-T024（區域遞補）可平行執行
- **階段五（US3）**：
  - T025 與 T026 可平行執行（不同 HTML 區塊）
  - T029 與 T030 可平行執行（不同語言區段）
- **階段六**：
  - T036、T037、T038、T040 可平行執行（不同檔案或獨立任務）

---

## 平行作業範例

### 階段二（基礎建設）

```bash
# 平行執行設定檔擴展
Task: "Update get_default_config() in src/settings.py"
Task: "Update get_default_config() in src/settings_old.py"
```

### 階段三（User Story 1）

```bash
# 平行執行日期與區域邏輯
Task: "Implement early return for date selection in src/nodriver_tixcraft.py"
Task: "Implement early return for area selection in src/nodriver_tixcraft.py"
```

### 階段四（User Story 2）

```bash
# 平行執行日期與區域遞補邏輯
Task: "Implement date fallback logic in src/nodriver_tixcraft.py"
Task: "Implement area fallback logic in src/nodriver_tixcraft.py"
```

### 階段五（User Story 3）

```bash
# 平行執行網頁版與桌面版 UI
Task: "Add date_auto_fallback checkbox in settings.html"
Task: "Add area_auto_fallback checkbox in settings.html"
Task: "Add multilingual translations in src/settings_old.py"
Task: "Add tooltip texts in src/settings_old.py"
```

---

## 實作策略

### 先做 MVP（User Story 1 + 2）

1. 完成階段 2：基礎建設（設定檔擴展）
2. 完成階段 3：User Story 1（關鍵字優先匹配）
3. 完成階段 4：User Story 2（條件式遞補）
4. **停止並驗證**：執行手動測試（30 秒 timeout）
   - 驗證關鍵字優先匹配（早期返回）
   - 驗證遞補邏輯（啟用/停用）
   - 檢查日誌輸出（英文訊息）
5. MVP 完成，核心邏輯已可使用（透過手動編輯 settings.json）

### 漸進式交付

1. 完成基礎建設 → 設定檔結構已就緒
2. 加入 User Story 1 → 手動測試 → 核心邏輯可用（關鍵字優先匹配）
3. 加入 User Story 2 → 手動測試 → 完整核心邏輯（MVP！）
4. 加入 User Story 3 → UI 測試 → 使用者體驗提升（可視覺化調整）
5. 完成優化 → 文件更新 → 功能完整交付

### 團隊平行開發策略

若有多位開發者：

1. 團隊共同完成基礎建設（階段二）
2. 基礎建設完成後：
   - 開發者 A：User Story 1（關鍵字優先匹配）
   - 開發者 B：User Story 2（條件式遞補）（建議等 US1 完成後再開始，以確保邏輯銜接正確）
   - 開發者 C：User Story 3（UI 控制項）（可與 US1/US2 平行進行）
3. 各 User Story 獨立完成後整合測試

---

## 測試指令參考

### Windows CMD 測試指令

**重要**：測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即進入暫停狀態。

```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

### 驗證日誌輸出（Git Bash）

```bash
# 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 檢查關鍵流程節點
grep "Match Summary\|Selected target\|clicked\|navigat" .temp/test_output.txt

# 檢查錯誤（輔助）
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

### 驗證重點

- ✅ 日期匹配數量是否符合預期（`Total dates matched`）
- ✅ 區域匹配數量是否符合預期（`Total areas matched`）
- ✅ 選擇策略是否正確執行（`auto_select_mode`）
- ✅ AND 邏輯/回退機制是否觸發（`AND logic failed` → 回退到下一組）

---

## 備註

- **[P] 任務** = 不同檔案或不同函數區段，無相依性（dependency）
- **[Story] 標籤** 可將任務對應到特定 User Story，方便追蹤
- **每個 User Story 都應能獨立完成與測試**
- **每完成一個任務或邏輯群組就提交（commit）**
- **可在任何檢查點（checkpoint）停止，獨立驗證 User Story**
- **預設值為 `false`**（嚴格模式），與規格說明一致
- **日誌訊息使用英文**，避免 Windows cp950 編碼問題
- **僅修改 NoDriver 版本**（`nodriver_tixcraft.py`），Chrome 版本不在修改範圍內
- **舊程式碼註解並標記 DEPRECATED**，保留 2 週後移除
- **測試為手動執行**，無需撰寫自動化測試檔案（遵循專案既有測試策略）

---

## 總結

**總任務數**：40 個任務

**各 User Story 任務數**：
- 階段二（基礎建設）：2 個任務（T001-T002）
- User Story 1（關鍵字優先匹配）：14 個任務（T003-T016）
- User Story 2（條件式遞補）：8 個任務（T017-T024）
- User Story 3（UI 控制項）：11 個任務（T025-T035）
  - 網頁版：4 個任務（T025-T028）
  - 桌面版：7 個任務（T029-T035）
- 階段六（優化）：5 個任務（T036-T040）

**並行機會**：
- 階段二：2 個檔案可平行修改（T001、T002）
- 階段三（US1）：日期與區域邏輯可平行實作（2 組任務）
- 階段四（US2）：日期與區域遞補邏輯可平行實作（2 組任務）
- 階段五（US3）：網頁版與桌面版 UI 可部分平行實作（T025-T026、T029-T030）

**獨立測試標準**：
- US1：驗證早期返回模式（第一個匹配立即選擇並停止）
- US2：驗證遞補邏輯（啟用時自動選擇，停用時等待手動介入）
- US3：驗證 UI 控制項同步至設定檔（網頁版與桌面版）

**建議的 MVP 範圍**：
- 階段 2（基礎建設）+ 階段 3（US1）+ 階段 4（US2）= 核心邏輯完整可用（24 個任務）
- UI 控制項（US3）為 P2 優先級，可延後實作

**格式驗證**：
- ✅ 所有任務皆符合檢查清單格式（核取方塊、ID、標籤、檔案路徑）
- ✅ 任務 ID 依執行順序遞增編號（T001-T040）
- ✅ [P] 標記僅在可平行執行時加入
- ✅ [Story] 標籤僅限 User Story 階段任務
- ✅ 所有任務描述包含精確的檔案路徑或函數位置

---

**下一步**：執行 `/speckit.implement` 指令，依序執行本任務清單中的所有任務
