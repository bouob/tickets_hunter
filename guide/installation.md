<!--
文件說明：協助使用者完成 Tickets Hunter 執行檔版本的安裝與首次執行
分類：Getting Started (level: 1)
目標受眾：初學者
最後更新：2025-11-12
-->

# 安裝與首次執行指南

本指南將協助您完成 Tickets Hunter 執行檔版本的安裝與首次執行。

---

## ⚠️ 重要更新 (2025.10.30)

**關鍵字分隔符號已變更：逗號 (`,`) → 分號 (`;`)**

從 2025.10.30 版本開始，多組關鍵字的分隔符號已從「逗號」改為「分號」，以避免與常見數字格式（如票價 3,280）混淆。

**範例：**
- ❌ 舊格式：`11/16,11/17,11/18`
- ✅ 新格式：`11/16;11/17;11/18`

**注意：**
- 千位分隔符號的逗號不受影響（如 `3,280` 仍然有效）
- 空格仍然表示 AND 邏輯（如 `週六 19:30` 表示同時包含「週六」**且**「19:30」）

詳細說明請參閱 [關鍵字與回退機制](keyword-mechanism.md)。

---

## 📥 步驟 1：下載 Release ZIP

### 前往 GitHub Releases 頁面

1. 開啟瀏覽器，前往 [Tickets Hunter Releases 頁面](https://github.com/bouob/tickets_hunter/releases)
2. 找到最新版本（例如：`v2025.11.03`）
3. 下載 ZIP 檔案：`tickets_hunter_vXXXX.XX.XX.zip`

**檔案大小**：約 150-250 MB（包含所有必要的依賴套件）

---

## 📂 步驟 2：解壓縮

1. 將下載的 ZIP 檔案解壓縮到任意目錄
   - 建議放在容易找到的位置（例如：`D:\tickets_hunter\`）
   - **不要**放在需要管理員權限的目錄（如 `C:\Program Files\`）

2. 解壓縮後的資料夾結構如下：

```
tickets_hunter/
├── nodriver_tixcraft.exe       # NoDriver 搶票引擎
├── chrome_tixcraft.exe          # Chrome 搶票引擎
├── settings.exe                 # 設定編輯器（主要入口）
│
├── _internal/                   # 依賴函式庫（請勿刪除！）
├── webdriver/                   # WebDriver 與擴充套件
│   ├── Maxbotplus_1.0.0/
│   └── Maxblockplus_1.0.0/
│
├── assets/                      # 資源檔案
│   ├── icons/                   # 圖示
│   └── sounds/                  # 音效檔案
│
├── www/                         # 網頁設定介面
│   ├── settings.html
│   ├── settings.js
│   └── dist/
│
├── settings.json                # 設定檔範本
├── README_Release.txt           # 使用說明
└── CHANGELOG.md                 # 版本更新記錄
```

**⚠️ 重要提醒**：
- **請勿刪除 `_internal/` 資料夾**，它包含所有執行檔共用的依賴函式庫
- **請勿移動執行檔**到其他目錄，否則會找不到依賴檔案

---

## 🚀 步驟 3：首次執行

### 3.1 開啟設定介面

1. 雙擊執行 `settings.exe`
2. 瀏覽器會自動開啟設定頁面（預設為 `http://127.0.0.1:16888`）

**如果遇到 Windows Defender 提示**，請參閱 [Windows Defender 處理方式](#windows-defender-處理)。

### 3.2 設定介面說明

設定介面分為多個頁籤：

#### 📋 基本設定頁籤
- **網址（homepage）**：票務平台的活動網址
  - 範例：`https://tixcraft.com/activity/game/XXXX`
- **票數（ticket_number）**：想買的票數（1-4）
- **日期關鍵字**：想選擇的日期（例如：`11/16;11/17;週六`）
- **區域關鍵字**：想選擇的區域（例如：`搖滾A;VIP;1F`）
- **日期自動遞補**：當找不到日期關鍵字時的行為（開啟/關閉）
- **區域自動遞補**：當找不到區域關鍵字時的行為（開啟/關閉）

#### ⚙️ 進階設定頁籤
- **WebDriver類別（webdriver_type）**：選擇搶票引擎
  - **nodriver**：推薦，反偵測能力最強（預設）
  - **undetected_chrome**：傳統方案，穩定性高
- **驗證碼設定**：OCR 自動辨識選項
- **優惠代碼**：特定活動需要的會員序號或優惠代碼（KKTIX、TicketPlus）⭐ 新增功能
- **音效設定**：成功時播放提示音
- **瀏覽器選項**：無頭模式、擴充套件等

### 3.3 填寫基本設定

在設定介面填寫以下資訊即可開始搶票。

---

#### ✅ 必填欄位

##### 1️⃣ 售票網站（homepage）

**說明**：票務平台的活動網址

**範例**：
```
https://tixcraft.com/activity/game/25_alin
https://kktix.com/events/example-event
https://ticket.ibon.com.tw/ActivityInfo/Details/25EXAMPLE
```

**支援平台**：TixCraft 拓元、KKTIX、TicketPlus 遠大、iBon、KHAM 寬宏、年代售票、FamiTicket 全家、FANSI GO、Cityline、Ticketmaster 等

**提示**：直接複製活動頁面網址即可

---

##### 2️⃣ 門票張數（ticket_number）

**說明**：想買的票數

**可選值**：1-4 張（依活動規定）

**注意**：請遵守活動規定，超過限制可能導致購票失敗

---

##### 3️⃣ 日期關鍵字

填寫想選擇的日期文字，例如：`11/16;11/17;週六`

| 語法 | 說明 | 範例 |
|------|------|------|
| 分號 `;` | OR 邏輯（任一命中） | `11/16;11/17` |
| 空格 | AND 邏輯（同時包含） | `11/16 上午` |

---

##### 4️⃣ 區域關鍵字

填寫想選擇的區域文字，例如：`搖滾A;VIP;3,280`

| 語法 | 說明 | 範例 |
|------|------|------|
| 分號 `;` | OR 邏輯（任一命中） | `搖滾A;VIP` |
| 空格 | AND 邏輯（同時包含） | `搖滾A 3280` |

---

##### 5️⃣ 排除關鍵字

排除不想選的區域：`輪椅;身障;陪同`

---

##### 6️⃣ 自動遞補設定

| 設定 | 關閉（嚴格模式） | 開啟（自動遞補） |
|------|------------------|------------------|
| **行為** | 關鍵字失敗時暫停等待 | 關鍵字失敗時自動選擇 |
| **適用** | 只要特定日期/區域 | 任何票都可以 |

---

> **📖 完整關鍵字教學** → [關鍵字與回退機制](keyword-mechanism.md)
>
> 包含：AND/OR 邏輯詳解、回退機制、設定範例

### 3.4 啟動搶票

1. 確認設定無誤後，點擊頁面底部的 **「搶票」** 按鈕
2. 系統會自動根據您的 `webdriver_type` 設定啟動對應的搶票引擎：
   - **nodriver** → 自動啟動 `nodriver_tixcraft.exe`
   - **undetected_chrome** → 自動啟動 `chrome_tixcraft.exe`
3. 搶票程式會顯示執行進度與 log
4. 成功進入購票頁面時會發出音效提示（如有設定）

**⚠️ 注意**：
- 搶票引擎會自動處理日期選擇、區域選擇、驗證碼填寫等步驟
- 最後一步（填寫個人資料、完成付款）需要您手動操作

---

## 🛡️ Windows Defender 處理

首次執行 `settings.exe` 時，Windows Defender SmartScreen 可能會顯示「威脅已阻止」提示。這是因為執行檔沒有數位簽章（需要昂貴的簽章憑證），並非真的病毒。

### 方法一：允許執行（推薦）

1. 點擊 **「詳細資訊」**
2. 點擊 **「仍要執行」**
3. 執行檔會啟動

### 方法二：加入排除清單（一勞永逸）

1. 開啟 Windows 安全性（Windows Security）
2. 點擊 **「病毒與威脅防護」**
3. 點擊 **「管理設定」**
4. 滾動到 **「排除項目」** → 點擊 **「新增或移除排除項目」**
5. 點擊 **「新增排除項目」** → 選擇 **「資料夾」**
6. 選擇您的 `tickets_hunter/` 資料夾
7. 完成！之後不會再出現提示

---

## 🌐 防火牆提示處理

首次執行 `settings.exe` 時，Windows 防火牆可能會詢問是否允許網路存取。

**請點擊「允許存取」**，因為：
- `settings.exe` 需要啟動網頁伺服器（預設 Port 16888）
- 搶票引擎需要連線到票務網站

**⚠️ 注意**：網頁伺服器僅監聽本機（127.0.0.1），不會對外開放，安全無虞。

---

## 🔽 NoDriver 首次自動下載 Chrome

如果您選擇 **NoDriver** 搶票引擎（推薦），首次執行時會自動下載獨立的 Chrome 瀏覽器。

### 下載過程

1. 首次執行 `nodriver_tixcraft.exe` 時，會顯示：
   ```
   Downloading Chrome browser... (約 100-200 MB)
   ```

2. 下載位置：
   - Windows：`C:\Users\<您的使用者名稱>\AppData\Local\nodriver\`
   - 不會影響您現有的 Chrome 瀏覽器

3. 下載時間：約 2-5 分鐘（視網路速度）

4. 下載完成後，後續執行會直接使用已下載的 Chrome，速度變快

**⚠️ 注意**：
- 首次執行請保持網路暢通
- 下載完成前請勿關閉程式
- 如果下載失敗，請重新執行，程式會自動重試

---

## ❓ 常見問題

### Q1: 執行檔點擊後沒有反應？

**可能原因**：
- `_internal/` 資料夾被刪除或移動
- 防毒軟體阻擋執行
- 缺少系統權限

**解決方案**：
1. 確認 `_internal/` 資料夾與執行檔在同一目錄
2. 檢查防毒軟體是否阻擋（加入排除清單）
3. 使用「以系統管理員身分執行」

### Q2: 出現「找不到 python310.dll」錯誤？

**原因**：`_internal/` 資料夾被刪除或移動

**解決方案**：重新解壓縮 ZIP 檔案

### Q3: NoDriver 版本首次執行很慢？

**原因**：正常現象，首次執行會自動下載 Chrome 瀏覽器（約 100-200MB）

**解決方案**：耐心等待下載完成，後續執行會變快

### Q4: Chrome 版本出現「chromedriver.exe 不相容」錯誤？

**原因**：系統 Chrome 版本與 chromedriver.exe 版本不符

**解決方案**：
1. 前往 [ChromeDriver 下載頁面](https://chromedriver.chromium.org/)
2. 下載與您的 Chrome 版本相符的 chromedriver.exe
3. 放到 `webdriver/` 目錄中，覆蓋舊檔案

**建議**：改用 NoDriver 引擎，無需手動管理 chromedriver

### Q5: 設定介面無法開啟（瀏覽器沒有自動開啟）？

**可能原因**：
- Port 16888 被其他程式佔用或被系統阻擋（Hyper-V、WSL、Docker 等）
- 防火牆阻擋

**解決方案**：
1. 手動開啟瀏覽器，輸入 `http://127.0.0.1:16888`
2. 如果仍無法開啟，**修改 Port 號碼**：
   - 先手動編輯 `settings.json`，在 `advanced` 區塊加入 `"server_port": 16889`
   - 重新啟動設定介面
   - 或參考[設定介面 Port 說明](settings-guide.md#設定介面-portserver_port-v202512-新增)
3. 檢查防火牆設定
4. 重新執行 `settings.exe`

**檢查 Port 是否被系統保留**（Windows CMD）：
```cmd
netsh interface ipv4 show excludedportrange protocol=tcp
```

### Q6: 可以在不同電腦上使用嗎？

**可以！** 直接複製整個 `tickets_hunter/` 資料夾到其他電腦即可。

**注意**：
- Windows 版本限定 Windows 10/11（64-bit）
- 首次執行 NoDriver 時仍需下載 Chrome

### Q7: 如何更新到新版本？

**步驟**：
1. 從 [GitHub Releases](https://github.com/bouob/tickets_hunter/releases) 下載最新 ZIP
2. 解壓縮到新資料夾（或覆蓋舊版本）
3. 複製舊版的 `settings.json` 到新版資料夾（保留設定）
4. 完成！

---

## 📚 進階參考

如果想深入理解搶票邏輯，請參閱：

- **[關鍵字機制詳解](keyword-mechanism.md)** - 深入理解關鍵字匹配、AND/OR 邏輯、自動回退策略
- **[詳細設定說明](settings-guide.md)** - settings.json 完整欄位參考（進階使用者）

---

## 💬 需要協助？

遇到問題或有疑問？歡迎到社群尋求協助：

- 🙋 **[Q&A 問題解答](https://github.com/bouob/tickets_hunter/discussions/categories/q-a)** - 使用疑問先來這裡問
- 💬 **[一般討論](https://github.com/bouob/tickets_hunter/discussions/categories/general)** - 分享使用經驗
- 🐛 **[回報 Bug](https://github.com/bouob/tickets_hunter/issues/new?template=bug_report.md)** - 確定是程式錯誤請開 Issue
- 💡 **[功能建議](https://github.com/bouob/tickets_hunter/discussions/categories/ideas)** - 想要新功能到這裡提案

---

**安裝完成！祝您搶票成功！** 🎉

*最後更新：2025-11-12*
