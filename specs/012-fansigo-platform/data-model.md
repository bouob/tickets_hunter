# 資料模型：FANSI GO 平台支援

**功能分支**：`012-fansigo-platform`
**建立日期**：2026-02-05

---

## 實體定義

### 1. Event（活動）

**描述**：FANSI GO 上的一個活動，可能包含多個場次。

| 屬性 | 類型 | 說明 | 範例 |
|------|------|------|------|
| eventId | int | 活動唯一識別碼 | 590002 |
| name | str | 活動名稱 | "普通隊長 × HONEST" |
| organizer | str | 主辦單位 | "LUCKY RECORDS" |
| shows | list[Show] | 場次列表 | [...] |

**URL 模式**：`/events/{eventId}`

---

### 2. Show（場次）

**描述**：活動中的一個演出場次，包含日期、地點、票種資訊。

| 屬性 | 類型 | 說明 | 範例 |
|------|------|------|------|
| showId | int | 場次唯一識別碼 | 590003 |
| name | str | 場次名稱 | "高雄場 KAOHSIUNG" |
| datetime | str | 日期時間 | "2026/02/07 19:00" |
| venue | str | 場地名稱 | "LIVE WAREHOUSE" |
| address | str | 場地地址 | "803高雄市鹽埕區大義街2-5號C10" |
| sections | list[Section] | 票種列表 | [...] |

**URL 模式**：`/tickets/show/{showId}`

---

### 3. Section（票種）

**描述**：一個票種/區域，包含價格、數量、狀態資訊。

| 屬性 | 類型 | 說明 | 範例 |
|------|------|------|------|
| sectionId | int | 票種唯一識別碼 | 150103 |
| name | str | 票種名稱 | "限量雙日VIP優先票" |
| price | int | 票價（NTD） | 2400 |
| totalSupply | int | 剩餘票數 | 20 |
| maxSupply | int | 總票數 | 50 |
| category | str | 分類（如 VIP） | "VIP" |
| status | SectionStatus | 販售狀態 | SectionStatus.ON_SALE |
| saleStart | datetime | 開賣時間 | "2026-02-01T04:00:00.000Z" |
| saleEnd | datetime | 結束時間 | "2026-03-12T16:00:00.000Z" |

**狀態列舉**：
```python
class SectionStatus(Enum):
    ON_SALE = "on_sale"       # ★ 熱賣中
    COMING_SOON = "coming"    # ⏱︎ 即將開賣
    ENDED = "ended"           # ☹︎ 你已太晚
    SOLD_OUT = "sold_out"     # 已售完
```

---

### 4. Order（訂單）

**描述**：購票訂單資訊。

| 屬性 | 類型 | 說明 | 範例 |
|------|------|------|------|
| orderId | str | 訂單識別碼 | "FG_260205_101602_0001" |
| status | str | 訂單狀態 | "pending_payment" |
| totalAmount | int | 總金額 | 4800 |
| items | list | 訂單項目 | [...] |

**orderId 格式**：`FG_YYMMDD_USERID_XXXX`

---

### 5. AuthInfo（認證資訊）

**描述**：Cookie 登入所需的認證資訊。

| 屬性 | 類型 | 說明 | 範例 |
|------|------|------|------|
| __typename | str | 類型標識 | "userToken" |
| accessToken | str | JWT Token | "eyJhbGciOiJIUzI1..." |
| tokenLife | int | 有效期（秒） | 604800 |

**Cookie 名稱**：`FansiAuthInfo`
**編碼方式**：URL Encoded JSON

---

## 狀態轉換

### 購票流程狀態

```
┌─────────────────────────────────────────────────────────────────┐
│                        購票流程狀態機                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [INIT] ──► [EVENT_PAGE] ──► [SHOW_PAGE] ──► [CHECKOUT]         │
│     │           │                │               │               │
│     │           │                │               └──► [DONE]     │
│     │           │                │                               │
│     │           ▼                ▼                               │
│     │      (選擇場次)       (選擇票種)                           │
│     │                       (設定數量)                           │
│     │                                                            │
│     └──► [ERROR] ◄─────────────────────────────────────────────  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**狀態說明**：
| 狀態 | URL 模式 | 動作 |
|------|----------|------|
| INIT | - | 初始化驅動、設定 Cookie |
| EVENT_PAGE | `/events/{eventId}` | 選擇場次 |
| SHOW_PAGE | `/tickets/show/{showId}` | 選擇票種、設定數量 |
| CHECKOUT | `/tickets/payment/checkout/*` | 停止（使用者付款） |
| DONE | - | 完成 |
| ERROR | - | 錯誤處理、重試 |

---

## 驗證規則

### Event
- `eventId` 必須為正整數
- `shows` 至少包含一個場次

### Show
- `showId` 必須為正整數
- `datetime` 格式為 "YYYY/MM/DD HH:MM"
- `sections` 至少包含一個票種

### Section
- `sectionId` 必須為正整數
- `price` 必須為非負整數
- `totalSupply` 必須 >= 0
- `totalSupply` 必須 <= `maxSupply`
- `status` 必須為有效的 SectionStatus 值

### AuthInfo
- `accessToken` 必須為有效的 JWT 格式
- `tokenLife` 必須為正整數
