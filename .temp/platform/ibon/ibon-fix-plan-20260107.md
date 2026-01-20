# iBon 購票流程 4 問題修復計畫

**日期**：2026-01-07
**範圍**：iBon 平台購票流程修復
**用戶回報來源**：Discord 截圖

---

## 問題摘要

| # | 問題 | 位置 | 嚴重度 | 影響 |
|---|------|------|--------|------|
| 1 | 不自動輸入張數/驗證碼 | Line 13427-13466 | High | 卡在頁面重整 |
| 2 | 「已售完」無限輪迴 | Line 13797-13807 | High | 無法脫離 |
| 3 | 多票種只選第一個 SELECT | Line 11327 | Medium | 選錯票種 |
| 4 | 關鍵字無法區分票種 | Line 11304-11366 | Medium | 無法精確匹配 |

---

## 用戶回報內容

### 截圖 #1（v2025.12.24）
- 不會自動輸入張數和驗證碼
- 卡在「座位/數量」頁面重整

### 截圖 #2（v2025.12.26 - 多票種問題）
頁面結構：
| 票種名稱 | 價格 | SELECT 索引 |
|---------|------|-------------|
| 預售票 + 福利券 | 1,000 | selects[0] |
| 預售票 | 999 | selects[1] |

**問題**：程式只選第一個 SELECT，完全忽略票種名稱

### 用戶需求
1. 票種選擇需要根據關鍵字匹配
2. 票種選擇需要支援排除關鍵字

---

## 修改檔案

- `src/nodriver_tixcraft.py`

---

## 修復方案

### 問題 #1：流程順序錯誤

**原因**：驗證碼的 auto_submit 會檢查票數是否已選，但執行順序是先驗證碼後票數。

**修改位置**：Line 13427-13466

**修改內容**：
```
現行順序：
  Step 2: 驗證碼處理 (Line 13427-13440)
  Step 3: 票數選擇 (Line 13441-13466)

修正順序：
  Step 2: 票數選擇
  Step 3: 驗證碼處理
```

**同步修改**：Line 13546-13630 (is_area_already_selected 分支) 也需要調整順序。

**技術細節**：
- `nodriver_ibon_keyin_captcha_code()` 在 Line 11701-11825 會檢查票數是否已選
- 如果票數未選，`auto_submit` 會失敗，返回 `(False, False)`
- 調整順序後，驗證碼處理時票數已經選擇，`auto_submit` 成功

---

### 問題 #2：售完無限輪迴

**原因**：售完後執行 `tab.back()` + `tab.reload()`，回到未刷新的票區頁面，導致無限循環。

**修改位置**：Line 13797-13807

**修改內容**：
```python
# 現行代碼
if is_sold_out:
    await tab.back()
    await tab.reload()

# 修正代碼：導航到票區選擇頁面
if is_sold_out:
    # EventBuy URL: /EventBuy/{eventId}/{sessionId}/{areaId}
    # Event URL:    /Event/{eventId}/{sessionId}
    parts = url.split('/')
    if len(parts) >= 7 and 'eventbuy' in parts[3].lower():
        # 回到票區選擇頁面
        event_url = '/'.join(parts[:3] + ['Event', parts[4], parts[5]])
        await tab.get(event_url)
    else:
        await tab.back()

    await asyncio.sleep(auto_reload_interval)
```

**技術細節**：
- EventBuy URL 格式：`https://ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}`
- Event URL 格式：`https://ticket.ibon.com.tw/Event/{eventId}/{sessionId}`
- 導航到 Event 頁面會重新載入票區列表，避免無限輪迴

---

### 問題 #3 & #4：票種關鍵字匹配

**原因**：Line 11327 硬編碼 `selects[0]`，不考慮票種名稱。

**修改位置**：`nodriver_ibon_ticket_number_auto_select()` (Line 11254-11397)

**修改內容**：

#### Step 1：擴充 JavaScript 提取票種資訊
```javascript
// 取得所有票種列表（名稱、價格、是否有票）
let result = [];
let rows = document.querySelectorAll('table.rwdtable tbody tr');
rows.forEach((row, index) => {
    let select = row.querySelector('select.form-control-sm');
    if (!select) return;

    let nameCell = row.querySelector('td:first-child');
    let ticketName = nameCell ? nameCell.textContent.trim() : '';

    let hasValidOption = Array.from(select.options).some(
        opt => opt.value !== '0' && opt.value !== ''
    );

    result.push({
        index: index,
        name: ticketName,
        hasValidOption: hasValidOption
    });
});
return result;
```

#### Step 2：Python 端關鍵字匹配
```python
# 取得設定
area_keyword = config_dict["area_auto_select"]["area_keyword"]
keyword_exclude = config_dict.get("keyword_exclude", "")

# 解析關鍵字陣列
area_keyword_array = util.parse_keyword_string_to_array(area_keyword)

# 過濾有效票種（有可選數量）
valid_tickets = [t for t in ticket_types if t.get('hasValidOption')]

# 排除關鍵字過濾
filtered_tickets = []
for ticket in valid_tickets:
    ticket_name = ticket.get('name', '')
    if not util.reset_row_text_if_match_keyword_exclude(config_dict, ticket_name):
        filtered_tickets.append(ticket)

# 關鍵字匹配（AND 邏輯）
matched_ticket = None
for keyword_item in area_keyword_array:
    for ticket in filtered_tickets:
        ticket_name = util.format_keyword_string(ticket.get('name', ''))
        keyword_parts = keyword_item.split(' ')
        is_match = all(
            util.format_keyword_string(kw) in ticket_name
            for kw in keyword_parts
        )
        if is_match:
            matched_ticket = ticket
            break
    if matched_ticket:
        break

# 回退：無關鍵字設定或 fallback 時使用第一個
if not matched_ticket and filtered_tickets:
    matched_ticket = filtered_tickets[0]

# 設定票數
if matched_ticket:
    target_index = matched_ticket['index']
    await tab.evaluate(f'''
        (function() {{
            let rows = document.querySelectorAll('table.rwdtable tbody tr');
            let row = rows[{target_index}];
            if (!row) return false;

            let select = row.querySelector('select.form-control-sm');
            if (!select) return false;

            select.value = "{ticket_number}";
            select.dispatchEvent(new Event('change', {{bubbles: true}}));
            return true;
        }})();
    ''')
```

**複用現有機制**：
- `util.reset_row_text_if_match_keyword_exclude()` - 排除關鍵字檢查
- `util.format_keyword_string()` - 關鍵字格式化
- `util.parse_keyword_string_to_array()` - 關鍵字解析

---

## 頁面結構驗證

**EventBuy 頁面票種表格**（已從 `.temp/ibon/ibon-evenbuy.html` 驗證）：
```html
<table class="rwdtable">
  <tbody>
    <tr>
      <td data-title="內容">全票</td>  <!-- 第一個 td：票種名稱 -->
      <td data-title="說明"></td>
      <td data-title="價格(NT$)">1,088</td>
      <td><select class="form-control-sm">...</select></td>  <!-- SELECT元素 -->
    </tr>
  </tbody>
</table>
```

**JavaScript 修改策略**：
- 使用 `table.rwdtable tbody tr` 遍歷所有票種
- 從 `td:first-child` 提取票種名稱
- 從 `td:nth-child(4) select` 獲取 SELECT 元素

**舊版 .aspx 頁面回退**：
```javascript
// Fallback 1: old .aspx format
if (selects.length === 0) {
    selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
}

// Fallback 2: generic form-control-sm
if (selects.length === 0) {
    selects = document.querySelectorAll('select.form-control-sm');
}
```

---

## 測試驗證

### 測試 #1：流程順序
1. 進入 UTK0201_001 頁面
2. 啟用 verbose 模式
3. 確認日誌順序：`[TICKET]` 先於 `[CAPTCHA]`
4. 確認驗證碼自動提交成功

### 測試 #2：售完輪迴
1. 進入 EventBuy 頁面，選擇已售完票區
2. 確認導航到 Event 頁面（非無限重整）

### 測試 #3 & #4：票種匹配
```
場景：多票種頁面
- 預售票 + 福利券 (1,000)
- 預售票 (999)

測試 A：設定關鍵字「預售票」
- 預期：選擇「預售票」(999)

測試 B：設定排除關鍵字「福利」
- 預期：選擇「預售票」(999)

測試 C：設定 AND 邏輯「預售 一般」
- 預期：不匹配「預售票 + 福利券」
```

---

## 向後兼容

| 情況 | 行為 |
|------|------|
| 無關鍵字設定 | 保持現有行為（選第一個） |
| 單一票種 | 自動選擇唯一票種 |
| 舊版 .aspx 頁面 | JavaScript 選擇器有 fallback |

---

## 實作順序

1. **問題 #3 & #4**：票種關鍵字匹配（最核心，影響範圍最大）
2. **問題 #1**：流程順序調整（依賴票種選擇完成）
3. **問題 #2**：售完回退機制（獨立修改）

---

## 憲法合規性檢查

### I. 技術架構
- ✅ 修改 NoDriver 版本（`src/nodriver_tixcraft.py`）
- ❌ 不涉及 UC 或 Selenium

### II. 共用庫保護
- ⚠️ 使用 `util.py` 函式：
  - `reset_row_text_if_match_keyword_exclude()`
  - `format_keyword_string()`
  - `parse_keyword_string_to_array()`
- ✅ 只是調用，不修改 util.py

### III. 設定驅動
- ✅ 複用現有設定：
  - `area_keyword` - 票區關鍵字（現在也用於票種）
  - `keyword_exclude` - 排除關鍵字
- ❌ 不新增設定項

### IV. 程式碼安全
- ✅ 無 emoji in .py
- ✅ 無硬寫敏感資訊

### V. Git 工作流程
- 需使用 `/gsave` 提交
- 測試通過後再推送

---

## 探索與規劃記錄

### Phase 1: 探索（2 agents）
1. **Agent a164345** - iBon 購票流程探索
   - 分析 4 個問題的根本原因
   - 定位相關函式與行數

2. **Agent a45f791** - 關鍵字匹配機制探索
   - 分析現有關鍵字匹配邏輯（AND/OR）
   - 確認排除關鍵字實現

### Phase 2: 設計（1 agent）
- **Agent a759e1b** - 實現計畫設計
  - 提供詳細修復方案
  - 確認向後兼容策略

### Phase 3: 驗證
- 讀取關鍵代碼確認理解正確
- 讀取 `.temp/ibon/ibon-evenbuy.html` 驗證頁面結構

---

## MCP 測試記錄

### 實際頁面驗證（2026-01-07）

**頁面 URL**：
```
https://orders.ibon.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_ID=B0AJUJVF&GROUP_ID=&PERFORMANCE_PRICE_AREA_ID=B0AJUXDI
```

**頁面類型**：UTK02 (舊版購票頁面)

**票種結構驗證**：
| 索引 | 票種名稱 | 說明 | 價格 | SELECT Name |
|------|---------|------|------|-------------|
| **0** | **預售票＋福利券** | 選購此票券才能享有福利 | 1,000 | `ctl02$AMOUNT_DDL` |
| **1** | **預售票** | | 999 | `ctl03$AMOUNT_DDL` |

**問題確認**：
- 現有程式碼 `selects[0]` → 選到「預售票＋福利券」（錯誤）
- 用戶設定關鍵字「預售票」→ 應該選「預售票」（index 1）

**表格結構**：
```html
<table class="table table-sm rwdtable" id="ctl00_ContentPlaceHolder1_DataGrid">
  <thead class="thead-dark">
    <tr>
      <th>內容</th>
      <th>說明</th>
      <th>價格(NT$)</th>
      <th>購買數量</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-title="內容">預售票＋福利券</td>
      <td>選購此票券才能享有福利</td>
      <td>1,000</td>
      <td><select name="ctl02$AMOUNT_DDL">...</select></td>
    </tr>
    <tr>
      <td data-title="內容">預售票</td>
      <td></td>
      <td>999</td>
      <td><select name="ctl03$AMOUNT_DDL">...</select></td>
    </tr>
  </tbody>
</table>
```

**JavaScript 選擇器確認**：
- 舊版頁面：`table.table select[name*="AMOUNT_DDL"]`
- 新版頁面：`table.rwdtable select.form-control-sm`
- 兩種選擇器都適用於此頁面

**驗證結果**：計畫中的修復方案完全正確

---

## 相關文檔

- **用戶回報**：Discord 截圖（v2025.12.24, v2025.12.26）
- **憲法**：`.specify/memory/constitution.md` v2.2.0
- **開發標準**：`.claude/skills/ticket-dev-skill/` 12 階段標準

---

## 注意事項

1. **憲法第 II 條**：雖然使用 `util.py` 函式，但不修改共用庫
2. **測試紀律**：修改完成後必須測試（憲法第 VIII 條）
3. **提交前驗證**：確保沒有破壞現有功能
