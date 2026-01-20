# Urbtix NoDriver 轉換規劃

**建立日期**：2026-01-12
**狀態**：規劃中
**優先級**：中

---

## 1. 現況分析

### 1.1 實作狀態

| 版本 | 檔案 | 狀態 |
|------|------|------|
| Selenium/UC | `chrome_tixcraft.py` | ✅ 完整實作 |
| NoDriver | `nodriver_tixcraft.py` | ❌ **尚未轉換** |

### 1.2 NoDriver 現有程式碼

```python
# nodriver_tixcraft.py:24512-24513
if 'urbtix.hk' in url:
    #urbtix_main(driver, url, config_dict)  # <-- 被註解掉
```

僅有常數定義和 homepage 重定向邏輯，主功能未實作。

---

## 2. 需轉換的函數清單

### 2.1 核心函數（必要）

| 函數名稱 | 行號 | 功能 | 複雜度 |
|----------|------|------|--------|
| `urbtix_main` | 6654 | 主控制函數，URL 路由 | 中 |
| `urbtix_login` | 5441 | 帳號密碼登入 | 低 |
| `urbtix_purchase_ticket` | 4010 | 購票入口（event-detail 頁） | 低 |
| `urbtix_date_auto_select` | 3871 | 日期自動選擇 | 高 |
| `urbtix_performance` | 4350 | 場次頁面處理 | 中 |
| `urbtix_area_auto_select` | 4025 | 區域/票價自動選擇 | 高 |
| `urbtix_ticket_number_auto_select` | 4182 | 票數自動選擇 | 中 |

### 2.2 輔助函數（建議）

| 函數名稱 | 行號 | 功能 | 複雜度 |
|----------|------|------|--------|
| `urbtix_uncheck_adjacent_seat` | 4311 | 取消連座選項 | 低 |
| `urbtix_performance_confirm_dialog_popup` | 6342 | 確認對話框處理 | 低 |

### 2.3 可選函數（低優先）

| 函數名稱 | 行號 | 功能 | 備註 |
|----------|------|------|------|
| `urbtix_auto_survey` | 6490 | 自動問卷 | 目前在舊版也被註解 |
| `get_urbtix_survey_answer_by_question` | 6384 | 問卷答案判斷 | 配合 auto_survey |

---

## 3. 頁面結構分析（MCP 檢查結果）

### 3.1 首頁 (https://www.urbtix.hk/)

- 登入按鈕：下拉選單觸發
- 搜尋功能：textbox + button
- 節目列表：tabpanel 結構

### 3.2 登入頁面 (https://www.urbtix.hk/member-login)

| 元素 | 類型 | 選擇器（舊版） | 備註 |
|------|------|---------------|------|
| 登入名稱 | textbox | `input[name="loginId"]` | required |
| 密碼 | textbox | `input[name="password"]` | required |
| 驗證碼 | radio | 圖形/聲音 | 需人工處理 |
| 登入按鈕 | button | `.login-button` | |
| 智方便登入 | button | 以智方便繼續 | 替代登入方式 |

### 3.3 活動頁面 (event-detail) - MCP 實測

URL 格式：`https://www.urbtix.hk/event-detail/{eventId}/`

**實測結構**（單日期活動）：
```
heading "節目名稱:..."
generic "日期" + "2026年2月1日"
button "場地名稱"
tab "節目資料" / "票務資料"
button "查看門票詳情"
button "加到我的書籤"
button "購買門票"  <-- 點擊後導向登入頁
```

**行為發現**：
- 點擊「購買門票」會先跳轉到登入頁面（如未登入）
- 登入 URL：`/login/?redirect=%2Fperformance-detail%3FeventId%3D...%26performanceId%3D...`
- 非會員購票也需要完成驗證碼

### 3.4 場次頁面 (performance-detail)

URL 格式：`https://www.urbtix.hk/performance-detail/?eventId={id}&performanceId={id}`

**注意**：需登入後才能訪問，MCP 測試時被重定向至登入頁

---

## 4. 轉換策略

### 4.1 Selenium → NoDriver 對照

| Selenium | NoDriver |
|----------|----------|
| `driver.find_element(By.CSS_SELECTOR, sel)` | `await page.select(sel)` 或 `await page.query_selector(sel)` |
| `element.send_keys(text)` | `await element.send_keys(text)` |
| `element.click()` | `await element.click()` |
| `element.get_attribute('value')` | `await element.get_attribute('value')` 或 `element.attrs.get('value')` |
| `element.is_enabled()` | 檢查 element 是否存在 |
| `element.is_displayed()` | 需用其他方式判斷 |
| `driver.get(url)` | `await page.get(url)` |

### 4.2 注意事項

1. **async/await**：所有 NoDriver 操作都是異步的
2. **元素等待**：NoDriver 有內建等待機制，但可能需要額外 `await asyncio.sleep()`
3. **錯誤處理**：需要適當的 try/except 包裝
4. **驗證碼**：登入頁面有驗證碼，需保留人工介入機制

---

## 5. 實作順序建議

### Phase 1：基礎框架（1-2 小時）
1. 建立 `urbtix_main_async()` 函數框架
2. 實作 URL 路由邏輯
3. 取消 nodriver_tixcraft.py 中的註解

### Phase 2：登入功能（1 小時）
1. 轉換 `urbtix_login()` 為 async 版本
2. 測試登入流程（需注意驗證碼）

### Phase 3：購票核心（2-3 小時）
1. 轉換 `urbtix_purchase_ticket()`
2. 轉換 `urbtix_date_auto_select()`
3. 轉換 `urbtix_performance()`

### Phase 4：選位功能（2-3 小時）
1. 轉換 `urbtix_area_auto_select()`
2. 轉換 `urbtix_ticket_number_auto_select()`
3. 轉換 `urbtix_uncheck_adjacent_seat()`

### Phase 5：測試與調整（1-2 小時）
1. 完整流程測試
2. 邊界條件處理
3. 錯誤處理優化

---

## 6. 設定檔相關

### 6.1 現有設定項

```json
{
  "advanced": {
    "urbtix_account": "",
    "urbtix_password": "",
    "urbtix_password_plaintext": ""
  }
}
```

### 6.2 建議新增設定

無需新增，現有設定已足夠。

---

## 7. 測試計畫

### 7.1 測試環境

- 測試網站：https://www.urbtix.hk/
- 測試帳號：需準備 Urbtix 帳號

### 7.2 測試案例

| 測試項目 | 預期結果 |
|----------|----------|
| 登入頁面載入 | 正確顯示登入表單 |
| 自動填入帳號密碼 | 欄位正確填入 |
| 活動頁面日期選擇 | 自動選擇符合條件的日期 |
| 場次頁面區域選擇 | 自動選擇符合條件的區域 |
| 票數選擇 | 自動選擇正確票數 |

---

## 8. 風險評估

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| **Tencent CAPTCHA** | **高** | 保留手動登入選項，驗證碼為滑塊拼圖類型 |
| WAF 自動化偵測 | 高 | 使用 NoDriver 反偵測特性，控制操作頻率 |
| API `x-token` 認證 | 中 | 登入後 session 會持續有效 |
| 網站結構變更 | 中 | 使用多種選擇器作為備案 |
| IP 限制/封鎖 | 中 | 控制請求頻率，避免頻繁重試 |
| 排隊系統 | 低 | 檢測 landing-timer 頁面 |

### 8.1 MCP 實測發現的新風險

1. **Tencent CAPTCHA (captcha.gtimg.com)**
   - 類型：滑塊拼圖驗證碼
   - 觸發時機：登入、偵測自動化行為、頻繁操作
   - 影響：無法完全自動化登入流程

2. **Tencent EdgeOne WAF**
   - 網站使用 Tencent EdgeOne CDN 和 WAF
   - 會偵測自動化行為並觸發驗證碼
   - Cookie `x-waf-captcha-referer` 用於追蹤

3. **複雜認證機制**
   - 使用 `x-token` header 而非單純 Cookie
   - 需要 `x-client-id-enc` 加密客戶端 ID
   - Cookie 快速登入**不可行**

---

## 9. NoDriver 共用 Utility 函式

### 9.1 可重複使用的函式

以下函式已在 `nodriver_tixcraft.py` 中實作，Urbtix 轉換時可直接使用：

| 函式名稱 | 行號 | 功能 | 用途 |
|----------|------|------|------|
| `nodriver_press_button(tab, select_query)` | 217 | 按鈕點擊 | 通用按鈕操作 |
| `nodriver_check_checkbox(tab, select_query, value)` | 233 | checkbox 勾選 | 同意條款等 |
| `nodriver_force_check_checkbox(tab, checkbox_element)` | 287 | 強制勾選 checkbox | 確保勾選成功 |
| `nodriver_check_checkbox_enhanced(tab, select_query)` | 320 | 增強版勾選 | 複雜場景 |
| `nodriver_get_text_by_selector(tab, css_selector, attribute)` | 2887 | 取得元素文字 | 讀取頁面內容 |

### 9.2 NoDriver 基礎操作對照

```python
# 元素查詢
element = await tab.query_selector('selector')
elements = await tab.query_selector_all('selector')

# 點擊
await element.click()

# 輸入文字
await element.send_keys('text')

# 取得屬性
value = element.attrs.get('value')
# 或使用 JavaScript
value = await tab.evaluate('document.querySelector("selector").value')

# 取得 HTML 內容
html = await element.get_html()

# 執行 JavaScript
result = await tab.evaluate('JavaScript code')

# 頁面導航
await tab.get('url')
await page.reload()

# 等待元素
await tab.wait_for('selector', timeout=5)
```

### 9.3 Selenium vs NoDriver 對照表

| 操作 | Selenium | NoDriver |
|------|----------|----------|
| 查詢單一元素 | `driver.find_element(By.CSS_SELECTOR, sel)` | `await tab.query_selector(sel)` |
| 查詢多個元素 | `driver.find_elements(By.CSS_SELECTOR, sel)` | `await tab.query_selector_all(sel)` |
| 點擊元素 | `element.click()` | `await element.click()` |
| 輸入文字 | `element.send_keys(text)` | `await element.send_keys(text)` |
| 取得屬性 | `element.get_attribute('name')` | `element.attrs.get('name')` |
| 取得文字 | `element.text` | `await element.get_html()` + 處理 |
| 頁面跳轉 | `driver.get(url)` | `await tab.get(url)` |
| 執行 JS | `driver.execute_script(js)` | `await tab.evaluate(js)` |
| 元素可見 | `element.is_displayed()` | 需用 JS 判斷 |
| 元素啟用 | `element.is_enabled()` | 需用 JS 判斷 |

### 9.4 util.py 共用函式

以下 `util.py` 函式在 NoDriver 中同樣可用：

| 函式 | 用途 | 備註 |
|------|------|------|
| `util.get_debug_mode(config_dict)` | 取得除錯模式設定 | 無需修改 |
| `util.decryptMe(encrypted_text)` | 解密密碼 | 無需修改 |
| `util.remove_html_tags(html)` | 移除 HTML 標籤 | 用於 innerText |
| `util.get_target_index_by_mode()` | 計算目標索引 | 無需修改 |
| `util.get_target_item_from_matched_list()` | 取得目標物件 | 無需修改 |
| `util.parse_keyword_string_to_array()` | 解析關鍵字 | 無需修改 |

---

## 10. 參考資料

- 舊版實作：`src/chrome_tixcraft.py` 行 3871-6718
- NoDriver API：`docs/06-api-reference/nodriver_api_guide.md`
- 12 階段標準：`docs/02-development/ticket_automation_standard.md`
- NoDriver 共用函式：`src/nodriver_tixcraft.py` 行 217-357, 2887-2902

---

## 更新紀錄

| 日期 | 內容 |
|------|------|
| 2026-01-12 | 初次建立規劃文件 |
| 2026-01-12 | 新增 MCP 實測 event-detail 頁面結構 |
| 2026-01-12 | 更新風險評估：Tencent CAPTCHA、WAF、認證機制 |
| 2026-01-12 | 確認 Cookie 快速登入不可行 |
