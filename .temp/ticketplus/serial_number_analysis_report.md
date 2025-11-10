# TicketPlus 折價券輸入功能分析報告

**報告日期**: 2025-11-08
**Issue**: #37 - 遠大無法自動填入問題答案
**分析者**: Claude Code
**狀態**: 待評估實作

---

## 1. 問題描述

### 使用者回報
- **平台**: 遠大售票 (TicketPlus)
- **操作**: 加購福利 / 優惠票券
- **問題**: 無法自動填入折價券代碼（優惠序號 / 加購序號）
- **預期**: 應自動填入預設折價券代碼後搶票

### 影響範圍
- 遠大售票所有需要折價券代碼輸入的活動
  - 優惠序號（如遠傳優惠票）
  - 加購序號（如簽名會加購）
  - **註**: 兩者本質相同，均視為折價券代碼

---

## 2. HTML 結構分析

### 2.1 優惠序號輸入框 (area2.html)
```html
<!-- 檔案: .temp/ticketplus/area2.html -->
<!-- URL: https://ticketplus.com.tw/order/.../... -->

<div data-v-9c1a94a8="" class="exclusive-code">
  <form data-v-9c1a94a8="" novalidate="novalidate" class="v-form">
    <div data-v-9c1a94a8="" class="label">優惠序號</div>
    <div data-v-9c1a94a8="" class="v-input theme--light v-text-field ...">
      <div class="v-input__control">
        <div class="v-input__slot">
          <fieldset aria-hidden="true">
            <legend><span class="notranslate">​</span></legend>
          </fieldset>
          <div class="v-text-field__slot">
            <input id="input-493" placeholder="請輸入優惠序號" type="text">
          </div>
        </div>
        <div class="v-text-field__details">...</div>
      </div>
    </div>
  </form>
</div>
```

**關鍵元素**:
- 標籤文字: `優惠序號`
- Input ID: `input-493` (動態生成，不可靠)
- Placeholder: `請輸入優惠序號`
- 父容器 class: `exclusive-code`

### 2.2 加購序號輸入框 (area1.html)
```html
<!-- 檔案: .temp/ticketplus/area1.html -->
<!-- URL: https://ticketplus.com.tw/order/.../... -->

<div data-v-9c1a94a8="" class="exclusive-code">
  <form data-v-9c1a94a8="" novalidate="novalidate" class="v-form">
    <div data-v-9c1a94a8="" class="label">加購序號</div>
    <div data-v-9c1a94a8="" class="v-input theme--light v-text-field ...">
      <div class="v-input__control">
        <div class="v-input__slot">
          <fieldset aria-hidden="true">
            <legend><span class="notranslate">​</span></legend>
          </fieldset>
          <div class="v-text-field__slot">
            <input id="input-67" placeholder="請輸入加購序號" type="text">
          </div>
        </div>
        <div class="v-text-field__details">...</div>
      </div>
    </div>
  </form>
</div>
```

**關鍵元素**:
- 標籤文字: `加購序號`
- Input ID: `input-67` (動態生成，不可靠)
- Placeholder: `請輸入加購序號`
- 父容器 class: `exclusive-code`

### 2.3 共同特徵
1. **父容器**: `div.exclusive-code`
2. **標籤位置**: `div.label` (包含「優惠序號」或「加購序號」文字)
3. **Input 位置**: `.v-text-field__slot input[type="text"]`
4. **動態 ID**: Vue.js 生成的動態 ID，不可依賴
5. **⚠️ 動態展開**: 折價券輸入欄位可能在點擊「+號」或展開按鈕後才出現，需等待元素載入

---

## 3. 現有實作檢查

### 3.1 目前程式碼位置
- **主檔案**: `src/nodriver_tixcraft.py`
- **相關函數**:
  - `nodriver_ticketplus_order()` - Line 6373 (訂單處理主函數)
  - `nodriver_ticketplus_order_exclusive_code()` - Line 6613 (優惠碼處理)

### 3.2 目前實作狀況
```python
# Line 6613-6628
async def nodriver_ticketplus_order_exclusive_code(tab, config_dict, fail_list):
    """處理活動專屬代碼 - 直接跳過處理"""
    show_debug_message = config_dict["advanced"]["verbose"]

    # 檢查暫停狀態
    if await check_and_handle_pause(config_dict):
        return False, fail_list, False

    if show_debug_message:
        print("Skipping discount code processing")

    # 直接返回預設值：未送出答案，原有失敗清單，無彈窗問題
    is_answer_sent = False
    is_question_popup = False

    return is_answer_sent, fail_list, is_question_popup
```

**現況**:
- ✅ 函數已存在
- ❌ 功能未實作 (直接跳過處理)
- ❌ 無讀取設定檔邏輯
- ❌ 無輸入折價券代碼邏輯

### 3.3 呼叫位置
```python
# Line 6484 (nodriver_ticketplus_order 函數內)
# 處理優惠碼
is_answer_sent, ticketplus_dict["fail_list"], is_question_popup = \
    await nodriver_ticketplus_order_exclusive_code(tab, config_dict, ticketplus_dict["fail_list"])
```

**呼叫時機**: 票種選擇成功後，提交表單之前

---

## 4. 設定檔設計

### 4.1 建議的 settings.json 結構

**採用單一欄位設計**（優惠序號與加購序號本質相同）

```json
{
  "advanced": {
    "ticketplus_account": "0911***551",
    "ticketplus_password": "",
    "ticketplus_password_plaintext": "",
    "ticketplus_discount_code": ""
  }
}
```

**設計理念**:
- 優惠序號和加購序號本質上是相同的折價券代碼
- 使用單一欄位 `ticketplus_discount_code` 即可涵蓋所有情境
- 程式自動偵測頁面上的折價券輸入欄位並填入
- 無論是「優惠序號」或「加購序號」欄位，都會填入相同的代碼

**優點**:
- ✅ 設定簡單，只需一個欄位
- ✅ 使用者不需要區分優惠序號或加購序號
- ✅ 程式自動偵測並填入所有符合的輸入框
- ✅ 支援同一頁面有多個折價券欄位的情境

**使用情境**:
- 單一優惠序號 → 自動填入
- 單一加購序號 → 自動填入
- 同時有優惠序號和加購序號 → 兩個欄位都填入相同代碼

### 4.2 www/settings.html 對應修改

需要在 `www/settings.html` 新增輸入框（TicketPlus 區塊）：

```html
<!-- TicketPlus 帳號設定區塊 -->
<div class="form-group">
  <label for="ticketplus_discount_code">折價券代碼:</label>
  <input type="text" id="ticketplus_discount_code" name="ticketplus_discount_code"
         placeholder="優惠序號 / 加購序號" class="form-control">
  <small class="form-text text-muted">
    適用於所有類型的折價券代碼（優惠序號、加購序號等），程式會自動偵測並填入所有符合的輸入欄位
  </small>
</div>
```

---

## 5. 實作建議

### 5.1 選擇器策略

#### JavaScript 選擇器（推薦）
```javascript
// 策略 1: 透過標籤文字偵測（使用關鍵字匹配）
const labelDivs = document.querySelectorAll('.exclusive-code .label');
const keywords = ['序號', '加購', '優惠'];

for (let label of labelDivs) {
  const labelText = label.textContent.trim();
  const container = label.closest('.exclusive-code');
  const input = container.querySelector('.v-text-field__slot input[type="text"]');

  // 檢查是否包含任一關鍵字
  const hasKeyword = keywords.some(keyword => labelText.includes(keyword));
  if (hasKeyword && input) {
    // 填入折價券代碼
    input.value = discountCode;
  }
}

// 策略 2: 透過 placeholder 偵測（備用）
const inputs = document.querySelectorAll('.exclusive-code input[type="text"]');
for (let input of inputs) {
  const placeholder = input.getAttribute('placeholder');
  if (placeholder) {
    // 檢查 placeholder 是否包含任一關鍵字
    const hasKeyword = keywords.some(keyword => placeholder.includes(keyword));
    if (hasKeyword) {
      // 填入折價券代碼
      input.value = discountCode;
    }
  }
}
```

**關鍵字匹配策略**:
- ✅ 「序號」- 涵蓋「優惠序號」、「加購序號」、「專屬序號」等
- ✅ 「加購」- 涵蓋「加購序號」、「加購碼」等
- ✅ 「優惠」- 涵蓋「優惠序號」、「優惠碼」等
- 📝 使用 `Array.some()` 檢查是否包含任一關鍵字，提高靈活性

#### NoDriver 選擇器（備用）
```python
# 策略 1: CSS 選擇器
input_element = await tab.query_selector('.exclusive-code input[type="text"]')

# 策略 2: XPath (更精確)
input_element = await tab.find('//div[@class="label"][contains(text(),"優惠序號")]/..//input[@type="text"]')
```

### 5.2 實作流程

```python
async def nodriver_ticketplus_order_exclusive_code(tab, config_dict, fail_list):
    """處理折價券代碼輸入 - 使用關鍵字匹配策略

    注意: 此函數在 nodriver_ticketplus_order() 中被呼叫時，
    應該已經處理完展開面板的邏輯，折價券輸入欄位應該已經可見。
    如果欄位尚未展開，可能需要在呼叫此函數前先觸發展開動作。
    """
    show_debug_message = config_dict["advanced"]["verbose"]

    # 檢查暫停狀態
    if await check_and_handle_pause(config_dict):
        return False, fail_list, False

    # 讀取設定
    discount_code = config_dict["advanced"].get("ticketplus_discount_code", "").strip()

    # 檢查是否有折價券代碼需要填入
    if not discount_code:
        if show_debug_message:
            print("No discount code configured, skipping")
        return False, fail_list, False

    if show_debug_message:
        print("Processing discount code input...")

    is_answer_sent = False
    is_question_popup = False

    try:
        # 使用 JavaScript 偵測並填入折價券代碼（使用關鍵字匹配）
        result = await tab.evaluate(f'''
            (function() {{
                const discountCode = "{discount_code}";
                const keywords = ['序號', '加購', '優惠'];
                let filledCount = 0;

                // 策略 1: 透過標籤文字偵測（使用關鍵字匹配）
                const labelDivs = document.querySelectorAll('.exclusive-code .label');
                for (let label of labelDivs) {{
                    const labelText = label.textContent.trim();
                    const container = label.closest('.exclusive-code');
                    const input = container?.querySelector('.v-text-field__slot input[type="text"]');

                    if (!input) continue;

                    // 檢查是否包含任一關鍵字
                    const hasKeyword = keywords.some(keyword => labelText.includes(keyword));
                    if (hasKeyword && discountCode) {{
                        input.value = discountCode;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        filledCount++;
                        console.log(`[TicketPlus] 已填入折價券代碼 (標籤: ${{labelText}}):`, discountCode);
                    }}
                }}

                // 策略 2: 如果策略1失敗，透過 placeholder 偵測
                if (filledCount === 0) {{
                    const inputs = document.querySelectorAll('.exclusive-code input[type="text"]');
                    for (let input of inputs) {{
                        const placeholder = input.getAttribute('placeholder');

                        if (placeholder) {{
                            const hasKeyword = keywords.some(keyword => placeholder.includes(keyword));
                            if (hasKeyword && discountCode) {{
                                input.value = discountCode;
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                filledCount++;
                                console.log(`[TicketPlus] 已填入折價券代碼 (placeholder: ${{placeholder}}):`, discountCode);
                            }}
                        }}
                    }}
                }}

                return {{
                    success: filledCount > 0,
                    filledCount: filledCount,
                    message: filledCount > 0 ? `成功填入 ${{filledCount}} 個折價券代碼` : '未找到折價券輸入欄位'
                }};
            }})();
        ''')

        # 解析結果
        result = util.parse_nodriver_result(result)

        if isinstance(result, dict):
            is_answer_sent = result.get('success', False)
            if show_debug_message:
                if is_answer_sent:
                    print(f"[SUCCESS] {result.get('message', '')}")
                else:
                    print(f"[INFO] {result.get('message', '')}")

    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] Discount code processing failed: {exc}")

    return is_answer_sent, fail_list, is_question_popup
```

### 5.3 測試案例

1. **基本功能測試**
   - 目標網址: 有折價券欄位的活動
   - 設定 `ticketplus_discount_code`
   - **前置條件**: 確保折價券輸入欄位已展開（可能需要點擊「+號」按鈕）
   - 驗證: 折價券欄位是否自動填入

2. **關鍵字匹配測試**
   - 測試「優惠序號」欄位 → 應成功填入
   - 測試「加購序號」欄位 → 應成功填入
   - 測試其他包含「序號」、「加購」、「優惠」關鍵字的欄位 → 應成功填入

3. **動態展開測試**
   - 確認折價券欄位在點擊「+號」後才出現
   - 驗證: 函數是否在欄位展開後正確填入

4. **多欄位測試**
   - 目標: 同時有多個折價券欄位的活動（如優惠序號 + 加購序號）
   - 驗證: 所有符合關鍵字的欄位是否都填入相同代碼

---

## 6. 風險評估

### 6.1 技術風險
- **低風險**: HTML 結構簡單，選擇器穩定
- **Vue.js 響應**: 需要觸發 `input` 和 `change` 事件
- **動態 ID**: 已避免依賴動態 ID
- **動態展開**: 需確保在呼叫函數前，折價券欄位已經展開可見

### 6.2 關鍵字匹配風險
- **誤匹配風險**: 低 - 關鍵字「序號」、「加購」、「優惠」組合已涵蓋大部分情境
- **漏匹配風險**: 中 - 如果出現新的命名方式（如「兌換碼」），需要擴充關鍵字清單
- **建議**: 如發現新的欄位名稱，可在程式碼中擴充 `keywords` 陣列

### 6.3 相容性風險
- **其他平台**: 修改僅影響 TicketPlus，不影響其他平台
- **現有功能**: 不破壞現有流程（僅新增折價券填入步驟）

### 6.4 使用者體驗風險
- **設定簡單**: 單一欄位設計，使用者易於理解
- **誤填風險**: 低 - 程式會自動將相同代碼填入所有符合的欄位

---

## 7. 實作優先級與建議

### 7.1 設計決策
**採用方案**: **單一欄位 + 關鍵字匹配**

理由:
1. ✅ 設定簡單 - 使用者只需填寫一個欄位
2. ✅ 自動偵測 - 程式自動匹配所有符合關鍵字的欄位
3. ✅ 靈活性高 - 支援「優惠序號」、「加購序號」等各種命名
4. ✅ 易於維護 - 如出現新的欄位名稱，僅需擴充關鍵字清單

### 7.2 實作步驟
1. ✅ 分析 HTML 結構 (已完成)
2. ✅ 檢查現有實作 (已完成)
3. ⏳ 修改 `settings.json` (新增 1 個欄位: `ticketplus_discount_code`)
4. ⏳ 修改 `www/settings.html` (新增折價券代碼輸入框)
5. ⏳ 實作 `nodriver_ticketplus_order_exclusive_code()` 函數（使用關鍵字匹配）
6. ⏳ 確認呼叫時機（確保折價券欄位已展開）
7. ⏳ 測試驗證（真實活動或模擬環境）

### 7.3 預估工時
- **設定檔修改**: 10 分鐘
- **函數實作**: 30 分鐘
- **測試驗證**: 30 分鐘（需要真實活動）
- **總計**: 約 1-1.5 小時

---

## 8. 待確認事項

1. **欄位命名確認**:
   - 使用 `ticketplus_discount_code` 作為欄位名稱，是否適當？
   - 中文顯示為「折價券代碼」，是否符合使用者習慣？

2. **關鍵字清單確認**:
   - 目前關鍵字: `['序號', '加購', '優惠']`
   - 是否需要新增其他關鍵字（如「兌換碼」、「折扣碼」）？

3. **動態展開邏輯確認**:
   - 確認 `nodriver_ticketplus_order()` 是否已處理展開邏輯
   - 確認此函數被呼叫時，折價券欄位是否已可見

4. **測試環境確認**:
   - 是否有可用的測試活動（包含折價券欄位）？
   - 是否需要準備測試折價券代碼？

5. **多欄位行為確認**:
   - 如果頁面同時有「優惠序號」和「加購序號」，填入相同代碼，是否符合預期？
   - 或者需要區分兩者（如果需要，可能需要調整為多欄位設計）？

---

## 9. 附錄

### 9.1 相關檔案清單
- `src/nodriver_tixcraft.py` - TicketPlus 主要實作
- `src/settings.json` - 設定檔範本
- `www/settings.html` - 使用者介面
- `.temp/ticketplus/area1.html` - 加購序號範例
- `.temp/ticketplus/area2.html` - 優惠序號範例

### 9.2 參考資料
- Issue #37: 遠大無法自動填入問題答案
- TicketPlus 官網: https://ticketplus.com.tw/
- Vue.js 表單處理文件

---

**報告結束** - 等待使用者評估與決策
