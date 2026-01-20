# tour.ibon.com.tw 新 UI 分析報告

**分析日期**：2025-12-23
**分析 URL**：`https://tour.ibon.com.tw/event/6909c1bda251122c730ccb97`
**狀態**：未支援（需要新增實作）

---

## 一、概述

ibon 推出了新的 `tour.ibon.com.tw` 購票系統，與現有的 `ticket.ibon.com.tw` 系統有顯著差異。新系統採用現代化的前端框架，UI 結構與元素選擇器完全不同。

### URL 結構對比

| 頁面類型 | 舊版 (`ticket.ibon.com.tw`) | 新版 (`tour.ibon.com.tw`) |
|----------|---------------------------|---------------------------|
| 活動詳情 | `/ActivityInfo/Details/{id}` | `/event/{eventId}` |
| 區域/票種選擇 | `/Event/{eventId}/{sessionId}` | `/event/{eventId}/options` |
| 結帳頁面 | `/EventBuy/{eventId}/{sessionId}/{areaId}` | `/event/{eventId}/checkout` |
| 登入系統 | 舊版 ibon 登入 | `huiwan.ibon.com.tw` 統一登入 |

---

## 二、現有程式碼支援度

### 目前的處理邏輯

**檔案**：`src/nodriver_tixcraft.py`
**位置**：第 14092-14099 行

```python
# https://tour.ibon.com.tw/event/e23010000300mxu
if 'tour' in url.lower() and '/event/' in url.lower():
    is_event_page = False
    if len(url.split('/'))==5:
        is_event_page = True
    if is_event_page:
        # ibon auto press signup
        await nodriver_press_button(tab, '.btn.btn-signup')
```

### 問題分析

1. **選擇器失效**：`.btn.btn-signup` 在新 UI 中不存在
2. **URL 判斷不足**：只匹配 `/event/{id}` 格式，不處理 `/options` 和 `/checkout`
3. **流程缺失**：沒有處理票種選擇、數量選擇、表單填寫、結帳流程

---

## 三、新 UI 頁面流程

```
1. 活動詳情頁 (/event/{eventId})
   ↓ 點擊「立即購票」
2. 票種選擇頁 (/event/{eventId}/options)
   ↓ 選擇數量 → 點擊「加入訂購」→ 點擊「確認付款方式」
3. 結帳頁面 (/event/{eventId}/checkout)
   ↓ 填寫資料 → 勾選同意 → 點擊「下一步」
4. 付款頁面
```

---

## 四、網頁元素標籤詳細記錄

### 4.1 活動詳情頁 (`/event/{eventId}`)

```
URL: https://tour.ibon.com.tw/event/{eventId}
```

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 活動標題 | `heading[level="1"]` | 活動名稱 | `h1` | 識別活動 |
| 活動時間 | `StaticText` | `2025/12/24 20:30` | - | 顯示資訊 |
| 活動地點 | `StaticText` | 場地名稱 | - | 顯示資訊 |
| **立即購票按鈕** | `button` | `立即購票` | `button:has-text("立即購票")` | **關鍵：進入購票流程** |

#### DOM 結構範例
```html
<main>
  <complementary>
    <button>立即購票</button>  <!-- 關鍵按鈕 -->
  </complementary>
</main>
```

---

### 4.2 票種選擇頁 (`/event/{eventId}/options`)

```
URL: https://tour.ibon.com.tw/event/{eventId}/options
```

#### 票種區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 票種標題 | `heading[level="4"]` | `預售票` | `h4` | 識別票種 |
| 票價 | `StaticText` | `票價：NT$ 500` | `text*="票價：NT$"` | 顯示價格 |
| 選擇數量標籤 | `StaticText` | `選擇數量` | - | 標籤 |
| **數量下拉選單** | `combobox` | `value="請選擇"` | `combobox[aria-label="選擇數量"]` | **關鍵：選擇票數** |
| 數量選項 1 | `option` | `value="1"` | - | 選項 |
| 數量選項 2 | `option` | `value="2"` | - | 選項 |
| ... | `option` | `value="3"` ~ `value="8"` | - | 選項 |
| **加入訂購按鈕** | `button` | `加入訂購` (初始 disabled) | `button:has-text("加入訂購")` | **關鍵：加入購物車** |
| 更多資訊按鈕 | `button` | `更多資訊` (expandable) | - | 展開詳情 |

#### 訂購確認區塊（點擊「加入訂購」後出現）

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 確認標題 | `heading[level="4"]` | `您將要訂購的票券` | - | 標題 |
| 副標題 | `heading[level="6"]` | `請確認內容後按下結帳按鈕` | - | 提示 |
| 票種名稱 | `heading[level="4"]` | `票種名稱` | - | 標題 |
| 票種 | `StaticText` | `票種：預售票` | - | 顯示 |
| 場次 | `StaticText` | `場次 --` | - | 顯示 |
| 票區 | `StaticText` | `票區 --` | - | 顯示 |
| 單價 | `StaticText` | `單價 NT$ 500` | - | 顯示 |
| 數量 | `StaticText` | `數量 2` | - | 顯示 |
| 小計 | `StaticText` | `小計 NT$ 1,000` | - | 顯示 |
| 刪除按鈕 | `button` | `刪除` | `button:has-text("刪除")` | 移除票券 |
| 訂購總價 | `StaticText` | `訂購總價 NT$ 1,000` | - | 顯示 |
| **確認付款方式按鈕** | `button` | `確認付款方式` | `button:has-text("確認付款方式")` | **關鍵：進入結帳** |

#### 側邊欄金額區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 總金額標籤 | `StaticText` | `總金額：` | - | 標籤 |
| 總金額值 | `StaticText` | `NT$ 1,000` | - | 動態更新 |
| 確認付款方式按鈕 | `button` | `確認付款方式` (disabled → enabled) | - | 側邊按鈕 |

#### DOM 結構範例
```html
<main>
  <!-- 票種選擇區 -->
  <heading level="4">預售票</heading>
  <StaticText>票價：NT$ 500</StaticText>
  <StaticText>選擇數量</StaticText>
  <combobox value="請選擇" expandable haspopup="menu">
    <option value="1">1</option>
    <option value="2">2</option>
    <!-- ... -->
    <option value="8">8</option>
  </combobox>
  <button disabled>加入訂購</button>  <!-- 選擇數量後啟用 -->

  <!-- 訂購確認區（動態出現） -->
  <heading level="4">您將要訂購的票券</heading>
  <button>確認付款方式</button>
</main>
```

---

### 4.3 結帳頁面 (`/event/{eventId}/checkout`)

```
URL: https://tour.ibon.com.tw/event/{eventId}/checkout
```

#### 訂單摘要區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 票種標題 | `heading[level="4"]` | `預售票` | - | 顯示 |
| 單價 | `StaticText` | `單價` + `NT$ 500` | - | 顯示 |
| 數量 | `StaticText` | `數量` + `2` | - | 顯示 |
| 小計 | `StaticText` | `小計 NT$` + `1,000` | - | 顯示 |

#### 優惠碼區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 優惠碼輸入框 | `textbox` | placeholder=`優惠或折扣碼` | `textbox[placeholder*="優惠"]` | 輸入折扣碼 |
| 使用按鈕 | `button` | `使用` | `button:has-text("使用")` | 套用折扣 |

#### 金額摘要區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 總額標籤 | `StaticText` | `總額` | - | 標籤 |
| 總額值 | `StaticText` | `1,000 元` | - | 顯示 |
| 應付金額標籤 | `StaticText` | `應付金額` | - | 標籤 |
| 應付金額值 | `StaticText` | `1,000 元` | - | 顯示 |

#### 訂票人資料區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| Email 欄位 | `textbox` | `readonly`, `required`, value=用戶 email | `textbox[aria-label*="Email"]` | 自動填入（唯讀） |
| **姓名欄位** | `textbox` | `required`, placeholder=`請留下您的真實姓名` | `textbox[aria-label*="真實姓名"]` | **必填：需自動填入** |
| **手機欄位** | `textbox` | `required`, placeholder=`請務必輸入正確手機號碼` | `textbox[aria-label*="手機號碼"]` | **必填：需自動填入** |

#### 取票方式區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 區塊標題 | `heading[level="6"]` | `請選擇取票方式` | - | 標題 |
| **電子票選項** | `radio` | `電子票`, `checked` (預設) | `radio[value="電子票"]` | 取票方式 |
| 紙本票選項 | `radio` | `紙本票` | `radio[value="紙本票"]` | 取票方式 |

#### 付款方式區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 區塊標題 | `heading[level="6"]` | `請選擇付款方式` | - | 標題 |
| **信用卡選項** | `radio` | `信用卡`, `checked` (預設) | `radio[value="信用卡"]` | 付款方式 |
| LINE Pay 選項 | `radio` | `LINE Pay` | `radio[value="LINE Pay"]` | 付款方式 |

#### 同意條款區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| **同意條款核取方塊** | `checkbox` | `我已詳閱活動資訊並同意ibon售票系統 隱私權政策暨資料蒐集處理及利用` | `checkbox[aria-label*="我已詳閱"]` | **必選：需自動勾選** |
| 隱私權政策連結 | `button` | `隱私權政策暨資料蒐集處理及利用` | - | 彈出說明 |

#### 提交區塊

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| **下一步按鈕** | `button` | `下一步`, `disabled` (初始) | `button:has-text("下一步")` | **關鍵：提交訂單** |

#### DOM 結構範例
```html
<main>
  <!-- 訂單摘要 -->
  <heading level="4">預售票</heading>

  <!-- 優惠碼 -->
  <textbox placeholder="優惠或折扣碼"></textbox>
  <button>使用</button>

  <!-- 訂票人資料 -->
  <group aria-label="訂票人 Email">
    <textbox readonly required value="user@example.com"></textbox>
  </group>
  <group aria-label="訂票人 真實姓名">
    <textbox required></textbox>
  </group>
  <group aria-label="訂票人 手機號碼">
    <textbox required></textbox>
  </group>

  <!-- 取票方式 -->
  <heading level="6">請選擇取票方式</heading>
  <radiogroup>
    <radio checked>電子票</radio>
    <radio>紙本票</radio>
  </radiogroup>

  <!-- 付款方式 -->
  <heading level="6">請選擇付款方式</heading>
  <radiogroup>
    <radio checked>信用卡</radio>
    <radio>LINE Pay</radio>
  </radiogroup>

  <!-- 同意條款 -->
  <checkbox>我已詳閱活動資訊並同意...</checkbox>

  <!-- 提交 -->
  <button disabled>下一步</button>
</main>
```

---

## 五、登入系統分析

### 統一登入 (`huiwan.ibon.com.tw`)

```
URL: https://huiwan.ibon.com.tw/huiwan/LoginHuiwan/UserLogin.aspx?taxid={id}&targeturl=https://tour.ibon.com.tw/oauth2
```

| 元素 | 類型 | 文字/屬性 | 選擇器建議 | 用途 |
|------|------|----------|-----------|------|
| 頁面標題 | `StaticText` | `請選擇登入方式` | - | 標題 |
| uniopen 登入按鈕 | `generic` (clickable) | `使用 uniopen 登入/註冊` | `text="使用 uniopen 登入/註冊"` | 主要登入 |
| Google 登入按鈕 | `generic` (clickable) | `使用 Google 登入` | `text="使用 Google 登入"` | OAuth 登入 |
| LINE 登入按鈕 | `generic` (clickable) | `使用 LINE 登入` | `text="使用 LINE 登入"` | OAuth 登入 |
| Apple 登入按鈕 | `generic` (clickable) | `Sign in with Apple` | `text="Sign in with Apple"` | OAuth 登入 |

### 現有支援

**檔案**：`src/nodriver_tixcraft.py`
**位置**：第 13987 行

```python
if 'huiwan.ibon.com.tw/huiwan/loginhuiwan' in url.lower():
    # 目前只印出訊息，沒有實際處理
```

---

## 六、與現有 ibon 實作差異對比

| 功能 | 舊版 `ticket.ibon.com.tw` | 新版 `tour.ibon.com.tw` | 差異說明 |
|------|--------------------------|------------------------|---------|
| **票數選擇** | TR 表格 + 點擊按鈕 | combobox 下拉選單 | 完全不同的交互方式 |
| **區域選擇** | 有區域表格 | 無（直接選票種） | 流程簡化 |
| **驗證碼** | 有 `/pic.aspx` 圖片驗證碼 | 無驗證碼 | 無需 OCR 處理 |
| **結帳表單** | ASP.NET 傳統表單 | 現代化 SPA 表單 | 新的選擇器 |
| **登入** | 舊版 ibon 登入 | huiwan 統一登入 | 已部分支援 |
| **取票方式** | 無選項 | 電子票/紙本票 radio | 新增功能 |
| **付款方式** | 信用卡為主 | 信用卡/LINE Pay radio | 新增選項 |

---

## 七、實作建議

### 7.1 URL 判斷邏輯

```python
# 建議新增的 URL 判斷
if 'tour.ibon.com.tw' in url.lower():
    if '/event/' in url.lower():
        url_parts = url.split('/')

        # /event/{eventId} - 活動詳情頁
        if len(url_parts) == 5:
            await nodriver_tour_ibon_event_detail(tab, config_dict)

        # /event/{eventId}/options - 票種選擇頁
        elif 'options' in url.lower():
            await nodriver_tour_ibon_options(tab, config_dict)

        # /event/{eventId}/checkout - 結帳頁
        elif 'checkout' in url.lower():
            await nodriver_tour_ibon_checkout(tab, config_dict)
```

### 7.2 關鍵函數建議

#### 活動詳情頁處理
```python
async def nodriver_tour_ibon_event_detail(tab, config_dict):
    """處理 tour.ibon.com.tw 活動詳情頁"""
    # 點擊「立即購票」按鈕
    await nodriver_press_button(tab, 'button:has-text("立即購票")')
```

#### 票種選擇頁處理
```python
async def nodriver_tour_ibon_options(tab, config_dict):
    """處理 tour.ibon.com.tw 票種選擇頁"""
    ticket_number = config_dict.get("ticket_number", 2)

    # 1. 選擇票數（combobox）
    # 需要使用 CDP 或 fill 操作

    # 2. 點擊「加入訂購」
    await nodriver_press_button(tab, 'button:has-text("加入訂購")')

    # 3. 等待確認區塊出現
    await asyncio.sleep(0.5)

    # 4. 點擊「確認付款方式」
    await nodriver_press_button(tab, 'button:has-text("確認付款方式")')
```

#### 結帳頁處理
```python
async def nodriver_tour_ibon_checkout(tab, config_dict):
    """處理 tour.ibon.com.tw 結帳頁"""
    # 1. 填寫姓名（從 config 讀取）
    # 2. 填寫手機（從 config 讀取）
    # 3. 選擇取票方式（預設電子票）
    # 4. 選擇付款方式（預設信用卡）
    # 5. 勾選同意條款
    # 6. 點擊「下一步」
```

### 7.3 設定檔建議新增欄位

```json
{
  "tour_ibon": {
    "real_name": "使用者真實姓名",
    "phone": "0912345678",
    "ticket_type": "電子票",
    "payment_method": "信用卡"
  }
}
```

---

## 八、測試要點

1. **登入狀態**：確保 huiwan 登入 cookie 有效
2. **票種選擇**：combobox 操作是否正確
3. **按鈕狀態**：注意 disabled → enabled 的狀態變化
4. **表單驗證**：必填欄位是否正確填入
5. **同意條款**：checkbox 是否自動勾選

---

## 九、相關檔案

- **主程式**：`src/nodriver_tixcraft.py`
- **現有處理**：第 14092-14099 行（需修改）
- **登入處理**：第 13987 行（需擴充）
- **ibon 相關函數**：
  - `nodriver_ibon_main()` - 第 13964 行
  - `nodriver_ibon_event_area_auto_select()` - 第 11772 行
  - `nodriver_ibon_ticket_number_auto_select()` - 相關函數

---

## 十、參考資料

- [Shadow DOM Pierce Guide](./shadow_dom_pierce_guide.md)
- [NoDriver API Guide](../06-api-reference/nodriver_api_guide.md)
- [Ticket Automation Standard](../02-development/ticket_automation_standard.md)
