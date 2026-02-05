# 快速開始：FANSI GO 平台支援

**功能分支**：`012-fansigo-platform`
**建立日期**：2026-02-05

---

## 使用步驟

### 1. 設定目標活動

在設定中填入 FANSI GO 活動或購票頁網址：

```json
{
  "homepage": "https://go.fansi.me/events/590002"
}
```

**支援的網址格式**：
- 活動頁：`https://go.fansi.me/events/{eventId}`
- 購票頁：`https://go.fansi.me/tickets/show/{showId}`

### 2. 設定場次關鍵字（如有多場次）

若活動有多個場次（如高雄場、台北場），設定場次關鍵字：

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "高雄"
  }
}
```

**支援的關鍵字類型**：
- 城市名稱：「高雄」「台北」「台中」
- 日期：「02/07」「2026/02/08」
- 場地名稱：「WAREHOUSE」「Pipe」

### 3. 設定票種關鍵字

設定要購買的票種：

```json
{
  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP"
  }
}
```

**常見票種關鍵字**：
- 「VIP」- 匹配 VIP 票種
- 「雙日」- 匹配雙日票
- 「單日」- 匹配單日票
- 「預售」- 匹配預售票

### 4. 設定購票數量

```json
{
  "ticket_number": 2
}
```

### 5. 設定 Cookie 登入（可選）

若需要登入（會員優惠、限定活動），設定 Cookie：

**取得 Cookie 步驟**：
1. 在瀏覽器登入 FANSI GO
2. 開啟開發者工具（F12）
3. 切換到 Application > Cookies > go.fansi.me
4. 複製 `FansiAuthInfo` 的值

```json
{
  "accounts": {
    "fansigo_cookie": "你的 FansiAuthInfo Cookie 值"
  }
}
```

### 6. 執行程式

```bash
python src/nodriver_tixcraft.py --input settings.json
```

---

## 完整設定範例

### 範例：購買普通隊長高雄場 VIP 票 2 張

```json
{
  "homepage": "https://go.fansi.me/events/590002",
  "ticket_number": 2,
  "date_auto_select": {
    "enable": true,
    "date_keyword": "高雄",
    "mode": "from top to bottom"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP",
    "mode": "from top to bottom"
  },
  "accounts": {
    "fansigo_cookie": ""
  }
}
```

---

## 注意事項

### 購票流程終點

程式會在**付款方式選擇頁面**自動停止，不會進行付款操作。
使用者需手動完成付款。

### Cloudflare 驗證

若遇到 Cloudflare 驗證頁面，請手動完成驗證，程式會自動繼續。

### Cookie 有效期

FansiAuthInfo Cookie 有效期為 **7 天**。過期後需重新登入並更新 Cookie。

### 無驗證碼

FANSI GO 平台目前不需要輸入驗證碼。

---

## 故障排除

### 問題：找不到符合的場次

**可能原因**：
- `date_keyword` 設定不正確
- 場次名稱與關鍵字不匹配

**解決方案**：
1. 檢查實際場次名稱
2. 調整關鍵字（嘗試日期、城市、場地名稱）
3. 設定 `date_auto_fallback: true` 使用自動選擇

### 問題：找不到符合的票種

**可能原因**：
- `area_keyword` 設定不正確
- 票種已售完或未開賣

**解決方案**：
1. 檢查實際票種名稱
2. 調整關鍵字
3. 確認票種狀態為「★ 熱賣中」

### 問題：Cookie 登入失敗

**可能原因**：
- Cookie 已過期
- Cookie 格式不正確

**解決方案**：
1. 重新登入 FANSI GO 並取得新 Cookie
2. 確認 Cookie 為完整的 URL Encoded 字串
