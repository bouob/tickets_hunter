# 快速開始：關鍵字分隔符號新格式

**功能**：002-keyword-delimiter-fix
**版本**：2.0.0
**更新日期**：2025-10-28

## 概述

本指南說明如何使用新的關鍵字分隔符號格式（分號 `;`），以及如何從舊格式（逗號 `,`）遷移。

---

## 快速開始

### 1. 檢查當前設定

開啟 `src/settings.json`，檢查以下欄位：

```json
{
  "date_auto_select": {
    "date_keyword": "..."
  },
  "area_auto_select": {
    "area_keyword": "..."
  },
  "keyword_exclude": "...",
  "advanced": {
    "idle_keyword": "...",
    "resume_keyword": "...",
    "idle_keyword_second": "...",
    "resume_keyword_second": "..."
  }
}
```

### 2. 更新為新格式

**舊格式（逗號）**：
```json
{
  "date_keyword": "10/03,10/05,10/07",
  "area_keyword": "3,280,2,680,1,980"
}
```

**新格式（分號）**：
```json
{
  "date_keyword": "10/03;10/05;10/07",
  "area_keyword": "3,280;2,680;1,980"
}
```

### 3. 執行程式

```bash
python src/nodriver_tixcraft.py --input src/settings.json
```

### 4. 檢查日誌

若使用舊格式，會看到警告訊息：
```
[WARNING] 偵測到舊格式的關鍵字設定
[WARNING] 當前設定: "10/03,10/05"
[WARNING] 建議格式: "10/03;10/05"
```

---

## 使用範例

### 範例 1：TicketPlus 票價選擇

**場景**：TicketPlus 遠大售票，選擇「NT$ 3,280」或「NT$ 2,680」票價。

**設定**：
```json
{
  "homepage": "https://ticketplus.com.tw/activity/077604571cf54a0abfd1541fed0eaa05",
  "webdriver_type": "nodriver",
  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "area_keyword": "3,280;2,680"
  }
}
```

**說明**：
- 關鍵字 `"3,280"` 和 `"2,680"` 包含逗號（金額格式）
- 使用分號 `;` 分隔兩個關鍵字
- 系統依序嘗試匹配「3,280」→「2,680」

**日誌輸出**：
```
[AREA KEYWORD] Trying to match: 3,280
[AREA SELECT] Selected area: NT$ 3,280
```

---

### 範例 2：TixCraft 日期選擇

**場景**：TixCraft 拓元售票，選擇「2025/10/03」或「2025/10/05」場次。

**設定**：
```json
{
  "homepage": "https://tixcraft.com/activity/detail/24_taipeiarena",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "date_keyword": "10/03;10/05"
  }
}
```

**說明**：
- 使用分號 `;` 分隔兩個日期關鍵字
- 系統依序嘗試匹配「10/03」→「10/05」

**日誌輸出**：
```
[DATE KEYWORD] Trying to match: 10/03
[DATE SELECT] Selected date: 2025/10/03
```

---

### 範例 3：排除關鍵字

**場景**：排除「輪椅」、「身障」、「視線受阻」座位區。

**設定**：
```json
{
  "keyword_exclude": "輪椅;身障;視線受阻"
}
```

**說明**：
- 使用分號 `;` 分隔多個排除關鍵字
- 系統自動過濾包含這些關鍵字的區域

---

### 範例 4：時間控制關鍵字

**場景**：在特定時間暫停/恢復系統（例如：午休時間暫停）。

**設定**：
```json
{
  "advanced": {
    "idle_keyword": "12:00:00;13:00:00",
    "resume_keyword": "12:00:05;13:00:05"
  }
}
```

**說明**：
- `idle_keyword`：在 12:00:00 或 13:00:00 暫停系統
- `resume_keyword`：在 12:00:05 或 13:00:05 恢復系統
- 使用分號 `;` 分隔多個時間點

---

### 範例 5：JSON 陣列格式（進階）

**場景**：使用 JSON 陣列格式（更明確但輸入複雜）。

**設定**：
```json
{
  "date_keyword": ["10/03", "10/05", "10/07"],
  "area_keyword": ["3,280", "2,680", "1,980"],
  "keyword_exclude": ["輪椅", "身障", "視線受阻"]
}
```

**說明**：
- JSON 陣列格式明確無歧義
- 適合包含特殊字元的關鍵字
- 不推薦給一般使用者（輸入複雜）

---

## 遷移指南

### 自動遷移（推薦）

**步驟 1**：使用文字編輯器開啟 `settings.json`

**步驟 2**：使用「尋找與取代」功能

**尋找**：`"date_keyword": "([^"]+),([^"]+)"`（正則表達式）
**取代**：`"date_keyword": "\1;\2"`

**步驟 3**：重複步驟 2，替換所有關鍵字欄位

**步驟 4**：儲存檔案

### 手動遷移

**步驟 1**：開啟 `settings.json`

**步驟 2**：找到關鍵字欄位

**步驟 3**：將逗號 `,` 替換為分號 `;`

**步驟 4**：儲存檔案

**範例**：
```json
// Before
"area_keyword": "3,280,2,680"

// After
"area_keyword": "3,280;2,680"
```

---

## 疑難排解

### Q1：為什麼要改用分號？

**A1**：逗號與金額千位分隔符號衝突。例如：
- 舊格式：`"3,280,2,680"` 被錯誤分割為 `["3", "280", "2", "680"]`
- 新格式：`"3,280;2,680"` 正確分割為 `["3,280", "2,680"]`

---

### Q2：我的舊設定還能用嗎？

**A2**：可以，但會顯示警告訊息。建議儘快更新為新格式以避免金額關鍵字匹配錯誤。

---

### Q3：如何驗證新格式是否生效？

**A3**：執行程式並檢查日誌輸出：

```bash
# 執行測試
python src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1

# 檢查關鍵字匹配
grep "\[DATE KEYWORD\]\|\[AREA KEYWORD\]" .temp/test_output.txt
```

---

### Q4：什麼時候應該使用 JSON 陣列格式？

**A4**：當關鍵字包含特殊字元（如分號 `;`）時：

```json
{
  "area_keyword": ["A區;特別座", "B區;特別座"]
}
```

---

### Q5：我不小心混用了逗號和分號會怎樣？

**A5**：系統優先使用分號分割：

```json
// 混用格式（不推薦）
"area_keyword": "3,280;2,680,1,980"

// 解析結果
["3,280", "2,680,1,980"]  // "2,680,1,980" 視為單一關鍵字
```

**建議**：統一使用分號 `;`。

---

## 最佳實踐

### 1. 關鍵字命名

✅ **推薦**：
```json
{
  "area_keyword": "3,280;2,680",          // 金額格式
  "date_keyword": "10/03;10/05",          // 日期格式
  "keyword_exclude": "輪椅;身障;視線受阻"  // 排除關鍵字
}
```

❌ **不推薦**：
```json
{
  "area_keyword": "A;B;C",  // 太模糊
  "date_keyword": "1;2;3"   // 無法識別
}
```

### 2. 關鍵字順序

- 優先順序：從左到右
- 建議：將最想要的關鍵字放在最前面

```json
{
  "area_keyword": "VIP區;A區;B區"  // 優先嘗試 VIP區
}
```

### 3. 空白處理

- 系統自動去除前後空白
- 可讀性優先

```json
{
  "area_keyword": "3,280; 2,680; 1,980"  // 可讀性高
}
```

---

## 完整設定範例

### TicketPlus 遠大售票

```json
{
  "homepage": "https://ticketplus.com.tw/activity/077604571cf54a0abfd1541fed0eaa05",
  "browser": "chrome",
  "language": "繁體中文",
  "ticket_number": 2,
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/03;10/05",
    "mode": "from top to bottom"
  },
  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "area_keyword": "3,280;2,680"
  },
  "keyword_exclude": "輪椅;身障;視線受阻",
  "advanced": {
    "verbose": true,
    "auto_reload_page_interval": 5.0
  }
}
```

### TixCraft 拓元售票

```json
{
  "homepage": "https://tixcraft.com/activity/detail/24_taipeiarena",
  "browser": "chrome",
  "language": "繁體中文",
  "ticket_number": 2,
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/03;10/05;10/07",
    "mode": "from top to bottom"
  },
  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom",
    "area_keyword": "搖滾A區;搖滾B區"
  },
  "keyword_exclude": "輪椅;身障",
  "tixcraft": {
    "pass_date_is_sold_out": true,
    "auto_reload_coming_soon_page": true
  },
  "advanced": {
    "verbose": true,
    "tixcraft_sid": "",
    "auto_reload_page_interval": 3.0
  }
}
```

---

## 進階配置

### 時間控制（暫停/恢復）

```json
{
  "advanced": {
    "idle_keyword": "12:00:00;18:00:00",
    "resume_keyword": "13:00:00;19:00:00",
    "idle_keyword_second": "23:00:00",
    "resume_keyword_second": "08:00:00"
  }
}
```

**說明**：
- 在 12:00:00 或 18:00:00 暫停系統
- 在 13:00:00 或 19:00:00 恢復系統
- 在 23:00:00 暫停（隔夜）
- 在 08:00:00 恢復（隔天早上）

---

## 相關資源

- **Issue**：[GitHub Issue #23](https://github.com/max32002/tixcraft_bot/issues/23)
- **API 契約**：`specs/002-keyword-delimiter-fix/contracts/keyword-format.md`
- **規格文件**：`specs/002-keyword-delimiter-fix/spec.md`
- **CHANGELOG**：`CHANGELOG.md`（查看版本變更記錄）
- **設定範本**：`src/settings.json`

---

## 支援

若遇到問題，請：
1. 檢查 `verbose` 是否設為 `true`（啟用詳細日誌）
2. 查看 `.temp/test_output.txt` 的日誌輸出
3. 在 GitHub Issues 提問並附上設定檔與日誌

---

**版本**：2.0.0 | **更新日期**：2025-10-28 | **作者**：Tickets Hunter Team
