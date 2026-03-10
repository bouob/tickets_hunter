# 平台實作參考：TicketPlus

**文件說明**：TicketPlus 平台的完整實作參考，涵蓋排隊偵測、展開面板設計、實名驗證、多版面自動識別等技術實作指南。
**最後更新**：2025-12-02

---

## 平台概述

**平台名稱**：TicketPlus (遠大售票)
**市場地位**：台灣中型票務平台
**主要業務**：演唱會、展覽、運動賽事
**完成度**：85% ✅
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- Vue.js SPA 架構，DOM 結構相對穩定
- 支援多種版面自動識別
- 完整的排隊偵測機制
- 支援折扣碼輸入

⚠️ **挑戰**：
- 多種版面類型（Style 1/2/3）
- 展開面板（Accordion）設計
- 實名驗證需求
- 排隊機制需要等待

### 特殊機制

1. **排隊偵測**（核心功能）
   - 自動偵測排隊狀態關鍵字
   - 偵測到排隊時暫停操作
   - 等待排隊結束後繼續

   | 排隊關鍵字 | 說明 |
   |-----------|------|
   | `排隊購票中` | 進入排隊狀態 |
   | `請稍候` | 系統處理中 |
   | `請別離開頁面` | 排隊進行中 |
   | `請勿離開` | 排隊進行中 |
   | `請勿關閉網頁` | 排隊進行中 |
   | `同時使用多個裝置` | 多裝置警告 |
   | `視窗購票` | 排隊視窗提示 |
   | `正在處理` | 系統處理中 |
   | `處理中` | 系統處理中 |

2. **多版面自動識別**
   - Style 1: 標準版面（v-expansion-panels）
   - Style 2: 簡化版面（直接按鈕）
   - Style 3: 新版面（v-card 結構）
   - 自動偵測並套用對應選擇器

3. **展開面板**（Accordion）
   - 票區需要先點擊展開
   - 展開後才能選擇票數
   - 支援關鍵字匹配展開

4. **實名驗證對話框**
   - 自動偵測並關閉實名驗證提示
   - 自動處理「其他活動推薦」對話框
   - 自動處理「訂單失敗」對話框

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_ticketplus_main()` | 8928 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_ticketplus_account_sign_in()` | 6357 | 帳號登入 |
| Stage 2 | `nodriver_ticketplus_account_auto_fill()` | 6433 | 自動填入帳密 |
| Stage 3 | `nodriver_ticketplus_detect_layout_style()` | 6227 | 版面類型偵測 |
| Stage 4 | `nodriver_ticketplus_date_auto_select()` | 6485 | 日期自動選擇 |
| Stage 5 | `nodriver_ticketplus_unified_select()` | 6814 | 統一區域選擇 |
| Stage 5 | `nodriver_ticketplus_order_expansion_auto_select()` | 7453 | 展開面板區域選擇 |
| Stage 6 | `nodriver_ticketplus_assign_ticket_number()` | 8029 | 票數設定 |
| Stage 9 | `nodriver_ticketplus_ticket_agree()` | 8207 | 同意條款 |
| Stage 10 | `nodriver_ticketplus_click_next_button_unified()` | 7348 | 下一步按鈕 |
| Stage 11 | `nodriver_ticketplus_check_queue_status()` | 8376 | **排隊狀態偵測** |
| Stage 11 | `nodriver_ticketplus_order_auto_reload_coming_soon()` | 8455 | 即將開賣頁面處理 |
| Stage 12 | `nodriver_ticketplus_confirm()` | 8574 | 確認頁面處理 |
| Util | `nodriver_ticketplus_accept_realname_card()` | 8272 | 關閉實名驗證對話框 |
| Util | `nodriver_ticketplus_accept_other_activity()` | 8285 | 關閉推薦活動對話框 |
| Util | `nodriver_ticketplus_accept_order_fail()` | 8298 | 處理訂單失敗對話框 |
| Util | `nodriver_ticketplus_order_exclusive_code()` | 8844 | 折扣碼輸入 |
| Util | `nodriver_ticketplus_check_next_button()` | 8808 | 下一步按鈕狀態檢查 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## 特殊設計 1: 排隊狀態偵測

### 挑戰

TicketPlus 在高流量時會進入排隊狀態，此時：
- 頁面顯示排隊訊息
- 可能有 overlay 遮罩層
- 需要等待而非重複操作

### 解決方案

**核心程式碼**（`nodriver_ticketplus_check_queue_status`, Line 8376）:

```python
async def nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False):
    """檢查排隊狀態 - 優化版，避免重複輸出"""

    result = await tab.evaluate('''
        (function() {
            // 檢查排隊中的關鍵字
            const queueKeywords = [
                '排隊購票中',
                '請稍候',
                '請別離開頁面',
                '請勿離開',
                '請勿關閉網頁',
                '同時使用多個裝置',
                '視窗購票',
                '正在處理',
                '處理中'
            ];

            const bodyText = document.body.textContent || '';

            // 檢查是否包含任何排隊關鍵字
            const hasQueueKeyword = queueKeywords.some(keyword => bodyText.includes(keyword));

            // 檢查是否有遮罩層（排隊中的視覺指示）
            const overlayScrim = document.querySelector('.v-overlay__scrim');
            const hasOverlay = overlayScrim &&
                (overlayScrim.style.opacity === '1' ||
                 overlayScrim.style.display !== 'none');

            // 檢查對話框中的排隊訊息
            const dialogText = document.querySelector('.v-dialog')?.textContent || '';
            const hasQueueDialog = dialogText.includes('排隊') ||
                                   dialogText.includes('請稍候');

            return {
                inQueue: hasQueueKeyword || hasOverlay || hasQueueDialog,
                foundKeywords: queueKeywords.filter(keyword => bodyText.includes(keyword)),
                hasOverlay: hasOverlay,
                hasQueueDialog: hasQueueDialog
            };
        })();
    ''')

    return result.get('inQueue', False)
```

**排隊監控邏輯**：
```python
# 進入排隊監控循環，每 5 秒檢查一次
while True:
    is_still_in_queue = await nodriver_ticketplus_check_queue_status(tab, config_dict)

    if not is_still_in_queue:
        # 排隊結束，繼續處理
        print("[QUEUE END] Queue ended, continuing page processing")
        break

    await asyncio.sleep(5)  # 每 5 秒檢查一次
```

---

## 特殊設計 2: 多版面自動識別

### 挑戰

TicketPlus 有多種頁面版面，選擇器不同：
- **Style 1**: 使用 `v-expansion-panels` 展開面板
- **Style 2**: 直接按鈕式選擇
- **Style 3**: 使用 `v-card` 卡片結構

### 解決方案

**核心程式碼**（`nodriver_ticketplus_detect_layout_style`, Line 6227）:

```python
async def nodriver_ticketplus_detect_layout_style(tab, config_dict=None):
    """自動偵測 TicketPlus 頁面版面類型"""

    result = await tab.evaluate('''
        (function() {
            // Style 1: v-expansion-panels (標準展開面板)
            if (document.querySelector('.v-expansion-panels')) {
                return { style: 1, selector: '.v-expansion-panels' };
            }

            // Style 2: 直接按鈕
            if (document.querySelector('.ticket-area-btn')) {
                return { style: 2, selector: '.ticket-area-btn' };
            }

            // Style 3: v-card 結構
            if (document.querySelector('.v-card.ticket-card')) {
                return { style: 3, selector: '.v-card.ticket-card' };
            }

            return { style: 0, selector: null };
        })();
    ''')

    return result.get('style', 0)
```

---

## 特殊設計 3: 展開面板區域選擇

### 流程

1. **偵測展開面板**：查找 `.v-expansion-panel-header`
2. **關鍵字匹配**：比對票區名稱
3. **點擊展開**：展開目標票區
4. **等待動畫**：等待展開動畫完成
5. **設定票數**：在展開的面板中設定票數

### 核心程式碼片段

```python
# 展開面板選擇器
panel_headers = await tab.query_selector_all('.v-expansion-panel-header')

for header in panel_headers:
    header_text = await header.text

    # 關鍵字匹配
    if area_keyword in header_text:
        # 檢查是否已展開
        is_expanded = 'v-expansion-panel--active' in await header.get_attribute('class')

        if not is_expanded:
            await header.click()
            await asyncio.sleep(0.5)  # 等待展開動畫

        # 在展開的面板中設定票數
        panel_content = await header.query_selector('~ .v-expansion-panel-content')
        ticket_input = await panel_content.query_selector('input[type="number"]')

        if ticket_input:
            await ticket_input.clear()
            await ticket_input.send_keys(str(ticket_number))
```

---

## URL 路由表

| URL 模式 | 頁面類型 | 處理函數 |
|---------|---------|---------|
| `ticketplus.com.tw/` | 首頁 | 自動登入填入 |
| `/activity/{id}` | 活動頁面 | 日期選擇 |
| `/order/{id}/{session}` | 訂單頁面 | 區域+票數選擇 |
| `/confirm/{id}/{session}` | 確認頁面 | 確認訂單 |
| `/confirmseat/{id}/{session}` | 座位確認 | 確認座位 |

---

## 配置範例

```json
{
  "homepage": "https://ticketplus.com.tw/activity/xxx",
  "webdriver_type": "nodriver",
  "ticket_account": {
    "ticketplus": {
      "email": "your@email.com",
      "password": "your_password"
    }
  },
  "date_auto_select": {
    "enable": true,
    "date_keyword": "12/25",
    "mode": "random"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"VIP區\",\"搖滾區\",\"一般區\"",
    "mode": "random"
  },
  "ticket_number": 2,
  "advanced": {
    "verbose": true,
    "auto_reload_page_interval": 3
  }
}
```

---

## 常見問題與解決方案

### Q1: 為什麼一直卡在排隊？

**A**: 這是正常現象，程式會自動等待排隊結束。

**檢查項目**：
- 查看日誌是否顯示 `[QUEUE] Queue status detected`
- 確認網路連線穩定
- 排隊時間視活動熱門程度而定

### Q2: 展開面板無法點擊？

**A**: 可能是版面類型偵測錯誤。

**解決方案**：
1. 啟用 `verbose` 模式查看偵測結果
2. 檢查 `layout_style` 輸出
3. 手動確認頁面結構是否符合預期

### Q3: 折扣碼無法輸入？

**A**: 確認 `exclusive_code` 設定正確。

**設定方式**：
```json
{
  "advanced": {
    "ticketplus_exclusive_code": "YOUR_CODE"
  }
}
```

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 日期按鈕 | `.session-btn`, `.date-btn` | 依版面類型 |
| 展開面板 | `.v-expansion-panel-header` | Style 1 |
| 票數輸入 | `input[type="number"]` | 在面板內 |
| 下一步按鈕 | `.v-btn.primary`, `button[type="submit"]` | 多種選擇器 |
| 排隊遮罩 | `.v-overlay__scrim` | 偵測排隊 |
| 對話框 | `.v-dialog` | 各種提示 |

---

## 相關文件

- 📋 [Stage 11: 排隊處理機制](../../03-mechanisms/11-queue-handling.md) - 排隊偵測詳解
- 📋 [Stage 5: 區域選擇機制](../../03-mechanisms/05-area-selection.md) - 展開面板處理
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - TicketPlus 函數索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本功能支援 |
| v1.1 | 2025-08 | 多版面自動識別 |
| v1.2 | 2025-10 | 展開面板優化 |
| **v1.3** | **2025-11** | **排隊偵測機制完善** |
| **v1.4** | **2025-12** | **折扣碼支援 + 文件更新** |

**v1.4 亮點**：
- ✅ 完整的排隊偵測機制（9 個關鍵字 + overlay 偵測）
- ✅ 多版面自動識別（Style 1/2/3）
- ✅ 展開面板關鍵字匹配
- ✅ 折扣碼自動輸入
- ✅ 實名驗證對話框自動處理
