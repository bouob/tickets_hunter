# iBon 平台參考實作

**文件說明**：iBon 平台的完整實作參考，重點覆蓋 Shadow DOM 處理、Angular SPA 架構、DOMSnapshot API 應用等高難度技術挑戰。
**最後更新**：2025-12-02

---

## 概述

**平台名稱**：iBon（票券通路）
**主要特色**：
- **closed Shadow DOM**：最具技術挑戰性的 DOM 結構
- **Angular SPA**：單頁應用程式（需特殊事件觸發）
- **DOMSnapshot 平坦化**：突破 Shadow DOM 限制的關鍵技術
- **兩種頁面架構**：Event 頁面（新版 SPA）+ .aspx 頁面（舊版）

**完成度**：100% ✅
**推薦作為**：Shadow DOM 處理、DOMSnapshot API 的參考實作

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_ibon_main()` | 14253 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_ibon_login()` | 9068 | Cookie 登入處理 |
| Stage 4 | `nodriver_ibon_date_auto_select()` | 10625 | 日期選擇（DOMSnapshot）|
| Stage 4 | `nodriver_ibon_date_auto_select_pierce()` | 10234 | 日期選擇（CDP pierce）|
| Stage 5 | `nodriver_ibon_area_auto_select()` | 12233 | 區域選擇（DOMSnapshot）|
| Stage 5 | `nodriver_ibon_event_area_auto_select()` | 11728 | 區域選擇（Event 頁面）|
| Stage 6 | `nodriver_ibon_ticket_number_auto_select()` | 12813 | 票數自動設定 |
| Stage 7 | `nodriver_ibon_get_captcha_image_from_shadow_dom()` | 12970 | 驗證碼圖片擷取 |
| Stage 7 | `nodriver_ibon_captcha()` | 13627 | OCR 驗證碼處理 |
| Stage 7 | `nodriver_ibon_auto_ocr()` | 13455 | 自動 OCR 重試 |
| Stage 8 | `nodriver_ibon_verification_question()` | 14130 | 驗證問題自動填寫 |
| Stage 8 | `nodriver_ibon_fill_verify_form()` | 13958 | 驗證表單填寫（支援多欄位）|
| Stage 8 | `extract_answer_by_question_pattern()` | 13911 | 前/末 X 碼智慧提取 |
| Stage 9 | `nodriver_ibon_ticket_agree()` | 11691 | 同意條款勾選 |
| Stage 10 | `nodriver_ibon_purchase_button_press()` | 13724 | 送出購票按鈕 |
| Util | `nodriver_ibon_check_sold_out()` | 13781 | 售完檢測 |
| Util | `nodriver_ibon_allow_not_adjacent_seat()` | 11697 | 允許非相鄰座位 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## 特殊設計 1: closed Shadow DOM 突破

### 挑戰

iBon 使用 **closed Shadow DOM**,這是最難處理的 DOM 結構:

```javascript
// iBon 的 Shadow DOM 設定
const shadowRoot = element.attachShadow({ mode: 'closed' });
// 結果：無法透過標準 API 訪問
console.log(element.shadowRoot);  // null ❌
```

**標準方法失敗**：
```python
# ❌ 失敗：closed Shadow DOM 無法訪問
shadow_root = await element.shadow_root  # Returns None
buttons = await shadow_root.query_selector_all('button')  # Error!
```

### 解決方案: DOMSnapshot 平坦化

**核心技術**：使用 Chrome DevTools Protocol 的 `DOMSnapshot.captureSnapshot()` API 將整個 DOM（包括所有 Shadow DOM）平坦化為可查詢的結構。

**完整實作**（`nodriver_ibon_area_auto_select`, Line 9083-10378）：

```python
async def nodriver_ibon_area_auto_select(tab, config_dict):
    """
    使用 DOMSnapshot 平坦化策略處理 iBon 的 closed Shadow DOM
    這是整個專案中最複雜的函數（1295 行）
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # ========== Step 1: 使用 DOMSnapshot 平坦化整個 DOM ==========
    dom_snapshot_result = await tab.send(nodriver.cdp.dom_snapshot.capture_snapshot(
        computed_styles=[]  # 不需要樣式資訊，只要 DOM 結構
    ))

    # ========== Step 2: 解析平坦化結果 ==========
    documents = dom_snapshot_result[0]  # DocumentSnapshot list
    strings = dom_snapshot_result[1]    # String table (attribute values)

    if show_debug_message:
        print(f"[IBON SNAPSHOT] Captured {len(documents)} document(s)")
        print(f"[IBON SNAPSHOT] String table size: {len(strings)}")

    # ========== Step 3: 遍歷平坦化的 DOM 樹 ==========
    formated_area_list = []
    formated_area_list_text = []

    for doc in documents:
        layout = doc.layout
        node_index = layout.node_index
        backend_node_id_list = layout.backend_node_id

        if show_debug_message:
            print(f"[IBON SNAPSHOT] Processing document with {len(node_index)} nodes")

        # ========== Step 4: 搜尋特定元素（在平坦化結構中）==========
        for idx, node_id in enumerate(node_index):
            # 取得節點屬性（從 strings table）
            if idx < len(layout.styles):
                # layout.styles[idx][0] 是 string table 的索引
                node_name_idx = layout.styles[idx][0] if layout.styles[idx] else None

                if node_name_idx is not None and node_name_idx < len(strings):
                    node_name = strings[node_name_idx]

                    # ⭐ 搜尋目標元素（例如：class="area-button"）
                    if 'area-button' in node_name or 'seat-map-btn' in node_name:
                        backend_node_id = backend_node_id_list[idx]

                        # ========== Step 5: 取得節點文字內容 ==========
                        try:
                            # 使用 backend_node_id 取得 remote object
                            remote_object = await tab.send(
                                nodriver.cdp.dom.resolve_node(backend_node_id=backend_node_id)
                            )

                            # 取得文字內容
                            node_text_result = await tab.send(
                                nodriver.cdp.runtime.call_function_on(
                                    function_declaration='function() { return this.textContent; }',
                                    object_id=remote_object.object_id
                                )
                            )

                            node_text = node_text_result.result.value

                            # ========== Step 6: 過濾與匹配 ==========
                            # Apply keyword_exclude
                            if not util.reset_row_text_if_match_keyword_exclude(config_dict, node_text):
                                formated_area_list.append(backend_node_id)
                                formated_area_list_text.append(node_text)

                                if show_debug_message:
                                    print(f"[IBON AREA] Found area: {node_text[:50]}...")

                        except Exception as exc:
                            if show_debug_message:
                                print(f"[IBON AREA] Error processing node: {exc}")

    # ========== Step 7: 關鍵字匹配（Early Return Pattern）==========
    matched_blocks = []
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    if area_keyword:
        # Parse keywords
        area_keyword_array = [kw.strip().strip('"').strip("'") for kw in area_keyword.split(',') if kw.strip()]

        # Early Return Pattern
        for keyword_index, area_keyword_item in enumerate(area_keyword_array):
            if show_debug_message:
                print(f"[IBON AREA] Checking keyword #{keyword_index + 1}: {area_keyword_item}")

            for i, row_text in enumerate(formated_area_list_text):
                # AND logic
                keyword_parts = area_keyword_item.split(' ')
                if all(kw in row_text for kw in keyword_parts):
                    matched_blocks.append(formated_area_list[i])  # backend_node_id
                    if show_debug_message:
                        print(f"[IBON AREA] Keyword #{keyword_index + 1} matched: '{area_keyword_item}'")
                    break  # ⭐ Early Return

            if matched_blocks:
                break  # ⭐ Early Return
    else:
        matched_blocks = formated_area_list

    # ========== Step 8: 點擊目標元素 ==========
    if matched_blocks:
        target_backend_node_id = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

        if target_backend_node_id:
            try:
                # 使用 CDP dispatchMouseEvent 點擊
                remote_object = await tab.send(
                    nodriver.cdp.dom.resolve_node(backend_node_id=target_backend_node_id)
                )

                # 取得元素位置
                box_model = await tab.send(
                    nodriver.cdp.dom.get_box_model(backend_node_id=target_backend_node_id)
                )

                # 計算點擊座標（中心點）
                quad = box_model.model.content
                click_x = (quad[0] + quad[2]) / 2
                click_y = (quad[1] + quad[5]) / 2

                # 發送滑鼠點擊事件
                await tab.send(nodriver.cdp.input.dispatch_mouse_event(
                    type_='mousePressed',
                    x=click_x,
                    y=click_y,
                    button='left',
                    click_count=1
                ))
                await tab.send(nodriver.cdp.input.dispatch_mouse_event(
                    type_='mouseReleased',
                    x=click_x,
                    y=click_y,
                    button='left',
                    click_count=1
                ))

                if show_debug_message:
                    print(f"[IBON AREA] Clicked area at ({click_x}, {click_y})")

            except Exception as exc:
                if show_debug_message:
                    print(f"[IBON AREA] Click error: {exc}")
```

**關鍵突破點**：
1. **DOMSnapshot.captureSnapshot()**：將所有 Shadow DOM 平坦化
2. **backend_node_id**：唯一標識 Shadow DOM 內的元素
3. **DOM.resolveNode()**：將 backend_node_id 轉為可操作的 remote object
4. **CDP dispatchMouseEvent**：直接發送底層滑鼠事件

---

## 特殊設計 2: Angular SPA 事件觸發

### 挑戰

iBon 使用 **Angular 單頁應用程式 (SPA)**,標準的 JavaScript 事件不足以觸發 Angular 的模型更新。

### 解決方案

```python
# 觸發 Angular 事件的完整流程
await tab.evaluate(f'''
    (function() {{
        const targetInput = document.querySelector('#ticket_price');

        // Step 1: 設定值
        targetInput.value = "{ticket_number}";

        // Step 2: 觸發標準事件
        targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        targetInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));

        // Step 3: ⭐ 觸發 Angular 更新（關鍵）
        if (window.angular) {{
            const scope = window.angular.element(targetInput).scope();
            if (scope) {{
                scope.$apply();  // 強制 Angular 模型更新
            }}
        }}

        return {{ success: true }};
    }})();
''')
```

**為什麼需要 `scope.$apply()`？**
- Angular 使用雙向綁定（Two-way Data Binding）
- 標準 JavaScript 事件不會觸發 Angular 的變更檢測
- `scope.$apply()` 強制 Angular 重新檢查模型並更新 UI

---

## 特殊設計 3: 驗證碼圖片擷取（Shadow DOM）

### 挑戰

iBon 的驗證碼圖片也在 closed Shadow DOM 內,無法直接取得。

### 解決方案

**核心程式碼**（`nodriver_ibon_get_captcha_image_from_shadow_dom`, Line 9643-9730）：

```python
async def nodriver_ibon_get_captcha_image_from_shadow_dom(tab, config_dict):
    """
    從 closed Shadow DOM 中擷取驗證碼圖片
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        # Step 1: DOMSnapshot 平坦化
        dom_snapshot_result = await tab.send(nodriver.cdp.dom_snapshot.capture_snapshot(
            computed_styles=[]
        ))

        documents = dom_snapshot_result[0]
        strings = dom_snapshot_result[1]

        # Step 2: 搜尋驗證碼圖片元素
        captcha_backend_node_id = None
        for doc in documents:
            layout = doc.layout
            for idx, node_id in enumerate(layout.node_index):
                if idx < len(layout.styles):
                    node_name_idx = layout.styles[idx][0] if layout.styles[idx] else None

                    if node_name_idx and node_name_idx < len(strings):
                        node_name = strings[node_name_idx]

                        # ⭐ 搜尋驗證碼圖片（class="captcha-image" 或類似）
                        if 'captcha' in node_name.lower() or 'verify' in node_name.lower():
                            captcha_backend_node_id = layout.backend_node_id[idx]
                            if show_debug_message:
                                print(f"[IBON CAPTCHA] Found captcha image: {node_name}")
                            break

        if not captcha_backend_node_id:
            if show_debug_message:
                print("[IBON CAPTCHA] Captcha image not found in Shadow DOM")
            return None

        # Step 3: 使用 CDP Page.captureScreenshot 擷取元素截圖
        # 取得元素位置
        box_model = await tab.send(
            nodriver.cdp.dom.get_box_model(backend_node_id=captcha_backend_node_id)
        )

        # 計算裁切區域
        quad = box_model.model.content
        clip = {
            'x': quad[0],
            'y': quad[1],
            'width': quad[2] - quad[0],
            'height': quad[5] - quad[1],
            'scale': 1
        }

        # 擷取截圖
        screenshot_result = await tab.send(nodriver.cdp.page.captureScreenshot(
            format_='png',
            clip=clip,  # ⭐ 只截取驗證碼區域
            from_surface=True
        ))

        img_base64 = base64.b64decode(screenshot_result)

        if show_debug_message:
            print(f"[IBON CAPTCHA] Captcha image captured ({len(img_base64)} bytes)")

        return img_base64

    except Exception as exc:
        if show_debug_message:
            print(f"[IBON CAPTCHA] Shadow DOM extraction error: {exc}")
        return None
```

**關鍵技術**：
- **DOM.getBoxModel()**：取得元素的位置和尺寸
- **Page.captureScreenshot(clip=...)**：只截取特定區域
- 避免截取整個頁面，減少圖片大小

---

## 特殊設計 4: 兩種頁面架構支援

### 挑戰

iBon 有**兩種不同的頁面架構**：
1. **Event 頁面**（新版）：`/Event/...` 路徑,Angular SPA
2. **.aspx 頁面**（舊版）：`/ActivityDetail.aspx` 路徑,傳統伺服器渲染

### 解決方案

```python
# 根據 URL 判斷頁面類型
if '/Event/' in url:
    # 新版 Event 頁面（Angular SPA）
    await nodriver_ibon_event_area_auto_select(tab, config_dict)
elif '.aspx' in url:
    # 舊版 .aspx 頁面
    await nodriver_ibon_area_auto_select(tab, config_dict)
```

**兩種實作的差異**：

| 項目 | Event 頁面 | .aspx 頁面 |
|------|-----------|-----------|
| DOM 結構 | Shadow DOM | 標準 DOM + Shadow DOM |
| 函數名稱 | `nodriver_ibon_event_area_auto_select()` | `nodriver_ibon_area_auto_select()` |
| 程式碼行數 | 393 行 | 1295 行 |
| 複雜度 | 中等 | 極高 |

---

## DOMSnapshot API 完整參考

### API 呼叫

```python
import nodriver

# 呼叫 DOMSnapshot.captureSnapshot()
result = await tab.send(nodriver.cdp.dom_snapshot.capture_snapshot(
    computed_styles=[],  # 可選：需要的 CSS 屬性
    include_paint_order=False,
    include_dom_rects=True  # 包含元素位置資訊
))

documents = result[0]  # List[DocumentSnapshot]
strings = result[1]    # List[str] - String table
```

### 資料結構

```python
# DocumentSnapshot
document = documents[0]
layout = document.layout

# 重要屬性
node_index = layout.node_index            # List[int] - 節點索引
backend_node_id = layout.backend_node_id  # List[int] - ⭐ 唯一標識
styles = layout.styles                    # List[List[int]] - 樣式索引
bounds = layout.bounds                    # List[List[float]] - 元素位置
```

### 常用操作

```python
# 1. 遍歷所有節點
for idx, node_id in enumerate(layout.node_index):
    backend_node_id = layout.backend_node_id[idx]

    # 2. 取得節點名稱/class（從 strings table）
    if idx < len(layout.styles) and layout.styles[idx]:
        node_name_idx = layout.styles[idx][0]
        node_name = strings[node_name_idx]

    # 3. 搜尋目標元素
    if 'target-class' in node_name:
        # 4. 使用 backend_node_id 操作元素
        remote_object = await tab.send(
            nodriver.cdp.dom.resolve_node(backend_node_id=backend_node_id)
        )

        # 5. 取得文字內容
        text_result = await tab.send(
            nodriver.cdp.runtime.call_function_on(
                function_declaration='function() { return this.textContent; }',
                object_id=remote_object.object_id
            )
        )
        node_text = text_result.result.value

        # 6. 點擊元素
        box_model = await tab.send(
            nodriver.cdp.dom.get_box_model(backend_node_id=backend_node_id)
        )
        # ... (見前面完整實作)
```

---

## 完整流程範例（iBon 購票）

```python
async def ibon_purchase_flow_example():
    """iBon 完整購票流程示範"""

    # Stage 4: 日期選擇（DOMSnapshot）
    await nodriver_ibon_date_auto_select(tab, config_dict)
    # → 使用 DOMSnapshot 找到日期按鈕
    # → CDP dispatchMouseEvent 點擊

    # Stage 5: 區域選擇（1295行巨型函數）
    if '/Event/' in url:
        await nodriver_ibon_event_area_auto_select(tab, config_dict)
    else:
        await nodriver_ibon_area_auto_select(tab, config_dict)
    # → DOMSnapshot 平坦化 Shadow DOM
    # → 搜尋 area-button 元素
    # → Early Return Pattern 關鍵字匹配
    # → CDP dispatchMouseEvent 點擊

    # Stage 7: OCR 驗證碼
    await nodriver_ibon_captcha(tab, config_dict, ocr)
    # → DOMSnapshot 找驗證碼圖片
    # → Page.captureScreenshot 截圖
    # → ddddocr 辨識
    # → 填入答案 + Angular scope.$apply()
```

---

## 最佳實踐建議

### 1. Shadow DOM 除錯

**檢查 Shadow DOM 類型**：
```javascript
// 在瀏覽器 Console 執行
const element = document.querySelector('.your-element');
console.log(element.shadowRoot);  // null = closed, object = open
```

**檢視 DOMSnapshot 結果**：
```python
# 啟用 verbose 模式
config_dict["advanced"]["verbose"] = True

# 查看抓取到的節點數量
print(f"Captured {len(node_index)} nodes")
print(f"Found {len(formated_area_list)} valid areas")
```

### 2. Angular 事件觸發

**必須步驟**：
1. 標準事件（input, change, blur）
2. Angular 事件（`scope.$apply()`）
3. 兩者缺一不可

**檢查 Angular 是否存在**：
```javascript
console.log(window.angular);  // 應該是一個 object
```

### 3. 效能優化

**DOMSnapshot 很慢**：
- 平均耗時：200-500ms
- 建議：僅在 Shadow DOM 頁面使用
- 避免：頻繁重複呼叫

**優化策略**：
```python
# ❌ 不好：每次都重新抓取
for i in range(10):
    dom_snapshot = await tab.send(dom_snapshot.capture_snapshot())

# ✅ 好：一次抓取,重複使用
dom_snapshot = await tab.send(dom_snapshot.capture_snapshot())
for i in range(10):
    # 使用同一份 dom_snapshot
    process_snapshot(dom_snapshot)
```

---

## 常見問題

### Q1: DOMSnapshot 和標準 DOM API 有什麼差別？

**A**: DOMSnapshot 是**快照**,不是即時 DOM。

**標準 DOM API**（即時）：
```python
elements = await tab.query_selector_all('button')  # 即時查詢
# 頁面變化 → 立即反映
```

**DOMSnapshot**（快照）：
```python
snapshot = await tab.send(dom_snapshot.capture_snapshot())  # 一次性快照
# 頁面變化 → 快照不會更新（需要重新抓取）
```

**使用時機**：
- **標準 DOM API**：開放的 Shadow DOM、標準 DOM
- **DOMSnapshot**：closed Shadow DOM（無其他選擇）

### Q2: backend_node_id 和 node_id 有什麼差別？

**A**:
- **node_id**: DOM 樹中的節點 ID（會變化）
- **backend_node_id**: 永久的節點 ID（穩定）

**使用 backend_node_id 的原因**：
```python
# backend_node_id 在頁面生命週期內保持不變
backend_node_id = 12345

# 5 秒後仍然有效
await asyncio.sleep(5)
remote_object = await tab.send(
    nodriver.cdp.dom.resolve_node(backend_node_id=backend_node_id)
)  # ✅ 仍然有效
```

### Q3: 為什麼 iBon 函數這麼長（1295行）？

**A**: 因為需要處理**極度複雜的 Shadow DOM 結構** + **多種頁面變體**。

**複雜性來源**：
1. **DOMSnapshot 遍歷**：需要手動遍歷整個 DOM 樹（~500 行）
2. **多種元素類型**：按鈕/連結/座位圖（~300 行）
3. **錯誤處理**：各種邊界情況（~200 行）
4. **除錯日誌**：詳細的除錯輸出（~295 行）

**簡化方案**：
- 未來可能拆分為多個子函數
- 目前優先保證功能穩定性

---

## 相關文件

- 📋 [Stage 4: 日期選擇機制](../../02-mechanisms/04-date-selection.md) - DOMSnapshot 應用
- 📋 [Stage 7: 驗證碼處理機制](../../02-mechanisms/07-captcha-handling.md) - Shadow DOM 驗證碼
- 📋 [CDP 協議參考](../../03-api-reference/cdp_protocol_reference.md) - DOMSnapshot 完整 API
- 🐛 [除錯方法論](../../04-testing-debugging/debugging_methodology.md) - Shadow DOM 除錯
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - iBon 函數索引

---

## 特殊設計 5: 驗證問題自動填寫

### 概述

iBon 購票流程中有時會出現驗證問題頁面，要求使用者輸入手機號碼末幾碼、信用卡前 6 碼、訂單號碼等資訊。此功能可自動偵測並填寫這些驗證問題。

**核心函數**：

| 函數名稱 | 行數 | 說明 |
|---------|------|------|
| `extract_answer_by_question_pattern()` | ~13911 | 從答案清單中根據問題模式提取答案（前/末 X 碼） |
| `nodriver_ibon_fill_verify_form()` | ~13958 | 填寫驗證表單（支援單/多欄位） |
| `nodriver_ibon_verification_question()` | ~14130 | 驗證問題主處理邏輯 |

### 答案來源與優先順序

1. **使用者自訂字典**：`user_guess_string`（進階設定 → 優惠代碼）
2. **自動猜測**：`auto_guess_options`（需啟用，從問題文字推測答案）

### 前/末 X 碼智慧提取

**支援的問題模式**：

| 問題類型 | 關鍵字偵測 | 範例問題 | 字典輸入 | 自動輸出 |
|---------|----------|---------|---------|---------|
| 手機末 X 碼 | `末X碼`、`後X碼`、`最後X碼` | 「請輸入手機末三碼」 | `0912345678` | `678` |
| 信用卡前 6 碼 | `前X碼`、`首X碼` | 「請輸入信用卡前6碼」 | `123456` | `123456` |
| 訂單號碼前 X 碼 | `前X碼` | 「請輸入訂單號碼前4碼」 | `D12345678` | `D123` |

**中文數字支援**：
- 自動轉換：`三` → `3`、`四` → `4`、`六` → `6`
- 例：「請輸入手機末三碼」→ 偵測為「末 3 碼」

**實作程式碼**（`extract_answer_by_question_pattern`）：

```python
def extract_answer_by_question_pattern(answer_list, question_text):
    """
    根據問題模式從答案清單中提取答案

    Args:
        answer_list: 使用者字典答案列表
        question_text: 問題文字

    Returns:
        tuple: (提取的答案, 剩餘答案清單) 或 (None, 原答案清單)
    """
    import re

    # 中文數字對照表
    chinese_to_digit = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
    }

    # 末 X 碼模式
    last_patterns = [
        r"末([一二三四五六七八九十\d]+)碼",
        r"後([一二三四五六七八九十\d]+)碼",
        r"最後([一二三四五六七八九十\d]+)碼",
        r"末([一二三四五六七八九十\d]+)位",
    ]

    # 前 X 碼模式
    first_patterns = [
        r"前([一二三四五六七八九十\d]+)碼",
        r"首([一二三四五六七八九十\d]+)碼",
        r"前([一二三四五六七八九十\d]+)位",
    ]

    # 檢查末 X 碼
    for pattern in last_patterns:
        match = re.search(pattern, question_text)
        if match:
            n_str = match.group(1)
            n = int(chinese_to_digit.get(n_str, n_str))
            for i, answer in enumerate(answer_list):
                if len(answer) >= n:
                    extracted = answer[-n:]  # 取末 N 碼
                    remaining = answer_list[:i] + answer_list[i+1:]
                    return extracted, remaining

    # 檢查前 X 碼
    for pattern in first_patterns:
        match = re.search(pattern, question_text)
        if match:
            n_str = match.group(1)
            n = int(chinese_to_digit.get(n_str, n_str))
            for i, answer in enumerate(answer_list):
                if len(answer) >= n:
                    extracted = answer[:n]  # 取前 N 碼
                    remaining = answer_list[:i] + answer_list[i+1:]
                    return extracted, remaining

    return None, answer_list
```

### 多欄位支援

**使用情境**：某些驗證頁面有 2 個輸入欄位（如：信用卡前 6 碼 + 身分證字號）

**字典輸入格式**：使用分號 `;` 分隔多個答案，按順序對應輸入欄位

| 字典輸入 | 解析結果 | 對應欄位 |
|---------|---------|---------|
| `123456;A123456789` | `["123456", "A123456789"]` | 欄位1=123456, 欄位2=A123456789 |
| `0912345678;D12345678` | `["0912345678", "D12345678"]` | 欄位1（末X碼提取）, 欄位2（訂單號碼） |

**多欄位判斷邏輯**：

```python
# 判斷是否為多欄位模式
is_multi_question_mode = False
if form_input_count == 2 and len(answer_list) >= 2:
    if len(answer_list[0]) > 0 and len(answer_list[1]) > 0:
        is_multi_question_mode = True

# 填入邏輯
if is_multi_question_mode:
    # 雙欄位：按順序填入
    await nodriver_ibon_form_fill(tab, form_input_1, answer_list[0])
    await nodriver_ibon_form_fill(tab, form_input_2, answer_list[1])
else:
    # 單欄位：填入第一個未嘗試過的答案
    for answer in answer_list:
        if answer not in fail_list:
            await nodriver_ibon_form_fill(tab, form_input_1, answer)
            break
```

### CSS 選擇器

```python
# 問題文字
QUESTION_DESC_CSS = '#content div.form-group'

# 輸入欄位（支援多個）
INPUT_CSS = 'div.editor-box input[type="text"], div.editor-box input:not([type]), div.form-group > input'

# 送出按鈕
SUBMIT_BTN_CSS = 'div.editor-box a.btn'
```

### fail_list 機制

- 每次嘗試的答案會加入 `fail_list`
- 下次重試時會跳過已失敗的答案
- 避免無限重複嘗試相同的錯誤答案
- `fail_list` 在離開驗證頁面後自動清空

### 測試範例

| 測試案例 | 字典輸入 | 問題文字 | 預期輸出 |
|----------|----------|----------|----------|
| 手機末三碼 | `0912345678` | 請輸入手機末三碼 | `678` |
| 手機後四碼 | `0912345678` | 請輸入手機後4碼 | `5678` |
| 信用卡前6碼 | `123456` | 請輸入信用卡號前6碼 | `123456` |
| 訂單前4碼 | `D12345678` | 請輸入訂單號碼前4碼 | `D123` |
| 完整訂單號碼 | `D12345678` | 請輸入訂單號碼 | `D12345678` |
| 雙欄位 | `123456;A123456789` | 信用卡前6碼 + 身分證 | 欄位1=`123456`, 欄位2=`A123456789` |

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：.aspx 頁面基本支援 |
| **v1.1** | **2025-08** | **DOMSnapshot 平坦化技術導入** |
| **v1.2** | **2025-10** | **Event 頁面支援 + Angular 整合** |
| **v1.3** | **2025-11** | **Early Return Pattern + 效能優化** |
| **v1.4** | **2025-12** | **驗證問題自動填寫（前/末 X 碼智慧提取）** |

**v1.4 亮點**：
- ✅ 驗證問題自動填寫功能
- ✅ 前/末 X 碼智慧提取（含中文數字轉換）
- ✅ 多欄位支援（雙欄位按順序填入）
- ✅ fail_list 機制避免重複嘗試

**v1.3 亮點**：
- ✅ iBon 是唯一需要 DOMSnapshot 的平台（最複雜）
- ✅ 完整的 closed Shadow DOM 解決方案
- ✅ 支援 Event 頁面（Angular SPA）和 .aspx 頁面（傳統）
- ✅ 1295 行巨型函數（最長的單一函數）
