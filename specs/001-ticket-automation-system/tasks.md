---
description: "多平台自動化搶票系統任務清單（2025-10-27 更新）"
---

# 任務：多平台自動化搶票系統

**輸入**：來自 `specs/001-ticket-automation-system/` 的設計文件
**前置需求**：plan.md（必填）、spec.md（必填）、research.md、data-model.md、contracts/

**重大更新（2025-10-27）**：
- ✅ 涵蓋 TDR-004 技術決策（CDP 原生方法遷移）
- ✅ 涵蓋非功能性需求（NFR-001 至 NFR-007）
- ✅ 移除違反憲章的 JavaScript 回退任務
- ✅ 統一術語（Shadow DOM 穿透）

**測試**：本任務清單包含測試任務。測試為選填——僅在功能規格說明中明確要求時包含。

**組織方式**：任務依 7 個用戶故事（spec.md）分組，以利每個用戶故事可獨立實作與測試。

---

## 格式說明：`[ID] [P?] [Story] Description`
- **[ID]**：任務編號（T001、T002...）
- **[P]**：可並行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的用戶故事（US1-US7）
- 描述中**必須**包含精確的檔案路徑

---

## 相依性與執行順序

### 用戶故事完成順序（依優先度）

```
Phase 1: Setup（共用基礎）
    ↓
Phase 2: Foundational（核心前置）
    ↓
Phase 3: [US1] 自動化購票流程 (P1) ← 核心MVP
    ↓
Phase 4: [US2] 智慧日期與座位選擇 (P1) ← 與US1可部分並行
    ↓
Phase 5: [US7] 錯誤復原與重試 (P1) ← 與US1/US2可部分並行
    ↓
Phase 6: [US3] 自動身份認證 (P2)
Phase 6: [US6] 配置驅動行為 (P2) ← 可與US3並行
    ↓
Phase 7: [US4] 驗證碼處理 (P2)
    ↓
Phase 8: [US5] 多平台支援 (P3)
    ↓
Phase 9: NoDriver CDP 原生方法遷移（TDR-004）
    ↓
Phase 10: 效能與品質驗證（NFR 驗證）
```

### 並行執行機會

**Phase 1-2 中的並行任務：**
- T001-T005：共用基礎設施初始化（獨立且可並行）

**Phase 3 中的並行任務：**
- T015-T017：環境初始化子任務（獨立的平台初始化）
- T021-T023：核心工作流引擎模組（獨立模組開發）

**Phase 4 中的並行任務：**
- T031-T035：日期/區域選擇器開發（獨立模組）

**Phase 6 中的並行任務：**
- US3 任務與 US6 任務可完全並行（不同模組）

---

## Phase 1：Setup（共用基礎設施）

**目的**：專案初始化與基本結構建立

### 基礎設施

- [ ] T001 建立專案結構與目錄組織 (src/, tests/, docs/, specs/)
- [ ] T002 [P] 配置 Python 環境與虛擬環境 (requirements.txt 依賴安裝)
- [ ] T003 [P] 初始化 Git 倉庫與 .gitignore 配置
- [ ] T004 [P] 設定 settings.json 模板與驗證機制 (src/settings.json)
- [ ] T005 [P] 建立日誌系統與偵錯設定 (src/util.py - logging utilities)

### 核心配置架構

- [ ] T006 實作 JSON Schema 驗證層 (specs/001-ticket-automation-system/contracts/config-schema.md validation)
- [ ] T007 [P] 建立配置讀取器 (src/util.py - load_config_dict())
- [ ] T008 [P] 實作配置預設值與覆蓋機制 (src/util.py - apply_defaults())

### 文件與文件化

- [ ] T009 生成 API 參考文件骨架 (docs/03-api-reference/)
- [ ] T010 [P] 建立快速入門指南執行檔 (docs/01-getting-started/ - verification scripts)

---

## Phase 2：Foundational（核心前置作業）

**目的**：所有用戶故事必須的核心功能

### WebDriver 初始化層

- [ ] T011 實作 WebDriver 工廠模式 (src/nodriver_tixcraft.py - init_driver() for NoDriver)
- [ ] T012 [P] 實作 Chrome Driver 初始化 (src/chrome_tixcraft.py - init_driver() for Chrome - 遺留版本)
- [ ] T013 [P] 實作 Selenium WebDriver 初始化 (src/util.py - selenium fallback)
- [ ] T014 實作瀏覽器設定檔管理 (src/util.py - profile management)

### 暫停機制與安全檢查

- [ ] T015 實作強制暫停機制（5秒確認） (src/util.py - pause_before_checkout())
- [ ] T016 [P] 實作使用者確認對話框 (src/util.py - confirmation utilities)

### NoDriver CDP 標準工具函式（TDR-004）

- [ ] T017 實作 CDP perform_search() 封裝函式 (src/util.py - search_elements_pierce() - contracts/platform-interface.md)
  - 必須使用 include_user_agent_shadow_dom=True
  - 支援 timeout 參數（預設 5.0 秒）
  - 自動清理資源（discard_search_results）
  - 返回 node_id 列表

- [ ] T018 [P] 實作 CDP 原生點擊函式 (src/util.py - click_element_native() - contracts/platform-interface.md)
  - 使用 scroll_into_view_if_needed()
  - 使用 get_box_model() 取得座標
  - 使用 dispatch_mouse_event() (mousePressed + mouseReleased)
  - 禁止回退到 JavaScript

- [ ] T019 [P] 實作智能等待函式 (src/util.py - wait_for_element_pierce() - TDR-004)
  - 初始隨機等待 1.2-1.8 秒
  - 輪詢檢查（間隔 0.3 秒）
  - 最多額外等待 5 秒
  - 返回 (found, elapsed_time)

- [ ] T020 [P] 實作資源清理工具函式 (src/util.py - cleanup_search_resources())
  - 防禦性 try-except
  - 記錄清理失敗（verbose 模式）

### 共用工具函數庫

- [ ] T021 [P] 實作文本匹配與關鍵字搜尋工具 (src/util.py - keyword_matching functions)
- [ ] T022 [P] 實作錯誤分類與記錄 (src/util.py - error_classifier)

### 核心工作流引擎架構

- [ ] T023 實作 12 階段主工作流框架 (src/nodriver_tixcraft.py - main workflow orchestrator)
- [ ] T024 [P] 實作每個階段的生命週期管理 (src/util.py - stage lifecycle)
- [ ] T025 [P] 實作平台適配器基類 (src/util.py - PlatformAdapter abstract class)

---

## Phase 3：[US1] 自動化購票流程（P1）

**使用者故事**：身為購票者，我希望系統能自動完成從頭到尾的整個購票流程。

**獨立測試標準**：
1. 配置目標活動 URL 與票券條件
2. 執行自動化流程
3. 驗證系統完成所有 12 個階段
4. 確認最終訂單確認頁面顯示

### 階段 1：環境初始化

- [ ] T026 [US1] 實作 WebDriver 類型選擇邏輯 (src/nodriver_tixcraft.py - webdriver_type config - FR-001)
- [ ] T027 [US1] [P] 實作瀏覽器選項配置（無頭、視窗大小、代理） (src/nodriver_tixcraft.py - browser_options - FR-002)
- [ ] T028 [US1] [P] 實作瀏覽器擴充功能載入 (src/util.py - load_extensions - FR-003)
- [ ] T029 [US1] [P] 實作配置驗證與啟動檢查 (src/util.py - validate_startup_config - FR-004)

### 階段 2：身份認證（基礎版本 - 與 US3 錯開）

- [ ] T030 [US1] 實作 Cookie 注入機制（基本支援） (src/util.py - inject_cookies_basic - FR-005)
- [ ] T031 [US1] [P] 實作登入狀態驗證 (src/util.py - verify_login_state - FR-007)
- [ ] T032 [US1] [P] 實作會話維持機制 (src/nodriver_tixcraft.py - maintain_session - FR-008)

### 階段 3：頁面監控與重載

- [ ] T033 [US1] 實作自動重載迴圈 (src/nodriver_tixcraft.py - auto_reload_loop - FR-009)
- [ ] T034 [US1] [P] 實作過熱保護（退避策略） (src/util.py - overheat_protection - FR-010)
- [ ] T035 [US1] [P] 實作彈出視窗偵測與關閉 (src/util.py - close_popups - FR-011)
- [ ] T036 [US1] [P] 實作「即將開賣」頁面偵測 (src/util.py - detect_coming_soon - FR-012)
- [ ] T037 [US1] [P] 實作排隊/等候室偵測 (src/util.py - detect_queue - FR-013)

### 階段 4-6：選擇與數量（與 US2 錯開 - 此處為簡化版）

- [ ] T038 [US1] 實作日期選擇基礎邏輯（簡化） (src/nodriver_tixcraft.py - select_date_simple - FR-014-019)
  - 使用 CDP perform_search() 查找日期按鈕
  - 使用 CDP dispatch_mouse_event() 點擊
  - 禁止 JavaScript 執行（NFR-004）

- [ ] T039 [US1] [P] 實作區域選擇基礎邏輯（簡化） (src/nodriver_tixcraft.py - select_area_simple - FR-020-026)
  - 使用 CDP perform_search() 查找區域按鈕
  - 使用 CDP dispatch_mouse_event() 點擊
  - 禁止 JavaScript 執行（NFR-004）

- [ ] T040 [US1] [P] 實作票券數量設定 (src/nodriver_tixcraft.py - set_ticket_count - FR-027-030)

### 階段 7-9：驗證碼、表單、同意（與 US4 錯開）

- [ ] T041 [US1] 實作驗證碼偵測（基礎） (src/util.py - detect_captcha_basic - FR-031-032)
- [ ] T042 [US1] [P] 實作手動驗證碼輸入回退 (src/util.py - manual_captcha_fallback - FR-037)
- [ ] T043 [US1] [P] 實作表單欄位填寫（基礎） (src/util.py - fill_form_basic - FR-040-043)
- [ ] T044 [US1] [P] 實作同意核取方塊自動勾選 (src/util.py - auto_check_agreements - FR-044-047)

### 階段 10：訂單確認與送出

- [ ] T045 [US1] 實作訂單詳情審查 (src/nodriver_tixcraft.py - review_order - FR-048)
- [ ] T046 [US1] [P] 實作訂單送出按鈕偵測與點擊 (src/nodriver_tixcraft.py - submit_order - FR-049)
  - 使用 CDP perform_search() 查找送出按鈕
  - 使用 CDP dispatch_mouse_event() 點擊
  - 禁止 JavaScript 回退（FR-060, FR-064）

- [ ] T047 [US1] [P] 實作確認對話框處理 (src/util.py - handle_confirmation_dialog - FR-050)
- [ ] T048 [US1] [P] 實作音訊通知（基礎） (src/util.py - play_notification_basic - FR-051-052)
- [ ] T049 [US1] [P] 實作訂單成功驗證 (src/nodriver_tixcraft.py - verify_order_success - FR-053)

### 階段 11-12：排隊與錯誤處理

- [ ] T050 [US1] 實作排隊流程處理 (src/nodriver_tixcraft.py - handle_queue - FR-054-057)
- [ ] T051 [US1] [P] 實作錯誤類型偵測與分類 (src/util.py - classify_error - FR-058)
- [ ] T052 [US1] [P] 實作詳細錯誤日誌 (src/util.py - detailed_error_logging - FR-059)
- [ ] T053 [US1] [P] 實作 CDP 原生重試機制 (src/util.py - cdp_native_retry - FR-060)
  - 使用 CDP dispatch_mouse_event() 重試點擊
  - 使用 CDP perform_search() 重新查詢元素
  - 禁止回退到 JavaScript（FR-060 明確禁止）

- [ ] T054 [US1] [P] 實作錯誤通知 (src/util.py - error_notification - FR-062)
- [ ] T055 [US1] [P] 實作售罄狀態持續重試機制 (src/util.py - handle_sold_out - FR-063)
  - 根據 auto_reload_page_interval 持續刷新頁面
  - 監控票券狀態直到可用
  - 避免在售罄時停止程式

### US1 整合與測試

- [ ] T056 [US1] 整合 12 個階段成完整工作流 (src/nodriver_tixcraft.py - main workflow)
- [ ] T057 [US1] [P] 建立 US1 測試案例與文件 (tests/integration/test_us1_full_workflow.py)
- [ ] T058 [US1] [P] 手動驗證 TixCraft 平台 (complete end-to-end purchase simulation)

---

## Phase 4：[US2] 智慧日期與座位選擇（P1）

**使用者故事**：身為購票者，我希望系統使用關鍵字匹配搭配回退策略來選擇偏好的日期和座位區域。

**獨立測試標準**：
1. 配置日期/區域關鍵字和回退模式
2. 執行選擇流程
3. 驗證關鍵字匹配邏輯（第一選擇 90% 成功率 - SC-002）
4. 驗證回退策略（模式選擇正確執行）

### 日期選擇高級版（使用 CDP 原生方法）

- [ ] T059 [US2] 實作日期選擇佈局類型偵測 (src/util.py - detect_date_layout - FR-014)
  - 使用 CDP perform_search() 偵測按鈕/下拉/日曆佈局

- [ ] T060 [US2] [P] 實作日期列表解析與售罄過濾 (src/util.py - parse_available_dates - FR-015-016)
  - 使用 CDP perform_search() 提取所有日期選項
  - 使用 CDP describe_node() 解析屬性（disabled 狀態）

- [ ] T061 [US2] [P] 實作多關鍵字日期匹配 (src/util.py - match_date_keywords - FR-017)
- [ ] T062 [US2] [P] 實作日期回退模式選擇 (src/util.py - fallback_date_selection - FR-018)
- [ ] T063 [US2] [P] 實作日期選擇驗證 (src/util.py - verify_date_selected - FR-019)

### 區域/座位選擇高級版（使用 CDP 原生方法）

- [ ] T064 [US2] 實作區域選擇佈局類型偵測 (src/util.py - detect_area_layout - FR-020)
  - 使用 CDP perform_search() 偵測區域按鈕/下拉/座位圖/展開面板

- [ ] T065 [US2] [P] 實作區域列表解析與定價資訊提取 (src/util.py - parse_available_areas - FR-021)
  - 使用 CDP perform_search() 提取所有區域選項
  - 使用 CDP get_outer_html() 提取定價資訊

- [ ] T066 [US2] [P] 實作排除關鍵字過濾 (src/util.py - filter_excluded_areas - FR-022)
- [ ] T067 [US2] [P] 實作多關鍵字區域匹配 (src/util.py - match_area_keywords - FR-023)
- [ ] T068 [US2] [P] 實作區域回退模式選擇 (src/util.py - fallback_area_selection - FR-024)
- [ ] T069 [US2] [P] 實作自動座位選擇演算法 (src/util.py - auto_select_seats - FR-025)
- [ ] T070 [US2] [P] 實作相鄰座位切換支援 (src/util.py - allow_non_adjacent_seats - FR-026)
- [ ] T071 [US2] [P] 實作區域選擇驗證 (src/util.py - verify_area_selected)

### US2 測試

- [ ] T072 [US2] 建立日期/區域匹配測試用例 (tests/unit/test_date_area_matching.py)
- [ ] T073 [US2] [P] 建立回退策略測試用例 (tests/unit/test_fallback_strategies.py)
- [ ] T074 [US2] [P] 手動驗證多平台日期/區域選擇 (test against KKTIX, TicketPlus, iBon)

---

## Phase 5：[US7] 錯誤復原與重試（P1）

**使用者故事**：身為購票者，我希望系統自動重試失敗的操作並處理常見錯誤。

**獨立測試標準**：
1. 模擬各類錯誤（點擊失敗、網路錯誤、頁面超時）
2. 驗證 CDP 原生重試機制正常運作
3. 確認售罄場景持續重試機制（根據刷新間隔自動重試）
4. 驗證成功率達到 95%+（SC-005）

### 錯誤分類與重試基礎

- [ ] T075 [US7] 實作錯誤型別分類系統 (src/util.py - error_classifier - FR-058)
- [ ] T076 [US7] [P] 實作詳細錯誤日誌系統 (src/util.py - verbose_error_logging - FR-059)
- [ ] T077 [US7] [P] 實作指數退避重試策略 (src/util.py - exponential_backoff - FR-060)
- [ ] T078 [US7] [P] 實作可配置重試限制 (src/util.py - retry_limits config - FR-061)

### CDP 原生操作層面重試（遵循 TDR-004）

- [ ] T079 [US7] 實作 CDP 點擊重試機制 (src/nodriver_tixcraft.py - cdp_click_retry - FR-060)
  - 使用 dispatch_mouse_event() 重試
  - 記錄重試次數與延遲
  - 禁止回退到 JavaScript（FR-060 明確規定）

- [ ] T080 [US7] [P] 實作 CDP DOM 重新查詢機制 (src/util.py - cdp_requery_element)
  - 使用 perform_search() 重新查找元素
  - 處理 Shadow DOM 變化
  - 更新 node_id 快取

- [ ] T081 [US7] [P] 實作元素互動成功率 95%+ 驗證 (tests/integration/test_click_success_rate.py - SC-005)

### 特殊場景處理

- [ ] T082 [US7] 實作售罄狀態偵測與自動重試邏輯 (src/util.py - handle_sold_out - FR-063)
  - 偵測售罄狀態（文字匹配、元素檢查）
  - 根據配置的刷新間隔持續重試
  - 在 verbose 模式下記錄重試日誌

- [ ] T083 [US7] [P] 實作錯誤通知與警報 (src/util.py - error_notification - FR-062)
- [ ] T084 [US7] [P] 實作頁面變更時的重試邏輯 (src/util.py - retry_on_page_change)

### US7 測試

- [ ] T085 [US7] 建立錯誤處理測試用例 (tests/unit/test_error_handling.py)
- [ ] T086 [US7] [P] 建立 CDP 重試機制測試 (tests/unit/test_cdp_retry_logic.py)
- [ ] T087 [US7] [P] 模擬高壓力下的錯誤恢復 (stress test simulation)

---

## Phase 6：[US3] 自動身份認證 + [US6] 配置驅動行為（P2）

**可並行執行**：US3 與 US6 為獨立模組，可完全並行開發。

### [US3] 自動身份認證（P2）

**使用者故事**：身為購票者，我希望系統使用儲存的憑證或 Cookie 自動登入售票平台。

**獨立測試標準**：
1. 配置平台憑證或 Cookie
2. 執行登入流程
3. 驗證登入成功
4. 確認會話維持

#### Cookie 注入（主要方法）

- [ ] T088 [US3] 實作 TixCraft Cookie 注入 (tixcraft_sid) (src/util.py - inject_tixcraft_cookie - FR-005)
- [ ] T089 [US3] [P] 實作 iBon Cookie 注入 (ibonqware) (src/util.py - inject_ibon_cookie - FR-005)
- [ ] T090 [US3] [P] 實作通用 Cookie 注入框架 (src/util.py - generic_cookie_injection - FR-005)

#### 使用者名稱/密碼登入（回退方法）

- [ ] T091 [US3] 實作登入表單偵測 (src/util.py - detect_login_form - FR-006)
  - 使用 CDP perform_search() 查找登入表單

- [ ] T092 [US3] [P] 實作認證欄位填寫 (src/util.py - fill_credentials)
- [ ] T093 [US3] [P] 實作登入表單送出 (src/util.py - submit_login_form)

#### 登入驗證與會話維持

- [ ] T094 [US3] 實作登入成功驗證 (src/util.py - verify_login_success - FR-007)
- [ ] T095 [US3] [P] 實作會話狀態維持 (src/nodriver_tixcraft.py - maintain_session_throughout - FR-008)

#### US3 測試

- [ ] T096 [US3] 建立 Cookie 注入測試 (tests/unit/test_cookie_injection.py)
- [ ] T097 [US3] [P] 建立登入流程測試 (tests/unit/test_login_flow.py)

### [US6] 配置驅動行為（P2）

**使用者故事**：身為購票者，我希望透過設定檔配置所有自動化行為而無需修改程式碼。

**獨立測試標準**：
1. 修改 settings.json 參數
2. 執行購票流程
3. 驗證行為根據配置變化
4. 達成 95% 使用案例可配置（SC-001）

#### 配置驗證與默認值

- [ ] T098 [US6] 實作 JSON Schema 配置驗證 (src/util.py - validate_config_schema)
- [ ] T099 [US6] [P] 實作配置默認值應用 (src/util.py - apply_config_defaults - FR-004)
- [ ] T100 [US6] [P] 實作清楚的配置錯誤訊息 (SC-009 requirement)

#### 可配置參數實作

- [ ] T101 [US6] 實作票券數量配置 (ticket_number in settings.json)
- [ ] T102 [US6] [P] 實作日期/區域關鍵字配置 (date_keyword, area_keyword, mode)
- [ ] T103 [US6] [P] 實作自動重載間隔配置 (auto_reload_page_interval - FR-009, FR-061)
- [ ] T104 [US6] [P] 實作聲音通知配置 (play_sound settings - FR-051-052)
- [ ] T105 [US6] [P] 實作重試參數配置 (retry limits, exponential backoff)
- [ ] T106 [US6] [P] 實作 OCR 相關配置（與 US4 整合） (ocr_captcha settings)
- [ ] T107 [US6] [P] 實作 WebDriver 類型配置 (webdriver_type - NoDriver/Chrome/Selenium)
- [ ] T108 [US6] [P] 實作平台特定配置覆蓋 (advanced.{platform}_* settings)

#### 配置驅動的行為控制

- [ ] T109 [US6] 實作配置驅動的 OCR 開關 (src/nodriver_tixcraft.py - ocr_captcha.enable)
- [ ] T110 [US6] [P] 實作配置驅動的無頭模式 (headless config)
- [ ] T111 [US6] [P] 實作配置驅動的詳細模式 (verbose config)
- [ ] T112 [US6] [P] 實作多設定檔支援 (src/config_launcher.py - multi-config management)

#### US6 測試

- [ ] T113 [US6] 建立配置驗證測試 (tests/unit/test_config_validation.py)
- [ ] T114 [US6] [P] 建立配置驅動行為測試 (tests/unit/test_config_driven_behavior.py)

---

## Phase 7：[US4] 驗證碼處理（P2）

**使用者故事**：身為購票者，我希望系統使用 OCR 自動辨識並輸入驗證碼。

**獨立測試標準**：
1. 配置 OCR 相關設定
2. 遇到驗證碼挑戰
3. 驗證 OCR 辨識準確率 70%+（SC-004）
4. 驗證手動輸入回退正常運作

### 驗證碼偵測

- [ ] T115 [US4] 實作驗證碼類型偵測 (img, canvas, reCAPTCHA, hCaptcha) (src/util.py - detect_captcha_type - FR-031)
  - 使用 CDP perform_search() 查找驗證碼元素

- [ ] T116 [US4] [P] 實作驗證碼圖片提取 (canvas/img) (src/util.py - extract_captcha_image - FR-032)

### OCR 辨識

- [ ] T117 [US4] 實作 ddddocr 整合 (src/util.py - ocr_recognize_captcha - FR-033)
- [ ] T118 [US4] [P] 實作 Beta OCR 模型支援 (ddddocr beta model - FR-034)
- [ ] T119 [US4] [P] 實作 OCR 準確率測試 (達到 70%+ 目標 - SC-004)

### 驗證碼輸入與回退

- [ ] T120 [US4] 實作自動驗證碼輸入 (src/util.py - auto_input_captcha - FR-035)
- [ ] T121 [US4] [P] 實作強制送出 vs. 等待手動確認邏輯 (FR-036)
- [ ] T122 [US4] [P] 實作手動驗證碼輸入回退 (src/util.py - manual_captcha_input - FR-037)
- [ ] T123 [US4] [P] 實作驗證碼重新整理功能 (FR-038)
- [ ] T124 [US4] [P] 實作可配置重試次數 (FR-039)

### US4 測試

- [ ] T125 [US4] 建立 OCR 辨識測試 (tests/unit/test_ocr_recognition.py)
- [ ] T126 [US4] [P] 建立驗證碼處理測試 (tests/unit/test_captcha_handling.py)
- [ ] T127 [US4] [P] 手動驗證 TixCraft OCR 辨識（測試帳號） (manual verification with real captchas)

---

## Phase 8：[US5] 多平台支援（P3）

**使用者故事**：身為跨區域的購票者，我希望系統支援多個售票平台。

**獨立測試標準**：
1. 配置不同平台 URL
2. 執行每個平台的購票流程
3. 驗證平台特定邏輯正確執行
4. 達成 5 個主要平台完全支援（SC-006）

### 平台適配器實作（所有平台使用 CDP 原生方法）

#### TixCraft 適配器（NoDriver 標準）

- [ ] T128 [US5] 實作 TixCraft 平台識別邏輯 (src/nodriver_tixcraft.py - platform detection)
- [ ] T129 [US5] [P] 實作 TixCraft CDP 選擇器 (src/util.py - tixcraft_cdp_selectors)
  - 所有 DOM 查詢使用 perform_search()
  - 所有點擊使用 dispatch_mouse_event()

- [ ] T130 [US5] [P] 實作 TixCraft Cookie 登入 (tixcraft_sid)

#### KKTIX 適配器（NoDriver 標準）

- [ ] T131 [US5] 實作 KKTIX 平台識別邏輯 (src/nodriver_tixcraft.py - KKTIX detection)
- [ ] T132 [US5] [P] 實作 KKTIX 價格清單佈局處理 (src/util.py - kktix_price_list_layout_cdp)
  - 使用 perform_search() 處理價格清單

- [ ] T133 [US5] [P] 實作 KKTIX 排隊處理邏輯 (KKTIX queue/waiting room)

#### iBon 適配器（NoDriver 標準 - Shadow DOM 穿透）

- [ ] T134 [US5] 實作 iBon 平台識別邏輯 (src/nodriver_tixcraft.py - iBon detection)
- [ ] T135 [US5] [P] 實作 iBon Shadow DOM 穿透處理 (src/util.py - shadow_dom_pierce_ibon - TDR-004)
  - 使用 perform_search(include_user_agent_shadow_dom=True)
  - 實作智能等待（1.2-6.2秒輪詢）
  - 效能目標：2-5秒完成，95%+ 首次成功率（NFR-001, NFR-002）

- [ ] T136 [US5] [P] 實作 iBon Angular SPA 支援 (iBon SPA handling with CDP)
- [ ] T137 [US5] [P] 實作 iBon Cookie 登入 (ibonqware)

#### TicketPlus 適配器（NoDriver 標準）

- [ ] T138 [US5] 實作 TicketPlus 平台識別邏輯 (src/nodriver_tixcraft.py - TicketPlus detection)
- [ ] T139 [US5] [P] 實作 TicketPlus 展開面板佈局 (collapsible panel handling with CDP)
  - 使用 perform_search() 查找展開按鈕
  - 使用 dispatch_mouse_event() 展開面板

- [ ] T140 [US5] [P] 實作 TicketPlus 實名驗證對話框 (real name verification dialog)

#### KHAM 適配器（NoDriver 標準）

- [ ] T141 [US5] 實作 KHAM 平台識別邏輯 (src/nodriver_tixcraft.py - KHAM detection)
- [ ] T142 [US5] [P] 實作 KHAM 自動 vs. 手動座位切換 (seat selection toggle with CDP)
- [ ] T143 [US5] [P] 實作 KHAM 實名對話框 (real name dialog)

### 多平台測試

- [ ] T144 [US5] 建立平台識別測試 (tests/unit/test_platform_detection.py)
- [ ] T145 [US5] [P] 建立平台特定 CDP 選擇器測試 (tests/unit/test_platform_cdp_selectors.py)
- [ ] T146 [US5] [P] 手動驗證各平台購票流程 (manual test with real ticket websites)

---

## Phase 9：NoDriver CDP 原生方法遷移（TDR-004）

**目的**：完成所有平台向 CDP 原生方法的遷移，確保反偵測與效能目標

**參考**：plan.md TDR-004、contracts/platform-interface.md

### TixCraft 平台遷移

- [ ] T147 [TDR-004] 遷移 TixCraft 日期選擇到 perform_search() (src/nodriver_tixcraft.py - nodriver_tixcraft_date_auto_select)
  - 移除所有 tab.evaluate() 調用
  - 移除所有 tab.find() 調用
  - 使用 perform_search(include_user_agent_shadow_dom=True)
  - 使用 dispatch_mouse_event() 點擊

- [ ] T148 [P] [TDR-004] 遷移 TixCraft 區域選擇到 perform_search() (src/nodriver_tixcraft.py - nodriver_tixcraft_area_auto_select)
- [ ] T149 [P] [TDR-004] 遷移 TixCraft 驗證碼處理到 CDP 原生方法 (src/nodriver_tixcraft.py)

### KKTIX 平台遷移

- [ ] T150 [TDR-004] 遷移 KKTIX 價格清單到 perform_search() (src/nodriver_tixcraft.py - nodriver_kktix_*)
- [ ] T151 [P] [TDR-004] 遷移 KKTIX 排隊頁面到 CDP 原生方法 (src/nodriver_tixcraft.py)

### TicketPlus 平台遷移

- [ ] T152 [TDR-004] 遷移 TicketPlus 展開面板到 perform_search() (src/nodriver_tixcraft.py - nodriver_ticketplus_*)

### KHAM 平台遷移

- [ ] T153 [TDR-004] 遷移 KHAM 座位選擇到 perform_search() (src/nodriver_tixcraft.py - nodriver_kham_*)

### 程式碼審查與驗證（TDR-004 檢查清單）

- [ ] T154 [TDR-004] 執行 NoDriver 版本程式碼稽核 (全專案掃描 - NFR-004)
  - [ ] 確認不存在 tab.evaluate() 調用
  - [ ] 確認不存在 tab.find() 調用
  - [ ] 確認所有 DOM 查詢使用 perform_search()
  - [ ] 確認所有點擊使用 dispatch_mouse_event()
  - [ ] 確認所有 perform_search() 後調用 discard_search_results()
  - [ ] 確認智能等待使用隨機初始延遲（1.2-1.8秒）

- [ ] T155 [P] [TDR-004] 更新 Chrome Driver 版本標記為遺留 (src/chrome_tixcraft.py - 註釋標記維護模式)

---

## Phase 10：效能與品質驗證（NFR 驗證）

**目的**：驗證非功能性需求達標，確保生產就緒

### 效能驗證（NFR-001 至 NFR-003）

- [ ] T156 [NFR-001] 建立 Shadow DOM 查詢效能測試 (tests/performance/test_dom_query_speed.py)
  - 目標：2-5秒內完成（平均值）
  - 測試平台：iBon（Shadow DOM）、TicketPlus（展開面板）
  - 測量方法：time.time() 計時 perform_search() 執行時間
  - 記錄：verbose 模式輸出 "[PERF] DOM query completed in X.Xs"

- [ ] T157 [P] [NFR-002] 建立首次成功率統計工具 (tests/performance/test_first_attempt_success_rate.py)
  - 目標：>= 95% 首次找到目標元素
  - 測試方法：執行 100 次 perform_search()，統計 count > 0 的比例
  - 記錄成功率至日誌

- [ ] T158 [P] [NFR-003] 建立記憶體消耗測試 (tests/performance/test_memory_usage.py)
  - 目標：單次 DOM 查詢 < 5MB
  - 測量方法：使用 tracemalloc 測量 perform_search() 記憶體峰值
  - 對比：DOMSnapshot 方法（應為 50MB+）

### 反偵測驗證（NFR-004 至 NFR-006）

- [ ] T159 [NFR-004] 建立 JavaScript 執行偵測測試 (tests/security/test_no_javascript_execution.py)
  - 目標：NoDriver 版本 100% 避免 JavaScript 執行
  - 測試方法：
    - 靜態程式碼分析（grep 搜尋 tab.evaluate）
    - 執行時監控（檢查 CDP JavaScript.evaluate 調用）
  - 斷言：0 次 JavaScript 執行

- [ ] T160 [P] [NFR-005] 建立 CDP 原生事件驗證測試 (tests/security/test_cdp_native_events.py)
  - 目標：所有互動使用 CDP 原生事件
  - 驗證：所有點擊使用 dispatch_mouse_event()
  - 驗證：所有滾動使用 scroll_into_view_if_needed()

- [ ] T161 [P] [NFR-006] 建立反機器人檢測通過測試 (tests/security/test_anti_bot_detection.py)
  - 目標：通過 reCAPTCHA v2、Cloudflare Challenge
  - 測試平台：TixCraft、iBon（實際反機器人場景）
  - 測量：執行 10 次購票流程，記錄是否被標記
  - 成功標準：0 次被封鎖或要求額外驗證

### 可靠性驗證（NFR-007）

- [ ] T162 [NFR-007] 建立 CDP 原生方法優先策略驗證 (tests/integration/test_cdp_native_priority.py)
  - 驗證：NoDriver 版本純 CDP 實作（無 JavaScript 回退）
  - 驗證：Chrome Driver 版本標記為遺留
  - 程式碼審查：確認所有錯誤重試使用 CDP 方法

### 整體品質保證

- [ ] T163 完整功能迴歸測試 (all 7 user stories end-to-end - SC-010)
  - 測試範圍：US1 至 US7 完整流程
  - 測試平台：TixCraft、KKTIX、iBon、TicketPlus、KHAM
  - 成功標準：99% 運作時間（高流量模擬）

- [ ] T164 [P] 跨平台相容性測試 (Windows, macOS, Linux)
- [ ] T165 [P] 高流量壓力測試 (99%+ uptime simulation - SC-010)

### 文件與文件化

- [ ] T166 更新 NoDriver API 參考文件 (docs/03-api-reference/nodriver_api_guide.md)
  - 新增 TDR-004 相關 API 說明
  - 新增 CDP 標準介面範例
  - 更新 Shadow DOM 穿透指南

- [ ] T167 [P] 更新多平台開發指南 (docs/02-development/platform_development_guide.md)
  - 新增 CDP 原生方法遷移檢查清單
  - 新增反偵測最佳實踐

- [ ] T168 [P] 更新故障排除指南 (docs/05-troubleshooting/README.md)
  - 新增 CDP 相關常見問題
  - 新增效能調優指南

- [ ] T169 [P] 更新 CHANGELOG (docs/07-project-tracking/CHANGELOG.md)
  - 記錄 TDR-004 架構遷移
  - 記錄效能提升數據（60-70% 速度提升）
  - 記錄反偵測改進

### 部署與發佈

- [ ] T170 設定 CI/CD 管道 (.github/workflows/)
- [ ] T171 [P] 建立自動化測試運行程序 (pytest CI)
- [ ] T172 [P] 準備打包配置 (PyInstaller/構建指令)
- [ ] T173 [P] 最終安全審查與法律合規檢查 (LEGAL_NOTICE.md review)

---

## 實作策略與 MVP 範圍

### 推薦 MVP 範圍（第一階段發佈）

**Phase 1-5 完成後，系統已達成生產就緒的 MVP：**

✅ **包含**：
- 完整的自動化購票流程（12 個階段）
- 智慧日期/區域選擇搭配回退
- 錯誤復原與 CDP 原生重試
- NoDriver CDP 標準工具函式
- 為 TixCraft 平台優化（使用 CDP 原生方法）

⏸️ **延後至 MVP 後**：
- 完整的多平台支援（可漸進式新增）
- 高級 OCR 功能（70% 基礎已達成）
- 全平台 CDP 遷移（Phase 9）

### 漸進式交付計畫

```
V1.0.0-MVP (Phase 1-5 完成)
├── Core: 自動化購票 + 日期/區域選擇 + CDP 原生錯誤處理
├── Platform: TixCraft 完全支援（CDP 原生方法）
├── Target: 90%+ 使用案例成功率
├── Performance: 60-70% 速度提升（vs. JavaScript 方法）

V1.1.0 (Phase 6 完成)
├── Add: 自動身份認證 (Cookie + 憑證)
├── Add: 配置驅動行為 (settings.json 全功能)

V1.2.0 (Phase 7 完成)
├── Add: OCR 驗證碼處理 (70%+ 準確率)

V2.0.0 (Phase 8-9 完成)
├── Add: 多平台支援 (KKTIX, iBon, TicketPlus, KHAM)
├── Add: 全平台 CDP 原生方法遷移
├── Target: 5 個主要平台完全支援
├── Performance: 95%+ Shadow DOM 首次成功率

V2.1.0 (Phase 10 完成)
├── Add: NFR 驗證完成（效能、反偵測、可靠性）
├── Quality: 99% 運作時間（高流量場景）
├── Documentation: 完整 API 參考與故障排除指南
```

---

## 任務執行建議

### 優先執行順序

1. **優先度最高**（Phase 1-2）：共用基礎，所有故事都依賴
   - **關鍵**：T017-T020（CDP 標準工具函式）必須優先完成

2. **優先度高**（Phase 3-5）：核心 MVP 功能，快速交付價值
   - **關鍵**：所有任務使用 CDP 原生方法，禁止 JavaScript

3. **優先度中**（Phase 6-8）：增強功能，可視化支援

4. **優先度低**（Phase 9-10）：遷移與驗證

### 並行機會

- **Phase 1 中的 T002-T005**：完全獨立，可 4 人並行
- **Phase 2 中的 T017-T020**：CDP 工具函式，可 4 人並行
- **Phase 3 中的 T033-T037**：頁面監控任務，可 5 人並行
- **Phase 6：US3 與 US6** 完全獨立，可 2 個團隊並行
- **Phase 9 中的 T147-T153**：平台遷移任務，可並行（不同平台）
- **Phase 10 中的 T156-T173**：測試與文件，大多數獨立，可多人並行

### 關鍵里程碑檢查點

1. **Milestone 1**：Phase 2 完成
   - 驗證：CDP 標準工具函式可運作
   - 驗證：perform_search() 可穿透 Shadow DOM
   - 驗證：dispatch_mouse_event() 可點擊元素

2. **Milestone 2**：Phase 5 完成（MVP）
   - 驗證：TixCraft 完整購票流程可運作
   - 驗證：關鍵字匹配與回退策略正常
   - 驗證：CDP 原生重試機制正常

3. **Milestone 3**：Phase 9 完成
   - 驗證：所有平台遷移到 CDP 原生方法
   - 驗證：程式碼稽核通過（無 JavaScript 執行）

4. **Milestone 4**：Phase 10 完成（生產就緒）
   - 驗證：所有 NFR 達標
   - 驗證：反偵測測試通過
   - 驗證：效能目標達成（2-5秒、95%+ 成功率）

---

## 任務覆蓋統計

| 指標 | 數值 |
|------|------|
| **總任務數** | 173 |
| **Setup 任務** | 10 |
| **Foundational 任務** | 15 (含 4 個 CDP 工具任務) |
| **US1 任務** | 33 |
| **US2 任務** | 16 |
| **US7 任務** | 13 |
| **US3 任務** | 10 |
| **US6 任務** | 17 |
| **US4 任務** | 13 |
| **US5 任務** | 19 |
| **TDR-004 遷移任務** | 9 |
| **NFR 驗證任務** | 18 |
| **可並行執行的任務** | ~70 (40%) |
| **預計完成時間** | 7-9 週（6 人團隊） |

### 需求覆蓋率

| 需求類型 | 總數 | 有任務覆蓋 | 覆蓋率 |
|---------|------|-----------|--------|
| **功能需求 (FR)** | 64 | 64 | **100%** ✅ |
| **非功能需求 (NFR)** | 7 | 7 | **100%** ✅ |
| **TDR-004 要求** | 5 | 5 | **100%** ✅ |
| **憲章原則** | 8 | 8 | **100%** ✅ |

---

**生成日期**：2025-10-27
**更新原因**：涵蓋 TDR-004 技術決策與 NFR-001~NFR-007
**計劃分支**：`001-ticket-automation-system`
**下一步**：執行 `/speckit.implement` 開始實作