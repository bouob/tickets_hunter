# 功能規格說明: Cityline Platform NoDriver Migration

**功能分支**: `006-cityline-nodriver-migration`
**建立日期**: 2025-11-10
**狀態**: 草稿
**輸入**: 用戶描述: "cityline 平台從Chrome UC 遷移到 nodriver 有一些nodriver參考文件可以查詢 docs/"

## Clarifications

### Session 2025-11-10

- Q: Cityline 是否需要實作 date_auto_fallback 條件回退機制? → A: 實作 date_auto_fallback 功能,保持跨平台一致性 (預設 false)
- Q: Cityline 是否需要實作 area_auto_fallback 條件回退機制? → A: 實作 area_auto_fallback 功能,保持跨平台一致性 (預設 false)
- Q: 當 date_auto_fallback=false 且關鍵字匹配失敗時,Cityline 是否需要支援自動重新整理頁面? → A: 嚴格模式仍允許自動刷新,重新嘗試匹配
- Q: Cityline 的 date_auto_fallback 和 area_auto_fallback 設定應該放在 settings.json 的哪個位置? → A: 直接取用現有設定
- Q: Cityline NoDriver 實作的條件回退機制日誌訊息應該使用哪種格式? → A: 使用 [DATE FALLBACK] / [AREA FALLBACK] 前綴 (與 TixCraft 一致)

## 用戶情境與測試 *(必填)*

### User Story 1 - NoDriver 完整票務流程實作 (Priority: P1)

使用者希望在 Cityline 平台上使用 NoDriver 技術完成完整的搶票流程,包含登入、日期選擇、區域選擇、數量選擇及提交,以獲得更好的反偵測能力和穩定性。

**優先級說明**: 這是核心價值所在 - 完整實作所有關鍵步驟才能讓使用者真正使用 NoDriver 進行搶票。NoDriver 比 Chrome UC 有更好的反偵測能力,是專案的技術架構優先選擇。

**獨立測試方式**: 可透過配置 `settings.json` 中的 `webdriver_type: "nodriver"` 並指定 Cityline 測試活動 URL,完整測試從登入到座位選擇的完整流程,並驗證所有步驟都能正確執行。

**驗收情境**:

1. **假設** 使用者在 `settings.json` 中設定 `webdriver_type: "nodriver"`,**當** 執行 Cityline 搶票腳本,**則** 系統使用 NoDriver 啟動瀏覽器並成功進入活動頁面
2. **假設** 使用者已設定 Cityline 帳號,**當** 腳本偵測到登入頁面,**則** 系統自動填入帳號並勾選同意條款(排除記得密碼選項)
3. **假設** 使用者設定了日期關鍵字,**當** 進入日期選擇頁面,**則** 系統根據關鍵字與選擇模式自動選擇符合的日期並點擊購買按鈕
4. **假設** 使用者設定了區域關鍵字,**當** 進入價格/座位區域選擇頁面,**則** 系統根據關鍵字匹配可用區域並勾選對應的 radio 按鈕
5. **假設** 使用者設定了購票數量,**當** 進入數量選擇頁面,**則** 系統自動選擇指定的票數並點擊下一步按鈕
6. **假設** 流程中出現廣告或彈窗,**當** 腳本偵測到這些干擾元素,**則** 系統自動清除或關閉干擾元素
7. **假設** Cityline 自動開啟第二個分頁,**當** 腳本偵測到多分頁情況,**則** 系統關閉舊分頁並切換到正確的活動分頁

---

### User Story 2 - 關鍵字匹配與條件回退策略 (Priority: P2)

使用者希望系統能夠根據設定的關鍵字智能匹配日期和區域,並在無法匹配時根據 `date_auto_fallback` 和 `area_auto_fallback` 設定決定是否執行回退策略(使用 `auto_select_mode` 自動選擇)或等待手動介入(嚴格模式)。

**優先級說明**: 關鍵字匹配與條件回退機制是搶票系統的智能核心,能大幅提升成功率。條件回退功能(Feature 003, v1.2)讓使用者可在「只要能買到票就好」和「避免誤購不想要的場次/區域」兩種策略間靈活選擇。

**獨立測試方式**: 透過設定不同的日期/區域關鍵字(包含空關鍵字、單一關鍵字、多關鍵字組合),並搭配 `date_auto_fallback` / `area_auto_fallback` 開關與不同的 `auto_select_mode`,驗證系統在各種情境下都能正確選擇目標或執行回退/嚴格模式邏輯。

**驗收情境**:

1. **假設** 使用者設定日期關鍵字為"週六",**當** 系統在日期列表中找到多個符合的選項,**則** 根據 `auto_select_mode` 選擇第一個/最後一個/隨機一個
2. **假設** 使用者設定區域關鍵字為"搖滾區",**當** 系統在區域列表中找到符合且未售罄的選項,**則** 自動勾選該區域的 radio 按鈕
3. **假設** 使用者未設定任何關鍵字(空字串),**當** 進入選擇頁面,**則** 系統將所有可用選項視為匹配,並根據 `auto_select_mode` 選擇
4. **假設** 使用者設定的日期關鍵字無法匹配任何選項且 `date_auto_fallback=true`,**當** 系統完成關鍵字匹配,**則** 回退到 `auto_select_mode` 從所有可用日期中選擇,並記錄 `[DATE FALLBACK]` 日誌
5. **假設** 使用者設定的日期關鍵字無法匹配任何選項且 `date_auto_fallback=false`,**當** 系統完成關鍵字匹配,**則** 記錄 `[DATE FALLBACK] fallback is disabled` 日誌,並根據 `auto_reload_coming_soon_page` 設定決定是否自動重新整理頁面或等待手動介入
6. **假設** 使用者設定的區域關鍵字無法匹配任何選項且 `area_auto_fallback=true`,**當** 系統完成關鍵字匹配,**則** 回退到 `auto_select_mode` 從所有可用區域中選擇,並記錄 `[AREA FALLBACK]` 日誌
7. **假設** 使用者設定的區域關鍵字無法匹配任何選項且 `area_auto_fallback=false`,**當** 系統完成關鍵字匹配,**則** 返回失敗,不選擇任何區域,等待手動介入,並記錄 `[AREA FALLBACK] fallback is disabled` 日誌

---

### User Story 3 - NoDriver CDP 優先實作策略 (Priority: P2)

開發者在實作 Cityline NoDriver 功能時,優先使用 NoDriver 原生 CDP 方法進行 DOM 操作,僅在簡單操作或 CDP 過於複雜時才使用 JavaScript,以確保更好的穩定性、效能和反偵測能力。

**優先級說明**: 雖然對使用者不可見,但這是技術實作的品質保證。遵循 NoDriver First 原則能確保長期維護性和穩定性。

**獨立測試方式**: Code Review 時檢查 Cityline NoDriver 實作中是否優先使用 `await tab.query_selector()`、`await tab.send(cdp.*)`等 NoDriver 原生方法,而非過度依賴 `await tab.evaluate(JavaScript)`。

**驗收情境**:

1. **假設** 需要查詢 Shadow DOM 元素,**當** 開發者實作元素定位,**則** 使用 `cdp.dom.perform_search()` 搭配 `include_user_agent_shadow_dom=True` 而非 JavaScript 查詢
2. **假設** 需要點擊按鈕或輸入文字,**當** 開發者實作互動邏輯,**則** 優先使用 `await element.click()`、`await element.send_keys()` 等 NoDriver 原生方法
3. **假設** 需要執行簡單的 DOM 查詢(檢查元素存在、讀取屬性),**當** CDP 實作需要超過 50 行而 JavaScript 僅需 10 行內,**則** 允許使用 JavaScript 作為合理例外

---

### 邊界情境

- 當 Cityline 平台偵測到自動化行為並顯示 reCAPTCHA 驗證時會怎樣?
  - 系統應在點擊購買按鈕後等待 6 秒,給予驗證視窗足夠的載入時間,並保持腳本運行不中斷,讓使用者有機會手動完成驗證

- 當使用者設定的關鍵字過於嚴格導致無任何匹配時會怎樣?
  - **日期選擇**: 若 `date_auto_fallback=true`,系統回退到 `auto_select_mode` 自動選擇任意可用日期;若 `date_auto_fallback=false` (預設,嚴格模式),系統根據 `auto_reload_coming_soon_page` 設定決定是否自動重新整理頁面,或保持在當前頁面等待手動介入
  - **區域選擇**: 若 `area_auto_fallback=true`,系統回退到 `auto_select_mode` 自動選擇任意可用區域;若 `area_auto_fallback=false` (預設,嚴格模式),系統返回失敗,不選擇任何區域,等待手動介入以避免誤購不想要的區域

- 當 Cityline 自動彈出多個分頁或廣告視窗時會怎樣?
  - 系統應偵測並關閉非主要活動頁面的分頁,並清除頁面上的廣告元素,確保腳本專注於正確的活動流程

- 當區域選項中包含"售罄"狀態時會怎樣?
  - 系統應透過檢查 `span.price-limited > span[data-i18n*="soldout"]` 等標記,過濾掉已售罄的選項,僅從可用選項中進行匹配與選擇

- 當使用者在 NoDriver 和 Chrome UC 之間切換時會怎樣?
  - 系統應根據 `settings.json` 中的 `webdriver_type` 設定,自動選擇對應的平台入口函數(`nodriver_cityline_main` 或 `cityline_main`),無需使用者修改程式碼

## 需求 *(必填)*

### 功能性需求

- **FR-001**: 系統必須支援透過 `settings.json` 中的 `webdriver_type: "nodriver"` 設定,啟用 Cityline 平台的 NoDriver 實作
- **FR-002**: 系統必須實作 NoDriver 版本的 Cityline 登入功能,支援帳號自動填入、同意條款勾選(排除記得密碼選項)
- **FR-003**: 系統必須實作 NoDriver 版本的日期選擇功能,支援關鍵字匹配、`auto_select_mode` 選擇策略、條件回退機制(`date_auto_fallback`)及購買按鈕點擊
- **FR-003a**: 系統必須支援 `date_auto_fallback` 條件回退機制(Feature 003):當日期關鍵字無法匹配且 `date_auto_fallback=true` 時,回退到 `auto_select_mode` 自動選擇;當 `date_auto_fallback=false` (預設)時,根據 `auto_reload_coming_soon_page` 設定決定是否自動重新整理或等待手動介入
- **FR-003b**: 系統必須在日期選擇的條件回退流程中記錄結構化日誌,使用 `[DATE FALLBACK]` 前綴,包含 `date_auto_fallback` 狀態與選擇策略資訊
- **FR-004**: 系統必須實作 NoDriver 版本的區域(價格)選擇功能,支援關鍵字匹配、售罄過濾、條件回退機制(`area_auto_fallback`)、radio 按鈕勾選
- **FR-004a**: 系統必須支援 `area_auto_fallback` 條件回退機制(Feature 003):當區域關鍵字無法匹配且 `area_auto_fallback=true` 時,回退到 `auto_select_mode` 自動選擇;當 `area_auto_fallback=false` (預設)時,返回失敗並等待手動介入,避免誤購不想要的區域
- **FR-004b**: 系統必須在區域選擇的條件回退流程中記錄結構化日誌,使用 `[AREA FALLBACK]` 前綴,包含 `area_auto_fallback` 狀態與選擇策略資訊
- **FR-005**: 系統必須實作 NoDriver 版本的票數選擇功能,支援透過 `select.select-num` 選擇器自動填入購票數量
- **FR-006**: 系統必須實作 NoDriver 版本的下一步按鈕點擊功能,能夠在區域與票數選擇完成後自動提交
- **FR-007**: 系統必須支援自動重試進入活動頁面功能,透過呼叫 `goEvent()` JavaScript 函數或頁面重新整理實現
- **FR-008**: 系統必須支援自動清除 Cityline 廣告與彈窗,避免干擾搶票流程
- **FR-009**: 系統必須支援自動處理 Cityline 多分頁情況,關閉舊分頁並切換至正確的活動分頁
- **FR-010**: 系統必須支援 Cookie 接受按鈕的自動點擊(若 Cityline 顯示 Cookie 同意視窗)
- **FR-011**: 系統必須在日期選擇失敗時,根據 `auto_reload_coming_soon_page` 設定決定是否自動重新整理頁面
- **FR-012**: 系統必須在點擊購買按鈕後等待 6 秒,以便 reCAPTCHA 驗證視窗有足夠時間載入
- **FR-013**: 系統必須支援音效播放功能,當成功進入座位選擇頁面時,根據 `play_sound.ticket` 設定播放提示音
- **FR-014**: 系統必須在區域選擇時過濾掉已售罄的選項(透過 `data-i18n="soldout"` 屬性檢查)
- **FR-015**: 系統必須遵循專案的 NoDriver First 原則,優先使用 NoDriver 原生 CDP 方法而非 JavaScript
- **FR-016**: 系統必須保持與 Chrome UC 版本的功能對等性,確保遷移後不損失任何既有功能
- **FR-017**: 系統必須支援 `auto_reload_page_interval` 設定,在自動重新整理時延遲指定秒數,避免過快刷新導致 IP 封鎖

### 主要實體

- **Cityline Event Page (活動頁面)**: 包含活動資訊與"購買"按鈕的頁面,使用者從此頁面開始搶票流程
- **Date Selection Page (日期選擇頁面)**: 包含多個日期時段選項(`button.date-time-position`),使用者選擇演出日期
- **Area Selection Page (區域選擇頁面)**: 包含多個座位區域或價格選項(`div.form-check` 內含 `input[type=radio]`),使用者選擇座位區域
- **Ticket Number Selector (票數選擇器)**: 使用 `select.select-num` 的下拉選單,使用者選擇購買張數
- **Login Page (登入頁面)**: Cityline 登入表單頁面(`cityline.com/Login.html`),使用者輸入帳號並同意條款
- **Purchase Flow State (購買流程狀態)**: 全域狀態變數,追蹤購買按鈕是否已點擊、音效是否已播放等流程控制資訊

## 成功標準 *(必填)*

### 可衡量成果

- **SC-001**: 使用者能夠在 `settings.json` 設定 `webdriver_type: "nodriver"` 後,成功使用 NoDriver 完成 Cityline 完整搶票流程(從登入到座位選擇),成功率與 Chrome UC 版本相當(>90%)
- **SC-002**: 系統在日期選擇階段,當設定關鍵字時,關鍵字匹配成功率達 90% 以上(基於歷史測試資料);當 `date_auto_fallback=false` 且關鍵字匹配失敗時,100% 正確執行嚴格模式邏輯(不自動選擇或根據設定自動重新整理)
- **SC-003**: 系統在區域選擇階段,能正確過濾 100% 的已售罄選項,避免選擇無效區域;當 `area_auto_fallback=false` 且關鍵字匹配失敗時,100% 不自動選擇任何區域,避免誤購
- **SC-004**: NoDriver 實作的程式碼中,90% 以上的 DOM 操作使用 NoDriver 原生方法(CDP 或內建 API),JavaScript 使用比例低於 10%
- **SC-005**: 系統在偵測到多分頁情況時,100% 能正確關閉舊分頁並切換至正確的活動分頁
- **SC-006**: 當設定 `auto_reload_coming_soon_page: true` 時,系統在日期列表為空的情況下,能在 3 秒內自動重新整理頁面
- **SC-007**: 系統在點擊購買按鈕後,能穩定等待 6 秒讓 reCAPTCHA 載入,無過早中斷或過長等待
- **SC-008**: NoDriver 版本與 Chrome UC 版本功能對等性達 100%,所有 Chrome UC 版本支援的功能(登入、日期選擇、區域選擇、票數選擇、下一步按鈕)在 NoDriver 版本中皆可用

## 假設 *(Assumptions)*

- **AS-001**: Cityline 平台的 DOM 結構在短期內(3-6 個月)保持穩定,選擇器如 `button.date-time-position`、`div.form-check`、`select.select-num` 等不會大幅變更
- **AS-002**: NoDriver 函式庫的 API 保持穩定,專案使用的核心方法(`query_selector`、`send_keys`、`click`、`cdp.dom.*`)在版本更新時保持向後相容
- **AS-003**: 使用者在 `settings.json` 中正確設定 Cityline 帳號(`cityline_account`),系統不負責帳號驗證或密碼處理(Cityline 登入僅需帳號)
- **AS-004**: Cityline 平台的 reCAPTCHA 驗證需要使用者手動完成,系統提供 6 秒等待時間但不實作自動驗證碼辨識
- **AS-005**: 專案已安裝 NoDriver 函式庫且版本符合最低需求(詳見 `docs/06-api-reference/nodriver_api_guide.md`)
- **AS-006**: 使用者的網路環境穩定,頁面載入時間在正常範圍內(<5 秒),不會因極端網路延遲導致腳本失敗
- **AS-007**: 本次遷移專注於功能對等性,效能優化與反偵測增強為後續改進項目

## 範圍 *(Scope)*

### 包含在本次規格內

- Cityline 平台從 Chrome UC 到 NoDriver 的完整功能遷移
- 登入功能(帳號填入、同意條款勾選)
- 日期選擇功能(關鍵字匹配、auto_select_mode、條件回退機制 date_auto_fallback、購買按鈕點擊)
- 區域選擇功能(關鍵字匹配、售罄過濾、條件回退機制 area_auto_fallback、radio 勾選)
- 票數選擇功能(下拉選單填入)
- 下一步按鈕點擊功能
- 多分頁處理功能
- 廣告清除功能
- 自動重試進入活動功能
- reCAPTCHA 等待處理
- 音效播放功能
- 遵循 NoDriver First 原則的程式碼實作
- 與 Chrome UC 版本的功能對等性驗證

### 明確排除在本次規格外

- Cityline 密碼自動填入功能(Cityline 登入不需要密碼輸入)
- 自動驗證碼辨識與繞過(reCAPTCHA 需手動完成)
- Cityline 平台的付款流程自動化(不在搶票系統範圍內)
- 其他平台(TixCraft、iBon、KKTIX 等)的 NoDriver 遷移
- NoDriver 效能優化與反偵測增強(列為後續改進項目)
- UI 介面變更或 settings.json 新增專屬設定(使用既有設定即可)
- 錯誤分類與詳細錯誤訊息(使用既有錯誤處理機制)
- 跨平台相容性測試(專注於 Windows 環境,其他平台為後續驗證)

## 相依性 *(Dependencies)*

- **DEP-001**: NoDriver 函式庫已安裝且版本符合專案需求(參考 `docs/06-api-reference/nodriver_api_guide.md`)
- **DEP-002**: Chrome 瀏覽器版本 90 以上(NoDriver 相容性需求)
- **DEP-003**: `settings.json` 中已正確設定 `webdriver_type`、`cityline_account`、日期/區域關鍵字、`date_auto_fallback`、`area_auto_fallback` 等必要參數
- **DEP-004**: 專案現有的通用工具函式(`util.is_row_match_keyword`、`util.get_target_item_from_matched_list` 等)功能正常
- **DEP-005**: Chrome UC 版本的 Cityline 實作已完成並經過驗證,可作為功能對等性的參考基準
- **DEP-006**: 音效檔案(`play_sound_while_ordering`)與相關配置已就緒

## 限制 *(Constraints)*

- **CON-001**: 本次實作必須遵循專案的 NoDriver First 原則(憲法第 I 條),優先使用 NoDriver 原生 CDP 方法
- **CON-002**: 程式碼必須遵循專案的 Emoji 使用規範(NON-NEGOTIABLE):所有 `.py` 檔案中禁止使用 emoji,避免 Windows cp950 編碼錯誤
- **CON-003**: 實作必須保持與 Chrome UC 版本的功能對等性,不得移除或削減既有功能
- **CON-004**: 所有修改必須符合專案的函數拆分原則(憲法第 IV 條):單一職責、可組合性、可測試性
- **CON-005**: 程式碼修改必須更新對應的文件(`docs/02-development/structure.md` 等),遵循文件與代碼同步原則(憲法第 VIII 條)
- **CON-006**: 本次實作不改變 `settings.json` 的既有結構,所有 Cityline 相關設定使用現有欄位
- **CON-007**: 記憶體使用必須控制在 500MB 以內(專案整體限制,參考憲法假設與約束)
- **CON-008**: Cityline reCAPTCHA 驗證必須由使用者手動完成,系統僅提供等待時間,不實作自動繞過機制

## 風險 *(Risks)*

- **RISK-001**: Cityline 平台可能偵測到 NoDriver 自動化行為並加強反爬蟲機制,導致搶票成功率下降
  - **緩解措施**: 遵循 NoDriver First 原則,使用原生 CDP 方法降低偵測風險;預留後續反偵測增強空間

- **RISK-002**: Cityline 平台可能變更 DOM 結構或 CSS 選擇器,導致腳本失效
  - **緩解措施**: 在程式碼中清楚標註選擇器位置,方便快速定位與修復;建議定期監控平台變更

- **RISK-003**: NoDriver 函式庫可能存在未知 bug 或穩定性問題,影響搶票流程
  - **緩解措施**: 保留 Chrome UC 版本作為回退方案,使用者可隨時透過 `webdriver_type` 切換

- **RISK-004**: reCAPTCHA 等待時間(6 秒)可能不足或過長,影響使用者體驗
  - **緩解措施**: 基於既有實作經驗設定 6 秒,後續可根據實際測試調整或改為可配置參數

- **RISK-005**: 多分頁處理邏輯可能在特定情況下誤關正確分頁
  - **緩解措施**: 實作時參考 Chrome UC 版本的邏輯,加入 URL 驗證(`tmp_url[:5] == "https"`)確保正確性

## 非功能性需求 *(Non-Functional Requirements)*

### 效能需求

- **NFR-001**: 日期選擇與區域選擇的關鍵字匹配處理時間應在 2 秒內完成(不含網路延遲)
- **NFR-002**: 頁面元素查詢(query_selector)應在 5 秒內完成或逾時,避免無限等待
- **NFR-003**: 自動重新整理頁面的間隔時間應遵循 `auto_reload_page_interval` 設定,預設建議 1-3 秒

### 可維護性需求

- **NFR-004**: 所有 Cityline NoDriver 相關函數應遵循命名規範:`nodriver_cityline_<功能名稱>`,便於識別與維護
- **NFR-005**: 程式碼應包含適當的註解,特別是與 Chrome UC 版本有差異的部分,說明實作考量
- **NFR-006**: 選擇器應集中定義為變數(如 `my_css_selector`),方便平台變更時快速修復
- **NFR-007**: 條件回退機制的日誌訊息應使用結構化前綴格式(`[DATE FALLBACK]` / `[AREA FALLBACK]`),與 TixCraft 等其他平台保持一致,便於跨平台日誌分析與除錯

### 相容性需求

- **NFR-008**: NoDriver 實作應與 Chrome UC 實作共存,不相互干擾,使用者可透過設定檔自由切換
- **NFR-009**: 支援 Windows 10 以上作業系統(專案主要目標平台)
- **NFR-010**: 支援 Chrome 瀏覽器版本 90 以上

### 可靠性需求

- **NFR-011**: 在網路暫時中斷或頁面載入失敗時,系統應捕獲異常並記錄錯誤,不應直接崩潰
- **NFR-012**: 關鍵操作(點擊、輸入)應包含異常處理,失敗時嘗試替代方案(如 JavaScript 強制點擊)
- **NFR-013**: 全域狀態變數(如 `cityline_purchase_button_pressed`)應正確初始化與重置,避免狀態污染

### 安全性需求

- **NFR-014**: 帳號資訊僅從 `settings.json` 讀取,不在程式碼中硬編碼
- **NFR-015**: 遵循專案的法律合規性原則(憲法假設與約束):個人使用,禁止商業黃牛行為

## 未來考量 *(Future Considerations)*

- 考慮實作 Cityline 密碼加密儲存功能(目前 Cityline 登入不需密碼,但未來平台可能變更)
- 考慮實作更精細的 reCAPTCHA 偵測機制,動態調整等待時間而非固定 6 秒
- 考慮實作 Cityline 專屬的錯誤分類與詳細錯誤訊息,提升除錯效率
- 考慮將 `auto_reload_page_interval`、`recaptcha_wait_time` 等硬編碼參數改為可配置選項
- 考慮實作 Cityline 平台的效能監控與反偵測增強,進一步提升 NoDriver 的優勢
- 考慮擴展測試覆蓋範圍,包含 macOS 與 Linux 平台的相容性驗證
