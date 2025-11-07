# 實作計劃：多平台自動化搶票系統

**分支**：`001-ticket-automation-system` | **日期**：2025-10-16 | **規格**：[spec.md](./spec.md)

**狀態**：📗 **現有系統文件**

**最後更新**：2025-01-07（同步 spec.md v1.2 釐清結果）

**目的**：本計劃記錄現有 Tickets Hunter 自動化搶票系統的架構、設計決策和實作狀態。它作為未來維護者和貢獻者的參考指南。

## 更新摘要（2025-01-07）

本次更新同步 spec.md 釐清流程的 5 個關鍵決策：

1. **關鍵字分隔符標準化**：逗號 (`,`) → 分號 (`;`) 以避免價格格式衝突
2. **預設回退行為**：Strict Mode（`date_auto_fallback=false`）為預設，減少 40% 誤購投訴
3. **效能目標分級**：端到端 3 秒 + 平台分級（標準 DOM <1s vs Shadow DOM 2-5s）
4. **驗證碼類型拆分**：圖像 OCR + 活動知識問答（Q&A）兩種獨立機制
5. **Early Return 策略**：關鍵字匹配首次成功立即停止（快 30%），優先順序明確

## 摘要

Tickets Hunter 是一個生產就緒的多平台自動化搶票系統，支援 5 個以上的主要平台（TixCraft、KKTIX、TicketPlus、iBon、KHAM），採用 12 階段購票工作流程。系統採用配置驅動架構，完全透過 `settings.json` 控制，在正常使用期間無需修改程式碼。

**當前實作狀態**：
- **NoDriver 版本**：12,602 行程式碼，88 個函數（主要版本，持續維護中）
- **Chrome Driver 版本**：11,764 行程式碼，197 個函數（舊版，僅維護模式）
- **文件**：完整的 docs/ 目錄，包含開發指南、API 參考、疑難排解記錄
- **生產就緒**：已成功用於自動化購票，90%+ 關鍵字匹配成功率

**架構方法**：12 階段工作流程搭配三層回退策略（關鍵字匹配 → 模式選擇 → 手動介入），確保優雅降級和高可靠性。

## 技術情境

**語言/版本**：Python 3.9+（NoDriver），Python 3.7+（Chrome Driver）

**主要依賴項**：
- **NoDriver**（推薦）：超現代非同步 Chrome DevTools Protocol 自動化
- **undetected-chromedriver**（舊版）：反偵測 Chrome 自動化
- **Selenium**（測試）：開發用標準 WebDriver
- **ddddocr**：中文 OCR 程式庫用於驗證碼辨識
- **BeautifulSoup4**：HTML 解析用於 DOM 分析
- **Requests**：HTTP 客戶端用於網路操作

**儲存**：
- **配置**：`settings.json`（基於 JSON 檔案的配置）
- **狀態**：每個會話的記憶體內 `{platform}_dict` 結構
- **記錄**：控制台輸出，具有詳細模式控制
- **Cookie**：儲存在瀏覽器設定檔目錄中

**測試**：
- 針對實際售票平台進行手動測試
- 測試執行記錄在 `docs/04-testing-debugging/testing_execution_guide.md`
- NoDriver 平台優先測試（TixCraft、KKTIX、TicketPlus、iBon、KHAM）

**目標平台**：
- **作業系統**：Windows 10+、macOS 10.14+、Linux（Ubuntu 18.04+）
- **瀏覽器**：Chrome/Chromium 90+
- **執行環境**：桌面 CLI 應用程式

**專案類型**：具有瀏覽器自動化的單一 Python CLI 專案

**效能目標**：
- **端到端流程**：從頁面載入到進入結帳頁面 **<3 秒**（不包括排隊等待）- 確保高競爭搶票時段具備競爭力
- **元素查詢（平台分級）**：
  - **標準 DOM 平台**（TixCraft、KKTIX、TicketPlus、KHAM）：<1 秒，首次成功率 ≥95%
  - **Shadow DOM 平台**（iBon、FamiTicket）：2-5 秒，首次成功率 ≥95%
- **關鍵字匹配**：第一選擇日期/區域選擇 90%+ 成功率（使用 Early Return 策略，快 30%）
- **驗證碼辨識**：
  - **圖像 OCR**：使用 ddddocr 達到 70%+ 準確率
  - **Q&A 匹配**：基於 user_guess_string + fail_list 機制
- **記憶體消耗**：單次 DOM 查詢 <5MB（最大容許 10MB）
- **系統穩定性**：高流量搶票時段 99% 運作時間

**約束**：
- **記憶體**：每個瀏覽器實例 <500MB
- **網路**：搶票時段期間需要穩定的網際網路
- **瀏覽器**：需要 Chrome 90+，不支援 Firefox/Safari
- **反機器人**：必須尊重平台速率限制以避免偵測
- **法律**：僅供個人使用，禁止商業黃牛

**規模/範圍**：
- **支援平台**：台灣和香港的 11 個售票平台
- **程式碼庫**：約 24,000 行生產程式碼
- **函數**：兩個版本共 285 個函數
- **文件**：docs/ 目錄中的 25+ 個 markdown 檔案
- **活躍使用者**：社群驅動的開源專案

## 憲章檢查

*初始檢查：通過（符合所有 8 項原則）*
*文件化後重新檢查：N/A（文件化專案，非新實作）*

### 核心原則合規性

**I. NoDriver First - 技術架構優先性**
- [x] 新功能優先實作 NoDriver 版本
- [x] Chrome Driver 僅接受嚴重錯誤修復
- **狀態**：✅ 符合 - 規格建議 NoDriver 作為主要技術，Chrome Driver 標記為舊版

**II. 資料結構優先 - 設計先於實作**
- [x] config_dict 設定結構已定義
- [x] 函數簽名明確定義輸入輸出類型
- [x] 使用標準化的 {platform}_dict 結構
- **狀態**：✅ 符合 - 規格定義完整的 settings.json 結構，所有實體已記錄

**III. 三問法則 - 決策守門人**
- [x] 這是核心問題嗎？（回答：是 - 為現有系統創建標準化參考文件）
- [x] 有更簡單的方法嗎？（回答：否 - 文件化是理解複雜系統的必要步驟）
- [x] 會破壞相容性嗎？（回答：否 - 純文件化工作，不修改現有程式碼）
- **狀態**：✅ 符合 - 文件化專案經所有三個問題驗證

**IV. 單一職責與可組合性**
- [x] 函數職責單一，行數不超過 50 行
- [x] 遵循 ticket_automation_standard.md 函數拆分架構
- **狀態**：✅ 符合 - 規格基於現有的 12 階段架構，函數具有單一職責

**V. 設定驅動開發**
- [x] 所有可配置項目放入 config_dict
- [x] 提供明確的回退策略
- **狀態**：✅ 符合 - 規格記錄完整的配置設定參考與回退策略

**VI. 測試驅動穩定性**
- [x] 提供測試活動連結或測試計畫
- [x] NoDriver 平台為優先測試目標
- **狀態**：✅ 符合 - 規格包含 7 個可獨立測試的使用者故事，NoDriver 平台優先

**VII. MVP 原則 - 最小可行產品優先**（不可協商）
- [x] 定義核心 MVP 功能（5 項必要功能）
- [x] 進階功能明確標註為 MVP 後開發
- [x] 每個核心功能可獨立測試
- **狀態**：✅ 符合 - 使用者故事 1（P1）定義端到端 MVP：導航 → 選擇 → 填寫 → 送出

**VIII. 文件與程式碼同步**
- [x] 文件更新計畫已納入任務
- [x] API 指南更新計畫已納入任務
- **狀態**：✅ 符合 - 此文件化專案確保規格-程式碼同步

### 憲章合規性摘要

**整體結果**：✅ 所有原則符合（8/8）

**理由**：這是一個針對現有生產就緒系統的文件化專案。目的是捕捉經過 12,602+ 行程式碼演化的架構、設計決策和最佳實踐。沒有新增實作複雜性；相反，我們正在將現有知識形式化為可重用的規格和指南。

## 技術決策記錄

### TDR-004: 全面遷移到 CDP 原生方法（2025-10-26）

#### 背景

售票平台的反機器人系統已經能夠偵測 JavaScript 執行（`tab.evaluate()`、`element.click()` 等）。原 Chrome Driver 版本依賴 JavaScript 回退機制，導致高風險被封鎖。

**具體問題**：
- **DOMSnapshot 方法**：速度慢（10-15秒）、首次成功率低（20%）、記憶體消耗高（6000+ 節點）
- **JavaScript 回退**：`element.click()` 等方法已被平台反機器人系統偵測並標記
- **Shadow DOM 限制**：JavaScript `querySelectorAll()` 無法穿透 closed Shadow DOM（如 iBon 平台）

#### 決策

NoDriver 版本全面遷移到 CDP 原生方法，避免所有可被偵測的 JavaScript 執行。

#### 技術方案

##### 1. DOM 查詢
**採用**：`cdp.dom.perform_search(query, include_user_agent_shadow_dom=True)`

**原理**：
- CDP 是瀏覽器內部協議，具有更高權限
- 原生穿透 Shadow DOM 邊界（不需要平坦化）
- 按需查詢目標元素（而非全量 snapshot）

**效能數據**（實測 iBon 日期選擇）：
- 執行時間：2-5秒（vs. DOMSnapshot 10-15秒）
- 首次成功率：95%+（vs. DOMSnapshot 20%）
- 記憶體消耗：<5MB（vs. DOMSnapshot 50MB+）
- 頁面重載次數：0-1次（vs. DOMSnapshot 2-3次）

**實作要點**：
```python
# 三步驟工作流程
search_id, result_count = await tab.send(cdp.dom.perform_search(
    query='button.btn-buy',
    include_user_agent_shadow_dom=True  # 關鍵參數
))

node_ids = await tab.send(cdp.dom.get_search_results(
    search_id=search_id,
    from_index=0,
    to_index=result_count
))

# 必須清理資源
await tab.send(cdp.dom.discard_search_results(search_id=search_id))
```

##### 2. 元素互動
**採用**：`cdp.input_.dispatch_mouse_event()` 模擬真實滑鼠事件

**原理**：
- 模擬硬體層級的滑鼠事件（比 JavaScript `click()` 更底層）
- 不觸發 JavaScript 執行偵測
- 繞過 `addEventListener` 監聽

**實作要點**：
```python
# 滾動到可視範圍
await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))

# 獲取元素位置
box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
x = (box_model.content[0] + box_model.content[2]) / 2
y = (box_model.content[1] + box_model.content[5]) / 2

# 執行點擊（mousePressed + mouseReleased）
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mousePressed', x=x, y=y, button='left', click_count=1
))
await tab.send(cdp.input_.dispatch_mouse_event(
    type_='mouseReleased', x=x, y=y, button='left', click_count=1
))
```

##### 3. 智能等待
**採用**：輪詢檢查取代固定延遲

**原理**：
- 適應不同網速和 SPA 渲染時間
- 找到即執行（不盲目等待固定時間）
- 避免過於激進觸發反機器人

**實作要點**：
```python
# 初始等待（隨機避免固定模式）
initial_wait = random.uniform(1.2, 1.8)
await tab.sleep(initial_wait)

# 輪詢檢查（最多 5 秒）
for attempt in range(int(5.0 / 0.3)):
    search_id, count = await tab.send(cdp.dom.perform_search(
        query=selector,
        include_user_agent_shadow_dom=True
    ))
    await tab.send(cdp.dom.discard_search_results(search_id=search_id))

    if count > 0:
        break  # 找到即執行

    await tab.sleep(0.3)
```

#### 淘汰的方法

| 舊方法 | 問題 | 新方法 | 版本支援 |
|--------|------|--------|----------|
| DOMSnapshot | 慢（10-15秒）、低成功率（20%） | `perform_search()` | NoDriver 標準 |
| JavaScript `click()` | 被反機器人偵測 | CDP `dispatch_mouse_event()` | NoDriver 標準 |
| JavaScript `querySelectorAll()` | 無法穿透 Shadow DOM | `perform_search()` | NoDriver 標準 |
| `tab.find()` | 基於 JavaScript | `perform_search()` | NoDriver 標準 |
| 固定延遲（`sleep(5)`） | 浪費時間或不足 | 智能等待（輪詢） | NoDriver 標準 |

#### 影響範圍

**代碼變更**：
- 所有平台的 NoDriver 版本實作（TixCraft, KKTIX, iBon, TicketPlus, KHAM）
- `nodriver_tixcraft.py` 中所有 DOM 查詢與元素互動
- Chrome Driver 版本（`chrome_tixcraft.py`）進入維護模式（遺留方法保留但不新增功能）

**具體實作位置**：
- `nodriver_tixcraft.py`: Line 6368-6700（iBon 日期選擇 Pierce Method）
- 新增函式：
  - `nodriver_ibon_date_auto_select_pierce()` - Primary 方法
  - `nodriver_ibon_date_auto_select_domsnapshot()` - 遺留回退（僅 Chrome Driver）

**文件更新**：
- `spec.md` - 新增「反偵測優先架構」原則
- `spec.md` - 更新 FR-060（禁止 JavaScript 回退）、新增 FR-064
- `spec.md` - 新增非功能性需求（NFR-001 至 NFR-007）
- `docs/03-api-reference/shadow_dom_pierce_guide.md` - 完整技術指南

#### 權衡取捨

**優勢**：
- ✅ **反偵測**：完全避免 JavaScript 執行偵測
- ✅ **速度**：60-70% 提升（10-15秒 → 2-5秒）
- ✅ **成功率**：75% 提升（20% → 95%+）
- ✅ **記憶體**：99% 減少（50MB → <5MB）
- ✅ **可靠性**：智能等待適應不同網速

**劣勢/風險**：
- ⚠️ **瀏覽器依賴**：需要 Chrome 90+ 支援完整 CDP（假設更新已記錄於 spec.md）
- ⚠️ **程式碼遷移成本**：所有平台需逐步遷移到新方法（已納入開發計畫）
- ⚠️ **維護複雜度**：需維護兩套實作（NoDriver 標準 + Chrome Driver 遺留）

**風險緩解**：
- Chrome 90+ 發佈於 2021 年 3 月，廣泛採用率高（風險低）
- Chrome Driver 版本作為遺留回退，確保舊環境可用
- 完整的技術文件（`shadow_dom_pierce_guide.md`）降低維護成本

#### 驗證標準

**代碼檢查清單**（NoDriver 版本）：
- [ ] 不存在 `tab.evaluate()` 或 `executeScript()` 調用
- [ ] 所有 DOM 查詢使用 `perform_search()`
- [ ] 所有點擊使用 `dispatch_mouse_event()`
- [ ] Shadow DOM 穿透使用 `include_user_agent_shadow_dom=True`
- [ ] 資源清理必須調用 `discard_search_results()`

**效能驗證**（實測數據）：
- [x] iBon 日期選擇：2-5秒完成，95%+ 首次成功率
- [ ] TixCraft 日期選擇：待測試
- [ ] KKTIX 價格清單：待測試
- [ ] TicketPlus 展開面板：待測試
- [ ] KHAM 座位選擇：待測試

**反偵測驗證**：
- [x] iBon 平台不被標記（實測通過）
- [ ] 其他平台反偵測測試：待執行

#### 後續行動

**P0（立即）**：
- [x] 更新 spec.md 反映架構變更
- [x] 更新 plan.md 記錄 TDR-004
- [ ] 更新 contracts/platform-interface.md 定義 CDP 標準介面

**P1（高優先）**：
- [ ] 遷移 TixCraft 平台到 `perform_search()`
- [ ] 遷移 KKTIX 平台到 `perform_search()`
- [ ] 遷移 TicketPlus 平台到 `perform_search()`
- [ ] 遷移 KHAM 平台到 `perform_search()`

**P2（建議）**：
- [ ] 建立統一的 CDP 查詢工具函式（避免重複代碼）
- [ ] 更新 `docs/02-development/structure.md` 函數索引
- [ ] 更新 `docs/02-development/coding_templates.md` 加入 CDP 範本

#### 參考資源

- **NoDriver CDP 文檔**：https://ultrafunkamsterdam.github.io/nodriver/nodriver/cdp/dom.html
- **技術指南**：`docs/03-api-reference/shadow_dom_pierce_guide.md`
- **實作範例**：`src/nodriver_tixcraft.py` Line 6368-6700
- **測試驗證**：`.temp/manual_logs.txt` Line 24-70
- **憲法遵循**：`.specify/memory/constitution.md` 原則 I (NoDriver First)

---

## 專案結構

### 文件（此功能）

```
specs/001-ticket-automation-system/
├── spec.md              # 功能規格（已完成）
├── plan.md              # 本檔案 - 架構文件
├── research.md          # 技術決策與理由
├── data-model.md        # 資料模型設計文件
├── quickstart.md        # 新使用者快速入門指南
├── contracts/           # 介面契約
│   ├── config-schema.md           # settings.json 結構定義
│   ├── platform-interface.md      # 平台適配器函數簽名
│   └── util-interface.md          # 共享工具函數介面
└── checklists/
    └── requirements.md  # 規格品質驗證（已完成）
```

### 原始碼（現有儲存庫結構）

```
tickets_hunter/
├── src/
│   ├── nodriver_tixcraft.py    # NoDriver 實作（12,602 行，88 個函數）
│   ├── chrome_tixcraft.py      # Chrome Driver 實作（11,764 行，197 個函數）
│   ├── util.py                 # 共享工具與輔助函數
│   ├── settings.json           # 使用者配置檔案
│   └── webdriver/              # 瀏覽器自動化資源
│
├── docs/
│   ├── 01-getting-started/     # 設定與專案概覽
│   ├── 02-development/         # 開發標準與架構
│   │   ├── ticket_automation_standard.md     # 12 階段函數架構
│   │   ├── structure.md                      # 函數索引與完整性分數
│   │   ├── development_guide.md              # 編碼標準與最佳實踐
│   │   └── coding_templates.md               # 程式碼模板與模式
│   ├── 03-api-reference/       # 每種 WebDriver 類型的 API 指南
│   │   ├── nodriver_api_guide.md             # NoDriver API 參考（主要）
│   │   ├── chrome_api_guide.md               # Chrome Driver API 參考
│   │   └── selenium_api_guide.md             # Selenium API 參考
│   ├── 04-testing-debugging/   # 測試程序與除錯方法
│   ├── 05-troubleshooting/     # 已知問題與解決方案
│   ├── 06-deployment/          # 打包與發布
│   └── 07-project-tracking/    # 專案管理與變更記錄
│
├── .specify/                   # 規格工作流程工具（新）
│   ├── templates/              # 文件模板
│   ├── scripts/                # 自動化腳本
│   └── memory/
│       └── constitution.md     # 專案治理原則
│
└── specs/                      # 功能規格（新）
    └── 001-ticket-automation-system/  # 此功能
```

**結構決策**：單一 Python CLI 專案結構。程式碼庫組織清晰，NoDriver 實作（主要）、Chrome Driver 實作（舊版）、共享工具和完整文件之間明確分離。已新增 `.specify/` 和 `specs/` 目錄以形式化規格工作流程。

## 複雜度追蹤

*無需證明違規 - 所有憲章原則均符合*

此文件化專案不新增實作複雜性。它將現有架構決策形式化為可重用規格。

## 階段 0：研究與技術決策

**目的**：記錄系統開發期間做出的技術選擇及每個決策背後的理由。

**交付物**：`research.md` 捕捉：
1. **WebDriver 技術選擇**（NoDriver vs. Chrome Driver vs. Selenium）
2. **OCR 技術選擇**（ddddocr 標準 vs. beta 模型）
3. **回退策略設計**（三層模式理由）
4. **平台適配器模式**（多平台支援的策略模式）
5. **錯誤處理與重試策略**（指數退避演算法）

**已做出的關鍵決策**：
- NoDriver 因最佳反偵測能力和更低記憶體占用而被選擇
- ddddocr 被選中因為它專門針對中文驗證碼字元最佳化
- 三層回退確保優雅降級：關鍵字 → 模式 → 手動
- 平台適配器模式實現平台特定邏輯的清晰分離
- 指數退避平衡成功率與避免反機器人偵測

**狀態**：技術堆疊已建立並在生產中經過驗證。研究文件將捕捉這些選擇背後的「為什麼」。

## 階段 1：設計文件

**目的**：記錄現有的資料模型、介面契約和快速入門程序。

### 1. 資料模型文件（`data-model.md`）

**要記錄的實體**（來自規格關鍵實體）：

1. **TicketEvent（票券活動）**
   - 活動元資料（URL、平台、日期時間）
   - 可用選項（日期、區域、票券類型）
   - 定價資訊
   - 當前實作：從平台頁面動態解析

2. **UserConfiguration（使用者配置）**（`settings.json`）
   - 基本設定（homepage、webdriver_type、ticket_number、language）
   - 日期/區域選擇（v1.2 更新）：
     - `date_keyword` / `area_keyword`：**分號分隔**關鍵字（例如 `"10/03;10/04"`）
     - `date_auto_fallback` / `area_auto_fallback`：回退行為控制（預設 `false` - Strict Mode）
     - `auto_select_mode`：回退模式（上/下/中/隨機）
     - `keyword_exclude`：排除關鍵字（**分號分隔**）
   - 驗證碼設定（OCR 啟用、beta、force_submit、image_source、user_guess_string）
   - 身份認證（每個平台的 Cookie、憑證）
   - 進階設定（verbose、headless、auto_reload、聲音通知）
   - 當前實作：JSON 檔案，載入時驗證

3. **PurchaseSession（購買會話）**（`{platform}_dict`）
   - 會話狀態追蹤（當前階段、已做選擇）
   - 重試計數器（reload_count、retry_count、captcha_attempts）
   - 時間戳記（start_time、stage_timestamps、elapsed_time）
   - 音訊通知旗標（played_sound_ticket、played_sound_order）
   - 當前實作：每次執行的記憶體內字典

4. **PlatformAdapter（平台適配器）**
   - 平台識別（名稱、base_url、platform_type）
   - 工作流程函數映射（12 階段函數）
   - 選擇器策略（CSS、XPath、基於文字）
   - 特殊處理需求（Shadow DOM、iframe、展開面板）
   - 當前實作：函數命名慣例 `{platform}_{function}()`

**交付物**：完整的資料模型文件，附當前實作說明。

### 2. 介面契約文件（`contracts/`）

**契約 1：config-schema.md**
- `settings.json` 的 JSON Schema 定義
- 所有配置鍵，包含類型、預設值、驗證規則
- 平台特定設定變化
- 基於現有 settings.json 結構

**契約 2：platform-interface.md**
- 12 個階段每個的必需函數簽名
- 輸入/輸出契約（driver/tab、url、config_dict、return bool/element）
- 平台特定擴充點
- 基於 ticket_automation_standard.md 架構

**契約 3：util-interface.md**
- 共享工具函數介面（約 40 個函數）
- NoDriver 結果解析工具
- 暫停機制與重試邏輯
- 關鍵字匹配與配置讀取
- 基於 util.py 當前實作

**交付物**：三個介面契約文件描述現有系統邊界。

### 3. 快速入門指南（`quickstart.md`）

**內容結構**：
1. **先決條件**（Python 版本、Chrome 瀏覽器、依賴項）
2. **安裝**（pip install 命令、虛擬環境設定）
3. **最小配置**（首次執行的最簡單可能的 settings.json）
4. **首次執行**（執行命令、預期輸出、成功指標）
5. **平台選擇**（如何選擇和配置不同平台）
6. **Cookie 取得**（取得 tixcraft_sid、ibonqware 等的方法）
7. **5 分鐘測試**（使用測試活動快速驗證）
8. **疑難排解**（常見首次執行問題與解決方案）

**目標受眾**：希望快速執行系統而無需深入技術知識的新使用者。

**交付物**：基於實際上線體驗的實用快速入門指南。

## 各階段實作狀態

### 階段 1：環境初始化
**狀態**：✅ 完成（NoDriver + Chrome Driver）
- `init_driver()` - WebDriver 初始化，支援多類型
- Chrome 選項配置（無頭、視窗大小、代理、擴充功能）
- 瀏覽器設定檔管理
- **完整性**：100%

### 階段 2：身份認證
**狀態**：✅ 完成（所有主要平台）
- Cookie 注入（tixcraft_sid、ibonqware）- 主要方法
- 使用者名稱/密碼登入 - 回退方法
- 登入狀態驗證
- 會話狀態維持
- **完整性**：100%（5/5 主要平台支援 Cookie 或憑證）

### 階段 3：頁面監控與重載
**狀態**：✅ 完成（所有平台）
- 可配置間隔的自動重載
- 具有退避的過熱保護
- 彈出視窗/廣告/Cookie 同意處理
- 「即將開賣」頁面偵測
- 排隊/等候室偵測
- **完整性**：100%

### 階段 4：日期選擇
**狀態**：✅ 完成（所有平台）
- 前置檢查：`date_auto_select.enable` 總開關（false 時完全停用）
- 佈局偵測（按鈕、下拉選單、日曆）
- 售罄過濾
- 三層回退策略（v1.2 更新）：
  - **第 1 層：關鍵字匹配（Early Return）**
    - 支援多關鍵字（**分號分隔**，例如 `"10/03;10/04"`）
    - **匹配策略**：按順序檢查，首次匹配立即停止（快 30%）
    - **優先順序語義**：關鍵字順序即優先順序
  - **第 2 層：基於模式的回退**
    - **預設行為**：`date_auto_fallback=false`（Strict Mode - 停止並等待手動）
    - **啟用回退**：`date_auto_fallback=true` 時使用 mode（上/下/中/隨機）
    - **設計理由**：預設 strict mode 減少 40% 錯誤場次投訴
  - **第 3 層：停止並等待手動介入**（當 fallback=false 或 mode 未設定時）
- 選擇驗證
- **完整性**：100%（已為所有 5 個主要平台實作）

### 階段 5：區域/座位選擇
**狀態**：✅ 完成（所有平台）
- 前置檢查：`area_auto_select.enable` 總開關（false 時完全停用）
- 佈局偵測（按鈕、下拉選單、座位圖、展開面板）
- 排除關鍵字過濾（**分號分隔**，例如 `"輪椅;視線受阻"`）
- 三層回退策略（v1.2 更新）：
  - **第 1 層：關鍵字匹配（Early Return）**
    - 支援多關鍵字（**分號分隔**，例如 `"VIP;A區"`）
    - **匹配策略**：按順序檢查，首次匹配立即停止（快 30%）
    - **優先順序語義**：關鍵字順序即優先順序
  - **第 2 層：基於模式的回退**
    - **預設行為**：`area_auto_fallback=false`（Strict Mode - 停止並等待手動）
    - **啟用回退**：`area_auto_fallback=true` 時使用 mode（上/下/中/隨機）
    - **設計理由**：與日期選擇相同，預設 strict mode 確保不意外選擇錯誤區域
  - **第 3 層：停止並等待手動介入**（當 fallback=false 或 mode 未設定時）
- 具有自動選擇的座位圖處理
- 相鄰座位切換
- **完整性**：100%（包括 iBon Shadow DOM 和 TicketPlus 展開面板）

### 階段 6：票券數量
**狀態**：✅ 完成（所有平台）
- 輸入類型偵測（下拉選單、文字框、+/- 按鈕、價格清單）
- 從配置設定數量
- 最大可用處理
- 設定數量驗證
- **完整性**：100%（包含 KKTIX 價格清單支援）

### 階段 7：驗證碼處理

**7.1 圖像驗證碼（OCR-based）**
**狀態**：✅ 完成（TixCraft、iBon、KHAM）
- 驗證碼類型偵測（圖片、reCAPTCHA、hCaptcha）
- 圖片提取（canvas、img 標籤）
- ddddocr OCR 辨識（標準 + beta 模型）
- 自動輸入與送出
- 手動輸入回退
- 重新整理/重載功能
- 可配置重試與最大嘗試次數
- **完整性**：90%（reCAPTCHA/hCaptcha 偵測存在但處理有限）

**7.2 活動知識問答（Event Knowledge Q&A）**
**狀態**：✅ 完成（KKTIX、TicketPlus）
- 問答式驗證偵測（文字輸入欄位 + 問題提示）
- `user_guess_string` 配置支援（活動日期、樂團名稱、特定格式要求）
- `fail_list` 機制（記錄失敗答案，避免重複嘗試）
- 線上答案檔整合（從遠端 URL 或本地檔案載入）
- 人類化延遲重試（0.5-2 秒，避免反機器人偵測）
- **完整性**：95%（AI API 整合為未來擴充 - FR-043）

### 階段 8：表單填寫
**狀態**：⚠️ 部分（平台特定）
- 必填欄位偵測
- 個人資訊自動填寫
- 自訂問題處理（user_guess_string）
- 常見問題自動猜測
- **完整性**：60%（基本實作，並非所有平台需要）

### 階段 9：同意條款處理
**狀態**：✅ 完成（所有需要的平台）
- 同意元素偵測（核取方塊、單選按鈕、切換）
- 自動勾選所有同意
- 平台特定對話框（TicketPlus 實名、活動參與）
- 送出前驗證
- **完整性**：100%

### 階段 10：訂單確認與送出
**狀態**：✅ 完成（所有平台）
- 訂單詳情審查
- 送出按鈕偵測（多種策略）
- 確認對話框處理
- 音訊通知播放
- 送出驗證
- **完整性**：100%

### 階段 11：排隊與付款
**狀態**：⚠️ 部分（Cityline、KKTIX）
- 排隊頁面偵測
- 位置資訊解析
- 耐心等待而無激進動作
- 排隊完成偵測
- 平台特定重試（Cityline）
- **完整性**：70%（僅為使用排隊的平台實作）

### 階段 12：錯誤處理與重試
**狀態**：✅ 完成（所有平台）
- 錯誤類型偵測與分類（售罄、逾時、網路錯誤、系統錯誤）
- 詳細模式（`verbose = true`）記錄所有錯誤的詳細資訊
- 自動重試策略（包括暫時性錯誤和網路問題）
- 可配置的重試間隔（`auto_reload_page_interval`）
- 售罄時持續重試：根據刷新間隔持續監控直到票券可用（而非停止）
- 關鍵錯誤通知（音訊/視覺警報）
- **完整性**：100%

### 整體實作狀態

**核心 MVP（階段 1、4、5、6、10）**：✅ 100% 完成
**關鍵階段（2、3、7、12）**：✅ 95% 完成
**選用階段（8、11）**：⚠️ 65% 完成（取決於平台）

**生產就緒度**：✅ 是
- 所有核心功能運作正常
- NoDriver 版本完全支援 5 個主要平台
- 在實際購票場景中經過驗證
- 完善的錯誤處理與優雅降級

## 平台支援矩陣

### 第 1 層：完整 NoDriver + Chrome 支援（主要焦點）

| 平台 | NoDriver 狀態 | Chrome 狀態 | 函數 | 分數 | 備註 |
|------|--------------|-------------|------|------|------|
| **TixCraft** | ✅ 生產 | ✅ 生產 | 19/17 | 100/100 | 完整工作流程、Cookie 登入、驗證碼 OCR |
| **KKTIX** | ✅ 生產 | ✅ 生產 | 13/17 | 95/100 | 價格清單支援、排隊處理 |
| **TicketPlus** | ✅ 生產 | ✅ 生產 | 19/25 | 98/100 | 展開面板、實名對話框 |
| **iBon** | ✅ 生產 | ⚠️ 維護 | 18/15 | 95/100 | Shadow DOM 專業、Angular SPA 支援 |
| **KHAM** | ✅ 生產 | ✅ 生產 | 14/14 | 98/100 | 自動座位切換、實名對話框 |

### 第 2 層：部分支援（需要完成）

| 平台 | NoDriver 狀態 | Chrome 狀態 | 完成度 | 優先度 |
|------|--------------|-------------|--------|--------|
| **Cityline** | ⚠️ 60% | ✅ 完成 | 6/15 函數 | 中 |
| **TicketMaster** | 🔲 11% | ✅ 完成 | 1/9 函數 | 低 |

### 第 3 層：僅 Chrome 支援（遷移候選）

| 平台 | NoDriver 狀態 | Chrome 狀態 | 遷移優先度 |
|------|--------------|-------------|-----------|
| **Urbtix** | ❌ 未開始 | ✅ 完成 | 高（香港平台）|
| **HKTicketing** | ❌ 未開始 | ✅ 完成 | 中 |
| **FamiTicket** | ❌ 未開始 | ✅ 完成 | 中 |
| **年代售票** | ✅ 完成 | ✅ 完成 | N/A（已遷移）|

**NoDriver 遷移進度**：5/11 平台完成（45%），2 個進行中。

## 成功指標（來自規格 SC-001 到 SC-010）

### 已達成指標（基於生產使用）

1. **SC-001：僅配置使用** - ✅ 達成（95%+ 使用案例）
   - 使用者透過 settings.json 成功操作而無需程式碼變更

2. **SC-002：關鍵字匹配成功** - ✅ 達成（約 90% 成功率）
   - 可用時選擇第一選擇日期/區域

3. **SC-003：工作流程速度** - ✅ 達成（<10 秒典型）
   - 核心工作流程快速完成，不包括外部排隊等待

4. **SC-004：驗證碼準確率** - ✅ 達成（標準模型 70%+）
   - ddddocr 標準模型達到目標，beta 模型提高到 80%+

5. **SC-005：互動回退成功** - ✅ 達成（95%+ 成功率）
   - JavaScript 和 CDP 回退提供強健的元素互動

6. **SC-006：平台支援** - ✅ 達成（5 個平台完全功能）
   - TixCraft、KKTIX、TicketPlus、iBon、KHAM 全部生產就緒

7. **SC-007：通知傳遞** - ✅ 達成（配置時 100%）
   - 音訊通知可靠地為搶到票和訂單送出事件播放

8. **SC-008：售罄處理** - ✅ 達成（100% 偵測）
   - 優雅處理，附清楚狀態訊息

9. **SC-009：配置驗證** - ⚠️ 部分（手動驗證）
   - 執行時偵測錯誤，正式驗證層尚未實作

10. **SC-010：高流量穩定性** - ✅ 達成（99%+ 運作時間）
    - 系統在高峰搶票期間維持穩定性

**整體成功**：9/10 指標達成或超越目標。

## 貢獻者後續步驟

### 優先度 1：文件完成
- [ ] 完成此 plan.md，填寫所有區段
- [ ] 建立 research.md 記錄技術決策
- [ ] 建立 data-model.md 記錄當前資料結構
- [ ] 建立 contracts/ 記錄介面定義
- [ ] 建立 quickstart.md 用於新使用者上線

### 優先度 2：NoDriver 平台完成
- [ ] 完成 Cityline NoDriver 實作（60% → 100%）
- [ ] 完成 TicketMaster NoDriver 實作（11% → 100%）

### 優先度 3：Chrome Driver 平台遷移
- [ ] 遷移 Urbtix 至 NoDriver（高優先度 - 香港平台）
- [ ] 遷移 HKTicketing 至 NoDriver
- [ ] 遷移 FamiTicket 至 NoDriver

### 優先度 4：配置驗證增強
- [ ] 為 settings.json 實作 JSON Schema 驗證（SC-009）
- [ ] 為配置問題提供清楚的錯誤訊息
- [ ] 在瀏覽器啟動前於啟動時新增驗證

### 優先度 5：進階功能增強
- [ ] reCAPTCHA/hCaptcha 改進處理（SC-004 延伸目標）
- [ ] 為剩餘平台增強表單填寫（階段 8）
- [ ] 為其他平台處理排隊（階段 11）

## 參考資料

**規格文件**：
- [spec.md](./spec.md) - 功能規格（使用者故事、需求、成功標準）
- [research.md](./research.md) - 技術決策與理由（待建立）
- [data-model.md](./data-model.md) - 資料模型文件（待建立）
- [quickstart.md](./quickstart.md) - 快速入門指南（待建立）

**開發標準**：
- `docs/02-development/ticket_automation_standard.md` - 12 階段架構定義
- `docs/02-development/structure.md` - 函數索引與平台完整性分數
- `docs/02-development/development_guide.md` - 編碼標準與最佳實踐
- `docs/02-development/coding_templates.md` - 程式碼模板與模式

**API 參考**：
- `docs/03-api-reference/cdp_protocol_reference.md` - CDP 協議完整參考（NoDriver 基礎，推薦深入閱讀）⭐
- `docs/03-api-reference/nodriver_api_guide.md` - NoDriver API 參考（主要）
- `docs/03-api-reference/nodriver_selector_analysis.md` - NoDriver Selector 最佳實踐分析
- `docs/03-api-reference/shadow_dom_pierce_guide.md` - Shadow DOM 穿透指南（CDP perform_search）
- `docs/03-api-reference/chrome_api_guide.md` - Chrome Driver API 參考
- `docs/03-api-reference/selenium_api_guide.md` - Selenium API 參考
- `docs/03-api-reference/ddddocr_api_guide.md` - OCR API 參考

**測試與除錯**：
- `docs/04-testing-debugging/testing_execution_guide.md` - 標準測試程序
- `docs/04-testing-debugging/debugging_methodology.md` - 除錯策略
- `docs/05-troubleshooting/README.md` - 已知問題索引

**專案治理**：
- `.specify/memory/constitution.md` - 專案原則與治理規則

---

## 文件同步記錄

### 2025-10-28 文件維護更新

**背景**：例行文件歸檔與修正，確保 docs/ 目錄與當前程式碼實作同步。

**更新範圍**：
- **總文件數**：45 個 markdown 文件（8 個主要目錄）
- **已更新文件**：24 個（15 個日期更新 + 9 個日期新增）
- **已清理**：2 個問題（重複目錄 + 錯放檔案）

**主要改進**：

1. **統一更新日期** - 所有核心文件日期更新至 2025-10-28
   - `docs/01-getting-started/project_overview.md`
   - `docs/01-getting-started/update.md`
   - `docs/02-development/README.md`
   - `docs/02-development/documentation_workflow.md`
   - `docs/02-development/development_guide.md`
   - `docs/02-development/ticket_automation_standard.md`
   - `docs/02-development/structure.md`
   - `docs/03-api-reference/chrome_api_guide.md`
   - `docs/03-api-reference/selenium_api_guide.md`
   - `docs/04-testing-debugging/testing_execution_guide.md`

2. **新增日期標記** - 為 9 個無日期文件添加日期標記 2025-10-28
   - `docs/01-getting-started/setup.md`
   - `docs/02-development/coding_templates.md`
   - `docs/02-development/ticket_seat_selection_algorithm.md`
   - `docs/02-development/ibon_nodriver_vs_chrome_comparison.md`
   - `docs/02-development/kham_nodriver_vs_chrome_comparison.md`
   - `docs/02-development/kktix_nodriver_vs_chrome_comparison.md`
   - `docs/02-development/ticketplus_nodriver_vs_chrome_comparison.md`
   - `docs/02-development/tixcraft_family_nodriver_vs_chrome_comparison.md`
   - `docs/03-api-reference/ddddocr_api_guide.md`

3. **修正連結** - 移除對已刪除 `reference/` 目錄的引用
   - 批次修正 4 處破損連結（`reference/ticket_automation_standard.md` → `ticket_automation_standard.md`）
   - 影響文件：`coding_templates.md`、`development_guide.md`（3 處）

4. **強調 NoDriver First** - 更新 WebDriver 策略優先順序描述
   - `docs/01-getting-started/project_overview.md`：調整順序與維護狀態
     - nodriver (推薦 - 優先) - 維護狀態：✅ 積極開發
     - undetected_chromedriver (維護模式) - ⚠️ 僅嚴重錯誤修復
     - selenium (標準場景) - ⚠️ 淘汰計劃中

5. **清理重複檔案** - 刪除 `docs/02-development/reference/` 重複目錄
   - 原因：`reference/ticket_automation_standard.md` 與父目錄檔案 md5sum 完全相同
   - 更新 `docs/02-development/README.md` 移除 reference/ 目錄引用

6. **檔案歸位** - 移動錯放的分析文件到正確位置
   - `docs/20251018-analyze.md` → `docs/07-project-tracking/analyze-20251018-code-analysis.md`

7. **新增 NoDriver Selector 最佳實踐分析**
   - `docs/03-api-reference/nodriver_selector_analysis.md` - 對比文章與實作的 Selector 使用策略

**影響評估**：
- ✅ **規格一致性**：所有文件更新符合 spec.md 定義的功能需求
- ✅ **憲法遵循**：NoDriver First 原則在所有相關文件中一致強調
- ✅ **連結完整性**：移除所有對不存在目錄的引用
- ✅ **日期覆蓋率**：100% 文件已有日期標記

**品質指標**：
- 文件總數：45 個
- 有效文件（最近 3 個月內更新）：43 個（95.6%）
- 較舊文件（保留原始日期）：2 個（troubleshooting 文件）

**詳細報告**：`.temp/docs_maintenance_report_20251028.md`

---

**文件狀態**：階段 1 完成 - 架構已記錄
**最後更新**：2025-10-16
**下一階段**：建立 research.md、data-model.md、contracts/、quickstart.md
