# 實作計畫：關鍵字優先選擇與條件式自動遞補

**分支**：`feature/003-keyword-priority-fallback` | **日期**：2025-10-31 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/003-keyword-priority-fallback/spec.md` 的功能規格說明

**注意**：本範本由 `/speckit.plan` 指令填寫。執行流程請參見 `.specify/templates/commands/plan.md`。

## 摘要

本功能對現有的日期與區域選擇邏輯進行重構，主要變更包括：

1. **關鍵字優先匹配（早期返回）**: 從「掃描全部關鍵字後再選擇」改為「第一個匹配立即選擇並停止」，平均節省 30% 的匹配時間
2. **條件式自動遞補**: 新增兩個布林開關（`date_auto_fallback` / `area_auto_fallback`），當所有關鍵字都未匹配時，控制是否觸發自動遞補選擇
3. **嚴格模式預設**: 預設值為 `false`（嚴格模式），僅選擇關鍵字匹配的選項，避免誤搶不想要的場次
4. **UI 控制項**: 在 `settings.html` 新增兩個核取方塊，讓使用者可視覺化調整遞補開關

**技術方案**（來自 research.md）:
- 使用早期返回（Early Return）模式，一旦第一個關鍵字匹配成功立即返回
- 使用頂層獨立欄位（`date_auto_fallback` / `area_auto_fallback`）而非巢狀結構
- 日誌訊息採用英文輸出，避免 Windows cp950 編碼問題
- 舊程式碼註解並標記 DEPRECATED，保留 2 週後移除

## 技術上下文 (Technical Context)

**語言/版本**：Python 3.7+（專案既有需求）
**主要相依性 (dependency)**：
- NoDriver（優先，反偵測能力最強）
- Undetected Chrome（舊版回退）
- Bootstrap 5.3.8（UI 框架）

**儲存方式**：JSON 配置檔（`src/settings.json`）
**測試**：
- 手動執行測試（`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`）
- 日誌檢查（`grep "[DATE KEYWORD]" .temp/test_output.txt`）

**目標平台**：
- TixCraft（主要）
- KKTIX、iBon、TicketPlus、KHAM、FamiTicket（共用邏輯）

**專案類型**：Single project（Python 自動化腳本）
**效能目標**：
- 關鍵字匹配時間節省 30%（early return 效果）
- 日期/區域選擇完成時間 <500ms（既有標準）

**限制條件**：
- Windows cp950 編碼限制（日誌必須使用英文）
- 向後相容性（舊版設定檔必須正常運作）
- NoDriver 優先（Chrome 版本進入維護模式）

**規模/範圍**：
- 修改函數數量：2-3 個（日期選擇、區域選擇）
- 新增設定欄位：2 個（`date_auto_fallback`, `area_auto_fallback`）
- 新增 UI 控制項：2 個核取方塊
- 影響平台數量：6 個（所有支援平台）

## 專案憲章檢查 (Constitution Check)

*GATE：必須通過後才能進入 Phase 0 研究階段。Phase 1 設計後需再次檢查。*

### 檢查點 1：NoDriver First（憲章第 I 條）

**狀態**: ✅ **通過**

**說明**: 本功能是邏輯重構，修改的是共用選擇邏輯，對所有引擎（NoDriver / UC / Selenium）通用。根據憲章：
- 優先修改 NoDriver 版本（`nodriver_tixcraft.py`） ✅
- Chrome 版本（`chrome_tixcraft.py`）不在修改範圍內，符合「進入維護模式」方針 ✅

**無違規**。

---

### 檢查點 2：資料結構優先（憲章第 II 條）

**狀態**: ✅ **通過**

**設計流程**:
1. ✅ 已完成 `data-model.md`，定義核心實體（Configuration, KeywordMatchResult）
2. ✅ 已完成 `contracts/config-schema.md`，定義設定檔結構擴展
3. ✅ 實作將完全符合資料模型定義

**無違規**。

---

### 檢查點 3：三問法則（憲章第 III 條）

**問題 1：是核心問題嗎？**
✅ **是**。日期與區域選擇是搶票流程的核心環節，直接影響搶票成功率。

**問題 2：有更簡單的方法嗎？**
✅ **已選擇最簡單方案**。早期返回模式（Early Return）是最簡潔的實作方式，已在 `research.md` 中評估過其他替代方案（掃描全部後篩選、Generator 模式）並拒絕。

**問題 3：會破壞相容性嗎？**
✅ **不會**。預設值設為 `false`，舊版設定檔升級後行為符合使用者預期（嚴格模式：僅選擇關鍵字匹配的選項）。使用 `.get('date_auto_fallback', False)` 安全存取，確保向後相容。

**無違規**。

---

### 檢查點 4：單一職責與可組合性（憲章第 IV 條）

**狀態**: ✅ **通過**

**函數設計**:
- 關鍵字匹配邏輯與遞補邏輯分離為獨立函數
- 函數命名清晰（如 `select_date_by_keyword()` / `select_date_by_fallback()`）
- 每個函數職責單一（匹配 vs 遞補）

**無違規**。

---

### 檢查點 5：設定驅動開發（憲章第 V 條）

**狀態**: ✅ **通過**

**配置架構**:
- ✅ 新增欄位完全由 `settings.json` 控制
- ✅ 已定義 JSON schema（`contracts/config-schema.md`）
- ✅ UI 控制項同步至設定檔
- ✅ 無硬寫值於程式碼中

**無違規**。

---

### 檢查點 6：測試驅動穩定性（憲章第 VI 條）

**狀態**: ✅ **通過**

**測試計畫**:
- ✅ 實作完成後執行實際搶票測試（30 秒 timeout）
- ✅ 驗證日誌輸出（檢查關鍵字匹配過程、遞補觸發）
- ✅ 測試邊界情境（空白關鍵字、主開關停用、舊版設定檔）

**無違規**。

---

### 檢查點 7：MVP 原則（憲章第 VII 條）

**狀態**: ✅ **通過**

**優先級分類**:
- **P1 (MVP)**: 核心邏輯變更（早期返回 + 遞補機制）
- **P2**: UI 控制項（非必要，可先透過手動編輯 settings.json）

**實作順序**:
1. Phase 1：核心邏輯（FR-001 至 FR-018）
2. Phase 2：UI 控制項（FR-019 至 FR-022）

**無違規**。

---

### 檢查點 8：文件與代碼同步（憲章第 VIII 條）

**狀態**: ✅ **通過**

**同步計畫**:
- ✅ 已建立完整的 spec.md、research.md、data-model.md、contracts/、quickstart.md
- ✅ 實作完成後需更新 `CHANGELOG.md`（記錄功能變更與遷移指南）
- ✅ 需更新 `docs/02-development/structure.md`（若新增函數）

**無違規**。

---

### 檢查點 9：Git 提交規範（憲章第 IX 條）

**狀態**: ✅ **通過**

**提交策略**:
- 使用 Conventional Commits 格式（`feat(nodriver): add early return for keyword matching`）
- 分支命名：`feature/003-keyword-priority-fallback` ✅
- 提交訊息英文，主題行限制 50 字符

**無違規**。

---

### 憲章檢查結論

**✅ 所有檢查點通過，無違規項目。本功能可進入實作階段。**

## 專案結構

### 文件（本功能）

```
specs/003-keyword-priority-fallback/
├── spec.md                  # 功能規格說明（已完成）
├── plan.md                  # 本文件（/speckit.plan 輸出）
├── research.md              # Phase 0 輸出（技術研究與決策）
├── data-model.md            # Phase 1 輸出（資料結構設計）
├── quickstart.md            # Phase 1 輸出（快速開始指南）
├── contracts/               # Phase 1 輸出（API 契約）
│   └── config-schema.md     # 設定檔結構擴展
└── tasks.md                 # Phase 2 輸出（/speckit.tasks 指令 - 尚未建立）
```

### 原始碼（repository 根目錄）

```
tickets_hunter/
├── src/
│   ├── nodriver_tixcraft.py       # [修改] 日期與區域選擇邏輯
│   ├── settings.py                # [修改] get_default_config() 新增欄位
│   ├── settings_old.py            # [修改] get_default_config() 新增欄位 + tkinter GUI 核取方塊 + 多語言支援
│   └── settings.json              # [擴展] 新增 date_auto_fallback 和 area_auto_fallback
│
├── settings.html                  # [修改] 新增兩個核取方塊（網頁版 UI）
│
├── tests/
│   └── integration/
│       └── test_keyword_priority_fallback.py  # [新增] 整合測試（可選）
│
├── docs/
│   └── 07-project-tracking/
│       └── CHANGELOG.md           # [更新] 記錄功能變更
│
└── specs/003-keyword-priority-fallback/  # [本功能規格目錄]
```

**結構決策**: 本專案為 Single project（Python 自動化腳本），採用扁平式目錄結構，所有核心邏輯集中於 `src/` 目錄。選擇此結構是因為：
1. 專案規模中等（<10k 行程式碼）
2. 單一語言（Python）
3. 無前後端分離需求
4. 符合專案既有架構

## 複雜度追蹤

*僅在專案憲章檢查（Constitution Check）有違規且必須說明時填寫*

**本功能無違規項目，此表格留空。**

---

## Phase 0：大綱與研究（已完成）

**輸出**: `research.md`

**完成的研究任務**:
1. ✅ 關鍵字匹配邏輯的實作策略（決策：Early Return 模式）
2. ✅ 新增布林參數的設定檔整合策略（決策：頂層獨立欄位）
3. ✅ UI 控制項的設計與位置（決策：對應區塊各新增一個核取方塊）
4. ✅ 日誌訊息格式與詳細程度（決策：結構化英文日誌）
5. ✅ 舊邏輯的移除策略（決策：逐步重構，標記 DEPRECATED）

**關鍵決策摘要**:
- 採用早期返回（Early Return）模式，一旦第一個關鍵字匹配成功立即返回
- 新增頂層欄位 `date_auto_fallback` / `area_auto_fallback`，預設值為 `false`
- UI 核取方塊放在對應的「日期自動點選」和「區域自動點選」區塊下
- 日誌訊息使用英文，避免 Windows cp950 編碼問題
- 舊程式碼註解並標記 DEPRECATED，保留 2 週後完全移除

---

## Phase 1：設計與契約（已完成）

**輸出**: `data-model.md`, `contracts/config-schema.md`, `quickstart.md`

### 資料模型摘要（data-model.md）

**核心實體**:

1. **Configuration（設定檔）**:
   - `date_auto_fallback` (Boolean, 預設 `false`): 日期自動遞補開關
   - `area_auto_fallback` (Boolean, 預設 `false`): 區域自動遞補開關
   - 相關欄位：`date_keyword`, `area_keyword`, `date_select_order`, `area_select_order`

2. **KeywordMatchResult（關鍵字匹配結果）**（概念性，用於理解流程）:
   - `matched` (Boolean): 是否有關鍵字匹配成功
   - `matched_keyword` (String/Null): 匹配成功的關鍵字內容
   - `matched_index` (Integer/Null): 匹配成功的關鍵字索引
   - `selected_option` (String/Null): 最終選擇的選項內容
   - `is_fallback` (Boolean): 最終選擇是否來自遞補邏輯

**狀態轉換邏輯**:
```
[Start] → [Iterate Keywords]
    → [Keyword Matched?] --Yes--> [State: Full Match] → [End]
    → [More Keywords?] --No--> [All Keywords Failed]
        → [Check Fallback Flag]
            --true--> [State: Fallback Selection] → [End]
            --false--> [State: No Selection] → [End]
```

**資料不變性約束**:
1. 關鍵字順序不可變（代表優先順序）
2. 遞補開關的語意一致性（僅控制「全部未匹配」時的行為）
3. 狀態轉換的單向性（一旦進入 Full Match 狀態，不得回退）

### API 契約摘要（contracts/config-schema.md）

**新增欄位**:

1. **`date_auto_fallback`**:
   - 類型：`boolean`
   - 預設值：`false`
   - 行為：
     - `true`: 所有日期關鍵字都未匹配時，根據 `date_select_order` 自動選擇可用日期
     - `false`: 所有日期關鍵字都未匹配時，不自動選擇，等待手動介入

2. **`area_auto_fallback`**:
   - 類型：`boolean`
   - 預設值：`false`
   - 行為：
     - `true`: 所有區域關鍵字都未匹配時，根據 `area_select_order` 自動選擇可用區域
     - `false`: 所有區域關鍵字都未匹配時，不自動選擇，等待手動介入

**向後相容性**:
- 使用 `.get('date_auto_fallback', False)` 安全存取
- 舊版設定檔升級後預設為嚴格模式（`false`）
- 無破壞性變更

**實作需求**:
1. `settings.py` / `settings_old.py`：更新 `get_default_config()` 函數
2. `nodriver_tixcraft.py`：安全存取模式 + 結構化日誌
3. `settings.html`：新增兩個核取方塊 + JavaScript 同步邏輯

---

## Phase 2：任務生成（待執行 /speckit.tasks）

**下一步**: 執行 `/speckit.tasks` 指令，根據本計畫生成可執行的 `tasks.md`。

**預期任務分類**:
1. **核心邏輯實作**（P1）:
   - 修改日期選擇邏輯（早期返回模式）
   - 修改區域選擇邏輯（早期返回模式）
   - 實作條件式遞補邏輯（檢查開關 + 觸發遞補）
   - 新增結構化日誌訊息（英文）
   - 註解舊程式碼並標記 DEPRECATED

2. **設定檔擴展**（P1）:
   - 更新 `settings.py` 的 `get_default_config()` 函數
   - 更新 `settings_old.py` 的 `get_default_config()` 函數

3. **UI 控制項**（P2）:
   - **網頁版 (settings.html)**:
     - 在 `settings.html` 新增「日期自動遞補」核取方塊
     - 在 `settings.html` 新增「區域自動遞補」核取方塊
     - 實作 JavaScript 載入/儲存邏輯
   - **桌面版 (settings_old.py tkinter GUI)**:
     - 在日期自動選擇區塊新增「日期自動遞補」核取方塊（chk_date_auto_fallback），緊接在主開關下方
     - 在區域自動選擇區塊新增「區域自動遞補」核取方塊（chk_area_auto_fallback），緊接在主開關下方
     - 實作完整多語言支援（en_us, zh_tw, ja_jp）
     - 實作 tooltip 顯示完整說明文字
     - 實作 tkinter 核取方塊載入/儲存邏輯

4. **測試與驗證**（P1）:
   - 執行實際搶票測試（30 秒 timeout）
   - 驗證日誌輸出（關鍵字匹配過程、遞補觸發）
   - 測試邊界情境（空白關鍵字、主開關停用、舊版設定檔）

5. **文件更新**（P2）:
   - 更新 `CHANGELOG.md`（記錄功能變更）
   - 更新 `docs/02-development/structure.md`（若新增函數）

---

## 測試策略

### 單元測試（可選，時間允許時執行）

1. **測試 `get_default_config()` 包含新欄位**:
   ```python
   config = get_default_config()
   assert "date_auto_fallback" in config
   assert config["date_auto_fallback"] == False
   ```

2. **測試安全存取模式**:
   ```python
   old_config = {"date_keyword": "11/16"}  # 舊版設定檔
   date_auto_fallback = old_config.get('date_auto_fallback', False)
   assert date_auto_fallback == False
   ```

### 整合測試（必須執行）

1. **測試案例 1：第一個關鍵字匹配**:
   - 設定：`date_keyword = "11/16;11/17;11/18"`，頁面有 "11/16" 和 "11/19"
   - 預期：選擇 "11/16"，日誌顯示 "Keyword #1 matched"

2. **測試案例 2：第二個關鍵字匹配**:
   - 設定：`date_keyword = "11/16;11/17;11/18"`，頁面僅有 "11/17" 和 "11/19"
   - 預期：選擇 "11/17"，日誌顯示 "Keyword #2 matched"

3. **測試案例 3：全部未匹配，遞補啟用**:
   - 設定：`date_keyword = "11/16;11/17"`，`date_auto_fallback = true`，頁面有 "11/18" 和 "11/19"
   - 預期：選擇 "11/18"，日誌顯示 "date_auto_fallback=true, triggering auto fallback"

4. **測試案例 4：全部未匹配，遞補停用**:
   - 設定：`date_keyword = "11/16;11/17"`，`date_auto_fallback = false`，頁面有 "11/18" 和 "11/19"
   - 預期：不選擇任何日期，日誌顯示 "date_auto_fallback=false, fallback is disabled"

### 測試指令

**Windows CMD**:
```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

**驗證日誌**:
```bash
# 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
```

---

## 風險與緩解措施

### 風險 1：邏輯變更導致非預期行為

**可能性**: 中
**影響**: 高（影響所有平台的搶票成功率）

**緩解措施**:
- ✅ 保留舊程式碼作為註解，標記 DEPRECATED
- ✅ 執行實際搶票測試驗證新邏輯
- ✅ 使用結構化日誌，便於除錯
- ✅ 若發現問題，可快速回滾至舊邏輯

### 風險 2：設定檔相容性問題

**可能性**: 低
**影響**: 中（舊版使用者升級後行為改變）

**緩解措施**:
- ✅ 提供預設值 `false`（嚴格模式），與使用者預期一致
- ✅ 在 CHANGELOG.md 記錄新增欄位與遷移指南
- ✅ UI 核取方塊明確說明功能

### 風險 3：日誌輸出過多影響效能

**可能性**: 低
**影響**: 低（日誌僅在關鍵路徑輸出）

**緩解措施**:
- ✅ 日誌訊息簡潔明確，僅輸出關鍵決策點
- ✅ 可在 `verbose` 模式下啟用詳細日誌
- ✅ 使用結構化前綴（如 `[DATE KEYWORD]`），便於過濾

---

## 交付標準

### 核心功能（P1）

1. ✅ 日期選擇邏輯實作早期返回模式
2. ✅ 區域選擇邏輯實作早期返回模式
3. ✅ 條件式遞補邏輯實作並正確檢查開關
4. ✅ 結構化日誌訊息（英文）輸出
5. ✅ 舊程式碼註解並標記 DEPRECATED
6. ✅ `settings.py` 和 `settings_old.py` 更新預設值
7. ✅ 通過所有整合測試案例

### UI 控制項（P2）

**網頁版 (settings.html)**:
8. ✅ `settings.html` 新增兩個核取方塊
9. ✅ JavaScript 載入/儲存邏輯正確同步

**桌面版 (settings_old.py tkinter GUI)**:
10. ✅ `settings_old.py` 新增兩個 tkinter 核取方塊（chk_date_auto_fallback、chk_area_auto_fallback）
11. ✅ 多語言支援實作完成（en_us, zh_tw, ja_jp）
12. ✅ tooltip 說明文字正確顯示
13. ✅ tkinter 核取方塊載入/儲存邏輯正確同步

### 文件（P2）

14. ✅ `CHANGELOG.md` 記錄功能變更與遷移指南
15. ✅ `docs/02-development/structure.md` 更新（若有新增函數）

---

## 時程估算

**Phase 1（核心邏輯）**: 2-3 小時
- 修改日期選擇邏輯：1 小時
- 修改區域選擇邏輯：1 小時
- 更新設定檔預設值：0.5 小時
- 整合測試：0.5 小時

**Phase 2（UI 控制項）**: 2-3 小時
- **網頁版 (settings.html)**：1-1.5 小時
  - 新增核取方塊：0.5 小時
  - JavaScript 同步邏輯：0.5 小時
  - UI 測試：0.5 小時
- **桌面版 (settings_old.py tkinter GUI)**：1-1.5 小時
  - 新增 tkinter 核取方塊：0.5 小時
  - 多語言支援與 tooltip：0.5 小時
  - 載入/儲存邏輯與測試：0.5 小時

**Phase 3（文件更新）**: 0.5 小時
- 更新 CHANGELOG.md：0.3 小時
- 更新 structure.md：0.2 小時

**總計**: 5-7 小時

---

## 相關文件

- **功能規格**: [spec.md](./spec.md)
- **技術研究**: [research.md](./research.md)
- **資料模型**: [data-model.md](./data-model.md)
- **API 合約**: [contracts/config-schema.md](./contracts/config-schema.md)
- **快速開始**: [quickstart.md](./quickstart.md)
- **專案憲章**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **開發指南**: [docs/02-development/development_guide.md](../../docs/02-development/development_guide.md)

---

**計畫完成日期**: 2025-10-31
**下一步**: 執行 `/speckit.tasks` 指令生成可執行任務清單
