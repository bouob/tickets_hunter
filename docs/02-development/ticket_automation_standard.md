# 搶票自動化標準功能定義

**文件說明**：定義完整搶票程式的 12 階段標準架構、功能模組拆分規範與開發評估標準
**最後更新**：2025-11-12

---

> **目的**：定義完整的搶票程式應包含的功能模組與函式拆分規範，作為開發新平台或評估現有實作的標準

## 📋 核心設計原則

### 設定驅動 (Configuration-Driven)
所有功能行為由 `settings.json` 控制，使用者無需修改程式碼即可調整行為。

### 回退策略 (Fallback Strategy)
每個功能都有明確的優先策略與回退方案：
1. **優先策略**：使用使用者指定的關鍵字或參數
2. **回退策略 1**：關鍵字未命中時使用自動選擇模式
3. **回退策略 2**：功能禁用時跳過或等待手動操作

### 函式拆分原則
- **原子化**：每個函式只負責一個明確的任務
- **可組合**：函式可以組合成更複雜的工作流程
- **可測試**：函式輸入輸出明確，易於單元測試
- **可重用**：跨平台可共用的邏輯抽取為通用工具函式

---

## 🎯 完整功能架構（12 階段）

### 階段 1：環境初始化

#### 功能模組：WebDriver 初始化

**設定來源**：
```python
config_dict["webdriver_type"]                  # 驅動類型 (nodriver/chrome)
config_dict["browser"]                         # 瀏覽器類型
config_dict["advanced"]["headless"]            # 是否無頭模式
config_dict["advanced"]["window_size"]         # 視窗大小
config_dict["advanced"]["proxy_server_port"]   # 代理伺服器
config_dict["advanced"]["chrome_extension"]    # 是否載入擴充功能
```

**函式拆分**：
```
init_driver()
├── read_driver_config(config_dict) -> dict
│   └── 讀取驅動相關設定，返回設定字典
├── setup_chrome_options(config_dict) -> ChromeOptions
│   ├── set_headless_mode(headless: bool)
│   ├── set_window_size(size: str)
│   └── set_proxy(proxy_port: str)
├── load_extensions(extension_path: str) -> bool
│   └── 載入瀏覽器擴充功能
└── start_driver(webdriver_type: str, options: ChromeOptions) -> WebDriver
    ├── 根據 webdriver_type 啟動對應驅動
    └── 返回 WebDriver 實例
```

**回退策略**：
- **無自動回退**：當 `webdriver_type` 已指定時，僅使用該驅動類型
- 若指定的驅動初始化失敗 → 拋出錯誤並終止（不自動切換到其他驅動）
- **原因**：尊重使用者的明確選擇，不同驅動行為差異大，自動切換可能導致非預期結果
- **例外**：除非使用者在設定中明確啟用 `auto_fallback_driver` 選項

**函式命名規範**：
- 通用初始化：`init_driver()`
- 平台無關，不加 platform 前綴

---

### 階段 2：身份認證

#### 功能模組：自動登入

**設定來源**：
```python
config_dict["accounts"]["{platform}_account"]           # 帳號
config_dict["accounts"]["{platform}_password"]          # 密碼
config_dict["accounts"]["tixcraft_sid"]                # Cookie SID（拓元專用）
config_dict["accounts"]["ibonqware"]                   # Cookie qware（ibon專用）
config_dict["accounts"]["funone_session_cookie"]       # Cookie（FunOne 專用）
```

**函式拆分**：
```
{platform}_login(driver, config_dict) -> bool
├── check_login_status(driver) -> bool
│   └── 檢查是否已登入（檢查特定元素或 Cookie）
├── detect_login_method(config_dict) -> str
│   ├── 判斷使用 Cookie 注入（優先）
│   └── 判斷使用帳號密碼登入
├── inject_cookies(driver, sid: str, qware: str) -> bool
│   └── 注入 Cookie 實現快速登入
├── fill_credentials(driver, account: str, password: str) -> bool
│   ├── input_username(driver, account: str)
│   └── input_password(driver, password: str)
├── handle_login_captcha(driver, config_dict) -> bool
│   └── 處理登入驗證碼
├── click_login_button(driver) -> bool
└── verify_login_success(driver) -> bool
```

**回退策略**：
1. **優先**：Cookie 注入（若有 tixcraft_sid/ibonqware）
2. **回退 1**：帳號密碼登入（若有帳密）
3. **回退 2**：保持未登入狀態（部分平台可購票）

**函式命名規範**：
- 主函式：`{platform}_login()`，例如 `tixcraft_login()`、`kktix_login()`
- 子函式：使用通用名稱，可跨平台共用

---

### 階段 3：頁面監控與重載

#### 功能模組：自動重載頁面

**設定來源**：
```python
config_dict["advanced"]["auto_reload_page_interval"]    # 重載間隔（秒）
config_dict["advanced"]["auto_reload_overheat_count"]   # 過熱計數閾值
config_dict["advanced"]["auto_reload_overheat_cd"]      # 過熱冷卻時間（秒）
config_dict["advanced"]["reset_browser_interval"]       # 重置瀏覽器間隔（分鐘）
config_dict["tixcraft"]["auto_reload_coming_soon_page"] # 是否重載即將開賣頁面
```

**函式拆分**：
```
auto_reload_page(driver, config_dict, state_dict) -> bool
├── check_page_status(driver) -> str
│   ├── detect_coming_soon_page(driver) -> bool
│   ├── detect_queue_page(driver) -> bool
│   └── detect_error_page(driver) -> bool
├── calculate_reload_interval(config_dict, state_dict) -> float
│   └── 根據設定計算下次重載間隔
├── check_overheat_status(state_dict, threshold: int) -> bool
│   └── 檢查是否達到過熱閾值
├── reload_with_backoff(driver, state_dict) -> bool
│   ├── 執行頁面重載
│   └── 更新狀態字典（重載次數、時間戳等）
└── reset_browser_if_needed(driver, config_dict, state_dict) -> WebDriver
    └── 超過重置間隔時完全重啟瀏覽器
```

**回退策略**：
1. **優先**：按 `auto_reload_page_interval` 定期重載
2. **回退 1**：達到 `overheat_count` 時啟動冷卻時間
3. **回退 2**：若 `auto_reload_coming_soon_page=false`，不重載即將開賣頁面

**函式命名規範**：
- 通用功能：`auto_reload_page()`
- 平台無關，不加前綴

#### 功能模組：彈窗處理

**函式拆分**：
```
{platform}_close_popup_windows(driver) -> bool
├── detect_popup_types(driver) -> list
│   └── 偵測頁面上的彈窗類型
├── close_ad_popup(driver) -> bool
├── close_announcement_popup(driver) -> bool
├── accept_cookie_consent(driver) -> bool
└── handle_platform_specific_popup(driver) -> bool
```

**函式命名規範**：
- 主函式：`{platform}_close_popup_windows()`
- 可能需要平台特定實作

---

### 階段 4：日期選擇

#### 功能模組：自動選擇日期

**設定來源**：
```python
config_dict["date_auto_select"]["enable"]         # 是否啟用
config_dict["date_auto_select"]["date_keyword"]   # 日期關鍵字（支援多個，分號分隔）
config_dict["date_auto_select"]["mode"]           # 選擇模式
config_dict["date_auto_fallback"]                 # 條件式遞補開關 (v1.2+, 預設: false)
config_dict["tixcraft"]["pass_date_is_sold_out"]  # 是否跳過售完日期
```

**函式拆分**：
```
{platform}_date_auto_select(driver, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
│   └── 檢查 date_auto_select.enable
├── detect_date_layout(driver) -> str
│   ├── detect_button_layout() -> bool   # 按鈕式版面
│   ├── detect_dropdown_layout() -> bool # 下拉式版面
│   └── detect_calendar_layout() -> bool # 日曆式版面
├── get_all_date_options(driver, layout_type: str) -> list
│   ├── parse_date_text(element) -> str
│   ├── parse_date_status(element) -> str  # "available"/"sold_out"
│   └── filter_sold_out_dates(dates: list, config_dict) -> list
├── match_date_by_keyword(dates: list, config_dict) -> element
│   ├── split_keywords(keyword_string: str) -> list
│   │   └── 分割分號分隔的關鍵字，例如 "10/03;10/04"
│   ├── match_exact(date_text: str, keywords: list) -> bool
│   ├── match_fuzzy(date_text: str, keywords: list) -> float
│   └── apply_exclude_filter(dates: list, exclude_keywords: str) -> list
├── fallback_select_by_mode(dates: list, mode: str) -> element
│   ├── select_from_top(dates: list) -> element
│   ├── select_from_bottom(dates: list) -> element
│   ├── select_center(dates: list) -> element
│   └── select_random(dates: list) -> element
├── click_date_element(driver, element) -> bool
│   ├── click_by_javascript(driver, element)
│   └── click_by_cdp(tab, element)  # ZenDriver 專用
└── verify_date_selected(driver, selected_text: str) -> bool
```

**回退策略** (v1.2 更新為條件式遞補)：
1. **優先策略**：使用 `date_keyword` 匹配（早期返回模式）
   - 支援多關鍵字：`"10/03;10/04;10/05"`（分號分隔）
   - 依序嘗試每個關鍵字，**第一個匹配成功即停止**
   - 支援精確與模糊匹配
   - 關鍵字順序決定優先權

2. **條件式遞補策略** (v1.2+)：關鍵字全部失敗時
   - **若 `date_auto_fallback=false`（預設嚴格模式）**：
     - **停止執行**，不選擇任何日期
     - 等待使用者手動介入（避免誤購）
   - **若 `date_auto_fallback=true`（自動遞補模式）**：
     - 使用 `mode` 自動選擇可用日期
     - `"from top to bottom"` → 選第一個可用日期
     - `"from bottom to top"` → 選最後一個可用日期
     - `"center"` → 選中間的日期
     - `"random"` → 隨機選擇

3. **功能禁用策略**：若 `enable=false` → 跳過日期選擇，等待使用者手動操作

**重要變更 (v1.2)**：
- 舊版本：關鍵字失敗時**無條件自動遞補**至 mode 選擇
- 新版本：關鍵字失敗時根據 `date_auto_fallback` 決定是否遞補
- 預設為**嚴格模式** (false)，避免誤購不想要的場次

**函式命名規範**：
- 主函式：`{platform}_date_auto_select()`
- 例如：`tixcraft_date_auto_select()`, `kktix_date_auto_select()`

**輸入輸出規範**：
- **輸入**：
  - `driver` (WebDriver): 瀏覽器驅動實例
  - `url` (str): 當前頁面 URL
  - `config_dict` (dict): 設定字典
- **輸出**：
  - `bool`: 是否成功選擇日期

---

### 階段 5：區域/座位選擇

#### 功能模組：自動選擇區域

**設定來源**：
```python
config_dict["area_auto_select"]["enable"]           # 是否啟用
config_dict["area_auto_select"]["area_keyword"]     # 區域關鍵字（支援多個）
config_dict["area_auto_select"]["mode"]             # 選擇模式
config_dict["area_auto_fallback"]                   # 條件式遞補開關 (v1.2+, 預設: false)
config_dict["keyword_exclude"]                      # 排除關鍵字（分號分隔）
config_dict["advanced"]["disable_adjacent_seat"]    # 是否禁用相鄰座位
```

**函式拆分**：
```
{platform}_area_auto_select(driver, url, config_dict) -> bool
├── check_enable_status(config_dict) -> bool
├── detect_area_layout(driver) -> str
│   ├── detect_button_layout() -> bool       # 按鈕式版面
│   ├── detect_dropdown_layout() -> bool     # 下拉式版面
│   ├── detect_seat_map_layout() -> bool     # 座位圖式版面
│   └── detect_expansion_panel() -> bool     # 展開式面板（TicketPlus）
├── get_all_area_options(driver, layout_type: str) -> list
│   ├── parse_area_name(element) -> str
│   ├── parse_area_price(element) -> int
│   ├── parse_area_status(element) -> dict
│   │   └── 返回 {"status": "available"/"sold_out", "remaining": int}
│   └── filter_sold_out_areas(areas: list) -> list
├── apply_exclude_keywords(areas: list, exclude_keywords: str) -> list
│   └── filter_by_exclude_list(areas: list, keywords: list) -> list
│       └── 過濾掉包含「輪椅」「身障」「視線不良」等關鍵字的區域
├── match_area_by_keyword(areas: list, config_dict) -> element
│   ├── split_keywords(keyword_string: str) -> list
│   ├── match_exact(area_name: str, keywords: list) -> bool
│   ├── match_fuzzy(area_name: str, keywords: list) -> float
│   └── prioritize_by_price(matched_areas: list) -> list
├── fallback_select_by_mode(areas: list, mode: str) -> element
│   ├── select_from_top(areas: list)    # 通常是最貴的
│   ├── select_from_bottom(areas: list)
│   ├── select_center(areas: list)
│   └── select_random(areas: list)
├── handle_seat_map(driver, config_dict) -> bool
│   ├── auto_select_seats(driver, seat_count: int) -> list
│   ├── check_adjacent_seat(seats: list) -> bool
│   ├── allow_non_adjacent(driver) -> bool
│   └── confirm_seat_selection(driver) -> bool
├── click_area_element(driver, element) -> bool
└── verify_area_selected(driver, selected_text: str) -> bool
```

**回退策略** (v1.2 更新為條件式遞補)：
1. **優先策略**：使用 `area_keyword` 匹配（早期返回模式）
   - 先套用 `keyword_exclude` 排除不要的區域（輪椅、身障、視線不良等）
   - 支援多關鍵字：`"搖滾A;搖滾B;VIP"`（分號分隔）
   - 依序嘗試每個關鍵字，**第一個匹配成功即停止**
   - 關鍵字順序決定優先權
   - 若有多個匹配，可根據價格排序

2. **條件式遞補策略** (v1.2+)：關鍵字全部失敗時
   - **若 `area_auto_fallback=false`（預設嚴格模式）**：
     - **停止執行**，不選擇任何區域
     - 等待使用者手動介入（避免誤購不想要的座位）
   - **若 `area_auto_fallback=true`（自動遞補模式）**：
     - 使用 `mode` 自動選擇可用區域
     - `"from top to bottom"` → 選第一個可用區域（通常最貴）
     - `"from bottom to top"` → 選最後一個（通常最便宜）
     - `"center"` → 選中間區域
     - `"random"` → 隨機選擇

3. **功能禁用策略**：若 `enable=false` → 跳過區域選擇

**重要變更 (v1.2)**：
- 舊版本：關鍵字失敗時**無條件自動遞補**至 mode 選擇
- 新版本：關鍵字失敗時根據 `area_auto_fallback` 決定是否遞補
- 預設為**嚴格模式** (false)，避免誤購不想要的座位（如輪椅席、視線不良區）

**函式命名規範**：
- 主函式：`{platform}_area_auto_select()`
- 目標區域取得：`get_{platform}_target_area()`

---

### 階段 6：票數設定

#### 功能模組：自動設定票數

**設定來源**：
```python
config_dict["ticket_number"]  # 購票張數
```

**函式拆分**：
```
{platform}_assign_ticket_number(driver, config_dict) -> bool
├── detect_ticket_layout(driver) -> str
│   ├── detect_dropdown_layout() -> bool   # 下拉選單式
│   ├── detect_input_layout() -> bool      # 輸入框式
│   ├── detect_button_layout() -> bool     # 按鈕式（+/- 按鈕）
│   └── detect_price_list_layout() -> bool # 價格清單式（KKTIX）
├── get_ticket_types(driver, layout_type: str) -> list
│   ├── parse_ticket_name(element) -> str
│   ├── parse_ticket_price(element) -> int
│   └── parse_ticket_remaining(element) -> int
├── calculate_ticket_distribution(ticket_types: list, total_count: int) -> dict
│   └── distribute_to_types(types: list, count: int) -> dict
│       └── 將總票數分配到各票種（通常全分配給第一個票種）
├── select_ticket_number(driver, layout_type: str, count: int) -> bool
│   ├── select_by_dropdown(driver, count: int)
│   ├── input_by_textbox(driver, count: int)
│   ├── click_plus_button(driver, count: int)
│   └── fill_price_list(driver, distribution: dict)  # KKTIX 專用
└── verify_ticket_selected(driver, expected_count: int) -> bool
```

**回退策略**：
1. 若票種剩餘張數 < `ticket_number` → 選擇剩餘張數（最大可選）
2. 若有多票種 → 優先選擇第一個票種
3. 若無法設定 → 保持預設值（通常為 1）

**函式命名規範**：
- 主函式：`{platform}_assign_ticket_number()`
- 通用版本：`assign_ticket_number_by_select()` (跨平台共用)

---

### 階段 7：驗證碼處理

#### 功能模組：自動處理驗證碼

**設定來源**：
```python
config_dict["ocr_captcha"]["enable"]        # 是否啟用 OCR
config_dict["ocr_captcha"]["beta"]          # 是否使用 beta OCR 模式
config_dict["ocr_captcha"]["force_submit"]  # 是否強制送出
config_dict["ocr_captcha"]["image_source"]  # 圖片來源（canvas/img）
```

**函式拆分**：
```
{platform}_captcha_handler(driver, config_dict) -> bool
├── detect_captcha_type(driver) -> str
│   ├── detect_image_captcha() -> bool
│   ├── detect_recaptcha() -> bool
│   ├── detect_hcaptcha() -> bool
│   └── detect_cloudflare() -> bool
├── handle_image_captcha(driver, config_dict) -> bool
│   ├── get_captcha_image(driver, image_source: str) -> bytes
│   │   ├── get_from_canvas(driver) -> bytes
│   │   └── get_from_img_tag(driver) -> bytes
│   ├── ocr_recognize(image_data: bytes, use_beta: bool) -> str
│   │   ├── use_ddddocr(image: bytes) -> str
│   │   ├── use_beta_model(image: bytes) -> str
│   │   └── filter_result(text: str) -> str
│   ├── input_captcha_code(driver, code: str) -> bool
│   ├── submit_or_wait(driver, force_submit: bool) -> bool
│   │   ├── force_submit_form(driver)
│   │   └── wait_for_manual_confirm(driver)
│   ├── verify_result(driver) -> bool
│   └── retry_if_failed(driver, max_retry: int) -> bool
├── handle_recaptcha(driver) -> bool
├── reload_captcha(driver) -> bool
└── manual_input_fallback(driver, timeout: int) -> str
```

**回退策略**：
1. **優先策略**：若 `enable=true` → 自動 OCR 辨識
   - 使用 beta 模型（若 `beta=true`）
   - 辨識後強制送出（若 `force_submit=true`）
   - 辨識後等待手動確認（若 `force_submit=false`）

2. **回退策略 1**：若 `enable=false` → 等待手動輸入

3. **回退策略 2**：若 OCR 連續失敗 3 次以上 → 切換手動輸入模式

**函式命名規範**：
- 主處理函式：`{platform}_captcha()`, `{platform}_verify()`
- OCR 函式：`{platform}_auto_ocr()`, `{platform}_get_ocr_answer()`
- 輸入函式：`{platform}_keyin_captcha_code()`
- 重載函式：`{platform}_reload_captcha()`

---

### 階段 8：表單填寫

#### 功能模組：自動填寫購票資訊

**設定來源**：
```python
config_dict["advanced"]["user_guess_string"]    # 自訂問題答案
config_dict["advanced"]["auto_guess_options"]   # 是否自動猜測答案
```

**函式拆分**：
```
{platform}_form_auto_fill(driver, config_dict) -> bool
├── detect_form_fields(driver) -> list
│   ├── detect_input_fields(driver) -> list
│   ├── detect_dropdown_fields(driver) -> list
│   ├── detect_radio_fields(driver) -> list
│   └── detect_textarea_fields(driver) -> list
├── parse_field_requirements(fields: list) -> dict
│   ├── detect_required_fields(fields: list) -> list
│   └── parse_field_labels(field) -> str
├── fill_personal_info(driver, fields: list) -> bool
│   ├── fill_name(driver, field) -> bool
│   ├── fill_phone(driver, field) -> bool
│   ├── fill_email(driver, field) -> bool
│   ├── fill_id_number(driver, field) -> bool
│   └── fill_address(driver, field) -> bool
├── handle_custom_questions(driver, fields: list, config_dict) -> bool
│   ├── match_by_user_guess(question: str, user_guess: str) -> str
│   ├── auto_guess_answer(question: str, options: list) -> str
│   └── fill_answer(driver, field, answer: str) -> bool
└── verify_form_completed(driver, fields: list) -> bool
```

**回退策略**：
1. **優先策略**：使用 `user_guess_string` 填寫自訂問題答案
2. **回退策略 1**：若 `auto_guess_options=true` → 自動猜測並填寫
3. **回退策略 2**：若無法自動填寫 → 跳過非必填欄位，等待手動填寫必填欄位

**函式命名規範**：
- 主函式：`{platform}_form_auto_fill()` (若平台有此需求)
- 通用工具：`fill_input_text_with_retry()`

---

### 階段 9：同意條款處理

#### 功能模組：勾選同意條款

**設定來源**：
- 無特定設定，自動勾選所有同意條款

**函式拆分**：
```
{platform}_ticket_agree(driver, config_dict) -> bool
├── find_agreement_elements(driver) -> list
│   ├── find_checkboxes(driver) -> list
│   ├── find_radio_buttons(driver) -> list
│   └── find_toggle_buttons(driver) -> list
├── check_all_agreements(driver, elements: list) -> bool
│   ├── check_by_checkbox(driver, element)
│   ├── check_by_click(driver, element)
│   └── check_by_javascript(driver, element)
├── handle_special_dialogs(driver, config_dict) -> bool
│   ├── accept_realname_card(driver)          # TicketPlus 專用
│   ├── accept_other_activity(driver)         # TicketPlus 專用
│   └── accept_survey(driver)                 # Urbtix 專用
└── verify_agreements_checked(driver, elements: list) -> bool
```

**回退策略**：
- 若無法自動勾選 → 記錄錯誤，繼續執行（部分平台可能無條款）

**函式命名規範**：
- 主函式：`{platform}_ticket_agree()`, `{platform}_ticket_main_agree()`
- 特殊處理：`{platform}_accept_realname_card()`, `{platform}_accept_other_activity()`

---

### 階段 10：訂單確認與送出

#### 功能模組：確認並送出訂單

**設定來源**：
```python
config_dict["advanced"]["play_sound"]["ticket"]     # 是否播放票券音效
config_dict["advanced"]["play_sound"]["order"]      # 是否播放訂單音效
config_dict["advanced"]["play_sound"]["filename"]   # 音效檔名
config_dict["kktix"]["auto_press_next_step_button"] # 是否自動按下一步（KKTIX）
config_dict["kktix"]["max_dwell_time"]              # 最大停留時間（KKTIX）
```

**函式拆分**：
```
{platform}_order_submit(driver, config_dict) -> bool
├── review_order_details(driver) -> dict
│   ├── get_order_summary(driver) -> dict
│   ├── verify_ticket_count(driver, expected: int) -> bool
│   ├── verify_total_price(driver) -> int
│   └── log_order_info(order_info: dict)
├── find_submit_button(driver) -> element
│   ├── find_by_text(driver, text_list: list) -> element
│   ├── find_by_id(driver, id_list: list) -> element
│   └── find_by_class(driver, class_list: list) -> element
├── click_submit_button(driver, element) -> bool
│   ├── click_by_javascript(driver, element)
│   └── click_by_cdp(tab, element)  # ZenDriver 專用
├── handle_confirmation_dialog(driver) -> bool
├── play_sound_notification(config_dict, sound_type: str) -> bool
│   ├── check_play_condition(config_dict, sound_type) -> bool
│   └── play_audio_file(filename: str)
└── verify_order_submitted(driver) -> bool
```

**回退策略**：
1. 若無法自動送出 → 等待使用者手動點擊
2. 若 `auto_press_next_step_button=false` → 不自動點擊下一步

**函式命名規範**：
- 主函式：`{platform}_ticket_main()`, `{platform}_order()`
- 按鈕操作：`{platform}_press_next_button()`, `{platform}_purchase_button_press()`

---

### 階段 11：排隊與付款

#### 功能模組：處理排隊狀態

**設定來源**：
```python
config_dict["cityline"]["cityline_queue_retry"]  # 是否在排隊時自動重試（Cityline）
```

**函式拆分**：
```
{platform}_handle_queue(driver, config_dict) -> bool
├── detect_queue_page(driver) -> bool
│   ├── detect_waiting_room(driver) -> bool
│   ├── detect_queue_number(driver) -> int
│   └── detect_progress_bar(driver) -> int
├── parse_queue_info(driver) -> dict
│   ├── get_queue_position(driver) -> int
│   ├── get_estimated_time(driver) -> int
│   └── get_queue_status(driver) -> str
├── wait_in_queue(driver, config_dict, timeout: int) -> bool
│   ├── monitor_queue_status(driver) -> str
│   ├── auto_refresh_if_needed(driver, interval: int)
│   └── detect_queue_complete(driver) -> bool
└── handle_queue_timeout(driver, config_dict) -> bool
```

**回退策略**：
1. 若 `cityline_queue_retry=true` → 排隊失敗時自動重試
2. 若 `cityline_queue_retry=false` → 排隊失敗時停止

**函式命名規範**：
- 主函式：`{platform}_handle_queue()`, `{platform}_paused_main()`
- 重試函式：`{platform}_auto_retry_access()`

---

### 階段 12：錯誤處理與重試

#### 功能模組：全域錯誤處理

**設定來源**：
```python
config_dict["advanced"]["verbose"]  # 是否顯示詳細除錯訊息
```

**函式拆分**：
```
global_error_handler(driver, error, config_dict) -> bool
├── detect_error_type(error) -> str
│   ├── detect_sold_out(driver) -> bool
│   ├── detect_timeout(error) -> bool
│   ├── detect_network_error(error) -> bool
│   ├── detect_captcha_error(driver) -> bool
│   └── detect_system_error(error) -> bool
├── log_error(error, config_dict) -> None
│   ├── log_to_console(error, verbose: bool)
│   └── log_to_file(error, log_path: str)
├── retry_with_strategy(func, max_retry: int, backoff: float) -> bool
│   ├── calculate_backoff(attempt: int, base: float) -> float
│   ├── check_retry_limit(attempt: int, max_retry: int) -> bool
│   └── execute_retry(func, attempt: int) -> bool
└── notify_user(error_type: str, config_dict) -> None
    ├── play_error_sound(filename: str)
    └── display_error_message(message: str)
```

**函式命名規範**：
- 通用錯誤處理，不加平台前綴
- 特定錯誤檢查：`{platform}_check_sold_out()`, `{platform}_toast()`

---

## 🔧 跨階段通用工具函式

### 工具模組 1：元素查找與操作

**檔案位置**：`util.py`（已存在）

**函式拆分**：
```
element_utils
├── find_element_safe(driver, selector: str, method: str) -> element
│   ├── try_by_id(driver, id: str)
│   ├── try_by_xpath(driver, xpath: str)
│   ├── try_by_css(driver, css: str)
│   └── return_none_if_not_found()
├── wait_for_element(driver, selector: str, timeout: int) -> element
│   └── 等待元素出現，支援 Chrome 和 ZenDriver
├── click_element_safe(driver, element) -> bool
│   ├── try_standard_click(driver, element)
│   ├── try_javascript_click(driver, element)
│   └── try_cdp_click(tab, element)  # ZenDriver 專用
├── input_text_safe(driver, element, text: str) -> bool
│   ├── clear_and_input(element, text)
│   └── verify_input(element, expected: str)
└── execute_javascript(driver, script: str, *args) -> any
```

**命名規範**：
- 通用工具函式，不加平台前綴
- 名稱以動詞開頭：`find_`, `wait_for_`, `click_`, `input_`

---

### 工具模組 2：關鍵字匹配引擎

**檔案位置**：`util.py`（部分已存在，需擴充）

**函式拆分**：
```
keyword_matcher
├── match_by_keywords(text: str, keywords: str, mode: str) -> bool
│   ├── split_keywords(keyword_string: str) -> list
│   │   └── 分割分號分隔的關鍵字
│   ├── exact_match(text: str, keyword: str) -> bool
│   ├── fuzzy_match(text: str, keyword: str) -> float
│   │   └── 計算相似度分數
│   └── score_matches(matches: list) -> list
│       └── 根據匹配度排序
├── apply_exclude_filter(items: list, exclude_keywords: str) -> list
│   └── read_keyword_exclude(config_dict) -> list
└── select_by_priority(items: list, priority_rules: dict) -> element
    └── 根據優先度規則排序並選擇
```

**命名規範**：
- 已存在函式：`format_keyword_string()`, `is_all_alpha_or_numeric()`
- 新增函式：`match_keyword_by_and()`, `match_keyword_by_or()`

---

### 工具模組 3：設定讀取器

**檔案位置**：`util.py`（部分已存在）

**函式拆分**：
```
config_reader
├── read_config_safe(config_dict, key_path: list, default: any) -> any
│   ├── get_with_default(config_dict, keys: list, default)
│   └── handle_missing_key(key_path: list, default)
├── validate_config(config_dict, required_keys: list) -> bool
│   └── 驗證必要的設定項目是否存在
└── merge_platform_config(base_config: dict, platform: str) -> dict
    └── 合併平台特定設定與基礎設定
```

---

### 工具模組 4：狀態管理

**檔案位置**：各平台 main 函式內的 `{platform}_dict`

**標準結構**：
```python
{platform}_dict = {
    "fail_list": [],              # 失敗記錄列表
    "start_time": None,           # 開始時間
    "done_time": None,            # 完成時間
    "elapsed_time": None,         # 經過時間
    "played_sound_ticket": False, # 是否已播放票券音效
    "played_sound_order": False,  # 是否已播放訂單音效
    "reload_count": 0,            # 重載次數
    "last_reload_time": None,     # 上次重載時間
    "retry_count": 0              # 重試次數
}
```

**函式拆分**：
```
state_manager
├── init_state_dict(platform: str) -> dict
│   └── 初始化狀態字典
├── update_state(state_dict: dict, key: str, value: any) -> None
├── get_current_state(state_dict: dict, key: str) -> any
├── save_checkpoint(state_dict: dict, checkpoint_name: str) -> None
└── restore_checkpoint(state_dict: dict, checkpoint_name: str) -> dict
```

---

## 📊 完整設定項目索引表

### 基礎設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| homepage | `config_dict["homepage"]` | str | "" | 目標網址 |
| webdriver_type | `config_dict["webdriver_type"]` | str | "nodriver" | 驅動類型 (nodriver/chrome) |
| browser | `config_dict["browser"]` | str | "chrome" | 瀏覽器類型 |
| language | `config_dict["language"]` | str | "繁體中文" | 語言設定 |
| ticket_number | `config_dict["ticket_number"]` | int | 1 | 購票張數 |
| refresh_datetime | `config_dict["refresh_datetime"]` | str | "" | 刷新時間 |

### 日期選擇設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| enable | `config_dict["date_auto_select"]["enable"]` | bool | true | 是否啟用自動選擇日期 |
| date_keyword | `config_dict["date_auto_select"]["date_keyword"]` | str | "" | 日期關鍵字（支援多個，分號分隔） |
| mode | `config_dict["date_auto_select"]["mode"]` | str | "from top to bottom" | 選擇模式 |

**mode 可選值**：
- `"from top to bottom"` - 從上到下選擇（第一個）
- `"from bottom to top"` - 從下到上選擇（最後一個）
- `"center"` - 選擇中間
- `"random"` - 隨機選擇

### 區域選擇設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| enable | `config_dict["area_auto_select"]["enable"]` | bool | true | 是否啟用自動選擇區域 |
| area_keyword | `config_dict["area_auto_select"]["area_keyword"]` | str | "" | 區域關鍵字（支援多個，分號分隔） |
| mode | `config_dict["area_auto_select"]["mode"]` | str | "from top to bottom" | 選擇模式（同日期） |

### 關鍵字排除設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| keyword_exclude | `config_dict["keyword_exclude"]` | str | "" | 排除關鍵字（分號分隔），如"輪椅;身障" |

### 驗證碼設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| enable | `config_dict["ocr_captcha"]["enable"]` | bool | true | 是否啟用 OCR 自動辨識 |
| beta | `config_dict["ocr_captcha"]["beta"]` | bool | true | 是否使用 ddddocr beta 模型（fallback 時） |
| force_submit | `config_dict["ocr_captcha"]["force_submit"]` | bool | true | 辨識後是否強制送出 |
| image_source | `config_dict["ocr_captcha"]["image_source"]` | str | "canvas" | 圖片來源 (canvas/img) |
| use_universal | `config_dict["ocr_captcha"]["use_universal"]` | bool | true | 是否使用內建通用 OCR 模型（99-100% 準確率） |
| path | `config_dict["ocr_captcha"]["path"]` | str | "assets/model/universal" | 通用模型路徑 |

### 平台特定設定

#### KKTIX 設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| auto_press_next_step_button | `config_dict["kktix"]["auto_press_next_step_button"]` | bool | true | 是否自動按下一步 |
| auto_fill_ticket_number | `config_dict["kktix"]["auto_fill_ticket_number"]` | bool | true | 是否自動填寫票數 |
| max_dwell_time | `config_dict["kktix"]["max_dwell_time"]` | int | 90 | 最大停留時間（秒） |

#### Tixcraft 設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| pass_date_is_sold_out | `config_dict["tixcraft"]["pass_date_is_sold_out"]` | bool | true | 是否跳過售完日期 |
| auto_reload_coming_soon_page | `config_dict["tixcraft"]["auto_reload_coming_soon_page"]` | bool | true | 是否自動重載即將開賣頁面 |

#### Cityline 設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| cityline_queue_retry | `config_dict["cityline"]["cityline_queue_retry"]` | bool | true | 排隊失敗時是否重試 |

### 進階設定

#### 音效通知

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| ticket | `config_dict["advanced"]["play_sound"]["ticket"]` | bool | true | 選到票時播放音效 |
| order | `config_dict["advanced"]["play_sound"]["order"]` | bool | true | 送出訂單時播放音效 |
| filename | `config_dict["advanced"]["play_sound"]["filename"]` | str | "ding-dong.wav" | 音效檔名 |

#### 帳號密碼（各平台）

| 設定項目 | 設定路徑 | 類型 | 說明 |
|---------|---------|------|------|
| {platform}_account | `config_dict["accounts"]["{platform}_account"]` | str | 平台帳號 |
| {platform}_password | `config_dict["accounts"]["{platform}_password"]` | str | 密碼 |

**支援平台**：facebook, kktix, fami, cityline, urbtix, hkticketing, kham, ticket, udn, ticketplus, fansigo

#### Cookie 設定

| 設定項目 | 設定路徑 | 類型 | 說明 |
|---------|---------|------|------|
| tixcraft_sid | `config_dict["accounts"]["tixcraft_sid"]` | str | 拓元 Cookie SID |
| ibonqware | `config_dict["accounts"]["ibonqware"]` | str | ibon Cookie qware |
| funone_session_cookie | `config_dict["accounts"]["funone_session_cookie"]` | str | FunOne Cookie |
| fansigo_cookie | `config_dict["accounts"]["fansigo_cookie"]` | str | FANSI GO Cookie |

#### 瀏覽器設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| chrome_extension | `config_dict["advanced"]["chrome_extension"]` | bool | true | 是否載入擴充功能 |
| disable_adjacent_seat | `config_dict["advanced"]["disable_adjacent_seat"]` | bool | false | 是否禁用相鄰座位 |
| hide_some_image | `config_dict["advanced"]["hide_some_image"]` | bool | false | 是否隱藏部分圖片 |
| block_facebook_network | `config_dict["advanced"]["block_facebook_network"]` | bool | false | 是否阻擋 Facebook 網路請求 |
| headless | `config_dict["advanced"]["headless"]` | bool | false | 是否無頭模式 |
| window_size | `config_dict["advanced"]["window_size"]` | str | "600,1024" | 視窗大小 (寬,高) |

#### 自動重載設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| auto_reload_page_interval | `config_dict["advanced"]["auto_reload_page_interval"]` | float | 3.0 | 自動重載間隔（秒） |
| auto_reload_overheat_count | `config_dict["advanced"]["auto_reload_overheat_count"]` | int | 4 | 過熱計數閾值 |
| auto_reload_overheat_cd | `config_dict["advanced"]["auto_reload_overheat_cd"]` | float | 1.0 | 過熱冷卻時間（秒） |
| reset_browser_interval | `config_dict["advanced"]["reset_browser_interval"]` | int | 0 | 重置瀏覽器間隔（分鐘，0=不重置） |

#### 除錯設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| verbose | `config_dict["advanced"]["verbose"]` | bool | false | 是否顯示詳細除錯訊息 |
| show_timestamp | `config_dict["advanced"]["show_timestamp"]` | bool | false | 除錯訊息是否顯示時間戳記 `[HH:MM:SS]` |

#### 通知設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| discord_webhook_url | `config_dict["advanced"]["discord_webhook_url"]` | str | "" | Discord Webhook URL |
| telegram_bot_token | `config_dict["advanced"]["telegram_bot_token"]` | str | "" | Telegram Bot Token |
| telegram_chat_id | `config_dict["advanced"]["telegram_chat_id"]` | str | "" | Telegram Chat ID（支援多個，逗號分隔） |

#### 其他進階設定

| 設定項目 | 設定路徑 | 類型 | 預設值 | 說明 |
|---------|---------|------|--------|------|
| server_port | `config_dict["advanced"]["server_port"]` | int | 16888 | 設定介面 Web Server 埠號 |
| discount_code | `config_dict["advanced"]["discount_code"]` | str | "" | 優惠序號（TicketPlus、KKTIX 等活動用） |
| auto_guess_options | `config_dict["advanced"]["auto_guess_options"]` | bool | false | 是否自動猜測選項 |
| user_guess_string | `config_dict["advanced"]["user_guess_string"]` | str | "" | 使用者自訂答案字串 |
| proxy_server_port | `config_dict["advanced"]["proxy_server_port"]` | str | "" | 代理伺服器端口 |
| remote_url | `config_dict["advanced"]["remote_url"]` | str | "" | 遠端 WebDriver URL |
| idle_keyword | `config_dict["advanced"]["idle_keyword"]` | str | "" | 閒置關鍵字 |
| resume_keyword | `config_dict["advanced"]["resume_keyword"]` | str | "" | 恢復關鍵字 |

---

## 📝 函式命名規範總結

### 命名模式

1. **平台特定函式**：`{platform}_{function_name}()`
   - 例如：`tixcraft_date_auto_select()`, `kktix_login()`, `ticketplus_order()`

2. **通用工具函式**：直接使用功能名稱，不加平台前綴
   - 例如：`find_element_safe()`, `click_element_safe()`, `init_driver()`

3. **NoDriver 版本**：加上 `nodriver_` 前綴
   - 例如：`async nodriver_tixcraft_date_auto_select()`, `async nodriver_kktix_login()`

### 動詞選擇

- **取得資料**：`get_`, `parse_`, `detect_`, `find_`
- **操作元素**：`click_`, `input_`, `select_`, `fill_`
- **狀態檢查**：`check_`, `verify_`, `is_`, `has_`
- **處理邏輯**：`handle_`, `process_`, `apply_`
- **執行動作**：`auto_`, `execute_`, `perform_`

### 常見函式名稱

| 功能 | 函式名稱模式 | 範例 |
|-----|------------|------|
| 主流程 | `{platform}_main()` | `tixcraft_main()` |
| 日期選擇 | `{platform}_date_auto_select()` | `kktix_date_auto_select()` |
| 區域選擇 | `{platform}_area_auto_select()` | `ticketplus_area_auto_select()` |
| 票數設定 | `{platform}_assign_ticket_number()` | `tixcraft_assign_ticket_number()` |
| 驗證碼 | `{platform}_auto_ocr()` | `kham_auto_ocr()` |
| 登入 | `{platform}_login()` | `cityline_login()` |
| 同意條款 | `{platform}_ticket_agree()` | `ibon_ticket_agree()` |
| 送出訂單 | `{platform}_ticket_main()` | `tixcraft_ticket_main()` |

---

## 🎯 函式設計原則

### 1. 單一職責原則 (Single Responsibility)
每個函式只負責一個明確的任務。

**良好範例**：
```python
def get_all_date_options(driver):
    """只負責取得所有日期選項"""
    return driver.find_elements(By.CSS_SELECTOR, ".date-option")

def filter_sold_out_dates(dates, config_dict):
    """只負責過濾售完日期"""
    if config_dict["tixcraft"]["pass_date_is_sold_out"]:
        return [d for d in dates if "售完" not in d.text]
    return dates
```

**不良範例**：
```python
def get_and_filter_dates(driver, config_dict):
    """混合了取得和過濾兩個職責"""
    dates = driver.find_elements(By.CSS_SELECTOR, ".date-option")
    if config_dict["tixcraft"]["pass_date_is_sold_out"]:
        return [d for d in dates if "售完" not in d.text]
    return dates
```

### 2. 可組合性 (Composability)
小函式可以組合成大函式。

**範例**：
```python
def tixcraft_date_auto_select(driver, url, config_dict):
    """主函式組合多個小函式"""
    dates = get_all_date_options(driver)
    dates = filter_sold_out_dates(dates, config_dict)
    target = match_date_by_keyword(dates, config_dict)

    if not target:
        target = fallback_select_by_mode(dates, config_dict["date_auto_select"]["mode"])

    return click_date_element(driver, target)
```

### 3. 明確的輸入輸出 (Clear I/O)
函式的輸入參數和返回值應該明確且有文檔。

**範例**：
```python
def match_date_by_keyword(dates: list, config_dict: dict) -> element:
    """
    根據關鍵字匹配日期

    Args:
        dates (list): 日期元素列表
        config_dict (dict): 設定字典

    Returns:
        element: 匹配到的日期元素，若未匹配則返回 None
    """
    keyword = config_dict["date_auto_select"]["date_keyword"]
    for date in dates:
        if keyword in date.text:
            return date
    return None
```

### 4. 錯誤處理 (Error Handling)
每個函式都應該妥善處理可能的錯誤。

**範例**：
```python
def click_element_safe(driver, element):
    """安全點擊元素，包含多種回退方案"""
    try:
        element.click()
        return True
    except ElementClickInterceptedException:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as exc:
            if show_debug_message:
                print(f"Click failed: {exc}")
            return False
```

### 5. 設定驅動 (Configuration-Driven)
函式行為由設定控制，不寫死在程式碼中。

**良好範例**：
```python
def select_by_mode(items, mode):
    """根據 mode 選擇項目"""
    if mode == "from top to bottom":
        return items[0]
    elif mode == "from bottom to top":
        return items[-1]
    elif mode == "center":
        return items[len(items) // 2]
    elif mode == "random":
        return random.choice(items)
```

**不良範例**：
```python
def select_item(items):
    """寫死選擇邏輯"""
    return items[0]  # 永遠選第一個
```

---

## 📐 實作檢查清單

開發新平台時，應確保實作以下功能模組：

### 必要功能 (Must Have)
- [ ] 主流程控制：`{platform}_main()`
- [ ] 日期選擇：`{platform}_date_auto_select()`
- [ ] 區域選擇：`{platform}_area_auto_select()`
- [ ] 票數設定：`{platform}_assign_ticket_number()`
- [ ] 同意條款：`{platform}_ticket_agree()`
- [ ] 訂單送出：`{platform}_ticket_main()` 或 `{platform}_order()`

### 重要功能 (Should Have)
- [ ] 登入功能：`{platform}_login()`
- [ ] 驗證碼處理：`{platform}_auto_ocr()`, `{platform}_captcha()`
- [ ] 彈窗處理：`{platform}_close_popup_windows()`
- [ ] 頁面重載：`{platform}_auto_reload()` 或 `auto_reload_page()`

### 選擇性功能 (Nice to Have)
- [ ] 表單填寫：`{platform}_form_auto_fill()`
- [ ] 排隊處理：`{platform}_handle_queue()`
- [ ] 座位圖選座：`{platform}_seat_auto_select()`
- [ ] 問卷調查：`{platform}_auto_survey()`

### 平台特定功能 (Platform Specific)
- [ ] 實名制處理：`{platform}_accept_realname_card()`
- [ ] 特殊對話框：`{platform}_accept_other_activity()`
- [ ] 密碼輸入：`{platform}_date_password_input()`
- [ ] iframe 處理：`{platform}_travel_iframe()`

---

## 🔍 功能完整度評分標準

### 評分方式

**滿分：100 分**

| 功能模組 | 權重 | 說明 |
|---------|------|------|
| 主流程控制 | 10 分 | 必須有 `{platform}_main()` |
| 日期選擇 | 15 分 | 支援關鍵字 + mode 回退 |
| 區域選擇 | 15 分 | 支援關鍵字 + mode 回退 + 排除關鍵字 |
| 票數設定 | 10 分 | 能正確設定票數 |
| 驗證碼處理 | 10 分 | 支援 OCR + 手動輸入回退 |
| 同意條款 | 5 分 | 能自動勾選條款 |
| 訂單送出 | 10 分 | 能找到並點擊送出按鈕 |
| 登入功能 | 10 分 | 支援帳密或 Cookie 登入 |
| 錯誤處理 | 5 分 | 有完整的 try-except 和錯誤日誌 |
| 彈窗處理 | 5 分 | 能處理常見彈窗 |
| 頁面重載 | 5 分 | 支援自動重載與過熱保護 |

### 評分等級

- **90-100 分**：白金級 - 功能完整，可直接使用
- **80-89 分**：金級 - 核心功能完整，部分功能待補強
- **60-79 分**：銀級 - 基本可用，需要補充多個功能
- **40-59 分**：銅級 - 僅有框架，不建議使用
- **0-39 分**：未完成 - 需要重新實作

---

**文件版本**：v1.1
**最後更新**：2026-03-09
**相關文件**：
- [程式結構索引](./structure.md)
- [開發規範指南](./development_guide.md)
- [程式碼範本](./coding_templates.md)