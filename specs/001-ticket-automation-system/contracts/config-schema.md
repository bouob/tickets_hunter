# 配置 Schema 契約

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：定義 settings.json 的完整 JSON Schema 和配置規範。

---

## 概述

本文件定義 `settings.json` 配置檔案的完整 schema，包括所有欄位的型別、預設值、驗證規則和範例。這個 schema 可用於：

- **配置驗證**：自動驗證用戶配置的正確性
- **IDE 支援**：提供自動完成和錯誤提示
- **文件參考**：作為配置欄位的權威文件

**未來計劃**：
- 實作 JSON Schema 驗證（SC-009）
- 生成 TypeScript 型別定義
- 創建互動式配置編輯器

---

## 完整 JSON Schema

### Schema 版本 1.0

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Tickets Hunter Configuration",
  "description": "多平台自動化搶票系統的配置 schema",
  "type": "object",
  "required": ["homepage", "ticket_number"],
  "properties": {
    "homepage": {
      "type": "string",
      "format": "uri",
      "description": "活動頁面的完整 URL",
      "examples": [
        "https://tixcraft.com/activity/detail/23_event",
        "https://kktix.com/events/concert-2023"
      ]
    },
    "webdriver_type": {
      "type": "string",
      "enum": ["nodriver", "uc", "selenium"],
      "default": "nodriver",
      "description": "使用的 WebDriver 類型"
    },
    "ticket_number": {
      "type": "integer",
      "minimum": 1,
      "maximum": 6,
      "default": 2,
      "description": "購票數量"
    },
    "date_auto_select": {
      "type": "object",
      "description": "日期自動選擇設定",
      "properties": {
        "enable": {
          "type": "boolean",
          "default": true,
          "description": "總開關：是否啟用自動日期選擇。當為 false 時，完全停用自動日期選擇，所有關鍵字和模式設定都會被忽略，讓使用者手動選擇日期"
        },
        "date_keyword": {
          "type": "string",
          "default": "",
          "description": "日期關鍵字，多個關鍵字用分號分隔",
          "examples": ["10/15", "10/15;10/16", "2025/10/15"]
        },
        "mode": {
          "type": "string",
          "enum": ["from top to bottom", "from bottom to top", "center", "random"],
          "default": "from top to bottom",
          "description": "當關鍵字無匹配時的回退模式。如果未設定且關鍵字沒有匹配，系統將停止選擇並等待手動介入"
        }
      }
    },
    "area_auto_select": {
      "type": "object",
      "description": "區域/座位自動選擇設定",
      "properties": {
        "enable": {
          "type": "boolean",
          "default": true,
          "description": "總開關：是否啟用自動區域選擇。當為 false 時，完全停用自動區域選擇，所有關鍵字和模式設定都會被忽略，讓使用者手動選擇區域"
        },
        "area_keyword": {
          "type": "string",
          "default": "",
          "description": "區域關鍵字，多個關鍵字用分號分隔",
          "examples": ["VIP區", "VIP;搖滾區A", "1F"]
        },
        "mode": {
          "type": "string",
          "enum": ["from top to bottom", "from bottom to top", "center", "random"],
          "default": "from top to bottom",
          "description": "當關鍵字無匹配時的回退模式。如果未設定且關鍵字沒有匹配，系統將停止選擇並等待手動介入"
        }
      }
    },
    "seat_auto_select": {
      "type": "object",
      "description": "座位圖自動選擇設定（僅部分平台）",
      "properties": {
        "enable": {
          "type": "boolean",
          "default": true,
          "description": "是否啟用自動座位選擇"
        },
        "select_mode": {
          "type": "string",
          "enum": ["random", "from top to bottom"],
          "default": "random",
          "description": "座位選擇模式"
        },
        "adjacent_seat": {
          "type": "boolean",
          "default": true,
          "description": "是否要求相鄰座位（ibon 專用）"
        }
      }
    },
    "ticket_form_data": {
      "type": "object",
      "description": "購票人資訊",
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1,
          "description": "購票人姓名",
          "examples": ["王大明", "John Doe"]
        },
        "email": {
          "type": "string",
          "format": "email",
          "description": "電子郵件地址",
          "examples": ["user@example.com"]
        },
        "phone": {
          "type": "string",
          "pattern": "^[0-9]{10}$",
          "description": "手機號碼（10 碼）",
          "examples": ["0912345678"]
        },
        "address": {
          "type": "string",
          "description": "地址（部分平台需要）",
          "examples": ["台北市信義區市府路1號"]
        }
      }
    },
    "ocr_captcha": {
      "type": "object",
      "description": "驗證碼 OCR 設定",
      "properties": {
        "enable": {
          "type": "boolean",
          "default": true,
          "description": "是否啟用自動 OCR 辨識"
        },
        "beta": {
          "type": "boolean",
          "default": false,
          "description": "是否使用 beta 模型（較慢但更準確）"
        },
        "force_submit": {
          "type": "boolean",
          "default": true,
          "description": "OCR 失敗時是否仍然送出表單"
        },
        "retry": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10,
          "default": 3,
          "description": "OCR 重試次數"
        }
      }
    },
    "advanced": {
      "type": "object",
      "description": "進階設定",
      "properties": {
        "verbose": {
          "type": "boolean",
          "default": true,
          "description": "啟用詳細除錯模式。當為 true 時，系統會記錄所有錯誤的詳細資訊，包括堆疊追蹤、元素查找失敗原因等，用於除錯和問題診斷"
        },
        "headless": {
          "type": "boolean",
          "default": false,
          "description": "是否使用無頭模式（不顯示瀏覽器視窗）"
        },
        "auto_reload_page_interval": {
          "type": "number",
          "minimum": 0.1,
          "default": 1.5,
          "description": "頁面自動重載間隔（秒）。用於等待票券開賣和售罄時的持續重試，系統會根據此間隔持續刷新頁面直到票券可用"
        },
        "auto_reload_overheat_count": {
          "type": "integer",
          "minimum": 1,
          "default": 10,
          "description": "過熱保護：連續重載次數閾值"
        },
        "auto_reload_overheat_cd": {
          "type": "number",
          "minimum": 1,
          "default": 60,
          "description": "過熱保護：觸發後的冷卻時間（秒）"
        },
        "tixcraft_sid": {
          "type": "string",
          "default": "",
          "description": "TixCraft session cookie",
          "examples": ["abc123def456"]
        },
        "kktix_account": {
          "type": "string",
          "format": "email",
          "default": "",
          "description": "KKTIX 帳號（Email）"
        },
        "kktix_password": {
          "type": "string",
          "default": "",
          "description": "KKTIX 密碼"
        },
        "ibon_ibonqware": {
          "type": "string",
          "default": "",
          "description": "ibon session cookie"
        },
        "kham_tk": {
          "type": "string",
          "default": "",
          "description": "KHAM session cookie"
        }
      }
    },
    "browser_args": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "default": [],
      "description": "Chrome 瀏覽器命令列參數",
      "examples": [
        ["--disable-blink-features=AutomationControlled"],
        ["--user-agent=Mozilla/5.0..."]
      ]
    },
    "payment": {
      "type": "object",
      "description": "付款設定（保留欄位，未實作）",
      "properties": {
        "method": {
          "type": "string",
          "enum": ["credit_card", "convenience_store", "atm"],
          "description": "付款方式"
        },
        "auto_pay": {
          "type": "boolean",
          "default": false,
          "description": "是否自動付款（未實作）"
        }
      }
    }
  }
}
```

---

## 欄位詳細說明

### 1. 基本設定

#### homepage

**型別**：`string` (URI)
**必需**：✅ 是
**描述**：活動頁面的完整 URL，系統將從此 URL 開始自動化流程。

**支援的平台**：
- TixCraft：`https://tixcraft.com/activity/detail/{event_id}`
- KKTIX：`https://kktix.com/events/{event_name}`
- TicketPlus：`https://ticketplus.com.tw/activity/{event_id}`
- ibon：`https://ticket.ibon.com.tw/ActivityInfo/Details/{event_id}`
- KHAM：`https://kham.com.tw/application/UTK01/UTK0101_.aspx?PRODUCT_ID={event_id}`

**範例**：
```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_taylorswift"
}
```

**驗證規則**：
- 必須是有效的 URL
- 必須使用 HTTPS 協定
- 必須包含支援的平台域名

---

#### webdriver_type

**型別**：`string` (enum)
**必需**：❌ 否
**預設值**：`"nodriver"`
**可選值**：`"nodriver"` | `"uc"` | `"selenium"`

**描述**：選擇使用的 WebDriver 技術。

**選項說明**：
- **nodriver**（推薦）：
  - 最佳反偵測能力
  - 需要 Python 3.9+
  - 非同步架構，效能最佳
  - 記憶體占用最低

- **uc**（undetected-chromedriver）：
  - 良好的反偵測能力
  - 支援 Python 3.7+
  - 同步架構
  - 適合舊系統

- **selenium**（不推薦）：
  - 容易被偵測
  - 僅用於測試和教學

**範例**：
```json
{
  "webdriver_type": "nodriver"
}
```

---

#### ticket_number

**型別**：`integer`
**必需**：✅ 是
**最小值**：1
**最大值**：6
**預設值**：2

**描述**：購票數量。大多數平台限制單次購票 1-6 張。

**平台限制**：
- TixCraft：1-6 張
- KKTIX：1-10 張（但建議 1-6）
- iBon：1-4 張
- KHAM：1-6 張

**範例**：
```json
{
  "ticket_number": 2
}
```

---

### 2. 日期選擇設定

#### date_auto_select

**型別**：`object`
**必需**：❌ 否

**子欄位**：

##### date_auto_select.enable

**型別**：`boolean`
**預設值**：`true`
**描述**：是否啟用自動日期選擇。如果停用，將暫停並等待用戶手動選擇。

##### date_auto_select.date_keyword

**型別**：`string`
**預設值**：`""`
**描述**：日期關鍵字，用於匹配場次日期。支援多個關鍵字（分號分隔），按順序嘗試匹配。

**匹配邏輯**：
- 精確匹配（輸入什麼就匹配什麼）
- 嘗試所有關鍵字，直到找到匹配
- 如果無匹配，回退到 `mode` 選擇

**關鍵字格式建議**：
- 簡短格式：`"10/15"`
- 完整格式：`"2025/10/15"`
- 包含星期：`"10/15 (日)"`
- 多個關鍵字：`"10/15;10/16;10/17"`

**範例**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/15,10/16"
  }
}
```

##### date_auto_select.mode

**型別**：`string` (enum)
**預設值**：`"from top to bottom"`
**可選值**：
- `"from top to bottom"`：選擇第一個可用日期
- `"from bottom to top"`：選擇最後一個可用日期
- `"center"`：選擇中間的日期
- `"random"`：隨機選擇

**描述**：當 `date_keyword` 無匹配時的回退模式（三層回退的第 2 層）。

---

### 3. 區域/座位選擇設定

#### area_auto_select

**型別**：`object`
**必需**：❌ 否

**子欄位**：

##### area_auto_select.enable

**型別**：`boolean`
**預設值**：`true`

##### area_auto_select.area_keyword

**型別**：`string`
**預設值**：`""`
**描述**：區域關鍵字，用於匹配票區。

**常見關鍵字**：
- `"VIP"` 或 `"VIP區"`
- `"搖滾區"` 或 `"搖滾區A"`
- `"1F"` 或 `"一樓"`
- `"$3000"`（按價格匹配）

**多關鍵字範例**：
```json
{
  "area_auto_select": {
    "area_keyword": "VIP區,搖滾區A,搖滾區B"
  }
}
```

##### area_auto_select.mode

**型別**：`string` (enum)
**預設值**：`"from top to bottom"`
**可選值**：同 `date_auto_select.mode`

---

#### seat_auto_select

**型別**：`object`
**必需**：❌ 否
**適用平台**：僅有座位圖的平台（ibon、部分 TixCraft 活動）

**子欄位**：

##### seat_auto_select.enable

**型別**：`boolean`
**預設值**：`true`

##### seat_auto_select.select_mode

**型別**：`string` (enum)
**預設值**：`"random"`
**可選值**：
- `"random"`：隨機選擇可用座位
- `"from top to bottom"`：從上方開始選擇

##### seat_auto_select.adjacent_seat

**型別**：`boolean`
**預設值**：`true`
**描述**：是否要求選擇相鄰座位（ibon 專用功能）。

**ibon 特殊行為**：
- `true`：勾選「相鄰座位」選項，確保選到的座位相連
- `false`：不勾選，允許分散座位

---

### 4. 購票人資訊

#### ticket_form_data

**型別**：`object`
**必需**：❌ 否（但強烈建議填寫）

**子欄位**：

##### ticket_form_data.name

**型別**：`string`
**最小長度**：1
**描述**：購票人姓名（中文或英文）。

**範例**：
```json
{
  "ticket_form_data": {
    "name": "王大明"
  }
}
```

##### ticket_form_data.email

**型別**：`string` (email)
**描述**：電子郵件地址，用於接收訂單確認信。

**驗證**：必須符合 Email 格式（`user@domain.com`）

##### ticket_form_data.phone

**型別**：`string`
**格式**：10 碼數字
**描述**：台灣手機號碼。

**範例**：`"0912345678"`

**驗證規則**：
- 必須是 10 碼
- 僅包含數字
- 通常以 09 開頭

##### ticket_form_data.address

**型別**：`string`
**描述**：地址（部分平台需要，如實體票配送）。

---

### 5. 驗證碼設定

#### ocr_captcha

**型別**：`object`
**必需**：❌ 否

**子欄位**：

##### ocr_captcha.enable

**型別**：`boolean`
**預設值**：`true`
**描述**：是否啟用自動 OCR 辨識。

**停用情境**：
- 平台無驗證碼（TicketPlus、ibon）
- 用戶想手動輸入驗證碼

##### ocr_captcha.beta

**型別**：`boolean`
**預設值**：`false`
**描述**：是否使用 ddddocr 的 beta 模型。

**模型比較**：
| 模型 | 速度 | 準確度 | 建議使用 |
|------|------|--------|---------|
| 標準 | 快（~200ms） | 70% | 一般情況 |
| Beta | 慢（~500ms） | 80%+ | 重要活動、願意等待 |

##### ocr_captcha.force_submit

**型別**：`boolean`
**預設值**：`true`
**描述**：OCR 失敗時是否仍然送出表單。

**行為**：
- `true`：OCR 失敗後留空並送出（依賴運氣或平台容錯）
- `false`：OCR 失敗時停止流程，等待手動介入

**建議**：搶票場景建議設為 `true`，增加成功率。

##### ocr_captcha.retry

**型別**：`integer`
**最小值**：1
**最大值**：10
**預設值**：3
**描述**：OCR 重試次數。

**重試策略**：
- 每次重試重新截取驗證碼圖片
- 使用指數退避（第 1 次 0.5s、第 2 次 1s、第 3 次 2s）

---

### 6. 進階設定

#### advanced

**型別**：`object`
**必需**：❌ 否

**子欄位**：

##### advanced.verbose

**型別**：`boolean`
**預設值**：`true`
**描述**：是否顯示詳細日誌輸出。

**日誌範例**（`verbose=true`）：
```
[INIT] 正在初始化瀏覽器...
[AUTH] 注入 session cookie
[RELOAD] 正在重載頁面... (1/10)
[DATE] 找到 3 個可用日期
[DATE] 使用關鍵字 '10/15' 匹配到：2025/10/15 (日) 19:30
```

##### advanced.headless

**型別**：`boolean`
**預設值**：`false`
**描述**：是否使用無頭模式（不顯示瀏覽器視窗）。

**注意**：
- 無頭模式可能增加偵測風險
- 建議僅在伺服器環境使用
- NoDriver 的無頭模式偵測風險較低

##### advanced.auto_reload_page_interval

**型別**：`number`
**最小值**：0.1
**預設值**：1.5
**單位**：秒
**描述**：頁面自動重載的間隔時間。

**調整建議**：
- 熱門活動：0.5-1.0 秒（更頻繁）
- 一般活動：1.5-2.0 秒（預設）
- 避免過快（可能被偵測）

##### advanced.auto_reload_overheat_count

**型別**：`integer`
**最小值**：1
**預設值**：10
**描述**：觸發過熱保護的連續重載次數閾值。

**過熱保護機制**：
- 當連續重載達到此次數時，進入冷卻期
- 冷卻期間等待 `auto_reload_overheat_cd` 秒
- 重置計數器後繼續重載

**範例**：
- `overheat_count=10`，`interval=1.5`
- 連續重載 10 次（15 秒）後觸發冷卻

##### advanced.auto_reload_overheat_cd

**型別**：`number`
**最小值**：1
**預設值**：60
**單位**：秒
**描述**：過熱保護觸發後的冷卻時間。

---

##### 平台認證憑證

###### advanced.tixcraft_sid

**型別**：`string`
**預設值**：`""`
**描述**：TixCraft 的 session cookie 值。

**取得方式**：
1. 瀏覽器登入 TixCraft
2. 開啟開發者工具（F12）
3. Application → Cookies → `https://tixcraft.com`
4. 複製 `tixcraft_sid` 的值

**範例**：`"abc123def456ghi789"`

---

###### advanced.kktix_account

**型別**：`string` (email)
**預設值**：`""`
**描述**：KKTIX 帳號（Email 格式）。

###### advanced.kktix_password

**型別**：`string`
**預設值**：`""`
**描述**：KKTIX 密碼。

**安全注意**：
- 密碼明文儲存，請確保檔案權限正確
- 建議將 `settings.json` 加入 `.gitignore`
- 未來計劃支援加密儲存

---

###### advanced.ibon_ibonqware

**型別**：`string`
**預設值**：`""`
**描述**：ibon 的 session cookie 值。

**取得方式**：同 TixCraft，Cookie 名稱為 `ibonqware`。

---

###### advanced.kham_tk

**型別**：`string`
**預設值**：`""`
**描述**：KHAM 的 session cookie 值。

**取得方式**：Cookie 名稱為 `tk`。

---

#### browser_args

**型別**：`array` of `string`
**預設值**：`[]`
**描述**：Chrome 瀏覽器的命令列參數列表。

**常用參數**：
```json
{
  "browser_args": [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  ]
}
```

**參數說明**：
- `--disable-blink-features=AutomationControlled`：隱藏自動化標記
- `--disable-dev-shm-usage`：避免共享記憶體問題（Docker 環境）
- `--no-sandbox`：停用沙盒（某些環境需要）
- `--window-size=1920,1080`：設定視窗大小
- `--user-agent=...`：自定義 User-Agent

---

#### payment

**型別**：`object`
**必需**：❌ 否
**狀態**：⚠️ 保留欄位，未實作

**子欄位**：

##### payment.method

**型別**：`string` (enum)
**可選值**：
- `"credit_card"`：信用卡
- `"convenience_store"`：超商代碼
- `"atm"`：ATM 轉帳

##### payment.auto_pay

**型別**：`boolean`
**預設值**：`false`
**描述**：是否自動付款（未實作）。

**未來計劃**：
- 自動填寫信用卡資訊
- 自動點擊付款按鈕
- ⚠️ 安全風險較高，需謹慎設計

---

## 完整配置範例

### 範例 1：TixCraft 基本配置

```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_taylorswift",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/15,10/16",
    "mode": "from top to bottom"
  },

  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP區,搖滾區A",
    "mode": "from top to bottom"
  },

  "ticket_form_data": {
    "name": "王大明",
    "email": "user@example.com",
    "phone": "0912345678"
  },

  "ocr_captcha": {
    "enable": true,
    "beta": false,
    "force_submit": true,
    "retry": 3
  },

  "advanced": {
    "verbose": true,
    "headless": false,
    "auto_reload_page_interval": 1.5,
    "auto_reload_overheat_count": 10,
    "auto_reload_overheat_cd": 60,
    "tixcraft_sid": "your_session_cookie_here"
  }
}
```

---

### 範例 2：KKTIX 帳密登入

```json
{
  "homepage": "https://kktix.com/events/concert-2023",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/15",
    "mode": "from top to bottom"
  },

  "ocr_captcha": {
    "enable": true,
    "beta": false,
    "force_submit": true
  },

  "advanced": {
    "verbose": true,
    "headless": false,
    "kktix_account": "your_email@example.com",
    "kktix_password": "your_password"
  }
}
```

---

### 範例 3：ibon 座位圖選擇

```json
{
  "homepage": "https://ticket.ibon.com.tw/ActivityInfo/Details/24012345",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025/10/15"
  },

  "seat_auto_select": {
    "enable": true,
    "select_mode": "random",
    "adjacent_seat": true
  },

  "ticket_form_data": {
    "name": "王大明",
    "email": "user@example.com",
    "phone": "0912345678"
  },

  "advanced": {
    "verbose": true,
    "ibon_ibonqware": "your_session_cookie_here"
  }
}
```

---

### 範例 4：無頭模式（伺服器環境）

```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_event",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "mode": "from top to bottom"
  },

  "area_auto_select": {
    "enable": true,
    "mode": "from top to bottom"
  },

  "ocr_captcha": {
    "enable": true,
    "force_submit": true
  },

  "advanced": {
    "verbose": true,
    "headless": true,
    "tixcraft_sid": "your_session_cookie_here"
  },

  "browser_args": [
    "--disable-dev-shm-usage",
    "--no-sandbox"
  ]
}
```

---

### 範例 5：最小配置

```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_event",
  "ticket_number": 2
}
```

**說明**：使用所有預設值，適合快速測試。

---

## 配置驗證規則

### 必需欄位驗證

```python
def validate_required_fields(config_dict):
    """驗證必需欄位"""
    required = ["homepage", "ticket_number"]

    for field in required:
        if field not in config_dict:
            raise ValueError(f"缺少必需欄位：{field}")

    return True
```

---

### 型別驗證

```python
def validate_types(config_dict):
    """驗證欄位型別"""
    validations = [
        ("homepage", str),
        ("ticket_number", int),
        ("webdriver_type", str),
        ("date_auto_select.enable", bool),
        ("advanced.verbose", bool)
    ]

    for path, expected_type in validations:
        value = get_config_value(config_dict, *path.split('.'))
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"欄位 {path} 型別錯誤：期望 {expected_type.__name__}，實際 {type(value).__name__}")

    return True
```

---

### 範圍驗證

```python
def validate_ranges(config_dict):
    """驗證數值範圍"""
    ticket_number = config_dict.get("ticket_number")
    if ticket_number < 1 or ticket_number > 6:
        raise ValueError(f"ticket_number 必須在 1-6 之間，實際值：{ticket_number}")

    interval = get_config_value(config_dict, "advanced", "auto_reload_page_interval", default=1.5)
    if interval < 0.1:
        raise ValueError(f"auto_reload_page_interval 不得小於 0.1 秒")

    return True
```

---

### 枚舉驗證

```python
def validate_enums(config_dict):
    """驗證枚舉值"""
    webdriver_type = config_dict.get("webdriver_type", "nodriver")
    if webdriver_type not in ["nodriver", "uc", "selenium"]:
        raise ValueError(f"不支援的 webdriver_type：{webdriver_type}")

    mode = get_config_value(config_dict, "date_auto_select", "mode", default="from top to bottom")
    valid_modes = ["from top to bottom", "from bottom to top", "center", "random"]
    if mode not in valid_modes:
        raise ValueError(f"不支援的 mode：{mode}")

    return True
```

---

## 配置最佳實踐

### 1. 安全性

✅ **建議**：
- 將 `settings.json` 加入 `.gitignore`
- 設定檔案權限為 600（僅擁有者可讀寫）
- 定期更新 session cookies
- 避免在公開位置分享配置檔案

❌ **避免**：
- 將密碼明文提交到版本控制
- 使用弱密碼
- 分享包含憑證的配置檔案

---

### 2. 效能優化

✅ **建議**：
- 使用 `webdriver_type="nodriver"`（最佳效能）
- 熱門活動：縮短 `auto_reload_page_interval`（0.5-1.0 秒）
- 啟用 `ocr_captcha.force_submit`（增加成功率）
- 無頭模式僅在必要時使用

❌ **避免**：
- 過短的重載間隔（<0.3 秒，可能被偵測）
- 過多的 `browser_args`（可能影響穩定性）

---

### 3. 可靠性

✅ **建議**：
- 提供多個關鍵字作為備選（`"10/15,10/16,10/17"`）
- 設定合理的 `ocr_captcha.retry`（3-5 次）
- 保持 `verbose=true` 以便除錯
- 設定適當的過熱保護參數

❌ **避免**：
- 僅使用單一關鍵字（無回退選項）
- 設定過高的重試次數（拖慢速度）
- 完全停用 verbose（難以除錯）

---

### 4. 維護性

✅ **建議**：
- 為不同活動創建獨立配置檔案
- 使用描述性檔名（`tixcraft_taylorswift_1015.json`）
- 定期備份成功的配置
- 記錄平台特定的設定經驗

❌ **避免**：
- 多個活動共用同一配置檔案
- 缺少註解或說明（JSON 不支援註解，可建立對應的 `.md` 文件）

---

## 平台特定配置建議

### TixCraft

```json
{
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "date_keyword": "具體日期"
  },
  "area_auto_select": {
    "area_keyword": "VIP,搖滾區"
  },
  "ocr_captcha": {
    "enable": true,
    "beta": false
  },
  "advanced": {
    "auto_reload_page_interval": 1.0,
    "tixcraft_sid": "必需"
  }
}
```

---

### KKTIX

```json
{
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "date_keyword": "具體日期"
  },
  "ocr_captcha": {
    "enable": true
  },
  "advanced": {
    "kktix_account": "必需",
    "kktix_password": "必需"
  }
}
```

---

### ibon

```json
{
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "date_keyword": "完整日期格式"
  },
  "seat_auto_select": {
    "enable": true,
    "adjacent_seat": true
  },
  "ocr_captcha": {
    "enable": false
  },
  "advanced": {
    "ibon_ibonqware": "必需"
  }
}
```

---

## 配置遷移指南

### 從舊版本遷移

如果您使用的是舊版配置格式，請參考以下對應關係：

**舊格式** → **新格式**：
- `homepage_url` → `homepage`
- `browser_type` → `webdriver_type`
- `max_ticket` → `ticket_number`
- `date_select_keyword` → `date_auto_select.date_keyword`
- `area_select_keyword` → `area_auto_select.area_keyword`

---

## 未來改進計劃

### 短期（SC-009）

- ✅ JSON Schema 驗證實作
- ✅ 配置檔案範例生成器
- ✅ IDE 自動完成支援（透過 schema）

### 中期

- 🔄 加密敏感欄位（密碼、cookies）
- 🔄 配置檔案視覺化編輯器（Web UI）
- 🔄 配置檔案版本控制

### 長期

- ⏳ 環境變數支援（替代明文儲存）
- ⏳ 雲端配置同步
- ⏳ 配置檔案模板市場（社群分享）

---

**文件狀態**：配置 Schema 契約完成
**最後更新**：2025-10-16
**下一步**：創建 quickstart.md 快速入門指南
