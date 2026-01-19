# 快速開始：UDN 售票網自動搶票

**分支**：`010-udn-seat-select` | **日期**：2025-12-17

## 概述

本指南說明如何使用 UDN 售票網自動搶票功能，包含座位自動選擇和遞補機制。

---

## 前置需求

1. Python 3.10+
2. NoDriver 已安裝
3. Chrome 瀏覽器 90+
4. 已設定 `settings.json`

---

## 快速設定

### 1. 基本設定

編輯 `src/settings.json`：

```json
{
  "homepage": "https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=YOUR_PRODUCT_ID",
  "webdriver_type": "nodriver",
  "ticket_number": 2
}
```

### 2. 日期選擇設定

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": false
  }
}
```

**關鍵字說明**：
- OR 邏輯：`"\"12/25\",\"12/26\""`（任一匹配）
- AND 邏輯：`"\"12/25 週六\""`（必須同時包含 12/25 和 週六）

**遞補開關**：
- `false`（預設）：關鍵字失敗時等待手動選擇
- `true`：關鍵字失敗時自動選擇第一個可用場次

### 3. 區域選擇設定

```json
{
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"特A區\",\"特B區\"",
    "area_auto_fallback": true
  },
  "keyword_exclude": "\"輪椅\",\"身障\""
}
```

**排除關鍵字**：自動跳過包含指定關鍵字的區域

---

## 執行

### 快速測試

```bash
cd tickets_hunter
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

### 檢查輸出

```bash
# 檢查日期選擇日誌
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇日誌
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 檢查座位選擇日誌
grep "\[UDN SEAT\]\|\[SUCCESS\]" .temp/test_output.txt
```

---

## 使用場景

### 場景 1：嚴格模式（推薦）

只購買指定場次和區域，失敗時等待手動介入。

```json
{
  "date_auto_select": {
    "date_keyword": "\"12/25\"",
    "date_auto_fallback": false
  },
  "area_auto_select": {
    "area_keyword": "\"特A區\"",
    "area_auto_fallback": false
  }
}
```

### 場景 2：彈性模式

指定優先場次，失敗時自動選擇其他可用場次。

```json
{
  "date_auto_select": {
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": true
  },
  "area_auto_select": {
    "area_keyword": "\"特A區\",\"特B區\",\"特C區\"",
    "area_auto_fallback": true
  }
}
```

### 場景 3：只要買到票就好

不指定關鍵字，直接選擇第一個可用選項。

```json
{
  "date_auto_select": {
    "date_keyword": "",
    "date_auto_fallback": true
  },
  "area_auto_select": {
    "area_keyword": "",
    "area_auto_fallback": true
  },
  "auto_select_mode": "from top to bottom"
}
```

---

## 購票流程

```
1. 活動頁面 (UTK0201)
   └─ 點擊「立即購票」

2. 場次選擇 (UTK0203)
   └─ 日期關鍵字匹配
   └─ 若失敗且 date_auto_fallback=true → 自動遞補
   └─ 點擊「前往購票」

3. 票區選擇 (UTK0204)
   └─ 區域關鍵字匹配（排除 keyword_exclude）
   └─ 若失敗且 area_auto_fallback=true → 自動遞補
   └─ 點擊票區列

4. 座位選擇 (UTK0205 彈出視窗)
   └─ 自動選擇座位（連續座位優先）
   └─ 加入購物車

5. 購物車
   └─ 完成！
```

---

## 除錯

### 啟用詳細日誌

```json
{
  "advanced": {
    "verbose": true
  }
}
```

### 常見問題

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| 日期選擇失敗 | 關鍵字不匹配 | 檢查關鍵字格式，啟用 `date_auto_fallback` |
| 區域選擇失敗 | 票區售完或被排除 | 新增更多關鍵字，啟用 `area_auto_fallback` |
| 座位選擇失敗 | 無可用連續座位 | 減少 `ticket_number` 或啟用非連續座位 |

### MCP 即時除錯

```bash
/mcpstart
```

使用 MCP 工具即時觀察頁面狀態：
- `mcp__chrome-devtools__take_snapshot` - 擷取 DOM
- `mcp__chrome-devtools__list_network_requests` - 檢查 API
- `mcp__chrome-devtools__evaluate_script` - 執行 JavaScript

---

## 注意事項

1. **reCaptcha**：UDN 使用 reCaptcha，目前無法自動處理
2. **帳號登入**：請先手動登入 UDN 或設定帳密自動登入
3. **票數限制**：單筆訂單通常有上限，請確認 `ticket_number` 設定合理
4. **網路環境**：建議使用穩定網路，避免 timeout

---

## 參考文件

- [功能規格](./spec.md)
- [實作計畫](./plan.md)
- [資料模型](./data-model.md)
- [函數介面](./contracts/udn-seat-interface.md)
- [設定 Schema](./contracts/settings-schema.md)
