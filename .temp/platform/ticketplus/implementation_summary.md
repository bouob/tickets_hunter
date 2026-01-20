# TicketPlus 序號輸入功能 - 實作摘要

**快速決策版** - 供早上評估使用

---

## 問題
- 遠大售票無法自動填入序號（優惠序號 / 加購序號）
- 目前函數已存在但未實作（直接跳過）

---

## 解決方案

### 方案選擇：混合方案（推薦）

**settings.json 新增欄位**：
```json
{
  "advanced": {
    "ticketplus_serial_code": "",        // 通用序號（自動偵測）
    "ticketplus_discount_code": "",      // 優惠序號（明確指定）
    "ticketplus_purchase_code": ""       // 加購序號（明確指定）
  }
}
```

**優先級**: 明確欄位 > 通用欄位

---

## HTML 結構

### 優惠序號
```html
<div class="exclusive-code">
  <div class="label">優惠序號</div>
  <input placeholder="請輸入優惠序號" type="text">
</div>
```

### 加購序號
```html
<div class="exclusive-code">
  <div class="label">加購序號</div>
  <input placeholder="請輸入加購序號" type="text">
</div>
```

---

## 實作重點

### 選擇器策略
1. **主要策略**: 透過 `.label` 文字偵測（「優惠序號」/「加購序號」）
2. **備用策略**: 透過 `placeholder` 屬性偵測
3. **避免依賴**: 動態 ID（如 `input-493`）

### JavaScript 核心邏輯
```javascript
// 偵測標籤文字
const labelDivs = document.querySelectorAll('.exclusive-code .label');
for (let label of labelDivs) {
  const labelText = label.textContent.trim();
  const container = label.closest('.exclusive-code');
  const input = container?.querySelector('input[type="text"]');

  if (labelText.includes('優惠序號') && input) {
    input.value = discountCode || serialCode;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  if (labelText.includes('加購序號') && input) {
    input.value = purchaseCode || serialCode;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
}
```

### 修改函數
`src/nodriver_tixcraft.py` Line 6613
```python
async def nodriver_ticketplus_order_exclusive_code(tab, config_dict, fail_list):
    # 讀取設定
    serial_code = config_dict["advanced"].get("ticketplus_serial_code", "").strip()
    discount_code = config_dict["advanced"].get("ticketplus_discount_code", "").strip()
    purchase_code = config_dict["advanced"].get("ticketplus_purchase_code", "").strip()

    # 使用 tab.evaluate() 執行上述 JavaScript
    # 偵測並填入序號
    # 返回填入結果
```

---

## 需要修改的檔案

1. **src/settings.json** - 新增 3 個欄位
2. **src/nodriver_tixcraft.py** - 實作 `nodriver_ticketplus_order_exclusive_code()` 函數
3. **www/settings.html** - 新增序號輸入框（可選，建議實作）

---

## 風險評估

- **技術風險**: 低（HTML 結構簡單穩定）
- **相容性風險**: 低（僅影響 TicketPlus）
- **測試需求**: 需要真實活動驗證

---

## 預估工時

- **核心實作**: 30-45 分鐘
- **UI 修改**: 15 分鐘（如果需要）
- **測試驗證**: 30 分鐘
- **總計**: 約 1.5-2 小時

---

## 決策點

### 必須決定：
1. 是否採用 3 個欄位（通用 + 明確）？
   - ✅ 推薦：是（最大彈性）
   - ❌ 替代：只用 1 個通用欄位（簡單但功能受限）

2. 是否修改 `www/settings.html`？
   - ✅ 推薦：是（使用者友善）
   - ❌ 替代：使用者手動編輯 JSON（進階使用者可接受）

3. 何時實作？
   - 立即實作（Issue #37 已回報）
   - 延後實作（待更多使用者回報）

---

## 測試計畫

1. **單元測試**:
   - 測試優惠序號偵測與填入
   - 測試加購序號偵測與填入
   - 測試優先級邏輯

2. **整合測試**:
   - 真實活動測試（需要有效序號）
   - 驗證表單提交成功

---

**建議**: 採用混合方案，立即實作，完整修改包含 UI
