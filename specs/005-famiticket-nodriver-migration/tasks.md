# 任務：FamiTicket NoDriver 遷移

**輸入**：來自 `/specs/005-famiticket-nodriver-migration/` 的設計文件
**前置需求**：plan.md、spec.md、research.md、data-model.md、contracts/function-signatures.md、contracts/config-schema.md

**測試**：本專案採用「真實頁面測試」策略（遵循憲法第 VI 條），每個 User Story 完成後必須在真實 FamiTicket 頁面測試。

**組織方式**：任務依 User Story 分組（P1: US1-US4, P2: US5），確保每個 User Story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 User Story（如 US1、US2、US3）
- 描述中包含精確的檔案路徑

## 路徑命名慣例
- **單一專案**（本專案結構）：`src/nodriver_tixcraft.py`（主要修改目標）
- **工具函數重用**：`src/util.py`（format_keyword_string、fill_common_verify_form 等）
- **設定檔**：`src/settings.json`（無需修改，測試用）
- **測試輸出**：`.temp/test_output.txt`（背景測試輸出）

---

## 階段一：初始化（共用基礎設施）

**目的**：準備工具函數與驗證現有程式碼結構

**檢查點**：工具函數就緒，可開始 User Story 實作

- [ ] T001 [P] 新增 `nodriver_click_element()` 工具函數於 `src/nodriver_tixcraft.py`（CDP 點擊優先 + element.click() 備用）
- [ ] T002 [P] 新增 `nodriver_search_element()` 工具函數於 `src/nodriver_tixcraft.py`（Pierce 方法元素搜尋）
- [ ] T003 驗證現有工具函數可用性：確認 `src/util.py` 中的 `format_keyword_string()`、`guess_tixcraft_question()`、`fill_common_verify_form()` 可正常呼叫

---

## 階段二：基礎建設（阻斷性前置需求）

**目的**：無（本專案無阻斷性基礎建設，直接進入 User Story 實作）

**注意**：FamiTicket 遷移完全重用現有 NoDriver 基礎設施（已存在於 `src/nodriver_tixcraft.py` 的 TixCraft/KKTIX 實作中），無需額外基礎建設。

**檢查點**：階段一完成後，所有 User Story 可開始平行實作

---

## 階段三：User Story 1 - 使用帳號密碼登入 FamiTicket (Priority: P1) 🎯 MVP

**目標**：實作 FamiTicket 帳號密碼登入功能，支援自動填寫表單與提交（FR-001 至 FR-009）

**獨立測試**：
1. 修改 `src/settings.json` 設定 `webdriver_type: "nodriver"` 與 `advanced.fami_account`、`advanced.fami_password_plaintext`
2. 清空 cookies 確保未登入狀態
3. 執行 `python -u src/nodriver_tixcraft.py --input src/settings.json`
4. 觀察自動登入流程（偵測登入頁面 → 填寫帳號密碼 → 提交表單 → 登入成功）
5. 驗證成功標準：SC-001（95% 登入成功率，< 5 秒）

### User Story 1 實作

- [ ] T004 [US1] 實作 `nodriver_fami_login()` 於 `src/nodriver_tixcraft.py`：偵測登入頁面（URL 包含 `/Home/User/SignIn`）、填寫帳號（CSS: `#usr_act`）與密碼（CSS: `#usr_pwd`）、提交表單（參考 Chrome 版本 line 6302）
- [ ] T005 [US1] 實作 `nodriver_fami_activity()` 於 `src/nodriver_tixcraft.py`：偵測活動頁面（URL 包含 `/Home/Activity/Info/`）、點擊「立即購買」按鈕（CSS: `button.btn-buy`，參考 Chrome 版本 line 3336）
- [ ] T006 [US1] 實作 `nodriver_fami_home_auto_select()` 於 `src/nodriver_tixcraft.py`：處理首頁入口（URL: `/Home/Activity`），參考 Chrome 版本 `fami_home()` 邏輯

**檢查點**：執行 30 秒背景測試 + 真實 FamiTicket 登入頁面測試，驗證登入流程完整可用

---

## 階段四：User Story 2 - 根據日期關鍵字自動選擇日期 (Priority: P1)

**目標**：實作日期關鍵字匹配（OR 邏輯）與自動選擇功能（FR-010 至 FR-015）

**獨立測試**：
1. 修改 `src/settings.json` 設定 `date_auto_select.date_keyword: "2025-11-10,週六"`
2. 執行程式並觀察日期選擇流程
3. 檢查 `.temp/test_output.txt` 中的 `[DATE KEYWORD]` 與 `[DATE SELECT]` 訊息
4. 驗證關鍵字匹配邏輯（包含「2025-11-10」或「週六」的日期被選中）
5. 驗證回退機制（若無匹配 → 使用 `auto_select_mode` 選擇第一個可用日期）
6. 驗證成功標準：SC-002（90% 日期列表掃描成功率，< 2 秒）

### User Story 2 實作

- [ ] T007 [US2] 實作 `nodriver_fami_date_auto_select()` 於 `src/nodriver_tixcraft.py`（不含自動補票）：掃描日期列表（CSS: `table.session__list > tbody > tr`）、提取日期文字/區域文字/購買按鈕、關鍵字匹配（OR 邏輯，使用 `format_keyword_string()`）、回退至 `auto_select_mode`（參考 Chrome 版本 line 3380）

**檢查點**：執行 30 秒背景測試（驗證日期匹配數量 `Total dates matched`）+ 真實 FamiTicket 日期選擇頁面測試

---

## 階段五：User Story 3 - 根據區域關鍵字自動選擇區域 (Priority: P1)

**目標**：實作區域關鍵字匹配（AND/OR 邏輯）與自動選擇功能（FR-016 至 FR-021）

**獨立測試**：
1. 修改 `src/settings.json` 設定 `area_auto_select.area_keyword_and: [["搖滾區", "不含柱"], ["VIP", "前排"]]`
2. 執行程式並觀察區域選擇流程
3. 檢查 `.temp/test_output.txt` 中的 `[AREA KEYWORD]` 與 `[AREA SELECT]` 訊息
4. 驗證 AND 邏輯（選擇同時包含「搖滾區」**且**「不含柱」的區域）
5. 驗證回退機制（第一組無匹配 → 嘗試下一組 → 若所有組都無匹配 → 使用 `area_keyword` OR 邏輯 → 最終回退至 `auto_select_mode`）
6. 驗證已停用區域過濾（class 包含 `"area disabled"` 的區域被跳過）
7. 驗證成功標準：SC-003（90% 區域列表掃描成功率，< 2 秒）

### User Story 3 實作

- [ ] T008 [US3] 實作 `nodriver_fami_area_auto_select()` 於 `src/nodriver_tixcraft.py`：掃描區域列表（CSS: `div > a.area`）、過濾已停用區域（class 包含 `"area disabled"`）、AND 邏輯匹配（`area_keyword_and`）、OR 邏輯匹配（`area_keyword`）、回退至 `auto_select_mode`（參考 Chrome 版本 line 3514）

**檢查點**：執行 30 秒背景測試（驗證區域匹配數量 `Total areas matched` 與 AND 邏輯正確性）+ 真實 FamiTicket 區域選擇頁面測試

---

## 階段六：User Story 4 - 自動處理驗證問題 (Priority: P1)

**目標**：實作驗證問題偵測、自動填寫與猜測功能（FR-022 至 FR-025）

**獨立測試**：
1. 修改 `src/settings.json` 設定 `advanced.auto_guess_options: true`
2. 執行程式並等待遇到驗證問題頁面
3. 檢查 `.temp/test_output.txt` 中的 `verify` 與 `question` 相關訊息
4. 驗證偵測驗證輸入框（CSS: `#verifyPrefAnswer`）
5. 驗證呼叫 `fill_common_verify_form()` 工具函數
6. 驗證自動猜測答案（`auto_guess_options: true` 時）
7. 驗證追蹤錯誤答案（`fail_list` 正確更新）
8. 驗證成功標準：SC-004（95% 驗證問題處理成功率）

### User Story 4 實作

- [ ] T009 [US4] 實作 `nodriver_fami_verify()` 於 `src/nodriver_tixcraft.py`：偵測驗證輸入框（CSS: `#verifyPrefAnswer`）、呼叫 `fill_common_verify_form()` 工具函數（重用 `src/util.py`）、支援自動猜測（`auto_guess_options: true`）、追蹤錯誤答案（`fail_list`，參考 Chrome 版本 line 3298）

**檢查點**：真實 FamiTicket 驗證問題測試（遇到驗證頁面時）

---

## 階段七：整合所有 P1 User Stories（完整購票流程）

**目標**：整合 US1-US4 成為完整的票務自動化流程（FR-034、FR-037）

**獨立測試**：
1. 選擇一個即將開賣或已開賣的 FamiTicket 活動
2. 修改 `src/settings.json` 設定完整參數（帳號密碼、日期關鍵字、區域關鍵字）
3. 執行程式並觀察完整流程：登入 → 活動頁面 → 日期選擇 → 區域選擇 → 驗證問題（若有）
4. 驗證每個步驟都能正確執行
5. 驗證 URL 路由正確性（不同 URL 模式分派至對應函數）

### 整合實作

- [ ] T010 [US1-4] 實作 `nodriver_fami_date_to_area()` 於 `src/nodriver_tixcraft.py`：協調日期選擇 → 區域選擇流程（呼叫 `nodriver_fami_date_auto_select()` 與 `nodriver_fami_area_auto_select()`，參考 TixCraft NoDriver 協調器模式）
- [ ] T011 [US1-4] 實作 `nodriver_famiticket_main()` 於 `src/nodriver_tixcraft.py`：根據 URL 模式分派至對應函數（`/Home/User/SignIn` → login、`/Home/Activity/Info/` → activity、`/Home/Activity` → home、日期選擇頁面 → date_to_area、驗證頁面 → verify，參考 TixCraft NoDriver 的 `nodriver_tixcraft_main()` 模式）
- [ ] T012 [US1-4] 解除 NoDriver 主循環中的 FamiTicket 註解於 `src/nodriver_tixcraft.py` line 16841-16842：修改為 `await nodriver_famiticket_main(tab, url, config_dict)`

**檢查點**：執行 30 秒背景測試（驗證 URL 路由正確性）+ 真實 FamiTicket 完整購票流程測試（登入 → 日期 → 區域 → 驗證）

---

## 階段八：User Story 5 - 自動補票功能 (Priority: P2)

**目標**：實作自動補票功能（當日期列表為空時自動重新載入活動頁面，FR-028、FR-029）

**獨立測試**：
1. 修改 `src/settings.json` 設定 `tixcraft.auto_reload_coming_soon_page: true` 與 `advanced.auto_reload_page_interval: 5.0`
2. 選擇一個「即將開賣」的活動（日期列表為空）
3. 執行程式並觀察自動補票流程
4. 檢查 `.temp/test_output.txt` 中的 `reload` 與 `coming soon` 相關訊息
5. 驗證觸發條件（日期列表為空 + `auto_reload_coming_soon_page: true`）
6. 驗證等待間隔（`auto_reload_page_interval` 秒）
7. 驗證返回活動頁面（`await tab.get(last_activity_url)` 而非 `tab.reload()`，這是 FamiTicket 特定邏輯）
8. 驗證無死循環（程式在 30 秒後自動終止）
9. 驗證成功標準：SC-006（30 秒背景測試通過）、SC-008（重新載入間隔可配置）

### User Story 5 實作

- [ ] T013 [US5] 在 `nodriver_fami_date_auto_select()` 中新增自動補票邏輯於 `src/nodriver_tixcraft.py`：當日期列表為空（`formated_area_list` 為 None 或長度為 0）且 `auto_reload_coming_soon_page: true` 時，等待 `auto_reload_page_interval` 秒，使用 `await tab.get(last_activity_url)` 返回活動頁面（參考 Chrome 版本 line 3498-3510，但改用 `tab.get()` 而非 `tab.reload()`）

**檢查點**：執行 30 秒背景測試（驗證自動補票邏輯觸發且無死循環）+ 真實 FamiTicket「即將開賣」頁面測試

---

## 階段九：優化與橫向議題

**目的**：優化除錯訊息、錯誤處理與文件更新

- [ ] T014 [P] 新增除錯訊息（show_debug_message）於所有 FamiTicket 函數：日期匹配訊息（`[DATE KEYWORD] Matched keyword: "xxx"`）、區域匹配訊息（`[AREA KEYWORD] AND logic: ["xxx", "yyy"]`）、選擇結果訊息（`[DATE SELECT] Selected date: "xxx"`）、錯誤訊息（`[ERROR] Element not found: #usr_act`，參考 TixCraft NoDriver 除錯訊息格式）
- [ ] T015 [P] 強化錯誤處理與回退機制於所有 FamiTicket 函數：try-except 包裹所有 CDP 操作、返回布林值（簡化狀態管理）、備用方案（CDP 點擊失敗 → element.click()，參考 `research.md` 非同步錯誤處理模式）
- [ ] T016 [P] 更新 `docs/02-development/structure.md`：新增 FamiTicket NoDriver 函數索引（8 個函數：nodriver_famiticket_main、nodriver_fami_login、nodriver_fami_activity、nodriver_fami_date_auto_select、nodriver_fami_area_auto_select、nodriver_fami_verify、nodriver_fami_date_to_area、nodriver_fami_home_auto_select）
- [ ] T017 [P] 更新 `docs/10-project-tracking/accept_changelog.md`：記錄 FamiTicket NoDriver 遷移變更（遵循 Conventional Commits 格式，參考 `docs/10-project-tracking/changelog_guide.md`）
- [ ] T018 執行 quickstart.md 驗證：依照 `specs/005-famiticket-nodriver-migration/quickstart.md` 的 5 分鐘快速測試流程，確保所有步驟可順利執行（修改 settings.json → 30 秒背景測試 → 驗證輸出 → 真實頁面測試）

**檢查點**：所有文件更新完成，quickstart.md 驗證通過

---

## 相依性（Dependency）與執行順序

### 階段相依性

- **初始化（階段一）**：無相依性——可立即開始（T001、T002、T003 可平行執行）
- **基礎建設（階段二）**：無（本專案無阻斷性基礎建設）
- **User Stories（階段三至八）**：
  - **US1（階段三）**：依賴初始化完成（T001-T003）——不依賴其他 User Stories
  - **US2（階段四）**：依賴初始化完成（T001-T003）——可與 US1 平行開發
  - **US3（階段五）**：依賴初始化完成（T001-T003）——可與 US1、US2 平行開發
  - **US4（階段六）**：依賴初始化完成（T001-T003）——可與 US1、US2、US3 平行開發
  - **整合（階段七）**：依賴 US1、US2、US3、US4 完成（T004-T009）
  - **US5（階段八）**：依賴 US2 完成（T007，因需修改 `nodriver_fami_date_auto_select()`）
- **優化（階段九）**：依賴所有 User Stories 完成（T004-T013）

### User Story 相依性

```
初始化 (T001-T003)
    ├──> US1 (T004-T006) ──┐
    ├──> US2 (T007) ───────┤
    ├──> US3 (T008) ───────┼──> 整合 (T010-T012) ──> 優化 (T014-T018)
    └──> US4 (T009) ───────┘              ↓
                                      US5 (T013)
```

**關鍵決策**：
- US1-US4 可平行開發（如團隊人力允許）
- 整合（T010-T012）必須等待 US1-US4 完成
- US5（自動補票）依賴 US2（日期選擇）完成，因需修改 `nodriver_fami_date_auto_select()` 函數

### 每個 User Story 內部

- **US1**：T004 → T005 → T006（依序執行，T005 依賴 T004 的登入流程）
- **US2**：T007（單一任務，無內部相依性）
- **US3**：T008（單一任務，無內部相依性）
- **US4**：T009（單一任務，無內部相依性）
- **整合**：T010 → T011 → T012（依序執行，T011 依賴 T010 的協調器，T012 依賴 T011 的主函數）
- **US5**：T013（單一任務，但需修改 T007 的函數）
- **優化**：T014-T018（T014-T017 可平行執行，T018 最後執行）

### 平行作業機會

#### 初始化階段（T001-T003）
所有任務可平行執行（不同功能、無相依性）：
```bash
Task: "新增 nodriver_click_element() 工具函數於 src/nodriver_tixcraft.py"
Task: "新增 nodriver_search_element() 工具函數於 src/nodriver_tixcraft.py"
Task: "驗證現有工具函數可用性：src/util.py"
```

#### User Stories 平行開發（T004-T009）
基礎建設完成後，所有 P1 User Stories 可平行啟動（如團隊人力允許）：
```bash
# 開發者 A：US1
Task: "實作 nodriver_fami_login() 於 src/nodriver_tixcraft.py"
Task: "實作 nodriver_fami_activity() 於 src/nodriver_tixcraft.py"
Task: "實作 nodriver_fami_home_auto_select() 於 src/nodriver_tixcraft.py"

# 開發者 B：US2
Task: "實作 nodriver_fami_date_auto_select() 於 src/nodriver_tixcraft.py"

# 開發者 C：US3
Task: "實作 nodriver_fami_area_auto_select() 於 src/nodriver_tixcraft.py"

# 開發者 D：US4
Task: "實作 nodriver_fami_verify() 於 src/nodriver_tixcraft.py"
```

**注意**：由於所有函數都在同一個檔案（`src/nodriver_tixcraft.py`），平行開發時需注意程式碼衝突。建議依序開發或使用功能分支。

#### 優化階段（T014-T017）
文件更新任務可平行執行：
```bash
Task: "新增除錯訊息於所有 FamiTicket 函數"
Task: "強化錯誤處理與回退機制於所有 FamiTicket 函數"
Task: "更新 docs/02-development/structure.md"
Task: "更新 docs/10-project-tracking/accept_changelog.md"
```

---

## 平行作業範例：User Story 1

由於 US1 包含 3 個函數，且有相依性（login → activity → home），建議依序執行：

```bash
# Step 1: 登入功能（阻斷後續）
Task: "實作 nodriver_fami_login() 於 src/nodriver_tixcraft.py"

# Step 2: 活動頁面（依賴登入成功）
Task: "實作 nodriver_fami_activity() 於 src/nodriver_tixcraft.py"

# Step 3: 首頁入口（依賴登入成功）
Task: "實作 nodriver_fami_home_auto_select() 於 src/nodriver_tixcraft.py"
```

**測試檢查點**（每個 Task 完成後）：
```bash
# 執行 30 秒背景測試
cd /d/Desktop/bouob-TicketHunter\(MaxBot\)/tickets_hunter
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
echo "" > .temp/test_output.txt
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1

# 驗證輸出
grep "login\|SignIn\|usr_act" .temp/test_output.txt
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1-4）

1. **完成階段一**：初始化（T001-T003）
2. **完成階段三**：User Story 1（T004-T006）
3. **停止並驗證**：真實 FamiTicket 登入頁面測試
4. **完成階段四至六**：User Story 2-4（T007-T009）
5. **完成階段七**：整合所有 P1 User Stories（T010-T012）
6. **停止並驗證**：真實 FamiTicket 完整購票流程測試
7. **若已準備好則展示**：FamiTicket NoDriver 版本可用（P1 MVP）

### 漸進式交付

1. **初始化完成** → 工具函數就緒
2. **US1 完成（登入）** → 獨立測試 → 可展示登入功能
3. **US2 完成（日期選擇）** → 獨立測試 → 可展示日期關鍵字匹配
4. **US3 完成（區域選擇）** → 獨立測試 → 可展示區域關鍵字匹配（AND/OR 邏輯）
5. **US4 完成（驗證問題）** → 獨立測試 → 可展示驗證問題自動處理
6. **整合完成** → 真實頁面測試 → **MVP 達成！**（完整購票流程）
7. **US5 完成（自動補票）** → 獨立測試 → 增加自動補票功能（P2）
8. **優化完成** → quickstart.md 驗證 → **遷移完成！**

### 團隊平行開發策略

**若有多位開發者**：

1. **團隊共同完成**：初始化（T001-T003）
2. **初始化完成後分工**：
   - 開發者 A：US1（登入功能，T004-T006）
   - 開發者 B：US2（日期選擇，T007）
   - 開發者 C：US3（區域選擇，T008）
   - 開發者 D：US4（驗證問題，T009）
3. **US1-4 完成後整合**：開發者 A 負責整合（T010-T012）
4. **整合完成後**：開發者 B 負責 US5（自動補票，T013，需修改 T007 的函數）
5. **所有 User Stories 完成後**：團隊平行執行優化（T014-T018）

**注意**：由於所有函數都在同一個檔案（`src/nodriver_tixcraft.py`），建議使用 Git 功能分支避免衝突：
- `feat/us1-login`
- `feat/us2-date-selection`
- `feat/us3-area-selection`
- `feat/us4-verify`
- `feat/us5-auto-reload`

---

## 實作檢查點（每個任務完成後必須檢查）

### 程式碼品質

- [ ] 函數簽章符合 `contracts/function-signatures.md`（async/await、show_debug_message 參數、返回布林值）
- [ ] 函數命名遵循 `nodriver_fami_*` 規範（FR-039）
- [ ] 設定檔欄位符合 `contracts/config-schema.md`（完全重用現有欄位，無新增）
- [ ] 資料結構符合 `data-model.md`（6 個核心實體）
- [ ] 除錯訊息格式一致（`[DATE KEYWORD]`、`[AREA SELECT]` 等）
- [ ] 錯誤處理完整（try-except + 布林返回值）

### 測試驗證

- [ ] 30 秒背景測試通過（SC-006、SC-007）：無崩潰、無死循環
- [ ] 真實頁面測試通過（每個 User Story 獨立測試）
- [ ] 效能目標達成：
  - 登入操作 < 5 秒
  - 日期列表掃描 < 2 秒（SC-002）
  - 區域列表掃描 < 2 秒（SC-003）
  - 記憶體使用量 < 500MB

### 憲法遵循

- [ ] ✅ I. NoDriver First：使用 NoDriver API（async/await、CDP、Pierce 方法）
- [ ] ✅ II. 資料結構優先：所有實體定義於 `data-model.md`
- [ ] ✅ III. 三問法則：核心問題、簡單性、相容性
- [ ] ✅ IV. 單一職責與可組合性：每個函數職責單一，可組合
- [ ] ✅ V. 設定驅動開發：所有行為由 `settings.json` 控制
- [ ] ✅ VI. 測試驅動穩定性：30 秒背景測試 + 真實頁面測試
- [ ] ✅ VII. MVP 原則：P1 User Stories 優先完成，可獨立測試
- [ ] ✅ VIII. 文件與代碼同步：更新 `structure.md` 與 `accept_changelog.md`
- [ ] ✅ IX. Git 提交規範：使用 `/gsave` 指令，Conventional Commits 格式

---

## 備註

- **[P] 任務**：可平行執行（不同功能或文件，無相依性）
- **[Story] 標籤**：將任務對應到特定 User Story，方便追蹤進度
- **每個 User Story 都應能獨立完成與測試**（遵循 MVP 原則）
- **30 秒背景測試**：每個任務完成後必須執行（驗證邏輯正確性，無崩潰）
- **真實頁面測試**：每個 User Story 完成後必須執行（驗證實際票務流程）
- **每完成一個任務或邏輯群組就提交（commit）**：使用 `/gsave` 指令
- **可在任何檢查點停止**：獨立驗證 User Story，確保漸進式交付
- **避免**：任務描述模糊、同檔案衝突（使用功能分支）、跨 User Story 的相依性導致無法獨立

---

## 任務總結

**任務總數**：18 個任務

**各 User Story 任務數**：
- 初始化（Setup）：3 個任務（T001-T003）
- User Story 1（登入）：3 個任務（T004-T006）
- User Story 2（日期選擇）：1 個任務（T007）
- User Story 3（區域選擇）：1 個任務（T008）
- User Story 4（驗證問題）：1 個任務（T009）
- 整合（所有 P1 User Stories）：3 個任務（T010-T012）
- User Story 5（自動補票，P2）：1 個任務（T013）
- 優化與文件：5 個任務（T014-T018）

**平行執行機會**：
- 初始化階段：T001-T003（3 個任務可平行）
- User Stories 階段：US1-US4（4 個 User Stories 可平行開發，需注意同檔案衝突）
- 優化階段：T014-T017（4 個任務可平行）

**建議 MVP 範圍**：
- **最小 MVP**：初始化 + US1（登入功能）
- **完整 MVP**：初始化 + US1-US4 + 整合（完整購票流程，P1 優先級）
- **增強版**：完整 MVP + US5（自動補票，P2 優先級）

**預估完成時間**（單人開發）：
- 初始化：1-2 小時
- US1（登入）：2-3 小時
- US2（日期選擇）：2-3 小時
- US3（區域選擇）：2-3 小時
- US4（驗證問題）：1-2 小時
- 整合：2-3 小時
- US5（自動補票）：1-2 小時
- 優化與文件：2-3 小時
- **總計**：13-21 小時（約 2-3 個工作日）

**格式驗證**：✅ 所有任務均符合檢查清單格式（核取方塊、ID、標籤、檔案路徑）

---

**下一步**：執行 `/speckit.implement` 開始實作，或先執行 `/speckit.analyze` 檢查一致性。
