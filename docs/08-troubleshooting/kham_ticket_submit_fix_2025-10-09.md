**文件說明**：年代售票 提交按鈕的修復記錄，涵蓋選擇器錯誤、參數序列化問題與修復方案。

**最後更新**：2025-11-12

---

# 年代售票 (ticket.com.tw) 提交按鈕修復記錄

**日期**: 2025-10-09
**問題類型**: Submit button selector incorrect, parameter serialization error
**影響頁面**: UTK0202 (票種/票數選擇頁)
**狀態**: ✅ 已修復

---

## 📋 問題描述

### 問題 1: Bootstrap Select 參數序列化錯誤

**錯誤訊息**:
```
Bootstrap Select interaction error: Invalid parameters [code: -32602]
```

**發生位置**: `src/nodriver_tixcraft.py:12895`

**原因**:
- 在 Bootstrap Select 的 fallback 代碼中，使用 `tab.evaluate()` 傳遞 `target_text` 參數
- NoDriver 無法正確序列化包含中文字符的參數

**原始錯誤代碼**:
```python
select_result = await tab.evaluate('''
    (function(targetText) {
        const select = document.querySelector('select#PRICE, select[id$="_PRICE"]');
        if (!select) return false;

        // Find option by text
        for (let opt of select.options) {
            if (opt.textContent.trim() === targetText) {
                select.value = opt.value;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }
        }
        return false;
    })(arguments[0]);
''', target_text)  # ❌ Parameter serialization fails
```

### 問題 2: 提交按鈕選擇器錯誤（票數頁面）

**錯誤位置**: `src/nodriver_tixcraft.py:13713` (原 13688)

**問題**:
- 代碼使用選擇器 `a[onclick="return chkCart();"]` 來查找提交按鈕
- 但實際的 HTML 結構是 `<input type="submit" id="ctl00_ContentPlaceHolder1_AddShopingCart">`
- 導致按鈕無法被找到，表單無法提交

### 問題 3: 提交按鈕選擇器錯誤（票區選擇頁面） - 導致無限循環

**錯誤位置**: `src/nodriver_tixcraft.py:13457` (修正前)

**問題**:
- 在 UTK0202 票區選擇頁面（URL 含 `PERFORMANCE_ID` 和 `PRODUCT_ID`，但無 `PERFORMANCE_PRICE_AREA_ID`）
- 程式成功選擇票區並填入驗證碼後，應該點擊「下一步」按鈕進入票數選擇頁面
- 但 line 13457 使用錯誤選擇器 `a[onclick="return chkCart();"]`，導致按鈕找不到
- 頁面無法跳轉，程式重新執行票區選擇邏輯，形成無限循環

**症狀**:
- 日誌重複出現：「Successfully clicked Bootstrap Select option」→「OCR answer: xxxx」→ 回到票區選擇
- 頁面停留在 `UTK0202_.aspx?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx`
- 無法進入下一個頁面（票數選擇頁）

### 問題 4: 重複提交導致購物車票數翻倍

**錯誤位置**: `src/nodriver_tixcraft.py:13483-13485, 13773-13775` (修正前)

**問題子原因 1: 沒有等待頁面跳轉**
- 點擊提交按鈕後，程式**沒有等待頁面跳轉**
- NoDriver 的 CDP click 是非同步的，點擊後立即返回
- 程式繼續執行，因為 URL 還沒變化，誤判仍在同一頁面
- 重新執行票區選擇邏輯 → 再次點擊提交按鈕

**問題子原因 2: 沒有關閉成功對話框（更嚴重）**
- 點擊提交按鈕後，年代售票會彈出對話框「加入購物車完成, 請於 10 分鐘內完成結帳!」
- **必須點擊 Ok 關閉對話框，URL 才會變化**
- 程式等待 10 秒後超時，但對話框仍然存在
- **CDP 可以穿透對話框繼續點擊按鈕** → 重複提交
- 程式重新執行票區選擇並再次點擊提交
- 對話框累積出現多次

**症狀**（來自 manual_logs.txt）:
```
Line 99: OCR answer: pag2
Line 100-103: [SUBMIT] Add shopping cart button clicked successfully!  ← 第一次點擊
Line 104: [SUBMIT] WARNING: URL did not change after 10 seconds...  ← 超時
Line 105-116: 又重複執行票區選擇
Line 128: OCR answer: -Pag2
Line 129-131: Dialog message: 加入購物車完成, 請於 10 分鐘內完成結帳!  ← 對話框出現 3 次！
Line 132-144: 再次重複執行票區選擇
```

**實際影響**:
- 設定購買 2 張票
- 實際購物車有 4 張票或更多（多次重複提交）
- 對話框累積出現，但都沒被關閉

**原始錯誤代碼**:
```python
if "ticket.com.tw" in url:
    el_btn = await tab.query_selector('a[onclick="return chkCart();"]')  # ❌ Wrong selector
```

**實際 HTML**:
```html
<input type="submit"
       name="ctl00$ContentPlaceHolder1$AddShopingCart"
       value="   加入購物車   "
       id="ctl00_ContentPlaceHolder1_AddShopingCart"
       class="red" />
```

---

## ✅ 解決方案

### 修復 1: Bootstrap Select 參數序列化 (line 12880-12901)

改用 CDP 直接操作，避免參數序列化問題：

```python
# Use CDP to directly set select value (avoid parameter serialization)
select_result = False
try:
    select_elem = await tab.query_selector('select#PRICE, select[id$="_PRICE"]')
    if select_elem:
        # Set value directly using CDP
        await select_elem.apply(f'function(el) {{ el.value = "{target_value}"; }}')
        # Trigger change event
        await tab.evaluate('''
            (function() {
                const select = document.querySelector('select#PRICE, select[id$="_PRICE"]');
                if (select) {
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })();
        ''')
        select_result = True
except Exception as fallback_exc:
    if show_debug_message:
        print(f"Direct select value setting error: {fallback_exc}")
```

**關鍵改進**:
1. ✅ 使用 `query_selector` 獲取元素 (CDP 原生方法)
2. ✅ 使用 `apply()` 設置值 (使用 f-string 嵌入值，而非參數傳遞)
3. ✅ 使用無參數的 `evaluate()` 觸發事件

### 修復 2: 票數頁面提交按鈕 (line 13713-13754)

更正選擇器為正確的 `<input>` 元素：

```python
try:
    if "ticket.com.tw" in url:
        # ticket.com.tw uses <input type="submit"> with id ending in AddShopingCart
        el_btn = await tab.query_selector('input[id$="AddShopingCart"]')
        if not el_btn:
            # Fallback to <a> tag (for other possible layouts)
            el_btn = await tab.query_selector('a[onclick="return chkCart();"]')
    else:
        # Kham
        el_btn = await tab.query_selector('button[onclick="addShoppingCart();return false;"]')

    if el_btn:
        await el_btn.click()
        if show_debug_message:
            print("[SUBMIT] Add shopping cart button clicked")
    else:
        if show_debug_message:
            print("[SUBMIT] Add shopping cart button not found")
except Exception as exc:
    if show_debug_message:
        print("[SUBMIT] Click chkCart/addShoppingCart button fail:", exc)
```

### 修復 3: 票區選擇頁面提交按鈕 (line 13460-13491) - 解決無限循環

**核心問題**: 票區選擇頁面與票數頁面使用相同的按鈕，但之前只修正了票數頁面的選擇器

**修正方案**: 將 line 13460-13491 的按鈕選擇器改為與 line 13713-13754 一致

```python
# Submit if captcha sent
if is_captcha_sent:
    try:
        if "ticket.com.tw" in url:
            # ticket.com.tw uses <input type="submit"> with id ending in AddShopingCart
            if show_debug_message:
                print("[SUBMIT] Searching for ticket.com.tw submit button...")
            el_btn = await tab.query_selector('input[id$="AddShopingCart"]')
            if not el_btn:
                # Fallback to <a> tag (for other possible layouts)
                el_btn = await tab.query_selector('a[onclick="return chkCart();"]')
        else:
            # Kham
            if show_debug_message:
                print("[SUBMIT] Searching for Kham submit button...")
            el_btn = await tab.query_selector('button[onclick="addShoppingCart();return false;"]')

        if el_btn:
            if show_debug_message:
                print("[SUBMIT] Submit button found, scrolling into view...")
            # Scroll button into view first (important for CDP click)
            try:
                await el_btn.scroll_into_view()
                await tab.sleep(0.3)
            except:
                pass

            if show_debug_message:
                print("[SUBMIT] Clicking using CDP native click...")
            # Use NoDriver CDP native click
            await el_btn.click()
            if show_debug_message:
                print("[SUBMIT] Add shopping cart button clicked successfully!")
        else:
            if show_debug_message:
                print("[SUBMIT] Add shopping cart button not found")
    except Exception as exc:
        if show_debug_message:
            print(f"[SUBMIT] Click chkCart/addShoppingCart button fail: {exc}")
```

**關鍵改進**:
1. ✅ 使用 CSS 屬性選擇器 `[id$="AddShopingCart"]` 匹配結尾
2. ✅ 增加 fallback 機制，提高兼容性
3. ✅ 增加調試輸出，便於追蹤執行狀態
4. ✅ 使用 CDP native click + scroll_into_view，確保點擊成功
5. ✅ 兩個頁面使用一致的按鈕選擇邏輯，避免重複錯誤

### 修復 4: 等待頁面跳轉，避免重複提交 (line 13487-13516, 13777-13806)

**核心問題**: CDP click 非同步執行，點擊後立即返回，導致程式繼續執行並重複提交

**修正方案 v1（失敗）**: 點擊後等待 URL 變化 5 秒
- ❌ 年代售票頁面跳轉較慢，5 秒不夠
- ❌ 超時後立即返回，main loop 馬上重新執行

**修正方案 v2（仍失敗）**: 增加等待時間到 10 秒
- ❌ 忽略了關鍵問題：**年代售票彈出成功對話框**
- ❌ 必須關閉對話框，URL 才會變化
- ❌ 等待 10 秒超時，對話框仍存在
- ❌ CDP 可穿透對話框繼續點擊 → 重複提交

**修正方案 v3（成功）**: 先關閉對話框，再等待 URL 變化

```python
await el_btn.click()
if show_debug_message:
    print("[SUBMIT] Add shopping cart button clicked successfully!")

# ✅ Check and close success dialog (Kham/Ticket.com.tw shows "加入購物車完成" dialog)
await tab.sleep(0.5)
try:
    dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button[type="button"]')
    if dialog_btn:
        if show_debug_message:
            print("[SUBMIT] Closing success dialog...")
        await dialog_btn.click()
        await tab.sleep(0.3)
except:
    pass

# Wait for URL change to prevent duplicate submission
current_url = tab.target.url
url_changed = False
for i in range(20):  # Max 10 seconds (increased from 5)
    await tab.sleep(0.5)
    new_url = tab.target.url
    if new_url != current_url:
        if show_debug_message:
            print(f"[SUBMIT] Page transitioned from {current_url}")
            print(f"[SUBMIT] to {new_url}")
        url_changed = True
        break

# If timeout, wait additional time before returning to prevent immediate re-execution
if not url_changed:
    if show_debug_message:
        print(f"[SUBMIT] WARNING: URL did not change after 10 seconds, waiting additional 2 seconds...")
    await tab.sleep(2.0)
```

**關鍵改進 v3**:
1. ✅ **先關閉成功對話框**（v3 新增，關鍵修正！）
2. ✅ 等待 URL 變化，最多 **10 秒**（從 5 秒增加）
3. ✅ 記錄 URL 是否變化的狀態
4. ✅ **超時處理**：如果 10 秒後 URL 仍未變化，額外等待 2 秒再返回
5. ✅ 防止 main loop 立即重新執行導致重複提交
6. ✅ 增加 WARNING 日誌，便於診斷異常情況

**為什麼需要 v3**:
- v1 問題：年代售票頁面跳轉較慢，5 秒可能不夠
- v2 問題：**忽略了年代售票會彈出成功對話框的特性**
- v2 問題：對話框不關閉，URL 永遠不會變化 → 10 秒超時
- v2 問題：對話框存在時，CDP 仍可穿透點擊按鈕 → 重複提交
- v3 解決：**點擊提交按鈕後立即關閉對話框** → URL 才會正常變化

**年代售票的特殊行為**:
- 點擊「加入購物車」按鈕
- ↓
- 彈出 UI Dialog：「加入購物車完成, 請於 10 分鐘內完成結帳!」
- ↓
- **必須點擊 Ok 按鈕關閉對話框**
- ↓
- URL 才會從 `UTK0202_.aspx?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx` 變化到下一頁

**修正效果**:
- 修正前：購買 2 張票 → 購物車有 4 張票或更多（重複提交）
- 修正 v1：購買 2 張票 → 購物車有 4 張票（仍失敗，等待時間不夠）
- 修正 v2：購買 2 張票 → 購物車有 4 張票（仍失敗，對話框沒關閉）
- 修正 v3：購買 2 張票 → 購物車只有 2 張票 ✅

---

## 🔍 執行流程分析

### 年代售票頁面流程架構

```
UTK0201_00 (日期選擇)
    ↓ 點擊日期
UTK0202 (票區選擇) ← 無限循環發生在這裡！
    URL: ?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx
    ↓ 選擇票區 + 驗證碼 + 點擊「下一步」
UTK0202 (票數選擇)
    URL: ?PERFORMANCE_ID=xxx&PERFORMANCE_PRICE_AREA_ID=xxx
    ↓ 填寫票數 + 驗證碼 + 點擊「加入購物車」
UTK0206 (結帳頁面)
```

### UTK0202 票區選擇頁面流程 (URL: ?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx)

**處理函數**: `nodriver_kham_main()` → line 13375-13491

1. **票區選擇** (`nodriver_kham_performance` → `nodriver_kham_area_auto_select`)
   - 使用 Bootstrap Select 或普通 dropdown
   - 根據 `area_keyword` 過濾選項
   - ✅ 已修復參數序列化問題 (line 12880-12901)

2. **驗證碼處理** (`nodriver_kham_captcha`)
   - OCR 識別驗證碼
   - 自動填入驗證碼
   - 設置 `is_captcha_sent = True`

3. **票數填寫** (line 13428-13444)
   - 自動填入 `config_dict["ticket_number"]`
   - 使用 JavaScript 設置值並觸發事件

4. **提交表單（點擊「下一步」按鈕）** (line 13460-13491)
   - 檢查 `is_captcha_sent` 是否為 True
   - 查找並點擊提交按鈕（進入票數選擇頁面）
   - ✅ **已修復按鈕選擇器，解決無限循環問題**

### UTK0202 票數選擇頁面流程 (URL: ?PERFORMANCE_ID=xxx&PERFORMANCE_PRICE_AREA_ID=xxx)

**處理函數**: `nodriver_kham_main()` → line 13503-13754

1. **檢查驗證碼是否已填寫** (line 13493-13510)
   - 若上一頁已填寫，設置 `is_captcha_sent = True`

2. **驗證碼處理** (line 13533-13536)
   - 若未填寫，執行 OCR 識別並填入

3. **票數填寫** (line 13537-13649)
   - 自動填入 `config_dict["ticket_number"]`
   - 處理多種票種（原價、身心障礙票等）

4. **提交表單（點擊「加入購物車」按鈕）** (line 13713-13754)
   - 檢查 `is_captcha_sent` 是否為 True
   - 查找並點擊提交按鈕（進入結帳頁面）
   - ✅ 已修復按鈕選擇器

---

## 📊 測試驗證

### 測試環境
- **平台**: ticket.com.tw (年代售票)
- **頁面**: UTK0202_.aspx (票種選擇頁)
- **WebDriver**: NoDriver

### 預期行為
1. ✅ Bootstrap Select 選項選擇成功
2. ✅ 驗證碼自動填入
3. ✅ 票數自動填入
4. ✅ 提交按鈕自動點擊
5. ✅ **等待 URL 變化（新增）**
6. ✅ 頁面跳轉至確認頁面
7. ✅ **不會重複執行票區選擇（新增）**
8. ✅ **購物車票數正確，不會翻倍（新增）**

### 調試輸出示例（修正 v3 後）
```
area_keyword: "3,580"
Found dropdown with 2 options
Option excluded by keyword: '輪椅席 3,580'
Option matched: '站席 3,580'
Selecting option: 站席 3,580 (value: P11X33II|952)
Found Bootstrap Select button, clicking to open dropdown...
Dropdown opened, looking for option: 站席 3,580
Found 3 menu items via CDP
  Checking option: '-請選擇-'
  Checking option: '輪椅席 3,580'
  Checking option: '站席 3,580'
  Match found! Clicking...
Successfully clicked Bootstrap Select option: 站席 3,580
Starting Kham OCR processing...
OCR answer: 4M4r
[TICKET] Ticket number set to: 2
[SUBMIT] Searching for ticket.com.tw submit button...
[SUBMIT] Submit button found, scrolling into view...
[SUBMIT] Clicking using CDP native click...
[SUBMIT] Add shopping cart button clicked successfully!
[SUBMIT] Closing success dialog...  ← v3 新增：關閉對話框
[SUBMIT] Page transitioned from https://ticket.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx
[SUBMIT] to https://ticket.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_ID=xxx&PERFORMANCE_PRICE_AREA_ID=xxx
```

**關鍵差異 v3**:
- ✅ **新增「Closing success dialog」訊息**（關鍵修正）
- ✅ 對話框被關閉後，URL 才會正常變化
- ✅ 新增 URL 變化訊息，確認頁面已跳轉
- ✅ 不會再重複執行票區選擇
- ✅ 只點擊一次提交按鈕
- ✅ 購物車票數正確（不會有 4 張或更多）

---

## 🔗 相關文件

- **Bootstrap Select 序列化問題**: `docs/08-troubleshooting/kham_nodriver_dropdown_serialization.md`
- **NoDriver API 指南**: `docs/06-api-reference/nodriver_api_guide.md`
- **Chrome API 指南**: `docs/06-api-reference/chrome_api_guide.md`
- **除錯方法論**: `docs/07-testing-debugging/debugging_methodology.md`

---

## 📌 技術總結

### NoDriver 參數傳遞限制

| 方法 | 是否可傳參 | 備註 |
|------|-----------|------|
| `evaluate()` | ⚠️ 有限支援 | 簡單類型可以，中文字符可能失敗 |
| `apply()` | ⚠️ 有限支援 | 建議使用 f-string 嵌入值 |
| 直接 JavaScript | ✅ 推薦 | 使用 f-string 將值嵌入代碼 |

### 最佳實踐

1. **避免參數序列化**: 使用 f-string 將值嵌入 JavaScript 代碼
2. **使用 CDP 原生方法**: `query_selector`, `apply()`, `evaluate()`
3. **增加 Fallback 機制**: 多個選擇器，提高兼容性
4. **詳細調試輸出**: 使用 `[TAG]` 前綴便於搜尋

---

**修復版本**: 2025-10-09
**影響檔案**: `src/nodriver_tixcraft.py`
**影響行數**:
- 12880-12901 (Bootstrap Select 參數序列化)
- 13460-13516 (票區選擇頁面提交按鈕 + 對話框關閉 + URL 等待 v3)
- 13750-13806 (票數頁面提交按鈕 + 對話框關閉 + URL 等待 v3)

**影響函數**: `nodriver_kham_area_auto_select()`, `nodriver_kham_main()`

**完整修復歷程**:
1. **2025-10-09 初次修復**: Bootstrap Select 參數序列化問題 (line 12880-12901)
2. **2025-10-09 追加修復 1**: 票區選擇頁面提交按鈕選擇器錯誤，解決無限循環 (line 13460-13491)
3. **2025-10-09 追加修復 2 (v1)**: 兩個頁面增加 URL 等待邏輯 5 秒（失敗，時間不夠）
4. **2025-10-09 追加修復 2 (v2)**: 增加等待時間到 10 秒 + 超時緩衝 2 秒（失敗，對話框沒關閉）
5. **2025-10-09 追加修復 2 (v3)**: 點擊提交後先關閉成功對話框，再等待 URL 變化，解決重複提交 ✅
