# Selenium WebDriver API 使用指南

> **目標**：搶票系統的 Selenium WebDriver 完整使用手册，涵蓋所有核心功能和最佳實踐

**官方文件**: https://www.selenium.dev/documentation/
**GitHub 專案**: https://github.com/SeleniumHQ/selenium

## 核心概念

### Selenium 生態系統
```
Selenium IDE    ──┐
Selenium WebDriver ├─ Selenium 專案
Selenium Grid   ──┘
```

### W3C WebDriver 標準
- **統一介面**：跨瀏覽器、跨平台的標準化 API
- **原生支援**：瀏覽器廠商直接實作 WebDriver 協定
- **語言綁定**：支援 Python、Java、C#、Ruby、JavaScript、Kotlin

### 與其他自動化工具比較

| 特性 | Selenium | Undetected-Chrome | NoDriver |
|------|----------|------------------|----------|
| **學習成本** | 🟢 低 (業界標準) | 🟡 低 (Selenium 相容) | 🔴 高 (async/await) |
| **反偵測能力** | ❌ 無 | ✅ 強 | ✅ 極強 |
| **穩定性** | ✅ 最高 | ✅ 高 | 🟡 中等 |
| **文件完整性** | ✅ 最完整 | 🟡 中等 | 🟡 中等 |
| **社群支援** | ✅ 最廣泛 | 🟡 中等 | 🟡 小眾 |
| **搶票適用性** | 🟡 基礎 | ✅ 優秀 | ✅ 最佳 |

## 環境設置與初始化

### 1. 安裝依賴
```bash
pip install selenium
```

### 2. 自動化 WebDriver 管理 (Selenium 4.6+)
```python
from selenium import webdriver

# Selenium Manager 自動下載和管理 WebDriver
driver = webdriver.Chrome()  # 自動下載 ChromeDriver
driver = webdriver.Firefox() # 自動下載 GeckoDriver
driver = webdriver.Edge()    # 自動下載 EdgeDriver
```

### 3. 手動指定 WebDriver 路徑
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 手動指定 ChromeDriver 路徑
service = Service('/path/to/chromedriver')
driver = webdriver.Chrome(service=service)
```

### 4. 完整初始化函數 (搶票系統專用)
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

def init_selenium_driver(config_dict, webdriver_path):
    """搶票系統專用 Selenium 初始化"""

    # 1. 檢查 ChromeDriver 路徑
    chromedriver_path = os.path.join(webdriver_path, "chromedriver.exe")
    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not found, using Selenium Manager")
        chromedriver_path = None

    # 2. 設定 Chrome 選項
    chrome_options = Options()

    # 基本選項
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # 加速載入

    # 無頭模式 (可選)
    if config_dict.get("headless", False):
        chrome_options.add_argument("--headless")

    # 頁面載入策略
    chrome_options.page_load_strategy = 'eager'  # 推薦：平衡速度和穩定性

    # 提示處理
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # 3. 初始化 WebDriver
    try:
        if chromedriver_path:
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        # 4. 設定等待時間
        driver.implicitly_wait(10)  # 隱式等待 10 秒

        # 5. 最大化視窗
        driver.maximize_window()

        return driver

    except Exception as exc:
        print(f"WebDriver initialization failed: {exc}")
        return None
```

## 元素定位策略

### 1. 八種定位方法

#### By.ID - 最優先選擇
```python
from selenium.webdriver.common.by import By

# HTML: <input id="username" type="text">
element = driver.find_element(By.ID, "username")
```

#### By.NAME - 表單元素常用
```python
# HTML: <input name="password" type="password">
element = driver.find_element(By.NAME, "password")
```

#### By.CLASS_NAME - 樣式類別
```python
# HTML: <button class="btn-primary">購買</button>
element = driver.find_element(By.CLASS_NAME, "btn-primary")
```

#### By.TAG_NAME - HTML 標籤
```python
# 查找所有按鈕
buttons = driver.find_elements(By.TAG_NAME, "button")
```

#### By.LINK_TEXT - 完整連結文字
```python
# HTML: <a href="/tickets">立即購票</a>
element = driver.find_element(By.LINK_TEXT, "立即購票")
```

#### By.PARTIAL_LINK_TEXT - 部分連結文字
```python
# 包含「購票」的連結
element = driver.find_element(By.PARTIAL_LINK_TEXT, "購票")
```

#### By.CSS_SELECTOR - CSS 選擇器 ⭐ **搶票系統主力**
```python
# 複雜選擇器
ticket_button = driver.find_element(By.CSS_SELECTOR, "div.ticket-area button.buy-now")

# 屬性選擇器
date_option = driver.find_element(By.CSS_SELECTOR, "option[value='2025-10-22']")

# 偽類選擇器
first_available = driver.find_element(By.CSS_SELECTOR, "tr.available:first-child")
```

#### By.XPATH - XPath 表達式 ⚡ **最強大但較慢**
```python
# 文字內容匹配
buy_button = driver.find_element(By.XPATH, "//button[contains(text(), '立即購買')]")

# 屬性條件
ticket_area = driver.find_element(By.XPATH, "//div[@class='ticket-area' and @data-available='true']")

# 相對位置
next_button = driver.find_element(By.XPATH, "//input[@id='date']/following-sibling::button")
```

### 2. 相對定位器 (Selenium 4+)
```python
from selenium.webdriver.support.relative_locator import locate_with

# 在某元素上方
password_field = driver.find_element(
    locate_with(By.TAG_NAME, "input").above(submit_button)
)

# 在某元素右側
captcha_input = driver.find_element(
    locate_with(By.TAG_NAME, "input").to_right_of(captcha_image)
)

# 組合條件
target_element = driver.find_element(
    locate_with(By.TAG_NAME, "button")
    .below(header)
    .to_left_of(sidebar)
)
```

### 3. 元素查找最佳實踐
```python
def safe_find_element(driver, by, value, timeout=10):
    """安全的元素查找函數"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Element not found: {by}={value}")
        return None

def find_multiple_elements_safe(driver, selectors):
    """嘗試多個選擇器直到找到元素"""
    for by, value in selectors:
        try:
            element = driver.find_element(by, value)
            if element:
                return element
        except NoSuchElementException:
            continue
    return None

# 使用範例
ticket_button = find_multiple_elements_safe(driver, [
    (By.ID, "buy-ticket"),
    (By.CLASS_NAME, "ticket-btn"),
    (By.CSS_SELECTOR, "button[data-action='buy']"),
    (By.XPATH, "//button[contains(text(), '購票')]")
])
```

## 等待機制

### 1. 隱式等待 (Implicit Wait)
```python
# 設定全域隱式等待
driver.implicitly_wait(10)  # 所有元素查找最多等待 10 秒

# 優點：設定一次，全域生效
# 缺點：無法針對特定條件等待
```

### 2. 顯式等待 (Explicit Wait) ⭐ **推薦**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)

# 等待元素出現
element = wait.until(EC.presence_of_element_located((By.ID, "submit")))

# 等待元素可點擊
buy_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "buy-now")))

# 等待元素消失 (loading 畫面)
wait.until(EC.invisibility_of_element((By.CLASS_NAME, "loading")))

# 等待文字出現
wait.until(EC.text_to_be_present_in_element((By.ID, "status"), "Available"))
```

### 3. Expected Conditions 完整列表
```python
# 存在性檢查
EC.presence_of_element_located(locator)           # 元素存在於 DOM
EC.presence_of_all_elements_located(locator)      # 所有元素存在於 DOM

# 可見性檢查
EC.visibility_of_element_located(locator)         # 元素可見
EC.visibility_of(element)                         # 指定元素可見
EC.invisibility_of_element(locator)               # 元素不可見

# 可互動性檢查
EC.element_to_be_clickable(locator)               # 元素可點擊
EC.element_to_be_selected(element)                # 元素被選中

# 文字內容檢查
EC.text_to_be_present_in_element(locator, text)   # 元素包含指定文字
EC.text_to_be_present_in_element_value(locator, text)  # 元素值包含指定文字

# 屬性檢查
EC.element_attribute_to_include(locator, attribute)    # 元素包含指定屬性

# 彈窗檢查
EC.alert_is_present()                             # 彈窗出現

# 頁面狀態檢查
EC.title_is(title)                                # 頁面標題是
EC.title_contains(title)                          # 頁面標題包含
EC.url_contains(url)                              # 當前 URL 包含
EC.url_to_be(url)                                 # 當前 URL 是

# Frame 檢查
EC.frame_to_be_available_and_switch_to_it(locator)    # Frame 可用並切換
```

### 4. 流暢等待 (Fluent Wait)
```python
from selenium.webdriver.support.wait import WebDriverWait

wait = WebDriverWait(
    driver,
    timeout=30,           # 最大等待時間
    poll_frequency=0.5,   # 檢查頻率
    ignored_exceptions=[NoSuchElementException, ElementNotVisibleException]
)

element = wait.until(EC.element_to_be_clickable((By.ID, "dynamic-button")))
```

### 5. 搶票系統專用等待函數
```python
def wait_for_ticket_available(driver, timeout=30):
    """等待票券變為可購買狀態"""
    wait = WebDriverWait(driver, timeout)

    # 等待購買按鈕可點擊且不是「售完」狀態
    def ticket_available(driver):
        try:
            buy_buttons = driver.find_elements(By.CSS_SELECTOR, "button.ticket-buy")
            for button in buy_buttons:
                if button.is_enabled() and "sold out" not in button.text.lower():
                    return button
            return False
        except:
            return False

    return wait.until(ticket_available)

def wait_for_page_load_complete(driver, timeout=30):
    """等待頁面完全載入"""
    wait = WebDriverWait(driver, timeout)

    # 等待 document.readyState 為 complete
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    # 等待 jQuery 載入完成 (如果有的話)
    wait.until(lambda driver: driver.execute_script("return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true"))
```

## 元素互動操作

### 1. 基本互動操作
```python
# 點擊操作
element.click()

# 輸入文字
element.send_keys("Hello World")

# 清除內容
element.clear()

# 提交表單
element.submit()

# 獲取文字內容
text = element.text

# 獲取屬性值
value = element.get_attribute("value")
href = element.get_attribute("href")

# 獲取 CSS 屬性
color = element.value_of_css_property("color")

# 檢查元素狀態
is_displayed = element.is_displayed()
is_enabled = element.is_enabled()
is_selected = element.is_selected()
```

### 2. 表單處理

#### Select 下拉選單 ⭐ **搶票系統常用**
```python
from selenium.webdriver.support.ui import Select

# 查找 select 元素
select_element = driver.find_element(By.ID, "ticket-quantity")
select = Select(select_element)

# 根據可見文字選擇
select.select_by_visible_text("2 張")

# 根據值選擇
select.select_by_value("2")

# 根據索引選擇
select.select_by_index(1)

# 獲取所有選項
all_options = select.options
for option in all_options:
    print(option.text)

# 獲取選中的選項
selected_option = select.first_selected_option
print(selected_option.text)

# 多選下拉選單
select.deselect_all()
select.select_by_visible_text("VIP 區")
select.select_by_visible_text("一般區")
```

#### 搶票系統 Select 處理函數
```python
def safe_select_option(driver, select_locator, target_value, method="text"):
    """安全的下拉選單選擇"""
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(select_locator)
        )
        select = Select(select_element)

        if method == "text":
            # 嘗試精確匹配
            try:
                select.select_by_visible_text(target_value)
                return True
            except NoSuchElementException:
                # 嘗試部分匹配
                for option in select.options:
                    if target_value in option.text:
                        select.select_by_visible_text(option.text)
                        return True

        elif method == "value":
            select.select_by_value(target_value)
            return True

        elif method == "index":
            select.select_by_index(int(target_value))
            return True

        return False

    except Exception as exc:
        print(f"Select option failed: {exc}")
        return False

# 使用範例
success = safe_select_option(
    driver,
    (By.ID, "ticket-count"),
    "2",
    method="value"
)
```

#### Radio Button 和 Checkbox
```python
# Radio Button 選擇
radio_button = driver.find_element(By.CSS_SELECTOR, "input[type='radio'][value='vip']")
if not radio_button.is_selected():
    radio_button.click()

# Checkbox 處理
checkbox = driver.find_element(By.ID, "agree-terms")
if not checkbox.is_selected():
    checkbox.click()

# 批量處理 Checkbox
checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
for checkbox in checkboxes:
    if checkbox.get_attribute("data-required") == "true":
        if not checkbox.is_selected():
            checkbox.click()
```

### 3. 檔案上傳
```python
# 標準檔案上傳
file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
file_input.send_keys("/path/to/file.jpg")

# 多檔案上傳
file_input.send_keys("/path/to/file1.jpg\n/path/to/file2.jpg")
```

### 4. 拖放操作 (少用)
```python
from selenium.webdriver.common.action_chains import ActionChains

source = driver.find_element(By.ID, "source")
target = driver.find_element(By.ID, "target")

# 拖放操作
ActionChains(driver).drag_and_drop(source, target).perform()

# 拖放到指定位置
ActionChains(driver).drag_and_drop_by_offset(source, 100, 200).perform()
```

## 進階互動 (Actions API)

### 1. 滑鼠操作
```python
from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(driver)

# 基本滑鼠操作
actions.click(element)                    # 點擊元素
actions.click_and_hold(element)           # 點擊並持續按住
actions.release(element)                  # 釋放滑鼠按鍵
actions.double_click(element)             # 雙擊
actions.context_click(element)            # 右鍵點擊

# 滑鼠移動
actions.move_to_element(element)          # 移動到元素
actions.move_by_offset(100, 200)          # 相對移動
actions.move_to_element_with_offset(element, 10, 20)  # 移動到元素偏移位置

# 執行動作
actions.perform()
```

### 2. 鍵盤操作
```python
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 單一按鍵
element.send_keys(Keys.ENTER)
element.send_keys(Keys.TAB)
element.send_keys(Keys.ESCAPE)

# 組合鍵
element.send_keys(Keys.CONTROL + "a")     # Ctrl+A
element.send_keys(Keys.CONTROL + "c")     # Ctrl+C
element.send_keys(Keys.CONTROL + "v")     # Ctrl+V

# 使用 Actions API
actions = ActionChains(driver)
actions.key_down(Keys.CONTROL)            # 按下 Ctrl
actions.send_keys("a")                    # 按下 A
actions.key_up(Keys.CONTROL)              # 釋放 Ctrl
actions.perform()
```

### 3. 搶票系統專用動作鏈
```python
def rapid_ticket_purchase(driver, ticket_data):
    """快速購票動作鏈"""
    actions = ActionChains(driver)

    try:
        # 1. 選擇日期
        date_element = driver.find_element(By.CSS_SELECTOR, f"[data-date='{ticket_data['date']}']")
        actions.move_to_element(date_element).click()

        # 2. 選擇區域
        area_element = driver.find_element(By.CSS_SELECTOR, f"[data-area='{ticket_data['area']}']")
        actions.move_to_element(area_element).click()

        # 3. 快速填入數量
        quantity_input = driver.find_element(By.ID, "quantity")
        actions.move_to_element(quantity_input).click()
        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)  # 全選
        actions.send_keys(str(ticket_data['quantity']))

        # 4. 提交
        submit_button = driver.find_element(By.ID, "submit")
        actions.move_to_element(submit_button).click()

        # 執行所有動作
        actions.perform()

        return True

    except Exception as exc:
        print(f"Rapid purchase failed: {exc}")
        return False

def scroll_to_element_smooth(driver, element):
    """平滑滾動到元素"""
    actions = ActionChains(driver)

    # 滾動到元素位置
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", element)
    time.sleep(0.5)  # 等待滾動完成

    # 移動滑鼠到元素 (模擬真實用戶行為)
    actions.move_to_element(element).perform()
```

## 瀏覽器控制

### 1. 導航操作
```python
# 基本導航
driver.get("https://example.com")         # 導航到 URL
driver.back()                             # 返回上一頁
driver.forward()                          # 前進到下一頁
driver.refresh()                          # 重新整理頁面

# 獲取頁面資訊
current_url = driver.current_url          # 當前 URL
page_title = driver.title                 # 頁面標題
page_source = driver.page_source          # 頁面 HTML 源碼
```

### 2. 視窗管理
```python
# 視窗大小控制
driver.maximize_window()                  # 最大化視窗
driver.minimize_window()                  # 最小化視窗
driver.fullscreen_window()                # 全螢幕模式

# 設定視窗大小
driver.set_window_size(1920, 1080)

# 獲取視窗大小
size = driver.get_window_size()
print(f"Width: {size['width']}, Height: {size['height']}")

# 設定視窗位置
driver.set_window_position(100, 100)

# 獲取視窗位置
position = driver.get_window_position()
print(f"X: {position['x']}, Y: {position['y']}")
```

### 3. 多分頁處理
```python
# 開啟新分頁
driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[1])
driver.get("https://example.com")

# 獲取所有視窗控制代碼
all_windows = driver.window_handles

# 切換到特定視窗
driver.switch_to.window(all_windows[0])   # 切換到第一個視窗

# 關閉當前視窗
driver.close()

# 搶票系統多分頁管理
def manage_multiple_tabs(driver, urls):
    """管理多個購票分頁"""
    original_window = driver.current_window_handle

    # 開啟多個分頁
    for url in urls:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

    # 回到原始分頁
    driver.switch_to.window(original_window)

    return driver.window_handles

def close_extra_windows(driver, keep_main=True):
    """關閉多餘視窗，保留主視窗"""
    main_window = driver.window_handles[0] if keep_main else None

    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            driver.close()

    if keep_main:
        driver.switch_to.window(main_window)
```

### 4. Frame 和 IFrame 處理
```python
# 切換到 Frame
driver.switch_to.frame("frame_name")      # 根據 name 屬性
driver.switch_to.frame(0)                 # 根據索引
frame_element = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(frame_element)     # 根據元素

# 回到主要內容
driver.switch_to.default_content()

# 回到上一層 Frame
driver.switch_to.parent_frame()

# 搶票系統 Frame 處理
def handle_captcha_frame(driver):
    """處理驗證碼 Frame"""
    try:
        # 等待 iframe 載入
        iframe = WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "captcha-frame"))
        )

        # 在 iframe 內操作驗證碼
        captcha_input = driver.find_element(By.ID, "captcha-input")
        captcha_input.send_keys("123456")

        # 回到主要內容
        driver.switch_to.default_content()

        return True

    except Exception as exc:
        print(f"Captcha frame handling failed: {exc}")
        driver.switch_to.default_content()  # 確保回到主要內容
        return False
```

### 5. 彈窗和對話框處理
```python
# Alert 對話框處理
def handle_alert(driver, action="accept"):
    """處理 JavaScript Alert 對話框"""
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())

        # 獲取 Alert 文字
        alert_text = alert.text
        print(f"Alert message: {alert_text}")

        if action == "accept":
            alert.accept()          # 點擊「確定」
        elif action == "dismiss":
            alert.dismiss()         # 點擊「取消」

        return True, alert_text

    except TimeoutException:
        print("No alert present")
        return False, None

# Confirm 對話框
def handle_confirm(driver, accept=True):
    """處理 Confirm 對話框"""
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())

        if accept:
            alert.accept()
        else:
            alert.dismiss()

        return True

    except TimeoutException:
        return False

# Prompt 對話框
def handle_prompt(driver, input_text=""):
    """處理 Prompt 對話框"""
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())

        if input_text:
            alert.send_keys(input_text)

        alert.accept()
        return True

    except TimeoutException:
        return False
```

## JavaScript 執行

### 1. 基本 JavaScript 執行
```python
# 執行 JavaScript 並獲取返回值
result = driver.execute_script("return document.title;")

# 執行 JavaScript 腳本
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# 傳遞參數給 JavaScript
element = driver.find_element(By.ID, "target")
driver.execute_script("arguments[0].style.backgroundColor = 'yellow';", element)

# 執行異步 JavaScript
def callback_function():
    print("Async script completed")

driver.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    setTimeout(function() {
        callback('Script completed');
    }, 1000);
""")
```

### 2. 搶票系統常用 JavaScript 操作
```python
def scroll_to_element(driver, element):
    """滾動到指定元素"""
    driver.execute_script("arguments[0].scrollIntoView();", element)

def smooth_scroll_to_bottom(driver):
    """平滑滾動到頁面底部"""
    driver.execute_script("""
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    """)

def force_click_element(driver, element):
    """強制點擊元素 (繞過覆蓋問題)"""
    driver.execute_script("arguments[0].click();", element)

def remove_element_attribute(driver, element, attribute):
    """移除元素屬性"""
    driver.execute_script(f"arguments[0].removeAttribute('{attribute}');", element)

def set_element_value(driver, element, value):
    """直接設定元素值"""
    driver.execute_script(f"arguments[0].value = '{value}';", element)
    # 觸發 change 事件
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", element)

def wait_for_ajax_complete(driver, timeout=30):
    """等待 AJAX 請求完成"""
    script = """
        return (function() {
            if (typeof jQuery !== 'undefined') {
                return jQuery.active == 0;
            }
            if (typeof axios !== 'undefined') {
                return axios.pendingRequests == 0;
            }
            return true;
        })();
    """

    wait = WebDriverWait(driver, timeout)
    wait.until(lambda driver: driver.execute_script(script))

def inject_custom_script(driver):
    """注入自訂腳本"""
    custom_script = """
        // 搶票輔助函數
        window.quickTicket = {
            clickFastest: function(selector) {
                var elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    elements[0].click();
                    return true;
                }
                return false;
            },

            fillForm: function(data) {
                Object.keys(data).forEach(function(key) {
                    var element = document.querySelector('[name="' + key + '"]');
                    if (element) {
                        element.value = data[key];
                        element.dispatchEvent(new Event('change'));
                    }
                });
            }
        };
    """
    driver.execute_script(custom_script)
```

### 3. 高級 JavaScript 技巧
```python
def monitor_network_requests(driver):
    """監控網路請求"""
    script = """
        window.networkRequests = [];

        // 攔截 fetch 請求
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            window.networkRequests.push({
                type: 'fetch',
                url: args[0],
                timestamp: Date.now()
            });
            return originalFetch.apply(this, args);
        };

        // 攔截 XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            xhr.open = function(method, url) {
                window.networkRequests.push({
                    type: 'xhr',
                    method: method,
                    url: url,
                    timestamp: Date.now()
                });
                return originalOpen.apply(this, arguments);
            };
            return xhr;
        };
    """
    driver.execute_script(script)

def get_network_requests(driver):
    """獲取網路請求記錄"""
    return driver.execute_script("return window.networkRequests || [];")

def simulate_human_behavior(driver):
    """模擬人類行為"""
    script = """
        // 隨機滑鼠移動
        function randomMouseMove() {
            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight;

            const event = new MouseEvent('mousemove', {
                clientX: x,
                clientY: y,
                bubbles: true
            });

            document.dispatchEvent(event);
        }

        // 定期執行
        setInterval(randomMouseMove, 2000 + Math.random() * 3000);
    """
    driver.execute_script(script)
```

## Cookie 和儲存管理

### 1. Cookie 操作
```python
# 獲取所有 Cookie
all_cookies = driver.get_cookies()

# 獲取特定 Cookie
session_cookie = driver.get_cookie("session_id")

# 新增 Cookie
driver.add_cookie({
    'name': 'test_cookie',
    'value': 'test_value',
    'domain': 'example.com',
    'path': '/',
    'secure': True,
    'httpOnly': False
})

# 刪除特定 Cookie
driver.delete_cookie("session_id")

# 刪除所有 Cookie
driver.delete_all_cookies()

# 搶票系統 Cookie 管理
def save_login_cookies(driver, file_path):
    """保存登入狀態 Cookie"""
    import pickle

    cookies = driver.get_cookies()
    with open(file_path, 'wb') as file:
        pickle.dump(cookies, file)

    print(f"Cookies saved to {file_path}")

def load_login_cookies(driver, file_path):
    """載入登入狀態 Cookie"""
    import pickle
    import os

    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, 'rb') as file:
            cookies = pickle.load(file)

        for cookie in cookies:
            driver.add_cookie(cookie)

        print(f"Cookies loaded from {file_path}")
        return True

    except Exception as exc:
        print(f"Failed to load cookies: {exc}")
        return False

def check_login_status(driver):
    """檢查登入狀態"""
    # 檢查登入相關 Cookie
    login_cookies = ['session_id', 'auth_token', 'user_id']

    for cookie_name in login_cookies:
        cookie = driver.get_cookie(cookie_name)
        if cookie:
            return True

    # 檢查頁面元素
    try:
        logout_button = driver.find_element(By.CSS_SELECTOR, ".logout, .signout")
        return True
    except NoSuchElementException:
        return False
```

### 2. Local Storage 操作
```python
def set_local_storage(driver, key, value):
    """設定 Local Storage"""
    driver.execute_script(f"localStorage.setItem('{key}', '{value}');")

def get_local_storage(driver, key):
    """獲取 Local Storage"""
    return driver.execute_script(f"return localStorage.getItem('{key}');")

def remove_local_storage(driver, key):
    """移除 Local Storage 項目"""
    driver.execute_script(f"localStorage.removeItem('{key}');")

def clear_local_storage(driver):
    """清空 Local Storage"""
    driver.execute_script("localStorage.clear();")

def get_all_local_storage(driver):
    """獲取所有 Local Storage 資料"""
    return driver.execute_script("""
        var items = {};
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            items[key] = localStorage.getItem(key);
        }
        return items;
    """)
```

### 3. Session Storage 操作
```python
def set_session_storage(driver, key, value):
    """設定 Session Storage"""
    driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")

def get_session_storage(driver, key):
    """獲取 Session Storage"""
    return driver.execute_script(f"return sessionStorage.getItem('{key}');")

def clear_session_storage(driver):
    """清空 Session Storage"""
    driver.execute_script("sessionStorage.clear();")
```

## 搶票系統實戰應用

### 1. 驗證碼處理
```python
def handle_text_captcha(driver, captcha_input_selector):
    """處理文字驗證碼"""
    try:
        # 截取驗證碼圖片
        captcha_image = driver.find_element(By.CSS_SELECTOR, ".captcha-image")
        captcha_image.screenshot("captcha.png")

        # 這裡可以整合 OCR 服務
        # captcha_text = ocr_service.recognize("captcha.png")

        # 手動輸入示例
        captcha_text = input("請輸入驗證碼: ")

        # 填入驗證碼
        captcha_input = driver.find_element(By.CSS_SELECTOR, captcha_input_selector)
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)

        return True

    except Exception as exc:
        print(f"Captcha handling failed: {exc}")
        return False

def handle_slider_captcha(driver):
    """處理滑動驗證碼"""
    try:
        slider = driver.find_element(By.CSS_SELECTOR, ".slider-button")
        track = driver.find_element(By.CSS_SELECTOR, ".slider-track")

        # 計算滑動距離
        track_width = track.size['width']
        slider_width = slider.size['width']
        distance = track_width - slider_width

        # 執行滑動
        actions = ActionChains(driver)
        actions.click_and_hold(slider)
        actions.move_by_offset(distance, 0)
        actions.release()
        actions.perform()

        return True

    except Exception as exc:
        print(f"Slider captcha failed: {exc}")
        return False
```

### 2. 動態內容等待
```python
def wait_for_ticket_release(driver, check_interval=1, max_wait_time=300):
    """等待票券開賣"""
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        try:
            # 檢查是否有購買按鈕出現
            buy_buttons = driver.find_elements(By.CSS_SELECTOR, ".buy-ticket, .purchase-btn")

            for button in buy_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = button.text.lower()
                    if "buy" in button_text or "購買" in button_text:
                        return button

            # 重新整理頁面
            driver.refresh()
            time.sleep(check_interval)

        except Exception as exc:
            print(f"Error while waiting for tickets: {exc}")
            time.sleep(check_interval)

    return None

def monitor_ticket_status(driver, callback_function=None):
    """監控票券狀態變化"""
    previous_status = ""

    while True:
        try:
            status_element = driver.find_element(By.CSS_SELECTOR, ".ticket-status")
            current_status = status_element.text

            if current_status != previous_status:
                print(f"Status changed: {previous_status} -> {current_status}")

                if callback_function:
                    callback_function(current_status)

                previous_status = current_status

            time.sleep(1)  # 每秒檢查一次

        except KeyboardInterrupt:
            print("Monitoring stopped by user")
            break
        except Exception as exc:
            print(f"Monitoring error: {exc}")
            time.sleep(1)
```

### 3. 並發操作
```python
import threading
from queue import Queue

def concurrent_ticket_purchase(ticket_urls, config):
    """並發搶票"""
    results = Queue()

    def purchase_worker(url):
        """單個購票工作線程"""
        driver = init_selenium_driver(config, "webdriver")

        try:
            driver.get(url)

            # 執行購票流程
            success = execute_purchase_flow(driver, config)

            results.put({
                'url': url,
                'success': success,
                'thread_id': threading.current_thread().ident
            })

        except Exception as exc:
            results.put({
                'url': url,
                'success': False,
                'error': str(exc),
                'thread_id': threading.current_thread().ident
            })
        finally:
            driver.quit()

    # 建立並啟動線程
    threads = []
    for url in ticket_urls:
        thread = threading.Thread(target=purchase_worker, args=(url,))
        thread.start()
        threads.append(thread)

    # 等待所有線程完成
    for thread in threads:
        thread.join()

    # 收集結果
    all_results = []
    while not results.empty():
        all_results.append(results.get())

    return all_results

def execute_purchase_flow(driver, config):
    """執行購票流程"""
    try:
        # 1. 登入
        if not auto_login(driver, config):
            return False

        # 2. 選擇票券
        if not select_ticket_options(driver, config):
            return False

        # 3. 填寫資料
        if not fill_purchase_form(driver, config):
            return False

        # 4. 處理驗證碼
        if not handle_captcha_if_present(driver):
            return False

        # 5. 確認購買
        if not confirm_purchase(driver):
            return False

        return True

    except Exception as exc:
        print(f"Purchase flow failed: {exc}")
        return False
```

### 4. 錯誤重試機制
```python
import time
import random
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """裝飾器：失敗時自動重試"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    if attempt == max_retries - 1:
                        raise exc

                    print(f"Attempt {attempt + 1} failed: {exc}")
                    print(f"Retrying in {retry_delay} seconds...")

                    time.sleep(retry_delay)
                    retry_delay *= backoff

            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
def robust_element_click(driver, locator, timeout=10):
    """可靠的元素點擊"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )

    # 滾動到元素位置
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(0.5)

    # 嘗試點擊
    try:
        element.click()
    except ElementClickInterceptedException:
        # 如果被遮擋，使用 JavaScript 點擊
        driver.execute_script("arguments[0].click();", element)

    return True

def adaptive_retry_strategy(driver, operation_func, *args, **kwargs):
    """自適應重試策略"""
    max_attempts = 5
    base_delay = 1

    for attempt in range(max_attempts):
        try:
            return operation_func(driver, *args, **kwargs)

        except TimeoutException:
            if attempt < max_attempts - 1:
                # 頁面載入超時，嘗試重新整理
                driver.refresh()
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)

        except NoSuchElementException:
            if attempt < max_attempts - 1:
                # 元素未找到，等待更長時間
                delay = base_delay * (3 ** attempt)
                time.sleep(delay)

        except Exception as exc:
            print(f"Unexpected error on attempt {attempt + 1}: {exc}")
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)

    raise Exception(f"Operation failed after {max_attempts} attempts")
```

## 效能優化

### 1. 頁面載入策略
```python
from selenium.webdriver.chrome.options import Options

def get_optimized_chrome_options():
    """效能優化的 Chrome 選項"""
    options = Options()

    # 頁面載入策略
    options.page_load_strategy = 'eager'  # 推薦：DOM 完成即可
    # options.page_load_strategy = 'none'   # 最快：不等待載入

    # 禁用圖片載入
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    # 禁用不必要的功能
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    # 效能優化
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")

    return options
```

### 2. 無頭模式
```python
def get_headless_options():
    """無頭模式設定"""
    options = Options()

    # 啟用無頭模式
    options.add_argument("--headless")

    # 設定視窗大小 (無頭模式必須)
    options.add_argument("--window-size=1920,1080")

    # 禁用 GPU (避免無頭模式問題)
    options.add_argument("--disable-gpu")

    return options

# 條件式無頭模式
def init_driver_with_headless_option(config_dict):
    """根據設定決定是否使用無頭模式"""
    options = get_optimized_chrome_options()

    # 根據時間決定是否使用無頭模式
    import datetime
    current_hour = datetime.datetime.now().hour

    # 凌晨時段使用無頭模式節省資源
    if current_hour < 6 or config_dict.get("force_headless", False):
        options.add_argument("--headless")
        print("Running in headless mode")

    return webdriver.Chrome(options=options)
```

### 3. 資源載入控制
```python
def setup_request_interception(driver):
    """設定請求攔截"""
    # 啟用網路域
    driver.execute_cdp_cmd("Network.enable", {})

    # 設定要阻擋的資源類型
    blocked_types = ["Image", "Font", "Media", "Stylesheet"]

    # 攔截請求
    def interceptor(request):
        if request["resourceType"] in blocked_types:
            return {"errorReason": "BlockedByClient"}

    # 註冊攔截器
    driver.execute_cdp_cmd("Network.setRequestInterception", {
        "patterns": [{"urlPattern": "*", "resourceType": "Document"}]
    })

def optimize_page_load(driver, url):
    """優化頁面載入"""
    # 設定頁面載入超時
    driver.set_page_load_timeout(15)

    try:
        driver.get(url)
    except TimeoutException:
        # 如果載入超時，停止載入
        driver.execute_script("window.stop();")
        print("Page load timeout, stopped loading")

    # 等待關鍵元素載入
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
```

### 4. 記憶體管理
```python
import gc
import psutil
import os

def monitor_memory_usage():
    """監控記憶體使用情況"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
    return memory_info.rss

def cleanup_driver_resources(driver):
    """清理驅動程式資源"""
    try:
        # 清除快取
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")

        # 刪除所有 Cookie
        driver.delete_all_cookies()

        # 關閉所有分頁
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()

        # 回到主分頁
        if driver.window_handles:
            driver.switch_to.window(driver.window_handles[0])

        # 強制垃圾回收
        gc.collect()

    except Exception as exc:
        print(f"Cleanup failed: {exc}")

def periodic_memory_cleanup(driver, interval=300):
    """定期記憶體清理"""
    import threading
    import time

    def cleanup_worker():
        while True:
            time.sleep(interval)
            cleanup_driver_resources(driver)
            print("Periodic cleanup completed")

    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
```

## 除錯和測試

### 1. 截圖和錄影
```python
import os
import datetime

def take_screenshot(driver, name="screenshot"):
    """拍攝螢幕截圖"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"

    # 確保目錄存在
    os.makedirs("screenshots", exist_ok=True)
    filepath = os.path.join("screenshots", filename)

    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")
    return filepath

def take_element_screenshot(driver, element, name="element"):
    """拍攝元素截圖"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"

    os.makedirs("screenshots", exist_ok=True)
    filepath = os.path.join("screenshots", filename)

    element.screenshot(filepath)
    print(f"Element screenshot saved: {filepath}")
    return filepath

def auto_screenshot_on_error(func):
    """裝飾器：錯誤時自動截圖"""
    @wraps(func)
    def wrapper(driver, *args, **kwargs):
        try:
            return func(driver, *args, **kwargs)
        except Exception as exc:
            error_screenshot = take_screenshot(driver, f"error_{func.__name__}")
            print(f"Error occurred, screenshot saved: {error_screenshot}")
            raise exc
    return wrapper
```

### 2. 日誌收集
```python
import logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def setup_browser_logging():
    """設定瀏覽器日誌收集"""
    # 啟用瀏覽器日誌
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {
        'browser': 'ALL',
        'driver': 'ALL',
        'performance': 'ALL'
    }

    return caps

def collect_browser_logs(driver):
    """收集瀏覽器日誌"""
    logs = {
        'browser': driver.get_log('browser'),
        'driver': driver.get_log('driver'),
        'performance': driver.get_log('performance')
    }

    return logs

def setup_custom_logging():
    """設定自訂日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('selenium_automation.log'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)

# 使用範例
logger = setup_custom_logging()

@auto_screenshot_on_error
def logged_operation(driver, operation_name):
    """記錄的操作"""
    logger.info(f"Starting operation: {operation_name}")

    try:
        # 執行操作
        result = perform_operation(driver)
        logger.info(f"Operation {operation_name} completed successfully")
        return result

    except Exception as exc:
        logger.error(f"Operation {operation_name} failed: {exc}")

        # 收集除錯資訊
        logs = collect_browser_logs(driver)
        logger.error(f"Browser logs: {logs}")

        raise exc
```

### 3. 網路監控
```python
def monitor_network_performance(driver):
    """監控網路效能"""
    # 獲取效能日誌
    perf_logs = driver.get_log('performance')

    network_events = []
    for log in perf_logs:
        message = json.loads(log['message'])
        if message['message']['method'].startswith('Network.'):
            network_events.append(message)

    return network_events

def analyze_page_load_timing(driver):
    """分析頁面載入時間"""
    timing_script = """
        return {
            navigationStart: performance.timing.navigationStart,
            loadEventEnd: performance.timing.loadEventEnd,
            domContentLoaded: performance.timing.domContentLoadedEventEnd,
            firstPaint: performance.getEntriesByType('paint')[0].startTime,
            firstContentfulPaint: performance.getEntriesByType('paint')[1].startTime
        };
    """

    timing = driver.execute_script(timing_script)

    # 計算各階段時間
    total_load_time = timing['loadEventEnd'] - timing['navigationStart']
    dom_load_time = timing['domContentLoaded'] - timing['navigationStart']

    print(f"Total load time: {total_load_time}ms")
    print(f"DOM load time: {dom_load_time}ms")

    return timing
```

### 4. 效能分析
```python
import time
import json

class PerformanceProfiler:
    """效能分析器"""

    def __init__(self, driver):
        self.driver = driver
        self.start_time = None
        self.operations = []

    def start_profiling(self):
        """開始效能分析"""
        self.start_time = time.time()
        self.operations = []

        # 啟用效能監控
        self.driver.execute_cdp_cmd('Performance.enable', {})

    def log_operation(self, operation_name):
        """記錄操作"""
        current_time = time.time()
        elapsed = current_time - self.start_time if self.start_time else 0

        self.operations.append({
            'operation': operation_name,
            'timestamp': current_time,
            'elapsed': elapsed
        })

    def get_performance_metrics(self):
        """獲取效能指標"""
        metrics = self.driver.execute_cdp_cmd('Performance.getMetrics', {})
        return metrics['metrics']

    def generate_report(self):
        """生成效能報告"""
        metrics = self.get_performance_metrics()

        report = {
            'operations': self.operations,
            'metrics': metrics,
            'total_time': time.time() - self.start_time if self.start_time else 0
        }

        # 保存報告
        with open('performance_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report

# 使用範例
def performance_test_ticket_purchase(driver, config):
    """效能測試搶票流程"""
    profiler = PerformanceProfiler(driver)
    profiler.start_profiling()

    try:
        profiler.log_operation("start_navigation")
        driver.get("https://ticketing-site.com")

        profiler.log_operation("login_complete")
        auto_login(driver, config)

        profiler.log_operation("ticket_selection_complete")
        select_ticket_options(driver, config)

        profiler.log_operation("purchase_complete")
        confirm_purchase(driver)

    finally:
        report = profiler.generate_report()
        print(f"Performance test completed in {report['total_time']:.2f} seconds")
```

## 常見問題和解決方案

### 1. 驅動程式問題
```python
# ChromeDriver 版本不匹配
# 解決方案：使用 Selenium Manager 自動管理
driver = webdriver.Chrome()  # Selenium 4.6+ 自動處理

# 手動版本管理
import subprocess

def get_chrome_version():
    """獲取 Chrome 版本"""
    try:
        version = subprocess.check_output([
            'google-chrome', '--version'
        ]).decode('utf-8').strip()
        return version.split()[-1]
    except:
        return None
```

### 2. 元素等待問題
```python
# 常見錯誤：元素找不到
# 錯誤做法
element = driver.find_element(By.ID, "submit")  # 可能失敗

# 正確做法
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "submit")))
```

### 3. 反偵測限制
```python
# Selenium 容易被偵測
# 基本偽裝
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)

# 移除 webdriver 標識
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

## 注意事項

### ⚠️ 重要提醒

1. **瀏覽器相容性**：不同瀏覽器的 WebDriver 實作可能有差異
2. **版本更新**：定期更新 Selenium 和瀏覽器驅動程式
3. **資源管理**：務必在使用後關閉 WebDriver (`driver.quit()`)
4. **反偵測限制**：標準 Selenium 容易被偵測，搶票建議使用 Undetected-Chrome

### 🚫 避免的做法

- 不要忘記設定等待時間 (`implicitly_wait` 或 `WebDriverWait`)
- 不要在高頻操作中使用 `time.sleep()`
- 不要同時開啟過多瀏覽器實例
- 不要忽略異常處理

### ✅ 最佳實踐

- 優先使用 CSS Selector 而非 XPath (更快)
- 使用 Page Object Model 設計模式
- 實作完整的錯誤重試機制
- 定期清理瀏覽器資源
- 使用 Selenium Manager 自動管理驅動程式

---

**更新日期**: 2025-10-28
**適用版本**: Selenium 4.x
**相關文件**: [Undetected-ChromeDriver 指南](./chrome_api_guide.md) | [NoDriver 指南](./nodriver_api_guide.md)