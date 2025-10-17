# Tickets Hunter 搶票機器人 🎫

**📖 前言**：因原專案 MaxBot作者 max32002/tixcraft_bot 已停止更新，本專案為後續延伸產品  
**🤖 技術支援**：本專案由 [Claude Code](https://claude.ai/code) 提供 AI 輔助開發與技術支援  
**⚡ 版本**：Tickets Hunter (2025.10.17)
**🎯 目標**：讓一般民眾與代購黃牛有相同的起跑線，用魔法對抗魔法；各位都能順利搶到大巨蛋！

---

## 📋 專案概述

Tickets Hunter 是一個開放原始碼的多平台搶票自動化系統，支援台灣及海外主要票務網站。

### 🎪 平台支援狀態

| 平台 | Chrome/Selenium | NoDriver | 實測狀況 | 備註 |
|------|:---------------:|:--------:|:--------:|------|
| **🎭 TixCraft** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | **建議使用 NoDriver** |
| **🎨 KKTIX** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | **建議使用 NoDriver** |
| **🎵 TicketPlus** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | **建議使用 NoDriver** |
| **🎫 iBon** | ❌ 不修復 | ✅ 完全支援 | 🟢 已測試 | **建議使用 NoDriver** |
| **🎪 Cityline** | ✅ 完全支援 | ⚠️ 部分支援 | 🟡 待測試 | Chrome版本為主 |
| **🎤 TicketMaster** | ✅ 完全支援 | ⚠️ 部分支援 | 🟡 待測試 | Chrome版本為主 |
| **🏟️ Urbtix** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🎭 年代售票** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🎪 寬宏售票** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🏟️ HKTicketing** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |
| **🎪 FamiTicket** | ✅ 完全支援 | ❌ 不支援 | 🟡 待測試 | 僅支援Chrome |


### 🚀 核心特色
- **NoDriver 優先架構** - NoDriver (推薦) + UC (備用) + Selenium (維護模式)
- **OCR 驗證碼辨識** - 整合 ddddocr 自動處理驗證碼
- **智慧化選取** - 日期、區域、票數自動選擇
- **擴充套件輔助** - 廣告阻擋 + DOM 操作加速
- **多設定檔管理** - 不同活動快速切換設定
- **網頁設定介面** - 現代化回應式管理介面

> **✅ NoDriver 引擎狀態更新 (2025.10.15)**
> NoDriver 引擎主流平台（TixCraft、KKTIX、TicketPlus、iBon、KHAM）已實測搶票成功。
> **建議一般使用者優先使用 NoDriver 驅動**，遇到問題可切換至 UC 或 Selenium。
> Selenium 與 UC 已進入維護模式，未來將逐步停止更新。
> 如遇到任何問題請至 [GitHub Issues](https://github.com/bouob/tickets_hunter/issues) 回報。

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
- 📚 **教育研究**：學術研究、技術測試等合法用途

**使用原則**：
- 勿以身試法，了解當地法規
- 不得用於商業牟利或惡意囤票
- 尊重售票平台使用條款

</details>

---

## 💻 安裝與執行

### 🔧 環境設定

**系統需求**
- Python 3.9-3.10 (NoDriver 需 3.9+)
- Chrome 瀏覽器
- 4GB+ RAM (多開瀏覽器需更多)

### 📦 下載方式

**1. 執行檔版本（僅 Windows）**
```
TODO - 尚未計畫打包，請從原始碼執行
```

**2. 原始碼版本（推薦，跨平台）**
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter/src
pip install -r requirement.txt
```


### 🚀 執行方式

**1. 網頁設定介面（推薦）**
```bash
cd tickets_hunter/src
python settings.py
# 瀏覽器自動開啟網頁UI：http://127.0.0.1:16888/
```

**2. 多設定檔管理**
```bash
cd tickets_hunter/src
python config_launcher.py
```

### 🔄 更新方式

**取得最新版本**
```bash
cd tickets_hunter
git pull
```

**或重新下載**
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter/src
pip install -r requirement.txt
```

---

## 🏗️ 專案架構

```
tickets_hunter/
├── 📦 src/                      # 原始碼目錄
│   ├── 🎯 核心搶票引擎
│   │   ├── chrome_tixcraft.py      # Selenium WebDriver 主引擎 (原始版本)
│   │   ├── nodriver_tixcraft.py    # NoDriver 反偵測引擎 (實驗版本 🚧)
│   │   └── util.py                 # 共用函式庫與平台抽象層
│   ├── ⚙️ 設定介面
│   │   ├── settings.py             # 現代網頁設定介面
│   │   ├── settings_old.py         # 傳統桌面介面
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
│           └── sounds/             # 搶票成功音效檔
└── 📋 專案資訊
    ├── README.md               # 專案說明文件
    ├── CONTRIBUTING.md         # 貢獻指南
    ├── LEGAL_NOTICE.md         # 法律聲明
    ├── LICENSE                 # 授權條款
    └── requirement.txt         # Python 相依套件
```

### 🎯 核心 Python 模組說明

| 檔案 | 功能 | 特色 |
|------|------|------|
| `chrome_tixcraft.py` | Selenium 主引擎 | 維護模式，支援所有平台 |
| `nodriver_tixcraft.py` | NoDriver 引擎 | **推薦使用**，反偵測能力強，主流平台已完成 ✅ |
| `util.py` | 共用函式庫 | 平台抽象層，OCR、瀏覽器控制、設定處理 |
| `settings.py` | 現代網頁設定介面 | Tornado 伺服器，響應式設計 |
| `settings_old.py` | 傳統視窗介面 | Tkinter GUI，偏好桌面介面用戶 |
| `config_launcher.py` | 多設定檔管理 | 快速切換不同活動設定 |
| `NonBrowser.py` | 非瀏覽器模式 | 純 HTTP 請求處理 |

### 🔌 瀏覽器擴充套件
- **Maxblockplus** - 廣告阻擋，加速頁面載入
- **Maxbotplus** - DOM 操作輔助，支援 15+ 平台

---

## 🔧 技術實作

### 🛠️ WebDriver 策略
1. **NoDriver** (推薦) - 反偵測能力最強，支援主流平台 ✅
2. **undetected_chromedriver** (維護模式) - 隱蔽性佳，未來將停止更新
3. **Selenium ChromeDriver** (維護模式) - 穩定性高，未來將停止更新

> **📢 策略轉變公告 (2025.10.15)**
> 本專案自 2025.10.15 起採用「NoDriver First」策略，優先開發與維護 NoDriver 版本。
> UC 與 Selenium 已進入維護模式，僅修復嚴重錯誤，不再新增功能。

#### NoDriver 平台支援狀態
- ✅ **完整支援且已測試**: TixCraft, KKTIX, TicketPlus, iBon, KHAM
- ⚠️ **部分支援**: TicketMaster, Cityline
- ❌ **不支援** (僅提供 Chrome 版本): Urbtix, 年代售票, 寬宏售票, HK Ticketing, FamiTicket

### 🧠 OCR 驗證碼辨識
- 使用 [ddddocr](https://github.com/sml2h3/ddddocr) 進行圖像辨識
- 支援 Canvas 和 Image 兩種驗證碼格式
- 可調整辨識精度與提交策略

### 🎯 智慧選取邏輯
- **關鍵字匹配**：支援正則表達式和模糊匹配
- **排除邏輯**：自動避開輪椅席、視線不良等位置
- **隨機模式**：模擬真人選擇行為

---

## 🎬 教學資源

### 📺 示範影片
- [虛擬主機搶票教學](https://max-everyday.com/2023/11/buy-ticket-by-vm/)

### 📖 平台專用教學
- [拓元/Ticketmaster 教學](https://max-everyday.com/2018/03/tixcraft-bot/)
- [KKTIX 教學](https://max-everyday.com/2018/12/kktix-bot/)
- [Cityline 教學](https://max-everyday.com/2019/03/cityline-bot/)
- [Urbtix 教學](https://max-everyday.com/2019/02/urbtix-bot/)
- [HKTicketing 教學](https://max-everyday.com/2023/01/hkticketing-bot/)

---

## ❓ 常見問題

### 🐛 安裝問題
**Q: ARM CPU (M1/M2/M3) 安裝 ddddocr 時顯示錯誤？**
A: 參考 [ddddocr MacOS ARM 安裝指南](FAQ/ddddocr_macos_arm_installation.md) 解決方案

**Q: fatal: destination path already exists？**  
A: 目錄已存在，直接 `cd tixcraft_bot` 即可

**Q: Out of Memory 錯誤？**  
A: 增加 Windows 虛擬記憶體或減少瀏覽器數量

### ⚡ 效能最佳化
- 使用原始碼執行比執行檔效率更高
- 關閉不必要的瀏覽器擴充套件
- 調整自動重載間隔避免過度佔用資源

---

## 🤝 貢獻與支援

### 💡 技術實作參考
- [擴充套件隱私權政策](https://github.com/bouob/tickets_hunter/blob/main/README_EXTENSION.md)

---

## 📄 授權條款

本專案採用 GNU GPL 授權，遵循開源精神。使用時請遵守：
- 保持開源授權條款
- 標註原作者資訊  
- 不得用於商業牟利

**祝您搶票成功！** 🎉

---

*最後更新：2025.10.17 | 由 Claude Code AI 輔助維護*