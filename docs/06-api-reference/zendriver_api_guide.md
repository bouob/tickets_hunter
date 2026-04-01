# Zendriver API 使用指南

**文件說明**：Zendriver（nodriver fork）的 API 參考，專注於本專案使用的功能和與 nodriver 的差異
**最後更新**：2026-03-14
**zendriver 版本**：0.15.3
**官方文件**：https://zendriver.dev/

---

> **重要**：本文件是 nodriver_api_guide.md 的 zendriver 版本。核心原則（CDP 優先、Shadow DOM 處理等）不變，僅記錄 API 差異。

**相關文件**：
- **[CDP Protocol 參考指南](cdp_protocol_reference.md)** -- Chrome DevTools Protocol 完整參考
- **[nodriver API 指南](nodriver_api_guide.md)** -- 舊版參考（遷移前）
- **[遷移研究報告](../internal/reference/chrome-nodriver-compatibility-research.md)** -- 完整相容性分析

---

## 1. Import 對照

```python
# nodriver（舊）                          # zendriver（新）
import nodriver as uc                     import zendriver as uc
from nodriver import cdp                  from zendriver import cdp
from nodriver.core.config import Config   from zendriver.core.config import Config
```

---

## 2. 啟動與事件迴圈

### 事件迴圈（Breaking Change #1）

```python
# nodriver（舊）-- loop() 在 zendriver 中已棄用
uc.loop().run_until_complete(main(args))

# zendriver（新）
import asyncio
asyncio.run(main(args))
```

### 瀏覽器啟動

```python
# 完全相容，不需改動
driver = await uc.start(conf)

# zendriver 新增參數（可選）
driver = await uc.start(
    conf,
    browser="chrome",       # 新增：指定瀏覽器類型
    user_agent="custom_ua"  # 新增：自訂 User-Agent
)
```

---

## 3. Config 參數對照

```python
from zendriver.core.config import Config

conf = Config(
    # === 完全相容的參數 ===
    browser_args=browser_args,           # list[str]
    headless=False,                      # bool
    browser_executable_path=chrome_path, # str | None
    host="127.0.0.1",                    # str（MCP 連線模式）
    port=9222,                           # int（MCP 連線模式）

    # === 行為差異的參數 ===
    lang="zh-TW",                        # nodriver 預設 "en-US"，zendriver 預設 None
                                         # 專案已明確傳入，不受影響

    sandbox=True,                        # nodriver 用 no_sandbox（但被 **kwargs 吞掉）
                                         # zendriver 同樣有 sandbox 參數
                                         # 遷移時修正：sandbox=not no_sandbox

    # === zendriver 新增參數 ===
    browser="auto",                      # "chrome" | "brave" | "auto"
    user_agent=None,                     # 自訂 User-Agent
    disable_webrtc=True,                 # 防 WebRTC IP 洩漏（預設啟用）
    disable_webgl=False,                 # 停用 WebGL
    browser_connection_timeout=0.25,     # 連線逾時（秒）
    browser_connection_max_tries=10,     # 最大重試次數
)

# 屬性存取（相容）
conf.user_data_dir                       # 使用者資料目錄
conf.add_extension(path)                 # 載入擴充功能
```

---

## 4. Tab API 對照

### 100% 相容（不需改動）

```python
# 導航
await tab.get(url)                           # 導航到 URL
await tab.reload()                           # 重新載入
await tab.close()                            # 關閉分頁

# 元素查找
el = await tab.query_selector('selector')    # 查找單個元素
els = await tab.query_selector_all('selector')  # 查找多個元素
el = await tab.find('text', timeout=10)      # 依文字查找

# JS 執行
result = await tab.evaluate('js_code')       # 執行 JavaScript
result = await tab.js_dumps('obj_name')      # JSON dump
content = await tab.get_content()            # 取得頁面 HTML

# 視窗
await tab.set_window_size(1024, 768)         # 設定視窗大小

# 等待
await tab.sleep(seconds)                     # 非同步等待

# CDP
result = await tab.send(cdp.dom.get_document())  # 發送 CDP 命令

# 事件
tab.add_handler(event_type, handler)         # 新增事件處理器

# 滑鼠
await tab.mouse_click(x, y)                 # 點擊
await tab.mouse_move(x, y)                  # 移動

# Cloudflare
await tab.verify_cf()                        # Cloudflare 驗證
```

### 有差異的 API

```python
# --- Breaking Change #3: remove_handler 改名 ---
# nodriver（舊）
tab.remove_handler(event_type, handler)

# zendriver（新）
tab.remove_handlers(event_type)              # 注意：複數形式

# --- Breaking Change #4: evaluate 預設值不同 ---
# nodriver: return_by_value=False（回傳 RemoteObject）
# zendriver: return_by_value=True（回傳實際值）
result = await tab.evaluate('document.title')
# nodriver: result 是 RemoteObject，需要 parse_nodriver_result() 轉換
# zendriver: result 直接是 "Page Title" 字串

# 如需保持 nodriver 行為：
result = await tab.evaluate('document.title', return_by_value=False)
```

### zendriver 新增 API

```python
# 導航
await tab.back()                             # 上一頁
await tab.forward()                          # 下一頁

# 元素查找（新增）
el = await tab.select('selector', timeout=10)        # 等待 + 查找
els = await tab.select_all('selector', timeout=10)   # 等待 + 查找全部
els = await tab.xpath('//button[@class="buy"]')      # XPath 查找

# 截圖
b64 = await tab.screenshot_b64()             # Base64 截圖
await tab.save_screenshot('path.png')        # 儲存截圖

# PDF
pdf = await tab.print_to_pdf()               # 頁面轉 PDF

# 網路攔截
await tab.intercept(pattern, handler)        # 請求攔截

# 等待條件
await tab.wait_for(condition, timeout=10)    # 等待條件成立

# 請求/回應等待
req = await tab.expect_request(predicate)    # 等待特定請求
resp = await tab.expect_response(predicate)  # 等待特定回應
dl = await tab.expect_download(timeout=10)   # 等待下載

# Storage
data = await tab.get_local_storage()         # 讀取 localStorage
await tab.set_local_storage(data)            # 設定 localStorage

# User-Agent
await tab.set_user_agent("custom_ua")        # 動態設定 UA

# 視窗（新增）
await tab.maximize()                         # 最大化
await tab.minimize()                         # 最小化
await tab.fullscreen()                       # 全螢幕
```

---

## 5. Browser API 對照

### 100% 相容

```python
driver.tabs                                  # 所有分頁（property）
driver.main_tab                              # 主分頁
await driver.get(url)                        # 導航（便利方法）
await driver.stop()                          # 關閉瀏覽器
await driver.grant_all_permissions()         # 授予所有權限
driver.tile_windows()                        # 排列視窗
driver.config.port                           # CDP 連線埠
```

### zendriver 新增/改進

```python
# Cookie 管理（zendriver CookieJar）
driver.cookies                               # CookieJar 物件
await driver.cookies.get_all()               # 取得所有 Cookie
await driver.cookies.set_all(cookies)        # 批量設定
await driver.cookies.clear()                 # 清除
await driver.cookies.save('path.json')       # 儲存到檔案
await driver.cookies.load('path.json')       # 從檔案載入

# 類別方法（新增）
driver = await Browser.create(config=conf)   # 替代 uc.start()
```

---

## 6. CDP 模組對照

### 100% 相容的 CDP 操作

```python
from zendriver import cdp

# DOM（全部相容）
await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
await tab.send(cdp.dom.perform_search(query='btn', include_user_agent_shadow_dom=True))
await tab.send(cdp.dom.get_search_results(search_id=sid, from_index=0, to_index=count))
await tab.send(cdp.dom.discard_search_results(search_id=sid))
await tab.send(cdp.dom.get_box_model(node_id=nid))
await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=nid))
await tab.send(cdp.dom.describe_node(node_id=nid))
await tab.send(cdp.dom.resolve_node(node_id=nid))
await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(backend_node_ids=[bnid]))
await tab.send(cdp.dom.get_outer_html(node_id=nid))
await tab.send(cdp.dom.focus(node_id=nid))

# DOM Snapshot（全部相容）
await tab.send(cdp.dom_snapshot.capture_snapshot(computed_styles=[]))

# Input（全部相容）
await tab.send(cdp.input_.dispatch_mouse_event(type_='mousePressed', x=x, y=y, button=cdp.input_.MouseButton('left'), click_count=1))
await tab.send(cdp.input_.dispatch_key_event(type_='keyDown', code='Enter', key='Enter'))

# Page（全部相容）
tab.add_handler(cdp.page.JavascriptDialogOpening, handler)
await tab.send(cdp.page.handle_java_script_dialog(accept=True))
await tab.send(cdp.page.capture_screenshot(format_='png'))

# Target（全部相容）
await tab.send(cdp.target.get_targets())

# Runtime（全部相容）
await tab.send(cdp.runtime.evaluate(expression='...'))

# Network -- Cookie 操作（全部相容）
await tab.send(cdp.network.enable())
await tab.send(cdp.network.delete_cookies(name='name', domain='domain'))
await tab.send(cdp.network.set_cookie(name='n', value='v', domain='d', path='/', secure=True, http_only=True, same_site='Lax'))
```

### CDP 改名（Breaking Change #2）

```python
# nodriver（舊）
await tab.send(cdp.network.set_blocked_ur_ls(urls=BLOCKED_URLS))

# zendriver（新）
await tab.send(cdp.network.set_blocked_urls(urls=BLOCKED_URLS))
```

---

## 7. 遷移 Breaking Changes 完整清單

| # | 變更 | 搜尋 | 替換 | 影響檔案 |
|---|------|------|------|---------|
| 1 | 事件迴圈 | `uc.loop().run_until_complete(` | `asyncio.run(` | nodriver_tixcraft.py, fetch_tixcraft_captcha.py |
| 2 | CDP 改名 | `set_blocked_ur_ls` | `set_blocked_urls` | nodriver_tixcraft.py |
| 3 | Handler 改名 | `remove_handler(` | `remove_handlers(` | 需全域搜尋確認 |
| 4 | evaluate 預設值 | 不需搜尋替換 | 煙霧測試驗證 | 全部（267 處） |
| 5 | Import | `from nodriver` / `import nodriver` | `from zendriver` / `import zendriver` | 13 個檔案 |
| 6 | PyInstaller | `'nodriver'` | `'zendriver'` | nodriver_tixcraft.spec |
| 7 | sandbox bug | `no_sandbox=no_sandbox` | `sandbox=not no_sandbox` | nodriver_common.py |

---

## 8. 常用操作速查

```python
import zendriver as uc
from zendriver import cdp
import asyncio

async def main():
    # 啟動
    conf = Config(headless=False, lang="zh-TW")
    driver = await uc.start(conf)
    tab = await driver.get('https://example.com')

    # 基本操作
    await tab.evaluate('document.title')
    el = await tab.query_selector('#btn')
    await el.click()

    # CDP 進階
    doc = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
    box = await tab.send(cdp.dom.get_box_model(node_id=nid))

    # 關閉
    await driver.stop()

asyncio.run(main())
```

---

## 9. evaluate() 回傳值行為差異詳解

這是遷移最需要注意的差異。

### nodriver 行為（return_by_value=False）

```python
result = await tab.evaluate('document.title')
# result 是 RemoteObject: {'type': 'string', 'value': 'Page Title'}
# 需要 parse_nodriver_result(result) 或 convert_remote_object(result) 轉換
```

### zendriver 行為（return_by_value=True）

```python
result = await tab.evaluate('document.title')
# result 直接是: 'Page Title'
# 不需要額外轉換
```

### 影響分析

專案中的 `convert_remote_object()` 和 `parse_nodriver_result()` 函式在收到實際值時會直接回傳原值，所以**不會壞**。但這些函式在 zendriver 下變成多餘的 pass-through。

遷移後可考慮（非必要）：
- 移除 `convert_remote_object()` 的呼叫
- 簡化 `parse_nodriver_result()` 的使用

---

## 10. 參考資源

- [zendriver 官方文件](https://zendriver.dev/)
- [zendriver GitHub](https://github.com/cdpdriver/zendriver)
- [zendriver Release Notes](https://zendriver.dev/release-notes/)
- [zendriver CDP 教學](https://zendriver.dev/tutorials/cdp/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
