# ZenDriver vs Chrome 函式結構分析與平台索引

**文件說明**：提供 Tickets Hunter 專案的模組結構、核心函數索引、平台實作分析與功能完整度評分
**最後更新**：2026-03-05

---

此文件整合了以下內容（以 ZenDriver 為主要開發目標）：
1. **標準功能架構** - 完整的搶票程式應包含的功能模組定義
2. **平台函數索引** - 快速定位各平台函數行號位置
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
- **nodriver_tixcraft.py** - NoDriver 版本主迴圈 + URL 路由 (~827 行)
- **nodriver_common.py** - 共用瀏覽器基礎設施（DOM 工具、暫停機制、Cloudflare、初始化）
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

> 此部分作為函數定位工具，可根據行號快速跳轉到特定功能
>
> **重要說明**：依照 ZenDriver First 開發策略，以下所有平台章節皆以 **ZenDriver 版本優先列出**，Chrome Driver 版本作為參考對照。建議優先查閱和開發 ZenDriver 版本功能。

### 🎫 **TixCraft 拓元**

#### ZenDriver
```
拓元主流程
├── nodriver_tixcraft_main               # 行 5878
├── nodriver_tixcraft_date_auto_select   # 行 4564
├── nodriver_tixcraft_area_auto_select   # 行 4871
├── nodriver_get_tixcraft_target_area    # 行 4992
├── nodriver_tixcraft_assign_ticket_number # 行 5189 ✅ (v1.3+ 支援 Indievox 票種關鍵字匹配)
├── nodriver_tixcraft_ticket_main        # 行 5459
├── nodriver_tixcraft_ticket_main_agree  # 行 5443
├── nodriver_tixcraft_verify             # 行 4396
├── nodriver_fill_verify_form            # 行 4400
├── nodriver_tixcraft_input_check_code   # 行 4531
├── nodriver_tixcraft_ticket_main_ocr    # 行 5800
├── nodriver_tixcraft_keyin_captcha_code # 行 5520
├── nodriver_tixcraft_toast              # 行 5652
├── nodriver_tixcraft_reload_captcha     # 行 5666
├── nodriver_tixcraft_get_ocr_answer     # 行 5684
├── nodriver_tixcraft_auto_ocr           # 行 5738
├── nodriver_tixcraft_home_close_window  # 行 3004
├── nodriver_tixcraft_redirect           # 行 3031
└── nodriver_ticket_number_select_fill   # 行 5113
```

#### Chrome
```
拓元主流程
├── tixcraft_main                        # 行 5952
├── tixcraft_date_auto_select            # 行 967
├── tixcraft_area_auto_select            # 行 1535
├── get_tixcraft_target_area             # 行 1333
├── tixcraft_assign_ticket_number        # 行 2279
├── tixcraft_ticket_main                 # 行 2337
├── tixcraft_ticket_main_agree           # 行 2153
├── tixcraft_verify                      # 行 1876
├── tixcraft_auto_ocr                    # 行 2082
├── tixcraft_keyin_captcha_code          # 行 1934
└── tixcraft_ticket_main_ocr            # 行 2363
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
└── nodriver_facebook_login              # platforms/facebook.py
```

#### Chrome
```
KKTIX 主流程
├── kktix_main                           # 行 6117
├── kktix_paused_main                    # 行 6084
├── kktix_login                          # 行 5303
├── kktix_reg_new_main                   # 行 2888
├── kktix_travel_price_list              # 行 2456
├── kktix_assign_ticket_number           # 行 2661
├── kktix_reg_captcha                    # 行 2841
├── kktix_check_agree_checkbox           # 行 2720
└── kktix_press_next_button              # 行 2419
```

### 🎵 **TicketMaster**

#### ZenDriver
```
TicketMaster 功能 (整合在 nodriver_tixcraft_main)
├── nodriver_ticketmaster_promo                    # 行 4392
├── nodriver_ticketmaster_parse_zone_info          # 行 3254
├── get_ticketmaster_target_area                   # 行 3404
├── nodriver_ticketmaster_get_ticketPriceList      # 行 3572
├── nodriver_ticketmaster_date_auto_select         # 行 3668
├── nodriver_ticketmaster_area_auto_select         # 行 3888
├── nodriver_ticketmaster_assign_ticket_number     # 行 3987
└── nodriver_ticketmaster_captcha                  # 行 4121
```

#### Chrome
```
TicketMaster 功能 (整合在 tixcraft_main)
├── ticketmaster_date_auto_select        # 行 1204
├── ticketmaster_area_auto_select        # 行 1600
├── get_ticketmaster_target_area         # 行 1446
├── ticketmaster_assign_ticket_number    # 行 5845
├── ticketmaster_captcha                 # 行 5914
└── ticketmaster_promo                   # 行 1872
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
├── cityline_main                        # 行 6777
├── cityline_login                       # 行 5363
├── cityline_date_auto_select            # 行 4343
├── cityline_area_auto_select            # 行 4457
├── cityline_ticket_number_auto_select   # 行 4604
├── cityline_purchase_button_press       # 行 4693
├── cityline_next_button_press           # 行 4718
├── cityline_performance                 # 行 4754
└── cityline_input_code                  # 行 6733
```

### 💳 **iBon**

#### ZenDriver （🥇 金級實作 - 95% 完整度）
```
iBon 主流程
├── nodriver_ibon_login                      # 行 8094 ✅ (Cookie 登入)
├── nodriver_ibon_date_auto_select           # 行 9393 ✅ (v1.3+ 性能優化)
│   ├── nodriver_ibon_date_auto_select_pierce # 行 9085 (Shadow DOM 穿透)
│   └── nodriver_ibon_date_auto_select_domsnapshot # 行 9415 (DOMSnapshot 快照)
├── nodriver_ibon_event_area_auto_select     # 行 9774 ✅ (Angular SPA Event 頁面)
├── nodriver_ibon_area_auto_select           # 行 10217 ✅ (舊版 .aspx 頁面)
├── nodriver_ibon_ticket_number_auto_select  # 行 10791 ✅ (票數自動設定)
├── nodriver_ibon_get_captcha_image_from_shadow_dom # 行 11108 ✅ (Shadow DOM 截圖)
├── nodriver_ibon_keyin_captcha_code         # 行 11289 ✅ (驗證碼輸入)
├── nodriver_ibon_refresh_captcha            # 行 11524 ✅ (刷新驗證碼)
├── nodriver_ibon_auto_ocr                   # 行 11555 ✅ (OCR 自動識別)
├── nodriver_ibon_captcha                    # 行 11714 ✅ (驗證碼主控制)
├── nodriver_ibon_purchase_button_press      # 行 11803 ✅ (購票按鈕)
├── nodriver_ibon_check_sold_out             # 行 11858 ✅ (售罄檢查)
├── nodriver_ibon_wait_for_select_elements   # 行 11894 ✅ (等待選擇元素)
├── nodriver_ibon_check_sold_out_on_ticket_page # 行 11937 ✅ (票券頁售罄檢查)
├── nodriver_ibon_navigate_on_sold_out       # 行 12060 ✅ (售罄導航)
├── nodriver_ibon_fill_verify_form           # 行 12122 ✅ (驗證表單填寫)
├── nodriver_ibon_verification_question      # 行 12299 ✅ (驗證問題)
├── nodriver_ibon_ticket_agree               # 行 9739 ✅ (同意條款)
├── nodriver_ibon_allow_not_adjacent_seat    # 行 9745 ✅ (非連續座位)
│
├── iBon Tour 模組
├── nodriver_tour_ibon_event_detail          # 行 12442 ✅ (Tour 活動詳情)
├── nodriver_tour_ibon_options               # 行 12493 ✅ (Tour 選項)
├── nodriver_tour_ibon_checkout              # 行 12629 ✅ (Tour 結帳)
│
└── nodriver_ibon_main                       # 行 12763 ✅ (主流程完整)
```

#### Chrome
```
iBon 主流程
├── ibon_main                            # 行 7132
├── ibon_date_auto_select                # 行 4822
├── ibon_area_auto_select                # 行 4951
├── ibon_ticket_number_auto_select       # 行 4636
├── ibon_ticket_agree                    # 行 6900
├── ibon_captcha                         # 行 7098
├── ibon_auto_ocr                        # 行 6992
├── ibon_keyin_captcha_code              # 行 6928
├── ibon_purchase_button_press           # 行 5216
└── ibon_performance                     # 行 5167
```

### 🎭 **Urbtix**

#### Chrome
```
Urbtix 主流程
├── urbtix_main                          # 行 6589
├── urbtix_login                         # 行 5376
├── urbtix_date_auto_select              # 行 3806
├── urbtix_area_auto_select              # 行 3960
├── urbtix_ticket_number_auto_select     # 行 4117
├── urbtix_purchase_ticket               # 行 3945
├── urbtix_performance                   # 行 4285
└── urbtix_auto_survey                   # 行 6425
```

#### ZenDriver
```
❌ 完全未實作
```

### 🎪 **KHAM 寬宏售票**

#### ZenDriver
```
KHAM 主流程 (含 UDN 售票網、Ticket.com.tw)
├── nodriver_kham_main                   # 行 16011 ✅
├── nodriver_kham_login                  # 行 14685 ✅
├── nodriver_kham_date_auto_select       # 行 15045 ✅ (Feature 003: Early Return + Fallback)
├── nodriver_kham_go_buy_redirect        # 行 14821 ✅
├── nodriver_kham_check_realname_dialog  # 行 14876 ✅
├── nodriver_kham_allow_not_adjacent_seat # 行 14938 ✅
├── nodriver_kham_switch_to_auto_seat    # 行 14955 ✅
├── nodriver_kham_check_captcha_text_error # 行 14992 ✅
├── nodriver_kham_product                # 行 15025 ✅
├── nodriver_kham_area_auto_select       # 行 15421 ✅ (Feature 003: Early Return + Fallback)
├── nodriver_kham_keyin_captcha_code     # 行 15309 ✅
├── nodriver_kham_auto_ocr              # 行 15816 ✅
├── nodriver_kham_captcha                # 行 15890 ✅
├── nodriver_kham_performance            # 行 15934 ✅
│
├── 座位選擇模組 (KHAM/UDN/Ticket.com.tw 共用)
├── nodriver_kham_seat_main              # 行 18305 ✅ 座位選擇主流程
├── nodriver_kham_seat_auto_select       # 行 17941 ✅ 座位自動選擇核心
├── nodriver_kham_seat_type_auto_select  # 行 17616 ✅ 票種自動選擇
│
├── UDN 專屬座位選擇模組
├── nodriver_udn_seat_auto_select        # 行 18538 ✅ UDN 座位自動選擇
├── nodriver_udn_seat_select_ticket_type # 行 18658 ✅ UDN 票種選擇
└── nodriver_udn_seat_main              # 行 18798 ✅ UDN 座位選擇主流程
```

#### Chrome
```
KHAM 主流程
├── kham_main                            # 行 9644
├── kham_login                           # 行 5492
├── hkam_date_auto_select                # 行 8463
├── kham_go_buy_redirect                 # 行 8449
├── kham_product                         # 行 8646
├── kham_area_auto_select                # 行 8662
├── kham_switch_to_auto_seat             # 行 9230
├── kham_performance                     # 行 9307
├── kham_keyin_captcha_code              # 行 9359
├── kham_auto_ocr                        # 行 9426
├── kham_captcha                         # 行 9532
├── kham_check_captcha_text_error        # 行 9565
├── kham_check_realname_dialog           # 行 9592
└── kham_allow_not_adjacent_seat         # 行 9623
```

**UDN 專屬說明**：
- UDN 與 KHAM 共用 UTK 後端，座位選擇邏輯完全複用
- UDN 座位選擇模組：`nodriver_udn_seat_auto_select` (行 18538)、`nodriver_udn_seat_select_ticket_type` (行 18658)、`nodriver_udn_seat_main` (行 18798)
- 支援 Feature 003 遞補機制：`date_auto_fallback`、`area_auto_fallback`

### 🎫 **HK Ticketing**

#### ZenDriver
```
HKTicketing 主流程
├── nodriver_hkticketing_main           # 行 23131
├── nodriver_hkticketing_login          # 行 20778
├── nodriver_hkticketing_accept_cookie  # 行 20919
├── nodriver_hkticketing_date_buy_button_press # 行 20931
├── nodriver_hkticketing_date_assign    # 行 21004
├── nodriver_hkticketing_date_password_input # 行 21183
├── nodriver_hkticketing_date_auto_select # 行 21232
├── nodriver_hkticketing_area_auto_select # 行 21273
├── nodriver_hkticketing_ticket_number_auto_select # 行 21510
├── nodriver_hkticketing_ticket_delivery_option # 行 21558
├── nodriver_hkticketing_next_button_press # 行 21598
├── nodriver_hkticketing_go_to_payment  # 行 21662
├── nodriver_hkticketing_hide_tickets_blocks # 行 21709
├── nodriver_hkticketing_performance    # 行 22921
├── nodriver_hkticketing_escape_robot_detection # 行 22955
├── nodriver_hkticketing_url_redirect   # 行 22972
├── nodriver_hkticketing_content_refresh # 行 23032
├── nodriver_hkticketing_travel_iframe  # 行 23080
│
├── HKTicketing Type02 模組 (新版網站)
├── nodriver_hkticketing_type02_clear_session # 行 21735 ✅
├── nodriver_hkticketing_type02_check_traffic_overload # 行 21792 ✅
├── nodriver_hkticketing_type02_login   # 行 21851 ✅
├── nodriver_hkticketing_type02_dismiss_modal # 行 22003 ✅
├── nodriver_hkticketing_type02_event_page_buy_button # 行 22053 ✅
├── nodriver_hkticketing_type02_event_page # 行 22114 ✅
├── nodriver_hkticketing_type02_date_assign # 行 22144 ✅
├── nodriver_hkticketing_type02_area_auto_select # 行 22324 ✅
├── nodriver_hkticketing_type02_ticket_number_select # 行 22463 ✅
├── nodriver_hkticketing_type02_next_button_press # 行 22558 ✅
├── nodriver_hkticketing_type02_performance # 行 22594 ✅
└── nodriver_hkticketing_type02_confirm_order # 行 22644 ✅
```

#### Chrome
```
HK Ticketing 功能 (無獨立 main)
├── hkticketing_login                    # 行 5596
├── hkticketing_date_auto_select         # 行 7592
├── hkticketing_date_assign              # 行 7388
├── hkticketing_area_auto_select         # 行 7676
├── hkticketing_ticket_number_auto_select # 行 7816
├── hkticketing_performance              # 行 7953
├── hkticketing_next_button_press        # 行 7833
└── hkticketing_go_to_payment            # 行 7856
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
├── ticketplus_main                      # 行 11238
├── ticketplus_account_sign_in           # 行 11085
├── ticketplus_account_auto_fill         # 行 11005
├── ticketplus_date_auto_select          # 行 9862
├── ticketplus_assign_ticket_number      # 行 10030
├── ticketplus_order_expansion_auto_select # 行 10104
├── ticketplus_ticket_agree              # 行 11196
├── ticketplus_auto_ocr                  # 行 10732
├── ticketplus_keyin_captcha_code        # 行 10892
└── ticketplus_order_ocr                 # 行 10691
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
├── famiticket_main                      # 行 6250
├── fami_login                           # 行 6243
├── fami_date_auto_select                # 行 3321
├── fami_area_auto_select                # 行 3455
├── fami_verify                          # 行 3239
├── fami_activity                        # 行 3277
└── fami_home_auto_select                # 行 3651
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
├── ticket_login (Ticket.com.tw)         # 行 5501
├── udn_login (UDN)                      # 行 5562
├── facebook_login                       # 行 5296
├── facebook_main                        # 行 11328
└── softix_powerweb_main                 # 行 8239
```

#### ZenDriver
```
其他平台
├── nodriver_facebook_login              # platforms/facebook.py
├── nodriver_facebook_main               # platforms/facebook.py
├── nodriver_ticket_login                # nodriver_tixcraft.py
│
├── 年代售票 座位選擇模組
├── nodriver_ticket_seat_type_auto_select # 行 18866
├── nodriver_ticket_seat_auto_select     # 行 19891
├── nodriver_ticket_seat_main            # 行 19938
├── nodriver_ticket_check_seat_taken_dialog # 行 20168
├── nodriver_ticket_close_dialog_with_retry # 行 20218
├── nodriver_ticket_allow_not_adjacent_seat # 行 20263
└── nodriver_ticket_switch_to_auto_seat  # 行 20303
```

### 🔧 **共用工具函數**

#### ZenDriver
```
OCR 相關
├── nodriver_tixcraft_get_ocr_answer     # 行 5684
└── nodriver_force_check_checkbox        # 行 260

Cloudflare Turnstile
├── detect_cloudflare_challenge          # 行 350 ✅ (Cloudflare Turnstile 三層偵測)
├── _find_cf_iframe_in_dom              # 行 413 ✅ (DOM 樹遞迴搜尋 CF iframe)
├── _cdp_click                          # 行 446 ✅ (CDP 滑鼠事件封裝)
└── handle_cloudflare_challenge         # 行 459 ✅ (Cloudflare Turnstile 三階段處理)

輔助工具
├── play_sound_while_ordering            # 行 154
├── send_discord_notification            # 行 159
├── send_telegram_notification           # 行 172
├── nodriver_press_button                # 行 190
├── nodriver_check_checkbox              # 行 206
├── nodriver_check_checkbox_enhanced     # 行 293
├── nodriver_get_text_by_selector        # 行 3014
├── nodriver_goto_homepage               # 行 751
├── nodriver_resize_window               # 行 20545
├── nodriver_current_url                 # 行 20556
├── nodriver_overwrite_prefs             # 行 20591
└── cli                                  # 行 26289
```

#### util.py 共用函數
```
Debug 輸出
├── DebugLogger                          # class (行 1273) ✅ 統一除錯訊息管理
├── create_debug_logger(config_dict)     # factory (行 1291) ✅ 建立 DebugLogger 實例
└── get_debug_mode                       # 行 1245 ✅ 安全讀取 debug 模式設定

選擇模式與關鍵字處理
├── is_text_match_keyword                # 行 174 ✅ 關鍵字比對核心
├── get_matched_blocks_by_keyword        # 行 1334 ✅ 區域/日期關鍵字匹配
├── get_matched_blocks_by_keyword_item_set # 行 1129 ✅ 關鍵字集合匹配
├── get_target_index_by_mode             # 行 1176 ✅ 選擇模式索引計算
├── get_target_item_from_matched_list    # 行 1224 ✅ 從匹配列表取得目標項目
├── parse_keyword_string_to_array        # 行 1296 ✅ 統一 JSON 關鍵字解析
├── is_row_match_keyword                 # 行 1345 ✅ 行匹配檢查
└── reset_row_text_if_match_keyword_exclude # 行 1379 ✅ 排除關鍵字匹配檢查

字串處理
├── format_keyword_for_display           # 行 112
├── format_config_keyword_for_json       # 行 132
├── format_keyword_string                # 行 314
├── format_quota_string                  # 行 325
├── full2half                            # 行 351
├── find_between                         # 行 83
├── remove_html_tags                     # 行 74
├── find_continuous_number               # 行 408
├── find_continuous_text                 # 行 412
├── find_continuous_pattern              # 行 416
├── is_all_alpha_or_numeric              # 行 431
└── convert_string_to_pattern            # 行 473

中文數字處理
├── get_chinese_numeric                  # 行 364
├── synonym_dict                         # 行 379
├── chinese_numeric_to_int               # 行 388
└── normalize_chinese_numeric            # 行 400

OCR 與驗證碼
├── guess_answer_list_from_multi_options # 行 515
├── guess_answer_list_from_symbols       # 行 685
├── get_offical_hint_string_from_symbol  # 行 717
├── guess_answer_list_from_hint          # 行 755
├── format_question_string               # 行 1000
├── permutations                         # 行 1049
├── get_answer_list_by_question          # 行 1072
├── check_answer_keep_symbol             # 行 1506
├── kktix_get_web_datetime               # 行 1548
├── get_answer_string_from_web_date      # 行 1600
├── get_answer_string_from_web_time      # 行 1723
├── get_answer_list_from_question_string # 行 1809
├── guess_tixcraft_question              # 行 1384
├── get_answer_list_from_user_guess_string # 行 1423
└── extract_answer_by_question_pattern   # 行 1455

音訊與通知
├── play_mp3_async                       # 行 279
├── play_mp3                             # 行 282
├── build_discord_message                # 行 2190 ✅ Discord 訊息建構
├── send_discord_webhook                 # 行 2217 ✅ Discord Webhook 同步發送
├── send_discord_webhook_async           # 行 2260 ✅ Discord Webhook 非同步發送
├── build_telegram_message               # 行 2292 ✅ Telegram 訊息建構 (v2026.03)
├── send_telegram_message                # 行 2316 ✅ Telegram Bot 同步發送 (v2026.03)
└── send_telegram_message_async          # 行 2365 ✅ Telegram Bot 非同步發送 (v2026.03)

檔案 I/O
├── save_json                            # 行 231
├── write_string_to_file                 # 行 239
├── save_url_to_file                     # 行 249
└── force_remove_file                    # 行 297

系統工具
├── get_ip_address                       # 行 27
├── is_connectable                       # 行 56
├── is_arm                               # 行 93
├── get_app_root                         # 行 99
├── t_or_f                               # 行 305
├── get_brave_bin_path                   # 行 452
├── launch_maxbot                        # 行 2050
├── parse_nodriver_result                # 行 2100
└── get_token                            # 行 2183

KKTIX 專用
├── kktix_get_registerStatus             # 行 2001
└── kktix_get_event_code                 # 行 2036

Cloudflare 模板匹配
├── get_cf_template_paths                # 行 2398
└── verify_cf_with_templates             # 行 2426

iBon Livemap
├── ibon_fetch_and_parse_livemap         # 行 2494
├── ibon_livemap_select_area             # 行 2548
└── ibon_build_skip_url                  # 行 2593
```

### 🛑 **暫停機制輔助函數** (ZenDriver 專用)

> **位置**: `src/nodriver_tixcraft.py:7406-7470`

#### 核心暫停檢查函數

```
check_and_handle_pause(config_dict)      # 行 7406 ✅
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
sleep_with_pause_check(tab, seconds, config_dict)              # 行 7420 ✅
├── 取代 tab.sleep()
├── 等待期間檢查暫停狀態
└── 返回 True (暫停中) / False (正常)

asyncio_sleep_with_pause_check(seconds, config_dict)           # 行 7427 ✅
├── 取代 asyncio.sleep()
├── 不需要 tab 物件的純延遲
└── 返回 True (暫停中) / False (正常)

evaluate_with_pause_check(tab, javascript_code, config_dict)   # 行 7435 ✅
├── JavaScript 執行前檢查暫停
├── 暫停時返回 None
└── 正常時返回 JavaScript 執行結果

with_pause_check(task_func, config_dict, *args, **kwargs)      # 行 7449 ✅
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

| 平台 | Chrome 行數範圍 | ZenDriver 行數範圍 | 完整度 |
|------|:---------------:|:-----------------:|:------:|
| TixCraft | 967-5952 | platforms/tixcraft.py | ✅/✅ |
| KKTIX | 2419-6117 | platforms/kktix.py | ✅/✅ |
| TicketPlus | 9862-11238 | platforms/ticketplus.py | ✅/✅ |
| KHAM 寬宏 | 5492-9644 | platforms/kham.py | ✅/✅ |
| TicketMaster | 1204-5914 | platforms/tixcraft.py | ✅/✅ |
| Cityline | 4343-6777 | platforms/cityline.py | ✅/✅ |
| iBon | 4636-7132 | platforms/ibon.py | ✅/🥇 |
| FamiTicket | 3321-6250 | platforms/famiticket.py | ✅/🏅 |
| HK Ticketing | 5596-7953 | platforms/hkticketing.py | ✅/🏅 |
| FunOne | - | platforms/funone.py | -/✅ |
| Fansigo | - | platforms/fansigo.py | -/✅ |
| Urbtix | 3806-6589 | 未實作 | ✅/❌ |

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
**最新檔案大小：nodriver_tixcraft.py (19,049 行)**

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

### ZenDriver 版本 (19個函式)
- `async nodriver_tixcraft_main()` - 主控制器 ✅ (Line 5878)
- `async nodriver_tixcraft_home_close_window()` - 關閉彈窗 ✅ (Line 3004)
- `async nodriver_tixcraft_redirect()` - 頁面重定向 ✅ (Line 3031)
- `async nodriver_tixcraft_date_auto_select()` - 自動選擇日期 ✅ (Line 4564)
- `async nodriver_get_tixcraft_target_area()` - 取得目標區域 ✅ (Line 4992)
- `async nodriver_tixcraft_area_auto_select()` - 自動選擇區域 ✅ (Line 4871)
- `async nodriver_tixcraft_verify()` - 驗證處理 ✅ (Line 4396)
- `async nodriver_fill_verify_form()` - 填寫驗證表單 ✅ (Line 4400)
- `async nodriver_tixcraft_input_check_code()` - 輸入驗證碼 ✅ (Line 4531)
- `async nodriver_tixcraft_toast()` - 顯示提示訊息 ✅ (Line 5652)
- `async nodriver_tixcraft_keyin_captcha_code()` - 手動輸入驗證碼 ✅ (Line 5520)
- `async nodriver_tixcraft_reload_captcha()` - 重新載入驗證碼 ✅ (Line 5666)
- `async nodriver_tixcraft_get_ocr_answer()` - OCR 識別 ✅ (Line 5684)
- `async nodriver_tixcraft_auto_ocr()` - 自動 OCR ✅ (Line 5738)
- `async nodriver_tixcraft_ticket_main_agree()` - 勾選同意條款 ✅ (Line 5443)
- `async nodriver_tixcraft_assign_ticket_number()` - 設定票券數量 ✅ (Line 5189)
- `async nodriver_tixcraft_ticket_main()` - 票券頁面主處理 ✅ (Line 5459)
- `async nodriver_tixcraft_ticket_main_ocr()` - 票券頁面 OCR ✅ (Line 5800)
- `async nodriver_ticket_number_select_fill()` - 填入票券數量 ✅ (Line 5113)

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
- `async nodriver_kktix_order_member_code()` - 會員代碼 ✅
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
  - 實作位置：`nodriver_kktix_reg_captcha()` (Line 1411)
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

### ZenDriver 版本 (8個函式)
- `nodriver_ticket_login()` - 登入 (Line 17543)
- `nodriver_ticket_seat_type_auto_select()` - 自動選擇票別 (Line 18866)
- `nodriver_ticket_seat_auto_select()` - 自動選擇座位 (Line 19891)
- `nodriver_ticket_seat_main()` - 座位選擇主流程 (Line 19938)
- `nodriver_ticket_check_seat_taken_dialog()` - 座位佔用對話框 (Line 20168)
- `nodriver_ticket_close_dialog_with_retry()` - 重試關閉對話框 (Line 20218)
- `nodriver_ticket_allow_not_adjacent_seat()` - 允許非相鄰座位 (Line 20263)
- `nodriver_ticket_switch_to_auto_seat()` - 切換到自動選座 (Line 20303)

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

### ZenDriver 版本 (17個函式) - ✅ **完整實作**
- `nodriver_kham_main()` - 主控制器 (Line 16011)
- `nodriver_kham_login()` - 登入 (Line 14685)
- `nodriver_kham_go_buy_redirect()` - 購買重定向 (Line 14821)
- `nodriver_kham_check_realname_dialog()` - 實名對話框 (Line 14876)
- `nodriver_kham_allow_not_adjacent_seat()` - 非相鄰座位 (Line 14938)
- `nodriver_kham_switch_to_auto_seat()` - 切換自動選座 (Line 14955)
- `nodriver_kham_check_captcha_text_error()` - 驗證碼錯誤檢查 (Line 14992)
- `nodriver_kham_product()` - 產品頁 (Line 15025)
- `nodriver_kham_date_auto_select()` - 日期選擇 (Line 15045)
- `nodriver_kham_keyin_captcha_code()` - 驗證碼輸入 (Line 15309)
- `nodriver_kham_area_auto_select()` - 區域選擇 (Line 15421)
- `nodriver_kham_auto_ocr()` - 自動 OCR (Line 15816)
- `nodriver_kham_captcha()` - 驗證碼處理 (Line 15890)
- `nodriver_kham_performance()` - 演出處理 (Line 15934)
- `nodriver_kham_seat_type_auto_select()` - 票種選擇 (Line 17616)
- `nodriver_kham_seat_auto_select()` - 座位選擇 (Line 17941)
- `nodriver_kham_seat_main()` - 座位選擇主流程 (Line 18305)

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

### ZenDriver 版本 (25個函式)
- `async nodriver_ibon_login()` - Cookie 登入處理 ✅ (Line 8094)
- `async nodriver_ibon_date_auto_select_pierce()` - 日期選擇 Shadow DOM 穿透 ✅ (Line 9085)
- `async nodriver_ibon_date_auto_select()` - 日期自動選擇 ✅ (Line 9393)
- `async nodriver_ibon_date_auto_select_domsnapshot()` - DOMSnapshot 快照 ✅ (Line 9415)
- `async nodriver_ibon_ticket_agree()` - 同意條款 ✅ (Line 9739)
- `async nodriver_ibon_allow_not_adjacent_seat()` - 非連續座位 ✅ (Line 9745)
- `async nodriver_ibon_event_area_auto_select()` - Angular SPA Event 區域選擇 ✅ (Line 9774)
- `async nodriver_ibon_area_auto_select()` - 座位區域自動選擇 ✅ (Line 10217)
- `async nodriver_ibon_ticket_number_auto_select()` - 票數自動設定 ✅ (Line 10791)
- `async nodriver_ibon_get_captcha_image_from_shadow_dom()` - Shadow DOM 截圖 ✅ (Line 11108)
- `async nodriver_ibon_keyin_captcha_code()` - 驗證碼輸入 ✅ (Line 11289)
- `async nodriver_ibon_refresh_captcha()` - 刷新驗證碼 ✅ (Line 11524)
- `async nodriver_ibon_auto_ocr()` - OCR 自動識別 ✅ (Line 11555)
- `async nodriver_ibon_captcha()` - 驗證碼主控制 ✅ (Line 11714)
- `async nodriver_ibon_purchase_button_press()` - 購票按鈕 ✅ (Line 11803)
- `async nodriver_ibon_check_sold_out()` - 售罄檢查 ✅ (Line 11858)
- `async nodriver_ibon_wait_for_select_elements()` - 等待選擇元素 ✅ (Line 11894)
- `async nodriver_ibon_check_sold_out_on_ticket_page()` - 票券頁售罄檢查 ✅ (Line 11937)
- `async nodriver_ibon_navigate_on_sold_out()` - 售罄導航 ✅ (Line 12060)
- `async nodriver_ibon_fill_verify_form()` - 驗證表單填寫 ✅ (Line 12122)
- `async nodriver_ibon_verification_question()` - 驗證問題 ✅ (Line 12299)
- `async nodriver_tour_ibon_event_detail()` - iBon Tour 活動詳情 ✅ (Line 12442)
- `async nodriver_tour_ibon_options()` - iBon Tour 選項 ✅ (Line 12493)
- `async nodriver_tour_ibon_checkout()` - iBon Tour 結帳 ✅ (Line 12629)
- `async nodriver_ibon_main()` - 主控制器 ✅ (Line 12763)

### iBon 差異分析
🥇 **實際狀態：25/15** (完整度: 95% - 金級)

**✅ 已完整實作（25 個函式，核心搶票流程 100% 完成）：**
- **登入功能** (Line 8094)：Cookie 處理、頁面重新載入和登入狀態驗證
- **日期選擇** (Line 9085-9415)：使用 DOMSnapshot 平坦化策略穿透 closed Shadow DOM
- **座位區域選擇** (Line 9774-10217)：支援 Angular SPA Event 頁面 + .aspx 頁面
- **驗證碼處理** (Line 11108-11714)：Shadow DOM 截圖、OCR、輸入、重試
- **售罄處理** (Line 11858-12060)：售罄檢查、票券頁售罄、售罄導航
- **iBon Tour 模組** (Line 12442-12629)：活動詳情、選項、結帳
- **同意條款** (Line 9739)：簡單但完整的勾選實作

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

### ZenDriver 版本 (17個函式)
- `async nodriver_cityline_main()` - 主控制器 ✅ (Line 14537)
- `async nodriver_cityline_auto_retry_access()` - 自動重試存取 ✅ (Line 13737)
- `async nodriver_cityline_login()` - 登入 ✅ (Line 13751)
- `async nodriver_cityline_date_auto_select()` - 自動選擇日期 ✅ (Line 13810)
- `async nodriver_cityline_check_login_modal()` - 登入模態框檢查 ✅ (Line 13911)
- `async nodriver_cityline_continue_button_press()` - 繼續按鈕 ✅ (Line 14000)
- `async nodriver_cityline_area_auto_select()` - 自動選擇區域 ✅ (Line 14056)
- `async nodriver_cityline_ticket_number_auto_select()` - 自動選擇票數 ✅ (Line 14172)
- `async nodriver_cityline_next_button_press()` - 下一步按鈕 ✅ (Line 14214)
- `async nodriver_cityline_performance()` - 演出處理 ✅ (Line 14250)
- `async nodriver_cityline_check_shopping_basket()` - 購物籃檢查 ✅ (Line 14283)
- `async nodriver_check_modal_dialog_popup()` - 模態對話框 ✅ (Line 14317)
- `async nodriver_cityline_purchase_button_press()` - 購買按鈕 ✅ (Line 14328)
- `async nodriver_cityline_close_second_tab()` - 關閉第二個標籤 ✅ (Line 14354)
- `async nodriver_cityline_cookie_accept()` - 接受 Cookie ✅ (Line 14372)
- `async nodriver_cityline_press_buy_button()` - 購買按鈕 ✅ (Line 14404)
- `async nodriver_cityline_clean_ads()` - 清除廣告 ✅ (Line 14484)

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

### ZenDriver 版本 (30個函式) - v2025.11.28 新增
- `nodriver_hkticketing_main()` - 主控制器（行 23131）
- `nodriver_hkticketing_login()` - 登入（行 20778）
- `nodriver_hkticketing_accept_cookie()` - 接受 Cookie（行 20919）
- `nodriver_hkticketing_date_buy_button_press()` - 按下日期購買按鈕（行 20931）
- `nodriver_hkticketing_date_assign()` - 指定日期（行 21004）
- `nodriver_hkticketing_date_password_input()` - 日期密碼輸入（行 21183）
- `nodriver_hkticketing_date_auto_select()` - 自動選擇日期（行 21232）
- `nodriver_hkticketing_area_auto_select()` - 自動選擇區域（行 21273）
- `nodriver_hkticketing_ticket_number_auto_select()` - 自動選擇票數（行 21510）
- `nodriver_hkticketing_ticket_delivery_option()` - 票券配送選項（行 21558）
- `nodriver_hkticketing_next_button_press()` - 按下下一步按鈕（行 21598）
- `nodriver_hkticketing_go_to_payment()` - 前往付款（行 21662）
- `nodriver_hkticketing_hide_tickets_blocks()` - 隱藏票券區塊（行 21709）
- `nodriver_hkticketing_type02_clear_session()` - Type02 清除 Session（行 21735）
- `nodriver_hkticketing_type02_check_traffic_overload()` - Type02 流量超載檢查（行 21792）
- `nodriver_hkticketing_type02_login()` - Type02 登入（行 21851）
- `nodriver_hkticketing_type02_dismiss_modal()` - Type02 關閉模態框（行 22003）
- `nodriver_hkticketing_type02_event_page_buy_button()` - Type02 活動頁購買按鈕（行 22053）
- `nodriver_hkticketing_type02_event_page()` - Type02 活動頁（行 22114）
- `nodriver_hkticketing_type02_date_assign()` - Type02 日期指定（行 22144）
- `nodriver_hkticketing_type02_area_auto_select()` - Type02 區域選擇（行 22324）
- `nodriver_hkticketing_type02_ticket_number_select()` - Type02 票數選擇（行 22463）
- `nodriver_hkticketing_type02_next_button_press()` - Type02 下一步按鈕（行 22558）
- `nodriver_hkticketing_type02_performance()` - Type02 演出處理（行 22594）
- `nodriver_hkticketing_type02_confirm_order()` - Type02 確認訂單（行 22644）
- `nodriver_hkticketing_performance()` - 演出處理（行 22921）
- `nodriver_hkticketing_escape_robot_detection()` - 避開機器人偵測（行 22955）
- `nodriver_hkticketing_url_redirect()` - URL 重定向（行 22972）
- `nodriver_hkticketing_content_refresh()` - 內容重新整理（行 23032）
- `nodriver_hkticketing_travel_iframe()` - 遍歷 iframe（行 23080）

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

### ZenDriver 版本 (8個函式) ✅ **2025-11-18 完成**
- `async nodriver_ticketmaster_promo()` - 促銷代碼 ✅ (Line 4392)
- `async nodriver_ticketmaster_parse_zone_info()` - 解析區域資訊 ✅ (Line 3254)
- `get_ticketmaster_target_area()` - 取得目標區域 ✅ (Line 3404)
- `async nodriver_ticketmaster_get_ticketPriceList()` - 取得票價清單 ✅ (Line 3572)
- `async nodriver_ticketmaster_date_auto_select()` - 自動選擇日期 ✅ (Line 3668)
- `async nodriver_ticketmaster_area_auto_select()` - 自動選擇區域 ✅ (Line 3888)
- `async nodriver_ticketmaster_assign_ticket_number()` - 設定票券數量 ✅ (Line 3987)
- `async nodriver_ticketmaster_captcha()` - 驗證碼處理 ✅ (Line 4121)

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

| 平台 | 函式數量 | 行數範圍 | 可信度 | 建議 |
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
2. **跳轉代碼**：使用行號快速跳轉到具體實作
3. **版本對比**：比較 ZenDriver 與 Chrome 版本差異
4. **缺失識別**：快速識別未實作功能位置
5. **開發優先度**：優先開發和維護 ZenDriver 版本功能

此文件可作為開發和除錯時的快速參考工具。

---

*此文件最後更新：2026-03-05（行號引用全面更新）*
*分析基於：nodriver_tixcraft.py (19,049 行) + platforms/*.py*
*整合內容：標準功能架構定義 + 平台函數索引 + 功能完整度評分 + 結構差異分析*
*相關文件：[標準功能定義](./ticket_automation_standard.md) | [開發規範](./development_guide.md) | [程式碼範本](./coding_templates.md)*

**🎯 重大更新（2026.03.05）：函數行號引用全面更新**
- **檔案規模**：nodriver_tixcraft.py 從 26,357 行縮減至 19,049 行（6 個平台已拆分至 platforms/）
- **新增平台**：FunOne Tickets (18 函式)、Fansigo (9 函式)
- **新增模組**：HKTicketing Type02 (12 函式)、iBon Tour (3 函式)、UDN 座位選擇 (3 函式)
- **已移除函式**：`nodriver_ticketplus_order_expansion_auto_select`、`nodriver_ticketplus_assign_ticket_number`、`nodriver_ticketplus_order_auto_reload_coming_soon`
- **行號更新**：所有平台函數行號引用已更新至最新版本，確保文件與代碼同步
