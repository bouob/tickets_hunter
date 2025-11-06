# 資料模型：FamiTicket NoDriver 遷移

**功能分支**：`005-famiticket-nodriver-migration`
**建立日期**：2025-11-04
**目的**：定義 FamiTicket 自動化過程中的核心資料結構

---

## 概述

本文件定義 FamiTicket NoDriver 遷移所需的核心資料實體、欄位、關係與狀態轉換。所有資料結構遵循**憲法第 II 條（資料結構優先）**原則，先定義結構再進入實作。

---

## 核心實體 (Core Entities)

### 1. FamiTicket 登入憑證 (Login Credentials)

**用途**：代表使用者的 FamiTicket 帳號與密碼

**資料來源**：`settings.json` 設定檔

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 來源設定檔路徑 |
|---------|------|------|------|----------------|
| `account` | string | ✅ | FamiTicket 帳號（電子郵件或手機號碼） | `advanced.fami_account` |
| `password` | string | ✅ | 明文密碼 | `advanced.fami_password_plaintext` |
| `password_encrypted` | string | ⚠️ | 加密密碼（備用） | `advanced.fami_password` |

**驗證規則**：
- `account` 長度 > 0
- `password` 或 `password_encrypted` 至少一個必須存在
- 若兩者皆存在，優先使用 `password_plaintext`

**使用情境**：
- 偵測到登入頁面（URL 包含 `/Home/User/SignIn`）
- 填寫 `#usr_act` (帳號) 與 `#usr_pwd` (密碼) 輸入框

---

### 2. 日期列表 (Date List)

**用途**：代表活動的所有可用演出日期

**資料來源**：FamiTicket 頁面 DOM（CSS 選擇器：`table.session__list > tbody > tr`）

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 擷取方式 |
|---------|------|------|------|---------|
| `date_text` | string | ✅ | 日期文字（例如：「2025-12-25 週六 19:30」） | `td:nth-child(1)` 的文字內容 |
| `area_text` | string | ✅ | 區域文字（例如：「台北小巨蛋」） | `td:nth-child(2)` 的文字內容 |
| `button_text` | string | ✅ | 按鈕文字（例如：「立即購買」或「售完」） | `button` 元素的文字內容 |
| `button_element` | DOM Element | ✅ | 購買按鈕的 DOM 元素引用 | NoDriver element 物件 |
| `is_available` | boolean | ✅ | 是否可購買（按鈕文字包含「立即購買」） | 衍生欄位 |
| `node_id` | int | ✅ | CDP node ID（用於點擊） | CDP `get_node_id()` |

**資料結構（記憶體表示）**：
```python
formated_area_list = [
    {
        "date": "2025-12-25 週六 19:30",
        "area": "台北小巨蛋",
        "button_text": "立即購買",
        "button_element": <NoDriver Element>,
        "is_available": True,
        "node_id": 12345
    },
    {
        "date": "2025-12-26 週日 14:00",
        "area": "高雄巨蛋",
        "button_text": "售完",
        "button_element": None,
        "is_available": False,
        "node_id": None
    }
]
```

**驗證規則**：
- `date_text` 非空字串
- `button_text` 必須為「立即購買」或「售完」或類似文字
- `is_available == True` 時，`button_element` 與 `node_id` 必須非 None

**狀態轉換**：
```
初始狀態 (空列表)
  ↓ 掃描 DOM（perform_search）
從 DOM 擷取資料
  ↓ 關鍵字匹配（date_keyword, area_keyword）
過濾後的日期列表
  ↓ 選擇目標日期
目標日期 (單一項目)
  ↓ 點擊按鈕 (dispatch_mouse_event)
進入區域選擇頁面
```

---

### 3. 區域列表 (Area List)

**用途**：代表單一演出日期的所有可用座位區域

**資料來源**：FamiTicket 頁面 DOM（CSS 選擇器：`div > a.area`）

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 擷取方式 |
|---------|------|------|------|---------|
| `area_name` | string | ✅ | 區域名稱（例如：「VIP 一樓」） | `a.area` 的文字內容 |
| `area_html` | string | ✅ | 區域 HTML（用於檢查 disabled） | `innerHTML` 屬性 |
| `is_disabled` | boolean | ✅ | 是否已停用（class 包含 `"area disabled"`） | 衍生欄位 |
| `area_element` | DOM Element | ⚠️ | 區域連結的 DOM 元素（若可用） | NoDriver element 物件 |
| `node_id` | int | ⚠️ | CDP node ID（用於點擊） | CDP `get_node_id()` |

**資料結構（記憶體表示）**：
```python
area_list = [
    {
        "area_name": "VIP 一樓",
        "area_html": "<a class='area'>VIP 一樓</a>",
        "is_disabled": False,
        "area_element": <NoDriver Element>,
        "node_id": 23456
    },
    {
        "area_name": "搖滾區",
        "area_html": "<a class='area disabled'>搖滾區</a>",
        "is_disabled": True,
        "area_element": None,
        "node_id": None
    }
]
```

**驗證規則**：
- `area_name` 非空字串
- `is_disabled == False` 時，`area_element` 與 `node_id` 必須非 None
- 過濾時必須排除 `is_disabled == True` 的項目

**關鍵字匹配邏輯（AND）**：
```python
# 區域關鍵字：「VIP,一樓」（逗號分隔 = AND 邏輯）
area_keywords = ["VIP", "一樓"]

# 匹配條件：所有關鍵字都必須在 area_name 中
is_match = all(keyword in area_name for keyword in area_keywords)
```

---

### 4. 驗證問題答案字典 (Verification Answer Dictionary)

**用途**：儲存預設的驗證問題答案，用於自動填寫或猜測

**資料來源**：`settings.json` 設定檔（`area_auto_select.area_answer`）

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 來源設定檔路徑 |
|---------|------|------|------|----------------|
| `answer_string` | string | ✅ | 預設答案文字 | `area_auto_select.area_answer` |
| `answer_list` | list[string] | ✅ | 分割後的答案清單（逗號分隔） | 衍生欄位 |
| `auto_guess_enable` | boolean | ✅ | 是否啟用自動猜測 | `advanced.auto_guess_options` |

**資料結構（記憶體表示）**：
```python
verification_config = {
    "answer_string": "五月天演唱會,MayDay Concert",
    "answer_list": ["五月天演唱會", "MayDay Concert"],
    "auto_guess_enable": True
}
```

**使用流程**：
1. 偵測驗證輸入框（`#verifyPrefAnswer`）
2. 若 `auto_guess_enable == True`：
   - 呼叫 `guess_tixcraft_question()` 從活動標題推斷答案
3. 否則：
   - 從 `answer_list` 中選擇第一個未失敗的答案

**整合工具函數**：
- `util.get_answer_list_from_user_guess_string()`: 將 `answer_string` 分割為 `answer_list`
- `util.guess_tixcraft_question()`: 從頁面內容推斷答案
- `util.fill_common_verify_form()`: 填寫驗證表單（可重用）

---

### 5. 錯誤答案清單 (fail_list)

**用途**：追蹤已嘗試但失敗的驗證答案，避免重複嘗試

**資料來源**：執行階段記憶體（初始為空列表）

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `failed_answers` | list[string] | ✅ | 已失敗的答案文字列表 |

**資料結構（記憶體表示）**：
```python
fail_list = ["錯誤答案1", "錯誤答案2"]
```

**狀態轉換**：
```
初始狀態 (空列表)
  ↓ 嘗試答案 A
驗證失敗
  ↓ 加入 fail_list
fail_list = ["答案 A"]
  ↓ 嘗試答案 B
驗證成功
  ↓ 清空 fail_list（或保留供下次使用）
fail_list = []
```

**驗證規則**：
- 嘗試答案前，檢查答案是否在 `fail_list` 中
- 若在，跳過該答案
- 驗證失敗後，立即加入 `fail_list`

---

### 6. 自動補票設定 (Auto-Reload Configuration)

**用途**：控制自動重新載入頁面的行為

**資料來源**：`settings.json` 設定檔

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 來源設定檔路徑 |
|---------|------|------|------|----------------|
| `enable` | boolean | ✅ | 是否啟用自動補票 | `tixcraft.auto_reload_coming_soon_page` |
| `interval` | float | ✅ | 重新載入間隔（秒） | `advanced.auto_reload_page_interval` |
| `last_activity_url` | string | ⚠️ | 活動頁面 URL（用於返回） | 執行階段傳遞 |

**資料結構（記憶體表示）**：
```python
auto_reload_config = {
    "enable": True,
    "interval": 5.0,  # 5 秒
    "last_activity_url": "https://www.famiticket.com.tw/Home/Activity/Info/123"
}
```

**觸發條件**：
```python
if auto_reload_config["enable"]:
    if formated_area_list is None or len(formated_area_list) == 0:
        # 等待間隔
        if auto_reload_config["interval"] > 0:
            await tab.sleep(auto_reload_config["interval"])

        # 重新載入活動頁面（FamiTicket 專屬邏輯）
        await tab.get(auto_reload_config["last_activity_url"])
        await tab.sleep(0.5)
```

**驗證規則**：
- `interval` 必須 >= 0（0 表示立即重新載入）
- `last_activity_url` 必須為有效 URL（包含 `/Home/Activity/Info/`）

---

## 實體關係圖 (Entity Relationships)

```
┌─────────────────────────┐
│  Login Credentials      │
│  (設定檔讀取)           │
└────────────┬────────────┘
             │
             ↓ 用於登入
┌─────────────────────────┐
│  FamiTicket 登入頁面     │
└────────────┬────────────┘
             │
             ↓ 成功後進入
┌─────────────────────────┐
│  活動頁面 (Activity)    │
└────────────┬────────────┘
             │
             ↓ 點擊購買按鈕
┌─────────────────────────┐
│  Date List              │
│  (多個演出日期)         │
└────────────┬────────────┘
             │
             ├─ 關鍵字匹配 ← date_keyword (設定檔)
             │
             ↓ 選擇目標日期
┌─────────────────────────┐
│  Area List              │
│  (單一日期的多個區域)   │
└────────────┬────────────┘
             │
             ├─ 關鍵字匹配 ← area_keyword (設定檔)
             │
             ↓ 選擇目標區域
┌─────────────────────────┐
│  驗證問題頁面            │
└────────────┬────────────┘
             │
             ├─ 答案來源 ← Verification Answer Dictionary
             │
             ├─ 錯誤追蹤 ← fail_list
             │
             ↓ 驗證成功
┌─────────────────────────┐
│  購票確認頁面            │
└─────────────────────────┘

【自動補票迴圈】
  Date List 為空
     ↓
  Auto-Reload Config (若啟用)
     ↓ 等待間隔
  重新載入 last_activity_url
     ↓
  回到 Date List 掃描
```

---

## 狀態機模型 (State Machine)

### FamiTicket 自動化狀態轉換

```
[初始狀態]
  ↓
[登入狀態]
  │ 條件：URL 包含 /Home/User/SignIn
  │ 動作：填寫 Login Credentials
  │ 轉移：成功 → [活動頁面]，失敗 → [錯誤狀態]
  ↓
[活動頁面]
  │ 條件：URL 包含 /Home/Activity/Info/
  │ 動作：點擊購買按鈕 (#buyWaiting)
  │ 轉移：成功 → [日期選擇]，按鈕不存在 → [重新整理]
  ↓
[日期選擇]
  │ 條件：Date List 非空
  │ 動作：關鍵字匹配 + 點擊目標日期
  │ 轉移：成功 → [區域選擇]，列表為空 → [自動補票]
  ↓
[區域選擇]
  │ 條件：Area List 非空
  │ 動作：關鍵字匹配（AND 邏輯）+ 點擊目標區域
  │ 轉移：成功 → [驗證問題]，無匹配 → [回退模式]
  ↓
[驗證問題]
  │ 條件：偵測到 #verifyPrefAnswer
  │ 動作：填寫答案（從 Answer Dictionary 或自動猜測）
  │ 轉移：成功 → [購票確認]，失敗 → [重試]（加入 fail_list）
  ↓
[購票確認]
  │ 條件：進入確認頁面
  │ 動作：等待使用者手動確認
  │ 轉移：無自動操作
  ↓
[結束狀態]

【特殊狀態】
[自動補票]
  │ 條件：Date List 為空 且 auto_reload_enable == True
  │ 動作：await tab.sleep(interval) → await tab.get(last_activity_url)
  │ 轉移：回到 [日期選擇]

[錯誤狀態]
  │ 條件：任何步驟發生例外
  │ 動作：記錄錯誤訊息 → 停止執行
  │ 轉移：無（需手動介入）
```

---

## 資料驗證規則總結

| 實體 | 必填欄位 | 驗證邏輯 | 錯誤處理 |
|------|---------|---------|---------|
| Login Credentials | account, password | 長度 > 0 | 停止執行 |
| Date List | date_text, button_text | button_text == "立即購買" | 過濾該項目 |
| Area List | area_name, area_html | is_disabled == False | 過濾該項目 |
| Answer Dictionary | answer_string | 非空字串 | 使用自動猜測 |
| fail_list | - | 答案不在列表中 | 跳過該答案 |
| Auto-Reload Config | enable, interval | interval >= 0 | 停用自動補票 |

---

## 下一步

Phase 1 將繼續產生：
1. **contracts/function-signatures.md**：定義所有函數簽章
2. **contracts/config-schema.md**：確認設定檔欄位（無需新增）
3. **quickstart.md**：提供快速測試與部署指南

---

**建立日期**：2025-11-04
**下一階段**：contracts/ 與 quickstart.md
