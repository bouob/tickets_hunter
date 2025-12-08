# 任務：HKTicketing NoDriver 遷移

**輸入**：來自 `/specs/008-hkticketing-nodriver/` 的設計文件
**先決條件**：plan.md、spec.md、research.md、data-model.md、contracts/hkticketing-interface.md

**測試**：本專案使用手動整合測試，無自動化測試任務

**組織**：任務按使用者故事分組，以實現每個故事的獨立實作和測試

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務屬於哪個使用者故事（例如，US1、US2、US3）
- 在描述中包含確切的檔案路徑

## 路徑慣例

- **主要修改檔案**：`src/nodriver_tixcraft.py`
- **參考來源**：`src/chrome_tixcraft.py`（行 5661-8459）
- **共用工具**：`src/util.py`（無需修改）

---

## 階段 1：設定（共享基礎設施）

**目的**：確認開發環境和參考資料準備就緒

- [X] T001 確認 `src/nodriver_tixcraft.py` 可正常執行（`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`）
- [X] T002 確認 `src/chrome_tixcraft.py` 中的 HKTicketing 函數位置（行 5661-8459）
- [X] T003 [P] 確認 `src/settings.py` 已包含 `date_auto_fallback` 和 `area_auto_fallback` 設定欄位

---

## 階段 2：基礎（阻擋先決條件）

**目的**：建立 HKTicketing NoDriver 的基礎架構和狀態管理

**⚠️ 關鍵**：在此階段完成之前，不能開始任何使用者故事工作

- [X] T004 在 `src/nodriver_tixcraft.py` 中建立 `hkticketing_dict` 全域狀態字典（參考 data-model.md）
- [X] T005 [P] 在 `src/nodriver_tixcraft.py` 中建立 HKTicketing URL 模式識別常數（參考 data-model.md）
- [X] T006 [P] 在 `src/nodriver_tixcraft.py` 中建立錯誤訊息清單常數 `content_retry_string_list`（參考 data-model.md）
- [X] T007 在 `src/nodriver_tixcraft.py` 中建立 `nodriver_hkticketing_main` 主流程控制函數骨架

**檢查點**：基礎準備就緒——現在可以平行開始使用者故事實作

---

## 階段 3：使用者故事 1 - HKTicketing 日期自動選擇（優先順序：P1）🎯 MVP

**目標**：使用者設定日期關鍵字後，程式可在活動頁面自動選擇符合關鍵字的場次日期，並自動點擊購買按鈕

**獨立測試**：導航到 HKTicketing 活動頁面（`shows/show.aspx?`），驗證日期選擇與購買按鈕點擊功能

**功能需求**：FR-020~FR-026

### 使用者故事 1 的實作

- [X] T008 [US1] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_date_assign` - 日期指派核心邏輯（CSS: `#p`、`#p > option`）
- [X] T009 [US1] 在 `nodriver_hkticketing_date_assign` 中實作已售完日期過濾邏輯（FR-021）
- [X] T010 [US1] 在 `nodriver_hkticketing_date_assign` 中實作 `date_auto_fallback` 遞補機制（FR-026）
- [X] T011 [P] [US1] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_date_buy_button_press` - 點擊購買按鈕（CSS: `#buyButton > input`）
- [X] T012 [P] [US1] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_date_password_input` - 密碼保護頁面處理（CSS: `#entitlementPassword...`）
- [X] T013 [US1] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_date_auto_select` - 日期自動選擇整合函數
- [X] T014 [US1] 在 `nodriver_hkticketing_main` 中整合日期選擇功能（URL 模式：`shows/show.aspx?`）

**檢查點**：日期選擇功能可獨立測試

---

## 階段 4：使用者故事 2 - HKTicketing 區域/票價自動選擇（優先順序：P1）

**目標**：使用者設定區域關鍵字後，程式可在選票頁面自動選擇符合關鍵字的票價區域

**獨立測試**：導航到 HKTicketing 選票頁面（`/events/.../performances/.../tickets`），驗證區域選擇功能

**功能需求**：FR-030~FR-036

### 使用者故事 2 的實作

- [X] T015 [US2] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_area_auto_select` - 區域自動選擇（CSS: `#ticketSelectorContainer > ul > li`）
- [X] T016 [US2] 在 `nodriver_hkticketing_area_auto_select` 中實作區域過濾邏輯（disabled/unavailable/selected）
- [X] T017 [US2] 在 `nodriver_hkticketing_area_auto_select` 中實作排除關鍵字邏輯（使用 `util.reset_row_text_if_match_keyword_exclude`）
- [X] T018 [US2] 在 `nodriver_hkticketing_area_auto_select` 中實作 AND 邏輯關鍵字匹配（FR-034）
- [X] T019 [US2] 在 `nodriver_hkticketing_area_auto_select` 中實作 `area_auto_fallback` 遞補機制（FR-036）

**檢查點**：區域選擇功能可獨立測試

---

## 階段 5：使用者故事 3 - HKTicketing 票數自動設定與訂單送出（優先順序：P1）

**目標**：程式在區域選擇後自動設定購票張數，選擇取票方式，並點擊下一步按鈕完成訂單送出

**獨立測試**：在選票頁面驗證票數設定、取票方式選擇和下一步按鈕點擊功能

**功能需求**：FR-040~FR-041、FR-050~FR-053

### 使用者故事 3 的實作

- [X] T020 [P] [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_ticket_number_auto_select` - 票數自動設定（CSS: `select.shortSelect`）
- [X] T021 [P] [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_nav_to_footer` - 捲動到頁面底部（CSS: `#wrapFooter`）
- [X] T022 [P] [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_ticket_delivery_option` - 選擇取票方式（CSS: `#selectDeliveryType`）
- [X] T023 [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_next_button_press` - 點擊下一步按鈕（CSS: `#continueBar > div.chooseTicketsOfferDiv > button`）
- [X] T024 [P] [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_go_to_payment` - 點擊前往付款按鈕（CSS: `#goToPaymentButton`）
- [X] T025 [US3] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_performance` - 票券選擇頁面整合流程
- [X] T026 [US3] 在 `nodriver_hkticketing_main` 中整合票券選擇和訂單送出功能（URL 模式：`/events/.../performances/.../tickets` 和 `/seatmap`）

**檢查點**：票數設定和訂單送出功能可獨立測試

---

## 階段 6：使用者故事 4 - HKTicketing 自動登入（優先順序：P2）

**目標**：使用者設定 HKTicketing 帳號密碼後，程式可在登入頁面自動填入帳號並輸入密碼，完成登入流程

**獨立測試**：導航到 HKTicketing 登入頁面，驗證帳號密碼自動填入功能

**功能需求**：FR-010~FR-012

### 使用者故事 4 的實作

- [X] T027 [US4] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_login` - 自動登入（CSS: `div.loginContentContainer > input.borInput`、`input[type="password"]`）
- [X] T028 [US4] 在 `nodriver_hkticketing_main` 中整合登入功能（URL 模式：`ShowLogin.aspx` 或 `Membership/Login.aspx`）

**檢查點**：登入功能可獨立測試

---

## 階段 7：使用者故事 5 - HKTicketing 頁面重定向與錯誤處理（優先順序：P2）

**目標**：程式能自動處理排隊頁面、錯誤頁面的重定向，以及偵測並繞過機器人檢測

**獨立測試**：模擬各種錯誤頁面場景，驗證重定向功能

**功能需求**：FR-060~FR-065

### 使用者故事 5 的實作

- [X] T029 [P] [US5] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_url_redirect` - URL 重定向處理（queue.hkticketing.com、detection.aspx、busy_galaxy）
- [X] T030 [P] [US5] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_content_refresh` - 內容錯誤重載處理（Access Denied、503 等）
- [X] T031 [P] [US5] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_travel_iframe` - 遍歷 iframe 內容進行錯誤檢測
- [X] T032 [P] [US5] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_escape_robot_detection` - 機器人檢測繞過（CSS: `#main-iframe`）
- [X] T033 [US5] 在 `nodriver_hkticketing_main` 中整合錯誤處理功能

**檢查點**：錯誤處理功能可獨立測試

---

## 階段 8：使用者故事 6 - Cookie 同意處理（優先順序：P3）

**目標**：程式能自動關閉 Cookie 同意彈窗

**獨立測試**：導航到 HKTicketing 首頁，驗證 Cookie 彈窗自動關閉功能

**功能需求**：FR-070

### 使用者故事 6 的實作

- [X] T034 [P] [US6] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_accept_cookie` - 關閉 Cookie 同意彈窗（CSS: `#closepolicy_new`）
- [X] T035 [P] [US6] 在 `src/nodriver_tixcraft.py` 中實作 `nodriver_hkticketing_hide_tickets_blocks` - 隱藏不必要的頁面區塊
- [X] T036 [US6] 在 `nodriver_hkticketing_main` 中整合 Cookie 處理功能

**檢查點**：Cookie 處理功能可獨立測試

---

## 階段 9：收尾與跨領域關注點

**目的**：完成主流程整合、文件更新和驗證

- [X] T037 完成 `nodriver_hkticketing_main` 主流程控制函數（整合所有 URL 路由和功能）
- [X] T038 [P] 在 `docs/02-development/structure.md` 中更新 HKTicketing NoDriver 函數文件
- [X] T039 [P] 驗證 Galaxy Macau 子網站支援（ticketing.galaxymacau.com）
- [X] T040 [P] 驗證 Ticketek Australia 子網站支援（ticketek.com.au）
- [X] T041 執行完整購票流程手動測試（日期選擇 → 區域選擇 → 票數設定 → 訂單送出）
- [X] T042 執行 quickstart.md 驗證

---

## 相依性與執行順序

### 階段相依性

- **設定（階段 1）**：無相依性——可立即開始
- **基礎（階段 2）**：依賴設定完成——阻擋所有使用者故事
- **使用者故事（階段 3-8）**：全部依賴基礎階段完成
  - US1、US2、US3 為 P1 優先級，建議依序完成
  - US4、US5 為 P2 優先級，可在 P1 完成後平行進行
  - US6 為 P3 優先級，最後處理
- **收尾（階段 9）**：依賴所有使用者故事完成

### 使用者故事相依性

- **使用者故事 1（P1）**：日期選擇——不依賴其他故事
- **使用者故事 2（P1）**：區域選擇——不依賴其他故事，但實際流程在 US1 之後
- **使用者故事 3（P1）**：票數設定/訂單送出——整合 US2 的區域選擇
- **使用者故事 4（P2）**：登入——獨立功能
- **使用者故事 5（P2）**：錯誤處理——獨立功能，但影響所有頁面
- **使用者故事 6（P3）**：Cookie 處理——獨立功能

### 每個使用者故事內

- 核心函數先於整合函數
- 基礎邏輯先於進階功能（如 fallback）
- 故事完成後才移至下一優先順序

### 平行機會

- T003、T005、T006 可平行執行（設定階段）
- T011、T012 可平行執行（US1 內）
- T020、T021、T022、T024 可平行執行（US3 內）
- T029、T030、T031、T032 可平行執行（US5 內）
- T034、T035 可平行執行（US6 內）
- T038、T039、T040 可平行執行（收尾階段）

---

## 平行範例：使用者故事 3

```bash
# 一起啟動使用者故事 3 的所有可平行任務：
任務："在 src/nodriver_tixcraft.py 中實作 nodriver_hkticketing_ticket_number_auto_select"
任務："在 src/nodriver_tixcraft.py 中實作 nodriver_hkticketing_nav_to_footer"
任務："在 src/nodriver_tixcraft.py 中實作 nodriver_hkticketing_ticket_delivery_option"
任務："在 src/nodriver_tixcraft.py 中實作 nodriver_hkticketing_go_to_payment"
```

---

## 實作策略

### MVP 優先（使用者故事 1-3）

1. 完成階段 1：設定
2. 完成階段 2：基礎（關鍵——阻擋所有故事）
3. 完成階段 3：使用者故事 1（日期選擇）
4. 完成階段 4：使用者故事 2（區域選擇）
5. 完成階段 5：使用者故事 3（票數設定/訂單送出）
6. **停止並驗證**：執行完整購票流程測試
7. 如準備就緒則交付 MVP

### 增量交付

1. 完成設定 + 基礎 → 基礎準備就緒
2. 新增 US1（日期選擇）→ 獨立測試 → 交付
3. 新增 US2（區域選擇）→ 獨立測試 → 交付
4. 新增 US3（票數/訂單）→ 獨立測試 → 交付（MVP！）
5. 新增 US4（登入）→ 獨立測試 → 交付
6. 新增 US5（錯誤處理）→ 獨立測試 → 交付
7. 新增 US6（Cookie）→ 獨立測試 → 交付（完整版！）

---

## Fallback 機制實作要點（FR-026、FR-036）

### 日期 Fallback（T010）

```python
# 在 nodriver_hkticketing_date_assign 中
date_auto_fallback = config_dict.get("date_auto_fallback", False)

if not matched_dates:
    if date_auto_fallback:
        print("[DATE FALLBACK] date_auto_fallback=true, selecting from all available dates")
        target = util.get_target_item_from_matched_list(available_dates, auto_select_mode)
    else:
        print("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
        return False, False, []
```

### 區域 Fallback（T019）

```python
# 在 nodriver_hkticketing_area_auto_select 中
area_auto_fallback = config_dict.get("area_auto_fallback", False)

if not matched_areas:
    if area_auto_fallback:
        print("[AREA FALLBACK] area_auto_fallback=true, selecting from all available areas")
        target = util.get_target_item_from_matched_list(available_areas, auto_select_mode)
    else:
        print("[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
        return True, False  # is_need_refresh=True
```

### 參考實作

| 平台 | 日期 Fallback | 區域 Fallback |
|------|--------------|--------------|
| Cityline | `nodriver_tixcraft.py:15125-15131` | `nodriver_tixcraft.py:15407-15413` |
| KKTIX | `nodriver_tixcraft.py:1730-1741` | `nodriver_tixcraft.py:2264-2277` |

---

## 註記

- [P] 任務 = 不同函數、無相依性
- [Story] 標籤將任務對應到特定使用者故事以便追溯
- 每個使用者故事應可獨立完成和測試
- 每個任務或邏輯群組後提交（使用 `/gsave`）
- 在任何檢查點停止以獨立驗證故事
- 避免：模糊任務、同函數衝突、破壞獨立性的跨故事相依性
- 程式碼中禁止使用 emoji（避免 Windows cp950 編碼錯誤）
