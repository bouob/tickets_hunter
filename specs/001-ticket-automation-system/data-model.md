# 資料模型與資料結構

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：記錄 Tickets Hunter 系統中使用的核心資料結構、實體和資料流。

---

## 概述

本文件記錄系統中的主要資料結構，包括配置實體、執行時狀態、平台特定資料和瀏覽器自動化物件。這些結構構成系統的「資料語言」，跨越 12 個自動化階段傳遞和轉換。

**設計原則**：
- **配置驅動**：所有行為由 `config_dict` 控制
- **不可變配置**：settings.json 載入後不修改（僅讀取）
- **可變狀態**：執行時狀態（重試計數、錯誤）在函式間傳遞
- **平台無關**：核心資料結構在所有平台間通用

---

## 核心資料結構

### 1. 配置字典（config_dict）

**用途**：從 settings.json 載入的完整用戶配置，控制所有自動化行為。

**結構**：
```python
config_dict = {
    # 基本配置
    "homepage": str,              # 活動頁面 URL
    "webdriver_type": str,        # "nodriver" | "uc" | "selenium"
    "ticket_number": int,         # 購票數量（1-6）

    # 日期選擇配置 (v1.2 更新)
    "date_auto_select": {
        "enable": bool,           # 啟用自動日期選擇
        "date_keyword": str,      # 日期關鍵字（分號分隔）："10/15;10/16"
        "mode": str,              # 回退模式："from top to bottom" | "from bottom to top" | "center" | "random"
        "date_auto_fallback": bool # 關鍵字失敗時是否回退到 mode（預設 false - Strict Mode）
    },

    # 區域選擇配置 (v1.2 更新)
    "area_auto_select": {
        "enable": bool,           # 啟用自動區域選擇
        "area_keyword": str,      # 區域關鍵字（分號分隔）："VIP區;搖滾區A"
        "mode": str,              # 回退模式（同上）
        "area_auto_fallback": bool # 關鍵字失敗時是否回退到 mode（預設 false - Strict Mode）
    },

    # 座位選擇配置
    "seat_auto_select": {
        "enable": bool,           # 啟用自動座位選擇
        "select_mode": str,       # "random" | "from top to bottom"
        "adjacent_seat": bool     # 要求相鄰座位（ibon 專用）
    },

    # 票務資訊配置
    "ticket_form_data": {
        "name": str,              # 購票人姓名
        "email": str,             # 電子郵件
        "phone": str,             # 手機號碼
        "address": str            # 地址（部分平台需要）
    },

    # 驗證碼配置 (v1.2 更新)
    "ocr_captcha": {
        "enable": bool,           # 啟用自動 OCR（圖像驗證碼）
        "beta": bool,             # 使用 beta 模型（較慢但更準確）
        "force_submit": bool,     # OCR 失敗時強制送出
        "retry": int              # OCR 重試次數（1-5）
    },

    # 問答驗證配置 (v1.2 新增)
    "user_guess_string": str,     # 預設答案（活動知識問答），多個答案用分號分隔

    # 進階配置
    "advanced": {
        "verbose": bool,          # 詳細日誌輸出
        "headless": bool,         # 無頭模式（NoDriver/UC）
        "auto_reload_page_interval": float,  # 頁面重載間隔（秒）
        "auto_reload_overheat_count": int,   # 過熱保護：重載次數閾值
        "auto_reload_overheat_cd": float,    # 過熱保護：冷卻時間（秒）
        "tixcraft_sid": str,      # TixCraft session cookie
        "kktix_account": str,     # KKTIX 帳號
        "kktix_password": str,    # KKTIX 密碼
        "ibon_ibonqware": str,    # ibon session cookie
        "kham_tk": str            # KHAM session cookie
    },

    # 瀏覽器配置（NoDriver 專用）
    "browser_args": [str],        # Chrome 命令列參數列表

    # 付款配置（保留欄位，未實作）
    "payment": {
        "method": str,            # "credit_card" | "convenience_store" | "atm"
        "auto_pay": bool          # 自動付款（未實作）
    }
}
```

**載入方式**：
```python
import json

# 從命令列參數載入
with open(args.input, 'r', encoding='utf-8') as f:
    config_dict = json.load(f)

# 在函式間作為參數傳遞
await nodriver_tixcraft_main(tab, url, config_dict)
```

**不可變性**：
- config_dict 在載入後不應被修改
- 所有函式以唯讀方式存取配置
- 執行時狀態使用獨立變數追蹤

---

### 2. 瀏覽器自動化物件

#### 2.1 NoDriver 物件

**Browser 物件**：
```python
# 瀏覽器實例（整個執行期間持續）
browser: nodriver.Browser
  .config: BrowserConfig          # 瀏覽器配置
  .connection: Connection         # CDP 連線
  .tabs: List[Tab]                # 所有分頁列表

# 主要操作
browser = await nodriver.start(browser_args=args)
tab = await browser.get(url)
await browser.stop()
```

**Tab 物件**（主要互動介面）：
```python
# 分頁實例（頁面情境）
tab: nodriver.Tab
  .target: Target                 # CDP Target
  .connection: Connection         # CDP 連線

# 主要操作
await tab.get(url)                           # 導航到 URL
await tab.sleep(seconds)                     # 等待
result = await tab.evaluate(js_code)        # 執行 JavaScript
await tab.reload()                           # 重載頁面
element = await tab.find(selector)           # 查找元素（避免使用）
elements = await tab.find_all(selector)      # 查找多個元素（資訊用）
```

**Element 物件**（僅資訊擷取，避免互動）：
```python
# 元素物件（容易過期，避免 .click()/.send_keys()）
element: nodriver.Element
  .node_id: int                   # CDP 節點 ID
  .backend_node_id: int           # 後端節點 ID

# 僅用於資訊擷取
text = await element.text
attrs = await element.attrs
```

**建議模式**：
```python
# ✅ 推薦：透過 tab.evaluate() 互動
result = await tab.evaluate('''
    document.querySelector("#button").click();
''')

# ❌ 避免：直接使用 element.click()（可能過期）
element = await tab.find("#button")
await element.click()  # 可能失敗
```

#### 2.2 Chrome Driver 物件（UC/Selenium）

**Driver 物件**：
```python
# WebDriver 實例（同步 API）
driver: uc.Chrome | webdriver.Chrome
  .session_id: str                # Session ID
  .capabilities: dict             # 瀏覽器能力

# 主要操作
driver.get(url)                              # 導航到 URL
driver.refresh()                             # 重載頁面
element = driver.find_element(By.CSS_SELECTOR, selector)
driver.quit()                                # 關閉瀏覽器
```

**WebElement 物件**：
```python
# 元素物件（Selenium API）
element: WebElement
  .tag_name: str
  .text: str

# 主要操作
element.click()
element.send_keys(text)
element.get_attribute(name)
```

---

### 3. 執行時狀態資料

#### 3.1 頁面重載狀態

**用途**：追蹤自動重載頁面的次數和過熱狀態（階段 3）。

**結構**：
```python
# 函式內部變數
reload_count = 0                  # 當前重載次數
last_reload_time = 0.0            # 上次重載時間戳

# 過熱檢查邏輯
if reload_count >= config_dict["advanced"]["auto_reload_overheat_count"]:
    # 進入冷卻期
    wait_time = config_dict["advanced"]["auto_reload_overheat_cd"]
    reload_count = 0  # 重置
```

**資料流**：
```
載入頁面 → reload_count = 0
  ↓
檢查按鈕可用性
  ↓ (按鈕不可用)
重載頁面 → reload_count += 1
  ↓
檢查過熱 → if reload_count >= overheat_count
  ↓ (是)
等待冷卻 → sleep(overheat_cd)
  ↓
reload_count = 0
```

#### 3.2 重試狀態

**用途**：追蹤元素互動、CAPTCHA 辨識的重試次數。

**結構**：
```python
# 指數退避重試
for retry_count in range(max_retry):
    try:
        # 嘗試操作
        result = await perform_operation()
        break  # 成功
    except Exception as exc:
        if retry_count < max_retry - 1:
            wait_time = 0.5 * (2 ** retry_count)  # 指數退避
            wait_time += random.uniform(0, 0.2)   # 抖動
            await asyncio.sleep(wait_time)
        else:
            raise exc  # 最後一次失敗
```

**重試參數**：
- **max_retry**：3-5 次（根據操作類型）
- **base_wait**：0.5 秒
- **jitter**：0-0.2 秒隨機

#### 3.3 暫停機制狀態（NoDriver 專用）

**用途**：允許用戶透過檔案系統暫停自動化。

**實作**：
```python
# 檔案標記
PAUSE_FILE = "MAXBOT_INT28_IDLE.txt"

# 檢查暫停
def check_and_handle_pause(config_dict):
    if os.path.exists(PAUSE_FILE):
        if config_dict["advanced"]["verbose"]:
            print("[PAUSED] 自動化已暫停，刪除檔案以繼續...")
        while os.path.exists(PAUSE_FILE):
            time.sleep(1)
        if config_dict["advanced"]["verbose"]:
            print("[RESUMED] 繼續執行")
```

**使用位置**：
- 每次 `await tab.sleep()` 前檢查
- 每次 `await tab.evaluate()` 前檢查
- 關鍵決策點前檢查

---

### 4. 平台特定資料

#### 4.1 URL 路由資料

**用途**：根據 URL 判斷平台並路由到對應函式。

**結構**：
```python
# URL → 平台映射
PLATFORM_DOMAINS = {
    "tixcraft.com": "tixcraft",
    "kktix.com": "kktix",
    "ticketplus.com.tw": "ticketplus",
    "ticket.ibon.com.tw": "ibon",
    "kham.com.tw": "kham",
    "ticket.cityline.com": "cityline",
    "ticketmaster.com": "ticketmaster",
    "urbtix.hk": "urbtix",
    "hkticketing.com": "hkticketing",
    "famiticket.com.tw": "famiticket"
}

# 路由邏輯
async def nodriver_main(tab, url, config_dict):
    if "tixcraft.com" in url:
        return await nodriver_tixcraft_main(tab, url, config_dict)
    elif "kktix.com" in url:
        return await nodriver_kktix_main(tab, url, config_dict)
    # ... 其他平台
```

#### 4.2 DOM 選擇器資料（平台特定）

**用途**：每個平台的 CSS 選擇器和 XPath 表達式。

**範例（TixCraft）**：
```python
TIXCRAFT_SELECTORS = {
    # 日期選擇
    "date_list": "table.table a[onclick*='performance_id']",
    "date_sold_out_class": "sold_out",

    # 區域選擇
    "area_list": "select#ticketPriceArea option",
    "area_select": "select#ticketPriceArea",

    # 票數選擇
    "ticket_number_select": "select#ticketPriceQuantity",

    # 驗證碼
    "captcha_image": "img#captchaImg",
    "captcha_input": "input#captcha",

    # 同意條款
    "agree_checkbox": "input#agreeCheckbox",

    # 送出按鈕
    "submit_button": "button#submitButton"
}
```

**變化處理**：
- 選擇器在平台函式內硬編碼
- 平台佈局變更時更新選擇器
- 無跨平台選擇器共享（每個平台獨立）

#### 4.3 認證資料

**用途**：儲存平台認證憑證（session cookies、帳密）。

**TixCraft**（Cookie 注入）：
```python
# 從 config_dict 取得 session cookie
tixcraft_sid = config_dict["advanced"]["tixcraft_sid"]

# NoDriver：透過 CDP 注入
await tab.send(cdp.network.set_cookie(
    name="tixcraft_sid",
    value=tixcraft_sid,
    domain=".tixcraft.com",
    path="/",
    secure=True,
    http_only=True
))

# UC：透過 Selenium API 注入
driver.add_cookie({
    'name': 'tixcraft_sid',
    'value': tixcraft_sid,
    'domain': '.tixcraft.com',
    'path': '/',
    'secure': True,
    'httpOnly': True
})
```

**KKTIX**（表單登入）：
```python
# 從 config_dict 取得帳密
kktix_account = config_dict["advanced"]["kktix_account"]
kktix_password = config_dict["advanced"]["kktix_password"]

# 透過表單登入
await tab.evaluate(f'''
    document.querySelector("input#user_email").value = "{kktix_account}";
    document.querySelector("input#user_password").value = "{kktix_password}";
    document.querySelector("button[type='submit']").click();
''')
```

---

### 5. CAPTCHA 處理資料

#### 5.1 CAPTCHA 圖片資料

**用途**：儲存驗證碼圖片以供 OCR 辨識。

**擷取流程**：
```python
# NoDriver：透過 CDP 截圖
captcha_element = await tab.find("img#captchaImg")
captcha_base64 = await tab.evaluate('''
    (() => {
        const img = document.querySelector("img#captchaImg");
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return canvas.toDataURL('image/png').split(',')[1];
    })()
''')

# 解碼 base64
import base64
captcha_bytes = base64.b64decode(captcha_base64)

# UC：透過 PIL 截圖
from PIL import Image
captcha_element = driver.find_element(By.CSS_SELECTOR, "img#captchaImg")
location = captcha_element.location
size = captcha_element.size
screenshot = driver.get_screenshot_as_png()
image = Image.open(io.BytesIO(screenshot))
captcha_image = image.crop((
    location['x'],
    location['y'],
    location['x'] + size['width'],
    location['y'] + size['height']
))
```

#### 5.2 OCR 結果資料

**用途**：儲存 ddddocr 辨識結果。

**結構**：
```python
ocr_result = {
    "text": str,              # 辨識的文字
    "confidence": float,      # 信心度（0.0-1.0，ddddocr 不提供）
    "success": bool,          # 辨識是否成功
    "model": str              # "standard" | "beta"
}
```

**辨識流程**：
```python
import ddddocr

# 初始化 OCR 實例
if config_dict["ocr_captcha"]["beta"]:
    ocr = ddddocr.DdddOcr(beta=True)  # Beta 模型
else:
    ocr = ddddocr.DdddOcr()           # 標準模型

# 辨識
captcha_text = ocr.classification(captcha_bytes)

# 驗證結果（基本檢查）
if len(captcha_text) >= 4 and captcha_text.isalnum():
    ocr_result = {"text": captcha_text, "success": True}
else:
    ocr_result = {"text": "", "success": False}
```

---

### 6. 選擇資料（用戶選擇結果）

#### 6.1 日期選擇資料

**用途**：儲存可用日期和用戶選擇的日期。

**結構**：
```python
# 可用日期列表
available_dates = [
    {
        "text": "2025/10/15 (日) 19:30",
        "element_id": "performance_12345",
        "sold_out": False,
        "match_keyword": True  # 是否匹配關鍵字
    },
    {
        "text": "2025/10/16 (一) 19:30",
        "element_id": "performance_12346",
        "sold_out": False,
        "match_keyword": False
    }
]

# 選擇的日期
selected_date = {
    "text": "2025/10/15 (日) 19:30",
    "element_id": "performance_12345",
    "selection_method": "keyword"  # "keyword" | "mode" | "manual"
}
```

**選擇邏輯（v1.2 更新）**：
```python
# 第 1 層：關鍵字匹配（Early Return 策略）
date_keyword = config_dict["date_auto_select"]["date_keyword"]
keywords = date_keyword.split(';')  # v1.2: 分號分隔

for keyword in keywords:  # 按順序檢查（優先順序）
    for date in available_dates:
        if keyword in date["text"]:
            date["match_keyword"] = True
            selected_date = date
            break  # Early Return：首次匹配立即停止
    if selected_date:
        break

# 第 2 層：模式選擇（Strict Mode 預設）
if not selected_date:
    date_auto_fallback = config_dict["date_auto_select"].get("date_auto_fallback", False)

    if date_auto_fallback:  # Auto Mode
        mode = config_dict["date_auto_select"]["mode"]
        if mode == "from top to bottom":
            selected_date = available_dates[0]
        elif mode == "from bottom to top":
            selected_date = available_dates[-1]
        # ... 其他模式
    else:  # Strict Mode（預設）
        # 停止並等待手動介入
        print("[WARNING] 關鍵字不匹配，等待手動選擇...")
        # 暫停自動化
```

#### 6.2 區域選擇資料

**用途**：儲存可用區域和用戶選擇的區域。

**結構**：
```python
# 可用區域列表
available_areas = [
    {
        "text": "VIP區 $3000",
        "value": "area_1",
        "sold_out": False,
        "match_keyword": True
    },
    {
        "text": "搖滾區A $2000",
        "value": "area_2",
        "sold_out": False,
        "match_keyword": False
    }
]

# 選擇的區域
selected_area = {
    "text": "VIP區 $3000",
    "value": "area_1",
    "selection_method": "keyword"
}
```

#### 6.3 座位選擇資料（座位圖）

**用途**：儲存座位圖上的可用座位和選擇的座位。

**結構**：
```python
# 可用座位列表
available_seats = [
    {
        "id": "seat_A01",
        "row": "A",
        "number": 1,
        "status": "available",  # "available" | "taken" | "reserved"
        "price": 3000
    },
    {
        "id": "seat_A02",
        "row": "A",
        "number": 2,
        "status": "available",
        "price": 3000
    }
]

# 選擇的座位
selected_seats = [
    {"id": "seat_A01", "row": "A", "number": 1},
    {"id": "seat_A02", "row": "A", "number": 2}
]

# ibon 特殊：相鄰座位要求
adjacent_seats_required = config_dict["seat_auto_select"]["adjacent_seat"]
```

---

### 7. 錯誤與日誌資料

#### 7.1 錯誤資料

**用途**：記錄錯誤資訊以供除錯和重試決策。

**結構**：
```python
error_info = {
    "stage": str,             # 發生錯誤的階段："date_select" | "captcha" | ...
    "error_type": str,        # 錯誤類型："ElementNotFound" | "ClickIntercepted" | ...
    "message": str,           # 錯誤訊息
    "timestamp": float,       # 時間戳
    "retry_count": int,       # 已重試次數
    "recoverable": bool       # 是否可恢復
}
```

**錯誤處理模式**：
```python
try:
    await perform_stage_operation()
except ElementNotFoundError as e:
    error_info = {
        "stage": "date_select",
        "error_type": "ElementNotFound",
        "message": str(e),
        "timestamp": time.time(),
        "retry_count": retry_count,
        "recoverable": True
    }
    # 記錄錯誤
    if config_dict["advanced"]["verbose"]:
        print(f"[ERROR] {error_info}")
    # 決定重試或失敗
    if error_info["recoverable"] and retry_count < max_retry:
        # 重試
        pass
    else:
        raise
```

#### 7.2 日誌資料

**用途**：記錄執行過程以供用戶監控。

**日誌格式**：
```python
# 詳細模式（verbose=True）
print(f"[{stage}] {message}")

# 範例
"[INIT] 正在初始化瀏覽器..."
"[AUTH] 注入 session cookie"
"[RELOAD] 正在重載頁面... (1/10)"
"[DATE] 找到 3 個可用日期"
"[DATE] 使用關鍵字 '10/15' 匹配到日期"
"[AREA] 選擇區域：VIP區 $3000"
"[CAPTCHA] OCR 辨識結果：AB12"
"[SUBMIT] 正在送出訂單..."
"[SUCCESS] 訂單已送出，請完成付款"
```

**日誌等級**（隱含）：
- **INFO**：`[STAGE]` - 正常流程
- **WARNING**：`[WARNING]` - 非關鍵問題
- **ERROR**：`[ERROR]` - 錯誤但可恢復
- **CRITICAL**：`[CRITICAL]` - 致命錯誤

---

## 資料流圖

### 整體資料流（12 階段）

```
settings.json
  ↓ (載入)
config_dict
  ↓ (傳遞給所有函式)
┌─────────────────────────────────────┐
│ 階段 1：環境初始化                   │
│ 輸入：config_dict                    │
│ 輸出：browser, tab (NoDriver)       │
│       driver (UC/Selenium)           │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 2：身份認證                     │
│ 輸入：config_dict, tab/driver       │
│ 輸出：已認證的 session               │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 3：頁面監控與重載               │
│ 輸入：config_dict, tab/driver       │
│ 狀態：reload_count                   │
│ 輸出：按鈕可用的頁面                 │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 4：日期選擇                     │
│ 輸入：config_dict, tab/driver       │
│ 資料：available_dates                │
│ 輸出：selected_date                  │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 5：區域/座位選擇                │
│ 輸入：config_dict, tab/driver       │
│ 資料：available_areas/seats          │
│ 輸出：selected_area/seats            │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 6：票數設定                     │
│ 輸入：config_dict.ticket_number     │
│ 輸出：已設定票數                     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 7：驗證碼處理                   │
│ 輸入：config_dict, tab/driver       │
│ 資料：captcha_bytes → ocr_result    │
│ 輸出：captcha_text（已填入）         │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 8：表單填寫                     │
│ 輸入：config_dict.ticket_form_data  │
│ 輸出：已填寫表單                     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 9：同意條款處理                 │
│ 輸入：tab/driver                     │
│ 輸出：已勾選條款                     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 10：訂單確認與送出              │
│ 輸入：tab/driver                     │
│ 輸出：訂單已送出                     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 11：排隊與付款                  │
│ 輸入：tab/driver                     │
│ 輸出：進入付款頁面（手動付款）       │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 階段 12：錯誤處理與重試              │
│ 輸入：error_info, retry_count       │
│ 輸出：重試或終止                     │
└─────────────────────────────────────┘
```

### 三層回退資料流（日期/區域選擇）

```
config_dict.date_auto_select
  ↓
┌─────────────────────────────────────┐
│ 第 1 層：關鍵字匹配                  │
│ 輸入：date_keyword, available_dates │
│ 邏輯：遍歷 keywords，檢查 text      │
│ 輸出：matched_date 或 None          │
└─────────────────────────────────────┘
  ↓ (如果 None)
┌─────────────────────────────────────┐
│ 第 2 層：模式選擇                    │
│ 輸入：mode, available_dates         │
│ 邏輯：根據 mode 選擇（top/bottom）  │
│ 輸出：selected_date 或 None         │
└─────────────────────────────────────┘
  ↓ (如果 None)
┌─────────────────────────────────────┐
│ 第 3 層：手動介入                    │
│ 邏輯：暫停自動化，播放音效          │
│ 等待：用戶手動選擇                   │
│ 輸出：user_selected_date            │
└─────────────────────────────────────┘
  ↓
selected_date（繼續下一階段）
```

---

## 資料持久化

### 不持久化的資料

**執行時狀態**：
- `reload_count`：僅在記憶體中
- `retry_count`：僅在記憶體中
- `selected_date/area/seats`：僅在記憶體中
- `error_info`：僅在記憶體中（可選日誌到檔案）

**瀏覽器物件**：
- `browser/tab`（NoDriver）：程序結束時銷毀
- `driver`（UC/Selenium）：程序結束時 quit()

### 持久化的資料

**配置檔案**（settings.json）：
- 使用者手動編輯
- 系統僅讀取，不寫入

**暫停標記**（MAXBOT_INT28_IDLE.txt）：
- 使用者手動建立/刪除
- 系統僅讀取（檢查存在性）

**Cookies**（可選）：
- 部分平台支援從瀏覽器匯出 cookies
- 儲存在 settings.json 的 `advanced` 區段
- 系統載入並注入到瀏覽器

**日誌檔案**（可選，未實作）：
- 可選擇將 stdout 重定向到檔案
- 命令：`python nodriver_tixcraft.py > output.log 2>&1`

---

## 資料驗證

### 配置驗證（部分實作）

**當前狀態**：
- 無 JSON Schema 驗證
- 基本型別檢查（隱含）
- 欄位存在性檢查（KeyError 處理）

**改進方向**（SC-009）：
```python
# 未來：使用 JSON Schema 驗證
import jsonschema

schema = {
    "type": "object",
    "properties": {
        "homepage": {"type": "string", "format": "uri"},
        "ticket_number": {"type": "integer", "minimum": 1, "maximum": 6},
        "date_auto_select": {
            "type": "object",
            "properties": {
                "enable": {"type": "boolean"},
                "date_keyword": {"type": "string"},
                "mode": {"type": "string", "enum": ["from top to bottom", "from bottom to top", "center", "random"]}
            },
            "required": ["enable"]
        }
    },
    "required": ["homepage", "ticket_number"]
}

jsonschema.validate(config_dict, schema)
```

### 執行時驗證

**元素存在性檢查**：
```python
# NoDriver
result = await tab.evaluate('''
    (() => {
        const element = document.querySelector("#button");
        if (!element) return {success: false, reason: "not_found"};
        return {success: true};
    })()
''')

if not result.get('success'):
    raise ElementNotFoundError("按鈕不存在")
```

**CAPTCHA 結果驗證**：
```python
# 基本檢查
if len(captcha_text) < 4:
    raise CaptchaRecognitionError("驗證碼長度不足")

if not captcha_text.isalnum():
    raise CaptchaRecognitionError("驗證碼包含非法字符")
```

---

## 平台差異資料

### DOM 結構差異

**TixCraft**：
- 日期選擇：`<a>` 元素，`onclick` 屬性包含 performance_id
- 區域選擇：`<select>` 下拉選單
- 驗證碼：標準 `<img>` 元素

**ibon**：
- 日期選擇：`<button>` 元素，Shadow DOM 內部
- 座位選擇：互動式座位圖，相鄰座位要求
- 無驗證碼

**KKTIX**：
- 日期選擇：`<button>` 元素，展開式面板
- 區域選擇：無（直接設定票數）
- 驗證碼：標準 `<img>` 元素

### 認證方式差異

| 平台 | 認證方式 | 資料儲存 | 注入方式 |
|------|---------|---------|---------|
| TixCraft | Session Cookie | `tixcraft_sid` | CDP/Selenium Cookie API |
| KKTIX | 帳號密碼 | `kktix_account`, `kktix_password` | 表單填寫 + 送出 |
| ibon | Session Cookie | `ibon_ibonqware` | CDP/Selenium Cookie API |
| KHAM | Session Cookie | `kham_tk` | CDP/Selenium Cookie API |
| TicketPlus | 無（公開售票） | N/A | N/A |

---

## 記憶體管理

### NoDriver 記憶體占用

**典型占用**：
- Browser 實例：~50-80 MB
- Tab 實例：~30-50 MB per tab
- JavaScript 執行：臨時 +10-20 MB

**最佳化**：
- 單一 tab 策略（避免多個 tabs）
- 避免累積 element 物件（使用後立即釋放）
- 定期垃圾回收（Python gc）

### Chrome Driver 記憶體占用

**典型占用**：
- Driver 實例：~100-150 MB（比 NoDriver 高 30%）
- WebElement 快取：+20-30 MB

**差異原因**：
- WebDriver 協定開銷
- 元素物件快取機制
- 同步 API 的阻塞等待

---

## 資料安全

### 敏感資料保護

**儲存於 settings.json**：
- ❌ 明文儲存：Session cookies, 密碼
- ⚠️ 風險：檔案系統權限、版本控制外洩

**緩解措施**：
- `.gitignore` 排除 settings.json
- 檔案權限限制（chmod 600）
- 可選加密（未實作）

**傳輸中的資料**：
- ✅ HTTPS：所有平台 API 通訊
- ✅ Secure Cookies：設定 `secure=True`

### 未來改進

**加密配置**（建議）：
```python
# 加密敏感欄位
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

encrypted_password = fernet.encrypt(password.encode())
config_dict["advanced"]["kktix_password_encrypted"] = encrypted_password.decode()
```

**環境變數**（替代方案）：
```bash
export TIXCRAFT_SID="your_session_id"
export KKTIX_PASSWORD="your_password"
```

```python
import os
tixcraft_sid = os.getenv("TIXCRAFT_SID") or config_dict["advanced"]["tixcraft_sid"]
```

---

## 資料模型總結

### 核心實體

1. **config_dict**：所有配置的唯一來源
2. **browser/tab**（NoDriver）：瀏覽器自動化的主要介面
3. **driver**（UC/Selenium）：舊版瀏覽器自動化介面
4. **available_dates/areas/seats**：用戶選擇的候選項
5. **selected_date/area/seats**：用戶的最終選擇
6. **captcha_bytes → ocr_result**：驗證碼處理流程
7. **error_info**：錯誤追蹤與恢復

### 資料流原則

1. **單向流動**：配置 → 執行時狀態 → 結果
2. **不可變配置**：config_dict 唯讀
3. **可變狀態**：執行時狀態在函式間傳遞
4. **無全域狀態**：所有狀態作為參數傳遞

### 擴展性

**新增平台**：
- 定義平台特定選擇器
- 實作 12 階段函式
- 在路由器中註冊 URL 映射

**新增配置選項**：
- 在 settings.json 新增欄位
- 更新 config_dict 結構文件
- 在對應階段函式中讀取

---

**文件狀態**：資料模型完成
**最後更新**：2025-10-16
**下一步**：創建 contracts/ 目錄記錄介面契約
