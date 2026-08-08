# ZenDriver vs Chrome 函式結構分析與平台索引

**文件說明**：提供 Tickets Hunter 專案的模組結構、核心函數索引、平台實作分析與功能完整度評分
**最後更新**：2026-06-10

---

此文件整合了以下內容（以 ZenDriver 為主要開發目標）：
1. **標準功能架構** - 完整的搶票程式應包含的功能模組定義
2. **平台函數索引** - 快速定位各平台函數所屬檔案
3. **結構差異分析** - ZenDriver 與 Chrome 版本的函式實作差異
4. **功能完整度評分** - 根據標準架構評估各平台實作品質
5. **重構規劃建議** - 基於分析結果的開發優先度建議

---

## 📘 標準功能架構定義

完整的搶票程式標準功能定義請參考：**[搶票自動化標準功能定義](./ticket_automation_standard.md)**

### 功能架構概覽（12 階段）

<details>
<summary>點擊展開查看完整架構</summary>

1. **環境初始化** - WebDriver 初始化、瀏覽器設定
2. **身份認證** - 自動登入、Cookie 注入
3. **頁面監控與重載** - 自動重載、彈窗處理、版面自動偵測 (v2.0+)
4. **日期選擇** - 關鍵字匹配 + 條件式遞補 (v1.2+)
5. **區域/座位選擇** - 關鍵字匹配 + 條件式遞補 + 排除過濾 (v1.2+)
6. **票數設定** - 自動設定購票張數
7. **驗證碼處理** - OCR 自動辨識 + 自動答題 + 手動輸入回退 (v2.0+)
8. **表單填寫** - 自動填寫購票資訊、實名認證處理 (v2.0+)
9. **同意條款處理** - 自動勾選條款
10. **訂單確認與送出** - 確認並送出訂單
11. **排隊與付款** - 處理排隊狀態
12. **錯誤處理與重試** - 全域錯誤處理

詳細的函式拆分、設定來源、回退策略請參考 [ticket_automation_standard.md](./ticket_automation_standard.md)

</details>

### 核心設計原則

1. **設定驅動 (Configuration-Driven)**：所有行為由 `settings.json` 控制
2. **條件式遞補策略 (Conditional Fallback Strategy)** (v1.2+)：
   - 優先使用關鍵字匹配（早期返回模式）
   - 關鍵字失敗時根據 `date_auto_fallback` / `area_auto_fallback` 決定是否遞補
   - 嚴格模式 (false, 預設)：停止執行，避免誤購
   - 自動遞補模式 (true)：回退使用 mode 自動選擇
3. **函式拆分原則**：原子化、可組合、可測試、可重用

### 函式命名規範

- **NoDriver 版本（推薦）**：加上 `nodriver_` 前綴 - 例如 `async nodriver_tixcraft_main()`
- **Chrome 版本（維護模式）**：`{platform}_{function_name}()` - 例如 `tixcraft_date_auto_select()`
- **通用工具**：直接使用功能名稱 - 例如 `find_element_safe()`

---

## 🎯 快速索引

### 主要檔案
- **nodriver_tixcraft.py** - NoDriver 版本主迴圈 + URL 路由
- **nodriver_common.py** - 共用瀏覽器基礎設施（DOM 工具、暫停機制、Cloudflare、初始化）
- **NonBrowser.py** - OCR 輔助模組（被 nodriver_tixcraft.py import）
- **platforms/facebook.py** - Facebook 登入（2 函式）
- **platforms/fansigo.py** - FANSI GO 平台（14 函式）
- **platforms/cityline.py** - Cityline 平台（16 函式）
- **platforms/famiticket.py** - FamiTicket 全家平台（9 函式）
- **platforms/ticketplus.py** - TicketPlus 遠大平台（18 函式）
- **platforms/funone.py** - FunOne Tickets 平台（18 函式）
- **platforms/kktix.py** - KKTIX 平台（17 函式）
- **platforms/tixcraft.py** - TixCraft + Ticketmaster 平台（27 函式）
- **platforms/ibon.py** - iBon + Tour iBon 平台（25 函式）
- **platforms/kham.py** - KHAM + ticket.com.tw + UDN 平台（21 函式）
- **platforms/hkticketing.py** - HKTicketing + GalaxyMacau + Ticketek 平台（30 函式）

### 🌐 支援平台清單

#### 台灣地區
- **Tixcraft 拓元售票** - https://tixcraft.com
- **添翼 Teamear** - https://teamear.tixcraft.com/
- **Indievox 獨立音樂** - https://www.indievox.com/
- **KKTIX** - https://kktix.com
- **iBon** - https://ticket.ibon.com.tw/
- **FamiTicket 全網** - https://www.famiticket.com.tw
- **Kham 寬宏售票** - https://kham.com.tw/
- **Ticket.com.tw 年代** - https://ticket.com.tw/
- **UDN售票網** - https://tickets.udnfunlife.com/
- **TicketPlus 遠大** - https://ticketplus.com.tw/

#### 海外地區
- **Urbtix 城市** - http://www.urbtix.hk/
- **Cityline 買飛** - https://www.cityline.com/
- **HKTicketing 快達票** - https://hotshow.hkticketing.com/
- **澳門銀河** - https://ticketing.galaxymacau.com/
- **TicketMaster Singapore** - https://ticketmaster.sg
- **Ticketek Australia** - http://premier.ticketek.com.au

---

## 📖 平台函數 Sitemap

> 此部分作為函數定位工具，可根據檔案歸屬快速定位特定功能
>
> **重要說明**：依照 ZenDriver First 開發策略，以下所有平台章節皆以 **ZenDriver 版本優先列出**，Chrome Driver 版本作為參考對照。建議優先查閱和開發 ZenDriver 版本功能。

### 🎫 **TixCraft 拓元**

#### ZenDriver (`platforms/tixcraft.py`)
```
拓元主流程
├── nodriver_tixcraft_main
├── nodriver_tixcraft_date_auto_select
├── nodriver_tixcraft_area_auto_select
├── nodriver_get_tixcraft_target_area
├── nodriver_tixcraft_assign_ticket_number # ✅ (v1.3+ 支援 Indievox 票種關鍵字匹配)
├── nodriver_tixcraft_ticket_main
├── nodriver_tixcraft_ticket_main_agree
├── nodriver_tixcraft_verify
├── nodriver_fill_verify_form
├── nodriver_tixcraft_input_check_code
├── nodriver_tixcraft_ticket_main_ocr
├── nodriver_tixcraft_keyin_captcha_code
├── nodriver_tixcraft_toast
├── nodriver_tixcraft_reload_captcha
├── nodriver_tixcraft_get_ocr_answer
├── nodriver_tixcraft_auto_ocr
├── nodriver_tixcraft_home_close_window
├── nodriver_tixcraft_redirect
└── nodriver_ticket_number_select_fill
```

#### Chrome
```
拓元主流程
├── tixcraft_main
├── tixcraft_date_auto_select
├── tixcraft_area_auto_select
├── get_tixcraft_target_area
├── tixcraft_assign_ticket_number
├── tixcraft_ticket_main
├── tixcraft_ticket_main_agree
├── tixcraft_verify
├── tixcraft_auto_ocr
├── tixcraft_keyin_captcha_code
└── tixcraft_ticket_main_ocr
```

### 🎪 **KKTIX**

#### ZenDriver (`platforms/kktix.py`)
```
KKTIX 主流程
├── nodriver_kktix_main                  # platforms/kktix.py
├── nodriver_kktix_paused_main           # platforms/kktix.py
├── nodriver_kktix_signin                # platforms/kktix.py
├── nodriver_kktix_date_auto_select      # platforms/kktix.py
├── nodriver_kktix_reg_new_main          # platforms/kktix.py
├── nodriver_kktix_travel_price_list     # platforms/kktix.py
├── nodriver_kktix_assign_ticket_number  # platforms/kktix.py
├── nodriver_kktix_reg_captcha           # platforms/kktix.py
├── nodriver_kktix_events_press_next_button # platforms/kktix.py
├── nodriver_kktix_check_guest_modal     # platforms/kktix.py
├── nodriver_kktix_press_next_button     # platforms/kktix.py
├── nodriver_kktix_check_ticket_page_status # platforms/kktix.py
├── nodriver_kktix_booking_main          # platforms/kktix.py
├── nodriver_kktix_confirm_order_button  # platforms/kktix.py
├── nodriver_kktix_order_member_code     # platforms/kktix.py
├── nodriver_kktix_check_form_state      # platforms/kktix.py
├── nodriver_kktix_check_qualification   # platforms/kktix.py
├── nodriver_kktix_check_form_ready      # platforms/kktix.py
├── nodriver_kktix_select_qualification  # platforms/kktix.py
├── nodriver_kktix_wait_member_code_enabled # platforms/kktix.py
├── nodriver_kktix_handle_qualification_and_next # platforms/kktix.py
├── is_kktix_account_configured          # platforms/kktix.py
└── nodriver_facebook_login              # platforms/facebook.py
```

#### Chrome
```
KKTIX 主流程
├── kktix_main
├── kktix_paused_main
├── kktix_login
├── kktix_reg_new_main
├── kktix_travel_price_list
├── kktix_assign_ticket_number
├── kktix_reg_captcha
├── kktix_check_agree_checkbox
└── kktix_press_next_button
```

### 🎵 **TicketMaster**

#### ZenDriver (`platforms/tixcraft.py`)
```
TicketMaster 功能 (整合在 nodriver_tixcraft_main)
├── nodriver_ticketmaster_promo
├── nodriver_ticketmaster_parse_zone_info
├── get_ticketmaster_target_area
├── nodriver_ticketmaster_get_ticketPriceList
├── nodriver_ticketmaster_date_auto_select
├── nodriver_ticketmaster_area_auto_select
├── nodriver_ticketmaster_assign_ticket_number
└── nodriver_ticketmaster_captcha
```

#### Chrome
```
TicketMaster 功能 (整合在 tixcraft_main)
├── ticketmaster_date_auto_select
├── ticketmaster_area_auto_select
├── get_ticketmaster_target_area
├── ticketmaster_assign_ticket_number
├── ticketmaster_captcha
└── ticketmaster_promo
```

### 🏙️ **Cityline**

#### ZenDriver (platforms/cityline.py)
```
Cityline 主流程
├── nodriver_cityline_main                     # 主控制器
├── nodriver_cityline_login                    # 登入
├── nodriver_cityline_date_auto_select         # 日期選擇
├── nodriver_cityline_check_login_modal        # 登入 Modal 處理
├── nodriver_cityline_continue_button_press    # Continue 按鈕
├── nodriver_cityline_area_auto_select         # 區域選擇
├── nodriver_cityline_ticket_number_auto_select # 票數設定
├── nodriver_cityline_next_button_press        # Next 按鈕
├── nodriver_cityline_performance              # Performance 頁面整合
├── nodriver_cityline_check_shopping_basket    # 購物車偵測
├── nodriver_cityline_purchase_button_press    # eventDetail 處理
├── nodriver_cityline_close_second_tab         # 多分頁處理
├── nodriver_cityline_cookie_accept            # Cookie 同意
├── nodriver_cityline_press_buy_button         # Buy Ticket 按鈕
├── nodriver_cityline_clean_ads                # 廣告清除
└── nodriver_cityline_auto_retry_access        # 自動重試
```

#### Chrome
```
Cityline 主流程
├── cityline_main
├── cityline_login
├── cityline_date_auto_select
├── cityline_area_auto_select
├── cityline_ticket_number_auto_select
├── cityline_purchase_button_press
├── cityline_next_button_press
├── cityline_performance
└── cityline_input_code
```

### 💳 **iBon**

#### ZenDriver (`platforms/ibon.py`)（🥇 金級實作 - 95% 完整度）
```
iBon 主流程
├── nodriver_ibon_login                      # ✅ (Cookie 登入)
├── nodriver_ibon_date_auto_select           # ✅ (v1.3+ 性能優化)
│   ├── nodriver_ibon_date_auto_select_pierce # (Shadow DOM 穿透)
│   └── nodriver_ibon_date_auto_select_domsnapshot # (DOMSnapshot 快照)
├── nodriver_ibon_event_area_auto_select     # ✅ (Angular SPA Event 頁面)
├── nodriver_ibon_area_auto_select           # ✅ (舊版 .aspx 頁面)
├── nodriver_ibon_ticket_number_auto_select  # ✅ (票數自動設定)
├── nodriver_ibon_keyin_captcha_code         # ✅ (驗證碼輸入)
├── nodriver_ibon_refresh_captcha            # ✅ (刷新驗證碼)
├── nodriver_ibon_auto_ocr                   # ✅ (OCR 自動識別)
├── nodriver_ibon_captcha                    # ✅ (驗證碼主控制)
├── nodriver_ibon_purchase_button_press      # ✅ (購票按鈕)
├── nodriver_ibon_check_sold_out             # ✅ (售罄檢查)
├── nodriver_ibon_wait_for_select_elements   # ✅ (等待選擇元素)
├── nodriver_ibon_check_sold_out_on_ticket_page # ✅ (票券頁售罄檢查)
├── nodriver_ibon_navigate_on_sold_out       # ✅ (售罄導航)
├── nodriver_ibon_fill_verify_form           # ✅ (驗證表單填寫)
├── nodriver_ibon_verification_question      # ✅ (驗證問題)
├── nodriver_ibon_ticket_agree               # ✅ (同意條款)
├── nodriver_ibon_allow_not_adjacent_seat    # ✅ (非連續座位)
│
├── iBon Tour 模組
├── nodriver_tour_ibon_event_detail          # ✅ (Tour 活動詳情)
├── nodriver_tour_ibon_options               # ✅ (Tour 選項)
├── nodriver_tour_ibon_checkout              # ✅ (Tour 結帳)
│
└── nodriver_ibon_main                       # ✅ (主流程完整)
```

#### Chrome
```
iBon 主流程
├── ibon_main
├── ibon_date_auto_select
├── ibon_area_auto_select
├── ibon_ticket_number_auto_select
├── ibon_ticket_agree
├── ibon_captcha
├── ibon_auto_ocr
├── ibon_keyin_captcha_code
├── ibon_purchase_button_press
└── ibon_performance
```

### 🎭 **Urbtix**

#### Chrome
```
Urbtix 主流程
├── urbtix_main
├── urbtix_login
├── urbtix_date_auto_select
├── urbtix_area_auto_select
├── urbtix_ticket_number_auto_select
├── urbtix_purchase_ticket
├── urbtix_performance
└── urbtix_auto_survey
```

#### ZenDriver
```
❌ 完全未實作
```

### 🎪 **KHAM 寬宏售票**

#### ZenDriver
```
KHAM 主流程 (含 UDN 售票網、Ticket.com.tw)，檔案：src/platforms/kham.py
├── nodriver_kham_main                   # ✅
├── nodriver_kham_login                  # ✅
├── nodriver_kham_date_auto_select       # ✅ (Feature 003: Early Return + Fallback；#357 群組項目頁共用)
├── nodriver_kham_go_buy_redirect        # ✅
├── nodriver_kham_check_realname_dialog  # ✅
├── nodriver_kham_allow_not_adjacent_seat # ✅
├── nodriver_kham_switch_to_auto_seat    # ✅
├── nodriver_kham_check_captcha_text_error # ✅
├── nodriver_kham_product                # ✅
├── nodriver_kham_area_auto_select       # ✅ (Feature 003: Early Return + Fallback)
├── nodriver_kham_keyin_captcha_code     # ✅
├── nodriver_kham_auto_ocr              # ✅
├── nodriver_kham_captcha                # ✅
├── nodriver_kham_performance            # ✅
│
├── 座位選擇模組 (KHAM/UDN/Ticket.com.tw 共用)
├── nodriver_kham_seat_main              # ✅ 座位選擇主流程
├── nodriver_kham_seat_auto_select       # ✅ 座位自動選擇核心
├── nodriver_kham_seat_type_auto_select  # ✅ 票種自動選擇
│
├── UDN 專屬座位選擇模組
├── nodriver_udn_seat_auto_select        # ✅ UDN 座位自動選擇
├── nodriver_udn_seat_select_ticket_type # ✅ UDN 票種選擇
└── nodriver_udn_seat_main              # ✅ UDN 座位選擇主流程
```

#### Chrome
```
KHAM 主流程
├── kham_main
├── kham_login
├── hkam_date_auto_select
├── kham_go_buy_redirect
├── kham_product
├── kham_area_auto_select
├── kham_switch_to_auto_seat
├── kham_performance
├── kham_keyin_captcha_code
├── kham_auto_ocr
├── kham_captcha
├── kham_check_captcha_text_error
├── kham_check_realname_dialog
└── kham_allow_not_adjacent_seat
```

**UDN 專屬說明**：
- UDN 與 KHAM 共用 UTK 後端，座位選擇邏輯完全複用
- UDN 座位選擇模組：`nodriver_udn_seat_auto_select`、`nodriver_udn_seat_select_ticket_type`、`nodriver_udn_seat_main`
- 支援 Feature 003 遞補機制：`date_auto_fallback`、`area_auto_fallback`

### 🎫 **HK Ticketing**

#### ZenDriver (`platforms/hkticketing.py`)
```
HKTicketing 主流程
├── nodriver_hkticketing_main
├── nodriver_hkticketing_login
├── nodriver_hkticketing_accept_cookie
├── nodriver_hkticketing_date_buy_button_press
├── nodriver_hkticketing_date_assign
├── nodriver_hkticketing_date_password_input
├── nodriver_hkticketing_date_auto_select
├── nodriver_hkticketing_area_auto_select
├── nodriver_hkticketing_ticket_number_auto_select
├── nodriver_hkticketing_ticket_delivery_option
├── nodriver_hkticketing_next_button_press
├── nodriver_hkticketing_go_to_payment
├── nodriver_hkticketing_hide_tickets_blocks
├── nodriver_hkticketing_performance
├── nodriver_hkticketing_escape_robot_detection
├── nodriver_hkticketing_url_redirect
├── nodriver_hkticketing_content_refresh
├── nodriver_hkticketing_travel_iframe
│
├── HKTicketing Type02 模組 (新版網站)
├── nodriver_hkticketing_type02_clear_session # ✅
├── nodriver_hkticketing_type02_check_traffic_overload # ✅
├── nodriver_hkticketing_type02_login   # ✅
├── nodriver_hkticketing_type02_dismiss_modal # ✅
├── nodriver_hkticketing_type02_event_page_buy_button # ✅
├── nodriver_hkticketing_type02_event_page # ✅
├── nodriver_hkticketing_type02_date_assign # ✅
├── nodriver_hkticketing_type02_area_auto_select # ✅
├── nodriver_hkticketing_type02_ticket_number_select # ✅
├── nodriver_hkticketing_type02_next_button_press # ✅
├── nodriver_hkticketing_type02_performance # ✅
└── nodriver_hkticketing_type02_confirm_order # ✅
```

#### Chrome
```
HK Ticketing 功能 (無獨立 main)
├── hkticketing_login
├── hkticketing_date_auto_select
├── hkticketing_date_assign
├── hkticketing_area_auto_select
├── hkticketing_ticket_number_auto_select
├── hkticketing_performance
├── hkticketing_next_button_press
└── hkticketing_go_to_payment
```

### ➕ **TicketPlus**

#### ZenDriver (platforms/ticketplus.py)
```
TicketPlus 主流程
├── nodriver_ticketplus_main                      # platforms/ticketplus.py ✅
├── nodriver_ticketplus_detect_layout_style       # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_account_sign_in           # platforms/ticketplus.py ✅
├── nodriver_ticketplus_is_signin                 # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_account_auto_fill         # platforms/ticketplus.py ✅
├── nodriver_ticketplus_date_auto_select          # platforms/ticketplus.py ✅
├── nodriver_ticketplus_unified_select            # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_click_next_button_unified # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_ticket_agree              # platforms/ticketplus.py ✅
├── nodriver_ticketplus_accept_realname_card      # platforms/ticketplus.py ✅
├── nodriver_ticketplus_accept_other_activity     # platforms/ticketplus.py ✅
├── nodriver_ticketplus_accept_order_fail         # platforms/ticketplus.py ✅
├── nodriver_ticketplus_check_queue_status        # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_confirm                   # platforms/ticketplus.py ✅
├── nodriver_ticketplus_order                     # platforms/ticketplus.py ✅
├── nodriver_ticketplus_wait_for_vue_ready        # platforms/ticketplus.py ✅ (額外功能)
├── nodriver_ticketplus_check_next_button         # platforms/ticketplus.py ✅ (額外功能)
└── nodriver_ticketplus_order_exclusive_code      # platforms/ticketplus.py ✅ (v1.3+ 折扣碼自動填入)
```

#### Chrome
```
TicketPlus 主流程
├── ticketplus_main
├── ticketplus_account_sign_in
├── ticketplus_account_auto_fill
├── ticketplus_date_auto_select
├── ticketplus_assign_ticket_number
├── ticketplus_order_expansion_auto_select
├── ticketplus_ticket_agree
├── ticketplus_auto_ocr
├── ticketplus_keyin_captcha_code
└── ticketplus_order_ocr
```

### 🎪 **FamiTicket 全家** (🏅 白金級 - v2025.11.24 完整實作)

#### ZenDriver (platforms/famiticket.py, 🏅 白金級 - 100% 完整)
```
FamiTicket 主流程
├── nodriver_famiticket_main                 # platforms/famiticket.py ✅ (主控制器 - URL 路由器)
├── nodriver_fami_login                      # platforms/famiticket.py ✅ (帳號密碼登入，HTTP-Only Cookie)
├── nodriver_fami_activity                   # platforms/famiticket.py ✅ (活動頁面「購買」按鈕)
├── nodriver_fami_verify                     # platforms/famiticket.py ✅ (驗證問題/實名認證)
├── nodriver_fami_date_auto_select           # platforms/famiticket.py ✅ (日期選擇+條件回退 date_auto_fallback)
├── nodriver_fami_area_auto_select           # platforms/famiticket.py ✅ (區域選擇+AND邏輯+條件回退)
├── nodriver_fami_date_to_area               # platforms/famiticket.py ✅ (日期/區域協調器)
├── nodriver_fami_ticket_select              # platforms/famiticket.py ✅ (票種選擇頁面)
└── nodriver_fami_home_auto_select           # platforms/famiticket.py ✅ (首頁入口分派)
```

#### Chrome
```
FamiTicket 主流程
├── famiticket_main
├── fami_login
├── fami_date_auto_select
├── fami_area_auto_select
├── fami_verify
├── fami_activity
└── fami_home_auto_select
```

**FamiTicket ZenDriver 功能特點**：
- ✅ 完整 9 函數實作，涵蓋登入→活動→日期→區域→票種→結帳完整流程
- ✅ 日期選擇支援關鍵字匹配（OR 邏輯，逗號分隔）+ `date_auto_fallback` 條件回退
- ✅ 區域選擇支援 AND 邏輯（空格分隔）+ 多組關鍵字（分號分隔）
- ✅ 隨機延遲 0.4-1.2 秒模擬人類操作（反爬蟲）
- ✅ 使用 ZenDriver 官方 API（`query_selector_all`、`wait_for`）

### 🎪 **FunOne Tickets** (v2026.01.13 新增)

#### ZenDriver (platforms/funone.py)
```
FunOne Tickets 主流程 (Feature 011)
├── nodriver_funone_main                    # platforms/funone.py ✅ (主控制器 - URL 路由器)
├── nodriver_funone_inject_cookie           # platforms/funone.py ✅ (Cookie 注入登入)
├── nodriver_funone_check_login_status      # platforms/funone.py ✅ (登入狀態檢查)
├── nodriver_funone_verify_login            # platforms/funone.py ✅ (驗證登入+重新注入)
├── nodriver_funone_close_popup             # platforms/funone.py ✅ (關閉彈窗)
├── nodriver_funone_date_auto_select        # platforms/funone.py ✅ (場次選擇+關鍵字匹配)
├── nodriver_funone_area_auto_select        # platforms/funone.py ✅ (票種選擇+關鍵字匹配)
├── nodriver_funone_check_sold_out          # platforms/funone.py ✅ (售罄檢查)
├── nodriver_funone_click_refresh_button    # platforms/funone.py ✅ (刷新按鈕)
├── nodriver_funone_assign_ticket_number    # platforms/funone.py ✅ (張數設定)
├── nodriver_funone_captcha_handler         # platforms/funone.py ✅ (驗證碼等待)
├── nodriver_funone_reload_captcha          # platforms/funone.py ✅ (重新載入驗證碼)
├── nodriver_funone_ocr_captcha             # platforms/funone.py ✅ (OCR 驗證碼辨識)
├── nodriver_funone_detect_step             # platforms/funone.py ✅ (步驟偵測)
├── nodriver_funone_ticket_agree            # platforms/funone.py ✅ (同意條款)
├── nodriver_funone_order_submit            # platforms/funone.py ✅ (訂單提交)
├── nodriver_funone_auto_reload             # platforms/funone.py ✅ (開賣前自動刷新)
└── nodriver_funone_error_handler           # platforms/funone.py ✅ (錯誤處理)
```

**FunOne Tickets ZenDriver 功能特點**：
- ✅ 完整 18 函數實作，涵蓋 Cookie 登入→場次→票種→張數→驗證碼→提交完整流程
- ✅ Cookie 注入登入（FunOne 使用 OTP 登入，僅能透過 Cookie 快速登入）
- ✅ 場次/票種選擇支援關鍵字匹配 + random/from_top_to_bottom 遞補模式
- ✅ 支援售罄跳過（pass_date_is_sold_out）
- ✅ 使用通用 `ticket_number` 設定（與其他平台一致）
- ✅ OCR 驗證碼辨識 + 驗證碼重載

### 🎪 **Fansigo** (platforms/fansigo.py)

#### ZenDriver
```
Fansigo 主流程
├── nodriver_fansigo_main                    # 主控制器
├── nodriver_fansigo_inject_cookie           # Cookie 注入
├── nodriver_fansigo_get_shows               # 取得場次列表
├── nodriver_fansigo_click_show              # 點擊場次
├── nodriver_fansigo_date_auto_select        # 日期自動選擇
├── nodriver_fansigo_get_sections            # 取得區域列表
├── nodriver_fansigo_area_auto_select        # 區域自動選擇
├── nodriver_fansigo_assign_ticket_number    # 票數設定
└── nodriver_fansigo_click_checkout          # 點擊結帳
```

### 🌐 **其他平台**

#### Chrome
```
其他平台
├── ticket_login (Ticket.com.tw)
├── udn_login (UDN)
├── facebook_login
├── facebook_main
└── softix_powerweb_main
```

#### ZenDriver
```
其他平台
├── nodriver_facebook_login              # platforms/facebook.py
├── nodriver_facebook_main               # platforms/facebook.py
├── nodriver_ticket_login                # platforms/kham.py
│
├── 年代售票 座位選擇模組 (platforms/kham.py)
├── nodriver_ticket_seat_type_auto_select
├── nodriver_ticket_seat_auto_select
├── nodriver_ticket_seat_main
├── nodriver_ticket_check_seat_taken_dialog
├── nodriver_ticket_close_dialog_with_retry
├── nodriver_ticket_allow_not_adjacent_seat
└── nodriver_ticket_switch_to_auto_seat
```

### 🔧 **共用工具函數**

#### ZenDriver
```
OCR 相關
├── nodriver_tixcraft_get_ocr_answer     # platforms/tixcraft.py
└── nodriver_force_check_checkbox        # nodriver_common.py

Cloudflare Turnstile
├── detect_cloudflare_challenge          # nodriver_common.py ✅ (Cloudflare Turnstile 三層偵測)
├── _find_cf_iframe_in_dom              # nodriver_common.py ✅ (DOM 樹遞迴搜尋 CF iframe)
├── _cdp_click                          # nodriver_common.py ✅ (CDP 滑鼠事件封裝)
└── handle_cloudflare_challenge         # nodriver_common.py ✅ (Cloudflare Turnstile 三階段處理)

輔助工具
├── play_sound_while_ordering            # nodriver_common.py
├── send_discord_notification            # nodriver_common.py
├── send_telegram_notification           # nodriver_common.py
├── nodriver_press_button                # nodriver_common.py
├── nodriver_check_checkbox              # nodriver_common.py
├── nodriver_check_checkbox_enhanced     # nodriver_common.py
├── nodriver_get_text_by_selector        # nodriver_common.py
├── nodriver_goto_homepage               # nodriver_tixcraft.py
├── nodriver_resize_window               # nodriver_common.py
├── nodriver_current_url                 # nodriver_common.py
├── nodriver_overwrite_prefs             # nodriver_common.py
└── cli                                  # nodriver_tixcraft.py
```

#### util.py 共用函數
```
Debug 輸出
├── DebugLogger                          # class ✅ 統一除錯訊息管理
├── create_debug_logger(config_dict)     # factory ✅ 建立 DebugLogger 實例
└── get_debug_mode                       # ✅ 安全讀取 debug 模式設定

選擇模式與關鍵字處理
├── is_text_match_keyword                # ✅ 關鍵字比對核心
├── get_matched_blocks_by_keyword        # ✅ 區域/日期關鍵字匹配
├── get_matched_blocks_by_keyword_item_set # ✅ 關鍵字集合匹配
├── get_target_index_by_mode             # ✅ 選擇模式索引計算
├── get_target_item_from_matched_list    # ✅ 從匹配列表取得目標項目
├── parse_keyword_string_to_array        # ✅ 統一 JSON 關鍵字解析
├── is_row_match_keyword                 # ✅ 行匹配檢查
└── reset_row_text_if_match_keyword_exclude # ✅ 排除關鍵字匹配檢查

字串處理
├── format_keyword_for_display
├── format_config_keyword_for_json
├── format_keyword_string
├── format_quota_string
├── full2half
├── find_between
├── remove_html_tags
├── find_continuous_number
├── find_continuous_text
├── find_continuous_pattern
├── is_all_alpha_or_numeric
└── convert_string_to_pattern

中文數字處理
├── get_chinese_numeric
├── synonym_dict
├── chinese_numeric_to_int
└── normalize_chinese_numeric

OCR 與驗證碼
├── guess_answer_list_from_multi_options
├── guess_answer_list_from_symbols
├── get_offical_hint_string_from_symbol
├── guess_answer_list_from_hint
├── format_question_string
├── permutations
├── get_answer_list_by_question
├── check_answer_keep_symbol
├── kktix_get_web_datetime
├── get_answer_string_from_web_date
├── get_answer_string_from_web_time
├── get_answer_list_from_question_string
├── guess_tixcraft_question
├── get_answer_list_from_user_guess_string
└── extract_answer_by_question_pattern

音訊與通知
├── play_mp3_async
├── play_mp3
├── build_discord_message                # ✅ Discord 訊息建構
├── send_discord_webhook                 # ✅ Discord Webhook 同步發送
├── send_discord_webhook_async           # ✅ Discord Webhook 非同步發送
├── build_telegram_message               # ✅ Telegram 訊息建構 (v2026.03)
├── send_telegram_message                # ✅ Telegram Bot 同步發送 (v2026.03)
└── send_telegram_message_async          # ✅ Telegram Bot 非同步發送 (v2026.03)

檔案 I/O
├── save_json
├── write_string_to_file
└── force_remove_file

系統工具
├── get_ip_address
├── is_connectable
├── is_arm
├── get_app_root
├── set_instance_id                       # 多開：設定本行程 instance id
├── get_instance_id
├── get_instance_state_path               # 多開：解析 per-instance 狀態檔路徑
├── t_or_f
├── get_brave_bin_path
├── launch_maxbot                         # 支援 instance= 參數（多開序號實例）
├── parse_nodriver_result
└── get_token

KKTIX 專用
├── kktix_get_registerStatus
└── kktix_get_event_code

Cloudflare 模板匹配
├── get_cf_template_paths
└── verify_cf_with_templates

iBon Livemap
├── ibon_fetch_and_parse_livemap
├── ibon_livemap_select_area
└── ibon_build_skip_url
```

**機制索引**：
- 設定熱重載（hot-reload）：`reload_config`（nodriver_tixcraft.py），詳見 [14-hot-reload.md](../03-mechanisms/14-hot-reload.md)
- 多開實例（multi-instance）：`set_instance_id` / `get_instance_state_path`（util.py）、`InstancesHandler` / `list_instance_ids` / `get_instance_status` / `launch_maxbot`（settings.py），詳見 [17-multi-instance.md](../03-mechanisms/17-multi-instance.md)
- Cloudflare Turnstile：`detect_cloudflare_challenge` / `handle_cloudflare_challenge`（nodriver_common.py），詳見 [15-cloudflare-turnstile.md](../03-mechanisms/15-cloudflare-turnstile.md)

### 🛑 **暫停機制輔助函數** (ZenDriver 專用)

> **位置**: `src/nodriver_common.py`

#### 核心暫停檢查函數

```
check_and_handle_pause(config_dict)      # ✅
└── 統一暫停檢查入口
    ├── 檢查 MAXBOT_INT28_IDLE.txt
    ├── 根據 verbose 顯示訊息
    └── 返回暫停狀態 (True/False)
```

**功能說明**：
- 主要暫停檢查函數，所有平台函數的統一入口
- 根據 `config_dict["advanced"]["verbose"]` 控制訊息顯示
- `verbose = true` → 顯示 "BOT Paused."
- `verbose = false` → 不顯示訊息

#### 暫停輔助包裝函數

```
sleep_with_pause_check(tab, seconds, config_dict)              # ✅
├── 取代 tab.sleep()
├── 等待期間檢查暫停狀態
└── 返回 True (暫停中) / False (正常)

asyncio_sleep_with_pause_check(seconds, config_dict)           # ✅
├── 取代 asyncio.sleep()
├── 不需要 tab 物件的純延遲
└── 返回 True (暫停中) / False (正常)

evaluate_with_pause_check(tab, javascript_code, config_dict)   # ✅
├── JavaScript 執行前檢查暫停
├── 暫停時返回 None
└── 正常時返回 JavaScript 執行結果

with_pause_check(task_func, config_dict, *args, **kwargs)      # ✅
├── 包裝長時間任務
├── 支援中途暫停（每 50ms 檢查一次）
└── 暫停時取消任務並返回 None
```

#### 使用規範

1. **統一入口**：所有暫停檢查必須使用 `check_and_handle_pause(config_dict)`
2. **輔助函數優先**：使用專用包裝函數取代原生 sleep/evaluate
3. **僅 ZenDriver 支援**：Chrome Driver 版本不支援暫停機制
4. **訊息控制**：由 verbose 設定統一控制顯示

#### 相關文件

- [暫停機制範本](./coding_templates.md#暫停機制標準範本) - 完整實作範例
- [暫停機制開發規範](./development_guide.md#暫停機制開發規範) - 開發原則與檢查清單

---

### 📊 **平台實作狀態一覽**

| 平台 | ZenDriver 檔案 | 完整度 |
|------|:-----------------:|:------:|
| TixCraft | platforms/tixcraft.py | ✅/✅ |
| KKTIX | platforms/kktix.py | ✅/✅ |
| TicketPlus | platforms/ticketplus.py | ✅/✅ |
| KHAM 寬宏 | platforms/kham.py | ✅/✅ |
| TicketMaster | platforms/tixcraft.py | ✅/✅ |
| Cityline | platforms/cityline.py | ✅/✅ |
| iBon | platforms/ibon.py | ✅/🥇 |
| FamiTicket | platforms/famiticket.py | ✅/🏅 |
| HK Ticketing | platforms/hkticketing.py | ✅/🏅 |
| FunOne | platforms/funone.py | -/✅ |
| Fansigo | platforms/fansigo.py | -/✅ |
| Urbtix | 未實作 | ✅/❌ |

---

## 總體統計

| 平台 | Chrome版本函式數 | ZenDriver版本函式數 | 實際實作度 | 狀態 |
|------|------------------|-------------------|------------|------|
| Tixcraft | 17 | 19 | 95% | ✅ **雙版本完整** |
| KKTIX | 17 | 17 | 100% | ✅ **雙版本完整** → `platforms/kktix.py` |
| TicketPlus | 25 | 18 | 95% | ✅ **雙版本完整** |
| KHAM 寬宏 | 14 | 17 | 98% | 🏅 **白金級** |
| 年代售票 | 7 | 8 | 100% | ✅ **雙版本完整** |
| iBon | 15 | 25 | 95% | 🥇 **金級實作** |
| FamiTicket | 10 | 9 | 100% | 🏅 **白金級** (v2025.11.24) |
| Cityline | 15 | 17 | 80% | 🥇 **金級** |
| UrBtix | 11 | 0 | 0% | ❌ 未實作 |
| HKTicketing | 20 | 30 | 95% | 🏅 **白金級** (v2025.11.28) |
| Ticketmaster | 9 | 8 | 89% | 🥇 **金級實作** |
| FunOne | 0 | 18 | 100% | ✅ **ZenDriver 完整** (v2026.01.13) |
| Fansigo | 0 | 9 | 100% | ✅ **ZenDriver 完整** |

**總計：ZenDriver 239 個函式，實際可用度：約 90%**

**🎯 重要更新：八大主流平台（TixCraft、KKTIX、TicketPlus、iBon、KHAM、FamiTicket、FunOne、Fansigo）ZenDriver 版本已完全可用**
**ℹ️ 備註：TicketPlus ZenDriver 版本缺少 4 個 OCR 函式，但目前活動無 OCR 需求，暫不影響使用**

### 實作品質說明
- ✅ **基本完整**：大部分功能已實作且可使用
- ⚠️ **有 TODO/部分實作**：函式存在但包含 TODO 或未完成
- 🔲 **僅框架**：函式定義存在但實際功能空白
- ❌ **未實作**：完全沒有對應函式
- 🥇 **金級實作**：功能完整度達 90% 以上，包含完整的核心搶票流程

---

## 📊 功能完整度評分（基於標準架構）

> **評分標準**：根據 [ticket_automation_standard.md](./ticket_automation_standard.md) 定義的 12 階段功能架構評分

### 評分方式說明

**滿分：100 分**

| 功能模組 | 權重 | 評分標準 |
|---------|------|---------|
| 主流程控制 | 10 分 | 必須有 `{platform}_main()` 統籌流程 |
| 日期選擇 | 15 分 | 支援關鍵字 + mode 回退策略 |
| 區域選擇 | 15 分 | 支援關鍵字 + mode 回退 + 排除關鍵字 |
| 票數設定 | 10 分 | 能正確設定票數 |
| 驗證碼處理 | 10 分 | 支援 OCR + 手動輸入回退 |
| 同意條款 | 5 分 | 能自動勾選條款 |
| 訂單送出 | 10 分 | 能找到並點擊送出按鈕 |
| 登入功能 | 10 分 | 支援帳密或 Cookie 登入 |
| 錯誤處理 | 5 分 | 有完整的 try-except 和錯誤日誌 |
| 彈窗處理 | 5 分 | 能處理常見彈窗 |
| 頁面重載 | 5 分 | 支援自動重載與過熱保護 |

### Chrome 版本功能完整度評分

| 平台 | 主流程 | 日期選擇 | 區域選擇 | 票數設定 | 驗證碼 | 條款 | 送出 | 登入 | 錯誤處理 | 彈窗 | 重載 | **總分** | 等級 |
|-----|:-----:|:-------:|:-------:|:-------:|:-----:|:---:|:---:|:---:|:-------:|:---:|:---:|:-------:|:---:|
| **TixCraft** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 5 | 5 | **100** | 🏅 白金 |
| **KKTIX** | 10 | 10 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 5 | 5 | **95** | 🏅 白金 |
| **TicketPlus** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 5 | 5 | **100** | 🏅 白金 |
| **Cityline** | 10 | 15 | 15 | 10 | 5 | 3 | 10 | 10 | 5 | 5 | 5 | **93** | 🏅 白金 |
| **iBon** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 5 | 5 | 5 | 5 | **95** | 🏅 白金 |
| **Urbtix** | 10 | 15 | 15 | 10 | 5 | 3 | 10 | 10 | 5 | 3 | 5 | **91** | 🥇 金 |
| **KHAM** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 5 | 5 | **100** | 🏅 白金 |
| **HKTicketing** | 10 | 15 | 15 | 10 | 5 | 5 | 10 | 10 | 5 | 5 | 5 | **95** | 🏅 白金 |
| **FamiTicket** | 10 | 15 | 15 | 10 | 5 | 5 | 10 | 10 | 5 | 3 | 5 | **93** | 🏅 白金 |
| **Ticketmaster** | 10 | 10 | 10 | 10 | 10 | 3 | 10 | 5 | 5 | 3 | 5 | **81** | 🥇 金 |

**Chrome 版本平均分：94.3 分**

### ZenDriver 版本功能完整度評分

| 平台 | 主流程 | 日期選擇 | 區域選擇 | 票數設定 | 驗證碼 | 條款 | 送出 | 登入 | 錯誤處理 | 彈窗 | 重載 | **總分** | 等級 |
|-----|:-----:|:-------:|:-------:|:-------:|:-----:|:---:|:---:|:---:|:-------:|:---:|:---:|:-------:|:---:|
| **TicketPlus** | 10 | 15 | 15 | 10 | 8 | 5 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 |
| **KHAM** | 10 | 15 | 15 | 10 | 10 | 3 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 |
| **FamiTicket** | 10 | 15 | 15 | 10 | 8 | 5 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 (v2025.11.24) |
| **iBon** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 3 | 2 | **95** | 🏅 白金 |
| **HKTicketing** | 10 | 15 | 15 | 10 | 0 | 5 | 10 | 10 | 5 | 5 | 5 | **90** | 🏅 白金 (v2025.11.28) |
| **FunOne** | 10 | 15 | 15 | 10 | 8 | 5 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 (v2026.01.13) |
| **Fansigo** | 10 | 15 | 15 | 10 | 0 | 0 | 10 | 10 | 5 | 3 | 5 | **83** | 🥇 金 |
| **KKTIX** | 10 | 8 | 12 | 10 | 8 | 4 | 10 | 10 | 4 | 4 | 4 | **84** | 🥇 金 |
| **TixCraft** | 10 | 12 | 12 | 8 | 8 | 4 | 8 | 8 | 4 | 4 | 4 | **82** | 🥇 金 |
| **Ticketmaster** | 10 | 12 | 10 | 8 | 8 | 4 | 8 | 8 | 4 | 3 | 5 | **80** | 🥇 金 |
| **Cityline** | 10 | 10 | 8 | 5 | 0 | 0 | 8 | 8 | 3 | 3 | 5 | **60** | 🥈 銀 |
| **Urbtix** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | ❌ 未實作 |
| **Facebook** | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 3 | 3 | 0 | **24** | ❌ 未完成 |

**ZenDriver 版本平均分：68.5 分**（僅計算有實作的平台：**87.8 分**）

### 評分等級說明

- **🏅 白金級 (90-100 分)**：功能完整，可直接用於生產環境
- **🥇 金級 (80-89 分)**：核心功能完整，部分功能待補強
- **🥈 銀級 (60-79 分)**：基本可用，需要補充多個功能
- **🥉 銅級 (40-59 分)**：僅有框架，不建議使用
- **❌ 未完成 (0-39 分)**：需要重新實作或完全未實作

### 關鍵發現

1. **Chrome 版本**：整體品質極高，平均 94.3 分
   - 9 個白金級平台，1 個金級平台
   - TixCraft、TicketPlus、KHAM 達到滿分 100 分
   - 所有平台均可直接用於生產環境

2. **ZenDriver 版本**：大幅進步，8 個平台可用
   - 6 個白金級平台：TicketPlus (98)、KHAM (98)、FamiTicket (98)、FunOne (98)、iBon (95)、HKTicketing (90)
   - 4 個金級平台：KKTIX (84)、Fansigo (83)、TixCraft (82)、Ticketmaster (80)
   - 1 個銀級平台：Cityline (60)
   - 1 個未實作：Urbtix

3. **實作差距**：
   - ZenDriver 版本已覆蓋 12 個平台中的 11 個
   - 主要差距在 Urbtix 完全未實作、Cityline 待補強

### 平台實作對照表

根據標準功能架構，以下是各平台實作狀況對照：

#### ✅ 完全實作（Chrome + ZenDriver 雙版本可用）
- **TicketPlus**：Chrome 100 分，ZenDriver 98 分
- **KHAM**：Chrome 100 分，ZenDriver 98 分
- **FamiTicket**：Chrome 93 分，ZenDriver 98 分
- **iBon**：Chrome 95 分，ZenDriver 95 分
- **HKTicketing**：Chrome 95 分，ZenDriver 90 分
- **KKTIX**：Chrome 95 分，ZenDriver 84 分
- **TixCraft**：Chrome 100 分，ZenDriver 82 分
- **Ticketmaster**：Chrome 81 分，ZenDriver 80 分

#### ✅ ZenDriver 專有平台
- **FunOne**：ZenDriver 98 分（白金級，v2026.01.13）
- **Fansigo**：ZenDriver 83 分（金級）

#### ⚠️ 部分實作（ZenDriver 版本待補強）
- **Cityline**：Chrome 93 分，ZenDriver 60 分（銀級）
- **Urbtix**：Chrome 91 分，ZenDriver 未實作

#### 📋 建議開發優先度

**Phase 1（緊急）**：
1. **補強 ZenDriver Cityline**（60→85 分）
   - 補完缺失功能

**Phase 2（重要）**：
2. **實作 ZenDriver Urbtix**（0→85 分）
   - 香港重要平台，Chrome 已有 11 個完整函式

**Phase 3（次要）**：
3. **TicketPlus OCR 功能補完** (暫時忽略，等待實際需求)

---

## 1. Tixcraft 平台 (拓元)

### Chrome 版本 (17個函式)
- `tixcraft_main()` - 主控制器
- `tixcraft_home_close_window()` - 關閉彈窗
- `tixcraft_redirect()` - 頁面重定向
- `tixcraft_date_auto_select()` - 自動選擇日期
- `get_tixcraft_target_area()` - 取得目標區域
- `tixcraft_area_auto_select()` - 自動選擇區域
- `tixcraft_verify()` - 驗證處理
- `tixcraft_input_check_code()` - 輸入驗證碼
- `tixcraft_change_captcha()` - 更換驗證碼
- `tixcraft_toast()` - 顯示提示訊息
- `tixcraft_keyin_captcha_code()` - 手動輸入驗證碼
- `tixcraft_reload_captcha()` - 重新載入驗證碼
- `tixcraft_get_ocr_answer()` - OCR 識別
- `tixcraft_auto_ocr()` - 自動 OCR
- `tixcraft_ticket_main_agree()` - 勾選同意條款
- `tixcraft_assign_ticket_number()` - 設定票券數量
- `tixcraft_ticket_main()` - 票券頁面主處理

### ZenDriver 版本 (19個函式, platforms/tixcraft.py)
- `async nodriver_tixcraft_main()` - 主控制器 ✅
- `async nodriver_tixcraft_home_close_window()` - 關閉彈窗 ✅
- `async nodriver_tixcraft_redirect()` - 頁面重定向 ✅
- `async nodriver_tixcraft_date_auto_select()` - 自動選擇日期 ✅
- `async nodriver_get_tixcraft_target_area()` - 取得目標區域 ✅
- `async nodriver_tixcraft_area_auto_select()` - 自動選擇區域 ✅
- `async nodriver_tixcraft_verify()` - 驗證處理 ✅
- `async nodriver_fill_verify_form()` - 填寫驗證表單 ✅
- `async nodriver_tixcraft_input_check_code()` - 輸入驗證碼 ✅
- `async nodriver_tixcraft_toast()` - 顯示提示訊息 ✅
- `async nodriver_tixcraft_keyin_captcha_code()` - 手動輸入驗證碼 ✅
- `async nodriver_tixcraft_reload_captcha()` - 重新載入驗證碼 ✅
- `async nodriver_tixcraft_get_ocr_answer()` - OCR 識別 ✅
- `async nodriver_tixcraft_auto_ocr()` - 自動 OCR ✅
- `async nodriver_tixcraft_ticket_main_agree()` - 勾選同意條款 ✅
- `async nodriver_tixcraft_assign_ticket_number()` - 設定票券數量 ✅
- `async nodriver_tixcraft_ticket_main()` - 票券頁面主處理 ✅
- `async nodriver_tixcraft_ticket_main_ocr()` - 票券頁面 OCR ✅
- `async nodriver_ticket_number_select_fill()` - 填入票券數量 ✅

### Tixcraft 差異分析
✅ **已實作：19/17** (函式數量完整，品質優良)
✅ **核心功能完整：** 所有關鍵函式已實作並可用
➕ **額外功能：** ZenDriver 版本新增了 `ticket_main_ocr()` 分離 OCR 邏輯、`fill_verify_form()` 通用驗證表單

**實作完整度：** 主流程控制、日期選擇、區域選擇、票數設定、驗證碼處理、同意條款、訂單送出等功能完整

---

## 2. KKTIX 平台

### Chrome 版本 (17個函式)
- `kktix_main()` - 主控制器
- `kktix_confirm_order_button()` - 確認訂單按鈕
- `kktix_events_press_next_button()` - 活動頁下一步
- `kktix_press_next_button()` - 按下下一步按鈕
- `kktix_travel_price_list()` - 遍歷票價清單
- `kktix_assign_ticket_number()` - 設定票券數量
- `kktix_check_agree_checkbox()` - 檢查同意條款
- `kktix_double_check_all_text_value()` - 雙重檢查文字值
- `set_kktix_control_label_text()` - 設定控制標籤文字
- `kktix_reg_captcha()` - 註冊驗證碼
- `kktix_reg_new_main()` - 新註冊主流程
- `kktix_check_register_status()` - 檢查註冊狀態
- `kktix_reg_auto_reload()` - 自動重新載入
- `kktix_login()` - 登入
- `kktix_paused_main()` - 暫停主流程
- `get_tixcraft_ticket_select_by_keyword()` - 根據關鍵字選票
- `get_tixcraft_ticket_select()` - 選票處理

### ZenDriver 版本 (17個函式) → `platforms/kktix.py`
- `async nodriver_kktix_main()` - 主控制器 ✅
- `async nodriver_kktix_signin()` - 登入 ✅
- `async nodriver_kktix_paused_main()` - 暫停主流程 ✅
- `async nodriver_kktix_travel_price_list()` - 遍歷票價清單 ✅
- `async nodriver_kktix_assign_ticket_number()` - 設定票券數量 ✅
- `async nodriver_kktix_reg_captcha()` - 註冊驗證碼處理(含自動答題功能) ✅
- `async nodriver_kktix_date_auto_select()` - 日期自動選擇 ✅
- `async nodriver_kktix_events_press_next_button()` - 活動頁下一步 ✅
- `async nodriver_kktix_check_guest_modal()` - 訪客模態框檢查 ✅
- `async nodriver_kktix_press_next_button()` - 按下下一步按鈕 ✅
- `async nodriver_kktix_check_ticket_page_status()` - 票券頁狀態檢查 ✅
- `async nodriver_kktix_reg_new_main()` - 新註冊主流程 ✅
- `async nodriver_kktix_booking_main()` - 訂票主流程 ✅
- `async nodriver_kktix_confirm_order_button()` - 確認訂單按鈕 ✅
- `async nodriver_kktix_order_member_code()` - 會員序號 ✅
- `async nodriver_kktix_check_form_state()` - 表單狀態單一來源（票數/條款/資格）✅
- `async nodriver_kktix_check_qualification()` - 購票資格狀態 ✅
- `async nodriver_kktix_check_form_ready()` - 表單是否全部就緒 ✅
- `async nodriver_kktix_select_qualification()` - 選取購票資格 radio ✅
- `async nodriver_kktix_wait_member_code_enabled()` - 等待序號欄位解鎖 ✅
- `async nodriver_kktix_handle_qualification_and_next()` - 資格處理與送出編排 ✅
- `is_kktix_account_configured()` - 帳號是否已設定（三處呼叫的單一判定）✅
- `async debug_kktix_page_state()` - 除錯頁面狀態 ✅
- `check_kktix_got_ticket()` - 檢查是否取得票券 ✅

### KKTIX 差異分析
✅ **已實作：15/17** (完整度: 88%)
✅ **已完成功能：**
- 主控制器、登入、日期選擇、票價遍歷
- 票券數量設定、驗證碼處理（含自動答題）
- 活動頁處理、確認訂單按鈕
- 訪客模態框、票券頁狀態檢查
- 訂票主流程、會員代碼

**🎯 重大更新記錄：**
- **2025.11.03**: 新增 KKTIX 自動答題功能（Feature Branch: 004-kktix-auto-answer）
  - 功能：自動偵測 KKTIX 驗證問題、推測答案、模擬人類填寫
  - 實作位置：`nodriver_kktix_reg_captcha()`
  - 核心機制：
    - 問題偵測與記錄（自動寫入 question.txt）
    - 答案推測邏輯（複用 util.py 函數）
    - 人類化填寫（逐字輸入、隨機延遲 0.3-1.0 秒）
    - 失敗重試機制（維護 fail_list，跳過已失敗答案）
  - 配置項目：`advanced.auto_guess_options`（預設 false）、`advanced.user_guess_string`、`advanced.verbose`
  - 相關文件：[NoDriver API Guide - KKTIX 自動答題流程](../06-api-reference/nodriver_api_guide.md#kktix-自動答題流程)
  - 規格文件：`specs/004-kktix-auto-answer/`（spec.md、plan.md、tasks.md）

---

## 3. 年代售票 (ticket.com.tw)

### Chrome 版本 (7個函式)
- `ticket_seat_type_auto_select()` - 自動選擇票別
- `ticket_find_best_seats()` - 尋找最佳座位
- `ticket_seat_auto_select()` - 自動選擇座位
- `ticket_seat_main()` - 座位選擇主流程
- `ticket_allow_not_adjacent_seat()` - 允許非相鄰座位
- `ticket_switch_to_auto_seat()` - 切換到自動選座
- `ticket_login()` - 登入

### ZenDriver 版本 (8個函式, platforms/kham.py)
- `nodriver_ticket_login()` - 登入
- `nodriver_ticket_seat_type_auto_select()` - 自動選擇票別
- `nodriver_ticket_seat_auto_select()` - 自動選擇座位
- `nodriver_ticket_seat_main()` - 座位選擇主流程
- `nodriver_ticket_check_seat_taken_dialog()` - 座位佔用對話框
- `nodriver_ticket_close_dialog_with_retry()` - 重試關閉對話框
- `nodriver_ticket_allow_not_adjacent_seat()` - 允許非相鄰座位
- `nodriver_ticket_switch_to_auto_seat()` - 切換到自動選座

### 年代售票實作狀態
✅ **已實作：8/7** (完整度: 100%)
✅ **完整雙版本支援** - Chrome 和 ZenDriver 版本功能一致
- 完整的座位選擇邏輯
- 票別自動選擇
- 登入功能
- ZenDriver 額外新增：座位佔用對話框檢查、重試關閉對話框

---

## 4. 寬宏售票 (kham.com.tw)

### Chrome 版本 (14個函式)
- `kham_product()` - 產品頁處理
- `kham_area_auto_select()` - 自動選擇區域
- `kham_switch_to_auto_seat()` - 切換自動選座
- `kham_performance()` - 演出處理
- `kham_keyin_captcha_code()` - 手動輸入驗證碼
- `kham_auto_ocr()` - 自動 OCR
- `kham_captcha()` - 驗證碼處理
- `kham_check_captcha_text_error()` - 檢查驗證碼錯誤
- `kham_check_realname_dialog()` - 檢查實名對話框
- `kham_allow_not_adjacent_seat()` - 允許非相鄰座位
- `kham_main()` - 主控制器
- `kham_login()` - 登入
- `get_tixcraft_target_area()` - 目標區域選擇
- `assign_ticket_number_by_select()` - 透過選擇器設定票數

### ZenDriver 版本 (17個函式) - ✅ **完整實作**（檔案：`src/platforms/kham.py`）
- `nodriver_kham_main()` - 主控制器
- `nodriver_kham_login()` - 登入
- `nodriver_kham_go_buy_redirect()` - 購買重定向
- `nodriver_kham_check_realname_dialog()` - 實名對話框
- `nodriver_kham_allow_not_adjacent_seat()` - 非相鄰座位
- `nodriver_kham_switch_to_auto_seat()` - 切換自動選座
- `nodriver_kham_check_captcha_text_error()` - 驗證碼錯誤檢查
- `nodriver_kham_product()` - 產品頁
- `nodriver_kham_date_auto_select()` - 日期選擇
- `nodriver_kham_keyin_captcha_code()` - 驗證碼輸入
- `nodriver_kham_area_auto_select()` - 區域選擇
- `nodriver_kham_auto_ocr()` - 自動 OCR
- `nodriver_kham_captcha()` - 驗證碼處理
- `nodriver_kham_performance()` - 演出處理
- `nodriver_kham_seat_type_auto_select()` - 票種選擇
- `nodriver_kham_seat_auto_select()` - 座位選擇
- `nodriver_kham_seat_main()` - 座位選擇主流程

### 寬宏售票差異分析
✅ **已實作：17/14** (完整度: 98%)
✅ **核心功能完整：**
- 完整的主控制流程、OCR 驗證碼處理
- 實名制對話框處理、座位選擇邏輯
- ZenDriver 額外新增座位選擇模組（含 UDN 共用）

---

## 5. iBon 售票

### Chrome 版本 (15個函式)
- `ibon_main()` - 主控制器
- `ibon_date_auto_select()` - 自動選擇日期
- `ibon_area_auto_select()` - 自動選擇區域
- `ibon_ticket_number_appear()` - 票數選項出現檢查
- `ibon_ticket_number_auto_select()` - 自動選擇票數
- `ibon_allow_not_adjacent_seat()` - 允許非相鄰座位
- `ibon_performance()` - 演出處理
- `ibon_purchase_button_press()` - 按下購買按鈕
- `get_ibon_question_text()` - 取得問題文字
- `ibon_verification_question()` - 驗證問題
- `ibon_ticket_agree()` - 同意條款
- `ibon_check_sold_out()` - 檢查售完
- `ibon_keyin_captcha_code()` - 手動輸入驗證碼
- `ibon_auto_ocr()` - 自動 OCR
- `ibon_captcha()` - 驗證碼處理

### ZenDriver 版本 (24個函式, platforms/ibon.py)
- `async nodriver_ibon_login()` - Cookie 登入處理 ✅
- `async nodriver_ibon_date_auto_select_pierce()` - 日期選擇 Shadow DOM 穿透 ✅
- `async nodriver_ibon_date_auto_select()` - 日期自動選擇 ✅
- `async nodriver_ibon_date_auto_select_domsnapshot()` - DOMSnapshot 快照 ✅
- `async nodriver_ibon_ticket_agree()` - 同意條款 ✅
- `async nodriver_ibon_allow_not_adjacent_seat()` - 非連續座位 ✅
- `async nodriver_ibon_event_area_auto_select()` - Angular SPA Event 區域選擇 ✅
- `async nodriver_ibon_area_auto_select()` - 座位區域自動選擇 ✅
- `async nodriver_ibon_ticket_number_auto_select()` - 票數自動設定 ✅
- `async nodriver_ibon_keyin_captcha_code()` - 驗證碼輸入 ✅
- `async nodriver_ibon_refresh_captcha()` - 刷新驗證碼 ✅
- `async nodriver_ibon_auto_ocr()` - OCR 自動識別 ✅
- `async nodriver_ibon_captcha()` - 驗證碼主控制 ✅
- `async nodriver_ibon_purchase_button_press()` - 購票按鈕 ✅
- `async nodriver_ibon_check_sold_out()` - 售罄檢查 ✅
- `async nodriver_ibon_wait_for_select_elements()` - 等待選擇元素 ✅
- `async nodriver_ibon_check_sold_out_on_ticket_page()` - 票券頁售罄檢查 ✅
- `async nodriver_ibon_navigate_on_sold_out()` - 售罄導航 ✅
- `async nodriver_ibon_fill_verify_form()` - 驗證表單填寫 ✅
- `async nodriver_ibon_verification_question()` - 驗證問題 ✅
- `async nodriver_tour_ibon_event_detail()` - iBon Tour 活動詳情 ✅
- `async nodriver_tour_ibon_options()` - iBon Tour 選項 ✅
- `async nodriver_tour_ibon_checkout()` - iBon Tour 結帳 ✅
- `async nodriver_ibon_main()` - 主控制器 ✅

### iBon 差異分析
🥇 **實際狀態：25/15** (完整度: 95% - 金級)

**✅ 已完整實作（25 個函式，核心搶票流程 100% 完成）：**
- **登入功能**：Cookie 處理、頁面重新載入和登入狀態驗證
- **日期選擇**：使用 DOMSnapshot 平坦化策略穿透 closed Shadow DOM
- **座位區域選擇**：支援 Angular SPA Event 頁面 + .aspx 頁面
- **驗證碼處理**：Shadow DOM 截圖、OCR、輸入、重試
- **售罄處理**：售罄檢查、票券頁售罄、售罄導航
- **iBon Tour 模組**：活動詳情、選項、結帳
- **同意條款**：簡單但完整的勾選實作

---

## 6. Cityline (香港)

### Chrome 版本 (15個函式)
- `cityline_main()` - 主控制器
- `cityline_date_auto_select()` - 自動選擇日期
- `cityline_area_auto_select()` - 自動選擇區域
- `cityline_area_selected_text()` - 區域選中文字
- `cityline_ticket_number_auto_select()` - 自動選擇票數
- `cityline_purchase_button_press()` - 按下購買按鈕
- `cityline_next_button_press()` - 按下下一步按鈕
- `cityline_performance()` - 演出處理
- `cityline_login()` - 登入
- `cityline_shows_goto_cta()` - 前往 CTA
- `cityline_cookie_accept()` - 接受 Cookie
- `cityline_auto_retry_access()` - 自動重試存取
- `cityline_clean_ads()` - 清除廣告
- `cityline_input_code()` - 輸入代碼
- `cityline_close_second_tab()` - 關閉第二個標籤

### ZenDriver 版本 (17個函式, platforms/cityline.py)
- `async nodriver_cityline_main()` - 主控制器 ✅
- `async nodriver_cityline_auto_retry_access()` - 自動重試存取 ✅
- `async nodriver_cityline_login()` - 登入 ✅
- `async nodriver_cityline_date_auto_select()` - 自動選擇日期 ✅
- `async nodriver_cityline_check_login_modal()` - 登入模態框檢查 ✅
- `async nodriver_cityline_continue_button_press()` - 繼續按鈕 ✅
- `async nodriver_cityline_area_auto_select()` - 自動選擇區域 ✅
- `async nodriver_cityline_ticket_number_auto_select()` - 自動選擇票數 ✅
- `async nodriver_cityline_next_button_press()` - 下一步按鈕 ✅
- `async nodriver_cityline_performance()` - 演出處理 ✅
- `async nodriver_cityline_check_shopping_basket()` - 購物籃檢查 ✅
- `async nodriver_check_modal_dialog_popup()` - 模態對話框（nodriver_common.py 共用） ✅
- `async nodriver_cityline_purchase_button_press()` - 購買按鈕 ✅
- `async nodriver_cityline_close_second_tab()` - 關閉第二個標籤 ✅
- `async nodriver_cityline_cookie_accept()` - 接受 Cookie ✅
- `async nodriver_cityline_press_buy_button()` - 購買按鈕 ✅
- `async nodriver_cityline_clean_ads()` - 清除廣告 ✅

### Cityline 差異分析
✅ **已實作：17/15** (完整度: 80%)
✅ **已完成功能：**
- 主控制器、登入、日期選擇
- 區域自動選擇、票數自動設定
- 購買按鈕處理、Cookie 接受
- 廣告清除、模態對話框處理
- 購物籃檢查、登入模態框

---

## 7. UrBtix (香港)

### Chrome 版本 (11個函式)
- `urbtix_main()` - 主控制器
- `urbtix_date_auto_select()` - 自動選擇日期
- `urbtix_area_auto_select()` - 自動選擇區域
- `urbtix_purchase_ticket()` - 購買票券
- `urbtix_ticket_number_auto_select()` - 自動選擇票數
- `urbtix_uncheck_adjacent_seat()` - 取消相鄰座位
- `urbtix_performance()` - 演出處理
- `urbtix_login()` - 登入
- `urbtix_performance_confirm_dialog_popup()` - 確認對話框
- `get_urbtix_survey_answer_by_question()` - 根據問題取得調查答案
- `urbtix_auto_survey()` - 自動調查

### ZenDriver 版本
❌ **完全缺失** - UrBtix 在 ZenDriver 版本中完全沒有實作

### UrBtix 差異分析
✅ **已實作：0/11** (完整度: 0%)
❌ **需要移植的關鍵功能：**
- 完整的購票流程
- 調查問卷自動填寫
- 座位選擇邏輯

---

## 8. HKTicketing (香港)

### Chrome 版本 (20個函式)
- `hkticketing_main()` (透過 chrome_main 調用)
- `hkticketing_accept_cookie()` - 接受 Cookie
- `hkticketing_date_buy_button_press()` - 按下日期購買按鈕
- `hkticketing_date_assign()` - 指定日期
- `hkticketing_date_password_input()` - 日期密碼輸入
- `hkticketing_date_auto_select()` - 自動選擇日期
- `hkticketing_area_auto_select()` - 自動選擇區域
- `hkticketing_ticket_number_auto_select()` - 自動選擇票數
- `hkticketing_nav_to_footer()` - 導航到頁尾
- `hkticketing_next_button_press()` - 按下下一步按鈕
- `hkticketing_go_to_payment()` - 前往付款
- `hkticketing_ticket_delivery_option()` - 票券配送選項
- `hkticketing_hide_tickets_blocks()` - 隱藏票券區塊
- `hkticketing_performance()` - 演出處理
- `hkticketing_escape_robot_detection()` - 避開機器人偵測
- `hkticketing_url_redirect()` - URL 重定向
- `hkticketing_content_refresh()` - 內容重新整理
- `hkticketing_travel_iframe()` - 遍歷 iframe
- `hkticketing_login()` - 登入
- `get_ticketmaster_target_area()` - 共用目標區域取得

### ZenDriver 版本 (30個函式, platforms/hkticketing.py) - v2025.11.28 新增
- `nodriver_hkticketing_main()` - 主控制器
- `nodriver_hkticketing_login()` - 登入
- `nodriver_hkticketing_accept_cookie()` - 接受 Cookie
- `nodriver_hkticketing_date_buy_button_press()` - 按下日期購買按鈕
- `nodriver_hkticketing_date_assign()` - 指定日期
- `nodriver_hkticketing_date_password_input()` - 日期密碼輸入
- `nodriver_hkticketing_date_auto_select()` - 自動選擇日期
- `nodriver_hkticketing_area_auto_select()` - 自動選擇區域
- `nodriver_hkticketing_ticket_number_auto_select()` - 自動選擇票數
- `nodriver_hkticketing_ticket_delivery_option()` - 票券配送選項
- `nodriver_hkticketing_next_button_press()` - 按下下一步按鈕
- `nodriver_hkticketing_go_to_payment()` - 前往付款
- `nodriver_hkticketing_hide_tickets_blocks()` - 隱藏票券區塊
- `nodriver_hkticketing_type02_clear_session()` - Type02 清除 Session
- `nodriver_hkticketing_type02_check_traffic_overload()` - Type02 流量超載檢查
- `nodriver_hkticketing_type02_login()` - Type02 登入
- `nodriver_hkticketing_type02_dismiss_modal()` - Type02 關閉模態框
- `nodriver_hkticketing_type02_event_page_buy_button()` - Type02 活動頁購買按鈕
- `nodriver_hkticketing_type02_event_page()` - Type02 活動頁
- `nodriver_hkticketing_type02_date_assign()` - Type02 日期指定
- `nodriver_hkticketing_type02_area_auto_select()` - Type02 區域選擇
- `nodriver_hkticketing_type02_ticket_number_select()` - Type02 票數選擇
- `nodriver_hkticketing_type02_next_button_press()` - Type02 下一步按鈕
- `nodriver_hkticketing_type02_performance()` - Type02 演出處理
- `nodriver_hkticketing_type02_confirm_order()` - Type02 確認訂單
- `nodriver_hkticketing_performance()` - 演出處理
- `nodriver_hkticketing_escape_robot_detection()` - 避開機器人偵測
- `nodriver_hkticketing_url_redirect()` - URL 重定向
- `nodriver_hkticketing_content_refresh()` - 內容重新整理
- `nodriver_hkticketing_travel_iframe()` - 遍歷 iframe

### HKTicketing 差異分析
✅ **已實作：30/20** (完整度: 95%)
✅ **完整移植功能：**
- 完整的購票流程（日期選擇、區域選擇、票數設定、訂單送出）
- 機器人偵測規避
- iframe 錯誤檢測
- 密碼輸入邏輯
- Fallback 遞補機制（date_auto_fallback、area_auto_fallback）
- 支援子網站：Galaxy Macau、Ticketek Australia
- **新增 Type02 模組**（12 個函式）：支援新版 HKTicketing 網站

---

## 9. TicketPlus (遠大)

### Chrome 版本 (25個函式)
- `ticketplus_main()` - 主控制器
- `ticketplus_date_auto_select()` - 自動選擇日期
- `ticketplus_assign_ticket_number()` - 設定票券數量
- `ticketplus_order_expansion_auto_select()` - 訂單展開自動選擇
- `ticketplus_order_expansion_panel()` - 訂單展開面板
- `ticketplus_order_exclusive_code()` - 訂單專屬代碼
- `ticketplus_order_auto_reload_coming_soon()` - 即將開賣自動重載
- `ticketplus_order()` - 訂單處理
- `ticketplus_order_ocr()` - 訂單 OCR
- `ticketplus_auto_ocr()` - 自動 OCR
- `ticketplus_check_and_renew_captcha()` - 檢查並更新驗證碼
- `ticketplus_keyin_captcha_code()` - 手動輸入驗證碼
- `ticketplus_account_auto_fill()` - 帳號自動填入
- `ticketplus_account_sign_in()` - 帳號登入
- `ticketplus_accept_realname_card()` - 接受實名卡
- `ticketplus_accept_other_activity()` - 接受其他活動
- `ticketplus_accept_order_fail()` - 接受訂單失敗
- `ticketplus_ticket_agree()` - 同意條款
- `ticketplus_confirm()` - 確認
- `get_chrome_options()` - 取得 Chrome 選項 (共用)
- `chrome_main()` - Chrome 主函式 (共用)
- `assign_ticket_number_by_select()` - 透過選擇器設定票數 (共用)
- `get_target_item_from_matched_list()` - 從匹配清單取得目標項目 (共用)
- `play_sound_while_ordering()` - 訂票時播放聲音 (共用)
- `send_discord_notification()` - 發送 Discord Webhook 通知 (共用)

### ZenDriver 版本 (18個函式, platforms/ticketplus.py)
- `async nodriver_ticketplus_main()` - 主控制器 ✅
- `async nodriver_ticketplus_detect_layout_style()` - 偵測版面樣式 ✅
- `async nodriver_ticketplus_account_sign_in()` - 帳號登入 ✅
- `async nodriver_ticketplus_is_signin()` - 檢查登入狀態 ✅
- `async nodriver_ticketplus_account_auto_fill()` - 帳號自動填入 ✅
- `async nodriver_ticketplus_date_auto_select()` - 自動選擇日期 ✅
- `async nodriver_ticketplus_unified_select()` - 統一選擇器 ✅
- `async nodriver_ticketplus_click_next_button_unified()` - 統一下一步點擊 ✅
- `async nodriver_ticketplus_ticket_agree()` - 同意條款 ✅
- `async nodriver_ticketplus_accept_realname_card()` - 接受實名卡 ✅
- `async nodriver_ticketplus_accept_other_activity()` - 接受其他活動 ✅
- `async nodriver_ticketplus_accept_order_fail()` - 接受訂單失敗 ✅
- `async nodriver_ticketplus_check_queue_status()` - 排隊狀態檢查 ✅
- `async nodriver_ticketplus_confirm()` - 確認 ✅
- `async nodriver_ticketplus_order()` - 訂單處理 ✅
- `async nodriver_ticketplus_wait_for_vue_ready()` - Vue 準備狀態等待 ✅
- `async nodriver_ticketplus_check_next_button()` - 檢查下一步按鈕 ✅
- `async nodriver_ticketplus_order_exclusive_code()` - 訂單專屬代碼 ✅

### TicketPlus 差異分析
✅ **已實作：18/25** (完整度: 95% - **實際測試完全可用**)
✅ **核心功能完整：**
- 登入系統、日期選擇、區域選擇完整
- 同意條款處理完整
- 實名卡與其他活動處理完整
- 排隊狀態檢查與確認完整

➕ **ZenDriver 額外功能：**
- `detect_layout_style()` - 版面樣式偵測
- `is_signin()` - 登入狀態檢查
- `unified_select()` - 統一選擇器
- `check_queue_status()` - 排隊狀態檢查
- `wait_for_vue_ready()` - Vue 準備狀態等待

ℹ️ **暫時忽略 - OCR 驗證碼處理** (4 個函式，目前無需求):
- `nodriver_ticketplus_auto_ocr()` - 自動 OCR 識別 ⏸️
- `nodriver_ticketplus_order_ocr()` - 訂單 OCR 處理 ⏸️
- `nodriver_ticketplus_keyin_captcha_code()` - 手動輸入驗證碼 ⏸️
- `nodriver_ticketplus_check_and_renew_captcha()` - 驗證碼刷新 ⏸️

**說明：** 目前 TicketPlus 活動不使用 OCR 驗證碼機制，這 4 個函式缺失不影響實際搶票功能

**評估結果：** ZenDriver 版本**可完全正常搶票使用**，實測通過

---

## 10. FamiTicket (全網) - 🏅 白金級

### Chrome 版本 (10個函式)
- `famiticket_main()` - 主控制器
- `get_fami_target_area()` - 取得目標區域
- `fami_verify()` - 驗證處理
- `fami_activity()` - 活動處理
- `fami_date_auto_select()` - 自動選擇日期
- `fami_area_auto_select()` - 自動選擇區域
- `fami_date_to_area()` - 從日期到區域
- `fami_home_auto_select()` - 首頁自動選擇
- `fami_login()` - 登入
- `assign_ticket_number_by_select()` - 透過選擇器設定票數 (共用)

### ZenDriver 版本 (9個函式, platforms/famiticket.py) - ✅ **2025-11-24 完成**
- `nodriver_famiticket_main()` - 主控制器（URL 路由器）
- `nodriver_fami_login()` - 帳號密碼登入（HTTP-Only Cookie）
- `nodriver_fami_activity()` - 活動頁面處理
- `nodriver_fami_verify()` - 驗證問題/實名認證
- `nodriver_fami_date_auto_select()` - 日期選擇+條件回退
- `nodriver_fami_area_auto_select()` - 區域選擇+AND邏輯
- `nodriver_fami_date_to_area()` - 日期/區域協調器
- `nodriver_fami_ticket_select()` - 票種選擇頁面
- `nodriver_fami_home_auto_select()` - 首頁入口分派

### FamiTicket 差異分析
✅ **已實作：9/10** (完整度: 100% - 🏅 白金級)
✅ **核心功能完整：**
- 登入系統（帳號密碼 + HTTP-Only Cookie）
- 日期選擇（關鍵字匹配 + `date_auto_fallback` 條件回退）
- 區域選擇（AND 邏輯 + `area_auto_fallback` 條件回退）
- 驗證問題自動填寫
- 票種選擇與結帳流程

**🎯 重大更新記錄：**
- **2025-11-24**: 完成 FamiTicket ZenDriver 完整實作
  - 9 個函數全面實作
  - 使用 ZenDriver 官方 API（`query_selector_all`、`wait_for`）
  - 隨機延遲 0.4-1.2 秒模擬人類操作（反爬蟲）
  - 完整文檔記錄：詳見內部疑難排解文件

---

## 11. Ticketmaster (國際)

### Chrome 版本 (9個函式)
- `ticketmaster_date_auto_select()` - 自動選擇日期
- `get_ticketmaster_target_area()` - 取得目標區域
- `ticketmaster_area_auto_select()` - 自動選擇區域
- `ticketmaster_promo()` - 促銷代碼
- `ticketmaster_parse_zone_info()` - 解析區域資訊
- `ticketmaster_get_ticketPriceList()` - 取得票價清單
- `ticketmaster_assign_ticket_number()` - 設定票券數量
- `ticketmaster_captcha()` - 驗證碼處理
- `get_target_item_from_matched_list()` - 從匹配清單取得目標項目 (共用)

### ZenDriver 版本 (8個函式, platforms/tixcraft.py) ✅ **2025-11-18 完成**
- `async nodriver_ticketmaster_promo()` - 促銷代碼 ✅
- `async nodriver_ticketmaster_parse_zone_info()` - 解析區域資訊 ✅
- `get_ticketmaster_target_area()` - 取得目標區域 ✅
- `async nodriver_ticketmaster_get_ticketPriceList()` - 取得票價清單 ✅
- `async nodriver_ticketmaster_date_auto_select()` - 自動選擇日期 ✅
- `async nodriver_ticketmaster_area_auto_select()` - 自動選擇區域 ✅
- `async nodriver_ticketmaster_assign_ticket_number()` - 設定票券數量 ✅
- `async nodriver_ticketmaster_captcha()` - 驗證碼處理 ✅

### Ticketmaster 差異分析
✅ **已實作：8/9** (完整度: 89%)
✅ **已實作功能：**
- 日期自動選擇（含 Early Return Pattern、date_auto_fallback）
- 區域自動選擇（含 Early Return Pattern、area_auto_fallback、關鍵字增強解析）
- 票價解析
- 票券數量設定
- 驗證碼處理（含 OCR 自動辨識、錯誤重試、Modal 處理）
- 區域資訊解析

⚠️ **待改進：**
- Modal 錯誤檢查（'list' object has no attribute 'get' 錯誤）

---

## 實作品質分析

### 實作可信度評估

| 平台 | 函式數量 | 檔案 | 可信度 | 建議 |
|------|----------|------------|--------|------|
| Tixcraft | 19 | platforms/tixcraft.py | 高 | 實測通過，可直接使用 |
| KKTIX | 17 | platforms/kktix.py | 高 | 實測通過，可直接使用 |
| iBon | 25 | platforms/ibon.py | 🥇 極高 | **金級實作，可直接使用** |
| Cityline | 17 | platforms/cityline.py | 中等 | 大部分功能可用，需補完 |
| TicketPlus | 18 | platforms/ticketplus.py | 高 | 實測通過，可直接使用 |
| Ticketmaster | 8 | platforms/tixcraft.py | 高 | 實測通過，可直接使用 |
| KHAM | 21 | platforms/kham.py | 🥇 極高 | 白金級實作 |
| FamiTicket | 9 | platforms/famiticket.py | 🥇 極高 | 白金級實作 |
| HKTicketing | 30 | platforms/hkticketing.py | 🥇 極高 | 白金級實作 |
| FunOne | 18 | platforms/funone.py | 高 | 完整實作 |
| Fansigo | 9 | platforms/fansigo.py | 高 | 完整實作 |

---

## 重構建議與評估

### 1. 實作優先度

**Phase 1（緊急）**：
1. **Cityline 功能補完** - 補完缺失功能（60% → 85%）

**Phase 2（重要）**：
2. **Urbtix 完整移植** - 香港重要平台，Chrome 已有 11 個完整函式

**Phase 3（次要）**：
3. ⏸️ **TicketPlus OCR** - 暫時忽略（目前無需求，Chrome 有 4 個函式可參考）

### 2. 可共用函式識別
以下函式具有共用潛力，可考慮抽象化：
- **OCR 相關**：`*_auto_ocr()`, `*_get_ocr_answer()`, `*_keyin_captcha_code()`
- **登入相關**：`*_login()`, `*_account_sign_in()`
- **票券選擇**：`*_assign_ticket_number()`, `*_ticket_number_auto_select()`
- **同意條款**：`*_ticket_agree()`, `*_check_agree_checkbox()`
- **按鈕操作**：`*_press_next_button()`, `*_purchase_button_press()`

### 3. 架構改善建議
1. **建立基礎類別**：抽象化共同的購票流程
2. **統一介面**：標準化各平台的主要函式介面
3. **模組化設計**：將 OCR、登入、選票等功能模組化
4. **狀態管理**：統一管理購票狀態與重試邏輯

---

---

## 🎯 **使用方式**

1. **定位功能**：根據平台名稱找到對應函數（ZenDriver 版本優先）
2. **定位代碼**：依檔案歸屬開啟對應模組檔案
3. **版本對比**：比較 ZenDriver 與 Chrome 版本差異
4. **缺失識別**：快速識別未實作功能位置
5. **開發優先度**：優先開發和維護 ZenDriver 版本功能

此文件可作為開發和除錯時的快速參考工具。

---

*此文件最後更新：2026-06-10（移除行號引用，改以檔案歸屬索引）*
*分析基於：src/nodriver_tixcraft.py + src/platforms/*.py + src/nodriver_common.py*
*整合內容：標準功能架構定義 + 平台函數索引 + 功能完整度評分 + 結構差異分析*
*相關文件：[標準功能定義](./ticket_automation_standard.md) | [開發規範](./development_guide.md) | [程式碼範本](./coding_templates.md)*

**🎯 重大更新（2026.03.05）：函數行號引用全面更新**
- **檔案規模**：nodriver_tixcraft.py 從 26,357 行縮減至 19,049 行（6 個平台已拆分至 platforms/）
- **新增平台**：FunOne Tickets (18 函式)、Fansigo (9 函式)
- **新增模組**：HKTicketing Type02 (12 函式)、iBon Tour (3 函式)、UDN 座位選擇 (3 函式)
- **已移除函式**：`nodriver_ticketplus_order_expansion_auto_select`、`nodriver_ticketplus_assign_ticket_number`、`nodriver_ticketplus_order_auto_reload_coming_soon`
- **行號更新**：所有平台函數行號引用已更新至最新版本，確保文件與代碼同步
