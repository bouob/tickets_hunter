# 功能規格說明: 關鍵字優先選擇與條件式自動遞補

**功能分支**: `feature/003-keyword-priority-fallback`
**建立日期**: 2025-10-31
**狀態**: 草稿
**輸入**: 用戶描述: "目前程式的日期與區域選擇的邏輯是依序比對關鍵字，如果命中了就加入陣列清單，然後依據自動選擇模式來進行。規格需要調整：1. 主開關檢查 2. 關鍵字優先匹配（早期返回）3. 條件式自動遞補 4. 排除關鍵字處理 5. UI 設計。重要：預設遞補為關閉狀態（false）"

## Clarifications

### Session 2025-10-31

- Q: 傳統視窗 UI (settings_old.py) 的遞補開關實作方式 → A: 使用與 settings.html 相同的核取方塊控制項，放在對應的自動選擇區塊下方
- Q: 傳統視窗 UI 的具體實作技術 → A: tkinter 桌面 GUI（settings_old.py 使用 tkinter，而非 tornado web 介面）
- Q: 傳統視窗 UI 的多語言支援需求 → A: 提供完整多語言支援（en_us, zh_tw, ja_jp），與既有欄位保持一致
- Q: tkinter GUI 中遞補開關的放置位置 → A: 在對應 frame 中，緊接在主開關核取方塊下方（date_auto_fallback 緊接 chk_date_auto_select，area_auto_fallback 緊接 chk_area_auto_select）
- Q: tkinter GUI 中遞補開關的說明文字呈現方式 → A: 使用較簡短的標籤文字（如「遞補選擇」），搭配 tooltip 顯示完整說明（避免介面擁擠）

## 用戶情境與測試

### User Story 1 - 關鍵字優先匹配（早期返回）(Priority: P1)

身為搶票使用者，當我設定了日期或區域關鍵字清單時，我希望系統依照我設定的順序依序檢查，並在第一個匹配成功時立即選擇該選項並停止後續檢查，這樣我就能確保優先級最高的選項被快速鎖定，同時節省檢查時間。

**優先級說明**: 這是核心邏輯變更，直接影響所有平台（TixCraft、KKTIX、iBon、TicketPlus、KHAM、FamiTicket）的搶票效能與準確度。早期返回模式可平均節省 30% 的關鍵字檢查時間，提升搶票成功率。

**獨立測試方式**: 可透過設定 `date_keyword = "11/16;11/17;11/18"`，在測試頁面僅提供 "11/17"，驗證系統是否：(1) 跳過第一個關鍵字；(2) 在第二個關鍵字匹配時立即選擇；(3) 不檢查第三個關鍵字；(4) 記錄英文日誌訊息。

**驗收情境**:

1. **假設** 使用者設定 `date_keyword = "11/16;11/17;11/18"`，頁面上有 "11/16" 和 "11/19"，**當** 系統執行日期選擇邏輯，**則** 系統選擇 "11/16" 並立即停止，日誌顯示 "Keyword #1 matched: '11/16'" 和 "Selected date: 11/16 (keyword match)"
2. **假設** 使用者設定 `date_keyword = "11/16;11/17;11/18"`，頁面上僅有 "11/17" 和 "11/19"，**當** 系統執行日期選擇邏輯，**則** 系統跳過第一個關鍵字，選擇 "11/17" 並停止，日誌顯示 "Keyword #1: No match" 和 "Keyword #2 matched: '11/17'"
3. **假設** 使用者設定 `area_keyword = "搖滾區A;VIP區;一般區"`，頁面上有 "VIP區" 和 "一般區"，**當** 系統執行區域選擇邏輯，**則** 系統選擇 "VIP區"（第二順位）並停止，不檢查 "一般區"
4. **假設** 使用者設定 `area_keyword = "1280 一般"`（AND 邏輯），頁面上有 "搖滾區 $1,280 一般票"，**當** 系統執行區域選擇邏輯，**則** 系統匹配成功（同時包含 "1280" 和 "一般"），立即選擇該選項

---

### User Story 2 - 條件式自動遞補控制 (Priority: P1)

身為搶票使用者，當我的所有關鍵字都未能匹配成功時，我希望能選擇是否讓系統自動遞補選擇其他可用選項，或者保持等待手動介入，這樣我就能在嚴格匹配模式（只選擇特定場次）和彈性模式（接受替代選項）之間彈性切換。

**優先級說明**: 這是新增的核心功能，讓使用者能控制「關鍵字全部失敗」時的行為。預設為嚴格模式（false），只選擇關鍵字匹配的選項，避免誤搶不想要的場次。使用者可主動開啟遞補功能（true）以提高搶票成功率。

**獨立測試方式**: 可透過設定 `date_keyword = "11/16;11/17"` 和 `date_auto_fallback = false`（預設值），在頁面僅有 "11/18" 和 "11/19" 的情況下，驗證系統是否不選擇任何日期並記錄 "fallback is disabled"。設定 `date_auto_fallback = true` 時，驗證系統是否根據 `date_select_order` 自動選擇可用日期。

**驗收情境**:

1. **假設** 使用者設定 `date_keyword = "11/16;11/17"`，頁面上有 "11/18" 和 "11/19"（關鍵字全部失敗），且未設定 `date_auto_fallback`（使用預設值 false），**當** 系統執行日期選擇邏輯，**則** 系統不選擇任何日期（返回 None 或 False），日誌顯示 "All keywords failed to match" 和 "date_auto_fallback=false, fallback is disabled" 和 "Waiting for manual intervention"
2. **假設** 使用者設定 `date_keyword = "11/16;11/17"`、`date_auto_fallback = true`、`date_select_order = "from_top_to_bottom"`，頁面上有 "11/18" 和 "11/19"（關鍵字全部失敗），**當** 系統執行日期選擇邏輯，**則** 系統選擇 "11/18"（第一個可用選項），日誌顯示 "All keywords failed to match" 和 "date_auto_fallback=true, triggering auto fallback" 和 "Selected date: 11/18 (fallback)"
3. **假設** 使用者設定 `area_keyword = "VIP區"`、`area_auto_fallback = true`、`area_select_order = "random"`，頁面上有 "搖滾區A" 和 "搖滾區B"（關鍵字失敗），**當** 系統執行區域選擇邏輯，**則** 系統從可用區域隨機選擇一個，日誌顯示 "Selected area: [選項] (fallback)"
4. **假設** 使用者擁有不包含 `date_auto_fallback` 欄位的舊版設定檔，**當** 系統載入設定並執行日期選擇邏輯，**則** 系統使用 `.get('date_auto_fallback', False)` 取得預設值 `False`，啟用嚴格模式（僅選擇關鍵字匹配的選項）
5. **假設** 使用者設定 `date_auto_fallback = true` 但頁面上所有日期都包含排除關鍵字（`keyword_exclude = "已售完"`，所有日期都標記為 "已售完"），**當** 系統執行遞補邏輯，**則** `formated_area_list` 為空，系統返回 None，日誌顯示 "No available options after exclusion"

---

### User Story 3 - UI 控制項設計與整合 (Priority: P2)

身為搶票使用者，我希望在設定頁面（無論是網頁版 settings.html 或桌面版 settings_old.py）能看到清楚的「日期自動遞補」和「區域自動遞補」核取方塊，並附有簡單易懂的說明文字，這樣我就能快速理解並調整遞補功能的開關，無需翻閱技術文件或手動編輯 JSON 檔案。

**優先級說明**: 這是 UI 改善，優先級較低。核心邏輯（P1）完成後，使用者可透過手動編輯 settings.json 來控制遞補功能。UI 控制項提升使用者體驗，但不影響功能本身。兩種 UI 介面（網頁版與桌面版）皆需提供一致的控制項。

**獨立測試方式**:
- **網頁版 (settings.html)**: 開啟 settings.html，驗證：(1) 「日期自動點選」區塊下有「日期自動遞補」核取方塊，預設未勾選；(2) 「區域自動點選」區塊下有「區域自動遞補」核取方塊，預設未勾選；(3) 切換核取方塊並儲存後，settings.json 正確寫入布林值；(4) 重新載入頁面後，核取方塊狀態與設定檔一致。
- **桌面版 (settings_old.py tkinter GUI)**: 啟動 settings_old.py，驗證：(1) 日期自動選擇區塊下有「日期自動遞補」核取方塊（chk_date_auto_fallback），緊接在主開關下方；(2) 區域自動選擇區塊下有「區域自動遞補」核取方塊（chk_area_auto_fallback），緊接在主開關下方；(3) 滑鼠懸停時顯示 tooltip 說明；(4) 切換核取方塊並儲存後，settings.json 正確寫入布林值。

**驗收情境（網頁版 settings.html）**:

1. **假設** 使用者首次開啟 settings.html（設定檔不含新欄位），**當** 頁面載入完成，**則** 「日期自動遞補」和「區域自動遞補」核取方塊皆為未勾選狀態（預設 false）
2. **假設** 使用者勾選「日期自動遞補」核取方塊並點擊「儲存」，**當** 設定儲存完成，**則** settings.json 包含 `"date_auto_fallback": true`
3. **假設** settings.json 包含 `"date_auto_fallback": true` 和 `"area_auto_fallback": false`，**當** 使用者開啟 settings.html，**則** 「日期自動遞補」核取方塊已勾選，「區域自動遞補」核取方塊未勾選
4. **假設** 使用者在「日期自動遞補」核取方塊下看到說明文字，**當** 閱讀說明，**則** 文字清楚表示「當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉，僅選擇關鍵字匹配的選項）」（非技術術語）

**驗收情境（桌面版 settings_old.py tkinter GUI）**:

1. **假設** 使用者啟動 settings_old.py 桌面 GUI（設定檔不含新欄位），**當** 介面載入完成，**則** 「日期自動遞補」（chk_date_auto_fallback）和「區域自動遞補」（chk_area_auto_fallback）核取方塊皆為未勾選狀態（預設 false），且緊接在對應的主開關下方
2. **假設** 使用者勾選「日期自動遞補」核取方塊並點擊「Save」，**當** 設定儲存完成，**則** settings.json 包含 `"date_auto_fallback": true`
3. **假設** 使用者將滑鼠懸停在「日期自動遞補」核取方塊上，**當** tooltip 顯示，**則** 完整說明文字顯示「當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉，僅選擇關鍵字匹配的選項）」
4. **假設** 使用者切換介面語言為英文（en_us），**當** 介面重新載入，**則** 核取方塊標籤顯示為 "Date Auto Fallback" 和 "Area Auto Fallback"（多語言支援）
5. **假設** 使用者切換介面語言為日文（ja_jp），**當** 介面重新載入，**則** 核取方塊標籤顯示對應的日文翻譯（多語言支援）

---

### 邊界情境

- 當關鍵字清單為空字串（`date_keyword = ""`）時會怎樣？
  - 系統跳過關鍵字匹配邏輯，直接使用 `date_select_order` 從 `formated_area_list` 選擇可用日期（既有行為，不受新功能影響）

- 當主開關（`date_auto_select.enable`）關閉時，`date_auto_fallback` 是否仍生效？
  - 否，主開關關閉時完全不執行日期選擇函數，`date_auto_fallback` 開關被忽略

- 系統如何處理關鍵字解析錯誤（如 JSON 格式不正確）？
  - 使用 try-except 捕捉異常，記錄錯誤日誌（英文），將關鍵字清單視為空，繼續執行後續邏輯（直接使用 mode 選擇）

- 當遞補選擇失敗（`formated_area_list` 為空，所有選項都被排除）時會怎樣？
  - 返回 None 或 False，記錄警告日誌 "No available options after exclusion"，系統進入等待狀態（根據平台特定邏輯處理，如重新整理頁面）

- 排除關鍵字（`keyword_exclude`）如何與新邏輯互動？
  - 現有邏輯已在建立 `formated_area_list` 時透過 `util.reset_row_text_if_match_keyword_exclude()` 過濾掉包含排除關鍵字的選項
  - 關鍵字匹配與遞補選擇都是從已過濾的 `formated_area_list` 中進行，因此自動遵守排除規則
  - 無需在匹配或遞補階段額外檢查排除關鍵字

## 需求

### 功能性需求

**主開關檢查**

- **FR-001**: 系統必須檢查 `date_auto_select.enable` 布林欄位，若為 `False` 則完全不執行日期選擇邏輯，直接返回
- **FR-002**: 系統必須檢查 `area_auto_select.enable` 布林欄位，若為 `False` 則完全不執行區域選擇邏輯，直接返回

**關鍵字優先匹配（早期返回）**

- **FR-003**: 系統必須依照使用者設定的日期關鍵字清單順序（`date_keyword`，分號分隔），依序檢查 `formated_area_list` 中的日期選項，一旦第一個關鍵字匹配成功，立即選擇該日期並返回，不再檢查後續關鍵字
- **FR-004**: 系統必須依照使用者設定的區域關鍵字清單順序（`area_keyword`，分號分隔），依序檢查 `formated_area_list` 中的區域選項，一旦第一個關鍵字匹配成功，立即選擇該區域並返回，不再檢查後續關鍵字
- **FR-005**: 系統在進行關鍵字匹配時，必須支援 AND 邏輯（空格分隔），當關鍵字包含空格時（如 "1280 一般"），選項必須同時包含所有詞彙才視為匹配成功

**條件式遞補機制**

- **FR-006**: 系統必須在設定檔中新增 `date_auto_fallback` 布林欄位，預設值為 `False`（嚴格模式：僅選擇關鍵字匹配的選項）
- **FR-007**: 系統必須在設定檔中新增 `area_auto_fallback` 布林欄位，預設值為 `False`（嚴格模式：僅選擇關鍵字匹配的選項）
- **FR-008**: 當所有日期關鍵字都未匹配成功時，系統必須使用 `.get('date_auto_fallback', False)` 安全存取該欄位，若為 `True` 則根據 `date_select_order` 從 `formated_area_list` 中自動選擇可用日期，若為 `False` 則返回 None 或 False（等待手動介入）
- **FR-009**: 當所有區域關鍵字都未匹配成功時，系統必須使用 `.get('area_auto_fallback', False)` 安全存取該欄位，若為 `True` 則根據 `area_select_order` 從 `formated_area_list` 中自動選擇可用區域，若為 `False` 則返回 None 或 False（等待手動介入）

**排除關鍵字處理**

- **FR-010**: 系統必須在建立 `formated_area_list` 時使用 `util.reset_row_text_if_match_keyword_exclude(config_dict, row_text)` 函數過濾掉包含 `keyword_exclude` 清單中任一關鍵字的選項
- **FR-011**: 關鍵字匹配邏輯必須僅從已過濾的 `formated_area_list` 中進行匹配，無需額外檢查排除關鍵字
- **FR-012**: 遞補選擇邏輯必須僅從已過濾的 `formated_area_list` 中選擇，無需額外檢查排除關鍵字

**日誌與除錯**

- **FR-013**: 系統必須記錄英文日誌訊息，當開始檢查關鍵字時輸出 "Start checking keywords in order: [清單]"
- **FR-014**: 系統必須記錄英文日誌訊息，當第 N 個關鍵字匹配成功時輸出 "Keyword #N matched: '[關鍵字]'" 和 "Selected date/area: [選項] (keyword match)"
- **FR-015**: 系統必須記錄英文日誌訊息，當所有關鍵字都未匹配時輸出 "All keywords failed to match"
- **FR-016**: 系統必須記錄英文日誌訊息，當遞補功能啟用時輸出 "date_auto_fallback=true, triggering auto fallback" 和 "Selected date/area: [選項] (fallback)"
- **FR-017**: 系統必須記錄英文日誌訊息，當遞補功能停用時輸出 "date_auto_fallback=false, fallback is disabled" 和 "Waiting for manual intervention"
- **FR-018**: 系統必須記錄英文日誌訊息，當遞補選擇失敗（`formated_area_list` 為空）時輸出 "No available options after exclusion"

**UI 設計（網頁版 settings.html）**

- **FR-019**: settings.html 必須在「日期自動點選」區塊新增「日期自動遞補」核取方塊（id="date_auto_fallback"），預設未勾選，附帶說明文字「當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉）」
- **FR-020**: settings.html 必須在「區域自動點選」區塊新增「區域自動遞補」核取方塊（id="area_auto_fallback"），預設未勾選，附帶說明文字「當所有區域關鍵字都未匹配時，是否自動選擇可用區域（預設關閉）」
- **FR-021**: settings.html 的 JavaScript 必須在載入設定時讀取 `date_auto_fallback` 和 `area_auto_fallback` 欄位，若欄位不存在則使用預設值 `false`
- **FR-022**: settings.html 的 JavaScript 必須在儲存設定時將核取方塊狀態（checked/unchecked）寫入 `date_auto_fallback` 和 `area_auto_fallback` 欄位為布林值（true/false）

**UI 設計（桌面版 settings_old.py tkinter GUI）**

- **FR-023**: settings_old.py 必須在日期自動選擇區塊（frame_group_tixcraft）新增「日期自動遞補」核取方塊（chk_date_auto_fallback），緊接在 chk_date_auto_select 主開關下方，預設未勾選
- **FR-024**: settings_old.py 必須在區域自動選擇區塊（frame_group_area）新增「區域自動遞補」核取方塊（chk_area_auto_fallback），緊接在 chk_area_auto_select 主開關下方，預設未勾選
- **FR-025**: settings_old.py 必須為兩個遞補核取方塊提供完整多語言支援（en_us, zh_tw, ja_jp），標籤文字簡短（如繁中「遞補選擇」、英文「Auto Fallback」、日文「自動フォールバック」）
- **FR-026**: settings_old.py 必須為兩個遞補核取方塊新增 tooltip（滑鼠懸停提示），顯示完整說明文字「當所有日期/區域關鍵字都未匹配時，是否自動選擇可用日期/區域（預設關閉，僅選擇關鍵字匹配的選項）」（依語言顯示對應翻譯）
- **FR-027**: settings_old.py 的儲存邏輯必須讀取兩個遞補核取方塊的狀態（chk_state_date_auto_fallback.get() 和 chk_state_area_auto_fallback.get()），並寫入 `date_auto_fallback` 和 `area_auto_fallback` 欄位為布林值
- **FR-028**: settings_old.py 的載入邏輯必須讀取 `date_auto_fallback` 和 `area_auto_fallback` 欄位，若欄位不存在則使用預設值 `False`，並設定核取方塊狀態

**程式碼維護**

- **FR-029**: 系統必須將舊版的「掃描所有關鍵字後將匹配項加入陣列再選擇」的邏輯註解並標記為 DEPRECATED，保留程式碼但不執行，以便測試與回滾
- **FR-030**: 僅修改 `nodriver_tixcraft.py`，`chrome_tixcraft.py` 保持不變（進入維護模式）
- **FR-031**: 系統必須在 `settings.py` 和 `settings_old.py` 的 `get_default_config()` 函數中新增 `date_auto_fallback` 和 `area_auto_fallback` 欄位，預設值皆為 `False`

### 主要實體

- **Configuration（設定檔）**: 代表使用者的搶票偏好設定，包含：
  - `date_auto_select.enable` (boolean): 日期自動選擇主開關
  - `date_auto_select.date_keyword` (string): 分號分隔的日期關鍵字清單
  - `date_auto_select.mode` (string): 日期排序規則（如 "from_top_to_bottom"）
  - `date_auto_fallback` (boolean): 日期自動遞補開關（新增，預設 false）
  - `area_auto_select.enable` (boolean): 區域自動選擇主開關
  - `area_auto_select.area_keyword` (string): 分號分隔的區域關鍵字清單
  - `area_auto_select.mode` (string): 區域排序規則
  - `area_auto_fallback` (boolean): 區域自動遞補開關（新增，預設 false）
  - `keyword_exclude` (string): 分號分隔的排除關鍵字清單

- **FormatedAreaList（已過濾的可用選項清單）**: 代表頁面上可用的日期或區域選項，經過以下過濾：
  - 移除包含排除關鍵字（`keyword_exclude`）的選項
  - 移除「即將開賣」狀態的選項（依平台設定）
  - 移除「已售完」狀態的選項（依平台設定）
  - 此清單是關鍵字匹配與遞補選擇的唯一來源

- **KeywordMatchResult（關鍵字匹配結果）**: 代表關鍵字匹配過程的結果狀態（概念性，用於理解流程）：
  - `matched` (boolean): 是否有關鍵字匹配成功
  - `matched_keyword` (string|null): 匹配成功的關鍵字內容
  - `matched_index` (integer|null): 匹配成功的關鍵字索引（從 1 開始）
  - `selected_option` (object|null): 最終選擇的選項（DOM 元素）
  - `is_fallback` (boolean): 最終選擇是否來自遞補邏輯

## 成功標準

### 可衡量成果

- **SC-001**: 當第一個關鍵字匹配成功時，系統平均檢查時間減少 30%（相較於掃描所有關鍵字的舊邏輯）
- **SC-002**: 在 100 個測試案例中，當第 2 個關鍵字匹配成功時，系統在 100% 的案例中選擇第 2 個關鍵字對應的選項，且不檢查第 3 個關鍵字
- **SC-003**: 使用嚴格模式（`date_auto_fallback = false`，預設值）的使用者，在關鍵字全部失敗時，系統不會自動選擇任何選項的成功率達 100%
- **SC-004**: 使用彈性模式（`date_auto_fallback = true`）的使用者，在關鍵字全部失敗且頁面有可用選項時，系統能成功遞補選擇可用選項的成功率達 100%
- **SC-005**: 舊版設定檔（不含新欄位）升級後，系統啟用嚴格模式（僅選擇關鍵字匹配的選項），避免誤搶不想要的場次，安全性達 100%
- **SC-006**: 使用者能在 30 秒內理解並調整 UI 中的遞補開關，無需查閱技術文件
- **SC-007**: 所有日誌訊息使用英文輸出，不會因編碼問題（Windows cp950）導致程式崩潰，穩定性達 100%

## 範圍

### 包含項目

- 修改 `nodriver_tixcraft.py` 中的日期與區域選擇邏輯
- 實作主開關檢查邏輯（`date_auto_select.enable` / `area_auto_select.enable`）
- 實作關鍵字優先匹配（早期返回模式）
- 實作條件式遞補邏輯（檢查 `date_auto_fallback` / `area_auto_fallback` 開關）
- 新增 `date_auto_fallback` 和 `area_auto_fallback` 欄位至設定檔結構（預設值 false）
- 新增結構化英文日誌訊息
- 在 settings.html 新增遞補開關的 UI 控制項（網頁版，預設未勾選）
- 在 settings_old.py 新增遞補開關的 tkinter GUI 控制項（桌面版，含多語言支援與 tooltip）
- 更新 `settings.py` 和 `settings_old.py` 的 `get_default_config()` 函數以包含新欄位
- 註解舊程式碼並標記 DEPRECATED
- 更新 CHANGELOG.md 記錄功能變更

### 排除項目

- 不修改 `chrome_tixcraft.py`（進入維護模式）
- 不修改排除關鍵字（`keyword_exclude`）的過濾邏輯（既有邏輯已正確運作）
- 不修改 `formated_area_list` 的建立邏輯（既有邏輯已包含排除關鍵字過濾）
- 不修改 `date_select_order` 或 `area_select_order` 的排序規則（既有功能）
- 不修改 `util.reset_row_text_if_match_keyword_exclude()` 函數（既有工具函數）
- 不修改平台特定的 DOM 選擇器或點擊方法（如 TixCraft、KKTIX、iBon 等平台的具體實作）
- 不修改驗證碼辨識、Cookie 登入、排隊處理等其他功能
- 不新增關鍵字正規表達式支援（保持現有的精確匹配邏輯）

## 假設與相依性

### 假設

- 使用者理解關鍵字清單的順序代表優先順序（第一個關鍵字優先級最高）
- 使用者設定的排除關鍵字（`keyword_exclude`）不會與所有關鍵字清單（`date_keyword`、`area_keyword`）完全衝突（若衝突，`formated_area_list` 將為空，系統無法選擇任何選項）
- 頁面結構保持穩定，日期與區域選項的 DOM 結構不會頻繁變更
- 使用者在設定遞補開關時，理解「嚴格模式」（預設，僅選擇關鍵字匹配）與「彈性模式」（開啟遞補，接受替代選項）的差異
- 舊版設定檔升級後，系統預設啟用嚴格模式（`date_auto_fallback = false`），使用者需主動開啟遞補功能以提高搶票成功率
- 日誌訊息使用英文不會造成中文使用者的理解困難（因為日誌主要用於除錯，非一般使用者閱讀）
- 現有的 `formated_area_list` 建立邏輯已正確過濾掉包含排除關鍵字的選項，無需在關鍵字匹配或遞補階段額外檢查

### 相依性

- **設定檔載入機制**: 依賴 `settings.py` 或 `settings_old.py` 的 `get_default_config()` 和 JSON 載入函數
- **關鍵字解析邏輯**: 依賴分號分隔符（`;`）解析關鍵字清單（Feature 002 已實作）
- **排除關鍵字過濾邏輯**: 依賴 `util.reset_row_text_if_match_keyword_exclude()` 函數（既有工具函數）
- **排序模式邏輯**: 依賴 `util.get_target_item_from_matched_list()` 函數根據 `date_select_order` 或 `area_select_order` 選擇選項
- **NoDriver API**: 依賴 NoDriver 瀏覽器控制 API 進行元素互動與點擊
- **平台特定實作**: 依賴各平台模組（TixCraft、KKTIX、iBon、TicketPlus、KHAM、FamiTicket）的 DOM 選擇器與互動邏輯
- **UI 框架（網頁版）**: settings.html 依賴 Bootstrap 5.3.8 框架提供核取方塊樣式
- **GUI 框架（桌面版）**: settings_old.py 依賴 tkinter（Python 內建 GUI 框架）提供核取方塊、tooltip 等控制項
- **多語言系統**: settings_old.py 依賴既有的多語言翻譯字典（translate['en_us'], translate['zh_tw'], translate['ja_jp']）

### 技術約束

- 僅支援 NoDriver 引擎（chrome_tixcraft.py 不在修改範圍內）
- 支援的平台：TixCraft、KKTIX、iBon、TicketPlus、KHAM、FamiTicket
- 作業系統：Windows（日誌訊息必須避免 cp950 編碼錯誤）
- 設定檔格式：JSON（必須保持向後相容）
- 日誌訊息語言：英文（避免編碼問題）
- Python 版本：3.7+（依據專案既有需求）

### 法律與合規

- 本功能僅供個人使用，禁止商業黃牛行為
- 遵守各售票平台的使用條款（如速率限制、反爬蟲政策）
- 不提供繞過驗證碼或反偵測機制的功能（僅處理關鍵字匹配邏輯）
- 不涉及使用者個人資料處理（僅處理設定檔偏好）
