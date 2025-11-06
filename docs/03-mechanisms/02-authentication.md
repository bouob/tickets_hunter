# 機制 02：身份認證 (Stage 2)

## 概述

身份認證是許多售票平台的必要步驟。在此階段，系統需要確保使用者已登入，並維持有效的認證狀態，以便後續進行購票操作。

**核心目標**：自動完成身份認證，確保系統擁有必要的權限進行購票。

**優先度**：🟡 P2 - 重要但非核心流程

---

## 認證機制流程

### 1. 認證狀態檢查

#### 1.1 初始狀態評估
系統首先檢查頁面是否已經在認證狀態。

**檢查方法**：
1. **查找認證指示符**
   - 搜尋使用者名稱/帳號顯示
   - 查找「登出」按鈕或鏈接
   - 檢查使用者頭像或個人資料

2. **檢查頁面 HTML 元素**
   - 查找常見的認證令牌標籤
   - 檢查 `localStorage` 中的認證信息
   - 驗證 `sessionStorage` 中的會話資料

3. **嘗試訪問受保護功能**
   - 嘗試查看購物車（需認證）
   - 檢查個人訂單頁面（需認證）

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 500-600 (認證狀態檢查)

**代碼範例**：
```python
async def check_authentication_status(page) -> bool:
    """檢查認證狀態"""
    # 方法 1: 查找認證指示符
    user_info = await page.query_selector('.user-info, .account-name, .profile-name')
    if user_info:
        text = await user_info.get_text()
        if text and len(text.strip()) > 0:
            print(f"[AUTH] 檢測到已認證狀態: {text}")
            return True

    # 方法 2: 查找登出按鈕
    logout_btn = await page.query_selector('a[href*="logout"], button[title*="登出"]')
    if logout_btn:
        print("[AUTH] 檢測到登出按鈕，已認證")
        return True

    return False
```

#### 1.2 若未認證，判斷認證類型
系統需要判斷應該使用哪種認證方式：
- **Cookie 認證** - 如果配置中提供了 Cookie
- **帳號密碼認證** - 如果提供了帳號憑證
- **第三方認證** - 例如 Google、Facebook 登入（目前不支援）

### 2. Cookie 認證

#### 2.1 Cookie 注入（優先方式）
如果配置中提供了有效的 Cookie，優先使用 Cookie 進行認證。

**優勢**：
- ✅ 最快速，無需互動
- ✅ 不需要輸入帳號密碼
- ✅ 減少反偵測風險
- ✅ 平台通常接受有效 Cookie

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 600-650 (Cookie 注入)

**代碼範例**：
```python
async def authenticate_with_cookie(page, cookies: dict):
    """使用 Cookie 進行認證"""
    if not cookies:
        print("[AUTH] 未提供 Cookie")
        return False

    try:
        # 解析 Cookie 字典
        cookie_list = parse_cookie_dict(cookies)

        # 注入到頁面
        await page.add_init_script("""
            localStorage.setItem('auth_token', arguments[0]);
        """, cookies.get('auth_token', ''))

        print(f"[AUTH] 已注入 {len(cookie_list)} 個 Cookie")

        # 重新載入頁面以應用 Cookie
        await page.reload(wait_until='networkidle2')

        # 驗證認證成功
        if await check_authentication_status(page):
            print("[AUTH] Cookie 認證成功")
            return True
        else:
            print("[WARNING] Cookie 注入完成但認證失敗，可能已過期")
            return False

    except Exception as e:
        print(f"[ERROR] Cookie 注入失敗: {e}")
        return False
```

#### 2.2 Cookie 有效期檢查
檢查 Cookie 是否已過期或即將過期。

**檢查項目**：
- 如果 Cookie 包含 `expires` 或 `max-age` 欄位，驗證有效期
- 某些平台將有效期存放在 Cookie 值本身（如編碼的過期時間戳）
- 建議在 Cookie 年齡超過 1 週時重新更新

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 650-700

### 3. 帳號密碼認證

#### 3.1 登入頁面檢測
系統檢測是否存在登入頁面，並自動填寫帳號密碼。

**登入頁面特徵**：
- 包含使用者名稱或帳號輸入欄
- 包含密碼輸入欄
- 包含「登入」或「確認」按鈕
- URL 通常含有 `/login` 或 `/signin`

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 700-750

**代碼範例**：
```python
async def detect_login_page(page) -> bool:
    """檢測是否在登入頁面"""
    selectors = [
        'input[type="email"]',
        'input[name*="email"]',
        'input[name*="account"]',
        'input[type="password"]'
    ]

    for selector in selectors:
        element = await page.query_selector(selector)
        if element:
            print(f"[AUTH] 檢測到登入頁面: {selector}")
            return True

    return False
```

#### 3.2 帳號密碼填寫
自動填寫登入表單。

**填寫流程**：
1. 定位帳號輸入欄 (`email`、`username`、`account`)
2. 定位密碼輸入欄 (`password`)
3. 輸入配置中的帳號和密碼
4. 尋找並點擊登入按鈕

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 750-800

**代碼範例**：
```python
async def fill_login_form(page, username: str, password: str):
    """填寫登入表單"""
    try:
        # 定位帳號輸入欄
        username_input = await page.query_selector(
            'input[name*="email"], input[name*="account"], input[type="email"]'
        )
        if username_input:
            await username_input.type(username, delay=50)
            print(f"[AUTH] 已輸入帳號")

        # 定位密碼輸入欄
        password_input = await page.query_selector('input[type="password"]')
        if password_input:
            await password_input.type(password, delay=50)
            print(f"[AUTH] 已輸入密碼")

        # 定位登入按鈕
        login_button = await page.query_selector(
            'button:has-text("登入"), button:has-text("Sign In"), button[type="submit"]'
        )
        if login_button:
            await login_button.click()
            print("[AUTH] 已點擊登入按鈕")

            # 等待頁面載入
            await page.wait_for_timeout(3000)
            await page.wait_for_load_state('networkidle2')

    except Exception as e:
        print(f"[ERROR] 登入表單填寫失敗: {e}")
        return False

    return True
```

#### 3.3 登入成功驗證
驗證登入是否成功。

**驗證方法**：
- 檢查是否仍在登入頁面（未成功則通常留在原頁面）
- 檢查是否出現登出按鈕或使用者資訊
- 檢查 URL 是否改變（某些平台登入成功後重新導向）

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 800-850

### 4. 多因素認證 (MFA)

#### 4.1 MFA 檢測
檢測是否需要進行多因素認證（如簡訊驗證、電子郵件驗證、OTP）。

**MFA 頁面特徵**：
- 顯示「驗證碼已發送至您的手機」或電子郵件
- 包含數字輸入欄（通常 4-8 位數）
- 顯示「重新發送驗證碼」選項
- 倒數計時器

#### 4.2 MFA 處理
目前系統對 MFA 的支持有限，採用以下策略：

**策略**：
1. 偵測到 MFA 時，提供清晰的提示
2. 等待使用者手動輸入驗證碼（在 Web UI 上）
3. 記錄 MFA 失敗次數，超過限制時停止

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 850-900

---

## 平台特定認證

### TixCraft

**認證機制**：
- 優先使用 Cookie（`tixcraft_sessionid`）
- 支援帳號密碼登入（電子郵件 + 密碼）
- Cookie 通常有效期為 30 天

**相關設定**：
```json
{
  "ticket_account": {
    "tixcraft": {
      "email": "your@email.com",
      "password": "your_password"
    }
  }
}
```

**Cookie 取得方法**：
1. 訪問 https://tixcraft.com
2. 登入帳號
3. 開啟瀏覽器開發者工具 (F12)
4. 檢查 Cookies，複製 `tixcraft_sessionid`

### KKTIX

**認證機制**：
- 使用 `KKTIX_SESSION` Cookie
- 支援帳號密碼登入（通常是帳號 + 密碼）
- Cookie 有效期通常較短（7-14 天）

**相關設定**：
```json
{
  "ticket_account": {
    "kktix": {
      "account": "your_account",
      "password": "your_password"
    }
  }
}
```

### iBon

**認證機制**：
- 使用 `IBON_SESSION` 或類似 Cookie
- 某些活動需要會員登入
- 支援帳號密碼登入

### TicketPlus

**認證機制**：
- 需要帳號登入
- 可能有額外的地理位置驗證

### KHAM

**認證機制**：
- 某些活動開放登入
- 支援帳號密碼或第三方登入

---

## 成功標準

**SC-005: 身份認證成功率** ≥ 95%
- 成功完成認證的次數 / 總認證嘗試次數

**SC-009: 錯誤恢復能力** ≥ 90%
- 認證失敗時能夠提供清晰錯誤訊息或自動回退

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-006 | Cookie 認證 | ✅ 實作 |
| FR-007 | 帳號密碼認證 | ✅ 實作 |
| FR-008 | MFA 基本支持 | 🔄 部分實作 |

---

## 故障排除

### 問題 1: Cookie 認證失敗
**症狀**：Cookie 注入後仍被要求登入

**可能原因**：
- Cookie 已過期
- Cookie 格式不正確
- 平台更改了認證機制

**解決方案**：
1. 重新取得 Cookie（清除舊 Cookie）
2. 驗證 Cookie 格式是否正確
3. 檢查 Cookie 是否含有過期時間戳

### 問題 2: 帳號密碼登入失敗
**症狀**：帳號密碼填寫後無法登入

**可能原因**：
- 帳號或密碼錯誤
- 帳號已被鎖定（多次失敗嘗試）
- 平台有額外的安全檢查（IP 限制、設備驗證）

**解決方案**：
1. 驗證帳號密碼正確性
2. 手動登入以確認帳號狀態
3. 檢查平台的安全設定

### 問題 3: MFA 無法處理
**症狀**：進行到 MFA 頁面後無法繼續

**可能原因**：
- 系統不支援該 MFA 方式
- 使用者未收到驗證碼

**解決方案**：
1. 臨時在 Web UI 手動完成 MFA
2. 使用已認證的 Cookie 來回避 MFA
3. 聯繫平台支持

---

## 最佳實踐

### ✅ 推薦做法

1. **優先使用 Cookie 認證**
   - 最快速且最可靠
   - 減少反偵測風險
   ```python
   config_dict['ticket_account']['cookies'] = {'tixcraft_sessionid': '...'}
   ```

2. **定期更新 Cookie**
   - 建議每週至少手動更新一次
   - 特別是在購票季節前

3. **妥善儲存敏感信息**
   - 不要將帳號密碼提交到 Git
   - 使用環境變數或加密配置文件

4. **實現認證失敗回退**
   - Cookie 失敗 → 嘗試帳號密碼
   - 認證完全失敗 → 提供清晰錯誤訊息

### ❌ 避免做法

1. ❌ 硬編碼帳號密碼到程式碼中
   - 應使用配置文件

2. ❌ 無限期保存過期的 Cookie
   - Cookie 應定期更新

3. ❌ 在登入失敗時無提示地跳過認證
   - 應記錄警告並提示使用者

4. ❌ 嘗試自動繞過 MFA
   - 應尊重平台的安全機制

---

## 開發檢查清單

- [ ] Cookie 認證邏輯正確
- [ ] 帳號密碼登入邏輯正確
- [ ] MFA 偵測正確
- [ ] 認證失敗訊息清晰
- [ ] 所有平台認證測試通過
- [ ] 認證狀態驗證正確
- [ ] 敏感信息妥善儲存

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: ✅ Phase 3 進行中

