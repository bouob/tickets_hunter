# 機制 06：票數設定 (Stage 6)

**文件說明**：說明搶票系統的票數設定機制、數量選擇方式與配置驅動策略
**最後更新**：2025-11-12

---

## 概述

票數設定是確定使用者希望購買的票券數量。系統需要在購票表單中輸入或選擇購票數量，通常在選擇日期和座位區域之後進行。

**核心目標**：正確設定購票數量，符合使用者配置和平台限制。

**優先度**：🟡 P2 - 重要流程

---

## 票數設定流程

### 1. 票數輸入欄位定位

#### 1.1 尋找票數選擇器
系統需要在頁面上定位票數設定的控制項。

**常見的票數選擇方式**：
1. **數字輸入欄** (`<input type="number">`)
   - 使用者可直接輸入數字
   - 通常有最小值和最大值限制

2. **下拉選單** (`<select>`)
   - 顯示預定義的數量選項（1, 2, 3...）
   - 通過選擇項目來設定數量

3. **加減按鈕** (`<button>`)
   - 「+」和「-」按鈕增減數量
   - 通常配合顯示當前數量的標籤

4. **單選框或複選框** (`<input type="radio/checkbox">`)
   - 某些平台使用選項卡形式
   - 選擇對應數量的選項

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1600-1700 (票數選擇器定位)

**代碼範例**：
```python
async def find_ticket_count_selector(page):
    """定位票數選擇器"""
    # 方法 1: 尋找 number 輸入欄
    count_input = await page.query_selector('input[type="number"]')
    if count_input:
        return ('input', count_input)

    # 方法 2: 尋找下拉選單
    count_select = await page.query_selector('select[name*="count"], select[name*="qty"]')
    if count_select:
        return ('select', count_select)

    # 方法 3: 尋找加減按鈕
    plus_btn = await page.query_selector('button[aria-label*="plus"], button[id*="plus"]')
    minus_btn = await page.query_selector('button[aria-label*="minus"], button[id*="minus"]')
    if plus_btn and minus_btn:
        return ('button', (plus_btn, minus_btn))

    return None
```

#### 1.2 獲取數量限制
確定平台允許的最小和最大購票數量。

**限制信息來源**：
1. **HTML 屬性**
   - `<input min="1" max="10" ... >`
   - `<option>` 標籤中的值

2. **頁面文字提示**
   - 例如「每人最多購買 5 張票」
   - 「每場活動最多 10 張」

3. **實時檢查**
   - 嘗試輸入超大數字，觀察是否被拒絕

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1700-1750

**代碼範例**：
```python
async def get_ticket_count_limits(page, selector_element) -> tuple:
    """獲取票數限制 (最小值, 最大值)"""
    try:
        # 嘗試從 HTML 屬性獲取
        min_val = await selector_element.get_attribute('min') or '1'
        max_val = await selector_element.get_attribute('max')

        if max_val:
            return (int(min_val), int(max_val))

        # 若無法從屬性獲取，預設設定
        return (1, 10)

    except Exception as e:
        print(f"[WARNING] 無法獲取票數限制: {e}")
        return (1, 10)  # 預設值
```

### 2. 票數設定

#### 2.1 從配置讀取目標數量
系統從 `settings.json` 讀取使用者希望購買的票數。

**配置欄位**：
```json
{
  "ticket_count": 1,
  "ticket_count_auto": false
}
```

**默認值**：
- 如未指定，默認為 1 張

#### 2.2 數量驗證
驗證目標數量是否在平台限制範圍內。

**驗證邏輯**：
1. 檢查是否 ≥ 最小值
2. 檢查是否 ≤ 最大值
3. 如果超出範圍，調整到最大允許值

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1750-1800

**代碼範例**：
```python
async def set_ticket_count(page, target_count: int, min_count: int, max_count: int):
    """設定票數"""
    # 驗證範圍
    if target_count < min_count:
        print(f"[WARNING] 目標數量 {target_count} 低於最小值 {min_count}，調整為 {min_count}")
        target_count = min_count
    elif target_count > max_count:
        print(f"[WARNING] 目標數量 {target_count} 超過最大值 {max_count}，調整為 {max_count}")
        target_count = max_count

    return target_count
```

### 3. 不同選擇器的處理方式

#### 3.1 數字輸入欄（推薦）
直接輸入數字。

**步驟**：
1. 清除現有值
2. 輸入目標數量
3. 驗證輸入是否成功

**代碼範例**：
```python
async def set_count_via_input(page, selector: str, count: int):
    """通過 input 欄位設定票數"""
    input_elem = await page.query_selector(selector)
    if not input_elem:
        print(f"[ERROR] 無法找到票數輸入欄: {selector}")
        return False

    try:
        # 清除現有值
        await input_elem.triple_click()  # 選中所有文字
        await input_elem.type(str(count))
        print(f"[TICKET_COUNT] 已設定票數: {count}")
        return True
    except Exception as e:
        print(f"[ERROR] 輸入票數失敗: {e}")
        return False
```

#### 3.2 下拉選單
從選單中選擇對應的數量。

**步驟**：
1. 點擊下拉選單
2. 等待選項加載
3. 尋找對應數量的選項
4. 點擊選項

**代碼範例**：
```python
async def set_count_via_select(page, selector: str, count: int):
    """通過 select 欄位設定票數"""
    select_elem = await page.query_selector(selector)
    if not select_elem:
        return False

    try:
        # 設定選擇值
        await select_elem.select_option(str(count))
        print(f"[TICKET_COUNT] 已通過下拉選單設定票數: {count}")
        return True
    except Exception as e:
        print(f"[ERROR] 下拉選單設定失敗: {e}")
        return False
```

#### 3.3 加減按鈕
使用「+」和「-」按鈕調整數量。

**步驟**：
1. 獲取當前數量
2. 計算需要點擊次數
3. 點擊對應次數的「+」或「-」按鈕

**代碼範例**：
```python
async def set_count_via_buttons(page, plus_selector: str, minus_selector: str,
                                current_display_selector: str, target_count: int):
    """通過按鈕設定票數"""
    try:
        # 獲取當前數量
        current_elem = await page.query_selector(current_display_selector)
        current_text = await current_elem.get_text()
        current_count = int(current_text)

        # 計算需要點擊次數
        diff = target_count - current_count
        button_selector = plus_selector if diff > 0 else minus_selector

        # 點擊按鈕
        button = await page.query_selector(button_selector)
        for i in range(abs(diff)):
            await button.click()
            await asyncio.sleep(100)  # 延遲以確保 UI 更新

        print(f"[TICKET_COUNT] 已通過按鈕設定票數: {target_count}")
        return True

    except Exception as e:
        print(f"[ERROR] 按鈕設定失敗: {e}")
        return False
```

### 4. 票數驗證

#### 4.1 設定後驗證
確認票數是否正確設定。

**驗證方法**：
1. 讀取頁面上顯示的票數
2. 檢查是否與目標數量匹配
3. 檢查總金額是否更新（反映票數變化）

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 1800-1850

**代碼範例**：
```python
async def verify_ticket_count(page, expected_count: int) -> bool:
    """驗證票數設定"""
    try:
        # 方法 1: 檢查 input 值
        count_input = await page.query_selector('input[type="number"]')
        if count_input:
            value = await count_input.input_value()
            if int(value) == expected_count:
                print(f"[VERIFY] 票數驗證成功: {value}")
                return True

        # 方法 2: 檢查顯示文字
        count_display = await page.query_selector('.count-display, .ticket-count')
        if count_display:
            text = await count_display.get_text()
            if str(expected_count) in text:
                print(f"[VERIFY] 票數驗證成功: {text}")
                return True

        print(f"[WARNING] 無法驗證票數，可能設定失敗")
        return False

    except Exception as e:
        print(f"[ERROR] 驗證票數失敗: {e}")
        return False
```

---

## 平台特定考量

### TixCraft
- 通常使用數字輸入欄
- 可能有各場次不同的限制
- 總金額實時更新

### KKTIX
- 通常使用下拉選單
- 限制相對寬鬆（通常允許 1-10 張）
- 某些活動可能無票數選擇

### iBon
- 可能使用加減按鈕
- 某些活動有嚴格的數量限制
- 需要檢查「可購數量」欄位

### TicketPlus
- 通常使用下拉選單或輸入欄
- 可能有「每筆訂單最多 X 張」的限制

### KHAM
- 票數限制可能較為複雜
- 某些座位區有不同的限制

---

## 成功標準

**SC-003: 票數選擇成功率** ≥ 95%
- 系統正確設定票數的次數 / 總嘗試次數

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-028 | 票數設定 | ✅ 實作 |
| FR-029 | 數量限制驗證 | ✅ 實作 |

---

## 故障排除

### 問題 1: 無法設定票數
**症狀**：票數設定欄位未找到或設定失敗

**可能原因**：
- 選擇器過時（頁面結構改變）
- 欄位被禁用或隱藏
- 頁面尚未完全加載

**解決方案**：
1. 檢查最新的頁面結構
2. 增加等待時間
3. 更新選擇器

### 問題 2: 票數驗證失敗
**症狀**：設定的票數與預期不符

**可能原因**：
- 平台自動調整了數量（超過限制）
- UI 更新延遲
- 驗證邏輯不正確

**解決方案**：
1. 檢查平台的數量限制
2. 增加等待時間以確保 UI 更新
3. 改進驗證邏輯

---

## 最佳實踐

### ✅ 推薦做法

1. **總是驗證平台的數量限制**
   - 避免設定超出限制的數量
   ```python
   if target_count > max_allowed:
       target_count = max_allowed
   ```

2. **實現多重選擇器支持**
   - 某些平台的 UI 變化較頻繁
   - 提供備選選擇器
   ```python
   selectors = [
       'input[name="count"]',
       'input[id*="qty"]',
       'input.ticket-count'
   ]
   ```

3. **添加延遲以確保 UI 更新**
   - 某些平台 UI 更新較慢
   ```python
   await asyncio.sleep(500)
   ```

### ❌ 避免做法

1. ❌ 假設所有平台的票數限制相同
   - 應動態獲取限制

2. ❌ 無視用戶的配置設定
   - 應尊重 `settings.json` 中的設定

3. ❌ 跳過票數驗證
   - 應確保設定成功

---

## 開發檢查清單

- [ ] 票數選擇器定位正確
- [ ] 數量限制獲取正確
- [ ] 數字輸入欄設定成功
- [ ] 下拉選單選擇成功
- [ ] 加減按鈕邏輯正確
- [ ] 票數驗證準確
- [ ] 所有平台測試通過

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: ✅ Phase 3 進行中

