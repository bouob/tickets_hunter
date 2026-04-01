# 安裝與環境設定

**文件說明**：引導開發者完成 Tickets Hunter 環境設定、依賴套件安裝與開發環境準備
**最後更新**：2026-03-09

---

## 系統需求

### 必要條件
| 項目 | 需求 | 說明 |
|------|------|------|
| **Python** | **3.10-3.11**（推薦） | 完整支援所有功能 |
| Python | 3.12 | 可能支援，部分套件相容性待驗證 |
| Python | 3.13+ | ❌ 不支援（ddddocr 不相容） |
| **Chrome** | 90+ | 建議使用最新穩定版 |
| **作業系統** | Windows 10/11 | 主要支援平台 |
| 作業系統 | macOS / Linux | 部分功能支援 |

### 硬體建議
- **記憶體**：4GB 以上（建議 8GB）
- **網路**：穩定的網路連線（搶票時延遲敏感）
- **磁碟空間**：500MB 以上（含 OCR 模型）

---

## 快速安裝（一般使用者）

### 方式一：使用 exe 執行檔（推薦）
1. 從 [Releases 頁面](https://github.com/bouob/tickets_hunter/releases) 下載最新版本
2. 解壓縮後直接執行 `settings.exe` 開啟設定介面
3. 設定完成後點擊「搶票」按鈕

### 方式二：從原始碼安裝

#### 1. 安裝 Python 3.10-3.11
```bash
# Windows - 從官網下載
# https://www.python.org/downloads/

# 確認版本
python --version  # 應顯示 Python 3.10.x 或 3.11.x
```

> **注意**：安裝時請勾選「Add Python to PATH」

#### 2. 下載專案
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
```

#### 3. 安裝基本套件
```bash
pip install -r requirement.txt
```

#### 4. ZenDriver 安裝（推薦）
```bash
# 從 PyPI 安裝（推薦）
pip install zendriver

# ZenDriver 是 nodriver 的活躍 fork，支援 Chrome 145+ 並有持續維護
```

#### 5. OCR 驗證碼辨識（選用）
```bash
pip install ddddocr
```

---

## WebDriver 模式選擇

在設定介面的「瀏覽器設定」中選擇，或直接編輯 `settings.json` 的 `webdriver_type`：

| 模式 | 值 | 說明 | 推薦度 |
|------|-----|------|--------|
| **ZenDriver** | `"nodriver"` | 最強反偵測，支援 12 個平台（後端為 zendriver，nodriver 的活躍 fork） | ⭐⭐⭐ 推薦 |
| Chrome | `"chrome"` | 傳統模式，維護中 | ⭐ |

### ZenDriver 支援平台（12 個完全支援）

| 類別 | 平台 | 完成度 |
|------|------|--------|
| **TixCraft Family** | 拓元、添翼、獨立音樂 | 95% |
| **台灣主流** | KKTIX、TicketPlus、iBon | 95% |
| **年代/寬宏** | KHAM、年代售票、UDN | 90-100% |
| **其他** | TicketMaster、HK Ticketing、FamiTicket | 89-98% |

---

## 設定介面

### 網頁介面（推薦）
```bash
cd tickets_hunter/src
python settings.py
# 開啟瀏覽器訪問 http://127.0.0.1:16888/
```

### 桌面介面（舊版）
```bash
cd tickets_hunter/src
python settings_old.py
```

---

## 執行搶票程式

### ZenDriver 模式（推薦）
```bash
cd tickets_hunter/src
python nodriver_tixcraft.py
```

### 使用自訂設定檔
```bash
python nodriver_tixcraft.py --input path/to/settings.json
```

---

## 除錯模式

### 詳細輸出（verbose）
```bash
python nodriver_tixcraft.py --verbose
```

### 快速測試指令
```bash
# 清除快取並執行 30 秒測試
rm -rf src/__pycache__ && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

> **注意**：測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即進入暫停狀態。

---

## 多設定檔執行

編輯 `src/config_launcher.json`：
```json
{
  "profiles": [
    "settings.json",
    "settings_profile2.json"
  ]
}
```

執行：
```bash
cd tickets_hunter/src
python config_launcher.py
```

---

## 時間功能設定

### 1. 效能計時功能
**用途**：測量搶票流程耗時，用於效能分析

**啟用方式**（settings.json）：
```json
{
  "advanced": {
    "verbose": true
  }
}
```

**輸出範例**：
```
bot elapsed time: 2.458 秒
TicketPlus 搶票耗時: 1.823 秒
```

### 2. 定時啟動功能
**用途**：在指定時間自動重整頁面啟動搶票

**設定方式**（settings.json）：
```json
{
  "refresh_datetime": "14:00:00"
}
```

**時間格式**：HH:MM:SS (24小時制)
- `"14:00:00"` - 下午2點整
- `"09:30:00"` - 上午9點30分
- `""` - 停用功能

**使用情境**：
1. 已知開賣時間（如下午2點）
2. 提前 5-10 分鐘啟動程式並導航到售票頁面
3. 程式會在指定時間自動重整並開始搶票

---

## 重要設定說明

### 日期/區域關鍵字設定
支援 AND/OR 邏輯篩選：
```json
{
  "date_keyword": "12/25,12/26",
  "area_keyword": "搖滾區,站區"
}
```

**AND 邏輯**（同時包含）：
```json
{
  "date_keyword": "[\"12/25\", \"晚場\"]"
}
```

### 自動遞補設定
```json
{
  "date_auto_fallback": true,
  "area_auto_fallback": true,
  "auto_select_mode": "random"
}
```

| 設定 | 說明 |
|------|------|
| `date_auto_fallback` | 日期關鍵字無匹配時自動選擇 |
| `area_auto_fallback` | 區域關鍵字無匹配時自動選擇 |
| `auto_select_mode` | `"random"` / `"from_top"` / `"from_bottom"` |

### OCR 驗證碼設定
```json
{
  "ocr_captcha": {
    "enable": true,
    "beta": true,
    "force_submit": true,
    "image_source": "canvas",
    "use_universal": true,
    "path": "assets/model/universal"
  }
}
```

| 設定 | 說明 |
|------|------|
| `enable` | 啟用 OCR 自動辨識 |
| `beta` | 使用 ddddocr beta 模型（fallback 時啟用） |
| `force_submit` | 辨識後自動送出，不等待確認 |
| `use_universal` | 使用內建通用 OCR 模型（準確率 99-100%） |
| `path` | 通用模型路徑（預設：`assets/model/universal`） |

---

## 常見問題

### Python 版本問題

**問題**：`ModuleNotFoundError` 或套件安裝失敗

**解決**：確認使用 Python 3.10-3.11
```bash
python --version

# 使用 virtualenv 隔離環境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirement.txt
```

### OCR 功能無法使用

**問題**：`ModuleNotFoundError: No module named 'ddddocr'`

**解決**：
```bash
pip install ddddocr
```

### ZenDriver 連線失敗

**問題**：`Connection refused` 或 `Cannot connect to browser`

**解決**：
1. 確認沒有其他 Chrome 實例在運行
2. 關閉所有 Chrome 視窗後重試
3. 檢查防火牆設定

### 程式立即暫停

**問題**：程式啟動後立即進入暫停狀態

**解決**：刪除暫停標記檔案
```bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
```

### 編碼錯誤 (cp950)

**問題**：`UnicodeEncodeError: 'cp950' codec can't encode character`

**解決**：
1. 確認 Python 代碼中沒有 emoji
2. 設定環境變數：`set PYTHONIOENCODING=utf-8`

---

## 進階設定

### 瀏覽器 Profile 設定
保留登入狀態：
```json
{
  "browser": {
    "profile_name": "MaxBot"
  }
}
```

### Headless 模式
無圖形界面運行：
```json
{
  "advanced": {
    "headless": true
  }
}
```

> **注意**：headless 模式下部分平台可能偵測到自動化

### 音效提醒
搶票成功時播放音效：
```json
{
  "advanced": {
    "play_sound": {
      "ticket": true,
      "order": true,
      "filename": "assets/sounds/ding-dong.wav"
    }
  }
}
```

| 設定 | 說明 |
|------|------|
| `ticket` | 找到票時播放音效 |
| `order` | 送出訂單時播放音效 |
| `filename` | 音效檔路徑（相對於程式執行目錄） |

### 通知設定
購票成功時發送 Discord/Telegram 通知：
```json
{
  "advanced": {
    "discord_webhook_url": "https://discord.com/api/webhooks/...",
    "telegram_bot_token": "123456:ABC-DEF...",
    "telegram_chat_id": "-100123456789"
  }
}
```

### 其他進階設定

| 設定 | 說明 | 預設值 |
|------|------|--------|
| `advanced.show_timestamp` | 除錯訊息顯示時間戳記 `[HH:MM:SS]` | `false` |
| `advanced.discount_code` | 優惠序號（TicketPlus、KKTIX 等） | `""` |
| `advanced.server_port` | 設定介面 Web Server 埠號 | `16888` |
| `advanced.headless` | 無頭模式（背景執行） | `false` |

---

## 相關文件

| 文件 | 說明 |
|------|------|
| [專案概覽](./project_overview.md) | 整體架構介紹 |
| [開發規範](../02-development/development_guide.md) | 開發者指南 |
| [NoDriver API](../06-api-reference/nodriver_api_guide.md) | NoDriver 技術文件 |

---

**最後更新**: 2026-03-09
