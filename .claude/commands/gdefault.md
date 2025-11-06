---
description: "清除本地敏感設定檔案，避免提交到 Git"
allowed-tools: ["Bash"]
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

# 清除本地敏感設定檔案

此指令用於在執行 `/gsave` 或 `/gpush` 之前，清理本地的敏感設定檔案，避免個人測試資料或敏感資訊被提交到 Git。

## 執行步驟

### 1. 列出需要清理的檔案

執行以下指令檢查哪些敏感檔案存在：

```bash
cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter"
echo "=== 檢查需要清理的設定檔案 ==="
ls -lh src/settings.json 2>/dev/null && echo "[✓] src/settings.json" || echo "[✗] src/settings.json"
ls -lh src/config_launcher.json 2>/dev/null && echo "[✓] src/config_launcher.json" || echo "[✗] src/config_launcher.json"
ls -lh src/MAXBOT_LAST_URL.txt 2>/dev/null && echo "[✓] src/MAXBOT_LAST_URL.txt" || echo "[✗] src/MAXBOT_LAST_URL.txt"
ls -lh src/MAXBOT_INT28_IDLE.txt 2>/dev/null && echo "[✓] src/MAXBOT_INT28_IDLE.txt" || echo "[✗] src/MAXBOT_INT28_IDLE.txt"
ls -lh src/webdriver/Maxbotplus_1.0.0/data/settings.json 2>/dev/null && echo "[✓] Maxbotplus settings.json" || echo "[✗] Maxbotplus settings.json"
ls -lh src/webdriver/Maxblockplus_1.0.0/data/settings.json 2>/dev/null && echo "[✓] Maxblockplus settings.json" || echo "[✗] Maxblockplus settings.json"
ls -lh src/webdriver/Maxbotplus_1.0.0/data/status.json 2>/dev/null && echo "[✓] Maxbotplus status.json" || echo "[✗] Maxbotplus status.json"
ls -lh src/webdriver/Maxblockplus_1.0.0/data/status.json 2>/dev/null && echo "[✓] Maxblockplus status.json" || echo "[✗] Maxblockplus status.json"
ls -lh src/webdriver/chromedriver.exe 2>/dev/null && echo "[✓] src/webdriver/chromedriver.exe" || echo "[✗] src/webdriver/chromedriver.exe"
```

### 2. 清除敏感設定檔案

刪除本地測試用的設定檔案：

```bash
echo ""
echo "=== 開始清除敏感設定檔案 ==="

# 主目錄設定檔案
rm -f src/settings.json && echo "[✓] 已刪除 src/settings.json" || echo "[✗] 無法刪除 src/settings.json"
rm -f src/config_launcher.json && echo "[✓] 已刪除 src/config_launcher.json" || echo "[✗] 無法刪除 src/config_launcher.json"

# 臨時記錄檔案
rm -f src/MAXBOT_LAST_URL.txt && echo "[✓] 已刪除 MAXBOT_LAST_URL.txt" || echo "[✗] 無法刪除 MAXBOT_LAST_URL.txt"
rm -f src/MAXBOT_INT28_IDLE.txt && echo "[✓] 已刪除 MAXBOT_INT28_IDLE.txt" || echo "[✗] 無法刪除 MAXBOT_INT28_IDLE.txt"

# Webdriver extension 設定檔案
rm -f src/webdriver/Maxbotplus_1.0.0/data/settings.json && echo "[✓] 已刪除 Maxbotplus settings.json" || echo "[✗] 無法刪除 Maxbotplus settings.json"
rm -f src/webdriver/Maxblockplus_1.0.0/data/settings.json && echo "[✓] 已刪除 Maxblockplus settings.json" || echo "[✗] 無法刪除 Maxblockplus settings.json"

# Status 檔案（如果存在）
rm -f src/webdriver/Maxbotplus_1.0.0/data/status.json && echo "[✓] 已刪除 Maxbotplus status.json" || echo "[✗] 無法刪除 Maxbotplus status.json"
rm -f src/webdriver/Maxblockplus_1.0.0/data/status.json && echo "[✓] 已刪除 Maxblockplus status.json" || echo "[✗] 無法刪除 Maxblockplus status.json"

# ChromeDriver 執行檔
rm -f src/webdriver/chromedriver.exe && echo "[✓] 已刪除 chromedriver.exe" || echo "[✗] 無法刪除 chromedriver.exe"
```

### 3. 確認清理結果

再次檢查確認所有敏感檔案已被刪除：

```bash
echo ""
echo "=== 清理結果確認 ==="
echo "以下檔案應該都不存在了："
ls -lh src/settings.json 2>/dev/null && echo "[!] 警告：src/settings.json 仍然存在" || echo "[✓] src/settings.json 已清除"
ls -lh src/config_launcher.json 2>/dev/null && echo "[!] 警告：src/config_launcher.json 仍然存在" || echo "[✓] src/config_launcher.json 已清除"
ls -lh src/MAXBOT_LAST_URL.txt 2>/dev/null && echo "[!] 警告：MAXBOT_LAST_URL.txt 仍然存在" || echo "[✓] MAXBOT_LAST_URL.txt 已清除"
ls -lh src/webdriver/Maxbotplus_1.0.0/data/settings.json 2>/dev/null && echo "[!] 警告：Maxbotplus settings.json 仍然存在" || echo "[✓] Maxbotplus settings.json 已清除"
ls -lh src/webdriver/Maxblockplus_1.0.0/data/settings.json 2>/dev/null && echo "[!] 警告：Maxblockplus settings.json 仍然存在" || echo "[✓] Maxblockplus settings.json 已清除"
ls -lh src/webdriver/chromedriver.exe 2>/dev/null && echo "[!] 警告：chromedriver.exe 仍然存在" || echo "[✓] chromedriver.exe 已清除"
```

### 4. 檢查 Git 狀態

最後檢查 git 狀態，確認沒有敏感檔案會被提交：

```bash
echo ""
echo "=== 檢查 Git 狀態 ==="
git status --short
```

## 📋 說明

- **清理的檔案**：
  - `src/settings.json` - 主設定檔（包含帳號密碼等敏感資訊）
  - `src/config_launcher.json` - 啟動器設定
  - `src/MAXBOT_LAST_URL.txt` - 最後訪問的 URL 記錄
  - `src/MAXBOT_INT28_IDLE.txt` - 閒置狀態記錄
  - `src/webdriver/*/data/settings.json` - Chrome extension 設定檔
  - `src/webdriver/*/data/status.json` - Chrome extension 狀態檔
  - `src/webdriver/chromedriver.exe` - ChromeDriver 執行檔（避免版本衝突）

- **使用時機**：
  - 在執行 `/gsave` 之前
  - 在執行 `/gpush` 之前
  - 想要清除本地測試資料時

## ⚠️ 注意事項

1. 這些設定檔案會在下次執行程式時自動重建，不用擔心
2. 所有被清除的檔案都已經在 `.gitignore` 中，不會被提交
3. 程式會根據 `src/settings.json` 的內容自動生成 webdriver 的設定檔
