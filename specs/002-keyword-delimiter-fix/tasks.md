# 任務：關鍵字分隔符號改善

**輸入**：來自 `/specs/002-keyword-delimiter-fix/` 的設計文件
**前置需求**：plan.md、spec.md、research.md、contracts/keyword-format.md、quickstart.md

**測試**：本功能使用手動整合測試（不包含單元測試任務）

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（如 US1、US2）
- 描述中請包含精確的檔案路徑

## 路徑命名慣例
- **單一專案**：`src/`、`docs/` 於 repository 根目錄
- 本專案採用單一專案結構

---

## 階段一：初始化（共用基礎設施）

**目的**：準備開發環境與設定檔範例

- [X] T001 確認專案結構符合實作計畫（無需建立新檔案）
- [X] T002 備份當前 settings.json 至 .temp/settings.json.backup
- [X] T003 [P] 建立測試輸出目錄 .temp/（若不存在）

---

## 階段二：基礎建設（阻斷性前置需求）

**目的**：修改核心關鍵字解析邏輯，所有 user story 依賴此階段完成

**⚠️ 關鍵**：本階段未完成前，不得開始任何 user story 實作

- [X] T004 在 src/util.py 開頭定義關鍵字分隔符號常數 CONST_KEYWORD_DELIMITER = ';' 和 CONST_KEYWORD_DELIMITER_OLD = ','
- [X] T005 修改 src/util.py:format_config_keyword_for_json() 函數，將 split(',') 改為 split(';')
- [X] T006 修改 src/util.py:is_text_match_keyword() 函數，將逗號分隔邏輯（行 183-186）改為分號分隔
- [X] T007 在 src/util.py:is_text_match_keyword() 中新增舊格式偵測邏輯（偵測包含逗號但無分號的字串）
- [X] T008 在 src/util.py:is_text_match_keyword() 中新增警告訊息輸出（當 verbose = True 且偵測到舊格式時）
- [X] T009 修改 src/settings.py:format_config_keyword_for_json() 函數（行 584），將 split(',') 改為 split(';')
- [X] T009b [額外發現] 修改 src/util.py:format_keyword_for_display() 函數，修復 UI 顯示邏輯（將 "," 轉換為 ";"）
- [X] T010 [P] 修改 src/nodriver_tixcraft.py:3875 行（日期關鍵字解析），確保使用新的分號分隔邏輯
- [X] T011 [P] 修改 src/nodriver_tixcraft.py:4035 行（排除關鍵字解析），將 split(',') 改為 split(';')
- [X] T012 [P] 修改 src/chrome_tixcraft.py 對應的關鍵字解析函數（同步 NoDriver 版本修改）

**檢查點**：基礎設施就緒——核心邏輯已改為分號分隔，user story 實作可開始

---

## 階段三：User Story 1 - 修正關鍵字分隔符號 (Priority: P1) 🎯 MVP

**目標**：所有平台的關鍵字正確使用分號分隔，包含金額、日期、時間控制關鍵字

**獨立測試**：透過設定分號分隔的關鍵字（如「3,280;2,680」），執行手動測試並驗證日誌輸出顯示正確的關鍵字匹配數量

### User Story 1 實作

- [X] T013 [P] [US1] 更新 src/settings.json 範例檔案，將所有關鍵字欄位改為分號分隔格式（date_keyword, area_keyword, keyword_exclude, idle_keyword, resume_keyword, idle_keyword_second, resume_keyword_second）
- [ ] T014 [US1] 執行手動整合測試（TicketPlus 平台）：設定 area_keyword 為「3,280;2,680」，執行 30 秒測試並檢查 .temp/test_output.txt [需手動執行]
- [ ] T015 [US1] 驗證測試日誌：使用 grep 檢查 "[AREA KEYWORD]" 輸出，確認關鍵字匹配數量為 2（"3,280" 和 "2,680"）[需手動執行]
- [ ] T016 [US1] 執行手動整合測試（TixCraft 平台）：設定 date_keyword 為「10/03;10/05」，執行 30 秒測試並檢查 .temp/test_output.txt [需手動執行]
- [ ] T017 [US1] 驗證測試日誌：使用 grep 檢查 "[DATE KEYWORD]" 輸出，確認日期關鍵字正確匹配 [需手動執行]
- [ ] T018 [US1] 執行手動整合測試（時間控制關鍵字）：設定 idle_keyword 為「09:30:00;14:15:30」，驗證系統在兩個時間點觸發暫停 [需手動執行]
- [ ] T019 [US1] 修正測試中發現的任何問題（若有）[待測試完成]

**檢查點**：User Story 1 完成——分號分隔的關鍵字在所有平台正確運作

---

## 階段四：User Story 2 - 向後相容性處理 (Priority: P2)

**目標**：舊格式（逗號分隔）觸發警告訊息，但系統仍能正常運作

**獨立測試**：載入包含逗號分隔關鍵字的 settings.json，驗證系統顯示警告訊息且包含正確的新格式範例

### User Story 2 實作

- [ ] T020 [US2] 建立測試用舊格式設定檔 .temp/settings_old_format.json，包含逗號分隔的關鍵字（例如：「A區,B區」）
- [ ] T021 [US2] 執行手動整合測試（舊格式偵測）：使用 --input .temp/settings_old_format.json 參數，執行 30 秒測試並啟用 verbose 模式
- [ ] T022 [US2] 驗證測試日誌：使用 grep 檢查 "[WARNING]" 輸出，確認警告訊息包含「偵測到舊格式的關鍵字設定」
- [ ] T023 [US2] 驗證測試日誌：確認警告訊息包含「建議格式」範例（將逗號替換為分號）
- [ ] T024 [US2] 驗證系統行為：確認舊格式設定檔仍可運作（不阻斷系統啟動），但會顯示警告
- [ ] T025 [US2] 清理測試檔案：刪除 .temp/settings_old_format.json

**檢查點**：User Story 2 完成——向後相容性機制正常運作，舊格式觸發警告但不中斷系統

---

## 階段五：文件更新 (Priority: P2)

**目的**：所有文件與範例同步更新為新格式

- [ ] T026 [P] 更新 README.md：搜尋所有關鍵字範例，將逗號替換為分號（使用 grep 驗證無殘留舊格式）
- [ ] T027 [P] 更新 docs/01-getting-started/setup.md：更新 settings.json 設定範例，將所有關鍵字欄位改為分號分隔格式
- [ ] T028 [P] 更新 specs/001-ticket-automation-system/contracts/config-schema.md：更新 date_keyword、area_keyword、keyword_exclude、idle_keyword、resume_keyword 的描述與範例
- [ ] T029 [P] 更新 specs/001-ticket-automation-system/quickstart.md：更新所有平台的設定範例，將關鍵字格式改為分號分隔
- [ ] T030 更新 CHANGELOG.md：新增版本記錄，標記為 BREAKING CHANGE，包含遷移指南參考（quickstart.md）

**檢查點**：所有文件已同步更新，無殘留舊格式範例

---

## 階段六：驗證與優化

**目的**：最終驗證與文件檢查

- [ ] T031 使用 grep 全域搜尋專案中所有 split(',') 的用法，確認無遺漏修改
- [ ] T032 使用 grep 搜尋所有文件中的舊格式範例（搜尋 `","` 模式），確認已全部更新
- [ ] T033 執行 quickstart.md 中的完整設定範例（TicketPlus 與 TixCraft），驗證新格式正常運作
- [ ] T034 [P] 執行所有平台的冒煙測試（TixCraft、KKTIX、TicketPlus、iBon、KHAM），確認分號分隔邏輯在各平台正常運作
- [ ] T035 撰寫 Release Notes（包含 BREAKING CHANGE 說明與遷移步驟）

---

## 相依性與執行順序

### 階段相依性

- **階段一（初始化）**：無相依性——可立即開始
- **階段二（基礎建設）**：依賴初始化完成——阻斷所有 user story
- **階段三（User Story 1）**：依賴基礎建設完成——核心功能實作
- **階段四（User Story 2）**：依賴基礎建設完成——可與 US1 平行進行（不同測試情境）
- **階段五（文件更新）**：依賴 US1 與 US2 完成——確保文件反映實際實作
- **階段六（驗證與優化）**：依賴所有前置階段完成——最終檢查

### User Story 相依性

- **User Story 1（P1）**：基礎建設（階段二）完成後可開始——不依賴其他 stories
- **User Story 2（P2）**：基礎建設（階段二）完成後可開始——可與 US1 平行測試（使用不同設定檔）

### 平行作業機會

**基礎建設階段（階段二）**：
```bash
# T010-T012 可平行執行（不同檔案）
Task: "修改 src/nodriver_tixcraft.py:3875 行（日期關鍵字解析）"
Task: "修改 src/nodriver_tixcraft.py:4035 行（排除關鍵字解析）"
Task: "修改 src/chrome_tixcraft.py 對應的關鍵字解析函數"
```

**文件更新階段（階段五）**：
```bash
# T026-T029 可平行執行（不同檔案）
Task: "更新 README.md"
Task: "更新 docs/01-getting-started/setup.md"
Task: "更新 specs/001-ticket-automation-system/contracts/config-schema.md"
Task: "更新 specs/001-ticket-automation-system/quickstart.md"
```

**驗證階段（階段六）**：
```bash
# T034 可平行執行（不同平台）
Task: "執行 TixCraft 冒煙測試"
Task: "執行 KKTIX 冒煙測試"
Task: "執行 TicketPlus 冒煙測試"
Task: "執行 iBon 冒煙測試"
Task: "執行 KHAM 冒煙測試"
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1）

1. 完成階段一：初始化（T001-T003）
2. 完成階段二：基礎建設（T004-T012）——關鍵阻斷點
3. 完成階段三：User Story 1（T013-T019）
4. **停止並驗證**：執行手動整合測試，確認分號分隔邏輯在所有平台正常運作
5. 若已準備好則部署／展示

### 漸進式交付

1. 完成初始化 + 基礎建設 → 核心邏輯已修改
2. 加入 User Story 1 → 獨立測試 → 部署／展示（MVP！）
3. 加入 User Story 2 → 獨立測試 → 確保向後相容性
4. 完成文件更新 → 所有文件同步
5. 執行最終驗證 → 準備發佈

### 團隊平行開發策略

若有多位開發者：

1. **開發者 A**：
   - 負責階段二（基礎建設）的核心邏輯修改（T004-T009）
   - 負責階段三（User Story 1）的測試與驗證

2. **開發者 B**：
   - 負責階段二（基礎建設）的平台特定修改（T010-T012）
   - 負責階段四（User Story 2）的向後相容性測試

3. **開發者 C**：
   - 負責階段五（文件更新）的所有文件同步（T026-T030）
   - 負責階段六（驗證與優化）的最終檢查

---

## 測試執行指令

### 手動整合測試（Git Bash）

**NoDriver 版本**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**驗證日誌輸出**：
```bash
# 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 檢查關鍵流程節點
grep "Match Summary\|Selected target\|clicked\|navigat" .temp/test_output.txt

# 檢查警告訊息（舊格式偵測）
grep "\[WARNING\]" .temp/test_output.txt
```

### 全域搜尋驗證

**搜尋未修改的 split(',')**：
```bash
# 搜尋程式碼中的逗號分割
git grep "split\(','\)" src/

# 預期結果：僅保留非關鍵字相關的用法（例如 base64 解碼）
```

**搜尋文件中的舊格式範例**：
```bash
# 搜尋文件中的逗號分隔關鍵字
git grep '","' docs/ specs/ README.md

# 預期結果：僅保留 JSON 陣列格式範例或非關鍵字內容
```

---

## 憲法原則映射

本任務清單遵循以下憲法原則：

- **I. NoDriver First**：T010-T011 優先修改 NoDriver 版本，T012 同步修改 Chrome 版本
- **II. 資料結構優先**：無資料結構變更，僅修改解析邏輯
- **III. 三問法則**：
  - 是核心問題嗎？✅ 是（Issue #23，關鍵字匹配失效）
  - 有更簡單方法嗎？✅ 是（全域替換分隔符號）
  - 會破壞相容性嗎？⚠️ 會（提供 US2 向後相容性機制）
- **IV. 單一職責與可組合性**：關鍵字解析邏輯集中在 util.py
- **V. 設定驅動開發**：T013 更新 settings.json 範例
- **VI. 測試驅動穩定性**：T014-T018（US1 測試）、T021-T024（US2 測試）
- **VII. MVP 原則**：階段三（User Story 1）為 MVP，可獨立交付
- **VIII. 文件與代碼同步**：階段五（T026-T030）確保所有文件同步
- **IX. Git 提交規範**：T030 更新 CHANGELOG，標記 BREAKING CHANGE

---

## 備註

- **[P] 任務**：不同檔案，無相依性，可平行執行
- **[Story] 標籤**：將任務對應到特定 User Story，方便追蹤
- **測試策略**：本功能使用手動整合測試，無單元測試任務
- **Breaking Change**：使用者必須更新 settings.json（逗號 → 分號）
- **Release Notes**：需包含遷移指南與範例
- **Commit Message 範本**：
  ```
  feat(keywords)!: change delimiter from comma to semicolon

  Replace comma (,) with semicolon (;) as keyword delimiter to avoid
  conflicts with currency format (e.g., "3,280") and time format
  (e.g., "09:30:00,14:15:30").

  BREAKING CHANGE: Keyword delimiter changed from comma to semicolon.
  Users must update their settings.json accordingly. See
  specs/002-keyword-delimiter-fix/quickstart.md for migration guide.

  Closes #23
  ```
- **每完成一個任務或邏輯群組就提交（commit）**
- **可在任何檢查點（checkpoint）停止，獨立驗證 User Story**
- **階段二（基礎建設）完成後，User Story 1 與 2 可平行進行**

---

**任務總數**：35 個
**MVP 範圍**：階段一、二、三（T001-T019），共 19 個任務
**預估時間**：1-2 天（MVP 可在 1 天內完成）
