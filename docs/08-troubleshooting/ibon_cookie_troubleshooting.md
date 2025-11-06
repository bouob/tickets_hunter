# ibon Cookie 自動登入問題排解指南

## 🔍 問題診斷

### 常見問題徵狀
1. **無法自動登入**：程式啟動後仍需手動登入
2. **重定向到登入頁**：自動跳轉到 `huiwan.ibon.com.tw/LoginHuiwan/UserLogin.aspx`
3. **Cookie 設定失敗**：除錯日誌顯示 cookie 相關錯誤

## 🛠️ 解決步驟

### 步驟 1: 檢查 Cookie 格式
確認 `settings.json` 中的 `ibonqware` 欄位格式正確：

```json
{
  "advanced": {
    "ibonqware": "mem_id=您的會員ID&mem_email=您的信箱&huiwanTK=認證令牌&ibonqwareverify=驗證碼"
  }
}
```

**正確格式範例：**
```
mem_id=92241746616563527292&mem_email=user@example.com&huiwanTK=ABC123...XYZ&ibonqwareverify=615898b4d4cf8477859f
```

### 步驟 2: 取得正確的 Cookie 值
1. **手動登入** ibon.com.tw
2. **開啟開發者工具** (F12)
3. **前往 Application/儲存體 → Cookies → https://ticket.ibon.com.tw**
4. **找到 `ibonqware` cookie**
5. **複製完整的 Value 值**

### 步驟 3: 啟用詳細除錯
在 `settings.json` 中設定：
```json
{
  "advanced": {
    "verbose": true
  }
}
```

### 步驟 4: 檢查除錯輸出
啟動程式後查看控制台輸出，應該包含：

```
Setting ibon cookie with length: XXX
Cookie contains mem_id: True
Cookie contains mem_email: True
Cookie contains huiwanTK: True
Cookie contains ibonqwareverify: True
ibon cookie set successfully
Verified: ibon cookie exists with value length: XXX
Cookie domain: .ibon.com.tw
Cookie path: /
Cookie secure: True
Reloading page to apply ibon cookie...
Checking ibon login status at URL: https://ticket.ibon.com.tw/
✅ ibon auto-login appears successful
```

### 步驟 5: 如果顯示登入失敗
如果看到 `❌ ibon auto-login may have failed`，請嘗試：

1. **手動重新整理頁面** - 有時需要額外的頁面刷新
2. **檢查 Cookie 是否過期** - 重新取得新的 Cookie 值
3. **確認網路連線** - 確保能正常訪問 ibon 網站

## 🧪 測試驗證

### 手動測試步驟
1. **清除瀏覽器 Cookie**
2. **啟動程式**並設定目標為 ibon 網站
3. **觀察除錯日誌**
4. **檢查是否成功登入**

### 驗證登入狀態
- **成功指標**：可以看到會員相關選單或登出連結
- **失敗指標**：出現登入按鈕或跳轉到登入頁面

### WebDriver 類型差異
- **Chrome/UC**: 使用 `driver.add_cookie()` 方法
- **NoDriver**: 使用 `await driver.cookies.set_all()` 方法

## ❌ 常見錯誤與解決方案

### 1. Cookie 格式錯誤
**錯誤：** 只有部分 `huiwanTK` 值，缺少其他參數
**解決：** 重新取得完整的 cookie 值

### 2. Domain 設定問題
**錯誤：** Cookie domain 設定為 `ibon.com.tw`
**解決：** 已修正為 `.ibon.com.tw` (注意前面的點)

### 3. Cookie 過期
**錯誤：** Cookie 已過期失效
**解決：** 重新登入並取得新的 cookie 值

### 4. 頁面載入時機問題
**現象：** Cookie 設定成功但登入檢查失敗
**原因：** 頁面需要重新載入才能套用 Cookie
**解決：** 程式已自動添加頁面重新載入，如仍有問題請手動重新整理

### 5. 登入狀態檢查誤判
**現象：** 實際已登入但系統顯示未登入
**原因：** ibon 網站結構變更導致檢查邏輯失效
**解決：** 手動檢查頁面是否顯示會員資訊或登出按鈕

### 6. WebDriver 類型不匹配
**錯誤：** 設定的 webdriver_type 與實際使用不符
**解決：** 確認 `settings.json` 中的 `webdriver_type` 設定

## 🔧 進階除錯

### 檢查 Cookie 是否生效
```python
# 在程式中添加此段代碼來檢查 cookie
cookies = driver.get_cookies()
for cookie in cookies:
    if cookie.get('name') == 'ibonqware':
        print(f"Found ibon cookie: {cookie}")
```

### 檢查當前 URL
```python
current_url = driver.current_url
print(f"Current URL: {current_url}")
if 'huiwan.ibon.com.tw' in current_url:
    print("被重定向到登入頁，Cookie 可能無效")
```

## 📝 注意事項

1. **隱私保護**：Cookie 包含個人登入資訊，請妥善保管
2. **時效性**：Cookie 有過期時間，建議定期更新
3. **網域限制**：Cookie 僅在 ibon.com.tw 網域下有效
4. **瀏覽器相容性**：不同 WebDriver 的 Cookie 處理方式略有差異

## 🆘 仍無法解決？

如果按照上述步驟仍無法解決問題：

1. **檢查網路連線**：確保能正常訪問 ibon 網站
2. **更新 WebDriver**：使用最新版本的 ChromeDriver
3. **清除快取**：清除瀏覽器快取和 Cookie
4. **手動登入測試**：確認帳號密碼正確且未被鎖定
5. **聯繫技術支援**：提供完整的除錯日誌

---

*最後更新：2024年*