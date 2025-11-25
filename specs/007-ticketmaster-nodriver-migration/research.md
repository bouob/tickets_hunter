# 技術研究：Ticketmaster.com NoDriver 遷移

**研究日期**: 2025-11-15
**專案**: Tickets Hunter - 多平台搶票自動化系統
**分支**: 007-ticketmaster-nodriver-migration

---

## 目錄

1. [Chrome Driver 版本現有實作分析](#1-chrome-driver-版本現有實作分析)
2. [zone_info JSON 資料結構](#2-zone_info-json-資料結構)
3. [NoDriver 最佳實踐](#3-nodriver-最佳實踐)
4. [Selenium → NoDriver API 對應表](#4-selenium--nodriver-api-對應表)
5. [關鍵技術決策總結](#5-關鍵技術決策總結)

---

## 1. Chrome Driver 版本現有實作分析

### 函數 1: `ticketmaster_date_auto_select()`

**位置**: `src/chrome_tixcraft.py:1274-1395`

**決策**: 使用 CSS 選擇器定位日期列表，透過關鍵字匹配選擇目標日期
**理由**: Ticketmaster 使用標準的 DOM 結構，日期資訊直接在 HTML 中可見
**Selenium API 使用**:
- `driver.find_elements(By.CSS_SELECTOR, '#list-view > div > div.event-listing > div.accordion-wrapper > div')` - 找到所有日期區塊
- `row.get_attribute('innerHTML')` - 取得每個日期區塊的 HTML
- `press_button(target_area, By.CSS_SELECTOR, 'a')` - 點擊選中的日期連結
- `driver.window_handles` - 處理新分頁
- `driver.switch_to.window()` / `driver.close()` - 分頁切換與關閉
- `driver.refresh()` - 自動重載頁面

**選擇器**:
- 日期列表: `#list-view > div > div.event-listing > div.accordion-wrapper > div`
- 日期連結: `a` (在父元素內)

**核心邏輯**:
1. 找到所有日期區塊
2. 過濾掉不含 "See Tickets" 的區塊
3. 過濾掉已售完的區塊（根據設定 `pass_date_is_sold_out`）
4. 使用關鍵字匹配目標日期
5. 根據 `auto_select_mode` 選擇目標日期（從上到下/從下到上/隨機）
6. 點擊日期連結
7. 處理可能彈出的新分頁（切換回主分頁並關閉新分頁）
8. 若未匹配到日期且開啟 `auto_reload_coming_soon_page`，則自動重載頁面

**考慮過的替代方案**:
- 使用 XPath 定位: 可行，但 CSS 選擇器更簡潔
- 直接執行 JavaScript 點擊: 可行，但標準的 Selenium 點擊更穩定

---

### 函數 2: `get_ticketmaster_target_area()`

**位置**: `src/chrome_tixcraft.py:1516-1596`

**決策**: 從 JSON 物件 `zone_info` 中提取區域資訊並匹配關鍵字
**理由**: Ticketmaster 使用 JavaScript 變數儲存區域資訊，不依賴 DOM 元素
**Selenium API 使用**: 無（純數據處理）

**核心邏輯**:
1. 遍歷 `zone_info` 字典的每個區域
2. 檢查 `zone_info[row]["areaStatus"]` 是否為 "UNAVAILABLE"
3. 組合區域文字: `groupName + description + price[0].ticketPrice`
4. 使用 `util.format_keyword_string()` 格式化關鍵字
5. 匹配關鍵字（支援空白分隔的多關鍵字 AND 邏輯）
6. 返回匹配的區域 ID 列表

**zone_info 欄位**:
- `areaStatus`: "AVAILABLE" / "UNAVAILABLE"
- `groupName`: 區域名稱
- `description`: 區域描述
- `price[0].ticketPrice`: 票價

**考慮過的替代方案**:
- 從 DOM 元素提取區域資訊: 不可行，Ticketmaster 使用 JavaScript 渲染，資訊儲存在 JS 變數中

---

### 函數 3: `ticketmaster_area_auto_select()`

**位置**: `src/chrome_tixcraft.py:1665-1720`

**決策**: 使用 JavaScript 執行區域點擊 `areaTicket()`
**理由**: Ticketmaster 的區域選擇是透過 JavaScript 函數觸發，而非 DOM 元素點擊
**Selenium API 使用**:
- `driver.execute_script('areaTicket("%s", "map");' % target_area)` - 執行 JavaScript 函數

**選擇器**: 無（直接執行 JavaScript）

**核心邏輯**:
1. 解析 `area_keyword` JSON 陣列
2. 遍歷每個關鍵字，調用 `get_ticketmaster_target_area()` 匹配區域
3. 如果找到匹配區域，取得目標區域 ID（根據 `auto_select_mode`）
4. 執行 JavaScript: `areaTicket("<zone_id>", "map");`
5. 若未找到區域且需要重載，執行 `driver.refresh()`

**考慮過的替代方案**:
- 點擊 DOM 元素: 不可行，區域是 SVG 圖片上的區塊，需要 JavaScript 觸發
- 模擬滑鼠點擊座標: 不穩定，座標會隨頁面大小變化

---

### 函數 4: `ticketmaster_parse_zone_info()`

**位置**: `src/chrome_tixcraft.py:5808-5862`

**決策**: 從 `#mapSelectArea` 元素的 `innerHTML` 中提取 JavaScript 變數 `zone`
**理由**: Ticketmaster 將區域資訊嵌入在 HTML 的 `<script>` 標籤中
**Selenium API 使用**:
- `driver.find_element(By.CSS_SELECTOR, '#mapSelectArea')` - 定位包含 zone 資訊的元素
- `mapSelectArea.get_attribute('innerHTML')` - 取得 innerHTML

**選擇器**: `#mapSelectArea`

**核心邏輯**:
1. 定位 `#mapSelectArea` 元素
2. 取得 `innerHTML`
3. 使用字串分割提取 `var zone = {...}` 之間的 JSON 字串
   - 開始標記: `"var zone ="`
   - 結束標記: `"fieldImageType"`
4. 清理尾部逗號與換行符
5. 使用 `json.loads()` 解析 JSON
6. 調用 `ticketmaster_area_auto_select()` 執行區域選擇

**JSON 提取邏輯**:
```python
zone_string = mapSelectArea_html.split("var zone =")[1]
zone_string = zone_string.split("fieldImageType")[0]
zone_string = zone_string.strip()
if zone_string[-1:] == "\n":
    zone_string = zone_string[:-1]
zone_string = zone_string.strip()
if zone_string[-1:] == ",":
    zone_string = zone_string[:-1]
```

**考慮過的替代方案**:
- 使用 `driver.execute_script('return zone;')`: 可行，但 `zone` 是局部變數，可能無法直接存取
- 使用正則表達式提取: 可行，但字串分割更簡單穩定

---

### 函數 5: `ticketmaster_get_ticketPriceList()`

**位置**: `src/chrome_tixcraft.py:5864-5908`

**決策**: 檢查頁面載入狀態後嘗試定位 `#ticketPriceList` 表格
**理由**: Ticketmaster 使用載入動畫，需要等待載入完成後才能操作票數選擇
**Selenium API 使用**:
- `driver.find_element(By.CSS_SELECTOR, '#mapContainer')` - 檢查地圖容器存在
- `driver.find_element(By.CSS_SELECTOR, '#loadingmap')` - 檢查載入動畫
- `driver.find_element(By.CSS_SELECTOR, '#ticketPriceList')` - 定位票價表格

**選擇器**:
- `#mapContainer` - 地圖容器
- `#loadingmap` - 載入動畫
- `#ticketPriceList` - 票價表格

**核心邏輯**:
1. 檢查 `#mapContainer` 是否存在
2. 檢查 `#loadingmap` 是否存在（判斷是否正在載入）
3. 若未載入，嘗試定位 `#ticketPriceList`
4. 若 `#ticketPriceList` 不存在，回退到 `ticketmaster_parse_zone_info()` 使用區域地圖選擇

**考慮過的替代方案**:
- 使用顯式等待: 可行，但專案統一使用條件檢查 + 回退策略
- 直接操作區域地圖: 作為回退方案已實作

---

### 函數 6: `ticketmaster_assign_ticket_number()`

**位置**: `src/chrome_tixcraft.py:5910-5977`

**決策**: 從 `#ticketPriceList` 中找到 `<select>` 元素並設定票數
**理由**: Ticketmaster 使用標準的 HTML `<select>` 元素控制票數
**Selenium API 使用**:
- `ticketmaster_get_ticketPriceList()` - 取得票價表格
- `table_select.find_element(By.CSS_SELECTOR, 'select')` - 定位下拉選單
- `form_select.is_enabled()` - 檢查元素可見性
- `Select(form_select)` - 建立 Select 物件
- `select_obj.first_selected_option.text` - 檢查當前選擇
- `ticket_number_select_fill()` - 設定票數（使用 `select_by_visible_text()`）
- `press_button(driver, By.CSS_SELECTOR, '#autoMode')` - 點擊自動模式按鈕

**選擇器**:
- `select` (在 `#ticketPriceList` 內)
- `#autoMode` - 自動模式按鈕

**核心邏輯**:
1. 調用 `ticketmaster_get_ticketPriceList()` 取得表格
2. 在表格中定位 `<select>` 元素
3. 檢查元素是否可用（`is_enabled()`）
4. 檢查當前選擇的值是否已設定（避免重複設定）
5. 使用 `Select.select_by_visible_text()` 設定票數
6. 點擊 `#autoMode` 按鈕觸發後續流程

**考慮過的替代方案**:
- 使用 JavaScript 直接設定 value: 可行，但標準的 Select API 更穩定
- 使用 `select_by_value()`: 可行，但文字選擇更直觀

---

### 函數 7: `ticketmaster_promo()`

**位置**: `src/chrome_tixcraft.py:1937-1939`

**決策**: 封裝調用 `tixcraft_input_check_code()` 處理 Promo Code 驗證
**理由**: Ticketmaster 的 Promo Code 驗證與 TixCraft 的驗證碼邏輯相同
**Selenium API 使用**: 繼承自 `tixcraft_input_check_code()`

**選擇器**: `#promoBox`

**核心邏輯**:
1. 設定問題選擇器為 `#promoBox`
2. 調用 `tixcraft_input_check_code()` 處理驗證
3. 返回 `fail_list`（記錄失敗的答案）

**tixcraft_input_check_code() 核心邏輯** (Line 1945-1980):
1. 從 `question_selector` 取得問題文字
2. 將問題寫入 `question.txt` 檔案
3. 從使用者設定或自動推測取得答案列表
4. 過濾掉 `fail_list` 中的答案
5. 調用 `fill_common_verify_form()` 填寫答案並提交

**考慮過的替代方案**:
- 單獨實作 Promo Code 處理: 不必要，邏輯完全相同

---

### 函數 8: `ticketmaster_captcha()`

**位置**: `src/chrome_tixcraft.py:5979-6016`

**決策**: 重用 TixCraft 的驗證碼處理邏輯（`tixcraft_auto_ocr()` / `tixcraft_keyin_captcha_code()`）
**理由**: Ticketmaster 與 TixCraft 使用相同的驗證碼系統
**Selenium API 使用**:
- `check_checkbox(driver, By.CSS_SELECTOR, '#TicketForm_agree')` - 勾選同意條款
- `tixcraft_keyin_captcha_code(driver)` - 手動輸入驗證碼（OCR 關閉時）
- `tixcraft_auto_ocr()` - 自動 OCR 辨識驗證碼

**選擇器**:
- `#TicketForm_agree` - 同意條款 checkbox

**核心邏輯**:
1. 勾選同意條款 checkbox（重試 2 次）
2. 檢查 `config_dict["ocr_captcha"]["enable"]`
   - **OCR 關閉**: 調用 `tixcraft_keyin_captcha_code()` 等待手動輸入
   - **OCR 開啟**: 循環調用 `tixcraft_auto_ocr()` 自動辨識（最多 99 次）
3. 如果表單已提交或 URL 改變，跳出循環

**考慮過的替代方案**:
- 單獨實作驗證碼處理: 不必要，邏輯完全相同

---

## 2. zone_info JSON 資料結構

### 決策: 完整保留 Chrome Driver 版本的 JSON 結構

**理由**: zone_info 是 Ticketmaster 伺服器端提供的標準資料格式，不應修改

### 必要欄位

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",           // 區域狀態: "AVAILABLE" / "UNAVAILABLE"
    "groupName": "VIP區",                 // 區域名稱
    "description": "最佳視野",            // 區域描述
    "price": [
      {
        "ticketPrice": "3500"             // 票價（字串格式）
      }
    ]
  },
  "zone_2": {
    "areaStatus": "UNAVAILABLE",
    "groupName": "一般區",
    "description": "標準座位",
    "price": [
      {
        "ticketPrice": "1500"
      }
    ]
  }
}
```

### 提取方法

**決策**: 從 `#mapSelectArea` 的 `innerHTML` 中提取 JavaScript 變數 `zone`
**理由**: 這是 Ticketmaster 唯一提供區域資訊的方式

**HTML 結構範例**:
```html
<div id="mapSelectArea">
  <script>
    var zone = {
      "zone_1": {"areaStatus": "AVAILABLE", "groupName": "VIP區", ...},
      "zone_2": {"areaStatus": "UNAVAILABLE", "groupName": "一般區", ...},
    };
    var fieldImageType = "map";
  </script>
</div>
```

**提取邏輯**:
1. 定位 `#mapSelectArea` 元素
2. 取得 `innerHTML`
3. 字串分割:
   - 開始標記: `"var zone ="`
   - 結束標記: `"fieldImageType"`
4. 清理 JSON 字串（移除尾部逗號與換行符）
5. 使用 `json.loads()` 解析

**健壯性處理**:
- **尾部逗號**: JavaScript 允許，但 JSON 標準不允許 → 需移除
- **換行符**: 可能包含 `\n` → 需 `strip()`
- **JSON 解析失敗**: 捕獲 `Exception`，輸出錯誤訊息

**NoDriver 實作考量**:
- 使用 `tab.evaluate()` 直接執行 JavaScript 取得 `zone` 變數（推薦）
- 或使用 `tab.query_selector()` + `element.get_attribute('innerHTML')` 後字串處理

### 考慮過的替代方案

1. **從 API 請求取得**: 不可行，zone_info 是伺服器端渲染時注入的靜態資料，無單獨 API
2. **從 SVG 圖片解析座位區域**: 不可行，SVG 只有視覺資訊，無區域名稱與狀態
3. **從 Cookie 或 localStorage**: 不可行，zone_info 不儲存在客戶端儲存中

---

## 3. NoDriver 最佳實踐

### 元素定位

**決策**: 優先使用 `tab.query_selector()` 或 `tab.evaluate()` 執行 JavaScript
**理由**: NoDriver 的 `query_selector()` 簡潔穩定，適合標準 DOM 查詢

**範例代碼**:
```python
# 方法 1: NoDriver 高階 API（推薦）
element = await tab.query_selector('#mapSelectArea')
if element:
    innerHTML = await element.get_attribute('innerHTML')

# 方法 2: JavaScript Evaluate（適合快速查詢）
result = await tab.evaluate('''
    (function() {
        const el = document.querySelector('#mapSelectArea');
        return el ? el.innerHTML : null;
    })();
''')
```

**考慮過的替代方案**:
- 使用 CDP `DOM.querySelector`: 可行，但過於底層，不適合簡單查詢
- 使用 XPath: 可行，但 CSS 選擇器更簡潔

### 元素互動

**決策**: 優先使用 NoDriver 的 `element.click()`，回退到 CDP `Input.dispatchMouseEvent()`
**理由**: `element.click()` 簡潔穩定，CDP 作為精確控制的回退方案

**範例代碼**:
```python
# 方法 1: NoDriver 高階 API（推薦）
element = await tab.query_selector('a.date-link')
if element:
    await element.click()

# 方法 2: CDP 精確點擊（適合需要座標控制的場景）
from nodriver import cdp

# 取得元素位置
box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
x = (box_model.content[0] + box_model.content[2]) / 2
y = (box_model.content[1] + box_model.content[5]) / 2

# 執行點擊
await tab.mouse_click(x, y)
```

**專案現有實作參考**:
- `nodriver_kktix_press_next_button()` (Line 1863): 使用 `element.click()`
- `nodriver_ibon_date_auto_select_pierce()` (Line 7662): 使用 CDP `mouse_click()`

**考慮過的替代方案**:
- JavaScript `element.click()`: 可行，但容易被反爬蟲偵測
- CDP `Runtime.callFunctionOn()`: 可行，但過於複雜

### JavaScript 執行

**決策**: 使用 `tab.evaluate()` 執行 JavaScript 並取得回傳值
**理由**: `evaluate()` 是 NoDriver 推薦的標準方法，支援複雜邏輯與回傳值

**範例代碼**:
```python
# 執行 JavaScript 並取得回傳值
result = await tab.evaluate('''
    (function() {
        // 直接存取 JavaScript 變數（如果在全域作用域）
        if (typeof zone !== 'undefined') {
            return zone;
        }

        // 或從 DOM 元素提取
        const el = document.querySelector('#mapSelectArea');
        if (!el) return null;

        const html = el.innerHTML;
        const match = html.match(/var zone = ({[\\s\\S]*?});/);
        if (!match) return null;

        return JSON.parse(match[1]);
    })();
''')

if result:
    zone_info = result  # 已經是 Python 字典，無需再次解析
```

**健壯性處理**:
- 使用 IIFE `(function() {...})()` 避免污染全域作用域
- 檢查元素存在性（`if (!el) return null`）
- 捕獲 JSON 解析錯誤

**考慮過的替代方案**:
- 使用 CDP `Runtime.evaluate()`: 可行，但 `tab.evaluate()` 已封裝，更簡潔

### 等待元素載入

**決策**: 使用 JavaScript Promise 實作條件等待，或使用 `tab.sleep()` 配合輪詢
**理由**: NoDriver 沒有內建的 `wait_for()`（不穩定），需自行實作

**範例代碼**:
```python
# 方法 1: JavaScript Promise 條件等待（推薦）
result = await tab.evaluate(f'''
    (function() {{
        return new Promise((resolve) => {{
            let retryCount = 0;
            const maxRetries = 50;  // 10 秒 (50 * 200ms)

            function checkElement() {{
                const element = document.querySelector('#ticketPriceList');
                const loadingElement = document.querySelector('#loadingmap');

                // 檢查元素存在且載入動畫消失
                if (element && !loadingElement) {{
                    resolve({{ success: true, found: true }});
                    return;
                }}

                if (retryCount < maxRetries) {{
                    retryCount++;
                    setTimeout(checkElement, 200);
                }} else {{
                    resolve({{ success: false, error: "Timeout" }});
                }}
            }}

            checkElement();
        }});
    }})();
''')

# 方法 2: Python 輪詢（適合簡單場景）
for _ in range(50):  # 最多等待 10 秒
    element = await tab.query_selector('#ticketPriceList')
    loading = await tab.query_selector('#loadingmap')
    if element and not loading:
        break
    await tab.sleep(0.2)
```

**專案現有實作參考**:
- `nodriver_api_guide.md` Line 624-655: JavaScript Promise 條件等待範例

**考慮過的替代方案**:
- 使用 `tab.wait_for()`: 不推薦，官方文件標註為不穩定
- 固定 `sleep()`: 不推薦，浪費時間且不可靠

---

## 4. Selenium → NoDriver API 對應表

| Selenium API | NoDriver 對應 | 說明 | 備註 |
|--------------|---------------|------|------|
| `driver.find_element(By.CSS_SELECTOR, "selector")` | `await tab.query_selector("selector")` | 定位單個元素 | NoDriver 返回 Element 物件或 None |
| `driver.find_elements(By.CSS_SELECTOR, "selector")` | `await tab.query_selector_all("selector")` | 定位多個元素 | 返回 Element 列表 |
| `element.click()` | `await element.click()` | 點擊元素 | NoDriver 原生支援 |
| `element.send_keys("text")` | `await element.send_keys("text")` | 輸入文字 | NoDriver 原生支援 |
| `element.get_attribute("attr")` | `await element.get_attribute("attr")` | 取得屬性 | NoDriver 原生支援 |
| `element.text` | `await element.text` | 取得文字內容 | NoDriver 需要 await |
| `element.is_enabled()` | `await tab.evaluate('!el.disabled', el=element)` | 檢查元素可用性 | 需要 JavaScript |
| `driver.execute_script("js", element)` | `await tab.evaluate("js")` | 執行 JavaScript | NoDriver 支援參數傳遞 |
| `driver.execute_script("return zone;")` | `await tab.evaluate("return zone;")` | 執行 JS 並取得回傳值 | 直接返回 Python 物件 |
| `driver.window_handles` | `driver.tabs` | 取得所有分頁 | NoDriver 使用 `tabs` 屬性 |
| `driver.switch_to.window(handle)` | `await tab.activate()` | 切換分頁 | NoDriver 直接操作 Tab 物件 |
| `driver.close()` | `await tab.close()` | 關閉分頁 | NoDriver 原生支援 |
| `driver.refresh()` | `await tab.reload()` | 重新載入頁面 | NoDriver 原生支援 |
| `Select(element)` | 無對應 API | 下拉選單操作 | 需使用 JavaScript 或 CDP |
| `select.select_by_visible_text("text")` | `await tab.evaluate('el.value = "value"; el.dispatchEvent(new Event("change"))', el=element)` | 設定下拉選單 | 使用 JavaScript 模擬 |
| `driver.get_cookies()` | `await driver.cookies.get_all()` | 取得所有 Cookie | NoDriver API |
| `driver.add_cookie(cookie_dict)` | `await driver.cookies.set_all([cookie])` | 設定 Cookie | NoDriver 使用 `CookieParam` 物件 |

### JavaScript 執行補充

**Selenium**:
```python
# 執行 JavaScript 並取得回傳值
result = driver.execute_script("return document.title;")

# 傳遞參數
driver.execute_script("arguments[0].click();", element)
```

**NoDriver**:
```python
# 執行 JavaScript 並取得回傳值
result = await tab.evaluate("return document.title;")

# 傳遞參數
result = await tab.evaluate("el.click();", el=element)
```

### Select 下拉選單操作

**Selenium**:
```python
from selenium.webdriver.support.ui import Select

select_element = driver.find_element(By.CSS_SELECTOR, "select")
select_obj = Select(select_element)
select_obj.select_by_visible_text("2")  # 選擇文字為 "2" 的選項
```

**NoDriver**:
```python
# 方法 1: JavaScript 直接設定（推薦）
select_element = await tab.query_selector("select")
result = await tab.evaluate('''
    (function(selectEl, targetText) {
        const options = selectEl.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].text === targetText) {
                selectEl.selectedIndex = i;
                selectEl.dispatchEvent(new Event('change', { bubbles: true }));
                return { success: true, value: options[i].value };
            }
        }
        return { success: false, error: "Option not found" };
    })(arguments[0], arguments[1]);
''', select_element, "2")

# 方法 2: 使用 element 參數（更簡潔）
result = await tab.evaluate('''
    const options = el.options;
    for (let i = 0; i < options.length; i++) {
        if (options[i].text === targetText) {
            el.selectedIndex = i;
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
    }
    return false;
''', el=select_element, targetText="2")
```

---

## 5. 關鍵技術決策總結

### 決策 1: 使用 `tab.evaluate()` 直接取得 `zone` 變數

**理由**:
- 避免字串處理的複雜性與錯誤風險
- JavaScript 可以直接存取全域變數或執行字串匹配
- `tab.evaluate()` 自動將 JavaScript 物件轉換為 Python 字典

**考慮過的替代方案**:
- 使用 `tab.query_selector()` + 字串分割: 可行，但需要處理尾部逗號、換行符等邊界情況
- 使用 CDP `Runtime.evaluate()`: 可行，但 `tab.evaluate()` 已封裝，更簡潔

**風險**:
- 如果 `zone` 是局部變數（在函數作用域內），JavaScript 無法直接存取
- 解決方案: 回退到字串處理方法

---

### 決策 2: 使用 JavaScript 設定 `<select>` 元素

**理由**:
- NoDriver 沒有內建的 `Select` API
- JavaScript 設定更靈活，可以觸發 `change` 事件
- 專案慣例: 簡單表單操作使用 JavaScript（參考 KKTIX 自動答題）

**考慮過的替代方案**:
- 使用 CDP `DOM.setAttributeValue`: 可行，但過於底層
- 使用 `element.send_keys()` 模擬鍵盤選擇: 不可行，`<select>` 不支援鍵盤輸入文字

**範例代碼**: 見上方 API 對應表

---

### 決策 3: 使用 JavaScript `areaTicket()` 執行區域選擇

**理由**:
- Ticketmaster 的區域選擇必須透過 JavaScript 函數觸發
- NoDriver 的 `tab.evaluate()` 完美支援這種場景

**範例代碼**:
```python
# Chrome Driver
driver.execute_script('areaTicket("%s", "map");' % target_area)

# NoDriver
await tab.evaluate(f'areaTicket("{target_area}", "map");')
```

**考慮過的替代方案**:
- 點擊 SVG 區域: 不可行，座標不穩定
- 使用 CDP 模擬點擊: 過於複雜，JavaScript 已足夠

---

### 決策 4: 使用 JavaScript Promise 實作條件等待

**理由**:
- NoDriver 的 `wait_for()` 不穩定（官方文件警告）
- JavaScript Promise 提供精確的條件控制與超時處理
- 專案慣例: 參考 `nodriver_api_guide.md` 的條件等待範例

**範例代碼**: 見上方「等待元素載入」章節

**考慮過的替代方案**:
- Python 輪詢 `tab.query_selector()`: 可行，但效能較差（需要多次跨進程通訊）
- 固定 `sleep()`: 不推薦，浪費時間

---

### 決策 5: domain_name 判斷機制

**決策**: 使用 `'ticketmaster' in domain_name` 判斷是否為 Ticketmaster 平台
**理由**: Ticketmaster 可能有多個子域名（如 `ticketmaster.com`, `ticketmaster.sg`）

**範例代碼**:
```python
# Chrome Driver (Line 6078)
if '/ticket/area/' in url:
    domain_name = url.split('/')[2]
    if config_dict["area_auto_select"]["enable"]:
        if not 'ticketmaster' in domain_name:
            tixcraft_area_auto_select(driver, url, config_dict)

# NoDriver
domain_name = url.split('/')[2]
if 'ticketmaster' in domain_name:
    # 執行 Ticketmaster 邏輯
else:
    # 執行 TixCraft 邏輯
```

**考慮過的替代方案**:
- 精確匹配 `domain_name == 'ticketmaster.com'`: 不可行，無法支援多個子域名
- 使用正則表達式: 過於複雜，字串包含判斷已足夠

---

### 決策 6: JSON 解析的健壯性處理

**決策**: 在字串分割後移除尾部逗號與換行符
**理由**: JavaScript 允許 trailing comma，但 Python `json.loads()` 不允許

**範例代碼**:
```python
# Chrome Driver (Line 5842-5846)
zone_string = zone_string.strip()
if zone_string[-1:] == "\n":
    zone_string = zone_string[:-1]
zone_string = zone_string.strip()
if zone_string[-1:] == ",":
    zone_string = zone_string[:-1]

# NoDriver (若使用字串處理)
zone_string = zone_string.strip().rstrip('\n,')
```

**考慮過的替代方案**:
- 使用正則表達式替換: 可行，但字串操作更直觀
- 使用 `json.loads()` 的 `strict=False`: 不存在此參數

---

### 決策 7: 分頁管理策略

**決策**: Ticketmaster 日期選擇可能開啟新分頁，需要切換回主分頁並關閉新分頁
**理由**: 保持主分頁活躍，避免操作錯誤的分頁

**範例代碼**:
```python
# Chrome Driver (Line 1373-1380)
window_handles_count = len(driver.window_handles)
if window_handles_count > 1:
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(0.2)

# NoDriver
if len(driver.tabs) > 1:
    # 關閉非主分頁
    for tab in driver.tabs[1:]:
        await tab.close()
    # 確保主分頁活躍
    await driver.tabs[0].activate()
    await driver.tabs[0].sleep(0.2)
```

**專案現有實作參考**:
- `nodriver_api_guide.md` Line 673-691: 多分頁管理範例

**考慮過的替代方案**:
- 保留所有分頁: 不可行，會導致操作錯誤的分頁
- 只關閉新分頁不切換: 可行，但不穩定

---

### 決策 8: 使用專案現有的 `tixcraft_*` 函數處理驗證碼

**決策**: 重用 `tixcraft_keyin_captcha_code()` 與 `tixcraft_auto_ocr()`
**理由**: Ticketmaster 與 TixCraft 使用相同的驗證碼系統，邏輯完全相同

**考慮過的替代方案**:
- 單獨實作 Ticketmaster 驗證碼處理: 不必要，違反 DRY 原則

---

## 6. 風險與未知項目

### 風險 1: `zone` 變數可能在局部作用域

**描述**: 如果 `var zone = {...}` 宣告在函數內部，`tab.evaluate('return zone;')` 將無法存取
**影響**: 無法直接取得 zone_info
**解決方案**: 回退到字串分割方法（從 `innerHTML` 提取）
**優先度**: 中（需實際測試確認）

---

### 風險 2: Ticketmaster 可能使用 Cloudflare 防護

**描述**: 如果 Ticketmaster 啟用 Cloudflare Challenge，NoDriver 可能需要處理驗證
**影響**: 無法載入頁面
**解決方案**: 參考 `nodriver_api_guide.md` Line 852-886 的 Cloudflare 處理邏輯
**優先度**: 低（目前無證據顯示 Ticketmaster 使用 Cloudflare）

---

### 未知項目 1: Ticketmaster 的反爬蟲機制

**描述**: 尚未確認 Ticketmaster 是否有額外的反爬蟲檢測（如 Canvas Fingerprinting、WebRTC Leak）
**影響**: NoDriver 可能被偵測為機器人
**解決方案**: 遵循 NoDriver 的反偵測配置（參考 `nodriver_api_guide.md` Line 832-848）
**優先度**: 中（需實際測試確認）

---

### 未知項目 2: `#ticketPriceList` 的載入時間

**描述**: 尚未確認 `#loadingmap` 消失到 `#ticketPriceList` 出現的時間間隔
**影響**: 可能需要調整等待邏輯
**解決方案**: 使用 JavaScript Promise 條件等待（最多 10 秒）
**優先度**: 低（條件等待已足夠應對）

---

## 7. 實作建議優先度

### 高優先度（立即實作）

1. **`nodriver_ticketmaster_date_auto_select()`** - 日期選擇（核心功能）
2. **`nodriver_ticketmaster_parse_zone_info()`** - 提取 zone_info（區域選擇前置）
3. **`nodriver_ticketmaster_area_auto_select()`** - 區域選擇（核心功能）
4. **`nodriver_ticketmaster_assign_ticket_number()`** - 票數設定（核心功能）

### 中優先度（後續實作）

5. **`nodriver_ticketmaster_get_ticketPriceList()`** - 票價表格檢查（輔助功能）
6. **`nodriver_ticketmaster_captcha()`** - 驗證碼處理（可重用 TixCraft 邏輯）
7. **`nodriver_ticketmaster_promo()`** - Promo Code 處理（可重用 TixCraft 邏輯）

### 低優先度（測試後決定）

8. **分頁管理** - 處理新分頁（若測試發現不需要則跳過）
9. **Cloudflare 處理** - 反爬蟲應對（若測試發現不需要則跳過）

---

## 8. 參考資源

### 專案內部文件

- **NoDriver API 使用指南**: `docs/06-api-reference/nodriver_api_guide.md`
- **CDP Protocol 參考指南**: `docs/06-api-reference/cdp_protocol_reference.md`
- **程式碼結構**: `docs/02-development/structure.md`
- **搞票自動化標準**: `docs/02-development/ticket_automation_standard.md`

### 專案現有實作範例

- **KKTIX 自動答題** (JavaScript 表單處理): `nodriver_tixcraft.py:1175-1313`
- **ibon 日期選擇** (Pierce Method Shadow DOM): `nodriver_tixcraft.py:7662-8051`
- **TixCraft 日期選擇** (關鍵字匹配): `nodriver_tixcraft.py:3155-3515`
- **多分頁管理**: `nodriver_api_guide.md:673-691`
- **Cloudflare 處理**: `nodriver_api_guide.md:852-886`

### Chrome Driver 版本參考

- `src/chrome_tixcraft.py:1274` - `ticketmaster_date_auto_select()`
- `src/chrome_tixcraft.py:1516` - `get_ticketmaster_target_area()`
- `src/chrome_tixcraft.py:1665` - `ticketmaster_area_auto_select()`
- `src/chrome_tixcraft.py:5808` - `ticketmaster_parse_zone_info()`
- `src/chrome_tixcraft.py:5864` - `ticketmaster_get_ticketPriceList()`
- `src/chrome_tixcraft.py:5910` - `ticketmaster_assign_ticket_number()`
- `src/chrome_tixcraft.py:1937` - `ticketmaster_promo()`
- `src/chrome_tixcraft.py:5979` - `ticketmaster_captcha()`

---

**研究完成日期**: 2025-11-15
**下一步**: 開始實作 NoDriver 版本的 Ticketmaster 函數
