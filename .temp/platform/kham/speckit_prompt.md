# UDN 平台 speckit.specify 提示詞

複製以下內容並搭配 `/speckit.specify` 指令使用：

---

## 完整版提示詞

```
實作 UDN 售票網 (tickets.udnfunlife.com) 完整搶票自動化功能

## 背景資訊

UDN 售票網是 KHAM 家族成員，與 kham.com.tw、ticket.com.tw 共用相同的 UTK 後端系統。
現有程式碼已有部分 UDN 支援（場次選擇、票區選擇），但缺少關鍵的座位自動選擇功能。

## 參考網址
- 首頁：https://tickets.udnfunlife.com/application/utk01/utk0101_.aspx
- 演唱會範例：https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P12YQQ5C
- 活動範例二：https://tickets.udnfunlife.com/Application/UTK02/UTK0201_.aspx?PRODUCT_ID=P13EVEWY
- 活動範例三：https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P0ZS0ZFD&kdid=A05

## 功能需求

### 1. 座位自動選擇（核心新功能）
UDN 採用「逐位選擇」模式，點擊票區後會彈出座位圖，需要手動點選座位。
- 自動偵測彈出的選位視窗
- 根據 ticket_number 設定自動選擇指定數量的空位
- 座位選擇策略：優先選擇前排、中間位置
- 支援連號座位優先選擇（相鄰座位）
- 處理座位狀態：空位（可選）、已售出（跳過）、已被選擇、已加入購物車

### 2. 強化現有功能
- 場次選擇：優化 `div.yd_session-block` 選擇器
- 票區選擇：優化 `table.status > tr.status_tr` 選擇器
- 「前往購票」按鈕：處理 `div.goNext` 點擊
- 驗證「已售完」（Soldout class）票區過濾

### 3. 完整購票流程
確保完整購票流程：
- UTK0201：活動頁 → 點擊「立即購票」或「快速訂購」
- UTK0203：場次選擇 → 日期關鍵字匹配 → 點擊「前往購票」
- UTK0204_00：票區選擇 → 區域關鍵字匹配 → 點擊票區列
- 選位彈出視窗：自動選擇座位 → 加入購物車

### 4. 設定檔支援
確保 settings.json 相關設定正確應用：
- date_auto_select：日期自動選擇（關鍵字匹配）
- area_auto_select：區域自動選擇（關鍵字匹配）
- ticket_number：購票數量
- auto_select_mode：選擇模式（random/order/reverse）
- udn_account / udn_password：UDN 登入帳密

## 技術參考

### 現有 KHAM 實作（可參考）
- `nodriver_kham_date_auto_select()`：場次選擇邏輯
- `nodriver_kham_area_auto_select()`：票區選擇邏輯
- `nodriver_kham_main()`：主流程控制

### UDN 特有選擇器
- 場次區塊：`div.yd_session-block`
- 前往購票按鈕：`div.goNext`
- 票區表格：`table.status`
- 票區列：`tr.status_tr`
- 售完標記：`class="Soldout"`
- 座位格子：`td[title]` 或 `LayoutTableCell[description]`

### 座位選擇 HTML 結構
```html
<td title="特B區-1排-1號" class="seat available">...</td>
<td title="特B區-1排-2號" class="seat sold">...</td>
```

## 開發約束

1. 遵循 NoDriver First 原則（憲法第 I 條）
2. 保持與現有 KHAM 邏輯的相容性
3. 使用設定驅動架構（憲法第 V 條）
4. reCaptcha 暫時跳過（UDN 使用 reCaptcha，非圖形驗證碼）
5. 程式碼禁止使用 emoji（Windows cp950 編碼限制）
```

---

## 精簡版提示詞

如果想聚焦在核心功能：

```
實作 UDN 售票網 (tickets.udnfunlife.com) 座位自動選擇功能

UDN 是 KHAM 家族成員（如 kham.com.tw）。現有實作已有場次/票區選擇，但缺少座位選擇。

核心需求：UDN 使用「逐位選擇」彈出視窗，需根據 ticket_number 自動點選空位。

參考資料：
- https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P12YQQ5C
- 現有程式碼：nodriver_tixcraft.py 中的 nodriver_kham_area_auto_select()

選擇器：
- 場次：div.yd_session-block
- 票區：table.status > tr.status_tr
- 購票按鈕：div.goNext
- 座位：彈出視窗中的 td[title]

約束：NoDriver First、禁用 emoji、settings.json 驅動
```

---

## 使用方式

1. 執行 `/speckit.specify`
2. 貼上上方提示詞（完整版或精簡版）
3. 依照 speckit 工作流程進行規格驅動開發
