# 平台實作參考：KHAM

**文件說明**：KHAM (寬宏售票) 平台的完整實作參考，涵蓋 ASP.NET 傳統架構、OCR 驗證碼、座位圖選擇、實名驗證，以及中職售票 UTK RWD 版的差異等技術實作指南。
**最後更新**：2026-10-30

---

## 平台概述

**平台名稱**：KHAM (寬宏售票)
**關聯網站**：
- `kham.com.tw` - 主站
- `ticket.com.tw` - 別名
- `tickets.udnfunlife.com` - UDN 聯合報系統
- `tix.ctbcsports.com`、`tix.wdragons.com`、`guardians.fami.life` - 中職售票；同系統籃球隊中信特攻（`tix.ctbcsports.com/DEA`）、富邦勇士（`tix.fubonbraves.com`）也適用（UTK RWD 版，尚未真站實測），見[UTK RWD 版差異](#utk-rwd-版差異中職售票)

**市場地位**：台灣主要票務平台之一
**主要業務**：演唱會、藝文活動、運動賽事
**完成度**：90% ✅
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- ASP.NET 傳統架構，頁面結構穩定
- 完整的座位圖選擇支援
- OCR 驗證碼辨識成功率高
- 支援多種購票流程（一般/座位圖）

⚠️ **挑戰**：
- 多種頁面型別（UTK0201/UTK0202/UTK0203/UTK0205）
- 實名驗證對話方塊處理
- 座位圖互動（SVG/Canvas）
- 舊版 ASP.NET 表單提交機制

### 特殊機制

1. **多頁面型別**
   - `UTK0201_.aspx` - 產品頁面（直接購買）
   - `UTK0201_00.aspx` - 日期選擇頁面
   - `UTK0202_.aspx` - 區域/票種選擇頁面
   - `UTK0203_.aspx` - 票數設定頁面（UDN 專用）
   - `UTK0205_.aspx` - 座位圖選擇頁面

2. **實名驗證對話方塊**
   - 自動偵測並關閉實名驗證提示
   - 處理各種彈出對話方塊

3. **座位圖選擇**（UTK0205）
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
| Stage 5 | `nodriver_kham_seat_type_auto_select()` | 3041 | 座位圖票種選擇 |
| Stage 5 | `nodriver_kham_seat_auto_select()` | 3366 | 座位圖區域選擇 |
| Stage 6 | `nodriver_kham_performance()` | 1365 | 票數設定頁面 |
| Stage 7 | `nodriver_kham_captcha()` | 1321 | OCR 驗證碼處理 |
| Stage 7 | `nodriver_kham_auto_ocr()` | 1248 | 自動 OCR 重試 |
| Stage 7 | `nodriver_kham_keyin_captcha_code()` | 741 | 驗證碼輸入 |
| Stage 9 | `nodriver_kham_check_realname_dialog()` | 265 | 實名驗證對話方塊 |
| Stage 10 | `nodriver_kham_go_buy_redirect()` | 210 | 點擊購買按鈕 |
| Util | `nodriver_kham_allow_not_adjacent_seat()` | 327 | 允許非相鄰座位 |
| Util | `nodriver_kham_switch_to_auto_seat()` | 344 | 切換系統選位 |
| Util | `nodriver_kham_check_captcha_text_error()` | 424 | 驗證碼錯誤偵測 |
| Seat | `nodriver_kham_seat_main()` | 3769 | 座位圖主處理 |

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
| `utk0204_.aspx`（無 PRICE_AREA_ID）| UDN 區域選擇 | UDN 區域 + 座位圖同頁 |
| `utk0205_.aspx` | 座位圖 | `nodriver_kham_seat_main()` |
| `utk0222_02.aspx?product_id=` | UDN 快速購買 | UDN quick buy 流程 |
| `utk0206_.aspx` | 結帳頁 | 送單後確認 |

---

## 特殊設計 1: 座位圖選擇（UTK0205）

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

### 舞台方向與排序

`nodriver_kham_seat_auto_select()` 讀 `.stageDirection` 判斷舞台（球場）方向：

- **舞台在上／下**：依排在座位圖上的位置（`#TBL` 的列順序）排序，越靠近舞台的排越先選，不看排號。中信特攻的座位圖把 I 排畫在 E 排上方、球場在下，排號往遠離球場的方向遞增；舊規則「排號越大越前」會選到最遠的排。
- **舞台在左／右**：仍依座位號排序（未變）。

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

## UTK RWD 版差異（中職售票）

中信兄弟、味全龍、富邦悍將的售票網是寬宏 UTK 系統的 RWD 新版（ASP.NET Core 改寫），同系統的籃球隊新北中信特攻（TPBL）、臺北富邦勇士（PLG）也適用。各站併入 `src/platforms/kham.py`，與寬宏共用 `nodriver_kham_main()`，不是獨立的平台檔。

> ⚠️ **尚未真站實測**：開發時正值季後、沒有賽事，只用未登入的真實頁面快照驗證過選擇器，沒有實際送單。2026-10-30 以未登入狀態唯讀比對中信特攻的場次（UTK0201）、票區（UTK0204）、場邊特區票數（UTK0202）、選位（UTK0205）頁，選擇器相符；登入與加入購物車仍未實測。富邦勇士只確認過首頁（`FUBONBRAVES|*`、`_ul`、登入彈窗）。不支援會員優先購與季票。

### 站台與路由

| 站台 | 網域 | Cookie 名稱開頭 |
|------|------|----------------|
| 中信兄弟 | `tix.ctbcsports.com`（含 `/BROTHERS/`、`/DEA/` 虛擬目錄；`/DEA/` 為籃球隊中信特攻） | `CTBC_` |
| 味全龍 | `tix.wdragons.com` | `WDRAGONS\|` |
| 富邦悍將 | `guardians.fami.life` | `FBGUARDIANS\|` |
| 臺北富邦勇士（PLG） | `tix.fubonbraves.com` | `FUBONBRAVES\|` |

- 站台清單集中在 `CONST_UTK_RWD_TENANTS`。`src/nodriver_tixcraft.py` 的 `main()` 用 `is_utk_rwd_url()` 判斷網域，把各站歸入寬宏家族。
- RWD 網址拿掉了 `/application/utkNN/` 與 `.aspx`（例如 `/BROTHERS/UTK0201_?PRODUCT_ID=`）。`nodriver_kham_main()` 進場先用 `normalize_utk_rwd_url()` 改寫成寬宏版面（`/application/utk02/utk0201_.aspx?PRODUCT_ID=`），既有的頁型判斷就能直接套用。改寫結果**只供判斷、不可導航**（RWD 站沒有這些路徑）；無圖形界面模式結帳時開啟的仍是原始網址。
- 頁面元素 id 沿用寬宏（`#CHK`、`table#TBL`、`addShoppingCart`、`#dialog-message`）。

### 頁面差異

| 頁面 | RWD 差異 | 處理方式 |
|------|---------|---------|
| 首頁 `UTK0101_`、站台根目錄、虛擬目錄 | 三者都是首頁 | 依「售票網站」設定轉跳 |
| 商品頁 `UTK0201_?PRODUCT_ID=` | 場次列表以 XHR 載入；完整列表在隱藏彈窗 `#PerformanceListTable_popup`，頁內表格最多四場 | 等列表出現後走 `nodriver_kham_date_auto_select()`，先讀彈窗再讀頁內表格；只點以 `location.href` 轉頁的購買鈕，`VipSellCheck()`（會員優先購）列略過 |
| 票區頁 `UTK0204_` | 票區表為 `table.f1 > tbody > tr.saleTr`，售完列顯示「售完」；按下票區只會把點選動作轉給 XHR 載入的座位圖 `<area>` | 等 `#mapdata area` 出現才選區；本頁沒有訂單驗證碼，不跑 OCR |
| 票數頁 `UTK0202_` | 中信的場次列表會直接連到 UTK0202，整場票區列在同一頁（網址沒有 `PERFORMANCE_PRICE_AREA_ID`），每區各有一個 `#AMOUNT` | `nodriver_utk_rwd_assign_ticket_number()` 先選列再加到指定張數，規則見下 |
| 選位頁 `UTK0205_` | 空位沒有 `empty` class，而是帶 `title`、背景圖為 `seat-empty_N.png` 的 `#TBL` 格 | `nodriver_kham_seat_auto_select(rwd=True)` 改用此規則認空位，其餘選位邏輯共用（舞台方向排序見[舞台方向與排序](#舞台方向與排序)） |
| 結帳頁 | 味全為 `UTK0206_02`，其他站為 `UTK0206_` | 改寫後都視為結帳頁 |

**UTK0202 選列規則**（`_pick_utk_rwd_amount_row()`）：
1. 剔除命中排除關鍵字、或剩餘張數少於門票張數的列；售完的票區沒有 `#AMOUNT`，本來就不會列入。
2. 全場票區頁用「票區名稱 + 票種」比對區域關鍵字（空格為 AND，多組依序嘗試）；都對不上時，只有開啟區域自動遞補才依區域排序方式挑一列。
3. 從票區點進來的 UTK0202 票區已固定，只套用排除關鍵字，剩下的列依區域排序方式挑選。
4. 沒有可買的列時不送單，重新整理頁面並等待 `max(自動刷新頁面間隔, CONST_KHAM_RELOAD_SETTLE)`。

**驗證碼抓圖**：`src/nodriver_common.py` 的 `nodriver_get_captcha_image_from_dom_snapshot()` 除了 `/pic.aspx?TYPE=`，也接受 RWD 的 `/Home/pic?TYPE=`（含虛擬目錄下的 `/DEA/Home/pic`），並略過登入彈窗的 `#master_chk_pic`——它與訂單驗證碼同頁，且在 DOM 中排在前面。

### 登入（#437）

每次進入 `nodriver_kham_main()` 先呼叫 `nodriver_utk_rwd_ensure_login()`，用頁面變數 `_ul` 判斷登入狀態（`'0'` 為訪客，與站方腳本的判斷相同）：

1. **Cookie 優先**：「中職售票 Cookie」有填時，每個站台先試一次 `nodriver_utk_rwd_cookie_login()`。`parse_cookie_string()` 解析整串 Cookie，`filter_utk_rwd_cookies()` 只留名稱開頭屬於目前站台的 Cookie；刪除同名舊 Cookie 後寫入目前網域（host-only），重新載入再看 `_ul`。一串 Cookie 不會跨站混用；log 只記數量，不記值。
2. **帳密彈窗**：Cookie 沒填或無效時，用「中職售票 帳號／密碼」走頁內登入彈窗（`nodriver_utk_rwd_login()`）：開啟 `#popupuser`、OCR 辨識 `#master_chk_pic`、呼叫站方的 `doMasterLogin()`。每站最多送出 5 次、間隔 3 秒（`CONST_UTK_RWD_LOGIN_MAX_TRIES`、`CONST_UTK_RWD_LOGIN_RETRY_SEC`），避免密碼錯誤時鎖帳號；OCR 讀到的不是 4 碼就換一張圖重試，不計入送出次數。
3. **沒開 OCR**：只填帳號密碼，驗證碼與登入留給使用者，之後不再覆寫彈窗內容。
4. **自動登入停止後**：訪客仍可瀏覽，但進到下單頁（UTK0205、UTK0202、UTK0201_001）會停住，等使用者手動登入。帳號是身分證或護照號碼，log 不記任何片段。

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

### Q2: 座位圖無法選擇？

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
| 票種按鈕 | `.ticket-type-btn`, `button.type-btn` | 座位圖頁面 |
| 驗證碼圖片 | `#imgCAPTCHA` | Base64 格式 |
| 驗證碼輸入 | `#CAPTCHA`, `input[name="CAPTCHA"]` | 文字輸入 |
| 票數輸入 | `#AMOUNT`, `input.yd_counterNum` | 數量設定 |
| 加入購物車 | `button[onclick*="addShoppingCart"]` | 提交按鈕 |
| 實名對話方塊 | `.modal-dialog`, `.popup-dialog` | 彈出視窗 |

---

## 相關文件

- 📋 [Stage 7: 驗證碼處理機制](../../03-mechanisms/07-captcha-handling.md) - OCR 驗證碼詳解
- 📋 [Stage 5: 區域選擇機制](../../03-mechanisms/05-area-selection.md) - 座位圖處理
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - KHAM 函式索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本功能支援 |
| v1.1 | 2025-08 | 座位圖選擇支援 |
| v1.2 | 2025-10 | OCR 驗證碼最佳化 |
| v1.3 | 2025-12 | UTK0205 座位圖完整支援 |
| v1.4 | 2026-06 | #357 群組活動修復：041 群組項目改走 date_auto_select、以檔名區分 UTK0201_000/UTK0202、售完節流；索引對齊 platforms/kham.py |
| **v1.5** | **2026-10** | **中職售票（中信兄弟／味全龍／富邦悍將）UTK RWD 版併入寬宏流程，含 Cookie 與登入彈窗（#437）；尚未真站實測** |
| v1.6 | 2026-10 | 新增同系統籃球隊中信特攻（`/DEA`）、富邦勇士；選位在舞台上／下時改依座位圖位置排序，不看排號 |

**v1.3 亮點**：
- ✅ 完整的座位圖選擇流程（UTK0205）
- ✅ 多頁面型別支援（UTK0201/0202/0203/0205）
- ✅ 實名驗證對話方塊自動處理
- ✅ OCR 驗證碼自動重試機制
- ✅ 系統自動選位切換
