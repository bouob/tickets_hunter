<!--
文件說明：macOS 使用者的下載、執行與自行打包完整流程
分類：Getting Started (level: 1)
目標受眾：macOS 使用者
最後更新：2026-09-22
-->

# macOS 使用指南

macOS 版由 GitHub Actions 自動建置，隨每次 Release 一起發布。**多數人只要下載、解除一次
Gatekeeper 限制就能用**，不需要裝 Python、也不需要自己打包。

想從原始碼建、或用的是 Intel Mac（官方版只有 Apple Silicon）才需要看後半段。

| 你的情況 | 看哪一段 |
|----------|----------|
| Apple Silicon（M1/M2/M3/M4） | [下載官方版](#下載官方版) |
| Intel Mac | [自行打包](#自行打包) |
| 想改程式碼 | [自行打包](#自行打包) |

---

## 下載官方版

### 步驟 1：下載

到 [Releases 頁面](https://github.com/bouob/tickets_hunter/releases)，在最新版本的
**Assets** 底下找這兩個檔案：

| 檔案 | 用途 |
|------|------|
| `tickets_hunter_macos_arm64_vXXXX.XX.XX.zip` | 程式本體 |
| `SHA256SUMS-macos-arm64.txt` | 校驗碼（選用） |

**只有 Apple Silicon 版，需要 macOS 13 Ventura 以上。** 不確定自己是哪一種的話，左上角蘋果選單
→「關於這台 Mac」，晶片寫 Apple M 開頭就是。Intel Mac 請改看[自行打包](#自行打包)。

### 步驟 2：解壓縮

雙擊 ZIP 即可。建議把解出來的 `tickets_hunter` 資料夾放到固定位置，例如家目錄底下——之後
搬動位置要重做步驟 3。

### 步驟 3：解除 Gatekeeper 限制（只需做一次）

這個程式沒有 Apple 的開發者簽章，macOS 預設會擋下第一次執行。這是 Gatekeeper 的既定行為，
不代表檔案有問題。

打開「終端機」，輸入下面這串（**結尾留一個空格**）：

```bash
xattr -dr com.apple.quarantine 
```

然後把解壓縮出來的 `tickets_hunter` **資料夾直接拖進終端機視窗**，路徑會自動補上，按 Enter。

不解除的話雙擊會跳出「無法打開，因為無法驗證開發者」。

### 步驟 4：執行

打開 `tickets_hunter` 資料夾，裡面有兩個可以雙擊的檔案：

| 檔案 | 用途 |
|------|------|
| `start-settings.command` | 開啟設定介面（會在瀏覽器開設定頁） |
| `start-bot.command` | 開始搶票 |

**先跑 `start-settings.command` 設定好活動網址、日期、票數，再跑 `start-bot.command`。**

設定方式與 Windows 版完全相同，請看[快速入門指南](quick-start.md)與[詳細設定說明](settings-guide.md)。

### 選用：驗證這份檔案的來源

每個 macOS 版都附帶 build provenance attestation，可以證明它是由這個 repo 的公開原始碼、
在 GitHub Actions 上建置的，不是別人重新打包過的東西。

需要先安裝 [GitHub CLI](https://cli.github.com/)：

```bash
gh attestation verify tickets_hunter_macos_arm64_vXXXX.XX.XX.zip --repo bouob/tickets_hunter
```

也可以比對校驗碼：

```bash
shasum -a 256 -c SHA256SUMS-macos-arm64.txt
```

---

## 自行打包

Intel Mac 沒有官方版，想改程式碼也需要自己建。整個流程包成一個檔案，雙擊就好。

PyInstaller 無法交叉編譯：打包工具會把執行當下那台機器的 Python 直譯器與原生模組一起收進
成品，所以 macOS 版**必須在 Mac 上建**，在 Windows 上執行只會產出 Windows 版。

### 你需要什麼

| 項目 | 需求 |
|------|------|
| macOS | 13 Ventura 以上 |
| Python | **3.10 或 3.11**（推薦 3.11.9） |
| 硬碟空間 | 約 2 GB |
| 時間 | 首次約 10 分鐘，之後重跑不到 1 分鐘 |

**Python 3.12 未經驗證，3.13 以上不能用。** 驗證碼辨識用的 ddddocr 限定 Python 3.12 以下。
打包腳本會依序尋找 `python3.11`、`python3.10`，不會誤用系統預設的 `python3`。

最低需要 macOS 13，是因為 onnxruntime 與 OpenCV 的 Apple Silicon 安裝套件只支援 13 以上，
在 macOS 12 上安裝套件這一步就會失敗。

### 步驟 1：安裝 Python

```bash
python3.11 --version
```

顯示 `Python 3.11.x` 就跳到步驟 2。顯示 `command not found` 的話：

```bash
brew install python@3.11
```

沒有 Homebrew 的話先裝它（[brew.sh](https://brew.sh)），或從
[python.org](https://www.python.org/downloads/) 下載 3.11.9 的安裝檔。

### 步驟 2：下載原始碼

```bash
git clone https://github.com/bouob/tickets_hunter.git
```

```bash
cd tickets_hunter
```

macOS 第一次用 `git` 會跳出「需要安裝命令列開發者工具」，按安裝等它跑完即可。

### 步驟 3：打包

```bash
open build_scripts/macos/
```

**雙擊 `build.command`**。不想用 Finder 的話直接執行也一樣：

```bash
./build_scripts/macos/build.command
```

它會挑選 Python、建立虛擬環境、安裝套件、檢查驗證碼辨識能不能用、打包、跑 21 項檢查（含打包後的驗證碼辨識自我檢查），最後
自動解除 Gatekeeper 限制。跑完會停住等你按 Return。

**重跑很快**：虛擬環境會沿用，套件只有在 `requirement.txt` 有更動時才重裝。

成功時會看到：

```
All 21 checks passed
Bundle: /Users/你的帳號/tickets_hunter/dist/tickets_hunter

Gatekeeper quarantine flag cleared.

============================================================
Build finished.
OCR stack: working
```

### 步驟 4：執行

```bash
open dist/tickets_hunter/
```

一樣是 `start-settings.command` 與 `start-bot.command`，用法同上。

### 更新

自行打包的版本不會自動更新，有新版時：

```bash
git pull
```

```bash
./build_scripts/macos/build.command
```

---

## 遇到問題

### 雙擊沒反應，或跳出「無法打開」

先確認做過 Gatekeeper 解除（下載官方版的步驟 3）。還是不行的話在終端機裡直接跑，才看得到
錯誤訊息：

```bash
./tickets_hunter/start-settings.command
```

如果顯示 `permission denied`：

```bash
chmod +x tickets_hunter/*.command
```

### 打包時顯示找不到 Python 3.10 或 3.11

回到自行打包的步驟 1。注意 `python3 --version` 顯示的版本**不代表** `python3.11` 存在——
macOS 內建的 `python3` 通常是別的版本。

### 打包失敗

失敗訊息會指出是哪個模組找不到。詳細紀錄在 `build/` 資料夾，但預設跑完會刪掉，要保留的話：

```bash
python build_scripts/build_local.py --keep
```

然後看 `build/*/warn-*.txt`。

### 21 項檢查有失敗

檢查項目包含驗證碼模型有沒有被正確打包、打包後能不能實際辨識驗證碼、不該進去的大型套件有沒有被排除。任何一項失敗都表示
打包出來的東西有問題，請把完整輸出貼到
[GitHub Issues](https://github.com/bouob/tickets_hunter/issues)。

---

## 已知狀況

**Apple Silicon 的驗證碼辨識可以用。** 2026-09-22 在 M 系列晶片上實測兩場拓元活動：驗證碼
被正確辨識、通過伺服器驗證，一路走到結帳頁。曾有說法指 ARM 環境無法使用圖形驗證碼辨識，
以這次的結果而言並不成立。

若你看到「ddddocr 組件無法使用」，那是安裝問題而不是架構限制——通常是 Python 版本不對，
回到上面的步驟 1 確認用的是 3.10 或 3.11。

**Intel Mac 沒有官方版，也沒有實測過。** 打包流程本身不區分架構，理論上可行，但沒有人跑過。
官方版不含 Intel 是因為 GitHub 的 x86_64 建置環境將於 2027 年 8 月退場，而 macOS 的建置
額度計費是其他系統的 10 倍。若你在 Intel Mac 上成功或失敗，歡迎回報。

**沒有 Apple 簽章。** 簽章與公證需要每年付費的開發者帳號。替代方案是每個版本都附
build provenance attestation，可以驗證檔案確實出自這個 repo 的公開原始碼。

---

## 相關文件

| 文件 | 說明 |
|------|------|
| [快速入門指南](quick-start.md) | 設定與首次搶票 |
| [詳細設定說明](settings-guide.md) | 所有設定欄位的完整說明 |
| [關鍵字與回退機制](keyword-mechanism.md) | 日期與區域關鍵字怎麼寫 |
