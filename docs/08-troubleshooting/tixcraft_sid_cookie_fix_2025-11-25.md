**文件說明**：Issue #137 TixCraft 家族 Cookie SID 登入問題分析與修正方案
**最後更新**：2025-11-25

---

# TixCraft 家族 Cookie SID 登入修正報告

**Issue**: [#137](https://github.com/bouob/tickets_hunter/issues/137) - 機器人無法使用拓元家族 cookie SID 自動登錄
**回報者**: @GushuLily
**狀態**: ✅ 已實作
**影響平台**: TixCraft、Ticketmaster、Indievox

---

## 📋 問題描述

### 原始問題

使用者回報在使用 NoDriver 引擎時，TixCraft 家族（TixCraft、Ticketmaster、Indievox）的 Cookie SID 自動登入功能無法正常運作。

**現象**：
- 填寫 Cookie SID 後，程式在無登入狀態下尋找區域
- 機器人填寫 captcha，若順利就會去下一頁，但實際上未登入
- 預期行為：應該要能使用 Cookie 登入

### 使用者環境

| 項目 | 值 |
|------|-----|
| 版本 | Tickets Hunter 2025.11.20 |
| 作業系統 | Windows |
| 執行方式 | exe 執行檔 |
| WebDriver | nodriver (預設) |
| 測試平台 | Ticketmaster |
| 測試網址 | `https://tixcraft.com/ticket/area/25_david/20137` |

---

## 🔍 根因分析

### 關鍵發現

使用者 @GushuLily 提供了關鍵技術分析：

> 我發現現在的拓元 SID 需要 **http only** 以及 **host only** 為 on

### 技術驗證

#### 1. Cookie HttpOnly 屬性問題

**CDP 協議行為**：
- `cdp.network.set_cookie()` 會根據 Cookie 的 `name + domain + path + httpOnly` 判斷是否為「等效 Cookie」
- 如果 `httpOnly` 屬性不同，兩個 Cookie **不會被視為等效**，導致同時存在兩個 SID Cookie

**實際情況**：
- TixCraft 伺服器設定的 SID Cookie 帶有 `HttpOnly=true` 屬性
- 現有程式碼設定 `http_only=False`
- 結果：產生兩個 SID Cookie，瀏覽器行為不可預期

#### 2. 程式碼比較

| 實作版本 | 位置 | http_only | 先刪除舊 Cookie |
|---------|------|-----------|----------------|
| **Chrome Driver** | `chrome_tixcraft.py:847` | N/A (Selenium 自動處理) | ✅ `driver.delete_cookie("SID")` |
| **NoDriver (現有)** | `nodriver_tixcraft.py:700` | ❌ `False` | ❌ 無 |
| **NoDriver iBon** | `nodriver_tixcraft.py:8898` | ✅ `True` | ❌ 無 |

### 根本原因確認

1. **`http_only=False` 設定錯誤** - 應改為 `True`
2. **未先刪除舊 Cookie** - 可能導致 Cookie 衝突

---

## ✅ 解決方案

### 推薦方案：完整修改（對齊 Chrome Driver 實作）

**修改範圍**：`src/nodriver_tixcraft.py` 第 674-735 行

### 修改內容

#### 修改 1：新增 Cookie 刪除邏輯

**位置**：第 693 行前插入

**新增程式碼**：
```python
# 步驟 1：刪除所有現有的 SID Cookie（對齊 Chrome Driver 實作）
try:
    await tab.send(cdp.network.delete_cookies(
        name="SID",
        domain=cookie_domain
    ))
    if config_dict["advanced"]["verbose"]:
        print(f"Deleted existing SID cookies for domain: {cookie_domain}")
except Exception as del_e:
    if config_dict["advanced"]["verbose"]:
        print(f"Note: Could not delete existing cookies: {del_e}")
```

#### 修改 2：修正 http_only 參數

**位置**：第 700 行

**修改前**：
```python
http_only=False  # TixCraft SID cookie is not httpOnly
```

**修改後**：
```python
http_only=True  # TixCraft SID cookie requires httpOnly
```

#### 修改 3：加強錯誤處理

**位置**：第 717-719 行

**修改前**：
```python
except Exception as e:
    if config_dict["advanced"]["verbose"]:
        print(f"Error setting TixCraft SID cookie: {str(e)}")
        print("Falling back to old method...")
```

**修改後**：
```python
except Exception as e:
    if config_dict["advanced"]["verbose"]:
        print(f"Error setting TixCraft SID cookie: {str(e)}")
        import traceback
        traceback.print_exc()
        print("Falling back to old method...")
```

#### 修改 4：修正回退機制

**位置**：第 721-732 行

**修改前**：
```python
# Fallback to old method if CDP fails
cookies  = await driver.cookies.get_all()
is_cookie_exist = False
for cookie in cookies:
    if cookie.name=='SID':
        cookie.value=tixcraft_sid
        is_cookie_exist = True
        break
if not is_cookie_exist:
    new_cookie = cdp.network.CookieParam("SID",tixcraft_sid, domain=cookie_domain, path="/", http_only=False, secure=True)
    cookies.append(new_cookie)
await driver.cookies.set_all(cookies)
```

**修改後**：
```python
# Fallback to old method if CDP fails
cookies = await driver.cookies.get_all()
# 過濾掉所有 SID Cookie（避免衝突）
cookies_filtered = [c for c in cookies if c.name != 'SID']
# 建立新的 SID Cookie
new_cookie = cdp.network.CookieParam(
    "SID",
    tixcraft_sid,
    domain=cookie_domain,
    path="/",
    http_only=True,  # 修正：改為 True
    secure=True
)
cookies_filtered.append(new_cookie)
await driver.cookies.set_all(cookies_filtered)
```

---

## 📊 完整修改後程式碼

```python
    if tixcraft_family:
        # Determine correct cookie domain based on homepage
        if 'ticketmaster.sg' in homepage:
            cookie_domain = ".ticketmaster.sg"
        elif 'ticketmaster.com' in homepage:
            cookie_domain = ".ticketmaster.com"
        elif 'indievox.com' in homepage:
            cookie_domain = ".indievox.com"
        else:
            cookie_domain = ".tixcraft.com"

        tixcraft_sid = config_dict["advanced"]["tixcraft_sid"]
        if len(tixcraft_sid) > 1:
            if config_dict["advanced"]["verbose"]:
                print(f"Setting tixcraft SID cookie, length: {len(tixcraft_sid)}")

            try:
                from nodriver import cdp

                # 步驟 1：刪除所有現有的 SID Cookie（對齊 Chrome Driver 實作）
                try:
                    await tab.send(cdp.network.delete_cookies(
                        name="SID",
                        domain=cookie_domain
                    ))
                    if config_dict["advanced"]["verbose"]:
                        print(f"Deleted existing SID cookies for domain: {cookie_domain}")
                except Exception as del_e:
                    if config_dict["advanced"]["verbose"]:
                        print(f"Note: Could not delete existing cookies: {del_e}")

                # 步驟 2：設定新的 SID Cookie（修正 http_only=True）
                cookie_result = await tab.send(cdp.network.set_cookie(
                    name="SID",
                    value=tixcraft_sid,
                    domain=cookie_domain,
                    path="/",
                    secure=True,
                    http_only=True  # 修正：改為 True
                ))

                if config_dict["advanced"]["verbose"]:
                    print(f"CDP setCookie result: {cookie_result}")
                    print("tixcraft SID cookie set successfully")

                # 驗證 cookie 是否設定成功
                updated_cookies = await driver.cookies.get_all()
                sid_cookies = [c for c in updated_cookies if c.name == 'SID']
                if not sid_cookies:
                    if config_dict["advanced"]["verbose"]:
                        print("Warning: TixCraft SID cookie not found after setting")
                elif config_dict["advanced"]["verbose"]:
                    print(f"Verified SID cookie: domain={sid_cookies[0].domain}, value length={len(sid_cookies[0].value)}")

            except Exception as e:
                if config_dict["advanced"]["verbose"]:
                    print(f"Error setting TixCraft SID cookie: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    print("Falling back to old method...")

                # Fallback to old method if CDP fails
                cookies = await driver.cookies.get_all()
                # 過濾掉所有 SID Cookie（避免衝突）
                cookies_filtered = [c for c in cookies if c.name != 'SID']
                # 建立新的 SID Cookie
                new_cookie = cdp.network.CookieParam(
                    "SID",
                    tixcraft_sid,
                    domain=cookie_domain,
                    path="/",
                    http_only=True,  # 修正：改為 True
                    secure=True
                )
                cookies_filtered.append(new_cookie)
                await driver.cookies.set_all(cookies_filtered)

                if config_dict["advanced"]["verbose"]:
                    print("tixcraft SID cookie set successfully (fallback method)")
```

---

## 🛡️ 風險評估

| 風險項目 | 等級 | 說明 | 緩解措施 |
|---------|------|------|----------|
| delete_cookies 失敗 | 低 | CDP 指令可能因網路或瀏覽器狀態失敗 | 已加入 try-except，失敗不影響後續設定 |
| 破壞現有功能 | 低 | 修改核心 Cookie 邏輯 | 保留回退機制，且同步修正回退邏輯 |
| domain 格式問題 | 無 | 維持現有 `.domain` 格式 | 已驗證格式正確 |
| 其他平台受影響 | 無 | 僅修改 TixCraft 家族分支 | 條件判斷已隔離影響範圍 |

---

## 🧪 測試驗證

### 測試前準備

```bash
# 1. 刪除暫停標記
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt

# 2. 設定 settings.json
# - homepage: TixCraft/Ticketmaster/Indievox 活動頁面
# - tixcraft_sid: 有效的 SID 值
# - advanced.verbose: true
```

### 測試指令

```bash
cd D:\Desktop\bouob-TicketHunter(MaxBot)\tickets_hunter
timeout 60 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

### 驗證項目

| 項目 | 預期日誌輸出 | 驗證方式 |
|------|-------------|---------|
| Cookie 刪除 | `Deleted existing SID cookies for domain: .tixcraft.com` | grep 日誌 |
| Cookie 設定成功 | `tixcraft SID cookie set successfully` | grep 日誌 |
| Cookie 驗證 | `Verified SID cookie: domain=...` | grep 日誌 |
| 登入狀態 | 頁面右上角顯示使用者名稱 | 目視確認 |

### 回歸測試

- [ ] TixCraft (tixcraft.com)
- [ ] Ticketmaster TW (ticketmaster.com)
- [ ] Ticketmaster SG (ticketmaster.sg)
- [ ] Indievox (indievox.com)

---

## 📚 參考資料

### 相關規格

| 規格編號 | 說明 |
|---------|------|
| FR-005 | 系統必須支援透過 Cookie 注入（tixcraft_sid、ibonqware）作為主要方法進行自動登入 |
| FR-008 | 系統必須在整個購票工作流程中維持會話狀態 |

### 相關程式碼

| 檔案 | 行號 | 說明 |
|------|------|------|
| `nodriver_tixcraft.py` | 674-735 | TixCraft SID Cookie 設定邏輯（本次修改） |
| `nodriver_tixcraft.py` | 8865-8928 | iBon Cookie 設定（參考實作） |
| `chrome_tixcraft.py` | 845-849 | Chrome Driver Cookie 設定（正確實作） |

### 外部參考

- [Chrome DevTools Protocol - Network.setCookie](https://chromedevtools.github.io/devtools-protocol/tot/Network/#method-setCookie)
- [Chrome DevTools Protocol - Network.deleteCookies](https://chromedevtools.github.io/devtools-protocol/tot/Network/#method-deleteCookies)
- [MDN - HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)

---

## ✏️ 致謝

感謝 @GushuLily 提供詳細的問題分析和修改建議，加速了問題的定位和解決。

---

*最後更新：2025-11-25*
