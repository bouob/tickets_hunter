# 音效通知系統 (Sound Notification System)

**文件說明**：說明 Tickets Hunter 的音效通知機制、兩階段音效設計、實作邏輯與程式碼範例
**最後更新**：2026-09-16

---

本文件說明搶票系統中的音效通知機制，包含兩階段音效設計、實作邏輯與程式碼範例。

---

## 📋 目錄

- [概述](#概述)
- [設定參數說明](#設定參數說明)
- [兩階段音效邏輯](#兩階段音效邏輯)
- [實作細節](#實作細節)
- [程式碼範例](#程式碼範例)
- [平台實作索引](#平台實作索引)
- [注意事項與最佳實踐](#注意事項與最佳實踐)

---

## 概述

### 設計理念

音效通知系統採用**兩階段通知設計**，分別在購票流程的兩個關鍵時刻提供音效回饋：

1. **階段 1：找到票（有票通知）** - 當系統找到可購買的票並嘗試進入結帳時
2. **階段 2：購票成功（訂單通知）** - 當系統真正到達結帳頁面並完成訂單時

### 為什麼需要兩階段？

在許多售票平台（如 ibon、KKTIX），從「找到票」到「購票成功」之間可能存在：
- **排隊機制**：需要等待其他使用者完成交易
- **座位分配延遲**：系統需要時間分配座位
- **網路延遲**：網頁導航需要時間
- **可能失敗**：排隊逾時、座位被搶走、系統錯誤等

因此，兩階段音效可以：
- ✅ **第一時間通知使用者**：有票時立即播放音效，使用者可以準備
- ✅ **確認最終結果**：真正購票成功時再次播放，避免誤判
- ✅ **區分狀態**：如果只聽到第一次音效但沒有第二次，表示排隊失敗

---

## 設定參數說明

### settings.json 設定結構

```json
{
  "advanced": {
    "play_sound": {
      "ticket": true,
      "order": true,
      "filename": "assets/sounds/ding-dong.wav"
    }
  }
}
```

### 參數詳解

| 參數 | 型別 | 說明 | 預設值 |
|------|------|------|--------|
| `ticket` | boolean | **有票時播放音效**<br>當找到可購買的票並點擊購買按鈕時播放 | `true` |
| `order` | boolean | **訂購完成時播放音效**<br>當成功到達結帳頁面（checkout）時播放 | `true` |
| `filename` | string | 音效檔案路徑（相對於專案根目錄） | `"assets/sounds/ding-dong.wav"` |

### 常見設定組合

#### 1. 兩階段都通知（推薦）
```json
"play_sound": {
  "ticket": true,
  "order": true
}
```
**適用情境**：希望在找到票和購票成功時都收到通知

#### 2. 只在購票成功時通知
```json
"play_sound": {
  "ticket": false,
  "order": true
}
```
**適用情境**：避免虛驚一場，只想在真正購票成功時收到通知

#### 3. 關閉所有音效
```json
"play_sound": {
  "ticket": false,
  "order": false
}
```
**適用情境**：無聲模式、測試環境

---

## 兩階段音效邏輯

### 階段 1：有票通知 (`play_sound.ticket`)

#### 觸發時機

當以下條件**全部滿足**時播放：

1. ✅ 已選擇日期、區域、票數
2. ✅ 已完成驗證碼填寫
3. ✅ **點擊購買按鈕成功**（`click_ret = True`）
4. ✅ `config_dict["advanced"]["play_sound"]["ticket"]` 為 `true`
5. ✅ 本次購票流程中尚未播放過（`ibon_dict["played_sound_ticket"] = False`）

#### 流程圖

```
┌─────────────────────────┐
│ 找到可購買的票         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 填寫驗證碼             │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 點擊購買按鈕 (成功)    │ ◄─── 階段 1 觸發點
└──────────┬──────────────┘
           │
           ▼
    🔊 播放 ticket 音效
           │
           ▼
┌─────────────────────────┐
│ 進入排隊/等待狀態      │
└─────────────────────────┘
```

#### 程式碼位置


---

### 階段 2：訂單通知 (`play_sound.order`)

#### 觸發時機

當以下條件**全部滿足**時播放：

1. ✅ URL 包含結帳頁面路徑（如 `/utk02/utk0206_.aspx`、`/order/status`）
2. ✅ `config_dict["advanced"]["play_sound"]["order"]` 為 `true`
3. ✅ 本次購票流程中尚未播放過（`ibon_dict["played_sound_order"] = False`）

#### 流程圖

```
┌─────────────────────────┐
│ 排隊中...              │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 成功分配座位           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 導航到結帳頁面         │ ◄─── 階段 2 觸發點
└──────────┬──────────────┘
           │
           ▼
    🔊 播放 order 音效
           │
           ▼
┌─────────────────────────┐
│ 購票完成！             │
└─────────────────────────┘
```

#### 程式碼位置

- **TicketPlus**：對應平台模組（`src/platforms/*.py`）
- **KHAM**：對應平台模組（`src/platforms/*.py`）
- **Ticket.com.tw**：對應平台模組（`src/platforms/*.py`）

---

### 完整流程範例

#### 成功購票流程

```
1. 找到票 → 點擊購買按鈕
   └─► 🔊 播放 ticket 音效 (階段 1)

2. 排隊中...（等待 5 秒）

3. 成功進入結帳頁面
   └─► 🔊 播放 order 音效 (階段 2)

總共播放 2 次音效
```

#### 排隊失敗流程

```
1. 找到票 → 點擊購買按鈕
   └─► 🔊 播放 ticket 音效 (階段 1)

2. 排隊中...（等待 30 秒）

3. ❌ 排隊超時，返回票券頁面
   └─► 🔇 不播放 order 音效

總共播放 1 次音效（告知有票，但未購票成功）
```

---

## 實作細節

### 防重複播放機制

使用全域字典 `{platform}_dict` 儲存播放狀態：

```python
# 以 ibon 為例
ibon_dict = {
    "played_sound_ticket": False,  # 階段 1 音效是否已播放
    "played_sound_order": False,   # 階段 2 音效是否已播放
}
```

### 狀態重置時機

當使用者**離開結帳頁面**時，重置所有音效狀態（允許下次購票重新播放）：

```python
if '/utk02/utk0206_.aspx' in url.lower():
    # 在結帳頁面：播放音效、觸發 idle
    # ...
else:
    # 離開結帳頁面：重置狀態
    ibon_dict["is_popup_checkout"] = False
    ibon_dict["played_sound_order"] = False
    ibon_dict["played_sound_ticket"] = False  # ← 重置！
    ibon_dict["shown_checkout_message"] = False
```

### 音效播放函式

```python
def play_sound_while_ordering(config_dict):
    """播放音效（非同步）"""
    app_root = util.get_app_root()
    captcha_sound_filename = os.path.join(
        app_root,
        config_dict["advanced"]["play_sound"]["filename"].strip()
    )
    util.play_mp3_async(captcha_sound_filename)
```

**特性**：
- 使用 `play_mp3_async`，不會阻塞主執行緒
- 支援 `.wav`、`.mp3` 格式
- 檔案路徑相對於專案根目錄

---

## 程式碼範例

### 範例 1：ibon 新版 EventBuy 頁面（階段 1）

```python
# 位置：nodriver_tixcraft.py 第 12097-12107 行

click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)

# Play sound if button clicked successfully
if click_ret:
    # Play "ticket" sound when attempting to enter checkout (found ticket)
    if config_dict["advanced"]["play_sound"]["ticket"]:
        if not ibon_dict.get("played_sound_ticket", False):
            play_sound_while_ordering(config_dict)
            ibon_dict["played_sound_ticket"] = True
    if show_debug_message:
        print("[NEW EVENTBUY] Purchase button clicked successfully")
```

**關鍵點**：
1. ✅ 檢查 `click_ret`（購買按鈕是否點擊成功）
2. ✅ 檢查 `play_sound.ticket` 設定
3. ✅ 檢查 `played_sound_ticket` 防重複
4. ✅ 播放後立即設定 `played_sound_ticket = True`

---

### 範例 2：ibon 結帳頁面（階段 2）

```python
# 位置：nodriver_tixcraft.py 第 12301-12333 行

# Check if reached checkout page (ticket purchase successful)
# https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
if '/utk02/utk0206_.aspx' in url.lower():
    # Show debug message (only once)
    if config_dict["advanced"].get("verbose", False):
        if not ibon_dict["shown_checkout_message"]:
            print("Reached checkout page - ticket purchase successful!")
        ibon_dict["shown_checkout_message"] = True

    # Play sound notification (only once)
    if config_dict["advanced"]["play_sound"]["order"]:
        if not ibon_dict["played_sound_order"]:
            play_sound_while_ordering(config_dict)
        ibon_dict["played_sound_order"] = True

    # If headless mode, open browser to show checkout page (only once)
    if config_dict["advanced"]["headless"]:
        if not ibon_dict["is_popup_checkout"]:
            checkout_url = url
            print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
            webbrowser.open_new(checkout_url)
            ibon_dict["is_popup_checkout"] = True

    # Trigger idle mode (only once)
    if not ibon_dict.get("triggered_idle", False):
        settings.maxbot_idle()
        if config_dict["advanced"].get("verbose", False):
            print("[INFO] Triggered maxbot_idle() - entering idle mode")
        ibon_dict["triggered_idle"] = True
else:
    # Reset status when leaving checkout page
    ibon_dict["is_popup_checkout"] = False
    ibon_dict["played_sound_order"] = False
    ibon_dict["played_sound_ticket"] = False  # ← 重置階段 1 狀態
    ibon_dict["shown_checkout_message"] = False
```

**關鍵點**：
1. ✅ URL 判斷（確認到達結帳頁面）
2. ✅ 檢查 `play_sound.order` 設定
3. ✅ 檢查 `played_sound_order` 防重複
4. ✅ `else` 區塊重置所有狀態（包括 `played_sound_ticket`）

---

### 範例 3：TixCraft 票券頁面（階段 1）

```python
# 位置：nodriver_tixcraft.py 第 3401-3407 行

# Play sound when ticket is available
if config_dict["advanced"]["play_sound"]["ticket"]:
    if not tixcraft_dict["played_sound_ticket"]:
        play_sound_while_ordering(config_dict)
    tixcraft_dict["played_sound_ticket"] = True
else:
    tixcraft_dict["played_sound_ticket"] = False
```

**注意**：
- TixCraft 在「找到票券頁面」時播放 `ticket` 音效
- 與 ibon 不同，TixCraft 不需要等到點擊按鈕

---

## 平台實作索引

### ibon

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 1 | 舊版 UTK0201 購買按鈕點擊 | 11949 行 | `play_sound.ticket` |
| 階段 1 | 新版 EventBuy 購買按鈕點擊 | 12102 行 | `play_sound.ticket` |
| 階段 1 | 舊版 UTK0201 購買按鈕點擊（另一流程） | 12249 行 | `play_sound.ticket` |
| 階段 2 | 到達結帳頁面 (UTK0206) | 12309 行 | `play_sound.order` |

### TixCraft

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 1 | 票券頁面（有票） | 3404 行 | `play_sound.ticket` |
| 階段 2 | 到達確認頁面 | 3436 行 | `play_sound.order` |

### KKTIX

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 1 | 票券頁面（有票） | 1715 行 | `play_sound.ticket` |
| 階段 2 | 到達確認頁面 | 1946 行 | `play_sound.order` |

### TicketPlus

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 2 | 到達確認頁面 | 6063 行 | `play_sound.order` |

**注意**：TicketPlus 目前僅實作階段 2 音效

### KHAM

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 2 | 到達結帳頁面 | 14924 行 | `play_sound.order` |

### Ticket.com.tw

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 2 | 訂單送出成功 | 17063 行 | `play_sound.order` |

### Cityline

| 階段 | 觸發點 | 程式碼位置 | 設定參數 |
|------|--------|-----------|---------|
| 階段 1 | 票券頁面（有票） | 13007 行 | `play_sound.ticket` |

**注意**：Cityline 目前僅實作階段 1 音效

---

## 注意事項與最佳實踐

### ⚠️ 常見錯誤

#### ❌ 錯誤 1：沒有檢查設定

```python
# ❌ 錯誤：無條件播放音效
if click_ret:
    play_sound_while_ordering(config_dict)
```

```python
# ✅ 正確：檢查設定
if click_ret:
    if config_dict["advanced"]["play_sound"]["ticket"]:
        if not ibon_dict.get("played_sound_ticket", False):
            play_sound_while_ordering(config_dict)
            ibon_dict["played_sound_ticket"] = True
```

---

#### ❌ 錯誤 2：共用防重複標記

```python
# ❌ 錯誤：階段 1 和階段 2 共用同一個標記
if click_ret:
    if config_dict["advanced"]["play_sound"]["ticket"]:
        if not ibon_dict.get("played_sound_order", False):  # ← 錯誤！
            play_sound_while_ordering(config_dict)
            ibon_dict["played_sound_order"] = True
```

**問題**：如果階段 1 播放後設定 `played_sound_order = True`，階段 2 就不會播放了！

```python
# ✅ 正確：各自使用獨立標記
# 階段 1 使用 played_sound_ticket
# 階段 2 使用 played_sound_order
```

---

#### ❌ 錯誤 3：忘記重置狀態

```python
# ❌ 錯誤：只重置 played_sound_order
else:
    ibon_dict["played_sound_order"] = False
    # 缺少 played_sound_ticket 重置！
```

```python
# ✅ 正確：重置所有狀態
else:
    ibon_dict["played_sound_order"] = False
    ibon_dict["played_sound_ticket"] = False  # ← 必須！
    ibon_dict["shown_checkout_message"] = False
```

---

### ✅ 最佳實踐

#### 1. 使用 `.get()` 方法避免 KeyError

```python
# ✅ 推薦：使用 .get() 提供預設值
if not ibon_dict.get("played_sound_ticket", False):
    # ...
```

#### 2. 保持一致的命名規範

```python
# 平台字典命名：{platform}_dict
ibon_dict = {}
tixcraft_dict = {}
kktix_dict = {}

# 狀態鍵命名
"played_sound_ticket"  # 階段 1
"played_sound_order"   # 階段 2
```

#### 3. 添加除錯訊息（可選）

```python
if click_ret:
    if config_dict["advanced"]["play_sound"]["ticket"]:
        if not ibon_dict.get("played_sound_ticket", False):
            if show_debug_message:
                print("[SOUND] Playing ticket notification")  # ← 除錯訊息
            play_sound_while_ordering(config_dict)
            ibon_dict["played_sound_ticket"] = True
```

#### 4. 確保音效檔案存在

```python
# 在程式啟動時驗證音效檔案
def validate_sound_file(config_dict):
    app_root = util.get_app_root()
    sound_file = os.path.join(
        app_root,
        config_dict["advanced"]["play_sound"]["filename"].strip()
    )
    if not os.path.exists(sound_file):
        print(f"[WARNING] Sound file not found: {sound_file}")
        return False
    return True
```

---

## 總結

### 核心原則

1. **兩階段獨立**：`ticket` 和 `order` 音效是獨立的兩個階段
2. **設定驅動**：所有音效播放必須檢查對應的設定參數
3. **防重複播放**：使用獨立的狀態標記防止重複播放
4. **狀態重置**：離開結帳頁面時重置所有音效狀態

### 檢查清單

在實作音效通知時，請確認：

- [ ] 階段 1 檢查 `config_dict["advanced"]["play_sound"]["ticket"]`
- [ ] 階段 2 檢查 `config_dict["advanced"]["play_sound"]["order"]`
- [ ] 階段 1 使用 `played_sound_ticket` 標記
- [ ] 階段 2 使用 `played_sound_order` 標記
- [ ] 播放前檢查標記狀態（防重複）
- [ ] 播放後立即設定標記為 `True`
- [ ] 離開結帳頁面時重置所有狀態
- [ ] 使用 `.get()` 方法避免 KeyError

---

## 相關文件

- [開發規範 (development_guide.md)](./development_guide.md)
- [程式碼範本 (coding_templates.md)](./coding_templates.md)
- [函式結構分析 (structure.md)](./structure.md)
- [邏輯流程圖 (logic_flowcharts.md)](./logic_flowcharts.md)

---

**文件版本**：v1.0
**最後更新**：2025-10-22
**維護者**：MaxBot 開發團隊
