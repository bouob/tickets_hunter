# 🚀 Tickets Hunter 打包快速開始

---

## 📦 一鍵打包與測試

### 使用方法

```batch
cd build_scripts
build_and_test.bat

REM 或者從專案根目錄執行
build_scripts\build_and_test.bat
```

**注意**：腳本會自動安裝依賴，從 `build_scripts/` 執行即可。

### 功能特點

✅ **自動化依賴管理**
- 自動檢測並安裝 requirement.txt 所有依賴
- 自動安裝 PyInstaller

✅ **完整打包流程**
- 打包 3 個 exe（nodriver_tixcraft, settings, config_launcher）
- 自動整合 `_internal/` 依賴目錄（共用依賴，減少總大小）
- 複製共用資源（webdriver/, assets/, www/）

✅ **自動化測試**
- 執行 30 秒啟動測試
- 驗證核心模組載入（util, NonBrowser, ddddocr）
- 測試結果保存至 `.temp/test_output.txt`

✅ **發布 ZIP 生成**
- 自動打包成 `dist/release/tickets_hunter_v{VERSION}.zip`
- 版本號自動從 Git tag 讀取

### 輸出檔案

- `dist/release/tickets_hunter_v2025.11.03.zip` - 發布 ZIP
- `.temp/test_output.txt` - 測試輸出記錄

### 執行時間

約 10-20 分鐘（視硬體效能）

---

## 🧪 測試打包結果

### 方法 A：Windows Sandbox（推薦）

```batch
1. 啟動 Windows Sandbox
2. 複製 ZIP 到 Sandbox 桌面
3. 解壓縮並測試 3 個 exe
```

### 方法 B：開發機快速測試

```batch
cd dist\tickets_hunter
config_launcher.exe       # 測試 GUI
settings.exe              # 測試網頁介面
```

---

## 📤 發布到 GitHub Release

### Step 1: 更新版本號

編輯 3 個檔案的 `CONST_APP_VERSION`：
- `src/nodriver_tixcraft.py`
- `src/config_launcher.py`
- `src/settings.py`

### Step 2: 更新 CHANGELOG.md

記錄本次版本的更新內容。

### Step 3: 提交並推送 Tag

```batch
git add .
git commit -m "chore: bump version to 2025.11.03"
git push origin main

git tag v2025.11.03
git push origin v2025.11.03
```

### Step 4: GitHub Actions 自動執行

前往 GitHub → Actions，查看自動化打包進度（約 15-25 分鐘）。

### Step 5: 驗證 Release

前往 GitHub → Releases，下載並測試 ZIP 檔案。

---

## 📁 檔案結構參考

### 打包前（專案結構）
```
tickets_hunter/
├── src/                        原始碼
├── build_scripts/              打包腳本
│   ├── build_and_test.bat      ← 一鍵打包測試
│   ├── *.spec                  ← PyInstaller 配置（3 個）
│   ├── README_Build.md         ← 開發者指南
│   ├── README_Release.txt      ← 使用者說明
│   └── QUICK_START.md          ← 本文件
├── requirement.txt             依賴清單
└── CHANGELOG.md                版本記錄
```

### 打包後（輸出結構）
```
dist/
├── tickets_hunter/             整合目錄
│   ├── nodriver_tixcraft.exe
│   ├── settings.exe
│   ├── config_launcher.exe
│   ├── _internal/              共用依賴（3 個 exe 共用）
│   ├── assets/
│   ├── www/
│   └── settings.json
└── release/
    └── tickets_hunter_v2025.11.03.zip      ← 發布 ZIP

.temp/
└── test_output.txt             ← 測試輸出記錄（build_and_test.bat）
```

---

## 🆘 常見問題

### Q1: 如何在虛擬機中測試？
**A**: 查看 `VM_TEST_GUIDE.md`，有完整的虛擬機測試步驟。

### Q2: 打包失敗怎麼辦？
**A**: 查看 `README_Build.md` 的「疑難排解」章節。

### Q3: 如何確保 exe 不依賴本地 Python？
**A**: 使用 Windows Sandbox 或虛擬機測試（沒有安裝 Python）。

### Q4: GitHub Actions 打包失敗？
**A**: 檢查 GitHub → Actions → Build and Release → 查看錯誤 log。

### Q5: 使用者回報 exe 無法執行？
**A**:
1. 確認 `_internal/` 資料夾與 exe 在同一目錄
2. 檢查 Windows Defender 是否阻擋
3. 提供 `README_Release.txt` 給使用者

---

## 📚 詳細文件

- **開發者打包指南**：`README_Build.md`
- **虛擬機測試指南**：`VM_TEST_GUIDE.md`
- **使用者使用說明**：`README_Release.txt`（會包入 ZIP）

---

## ⚡ 快速參考表

| 目標 | 使用方法 | 時間 | 輸出 |
|------|---------|------|------|
| 本地打包與測試 | `build_and_test.bat` | 10-20 分鐘 | ZIP + 測試輸出 |
| 更新版本號 | `/gupdate` 指令 | < 1 分鐘 | 更新 3 個檔案 |
| GitHub 自動發布 | 推送 tag | 15-25 分鐘 | GitHub Release |

---

**最後更新**：2025-11-04
