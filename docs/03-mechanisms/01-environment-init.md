# 機制 01：環境初始化 (Stage 1)

**文件說明**：說明搶票自動化系統的環境初始化機制、設定載入與運行環境驗證流程
**最後更新**：2025-11-12

---

## 概述

環境初始化是整個自動化購票系統的第一個關鍵階段。在這個階段中，系統需要準備運行環境、啟動瀏覽器、載入配置並驗證環境就緒。

**核心目標**：建立穩定的運行環境，確保系統能夠順利進行後續的購票自動化。

**優先度**：🔴 P1 - 核心流程，必須完成

---

## 機制流程

### 1. 環境配置加載

#### 1.1 配置文件解析
系統首先讀取 `settings.json` 配置文件，解析使用者的所有設定。

**相關功能需求**：
- FR-001: 支援多平台配置（TixCraft、KKTIX、iBon、TicketPlus、KHAM）
- FR-005: 配置驅動開發 - 所有行為由 `settings.json` 控制

**配置驗證清單**：
- ✅ 活動 URL (`url` 欄位)
- ✅ Webdriver 類型 (`webdriver_type`: nodriver/chrome/undetected_chrome)
- ✅ 日期選擇配置 (`date_auto_select`)
- ✅ 區域選擇配置 (`area_auto_select`)
- ✅ 驗證碼配置 (`captcha`)
- ✅ 登入憑證 (`ticket_account`)
- ✅ 進階設定 (`advanced`)
- ✅ 日誌級別 (`log_level`)

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1-100 (設定加載)
- `src/common.py`: 配置驗證邏輯

**代碼範例**：
```python
# 加載配置
with open(config_file, 'r', encoding='utf-8') as f:
    config_dict = json.load(f)

# 驗證必填欄位
required_fields = ['url', 'webdriver_type', 'date_auto_select', 'area_auto_select']
for field in required_fields:
    if field not in config_dict:
        raise ValueError(f"配置缺少必填欄位: {field}")
```

#### 1.2 平台識別
根據活動 URL 自動識別目標平台。

**支援的平台識別邏輯**：
1. TixCraft: `tixcraft.com` 在 URL 中
2. KKTIX: `kktix.com` 在 URL 中
3. iBon: `ibon.com.tw` 在 URL 中
4. TicketPlus: `ticketplus.com.tw` 在 URL 中
5. KHAM: `kham.com.tw` 在 URL 中

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 100-150 (平台識別)

**代碼範例**：
```python
def detect_platform(url: str) -> str:
    """識別購票平台"""
    if 'tixcraft.com' in url:
        return 'tixcraft'
    elif 'kktix.com' in url:
        return 'kktix'
    elif 'ibon.com.tw' in url:
        return 'ibon'
    elif 'ticketplus.com.tw' in url:
        return 'ticketplus'
    elif 'kham.com.tw' in url:
        return 'kham'
    else:
        raise ValueError(f"不支援的平台 URL: {url}")
```

### 2. Webdriver 初始化

#### 2.1 NoDriver 初始化（推薦）
根據憲法「NoDriver First」原則，優先使用 NoDriver 作為 webdriver。

**優勢**：
- ✅ 最佳反偵測性能
- ✅ 原生 CDP 協議，無 JavaScript 執行風險
- ✅ 最小記憶體消耗
- ✅ 官方維護，長期支持

**初始化流程**：
1. 檢查 Chrome/Chromium 瀏覽器是否安裝
2. 啟動 NoDriver 瀏覽器實例
3. 驗證連線成功
4. 設定頁面超時與導航超時

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 150-250 (NoDriver 初始化)

**代碼範例**：
```python
import nodriver

async def init_nodriver(config_dict):
    """初始化 NoDriver 瀏覽器"""
    browser = await nodriver.start(
        headless=config_dict.get('advanced', {}).get('headless', True),
        disable_image_loading=config_dict.get('advanced', {}).get('disable_images', True),
        window_size=(1920, 1080)
    )

    # 驗證連線
    if not browser:
        raise RuntimeError("NoDriver 初始化失敗")

    return browser
```

#### 2.2 Chrome Driver 初始化（回退）
如果 webdriver_type 設定為 'chrome'，使用 Selenium + Chrome Driver。

**當使用 Chrome Driver 時**：
- 僅用於測試或遺留環境
- 不推薦用於生產環境
- 反偵測性能較差

**實作位置**：
- `src/chrome_tixcraft.py`: Chrome Driver 版本

#### 2.3 Undetected Chrome 初始化（中繼）
UC (Undetected Chrome) 作為 Chrome Driver 的增強版本。

**使用場景**：
- 需要繞過進階反偵測的平台
- Chrome Driver 無法訪問時的備選方案

**實作位置**：
- `src/uc_tixcraft.py`: UC 版本

### 3. Cookie 與認證準備

#### 3.1 Cookie 注入
如果配置中提供了 Cookie，在瀏覽器啟動後立即注入。

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 250-300 (Cookie 注入)

**代碼範例**：
```python
async def inject_cookies(page, cookies: dict):
    """注入 Cookie 到頁面"""
    if not cookies:
        return

    cookie_list = []
    for name, value in cookies.items():
        cookie_list.append({
            'name': name,
            'value': value,
            'domain': extract_domain(page.url),
            'path': '/',
            'httpOnly': False,
            'secure': False,
            'sameSite': 'None'
        })

    await page.set_cookies(cookie_list)
```

#### 3.2 認證狀態驗證
驗證注入的 Cookie 是否有效，確保已認證狀態。

**驗證方法**：
1. 檢查頁面是否包含「登出」按鈕或使用者資訊
2. 檢查頁面 HTML 中是否有認證令牌
3. 嘗試訪問受保護的功能

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 300-350 (認證驗證)

### 4. 頁面導航與等待

#### 4.1 導航到活動 URL
系統導航到配置中的活動 URL。

**超時設定**：
- 頁面加載超時：30 秒
- 導航超時：20 秒

**等待條件**：
- ✅ 頁面 DOM 載入完成 (`domcontentloaded`)
- ✅ 頁面網路空閒 (`networkidle2`: 500ms 內無新請求)

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 350-400 (導航)

**代碼範例**：
```python
async def navigate_to_url(page, url: str, timeout: int = 30000):
    """導航到活動頁面"""
    try:
        await page.goto(url, wait_until='networkidle2', timeout=timeout)
        print(f"[NAVIGATION] 成功導航到 {url}")
    except asyncio.TimeoutError:
        print(f"[WARNING] 頁面加載超時，但繼續進行")
        # 繼續執行，某些平台可能有遲延加載
```

#### 4.2 頁面準備驗證
驗證頁面是否已正確加載。

**驗證項目**：
- ✅ 頁面標題不為空
- ✅ 活動資訊容器存在
- ✅ 沒有錯誤訊息或 404 頁面
- ✅ JavaScript 有成功執行（如適用）

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 400-450 (頁面驗證)

### 5. 資源與日誌準備

#### 5.1 日誌系統初始化
設定日誌級別和輸出目標。

**支援的日誌級別**：
- 🔴 DEBUG: 詳細除錯信息（開發用）
- 🟡 INFO: 一般信息（預設）
- 🟠 WARNING: 警告信息
- 🔴 ERROR: 錯誤信息
- 🔴 CRITICAL: 嚴重錯誤

**實作位置**：
- `src/common.py`: 日誌配置

#### 5.2 暫停機制檢查
檢查 `MAXBOT_INT28_IDLE.txt` 檔案，實現暫停機制（憲法原則）。

**暫停機制目的**：
- 允許使用者在任何時間暫停自動化
- 實現優雅的停止，不強行終止
- 保留現有狀態供恢復使用

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 450-500 (暫停檢查)

**代碼範例**：
```python
async def check_pause_mechanism():
    """檢查是否存在暫停檔案"""
    pause_file = 'MAXBOT_INT28_IDLE.txt'
    if os.path.exists(pause_file):
        print("[PAUSE] 檢測到暫停信號，進入等待狀態...")
        while os.path.exists(pause_file):
            await asyncio.sleep(1)
        print("[RESUME] 恢復執行")
```

---

## 成功標準

**SC-001: 環境初始化成功率** ≥ 95%
- 環境初始化成功完成的次數 / 總嘗試次數

**SC-004: 瀏覽器啟動時間** ≤ 15 秒
- 從啟動開始到頁面可互動的時間

**SC-009: 錯誤恢復能力** ≥ 90%
- 系統在遭遇初始化錯誤時，能夠自動恢復或提供清晰的錯誤訊息

---

## 平台特定考量

### TixCraft
- ✅ 直接導航到活動 URL
- ✅ Cookie 認證通常有效
- ⚠️ 某些活動可能需要額外的 JavaScript 執行

### KKTIX
- ✅ 支援 Cookie 認證
- ⚠️ 可能需要等待更久的頁面加載
- ⚠️ 動態內容加載較多

### iBon
- ✅ 支援 Cookie 認證
- ⚠️ 使用 Angular SPA，需要更強的 JavaScript 支持
- ⚠️ Shadow DOM 結構複雜

### TicketPlus
- ✅ 直接導航
- ⚠️ 可能有地理位置限制檢查

### KHAM
- ✅ 直接導航
- ⚠️ 頁面載入可能不穩定

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-001 | 多平台支援識別 | ✅ 實作 |
| FR-005 | 配置驅動開發 | ✅ 實作 |
| FR-037 | 暫停機制 (MAXBOT_INT28_IDLE.txt) | ✅ 實作 |
| FR-055 | 日誌與除錯 | ✅ 實作 |

---

## 相關檔案

### 核心實作
- `src/nodriver_tixcraft.py` - NoDriver 版本主程序（行 1-500）
- `src/chrome_tixcraft.py` - Chrome Driver 版本（備份）
- `src/uc_tixcraft.py` - Undetected Chrome 版本（中繼）
- `src/common.py` - 共通函式庫

### 配置文件
- `src/settings.json` - 主配置文件
- `src/settings-template.json` - 配置範本

### 輔助檔案
- `.temp/MAXBOT_INT28_IDLE.txt` - 暫停信號檔案

---

## 故障排除

### 問題 1: NoDriver 初始化失敗
**症狀**：`RuntimeError: NoDriver 初始化失敗`

**可能原因**：
- Chrome/Chromium 未安裝
- NoDriver 版本不相容
- 系統權限不足

**解決方案**：
1. 驗證 Chrome 安裝：`chrome --version`
2. 更新 NoDriver：`pip install --upgrade nodriver`
3. 檢查系統權限
4. 嘗試回退到 Chrome Driver

### 問題 2: 頁面加載超時
**症狀**：`TimeoutError: 等待頁面加載超過 30 秒`

**可能原因**：
- 網路連接較慢
- 平台伺服器響應較慢
- 某些 JavaScript 資源加載失敗

**解決方案**：
1. 增加超時時間（`timeout` 參數）
2. 啟用 `disable_images` 加快加載
3. 檢查網路連接
4. 查詢平台的維護公告

### 問題 3: Cookie 注入失敗
**症狀**：注入的 Cookie 無法驗證，仍被要求登入

**可能原因**：
- Cookie 已過期
- Cookie 格式不正確
- 平台更改了認證機制

**解決方案**：
1. 重新取得 Cookie（清除舊 Cookie，重新登入）
2. 驗證 Cookie 格式（應包含 `domain`、`path` 等欄位）
3. 檢查 Cookie 有效期

---

## 最佳實踐

### ✅ 推薦做法

1. **使用 NoDriver 優先**
   - 最佳反偵測、最小資源消耗
   ```python
   config_dict['webdriver_type'] = 'nodriver'
   ```

2. **啟用詳細日誌進行調試**
   - 開發階段設定為 DEBUG，生產環境設定為 INFO
   ```python
   config_dict['advanced']['verbose'] = True
   ```

3. **驗證 Cookie 的有效性**
   - 定期更新 Cookie（建議每週一次）
   - 使用專用帳號以減少 Cookie 失效風險

4. **實現優雅的錯誤處理**
   - 提供清晰的錯誤訊息
   - 記錄完整的堆棧追蹤用於除錯

### ❌ 避免做法

1. ❌ 硬編碼 Cookie 值
   - 應使用配置文件或環境變數

2. ❌ 忽略頁面加載超時
   - 應至少記錄警告，繼續前進前驗證頁面狀態

3. ❌ 假設所有平台的初始化邏輯相同
   - 應在進行特定平台操作前驗證平台識別

4. ❌ 在生產環境中使用 DEBUG 日誌級別
   - 將生成大量日誌，影響效能

---

## 開發檢查清單

- [ ] 配置文件正確解析
- [ ] 平台自動識別正確
- [ ] NoDriver 成功初始化
- [ ] Cookie（如有）成功注入
- [ ] 頁面導航成功
- [ ] 頁面驗證通過
- [ ] 日誌系統正常工作
- [ ] 暫停機制檢查正常
- [ ] 錯誤訊息清晰明確
- [ ] 所有平台測試通過

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: ✅ Phase 2 已驗證

