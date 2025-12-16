# 延遲優化方案 - 從固定延遲到智慧等待

**建立日期**: 2025-12-15
**相關 Issue**: #188 Q3

---

## 1. 現況分析

### 1.1 固定延遲清單

| 檔案位置 | 延遲 | 用途 | 可優化 |
|----------|------|------|--------|
| `nodriver_kham_date_auto_select:16345` | 0.6s | 等待頁面載入 | **是** |
| `nodriver_ticket_seat_type_auto_select:19474` | 0.2s | 滾動元素到視野 | 否 |
| `nodriver_ticket_seat_type_auto_select:19511` | 1.5s | 票別選擇後等待 AJAX | **是** |
| `nodriver_ticket_seat_main:20319` | 2.0s | 票別選擇後等待座位表 | **是** |
| `nodriver_ticket_seat_main:20398` | 0.5s * 10 | 等待對話框 | **是** |
| `nodriver_kham_main:17474` | 1.0s | 點擊購買按鈕後等待 | **是** |
| `nodriver_kham_main:17680` | 0.3s | 滾動按鈕到視野 | 否 |
| `nodriver_kham_main:17694-17744` | 0.5s * N | 等待對話框/URL | **是** |

**總固定延遲**: 約 4-8 秒（取決於流程）

### 1.2 問題分析

1. **固定延遲的問題**:
   - 網路快時浪費時間
   - 網路慢時可能不夠
   - 無法適應不同環境

2. **搶票場景的特殊性**:
   - 毫秒級的差異可能決定成敗
   - 但過快可能導致操作失敗
   - 需要在速度和穩定性之間取得平衡

---

## 2. 智慧等待方案設計

### 2.1 核心概念

```
固定延遲: sleep(2.0)  →  無論如何都等待 2 秒

智慧等待: wait_for_element(selector, timeout=5.0)
         →  元素出現立即繼續
         →  最多等待 5 秒
         →  實際可能只需 0.3 秒
```

### 2.2 等待類型分類

| 等待類型 | 觸發條件 | 完成條件 | 建議策略 |
|----------|----------|----------|----------|
| 頁面載入 | 導航/刷新 | `document.readyState === 'complete'` | DOM Ready 檢查 |
| AJAX 更新 | 按鈕點擊 | 目標元素出現/更新 | MutationObserver |
| 對話框 | 操作後 | 對話框元素出現 | 輪詢檢查 |
| URL 變化 | 表單提交 | URL 改變 | URL 監聽 |

### 2.3 實作方案

#### 方案 A: 元素輪詢 (簡單穩定)

```python
async def wait_for_element(tab, selector, timeout_ms=5000, interval_ms=100):
    """
    等待元素出現

    Args:
        tab: NoDriver tab 物件
        selector: CSS 選擇器
        timeout_ms: 最大等待時間 (毫秒)
        interval_ms: 檢查間隔 (毫秒)

    Returns:
        element: 找到的元素，或 None（超時）
    """
    elapsed = 0
    while elapsed < timeout_ms:
        try:
            element = await tab.query_selector(selector)
            if element:
                return element
        except Exception:
            pass

        await tab.sleep(interval_ms / 1000)
        elapsed += interval_ms

    return None


async def wait_for_element_change(tab, selector, old_content, timeout_ms=5000):
    """
    等待元素內容變化

    Args:
        tab: NoDriver tab 物件
        selector: CSS 選擇器
        old_content: 變化前的內容
        timeout_ms: 最大等待時間

    Returns:
        bool: 是否偵測到變化
    """
    elapsed = 0
    interval_ms = 100

    while elapsed < timeout_ms:
        try:
            new_content = await tab.evaluate(f'''
                (() => {{
                    const el = document.querySelector('{selector}');
                    return el ? el.innerHTML : null;
                }})()
            ''')

            if new_content and new_content != old_content:
                return True
        except Exception:
            pass

        await tab.sleep(interval_ms / 1000)
        elapsed += interval_ms

    return False
```

#### 方案 B: MutationObserver (更即時)

```python
async def wait_for_dom_mutation(tab, selector, timeout_ms=5000):
    """
    使用 MutationObserver 等待 DOM 變化

    比輪詢更即時，但需要處理 Promise
    """
    result = await tab.evaluate(f'''
        new Promise((resolve, reject) => {{
            const target = document.querySelector('{selector}');

            if (!target) {{
                // 等待元素出現
                const bodyObserver = new MutationObserver((mutations, obs) => {{
                    const el = document.querySelector('{selector}');
                    if (el) {{
                        obs.disconnect();
                        resolve({{ found: true, type: 'appeared' }});
                    }}
                }});

                bodyObserver.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});

                setTimeout(() => {{
                    bodyObserver.disconnect();
                    resolve({{ found: false, type: 'timeout' }});
                }}, {timeout_ms});

                return;
            }}

            // 等待元素變化
            const observer = new MutationObserver((mutations, obs) => {{
                obs.disconnect();
                resolve({{ found: true, type: 'changed', mutations: mutations.length }});
            }});

            observer.observe(target, {{
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            }});

            setTimeout(() => {{
                observer.disconnect();
                resolve({{ found: false, type: 'timeout' }});
            }}, {timeout_ms});
        }})
    ''')

    return result


async def wait_for_seat_table_loaded(tab, timeout_ms=5000):
    """
    專門等待座位表載入完成

    完成條件:
    1. #locationChoice table 存在
    2. 至少有一個 td[title] 座位元素
    """
    result = await tab.evaluate(f'''
        new Promise((resolve) => {{
            const checkLoaded = () => {{
                const table = document.querySelector('#locationChoice table, table#TBL');
                const seats = document.querySelectorAll('td[title][style*="icon_chair"]');
                return table && seats.length > 0;
            }};

            if (checkLoaded()) {{
                resolve({{ loaded: true, waitTime: 0 }});
                return;
            }}

            const startTime = Date.now();
            const observer = new MutationObserver(() => {{
                if (checkLoaded()) {{
                    observer.disconnect();
                    resolve({{
                        loaded: true,
                        waitTime: Date.now() - startTime
                    }});
                }}
            }});

            observer.observe(document.body, {{
                childList: true,
                subtree: true
            }});

            setTimeout(() => {{
                observer.disconnect();
                resolve({{
                    loaded: checkLoaded(),
                    waitTime: {timeout_ms},
                    timeout: true
                }});
            }}, {timeout_ms});
        }})
    ''')

    return result
```

#### 方案 C: 複合策略 (最佳實踐)

```python
class SmartWait:
    """智慧等待管理器"""

    def __init__(self, config_dict):
        self.config = config_dict.get("advanced", {}).get("smart_wait", {})
        self.enabled = self.config.get("enable", False)
        self.min_wait = self.config.get("min_wait_ms", 50) / 1000
        self.max_wait = self.config.get("max_wait_ms", 5000) / 1000
        self.interval = self.config.get("interval_ms", 100) / 1000
        self.verbose = config_dict.get("advanced", {}).get("verbose", False)

    async def wait(self, tab, wait_type, **kwargs):
        """
        統一的等待介面

        wait_type:
        - 'page_ready': 等待頁面完成載入
        - 'element': 等待元素出現 (需要 selector)
        - 'element_change': 等待元素變化 (需要 selector)
        - 'ajax': 等待 AJAX 完成 (需要 selector 或 url_pattern)
        - 'dialog': 等待對話框出現
        - 'url_change': 等待 URL 變化
        """
        if not self.enabled:
            # 回退到固定延遲
            fallback = kwargs.get('fallback', 1.0)
            await tab.sleep(fallback)
            return {'method': 'fallback', 'waited': fallback}

        start_time = time.time()

        # 最小等待（給予頁面反應時間）
        await tab.sleep(self.min_wait)

        result = None

        if wait_type == 'page_ready':
            result = await self._wait_page_ready(tab)

        elif wait_type == 'element':
            selector = kwargs.get('selector')
            result = await self._wait_element(tab, selector)

        elif wait_type == 'element_change':
            selector = kwargs.get('selector')
            result = await self._wait_element_change(tab, selector)

        elif wait_type == 'dialog':
            result = await self._wait_dialog(tab)

        elif wait_type == 'url_change':
            old_url = kwargs.get('old_url', tab.target.url)
            result = await self._wait_url_change(tab, old_url)

        elapsed = time.time() - start_time

        if self.verbose:
            print(f"[SMART WAIT] {wait_type}: {elapsed:.3f}s - {result}")

        return {
            'method': 'smart',
            'type': wait_type,
            'waited': elapsed,
            'result': result
        }

    async def _wait_page_ready(self, tab):
        """等待頁面完成載入"""
        elapsed = 0
        while elapsed < self.max_wait:
            state = await tab.evaluate('document.readyState')
            if state == 'complete':
                return True
            await tab.sleep(self.interval)
            elapsed += self.interval
        return False

    async def _wait_element(self, tab, selector):
        """等待元素出現"""
        elapsed = 0
        while elapsed < self.max_wait:
            element = await tab.query_selector(selector)
            if element:
                return True
            await tab.sleep(self.interval)
            elapsed += self.interval
        return False

    async def _wait_element_change(self, tab, selector):
        """等待元素內容變化"""
        # 先記錄當前內容
        old_content = await tab.evaluate(f'''
            (() => {{
                const el = document.querySelector('{selector}');
                return el ? el.innerHTML : '';
            }})()
        ''')

        elapsed = 0
        while elapsed < self.max_wait:
            new_content = await tab.evaluate(f'''
                (() => {{
                    const el = document.querySelector('{selector}');
                    return el ? el.innerHTML : '';
                }})()
            ''')

            if new_content != old_content:
                return True

            await tab.sleep(self.interval)
            elapsed += self.interval

        return False

    async def _wait_dialog(self, tab):
        """等待對話框出現"""
        dialog_selectors = [
            'div.ui-dialog',
            'div.modal.show',
            'div[role="dialog"]',
            '.swal2-popup'
        ]

        elapsed = 0
        while elapsed < self.max_wait:
            for selector in dialog_selectors:
                element = await tab.query_selector(selector)
                if element:
                    return selector
            await tab.sleep(self.interval)
            elapsed += self.interval

        return None

    async def _wait_url_change(self, tab, old_url):
        """等待 URL 變化"""
        elapsed = 0
        while elapsed < self.max_wait:
            current_url = tab.target.url
            if current_url != old_url:
                return current_url
            await tab.sleep(self.interval)
            elapsed += self.interval
        return None
```

---

## 3. 具體應用場景

### 3.1 票別選擇後等待座位表

**原本**:
```python
# Line 20318-20320
await tab.sleep(2.0)  # 固定等待 2 秒
is_seat_assigned = await nodriver_ticket_seat_auto_select(tab, config_dict)
```

**優化後**:
```python
# 使用智慧等待
smart_wait = SmartWait(config_dict)

# 等待座位表載入
result = await smart_wait.wait(
    tab,
    'element',
    selector='#locationChoice table td[title][style*="icon_chair"]',
    fallback=2.0  # 回退延遲
)

if config_dict["advanced"].get("verbose"):
    print(f"[SEAT TABLE] 座位表載入耗時: {result['waited']:.3f}s")

is_seat_assigned = await nodriver_ticket_seat_auto_select(tab, config_dict)
```

### 3.2 加入購物車後等待對話框

**原本**:
```python
# Line 20398-20410
for i in range(10):  # 固定嘗試 10 次，每次 0.5 秒
    await tab.sleep(0.5)
    dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button')
    if dialog_btn:
        await dialog_btn.click()
        break
```

**優化後**:
```python
# 使用智慧等待
result = await smart_wait.wait(
    tab,
    'dialog',
    fallback=5.0
)

if result['result']:  # 對話框出現
    dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button')
    if dialog_btn:
        await dialog_btn.click()
```

### 3.3 頁面載入等待

**原本**:
```python
# Line 16345
await tab.sleep(0.6)  # 固定等待頁面載入
```

**優化後**:
```python
await smart_wait.wait(
    tab,
    'page_ready',
    fallback=0.6
)
```

---

## 4. 設定檔擴充

### 4.1 settings.json 新增選項

```json
{
    "advanced": {
        "smart_wait": {
            "enable": true,
            "min_wait_ms": 50,
            "max_wait_ms": 5000,
            "interval_ms": 100
        }
    }
}
```

### 4.2 settings.py 設定定義

```python
SMART_WAIT_SETTINGS = {
    "enable": {
        "type": "bool",
        "default": False,
        "description": "啟用智慧等待（實驗性功能）"
    },
    "min_wait_ms": {
        "type": "int",
        "default": 50,
        "min": 0,
        "max": 1000,
        "description": "最小等待時間（毫秒）"
    },
    "max_wait_ms": {
        "type": "int",
        "default": 5000,
        "min": 1000,
        "max": 30000,
        "description": "最大等待時間（毫秒）"
    },
    "interval_ms": {
        "type": "int",
        "default": 100,
        "min": 50,
        "max": 500,
        "description": "檢查間隔（毫秒）"
    }
}
```

---

## 5. 效能預估

### 5.1 理想情況

| 操作 | 固定延遲 | 智慧等待 | 節省 |
|------|----------|----------|------|
| 頁面載入 | 0.6s | ~0.2s | 0.4s |
| 票別選擇 | 1.5s + 2.0s | ~0.5s | 3.0s |
| 對話框等待 | 5.0s | ~0.3s | 4.7s |
| **總計** | ~9.1s | ~1.0s | **~8.1s** |

### 5.2 保守估計

考慮網路延遲和頁面複雜度：

| 操作 | 固定延遲 | 智慧等待 | 節省 |
|------|----------|----------|------|
| 頁面載入 | 0.6s | ~0.4s | 0.2s |
| 票別選擇 | 3.5s | ~1.5s | 2.0s |
| 對話框等待 | 5.0s | ~1.0s | 4.0s |
| **總計** | ~9.1s | ~2.9s | **~6.2s** |

---

## 6. 風險評估

### 6.1 潛在問題

| 風險 | 嚴重度 | 緩解措施 |
|------|--------|----------|
| 元素判斷錯誤 | 中 | 使用多重選擇器、fallback 機制 |
| 過快操作導致失敗 | 高 | 保留 min_wait_ms 最小等待 |
| 瀏覽器相容性 | 低 | 使用標準 DOM API |
| 效能開銷 | 低 | 輪詢間隔可配置 |

### 6.2 建議策略

1. **漸進式導入**: 先在非關鍵路徑測試
2. **保留開關**: 可隨時切回固定延遲
3. **日誌監控**: 記錄實際等待時間，持續優化
4. **A/B 測試**: 比較兩種策略的成功率

---

## 7. 實作優先級

| 優先級 | 項目 | 預估節省 | 複雜度 |
|--------|------|----------|--------|
| 1 | 座位表載入等待 | 2-3s | 低 |
| 2 | 對話框等待 | 3-4s | 低 |
| 3 | 頁面載入等待 | 0.2-0.4s | 低 |
| 4 | URL 變化等待 | 1-2s | 中 |

---

## 8. 測試計畫

### 8.1 單元測試

```python
# tests/test_smart_wait.py

import pytest
import asyncio

class TestSmartWait:
    @pytest.mark.asyncio
    async def test_wait_element_found(self):
        """測試元素快速出現的情況"""
        # ...

    @pytest.mark.asyncio
    async def test_wait_element_timeout(self):
        """測試超時的情況"""
        # ...

    @pytest.mark.asyncio
    async def test_fallback_when_disabled(self):
        """測試停用時使用 fallback"""
        # ...
```

### 8.2 整合測試

```bash
# 測試腳本
#!/bin/bash

echo "=== 固定延遲測試 ==="
time python -u src/nodriver_tixcraft.py --input settings_fixed.json 2>&1

echo "=== 智慧等待測試 ==="
time python -u src/nodriver_tixcraft.py --input settings_smart.json 2>&1
```

---

## 9. 結論

智慧等待方案可以顯著提升搶票效率，預估節省 60-80% 的等待時間。建議：

1. **Phase 1**: 實作基礎的 `wait_for_element` 函數
2. **Phase 2**: 應用到座位表載入和對話框等待
3. **Phase 3**: 全面替換固定延遲
4. **Phase 4**: 收集數據，持續優化

整體實作預估工時：2-3 天
