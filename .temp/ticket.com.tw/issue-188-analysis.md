# Issue #188 - ERA TICKET (ticket.com.tw) Bug 深度分析報告

**建立日期**: 2025-12-15
**Issue URL**: https://github.com/bouob/tickets_hunter/issues/188
**相關 Issue**: #177 (同平台類似問題)

---

## 1. 問題總覽

| 編號 | 問題描述 | 嚴重程度 | 狀態 |
|------|----------|----------|------|
| Q1 | 等待開賣的場次首頁不會自動刷新至開賣時間 | **高** | Bug 確認 |
| Q2 | 選擇票別&座位後沒有自動加入購物車，連號會點選到前後排 | **高** | 需驗證 |
| Q3 | 速度沒有像設定的參數那麼快 | **中** | 設計限制 |

---

## 2. Q1: 等待開賣頁面不會自動刷新

### 2.1 問題根源分析

**測試 URL**: `https://ticket.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P14GOB32`

#### MCP 檢查結果

頁面流程：
```
UTK0201_.aspx (產品頁)
    → 點擊「立即訂購」
    → UTK0201_00.aspx (場次選擇頁)
        → 顯示「尚未開賣 2025/12/17 13:00:00啟售」按鈕
```

**「尚未開賣」按鈕 HTML 結構**:
```html
<button type="button" class="btn btn-event active disabled">
    尚未開賣<br>
    <font style="font-size: .7em;">2025/12/17<br>13:00:00啟售</font>
</button>
```

**關鍵發現**:
1. 按鈕使用 CSS class `disabled` 而非 HTML `disabled` 屬性
2. `disabled: false` (HTML 屬性未設定)
3. 頁面**沒有** JavaScript 倒計時元素
4. 按鈕文字是「尚未開賣」而非「立即訂購」

### 2.2 程式碼問題定位

**檔案**: `src/nodriver_tixcraft.py`
**函數**: `nodriver_kham_date_auto_select()` (Line 16336-16595)

```python
# Line 16391-16392: 過濾 disabled 按鈕
if ' disabled">' in row_html:
    continue

# Line 16396-16400: 過濾非購票按鈕
if '<button' in row_html:
    if '立即訂購' not in row_html and '點此購票' not in row_html:
        continue
else:
    continue  # No button, skip
```

**問題**:
1. `' disabled">'` 會匹配到 `class="... disabled">`，導致「尚未開賣」按鈕被過濾
2. 按鈕文字「尚未開賣」不包含「立即訂購」或「點此購票」，再次被過濾
3. 結果：`formated_area_list` 為空，觸發重新載入但沒有等待開賣時間的機制

### 2.3 解決方案

#### 方案 A: 支援「尚未開賣」狀態等待 (推薦)

```python
# 在 nodriver_kham_date_auto_select() 中新增

# 1. 檢測「尚未開賣」按鈕並提取開賣時間
async def detect_coming_soon_button(tab, domain_name):
    """檢測 ERA TICKET 的「尚未開賣」按鈕並提取開賣時間"""
    result = await tab.evaluate('''
        (function() {
            // 尋找「尚未開賣」按鈕
            const buttons = document.querySelectorAll('button.btn-event');
            for (const btn of buttons) {
                if (btn.innerText.includes('尚未開賣') && btn.innerText.includes('啟售')) {
                    // 提取開賣時間 (格式: 2025/12/17 13:00:00)
                    const text = btn.innerText;
                    const match = text.match(/(\d{4}\/\d{2}\/\d{2})\s*(\d{2}:\d{2}:\d{2})/);
                    if (match) {
                        const dateStr = match[1] + ' ' + match[2];
                        const saleTime = new Date(dateStr.replace(/\//g, '-'));
                        const now = new Date();
                        const diffMs = saleTime - now;
                        return {
                            found: true,
                            saleTime: dateStr,
                            diffSeconds: Math.floor(diffMs / 1000),
                            buttonText: btn.innerText.trim()
                        };
                    }
                }
            }
            return { found: false };
        })();
    ''')
    return result

# 2. 等待開賣時間到達後自動刷新
async def wait_for_sale_time(tab, config_dict, sale_info):
    """等待開賣時間到達"""
    show_debug = config_dict["advanced"].get("verbose", False)
    diff_seconds = sale_info.get('diffSeconds', 0)

    if diff_seconds > 0:
        if show_debug:
            print(f"[ERA TICKET] 距離開賣還有 {diff_seconds} 秒")
            print(f"[ERA TICKET] 開賣時間: {sale_info.get('saleTime')}")

        # 提前 3 秒開始準備
        wait_time = max(0, diff_seconds - 3)

        if wait_time > 60:
            # 超過 1 分鐘，顯示倒計時
            if show_debug:
                print(f"[ERA TICKET] 等待 {wait_time} 秒後開始搶票...")
            await asyncio.sleep(wait_time)
        else:
            # 最後 1 分鐘，每秒檢查
            for i in range(wait_time):
                await tab.sleep(1)
                if show_debug and i % 10 == 0:
                    print(f"[ERA TICKET] 倒數 {wait_time - i} 秒...")

        # 時間到，立即刷新
        if show_debug:
            print("[ERA TICKET] 開賣時間到達，刷新頁面！")
        await tab.reload()
        return True

    return False
```

#### 方案 B: 修改過濾邏輯 (最小改動)

```python
# Line 16391-16392 修改為更精確的過濾
# 原本:
if ' disabled">' in row_html:
    continue

# 修改為: 檢查 HTML disabled 屬性而非 CSS class
if 'disabled="disabled"' in row_html or 'disabled=""' in row_html:
    continue

# Line 16396-16400 新增「尚未開賣」支援
if '<button' in row_html:
    # 新增「尚未開賣」作為有效選項（點擊後在頁面等待）
    valid_texts = ['立即訂購', '點此購票', '尚未開賣']
    if not any(text in row_html for text in valid_texts):
        continue
```

### 2.4 測試建議

```bash
# 測試步驟
1. 找一個「尚未開賣」的活動頁面
2. 設定 settings.json:
   - homepage: "https://ticket.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=xxx"
   - verbose: true
   - auto_reload_coming_soon_page: true

3. 執行測試:
   timeout 120 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/ticket.com.tw/q1_test.log 2>&1

4. 檢查日誌:
   grep -i "尚未開賣\|coming\|reload\|sale" .temp/ticket.com.tw/q1_test.log
```

---

## 3. Q2: 座位選擇與加入購物車問題

### 3.1 問題分析

**測試 URL**: `https://ticket.com.tw/application/UTK02/UTK0205_.aspx?PERFORMANCE_ID=P14NPP3K&GROUP_ID=37&PERFORMANCE_PRICE_AREA_ID=P14NPWGX`

#### MCP 檢查結果

**頁面結構**:
```
Step 1: 選擇場次 (已完成)
Step 2: 座位/數量 ← 當前頁面
Step 3: 購物車
Step 4: 結帳
Step 5: 完成訂購
```

**票別按鈕**:
- `原價-NT$4,600` (數量: 0)
- `身心障礙者-NT$2,300` (數量: 0)
- `身障陪同者-NT$2,300` (數量: 0)

**座位結構分析**:
```json
{
  "totalAvailable": 24,
  "rowAnalysis": {
    "8": {"count": 1, "seats": [13], "consecutive": true},
    "9": {"count": 2, "seats": [13, 18], "consecutive": false},
    "13": {"count": 4, "seats": [11, 12, 15, 16], "consecutive": false},
    "14": {"count": 9, "seats": [11-19], "consecutive": true},
    "15": {"count": 6, "seats": [13-18], "consecutive": true}
  }
}
```

**登入區域**:
- 需要輸入帳號、密碼、驗證碼
- 「加入購物車」按鈕

### 3.2 「連號會點選到前後排」問題分析

**程式碼位置**: `nodriver_tixcraft.py:19808-19980`

**現有邏輯**:
1. 按排號 (`rowNum`) 分組座位
2. 在每排內按 DOM 位置 (`domIndex`) 判斷連續性
3. `domGap > 1` 則認為不連續

**可能問題**:
1. **DOM 結構不一致**: 座位圖可能有隱藏的 TD 元素（走道、空格）
2. **排號解析錯誤**: title 格式 `2樓2D區-8排-13號` 解析可能出錯
3. **跨排選擇**: 如果某排座位不足，程式碼會跳到下一排，但不應該跨排選擇

**驗證腳本**:
```javascript
// 在瀏覽器 Console 中執行
(function() {
    const availableSeats = document.querySelectorAll('td[title][style*="icon_chair_empty"]');
    const rowMap = {};

    availableSeats.forEach((seat, i) => {
        const title = seat.getAttribute('title');
        const parts = title.split('-');
        if (parts.length >= 3) {
            const rowNum = parts[1].replace('排', '');
            if (!rowMap[rowNum]) rowMap[rowNum] = [];
            rowMap[rowNum].push({
                seatNum: parts[2].replace('號', ''),
                title: title,
                domRow: seat.parentElement.rowIndex,
                domCol: seat.cellIndex
            });
        }
    });

    console.log('座位分布:', rowMap);

    // 檢查是否有跨排的 DOM 位置
    for (const [row, seats] of Object.entries(rowMap)) {
        const domRows = [...new Set(seats.map(s => s.domRow))];
        if (domRows.length > 1) {
            console.warn(`警告: ${row}排的座位分布在多個 DOM 行: ${domRows}`);
        }
    }
})();
```

### 3.3 「沒有自動加入購物車」問題分析

**程式碼流程** (`nodriver_ticket_seat_main`, Line 20293-20437):
```
1. nodriver_ticket_seat_type_auto_select() - 選擇票別
2. nodriver_ticket_seat_auto_select() - 選擇座位
3. nodriver_kham_captcha() - 處理驗證碼
4. 點擊「加入購物車」按鈕
```

**可能問題**:
1. **需要登入**: 頁面顯示需要登入帳號才能加入購物車
2. **驗證碼未處理**: 如果 `ocr_captcha.enable = false`，驗證碼不會自動填寫
3. **按鈕選擇器不正確**: 「加入購物車」按鈕可能使用不同的選擇器

**「加入購物車」按鈕分析**:
```html
<button class="btn btn-danger btn-block">加入購物車</button>
```

**程式碼中的選擇器** (Line 20349-20358):
```python
submitButton = document.querySelector('button.sumitButton[onclick*="addShoppingCart1"]')
# 備用:
submitButton = document.querySelector('button.btn.sumitButton')
submitButton = document.querySelector('button[onclick*="addShoppingCart1"]')
submitButton = document.querySelector('button.sumitButton')
```

**問題**: 實際按鈕是 `btn btn-danger btn-block`，沒有 `sumitButton` class！

### 3.4 解決方案

#### 修復「加入購物車」按鈕選擇器

```python
# Line 20349-20358 修改
result = await tab.evaluate(f'''
    (function() {{
        const showDebug = {json.dumps(show_debug)};

        // 多個備用選擇器 (包含 ERA TICKET 的 btn-danger)
        const selectors = [
            'button.sumitButton[onclick*="addShoppingCart1"]',
            'button.btn.sumitButton',
            'button[onclick*="addShoppingCart1"]',
            'button.sumitButton',
            'button.btn-danger:contains("加入購物車")',  // 新增
            'button.btn-danger.btn-block',  // 新增
            'button:contains("加入購物車")'  // 新增
        ];

        let submitButton = null;
        for (const selector of selectors) {{
            try {{
                if (selector.includes(':contains')) {{
                    // 手動實作 :contains
                    const buttons = document.querySelectorAll('button');
                    const text = selector.match(/:contains\("([^"]+)"\)/)[1];
                    submitButton = Array.from(buttons).find(b => b.innerText.includes(text));
                }} else {{
                    submitButton = document.querySelector(selector);
                }}
                if (submitButton) break;
            }} catch (e) {{}}
        }}

        if (submitButton && !submitButton.disabled) {{
            submitButton.click();
            return true;
        }}
        return false;
    }})();
''')
```

### 3.5 測試建議

```bash
# 測試步驟
1. 先手動登入 ticket.com.tw
2. 設定 settings.json:
   - homepage: UTK0205 座位選擇頁面 URL
   - ticket_number: 2
   - area_keyword: "原價"
   - verbose: true
   - ocr_captcha.enable: true

3. 執行測試:
   timeout 60 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/ticket.com.tw/q2_test.log 2>&1

4. 檢查日誌:
   grep -i "SEAT\|SUBMIT\|cart\|click" .temp/ticket.com.tw/q2_test.log
```

---

## 4. Q3: 速度參數問題

### 4.1 固定延遲分析

**目前程式碼中的固定延遲**:

| 位置 | 延遲時間 | 用途 |
|------|----------|------|
| `nodriver_kham_date_auto_select:16345` | 0.6s | 等待頁面載入 |
| `nodriver_ticket_seat_type_auto_select:19511` | 1.5s | 票別選擇後等待 AJAX |
| `nodriver_ticket_seat_main:20319` | 2.0s | 票別選擇後等待座位表載入 |
| `nodriver_ticket_seat_main:20398-20406` | 0.5s * 10 | 等待對話框出現 |
| `nodriver_kham_main:17680-17681` | 0.3s | 滾動按鈕到視野 |
| `nodriver_kham_main:17694-17744` | 0.5s * N | 等待對話框/URL 變化 |

**總計**: 最少 4-5 秒的固定延遲

### 4.2 動態等待方案評估

#### 方案 A: 元素存在檢查 (推薦)

```python
async def wait_for_element(tab, selector, timeout_ms=5000, interval_ms=100):
    """等待元素出現，取代固定延遲"""
    elapsed = 0
    while elapsed < timeout_ms:
        try:
            element = await tab.query_selector(selector)
            if element:
                return element
        except:
            pass
        await tab.sleep(interval_ms / 1000)
        elapsed += interval_ms
    return None

# 使用範例: 等待座位表載入
# 原本: await tab.sleep(2.0)
# 改為:
seat_table = await wait_for_element(tab, '#locationChoice table td[title]', timeout_ms=5000)
if seat_table:
    # 座位表已載入，立即繼續
    pass
```

#### 方案 B: MutationObserver 監聽 DOM 變化

```python
async def wait_for_dom_change(tab, selector, timeout_ms=5000):
    """監聽 DOM 變化，等待元素更新"""
    result = await tab.evaluate(f'''
        new Promise((resolve) => {{
            const target = document.querySelector('{selector}');
            if (!target) {{
                resolve(false);
                return;
            }}

            const observer = new MutationObserver((mutations) => {{
                observer.disconnect();
                resolve(true);
            }});

            observer.observe(target, {{
                childList: true,
                subtree: true,
                attributes: true
            }});

            // 超時處理
            setTimeout(() => {{
                observer.disconnect();
                resolve(false);
            }}, {timeout_ms});
        }})
    ''')
    return result
```

#### 方案 C: 網路請求完成檢查

```python
async def wait_for_network_idle(tab, timeout_ms=5000):
    """等待網路請求完成"""
    # 使用 CDP 監聽網路活動
    from nodriver import cdp

    # 啟用網路監聽
    await tab.send(cdp.network.enable())

    last_activity = time.time()
    while (time.time() - last_activity) < 0.5:  # 0.5 秒無活動視為完成
        await tab.sleep(0.1)
        # 這裡需要實作網路活動監聽

    return True
```

### 4.3 建議的優化策略

```python
# 新增設定選項
config_dict["advanced"]["smart_wait"] = {
    "enable": True,
    "min_wait_ms": 100,      # 最小等待時間
    "max_wait_ms": 5000,     # 最大等待時間
    "check_interval_ms": 100  # 檢查間隔
}

# 統一的智慧等待函數
async def smart_wait(tab, config_dict, wait_type, selector=None):
    """
    智慧等待：根據元素狀態動態調整等待時間

    wait_type:
    - 'page_load': 等待頁面載入完成
    - 'ajax': 等待 AJAX 請求完成
    - 'element': 等待特定元素出現
    - 'element_change': 等待元素內容變化
    """
    smart_config = config_dict["advanced"].get("smart_wait", {})

    if not smart_config.get("enable", False):
        # 回退到固定延遲
        fallback_delays = {
            'page_load': 0.6,
            'ajax': 1.5,
            'element': 2.0,
            'element_change': 0.5
        }
        await tab.sleep(fallback_delays.get(wait_type, 1.0))
        return

    min_wait = smart_config.get("min_wait_ms", 100) / 1000
    max_wait = smart_config.get("max_wait_ms", 5000) / 1000
    interval = smart_config.get("check_interval_ms", 100) / 1000

    # 最小等待
    await tab.sleep(min_wait)

    elapsed = min_wait
    while elapsed < max_wait:
        if wait_type == 'element' and selector:
            element = await tab.query_selector(selector)
            if element:
                return
        elif wait_type == 'page_load':
            ready_state = await tab.evaluate('document.readyState')
            if ready_state == 'complete':
                return
        # ... 其他等待類型

        await tab.sleep(interval)
        elapsed += interval
```

### 4.4 測試建議

```bash
# 比較固定延遲 vs 智慧等待的效能

# 1. 固定延遲測試
time timeout 60 python -u src/nodriver_tixcraft.py --input src/settings.json 2>&1 | tee .temp/ticket.com.tw/speed_fixed.log

# 2. 智慧等待測試 (需實作後)
# 設定 smart_wait.enable = true
time timeout 60 python -u src/nodriver_tixcraft.py --input src/settings.json 2>&1 | tee .temp/ticket.com.tw/speed_smart.log

# 3. 比較結果
grep -i "sleep\|wait\|elapsed" .temp/ticket.com.tw/speed_*.log
```

---

## 5. 測試清單

### 5.1 Q1 測試

- [ ] 找到「尚未開賣」的活動頁面
- [ ] 測試現有程式碼行為（確認被過濾）
- [ ] 實作方案 A 或 B
- [ ] 驗證修復後可以等待開賣時間

### 5.2 Q2 測試

- [ ] 手動登入 ticket.com.tw
- [ ] 測試票別選擇功能
- [ ] 測試座位選擇功能（特別是連號邏輯）
- [ ] 測試「加入購物車」按鈕點擊
- [ ] 驗證整個流程是否順暢

### 5.3 Q3 測試

- [ ] 記錄目前固定延遲的總時間
- [ ] 實作智慧等待函數
- [ ] 比較效能提升幅度
- [ ] 確保穩定性不受影響

---

## 6. 檔案修改清單

| 檔案 | 行號 | 修改內容 |
|------|------|----------|
| `src/nodriver_tixcraft.py` | 16391-16400 | 修改「尚未開賣」過濾邏輯 |
| `src/nodriver_tixcraft.py` | 16572-16593 | 新增等待開賣時間機制 |
| `src/nodriver_tixcraft.py` | 20349-20358 | 修復「加入購物車」按鈕選擇器 |
| `src/nodriver_tixcraft.py` | 多處 | 將固定延遲改為智慧等待 |
| `src/settings.py` | 新增 | `smart_wait` 設定選項 |

---

## 7. 附錄

### A. MCP 檢查指令

```bash
# 啟動 MCP 除錯模式
/mcpstart

# 常用 MCP 工具
mcp__chrome-devtools__take_snapshot    # 擷取 DOM 結構
mcp__chrome-devtools__take_screenshot  # 截圖
mcp__chrome-devtools__evaluate_script  # 執行 JavaScript
mcp__chrome-devtools__click            # 點擊元素
```

### B. 日誌關鍵字

```bash
# Q1 相關
grep -i "尚未開賣\|coming\|reload\|disabled" log.txt

# Q2 相關
grep -i "SEAT\|SUBMIT\|cart\|click\|rowNum\|domIndex" log.txt

# Q3 相關
grep -i "sleep\|wait\|elapsed\|interval" log.txt
```
