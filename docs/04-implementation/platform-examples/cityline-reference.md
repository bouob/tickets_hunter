**文件說明**：Cityline (城市電腦售票) 平台的完整實作參考，涵蓋香港票務系統、多域名處理、Cloudflare Turnstile 驗證等技術實作指南。

**最後更新**：2025-12-02

---

# 平台實作參考：Cityline

## 平台概述

**平台名稱**：Cityline (城市電腦售票)
**網站**：
- `cityline.com` - 主站入口
- `shows.cityline.com` - 活動展示頁面
- `venue.cityline.com` - 購票流程頁面

**市場地位**：香港最大票務平台
**主要業務**：演唱會、音樂會、戲劇、體育賽事
**完成度**：85% ✅
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 完整的購票流程支援
- 多分頁自動關閉處理
- 廣告自動清除
- Cookie 接受處理

⚠️ **挑戰**：
- 多域名架構（cityline.com / shows.cityline.com / venue.cityline.com）
- Cloudflare Turnstile 驗證
- 登入模態對話框處理
- 按鈕等待啟用機制

### 特殊機制

1. **多域名架構**
   - `cityline.com/Events.html` - 首頁/登入
   - `shows.cityline.com` - 活動詳情頁面
   - `venue.cityline.com/eventDetail` - 日期選擇
   - `venue.cityline.com/performance` - 區域/票數選擇
   - `venue.cityline.com/shoppingBasket` - 購物車（成功頁面）

2. **按鈕等待機制**
   - 購票按鈕需等待啟用
   - 自動偵測按鈕狀態
   - 最長等待 60 秒

3. **登入模態對話框**
   - 購票過程中可能彈出登入提示
   - 自動偵測並處理 Cookie 注入

4. **多分頁處理**
   - 自動關閉彈出的第二分頁
   - 保持主分頁焦點

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_cityline_main()` | 15820 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_cityline_login()` | 14912 | 帳號登入 |
| Stage 2 | `nodriver_cityline_handle_login_redirect()` | 14971 | 登入後轉跳處理 |
| Stage 3 | `nodriver_cityline_cookie_accept()` | 15652 | Cookie 接受處理 |
| Stage 3 | `nodriver_cityline_clean_ads()` | 15767 | 廣告清除 |
| Stage 4 | `nodriver_cityline_date_auto_select()` | 15073 | 日期自動選擇 |
| Stage 4 | `nodriver_cityline_press_buy_button()` | 15684 | 購票按鈕點擊 |
| Stage 4 | `nodriver_cityline_purchase_button_press()` | 15607 | 購買按鈕點擊 |
| Stage 5 | `nodriver_cityline_area_auto_select()` | 15330 | 區域自動選擇 |
| Stage 6 | `nodriver_cityline_ticket_number_auto_select()` | 15452 | 票數自動設定 |
| Stage 8 | `nodriver_cityline_performance()` | 15531 | 整合處理（區域+票數+下一步）|
| Stage 10 | `nodriver_cityline_next_button_press()` | 15495 | 下一步按鈕 |
| Stage 10 | `nodriver_cityline_continue_button_press()` | 15272 | 繼續按鈕 |
| Stage 12 | `nodriver_cityline_check_shopping_basket()` | 15564 | 購物車頁面（成功偵測）|
| Util | `nodriver_cityline_check_login_modal()` | 15181 | 登入模態對話框檢測 |
| Util | `nodriver_cityline_close_second_tab()` | 15634 | 關閉第二分頁 |
| Util | `nodriver_cityline_auto_retry_access()` | 14898 | 自動重試存取 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## URL 路由表

| URL 模式 | 頁面類型 | 處理函數 |
|---------|---------|---------|
| `cityline.com/Events.html` | 首頁 | Cookie 接受 + 廣告清除 |
| `cityline.com/Login.html` | 登入頁面 | `nodriver_cityline_login()` |
| `shows.cityline.com/{event}` | 活動詳情 | `nodriver_cityline_press_buy_button()` |
| `venue.cityline.com/eventDetail` | 日期選擇 | `nodriver_cityline_purchase_button_press()` |
| `venue.cityline.com/performance` | 區域選擇 | `nodriver_cityline_performance()` |
| `venue.cityline.com/shoppingBasket` | 購物車 | 成功偵測 + 播放音效 |

---

## 特殊設計 1: 購票按鈕等待機制

### 挑戰

Cityline 的購票按鈕可能需要等待一段時間才會啟用（倒數計時）。

### 解決方案

```python
async def nodriver_cityline_press_buy_button(tab, config_dict):
    """等待並點擊購票按鈕"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    print("[CITYLINE] Waiting for buy ticket button to appear...")

    max_wait = 60  # 最長等待 60 秒
    check_interval = 0.5

    for attempt in range(int(max_wait / check_interval)):
        # 查找購票按鈕
        result = await tab.evaluate('''
            (function() {
                // 多種按鈕選擇器
                const selectors = [
                    'button.buy-ticket-btn',
                    'a.buy-btn',
                    'button[data-action="buy"]',
                    '.event-buy-btn'
                ];

                for (const selector of selectors) {
                    const btn = document.querySelector(selector);
                    if (btn) {
                        const isDisabled = btn.disabled ||
                                           btn.classList.contains('disabled') ||
                                           btn.getAttribute('aria-disabled') === 'true';

                        if (!isDisabled) {
                            btn.click();
                            return { clicked: true, selector: selector };
                        } else {
                            return { clicked: false, disabled: true };
                        }
                    }
                }
                return { clicked: false, notFound: true };
            })();
        ''')

        if result.get('clicked'):
            if show_debug_message:
                print(f"[CITYLINE] Buy button clicked via {result.get('selector')}")
            return True

        if result.get('disabled') and attempt % 10 == 0:
            print(f"[CITYLINE] Still waiting for button... ({attempt * check_interval:.1f}s elapsed)")

        await asyncio.sleep(check_interval)

    return False
```

---

## 特殊設計 2: 登入模態對話框處理

### 挑戰

在購票過程中，Cityline 可能彈出登入模態對話框，需要自動處理。

### 解決方案

```python
async def nodriver_cityline_check_login_modal(tab, config_dict):
    """檢查並處理登入模態對話框"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    result = await tab.evaluate('''
        (function() {
            // 查找登入模態對話框
            const modal = document.querySelector('.login-modal, .modal-login, #loginModal');
            if (modal && modal.style.display !== 'none') {
                // 查找登入按鈕（等待啟用）
                const loginBtn = modal.querySelector('button.login-btn, #loginBtn');
                if (loginBtn && !loginBtn.disabled) {
                    return { hasModal: true, buttonEnabled: true };
                }
                return { hasModal: true, buttonEnabled: false };
            }
            return { hasModal: false };
        })();
    ''')

    if result.get('hasModal'):
        if show_debug_message:
            print("[CITYLINE LOGIN MODAL] Login modal detected, waiting for button to be enabled...")

        # 等待按鈕啟用或使用者完成登入
        # ...
```

---

## 特殊設計 3: 多分頁處理

### 挑戰

Cityline 點擊某些按鈕會開啟新分頁，需要自動關閉以保持操作在主分頁。

### 解決方案

```python
async def nodriver_cityline_close_second_tab(tab, url):
    """關閉第二分頁，保持主分頁焦點"""

    try:
        # 取得所有分頁
        all_tabs = tab.browser.tabs

        if len(all_tabs) > 1:
            # 關閉非當前的分頁
            for other_tab in all_tabs:
                if other_tab != tab:
                    await other_tab.close()

            # 確保焦點回到主分頁
            await tab.activate()

    except Exception as exc:
        pass

    return tab
```

---

## 特殊設計 4: Cloudflare Turnstile 處理

### 挑戰

部分頁面使用 Cloudflare Turnstile 驗證，需要等待驗證完成。

### 解決方案

```python
# 等待 Cloudflare Turnstile 驗證完成
print("[CITYLINE DATE] Waiting 3 seconds for Cloudflare Turnstile...")
await asyncio.sleep(3.0)

# 檢查是否通過驗證
turnstile_result = await tab.evaluate('''
    (function() {
        // 檢查 Turnstile 狀態
        const turnstile = document.querySelector('[data-turnstile-response]');
        if (turnstile) {
            const response = turnstile.getAttribute('data-turnstile-response');
            return { verified: response && response.length > 0 };
        }
        return { verified: true };  // 沒有 Turnstile
    })();
''')
```

---

## 配置範例

```json
{
  "homepage": "https://shows.cityline.com/tc/2025/your-event.html",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "12/25",
    "mode": "random"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"A區\",\"B區\",\"C區\"",
    "mode": "random"
  },
  "ticket_number": 2,
  "advanced": {
    "verbose": true,
    "cityline_account": "your_email@example.com",
    "play_sound": {
      "ticket": true,
      "order": true
    }
  }
}
```

---

## 常見問題與解決方案

### Q1: 購票按鈕一直無法點擊？

**A**: 可能是倒數計時未結束或 Cloudflare 驗證未通過。

**檢查項目**：
1. 手動確認頁面上是否有倒數計時
2. 檢查是否有 Cloudflare 驗證提示
3. 啟用 `verbose` 查看等待狀態

### Q2: 登入後沒有轉跳到活動頁面？

**A**: 確認 `homepage` 設定正確。

**解決方案**：
1. 設定 `homepage` 為 `shows.cityline.com` 的活動頁面
2. 確認帳號已登入成功
3. 檢查是否有驗證阻擋

### Q3: 區域選擇失敗？

**A**: 關鍵字可能不匹配或區域已售完。

**解決方案**：
1. 啟用 `verbose` 查看可用區域
2. 調整 `area_keyword` 設定
3. 檢查是否有區域已售完提示

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 購票按鈕 | `button.buy-ticket-btn`, `.buy-btn` | shows.cityline.com |
| 購買按鈕 | `button.purchase-btn`, `.btn-purchase` | venue.cityline.com |
| 日期選項 | `.performance-item`, `.date-option` | eventDetail 頁面 |
| 區域選項 | `.seat-area`, `.area-btn` | performance 頁面 |
| 票數輸入 | `input.ticket-qty`, `select.qty-select` | performance 頁面 |
| 下一步按鈕 | `button.next-btn`, `.btn-next` | 各頁面 |
| Cookie 按鈕 | `button.accept-cookie`, `.cookie-accept` | 首頁 |
| 登入模態 | `.login-modal`, `#loginModal` | 彈出視窗 |

---

## 相關文件

- 📋 [Stage 4: 日期選擇機制](../../03-mechanisms/04-date-selection.md) - 日期選擇邏輯
- 📋 [Stage 5: 區域選擇機制](../../03-mechanisms/05-area-selection.md) - 區域選擇邏輯
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - Cityline 函數索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本功能支援 |
| v1.1 | 2025-08 | 多域名架構支援 |
| v1.2 | 2025-10 | Cloudflare Turnstile 處理 |
| **v1.3** | **2025-12** | **登入模態 + 多分頁處理** |

**v1.3 亮點**：
- ✅ 完整的多域名架構支援
- ✅ 購票按鈕等待機制（最長 60 秒）
- ✅ 登入模態對話框自動處理
- ✅ 多分頁自動關閉
- ✅ Cookie 接受 + 廣告清除
- ✅ 購物車成功偵測 + 音效播放
