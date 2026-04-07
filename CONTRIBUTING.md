# Contributing to Tickets Hunter

歡迎參與 Tickets Hunter 專案！請閱讀以下指南後再提交你的貢獻。

## 重要提醒

- 本專案僅供教育和研究用途
- 使用者需自行承擔法律責任
- 禁止用於商業牟利或違法用途
- 遵守各票務平台的使用條款

## 開發策略

本專案使用 **zendriver**（nodriver 的活躍 fork，支援 Chrome 145+）作為唯一搶票引擎。平台邏輯已拆分至 `src/platforms/` 目錄，各平台一個模組。

## 貢獻流程

### 1. Fork 與設定

```bash
# Fork 此倉庫後 clone
git clone https://github.com/YOUR_USERNAME/tickets_hunter.git
cd tickets_hunter

# 設定上游倉庫
git remote add upstream https://github.com/bouob/tickets_hunter.git
```

### 2. 建立分支

```bash
# 同步最新版本
git fetch upstream
git checkout main
git merge upstream/main

# 建立功能分支
git checkout -b feature/your-feature-name
```

**分支命名規則：**

| 前綴 | 用途 |
|------|------|
| `feature/` | 新功能 |
| `fix/` | Bug 修復 |
| `docs/` | 文件更新 |
| `refactor/` | 程式碼重構 |

### 3. Commit 規範

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式（**不含 emoji**）：

```
<type>(<scope>): <description>
```

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `docs` | 文件更新 |
| `refactor` | 程式碼重構 |
| `perf` | 效能改善 |
| `chore` | 維護工作 |
| `test` | 測試 |
| `style` | UI/樣式 |

**範例：**
```
feat(kktix): add zendriver area auto select
fix(tixcraft): fix OCR captcha overwriting user input
refactor(fansigo): consolidate tracker blocking into global block list
```

### 4. 提交 Pull Request

```bash
# 推送到你的 fork
git push origin feature/your-feature-name
```

然後在 GitHub 上建立 Pull Request 到 `main` 分支。

**PR 檢查清單：**

- [ ] 程式碼遵循專案風格
- [ ] `.py` 檔案中沒有使用 emoji
- [ ] 已測試變更功能正常
- [ ] 無敏感資訊（密碼、API key 等）

## 程式碼規範

- **Python 版本**：3.11.9+
- **Emoji 限制**：`.py` 檔案禁止使用 emoji，`.md` 檔案允許
- **除錯輸出**：使用 `DebugLogger`（`debug = util.create_debug_logger(config_dict)`），禁止 `print()`
- **函數命名**：平台函式使用 `nodriver_{platform}_{function}()` 格式，以 `tab, config_dict` 為首參數

## 測試

```bash
cd src
python nodriver_tixcraft.py --input settings.json
```

確認：瀏覽器正常啟動、Console 無錯誤。

## 問題回報

透過 [GitHub Issues](https://github.com/bouob/tickets_hunter/issues) 回報，請附上：

- 作業系統、Python 版本、Chrome 版本
- 重現步驟與錯誤訊息
- 相關螢幕截圖

## 致謝

- **@bouob** - 專案維護者
- **max32002/tixcraft_bot** - 原始專案啟發
- 所有貢獻者與 issue 回報者
