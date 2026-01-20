# Issue #193 深入分析報告

**Issue**: [BUG] 拓元購票成功后持續多次打開 checkout 窗口
**回報者**: Hwang-HAHA
**版本**: v2025.12.15
**平台**: TixCraft

---

## 問題摘要

使用者回報購票成功後，程式持續無限次打印 `Ticket purchase successful` 訊息，並可能無限次開啟 checkout 視窗。

---

## 問題日誌分析

```
https://tixcraft.com/ticket/checkout
bot elapsed time: 12.203
Ticket purchase successful, please check order at: https://tixcraft.com/ticket/checkout
TixCraft ticket purchase completed
Ticket purchase successful, please check order at: https://tixcraft.com/ticket/checkout  ← 重複
Ticket purchase successful, please check order at: https://tixcraft.com/ticket/checkout  ← 重複
... (無限重複)
```

**關鍵觀察**：
1. `bot elapsed time: 12.203` - 計時只輸出一次（正確）
2. `TixCraft ticket purchase completed` - 完成訊息輸出（正確）
3. `Ticket purchase successful...` - **無限重複輸出（Bug）**

---

## 根因定位

### Bug 位置
**檔案**: `src/nodriver_tixcraft.py`
**行號**: 6385

### 問題代碼

```python
# 第 6378-6389 行
# Always set is_quit_bot when checkout page is detected (not just in headless mode)
if not tixcraft_dict["is_popup_checkout"]:     # ✅ 正確：只執行一次
    is_quit_bot = True
    tixcraft_dict["is_popup_checkout"] = True

# Headless-specific behavior: open checkout URL in new browser window
if config_dict["advanced"]["headless"]:
    if tixcraft_dict["is_popup_checkout"]:     # ❌ BUG：缺少 NOT
        domain_name = url.split('/')[2]
        checkout_url = "https://%s/ticket/checkout" % (domain_name)
        print("Ticket purchase successful, please check order at: %s" % (checkout_url))
        webbrowser.open_new(checkout_url)
```

### 正確實作對照

**KKTIX（正確）- 第 2831 行**:
```python
if config_dict["advanced"]["headless"]:
    if not kktix_dict["is_popup_checkout"]:    # ✅ 使用 NOT，只執行一次
        # ... 執行一次的代碼 ...
        kktix_dict["is_popup_checkout"] = True
```

**iBon（正確）- 第 14859 行**:
```python
if config_dict["advanced"]["headless"]:
    if not ibon_dict["is_popup_checkout"]:     # ✅ 使用 NOT，只執行一次
        checkout_url = url
        print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
        webbrowser.open_new(checkout_url)
        ibon_dict["is_popup_checkout"] = True
```

---

## 問題流程圖

```
首次進入 checkout 頁面
    │
    ├─ 第 6379 行: is_popup_checkout = False?
    │       └─ 是 → 設定 is_quit_bot = True
    │              設定 is_popup_checkout = True
    │
    ├─ 第 6385 行: is_popup_checkout = True?
    │       └─ 是 → 執行 print() + webbrowser.open_new()  ← 問題開始
    │
    ├─ 返回 is_quit_bot = True
    │
    ▼
主循環 (第 25094-25099 行)
    │
    ├─ 打印 "TixCraft ticket purchase completed"
    ├─ 重置 is_quit_bot = False  ← 主循環繼續！
    │
    ▼
再次調用 nodriver_tixcraft_main()
    │
    ├─ 仍在 checkout 頁面
    ├─ 第 6379 行: is_popup_checkout = True?
    │       └─ 否 → 跳過（不再設定 is_quit_bot）
    │
    ├─ 第 6385 行: is_popup_checkout = True?
    │       └─ 是 → 再次執行 print() + webbrowser.open_new()  ← 無限循環！
    │
    ▼
無限重複...
```

---

## 修復方案

### 修改位置
`src/nodriver_tixcraft.py` 第 6385 行

### 修改內容

**修改前**:
```python
if tixcraft_dict["is_popup_checkout"]:
```

**修改後**:
```python
if not tixcraft_dict["is_popup_checkout"]:
```

### 完整修復代碼

```python
# Headless-specific behavior: open checkout URL in new browser window
if config_dict["advanced"]["headless"]:
    if not tixcraft_dict["is_popup_checkout"]:  # 修復：加入 NOT
        domain_name = url.split('/')[2]
        checkout_url = "https://%s/ticket/checkout" % (domain_name)
        print("Ticket purchase successful, please check order at: %s" % (checkout_url))
        webbrowser.open_new(checkout_url)
        tixcraft_dict["is_popup_checkout"] = True  # 移動到這裡確保只執行一次
```

---

## 影響範圍

- **平台**: TixCraft / Ticketmaster / IndieVox（tixcraft_family）
- **模式**: Headless 模式（`config_dict["advanced"]["headless"] = True`）
- **使用者設定**: 使用者需啟用 headless 模式才會觸發此 Bug

---

## 驗證條件

修復後應符合以下條件：
1. `Ticket purchase successful...` 訊息只輸出一次
2. `webbrowser.open_new()` 只執行一次
3. 程式在 checkout 頁面應停止自動操作（is_quit_bot 邏輯保持不變）

---

## 相關設定

使用者日誌中的設定：
- `away_from_keyboard_enable: True` - OCR 自動提交已啟用
- `webdriver_type: nodriver` - 使用 NoDriver
- 可能啟用了 headless 模式

---

## 建議優先度

**高優先度** - 核心購票流程問題，會導致：
1. Console 輸出被大量無用訊息淹沒
2. 可能無限開啟瀏覽器視窗/分頁
3. 系統資源耗盡

---

## 修復確認清單

- [ ] 修改 `src/nodriver_tixcraft.py` 第 6385 行
- [ ] 確認其他 tixcraft_family 平台使用相同邏輯
- [ ] 測試 headless 模式下的購票流程
- [ ] 確認 `is_popup_checkout` 只被設定一次
