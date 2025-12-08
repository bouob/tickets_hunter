# Data Model: Discord Webhook 通知

**分支**：`009-discord-webhook` | **日期**：2025-12-04 | **規格**：[spec.md](./spec.md)

---

## 1. 核心實體

### 1.1 Webhook 設定 (WebhookConfig)

**儲存位置**：`settings.json` → `advanced.discord_webhook_url`

```typescript
interface WebhookConfig {
    discord_webhook_url: string;  // Discord Webhook URL，空字串表示停用
}
```

**驗證規則**：
- 空字串或 `null`：停用 webhook 功能
- 非空字串：必須是有效 URL 格式（以 `https://discord.com/api/webhooks/` 或 `https://discordapp.com/api/webhooks/` 開頭）

**settings.json 片段**：
```json
{
    "advanced": {
        "play_sound": {
            "ticket": false,
            "order": true,
            "filename": "assets/sounds/ding-dong.wav"
        },
        "discord_webhook_url": ""
    }
}
```

### 1.2 通知事件 (NotificationEvent)

**僅存在於執行階段記憶體中**

```typescript
interface NotificationEvent {
    stage: "ticket" | "order";    // 觸發階段
    platform: string;              // 平台名稱 (TixCraft, iBon, KKTIX 等)
    message: string;               // 通知訊息
    timestamp: Date;               // 觸發時間（僅供日誌用）
}
```

**階段定義**：
| Stage | 名稱 | 觸發時機 |
|-------|------|----------|
| `ticket` | 找到票券 | 系統發現可購買的票券時 |
| `order` | 訂單成功 | 進入結帳/確認頁面時 |

### 1.3 通知狀態 (NotificationState)

**複用現有平台字典**

```typescript
// 各平台已有的狀態追蹤（無需新增）
interface PlatformDict {
    played_sound_ticket: boolean;  // 已發送 Stage 1 通知
    played_sound_order: boolean;   // 已發送 Stage 2 通知
    // ... 其他現有欄位
}
```

**決策說明**：Webhook 通知與聲音通知共用相同的防重複標記，確保行為一致性。

---

## 2. 資料流程

### 2.1 設定載入流程

```
settings.json
    ↓ load
config_dict["advanced"]["discord_webhook_url"]
    ↓ validate
有效 URL 或空字串
```

### 2.2 通知發送流程

```
觸發事件（找到票/訂單成功）
    ↓ check
played_sound_{stage} == False?
    ↓ yes
建立 NotificationEvent
    ↓
發送聲音通知（現有邏輯）
    ↓
discord_webhook_url 非空?
    ↓ yes
非同步發送 Webhook
    ↓
設定 played_sound_{stage} = True
```

### 2.3 Discord API 請求格式

```typescript
interface DiscordWebhookPayload {
    content: string;           // 訊息內容
    username: string;          // 顯示名稱（固定為 "Tickets Hunter"）
}
```

**範例**：
```json
{
    "content": "[TixCraft] 找到票券！請儘速查看電腦",
    "username": "Tickets Hunter"
}
```

---

## 3. 狀態轉換圖

### 3.1 通知狀態機

```
                  ┌─────────────────────────────────────┐
                  │                                     │
                  ▼                                     │
    ┌─────────────────────────┐                        │
    │  IDLE                   │                        │
    │  played_sound_ticket=F  │                        │
    │  played_sound_order=F   │                        │
    └───────────┬─────────────┘                        │
                │ 找到票券                              │
                ▼                                      │
    ┌─────────────────────────┐                        │
    │  TICKET_NOTIFIED        │                        │
    │  played_sound_ticket=T  │                        │
    │  played_sound_order=F   │                        │
    └───────────┬─────────────┘                        │
                │ 進入結帳頁                            │
                ▼                                      │
    ┌─────────────────────────┐                        │
    │  ORDER_NOTIFIED         │                        │
    │  played_sound_ticket=T  │                        │
    │  played_sound_order=T   │                        │
    └───────────┬─────────────┘                        │
                │ 離開結帳頁                            │
                │ (重置狀態)                           │
                └──────────────────────────────────────┘
```

### 3.2 有效狀態轉換

| 當前狀態 | 事件 | 下一狀態 | 動作 |
|----------|------|----------|------|
| IDLE | 找到票券 | TICKET_NOTIFIED | 發送 Stage 1 通知 |
| IDLE | 進入結帳頁 | ORDER_NOTIFIED | 發送 Stage 2 通知 |
| TICKET_NOTIFIED | 進入結帳頁 | ORDER_NOTIFIED | 發送 Stage 2 通知 |
| TICKET_NOTIFIED | 找到票券 | TICKET_NOTIFIED | 無動作（已通知） |
| ORDER_NOTIFIED | 任何事件 | ORDER_NOTIFIED | 無動作（已通知） |
| ORDER_NOTIFIED | 離開結帳頁 | IDLE | 重置狀態 |

---

## 4. 不變性約束 (Invariants)

### 4.1 設定不變性

1. **I-001**：`discord_webhook_url` 必須是字串類型
2. **I-002**：有效 URL 必須以 `https://discord.com/api/webhooks/` 或 `https://discordapp.com/api/webhooks/` 開頭
3. **I-003**：空字串視為停用，不發送任何 webhook

### 4.2 執行階段不變性

1. **I-004**：同一階段（ticket/order）在狀態重置前只發送一次通知
2. **I-005**：Webhook 發送失敗不得影響 `played_sound_*` 標記設定
3. **I-006**：Webhook 發送必須是非阻塞的（使用背景執行緒）
4. **I-007**：Webhook 超時必須 <= 3 秒（符合 SC-003）

### 4.3 訊息內容不變性

1. **I-008**：訊息必須包含平台名稱
2. **I-009**：訊息必須包含明確提醒文字
3. **I-010**：`username` 固定為 "Tickets Hunter"

---

## 5. 平台訊息範本

### 5.1 Stage 1（找到票券）

| 平台 | 訊息內容 |
|------|----------|
| TixCraft | `[TixCraft] 找到票券！請儘速查看電腦` |
| iBon | `[iBon] 找到票券！請儘速查看電腦` |
| KKTIX | `[KKTIX] 找到票券！請儘速查看電腦` |
| Cityline | `[Cityline] 找到票券！請儘速查看電腦` |
| HKTicketing | `[HKTicketing] 找到票券！請儘速查看電腦` |

### 5.2 Stage 2（訂單成功）

| 平台 | 訊息內容 |
|------|----------|
| TixCraft | `[TixCraft] 訂單成功！請儘速結帳付款` |
| iBon | `[iBon] 訂單成功！請儘速結帳付款` |
| KKTIX | `[KKTIX] 訂單成功！請儘速結帳付款` |
| KHAM | `[KHAM] 訂單成功！請儘速結帳付款` |
| Cityline | `[Cityline] 訂單成功！請儘速結帳付款` |
| HKTicketing | `[HKTicketing] 訂單成功！請儘速結帳付款` |
| TicketPlus | `[TicketPlus] 訂單成功！請儘速結帳付款` |

---

## 6. 與現有系統的關係

### 6.1 設定系統整合

```
settings.json
├── advanced
│   ├── play_sound          # 現有聲音通知設定
│   │   ├── ticket         # Stage 1 開關
│   │   ├── order          # Stage 2 開關
│   │   └── filename       # 音效檔案
│   └── discord_webhook_url # [新增] Webhook URL
```

### 6.2 通知邏輯整合

```python
# 概念性程式碼（非實際實作）
def notify(config_dict, platform_dict, stage, platform_name):
    flag_key = f"played_sound_{stage}"

    if platform_dict.get(flag_key, False):
        return  # 已通知，跳過

    # 聲音通知（現有邏輯）
    if config_dict["advanced"]["play_sound"][stage]:
        play_sound_while_ordering(config_dict)

    # Webhook 通知（新增邏輯）
    webhook_url = config_dict["advanced"].get("discord_webhook_url", "")
    if webhook_url:
        send_discord_webhook_async(webhook_url, stage, platform_name)

    # 設定標記
    platform_dict[flag_key] = True
```

---

## 7. 邊界案例處理

| 案例 | 處理方式 |
|------|----------|
| URL 為空字串 | 跳過 webhook 發送 |
| URL 格式錯誤 | 靜默忽略，記錄 verbose 日誌 |
| Discord 服務不可用 | 超時後靜默放棄 |
| 網路中斷 | 靜默失敗，不影響主流程 |
| 快速連續觸發 | 標記機制防止重複 |
| 程式異常中止 | daemon 執行緒自動清理 |
