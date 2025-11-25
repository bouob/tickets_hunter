# 功能規格說明: Ticketmaster.com NoDriver 平台遷移

**功能分支**: `007-ticketmaster-nodriver-migration`
**建立日期**: 2025-11-15
**狀態**: 草稿
**輸入**: 用戶描述: "實作ticketmaster.com 的功能 由於這個是Tixcraft 家族 所以有些程式是互相共用的 修改時必須特別小心 現在在程式中 有一些TODO 是保留給 ticketmaster的 在chrome版本中是可以運作的 請參考chrome版本的邏輯轉移到nodriver平台並且使用nodriver CDP/API技術  chrome UC版本的原始邏輯 可以參考 或是讀取docs過濾關鍵資料 如果卡關可以直接搜尋 API guide 連結到官方手冊查找資訊"

## 用戶情境與測試 *(必填)*

### User Story 1 - 自動選擇演出日期 (Priority: P1)

使用者啟用日期自動選擇功能後,系統能在 Ticketmaster.com 的活動頁面自動根據設定的關鍵字識別並點選符合條件的演出場次。

**優先級說明**: 日期選擇是搶票流程的第一個關鍵環節,沒有此功能則無法進入後續的區域選擇和票務處理階段,屬於核心 MVP 功能。

**獨立測試方式**: 可透過設定特定日期關鍵字(如"2025-12-25"),訪問 Ticketmaster.com 的藝人活動頁面(如 `/artist/{artist_name}`),系統應能自動找到並點擊符合條件的演出日期,帶來立即可見的自動化價值。

**驗收情境**:

1. **假設** 使用者在 settings.json 中啟用日期自動選擇並設定日期關鍵字為"2025-12-25",**當** 系統載入包含該日期演出的 Ticketmaster 活動頁面,**則** 系統應自動點擊該日期的 "See Tickets" 連結並導航至座位選擇頁面
2. **假設** 使用者設定關鍵字為"聖誕",**當** 頁面包含"Christmas Special"等包含關鍵字的演出名稱,**則** 系統應成功匹配並選擇該場次
3. **假設** 使用者設定的關鍵字匹配到多個場次,**當** auto_select_mode 為"from top to bottom",**則** 系統應選擇第一個符合的場次
4. **假設** 使用者啟用"跳過已售罄場次"選項,**當** 某場次顯示"Sold out"或"No tickets available",**則** 系統應跳過該場次並選擇下一個符合條件的場次

---

### User Story 2 - 自動選擇座位區域 (Priority: P1)

使用者啟用區域自動選擇功能後,系統能在座位選擇頁面根據區域關鍵字自動識別並點選符合條件的座位區塊。

**優先級說明**: 區域選擇直接影響是否能搶到理想座位,與日期選擇同等重要,缺少此功能將導致自動化流程中斷,需要手動介入。

**獨立測試方式**: 可透過設定區域關鍵字(如"VIP"、"搖滾區"),訪問 Ticketmaster 的 `/ticket/area/` 頁面,系統應能解析頁面中的 zone_info JSON 資料,自動選擇符合條件且可用(areaStatus != "UNAVAILABLE")的座位區域。

**驗收情境**:

1. **假設** 使用者設定區域關鍵字為"VIP",**當** 系統載入座位選擇頁面且存在狀態為可用的 VIP 區域,**則** 系統應自動選擇該區域
2. **假設** 使用者設定多組區域關鍵字(如["VIP", "搖滾區", "一般票"]),**當** VIP 區域不可用,**則** 系統應自動嘗試下一個關鍵字組合
3. **假設** 使用者設定排除關鍵字(如"受限視野"),**當** 某區域描述包含排除關鍵字,**則** 系統應忽略該區域即使其他條件符合
4. **假設** 座位選擇頁面使用圖形化座位圖(mapSelectArea),**當** 系統需要解析 zone_info JSON 資料,**則** 系統應能從頁面 HTML 中正確提取並解析 JavaScript 變數
5. **假設** 座位選擇頁面使用表格式價格清單(ticketPriceList),**當** 系統偵測到該表格,**則** 系統應能處理並選擇符合條件的座位類型

---

### User Story 3 - 票數設定與促銷碼填寫 (Priority: P2)

使用者設定購買票數後,系統能在票務頁面自動設定正確的票數,並在需要時填寫促銷碼。

**優先級說明**: 雖然重要,但相對於日期和區域選擇,票數設定較為簡單且失敗影響較小,可作為第二優先級實作。

**獨立測試方式**: 可透過設定 ticket_number 為特定數字(如 2 張),訪問 Ticketmaster 的票務頁面,系統應能找到 ticketPriceList 中的 select 元素並自動設定票數,並點擊 autoMode 按鈕繼續流程。

**驗收情境**:

1. **假設** 使用者設定購買 2 張票,**當** 系統進入票務頁面(包含 ticketPriceList),**則** 系統應自動在票數下拉選單選擇"2"並點擊繼續按鈕
2. **假設** 頁面顯示載入中狀態(loadingmap 元素存在),**當** 系統偵測到此狀態,**則** 系統應等待載入完成後才進行票數設定
3. **假設** 使用者設定促銷碼,**當** 頁面存在 promoBox 輸入框,**則** 系統應自動填寫促銷碼
4. **假設** 促銷碼填寫失敗,**當** 系統記錄失敗的促銷碼,**則** 系統應避免重複嘗試相同的失敗碼

---

### User Story 4 - 驗證碼自動處理 (Priority: P3)

使用者啟用驗證碼自動辨識後,系統能在驗證碼頁面自動辨識圖形驗證碼或處理其他驗證機制。

**優先級說明**: 驗證碼處理屬於輔助功能,且可能需要更複雜的 OCR 整合,可作為後期優化項目。基礎功能可先實作勾選同意條款的自動化。

**獨立測試方式**: 可透過訪問 `/ticket/check-captcha/` 頁面,系統應能自動勾選 TicketForm_agree 條款勾選框,並在啟用 OCR 的情況下嘗試辨識驗證碼。

**驗收情境**:

1. **假設** 系統進入驗證碼頁面,**當** 頁面存在 TicketForm_agree 勾選框,**則** 系統應自動勾選該條款
2. **假設** 使用者啟用 OCR 驗證碼辨識,**當** 頁面包含圖形驗證碼,**則** 系統應嘗試辨識並填寫驗證碼
3. **假設** 使用者未啟用 OCR,**當** 遇到驗證碼,**則** 系統應聚焦於輸入框等待手動輸入
4. **假設** 驗證碼辨識失敗,**當** 系統偵測到需要重試,**則** 系統應記錄失敗的答案避免重複嘗試

---

### 邊界情境

- 當 Ticketmaster.com 更新頁面結構或選擇器時,系統應提供清晰的錯誤訊息指出元素定位失敗,避免靜默失敗
- 系統如何處理網路延遲或頁面載入緩慢的情況?(應實作適當的等待機制和超時處理)
- 當使用者同時設定多個平台(Tixcraft 家族共享代碼),修改如何確保不影響其他平台的功能?(應通過條件判斷 domain_name 來區分平台特定邏輯)
- 當關鍵字匹配失敗且未啟用 fallback 機制時,系統應如何通知使用者?(應記錄詳細的匹配失敗日誌並考慮自動重新整理頁面)
- 當頁面同時存在多種座位選擇方式(圖形座位圖和價格表)時,系統優先處理哪一種?(應優先嘗試 ticketPriceList,失敗後回退到 zone_info 解析)

## 需求 *(必填)*

### 功能性需求

- **FR-001**: 系統必須能在 Ticketmaster.com 的藝人活動頁面(/artist/)自動識別並點選符合日期關鍵字的演出場次
- **FR-002**: 系統必須能解析頁面中的演出列表(CSS selector: '#list-view > div > div.event-listing > div.accordion-wrapper > div'),並過濾包含"See Tickets"文字的可用場次
- **FR-003**: 系統必須支援跳過包含售罄關鍵字(如"Sold out", "No tickets available")的場次,此行為由設定檔控制
- **FR-004**: 系統必須能在座位選擇頁面(/ticket/area/)解析 zone_info JavaScript 變數,該變數包含在 #mapSelectArea 元素的 innerHTML 中
- **FR-005**: 系統必須能根據區域關鍵字和 areaStatus 狀態(排除 "UNAVAILABLE")篩選可用的座位區域
- **FR-006**: 系統必須支援多組區域關鍵字的回退機制,當第一組關鍵字匹配失敗時自動嘗試下一組
- **FR-007**: 系統必須能在票務頁面偵測並等待 #loadingmap 元素消失後才進行票數設定
- **FR-008**: 系統必須能在 #ticketPriceList 表格中找到 select 元素並設定使用者指定的票數
- **FR-009**: 系統必須在成功設定票數後自動點擊 #autoMode 按鈕繼續流程
- **FR-010**: 系統必須能在 promoBox 輸入框填寫促銷碼,並記錄失敗的促銷碼避免重複嘗試
- **FR-011**: 系統必須能在驗證碼頁面(/ticket/check-captcha/)自動勾選 #TicketForm_agree 條款勾選框
- **FR-012**: 系統必須使用 NoDriver 的 CDP (Chrome DevTools Protocol) API 而非 Selenium API 來實作所有元素互動
- **FR-013**: 系統必須通過檢查 URL 中的 domain_name 來區分 Ticketmaster.com 和其他 Tixcraft 家族平台,確保平台特定邏輯不互相影響
- **FR-014**: 系統必須在偵測到結帳頁面(/ticket/checkout)時記錄搶票成功的耗時並觸發成功通知
- **FR-015**: 系統必須提供詳細的除錯日誌,包含元素定位失敗、關鍵字匹配結果、選擇決策等資訊,日誌輸出由 config["advanced"]["verbose"] 控制

### 主要實體 *(若功能涉及資料)*

- **演出場次 (Event Date)**: 代表單一演出的日期與時間資訊,包含場次名稱、日期文字、可用狀態("See Tickets" 或 "Sold out"),對應頁面中的 accordion-wrapper > div 元素
- **座位區域 (Zone)**: 代表可供選擇的座位區塊,包含 zone ID、groupName(區域名稱)、description(說明)、areaStatus(可用狀態)、price(票價資訊),資料來源為頁面 JavaScript 中的 zone 變數
- **設定檔項目 (Configuration)**: 控制自動化行為的參數,包含日期關鍵字、區域關鍵字、排除關鍵字、選擇模式(from top/random)、票數、回退策略啟用狀態等
- **失敗記錄 (Failure List)**: 記錄已嘗試但失敗的項目(如促銷碼、驗證碼答案),用於避免重複嘗試相同失敗的操作

## 成功標準 *(必填)*

### 可衡量成果

- **SC-001**: 系統能在 90% 的測試案例中成功識別並點選符合日期關鍵字的演出場次(基於包含至少 10 個不同演出的測試資料集)
- **SC-002**: 系統能在 95% 的情況下正確解析並提取頁面中的 zone_info JSON 資料,即使 HTML 結構包含換行符和額外逗號
- **SC-003**: 系統從進入活動頁面到完成票數設定的整體流程耗時不超過原 Chrome Driver 版本的 110%(NoDriver 版本允許略微的效能差異以換取更好的反偵測能力)
- **SC-004**: 系統在處理 Tixcraft 家族其他平台(如 tixcraft.com, teamear.tixcraft.com)時不會觸發 Ticketmaster 特定邏輯,跨平台隔離度達 100%
- **SC-005**: 系統在啟用 verbose 模式時,能為每個關鍵決策點(日期匹配、區域選擇、票數設定)輸出可理解的日誌資訊,協助使用者除錯成功率達 85% 以上

## 假設與限制 *(必填)*

### 假設

- 假設 Ticketmaster.com 的頁面結構保持相對穩定,關鍵選擇器(如 #list-view, #mapSelectArea, #ticketPriceList)在短期內不會大幅變更
- 假設 NoDriver 套件能夠穩定運行且 CDP API 完整性足以實作所有必要的元素互動(點擊、文字輸入、屬性讀取)
- 假設使用者已經完成 Ticketmaster.com 的身份認證(登入),本功能聚焦於已登入後的搶票流程自動化
- 假設 Chrome Driver 版本的實作邏輯已經過實際測試驗證,可作為可靠的遷移參考基準
- 假設 zone_info 的 JSON 格式保持一致,包含 areaStatus、groupName、description、price 等標準欄位

### 限制

- 本功能不涵蓋 Ticketmaster.com 的自動登入功能,使用者需預先手動登入或透過其他機制注入登入狀態
- NoDriver 版本的實作必須與現有 Tixcraft 家族平台共享部分程式碼,因此需要特別注意條件判斷避免相互干擾,可能限制程式碼結構的彈性
- 驗證碼自動辨識的準確率受限於現有 OCR 引擎(ddddocr)的能力,可能無法達到 100% 成功率
- 由於 Ticketmaster.com 可能實施機器人偵測機制,即使使用 NoDriver 的反偵測功能,仍可能遭遇不可預測的封鎖或驗證挑戰
- 座位圖形化選擇(clickable SVG map)的複雜互動若需要精確座標點擊,可能需要額外的視覺分析,本版本優先處理基於 zone_info 的選擇邏輯

## 範圍界定 *(必填)*

### 包含在此功能中

- 從 Chrome Driver 版本遷移以下核心函數至 NoDriver:
  - `ticketmaster_date_auto_select()` - 日期自動選擇
  - `get_ticketmaster_target_area()` - 區域匹配邏輯
  - `ticketmaster_area_auto_select()` - 區域自動選擇
  - `ticketmaster_parse_zone_info()` - zone_info 解析
  - `ticketmaster_get_ticketPriceList()` - 票價表取得
  - `ticketmaster_assign_ticket_number()` - 票數設定
  - `ticketmaster_promo()` - 促銷碼填寫
  - `ticketmaster_captcha()` - 驗證碼頁面處理
- 在主流程函數(nodriver_tixcraft_main)中整合上述功能,對應 URL 路徑:
  - `/artist/` - 觸發日期選擇
  - `/ticket/area/` - 觸發區域選擇
  - `/ticket/check-captcha/` - 觸發驗證碼處理
- 實作適當的錯誤處理和日誌記錄機制
- 確保與現有 Tixcraft 家族平台的程式碼隔離(透過 domain_name 判斷)

### 明確排除的項目

- Ticketmaster.com 的自動登入功能(假設使用者已登入)
- 完整的 OCR 驗證碼辨識引擎重構(沿用現有 tixcraft_auto_ocr 機制)
- 圖形化座位圖的視覺化座標點擊(優先使用 zone_info 資料結構選擇)
- 排隊與付款頁面的深度自動化(主要聚焦於選票階段)
- 效能優化與程式碼重構(專注於功能遷移,保持與 Chrome 版本邏輯一致)
- 跨瀏覽器相容性(專注於 Chrome/Chromium via NoDriver)

## 相依性 *(必填)*

### 技術相依性

- **NoDriver 套件**: 提供 CDP-based 的瀏覽器自動化能力,版本需支援 async/await 語法
- **Python 3.8+**: 支援 async/await 和 typing 提示
- **ddddocr**: 驗證碼辨識引擎(若啟用 OCR 功能)
- **現有 util 模組**: 提供關鍵字匹配(get_matched_blocks_by_keyword)、格式化(format_keyword_string)、選擇邏輯(get_target_item_from_matched_list)等共用工具函數

### 功能相依性

- 依賴現有的 nodriver_tixcraft_main() 主流程架構,需在該函數中新增 Ticketmaster 特定的 URL 路徑判斷
- 依賴 settings.json 設定檔結構,包含:
  - `date_auto_select["enable"]` 和 `date_auto_select["date_keyword"]`
  - `area_auto_select["enable"]` 和 `area_auto_select["area_keyword"]`
  - `area_auto_select["mode"]` (選擇策略)
  - `ticket_number` (購票張數)
  - `tixcraft["pass_date_is_sold_out"]` (跳過售罄場次)
  - `ocr_captcha["enable"]` (OCR 啟用狀態)
- 依賴現有的 Captcha_Browser 和 ocr 物件(用於驗證碼處理)

### 資料相依性

- 需存取和解析 Ticketmaster.com 頁面中的特定 DOM 元素和 JavaScript 變數
- 依賴 zone_info JSON 資料的結構穩定性(含 areaStatus, groupName, description, price 欄位)

## 風險與緩解措施 *(必填)*

### 已識別風險

**風險 1: 頁面結構變更**
**影響**: 高 | **機率**: 中
**描述**: Ticketmaster.com 可能更新頁面 HTML 結構或選擇器,導致元素定位失敗
**緩解措施**: 實作詳細的錯誤日誌記錄,在元素定位失敗時輸出清晰訊息;採用多重選擇器回退策略;建立定期的自動化測試流程監控頁面變更

**風險 2: Tixcraft 家族共享代碼污染**
**影響**: 高 | **機率**: 中
**描述**: Ticketmaster 特定邏輯可能不慎影響其他 Tixcraft 家族平台(如 tixcraft.com, teamear.tixcraft.com)
**緩解措施**: 嚴格使用 domain_name 條件判斷;為所有 Ticketmaster 特定函數加上明確的 domain 檢查;建立跨平台迴歸測試確保隔離性

**風險 3: NoDriver API 限制**
**影響**: 中 | **機率**: 低
**描述**: NoDriver 的 CDP API 可能無法完全實現 Selenium 原有的某些元素互動功能
**緩解措施**: 優先參考專案現有的 NoDriver 實作範例(如 nodriver_tixcraft_area_auto_select);查閱 NoDriver 官方文件和 CDP Protocol 規範;必要時實作 CDP 原生指令的直接調用

**風險 4: 機器人偵測**
**影響**: 中 | **機率**: 中
**描述**: Ticketmaster.com 可能偵測並封鎖自動化行為,即使使用 NoDriver 的反偵測功能
**緩解措施**: 遵循專案既有的反偵測最佳實踐(隨機延遲、模擬人類行為);使用 NoDriver 的內建反偵測機制;提供手動介入選項作為回退方案

**風險 5: JSON 解析失敗**
**影響**: 中 | **機率**: 低
**描述**: 從 HTML 提取的 zone_info JavaScript 變數可能包含格式問題(多餘逗號、換行符)導致 JSON 解析失敗
**緩解措施**: 實作健壯的字串清理邏輯(如移除尾部逗號和換行符);使用 try-except 包裹 JSON 解析並記錄原始字串;提供回退到 ticketPriceList 表格的替代路徑

## 開放性問題

1. 是否需要支援 Ticketmaster.com 的多語言版本(如英語、中文界面),或僅針對特定語言優化關鍵字匹配?
2. 當同時存在圖形座位圖和價格表兩種選擇方式時,是否需要提供設定選項讓使用者選擇優先使用哪一種?
3. 是否需要為 Ticketmaster 實作專屬的錯誤分類機制(如區分網路錯誤、元素定位錯誤、售罄錯誤),還是沿用現有的通用錯誤處理?
