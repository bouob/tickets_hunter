**文件說明**：Tickets Hunter 打包部署完整指南，涵蓋 GitHub Actions 自動化打包、本地測試打包、PyInstaller 技術細節與疑難排解。

**最後更新**：2025-11-24

---

# Tickets Hunter 打包部署指南

## 📋 目錄
1. [快速開始](#快速開始)
2. [打包流程概覽](#打包流程概覽)
3. [GitHub Actions 自動化打包](#github-actions-自動化打包)
4. [本地測試打包](#本地測試打包)
5. [PyInstaller 配置說明](#pyinstaller-配置說明)
6. [疑難排解](#疑難排解)
7. [進階主題](#進階主題)

---

## 快速開始

### 🎯 你想做什麼？

| 目標 | 使用方法 | 時間 | 說明 |
|------|---------|------|------|
| **本地測試打包** | `build_scripts\build_and_test.bat` | 10-20 分鐘 | 開發階段驗證打包結果 |
| **正式發布版本** | 推送 Git tag (`v2025.11.24`) | 15-25 分鐘 | GitHub Actions 自動打包並發布 |
| **了解技術細節** | 閱讀本文件 | 30 分鐘 | 深入理解 PyInstaller 配置 |

### ⚡ 最快方式

**本地測試打包**（開發階段）：
```batch
cd build_scripts
build_and_test.bat
```

**正式發布**（生產環境）：
```bash
# 1. 更新版本號（5 個檔案的 CONST_APP_VERSION）
/gupdate

# 2. 更新 CHANGELOG.md
# （手動編輯）

# 3. 提交並推送 tag
/gsave
/gpush
git tag v2025.11.24
git push private v2025.11.24

# 4. GitHub Actions 自動執行（15-25 分鐘）
# 前往 GitHub → Actions → Build and Release 查看進度

# 5. 驗證 Release
# 前往 GitHub → Releases → 下載並測試 ZIP
```

> 📖 **詳細流程請參閱** → [`build_scripts/QUICK_START.md`](../../build_scripts/QUICK_START.md)

---

## 打包流程概覽

### 🏗️ 打包架構

Tickets Hunter 使用 **雙軌打包策略**：

```
開發階段（本地）          生產階段（GitHub Actions）
    ↓                           ↓
build_and_test.bat         .github/workflows/build-release.yml
    ↓                           ↓
PyInstaller 打包            PyInstaller 打包
    ↓                           ↓
自動化測試                   建立 ZIP
    ↓                           ↓
生成測試報告                 發布 GitHub Release
```

### 📦 打包產物

**輸出結構**：
```
dist/
├── tickets_hunter/                    # 統一目錄（4 個 exe 共用依賴）
│   ├── nodriver_tixcraft.exe         # NoDriver 版本主程式
│   ├── chrome_tixcraft.exe            # Chrome/Selenium 版本主程式
│   ├── settings.exe                   # 網頁設定介面
│   ├── config_launcher.exe            # 多設定檔管理器
│   ├── _internal/                     # 共用依賴（Python runtime + 模組）
│   │   ├── python310.dll
│   │   ├── ddddocr/
│   │   ├── selenium/
│   │   ├── nodriver/
│   │   └── ... (其他依賴)
│   ├── webdriver/                     # 瀏覽器擴充套件
│   │   ├── Maxbotplus_1.0.0/
│   │   └── Maxblockplus_1.0.0/
│   ├── assets/                        # 資源檔案（音效等）
│   ├── www/                           # 網頁介面資源
│   ├── README_Release.txt             # 使用者說明
│   └── CHANGELOG.md                   # 更新記錄
└── release/
    └── tickets_hunter_v2025.11.24.zip # 發布 ZIP（含上述所有內容）
```

### 🎯 設計理念

1. **統一依賴目錄**：4 個 exe 共用 `_internal/`，減少總大小
2. **自動生成設定**：不打包 `settings.json`，由程式自動生成
3. **自動下載驅動**：不打包 `chromedriver.exe`，由 `settings.exe` 自動下載
4. **資源分離**：靜態資源（webdriver, assets, www）與 Python 依賴分離

---

## GitHub Actions 自動化打包

### 🤖 自動化流程

**觸發條件**：推送 Git tag（格式：`v*`，例如 `v2025.11.24`）

**執行步驟**：
1. **環境準備**：設定 Python 3.10.11 環境
2. **安裝依賴**：安裝 `requirement.txt` + PyInstaller
3. **打包 4 個 exe**：
   - `nodriver_tixcraft.exe`（NoDriver 版本，最大）
   - `chrome_tixcraft.exe`（Chrome/Selenium 版本）
   - `settings.exe`（網頁設定介面）
   - `config_launcher.exe`（多設定檔管理器）
4. **整合統一目錄**：
   - 複製 4 個 exe 到 `dist/tickets_hunter/`
   - 合併 4 個 `_internal/` 目錄（共用依賴）
   - 複製資源目錄（webdriver, assets, www）
   - 複製文件（README_Release.txt, CHANGELOG.md）
5. **建立 ZIP**：壓縮統一目錄為 `tickets_hunter_v{VERSION}.zip`
6. **發布 Release**：
   - 自動提取 CHANGELOG.md 對應版本的更新內容
   - 建立 Draft Release（需手動 Publish）
   - 上傳 ZIP 檔案

### 📋 配置檔案

**位置**：`.github/workflows/build-release.yml`

**關鍵配置**：
```yaml
on:
  push:
    tags:
      - 'v*'  # 觸發條件：推送 v 開頭的 tag

jobs:
  build-windows:
    runs-on: windows-latest

    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10.11'  # 固定 Python 版本

      - name: Build executables with PyInstaller
        run: |
          python -m PyInstaller build_scripts/nodriver_tixcraft.spec --clean --noconfirm
          python -m PyInstaller build_scripts/chrome_tixcraft.spec --clean --noconfirm
          python -m PyInstaller build_scripts/settings.spec --clean --noconfirm
          python -m PyInstaller build_scripts/config_launcher.spec --clean --noconfirm

      - name: Create unified directory structure
        # 整合 4 個 exe 與 _internal/ 依賴

      - name: Extract CHANGELOG for release notes
        # 自動提取 CHANGELOG.md 對應版本的更新內容
```

### 🔍 監控與驗證

**查看打包進度**：
1. 前往 GitHub 倉庫
2. 點擊 **Actions** 標籤
3. 選擇 **Build and Release** workflow
4. 查看執行狀態（約 15-25 分鐘）

**驗證 Release**：
1. 前往 GitHub 倉庫
2. 點擊 **Releases** 標籤
3. 下載最新版本的 ZIP 檔案
4. 在乾淨環境（Windows Sandbox 或虛擬機）測試所有 exe

---

## 本地測試打包

### 🧪 測試目的

在推送 tag 觸發 GitHub Actions **之前**，先在本地驗證打包結果，避免浪費 CI/CD 時間。

### ⚙️ 測試腳本

**位置**：`build_scripts/build_and_test.bat`

**功能特點**：
- ✅ 自動安裝依賴（`requirement.txt` + PyInstaller）
- ✅ 打包 4 個 exe（與 GitHub Actions 相同流程）
- ✅ 整合統一目錄（與 GitHub Actions 相同結構）
- ✅ 自動化測試（13 項檢查）
- ✅ 生成測試報告（`test_report_{VERSION}.txt`）
- ✅ 生成發布 ZIP（`tickets_hunter_v{VERSION}.zip`）

### 🚀 執行方式

**方法 A：從 `build_scripts/` 執行**（推薦）
```batch
cd build_scripts
build_and_test.bat
```

**方法 B：從專案根目錄執行**
```batch
build_scripts\build_and_test.bat
```

### 📊 測試項目

腳本會自動執行以下測試：

**結構測試**（Test 1-11）：
1. 檢查 4 個 exe 是否存在
2. 檢查 `_internal/` 目錄是否存在
3. 檢查 `python310.dll` 是否存在
4. 檢查 `ddddocr` 模組是否存在
5. 檢查 `selenium` 模組是否存在
6. 檢查 `onnxruntime` 模組是否存在
7. 檢查 `webdriver/` 目錄是否存在
8. 檢查 `assets/` 目錄是否存在
9. 檢查 `www/` 目錄是否存在
10. 檢查 `settings.json` 是否被排除（應該不存在）
11. 檢查 ZIP 檔案是否生成

**啟動測試**（Test 12-13）：
12. 測試 `config_launcher.exe` 是否可啟動（3 秒自動關閉）
13. 測試 `settings.exe` 是否可啟動（3 秒自動關閉）

### 📄 測試報告

**位置**：`dist/release/test_report_{VERSION}.txt`

**報告內容**：
- 測試日期與環境資訊（Python 版本）
- 測試結果摘要（通過/失敗數量）
- 詳細測試結果（逐項列出）
- 打包產物資訊（ZIP 大小、exe 大小）
- 下一步建議（成功則建議推送 tag，失敗則建議修復）

### 🖥️ 進階測試

**Windows Sandbox 測試**（推薦）：
```batch
# 1. 啟動 Windows Sandbox
# 2. 複製 ZIP 到 Sandbox 桌面
# 3. 解壓縮並測試 4 個 exe
# 4. 驗證是否缺少 DLL 或模組
```

**虛擬機測試**：
- 使用乾淨的 Windows 10/11 虛擬機（無 Python 環境）
- 安裝 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 測試所有功能是否正常

---

## PyInstaller 配置說明

### 📋 .spec 配置檔案

Tickets Hunter 使用 **4 個獨立的 .spec 配置檔**，每個對應一個 exe：

| 配置檔 | 對應程式 | 說明 |
|--------|---------|------|
| `nodriver_tixcraft.spec` | `nodriver_tixcraft.exe` | NoDriver 版本主程式（最大） |
| `chrome_tixcraft.spec` | `chrome_tixcraft.exe` | Chrome/Selenium 版本主程式 |
| `settings.spec` | `settings.exe` | 網頁設定介面 |
| `config_launcher.spec` | `config_launcher.exe` | 多設定檔管理器 |

### 🔧 配置結構

**以 `nodriver_tixcraft.spec` 為例**：

```python
# -*- mode: python ; coding: utf-8 -*-

# =============================================================================
# Tickets Hunter - NoDriver Version Build Specification
# =============================================================================

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# 收集 ddddocr 資料檔案（ONNX 模型、字體等）
datas = collect_data_files('ddddocr')

a = Analysis(
    ['../src/nodriver_tixcraft.py'],  # 主程式入口
    pathex=[],
    binaries=[],
    datas=datas,  # 資料檔案
    hiddenimports=[
        # NoDriver 相關
        'nodriver',
        'nodriver.cdp',
        'nodriver.core.config',
        # Selenium 相關
        'selenium',
        'selenium.webdriver',
        # 驗證碼辨識
        'ddddocr',
        'onnxruntime',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        # 影像處理
        'cv2',
        'PIL',
        # 網路
        'urllib3',
        'websockets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型套件
        'matplotlib',
        'numpy.distutils',
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],  # 資料夾模式：不包含 binaries
    exclude_binaries=True,  # 啟用資料夾模式
    name='nodriver_tixcraft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用 UPX 壓縮
    console=True,  # 保留命令列視窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nodriver_tixcraft',
)
```

### 🎯 關鍵配置項

#### 1. `datas` - 資料檔案

**目的**：打包非 Python 程式碼的資源檔案

**Tickets Hunter 策略**：
- ✅ 打包 `ddddocr` 資料檔案（使用 `collect_data_files()`）
- ❌ **不打包** `webdriver/`, `assets/`, `www/`（改用 xcopy 複製）
- ❌ **不打包** `settings.json`（由程式自動生成）

**原因**：
- PyInstaller 的 `datas` 會將檔案壓縮到 `_internal/`
- 直接複製目錄更可靠，使用者也可自行修改

#### 2. `hiddenimports` - 隱藏導入

**目的**：明確指定動態導入的模組（PyInstaller 無法自動偵測）

**Tickets Hunter 必要模組**：
```python
hiddenimports=[
    # NoDriver（反偵測 WebDriver）
    'nodriver',
    'nodriver.cdp',
    'nodriver.core.config',

    # Selenium（標準 WebDriver）
    'selenium',
    'selenium.webdriver',

    # 驗證碼辨識（ddddocr + ONNX Runtime）
    'ddddocr',
    'onnxruntime',
    'onnxruntime.capi.onnxruntime_pybind11_state',  # 重要！缺少會導致 ddddocr 無法使用

    # 影像處理
    'cv2',  # OpenCV
    'PIL',  # Pillow

    # 網路
    'urllib3',
    'websockets',
]
```

#### 3. `excludes` - 排除模組

**目的**：減少打包大小，排除不需要的大型套件

**Tickets Hunter 排除清單**：
```python
excludes=[
    'matplotlib',      # 繪圖庫（不需要）
    'numpy.distutils', # NumPy 編譯工具（不需要）
    'tkinter',         # GUI 框架（不需要，我們使用網頁介面）
    'test',            # 測試模組
    'unittest',        # 單元測試模組
]
```

#### 4. `exclude_binaries=True` - 資料夾模式

**目的**：將依賴檔案放到 `_internal/` 目錄，而非打包成單一 exe

**優點**：
- ✅ 啟動速度快（無需解壓縮）
- ✅ 易於除錯（可直接查看依賴檔案）
- ✅ 支援多個 exe 共用依賴（節省空間）

**缺點**：
- ❌ 需要分發整個資料夾（不過我們會打包成 ZIP）

#### 5. `console=True` - 保留命令列視窗

**目的**：顯示執行日誌，方便使用者查看進度

**Tickets Hunter 策略**：
- ✅ `nodriver_tixcraft.exe` - 保留 console（查看搶票日誌）
- ✅ `chrome_tixcraft.exe` - 保留 console（查看搶票日誌）
- ✅ `settings.exe` - 保留 console（查看伺服器日誌）
- ❌ `config_launcher.exe` - 隱藏 console（GUI 程式）

### 🔍 常見問題

#### Q1: 為什麼不使用 `--onefile` 單一檔案模式？

**原因**：
1. **啟動慢**：單一 exe 需要先解壓縮到暫存目錄（5-10 秒）
2. **檔案大**：無法共用依賴，每個 exe 都包含完整 runtime（總大小 1GB+）
3. **不易除錯**：無法直接查看依賴檔案

**Tickets Hunter 選擇**：
- 使用資料夾模式（`exclude_binaries=True`）
- 4 個 exe 共用 `_internal/` 依賴
- 最終打包成 ZIP 分發（兼顧方便性與效能）

#### Q2: 為什麼 `onnxruntime.capi.onnxruntime_pybind11_state` 必須加入 `hiddenimports`？

**原因**：
- `ddddocr` 依賴 ONNX Runtime 進行模型推論
- ONNX Runtime 使用動態導入載入 C++ 擴充套件
- PyInstaller 無法自動偵測，必須明確指定

**症狀**：
- 缺少此模組會導致 `ddddocr` 初始化失敗
- 錯誤訊息：`ModuleNotFoundError: No module named 'onnxruntime.capi.onnxruntime_pybind11_state'`

#### Q3: 為什麼不打包 `webdriver/`, `assets/`, `www/` 目錄？

**原因**：
1. **可靠性**：PyInstaller `datas` 壓縮後路徑可能改變，導致程式找不到檔案
2. **可修改性**：使用者可直接修改這些目錄（例如替換音效檔案）
3. **簡潔性**：避免重複打包（4 個 exe 會重複包含相同檔案）

**Tickets Hunter 策略**：
- 使用 `xcopy` 直接複製目錄到 `dist/tickets_hunter/`
- 程式使用相對路徑讀取（例如 `./webdriver/`）

---

## 疑難排解

### 🐛 常見錯誤

#### 錯誤 1: `ModuleNotFoundError: No module named 'xxx'`

**原因**：PyInstaller 未偵測到該模組

**解決方案**：
1. 在對應的 `.spec` 檔案中加入 `hiddenimports`：
   ```python
   hiddenimports=[
       'xxx',  # 加入缺少的模組
   ],
   ```
2. 重新打包：
   ```bash
   python -m PyInstaller build_scripts/nodriver_tixcraft.spec --clean --noconfirm
   ```

#### 錯誤 2: `FileNotFoundError: [Errno 2] No such file or directory: 'xxx.dll'`

**原因**：缺少 Microsoft Visual C++ Redistributable

**解決方案**：
- 下載並安裝 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 或在發布 ZIP 中包含安裝程式

#### 錯誤 3: `ddddocr` 初始化失敗

**症狀**：
```
Error: ddddocr initialization failed
ModuleNotFoundError: No module named 'onnxruntime.capi.onnxruntime_pybind11_state'
```

**解決方案**：
1. 確認 `.spec` 中包含：
   ```python
   hiddenimports=[
       'ddddocr',
       'onnxruntime',
       'onnxruntime.capi.onnxruntime_pybind11_state',
   ],
   ```
2. 確認使用 `collect_data_files('ddddocr')` 收集資料檔案：
   ```python
   from PyInstaller.utils.hooks import collect_data_files
   datas = collect_data_files('ddddocr')
   ```

#### 錯誤 4: 程式找不到 `webdriver/`, `assets/`, `www/` 目錄

**原因**：這些目錄未正確複製到 `dist/tickets_hunter/`

**解決方案**：
1. **GitHub Actions**：檢查 `.github/workflows/build-release.yml` 中的複製步驟
2. **本地測試**：檢查 `build_scripts/build_and_test.bat` 中的複製步驟
3. 手動複製：
   ```batch
   xcopy /E /I /Y src\webdriver\Maxbotplus_1.0.0 dist\tickets_hunter\webdriver\Maxbotplus_1.0.0
   xcopy /E /I /Y src\webdriver\Maxblockplus_1.0.0 dist\tickets_hunter\webdriver\Maxblockplus_1.0.0
   xcopy /E /I /Y src\assets dist\tickets_hunter\assets
   xcopy /E /I /Y src\www dist\tickets_hunter\www
   ```

#### 錯誤 5: Windows Defender 或防毒軟體誤判

**原因**：PyInstaller 打包的 exe 可能被誤判為病毒

**解決方案**：
1. **短期**：加入防毒軟體白名單
2. **長期**：數位簽章（需購買 Code Signing Certificate）

#### 錯誤 6: `settings.json` 被打包進去了

**症狀**：發布 ZIP 中包含開發者的 `settings.json`

**解決方案**：
1. 確認 `.spec` 中 **沒有** 包含 `settings.json`：
   ```python
   datas=[
       # ❌ 錯誤：('settings.json', '.'),
   ],
   ```
2. 確認程式有自動生成邏輯：
   ```python
   if not os.path.exists('settings.json'):
       # 生成預設 settings.json
   ```

### 🔧 除錯技巧

#### 1. 查看打包日誌

**PyInstaller 會生成詳細日誌**：
```bash
python -m PyInstaller build_scripts/nodriver_tixcraft.spec --clean --noconfirm --log-level DEBUG
```

#### 2. 檢查 `_internal/` 目錄

**手動檢查依賴是否完整**：
```bash
cd dist/tickets_hunter/_internal
dir | findstr /I "ddddocr"
dir | findstr /I "selenium"
dir | findstr /I "onnxruntime"
```

#### 3. 使用 `--debug` 模式

**在 `.spec` 中啟用除錯**：
```python
exe = EXE(
    # ...
    debug=True,  # 啟用除錯模式
    console=True,  # 保留 console 查看日誌
)
```

#### 4. 在乾淨環境測試

**Windows Sandbox**（推薦）：
- 無需安裝虛擬機
- 啟動快速（30 秒）
- 關閉後自動清理

**虛擬機**：
- 使用 VirtualBox 或 VMware
- 安裝乾淨的 Windows 10/11
- 不安裝 Python 或任何開發工具

---

## 進階主題

### 🚀 優化打包大小

#### 1. 排除不需要的套件

**在 `.spec` 中加入 `excludes`**：
```python
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
    'numpy.distutils',
    'tkinter',
    'test',
    'unittest',
    'email',
    'html',
    'http',
    'xml',
    'pydoc',
],
```

#### 2. 使用 UPX 壓縮

**UPX（Ultimate Packer for eXecutables）**：
- 下載：https://github.com/upx/upx/releases
- 解壓到 PATH（例如 `C:\Windows\System32`）

**在 `.spec` 中啟用**：
```python
exe = EXE(
    # ...
    upx=True,  # 啟用 UPX 壓縮
    upx_exclude=[
        'vcruntime140.dll',  # 不壓縮 VC++ Runtime（可能導致無法執行）
    ],
)
```

**效果**：節省 30-40% 空間

#### 3. 清理 Python 快取

**打包前清理**：
```bash
# Git Bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Windows CMD
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc
```

### ⚡ 優化啟動速度

#### 1. 使用資料夾模式

**已採用**：Tickets Hunter 使用 `exclude_binaries=True`

#### 2. 延遲導入大型模組

**修改程式碼**：
```python
# ❌ 全域導入（啟動時載入）
import nodriver as uc
import selenium

# ✅ 延遲導入（使用時才載入）
def main():
    import nodriver as uc
    import selenium
    # ...
```

#### 3. 關閉除錯模式

**在 `.spec` 中**：
```python
exe = EXE(
    # ...
    debug=False,  # 關閉除錯（提升啟動速度）
)
```

### 🔒 增強安全性

#### 1. 程式碼混淆

**使用 PyArmor**：
```bash
pip install pyarmor
pyarmor obfuscate src/nodriver_tixcraft.py
```

**注意**：可能影響效能與相容性

#### 2. 數位簽章

**購買 Code Signing Certificate**（約 $100-$300/年）：
- Sectigo
- DigiCert
- GlobalSign

**簽署 exe**：
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/tickets_hunter/nodriver_tixcraft.exe
```

**效果**：
- 避免 Windows SmartScreen 警告
- 增強使用者信任

### 🎯 替代方案：Nuitka

**Nuitka**：將 Python 編譯為 C++，而非打包

**優點**：
- 執行速度更快（接近原生）
- 檔案大小更小（100-150MB vs 200-300MB）

**缺點**：
- 打包時間更長（5-10 分鐘）
- 相容性較差（某些套件不支援）

**安裝**：
```bash
pip install nuitka
pip install ordered-set
```

**編譯**：
```bash
nuitka --standalone ^
    --onefile ^
    --windows-console-mode=force ^
    --include-data-dir=webdriver=webdriver ^
    --include-data-file=settings.json=settings.json ^
    --output-dir=dist_nuitka ^
    --output-filename=nodriver_tixcraft.exe ^
    src/nodriver_tixcraft.py
```

**Tickets Hunter 策略**：
- 目前使用 PyInstaller（成熟、相容性好）
- Nuitka 作為未來優化選項

---

## 參考資源

### 官方文件
- [PyInstaller 官方文件](https://pyinstaller.org/en/stable/)
- [Nuitka 官方文件](https://nuitka.net/doc/)
- [UPX 壓縮工具](https://upx.github.io/)

### 專案內部文件
- [`build_scripts/QUICK_START.md`](../../build_scripts/QUICK_START.md) - 快速開始指南
- [`.github/workflows/build-release.yml`](../../.github/workflows/build-release.yml) - GitHub Actions 配置
- [`build_scripts/build_and_test.bat`](../../build_scripts/build_and_test.bat) - 本地測試打包腳本

### 疑難排解
- [PyInstaller GitHub Issues](https://github.com/pyinstaller/pyinstaller/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pyinstaller)

---

**文件版本**: 2.0
**最後更新**: 2025-11-24
**適用專案**: Tickets Hunter
**測試環境**: Windows 10/11, Python 3.10.11
