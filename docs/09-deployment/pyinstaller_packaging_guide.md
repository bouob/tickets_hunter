**文件說明**：Python 打包成 .exe 的完整指南，涵蓋環境準備、PyInstaller 安裝、打包設定、常見問題與優化策略。

**最後更新**：2025-11-12

---

# Python 打包成 .exe 完整指南

## 📋 目錄
1. [環境準備](#環境準備)
2. [PyInstaller 安裝](#pyinstaller-安裝)
3. [打包配置](#打包配置)
4. [執行打包](#執行打包)
5. [測試驗證](#測試驗證)
6. [常見問題](#常見問題)
7. [優化建議](#優化建議)

---

## 環境準備

### 系統需求

- **作業系統**: Windows 10/11
- **Python 版本**: 3.10.x（建議使用 3.10.11，與開發環境一致）
- **磁碟空間**: 至少 2GB（打包過程需要暫存空間）
- **記憶體**: 建議 8GB 以上

### Python 環境檢查

```bash
# 檢查 Python 版本
python --version
# 應顯示：Python 3.10.11

# 檢查 pip 版本
pip --version
```

### 建立虛擬環境（強烈建議）

為了避免套件衝突，建議在虛擬環境中進行打包：

```bash
# 切換到專案目錄
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter"

# 建立虛擬環境
python -m venv venv_build

# 啟動虛擬環境
# Windows CMD
venv_build\Scripts\activate.bat

# Windows PowerShell
venv_build\Scripts\Activate.ps1

# Git Bash
source venv_build/Scripts/activate
```

### 安裝專案依賴

```bash
# 確保在虛擬環境中
pip install --upgrade pip

# 安裝專案所需套件
pip install nodriver==0.46.1
pip install selenium==4.33.0
pip install ddddocr==1.5.6
pip install urllib3
pip install Pillow
pip install opencv-python
pip install requests

# 如果有其他依賴，請根據實際需求安裝
```

---

## PyInstaller 安裝

### 安裝 PyInstaller

```bash
# 安裝最新穩定版
pip install pyinstaller

# 或指定版本（建議 6.x）
pip install pyinstaller==6.3.0

# 驗證安裝
pyinstaller --version
```

### PyInstaller 基本概念

- **單一檔案模式** (`--onefile`): 將所有內容打包成單一 .exe（啟動較慢，但方便分發）
- **資料夾模式** (`--onedir`): 產生 exe + 資料夾（啟動快，檔案較多）
- **視窗模式** (`--windowed`/`--noconsole`): 隱藏命令列視窗（GUI 程式使用）
- **命令列模式** (預設): 保留命令列視窗（CLI 程式使用）

---

## 打包配置

### 專案結構分析

Tickets Hunter 專案包含以下需要處理的元素：

```
tickets_hunter/
├── src/                     # 原始碼目錄
│   ├── nodriver_tixcraft.py    # NoDriver 版本主程式
│   ├── chrome_tixcraft.py       # Chrome/Selenium 版本主程式
│   ├── util.py                  # 工具函數
│   ├── NonBrowser.py            # 非瀏覽器模式
│   ├── settings.json            # 設定檔（需要複製）
│   └── webdriver/               # WebDriver 與擴充套件（需要複製）
│       ├── chromedriver.exe
│       ├── Maxbotplus_1.0.0/
│       └── Maxblockplus_1.0.0/
├── .temp/                   # 暫存資料夾（執行時建立）
└── docs/                    # 文件（可選）
```

### 方案選擇

#### 方案 A：單一 .exe（推薦給一般使用者）
- **優點**: 單一檔案，方便分發
- **缺點**: 檔案大（100-300MB），啟動較慢（5-10秒）
- **適用**: 終端使用者、快速分發

#### 方案 B：資料夾模式（推薦給進階使用者）
- **優點**: 啟動快（1-2秒），易於除錯
- **缺點**: 檔案多，需要打包整個資料夾
- **適用**: 開發測試、企業內部使用

---

## 執行打包

### 方案 A：單一 .exe 打包（NoDriver 版本）

#### 步驟 1：建立 .spec 配置檔

建立 `nodriver_tixcraft.spec` 檔案：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['nodriver_tixcraft.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('webdriver', 'webdriver'),              # 包含 webdriver 資料夾
        ('settings.json', '.'),                   # 包含設定檔
        ('util.py', '.'),                         # 包含工具模組
        ('NonBrowser.py', '.'),                   # 包含 NonBrowser 模組
    ],
    hiddenimports=[
        'nodriver',
        'nodriver.cdp',
        'nodriver.core.config',
        'selenium',
        'selenium.webdriver',
        'ddddocr',
        'cv2',
        'PIL',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',      # 排除不需要的大型套件
        'numpy.distutils', # 排除 numpy 的編譯工具
        'tkinter',         # 如果不使用 GUI
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TicketsHunter_NoDriver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # 使用 UPX 壓縮（需要安裝 UPX）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,                # 保留命令列視窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',             # 可選：自訂圖示
)
```

#### 步驟 2：執行打包

```bash
# 使用 .spec 檔案打包
pyinstaller nodriver_tixcraft.spec

# 或直接使用命令列（不建議，參數太多）
pyinstaller --onefile ^
    --name TicketsHunter_NoDriver ^
    --add-data "webdriver;webdriver" ^
    --add-data "settings.json;." ^
    --add-data "util.py;." ^
    --add-data "NonBrowser.py;." ^
    --hidden-import nodriver ^
    --hidden-import nodriver.cdp ^
    --hidden-import selenium ^
    --hidden-import ddddocr ^
    --console ^
    nodriver_tixcraft.py
```

**注意**：Windows 的路徑分隔符在 `--add-data` 中使用分號 `;`（Linux/Mac 使用冒號 `:`）

#### 步驟 3：檢查輸出

打包完成後，檔案結構：

```
tickets_hunter/
├── build/                    # 暫存檔案（可刪除）
├── dist/                     # 打包結果
│   └── TicketsHunter_NoDriver.exe  # 主程式
├── nodriver_tixcraft.spec    # 配置檔
└── ... (原始檔案)
```

### 方案 B：資料夾模式打包

修改 .spec 檔案中的 `EXE` 部分：

```python
exe = EXE(
    pyz,
    a.scripts,
    [],                          # 移除 a.binaries
    exclude_binaries=True,       # 啟用資料夾模式
    name='TicketsHunter_NoDriver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='TicketsHunter_NoDriver',
)
```

打包後結果：

```
dist/
└── TicketsHunter_NoDriver/
    ├── TicketsHunter_NoDriver.exe  # 主程式
    ├── _internal/                   # 依賴檔案
    │   ├── webdriver/
    │   ├── settings.json
    │   └── ... (其他依賴)
    └── ... (Python runtime)
```

### Chrome/Selenium 版本打包

建立 `chrome_tixcraft.spec`，將 `nodriver_tixcraft.py` 替換為 `chrome_tixcraft.py`，其他配置相同。

---

## 測試驗證

### 基本功能測試

```bash
# 切換到 dist 資料夾
cd dist

# 測試執行（單一 .exe 模式）
TicketsHunter_NoDriver.exe --help

# 測試執行（資料夾模式）
cd TicketsHunter_NoDriver
TicketsHunter_NoDriver.exe --help

# 實際執行測試
TicketsHunter_NoDriver.exe --input settings.json
```

### 檢查事項清單

- [ ] 程式是否正常啟動
- [ ] settings.json 是否被正確讀取
- [ ] webdriver/chromedriver.exe 是否可執行
- [ ] NoDriver/Selenium 是否正常運作
- [ ] ddddocr 驗證碼辨識是否正常
- [ ] 是否出現缺少 DLL 的錯誤
- [ ] 是否出現 Python 模組缺失錯誤
- [ ] 記憶體使用是否正常（不超過 500MB）
- [ ] 是否可在乾淨的 Windows 系統執行（無 Python 環境）

### 常見錯誤排查

#### 錯誤 1：缺少 DLL
```
Error: Cannot load library xxx.dll
```
**解決方案**：安裝 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

#### 錯誤 2：找不到模組
```
ModuleNotFoundError: No module named 'xxx'
```
**解決方案**：在 .spec 的 `hiddenimports` 中加入該模組

#### 錯誤 3：找不到資料檔案
```
FileNotFoundError: settings.json not found
```
**解決方案**：檢查 .spec 的 `datas` 是否正確包含該檔案

---

## 常見問題

### Q1：為什麼 .exe 檔案這麼大（200-300MB）？

**原因**：
- Python runtime（50MB）
- nodriver + Selenium（80MB）
- ddddocr + OpenCV（70MB）
- 其他依賴套件（50MB）

**解決方案**：
1. 使用資料夾模式（可共用 DLL）
2. 使用 UPX 壓縮（節省 30-40%）
3. 排除不必要的套件（如 matplotlib、pandas）
4. 考慮使用 Nuitka（編譯型打包，檔案更小）

### Q2：啟動速度很慢（10-20秒）？

**原因**：
- 單一 .exe 需要先解壓縮到暫存目錄
- 載入大型模組（nodriver, selenium, ddddocr）

**解決方案**：
1. 改用資料夾模式（啟動快 5-10 倍）
2. 使用 `--noupx` 取消壓縮（犧牲檔案大小換取速度）
3. 延遲載入非必要模組

### Q3：在其他電腦無法執行？

**可能原因**：
1. 缺少 Visual C++ Redistributable
2. Windows 版本不相容（如打包在 Win11，執行在 Win7）
3. 防毒軟體誤判
4. 缺少管理員權限

**解決方案**：
1. 隨附 VC++ Redistributable 安裝程式
2. 在目標系統版本上打包
3. 數位簽章或加入防毒白名單
4. 要求使用者以管理員身份執行

### Q4：ddddocr 在 .exe 中無法使用？

**原因**：ddddocr 依賴 ONNX Runtime，需要額外的 DLL

**解決方案**：
```python
# 在 .spec 中加入
hiddenimports=[
    'ddddocr',
    'onnxruntime',
    'onnxruntime.capi.onnxruntime_pybind11_state',
],
```

### Q5：NoDriver 無法啟動瀏覽器？

**原因**：NoDriver 需要動態下載 Chrome/Chromium

**解決方案**：
1. 確保 .exe 有網路權限
2. 預先下載 Chrome 並包含在打包中
3. 或在首次執行時提示使用者下載

---

## 優化建議

### 檔案大小優化

#### 1. 排除不必要的套件

在 .spec 的 `excludes` 中加入：

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

下載 UPX：https://github.com/upx/upx/releases

```bash
# 下載 UPX 並解壓到 PATH
# 在 .spec 中設定
upx=True,
upx_exclude=[
    'vcruntime140.dll',  # 不壓縮 VC++ Runtime
],
```

#### 3. 清理 Python 快取

```bash
# 打包前清理
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 啟動速度優化

#### 1. 延遲導入

```python
# 修改程式碼，將大型模組改為延遲導入
def main():
    import nodriver as uc  # 只在需要時導入
    import selenium
    # ...
```

#### 2. 使用資料夾模式

資料夾模式比單一 .exe 快 5-10 倍。

#### 3. 關閉除錯模式

```python
# .spec 中設定
debug=False,
```

### 安全性優化

#### 1. 程式碼混淆

考慮使用 PyArmor 混淆程式碼：

```bash
pip install pyarmor
pyarmor obfuscate nodriver_tixcraft.py
```

#### 2. 數位簽章

使用 Code Signing Certificate 簽署 .exe，避免 SmartScreen 警告。

---

## 進階：使用 Nuitka（替代方案）

Nuitka 是一個將 Python 編譯為 C++ 的工具，效能和檔案大小都比 PyInstaller 好。

### 安裝 Nuitka

```bash
pip install nuitka
pip install ordered-set  # Nuitka 依賴
```

### 編譯指令

```bash
nuitka --standalone ^
    --onefile ^
    --windows-console-mode=force ^
    --include-data-dir=webdriver=webdriver ^
    --include-data-file=settings.json=settings.json ^
    --output-dir=dist_nuitka ^
    --output-filename=TicketsHunter_NoDriver.exe ^
    nodriver_tixcraft.py
```

### Nuitka vs PyInstaller

| 特性 | PyInstaller | Nuitka |
|------|-------------|--------|
| 打包速度 | 快（1-2分鐘） | 慢（5-10分鐘） |
| 執行速度 | 較慢 | 快（接近原生） |
| 檔案大小 | 大（200-300MB） | 較小（100-150MB） |
| 相容性 | 高 | 中（某些套件不支援） |
| 難度 | 簡單 | 中等 |

---

## 自動化打包腳本

建立 `build_scripts/build_all.bat`：

```batch
@echo off
echo ================================================
echo Tickets Hunter - 自動化打包腳本
echo ================================================

REM 啟動虛擬環境
call venv_build\Scripts\activate.bat

REM 清理舊檔案
echo [1/5] 清理舊檔案...
rd /s /q build dist 2>nul

REM 打包 NoDriver 版本
echo [2/5] 打包 NoDriver 版本...
pyinstaller nodriver_tixcraft.spec
if errorlevel 1 goto error

REM 打包 Chrome 版本
echo [3/5] 打包 Chrome 版本...
pyinstaller chrome_tixcraft.spec
if errorlevel 1 goto error

REM 複製必要檔案到 dist
echo [4/5] 複製設定檔...
copy settings.json dist\
xcopy /E /I webdriver dist\webdriver\

REM 產生版本資訊
echo [5/5] 產生版本資訊...
echo Build Date: %date% %time% > dist\BUILD_INFO.txt
echo Python Version: >> dist\BUILD_INFO.txt
python --version >> dist\BUILD_INFO.txt

echo ================================================
echo 打包完成！檔案位於 dist\ 資料夾
echo ================================================
pause
goto end

:error
echo ================================================
echo 打包失敗！請檢查錯誤訊息
echo ================================================
pause

:end
```

執行方式：

```bash
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter"
build_scripts\build_all.bat
```

---

## 分發建議

### 打包成安裝程式（進階）

使用 Inno Setup 建立安裝程式：

1. 下載 Inno Setup：https://jrsoftware.org/isinfo.php
2. 建立 `installer.iss` 腳本
3. 包含 VC++ Redistributable
4. 建立桌面捷徑
5. 加入自動更新機制

### 檔案檢查清單

分發前確認包含：

```
release/
├── TicketsHunter_NoDriver.exe    # 主程式
├── TicketsHunter_Chrome.exe      # 備用版本
├── settings.json                  # 設定檔範本
├── README.txt                     # 使用說明
├── CHANGELOG.txt                  # 更新日誌
├── LICENSE.txt                    # 授權條款
└── vcredist_x64.exe              # VC++ Runtime（可選）
```

---

## 參考資源

### 官方文件
- PyInstaller 文件：https://pyinstaller.org/en/stable/
- Nuitka 文件：https://nuitka.net/doc/
- UPX 壓縮工具：https://upx.github.io/

### 疑難排解
- PyInstaller GitHub Issues：https://github.com/pyinstaller/pyinstaller/issues
- Stack Overflow：搜尋 "pyinstaller + [你的錯誤訊息]"

---

**文件版本**: 1.0
**最後更新**: 2025-10-03
**適用專案**: Tickets Hunter (TicketsHunter 2025.09.29)
**測試環境**: Windows 10/11, Python 3.10.11
