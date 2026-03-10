# NoDriver API 使用指南

**文件說明**：NoDriver 的完整 API 使用指南，涵蓋 CDP 原生方法、JavaScript 輔助、Shadow DOM 處理等核心概念與最佳實踐。
**最後更新**：2025-11-12

---

> **重要**：優先使用 CDP 原生方法，避免過度依賴 JavaScript

**官方文件**: https://ultrafunkamsterdam.github.io/nodriver/

**相關文件**:
- **[CDP Protocol 參考指南](cdp_protocol_reference.md)** - Chrome DevTools Protocol 完整參考（推薦深入閱讀）
- 本文件著重於 NoDriver 高階 API 使用，CDP 詳細規格請參考上述文件

## 核心原則

1. **優先使用 NoDriver 原生 CDP 方法**：CDP 方法提供更強大的功能、更好的效能和更高的穩定性
2. **JavaScript 作為輔助**：僅在簡單 DOM 操作或 CDP 方法過於複雜（>50 行）時使用
3. **Shadow DOM 處理**：必須使用 CDP DOMSnapshot 和 DOM API（JavaScript 無法穿透 closed Shadow DOM）
4. **內建重試機制**：在適當層級實作等待和重試邏輯
5. **詳細錯誤處理**：妥善處理 CDP 方法的異常

## NoDriver vs JavaScript 使用決策

### 何時使用 CDP 方法（推薦）

**必須使用 CDP 的場景：**
- Shadow DOM 操作（closed Shadow DOM 只能用 CDP）
- 元素精確定位與截圖
- 模擬真實滑鼠/鍵盤行為
- 網路監控與攔截

**優勢：**
- 直接與瀏覽器底層溝通，效能更好
- 不受頁面 JavaScript 環境影響
- 更難被反爬蟲機制偵測
- 支援更多進階功能

### 何時使用 JavaScript（謹慎使用）

**適合場景：**
- 簡單 DOM 查詢（檢查元素存在、讀取屬性）
- 表單操作（open Shadow DOM）
- CDP 實作過於複雜（>50 行 vs <10 行）

**限制：**
- 無法穿透 closed Shadow DOM
- 容易被反爬蟲機制偵測
- 受頁面環境影響

### 決策流程

```
需要操作 DOM 元素？
    |
    v
涉及 Shadow DOM？
    |
    +-- 是 --> 使用 CDP DOMSnapshot + DOM API（必須）
    |
    +-- 否 --> 需要精確定位/截圖？
                |
                +-- 是 --> 使用 CDP DOM API（推薦）
                |
                +-- 否 --> 簡單查詢/表單操作？
                            |
                            +-- 是 --> JavaScript 可接受
                            |
                            +-- 否 --> 評估程式碼複雜度
                                        |
                                        +-- CDP < 50 行 --> 使用 CDP（推薦）
                                        +-- CDP > 50 行且 JS < 10 行 --> 使用 JavaScript
```

## 📚 NoDriver API 快速查詢

### 常用操作速查

```python
# 基本操作
await tab.get(url)                    # 導航
await tab.evaluate('JavaScript')     # 執行 JS
await tab.sleep(seconds)              # 等待

# CDP 進階操作（推薦）
# 詳細 CDP 命令參考：cdp_protocol_reference.md
from nodriver import cdp

# 穿透 Shadow DOM（推薦優先：Pierce Method）
search_id, count = await tab.send(cdp.dom.perform_search(
    query='button.btn-buy',
    include_user_agent_shadow_dom=True  # 穿透 Shadow DOM
))
node_ids = await tab.send(cdp.dom.get_search_results(
    search_id=search_id, from_index=0, to_index=count
))
await tab.send(cdp.dom.discard_search_results(search_id=search_id))

# 穿透 Shadow DOM（回退方法：DOMSnapshot）
await tab.send(cdp.dom_snapshot.capture_snapshot())

# 元素精確定位
await tab.send(cdp.dom.get_box_model(node_id=node_id))

# 模擬真實點擊
await tab.send(cdp.input.dispatch_mouse_event(
    type_='mousePressed', x=x, y=y, button='left'
))

# 截圖
await tab.send(cdp.page.capture_screenshot(format_='png'))
```

**📖 深入學習 CDP：** 查看 **[CDP Protocol 參考指南](cdp_protocol_reference.md)** 了解完整的 CDP 命令、參數和使用範例。

### 推薦方法對照表

| 需求 | 推薦方法（優先） | 回退方法 | 備註 |
|-----|----------------|---------|------|
| 穿透 closed Shadow DOM | `cdp.dom.perform_search()` + `include_user_agent_shadow_dom=True` | `cdp.dom_snapshot.capture_snapshot()` | **Pierce Method 速度快 60-70%** ⭐ |
| 元素精確定位 | `cdp.dom.get_box_model()` | - | 提供完整座標資訊 |
| 元素點擊 | `cdp.input.dispatch_mouse_event()` | - | 模擬真實滑鼠行為 |
| 元素截圖 | `cdp.page.capture_screenshot()` | - | 支援完整頁面或區域 |
| 表單輸入 | `element.send_keys()` | - | 模擬真實鍵盤輸入 |
| 簡單查詢 | `tab.evaluate()` | - | 快速檢查可見性 |

### ⚠️ 避免使用

- `tab.wait_for()` - 方法不穩定
- `tab.select()` - 方法不存在
- `element.get_attribute()` - 用 CDP 或 evaluate
- JavaScript 穿透 Shadow DOM - 無法存取 closed Shadow DOM

## ibon 實作範例：CDP 方法最佳實踐

### 範例 0：Pierce Method - Shadow DOM 穿透最佳實踐（推薦優先） ⭐

**重大突破**：從優化 DOMSnapshot 速度發現的更優方法，60-70% 性能提升！

**ibon 購票按鈕** 位於 closed Shadow DOM 內，傳統 JavaScript 無法存取。使用 Pierce Method 可以：
- ⚡ **速度快**：2-5 秒（vs DOMSnapshot 10-15 秒）
- ⚡ **成功率高**：第一次 95%+（vs DOMSnapshot 20%）
- ⚡ **智慧等待**：輪詢檢查，找到即執行（vs 固定延遲）

```python
async def nodriver_ibon_date_auto_select_pierce(tab, config_dict):
    """
    使用 Pierce Method 穿透 Shadow DOM（優先方法）
    優勢：速度快、成功率高、智慧等待
    """
    from nodriver import cdp
    import random

    show_debug_message = config_dict["advanced"].get("verbose", False)

    # 階段 1：智慧等待 - 輪詢檢查按鈕是否出現
    initial_wait = random.uniform(1.2, 1.8)
    await tab.sleep(initial_wait)

    # 捲動觸發 lazy loading
    await tab.evaluate('window.scrollTo(0, document.body.scrollHeight);')
    await tab

    # 輪詢檢查（最多 5 秒）
    max_wait = 5
    check_interval = 0.3
    max_attempts = int(max_wait / check_interval)
    button_found = False

    for attempt in range(max_attempts):
        try:
            search_id, count = await tab.send(cdp.dom.perform_search(
                query='button.btn-buy',
                include_user_agent_shadow_dom=True  # 穿透 Shadow DOM
            ))

            # 必須清理搜尋會話
            try:
                await tab.send(cdp.dom.discard_search_results(search_id=search_id))
            except:
                pass

            if count > 0:
                button_found = True
                if show_debug_message:
                    print(f"[PIERCE] Found {count} button(s) after {initial_wait + attempt * check_interval:.1f}s")
                break
        except:
            pass

        await tab.sleep(check_interval)

    # 階段 2：獲取文檔根節點（depth=0 避免 CBOR 錯誤）
    doc_result = await tab.send(cdp.dom.get_document(depth=0, pierce=False))
    root_node_id = doc_result.node_id

    # 階段 3：搜尋購票按鈕
    search_id, result_count = await tab.send(cdp.dom.perform_search(
        query='button.btn-buy',
        include_user_agent_shadow_dom=True
    ))

    if result_count == 0:
        await tab.send(cdp.dom.discard_search_results(search_id=search_id))
        return False  # 觸發回退到 DOMSnapshot

    # 獲取搜尋結果（node IDs）
    button_node_ids = await tab.send(cdp.dom.get_search_results(
        search_id=search_id,
        from_index=0,
        to_index=result_count
    ))

    # 清理搜尋會話
    await tab.send(cdp.dom.discard_search_results(search_id=search_id))

    # 階段 4：提取按鈕屬性
    purchase_buttons = []

    for node_id in button_node_ids:
        # 獲取節點詳細資訊
        node_desc = await tab.send(cdp.dom.describe_node(node_id=node_id))
        node = node_desc if hasattr(node_desc, 'attributes') else node_desc.node

        # 解析屬性（平坦陣列：[key1, val1, key2, val2, ...]）
        attrs = {}
        if hasattr(node, 'attributes') and node.attributes:
            for i in range(0, len(node.attributes), 2):
                if i + 1 < len(node.attributes):
                    attrs[node.attributes[i]] = node.attributes[i + 1]

        button_class = attrs.get('class', '')
        button_disabled = 'disabled' in attrs

        purchase_buttons.append({
            'node_id': node_id,
            'class': button_class,
            'disabled': button_disabled
        })

    # 過濾掉 disabled 按鈕
    enabled_buttons = [b for b in purchase_buttons if not b['disabled']]

    if len(enabled_buttons) == 0:
        return False

    # 階段 5：選擇按鈕並點擊
    target_button = enabled_buttons[0]  # 選擇第一個可用按鈕

    # CDP 原生點擊
    await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=target_button['node_id']))

    box_model = await tab.send(cdp.dom.get_box_model(node_id=target_button['node_id']))

    # 計算點擊座標（元素中心）
    x = (box_model.content[0] + box_model.content[2]) / 2
    y = (box_model.content[1] + box_model.content[5]) / 2

    # 執行點擊
    await tab.send(cdp.input_.dispatch_mouse_event(
        type_='mousePressed', x=x, y=y, button='left', click_count=1
    ))
    await tab.send(cdp.input_.dispatch_mouse_event(
        type_='mouseReleased', x=x, y=y, button='left', click_count=1
    ))

    return True
```

**性能對比**：

| 指標 | DOMSnapshot (範例 1) | Pierce Method (範例 0) | 提升幅度 |
|------|---------------------|----------------------|---------|
| 執行時間 | 10-15 秒 | 2-5 秒 | **60-70% ↓** |
| 第一次成功率 | 20% | 95%+ | **75% ↑** |
| 處理節點數 | 6000+ 節點 | 1-10 節點 | **99% ↓** |
| 記憶體消耗 | ~50MB | ~5MB | **90% ↓** |

**何時使用 Pierce vs DOMSnapshot**：

| 情境 | 推薦方法 |
|------|---------|
| 搜尋特定元素（如按鈕） | ✅ Pierce Method |
| 需要快速響應 | ✅ Pierce Method |
| 需要提取複雜關聯數據（如表格） | ✅ DOMSnapshot |
| 作為 Pierce 的 Fallback | ✅ DOMSnapshot |

**Primary → Fallback 設計模式**：

```python
async def nodriver_ibon_date_auto_select(tab, config_dict):
    """主入口：Pierce 優先，失敗回退 DOMSnapshot"""

    # Primary: 嘗試 Pierce Method
    try:
        if await nodriver_ibon_date_auto_select_pierce(tab, config_dict):
            return True
    except Exception as e:
        print(f"[IBON DATE] pierce method error: {e}")

    # Fallback: 回退到 DOMSnapshot
    return await nodriver_ibon_date_auto_select_domsnapshot(tab, config_dict)
```

**📖 深入學習**：查看 **[Shadow DOM Pierce Method 完整指南](shadow_dom_pierce_guide.md)** 了解技術原理、完整實作和最佳實踐。

---

### 範例 1：DOMSnapshot 穿透 Shadow DOM 搜尋按鈕（回退方法）

ibon 的購票按鈕位於 closed Shadow DOM 內，JavaScript 無法存取。

```python
async def nodriver_ibon_date_auto_select(tab, config_dict):
    """
    使用 DOMSnapshot 穿透 Shadow DOM 搜尋購票按鈕
    優勢：可存取 closed Shadow DOM，JavaScript 無法做到
    """
    from nodriver import cdp

    # 步驟 1：捕獲平坦化的 DOM 結構
    documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
        computed_styles=[],
        include_dom_rects=True
    ))

    purchase_buttons = []

    if documents and len(documents) > 0:
        document_snapshot = documents[0]
        nodes = document_snapshot.nodes

        # 步驟 2：提取節點資訊
        node_names = [strings[i] for i in nodes.node_name]
        node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
        attributes_list = nodes.attributes
        backend_node_ids = list(nodes.backend_node_id)

        # 步驟 3：搜尋購票按鈕
        for i, node_name in enumerate(node_names):
            if node_name.upper() == 'BUTTON':
                # 解析屬性
                attrs = {}
                if i < len(attributes_list):
                    attr_indices = attributes_list[i]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key = strings[attr_indices[j]]
                            val = strings[attr_indices[j + 1]]
                            attrs[key] = val

                # 檢查是否為購票按鈕
                button_class = attrs.get('class', '')
                if 'ng-tns-c57' in button_class or 'btn-buy' in button_class:
                    purchase_buttons.append({
                        'backend_node_id': backend_node_ids[i],
                        'class': button_class,
                        'disabled': 'disabled' in attrs
                    })

    return purchase_buttons
```

**關鍵優勢：**
- DOMSnapshot 自動平坦化所有 Shadow DOM（包含 closed）
- 一次呼叫即可獲得完整 DOM 結構
- 性能優異，適合大規模元素搜尋

**JavaScript 無法實現（對比）：**
```python
# JavaScript 無法穿透 closed Shadow DOM
result = await tab.evaluate('''
    document.querySelectorAll('button');  // 返回空陣列，因為按鈕在 closed Shadow DOM 內
''')
```

### 範例 2：CDP DOM API 截取 Shadow DOM 內的驗證碼圖片

```python
async def nodriver_ibon_get_captcha_image(tab, config_dict):
    """
    使用 CDP 截取 Shadow DOM 內的驗證碼圖片
    優勢：精確定位並截圖，不受 Shadow DOM 限制
    """
    from nodriver import cdp
    import base64
    from PIL import Image
    import io

    # 步驟 1：使用 DOMSnapshot 找到驗證碼圖片
    documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
        computed_styles=[],
        include_dom_rects=True
    ))

    img_backend_node_id = None

    for doc in documents:
        node_names = [strings[i] for i in doc.nodes.node_name]

        for idx, node_name in enumerate(node_names):
            if node_name.lower() == 'img':
                attrs = doc.nodes.attributes[idx]
                attr_dict = {}
                for i in range(0, len(attrs), 2):
                    if i + 1 < len(attrs):
                        attr_dict[strings[attrs[i]]] = strings[attrs[i + 1]]

                # 檢查是否為驗證碼圖片
                if '/pic.aspx?TYPE=' in attr_dict.get('src', ''):
                    img_backend_node_id = doc.nodes.backend_node_id[idx]
                    break

        if img_backend_node_id:
            break

    if not img_backend_node_id:
        return None

    # 步驟 2：初始化 DOM 並轉換 node ID
    await tab.send(cdp.dom.get_document())
    result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([img_backend_node_id]))
    img_node_id = result[0]

    # 步驟 3：確保元素可見
    await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=img_node_id))
    await asyncio.sleep(0.1)

    # 步驟 4：獲取元素位置（box model）
    box_model = await tab.send(cdp.dom.get_box_model(node_id=img_node_id))

    if box_model and hasattr(box_model, 'content'):
        quad = box_model.content
        x = min(quad[0], quad[2], quad[4], quad[6])
        y = min(quad[1], quad[3], quad[5], quad[7])
        width = max(quad[0], quad[2], quad[4], quad[6]) - x
        height = max(quad[1], quad[3], quad[5], quad[7]) - y

        # 步驟 5：截取頁面並裁切
        device_pixel_ratio = await tab.evaluate('window.devicePixelRatio')
        full_screenshot = await tab.send(cdp.page.capture_screenshot(format_='png'))

        full_img_bytes = base64.b64decode(full_screenshot)
        full_img = Image.open(io.BytesIO(full_img_bytes))

        # 根據 device pixel ratio 調整座標
        left = int(x * device_pixel_ratio)
        top = int(y * device_pixel_ratio)
        right = int((x + width) * device_pixel_ratio)
        bottom = int((y + height) * device_pixel_ratio)

        cropped_img = full_img.crop((left, top, right, bottom))

        # 步驟 6：轉換為 bytes
        img_buffer = io.BytesIO()
        cropped_img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()

    return None
```

**關鍵優勢：**
- `get_box_model()` 提供精確的元素位置
- `capture_screenshot()` 支援完整頁面截圖
- 結合 PIL 進行精確裁切
- 不受 Shadow DOM 類型限制

### 範例 3：CDP 原生點擊 vs JavaScript 點擊

```python
async def click_button_with_cdp(tab, backend_node_id):
    """
    使用 CDP 原生方法點擊按鈕
    優勢：更接近真實使用者行為，不易被偵測
    """
    from nodriver import cdp

    # 步驟 1：初始化並轉換 node ID
    await tab.send(cdp.dom.get_document())
    result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([backend_node_id]))
    node_id = result[0]

    # 步驟 2：滾動元素到可見區域
    await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
    await asyncio.sleep(0.1)

    # 步驟 3：獲取元素中心座標
    box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
    quad = box_model.content
    center_x = (quad[0] + quad[2] + quad[4] + quad[6]) / 4
    center_y = (quad[1] + quad[3] + quad[5] + quad[7]) / 4

    # 步驟 4：模擬真實滑鼠點擊
    await tab.send(cdp.input.dispatch_mouse_event(
        type_='mousePressed',
        x=center_x,
        y=center_y,
        button='left',
        click_count=1
    ))
    await tab.send(cdp.input.dispatch_mouse_event(
        type_='mouseReleased',
        x=center_x,
        y=center_y,
        button='left',
        click_count=1
    ))

    return True
```

**對比 JavaScript 點擊（容易被偵測）：**
```python
# JavaScript 點擊不產生真實滑鼠事件，容易被偵測
await tab.evaluate('document.querySelector("button").click()')
```

### 範例 4：表單輸入 - 結合 CDP 和 NoDriver

```python
async def nodriver_ibon_keyin_captcha_code(tab, answer, config_dict):
    """
    驗證碼輸入 - 結合 CDP 定位和 NoDriver 輸入
    """
    # 步驟 1：使用 NoDriver 原生方法查找輸入框
    form_verifyCode = None
    try:
        form_verifyCode = await tab.query_selector('input[placeholder="驗證碼"]')
    except:
        pass

    if not form_verifyCode:
        try:
            form_verifyCode = await tab.query_selector('#ctl00_ContentPlaceHolder1_CHK')
        except:
            pass

    if not form_verifyCode:
        return False

    # 步驟 2：檢查可見性（使用 JavaScript，簡單查詢）
    is_visible = await tab.evaluate('''
        (function() {
            const element = document.querySelector('input[placeholder="驗證碼"]') ||
                           document.querySelector('#ctl00_ContentPlaceHolder1_CHK');
            return element && !element.disabled && element.offsetParent !== null;
        })();
    ''')

    if not is_visible:
        return False

    # 步驟 3：填寫驗證碼（使用 NoDriver Element 方法）
    try:
        await form_verifyCode.click()
        await form_verifyCode.apply('function (element) { element.value = ""; }')
        await form_verifyCode.send_keys(answer)
        return True
    except Exception as e:
        return False
```

**使用原則：**
- 元素查找：NoDriver `query_selector()`（簡單穩定）
- 可見性檢查：JavaScript（快速查詢）
- 文字輸入：NoDriver `send_keys()`（模擬真實輸入）

## 正確的 NoDriver 方法

### 1. 基本頁面操作

```python
# 導航到頁面
await tab.get(url)
await tab  # 等待頁面基本載入

# 等待
await tab.sleep(seconds)  # 簡單等待
await asyncio.sleep(seconds)  # 替代方法

# 重新載入
await tab.reload()

# 取得資訊
current_url = tab.url
page_title = await tab.evaluate('document.title')
```

### 2. JavaScript 執行

```python
# 執行簡單 JavaScript
result = await tab.evaluate('document.title')

# 複雜操作（IIFE 模式）
result = await tab.evaluate('''
    (function() {
        const element = document.querySelector('#selector');
        if (element) {
            element.click();
            return { success: true };
        }
        return { success: false };
    })();
''')

# 傳遞參數
value = "test_value"
result = await tab.evaluate(f'''
    (function() {{
        const value = "{value}";
        return {{ received: value }};
    }})()
''')
```

### 3. 條件等待（推薦）

```python
async def wait_for_element(tab, selector, timeout=10):
    """等待元素載入並確保可見"""
    result = await tab.evaluate(f'''
        (function() {{
            return new Promise((resolve) => {{
                let retryCount = 0;
                const maxRetries = {timeout * 5};

                function checkElement() {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        const rect = element.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0;

                        if (isVisible) {{
                            resolve({{ success: true, visible: true }});
                            return;
                        }}
                    }}

                    if (retryCount < maxRetries) {{
                        retryCount++;
                        setTimeout(checkElement, 200);
                    }} else {{
                        resolve({{ success: false, error: "Timeout" }});
                    }}
                }}

                checkElement();
            }});
        }})();
    ''')
    return result
```

### 4. JavaScript Alerts 處理

```python
# 處理 alert/confirm/prompt
await tab.handle_java_script_dialog(accept=True, prompt_text="optional_text")

# 或預先禁用
await tab.evaluate('''
    window.alert = function() { return true; };
    window.confirm = function() { return true; };
    window.prompt = function() { return "default"; };
''')
```

### 5. 多分頁管理

```python
# 正確的分頁管理
driver = await nd.start()
main_tab = driver.tabs[0]

# 開啟新分頁
new_tab = await driver.new_tab()
await new_tab.get('https://example.com')

# 切換分頁
for tab in driver.tabs:
    if 'target_page' in tab.url:
        await tab.activate()
        break

# 關閉分頁
await new_tab.close()
# 不要再使用 new_tab 變數，改用 driver.tabs
```

## Shadow DOM 操作進階

### 1. CDP DOM 原生穿透（推薦）

```python
async def advanced_shadow_dom_traversal(tab, target_selector="button"):
    """使用 CDP DOM 原生方法穿透 Shadow DOM"""
    from nodriver import cdp

    # 使用 pierce=True 獲取包含 Shadow DOM 的完整文檔樹
    document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

    async def find_elements_in_node(node, path=""):
        found_elements = []
        node_name = getattr(node, 'node_name', '').lower()

        # 檢查當前節點
        if node_name == target_selector.lower():
            try:
                node_desc = await tab.send(cdp.dom.describe_node(node_id=node.node_id))
                outer_html = await tab.send(cdp.dom.get_outer_html(node_id=node.node_id))

                # 解析屬性
                attributes = getattr(node_desc.node, 'attributes', [])
                attr_dict = {}
                for i in range(0, len(attributes), 2):
                    if i + 1 < len(attributes):
                        attr_dict[attributes[i]] = attributes[i + 1]

                found_elements.append({
                    'node_id': node.node_id,
                    'path': path,
                    'attributes': attr_dict,
                    'html': outer_html.outer_html
                })
            except Exception as e:
                pass

        # 遞迴檢查子節點
        if hasattr(node, 'children'):
            for i, child in enumerate(node.children):
                child_elements = await find_elements_in_node(child, f"{path}/{node_name}[{i}]")
                found_elements.extend(child_elements)

        # 檢查 Shadow roots（關鍵：可存取 closed Shadow DOM）
        if hasattr(node, 'shadow_roots'):
            for i, shadow_root in enumerate(node.shadow_roots):
                shadow_elements = await find_elements_in_node(shadow_root, f"{path}/{node_name}[shadow_{i}]")
                found_elements.extend(shadow_elements)

        return found_elements

    # 搜尋目標元素
    buttons = await find_elements_in_node(document.root)
    return buttons
```

### 2. Shadow Root 類型檢測

```python
async def detect_shadow_root_types(tab):
    """檢測頁面中的 Shadow Root 類型"""
    from nodriver import cdp

    document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

    async def analyze_shadow_roots(node, results=None):
        if results is None:
            results = {
                'USER_AGENT': 0,
                'OPEN': 0,
                'CLOSED': 0,
                'total_shadow_hosts': 0
            }

        # 檢查 Shadow roots
        if hasattr(node, 'shadow_roots') and node.shadow_roots:
            results['total_shadow_hosts'] += 1

            for shadow_root in node.shadow_roots:
                shadow_type = getattr(shadow_root, 'shadow_root_type', 'UNKNOWN')
                if shadow_type in results:
                    results[shadow_type] += 1

        # 遞迴檢查子節點
        if hasattr(node, 'children'):
            for child in node.children:
                await analyze_shadow_roots(child, results)

        return results

    return await analyze_shadow_roots(document.root)
```

**Shadow Root 類型說明：**
- **`USER_AGENT`**: 瀏覽器原生創建（如 `<input type="date">`）
- **`OPEN`**: 開放式，JavaScript 可存取
- **`CLOSED`**: 封閉式，JavaScript 無法存取

**重要**：CDP 的 `pierce=True` 可穿透所有類型的 Shadow DOM

### 3. DOMSnapshot 大規模檢測（推薦）

```python
async def capture_shadow_dom_snapshot(tab):
    """使用 DOMSnapshot 獲取平坦化結構"""
    from nodriver import cdp

    # 捕獲完整頁面快照，自動平坦化 Shadow DOM
    documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
        include_dom_rects=True,
        include_paint_order=True
    ))

    # documents 包含平坦化後的 DOM 樹
    for doc_idx, document in enumerate(documents):
        nodes = document.nodes

        # 搜尋目標元素
        for node_idx, node_name_idx in enumerate(nodes.node_name):
            node_name = strings[node_name_idx]

            if node_name.upper() == 'BUTTON':
                # 解析屬性
                if node_idx < len(nodes.attributes):
                    attrs = nodes.attributes[node_idx]
                    attr_dict = {}
                    for i in range(0, len(attrs), 2):
                        if i + 1 < len(attrs):
                            attr_dict[strings[attrs[i]]] = strings[attrs[i + 1]]

                    # 檢查是否符合條件
                    if 'btn-buy' in attr_dict.get('class', ''):
                        return True

    return False
```

## 反偵測配置

```python
import nodriver as nd

driver = await nd.start(
    headless=False,
    browser_args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
    ],
    user_data_dir=None  # 使用臨時 profile
)
```

## Cloudflare 挑戰處理

```python
async def bypass_cloudflare(tab, max_retries=10, retry_interval=2):
    """處理 Cloudflare 挑戰"""

    # 檢查是否有 Cloudflare
    has_cloudflare = await tab.evaluate('''
        (function() {
            const indicators = [
                'iframe[src*="challenges.cloudflare.com"]',
                'iframe[src*="cf-spinner"]',
                '.cf-challenge-running'
            ];
            return indicators.some(sel => document.querySelector(sel));
        })();
    ''')

    if not has_cloudflare:
        return True

    print("Detected Cloudflare, waiting...")

    for attempt in range(max_retries):
        # 等待自動通過
        await tab.sleep(retry_interval)

        # 檢查是否通過
        still_challenging = await tab.evaluate('''
            document.querySelector('iframe[src*="challenges.cloudflare.com"]') !== null
        ''')

        if not still_challenging:
            print("Cloudflare passed")
            return True

    return False
```

## KKTIX 自動答題流程

**功能分支**: `004-kktix-auto-answer`
**實作位置**: `src/nodriver_tixcraft.py:1172-1313` (nodriver_kktix_reg_captcha 函數)

### 功能概述

KKTIX 平台使用自訂驗證問題作為防機器人機制,系統需能自動偵測問題、推測答案並模擬人類填寫行為。

### 核心流程

```python
# 1. 批次檢查頁面元素(JavaScript)
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

# 2. 問題偵測與記錄
if elements_check and elements_check.get('hasQuestion'):
    question_text = elements_check.get('questionText', '')
    if len(question_text) > 0:
        # 記錄問題至檔案
        write_question_to_file(question_text)

        # 3. 產生候選答案清單
        # 優先使用用戶定義答案
        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)

        # 若無用戶答案且啟用自動推測,則從問題推測答案
        if len(answer_list) == 0 and config_dict["advanced"]["auto_guess_options"]:
            answer_list = util.get_answer_list_from_question_string(None, question_text)

        # 4. 過濾失敗清單
        inferred_answer_string = ""
        for answer_item in answer_list:
            if answer_item not in fail_list:  # 跳過已失敗的答案
                inferred_answer_string = answer_item
                break

        # 5. 填寫答案(模擬人類行為)
        if len(inferred_answer_string) > 0:
            # 人類化延遲(0.3-1.0秒)
            human_delay = random.uniform(0.3, 1.0)
            await tab.sleep(human_delay)

            # JavaScript 模擬逐字輸入
            fill_result = await tab.evaluate(f'''
                (function() {{
                    const input = document.querySelector('div.custom-captcha-inner > div > div > input');
                    if (!input) {{
                        return {{ success: false, error: "Input not found" }};
                    }}

                    // 確保輸入框可用
                    if (input.disabled || input.readOnly) {{
                        return {{ success: false, error: "Input is disabled or readonly" }};
                    }}

                    // 模擬人類打字
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
                        value: input.value
                    }};
                }})();
            ''')

            # 6. 點擊下一步按鈕
            if fill_result and fill_result.get('success'):
                button_delay = random.uniform(0.5, 1.2)
                await tab.sleep(button_delay)
                button_click_success = await nodriver_kktix_press_next_button(tab, config_dict)

                # 7. 記錄已嘗試的答案至 fail_list
                if button_click_success:
                    fail_list.append(inferred_answer_string)
```

### 設計決策

**為何使用 JavaScript 而非 CDP?**
- 簡單表單操作:JavaScript evaluate 10 行 vs CDP 需 50+ 行
- open Shadow DOM:不需 CDP DOMSnapshot
- 符合決策流程:「CDP > 50 行且 JS < 10 行」的場景

**人類化策略**
1. 隨機延遲(0.3-1.0 秒)模擬思考時間
2. 逐字輸入模擬打字行為
3. 觸發 DOM 事件(focus、input、change、blur)確保前端識別
4. 按鈕點擊前額外延遲(0.5-1.2 秒)

**失敗重試機制**
- 維護 session 級別的 `fail_list`
- 答案嘗試後加入失敗清單
- 重試時自動跳過已失敗答案
- 所有候選答案耗盡時停止自動填寫

### 配置項目

```json
{
  "advanced": {
    "auto_guess_options": false,      // 啟用自動推測答案(預設關閉)
    "user_guess_string": "",          // 用戶預定義答案(逗號分隔)
    "verbose": false                  // Debug 模式輸出
  }
}
```

### Verbose 模式輸出

啟用 `verbose: true` 時會輸出:
```
inferred_answer_string: SUNSET
question_text: 落日飛車的英文團名是 _ _ _ _ _ _ Rollercoaster...
answer_list: ['SUNSET', 'Sunset']
fail_list: []
Captcha answer filled successfully: SUNSET
```

### 相關函數

- `util.get_answer_list_from_user_guess_string()` - 讀取用戶預定義答案
- `util.get_answer_list_from_question_string()` - 從問題推測答案
- `write_question_to_file()` - 記錄問題至 `src/question.txt`
- `nodriver_kktix_press_next_button()` - 點擊下一步按鈕

### 測試方式

```bash
# 啟用 auto_guess_options 於 settings.json
# 使用測試案例: .temp/kktix-sunset-qa.html
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

## Debug 工具

### 頁面狀態快照

```python
async def capture_page_state(tab):
    """擷取頁面狀態供 debug"""
    state = await tab.evaluate('''
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                forms: document.forms.length,
                buttons: document.querySelectorAll('button').length
            };
        })();
    ''')
    print("Page State:", state)
    return state
```

### 元素存在性檢查

```python
async def check_elements_existence(tab, selectors):
    """批次檢查元素是否存在"""
    for selector in selectors:
        exists = await tab.evaluate(f'''
            document.querySelector('{selector}') !== null
        ''')
        print(f"{'✓' if exists else '✗'} {selector}")
```

## 常見錯誤與解決方案

| 錯誤訊息 | 原因 | 解決方案 |
|---------|------|----------|
| `'NoneType' object is not callable` | 呼叫不存在的方法 | 使用 evaluate() 執行 JavaScript |
| `Could not find node with given id` | 元素已從 DOM 移除 | 重新查詢元素 |
| `Cannot read properties of null` | JavaScript 中元素為 null | 加入 null 檢查 |
| `Timeout waiting for element` | 元素未及時出現 | 增加 timeout 或檢查選擇器 |

## 最佳實踐檢查清單

- [ ] **Shadow DOM**：使用 CDP DOMSnapshot 或 DOM API
- [ ] **元素點擊**：使用 CDP Input.dispatchMouseEvent
- [ ] **元素定位**：使用 CDP DOM get_box_model
- [ ] **截圖**：使用 CDP Page capture_screenshot
- [ ] **簡單查詢**：可使用 JavaScript evaluate
- [ ] **實作重試機制**：包含 CDP 異常處理
- [ ] **條件等待**：避免固定 sleep
- [ ] **詳細 debug 資訊**：方便問題追蹤

## 參考資源

### 技術文章
1. [NoDriver 繞過 Cloudflare Argus](https://stackoverflow.max-everyday.com/2024/10/nodriver-argus-cloudflare/)
2. [JavaScript ShadowRoot 操作](https://stackoverflow.max-everyday.com/2025/07/javascript-shadowroot-demo/)
3. [NoDriver 與 JavaScript Alerts 互動](https://stackoverflow.max-everyday.com/2025/03/nodriver%e8%88%87%e7%80%8f%e8%a6%bd%e5%99%a8%e5%85%a7%e5%bb%ba%e7%9a%84-javascript-alerts%e4%ba%92%e5%8b%95/)
4. [NoDriver 多分頁管理](https://stackoverflow.max-everyday.com/2024/10/nodriver-manually-close-mulit-tab-no-response/)

### 專案範例
- [NoDriver Cloudflare 驗證專案](https://github.com/omegastrux/nodriver-cf-verify)

## 總結

### 核心要點

1. **優先使用 CDP 方法**
   - Shadow DOM：`cdp.dom_snapshot.capture_snapshot()`
   - 元素定位：`cdp.dom.get_box_model()`
   - 元素操作：`cdp.input.dispatch_mouse_event()`
   - 截圖：`cdp.page.capture_screenshot()`

2. **JavaScript 作為輔助**
   - 僅用於簡單查詢和表單操作
   - 評估程式碼複雜度：CDP < 50 行優先

3. **Shadow DOM 必須用 CDP**
   - JavaScript 無法穿透 closed Shadow DOM
   - DOMSnapshot 提供平坦化結構
   - 保留 backend_node_id 供後續使用

4. **效能與穩定性**
   - CDP 直接與瀏覽器溝通，效能更優
   - 不受頁面環境影響
   - 更難被反爬蟲偵測

### 方法選擇快速參考

| 場景 | 方法 | 理由 |
|-----|------|-----|
| closed Shadow DOM | CDP DOMSnapshot | JavaScript 無法實現 |
| 精確定位 | CDP get_box_model | 完整座標資訊 |
| 真實點擊 | CDP dispatch_mouse_event | 模擬真實行為 |
| 截圖 | CDP capture_screenshot | 支援區域截圖 |
| 表單輸入 | Element send_keys | 模擬真實輸入 |
| 簡單查詢 | JavaScript evaluate | 快速簡單 |

---

**學習建議**：
1. 研讀本文件的 ibon 實作範例
2. 參考官方文件深入了解 CDP 方法
3. 遵循「CDP 優先」原則進行開發
