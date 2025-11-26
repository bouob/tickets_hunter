**文件說明**：專案待實作功能清單，包含開發策略、版本優先度、平台進度與任務優先級。

**最後更新**：2025-11-26

---

# 待實作功能清單

> 基於最新開發規範更新，按版本優先度重新整理

## ⚠️ **開發策略調整**

**版本優先度**：
- **Chrome/Selenium 版本** 【必須優先】：完善穩定，已運作於多平台
- **NoDriver 版本** 【**已可正常使用**】：三大主流平台（TixCraft、KKTIX、TicketPlus）功能完整

**新開發方針**：
1. **Chrome 版本持續完善**：確保所有平台功能完整穩定
2. **NoDriver 版本已可使用**：三大主流平台已完全可用，可作為反偵測選擇
3. **遵循標準架構**：參考 `/docs/coding_templates.md` 統一規範

---

## 🚨 **第一階段：核心修復（影響所有平台）**

### 日期 AND 邏輯篩選 ✅ **已實作**
- **Chrome**: `chrome_tixcraft.py:967, 1204` ✅ 已完成
- **NoDriver**: `nodriver_tixcraft.py:1144-1327` ✅ 已完成
- **平台**: TixCraft, TicketMaster
- **狀態**: 已支援 JSON 陣列格式的 AND/OR 邏輯篩選
- **實作**: 透過 `json.loads("[" + date_keyword + "]")` 支援複雜邏輯

---

## 🐛 **使用者回報問題修復（高優先度）**

> 以下為使用者實際回報的問題，需優先調查與修復

### 1. TixCraft 自動登入失效問題 ✅ **已修復**
- **問題描述**: 在設定檔案中設定了 SID 但是沒有自動登入
- **影響範圍**: TixCraft 平台（NoDriver 版本）
- **嚴重程度**: 🔥 高 - 影響核心登入功能
- **狀態**: ✅ 已修復並測試通過 (2025-10-17)
- **根本原因**:
  1. Cookie domain 設定錯誤：`domain="tixcraft.com"` 無法套用到子域名
  2. `http_only=True` 與 Chrome 版本不一致
- **解決方案**:
  - 修正 `nodriver_goto_homepage()` 函數 (Line 640-660)
  - 將 domain 改為 `.tixcraft.com`（包含所有子域名）
  - 將 `http_only` 改為 `False`（與 Chrome 一致）
  - 增加 verbose 模式除錯訊息
- **測試結果**:
  ```
  Setting tixcraft SID cookie, length: 26
  tixcraft SID cookie set successfully
  https://tixcraft.com/activity/detail/25_yama
  ```
  ✅ 自動登入功能正常運作

### 2. KKTIX 票券選擇器更新與暫停機制修復 ✅ **已修復**
- **問題描述**:
  1. 新版 KKTIX 頁面（register-intent-new）無法選擇票券數量
  2. 搶票完成後持續輸出訊息，無法進入暫停狀態
- **影響範圍**: KKTIX 平台（NoDriver 版本）
- **嚴重程度**: 🔥 高 - 影響核心購票流程與暫停機制
- **狀態**: ✅ 已修復並測試通過 (2025-10-18)
- **根本原因**:
  1. **選擇器問題**: KKTIX 更新 HTML 結構，從 `div.display-table-row` 改為 `div.ticket-item`
  2. **暫停問題**: `check_kktix_got_ticket()` 函數錯誤將返回值設為 `False`，導致無法觸發暫停
- **解決方案**:
  - **修正 1**: `nodriver_kktix_travel_price_list()` (Lines 698-763)
    - 採用舊版優先策略：先嘗試 `div.display-table-row`，找不到才用 `div.ticket-item`
    - JavaScript 查詢邏輯支援雙版本選擇器
  - **修正 2**: `nodriver_kktix_assign_ticket_number()` (Lines 974-991)
    - Input 選擇器支援雙版本：`div.display-table-row input` 或 `div.ticket-item input.number-step-input-core`
    - 父元素查詢支援雙版本回退策略
  - **修正 3**: `check_kktix_got_ticket()` (Lines 1813-1816)
    - 移除 `is_kktix_got_ticket = False` 錯誤賦值
    - 保留除錯訊息，但不改變返回值
    - 重複動作保護已由 `success_actions_done` 標記處理
- **測試結果**:
  - ✅ 舊版頁面（kktix1.html, kktix2.html）繼續正常運作
  - ✅ 新版頁面（kktix-HK.html）自動回退到新選擇器
  - ✅ 搶票成功後立即進入暫停狀態
  - ✅ 不再重複輸出訊息

### 3. iBon 登入後區域選擇無動作 🟡
- **問題描述**: 登入後進入選取票區時沒有做動作
- **影響範圍**: iBon 平台
- **影響版本**: 待確認（Chrome/NoDriver）
- **嚴重程度**: 🔥 高 - 影響核心購票流程
- **狀態**: 🟡 需進一步驗證（NoDriver 核心流程已完整 95%）
- **相關檔案**:
  - Chrome: `chrome_tixcraft.py:4636-7132`
  - NoDriver: `nodriver_tixcraft.py:5806-11530`（金級實作 95%）
- **備註**: NoDriver 版本核心搶票流程已 100% 完成，包含日期選擇、區域選擇、票數填寫、驗證碼識別，此問題可能為特定情況或已間接修復
- **建議調查方向**:
  - 檢查日期選擇後的流程銜接
  - 確認區域選擇函數是否被觸發
  - 驗證 `ibon_area_auto_select()` 或 `nodriver_ibon_area_auto_select()` 函數
  - 檢查 Shadow DOM 元素偵測邏輯

---

## 🔥 **第二階段：Chrome 版本平台完善（高優先度）**

### Chrome 版本功能缺口檢查
所有平台 Chrome 版本已基本完善，需要進行以下檢查與優化：

#### OCR 效能優化 ⏳ **低優先度**
- **問題**: OCR 初始化時間過長，每次進入主循環都重新初始化 ddddocr 物件（1-3秒延遲）
- **狀態**: 已識別問題根本原因，目前功能正常運作，暫不處理 ⚠️
- **影響平台**: 6個平台（TixCraft、Ticketmaster、iBon、KHAM、TicketPlus、KKTIX）
- **建議**: 將 OCR 初始化移至程式啟動時，避免重複載入 40-50MB 深度學習模型

#### Chrome 版本穩定性測試
- **目標**: 確保所有平台 Chrome 版本穩定運作
- **測試範圍**: TixCraft, KKTIX, TicketMaster, iBon, Cityline, TicketPlus, Urbtix, KHAM, HK Ticketing, FamiTicket
- **重點**: 驗證核心搶票流程無障礙

---

## 🔧 **第三階段：NoDriver 版本考慮（低優先度）**

> **重要更新**: NoDriver 版本三大主流平台已完全可用，實測搶票功能正常

### 現有 NoDriver 實作狀態 ✅ **實測確認：三大平台完全可用**

> **實測確認**: NoDriver 版本四大主流平台（TixCraft、KKTIX、TicketPlus、iBon）**已可完全正常搶票使用**，實際完成度約 **70%**，共 **88 個函式**（nodriver_tixcraft.py: 12,602 行）。

#### 完全可用平台 ✅ **實測通過** (95%)
- **TixCraft 拓元**: ✅ **完全可用** (Lines 1266-2186)
  - 日期選擇（含 AND/OR 邏輯）✅ 已完成
  - 區域選擇邏輯 ✅ 已完成
  - 票數設定 ✅ 已完成
  - OCR 驗證碼處理 ✅ 已完成
  - 勾選同意條款 ✅ 已完成
  - **實測狀態：搶票功能完全正常**
- **Teamear 添翼**: ✅ **完全可用** (與 TixCraft 共用程式碼)
  - **Tixcraft Family 成員** - 共用 100% 邏輯
  - 支援 button[data-href]、售罄過濾等完整功能
  - **實測狀態：搶票功能完全正常 (2025.10.22)**
- **Indievox 獨立音樂**: ✅ **完全可用** (與 TixCraft 共用程式碼)
  - **Tixcraft Family 成員** - 共用 100% 邏輯
  - ✅ 2025.10.22 修復：售罄選項過濾（「選購一空」）
  - ✅ 使用 NoDriver Element API 替代 JavaScript evaluate
  - **實測狀態：搶票功能完全正常 (2025.10.22)**
- **KKTIX**: ✅ **完全可用** (Lines 302-2141)
  - 登入、Cloudflare 處理、選日期、選區域、驗證碼都已實作
  - 新增功能：訂單確認按鈕、雙重檢查機制、註冊狀態檢查、自動重載機制
  - 實作品質高，函式完整，共 13 個函數
  - **實測狀態：搶票功能完全正常**
- **TicketPlus**: ✅ **完全可用** (Lines 3106-5782)
  - 登入系統 ✅ 已完成
  - 日期選擇 ✅ 已完成
  - 區域選擇和佈局偵測 ✅ 已完成
  - 票券數量設定 ✅ 已完成
  - 同意條款處理 ✅ 已完成
  - 實名卡與其他活動處理 ✅ 已完成
  - 排隊狀態檢查 ✅ 額外新增功能
  - **實測狀態：搶票功能完全正常**

#### 中完成度平台 ⚠️ **部分可用** (30-50%)
- **Cityline**: ⚠️ 部分實作，需要驗證

#### 高完成度平台 ✅ **金級 - NoDriver 專用** (89%)
- **TicketMaster**: ✅ **金級實作** (Lines 3177-3867 共 8 個函式) 🆕⭐⭐⭐
  - **NoDriver 版本現狀**: 8 個核心函式完整實作 ✅
  - **已完成核心搶票流程**:
    - ✅ `nodriver_ticketmaster_main()` - 主控制器（Line 3177）
    - ✅ `nodriver_ticketmaster_date_auto_select()` - 日期自動選擇（Line 3686）🎯
      - 支援 AND/OR 邏輯關鍵字匹配
      - Early Return Pattern 優先匹配
      - date_auto_fallback 條件回退
    - ✅ `nodriver_ticketmaster_area_auto_select()` - 區域自動選擇（Line 3867）🎯
      - 支援 AND/OR 邏輯關鍵字匹配
      - Early Return Pattern 優先匹配
      - area_auto_fallback 條件回退
      - Word boundary 匹配避免誤匹配
    - ✅ `nodriver_ticketmaster_ticket_number_auto_select()` - 票數設定（Line 3549）
    - ✅ `nodriver_ticketmaster_captcha()` - 驗證碼主處理器（Line 3272）
    - ✅ `nodriver_ticketmaster_auto_ocr()` - OCR 自動識別（Line 3336）
    - ✅ `nodriver_ticketmaster_get_area_info()` - 區域資訊解析（Line 3456）
    - ✅ `convert_remote_object()` - RemoteObject 格式轉換（Line 3129）
  - **功能完整度評分**: 80/90 分 → **金級** 🥇
    - 主流程控制: 10/10 ✅
    - 日期選擇: 15/15 ✅
    - 區域選擇: 15/15 ✅
    - 票數設定: 10/10 ✅
    - 驗證碼: 10/10 ✅
    - 訂單送出: 10/10 ✅
    - 錯誤處理: 5/5 ✅
    - 登入功能: 0/5 ⚠️ (不需要，平台無登入)
    - 彈窗處理: 5/5 ✅
  - **特殊說明**: NoDriver 專用平台，Chrome/Selenium 不支援

#### 白金級平台 🏅 **完全可用** (98%)
- **KHAM 寬宏**: 🏅 **白金級實作** (Lines 12064-13080 共 14 個函式，與 Chrome 完全對應) 🆕⭐⭐⭐
  - **Chrome 版本已實作函數**: 14 個核心函數
  - **NoDriver 版本現狀**: 已有 14 個函數，與 Chrome 版本完全對應 ✅
  - **已完成核心搶票流程**:
    - ✅ `nodriver_kham_main()` - 主控制器（Line 13080）
    - ✅ `nodriver_kham_login()` - 帳密登入（Line 12064，含 OCR 驗證碼）
    - ✅ `nodriver_kham_date_auto_select()` - 日期自動選擇（Line 12704）🎯
      - 支援關鍵字匹配與模式選擇回退
      - 支援 kham.com.tw、ticket.com.tw、udnfunlife.com 三個域名
      - 完整的售罄過濾與價格檢查邏輯
    - ✅ `nodriver_kham_area_auto_select()` - 區域自動選擇（Line 12676）
    - ✅ `nodriver_kham_product()` - 產品頁處理（Line 12377）
    - ✅ `nodriver_kham_performance()` - 演出處理（Line 13025）
    - ✅ `nodriver_kham_captcha()` - 驗證碼主處理器（Line 12985）
    - ✅ `nodriver_kham_auto_ocr()` - OCR 自動識別（Line 12909）
    - ✅ `nodriver_kham_keyin_captcha_code()` - 手動輸入驗證碼（Line 12603）
    - ✅ `nodriver_kham_check_realname_dialog()` - 實名制對話框（Line 12251）
    - ✅ `nodriver_kham_allow_not_adjacent_seat()` - 允許非連續座位（Line 12287）
    - ✅ `nodriver_kham_switch_to_auto_seat()` - 切換自動選座（Line 12305）
    - ✅ `nodriver_kham_check_captcha_text_error()` - 驗證碼錯誤檢查（Line 12342）
    - ✅ `nodriver_kham_go_buy_redirect()` - 購買重導向（Line 12216）
  - **功能完整度評分**: 98/100 分 → **白金級** 🏅
    - 主流程控制: 10/10 ✅
    - 日期選擇: 15/15 ✅
    - 區域選擇: 15/15 ✅
    - 票數設定: 10/10 ✅ (在 main 中處理)
    - 驗證碼: 10/10 ✅
    - 同意條款: 3/5 ⚠️ (可能沒有獨立函式)
    - 訂單送出: 10/10 ✅
    - 登入功能: 10/10 ✅
    - 錯誤處理: 5/5 ✅
    - 彈窗處理: 5/5 ✅
    - 頁面重載: 5/5 ✅
  - **完整流程測試**: 登入 → 日期選擇 → 區域選擇 → 驗證碼識別 → 訂單送出 ✅

#### 高完成度平台 ✅ **金級 - 核心完整可用** (90-95%)
- **iBon**: 🥇 **金級實作** (Lines 5806-11530 共 18 個函式，核心流程完整) ⭐⭐⭐
  - **Chrome 版本已實作函數**: 15 個核心函數
  - **NoDriver 版本現狀**: 已有 18 個函數，核心搶票流程 100% 完成 ✅
  - **已完成核心搶票流程**:
    - ✅ `nodriver_ibon_login()` - Cookie 登入處理（98行）
    - ✅ `nodriver_ibon_date_auto_select()` - 日期自動選擇（282行，Shadow DOM 平坦化）🎯
      - **2025.09.30 更新**: 修復程式凍結、UTF-8 編碼、CP950 錯誤
      - **2025.09.30 新增**: 日期格式標準化 (支援 M/D, MM/DD, YY/MM/DD, YYYY/MM/DD)
      - 通過 5 組測試驗證，完全穩定運作
    - ✅ `nodriver_ibon_event_area_auto_select()` - 新版 Event 頁面區域選擇（393行，Angular SPA）🎯⭐
      - **2025.10.03 新增**: 支援新版 ibon Angular SPA Event 頁面格式 (/Event/{id}/{id})
      - 使用 DOMSnapshot 穿透 Shadow DOM 獲取區域資料
      - 關鍵字匹配同時檢查區域名稱與內容（提升準確度）
      - 完整的 5 階段流程：提取 → 過濾 → 匹配 → 選擇 → CDP 點擊
    - ✅ `nodriver_ibon_area_auto_select()` - 舊版 .aspx 頁面區域選擇（457行，DOMSnapshot 平坦化）🎯
      - **2025.09.30 完成**: 使用 DOMSnapshot 穿透 closed Shadow DOM
      - **2025.10.03 改善**: 關鍵字匹配同時檢查區域名稱與內容
      - 支援關鍵字匹配（AND 邏輯）+ 模式選擇回退
      - 實作剩餘票數檢查邏輯
      - 完整的錯誤處理和除錯訊息
    - ✅ `nodriver_ibon_ticket_number_auto_select()` - 自動填寫票數（93行）🎯
      - **2025.10.01 完成**: JavaScript 選擇器自動設定票數
      - **2025.10.03 改善**: 支援新版 EventBuy 頁面格式偵測
      - 支援回退邏輯（目標數量不可用時設為 1）
      - 已設定值自動跳過
    - ✅ `nodriver_ibon_get_captcha_image_from_shadow_dom()` - 驗證碼截圖（204行）🎯⭐
      - **2025.10.01 完成**: 突破 closed Shadow DOM 截圖難題
      - 使用 DOMSnapshot + DOM API + 全頁面截圖 + PIL 裁切
      - 10 種視窗大小測試 100% 成功
      - 支援 verbose 模式控制檔案儲存
    - ✅ `nodriver_ibon_keyin_captcha_code()` - 驗證碼輸入與提交（219行）🎯
      - Alert 自動處理機制
      - 表單自動提交與驗證
    - ✅ `nodriver_ibon_auto_ocr()` - OCR 自動識別（151行）🎯
      - 票數自動重選機制（iBon 錯誤後會清空）
      - OCR 結果過濾與驗證
      - URL 變化檢測驗證成功
    - ✅ `nodriver_ibon_captcha()` - 驗證碼主處理器（93行）🎯
      - 19 次重試循環
      - 失敗計數與刷新邏輯
      - 自動/手動模式切換
    - ✅ `nodriver_ibon_refresh_captcha()` - 驗證碼刷新（34行）
    - ✅ `nodriver_ibon_ticket_agree()` - 同意條款（6行）
    - ✅ `nodriver_ibon_allow_not_adjacent_seat()` - 允許非連續座位（28行）✅
    - ✅ `nodriver_ibon_purchase_button_press()` - 購票按鈕（57行）✅
    - ✅ `nodriver_ibon_check_sold_out()` - 檢查售罄狀態（38行）✅
    - ✅ `nodriver_ibon_verification_question()` - 驗證問題處理（54行）✅
    - ✅ `nodriver_ibon_main()` - 主控制器（209行，核心流程已接通）🎯
      - **2025.10.01 新增**: 結帳頁面偵測與音效播放功能
      - 偵測 UTK0206 結帳頁面並播放成功音效
      - 支援無頭模式自動開啟瀏覽器顯示結帳頁面
  - **完整流程測試通過**: 日期選擇 → 區域選擇 → 票數填寫 → 驗證碼識別 → 成功跳轉 → 結帳提醒 ✅
  - **🎯 2025.10.03 重大改進 (PR #10)**:
    - ✅ **移除所有 emoji 字符**: 修正 Windows cp950 編碼錯誤（✅❌⚠️ → [SUCCESS][ERROR][WARNING]）
    - ✅ **OCR 失敗處理機制**: 3 次連續失敗自動重新整理，5 次總失敗切換手動輸入
    - ✅ **新頁面格式支援**: 實作 `nodriver_ibon_event_area_auto_select` 處理 Angular SPA Event 頁面
    - ✅ **關鍵字匹配改善**: 同時檢查區域名稱與內容，提升匹配準確度
    - ✅ **統一日誌前綴**: 標準化為 [TIXCRAFT OCR], [ibon], [NEW EVENT CDP CLICK]
    - ✅ **Bug 修正**: 修正關鍵字匹配 typo (`row_texttext` → `row_text`)
- **年代售票 (ticket.com.tw)**: ✅ **NoDriver 已完成 (2025-10-09)** - 7/7 函式全部實作
- **寬宏售票 (kham.com.tw)**: ✅ **NoDriver 已完成** - 14/14 函式全部實作 🏅 白金級
- **Urbtix**: 完全未實作
- **HK Ticketing**: 完全未實作
- **FamiTicket**: ✅ **白金級實作 (2025-11-24)** - 9 個函式全部完成

**使用建議**: **七大主流平台（TixCraft Family【拓元/添翼/獨立音樂】、KKTIX、TicketPlus、iBon、KHAM、年代售票、FamiTicket）可直接使用 NoDriver 版本進行搶票**，特別適合需要反偵測的情況

> 📌 **Tixcraft Family 說明**：TixCraft (拓元)、Teamear (添翼)、Indievox (獨立音樂) 三個平台使用完全相同的程式碼，共用所有功能 (2025.10.22 確認)

---

## ⚠️ **第三階段：功能完整性**

### 驗證碼處理優化
#### 驗證碼更換機制 ✅ **已實作**
- **Chrome**: `chrome_tixcraft.py:2005, 2138` ✅ 已完成
- **NoDriver**: `nodriver_tixcraft.py:1718-1846` ✅ 已完成
- **函式**: `tixcraft_reload_captcha()`, `nodriver_tixcraft_refresh_captcha()`
- **狀態**: 已實作點擊驗證碼圖片進行刷新功能

### OCR 處理完整性
#### TixCraft OCR 實作狀態 ✅ **已完成**
- **Chrome**: `chrome_tixcraft.py:2082-2363` ✅ 已完成
- **NoDriver**: `nodriver_tixcraft.py:1731-2058` ✅ **已完成**
- **功能**: Canvas 驗證碼提取、OCR 識別、自動填入與提交、重試機制
- **狀態**: 完整的 OCR 流程已實作，包含錯誤處理和自動重試

#### TixCraft 勾選同意條款 ✅ **已修正**
- **Chrome**: `chrome_tixcraft.py:2153-2337` ✅ 完整實作
- **NoDriver**: `nodriver_tixcraft.py:1545-1609, 279-325` ✅ **已完成修正**
- **問題**: 邏輯判斷錯誤導致勾選函式未執行
- **解決方案**: 移除 Chrome Extension 判斷，NoDriver 模式下強制執行勾選
- **技術**: 使用純 JavaScript 直接操作 DOM，`document.querySelector('#TicketForm_agree')`
- **狀態**: 已通過實際測試驗證，勾選功能正常運作

### 排隊狀態監控
#### HK Ticketing 排隊提醒
- **檔案**: Chrome 版本有基本架構，NoDriver 未實作
- **問題**: 無法判斷排隊狀態變化
- **建議**: 監測頁面元素變化觸發音效

---

## 🔧 **第四階段：使用者體驗**

### 擴充套件整合
#### KKTIX 擴充套件整合 ✅ **已實作**
- **Chrome**: `chrome_tixcraft.py:2888-2930` ✅ 已完成
- **NoDriver**: `nodriver_tixcraft.py:775-913` ✅ 已完成
- **狀態**: 已支援根據瀏覽器類型選擇填表方式
- **邏輯**: Chrome 家族 + 擴充套件啟用時使用擴充套件，否則使用 WebDriver

### 頁面提示優化
#### TixCraft 頁面提示 ✅ **已實作**
- **Chrome**: `chrome_tixcraft.py:1876-1934` ✅ 已完成
- **NoDriver**: 顯示在 console ⚠️ 部分實作
- **功能**: Chrome 版本已實作 `tixcraft_toast()` 在頁面顯示 OCR 答案提示
- **建議**: NoDriver 版本可加入類似頁面提示功能

### 特殊處理改善需求
#### 座位選擇邏輯優化
- **平台**: 影響所有支援座位選擇的平台
- **問題**: 單數票券可能選到不相鄰座位
- **功能**: 檢查剩餘座位數量，避免選擇剩餘座位不足的區域
- **實作狀態**:
  - KKTIX: Chrome ✅, NoDriver ✅ (已有 1-9 席檢查邏輯)
  - TixCraft: Chrome ✅, NoDriver ✅ (已有字體檢查邏輯)

#### OCR 錯誤重試機制 ✅ **已實作**
- **Chrome**: `chrome_tixcraft.py:2082-2363` ✅ 已完成
- **NoDriver**: `nodriver_tixcraft.py:1718-1889` ✅ 已完成
- **功能**: 自動重試機制、驗證碼刷新、答案長度驗證
- **狀態**: 兩版本都有完整的錯誤處理與重試邏輯

---

## 📊 **實作狀態總覽（更新版本優先度）**

| 平台 | Chrome 版本 | NoDriver 版本 | 實作完成度 | 整體狀態 |
|------|:-----------:|:-------------:|:-------------:|:--------:|
| TixCraft 拓元 | ✅ 完整穩定 | ✅ **實測通過** | 🟢 **95%** | 雙版本可用 |
| Teamear 添翼 | ✅ 完整穩定 | ✅ **實測通過** | 🟢 **95%** | **Tixcraft Family 🆕** |
| Indievox 獨立音樂 | ✅ 完整穩定 | ✅ **實測通過** | 🟢 **95%** | **Tixcraft Family 🆕** |
| KKTIX | ✅ 完整穩定 | ✅ **實測通過** | 🟢 **95%** | 雙版本可用 |
| TicketPlus 遠大 | ✅ 基本完整 | ✅ **實測通過** | 🟢 **95%** | 雙版本可用 |
| KHAM 寬宏 | ✅ 完整穩定 | 🏅 **白金級** | 🟢 **98%** | 雙版本完整 |
| iBon | ⚠️ 問題回報 | 🥇 **金級實作** | 🟢 **95%** | **NoDriver 核心完整 ⭐** |
| 年代售票 | ✅ 完整穩定 | ✅ **雙版本完整** | 🟢 **100%** | 雙版本完整 |
| Cityline 買飛 | ✅ 基本完整 | 🥈 銀級實作 | 🟡 **60%** | Chrome 主要 |
| TicketMaster | ❌ 不支援 | ✅ **金級實作** | 🟢 **89%** | NoDriver 專用 🆕 |
| Urbtix 城市 | ✅ 基本完整 | ❌ 未實作 | 🔴 **0%** | Chrome 單一 |
| HK Ticketing 快達票 | ✅ 基本完整 | ❌ 未實作 | 🔴 **0%** | Chrome 單一 |
| FamiTicket 全網 | ✅ 完整穩定 | 🏅 **白金級** | 🟢 **98%** | 雙版本完整 🆕 |

> **策略調整**：NoDriver 版本實際可用度約 **70%**，八大主流平台（**TixCraft Family【拓元/添翼/獨立音樂】**、KKTIX、TicketPlus、iBon、KHAM、年代售票、TicketMaster、FamiTicket）**核心功能完整**
>
> ✅ **實測確認**：NoDriver 版本八大核心平台功能完整，**可直接用於搶票**，是反偵測的有效選擇
>
> 🆕 **2025-11-26 更新**：FamiTicket NoDriver 白金級實作完成（9 個函式，98% 完成度），成為第八個完整支援平台
>
> ℹ️ **TicketPlus OCR 說明**：目前 TicketPlus 活動不需要 OCR 驗證碼，相關功能暫時忽略（Chrome 版本有 4 個 OCR 函式，NoDriver 未實作但不影響使用）
>
> 🎯 **最新完成**：FamiTicket NoDriver 白金級實作 (2025-11-24) - 9/9 函式全部完成 ✅

---

## 🎯 **開發建議**

### 調整後實作順序 🚨 **更新至 2025-11-26**
1. ✅ **核心修復**：OCR 驗證、日期邏輯（已完成）
2. 🔥 **最高優先度 - NoDriver 平台移植**：
   - ✅ **Phase 1**: 寬宏售票移植 **已完成！白金級 (98/100 分)** 🏅
   - ✅ **Phase 2**: 年代售票移植 **已完成！(2025-10-09)** - 7/7 函式全部實作 ✅
   - ✅ **Phase 2**: TicketMaster 移植 **已完成！金級 (89%)** 🥇 - 8/8 函式全部實作 (2025-11-18)
   - ✅ **Phase 3**: FamiTicket 移植 **已完成！白金級 (98%)** 🏅 - 9/9 函式全部實作 (2025-11-24) 🆕
   - **Phase 4**: 補完 Cityline (60% → 85%)
3. ⏸️ **暫時忽略 - TicketPlus OCR**：
   - **現況**: 目前 TicketPlus 活動不需要 OCR 驗證碼
   - **缺失函式** (4個): `auto_ocr()`, `order_ocr()`, `keyin_captcha_code()`, `check_and_renew_captcha()`
   - **策略**: 等實際需求出現後再補充，參考 Chrome Lines 10824-11025
3. 🚨 **緊急修復**：OCR 初始化效能優化
4. 🔧 **穩定性提升**：Chrome 版本全平台測試與優化
5. ⚠️ **程式碼規範化**：遵循 `/docs/coding_templates.md` 標準
6. ✅ **文檔完整性**：更新 platforms.md 函數對照表 (已完成)

### 已完成的改善項目
- ✅ 日期選擇 AND/OR 邏輯篩選支援
- ✅ OCR 驗證碼處理完整實作
- ✅ 驗證碼刷新機制
- ✅ 擴充套件整合邏輯
- ✅ 座位數量檢查邏輯
- ✅ TixCraft 和 KKTIX 雙版本完整支援
- ✅ TixCraft NoDriver 勾選同意條款修正
- ✅ 程式開發規範建立（CLAUDE.md + coding_templates.md）
- ✅ platforms.md 函數行號對照表更新 (2024年最新版本)
- ✅ **2025.10.03 更新**：
  - ✅ 移除所有 emoji 字符，修正 Windows cp950 編碼錯誤
  - ✅ OCR 失敗處理機制（3 次重試 + 5 次手動輸入）
  - ✅ ibon Angular SPA Event 頁面支援
  - ✅ ibon 關鍵字匹配改善（同時檢查區域名稱與內容）
  - ✅ ibon 票數選擇支援新版 EventBuy 頁面格式
  - ✅ PR Template 重構（整合 12-stage 架構與開發規範）
  - ✅ structure.md 與 todo.md 文件更新
- ✅ **2025.10.18 更新**：
  - ✅ KKTIX 票券選擇器雙版本相容（舊版 `div.display-table-row` + 新版 `div.ticket-item`）
  - ✅ KKTIX 搶票完成後暫停機制修復（移除錯誤的 `is_kktix_got_ticket = False` 賦值）
  - ✅ KKTIX 新版 HTML 結構支援（register-intent-new 頁面）
  - ✅ 搶票成功後立即進入暫停，不再重複輸出訊息
- ✅ **2025.10.22 更新**：
  - ✅ Tixcraft Family 平台 NoDriver 完全支援確認（TixCraft、Teamear、Indievox）
  - ✅ Indievox 售罄選項過濾功能（檢測「選購一空」並跳過）
  - ✅ NoDriver Element API 重構 - 使用 `element.attrs` 替代 JavaScript evaluate
  - ✅ 日期選擇 button[data-href] 屬性提取改用 NoDriver API
  - ✅ 票種選擇 disabled/option 檢查改用 NoDriver API
  - ✅ 消除 `'NoneType' object is not callable` 錯誤（element.get_attribute 問題）
  - ✅ 雙平台實測驗證通過（tixcraft.com + indievox.com）
- ✅ **2025.11.11 更新**：
  - ✅ Cityline NoDriver 引擎支援（包含完整購票流程）
- ✅ **2025.11.19 更新**：
  - ✅ TicketMaster NoDriver 完整實作（日期/區域自動選擇、驗證碼 OCR、票數設定）
- ✅ **2025.11.24 更新**：
  - ✅ FamiTicket NoDriver 白金級完整實作（9 個函數）
  - ✅ FamiTicket 登入處理（Cookie 驗證、表單填寫）
  - ✅ FamiTicket 日期/區域選擇（AND/OR 邏輯 + 條件回退）
  - ✅ FamiTicket 驗證問題處理
- ✅ **2025.11.25 更新**：
  - ✅ Ticketmaster 自訂 OCR 模型支援
  - ✅ TixCraft SID Cookie 設定修復
  - ✅ KKTIX fallback alert handling 改善

### 當前技術債務
#### 最高優先度 🔥 **基於 2025.10.06 分析**
- ✅ **NoDriver iBon 平台核心完成**：核心搶票流程 100% 實作完成 ✅（50% → **95%**）
  - **Phase 0: Cookie 登入處理** ✅ **已完成**
    - ✅ 實作 `nodriver_ibon_login()` - Cookie 登入處理（97行）
    - 完整的錯誤處理和登入狀態驗證
  - **Phase 1: 核心購票流程** ✅ **已完成**
    - ✅ 實作 `nodriver_ibon_date_auto_select()` - Shadow DOM 按鈕點擊與日期選擇（282行）
      - 使用 **DOMSnapshot 平坦化策略**穿透 closed Shadow DOM
      - 支援日期關鍵字匹配與 AND/OR 邏輯篩選
      - 完全基於 CDP API，**不依賴 JavaScript 選擇器**
      - 完整的重試機制和錯誤處理
      - **2025.09.30 重大更新**:
        - ✅ 修復程式凍結問題 (移除 NodeId 物件重複列舉)
        - ✅ 修復 UTF-8 編碼死鎖 (條件式啟用 wrapper)
        - ✅ 修復 DOMSnapshot CP950 編碼錯誤 (try-except 保護)
        - ✅ 新增日期格式標準化功能 (normalize_date_keyword)
          - 支援 M/D, MM/DD, YY/MM/DD, YYYY/MM/DD 四種格式
          - 5 組測試全部通過
    - ✅ 實作 `nodriver_ibon_ticket_agree()` - 同意條款（5行）
    - ✅ 實作 `nodriver_ibon_area_auto_select()` - 選擇座位區域（2025.09.30 完成）
    - ✅ 實作 `nodriver_ibon_ticket_number_auto_select()` - 填寫票數（2025.10.01 完成）
    - ✅ 實作 `nodriver_ibon_main()` - 主控制器（核心流程已接通）
      - **2025.10.01 新增**: 結帳頁面偵測與音效播放功能
  - **Phase 2: 驗證碼處理** ✅ **已完成 (2025.10.01)** 🎯⭐
    - ✅ 實作 `nodriver_ibon_get_captcha_image_from_shadow_dom()` - 突破 closed Shadow DOM 截圖
    - ✅ 實作 `nodriver_ibon_captcha()` - 主驗證碼處理器（19次重試循環）
    - ✅ 實作 `nodriver_ibon_auto_ocr()` - OCR 自動識別與重試邏輯
    - ✅ 實作 `nodriver_ibon_keyin_captcha_code()` - 驗證碼輸入與提交
    - ✅ 實作 `nodriver_ibon_refresh_captcha()` - 驗證碼刷新機制
    - **測試驗證**: 10種視窗大小 100% 成功，重試機制正常運作
  - **Phase 3: 成功提醒功能** ✅ **已完成 (2025.10.01)**
    - ✅ 結帳頁面偵測（偵測 UTK0206 頁面）
    - ✅ 音效播放功能（根據 play_sound.order 設定）
    - ✅ 無頭模式自動開啟瀏覽器顯示結帳頁面
    - ✅ 狀態重置機制（離開結帳頁面時）
  - **Phase 4: 輔助功能** (低優先，非核心)
    - ⚠️ `nodriver_ibon_verification_question()` - 驗證問題處理
    - ⚠️ `nodriver_ibon_check_sold_out()` - 檢查售罄狀態
    - ⚠️ `nodriver_ibon_allow_not_adjacent_seat()` - 允許非連續座位
- 🚨 **NoDriver TODO 清理** (共 18 個 TODO 標記)：
  - KKTIX: Lines 1680, 1683 - Extension 相關邏輯待完善
  - TicketPlus: Lines 3065, 3085, 3096, 3101 - 細節優化
  - iBon: Lines 11310-11665 - 註解提示（實際功能已完成）
  - Cityline: Line 12038 - 待確認內容

- 🚨 **未實作平台移植** (共 31 個缺失函式)：
  - **Urbtix 城市售票** (11 個函式) - 香港主要平台
  - **HKTicketing 快達票** (20 個函式) - 香港平台

- ✅ **TixCraft NoDriver**：核心功能已完成，無需緊急修復
- ✅ **KKTIX NoDriver**：核心功能已完成，無需緊急修復
- ✅ **iBon NoDriver**：核心功能已完成，包含完整 OCR 處理
- ✅ **TicketPlus NoDriver**：核心功能已完成，實測通過（目前無 OCR 需求）
- ✅ **KHAM NoDriver**：**完整實作，白金級 (98/100 分)**，14 個函式與 Chrome 版本完全對應
- ✅ **年代售票 NoDriver**：**完整實作 (2025-10-09)**，7 個函式與 Chrome 版本完全對應，雙版本完整
- ✅ **FamiTicket NoDriver**：🆕 **完整實作，白金級 (98%)** (2025-11-24)，9 個函式全部實作

- ⏸️ **TicketPlus OCR 暫時忽略** - **現況無需求**
  - **說明**: 目前 TicketPlus 活動不使用 OCR 驗證碼，NoDriver 版本缺少的 4 個 OCR 函式暫不影響使用
  - **Chrome 版本有的函式** (4個): `ticketplus_order_ocr()`, `auto_ocr()`, `check_and_renew_captcha()`, `keyin_captcha_code()`
  - **NoDriver 現狀**: 未實作，但不影響當前搶票功能
  - **策略**: 等實際需求出現後再補充
  - **參考實作**: Chrome Lines 10824-11025, TixCraft NoDriver OCR Lines 2821-2949

#### 高優先度
- 🚨 **OCR 效能優化**：初始化時間過長問題
- 📋 **程式碼標準化**：遵循統一的函數命名和錯誤處理格式
- 🔧 **Chrome 版本穩定性**：全平台搶票流程測試

#### 中優先度
- ✅ **文檔同步**：更新 platforms.md 行號對照 (已完成)
- 🧹 **程式碼重構**：減少重複邏輯，提高可維護性
- ⚠️ **錯誤處理統一**：標準化異常處理機制
- 🔄 **NoDriver OCR 優化**：將 Selenium 風格實作改為原生 NoDriver 方法

#### 程式碼品質改進（Code Review 建議 - PR #10）
> 來源：2025.10.03 Code Review，後續改進建議

- ⏳ **改善錯誤處理**：
  - 避免使用 bare `except:`，改為 `except Exception as e:`
  - 範例位置：nodriver_tixcraft.py:3007-3011 (OCR alert 處理)
  - 影響範圍：全檔案中的異常處理區塊

- ⏳ **定義常數取代 Magic Numbers**：
  - `await asyncio.sleep(2.5)` → `CAPTCHA_REFRESH_WAIT = 2.5`
  - `await tab.sleep(1.5)` → `ANGULAR_APP_LOAD_WAIT = 1.5`
  - `random.uniform(0.8, 1.2)` → `RANDOM_WAIT_MIN/MAX`
  - 範例位置：nodriver_tixcraft.py:3012, 9564-9565

- ⏳ **清理註解掉的程式碼**：
  - 移除或啟用大量註解掉的 debug 訊息
  - 或改用 `ultra_verbose` 等級控制
  - 影響範圍：nodriver_ibon_event_area_auto_select 等函式

- 🔄 **重構共用邏輯**：
  - `nodriver_ibon_event_area_auto_select` 與 `nodriver_ibon_area_auto_select` 約 80% 相似
  - 建議：提取共用的 Phase 2-4 邏輯為獨立函式
  - 差異：Phase 1 (數據提取方法) 與 Phase 5 (點擊方法相同)
  - 優先度：低（功能正常運作，重構風險較高）

#### 低優先度（暫緩）
- 🧪 **單元測試框架**：建立自動化測試
- 🚀 **CI/CD 流程**：自動化部署與測試
- 🔄 **NoDriver 版本**：函數命名與 Chrome 版本對齊

---

## 🔮 **將來技術方向**


### 其他前瞻技術
- **機器學習 OCR**: 使用 TensorFlow/PyTorch 訓練專屬驗證碼模型
- **行為模擬**: 更精確的人類操作模擬（滑鼠軌跡、打字速度）
- **分散式架構**: 多節點搶票降低單點失敗風險