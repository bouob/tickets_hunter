# 🤝 Contributing to Tickets Hunter

歡迎參與 Tickets Hunter 專案！我們歡迎社群貢獻，讓這個搶票系統變得更好。

---

## 📋 貢獻指南

### 🎯 專案目標

Tickets Hunter 是一個開放原始碼的多平台搶票自動化系統，旨在：
- 提供公平的搶票環境，對抗黃牛
- 支援多個票務平台的自動化操作
- 維持高度的安全性和隱蔽性
- 持續改善使用者體驗

### 🚨 重要提醒

**法律合規性：**
- 本專案僅供教育和研究用途
- 使用者需自行承擔法律責任
- 禁止用於商業牟利或違法用途
- 遵守各票務平台的使用條款

---

## 🎯 開發策略：NoDriver First (2025.10.13 起)

本專案自 2025.10.13 起採用「**NoDriver First**」開發策略：

- ✅ **優先開發**: NoDriver 版本（反偵測能力最強，記憶體佔用小）
- ⚠️ **維護模式**: Chrome Driver (UC/Selenium) 僅修復嚴重錯誤，不接受新功能
- 🎫 **已完成平台**: TixCraft、KKTIX、TicketPlus、iBon、KHAM

### 技術選擇

| 驅動類型 | 狀態 | 適用場景 |
|---------|------|---------|
| **nodriver** | 推薦 | 新功能開發、反偵測需求 |
| **undetected_chromedriver** | 維護 | 現有功能維護 |
| **selenium** | 維護 | 現有功能維護 |

**給貢獻者的建議**：
- 🆕 開發新功能請優先實作 NoDriver 版本
- 🐛 修復 Bug 時優先處理 NoDriver 版本
- ⚠️ Chrome Driver 版本僅接受嚴重錯誤修復

---

## 🔄 貢獻流程

### 1. 準備工作

#### Fork 專案
```bash
# 1. Fork 此倉庫到您的 GitHub 帳號
# 2. Clone 您的 fork
git clone https://github.com/YOUR_USERNAME/tickets_hunter.git
cd tickets_hunter

# 3. 設定上游倉庫
git remote add upstream https://github.com/bouob/tickets_hunter.git
```

#### 環境設定

**系統需求**：
- **Python 版本**: 3.9-3.10 (NoDriver 需 3.9+，Chrome Driver 支援 3.7+)
- **Chrome 瀏覽器**: 建議 90+ 版本
- **記憶體**: 4GB+ RAM (NoDriver 記憶體佔用較小)

**安裝依賴**：
```bash
# 進入 src 目錄
cd src

# 安裝 Python 依賴
pip install -r requirement.txt
```

**檢查環境**：
```bash
# NoDriver 版本（推薦）
python nodriver_tixcraft.py --help

# Chrome Driver 版本
python chrome_tixcraft.py --help
```

### 2. 開發流程

#### 建立功能分支
```bash
# 同步最新版本
git fetch upstream
git checkout main
git merge upstream/main

# 建立功能分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
# 或
git checkout -b docs/update-documentation
```

#### 開發規範

**分支命名規則：**
- `feature/功能描述` - 新功能
- `fix/問題描述` - Bug 修復
- `docs/文件描述` - 文件更新
- `refactor/重構描述` - 程式碼重構
- `test/測試描述` - 測試相關

**Commit 訊息格式：**
```
<emoji> <type>: <description>

<optional body>
```

**Emoji 參考：**
- ✨ feat: 新功能
- 🐛 fix: Bug 修復
- 📝 docs: 文件更新
- ♻️ refactor: 程式碼重構
- ✅ test: 測試
- 🔧 chore: 維護
- 💄 style: UI/樣式
- ⚡ perf: 效能改善

---

### 程式碼規範

#### 函數命名規則

**NoDriver 版本（推薦優先開發）：**
```python
# 平台主函式
async def nodriver_{platform}_main(tab, config_dict):
    pass

# 平台功能函式
async def nodriver_{platform}_date_auto_select(tab, config_dict):
    pass

# 範例
async def nodriver_tixcraft_main(tab, config_dict):
    pass

async def nodriver_kktix_area_auto_select(tab, config_dict):
    pass
```

**Chrome Driver 版本（維護模式）：**
```python
# 平台主函式
def {platform}_main(driver, config_dict):
    pass

# 平台功能函式
def {platform}_date_auto_select(driver, config_dict):
    pass

# 範例
def tixcraft_main(driver, config_dict):
    pass

def kktix_area_auto_select(driver, config_dict):
    pass
```

#### Emoji 使用規範 ⚠️ 重要

**✅ 允許使用 Emoji 的地方：**
- Git commit 訊息: `✨ feat: 新增 NoDriver KKTIX 支援`
- Markdown 文件 (`*.md`)
- README、CONTRIBUTING 等文件

**❌ 禁止使用 Emoji 的地方：**
- Python 程式碼 (`*.py`)
- JavaScript 程式碼 (`*.js`)
- 程式註解
- `print()` 輸出訊息
- `console.log()` 輸出訊息


**正確範例：**
```python
# 正確
print("[SUCCESS] 操作成功")
print("[INFO] 開始執行")

# 錯誤
print("✅ 操作成功")  # ❌ 禁止
print("[INFO] 開始執行")  # ❌ 禁止
```

#### NoDriver 專屬功能

**暫停機制（NoDriver 專用）：**

NoDriver 版本支援運行時暫停功能，開發時請使用以下函數：

```python
async def nodriver_platform_function(tab, config_dict):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    # 等待時使用暫停版本
    if await sleep_with_pause_check(tab, 0.6, config_dict):
        return False

    # 長迴圈中定期檢查
    for i in range(100):
        if await check_and_handle_pause(config_dict):
            break
        # ... 執行操作
```

**注意事項**：
- ✅ 使用 `check_and_handle_pause(config_dict)` 統一檢查
- ❌ 不要直接檢查暫停檔案 `os.path.exists(CONST_MAXBOT_INT28_FILE)`

#### 錯誤處理規範

**必要的錯誤處理模式：**
```python
# 可控制的除錯輸出
show_debug_message = config_dict["advanced"]["verbose"]

# 標準異常處理
try:
    # 主要邏輯
    result = perform_action()
except Exception as exc:
    if show_debug_message:
        print(f"Error in {function_name}: {exc}")
    return False
```

### 3. 提交 Pull Request

#### PR 準備檢查清單
- [ ] 程式碼遵循專案風格
- [ ] 新增適當的註解和文件
- [ ] 測試您的變更
- [ ] 更新相關文件
- [ ] 檢查沒有敏感資訊

#### PR 模板
```markdown
## 🎯 變更摘要
簡述此 PR 的目的和主要變更

## 🔧 技術細節
- 修改的檔案：
- 主要變更：
- 影響範圍：

## ✅ 測試
- [ ] 本地測試通過
- [ ] 功能正常運作
- [ ] 無破壞性變更

## 📋 檢查清單
- [ ] 程式碼品質良好
- [ ] 文件已更新
- [ ] 無敏感資訊洩露
```

---

## 🎪 平台支援狀態

了解各平台目前的支援情況，可以幫助您決定貢獻方向：

| 平台 | Chrome/Selenium | NoDriver | 實測狀況 | 需要貢獻 |
|------|:---------------:|:--------:|:--------:|:--------:|
| **TixCraft** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | - |
| **KKTIX** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | - |
| **TicketPlus** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | - |
| **iBon** | ❌ 不修復 | ✅ 完全支援 | 🟢 已測試 | - |
| **KHAM** | ✅ 完全支援 | ✅ 完全支援 | 🟢 已測試 | - |
| **Cityline** | ✅ 完全支援 | ⚠️ 部分支援 (40%) | 🟡 待測試 | 🙏 補完功能 |
| **TicketMaster** | ✅ 完全支援 | ⚠️ 部分支援 (11%) | 🟡 待測試 | 🙏 補完功能 |
| **Urbtix** | ✅ 完全支援 | ❌ 未實作 | 🟡 待測試 | 🙏 NoDriver 移植 |
| **年代售票** | ✅ 完全支援 | ✅ 完全支援 | 🟡 待測試 | - |
| **寬宏售票** | ✅ 完全支援 | ❌ 未實作 | 🟡 待測試 | 🙏 NoDriver 移植 |
| **HKTicketing** | ✅ 完全支援 | ❌ 未實作 | 🟡 待測試 | 🙏 NoDriver 移植 |
| **FamiTicket** | ✅ 完全支援 | ❌ 未實作 | 🟡 待測試 | 🙏 NoDriver 移植 |

**圖例說明**：
- ✅ 完全支援 - 功能完整且穩定
- ⚠️ 部分支援 - 核心功能可用，但缺少部分功能
- ❌ 未實作 - 完全沒有實作或不再維護
- 🟢 已測試 - 實測搶票成功
- 🟡 待測試 - 需要實測驗證
- 🙏 需要貢獻 - 歡迎社群貢獻

---

## 🛠️ 開發指南

### 程式碼風格

#### Python 編碼規範
```python
# 函數命名：平台_功能_描述
def tixcraft_auto_select_date():
    pass

# 常數命名：全大寫
CONST_APP_VERSION = "TicketsHunter (2025.09.24)"

# 除錯輸出格式
show_debug_message = config_dict["advanced"]["verbose"]
if show_debug_message:
    print(f"Debug: {function_name} - {message}")

# 異常處理
try:
    # 主要邏輯
    result = perform_action()
except Exception as exc:
    if show_debug_message:
        print(f"Error in {function_name}: {exc}")
    return False
```

#### 檔案結構規範
```
票務平台支援架構：
├── {platform}_main()           # 主控制器
├── {platform}_date_auto_select()    # 日期選擇
├── {platform}_area_auto_select()    # 座位選擇
├── {platform}_assign_ticket_number() # 票數設定
├── {platform}_auto_ocr()       # OCR 處理
├── {platform}_login()          # 登入處理
└── {platform}_ticket_agree()   # 同意條款
```

### 平台支援開發

#### 新增平台支援
1. 研究平台的 DOM 結構
2. 實作核心函數架構
3. 新增 OCR 處理邏輯
4. 測試完整流程
5. 更新文件

#### 現有平台維護
- 監控 DOM 變更
- 更新選擇器
- 改善錯誤處理
- 效能最佳化

---

## 🧪 測試你的改動

開發完成後，務必進行完整測試確保功能正常運作。

### NoDriver 版本測試（推薦）

```bash
# 進入 src 目錄
cd src

# 執行 NoDriver 版本
python nodriver_tixcraft.py --input settings.json
```

### Chrome Driver 版本測試

```bash
# 進入 src 目錄
cd src

# 執行 Chrome Driver 版本
python chrome_tixcraft.py --input settings.json
```

### 測試檢查清單

**基本檢查**：
- [ ] 瀏覽器正常啟動
- [ ] Console 輸出無錯誤訊息
- [ ] 無 emoji 編碼錯誤 (UnicodeEncodeError)
- [ ] 設定檔正確載入

**功能測試**（建議使用測試活動）：
- [ ] 日期選擇功能正常
- [ ] 區域選擇功能正常
- [ ] 票數設定功能正常
- [ ] 驗證碼處理功能正常（如適用）
- [ ] 整體搶票流程完整

**效能測試**：
- [ ] 記憶體使用正常（NoDriver 通常較省）
- [ ] 頁面載入速度正常
- [ ] 無異常延遲或卡頓

### Debug 模式

開啟詳細除錯訊息：

```json
// settings.json
{
  "advanced": {
    "verbose": true
  }
}
```

### 常見測試錯誤

**UnicodeEncodeError (cp950)**：
- 原因：程式碼中使用了 emoji
- 解決：移除所有 emoji，改用純文字 `[SUCCESS]` 等

**ImportError**：
- 原因：缺少依賴套件
- 解決：`pip install -r requirement.txt`

**ChromeDriver 版本不符**：
- 原因：Chrome 瀏覽器與 ChromeDriver 版本不匹配
- 解決：更新 Chrome 瀏覽器或 ChromeDriver

---

## 🐛 問題回報

### Bug 回報模板

```markdown
## 🐛 Bug 描述
清楚描述遇到的問題

## 🔄 重現步驟
1. 執行環境：
2. 操作步驟：
3. 預期結果：
4. 實際結果：

## 💻 環境資訊
- OS:
- Python 版本：
- Chrome 版本：
- 票務平台：

## 📋 補充資訊
- 錯誤訊息：
- 螢幕截圖：
- 相關設定：
```

---

## 🎯 貢獻領域

### 🔥 最優先（NoDriver First 策略）

依據 NoDriver First 開發策略，以下是目前最需要的貢獻方向：

#### Phase 1: 維護已完成平台 ✅
- **TixCraft、KKTIX、TicketPlus、iBon、KHAM** NoDriver 版本
- 🐛 Bug 修復與穩定性改善
- ✅ 實測驗證與問題回報
- 📝 使用文件完善

#### Phase 2: 補完部分實作平台 ⚠️
- **Cityline NoDriver 補完**（目前 40% → 目標 85%）
  - 缺少：區域選擇、票數設定、驗證碼處理等 9 個函式
- **TicketMaster NoDriver 補完**（目前 11% → 目標 80%）
  - 缺少：日期選擇、區域選擇、票數設定等 8 個函式

#### Phase 3: 新平台 NoDriver 移植 🆕
優先度排序：
1. **Urbtix 移植**（香港重要平台，Chrome 版本已有 11 個函式）
2. **寬宏售票移植**（台灣平台，但 NoDriver 版本已完成）
3. **HKTicketing 移植**（香港平台，Chrome 版本已有 20 個函式）
4. **FamiTicket 移植**（全網平台，Chrome 版本已有 10 個函式）

### 一般優先度

- 📚 文件完善和翻譯
- 🧪 測試覆蓋率提升
- 🚀 效能和穩定性改善
- 💄 網頁介面美化

### ⚠️ 維護模式（優先度低）

**Chrome Driver (UC/Selenium) 版本**：
- ❌ 不接受新功能開發
- ✅ 僅接受嚴重錯誤修復
- 📌 維護現有功能穩定性

### 技術領域

- **前端開發**：網頁設定介面改善
- **後端開發**：NoDriver 核心邏輯最佳化
- **自動化測試**：CI/CD 流程建立
- **安全性**：反偵測機制強化
- **文件撰寫**：使用指南和貢獻文件

---

## 📞 聯繫方式

### 取得協助
- **GitHub Issues**：回報 Bug 和功能請求
- **GitHub Discussions**：一般討論和問題解答
- **Pull Request**：程式碼審查和討論

### 社群準則
- 🤝 友善和尊重的溝通
- 📚 樂於分享知識和經驗
- 🎯 專注於技術改善
- ⚖️ 遵守法律和道德規範

---

## 🎉 致謝

感謝每一位貢獻者讓 Tickets Hunter 變得更好！

### 貢獻者名單
- **@bouob** - 專案維護者
- **Claude Code AI** - 技術支援

### 特別感謝
- **max32002/tixcraft_bot** - 原始專案啟發
- **所有 issue 回報者和測試者**
- **開源社群的支持**

---

*最後更新：2025.10.13 | NoDriver First 策略更新 | 由 Claude Code AI 輔助維護*