# Undetected-ChromeDriver API 使用指南

> **目標**：專為搶票系統設計的 ChromeDriver 反偵測指南，提供完整的 API 使用方法和最佳實踐

**官方專案**: https://github.com/ultrafunkamsterdam/undetected-chromedriver

## 核心原則

1. **反偵測優先**：自動繞過 CloudFlare、Distil、Imperva 等反機器人系統
2. **Selenium 相容**：完全相容 Selenium WebDriver API
3. **自動管理**：自動下載和配置 ChromeDriver
4. **簡化初始化**：最少設定即可運行

## 與其他 WebDriver 的比較

| 特性 | Undetected-Chrome | Selenium Chrome | NoDriver |
|------|------------------|-----------------|----------|
| 反偵測能力 | ✅ 強 | ❌ 無 | ✅ 極強 |
| API 學習成本 | 🟡 低 (Selenium 相容) | 🟢 最低 | 🔴 高 (async/await) |
| 穩定性 | ✅ 高 | ✅ 最高 | 🟡 中等 |
| 搶票適用性 | ✅ 優秀 | ❌ 差 | ✅ 最佳 |

## 安裝與設置

### 1. 基本安裝
```bash
pip install undetected-chromedriver
```

### 2. 自動 ChromeDriver 管理
```python
import undetected_chromedriver as uc

# 自動下載和配置 ChromeDriver
driver = uc.Chrome()
```

### 3. 手動指定 ChromeDriver 路徑
```python
import undetected_chromedriver as uc

driver = uc.Chrome(
    driver_executable_path='/path/to/chromedriver',
    options=options
)
```

## Chrome 選項配置

### 1. 基本選項設定
```python
import undetected_chromedriver as uc

def get_uc_options(config_dict, webdriver_path):
    """建立 UC Chrome 選項"""
    options = uc.ChromeOptions()

    # 頁面載入策略
    options.page_load_strategy = 'eager'  # 推薦：加快載入速度
    # options.page_load_strategy = 'none'   # 最快但需手動等待

    # 未處理提示行為
    options.unhandled_prompt_behavior = "accept"

    return options
```

### 2. 進階選項配置
```python
def get_advanced_uc_options(config_dict):
    """進階 UC Chrome 選項"""
    options = uc.ChromeOptions()

    # Performance 日誌收集 (適用於 TicketPlus 等需要效能監控的網站)
    performace_sites = ['ticketplus', 'tixcraft']
    if any(site in config_dict["homepage"] for site in performace_sites):
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # 禁用圖片載入 (提升速度)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    # 禁用擴充功能
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")

    return options
```

### 3. 擴充套件載入
```python
def load_chrome_extensions(options, webdriver_path, config_dict):
    """載入 Chrome 擴充套件"""
    extension_list = []

    if config_dict["advanced"]["chrome_extension"]:
        extension_list = get_favoriate_extension_path(webdriver_path, config_dict)

    load_extension_path = ""
    for ext in extension_list:
        ext = ext.replace('.crx', '')
        if os.path.exists(ext):
            # 同步配置到擴充套件
            if "maxbot" in ext:
                util.dump_settings_to_maxbot_plus_extension(ext, config_dict)
            load_extension_path += ("," + os.path.abspath(ext))

    if load_extension_path:
        options.add_argument(f"--load-extension={load_extension_path[1:]}")

    return options
```

## 驅動程式初始化

### 1. 基本初始化模式
```python
import undetected_chromedriver as uc

def init_uc_driver_basic(config_dict):
    """基本初始化"""
    try:
        options = get_uc_options(config_dict)
        driver = uc.Chrome(
            options=options,
            headless=config_dict["advanced"]["headless"]
        )
        return driver
    except Exception as exc:
        print(f"UC Driver initialization failed: {exc}")
        return None
```

### 2. 完整初始化模式 (推薦)
```python
def init_uc_driver_complete(config_dict, webdriver_path):
    """完整的 UC Driver 初始化 - 搶票系統專用"""

    # 1. 檢查 ChromeDriver 路徑
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not exist, downloading...")
        try:
            chromedriver_autoinstaller_max.install(
                path=webdriver_path,
                make_version_dir=False
            )
        except Exception as exc:
            print(f"ChromeDriver download failed: {exc}")
            return None

    # 2. 清理 UC 暫存檔案
    util.clean_uc_exe_cache()

    # 3. 初始化選項
    options = get_uc_options(config_dict, webdriver_path)

    # 4. 平台特殊處理
    launch_with_path = True
    if "macos" in platform.platform().lower():
        if "arm64" in platform.platform().lower():
            launch_with_path = False  # Apple Silicon Mac 不指定路徑

    # 5. 嘗試初始化
    driver = None
    if launch_with_path:
        try:
            driver = uc.Chrome(
                driver_executable_path=chromedriver_path,
                options=options,
                headless=config_dict["advanced"]["headless"]
            )
        except Exception as exc:
            print(f"UC with path failed: {exc}")
            # 失敗時嘗試自動下載
            try:
                driver = uc.Chrome(options=options)
            except Exception as exc2:
                print(f"UC auto download also failed: {exc2}")
    else:
        try:
            driver = uc.Chrome(options=options)
        except Exception as exc:
            print(f"UC without path failed: {exc}")

    return driver
```

### 3. 多視窗管理
```python
def handle_multiple_windows(driver):
    """處理多視窗情況"""
    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            # 關閉額外視窗，保留主視窗
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(f"Closed extra window, keeping main window")
    except Exception as exc:
        print(f"Window management failed: {exc}")
```

## CDP (Chrome DevTools Protocol) 使用

### 1. 網路請求攔截
```python
def setup_network_blocking(driver, config_dict):
    """設定網路請求攔截"""
    try:
        # 啟用網路域
        driver.execute_cdp_cmd('Network.enable', {})

        # 設定要阻擋的 URL 模式
        blocked_urls = [
            '*.woff', '*.woff2', '*.ttf', '*.otf',  # 字體檔案
            '*fonts.googleapis.com/*',              # Google 字體
            '*.ico',                                # 圖示
            '*facebook.com/*', '*.fbcdn.net/*'      # Facebook 追蹤
        ]

        if config_dict["advanced"]["block_facebook_network"]:
            blocked_urls.extend(['*facebook.com/*', '*.fbcdn.net/*'])

        # 執行阻擋
        driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": blocked_urls})

        print(f"Network blocking enabled for {len(blocked_urls)} patterns")

    except Exception as exc:
        print(f"Network blocking setup failed: {exc}")
```

### 2. Performance 監控
```python
def setup_performance_monitoring(driver):
    """設定效能監控"""
    try:
        # 啟用 Performance 域
        driver.execute_cdp_cmd('Performance.enable', {})

        # 啟用 Runtime 域
        driver.execute_cdp_cmd('Runtime.enable', {})

        print("Performance monitoring enabled")

    except Exception as exc:
        print(f"Performance monitoring setup failed: {exc}")

def get_performance_logs(driver):
    """取得效能日誌"""
    try:
        logs = driver.get_log('performance')
        return logs
    except Exception as exc:
        print(f"Failed to get performance logs: {exc}")
        return []
```

### 3. Cookie 和儲存管理
```python
def manage_cookies_and_storage(driver):
    """Cookie 和儲存管理"""
    try:
        # 清除所有 Cookie
        driver.execute_cdp_cmd('Network.clearBrowserCookies', {})

        # 清除本地儲存
        driver.execute_cdp_cmd('DOMStorage.clear', {
            'storageId': {
                'securityOrigin': driver.current_url,
                'isLocalStorage': True
            }
        })

        print("Cookies and storage cleared")

    except Exception as exc:
        print(f"Cookie/storage management failed: {exc}")
```

## Selenium API 相容性

### 1. 標準元素操作
```python
# UC Chrome 完全支援標準 Selenium API
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 元素查找
element = driver.find_element(By.CSS_SELECTOR, 'button.buy-ticket')

# 等待條件
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, 'submit-btn')))

# 元素操作
element.click()
element.send_keys("text")
```

### 2. JavaScript 執行
```python
def execute_js_safely(driver, script, *args):
    """安全執行 JavaScript"""
    try:
        return driver.execute_script(script, *args)
    except Exception as exc:
        print(f"JavaScript execution failed: {exc}")
        return None

# 使用範例
result = execute_js_safely(driver, """
    return document.querySelector('#ticket-area').textContent;
""")
```

### 3. 表單處理
```python
from selenium.webdriver.support.ui import Select

def handle_select_dropdown(driver, selector, value):
    """處理下拉選單"""
    try:
        select_element = driver.find_element(By.CSS_SELECTOR, selector)
        select = Select(select_element)

        # 嘗試多種選擇方式
        try:
            select.select_by_value(value)
        except:
            try:
                select.select_by_visible_text(value)
            except:
                select.select_by_index(0)  # 選擇第一個選項

        return True
    except Exception as exc:
        print(f"Select dropdown failed: {exc}")
        return False
```

## 反偵測最佳實踐

### 1. 瀏覽器指紋偽裝
```python
def setup_anti_detection(options):
    """設定反偵測"""

    # 使用者代理偽裝
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    # 禁用自動化標識
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 禁用 Blink 特性
    options.add_argument("--disable-blink-features=AutomationControlled")

    return options
```

### 2. 隨機化行為
```python
import random
import time

def random_delay(min_sec=0.5, max_sec=2.0):
    """隨機延遲"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def human_like_typing(element, text):
    """模擬人類打字"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))
```

### 3. 錯誤重試機制
```python
def retry_with_backoff(func, max_retries=3, base_delay=1):
    """指數退避重試"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exc:
            if attempt == max_retries - 1:
                raise exc

            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
```

## 搶票系統整合範例

### 1. 票務網站初始化
```python
def init_ticket_driver(config_dict):
    """搶票系統專用初始化"""

    # 1. 設定反偵測選項
    options = uc.ChromeOptions()
    options = setup_anti_detection(options)
    options = get_uc_options(config_dict)

    # 2. 啟用效能監控 (TicketPlus)
    if 'ticketplus' in config_dict.get("homepage", ""):
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # 3. 初始化驅動
    driver = uc.Chrome(options=options)

    # 4. 設定 CDP 功能
    setup_network_blocking(driver, config_dict)

    # 5. 移除自動化標識
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver
```

### 2. 登入處理
```python
def auto_login(driver, config_dict):
    """自動登入處理"""
    try:
        # 等待登入表單載入
        wait = WebDriverWait(driver, 10)

        # 填入帳號密碼
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")

        # 模擬人類打字
        human_like_typing(username_field, config_dict["login"]["username"])
        random_delay(0.3, 0.8)
        human_like_typing(password_field, config_dict["login"]["password"])

        # 點擊登入按鈕
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        random_delay(0.5, 1.0)
        login_btn.click()

        return True

    except Exception as exc:
        print(f"Auto login failed: {exc}")
        return False
```

### 3. 購票流程
```python
def purchase_tickets(driver, config_dict):
    """購票主流程"""

    # 1. 選擇日期
    if not select_event_date(driver, config_dict):
        return False

    # 2. 選擇座位區域
    if not select_seat_area(driver, config_dict):
        return False

    # 3. 選擇票數
    if not select_ticket_count(driver, config_dict):
        return False

    # 4. 處理驗證碼
    if not handle_captcha(driver, config_dict):
        return False

    # 5. 確認購買
    return confirm_purchase(driver, config_dict)
```

## 錯誤處理和除錯

### 1. 常見錯誤處理
```python
def handle_common_errors(driver, exc):
    """處理常見錯誤"""
    error_message = str(exc).lower()

    if "timeout" in error_message:
        print("Timeout error - page may be slow")
        return "retry"

    elif "no such element" in error_message:
        print("Element not found - page structure may have changed")
        return "refresh"

    elif "session deleted" in error_message:
        print("Browser session ended - reinitialize driver")
        return "restart"

    elif "chrome not reachable" in error_message:
        print("Chrome process crashed - restart browser")
        return "restart"

    else:
        print(f"Unknown error: {exc}")
        return "unknown"
```

### 2. 狀態監控
```python
def monitor_driver_health(driver):
    """監控驅動程式健康狀態"""
    try:
        # 檢查頁面標題
        title = driver.title

        # 檢查當前 URL
        current_url = driver.current_url

        # 檢查視窗數量
        window_count = len(driver.window_handles)

        return {
            "healthy": True,
            "title": title,
            "url": current_url,
            "windows": window_count
        }

    except Exception as exc:
        return {
            "healthy": False,
            "error": str(exc)
        }
```

### 3. 清理和關閉
```python
def cleanup_driver(driver):
    """清理驅動程式資源"""
    try:
        if driver:
            # 清除所有 Cookie
            driver.delete_all_cookies()

            # 關閉所有視窗
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                driver.close()

            # 退出驅動程式
            driver.quit()

        # 清理暫存檔案
        util.clean_uc_exe_cache()

        print("Driver cleanup completed")

    except Exception as exc:
        print(f"Driver cleanup failed: {exc}")
```

## 效能優化建議

### 1. 載入策略
```python
# 推薦設定
options.page_load_strategy = 'eager'  # 平衡速度和穩定性

# 極速模式 (需要更多手動等待)
options.page_load_strategy = 'none'
```

### 2. 資源阻擋
```python
# 阻擋不必要的資源
blocked_resources = [
    '*.woff', '*.woff2', '*.ttf', '*.otf',  # 字體
    '*.png', '*.jpg', '*.gif', '*.svg',     # 圖片 (謹慎使用)
    '*analytics*', '*tracking*',            # 追蹤腳本
    '*advertisement*', '*ads*'              # 廣告
]
```

### 3. 記憶體管理
```python
import gc

def optimize_memory():
    """記憶體優化"""
    gc.collect()  # 強制垃圾回收
```

## 注意事項

### ⚠️ 重要提醒

1. **IP 信譽度影響**：UC 只能繞過瀏覽器偵測，無法隱藏 IP 位址
2. **版本相容性**：定期更新以確保與最新 Chrome 版本相容
3. **效能考量**：反偵測功能可能略微影響執行速度
4. **法律合規**：確保使用符合網站服務條款和當地法律

### 🚫 避免的做法

- 不要同時運行太多 UC 實例 (記憶體消耗大)
- 不要在生產環境使用除錯模式
- 不要忽略異常處理
- 不要使用過於激進的自動化腳本

### ✅ 最佳實踐

- 使用適當的延遲模擬人類行為
- 實作完整的錯誤重試機制
- 定期清理瀏覽器暫存和 Cookie
- 監控驅動程式健康狀態

---

**更新日期**: 2025-10-28
**適用版本**: undetected-chromedriver 3.5.x+
**相關文件**: [NoDriver API 指南](./nodriver_api_guide.md)