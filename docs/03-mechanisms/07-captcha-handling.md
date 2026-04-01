# Stage 7: 驗證碼處理機制

**文件說明**：說明搶票系統的驗證碼處理機制、圖形/問答驗證碼辨識與自動填寫策略
**最後更新**：2026-03-09

---

## 概述

**目的**：自動辨識並填寫驗證碼（圖形/問答）
**輸入**：驗證碼圖片或問題文字 + OCR 引擎 + 使用者答案
**輸出**：填入驗證碼答案 + 提交表單（可選）
**關鍵技術**：
- **通用 OCR 模型**：內建 ONNX 模型（svtr_tiny），準確率 99-100%（TixCraft/iBon/KHAM）
- **ddddocr OCR 引擎**：官方模型 fallback 及 FunOne 平台使用
- **問答匹配引擎**：KKTIX 問答式驗證碼
- **自動答題機制**：智慧推測答案（KKTIX, v2.0+）
- **fail_list 機制**：記錄失敗答案，避免重複錯誤
- **人類化延遲**：隨機延遲模擬真人行為
- **重試機制**：填寫失敗時自動重試

---

## 驗證碼類型

### 1. 圖形驗證碼（OCR）

**平台**：TixCraft, iBon, KHAM
**特徵**：4-6 位數字/英文字母圖片
**辨識方式**：通用 OCR 模型（優先）/ ddddocr OCR 引擎（fallback）

**OCR 模型選擇邏輯**：
```
ocr_captcha.use_universal=true（預設）
  └─ src/assets/model/universal/ 存在？
      ├─ [是] → 使用通用模型（準確率 99-100%）
      └─ [否] → Fallback 到 ddddocr 官方模型
ocr_captcha.use_universal=false
  └─ 使用 ddddocr 官方模型（beta=true 時使用 beta 模型）
```

**各平台準確率**：
| 平台 | 通用模型 | ddddocr 官方 | 備注 |
|------|---------|-------------|------|
| TixCraft | 99% | ~85-90% | 優先通用模型 |
| iBon | 100% | ~85-90% | 優先通用模型 |
| KHAM | 99.67% | ~85-90% | 優先通用模型 |
| FunOne | 75.67% | ~85-90% | 維持 ddddocr（set_ranges(5)） |

### 2. 問答式驗證碼

**平台**：KKTIX
**特徵**：文字問題 + 選擇答案/自由輸入
**辨識方式**：關鍵字匹配 + 使用者自訂答案

---

## 核心流程（圖形驗證碼 - OCR）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 檢查 OCR 引擎可用性                                       │
│    ├─ ddddocr 模組已載入？[是] → 繼續                      │
│    └─ ddddocr 不可用（ARM）？[是] → 等待手動輸入           │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 擷取驗證碼圖片                                           │
│    ├─ Canvas 方式（TixCraft, KHAM）                        │
│    │   └─ document.getElementById + canvas.toDataURL()     │
│    ├─ Shadow DOM 方式（iBon）                              │
│    │   └─ DOMSnapshot + CSS screenshot                     │
│    └─ NonBrowser 方式（外部伺服器）                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. OCR 辨識                                                  │
│    ├─ ddddocr.classification(image_base64)                  │
│    ├─ 檢查辨識結果長度（4-6 字元）                         │
│    └─ 長度不符？→ 重新載入驗證碼圖片                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 填入驗證碼答案                                           │
│    ├─ 人類化延遲（0.1-0.3 秒）                             │
│    ├─ input.focus() → 逐字輸入 → input.blur()             │
│    └─ 觸發 input/change 事件                               │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 提交表單（可選）                                         │
│    ├─ [force_submit = true]  → 自動提交                   │
│    └─ [force_submit = false] → 等待手動確認               │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心流程（問答式驗證碼 - KKTIX）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 檢測問題元素                                             │
│    ├─ 查詢 'div.custom-captcha-inner p'                    │
│    └─ 取得問題文字（questionText）                         │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 取得答案列表                                             │
│    ├─ 讀取使用者自訂答案（user_guess_string）              │
│    ├─ 讀取線上答案檔案（MAXBOT_ANSWER_ONLINE_FILE）       │
│    └─ [auto_guess_options=true] → 自動推測答案            │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 選擇答案（fail_list 機制）                               │
│    ├─ 遍歷 answer_list                                      │
│    ├─ 跳過已失敗答案（fail_list 中的項目）                 │
│    └─ 選擇第一個未失敗的答案                               │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 填入答案（人類化延遲 + 重試）                            │
│    ├─ 隨機延遲 0.3-1.0 秒                                  │
│    ├─ input.focus() → 逐字輸入 → input.blur()             │
│    ├─ 填寫失敗？→ 重試最多 3 次                           │
│    └─ 驗證 input.value 是否正確填入                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 點擊下一步按鈕                                           │
│    ├─ 查詢 'div.register-new-next-button-area > button'    │
│    ├─ 人類化延遲（0.2-0.5 秒）                             │
│    └─ button.click()                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 關鍵程式碼片段

### 1. OCR 圖片擷取（Canvas 方式 - TixCraft）

**範例來源**：TixCraft (`nodriver_tixcraft.py:3737-3770`)

```python
# 使用 JavaScript 從 canvas 取得圖片
image_id = 'TicketForm_verifyCode-image'
form_verifyCode_base64 = await tab.evaluate(f'''
    (function() {{
        var canvas = document.createElement('canvas');
        var context = canvas.getContext('2d');
        var img = document.getElementById('{image_id}');
        if(img) {{
            canvas.height = img.naturalHeight;
            canvas.width = img.naturalWidth;
            context.drawImage(img, 0, 0);
            return canvas.toDataURL();  // 返回 Base64 圖片
        }}
        return null;
    }})();
''')

if form_verifyCode_base64:
    # 解碼 Base64 資料
    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])

# Fallback: 若 Canvas 方式失敗，使用外部伺服器
if img_base64 is None:
    if not Captcha_Browser is None:
        print("Failed to get image from canvas, using fallback: NonBrowser")
        img_base64 = base64.b64decode(Captcha_Browser.request_captcha())
```

**關鍵設計**：
- **Canvas 方式**：從頁面 `<img>` 元素繪製到 canvas，取得 Base64 圖片
- **雙重回退**：Canvas 失敗時，使用外部伺服器（NonBrowser）

---

### 2. ddddocr OCR 辨識

**範例來源**：TixCraft (`nodriver_tixcraft.py:3772-3778`)

```python
# OCR 識別
if not img_base64 is None:
    try:
        ocr_answer = ocr.classification(img_base64)  # ddddocr 辨識
    except Exception as exc:
        if show_debug_message:
            print("OCR recognition failed:", exc)
```

**ddddocr 使用方式**：
```python
import ddddocr

# 初始化 OCR 引擎（官方模型，fallback 用）
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)

# 辨識圖片（傳入 bytes）
result = ocr.classification(image_bytes)  # 返回字串，如 "A3B7"
```

**注意事項**：
- **ARM 平台不支援**：ddddocr 僅支援 x86/x64，ARM 需等待手動輸入
- **官方模型準確率**：約 85-90%；通用 OCR 模型準確率 99-100%（TixCraft/iBon/KHAM）
- **Beta 模型**：`ocr_captcha.beta=true` 可啟用 ddddocr beta 模型（僅影響 fallback 路徑）
- **通用模型優先**：`ocr_captcha.use_universal=true`（預設）時優先使用內建通用模型

---

### 3. 問答式驗證碼處理（KKTIX）

**範例來源**：KKTIX (`nodriver_tixcraft.py:1182-1221`)

```python
# 批次檢查頁面元素狀態
elements_check = await tab.evaluate('''
    (function() {
        return {
            hasQuestion: !!document.querySelector('div.custom-captcha-inner p'),
            hasInput: !!document.querySelector('div.custom-captcha-inner > div > div > input'),
            hasButtons: document.querySelectorAll('div.register-new-next-button-area > button').length,
            questionText: document.querySelector('div.custom-captcha-inner p')?.innerText || ''
        };
    })();
''')
elements_check = util.parse_nodriver_result(elements_check)

is_question_popup = False
if elements_check and elements_check.get('hasQuestion'):
    question_text = elements_check.get('questionText', '')

    if len(question_text) > 0:
        is_question_popup = True
        write_question_to_file(question_text)  # 記錄問題到檔案

        # 1. 取得答案列表
        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list) == 0:
            if config_dict["advanced"]["auto_guess_options"]:
                # 2. 自動推測答案
                answer_list = util.get_answer_list_from_question_string(None, question_text)

        # 3. fail_list 機制：跳過已失敗的答案
        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:  # ⭐ 跳過失敗答案
                inferred_answer_string = answer_item
                break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("question_text:", question_text)
            print("answer_list:", answer_list)
            print("fail_list:", fail_list)  # 顯示失敗歷史
```

**fail_list 機制**：
- **用途**：記錄已嘗試但失敗的答案，避免重複錯誤
- **運作**：每次提交失敗後，將答案加入 fail_list
- **效果**：下次選擇答案時，自動跳過 fail_list 中的項目

---

### 4. 人類化延遲 + 重試機制（KKTIX）

**範例來源**：KKTIX (`nodriver_tixcraft.py:1224-1270`)

```python
# 增強版答案填寫流程，包含重試機制
if len(inferred_answer_string) > 0 and elements_check.get('hasInput'):
    success = False
    max_retries = 3

    for retry_count in range(max_retries):
        if show_debug_message and retry_count > 0:
            print(f"Captcha filling retry {retry_count}/{max_retries}")

        try:
            # ⭐ 人類化延遲：0.3-1秒隨機延遲
            human_delay = random.uniform(0.3, 1.0)
            await tab.sleep(human_delay)

            # 填寫驗證碼答案
            fill_result = await tab.evaluate(f'''
                (function() {{
                    const input = document.querySelector('div.custom-captcha-inner > div > div > input');
                    if (!input) {{
                        return {{ success: false, error: "Input not found" }};
                    }}

                    // 確保輸入框可見和可用
                    if (input.disabled || input.readOnly) {{
                        return {{ success: false, error: "Input is disabled or readonly" }};
                    }}

                    // ⭐ 模擬人類打字（逐字輸入）
                    input.focus();
                    input.value = "";

                    const answer = "{inferred_answer_string}";
                    for (let i = 0; i < answer.length; i++) {{
                        input.value += answer[i];
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}

                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    input.blur();

                    return {{
                        success: true,
                        value: input.value,
                        focused: document.activeElement === input
                    }};
                }})();
            ''')

            fill_result = util.parse_nodriver_result(fill_result)

            if fill_result and fill_result.get('success'):
                if show_debug_message:
                    print(f"Captcha filled successfully: {fill_result.get('value')}")
                success = True
                break  # 成功，跳出重試迴圈
            else:
                if show_debug_message:
                    print(f"Captcha filling failed: {fill_result.get('error')}")
                # 繼續重試

        except Exception as exc:
            if show_debug_message:
                print(f"Captcha filling exception: {exc}")
            # 繼續重試
```

**人類化延遲策略**：
- **填寫前延遲**：0.3-1.0 秒（避免立即填寫被偵測）
- **逐字輸入**：模擬真人逐字打字
- **點擊按鈕延遲**：0.2-0.5 秒（避免立即提交）

**重試策略**：
- **最多重試 3 次**
- 填寫失敗時自動重試（input 未找到、disabled 等）
- 重試間有隨機延遲

---

### 5. Shadow DOM 圖片擷取（iBon）

**範例來源**：iBon (`nodriver_tixcraft.py:9643-9730`)

```python
async def nodriver_ibon_get_captcha_image_from_shadow_dom(tab, config_dict):
    """
    從 iBon 的 closed Shadow DOM 中擷取驗證碼圖片
    使用 DOMSnapshot + CSS screenshot 方式
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        # Step 1: 使用 DOMSnapshot 平坦化 Shadow DOM
        dom_snapshot_result = await tab.send(zendriver.cdp.dom_snapshot.capture_snapshot(
            computed_styles=[]
        ))

        documents = dom_snapshot_result[0]
        strings = dom_snapshot_result[1]

        # Step 2: 搜尋驗證碼圖片元素（在 Shadow DOM 內）
        captcha_backend_node_id = None
        for doc in documents:
            layout = doc.layout
            for idx, node_id in enumerate(layout.node_index):
                # 檢查節點名稱
                if idx < len(layout.styles):
                    node_name = strings[layout.styles[idx][0]] if layout.styles[idx] else None

                    # iBon 驗證碼圖片通常在 img.captcha-image 或類似 class
                    if node_name and 'captcha' in node_name.lower():
                        captcha_backend_node_id = layout.backend_node_id[idx]
                        if show_debug_message:
                            print(f"Found captcha image node: {node_name}")
                        break

        if not captcha_backend_node_id:
            if show_debug_message:
                print("Captcha image not found in Shadow DOM")
            return None

        # Step 3: 使用 CDP Page.captureScreenshot 擷取元素圖片
        screenshot_result = await tab.send(zendriver.cdp.page.captureScreenshot(
            format_='png',
            from_surface=True,
            capture_beyond_viewport=False
        ))

        img_base64 = base64.b64decode(screenshot_result)
        return img_base64

    except Exception as exc:
        if show_debug_message:
            print(f"Shadow DOM captcha extraction error: {exc}")
        return None
```

**關鍵技術**：
- **DOMSnapshot**：平坦化 closed Shadow DOM
- **backend_node_id**：定位 Shadow DOM 內的元素
- **Page.captureScreenshot**：擷取元素截圖

---

## 平台實作差異

### 標準驗證碼機制

| 平台 | 驗證碼類型 | 擷取方式 | OCR 引擎 | 特殊處理 | 函數名稱 | 完成度 |
|------|-----------|---------|---------|---------|---------|--------|
| **KKTIX** | 問答式 | DOM 查詢 | ❌ 不需要 | fail_list 機制 | `nodriver_kktix_reg_captcha()` | 100% ✅ |
| **TixCraft** | 圖形 4字 | Canvas | ddddocr | NonBrowser fallback | `nodriver_tixcraft_get_ocr_answer()` | 100% ✅ |
| **iBon** | 圖形 4字 | Shadow DOM | ddddocr | DOMSnapshot + Screenshot | `nodriver_ibon_captcha()` | 100% ✅ |
| **KHAM** | 圖形 4字 | Canvas | ddddocr | 3域名變體支援 | `nodriver_kham_captcha()` | 100% ✅ |
| **TicketPlus** | ❌ 無標準驗證碼 | - | - | - | - | N/A |

**程式碼位置**（`nodriver_tixcraft.py`）：
- **KKTIX**: Line 1171 (`nodriver_kktix_reg_captcha`, 問答式主要範例) ⭐
- **TixCraft**: Line 3724 (`nodriver_tixcraft_get_ocr_answer`, OCR 主要範例) ⭐
- iBon: Line 9643 (`nodriver_ibon_get_captcha_image_from_shadow_dom`, Shadow DOM 範例)
- KHAM: Line 13101 (`nodriver_kham_captcha`)

### 特殊功能：優惠代碼填寫（非驗證碼）

| 平台 | 功能類型 | 使用場景 | 實作方式 | 函數名稱 | 完成度 |
|------|---------|---------|---------|---------|--------|
| **TicketPlus** | 優惠序號自動填寫 | 特定活動要求先輸入優惠序號才能購票 | 關鍵字偵測 + JavaScript 注入 + Vue.js 事件 | `nodriver_ticketplus_order_exclusive_code()` | 100% ✅ |
| **KKTIX** | 會員序號自動填寫 | 特定活動需要會員序號資格驗證 | Class 選擇器 + JavaScript 注入 + AngularJS 綁定 | `nodriver_kktix_order_member_code()` | 100% ✅ |

**說明**：
- **不是驗證碼**：優惠代碼並非安全驗證機制，而是活動購票資格限制
- **觸發條件**：僅在特定活動頁面出現代碼欄位時才需要
- **設定方式**：`settings.json` → `advanced.discount_code`（通用設定）
- **TicketPlus 特性**：
  - 關鍵字偵測：自動偵測包含「序號」、「加購」、「優惠」等關鍵字的欄位
  - Vue.js 事件：觸發 `input` + `change` 事件
  - 程式碼位置：`nodriver_tixcraft.py:6794`
- **KKTIX 特性**：
  - 選擇器策略：`input.member-code` + `input[ng-model*="member_codes"]`（雙重保障）
  - AngularJS 綁定：觸發 `input` + `change` + `blur` 事件 + `scope.$apply()`
  - 插入時機：票數選擇完成後、播放音效之前（`nodriver_kktix_reg_new_main:2188`）
  - 程式碼位置：`nodriver_tixcraft.py:2625`
- **通用設計**：使用單一 `discount_code` 設定支援所有平台，程式自動偵測欄位類型

---

## 實作檢查清單

- [ ] **OCR 引擎整合**
  - [ ] 初始化 ddddocr 引擎
  - [ ] ARM 平台檢測與回退
  - [ ] OCR 結果驗證（長度檢查）

- [ ] **圖片擷取**
  - [ ] Canvas 方式（TixCraft, KHAM）
  - [ ] Shadow DOM 方式（iBon）
  - [ ] NonBrowser fallback

- [ ] **問答式驗證碼（KKTIX）**
  - [ ] 問題文字擷取
  - [ ] 答案列表取得（user_guess_string + auto_guess）
  - [ ] fail_list 機制實作

- [ ] **人類化行為**
  - [ ] 填寫前隨機延遲（0.3-1.0 秒）
  - [ ] 逐字輸入模擬
  - [ ] 點擊按鈕前延遲（0.2-0.5 秒）

- [ ] **重試機制**
  - [ ] 填寫失敗重試（最多 3 次）
  - [ ] OCR 辨識失敗重新載入圖片
  - [ ] 長度不符時重新載入

- [ ] **除錯輸出**
  - [ ] Verbose 模式除錯訊息
  - [ ] OCR 辨識結果日誌
  - [ ] 問答匹配日誌

- [ ] **錯誤處理**
  - [ ] 元素未找到時的處理
  - [ ] OCR 引擎異常捕獲
  - [ ] 異常時等待手動輸入

---

## 常見問題 (FAQ)

### Q1: ddddocr 在 ARM 平台無法使用怎麼辦？

**A**: ddddocr 僅支援 x86/x64 架構，ARM 平台（Apple M1/M2）需要手動輸入驗證碼。

**解決方案**：
1. **檢測 ARM 平台**：
```python
if ocr is None:
    print("[TIXCRAFT OCR] ddddocr component unavailable, you may be running on ARM")
    # 等待手動輸入
```

2. **替代方案**：
   - **方案 1**：使用 x86/x64 電腦執行程式
   - **方案 2**：使用 Docker (x86 模擬)
   - **方案 3**：等待 ddddocr ARM 版本發布

**參考文件**：詳見內部疑難排解文件

---

### Q2: fail_list 機制如何運作？

**A**: fail_list 記錄已嘗試但失敗的答案，避免重複錯誤。

**運作流程**：
```
1. 初始狀態：fail_list = []
2. 第一次嘗試：answer = "A" → 提交失敗
3. 更新 fail_list：fail_list = ["A"]
4. 第二次嘗試：跳過 "A"，選擇 "B" → 提交成功 ✓
```

**實作**：
```python
inferred_answer_string = ""
for answer_item in answer_list:
    if not answer_item in fail_list:  # 跳過失敗答案
        inferred_answer_string = answer_item
        break

# 提交失敗時，將答案加入 fail_list
if submit_failed:
    fail_list.append(inferred_answer_string)
```

**優勢**：
- 避免重複嘗試已知錯誤答案
- 提高成功率（從剩餘選項中選擇）
- 適用於 KKTIX 多選題

---

### Q3: 為什麼需要人類化延遲？

**A**: 模擬真人行為，避免被搶票系統偵測為機器人。

**延遲策略**：
```python
# 1. 填寫前延遲（0.3-1.0 秒）
human_delay = random.uniform(0.3, 1.0)
await tab.sleep(human_delay)

# 2. 逐字輸入（每字約 0.05-0.1 秒）
for i, char in enumerate(answer):
    input.value += char
    input.dispatchEvent(new Event('input'))
    # 自然地模擬打字速度

# 3. 點擊按鈕前延遲（0.2-0.5 秒）
button_delay = random.uniform(0.2, 0.5)
await tab.sleep(button_delay)
```

**為什麼有效？**
- **真人特徵**：真人打字有延遲，機器人則瞬間完成
- **事件觸發**：逐字輸入觸發多次 `input` 事件（真人行為）
- **隨機性**：每次延遲不同，避免被偵測為固定模式

---

### Q4: Shadow DOM 驗證碼如何擷取？

**A**: 使用 **DOMSnapshot** 平坦化 closed Shadow DOM，再使用 CDP 擷取截圖。

**問題**：
- iBon 使用 `closed` Shadow DOM
- 標準 API 無法訪問：`element.shadowRoot === null`

**解決方案（3 步驟）**：
```python
# Step 1: 使用 DOMSnapshot 平坦化 Shadow DOM
dom_snapshot_result = await tab.send(zendriver.cdp.dom_snapshot.capture_snapshot())

# Step 2: 搜尋驗證碼元素（在平坦化結構中）
for doc in dom_snapshot_result[0]:
    for idx, node_id in enumerate(doc.layout.node_index):
        if 'captcha' in node_name.lower():
            captcha_backend_node_id = doc.layout.backend_node_id[idx]

# Step 3: 使用 CDP 擷取元素截圖
screenshot = await tab.send(zendriver.cdp.page.captureScreenshot())
```

**優勢**：
- 支援 `closed` Shadow DOM
- 不需要逐層打開 Shadow Root
- 一次性取得整個 DOM 結構

**參考文件**：Shadow DOM 除錯章節 - 詳見內部開發文件

---

## 相關文件

- 📋 [ddddocr API 指南](../03-api-reference/ddddocr_api_guide.md) - OCR 引擎完整參考
- 📋 [12-Stage 標準](../02-development/ticket_automation_standard.md) - Stage 7 規格
- 🔧 [KKTIX 參考實作](../03-implementation/platform-examples/kktix-reference.md) - 問答式驗證碼
- 🔧 [iBon 參考實作](../03-implementation/platform-examples/ibon-reference.md) - Shadow DOM 驗證碼
- 🔧 [TixCraft 參考實作](../03-implementation/platform-examples/tixcraft-reference.md) - OCR 驗證碼
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 函數位置索引
- 🐛 [ARM 平台 ddddocr 安裝](../05-troubleshooting/ddddocr_macos_arm_installation.md) - ARM 疑難排解

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：ddddocr OCR 基本功能 |
| v1.1 | 2025-08 | 新增 iBon Shadow DOM 支援 |
| **v1.2** | **2025-10** | **KKTIX 問答式驗證碼 + fail_list 機制** |
| **v1.3** | **2025-11** | **人類化延遲 + 重試機制強化** |
| **v1.4** | **2026-02** | **通用 OCR 模型（svtr_tiny）整合** |

**v1.4 重大變更**：
- ✅ 內建通用 OCR 模型（`src/assets/model/universal/`，1.32MB）
- ✅ TixCraft/iBon/KHAM 準確率提升至 99-100%
- ✅ `ocr_captcha.use_universal` 設定鍵控制模型選擇
- ✅ `create_universal_ocr()` 在程式頂部統一初始化
- ✅ FunOne 維持 ddddocr 官方模型（通用模型準確率 75.67% 不符需求）
