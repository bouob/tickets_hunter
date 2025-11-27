# NoDriver vs Chrome 函式結構分析與平台索引

**文件說明**：提供 Tickets Hunter 專案的模組結構、核心函數索引、平台實作分析與功能完整度評分
**最後更新**：2025-11-12

---

此文件整合了以下內容（以 NoDriver 為主要開發目標）：
1. **標準功能架構** - 完整的搶票程式應包含的功能模組定義
2. **平台函數索引** - 快速定位各平台函數行號位置
3. **結構差異分析** - NoDriver 與 Chrome 版本的函式實作差異
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
3. **頁面監控與重載** - 自動重載、彈窗處理
4. **日期選擇** - 關鍵字匹配 + 條件式遞補 (v1.2+)
5. **區域/座位選擇** - 關鍵字匹配 + 條件式遞補 + 排除過濾 (v1.2+)
6. **票數設定** - 自動設定購票張數
7. **驗證碼處理** - OCR 自動辨識 + 手動輸入回退
8. **表單填寫** - 自動填寫購票資訊
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
- **Chrome Driver 版本**：`{platform}_{function_name}()` - 例如 `tixcraft_date_auto_select()`
- **通用工具**：直接使用功能名稱 - 例如 `find_element_safe()`

---

## 🎯 快速索引

### 主要檔案
- **nodriver_tixcraft.py** - NoDriver 版本（推薦） (21,200 行, 177 個函式)
- **chrome_tixcraft.py** - Chrome/Undetected/Selenium 版本 (11,764 行, 197 個函式)

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
> **重要說明**：依照 NoDriver First 開發策略，以下所有平台章節皆以 **NoDriver 版本優先列出**，Chrome Driver 版本作為參考對照。建議優先查閱和開發 NoDriver 版本功能。

### 🎫 **TixCraft 拓元**

#### NoDriver
```
拓元主流程
├── nodriver_tixcraft_main               # 行 5968
├── nodriver_tixcraft_date_auto_select   # 行 4530
├── nodriver_tixcraft_area_auto_select   # 行 4891
├── nodriver_get_tixcraft_target_area    # 行 4943
├── nodriver_tixcraft_assign_ticket_number # 行 5268 ✅ (v1.3+ 支援 Indievox 票種關鍵字匹配)
├── nodriver_tixcraft_ticket_main        # 行 5547
├── nodriver_tixcraft_ticket_main_agree  # 行 5529
├── nodriver_tixcraft_verify             # 行 4489
├── nodriver_tixcraft_ticket_main_ocr    # 行 5889
└── nodriver_tixcraft_keyin_captcha_code # 行 5597
```

#### Chrome/Undetected
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
└── tixcraft_ticket_main_ocr             # 行 2363
```

#### NoDriver (舊版本參考 - 已過期)
```
拓元主流程
├── nodriver_tixcraft_main               # 行 5968 (更新)
├── nodriver_tixcraft_date_auto_select   # 行 4530 (更新)
├── nodriver_tixcraft_area_auto_select   # 行 4891 (更新)
├── nodriver_get_tixcraft_target_area    # 行 4943 (更新)
├── nodriver_tixcraft_assign_ticket_number # 行 5268 (更新)
├── nodriver_tixcraft_ticket_main        # 行 5547 (更新)
├── nodriver_tixcraft_ticket_main_agree  # 行 5529 (更新)
├── nodriver_tixcraft_verify             # 行 4489 (更新)
├── nodriver_tixcraft_ticket_main_ocr    # 行 5889 (更新)
└── nodriver_tixcraft_keyin_captcha_code # 行 5597 (更新)
```

### 🎪 **KKTIX**

#### NoDriver
```
KKTIX 主流程
├── nodriver_kktix_main                  # 行 2645
├── nodriver_kktix_paused_main           # 行 1687
├── nodriver_kktix_signin                # 行 498
├── nodriver_kktix_reg_new_main          # 行 2191
├── nodriver_kktix_travel_price_list     # 行 774
├── nodriver_kktix_assign_ticket_number  # 行 1051
├── nodriver_kktix_reg_captcha           # 行 1204
├── nodriver_kktix_press_next_button     # 行 1461
├── nodriver_kktix_confirm_order_button  # 行 2396
├── nodriver_kktix_double_check_all_text_value # 行 2431
├── nodriver_kktix_check_register_status # 行 2476
├── nodriver_kktix_reg_auto_reload       # 行 2576
└── nodriver_facebook_login              # 行 342
```

#### Chrome/Undetected
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

#### Chrome/Undetected
```
TicketMaster 功能 (整合在 tixcraft_main)
├── ticketmaster_date_auto_select        # 行 1204
├── ticketmaster_area_auto_select        # 行 1600
├── get_ticketmaster_target_area         # 行 1446
├── ticketmaster_assign_ticket_number    # 行 5845
├── ticketmaster_captcha                 # 行 5914
└── ticketmaster_promo                   # 行 1872
```

#### NoDriver
```
TicketMaster 功能 (整合在 nodriver_tixcraft_main)
├── nodriver_ticketmaster_promo                    # 行 2961
├── nodriver_ticketmaster_parse_zone_info          # 行 3030
├── get_ticketmaster_target_area                   # 行 3196
├── nodriver_ticketmaster_get_ticketPriceList      # 行 3335
├── nodriver_ticketmaster_date_auto_select         # 行 3685
├── nodriver_ticketmaster_area_auto_select         # 行 3927
├── nodriver_ticketmaster_assign_ticket_number     # 行 4058
└── nodriver_ticketmaster_captcha                  # 行 4206
```

### 🏙️ **Cityline**

#### Chrome/Undetected
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

#### NoDriver
```
Cityline 主流程
├── nodriver_cityline_main               # 行 15802
├── nodriver_cityline_login              # 行 14894
├── nodriver_cityline_date_auto_select   # 行 15055
├── nodriver_cityline_area_auto_select   # 行 15312
├── nodriver_cityline_ticket_number_auto_select # 行 15434
├── nodriver_cityline_purchase_button_press # 行 15667
└── nodriver_cityline_auto_retry_access  # 行 14841
```

### 💳 **iBon**

#### NoDriver （🥇 金級實作 - 95% 完整度）
```
iBon 主流程
├── nodriver_ibon_login                      # 行 9061 ✅ (Cookie 登入)
├── nodriver_ibon_date_auto_select           # 行 10613 ✅ (v1.3+ 性能優化：80% 效能提升)
│   ├── nodriver_ibon_date_auto_select_pierce # 行 10222 (Shadow DOM 穿透)
│   └── nodriver_ibon_date_auto_select_domsnapshot # 行 10637 (DOMSnapshot 快照)
├── nodriver_ibon_event_area_auto_select     # 行 11716 ✅ (Angular SPA Event 頁面)
├── nodriver_ibon_area_auto_select           # 行 12221 ✅ (舊版 .aspx 頁面)
├── nodriver_ibon_ticket_number_auto_select  # 行 12801 ✅ (票數自動設定)
├── nodriver_ibon_get_captcha_image_from_shadow_dom # 行 12958 ✅ (Shadow DOM 截圖)
├── nodriver_ibon_keyin_captcha_code         # 行 13162 ✅ (驗證碼輸入)
├── nodriver_ibon_refresh_captcha            # 行 13409 ✅ (刷新驗證碼)
├── nodriver_ibon_auto_ocr                   # 行 13443 ✅ (OCR 自動識別)
├── nodriver_ibon_captcha                    # 行 13615 ✅ (驗證碼主控制)
├── nodriver_ibon_purchase_button_press      # 行 13712 ✅ (購票按鈕)
├── nodriver_ibon_check_sold_out             # 行 13769 ✅ (售罄檢查)
├── nodriver_ibon_verification_question      # 行 13919 ✅ (驗證問題)
├── nodriver_ibon_ticket_agree               # 行 11679 ✅ (同意條款)
├── nodriver_ibon_allow_not_adjacent_seat    # 行 11685 ✅ (非連續座位)
└── nodriver_ibon_main                       # 行 13973 ✅ (主流程完整)
```

#### Chrome/Undetected
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

#### Chrome/Undetected
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

#### NoDriver
```
❌ 完全未實作                            # 行 4481 (註解)
```

### 🎪 **KHAM 寬宏售票**

#### Chrome/Undetected
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

#### NoDriver
```
KHAM 主流程
├── nodriver_kham_main                   # 行 19174 ✅
├── nodriver_kham_login                  # 行 15956 ✅
├── nodriver_kham_date_auto_select       # 行 16318 ✅
├── nodriver_kham_go_buy_redirect        # 行 16130 ✅
├── nodriver_kham_product                # 行 16189 ✅
├── nodriver_kham_area_auto_select       # 行 16713 ✅
├── nodriver_kham_switch_to_auto_seat    # 行 16890 ✅
├── nodriver_kham_performance            # 行 17259 ✅
├── nodriver_kham_keyin_captcha_code     # 行 16417 ✅
├── nodriver_kham_auto_ocr               # 行 16723 ✅
├── nodriver_kham_captcha                # 行 17215 ✅
├── nodriver_kham_check_captcha_text_error # 行 16246 ✅
├── nodriver_kham_check_realname_dialog  # 行 16165 ✅
└── nodriver_kham_allow_not_adjacent_seat # 行 16201 ✅
```

### 🎫 **HK Ticketing**

#### Chrome/Undetected
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

#### NoDriver
```
❌ 完全未實作
```

### ➕ **TicketPlus**

#### Chrome/Undetected
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

#### NoDriver
```
TicketPlus 主流程
├── nodriver_ticketplus_main                      # 行 8921 ✅
├── nodriver_ticketplus_detect_layout_style       # 行 6236 ✅ (額外功能)
├── nodriver_ticketplus_account_sign_in           # 行 6350 ✅
├── nodriver_ticketplus_is_signin                 # 行 6410 ✅ (額外功能)
├── nodriver_ticketplus_account_auto_fill         # 行 6426 ✅
├── nodriver_ticketplus_date_auto_select          # 行 6478 ✅
├── nodriver_ticketplus_unified_select            # 行 6807 ✅ (額外功能)
├── nodriver_ticketplus_click_next_button_unified # 行 7306 ✅ (額外功能)
├── nodriver_ticketplus_order_expansion_auto_select # 行 7446 ✅
├── nodriver_ticketplus_assign_ticket_number      # 行 8022 ✅
├── nodriver_ticketplus_ticket_agree              # 行 8200 ✅
├── nodriver_ticketplus_accept_realname_card      # 行 8265 ✅
├── nodriver_ticketplus_accept_other_activity     # 行 8278 ✅
├── nodriver_ticketplus_accept_order_fail         # 行 8291 ✅
├── nodriver_ticketplus_check_queue_status        # 行 8369 ✅ (額外功能)
├── nodriver_ticketplus_order_auto_reload_coming_soon # 行 8448 ✅
├── nodriver_ticketplus_confirm                   # 行 8559 ✅
├── nodriver_ticketplus_order                     # 行 8597 ✅
├── nodriver_ticketplus_check_next_button         # 行 8785 ✅ (額外功能)
└── nodriver_ticketplus_order_exclusive_code      # 行 8821 ✅ (v1.3+ 折扣碼自動填入)
```

### 🎪 **FamiTicket 全家** (🏅 白金級 - v2025.11.24 完整實作)

#### Chrome/Undetected
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

#### NoDriver (🏅 白金級 - 100% 完整)
```
FamiTicket 主流程
├── nodriver_famiticket_main                 # 行 10133 ✅ (主控制器 - URL 路由器)
├── nodriver_fami_login                      # 行 9181 ✅ (帳號密碼登入，HTTP-Only Cookie)
├── nodriver_fami_activity                   # 行 9296 ✅ (活動頁面「購買」按鈕)
├── nodriver_fami_verify                     # 行 9355 ✅ (驗證問題/實名認證)
├── nodriver_fami_date_auto_select           # 行 9463 ✅ (日期選擇+條件回退 date_auto_fallback)
├── nodriver_fami_area_auto_select           # 行 9659 ✅ (區域選擇+AND邏輯+條件回退)
├── nodriver_fami_date_to_area               # 行 9821 ✅ (日期/區域協調器)
├── nodriver_fami_ticket_select              # 行 9898 ✅ (票種選擇頁面)
└── nodriver_fami_home_auto_select           # 行 10026 ✅ (首頁入口分派)
```

**FamiTicket NoDriver 功能特點**：
- ✅ 完整 9 函數實作，涵蓋登入→活動→日期→區域→票種→結帳完整流程
- ✅ 日期選擇支援關鍵字匹配（OR 邏輯，逗號分隔）+ `date_auto_fallback` 條件回退
- ✅ 區域選擇支援 AND 邏輯（空格分隔）+ 多組關鍵字（分號分隔）
- ✅ 隨機延遲 0.4-1.2 秒模擬人類操作（反爬蟲）
- ✅ 使用 NoDriver 官方 API（`query_selector_all`、`wait_for`）

### 🌐 **其他平台**

#### Chrome/Undetected
```
其他平台
├── ticket_login (Ticket.com.tw)         # 行 5501
├── udn_login (UDN)                      # 行 5562
├── facebook_login                       # 行 5296
├── facebook_main                        # 行 11328
└── softix_powerweb_main                 # 行 8239
```

#### NoDriver
```
其他平台
├── nodriver_facebook_login              # 行 342
└── nodriver_facebook_main               # 行 4481
```

### 🔧 **共用工具函數**

#### Chrome/Undetected
```
OCR 相關
├── ddddocr_image_to_text                # 行 676
├── get_ocr_answer                       # 行 773
├── force_check_checkbox                 # 行 711
└── force_press_button                   # 行 746

輔助工具
├── play_mp3_async                       # 行 628
├── get_favoriate_extension_path         # 行 649
├── get_chrome_options                   # 行 416
└── Driver                               # 行 11364
```

#### NoDriver
```
OCR 相關
├── nodriver_ddddocr_image_to_text       # 行 64
├── nodriver_tixcraft_get_ocr_answer     # 行 5713
└── nodriver_force_check_checkbox        # 行 305

輔助工具
├── play_mp3_async (在 util.py)        # 行 236
├── nodriver_press_button                # 行 202
├── nodriver_check_checkbox              # 行 218
├── nodriver_check_checkbox_enhanced     # 行 305
├── nodriver_facebook_login              # 行 342
├── detect_cloudflare_challenge          # 行 365
└── handle_cloudflare_challenge          # 行 408
```

### 🛑 **暫停機制輔助函數** (NoDriver 專用)

> **位置**: `src/nodriver_tixcraft.py:8304-8370`

#### 核心暫停檢查函數

```
check_and_handle_pause(config_dict)      # 行 8304 ✅
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
sleep_with_pause_check(tab, seconds, config_dict)              # 行 8321 ✅
├── 取代 tab.sleep()
├── 等待期間檢查暫停狀態
└── 返回 True (暫停中) / False (正常)

asyncio_sleep_with_pause_check(seconds, config_dict)           # 行 8328 ✅
├── 取代 asyncio.sleep()
├── 不需要 tab 物件的純延遲
└── 返回 True (暫停中) / False (正常)

evaluate_with_pause_check(tab, javascript_code, config_dict)   # 行 8336 ✅
├── JavaScript 執行前檢查暫停
├── 暫停時返回 None
└── 正常時返回 JavaScript 執行結果

with_pause_check(task_func, config_dict, *args, **kwargs)      # 行 8348 ✅
├── 包裝長時間任務
├── 支援中途暫停（每 50ms 檢查一次）
└── 暫停時取消任務並返回 None
```

#### 使用規範

1. **統一入口**：所有暫停檢查必須使用 `check_and_handle_pause(config_dict)`
2. **輔助函數優先**：使用專用包裝函數取代原生 sleep/evaluate
3. **僅 NoDriver 支援**：Chrome Driver 版本不支援暫停機制
4. **訊息控制**：由 verbose 設定統一控制顯示

#### 相關文件

- [暫停機制範本](./coding_templates.md#暫停機制標準範本) - 完整實作範例
- [暫停機制開發規範](./development_guide.md#暫停機制開發規範) - 開發原則與檢查清單

---

### 📊 **平台實作狀態一覽**

| 平台 | Chrome 行數範圍 | NoDriver 行數範圍 | 完整度 |
|------|:---------------:|:-----------------:|:------:|
| TixCraft | 967-5952 | 1103-1889 | ✅/✅ |
| KKTIX | 2419-6117 | 302-913 | ✅/✅ |
| TicketPlus | 9862-11238 | 3106-5782 | ✅/✅ |
| KHAM 寬宏 | 5492-9644 | 12064-13080 | ✅/✅ |
| TicketMaster | 1204-5914 | 1099-1931 | ✅/⚠️ |
| Cityline | 4343-6777 | 3829-4005 | ✅/⚠️ |
| iBon | 4636-7132 | 5806-11530 | ✅/🥇 |
| Urbtix | 3806-6589 | 未實作 | ✅/❌ |
| HK Ticketing | 5596-7953 | 未實作 | ✅/❌ |
| FamiTicket | 3321-6250 | 未實作 | ✅/❌ |

---

## 總體統計

| 平台 | Chrome版本函式數 | NoDriver版本函式數 | 實際實作度 | 狀態 |
|------|------------------|-------------------|------------|------|
| Tixcraft | 17 | 19 | 95% | ✅ **雙版本完整** |
| KKTIX | 17 | 13 | 95% | ✅ **雙版本完整** |
| TicketPlus | 25 | 19 | 95% | ✅ **雙版本完整** |
| KHAM 寬宏 | 14 | 14 | 98% | 🏅 **白金級** |
| 年代售票 | 7 | 7 | 100% | ✅ **雙版本完整** |
| iBon | 15 | 18 | 95% | 🥇 **金級實作** |
| FamiTicket | 10 | 9 | 100% | 🏅 **白金級** (v2025.11.24) |
| Cityline | 15 | 6 | 40% | ⚠️ 部分實作 |
| UrBtix | 11 | 0 | 0% | ❌ 未實作 |
| HKTicketing | 20 | 0 | 0% | ❌ 未實作 |
| Ticketmaster | 9 | 8 | 89% | 🥇 **金級實作** |

**總計：Chrome 197 個函式，NoDriver 177 個函式，實際可用度：約 80%**
**最新檔案大小：chrome_tixcraft.py (11,764 行)，nodriver_tixcraft.py (21,200 行)**

**🎯 重要更新：六大主流平台（TixCraft、KKTIX、TicketPlus、iBon、KHAM、FamiTicket）NoDriver 版本已完全可用**
**ℹ️ 備註：TicketPlus NoDriver 版本缺少 4 個 OCR 函式，但目前活動無 OCR 需求，暫不影響使用**

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

### NoDriver 版本功能完整度評分

| 平台 | 主流程 | 日期選擇 | 區域選擇 | 票數設定 | 驗證碼 | 條款 | 送出 | 登入 | 錯誤處理 | 彈窗 | 重載 | **總分** | 等級 |
|-----|:-----:|:-------:|:-------:|:-------:|:-----:|:---:|:---:|:---:|:-------:|:---:|:---:|:-------:|:---:|
| **TicketPlus** | 10 | 15 | 15 | 10 | 8 | 5 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 |
| **KHAM** | 10 | 15 | 15 | 10 | 10 | 3 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 |
| **FamiTicket** | 10 | 15 | 15 | 10 | 8 | 5 | 10 | 10 | 5 | 5 | 5 | **98** | 🏅 白金 (v2025.11.24) |
| **iBon** | 10 | 15 | 15 | 10 | 10 | 5 | 10 | 10 | 5 | 3 | 2 | **95** | 🏅 白金 |
| **KKTIX** | 10 | 8 | 12 | 10 | 8 | 4 | 10 | 10 | 4 | 4 | 4 | **84** | 🥇 金 |
| **TixCraft** | 10 | 12 | 12 | 8 | 8 | 4 | 8 | 8 | 4 | 4 | 4 | **82** | 🥇 金 |
| **Ticketmaster** | 10 | 12 | 10 | 8 | 8 | 4 | 8 | 8 | 4 | 3 | 5 | **80** | 🥇 金 |
| **Cityline** | 10 | 10 | 8 | 5 | 0 | 0 | 8 | 8 | 3 | 3 | 5 | **60** | 🥈 銀 |
| **Urbtix** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | ❌ 未實作 |
| **HKTicketing** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | ❌ 未實作 |
| **Facebook** | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 3 | 3 | 0 | **24** | ❌ 未完成 |

**NoDriver 版本平均分：56.3 分**（僅計算有實作的平台：**86.9 分**）

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

2. **NoDriver 版本**：發展不均，僅 3 個平台可用
   - 1 個白金級平台：TicketPlus (98 分)
   - 2 個金級平台：TixCraft (82 分)、KKTIX (84 分)
   - 其餘平台未完成或未實作

3. **實作差距**：
   - Chrome 與 NoDriver 版本平均相差 61.3 分
   - NoDriver 版本僅實作 11 個平台中的 4 個
   - 主要差距在驗證碼處理、表單填寫、彈窗處理

### 平台實作對照表

根據標準功能架構，以下是各平台實作狀況對照：

#### ✅ 完全實作（Chrome + NoDriver 雙版本可用）
- **TicketPlus**：Chrome 100 分，NoDriver 98 分
- **KKTIX**：Chrome 95 分，NoDriver 84 分
- **TixCraft**：Chrome 100 分，NoDriver 82 分

#### ⚠️ 部分實作（NoDriver 版本待補強）
- **Cityline**：Chrome 93 分，NoDriver 60 分（銀級）
- **Urbtix**：Chrome 91 分，NoDriver 未實作
- **HKTicketing**：Chrome 95 分，NoDriver 未實作

#### 🥇 金級實作（核心功能可用）
- **Ticketmaster**：Chrome 81 分，NoDriver 80 分（金級）

#### 📋 建議開發優先度

**Phase 1（緊急）**：
1. **修復 NoDriver TixCraft**（82→95 分）
   - 補完驗證碼處理功能
   - 加強錯誤處理機制

2. **修復 NoDriver iBon**（9→80 分）
   - 幾乎完全重寫，參考 Chrome 版本

**Phase 2（重要）**：
3. **實作 NoDriver KHAM**（0→90 分）
   - Chrome 版本已滿分，直接移植

4. **實作 NoDriver Urbtix**（0→85 分）
   - 香港重要平台

**Phase 3（次要）**：
5. **補強 NoDriver Cityline**（60→85 分）
6. **實作 NoDriver HKTicketing**（0→85 分）
7. **實作 NoDriver FamiTicket**（0→85 分）

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

### NoDriver 版本 (18個函式)
- `async nodriver_tixcraft_main()` - 主控制器 ✅ (Line 5968)
- `async nodriver_tixcraft_home_close_window()` - 關閉彈窗 ✅
- `async nodriver_tixcraft_redirect()` - 頁面重定向 ✅
- `async nodriver_tixcraft_date_auto_select()` - 自動選擇日期 ✅ (Line 4530)
- `async nodriver_get_tixcraft_target_area()` - 取得目標區域 ✅ (Line 4943)
- `async nodriver_tixcraft_area_auto_select()` - 自動選擇區域 ✅ (Line 4891)
- `async nodriver_tixcraft_verify()` - 驗證處理 ✅ (Line 4489)
- `async nodriver_tixcraft_input_check_code()` - 輸入驗證碼 ✅
- `async nodriver_tixcraft_toast()` - 顯示提示訊息 ✅
- `async nodriver_tixcraft_keyin_captcha_code()` - 手動輸入驗證碼 ✅ (Line 5597)
- `async nodriver_tixcraft_reload_captcha()` - 重新載入驗證碼 ✅
- `async nodriver_tixcraft_get_ocr_answer()` - OCR 識別 ✅ (Line 5713)
- `async nodriver_tixcraft_auto_ocr()` - 自動 OCR ✅ (Line 5818)
- `async nodriver_tixcraft_ticket_main_agree()` - 勾選同意條款 ✅ (Line 5529)
- `async nodriver_tixcraft_assign_ticket_number()` - 設定票券數量 ✅ (Line 5268)
- `async nodriver_tixcraft_ticket_main()` - 票券頁面主處理 ✅ (Line 5547)
- `async nodriver_tixcraft_ticket_main_ocr()` - 票券頁面 OCR ✅ (Line 5889)
- `async nodriver_ticket_number_select_fill()` - 填入票券數量 ✅

### Tixcraft 差異分析
✅ **已實作：18/17** (函式數量完整，品質優良)
✅ **核心功能完整：** 所有關鍵函式已實作並可用
➕ **額外功能：** NoDriver 版本新增了 `ticket_main_ocr()` 分離 OCR 邏輯

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

### NoDriver 版本 (9個函式)
- `async nodriver_kktix_main()` - 主控制器 ✅ (Line 2645)
- `async nodriver_kktix_signin()` - 登入 ✅ (Line 498)
- `async nodriver_kktix_paused_main()` - 暫停主流程 ✅ (Line 1687)
- `async nodriver_kktix_travel_price_list()` - 遍歷票價清單 ✅ (Line 774)
- `async nodriver_kktix_assign_ticket_number()` - 設定票券數量 ✅ (Line 1051)
- `async nodriver_kktix_reg_captcha()` - 註冊驗證碼處理(含自動答題功能) ✅ (Line 1204) [Updated: 2025-11-03]
- `async nodriver_kktix_press_next_button()` - 按下下一步按鈕 ✅ (Line 1461)
- `async nodriver_kktix_reg_new_main()` - 新註冊主流程 ✅ (Line 2191)
- `async nodriver_facebook_login()` - Facebook 登入 ✅ (Line 342)

### KKTIX 差異分析
✅ **已實作：9/17** (完整度: 53%)
❌ **缺失功能：**
- `kktix_confirm_order_button()` - 確認訂單
- `kktix_events_press_next_button()` - 活動頁處理
- `kktix_check_agree_checkbox()` - 同意條款檢查
- `kktix_double_check_all_text_value()` - 雙重檢查
- `set_kktix_control_label_text()` - 控制標籤
- `kktix_check_register_status()` - 註冊狀態檢查
- `kktix_reg_auto_reload()` - 自動重載
- `get_tixcraft_ticket_select*()` - 票券選擇邏輯

**🎯 重大更新記錄：**
- **2025.11.03**: 新增 KKTIX 自動答題功能（Feature Branch: 004-kktix-auto-answer）
  - 功能：自動偵測 KKTIX 驗證問題、推測答案、模擬人類填寫
  - 實作位置：`nodriver_kktix_reg_captcha()` (Line 1204)
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

### NoDriver 版本 (7個函式) - ✅ **2025-10-09 完成**
- `nodriver_ticket_login()` - 登入 (Line 13626-13695)
- `nodriver_ticket_seat_type_auto_select()` - 自動選擇票別 (Line 13698-13781)
- `nodriver_ticket_find_best_seats()` - 尋找最佳座位 (Line 13784-13855)
- `nodriver_ticket_seat_auto_select()` - 自動選擇座位 (Line 13858-13918)
- `nodriver_ticket_seat_main()` - 座位選擇主流程 (Line 13921-13994)
- `nodriver_ticket_allow_not_adjacent_seat()` - 允許非相鄰座位 (Line 13997-14029)
- `nodriver_ticket_switch_to_auto_seat()` - 切換到自動選座 (Line 14032-14073)

### 年代售票實作狀態
✅ **已實作：7/7** (完整度: 100%)
✅ **完整雙版本支援** - Chrome 和 NoDriver 版本功能一致
- 完整的座位選擇邏輯
- 票別自動選擇
- 最佳座位算法
- 登入功能

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

### NoDriver 版本
❌ **完全缺失** - 寬宏售票在 NoDriver 版本中完全沒有實作

### 寬宏售票差異分析
✅ **已實作：0/14** (完整度: 0%)
❌ **需要移植的關鍵功能：**
- 完整的主控制流程
- OCR 驗證碼處理
- 實名制對話框處理
- 座位選擇邏輯

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

### NoDriver 版本 (18個函式)
- `async nodriver_ibon_login()` - Cookie 登入處理 ✅ (Line 9061, 97行, 完整實作)
- `async nodriver_ibon_date_auto_select()` - 日期自動選擇 ✅ (Line 10613, DOMSnapshot 快照)
- `async nodriver_ibon_date_auto_select_pierce()` - 日期選擇 Shadow DOM 穿透 ✅ (Line 10222)
- `async nodriver_ibon_event_area_auto_select()` - Angular SPA Event 頁面區域選擇 ✅ (Line 11716)
- `async nodriver_ibon_area_auto_select()` - 座位區域自動選擇 ✅ (Line 12221, DOMSnapshot 平坦化)
- `async nodriver_ibon_ticket_number_auto_select()` - 票數自動設定 ✅ (Line 12801)
- `async nodriver_ibon_get_captcha_image_from_shadow_dom()` - Shadow DOM 截圖 ✅ (Line 12958)
- `async nodriver_ibon_keyin_captcha_code()` - 驗證碼輸入 ✅ (Line 13162)
- `async nodriver_ibon_refresh_captcha()` - 刷新驗證碼 ✅ (Line 13409)
- `async nodriver_ibon_auto_ocr()` - OCR 自動識別 ✅ (Line 13443)
- `async nodriver_ibon_captcha()` - 驗證碼主控制 ✅ (Line 13615)
- `async nodriver_ibon_purchase_button_press()` - 購票按鈕 ✅ (Line 13712)
- `async nodriver_ibon_check_sold_out()` - 售罄檢查 ✅ (Line 13769)
- `async nodriver_ibon_verification_question()` - 驗證問題 ✅ (Line 13919)
- `async nodriver_ibon_ticket_agree()` - 同意條款 ✅ (Line 11679)
- `async nodriver_ibon_allow_not_adjacent_seat()` - 非連續座位 ✅ (Line 11685)
- `async nodriver_ibon_main()` - 主控制器 ✅ (Line 13973, 主流程完整)

### iBon 差異分析
🥇 **實際狀態：18/15** (完整度: 95% - 金級)

**✅ 已完整實作（18 個函式，核心搶票流程 100% 完成）：**
- **登入功能** (Line 5762-5858, 97行)：
  - Cookie 處理、頁面重新載入和登入狀態驗證
  - 完整的錯誤處理和除錯訊息
- **日期選擇** (Line 5860-6141, 282行)：
  - 使用 DOMSnapshot 平坦化策略穿透 closed Shadow DOM
  - 支援 AND/OR 邏輯、關鍵字匹配、模式選擇
  - 完整的重試機制和錯誤處理
  - 🎯 **重大更新** (2025.09.29 + 2025.09.30)
- **座位區域選擇** (Line 9083-10377, 1295行)：
  - 使用 DOMSnapshot 穿透 closed Shadow DOM
  - 支援關鍵字匹配（AND 邏輯）+ 模式選擇回退
  - 實作剩餘票數檢查邏輯
  - 🎯 **新增完成** (2025.09.30)
- **同意條款** (Line 9074-9078, 5行)：簡單但完整的勾選實作

**✅ 完整流程已接通：**
- 日期選擇 → 區域選擇 → 票數填寫 → 驗證碼識別 → 成功跳轉 → 結帳提醒 ✅
- 支援新舊兩種頁面格式（Event 頁面 + .aspx 頁面）
- 完整的 OCR 處理流程（截圖、識別、輸入、重試）
- 結帳頁面偵測與音效播放

**🎯 重大更新記錄：**
- **2025.09.29**: 完成日期選擇功能（Shadow DOM 平坦化策略）
- **2025.09.30**: 完成座位區域選擇功能（DOMSnapshot 平坦化策略）
- **2025.10.01**: 完成驗證碼處理（突破 closed Shadow DOM 截圖）+ 結帳提醒
- **2025.10.03**: 新增 Angular SPA Event 頁面支援 + 移除 emoji 修正 cp950 錯誤
- **實作完成度進度**: 0% → 35%（銅級）→ 50%（銀級）→ **95%（金級）** 🥇

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

### NoDriver 版本 (6個函式)
- `async nodriver_cityline_main()` - 主控制器 ✅ (Line 15802)
- `async nodriver_cityline_auto_retry_access()` - 自動重試存取 ✅ (Line 14841)
- `async nodriver_cityline_login()` - 登入 ✅ (Line 14894)
- `async nodriver_cityline_date_auto_select()` - 自動選擇日期 ✅ (Line 15055)
- `async nodriver_cityline_area_auto_select()` - 自動選擇區域 ✅ (Line 15312)
- `async nodriver_cityline_ticket_number_auto_select()` - 自動選擇票數 ✅ (Line 15434)
- `async nodriver_cityline_purchase_button_press()` - 按下購買按鈕 ✅ (Line 15667)
- `async nodriver_cityline_close_second_tab()` - 關閉第二個標籤 ✅

### Cityline 差異分析
✅ **已實作：8/15** (完整度: 53%)
✅ **已完成功能：**
- 主控制器、登入、日期選擇
- 區域自動選擇（新增）
- 票數自動設定（新增）
- 購買按鈕處理

❌ **缺失功能：**
- 演出處理邏輯
- Cookie 處理
- 廣告清除
- 驗證碼輸入

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

### NoDriver 版本
❌ **完全缺失** - UrBtix 在 NoDriver 版本中完全沒有實作

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

### NoDriver 版本
❌ **完全缺失** - HKTicketing 在 NoDriver 版本中完全沒有實作

### HKTicketing 差異分析
✅ **已實作：0/20** (完整度: 0%)
❌ **需要移植的關鍵功能：**
- 完整的購票流程
- 機器人偵測規避
- iframe 處理
- 密碼輸入邏輯

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
- `get_favoriate_extension_path()` - 取得偏好擴充功能路徑 (共用)

### NoDriver 版本 (20個函式)
- `async nodriver_ticketplus_main()` - 主控制器 ✅ (Line 8921)
- `async nodriver_ticketplus_detect_layout_style()` - 偵測版面樣式 ✅ (Line 6236)
- `async nodriver_ticketplus_account_sign_in()` - 帳號登入 ✅ (Line 6350)
- `async nodriver_ticketplus_is_signin()` - 檢查登入狀態 ✅ (Line 6410)
- `async nodriver_ticketplus_account_auto_fill()` - 帳號自動填入 ✅ (Line 6426)
- `async nodriver_ticketplus_date_auto_select()` - 自動選擇日期 ✅ (Line 6478)
- `async nodriver_ticketplus_unified_select()` - 統一選擇器 ✅ (Line 6807)
- `async nodriver_ticketplus_click_next_button_unified()` - 統一下一步點擊 ✅ (Line 7306)
- `async nodriver_ticketplus_order_expansion_auto_select()` - 訂單展開自動選擇 ✅ (Line 7446)
- `async nodriver_ticketplus_assign_ticket_number()` - 設定票券數量 ✅ (Line 8022)
- `async nodriver_ticketplus_ticket_agree()` - 同意條款 ✅ (Line 8200)
- `async nodriver_ticketplus_accept_realname_card()` - 接受實名卡 ✅ (Line 8265)
- `async nodriver_ticketplus_accept_other_activity()` - 接受其他活動 ✅ (Line 8278)
- `async nodriver_ticketplus_accept_order_fail()` - 接受訂單失敗 ✅ (Line 8291)
- `async nodriver_ticketplus_check_queue_status()` - 排隊狀態檢查 ✅ (Line 8369)
- `async nodriver_ticketplus_order_auto_reload_coming_soon()` - 即將開賣自動重載 ✅ (Line 8448)
- `async nodriver_ticketplus_confirm()` - 確認 ✅ (Line 8559)
- `async nodriver_ticketplus_order()` - 訂單處理 ✅ (Line 8597)
- `async nodriver_ticketplus_check_next_button()` - 檢查下一步按鈕 ✅ (Line 8785)
- `async nodriver_ticketplus_order_exclusive_code()` - 訂單專屬代碼 ✅ (Line 8821)

### TicketPlus 差異分析
✅ **已實作：19/25** (完整度: 95% - **實際測試完全可用**)
✅ **核心功能完整：**
- 登入系統、日期選擇、區域選擇完整
- 票券數量設定、同意條款處理完整
- 實名卡與其他活動處理完整
- 排隊狀態檢查與自動重載完整

➕ **NoDriver 額外功能：**
- `detect_layout_style()` - 版面樣式偵測
- `is_signin()` - 登入狀態檢查
- `unified_select()` - 統一選擇器
- `check_queue_status()` - 排隊狀態檢查
- 多個簡化版本的輔助函式

ℹ️ **暫時忽略 - OCR 驗證碼處理** (4 個函式，目前無需求):
- `nodriver_ticketplus_auto_ocr()` - 自動 OCR 識別 ⏸️
- `nodriver_ticketplus_order_ocr()` - 訂單 OCR 處理 ⏸️
- `nodriver_ticketplus_keyin_captcha_code()` - 手動輸入驗證碼 ⏸️
- `nodriver_ticketplus_check_and_renew_captcha()` - 驗證碼刷新 ⏸️

**說明：** 目前 TicketPlus 活動不使用 OCR 驗證碼機制，這 4 個函式缺失不影響實際搶票功能

**評估結果：** NoDriver 版本**可完全正常搶票使用**，實測通過

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

### NoDriver 版本 (9個函式) - ✅ **2025-11-24 完成**
- `nodriver_famiticket_main()` - 主控制器（URL 路由器）(Line 10133)
- `nodriver_fami_login()` - 帳號密碼登入（HTTP-Only Cookie）(Line 9181)
- `nodriver_fami_activity()` - 活動頁面處理 (Line 9296)
- `nodriver_fami_verify()` - 驗證問題/實名認證 (Line 9355)
- `nodriver_fami_date_auto_select()` - 日期選擇+條件回退 (Line 9463)
- `nodriver_fami_area_auto_select()` - 區域選擇+AND邏輯 (Line 9659)
- `nodriver_fami_date_to_area()` - 日期/區域協調器 (Line 9821)
- `nodriver_fami_ticket_select()` - 票種選擇頁面 (Line 9898)
- `nodriver_fami_home_auto_select()` - 首頁入口分派 (Line 10026)

### FamiTicket 差異分析
✅ **已實作：9/10** (完整度: 100% - 🏅 白金級)
✅ **核心功能完整：**
- 登入系統（帳號密碼 + HTTP-Only Cookie）
- 日期選擇（關鍵字匹配 + `date_auto_fallback` 條件回退）
- 區域選擇（AND 邏輯 + `area_auto_fallback` 條件回退）
- 驗證問題自動填寫
- 票種選擇與結帳流程

**🎯 重大更新記錄：**
- **2025-11-24**: 完成 FamiTicket NoDriver 完整實作
  - 9 個函數全面實作
  - 使用 NoDriver 官方 API（`query_selector_all`、`wait_for`）
  - 隨機延遲 0.4-1.2 秒模擬人類操作（反爬蟲）
  - 完整文檔記錄：`docs/08-troubleshooting/famiticket_nodriver_fixes.md`

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

### NoDriver 版本 (8個函式) ✅ **2025-11-18 完成**
- `async nodriver_ticketmaster_promo()` - 促銷代碼 ✅ (Line 2961)
- `async nodriver_ticketmaster_parse_zone_info()` - 解析區域資訊 ✅ (Line 3030)
- `get_ticketmaster_target_area()` - 取得目標區域 ✅ (Line 3196)
- `async nodriver_ticketmaster_get_ticketPriceList()` - 取得票價清單 ✅ (Line 3335)
- `async nodriver_ticketmaster_date_auto_select()` - 自動選擇日期 ✅ (Line 3685)
- `async nodriver_ticketmaster_area_auto_select()` - 自動選擇區域 ✅ (Line 3927)
- `async nodriver_ticketmaster_assign_ticket_number()` - 設定票券數量 ✅ (Line 4058)
- `async nodriver_ticketmaster_captcha()` - 驗證碼處理 ✅ (Line 4206)

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

### TODO 函式統計 (基於程式碼掃描)

NoDriver 版本中發現 **24+ 個 TODO 標記**，分布如下：

**Tixcraft 平台：**
- Lines 831, 890, 893, 954: 基礎功能未完成
- Line 1140: 驗證表單填寫待實作
- Lines 1932, 1952, 1963, 1968: 票券處理邏輯

**iBon 平台：**
- Lines 3639, 3666, 3690, 3719: 主控制器框架
- Lines 3723, 3731, 3737, 3747: 細節處理
- Lines 3762, 3769, 3775, 3780, 3785: 同意條款處理

**其他：**
- Line 3506: 通用功能
- Line 4053: 最後一個 TODO

### 實作可信度評估

| 平台 | 函式數量 | TODO 數量 | 行數範圍 | 可信度 | 建議 |
|------|----------|-----------|------------|--------|------|
| Tixcraft | 19 | ~5 | 2108-3024 | 高 | 實測通過，可直接使用 |
| KKTIX | 13 | ~2 | 338-2076 | 高 | 實測通過，可直接使用 |
| iBon | 18 | ~8 | 5837-11767 | 🥇 極高 | **金級實作，可直接使用** |
| Cityline | 6 | ~1 | 11768-11993 | 中等 | 部分功能可用，需補完 |
| TicketPlus | 19 | ~4 | 3152-5709 | 高 | 實測通過，可直接使用 |
| Ticketmaster | 8 | 1 | 3101-4300 | 高 | 實測通過，可直接使用 |

**總計 TODO 標記：18 個**（已從原本 24+ 個清理至 18 個）

---

## 重構建議與評估

### 1. 緊急修復優先度 🔥 **更新至 2025.10.09**
1. ✅ ~~**年代售票移植**~~ - **已完成 (2025-10-09)** - Chrome 已有 7 個完整函式
2. **寬宏售票移植** - 🔥 台灣重要平台，Chrome 已有 14 個完整函式（但 NoDriver 版本已完成 14/14）
3. **Cityline 補完** - 補完缺失的 9 個函式（40% → 85%）
4. ⏸️ **TicketPlus OCR** - 暫時忽略（目前無需求，Chrome 有 4 個函式可參考）

### 2. 高優先度移植平台
1. ✅ ~~**TicketMaster 補完**~~ - **已完成 (2025-11-18)** - 8/9 函式實作完成
2. **Urbtix 移植** - 香港重要平台，Chrome 已有 11 個完整函式
3. **HKTicketing 移植** - 香港平台，Chrome 已有 20 個完整函式

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

### 4. 實作優先度 🔥 **更新至 2025.10.09**

**Phase 1 (台灣重要平台移植 🔥)：**
- ✅ ~~**年代售票完整移植**~~ - **已完成 (2025-10-09)** (7/7 函式)
- ✅ ~~**寬宏售票完整移植**~~ - **已完成** (14/14 函式，NoDriver 版本 2025.10 前完成)
- 實際完成度：100% (Phase 1 全部完成)

**Phase 2 (部分實作平台補完)：**
- **Cityline 功能補完** (9 個函式) - 40% → 85%
- ✅ ~~**TicketMaster 功能補完**~~ - **已完成 (2025-11-18)** - 8/9 函式實作完成 (11% → 89%)

**Phase 3 (香港平台移植)：**
- **Urbtix 完整移植** (11 個函式)
- **HKTicketing 完整移植** (20 個函式)
- **FamiTicket 完整移植** (10 個函式)

**Phase 4 (程式碼品質改善)：**
- TODO 標記清理（18 個 → 0 個）
- 共用邏輯重構
- 錯誤處理統一
- 架構優化與測試覆蓋

**暫時忽略 (⏸️ 等待實際需求)：**
- **TicketPlus OCR 功能補完** (4 個函式)
  - 現況：目前 TicketPlus 活動不使用 OCR 驗證碼
  - 參考：Chrome Lines 10824-11025, TixCraft NoDriver OCR Lines 2821-2949
  - 預計完成度：95% → 98% (等需求出現後再補充)

---

---

## 🎯 **使用方式**

1. **定位功能**：根據平台名稱找到對應函數（NoDriver 版本優先）
2. **跳轉代碼**：使用行號快速跳轉到具體實作
3. **版本對比**：比較 NoDriver 與 Chrome 版本差異
4. **缺失識別**：快速識別未實作功能位置
5. **開發優先度**：優先開發和維護 NoDriver 版本功能

此文件可作為開發和除錯時的快速參考工具。

---

*此文件最後更新：2025-11-27（行號引用更新）*
*分析基於：nodriver_tixcraft.py (21,200 行, 177 functions) vs chrome_tixcraft.py (11,764 行, 197 functions)*
*整合內容：標準功能架構定義 + 平台函數索引 + 功能完整度評分 + 結構差異分析*
*相關文件：[標準功能定義](./ticket_automation_standard.md) | [開發規範](./development_guide.md) | [程式碼範本](./coding_templates.md)*

**🎯 重大更新（2025.11.27）：函數行號引用全面更新**
- **檔案規模**：NoDriver 版本已從 12,602 行擴展至 21,200 行，函式數從 88 個增加至 177 個
- **六大主流平台完整支援**：TixCraft、KKTIX、TicketPlus、iBon、KHAM、FamiTicket 的 NoDriver 版本已完全可用
- **NoDriver 優勢**：記憶體佔用小、難以偵測、更適合現代化搶票需求
- **行號更新**：所有平台函數行號引用已更新至最新版本，確保文件與代碼同步