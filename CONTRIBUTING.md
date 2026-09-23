# Contributing to Tickets Hunter

歡迎參與 Tickets Hunter 專案！請閱讀以下指南後再提交你的貢獻。

## 重要提醒

- 本專案僅供教育和研究用途
- 使用者需自行承擔法律責任
- 禁止用於商業牟利或違法用途
- 遵守各票務平台的使用條款

## 開發策略

本專案使用 **zendriver**（nodriver 的活躍 fork，支援 Chrome 145+）作為唯一搶票引擎。平台邏輯已拆分至 `src/platforms/` 目錄，各平台一個模組。

送出 PR 前請先閱讀 [`docs/02-development/code-boundaries.md`](docs/02-development/code-boundaries.md)，
其中定義了模組職責、依賴方向、命名慣例與禁止模式；另見根目錄的 [`CLAUDE.md`](CLAUDE.md)（AI 編碼工具的專案指南）。

## 貢獻流程

### 1. 先開 Issue（必要步驟）

**每個 PR 都必須先有對應的 Issue，並在 PR 內容連結該 Issue。**
沒有連結 Issue 的 PR 不會進入審查。

#### 為什麼這樣要求

- **審查需要脈絡**：搶票邏輯高度依賴各平台的 DOM 與流程細節，光看 diff 看不出為何要這樣改。
- **保留調查過程**：平台隨時改版，同一個症狀日後很可能再次出現。當初「試過什麼、排除了什麼」寫在 Issue 裡，下次不必重查一遍。
- **先對齊方向再寫程式**：避免修法方向不被接受，整個 PR 白做。
- **可追溯**：Release 說明與 CHANGELOG 都靠 Issue 編號回溯。

#### 一個合格的 Issue 要寫什麼

| 區塊 | 內容 |
|------|------|
| **問題** | 症狀、預期行為、重現步驟、環境資訊（版本 / 平台 / 目標網址 / OS） |
| **調查過程** | 試過什麼、看過哪裡、**排除了哪些可能與理由** |
| **調查結果（根因）** | 結論與證據；未確認就寫「未確認」並說明卡在哪一步 |
| **建議修法** | 打算改哪個檔案的哪個函式、是否影響其他平台 |

引用程式碼一律寫「檔案 + 函式名」，不要寫行號（行號會隨改版失效）。

> 只是回報問題、沒有要自己修的話，填完「問題」區塊即可，
> 後面三段留給接手的人補。要送 PR 才是四段全部必填。

#### 範例

```markdown
## Bug 描述
**問題**：TicketPlus 在日期列表頁卡住，不會自動選日期。
**預期行為**：自動點選第一個可售日期並進入下一步。

## 重現步驟
1. 目標網址填 TicketPlus 活動頁
2. 啟動 nodriver_tixcraft.exe
3. 頁面停在日期列表，紀錄檔重複輸出「date list not found」

## 環境資訊
- Release 版本：2026.05.02 / 平台：TicketPlus / OS：Windows 11 / 執行方式：exe

## 調查過程
- 換另外兩場活動同樣重現，排除單一活動設定問題
- 關閉「自動刷新頁面間隔」仍重現，排除刷新時序問題
- 用瀏覽器 DevTools 對照 DOM：`#buyTicket` 底下多了一層 wrapper，
  原本的直接子代選擇器抓不到日期列
- 已排除 Cloudflare 攔截（頁面正常載入，無挑戰頁）

## 調查結果（根因）
TicketPlus 2026-05 改版在 `#buyTicket` 與日期列之間插入一層容器，
`src/platforms/ticketplus.py` 的日期解析函式使用直接子代選擇器，因此比對不到任何列。

## 建議修法
把該函式的選擇器從直接子代改為後代選擇器，並保留舊結構的備援分支。
僅影響 TicketPlus，不動 `src/util.py`。
```

開好 Issue 後，等待維護者確認方向，再進行下一步。

### 2. Fork 與設定

```bash
# Fork 此倉庫後 clone
git clone https://github.com/YOUR_USERNAME/tickets_hunter.git
cd tickets_hunter

# 設定上游倉庫
git remote add upstream https://github.com/bouob/tickets_hunter.git
```

### 3. 建立分支

```bash
# 同步最新版本
git fetch upstream
git checkout main
git merge upstream/main

# 建立功能分支
git checkout -b fix/123-ticketplus-date-list
```

**分支命名規則：**

| 字首 | 用途 |
|------|------|
| `feature/` | 新功能 |
| `fix/` | Bug 修復 |
| `docs/` | 文件更新 |
| `refactor/` | 程式碼重構 |

建議在字首後帶上 Issue 編號，例如 `fix/123-ticketplus-date-list`。

### 4. Commit 規範

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

### 5. 提交 Pull Request

```bash
# 推送到你的 fork
git push origin fix/123-ticketplus-date-list
```

然後在 GitHub 上建立 Pull Request 到 `main` 分支。

**PR 檢查清單：**

- [ ] PR 內容最上方已填入 `Closes #編號`（只處理部分則用 `Refs #編號`）
- [ ] 該 Issue 已記錄問題描述、調查過程、調查結果（根因）
- [ ] 修改範圍與 Issue 的「建議修法」一致，未夾帶無關變更
- [ ] 程式碼遵循專案風格
- [ ] `.py` 檔案中沒有使用 emoji
- [ ] 已測試變更功能正常
- [ ] 無敏感資訊（密碼、API key 等）

> PR 內容有自動檢查：偵測不到 Issue 連結時會標記失敗並留言提醒，補上編號後會自動通過。

## 程式碼規範

- **Python 版本**：3.11.9+
- **Emoji 限制**：`.py` 檔案禁止使用 emoji，`.md` 檔案允許
- **除錯輸出**：使用 `DebugLogger`（`debug = util.create_debug_logger(config_dict)`），禁止 `print()`
- **函式命名**：平台函式使用 `nodriver_{platform}_{function}()` 格式，以 `tab, config_dict` 為首參數

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

若你打算自己動手修，請依照上方 [先開 Issue（必要步驟）](#1-先開-issue必要步驟) 把調查過程與根因一併寫進 Issue。

## 致謝

- **@bouob** - 專案維護者
- **max32002/tixcraft_bot** - 原始專案啟發
- 所有貢獻者與 issue 回報者
