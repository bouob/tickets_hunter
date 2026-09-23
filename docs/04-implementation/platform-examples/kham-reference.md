# 平台實作參考：KHAM

**文件說明**：KHAM (寬宏售票) 平台的完整實作參考，涵蓋 ASP.NET 傳統架構、OCR 驗證碼、座點陣圖選擇、實名驗證等技術實作指南。
**最後更新**：2026-06-10

---

## 平台概述

**平台名稱**：KHAM (寬宏售票)
**關聯網站**：
- `kham.com.tw` - 主站
- `ticket.com.tw` - 別名
- `tickets.udnfunlife.com` - UDN 聯合報系統

**市場地位**：台灣主要票務平台之一
**主要業務**：演唱會、藝文活動、運動賽事
**完成度**：90% ✅
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- ASP.NET 傳統架構，頁面結構穩定
- 完整的座點陣圖選擇支援
- OCR 驗證碼辨識成功率高
- 支援多種購票流程（一般/座點陣圖）

⚠️ **挑戰**：
- 多種頁面型別（UTK0201/UTK0202/UTK0203/UTK0205）
- 實名驗證對話方塊處理
- 座點陣圖互動（SVG/Canvas）
- 舊版 ASP.NET 表單提交機制

### 特殊機制

1. **多頁面型別**
   - `UTK0201_.aspx` - 產品頁面（直接購買）
   - `UTK0201_00.aspx` - 日期選擇頁面
   - `UTK0202_.aspx` - 區域/票種選擇頁面
   - `UTK0203_.aspx` - 票數設定頁面（UDN 專用）
   - `UTK0205_.aspx` - 座點陣圖選擇頁面

2. **實名驗證對話方塊**
   - 自動偵測並關閉實名驗證提示
   - 處理各種彈出對話方塊

3. **座點陣圖選擇**（UTK0205）
   - 票種按鈕選擇
   - 自動切換到系統選位
   - 座位區域自動選擇

4. **OCR 驗證碼**
   - 圖形驗證碼辨識
   - 自動重試機制
   - 錯誤偵測與刷新

---

## 核心函式索引

| 階段 | 函式名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_kham_main()` | 1475 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_kham_login()` | 77 | 帳號登入（含 OCR）|
| Stage 3 | `nodriver_kham_product()` | 457 | 產品頁面處理 |
| Stage 4 | `nodriver_kham_date_auto_select()` | 477 | 日期自動選擇（含群組項目頁）|
| Stage 5 | `nodriver_kham_area_auto_select()` | 853 | 區域自動選擇 |
| Stage 5 | `nodriver_kham_seat_type_auto_select()` | 3041 | 座點陣圖票種選擇 |
| Stage 5 | `nodriver_kham_seat_auto_select()` | 3366 | 座點陣圖區域選擇 |
| Stage 6 | `nodriver_kham_performance()` | 1365 | 票數設定頁面 |
| Stage 7 | `nodriver_kham_captcha()` | 1321 | OCR 驗證碼處理 |
| Stage 7 | `nodriver_kham_auto_ocr()` | 1248 | 自動 OCR 重試 |
| Stage 7 | `nodriver_kham_keyin_captcha_code()` | 741 | 驗證碼輸入 |
| Stage 9 | `nodriver_kham_check_realname_dialog()` | 265 | 實名驗證對話方塊 |
| Stage 10 | `nodriver_kham_go_buy_redirect()` | 210 | 點擊購買按鈕 |
| Util | `nodriver_kham_allow_not_adjacent_seat()` | 327 | 允許非相鄰座位 |
| Util | `nodriver_kham_switch_to_auto_seat()` | 344 | 切換系統選位 |
| Util | `nodriver_kham_check_captcha_text_error()` | 424 | 驗證碼錯誤偵測 |
| Seat | `nodriver_kham_seat_main()` | 3769 | 座點陣圖主處理 |

**程式碼位置**：`src/platforms/kham.py`（2026-03 自 `nodriver_tixcraft.py` 模組化拆出）

---

## URL 路由表

| URL 模式 | 頁面型別 | 處理函式 |
|---------|---------|---------|
| `kham.com.tw/` | 首頁 | 自動登入/轉跳 |
| `utk0201_.aspx?product_id=` | 產品頁面 | 直接購買+驗證碼 |
| `utk0201_00.aspx?product_id=` | 日期選擇 | `nodriver_kham_product()` |
| `utk0201_040.aspx?agid=` | 活動群組 | 購買按鈕點擊 |
| `utk0201_041.aspx?agid=` | 群組項目 | `nodriver_kham_date_auto_select()`（#357：套用 keyword_exclude + mode）|
| 非 UTK0202 的 `*.aspx?performance_id=&product_id=` | 區域頁（salesTable，含實體票 `UTK0201_000`）| 區域選擇 + 售完節流（#357）|
| `utk0202_.aspx?performance_id=&activity_group_id=` | 群組福利券票種頁 | 票種選擇 + 驗證碼（以檔名 `utk0202` 區分，#357）|
| `utk0202_.aspx?performance_id=&performance_price_area_id=` | 票數設定 | 票數 + 驗證碼 + 送單 |
| `utk0203_.aspx?product_id=` | UDN 場次選擇 | UDN 專用流程 |
| `utk0204_.aspx`（無 PRICE_AREA_ID）| UDN 區域選擇 | UDN 區域 + 座點陣圖同頁 |
| `utk0205_.aspx` | 座點陣圖 | `nodriver_kham_seat_main()` |
| `utk0222_02.aspx?product_id=` | UDN 快速購買 | UDN quick buy 流程 |
| `utk0206_.aspx` | 結帳頁 | 送單後確認 |

---

## 特殊設計 1: 座點陣圖選擇（UTK0205）

### 流程

1. **票種選擇**：點擊票種按鈕（如「全票」）
2. **自動切換**：切換到「系統自動選位」
3. **區域選擇**：根據關鍵字選擇區域
4. **票數設定**：設定購買張數
5. **提交訂單**：點擊加入購物車

### 核心程式碼片段

```python
async def nodriver_kham_seat_main(tab, config_dict, ocr, domain_name):
    """座位圖頁面主處理"""

    # Step 1: 票種選擇
    await nodriver_kham_seat_type_auto_select(tab, config_dict, area_keyword_item)

    # Step 2: 切換到系統選位
    await nodriver_kham_switch_to_auto_seat(tab)

    # Step 3: 區域選擇
    await nodriver_kham_seat_auto_select(tab, config_dict)

    # Step 4: 驗證碼處理
    if config_dict["ocr_captcha"]["enable"]:
        await nodriver_kham_captcha(tab, config_dict, ocr, model_name)
```

---

## 特殊設計 2: OCR 驗證碼處理

### 流程

1. **擷取圖片**：從 `#imgCAPTCHA` 取得驗證碼圖片
2. **OCR 辨識**：使用 ddddocr 辨識
3. **填入答案**：自動填入驗證碼輸入框
4. **錯誤偵測**：偵測錯誤訊息
5. **自動重試**：錯誤時刷新驗證碼重試

### 核心程式碼片段

```python
async def nodriver_kham_captcha(tab, config_dict, ocr, model_name):
    """KHAM 驗證碼處理"""

    # 取得驗證碼圖片
    captcha_img = await tab.query_selector('#imgCAPTCHA')
    if captcha_img:
        img_src = await captcha_img.get_attribute('src')

        # OCR 辨識
        if img_src.startswith('data:image'):
            img_base64 = img_src.split(',')[1]
            img_bytes = base64.b64decode(img_base64)
            answer = ocr.classification(img_bytes)

            # 填入答案
            await nodriver_kham_keyin_captcha_code(tab, answer, auto_submit=False)

            return True

    return False
```

---

## 特殊設計 3: 實名驗證對話方塊

### 挑戰

KHAM 在某些活動會彈出實名驗證對話方塊，需要自動關閉才能繼續操作。

### 解決方案

```python
async def nodriver_kham_check_realname_dialog(tab, config_dict):
    """檢查並關閉實名驗證對話框"""

    result = await tab.evaluate('''
        (function() {
            // 查找實名驗證對話框
            const dialog = document.querySelector('.modal-dialog, .popup-dialog');
            if (dialog) {
                // 查找關閉按鈕
                const closeBtn = dialog.querySelector('.btn-close, .close, button[data-dismiss="modal"]');
                if (closeBtn) {
                    closeBtn.click();
                    return { closed: true };
                }

                // 嘗試點擊「我知道了」按鈕
                const confirmBtn = dialog.querySelector('button.btn-primary, button.btn-confirm');
                if (confirmBtn && confirmBtn.textContent.includes('知道')) {
                    confirmBtn.click();
                    return { closed: true };
                }
            }
            return { closed: false };
        })();
    ''')

    return result.get('closed', False)
```

---

## 配置範例

```json
{
  "homepage": "https://kham.com.tw/application/UTK01/UTK0201_00.aspx?product_id=xxx",
  "webdriver_type": "nodriver",
  "ticket_account": {
    "kham": {
      "account": "your_account",
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
    "area_keyword": "\"全票\",\"優惠票\"",
    "mode": "random"
  },
  "ticket_number": 2,
  "ocr_captcha": {
    "enable": true
  },
  "advanced": {
    "verbose": true,
    "kham_account": "your_account",
    "kham_password": "your_password"
  }
}
```

---

## 常見問題與解決方案

### Q1: 驗證碼一直失敗？

**A**: 可能是 OCR 辨識率問題。

**解決方案**：
1. 確認 ddddocr 已正確安裝
2. 檢查驗證碼圖片是否正常載入
3. 啟用 `verbose` 檢視 OCR 結果

### Q2: 座點陣圖無法選擇？

**A**: 可能是票種未正確選擇。

**檢查項目**：
1. 確認 `area_keyword` 包含正確的票種名稱
2. 檢查是否已切換到「系統自動選位」
3. 檢視記錄中的選擇結果

### Q3: 實名驗證對話方塊無法關閉？

**A**: 對話方塊選擇器可能已變更。

**解決方案**：
1. 啟用 `verbose` 模式檢視對話方塊內容
2. 手動確認對話方塊的 HTML 結構
3. 回報問題以更新選擇器

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 日期/場次列 | `table.eventTABLE > tbody > tr` | 列過濾（keyword + keyword_exclude）後點列內按鈕；舊選擇器 `button.red[onclick*="UTK0202"]` 為 #357 根因，已移除 |
| 票種按鈕 | `.ticket-type-btn`, `button.type-btn` | 座點陣圖頁面 |
| 驗證碼圖片 | `#imgCAPTCHA` | Base64 格式 |
| 驗證碼輸入 | `#CAPTCHA`, `input[name="CAPTCHA"]` | 文字輸入 |
| 票數輸入 | `#AMOUNT`, `input.yd_counterNum` | 數量設定 |
| 加入購物車 | `button[onclick*="addShoppingCart"]` | 提交按鈕 |
| 實名對話方塊 | `.modal-dialog`, `.popup-dialog` | 彈出視窗 |

---

## 相關文件

- 📋 [Stage 7: 驗證碼處理機制](../../03-mechanisms/07-captcha-handling.md) - OCR 驗證碼詳解
- 📋 [Stage 5: 區域選擇機制](../../03-mechanisms/05-area-selection.md) - 座點陣圖處理
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - KHAM 函式索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本功能支援 |
| v1.1 | 2025-08 | 座點陣圖選擇支援 |
| v1.2 | 2025-10 | OCR 驗證碼最佳化 |
| v1.3 | 2025-12 | UTK0205 座點陣圖完整支援 |
| **v1.4** | **2026-06** | **#357 群組活動修復：041 群組項目改走 date_auto_select、以檔名區分 UTK0201_000/UTK0202、售完節流；索引對齊 platforms/kham.py** |

**v1.3 亮點**：
- ✅ 完整的座點陣圖選擇流程（UTK0205）
- ✅ 多頁面型別支援（UTK0201/0202/0203/0205）
- ✅ 實名驗證對話方塊自動處理
- ✅ OCR 驗證碼自動重試機制
- ✅ 系統自動選位切換
