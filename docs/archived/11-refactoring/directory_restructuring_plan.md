**文件說明**：專案目錄結構的重構計劃，涵蓋目標、現況分析、重構方案與實施步驟。

**最後更新**：2025-11-12

---

# 專案目錄重構計劃

> **目標**：整理專案目錄結構，將資源檔案分類收納，保持根目錄簡潔

**建立日期**：2025-10-07
**狀態**：規劃階段
**預估工時**：2-4 小時
**風險等級**：中等

---

## 📋 重構背景

### 當前問題

根目錄混亂，包含：
- 7 個 Python 主程式檔案
- 9 個多媒體資源檔案（圖示、音效）
- 6 個 Markdown 文件
- 3 個設定檔
- 多個資料夾

**影響**：
- 新手難以快速理解專案結構
- GitHub 首頁顯得雜亂
- 資源檔案分散，不易管理

### 重構目標

1. **根目錄簡潔化**：只保留 GitHub 必要文件和主執行檔
2. **程式碼模組化**：輔助程式移至 `src/` 目錄
3. **資源分類管理**：圖示、音效分別收納
4. **保持向下相容**：不破壞現有功能

---

## 🗂️ 目錄結構對比

### 當前結構（重構前）

```
tickets_hunter/
├── chrome_tixcraft.py          # 主程式
├── nodriver_tixcraft.py        # 主程式
├── config_launcher.py          # 啟動器
├── settings.py                 # 設定介面
├── settings_old.py             # 舊版設定
├── util.py                     # 工具函式
├── NonBrowser.py               # 輔助模組
├── settings.json               # 設定檔
├── requirement.txt             # 依賴清單
├── README.MD                   # 專案說明
├── CHANGELOG.md                # 版本記錄
├── CLAUDE.md                   # AI 規範
├── CONTRIBUTING.md             # 貢獻指南
├── LEGAL_NOTICE.md             # 法律聲明
├── LICENSE                     # 授權
├── icon_*.gif (4個)            # 圖示檔案
├── *.wav (2個)                 # 音效
├── *.mp3 (2個)                 # 音效
├── maxbot_logo2_single.ppm     # Logo
├── docs/                       # 文件目錄
├── webdriver/                  # 瀏覽器擴充
└── www/                        # 網頁介面
```

### 建議結構（重構後）

```
tickets_hunter/
│
├── 📄 README.MD                    # 專案說明
├── 📄 CHANGELOG.md                 # 版本記錄
├── 📄 LICENSE                      # 授權條款
├── 📄 CONTRIBUTING.md              # 貢獻指南
├── 📄 LEGAL_NOTICE.md              # 法律聲明
├── 📄 CLAUDE.md                    # AI 開發規範
├── 📄 requirement.txt              # 依賴清單
│
├── 🐍 chrome_tixcraft.py          # 主程式 (Chrome/Selenium/UC)
├── 🐍 nodriver_tixcraft.py        # 主程式 (NoDriver)
├── 🐍 config_launcher.py          # 多設定檔啟動器
├── ⚙️ settings.json                # 主設定檔
│
├── 📁 src/                         # 🆕 核心程式模組
│   ├── util.py                    # 共用工具函式庫
│   ├── NonBrowser.py              # 非瀏覽器模式模組
│   ├── settings.py                # 網頁設定介面
│   └── settings_old.py            # 桌面版設定介面（舊版）
│
├── 📁 assets/                      # 🆕 多媒體資源
│   ├── icons/                     # 🆕 圖示檔案
│   │   ├── icon_chrome_4.gif
│   │   ├── icon_copy_2.gif
│   │   ├── icon_play_1.gif
│   │   ├── icon_query_5.gif
│   │   └── maxbot_logo2_single.ppm
│   └── sounds/                    # 🆕 音效檔案
│       ├── ding.wav
│       ├── ding-dong.wav
│       ├── sound_clap.mp3
│       └── sound_victory.mp3
│
├── 📁 webdriver/                   # 瀏覽器擴充套件（保持不變）
│   ├── Maxblockplus_1.0.0/
│   └── Maxbotplus_1.0.0/
│
├── 📁 www/                         # 網頁介面資源（保持不變）
│   ├── css/
│   ├── dist/
│   └── icons/
│
├── 📁 docs/                        # 文件目錄（保持不變）
│   ├── 01-getting-started/
│   ├── 02-development/
│   ├── 03-api-reference/
│   ├── 04-testing-debugging/
│   ├── 05-troubleshooting/
│   ├── 06-deployment/
│   ├── 07-project-tracking/
│   └── 08-refactoring/            # 🆕 本計劃文件所在
│
├── 📁 .temp/                       # 暫存檔案（保持不變）
├── 📁 .claude/                     # Claude Code 配置（保持不變）
├── 📁 .github/                     # GitHub 配置（保持不變）
└── 📁 .git/                        # Git 版本控制（保持不變）
```

---

## 📝 目錄命名選擇：`src/` vs `core/`

### 推薦使用 `src/`

| 比較項目 | src/ | core/ |
|---------|------|-------|
| **業界標準** | ✅ Python 專案慣用 | ⚠️ 較少使用 |
| **語意明確** | ✅ source = 原始碼 | ⚠️ 易與「核心模組」混淆 |
| **工具支援** | ✅ PyInstaller, setuptools 預設支援 | ⚠️ 需要額外配置 |
| **可讀性** | ✅ 新手友善 | ⚠️ 可能誤解為核心功能 |

**結論**：採用 `src/` 作為程式模組目錄

---

## 🔢 影響範圍分析

### 1. Python Import 語句修改

需要修改 7 個檔案的 import 語句：

| 檔案 | 原語句 | 新語句 | 次數 |
|------|--------|--------|------|
| chrome_tixcraft.py | `import util` | `from src import util` | 1 |
| chrome_tixcraft.py | `from NonBrowser import NonBrowser` | `from src.NonBrowser import NonBrowser` | 1 |
| nodriver_tixcraft.py | `import util` | `from src import util` | 1 |
| nodriver_tixcraft.py | `from NonBrowser import NonBrowser` | `from src.NonBrowser import NonBrowser` | 1 |
| config_launcher.py | `import util` | `from src import util` | 1 |
| settings.py | `import util` | `from src import util` | 1 |
| settings_old.py | `import util` | `from src import util` | 1 |

**小計**：7 個檔案，共 7 處 import 修改

### 2. 檔案路徑引用修改

需要搜尋並修改檔案路徑引用：

| 檔案 | 修改項目 | 關鍵字搜尋 | 預估次數 |
|------|----------|-----------|----------|
| chrome_tixcraft.py | webdriver/ 路徑 | `"webdriver/"`, `'webdriver/'` | 1-2 |
| config_launcher.py | webdriver/ 路徑 | `"webdriver/"`, `'webdriver/'` | 1-2 |
| settings.py | webdriver/, www/, 音效/圖示 | `"icon_"`, `"sound_"`, `".gif"`, `".mp3"`, `".wav"` | 5-10 |
| settings_old.py | webdriver/, 音效/圖示 | 同上 | 5-10 |
| util.py | 音效檔案 (play_mp3_async) | `"sound_"`, `".mp3"`, `".wav"` | 2-3 |

**小計**：5 個檔案，約 **15-30 處**路徑修改

### 3. 文件更新

需要更新的文件：

| 檔案 | 修改項目 | 優先度 |
|------|----------|--------|
| README.MD | 目錄結構說明 | 高 |
| docs/01-getting-started/project_overview.md | 系統架構圖 | 高 |
| docs/01-getting-started/setup.md | ChromeDriver 連結 + 目錄結構 | 高 |
| docs/01-getting-started/update.md | ChromeDriver 連結 | 中 |
| docs/08-troubleshooting/README.md | ChromeDriver 連結 | 中 |

**小計**：5 個文件

---

## 📊 總計修改統計

| 類別 | 檔案數 | 修改處數 |
|------|--------|----------|
| Python import 語句 | 7 | 7 |
| 檔案路徑引用 | 5 | 15-30 |
| 外部連結更新 | 3 | 3 |
| 文件結構說明 | 2 | 2 |
| **總計** | **17** | **27-42 處** |

---

## 🚀 執行步驟

### Phase 1: 準備與備份（必須）

```bash
# 1. 建立 Git 備份點
git add .
git commit -m "backup: 目錄重構前的備份點"

# 2. 確認當前程式可正常運作
python chrome_tixcraft.py --help
python nodriver_tixcraft.py --help
```

### Phase 2: 建立新目錄結構

```bash
# 建立新目錄
mkdir src
mkdir assets
mkdir assets/icons
mkdir assets/sounds
mkdir docs/08-refactoring
```

### Phase 3: 檔案搬移

#### 3.1 搬移程式模組到 src/

```bash
# 搬移 Python 模組
mv util.py src/
mv NonBrowser.py src/
mv settings.py src/
mv settings_old.py src/
```

#### 3.2 搬移圖示檔案到 assets/icons/

```bash
# 搬移圖示
mv icon_chrome_4.gif assets/icons/
mv icon_copy_2.gif assets/icons/
mv icon_play_1.gif assets/icons/
mv icon_query_5.gif assets/icons/
mv maxbot_logo2_single.ppm assets/icons/
```

#### 3.3 搬移音效檔案到 assets/sounds/

```bash
# 搬移音效
mv ding.wav assets/sounds/
mv ding-dong.wav assets/sounds/
mv sound_clap.mp3 assets/sounds/
mv sound_victory.mp3 assets/sounds/
```

### Phase 4: 程式碼修改

#### 4.1 更新 import 語句（7 個檔案）

**檔案**: `chrome_tixcraft.py`, `nodriver_tixcraft.py`, `config_launcher.py`

```python
# 修改前
import util
from NonBrowser import NonBrowser

# 修改後
from src import util
from src.NonBrowser import NonBrowser
```

**檔案**: `settings.py`, `settings_old.py`（在 src/ 內部）

```python
# 修改前
import util

# 修改後（相對路徑）
from . import util
# 或（絕對路徑）
from src import util
```

#### 4.2 更新檔案路徑引用（搜尋替換）

**關鍵字搜尋清單**：

```python
# Chrome/設定相關檔案
"webdriver/"          → "webdriver/"          # 保持不變（在根目錄）
"www/"                → "www/"                # 保持不變（在根目錄）

# 圖示檔案
"icon_chrome_4.gif"   → "assets/icons/icon_chrome_4.gif"
"icon_copy_2.gif"     → "assets/icons/icon_copy_2.gif"
"icon_play_1.gif"     → "assets/icons/icon_play_1.gif"
"icon_query_5.gif"    → "assets/icons/icon_query_5.gif"
"maxbot_logo2_single.ppm" → "assets/icons/maxbot_logo2_single.ppm"

# 音效檔案
"ding.wav"            → "assets/sounds/ding.wav"
"ding-dong.wav"       → "assets/sounds/ding-dong.wav"
"sound_clap.mp3"      → "assets/sounds/sound_clap.mp3"
"sound_victory.mp3"   → "assets/sounds/sound_victory.mp3"
```

**需要檢查的檔案**：
- `chrome_tixcraft.py`
- `nodriver_tixcraft.py`
- `config_launcher.py`
- `src/settings.py`
- `src/settings_old.py`
- `src/util.py`

### Phase 5: 文件更新

#### 5.1 更新 ChromeDriver 官方連結（3 處）

**檔案**：
- `docs/01-getting-started/setup.md:140`
- `docs/01-getting-started/update.md:49-50`
- `docs/08-troubleshooting/README.md:59`

**修改**：
```markdown
# 舊連結（已失效）
https://chromedriver.chromium.org/

# 新連結（官方遷移）
https://developer.chrome.com/docs/chromedriver/
```

#### 5.2 更新目錄結構說明（2 處）

**檔案**：
- `README.MD` - 在「專案結構」段落更新
- `docs/01-getting-started/project_overview.md` - 更新架構圖

### Phase 6: 測試驗證（關鍵步驟）

#### 6.1 功能測試

```bash
# 測試主程式
python chrome_tixcraft.py --help
python nodriver_tixcraft.py --help

# 測試設定介面（網頁）
python src/settings.py
# 瀏覽器開啟 http://127.0.0.1:16888/ 驗證圖示和音效載入

# 測試設定介面（桌面）
python src/settings_old.py
# 驗證視窗顯示正常

# 測試多設定檔啟動器
python config_launcher.py
```

#### 6.2 路徑檢查

```bash
# 檢查是否有遺漏的路徑引用
grep -r "icon_chrome_4.gif" . --exclude-dir=.git
grep -r "sound_clap.mp3" . --exclude-dir=.git
grep -r "ding.wav" . --exclude-dir=.git

# 應該只在 assets/ 目錄找到實體檔案
# Python 檔案中的路徑引用應已更新為 assets/
```

#### 6.3 Import 檢查

```bash
# 檢查是否有遺漏的 import
grep -r "^import util$" . --include="*.py"
grep -r "^from NonBrowser import" . --include="*.py"

# 應該全部改為 from src import util
```

### Phase 7: 提交變更

```bash
# 提交重構
git add .
git commit -m "refactor: 重構目錄結構，分離程式模組與資源檔案

- 建立 src/ 目錄存放程式模組
- 建立 assets/ 目錄存放多媒體資源
- 更新所有 import 語句和檔案路徑引用
- 更新文件中的 ChromeDriver 連結
- 更新專案結構說明文件
"
```

---

## ⚠️ 風險評估與應對

### 風險等級：中等

| 風險項目 | 風險等級 | 影響 | 應對措施 |
|---------|---------|------|---------|
| Import 路徑錯誤 | 🟡 中 | 程式無法啟動 | 執行前先 git commit 備份 |
| 檔案路徑遺漏 | 🟡 中 | 圖示/音效無法載入 | 使用 grep 全面搜尋 |
| webdriver/ 路徑變更 | 🟢 低 | 瀏覽器擴充失效 | webdriver/ 保持在根目錄 |
| PyInstaller 打包失效 | 🟡 中 | 無法產生執行檔 | 需更新打包配置檔 |

### 回退策略

```bash
# 如果重構失敗，立即回退
git reset --hard HEAD~1

# 或使用備份提交的 SHA
git reset --hard <備份commit-sha>
```

---

## 📋 檢查清單

### 執行前檢查

- [ ] 已閱讀完整計劃
- [ ] 已建立 Git 備份點
- [ ] 已確認當前程式可正常運作
- [ ] 已準備測試環境

### 搬移階段檢查

- [ ] 已建立 `src/` 目錄
- [ ] 已建立 `assets/icons/` 目錄
- [ ] 已建立 `assets/sounds/` 目錄
- [ ] 已搬移 4 個 Python 模組到 `src/`
- [ ] 已搬移 5 個圖示檔案到 `assets/icons/`
- [ ] 已搬移 4 個音效檔案到 `assets/sounds/`

### 程式碼修改檢查

- [ ] 已更新 `chrome_tixcraft.py` import (2 處)
- [ ] 已更新 `nodriver_tixcraft.py` import (2 處)
- [ ] 已更新 `config_launcher.py` import (1 處)
- [ ] 已更新 `src/settings.py` import (1 處)
- [ ] 已更新 `src/settings_old.py` import (1 處)
- [ ] 已搜尋並更新所有圖示路徑引用
- [ ] 已搜尋並更新所有音效路徑引用

### 文件更新檢查

- [ ] 已更新 `setup.md` ChromeDriver 連結
- [ ] 已更新 `update.md` ChromeDriver 連結
- [ ] 已更新 `troubleshooting/README.md` ChromeDriver 連結
- [ ] 已更新 `README.MD` 目錄結構說明
- [ ] 已更新 `project_overview.md` 架構圖

### 測試驗證檢查

- [ ] `python chrome_tixcraft.py --help` 正常
- [ ] `python nodriver_tixcraft.py --help` 正常
- [ ] `python src/settings.py` 網頁介面正常
- [ ] 網頁介面圖示載入正常
- [ ] 網頁介面音效播放正常
- [ ] `python src/settings_old.py` 桌面介面正常
- [ ] `python config_launcher.py` 啟動器正常
- [ ] grep 檢查無遺漏路徑
- [ ] grep 檢查無遺漏 import

### 提交前檢查

- [ ] 所有測試通過
- [ ] 已撰寫清晰的 commit message
- [ ] 已更新 CHANGELOG.md（可選）

---

## 🎯 未來優化建議

### 短期（1-2 週內）

1. **建立 config/ 目錄**
   - 移動 `config_launcher.json` → `config/`
   - 移動 `settings.json` → `config/`（可選，影響使用者習慣）

2. **更新 PyInstaller 配置**
   - 修改 `docs/09-deployment/pyinstaller_packaging_guide.md`
   - 更新 .spec 檔案路徑配置

### 中期（1-2 個月內）

3. **程式模組化拆分**
   - 將 `chrome_tixcraft.py` (11,764 行) 拆分為多個模組
   - 將 `nodriver_tixcraft.py` (12,602 行) 拆分為多個模組
   - 參考：`docs/02-development/structure.md` 的平台函數索引

4. **建立單元測試**
   - 在 `tests/` 目錄建立測試檔案
   - 為核心函式撰寫測試案例

### 長期（3 個月以上）

5. **採用 setuptools 打包**
   - 建立 `setup.py` 或 `pyproject.toml`
   - 支援 `pip install .` 安裝方式

6. **Docker 化部署**
   - 建立 `Dockerfile`
   - 提供容器化執行環境

---

## 📚 相關文件

- [專案架構概覽](../01-getting-started/project_overview.md)
- [程式結構分析](../02-development/structure.md)
- [開發規範指南](../02-development/development_guide.md)
- [PyInstaller 打包指南](../06-deployment/pyinstaller_packaging_guide.md)

---

**最後更新**：2025-10-07
**維護者**：開發團隊
**版本**：1.0
