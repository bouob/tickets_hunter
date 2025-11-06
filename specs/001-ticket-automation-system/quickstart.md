# 快速入門指南

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：提供新用戶和維護者快速上手 Tickets Hunter 系統的完整指南。

---

## 概述

本文件提供 Tickets Hunter 多平台自動化搶票系統的快速入門指南。無論您是：
- **新用戶**：想要使用系統搶票
- **開發者**：想要理解系統架構
- **貢獻者**：想要新增平台或功能

都可以從這裡開始。

**預計時間**：15-30 分鐘完成基本設定和第一次執行。

---

## 前置需求

### 系統需求

**NoDriver 版本（推薦）**：
- **作業系統**：Windows 10+、macOS 10.15+、Linux（Ubuntu 20.04+）
- **Python**：3.9 或更高版本
- **記憶體**：至少 4GB RAM
- **瀏覽器**：Chrome 或 Chromium 90+

**Chrome Driver 版本（舊系統）**：
- **作業系統**：同上
- **Python**：3.7 或更高版本
- **記憶體**：至少 4GB RAM

### 檢查 Python 版本

```bash
python --version
# 或
python3 --version
```

**期望輸出**：`Python 3.9.x` 或更高（NoDriver）/ `Python 3.7.x` 或更高（Chrome Driver）

---

## 步驟 1：安裝依賴

### 1.1 克隆專案（如果尚未完成）

```bash
cd D:/Desktop/MaxBot搶票機器人
cd tickets_hunter
```

### 1.2 安裝 Python 套件

**NoDriver 版本**：
```bash
pip install -r requirements_nodriver.txt
```

**Chrome Driver 版本**：
```bash
pip install -r requirements.txt
```

**安裝項目**：
- `nodriver`（NoDriver 版本）
- `undetected-chromedriver`（Chrome Driver 版本）
- `ddddocr`：驗證碼辨識
- `beautifulsoup4`：HTML 解析
- `requests`：HTTP 請求

### 1.3 驗證安裝

```bash
python -c "import nodriver; print('NoDriver 安裝成功')"
# 或
python -c "import undetected_chromedriver; print('UC 安裝成功')"
```

---

## 步驟 2：創建配置檔案

### 2.1 複製範例配置

```bash
cp src/settings_example.json src/settings.json
```

### 2.2 編輯配置檔案

使用文字編輯器開啟 `src/settings.json`：

```bash
# Windows
notepad src/settings.json

# macOS
open -a TextEdit src/settings.json

# Linux
nano src/settings.json
```

### 2.3 基本配置範例（TixCraft）

```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_YOUR_EVENT_ID",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/15;10/16",
    "mode": "from top to bottom"
  },

  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP區;搖滾區A",
    "mode": "from top to bottom"
  },

  "ticket_form_data": {
    "name": "您的姓名",
    "email": "your_email@example.com",
    "phone": "0912345678"
  },

  "ocr_captcha": {
    "enable": true,
    "beta": false,
    "force_submit": true,
    "retry": 3
  },

  "advanced": {
    "verbose": true,
    "headless": false,
    "auto_reload_page_interval": 1.5,
    "tixcraft_sid": ""
  }
}
```

### 2.4 必需修改的欄位

✅ **必須修改**：
1. `homepage`：改為實際的活動 URL
2. `ticket_number`：改為想要的票數
3. `date_keyword`：改為目標日期關鍵字
4. `area_keyword`：改為目標區域關鍵字
5. `ticket_form_data`：改為您的真實資訊

---

## 步驟 3：取得認證憑證（重要）

### TixCraft（Cookie 注入）

#### 3.1 登入 TixCraft

在瀏覽器中登入 https://tixcraft.com

#### 3.2 開啟開發者工具

- **Windows/Linux**：按 `F12` 或 `Ctrl + Shift + I`
- **macOS**：按 `Cmd + Option + I`

#### 3.3 取得 Session Cookie

1. 切換到 **Application** 標籤（或 **Storage** 在 Firefox）
2. 左側選單：**Cookies** → `https://tixcraft.com`
3. 找到 `tixcraft_sid` 這一行
4. 複製 **Value** 欄位的值（通常是一串英數字）

#### 3.4 填入配置檔案

將複製的值貼到 `settings.json` 的 `advanced.tixcraft_sid` 欄位：

```json
{
  "advanced": {
    "tixcraft_sid": "abc123def456ghi789jkl012mno345pqr678"
  }
}
```

### KKTIX（帳號密碼）

直接在配置檔案中填入帳號密碼：

```json
{
  "advanced": {
    "kktix_account": "your_email@example.com",
    "kktix_password": "your_password"
  }
}
```

⚠️ **安全提醒**：密碼明文儲存，請確保檔案權限正確。

---

## 步驟 4：執行系統

### 4.1 NoDriver 版本（推薦）

```bash
cd D:/Desktop/MaxBot搶票機器人/tickets_hunter
python nodriver_tixcraft.py --input src/settings.json
```

### 4.2 Chrome Driver 版本

```bash
python chrome_tixcraft.py --input src/settings.json
```

### 4.3 期望行為

**初始化階段**：
```
[INIT] 正在初始化瀏覽器...
[INIT] 使用 NoDriver WebDriver
[AUTH] 注入 session cookie
[AUTH] Cookie 注入成功
```

**頁面監控階段**：
```
[RELOAD] 正在重載頁面... (1/10)
[RELOAD] 購票按鈕尚未出現，等待 1.5 秒
[RELOAD] 正在重載頁面... (2/10)
```

**開賣後**：
```
[RELOAD] 購票按鈕已出現
[DATE] 找到 3 個可用日期
[DATE] 使用關鍵字 '10/15' 匹配到：2025/10/15 (日) 19:30
[DATE] 點擊日期成功
[AREA] 找到 5 個可用區域
[AREA] 使用關鍵字 'VIP' 匹配到：VIP區 $3000
[AREA] 選擇區域成功
[CAPTCHA] OCR 辨識結果：AB12
[SUBMIT] 正在送出訂單...
[SUCCESS] 訂單已送出，請完成付款
```

---

## 步驟 5：監控和手動介入

### 5.1 暫停自動化（NoDriver 專用）

如果需要暫停並手動介入：

#### Windows（PowerShell）
```powershell
New-Item -Path "MAXBOT_INT28_IDLE.txt" -ItemType File
```

#### Git Bash / macOS / Linux
```bash
touch MAXBOT_INT28_IDLE.txt
```

**結果**：
```
[PAUSED] 自動化已暫停，刪除檔案以繼續...
```

此時您可以手動操作瀏覽器。

#### 繼續自動化

刪除暫停檔案：

```bash
# Windows
del MAXBOT_INT28_IDLE.txt

# macOS / Linux
rm MAXBOT_INT28_IDLE.txt
```

**結果**：
```
[RESUMED] 繼續執行
```

---

## 常見問題

### Q1：無法安裝 ddddocr（macOS ARM）

**問題**：macOS ARM（M1/M2/M3）無法直接安裝 ddddocr。

**解決方案**：

參考 `docs/05-troubleshooting/ddddocr_macos_arm_installation.md` 完整指南，簡要步驟：

1. 安裝 Rosetta 2：
   ```bash
   /usr/sbin/softwareupdate --install-rosetta --agree-to-license
   ```

2. 創建 x86 虛擬環境：
   ```bash
   arch -x86_64 python3 -m venv venv_x86
   source venv_x86/bin/activate
   ```

3. 安裝依賴：
   ```bash
   arch -x86_64 pip install ddddocr
   ```

---

### Q2：找不到元素（ElementNotFoundError）

**可能原因**：
1. 平台網頁結構變更
2. 頁面載入不完全
3. 選擇器錯誤

**解決方案**：

1. **增加等待時間**：
   ```json
   {
     "advanced": {
       "auto_reload_page_interval": 2.0
     }
   }
   ```

2. **檢查頁面結構**：
   - 開啟瀏覽器開發者工具
   - 檢查元素選擇器是否正確
   - 參考 `docs/02-development/structure.md` 查看函式實作

3. **查看疑難排解文件**：
   - `docs/05-troubleshooting/README.md`

---

### Q3：驗證碼辨識失敗

**症狀**：
```
[CAPTCHA] OCR 辨識結果：（空白或錯誤）
[CAPTCHA] OCR 辨識失敗，重試... (1/3)
```

**解決方案**：

**方案 1**：使用 Beta 模型（更準確但較慢）

```json
{
  "ocr_captcha": {
    "enable": true,
    "beta": true,
    "retry": 5
  }
}
```

**方案 2**：啟用 force_submit（依賴運氣）

```json
{
  "ocr_captcha": {
    "force_submit": true
  }
}
```

**方案 3**：手動輸入

1. 暫停自動化（建立 `MAXBOT_INT28_IDLE.txt`）
2. 手動輸入驗證碼
3. 繼續自動化（刪除暫停檔案）

---

### Q4：ibon 座位選擇失敗

**症狀**：無法點擊座位圖上的座位。

**解決方案**：

1. **確認使用 NoDriver**：
   ```json
   {
     "webdriver_type": "nodriver"
   }
   ```

2. **啟用相鄰座位**：
   ```json
   {
     "seat_auto_select": {
       "enable": true,
       "adjacent_seat": true
     }
   }
   ```

3. **參考疑難排解**：
   - `docs/05-troubleshooting/ibon_nodriver_fixes_2025-10-03.md`

---

### Q5：頁面重載次數過多（過熱保護）

**症狀**：
```
[RELOAD] 過熱保護：冷卻 60 秒
```

**原因**：連續重載超過 `auto_reload_overheat_count` 次。

**調整方案**：

**方案 1**：增加過熱閾值

```json
{
  "advanced": {
    "auto_reload_overheat_count": 20
  }
}
```

**方案 2**：減少冷卻時間

```json
{
  "advanced": {
    "auto_reload_overheat_cd": 30
  }
}
```

---

### Q6：cp950 編碼錯誤（Windows）

**症狀**：
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 10: character maps to <undefined>
```

**原因**：程式碼中使用了 emoji，Windows 預設編碼（cp950）不支援。

**解決方案**：

1. **檢查程式碼**：確保所有 `.py` 檔案中的 print() 和註解不含 emoji
2. **修改控制台編碼**：
   ```bash
   chcp 65001
   ```

3. **參考規範**：`docs/02-development/development_guide.md` - Emoji 使用規範

---

## 進階使用

### 多活動管理

為不同活動創建獨立配置檔案：

```bash
src/
├── settings_tixcraft_taylorswift_1015.json
├── settings_kktix_concert_1020.json
└── settings_ibon_musical_1025.json
```

**執行指定配置**：

```bash
python nodriver_tixcraft.py --input src/settings_tixcraft_taylorswift_1015.json
```

---

### 無頭模式（伺服器環境）

在伺服器上執行（無圖形介面）：

```json
{
  "advanced": {
    "headless": true
  },
  "browser_args": [
    "--disable-dev-shm-usage",
    "--no-sandbox"
  ]
}
```

⚠️ **注意**：無頭模式可能增加偵測風險，建議僅在必要時使用。

---

### 測試模式

在非開賣時間測試配置：

1. **減少重載次數**：
   ```json
   {
     "advanced": {
       "auto_reload_overheat_count": 3,
       "auto_reload_overheat_cd": 10
     }
   }
   ```

2. **啟用詳細日誌**：
   ```json
   {
     "advanced": {
       "verbose": true
     }
   }
   ```

3. **使用測試活動 URL**：找一個已售罄或過期的活動進行測試。

---

## 下一步學習

### 文件路徑

完成快速入門後，建議依序閱讀以下文件以深入理解系統：

#### 1. 架構理解

- **`specs/001-ticket-automation-system/spec.md`**
  - 功能需求完整定義
  - 7 個用戶故事
  - 63 個功能需求

- **`specs/001-ticket-automation-system/research.md`**
  - 10 個重要技術決策
  - 為什麼選擇 NoDriver
  - 三層回退策略原理

- **`specs/001-ticket-automation-system/data-model.md`**
  - 資料結構完整說明
  - config_dict 結構
  - 資料流圖

#### 2. 開發參考

- **`docs/02-development/ticket_automation_standard.md`**（必讀）
  - 12 階段購票流程標準
  - 每個階段的函式分解
  - 配置欄位映射

- **`docs/02-development/structure.md`**
  - 所有平台函式索引
  - 函式行號查詢
  - 平台完整度評分

- **`docs/03-api-reference/nodriver_api_guide.md`**（NoDriver 用戶必讀）
  - NoDriver API 完整指南
  - tab.evaluate() 最佳實踐
  - 常見錯誤處理

#### 3. 疑難排解

- **`docs/05-troubleshooting/README.md`**
  - 問題索引
  - 按平台、技術分類
  - 修復記錄連結

- **`docs/04-testing-debugging/debugging_methodology.md`**
  - 除錯方法論
  - 如何定位問題
  - 工具使用

#### 4. 介面契約（貢獻者）

如果您想新增平台或貢獻程式碼：

- **`specs/001-ticket-automation-system/contracts/platform-interface.md`**
  - 平台轉接器標準介面
  - 12 階段函式契約
  - 命名慣例

- **`specs/001-ticket-automation-system/contracts/util-interface.md`**
  - 共享工具函式
  - 如何使用 util.py

- **`specs/001-ticket-automation-system/contracts/config-schema.md`**
  - 配置 schema 完整定義
  - 新增配置欄位指南

---

## 平台特定快速入門

### TixCraft

**特點**：
- Cookie 注入認證
- 標準驗證碼（ddddocr 支援良好）
- 下拉選單式區域選擇

**最小配置**：
```json
{
  "homepage": "https://tixcraft.com/activity/detail/23_EVENT",
  "ticket_number": 2,
  "date_auto_select": {"date_keyword": "10/15"},
  "area_auto_select": {"area_keyword": "VIP"},
  "ocr_captcha": {"enable": true},
  "advanced": {"tixcraft_sid": "YOUR_SID"}
}
```

**參考文件**：
- `docs/02-development/structure.md` - TixCraft 函式索引

---

### KKTIX

**特點**：
- 帳號密碼登入
- 展開式日期選擇
- 標準驗證碼

**最小配置**：
```json
{
  "homepage": "https://kktix.com/events/concert",
  "ticket_number": 2,
  "date_auto_select": {"date_keyword": "10/15"},
  "ocr_captcha": {"enable": true},
  "advanced": {
    "kktix_account": "your@email.com",
    "kktix_password": "your_password"
  }
}
```

---

### ibon

**特點**：
- Cookie 注入認證
- Shadow DOM（複雜）
- 互動式座位圖
- 無驗證碼

**最小配置**：
```json
{
  "homepage": "https://ticket.ibon.com.tw/ActivityInfo/Details/24012345",
  "webdriver_type": "nodriver",
  "ticket_number": 2,
  "date_auto_select": {"date_keyword": "2025/10/15"},
  "seat_auto_select": {
    "enable": true,
    "adjacent_seat": true
  },
  "advanced": {"ibon_ibonqware": "YOUR_COOKIE"}
}
```

**重要**：ibon 強烈建議使用 NoDriver，Chrome Driver 對 Shadow DOM 支援較差。

**參考文件**：
- `docs/05-troubleshooting/ibon_nodriver_fixes_2025-10-03.md`
- `docs/05-troubleshooting/ibon_cookie_troubleshooting.md`

---

### KHAM

**特點**：
- Cookie 注入認證
- 標準驗證碼
- 下拉選單式選擇

**最小配置**：
```json
{
  "homepage": "https://kham.com.tw/application/UTK01/UTK0101_.aspx?PRODUCT_ID=EVENT",
  "ticket_number": 2,
  "date_auto_select": {"date_keyword": "10/15"},
  "area_auto_select": {"area_keyword": "VIP"},
  "ocr_captcha": {"enable": true},
  "advanced": {"kham_tk": "YOUR_TK"}
}
```

---

### TicketPlus

**特點**：
- 無需認證（公開售票）
- 展開面板式選擇
- 無驗證碼

**最小配置**：
```json
{
  "homepage": "https://ticketplus.com.tw/activity/EVENT_ID",
  "ticket_number": 2,
  "date_auto_select": {"date_keyword": "10/15"},
  "area_auto_select": {"area_keyword": "VIP"}
}
```

---

## 效能調校

### 針對熱門活動

熱門活動競爭激烈，速度至關重要：

```json
{
  "webdriver_type": "nodriver",
  "ocr_captcha": {
    "beta": false,
    "force_submit": true,
    "retry": 3
  },
  "advanced": {
    "auto_reload_page_interval": 0.5,
    "auto_reload_overheat_count": 20,
    "auto_reload_overheat_cd": 30
  }
}
```

**調整說明**：
- `auto_reload_page_interval: 0.5`：更頻繁重載（風險：可能被偵測）
- `beta: false`：使用快速 OCR 模型
- `force_submit: true`：OCR 失敗仍送出

---

### 針對一般活動

一般活動可以更穩定、更謹慎：

```json
{
  "webdriver_type": "nodriver",
  "ocr_captcha": {
    "beta": true,
    "force_submit": false,
    "retry": 5
  },
  "advanced": {
    "auto_reload_page_interval": 1.5,
    "auto_reload_overheat_count": 10,
    "auto_reload_overheat_cd": 60
  }
}
```

**調整說明**：
- `beta: true`：使用更準確的 OCR 模型
- `force_submit: false`：OCR 失敗時停止，確保正確性
- `retry: 5`：更多重試機會

---

## 安全與隱私

### 配置檔案安全

✅ **建議實踐**：

1. **加入 .gitignore**：
   ```bash
   echo "src/settings.json" >> .gitignore
   ```

2. **設定檔案權限**（Linux/macOS）：
   ```bash
   chmod 600 src/settings.json
   ```

3. **定期更新 cookies**：
   - TixCraft、ibon、KHAM 的 session cookies 會過期
   - 建議每週更新一次

4. **避免分享**：
   - 不要將包含憑證的配置檔案分享或上傳

---

### 反偵測最佳實踐

✅ **推薦設定**：

1. **使用 NoDriver**：
   ```json
   {"webdriver_type": "nodriver"}
   ```

2. **避免過快重載**：
   ```json
   {"auto_reload_page_interval": 1.0}  // 不要低於 0.5
   ```

3. **隨機性**：
   - 使用 `"mode": "random"` 增加不可預測性
   - 避免每次都選擇相同的日期/區域

4. **人工介入**：
   - 熱門活動考慮手動輸入驗證碼（更高成功率）
   - 使用暫停機制在關鍵時刻手動確認

---

## 測試清單

在實際搶票前，建議完成以下測試：

### 基本功能測試

- [ ] Python 環境正確（版本、依賴）
- [ ] 配置檔案語法正確（JSON 有效）
- [ ] 認證憑證有效（session cookies 或帳密）
- [ ] 瀏覽器能正常啟動
- [ ] 頁面能正常載入

### 自動化測試

- [ ] 頁面重載機制運作正常
- [ ] 日期選擇（關鍵字匹配或模式選擇）
- [ ] 區域選擇（關鍵字匹配或模式選擇）
- [ ] 驗證碼辨識（OCR 或手動）
- [ ] 表單填寫正確
- [ ] 暫停機制有效（NoDriver）

### 壓力測試

- [ ] 長時間重載（過熱保護是否觸發）
- [ ] 多次 OCR 重試（是否正確回退）
- [ ] 網路中斷恢復（錯誤處理）

---

## 獲取幫助

### 文件資源

- **專案 README**：`README.md`
- **疑難排解索引**：`docs/05-troubleshooting/README.md`
- **API 指南**：`docs/03-api-reference/nodriver_api_guide.md`

### 社群支援

- **GitHub Issues**：報告錯誤或請求功能
- **討論區**：提問和分享經驗

### 日誌分析

啟用 verbose 模式並儲存日誌：

```bash
python nodriver_tixcraft.py --input src/settings.json > output.log 2>&1
```

分析日誌：
```bash
# 查找錯誤
grep -i "error" output.log

# 查找警告
grep -i "warning" output.log

# 查看特定階段
grep "\[DATE\]" output.log
```

---

## 附錄 A：完整配置範本

### 通用範本（所有平台）

```json
{
  "homepage": "REQUIRED: 活動 URL",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "關鍵字1;關鍵字2",
    "mode": "from top to bottom"
  },

  "area_auto_select": {
    "enable": true,
    "area_keyword": "關鍵字1;關鍵字2",
    "mode": "from top to bottom"
  },

  "seat_auto_select": {
    "enable": true,
    "select_mode": "random",
    "adjacent_seat": true
  },

  "ticket_form_data": {
    "name": "您的姓名",
    "email": "your@email.com",
    "phone": "0912345678",
    "address": "您的地址（選填）"
  },

  "ocr_captcha": {
    "enable": true,
    "beta": false,
    "force_submit": true,
    "retry": 3
  },

  "advanced": {
    "verbose": true,
    "headless": false,
    "auto_reload_page_interval": 1.5,
    "auto_reload_overheat_count": 10,
    "auto_reload_overheat_cd": 60,
    "tixcraft_sid": "",
    "kktix_account": "",
    "kktix_password": "",
    "ibon_ibonqware": "",
    "kham_tk": ""
  },

  "browser_args": [],

  "payment": {
    "method": "credit_card",
    "auto_pay": false
  }
}
```

---

## 附錄 B：命令列參數

### NoDriver 版本

```bash
python nodriver_tixcraft.py --input <config_file> [options]
```

**參數**：
- `--input`：配置檔案路徑（必需）
- `--headless`：強制無頭模式（覆寫配置）
- `--verbose`：強制詳細輸出（覆寫配置）

**範例**：
```bash
python nodriver_tixcraft.py --input src/settings.json --verbose
```

---

## 附錄 C：平台支援狀態

| 平台 | NoDriver | Chrome Driver | 完整度 | 備註 |
|------|----------|---------------|--------|------|
| **TixCraft** | ✅ 完整 | ✅ 完整 | 100% | 參考實作 |
| **KKTIX** | ✅ 完整 | ✅ 完整 | 100% | 展開面板 |
| **TicketPlus** | ✅ 完整 | ✅ 完整 | 100% | 無驗證碼 |
| **ibon** | ✅ 完整 | ⚠️ 部分 | NoDriver: 100%, UC: 80% | Shadow DOM |
| **KHAM** | ✅ 完整 | ✅ 完整 | 100% | 標準流程 |
| **Cityline** | 🔄 開發中 | ✅ 完整 | NoDriver: 60%, UC: 100% | 香港平台 |
| **TicketMaster** | 🔄 開發中 | ✅ 完整 | NoDriver: 40%, UC: 100% | 複雜驗證 |
| **Urbtix** | ⏳ 計劃中 | ✅ 完整 | NoDriver: 0%, UC: 100% | 香港平台 |
| **HKTicketing** | ⏳ 計劃中 | ✅ 完整 | NoDriver: 0%, UC: 100% | 香港平台 |
| **FamiTicket** | ⏳ 計劃中 | ✅ 完整 | NoDriver: 0%, UC: 100% | 台灣平台 |

**圖例**：
- ✅ 完整：所有功能實作完成
- ⚠️ 部分：基本功能可用，部分功能受限
- 🔄 開發中：正在遷移或開發
- ⏳ 計劃中：尚未開始

**建議**：
- 優先使用 NoDriver 版本（TixCraft、KKTIX、TicketPlus、ibon、KHAM）
- 其他平台暫時使用 Chrome Driver 版本

---

## 總結

完成本快速入門後，您應該能夠：

✅ **理解系統架構**：
- 12 階段購票流程
- 三層回退策略
- NoDriver vs Chrome Driver

✅ **配置和執行**：
- 創建 settings.json
- 取得認證憑證
- 執行自動化腳本

✅ **處理常見問題**：
- 元素找不到
- 驗證碼辨識失敗
- 過熱保護觸發

✅ **下一步學習**：
- 深入文件以理解實作細節
- 貢獻程式碼或新增平台
- 最佳化配置以提高成功率

**祝您搶票成功！**

---

**文件狀態**：快速入門指南完成
**最後更新**：2025-10-16
**版本**：1.0
