# 程式開發規範指南

> **目標**：確保代碼品質一致性與最佳實踐，適用於所有 WebDriver 類型的搶票系統開發

## 寫作風格原則

**開發新功能時必須**：
1. **遵循架構範本**：參考 `/docs/coding_templates.md` 的標準架構
2. **參考最佳實踐**：以 NoDriver 平台實作（TixCraft、KKTIX、TicketPlus、iBon）作為開發標準
3. **保持一致性**：函數命名、錯誤處理、debug 輸出格式統一

## WebDriver 除錯規則

**重要：除錯任何 WebDriver 問題時，必須先查閱對應 API 指南**

### NoDriver 除錯規則（推薦優先）

當除錯或修改 NoDriver 平台實作時，必須遵循以下流程：

1. **首先查閱 API 指南**
   - 必須先查看 `/docs/nodriver_api_guide.md`
   - 確認使用的方法是否存在且穩定
   - 優先使用推薦的 JavaScript 方法

2. **避免元素物件操作**
   - 不使用 `element.get_html()` → 改用 `tab.evaluate()`
   - 不使用 `element.click()` → 改用 JavaScript 點擊
   - 不使用 `element.apply()` → 改用 `tab.evaluate()`
   - 不使用 `element.send_keys()` → 改用 `tab.send()` 或 JavaScript

3. **推薦模式**
   - 所有 DOM 操作都在 `evaluate()` 中完成
   - 使用 `util.parse_nodriver_result()` 處理返回值
   - 實作錯誤處理和重試機制

4. **Shadow DOM 穿透策略** ⭐
   - **優先使用 Pierce Method**：處理 Shadow DOM 時首選（60-70% 速度提升）
   - **技術方案**：`cdp.dom.perform_search()` + `include_user_agent_shadow_dom=True`
   - **Primary → Fallback 模式**：Pierce 失敗時回退 DOMSnapshot
   - **智能等待**：輪詢檢查元素是否出現，找到即執行（vs 固定延遲）
   - **參考實作**：`nodriver_ibon_date_auto_select_pierce()` (Line 6368-6700)
   - **詳細文檔**：`/docs/06-api-reference/shadow_dom_pierce_guide.md`
   - **性能對比**：
     ```
     Pierce Method: 2-5秒, 95%+ 成功率, 1-10 節點處理
     DOMSnapshot:  10-15秒, 20% 成功率, 6000+ 節點處理
     ```

5. **參考標準實作**
   - 以 NoDriver 平台（TixCraft、KKTIX、TicketPlus、iBon）為開發標準
   - 確認函數命名規範和錯誤處理模式
   - 遵循既有的重試機制和等待策略

### Chrome Driver 除錯規則（過渡期維護）

當除錯或修改 Chrome Driver 實作時，必須遵循以下流程：

1. **首先查閱 API 指南**
   - 必須先查看 `/docs/chrome_api_guide.md`
   - 確認 undetected_chromedriver 特定方法
   - 了解反偵測機制限制和最佳實踐

2. **參考標準實作**
   - 以 chrome_tixcraft.py 為 Chrome Driver 參考
   - 確認函數命名規範和錯誤處理模式
   - 遵循既有的重試機制和等待策略

## 搶票程式標準函數架構（12 階段）

### 核心設計原則

#### 1. 設定驅動 (Configuration-Driven)
所有功能行為由 `settings.json` 控制，使用者無需修改程式碼即可調整行為。

#### 2. 回退策略 (Fallback Strategy)
每個功能都有明確的優先策略與回退方案：
1. **優先策略**：使用使用者指定的關鍵字或參數
2. **回退策略 1**：關鍵字未命中時使用自動選擇模式
3. **回退策略 2**：功能禁用時跳過或等待手動操作

#### 3. 函式拆分原則
- **原子化**：每個函式只負責一個明確的任務
- **可組合**：函式可以組合成更複雜的工作流程
- **可測試**：函式輸入輸出明確，易於單元測試
- **可重用**：跨平台可共用的邏輯抽取為通用工具函式

### 12 階段完整功能架構

#### 階段 1：環境初始化
- `nodriver_{platform}_main()` 或 `{platform}_main()`
- 初始化 WebDriver、瀏覽器設定、擴充功能載入
- 配置驗證與啟動檢查

#### 階段 2：身份認證
- `{platform}_login()` - 自動登入處理
- 支援 Cookie 注入（優先）或帳號密碼登入
- 登入狀態驗證與會話維持

#### 階段 3：頁面監控與重載
- `auto_reload_page()` - 自動重載（通用）
- `{platform}_close_popup_windows()` - 彈窗處理
- 過熱保護、排隊/等候室偵測

#### 階段 4：日期選擇
- `{platform}_date_auto_select()` - 自動選擇日期
- 偵測版面類型 → 關鍵字匹配 → mode 回退選擇
- 支援多關鍵字、排除過濾、售完狀態處理

#### 階段 5：區域/座位選擇
- `{platform}_area_auto_select()` - 自動選擇區域
- 支援關鍵字匹配、排除過濾、自動座位選擇
- 相鄰座位處理、價格資訊提取

#### 階段 6：票數設定
- `{platform}_assign_ticket_number()` - 自動設定票數
- 支援多種版面類型（下拉/輸入框/按鈕/價格清單）
- 票數驗證與調整

#### 階段 7：驗證碼處理
- `{platform}_auto_ocr()` 或 `{platform}_captcha()` - 驗證碼自動處理
- 偵測類型 → 圖片提取 → OCR 辨識 → 輸入/回退
- 支援多重重試、手動輸入回退

#### 階段 8：表單填寫
- `{platform}_form_auto_fill()` - 自動填寫購票資訊
- 偵測欄位 → 填寫個人資訊 → 自訂問題答案處理

#### 階段 9：同意條款處理
- `{platform}_ticket_agree()` - 自動勾選同意條款
- 支援複選框、單選按鈕、特殊對話框處理

#### 階段 10：訂單確認與送出
- `{platform}_ticket_main()` 或 `{platform}_order()` - 確認並送出訂單
- 訂單詳情審查 → 送出按鈕點擊 → 確認對話框處理
- 音效通知、訂單成功驗證

#### 階段 11：排隊與付款
- `{platform}_paused_main()` 或 `{platform}_handle_queue()` - 排隊處理
- 排隊狀態監控、進度追蹤、逾時處理

#### 階段 12：錯誤處理與重試
- 全域錯誤分類與日誌記錄
- 指數退避重試策略、售完狀態優雅處理
- 錯誤通知與重試限制

### 每個平台實作必須包含以下核心函數：

#### 1. 主控制器 (Main Controller)
- `nodriver_{platform}_main()` - NoDriver 版本（推薦，async 函數）
- `{platform}_main()` - Chrome Driver 版本（過渡期維護）

#### 2. 核心功能模組
- **日期選擇**：
  - `nodriver_{platform}_date_auto_select()` - NoDriver 版本（推薦）
  - `{platform}_date_auto_select()` - Chrome Driver 版本
- **座位選擇**：
  - `nodriver_{platform}_area_auto_select()` - NoDriver 版本（推薦）
  - `{platform}_area_auto_select()` - Chrome Driver 版本
- **票數設定**：
  - `nodriver_{platform}_assign_ticket_number()` - NoDriver 版本（推薦）
  - `{platform}_assign_ticket_number()` - Chrome Driver 版本
- **驗證碼處理**：
  - `nodriver_{platform}_auto_ocr()` - NoDriver 版本（推薦）
  - `{platform}_auto_ocr()` - Chrome Driver 版本

#### 3. 輔助功能模組
- **登入處理**：`nodriver_{platform}_login()` / `{platform}_login()`
- **同意條款**：`nodriver_{platform}_ticket_agree()` / `{platform}_ticket_agree()`
- **實名認證**：`nodriver_{platform}_real_name_verify()` / `{platform}_real_name_verify()`
- **狀態檢查**：`nodriver_{platform}_check_status()` / `{platform}_check_status()`

> **詳細的 12 階段功能定義、函式拆分規範、設定項目索引表請參考**：[搶票自動化標準功能定義](./ticket_automation_standard.md)

## 程式碼品質標準

### 必要元素
```python
# 每個函數都必須包含可控制的除錯模式
show_debug_message = config_dict["advanced"]["verbose"]

# 標準異常處理
try:
    # 主要邏輯
except Exception as exc:
    if show_debug_message:
        print(f"Error in {function_name}: {exc}")
    # 提供合理的錯誤處理

# 重試機制（關鍵操作）
for retry_count in range(max_retry):
    if retry_count > 0:
        time.sleep(0.5)
    # 執行邏輯
```

---

## 暫停機制開發規範

> **適用範圍**：僅限 NoDriver 版本平台函數（Chrome Driver 不支援）

### 核心原則

1. **統一入口**
   - 所有暫停檢查必須使用 `check_and_handle_pause(config_dict)`
   - 禁止直接檢查 `os.path.exists(CONST_MAXBOT_INT28_FILE)`
   - 確保行為一致性，由 verbose 設定統一控制

2. **訊息顯示控制**
   - 由 `config_dict["advanced"]["verbose"]` 統一控制
   - `verbose = true` 時顯示 "BOT Paused."
   - `verbose = false` 時不顯示
   - 不要在呼叫端額外加入訊息顯示邏輯

3. **僅在 NoDriver 版本實作**
   - Chrome Driver 版本不支援暫停機制
   - 保持兩個版本的功能差異性
   - NoDriver 版本的優勢特性之一

### 實作原則

#### 1. 檢查時機

**必須檢查的位置：**
- 函數開始時：每個 NoDriver 函數入口
- 長時間迴圈內：每次迭代開始時

**建議檢查的位置：**
- 長時間操作前：如複雜 JavaScript 執行
- 延遲等待時：使用暫停版本的 sleep 函數

#### 2. 輔助函數優先

使用專用的暫停檢查包裝函數：

**`sleep_with_pause_check(tab, seconds, config_dict)`**
- 取代 `tab.sleep()`
- 等待期間檢查暫停狀態

**`asyncio_sleep_with_pause_check(seconds, config_dict)`**
- 取代 `asyncio.sleep()`
- 不需要 tab 物件的純延遲

**`evaluate_with_pause_check(tab, javascript_code, config_dict)`**
- JavaScript 執行前檢查暫停
- 暫停時返回 None

**`with_pause_check(task_func, config_dict, *args, **kwargs)`**
- 包裝長時間任務
- 支援中途暫停

#### 3. 暫停後處理

- 檢測到暫停後應該 `return` 而非 `break`
- 返回值應該表示操作未完成（通常是 `False`）
- 確保函數狀態一致性

### 開發檢查清單

開發 NoDriver 函數時，確保：
- [ ] 函數開始時呼叫 `check_and_handle_pause()`
- [ ] 所有 `tab.sleep()` 改用 `sleep_with_pause_check()`
- [ ] 所有 `asyncio.sleep()` 改用 `asyncio_sleep_with_pause_check()`
- [ ] 長時間迴圈內加入暫停檢查
- [ ] 暫停後返回適當的失敗值（通常是 `False`）
- [ ] 不要直接檢查 `CONST_MAXBOT_INT28_FILE`
- [ ] 確保與 Chrome Driver 版本的功能區隔

### 實作範例

```python
async def nodriver_platform_function(tab, config_dict):
    """
    標準 NoDriver 函數範本
    展示正確的暫停檢查位置
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 1. 函數開始時檢查
    if await check_and_handle_pause(config_dict):
        return False

    # 2. 等待時使用暫停版本
    if await sleep_with_pause_check(tab, 0.6, config_dict):
        if show_debug_message:
            print("Operation paused during wait")
        return False

    # 3. 長迴圈中定期檢查
    for i in range(100):
        if await check_and_handle_pause(config_dict):
            break

        # 執行操作...
        await tab.sleep(0.1)

    return True
```

### 常見錯誤

❌ **錯誤 1：直接檢查檔案**
```python
# 禁止這樣做
if os.path.exists(CONST_MAXBOT_INT28_FILE):
    print("BOT Paused.")
    return False
```

✅ **正確：使用統一函數**
```python
if await check_and_handle_pause(config_dict):
    return False
```

❌ **錯誤 2：在呼叫端重複顯示訊息**
```python
# 禁止這樣做
if await check_and_handle_pause(config_dict):
    print("Paused!")  # 重複顯示
    return False
```

✅ **正確：信任統一函數的訊息處理**
```python
# 訊息已在 check_and_handle_pause() 中處理
if await check_and_handle_pause(config_dict):
    return False
```

❌ **錯誤 3：在 Chrome Driver 版本實作**
```python
# Chrome Driver 不支援暫停機制
def platform_function(driver, config_dict):
    # 不要加入暫停檢查
    pass
```

### 相關文件

- [暫停機制範本](./coding_templates.md#暫停機制標準範本) - 完整實作範例
- [程式結構](./structure.md) - 暫停輔助函數位置

---

## 程式結構保護規則

**重要：修改程式前必須確認不會破壞現有結構**

當修改任何平台功能或共用函式庫時，必須遵循以下流程：

1. **結構查詢優先**
   - 修改任何平台功能前，必須先查看 `/docs/structure.md`
   - 確認函數位置和依賴關係
   - 了解 Chrome 與 NoDriver 版本差異

2. **影響評估**
   - 檢查修改是否影響其他平台
   - 確認不會破壞函數呼叫鏈
   - 評估對共用函式庫的影響
   - 驗證不會影響相依功能的正常運作

3. **跨版本相容性**
   - 確保修改在 Chrome 和 NoDriver 版本都能正常運作
   - 檢查是否需要同步更新兩個版本
   - 保持 API 介面的一致性

## util.py 共用函式庫修改規則

**重要警告：util.py 是所有 WebDriver 類型的共用函式庫**

修改 util.py 時必須遵循以下規則：

1. **強制檢查相容性**
   - 修改 util.py 任何函數前，必須確保 NoDriver 平台正常運作
   - 確保修改不會破壞 Chrome Driver (Selenium/Undetected Chrome) 的功能
   - 優先保證 NoDriver 版本的穩定性

2. **版本相容性原則**
   - 新增功能應該同時支援 NoDriver 和 Chrome Driver
   - NoDriver 特殊格式處理不應影響 Chrome Driver
   - 避免改變函數簽名或返回值格式

3. **測試範圍（優先順序）**
   - nodriver_tixcraft.py (NoDriver) - 優先測試
   - nodriver_kktix.py, nodriver_ticketplus.py, nodriver_ibon.py
   - chrome_tixcraft.py (Selenium/UC) - 確保不破壞
   - 所有平台的核心功能

4. **修改前確認清單**
   - [ ] 查閱對應的 API 指南文件
     - NoDriver: `/docs/nodriver_api_guide.md` - 優先查閱
     - Chrome: `/docs/chrome_api_guide.md`
     - Selenium: `/docs/selenium_api_guide.md`
   - [ ] 查看 `/docs/structure.md` 確認不破壞結構
   - [ ] 閱讀 NoDriver 平台使用該函數的所有位置
   - [ ] 確認修改不會改變現有行為
   - [ ] 測試所有 WebDriver 的資料格式相容性
   - [ ] 驗證所有平台核心功能正常

---

## 開發新平台功能檢查清單

開發新平台支援時，應依據 [ticket_automation_standard.md](./ticket_automation_standard.md) 定義的標準架構實作以下功能。

### 必要功能 (Must Have) - 100% 必須實作

#### 階段 1：主流程控制
- [ ] **主函式** `{platform}_main(driver, url, config_dict)`
  - [ ] 初始化狀態字典 `{platform}_dict`
  - [ ] URL 路由邏輯（根據不同頁面調用不同處理函式）
  - [ ] 頁面類型偵測與分流

#### 階段 4：日期選擇
- [ ] **日期自動選擇** `{platform}_date_auto_select(driver, url, config_dict)`
  - [ ] 讀取 `config_dict["date_auto_select"]["enable"]`
  - [ ] 偵測日期版面類型（按鈕/下拉/日曆）
  - [ ] 取得所有日期選項 `get_all_date_options()`
  - [ ] 關鍵字匹配 `match_date_by_keyword()`（讀取 `date_keyword`）
  - [ ] 回退策略：根據 `mode` 自動選擇（from top/bottom/center/random）
  - [ ] 點擊日期元素 `click_date_element()`
  - [ ] 驗證選擇成功 `verify_date_selected()`

#### 階段 5：區域/座位選擇
- [ ] **區域自動選擇** `{platform}_area_auto_select(driver, url, config_dict)`
  - [ ] 讀取 `config_dict["area_auto_select"]["enable"]`
  - [ ] 偵測區域版面類型
  - [ ] 取得所有區域選項 `get_all_area_options()`
  - [ ] 套用排除關鍵字 `apply_exclude_keywords()`（讀取 `keyword_exclude`）
  - [ ] 關鍵字匹配 `match_area_by_keyword()`（讀取 `area_keyword`）
  - [ ] 回退策略：根據 `mode` 自動選擇
  - [ ] 點擊區域元素 `click_area_element()`
  - [ ] 座位圖處理（若適用）`handle_seat_map()`

#### 階段 6：票數設定
- [ ] **票數自動設定** `{platform}_assign_ticket_number(driver, config_dict)`
  - [ ] 讀取 `config_dict["ticket_number"]`
  - [ ] 偵測票數版面類型（下拉/輸入框/按鈕/價格清單）
  - [ ] 取得票種清單 `get_ticket_types()`
  - [ ] 選擇票數 `select_ticket_number()`
  - [ ] 驗證票數設定 `verify_ticket_selected()`

#### 階段 9：同意條款
- [ ] **同意條款處理** `{platform}_ticket_agree(driver, config_dict)`
  - [ ] 找到同意條款元素 `find_agreement_elements()`
  - [ ] 勾選所有條款 `check_all_agreements()`
  - [ ] 處理特殊對話框（若有）
  - [ ] 驗證條款已勾選 `verify_agreements_checked()`

#### 階段 10：訂單送出
- [ ] **訂單確認送出** `{platform}_ticket_main(driver, config_dict)` 或 `{platform}_order()`
  - [ ] 檢視訂單詳情 `review_order_details()`
  - [ ] 找到送出按鈕 `find_submit_button()`
  - [ ] 點擊送出按鈕 `click_submit_button()`
  - [ ] 處理確認對話框 `handle_confirmation_dialog()`
  - [ ] 播放音效通知（若啟用）`play_sound_notification()`
  - [ ] 驗證訂單送出 `verify_order_submitted()`

### 重要功能 (Should Have) - 建議實作 80%

#### 階段 2：身份認證
- [ ] **自動登入** `{platform}_login(driver, config_dict)`
  - [ ] 檢查登入狀態 `check_login_status()`
  - [ ] 偵測登入方式（Cookie/帳密）
  - [ ] Cookie 注入（若平台支援）`inject_cookies()`
  - [ ] 帳號密碼填寫 `fill_credentials()`
  - [ ] 驗證登入成功 `verify_login_success()`

#### 階段 3：頁面監控
- [ ] **彈窗處理** `{platform}_close_popup_windows(driver)`
  - [ ] 偵測彈窗類型
  - [ ] 關閉廣告彈窗
  - [ ] 接受 Cookie 同意
  - [ ] 處理平台特定彈窗

#### 階段 7：驗證碼處理
- [ ] **驗證碼自動處理** `{platform}_auto_ocr(driver, config_dict)`
  - [ ] 偵測驗證碼類型
  - [ ] 取得驗證碼圖片 `get_captcha_image()`（讀取 `image_source`）
  - [ ] OCR 辨識 `ocr_recognize()`（讀取 `ocr_captcha.enable`, `beta`）
  - [ ] 輸入驗證碼 `input_captcha_code()`
  - [ ] 送出或等待（讀取 `force_submit`）
  - [ ] 重新載入驗證碼 `reload_captcha()`
  - [ ] 手動輸入回退 `manual_input_fallback()`

#### 階段 12：錯誤處理
- [ ] **錯誤日誌與重試**
  - [ ] 在所有關鍵函式加入 try-except
  - [ ] 記錄錯誤訊息（若 `verbose=true`）
  - [ ] 實作重試機制（關鍵操作）
  - [ ] 偵測售完狀態 `{platform}_check_sold_out()`

### 選擇性功能 (Nice to Have) - 依需求實作

#### 階段 8：表單填寫
- [ ] **表單自動填寫** `{platform}_form_auto_fill(driver, config_dict)`（若平台有自訂問題）
  - [ ] 偵測表單欄位
  - [ ] 填寫個人資訊
  - [ ] 處理自訂問題（讀取 `user_guess_string`）

#### 階段 11：排隊處理
- [ ] **排隊狀態處理** `{platform}_handle_queue(driver, config_dict)`（若平台有排隊機制）
  - [ ] 偵測排隊頁面
  - [ ] 解析排隊資訊
  - [ ] 監控排隊狀態
  - [ ] 處理排隊逾時

### 平台特定功能 (Platform Specific)

依據平台特性實作以下功能：

- [ ] **實名制處理** `{platform}_accept_realname_card()`（如 TicketPlus）
- [ ] **展開式面板** `{platform}_order_expansion_panel()`（如 TicketPlus）
- [ ] **密碼輸入** `{platform}_date_password_input()`（如 HKTicketing）
- [ ] **iframe 處理** `{platform}_travel_iframe()`（如 HKTicketing）
- [ ] **問卷調查** `{platform}_auto_survey()`（如 Urbtix）
- [ ] **座位圖選座** `{platform}_seat_auto_select()`（如 年代售票）
- [ ] **最佳座位算法** `{platform}_find_best_seats()`（如 年代售票）

### 檢查清單使用方式

1. **開發前**：複製此檢查清單，勾選需要實作的功能
2. **開發中**：完成一項勾選一項，確保不遺漏關鍵功能
3. **開發後**：對照檢查清單進行自我審查
4. **測試時**：根據檢查清單設計測試案例

---

## 函式拆分原則

### 基本原則

#### 1. 單一職責原則 (Single Responsibility Principle)

**定義**：每個函式只負責一個明確的任務

**範例 ✅ 良好**：
```python
def get_all_date_options(driver):
    """只負責取得所有日期選項"""
    return driver.find_elements(By.CSS_SELECTOR, ".date-option")

def filter_sold_out_dates(dates, config_dict):
    """只負責過濾售完日期"""
    if config_dict["tixcraft"]["pass_date_is_sold_out"]:
        return [d for d in dates if "售完" not in d.text]
    return dates

def match_date_by_keyword(dates, keyword):
    """只負責關鍵字匹配"""
    for date in dates:
        if keyword in date.text:
            return date
    return None
```

**範例 ❌ 不良**：
```python
def get_and_filter_and_match_dates(driver, config_dict, keyword):
    """混合了三個職責：取得、過濾、匹配"""
    dates = driver.find_elements(By.CSS_SELECTOR, ".date-option")
    if config_dict["tixcraft"]["pass_date_is_sold_out"]:
        dates = [d for d in dates if "售完" not in d.text]
    for date in dates:
        if keyword in date.text:
            return date
    return None
```

**判斷標準**：
- 函式名稱中有 "and" 或 "或"：通常違反單一職責
- 函式內有多個獨立的邏輯區塊：考慮拆分
- 修改一個功能需要改動多處：違反單一職責

---

#### 2. 可組合性原則 (Composability Principle)

**定義**：小函式可以組合成大函式，形成清晰的工作流程

**範例 ✅ 良好**：
```python
def tixcraft_date_auto_select(driver, url, config_dict):
    """主函式組合多個小函式，形成完整流程"""
    # Step 1: 取得所有日期
    dates = get_all_date_options(driver)

    # Step 2: 過濾售完日期
    dates = filter_sold_out_dates(dates, config_dict)

    # Step 3: 優先用關鍵字匹配
    keyword = config_dict["date_auto_select"]["date_keyword"]
    target = match_date_by_keyword(dates, keyword)

    # Step 4: 若未匹配，使用 mode 回退
    if not target:
        mode = config_dict["date_auto_select"]["mode"]
        target = fallback_select_by_mode(dates, mode)

    # Step 5: 點擊選中的日期
    return click_date_element(driver, target)
```

**優點**：
- 流程清晰易讀
- 每個步驟可獨立測試
- 容易修改或替換某個步驟
- 可重用子函式

---

#### 3. 明確的輸入輸出 (Clear Input/Output)

**定義**：函式的參數和返回值應該類型明確，並有清楚的文檔

**範例 ✅ 良好**：
```python
def match_date_by_keyword(dates: list, keyword: str) -> element:
    """
    根據關鍵字匹配日期

    Args:
        dates (list): WebElement 列表，包含所有日期元素
        keyword (str): 要匹配的關鍵字，例如 "10/03"

    Returns:
        WebElement: 匹配到的日期元素
        None: 若未匹配到任何日期

    Raises:
        ValueError: 若 dates 為空列表
    """
    if not dates:
        raise ValueError("dates list is empty")

    for date in dates:
        if keyword in date.text:
            return date
    return None
```

**文檔要素**：
- 功能描述（一句話說明）
- 參數說明（類型、意義、範例）
- 返回值說明（類型、意義、特殊情況）
- 異常說明（可能拋出的異常）

---

#### 4. 設定驅動原則 (Configuration-Driven)

**定義**：函式行為由設定控制，避免寫死在程式碼中

**範例 ✅ 良好**：
```python
def select_by_mode(items: list, mode: str) -> element:
    """根據 mode 設定選擇項目"""
    if mode == "from top to bottom":
        return items[0]
    elif mode == "from bottom to top":
        return items[-1]
    elif mode == "center":
        return items[len(items) // 2]
    elif mode == "random":
        return random.choice(items)
    else:
        raise ValueError(f"Unknown mode: {mode}")
```

**範例 ❌ 不良**：
```python
def select_item(items: list) -> element:
    """永遠選第一個，無法配置"""
    return items[0]
```

**優點**：
- 使用者可透過 settings.json 調整行為
- 不需修改程式碼即可改變邏輯
- 方便測試不同策略

---

#### 5. 錯誤處理原則 (Error Handling)

**定義**：每個函式都應該妥善處理可能的錯誤，並提供回退方案

**範例 ✅ 良好**：
```python
def click_element_safe(driver, element, config_dict):
    """
    安全點擊元素，包含多種回退方案

    嘗試順序：
    1. Selenium 原生點擊
    2. JavaScript 點擊
    3. CDP 點擊（NoDriver）
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 方案 1: Selenium 原生點擊
    try:
        element.click()
        return True
    except ElementClickInterceptedException as exc:
        if show_debug_message:
            print(f"Selenium click intercepted: {exc}")

    # 方案 2: JavaScript 點擊
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as exc:
        if show_debug_message:
            print(f"JavaScript click failed: {exc}")

    # 方案 3: 記錄完全失敗
    if show_debug_message:
        print("All click methods failed")
    return False
```

**錯誤處理檢查清單**：
- [ ] 使用 try-except 包裹可能出錯的操作
- [ ] 提供有意義的錯誤訊息（若 verbose=true）
- [ ] 實作回退方案（多種嘗試方法）
- [ ] 返回明確的成功/失敗狀態（bool 或 None）
- [ ] 不要吞掉異常（至少記錄日誌）

---

### 拆分實戰範例

#### 範例 1：日期選擇功能拆分

**原始大函式（不良）**：
```python
def tixcraft_date_auto_select(driver, url, config_dict):
    """一個超過 200 行的巨大函式，混合了所有邏輯"""
    # ... 100+ 行代碼混雜在一起 ...
```

**拆分後（良好）**：
```python
# 主函式（30 行）
def tixcraft_date_auto_select(driver, url, config_dict):
    dates = get_all_date_options(driver)
    dates = filter_sold_out_dates(dates, config_dict)
    target = match_date_by_keyword(dates, config_dict) or \
             fallback_select_by_mode(dates, config_dict["date_auto_select"]["mode"])
    return click_date_element(driver, target)

# 子函式 1（10 行）
def get_all_date_options(driver):
    return driver.find_elements(By.CSS_SELECTOR, ".date-option")

# 子函式 2（8 行）
def filter_sold_out_dates(dates, config_dict):
    if config_dict["tixcraft"]["pass_date_is_sold_out"]:
        return [d for d in dates if "售完" not in d.text]
    return dates

# 子函式 3（15 行）
def match_date_by_keyword(dates, config_dict):
    keyword = config_dict["date_auto_select"]["date_keyword"]
    if not keyword:
        return None
    for date in dates:
        if keyword in date.text:
            return date
    return None

# 子函式 4（12 行）
def fallback_select_by_mode(dates, mode):
    if mode == "from top to bottom":
        return dates[0]
    elif mode == "from bottom to top":
        return dates[-1]
    # ... 其他 mode
```

**拆分效果**：
- 原函式 200+ 行 → 4 個函式各 8-30 行
- 每個函式職責清晰
- 可獨立測試每個函式
- 容易理解和維護

---

#### 範例 2：驗證碼處理功能拆分

**拆分策略**：

```
tixcraft_captcha()  # 主控制器
├── detect_captcha_type()  # 偵測類型
├── get_captcha_image()  # 取得圖片
│   ├── get_from_canvas()  # 從 Canvas 取得
│   └── get_from_img_tag()  # 從 img 標籤取得
├── ocr_recognize()  # OCR 辨識
│   ├── use_ddddocr()  # 使用標準模型
│   └── use_beta_model()  # 使用 beta 模型
├── input_captcha_code()  # 輸入驗證碼
└── retry_if_failed()  # 失敗重試
```

**實作**：
```python
def tixcraft_captcha(driver, config_dict):
    """驗證碼處理主函式"""
    captcha_type = detect_captcha_type(driver)

    if captcha_type == "image":
        image_source = config_dict["ocr_captcha"]["image_source"]
        image_data = get_captcha_image(driver, image_source)

        use_beta = config_dict["ocr_captcha"]["beta"]
        captcha_text = ocr_recognize(image_data, use_beta)

        input_captcha_code(driver, captcha_text)

        force_submit = config_dict["ocr_captcha"]["force_submit"]
        if force_submit:
            return submit_form(driver)
        else:
            return wait_for_manual_confirm(driver)

    return False
```

---

### 拆分時機判斷

**何時應該拆分函式？**

| 指標 | 建議拆分閾值 | 說明 |
|-----|------------|------|
| 函式行數 | > 50 行 | 考慮拆分成多個小函式 |
| 巢狀層級 | > 3 層 | 內層邏輯抽取為子函式 |
| 重複代碼 | 出現 2 次以上 | 抽取為共用函式 |
| 註解區塊 | 有明顯分段註解 | 每段抽取為函式 |
| 條件分支 | > 5 個 if-elif | 考慮使用字典映射或策略模式 |

**拆分檢查清單**：
- [ ] 函式是否只做一件事？
- [ ] 函式名稱是否能準確描述功能？
- [ ] 函式是否有清楚的輸入輸出？
- [ ] 函式是否可以獨立測試？
- [ ] 函式是否可以被其他地方重用？

---

### 命名規範

#### 函式命名模式

| 類型 | 命名模式 | 範例 |
|-----|---------|------|
| NoDriver 平台主函式（推薦） | `async nodriver_{platform}_main()` | `async nodriver_tixcraft_main()` |
| NoDriver 平台功能函式（推薦） | `async nodriver_{platform}_{function}()` | `async nodriver_kktix_date_auto_select()` |
| Chrome Driver 平台主函式 | `{platform}_main()` | `tixcraft_main()` |
| Chrome Driver 平台功能函式 | `{platform}_{function}()` | `kktix_date_auto_select()` |
| 通用工具函式 | `{function}()` | `find_element_safe()` |
| 內部輔助函式 | `_{function}()` | `_parse_date_text()` |

#### 動詞選擇指南

| 動作類型 | 推薦動詞 | 範例 |
|---------|---------|------|
| 取得資料 | `get_`, `fetch_`, `retrieve_` | `get_all_date_options()` |
| 解析資料 | `parse_`, `extract_` | `parse_area_name()` |
| 偵測狀態 | `detect_`, `check_`, `is_`, `has_` | `detect_date_layout()` |
| 查找元素 | `find_`, `locate_` | `find_agreement_elements()` |
| 過濾資料 | `filter_`, `exclude_` | `filter_sold_out_dates()` |
| 匹配資料 | `match_`, `compare_` | `match_date_by_keyword()` |
| 操作元素 | `click_`, `input_`, `select_`, `fill_` | `click_date_element()` |
| 驗證結果 | `verify_`, `validate_`, `ensure_` | `verify_date_selected()` |
| 處理邏輯 | `handle_`, `process_`, `manage_` | `handle_captcha()` |
| 執行動作 | `execute_`, `perform_`, `run_` | `execute_javascript()` |
| 自動化操作 | `auto_` | `auto_reload_page()` |

---

**更新日期**: 2025-10-28
**相關文件**: [標準功能定義](./ticket_automation_standard.md) | [專案概覽](./project_overview.md) | [程式碼範本](./coding_templates.md) | [函數架構](./structure.md)