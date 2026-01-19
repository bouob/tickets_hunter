# 任務：FunOne Tickets 平台支援

**輸入**：來自 `/specs/011-funone-platform/` 的設計文件
**先決條件**：plan.md、spec.md、research.md、data-model.md、contracts/config-schema.md

**組織**：任務按使用者故事分組，以實現每個故事的獨立實作和測試。

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務屬於哪個使用者故事（US1、US2、US3、US4、US5）
- 在描述中包含確切的檔案路徑

## 路徑慣例

- **主程式**：`src/nodriver_tixcraft.py`
- **共用函數**：`src/util.py`（不修改）
- **設定檔**：`src/settings.json`
- **文件**：`docs/02-development/structure.md`

---

## 階段 1：設定（共享基礎設施）

**目的**：專案初始化和基本結構

- [X] T001 在 `src/nodriver_tixcraft.py` 頂部新增 `funone_dict` 狀態字典定義（約第 200 行附近，參考 `kham_dict` 格式）
- [X] T002 在 `src/settings.json` 的 `advanced` 區塊新增 `funone_session_cookie` 欄位（預設空字串）

**備註**：購票張數使用通用的 `ticket_number` 設定，不需要平台專用欄位

---

## 階段 2：基礎（阻擋先決條件）

**目的**：在任何使用者故事可實作之前必須完成的核心基礎設施

**⚠️ 關鍵**：在此階段完成之前，不能開始任何使用者故事工作

- [X] T004 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_main(tab, url, config_dict)` 主控制函數，包含 URL 路由邏輯（約 150 行）
- [X] T005 在 `nodriver_funone_main` 內實作頁面類型識別邏輯（識別 HOME、ACTIVITY_DETAIL、LOGIN、TICKET_SELECT、ORDER_CONFIRM、MEMBER）
- [X] T006 在 `src/nodriver_tixcraft.py` 的 `main()` 函數中新增 FunOne 路由（約第 24527 行後）：`if 'tickets.funone.io' in url: tab = await nodriver_funone_main(tab, url, config_dict)`

**檢查點**：基礎準備就緒——現在可以平行開始使用者故事實作

---

## 階段 3：使用者故事 1 - Cookie 快速登入（優先順序：P1）🎯 MVP

**目標**：使用者透過設定 `ticket_session` Cookie 實現免 OTP 快速登入

**獨立測試**：注入 Cookie 後訪問會員中心頁面（`/member`），驗證是否顯示已登入狀態

### 使用者故事 1 的實作

- [X] T007 [US1] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_inject_cookie(tab, config_dict)` 函數，使用 CDP `network.set_cookie` 注入 `ticket_session`（約 50 行）
- [X] T008 [US1] 在 `nodriver_funone_inject_cookie` 中設定正確的 Cookie 屬性：domain=`tickets.funone.io`、path=`/`、httpOnly=`true`、secure=`false`
- [X] T009 [P] [US1] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_check_login_status(tab)` 函數，透過檢查「登入/註冊」按鈕是否存在判斷登入狀態（約 30 行）
- [X] T010 [US1] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_verify_login(tab, config_dict)` 函數，驗證登入狀態並在失敗時重新注入 Cookie（約 30 行）
- [X] T011 [US1] 在 `nodriver_funone_main` 中整合登入流程：進入 FunOne 頁面時自動檢查並注入 Cookie

**檢查點**：此時，使用者故事 1 應該可完全運作且可獨立測試

---

## 階段 4：使用者故事 2 - 活動詳情頁場次選擇（優先順序：P1）

**目標**：自動識別並選擇符合條件的場次，點擊「下一步」進入購票流程

**獨立測試**：導航到活動詳情頁面，驗證場次選擇與「下一步」按鈕點擊功能

### 使用者故事 2 的實作

- [X] T012 [P] [US2] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_close_popup(tab)` 函數，關閉 Cookie 同意彈窗和活動公告彈窗（約 30 行）
- [X] T013 [US2] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_date_auto_select(tab, url, config_dict)` 函數骨架（約 120 行）
- [X] T014 [US2] 在 `nodriver_funone_date_auto_select` 內實作 `get_all_session_options(tab)` 解析所有可選場次
- [X] T015 [US2] 在 `nodriver_funone_date_auto_select` 內使用 `util.get_matched_blocks_by_keyword()` 進行場次關鍵字匹配
- [X] T016 [US2] 在 `nodriver_funone_date_auto_select` 內實作 `filter_sold_out_sessions()` 過濾已售罄場次
- [X] T017 [US2] 在 `nodriver_funone_date_auto_select` 內實作 `fallback_select_by_mode()` 根據 `auto_select_mode` 遞補選擇
- [X] T018 [US2] 在 `nodriver_funone_date_auto_select` 內實作 `click_next_button(tab)` 點擊「下一步」按鈕
- [X] T019 [US2] 在 `nodriver_funone_main` 中整合場次選擇：偵測到活動詳情頁時自動執行場次選擇

**檢查點**：此時，使用者故事 1 和 2 都應該獨立運作

---

## 階段 5：使用者故事 3 - 選票頁面票種張數選擇（優先順序：P1）

**目標**：自動選擇票種、設定張數，等待驗證碼輸入

**獨立測試**：導航到選票頁面，驗證票種選擇和張數設定功能

### 使用者故事 3 的實作

- [X] T020 [US3] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_area_auto_select(tab, url, config_dict)` 函數骨架（約 120 行）
- [X] T021 [US3] 在 `nodriver_funone_area_auto_select` 內實作 `get_all_ticket_types(tab)` 解析所有票種
- [X] T022 [US3] 在 `nodriver_funone_area_auto_select` 內使用 `util.get_matched_blocks_by_keyword()` 進行票種關鍵字匹配
- [X] T023 [US3] 在 `nodriver_funone_area_auto_select` 內實作 `apply_exclude_keywords()` 排除不要的票種（如身障席）
- [X] T024 [US3] 在 `nodriver_funone_area_auto_select` 內實作 `fallback_select_by_mode()` 根據 `auto_select_mode` 遞補選擇
- [X] T025 [P] [US3] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_assign_ticket_number(tab, config_dict)` 函數（約 60 行）
- [X] T026 [US3] 在 `nodriver_funone_assign_ticket_number` 內偵測張數選擇元件類型（dropdown 或 input）並設定張數
- [X] T027 [P] [US3] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_captcha_handler(tab, config_dict)` 函數（約 50 行）
- [X] T028 [US3] 在 `nodriver_funone_captcha_handler` 內實作驗證碼偵測和播放提示音等待人工輸入
- [X] T029 [US3] 在 `nodriver_funone_main` 中整合票種選擇流程：偵測到選票頁面時依序執行票種選擇、張數設定、驗證碼處理

**檢查點**：此時，使用者故事 1、2、3 都應該獨立運作

---

## 階段 6：使用者故事 4 - 訂單確認與提交（優先順序：P2）

**目標**：驗證碼完成後自動點擊提交按鈕完成訂單送出

**獨立測試**：在選票頁面完成所有選擇後，驗證提交按鈕點擊功能

### 使用者故事 4 的實作

- [X] T030 [P] [US4] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_ticket_agree(tab)` 函數，勾選同意條款（約 40 行，待實測確認是否需要）
- [X] T031 [US4] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_order_submit(tab, config_dict, funone_dict)` 函數骨架（約 60 行）
- [X] T032 [US4] 在 `nodriver_funone_order_submit` 內實作 `find_submit_button(tab)` 定位提交按鈕
- [X] T033 [US4] 在 `nodriver_funone_order_submit` 內實作訂單提交成功偵測和播放訂單音效
- [X] T034 [US4] 在 `nodriver_funone_main` 中整合訂單提交流程：驗證碼完成後自動提交訂單

**檢查點**：此時，使用者故事 1、2、3、4 都應該獨立運作

---

## 階段 7：使用者故事 5 - 頁面狀態監控與錯誤處理（優先順序：P2）

**目標**：監控頁面狀態，自動處理錯誤頁面重載和異常情況

**獨立測試**：模擬各種錯誤頁面場景，驗證自動重載功能

### 使用者故事 5 的實作

- [X] T035 [US5] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_auto_reload(tab, config_dict, funone_dict)` 函數骨架（約 50 行）
- [X] T036 [US5] 在 `nodriver_funone_auto_reload` 內實作錯誤頁面偵測（503、500、網路錯誤）
- [X] T037 [US5] 在 `nodriver_funone_auto_reload` 內實作「即將開賣」頁面偵測和自動重載
- [X] T038 [P] [US5] 在 `src/nodriver_tixcraft.py` 實作 `nodriver_funone_error_handler(tab, error, config_dict, funone_dict)` 函數（約 50 行）
- [X] T039 [US5] 在 `nodriver_funone_error_handler` 內實作售罄、超時、網路錯誤、Session 過期等錯誤類型處理
- [X] T040 [US5] 在 `nodriver_funone_main` 中整合錯誤處理和頁面監控邏輯

**檢查點**：所有使用者故事現在應該都可獨立運作

---

## 階段 8：收尾與跨領域關注點

**目的**：影響多個使用者故事的改進

- [X] T041 [P] 在 `docs/02-development/structure.md` 新增 FunOne 平台函數索引
- [X] T042 程式碼清理：確保所有函數遵循專案命名規範（`nodriver_funone_*`）
- [X] T043 [P] 新增適當的日誌輸出（使用 `print()` 但禁止 emoji）
- [X] T044 執行 quickstart.md 驗證：手動測試完整購票流程
- [X] T045 確認所有 util.py 共用函數呼叫正確（`get_matched_blocks_by_keyword`、`get_target_item_from_matched_list` 等）

---

## 相依性與執行順序

### 階段相依性

- **設定（階段 1）**：無相依性——可立即開始
- **基礎（階段 2）**：依賴設定完成——阻擋所有使用者故事
- **使用者故事（階段 3-7）**：全部依賴基礎階段完成
  - US1（P1）→ US2（P1）→ US3（P1）：核心流程，建議循序
  - US4（P2）、US5（P2）：可在核心流程後平行
- **收尾（階段 8）**：依賴所有使用者故事完成

### 使用者故事相依性

```
       ┌──────────────────────────────────────┐
       │         階段 2：基礎                 │
       │    (nodriver_funone_main 主流程)      │
       └──────────────────┬───────────────────┘
                          │
       ┌──────────────────┴───────────────────┐
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│  US1 (P1)   │                        │  US5 (P2)   │
│ Cookie 登入 │                        │ 頁面監控    │
└──────┬──────┘                        └─────────────┘
       │
       ▼
┌─────────────┐
│  US2 (P1)   │
│ 場次選擇    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  US3 (P1)   │
│ 票種選擇    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  US4 (P2)   │
│ 訂單提交    │
└─────────────┘
```

### 每個使用者故事內

- 函數骨架先於細節實作
- 核心功能先於輔助功能
- 單一函數完成後才整合到主流程
- 故事完成後才移至下一優先順序

### 平行機會

- T007、T009：Cookie 注入和登入檢查可平行實作
- T012、T025、T027：彈窗處理、張數設定、驗證碼處理可平行實作
- T030、T038：條款同意和錯誤處理可平行實作
- T041、T043：文件更新和日誌新增可平行執行

---

## 平行範例：使用者故事 3

```bash
# 一起啟動使用者故事 3 的平行任務：
任務："在 src/nodriver_tixcraft.py 實作 nodriver_funone_assign_ticket_number 函數"
任務："在 src/nodriver_tixcraft.py 實作 nodriver_funone_captcha_handler 函數"
```

---

## 實作策略

### MVP 優先（US1 + US2 + US3）

1. 完成階段 1：設定
2. 完成階段 2：基礎（關鍵——阻擋所有故事）
3. 完成階段 3：使用者故事 1（Cookie 快速登入）
4. **停止並驗證**：確認登入功能正常
5. 完成階段 4：使用者故事 2（場次選擇）
6. 完成階段 5：使用者故事 3（票種選擇）
7. **停止並驗證**：測試完整購票流程（到驗證碼步驟）

### 增量交付

1. 完成設定 + 基礎 → 基礎準備就緒
2. 新增 US1 → 獨立測試 → Cookie 登入可用
3. 新增 US2 → 獨立測試 → 場次選擇可用
4. 新增 US3 → 獨立測試 → 票種選擇可用（MVP！）
5. 新增 US4 → 獨立測試 → 訂單提交可用
6. 新增 US5 → 獨立測試 → 錯誤處理完善

---

## 摘要

| 階段 | 任務數 | 說明 |
|------|--------|------|
| 階段 1：設定 | 2 | 狀態字典、Cookie 設定欄位 |
| 階段 2：基礎 | 3 | 主流程、URL 路由 |
| 階段 3：US1 | 5 | Cookie 快速登入 |
| 階段 4：US2 | 8 | 場次選擇 |
| 階段 5：US3 | 10 | 票種張數選擇 |
| 階段 6：US4 | 5 | 訂單提交 |
| 階段 7：US5 | 6 | 頁面監控錯誤處理 |
| 階段 8：收尾 | 5 | 文件、清理、驗證 |
| **總計** | **44** | |

---

## 註記

- 所有函數位於 `src/nodriver_tixcraft.py`，位置約在第 24100 行後（HKTicketing 函數之後）
- 使用 `util.py` 共用函數，不直接修改 `util.py`
- 程式碼中禁止使用 emoji（避免 Windows cp950 編碼錯誤）
- 每個任務或邏輯群組後使用 `/gsave` 提交
- 手動測試使用指令：`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`
