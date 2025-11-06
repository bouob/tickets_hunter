# 平台轉接器介面契約

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：定義所有平台轉接器必須實作的標準介面和行為契約。

---

## 概述

本文件定義平台轉接器的標準介面，確保所有平台（TixCraft、KKTIX、iBon 等）遵循一致的函式簽名、命名慣例和行為模式。遵循此契約可確保新平台整合時不會破壞現有系統。

**目標**：
- 標準化平台函式命名
- 定義一致的參數和返回值
- 明確錯誤處理期望
- 促進平台間程式碼可讀性

**非目標**：
- 強制實作細節（每個平台可自由處理 DOM 差異）
- 要求抽象基底類別（保持輕量級函式模式）

---

## NoDriver CDP 標準介面（2025-10-26 新增）

**背景**：售票平台反機器人系統已能偵測 JavaScript 執行。NoDriver 版本必須全面使用 CDP 原生方法，避免所有可被偵測的操作。

**強制規則**（所有 NoDriver 平台實作）：
- ❌ **禁止**：`tab.evaluate()`、`page.evaluate()`、JavaScript 注入
- ❌ **禁止**：`tab.find()`（基於 JavaScript）
- ✅ **必須**：使用 CDP `perform_search()` 進行 DOM 查詢
- ✅ **必須**：使用 CDP `dispatch_mouse_event()` 進行點擊
- ✅ **必須**：使用 CDP `scroll_into_view_if_needed()` 進行滾動

### DOM 查詢標準

#### `search_elements_pierce(tab, selector: str, timeout: float = 5.0) -> List[int]`

使用 CDP `perform_search()` 查找元素（穿透 Shadow DOM）。

**參數**:
- `tab`: NoDriver Tab 物件
- `selector`: CSS selector 字串
- `timeout`: 最大等待時間（秒），預設 5.0

**返回值**:
- `List[int]`: 節點 ID 列表（CDP node_id）

**實作要求**:
```python
# 必須使用 include_user_agent_shadow_dom=True
search_id, count = await tab.send(cdp.dom.perform_search(
    query=selector,
    include_user_agent_shadow_dom=True
))

# 獲取結果
node_ids = await tab.send(cdp.dom.get_search_results(
    search_id=search_id,
    from_index=0,
    to_index=count
))

# 必須清理資源
await tab.send(cdp.dom.discard_search_results(search_id=search_id))
```

**效能要求**:
- 必須在 `timeout` 秒內完成或拋出異常
- 首次成功率 >= 90%

**禁止事項**:
- ❌ 不得使用 `tab.evaluate()` 執行 JavaScript
- ❌ 不得使用 `tab.find()`（基於 JavaScript）

---

### 元素互動標準

#### `click_element_native(tab, node_id: int) -> bool`

使用 CDP 原生事件點擊元素。

**參數**:
- `tab`: NoDriver Tab 物件
- `node_id`: CDP 節點 ID

**返回值**:
- `True`: 點擊成功
- `False`: 點擊失敗

**實作要求**:
```python
# 1. 滾動到可視範圍
await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))

# 2. 獲取元素位置
box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
x = (box_model.content[0] + box_model.content[2]) / 2
y = (box_model.content[1] + box_model.content[5]) / 2

# 3. 執行點擊（mousePressed + mouseReleased）
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mousePressed', x=x, y=y, button='left', click_count=1
))
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mouseReleased', x=x, y=y, button='left', click_count=1
))
```

**禁止事項**:
- ❌ 不得回退到 JavaScript `element.click()`
- ❌ 不得使用 `tab.evaluate('element.click()')`

---

### 智能等待標準

#### `wait_for_element_pierce(tab, selector: str, max_wait: float = 5.0, check_interval: float = 0.3) -> Tuple[bool, float]`

輪詢檢查元素是否出現（適應動態渲染）。

**參數**:
- `tab`: NoDriver Tab 物件
- `selector`: CSS selector 字串
- `max_wait`: 最大額外等待時間（秒）
- `check_interval`: 輪詢間隔（秒）

**返回值**:
- `(found: bool, elapsed_time: float)`: (是否找到, 總耗時)

**實作要求**:
```python
# 初始隨機等待（避免固定模式被偵測）
initial_wait = random.uniform(1.2, 1.8)
await tab.sleep(initial_wait)

# 輪詢檢查
for attempt in range(int(max_wait / check_interval)):
    search_id, count = await tab.send(cdp.dom.perform_search(
        query=selector,
        include_user_agent_shadow_dom=True
    ))
    await tab.send(cdp.dom.discard_search_results(search_id=search_id))

    if count > 0:
        return (True, initial_wait + attempt * check_interval)

    await tab.sleep(check_interval)

return (False, initial_wait + max_wait)
```

**適用場景**:
- Shadow DOM 元素檢測（如 iBon Angular SPA）
- 動態載入內容（如 KKTIX 排隊頁面）
- 延遲渲染的按鈕（如 TicketPlus 展開面板）

---

### 資源管理標準

**強制要求**：所有 `perform_search()` 調用後必須清理資源。

**正確範例**:
```python
search_id, count = await tab.send(cdp.dom.perform_search(...))

try:
    # 處理搜尋結果
    node_ids = await tab.send(cdp.dom.get_search_results(...))
    # ... 處理 node_ids
finally:
    # 防禦性清理
    try:
        await tab.send(cdp.dom.discard_search_results(search_id=search_id))
    except:
        pass  # 清理失敗不影響主流程
```

**為何重要**:
- CDP 維護搜尋會話狀態，不清理會累積記憶體
- 清理後不能再對該 `search_id` 調用 `get_search_results()`

---

### 效能指標

**NoDriver 版本必須達到的標準**（基於 iBon 實測數據）：

| 指標 | 目標值 | 測量方法 |
|------|--------|---------|
| DOM 查詢速度 | 2-5秒 | 從 `perform_search()` 開始到結果返回 |
| 首次成功率 | >= 95% | 第一次查詢即找到目標元素的比例 |
| 記憶體消耗 | < 5MB | 單次 DOM 查詢的記憶體峰值 |
| 智能等待時間 | 1.2-6.2秒 | 初始等待 + 輪詢時間 |

**驗證方法**:
```python
import time
start = time.time()
search_id, count = await tab.send(cdp.dom.perform_search(...))
elapsed = time.time() - start
print(f"[PERF] DOM query completed in {elapsed:.1f}s, found {count} elements")
```

---

### 檢查清單（Code Review 必檢）

**每個 NoDriver 平台函式提交前必須檢查**：

- [ ] 不存在 `tab.evaluate()` 或 `executeScript()` 調用
- [ ] 不存在 `tab.find()` 調用（改用 `perform_search()`）
- [ ] 所有 DOM 查詢使用 `perform_search(query, include_user_agent_shadow_dom=True)`
- [ ] 所有點擊使用 `dispatch_mouse_event()`（兩次調用：mousePressed + mouseReleased）
- [ ] 所有滾動使用 `scroll_into_view_if_needed()`
- [ ] 所有 `perform_search()` 後必須調用 `discard_search_results()`
- [ ] 使用防禦性 try-except 處理資源清理
- [ ] 智能等待使用隨機初始延遲（1.2-1.8秒）
- [ ] 輪詢間隔設定為 0.3 秒
- [ ] 記錄效能日誌（verbose 模式下）

---

## 命名慣例

### 函式命名模式

**NoDriver 平台函式**：
```
nodriver_{platform}_{stage}
```

**Chrome Driver 平台函式**：
```
chrome_{platform}_{stage}
```

**範例**：
```python
# NoDriver TixCraft
async def nodriver_tixcraft_main(tab, url, config_dict)
async def nodriver_tixcraft_date_auto_select(tab, url, config_dict)
async def nodriver_tixcraft_area_auto_select(tab, url, config_dict)

# Chrome Driver KKTIX
def chrome_kktix_main(driver, url, config_dict)
def chrome_kktix_date_auto_select(driver, url, config_dict)
def chrome_kktix_area_auto_select(driver, url, config_dict)
```

### 平台代號標準

| 平台 | 代號 | 範例函式 |
|------|------|---------|
| TixCraft | `tixcraft` | `nodriver_tixcraft_main` |
| KKTIX | `kktix` | `nodriver_kktix_main` |
| TicketPlus | `ticketplus` | `nodriver_ticketplus_main` |
| ibon | `ibon` | `nodriver_ibon_main` |
| KHAM | `kham` | `nodriver_kham_main` |
| Cityline | `cityline` | `nodriver_cityline_main` |
| TicketMaster | `ticketmaster` | `nodriver_ticketmaster_main` |
| Urbtix | `urbtix` | `nodriver_urbtix_main` |
| HKTicketing | `hkticketing` | `nodriver_hkticketing_main` |
| FamiTicket | `famiticket` | `nodriver_famiticket_main` |

---

## 必需函式（12 階段）

每個平台必須實作以下函式以支援完整的購票流程：

### 0. 環境初始化（呼叫者責任）

**用途**：初始化 WebDriver、載入配置、驗證設定檔結構。

**責任範圍**：主程式入口點（`nodriver_tixcraft.py`、`chrome_tixcraft.py` 等），**不屬於平台轉接器職責**。

**對應功能需求**：
- **FR-001**：支援多種 WebDriver 類型（NoDriver、Chrome Driver、Selenium）
- **FR-002**：使用配置初始化瀏覽器（無頭模式、視窗大小、代理設定）
- **FR-003**：載入擴充功能（廣告攔截器、隱私工具）
- **FR-004**：驗證 `settings.json` 結構，提供清楚的錯誤訊息

**實作位置**：
- NoDriver：`nodriver_tixcraft.py` 主程式區塊（行 1-100）
- Chrome Driver：`chrome_tixcraft.py` 主程式區塊

**行為契約**：
1. 從 `settings.json` 讀取配置
2. 驗證必需的配置鍵存在
3. 根據 `webdriver_type` 初始化對應的 WebDriver
4. 設定瀏覽器選項（headless、window-size、user-agent）
5. 載入配置的擴充功能（如有）
6. 將瀏覽器物件和配置傳遞給平台 `_main()` 函式

**範例實作**（NoDriver）：
```python
import nodriver
import json

# 讀取配置
with open("settings.json", "r", encoding="utf-8") as f:
    config_dict = json.load(f)

# 驗證配置
if "homepage" not in config_dict:
    print("[ERROR] Missing 'homepage' in settings.json")
    sys.exit(1)

# 初始化 NoDriver
browser = await nodriver.start(
    headless=config_dict["advanced"].get("headless", False),
    user_data_dir=None  # 每次啟動使用全新環境
)

tab = await browser.get(config_dict["homepage"])

# 呼叫平台主函式
result = await nodriver_tixcraft_main(tab, config_dict["homepage"], config_dict)
```

**注意事項**：
- 環境初始化**只執行一次**，在購票流程開始前完成
- 平台轉接器函式（`_main()`）接收已初始化的瀏覽器物件
- 配置驗證失敗應立即終止程式，不進入購票流程

---

### 1. 主協調器（Main Orchestrator）

**用途**：協調整個購票流程，按順序呼叫 12 個階段函式。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_main(
    tab: nodriver.Tab,
    url: str,
    config_dict: dict
) -> bool
```

**簽名**（Chrome Driver）：
```python
def chrome_{platform}_main(
    driver: uc.Chrome,
    url: str,
    config_dict: dict
) -> bool
```

**參數**：
- `tab` / `driver`：瀏覽器控制物件
- `url`：活動頁面 URL
- `config_dict`：完整配置字典

**返回值**：
- `True`：購票流程成功完成（訂單已送出）
- `False`：購票流程失敗（無法恢復）

**責任**：
1. 驗證 URL 屬於此平台
2. 依序呼叫階段函式
3. 處理階段間的錯誤傳播
4. 記錄整體流程狀態

**範例實作**：
```python
async def nodriver_tixcraft_main(tab, url, config_dict):
    """TixCraft 購票主流程"""
    try:
        # 階段 2：身份認證
        await nodriver_tixcraft_login(tab, config_dict)

        # 階段 3：頁面監控與重載
        await nodriver_tixcraft_auto_reload(tab, url, config_dict)

        # 階段 4：日期選擇
        await nodriver_tixcraft_date_auto_select(tab, url, config_dict)

        # 階段 5：區域選擇
        await nodriver_tixcraft_area_auto_select(tab, url, config_dict)

        # 階段 6-10：其他階段...
        await nodriver_tixcraft_ticket_main(tab, config_dict)

        return True
    except Exception as exc:
        if config_dict["advanced"]["verbose"]:
            print(f"[ERROR] TixCraft 購票失敗：{exc}")
        return False
```

---

### 2. 身份認證（Authentication）

**用途**：注入 session cookies 或執行登入流程。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_login(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**參數**：
- `tab` / `driver`：瀏覽器控制物件
- `config_dict`：包含認證憑證（cookies、帳密）

**返回值**：
- `True`：認證成功
- `False`：認證失敗（可能是憑證無效）

**行為契約**：
1. 從 `config_dict["advanced"]` 讀取憑證
2. 嘗試認證（Cookie 注入或表單登入）
3. 驗證認證成功（檢查登入狀態元素）
4. 失敗時記錄錯誤但不拋出異常（允許繼續）

**範例實作**（Cookie 注入）：
```python
async def nodriver_tixcraft_login(tab, config_dict):
    """TixCraft Cookie 注入"""
    tixcraft_sid = config_dict["advanced"].get("tixcraft_sid", "")

    if not tixcraft_sid:
        if config_dict["advanced"]["verbose"]:
            print("[AUTH] 未提供 tixcraft_sid，跳過認證")
        return False

    # 注入 Cookie
    await tab.send(cdp.network.set_cookie(
        name="tixcraft_sid",
        value=tixcraft_sid,
        domain=".tixcraft.com",
        path="/",
        secure=True,
        http_only=True
    ))

    if config_dict["advanced"]["verbose"]:
        print("[AUTH] Cookie 注入成功")

    return True
```

**範例實作**（表單登入）：
```python
async def nodriver_kktix_login(tab, config_dict):
    """KKTIX 表單登入"""
    account = config_dict["advanced"].get("kktix_account", "")
    password = config_dict["advanced"].get("kktix_password", "")

    if not account or not password:
        if config_dict["advanced"]["verbose"]:
            print("[AUTH] 未提供 KKTIX 帳密，跳過認證")
        return False

    # 導航到登入頁面
    await tab.get("https://kktix.com/users/sign_in")
    await tab.sleep(2)

    # 填寫表單
    result = await tab.evaluate(f'''
        (() => {{
            const emailInput = document.querySelector("input#user_email");
            const passwordInput = document.querySelector("input#user_password");
            const submitBtn = document.querySelector("button[type='submit']");

            if (!emailInput || !passwordInput || !submitBtn) {{
                return {{success: false, reason: "elements_not_found"}};
            }}

            emailInput.value = "{account}";
            passwordInput.value = "{password}";
            submitBtn.click();

            return {{success: true}};
        }})()
    ''')

    if result.get('success'):
        await tab.sleep(3)  # 等待登入完成
        return True
    else:
        return False
```

---

### 3. 頁面監控與重載（Auto Reload）

**用途**：在開賣前持續重載頁面，直到購票按鈕出現。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_auto_reload(
    tab: nodriver.Tab,
    url: str,
    config_dict: dict
) -> bool
```

**返回值**：
- `True`：購票按鈕已出現，可繼續流程
- `False`：超過重載次數限制或發生錯誤

**行為契約**：
1. 檢查購票按鈕是否可用
2. 如果不可用，等待 `auto_reload_page_interval` 秒後重載
3. 實作過熱保護（`auto_reload_overheat_count` 和 `auto_reload_overheat_cd`）
4. 支援暫停機制檢查（NoDriver）

**範例實作**：
```python
async def nodriver_tixcraft_auto_reload(tab, url, config_dict):
    """TixCraft 自動重載頁面"""
    reload_count = 0
    interval = config_dict["advanced"]["auto_reload_page_interval"]
    overheat_count = config_dict["advanced"]["auto_reload_overheat_count"]
    overheat_cd = config_dict["advanced"]["auto_reload_overheat_cd"]

    while True:
        # 檢查按鈕
        result = await tab.evaluate('''
            (() => {
                const btn = document.querySelector("a[onclick*='performance_id']");
                return {success: btn !== null, sold_out: btn && btn.classList.contains('sold_out')};
            })()
        ''')

        if result.get('success') and not result.get('sold_out'):
            if config_dict["advanced"]["verbose"]:
                print("[RELOAD] 購票按鈕已出現")
            return True

        # 過熱保護
        if reload_count >= overheat_count:
            if config_dict["advanced"]["verbose"]:
                print(f"[RELOAD] 過熱保護：冷卻 {overheat_cd} 秒")
            await asyncio_sleep_with_pause_check(overheat_cd, config_dict)
            reload_count = 0

        # 重載
        reload_count += 1
        if config_dict["advanced"]["verbose"]:
            print(f"[RELOAD] 重載頁面... ({reload_count})")

        await asyncio_sleep_with_pause_check(interval, config_dict)
        await tab.reload()
```

---

### 4. 日期選擇（Date Selection）

**用途**：根據關鍵字或模式選擇場次日期。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_date_auto_select(
    tab: nodriver.Tab,
    url: str,
    config_dict: dict
) -> bool
```

**返回值**：
- `True`：日期選擇成功（已點擊並導航到下一頁）
- `False`：無可用日期或選擇失敗

**行為契約**：
1. **前置檢查（總開關）**：
   - 檢查 `date_auto_select.enable` 設定值
   - 若為 `false`：完全停用自動選擇，記錄訊息並返回（讓使用者手動選擇）
   - 若為 `true`：繼續執行以下三層回退邏輯
2. 實作三層回退策略：
   - **第 1 層（關鍵字匹配）**：使用 `date_keyword` 匹配日期，成功則選擇並完成
   - **第 2 層（自動選擇模式）**：若第 1 層失敗且有設定 `mode`，使用模式選擇
   - **第 3 層（停止並等待手動）**：若前兩層都失敗或未設定 `mode`，停止自動選擇並記錄訊息
3. 過濾已售罄日期
4. 支援多個關鍵字（逗號分隔）
5. 記錄選擇結果

**範例實作**：
```python
async def nodriver_tixcraft_date_auto_select(tab, url, config_dict):
    """TixCraft 日期選擇"""
    date_config = config_dict.get("date_auto_select", {})

    if not date_config.get("enable", True):
        if config_dict["advanced"]["verbose"]:
            print("[DATE] 日期選擇已停用")
        return True

    # 取得可用日期
    result = await tab.evaluate('''
        (() => {
            const dates = Array.from(document.querySelectorAll("table.table a[onclick*='performance_id']"))
                .filter(a => !a.classList.contains('sold_out'))
                .map(a => ({
                    text: a.textContent.trim(),
                    element_id: a.getAttribute('onclick').match(/performance_id=(\\d+)/)[1]
                }));
            return {success: true, dates: dates};
        })()
    ''')

    available_dates = result.get('dates', [])
    if not available_dates:
        if config_dict["advanced"]["verbose"]:
            print("[DATE] No available dates found")
        return False

    # Layer 1: Keyword matching with AND/OR logic
    # Format: "AA BB","CC","DD" -> (AA AND BB) OR (CC) OR (DD)
    # Example: date_keyword = '"12/13","Taipei Saturday","Kaohsiung"'
    #   - Matches if date contains "12/13"
    #   - OR if date contains both "Taipei" AND "Saturday"
    #   - OR if date contains "Kaohsiung"
    date_keyword = date_config.get("date_keyword", "")

    selected_date = None
    if date_keyword:
        try:
            import json
            # Parse as JSON array (auto-removes quotes)
            keyword_array = json.loads("[" + date_keyword + "]")

            if config_dict["advanced"]["verbose"]:
                print(f"[DATE] Applying keyword filter: {keyword_array}")

            # Check each date against keyword groups (OR logic between groups)
            for date in available_dates:
                date_text = date['text'].lower()

                # Check if any keyword group matches (OR logic)
                for keyword_item in keyword_array:
                    # Split by space for AND logic (e.g., "AA BB" means AA AND BB)
                    sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]

                    # Check if all sub-keywords match (AND logic within group)
                    is_match = all(sub_kw.lower() in date_text for sub_kw in sub_keywords)

                    if is_match:
                        selected_date = date
                        if config_dict["advanced"]["verbose"]:
                            print(f"[DATE] Keyword '{keyword_item}' matched -> {date['text']}")
                        break

                if selected_date:
                    break
        except json.JSONDecodeError as e:
            if config_dict["advanced"]["verbose"]:
                print(f"[DATE] Keyword parse error: {e}")

    # Layer 2: Mode-based selection (fallback if no keyword match)
    if not selected_date:
        mode = date_config.get("mode", "")
        if mode:
            if mode == "from top to bottom":
                selected_date = available_dates[0]
            elif mode == "from bottom to top":
                selected_date = available_dates[-1]
            elif mode == "center":
                selected_date = available_dates[len(available_dates) // 2]
            elif mode == "random":
                import random
                selected_date = random.choice(available_dates)

            if config_dict["advanced"]["verbose"]:
                print(f"[DATE] No keyword match, using mode '{mode}' -> {selected_date['text']}")
        else:
            # Layer 3: Stop and wait for manual intervention
            if config_dict["advanced"]["verbose"]:
                print("[DATE] No keyword match and no mode set, stopping for manual selection")
            return False

    # 點擊日期
    click_result = await tab.evaluate(f'''
        (() => {{
            const link = document.querySelector("a[onclick*='performance_id={selected_date['element_id']}']");
            if (!link) return {{success: false}};
            link.click();
            return {{success: true}};
        }})()
    ''')

    if click_result.get('success'):
        await tab.sleep(2)
        return True
    else:
        return False
```

---

### 5. 區域/座位選擇（Area/Seat Selection）

**用途**：根據關鍵字或模式選擇票區或座位。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_area_auto_select(
    tab: nodriver.Tab,
    url: str,
    config_dict: dict
) -> bool
```

**返回值**：
- `True`：區域選擇成功
- `False`：無可用區域或選擇失敗

**行為契約**：
1. **前置檢查與三層回退策略**（同日期選擇）：
   - 前置檢查：`area_auto_select.enable`
   - 第 1 層：關鍵字匹配（`area_keyword`）
   - 第 2 層：模式選擇（`mode`）
   - 第 3 層：停止並等待手動介入
2. 處理兩種介面類型：
   - **下拉選單**（`<select>` 元素）
   - **座位圖**（互動式 SVG/Canvas）
3. 支援 ibon 特殊需求（相鄰座位）

**範例實作**（下拉選單）：
```python
async def nodriver_tixcraft_area_auto_select(tab, url, config_dict):
    """TixCraft 區域選擇（下拉選單）"""
    area_config = config_dict.get("area_auto_select", {})

    if not area_config.get("enable", True):
        return True

    # 取得可用區域
    result = await tab.evaluate('''
        (() => {
            const select = document.querySelector("select#ticketPriceArea");
            if (!select) return {success: false};

            const options = Array.from(select.options)
                .filter(opt => opt.value !== "" && !opt.disabled)
                .map(opt => ({
                    text: opt.textContent.trim(),
                    value: opt.value
                }));
            return {success: true, areas: options};
        })()
    ''')

    available_areas = result.get('areas', [])
    if not available_areas:
        return False

    # 關鍵字匹配
    area_keyword = area_config.get("area_keyword", "")
    keywords = [k.strip() for k in area_keyword.split(',') if k.strip()]

    selected_area = None
    for area in available_areas:
        for keyword in keywords:
            if keyword in area['text']:
                selected_area = area
                break
        if selected_area:
            break

    # 模式選擇（如果需要）
    if not selected_area:
        mode = area_config.get("mode", "from top to bottom")
        if mode == "from top to bottom":
            selected_area = available_areas[0]
        # ... 其他模式

    # 選擇區域
    select_result = await tab.evaluate(f'''
        (() => {{
            const select = document.querySelector("select#ticketPriceArea");
            if (!select) return {{success: false}};
            select.value = "{selected_area['value']}";
            select.dispatchEvent(new Event('change', {{bubbles: true}}));
            return {{success: true}};
        }})()
    ''')

    return select_result.get('success', False)
```

---

### 6. 票數設定（Ticket Quantity）

**用途**：設定購票數量。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_ticket_quantity_set(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**行為契約**：
1. 從 `config_dict["ticket_number"]` 讀取數量
2. 選擇對應的下拉選單選項
3. 驗證選擇成功

**範例實作**：
```python
async def nodriver_tixcraft_ticket_quantity_set(tab, config_dict):
    """TixCraft 票數設定"""
    ticket_number = config_dict.get("ticket_number", 1)

    result = await tab.evaluate(f'''
        (() => {{
            const select = document.querySelector("select#ticketPriceQuantity");
            if (!select) return {{success: false}};

            select.value = "{ticket_number}";
            select.dispatchEvent(new Event('change', {{bubbles: true}}));

            return {{success: true}};
        }})()
    ''')

    return result.get('success', False)
```

---

### 7. 驗證碼處理（CAPTCHA）

**用途**：識別並填寫驗證碼。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_captcha_auto_fill(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**返回值**：
- `True`：驗證碼已填寫（OCR 或手動）
- `False`：驗證碼處理失敗

**行為契約**：
1. 擷取驗證碼圖片
2. 使用 ddddocr 辨識
3. 填入輸入框
4. 支援重試（`ocr_captcha.retry`）
5. 支援 `force_submit`（OCR 失敗時仍送出）

**範例實作**：
```python
async def nodriver_tixcraft_captcha_auto_fill(tab, config_dict):
    """TixCraft 驗證碼處理"""
    ocr_config = config_dict.get("ocr_captcha", {})

    if not ocr_config.get("enable", True):
        return True

    max_retry = ocr_config.get("retry", 3)
    use_beta = ocr_config.get("beta", False)
    force_submit = ocr_config.get("force_submit", False)

    # 初始化 OCR
    import ddddocr
    ocr = ddddocr.DdddOcr(beta=use_beta)

    for retry_count in range(max_retry):
        # 擷取驗證碼圖片
        captcha_base64 = await tab.evaluate('''
            (() => {
                const img = document.querySelector("img#captchaImg");
                if (!img) return null;
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/png').split(',')[1];
            })()
        ''')

        if not captcha_base64:
            return False

        # 解碼並辨識
        import base64
        captcha_bytes = base64.b64decode(captcha_base64)
        captcha_text = ocr.classification(captcha_bytes)

        # 驗證結果
        if len(captcha_text) >= 4 and captcha_text.isalnum():
            # 填入驗證碼
            fill_result = await tab.evaluate(f'''
                (() => {{
                    const input = document.querySelector("input#captcha");
                    if (!input) return {{success: false}};
                    input.value = "{captcha_text}";
                    return {{success: true}};
                }})()
            ''')

            if fill_result.get('success'):
                if config_dict["advanced"]["verbose"]:
                    print(f"[CAPTCHA] OCR 辨識成功：{captcha_text}")
                return True

        # 重試
        if config_dict["advanced"]["verbose"]:
            print(f"[CAPTCHA] OCR 辨識失敗，重試... ({retry_count + 1}/{max_retry})")
        await tab.sleep(1)

    # 所有重試失敗
    if force_submit:
        if config_dict["advanced"]["verbose"]:
            print("[CAPTCHA] OCR 失敗，force_submit=True，繼續送出")
        return True
    else:
        return False
```

---

### 8. 表單填寫（Form Fill）

**用途**：填寫購票人資訊表單。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_form_fill(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**行為契約**：
1. 從 `config_dict["ticket_form_data"]` 讀取資訊
2. 填寫姓名、Email、電話、地址等欄位
3. 處理平台特定欄位（如身分證號）

**範例實作**：
```python
async def nodriver_tixcraft_form_fill(tab, config_dict):
    """TixCraft 表單填寫"""
    form_data = config_dict.get("ticket_form_data", {})

    result = await tab.evaluate(f'''
        (() => {{
            const nameInput = document.querySelector("input#name");
            const emailInput = document.querySelector("input#email");
            const phoneInput = document.querySelector("input#phone");

            if (nameInput) nameInput.value = "{form_data.get('name', '')}";
            if (emailInput) emailInput.value = "{form_data.get('email', '')}";
            if (phoneInput) phoneInput.value = "{form_data.get('phone', '')}";

            return {{success: true}};
        }})()
    ''')

    return result.get('success', False)
```

---

### 9. 同意條款（Terms Agreement）

**用途**：勾選同意條款核取方塊。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_agree_terms(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**行為契約**：
1. 查找同意條款核取方塊
2. 勾選核取方塊
3. 觸發 `change` 事件（某些平台需要）

**範例實作**：
```python
async def nodriver_tixcraft_agree_terms(tab, config_dict):
    """TixCraft 同意條款"""
    result = await tab.evaluate('''
        (() => {
            const checkbox = document.querySelector("input#agreeCheckbox");
            if (!checkbox) return {success: false};
            checkbox.checked = true;
            checkbox.dispatchEvent(new Event('change', {bubbles: true}));
            return {success: true};
        })()
    ''')

    return result.get('success', False)
```

---

### 10. 訂單送出（Submit Order）

**用途**：點擊送出按鈕，提交訂單。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_submit_order(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**行為契約**：
1. 查找送出按鈕
2. 點擊按鈕
3. 等待頁面跳轉
4. 驗證送出成功（檢查成功訊息或付款頁面）

**範例實作**：
```python
async def nodriver_tixcraft_submit_order(tab, config_dict):
    """TixCraft 訂單送出"""
    # 點擊送出按鈕
    result = await tab.evaluate('''
        (() => {
            const btn = document.querySelector("button#submitButton");
            if (!btn) return {success: false, reason: "button_not_found"};
            btn.click();
            return {success: true};
        })()
    ''')

    if not result.get('success'):
        return False

    # 等待跳轉
    await tab.sleep(3)

    # 驗證成功
    success_check = await tab.evaluate('''
        (() => {
            const successMsg = document.querySelector(".success-message");
            const paymentPage = document.querySelector(".payment-info");
            return {success: successMsg !== null || paymentPage !== null};
        })()
    ''')

    if success_check.get('success'):
        if config_dict["advanced"]["verbose"]:
            print("[SUCCESS] 訂單已送出")
        return True
    else:
        return False
```

---

### 11. 排隊與付款（Queue & Payment）

**用途**：處理排隊頁面，導航到付款頁面（不執行付款）。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_handle_queue(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**行為契約**：
1. 檢測排隊頁面
2. 等待排隊完成
3. 導航到付款頁面
4. **不執行自動付款**（範圍外）

**範例實作**：
```python
async def nodriver_tixcraft_handle_queue(tab, config_dict):
    """TixCraft 排隊處理"""
    max_wait = 300  # 最多等待 5 分鐘
    wait_count = 0

    while wait_count < max_wait:
        # 檢查排隊狀態
        result = await tab.evaluate('''
            (() => {
                const queueMsg = document.querySelector(".queue-message");
                const paymentPage = document.querySelector(".payment-info");

                if (paymentPage) return {status: "payment", in_queue: false};
                if (queueMsg) return {status: "queue", in_queue: true};
                return {status: "unknown", in_queue: false};
            })()
        ''')

        if result.get('status') == "payment":
            if config_dict["advanced"]["verbose"]:
                print("[QUEUE] 排隊完成，已進入付款頁面")
            return True
        elif result.get('status') == "queue":
            if config_dict["advanced"]["verbose"] and wait_count % 10 == 0:
                print(f"[QUEUE] 排隊中... ({wait_count}s)")
            await tab.sleep(1)
            wait_count += 1
        else:
            # 無排隊頁面，直接成功
            return True

    # 排隊超時
    if config_dict["advanced"]["verbose"]:
        print("[QUEUE] 排隊超時")
    return False
```

---

### 12. 錯誤處理（Error Handling）

**用途**：統一處理錯誤和重試邏輯。

**簽名**（NoDriver）：
```python
async def nodriver_{platform}_handle_error(
    tab: nodriver.Tab,
    error: Exception,
    stage: str,
    config_dict: dict
) -> bool
```

**參數**：
- `error`：捕獲的異常
- `stage`：發生錯誤的階段名稱

**返回值**：
- `True`：錯誤已處理，可重試
- `False`：無法恢復，終止流程

**行為契約**：
1. 記錄錯誤資訊
2. 判斷錯誤類型（可恢復 vs. 致命）
3. 實作指數退避重試
4. 超過重試次數時返回 False

---

## 可選函式

以下函式為可選實作，根據平台特性決定：

### Shadow DOM 處理（僅 ibon）

```python
async def nodriver_ibon_pierce_shadow_dom(
    tab: nodriver.Tab,
    selector: str
) -> bool
```

**用途**：穿透 Shadow DOM 查找元素（ibon 特殊需求）。

### 座位圖互動（僅有座位圖的平台）

```python
async def nodriver_{platform}_seat_map_select(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool
```

**用途**：在互動式座位圖上選擇座位。

---

## 錯誤處理契約

### 異常型別

所有平台函式應遵循以下異常處理模式：

**自定義異常**（可選但推薦）：
```python
class PlatformError(Exception):
    """平台特定錯誤基底類別"""
    pass

class ElementNotFoundError(PlatformError):
    """元素未找到"""
    pass

class ClickInterceptedError(PlatformError):
    """點擊被攔截"""
    pass

class CaptchaRecognitionError(PlatformError):
    """驗證碼辨識失敗"""
    pass

class SoldOutError(PlatformError):
    """票已售罄"""
    pass
```

### 重試模式

**指數退避重試**（推薦）：
```python
import asyncio
import random

async def retry_with_backoff(operation, max_retry=3, base_wait=0.5):
    """指數退避重試包裝器"""
    for retry_count in range(max_retry):
        try:
            result = await operation()
            return result
        except Exception as exc:
            if retry_count < max_retry - 1:
                wait_time = base_wait * (2 ** retry_count)
                wait_time += random.uniform(0, 0.2)  # 抖動
                await asyncio.sleep(wait_time)
            else:
                raise exc
```

---

## 暫停機制契約（NoDriver 專用）

### 暫停檢查函式

所有 NoDriver 平台函式應在關鍵點呼叫暫停檢查：

```python
# 在 sleep 前檢查
await asyncio_sleep_with_pause_check(seconds, config_dict)

# 在 evaluate 前檢查
result = await evaluate_with_pause_check(tab, js_code, config_dict)
```

**暫停點位置**（建議）：
1. 階段開始前
2. 重載頁面前
3. 等待用戶選擇前
4. 長時間 sleep 前

---

## 日誌記錄契約

### 日誌格式

所有平台函式應遵循一致的日誌格式：

**格式**：`[STAGE] message`

**階段代號**：
- `[INIT]`：初始化
- `[AUTH]`：身份認證
- `[RELOAD]`：頁面重載
- `[DATE]`：日期選擇
- `[AREA]`：區域選擇
- `[TICKET]`：票數設定
- `[CAPTCHA]`：驗證碼處理
- `[FORM]`：表單填寫
- `[TERMS]`：同意條款
- `[SUBMIT]`：訂單送出
- `[QUEUE]`：排隊處理
- `[ERROR]`：錯誤
- `[WARNING]`：警告
- `[SUCCESS]`：成功

**範例**：
```python
if config_dict["advanced"]["verbose"]:
    print("[DATE] 找到 3 個可用日期")
    print("[DATE] 使用關鍵字 '10/15' 匹配到：2025/10/15 (日) 19:30")
    print("[AREA] 選擇區域：VIP區 $3000")
```

---

## 平台路由契約

### URL 路由器

主路由器應根據 URL 判斷平台並呼叫對應的 `main` 函式：

```python
async def nodriver_main(tab, url, config_dict):
    """主路由器"""
    if "tixcraft.com" in url:
        return await nodriver_tixcraft_main(tab, url, config_dict)
    elif "kktix.com" in url:
        return await nodriver_kktix_main(tab, url, config_dict)
    elif "ticketplus.com.tw" in url:
        return await nodriver_ticketplus_main(tab, url, config_dict)
    elif "ticket.ibon.com.tw" in url:
        return await nodriver_ibon_main(tab, url, config_dict)
    elif "kham.com.tw" in url:
        return await nodriver_kham_main(tab, url, config_dict)
    else:
        raise ValueError(f"不支援的平台 URL：{url}")
```

---

## 測試契約

### 最小可測試實作

每個平台函式應可獨立測試：

```python
# 測試範例
async def test_tixcraft_date_select():
    """測試 TixCraft 日期選擇"""
    import nodriver

    config_dict = {
        "date_auto_select": {
            "enable": True,
            "date_keyword": "10/15",
            "mode": "from top to bottom"
        },
        "advanced": {"verbose": True}
    }

    browser = await nodriver.start()
    tab = await browser.get("https://tixcraft.com/activity/detail/TEST_EVENT")

    result = await nodriver_tixcraft_date_auto_select(tab, "", config_dict)

    assert result == True, "日期選擇應該成功"

    await browser.stop()
```

---

## 文件契約

### 函式文件字串

每個平台函式應包含文件字串：

```python
async def nodriver_tixcraft_date_auto_select(tab, url, config_dict):
    """
    TixCraft 日期自動選擇

    實作三層回退策略：
    1. 關鍵字匹配：嘗試匹配 date_keyword
    2. 模式選擇：使用 mode 選擇（top/bottom/center/random）
    3. 手動介入：暫停並等待用戶手動選擇

    Args:
        tab (nodriver.Tab): 瀏覽器分頁物件
        url (str): 活動頁面 URL（未使用）
        config_dict (dict): 配置字典

    Returns:
        bool: True 表示選擇成功，False 表示失敗

    Raises:
        ElementNotFoundError: 找不到日期元素時

    Config Keys Used:
        - date_auto_select.enable
        - date_auto_select.date_keyword
        - date_auto_select.mode
        - advanced.verbose
    """
    # 實作...
```

---

## 版本相容性

### NoDriver vs Chrome Driver

雖然介面相似，但兩個版本有以下差異：

| 特性 | NoDriver | Chrome Driver |
|------|----------|---------------|
| **非同步** | `async def` | `def` |
| **物件型別** | `nodriver.Tab` | `uc.Chrome` |
| **元素互動** | `tab.evaluate(js)` | `driver.find_element()` |
| **暫停機制** | ✅ 支援 | ❌ 不支援 |
| **Sleep** | `await tab.sleep()` | `time.sleep()` |

**保持一致的部分**：
- 函式命名（除了前綴）
- 參數順序和名稱
- 返回值型別
- config_dict 結構

---

## 契約遵循檢查表

新平台實作時，使用此檢查表確保契約遵循：

### 必需函式
- [ ] `{driver}_{platform}_main()` - 主協調器
- [ ] `{driver}_{platform}_login()` - 身份認證
- [ ] `{driver}_{platform}_auto_reload()` - 頁面重載
- [ ] `{driver}_{platform}_date_auto_select()` - 日期選擇
- [ ] `{driver}_{platform}_area_auto_select()` - 區域選擇
- [ ] `{driver}_{platform}_ticket_quantity_set()` - 票數設定
- [ ] `{driver}_{platform}_captcha_auto_fill()` - 驗證碼（如需要）
- [ ] `{driver}_{platform}_form_fill()` - 表單填寫（如需要）
- [ ] `{driver}_{platform}_agree_terms()` - 同意條款（如需要）
- [ ] `{driver}_{platform}_submit_order()` - 訂單送出

### 行為契約
- [ ] 三層回退策略實作（日期/區域選擇）
- [ ] 過熱保護實作（頁面重載）
- [ ] 指數退避重試實作（錯誤處理）
- [ ] 暫停機制檢查（NoDriver）
- [ ] 日誌記錄（`verbose` 控制）

### 配置整合
- [ ] 從 `config_dict` 讀取所有設定
- [ ] 不修改 `config_dict`
- [ ] 處理缺失配置鍵（預設值）

### 錯誤處理
- [ ] 使用 try-except 捕獲異常
- [ ] 記錄錯誤訊息
- [ ] 返回正確的布林值

### 文件
- [ ] 函式文件字串完整
- [ ] 列出使用的配置鍵
- [ ] 說明返回值含義

---

**文件狀態**：平台介面契約完成
**最後更新**：2025-10-16
**下一步**：創建 util-interface.md 記錄共享工具函式契約
