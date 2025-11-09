# 任務：Cityline Platform NoDriver Migration

**輸入**：來自 `/specs/006-cityline-nodriver-migration/` 的設計文件
**前置需求**：plan.md（已完成）、spec.md（已完成）、research.md（Phase 0 產出）

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（如 US1、US2、US3）
- 描述中請包含精確的檔案路徑

## 路徑命名慣例
- **單一專案**：`src/`、`tests/` 於 repository 根目錄
- 本專案採用單一專案結構，主要實作在 `src/nodriver_tixcraft.py`

---

## 階段一：初始化（共用基礎設施）

**目的**：確認開發環境就緒，建立必要的文件結構

- [ ] T001 確認 NoDriver 函式庫已安裝且版本符合需求（參考 docs/06-api-reference/nodriver_api_guide.md）
- [ ] T002 [P] 確認 Chrome 瀏覽器版本 90+ 已安裝（NoDriver 相容性需求）
- [ ] T003 [P] 建立 specs/006-cityline-nodriver-migration/research.md 文件架構（Phase 0 準備）
- [ ] T004 [P] 建立 specs/006-cityline-nodriver-migration/data-model.md 文件架構（Phase 1 準備）
- [ ] T005 [P] 建立 specs/006-cityline-nodriver-migration/contracts/ 目錄（Phase 1 準備）

---

## 階段二：基礎研究（Phase 0 - Research）

**目的**：研究 Cityline 平台特性與技術方案，為實作提供依據

**⚠️ 關鍵**：本階段未完成前，不得開始 User Story 實作

- [ ] T006 研究 Cityline 平台 DOM 結構並記錄於 research.md：日期選擇器（button.date-time-position）、區域選擇器（div.form-check input[type=radio]）、票數選擇器（select.select-num）
- [ ] T007 研究 Cityline 平台是否使用 Shadow DOM，記錄選擇器策略於 research.md
- [ ] T008 研究 Cityline 登入流程與帳號填入方式，確認是否需要密碼輸入（記錄於 research.md）
- [ ] T009 研究 Cityline reCAPTCHA 出現時機與等待策略，確認等待時間設定（記錄於 research.md，建議 6 秒）
- [ ] T010 研究 Cityline 多分頁處理邏輯，參考 Chrome UC 版本實作（src/chrome_tixcraft.py 中的 cityline_close_second_tab）
- [ ] T011 研究條件回退機制實作方式，參考 TixCraft NoDriver 實作（docs/03-mechanisms/04-date-selection.md、05-area-selection.md）
- [ ] T012 研究 NoDriver API 使用策略：CDP 方法 vs JavaScript，確立 90% CDP 使用目標（記錄於 research.md）
- [ ] T013 完成 research.md 並驗證所有研究問題已解決

**檢查點**：研究階段完成 - 所有技術未知項目已解決，可開始設計階段

---

## 階段三：設計文件（Phase 1 - Design）

**目的**：產出資料模型、契約定義、快速開始指南

**⚠️ 關鍵**：本階段完成後，才能開始實作

- [ ] T014 [P] 撰寫 data-model.md：定義 Cityline 全域狀態變數（cityline_purchase_button_pressed、is_cityline_account_assigned、matched_blocks 資料結構、is_fallback_selection 標記）
- [ ] T015 [P] 撰寫 contracts/cityline-interface.md：定義所有 nodriver_cityline_* 函數簽章與參數規範
- [ ] T016 [P] 撰寫 contracts/fallback-mechanism.md：定義條件回退機制契約（date_auto_fallback、area_auto_fallback 行為規範）
- [ ] T017 [P] 撰寫 contracts/logging-format.md：定義日誌訊息格式規範（[DATE FALLBACK]、[AREA FALLBACK] 前綴標準）
- [ ] T018 [P] 撰寫 quickstart.md：提供 settings.json 配置範例與測試指令
- [ ] T019 驗證所有設計文件與 spec.md 一致性

**檢查點**：設計階段完成 - 所有設計文件已就緒，可開始實作

---

## 階段四：User Story 1 - NoDriver 完整票務流程實作 (Priority: P1) 🎯 MVP

**目標**：實作 Cityline 平台 NoDriver 版本的完整搶票流程，包含登入、日期選擇、區域選擇、票數選擇及提交，實現與 Chrome UC 版本的功能對等性

**獨立測試**：透過配置 settings.json 中的 webdriver_type: "nodriver" 並指定 Cityline 測試活動 URL，執行 30 秒快速測試，驗證從登入到座位選擇的完整流程

### User Story 1 實作

#### 主入口與基礎設施

- [ ] T020 [P] [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_main(tab, url, config_dict) 主入口函數，實現流程控制邏輯
- [ ] T021 [P] [US1] 在 src/nodriver_tixcraft.py 實作全域狀態變數初始化（cityline_purchase_button_pressed、is_cityline_account_assigned），確保狀態不污染

#### 登入功能

- [ ] T022 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_login(tab, config_dict) 函數：偵測登入頁面（cityline.com/Login.html）
- [ ] T023 [US1] 在 nodriver_cityline_login 中實作帳號自動填入邏輯：使用 NoDriver CDP 方法查詢帳號欄位並填入 cityline_account
- [ ] T024 [US1] 在 nodriver_cityline_login 中實作同意條款勾選：勾選同意條款核取方塊，排除「記得密碼」選項

#### 日期選擇功能（基礎實作，不含條件回退）

- [ ] T025 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_date_auto_select(tab, config_dict) 函數：查詢所有日期選項（button.date-time-position）
- [ ] T026 [US1] 在 nodriver_cityline_date_auto_select 中實作關鍵字匹配邏輯：呼叫 util.is_row_match_keyword 進行關鍵字過濾
- [ ] T027 [US1] 在 nodriver_cityline_date_auto_select 中實作 auto_select_mode 選擇策略：呼叫 util.get_target_item_from_matched_list 選擇目標日期
- [ ] T028 [US1] 在 nodriver_cityline_date_auto_select 中實作購買按鈕點擊：使用 NoDriver CDP 方法點擊選中的日期按鈕
- [ ] T029 [US1] 在 nodriver_cityline_date_auto_select 中實作 reCAPTCHA 等待：點擊後等待 6 秒

#### 區域選擇功能（基礎實作，不含條件回退）

- [ ] T030 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_area_auto_select(tab, config_dict) 函數：查詢所有區域選項（div.form-check input[type=radio]）
- [ ] T031 [US1] 在 nodriver_cityline_area_auto_select 中實作售罄過濾邏輯：檢查 span.price-limited > span[data-i18n*="soldout"] 屬性，排除售罄選項
- [ ] T032 [US1] 在 nodriver_cityline_area_auto_select 中實作關鍵字匹配邏輯：呼叫 util.is_row_match_keyword 進行區域過濾
- [ ] T033 [US1] 在 nodriver_cityline_area_auto_select 中實作 radio 按鈕勾選：使用 NoDriver CDP 方法勾選目標區域

#### 票數選擇與提交

- [ ] T034 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_ticket_number_auto_select(tab, config_dict) 函數：查詢票數下拉選單（select.select-num）
- [ ] T035 [US1] 在 nodriver_cityline_ticket_number_auto_select 中實作票數選擇：使用 NoDriver CDP 方法選擇 ticket_number 指定的數量
- [ ] T036 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_next_button_press(tab) 函數：查詢並點擊「下一步」按鈕
- [ ] T037 [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_purchase_button_press(tab, config_dict) 函數：查詢並點擊「購買」按鈕，設定 cityline_purchase_button_pressed 標記

#### 輔助功能

- [ ] T038 [P] [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_cookie_accept(tab) 函數：偵測並點擊 Cookie 同意按鈕（若存在）
- [ ] T039 [P] [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_clean_ads(tab) 函數：偵測並清除頁面廣告元素
- [ ] T040 [P] [US1] 在 src/nodriver_tixcraft.py 實作 nodriver_cityline_close_second_tab(tab) 函數：偵測多分頁情況，關閉舊分頁並切換至正確活動分頁（參考 Chrome UC 版本邏輯）

#### 自動重試與音效

- [ ] T041 [US1] 在 nodriver_cityline_date_auto_select 中實作自動重試邏輯：當日期列表為空且 auto_reload_coming_soon_page=true 時，呼叫 goEvent() 或重新整理頁面
- [ ] T042 [US1] 在 nodriver_cityline_main 中整合音效播放功能：成功進入座位選擇頁面時，根據 play_sound.ticket 設定呼叫 play_sound_while_ordering

#### 整合與測試

- [ ] T043 [US1] 在 nodriver_cityline_main 中整合所有子函數：按照流程順序呼叫登入 → 日期選擇 → 區域選擇 → 票數選擇 → 下一步 → 購買
- [ ] T044 [US1] 執行 30 秒快速測試（參考 CLAUDE.md 快速測試指令），驗證完整流程可執行
- [ ] T045 [US1] 檢查 .temp/test_output.txt 輸出，確認日誌訊息格式正確且無 emoji（NON-NEGOTIABLE 規範）

**檢查點**：此時 User Story 1 應可完全獨立運作並可測試 - NoDriver 基礎流程已完整實作

---

## 階段五：User Story 2 - 關鍵字匹配與條件回退策略 (Priority: P2)

**目標**：實作條件回退機制（date_auto_fallback、area_auto_fallback），讓使用者可在嚴格模式與自動回退模式間選擇

**獨立測試**：透過設定不同的關鍵字組合與 fallback 開關，驗證系統在各種情境下都能正確執行回退或嚴格模式邏輯

### User Story 2 實作

#### 日期選擇條件回退

- [ ] T046 [US2] 在 nodriver_cityline_date_auto_select 中實作 date_auto_fallback 檢查：當關鍵字匹配結果為空時，檢查 date_auto_fallback 設定
- [ ] T047 [US2] 在 nodriver_cityline_date_auto_select 中實作回退邏輯：若 date_auto_fallback=true，將 matched_blocks 重置為所有可用日期，記錄 [DATE FALLBACK] date_auto_fallback=true 日誌
- [ ] T048 [US2] 在 nodriver_cityline_date_auto_select 中實作嚴格模式邏輯：若 date_auto_fallback=false，記錄 [DATE FALLBACK] date_auto_fallback=false, fallback is disabled 日誌，根據 auto_reload_coming_soon_page 決定是否自動重新整理或等待手動介入

#### 區域選擇條件回退

- [ ] T049 [US2] 在 nodriver_cityline_area_auto_select 中實作 area_auto_fallback 檢查：當關鍵字匹配結果為空時，檢查 area_auto_fallback 設定
- [ ] T050 [US2] 在 nodriver_cityline_area_auto_select 中實作回退邏輯：若 area_auto_fallback=true，將 matched_blocks 重置為所有可用區域，記錄 [AREA FALLBACK] area_auto_fallback=true 日誌
- [ ] T051 [US2] 在 nodriver_cityline_area_auto_select 中實作嚴格模式邏輯：若 area_auto_fallback=false，記錄 [AREA FALLBACK] area_auto_fallback=false, fallback is disabled 日誌，返回 False 不選擇任何區域

#### 回退機制測試

- [ ] T052 [US2] 執行日期選擇回退測試：設定不存在的日期關鍵字 + date_auto_fallback=true，驗證系統回退到 auto_select_mode
- [ ] T053 [US2] 執行日期選擇嚴格模式測試：設定不存在的日期關鍵字 + date_auto_fallback=false，驗證系統不自動選擇或根據設定自動重新整理
- [ ] T054 [US2] 執行區域選擇回退測試：設定不存在的區域關鍵字 + area_auto_fallback=true，驗證系統回退到 auto_select_mode
- [ ] T055 [US2] 執行區域選擇嚴格模式測試：設定不存在的區域關鍵字 + area_auto_fallback=false，驗證系統返回失敗且不選擇任何區域
- [ ] T056 [US2] 檢查日誌訊息格式：確認 [DATE FALLBACK] 和 [AREA FALLBACK] 前綴使用正確，與 TixCraft 等其他平台保持一致

**檢查點**：此時 User Story 1 與 2 均應能獨立運作 - 條件回退機制已完整實作

---

## 階段六：User Story 3 - NoDriver CDP 優先實作策略 (Priority: P2)

**目標**：優化實作品質，確保 90% 以上的 DOM 操作使用 NoDriver 原生 CDP 方法，降低 JavaScript 使用比例

**獨立測試**：Code Review 檢查所有 Cityline NoDriver 函數，統計 CDP 方法與 JavaScript 使用比例

### User Story 3 實作

#### Code Review 與優化

- [ ] T057 [P] [US3] 檢查所有 nodriver_cityline_* 函數中的 DOM 查詢操作：確認是否優先使用 await tab.query_selector() 而非 JavaScript
- [ ] T058 [P] [US3] 檢查所有 nodriver_cityline_* 函數中的點擊操作：確認是否優先使用 await element.click() 而非 JavaScript click()
- [ ] T059 [P] [US3] 檢查所有 nodriver_cityline_* 函數中的輸入操作：確認是否優先使用 await element.send_keys() 而非 JavaScript value 賦值
- [ ] T060 [US3] 統計 CDP 方法與 JavaScript 使用比例：確保 CDP 使用比例 ≥ 90%，JavaScript 比例 ≤ 10%
- [ ] T061 [US3] 針對不符合 NoDriver First 原則的程式碼進行重構：將 JavaScript 操作改為 CDP 方法（若技術可行）

#### 異常處理優化

- [ ] T062 [US3] 為所有關鍵操作（點擊、輸入）加入異常處理：失敗時記錄錯誤日誌，嘗試 JavaScript 替代方案（NFR-012）
- [ ] T063 [US3] 為所有 query_selector 操作加入 timeout 機制：確保在 5 秒內完成或逾時（NFR-002）

**檢查點**：所有 user stories 均應可獨立運作 - 實作品質符合 NoDriver First 原則

---

## 階段七：優化與橫向議題

**目的**：影響多個 user story 的改善項目與文件同步

- [ ] T064 [P] 更新 docs/02-development/structure.md：新增 Cityline NoDriver 函數索引與說明
- [ ] T065 [P] 更新 README.md：更新 platform support table，標註 Cityline NoDriver 支援狀態
- [ ] T066 [P] 準備 CHANGELOG.md 草稿：記錄 Cityline NoDriver 遷移完成（待 PR merge 時正式提交）
- [ ] T067 執行功能對等性驗證：對照 Chrome UC 版本（src/chrome_tixcraft.py 中的 cityline_* 函數），確保所有功能在 NoDriver 版本皆可用
- [ ] T068 執行整合測試：使用真實 Cityline 活動 URL，完整測試從登入到座位選擇的流程，驗證成功率 >90%
- [ ] T069 執行憲章合規性檢查：對照 plan.md 中的 9 條憲章原則檢查清單，確認所有檢查點已通過
- [ ] T070 清理程式碼：移除不必要的註解、調整縮排、統一程式碼風格
- [ ] T071 執行最終測試：使用 30 秒快速測試與完整整合測試，確保所有功能正常

---

## 相依性（dependency）與執行順序

### 階段相依性

- **初始化（階段一）**：無相依性 - 可立即開始
- **基礎研究（階段二 - Phase 0）**：依賴初始化完成 - 阻斷所有後續階段
- **設計文件（階段三 - Phase 1）**：依賴基礎研究完成 - 阻斷所有 user story 實作
- **User Story 1（階段四）**：依賴設計文件完成 - 為 MVP 核心，必須優先完成
- **User Story 2（階段五）**：依賴 User Story 1 完成（需在 US1 的日期/區域選擇函數基礎上增加條件回退邏輯）
- **User Story 3（階段六）**：依賴 User Story 1 與 2 完成（需對現有實作進行 Code Review 與優化）
- **優化（階段七）**：依賴所有 user story 完成

### User Story 相依性

- **User Story 1（P1）**：設計文件（階段三）完成後可開始 - 不依賴其他 stories
- **User Story 2（P2）**：依賴 User Story 1 的日期/區域選擇函數完成 - 在 US1 基礎上擴展條件回退機制
- **User Story 3（P2）**：依賴 User Story 1 與 2 完成 - 需對現有實作進行審查與優化

### 每個 User Story 內部

#### User Story 1 內部順序
1. 主入口與基礎設施（T020-T021）- 可與其他子功能平行
2. 登入功能（T022-T024）- 獨立實作
3. 日期選擇功能（T025-T029）- 獨立實作
4. 區域選擇功能（T030-T033）- 獨立實作
5. 票數選擇與提交（T034-T037）- 獨立實作
6. 輔助功能（T038-T040）- 可平行實作
7. 自動重試與音效（T041-T042）- 依賴日期選擇與主入口完成
8. 整合與測試（T043-T045）- 依賴所有子功能完成

#### User Story 2 內部順序
1. 日期選擇條件回退（T046-T048）- 依賴 US1 的 T025-T029
2. 區域選擇條件回退（T049-T051）- 依賴 US1 的 T030-T033
3. 回退機制測試（T052-T056）- 依賴 T046-T051 完成

#### User Story 3 內部順序
1. Code Review（T057-T061）- 可平行執行
2. 異常處理優化（T062-T063）- 依賴 Code Review 完成

### 平行作業機會

- 階段一（初始化）：T002、T003、T004、T005 可平行執行
- 階段三（設計文件）：T014、T015、T016、T017、T018 可平行執行
- User Story 1：T021、T038、T039、T040 可平行實作（不同功能模組）
- User Story 3：T057、T058、T059 可平行執行（Code Review 可由不同人員負責不同函數）
- 階段七（優化）：T064、T065、T066 可平行執行（不同文件）

---

## 平行作業範例：User Story 1

```bash
# Phase 1: 平行實作多個獨立子功能
Task T021: "在 src/nodriver_tixcraft.py 實作全域狀態變數初始化"
Task T038: "在 src/nodriver_tixcraft.py 實作 nodriver_cityline_cookie_accept(tab) 函數"
Task T039: "在 src/nodriver_tixcraft.py 實作 nodriver_cityline_clean_ads(tab) 函數"
Task T040: "在 src/nodriver_tixcraft.py 實作 nodriver_cityline_close_second_tab(tab) 函數"

# Phase 2: 順序實作核心流程（有相依性）
Task T022: "在 src/nodriver_tixcraft.py 實作 nodriver_cityline_login(tab, config_dict) 函數"
→ Task T023: "在 nodriver_cityline_login 中實作帳號自動填入邏輯"
→ Task T024: "在 nodriver_cityline_login 中實作同意條款勾選"

# Phase 3: 平行實作日期與區域選擇（不同函數）
Task T025-T029: "實作日期選擇功能"
Task T030-T033: "實作區域選擇功能"
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1）

1. 完成階段 1：初始化（T001-T005）
2. 完成階段 2：基礎研究 Phase 0（T006-T013）- 關鍵，會阻擋所有後續工作
3. 完成階段 3：設計文件 Phase 1（T014-T019）- 關鍵，會阻擋 User Story 實作
4. 完成階段 4：User Story 1（T020-T045）
5. **停止並驗證**：執行 30 秒快速測試與整合測試，驗證 NoDriver 基礎流程可用
6. 若已準備好則可進行初步展示或內部測試

### 漸進式交付

1. 完成 Setup + 基礎研究 + 設計文件 → 設計基礎已就緒
2. 加入 User Story 1 → 獨立測試 → 內部驗證（MVP！）
3. 加入 User Story 2 → 獨立測試 → 驗證條件回退機制
4. 加入 User Story 3 → Code Review → 確保實作品質符合 NoDriver First 原則
5. 完成階段七優化 → 文件同步 → PR 準備就緒
6. 每個 User Story 都能在不破壞前一個 User Story 的情況下增加價值

### 團隊平行開發策略

若有多位開發者：

1. 團隊共同完成 Setup + 基礎研究 + 設計文件（T001-T019）
2. 設計文件完成後：
   - 開發者 A：User Story 1 核心流程（登入、日期、區域選擇）
   - 開發者 B：User Story 1 輔助功能（多分頁、廣告清除、Cookie）
   - 開發者 C：準備測試環境與測試腳本
3. User Story 1 完成後：
   - 開發者 A：User Story 2（條件回退機制）
   - 開發者 B：User Story 3（Code Review 與優化）
   - 開發者 C：整合測試與功能對等性驗證

---

## 備註

- [P] 任務 = 不同檔案或不同功能模組，無相依性（dependency）
- [Story] 標籤可將任務對應到特定 User Story，方便追蹤進度
- 每個 User Story 都應能獨立完成與測試
- 每完成一個邏輯群組就提交（commit），遵循 Conventional Commits 規範
- 可在任何檢查點（checkpoint）停止，獨立驗證 User Story
- 請避免：任務描述模糊、同檔案衝突、跨 User Story 的相依性（dependency）導致無法獨立測試
- **NON-NEGOTIABLE 規範**：所有 `.py` 檔案中禁止使用 emoji，避免 Windows cp950 編碼錯誤
- 優先使用 NoDriver 原生 CDP 方法，確保 CDP 使用比例 ≥ 90%
- 遵循專案憲章 9 大核心原則（詳見 plan.md）

---

**任務總數**：71 個任務
**MVP 範圍**：T001-T045（階段一至階段四，User Story 1）
**關鍵里程碑**：
- T013：基礎研究完成（Phase 0）
- T019：設計文件完成（Phase 1）
- T045：User Story 1 完成（MVP）
- T056：User Story 2 完成（條件回退機制）
- T063：User Story 3 完成（實作品質優化）
- T071：專案完成（所有功能與文件就緒）

**建議執行順序**：階段一 → 階段二 → 階段三 → 階段四（MVP） → 階段五 → 階段六 → 階段七
