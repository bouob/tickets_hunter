# 研究報告：FunOne Tickets 平台支援

**分支**：`011-funone-platform` | **日期**：2026-01-13 | **規格**：[spec.md](./spec.md)

## 摘要

本報告整理 FunOne Tickets 平台的技術研究成果，包含認證機制、頁面結構、API 分析及與現有專案整合方案。所有研究已完成，無待釐清事項。

## 1. 認證機制研究

### 1.1 登入方式

| 方式 | 說明 | 可自動化 |
|------|------|----------|
| 手機 OTP | 手機號碼 + 簡訊驗證碼 | ❌ 否（需實體手機） |
| QPP 掃碼 | QR Code 掃碼登入 | ❌ 否（需手機 App） |
| **Cookie 注入** | 注入 `ticket_session` | ✅ **可行（已驗證）** |

### 1.2 Cookie 快速登入（已驗證）

**必要 Cookie**：僅需 `ticket_session`

```python
# 驗證結果
[RESULT] SUCCESS - Logged in! Cookie login works with ticket_session only!
```

**Cookie 屬性**：

| 屬性 | 值 |
|------|-----|
| Name | `ticket_session` |
| Domain | `tickets.funone.io` |
| Path | `/` |
| HttpOnly | `true` |
| Secure | `false` |
| SameSite | `Lax` |
| Expires | 24 小時 |

**注入方法**（CDP）：

```python
import nodriver.cdp as cdp

await tab.send(cdp.network.set_cookie(
    name="ticket_session",
    value="<session_value>",
    domain="tickets.funone.io",
    path="/",
    secure=False,
    http_only=True
))
```

### 1.3 CSRF 防護

- Laravel 標準 CSRF 機制
- `XSRF-TOKEN` cookie 自動生成
- API 請求需帶 `x-xsrf-token` header
- NoDriver 自動處理，無需手動介入

## 2. 頁面結構分析

### 2.1 URL 路由

| 頁面 | URL 模式 |
|------|----------|
| 首頁 | `https://tickets.funone.io/` |
| 活動詳情 | `https://tickets.funone.io/activity/activity_detail/{activityId}` |
| 登入 | `https://tickets.funone.io/login?redirectPath=...` |
| 會員中心 | `https://tickets.funone.io/member` |
| 訂單 | `https://tickets.funone.io/member/order` |

### 2.2 關鍵元素選擇器

**活動詳情頁**：

| 元素 | 選擇器/識別方式 |
|------|----------------|
| 場次列表 | 日期 + 時間 + 場地按鈕 |
| 下一步按鈕 | `button` 含「下一步」文字 |

**選票頁面**：

| 元素 | 選擇器/識別方式 |
|------|----------------|
| 票種選擇 | 票種名稱按鈕 |
| 張數選擇 | 數字輸入或 +/- 按鈕 |
| 驗證碼圖片 | `img` 元素 |
| 驗證碼輸入 | `textbox` 元素 |
| 確認按鈕 | `button` 含確認文字 |

### 2.3 彈窗處理

- 活動公告彈窗：關閉按鈕
- 售罄提示：返回或重試
- 錯誤訊息：`alert` dialog

## 3. MCP 實測（2026-01-13）

### 3.1 測試環境

| 項目 | 說明 |
|------|------|
| 測試工具 | Chrome DevTools MCP |
| 測試日期 | 2026-01-13 |
| 測試網站 | https://tickets.funone.io/ |
| 測試狀態 | 未登入 |

### 3.2 首頁結構（已驗證）

**URL**: `https://tickets.funone.io/`

```
banner (導航列)
  ├─ logo (連結)
  ├─ 最新消息
  ├─ 常見問題
  ├─ 探索活動
  ├─ 搜尋 (textbox)
  └─ 登入/註冊 (連結)

精彩活動
  ├─ button「精選活動」
  ├─ button「即將開賣」
  └─ 活動卡片列表
      └─ link → activity_detail/{activityId}

最新消息
  └─ 活動公告列表

contentinfo (頁尾)
```

**關鍵發現**：
- 活動卡片為 `link` 元素，可直接點擊跳轉
- URL 格式：`/activity/activity_detail/{activityId}`
- 活動狀態標籤：「開賣中」、「即將開賣」

### 3.3 活動詳情頁結構（已驗證）

**URL**: `https://tickets.funone.io/activity/activity_detail/eztNJvpZvXmaqn`

**頁面資訊區**：

```
活動圖片
活動標題
├─ 活動日期
├─ 票價 (TWD格式)
├─ 主辦單位
└─ 類型 (演唱會/其他)

navigation (導航標籤)
├─ 活動資訊
├─ 購票方式
├─ 取票方式
├─ 退票方式
└─ 注意事項
```

**場次選擇區**：

```
活動場次
├─ 日期時間 (2026/02/01 14:30)
├─ 場地名稱 (Zepp New Taipei)
└─ button「下一步」
```

**關鍵發現**：
1. **「下一步」按鈕**：
   - 未登入狀態點擊會觸發登入檢查
   - 彈出對話框：「登入會員」
   - 對話框內容：「登入會員，加速報名流程，並且讓您的資料更有保障。」
   - 兩個選項：「返回」、「登入」

2. **票價顯示**：
   - 格式：`TWD 1,980 / 1,680 / 1,480 / 990`
   - 多個票種以斜線分隔

3. **場次資訊**：
   - 場次為單一按鈕（非列表）
   - 顯示完整日期時間和時區：`2026.02.01 (日) 14:30 (GMT+8)`

### 3.4 登入頁面結構（已驗證）

**URL**: `https://tickets.funone.io/login`

**頁面標題**：「以手機號碼/QPP登入」

**手機號碼登入區**：

```
手機號碼
├─ combobox (國碼選擇)
│   ├─ +886 Taiwan (預設)
│   ├─ +81 Japan
│   ├─ +82 South Korea
│   ├─ +852 Hong Kong
│   ├─ +66 Thailand
│   ├─ +63 Philippines
│   ├─ +65 Singapore
│   ├─ +60 Malaysia
│   ├─ +86 China
│   ├─ +853 Macau
│   └─ +84 Vietnam
├─ textbox「0912345678」
└─ button「發送」(初始 disabled)

簡訊驗證碼
├─ textbox「請輸入簡訊驗證碼」
└─ button「登入」(初始 disabled)
```

**QPP 掃碼登入區**：

```
or (分隔線)

掃描QRcode登入
├─ QR Code 圖片
├─ 倒數計時「1 分 55 秒後過期」
└─ link「下載QPP」→ https://www.qpptec.com/
```

**關鍵發現**：
1. **國碼支援**：11 個國家/地區
2. **按鈕狀態**：初始為 `disabled`，需輸入內容後啟用
3. **QR Code**：動態生成，約 2 分鐘過期
4. **無密碼登入**：僅支援 OTP 和 QPP，無傳統帳密

### 3.5 元素選擇器（MCP 驗證）

| 頁面 | 元素 | 選擇器/特徵 |
|------|------|-------------|
| 首頁 | 活動卡片 | `link` 包含 `activity_detail/` |
| 首頁 | 登入按鈕 | `link` 文字「登入/註冊」|
| 活動詳情 | 下一步按鈕 | `button` 文字「下一步」|
| 活動詳情 | 場次資訊 | StaticText 包含日期時間 |
| 登入頁 | 國碼選擇 | `combobox` 預設 `+886 Taiwan` |
| 登入頁 | 電話輸入 | `textbox` placeholder `0912345678` |
| 登入頁 | 驗證碼輸入 | `textbox` placeholder `請輸入簡訊驗證碼` |

### 3.6 購票流程驗證

**測試步驟**：
1. ✅ 訪問首頁 → 成功載入
2. ✅ 點擊活動卡片 → 跳轉到活動詳情頁
3. ✅ 點擊「下一步」→ 觸發登入檢查對話框
4. ✅ 訪問登入頁 → 顯示 OTP 和 QPP 登入選項

**結論**：購票流程需要登入後才能進入選票頁面，驗證了 Cookie 快速登入的必要性。

## 4. API 結構分析

### 4.1 已識別 API

| API | 方法 | 用途 |
|-----|------|------|
| `/Member/CheckToken` | POST | 檢查登入狀態 |
| `/api/ApiTicket/GetModelActiveInfoList` | POST | 取得活動資訊 |
| `/Ticket/GetArrangeActiveList` | POST | 取得票券清單 |
| `/api/ApiFront/GetNowTime` | POST | 取得伺服器時間 |

### 4.2 認證 Headers

```
x-xsrf-token: <XSRF-TOKEN cookie value>
x-requested-with: XMLHttpRequest
Content-Type: application/json
```

## 5. WebSocket 機制

### 5.1 用途

- 即時票務操作（選位、鎖票）
- 購票流程中維持連線

### 5.2 特點

- 多個 WebSocket 伺服器端點（負載平衡）
- 購票流程中自動建立連線
- NoDriver 無需手動處理

## 6. 現有專案整合方案

### 6.1 函數命名規範

依據現有專案模式：

```python
# 格式：nodriver_{platform}_{action}
nodriver_funone_main()
nodriver_funone_inject_cookie()
nodriver_funone_date_auto_select()
nodriver_funone_area_auto_select()
```

### 6.2 Cookie 注入模式（參考 TixCraft）

```python
# 現有模式（tixcraft_sid）
if len(tixcraft_sid) > 0:
    await tab.send(cdp.network.set_cookie(
        name="SID",
        value=tixcraft_sid,
        domain="tixcraft.com",
        path="/",
        secure=True,
        http_only=True
    ))
```

### 6.3 主程式整合點

在 `nodriver_tixcraft.py` 的 `main()` 函數（約第 24527 行後）：

```python
# FunOne 路由
if 'tickets.funone.io' in url:
    tab = await nodriver_funone_main(tab, url, config_dict)
```

### 6.4 設定檔整合

在 `settings.json` 的 `advanced` 區塊：

```json
"advanced": {
    "funone_session_cookie": "",
    "funone_ticket_number": 2
}
```

## 7. 風險與緩解

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| Session 過期（24hr） | 中 | UI 提醒用戶更新 Cookie |
| 圖形驗證碼 | 低 | 人工輸入等待 |
| WebSocket 斷線 | 中 | 購票流程內處理 |
| 高流量售罄 | 低 | 快速選票邏輯 |

## 8. 與其他平台對比

| 項目 | FunOne | TixCraft | Urbtix |
|------|--------|----------|--------|
| Cookie 快速登入 | ✅ 可行 | ✅ 可行 | ❌ 不建議 |
| 反爬蟲機制 | 無 | reCAPTCHA | Tencent WAF |
| 驗證碼時機 | 購票時 | 購票時 | 登入時 |
| 實作難度 | **低** | 低 | 中 |

## 9. 研究結論

### 9.1 已解決事項

- [x] Cookie 快速登入可行性（已驗證）
- [x] 必要 Cookie 識別（僅需 `ticket_session`）
- [x] 頁面結構分析（含 MCP 實測）
- [x] 登入檢查機制（MCP 實測驗證）
- [x] 元素選擇器確認（MCP 實測）
- [x] API 結構分析
- [x] 整合方案設計

### 9.2 待實作確認事項

- [ ] 階段 9（同意條款）是否需要實作（需實測）
- [ ] WebSocket 連線細節（實作時確認）

### 9.3 研究資料來源

| 文件/工具 | 位置/說明 |
|----------|----------|
| Cookie 研究報告 | `.temp/funone/cookie-login-research.md` |
| 技術評估報告 | `.temp/funone/nodriver-technical-assessment.md` |
| **MCP 實測** | **Chrome DevTools MCP（2026-01-13）** |

**MCP 實測成果**：
- ✅ 首頁結構驗證
- ✅ 活動詳情頁結構驗證
- ✅ 登入頁面結構驗證
- ✅ 登入檢查機制驗證
- ✅ 元素選擇器確認
- ✅ 購票流程驗證

---

**研究狀態**：✅ 完成（含 MCP 實測驗證，無待釐清事項）
