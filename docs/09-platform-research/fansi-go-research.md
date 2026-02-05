# FANSI GO (go.fansi.me) 事前研究報告

**研究日期**：2026-02-05
**網站網址**：https://go.fansi.me/
**網站名稱**：FANSI GO - 你值得更好的售票平台

---

## 1. 網站概述

FANSI GO 是一個台灣的售票平台，主打「Web3 ticketing and membership system」，提供：
- 演唱會數位票根
- 安全轉讓
- 專屬鐵粉優惠
- 二手票轉讓市場

主要服務小型音樂表演場所和獨立音樂人。

---

## 2. 技術架構

### 2.1 前端框架
- **Next.js** (React SSR/SSG 框架)
- 路由特徵：`/_next/static/chunks/`、`/_next/data/`
- 使用 SSG (Static Site Generation) 預渲染頁面

### 2.2 API 架構
- **GraphQL API**：`https://api.fansi.me/graphql`
- 所有資料查詢透過 GraphQL 進行

### 2.3 CDN 與靜態資源
| 用途 | 域名 |
|------|------|
| 主站 | `go.fansi.me` |
| API | `api.fansi.me` |
| 圖片 CDN | `img.fansi.me` |
| 靜態資源 | `fansi-static.s3.ap-southeast-1.amazonaws.com` |

### 2.4 第三方支付服務
| 服務 | URL |
|------|-----|
| 91APP 支付 | `checkout.payments.91app.com` |
| AFTEE 後支付 | `auth.aftee.tw`、`checkout.aftee.tw` |

---

## 3. 追蹤技術分析 (重點)

### 3.1 需封鎖的追蹤器

#### Google Tag Manager / Google Analytics
```
www.googletagmanager.com/gtag/js?id=G-JZTSR2SVFV
analytics.google.com/g/collect
stats.g.doubleclick.net/g/collect
www.google.com.tw/ads/ga-audiences
```

**封鎖建議**：
```python
BLOCK_DOMAINS = [
    "googletagmanager.com",
    "analytics.google.com",
    "stats.g.doubleclick.net",
    "google.com.tw/ads",
]
```

#### Smartlook (用戶行為錄製)
```
web-sdk.smartlook.com/recorder.js
web-sdk.smartlook.com/es6/init.*.js
```

**說明**：Smartlook 會錄製用戶的滑鼠移動、點擊、滾動等行為，可能會偵測自動化行為。

**封鎖建議**：
```python
BLOCK_DOMAINS.append("smartlook.com")
```

### 3.2 Cloudflare Bot 保護 (需特別處理)

網站使用 Cloudflare Challenge Platform：
```
go.fansi.me/cdn-cgi/challenge-platform/scripts/jsd/main.js
go.fansi.me/cdn-cgi/challenge-platform/h/b/scripts/jsd/*/main.js
```

**特徵**：
- 會發送 JavaScript challenge
- 可能會檢測瀏覽器指紋
- 需要完成 challenge 後才能正常訪問

**處理建議**：
- 使用 NoDriver (CDP) 可能需要處理 challenge
- 考慮使用 `stealth` 模式
- 不要封鎖這些請求，否則無法通過驗證

### 3.3 可保留的服務

| 服務 | URL | 說明 |
|------|-----|------|
| Google Sign-In | `accounts.google.com/gsi/client` | 登入功能 |
| 支付服務 | `91app.com`、`aftee.tw` | 結帳必要 |
| Google Fonts | `fonts.googleapis.com` | 字體載入 |

---

## 4. 頁面結構

### 4.1 URL 模式
| 頁面類型 | URL 格式 | 範例 |
|----------|----------|------|
| 首頁 | `/` | `https://go.fansi.me/` |
| 活動列表 | `/events/{eventId}` | `https://go.fansi.me/events/170125` |
| 購票頁面 | `/tickets/show/{showId}` | `https://go.fansi.me/tickets/show/170158` |
| 我的票券 | `/collection/tickets` | - |
| 二手市場 | `/market` | - |
| 個人收藏 | `/collection` | - |

### 4.2 頁面元素識別

#### 首頁
- 搜尋框：`textbox "搜尋活動"`
- 活動卡片：包含活動標題、日期、場地

#### 活動頁面 (`/events/{eventId}`)
- 場次連結：`link` 元素，包含場次資訊
- URL 格式：`/tickets/show/{showId}`

#### 購票頁面 (`/tickets/show/{showId}`) - 詳細元素結構

**頁面標題區**：
```
sectionheader
├── link (返回活動頁面)
└── heading level="3" "選擇票券種類"
```

**活動資訊區**：
```
generic
├── image "活動主視覺"
├── paragraph "主辦單位名稱"
├── heading level="1" "活動名稱"
└── generic "show venue info"
    ├── paragraph "場次名稱"
    ├── time "日期時間"
    ├── link "+ 行事曆"
    ├── paragraph "場地名稱"
    └── link "地址" (Google Maps)
```

**票種區域選擇器** (重要)：
```
generic
├── paragraph "選擇票券種類"
├── paragraph "★ 熱賣中"
├── list                              ← 票種列表容器 (一般票種)
│   ├── listitem level="1"            ← 單一票種
│   │   ├── heading level="3"         ← 票種名稱 (如 "雙日預售票")
│   │   ├── paragraph "詳細資訊"
│   │   ├── paragraph + time          ← 販售結束時間
│   │   └── generic
│   │       ├── generic "NT＄ XXX"    ← 價格
│   │       └── generic               ← 數量選擇器
│   │           ├── button (-)        ← 減少按鈕
│   │           ├── paragraph "0"     ← 目前數量
│   │           └── button (+)        ← 增加按鈕
│   └── listitem level="1"            ← 其他票種...
├── list                              ← 特殊區域票種 (如 VIP)
│   ├── generic
│   │   └── paragraph "VIP"           ← 【區域分類標題】
│   └── listitem level="1"            ← VIP 票種
│       └── heading "限量雙日VIP優先票"
├── paragraph "⏱︎ 即將開賣"
├── list (即將開賣票種)
├── paragraph "☹︎ 你已太晚"
└── list (已結束票種)
```

**多區域範例** (2026 野地晃晃 - showId: 150006)：
| 區域 | 票種名稱 | 價格 |
|------|----------|------|
| 一般 | 雙日預售票 | NT$ 2,000 |
| 一般 | 單日預售票 | NT$ 1,300 |
| VIP | 限量雙日VIP優先票 | NT$ 2,400 |

**票種狀態分類**：
| 狀態標示 | 說明 |
|----------|------|
| ★ 熱賣中 | 可購買的票種 |
| ⏱︎ 即將開賣 | 尚未開始販售 |
| ☹︎ 你已太晚 | 已結束販售 |

**NoDriver 選擇器範例**：
```python
# 選擇票種列表
ticket_list = await page.query_selector('list')

# 選擇特定票種 (透過票種名稱關鍵字匹配)
# 方法 1: 精確匹配
ticket_item = await page.query_selector('heading:has-text("單人預售票")')

# 方法 2: 部分匹配 (適用於關鍵字搜尋)
keyword = "VIP"
all_headings = await page.query_selector_all('listitem heading')
for heading in all_headings:
    text = await heading.get_text()
    if keyword in text:
        # 找到匹配的票種
        listitem = await heading.query_selector('xpath=ancestor::listitem')
        break

# 數量增加按鈕 (每個 listitem 內的最後一個 button)
plus_buttons = await page.query_selector_all('listitem button:last-child')

# 取得目前選擇數量
quantity_text = await page.query_selector('listitem paragraph')
```

**關鍵字匹配策略** (重要)：
```python
def find_ticket_by_keyword(ticket_list: list, keyword: str) -> dict:
    """
    根據關鍵字找到匹配的票種

    關鍵字範例：
    - "VIP" -> 匹配 "限量雙日VIP優先票"
    - "雙日" -> 匹配 "雙日預售票", "限量雙日VIP優先票"
    - "單日" -> 匹配 "單日預售票"
    - "預售" -> 匹配所有預售票
    """
    for ticket in ticket_list:
        if keyword.lower() in ticket['name'].lower():
            return ticket
    return None

# 票種資料結構範例 (從 GraphQL API 取得)
ticket_sections = [
    {"sectionId": 150101, "sectionName": "雙日預售票", "price": 2000, "totalSupply": 50},
    {"sectionId": 150102, "sectionName": "單日預售票", "price": 1300, "totalSupply": 100},
    {"sectionId": 150103, "sectionName": "限量雙日VIP優先票", "price": 2400, "totalSupply": 20},
]
```

**驗證碼**：❌ 無（此平台不需要輸入驗證碼）

---

## 5. 建議封鎖清單

### 5.1 完整封鎖域名列表
```python
FANSI_GO_BLOCK_DOMAINS = [
    # Google 追蹤
    "googletagmanager.com",
    "analytics.google.com",
    "stats.g.doubleclick.net",
    "google.com/ads",
    "google.com.tw/ads",

    # 行為錄製
    "smartlook.com",
    "web-sdk.smartlook.com",
]
```

### 5.2 不要封鎖的域名
```python
FANSI_GO_ALLOW_DOMAINS = [
    # 核心功能
    "go.fansi.me",
    "api.fansi.me",
    "img.fansi.me",
    "fansi-static.s3.ap-southeast-1.amazonaws.com",

    # 認證與支付
    "accounts.google.com",
    "checkout.payments.91app.com",
    "auth.aftee.tw",
    "checkout.aftee.tw",

    # Cloudflare (必要)
    # cdn-cgi 路徑不要封鎖

    # 字體
    "fonts.googleapis.com",
    "fonts.gstatic.com",
]
```

---

## 6. 開發注意事項

### 6.1 Cloudflare 挑戰
- 網站使用 Cloudflare Challenge Platform
- NoDriver 應能處理，但需確認 stealth 設定
- 如遇到持續挑戰，考慮增加等待時間

### 6.2 GraphQL API
- 所有資料透過 `api.fansi.me/graphql` 獲取
- 需要分析 GraphQL 請求結構
- 可能需要特定 headers 或 cookies

### 6.3 Next.js SSG
- 頁面資料透過 `/_next/data/` JSON 預載
- 範例：`/_next/data/{buildId}/events/170125.json`
- 可直接請求 JSON 獲取資料（如果不需要完整渲染）

### 6.4 登入機制 (重要) - 已實測驗證

**認證服務**：AWS Cognito Hosted UI
- **域名**：`fansidev.auth.ap-southeast-1.amazoncognito.com`
- **Client ID**：`2mbpinf4i15qa89o097lceqjd4`
- **OAuth 流程**：OAuth 2.0 + PKCE (S256)

**登入方式**：
1. Google OAuth 登入
2. Email/Password 登入（Cognito 內建）

**Cookie 登入支援**：✅ 是（已實測驗證）

#### Cookie 登入運作機制

```
用戶登入成功
      ↓
設置 FansiAuthInfo Cookie（包含 JWT）
      ↓
前端 JS 讀取 Cookie
      ↓
提取 accessToken
      ↓
API 請求自動帶上 Authorization: Bearer <token>
```

#### 關鍵 Cookie：`FansiAuthInfo`

| 屬性 | 值 |
|------|-----|
| Cookie 名稱 | `FansiAuthInfo` |
| 格式 | URL Encoded JSON |
| 有效期 | 7 天 (604800 秒) |
| Domain | `go.fansi.me` |
| Path | `/` |

**Cookie 內容結構**：
```json
{
  "__typename": "userToken",
  "accessToken": "<JWT_TOKEN>",
  "tokenLife": 604800
}
```

**JWT Payload 結構**：
```json
{
  "sub": "9ccf578d-3057-4f92-a5b3-2338f8618237",
  "exp": 1770884392,
  "iat": 1770279592,
  "jti": "a14eec31-4171-466e-a0f9-9fc083fbd65a",
  "client_id": "Fansi1101602",
  "username": "9ccf578d-3057-4f92-a5b3-2338f8618237",
  "walletAddress": ""
}
```

#### NoDriver 實作程式碼

```python
import json
from urllib.parse import quote

async def set_fansi_auth_cookie(browser, access_token: str):
    """設定 FANSI GO 登入 Cookie"""
    auth_info = {
        "__typename": "userToken",
        "accessToken": access_token,
        "tokenLife": 604800
    }

    cookie_value = quote(json.dumps(auth_info))

    await browser.cookies.set({
        "name": "FansiAuthInfo",
        "value": cookie_value,
        "domain": "go.fansi.me",
        "path": "/",
        "expires": int(time.time()) + 604800  # 7 天
    })

async def get_fansi_auth_token(browser) -> str:
    """從 Cookie 取得 Access Token"""
    cookies = await browser.cookies.get_all()
    for cookie in cookies:
        if cookie.get("name") == "FansiAuthInfo":
            decoded = unquote(cookie.get("value", ""))
            auth_info = json.loads(decoded)
            return auth_info.get("accessToken")
    return None
```

#### 登入狀態驗證

登入成功後，頁面會顯示以下導覽選項：
- 「我的票劵」
- 「個人蒐藏」
- 「二手票轉讓」
- 「購票攻略」

未登入時只顯示基本導覽。

### 6.5 票數查詢 API (重要)

**GraphQL 查詢票數**：

```graphql
query ShowSections($ids: [Int!]) {
  setting: FGGetEventInfo(ids: $ids, type: 41)
  sections: FGGetEventInfo(ids: $ids, type: 31)
}
```

**Request**：
```json
{
  "operationName": "ShowSections",
  "variables": { "ids": [170160] },
  "query": "query ShowSections($ids: [Int!]) { ... }"
}
```

**Response 關鍵欄位**：
```json
{
  "showId": 170160,
  "sectionName": "預售單人票",
  "sectionId": 170253,
  "price": "750.00",
  "totalSupply": 71,      // ← 剩餘票數
  "maxSupply": 200,       // ← 總票數
  "saleStart": "2026-02-01T04:00:00.000Z",
  "saleEnd": "2026-03-12T16:00:00.000Z",
  "sectionStatus": 1      // 1=販售中
}
```

**票數計算**：
- 剩餘票數：`totalSupply`
- 已售出：`maxSupply - totalSupply`
- 售完判斷：`totalSupply == 0` 或 `sectionStatus != 1`

**直接 API 呼叫範例**：
```bash
curl -X POST https://api.fansi.me/graphql \
  -H "Content-Type: application/json" \
  -d '{"operationName":"ShowSections","variables":{"ids":[170160]},"query":"query ShowSections($ids: [Int!]) { sections: FGGetEventInfo(ids: $ids, type: 31) }"}'
```

---

## 7. 購票流程 (重要)

**測試日期**：2026-02-05
**測試狀態**：✅ 完整流程已記錄

### 7.1 購票流程總覽

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FANSI GO 購票流程                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. 票券選擇頁面                                                     │
│     /tickets/show/{showId}                                          │
│     ↓ 選擇票種、數量、填寫購票人資訊                                 │
│                                                                      │
│  2. 取得訂單 (API)                                                   │
│     POST api.fansi.me/graphql (GetOrder mutation)                   │
│     ↓ 系統建立訂單                                                   │
│                                                                      │
│  3. 訂單確認頁面                                                     │
│     /tickets/payment/orderresult/{orderId}                          │
│     ↓ 確認訂單資訊                                                   │
│                                                                      │
│  4. 待付款清單                                                       │
│     /collection/pending                                              │
│     ↓ 可查看所有待付款訂單                                           │
│                                                                      │
│  5. 付款方式選擇 ← 【自動化停止點】                                  │
│     /tickets/payment/checkout/{orderId}                              │
│     ★ 程式碼到此頁面即完成任務                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 URL 路由對照表

| 階段 | URL 格式 | 說明 |
|------|----------|------|
| 票券選擇 | `/tickets/show/{showId}` | showId 為場次 ID |
| 訂單確認 | `/tickets/payment/orderresult/{orderId}?orderId={orderId}` | 建立訂單後跳轉 |
| 待付款清單 | `/collection/pending` | 未付款訂單列表 |
| 付款結帳 | `/tickets/payment/checkout/{orderId}` | **自動化終點** |

### 7.3 訂單 ID 格式

```
FG_YYMMDD_USERID_XXXX

範例: FG_260205_101602_0001
      │  │      │      │
      │  │      │      └── 當日流水號 (4 位數)
      │  │      └── 用戶 ID (6 位數)
      │  └── 日期 YYMMDD
      └── 前綴 FG (FANSI GO)
```

### 7.4 付款方式

到達付款頁面後，用戶可選擇以下付款方式：

| 付款方式 | 處理服務 |
|----------|----------|
| 信用卡付款 | 91APP |
| Apple Pay | 91APP |
| 街口支付 | 91APP |
| Line Pay | 91APP |
| 一卡通 iPass Money | 91APP |
| AFTEE 先享後付 | AFTEE |

### 7.5 自動化開發指引

**自動化範圍**：票券選擇 → 付款頁面

**自動化停止條件**：
- URL 匹配 `/tickets/payment/checkout/*`
- 或頁面出現付款方式選擇介面

**程式碼判斷範例**：
```python
def is_purchase_complete(current_url: str) -> bool:
    """判斷是否到達購票完成頁面（付款方式選擇）"""
    return "/tickets/payment/checkout/" in current_url

# 自動化主流程
async def auto_purchase(browser, show_id: int, ...):
    # ... 票券選擇流程 ...

    while True:
        current_url = await browser.get_url()
        if is_purchase_complete(current_url):
            print("已到達付款頁面，自動化任務完成")
            break
        # ... 繼續處理 ...
```

### 7.6 關鍵 API 請求

#### 取得訂單 (GetOrder)
```graphql
mutation GetOrder($input: OrderInput!) {
  createOrder(input: $input) {
    orderId
    totalAmount
    status
  }
}
```

#### 查詢訂單狀態
```graphql
query GetOrderStatus($orderId: String!) {
  order(orderId: $orderId) {
    orderId
    status
    paymentStatus
    items {
      sectionName
      quantity
      price
    }
  }
}
```

---

## 8. 後續研究項目

- [x] 分析 GraphQL API 請求結構
- [x] 測試登入流程
- [x] 測試 cookie 登入自動化（已驗證成功）
- [x] 確認購票流程的完整步驟（已記錄完整流程）
- [ ] 驗證 Cloudflare challenge 處理方式
- [ ] 測試 Smartlook 封鎖後是否影響功能

---

## 9. 參考資訊

### 8.1 網站技術指標
| 項目 | 值 |
|------|-----|
| Google Analytics ID | G-JZTSR2SVFV |
| Next.js Build ID | PNc2n2J_xEnQ1TWgOJ9md (動態) |
| Cloudflare | 啟用 Challenge Platform |

### 8.2 相關連結
- FAQ：https://sweet-angle-e85.notion.site/FAQ-45d76bebcf1c4c02888dbc457ab98b3d
- 合作夥伴頁面：https://go.fansi.me/promo

### 8.3 AWS Cognito 設定
| 項目 | 值 |
|------|-----|
| Region | ap-southeast-1 |
| User Pool Domain | fansidev.auth.ap-southeast-1.amazoncognito.com |
| Client ID | 2mbpinf4i15qa89o097lceqjd4 |
| Redirect URI | https://go.fansi.me/login |
| Scopes | email, openid, aws.cognito.signin.user.admin |

---

## 10. GraphQL API 參考

### 9.1 查詢票券資訊 (ShowSections)
```graphql
query ShowSections($ids: [Int!]) {
  setting: FGGetEventInfo(ids: $ids, type: 41)
  sections: FGGetEventInfo(ids: $ids, type: 31)
}
```

### 9.2 查詢用戶資訊 (GetUserEventInfo)
```graphql
query GetUserEventInfo($eventId: Int!) {
  me {
    id
    email
    name
    phone
    address
    gender
    birthday
    idNumber
  }
  purchased: getUserEventTicketsCount(eventId: $eventId)
  orderId: getOngoingOrders(eventId: $eventId)
  market: FGStatusCheck(type: 1, infoId: $eventId) {
    message
    data
    success
  }
}
```

**說明**：
- `me`: 登入用戶資訊（未登入為 null）
- `purchased`: 該活動已購買票數
- `orderId`: 進行中的訂單

---

## 11. 結論

| 問題 | 答案 | 驗證狀態 |
|------|------|----------|
| 支援 Cookie 登入？ | ✅ 是，使用 `FansiAuthInfo` Cookie | ✅ 已實測 |
| 有票數查詢 API？ | ✅ 是，透過 GraphQL `ShowSections` 查詢 | ✅ 已實測 |
| 需要封鎖追蹤器？ | ✅ Google Analytics、Smartlook | ✅ 已確認 |
| 有 Bot 保護？ | ⚠️ Cloudflare Challenge Platform | ⏳ 待測試 |

**Cookie 登入實測結果**：
- 只需設定 `FansiAuthInfo` Cookie 即可完成登入
- 前端會自動從 Cookie 提取 JWT Token
- API 請求自動帶上 `Authorization: Bearer <token>` header
- Token 有效期 7 天

**開發優先級建議**：
1. ~~實作票數查詢（無需登入）~~ ✅
2. ~~實作 cookie 登入機制~~ ✅
3. 測試購票流程
4. 處理 Cloudflare challenge

---

## 附錄 A：Cookie 登入實測記錄

**測試日期**：2026-02-05

### A.1 登入前 Cookie 狀態

```
_ga=GA1.1.2114411188.1770279111
_ga_JZTSR2SVFV=GS2.1.s1770279111$o1$g1$t1770279562$j60$l0$h0
```

僅有 Google Analytics cookies。

### A.2 登入後 Cookie 狀態

新增 `FansiAuthInfo`：
```
FansiAuthInfo=%7B%22__typename%22%3A%22userToken%22%2C%22accessToken%22%3A%22eyJhbGciOiJIUzI1NiIs...%22%2C%22tokenLife%22%3A604800%7D
```

### A.3 登出後 Cookie 匯入測試

**測試步驟**：
1. 用戶登出
2. 清除所有 cookies
3. 透過 JavaScript 設定 `FansiAuthInfo` cookie
4. 重新載入頁面

**測試結果**：✅ 成功

頁面顯示登入後的導覽選項，API 請求自動帶上 `Authorization: Bearer` header。

### A.4 API 請求驗證

登入成功後，GraphQL API 請求 headers：
```
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIs...
content-type: application/json
origin: https://go.fansi.me
```

### A.5 結論

Cookie 登入機制完全可行，只需保存並設定 `FansiAuthInfo` cookie 即可實現自動化登入。
