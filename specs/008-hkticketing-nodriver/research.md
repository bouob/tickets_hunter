# 研究報告：HKTicketing NoDriver 遷移

**功能**：008-hkticketing-nodriver
**日期**：2025-11-27
**狀態**：完成

## 研究摘要

本研究分析了將 HKTicketing 從 Chrome UC Driver 遷移到 NoDriver 所需的 API 對應關係、共用函數相容性和最佳實踐模式。

---

## 1. API 對應關係

### 1.1 元素操作對應表

| 功能 | Selenium/UC | NoDriver | 備註 |
|------|-------------|----------|------|
| 元素查詢（單個）| `driver.find_element(By.CSS_SELECTOR, sel)` | `await tab.query_selector(sel)` | - |
| 元素查詢（多個）| `driver.find_elements(By.CSS_SELECTOR, sel)` | `await tab.query_selector_all(sel)` | - |
| 點擊 | `element.click()` | `await element.click()` | - |
| 輸入 | `element.send_keys(text)` | `await element.send_keys(text)` | - |
| 獲取 HTML | `element.get_attribute('innerHTML')` | `await element.get_html()` | **重要差異** |
| 獲取屬性 | `element.get_attribute('class')` | `await tab.evaluate(...)` | 需用 JS |
| 執行 JavaScript | `driver.execute_script(js, el)` | `await tab.evaluate(js)` | - |
| 頁面導航 | `driver.get(url)` | `await tab.get(url)` | - |
| 獲取頁面源碼 | `driver.page_source` | `await tab.get_content()` | - |
| 重載頁面 | `driver.refresh()` | `await tab.reload()` | - |
| 捲動到元素 | `ActionChains.move_to_element()` | `await element.scroll_into_view()` | - |

### 1.2 Select 下拉選單處理

**決策**：使用 JavaScript evaluate() 處理 SELECT 元素

**理由**：
- NoDriver 沒有 Selenium 的 `Select` 類別
- JavaScript 方案簡潔且通用
- 現有 Cityline、ibon 實作已採用此模式

**考慮的替代方案**：
- CDP 原生方法：過於複雜，不適合簡單 SELECT
- 模擬點擊展開選單：不穩定，依賴 UI 渲染

**實作模式**：
```python
async def select_option_by_value(tab, selector, value):
    return await tab.evaluate(f'''
        (function() {{
            const select = document.querySelector('{selector}');
            if (!select) return false;
            for (let i = 0; i < select.options.length; i++) {{
                if (select.options[i].value == "{value}") {{
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
        }})();
    ''')
```

### 1.3 ActionChains 替代方案

**決策**：使用 `element.scroll_into_view()` + `element.click()`

**理由**：
- NoDriver 元素原生支援這兩個方法
- 比 ActionChains 更簡潔
- 現有 Cityline 實作已驗證此模式

**實作模式**：
```python
# 原 UC 版本
builder = ActionChains(driver)
builder.move_to_element(el_nav)
builder.click(el_btn)
builder.perform()

# NoDriver 版本
await el_nav.scroll_into_view()
await el_btn.click()
```

---

## 2. util.py 共用函數相容性

### 2.1 相容性分析

| 函數 | 相容性 | 調整需求 |
|------|--------|----------|
| `get_matched_blocks_by_keyword()` | 部分相容 | 需在調用前提取文字 |
| `get_target_item_from_matched_list()` | 完全相容 | 無需調整 |
| `is_row_match_keyword()` | 完全相容 | 無需調整 |
| `reset_row_text_if_match_keyword_exclude()` | 完全相容 | 無需調整 |
| `format_keyword_string()` | 完全相容 | 無需調整 |
| `remove_html_tags()` | 完全相容 | 無需調整 |

### 2.2 get_matched_blocks_by_keyword 適配方案

**決策**：在 NoDriver 函數內部處理元素文字提取，然後調用 util 純字串函數

**理由**：
- 避免修改共用函數影響其他平台
- 保持關鍵字匹配邏輯一致性
- 遵循現有 Cityline 實作模式

**實作模式**：
```python
async def nodriver_hkticketing_match_by_keyword(elements, config_dict, keyword):
    """在 NoDriver 層處理元素，利用 util 函數做字串匹配"""
    matched = []
    for elem in elements:
        # NoDriver 特有：異步獲取 HTML
        elem_html = await elem.get_html()
        elem_text = util.remove_html_tags(elem_html)

        # 排除關鍵字檢查（使用原 util 函數）
        if util.reset_row_text_if_match_keyword_exclude(config_dict, elem_text):
            continue

        # 關鍵字匹配（利用原 util 函數）
        elem_text = util.format_keyword_string(elem_text)
        if util.is_row_match_keyword(keyword, elem_text):
            matched.append(elem)

    return matched
```

### 2.3 assign_ticket_number_by_select 替代方案

**決策**：為 HKTicketing 建立專用 NoDriver 版本函數

**理由**：
- HKTicketing 使用 `select.shortSelect` 選擇器
- 邏輯簡單，直接使用 JavaScript evaluate

**實作模式**：
```python
async def nodriver_hkticketing_ticket_number_auto_select(tab, config_dict):
    ticket_number = config_dict["ticket_number"]
    selector = "select.shortSelect"

    return await tab.evaluate(f'''
        (function() {{
            const select = document.querySelector('{selector}');
            if (!select) return false;
            for (let i = 0; i < select.options.length; i++) {{
                if (select.options[i].value == "{ticket_number}") {{
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
        }})();
    ''')
```

---

## 3. iframe 處理

### 3.1 原 UC 版本分析

HKTicketing 的 `hkticketing_travel_iframe` 使用：
- `driver.find_elements(By.TAG_NAME, "iframe")` 查找 iframe
- `driver.switch_to.frame(iframe)` 切換到 iframe
- `driver.switch_to.default_content()` 返回主框架

### 3.2 NoDriver 替代方案

**決策**：使用 JavaScript 在主框架中遍歷 iframe 內容

**理由**：
- NoDriver 沒有 `switch_to.frame()` 方法
- JavaScript 可以直接訪問 iframe 的 `contentDocument`（同源時）
- 跨域 iframe 無法訪問，但錯誤檢測邏輯可跳過

**實作模式**：
```python
async def nodriver_hkticketing_travel_iframe(tab, config_dict):
    """遍歷 iframe 內容進行錯誤檢測"""
    is_redirected = False

    # 使用 JavaScript 遍歷 iframe
    iframe_count = await tab.evaluate('''
        document.querySelectorAll('iframe').length
    ''')

    for idx in range(iframe_count):
        try:
            # 嘗試獲取 iframe 內容
            iframe_content = await tab.evaluate(f'''
                (function() {{
                    try {{
                        const iframe = document.querySelectorAll('iframe')[{idx}];
                        if (iframe && iframe.contentDocument) {{
                            return iframe.contentDocument.body.innerHTML;
                        }}
                    }} catch(e) {{
                        // 跨域 iframe 無法訪問
                    }}
                    return null;
                }})();
            ''')

            if iframe_content:
                # 檢查錯誤訊息
                for error_string in content_retry_string_list:
                    if error_string in iframe_content:
                        # 觸發重定向
                        await tab.get(new_url)
                        is_redirected = True
                        break
        except:
            pass

        if is_redirected:
            break

    return is_redirected
```

---

## 4. 狀態管理

### 4.1 hkticketing_dict 結構

**決策**：保持原有 `global hkticketing_dict` 結構

**結構定義**：
```python
hkticketing_dict = {
    "is_date_submiting": False,     # 是否正在提交日期
    "fail_list": [],                # 密碼嘗試失敗清單
    "played_sound_ticket": False,   # 是否已播放票券音效
    "played_sound_order": False     # 是否已播放訂單音效
}
```

**初始化位置**：在 `nodriver_hkticketing_main` 開頭

---

## 5. 錯誤處理模式

### 5.1 標準錯誤處理模板

```python
async def nodriver_hkticketing_example(tab, config_dict):
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        element = await tab.query_selector("selector")
        if element:
            await element.click()
            return True
    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] Operation failed: {exc}")

    return False
```

### 5.2 元素可見性檢查

**決策**：使用 `try/except` 包裝操作，而非顯式檢查 `is_enabled()`/`is_displayed()`

**理由**：
- NoDriver 元素沒有 Selenium 的 `is_enabled()`/`is_displayed()` 方法
- 直接嘗試操作並捕獲異常更簡潔

---

## 6. 建議實作順序

### 6.1 優先級排序

1. **P1 核心函數（第一批）**
   - `nodriver_hkticketing_main` - 主流程控制
   - `nodriver_hkticketing_date_assign` - 日期選擇核心
   - `nodriver_hkticketing_date_auto_select` - 日期自動選擇
   - `nodriver_hkticketing_area_auto_select` - 區域選擇
   - `nodriver_hkticketing_performance` - 整合流程

2. **P1 輔助函數（第二批）**
   - `nodriver_hkticketing_date_buy_button_press` - 購買按鈕
   - `nodriver_hkticketing_ticket_number_auto_select` - 票數設定
   - `nodriver_hkticketing_next_button_press` - 下一步按鈕
   - `nodriver_hkticketing_go_to_payment` - 付款導航
   - `nodriver_hkticketing_ticket_delivery_option` - 取票方式
   - `nodriver_hkticketing_nav_to_footer` - 捲動到底部

3. **P2 輔助函數（第三批）**
   - `nodriver_hkticketing_login` - 登入
   - `nodriver_hkticketing_date_password_input` - 密碼輸入
   - `nodriver_hkticketing_url_redirect` - URL 重定向
   - `nodriver_hkticketing_content_refresh` - 內容重載
   - `nodriver_hkticketing_travel_iframe` - iframe 遍歷
   - `nodriver_hkticketing_escape_robot_detection` - 機器人檢測

4. **P3 次要函數（第四批）**
   - `nodriver_hkticketing_accept_cookie` - Cookie 彈窗
   - `nodriver_hkticketing_hide_tickets_blocks` - 頁面優化

---

## 7. 參考實作

### 7.1 現有 NoDriver 平台實作

- **Cityline**：`nodriver_tixcraft.py` 行 14880-15941
- **ibon**：`nodriver_tixcraft.py` 行 10222-12900
- **KKTIX**：`nodriver_tixcraft.py` 行 1051-2400

### 7.2 推薦參考模式

| 功能 | 參考函數 | 行號 |
|------|----------|------|
| 主流程控制 | `nodriver_cityline_main` | 15802-15941 |
| 日期選擇 | `nodriver_cityline_date_auto_select` | 15055-15163 |
| 區域選擇 | `nodriver_cityline_area_auto_select` | 15312-15434 |
| 票數設定 | `nodriver_cityline_ticket_number_auto_select` | 15434-15477 |
| 登入處理 | `nodriver_cityline_login` | 14894-14953 |

---

## 8. Fallback 遞補機制（FR-026、FR-036）

### 8.1 功能概述

**決策**：實作 `date_auto_fallback` 和 `area_auto_fallback` 設定，與其他平台保持一致

**理由**：
- 所有其他 NoDriver 平台（KKTIX、TixCraft、iBon、TicketPlus、Cityline、KHAM、FamiTicket）都已實作此功能
- `settings.py` 已定義這兩個欄位（預設 `False`）
- 提供「嚴格模式」和「自動遞補」兩種選擇，滿足不同使用者需求

### 8.2 設定欄位

```python
# settings.py 行 212-213 已定義
config_dict["date_auto_fallback"] = False  # 預設：嚴格模式（避免誤購）
config_dict["area_auto_fallback"] = False  # 預設：嚴格模式（避免誤購）
```

### 8.3 行為定義

| 設定 | 值 | 行為 |
|------|-----|------|
| `date_auto_fallback` | `False` | 日期關鍵字全失敗時，停止選擇流程 |
| `date_auto_fallback` | `True` | 日期關鍵字全失敗時，使用 `auto_select_mode` 自動遞補 |
| `area_auto_fallback` | `False` | 區域關鍵字全失敗時，停止選擇流程 |
| `area_auto_fallback` | `True` | 區域關鍵字全失敗時，使用 `auto_select_mode` 自動遞補 |

### 8.4 實作模式（參考 Cityline）

```python
async def nodriver_hkticketing_date_assign(tab, config_dict):
    """日期選擇核心邏輯，包含 fallback 機制"""
    date_auto_fallback = config_dict.get("date_auto_fallback", False)
    auto_select_mode = config_dict["date_auto_select"]["mode"]

    # ... 關鍵字匹配邏輯 ...

    # 關鍵字匹配失敗時的處理
    if not matched_dates:
        if date_auto_fallback:
            # 使用 auto_select_mode 從所有可用日期中選擇
            print(f"[DATE FALLBACK] date_auto_fallback=true, selecting from all available dates")
            target = util.get_target_item_from_matched_list(available_dates, auto_select_mode)
        else:
            # 嚴格模式：停止選擇
            print("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            return False, False, []

    # ... 繼續選擇流程 ...
```

### 8.5 參考實作位置

| 平台 | 日期 Fallback | 區域 Fallback |
|------|--------------|--------------|
| Cityline | `nodriver_tixcraft.py:15125-15131` | `nodriver_tixcraft.py:15407-15413` |
| KKTIX | `nodriver_tixcraft.py:1730-1741` | `nodriver_tixcraft.py:2264-2277` |
| iBon | `nodriver_tixcraft.py:10946-10955` | `nodriver_tixcraft.py:12666-12677` |
| TicketPlus | `nodriver_tixcraft.py:6614-6622` | `nodriver_tixcraft.py:7020-7034` |

---

## 9. 結論

HKTicketing 遷移至 NoDriver 的技術可行性已確認。主要工作量在於：

1. **API 轉換**：將 19 個同步函數轉為異步函數
2. **SELECT 處理**：使用 JavaScript evaluate 替代 Selenium Select 類別
3. **捲動操作**：使用 `scroll_into_view()` 替代 ActionChains
4. **iframe 處理**：使用 JavaScript 遍歷替代 switch_to.frame
5. **Fallback 機制**：實作 `date_auto_fallback` 和 `area_auto_fallback`（FR-026、FR-036）

所有共用函數（util.py）保持不變，在 NoDriver 函數內部處理元素文字提取即可。
