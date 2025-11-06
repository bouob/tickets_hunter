---
description: "KKTIX 自動答題功能實作任務清單"
---

# 任務：KKTIX 自動答題功能（NoDriver 版本）

**輸入**：來自 `/specs/004-kktix-auto-answer/` 的設計文件
**前置需求**：plan.md、spec.md、research.md、data-model.md、contracts/

**測試**：功能規格未明確要求測試優先，因此採用實作後手動測試驗證方式。

**組織方式**：任務依 user story 分組，以利每個 user story 可獨立實作與測試。

## 格式說明：`[ID] [P?] [Story] Description`
- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的 user story（如 US1、US2、US3）
- 描述中包含精確的檔案路徑

## 路徑命名慣例
- **單一專案**（本專案結構）：`src/`、`docs/` 於 repository 根目錄
- **測試案例**：`.temp/`（臨時檔案，不納入 git）

---

## 階段一：初始化（共用基礎設施）

**目的**：專案初始化與基本結構確認

- [X] T001 驗證功能規格與設計文件完整性（spec.md、plan.md、data-model.md、contracts/）
- [X] T002 確認測試案例檔案存在於 .temp/kktix-sunset-qa.html

---

## 階段二：基礎建設（阻斷性前置需求）

**目的**：實作前必須完成的驗證工作

**⚠️ 關鍵**：本階段未完成前，不得開始任何 user story 實作

- [X] T003 [P] 驗證 write_question_to_file() 函數存在於 src/nodriver_tixcraft.py:178
- [X] T004 [P] 驗證 util.get_answer_list_from_question_string() 函數存在於 src/util.py 並接受 None 參數
- [X] T005 [P] 驗證 util.get_answer_list_from_user_guess_string() 函數存在於 src/util.py
- [X] T006 驗證 settings.json 中 advanced.auto_guess_options 配置欄位存在且預設為 false
- [X] T007 確認 nodriver_kktix_reg_captcha() 函數位於 src/nodriver_tixcraft.py:1172-1350 範圍

**檢查點**：基礎設施驗證完成——user story 實作可開始

---

## 階段三：User Story 1 - 自動偵測並回答 KKTIX 驗證問題 (Priority: P1) 🎯 MVP

**目標**：實作核心自動答題功能，包含問題偵測、答案推測、自動填寫

**獨立測試**：使用 .temp/kktix-sunset-qa.html 測試案例，啟用 auto_guess_options，驗證系統能偵測問題、推測答案並填寫至輸入框

### User Story 1 實作

- [X] T008 [US1] 在 src/nodriver_tixcraft.py:1206-1208 啟用 auto_guess_options 邏輯分支
- [X] T009 [US1] 確認呼叫 util.get_answer_list_from_question_string(None, question_text) 正確傳遞參數
- [X] T010 [US1] 實作答案清單過濾邏輯，跳過 fail_list 中已失敗的答案
- [X] T011 [US1] 實作 JavaScript 程式碼以模擬人類輸入行為（focus、input、change、blur 事件）
- [X] T012 [US1] 使用 tab.evaluate() 執行 JavaScript 填寫答案至輸入框
- [X] T013 [US1] 加入隨機延遲機制（0.3-1.0 秒）模擬人類行為
- [X] T014 [US1] 實作輸入框可用性檢查（disabled、readOnly 屬性）
- [X] T015 [US1] 加入錯誤處理機制，確保答題失敗不會導致搶票流程中斷

### User Story 1 測試

- [X] T016 [US1] 配置 settings.json 啟用 auto_guess_options: true
- [X] T017 [US1] 執行 30 秒 timeout 測試指令並檢查 .temp/test_output.txt
- [X] T018 [US1] 驗證問題文本正確偵測（question_text 不為空）
- [X] T019 [US1] 驗證答案清單正確產生（answer_list 不為空）
- [X] T020 [US1] 驗證答案成功填寫至輸入框

**檢查點**：此時 User Story 1 應可完全獨立運作並可測試（滿足 FR-001 至 FR-005）

---

## 階段四：User Story 2 - 答案重試與失敗記錄 (Priority: P2)

**目標**：實作失敗答案記錄機制，提升重試成功率

**獨立測試**：模擬答案錯誤情境，驗證系統能正確維護 fail_list 並跳過已失敗答案

### User Story 2 實作

- [X] T021 [US2] 確認 fail_list 參數在 nodriver_kktix_reg_captcha() 函數中正確傳遞
- [X] T022 [US2] 實作答案失敗時將答案加入 fail_list 的邏輯
- [X] T023 [US2] 實作選擇下一個答案時過濾 fail_list 的邏輯
- [X] T024 [US2] 實作當所有候選答案均失敗時停止自動填寫的邏輯
- [X] T025 [US2] 確保 fail_list 隨 session 清除（不持久化）

### User Story 2 測試

- [X] T026 [US2] 測試答案錯誤後 fail_list 正確記錄失敗答案
- [X] T027 [US2] 測試重試時跳過 fail_list 中的答案
- [X] T028 [US2] 測試所有候選答案失敗後停止自動填寫

**檢查點**：此時 User Story 1 與 2 均應能獨立運作（滿足 FR-006、FR-007）

---

## 階段五：User Story 3 - Debug 資訊輸出與問題記錄 (Priority: P3)

**目標**：實作 verbose 模式 Debug 輸出與問題記錄功能

**獨立測試**：啟用 verbose 模式，驗證終端輸出包含問題文本、答案清單、失敗記錄

### User Story 3 實作

- [X] T029 [P] [US3] 實作 verbose 模式檢查邏輯（config_dict["advanced"]["verbose"]）
- [X] T030 [P] [US3] 實作問題文本輸出（print question_text）
- [X] T031 [P] [US3] 實作答案清單輸出（print answer_list）
- [X] T032 [P] [US3] 實作失敗記錄輸出（print fail_list）
- [X] T033 [P] [US3] 實作推測答案輸出（print inferred_answer_string）
- [X] T034 [US3] 確認 write_question_to_file() 在偵測到問題後立即呼叫（line 1202 位置）

### User Story 3 測試

- [X] T035 [US3] 啟用 verbose: true 並執行測試
- [X] T036 [US3] 驗證終端輸出包含 question_text、answer_list、fail_list
- [X] T037 [US3] 驗證 src/question.txt 檔案正確記錄問題文本

**檢查點**：所有 user stories 均應可獨立運作（滿足 FR-009、FR-010、SC-006）

---

## 階段六：優化與橫向議題

**目的**：文件同步、效能驗證、成功標準檢查

- [X] T038 [P] 更新 docs/06-api-reference/nodriver_api_guide.md，新增 KKTIX 自動答題流程說明
- [X] T039 [P] 更新 docs/02-development/structure.md，新增 nodriver_kktix_reg_captcha() 函數索引與修改記錄
- [X] T040 驗證成功標準 SC-001：問題偵測時間 < 3 秒
- [X] T041 驗證成功標準 SC-002：答案推測成功率 >= 80%
- [X] T042 驗證成功標準 SC-003：答案填寫時間 < 2 秒
- [X] T043 驗證成功標準 SC-004：fail_list 正確記錄與過濾（100%）
- [X] T044 驗證成功標準 SC-005：無崩潰或異常拋出（0% 崩潰率）
- [X] T045 執行 quickstart.md 中的 5 分鐘快速啟用流程驗證
- [X] T046 檢查程式碼中無 emoji（避免 Windows cp950 編碼錯誤）
- [X] T047 [P] 更新 docs/10-project-tracking/accept_changelog.md 記錄本功能完成

---

## 相依性（dependency）與執行順序

### 階段相依性

- **初始化（階段一）**：無相依性——可立即開始
- **基礎建設（階段二）**：依賴初始化完成——阻斷所有 user story
- **User Stories（階段三起）**：皆依賴基礎建設完成
  - User Story 1 (P1)：基礎建設完成後可開始——不依賴其他 stories
  - User Story 2 (P2)：依賴 User Story 1 完成（需要 fail_list 機制）
  - User Story 3 (P3)：依賴 User Story 1 完成（需要答題流程存在）
- **優化（階段六）**：依賴所有 user story 完成

### User Story 相依性

- **User Story 1（P1）**：基礎建設完成後可開始——不依賴其他 stories（核心 MVP）
- **User Story 2（P2）**：依賴 User Story 1 完成——需要答題流程存在才能實作重試機制
- **User Story 3（P3）**：依賴 User Story 1 完成——需要答題流程存在才能實作 Debug 輸出

### 每個 User Story 內部

- **User Story 1**：
  1. 先實作核心邏輯（T008-T015）
  2. 再執行測試驗證（T016-T020）
- **User Story 2**：
  1. 先實作 fail_list 機制（T021-T025）
  2. 再執行測試驗證（T026-T028）
- **User Story 3**：
  - 所有標記 [P] 的輸出任務（T029-T033）可平行開發
  - T034 確認檔案記錄邏輯
  - 再執行測試驗證（T035-T037）

### 平行作業機會

- **階段二**：T003-T006 可平行執行（不同檔案、無相依性）
- **階段五**：T029-T033 可平行執行（不同輸出邏輯）
- **階段六**：T038-T039、T046-T047 可平行執行（不同文件）

---

## 平行作業範例：User Story 3

```bash
# Launch all verbose output tasks for User Story 3 together:
Task: "Implement verbose mode check logic (config_dict["advanced"]["verbose"])"
Task: "Implement question text output (print question_text)"
Task: "Implement answer list output (print answer_list)"
Task: "Implement fail list output (print fail_list)"
Task: "Implement inferred answer output (print inferred_answer_string)"
```

---

## 實作策略

### 先做 MVP（僅限 User Story 1）

1. 完成階段 1：Setup（T001-T002）
2. 完成階段 2：基礎建設（T003-T007）
3. 完成階段 3：User Story 1（T008-T020）
4. **停止並驗證**：獨立測試 User Story 1
5. 驗證 MVP 可用後再繼續 User Story 2 和 3

### 漸進式交付

1. 完成 Setup + 基礎建設 → 基礎驗證完成
2. 加入 User Story 1 → 獨立測試 → MVP 完成 🎯
3. 加入 User Story 2 → 獨立測試 → 重試機制完成
4. 加入 User Story 3 → 獨立測試 → Debug 功能完成
5. 完成優化與文件同步 → 功能交付完成

### 測試驗證策略

每個 User Story 完成後立即執行以下驗證：

**User Story 1 驗證**：
```cmd
cd "D:\Desktop\bouob-TicketHunter(MaxBot)\tickets_hunter"
del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul
echo. > .temp\test_output.txt
timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
type .temp\test_output.txt | findstr /C:"question_text" /C:"answer_list"
```

**User Story 2 驗證**：
檢查 `.temp/test_output.txt` 中的 `fail_list` 記錄

**User Story 3 驗證**：
啟用 `verbose: true` 並檢查終端輸出

---

## 技術上下文參考

**主要修改檔案**：
- `src/nodriver_tixcraft.py:1172-1350` - nodriver_kktix_reg_captcha() 函數
- 關鍵修改點：line 1206-1208（啟用 auto_guess_options 邏輯）

**複用函數（不修改）**：
- `src/util.py:1465-1493` - get_answer_list_from_user_guess_string()
- `src/util.py:1813-1950` - get_answer_list_from_question_string()
- `src/nodriver_tixcraft.py:178` - write_question_to_file()

**配置檔案**：
- `src/settings.json` - advanced.auto_guess_options、advanced.user_guess_string、advanced.verbose

**測試檔案**：
- `.temp/kktix-sunset-qa.html` - 測試案例
- `.temp/logs.txt` - 測試記錄參考
- `.temp/test_output.txt` - 測試輸出驗證

---

## 備註

- [P] 任務 = 不同檔案或邏輯，無相依性（dependency）
- [Story] 標籤可將任務對應到特定 User Story，方便追蹤
- 每個 User Story 都應能獨立完成與測試
- User Story 1 是 MVP，必須優先完成並驗證
- User Story 2 和 3 依賴 User Story 1 的答題流程存在
- 所有程式碼中禁止使用 emoji（避免 Windows cp950 編碼錯誤）
- 每完成一個任務或邏輯群組就提交（commit）
- 可在任何檢查點（checkpoint）停止，獨立驗證 User Story
- 實作完成後需執行 `/gsave` 提交，測試通過後執行 `/gpush` 推送

---

**任務清單版本**：1.0
**最後更新**：2025-11-03
**總任務數**：47 個任務
**MVP 範圍**：T001-T020（階段 1-3，User Story 1）
**預估並行機會**：9 個任務可平行執行（標記 [P]）
