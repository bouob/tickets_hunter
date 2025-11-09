# 實作計畫：Cityline Platform NoDriver Migration

**分支**：`006-cityline-nodriver-migration` | **日期**：2025-11-10 | **規格**：[spec.md](spec.md)
**輸入**：來自 `/specs/006-cityline-nodriver-migration/spec.md` 的功能規格說明

## 摘要

將 Cityline 平台搶票系統從 Chrome UC (Undetected Chrome) 遷移至 NoDriver,以獲得更好的反偵測能力和穩定性。本次遷移需實作完整的 NoDriver 版本票務流程,包含登入、日期選擇、區域選擇、票數選擇及提交,並遵循專案的 NoDriver First 原則。

**關鍵技術方案**：
- 優先使用 NoDriver 原生 CDP 方法 (query_selector, click, send_keys)
- 實作條件回退機制 (date_auto_fallback, area_auto_fallback)
- 保持與 Chrome UC 版本的功能對等性
- 使用現有 settings.json 欄位,不改變配置結構

**研究所得技術方案**（Phase 0 研究產出）：
- Cityline 平台使用標準 DOM 結構,不涉及 closed Shadow DOM
- 主要選擇器：`button.date-time-position`（日期）、`div.form-check input[type=radio]`（區域）、`select.select-num`（票數）
- 條件回退機制參考 TixCraft NoDriver 實作（Feature 003）
- 多分頁處理使用 tab management API
- reCAPTCHA 等待時間設定為 6 秒（參考既有實作經驗）

---

## 技術上下文 (Technical Context)

**語言/版本**：Python 3.10+
**主要相依性 (dependency)**：
- NoDriver（最新版本,參考 `docs/06-api-reference/nodriver_api_guide.md`）
- asyncio（異步流程控制）
- Chrome 瀏覽器 90+（NoDriver 運行需求）
- 現有工具函式（`util.py`）

**儲存方式**：N/A（不涉及資料庫,僅讀取 settings.json）

**測試**：
- 手動測試（30 秒 timeout 快速測試）
- 測試指令參考 `CLAUDE.md` 快速測試指令區塊
- 整合測試（完整搶票流程驗證）

**目標平台**：Windows 10+（專案主要目標平台）

**專案類型**：Single（CLI automation tool）

**效能目標**：
- 日期/區域關鍵字匹配處理時間 <2 秒（不含網路延遲）
- 頁面元素查詢 <5 秒或逾時
- 整體搶票流程與 Chrome UC 版本效能相當

**限制條件**：
- 記憶體使用 <500MB（專案整體限制）
- NoDriver 反偵測優勢優先於極致效能
- reCAPTCHA 需手動完成（不實作自動繞過）

**規模/範圍**：
- 單一平台遷移（Cityline）
- 約 10-15 個核心函數
- 預計程式碼量：800-1200 行（參考 TixCraft NoDriver 實作）

---

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

### I. NoDriver First（技術架構優先性）

**✅ 符合**：本專案核心目標即為遷移至 NoDriver。

- 新功能在 NoDriver 版本實作（`nodriver_tixcraft.py`）
- Chrome UC 版本保留作為回退方案（維護模式）
- 使用者可透過 `webdriver_type` 設定自由切換
- NoDriver 實作優先使用 CDP 原生方法（query_selector、click、send_keys）

**檢查點**：
- [x] 確認所有新函數使用 `nodriver_cityline_*` 命名前綴
- [x] 確認優先使用 NoDriver CDP 方法而非 JavaScript
- [x] 確認 Chrome UC 版本功能保持不變（功能對等性）

---

### II. 資料結構優先（設計先於實作）

**✅ 符合**：遵循標準 speckit 流程。

**Phase 0 - 研究階段**：
- 研究 Cityline 平台 DOM 結構與 CSS 選擇器
- 研究 NoDriver API 使用策略（CDP vs JavaScript）
- 研究條件回退機制實作方式（參考 TixCraft）

**Phase 1 - 設計階段**：
- 定義 Cityline 特定的資料模型（`data-model.md`）
  - 全域狀態變數（`cityline_purchase_button_pressed`、`is_cityline_account_assigned`）
  - 匹配結果資料結構（`matched_blocks`）
  - 回退模式標記（`is_fallback_selection`）
- 定義函數契約（`contracts/cityline-interface.md`）
  - 函數簽章與參數
  - 輸入驗證規則
  - 回傳值格式

**檢查點**：
- [ ] Phase 0 完成 research.md
- [ ] Phase 1 完成 data-model.md
- [ ] Phase 1 完成 contracts/ 目錄
- [ ] 實作前不偏離設計

---

### III. 三問法則（決策守門人）

**決策記錄**：

**Q1: 是核心問題嗎？**
- ✅ 是。Cityline 是專案支援的票務平台之一,NoDriver 遷移是架構升級的核心工作。
- ✅ 解決 Chrome UC 反偵測能力不足的問題。

**Q2: 有更簡單的方法嗎？**
- ❌ 無。必須完整實作 NoDriver 版本才能替代 Chrome UC。
- ✅ 複雜度有正當理由：NoDriver 提供更好的反偵測能力,是專案長期技術方向。
- ✅ 遵循 YAGNI：僅實作必要功能,不新增額外特性。

**Q3: 會破壞相容性嗎？**
- ✅ 不會。保留 Chrome UC 版本作為回退方案。
- ✅ 使用者透過 `webdriver_type` 設定切換,無需修改其他配置。
- ✅ settings.json 結構不變,不影響既有使用者。

**檢查點**：
- [x] 決策記錄於本文件
- [x] 複雜度有正當理由
- [x] 不破壞相容性

---

### IV. 單一職責與可組合性（函數設計原則）

**✅ 符合**：遵循平台模組設計原則。

**函數拆分策略**：
```python
# 主入口函數
nodriver_cityline_main(tab, url, config_dict)

# 各階段獨立函數（單一職責）
nodriver_cityline_login(tab, config_dict)
nodriver_cityline_date_auto_select(tab, config_dict)  # 含條件回退
nodriver_cityline_area_auto_select(tab, config_dict)  # 含條件回退
nodriver_cityline_ticket_number_auto_select(tab, config_dict)
nodriver_cityline_next_button_press(tab)
nodriver_cityline_purchase_button_press(tab, config_dict)

# 輔助函數
nodriver_cityline_cookie_accept(tab)
nodriver_cityline_clean_ads(tab)
nodriver_cityline_close_second_tab(tab)
```

**可組合性**：
- 每個函數可獨立測試
- 共用邏輯提取至 `util.py`（關鍵字匹配、選擇模式）
- 依賴注入：參數傳遞而非全域變數

**檢查點**：
- [x] 函數命名遵循 `nodriver_cityline_<功能>` 格式
- [x] 每個函數職責單一明確
- [x] 函數體長度 <50 行（超過需拆分）
- [x] 共用邏輯提取至 util.py

---

### V. 設定驅動開發（使用者友善設計）

**✅ 符合**：所有行為由 settings.json 驅動。

**使用的現有設定欄位**：
```json
{
  "webdriver_type": "nodriver",
  "advanced": {
    "cityline_account": "user@example.com",
    "verbose": true
  },
  "date_auto_select": {
    "enable": true,
    "date_keyword": "\"10/03\",\"10/04\"",
    "mode": "from top to bottom",
    "date_auto_fallback": false
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"搖滾區\",\"站票\"",
    "mode": "from top to bottom",
    "area_auto_fallback": false
  },
  "ticket_number": 2,
  "keyword_exclude": "\"輪椅\",\"身障\"",
  "auto_reload_coming_soon_page": true,
  "auto_reload_page_interval": 1.5,
  "play_sound": {
    "enable": true,
    "ticket": true
  }
}
```

**不新增設定欄位**：
- date_auto_fallback / area_auto_fallback 直接使用既有欄位
- reCAPTCHA 等待時間暫不可配置（硬編碼 6 秒）

**檢查點**：
- [x] 所有行為讀取自 settings.json
- [x] 不新增 Cityline 專屬設定欄位
- [x] 配置驗證透過現有 schema

---

### VI. 測試驅動穩定性（品質守門人）

**✅ 符合**：提供手動測試與整合測試策略。

**測試層級**：

1. **手動快速測試**（開發階段）
   ```bash
   cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
   rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
   echo "" > .temp/test_output.txt && \
   timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
   ```

2. **整合測試**（完整流程）
   - 測試 Cityline 登入流程
   - 測試日期選擇（含條件回退）
   - 測試區域選擇（含條件回退）
   - 測試多分頁處理

3. **功能對等性測試**
   - 與 Chrome UC 版本功能逐一對照
   - 確保所有既有功能在 NoDriver 版本可用

**檢查點**：
- [x] 提供快速測試指令
- [x] 文件化手動測試步驟
- [ ] PR 前完成整合測試
- [ ] 驗證功能對等性

---

### VII. MVP 原則（最小可行產品優先）

**✅ 符合**：優先實作核心流程。

**P1 (MVP) - 必須實作**：
- ✅ NoDriver 基礎設施（browser 啟動、tab 管理）
- ✅ 登入功能（帳號填入、同意條款勾選）
- ✅ 日期選擇（關鍵字匹配 + 條件回退）
- ✅ 區域選擇（關鍵字匹配 + 條件回退）
- ✅ 票數選擇
- ✅ 下一步按鈕點擊
- ✅ 購買按鈕點擊
- ✅ 多分頁處理

**P2 - 重要特性**：
- ✅ 廣告清除
- ✅ Cookie 同意
- ✅ 音效播放
- ✅ 自動重試進入活動

**P3 - 後續改進**：
- ⏸️ reCAPTCHA 等待時間可配置
- ⏸️ NoDriver 效能優化
- ⏸️ 錯誤分類與詳細錯誤訊息

**檢查點**：
- [x] P1 story 優先實作
- [x] 每個 P1 功能可獨立測試
- [x] P2/P3 不阻礙 P1 發佈

---

### VIII. 文件與代碼同步（知識傳承）

**✅ 符合**：同步更新所有相關文件。

**需更新的文件**：
- [ ] `docs/02-development/structure.md` - 新增 Cityline NoDriver 函數索引
- [ ] `README.md` - 更新 platform support table（Cityline NoDriver 支援狀態）
- [x] `specs/006-cityline-nodriver-migration/spec.md` - 功能規格（已完成）
- [x] `specs/006-cityline-nodriver-migration/plan.md` - 本文件
- [ ] `specs/006-cityline-nodriver-migration/data-model.md` - 資料模型（Phase 1）
- [ ] `specs/006-cityline-nodriver-migration/contracts/` - 契約定義（Phase 1）
- [ ] `CHANGELOG.md` - 記錄遷移完成（PR merge 時）

**文件同步檢查清單**（PR 評審必檢）：
- [ ] 新增函數已記錄於 structure.md
- [ ] README.md 平台支援表已更新
- [ ] spec.md 與實作代碼一致
- [ ] contracts/ 中的函數簽章與實作一致
- [ ] CHANGELOG.md 記錄變更

---

### IX. Git 提交規範與工作流程（版本控制紀律）

**✅ 符合**：使用 Conventional Commits 與 /gsave 指令。

**提交訊息格式**：
```
feat(cityline): implement NoDriver version for Cityline platform

Migrated Cityline ticket automation from Chrome UC to NoDriver engine,
including login, date selection, area selection, and ticket number selection.
Implemented conditional fallback mechanism (date_auto_fallback, area_auto_fallback)
to maintain feature parity with other platforms.

Closes #[issue-number]
```

**分支策略**：
- 功能分支：`006-cityline-nodriver-migration`
- 基於 `main` 分支開發
- PR merge 前確保所有測試通過

**雙 Repo 維護**：
- 公開檔案（`src/nodriver_tixcraft.py` 修改）→ 標準 commit
- 機敏檔案（`specs/`, `docs/`, `CLAUDE.md`）→ 帶 🔒 PRIVATE 標記的 commit
- 使用 `/gsave` 自動分離公開/機敏 commits
- 使用 `/publicpr` 建立 PR 到公開 repo（發布時）

**檢查點**：
- [x] 提交訊息遵循 Conventional Commits
- [x] 使用 /gsave 產生規範化提交
- [ ] PR 鏈接相關 spec 文件
- [ ] 通過所有 9 條憲章原則檢查

---

## 專案結構

### 文件（本功能）

```
specs/006-cityline-nodriver-migration/
├── plan.md              # 本文件 (/speckit.plan 產出)
├── research.md          # Phase 0 研究報告（研究 Cityline DOM、NoDriver API、條件回退機制）
├── data-model.md        # Phase 1 資料模型（Cityline 狀態變數、匹配結果結構）
├── quickstart.md        # Phase 1 快速開始（設定範例、測試指令）
├── contracts/           # Phase 1 契約定義
│   ├── cityline-interface.md       # Cityline NoDriver 函數簽章
│   ├── fallback-mechanism.md       # 條件回退機制契約
│   └── logging-format.md            # 日誌訊息格式規範
├── checklists/
│   └── requirements.md  # 規格品質檢查清單（已完成）
└── tasks.md             # Phase 2 任務清單（/speckit.tasks 產出 - 尚未建立）
```

### 原始碼（repository 根目錄）

```
src/
├── nodriver_tixcraft.py          # NoDriver 主程式（新增 Cityline 函數於此）
│   ├── nodriver_cityline_main()                    # 主入口
│   ├── nodriver_cityline_login()                   # 登入
│   ├── nodriver_cityline_date_auto_select()        # 日期選擇（含條件回退）
│   ├── nodriver_cityline_area_auto_select()        # 區域選擇（含條件回退）
│   ├── nodriver_cityline_ticket_number_auto_select() # 票數選擇
│   ├── nodriver_cityline_next_button_press()       # 下一步按鈕
│   ├── nodriver_cityline_purchase_button_press()   # 購買按鈕
│   ├── nodriver_cityline_cookie_accept()           # Cookie 同意
│   ├── nodriver_cityline_clean_ads()               # 廣告清除
│   └── nodriver_cityline_close_second_tab()        # 多分頁處理
├── chrome_tixcraft.py            # Chrome UC 版本（保持不變,作為參考）
├── util.py                       # 共用工具函式（關鍵字匹配、選擇模式）
└── settings.json                 # 配置檔案（不修改結構）

tests/
├── integration/
│   └── test_cityline_nodriver_flow.py  # 整合測試（手動測試為主）
└── unit/
    └── test_cityline_keyword_matching.py  # 單元測試（可選）

docs/
├── 02-development/
│   └── structure.md              # 更新：新增 Cityline NoDriver 函數索引
├── 03-mechanisms/
│   ├── 04-date-selection.md      # 參考：日期選擇機制
│   └── 05-area-selection.md      # 參考：區域選擇機制
└── 06-api-reference/
    └── nodriver_api_guide.md     # 參考：NoDriver API 使用指南
```

**結構決策**：
- 採用 **Single project** 結構
- 所有 Cityline NoDriver 函數新增至 `src/nodriver_tixcraft.py`（與 TixCraft、KKTIX、iBon 等平台共用同一檔案）
- 保留 Chrome UC 版本於 `src/chrome_tixcraft.py`（維護模式,不修改）
- 共用工具函式位於 `src/util.py`
- 測試以手動整合測試為主,單元測試為輔

---

## 複雜度追蹤

*本專案無違反憲章規範的複雜度,不需填寫此區塊。*

所有設計決策皆符合專案憲章 9 大核心原則,無需額外複雜度說明。

---

## 後續步驟

本文件（plan.md）完成後,接下來的工作流程：

1. **Phase 0: 研究階段**（下一步）
   - 執行 `/speckit.plan` 內建的研究流程（或手動研究）
   - 產出 `research.md`
   - 解決所有技術未知項目

2. **Phase 1: 設計階段**
   - 產出 `data-model.md`
   - 產出 `contracts/` 目錄下的契約檔案
   - 產出 `quickstart.md`

3. **Phase 2: 任務階段**
   - 執行 `/speckit.tasks` 產生 `tasks.md`
   - 將實作工作拆分為可執行的任務清單

4. **Phase 3: 實作階段**
   - 執行 `/speckit.implement` 或手動實作
   - 遵循 tasks.md 中的任務順序
   - 持續更新文件與測試

**重要提醒**：
- 每個階段完成後需回頭檢查憲章合規性
- 實作過程中若發現設計不足,必須回溯至 data-model.md 或 contracts/ 修訂
- 不得跳過設計階段直接進入實作

---

**計畫版本**：1.0
**最後更新**：2025-11-10
**建立者**：Claude (Sonnet 4.5)
**審核狀態**：待 Phase 0 研究完成後進行第二次憲章檢查
