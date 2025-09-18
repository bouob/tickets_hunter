# MaxBot 搶票機器人 🎫

**📖 前言**：因原專案 作者 max32002/tixcraft_bot 已停止更新，本專案為後續延伸產品  
**🤖 技術支援**：本專案由 [Claude Code](https://claude.ai/code) 提供 AI 輔助開發與技術支援  
**⚡ 版本**：Tickets Hunter (2025.09.18)  
**🎯 目標**：讓一般民眾與代購黃牛有相同的起跑線，用魔法對抗魔法；各位都能順利搶到大巨蛋！

---

## 📋 專案概述

MaxBot 是一個開放原始碼的多平台搶票自動化系統，支援台灣及海外主要票務網站。採用 Python + Selenium/NoDriver 雙引擎架構，搭配瀏覽器擴充套件，提供完整的自動化購票解決方案。

### 🎪 支援平台
- **🎭 拓元 (TixCraft/Indievox)** - 完整流程自動化
- **🎨 KKTIX** - 活動報名與表單填寫  
- **🎪 Cityline** - 排隊處理與活動預訂
- **🎫 iBon** - 完整購票流程
- **🎵 TicketPlus** - 活動與訂單管理
- **🏟️ Urbtix / HKTicketing** - 港澳地區票務
- **🎤 其他平台** - Ticket.com.tw, Kham, FamiTicket 等

### 🚀 核心特色
- **雙引擎架構** - Selenium (穩定) + NoDriver (反偵測，完成率 44.4% 🚧)
- **OCR 驗證碼辨識** - 整合 ddddocr 自動處理驗證碼
- **智慧化選取** - 日期、區域、票數自動選擇
- **擴充套件輔助** - 廣告阻擋 + DOM 操作加速
- **多設定檔管理** - 不同活動快速切換設定
- **網頁設定介面** - 現代化回應式管理介面

---

## ⚖️ 法律聲明

**🚨 重要提醒**：本軟體僅供教育研究用途，使用者需自行承擔法律責任。

<details>
<summary><code><b>詳細法律聲明</b>（點擊展開）</code></summary>

作者沒有意圖要他人購得的票券進行加價轉售或使用在違法事情上。使用此程式即表示您同意[法律聲明](https://github.com/bouob/tickets_hunter/blob/Main/LEGAL_NOTICE.md)。

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

## 🛡️ 帳號安全指南

<details>
<summary><code><b>如何避免帳號被封鎖</b>（點擊展開）</code></summary>

### 🔍 風險評估
售票系統主要透過伺服器存取記錄判斷機器人行為，過快的操作會導致帳號被封鎖。

### ⏱️ 建議時間設定
- **秒殺活動**：開搶前 2 秒啟動，開搶後 15 秒停止
- **清票模式**：重新整理間隔設為 2 秒以上
- **執行速度**：一般電腦約 10-12 秒完成流程

### 🎛️ 進階技巧
- 使用關鍵字功能讓機器人在特定時間啟動/暫停
- 模擬自然人操作節奏，避免規律性太強
- 分散多個帳號使用，降低單一帳號風險

</details>

---

## 💻 安裝與執行

### 📦 下載方式

**1. 執行檔版本（僅 Windows）**
```
TODO
```

**2. 原始碼版本（推薦，跨平台）**
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
```

### 🔧 環境設定

**系統需求**
- Python 3.7-3.10 (NoDriver 需 3.9+)
- Chrome 瀏覽器
- 4GB+ RAM (多開瀏覽器需更多)

**安裝套件**
```bash
# 基本套件安裝
pip install -r requirement.txt

# NoDriver (推薦最新版本)
python -m pip install git+https://github.com/ultrafunkamsterdam/nodriver
```

### 🚀 執行方式

**1. 網頁設定介面（推薦）**
```bash
python settings.py
# 瀏覽器自動開啟網頁UI：http://127.0.0.1:16888/
```

**2. 多設定檔管理**
```bash
python config_launcher.py
```

---

## 🏗️ 專案架構

### 🎯 核心程式
| 檔案 | 功能 | 特色 |
|------|------|------|
| `chrome_tixcraft.py` | Selenium 主引擎 | 穩定性高，支援所有平台 (11,646 行) |
| `nodriver_tixcraft.py` | NoDriver 引擎 | 反偵測能力強，適合嚴格檢查的平台 (3,039 行) 🚧 |
| `settings.py` | 現代網頁設定介面 | Tornado 伺服器，響應式設計 |
| `settings_old.py` | 傳統視窗介面 | Tkinter GUI，偏好桌面介面用戶 |
| `config_launcher.py` | 多設定檔管理 | 快速切換不同活動設定 |

### 🔧 輔助工具
| 檔案 | 功能 | 大小 |
|------|------|------|
| `util.py` | 核心工具函式庫 | 2,047 行 |
| `NonBrowser.py` | HTTP 請求自動化 | 43 行 |
| `settings.json` | 主設定檔 | JSON 格式 |
| `config_launcher.py` | 多設定檔管理器 | 491 行 |

### 🔌 瀏覽器擴充套件
- **Maxblockplus** - 廣告阻擋，加速頁面載入
- **Maxbotplus** - DOM 操作輔助，支援 15+ 平台

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

## 🔧 技術實作

### 🛠️ WebDriver 策略
1. **undetected_chromedriver** (主要) - 隱蔽性最佳，支援全平台
2. **Selenium ChromeDriver** (備用) - 穩定性最高，支援全平台
3. **NoDriver** (進階) - 反偵測能力最強，**完成率 44.4%** 🚧

#### NoDriver 平台支援狀態
- ✅ **完整支援** (22.2%): TixCraft, KKTIX
- ⚠️ **部分實作** (44.4%): TicketMaster, Cityline, iBon, TicketPlus
- ❌ **開發中** (33.3%): Urbtix, KHAM, HK Ticketing

### 🧠 OCR 驗證碼辨識
- 使用 [ddddocr](https://github.com/sml2h3/ddddocr) 進行圖像辨識
- 支援 Canvas 和 Image 兩種驗證碼格式
- 可調整辨識精度與提交策略

### 🎯 智慧選取邏輯
- **關鍵字匹配**：支援正則表達式和模糊匹配
- **排除邏輯**：自動避開輪椅席、視線不良等位置
- **隨機模式**：模擬真人選擇行為

---

## 📖 使用手冊

### 🎯 基本功能設定

本段說明透過設定介面可以看到的主要功能。

**🌐 網頁版設定介面（推薦）**
```bash
python settings.py
# 瀏覽器自動開啟網頁UI：http://127.0.0.1:16888/
```

**🖥️ 桌面版設定介面**
```bash
python settings_old.py
# 開啟桌面版本UI
```

**⚡ 直接執行主程式**
```bash
# Selenium 版本 (穩定)
python chrome_tixcraft.py

# NoDriver 版本
python nodriver_tixcraft.py

# 指定設定檔
python chrome_tixcraft.py --input settings.json
```

#### 🗓️ 日期自動選擇

控制搶票時自動選取場次日期的功能。

**基本設定**
- **啟用功能**：`date_auto_select.enable` = `true`
- **選擇模式**：`date_auto_select.mode`
  - `random` - 隨機選取匹配的場次
  - `from top to bottom` - 由上而下選取第一個匹配項目
  - `from bottom to top` - 由下而上選取第一個匹配項目
  - `center` - 選取中間位置的匹配項目

**關鍵字篩選**：`date_auto_select.date_keyword`

✅ **OR 邏輯 (任一匹配)**：
```json
"date_keyword": "\"9/11\",\"9/22\",\"3/3\""
```
- 依序嘗試：先找 9/11，找不到再找 9/22，最後找 3/3
- 找到第一個匹配就選取，符合優先順序原則

✅ **AND 邏輯 (全部匹配)**：
```json
"date_keyword": "\"9/11 週末\",\"9/22 平日\""
```
- `9/11 週末`：同時包含 "9/11" 和 "週末" 的場次
- `9/22 平日`：同時包含 "9/22" 和 "平日" 的場次
- 空格分隔的關鍵字需全部匹配

**實用範例**：
```json
// 指定多個日期 (OR 邏輯)
"date_keyword": "\"2024/12/25\",\"2024/12/26\",\"2024/12/31\""

// 日期 + 時段組合 (AND 邏輯)
"date_keyword": "\"12/25 晚上\",\"12/26 下午\",\"12/31 跨年\""

// 關鍵字 + 條件篩選
"date_keyword": "\"演唱會 VIP\",\"音樂會 搖滾區\",\"週末場次\""
```

#### 🎪 區域自動選擇

控制搶票時自動選取座位區域的功能。

**基本設定**
- **啟用功能**：`area_auto_select.enable` = `true`
- **選擇模式**：與日期選擇相同 (`random`, `from top to bottom` 等)

**關鍵字篩選**：`area_auto_select.area_keyword`
```json
// OR 邏輯：搖滾區 或 VIP區 或 前排座位
"area_keyword": "\"搖滾區\",\"VIP\",\"前排\""

// AND 邏輯：搖滾區的前排座位
"area_keyword": "\"搖滾區 前排\",\"VIP 中央\""
```

#### 🚫 排除關鍵字

自動避開不想要的座位類型。
```json
"keyword_exclude": "\"輪椅\",\"身障\",\"身心 障礙\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
```

#### 🎫 票券數量

指定要購買的票券張數。
```json
"ticket_number": 2
```

#### 🔍 OCR 驗證碼設定

自動辨識並填入驗證碼。
```json
"ocr_captcha": {
    "enable": true,        // 啟用 OCR 功能
    "beta": true,          // 使用 beta 版本 (準確度較高)
    "force_submit": true,  // 強制提交 (即使不確定正確性)
    "image_source": "canvas"  // 圖片來源：canvas 或 element
}
```

#### 🌐 瀏覽器設定

**WebDriver 類型**：`webdriver_type`
- `undetected_chromedriver` - 推薦，隱蔽性最佳
- `selenium` - 穩定性最高
- `nodriver` - 反偵測能力最強 (實驗性功能)

**語言設定**：`language`
- `繁體中文`, `简体中文`, `English`, `日本語` 等

#### ⚡ 進階設定

**重新載入設定**
```json
"advanced": {
    "auto_reload_page_interval": 3.0,    // 重新載入間隔 (秒)
    "auto_reload_overheat_count": 4,     // 過熱保護次數
    "auto_reload_overheat_cd": 1.0       // 過熱冷卻時間 (秒)
}
```

**音效提醒**
```json
"play_sound": {
    "ticket": true,                // 搶到票時播放音效
    "order": true,                 // 訂單完成時播放音效
    "filename": "ding-dong.wav"    // 音效檔案名稱
}
```

**暫停/恢復關鍵字**
```json
"idle_keyword": "暫停",      // 遇到此關鍵字時暫停執行
"resume_keyword": "繼續"     // 遇到此關鍵字時恢復執行
```

---

## 🏗️ 專案架構

### 🎯 核心程式
| 檔案 | 功能 | 特色 |
|------|------|------|
| `chrome_tixcraft.py` | Selenium 主引擎 | 穩定性高，支援所有平台 (11,646 行) |
| `nodriver_tixcraft.py` | NoDriver 引擎 | 反偵測能力強，適合嚴格檢查的平台 (3,039 行) 🚧 |
| `settings.py` | 現代網頁設定介面 | Tornado 伺服器，響應式設計 |
| `settings_old.py` | 傳統視窗介面 | Tkinter GUI，偏好桌面介面用戶 |
| `config_launcher.py` | 多設定檔管理 | 快速切換不同活動設定 |

### 🔧 輔助工具
| 檔案 | 功能 | 大小 |
|------|------|------|
| `util.py` | 核心工具函式庫 | 2,047 行 |
| `NonBrowser.py` | HTTP 請求自動化 | 43 行 |
| `settings.json` | 主設定檔 | JSON 格式 |

### 🔌 瀏覽器擴充套件
- **Maxblockplus** - 廣告阻擋，加速頁面載入
- **Maxbotplus** - DOM 操作輔助，支援 15+ 平台

---

## 🔧 技術實作

### 🛠️ WebDriver 策略
1. **undetected_chromedriver** (主要) - 隱蔽性最佳，支援全平台
2. **Selenium ChromeDriver** (備用) - 穩定性最高，支援全平台
3. **NoDriver** (進階) - 反偵測能力最強，**完成率 44.4%** 🚧

#### NoDriver 平台支援狀態
- ✅ **完整支援** (22.2%): TixCraft, KKTIX
- ⚠️ **部分實作** (44.4%): TicketMaster, Cityline, iBon, TicketPlus
- ❌ **開發中** (33.3%): Urbtix, KHAM, HK Ticketing

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
**Q: ARM CPU 在 Step 3 顯示錯誤？**  
A: 參考 [Issue #82](https://github.com/max32002/tixcraft_bot/issues/82#issuecomment-1878986084) 解決方案

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
- [Selenium WebDriver 實作方法](https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/)
- [擴充套件隱私權政策](https://github.com/bouob/tickets_hunter/blob/Main/README_EXTENSION.md)

### 🔄 更新方式
```bash
# 取得最新版本
git pull

# 或重新下載
git clone https://github.com/bouob/tickets_hunter.git
```
---

## 📄 授權條款

本專案採用 GNU GPL 授權，遵循開源精神。使用時請遵守：
- 保持開源授權條款
- 標註原作者資訊  
- 不得用於商業牟利

**祝您搶票成功！** 🎉

---

*最後更新：2025.09.18 | 由 Claude Code AI 輔助維護*