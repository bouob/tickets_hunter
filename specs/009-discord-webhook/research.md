# Research: Discord Webhook 通知

**分支**：`009-discord-webhook` | **日期**：2025-12-04 | **規格**：[spec.md](./spec.md)

---

## 1. 現有聲音通知系統分析

### 1.1 觸發函數

**主要函數**：`play_sound_while_ordering(config_dict)`
- **位置**：`src/nodriver_tixcraft.py` line 198
- **實作**：
```python
def play_sound_while_ordering(config_dict):
    app_root = util.get_app_root()
    captcha_sound_filename = os.path.join(app_root, config_dict["advanced"]["play_sound"]["filename"].strip())
    util.play_mp3_async(captcha_sound_filename)
```

**底層音訊函數**：`src/util.py` lines 296-311
```python
def play_mp3_async(sound_filename):
    threading.Thread(target=play_mp3, args=(sound_filename,)).start()

def play_mp3(sound_filename):
    from playsound import playsound
    try:
        playsound(sound_filename)
    except Exception as exc:
        if platform.system() == 'Windows':
            import winsound
            try:
                winsound.PlaySound(sound_filename, winsound.SND_FILENAME)
            except Exception as exc2:
                pass
```

### 1.2 防重複機制

系統使用 **平台狀態字典** 追蹤通知發送狀態：

```python
{platform}_dict = {
    "played_sound_ticket": False,  # 階段1鎖（找到票）
    "played_sound_order": False,   # 階段2鎖（購票成功）
}
```

**鎖定模式**：
```python
# 播放前檢查
if not played_sound_ticket:
    play_sound_while_ordering(config_dict)
# 播放後立即設定
played_sound_ticket = True
```

**重置機制**：離開結帳頁面時重置標記，允許下次購買重新播放
```python
if '/utk02/utk0206_.aspx' in url.lower():
    # 結帳頁面 - 播放音效
    if not ibon_dict["played_sound_order"]:
        play_sound_while_ordering(config_dict)
    ibon_dict["played_sound_order"] = True
else:
    # 離開結帳頁面 - 重置狀態
    ibon_dict["played_sound_order"] = False
    ibon_dict["played_sound_ticket"] = False
```

### 1.3 兩階段通知設計

| 階段 | 設定鍵 | 觸發時機 | 用途 |
|------|--------|----------|------|
| **Stage 1** | `play_sound.ticket` | 找到可購票券 | 提醒使用者票券可用 |
| **Stage 2** | `play_sound.order` | 進入結帳頁面 | 提醒使用者完成付款 |

### 1.4 平台實作矩陣

| 平台 | Stage 1 | Stage 2 | Stage 1 觸發點 | Stage 2 觸發點 |
|------|---------|---------|----------------|----------------|
| **iBon** | Yes | Yes | 購買按鈕點擊 | 結帳頁 URL 匹配 |
| **TixCraft** | Yes | Yes | 票券頁面載入 | 訂單確認頁 |
| **KKTIX** | Yes | Yes | 選票成功 | 確認頁面 |
| **KHAM** | No | Yes | - | 結帳頁面 |
| **Cityline** | Yes | No | 演出頁面 URL | - |
| **HKTicketing** | Yes | Yes | 票券頁面 | 確認頁面 |
| **TicketPlus** | No | Yes | - | 確認頁面 |

---

## 2. Settings 介面架構

### 2.1 HTML 結構模式

**檔案位置**：`src/www/settings.html`

**Tab 組織**：Bootstrap tabs，6 個主要區段
1. 使用需知
2. 基本設定
3. 進階設定 **← Discord webhook 應放這裡**
4. 驗證問題
5. 自動填表單
6. 執行階段

**表單欄位模式**：
```html
<div class="row mb-3">
  <label for="[id]" class="col-sm-2 col-form-label">[Label Text]</label>
  <div class="col-sm-10 col-lg-8 col-xl-6">
    <input class="form-control" id="[id]" value="" />
  </div>
</div>
```

**輔助說明模式**：
```html
<div class="form-text">
  [Help/explanation text for users]
</div>
```

### 2.2 JavaScript 儲存機制

**檔案位置**：`src/www/settings.js`

**主要流程**：
1. `save_changes_to_dict(silent_flag)` - 收集表單值到 settings 物件
2. `maxbot_save_api(callback)` - POST 到 `/save` 端點
3. `check_unsaved_fields()` - 追蹤未儲存變更

**元素宣告模式** (line ~27)：
```javascript
const fieldName = document.querySelector('#field-id');
```

**載入模式** (line ~167)：
```javascript
fieldName.value = settings.advanced.fieldName || '';
```

**儲存模式** (line ~404)：
```javascript
settings.advanced.fieldName = fieldName.value;
```

### 2.3 settings.json 結構

**現有 play_sound 結構**：
```json
"advanced": {
    "play_sound": {
        "ticket": false,
        "order": true,
        "filename": "assets/sounds/ding-dong.wav"
    }
}
```

**建議 Discord webhook 位置**：
```json
"advanced": {
    "play_sound": { ... },
    "discord_webhook_url": ""
}
```

---

## 3. HTTP 請求與錯誤處理

### 3.1 相依性確認

- **requests 庫**：已在專案中使用（`util.py`, `chrome_tixcraft.py`, `NonBrowser.py`）
- **threading 支援**：已有 `threading.Thread` 用於非阻塞操作

### 3.2 現有錯誤處理模式

**靜默處理模式**（用於外部服務）：
```python
def save_url_to_file(remote_url, ...):
    try:
        html_result = requests.get(remote_url, timeout=timeout)
    except Exception as exc:
        html_result = None
        # 靜默處理，不中斷流程
```

**Timeout 設定**：現有實作使用 0.5-0.7 秒

### 3.3 建議 Webhook 實作模式

```python
def send_discord_webhook_async(webhook_url, message_data, timeout=3):
    def _send():
        try:
            response = requests.post(webhook_url, json=message_data, timeout=timeout)
        except Exception as exc:
            if config_dict.get("advanced", {}).get("verbose"):
                print(f"Discord webhook send failed: {exc}")

    threading.Thread(target=_send, daemon=True).start()
```

---

## 4. 技術決策摘要

### 決策 1：Webhook URL 儲存位置

- **選擇**：`settings.json` → `advanced.discord_webhook_url`
- **理由**：
  - 與現有 `play_sound` 設定同層級
  - 簡單直覺，符合現有模式
  - 空字串表示停用
- **考慮的替代方案**：
  - ❌ 獨立通知物件：過度設計，此功能只需一個 URL
  - ❌ 多 webhook 支援：超出 spec 範圍

### 決策 2：非同步發送機制

- **選擇**：`threading.Thread` + `daemon=True`
- **理由**：
  - 與現有 `play_mp3_async` 模式一致
  - 不阻塞主搶票流程
  - daemon 執行緒在程式結束時自動清理
- **考慮的替代方案**：
  - ❌ `asyncio`：需要修改現有同步程式碼
  - ❌ `concurrent.futures`：過度複雜

### 決策 3：錯誤處理策略

- **選擇**：靜默處理 + verbose 模式日誌
- **理由**：
  - 符合 spec FR-008 要求
  - 與現有外部服務錯誤處理一致
  - verbose 模式可用於除錯
- **考慮的替代方案**：
  - ❌ 重試機制：spec 明確排除
  - ❌ 使用者通知失敗：可能干擾搶票

### 決策 4：防重複機制

- **選擇**：複用現有 `played_sound_*` 標記
- **理由**：
  - spec 明確要求「與現有音效防重複機制一致」
  - 無需新增狀態管理
- **考慮的替代方案**：
  - ❌ 獨立 webhook 標記：增加複雜度且 spec 要求一致

### 決策 5：Timeout 設定

- **選擇**：3 秒（符合 SC-003 要求）
- **理由**：
  - Discord API 通常在 1 秒內回應
  - 3 秒提供足夠緩衝
  - 失敗時主流程延遲 < 500ms（因為是非同步）
- **考慮的替代方案**：
  - ❌ 5 秒：過長
  - ❌ 1 秒：可能太短導致誤失敗

---

## 5. 整合點分析

### 5.1 需要修改的檔案

| 檔案 | 修改類型 | 說明 |
|------|----------|------|
| `src/settings.json` | 新增欄位 | `advanced.discord_webhook_url` |
| `src/www/settings.html` | 新增表單欄位 | Webhook URL 輸入框 |
| `src/www/settings.js` | 新增載入/儲存邏輯 | 處理新欄位 |
| `src/util.py` | 新增函數 | `send_discord_webhook_async()` |
| `src/nodriver_tixcraft.py` | 整合呼叫 | 在現有通知觸發點新增 webhook 呼叫 |

### 5.2 現有觸發點（需整合 webhook）

參考 1.4 平台實作矩陣，在每個 `play_sound_while_ordering()` 呼叫點旁新增 webhook 呼叫。

---

## 6. Discord Webhook API 參考

### 6.1 基本請求格式

```http
POST https://discord.com/api/webhooks/{webhook.id}/{webhook.token}
Content-Type: application/json

{
    "content": "訊息內容",
    "username": "Tickets Hunter",
    "embeds": [...]  // 可選
}
```

### 6.2 簡化訊息格式（本次實作）

```json
{
    "content": "[TixCraft] 找到票券！請儘速查看",
    "username": "Tickets Hunter"
}
```

### 6.3 Rate Limits

- 每個 webhook 每秒最多 30 次請求
- 搶票場景下不會觸及此限制

---

## 7. 風險評估

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|----------|
| Webhook URL 無效 | 中 | 低 | 靜默處理，不影響主流程 |
| Discord 服務中斷 | 低 | 低 | Timeout 機制 + 靜默處理 |
| 網路延遲 | 中 | 低 | 非同步發送 + 3秒 timeout |
| 重複發送 | 低 | 低 | 複用現有防重複機制 |

---

## 8. 已解決的「需要釐清」項目

| 項目 | 原始狀態 | 解決方案 |
|------|----------|----------|
| 觸發點位置 | 需要釐清 | 與現有 play_sound 相同位置 |
| 防重複機制 | 需要釐清 | 複用 `played_sound_*` 標記 |
| 設定介面整合 | 需要釐清 | 進階設定 Tab，play_sound 後方 |
| HTTP 庫選擇 | 需要釐清 | 使用現有 requests 庫 |
| 非同步機制 | 需要釐清 | threading.Thread (daemon) |
| 錯誤處理 | 需要釐清 | 靜默處理 + verbose 日誌 |
