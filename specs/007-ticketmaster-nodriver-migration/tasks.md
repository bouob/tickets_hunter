---
description: "Ticketmaster.com NoDriver 平台遷移實作任務清單"
---

# 任務：Ticketmaster.com NoDriver 平台遷移

**輸入**：來自 `/specs/007-ticketmaster-nodriver-migration/` 的設計文件
**前置需求**：plan.md、spec.md、data-model.md、contracts/function-interface.md、quickstart.md、research.md

**測試**：本功能採用手動測試驗證（需訪問真實 Ticketmaster.com 頁面），無自動化測試任務

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（如 US1、US2、US3、US4）
- 描述中請包含精確的檔案路徑

## 路徑命名慣例
- 單一專案結構：`src/`、`docs/` 於 repository 根目錄
- 主要實作檔案：`src/nodriver_tixcraft.py`（與現有 Tixcraft 家族平台共享）

---

## 階段一：初始化（共用基礎設施）

**目的**：專案結構驗證與相依性檢查

- [ ] T001 驗證專案結構符合 plan.md 定義（確認 src/、docs/、tests/ 存在）
- [ ] T002 驗證 Python 環境 >=3.8 且 NoDriver 套件已安裝（執行 `python -c "import nodriver; print(nodriver.__version__)"`）
- [ ] T003 [P] 驗證 settings.json schema 包含 Ticketmaster 所需欄位（date_auto_select, area_auto_select, ticket_number）

**檢查點**：環境就緒，可開始基礎建設

---

## 階段二：基礎建設（阻斷性前置需求）

**目的**：所有 user story 開始前「必須」完成的核心基礎設施

**⚠️ 關鍵**：本階段未完成前，不得開始任何 user story 實作

- [ ] T004 在 src/nodriver_tixcraft.py 中實作 `ticketmaster_parse_zone_info()` 輔助函數（解析 zone_info JSON）
- [ ] T005 [P] 在 src/nodriver_tixcraft.py 中實作 `get_ticketmaster_target_area()` 純函數（區域匹配邏輯）
- [ ] T006 [P] 在 src/nodriver_tixcraft.py 中實作 `ticketmaster_get_ticketPriceList()` 輔助函數（等待頁面載入並取得票價表）
- [ ] T007 [P] 在 src/nodriver_tixcraft.py 中實作 `check_checkbox()` 輔助函數（勾選同意條款，支援重試）
- [ ] T008 在 src/nodriver_tixcraft.py 的主流程中新增 Ticketmaster domain_name 判斷邏輯（檢查 URL 包含 'ticketmaster'）

**檢查點**：基礎輔助函數就緒——user story 實作可開始平行進行

---

## 階段三：User Story 1 - 自動選擇演出日期 (Priority: P1) 🎯 MVP

**目標**：在 Ticketmaster.com 的活動頁面自動根據設定的關鍵字識別並點選符合條件的演出場次

**獨立測試**：設定日期關鍵字（如 "2025-12-25"），訪問 Ticketmaster.com 的藝人活動頁面，驗證系統能自動找到並點擊符合條件的演出日期

**對應需求**：FR-001, FR-002, FR-003

### User Story 1 實作

- [ ] T009 [US1] 在 src/nodriver_tixcraft.py 實作 `ticketmaster_date_auto_select()` 函數（核心日期選擇邏輯）
  - 實作 CSS 選擇器查詢：`#list-view > div > div.event-listing > div.accordion-wrapper > div`
  - 實作日期區塊過濾邏輯（必須包含 "See Tickets"）
  - 實作售罄場次跳過邏輯（檢查 "Sold out", "No tickets available" 關鍵字）
  - 實作日期關鍵字匹配（使用 util.get_matched_blocks_by_keyword()）
  - 實作目標日期選擇（使用 util.get_target_item_from_matched_list()）
  - 實作 "See Tickets" 連結點擊與分頁管理
  - 實作 auto_reload_coming_soon_page 邏輯（若無匹配則重新整理頁面）
  - 實作 verbose 日誌輸出（匹配摘要、選擇目標）

- [ ] T010 [US1] 在 src/nodriver_tixcraft.py 的 `nodriver_tixcraft_main()` 主流程中整合日期選擇功能
  - 在 URL 路徑判斷中新增 `/artist/` 分支
  - 檢查 domain_name 包含 'ticketmaster'
  - 調用 `ticketmaster_date_auto_select(driver, tab, config)`

- [ ] T011 [US1] 建立手動測試流程文件於 .temp/test_ticketmaster_date.md（記錄測試步驟、預期結果、驗證指令）

**檢查點**：此時 User Story 1 應可完全獨立運作並可手動測試

**手動測試指令**：
```bash
# 設定 settings.json 的 homepage 為 https://www.ticketmaster.com/artist/[artist_id]
# 設定 date_keyword 為測試日期關鍵字
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
grep "\[DATE SELECT\]" .temp/test_output.txt
```

---

## 階段四：User Story 2 - 自動選擇座位區域 (Priority: P1)

**目標**：在座位選擇頁面根據區域關鍵字自動識別並點選符合條件的座位區塊

**獨立測試**：設定區域關鍵字（如 "VIP"），訪問 Ticketmaster 的 `/ticket/area/` 頁面，驗證系統能解析 zone_info JSON 並自動選擇符合條件的座位區域

**對應需求**：FR-004, FR-005, FR-006

### User Story 2 實作

- [ ] T012 [US2] 在 src/nodriver_tixcraft.py 實作 `ticketmaster_area_auto_select()` 函數（核心區域選擇邏輯）
  - 實作 config 驗證（檢查 area_auto_select.enable, area_keyword）
  - 實作 area_keyword JSON 陣列解析（支援多組關鍵字）
  - 實作多組關鍵字回退機制（遍歷每組關鍵字，直到找到匹配）
  - 實作調用 `get_ticketmaster_target_area()` 取得匹配區域列表
  - 實作目標區域選擇（使用 util.get_target_item_from_matched_list()）
  - 實作 JavaScript 執行：`areaTicket("<zone_id>", "map");`
  - 實作 verbose 日誌輸出（區域匹配摘要、選擇目標、JavaScript 執行結果）

- [ ] T013 [US2] 在 src/nodriver_tixcraft.py 的 `nodriver_tixcraft_main()` 主流程中整合區域選擇功能
  - 在 URL 路徑判斷中新增 `/ticket/area/` 分支
  - 檢查 domain_name 包含 'ticketmaster'
  - 調用 `ticketmaster_parse_zone_info(driver, tab, config)` 取得 zone_info
  - 若 zone_info 不為 None，調用 `ticketmaster_area_auto_select(driver, tab, config, zone_info)`

- [ ] T014 [US2] 建立手動測試流程文件於 .temp/test_ticketmaster_area.md（記錄測試步驟、預期結果、驗證指令）

**檢查點**：此時 User Story 1 與 2 均應能獨立運作（可分別測試日期選擇與區域選擇）

**手動測試指令**：
```bash
# 設定 settings.json 的 homepage 為 https://www.ticketmaster.com/ticket/area/[event_id]
# 設定 area_keyword 為測試區域關鍵字（JSON 陣列格式）
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
grep "\[AREA SELECT\]" .temp/test_output.txt
```

---

## 階段五：User Story 3 - 票數設定與促銷碼填寫 (Priority: P2)

**目標**：在票務頁面自動設定正確的票數，並在需要時填寫促銷碼

**獨立測試**：設定 ticket_number 為特定數字（如 2 張），訪問 Ticketmaster 的票務頁面，驗證系統能找到 ticketPriceList 並自動設定票數

**對應需求**：FR-007, FR-008, FR-009, FR-010

### User Story 3 實作

- [ ] T015 [US3] 在 src/nodriver_tixcraft.py 實作 `ticketmaster_assign_ticket_number()` 函數（票數設定邏輯）
  - 實作調用 `ticketmaster_get_ticketPriceList(tab, config)` 等待頁面載入
  - 實作在 ticketPriceList 表格中查詢 select 元素
  - 實作使用 JavaScript 設定 select 值（匹配 ticket_number 文字）
  - 實作觸發 change 事件（`dispatchEvent(new Event('change', { bubbles: true }))`）
  - 實作查詢並點擊 `#autoMode` 按鈕
  - 實作 verbose 日誌輸出（找到表格、設定票數、點擊按鈕）

- [ ] T016 [P] [US3] 在 src/nodriver_tixcraft.py 實作 `ticketmaster_promo()` 函數（促銷碼填寫邏輯）
  - 實作調用現有的 `tixcraft_input_check_code(driver, tab, config, "#promoBox", promo_code_fail_list)` 函數
  - 實作返回更新後的 fail_list

- [ ] T017 [US3] 在 src/nodriver_tixcraft.py 的 `nodriver_tixcraft_main()` 主流程中整合票數設定與促銷碼功能
  - 在適當的 URL 路徑判斷分支（票務頁面）中檢查 domain_name 包含 'ticketmaster'
  - 調用 `ticketmaster_assign_ticket_number(driver, tab, config)`
  - 若頁面包含 `#promoBox`，調用 `ticketmaster_promo(driver, tab, config, promo_code_fail_list)`

- [ ] T018 [US3] 建立手動測試流程文件於 .temp/test_ticketmaster_ticket.md（記錄測試步驟、預期結果、驗證指令）

**檢查點**：此時 User Story 1、2、3 均應能獨立運作或整合測試

**手動測試指令**：
```bash
# 設定 settings.json 的 ticket_number 為測試票數
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
grep "\[TICKET NUMBER\]" .temp/test_output.txt
```

---

## 階段六：User Story 4 - 驗證碼自動處理 (Priority: P3)

**目標**：在驗證碼頁面自動辨識圖形驗證碼或處理其他驗證機制

**獨立測試**：訪問 `/ticket/check-captcha/` 頁面，驗證系統能自動勾選 TicketForm_agree 條款，並在啟用 OCR 的情況下嘗試辨識驗證碼

**對應需求**：FR-011

### User Story 4 實作

- [ ] T019 [US4] 在 src/nodriver_tixcraft.py 實作 `ticketmaster_captcha()` 函數（驗證碼處理邏輯）
  - 實作調用 `check_checkbox(tab, '#TicketForm_agree', max_retries=2)` 勾選同意條款
  - 實作檢查 config["ocr_captcha"]["enable"]
  - 若 OCR 未啟用：調用 `tixcraft_keyin_captcha_code(tab)` 聚焦驗證碼輸入框，返回 False
  - 若 OCR 啟用：循環最多 99 次調用 `tixcraft_auto_ocr(driver, tab, config, ocr, captcha_browser)`，檢查表單提交或 URL 改變，返回 True
  - 實作 verbose 日誌輸出（勾選條款、OCR 辨識狀態）

- [ ] T020 [US4] 在 src/nodriver_tixcraft.py 的 `nodriver_tixcraft_main()` 主流程中整合驗證碼功能
  - 在 URL 路徑判斷中新增 `/ticket/check-captcha/` 分支
  - 檢查 domain_name 包含 'ticketmaster'
  - 調用 `ticketmaster_captcha(driver, tab, config, ocr, captcha_browser)`

- [ ] T021 [US4] 建立手動測試流程文件於 .temp/test_ticketmaster_captcha.md（記錄測試步驟、預期結果、驗證指令）

**檢查點**：所有 user stories 均應可獨立運作或整合測試

**手動測試指令**：
```bash
# 設定 settings.json 的 ocr_captcha.enable 為 false（手動輸入測試）
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
grep "\[CAPTCHA\]" .temp/test_output.txt
```

---

## 階段七：優化與橫向議題

**目的**：影響多個 user story 的改善項目與文件更新

- [ ] T022 [P] 更新 docs/02-development/structure.md 新增 Ticketmaster 函數索引（8 個核心函數的檔案位置與說明）
- [ ] T023 [P] 更新 README.md 中的 Ticketmaster.com 支援狀態（將 NoDriver 支援標記為完成）
- [ ] T024 [P] 更新 docs/10-project-tracking/accept_changelog.md 記錄本次遷移的變更（遵循憲法第 VIII 條）
- [ ] T025 檢查所有 Ticketmaster 函數的 domain_name 判斷邏輯（確保 100% 隔離，不影響其他 Tixcraft 家族平台）
- [ ] T026 執行跨平台迴歸測試（手動測試 tixcraft.com, teamear.tixcraft.com, kktix.com 等確保無干擾）
- [ ] T027 執行 quickstart.md 中的完整測試流程驗證（日期選擇 → 區域選擇 → 票數設定 → 驗證碼）
- [ ] T028 [P] 記錄常見問題與除錯案例於 docs/08-troubleshooting/ticketmaster_troubleshooting.md

**檢查點**：所有功能完成、文件同步、跨平台隔離驗證通過

---

## 相依性（dependency）與執行順序

### 階段相依性

- **初始化（階段一）**：無相依性——可立即開始
- **基礎建設（階段二）**：依賴初始化完成——阻斷所有 user story
- **User Stories（階段三至六）**：皆依賴基礎建設完成
  - User Story 1 (P1) 可優先進行（MVP）
  - User Story 2 (P1) 可與 US1 整合測試（日期選擇後自動進入區域選擇）
  - User Story 3 (P2) 可與 US1/US2 整合測試（完整流程：日期 → 區域 → 票數）
  - User Story 4 (P3) 為輔助功能，可獨立測試
- **優化（階段七）**：依賴所有目標 user story 完成

### User Story 相依性

- **User Story 1（P1 - 日期選擇）**：基礎建設（階段二）完成後可開始——不依賴其他 stories
- **User Story 2（P1 - 區域選擇）**：依賴 T004（zone_info 解析）與 T005（區域匹配邏輯）——可與 US1 整合但應可獨立測試
- **User Story 3（P2 - 票數設定）**：依賴 T006（ticketPriceList 取得）——可與 US1/US2 整合但應可獨立測試
- **User Story 4（P3 - 驗證碼）**：依賴 T007（check_checkbox 輔助函數）——可獨立測試

### 每個 User Story 內部

- **US1**：T009（核心函數）→ T010（主流程整合）→ T011（測試文件）
- **US2**：T012（核心函數）→ T013（主流程整合）→ T014（測試文件）
- **US3**：T015 與 T016 可平行執行（不同函數）→ T017（主流程整合）→ T018（測試文件）
- **US4**：T019（核心函數）→ T020（主流程整合）→ T021（測試文件）

### 平行作業機會

- **階段一**：T001, T002, T003 可平行執行（不同驗證任務）
- **階段二**：T005（純函數）, T006, T007 可平行執行（獨立的輔助函數）
- **階段三至六**：若團隊人力允許，US1/US2/US3/US4 可平行開發（不同函數）
- **階段七**：T022, T023, T024, T028 可平行執行（不同文件更新）

---

## 平行作業範例：基礎建設階段（階段二）

```bash
# Launch all foundational helper functions together:
Task: "Implement ticketmaster_parse_zone_info() in src/nodriver_tixcraft.py"
Task: "Implement get_ticketmaster_target_area() in src/nodriver_tixcraft.py"
Task: "Implement ticketmaster_get_ticketPriceList() in src/nodriver_tixcraft.py"
Task: "Implement check_checkbox() in src/nodriver_tixcraft.py"
```

## 平行作業範例：User Story 3 票數與促銷碼

```bash
# Launch ticket number and promo code functions together:
Task: "Implement ticketmaster_assign_ticket_number() in src/nodriver_tixcraft.py"
Task: "Implement ticketmaster_promo() in src/nodriver_tixcraft.py"
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1 日期選擇）

1. 完成階段 1：Setup（T001-T003）
2. 完成階段 2：基礎建設（T004-T008）
3. 完成階段 3：User Story 1（T009-T011）
4. **停止並驗證**：獨立測試日期選擇功能
5. 若已準備好則部署／展示

**MVP 驗證指令**：
```bash
# 設定 date_keyword 為測試關鍵字
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
grep "\[DATE SELECT\] Match Summary" .temp/test_output.txt
```

### 漸進式交付

1. 完成 Setup + 基礎建設 → 基礎已就緒
2. 加入 User Story 1（日期選擇）→ 獨立測試 → 部署（MVP！）
3. 加入 User Story 2（區域選擇）→ 整合測試（日期 → 區域）→ 部署
4. 加入 User Story 3（票數設定）→ 整合測試（日期 → 區域 → 票數）→ 部署
5. 加入 User Story 4（驗證碼）→ 整合測試（完整流程）→ 部署
6. 每個 User Story 都能在不破壞前一個 User Story 的情況下增加價值

### 團隊平行開發策略

若有多位開發者：

1. 團隊共同完成 Setup + 基礎建設（T001-T008）
2. 基礎建設完成後：
   - 開發者 A：User Story 1（日期選擇）
   - 開發者 B：User Story 2（區域選擇）
   - 開發者 C：User Story 3（票數設定）+ User Story 4（驗證碼）
3. 各 User Story 可獨立完成並整合

---

## 備註

- **[P] 任務**：不同檔案或不同函數，無相依性（dependency），可平行執行
- **[Story] 標籤**：可將任務對應到特定 User Story，方便追蹤
- **手動測試**：每個 User Story 都應能透過 quickstart.md 中的指令獨立測試
- **domain_name 隔離**：所有 Ticketmaster 特定邏輯必須檢查 domain_name 包含 'ticketmaster'
- **憲法遵循**：
  - 第 I 條（NoDriver First）：本功能僅實作 NoDriver 版本
  - 第 IV 條（單一職責）：每個函數職責明確，可組合使用
  - 第 V 條（設定驅動）：所有行為由 settings.json 控制
  - 第 VIII 條（文件同步）：實作後必須更新 structure.md 與 README.md
- **提交策略**：每完成一個 User Story 就提交（使用 `/gsave` 指令）
- **錯誤處理**：遵循 FR-015 提供詳細的除錯日誌（verbose 模式）
- **跨平台安全**：執行 T026 跨平台迴歸測試確保 100% 隔離（SC-004）

---

## 成功標準驗證（對應 spec.md）

### SC-001：日期匹配成功率 ≥90%
**驗證方式**：使用至少 10 個不同演出的測試資料集，檢查 `[DATE SELECT] Match Summary` 日誌

### SC-002：zone_info JSON 解析成功率 ≥95%
**驗證方式**：測試包含換行符和額外逗號的 zone_info，檢查 `[AREA SELECT] Successfully parsed zone_info` 日誌

### SC-003：整體流程耗時 ≤ Chrome Driver 版本的 110%
**驗證方式**：記錄從進入活動頁面到完成票數設定的總耗時，與 Chrome 版本對比

### SC-004：跨平台隔離度 100%
**驗證方式**：執行 T026 跨平台迴歸測試，確保 tixcraft.com 等平台不觸發 Ticketmaster 邏輯

### SC-005：除錯日誌可理解性協助率 ≥85%
**驗證方式**：啟用 verbose 模式，檢查每個關鍵決策點的日誌輸出是否清晰

---

**總任務數**：28 個任務
- 階段一（Setup）：3 個任務
- 階段二（基礎建設）：5 個任務
- 階段三（US1 日期選擇）：3 個任務
- 階段四（US2 區域選擇）：3 個任務
- 階段五（US3 票數設定）：4 個任務
- 階段六（US4 驗證碼）：3 個任務
- 階段七（優化與文件）：7 個任務

**並行機會**：
- 基礎建設：4 個任務可平行（T005, T006, T007, T003）
- User Story 實作：4 個 story 可平行（若團隊人力允許）
- 文件更新：4 個任務可平行（T022, T023, T024, T028）

**建議 MVP 範圍**：階段一 + 階段二 + 階段三（共 11 個任務）

**預估完成時間**：
- MVP（US1 日期選擇）：1-2 個工作日
- 完整功能（US1-US4）：3-5 個工作日
- 包含文件與測試：5-7 個工作日
