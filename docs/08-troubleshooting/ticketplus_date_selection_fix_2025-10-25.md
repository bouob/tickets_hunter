**文件說明**：TicketPlus 日期選擇的修復計畫，涵蓋關鍵字匹配失敗、購買按鈕點擊問題與 NoDriver + CDP 混合解決方案。

**最後更新**：2025-11-12

---

# TicketPlus 日期選擇修復計畫（NoDriver + CDP）

**日期**：2025-10-25
**問題**：日期關鍵字匹配失敗，無法點擊「立即購買」按鈕
**影響平台**：TicketPlus（NoDriver 版本）

---

## 問題根源分析

### 1. 關鍵字匹配範圍錯誤

**HTML 結構**：
```html
<div class="row pa-4">  <!-- 整個日期項目 -->

  <!-- 左側：活動資訊（佔 10/12 寬度） -->
  <div class="col-sm-10 col-md-10 col-12">
    - 標題：藍井艾露 2025「BLUE FLAiR」台北演唱會
    - 日期：2025-12-05(五)  ← 關鍵字應該匹配這裡
    - 時間：19:00
    - 地點：Legacy TERA
  </div>

  <!-- 右側：按鈕（佔 2/12 寬度） -->
  <div class="col-sm-2 col-md-2 col-12">
    <button class="nextBtn">立即購買</button>  ← 應該點擊這裡
  </div>

</div>
```

**當前問題**：
- Python 端：在整個 `div.row` 的文字中匹配關鍵字（包含按鈕文字「立即購買」）
- JavaScript 端：也在整個元素中匹配關鍵字
- 結果：關鍵字過濾範圍過大，邏輯混亂

### 2. 雙重過濾導致回退失敗

**流程分析**：
1. **Python 端**（第 3784-3838 行）：
   - 關鍵字 `"12-21"` 無法匹配頁面上的 `"2025-12-05(五)"`
   - 回退到 `formated_area_list`（所有可用日期）
   - Log：`[TicketPlus DATE] No keyword matches, falling back to mode 'from bottom to top'`

2. **JavaScript 端**（第 3851-3976 行）：
   - 仍然收到原始關鍵字 `"12-21"`
   - 再次用關鍵字過濾元素
   - 沒有匹配 → 返回錯誤：`No matched date elements found`

**根本問題**：Python 已經回退到「選擇所有日期」，但 JavaScript 不知道，仍然堅持使用關鍵字過濾。

### 3. Log 證據

**.temp/manual_logs.txt**：
```
date_list_count: 1
formated_area_list count: 1
[TicketPlus DATE] Applying keyword filter: ['12-21']
[TicketPlus DATE] No keyword matches, falling back to mode 'from bottom to top'
Date selection and click failed: No matched date elements found
```

**解讀**：
- 找到 1 個可用日期
- 關鍵字過濾失敗
- Python 回退成功
- JavaScript 點擊失敗（仍用關鍵字過濾）

---

## 修改方案（NoDriver First 原則）

### **修改 1：Python 端 - 精確關鍵字匹配**

**檔案**：`src/nodriver_tixcraft.py`
**函數**：`nodriver_ticketplus_date_auto_select`
**位置**：第 3800-3823 行

#### 當前代碼

```python
# Match keyword groups (OR logic between groups)
for i, row in enumerate(formated_area_list):
    # Get row text
    row_text = ""
    try:
        row_html = await row.get_html()
        row_text = util.remove_html_tags(row_html).lower()
    except Exception as exc:
        if show_debug_message:
            print(f"[TicketPlus DATE] Failed to get row text: {exc}")
        continue
```

#### 修改為

```python
# Match keyword groups (OR logic between groups)
for i, row in enumerate(formated_area_list):
    # Get row text - 只從活動資訊區取得（NoDriver query_selector）
    row_text = ""
    try:
        # 優先：只取活動資訊區的文字
        info_section = await row.query_selector('div.col-sm-10, div[class*="col-"]')
        if info_section:
            info_html = await info_section.get_html()
            row_text = util.remove_html_tags(info_html).lower()
            if show_debug_message:
                print(f"[TicketPlus DATE] Row {i} info section text (first 100): {row_text[:100]}")
        else:
            # 回退：如果找不到 col-sm-10，使用整個 row
            row_html = await row.get_html()
            row_text = util.remove_html_tags(row_html).lower()
            if show_debug_message:
                print(f"[TicketPlus DATE] Row {i} info section not found, using full text")
    except Exception as exc:
        if show_debug_message:
            print(f"[TicketPlus DATE] Failed to get row text: {exc}")
        continue
```

**關鍵改動**：
1. ✅ 使用 NoDriver `query_selector` 定位活動資訊區（`div.col-sm-10`）
2. ✅ 只在活動資訊區匹配關鍵字，不受按鈕文字干擾
3. ✅ 保留回退機制（找不到 col-sm-10 時使用整個 row）
4. ✅ 增加 debug 輸出

---

### **修改 2：JavaScript 端 - 分離匹配與點擊**

**檔案**：`src/nodriver_tixcraft.py`
**位置**：JavaScript evaluate 區塊（第 3851-4056 行）

#### 2.1 修改關鍵字匹配邏輯（第 3898-3918 行）

**當前代碼**：
```javascript
for (let element of allElements) {
    const text = element.textContent || element.innerText || '';
    const normalizedText = text.replace(/[\s\u3000]/g, '').toLowerCase();

    // 檢查是否包含任一關鍵字
    let matched = false;
    for (let keyword of keywords) {
        const normalizedKeyword = keyword.replace(/[\s\u3000]/g, '').toLowerCase();

        if (normalizedText.includes(normalizedKeyword)) {
            console.log('點擊邏輯匹配到日期元素:', '"' + keyword + '" -> ' + text.substring(0, 100));
            matched = true;
            break;
        }
    }

    if (matched) {
        matchedElements.push(element);
    }
}
```

**修改為**：
```javascript
for (let element of allElements) {
    // 只在活動資訊區匹配關鍵字
    let text = '';
    const infoSection = element.querySelector('div.col-sm-10, div[class*="col-sm-10"]');
    if (infoSection) {
        text = infoSection.textContent || infoSection.innerText || '';
        console.log('[TicketPlus] Matching in info section, text length:', text.length);
    } else {
        // 回退：使用整個元素
        text = element.textContent || element.innerText || '';
        console.log('[TicketPlus] Info section not found, using full element text');
    }

    const normalizedText = text.replace(/[\s\u3000]/g, '').toLowerCase();

    // 檢查是否包含任一關鍵字
    let matched = false;
    for (let keyword of keywords) {
        const normalizedKeyword = keyword.replace(/[\s\u3000]/g, '').toLowerCase();

        if (normalizedText.includes(normalizedKeyword)) {
            console.log('[TicketPlus] Keyword matched:', keyword, '-> Element text (first 100):', text.substring(0, 100));
            matched = true;
            break;
        }
    }

    if (matched) {
        matchedElements.push(element);
    }
}
```

**關鍵改動**：
1. ✅ 使用 DOM API `querySelector` 定位活動資訊區
2. ✅ 只在活動資訊區匹配關鍵字
3. ✅ 保留回退機制
4. ✅ 改善 console.log 輸出格式

#### 2.2 改進按鈕點擊邏輯（第 4001-4017 行）

**當前代碼**：
```javascript
// 方法1: 找內部的按鈕
const button = targetElement.querySelector('button');
if (button && !clickSuccess) {
    try {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        button.dispatchEvent(event);
        clickSuccess = true;
        clickAction = 'internal_button_clicked';
        console.log('Internal button click successful');
    } catch (e) {
        console.log('Internal button click failed:', e.message);
    }
}
```

**修改為**：
```javascript
// 方法1: 優先在按鈕區（col-sm-2）查找「立即購買」按鈕
let button = targetElement.querySelector('div.col-sm-2 button.nextBtn, div[class*="col-sm-2"] button.nextBtn');
if (!button) {
    // 回退1: 任何 nextBtn 按鈕
    button = targetElement.querySelector('button.nextBtn');
    console.log('[TicketPlus] Fallback to any nextBtn');
}
if (!button) {
    // 回退2: 任何按鈕
    button = targetElement.querySelector('button');
    console.log('[TicketPlus] Fallback to any button');
}

if (button && !clickSuccess) {
    console.log('[TicketPlus] Button found, class:', button.className, 'text:', (button.textContent || '').substring(0, 20));
    try {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        button.dispatchEvent(event);
        clickSuccess = true;
        clickAction = 'button_in_col_sm_2_clicked';
        console.log('[TicketPlus] Button click successful');
    } catch (e) {
        console.log('[TicketPlus] Button click failed:', e.message);
    }
}
```

**關鍵改動**：
1. ✅ 明確定位按鈕區（`div.col-sm-2 button.nextBtn`）
2. ✅ 多層回退機制（nextBtn → any button）
3. ✅ 詳細的 debug 輸出（按鈕 class、文字）

---

### **修改 3：修復回退邏輯傳遞**

**檔案**：`src/nodriver_tixcraft.py`
**位置**：第 3834-3856 行

#### 當前代碼

```python
# Fallback: if no matches found, use all available dates
if len(matched_blocks) == 0 and formated_area_list and len(formated_area_list) > 0:
    if show_debug_message:
        print(f"[TicketPlus DATE] No keyword matches, falling back to mode '{auto_select_mode}'")
    matched_blocks = formated_area_list

# ...後續執行點擊...
# 使用原始關鍵字進行點擊
original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
```

#### 修改為

```python
# Fallback: if no matches found, use all available dates
is_fallback_mode = False
if len(matched_blocks) == 0 and formated_area_list and len(formated_area_list) > 0:
    if show_debug_message:
        print(f"[TicketPlus DATE] No keyword matches, falling back to mode '{auto_select_mode}'")
    matched_blocks = formated_area_list
    is_fallback_mode = True

# ...後續執行點擊...
# 回退模式下，傳遞空字串給 JavaScript（讓 JS 跳過關鍵字過濾）
if is_fallback_mode:
    original_keyword = ""
    if show_debug_message:
        print(f"[TicketPlus DATE] Fallback mode: disabling JS keyword filter")
else:
    original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    if show_debug_message:
        print(f"[TicketPlus DATE] Normal mode: using keyword '{original_keyword}'")
```

**關鍵改動**：
1. ✅ 增加 `is_fallback_mode` 標記
2. ✅ 回退模式下傳遞空字串給 JavaScript
3. ✅ JavaScript 收到空字串時，會跳過關鍵字過濾（第 3881 行檢查 `originalKeyword && originalKeyword.trim() !== ''`）
4. ✅ 增加 debug 輸出

---

### **修改 4：增加除錯訊息**

在關鍵位置增加 debug 輸出（當 `verbose=True` 時）：

**Python 端增加**：
```python
if show_debug_message:
    print(f"[TicketPlus DATE] Total rows: {len(area_list)}")
    print(f"[TicketPlus DATE] Valid rows (formated_area_list): {len(formated_area_list)}")
    print(f"[TicketPlus DATE] After keyword filter: {len(matched_blocks)}")
    print(f"[TicketPlus DATE] Fallback mode: {is_fallback_mode}")
    print(f"[TicketPlus DATE] Keyword sent to JS: '{original_keyword}'")
```

**JavaScript 端增加**：
```javascript
console.log('[TicketPlus] === Date Selection Debug ===');
console.log('[TicketPlus] Keyword:', originalKeyword);
console.log('[TicketPlus] Auto select mode:', autoSelectMode);
console.log('[TicketPlus] Total elements found:', allElements.length);
console.log('[TicketPlus] After keyword filter:', matchedElements.length);
console.log('[TicketPlus] Target selector: div.col-sm-2 button.nextBtn');
```

---

## 修改摘要表

| 修改項目 | 檔案位置 | 使用技術 | 優先度 | 預期效果 |
|---------|---------|---------|--------|---------|
| **Python 關鍵字匹配範圍** | 3800-3823 行 | NoDriver `query_selector` | 🔴 高 | 只在活動資訊區匹配 |
| **JS 關鍵字匹配範圍** | 3898-3918 行 | DOM `querySelector` | 🔴 高 | 與 Python 邏輯一致 |
| **JS 按鈕點擊邏輯** | 4001-4017 行 | DOM `querySelector` | 🔴 高 | 明確定位按鈕區 |
| **回退邏輯修復** | 3834-3856 行 | Python 邏輯判斷 | 🟡 中 | 空字串禁用 JS 過濾 |
| **除錯訊息增強** | 多處 | console.log + print | 🟢 低 | 快速定位問題 |

---

## 測試驗證計畫

### 1. 測試前準備

**設定檔**（`src/settings.json`）：
```json
{
  "date_auto_select": {
    "mode": "from bottom to top",
    "date_keyword": "12-05"  // 匹配實際日期
  },
  "advanced": {
    "verbose": true  // 啟用詳細輸出
  }
}
```

### 2. 執行測試

**Git Bash**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**Windows CMD**：
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && \
del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && \
echo. > .temp\test_output.txt && \
timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

### 3. 檢查輸出

**檢查日期選擇邏輯**：
```bash
grep "\[TicketPlus DATE\]" .temp/test_output.txt
```

**預期輸出**：
```
[TicketPlus DATE] Total rows: 1
[TicketPlus DATE] Valid rows (formated_area_list): 1
[TicketPlus DATE] Row 0 info section text (first 100): 藍井艾露 2025「blue flair」台北演唱會日期2025-12-05(五)時間19:00地點legacy tera台北市南港區市民大道八段99號
[TicketPlus DATE] Keyword matched: '12-05' matched row 0
[TicketPlus DATE] After keyword filter: 1
[TicketPlus DATE] Fallback mode: False
[TicketPlus DATE] Keyword sent to JS: '12-05'
```

**檢查按鈕點擊**：
```bash
grep "\[TicketPlus\]" .temp/test_output.txt
```

**預期輸出**：
```
[TicketPlus] === Date Selection Debug ===
[TicketPlus] Keyword: 12-05
[TicketPlus] Auto select mode: from bottom to top
[TicketPlus] Total elements found: 15
[TicketPlus] Matching in info section, text length: 120
[TicketPlus] Keyword matched: 12-05 -> Element text (first 100): 藍井艾露 2025「BLUE FLAiR」台北演唱會...
[TicketPlus] After keyword filter: 1
[TicketPlus] Target selector: div.col-sm-2 button.nextBtn
[TicketPlus] Button found, class: nextBtn float-right v-btn v-btn--block..., text: 立即購買
[TicketPlus] Button click successful
```

### 4. 成功標準

✅ 日期匹配成功（`After keyword filter: 1`）
✅ 按鈕定位成功（`Button found`）
✅ 按鈕點擊成功（`Button click successful`）
✅ 頁面跳轉到下一階段（票種選擇頁面）

### 5. 回退測試

**設定檔**（使用錯誤關鍵字）：
```json
{
  "date_auto_select": {
    "mode": "from bottom to top",
    "date_keyword": "12-21"  // 故意使用不存在的日期
  },
  "advanced": {
    "verbose": true
  }
}
```

**預期輸出**：
```
[TicketPlus DATE] No keyword matches, falling back to mode 'from bottom to top'
[TicketPlus DATE] Fallback mode: True
[TicketPlus DATE] Keyword sent to JS: ''  // 空字串
[TicketPlus] Keyword:   // 空字串，跳過過濾
[TicketPlus] No keyword specified, filtering relevant buy buttons
[TicketPlus] No keyword - filtered to 1 relevant buy buttons
[TicketPlus] Button click successful
```

---

## 憲法規範檢查

### ✅ I. NoDriver First
- **Python 端**：使用 NoDriver `query_selector` 定位 DOM 元素
- **JavaScript 端**：使用原生 DOM API（符合 NoDriver 最佳實踐）
- **無 UC/Selenium 依賴**

### ✅ II. 資料結構優先
- **分離關注點**：活動資訊（左） vs 按鈕（右）
- **結構驅動邏輯**：基於 HTML 結構（col-sm-10 / col-sm-2）
- **好的結構讓特殊情況消失**：分離後，關鍵字匹配與按鈕點擊互不干擾

### ✅ III. 三問法則
1. **是核心問題嗎？** ✅ 是（日期選擇失敗，無法進入下一階段）
2. **有更簡單方法嗎？** ✅ 否（必須精確定位 DOM 結構）
3. **會破壞相容性嗎？** ✅ 否（保留回退機制，向下相容）

### ✅ IV. 單一職責與可組合性
- **匹配**：只在活動資訊區匹配關鍵字
- **點擊**：只在按鈕區查找並點擊
- **回退**：統一的回退機制（Python → JavaScript）

### ✅ V. 設定驅動開發
- 使用 `settings.json` 的 `date_keyword` 控制行為
- `verbose` 控制除錯輸出
- 無需修改代碼即可調整行為

### ✅ VI. 測試驅動穩定性
- 提供明確的測試指令
- 預期輸出範例
- 成功標準清單
- 回退測試案例

### ✅ VII. MVP 原則
- **核心功能優先**：修復日期選擇（核心流程）
- **最小修改範圍**：只修改 `nodriver_ticketplus_date_auto_select` 函數
- **漸進式改善**：保留回退機制，不破壞現有功能

### ✅ VIII. 文件與代碼同步
- 本計畫文件記錄修改理由、位置、預期效果
- 修改完成後更新 `docs/05-troubleshooting/ticketplus_date_selection_fix.md`
- 在 `docs/02-development/structure.md` 中更新函數描述

---

## 執行檢查清單

修改前：
- [ ] 備份當前代碼（`git stash` 或建立分支）
- [ ] 確認測試環境（Python 3.10+, NoDriver 最新版）
- [ ] 檢查 `settings.json` 設定

修改中：
- [ ] 修改 1：Python 端關鍵字匹配範圍
- [ ] 修改 2.1：JavaScript 端關鍵字匹配範圍
- [ ] 修改 2.2：JavaScript 端按鈕點擊邏輯
- [ ] 修改 3：回退邏輯修復
- [ ] 修改 4：增加除錯訊息

修改後：
- [ ] 執行測試（正常關鍵字匹配）
- [ ] 執行回退測試（錯誤關鍵字）
- [ ] 檢查 `.temp/test_output.txt` 輸出
- [ ] 更新疑難排解文件
- [ ] 提交 Git commit（使用 `/gsave`）

---

## 風險評估

| 風險 | 影響 | 緩解措施 |
|-----|------|---------|
| 回退機制失效 | 🟡 中 | 多層回退（col-sm-10 → 整個 row） |
| 其他平台受影響 | 🟢 低 | 只修改 `nodriver_ticketplus_date_auto_select` |
| 新版 TicketPlus HTML 變更 | 🟡 中 | 使用通用選擇器（`div[class*="col-"]`） |
| JavaScript 執行失敗 | 🟢 低 | Try-catch 保護 + 詳細錯誤輸出 |

---

## 參考資料

- **CDP 協議**：`docs/03-api-reference/cdp_protocol_reference.md`
- **NoDriver API**：`docs/03-api-reference/nodriver_api_guide.md`
- **除錯方法論**：`docs/04-testing-debugging/debugging_methodology.md`
- **TicketPlus HTML**：`.temp/ticketplus.html`
- **測試 Log**：`.temp/manual_logs.txt`

---

**修改計畫建立時間**：2025-10-25
**預計修改時間**：30 分鐘
**預計測試時間**：15 分鐘
**總計**：45 分鐘
