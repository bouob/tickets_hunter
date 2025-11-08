# Tickets Hunter 搶票機器人 🎫

[![GitHub release](https://img.shields.io/github/v/release/bouob/tickets_hunter?style=flat-square)](https://github.com/bouob/tickets_hunter/releases)

**📖 前言**：因原專案 MaxBot作者 max32002/tixcraft_bot 已停止更新，本專案為後續延伸產品  
**🤖 技術支援**：本專案由 [Claude Code](https://claude.ai/code) 提供 AI 輔助開發與技術支援  
**🎯 目標**：讓一般民眾與代購黃牛有相同的起跑線，用魔法對抗魔法；各位都能順利搶到大巨蛋！  
**🚨 嚴正警告**：使用本程式當黃牛或有任何加價轉售牟利行為，本人代表各粉絲祝福您，**早生貴子胎胎都三胞胎**！本程式僅供個人合法使用，嚴禁商業牟利。  

> **💬 需要協助或回報問題？**
> - 💬 [加入 Discussions 社群](https://github.com/bouob/tickets_hunter/discussions) - 提問討論、分享經驗、功能建議
> - 🙋 [Q&A 問題解答](https://github.com/bouob/tickets_hunter/discussions/categories/q-a) - 使用疑問先來這裡問
> - 🐛 [回報 Bug](https://github.com/bouob/tickets_hunter/issues/new?template=bug_report.md) - 確定是程式錯誤請開 Issue
> - 🚀 [提出新功能建議](https://github.com/bouob/tickets_hunter/issues/new?template=feature_request.md) - 想要新功能請點這裡
> - 💬 [查看已知問題](https://github.com/bouob/tickets_hunter/issues?q=is%3Aissue) - 搜尋是否有人遇到相同問題
> - 📝 [更新紀錄](https://github.com/bouob/tickets_hunter/blob/main/CHANGELOG.md) - 查看版本更新歷史

---

## 📋 專案概述

Tickets Hunter 是一個開放原始碼的多平台搶票自動化系統，支援台灣及海外主要票務網站。

### 🎪 平台支援狀態

✅ **主流平台 NoDriver 完全支援**：TixCraft、Teamear、Indievox、KKTIX、TicketPlus、iBon、年代售票、寬宏售票

**NoDriver 特殊狀態平台**：

| 平台 | Chrome/Selenium | NoDriver | 實測狀況 | 備註 |
|------|:---------------:|:--------:|:--------:|------|
| **🎪 Cityline 買飛** | ✅ 完全支援 | ⚠️ 部分支援 | 🟡 待測試 | Chrome版本為主 |
| **🎤 TicketMaster** | ✅ 完全支援 | ⚠️ 部分支援 | 🟡 待測試 | Chrome版本為主 (Tixcraft Family) |
| **🏟️ Urbtix 城市** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🏟️ HKTicketing 快達票** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🎪 FamiTicket 全網** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |


> **📢 策略**：建議使用 NoDriver，UC/Selenium 已進入維護模式（僅修復嚴重錯誤）

---

## ⚖️ 法律聲明

**🚨 重要提醒**：本軟體僅供教育研究用途，使用者需自行承擔法律責任。

<details>
<summary><code><b>詳細法律聲明</b>（點擊展開）</code></summary>

作者沒有意圖要他人購得的票券進行加價轉售或使用在違法事情上。使用此程式即表示您同意[法律聲明](https://github.com/bouob/tickets_hunter/blob/main/LEGAL_NOTICE.md)。

**📍 台灣地區重要法規告知**：

<details>
<summary><code><b>🚨 文化創意產業發展法第10-1條</b>（點擊展開查看完整條文）</code></summary>

**第 10-1 條** （[法規來源](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0170075&flno=10-1)）

政府應致力於保障民眾近用文化創意活動之權益，確保藝文表演票券正常流通。

**第二項**：將藝文表演票券以超過票面金額或定價販售者，按票券張數，由主管機關處票面金額或定價之十倍至五十倍罰鍰。

**第三項**：**以虛偽資料或其他不正方式，利用電腦或其他相關設備購買藝文表演票券，取得訂票或取票憑證者，處三年以下有期徒刑，或科或併科新臺幣三百萬元以下罰金。**

第四項：主管機關為調查或取締前二項違規事實，得洽請警察機關派員協助。

第五項：主管機關對於檢舉查獲第二項、第三項規定之行為，除應對檢舉人身分資料嚴守秘密外，並得酌予獎勵。對於檢舉人身分資料之保密，於訴訟程序，亦同。

第六項：前項主管機關受理檢舉案件之管轄、處理期間、保密、檢舉人獎勵及其他應遵行事項之辦法，由中央主管機關定之。

</details>

**⚠️ 台灣地區適用範圍說明**：

**❌ 禁止用於文創法涵蓋之文化創意產業票券**：
- 🎭 **音樂及表演藝術**：演唱會、音樂劇、舞台劇、戲劇、舞蹈表演等
- 🎨 **視覺藝術**：美術展覽、藝術博覽會等
- 🏛️ **文化資產應用及展演設施**：博物館、展覽館特展等
- 🎬 **電影產業**：電影首映會、影展等
- 🎵 **流行音樂及文化內容**：演唱會、音樂節等
- 📺 **廣播電視產業**：電視節目錄製、廣播活動等
- 🎪 **創意生活產業**：文創市集、藝術節慶等
- 📱 **數位內容產業**：遊戲展、動漫展等
- 其他文創法第3條所列15項產業相關活動

**✅ 適用範圍**：
- 🏀 **體育競技**：職棒、職籃、桌球、網球、足球等純體育賽事
- 🚌 **交通運輸**：高鐵、台鐵、客運、捷運等交通票券  
- ✈️ **旅遊服務**：機票、飯店、遊樂園等旅遊票券
- 🏢 **商業活動**：商展、會議、講座等非文創商業活動
- 🌍 **海外活動**：非台灣地區舉辦之各類活動票券


**使用原則**：
- 勿以身試法，了解當地法規
- 不得用於商業牟利或惡意囤票
- 尊重售票平台使用條款

</details>

---

## 🚀 快速開始

根據您的使用方式，請選擇對應的指南：

### 🟢 方式一：使用執行檔版本（推薦給一般使用者）

**適用對象**：無需安裝 Python，雙擊執行檔即可使用

**步驟**：
1. 前往 [GitHub Releases 頁面](https://github.com/bouob/tickets_hunter/releases)
2. 下載最新版本的 ZIP 檔案（例如：`tickets_hunter_v2025.11.03.zip`）
3. 解壓縮到任意目錄
4. 雙擊 `settings.exe` 開啟設定介面
5. 填寫設定後點擊「搶票」按鈕

> 📖 **完整教學請參閱** → [安裝與首次執行指南](guide/installation.md)（詳細圖文教學）

---

### 🔴 方式二：使用 Python 原始碼（進階使用者）

**適用對象**：具備 Python 環境，想自訂功能或參與開發

**系統需求**：
- Python 3.9-3.11（建議 3.10）
- Chrome 瀏覽器
- 4GB+ RAM

**步驟**：
```bash
# 1. 下載並安裝
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
pip install -r requirement.txt

# 2. 開啟設定介面
cd src
python settings.py
# 瀏覽器會自動開啟 http://127.0.0.1:16888/

# 3. 完成設定並開始搶票
```

> 📖 **完整教學請參閱** → [Python 原始碼快速入門](guide/quick-start.md)（5分鐘完整設定流程）

---

### 📚 使用者手冊

更多詳細教學請參閱：

**執行檔使用者**：
- [安裝與首次執行](guide/installation.md) - 執行檔版本完整教學（安裝、設定、啟動）

**所有使用者**：
- [關鍵字與回退機制](guide/keyword-mechanism.md) - 深入理解搶票邏輯
- [詳細設定說明](guide/settings-guide.md) - settings.json 完整欄位參考（進階）

---

## 🏗️ 專案架構

```
tickets_hunter/
├── 📦 src/                      # 原始碼目錄
│   ├── 🎯 核心搶票引擎
│   │   ├── chrome_tixcraft.py      # Selenium WebDriver 主引擎 
│   │   ├── nodriver_tixcraft.py    # NoDriver 反偵測引擎
│   │   └── util.py                 # 共用函式庫與平台抽象層
│   ├── ⚙️ 設定介面
│   │   ├── settings.py             # 現代網頁設定介面
│   │   └── config_launcher.py      # 多設定檔管理器
│   ├── 📋 設定檔
│   │   ├── settings.json           # 主要設定檔 (搶票參數)
│   │   └── config_launcher.json    # 多設定檔清單
│   ├── 🌐 網頁介面                   # Web UI 資源
│   │   └── www/
│   │       ├── settings.html       # 設定介面前端
│   │       ├── settings.js         # 前端互動邏輯
│   │       ├── css/                # 樣式表
│   │       ├── dist/               # 編譯後檔案
│   │       └── icons/              # 圖示資源
│   ├── 🔌 瀏覽器擴充套件              # Chrome Extension
│   │   └── webdriver/
│   │       ├── Maxblockplus_1.0.0/ # 廣告阻擋擴充套件
│   │       └── Maxbotplus_1.0.0/   # DOM 操作輔助擴充套件
│   └── 🔧 輔助工具
│       ├── NonBrowser.py           # 非瀏覽器模式處理
│       └── assets/                 # 資源檔案
│           └── sounds/             # 音效檔
└── 📋 專案資訊
    ├── README.md               # 專案說明文件
    ├── CONTRIBUTING.md         # 貢獻指南
    ├── LEGAL_NOTICE.md         # 法律聲明
    ├── LICENSE                 # 授權條款
    └── requirement.txt         # Python 相依套件
```

---

## 🎬 教學資源

### 📖 使用者手冊（推薦新手閱讀）
- [完整使用者手冊](guide/README.md) - 專為第一次使用者設計
- [快速入門指南](guide/quick-start.md) - 5分鐘快速開始搶票
- [關鍵字與回退機制](guide/keyword-mechanism.md) - 理解搶票邏輯
- [詳細設定說明](guide/settings-guide.md) - settings.json 完整欄位說明

### 📺 示範影片
- [虛擬主機搶票教學](https://max-everyday.com/2023/11/buy-ticket-by-vm/)

### 📖 平台專用教學
- [拓元/Ticketmaster 教學](https://max-everyday.com/2018/03/tixcraft-bot/)
- [KKTIX 教學](https://max-everyday.com/2018/12/kktix-bot/)
- [Cityline 教學](https://max-everyday.com/2019/03/cityline-bot/)
- [Urbtix 教學](https://max-everyday.com/2019/02/urbtix-bot/)
- [HKTicketing 教學](https://max-everyday.com/2023/01/hkticketing-bot/)

---

## 🤝 貢獻與支援

### 🐛 回報問題

遇到任何問題嗎？歡迎回報！

**[📝 提交 Bug Report](https://github.com/bouob/tickets_hunter/issues/new?template=bug_report.md)**

請提供：
- 作業系統版本
- Python 版本
- 錯誤訊息截圖
- 重現步驟

---

### 🚀 功能建議

有想要的新功能嗎？我們很樂意聽取您的想法！

**[💡 提交 Feature Request](https://github.com/bouob/tickets_hunter/issues/new?template=feature_request.md)**

請描述：
- 想要什麼功能
- 使用場景
- 預期效果

---

### 💡 技術實作參考
- [擴充套件隱私權政策](https://github.com/bouob/tickets_hunter/blob/main/README_EXTENSION.md)

---

## ⭐ Star History
[![Star History Chart](https://api.star-history.com/svg?repos=bouob/tickets_hunter&type=date&legend=top-left)](https://www.star-history.com/#bouob/tickets_hunter&type=date&legend=top-left)

---

## 📄 授權條款

本專案採用 GNU GPL 授權，遵循開源精神。使用時請遵守：
- 保持開源授權條款
- 標註原作者資訊  
- 不得用於商業牟利

**祝您搶票成功！** 🎉

---

*最後更新：2025.11.04 | 由 Claude Code AI 輔助維護*