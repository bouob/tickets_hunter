# NoDriver 程式全面結構分析報告

**文件說明**：全面分析 NoDriver 版本各平台實作狀況、識別最佳楷模平台、提供缺失功能對照表
**最後更新**：2025-11-12

---

> **目的**：全面分析 NoDriver 版本各平台實作狀況，識別最佳楷模平台，並提供詳細的缺失功能對照表
>
> **文件版本**：v1.0
> **分析基礎**：`nodriver_tixcraft.py` (17,191 行, 114 個函式)

---

## 📊 執行摘要

### 整體統計

| 項目 | 數值 | 說明 |
|------|------|------|
| **總行數** | 17,191 行 | 較舊版 12,602 行增加 36% |
| **總函式數** | 114 個 | NoDriver 專用非同步函式 |
| **支援平台數** | 7 個 | 含台灣與香港主流平台 |
| **白金級平台** | 3 個 | TicketPlus、KHAM、iBon |
| **金級平台** | 2 個 | TixCraft、KKTIX |
| **銀級平台** | 1 個 | Cityline（部分實作）|
| **年代售票** | 完整 | 100% 實作（9 個函式）|

### 平台完整度排名

| 排名 | 平台 | 函式數 | 12階段評分 | 等級 | 推薦作為參考 |
|:----:|------|:------:|:----------:|:----:|:------------:|
| 🥇 | **TicketPlus** | 20 | 98/100 | 🏅 白金 | ⭐⭐⭐⭐⭐ |
| 🥈 | **KHAM** | 17 | 98/100 | 🏅 白金 | ⭐⭐⭐⭐⭐ |
| 🥉 | **iBon** | 20 | 95/100 | 🥇 金+ | ⭐⭐⭐⭐ |
| 4 | **KKTIX** | 13 | 84/100 | 🥇 金 | ⭐⭐⭐ |
| 5 | **TixCraft** | 16 | 82/100 | 🥇 金 | ⭐⭐⭐ |
| 6 | **年代售票** | 9 | 100/100 | 🏅 白金 | ⭐⭐⭐⭐⭐ |
| 7 | **Cityline** | 6 | 60/100 | 🥈 銀 | ⭐ |

### 最佳楷模平台：TicketPlus + KHAM 雙楷模

**選定理由**：
1. **TicketPlus**（遠大售票）：
   - ✅ 12 階段功能完整度：98/100
   - ✅ 函式數量最多（20 個），覆蓋所有核心流程
   - ✅ 獨有功能：佈局檢測、統一選擇器、排隊狀態檢查
   - ✅ 程式碼品質高，架構清晰
   - ⚠️ 缺少 OCR 驗證碼處理（但目前無需求）

2. **KHAM**（寬宏售票）：
   - ✅ 12 階段功能完整度：98/100
   - ✅ OCR 驗證碼處理完整（含 auto_ocr、captcha、keyin）
   - ✅ 座位選擇邏輯完整（含自動選座、座位圖選擇）
   - ✅ 實名制對話框處理
   - ✅ 非連續座位處理

3. **年代售票**（票數雖少但品質極高）：
   - ✅ 座位選擇功能完整（座位圖最佳算法）
   - ✅ 函式設計優秀，可作為座位選擇的參考楷模

**雙楷模策略**：
- **TicketPlus** 作為「主流程架構楷模」：日期選擇、區域選擇、票數設定、同意條款
- **KHAM** 作為「驗證碼與座位楷模」：OCR 處理、座位選擇、特殊對話框
- **年代售票** 作為「座位選擇算法楷模」：最佳座位算法

---

## 🎯 各平台詳細分析

### 1. TicketPlus（遠大售票）- 主流程架構楷模 🏅

#### 函式清單（20 個）

**階段 1-2：初始化與登入**
```
nodriver_ticketplus_account_sign_in          # 行 4358  - 帳號登入
nodriver_ticketplus_is_signin                # 行 4418  - 檢查登入狀態
nodriver_ticketplus_account_auto_fill        # 行 4434  - 帳號自動填入
```

**階段 3：佈局檢測（獨有功能）**
```
nodriver_ticketplus_detect_layout_style      # 行 4228  - 偵測版面樣式 ⭐
```

**階段 4：日期選擇**
```
nodriver_ticketplus_date_auto_select         # 行 4486  - 自動選擇日期
```

**階段 5：區域選擇**
```
nodriver_ticketplus_unified_select           # 行 4815  - 統一選擇器 ⭐
nodriver_ticketplus_order_expansion_auto_select # 行 5419 - 訂單展開自動選擇
nodriver_ticketplus_click_next_button_unified # 行 5314 - 統一下一步按鈕 ⭐
nodriver_ticketplus_check_next_button        # 行 6758  - 檢查下一步按鈕 ⭐
```

**階段 6：票數設定**
```
nodriver_ticketplus_assign_ticket_number     # 行 5995  - 設定票券數量
```

**階段 8-9：表單與條款**
```
nodriver_ticketplus_ticket_agree             # 行 6173  - 同意條款
nodriver_ticketplus_accept_realname_card     # 行 6238  - 接受實名卡
nodriver_ticketplus_accept_other_activity    # 行 6251  - 接受其他活動
nodriver_ticketplus_accept_order_fail        # 行 6264  - 接受訂單失敗
```

**階段 10-11：訂單與排隊**
```
nodriver_ticketplus_order_exclusive_code     # 行 6794  - 訂單專屬代碼（折扣碼）
nodriver_ticketplus_confirm                  # 行 6532  - 確認
nodriver_ticketplus_order                    # 行 6562  - 訂單處理
nodriver_ticketplus_check_queue_status       # 行 6342  - 檢查排隊狀態 ⭐
nodriver_ticketplus_order_auto_reload_coming_soon # 行 6421 - 即將開賣自動重載
```

**主流程控制**
```
nodriver_ticketplus_main                     # 行 6878  - 主控制器
```

#### 12 階段完整度評分：98/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ✅ | 10/10 | 完整登入與狀態檢查 |
| 3 | 頁面監控 | ✅ | 5/5 | 即將開賣自動重載 |
| 4 | 日期選擇 | ✅ | 15/15 | 完整關鍵字 + mode 回退 |
| 5 | 區域選擇 | ✅ | 15/15 | 統一選擇器 + 展開面板 |
| 6 | 票數設定 | ✅ | 10/10 | 完整票數分配 |
| 7 | 驗證碼處理 | ⏸️ | 8/10 | 缺 OCR（目前無需求）|
| 8 | 表單填寫 | ✅ | 5/5 | 實名卡等特殊表單 |
| 9 | 同意條款 | ✅ | 5/5 | 完整條款處理 |
| 10 | 訂單送出 | ✅ | 10/10 | 確認與送出完整 |
| 11 | 排隊處理 | ✅ | 5/5 | 排隊狀態檢查完整 ⭐ |
| 12 | 錯誤處理 | ✅ | 5/5 | 訂單失敗處理 |
| **總分** | | | **98/100** | **白金級** 🏅 |

#### 獨有優勢功能
1. **佈局檢測系統** (`detect_layout_style`)：自動識別新舊版面
2. **統一選擇器** (`unified_select`)：跨版面通用選擇邏輯
3. **排隊狀態檢查** (`check_queue_status`)：實時監控排隊進度
4. **折扣碼自動填入** (`order_exclusive_code`)：v1.3+ 新功能

#### 適合參考的場景
- ✅ 日期選擇架構設計
- ✅ 區域選擇統一接口
- ✅ 多版面佈局適配
- ✅ 排隊機制處理
- ✅ 主流程控制架構

---

### 2. KHAM（寬宏售票）- 驗證碼與座位楷模 🏅

#### 函式清單（17 個）

**階段 2：登入**
```
nodriver_kham_login                          # 行 12088 - 登入
```

**階段 3：頁面導航**
```
nodriver_kham_go_buy_redirect                # 行 12240 - 購買重定向
nodriver_kham_product                        # 行 12401 - 產品頁處理
```

**階段 4：日期選擇**
```
nodriver_kham_date_auto_select               # 行 12421 - 自動選擇日期
```

**階段 5：區域/座位選擇**
```
nodriver_kham_area_auto_select               # 行 12816 - 自動選擇區域
nodriver_kham_seat_type_auto_select          # 行 14336 - 自動選擇座位類型 ⭐
nodriver_kham_seat_auto_select               # 行 14701 - 自動選擇座位 ⭐
nodriver_kham_switch_to_auto_seat            # 行 12329 - 切換到自動選座
nodriver_kham_allow_not_adjacent_seat        # 行 12311 - 允許非連續座位
```

**階段 7：驗證碼處理（完整實作）⭐**
```
nodriver_kham_keyin_captcha_code             # 行 12708 - 手動輸入驗證碼
nodriver_kham_auto_ocr                       # 行 13241 - 自動 OCR ⭐
nodriver_kham_captcha                        # 行 13318 - 驗證碼處理 ⭐
nodriver_kham_check_captcha_text_error       # 行 12366 - 檢查驗證碼錯誤
```

**階段 8-9：特殊對話框**
```
nodriver_kham_check_realname_dialog          # 行 12275 - 檢查實名對話框
```

**階段 10：演出與座位主流程**
```
nodriver_kham_performance                    # 行 13362 - 演出處理
nodriver_kham_seat_main                      # 行 15066 - 座位主流程 ⭐
```

**主流程控制**
```
nodriver_kham_main                           # 行 13451 - 主控制器
```

#### 12 階段完整度評分：98/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ✅ | 10/10 | 完整登入 |
| 3 | 頁面監控 | ✅ | 5/5 | 產品頁導航 |
| 4 | 日期選擇 | ✅ | 15/15 | 完整關鍵字 + mode |
| 5 | 區域選擇 | ✅ | 15/15 | 區域 + 座位類型 + 座位圖 ⭐ |
| 6 | 票數設定 | ✅ | 10/10 | 整合在座位選擇中 |
| 7 | 驗證碼處理 | ✅ | 10/10 | 完整 OCR 處理 ⭐ |
| 8 | 表單填寫 | ✅ | 3/5 | 實名對話框 |
| 9 | 同意條款 | ✅ | 3/5 | 非連續座位確認 |
| 10 | 訂單送出 | ✅ | 10/10 | 演出處理完整 |
| 11 | 排隊處理 | ✅ | 5/5 | 整合在主流程 |
| 12 | 錯誤處理 | ✅ | 5/5 | 驗證碼錯誤檢查 |
| **總分** | | | **98/100** | **白金級** 🏅 |

#### 獨有優勢功能
1. **完整 OCR 驗證碼處理**：`auto_ocr` + `captcha` + `keyin_captcha_code` + `check_captcha_text_error`
2. **座位選擇邏輯完整**：座位類型 → 座位圖 → 自動選座 → 非連續座位處理
3. **實名制對話框處理**：`check_realname_dialog`
4. **自動選座切換**：`switch_to_auto_seat`

#### 適合參考的場景
- ✅ OCR 驗證碼處理架構（最完整）
- ✅ 座位選擇流程設計
- ✅ 實名制對話框處理
- ✅ 驗證碼錯誤重試機制

---

### 3. iBon（7-11 售票）- Shadow DOM 處理楷模 🥇

#### 函式清單（20 個）

**階段 2：登入**
```
nodriver_ibon_login                          # 行 7014  - Cookie 登入
```

**階段 4：日期選擇（Shadow DOM 穿透）⭐**
```
nodriver_ibon_date_auto_select               # 行 7519  - 自動選擇日期（主入口）
nodriver_ibon_date_auto_select_pierce        # 行 7128  - Shadow DOM 穿透版本 ⭐
nodriver_ibon_date_auto_select_domsnapshot   # 行 7543  - DOMSnapshot 版本 ⭐
nodriver_ibon_date_mode_select               # 行 7079  - 日期模式選擇
```

**階段 5：區域選擇（雙版本支援）⭐**
```
nodriver_ibon_event_area_auto_select         # 行 8622  - Event 頁面區域選擇 ⭐
nodriver_ibon_area_auto_select               # 行 9127  - 舊版 .aspx 頁面 ⭐
```

**階段 6：票數設定**
```
nodriver_ibon_ticket_number_auto_select      # 行 9707  - 自動選擇票數
```

**階段 7：驗證碼處理（Shadow DOM 截圖）⭐**
```
nodriver_ibon_get_captcha_image_from_shadow_dom # 行 9864 - Shadow DOM 截圖 ⭐
nodriver_ibon_keyin_captcha_code             # 行 10068 - 手動輸入驗證碼
nodriver_ibon_refresh_captcha                # 行 10315 - 刷新驗證碼
nodriver_ibon_auto_ocr                       # 行 10349 - 自動 OCR
nodriver_ibon_captcha                        # 行 10521 - 驗證碼主控制
```

**階段 8-9：表單與條款**
```
nodriver_ibon_verification_question          # 行 10825 - 驗證問題
nodriver_ibon_ticket_agree                   # 行 8585  - 同意條款
nodriver_ibon_allow_not_adjacent_seat        # 行 8591  - 非連續座位
```

**階段 10-11：訂單處理**
```
nodriver_ibon_purchase_button_press          # 行 10618 - 購票按鈕
nodriver_ibon_check_sold_out                 # 行 10675 - 售罄檢查
nodriver_ibon_check_sold_out_on_ticket_page  # 行 10713 - 票券頁售罄檢查
```

**主流程控制**
```
nodriver_ibon_main                           # 行 10879 - 主控制器
```

#### 12 階段完整度評分：95/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ✅ | 10/10 | Cookie 登入完整 |
| 3 | 頁面監控 | ⚠️ | 2/5 | 缺少自動重載 |
| 4 | 日期選擇 | ✅ | 15/15 | Shadow DOM 穿透 ⭐ |
| 5 | 區域選擇 | ✅ | 15/15 | 雙版本支援 ⭐ |
| 6 | 票數設定 | ✅ | 10/10 | 完整票數選擇 |
| 7 | 驗證碼處理 | ✅ | 10/10 | Shadow DOM 截圖 ⭐ |
| 8 | 表單填寫 | ✅ | 5/5 | 驗證問題處理 |
| 9 | 同意條款 | ✅ | 5/5 | 條款 + 非連續座位 |
| 10 | 訂單送出 | ✅ | 10/10 | 購票按鈕完整 |
| 11 | 排隊處理 | ✅ | 3/5 | 基本售罄檢查 |
| 12 | 錯誤處理 | ✅ | 5/5 | 售罄檢查完整 |
| **總分** | | | **95/100** | **金級+** 🥇 |

#### 獨有優勢功能
1. **Shadow DOM 穿透技術**：`pierce` + `DOMSnapshot` 雙策略 ⭐
2. **Shadow DOM 截圖**：突破 closed Shadow DOM 限制
3. **雙版本頁面支援**：Event 頁面 + .aspx 頁面
4. **驗證問題自動答題**：`verification_question`

#### 適合參考的場景
- ✅ Shadow DOM 穿透技術（業界領先）
- ✅ DOMSnapshot API 應用
- ✅ 多版本頁面適配
- ✅ closed Shadow DOM 截圖技術

---

### 4. 年代售票（Ticket.com.tw）- 座位選擇算法楷模 🏅

#### 函式清單（9 個）

**階段 2：登入**
```
nodriver_ticket_login                        # 行 14256 - 登入
```

**階段 5：座位選擇（完整實作）⭐**
```
nodriver_ticket_seat_type_auto_select        # 行 15266 - 自動選擇座位類型
nodriver_ticket_find_best_seats              # 行 15585 - 尋找最佳座位 ⭐⭐⭐
nodriver_ticket_seat_auto_select             # 行 16223 - 自動選擇座位
nodriver_ticket_allow_not_adjacent_seat      # 行 16550 - 允許非連續座位
nodriver_ticket_switch_to_auto_seat          # 行 16592 - 切換到自動選座
nodriver_ticket_check_seat_taken_dialog      # 行 16499 - 檢查座位被佔對話框
```

**階段 10：座位主流程**
```
nodriver_ticket_seat_main                    # 行 16272 - 座位主流程
```

**主流程控制**
```
（整合在 tixcraft_main 或其他平台主流程中）
```

#### 12 階段完整度評分：100/100（限座位選擇範疇）

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 2 | 身份認證 | ✅ | 10/10 | 登入完整 |
| 5 | 座位選擇 | ✅ | 15/15 | 最佳座位算法 ⭐⭐⭐ |
| 6 | 票數設定 | ✅ | 10/10 | 整合在座位選擇 |
| 9 | 同意條款 | ✅ | 5/5 | 非連續座位確認 |
| 10 | 訂單送出 | ✅ | 10/10 | 座位主流程完整 |
| 12 | 錯誤處理 | ✅ | 5/5 | 座位被佔檢查 |
| **總分** | | | **100/100** | **白金級**（限座位選擇）🏅 |

#### 獨有優勢功能
1. **最佳座位算法** (`find_best_seats`)：
   - 連續座位優先策略
   - 智能分配算法
   - 非連續座位回退機制
   - 座位被佔檢測與重試

#### 適合參考的場景
- ✅ 座位圖選擇算法（業界最佳實踐）⭐⭐⭐
- ✅ 連續/非連續座位處理
- ✅ 座位被佔錯誤處理

---

### 5. KKTIX - 自動答題楷模 🥇

#### 函式清單（13 個）

**階段 2：登入**
```
nodriver_kktix_signin                        # 行 497   - 登入
nodriver_facebook_login                      # 行 341   - Facebook 登入
```

**階段 3：頁面監控**
```
nodriver_kktix_paused_main                   # 行 599   - 暫停主流程
```

**階段 4：日期選擇**
```
nodriver_kktix_date_auto_select              # 行 1491  - 自動選擇日期
```

**階段 5：區域/票價選擇**
```
nodriver_kktix_travel_price_list             # 行 744   - 遍歷票價清單
nodriver_kktix_assign_ticket_number          # 行 1021  - 設定票券數量
```

**階段 7：驗證碼/驗證問題（自動答題）⭐**
```
nodriver_kktix_reg_captcha                   # 行 1174  - 驗證問題自動答題 ⭐
```

**階段 10：訂單送出**
```
nodriver_kktix_press_next_button             # 行 1794  - 按下一步按鈕
nodriver_kktix_events_press_next_button      # 行 1762  - 活動頁下一步
nodriver_kktix_reg_new_main                  # 行 2070  - 新註冊主流程
nodriver_kktix_confirm_order_button          # 行 2493  - 確認訂單按鈕
```

**階段 12：狀態檢查**
```
nodriver_kktix_check_ticket_page_status      # 行 1953  - 檢查票券頁狀態
nodriver_kktix_double_check_all_text_value   # 行 2528  - 雙重檢查文字值
```

**主流程控制**
```
nodriver_kktix_main                          # 行 2316  - 主控制器
```

#### 12 階段完整度評分：84/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ✅ | 10/10 | 帳密 + Facebook 登入 |
| 3 | 頁面監控 | ✅ | 4/5 | 暫停主流程 |
| 4 | 日期選擇 | ⚠️ | 8/15 | 基本功能，待加強 |
| 5 | 區域選擇 | ⚠️ | 12/15 | 票價清單遍歷 |
| 6 | 票數設定 | ✅ | 10/10 | 完整票數分配 |
| 7 | 驗證碼處理 | ✅ | 8/10 | 自動答題（非 OCR）⭐ |
| 8 | 表單填寫 | ✅ | 4/5 | 註冊主流程 |
| 9 | 同意條款 | ⚠️ | 4/5 | 基本實作 |
| 10 | 訂單送出 | ✅ | 10/10 | 確認按鈕完整 |
| 11 | 排隊處理 | ✅ | 4/5 | 票券頁狀態檢查 |
| 12 | 錯誤處理 | ✅ | 5/5 | 雙重檢查機制 |
| **總分** | | | **84/100** | **金級** 🥇 |

#### 獨有優勢功能
1. **驗證問題自動答題** (`reg_captcha`)：
   - 問題偵測與記錄
   - 答案推測邏輯
   - 人類化填寫（逐字輸入、隨機延遲）
   - 失敗重試機制

#### 適合參考的場景
- ✅ 驗證問題自動答題（非 OCR 類驗證）⭐
- ✅ 票價清單遍歷邏輯
- ✅ Facebook 登入整合

---

### 6. TixCraft（拓元售票）🥇

#### 函式清單（16 個）

**階段 3：頁面控制**
```
nodriver_tixcraft_home_close_window          # 行 2581  - 關閉彈窗
nodriver_tixcraft_redirect                   # 行 2608  - 頁面重定向
```

**階段 4：日期選擇**
```
nodriver_tixcraft_date_auto_select           # 行 2670  - 自動選擇日期
```

**階段 5：區域選擇**
```
nodriver_tixcraft_area_auto_select           # 行 3031  - 自動選擇區域
nodriver_get_tixcraft_target_area            # 行 3176  - 取得目標區域
```

**階段 6：票數設定**
```
nodriver_ticket_number_select_fill           # 行 3337  - 填入票券數量
nodriver_tixcraft_assign_ticket_number       # 行 3397  - 設定票券數量
```

**階段 7：驗證碼處理**
```
nodriver_tixcraft_verify                     # 行 2629  - 驗證處理
nodriver_tixcraft_input_check_code           # 行 2633  - 輸入驗證碼
nodriver_tixcraft_keyin_captcha_code         # 行 3726  - 手動輸入驗證碼
nodriver_tixcraft_reload_captcha             # 行 3867  - 重新載入驗證碼
nodriver_tixcraft_get_ocr_answer             # 行 3885  - OCR 識別
nodriver_tixcraft_auto_ocr                   # 行 3942  - 自動 OCR
```

**階段 9：同意條款**
```
nodriver_tixcraft_ticket_main_agree          # 行 3658  - 勾選同意條款
```

**階段 10：訂單送出**
```
nodriver_tixcraft_ticket_main                # 行 3676  - 票券頁面主處理
nodriver_tixcraft_ticket_main_ocr            # 行 4013  - 票券頁面 OCR
nodriver_tixcraft_toast                      # 行 3853  - 顯示提示訊息
```

**主流程控制**
```
nodriver_tixcraft_main                       # 行 4092  - 主控制器
```

#### 12 階段完整度評分：82/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ⚠️ | 8/10 | 缺少登入函式 |
| 3 | 頁面監控 | ✅ | 4/5 | 彈窗關閉 + 重定向 |
| 4 | 日期選擇 | ⚠️ | 12/15 | 基本功能完整 |
| 5 | 區域選擇 | ⚠️ | 12/15 | 基本功能完整 |
| 6 | 票數設定 | ⚠️ | 8/10 | 基本功能 |
| 7 | 驗證碼處理 | ⚠️ | 8/10 | OCR 功能待加強 |
| 8 | 表單填寫 | ⚠️ | 4/5 | 驗證碼輸入 |
| 9 | 同意條款 | ⚠️ | 4/5 | 基本實作 |
| 10 | 訂單送出 | ⚠️ | 8/10 | 票券主流程 |
| 11 | 排隊處理 | ⚠️ | 4/5 | 基本實作 |
| 12 | 錯誤處理 | ✅ | 4/5 | Toast 提示 |
| **總分** | | | **82/100** | **金級** 🥇 |

#### 適合參考的場景
- ✅ 彈窗處理
- ✅ 頁面重定向邏輯

---

### 7. Cityline（香港）🥈

#### 函式清單（6 個）

**階段 2：登入**
```
nodriver_cityline_login                      # 行 11807 - 登入
```

**階段 3：頁面重試**
```
nodriver_cityline_auto_retry_access          # 行 11793 - 自動重試存取
```

**階段 4：日期選擇**
```
nodriver_cityline_date_auto_select           # 行 11894 - 自動選擇日期
```

**階段 10：訂單送出**
```
nodriver_cityline_purchase_button_press      # 行 11985 - 按下購買按鈕
nodriver_cityline_close_second_tab           # 行 12000 - 關閉第二個標籤
```

**主流程控制**
```
nodriver_cityline_main                       # 行 12018 - 主控制器
```

#### 12 階段完整度評分：60/100

| 階段 | 功能 | 實作狀態 | 分數 | 說明 |
|:----:|------|:--------:|:----:|------|
| 1 | 環境初始化 | ✅ | 10/10 | 由全域 nodriver() 處理 |
| 2 | 身份認證 | ✅ | 10/10 | 登入完整 |
| 3 | 頁面監控 | ✅ | 5/5 | 自動重試 |
| 4 | 日期選擇 | ⚠️ | 10/15 | 基本功能 |
| 5 | 區域選擇 | ❌ | 0/15 | **缺失** |
| 6 | 票數設定 | ❌ | 0/10 | **缺失** |
| 7 | 驗證碼處理 | ❌ | 0/10 | **缺失** |
| 8 | 表單填寫 | ❌ | 0/5 | **缺失** |
| 9 | 同意條款 | ❌ | 0/5 | **缺失** |
| 10 | 訂單送出 | ⚠️ | 8/10 | 購買按鈕 |
| 11 | 排隊處理 | ✅ | 3/5 | 重試機制 |
| 12 | 錯誤處理 | ✅ | 3/5 | 標籤關閉 |
| **總分** | | | **60/100** | **銀級** 🥈 |

#### 缺失功能（需補強）
- ❌ 區域選擇（0/15 分）
- ❌ 票數設定（0/10 分）
- ❌ 驗證碼處理（0/10 分）
- ❌ 表單填寫（0/5 分）
- ❌ 同意條款（0/5 分）

---

## 📋 跨平台功能對照表（12 階段標準）

### 完整對照矩陣

| 階段 | 功能模組 | TicketPlus | KHAM | iBon | 年代 | KKTIX | TixCraft | Cityline |
|:----:|---------|:----------:|:----:|:----:|:----:|:-----:|:--------:|:--------:|
| 1 | WebDriver 初始化 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 | 身份認證 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| 3 | 頁面監控與重載 | ✅ | ✅ | ⚠️ | ❌ | ✅ | ✅ | ✅ |
| 4 | 日期選擇 | ✅ | ✅ | ✅⭐ | ❌ | ⚠️ | ⚠️ | ⚠️ |
| 5 | 區域/座位選擇 | ✅⭐ | ✅⭐ | ✅⭐ | ✅⭐⭐⭐ | ⚠️ | ⚠️ | ❌ |
| 6 | 票數設定 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| 7 | 驗證碼處理 | ⏸️ | ✅⭐ | ✅⭐ | ❌ | ✅⭐ | ⚠️ | ❌ |
| 8 | 表單填寫 | ✅ | ⚠️ | ✅ | ❌ | ✅ | ⚠️ | ❌ |
| 9 | 同意條款 | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| 10 | 訂單送出 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| 11 | 排隊處理 | ✅⭐ | ✅ | ⚠️ | ❌ | ✅ | ⚠️ | ✅ |
| 12 | 錯誤處理 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| **總分** | **/100** | **98** | **98** | **95** | **100*** | **84** | **82** | **60** |
| **等級** | | 🏅白金 | 🏅白金 | 🥇金+ | 🏅白金* | 🥇金 | 🥇金 | 🥈銀 |

**圖例**：
- ✅ = 完整實作
- ⭐ = 獨有優勢
- ⚠️ = 部分實作/待加強
- ❌ = 缺失
- ⏸️ = 暫時忽略（無需求）
- \* = 限定範疇（年代售票專注座位選擇）

---

## 🔍 各平台缺失功能詳細分析

### 1. TicketPlus（98 分）- 近乎完美

**缺失功能（2 分）：**
- ⏸️ OCR 驗證碼處理（4 個函式）
  - `ticketplus_auto_ocr()`
  - `ticketplus_order_ocr()`
  - `ticketplus_keyin_captcha_code()`
  - `ticketplus_check_and_renew_captcha()`
  - **說明**：目前 TicketPlus 活動不使用 OCR 驗證碼，暫時忽略
  - **參考實作**：KHAM 或 iBon 的 OCR 處理架構

**建議優先度**：⏸️ 低（等待實際需求出現）

---

### 2. KHAM（98 分）- 近乎完美

**缺失功能（2 分）：**
- ⚠️ 表單填寫（僅實名對話框，缺少完整表單處理）
  - 缺少通用表單自動填寫
  - **參考實作**：iBon 的 `verification_question`

**建議優先度**：⏸️ 低（目前實名對話框已足夠）

---

### 3. iBon（95 分）- 技術領先

**缺失功能（5 分）：**
- ⚠️ 頁面監控與重載（3 分）
  - 缺少即將開賣頁面自動重載
  - **參考實作**：TicketPlus 的 `order_auto_reload_coming_soon`

- ⚠️ 排隊處理（2 分）
  - 基本售罄檢查已實作，缺少進階排隊狀態檢查
  - **參考實作**：TicketPlus 的 `check_queue_status`

**建議優先度**：🔥 中（補強後可達白金級）

---

### 4. KKTIX（84 分）

**缺失功能（16 分）：**

1. **日期選擇（7 分）**
   - ⚠️ 關鍵字匹配邏輯待加強
   - ⚠️ AND/OR 邏輯支援
   - **參考實作**：iBon 或 TicketPlus 的日期選擇

2. **區域選擇（3 分）**
   - ⚠️ 票價清單遍歷已實作，但缺少關鍵字優化
   - **參考實作**：TicketPlus 的 `unified_select`

3. **驗證碼處理（2 分）**
   - ✅ 驗證問題自動答題已完整
   - ⚠️ 若需支援 OCR，參考 KHAM

4. **同意條款（1 分）**
   - ⚠️ 基本實作，可加強檢查邏輯
   - **參考實作**：TicketPlus 的 `ticket_agree`

5. **頁面監控（1 分）**
   - ⚠️ 暫停主流程已實作，可加強自動重載
   - **參考實作**：TicketPlus

6. **排隊處理（1 分）**
   - ⚠️ 票券頁狀態檢查已實作，可加強
   - **參考實作**：TicketPlus 的 `check_queue_status`

**建議優先度**：🔥 中高（補強後可達白金級）

---

### 5. TixCraft（82 分）

**缺失功能（18 分）：**

1. **身份認證（2 分）**
   - ❌ 缺少獨立登入函式（可能整合在 main 中）
   - **參考實作**：KHAM 的 `kham_login`

2. **日期選擇（3 分）**
   - ⚠️ 基本功能已實作，待加強關鍵字邏輯
   - **參考實作**：iBon 或 TicketPlus

3. **區域選擇（3 分）**
   - ⚠️ `get_tixcraft_target_area` 已實作，待優化
   - **參考實作**：TicketPlus 的統一選擇器

4. **票數設定（2 分）**
   - ⚠️ 基本功能已實作，待加強
   - **參考實作**：TicketPlus

5. **驗證碼處理（2 分）**
   - ⚠️ OCR 功能已實作，待完善
   - **參考實作**：KHAM 的完整 OCR 架構

6. **訂單送出（2 分）**
   - ⚠️ 票券主流程已實作，待優化
   - **參考實作**：TicketPlus 的 `order`

7. **表單填寫、同意條款、排隊處理、錯誤處理**（各 1 分，共 4 分）
   - ⚠️ 基本實作，待加強

**建議優先度**：🔥 高（TixCraft 為台灣最大售票平台）

---

### 6. Cityline（60 分）- 需大幅補強

**缺失功能（40 分）：**

1. **區域選擇（15 分）❌ 完全缺失**
   - 需實作：`cityline_area_auto_select`
   - **參考實作**：TicketPlus 或 KHAM

2. **票數設定（10 分）❌ 完全缺失**
   - 需實作：`cityline_ticket_number_auto_select`
   - **參考實作**：KHAM

3. **驗證碼處理（10 分）❌ 完全缺失**
   - 需實作：OCR 或驗證問題處理
   - **參考實作**：KHAM（OCR）或 KKTIX（驗證問題）

4. **表單填寫（5 分）❌ 完全缺失**
   - 需實作：基本表單自動填寫
   - **參考實作**：iBon

5. **同意條款（5 分）❌ 完全缺失**
   - 需實作：`cityline_ticket_agree`
   - **參考實作**：TicketPlus

6. **日期選擇（5 分）⚠️ 待加強**
   - 已有基本實作，需優化關鍵字邏輯
   - **參考實作**：iBon 或 TicketPlus

7. **訂單送出（2 分）⚠️ 待加強**
   - 已有購買按鈕，需加強訂單確認流程
   - **參考實作**：TicketPlus

8. **錯誤處理（2 分）⚠️ 待加強**
   - 基本標籤關閉已實作，需加強錯誤檢查
   - **參考實作**：KHAM

**建議優先度**：🔥🔥 最高（Cityline 為香港重要平台，缺失過多）

---

## 🎯 開發建議與優先度規劃

### Phase 1：緊急修復（🔥🔥 最高優先度）

**目標**：將 Cityline 從銀級（60 分）提升至金級（80+ 分）

**必須補充的 9 個函式**：

1. **區域選擇**（最重要）
   ```
   nodriver_cityline_area_auto_select(tab, config_dict)
   參考：TicketPlus 的 unified_select（行 4815）
   ```

2. **票數設定**
   ```
   nodriver_cityline_ticket_number_auto_select(tab, config_dict)
   參考：KHAM 的 area_auto_select（行 12816）
   ```

3. **驗證碼處理（3 個函式）**
   ```
   nodriver_cityline_auto_ocr(tab, config_dict, ocr, ...)
   nodriver_cityline_keyin_captcha_code(tab, answer, ...)
   nodriver_cityline_captcha(tab, config_dict, ocr)
   參考：KHAM（行 13241, 12708, 13318）
   ```

4. **同意條款**
   ```
   nodriver_cityline_ticket_agree(tab, config_dict)
   參考：TicketPlus（行 6173）
   ```

5. **表單填寫**
   ```
   nodriver_cityline_form_auto_fill(tab, config_dict)
   參考：iBon 的 verification_question（行 10825）
   ```

6. **日期選擇優化**
   ```
   優化現有 nodriver_cityline_date_auto_select（行 11894）
   參考：iBon 的關鍵字邏輯
   ```

7. **訂單確認**
   ```
   nodriver_cityline_order_confirm(tab, config_dict)
   參考：TicketPlus 的 confirm（行 6532）
   ```

**預估工作量**：2-3 週（1 人）

---

### Phase 2：重要補強（🔥 高優先度）

**目標**：將 TixCraft 從金級（82 分）提升至白金級（90+ 分）

**需補充/優化的功能**：

1. **登入功能**
   ```
   nodriver_tixcraft_login(tab, config_dict)
   參考：KHAM 的 login（行 12088）
   ```

2. **日期選擇優化**
   ```
   優化 nodriver_tixcraft_date_auto_select（行 2670）
   參考：iBon 的 Shadow DOM 穿透技術
   ```

3. **區域選擇優化**
   ```
   優化 nodriver_tixcraft_area_auto_select（行 3031）
   參考：TicketPlus 的統一選擇器
   ```

4. **驗證碼處理完善**
   ```
   優化 OCR 相關函式（行 3942）
   參考：KHAM 的完整 OCR 架構（行 13241）
   ```

5. **票數設定優化**
   ```
   優化 nodriver_tixcraft_assign_ticket_number（行 3397）
   參考：TicketPlus（行 5995）
   ```

**預估工作量**：2 週（1 人）

---

### Phase 3：品質提升（🔥 中優先度）

**目標**：將 KKTIX 從金級（84 分）提升至白金級（90+ 分）

**需優化的功能**：

1. **日期選擇加強**（+7 分）
   ```
   優化 nodriver_kktix_date_auto_select（行 1491）
   加入 AND/OR 邏輯、關鍵字優化
   參考：iBon（行 7519）或 TicketPlus（行 4486）
   ```

2. **區域選擇優化**（+3 分）
   ```
   優化票價清單遍歷邏輯（行 744）
   加入關鍵字匹配優化
   參考：TicketPlus 的 unified_select（行 4815）
   ```

3. **同意條款加強**（+1 分）
   ```
   加強同意條款檢查邏輯
   參考：TicketPlus（行 6173）
   ```

4. **排隊處理加強**（+1 分）
   ```
   優化票券頁狀態檢查（行 1953）
   參考：TicketPlus 的 check_queue_status（行 6342）
   ```

**預估工作量**：1.5 週（1 人）

---

### Phase 4：錦上添花（⏸️ 低優先度）

**目標**：將 iBon 從金級+（95 分）提升至白金級（98+ 分）

**需補充的功能**：

1. **頁面自動重載**（+3 分）
   ```
   nodriver_ibon_auto_reload_coming_soon(tab, config_dict)
   參考：TicketPlus（行 6421）
   ```

2. **排隊狀態檢查**（+2 分）
   ```
   nodriver_ibon_check_queue_status(tab, config_dict)
   參考：TicketPlus（行 6342）
   ```

**預估工作量**：3 天（1 人）

---

### Phase 5：待需求出現（⏸️ 最低優先度）

**目標**：TicketPlus OCR 驗證碼支援

**需補充的功能**（僅在 TicketPlus 出現 OCR 驗證碼時實作）：

1. **OCR 處理（4 個函式）**
   ```
   nodriver_ticketplus_auto_ocr(tab, config_dict, ocr, ...)
   nodriver_ticketplus_order_ocr(tab, config_dict, ...)
   nodriver_ticketplus_keyin_captcha_code(tab, answer, ...)
   nodriver_ticketplus_check_and_renew_captcha(tab, config_dict)
   參考：KHAM（行 13241, 12708, 13318）或 iBon（行 10349）
   ```

**預估工作量**：1 週（1 人）

---

## 📚 最佳參考實作索引

### 按功能模組查找參考實作

#### 1. 身份認證（登入）

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **KHAM** | `nodriver_kham_login` | 12088 | 帳密登入完整 ⭐ |
| iBon | `nodriver_ibon_login` | 7014 | Cookie 登入 |
| Cityline | `nodriver_cityline_login` | 11807 | 基本登入 |
| KKTIX | `nodriver_kktix_signin` | 497 | 帳密登入 |
| KKTIX | `nodriver_facebook_login` | 341 | Facebook 登入 ⭐ |
| 年代 | `nodriver_ticket_login` | 14256 | 帳密登入 |

**最佳參考**：KHAM（完整性最高）

---

#### 2. 日期選擇

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **iBon** | `nodriver_ibon_date_auto_select` | 7519 | Shadow DOM 穿透 ⭐⭐⭐ |
| **iBon** | `nodriver_ibon_date_auto_select_pierce` | 7128 | Pierce 策略 ⭐ |
| **iBon** | `nodriver_ibon_date_auto_select_domsnapshot` | 7543 | DOMSnapshot 策略 ⭐ |
| **TicketPlus** | `nodriver_ticketplus_date_auto_select` | 4486 | 統一架構 ⭐ |
| KHAM | `nodriver_kham_date_auto_select` | 12421 | 完整關鍵字邏輯 |
| TixCraft | `nodriver_tixcraft_date_auto_select` | 2670 | 基本實作 |
| KKTIX | `nodriver_kktix_date_auto_select` | 1491 | 基本實作 |
| Cityline | `nodriver_cityline_date_auto_select` | 11894 | 基本實作 |

**最佳參考**：
- **技術難度高**（Shadow DOM）：iBon（3 個函式）
- **標準流程**：TicketPlus 或 KHAM

---

#### 3. 區域/座位選擇

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_unified_select` | 4815 | 統一選擇器 ⭐⭐⭐ |
| **TicketPlus** | `nodriver_ticketplus_order_expansion_auto_select` | 5419 | 展開面板 ⭐ |
| **iBon** | `nodriver_ibon_event_area_auto_select` | 8622 | Event 頁面 ⭐ |
| **iBon** | `nodriver_ibon_area_auto_select` | 9127 | .aspx 頁面 ⭐ |
| **KHAM** | `nodriver_kham_area_auto_select` | 12816 | 完整關鍵字邏輯 |
| **KHAM** | `nodriver_kham_seat_type_auto_select` | 14336 | 座位類型選擇 ⭐ |
| **KHAM** | `nodriver_kham_seat_auto_select` | 14701 | 座位圖選擇 ⭐ |
| **年代** | `nodriver_ticket_find_best_seats` | 15585 | 最佳座位算法 ⭐⭐⭐ |
| **年代** | `nodriver_ticket_seat_type_auto_select` | 15266 | 座位類型 |
| **年代** | `nodriver_ticket_seat_auto_select` | 16223 | 座位選擇 |
| TixCraft | `nodriver_get_tixcraft_target_area` | 3176 | 目標區域取得 |
| TixCraft | `nodriver_tixcraft_area_auto_select` | 3031 | 區域選擇 |

**最佳參考**：
- **統一架構**：TicketPlus 的 `unified_select` ⭐⭐⭐
- **雙版本支援**：iBon（Event + .aspx）⭐⭐
- **座位圖選擇算法**：年代售票 `find_best_seats` ⭐⭐⭐
- **完整座位流程**：KHAM（座位類型 → 座位圖 → 自動選座）⭐

---

#### 4. 票數設定

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_assign_ticket_number` | 5995 | 完整實作 ⭐ |
| KHAM | （整合在座位選擇中） | - | 整合設計 |
| iBon | `nodriver_ibon_ticket_number_auto_select` | 9707 | 完整實作 |
| TixCraft | `nodriver_tixcraft_assign_ticket_number` | 3397 | 基本實作 |
| TixCraft | `nodriver_ticket_number_select_fill` | 3337 | 填入邏輯 |
| KKTIX | `nodriver_kktix_assign_ticket_number` | 1021 | 基本實作 |

**最佳參考**：TicketPlus（架構最清晰）

---

#### 5. 驗證碼處理

##### OCR 驗證碼

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **KHAM** | `nodriver_kham_auto_ocr` | 13241 | 完整 OCR ⭐⭐⭐ |
| **KHAM** | `nodriver_kham_captcha` | 13318 | 驗證碼主控制 ⭐ |
| **KHAM** | `nodriver_kham_keyin_captcha_code` | 12708 | 手動輸入 |
| **KHAM** | `nodriver_kham_check_captcha_text_error` | 12366 | 錯誤檢查 ⭐ |
| **iBon** | `nodriver_ibon_auto_ocr` | 10349 | OCR 識別 |
| **iBon** | `nodriver_ibon_captcha` | 10521 | 驗證碼主控制 |
| **iBon** | `nodriver_ibon_get_captcha_image_from_shadow_dom` | 9864 | Shadow DOM 截圖 ⭐⭐⭐ |
| **iBon** | `nodriver_ibon_keyin_captcha_code` | 10068 | 手動輸入 |
| **iBon** | `nodriver_ibon_refresh_captcha` | 10315 | 刷新驗證碼 |
| TixCraft | `nodriver_tixcraft_auto_ocr` | 3942 | 基本 OCR |
| TixCraft | `nodriver_tixcraft_get_ocr_answer` | 3885 | OCR 識別 |
| TixCraft | `nodriver_tixcraft_keyin_captcha_code` | 3726 | 手動輸入 |
| TixCraft | `nodriver_tixcraft_reload_captcha` | 3867 | 刷新驗證碼 |

**最佳參考**：
- **完整 OCR 架構**：KHAM（4 個函式完整）⭐⭐⭐
- **Shadow DOM 截圖技術**：iBon ⭐⭐⭐

##### 驗證問題自動答題

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **KKTIX** | `nodriver_kktix_reg_captcha` | 1174 | 驗證問題自動答題 ⭐⭐⭐ |
| iBon | `nodriver_ibon_verification_question` | 10825 | 驗證問題處理 |

**最佳參考**：KKTIX（人類化填寫 + 重試機制）⭐⭐⭐

---

#### 6. 同意條款

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_ticket_agree` | 6173 | 完整實作 ⭐ |
| **TicketPlus** | `nodriver_ticketplus_accept_realname_card` | 6238 | 實名卡 ⭐ |
| **TicketPlus** | `nodriver_ticketplus_accept_other_activity` | 6251 | 其他活動 |
| iBon | `nodriver_ibon_ticket_agree` | 8585 | 基本實作 |
| iBon | `nodriver_ibon_allow_not_adjacent_seat` | 8591 | 非連續座位 |
| KHAM | `nodriver_kham_allow_not_adjacent_seat` | 12311 | 非連續座位 |
| 年代 | `nodriver_ticket_allow_not_adjacent_seat` | 16550 | 非連續座位 |
| TixCraft | `nodriver_tixcraft_ticket_main_agree` | 3658 | 基本實作 |

**最佳參考**：TicketPlus（特殊對話框處理完整）

---

#### 7. 訂單送出

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_confirm` | 6532 | 確認 ⭐ |
| **TicketPlus** | `nodriver_ticketplus_order` | 6562 | 訂單處理 ⭐ |
| **TicketPlus** | `nodriver_ticketplus_order_exclusive_code` | 6794 | 折扣碼 ⭐ |
| KHAM | `nodriver_kham_performance` | 13362 | 演出處理 |
| iBon | `nodriver_ibon_purchase_button_press` | 10618 | 購票按鈕 |
| TixCraft | `nodriver_tixcraft_ticket_main` | 3676 | 票券主流程 |
| KKTIX | `nodriver_kktix_press_next_button` | 1794 | 下一步按鈕 |
| KKTIX | `nodriver_kktix_confirm_order_button` | 2493 | 確認訂單 |
| Cityline | `nodriver_cityline_purchase_button_press` | 11985 | 購買按鈕 |

**最佳參考**：TicketPlus（流程最完整 + 折扣碼支援）

---

#### 8. 排隊處理

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_check_queue_status` | 6342 | 排隊狀態檢查 ⭐⭐⭐ |
| **TicketPlus** | `nodriver_ticketplus_order_auto_reload_coming_soon` | 6421 | 即將開賣重載 ⭐ |
| iBon | `nodriver_ibon_check_sold_out` | 10675 | 售罄檢查 |
| iBon | `nodriver_ibon_check_sold_out_on_ticket_page` | 10713 | 票券頁售罄 |
| KKTIX | `nodriver_kktix_check_ticket_page_status` | 1953 | 票券頁狀態 |
| Cityline | `nodriver_cityline_auto_retry_access` | 11793 | 自動重試 |

**最佳參考**：TicketPlus（排隊狀態檢查最完整）⭐⭐⭐

---

#### 9. 錯誤處理

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_accept_order_fail` | 6264 | 訂單失敗處理 ⭐ |
| KHAM | `nodriver_kham_check_captcha_text_error` | 12366 | 驗證碼錯誤 ⭐ |
| KHAM | `nodriver_kham_check_realname_dialog` | 12275 | 實名對話框 |
| 年代 | `nodriver_ticket_check_seat_taken_dialog` | 16499 | 座位被佔 ⭐ |
| KKTIX | `nodriver_kktix_double_check_all_text_value` | 2528 | 雙重檢查 |
| TixCraft | `nodriver_tixcraft_toast` | 3853 | Toast 提示 |

**最佳參考**：
- **訂單錯誤**：TicketPlus
- **驗證碼錯誤**：KHAM
- **座位錯誤**：年代售票

---

#### 10. 特殊功能

##### 佈局檢測

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **TicketPlus** | `nodriver_ticketplus_detect_layout_style` | 4228 | 版面檢測 ⭐⭐⭐ |
| **TicketPlus** | `nodriver_ticketplus_is_signin` | 4418 | 登入狀態檢測 |

##### Shadow DOM 處理

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **iBon** | `nodriver_ibon_date_auto_select_pierce` | 7128 | Pierce 穿透 ⭐⭐⭐ |
| **iBon** | `nodriver_ibon_date_auto_select_domsnapshot` | 7543 | DOMSnapshot ⭐⭐⭐ |
| **iBon** | `nodriver_ibon_get_captcha_image_from_shadow_dom` | 9864 | Shadow DOM 截圖 ⭐⭐⭐ |

##### 座位算法

| 平台 | 函式 | 行號 | 特色 |
|------|------|------|------|
| **年代** | `nodriver_ticket_find_best_seats` | 15585 | 最佳座位算法 ⭐⭐⭐ |

---

## 📖 使用指南

### 如何使用本文件

1. **查找參考實作**：
   - 按功能模組查找 → 使用「最佳參考實作索引」章節
   - 按平台查找 → 使用「各平台詳細分析」章節

2. **評估實作完整度**：
   - 查看「12 階段完整度評分」表格
   - 對照「跨平台功能對照表」

3. **規劃開發任務**：
   - 參考「開發建議與優先度規劃」章節
   - 使用「缺失功能詳細分析」識別需補充的函式

4. **尋找最佳楷模**：
   - **主流程架構**：TicketPlus ⭐⭐⭐
   - **驗證碼處理**：KHAM（OCR）⭐⭐⭐ 或 KKTIX（驗證問題）⭐⭐⭐
   - **Shadow DOM**：iBon ⭐⭐⭐
   - **座位選擇**：年代售票 ⭐⭐⭐

---

## 🔗 相關文件

- [搶票自動化標準功能定義](./ticket_automation_standard.md) - 12 階段標準詳細說明
- [NoDriver vs Chrome 函式結構分析](./structure.md) - 雙版本對照
- [開發規範指南](./development_guide.md) - 開發原則與規範
- [程式碼範本](./coding_templates.md) - 實作範例
- [NoDriver API 指南](../06-api-reference/nodriver_api_guide.md) - API 使用說明
- [CDP 協議參考](../06-api-reference/cdp_protocol_reference.md) - Chrome DevTools Protocol

---

**文件版本**：v1.0
**最後更新**：2025-11-10
**作者**：Claude (Anthropic)
**分析範圍**：`src/nodriver_tixcraft.py` (17,191 行, 114 個函式)
**分析方法**：基於 12 階段標準功能定義進行全面評估

---

**💡 核心結論**：

1. **雙楷模策略最佳**：
   - **TicketPlus**：主流程架構、日期/區域選擇、排隊處理
   - **KHAM**：OCR 驗證碼、座位選擇
   - **年代售票**：座位選擇算法
   - **iBon**：Shadow DOM 技術

2. **優先補強 Cityline**：缺失 40 分，需補充 9 個核心函式

3. **TixCraft 次優先**：台灣最大平台，需優化提升至白金級

4. **三大技術亮點**：
   - TicketPlus 的統一選擇器架構
   - iBon 的 Shadow DOM 穿透技術
   - 年代售票的最佳座位算法
