# 機制 03：頁面監控 (Stage 3)

**文件說明**：說明搶票系統的頁面監控機制、開賣偵測策略與自動化觸發流程
**最後更新**：2025-11-12

---

## 概述

頁面監控是自動化購票系統的關鍵機制。系統需要持續監控頁面，偵測票券是否開賣（通常通過頁面元素變化、URL 改變或特定訊息出現等方式），然後觸發後續的自動化流程。

**核心目標**：及時偵測票券開賣的時刻，觸發進入購票流程。

**優先度**：🔴 P1 - 核心流程，時間敏感

---

## 頁面監控流程

### 1. 初始等待狀態

#### 1.1 購票頁面辨識
系統確認頁面是否為購票頁面（如活動詳情頁或票券列表頁）。

**購票頁面特徵**：
- URL 包含活動 ID 或編號
- 頁面標題通常包含活動名稱
- 頁面中存在購票相關的元素（如開始時間、價格、選擇按鈕）

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 900-950 (頁面驗證)

**代碼範例**：
```python
async def verify_ticket_page(page):
    """驗證頁面是否為購票頁面"""
    # 檢查 URL
    url = page.url
    if not any(x in url for x in ['event', 'activity', 'ticket', 'show']):
        print(f"[WARNING] 頁面 URL 可能不正確: {url}")

    # 檢查頁面標題
    title = await page.title()
    if not title or len(title.strip()) == 0:
        print("[ERROR] 無法獲取頁面標題")
        return False

    print(f"[MONITOR] 頁面驗證成功: {title}")
    return True
```

#### 1.2 監控狀態提示
向使用者顯示系統正在等待票券開賣。

**提示內容**：
- 當前頁面標題和 URL
- 日期和時間
- 提示「等待票券開賣」

### 2. 票券開賣偵測

#### 2.1 視覺變化監控
監控頁面元素的變化，表示票券已開賣。

**常見視覺變化**：
1. **選擇按鈕出現**
   - 按鈕從禁用（disabled）變為可用
   - 按鈕顏色改變（灰色 → 彩色）
   - 按鈕文字從「敬請期待」變為「選擇」

2. **頁面重新載入**
   - 系統偵測到 DOM 結構大幅改變
   - 新的購票元素出現

3. **訊息提示**
   - 頁面出現「票券已開賣」訊息
   - 出現倒數計時器
   - 出現「現在購票」按鈕

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 950-1050 (票券開賣偵測)

**代碼範例**：
```python
async def monitor_ticket_release(page, timeout: int = 3600000):
    """監控票券開賣（默認 1 小時超時）"""
    start_time = time.time()
    check_interval = 2000  # 每 2 秒檢查一次

    while time.time() - start_time < timeout / 1000:
        try:
            # 檢查選擇按鈕是否出現
            select_button = await page.query_selector('[id*="select"], button:has-text("選擇")')
            if select_button:
                is_enabled = await select_button.is_enabled()
                if is_enabled:
                    print("[MONITOR] 檢測到票券已開賣！")
                    return True

            # 檢查是否有「已開賣」訊息
            sold_message = await page.query_selector(
                'text=已開賣, text=開賣, text=立即購票'
            )
            if sold_message:
                print("[MONITOR] 檢測到開賣訊息")
                return True

            # 等待後再檢查
            await asyncio.sleep(check_interval / 1000)

        except Exception as e:
            print(f"[ERROR] 監控過程中出現錯誤: {e}")
            await asyncio.sleep(check_interval / 1000)

    print("[TIMEOUT] 監控超時，未檢測到票券開賣")
    return False
```

#### 2.2 DOM 變化監控
監控 DOM（文檔對象模型）的變化。

**DOM 變化指標**：
1. **元素計數變化**
   - 票券選項數量增加
   - 日期選項數量增加

2. **元素屬性變化**
   - 按鈕的 `disabled` 屬性被移除
   - 按鈕的 `class` 屬性包含 `active` 或 `enabled`
   - 元素的 `visibility` 或 `display` 改變

3. **新元素出現**
   - 表單容器出現
   - 購票相關的新 div 出現

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1050-1100

**代碼範例**：
```python
async def wait_for_element_enabled(page, selector: str, timeout: int = 3600000):
    """等待特定元素變為可用"""
    try:
        element = await page.wait_for_selector(selector, timeout=timeout)
        await element.wait_for_element_state('enabled', timeout=timeout)
        print(f"[MONITOR] 元素已變為可用: {selector}")
        return True
    except Exception as e:
        print(f"[MONITOR] 等待超時或出錯: {e}")
        return False
```

#### 2.3 網路請求監控
監控頁面的網路請求，偵測票券信息的更新。

**監控網路請求**：
1. **票券列表 API 請求**
   - URL 通常含有 `ticket`、`product`、`session` 等關鍵字
   - 響應中應包含票券信息

2. **頁面更新請求**
   - 某些平台使用定期的 AJAX 請求更新頁面
   - 監控這些請求的響應

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1100-1150

### 3. 監控超時與重試

#### 3.1 超時設定
為避免無限等待，設定合理的超時時間。

**超時設定**：
- 預設超時：1 小時
- 可配置超時：`config_dict['advanced']['monitor_timeout']`

**超時處理**：
1. 記錄超時事件
2. 提示使用者超時
3. 優雅地停止程式或等待使用者操作

#### 3.2 重試邏輯
如果監控過程中出現臨時錯誤，應實現重試機制。

**重試條件**：
- 暫時性網路錯誤（連線超時）
- 瀏覽器暫時無響應
- DOM 解析錯誤

**重試次數**：通常 3-5 次

### 4. 監控狀態報告

#### 4.1 進度日誌
定期記錄監控進度，供使用者了解系統狀態。

**日誌內容**：
- 當前時間
- 距票券開賣時間還有多久
- 監控的檢查次數
- 最後一次檢查結果

**日誌頻率**：
- 每 30-60 秒記錄一次
- 偵測到關鍵變化時立即記錄

**代碼範例**：
```python
async def log_monitoring_status(page, elapsed_minutes: int):
    """記錄監控狀態"""
    title = await page.title()
    url = page.url
    print(f"[MONITOR] {elapsed_minutes} 分鐘已過，監控中... - {title}")
    print(f"[MONITOR] URL: {url}")
```

#### 4.2 監控統計
記錄監控過程的統計信息。

**統計項目**：
- 監控總耗時
- 檢查次數
- 檢查間隔
- 最終結果（成功/超時/失敗）

---

## 平台特定監控

### TixCraft
**特點**：
- 票券開賣時，頁面通常完全刷新
- 可能出現新的日期選擇容器
- 監控 URL 變化是有效的

**監控策略**：
```python
# 監控 URL 變化
prev_url = page.url
await asyncio.sleep(2)
if page.url != prev_url:
    print("[MONITOR] 檢測到 URL 變化，票券開賣")
```

### KKTIX
**特點**：
- 使用 AJAX 動態更新，不刷新頁面
- 監控 DOM 變化（按鈕變為可用）
- 某些活動可能沒有日期選擇

**監控策略**：
```python
# 監控「購票」按鈕狀態
buy_button = await page.wait_for_selector('button[id*="buy"]', timeout=3600000)
```

### iBon
**特點**：
- 使用 Angular 框架，DOM 更新較頻繁
- 票券開賣時會顯示倒數計時器
- 監控特定的 Angular 元素

### TicketPlus
**特點**：
- 頁面元素較多，監控需要更多時間
- 票券通常以表格形式展示

### KHAM
**特點**：
- 頁面加載可能不穩定
- 需要額外的等待時間

---

## 成功標準

**SC-007: 監控響應時間** ≤ 5 秒
- 從票券開賣到系統進入購票流程的時間

**SC-008: 監控準確度** ≥ 98%
- 系統正確偵測票券開賣的次數 / 總監控次數

**SC-009: 錯誤恢復能力** ≥ 90%
- 監控過程中遭遇錯誤時的恢復成功率

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-011 | 頁面監控 | ✅ 實作 |
| FR-012 | 票券開賣偵測 | ✅ 實作 |
| FR-013 | 監控超時 | ✅ 實作 |

---

## 故障排除

### 問題 1: 無法偵測票券開賣
**症狀**：監控超時，未偵測到票券開賣

**可能原因**：
- 選擇器已改變（頁面更新）
- 票券開賣的視覺指示不同
- 網路問題導致未能偵測到變化

**解決方案**：
1. 檢查最新的頁面 HTML 結構
2. 更新選擇器
3. 增加監控的詳細日誌

### 問題 2: 誤偵測票券開賣
**症狀**：未開賣時誤認為已開賣

**可能原因**：
- 選擇器過於寬鬆
- 頁面上有類似的元素
- 暫時性的 DOM 變化

**解決方案**：
1. 改進選擇器的精確性
2. 添加多重驗證條件
3. 檢查多個元素而不是單一元素

### 問題 3: 監控程序中斷
**症狀**：監控過程中程式意外停止

**可能原因**：
- 瀏覽器崩潰
- 網路連接中斷
- 系統資源不足

**解決方案**：
1. 增加錯誤處理和重試邏輯
2. 實現自動重新連接
3. 監控系統資源使用

---

## 最佳實踐

### ✅ 推薦做法

1. **使用多重監控條件**
   - 不要依賴單一的視覺指示
   - 結合 DOM 變化、按鈕狀態、訊息提示等多個條件
   ```python
   conditions = [
       check_button_enabled(),
       check_dom_change(),
       check_message_appeared()
   ]
   if any(conditions):
       print("票券開賣")
   ```

2. **實現適應性監控**
   - 動態調整檢查間隔
   - 票券開賣臨近時縮短間隔
   ```python
   if time_to_release < 60:  # 60秒內
       check_interval = 500  # 每500ms檢查一次
   else:
       check_interval = 2000  # 每2秒檢查一次
   ```

3. **詳細記錄監控狀態**
   - 便於除錯和優化
   - 幫助使用者了解進度

4. **定期驗證選擇器**
   - 監控頁面結構變化
   - 及時更新過期的選擇器

### ❌ 避免做法

1. ❌ 無限期的簡單迴圈檢查
   - 應設定合理的超時時間

2. ❌ 忽略暫時性錯誤
   - 應實現適當的重試邏輯

3. ❌ 過於頻繁的 DOM 查詢
   - 每次查詢都有性能成本
   - 設定合理的檢查間隔

4. ❌ 依賴單一監控條件
   - 應使用多重驗證

---

## 開發檢查清單

- [ ] 頁面驗證邏輯正確
- [ ] 票券開賣偵測準確
- [ ] DOM 變化監控有效
- [ ] 網路請求監控可靠
- [ ] 超時設定合理
- [ ] 重試邏輯正確
- [ ] 日誌記錄詳細
- [ ] 所有平台測試通過

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: ✅ Phase 3 進行中

