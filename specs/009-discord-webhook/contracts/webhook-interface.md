# Webhook Interface: Discord Webhook 函數契約

**分支**：`009-discord-webhook` | **日期**：2025-12-04

---

## 1. 函數簽章

### 1.1 主要函數：`send_discord_webhook`

**位置**：`src/util.py`

```python
def send_discord_webhook(
    webhook_url: str,
    stage: str,
    platform_name: str,
    timeout: float = 3.0
) -> bool:
    """
    發送 Discord Webhook 通知。

    此函數為同步函數，會阻塞直到請求完成或超時。
    建議使用 send_discord_webhook_async() 進行非阻塞呼叫。

    Args:
        webhook_url: Discord Webhook URL
        stage: 通知階段 ("ticket" 或 "order")
        platform_name: 平台名稱 (如 "TixCraft", "iBon")
        timeout: 請求超時秒數，預設 3.0 秒

    Returns:
        bool: 發送成功返回 True，失敗返回 False

    Example:
        >>> send_discord_webhook(
        ...     "https://discord.com/api/webhooks/123/abc",
        ...     "ticket",
        ...     "TixCraft"
        ... )
        True
    """
    pass
```

### 1.2 非同步包裝函數：`send_discord_webhook_async`

**位置**：`src/util.py`

```python
def send_discord_webhook_async(
    webhook_url: str,
    stage: str,
    platform_name: str,
    timeout: float = 3.0
) -> None:
    """
    非同步發送 Discord Webhook 通知。

    使用背景執行緒發送，不阻塞主流程。
    失敗時靜默處理，不拋出異常。

    Args:
        webhook_url: Discord Webhook URL
        stage: 通知階段 ("ticket" 或 "order")
        platform_name: 平台名稱 (如 "TixCraft", "iBon")
        timeout: 請求超時秒數，預設 3.0 秒

    Returns:
        None（立即返回，不等待發送完成）

    Example:
        >>> send_discord_webhook_async(
        ...     "https://discord.com/api/webhooks/123/abc",
        ...     "ticket",
        ...     "TixCraft"
        ... )
        # 立即返回，背景執行緒處理發送
    """
    pass
```

### 1.3 訊息生成函數：`build_discord_message`

**位置**：`src/util.py`

```python
def build_discord_message(stage: str, platform_name: str) -> dict:
    """
    根據階段和平台名稱生成 Discord 訊息內容。

    Args:
        stage: 通知階段 ("ticket" 或 "order")
        platform_name: 平台名稱

    Returns:
        dict: Discord Webhook payload，包含 content 和 username

    Example:
        >>> build_discord_message("ticket", "TixCraft")
        {
            "content": "[TixCraft] 找到票券！請儘速查看電腦",
            "username": "Tickets Hunter"
        }
    """
    pass
```

---

## 2. 輸入驗證

### 2.1 webhook_url 驗證

| 輸入 | 處理方式 |
|------|----------|
| 空字串 `""` | 立即返回，不發送 |
| `None` | 立即返回，不發送 |
| 無效 URL | 嘗試發送，失敗後靜默處理 |
| 有效 URL | 正常發送 |

### 2.2 stage 驗證

| 輸入 | 處理方式 |
|------|----------|
| `"ticket"` | 生成「找到票券」訊息 |
| `"order"` | 生成「訂單成功」訊息 |
| 其他值 | 使用預設訊息 |

### 2.3 platform_name 驗證

| 輸入 | 處理方式 |
|------|----------|
| 非空字串 | 包含在訊息中 |
| 空字串或 `None` | 使用 "Unknown" 替代 |

---

## 3. 錯誤處理

### 3.1 異常類型與處理

| 異常類型 | 來源 | 處理方式 |
|----------|------|----------|
| `requests.Timeout` | 網路超時 | 靜默忽略，返回 False |
| `requests.ConnectionError` | 網路中斷 | 靜默忽略，返回 False |
| `requests.HTTPError` | Discord 返回錯誤 | 靜默忽略，返回 False |
| `Exception` | 其他未預期錯誤 | 靜默忽略，返回 False |

### 3.2 日誌記錄

- **verbose 模式啟用時**：記錄錯誤詳情到 stdout
- **verbose 模式停用時**：完全靜默

```python
# 錯誤處理範例
try:
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return True
except Exception as exc:
    if verbose:
        print(f"[Discord Webhook] Send failed: {exc}")
    return False
```

---

## 4. Discord API 契約

### 4.1 請求格式

```http
POST {webhook_url}
Content-Type: application/json

{
    "content": "{message_text}",
    "username": "Tickets Hunter"
}
```

### 4.2 預期回應

| HTTP 狀態碼 | 意義 | 處理方式 |
|-------------|------|----------|
| 200 | 成功 | 返回 True |
| 204 | 成功（無內容） | 返回 True |
| 400 | 請求錯誤 | 返回 False |
| 401 | 未授權 | 返回 False |
| 404 | Webhook 不存在 | 返回 False |
| 429 | Rate Limited | 返回 False |
| 5xx | 伺服器錯誤 | 返回 False |

### 4.3 Rate Limits

- Discord 限制：每個 webhook 每秒最多 30 次請求
- 本功能預期使用頻率：極低（每次搶票最多 2 次通知）
- 無需實作 rate limiting 邏輯

---

## 5. 整合點

### 5.1 呼叫位置（nodriver_tixcraft.py）

在現有 `play_sound_while_ordering()` 呼叫點旁新增：

```python
# 現有程式碼
if config_dict["advanced"]["play_sound"]["ticket"]:
    if not platform_dict.get("played_sound_ticket", False):
        play_sound_while_ordering(config_dict)
        platform_dict["played_sound_ticket"] = True

# 新增程式碼
webhook_url = config_dict.get("advanced", {}).get("discord_webhook_url", "")
if webhook_url and not platform_dict.get("played_sound_ticket", False):
    util.send_discord_webhook_async(webhook_url, "ticket", platform_name)
```

### 5.2 函數呼叫順序

1. 檢查防重複標記
2. 播放聲音（如果啟用）
3. 發送 Webhook（如果 URL 有效）
4. 設定防重複標記

**注意**：Webhook 發送應在設定標記之前，確保標記設定不受 webhook 結果影響。

---

## 6. 測試案例

### 6.1 單元測試

```python
def test_build_discord_message_ticket():
    result = build_discord_message("ticket", "TixCraft")
    assert result["content"] == "[TixCraft] 找到票券！請儘速查看電腦"
    assert result["username"] == "Tickets Hunter"

def test_build_discord_message_order():
    result = build_discord_message("order", "iBon")
    assert result["content"] == "[iBon] 訂單成功！請儘速結帳付款"

def test_send_webhook_empty_url():
    result = send_discord_webhook("", "ticket", "TixCraft")
    assert result == False

def test_send_webhook_invalid_url():
    result = send_discord_webhook("not-a-url", "ticket", "TixCraft")
    assert result == False
```

### 6.2 整合測試

需要實際 Discord Webhook URL 進行測試（手動測試）。
