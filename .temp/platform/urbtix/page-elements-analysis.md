# Urbtix 頁面元素分析

**分析日期**：2026-01-12
**分析工具**：MCP Chrome DevTools

---

## 1. 登入頁面

**URL**：
- 會員登入頁：`https://www.urbtix.hk/member-login`
- 購票登入頁：`https://www.urbtix.hk/login/?redirect=...`

### 1.1 登入類型切換 (MCP 實測)

| 類型 | radio 狀態 | 說明 |
|------|------------|------|
| 會員登入 | checked (預設) | 需要帳號密碼 |
| 非會員登入 | - | 需要驗證碼 |

### 1.2 表單元素

| 元素 | UID | 類型 | 選擇器 | 備註 |
|------|-----|------|--------|------|
| 登入名稱 | - | textbox | `input[name="loginId"]` | required，會員登入 |
| 密碼 | - | textbox | `input[name="password"]` | required，會員登入 |
| 驗證碼-圖形 | - | radio | - | checked (預設) |
| 驗證碼-聲音 | - | radio | - | 無障礙選項 |
| 智方便登入 | - | button | - | 替代登入方式 |
| 登入按鈕 | - | button | - | 非會員登入模式下出現 |

### 1.3 Tencent CAPTCHA 驗證碼

**驗證碼類型**：滑塊拼圖 (Slider Puzzle)
**載入來源**：`https://captcha.gtimg.com/static/template/drag_ele.*.html`

```
Iframe (驗證碼)
  RootWebArea "验证码" url="https://captcha.gtimg.com/..."
    generic "視覺驗證"
      StaticText "安全驗證"
    button "關閉驗證"
    StaticText "拖動下方滑塊完成拼圖"
    image "slider"
    button "意見反映"
    button "刷新驗證"
```

**重要**：驗證碼會在以下情況觸發：
- 登入時
- 偵測到自動化行為時
- 頻繁操作時

### 1.2 頁面快照

```
RootWebArea "城市售票網 - 會員登入" url="https://www.urbtix.hk/member-login"
  banner
    link "城市售票網"
    textbox "關鍵字搜尋"
    button "關鍵字搜尋"
    ...
  heading "登入" level="1"
  StaticText "登入名稱"
  textbox "登入名稱" required
  StaticText "密碼"
  textbox "密碼" required
  link "忘記密碼?"
  StaticText "驗證碼"
  generic "選擇「聲音」以獲得無障礙的驗證體驗"
  radio "圖形" checked
  radio "聲音"
  button "以智方便繼續"
  ...
```

### 1.3 登入按鈕

舊版使用 `.login-button` 選擇器，但在 MCP 快照中未直接看到。
可能需要檢查驗證碼輸入後才會出現，或使用其他選擇器。

---

## 2. 首頁

**URL**：`https://www.urbtix.hk/`

### 2.1 主要元素

| 元素 | UID | 類型 | 功能 |
|------|-----|------|------|
| Logo | 5_4 | link | 首頁連結 |
| 搜尋框 | 5_5 | textbox | 關鍵字搜尋 |
| 搜尋按鈕 | 5_6 | button | 執行搜尋 |
| 進階搜尋 | 5_7 | button | 展開進階選項 |
| 場地 | 5_8 | button | 場地篩選 |
| 節目 | 5_10 | button | 節目篩選 |
| 日曆 | 5_12 | button | 日期篩選 |
| 語言 | 5_13 | button | 語言切換 |
| 購物籃 | 5_15 | button | 購物車 |
| 書籤 | 5_16 | button | 收藏 |
| 顧客服務 | 5_17 | button | 客服選單 |
| 登入 | 5_19 | button | 登入選單 |

### 2.2 節目列表 Tabs

| Tab | UID | 功能 |
|-----|-----|------|
| 今日開售 | 5_42 | 當日開賣節目 |
| 今日節目 | 5_44 | 當日演出節目 |
| 熱賣中 | 5_46 | 熱門節目 |
| 即將開售 | 5_48 | 即將開賣節目 |

---

## 3. 等待頁面

### 3.1 排隊/忙碌頁面

根據舊版程式碼，以下 URL 需要特殊處理：

```python
waiting_for_access_url = [
    '/session/landing-timer/',  # 排隊倒數
    'msg.urbtix.hk',            # 訊息頁
    'busy.urbtix.hk'            # 忙碌頁
]
```

處理方式：自動跳轉回首頁

### 3.2 登出頁面

URL 包含 `/logout?` 時，自動跳轉回首頁

---

## 4. 活動頁面 (event-detail)

**URL 格式**：`https://www.urbtix.hk/event-detail/{eventId}/`

**實測 URL**：`https://www.urbtix.hk/event-detail/14476/` (迷失時光)

### 4.1 MCP 快照結構

```
RootWebArea "城市售票網 - 迷失時光" url="https://www.urbtix.hk/event-detail/14476/"
  banner (導航列)
  image "迷失時光" (節目海報)
  heading "節目名稱:迷失時光 " level="1"
  StaticText "日期" + generic "2026年2月1日"
  StaticText "場地" + button "荃灣大會堂演奏廳"
  button "Facebook" / "Twitter" / "微博" (分享按鈕)
  heading "節目資料" level="2"
  tab "節目資料" selected
  heading "票務資料" level="2"
  tab "票務資料"
  tabpanel "節目資料"
    StaticText "主辦機構" / "節目類別" / "門票模式" / "節目簡介"
  image "購買門票"
  heading "購買門票" level="2"
  generic "節目名稱:..."
  generic "節目日期:..."
  button "查看門票詳情"
  button "加到我的書籤"
  button "購買門票"  <-- 關鍵按鈕，點擊後跳轉登入或場次頁
```

### 4.2 需要的操作

- 日期選擇：`urbtix_date_auto_select()` (多日期活動)
- 點擊購票：`urbtix_purchase_ticket()`

### 4.3 發現事項

1. 單日期活動直接顯示「購買門票」按鈕
2. 點擊「購買門票」會先跳轉到登入頁面（如未登入）
3. 登入後重定向至 performance-detail 頁面

---

## 5. 場次頁面 (performance-detail)

**URL 格式**：
- `https://www.urbtix.hk/performance-detail/?eventId={id}&performanceId={id}`
- `https://www.urbtix.hk/performance-detail?eventId={id}&performanceId={id}`

### 5.1 需要的操作

- 確認對話框：`urbtix_performance_confirm_dialog_popup()`
- 區域選擇：`urbtix_area_auto_select()`
- 票數選擇：`urbtix_ticket_number_auto_select()`
- 連座設定：`urbtix_uncheck_adjacent_seat()`

### 5.2 選擇器（待確認）

需要實際進入場次頁面才能分析元素結構。

---

## 6. Cookie 與認證資訊

### 6.1 登入前 Cookies (MCP 實測)

| Cookie | 用途 | 備註 |
|--------|------|------|
| `X-Client-ID` | 客戶端識別碼 | 32 字元 hex |
| `viewedEventIds` | 已瀏覽活動 ID | URL-encoded JSON array |
| `x-waf-captcha-referer` | WAF 驗證碼來源追蹤 | |
| `Cc2838679FT` | Token Cookie | 長字串，可能含加密資訊 |
| `Cc2838679FS` | Session Cookie | 類似 FT |
| `serverTime` | 伺服器時間戳 | Unix timestamp |

### 6.2 API 認證 Headers

| Header | 用途 | 備註 |
|--------|------|------|
| `x-client-id` | 客戶端 ID | 與 Cookie 相同 |
| `x-client-id-enc` | 加密客戶端 ID | Base64 加密 |
| `x-token` | 認證 Token | 未登入時為空 |
| `x-client-type` | 客戶端類型 | 固定值 `1` |
| `x-sales-channel` | 銷售渠道 | 固定值 `1` |
| `x-locale` | 語言設定 | `zh_HK` / `en_US` |
| `sw8` | SkyWalking 追蹤 | APM 監控用 |

### 6.3 Cookie 快速登入可行性分析

**結論**：**不建議** Cookie 快速登入

**原因**：
1. 認證機制複雜，使用 `x-token` header 而非單純 Cookie
2. 需要 `x-client-id-enc` 加密客戶端 ID
3. WAF (Tencent EdgeOne) 會偵測自動化行為
4. 驗證碼 (Tencent CAPTCHA) 頻繁觸發

**替代方案**：
- 使用 NoDriver 手動登入後保持 session
- 登入狀態可能保持至 session 過期

---

## 7. 注意事項

1. **驗證碼**：登入頁面有圖形/聲音驗證碼，需人工處理
2. **智方便**：支援香港「智方便」(iAM Smart) 電子身份登入
3. **非會員購票**：可選擇非會員方式購票，無需登入
4. **排隊系統**：高流量時會進入排隊頁面

---

## 更新紀錄

| 日期 | 內容 |
|------|------|
| 2026-01-12 | 初次分析登入頁面和首頁結構 |
| 2026-01-12 | 新增 event-detail 頁面 MCP 快照分析 |
| 2026-01-12 | 新增 Cookie 與 API 認證機制分析 |
| 2026-01-12 | 新增 Tencent CAPTCHA 驗證碼資訊 |
| 2026-01-12 | Cookie 快速登入可行性分析：不建議 |
