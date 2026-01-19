# 設定 Schema：UDN 座位選擇

**分支**：`010-udn-seat-select` | **日期**：2025-12-17

## 概述

定義 UDN 座位選擇功能相關的 settings.json 配置項目。

---

## 新增設定項目

### 1. date_auto_fallback

**位置**：`date_auto_select.date_auto_fallback`

```json
{
  "date_auto_select": {
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": false
  }
}
```

| 屬性 | 值 |
|------|-----|
| 類型 | boolean |
| 預設值 | `false` |
| 說明 | 日期關鍵字全部失敗時的遞補開關 |

**行為**：
- `false`（嚴格模式）：關鍵字失敗時不自動選擇，等待手動介入
- `true`（遞補模式）：關鍵字失敗時，使用 `auto_select_mode` 自動選擇

---

### 2. area_auto_fallback

**位置**：`area_auto_select.area_auto_fallback`

```json
{
  "area_auto_select": {
    "area_keyword": "\"特A區\",\"特B區\"",
    "area_auto_fallback": false
  }
}
```

| 屬性 | 值 |
|------|-----|
| 類型 | boolean |
| 預設值 | `false` |
| 說明 | 區域關鍵字全部失敗時的遞補開關 |

**行為**：
- `false`（嚴格模式）：關鍵字失敗時不自動選擇，等待手動介入
- `true`（遞補模式）：關鍵字失敗時，使用 `auto_select_mode` 自動選擇

---

## 現有設定項目（參考）

### date_auto_select

**位置**：`date_auto_select`

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": false,
    "mode": "from top to bottom"
  }
}
```

| 子項目 | 類型 | 預設值 | 說明 |
|--------|------|--------|------|
| `enable` | boolean | `true` | 啟用日期自動選擇 |
| `date_keyword` | string | `""` | 日期關鍵字（OR: 逗號分隔，AND: 空格分隔） |
| `date_auto_fallback` | boolean | `false` | 遞補開關（新增） |
| `mode` | string | `"from top to bottom"` | 選擇模式 |

---

### area_auto_select

**位置**：`area_auto_select`

```json
{
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"特A區\",\"特B區\"",
    "area_auto_fallback": false,
    "mode": "from top to bottom"
  }
}
```

| 子項目 | 類型 | 預設值 | 說明 |
|--------|------|--------|------|
| `enable` | boolean | `true` | 啟用區域自動選擇 |
| `area_keyword` | string | `""` | 區域關鍵字（OR: 逗號分隔，AND: 空格分隔） |
| `area_auto_fallback` | boolean | `false` | 遞補開關（新增） |
| `mode` | string | `"from top to bottom"` | 選擇模式 |

---

### keyword_exclude

**位置**：`keyword_exclude`

```json
{
  "keyword_exclude": "\"輪椅\",\"身障\",\"身心\",\"障礙\",\"Restricted View\""
}
```

| 屬性 | 值 |
|------|-----|
| 類型 | string |
| 預設值 | `""` |
| 說明 | 排除關鍵字，符合的選項將被過濾 |

**用途**：
- 過濾輪椅區、身障區
- 過濾視線受限區域（Restricted View）
- 在關鍵字匹配前執行

---

### auto_select_mode

**位置**：`ticket_number` 同層級或 `date_auto_select.mode`

```json
{
  "auto_select_mode": "from top to bottom"
}
```

| 值 | 說明 |
|-----|------|
| `"from top to bottom"` | 從第一個開始選擇 |
| `"from bottom to top"` | 從最後一個開始選擇 |
| `"center"` | 從中間開始選擇 |
| `"random"` | 隨機選擇 |

---

### ticket_number

**位置**：`ticket_number`

```json
{
  "ticket_number": 2
}
```

| 屬性 | 值 |
|------|-----|
| 類型 | integer |
| 預設值 | `2` |
| 範圍 | 1-10 |
| 說明 | 購票數量 |

---

### UDN 帳號設定

**位置**：`advanced`

```json
{
  "advanced": {
    "udn_account": "your_account",
    "udn_password": "encrypted_password",
    "udn_password_plaintext": ""
  }
}
```

| 子項目 | 類型 | 說明 |
|--------|------|------|
| `udn_account` | string | UDN 帳號 |
| `udn_password` | string | UDN 密碼（加密） |
| `udn_password_plaintext` | string | UDN 密碼（明文，優先使用） |

---

## 完整設定範例

```json
{
  "homepage": "https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P12YQQ5C",
  "webdriver_type": "nodriver",
  "ticket_number": 2,
  "auto_select_mode": "from top to bottom",

  "date_auto_select": {
    "enable": true,
    "date_keyword": "\"12/25\",\"12/26\"",
    "date_auto_fallback": false
  },

  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"特A區\",\"特B區\",\"特C區\"",
    "area_auto_fallback": true
  },

  "keyword_exclude": "\"輪椅\",\"身障\",\"Restricted View\"",

  "pass_date_is_sold_out": true,

  "advanced": {
    "udn_account": "your_account",
    "udn_password_plaintext": "your_password",
    "verbose": true
  }
}
```

---

## 驗證規則

### JSON Schema（簡化版）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "date_auto_select": {
      "type": "object",
      "properties": {
        "enable": { "type": "boolean", "default": true },
        "date_keyword": { "type": "string", "default": "" },
        "date_auto_fallback": { "type": "boolean", "default": false }
      }
    },
    "area_auto_select": {
      "type": "object",
      "properties": {
        "enable": { "type": "boolean", "default": true },
        "area_keyword": { "type": "string", "default": "" },
        "area_auto_fallback": { "type": "boolean", "default": false }
      }
    },
    "keyword_exclude": { "type": "string", "default": "" },
    "ticket_number": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "default": 2
    },
    "auto_select_mode": {
      "type": "string",
      "enum": ["from top to bottom", "from bottom to top", "center", "random"],
      "default": "from top to bottom"
    }
  }
}
```

---

## 遷移指南

### 從舊版本升級

如果現有 settings.json 沒有 `date_auto_fallback` 和 `area_auto_fallback` 設定：

1. 系統將自動使用預設值 `false`（嚴格模式）
2. 無需手動修改，行為與舊版本相同
3. 若需啟用遞補功能，手動新增設定項目

### 新增設定項目

在 `date_auto_select` 區塊新增：
```json
"date_auto_fallback": true
```

在 `area_auto_select` 區塊新增：
```json
"area_auto_fallback": true
```
