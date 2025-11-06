# 工具函式介面契約

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：定義 util.py 提供的共享工具函式的介面和行為契約。

---

## 概述

本文件定義 `util.py` 中所有共享工具函式的介面，這些函式被所有平台轉接器使用，提供通用功能如 NoDriver 結果解析、暫停檢查、重試邏輯等。

**設計原則**：
- **無狀態**：所有工具函式無副作用，僅依賴輸入參數
- **平台無關**：不包含平台特定邏輯
- **可測試**：每個函式可獨立測試
- **文件完整**：清晰的參數和返回值說明

---

## NoDriver 結果解析

### parse_nodriver_result()

**用途**：安全解析 NoDriver `tab.evaluate()` 返回的結果。

**簽名**：
```python
def parse_nodriver_result(
    result: Any,
    key: str,
    default: Any = None
) -> Any
```

**參數**：
- `result`：NoDriver `tab.evaluate()` 的返回值（通常是 dict）
- `key`：要擷取的鍵名
- `default`：鍵不存在時的預設值

**返回值**：
- `result[key]` 如果存在
- `default` 如果不存在

**範例**：
```python
# JavaScript 返回 {success: true, dates: [...]}
result = await tab.evaluate('''
    (() => {
        return {success: true, dates: ['2025/10/15', '2025/10/16']};
    })()
''')

# 安全解析
success = parse_nodriver_result(result, 'success', False)  # True
dates = parse_nodriver_result(result, 'dates', [])         # ['2025/10/15', '2025/10/16']
missing = parse_nodriver_result(result, 'missing', None)   # None
```

**錯誤處理**：
- 如果 `result` 不是 dict，返回 `default`
- 如果 `key` 不存在，返回 `default`
- 不拋出異常

---

## 暫停機制（NoDriver 專用）

### check_and_handle_pause()

**用途**：檢查暫停標記檔案，如果存在則阻塞直到檔案被刪除。

**簽名**：
```python
def check_and_handle_pause(config_dict: dict) -> None
```

**參數**：
- `config_dict`：配置字典（讀取 `advanced.verbose`）

**行為**：
1. 檢查 `MAXBOT_INT28_IDLE.txt` 是否存在
2. 如果存在且 `verbose=True`，列印暫停訊息
3. 每 1 秒檢查一次，直到檔案被刪除
4. 檔案刪除後，如果 `verbose=True`，列印繼續訊息

**範例**：
```python
# 在關鍵點呼叫
check_and_handle_pause(config_dict)

# 用戶體驗
# 1. 用戶創建檔案：touch MAXBOT_INT28_IDLE.txt
# 2. 自動化暫停，列印："[PAUSED] 自動化已暫停，刪除檔案以繼續..."
# 3. 用戶手動操作瀏覽器
# 4. 用戶刪除檔案：rm MAXBOT_INT28_IDLE.txt
# 5. 自動化繼續，列印："[RESUMED] 繼續執行"
```

**實作**：
```python
import os
import time

PAUSE_FILE = "MAXBOT_INT28_IDLE.txt"

def check_and_handle_pause(config_dict):
    """檢查並處理暫停標記"""
    if os.path.exists(PAUSE_FILE):
        if config_dict.get("advanced", {}).get("verbose", False):
            print("[PAUSED] 自動化已暫停，刪除檔案以繼續...")

        while os.path.exists(PAUSE_FILE):
            time.sleep(1)

        if config_dict.get("advanced", {}).get("verbose", False):
            print("[RESUMED] 繼續執行")
```

---

### sleep_with_pause_check()

**用途**：同步版本的 sleep，支援暫停檢查。

**簽名**：
```python
def sleep_with_pause_check(seconds: float, config_dict: dict) -> None
```

**參數**：
- `seconds`：睡眠秒數
- `config_dict`：配置字典

**行為**：
1. 睡眠 `seconds` 秒
2. 每 1 秒檢查暫停標記

**範例**：
```python
# Chrome Driver 使用
sleep_with_pause_check(5, config_dict)  # 睡眠 5 秒，支援暫停
```

**實作**：
```python
import time

def sleep_with_pause_check(seconds, config_dict):
    """同步 sleep，支援暫停檢查"""
    elapsed = 0
    while elapsed < seconds:
        check_and_handle_pause(config_dict)
        sleep_chunk = min(1, seconds - elapsed)
        time.sleep(sleep_chunk)
        elapsed += sleep_chunk
```

---

### asyncio_sleep_with_pause_check()

**用途**：非同步版本的 sleep，支援暫停檢查。

**簽名**：
```python
async def asyncio_sleep_with_pause_check(
    seconds: float,
    config_dict: dict
) -> None
```

**參數**：
- `seconds`：睡眠秒數
- `config_dict`：配置字典

**範例**：
```python
# NoDriver 使用
await asyncio_sleep_with_pause_check(5, config_dict)
```

**實作**：
```python
import asyncio

async def asyncio_sleep_with_pause_check(seconds, config_dict):
    """非同步 sleep，支援暫停檢查"""
    elapsed = 0
    while elapsed < seconds:
        check_and_handle_pause(config_dict)
        sleep_chunk = min(1, seconds - elapsed)
        await asyncio.sleep(sleep_chunk)
        elapsed += sleep_chunk
```

---

### evaluate_with_pause_check()

**用途**：NoDriver `tab.evaluate()` 的包裝器，執行前檢查暫停。

**簽名**：
```python
async def evaluate_with_pause_check(
    tab: nodriver.Tab,
    js_code: str,
    config_dict: dict
) -> Any
```

**參數**：
- `tab`：NoDriver Tab 物件
- `js_code`：要執行的 JavaScript 程式碼
- `config_dict`：配置字典

**返回值**：
- `tab.evaluate()` 的結果

**範例**：
```python
result = await evaluate_with_pause_check(tab, '''
    (() => {
        return {success: true};
    })()
''', config_dict)
```

**實作**：
```python
async def evaluate_with_pause_check(tab, js_code, config_dict):
    """執行 JavaScript 前檢查暫停"""
    check_and_handle_pause(config_dict)
    return await tab.evaluate(js_code)
```

---

### with_pause_check()

**用途**：通用裝飾器，為任何函式加入暫停檢查。

**簽名**：
```python
def with_pause_check(func):
    """裝飾器：執行前檢查暫停"""
    def wrapper(config_dict, *args, **kwargs):
        check_and_handle_pause(config_dict)
        return func(config_dict, *args, **kwargs)
    return wrapper
```

**範例**：
```python
@with_pause_check
def my_function(config_dict, param1, param2):
    # 執行前自動檢查暫停
    return param1 + param2

result = my_function(config_dict, 1, 2)
```

---

## 重試邏輯

### retry_with_backoff()

**用途**：指數退避重試包裝器（非同步版本）。

**簽名**：
```python
async def retry_with_backoff(
    operation: Callable,
    max_retry: int = 3,
    base_wait: float = 0.5,
    config_dict: dict = None
) -> Any
```

**參數**：
- `operation`：要重試的非同步函式（無參數）
- `max_retry`：最大重試次數
- `base_wait`：基礎等待時間（秒）
- `config_dict`：配置字典（可選，用於暫停檢查）

**返回值**：
- `operation()` 的返回值

**拋出異常**：
- 如果所有重試都失敗，拋出最後一次的異常

**重試策略**：
1. 第 1 次：立即執行
2. 第 2 次：等待 0.5s（基礎時間）
3. 第 3 次：等待 1s（2^1 * 0.5）
4. 第 4 次：等待 2s（2^2 * 0.5）
5. 每次加入 0-0.2s 隨機抖動

**範例**：
```python
async def risky_operation():
    # 可能失敗的操作
    result = await tab.evaluate('...')
    if not result.get('success'):
        raise Exception("操作失敗")
    return result

# 使用重試包裝
result = await retry_with_backoff(risky_operation, max_retry=5)
```

**實作**：
```python
import asyncio
import random

async def retry_with_backoff(operation, max_retry=3, base_wait=0.5, config_dict=None):
    """指數退避重試"""
    for retry_count in range(max_retry):
        try:
            return await operation()
        except Exception as exc:
            if retry_count < max_retry - 1:
                # 計算等待時間
                wait_time = base_wait * (2 ** retry_count)
                wait_time += random.uniform(0, 0.2)  # 抖動

                # 等待（支援暫停）
                if config_dict:
                    await asyncio_sleep_with_pause_check(wait_time, config_dict)
                else:
                    await asyncio.sleep(wait_time)
            else:
                # 最後一次失敗，拋出異常
                raise exc
```

---

### retry_with_backoff_sync()

**用途**：指數退避重試包裝器（同步版本）。

**簽名**：
```python
def retry_with_backoff_sync(
    operation: Callable,
    max_retry: int = 3,
    base_wait: float = 0.5,
    config_dict: dict = None
) -> Any
```

**範例**：
```python
def risky_sync_operation():
    driver.find_element(By.CSS_SELECTOR, "#button").click()

# 使用重試包裝
retry_with_backoff_sync(risky_sync_operation, max_retry=5)
```

---

## 關鍵字匹配

### match_keywords()

**用途**：在文字列表中匹配關鍵字（支援多個關鍵字）。

**簽名**：
```python
def match_keywords(
    texts: List[str],
    keywords: str,
    case_sensitive: bool = False
) -> Optional[int]
```

**參數**：
- `texts`：候選文字列表
- `keywords`：關鍵字字串（逗號分隔）
- `case_sensitive`：是否區分大小寫

**返回值**：
- 匹配到的第一個索引（int）
- 如果無匹配，返回 `None`

**範例**：
```python
dates = ["2025/10/15 (日)", "2025/10/16 (一)", "2025/10/17 (二)"]
keywords = "10/15,10/16"

index = match_keywords(dates, keywords)
# 返回 0（匹配到 "10/15"）

index = match_keywords(dates, "10/20")
# 返回 None（無匹配）
```

**實作**：
```python
def match_keywords(texts, keywords, case_sensitive=False):
    """在文字列表中匹配關鍵字"""
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

    for keyword in keyword_list:
        for i, text in enumerate(texts):
            # 大小寫處理
            search_text = text if case_sensitive else text.lower()
            search_keyword = keyword if case_sensitive else keyword.lower()

            if search_keyword in search_text:
                return i

    return None
```

---

### select_by_mode()

**用途**：根據模式從列表中選擇元素。

**簽名**：
```python
def select_by_mode(
    items: List[Any],
    mode: str
) -> Optional[Any]
```

**參數**：
- `items`：候選項列表
- `mode`：選擇模式
  - `"from top to bottom"`：選擇第一個
  - `"from bottom to top"`：選擇最後一個
  - `"center"`：選擇中間
  - `"random"`：隨機選擇

**返回值**：
- 選擇的元素
- 如果列表為空，返回 `None`

**範例**：
```python
areas = ["VIP區", "搖滾區A", "搖滾區B", "一般區"]

select_by_mode(areas, "from top to bottom")  # "VIP區"
select_by_mode(areas, "from bottom to top")  # "一般區"
select_by_mode(areas, "center")              # "搖滾區A" 或 "搖滾區B"
select_by_mode(areas, "random")              # 隨機
```

**實作**：
```python
import random

def select_by_mode(items, mode):
    """根據模式選擇元素"""
    if not items:
        return None

    if mode == "from top to bottom":
        return items[0]
    elif mode == "from bottom to top":
        return items[-1]
    elif mode == "center":
        return items[len(items) // 2]
    elif mode == "random":
        return random.choice(items)
    else:
        # 未知模式，預設為第一個
        return items[0]
```

---

## 配置讀取

### get_config_value()

**用途**：安全讀取巢狀配置值，支援預設值。

**簽名**：
```python
def get_config_value(
    config_dict: dict,
    *keys: str,
    default: Any = None
) -> Any
```

**參數**：
- `config_dict`：配置字典
- `*keys`：巢狀鍵路徑（可變參數）
- `default`：預設值

**返回值**：
- 配置值（如果存在）
- `default`（如果不存在）

**範例**：
```python
config_dict = {
    "date_auto_select": {
        "enable": True,
        "date_keyword": "10/15"
    }
}

# 讀取巢狀值
enable = get_config_value(config_dict, "date_auto_select", "enable", default=False)
# 返回 True

# 讀取不存在的值
mode = get_config_value(config_dict, "date_auto_select", "mode", default="from top to bottom")
# 返回 "from top to bottom"（預設值）

# 讀取深層巢狀
sid = get_config_value(config_dict, "advanced", "tixcraft_sid", default="")
# 返回 ""（不存在）
```

**實作**：
```python
def get_config_value(config_dict, *keys, default=None):
    """安全讀取巢狀配置值"""
    value = config_dict
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
```

---

## 驗證碼處理

### recognize_captcha()

**用途**：使用 ddddocr 辨識驗證碼圖片。

**簽名**：
```python
def recognize_captcha(
    image_bytes: bytes,
    use_beta: bool = False
) -> str
```

**參數**：
- `image_bytes`：驗證碼圖片的二進制資料
- `use_beta`：是否使用 beta 模型

**返回值**：
- 辨識的文字（str）
- 如果辨識失敗，返回空字串 `""`

**範例**：
```python
# 取得驗證碼圖片
captcha_bytes = await get_captcha_image(tab)

# 辨識
captcha_text = recognize_captcha(captcha_bytes, use_beta=False)

if captcha_text:
    print(f"[CAPTCHA] 辨識結果：{captcha_text}")
else:
    print("[CAPTCHA] 辨識失敗")
```

**實作**：
```python
import ddddocr

# 全域 OCR 實例（避免重複初始化）
_ocr_standard = None
_ocr_beta = None

def recognize_captcha(image_bytes, use_beta=False):
    """辨識驗證碼"""
    global _ocr_standard, _ocr_beta

    try:
        # 初始化 OCR
        if use_beta:
            if _ocr_beta is None:
                _ocr_beta = ddddocr.DdddOcr(beta=True)
            ocr = _ocr_beta
        else:
            if _ocr_standard is None:
                _ocr_standard = ddddocr.DdddOcr()
            ocr = _ocr_standard

        # 辨識
        text = ocr.classification(image_bytes)

        # 基本驗證
        if len(text) >= 4 and text.isalnum():
            return text
        else:
            return ""

    except Exception as exc:
        print(f"[ERROR] 驗證碼辨識失敗：{exc}")
        return ""
```

---

### validate_captcha_text()

**用途**：驗證驗證碼文字是否合法。

**簽名**：
```python
def validate_captcha_text(text: str, min_length: int = 4) -> bool
```

**參數**：
- `text`：驗證碼文字
- `min_length`：最小長度

**返回值**：
- `True`：文字合法
- `False`：文字不合法

**驗證規則**：
1. 長度 >= `min_length`
2. 僅包含字母和數字

**範例**：
```python
validate_captcha_text("AB12")    # True
validate_captcha_text("ABCD56")  # True
validate_captcha_text("AB1")     # False（長度不足）
validate_captcha_text("AB@1")    # False（包含特殊字符）
```

**實作**：
```python
def validate_captcha_text(text, min_length=4):
    """驗證驗證碼文字"""
    return len(text) >= min_length and text.isalnum()
```

---

## 字串處理

### normalize_whitespace()

**用途**：標準化字串空白（移除多餘空白）。

**簽名**：
```python
def normalize_whitespace(text: str) -> str
```

**範例**：
```python
normalize_whitespace("  VIP區   $3000  ")
# 返回 "VIP區 $3000"

normalize_whitespace("2025/10/15\n(日)\t19:30")
# 返回 "2025/10/15 (日) 19:30"
```

**實作**：
```python
def normalize_whitespace(text):
    """標準化空白"""
    import re
    # 將多個空白字符（空格、Tab、換行）替換為單一空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

---

### extract_price()

**用途**：從字串中提取價格數字。

**簽名**：
```python
def extract_price(text: str) -> Optional[int]
```

**參數**：
- `text`：包含價格的文字（例如 "VIP區 $3000"）

**返回值**：
- 價格數字（int）
- 如果找不到，返回 `None`

**範例**：
```python
extract_price("VIP區 $3000")       # 3000
extract_price("搖滾區A NT$2000")   # 2000
extract_price("一般區 500 元")     # 500
extract_price("免費")              # None
```

**實作**：
```python
import re

def extract_price(text):
    """提取價格"""
    # 匹配數字（可能包含逗號）
    match = re.search(r'[\$NT]?\s*(\d{1,3}(?:,\d{3})*|\d+)', text)
    if match:
        price_str = match.group(1).replace(',', '')
        return int(price_str)
    return None
```

---

## 日期/時間處理

### parse_date_string()

**用途**：解析日期字串為標準格式。

**簽名**：
```python
def parse_date_string(date_str: str) -> Optional[str]
```

**參數**：
- `date_str`：原始日期字串（例如 "2025/10/15 (日) 19:30"）

**返回值**：
- 標準化日期字串 `"YYYY/MM/DD"`
- 如果解析失敗，返回 `None`

**範例**：
```python
parse_date_string("2025/10/15 (日) 19:30")  # "2025/10/15"
parse_date_string("10/15")                  # "2025/10/15"（假設當年）
parse_date_string("15日")                   # None（無法解析）
```

**實作**：
```python
import re
from datetime import datetime

def parse_date_string(date_str):
    """解析日期字串"""
    # 匹配 YYYY/MM/DD 格式
    match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}/{month.zfill(2)}/{day.zfill(2)}"

    # 匹配 MM/DD 格式（假設當年）
    match = re.search(r'(\d{1,2})/(\d{1,2})', date_str)
    if match:
        month, day = match.groups()
        current_year = datetime.now().year
        return f"{current_year}/{month.zfill(2)}/{day.zfill(2)}"

    return None
```

---

## Cookie 處理

### format_cookie_for_cdp()

**用途**：將 cookie 字典格式化為 CDP 格式。

**簽名**：
```python
def format_cookie_for_cdp(
    name: str,
    value: str,
    domain: str,
    path: str = "/",
    secure: bool = True,
    http_only: bool = True
) -> dict
```

**參數**：
- `name`：Cookie 名稱
- `value`：Cookie 值
- `domain`：域名（例如 ".tixcraft.com"）
- `path`：路徑（預設 "/"）
- `secure`：是否為 Secure Cookie
- `http_only`：是否為 HttpOnly Cookie

**返回值**：
- CDP 格式的 cookie 字典

**範例**：
```python
cookie = format_cookie_for_cdp(
    name="tixcraft_sid",
    value="abc123",
    domain=".tixcraft.com"
)

# 使用 CDP 注入
await tab.send(cdp.network.set_cookie(**cookie))
```

**實作**：
```python
def format_cookie_for_cdp(name, value, domain, path="/", secure=True, http_only=True):
    """格式化 Cookie 為 CDP 格式"""
    return {
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "secure": secure,
        "httpOnly": http_only
    }
```

---

### format_cookie_for_selenium()

**用途**：將 cookie 字典格式化為 Selenium 格式。

**簽名**：
```python
def format_cookie_for_selenium(
    name: str,
    value: str,
    domain: str,
    path: str = "/",
    secure: bool = True,
    http_only: bool = True
) -> dict
```

**範例**：
```python
cookie = format_cookie_for_selenium(
    name="tixcraft_sid",
    value="abc123",
    domain=".tixcraft.com"
)

# 使用 Selenium 注入
driver.add_cookie(cookie)
```

**實作**：
```python
def format_cookie_for_selenium(name, value, domain, path="/", secure=True, http_only=True):
    """格式化 Cookie 為 Selenium 格式"""
    return {
        'name': name,
        'value': value,
        'domain': domain,
        'path': path,
        'secure': secure,
        'httpOnly': http_only
    }
```

---

## 瀏覽器偵測

### is_headless_mode()

**用途**：檢查是否為無頭模式。

**簽名**：
```python
def is_headless_mode(config_dict: dict) -> bool
```

**返回值**：
- `True`：無頭模式
- `False`：有頭模式

**範例**：
```python
if is_headless_mode(config_dict):
    print("[INFO] 執行於無頭模式")
```

**實作**：
```python
def is_headless_mode(config_dict):
    """檢查是否為無頭模式"""
    return get_config_value(config_dict, "advanced", "headless", default=False)
```

---

## 音效提醒

### play_alert_sound()

**用途**：播放音效提醒（手動介入時）。

**簽名**：
```python
def play_alert_sound() -> None
```

**行為**：
- 播放系統提示音
- 如果失敗，靜默處理（不拋出異常）

**範例**：
```python
# 需要手動介入時
if manual_selection_required:
    play_alert_sound()
    print("[MANUAL] 請手動選擇日期")
```

**實作**（跨平台）：
```python
def play_alert_sound():
    """播放音效提醒"""
    try:
        import platform
        import os

        system = platform.system()
        if system == "Windows":
            import winsound
            winsound.MessageBeep()
        elif system == "Darwin":  # macOS
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        else:  # Linux
            os.system('paplay /usr/share/sounds/freedesktop/stereo/bell.oga')
    except Exception:
        # 靜默失敗
        pass
```

---

## 日誌輔助

### log_with_stage()

**用途**：根據 `verbose` 設定條件性列印日誌。

**簽名**：
```python
def log_with_stage(
    stage: str,
    message: str,
    config_dict: dict
) -> None
```

**參數**：
- `stage`：階段代號（例如 "DATE"、"AREA"）
- `message`：日誌訊息
- `config_dict`：配置字典

**行為**：
- 如果 `config_dict["advanced"]["verbose"] == True`，列印日誌
- 格式：`[{stage}] {message}`

**範例**：
```python
log_with_stage("DATE", "找到 3 個可用日期", config_dict)
# 輸出（如果 verbose=True）："[DATE] 找到 3 個可用日期"
```

**實作**：
```python
def log_with_stage(stage, message, config_dict):
    """條件性列印日誌"""
    if get_config_value(config_dict, "advanced", "verbose", default=False):
        print(f"[{stage}] {message}")
```

---

## 錯誤格式化

### format_error_message()

**用途**：格式化錯誤訊息以供日誌記錄。

**簽名**：
```python
def format_error_message(
    stage: str,
    error: Exception
) -> str
```

**參數**：
- `stage`：發生錯誤的階段
- `error`：異常物件

**返回值**：
- 格式化的錯誤訊息字串

**範例**：
```python
try:
    await nodriver_tixcraft_date_auto_select(tab, url, config_dict)
except Exception as exc:
    error_msg = format_error_message("DATE", exc)
    print(error_msg)
    # 輸出："[ERROR] 階段 DATE 失敗：ElementNotFoundError - 找不到日期元素"
```

**實作**：
```python
def format_error_message(stage, error):
    """格式化錯誤訊息"""
    error_type = type(error).__name__
    error_str = str(error)
    return f"[ERROR] 階段 {stage} 失敗：{error_type} - {error_str}"
```

---

## 測試輔助

### create_mock_config()

**用途**：創建測試用的模擬配置字典。

**簽名**：
```python
def create_mock_config(**overrides) -> dict
```

**參數**：
- `**overrides`：要覆寫的配置鍵值對

**返回值**：
- 完整的測試配置字典

**範例**：
```python
# 創建預設測試配置
config = create_mock_config()

# 覆寫特定值
config = create_mock_config(
    ticket_number=4,
    date_auto_select={"enable": True, "date_keyword": "10/15"}
)

# 用於單元測試
async def test_date_select():
    config = create_mock_config()
    result = await nodriver_tixcraft_date_auto_select(tab, "", config)
    assert result == True
```

**實作**：
```python
def create_mock_config(**overrides):
    """創建測試配置"""
    config = {
        "homepage": "https://example.com",
        "webdriver_type": "nodriver",
        "ticket_number": 2,
        "date_auto_select": {
            "enable": True,
            "date_keyword": "",
            "mode": "from top to bottom"
        },
        "area_auto_select": {
            "enable": True,
            "area_keyword": "",
            "mode": "from top to bottom"
        },
        "ocr_captcha": {
            "enable": True,
            "beta": False,
            "force_submit": True,
            "retry": 3
        },
        "advanced": {
            "verbose": False,
            "headless": False
        }
    }

    # 應用覆寫
    for key, value in overrides.items():
        config[key] = value

    return config
```

---

## 函式索引

### 核心工具（必需）

| 函式 | 用途 | 版本 |
|------|------|------|
| `parse_nodriver_result()` | 安全解析 NoDriver 結果 | 通用 |
| `get_config_value()` | 安全讀取配置值 | 通用 |
| `log_with_stage()` | 條件性列印日誌 | 通用 |
| `format_error_message()` | 格式化錯誤訊息 | 通用 |

### 暫停機制（NoDriver）

| 函式 | 用途 | 版本 |
|------|------|------|
| `check_and_handle_pause()` | 檢查暫停標記 | NoDriver |
| `sleep_with_pause_check()` | 同步 sleep（支援暫停） | 通用 |
| `asyncio_sleep_with_pause_check()` | 非同步 sleep（支援暫停） | NoDriver |
| `evaluate_with_pause_check()` | tab.evaluate 包裝器 | NoDriver |

### 重試邏輯

| 函式 | 用途 | 版本 |
|------|------|------|
| `retry_with_backoff()` | 指數退避重試（非同步） | NoDriver |
| `retry_with_backoff_sync()` | 指數退避重試（同步） | Chrome Driver |

### 選擇邏輯

| 函式 | 用途 | 版本 |
|------|------|------|
| `match_keywords()` | 關鍵字匹配 | 通用 |
| `select_by_mode()` | 根據模式選擇 | 通用 |

### 驗證碼處理

| 函式 | 用途 | 版本 |
|------|------|------|
| `recognize_captcha()` | 驗證碼辨識 | 通用 |
| `validate_captcha_text()` | 驗證碼文字驗證 | 通用 |

### 字串處理

| 函式 | 用途 | 版本 |
|------|------|------|
| `normalize_whitespace()` | 標準化空白 | 通用 |
| `extract_price()` | 提取價格 | 通用 |
| `parse_date_string()` | 解析日期 | 通用 |

### Cookie 處理

| 函式 | 用途 | 版本 |
|------|------|------|
| `format_cookie_for_cdp()` | 格式化 CDP Cookie | NoDriver |
| `format_cookie_for_selenium()` | 格式化 Selenium Cookie | Chrome Driver |

### 其他輔助

| 函式 | 用途 | 版本 |
|------|------|------|
| `play_alert_sound()` | 播放音效提醒 | 通用 |
| `is_headless_mode()` | 檢查無頭模式 | 通用 |
| `create_mock_config()` | 創建測試配置 | 測試專用 |

---

## 使用範例

### 完整工作流程範例

```python
async def example_workflow(tab, url, config_dict):
    """示範使用多個工具函式的完整工作流程"""

    # 1. 日誌記錄
    log_with_stage("INIT", "開始執行工作流程", config_dict)

    # 2. 讀取配置
    date_keyword = get_config_value(
        config_dict,
        "date_auto_select",
        "date_keyword",
        default=""
    )

    # 3. 支援暫停的 sleep
    await asyncio_sleep_with_pause_check(2, config_dict)

    # 4. 帶重試的操作
    async def get_dates():
        result = await tab.evaluate('''
            (() => {
                const dates = Array.from(document.querySelectorAll(".date"))
                    .map(el => el.textContent.trim());
                return {success: true, dates: dates};
            })()
        ''')
        if not result.get('success'):
            raise Exception("無法取得日期")
        return result

    result = await retry_with_backoff(get_dates, max_retry=5, config_dict=config_dict)

    # 5. 解析結果
    dates = parse_nodriver_result(result, 'dates', [])
    log_with_stage("DATE", f"找到 {len(dates)} 個可用日期", config_dict)

    # 6. 關鍵字匹配
    matched_index = match_keywords(dates, date_keyword)

    # 7. 回退到模式選擇
    if matched_index is None:
        mode = get_config_value(config_dict, "date_auto_select", "mode", default="from top to bottom")
        selected_date = select_by_mode(dates, mode)
    else:
        selected_date = dates[matched_index]

    log_with_stage("DATE", f"選擇日期：{selected_date}", config_dict)

    return True
```

---

## 測試契約

所有工具函式應包含單元測試：

```python
import pytest

def test_match_keywords():
    """測試關鍵字匹配"""
    texts = ["2025/10/15", "2025/10/16", "2025/10/17"]

    # 測試單一關鍵字
    assert match_keywords(texts, "10/15") == 0

    # 測試多個關鍵字
    assert match_keywords(texts, "10/20,10/16") == 1

    # 測試無匹配
    assert match_keywords(texts, "10/20") is None

    # 測試大小寫
    texts_upper = ["VIP區", "搖滾區", "一般區"]
    assert match_keywords(texts_upper, "vip", case_sensitive=False) == 0
    assert match_keywords(texts_upper, "vip", case_sensitive=True) is None


def test_select_by_mode():
    """測試模式選擇"""
    items = [1, 2, 3, 4, 5]

    assert select_by_mode(items, "from top to bottom") == 1
    assert select_by_mode(items, "from bottom to top") == 5
    assert select_by_mode(items, "center") == 3
    assert select_by_mode([], "from top to bottom") is None


def test_get_config_value():
    """測試配置值讀取"""
    config = {
        "level1": {
            "level2": {
                "value": 42
            }
        }
    }

    assert get_config_value(config, "level1", "level2", "value") == 42
    assert get_config_value(config, "level1", "missing", default=0) == 0
    assert get_config_value(config, "missing", "path", default=None) is None
```

---

**文件狀態**：工具函式介面契約完成
**最後更新**：2025-10-16
**下一步**：創建 config-schema.md 記錄配置 schema
