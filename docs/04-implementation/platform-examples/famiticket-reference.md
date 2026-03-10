# 平台實作參考：FamiTicket

**文件說明**：FamiTicket (全家網票務) 平台的完整實作參考，涵蓋登入流程、日期/區域選擇、驗證問題處理等技術實作指南。
**最後更新**：2025-12-02

---

## 平台概述

**平台名稱**：FamiTicket (全家網票務)
**網站**：`www.famiticket.com.tw`
**市場地位**：台灣便利商店票務系統
**主要業務**：演唱會、展覽、交通票券
**完成度**：80% ✅
**難度級別**：⭐⭐ (中等)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 標準 Web 架構，DOM 結構清晰
- 登入流程相對簡單
- 支援自動日期/區域選擇
- URL 路由清晰

⚠️ **挑戰**：
- 問答式驗證（類似 KKTIX）
- 登入狀態維護
- 部分頁面需要等待 DOM 載入

### 特殊機制

1. **URL 路由分派**
   - `/Home/User/SignIn` - 登入頁面
   - `/Home/Activity/Info/{id}` - 活動資訊頁面
   - `/Sales/Home/Index/{id}` - 銷售首頁（日期/區域選擇）
   - `/Payment/` - 結帳頁面

2. **問答式驗證**
   - 自動偵測驗證問題
   - fail_list 機制避免重複錯誤答案
   - 支援使用者自訂答案庫

3. **活動頁面處理**
   - 自動記錄最後訪問的活動 URL
   - 登入後自動轉跳回活動頁面

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_famiticket_main()` | 10145 | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_fami_login()` | 9188 | 帳號登入 |
| Stage 3 | `nodriver_fami_activity()` | 9303 | 活動頁面處理 |
| Stage 4 | `nodriver_fami_date_auto_select()` | 9470 | 日期自動選擇 |
| Stage 5 | `nodriver_fami_area_auto_select()` | 9671 | 區域自動選擇 |
| Stage 5 | `nodriver_fami_date_to_area()` | 9833 | 日期→區域轉換 |
| Stage 6 | `nodriver_fami_ticket_select()` | 9910 | 票數選擇 |
| Stage 7 | `nodriver_fami_verify()` | 9362 | 問答式驗證處理 |
| Stage 10 | `nodriver_fami_home_auto_select()` | 10038 | 銷售首頁自動選擇 |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## URL 路由表

| URL 模式 | 頁面類型 | 處理函數 |
|---------|---------|---------|
| `/Home/User/SignIn` | 登入頁面 | `nodriver_fami_login()` |
| `/Home/Activity/Info/{id}` | 活動資訊 | `nodriver_fami_activity()` |
| `/Sales/Home/Index/{id}` | 銷售首頁 | `nodriver_fami_home_auto_select()` |
| `/Home/` | 首頁 | 自動轉跳 |
| `/Payment/` | 結帳頁面 | 等待使用者完成 |

---

## 特殊設計 1: 登入流程

### 流程

1. **偵測登入頁面**：檢查 URL 是否包含 `/SignIn`
2. **填入帳密**：自動填入 email 和密碼
3. **點擊登入**：點擊登入按鈕
4. **等待轉跳**：等待 URL 變化確認登入成功

### 核心程式碼片段

```python
async def nodriver_fami_login(tab, config_dict, show_debug_message=True):
    """FamiTicket 登入處理"""

    fami_account = config_dict["advanced"].get("fami_account", "")
    fami_password = config_dict["advanced"].get("fami_password_plaintext", "")

    if len(fami_account) < 4:
        return False

    # 填入帳號
    account_input = await tab.query_selector('input[name="Account"], #Account')
    if account_input:
        await account_input.clear()
        await account_input.send_keys(fami_account)

    # 填入密碼
    password_input = await tab.query_selector('input[name="Password"], #Password')
    if password_input:
        await password_input.clear()
        await password_input.send_keys(fami_password)

    # 點擊登入按鈕
    login_btn = await tab.query_selector('button[type="submit"], #btnLogin')
    if login_btn:
        await login_btn.click()
        await asyncio.sleep(1.0)

        if show_debug_message:
            print("[FAMI LOGIN] Login button clicked, waiting for URL change...")

    return True
```

---

## 特殊設計 2: 問答式驗證

### 挑戰

FamiTicket 使用問答式驗證（類似 KKTIX），需要回答活動相關問題。

### 解決方案

```python
async def nodriver_fami_verify(tab, config_dict, fail_list=None, show_debug_message=True):
    """問答式驗證處理"""

    if fail_list is None:
        fail_list = []

    # 取得問題文字
    question_result = await tab.evaluate('''
        (function() {
            const questionEl = document.querySelector('.verify-question, .question-text');
            return questionEl ? questionEl.textContent.trim() : null;
        })();
    ''')

    if not question_result:
        return True, fail_list

    # 取得答案列表
    answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)

    # 自動推測答案
    if len(answer_list) == 0 and config_dict["advanced"]["auto_guess_options"]:
        answer_list = util.get_answer_list_from_question_string(None, question_result)

    # fail_list 機制 - 跳過已失敗的答案
    inferred_answer = ""
    for answer_item in answer_list:
        if answer_item not in fail_list:
            inferred_answer = answer_item
            break

    if inferred_answer:
        # 填寫答案
        answer_input = await tab.query_selector('input.verify-input, #answer')
        if answer_input:
            await answer_input.clear()
            await answer_input.send_keys(inferred_answer)

        return True, fail_list

    return False, fail_list
```

---

## 特殊設計 3: 銷售首頁自動選擇

### 流程

1. **日期選擇**：根據關鍵字選擇日期
2. **區域選擇**：根據關鍵字選擇票區
3. **票數設定**：設定購買張數
4. **下一步**：點擊購買按鈕

### 核心程式碼片段

```python
async def nodriver_fami_home_auto_select(tab, config_dict, last_activity_url, show_debug_message=True):
    """銷售首頁自動選擇（日期 + 區域）"""

    # 日期選擇
    if config_dict["date_auto_select"].get("enable", True):
        await nodriver_fami_date_auto_select(tab, config_dict, last_activity_url, show_debug_message)

    # 區域選擇
    if config_dict["area_auto_select"].get("enable", True):
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        if area_keyword:
            # Parse keywords
            area_keyword_array = [kw.strip().strip('"') for kw in area_keyword.split(',') if kw.strip()]

            for area_keyword_item in area_keyword_array:
                result = await nodriver_fami_area_auto_select(tab, config_dict, area_keyword_item, show_debug_message)
                if result:
                    break  # Early return

    # 票數選擇
    await nodriver_fami_ticket_select(tab, config_dict, show_debug_message)

    return True
```

---

## 配置範例

```json
{
  "homepage": "https://www.famiticket.com.tw/Home/Activity/Info/xxx",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "12/25",
    "mode": "random"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"一般區\",\"VIP區\"",
    "mode": "random"
  },
  "ticket_number": 2,
  "advanced": {
    "verbose": true,
    "fami_account": "your_account",
    "fami_password_plaintext": "your_password",
    "user_guess_string": "台北,演唱會,2025",
    "auto_guess_options": true
  }
}
```

---

## 常見問題與解決方案

### Q1: 登入後沒有自動轉跳？

**A**: 可能是 `homepage` 設定問題。

**檢查項目**：
1. 確認 `homepage` 設定為活動頁面 URL
2. 確認帳號密碼正確
3. 檢查是否有驗證碼阻擋

### Q2: 問答驗證一直失敗？

**A**: 需要補充答案庫。

**解決方案**：
1. 查看問題日誌
2. 補充 `user_guess_string` 設定
3. 啟用 `auto_guess_options`

### Q3: 區域選擇失敗？

**A**: 關鍵字可能不匹配。

**解決方案**：
1. 啟用 `verbose` 查看可用區域
2. 調整 `area_keyword` 設定
3. 確認頁面已完全載入

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 帳號輸入 | `input[name="Account"]`, `#Account` | 登入頁面 |
| 密碼輸入 | `input[name="Password"]`, `#Password` | 登入頁面 |
| 登入按鈕 | `button[type="submit"]`, `#btnLogin` | 登入頁面 |
| 購買按鈕 | `#buyWaiting`, `.buy-btn` | 活動頁面 |
| 日期選項 | `.date-item`, `.session-item` | 銷售首頁 |
| 區域選項 | `.area-item`, `.ticket-area` | 銷售首頁 |
| 票數輸入 | `input[type="number"]`, `.ticket-count` | 銷售首頁 |
| 驗證問題 | `.verify-question`, `.question-text` | 驗證頁面 |

---

## 相關文件

- 📋 [Stage 7: 驗證碼處理機制](../../03-mechanisms/07-captcha-handling.md) - 問答式驗證詳解
- 📋 [Stage 4: 日期選擇機制](../../03-mechanisms/04-date-selection.md) - 日期選擇邏輯
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - FamiTicket 函數索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本功能支援 |
| v1.1 | 2025-08 | 登入流程優化 |
| **v1.2** | **2025-12** | **問答驗證 + 完整文件** |

**v1.2 亮點**：
- ✅ 完整的 URL 路由分派
- ✅ 問答式驗證支援（fail_list 機制）
- ✅ 自動記錄最後活動 URL
- ✅ 登入後自動轉跳
