# 功能規格：FunOne Tickets 平台支援

**功能分支**：`011-funone-platform`
**建立日期**：2026-01-12
**狀態**：草稿
**輸入**：使用者描述："FunOne 平台支援的計畫 - 購票流程自動化（首頁 → 活動詳情 → 選擇場次 → 登入檢查 → 選票（票種+張數+驗證碼）→ 付款 → 完成）"

## 使用者情境與測試 *（強制）*

### 使用者故事 1 - Cookie 快速登入（優先順序：P1）

使用者透過手動登入 FunOne 網站後，匯出 `ticket_session` Cookie 並設定到程式中，程式可在下次啟動時自動注入 Cookie 完成快速登入，無需重複 OTP 驗證。

**為何此優先順序**：FunOne 使用 OTP 登入機制（無傳統帳號密碼），Cookie 快速登入是唯一可自動化的登入方式，為所有後續功能的前置條件。

**獨立測試**：可透過注入 `ticket_session` Cookie 後訪問會員中心頁面，驗證是否成功保持登入狀態，交付免 OTP 快速登入價值。

**驗收情境**：

1. **給定** 使用者已在設定中填入有效的 `ticket_session` Cookie，**當** 程式啟動並訪問 FunOne 網站，**則** 自動注入 Cookie 並維持登入狀態
2. **給定** Cookie 已過期（超過 24 小時），**當** 程式嘗試訪問需登入頁面，**則** 顯示提醒訊息告知使用者需更新 Cookie
3. **給定** 使用者未設定 Cookie，**當** 程式導航到需登入頁面，**則** 停留在登入頁面等待手動 OTP 登入

---

### 使用者故事 2 - 活動詳情頁場次選擇（優先順序：P1）

使用者設定活動連結後，程式可在活動詳情頁面自動識別並選擇符合條件的場次日期時間，然後點擊「下一步」按鈕進入購票流程。

**為何此優先順序**：場次選擇是購票流程的第一步，決定能否成功進入選票頁面，為核心功能。

**獨立測試**：可透過導航到活動詳情頁面，驗證場次選擇與下一步按鈕點擊功能，交付場次自動選擇價值。

**驗收情境**：

1. **給定** 活動頁面有多個可選場次且使用者設定了日期關鍵字，**當** 程式載入頁面，**則** 自動選擇符合關鍵字的場次並點擊下一步
2. **給定** 使用者未設定日期關鍵字，**當** 程式載入頁面，**則** 根據 `auto_select_mode` 設定自動選擇場次
3. **給定** 頁面場次尚未開放選擇（coming soon 狀態），**當** `auto_reload_coming_soon_page` 啟用，**則** 自動重載頁面直到場次開放
4. **給定** 所有關鍵字場次都已售完，**當** `date_auto_fallback=true`，**則** 使用 `auto_select_mode` 選擇其他可用場次
5. **給定** 所有關鍵字場次都無法匹配且 `date_auto_fallback=false`，**當** 程式完成關鍵字匹配，**則** 停止場次選擇流程（嚴格模式）

---

### 使用者故事 3 - 選票頁面票種張數選擇（優先順序：P1）

使用者設定票種關鍵字和購票張數後，程式可在選票頁面自動選擇票種、設定張數，並等待使用者手動完成驗證碼後點擊下一步。

**為何此優先順序**：票種選擇是購票流程的核心步驟，決定最終購買的票券類型和數量，為核心功能。

**獨立測試**：可透過導航到選票頁面，驗證票種選擇和張數設定功能，交付票種自動選擇價值。

**驗收情境**：

1. **給定** 選票頁面有多個票種且使用者設定了票種關鍵字，**當** 程式載入頁面，**則** 自動選擇符合關鍵字的票種
2. **給定** 使用者設定購買張數為 N 張，**當** 程式完成票種選擇，**則** 自動將張數設定為 N
3. **給定** 頁面顯示圖形驗證碼，**當** 程式偵測到驗證碼，**則** 播放提示音並等待使用者手動輸入
4. **給定** 所有關鍵字票種都不可用，**當** `area_auto_fallback=true`，**則** 使用 `auto_select_mode` 選擇其他可用票種
5. **給定** 使用者設定了排除關鍵字（如「身障」），**當** 程式匹配票種，**則** 排除含有這些關鍵字的票種
6. **給定** 設定的票數大於剩餘可購票數，**當** 程式設定張數，**則** 自動選擇最大可用張數

---

### 使用者故事 4 - 訂單確認與提交（優先順序：P2）

程式在票種選擇完成後，等待驗證碼輸入完畢後自動點擊提交按鈕完成訂單送出。

**為何此優先順序**：訂單提交是購票流程的最後自動化步驟，但主要依賴前面步驟完成，且付款需人工操作，為次要優先級。

**獨立測試**：可透過在選票頁面完成所有選擇後，驗證提交按鈕點擊功能。

**驗收情境**：

1. **給定** 票種、張數、驗證碼都已填入，**當** 程式偵測到可提交狀態，**則** 自動點擊提交按鈕
2. **給定** 提交成功進入付款頁面，**當** 程式偵測到付款頁面，**則** 播放成功音效提醒使用者手動完成付款

---

### 使用者故事 5 - 頁面狀態監控與錯誤處理（優先順序：P2）

程式能監控頁面狀態，自動處理錯誤頁面重載和異常情況。

**為何此優先順序**：錯誤處理提升系統穩定性，但不影響主要購票流程，為次要優先級。

**獨立測試**：可透過模擬各種錯誤頁面場景，驗證自動重載功能。

**驗收情境**：

1. **給定** 頁面顯示錯誤訊息（503、500 等），**當** 程式偵測到錯誤內容，**則** 自動重新載入頁面
2. **給定** WebSocket 連線斷開，**當** 程式偵測到斷線，**則** 嘗試自動重連
3. **給定** 頁面載入超時，**當** 程式偵測到超時，**則** 自動重新載入頁面

---

### 邊界案例

- 當網路延遲導致頁面元素載入緩慢時，NoDriver 應使用適當的等待機制
- 當 FunOne 網站更新 DOM 結構時，CSS 選擇器應有足夠的彈性或清楚的錯誤提示
- 當 Session 過期（24 小時）時，應清楚提示使用者需重新登入取得新 Cookie
- 當驗證碼辨識困難時，程式應保持等待狀態，不進行自動提交
- 當票券瞬間售完時，程式應能快速偵測並通知使用者
- 當同時開啟多個瀏覽器分頁時，程式應能正確識別並操作目標分頁

## 需求 *（強制）*

### 功能需求

#### 核心架構需求

- **FR-001**：系統必須建立 FunOne 平台的 NoDriver 自動化模組，遵循「NoDriver First」原則
- **FR-002**：系統必須整合到現有的 `nodriver_tixcraft.py` 主檔案中，使用 URL 路由機制識別 FunOne 頁面
- **FR-003**：所有函數必須使用 async/await 語法，並以 `nodriver_funone_` 作為函數名稱前綴
- **FR-004**：系統必須重用 `util.py` 中的共用函數（`get_matched_blocks_by_keyword`、`get_target_item_from_matched_list`、`format_keyword_string` 等）

#### Cookie 快速登入（階段 2）

- **FR-010**：系統必須支援透過 CDP `network.set_cookie` 注入 `ticket_session` Cookie
- **FR-011**：系統必須在每次頁面載入前檢查並注入 Cookie（確保登入狀態）
- **FR-012**：系統必須能偵測登入狀態失效（Cookie 過期）並提示使用者
- **FR-013**：Cookie 屬性必須設定為：domain=`tickets.funone.io`、path=`/`、httpOnly=`true`、secure=`false`

#### 活動詳情頁處理（階段 4）

- **FR-020**：系統必須識別活動詳情頁面 URL 模式（`/activity/activity_detail/{activityId}`）
- **FR-021**：系統必須識別場次選擇區塊並解析所有可選場次（日期、時間、場地）
- **FR-022**：系統必須使用 `util.get_matched_blocks_by_keyword()` 進行場次關鍵字匹配
- **FR-023**：系統必須過濾已售完或不可選的場次
- **FR-024**：系統必須在場次選擇後自動點擊「下一步」按鈕
- **FR-025**：系統必須支援 `date_auto_fallback` 設定控制關鍵字匹配失敗時的遞補行為

#### 選票頁面處理（階段 5-6）

- **FR-030**：系統必須識別選票頁面並解析所有票種選項
- **FR-031**：系統必須使用關鍵字匹配選擇目標票種
- **FR-032**：系統必須支援排除關鍵字過濾不要的票種
- **FR-033**：系統必須識別張數選擇元件並設定購票張數
- **FR-034**：系統必須支援 `area_auto_fallback` 設定控制票種匹配失敗時的遞補行為
- **FR-035**：系統必須偵測圖形驗證碼並等待使用者手動輸入

#### 訂單提交（階段 10）

- **FR-040**：系統必須偵測訂單可提交狀態（票種、張數、驗證碼都已填入）
- **FR-041**：系統必須在可提交狀態下自動點擊提交按鈕
- **FR-042**：系統必須偵測付款頁面並播放成功音效

#### 頁面監控與錯誤處理（階段 12）

- **FR-050**：系統必須識別各種錯誤頁面（503、500、網路錯誤等）並自動重載
- **FR-051**：系統必須支援 `auto_reload_coming_soon_page` 設定控制尚未開賣頁面的重載
- **FR-052**：系統必須維護 WebSocket 連線狀態（購票流程中）
- **FR-053**：系統必須處理頁面載入超時情況

### 關鍵實體 *（如功能涉及資料則包含）*

- **funone_dict**：儲存 FunOne 平台的執行狀態資訊，包含：
  - `is_session_selecting`（bool）：是否正在選擇場次
  - `is_ticket_selecting`（bool）：是否正在選擇票種
  - `played_sound_ticket`（bool）：是否已播放票券音效
  - `played_sound_order`（bool）：是否已播放訂單音效
  - `session_cookie_injected`（bool）：是否已注入 session cookie
  - `fail_list`（list）：失敗記錄列表
  - `start_time`（datetime）：開始時間
  - `reload_count`（int）：重載次數

- **config_dict（FunOne 相關設定）**：從 settings.json 讀取的設定，包含：
  - `funone_session_cookie`（str）：手動取得的 ticket_session Cookie 值
  - `ticket_number`（int）：購票張數（通用設定）
  - `date_keyword`（str）：場次日期關鍵字
  - `area_keyword`（str）：票種關鍵字
  - `keyword_exclude`（str）：排除關鍵字
  - `date_auto_fallback`（bool，預設 False）：場次關鍵字失敗時是否自動遞補
  - `area_auto_fallback`（bool，預設 False）：票種關鍵字失敗時是否自動遞補
  - `auto_select_mode`（str）：自動選擇模式（from top to bottom、random 等）

## 成功標準 *（強制）*

### 可衡量結果

- **SC-001**：Cookie 快速登入功能必須能在 3 秒內完成注入並驗證登入狀態
- **SC-002**：場次選擇功能必須能在頁面載入後 2 秒內完成場次識別和選擇
- **SC-003**：票種選擇功能必須能正確識別所有票種並完成關鍵字匹配，達到 90% 以上的匹配成功率
- **SC-004**：完整購票流程（場次選擇 → 票種選擇 → 等待驗證碼 → 提交）必須能在 10 秒內完成自動化步驟（不含驗證碼輸入時間）
- **SC-005**：錯誤頁面處理必須能在 1 秒內偵測並觸發重載
- **SC-006**：程式碼必須遵循專案現有的 NoDriver 實作模式和命名規範
- **SC-007**：所有功能必須通過手動測試驗證，在實際 FunOne 網站上正常運作

## 假設與約束

### 假設

- FunOne 網站的 DOM 結構在開發期間保持穩定
- Cookie 快速登入機制（已驗證可行）將持續有效
- WebSocket 連線機制可透過 NoDriver 正常維護
- 使用者願意手動登入一次以取得 `ticket_session` Cookie
- 圖形驗證碼需要人工輸入，程式不自動處理

### 約束

- 必須遵循專案憲法的「NoDriver First」原則
- 程式碼必須整合到現有的 `nodriver_tixcraft.py` 檔案中
- 必須維持與 `settings.json` 設定檔的相容性
- 程式碼中禁止使用 emoji（避免 Windows cp950 編碼錯誤）
- OTP 登入流程無法自動化（需手機接收驗證碼）
- 付款流程無法自動化（需信用卡 3D 驗證或超商付款）

---

## 12 階段標準對照表

依據 `docs/02-development/ticket_automation_standard.md` 定義的 12 階段標準，以下是 FunOne 平台的實作對照：

### 階段覆蓋摘要

| 階段 | 階段名稱 | FunOne 實作狀態 | 說明 |
|------|----------|----------------|------|
| 1 | 環境初始化 | 共用 | 使用現有 NoDriver 初始化機制 |
| 2 | 身份認證 | **必須實作** | Cookie 快速登入（無帳密登入） |
| 3 | 頁面監控與重載 | **必須實作** | 自動重載 + 彈窗處理 |
| 4 | 日期選擇 | **必須實作** | 場次選擇功能 |
| 5 | 區域/座位選擇 | **必須實作** | 票種選擇功能 |
| 6 | 票數設定 | **必須實作** | 張數設定功能 |
| 7 | 驗證碼處理 | **必須實作** | 圖形驗證碼等待（人工輸入） |
| 8 | 表單填寫 | 不適用 | FunOne 無自訂表單 |
| 9 | 同意條款處理 | 待確認 | 需實測確認是否有條款 |
| 10 | 訂單確認與送出 | **必須實作** | 提交按鈕點擊 |
| 11 | 排隊與付款 | 不適用 | FunOne 無排隊機制 |
| 12 | 錯誤處理與重試 | **必須實作** | 錯誤頁面處理 |

---

### 階段 1：環境初始化

**狀態**：共用現有機制

FunOne 使用專案現有的 NoDriver 初始化流程，無需平台特定實作。

**相關設定**：
- `config_dict["webdriver_type"]` = "nodriver"
- `config_dict["browser"]` = "chrome"

---

### 階段 2：身份認證

**狀態**：必須實作

**FunOne 特殊性**：
- 無傳統帳號密碼登入
- 僅支援手機 OTP 或 QPP 掃碼
- **解決方案**：Cookie 快速登入（已驗證可行）

**實作函數**：

```
nodriver_funone_login(tab, config_dict) -> bool
├── nodriver_funone_check_login_status(tab) -> bool
│   └── 檢查是否已登入（檢查「登入/註冊」按鈕是否存在）
├── nodriver_funone_inject_cookie(tab, session_cookie) -> bool
│   └── 使用 CDP network.set_cookie 注入 ticket_session
└── nodriver_funone_verify_login(tab) -> bool
    └── 重新整理後驗證登入狀態
```

**回退策略**：
1. **優先**：Cookie 注入（若有 `funone_session_cookie`）
2. **回退**：保持未登入狀態，等待手動 OTP 登入

**設定來源**：
- `config_dict["advanced"]["funone_session_cookie"]`
- `config_dict["ticket_number"]`（通用票券張數）

---

### 階段 3：頁面監控與重載

**狀態**：必須實作

**實作函數**：

```
nodriver_funone_auto_reload(tab, config_dict, funone_dict) -> bool
├── nodriver_funone_check_page_status(tab) -> str
│   ├── detect_coming_soon_page(tab) -> bool
│   ├── detect_error_page(tab) -> bool
│   └── detect_sold_out_page(tab) -> bool
├── calculate_reload_interval(config_dict, funone_dict) -> float
└── reload_with_backoff(tab, funone_dict) -> bool

nodriver_funone_close_popup(tab) -> bool
├── close_cookie_consent(tab) -> bool
└── close_announcement_popup(tab) -> bool
```

**回退策略**：
1. 按 `auto_reload_page_interval` 定期重載
2. 達到 `overheat_count` 時啟動冷卻時間
3. 若 `auto_reload_coming_soon_page=false`，不重載即將開賣頁面

**設定來源**：
- `config_dict["advanced"]["auto_reload_page_interval"]`
- `config_dict["advanced"]["auto_reload_overheat_count"]`
- `config_dict["tixcraft"]["auto_reload_coming_soon_page"]`

---

### 階段 4：日期選擇（場次選擇）

**狀態**：必須實作

**FunOne 特殊性**：
- 活動詳情頁面顯示場次列表
- 每個場次包含：日期、時間、場地資訊
- 點擊場次後需點擊「下一步」按鈕

**實作函數**：

```
nodriver_funone_date_auto_select(tab, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
├── get_all_session_options(tab) -> list
│   ├── parse_session_text(element) -> str
│   ├── parse_session_status(element) -> str  # "available"/"sold_out"
│   └── filter_sold_out_sessions(sessions, config_dict) -> list
├── match_session_by_keyword(sessions, config_dict) -> element
│   ├── split_keywords(keyword_string) -> list
│   └── match_fuzzy(session_text, keywords) -> bool
├── fallback_select_by_mode(sessions, mode) -> element
│   ├── select_from_top(sessions)
│   ├── select_from_bottom(sessions)
│   ├── select_center(sessions)
│   └── select_random(sessions)
├── click_session_element(tab, element) -> bool
├── click_next_button(tab) -> bool
└── verify_session_selected(tab) -> bool
```

**回退策略**（條件式遞補 v1.2）：
1. **優先策略**：使用 `date_keyword` 匹配（早期返回模式）
2. **條件式遞補**：
   - 若 `date_auto_fallback=false`（預設）：停止執行，等待手動介入
   - 若 `date_auto_fallback=true`：使用 `mode` 自動選擇
3. **功能禁用**：若 `enable=false` → 跳過場次選擇

**設定來源**：
- `config_dict["date_auto_select"]["enable"]`
- `config_dict["date_auto_select"]["date_keyword"]`
- `config_dict["date_auto_select"]["mode"]`
- `config_dict["date_auto_fallback"]`

---

### 階段 5：區域/座位選擇（票種選擇）

**狀態**：必須實作

**FunOne 特殊性**：
- 選票頁面顯示票種列表
- 每個票種包含：名稱、價格、剩餘數量
- 需排除不要的票種（如身障席）

**實作函數**：

```
nodriver_funone_area_auto_select(tab, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
├── get_all_ticket_types(tab) -> list
│   ├── parse_ticket_name(element) -> str
│   ├── parse_ticket_price(element) -> int
│   ├── parse_ticket_status(element) -> dict
│   └── filter_sold_out_types(types) -> list
├── apply_exclude_keywords(types, exclude_keywords) -> list
├── match_type_by_keyword(types, config_dict) -> element
│   ├── split_keywords(keyword_string) -> list
│   └── match_fuzzy(type_name, keywords) -> bool
├── fallback_select_by_mode(types, mode) -> element
├── click_type_element(tab, element) -> bool
└── verify_type_selected(tab) -> bool
```

**回退策略**（條件式遞補 v1.2）：
1. **優先策略**：先套用 `keyword_exclude`，再用 `area_keyword` 匹配
2. **條件式遞補**：
   - 若 `area_auto_fallback=false`（預設）：停止執行
   - 若 `area_auto_fallback=true`：使用 `mode` 自動選擇
3. **功能禁用**：若 `enable=false` → 跳過票種選擇

**設定來源**：
- `config_dict["area_auto_select"]["enable"]`
- `config_dict["area_auto_select"]["area_keyword"]`
- `config_dict["area_auto_select"]["mode"]`
- `config_dict["area_auto_fallback"]`
- `config_dict["keyword_exclude"]`

---

### 階段 6：票數設定

**狀態**：必須實作

**實作函數**：

```
nodriver_funone_assign_ticket_number(tab, config_dict) -> bool
├── detect_ticket_layout(tab) -> str
│   ├── detect_dropdown_layout() -> bool
│   └── detect_input_layout() -> bool
├── get_max_available(tab) -> int
├── calculate_actual_count(requested, max_available) -> int
├── select_ticket_number(tab, count) -> bool
│   ├── select_by_dropdown(tab, count)
│   └── input_by_textbox(tab, count)
└── verify_ticket_selected(tab, expected_count) -> bool
```

**回退策略**：
1. 若剩餘張數 < `ticket_number` → 選擇剩餘張數
2. 若無法設定 → 保持預設值

**設定來源**：
- `config_dict["ticket_number"]`

---

### 階段 7：驗證碼處理

**狀態**：必須實作

**FunOne 特殊性**：
- 圖形驗證碼在選票頁面出現
- 暫不支援 OCR 自動辨識
- 播放提示音等待人工輸入

**實作函數**：

```
nodriver_funone_captcha_handler(tab, config_dict) -> bool
├── detect_captcha_type(tab) -> str
│   └── detect_image_captcha() -> bool
├── play_captcha_sound(config_dict) -> bool
├── wait_for_captcha_input(tab, timeout) -> bool
│   └── check_captcha_filled(tab) -> bool
└── verify_captcha_correct(tab) -> bool
```

**回退策略**：
1. 偵測到驗證碼 → 播放提示音
2. 等待使用者手動輸入
3. 若超時 → 記錄錯誤，繼續等待

**設定來源**：
- `config_dict["advanced"]["play_sound"]["ticket"]`

---

### 階段 8：表單填寫

**狀態**：不適用

FunOne 購票流程無需填寫自訂表單（個人資訊已於註冊時填寫）。

---

### 階段 9：同意條款處理

**狀態**：待確認

需實測確認 FunOne 購票流程是否有同意條款。

**預設實作**：

```
nodriver_funone_ticket_agree(tab, config_dict) -> bool
├── find_agreement_elements(tab) -> list
├── check_all_agreements(tab, elements) -> bool
└── verify_agreements_checked(tab) -> bool
```

---

### 階段 10：訂單確認與送出

**狀態**：必須實作

**實作函數**：

```
nodriver_funone_order_submit(tab, config_dict, funone_dict) -> bool
├── review_order_details(tab) -> dict
│   └── verify_ticket_count(tab, expected) -> bool
├── find_submit_button(tab) -> element
├── click_submit_button(tab, element) -> bool
├── handle_confirmation_dialog(tab) -> bool
├── play_sound_notification(config_dict, "order") -> bool
└── verify_order_submitted(tab) -> bool
```

**回退策略**：
1. 若無法自動送出 → 等待使用者手動點擊
2. 送出成功 → 播放訂單音效

**設定來源**：
- `config_dict["advanced"]["play_sound"]["order"]`
- `config_dict["advanced"]["play_sound"]["filename"]`

---

### 階段 11：排隊與付款

**狀態**：不適用

FunOne 無排隊機制。付款頁面需使用者手動完成（信用卡 3D 驗證或全家 FamiPort）。

---

### 階段 12：錯誤處理與重試

**狀態**：必須實作

**實作函數**：

```
nodriver_funone_error_handler(tab, error, config_dict, funone_dict) -> bool
├── detect_error_type(tab, error) -> str
│   ├── detect_sold_out(tab) -> bool
│   ├── detect_timeout(error) -> bool
│   ├── detect_network_error(error) -> bool
│   └── detect_session_expired(tab) -> bool
├── log_error(error, config_dict) -> None
├── retry_with_strategy(func, max_retry, backoff) -> bool
└── notify_user(error_type, config_dict) -> None
    └── play_error_sound(filename)
```

**回退策略**：
1. 錯誤頁面 → 自動重載
2. Session 過期 → 提示使用者更新 Cookie
3. 連續失敗 → 記錄錯誤，通知使用者

**設定來源**：
- `config_dict["advanced"]["verbose"]`

---

## 實作函數完整清單

依據 12 階段標準整理的完整函數清單：

| 序號 | 函數名稱 | 12 階段 | 優先級 | 說明 |
|------|----------|---------|--------|------|
| 1 | `nodriver_funone_main` | 主流程 | P1 | URL 路由與主控制函數 |
| 2 | `nodriver_funone_inject_cookie` | 階段 2 | P1 | Cookie 快速登入 |
| 3 | `nodriver_funone_check_login_status` | 階段 2 | P1 | 檢查登入狀態 |
| 4 | `nodriver_funone_verify_login` | 階段 2 | P1 | 驗證登入成功 |
| 5 | `nodriver_funone_auto_reload` | 階段 3 | P2 | 自動重載頁面 |
| 6 | `nodriver_funone_close_popup` | 階段 3 | P3 | 關閉彈窗 |
| 7 | `nodriver_funone_date_auto_select` | 階段 4 | P1 | 場次自動選擇 |
| 8 | `nodriver_funone_area_auto_select` | 階段 5 | P1 | 票種自動選擇 |
| 9 | `nodriver_funone_assign_ticket_number` | 階段 6 | P1 | 票數設定 |
| 10 | `nodriver_funone_captcha_handler` | 階段 7 | P1 | 驗證碼處理 |
| 11 | `nodriver_funone_ticket_agree` | 階段 9 | P3 | 同意條款（待確認） |
| 12 | `nodriver_funone_order_submit` | 階段 10 | P2 | 訂單送出 |
| 13 | `nodriver_funone_error_handler` | 階段 12 | P2 | 錯誤處理 |

---

## 功能完整度預估評分

依據 12 階段標準的評分標準：

| 功能模組 | 權重 | FunOne 預估得分 | 說明 |
|---------|------|----------------|------|
| 主流程控制 | 10 分 | 10 分 | `nodriver_funone_main()` |
| 日期選擇 | 15 分 | 15 分 | 場次選擇 + 關鍵字 + mode 回退 |
| 區域選擇 | 15 分 | 15 分 | 票種選擇 + 排除關鍵字 |
| 票數設定 | 10 分 | 10 分 | 張數設定功能 |
| 驗證碼處理 | 10 分 | 7 分 | 僅支援人工輸入（無 OCR） |
| 同意條款 | 5 分 | 3 分 | 待確認是否需要 |
| 訂單送出 | 10 分 | 10 分 | 提交按鈕點擊 |
| 登入功能 | 10 分 | 10 分 | Cookie 快速登入 |
| 錯誤處理 | 5 分 | 5 分 | 完整錯誤處理 |
| 彈窗處理 | 5 分 | 3 分 | 基本彈窗處理 |
| 頁面重載 | 5 分 | 5 分 | 自動重載 + 過熱保護 |

**預估總分**：93/100 分（白金級）

---

## 參考資料

- 技術評估報告：`.temp/funone/nodriver-technical-assessment.md`
- Cookie 研究報告：`.temp/funone/cookie-login-research.md`
- NoDriver API 指南：`docs/06-api-reference/nodriver_api_guide.md`
- 12 階段標準：`docs/02-development/ticket_automation_standard.md`
