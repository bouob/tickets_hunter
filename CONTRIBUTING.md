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
```bash
# 安裝 Python 依賴
pip install -r requirement.txt

# 檢查環境
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

### 優先需求
- 🆕 新平台支援 (如：大麥網、永樂票務)
- 🔧 現有平台功能改善
- 📚 文件完善和翻譯
- 🧪 測試覆蓋率提升
- 🚀 效能和穩定性改善

### 技術領域
- **前端開發**：網頁介面美化
- **後端開發**：核心邊輯最佳化
- **自動化測試**：CI/CD 流程建立
- **安全性**：反偵測機制強化
- **文件撰寫**：使用指南和 API 文件

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

*最後更新：2025.09.24 | 由 Claude Code AI 輔助撰寫*