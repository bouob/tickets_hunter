# 年代售票 NoDriver 下拉選單序列化問題

**平台**：年代售票（ticket.com.tw）
**問題類型**：NoDriver JavaScript 序列化錯誤
**影響範圍**：UTK0202 頁面（座位/票種選擇）
**問題日期**：2025-10-09
**修復版本**：已修復（使用 CDP DOM 操作）

---

## 📋 問題描述

### 錯誤訊息

```
AttributeError: 'list' object has no attribute 'get'
位置：src/nodriver_tixcraft.py:12717
```

### 問題現象

1. 年代售票 style2.html 頁面（UTK0202）座位選擇功能失敗
2. 程式在 `dropdown_result.get('hasDropdown')` 時拋出 AttributeError
3. 預期 `dropdown_result` 應為字典，實際返回列表

---

## 🔍 問題分析

### 根本原因

**NoDriver 的 `tab.evaluate()` 無法正確序列化嵌套的 JavaScript 對象結構**

#### 原始錯誤代碼（JavaScript）

```javascript
return { hasDropdown: true, options: result };
```

**問題**：
- NoDriver 嘗試將 JavaScript 對象 `{ hasDropdown: true, options: [...] }` 序列化為 Python 數據
- 序列化失敗或不完整，導致 Python 接收到錯誤的數據類型（list 而非 dict）

#### 原始錯誤代碼（Python）

```python
if dropdown_result and dropdown_result.get('hasDropdown'):
    options_data = dropdown_result.get('options', [])
```

**錯誤**：`dropdown_result` 實際上是 list，沒有 `.get()` 方法

---

## ✅ 解決方案：改用 CDP DOM 操作

### 方案概述

**不依賴 JavaScript 序列化，改用 NoDriver CDP 原生 DOM 操作**

### 修正前後對比

#### ❌ 修正前：JavaScript 序列化方式

```python
dropdown_result = await tab.evaluate('''
    (function() {
        const priceSelect = document.querySelector('select#PRICE, select[id$="_PRICE"]');
        if (!priceSelect) return null;

        const options = priceSelect.querySelectorAll('option:not([value="-1"])');
        const result = [];

        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            result.push({
                index: i,
                text: option.textContent.trim(),
                value: option.getAttribute('value'),
                element: option  // ❌ 無法序列化
            });
        }

        return { hasDropdown: true, options: result };  // ❌ 嵌套對象序列化失敗
    })();
''')

if dropdown_result and dropdown_result.get('hasDropdown'):  # ❌ AttributeError
    options_data = dropdown_result.get('options', [])
```

#### ✅ 修正後：CDP DOM 操作方式

```python
# 使用 CDP 獲取 select 元素
price_select = None
try:
    price_select = await tab.query_selector('select#PRICE')
    if not price_select:
        selects = await tab.query_selector_all('select[id$="_PRICE"]')
        if selects and len(selects) > 0:
            price_select = selects[0]
except Exception as exc:
    if show_debug_message:
        print(f"Error finding PRICE select: {exc}")

# 使用 CDP 獲取 option 元素
if price_select:
    try:
        option_elements = await price_select.query_selector_all('option:not([value="-1"])')

        # 使用 CDP 獲取元素屬性
        options_data = []
        for i, opt_elem in enumerate(option_elements):
            try:
                # 使用 get_html() 和 apply() 獲取數據
                opt_text = await opt_elem.get_html()
                opt_text = util.remove_html_tags(opt_text).strip()

                opt_value = await opt_elem.apply('function(el) { return el.value; }')
                is_disabled = await opt_elem.apply('function(el) { return el.disabled; }')

                if opt_text and not is_disabled:
                    options_data.append({
                        'index': i,
                        'text': opt_text,
                        'value': opt_value,
                        'element': opt_elem  # ✅ 保留 CDP 元素引用
                    })
            except Exception as exc:
                if show_debug_message:
                    print(f"Error processing option {i}: {exc}")

        # ... 關鍵字過濾邏輯 ...

        # 使用 CDP 點擊選項
        if matched_options:
            target_option = matched_options[0]
            try:
                await target_option['element'].click()  # ✅ CDP 原生點擊
                is_price_assign_by_bot = True
            except Exception as exc:
                # Fallback: JavaScript 設置值
                select_result = await tab.evaluate('''
                    (function(value) {
                        const select = document.querySelector('select#PRICE, select[id$="_PRICE"]');
                        if (select) {
                            select.value = value;
                            select.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                        return false;
                    })(arguments[0]);
                ''', target_option['value'])
                is_price_assign_by_bot = select_result

    except Exception as exc:
        if show_debug_message:
            print(f"Dropdown processing error: {exc}")
```

---

## 🔑 關鍵改進點

### 1. 使用 CDP 查詢元素

```python
# ✅ 使用 CDP query_selector
price_select = await tab.query_selector('select#PRICE')
option_elements = await price_select.query_selector_all('option:not([value="-1"])')
```

**優點**：
- 直接獲取 CDP 元素對象
- 不需要 JavaScript 序列化
- 可保留元素引用進行後續操作

### 2. 使用 CDP 獲取屬性

```python
# ✅ 使用 get_html() 和 apply()
opt_text = await opt_elem.get_html()
opt_value = await opt_elem.apply('function(el) { return el.value; }')
is_disabled = await opt_elem.apply('function(el) { return el.disabled; }')
```

**優點**：
- `get_html()` 獲取 HTML 內容（含標籤）
- `apply()` 執行簡單的 JavaScript 取值
- 返回基本數據類型（string, boolean），容易序列化

### 3. 使用 CDP 點擊元素

```python
# ✅ CDP 原生點擊
await target_option['element'].click()

# ✅ Fallback: JavaScript 設置值
await tab.evaluate('...', target_option['value'])
```

**優點**：
- 優先使用 CDP 原生方法
- 失敗時回退到 JavaScript
- 雙重保障確保成功

---

## 📊 測試結果

### 測試輸出

```
Found dropdown with 2 options
Option excluded by keyword: '標準區 3,580'
Option matched (no keyword filter): '搖滾區 3,580'
Selected dropdown option: 搖滾區 3,580
Starting Kham OCR processing...
```

### 驗證要點

✅ **成功找到下拉選單**（2 個選項）
✅ **關鍵字過濾成功**（排除第一個選項）
✅ **成功選擇目標選項**
✅ **程式繼續運行**（進入驗證碼處理階段）
✅ **無錯誤拋出**

---

## 📝 技術總結

### NoDriver JavaScript 序列化限制

| 數據類型 | 是否可序列化 | 備註 |
|---------|------------|------|
| String, Number, Boolean | ✅ 可以 | 基本數據類型 |
| Simple Object `{key: value}` | ⚠️ 有限支援 | 簡單對象可能成功 |
| Nested Object `{key: {nested}}` | ❌ 不穩定 | 嵌套結構容易失敗 |
| DOM Element | ❌ 不可以 | 無法序列化 DOM 節點 |
| Array of Simple Types | ✅ 可以 | 簡單數組可以 |
| Array of Objects | ⚠️ 有限支援 | 複雜結構可能失敗 |

### 最佳實踐

1. **優先使用 CDP DOM 操作**：`query_selector`, `query_selector_all`, `get_html()`, `apply()`
2. **避免複雜的 JavaScript 序列化**：不返回嵌套對象或 DOM 元素
3. **使用 `apply()` 取得簡單值**：返回 string, number, boolean
4. **保留元素引用**：將 CDP 元素存入 Python 變數，用於後續操作
5. **提供 JavaScript Fallback**：CDP 失敗時回退到 `evaluate()`

---

## 🔗 相關文件

- **NoDriver API 指南**：`docs/06-api-reference/nodriver_api_guide.md`
- **Chrome API 指南**：`docs/06-api-reference/chrome_api_guide.md`
- **除錯方法論**：`docs/07-testing-debugging/debugging_methodology.md`
- **程式結構**：`docs/02-development/structure.md`

---

## 📌 適用版本

- **修復版本**：2025-10-09
- **影響檔案**：`src/nodriver_tixcraft.py:12687-12798`
- **影響函數**：`nodriver_kham_area_auto_select()`
- **相關平台**：年代售票（ticket.com.tw）、ibon（相同邏輯）

---

---

## 🔄 後續修正：Bootstrap Select 互動問題

### 問題描述

初次修正後發現 NoDriver 無法正確選擇 Bootstrap Select 的選項：
- JavaScript 序列化問題已解決
- 但 Bootstrap Select UI 沒有更新
- 選項沒有被正確選中

### 根本原因

年代售票使用 **Bootstrap Select 插件**將原始 `<select>` 替換為自定義 UI：
- 原始 `<select>` 被隱藏（`tabindex="-98"`）
- Bootstrap 創建 `<button>` 和 `<ul><li><a>` 來模擬下拉選單
- 必須點擊 Bootstrap 生成的 UI 元素，而非原始 `<select>`

### 最終解決方案

**模擬真實用戶操作**：
1. 點擊 Bootstrap Select 按鈕打開選單
2. 等待選單展開（500ms）
3. 找到並點擊對應的 `<a>` 元素

```javascript
async function(targetText) {
    // Step 1: Find and click Bootstrap Select button
    const button = document.querySelector('button.dropdown-toggle[data-id$="_PRICE"]');
    if (!button) {
        // Fallback: direct select value setting
        const select = document.querySelector('select#PRICE, select[id$="_PRICE"]');
        if (select) {
            for (let opt of select.options) {
                if (opt.textContent.trim() === targetText) {
                    select.value = opt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    return { success: true, method: 'direct' };
                }
            }
        }
        return { success: false, method: 'none' };
    }

    // Click button to open dropdown
    button.click();

    // Wait for dropdown to open
    await new Promise(resolve => setTimeout(resolve, 500));

    // Step 2: Find and click the matching <a> element
    const menuItems = document.querySelectorAll('ul.dropdown-menu.inner li[data-original-index] a');

    for (let link of menuItems) {
        const textSpan = link.querySelector('span.text');
        if (textSpan && textSpan.textContent.trim() === targetText) {
            link.click();
            return { success: true, method: 'bootstrap' };
        }
    }

    return { success: false, method: 'not_found' };
}
```

### 關鍵改進

1. **使用 async function**
   - 在 JavaScript 中使用 `await` 正確等待選單展開
   - 避免點擊後立即查找選項（選單可能還沒展開）

2. **增加等待時間**
   - 從 300ms 增加到 500ms
   - 確保 Bootstrap Select 動畫完成

3. **詳細的調試信息**
   - 使用 `console.log` 記錄每個步驟
   - 返回包含 `success` 和 `method` 的對象

4. **Fallback 機制**
   - 如果找不到 Bootstrap Select 按鈕，直接設置 `<select>` 的值
   - 適用於非 Bootstrap Select 的場景

---

**最後更新**：2025-10-09
