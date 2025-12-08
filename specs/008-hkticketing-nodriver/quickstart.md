# 快速開始：HKTicketing NoDriver 遷移

**功能**：008-hkticketing-nodriver
**日期**：2025-11-27
**狀態**：✅ 實作完成（2025-11-28）

## 前置需求

- Python 3.11+
- NoDriver 套件已安裝
- 專案已設定完成

## 開發流程

### 1. 切換到功能分支

```bash
git checkout 008-hkticketing-nodriver
```

### 2. 開啟開發檔案

主要修改檔案：
- `src/nodriver_tixcraft.py` - 新增 NoDriver HKTicketing 函數

參考檔案：
- `src/chrome_tixcraft.py` - 原 UC Driver 實作（行 5661-8459）

### 3. 函數遷移順序

建議按以下順序實作：

**第一批（主流程 + 日期選擇）**：
1. `nodriver_hkticketing_accept_cookie`
2. `nodriver_hkticketing_date_assign`
3. `nodriver_hkticketing_date_buy_button_press`
4. `nodriver_hkticketing_date_password_input`
5. `nodriver_hkticketing_date_auto_select`

**第二批（區域 + 票數）**：
6. `nodriver_hkticketing_area_auto_select`
7. `nodriver_hkticketing_ticket_number_auto_select`
8. `nodriver_hkticketing_nav_to_footer`
9. `nodriver_hkticketing_ticket_delivery_option`
10. `nodriver_hkticketing_next_button_press`
11. `nodriver_hkticketing_go_to_payment`
12. `nodriver_hkticketing_performance`

**第三批（登入 + 錯誤處理）**：
13. `nodriver_hkticketing_login`
14. `nodriver_hkticketing_url_redirect`
15. `nodriver_hkticketing_content_refresh`
16. `nodriver_hkticketing_travel_iframe`
17. `nodriver_hkticketing_escape_robot_detection`
18. `nodriver_hkticketing_hide_tickets_blocks`

**最後**：
19. `nodriver_hkticketing_main`

### 4. 標準遷移模板

```python
# 原 UC 版本（chrome_tixcraft.py）
def hkticketing_example(driver, config_dict):
    ret = False
    try:
        el = driver.find_element(By.CSS_SELECTOR, "selector")
        if el.is_enabled():
            el.click()
            ret = True
    except Exception as exc:
        pass
    return ret

# NoDriver 版本（nodriver_tixcraft.py）
async def nodriver_hkticketing_example(tab, config_dict):
    ret = False
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        el = await tab.query_selector("selector")
        if el:
            await el.click()
            ret = True
    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] nodriver_hkticketing_example: {exc}")

    return ret
```

### 5. 測試

```bash
# 設定 settings.json
# - homepage: HKTicketing 活動頁面 URL
# - webdriver_type: "nodriver"
# - date_auto_select.enable: true
# - area_auto_select.enable: true

# 執行測試
timeout 60 python -u src/nodriver_tixcraft.py --input src/settings.json
```

### 6. 提交

```bash
/gsave
/gpush
```

## 關鍵 API 對照

| Selenium/UC | NoDriver |
|-------------|----------|
| `driver.find_element(By.CSS_SELECTOR, sel)` | `await tab.query_selector(sel)` |
| `driver.find_elements(By.CSS_SELECTOR, sel)` | `await tab.query_selector_all(sel)` |
| `element.click()` | `await element.click()` |
| `element.send_keys(text)` | `await element.send_keys(text)` |
| `element.get_attribute('innerHTML')` | `await element.get_html()` |
| `driver.execute_script(js)` | `await tab.evaluate(js)` |
| `driver.get(url)` | `await tab.get(url)` |
| `driver.refresh()` | `await tab.reload()` |
| `ActionChains.move_to_element(el)` | `await element.scroll_into_view()` |
| `Select(el).select_by_value(val)` | `await tab.evaluate(js_select)` |

## 參考實作

- **Cityline 主流程**：`nodriver_tixcraft.py` 行 15802-15941
- **Cityline 日期選擇**：`nodriver_tixcraft.py` 行 15055-15163
- **Cityline 區域選擇**：`nodriver_tixcraft.py` 行 15312-15434

## 常見問題

### Q: 如何處理 Select 下拉選單？

使用 JavaScript：
```python
await tab.evaluate(f'''
    (function() {{
        const select = document.querySelector('{selector}');
        select.value = "{value}";
        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }})();
''')
```

### Q: 如何處理元素不可見的情況？

先捲動到元素：
```python
await element.scroll_into_view()
await asyncio.sleep(0.1)
await element.click()
```

### Q: 如何處理 iframe？

使用 JavaScript 遍歷：
```python
content = await tab.evaluate('''
    document.querySelectorAll('iframe')[0].contentDocument.body.innerHTML
''')
```

### Q: 如何實作 Fallback 機制？（FR-026、FR-036）

在日期/區域選擇函數中加入 fallback 邏輯：

```python
async def nodriver_hkticketing_date_assign(tab, config_dict):
    """日期選擇核心邏輯，包含 fallback 機制"""
    # 讀取 fallback 設定（預設 False = 嚴格模式）
    date_auto_fallback = config_dict.get("date_auto_fallback", False)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # ... 關鍵字匹配邏輯 ...

    # 關鍵字匹配失敗時的處理
    if not matched_dates:
        if date_auto_fallback:
            # 使用 auto_select_mode 從所有可用日期中選擇
            if show_debug_message:
                print(f"[DATE FALLBACK] date_auto_fallback=true, selecting from all available dates")
            target = util.get_target_item_from_matched_list(available_dates, auto_select_mode)
        else:
            # 嚴格模式：停止選擇
            if show_debug_message:
                print("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            return False, False, []

    # ... 繼續選擇流程 ...
```

**Fallback 參考位置**：

| 平台 | 日期 Fallback | 區域 Fallback |
|------|--------------|--------------|
| HKTicketing | `nodriver_tixcraft.py:21191-21218` | `nodriver_tixcraft.py:21433-21461` |
| Cityline | `nodriver_tixcraft.py:15125-15131` | `nodriver_tixcraft.py:15407-15413` |
| KKTIX | `nodriver_tixcraft.py:1730-1741` | `nodriver_tixcraft.py:2264-2277` |
| iBon | `nodriver_tixcraft.py:10946-10955` | `nodriver_tixcraft.py:12666-12677` |

**設定欄位**：
- `date_auto_fallback`（bool，預設 False）：日期關鍵字全失敗時是否自動遞補
- `area_auto_fallback`（bool，預設 False）：區域關鍵字全失敗時是否自動遞補
