# 功能規格：HKTicketing NoDriver 遷移

**功能分支**：`008-hkticketing-nodriver`
**建立日期**：2025-11-27
**狀態**：草稿
**輸入**：使用者描述："把 HKTicketing 從 chrome UC driver 遷移到 nodriver_tixcraft.py，重構為 nodriver 版本，保持原始頁面判斷邏輯，更改為 nodriver API 或 nodriver CDP 來處理原始的 UC 程式邏輯"

## 使用者情境與測試 *（強制）*

### 使用者故事 1 - HKTicketing 日期自動選擇（優先順序：P1）

使用者設定日期關鍵字後，程式可在活動頁面自動選擇符合關鍵字的場次日期，並自動點擊購買按鈕。

**為何此優先順序**：日期選擇是搶票的核心功能，決定能否成功進入購票流程，為最高優先級。

**獨立測試**：可透過導航到 HKTicketing 活動頁面，驗證日期選擇與購買按鈕點擊功能，交付日期自動選擇價值。

**驗收情境**：

1. **給定** 活動頁面有多個可選日期且使用者設定了日期關鍵字，**當** 程式載入頁面，**則** 自動選擇符合關鍵字的日期並點擊購買按鈕
2. **給定** 活動頁面需要密碼驗證，**當** 程式偵測到密碼輸入框，**則** 使用 user_guess_string 自動嘗試填入密碼
3. **給定** 頁面尚未載入完成（選項為空），**當** auto_reload_coming_soon_page 啟用，**則** 自動重載頁面
4. **給定** 所有關鍵字日期都已售完，**當** 程式嘗試選擇，**則** 根據 auto_select_mode 選擇其他可用日期
5. **給定** 所有日期關鍵字都無法匹配且 `date_auto_fallback=true`，**當** 程式完成關鍵字匹配，**則** 自動使用 `auto_select_mode` 從所有可用日期中選擇（自動遞補）
6. **給定** 所有日期關鍵字都無法匹配且 `date_auto_fallback=false`，**當** 程式完成關鍵字匹配，**則** 停止日期選擇流程（嚴格模式，避免誤購）

---

### 使用者故事 2 - HKTicketing 區域/票價自動選擇（優先順序：P1）

使用者設定區域關鍵字後，程式可在選票頁面自動選擇符合關鍵字的票價區域。

**為何此優先順序**：區域選擇是購票流程的核心步驟，決定最終座位區域，與日期選擇同為最高優先級。

**獨立測試**：可透過導航到 HKTicketing 選票頁面，驗證區域選擇功能，交付區域自動選擇價值。

**驗收情境**：

1. **給定** 選票頁面有多個票價區域且使用者設定了區域關鍵字，**當** 程式載入頁面，**則** 自動選擇符合關鍵字的區域
2. **給定** 使用者設定了排除關鍵字（如「輪椅」「身障」），**當** 程式匹配區域，**則** 排除含有這些關鍵字的區域
3. **給定** 所有關鍵字區域都不可用（disabled/unavailable），**當** 程式嘗試選擇，**則** 根據 auto_select_mode 選擇其他可用區域
4. **給定** 已有區域被選中（selected 狀態），**當** 程式載入頁面，**則** 跳過區域選擇步驟
5. **給定** 所有區域關鍵字都無法匹配且 `area_auto_fallback=true`，**當** 程式完成關鍵字匹配，**則** 自動使用 `auto_select_mode` 從所有可用區域中選擇（自動遞補）
6. **給定** 所有區域關鍵字都無法匹配且 `area_auto_fallback=false`，**當** 程式完成關鍵字匹配，**則** 停止區域選擇流程（嚴格模式，避免誤購）

---

### 使用者故事 3 - HKTicketing 票數自動設定與訂單送出（優先順序：P1）

程式在區域選擇後自動設定購票張數，選擇取票方式，並點擊下一步按鈕完成訂單送出。

**為何此優先順序**：票數設定和訂單送出是完成購票的必要步驟，為核心功能。

**獨立測試**：可透過在選票頁面驗證票數設定、取票方式選擇和下一步按鈕點擊功能。

**驗收情境**：

1. **給定** 票數設定為 2 張，**當** 程式完成區域選擇，**則** 自動將票數下拉選單設定為 2
2. **給定** 頁面有取票方式選項，**當** 程式完成票數設定，**則** 自動選擇預設取票方式
3. **給定** 區域和票數已選擇完成，**當** 程式完成設定，**則** 自動點擊下一步按鈕
4. **給定** 導航到座位圖頁面（seatmap），**當** 程式載入頁面，**則** 自動點擊前往付款按鈕

---

### 使用者故事 4 - HKTicketing 自動登入（優先順序：P2）

使用者設定 HKTicketing 帳號密碼後，程式可在登入頁面自動填入帳號並輸入密碼，完成登入流程。

**為何此優先順序**：登入功能是購票流程的前置條件，但使用者也可以手動登入，因此為 P2。

**獨立測試**：可透過導航到 HKTicketing 登入頁面，驗證帳號密碼自動填入功能，交付自動登入價值。

**驗收情境**：

1. **給定** 使用者已設定有效的 HKTicketing 帳號密碼，**當** 程式導航到登入頁面，**則** 帳號密碼欄位自動填入並嘗試登入
2. **給定** 使用者未設定帳號密碼，**當** 程式導航到登入頁面，**則** 程式跳過登入流程，等待手動操作

---

### 使用者故事 5 - HKTicketing 頁面重定向與錯誤處理（優先順序：P2）

程式能自動處理排隊頁面、錯誤頁面的重定向，以及偵測並繞過機器人檢測。

**為何此優先順序**：錯誤處理提升穩定性，但不影響主要購票流程，為次要優先級。

**獨立測試**：可透過模擬各種錯誤頁面場景，驗證重定向功能。

**驗收情境**：

1. **給定** 導航到排隊頁面（queue.hkticketing.com），**當** 程式偵測到排隊頁面，**則** 自動重定向到入口頁面
2. **給定** 頁面顯示錯誤訊息（Access Denied、503 等），**當** 程式偵測到錯誤內容，**則** 自動重新載入或重定向
3. **給定** 偵測到 iframe 中的錯誤內容，**當** 程式遍歷 iframe，**則** 能正確識別並處理錯誤

---

### 使用者故事 6 - Cookie 同意處理（優先順序：P3）

程式能自動關閉 Cookie 同意彈窗。

**為何此優先順序**：Cookie 彈窗是次要障礙，不影響主要購票流程。

**獨立測試**：可透過導航到 HKTicketing 首頁，驗證 Cookie 彈窗自動關閉功能。

**驗收情境**：

1. **給定** 頁面顯示 Cookie 同意彈窗，**當** 程式偵測到彈窗，**則** 自動點擊接受按鈕關閉彈窗

---

### 邊界案例

- 當網路延遲導致頁面元素載入緩慢時，NoDriver 應使用適當的等待機制（asyncio.sleep 或輪詢）
- 當 HKTicketing 網站更新 DOM 結構時，CSS 選擇器應有足夠的彈性或清楚的錯誤提示
- 當同時開啟多個分頁時，程式應能正確識別並操作目標分頁
- 當遇到驗證碼（reCAPTCHA）時，程式應等待使用者手動處理
- 當 Galaxy Macau 子網站使用不同的 URL 結構時，程式應能正確識別並處理
- 當設定的票數大於剩餘可購票數時，應選擇最大可用張數

## 需求 *（強制）*

### 功能需求

#### 核心遷移需求

- **FR-001**：系統必須將 18 個 HKTicketing UC Driver 函數遷移到 NoDriver 版本，使用 async/await 語法
- **FR-002**：系統必須使用 NoDriver 的 `tab.query_selector()` 和 `tab.query_selector_all()` 取代 Selenium 的 `find_element()` 和 `find_elements()`
- **FR-003**：系統必須使用 `await tab.evaluate()` 取代 Selenium 的 `driver.execute_script()`
- **FR-004**：系統必須使用 `await element.send_keys()` 處理文字輸入
- **FR-005**：系統必須使用 `await tab.get()` 取代 Selenium 的 `driver.get()` 進行頁面導航
- **FR-006**：系統必須使用 `await tab.get_content()` 取代 Selenium 的 `driver.page_source` 獲取頁面內容
- **FR-007**：系統必須重用 `util.py` 中的共用函數（`get_matched_blocks_by_keyword`、`get_target_item_from_matched_list`、`reset_row_text_if_match_keyword_exclude`、`format_keyword_string`、`remove_html_tags`）

#### 登入功能（階段 2）

- **FR-010**：系統必須在登入頁面自動填入帳號（CSS: `div.loginContentContainer > input.borInput`）
- **FR-011**：系統必須在帳號填入後自動填入密碼（CSS: `div.loginContentContainer > input[type="password"]`）
- **FR-012**：系統必須在密碼填入後模擬按下 Enter 鍵提交登入

#### 日期選擇功能（階段 4）

- **FR-020**：系統必須能識別日期下拉選單（CSS: `#p`）並解析所有選項（CSS: `#p > option`）
- **FR-021**：系統必須過濾已售完的日期選項（包含 `Exhausted`、`配售完畢`、`配售完毕`、`No Longer On Sale`、`已停止發售`、`已停止发售` 等文字）
- **FR-022**：系統必須使用 `util.get_matched_blocks_by_keyword()` 進行日期關鍵字匹配
- **FR-023**：系統必須在日期選擇後自動點擊購買按鈕（CSS: `#buyButton > input`）
- **FR-024**：系統必須支援密碼保護的活動頁面（CSS: `#entitlementPassword > div > div > div > div > input[type='password']`）
- **FR-025**：系統必須根據 `auto_reload_coming_soon_page` 設定自動重載頁面
- **FR-026**：系統必須支援 `date_auto_fallback` 設定：當所有日期關鍵字匹配失敗時，若 `date_auto_fallback=true` 則使用 `auto_select_mode` 自動遞補選擇；若 `date_auto_fallback=false` 則停止日期選擇流程

#### 區域選擇功能（階段 5）

- **FR-030**：系統必須能識別票價區域列表（CSS: `#ticketSelectorContainer > ul > li`）
- **FR-031**：系統必須過濾不可用的區域（class 包含 `disabled` 或 `unavailable`）
- **FR-032**：系統必須識別已選中的區域（class 包含 `selected`）並跳過選擇
- **FR-033**：系統必須使用 `util.reset_row_text_if_match_keyword_exclude()` 排除不要的區域
- **FR-034**：系統必須支援 AND 邏輯的關鍵字匹配（空格分隔的關鍵字需全部命中）
- **FR-035**：系統必須在找不到匹配區域時根據設定觸發頁面重載
- **FR-036**：系統必須支援 `area_auto_fallback` 設定：當所有區域關鍵字匹配失敗時，若 `area_auto_fallback=true` 則使用 `auto_select_mode` 自動遞補選擇；若 `area_auto_fallback=false` 則停止區域選擇流程

#### 票數設定功能（階段 6）

- **FR-040**：系統必須能識別票數下拉選單（CSS: `select.shortSelect`）
- **FR-041**：系統必須使用共用函數 `assign_ticket_number_by_select()` 設定票數（需確認 NoDriver 版本相容性）

#### 訂單送出功能（階段 10）

- **FR-050**：系統必須能識別並點擊下一步按鈕（CSS: `#continueBar > div.chooseTicketsOfferDiv > button`）
- **FR-051**：系統必須在點擊前先滾動到頁面底部（導航到 `#wrapFooter` 元素）
- **FR-052**：系統必須支援取票方式選擇（CSS: `#selectDeliveryType`，預設值為 "1"）
- **FR-053**：系統必須能識別並點擊前往付款按鈕（CSS: `#goToPaymentButton`）

#### 頁面重定向與錯誤處理（階段 12）

- **FR-060**：系統必須識別排隊頁面（queue.hkticketing.com、detection.aspx、busy_galaxy、hot*.ticketek.com.au）並自動重定向
- **FR-061**：系統必須識別各種錯誤內容（Access Denied、Service Unavailable、HTTP Error 500/503、504 Gateway Time-out、502 Bad Gateway 等）並自動重載
- **FR-062**：系統必須能遍歷 iframe 內容進行錯誤檢測
- **FR-063**：系統必須識別機器人檢測頁面（`#main-iframe` 存在）
- **FR-064**：系統必須支援 Galaxy Macau 子網站的 URL 處理（ticketing.galaxymacau.com）
- **FR-065**：系統必須支援 ticketek.com.au 子網站的 URL 處理

#### Cookie 處理（階段 3）

- **FR-070**：系統必須能識別並關閉 Cookie 同意彈窗（CSS: `#closepolicy_new`）

### 關鍵實體 *（如功能涉及資料則包含）*

- **hkticketing_dict**：儲存 HKTicketing 平台的狀態資訊，包含：
  - `is_date_submiting`（bool）：是否正在提交日期選擇
  - `fail_list`（list）：密碼嘗試失敗清單，用於避免重複嘗試相同密碼
  - `played_sound_ticket`（bool）：是否已播放票券音效
  - `played_sound_order`（bool）：是否已播放訂單音效

- **config_dict（fallback 相關設定）**：從 settings.json 讀取的遞補設定，包含：
  - `date_auto_fallback`（bool，預設 False）：日期關鍵字全失敗時，是否自動使用「日期排序方式」選擇
  - `area_auto_fallback`（bool，預設 False）：區域關鍵字全失敗時，是否自動使用「區域排序方式」選擇
  - `date_auto_select.mode`（str）：日期排序方式（from top to bottom、from bottom to top、center、random）
  - `area_auto_select.mode`（str）：區域排序方式（from top to bottom、from bottom to top、center、random）

## 成功標準 *（強制）*

### 可衡量結果

- **SC-001**：遷移後的 NoDriver 版本必須能成功完成完整的購票流程（日期選擇 → 區域選擇 → 票數設定 → 訂單送出）
- **SC-002**：日期關鍵字匹配功能必須與 UC Driver 版本行為一致，達到 90% 以上的匹配成功率
- **SC-003**：區域關鍵字匹配功能必須與 UC Driver 版本行為一致，支援 AND 邏輯匹配和排除關鍵字
- **SC-004**：頁面重定向功能必須能處理所有原版本支援的錯誤類型（至少 15 種錯誤訊息）
- **SC-005**：遷移後的功能必須能在 HKTicketing、Galaxy Macau 和 ticketek.com.au 三個網站上正常運作
- **SC-006**：程式碼必須遵循專案現有的 NoDriver 實作模式（參考 nodriver_cityline_main 實作）
- **SC-007**：所有函數必須使用 async/await 語法，並以 `nodriver_hkticketing_` 作為函數名稱前綴

## 假設與約束

### 假設

- HKTicketing 網站的 DOM 結構在遷移期間保持穩定
- NoDriver API 的 `tab.query_selector()` 和 `tab.evaluate()` 方法足以取代所有 Selenium 操作
- 專案已有完整的 NoDriver 基礎架構，無需額外設定
- `util.py` 中的工具函數（`get_matched_blocks_by_keyword`、`reset_row_text_if_match_keyword_exclude` 等）可在 NoDriver 環境中正常運作（可能需要調整為處理非 WebElement 物件）

### 約束

- 必須遵循專案憲法的「NoDriver First」原則
- 遷移後的程式碼必須整合到現有的 `nodriver_tixcraft.py` 檔案中
- 必須維持與 `settings.json` 設定檔的相容性
- 程式碼中禁止使用 emoji（避免 Windows cp950 編碼錯誤）
- 必須保持與原 UC Driver 版本相同的頁面判斷邏輯和 URL 路由

## 待遷移函數清單（18 個）

| 序號 | 原函數名稱 | NoDriver 函數名稱 | 12 階段分類 | 優先級 |
|------|----------|------------------|------------|-------|
| 1 | `hkticketing_login` | `nodriver_hkticketing_login` | 階段 2 - 身份認證 | P2 |
| 2 | `hkticketing_accept_cookie` | `nodriver_hkticketing_accept_cookie` | 階段 3 - 彈窗處理 | P3 |
| 3 | `hkticketing_date_buy_button_press` | `nodriver_hkticketing_date_buy_button_press` | 階段 4 - 日期選擇 | P1 |
| 4 | `hkticketing_date_assign` | `nodriver_hkticketing_date_assign` | 階段 4 - 日期選擇 | P1 |
| 5 | `hkticketing_date_password_input` | `nodriver_hkticketing_date_password_input` | 階段 4 - 日期選擇 | P1 |
| 6 | `hkticketing_date_auto_select` | `nodriver_hkticketing_date_auto_select` | 階段 4 - 日期選擇 | P1 |
| 7 | `hkticketing_area_auto_select` | `nodriver_hkticketing_area_auto_select` | 階段 5 - 區域選擇 | P1 |
| 8 | `hkticketing_ticket_number_auto_select` | `nodriver_hkticketing_ticket_number_auto_select` | 階段 6 - 票數設定 | P1 |
| 9 | `hkticketing_nav_to_footer` | `nodriver_hkticketing_nav_to_footer` | 階段 10 - 訂單送出 | P1 |
| 10 | `hkticketing_next_button_press` | `nodriver_hkticketing_next_button_press` | 階段 10 - 訂單送出 | P1 |
| 11 | `hkticketing_go_to_payment` | `nodriver_hkticketing_go_to_payment` | 階段 10 - 訂單送出 | P1 |
| 12 | `hkticketing_ticket_delivery_option` | `nodriver_hkticketing_ticket_delivery_option` | 階段 10 - 訂單送出 | P1 |
| 13 | `hkticketing_hide_tickets_blocks` | `nodriver_hkticketing_hide_tickets_blocks` | 階段 3 - 頁面優化 | P3 |
| 14 | `hkticketing_performance` | `nodriver_hkticketing_performance` | 階段 5/6/10 - 整合流程 | P1 |
| 15 | `hkticketing_escape_robot_detection` | `nodriver_hkticketing_escape_robot_detection` | 階段 12 - 錯誤處理 | P2 |
| 16 | `hkticketing_url_redirect` | `nodriver_hkticketing_url_redirect` | 階段 12 - 錯誤處理 | P2 |
| 17 | `hkticketing_content_refresh` | `nodriver_hkticketing_content_refresh` | 階段 12 - 錯誤處理 | P2 |
| 18 | `hkticketing_travel_iframe` | `nodriver_hkticketing_travel_iframe` | 階段 12 - 錯誤處理 | P2 |
| 19 | `softix_powerweb_main` | `nodriver_hkticketing_main` | 主流程控制 | P1 |
