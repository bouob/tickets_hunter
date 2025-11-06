# 設定檔結構定義：FamiTicket NoDriver 遷移

**功能分支**：`005-famiticket-nodriver-migration`
**文件版本**：2025-11-04
**目的**：定義 FamiTicket NoDriver 所需的設定檔結構（完全重用現有欄位）

---

## 重要聲明：無新增欄位

**遵循憲法第 V 條（設定驅動開發）與規格 FR-026、FR-027 要求**：

- ✅ **完全重用**現有 `settings.json` 結構
- ✅ **無新增** FamiTicket 專屬欄位
- ✅ 使用者僅需修改 `webdriver_type` 即可切換引擎

本文件僅記錄 FamiTicket 使用的**現有欄位**及其用途。

---

## 1. 核心設定欄位

### 1.1 引擎選擇（必填）

```json
{
  "webdriver_type": "nodriver"
}
```

**欄位說明**：

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `webdriver_type` | string | ✅ 是 | `"nodriver"` | 瀏覽器引擎類型，選項：`"nodriver"` / `"undetected_chromedriver"` / `"selenium"` |

**FamiTicket 要求**：
- 必須設定為 `"nodriver"` 才能啟用 FamiTicket NoDriver 版本
- 若設定為其他值，將回退至 Chrome 版本（`chrome_tixcraft.py`）

**相關規格**：FR-001（系統必須支援 NoDriver 引擎）

---

## 2. 帳號密碼設定（必填）

### 2.1 FamiTicket 登入憑證

```json
{
  "advanced": {
    "fami_account": "your_account@example.com",
    "fami_password_plaintext": "your_password"
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `advanced.fami_account` | string | ✅ 是 | `""` | FamiTicket 帳號（電子郵件或會員帳號） |
| `advanced.fami_password_plaintext` | string | ✅ 是 | `""` | FamiTicket 密碼（明文） |

**安全性注意**：
- 密碼為明文儲存，請勿分享 `settings.json` 檔案
- 建議使用專用帳號，不要使用主要電子郵件帳號
- 檔案權限建議設定為僅使用者可讀（Unix: `chmod 600`）

**相關規格**：
- FR-002: 系統必須從設定檔讀取帳號與密碼
- FR-003: 使用正確的 CSS 選擇器填寫表單
- SC-001: 95% 登入成功率

**資料模型對應**：
- 對應 `data-model.md` 中的「FamiTicket 登入憑證」實體

---

## 3. 日期選擇設定（選填）

### 3.1 日期自動選擇模式

```json
{
  "date_auto_select": {
    "mode": "from_top_to_bottom",
    "date_keyword": "2025,演唱會"
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `date_auto_select.mode` | string | ⚠️ 建議填寫 | `"from_top_to_bottom"` | 選擇策略：<br>- `"from_top_to_bottom"`: 從第一個可用日期選擇<br>- `"from_bottom_to_top"`: 從最後一個可用日期選擇<br>- `"random"`: 隨機選擇 |
| `date_auto_select.date_keyword` | string | ❌ 否 | `""` | 日期關鍵字（逗號分隔，OR 邏輯），<br>例：`"2025-11-10,週六,演唱會"` |

**邏輯說明**：

1. **關鍵字匹配**（優先）：
   - 若 `date_keyword` 非空，搜尋包含任一關鍵字的日期列表項目
   - 關鍵字匹配範圍：日期文字（`td:nth-child(1)`）+ 區域文字（`td:nth-child(2)`）
   - 使用 OR 邏輯（任一關鍵字匹配即可）

2. **回退機制**（無匹配時）：
   - 若無任何日期匹配關鍵字 → 使用 `mode` 策略選擇可用日期
   - 若日期列表為空 → 觸發自動補票（若啟用）

**範例情境**：

| date_keyword | 匹配結果 | 選擇策略 |
|--------------|---------|---------|
| `"2025-11-10"` | 找到包含「2025-11-10」的日期 | 選擇第一個匹配項目 |
| `"週六,週日"` | 找到包含「週六」或「週日」的日期 | 選擇第一個匹配項目 |
| `""` (空字串) | 無關鍵字匹配 | 使用 `mode` 策略（從第一個可用日期選擇） |

**相關規格**：
- FR-010: 支援日期關鍵字（逗號分隔，OR 邏輯）
- FR-011: 使用 `format_keyword_string()` 正規化關鍵字
- FR-012: 回退至 `auto_select_mode`（若無匹配）
- SC-002: 90% 日期列表掃描成功率（< 2 秒）

**資料模型對應**：
- 對應 `data-model.md` 中的「日期列表」實體

---

## 4. 區域選擇設定（選填）

### 4.1 區域自動選擇模式

```json
{
  "area_auto_select": {
    "mode": "from_top_to_bottom",
    "area_keyword": "搖滾A區,VIP",
    "area_keyword_and": [
      ["搖滾區", "不含柱"],
      ["VIP", "前排"]
    ]
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `area_auto_select.mode` | string | ⚠️ 建議填寫 | `"from_top_to_bottom"` | 選擇策略（同日期選擇模式） |
| `area_auto_select.area_keyword` | string | ❌ 否 | `""` | 區域關鍵字（逗號分隔，OR 邏輯），<br>例：`"搖滾區,VIP,不含柱"` |
| `area_auto_select.area_keyword_and` | array | ❌ 否 | `[]` | AND 邏輯關鍵字群組（二維陣列），<br>例：`[["搖滾區", "不含柱"], ["VIP", "前排"]]` |

**邏輯說明**：

1. **AND 邏輯匹配**（最高優先）：
   - 若 `area_keyword_and` 非空陣列，遍歷每個關鍵字群組
   - 群組內所有關鍵字必須同時出現於區域名稱中
   - 選擇第一個匹配的群組

2. **OR 邏輯匹配**（次優先）：
   - 若 AND 邏輯無匹配，使用 `area_keyword`（逗號分隔）
   - 任一關鍵字匹配即可

3. **回退機制**（無匹配時）：
   - 使用 `mode` 策略選擇第一個可用區域

4. **停用區域過濾**：
   - 自動跳過 class 包含 `"area disabled"` 的區域
   - 確保不會選擇已售罄或不可選的區域

**範例情境**：

| area_keyword_and | area_keyword | 匹配邏輯 | 選擇結果 |
|------------------|--------------|---------|---------|
| `[["搖滾區", "不含柱"]]` | `""` | AND 優先 | 選擇同時包含「搖滾區」**且**「不含柱」的區域 |
| `[]` | `"搖滾區,VIP"` | OR 邏輯 | 選擇包含「搖滾區」**或**「VIP」的區域 |
| `[]` | `""` | 回退 | 使用 `mode` 策略（從第一個可用區域選擇） |

**相關規格**：
- FR-016: 支援區域關鍵字（AND 邏輯）
- FR-017: 支援 `area_keyword_and`（二維陣列）
- FR-018: 過濾已停用區域（class 包含 `"area disabled"`）
- FR-019: 回退至 `auto_select_mode`（若無匹配）
- SC-003: 90% 區域列表掃描成功率（< 2 秒）

**資料模型對應**：
- 對應 `data-model.md` 中的「區域列表」實體

---

## 5. 驗證問題設定（選填）

### 5.1 驗證答案字典

```json
{
  "advanced": {
    "tixcraft_sid": "your_session_cookie",
    "auto_guess_options": true
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `advanced.auto_guess_options` | boolean | ❌ 否 | `false` | 是否啟用自動猜測驗證問題答案 |

**邏輯說明**：

1. **驗證問題偵測**：
   - 檢查頁面是否存在 `#verifyPrefAnswer` 輸入框
   - 若存在 → 呼叫 `fill_common_verify_form()` 工具函數

2. **自動猜測機制**（`auto_guess_options: true` 時）：
   - 使用 `guess_tixcraft_question()` 函數猜測答案
   - 追蹤錯誤答案（`fail_list`），避免重複嘗試
   - 猜測失敗時自動換下一個選項

3. **重用工具函數**：
   - NoDriver 版本完全重用 `util.py` 中的 `fill_common_verify_form()` 函數
   - 僅需調整呼叫方式為非同步

**相關規格**：
- FR-022: 偵測驗證問題（`#verifyPrefAnswer`）
- FR-023: 呼叫 `fill_common_verify_form()` 工具函數
- FR-024: 支援自動猜測（`auto_guess_options: true`）
- FR-025: 追蹤錯誤答案（`fail_list`）
- SC-004: 95% 驗證問題處理成功率

**資料模型對應**：
- 對應 `data-model.md` 中的「驗證問題答案字典」與「錯誤答案清單」實體

---

## 6. 自動補票設定（選填）

### 6.1 自動重新載入設定

```json
{
  "tixcraft": {
    "auto_reload_coming_soon_page": true
  },
  "advanced": {
    "auto_reload_page_interval": 1.5
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `tixcraft.auto_reload_coming_soon_page` | boolean | ❌ 否 | `false` | 是否啟用「即將開賣」頁面自動重新載入 |
| `advanced.auto_reload_page_interval` | number (秒) | ❌ 否 | `0.0` | 自動重新載入間隔（秒），<br>建議值：`1.0` - `30.0` |

**邏輯說明**：

1. **觸發條件**（同時滿足）：
   - `tixcraft.auto_reload_coming_soon_page` 為 `true`
   - 日期列表為空（`formated_area_list` 為 `None` 或長度為 0）

2. **重新載入流程**：
   ```python
   if auto_reload_coming_soon_page_enable:
       if formated_area_list is None or len(formated_area_list) == 0:
           # 等待使用者設定的間隔
           if auto_reload_page_interval > 0:
               await tab.sleep(auto_reload_page_interval)
           # 返回活動頁面（FamiTicket 特定邏輯）
           await tab.get(last_activity_url)
   ```

3. **FamiTicket 特定差異**：
   - **TixCraft**：`await tab.reload()`（重新整理當前頁面）
   - **FamiTicket**：`await tab.get(last_activity_url)`（返回活動頁面）
   - 原因：FamiTicket 的「即將開賣」頁面需要返回活動入口頁面（根據 Chrome 版本邏輯）

**安全性警告**：

⚠️ **請勿設定過短的間隔**（< 1.0 秒）：
- 可能導致 IP 封鎖
- 違反票務平台服務條款
- 建議間隔：5-30 秒（視平台政策調整）

**相關規格**：
- FR-028: 支援自動補票（日期列表為空時自動重新載入）
- FR-029: 使用 `last_activity_url` 返回活動頁面
- SC-006: 30 秒背景測試通過（無崩潰、無死循環）
- SC-008: 重新載入間隔可配置（`auto_reload_page_interval`）

**資料模型對應**：
- 對應 `data-model.md` 中的「自動補票設定」實體

---

## 7. 除錯與日誌設定（選填）

### 7.1 除錯輸出控制

```json
{
  "advanced": {
    "verbose": true,
    "running_status_text": ""
  }
}
```

**欄位說明**：

| 欄位路徑 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `advanced.verbose` | boolean | ❌ 否 | `false` | 是否啟用詳細除錯訊息（`show_debug_message` 參數） |
| `advanced.running_status_text` | string | ❌ 否 | `""` | 執行狀態訊息（程式內部使用） |

**邏輯說明**：

1. **除錯訊息控制**：
   - 所有 FamiTicket 函數接受 `show_debug_message` 參數
   - 參數值從 `config_dict["advanced"]["verbose"]` 讀取
   - 啟用時輸出關鍵字匹配、元素搜尋、點擊操作等詳細日誌

2. **除錯輸出範例**：
   ```
   [DATE KEYWORD] Matched keyword: "2025-11-10"
   [DATE SELECT] Selected date: "2025-11-10 週六 19:30"
   [AREA KEYWORD] AND logic: ["搖滾區", "不含柱"]
   [AREA SELECT] Selected area: "搖滾區 不含柱 A1-A10"
   ```

**相關規格**：
- FR-038: 所有函數返回布林值（簡化狀態管理）
- FR-039: 函數命名遵循 `nodriver_fami_*` 規範

---

## 8. 完整設定範例

### 8.1 最小設定（僅登入）

```json
{
  "webdriver_type": "nodriver",
  "advanced": {
    "fami_account": "user@example.com",
    "fami_password_plaintext": "password123"
  }
}
```

### 8.2 完整設定（所有功能）

```json
{
  "webdriver_type": "nodriver",
  "homepage": "https://www.famiticket.com.tw",
  "advanced": {
    "fami_account": "user@example.com",
    "fami_password_plaintext": "password123",
    "auto_guess_options": true,
    "verbose": true,
    "auto_reload_page_interval": 5.0
  },
  "date_auto_select": {
    "mode": "from_top_to_bottom",
    "date_keyword": "2025-11-10,週六"
  },
  "area_auto_select": {
    "mode": "from_top_to_bottom",
    "area_keyword": "搖滾區,VIP",
    "area_keyword_and": [
      ["搖滾區", "不含柱"],
      ["VIP", "前排"]
    ]
  },
  "tixcraft": {
    "auto_reload_coming_soon_page": true
  }
}
```

---

## 9. 設定檔驗證檢查清單

**使用者在啟用 FamiTicket NoDriver 前必須檢查**：

- [ ] `webdriver_type` 已設定為 `"nodriver"`
- [ ] `advanced.fami_account` 已填寫（必填）
- [ ] `advanced.fami_password_plaintext` 已填寫（必填）
- [ ] `date_auto_select.mode` 已設定（建議）
- [ ] `area_auto_select.mode` 已設定（建議）
- [ ] `auto_reload_page_interval` >= 1.0（若啟用自動補票）
- [ ] 密碼儲存於安全位置（避免洩漏）

---

## 10. 變更記錄

| 日期 | 版本 | 變更內容 |
|------|------|---------|
| 2025-11-04 | 1.0.0 | 初始版本（完全重用現有欄位，無新增） |

---

**憲法遵循聲明**：
- ✅ 遵循憲法第 V 條（設定驅動開發）：所有行為由 `settings.json` 控制
- ✅ 遵循規格 FR-026：完全重用現有設定檔結構
- ✅ 遵循規格 FR-027：使用者僅需修改 `webdriver_type` 即可切換引擎
