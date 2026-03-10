# 平台實作參考：Facebook（OAuth 登入輔助模組）

**文件說明**：Facebook OAuth 登入輔助模組的實作參考，涵蓋自動帳密填入、OAuth 跳轉處理等技術說明。
**最後更新**：2026-03-05

---

## 平台概述

**模組名稱**：Facebook OAuth 登入
**網站**：`www.facebook.com/login.php`
**角色**：輔助模組，非獨立票務平台
**主要功能**：為其他票務平台提供 Facebook OAuth 自動登入
**完成度**：100% ✅ (2/2 Functions)
**難度級別**：⭐ (低)

---

## 模組特性

### 核心特點
✅ **優勢**：
- 極簡實作，僅 2 個函式
- 自動填入 Facebook 帳號與密碼
- 自動按下 Enter 鍵送出登入
- 完成登入後由原平台接管流程

⚠️ **限制**：
- 不處理 Facebook 雙重驗證（2FA）
- 不處理安全警告頁面
- 僅在瀏覽器導向至 `facebook.com/login.php` 時觸發

### 運作機制

當使用者設定的票務平台（如 Cityline、KKTIX 等）使用 Facebook OAuth 登入時，瀏覽器會被重導向至 `facebook.com/login.php`。此時本模組自動：

1. 偵測 URL 前綴為 `https://www.facebook.com/login.php?`
2. 從 `config_dict` 讀取 Facebook 帳密
3. 自動填入帳號（`#email`）與密碼（`#pass`）
4. 按下 Enter 鍵送出登入表單
5. 等待 2 秒後由 OAuth 回調返回原平台

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Stage 2 | `nodriver_facebook_login()` | 328 | 自動填入帳密並送出 |
| Main | `nodriver_facebook_main()` | 14675 | 入口函式，讀取設定並呼叫 login |

**程式碼位置**：`src/nodriver_tixcraft.py`

---

## 12 階段實作摘要

| 階段 | 名稱 | 狀態 | 說明 |
|------|------|------|------|
| 1 | 環境初始化 | ⬜ 不適用 | 由主平台處理 |
| 2 | 身份驗證 | ✅ 完成 | 帳密自動填入 + Enter 送出 |
| 3 | 頁面監控 | ⬜ 不適用 | 由主平台處理 |
| 4 | 日期選擇 | ⬜ 不適用 | 非票務平台 |
| 5 | 區域選擇 | ⬜ 不適用 | 非票務平台 |
| 6 | 票數設定 | ⬜ 不適用 | 非票務平台 |
| 7 | CAPTCHA | ⬜ 不適用 | 非票務平台 |
| 8 | 表單填寫 | ⬜ 不適用 | 非票務平台 |
| 9 | 條款同意 | ⬜ 不適用 | 非票務平台 |
| 10 | 訂單送出 | ⬜ 不適用 | 非票務平台 |
| 11 | 排隊/付款 | ⬜ 不適用 | 非票務平台 |
| 12 | 錯誤處理 | ⬜ 不適用 | 非票務平台 |

**備註**：此模組為 OAuth 登入輔助，12 階段標準不完全適用。僅 Stage 2（身份驗證）為本模組職責。

---

## 已知問題與解決方案

### 1. 雙重驗證（2FA）
**問題**：若 Facebook 帳號啟用 2FA，自動登入後會停留在驗證碼頁面。
**解決方案**：目前需手動輸入 2FA 驗證碼。建議使用者在搶票前先手動完成 Facebook 登入。

### 2. 安全警告
**問題**：Facebook 可能因異常登入行為（新裝置、新 IP）顯示安全警告。
**解決方案**：建議使用者在搶票前先在同一瀏覽器手動登入一次 Facebook。

### 3. 帳號長度檢查
**問題**：程式碼中有 `len(facebook_account) > 4` 的最小長度檢查。
**解決方案**：確保 `settings.json` 中的 `facebook_account` 欄位填入完整 Email/電話。

---

## 設定建議

```json
{
  "accounts": {
    "facebook_account": "your_email@example.com",
    "facebook_password": "your_password"
  }
}
```

**安全提醒**：Facebook 帳密儲存於本機 `settings.json`，請確保該檔案不被提交至版本控制。

---

## 相關文件

- 📋 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - 函數索引
- 憑證保護規範 - 詳見專案安全規則

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2026-03 | 初版：Facebook OAuth 登入輔助模組參考文件 |
