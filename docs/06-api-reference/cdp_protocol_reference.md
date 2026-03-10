# Chrome DevTools Protocol (CDP) 參考指南

**文件說明**：Chrome DevTools Protocol（CDP）的完整參考指南，涵蓋 NoDriver 與 CDP 的關係、核心 Domain 詳解、DOMSnapshot API 與實戰案例。
**最後更新**：2025-11-12

---

## 目錄

- [CDP 概述](#cdp-概述)
- [NoDriver 與 CDP 的關係](#nodriver-與-cdp-的關係)
- [基本使用語法](#基本使用語法)
- [核心 Domain 詳解](#核心-domain-詳解)
  - [DOMSnapshot Domain](#domsnapshot-domain)
  - [DOM Domain](#dom-domain)
  - [Input Domain](#input-domain)
  - [Network Domain](#network-domain)
  - [Page Domain](#page-domain)
  - [Runtime Domain](#runtime-domain)
- [快速查詢表](#快速查詢表)
- [實際程式碼範例](#實際程式碼範例)
- [參考資源](#參考資源)

---

## CDP 概述

### 什麼是 CDP？

**Chrome DevTools Protocol (CDP)** 是一個基於 JSON 的儀表化系統，允許開發工具對 Chromium 及其他 Blink 引擎瀏覽器進行：

- **檢查 (Inspection)** - 查看 DOM、網路請求、控制台訊息
- **調試 (Debugging)** - 設置斷點、追蹤執行流程
- **分析 (Profiling)** - 效能分析、記憶體監控
- **自動化 (Automation)** - 模擬使用者操作、注入程式碼

### CDP 架構

CDP 將功能劃分為多個 **Domain**（領域），每個 Domain 定義：

- **命令 (Commands)** - 可執行的操作（如 `Page.navigate`）
- **事件 (Events)** - 可監聽的通知（如 `Page.loadEventFired`）
- **型別 (Types)** - 資料結構定義

### 主要 Domain 分類

| Domain | 功能 | 本專案使用頻率 |
|--------|------|--------------|
| **DOMSnapshot** | DOM 快照、Shadow DOM 平坦化 | ⭐⭐⭐ 高 |
| **DOM** | 元素定位、查詢、操作 | ⭐⭐⭐ 高 |
| **Input** | 滑鼠/鍵盤模擬 | ⭐⭐⭐ 高 |
| **Network** | 網路請求、Cookie 管理 | ⭐⭐ 中 |
| **Page** | 導航、截圖、生命週期 | ⭐⭐ 中 |
| **Runtime** | JavaScript 執行、物件操作 | ⭐ 低 |

---

## NoDriver 與 CDP 的關係

### NoDriver 的 CDP 整合

[NoDriver](https://ultrafunkamsterdam.github.io/nodriver/) 是基於 CDP 構建的 Python 自動化框架：

```
使用者程式碼
    ↓
NoDriver Python API
    ↓
CDP JSON 訊息（WebSocket）
    ↓
Chrome/Chromium 瀏覽器
```

### 為什麼需要直接使用 CDP？

雖然 NoDriver 提供高階 API（如 `tab.get()`, `element.click()`），但某些場景必須直接使用 CDP：

**必須使用 CDP 的場景：**

1. **Shadow DOM 操作** - 特別是 closed Shadow DOM（JavaScript 無法穿透）
   - 範例：ibon、KHAM 平台的購票按鈕都在 Shadow DOM 內

2. **精確元素定位與操作**
   - 取得元素的精確座標位置
   - 模擬真實滑鼠/鍵盤行為（更難被偵測）

3. **底層瀏覽器控制**
   - Cookie 精細管理
   - 彈窗處理
   - 網路請求攔截

**優勢：**
- 直接與瀏覽器底層溝通，效能更好
- 不受頁面 JavaScript 環境影響
- 更難被反爬蟲機制偵測
- 支援更多進階功能

---

## 基本使用語法

### 1. 導入 CDP 模組

```python
from nodriver import cdp
```

### 2. 發送 CDP 命令

使用 `tab.send()` 方法發送 CDP 命令：

```python
# 基本語法
result = await tab.send(cdp.domain.command(parameters))

# 範例
documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
    computed_styles=[],
    include_dom_rects=True
))
```

### 3. 命名規範轉換

CDP 官方文件使用 camelCase，NoDriver 使用 snake_case：

| CDP 官方 | NoDriver Python |
|----------|----------------|
| `Page` | `cdp.page` |
| `Input` | `cdp.input_`（注意底線，避免與 Python 關鍵字衝突）|
| `DOMSnapshot` | `cdp.dom_snapshot` |
| `captureSnapshot` | `capture_snapshot()` |
| `dispatchKeyEvent` | `dispatch_key_event()` |

### 4. 錯誤處理

CDP 命令可能拋出異常，建議使用 try-except：

```python
try:
    result = await tab.send(cdp.dom.get_box_model(node_id=node_id))
except Exception as e:
    print(f"CDP command failed: {e}")
```

---

## 核心 Domain 詳解

### DOMSnapshot Domain

**用途：** 快速捕獲整個頁面的 DOM 結構，特別適合穿透 Shadow DOM。

#### 核心命令：`capture_snapshot`

**官方定義：** 返回文檔快照，包含完整的 DOM 樹（包括 iframe、template 內容、imported documents），以平坦化陣列形式呈現，並附帶佈局和樣式資訊。

**關鍵特性：** "Shadow DOM in the returned DOM tree is flattened."（Shadow DOM 會被平坦化）

#### 語法

```python
documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
    computed_styles=[],           # 要擷取的 CSS 屬性（空陣列 = 不擷取樣式）
    include_dom_rects=True,       # 包含元素位置資訊（offsetRects, clientRects）
    include_paint_order=False,    # 包含繪製順序（可選）
    include_blended_background_colors=False  # 包含混合背景色（實驗性）
))
```

#### 回傳值結構

```python
# documents: List[DOMNode]
#   - documents[0] 是主文件
#   - 包含 nodes, layout, textBoxes 等屬性

# strings: List[str]
#   - 字串池，所有文字內容都儲存在此
#   - nodes 中的索引指向此陣列

# 存取範例
document = documents[0]
nodes = document.nodes

# 節點屬性（透過索引存取 strings）
node_names = [strings[i] for i in nodes.node_name]
node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
backend_node_ids = list(nodes.backend_node_id)
```

#### 使用場景

1. **穿透 closed Shadow DOM** - JavaScript 無法存取的 Shadow DOM
2. **大規模元素搜尋** - 一次取得所有元素，比多次查詢效率高
3. **全頁面分析** - 需要分析整個頁面結構時

#### 範例：搜尋 Shadow DOM 內的按鈕

```python
async def find_buttons_in_shadow_dom(tab):
    """在 Shadow DOM 中搜尋所有按鈕"""
    from nodriver import cdp

    # 捕獲 DOM 快照
    documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
        computed_styles=[],
        include_dom_rects=True
    ))

    if not documents:
        return []

    document = documents[0]
    nodes = document.nodes

    # 提取節點資訊
    node_names = [strings[i] for i in nodes.node_name]
    attributes_list = nodes.attributes
    backend_node_ids = list(nodes.backend_node_id)

    buttons = []

    # 搜尋 BUTTON 元素
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

            buttons.append({
                'backend_node_id': backend_node_ids[i],
                'class': attrs.get('class', ''),
                'disabled': 'disabled' in attrs
            })

    return buttons
```

#### 注意事項

1. **記憶體消耗** - 捕獲整個頁面會佔用記憶體，特別是大型頁面
2. **快照時間點** - 捕獲的是當下狀態，動態內容需要重新捕獲
3. **backend_node_id** - 用於後續操作（需轉換為 node_id）

---

### DOM Domain

**用途：** 元素定位、查詢、操作，包括 Shadow DOM 穿透。

#### 核心命令

##### 1. `get_document` - 取得 DOM 樹

**語法：**

```python
document = await tab.send(cdp.dom.get_document(
    depth=-1,    # -1 = 完整深度, 1 = 只有第一層
    pierce=True  # True = 穿透 Shadow DOM
))
```

**用途：** 取得整個 DOM 樹結構，`pierce=True` 可以穿透 Shadow DOM。

**回傳：** `Node` 物件，包含整個 DOM 樹。

**⚠️ 注意 CBOR Stack Overflow**：
- 使用 `depth=-1` 會遞歸獲取整個 DOM 樹（可能 6000+ 節點）
- 在複雜頁面可能導致 `CBOR: stack limit exceeded` 錯誤
- **建議**：使用 `depth=0` 只獲取根節點，配合 `perform_search()` 按需查詢

##### 2. `perform_search` - 搜尋 Shadow DOM 元素（推薦優先） ⭐

**語法：**

```python
# 執行搜尋（穿透 Shadow DOM）
search_id, result_count = await tab.send(cdp.dom.perform_search(
    query='button.btn-buy',              # CSS selector、XPath 或純文本
    include_user_agent_shadow_dom=True   # 穿透 Shadow DOM
))

# 獲取搜尋結果（node IDs）
node_ids = await tab.send(cdp.dom.get_search_results(
    search_id=search_id,
    from_index=0,
    to_index=result_count
))

# 必須清理搜尋會話
await tab.send(cdp.dom.discard_search_results(search_id=search_id))
```

**用途：** 在整個頁面搜尋元素，自動穿透 Shadow DOM（包括 closed Shadow DOM）。

**參數：**
- `query` (str)：搜尋條件（支援 CSS selector、XPath、純文本）
- `include_user_agent_shadow_dom` (bool, optional)：設為 `True` 時穿透 Shadow DOM

**回傳值：**
- `search_id`：搜尋會話識別碼（用於後續操作）
- `result_count`：找到的元素數量

**三步驟工作流程：**
1. **`perform_search()`** - 執行搜尋，取得 `search_id` 和數量
2. **`get_search_results()`** - 取得搜尋結果的 `node_id` 陣列
3. **`discard_search_results()`** - 清理搜尋會話（釋放資源）

**重要提醒：**
- ⚠️ **必須清理**：完成後必須調用 `discard_search_results()` 釋放 CDP 資源
- ⚠️ **會話失效**：清理後不能再對該 `search_id` 調用 `get_search_results()`

**性能優勢（vs DOMSnapshot）：**
```
Pierce Method (perform_search):
  - 速度：2-5 秒
  - 處理節點：1-10 個（只有匹配結果）
  - 記憶體：~5MB（按需查詢）
  - 第一次成功率：95%+

DOMSnapshot (capture_snapshot):
  - 速度：10-15 秒
  - 處理節點：6000+ 個（整個 DOM 樹）
  - 記憶體：~50MB（全量快照）
  - 第一次成功率：20%
```

**最佳實踐：Primary → Fallback 模式**
```python
# 優先使用 Pierce Method
try:
    search_id, count = await tab.send(cdp.dom.perform_search(
        query='button.btn-buy',
        include_user_agent_shadow_dom=True
    ))

    if count > 0:
        # 找到元素，處理...
        pass
    else:
        # 回退到 DOMSnapshot
        pass

except Exception as e:
    # 發生錯誤，回退到 DOMSnapshot
    pass
```

**📖 深入學習**：查看 **[Shadow DOM Pierce Method 完整指南](shadow_dom_pierce_guide.md)** 了解智慧等待、父元素遍歷等進階技巧。

**參考資料**：
- NoDriver 官方文檔：https://ultrafunkamsterdam.github.io/nodriver/nodriver/cdp/dom.html
- 實作範例：`src/nodriver_tixcraft.py` Line 6368-6724

##### 3. `push_nodes_by_backend_ids_to_frontend` - 轉換 node ID

**語法：**

```python
result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(
    backend_node_ids=[backend_node_id]
))
node_id = result[0]
```

**用途：** 將 `backend_node_id`（從 DOMSnapshot 取得）轉換為 `node_id`（用於後續操作）。

**重要性：** DOMSnapshot 返回 `backend_node_id`，但其他 DOM 命令需要 `node_id`。

##### 3. `scroll_into_view_if_needed` - 滾動至元素

**語法：**

```python
await tab.send(cdp.dom.scroll_into_view_if_needed(
    node_id=node_id
))
```

**用途：** 確保元素在視窗內可見，必要時自動滾動。

**使用時機：** 點擊元素前，確保元素在視窗內。

##### 4. `focus` - 聚焦元素

**語法：**

```python
await tab.send(cdp.dom.focus(node_id=node_id))
```

**用途：** 將焦點設置到指定元素（如輸入框）。

##### 5. `get_box_model` - 取得元素位置

**語法：**

```python
box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))

# 取得元素中心座標
content_quad = box_model.content  # 或 box_model.model.content
x = (content_quad[0] + content_quad[2]) / 2
y = (content_quad[1] + content_quad[5]) / 2
```

**用途：** 取得元素的精確位置（content、padding、border、margin 四個區域的座標）。

**回傳值：** `BoxModel` 物件，包含 `content`、`padding`、`border`、`margin` 四個四邊形座標陣列。

**座標格式：** `[x1, y1, x2, y2, x3, y3, x4, y4]`（四個頂點）

##### 6. `resolve_node` - 解析節點為 RemoteObject

**語法：**

```python
resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))
remote_object_id = resolved.object.object_id
```

**用途：** 將 `node_id` 轉換為 `RemoteObject`，用於 Runtime.callFunctionOn。

##### 7. `get_outer_html` - 取得元素 HTML

**語法：**

```python
result = await tab.send(cdp.dom.get_outer_html(node_id=node_id))
html = result.outer_html
```

**用途：** 取得元素的完整 HTML（包含標籤本身）。

##### 8. `describe_node` - 取得節點詳細資訊

**語法：**

```python
node_desc = await tab.send(cdp.dom.describe_node(
    node_id=node_id,
    depth=1  # 子節點深度
))
```

**用途：** 取得節點的詳細資訊（標籤名、屬性、子節點等）。

#### 使用場景

1. **元素精確定位** - 取得元素位置後模擬滑鼠點擊
2. **Shadow DOM 穿透** - 使用 `get_document(pierce=True)`
3. **元素狀態檢查** - 取得 HTML、屬性進行判斷

#### 完整範例：點擊 Shadow DOM 內的按鈕

```python
async def click_button_in_shadow_dom(tab, backend_node_id):
    """點擊 Shadow DOM 內的按鈕（完整流程）"""
    from nodriver import cdp

    try:
        # 步驟 1: 初始化 DOM（必要步驟）
        await tab.send(cdp.dom.get_document())

        # 步驟 2: 轉換 backend_node_id 為 node_id
        result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(
            backend_node_ids=[backend_node_id]
        ))
        node_id = result[0]
        print(f"Node ID: {node_id}")

        # 步驟 3: 滾動至元素（確保可見）
        await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
        await tab.sleep(0.2)

        # 步驟 4: 聚焦元素
        await tab.send(cdp.dom.focus(node_id=node_id))

        # 步驟 5: 取得元素位置
        box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
        content_quad = box_model.content
        x = (content_quad[0] + content_quad[2]) / 2
        y = (content_quad[1] + content_quad[5]) / 2
        print(f"Click position: ({x:.1f}, {y:.1f})")

        # 步驟 6: 執行點擊（使用 NoDriver 高階 API）
        await tab.mouse_click(x, y)

        print("Button clicked successfully")
        return True

    except Exception as e:
        print(f"Click failed: {e}")
        return False
```

#### 注意事項

1. **必須先呼叫 `get_document()`** - 在使用其他 DOM 命令前初始化
2. **node_id vs backend_node_id** - 注意區分，必要時使用 `push_nodes_by_backend_ids_to_frontend` 轉換
3. **Shadow DOM 穿透** - 使用 `pierce=True` 參數

---

### Input Domain

**用途：** 模擬滑鼠、鍵盤、觸摸輸入，實現真實的使用者操作。

#### 核心命令

##### 1. `dispatch_key_event` - 鍵盤事件

**語法：**

```python
# 按下鍵盤（keyDown）
await tab.send(cdp.input_.dispatch_key_event(
    type_='keyDown',              # 事件類型: 'keyDown', 'keyUp', 'rawKeyDown', 'char'
    code='Enter',                 # 按鍵代碼（如 'KeyA', 'Enter'）
    key='Enter',                  # 按鍵名稱
    text='\r',                    # 輸入的文字（Enter = \r）
    windows_virtual_key_code=13   # Windows 虛擬鍵碼（Enter = 13）
))

# 釋放鍵盤（keyUp）
await tab.send(cdp.input_.dispatch_key_event(
    type_='keyUp',
    code='Enter',
    key='Enter',
    text='\r',
    windows_virtual_key_code=13
))
```

**參數說明：**

| 參數 | 說明 | 範例 |
|------|------|------|
| `type_` | 事件類型 | `'keyDown'`, `'keyUp'`, `'char'` |
| `code` | 物理按鍵代碼 | `'Enter'`, `'KeyA'`, `'Space'` |
| `key` | 按鍵邏輯名稱 | `'Enter'`, `'a'`, `' '` |
| `text` | 輸入的字元 | `'\r'`, `'a'`, `' '` |
| `windows_virtual_key_code` | Windows 虛擬鍵碼 | Enter=13, Space=32, A=65 |

**常用按鍵代碼：**

| 按鍵 | code | key | text | windows_virtual_key_code |
|------|------|-----|------|--------------------------|
| Enter | `'Enter'` | `'Enter'` | `'\r'` | 13 |
| Space | `'Space'` | `' '` | `' '` | 32 |
| Tab | `'Tab'` | `'Tab'` | `'\t'` | 9 |
| Escape | `'Escape'` | `'Escape'` | `''` | 27 |

##### 2. `dispatch_mouse_event` - 滑鼠事件

**語法：**

```python
# 滑鼠按下（mousePressed）
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mousePressed',  # 事件類型: 'mousePressed', 'mouseReleased', 'mouseMoved'
    x=100,                 # X 座標
    y=200,                 # Y 座標
    button='left',         # 按鈕: 'left', 'right', 'middle'
    click_count=1          # 點擊次數（1=單擊, 2=雙擊）
))

# 滑鼠釋放（mouseReleased）
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mouseReleased',
    x=100,
    y=200,
    button='left',
    click_count=1
))
```

**NoDriver 高階 API（推薦）：**

NoDriver 提供更簡潔的滑鼠點擊方法，內部使用 CDP：

```python
# 單擊
await tab.mouse_click(x=100, y=200)

# 雙擊
await tab.mouse_click(x=100, y=200, click_count=2)
```

##### 3. 其他輸入命令

**觸摸事件：**

```python
# dispatch_touch_event - 觸摸事件（touchStart, touchEnd, touchMove）
await tab.send(cdp.input_.dispatch_touch_event(
    type_='touchStart',
    touch_points=[{'x': 100, 'y': 200}]
))
```

**滾動手勢：**

```python
# synthesize_scroll_gesture - 模擬滾動
await tab.send(cdp.input_.synthesize_scroll_gesture(
    x=100,
    y=200,
    x_distance=0,
    y_distance=-500  # 負數 = 向上滾動
))
```

#### 使用場景

1. **模擬鍵盤輸入** - 特別是特殊鍵（Enter、Tab、Escape）
2. **精確滑鼠點擊** - 結合 `get_box_model` 取得座標後點擊
3. **防止被偵測** - CDP 輸入比 JavaScript 更難被反爬蟲偵測

#### 範例：完整的點擊流程

```python
async def click_element_with_cdp(tab, node_id):
    """使用 CDP 完整點擊元素流程"""
    from nodriver import cdp

    try:
        # 步驟 1: 滾動至元素
        await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
        await tab.sleep(0.2)

        # 步驟 2: 聚焦元素
        await tab.send(cdp.dom.focus(node_id=node_id))

        # 步驟 3: 取得元素位置
        box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
        content_quad = box_model.content
        x = (content_quad[0] + content_quad[2]) / 2
        y = (content_quad[1] + content_quad[5]) / 2

        # 步驟 4: 執行點擊（使用 NoDriver 高階 API）
        await tab.mouse_click(x, y)

        # 或使用原生 CDP 命令（更底層）
        # await tab.send(cdp.input_.dispatch_mouse_event(
        #     type_='mousePressed', x=x, y=y, button='left', click_count=1
        # ))
        # await tab.send(cdp.input_.dispatch_mouse_event(
        #     type_='mouseReleased', x=x, y=y, button='left', click_count=1
        # ))

        print(f"Clicked at ({x:.1f}, {y:.1f})")
        return True

    except Exception as e:
        print(f"Click failed: {e}")
        return False
```

#### 範例：模擬按下 Enter 鍵

```python
async def press_enter_key(tab):
    """模擬按下並釋放 Enter 鍵"""
    from nodriver import cdp

    # 按下 Enter
    await tab.send(cdp.input_.dispatch_key_event(
        type_='keyDown',
        code='Enter',
        key='Enter',
        text='\r',
        windows_virtual_key_code=13
    ))

    # 釋放 Enter
    await tab.send(cdp.input_.dispatch_key_event(
        type_='keyUp',
        code='Enter',
        key='Enter',
        text='\r',
        windows_virtual_key_code=13
    ))

    print("Enter key pressed")
```

#### 注意事項

1. **Input Domain 命名** - 在 Python 中是 `cdp.input_`（有底線，避免與 `input()` 衝突）
2. **keyDown + keyUp** - 完整的按鍵操作需要兩個事件
3. **座標系統** - (0, 0) 是視窗左上角，座標以像素為單位
4. **與高階 API 的選擇** - 優先使用 NoDriver 高階 API（如 `tab.mouse_click()`），只有在需要更精細控制時才使用原生 CDP

---

### Network Domain

**用途：** 網路請求管理、Cookie 操作、請求攔截。

#### 核心命令

##### 1. `set_cookie` - 設置 Cookie

**語法：**

```python
result = await tab.send(cdp.network.set_cookie(
    name='cookie_name',           # Cookie 名稱
    value='cookie_value',         # Cookie 值
    domain='.example.com',        # 域名（加 . 表示包含子域名）
    path='/',                     # 路徑
    secure=True,                  # 是否僅 HTTPS
    http_only=True,               # 是否僅 HTTP（不可被 JavaScript 存取）
    same_site='None'              # SameSite 屬性: 'Strict', 'Lax', 'None'
))

# result.success = True 表示設置成功
```

**參數說明：**

| 參數 | 說明 | 範例 |
|------|------|------|
| `name` | Cookie 名稱 | `'SID'`, `'ibonqware'` |
| `value` | Cookie 值 | `'abc123...'` |
| `domain` | 域名 | `.tixcraft.com`（含子域名）<br>`tixcraft.com`（僅主域名）|
| `path` | 路徑 | `'/'`（根路徑） |
| `secure` | 僅 HTTPS | `True` / `False` |
| `http_only` | 僅 HTTP | `True` / `False` |
| `same_site` | SameSite 策略 | `'Strict'`, `'Lax'`, `'None'` |

##### 2. `CookieParam` - Cookie 參數物件

**語法：**

```python
from nodriver import cdp

# 建立 Cookie 參數物件
cookie = cdp.network.CookieParam(
    name='SID',
    value='abc123',
    domain='.tixcraft.com',
    path='/',
    http_only=False,
    secure=True
)

# 批次設置多個 Cookie（使用 NoDriver API）
cookies = [cookie1, cookie2, cookie3]
await driver.cookies.set_all(cookies)
```

**用途：** 批次管理多個 Cookie 時使用。

##### 3. 其他 Network 命令

**取得 Cookie：**

```python
# get_cookies - 取得當前頁面的所有 Cookie
cookies = await tab.send(cdp.network.get_cookies())

for cookie in cookies:
    print(f"{cookie.name}={cookie.value}")
```

**刪除 Cookie：**

```python
# delete_cookies - 刪除特定 Cookie
await tab.send(cdp.network.delete_cookies(
    name='cookie_name',
    domain='.example.com',
    path='/'
))
```

**清除所有 Cookie：**

```python
# clear_browser_cookies - 清除所有 Cookie
await tab.send(cdp.network.clear_browser_cookies())
```

#### 使用場景

1. **自動登入** - 設置已保存的 Cookie 實現免密碼登入
2. **會話管理** - 在不同頁面間保持登入狀態
3. **繞過限制** - 某些網站檢查特定 Cookie

#### 範例：設置 TixCraft Cookie 實現自動登入

```python
async def set_tixcraft_cookie(driver, tixcraft_sid):
    """設置 TixCraft SID Cookie 實現自動登入"""
    from nodriver import cdp

    try:
        # 取得現有 Cookie
        cookies = list(await driver.cookies.get_all())

        # 檢查 SID Cookie 是否已存在
        is_cookie_exist = False
        for cookie in cookies:
            if cookie.name == "SID" and ".tixcraft.com" in cookie.domain:
                # 更新現有 Cookie
                cookie.value = tixcraft_sid
                is_cookie_exist = True
                break

        # 若不存在則新增
        if not is_cookie_exist:
            new_cookie = cdp.network.CookieParam(
                name='SID',
                value=tixcraft_sid,
                domain='.tixcraft.com',  # 包含所有子域名
                path='/',
                http_only=False,
                secure=True
            )
            cookies.append(new_cookie)

        # 批次設置所有 Cookie
        await driver.cookies.set_all(cookies)

        print("TixCraft SID cookie set successfully")
        return True

    except Exception as e:
        print(f"Failed to set cookie: {e}")
        return False
```

#### 範例：設置 ibon Cookie

```python
async def set_ibon_cookie(tab, ibonqware):
    """設置 ibon Cookie"""
    from nodriver import cdp

    try:
        result = await tab.send(cdp.network.set_cookie(
            name='ibonqware',
            value=ibonqware,
            domain='.ibon.com.tw',
            path='/',
            secure=True,
            http_only=True
        ))

        if result.success:
            print("ibon cookie set successfully")
            return True
        else:
            print("Failed to set ibon cookie")
            return False

    except Exception as e:
        print(f"Error setting ibon cookie: {e}")
        return False
```

#### 注意事項

1. **domain 前綴** - `.example.com` 包含所有子域名，`example.com` 僅主域名
2. **secure 與 http_only** - 根據目標網站的要求設置，錯誤的設置會導致 Cookie 無效
3. **same_site 屬性** - Chrome 預設為 `'Lax'`，跨站請求需要設置為 `'None'`（且必須 `secure=True`）
4. **時機** - 通常在導航到目標網站前設置 Cookie

---

### Page Domain

**用途：** 頁面導航、截圖、生命週期管理、彈窗處理。

#### 核心命令

##### 1. `handle_java_script_dialog` - 處理彈窗

**語法：**

```python
# 接受彈窗（點擊「確定」）
await tab.send(cdp.page.handle_java_script_dialog(accept=True))

# 拒絕彈窗（點擊「取消」）
await tab.send(cdp.page.handle_java_script_dialog(accept=False))

# 帶輸入的彈窗（prompt）
await tab.send(cdp.page.handle_java_script_dialog(
    accept=True,
    prompt_text='使用者輸入'
))
```

**用途：** 處理 JavaScript 彈窗（`alert`, `confirm`, `prompt`）。

**使用時機：** 當頁面彈出 alert/confirm/prompt 時，必須處理才能繼續操作。

##### 2. `navigate` - 導航至 URL

**語法：**

```python
result = await tab.send(cdp.page.navigate(url='https://example.com'))
```

**NoDriver 高階 API（推薦）：**

```python
await tab.get('https://example.com')
```

##### 3. `capture_screenshot` - 截圖

**語法：**

```python
screenshot = await tab.send(cdp.page.capture_screenshot(
    format_='png',              # 格式: 'png', 'jpeg', 'webp'
    quality=80,                 # JPEG 品質（1-100）
    clip={                      # 截取特定區域（可選）
        'x': 0,
        'y': 0,
        'width': 800,
        'height': 600,
        'scale': 1
    },
    capture_beyond_viewport=True  # 截取超出視窗的內容
))

# screenshot 是 base64 編碼的圖片資料
import base64
image_data = base64.b64decode(screenshot)
```

**NoDriver 高階 API（推薦）：**

```python
# 截取整個頁面
await tab.save_screenshot('screenshot.png')

# 截取特定元素
await element.save_screenshot('element.png')
```

##### 4. 其他 Page 命令

**重新載入頁面：**

```python
# reload - 重新載入頁面
await tab.send(cdp.page.reload(ignore_cache=True))
```

**啟用/禁用 Page 事件：**

```python
# enable - 啟用 Page domain 通知
await tab.send(cdp.page.enable())

# disable - 禁用 Page domain 通知
await tab.send(cdp.page.disable())
```

**列印為 PDF：**

```python
# print_to_pdf - 將頁面列印為 PDF
pdf_data = await tab.send(cdp.page.print_to_pdf(
    landscape=False,            # 橫向/直向
    display_header_footer=False,
    print_background=True
))
```

#### 使用場景

1. **彈窗處理** - 自動接受/拒絕 alert/confirm
2. **截圖記錄** - 記錄操作過程或錯誤畫面
3. **頁面控制** - 導航、重新載入

#### 範例：處理驗證碼錯誤彈窗

```python
async def handle_captcha_error_dialog(tab):
    """處理驗證碼錯誤後的 alert 彈窗"""
    from nodriver import cdp

    try:
        # 接受彈窗（點擊確定）
        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
        print("Alert dialog dismissed")
        return True

    except Exception as e:
        print(f"No dialog to handle or error: {e}")
        return False
```

#### 範例：截取特定區域並保存

```python
async def capture_captcha_area(tab, x, y, width, height):
    """截取驗證碼區域"""
    from nodriver import cdp
    import base64

    try:
        screenshot = await tab.send(cdp.page.capture_screenshot(
            format_='png',
            clip={
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'scale': 1
            }
        ))

        # 解碼並保存
        image_data = base64.b64decode(screenshot)
        with open('captcha.png', 'wb') as f:
            f.write(image_data)

        print("Captcha screenshot saved")
        return image_data

    except Exception as e:
        print(f"Screenshot failed: {e}")
        return None
```

#### 注意事項

1. **彈窗必須處理** - 出現彈窗時必須呼叫 `handle_java_script_dialog`，否則頁面會被阻塞
2. **截圖時機** - 確保頁面載入完成再截圖
3. **NoDriver 高階 API** - 優先使用 `tab.get()`, `tab.save_screenshot()` 等高階方法

---

### Runtime Domain

**用途：** JavaScript 執行、物件操作、遠端函數呼叫。

#### 核心命令

##### 1. `evaluate` - 執行 JavaScript

**語法：**

```python
result = await tab.send(cdp.runtime.evaluate(
    expression='document.title',  # JavaScript 表達式
    return_by_value=True           # True = 返回值, False = 返回物件引用
))

value = result.result.value
```

**NoDriver 高階 API（推薦）：**

```python
# 執行 JavaScript 並取得返回值
result = await tab.evaluate('document.title')
print(result)  # 直接得到值
```

##### 2. `call_function_on` - 在物件上呼叫函數

**語法：**

```python
from nodriver import cdp

# 首先解析 node 為 RemoteObject
resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))
remote_object_id = resolved.object.object_id

# 在該物件上呼叫函數
result = await tab.send(cdp.runtime.call_function_on(
    function_declaration='function() { this.click(); return true; }',
    object_id=remote_object_id,
    return_by_value=True
))

success = result.result.value
```

**用途：** 在特定物件（如 DOM 元素）上執行函數，特別適合操作 Shadow DOM 內的元素。

##### 3. 其他 Runtime 命令

**取得物件屬性：**

```python
# get_properties - 取得物件的所有屬性
properties = await tab.send(cdp.runtime.get_properties(
    object_id=remote_object_id,
    own_properties=True
))
```

**釋放物件：**

```python
# release_object - 釋放遠端物件引用
await tab.send(cdp.runtime.release_object(object_id=remote_object_id))
```

#### 使用場景

1. **執行 JavaScript** - 簡單的 DOM 查詢或操作
2. **物件方法呼叫** - 在特定元素上呼叫方法（如 `click()`）
3. **複雜操作** - 結合 DOM API 實現精細控制

#### 範例：在 Shadow DOM 元素上呼叫 click()

```python
async def click_element_via_runtime(tab, node_id):
    """使用 Runtime.callFunctionOn 點擊元素"""
    from nodriver import cdp
    from nodriver.cdp import runtime

    try:
        # 步驟 1: 解析 node_id 為 RemoteObject
        resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))

        # 取得 object_id
        if hasattr(resolved, 'object'):
            remote_object_id = resolved.object.object_id
        else:
            raise Exception("Could not resolve node to RemoteObject")

        # 步驟 2: 在該物件上呼叫 click() 方法
        result = await tab.send(runtime.call_function_on(
            function_declaration='function() { this.click(); return true; }',
            object_id=remote_object_id,
            return_by_value=True
        ))

        print("Element clicked via Runtime.callFunctionOn")
        return True

    except Exception as e:
        print(f"Click failed: {e}")
        return False
```

#### 注意事項

1. **優先使用高階 API** - `tab.evaluate()` 比直接使用 CDP 更簡潔
2. **RemoteObject** - `call_function_on` 需要 `object_id`，必須先使用 `resolve_node` 轉換
3. **記憶體管理** - 長時間運行時記得釋放不再使用的物件

---

## 快速查詢表

### 按需求分類

| 需求 | CDP 命令 | 說明 | 範例位置 |
|------|---------|------|---------|
| **穿透 Shadow DOM** | `cdp.dom_snapshot.capture_snapshot()` | 平坦化所有 Shadow DOM 結構 | [範例 1](#範例-1搜尋-shadow-dom-內的按鈕domsnapshot) |
| **元素精確點擊** | `cdp.dom.get_box_model()` + `tab.mouse_click()` | 取得座標後點擊 | [範例 2](#範例-2點擊-shadow-dom-內的按鈕完整流程) |
| **鍵盤輸入** | `cdp.input_.dispatch_key_event()` | 模擬按鍵（Enter、Tab 等）| [範例 3](#範例-3模擬按下-enter-鍵) |
| **設置 Cookie** | `cdp.network.set_cookie()` | 實現自動登入 | [範例 4](#範例-4設置-cookie-實現自動登入) |
| **處理彈窗** | `cdp.page.handle_java_script_dialog()` | 接受/拒絕 alert/confirm | [範例 5](#範例-5處理驗證碼錯誤彈窗) |
| **元素滾動** | `cdp.dom.scroll_into_view_if_needed()` | 滾動至元素可見 | [範例 2](#範例-2點擊-shadow-dom-內的按鈕完整流程) |
| **取得元素 HTML** | `cdp.dom.get_outer_html()` | 取得元素完整 HTML | - |
| **截圖** | `cdp.page.capture_screenshot()` | 全頁面或區域截圖 | [範例 6](#範例-6截取驗證碼區域) |
| **執行 JavaScript** | `tab.evaluate()` | 簡單 DOM 查詢 | - |
| **在元素上呼叫函數** | `cdp.runtime.call_function_on()` | 在特定物件上執行函數 | [範例 7](#範例-7使用-runtime-點擊元素) |

### 按 Domain 分類

| Domain | 常用命令 | 使用頻率 |
|--------|---------|---------|
| **DOMSnapshot** | `capture_snapshot()` | ⭐⭐⭐ |
| **DOM** | `get_document()`, `get_box_model()`, `scroll_into_view_if_needed()`, `focus()`, `push_nodes_by_backend_ids_to_frontend()` | ⭐⭐⭐ |
| **Input** | `dispatch_key_event()`, `dispatch_mouse_event()` | ⭐⭐⭐ |
| **Network** | `set_cookie()`, `get_cookies()` | ⭐⭐ |
| **Page** | `handle_java_script_dialog()`, `capture_screenshot()`, `navigate()` | ⭐⭐ |
| **Runtime** | `evaluate()`, `call_function_on()` | ⭐ |

---

## 實際程式碼範例

### 範例 1：搜尋 Shadow DOM 內的按鈕（DOMSnapshot）

**場景：** ibon 購票平台的按鈕位於 closed Shadow DOM 內，JavaScript 無法存取。

```python
async def find_ibon_purchase_buttons(tab):
    """
    使用 DOMSnapshot 穿透 Shadow DOM 搜尋購票按鈕
    優勢：可存取 closed Shadow DOM，JavaScript 無法做到
    """
    from nodriver import cdp

    try:
        # 步驟 1：捕獲平坦化的 DOM 結構
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_dom_rects=True
        ))

        if not documents:
            return []

        document = documents[0]
        nodes = document.nodes

        # 步驟 2：提取節點資訊
        node_names = [strings[i] for i in nodes.node_name]
        node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
        attributes_list = nodes.attributes
        backend_node_ids = list(nodes.backend_node_id)

        purchase_buttons = []

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
                if 'btn-buy' in button_class or 'ng-tns-c57' in button_class:
                    purchase_buttons.append({
                        'backend_node_id': backend_node_ids[i],
                        'class': button_class,
                        'disabled': 'disabled' in attrs,
                        'text': node_values[i] if i < len(node_values) else ''
                    })

        print(f"Found {len(purchase_buttons)} purchase buttons")
        return purchase_buttons

    except Exception as e:
        print(f"Search failed: {e}")
        return []
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

---

### 範例 2：點擊 Shadow DOM 內的按鈕（完整流程）

**場景：** 在找到按鈕的 `backend_node_id` 後，執行點擊操作。

```python
async def click_ibon_purchase_button(tab, backend_node_id):
    """
    點擊 ibon 購票按鈕（完整 CDP 流程）
    步驟：backend_node_id → node_id → 滾動 → 聚焦 → 取得座標 → 點擊
    """
    from nodriver import cdp

    try:
        # 步驟 1：初始化 DOM（必要步驟）
        await tab.send(cdp.dom.get_document())

        # 步驟 2：轉換 backend_node_id 為 node_id
        result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(
            backend_node_ids=[backend_node_id]
        ))
        node_id = result[0]
        print(f"[IBON] Button node_id: {node_id}")

        # 步驟 3：滾動至元素（確保可見）
        await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
        await tab.sleep(0.2)

        # 步驟 4：聚焦元素
        await tab.send(cdp.dom.focus(node_id=node_id))
        print(f"[IBON] Element focused")

        # 步驟 5：取得元素位置
        box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))

        # box_model.content 是 [x1, y1, x2, y2, x3, y3, x4, y4]（四個頂點）
        content_quad = box_model.content
        x = (content_quad[0] + content_quad[2]) / 2  # 中心 X
        y = (content_quad[1] + content_quad[5]) / 2  # 中心 Y
        print(f"[IBON] Click position: ({x:.1f}, {y:.1f})")

        # 步驟 6：執行點擊（使用 NoDriver 高階 API）
        await tab.mouse_click(x, y)

        # 等待頁面跳轉
        await tab.sleep(1.0)

        print(f"[IBON] Button clicked successfully")
        return True

    except Exception as e:
        print(f"[IBON] Click failed: {e}")
        return False
```

**流程圖：**

```
DOMSnapshot 搜尋按鈕
    ↓ 取得 backend_node_id
DOM.push_nodes_by_backend_ids_to_frontend
    ↓ 轉換為 node_id
DOM.scroll_into_view_if_needed
    ↓ 滾動至可見
DOM.focus
    ↓ 聚焦元素
DOM.get_box_model
    ↓ 取得座標
NoDriver mouse_click / CDP Input.dispatch_mouse_event
    ↓ 執行點擊
完成
```

---

### 範例 3：模擬按下 Enter 鍵

**場景：** 在輸入驗證碼後按下 Enter 送出表單。

```python
async def submit_form_with_enter(tab):
    """
    模擬按下 Enter 鍵送出表單
    完整按鍵操作 = keyDown + keyUp
    """
    from nodriver import cdp

    try:
        # 按下 Enter（keyDown）
        await tab.send(cdp.input_.dispatch_key_event(
            type_='keyDown',
            code='Enter',
            key='Enter',
            text='\r',
            windows_virtual_key_code=13
        ))

        # 釋放 Enter（keyUp）
        await tab.send(cdp.input_.dispatch_key_event(
            type_='keyUp',
            code='Enter',
            key='Enter',
            text='\r',
            windows_virtual_key_code=13
        ))

        print("[INPUT] Enter key pressed")
        await tab.sleep(1.0)  # 等待表單送出

        return True

    except Exception as e:
        print(f"[INPUT] Key press failed: {e}")
        return False
```

**常用按鍵參考：**

```python
# Tab 鍵
await tab.send(cdp.input_.dispatch_key_event(
    type_='keyDown', code='Tab', key='Tab', text='\t', windows_virtual_key_code=9
))

# Escape 鍵
await tab.send(cdp.input_.dispatch_key_event(
    type_='keyDown', code='Escape', key='Escape', text='', windows_virtual_key_code=27
))

# Space 鍵
await tab.send(cdp.input_.dispatch_key_event(
    type_='keyDown', code='Space', key=' ', text=' ', windows_virtual_key_code=32
))
```

---

### 範例 4：設置 Cookie 實現自動登入

**場景：** 在訪問 TixCraft 前設置已保存的 SID Cookie，實現免密碼登入。

```python
async def auto_login_tixcraft(driver, tixcraft_sid):
    """
    設置 TixCraft SID Cookie 實現自動登入
    步驟：取得現有 Cookie → 更新或新增 → 批次設置
    """
    from nodriver import cdp

    try:
        # 步驟 1：取得現有 Cookie
        cookies = list(await driver.cookies.get_all())

        # 步驟 2：檢查 SID Cookie 是否已存在
        is_cookie_exist = False
        for cookie in cookies:
            if cookie.name == "SID" and ".tixcraft.com" in cookie.domain:
                # 更新現有 Cookie
                cookie.value = tixcraft_sid
                is_cookie_exist = True
                print("[COOKIE] Updated existing SID cookie")
                break

        # 步驟 3：若不存在則新增
        if not is_cookie_exist:
            new_cookie = cdp.network.CookieParam(
                name='SID',
                value=tixcraft_sid,
                domain='.tixcraft.com',  # 加 . 表示包含所有子域名
                path='/',
                http_only=False,
                secure=True
            )
            cookies.append(new_cookie)
            print("[COOKIE] Added new SID cookie")

        # 步驟 4：批次設置所有 Cookie
        await driver.cookies.set_all(cookies)

        print("[COOKIE] TixCraft auto-login cookie set successfully")
        return True

    except Exception as e:
        print(f"[COOKIE] Failed to set cookie: {e}")
        return False
```

**ibon 平台 Cookie 設置（單一 Cookie）：**

```python
async def set_ibon_cookie(tab, ibonqware):
    """設置 ibon Cookie（使用 CDP 直接設置）"""
    from nodriver import cdp

    try:
        result = await tab.send(cdp.network.set_cookie(
            name='ibonqware',
            value=ibonqware,
            domain='.ibon.com.tw',
            path='/',
            secure=True,
            http_only=True
        ))

        if result.success:
            print("[COOKIE] ibon cookie set successfully")
            return True
        else:
            print("[COOKIE] Failed to set ibon cookie")
            return False

    except Exception as e:
        print(f"[COOKIE] Error: {e}")
        return False
```

---

### 範例 5：處理驗證碼錯誤彈窗

**場景：** 驗證碼輸入錯誤後，頁面彈出 alert 提示，必須點擊確定才能繼續。

```python
async def handle_captcha_error_dialog(tab):
    """
    處理驗證碼錯誤後的 alert 彈窗
    接受彈窗 = 點擊「確定」按鈕
    """
    from nodriver import cdp

    try:
        # 接受彈窗（點擊確定）
        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
        print("[DIALOG] Alert dismissed")
        return True

    except Exception as e:
        # 如果沒有彈窗，會拋出異常（正常情況）
        print(f"[DIALOG] No dialog to handle or error: {e}")
        return False
```

**使用時機範例：**

```python
# 在驗證碼輸入失敗後，嘗試關閉可能的錯誤彈窗
try:
    await tab.send(cdp.page.handle_java_script_dialog(accept=True))
    print("[CAPTCHA] Dismissed error alert, retrying...")
except:
    pass  # 沒有彈窗，繼續執行
```

---

### 範例 6：截取驗證碼區域

**場景：** 截取頁面上驗證碼圖片的特定區域，用於 OCR 辨識。

```python
async def capture_captcha_image(tab, x, y, width, height):
    """
    截取驗證碼區域並保存為圖片
    參數：x, y = 左上角座標, width, height = 寬高
    """
    from nodriver import cdp
    import base64
    from PIL import Image
    import io

    try:
        # 步驟 1：使用 CDP 截取特定區域
        screenshot = await tab.send(cdp.page.capture_screenshot(
            format_='png',
            clip={
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'scale': 1  # 縮放比例
            }
        ))

        # 步驟 2：解碼 base64 圖片
        image_data = base64.b64decode(screenshot)

        # 步驟 3：使用 PIL 開啟並處理圖片
        image = Image.open(io.BytesIO(image_data))

        # 步驟 4：保存圖片
        image.save('captcha.png')
        print(f"[SCREENSHOT] Captcha saved: {width}x{height} at ({x}, {y})")

        return image_data

    except Exception as e:
        print(f"[SCREENSHOT] Failed: {e}")
        return None
```

**完整頁面截圖（使用 NoDriver 高階 API）：**

```python
# 方法 1：截取完整頁面
await tab.save_screenshot('full_page.png')

# 方法 2：截取特定元素
element = await tab.find('img.captcha')
await element.save_screenshot('captcha_element.png')
```

---

### 範例 7：使用 Runtime 點擊元素

**場景：** 在 Shadow DOM 元素上呼叫 JavaScript `click()` 方法。

```python
async def click_element_via_runtime(tab, node_id):
    """
    使用 Runtime.callFunctionOn 在元素上呼叫 click() 方法
    適用於某些情況下 CDP 滑鼠點擊無效的場景
    """
    from nodriver import cdp
    from nodriver.cdp import runtime

    try:
        # 步驟 1：解析 node_id 為 RemoteObject
        resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))

        # 步驟 2：取得 object_id
        if hasattr(resolved, 'object'):
            remote_object_id = resolved.object.object_id
        elif hasattr(resolved, 'object_id'):
            remote_object_id = resolved.object_id
        else:
            raise Exception("Could not resolve node to RemoteObject")

        print(f"[RUNTIME] Resolved object_id: {remote_object_id}")

        # 步驟 3：在該物件上呼叫 click() 方法
        result = await tab.send(runtime.call_function_on(
            function_declaration='function() { this.click(); return true; }',
            object_id=remote_object_id,
            return_by_value=True
        ))

        print("[RUNTIME] Element clicked via Runtime.callFunctionOn")
        return True

    except Exception as e:
        print(f"[RUNTIME] Click failed: {e}")
        return False
```

**何時使用：**
- CDP 滑鼠點擊無效時的備用方案
- 需要在特定物件上執行自訂函數
- 操作 closed Shadow DOM 內的元素

---

## 參考資源

### 官方文件

- **CDP 官方文件**：https://chromedevtools.github.io/devtools-protocol/
  - 完整的 Domain、命令、事件參考
  - 各版本協議（tip-of-tree, stable, v1.3）

- **NoDriver 官方文件**：https://ultrafunkamsterdam.github.io/nodriver/
  - NoDriver Python API 參考
  - CDP 整合說明

### 專案內交叉引用

- **NoDriver API 使用指南** - `nodriver_api_guide.md`
  - NoDriver 高階 API 參考
  - NoDriver vs JavaScript 使用決策
  - Shadow DOM 處理範例

- **除錯方法論** - `debugging_methodology.md`
  - 除錯流程與工具
  - 常見問題排查

- **程式碼結構** - `structure.md`
  - 函數索引與位置
  - 各平台實作分析

- **測試執行指南** - `testing_execution_guide.md`
  - 測試流程與驗證方法
  - 邏輯流程檢查

### 常見問題快速連結

| 問題 | 相關文件 | 章節 |
|------|---------|------|
| Shadow DOM 無法存取 | 本文件 | [DOMSnapshot Domain](#domsnapshot-domain) |
| CDP 點擊失敗 | `nodriver_api_guide.md` | CDP Click Troubleshooting |
| Cookie 設定無效 | 本文件 | [Network Domain](#network-domain) |
| 彈窗無法關閉 | 本文件 | [Page Domain](#page-domain) |
| ibon 特定問題 | `ibon_nodriver_fixes_2025-10-03.md` | - |

### 學習路徑建議

**初學者：**
1. 閱讀 [CDP 概述](#cdp-概述) 了解基本概念
2. 查看 [基本使用語法](#基本使用語法) 學習如何發送命令
3. 參考 [快速查詢表](#快速查詢表) 找到常用命令
4. 執行 [實際程式碼範例](#實際程式碼範例) 進行練習

**進階開發者：**
1. 深入研究 [核心 Domain 詳解](#核心-domain-詳解)
2. 閱讀專案程式碼中的 CDP 使用（搜尋 `cdp.`）
3. 參考 CDP 官方文件了解完整參數和回傳值
4. 實驗不同 Domain 的組合使用

---

**文件版本：** 2025-10-25
**適用專案：** Tickets Hunter - 多平台搶票自動化系統
**維護者：** 開發團隊
