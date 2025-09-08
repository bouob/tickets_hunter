# 🎫 Ticket Hunter - 票券獵人 智慧搶票系統

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/bouob/ticket-hunter)

> **⚠️ 重要聲明：本專案僅供教育研究用途，使用者需自行承擔相關法律責任並遵守各售票平台服務條款。**

## 📋 專案概述

Ticket Hunter (票券獵人) 是一個強大的自動化搶票系統，支援台灣及香港地區多個主流售票平台。透過先進的 OCR 技術和智慧化自動操作，大幅提升搶票成功率。

> **📍 專案源起**：本專案前身為知名的 [MaxBot 搶票機器人](https://github.com/max32002/tixcraft_bot)，由於原作者 [max32002](https://github.com/max32002) 已關閉專案，此為社群維護的衍生版本，持續為廣大使用者提供搶票服務。
> 
> **🤖 技術支援**：本專案由 [Claude Code](https://claude.ai/code) 提供 AI 輔助開發與技術支援，確保程式碼品質與功能穩定性。

### 🎯 支援平台

- **🎪 TixCraft (拓元售票)**
- **🎵 KKTIX**
- **🎭 Cityline (城市售票)**
- **🎨 iBon**
- **🎬 FamiTicket**
- **🎪 Urbtix**
- **🎫 HKTicketing (快達票)**
- **🌟 Ticketmaster Singapore**
- **🎰 Galaxy Macau (澳門銀河)**
- **🎪 年代售票系統**
- **🎫 遠大售票系統**
- **🎵 IndieVox**

## ✨ 核心功能

### 🤖 智慧自動化
- **自動登入**：支援帳號密碼 & Cookie 登入
- **智慧選票**：自動選擇日期、場次、區域、票價
- **OCR 驗證碼**：使用 DDDDOCR 自動識別驗證碼
- **關鍵字匹配**：支援多組關鍵字與優先順序設定
- **自動重試**：網路異常或失敗時自動重新嘗試

### 🛠️ 進階功能
- **多開支援**：同時運行多個瀏覽器實例
- **聲音提醒**：重要操作時播放音效通知
- **視窗大小調整**：方便多開時的視窗管理
- **代理伺服器**：支援 Proxy 設定 (HTTP/HTTPS)
- **擴充功能**：內建瀏覽器擴充功能輔助

### 🔧 技術特色
- **Stealth 模式**：使用 undetected-chromedriver 避開偵測
- **nodriver 支援**：更進階的反偵測技術
- **多重 WebDriver**：Chrome、Edge、Firefox 支援
- **設定檔管理**：支援多設定檔切換

## 🚀 快速開始

### 📦 系統需求

- **Python 3.9+**
- **Chrome 瀏覽器** (建議最新版本)
- **Windows / macOS / Linux**

### ⚡ 安裝步驟

1. **複製專案**
   ```bash
   git clone https://github.com/bouob/ticket-hunter.git
   cd ticket-hunter
   ```

2. **安裝相依套件**
   ```bash
   pip install -r requirement.txt
   
   # nodriver 特殊版本 (需要 Python 3.9+)
   python -m pip install git+https://github.com/max32002/nodriver
   ```

3. **設定參數**
   ```bash
   # 啟動設定介面
   python settings.py
   ```

4. **開始使用**
   ```bash
   # 使用 Selenium Chrome WebDriver (預設)
   python chrome_tixcraft.py
   
   # 使用 nodriver (進階反偵測)
   python nodriver_tixcraft.py
   
   # 多設定檔管理
   python config_launcher.py
   ```

## ⚙️ 設定指南

### 🎛️ 基本設定

透過 `settings.py` 開啟網頁設定介面，主要設定項目：

- **瀏覽器設定**：WebDriver 類型、視窗大小、無頭模式
- **帳號資訊**：登入帳號密碼或 Cookie
- **搶票偏好**：日期關鍵字、區域關鍵字、票價偏好
- **驗證碼處理**：OCR 自動識別設定
- **聲音提醒**：成功/失敗音效設定

### 📝 設定檔說明

主要設定檔 `settings.json` 包含：

```json
{
  "homepage": "https://tixcraft.com",
  "browser": "chrome",
  "webdriver_type": "undetected_chromedriver",
  "ocr_captcha": {
    "enable": true,
    "module": "ddddocr"
  },
  "advanced": {
    "auto_login": true,
    "play_sound": true,
    "sound_filename": "ding-dong.wav"
  }
}
```

### 🔧 進階設定

- **多設定檔**：使用 `config_launcher.json` 管理多個設定組合
- **代理設定**：支援 HTTP/HTTPS Proxy
- **Cookie 登入**：避開帳號密碼登入的風險
- **關鍵字優先級**：設定多組關鍵字的搜尋順序

## 💡 使用技巧

### 基本操作
1. 首次使用建議執行 `python settings.py` 進行設定
2. 設定完成後執行 `python chrome_tixcraft.py` 開始搶票
3. 支援多視窗同時搶票，每個視窗可設定不同參數

### 🎯 KKTIX 專用模式（重要！）

**針對 KKTIX 網站，需要使用特殊的 Chrome Debug 模式避免 Cloudflare 檢測：**

#### 使用流程：
1. **第一步：啟動 Chrome Debug 模式**
   ```bash
   python kktix_launcher.py
   ```
   - 會自動啟動獨立的 Chrome Debug 實例
   - 請在新開的 Chrome 中前往 KKTIX 網站並完成登入

2. **第二步：執行設定介面**
   ```bash
   # 網頁版設定介面（推薦）
   python settings.py
   
   # 或桌面版設定介面
   python settings_old.py
   ```
   - 程式會自動偵測 KKTIX 網站
   - 自動檢查 Chrome Debug 模式是否就緒
   - 點擊「執行」開始搶票

#### 優點：
- 避免被 Cloudflare 識別為機器人
- 保留真實的 Cookie 和登入狀態
- 大幅提升 KKTIX 搶票成功率

#### 限制：
- **KKTIX 不支援多視窗搶票** - 一次只能開啟一個 KKTIX 搶票視窗
- 其他售票網站仍可正常使用多視窗功能

## 📱 瀏覽器擴充功能

內建 **Ticket Hunter Plus** 擴充功能提供：

- **廣告攔截**：提升頁面載入速度
- **DOM 操作**：輔助票券選擇
- **自動重新整理**：避開頁面逾時
- **驗證碼輔助**：提升識別準確率

擴充功能位置：`webdriver/Maxblockplus_1.0.0/`

## 🎥 示範影片

詳細的操作示範與功能介紹，請參考 [demo_video.md](demo_video.md)

最新功能展示：
- 信用卡活動自動填寫
- Cityline 自動購票  
- KKTIX 多開技巧

## 🛡️ 安全注意事項

### ⚠️ 重要提醒

1. **使用限制**：
   - 遵守各平台服務條款與使用規範
   - 避免大量頻繁請求造成伺服器負擔
   - 尊重其他使用者權益，理性搶票

2. **法律責任**：
   - 本工具僅供研究學習使用
   - 使用者需自行承擔所有法律風險
   - 不得用於商業營利目的

## 🤝 貢獻指南

歡迎貢獻程式碼、回報問題或提出建議！

### 📋 貢獻方式

1. **Fork** 本專案
2. 建立功能分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m '✨ 新增超棒功能'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 開啟 **Pull Request**

### 🐛 問題回報

請使用 [GitHub Issues](https://github.com/bouob/ticket-hunter/issues) 回報問題，並提供：

- 作業系統版本
- Python 版本
- 詳細錯誤訊息
- 重現步驟

## 📄 授權條款

本專案採用 [GNU General Public License v3.0](LICENSE) 授權。

詳細法律聲明請參閱 [LEGAL_NOTICE.md](LEGAL_NOTICE.md)

## 🙏 致謝

- 感謝 [max32002](https://github.com/max32002) 的原始專案 [tixcraft_bot](https://github.com/max32002/tixcraft_bot)
- 感謝所有貢獻者的無私奉獻
- 感謝社群使用者的回饋與建議

## 📞 聯絡資訊

- **專案維護**：[GitHub Issues](https://github.com/bouob/ticket-hunter/issues)
- **技術討論**：[GitHub Discussions](https://github.com/bouob/ticket-hunter/discussions)

---

**⭐ 如果這個專案對你有幫助，請給我們一顆星星！**

**🔗 更多資訊請參閱 [Wiki](https://github.com/bouob/ticket-hunter/wiki)**