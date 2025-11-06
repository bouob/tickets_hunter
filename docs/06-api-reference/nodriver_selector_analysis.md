# NoDriver Selector 使用分析報告

**日期**: 2025-10-28
**分析範圍**: `src/nodriver_tixcraft.py`
**參考文章**: https://stackoverflow.max-everyday.com/2025/10/nodriver-query-selector-sub-selector/

---

## 📚 文章核心要點總結

### 問題背景
在 NoDriver 中從特定選擇器獲取子選擇器時，如何避免多次不必要的 CDP 指令傳輸，提升效率。

### 三種解決方案比較

#### ❌ 解法1：重複查詢（不推薦）
```python
# 每次遍歷都重新查詢
for i in range(len(rows)):
    row = await tab.query_selector(f'tr:nth-child({i})')
    button = await tab.query_selector(f'tr:nth-child({i}) button')  # 重複查詢
```
**缺點**: 多花很多次無用的 CDP 指令傳輸，效率大打折扣

#### ⚠️ 解法2：延遲操作（可行）
```python
# 返回完整元素，需要時再點擊子元素
rows = await tab.query_selector_all('tr')
for row in rows:
    button = await row.query_selector('button')  # 延遲查詢子元素
    await button.click()
```
**優點**: 重用 cached element，效率較好

#### ✅ 解法3：直接存取（推薦）
```python
# 直接存取 cached element
select_query = "#host"
div_host = await demo_tab.query_selector(select_query)
# 直接操作 div_host，不進行第二次 sub selector
```
**優點**: 直接存取 cached element，效率最佳

### 關鍵原則
> **重用 cached elements** - 解法2與3的核心優勢在於「直接存取 cached element，所以效率會比較好」

---

## 🔍 專案程式碼使用分析

### 1️⃣ 日期選擇邏輯 (行 2372-2430)

#### 使用模式
```python
# 先取得目標區域（父元素）
target_area = formated_area_list[target_area_index]

# 方法1: 查詢子選擇器 button[data-href]
button_with_href = await target_area.query_selector('button[data-href]')
if button_with_href:
    await button_with_href.update()
    button_attrs = button_with_href.attrs or {}
    data_href = button_attrs.get('data-href', '')

# 方法2: 查詢子選擇器 a[href]
link = await target_area.query_selector('a[href]')
if link:
    await link.click()

# 方法3: 查詢子選擇器 button
button = await target_area.query_selector('button')
if button:
    await button.click()
```

#### 評估
- ✅ **符合解法2（延遲操作）**
- ✅ **效率良好**: 使用父元素的 cached element 進行子查詢
- ✅ **避免全域重複查詢**: 不是使用 `tab.query_selector()` 重複查詢整個 DOM
- ⚠️ **改進空間**: 若需要多次點擊同一按鈕，可考慮快取子元素

---

### 2️⃣ 區域選擇邏輯 (行 2542-2547)

#### 使用模式
```python
# el 是父元素（已由 tab.query_selector('.zone') 取得）
try:
    area_list = await el.query_selector_all('a')
except:
    if show_debug_message:
        print(f"[AREA KEYWORD] Failed to query area list")
    return True, None
```

#### 評估
- ✅ **符合解法2（延遲操作）**
- ✅ **效率良好**: 在父元素 `.zone` 內查詢所有連結
- ✅ **範圍限縮**: 避免全域查詢，只在特定區域內搜尋

---

### 3️⃣ 票價列表檢查 (行 2613-2621)

#### 使用模式
```python
# row 是 area_list 中的某一列
for row in area_list:
    if config_dict["ticket_number"] > 1:
        try:
            font_el = await row.query_selector('font')
            if font_el:
                font_text = await font_el.evaluate('el => el.textContent')
                if font_text:
                    font_text = "@%s@" % font_text
```

#### 評估
- ✅ **符合解法2（延遲操作）**
- ✅ **在迴圈中高效**: 每個 row 都是 cached element，子查詢效率良好
- ✅ **避免重複全域查詢**: 不是使用索引再重新查詢整個 DOM

---

### 4️⃣ 票價選項檢查 (行 2790-2798)

#### 使用模式
```python
# select_element 是已取得的 <select> 元素
for i, select_element in enumerate(form_select_list):
    # 檢查 option 元素
    option_elements = await select_element.query_selector_all('option')
    has_valid_option = False
    option_values = []

    for option_element in option_elements:
        try:
            # 處理每個 option
```

#### 評估
- ✅ **符合解法2（延遲操作）**
- ✅ **雙層迴圈最佳化**:
  - 外層: 遍歷 select 元素（已 cached）
  - 內層: 查詢每個 select 內的 options（在父元素內查詢）
- ✅ **避免 N×M 次全域查詢**: 若用解法1會非常低效

---

### 5️⃣ 單次查詢模式（無子選擇器）

#### 使用模式示例
```python
# 直接查詢並操作（無子選擇器）
form_verifyCode = await tab.query_selector('#TicketForm_verifyCode')
if form_verifyCode:
    await form_verifyCode.click()
    await form_verifyCode.send_keys(ocr_answer)
```

#### 評估
- ✅ **符合解法3（直接存取）**
- ✅ **最簡潔高效**: 查詢一次即可操作
- ✅ **適用場景**: 唯一元素或不需要遍歷的情況

---

## 📊 整體評估

### ✅ 優點

1. **避免解法1的反模式**
   - 專案中 **沒有** 使用重複全域查詢的模式
   - 未見到 `await tab.query_selector(f'selector:nth-child({i}) subselector')` 這類反模式

2. **大量使用解法2（延遲操作）**
   - 日期選擇: `target_area.query_selector()`
   - 區域選擇: `el.query_selector_all()`
   - 票價檢查: `row.query_selector()` + `select_element.query_selector_all()`

3. **適當使用解法3（直接存取）**
   - 單一元素操作: `tab.query_selector()` → 直接操作
   - Cookie 設定、登入表單等場景

4. **效率考量**
   - 在迴圈中使用子選擇器時，都是基於已取得的父元素
   - 避免多次 CDP 指令傳輸

### ⚠️ 潛在改進空間

#### 1. 子元素快取機會
**場景**: 日期選擇的多方法嘗試（行 2372-2430）

**現況**:
```python
button_with_href = await target_area.query_selector('button[data-href]')
if button_with_href:
    # 處理
else:
    link = await target_area.query_selector('a[href]')  # 第二次查詢
    if link:
        # 處理
    else:
        button = await target_area.query_selector('button')  # 第三次查詢
```

**改進建議**:
```python
# 一次查詢所有可能的子元素
button_with_href = await target_area.query_selector('button[data-href]')
link = await target_area.query_selector('a[href]')
button = await target_area.query_selector('button')

# 按優先順序處理
if button_with_href:
    # 處理方法1
elif link:
    # 處理方法2
elif button:
    # 處理方法3
```

**權衡**:
- ✅ 減少條件判斷的 CDP 往返
- ❌ 增加前置查詢成本
- 🤔 **實際影響**: 微小，因為大部分情況第一個方法就會成功

#### 2. 列表遍歷時的元素屬性存取

**現況**: 每次需要時才查詢子元素
```python
for row in area_list:
    font_el = await row.query_selector('font')
    if font_el:
        font_text = await font_el.evaluate('el => el.textContent')
```

**改進方向**: 使用 `get_html()` 一次性取得所有內容
```python
for row in area_list:
    row_html = await row.get_html()  # 一次取得所有內容
    # 使用 HTML 解析取代子查詢
```

**實際應用**: 專案中已在某些地方使用此技巧（行 2224）
```python
row_html = await row.get_html()
row_text = util.remove_html_tags(row_html)
```

---

## 🎯 結論與建議

### 總結
1. ✅ **專案整體符合文章推薦的最佳實踐**
2. ✅ **未發現解法1（重複查詢）的反模式**
3. ✅ **大量使用解法2（延遲操作）**，效率良好
4. ✅ **適當使用解法3（直接存取）**，簡潔高效

### 行動建議

#### 🟢 保持現狀（優先）
- 現有程式碼已經遵循最佳實踐
- 子選擇器使用合理且高效
- 無須大規模重構

#### 🟡 微調優化（可選）
1. **日期選擇多方法嘗試**（行 2372-2430）
   - 評估是否需要減少條件查詢的 CDP 往返
   - 實際影響可能微小，不建議優先處理

2. **元素屬性批量提取**
   - 繼續使用 `get_html()` 取代多次 `query_selector()` + `evaluate()`
   - 已在部分程式碼中採用，可擴大應用

#### 🔵 學習參考（文件化）
- 將文章要點整合到專案文件中
- 在 `docs/06-api-reference/nodriver_api_guide.md` 增加「子選擇器最佳實踐」章節
- 為未來開發者提供指引

---

## 📖 參考資料

- **原文**: https://stackoverflow.max-everyday.com/2025/10/nodriver-query-selector-sub-selector/
- **NoDriver API 指南**: `docs/06-api-reference/nodriver_api_guide.md`
- **程式結構文件**: `docs/02-development/structure.md`

---

**報告產生時間**: 2025-10-28
**分析工具**: Claude Code
**程式碼版本**: main branch (commit: 14d2f53)
