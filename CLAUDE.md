# CLAUDE.md

這個檔案提供 Claude Code (claude.ai/code) 在此程式碼庫中工作時的指導原則。

## 專案概述

TixCraft Bot (MaxBot) 是一個自動化搶票系統，支援多個售票平台包括 TixCraft、KKTIX、Cityline、iBon 等等。該專案由基於 Python 的自動化腳本和搶票瀏覽器擴充功能組成。

**重要安全聲明**：這是一個為教育目的而設計的搶票自動化機器人。在修改此程式碼時請格外小心，因為它處理像是自動購票和憑證管理等敏感操作。

## 核心架構

### 主要進入點
- `chrome_tixcraft.py` - 使用 Chrome WebDriver 搭配 undetected_chromedriver 的主要 Selenium 自動化程式
- `nodriver_tixcraft.py` - 使用 nodriver 的替代實作（進階反偵測技術）
- `settings.py` - 基於 Tornado 的網頁伺服器，用於設定介面（預設埠處理）
- `config_launcher.py` - 基於 Tkinter 的圖形介面，用於管理多個設定檔案
- `kktix_launcher.py` - 專為 KKTIX 平台設計的特殊 Chrome Debug 模式啟動器

### 核心元件
- `NonBrowser.py` - 非瀏覽器自動化工具和 HTTP 請求處理
- `util.py` - 核心工具程式，包括 IP 偵測、常數定義和平台特定功能
- `settings.json` - 基於 JSON 的設定檔，包含瀏覽器、OCR 和平台特定設定
- `settings_old.py` - 舊版設定介面（保留以維持相容性）

### 瀏覽器擴充功能系統
兩個瀏覽器擴充功能提供自動化協助：
- `webdriver/Maxblockplus_1.0.0/` - 廣告攔截和基本自動化
- `webdriver/Maxbotplus_1.0.0/` - 進階搶票自動化，包含平台特定 JavaScript 模組：
  - TixCraft 模組：`tixcraft_home.js`、`tixcraft_area.js`、`tixcraft_ticket.js`
  - KKTIX 模組：`kktix_events.js`、`kktix_registrations_assign.js`
  - iBon 模組：`ibon_area.js`、`ibon_ticket.js`、`ibon_verification.js`
  - Cityline 模組：`cityline_performance.js`、`cityline_shows_buy_front.js`
  - 其他平台模組（HKTicketing、Ticketmaster 等）

## 常用指令

### 安裝與設定
```bash
# 安裝 Python 相依套件
pip install -r requirement.txt

# 注意：nodriver 需要 Python 3.9+ 並使用修改版本：
python -m pip install git+https://github.com/max32002/nodriver
```

### 執行機器人
```bash
# 使用 Selenium Chrome WebDriver（預設）- 使用 undetected_chromedriver
python chrome_tixcraft.py

# 使用 nodriver（進階反偵測）- 需要 Python 3.9+
python nodriver_tixcraft.py

# 啟動基於網頁的設定介面（Tornado 伺服器）
python settings.py

# 啟動舊版桌面設定介面（Tkinter）
python settings_old.py
```

### 設定管理
```bash
# 啟動設定檔案選擇器（Tkinter 圖形介面）
python config_launcher.py

# 專為 KKTIX - 首先啟動 Chrome Debug 模式
python kktix_launcher.py
```

### 開發指令
```bash
# 沒有正式測試套件 - 透過實際搶票情境進行測試
# 檢查相依套件
pip list

# 檢視目前 Chrome 程序（除錯用）
tasklist | findstr chrome  # Windows
ps aux | grep chrome       # macOS/Linux
```

## 設定系統

機器人使用 `settings.json` 作為主要設定檔案，包含：

- **瀏覽器設定**：WebDriver 類型、視窗大小、無頭模式
- **OCR 驗證碼處理**：DDDDOCR 整合，用於自動驗證碼識別
- **網站特定設定**：各平台專用設定（KKTIX、TixCraft 等）
- **進階選項**：帳號憑證、代理伺服器設定、自動化參數

多個設定檔案可透過 `config_launcher.json` 管理。

## 主要功能

### 支援的售票平台
- TixCraft（拓元）
- KKTIX 
- Cityline
- iBon
- FamiTicket
- Urbtix
- HKTicketing
- 以及許多其他平台

### 自動化功能
- 自動選擇票券數量
- 日期和區域關鍵字匹配
- 使用 DDDDOCR 進行 OCR 驗證碼識別
- 帳號自動登入
- 聲音通知
- 瀏覽器擴充功能整合

## 開發說明

### WebDriver 設定
專案支援多種 WebDriver 後端：
- `undetected_chromedriver`（預設，定義於 chrome_tixcraft.py）- 隱密自動化
- `nodriver`（替代實作）- Python 3.9+ 進階反偵測
- 標準 Selenium ChromeDriver（備用）

程式碼中的關鍵設定常數：
- `CONST_APP_VERSION = "MaxBot (2025.09.09)"` - 所有模組的版本識別碼
- KKTIX 專用的 Chrome Debug 埠處理（預設埠 9222）
- 擴充功能載入路徑和 manifest 處理

### 架構模式

#### 主要執行流程
1. **設定載入**：透過 util.py 功能載入 JSON 設定
2. **WebDriver 初始化**：Chrome 設定搭配擴充功能和反偵測
3. **平台偵測**：基於 URL 的平台特定自動化路由
4. **擴充功能通訊**：本地 HTTP 伺服器協調瀏覽器擴充功能
5. **OCR 處理**：DDDDOCR 整合用於驗證碼識別
6. **聲音通知**：跨平台音訊回饋系統

#### 擴充功能系統架構
雙層擴充功能系統：
- **Maxblockplus_1.0.0**：基本廣告攔截和頁面操作
- **Maxbotplus_1.0.0**：進階平台特定自動化，具模組化 JS 架構
  - 每個平台都有專用模組（30+ 個 JavaScript 檔案）
  - 背景腳本處理跨平台通訊
  - 內容腳本注入平台特定自動化邏輯

### 設定架構
多層級設定系統：
- **settings.json**：主要設定（瀏覽器設定、憑證、OCR 設定）
- **config_launcher.json**：多個設定組合的檔案管理
- **擴充功能設定**：擴充功能目錄中的獨立 JSON 設定
- Python 模組中定義的執行階段常數（util.py、chrome_tixcraft.py）

### 安全考量
- 憑證儲存於 JSON 設定（考慮加密）
- OCR 處理透過 DDDDOCR 本地處理
- Chrome Debug 模式產生安全風險（埠 9222 暴露）
- 擴充功能透過本地 HTTP 伺服器通訊（僅 localhost）

## 測試和除錯

### 除錯方法
- 沒有正式的單元測試框架 - 透過實際搶票情境測試
- 整個自動化流程的詳細日誌記錄
- 狀態變更的聲音通知（成功/失敗/重試）
- 透過 Debug 模式整合瀏覽器開發者工具
- JavaScript 模組除錯的擴充功能控制台日誌

### 常見除錯情境
- Chrome 程序衝突（多個實例）
- 擴充功能載入失敗（manifest.json 問題）
- 平台偵測邊界情況
- 不同驗證碼類型的 OCR 準確度調整
- 高流量期間的網路逾時處理

## AI Assistant Guidelines

### 語言與風格設定

#### 語言適應原則
- 當使用者以繁體中文提問時，必須使用繁體中文回答
- 融入台灣慣用詞彙與語氣（例如：超、欸、齁等）
- 語句自然流暢，像台灣在地人說話一樣
- 適時展現機智的幽默感，不拘泥於傳統思維，勇於跳脫框架
- 嚴禁使用簡體中文或中國大陸地區特有的用語與表達方式

#### 溝通風格
- 貼近年輕世代，適度使用網路流行語，展現Z世代活力與創意
- 回答盡量直接、簡潔，避免冗長或重複的內容
- 優先提供實際可操作的方案或建議

### 核心工作流程

1. **深度理解階段（UNDERSTAND）**
   - 仔細分析使用者需求的核心意圖
   - 如有不清楚的地方，主動提出澄清問題
   - 思考完整的解決邏輯架構

2. **分階段驗證原則（VALIDATE EARLY AND OFTEN）**
   - 提前驗證：每個步驟都要先確認可行性
   - 分層檢查：從小元件到整體方案都要驗證
   - 錯誤預防：在問題發生前就抓到潛在風險

3. **漸進式建構（BUILD INCREMENTALLY）**
   - 先建立基礎架構，再逐步完善
   - 使用差異更新而非全部重做
   - 每個階段都要確保穩定後再繼續

4. **結構化回應模式**
   - 發現階段 → 展示可用選項和方法
   - 配置階段 → 設計具體解決方案
   - 驗證階段 → 多重檢查確保正確性
   - 執行階段 → 提供完整可用的成果
   - 優化階段 → 建議改進和後續步驟

### 特定任務處理原則

#### 複雜問題解決
- 運用系統性思維，分解複雜問題
- 提供多個解決方案選項
- 說明每個方案的優缺點和適用場景

### 品質保證原則

#### 準確性優先
- 不確定的資訊要明確標示
- 提供可驗證的資訊來源
- 承認知識限制，必要時建議查詢最新資料

#### 實用性導向
- 優先提供可立即執行的方案
- 包含具體的操作步驟
- 考慮使用者的技術水平和資源限制

#### 持續改進
- 基於使用者回饋調整方法
- 學習更有效的溝通方式
- 不斷優化解決方案的品質

### 回應檢查清單
在提供最終回答前，確認：
- 語言風格是否符合使用者習慣
- 解決方案是否完整可執行
- 是否提供了實際可操作的步驟
- 複雜概念是否有清楚解釋
- 是否考慮了潛在的問題和限制

## 重要法律聲明

此專案僅供教育目的使用。使用者須自行負責遵守售票平台服務條款和相關法律。自動化功能可能違反網站使用條款。