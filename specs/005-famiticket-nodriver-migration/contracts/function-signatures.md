# 函數簽章：FamiTicket NoDriver

**功能分支**：`005-famiticket-nodriver-migration`
**建立日期**：2025-11-04
**目的**：定義所有 FamiTicket NoDriver 函數的API契約

---

## 概述

本文件定義 FamiTicket NoDriver 遷移所需的所有函數簽章、參數、返回值與行為契約。所有函數遵循：
- **FR-030**：使用 `async` 非同步語法
- **FR-031**：使用 NoDriver `tab` 物件（而非 Selenium `driver`）
- **FR-038**：返回布林值或簡單狀態（簡化狀態管理）
- **命名規範**：以 `nodriver_fami_` 或 `nodriver_famiticket_` 開頭

---

## 核心函數 (Core Functions)

### 1. 主函數 - URL 路由器

#### `nodriver_famiticket_main()`

**簽章**：
```python
async def nodriver_famiticket_main(
    tab,                    # NoDriver tab 物件
    url: str,               # 當前頁面 URL
    config_dict: dict       # 設定字典（從 settings.json 讀取）
) -> bool
```

**用途**：FamiTicket 主函數，作為 URL 路由器，根據 URL 模式分派至對應的子函數

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件，用於頁面操作
- `url` (str): 當前頁面 URL
- `config_dict` (dict): 完整設定字典（包含 `advanced`、`tixcraft`、`date_auto_select`、`area_auto_select` 等）

**返回值**：
- `bool`: 操作成功返回 `True`，失敗或無匹配 URL 返回 `False`

**行為**：
1. 檢查 URL 模式：
   - 若包含 `/Home/User/SignIn` → 呼叫 `nodriver_fami_login()`
   - 若包含 `/Home/Activity/Info/` → 呼叫 `nodriver_fami_activity()`
   - 若包含 `/Sales/Home/Index/` → 呼叫 `nodriver_fami_home_auto_select()`
   - 其他 URL → 返回 `False`
2. 將呼叫結果返回

**錯誤處理**：
- 捕捉所有子函數的例外，記錄錯誤訊息後返回 `False`

**範例**：
```python
success = await nodriver_famiticket_main(tab, url, config_dict)
if not success:
    print("[ERROR] FamiTicket main function failed")
```

---

### 2. 登入函數

#### `nodriver_fami_login()`

**簽章**：
```python
async def nodriver_fami_login(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：自動填寫 FamiTicket 登入表單（帳號 + 密碼）

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（讀取 `advanced.fami_account` 與 `advanced.fami_password_plaintext`）
- `show_debug_message` (bool): 是否輸出除錯訊息（預設 `True`）

**返回值**：
- `bool`: 登入成功返回 `True`，失敗返回 `False`

**行為**：
1. 從 `config_dict` 讀取帳號與密碼
2. 使用 NoDriver `tab.select()` 定位帳號輸入框（`#usr_act`）
3. 使用 `await element.send_keys()` 填寫帳號
4. 使用 NoDriver `tab.select()` 定位密碼輸入框（`#usr_pwd`）
5. 使用 `await element.send_keys()` 填寫密碼（自動觸發表單提交）

**錯誤處理**：
- 若帳號或密碼為空：輸出錯誤訊息，返回 `False`
- 若元素未找到：輸出錯誤訊息，返回 `False`
- 捕捉所有例外，返回 `False`

**範例**：
```python
success = await nodriver_fami_login(tab, config_dict)
if success:
    print("[LOGIN] Login successful")
```

---

### 3. 活動頁面處理函數

#### `nodriver_fami_activity()`

**簽章**：
```python
async def nodriver_fami_activity(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：點擊活動頁面的「購買」按鈕（`#buyWaiting`）

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（用於讀取除錯選項）
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `bool`: 點擊成功返回 `True`，失敗返回 `False`

**行為**：
1. 使用 CDP `perform_search()` 搜尋購買按鈕（`#buyWaiting`）
2. 若找到按鈕：
   - 使用 CDP `dispatch_mouse_event()` 點擊（真實滑鼠點擊）
   - 返回 `True`
3. 若未找到按鈕：
   - 重新整理頁面（`await tab.reload()`）
   - 重試最多 3 次
   - 若仍未找到，返回 `False`

**錯誤處理**：
- 捕捉 CDP 例外，記錄錯誤訊息
- 重試失敗後返回 `False`

**範例**：
```python
success = await nodriver_fami_activity(tab, config_dict)
if not success:
    print("[ACTIVITY] Buy button not found after 3 retries")
```

---

### 4. 日期選擇函數

#### `nodriver_fami_date_auto_select()`

**簽章**：
```python
async def nodriver_fami_date_auto_select(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    last_activity_url: str,         # 活動頁面 URL（用於自動補票）
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：自動選擇符合關鍵字的演出日期

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（讀取 `date_auto_select.date_keyword`、`tixcraft.auto_reload_coming_soon_page`）
- `last_activity_url` (str): 活動頁面 URL（用於自動補票時返回）
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `bool`: 選擇成功返回 `True`，失敗返回 `False`

**行為**：
1. 使用 CDP `perform_search()` 掃描所有日期列（`table.session__list > tbody > tr`）
2. 從每一列提取：
   - 日期文字（`td:nth-child(1)`）
   - 區域文字（`td:nth-child(2)`）
   - 購買按鈕（`button`）
3. 過濾：僅保留包含「立即購買」按鈕的列
4. 關鍵字匹配（OR 邏輯）：
   - 讀取 `date_keyword`（逗號分隔）
   - 檢查日期文字是否包含任一關鍵字
5. 若匹配成功：
   - 使用 CDP `dispatch_mouse_event()` 點擊按鈕
   - 返回 `True`
6. 若無匹配：
   - 使用 `auto_select_mode` 選擇第一個可用日期（回退機制）
7. 若日期列表為空：
   - 檢查 `auto_reload_coming_soon_page` 是否啟用
   - 若是：等待 `auto_reload_page_interval` 後執行 `await tab.get(last_activity_url)`（返回活動頁面）
   - 若否：返回 `False`

**錯誤處理**：
- 捕捉 CDP 例外，記錄錯誤訊息
- 自動補票失敗時返回 `False`

**範例**：
```python
success = await nodriver_fami_date_auto_select(
    tab, config_dict, last_activity_url="https://www.famiticket.com.tw/Home/Activity/Info/123"
)
```

---

### 5. 區域選擇函數

#### `nodriver_fami_area_auto_select()`

**簽章**：
```python
async def nodriver_fami_area_auto_select(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    area_keyword_item: str,         # 區域關鍵字（單組，支援 AND 邏輯）
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：自動選擇符合關鍵字的座位區域

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（讀取 `area_auto_select.mode`）
- `area_keyword_item` (str): 區域關鍵字（逗號分隔 = AND 邏輯，例如："VIP,一樓"）
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `bool`: 選擇成功返回 `True`，失敗返回 `False`

**行為**：
1. 使用 CDP `perform_search()` 掃描所有區域連結（`div > a.area`）
2. 從每個連結提取：
   - 區域名稱（文字內容）
   - 區域 HTML（`innerHTML`）
3. 過濾：排除 class 包含 `"area disabled"` 的項目
4. 關鍵字匹配（AND 邏輯）：
   - 將 `area_keyword_item` 分割為多個關鍵字（逗號分隔）
   - 檢查區域名稱是否**同時**包含所有關鍵字
5. 若匹配成功：
   - 使用 CDP `dispatch_mouse_event()` 點擊區域連結
   - 返回 `True`
6. 若無匹配：
   - 使用 `auto_select_mode` 選擇第一個可用區域（回退機制）

**錯誤處理**：
- 捕捉 CDP 例外，記錄錯誤訊息
- 回退機制失敗時返回 `False`

**範例**：
```python
success = await nodriver_fami_area_auto_select(
    tab, config_dict, area_keyword_item="VIP,一樓"
)
```

---

### 6. 驗證問題處理函數

#### `nodriver_fami_verify()`

**簽章**：
```python
async def nodriver_fami_verify(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    fail_list: list = None,         # 錯誤答案清單
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> tuple[bool, list]
```

**用途**：自動填寫 FamiTicket 驗證問題答案

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（讀取 `area_auto_select.area_answer`、`advanced.auto_guess_options`）
- `fail_list` (list): 已失敗的答案清單（避免重複嘗試），預設為 `None`（空列表）
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `tuple[bool, list]`: `(成功與否, 更新後的 fail_list)`
  - 成功：`(True, fail_list)`
  - 失敗：`(False, fail_list + [新失敗答案])`

**行為**：
1. 使用 CDP `perform_search()` 搜尋驗證輸入框（`#verifyPrefAnswer`）
2. 若找到輸入框：
   - 呼叫 `util.fill_common_verify_form()`（重用現有工具函數）
   - 傳遞參數：`tab`, `config_dict`, `fail_list`
3. 若啟用自動猜測（`auto_guess_options: true`）：
   - 呼叫 `util.guess_tixcraft_question()` 從頁面內容推斷答案
   - 將推斷結果作為候選答案
4. 填寫答案後提交表單
5. 驗證結果：
   - 成功：返回 `(True, fail_list)`
   - 失敗：將答案加入 `fail_list`，返回 `(False, fail_list)`

**錯誤處理**：
- 若輸入框未找到：返回 `(False, fail_list)`
- 捕捉所有例外，返回 `(False, fail_list)`

**範例**：
```python
success, fail_list = await nodriver_fami_verify(tab, config_dict, fail_list=[])
if success:
    print("[VERIFY] Verification successful")
else:
    print(f"[VERIFY] Failed with fail_list: {fail_list}")
```

---

### 7. 日期/區域選擇協調器

#### `nodriver_fami_date_to_area()`

**簽章**：
```python
async def nodriver_fami_date_to_area(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    last_activity_url: str,         # 活動頁面 URL
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：協調日期選擇與區域選擇流程，處理多組區域關鍵字

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典（讀取 `area_auto_select.area_keyword`）
- `last_activity_url` (str): 活動頁面 URL（用於自動補票）
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `bool`: 操作成功返回 `True`，失敗返回 `False`

**行為**：
1. 讀取區域關鍵字（支援多組，以 `|` 分隔）
2. 對每組關鍵字：
   - 呼叫 `nodriver_fami_area_auto_select()`
   - 若成功：返回 `True`
   - 若失敗：嘗試下一組關鍵字
3. 若所有關鍵字都失敗：
   - 返回 `False`

**錯誤處理**：
- 捕捉所有例外，返回 `False`

**範例**：
```python
success = await nodriver_fami_date_to_area(tab, config_dict, last_activity_url)
```

---

### 8. 首頁自動選擇函數

#### `nodriver_fami_home_auto_select()`

**簽章**：
```python
async def nodriver_fami_home_auto_select(
    tab,                            # NoDriver tab 物件
    config_dict: dict,              # 設定字典
    last_activity_url: str,         # 活動頁面 URL
    show_debug_message: bool = True # 是否顯示除錯訊息
) -> bool
```

**用途**：首頁主要入口點，檢查是否需要票數選擇，若無則進入日期/區域選擇

**參數**：
- `tab` (NoDriver Tab): NoDriver tab 物件
- `config_dict` (dict): 設定字典
- `last_activity_url` (str): 活動頁面 URL
- `show_debug_message` (bool): 是否輸出除錯訊息

**返回值**：
- `bool`: 操作成功返回 `True`，失敗返回 `False`

**行為**：
1. 檢查是否存在票數選擇元素
2. 若不存在：
   - 呼叫 `nodriver_fami_date_auto_select()` 或 `nodriver_fami_date_to_area()`
3. 若存在：
   - 執行票數選擇邏輯（若未來實作）

**錯誤處理**：
- 捕捉所有例外，返回 `False`

---

## 工具函數 (Utility Functions)

### 重用現有工具函數（`src/util.py`）

以下函數**無需重新實作**，直接重用現有版本：

#### `format_keyword_string()`
- **用途**：正規化關鍵字字串（移除空白、轉小寫）
- **簽章**：`def format_keyword_string(keyword: str) -> str`

#### `get_answer_list_from_user_guess_string()`
- **用途**：將答案字串分割為答案清單（逗號分隔）
- **簽章**：`def get_answer_list_from_user_guess_string(answer_string: str) -> list[str]`

#### `guess_tixcraft_question()`
- **用途**：從活動標題推斷驗證問題答案
- **簽章**：`def guess_tixcraft_question(title: str, question: str) -> str`

#### `fill_common_verify_form()`
- **用途**：填寫通用驗證表單（需調整為非同步版本）
- **簽章**：`async def fill_common_verify_form(tab, config_dict, fail_list) -> tuple[bool, list]`

---

## 函數相依性圖 (Function Dependencies)

```
nodriver_famiticket_main()
  ├─ nodriver_fami_login()
  ├─ nodriver_fami_activity()
  └─ nodriver_fami_home_auto_select()
       └─ nodriver_fami_date_to_area()
            ├─ nodriver_fami_date_auto_select()
            └─ nodriver_fami_area_auto_select()
                 └─ nodriver_fami_verify()
                      ├─ util.fill_common_verify_form()
                      ├─ util.guess_tixcraft_question()
                      └─ util.get_answer_list_from_user_guess_string()
```

---

## 契約遵循檢查

| 契約要求 | 遵循狀態 | 證明 |
|---------|---------|------|
| FR-030: 使用 async/await | ✅ | 所有函數簽章包含 `async def` |
| FR-031: 使用 NoDriver tab 物件 | ✅ | 所有函數第一個參數為 `tab` |
| FR-032: 優先使用 CDP 點擊 | ✅ | 所有點擊操作使用 `dispatch_mouse_event()` |
| FR-033: 使用 Pierce 方法搜尋 | ✅ | 所有元素搜尋使用 `perform_search()` |
| FR-034: 使用 NoDriver 導航方法 | ✅ | 使用 `await tab.get()` / `await tab.reload()` |
| FR-035: 使用 NoDriver 等待方法 | ✅ | 使用 `await tab.sleep()` / `await asyncio.sleep()` |
| FR-036: 實作 6 個核心函數 | ✅ | 已定義 8 個函數（含協調器） |
| FR-037: 主函數作為路由器 | ✅ | `nodriver_famiticket_main()` 分派至子函數 |
| FR-038: 返回布林值 | ✅ | 所有函數返回 `bool` 或 `tuple[bool, list]` |
| 命名規範 | ✅ | 所有函數以 `nodriver_fami_` 開頭 |

---

**建立日期**：2025-11-04
**下一步**：產生 `config-schema.md`
