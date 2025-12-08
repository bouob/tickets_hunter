# Config Schema: Discord Webhook 設定

**分支**：`009-discord-webhook` | **日期**：2025-12-04

---

## 1. JSON Schema 定義

### 1.1 新增欄位 Schema

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Discord Webhook Configuration",
    "description": "Discord Webhook 通知設定，整合至 settings.json 的 advanced 區塊",

    "properties": {
        "advanced": {
            "type": "object",
            "properties": {
                "discord_webhook_url": {
                    "type": "string",
                    "description": "Discord Webhook URL。空字串表示停用功能。",
                    "default": "",
                    "examples": [
                        "",
                        "https://discord.com/api/webhooks/1234567890/abcdefghijk"
                    ],
                    "pattern": "^(https://(discord\\.com|discordapp\\.com)/api/webhooks/.+)?$"
                }
            }
        }
    }
}
```

### 1.2 完整 advanced 區塊 Schema（含新增欄位）

```json
{
    "advanced": {
        "type": "object",
        "properties": {
            "play_sound": {
                "type": "object",
                "properties": {
                    "ticket": {
                        "type": "boolean",
                        "default": false,
                        "description": "找到票券時播放音效"
                    },
                    "order": {
                        "type": "boolean",
                        "default": true,
                        "description": "訂單成功時播放音效"
                    },
                    "filename": {
                        "type": "string",
                        "default": "assets/sounds/ding-dong.wav",
                        "description": "音效檔案路徑"
                    }
                },
                "required": ["ticket", "order", "filename"]
            },
            "discord_webhook_url": {
                "type": "string",
                "default": "",
                "description": "Discord Webhook URL，空字串表示停用"
            }
        }
    }
}
```

---

## 2. 設定檔範例

### 2.1 停用狀態（預設）

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

### 2.2 啟用狀態

```json
{
    "advanced": {
        "play_sound": {
            "ticket": true,
            "order": true,
            "filename": "assets/sounds/ding-dong.wav"
        },
        "discord_webhook_url": "https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz"
    }
}
```

---

## 3. 驗證規則

### 3.1 URL 格式驗證

| 輸入 | 有效性 | 說明 |
|------|--------|------|
| `""` | 有效 | 空字串表示停用 |
| `"https://discord.com/api/webhooks/123/abc"` | 有效 | 標準 discord.com 格式 |
| `"https://discordapp.com/api/webhooks/123/abc"` | 有效 | 舊版 discordapp.com 格式 |
| `"http://discord.com/api/webhooks/123/abc"` | 無效 | 必須是 HTTPS |
| `"https://example.com/webhook"` | 無效 | 必須是 Discord 網域 |
| `"not a url"` | 無效 | 不是有效 URL |

### 3.2 驗證行為

- **無效 URL**：靜默忽略，等同於停用功能
- **驗證時機**：發送前檢查，非設定儲存時
- **原因**：使用者可能先設定 URL 再建立 webhook，預先驗證會阻礙使用

---

## 4. 向後相容性

### 4.1 欄位不存在處理

```python
# 安全讀取模式
webhook_url = config_dict.get("advanced", {}).get("discord_webhook_url", "")
```

### 4.2 遷移說明

- **從舊版升級**：無需遷移，新欄位預設為空字串
- **降級至舊版**：新欄位被忽略，不影響功能

---

## 5. 與 settings.html 的對應

### 5.1 表單欄位 ID

| settings.json 路徑 | HTML 元素 ID | 類型 |
|-------------------|--------------|------|
| `advanced.discord_webhook_url` | `discord_webhook_url` | `<input type="text">` |

### 5.2 JavaScript 存取模式

```javascript
// 載入
discord_webhook_url.value = settings.advanced.discord_webhook_url || '';

// 儲存
settings.advanced.discord_webhook_url = discord_webhook_url.value;
```
