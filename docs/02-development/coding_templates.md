# 搶票程式標準架構與範本

> Tickets Hunter 多平台搶票系統統一代碼範本庫

## 📚 **文件參考指南**

本文件專注於提供實際的程式碼範本和實作檢查清單。相關的架構和策略說明請參考：

- **開發規範與 NoDriver First 策略**：`development_guide.md`
- **12 階段詳細定義**：`ticket_automation_standard.md`
- **平台函數對照表**：`structure.md`

---

## 📖 **本文件包含的內容**

1. **標準範本庫** - 各功能模組的代碼範本（NoDriver 和 Chrome 版本）
2. **實作完整度檢查表** - 平台認證標準
3. **平台完成度評分** - 當前各平台的實作狀態
4. **2025 開發建議** - NoDriver First 優先策略

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
- **平台完成度總覽** → 當前各平台狀態
- **2025 開發建議** → NoDriver First 策略

---



## 🚨 **必要開發規範**

### Debug 訊息標準格式

#### 🏅 推薦標準 - NoDriver 版本 (async/await)

```python
async def nodriver_platform_function_name(tab, config_dict, ...):
    """
    NoDriver 版本函數範本
    採用非同步架構，效能更好
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print(f"[NoDriver] function_name: starting operation")
        print(f"[NoDriver] config value: {config_dict['key']}")

    try:
        # 主要業務邏輯
        result = await perform_async_operation()

        if show_debug_message:
            print(f"[NoDriver] operation result: {result}")

        return result

    except Exception as exc:
        if show_debug_message:
            print(f"[NoDriver] Exception: {exc}")
        return False
```

**NoDriver Debug 最佳實踐**：
- ✅ 使用 `[NoDriver]` 前綴區分引擎
- ✅ 詳細記錄非同步操作狀態
- ✅ 捕獲並記錄所有異常
- ✅ 使用 f-string 格式化輸出

---

#### 🥈 傳統標準 - Chrome/Selenium 版本 (同步)

```python
def platform_function_name(driver, config_dict, ...):
    """
    Chrome/Selenium 版本函數範本
    適用於過渡期或測試環境
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print(f"[Chrome] function_name: starting operation")

    try:
        # 主要業務邏輯
        result = perform_operation()

        if show_debug_message:
            print(f"[Chrome] operation result: {result}")

        return result

    except Exception as exc:
        if show_debug_message:
            print(f"[Chrome] Exception: {exc}")
        return False
```

**Chrome Debug 注意事項**：
- ⚠️ 使用 `[Chrome]` 前綴標記傳統方法
- ⚠️ 適合除錯但不適合生產環境
- ⚠️ 建議逐步遷移至 NoDriver

---

---

## 📚 **標準範本庫**

### 🏅 **推薦範本 - NoDriver 主程式架構**

```python
async def nodriver_{platform}_main(tab, url, config_dict, ocr=None):
    """
    NoDriver 版本主流程控制 (推薦使用)

    Args:
        tab: NoDriver Tab 實例
        url: 當前頁面 URL
        config_dict: 設定字典
        ocr: OCR 辨識器 (可選)

    特色:
        - 非同步架構，效能優異
        - 反偵測能力強
        - 記憶體佔用低
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 全域狀態管理
    global {platform}_dict
    if not '{platform}_dict' in globals():
        {platform}_dict = {}
        {platform}_dict["fail_list"] = []           # OCR 失敗記錄
        {platform}_dict["start_time"] = None        # 計時開始
        {platform}_dict["done_time"] = None         # 計時結束
        {platform}_dict["elapsed_time"] = None      # 總耗時
        {platform}_dict["played_sound_ticket"] = False  # 音效狀態
        {platform}_dict["played_sound_order"] = False

    if show_debug_message:
        print(f"[NoDriver] {platform}_main: processing URL: {url}")

    # URL 路由邏輯
    if '/login' in url or '/sign_in' in url:
        # 登入處理
        if config_dict["advanced"]["{platform}_account"]:
            await nodriver_{platform}_login(tab, config_dict)

    elif '/event' in url or '/activity' in url:
        # 活動列表 / 日期選擇頁面
        {platform}_dict["start_time"] = time.time()

        if config_dict["date_auto_select"]["enable"]:
            await nodriver_{platform}_date_auto_select(tab, config_dict)

    elif '/area' in url or '/seats' in url:
        # 座位區域選擇頁面
        if config_dict["area_auto_select"]["enable"]:
            await nodriver_{platform}_area_auto_select(tab, config_dict)

    elif '/ticket' in url or '/booking' in url:
        # 票數選擇與驗證碼頁面
        {platform}_dict["done_time"] = time.time()

        # 票數分配
        await nodriver_{platform}_assign_ticket_number(tab, config_dict)

        # OCR 驗證碼處理
        if ocr and config_dict["ocr_captcha"]["enable"]:
            await nodriver_{platform}_auto_ocr(tab, config_dict, ocr)

    elif '/checkout' in url or '/confirm' in url:
        # 成功頁面
        if {platform}_dict["start_time"] and {platform}_dict["done_time"]:
            elapsed = {platform}_dict["done_time"] - {platform}_dict["start_time"]
            print(f"[NoDriver] 搶票完成！耗時: {elapsed:.3f} 秒")

    if show_debug_message:
        print(f"[NoDriver] {platform}_main completed")
```

**NoDriver 主程式設計重點**：
- ✅ 使用 `async/await` 架構
- ✅ 完整的狀態追蹤機制
- ✅ URL 路由清晰明確
- ✅ 支援 OCR 可選參數
- ✅ 效能計時與監控

---

### 🥈 **傳統範本 - Chrome/Selenium 主程式架構**

```python
def {platform}_main(driver, url, config_dict, ocr=None):
    """
    Chrome/Selenium 版本主流程控制 (過渡期使用)

    Args:
        driver: WebDriver 實例
        url: 當前頁面 URL
        config_dict: 設定字典
        ocr: OCR 辨識器 (可選)

    限制:
        - 同步架構，效能較差
        - 容易被偵測
        - 建議遷移至 NoDriver
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    global {platform}_dict
    if not '{platform}_dict' in globals():
        {platform}_dict = {}
        {platform}_dict["fail_list"] = []
        {platform}_dict["start_time"] = None
        {platform}_dict["done_time"] = None

    if show_debug_message:
        print(f"[Chrome] {platform}_main: processing URL: {url}")

    # URL 路由邏輯 (同步版本)
    if '/login' in url:
        {platform}_login(driver, config_dict)
    elif '/event' in url:
        {platform}_dict["start_time"] = time.time()
        {platform}_date_auto_select(driver, config_dict)
        {platform}_area_auto_select(driver, config_dict)
    elif '/ticket' in url:
        {platform}_assign_ticket_number(driver, config_dict)
        if ocr:
            {platform}_auto_ocr(driver, config_dict, ocr)

    if show_debug_message:
        print(f"[Chrome] {platform}_main completed")
```

---

## 📅 **日期選擇範本**

### 🏅 **推薦範本 - NoDriver 日期選擇**

```python
async def nodriver_{platform}_date_auto_select(tab, config_dict):
    """
    NoDriver 版本日期自動選擇 (推薦使用)

    特色:
        - 非同步查找元素，效能優異
        - 支援 AND/OR 邏輯關鍵字匹配
        - 自動過濾售罄日期
        - 支援多種日期格式
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    if show_debug_message:
        print(f"[NoDriver] date_keyword: {date_keyword}")

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
        if show_debug_message:
            print(f"[NoDriver] find date elements Exception: {exc}")

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
                if show_debug_message:
                    print(f"[NoDriver] get date text Exception: {exc}")
                continue

            if date_text:
                date_text = util.format_keyword_string(date_text)

                if show_debug_message:
                    print(f"[NoDriver] date_text: {date_text}")

                # 檢查是否售罄
                is_sold_out = any(keyword in date_text.lower() for keyword in
                    ['sold out', '售完', '已售完', '選購一空', '無票'])

                if is_sold_out:
                    if show_debug_message:
                        print(f"[NoDriver] skip sold out date: {date_text}")
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

                    if show_debug_message:
                        print("[NoDriver] date auto select success")

                except Exception as exc:
                    if show_debug_message:
                        print(f"[NoDriver] date click Exception: {exc}")

    return is_date_assigned
```

**NoDriver 日期選擇設計重點**：
- ✅ 支援多種選擇器策略 (適應平台改版)
- ✅ 自動過濾售罄日期
- ✅ 支援 AND/OR 邏輯關鍵字
- ✅ 非同步操作，效能優異
- ✅ 完整的錯誤處理

---

### 🥈 **傳統範本 - Chrome 日期選擇**
```python
def {platform}_date_auto_select(driver, config_dict):
    """
    自動選擇演出日期
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    if show_debug_message:
        print(f"date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 查找日期元素
    date_list = None
    try:
        date_list = driver.find_elements(By.CSS_SELECTOR, 'div.date-item, .date-option, .performance-date')
    except Exception as exc:
        if show_debug_message:
            print("find date elements Exception:", exc)

    if date_list:
        date_keyword_array = date_keyword.split(' ')

        for date_row in date_list:
            date_text = ""
            try:
                date_text = date_row.get_attribute("innerText")
                if date_text is None:
                    date_text = date_row.text
            except Exception as exc:
                if show_debug_message:
                    print("get date text Exception:", exc)
                continue

            if date_text:
                date_text = util.format_keyword_string(date_text)
                if show_debug_message:
                    print(f"date_text: {date_text}")

                # 關鍵字比對
                is_match_date = util.is_matched_by_keyword(date_text, date_keyword_array)
                if is_match_date:
                    matched_blocks.append(date_row)

        # 選擇目標日期
        if matched_blocks:
            target_date = util.get_target_item_from_matched_list(matched_blocks, config_dict["date_auto_select"]["mode"])
            if target_date:
                try:
                    driver.execute_script("arguments[0].click();", target_date)
                    is_date_assigned = True
                    if show_debug_message:
                        print("date auto select success")
                except Exception as exc:
                    if show_debug_message:
                        print("date click Exception:", exc)

    return is_date_assigned
```

### 🥈 **銀級 - NoDriver 日期選擇** (簡化版範本)

```python
async def nodriver_{platform}_date_auto_select(tab, config_dict):
    """
    自動選擇演出日期 (NoDriver 版本)
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    if show_debug_message:
        print(f"date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 查找日期元素
    date_list = None
    try:
        date_list = await tab.query_selector_all('div.date-item, .date-option, .performance-date')
    except Exception as exc:
        if show_debug_message:
            print("find date elements Exception:", exc)

    if date_list:
        date_keyword_array = date_keyword.split(' ')

        for date_row in date_list:
            date_text = ""
            try:
                date_text = await date_row.get_property("innerText")
                if not date_text:
                    date_text = await date_row.get_property("textContent")
            except Exception as exc:
                if show_debug_message:
                    print("get date text Exception:", exc)
                continue

            if date_text:
                date_text = util.format_keyword_string(date_text)
                if show_debug_message:
                    print(f"date_text: {date_text}")

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
                    if show_debug_message:
                        print("date auto select success")
                except Exception as exc:
                    if show_debug_message:
                        print("date click Exception:", exc)

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
- **OR 邏輯**：按陣列順序，找到第一個匹配就選擇
- **AND 邏輯**：空格分隔表示必須全部包含
- **空字串**：不使用關鍵字，改用自動選擇模式（random/從上到下/從下到上）

**注意事項**：
- 大小寫不敏感（自動處理）
- 引號為 JSON 格式必要
- 建議關鍵字越精確越好，避免誤選

#### 關鍵字解析規範
```python
# Chrome/Selenium 版本 (標準實作)
area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
area_keyword_array = []
try:
    area_keyword_array = json.loads("["+ area_keyword +"]")
except Exception as exc:
    area_keyword_array = []

# NoDriver 版本 (必須對齊標準)
area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
area_keyword_array = []
try:
    area_keyword_array = json.loads("["+ area_keyword +"]")
except Exception as exc:
    area_keyword_array = []
```

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_area_auto_select(driver, config_dict):
    """
    自動選擇座位區域
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    if show_debug_message:
        print(f"area_keyword: {area_keyword}")

    is_area_assigned = False
    matched_blocks = []

    # 查找區域元素
    area_list = None
    try:
        area_list = driver.find_elements(By.CSS_SELECTOR, 'div.area-item, .seat-area, .zone-option')
    except Exception as exc:
        if show_debug_message:
            print("find area elements Exception:", exc)

    if area_list:
        # 使用標準關鍵字解析
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []

        for area_keyword_item in area_keyword_array:
            for area_row in area_list:
                area_text = ""
                try:
                    area_text = area_row.get_attribute("innerText")
                    if area_text is None:
                        area_text = area_row.text
                except Exception as exc:
                    if show_debug_message:
                        print("get area text Exception:", exc)
                    continue

                if area_text:
                    area_text = util.format_keyword_string(area_text)
                    if show_debug_message:
                        print(f"area_text: {area_text}")

                    # 關鍵字比對 (支援 AND 邏輯)
                    area_keyword_array_and = area_keyword_item.split(' ')
                    is_match_area = util.is_matched_by_keyword(area_text, area_keyword_array_and)
                    if is_match_area:
                        matched_blocks.append(area_row)

            # 如果找到匹配項目就停止
            if matched_blocks:
                break

        # 選擇目標區域
        if matched_blocks:
            target_area = util.get_target_item_from_matched_list(matched_blocks, config_dict["area_auto_select"]["mode"])
            if target_area:
                try:
                    driver.execute_script("arguments[0].click();", target_area)
                    is_area_assigned = True
                    if show_debug_message:
                        print("area auto select success")
                except Exception as exc:
                    if show_debug_message:
                        print("area click Exception:", exc)

    return is_area_assigned
```

---

## 🎟️ **票券數量選擇範本**

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_assign_ticket_number(driver, config_dict):
    """
    自動分配票券數量
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    ticket_number = config_dict["ticket_number"]

    if show_debug_message:
        print(f"ticket_number: {ticket_number}")

    is_ticket_number_assigned = False

    # 查找票數輸入框或選擇器
    ticket_input = None
    try:
        # 嘗試多種選擇器
        selectors = [
            'input[name="ticket_number"]',
            'select[name="quantity"]',
            'input.ticket-count',
            '.quantity-selector input'
        ]

        for selector in selectors:
            try:
                ticket_input = driver.find_element(By.CSS_SELECTOR, selector)
                if ticket_input:
                    break
            except:
                continue

    except Exception as exc:
        if show_debug_message:
            print("find ticket input Exception:", exc)

    if ticket_input:
        try:
            # 清空並輸入票數
            ticket_input.clear()
            ticket_input.send_keys(str(ticket_number))
            is_ticket_number_assigned = True

            if show_debug_message:
                print("ticket number assigned success")

        except Exception as exc:
            if show_debug_message:
                print("assign ticket number Exception:", exc)

    return is_ticket_number_assigned
```

---

## ✅ **同意條款處理範本**

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_ticket_agree(driver, config_dict):
    """
    自動勾選同意條款
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print("checking agreement checkboxes")

    is_agree_success = False

    # 查找同意條款選項
    agree_checkboxes = None
    try:
        selectors = [
            'input[type="checkbox"]',
            'input#agree',
            '.agreement-checkbox input',
            'input[name*="agree"]'
        ]

        for selector in selectors:
            try:
                agree_checkboxes = driver.find_elements(By.CSS_SELECTOR, selector)
                if agree_checkboxes:
                    break
            except:
                continue

    except Exception as exc:
        if show_debug_message:
            print("find agreement checkboxes Exception:", exc)

    if agree_checkboxes:
        for checkbox in agree_checkboxes:
            try:
                # 檢查是否已勾選
                is_checked = checkbox.is_selected()
                if not is_checked:
                    # 使用 JavaScript 點擊確保成功
                    driver.execute_script("arguments[0].click();", checkbox)
                    is_agree_success = True

                    if show_debug_message:
                        print("agreement checkbox checked")

            except Exception as exc:
                if show_debug_message:
                    print("checkbox click Exception:", exc)

    return is_agree_success
```

### NoDriver 版本 【推薦使用】
```python
async def nodriver_{platform}_ticket_agree(tab, config_dict):
    """
    自動勾選同意條款 (NoDriver 版本)
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print("checking agreement checkboxes")

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

                            if show_debug_message:
                                print("agreement checkbox checked")

                    except Exception as exc:
                        if show_debug_message:
                            print("checkbox click Exception:", exc)
                break
        except Exception as exc:
            if show_debug_message:
                print(f"find checkboxes with {selector} Exception:", exc)

    return is_agree_success
```

---

## 🆔 **實名認證處理範本**

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_real_name_verify(driver, config_dict):
    """
    自動填寫實名認證資料
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    real_name = config_dict["advanced"]["{platform}_real_name"].strip()
    id_number = config_dict["advanced"]["{platform}_id_number"].strip()

    if show_debug_message:
        print(f"real_name: {real_name}")
        print(f"id_number: {id_number[:3]}***")  # 隱藏部分身分證號

    is_real_name_filled = False

    if len(real_name) > 0 and len(id_number) > 0:
        try:
            # 查找姓名欄位
            name_input = None
            name_selectors = [
                'input[name="real_name"]',
                'input[name="name"]',
                'input.real-name',
                'input#real_name'
            ]

            for selector in name_selectors:
                try:
                    name_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if name_input:
                        break
                except:
                    continue

            # 查找身分證號欄位
            id_input = None
            id_selectors = [
                'input[name="id_number"]',
                'input[name="identity"]',
                'input.id-number',
                'input#id_number'
            ]

            for selector in id_selectors:
                try:
                    id_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if id_input:
                        break
                except:
                    continue

            # 填寫資料
            if name_input:
                name_input.clear()
                name_input.send_keys(real_name)

            if id_input:
                id_input.clear()
                id_input.send_keys(id_number)

            if name_input and id_input:
                is_real_name_filled = True

                if show_debug_message:
                    print("real name verification filled")

        except Exception as exc:
            if show_debug_message:
                print("real name verification Exception:", exc)

    return is_real_name_filled
```

### NoDriver 版本 【推薦使用】
```python
async def nodriver_{platform}_real_name_verify(tab, config_dict):
    """
    自動填寫實名認證資料 (NoDriver 版本)
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    real_name = config_dict["advanced"]["{platform}_real_name"].strip()
    id_number = config_dict["advanced"]["{platform}_id_number"].strip()

    if show_debug_message:
        print(f"real_name: {real_name}")
        print(f"id_number: {id_number[:3]}***")

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

                if show_debug_message:
                    print("real name verification filled")

        except Exception as exc:
            if show_debug_message:
                print("real name verification Exception:", exc)

    return is_real_name_filled
```

---

## 🔐 **登入處理範本**

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_login(driver, config_dict):
    """
    平台登入處理
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    account = config_dict["advanced"]["{platform}_account"]
    password = config_dict["advanced"]["{platform}_password_plaintext"].strip()

    if password == "":
        password = util.decryptMe(config_dict["advanced"]["{platform}_password"])

    if show_debug_message:
        print(f"account: {account}")

    is_login_success = False

    if len(account) > 0 and len(password) > 0:
        try:
            # 查找登入表單
            account_input = driver.find_element(By.CSS_SELECTOR, 'input[name="email"], input[name="account"], input[type="email"]')
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"], input[type="password"]')

            if account_input and password_input:
                account_input.clear()
                account_input.send_keys(account)

                password_input.clear()
                password_input.send_keys(password)

                # 查找登入按鈕
                login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], .btn-login')
                if login_button:
                    driver.execute_script("arguments[0].click();", login_button)
                    is_login_success = True

                    if show_debug_message:
                        print("login form submitted")

        except Exception as exc:
            if show_debug_message:
                print("login Exception:", exc)

    return is_login_success
```

---

## 🎨 **OCR 驗證碼處理範本**

### Chrome/Selenium 版本 【必須遵循】
```python
def {platform}_auto_ocr(driver, config_dict, ocr, Captcha_Browser, ocr_captcha_image_source):
    """
    自動 OCR 驗證碼處理
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    force_submit = config_dict["ocr_captcha"]["force_submit"]

    if show_debug_message:
        print("starting OCR captcha processing")

    is_captcha_solved = False

    # 查找驗證碼輸入框
    captcha_input = None
    try:
        captcha_input = driver.find_element(By.CSS_SELECTOR, 'input[name="captcha"], input.captcha-input, #verifyCode')
    except Exception as exc:
        if show_debug_message:
            print("find captcha input Exception:", exc)

    if captcha_input and ocr:
        # 獲取 OCR 答案
        ocr_answer = {platform}_get_ocr_answer(driver, ocr, ocr_captcha_image_source, Captcha_Browser)

        if ocr_answer and len(ocr_answer.strip()) > 0:
            ocr_answer = ocr_answer.strip()

            if show_debug_message:
                print(f"ocr_answer: {ocr_answer}")

            # 驗證答案長度 (依平台調整)
            if len(ocr_answer) == 4:  # 或其他平台特定長度
                try:
                    captcha_input.clear()
                    captcha_input.send_keys(ocr_answer)

                    if force_submit:
                        # 自動提交
                        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                        if submit_button:
                            driver.execute_script("arguments[0].click();", submit_button)

                    is_captcha_solved = True

                    if show_debug_message:
                        print("captcha OCR success")

                except Exception as exc:
                    if show_debug_message:
                        print("captcha input Exception:", exc)

    return is_captcha_solved
```

---

## 📝 **錯誤處理與重試機制**

### 標準錯誤處理
```python
def {platform}_function_with_retry(driver, config_dict, max_retry=3):
    """
    帶重試機制的函數範本
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    for retry_count in range(max_retry):
        try:
            if retry_count > 0:
                if show_debug_message:
                    print(f"retry attempt {retry_count}/{max_retry-1}")
                time.sleep(1)  # 重試間隔

            # 主要邏輯
            result = perform_main_logic()

            if result:
                if show_debug_message:
                    print(f"operation success on attempt {retry_count + 1}")
                return True

        except Exception as exc:
            if show_debug_message:
                print(f"attempt {retry_count + 1} failed:", exc)

            if retry_count == max_retry - 1:
                print("all retry attempts failed")

    return False
```

---

## 🛑 **暫停機制標準範本** (NoDriver 專用)

> 統一的暫停檢查機制，確保使用者可隨時中斷執行

### 核心暫停檢查函數

#### `check_and_handle_pause(config_dict)`
主要暫停檢查函數，所有平台函數都應使用此統一入口。

**位置**：`src/nodriver_tixcraft.py:5301-5308`

**行為說明**：
- 檢查暫停檔案 `MAXBOT_INT28_IDLE.txt` 是否存在
- 根據 `config_dict["advanced"]["verbose"]` 控制訊息顯示
- `verbose = true` → 顯示 "BOT Paused."
- `verbose = false` → 不顯示訊息

**使用場景**：
1. 函數開始時檢查
2. 長時間迴圈中定期檢查
3. 關鍵操作前檢查

**範本**：
```python
async def nodriver_platform_function(tab, config_dict):
    """平台功能函數範本"""
    show_debug_message = config_dict["advanced"]["verbose"]

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

### 暫停輔助函數

#### 1. `sleep_with_pause_check(tab, seconds, config_dict)`
取代 `tab.sleep()`，在等待期間檢查暫停狀態。

**位置**：`src/nodriver_tixcraft.py:5318-5323`

**使用時機**：需要延遲等待的 NoDriver 函數

**範本**：
```python
# 一般等待（無暫停檢查）
await tab.sleep(0.6)

# 改為：支援暫停的等待
if await sleep_with_pause_check(tab, 0.6, config_dict):
    if show_debug_message:
        print("Operation paused during wait")
    return False  # 暫停中，提前返回
```

#### 2. `asyncio_sleep_with_pause_check(seconds, config_dict)`
取代 `asyncio.sleep()`，在等待期間檢查暫停狀態。

**位置**：`src/nodriver_tixcraft.py:5325-5331`

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

**位置**：`src/nodriver_tixcraft.py:5333-5343`

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

**位置**：`src/nodriver_tixcraft.py:5345-5367`

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
    show_debug_message = config_dict["advanced"]["verbose"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    # 1. 函數開始時檢查
    if await check_and_handle_pause(config_dict):
        return False

    if show_debug_message:
        print(f"[NoDriver] date_keyword: {date_keyword}")

    is_date_assigned = False
    matched_blocks = []

    # 2. 等待頁面載入（支援暫停）
    if await sleep_with_pause_check(tab, 0.6, config_dict):
        if show_debug_message:
            print("[NoDriver] Paused during page load")
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
        if show_debug_message:
            print(f"[NoDriver] find date elements Exception: {exc}")

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
            if show_debug_message:
                print(f"[NoDriver] get date text Exception: {exc}")
            continue

    # 6. 選擇並點擊日期
    if matched_blocks:
        target_date = matched_blocks[0]
        try:
            await target_date.click()
            is_date_assigned = True

            if show_debug_message:
                print("[NoDriver] date auto select success")
        except Exception as exc:
            if show_debug_message:
                print(f"[NoDriver] date click Exception: {exc}")

    return is_date_assigned
```

---

### 重要規則與最佳實踐

#### 1. **統一使用 `check_and_handle_pause()`**
- ✅ 正確：使用統一函數
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

#### 3. **僅在 NoDriver 版本實作**
- Chrome Driver 版本不支援暫停機制
- 保持兩個版本的功能差異性
- NoDriver 版本的優勢之一

#### 4. **暫停後的處理**
- 檢測到暫停後應該 `return` 而非 `break`
- 返回值應該表示操作未完成（通常是 `False`）
- 確保函數狀態一致性

#### 5. **檢查時機建議**
- **必須**：函數開始時檢查
- **建議**：長時間操作前檢查（如 JavaScript 執行）
- **必須**：長時間迴圈內每次迭代檢查
- **建議**：延遲等待時使用暫停版本（`sleep_with_pause_check`）

---

### 檢查清單

開發 NoDriver 函數時，確保：
- [ ] 函數開始時呼叫 `check_and_handle_pause()`
- [ ] 所有 `tab.sleep()` 改用 `sleep_with_pause_check()`
- [ ] 所有 `asyncio.sleep()` 改用 `asyncio_sleep_with_pause_check()`
- [ ] 長時間迴圈內加入暫停檢查
- [ ] 暫停後返回適當的失敗值（通常是 `False`）
- [ ] 不要直接檢查 `CONST_MAXBOT_INT28_FILE`
- [ ] 確保與 Chrome Driver 版本的功能區隔

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
- 流程狀態管理 (`{platform}_dict`)
- 時間追蹤 (`start_time`, `done_time`, `elapsed_time`)
- 音效提醒控制 (`played_sound_ticket`, `played_sound_order`)

#### 2. 日期時段選擇模組 (Date Selection)
```python
# 功能: 自動選擇演出日期與時段
{platform}_date_auto_select(driver, url, config_dict, domain_name)
```
**核心邏輯**:
- **關鍵字匹配**: JSON 陣列格式支援 AND/OR 邏輯
- **售罄檢測**: 過濾 "選購一空"、"已售完"、"Sold out" 等狀態
- **即將開賣**: 檢測 "開賣倒數" 並自動重載頁面
- **多語言支援**: 繁中、英文、日文界面適配
- **選擇模式**: from top to bottom, center, random

#### 3. 座位區域選擇模組 (Area Selection)
```python
# 功能: 根據關鍵字自動選擇座位區域
{platform}_area_auto_select(driver, url, config_dict)
```
**智慧選擇邏輯**:
- **剩餘座位檢查**: 避免選擇座位不足的區域 (檢查字體標註的剩餘數量)
- **關鍵字過濾**: 支援多關鍵字 AND 邏輯匹配
- **排除關鍵字**: 避開不想選擇的區域
- **優先級排序**: 依選擇模式決定優先順序

#### 4. 票數分配模組 (Ticket Quantity)
```python
# 功能: 自動設定票券數量
{platform}_assign_ticket_number(driver, config_dict)
```
**適應性選擇器**:
- **多選擇器支援**: `.mobile-select`, `select.form-select`, `input[type="text"]`
- **區域綁定**: 根據選中區域自動定位對應票數選擇器
- **數量驗證**: 檢查當前值避免重複設定
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
- **Cloudflare 處理**: 針對 NoDriver 版本

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
- **搶票成功**: 檢測到 `/checkout` 頁面
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
- [x] **多語言支援**: 繁中/英文/日文界面適配
- [x] **效能優化**: DOM 查找快取與最小化等待
- [x] **音效提醒**: 搶票成功與失敗音效
- [x] **除錯模式**: 完整的 debug 輸出系統
- [x] **擴充套件整合**: Chrome Extension 協作模式

### 平台特殊功能
- [x] **TixCraft**: 區域多選擇器、即將開賣重載、驗證碼 Toast 提示
- [x] **KKTIX**: 實名制表單、Cloudflare 驗證、危險庫存檢查
- [ ] **TicketMaster**: 區域 JavaScript 選擇、座位地圖、Promo Code
- [ ] **iBon**: 鄰座限制、實名制欄位、特殊驗證碼格式

### 程式碼品質標準

#### 編碼規範檢查
- [x] **命名一致性**: `platform_function_name` 格式
- [x] **Debug 標準**: `show_debug_message = config_dict["advanced"]["verbose"]`
- [x] **異常處理**: 所有 DOM 操作包覆 try-catch
- [x] **狀態追蹤**: `{platform}_dict` 全域變數管理
- [x] **註解完整**: 函數用途、參數說明、回傳值說明

#### 效能與可靠性
- [x] **選擇器優化**: 使用高效能 CSS 選擇器
- [x] **等待機制**: 適當的 sleep 與 WebDriverWait
- [x] **重試邏輯**: 關鍵操作最多重試 3-19 次
- [x] **記憶體管理**: 及時釋放大型物件
- [x] **相容性**: 支援多瀏覽器與多作業系統

---

## 🛡️ **Cloudflare 驗證處理**

### NoDriver Cloudflare 處理
**官方文件**: https://ultrafunkamsterdam.github.io/nodriver/

```python
async def handle_cloudflare_verification(tab, config_dict):
    """
    處理 Cloudflare 驗證挑戰
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    try:
        # 使用 nodriver 內建方法
        await tab.verify_cf()
        if show_debug_message:
            print("Cloudflare 驗證處理完成")
    except AttributeError:
        # 如果方法不存在，使用手動檢測
        try:
            current_url = tab.url
            page_content = await tab.get_content()

            if ("cloudflare" in current_url.lower() or
                "cf-challenge" in current_url.lower() or
                "Checking your browser" in page_content):

                if show_debug_message:
                    print("偵測到 Cloudflare 驗證頁面，等待驗證完成...")

                # 等待驗證完成
                await tab.wait_for(cdp.page.load_event_fired)
                time.sleep(5)

        except Exception as manual_cf_e:
            if show_debug_message:
                print(f"Manual Cloudflare verification check: {manual_cf_e}")
    except Exception as cf_e:
        if show_debug_message:
            print(f"Cloudflare verification error: {cf_e}")
```

### 登入後 Cloudflare 處理範本
```python
async def nodriver_{platform}_login(tab, config_dict):
    """
    登入後處理 Cloudflare 驗證
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 執行登入操作
    await submit_login_form(tab, config_dict)

    # 等待頁面響應，可能出現 Cloudflare 驗證
    time.sleep(3)

    # 處理 Cloudflare 驗證
    await handle_cloudflare_verification(tab, config_dict)
```

**注意事項**:
- 需安裝 `opencv-python` 套件
- 目前僅支援英文界面驗證
- 建議在登入、頁面跳轉後調用

---

## 🎫 **TicketPlus 平台特殊實作**

### 區域選擇特殊模式
TicketPlus 使用展開式面板選擇，與其他平台不同：

```python
# Chrome/Selenium 版本
def ticketplus_order_expansion_panel(driver, config_dict, current_layout_style):
    """展開式面板處理"""
    # 支援三種佈局樣式
    # style_1: 舊版展開式
    # style_2: 新版簡單式
    # style_3: Vue.js 佈局

def ticketplus_order_expansion_auto_select(driver, config_dict, area_keyword_item, current_layout_style):
    """自動選擇區域（展開式面板模式）"""
    # 取代標準的 ticketplus_area_auto_select()

# NoDriver 版本
async def nodriver_ticketplus_select_ticket_simplified(tab, config_dict, area_keyword):
    """簡化的票種選擇（統一處理三種佈局）"""
```

### 登入處理
```python
# Chrome 版本
def ticketplus_account_auto_fill(driver, config_dict):
    """自動填寫帳密並登入"""

def ticketplus_account_sign_in(driver, config_dict):
    """執行登入動作"""

# 實際使用時整合為 ticketplus_login() 概念
```

### 彈窗處理機制
```python
# 實名制彈窗
def ticketplus_accept_realname_card(driver):
    """處理實名制確認彈窗"""

# 其他活動彈窗
def ticketplus_accept_other_activity(driver):
    """處理其他活動推薦彈窗"""

# 訂單失敗彈窗
def ticketplus_accept_order_fail(driver):
    """處理訂單失敗情況"""
```

### 特殊函數映射
由於 TicketPlus 的特殊實作方式，函數映射如下：

| 標準函數 | TicketPlus 實作 | 說明 |
|---------|----------------|------|
| `ticketplus_area_auto_select()` | `ticketplus_order_expansion_panel()` | 使用展開式面板 |
| `ticketplus_login()` | `ticketplus_account_auto_fill()` | 整合登入流程 |
| `ticketplus_real_name_verify()` | `ticketplus_accept_realname_card()` | 彈窗處理方式 |
| `ticketplus_get_ocr_answer()` | `ticketplus_order_ocr()` | OCR 處理整合 |

---

## 🔍 **除錯技巧**

### Debug 輸出標準格式
```python
if show_debug_message:
    print(f"function_name: variable_name = {variable_value}")
    print(f"DOM elements found: {len(element_list)}")
    print(f"operation result: {is_success}")
```

### 常用除錯代碼
```python
# DOM 元素檢查
if show_debug_message:
    print(f"element exists: {element is not None}")
    print(f"element text: {element.text if element else 'None'}")

# 狀態追蹤
if show_debug_message:
    print(f"current URL: {driver.current_url}")
    print(f"page title: {driver.title}")
```

---

## 🚀 **完整平台實作範例**

### 基於實際 TixCraft/KKTIX 分析的標準模版

```python
# Chrome/Selenium 版本完整實作範例
def example_platform_main(driver, url, config_dict, ocr, Captcha_Browser):
    """
    標準搶票平台主程式範本
    整合所有 8 個核心功能模組
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 全域狀態管理
    global example_platform_dict
    if not 'example_platform_dict' in globals():
        example_platform_dict = {}
        example_platform_dict["fail_list"] = []  # OCR 失敗答案記錄
        example_platform_dict["start_time"] = None  # 搶票開始時間
        example_platform_dict["done_time"] = None   # 搶票完成時間
        example_platform_dict["elapsed_time"] = None # 總耗時
        example_platform_dict["played_sound_ticket"] = False  # 音效狀態
        example_platform_dict["played_sound_order"] = False
        example_platform_dict["retry_count"] = 0  # 重試計數器

    # URL 路由分發
    domain_name = url.split('/')[2]

    # 1. 登入流程
    if '/login' in url or '/sign_in' in url:
        if config_dict["advanced"]["example_platform_account"]:
            is_login_success = example_platform_login(driver, config_dict)
            if show_debug_message:
                print(f"login result: {is_login_success}")

    # 2. 主要購票流程
    elif '/event' in url or '/activity' in url:
        example_platform_dict["start_time"] = time.time()

        # 日期選擇
        if config_dict["date_auto_select"]["enable"]:
            is_date_selected = example_platform_date_auto_select(driver, url, config_dict, domain_name)
            if show_debug_message:
                print(f"date selection result: {is_date_selected}")

    elif '/ticket/area' in url or '/seats' in url:
        # 座位區域選擇
        if config_dict["area_auto_select"]["enable"]:
            example_platform_area_auto_select(driver, url, config_dict)
            example_platform_dict["retry_count"] += 1

            # 冷卻機制
            if example_platform_dict["retry_count"] >= (60 * 15):
                example_platform_dict["retry_count"] = 0
                time.sleep(5)

    elif '/ticket/ticket' in url or '/booking' in url:
        # 票數分配與驗證碼處理
        example_platform_dict["done_time"] = time.time()

        # 同意條款
        is_agree_at_webdriver = not (
            config_dict["browser"] in ["chrome", "edge", "brave"] and
            config_dict["advanced"]["chrome_extension"]
        )
        if is_agree_at_webdriver:
            example_platform_ticket_main_agree(driver, config_dict)

        # 票數分配
        is_ticket_assigned = example_platform_assign_ticket_number(driver, config_dict)

        # OCR 驗證碼
        if is_ticket_assigned and config_dict["ocr_captcha"]["enable"]:
            example_platform_auto_ocr(driver, config_dict, ocr, Captcha_Browser, domain_name)

        # 音效提醒
        if config_dict["advanced"]["play_sound"]["ticket"]:
            if not example_platform_dict["played_sound_ticket"]:
                play_sound_while_ordering(config_dict)
            example_platform_dict["played_sound_ticket"] = True

    # 3. 成功檢測
    elif '/checkout' in url or '/confirm' in url:
        # 計算搶票效能
        if example_platform_dict["start_time"] and example_platform_dict["done_time"]:
            bot_elapsed_time = example_platform_dict["done_time"] - example_platform_dict["start_time"]
            if example_platform_dict["elapsed_time"] != bot_elapsed_time:
                print("bot elapsed time:", "{:.3f}".format(bot_elapsed_time))
            example_platform_dict["elapsed_time"] = bot_elapsed_time

        # 成功音效
        if config_dict["advanced"]["play_sound"]["order"]:
            if not example_platform_dict["played_sound_order"]:
                play_sound_while_ordering(config_dict)
            example_platform_dict["played_sound_order"] = True

        # 成功提醒
        checkout_url = f"https://{domain_name}/checkout"
        print(f"搶票成功, 請前往該帳號訂單查看: {checkout_url}")

        if not config_dict["advanced"]["headless"]:
            import webbrowser
            webbrowser.open_new(checkout_url)

    # 4. 錯誤處理
    else:
        # 重置狀態
        example_platform_dict["fail_list"] = []
        example_platform_dict["played_sound_ticket"] = False
        example_platform_dict["retry_count"] = 0

# NoDriver 版本範例 (簡化版)
async def nodriver_example_platform_main(tab, url, config_dict, ocr, Captcha_Browser):
    """
    NoDriver 版本標準範本
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 相同的全域狀態管理結構
    global example_platform_dict
    # ... 相同的初始化邏輯 ...

    # URL 路由 (使用 await)
    if '/login' in url:
        if config_dict["advanced"]["example_platform_account"]:
            await nodriver_example_platform_login(tab, config_dict)

    elif '/event' in url:
        if config_dict["date_auto_select"]["enable"]:
            await nodriver_example_platform_date_auto_select(tab, url, config_dict, domain_name)

    elif '/ticket/area' in url:
        if config_dict["area_auto_select"]["enable"]:
            await nodriver_example_platform_area_auto_select(tab, url, config_dict)

    elif '/ticket/ticket' in url:
        await nodriver_example_platform_ticket_main(tab, config_dict, ocr, Captcha_Browser, domain_name)

    # ... 其他流程相同 ...
```

### 🔧 **關鍵設計模式**

#### 1. **狀態管理模式**
```python
# 全域字典管理所有狀態
{platform}_dict = {
    "fail_list": [],           # 失敗記錄
    "start_time": None,        # 計時系統
    "done_time": None,
    "elapsed_time": None,
    "played_sound_ticket": False,  # 音效控制
    "played_sound_order": False,
    "retry_count": 0,          # 重試計數
}
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
for retry_count in range(max_retry):
    try:
        result = perform_operation()
        if result:
            break
    except Exception as exc:
        if show_debug_message:
            print(f"attempt {retry_count + 1} failed:", exc)
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
- [ ] **8個核心函數完整實作**
  - [ ] `{platform}_main()` - 主流程控制
  - [ ] `{platform}_date_auto_select()` - 日期選擇
  - [ ] `{platform}_area_auto_select()` - 區域選擇
  - [ ] `{platform}_assign_ticket_number()` - 票數分配
  - [ ] `{platform}_auto_ocr()` - OCR處理
  - [ ] `{platform}_login()` - 登入處理
  - [ ] `{platform}_ticket_agree()` - 同意條款
  - [ ] `{platform}_check_status()` - 狀態監控

- [ ] **代碼品質標準**
  - [ ] 無 TODO 標記
  - [ ] 完整異常處理
  - [ ] 統一 debug 輸出格式
  - [ ] 完整函數註解

- [ ] **功能驗證標準**
  - [ ] 實戰測試通過
  - [ ] 支援多語言界面
  - [ ] 智慧重試機制
  - [ ] 效能追蹤機制

#### 🥇 **金級認證標準** (80-95%)
- [ ] **6個主要函數實作**
  - [ ] 核心購票流程完整
  - [ ] 基本錯誤處理機制
  - [ ] 平台特殊功能支援

- [ ] **代碼品質標準**
  - [ ] 少量 TODO (≤3個)
  - [ ] 基本異常處理
  - [ ] debug 輸出規範

#### 🥈 **銀級認證標準** (60-80%)
- [ ] **基本架構完整**
  - [ ] 主要流程可運行
  - [ ] 基本功能實作

- [ ] **需要改善項目**
  - [ ] TODO 標記較多 (4-10個)
  - [ ] 部分功能未完成
  - [ ] 錯誤處理需強化

### 🚨 **開發檢查清單**

#### **開始新平台開發前**
- [ ] 選擇參考範本 (建議白金級 Chrome TixCraft)
- [ ] 確認平台特殊需求
- [ ] 建立測試環境
- [ ] 閱讀平台技術文件

#### **開發過程中**
- [ ] 遵循標準函數命名
- [ ] 實作標準 debug 輸出
- [ ] 每個函數加入異常處理
- [ ] 定期執行實戰測試

#### **完成開發後**
- [ ] 使用完整度檢查表評分
- [ ] 清理所有 TODO 標記
- [ ] 更新 platforms.md 函數對照
- [ ] 執行完整功能測試

### 📊 **目前平台完成度總覽** (2025.10 更新)

| 平台 | NoDriver版本 ⭐ | Chrome版本 | 推薦引擎 | 狀態 |
|------|:-------------:|:----------:|:--------:|:----:|
| **TixCraft** | 🏅 白金級 (92%) | 🥈 銀級 (95%) | **NoDriver** | ✅ 生產可用 |
| **KKTIX** | 🏅 白金級 (90%) | 🥈 銀級 (90%) | **NoDriver** | ✅ 生產可用 |
| **TicketPlus** | 🏅 白金級 (95%) | 🥈 銀級 (98%) | **NoDriver** | ✅ 生產可用 |
| **iBon** | 🥇 金級 (80%) | 🥈 銀級 (75%) | **NoDriver** | ✅ 可用 |
| **Cityline** | 🥈 銀級 (60%) | 🥈 銀級 (72%) | Chrome | 🔄 開發中 |
| **TicketMaster** | 🥈 銀級 (55%) | 🥈 銀級 (78%) | Chrome | 🔄 開發中 |
| **年代售票** | 🚧 規劃中 (0%) | 🥈 銀級 (70%) | Chrome | 📋 待移植 |
| **寬宏售票** | 🚧 規劃中 (0%) | 🥈 銀級 (68%) | Chrome | 📋 待移植 |

**圖例說明**：
- ⭐ NoDriver: 推薦使用（反偵測、高效能）
- Chrome: 傳統方案（過渡期、測試用）
- ✅ 生產可用: 實測穩定，可用於正式環境
- ✅ 可用: 基本功能完整，建議追蹤更新
- 🔄 開發中: 持續改進中
- 📋 待移植: 規劃從 Chrome 移植至 NoDriver

---

### ⭐ **2025 開發建議 (NoDriver First)**

#### **優先採用策略**

**新專案開發** (強烈推薦 NoDriver):
1. **首選平台**: NoDriver TixCraft / KKTIX / TicketPlus
2. **理由**:
   - ✅ 反偵測能力強，不易被封鎖
   - ✅ 記憶體效率高，可多開瀏覽器
   - ✅ 非同步架構，效能優異
   - ✅ 實戰驗證，穩定可靠
3. **學習路徑**: async/await → NoDriver API → 平台業務邏輯

**維護舊專案** (逐步遷移):
1. **短期**: 保持 Chrome/Selenium 運作
2. **中期**: 逐步改寫為 NoDriver
3. **長期**: 完全移除 UC，統一 NoDriver

**特殊需求場景**:
1. **快速測試除錯**: 使用 Chrome/Selenium (API 豐富)
2. **需要相容舊環境**: 使用 Chrome/Selenium
3. **生產環境搶票**: 優先使用 NoDriver

---

### 🚀 **NoDriver 開發優勢**

#### 技術優勢
- ✅ **反偵測**: 通過 Cloudflare、reCAPTCHA 等防護
- ✅ **效能**: 比 UC 節省 60% 記憶體
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
| 正式搶票 | NoDriver TixCraft/KKTIX/TicketPlus | 反偵測 + 高成功率 |
| 開發測試 | Chrome TixCraft | 除錯容易 + API 豐富 |
| 學習研究 | NoDriver TixCraft | 架構完整 + 文件齊全 |
| 快速原型 | Chrome 任意平台 | 開發速度快 |
| 平台移植 | 參考 NoDriver 三大平台 | 設計模式一致 |

---

此分級系統確保開發者能夠：
- ✅ 選擇最適合的技術方案
- ✅ 遵循 NoDriver First 策略
- ✅ 建立一致的代碼品質標準
- ✅ 提升整體系統可維護性
---

**最後更新**: 2025-10-28
