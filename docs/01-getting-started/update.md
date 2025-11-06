# 定期維護更新指南

> 此文件列出需要定期更新的項目，確保專案與外部環境保持同步（最後更新：2025.10.28）

---

## 📋 維護總覽表

| 項目 | 頻率 | 關鍵檔案 | 檢查命令 |
|------|------|----------|----------|
| **Chrome User-Agent** | 2-3個月 | `src/util.py:22`, `src/chrome_tixcraft.py:128`, `src/nodriver_tixcraft.py:102` | `grep -r "Chrome/[0-9]" src/*.py` |
| **Python 套件** | 3-6個月 | `requirements.txt` | `pip list --outdated` |
| **NoDriver 版本** | 每月 | 官方 repo | `pip show nodriver` |
| **平台相容性** | 每週 | 各平台主函式 | 手動測試 |
| **Chrome 擴充套件** | 有新版時 | `src/webdriver/Max*_1.0.0/` | 檢查 manifest.json |
| **版本號統一** | 每次發布 | `src/chrome_tixcraft.py:47`, `src/nodriver_tixcraft.py:44`, `src/config_launcher.py:36`, `src/settings.py:42`, `src/settings_old.py:37`, `README.md:5,484`, `www/settings.html:79` | 確保一致性 |
| **法規追蹤** | 法規修正時 | `README.md`, `LEGAL_NOTICE.md` | 監控官方公告 |
| **網頁介面** | 重大更新後 | `www/settings.html` | 版本/平台同步 |
| **Spec 文件** | 每次平台更新 | `specs/001-ticket-automation-system/`, `specs/platform-completion/` | 檢查平台完成度矩陣 |
| **CHANGELOG** | 每次發布 | `CHANGELOG.md` | 使用者視角編寫 |
| **憲法合規性** | 每季度 | `.specify/memory/constitution.md` | 9 大核心原則檢查 |

---

## 🎯 NoDriver First 策略維護

**遵循憲法第 I 條**：查詢 `.specify/memory/constitution.md`

### 引擎優先級與維護模式

```
優先度 1：NoDriver 版本
├── 新功能開發 → 優先在 NoDriver 版本實作
├── 核心修復 → 必須包含 NoDriver 版本
└── 監控來源：src/nodriver_tixcraft.py

優先度 2：Chrome 版本
├── 維護模式 → 僅嚴重錯誤與安全補丁
├── 新功能 → 暫不開發，進入維護模式
└── 監控來源：src/chrome_tixcraft.py

優先度 3：Selenium 版本
├── 標準場景 → 測試環境使用
└── 淘汰計劃 → 2025 年底前全面遷移至 NoDriver
```

### 平台 NoDriver 支援狀態維護

**完全支援** ✅（95%+ 完成）- 6 個平台
- TixCraft（拓元）、KKTIX、TicketPlus（遠大）
- iBon、KHAM（寬宏）、ticket.com.tw（年代）
- **維護重點**：微優化、邊界情況處理

**部分支援** ⚠️（15-60% 完成）- 2 個平台
- Cityline（進行中 40-60%）
- TicketMaster（進行中 15-25%）
- **維護重點**：完成缺失功能、增加測試覆蓋

**未支援** ❌（0% 完成）- 3 個平台
- FamiTicket、Urbtix、HKTicketing
- **維護重點**：根據優先級規劃遷移

### 平台完成度檢查流程

**每週平台測試**：
1. 優先測試 NoDriver 版本（src/nodriver_tixcraft.py）
2. 登入流程驗證
3. 日期/區域/票數選擇驗證
4. 驗證碼識別功能檢查（若支援）
5. 結帳流程驗證

**遇到問題處理**：
1. 檢查 specs/001-ticket-automation-system/spec.md 確認需求
2. 參考 platform-completion/tasks-all-platforms.md 了解已知問題
3. 檢查 docs/08-troubleshooting/README.md 尋找類似案例
4. 必要時參考憲法第 VI 條「測試驅動穩定性」進行除錯

---

## 📚 Spec 文件系統維護

**遵循憲法第 II、VIII 條**：資料結構優先、文件與代碼同步

### 核心 Spec 文件結構

```
specs/001-ticket-automation-system/
├── spec.md                     ← 功能規格（需求文件）
├── plan.md                     ← 實作計劃（設計文件）
├── tasks.md                    ← 主任務清單（可執行任務）
├── data-model.md               ← 資料結構設計
├── research.md                 ← 技術研究與決策
├── quickstart.md               ← 快速開始指南
│
├── contracts/
│   ├── config-schema.md        ← 配置 JSON Schema
│   ├── platform-interface.md   ← 平台介面契約
│   └── util-interface.md       ← 工具函式契約
│
├── checklists/
│   └── requirements.md         ← 品質檢查清單
│
└── archive/
    ├── tasks-p0-ibon-fix.md    ← 已完成的修復任務
    └── plan-incremental.md     ← 已過時的規劃文檔
```

### 平台遷移任務維護

**位置**：`specs/` 目錄下的各平台遷移目錄

**狀態標記規範**：
```yaml
status: "未開始 (0%)" / "進行中 (XX%)" / "已完成 (100%)"
last_updated: "2025-10-19"  # ISO 8601 格式
completion_estimate: "1-2 週"
notes: "相關注意事項"
```

**維護檢查清單**（每季度更新）：
- [ ] 所有遷移任務都有 `status` 標記
- [ ] 所有任務都有 `last_updated` 日期
- [ ] 已完成平台的任務已歸檔
- [ ] 平台完成度矩陣已同步（`platform-completion/tasks-all-platforms.md`）

### 憲法合規性檢查（每季度）

**9 大核心原則審查**（參考 `.specify/memory/constitution.md`）：

| 原則 | 檢查項目 | 驗收標準 |
|------|---------|---------|
| **I. NoDriver First** | 新功能優先 NoDriver | 所有新增功能在 src/nodriver_tixcraft.py |
| **II. 資料結構優先** | 設計先於實作 | 規格文件完整，無臨時代碼 |
| **III. 三問法則** | 決策有文件化 | spec.md 中有決策理由 |
| **IV. 單一職責** | 函數職責清晰 | 函數名稱準確描述功能 |
| **V. 設定驅動開發** | 配置在 settings.json | 無硬編碼業務邏輯 |
| **VI. 測試驅動穩定性** | 核心修改有測試 | 測試覆蓋率 > 70% |
| **VII. MVP 原則** | 優先完整核心流程 | 發布版本應是可工作的 MVP |
| **VIII. 文件與代碼同步** | 文件最新且准確 | 代碼改動時同步文檔 |
| **IX. Git 規範** | 提交訊息遵循規範 | 使用 Conventional Commits |

**審查命令**：
```bash
# 檢查代碼中是否有 emoji（Python 代碼中禁止）
grep -r "✅\|❌\|🔴\|⚠️" src/*.py

# 檢查是否有硬編碼業務邏輯（應在 settings.json）
grep -r "magic number\|硬編碼" src/*.py

# 檢查 Git 提交規範
git log --oneline --all | grep -v "^[a-z]*("
```

---

## 📝 CHANGELOG 維護指南

**遵循 `docs/10-project-tracking/changelog_guide.md`**

### 編寫原則（使用者視角）

**✅ 應該寫什麼**：
- 新增的平台支援
- 使用者可用的新功能
- 修正了什麼問題（使用者能感受）
- 行為改變（搶票流程、設定方式）
- 相容性破壞（需要使用者調整）

**❌ 不該寫什麼**（開發者文檔屬於 commit message）：
- 函數名稱、程式碼位置
- 實作細節、技術術語（DOM、CDP、Shadow DOM）
- 測試結果、效能數字
- 內部重構、檔案重新組織

### CHANGELOG 格式規範

```markdown
## YYYY.MM.DD

- 新增/修正 主要功能 (受影響平台)
- 改善 功能性改善 (受影響平台)
- 修正 問題描述 (受影響平台)
```

**範例（好）**：
```markdown
## 2025.10.18

- 修正 iBon 平台票券數量選擇穩定性問題（NoDriver 引擎）
- 新增票券數量設定驗證邏輯，確保配置值與實際選定數量一致
- 改善票券數量選擇邏輯，支援多組備選選擇器以提高相容性
```

**範例（不好）**：
```markdown
## 2025.10.18

- 修復 nodriver_ibon_ticket_number_auto_select 函數的 DOM 查詢失敗
- 在 nodriver_tixcraft.py:10646-10654 添加設定驗證邏輯
- 優化 Shadow DOM 查詢性能，減少 DOM 遍歷次數
```

### 發布前 CHANGELOG 檢查清單

- [ ] 每個條目從使用者角度描述
- [ ] 避免技術術語與實作細節
- [ ] 避免函數名稱與程式碼位置
- [ ] 標明受影響平台
- [ ] 新增/修正/改善 動詞正確
- [ ] 格式符合 `YYYY.MM.DD` 日期規範

---

## 🚨 緊急更新觸發條件

### ⚡ 立即處理（0-24 小時）
- **售票平台重大變更** → 影響核心功能（頁面結構、登入方式變更）
- **法規緊急修正** → 涉及合法性問題
- **安全漏洞發現** → 影響用戶數據或帳戶安全
- **Chrome 重大更新** → 破壞現有功能（新版本 WebDriver 不相容）

### 🔧 處理流程
1. 立即停止相關功能使用
2. 評估影響範圍和修復時間
3. **檢查規格與憲法** - 確保修復符合設計
4. 優先修復 NoDriver 版本（無需修復 Chrome 版本）
5. 測試驗證後發布
6. 更新 CHANGELOG（使用者視角）
7. 更新相關文件（spec.md、README.md）

---

## 🔄 定期維護（按頻率分組）

### 每月必檢 ⏰

#### Chrome User-Agent 更新
```bash
# 檢查當前版本
grep -r "Chrome/[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+" src/*.py

# 查詢最新版本
# https://chromereleases.googleblog.com/
# https://www.whatismybrowser.com/guides/the-latest-version/chrome
```

**更新檔案**（記錄當前 Chrome 版本號）：
- `src/util.py:22` - 主要 USER_AGENT 定義
- `src/chrome_tixcraft.py:128` - Chrome WebDriver 版本
- `src/nodriver_tixcraft.py:102` - NoDriver 版本

#### NoDriver 版本檢查
```bash
# 檢查當前版本
pip show nodriver

# 查看是否有新版本
pip index versions nodriver

# 更新至最新版本
python -m pip install git+https://github.com/ultrafunkamsterdam/nodriver --upgrade
```

**檢查後操作**：
- [ ] 記錄 NoDriver 版本號
- [ ] 測試關鍵平台（KKTIX、TixCraft）
- [ ] 檢查是否有不相容變更

#### 平台功能測試（NoDriver 優先）
**測試平台優先級**：
1. 🥇 **完全支援** - KKTIX、TixCraft、TicketPlus、iBon、KHAM、ticket.com.tw
2. 🥈 **部分支援** - Cityline、TicketMaster
3. 🥉 **Chrome 版本** - 僅嚴重錯誤修復

**檢查項目**：
- [ ] 手動測試主要流程（登入 → 選票 → 結帳）
- [ ] 監控 JavaScript 錯誤（瀏覽器控制台）
- [ ] 檢查 OCR 辨識成功率（若支援）
- [ ] 驗證售出狀態處理

### 每季更新 📅

#### Python 套件全面檢查
```bash
# 檢查過期套件
pip list --outdated

# 重點套件更新
pip install --upgrade selenium undetected-chromedriver ddddocr nodriver
```

**核心套件**：
- `selenium` - WebDriver 核心
- `undetected-chromedriver` - 反偵測核心
- `nodriver` - 新式反偵測引擎（優先更新）
- `ddddocr` - OCR 辨識引擎

#### Chrome 擴充套件檢查
**檔案位置**：
- `src/webdriver/Maxblockplus_1.0.0/` - 廣告阻擋
- `src/webdriver/Maxbotplus_1.0.0/` - DOM 操作輔助

**檢查要點**：
- [ ] manifest.json 相容性
- [ ] 新版 Chrome 支援度
- [ ] 阻擋規則有效性

#### 平台完成度矩陣更新
```bash
# 檢查平台完成度
cat specs/platform-completion/tasks-all-platforms.md

# 更新狀態（如有遷移進展）
# 編輯相應的 migration tasks.md 中的 status 欄位
```

#### Spec 文件一致性檢查
```bash
# 檢查 spec 文件語法
find specs/ -name "*.md" -exec grep -l "status:\|last_updated:" {} \;

# 列出所有未完成的遷移任務
grep -r "status.*未開始\|進行中" specs/
```

### 年度規劃 🎯

- [ ] 技術棧升級評估（Python、NoDriver 重大版本）
- [ ] 架構重構需求分析（考慮 MVP 原則）
- [ ] 新平台支援規劃（根據用戶需求）
- [ ] 安全性全面審查（查詢憲法第 III-IX 條）
- [ ] 法規變更全面檢討（台灣文化創意產業發展法）

---

## 🧰 快速工具指令

**遵循憲法第 IX 條**：Git 提交規範與工作流程

### Git 相關指令

```bash
# 自動生成規範化 commit message
/gsave

# 檢查最近變動與自動生成 CHANGELOG
/gchange [days]     # 例：/gchange 7 (過去 7 天)

# 清除本地敏感設定檔（避免提交）
/gdefault

# 推送累積的 commits 到遠端倉庫
/gpush
```

### 專案工具指令（speckit）

```bash
# 生成功能規格（spec.md）
/speckit.specify [功能描述]

# 檢查規格不足之處並提問
/speckit.clarify

# 生成實作計劃（plan.md、data-model.md 等）
/speckit.plan

# 生成任務清單（tasks.md）
/speckit.tasks

# 執行所有任務（自動背景測試）
/speckit.implement

# 檢查文件一致性（spec.md ↔ plan.md ↔ tasks.md）
/speckit.analyze

# 為當前功能生成品質檢查清單
/speckit.checklist
```

### 除錯工具指令

```bash
# 整合 spec 檢查、合規驗證、代碼定位的除錯工具
/debug
```

---

## 📁 檔案位置速查表

### 版本號相關檔案

| 檔案 | 行數 | 內容 | 說明 |
|------|------|------|------|
| `src/chrome_tixcraft.py` | 47 | `CONST_APP_VERSION` | Chrome 引擎版本 |
| `src/nodriver_tixcraft.py` | 44 | `CONST_APP_VERSION` | NoDriver 引擎版本 |
| `src/config_launcher.py` | 36 | `CONST_APP_VERSION` | 設定啟動器版本 |
| `src/settings.py` | 42 | `CONST_APP_VERSION` | 網頁設定介面版本 |
| `src/settings_old.py` | 37 | `CONST_APP_VERSION` | 舊版設定介面版本 |
| `README.md` | 5, 484 | 版本資訊/更新日期 | 對外展示版本 |
| `www/settings.html` | 79 | 網頁介面版本 | 使用者介面版本 |

### 核心設定檔案

| 檔案 | 說明 | 維護重點 |
|------|------|----------|
| `src/util.py` | 共用工具與設定 | User-Agent, 通用函式 |
| `src/settings.json` | 主要設定檔 | 平台參數、除錯設定 |
| `requirements.txt` | 套件依賴 | 版本鎖定與更新 |
| `CHANGELOG.md` | 更新歷史 | 使用者視角編寫 |

### 重要文件

| 檔案 | 用途 | 更新頻率 |
|------|------|---------|
| `.specify/memory/constitution.md` | 9 大核心原則 | 年度檢查 |
| `specs/001-ticket-automation-system/spec.md` | 功能規格 | 功能更新時 |
| `specs/platform-completion/tasks-all-platforms.md` | 平台完成度 | 季度更新 |
| `docs/10-project-tracking/changelog_guide.md` | CHANGELOG 規範 | 參考文檔 |

---

## 📝 操作手冊

### 版本號統一更新流程

```bash
# 1. 確認新版本號（格式：TicketsHunter (YYYY.MM.DD)）
# 範例：TicketsHunter (2025.10.19)

# 2. 批量更新所有檔案
sed -i 's/TicketsHunter (2025.10.18)/TicketsHunter (2025.10.19)/g' \
  src/chrome_tixcraft.py \
  src/nodriver_tixcraft.py \
  src/config_launcher.py \
  src/settings.py \
  src/settings_old.py \
  README.md \
  www/settings.html

# 3. 驗證更新結果
grep -r "CONST_APP_VERSION\|TicketsHunter" src/*.py | grep -v ".pyc"

# 4. 更新 CHANGELOG.md（使用 /gchange 工具自動生成）
/gchange 1

# 5. 提交變更
/gsave
```

### 平台相容性測試流程

1. **準備階段**
   - 清除瀏覽器快取：`Ctrl+Shift+Delete`
   - 確認網路連線穩定
   - 準備測試帳號

2. **測試項目清單**
   - [ ] 登入流程完整性
   - [ ] 選票頁面元素定位
   - [ ] 驗證碼辨識功能（若支援）
   - [ ] 提交流程無誤
   - [ ] 結帳頁面顯示正確

3. **問題記錄**
   - DOM 結構變更位置
   - 新增的防機器人機制
   - 效能問題或超時情況
   - **記錄至** `docs/08-troubleshooting/` 平台特定文件

### Spec 文件同步流程

每次功能更新後：

1. 檢查 `spec.md` 是否有相應的需求（FR-xxx、SC-xxx）
2. 更新 `plan.md` 中的設計決策（research.md 中有理由）
3. 生成或更新 `tasks.md`
4. 執行 `/speckit.analyze` 檢查文件一致性
5. 提交變更時同時更新相應文件

---

## 📊 維護檢查清單

### 🗓️ 月度檢查
- [ ] Chrome 版本號檢查更新
- [ ] NoDriver 套件版本確認
- [ ] NoDriver 平台功能測試（6 個完全支援平台）
- [ ] OCR 辨識率驗證（若使用）
- [ ] 擴充套件功能檢查
- [ ] 網頁介面版本同步

### 🗓️ 季度檢查
- [ ] Python 套件全面更新（`pip list --outdated`）
- [ ] 平台 DOM 結構深度檢查
- [ ] 平台完成度矩陣更新（`specs/platform-completion/`）
- [ ] 法規變更影響評估
- [ ] 文件完整性校對
- [ ] 憲法 9 大原則合規檢查
- [ ] 遷移任務狀態更新（未開始/進行中/已完成）

### 🗓️ 年度檢查
- [ ] 技術架構評估升級
- [ ] 新平台支援可行性分析
- [ ] 安全性威脅模型更新
- [ ] 使用者體驗優化規劃
- [ ] 專案憲章修訂評估（遵循 constitution.md）

---

## 📚 相關文件引用

**必讀文檔**：
1. `.specify/memory/constitution.md` - 9 大核心原則（必讀）
2. `CLAUDE.md` - Claude Code 專案指引
3. `docs/10-project-tracking/changelog_guide.md` - CHANGELOG 編寫規範
4. `docs/02-development/development_guide.md` - 開發規範
5. `docs/08-troubleshooting/README.md` - 問題排查索引

**快速查詢**：
- 平台狀態：`README.md` 中的「平台支援狀態」表格
- NoDriver API：`docs/06-api-reference/nodriver_api_guide.md`
- 規格文檔：`specs/001-ticket-automation-system/spec.md`
- 已知問題：`docs/08-troubleshooting/README.md`

---

## 💡 維護建議

- 📅 **設定日曆提醒**：每月第一個工作日進行月度檢查
- 🔔 **監控官方動態**：訂閱 Chrome 版本更新、法規修改
- 📊 **建立指標**：追蹤平台相容性、搶票成功率
- 🎯 **優先遷移**：Cityline(40%) → TicketMaster(15%) → FamiTicket → HKTicketing → Urbtix

---

*最後更新：2025.10.28 | 維護責任人：Claude Code | 下次季度檢查：2026.01.28*
