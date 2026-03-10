# 平台實作參考：HKTicketing

**文件說明**：HKTicketing (香港快達票) 平台的完整實作參考，涵蓋雙架構支援（ASP.NET + SPA）、排隊處理、流量過載偵測等技術實作指南。
**最後更新**：2025-12-02

---

## 平台概述

**平台名稱**：HKTicketing (香港快達票)
**網站**：
- `hkticketing.com` - Type 01 傳統架構（ASP.NET）
- `hkt.hkticketing.com` - Type 02 新架構（Vue/React SPA）

**市場地位**：香港主要票務平台
**主要業務**：演唱會、音樂會、戲劇、體育賽事
**完成度**：90% ✅
**難度級別**：⭐⭐⭐⭐ (極高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 完整支援兩種架構（Type 01 + Type 02）
- 排隊頁面自動重導向
- 流量過載自動刷新
- 詳細的購票流程控制

⚠️ **挑戰**：
- 雙架構維護複雜度高
- Type 02 SPA 狀態管理
- 多種排隊/錯誤頁面處理
- 登入狀態跨頁面維護

### 架構說明

#### Type 01: 傳統 ASP.NET 架構
- **URL 特徵**：`hkticketing.com/shows/show.aspx?`
- **頁面結構**：伺服器端渲染
- **登入方式**：表單登入

#### Type 02: 新版 SPA 架構
- **URL 特徵**：`hkt.hkticketing.com/hant/#/`
- **頁面結構**：Vue/React SPA
- **登入方式**：localStorage Token
- **特殊處理**：流量過載偵測

### 特殊機制

1. **排隊頁面處理**
   - `queue.hkticketing.com` - 排隊頁面
   - 自動偵測並等待
   - 排隊結束後自動重導向

2. **流量過載偵測**（Type 02）
   - 自動偵測過載頁面
   - 自動點擊刷新按鈕
   - 等待後重新嘗試

3. **錯誤頁面處理**
   - `hotshow.html` - 熱門活動錯誤頁
   - 自動重導向回目標頁面

4. **iframe 錯誤處理**
   - 偵測 iframe 內的錯誤訊息
   - 自動跳出錯誤狀態

---

## 核心函數索引

### Type 01 (傳統架構) 函數

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Stage 2 | `nodriver_hkticketing_login()` | 21052 | 帳號登入 |
| Stage 3 | `nodriver_hkticketing_accept_cookie()` | 21212 | Cookie 接受 |
| Stage 4 | `nodriver_hkticketing_date_auto_select()` | 21518 | 日期自動選擇 |
| Stage 4 | `nodriver_hkticketing_date_assign()` | 21305 | 日期指定 |
| Stage 4 | `nodriver_hkticketing_date_buy_button_press()` | 21225 | 購買按鈕點擊 |
| Stage 5 | `nodriver_hkticketing_area_auto_select()` | 21561 | 區域自動選擇 |
| Stage 6 | `nodriver_hkticketing_ticket_number_auto_select()` | 21812 | 票數自動設定 |
| Stage 9 | `nodriver_hkticketing_ticket_delivery_option()` | 21876 | 配送方式選擇 |
| Stage 10 | `nodriver_hkticketing_next_button_press()` | 21920 | 下一步按鈕 |
| Stage 10 | `nodriver_hkticketing_go_to_payment()` | 21997 | 前往付款 |
| Stage 11 | `nodriver_hkticketing_performance()` | 23309 | 整合處理 |

### Type 02 (SPA 架構) 函數

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Stage 2 | `nodriver_hkticketing_type02_login()` | 22266 | SPA 登入 |
| Stage 2 | `nodriver_hkticketing_type02_check_login_status()` | 22205 | 登入狀態檢查 |
| Stage 3 | `nodriver_hkticketing_type02_check_traffic_overload()` | 22142 | 流量過載偵測 |
| Stage 3 | `nodriver_hkticketing_type02_clear_session()` | 22079 | 清除 Session |
| Stage 4 | `nodriver_hkticketing_type02_event_page()` | 22546 | 活動頁面處理 |
| Stage 4 | `nodriver_hkticketing_type02_date_assign()` | 22578 | 日期指定 |
| Stage 5 | `nodriver_hkticketing_type02_area_auto_select()` | 22716 | 區域自動選擇 |
| Stage 6 | `nodriver_hkticketing_type02_ticket_number_select()` | 22863 | 票數選擇 |
| Stage 8 | `nodriver_hkticketing_type02_performance()` | 22978 | 整合處理 |
| Stage 10 | `nodriver_hkticketing_type02_next_button_press()` | 22937 | 下一步按鈕 |
| Stage 10 | `nodriver_hkticketing_type02_confirm_order()` | 23029 | 確認訂單 |
| Util | `nodriver_hkticketing_type02_dismiss_modal()` | 22425 | 關閉模態對話框 |
| Util | `nodriver_hkticketing_type02_event_page_buy_button()` | 22480 | 活動頁購買按鈕 |

### 共用函數

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_hkticketing_main()` | 23524 | 主控制流程 |
| Util | `nodriver_hkticketing_url_redirect()` | 23362 | URL 重導向處理 |
| Util | `nodriver_hkticketing_content_refresh()` | 23423 | 內容刷新處理 |
| Util | `nodriver_hkticketing_travel_iframe()` | 23472 | iframe 錯誤處理 |
| Util | `nodriver_hkticketing_escape_robot_detection()` | 23344 | 機器人偵測規避 |
| Util | `nodriver_hkticketing_hide_tickets_blocks()` | 22052 | 隱藏票區塊 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## URL 路由表

### Type 01 (傳統架構)

| URL 模式 | 頁面類型 | 處理函數 |
|---------|---------|---------|
| `/Secure/ShowLogin.aspx` | 登入頁面 | `nodriver_hkticketing_login()` |
| `/Membership/Login.aspx` | 登入頁面 | `nodriver_hkticketing_login()` |
| `/shows/show.aspx?` | 日期選擇 | `nodriver_hkticketing_date_auto_select()` |
| `/events/.../performances/` | 區域選擇 | `nodriver_hkticketing_area_auto_select()` |

### Type 02 (SPA 架構)

| URL 模式 | 頁面類型 | 處理函數 |
|---------|---------|---------|
| `#/login` | 登入頁面 | `nodriver_hkticketing_type02_login()` |
| `#/allEvents/detail/{id}` | 活動頁面 | `nodriver_hkticketing_type02_event_page()` |
| `#/allEvents/detail/selectTicket?activityId=` | 票券選擇 | `nodriver_hkticketing_type02_performance()` |
| `#/confirmOrder` | 確認訂單 | `nodriver_hkticketing_type02_confirm_order()` |
| `#/generateSeat/{id}` | 結帳頁面 | 成功偵測 |

---

## 特殊設計 1: 流量過載偵測（Type 02）

### 挑戰

Type 02 架構在高流量時會顯示過載頁面，需要自動偵測並刷新。

### 解決方案

```python
async def nodriver_hkticketing_type02_check_traffic_overload(tab, config_dict=None):
    """檢查流量過載頁面"""

    result = await tab.evaluate('''
        (function() {
            // 檢查過載訊息
            const bodyText = document.body.textContent || '';
            const overloadKeywords = [
                'Traffic Overload',
                '流量過大',
                'Please try again',
                '請稍後再試'
            ];

            const hasOverload = overloadKeywords.some(kw => bodyText.includes(kw));

            if (hasOverload) {
                // 查找刷新按鈕
                const refreshBtn = document.querySelector('button.refresh, .btn-refresh, button[onclick*="refresh"]');
                if (refreshBtn) {
                    refreshBtn.click();
                    return { overload: true, refreshed: true };
                }
                return { overload: true, refreshed: false };
            }

            return { overload: false };
        })();
    ''')

    return result.get('overload', False)
```

---

## 特殊設計 2: 排隊頁面處理

### 挑戰

HKTicketing 有多種排隊/等待頁面：
- `queue.hkticketing.com` - 排隊系統
- `hotshow.html` - 熱門活動頁面

### 解決方案

```python
# 排隊頁面 URL 清單
QUEUE_URL_PATTERNS = [
    "Hi fans, you're in the queue to",
    'queue.hkticketing.com/hotshow.html',
]

# 熱門排隊 URL（hot0 到 hot19）
for i in range(20):
    QUEUE_URL_PATTERNS.append(f'queue.hkticketing.com/hot{i}.html')

async def nodriver_hkticketing_url_redirect(tab, url, config_dict):
    """處理 URL 重導向（排隊頁面、錯誤頁面）"""

    # 檢查是否在排隊頁面
    for pattern in QUEUE_URL_PATTERNS:
        if pattern in url.lower():
            print("[HKTICKETING] Queue page detected, waiting...")
            await asyncio.sleep(5)  # 等待 5 秒後重新檢查

            # 嘗試重導向回目標頁面
            homepage = config_dict.get("homepage", "")
            if homepage:
                await tab.get(homepage)
                return True

    return False
```

---

## 特殊設計 3: Type 02 登入流程

### 挑戰

Type 02 使用 localStorage 儲存登入狀態，需要特殊處理。

### 解決方案

```python
async def nodriver_hkticketing_type02_login(tab, config_dict):
    """Type 02 SPA 登入流程"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    print("[HKTICKETING TYPE02] Waiting for login to complete (max 180 seconds)...")

    timeout = 180
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print("[HKTICKETING TYPE02] Login timeout")
            return False

        # 檢查登入狀態
        login_status = await nodriver_hkticketing_type02_check_login_status(tab, config_dict)

        if login_status:
            print("[HKTICKETING TYPE02] Login successful")
            return True

        if elapsed % 30 == 0:
            print(f"[HKTICKETING TYPE02] Waiting for login... ({elapsed}s / {timeout}s)")

        await asyncio.sleep(2)
```

---

## 特殊設計 4: 確認訂單頁面

### 流程

1. **配送方式選擇**：選擇取票方式
2. **同意條款**：勾選同意複選框
3. **點擊提交**：點擊提交訂單按鈕

### 核心程式碼片段

```python
async def nodriver_hkticketing_type02_confirm_order(tab, config_dict):
    """Type 02 確認訂單頁面處理"""

    # 配送方式選擇
    await tab.evaluate('''
        (function() {
            // 選擇「郵寄」或「自取」
            const deliveryOptions = document.querySelectorAll('input[name="delivery"]');
            if (deliveryOptions.length > 0) {
                deliveryOptions[0].click();  // 選擇第一個選項
            }
        })();
    ''')

    # 勾選同意條款
    await tab.evaluate('''
        (function() {
            const agreeCheckbox = document.querySelector('input[type="checkbox"].agree, #agreeTerms');
            if (agreeCheckbox && !agreeCheckbox.checked) {
                agreeCheckbox.click();
            }
        })();
    ''')

    # 點擊提交按鈕
    submit_btn = await tab.query_selector('button.submit-btn, .btn-submit')
    if submit_btn:
        await submit_btn.click()
```

---

## 配置範例

```json
{
  "homepage": "https://hkt.hkticketing.com/hant/#/allEvents/detail/xxx",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "12/25",
    "mode": "random"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"A區\",\"B區\"",
    "mode": "random"
  },
  "ticket_number": 2,
  "advanced": {
    "verbose": true,
    "hkticketing_account": "your_email@example.com",
    "hkticketing_password": "encrypted_password",
    "play_sound": {
      "ticket": true,
      "order": true
    }
  }
}
```

---

## 常見問題與解決方案

### Q1: Type 02 一直顯示流量過載？

**A**: 這是正常的高流量保護機制。

**處理方式**：
- 程式會自動偵測並刷新
- 等待系統恢復後繼續

### Q2: 登入狀態無法維持？

**A**: 可能是 Cookie 或 localStorage 問題。

**解決方案**：
1. 確認帳號密碼正確
2. 手動完成一次登入後再啟動
3. 檢查是否有驗證碼阻擋

### Q3: 如何判斷使用哪種架構？

**A**: 根據 URL 自動判斷：
- `hkticketing.com` → Type 01
- `hkt.hkticketing.com` → Type 02

---

## 選擇器快速參考

### Type 01 選擇器

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 登入表單 | `form#loginForm` | 登入頁面 |
| 日期選項 | `.show-date`, `.performance-date` | 日期選擇 |
| 區域選項 | `.seat-area`, `.area-option` | 區域選擇 |
| 票數輸入 | `select.ticket-qty` | 票數設定 |
| 購買按鈕 | `button.buy-btn`, `.btn-buy` | 各頁面 |

### Type 02 選擇器

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 登入輸入 | `input[type="email"]`, `input[type="password"]` | SPA 登入 |
| 活動按鈕 | `.event-buy-btn`, `.btn-ticket` | 活動頁面 |
| 日期選項 | `.date-item`, `.session-item` | 票券選擇 |
| 區域選項 | `.area-btn`, `.ticket-area` | 票券選擇 |
| 票數選擇 | `select.qty-select`, `.v-select` | 票券選擇 |
| 下一步按鈕 | `.btn-next`, `button.primary` | 各頁面 |
| 提交按鈕 | `.btn-submit`, `button[type="submit"]` | 確認頁面 |

---

## 相關文件

- 📋 [Stage 11: 排隊處理機制](../../03-mechanisms/11-queue-handling.md) - 排隊偵測詳解
- 📋 [Stage 4: 日期選擇機制](../../03-mechanisms/04-date-selection.md) - 日期選擇邏輯
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - HKTicketing 函數索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：Type 01 基本支援 |
| v1.1 | 2025-08 | Type 02 SPA 支援 |
| v1.2 | 2025-10 | 排隊頁面處理優化 |
| **v1.3** | **2025-12** | **流量過載偵測 + 完整文件** |

**v1.3 亮點**：
- ✅ 完整的雙架構支援（Type 01 + Type 02）
- ✅ 流量過載自動偵測與刷新
- ✅ 多種排隊頁面處理（hot0-hot19）
- ✅ Type 02 localStorage 登入
- ✅ 確認訂單頁面完整處理
- ✅ 成功偵測 + 音效播放
