# Issue #192 深入分析報告

**Issue**: [BUG] iBon 到最後選全票與輸入驗證碼頁面時，不會自動選張數與輸入驗證碼
**回報者**: maakenny
**版本**: v2025.12.15
**平台**: iBon

---

## 問題摘要

使用者回報 iBon 進入票數選擇與驗證碼頁面後，程式無法自動：
1. 選擇票數（張數）
2. 輸入驗證碼

---

## 使用者設定分析

| 項目 | 值 | 說明 |
|------|-----|------|
| 目標網址 | `https://ticket.ibon.com.tw/ActivityInfo/Details/39238` | 活動詳情頁 |
| 執行方式 | exe 執行檔 | 預編譯版本 |
| WebDriver | nodriver（預設） | NoDriver 模式 |

**缺少資訊**（需要使用者補充）：
- 錯誤訊息或日誌
- 是否啟用 OCR 驗證碼辨識
- 進入的購票頁面完整 URL（EventBuy 或 orders.ibon.com.tw）

---

## 程式碼流程分析

### iBon 頁面處理流程

```
ActivityInfo/Details/39238
    │
    ▼ (日期選擇)
nodriver_ibon_date_auto_select() [第 14101-14118 行]
    │
    ▼ (進入購票頁面，可能有 3 種格式)
    │
    ├─ 格式 1: orders.ibon.com.tw/UTK02/UTK0201_001.aspx?PERFORMANCE_PRICE_AREA_ID=xxx
    │   └─ [第 14734-14806 行] 處理票數+驗證碼
    │
    ├─ 格式 2: ticket.ibon.com.tw/Event/{eventId}/{sessionId}
    │   └─ [第 14486-14562 行] 區域選擇
    │       ▼
    │       ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}
    │       └─ [第 14567-14660 行] 處理票數+驗證碼 (NEW EventBuy)
    │
    └─ 格式 3: orders.ibon.com.tw/UTK02/UTK0206_.aspx
        └─ [第 14809-14828 行] 訂單確認頁
```

### 關鍵函數分析

#### 1. 票數選擇 `nodriver_ibon_ticket_number_auto_select()`

**檔案**: `nodriver_tixcraft.py:12781-12936`

**選擇器**（支援多種格式）：
```javascript
// 優先順序
1. 'table.rwdtable select.form-control-sm'    // 新版 EventBuy
2. 'table.table select[name*="AMOUNT_DDL"]'    // 舊版 .aspx
3. 'select.form-control-sm'                    // 通用回退
```

**潛在問題**：
- 如果頁面 DOM 結構變更，選擇器可能失效
- 沒有日誌輸出表示選擇器是否找到元素

#### 2. 驗證碼處理 `nodriver_ibon_captcha()`

**檔案**: `nodriver_tixcraft.py:13595-13690`

**前置條件**：
```python
# 第 13606-13608 行
away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
if not config_dict["ocr_captcha"]["enable"]:
    away_from_keyboard_enable = False
```

**潛在問題**：
- 如果 `ocr_captcha.enable = false`，會進入手動模式但不會自動填入
- 如果 `force_submit = false`，OCR 後不會自動提交

#### 3. 驗證碼輸入框選擇器 `nodriver_ibon_keyin_captcha_code()`

**檔案**: `nodriver_tixcraft.py:13142-13220`

**選擇器**：
```javascript
// 依序嘗試
1. 'input[placeholder*="驗證碼"]'
2. 'input[value="驗證碼"]'
3. '#ctl00_ContentPlaceHolder1_CHK'
```

**潛在問題**：
- 新版 EventBuy 頁面可能使用不同的輸入框選擇器
- Shadow DOM 可能導致無法直接查詢

#### 4. 驗證碼圖片獲取 `nodriver_ibon_get_captcha_image_from_shadow_dom()`

**檔案**: `nodriver_tixcraft.py:12938-13140`

**圖片識別方式**：
```javascript
// 尋找驗證碼圖片
1. IMG 元素: src 包含 '/pic.aspx?TYPE='
2. CANVAS 元素: 新版 EventBuy 格式
```

**潛在問題**：
- Shadow DOM 穿透需要使用 DOMSnapshot CDP API
- 如果圖片格式變更，可能無法正確擷取

---

## 可能原因分析

### 原因 1：OCR 設定未啟用（高機率）

**檢查項目**：
- `ocr_captcha.enable` 是否為 `true`
- `ocr_captcha.force_submit` 是否為 `true`

**驗證方法**：
檢查 `settings.json` 中的設定：
```json
{
  "ocr_captcha": {
    "enable": true,        // 必須為 true
    "force_submit": true   // 建議為 true（自動提交）
  }
}
```

### 原因 2：頁面格式未被識別（中機率）

**可能情況**：
- 新版 iBon 頁面 URL 格式變更
- Angular SPA 路由變更導致 URL 不匹配

**影響代碼**：
```python
# 第 14567 行
if 'ticket.ibon.com.tw' in url.lower() and '/eventbuy/' in url.lower():
```

### 原因 3：Shadow DOM 元素無法訪問（中機率）

**說明**：
iBon 使用 Angular SPA，部分元素可能在 Shadow DOM 內，普通 `querySelector` 無法訪問。

**相關代碼**：
```python
# 第 12952-12957 行 - 使用 DOMSnapshot 穿透 Shadow DOM
documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(...))
```

### 原因 4：票數下拉選單載入延遲（低機率）

**說明**：
程式等待票數下拉選單的最大時間為 1.5 秒（15 次 * 100ms），可能不夠。

**相關代碼**：
```python
# 第 12806 行
const maxAttempts = 15; // 15 * 100ms = 1.5 seconds max wait
```

---

## 需要使用者提供的資訊

為了進一步診斷，請提供：

1. **啟用詳細日誌**：
   在 settings.json 中設定 `"verbose": true`（在 advanced 區塊內）

2. **完整錯誤日誌**：
   重新執行並提供 console 輸出

3. **進入的購票頁面 URL**：
   進入票數選擇頁面後的完整網址

4. **OCR 設定**：
   確認 settings.json 中的 ocr_captcha 區塊設定

---

## 建議修復方向

### 短期修復

1. **增加日誌輸出**：在票數選擇和驗證碼處理函數中增加更多診斷日誌

2. **擴展選擇器**：
   ```python
   # 增加更多備用選擇器
   selectors = [
       'table.rwdtable select.form-control-sm',
       'table.table select[name*="AMOUNT_DDL"]',
       'select.form-control-sm',
       'select[id*="ticket"]',  # 新增
       'select[ng-model*="count"]'  # Angular 專用
   ]
   ```

3. **增加等待時間**：將 maxAttempts 從 15 增加到 30（3 秒）

### 長期修復

1. **統一 Shadow DOM 處理**：使用 CDP DOMSnapshot API 處理所有 iBon 頁面元素

2. **頁面格式偵測優化**：根據頁面內容而非 URL 判斷頁面類型

---

## 相關代碼位置

| 功能 | 檔案 | 行號 |
|------|------|------|
| iBon 主函數 | nodriver_tixcraft.py | 13953-14870 |
| 票數選擇 | nodriver_tixcraft.py | 12781-12936 |
| 驗證碼處理 | nodriver_tixcraft.py | 13595-13690 |
| 驗證碼輸入 | nodriver_tixcraft.py | 13142-13390 |
| Shadow DOM 圖片擷取 | nodriver_tixcraft.py | 12938-13140 |

---

## 建議優先度

**中優先度** - 影響 iBon 平台核心購票功能

需要使用者提供更多資訊才能確定根因。
