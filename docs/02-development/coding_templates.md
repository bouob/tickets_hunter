# 搶票程式標準架構與範本

**文件說明**：提供 Tickets Hunter 專案的程式碼範本、12 階段實作檢查清單與跨平台可重用程式碼片段
**最後更新**：2026-06-10

---

> Tickets Hunter 多平台搶票系統統一程式碼範本庫

## 📚 **文件參考指南**

本文件專注於提供實際的程式碼範本和實作檢查清單。相關的架構和策略說明請參考：

- **開發規範與 ZenDriver First 策略**：`development_guide.md`
- **12 階段詳細定義**：`ticket_automation_standard.md`
- **平台函式對照表**：`structure.md`

---

## 📖 **本文件包含的內容**

1. **標準範本庫** - 各功能模組的程式碼範本
2. **實作完整度檢查表** - 平台認證標準
3. **平台完成度評分** - 目前各平台的實作狀態
4. **2025 開發建議** - ZenDriver First 優先策略

---

## 🗂️ **快速導航**

### 範本庫 (按功能分類)
- **必要規範** → Debug 標準、暫停機制 (本檔案開頭)
- **主程式架構** → 主控制器範本
- **日期選擇** → 日期自動選擇範本
- **區域座位選擇** → 座位區域選擇範本
- **票券數量** → 票券分配範本
- **同意條款** → 條款勾選範本
- **實名認證** → 身份驗證範本
- **登入處理** → 自動登入範本
- **OCR 驗證碼** → 驗證碼識別範本
- **錯誤處理** → 重試機制範本
- **Cloudflare 處理** → CF 驗證範本

### 檢查清單與評分
- **實作完整度檢查表** → 白金/金/銀級標準
- **平台完成度總覽** → 目前各平台狀態
- **2025 開發建議** → ZenDriver First 策略

---



## 🚨 **必要開發規範**

### Debug 訊息標準格式

#### 🏅 統一標準 - DebugLogger

所有新程式碼必須使用 `DebugLogger`，禁止手寫 `if show_debug_message: print()` 模式。

```python
async def nodriver_platform_function_name(tab, config_dict, ...):
    """
    ZenDriver 版本函數範本
    採用非同步架構，效能更好
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[NoDriver] function_name: starting operation")
    debug.log(f"[NoDriver] config value: {config_dict['key']}")

    try:
        # 主要業務邏輯
        result = await perform_async_operation()

        debug.log(f"[NoDriver] operation result: {result}")

        return result

    except Exception as exc:
        debug.log(f"[NoDriver] Exception: {exc}")
        return False
```

**DebugLogger 最佳實踐**：
- ✅ 函式開頭建立 `debug = util.create_debug_logger(config_dict)`
- ✅ 使用 `debug.log()` 取代 `if show_debug_message: print()`
- ✅ 使用 `[NoDriver]` 字首區分引擎
- ✅ 詳細記錄非同步操作狀態
- ✅ 捕捉並記錄所有異常
- ✅ 使用 f-string 格式化輸出

**時間戳行為**：
- `show_timestamp` ON → 全部輸出（一般 print + debug.log）加 `[HH:MM:SS]`
- `show_timestamp` OFF → 全部不加時間戳
- DebugLogger 不自行加時間戳，統一由 `builtins.print` 覆寫控制

---

#### ❌ 舊模式（已棄用）

以下模式已棄用，不應出現在新程式碼中：

```python
# 禁止使用
show_debug_message = config_dict["advanced"]["verbose"]
if show_debug_message:
    print("message")
```

請改用：

```python
# 正確用法
debug = util.create_debug_logger(config_dict)
debug.log("message")
```

---

---

## 📚 **標準範本庫**

### 🏅 **推薦範本 - ZenDriver 主程式架構**

```python
# platforms/{platform}.py 模組層級狀態（檔案頂部宣告一次）
_state = {}

async def nodriver_{platform}_main(tab, url, config_dict, ocr=None):
    """
    ZenDriver 版本主流程控制 (推薦使用)

    Args:
        tab: ZenDriver Tab 實例
        url: 當前頁面 URL
        config_dict: 設定字典
        ocr: OCR 辨識器 (可選)

    特色:
        - 非同步架構，效能優異
        - 反偵測能力強
        - 記憶體佔用低
    """
    debug = util.create_debug_logger(config_dict)

    # 模組層級狀態管理
    if "fail_list" not in _state:
        _state.update({
            "fail_list": [],                # OCR 失敗記錄
            "start_time": None,             # 計時開始
            "done_time": None,              # 計時結束
            "elapsed_time": None,           # 總耗時
            "played_sound_ticket": False,   # 音效狀態
            "played_sound_order": False,
        })

    debug.log(f"[NoDriver] {platform}_main: processing URL: {url}")

    # URL 路由邏輯
    if '/login' in url or '/sign_in' in url:
        # 登入處理
        if config_dict["advanced"]["{platform}_account"]:
            await nodriver_{platform}_login(tab, config_dict)

    elif '/event' in url or '/activity' in url:
        # 活動列表 / 日期選擇頁面
        _state["start_time"] = time.time()

        if config_dict["date_auto_select"]["enable"]:
            await nodriver_{platform}_date_auto_select(tab, config_dict)

    elif '/area' in url or '/seats' in url:
        # 座位區域選擇頁面
        if config_dict["area_auto_select"]["enable"]:
            await nodriver_{platform}_area_auto_select(tab, config_dict)

    elif '/ticket' in url or '/booking' in url:
        # 票數選擇與驗證碼頁面
        _state["done_time"] = time.time()

        # 票數分配
        await nodriver_{platform}_assign_ticket_number(tab, config_dict)

        # OCR 驗證碼處理
        if ocr and config_dict["ocr_captcha"]["enable"]:
            await nodriver_{platform}_auto_ocr(tab, config_dict, ocr)

    elif '/checkout' in url or '/confirm' in url:
        # 成功頁面
        if _state["start_time"] and _state["done_time"]:
            elapsed = _state["done_time"] - _state["start_time"]
            print(f"[NoDriver] 搶票完成！耗時: {elapsed:.3f} 秒")

    debug.log(f"[NoDriver] {platform}_main completed")
```

**ZenDriver 主程式設計重點**：
- ✅ 使用 `async/await` 架構
- ✅ 完整的狀態追蹤機制
- ✅ URL 路由清晰明確
- ✅ 支援 OCR 可選參數
- ✅ 效能計時與監控

---

## 📅 **日期選擇範本**

### 🏅 **推薦範本 - ZenDriver 日期選擇**

```python
async def nodriver_{platform}_date_auto_select(tab, config_dict):
    """
    ZenDriver 版本日期自動選擇 (推薦使用)

    特色:
        - 非同步查找元素，效能優異
        - 支援 AND/OR 邏輯關鍵字匹配
        - 自動過濾售罄日期
        - 支援多種日期格式
    """
    debug = util.create_debug_logger(config_dict)
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    debug.log(f"[NoDriver] date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 查找日期元素 (非同步)
    date_list = None
    try:
        # 多種選擇器策略
        selectors = [
            'div.date-item',
            '.date-option',
            '.performance-date',
            'li.date-row',
            'button[data-date]'
        ]

        for selector in selectors:
            date_list = await tab.query_selector_all(selector)
            if date_list and len(date_list) > 0:
                break

    except Exception as exc:
        debug.log(f"[NoDriver] find date elements Exception: {exc}")

    if date_list:
        # 關鍵字解析 (支援 AND/OR 邏輯)
        date_keyword_array = date_keyword.split(',') if date_keyword else []

        for date_row in date_list:
            date_text = ""
            try:
                # 非同步獲取文本
                date_text = await date_row.get_property("innerText")
                if not date_text:
                    date_text = await date_row.get_property("textContent")

            except Exception as exc:
                debug.log(f"[NoDriver] get date text Exception: {exc}")
                continue

            if date_text:
                date_text = util.format_keyword_string(date_text)

                debug.log(f"[NoDriver] date_text: {date_text}")

                # 檢查是否售罄
                is_sold_out = any(keyword in date_text.lower() for keyword in
                    ['sold out', '售完', '已售完', '選購一空', '無票'])

                if is_sold_out:
                    debug.log(f"[NoDriver] skip sold out date: {date_text}")
                    continue

                # 關鍵字比對 (AND 邏輯)
                if date_keyword_array:
                    is_match_date = util.is_matched_by_keyword(date_text, date_keyword_array)
                    if is_match_date:
                        matched_blocks.append(date_row)
                else:
                    # 無關鍵字時選擇第一個可用日期
                    matched_blocks.append(date_row)
                    break

        # 選擇目標日期
        if matched_blocks:
            target_date = util.get_target_item_from_matched_list(
                matched_blocks,
                config_dict["date_auto_select"]["mode"]
            )

            if target_date:
                try:
                    await target_date.click()
                    is_date_assigned = True

                    debug.log("[NoDriver] date auto select success")

                except Exception as exc:
                    debug.log(f"[NoDriver] date click Exception: {exc}")

    return is_date_assigned
```

**ZenDriver 日期選擇設計重點**：
- ✅ 支援多種選擇器策略 (適應平台改版)
- ✅ 自動過濾售罄日期
- ✅ 支援 AND/OR 邏輯關鍵字
- ✅ 非同步操作，效能優異
- ✅ 完整的錯誤處理

---

### 🥈 **銀級 - ZenDriver 日期選擇** (簡化版範本)

```python
async def nodriver_{platform}_date_auto_select(tab, config_dict):
    """
    自動選擇演出日期 (ZenDriver 版本)
    """
    debug = util.create_debug_logger(config_dict)
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    debug.log(f"date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 查找日期元素
    date_list = None
    try:
        date_list = await tab.query_selector_all('div.date-item, .date-option, .performance-date')
    except Exception as exc:
        debug.log(f"find date elements Exception: {exc}")

    if date_list:
        date_keyword_array = date_keyword.split(' ')

        for date_row in date_list:
            date_text = ""
            try:
                date_text = await date_row.get_property("innerText")
                if not date_text:
                    date_text = await date_row.get_property("textContent")
            except Exception as exc:
                debug.log(f"get date text Exception: {exc}")
                continue

            if date_text:
                date_text = util.format_keyword_string(date_text)
                debug.log(f"date_text: {date_text}")

                # 關鍵字比對
                is_match_date = util.is_matched_by_keyword(date_text, date_keyword_array)
                if is_match_date:
                    matched_blocks.append(date_row)

        # 選擇目標日期
        if matched_blocks:
            target_date = util.get_target_item_from_matched_list(matched_blocks, config_dict["date_auto_select"]["mode"])
            if target_date:
                try:
                    await target_date.click()
                    is_date_assigned = True
                    debug.log("date auto select success")
                except Exception as exc:
                    debug.log(f"date click Exception: {exc}")

    return is_date_assigned
```

---

## 🎭 **區域座位選擇範本**

### 關鍵字處理標準規範

#### 關鍵字格式說明
關鍵字設定採用 JSON 陣列格式，支援以下模式：

```json
// 單一關鍵字
"area_keyword": "\"VIP票\""

// 多關鍵字 (OR 邏輯)
"area_keyword": "\"VIP票\",\"搖滾區\",\"A區\""

// 多關鍵字 (AND 邏輯，空格分隔)
"area_keyword": "\"VIP 搖滾區\""

// 優先級範例
"area_keyword": "\"2樓 A區\",\"1樓 VIP\",\"B區\""
```

#### 使用說明

**邏輯規則**：
- **OR 邏輯**：按陣列順序，找到第一個比對就選擇
- **AND 邏輯**：空格分隔表示必須全部包含
- **空字串**：不使用關鍵字，改用自動選擇模式（random/從上到下/從下到上）

**注意事項**：
- 大小寫不敏感（自動處理）
- 引號為 JSON 格式必要
- 建議關鍵字越精確越好，避免誤選

#### 關鍵字解析規範
## 🎟️ **票券數量選擇範本**

## ✅ **同意條款處理範本**

### ZenDriver 版本 【推薦使用】
```python
async def nodriver_{platform}_ticket_agree(tab, config_dict):
    """
    自動勾選同意條款 (ZenDriver 版本)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("checking agreement checkboxes")

    is_agree_success = False

    # 查找同意條款選項
    selectors = [
        'input[type="checkbox"]',
        'input#agree',
        '.agreement-checkbox input',
        'input[name*="agree"]'
    ]

    for selector in selectors:
        try:
            checkboxes = await tab.query_selector_all(selector)
            if checkboxes:
                for checkbox in checkboxes:
                    try:
                        # 檢查是否已勾選
                        is_checked = await checkbox.get_property("checked")
                        if not is_checked:
                            await checkbox.click()
                            is_agree_success = True

                            debug.log("agreement checkbox checked")

                    except Exception as exc:
                        debug.log(f"checkbox click Exception: {exc}")
                break
        except Exception as exc:
            debug.log(f"find checkboxes with {selector} Exception: {exc}")

    return is_agree_success
```

---

## 🆔 **實名認證處理範本**

### ZenDriver 版本 【推薦使用】
```python
async def nodriver_{platform}_real_name_verify(tab, config_dict):
    """
    自動填寫實名認證資料 (ZenDriver 版本)
    """
    debug = util.create_debug_logger(config_dict)
    real_name = config_dict["advanced"]["{platform}_real_name"].strip()
    id_number = config_dict["advanced"]["{platform}_id_number"].strip()

    debug.log(f"real_name: {real_name}")
    debug.log(f"id_number: {id_number[:3]}***")

    is_real_name_filled = False

    if len(real_name) > 0 and len(id_number) > 0:
        try:
            # 查找並填寫姓名
            name_selectors = [
                'input[name="real_name"]',
                'input[name="name"]',
                'input.real-name',
                'input#real_name'
            ]

            name_input = None
            for selector in name_selectors:
                try:
                    name_input = await tab.query_selector(selector)
                    if name_input:
                        break
                except:
                    continue

            # 查找並填寫身分證號
            id_selectors = [
                'input[name="id_number"]',
                'input[name="identity"]',
                'input.id-number',
                'input#id_number'
            ]

            id_input = None
            for selector in id_selectors:
                try:
                    id_input = await tab.query_selector(selector)
                    if id_input:
                        break
                except:
                    continue

            # 填寫資料
            if name_input:
                await name_input.click()
                await name_input.send_keys(real_name)

            if id_input:
                await id_input.click()
                await id_input.send_keys(id_number)

            if name_input and id_input:
                is_real_name_filled = True

                debug.log("real name verification filled")

        except Exception as exc:
            debug.log(f"real name verification Exception: {exc}")

    return is_real_name_filled
```

---

## 🔐 **登入處理範本**

## 🎨 **OCR 驗證碼處理範本**

## 📝 **錯誤處理與重試機制**

### 標準錯誤處理
```python
def {platform}_function_with_retry(driver, config_dict, max_retry=3):
    """
    帶重試機制的函數範本
    """
    debug = util.create_debug_logger(config_dict)

    for retry_count in range(max_retry):
        try:
            if retry_count > 0:
                debug.log(f"retry attempt {retry_count}/{max_retry-1}")
                time.sleep(1)  # 重試間隔

            # 主要邏輯
            result = perform_main_logic()

            if result:
                debug.log(f"operation success on attempt {retry_count + 1}")
                return True

        except Exception as exc:
            debug.log(f"attempt {retry_count + 1} failed: {exc}")

            if retry_count == max_retry - 1:
                print("all retry attempts failed")

    return False
```

---

## 🛑 **暫停機制標準範本** (ZenDriver 專用)

> 統一的暫停檢查機制，確保使用者可隨時中斷執行

### 核心暫停檢查函式

#### `check_and_handle_pause(config_dict)`
主要暫停檢查函式，所有平台函式都應使用此統一入口。

**位置**：`src/nodriver_common.py`

**行為說明**：
- 檢查暫停檔案 `MAXBOT_INT28_IDLE.txt` 是否存在
- 根據 `config_dict["advanced"]["verbose"]` 控制訊息顯示
- `verbose = true` → 顯示 "BOT Paused."
- `verbose = false` → 不顯示訊息

**使用情境**：
1. 函式開始時檢查
2. 長時間迴圈中定期檢查
3. 關鍵操作前檢查

**範本**：
```python
async def nodriver_platform_function(tab, config_dict):
    """平台功能函數範本"""
    debug = util.create_debug_logger(config_dict)

    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    # 執行主要邏輯...
    for i in range(100):
        # 長迴圈中定期檢查
        if await check_and_handle_pause(config_dict):
            break

        # 執行操作...
        await tab.sleep(0.1)

    return True
```

---

### 暫停輔助函式

#### 1. `sleep_with_pause_check(tab, seconds, config_dict)`
取代 `tab.sleep()`，在等待期間檢查暫停狀態。

**位置**：`src/nodriver_common.py`

**使用時機**：需要延遲等待的 ZenDriver 函式

**範本**：
```python
# 一般等待（無暫停檢查）
await tab.sleep(0.6)

# 改為：支援暫停的等待
if await sleep_with_pause_check(tab, 0.6, config_dict):
    debug.log("Operation paused during wait")
    return False  # 暫停中，提前返回
```

#### 2. `asyncio_sleep_with_pause_check(seconds, config_dict)`
取代 `asyncio.sleep()`，在等待期間檢查暫停狀態。

**位置**：`src/nodriver_common.py`

**使用時機**：不需要 tab 物件的純延遲等待

**範本**：
```python
import asyncio

# 一般等待
await asyncio.sleep(0.5)

# 改為：支援暫停的等待
if await asyncio_sleep_with_pause_check(0.5, config_dict):
    return False
```

#### 3. `evaluate_with_pause_check(tab, javascript_code, config_dict)`
在執行 JavaScript 前檢查暫停狀態。

**位置**：`src/nodriver_common.py`

**使用時機**：執行較長時間的 JavaScript 操作前

**範本**：
```python
# 一般執行
result = await tab.evaluate('...')

# 改為：執行前檢查暫停
result = await evaluate_with_pause_check(tab, '''
    (function() {
        return document.querySelectorAll('.date-item').length;
    })();
''', config_dict)

if result is None:  # 暫停中
    return False
```

#### 4. `with_pause_check(task_func, config_dict, *args, **kwargs)`
包裝長時間任務，支援中途暫停。

**位置**：`src/nodriver_common.py`

**使用時機**：執行耗時較長的非同步任務

**範本**：
```python
# 包裝耗時任務
result = await with_pause_check(
    long_running_task,
    config_dict,
    param1, param2
)

if result is None:
    return False  # 任務被暫停
```

---

### 完整實作範例

```python
async def nodriver_platform_date_auto_select(tab, config_dict):
    """
    日期選擇 - 完整暫停機制範例

    展示如何在關鍵位置整合暫停檢查機制
    """
    debug = util.create_debug_logger(config_dict)
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    # 1. 函數開始時檢查
    if await check_and_handle_pause(config_dict):
        return False

    debug.log(f"[NoDriver] date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 2. 等待頁面載入（支援暫停）
    if await sleep_with_pause_check(tab, 0.6, config_dict):
        debug.log("[NoDriver] Paused during page load")
        return False

    # 3. JavaScript 執行前檢查
    result = await evaluate_with_pause_check(tab, '''
        (function() {
            const elements = document.querySelectorAll('.date-item');
            return {
                count: elements.length,
                found: elements.length > 0
            };
        })();
    ''', config_dict)

    if result is None:  # 暫停中
        return False

    if not result.get('found', False):
        return False

    # 4. 查找日期元素
    date_list = None
    try:
        date_list = await tab.query_selector_all('.date-item, .date-option')
    except Exception as exc:
        debug.log(f"[NoDriver] find date elements Exception: {exc}")

    if not date_list:
        return False

    # 5. 長時間迴圈中檢查
    for date_row in date_list:
        # 每次迭代檢查暫停
        if await check_and_handle_pause(config_dict):
            break

        try:
            date_text = await date_row.get_property("innerText")
            if date_text:
                # 處理日期文本...
                matched_blocks.append(date_row)
        except Exception as exc:
            debug.log(f"[NoDriver] get date text Exception: {exc}")
            continue

    # 6. 選擇並點擊日期
    if matched_blocks:
        target_date = matched_blocks[0]
        try:
            await target_date.click()
            is_date_assigned = True

            debug.log("[NoDriver] date auto select success")
        except Exception as exc:
            debug.log(f"[NoDriver] date click Exception: {exc}")

    return is_date_assigned
```

---

### 重要規則與最佳實踐

#### 1. **統一使用 `check_and_handle_pause()`**
- ✅ 正確：使用統一函式
  ```python
  if await check_and_handle_pause(config_dict):
      return False
  ```
- ❌ 錯誤：直接檢查檔案
  ```python
  # 禁止直接檢查，破壞統一性
  if os.path.exists(CONST_MAXBOT_INT28_FILE):
      print("BOT Paused.")
      return False
  ```

#### 2. **訊息顯示由 verbose 統一控制**
- 所有暫停訊息都應該根據 `config_dict["advanced"]["verbose"]` 決定是否顯示
- 不要在呼叫端額外加入訊息顯示邏輯
- 保持行為一致性

#### 3. **僅在 ZenDriver 版本實作**
- 保持兩個版本的功能差異性
- ZenDriver 版本的優勢之一

#### 4. **暫停後的處理**
- 偵測到暫停後應該 `return` 而非 `break`
- 回傳值應該表示操作未完成（通常是 `False`）
- 確保函式狀態一致性

#### 5. **檢查時機建議**
- **必須**：函式開始時檢查
- **建議**：長時間操作前檢查（如 JavaScript 執行）
- **必須**：長時間迴圈內每次迭代檢查
- **建議**：延遲等待時使用暫停版本（`sleep_with_pause_check`）

---

### 檢查清單

開發 ZenDriver 函式時，確保：
- [ ] 函式開始時呼叫 `check_and_handle_pause()`
- [ ] 所有 `tab.sleep()` 改用 `sleep_with_pause_check()`
- [ ] 所有 `asyncio.sleep()` 改用 `asyncio_sleep_with_pause_check()`
- [ ] 長時間迴圈內加入暫停檢查
- [ ] 暫停後返回適當的失敗值（通常是 `False`）
- [ ] 不要直接檢查 `CONST_MAXBOT_INT28_FILE`

---

## 🏗️ **搶票系統核心架構分析**

> 基於 TixCraft 和 KKTIX 完整實作分析

### 核心功能模組架構

#### 1. 主程式控制器 (Main Controller)
```python
# 功能: 統籌整個搶票流程，根據 URL 路由分發至各功能模組
{platform}_main(driver, url, config_dict, ocr, Captcha_Browser)
```
**責任範圍**:
- URL 路由判斷 (`/login`, `/event`, `/ticket`, `/area`, `/checkout`)
- 流程狀態管理（模組層級 `_state` dict）
- 時間追蹤 (`start_time`, `done_time`, `elapsed_time`)
- 音效提醒控制 (`played_sound_ticket`, `played_sound_order`)

#### 2. 日期時段選擇模組 (Date Selection)
```python
# 功能: 自動選擇演出日期與時段
{platform}_date_auto_select(driver, url, config_dict, domain_name)
```
**核心邏輯**:
- **關鍵字比對**: JSON 陣列格式支援 AND/OR 邏輯
- **售罄偵測**: 過濾 "選購一空"、"已售完"、"Sold out" 等狀態
- **即將開賣**: 偵測 "開賣倒數" 並自動重載頁面
- **多語言支援**: 繁中、英文、日文介面適配
- **選擇模式**: from top to bottom, center, random

#### 3. 座位區域選擇模組 (Area Selection)
```python
# 功能: 根據關鍵字自動選擇座位區域
{platform}_area_auto_select(driver, url, config_dict)
```
**智慧選擇邏輯**:
- **剩餘座位檢查**: 避免選擇座位不足的區域 (檢查字體標註的剩餘數量)
- **關鍵字過濾**: 支援多關鍵字 AND 邏輯比對
- **排除關鍵字**: 避開不想選擇的區域
- **優先順序排序**: 依選擇模式決定優先順序

#### 4. 票數分配模組 (Ticket Quantity)
```python
# 功能: 自動設定票券數量
{platform}_assign_ticket_number(driver, config_dict)
```
**適應性選擇器**:
- **多選擇器支援**: `.mobile-select`, `select.form-select`, `input[type="text"]`
- **區域繫結**: 根據選取區域自動定位對應票數選擇器
- **數量驗證**: 檢查目前值避免重複設定
- **回退機制**: 目標數量不可選時回退至 1 張

#### 5. 驗證碼處理模組 (CAPTCHA/OCR)
```python
# 功能: 自動識別並填入驗證碼
{platform}_auto_ocr(driver, ocr, config_dict, Captcha_Browser)
{platform}_get_ocr_answer(driver, ocr, image_source, Captcha_Browser)
```
**多重處理策略**:
- **Canvas 擷取**: 使用 JavaScript 從圖片元素提取 base64
- **NonBrowser 備案**: Canvas 失敗時的外部 API 方案
- **長度驗證**: 檢查答案長度 (通常 4 位)
- **重試機制**: 最多 19 次重試
- **驗證碼刷新**: 點擊圖片重新產生驗證碼

#### 6. 登入認證模組 (Authentication)
```python
# 功能: 自動登入與狀態維護
{platform}_login(driver, config_dict)
```
**認證流程**:
- **多平台適配**: 不同表單選擇器
- **密碼解密**: 支援加密密碼儲存
- **登入狀態檢查**: Cookie 驗證
- **Cloudflare 處理**: 針對 ZenDriver 版本

#### 7. 同意條款模組 (Agreement)
```python
# 功能: 自動勾選必要的同意條款
{platform}_ticket_main_agree(driver, config_dict)
```
**智慧勾選**:
- **條件判斷**: 檢查是否已勾選
- **多次重試**: 最多 3 次嘗試
- **強制點擊**: JavaScript 備案

#### 8. 狀態監控模組 (Status Monitoring)
```python
# 功能: 監控頁面狀態與流程追蹤
{platform}_check_register_status(driver, url)
```
**關鍵監控點**:
- **搶票成功**: 偵測到 `/checkout` 頁面
- **排隊狀態**: 監控排隊頁面變化
- **錯誤頁面**: 自動回退或重新整理
- **效能追蹤**: 計算搶票耗時

## 🎯 **實作檢查清單**

### 必備核心功能 (8/8)
- [x] **主程式控制**: `{platform}_main()` / `nodriver_{platform}_main()`
- [x] **日期時段選擇**: `{platform}_date_auto_select()`
- [x] **座位區域選擇**: `{platform}_area_auto_select()`
- [x] **票數分配**: `{platform}_assign_ticket_number()`
- [x] **驗證碼處理**: `{platform}_auto_ocr()` + `{platform}_get_ocr_answer()`
- [x] **登入認證**: `{platform}_login()`
- [x] **同意條款**: `{platform}_ticket_main_agree()`
- [x] **狀態監控**: 流程追蹤與錯誤處理

### 進階功能模組 (6/6)
- [x] **智慧重試**: 自動重新整理與重試機制
- [x] **多語言支援**: 繁中/英文/日文介面適配
- [x] **效能最佳化**: DOM 尋找快取與最小化等待
- [x] **音效提醒**: 搶票成功與失敗音效
- [x] **除錯模式**: 完整的 debug 輸出系統
- [x] **擴充套件整合**: 瀏覽器擴充功能協作模式

### 平台特殊功能
- [x] **TixCraft**: 區域多選擇器、即將開賣重載、驗證碼 Toast 提示
- [x] **KKTIX**: 實名制表單、Cloudflare 驗證、危險庫存檢查
- [ ] **TicketMaster**: 區域 JavaScript 選擇、座位地圖、Promo Code
- [ ] **iBon**: 鄰座限制、實名制欄位、特殊驗證碼格式

### 程式碼品質標準

#### 編碼規範檢查
- [x] **命名一致性**: `platform_function_name` 格式
- [x] **Debug 標準**: `debug = util.create_debug_logger(config_dict)`
- [x] **異常處理**: 所有 DOM 操作包覆 try-catch
- [x] **狀態追蹤**: 模組層級 `_state` dict 管理
- [x] **註解完整**: 函式用途、參數說明、回傳值說明

#### 效能與可靠性
- [x] **選擇器最佳化**: 使用高效能 CSS 選擇器
- [x] **等待機制**: 適當的 sleep 與 WebDriverWait
- [x] **重試邏輯**: 關鍵操作最多重試 3-19 次
- [x] **記憶體管理**: 及時釋放大型物件
- [x] **相容性**: 支援多瀏覽器與多作業系統

---

## 🛡️ **Cloudflare 驗證處理**

### ZenDriver Cloudflare 處理
**官方文件**: https://zendriver.dev/

```python
async def handle_cloudflare_verification(tab, config_dict):
    """
    處理 Cloudflare 驗證挑戰
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # 使用 zendriver 內建方法
        await tab.verify_cf()
        debug.log("Cloudflare 驗證處理完成")
    except AttributeError:
        # 如果方法不存在，使用手動檢測
        try:
            current_url = tab.url
            page_content = await tab.get_content()

            if ("cloudflare" in current_url.lower() or
                "cf-challenge" in current_url.lower() or
                "Checking your browser" in page_content):

                debug.log("偵測到 Cloudflare 驗證頁面，等待驗證完成...")

                # 等待驗證完成
                await tab.wait_for(cdp.page.load_event_fired)
                time.sleep(5)

        except Exception as manual_cf_e:
            debug.log(f"Manual Cloudflare verification check: {manual_cf_e}")
    except Exception as cf_e:
        debug.log(f"Cloudflare verification error: {cf_e}")
```

### 登入後 Cloudflare 處理範本
```python
async def nodriver_{platform}_login(tab, config_dict):
    """
    登入後處理 Cloudflare 驗證
    """
    debug = util.create_debug_logger(config_dict)

    # 執行登入操作
    await submit_login_form(tab, config_dict)

    # 等待頁面響應，可能出現 Cloudflare 驗證
    time.sleep(3)

    # 處理 Cloudflare 驗證
    await handle_cloudflare_verification(tab, config_dict)
```

**注意事項**:
- 需安裝 `opencv-python` 套件
- 目前僅支援英文介面驗證
- 建議在登入、頁面跳轉後呼叫

---

## 🎫 **TicketPlus 平台特殊實作**

### 登入處理
```python
async def nodriver_ticketplus_is_signin(tab)                    # 判斷是否已登入
async def nodriver_ticketplus_account_auto_fill(tab, config_dict)  # 填入帳密
async def nodriver_ticketplus_account_sign_in(tab, config_dict)    # 送出登入
```

### 彈出視窗處理機制
```python
async def nodriver_ticketplus_accept_realname_card(tab)     # 實名制彈出視窗
async def nodriver_ticketplus_accept_other_activity(tab)    # 其他活動推薦
async def nodriver_ticketplus_accept_order_fail(tab)        # 訂單失敗
```

### 與標準階段的對應

TicketPlus 的實作與 12 階段標準有三處刻意偏離：

| 標準階段 | TicketPlus 實作 | 說明 |
|---------|----------------|------|
| 5 區域選擇 + 6 票數設定 | `nodriver_ticketplus_unified_select()` | 展開式面板，兩階段在同一頁完成，因此合併為單一函式 |
| 7 CAPTCHA | 無 | 目前活動不使用圖形驗證碼，改用優惠代碼 `order_exclusive_code`。`ocr` 與 `Captcha_Browser` 參數僅為簽章穿透，函式內未使用 |
| 2 身分驗證 | `nodriver_ticketplus_account_sign_in()` | 字尾為 `_sign_in` 而非規範的 `_signin`，屬既有偏離 |

版面差異由 `nodriver_ticketplus_detect_layout_style()` 判定後分派。

---

## 🔍 **除錯技巧**

### Debug 輸出標準格式
```python
debug = util.create_debug_logger(config_dict)

debug.log(f"function_name: variable_name = {variable_value}")
debug.log(f"DOM elements found: {len(element_list)}")
debug.log(f"operation result: {is_success}")
```

### 常用除錯程式碼
```python
debug = util.create_debug_logger(config_dict)

# DOM 元素檢查
debug.log(f"element exists: {element is not None}")
debug.log(f"element text: {element.text if element else 'None'}")

# 狀態追蹤
debug.log(f"current URL: {driver.current_url}")
debug.log(f"page title: {driver.title}")
```

---

## 🚀 **完整平台實作範例**

### 基於實際 TixCraft/KKTIX 分析的標準模版

### 🔧 **關鍵設計模式**

#### 1. **狀態管理模式**
```python
# 模組層級 _state dict 管理所有狀態（platforms/*.py 檔案頂部宣告）
_state = {}

# 函式內首次使用時初始化
if "fail_list" not in _state:
    _state.update({
        "fail_list": [],           # 失敗記錄
        "start_time": None,        # 計時系統
        "done_time": None,
        "elapsed_time": None,
        "played_sound_ticket": False,  # 音效控制
        "played_sound_order": False,
        "retry_count": 0,          # 重試計數
    })
```

#### 2. **模組化設計模式**
```python
# 每個功能獨立函數，可單獨測試與維護
{platform}_date_auto_select()    # 日期選擇模組
{platform}_area_auto_select()    # 區域選擇模組
{platform}_assign_ticket_number() # 票數分配模組
{platform}_auto_ocr()            # 驗證碼模組
```

#### 3. **錯誤處理模式**
```python
# 標準錯誤處理與重試
debug = util.create_debug_logger(config_dict)
for retry_count in range(max_retry):
    try:
        result = perform_operation()
        if result:
            break
    except Exception as exc:
        debug.log(f"attempt {retry_count + 1} failed: {exc}")
        if retry_count == max_retry - 1:
            print("all attempts failed")
```

#### 4. **效能監控模式**
```python
# 標準效能追蹤
start_time = time.time()
# ... 執行搶票邏輯 ...
done_time = time.time()
elapsed_time = done_time - start_time
print("elapsed time:", "{:.3f}".format(elapsed_time))
```

## ✅ **實作完整度檢查表**

### 🎯 **平台實作評分標準**

#### 🏅 **白金級認證標準** (95%+)
- [ ] **8個核心函式完整實作**
  - [ ] `{platform}_main()` - 主流程控制
  - [ ] `{platform}_date_auto_select()` - 日期選擇
  - [ ] `{platform}_area_auto_select()` - 區域選擇
  - [ ] `{platform}_assign_ticket_number()` - 票數分配
  - [ ] `{platform}_auto_ocr()` - OCR處理
  - [ ] `{platform}_login()` - 登入處理
  - [ ] `{platform}_ticket_agree()` - 同意條款
  - [ ] `{platform}_check_status()` - 狀態監控

- [ ] **程式碼品質標準**
  - [ ] 無 TODO 標記
  - [ ] 完整異常處理
  - [ ] 統一 debug 輸出格式
  - [ ] 完整函式註解

- [ ] **功能驗證標準**
  - [ ] 實戰測試通過
  - [ ] 支援多語言介面
  - [ ] 智慧重試機制
  - [ ] 效能追蹤機制

#### 🥇 **金級認證標準** (80-95%)
- [ ] **6個主要函式實作**
  - [ ] 核心購票流程完整
  - [ ] 基本錯誤處理機制
  - [ ] 平台特殊功能支援

- [ ] **程式碼品質標準**
  - [ ] 少量 TODO (≤3個)
  - [ ] 基本異常處理
  - [ ] debug 輸出規範

#### 🥈 **銀級認證標準** (60-80%)
- [ ] **基本架構完整**
  - [ ] 主要流程可執行
  - [ ] 基本功能實作

- [ ] **需要改善項目**
  - [ ] TODO 標記較多 (4-10個)
  - [ ] 部分功能未完成
  - [ ] 錯誤處理需強化

### 🚨 **開發檢查清單**

#### **開始新平台開發前**
- [ ] 選擇參考範本（建議 `platforms/tixcraft.py`，見 `docs/04-implementation/platform-examples/tixcraft-reference.md`）
- [ ] 確認平台特殊需求
- [ ] 建立測試環境
- [ ] 閱讀平台技術文件

#### **開發過程中**
- [ ] 遵循標準函式命名
- [ ] 實作標準 debug 輸出
- [ ] 每個函式加入異常處理
- [ ] 定期執行實戰測試

#### **完成開發後**
- [ ] 使用完整度檢查表評分
- [ ] 清理所有 TODO 標記
- [ ] 更新 platforms.md 函式對照
- [ ] 執行完整功能測試

### 📊 **平台完成度總覽**

平台完成度以 `docs/02-development/structure.md` 的「平台實作狀態」表為單一真相源，
本文件不重複維護一份，避免兩邊數字互相矛盾。

---

### ⭐ **開發建議**

#### **優先採用策略**

**新專案開發** (強烈推薦 ZenDriver):
1. **首選平台**: ZenDriver TixCraft / KKTIX / TicketPlus
2. **理由**:
   - ✅ 反偵測能力強，不易被封鎖
   - ✅ 記憶體效率高，可多開瀏覽器
   - ✅ 非同步架構，效能優異
   - ✅ 實戰驗證，穩定可靠
3. **學習路徑**: async/await → ZenDriver API → 平台業務邏輯

---

### 🚀 **ZenDriver 開發優勢**

#### 技術優勢
- ✅ **反偵測**: 通過 Cloudflare、reCAPTCHA 等防護
- ✅ **效能**: 記憶體佔用低
- ✅ **穩定**: 三大平台實測成功率 90%+
- ✅ **維護**: 活躍社群，持續更新

#### 實作優勢
- ✅ **範本完整**: 三大平台完整參考實作
- ✅ **文件齊全**: API 指南、除錯方法論
- ✅ **社群支援**: GitHub Issues、文件完善

---

### 🎯 **平台選擇建議**

| 需求情境 | 推薦方案 | 理由 |
|---------|---------|------|
| 正式搶票 | ZenDriver TixCraft/KKTIX/TicketPlus | 反偵測 + 高成功率 |
| 學習研究 | ZenDriver TixCraft | 架構完整 + 文件齊全 |
| 平台移植 | 參考 ZenDriver 三大平台 | 設計模式一致 |

---

此分級系統確保開發者能夠：
- ✅ 選擇最適合的技術方案
- ✅ 遵循 ZenDriver First 策略
- ✅ 建立一致的程式碼品質標準
- ✅ 提升整體系統可維護性
---

**最後更新**: 2026-09-16
