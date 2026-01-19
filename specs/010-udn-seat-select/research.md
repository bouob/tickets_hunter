# 技術研究：UDN 售票網座位選擇

**分支**：`010-udn-seat-select` | **日期**：2025-12-17

## 研究摘要

本研究分析 UDN 售票網 (tickets.udnfunlife.com) 的技術架構，以確定座位自動選擇功能的最佳實作方案。

**核心結論**：UDN 是 KHAM 家族成員，共用相同的 UTK 後端系統，現有 KHAM 座位選擇邏輯可直接複用。

---

## 1. UDN 與 KHAM 關係

### 1.1 平台架構

| 項目 | KHAM | UDN | 結論 |
|------|------|-----|------|
| 網域 | kham.com.tw / ticket.com.tw | tickets.udnfunlife.com | 不同網域，同一後端 |
| 後端系統 | UTK | UTK | 完全相同 |
| URL 模式 | utk0201_, utk0203_, utk0205_ | utk0201_, utk0203_, utk0205_ | 完全相同 |
| ASP.NET 架構 | 是 | 是 | 完全相同 |

### 1.2 頁面流程對比

| 步驟 | KHAM URL | UDN URL | 差異 |
|------|----------|---------|------|
| 活動頁 | utk0201_.aspx | utk0201_.aspx | 無 |
| 場次選擇 | utk0203_.aspx | utk0203_.aspx | 無 |
| 票區選擇 | utk0204_.aspx | utk0204_.aspx | 無 |
| 座位選擇 | utk0205_.aspx | utk0205_.aspx | 無 |

---

## 2. DOM 結構分析

### 2.1 座位選擇器對比

| 元素 | KHAM 選擇器 | UDN 選擇器 | 狀態 |
|------|------------|-----------|------|
| 座位表 | `#TBL` | `#TBL` | 相同 |
| 可用座位 | `#TBL td.empty` | `#TBL td.empty` | 相同 |
| 已售座位 | `#TBL td.people` | `#TBL td.people` | 相同 |
| 舞台方向 | `.stageDirection` | `.stageDirection` | 相同 |
| 票種按鈕 | `button[onclick*="setType"]` | `button[onclick*="setType"]` | 相同 |
| 驗證碼輸入 | `input#CHK` | `input#CHK` | 相同 |
| 提交按鈕 | `button.sumitButton` | `button.sumitButton` | 相同 |

### 2.2 差異項目

| 功能 | KHAM | UDN | 處理方式 |
|------|------|-----|---------|
| 購買按鈕 | `button[onclick*="red"]` | `button[name="fastBuy"]` | 條件判斷 |
| 票數輸入 | 區域選擇頁面 | `input.yd_counterNum` | 已實作 |

### 2.3 座位 DOM 結構

```html
<!-- 座位表格 (UTK0205 頁面) -->
<table id="TBL">
  <tr>
    <!-- 可用座位 -->
    <td class="empty up" title="2樓黃2D區-3排-14號"></td>
    <!-- 已售座位 -->
    <td class="people up" title="2樓黃2D區-3排-15號"></td>
    <!-- 間隔 -->
    <td>&nbsp;</td>
  </tr>
</table>

<!-- 舞台方向指示 -->
<div class="stageDirection topright"></div>

<!-- 票種選擇按鈕 -->
<button class="green" onclick="setType('type_id','原價-NT$3,680')">
  原價-NT$3,680
</button>
```

### 2.4 座位標題格式

```
格式：{樓層}{區域}-{排數}-{座位號}
範例：2樓黃2D區-3排-14號
      1樓紅A區-H排-8號（字母排號）
```

---

## 3. 現有 KHAM 實作分析

### 3.1 座位選擇函數

| 函數名稱 | 行號 | 功能 |
|---------|------|------|
| `nodriver_kham_seat_type_auto_select()` | 18405-18767 | 票種選擇（全票、身障票等） |
| `nodriver_kham_seat_auto_select()` | 18770-19132 | 座位自動選擇（核心邏輯） |
| `nodriver_kham_seat_main()` | 19135-19360 | 座位選擇主流程 |

### 3.2 座位選擇演算法

**舞台方向智慧選座**：

```
Step 1: 偵測舞台方向
   ├─ topright/topleft → stageDirection = 'up'
   ├─ downright/downleft → stageDirection = 'down'
   └─ left/right → stageDirection = 'left'/'right'

Step 2: 座位分組
   ├─ up/down → 按排數分組 (GROUP BY ROW)
   └─ left/right → 按座位號分組 (GROUP BY SEAT NUMBER)

Step 3: 排品質評估（三層優先度）
   ├─ Priority 1: 是否有足夠連續座位
   ├─ Priority 2: 中間區域座位比例（25%-75%）
   └─ Priority 3: 舞台方向優先度

Step 4: 連續座位檢測
   └─ 使用 DOM 索引（非座位號）檢測連續性

Step 5: 座位選擇
   ├─ disable_adjacent_seat = false → 尋找連續座位
   └─ disable_adjacent_seat = true → 從中間選中央位置
```

### 3.3 關鍵程式碼片段

**連續座位檢測**：
```javascript
// 使用 DOM 索引檢測連續性（重要！不要用座位號）
const domGap = rowSeats[i + 1].domIndex - rowSeats[i].domIndex;
if (domGap === 1) {  // 相鄰
    currentContinuous++;
}
```

**座位解析**：
```javascript
const title = seat.getAttribute('title');
// 格式: "2樓黃2D區-3排-14號"
const parts = title.split('-');
const rowText = parts[1];  // "H排" or "17排"
const seatNum = parseInt(parts[2].replace('號', ''));

// 支援字母排號轉換 (A->1, B->2, ..., Z->26)
const letterMatch = rowText.match(/([A-Z]+)排/);
```

---

## 4. Feature 003 遞補機制

### 4.1 Early Return Pattern

```python
# 依優先級順序嘗試關鍵字，第一個成功即停止
for keyword_index, keyword_item_set in enumerate(keyword_array):
    if is_match:
        # Early Return - 立即停止
        break
```

### 4.2 Conditional Fallback

```python
# 條件回退機制
if not matched and date_auto_fallback:
    # 使用 auto_select_mode 選擇
    matched_blocks = formated_area_list
else:
    # 嚴格模式：等待手動介入
    return False
```

### 4.3 設定參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `date_auto_fallback` | `false` | 日期遞補開關（嚴格模式預設） |
| `area_auto_fallback` | `false` | 區域遞補開關（嚴格模式預設） |
| `auto_select_mode` | `from top to bottom` | 回退時的選擇模式 |

---

## 5. UDN 特有配置

### 5.1 settings.json 配置

```json
{
  "advanced": {
    "udn_account": "your_account",
    "udn_password": "your_password",  // 加密
    "udn_password_plaintext": ""      // 明文（優先使用）
  },
  "date_auto_select": {
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": false
  },
  "area_auto_select": {
    "area_keyword": "\"特A區\",\"特B區\"",
    "area_auto_fallback": false
  },
  "keyword_exclude": "\"輪椅\",\"身障\""
}
```

---

## 6. 技術決策

### 6.1 決策：複用 KHAM 座位選擇邏輯

**選擇**：在 `nodriver_kham_main()` 中新增 UDN 網域判斷，直接呼叫現有座位選擇函數。

**理由**：
1. DOM 結構完全相同，選擇器可直接複用
2. 座位選擇演算法已經過驗證
3. 維護成本最低，符合 DRY 原則
4. 符合憲法第 III 條「三問法則」- 這是最簡單的方法

**考慮的替代方案**：
- ❌ 新建獨立的 UDN 座位選擇函數：程式碼重複，維護成本高
- ❌ 抽象化通用座位選擇介面：過度工程，目前只有 KHAM 家族使用

### 6.2 決策：整合 Feature 003 遞補機制

**選擇**：修改現有 `nodriver_kham_date_auto_select()` 和 `nodriver_kham_area_auto_select()` 函數，新增遞補邏輯。

**理由**：
1. 符合專案統一的選擇邏輯標準
2. 支援嚴格模式（預設）避免誤購
3. 支援智能遞補增加購票成功率

---

## 7. 風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|---------|
| UDN DOM 結構變更 | 低 | 共用 KHAM 後端，變更機率低 |
| reCaptcha 阻擋 | 中 | 暫不處理，明確標記為範圍外 |
| 座位狀態競爭 | 中 | 選座失敗時自動重試其他座位 |
| 網路延遲 | 低 | 設定適當 timeout 與重試機制 |

---

## 8. 參考資料

### 程式碼位置

| 檔案 | 行號 | 說明 |
|------|------|------|
| `src/nodriver_tixcraft.py` | 18405-19360 | KHAM 座位選擇完整實作 |
| `src/nodriver_tixcraft.py` | 17580-17613 | UDN 票券選擇流程 |
| `src/nodriver_tixcraft.py` | 16154-16187 | 購買按鈕點擊（UDN/KHAM 通用） |

### 文件參考

- `docs/03-mechanisms/04-date-selection.md` - 日期選擇機制
- `docs/03-mechanisms/05-area-selection.md` - 區域選擇機制
- `docs/02-development/ticket_seat_selection_algorithm.md` - 座位選擇演算法
- `docs/02-development/structure.md` - 程式碼結構索引
