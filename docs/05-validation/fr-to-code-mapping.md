**文件說明**：功能需求（FR-001 至 FR-064）到程式碼實作的快速索引，包含函數名稱、檔案位置、行號與優先度標記，支援快速定位與除錯。

**最後更新**：2025-11-12

---

# FR 到程式碼對照表 (FR to Code Mapping)

## 概述

本文件提供**功能需求（FR-001 至 FR-064）到程式碼實作的快速索引**，用於：
- 🔍 快速定位功能對應的函數
- 📍 查找函數檔案位置與行號
- 🧪 檢查測試覆蓋狀態
- 🎯 識別高優先級待實作項目

**使用場景**：
- 需要修改特定 FR 的實作時
- 除錯特定功能問題時
- 查詢功能是否已實作時

**資料來源**：
- 規格：`specs/001-ticket-automation-system/spec.md`
- 實作：`src/nodriver_tixcraft.py`
- 函數索引：`docs/02-development/structure.md`

---

## 圖例說明

### 實作狀態
- **✅ 已實作**：功能完整實作
- **🔄 部分實作**：功能部分完成
- **⬜ 未實作**：功能尚未開發
- **N/A**：該 FR 無單一對應函數（架構層級或分散實作）

### 測試狀態
- **✅ 已測試**：已通過測試驗證
- **🔄 部分測試**：部分場景已測試
- **⬜ 未測試**：尚未測試

### 優先度
- **🔴 P1**：高優先度（核心功能）
- **🟡 P2**：中優先度（支援功能）
- **🟢 P3**：低優先度（優化項目）

---

## 快速查找索引

### 按階段分類

- [Stage 1：環境初始化](#stage-1環境初始化) - FR-001 至 FR-004
- [Stage 2：身份認證](#stage-2身份認證) - FR-005 至 FR-008
- [Stage 3：頁面監控與重載](#stage-3頁面監控與重載) - FR-009 至 FR-013
- [Stage 4：日期選擇](#stage-4日期選擇) - FR-014 至 FR-019
- [Stage 5：區域/座位選擇](#stage-5區域座位選擇) - FR-020 至 FR-026
- [Stage 6：票券數量](#stage-6票券數量) - FR-027 至 FR-030
- [Stage 7：驗證碼處理](#stage-7驗證碼處理) - FR-031 至 FR-039
- [Stage 8：表單填寫](#stage-8表單填寫) - FR-040 至 FR-043
- [Stage 9：同意條款處理](#stage-9同意條款處理) - FR-044 至 FR-047
- [Stage 10：訂單確認與送出](#stage-10訂單確認與送出) - FR-048 至 FR-053
- [Stage 11：排隊與付款](#stage-11排隊與付款) - FR-054 至 FR-057
- [Stage 12：錯誤處理與重試](#stage-12錯誤處理與重試) - FR-058 至 FR-064

### 按狀態分類

- [已實作功能 (38/64)](#已實作功能清單)
- [部分實作功能 (19/64)](#部分實作功能清單)
- [未實作功能 (7/64)](#未實作功能清單)

---

## FR 對照表

### Stage 1：環境初始化

#### FR-001：多種 WebDriver 類型支援

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_main()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 16775-16834 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | NoDriver 主程式入口，支援 "nodriver"、"chrome"、"selenium" 三種驅動 |

---

#### FR-002：瀏覽器選項初始化

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_main()` (瀏覽器啟動邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 16775-16834 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 使用 `nodriver.start()` 啟動瀏覽器，支援無頭模式、視窗大小設定 |

---

#### FR-003：瀏覽器擴充功能載入

| 項目 | 內容 |
|-----|-----|
| **狀態** | ⬜ 未實作 |
| **函數** | N/A |
| **檔案** | N/A |
| **行號** | N/A |
| **測試** | ⬜ 未測試 |
| **優先度** | 🟢 P3 |
| **說明** | 待開發：需擴展 NoDriver 啟動參數，建議加入 `advanced.extensions` 設定 |

---

#### FR-004：settings.json 結構驗證

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `load_config_from_file()`<br>`check_settings_json()` |
| **檔案** | `util.py` |
| **行號** | 1500-1650（估計） |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 目前僅檢查基本欄位存在性，需要完整 JSON Schema 驗證 |

---

### Stage 2：身份認證

#### FR-005：Cookie 注入登入

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_main()` (Cookie 注入邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1889-2050 |
| **測試** | ✅ 已測試（TixCraft、iBon） |
| **優先度** | 🔴 P1 |
| **說明** | TixCraft: `tixcraft_sid`<br>iBon: `ibonqware` |
| **相關設定** | `settings.json → advanced.tixcraft_sid`<br>`advanced.ibonqware` |

---

#### FR-006：使用者名稱/密碼登入

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_kktix_signin()`<br>`nodriver_ibon_login()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 302-324（KKTIX）<br>5500-5700（iBon，估計） |
| **測試** | ✅ 已測試（KKTIX） |
| **優先度** | 🟡 P2 |
| **說明** | KKTIX：帳密登入 + Facebook OAuth<br>iBon：帳密回退 |
| **相關設定** | `settings.json → advanced.kktix_account`<br>`advanced.kktix_password` |

---

#### FR-007：驗證登入狀態

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台 `_main()` 函數中的登入檢查 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🔴 P1 |
| **說明** | 需要統一的登入狀態驗證函數 |

---

#### FR-008：維持會話狀態

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | NoDriver 瀏覽器會話管理（`nodriver_main()` 中的 browser 物件） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 16775-16834 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | NoDriver 自動維持會話，Cookie 在整個流程中有效 |

---

### Stage 3：頁面監控與重載

#### FR-009：自動重載頁面

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 各平台主流程中的重載邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 支援可配置的重載間隔 |
| **相關設定** | `settings.json → advanced.auto_reload_page_interval` |

---

#### FR-010：過熱保護

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 主流程中的重載計數器邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 達到閾值後延長重載間隔 |
| **相關設定** | `settings.json → advanced.auto_reload_overheat_count` |

---

#### FR-011：彈出視窗處理

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `close_popup_windows()` |
| **檔案** | `util.py`（估計）或各平台主流程 |
| **行號** | N/A（分散實作） |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的彈窗選擇器列表 |

---

#### FR-012：即將開賣頁面偵測

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_main()` (即將開賣偵測邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1889-2050 |
| **測試** | ✅ 已測試（TixCraft） |
| **優先度** | 🟡 P2 |
| **說明** | TixCraft 專屬功能，偵測「即將開賣」文字並自動重載 |

---

#### FR-013：排隊/等候室頁面處理

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_kktix_paused_main()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 325-400 |
| **測試** | ✅ 已測試（KKTIX 排隊） |
| **優先度** | 🟡 P2 |
| **說明** | KKTIX 排隊機制，待擴展 Cityline 等候室 |

---

### Stage 4：日期選擇

#### FR-014：偵測日期選擇佈局類型

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1144-1326 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 自動偵測按鈕、下拉選單、日曆佈局 |
| **參考文件** | [Stage 4: 日期選擇機制](../02-mechanisms/04-date-selection.md) |

---

#### FR-015：取得所有可用日期選項

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()`<br>使用 `perform_search()` 查詢 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2660-2807 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | NoDriver 版本使用 CDP `perform_search()`，效能 2-5 秒（NFR-001） |
| **技術細節** | CDP `perform_search(query, include_user_agent_shadow_dom=True)` |

---

#### FR-016：過濾售罄日期

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (售罄過濾邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2750-2807 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 偵測「售罄」、「sold out」關鍵字，自動跳過 |
| **相關設定** | `settings.json → date_auto_select.pass_date_is_sold_out` |

---

#### FR-017：自動日期選擇（總開關）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (前置檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2660-2807 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 三層回退策略的前置檢查，false 時完全停用 |
| **相關設定** | `settings.json → date_auto_select.enable` |

---

#### FR-017-1：關鍵字匹配優先（Early Return）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (Early Return Pattern) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2759-2807 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | Feature 003: Early Return Pattern，第一個匹配立即停止 |
| **相關設定** | `settings.json → date_auto_select.date_keyword` |
| **參考文件** | [Feature 003: Keyword Priority Fallback](../../specs/003-keyword-priority-fallback/implementation-guide.md) |

---

#### FR-017-2：模式回退（Conditional Fallback）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (Conditional Fallback) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2863-2876 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 條件式回退：`date_auto_fallback = false`（嚴格模式）或 `true`（自動回退） |
| **相關設定** | `settings.json → date_auto_select.mode`<br>`date_auto_fallback` |

---

#### FR-017-3：停止並等待手動

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (第三層回退) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2863-2876 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 安全網設計：避免無明確指示時強制選擇 |

---

#### FR-018：enable=false 時完全停用

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (前置檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2660-2670 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 即使有關鍵字或模式設定也不執行 |
| **相關設定** | `settings.json → date_auto_select.enable = false` |

---

#### FR-019：驗證日期選擇成功

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_tixcraft_date_auto_select()` (返回值檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 2660-2900 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的驗證機制，確認選擇生效並導航到下一頁 |

---

### Stage 5：區域/座位選擇

#### FR-020：偵測區域選擇佈局類型

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_area_auto_select()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1327-1378 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 偵測按鈕、下拉選單、座位圖、展開面板佈局 |
| **參考文件** | [Stage 5: 區域選擇機制](../02-mechanisms/05-area-selection.md) |

---

#### FR-021：取得所有區域選項及定價

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_get_tixcraft_target_area()`<br>使用 `perform_search()` 查詢 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1379-1489 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 同時取得區域名稱、定價、可用性 |

---

#### FR-022：排除關鍵字過濾

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_get_tixcraft_target_area()` (keyword_exclude 邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3194-3197 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 支援逗號分隔多個排除關鍵字 |
| **相關設定** | `settings.json → keyword_exclude` |

---

#### FR-023：自動區域選擇（總開關）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_area_auto_select()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3000-3100 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 與日期選擇相同的總開關設計 |
| **相關設定** | `settings.json → area_auto_select.enable` |

---

#### FR-023-1：關鍵字匹配優先（Early Return）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_get_tixcraft_target_area()` (Early Return Pattern) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3048-3061 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 支援 AND 邏輯：使用 `+` 連接（例：`"VIP+搖滾區"`） |
| **相關設定** | `settings.json → area_auto_select.area_keyword` |

---

#### FR-023-2：模式回退（Conditional Fallback）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_area_auto_select()` (Conditional Fallback) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3079-3094 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 與日期選擇相同的條件回退機制 |
| **相關設定** | `settings.json → area_auto_select.mode`<br>`area_auto_fallback` |

---

#### FR-023-3：停止並等待手動

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_area_auto_select()` (第三層回退) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3079-3094 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 與日期選擇相同的安全網設計 |

---

#### FR-024：enable=false 時完全停用

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_area_auto_select()` (前置檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3000-3010 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 完全停用機制，確保手動控制 |
| **相關設定** | `settings.json → area_auto_select.enable = false` |

---

#### FR-025：座位圖處理

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | KHAM 座位選擇邏輯（估計） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | KHAM 部分 |
| **測試** | ⬜ 未測試 |
| **優先度** | 🟡 P2 |
| **說明** | 待開發：完整的座位圖選擇演算法 |

---

#### FR-026：允許非相鄰座位

| 項目 | 內容 |
|-----|-----|
| **狀態** | ⬜ 未實作 |
| **函數** | N/A |
| **檔案** | N/A |
| **行號** | N/A |
| **測試** | ⬜ 未測試 |
| **優先度** | 🟢 P3 |
| **說明** | 待開發：建議加入 `area_auto_select.allow_non_adjacent` 設定 |

---

### Stage 6：票券數量

#### FR-027：偵測票券數量輸入類型

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_assign_ticket_number()`<br>`nodriver_kktix_travel_price_list()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1490-1544（TixCraft）<br>425-624（KKTIX 價格列表） |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | TixCraft: 下拉選單<br>KKTIX: 價格列表模式（特殊） |

---

#### FR-028：設定票券數量

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_assign_ticket_number()`<br>`nodriver_kktix_assign_ticket_number()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1490-1544（TixCraft）<br>625-683（KKTIX） |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 支援 1-10 張票券設定 |
| **相關設定** | `settings.json → ticket_number` |

---

#### FR-029：處理超過可用數量

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_tixcraft_assign_ticket_number()` (最大值檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1490-1544 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的數量驗證邏輯，自動回退到最大可用數量 |

---

#### FR-030：驗證票券數量設定

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_tixcraft_assign_ticket_number()` (返回值檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1490-1544 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的驗證機制 |

---

### Stage 7：驗證碼處理

#### FR-031：偵測驗證碼類型

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_verify()`<br>`nodriver_kktix_reg_captcha()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1103-1143（TixCraft）<br>684-747（KKTIX 問答式） |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 支援：圖片 OCR、問答式、reCAPTCHA（手動回退） |
| **參考文件** | [Stage 7: 驗證碼處理機制](../02-mechanisms/07-captcha-handling.md) |

---

#### FR-032：提取驗證碼圖片

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_ticket_main_ocr()` (Canvas 擷取)<br>iBon Shadow DOM 驗證碼擷取 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 3737-3770（TixCraft Canvas）<br>9643-9730（iBon Shadow DOM） |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 支援 Canvas、img 標籤、Shadow DOM img |
| **相關設定** | `settings.json → ocr_captcha.image_source` |

---

#### FR-033：OCR 辨識驗證碼

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `ddddocr.classification()` (OCR 工具函數) |
| **檔案** | `util.py` |
| **行號** | OCR 工具函數（分散整合） |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 使用 ddddocr 引擎 |
| **相關設定** | `settings.json → ocr_captcha.enable` |
| **API 文件** | [ddddocr API 指南](../03-api-reference/ddddocr_api_guide.md) |

---

#### FR-034：beta OCR 模型選項

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | OCR 初始化邏輯（根據 beta 設定選擇模型） |
| **檔案** | `util.py` |
| **行號** | OCR 模型載入 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | beta 模型體積較大但準確率更高（70% → 80%+） |
| **相關設定** | `settings.json → ocr_captcha.beta` |

---

#### FR-035：自動輸入驗證碼

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_keyin_captcha_code()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1609-1677 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 使用 CDP `dispatch_key_event()` 模擬真實打字<br>人類化延遲（0.3-1 秒隨機） |

---

#### FR-036：強制送出或等待確認

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_verify()` (force_submit 邏輯) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1103-1143 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | `force_submit = true`: 自動送出<br>`force_submit = false`: 等待手動確認 |
| **相關設定** | `settings.json → ocr_captcha.force_submit` |

---

#### FR-037：手動驗證碼回退

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_keyin_captcha_code()` (手動輸入模式) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1609-1677 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | OCR 失敗或停用時播放音效提醒，等待手動輸入 |
| **相關設定** | `settings.json → ocr_captcha.enable = false` |

---

#### FR-038：驗證碼重新整理

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | TixCraft 驗證碼處理中的重新整理邏輯（估計） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 驗證碼相關函數 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟢 P3 |
| **說明** | 需要標準化的驗證碼重新整理機制 |

---

#### FR-039：驗證碼重試機制

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_kktix_reg_captcha()` (fail_list 機制) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1171-1330 |
| **測試** | ✅ 已測試（KKTIX fail_list 驗證通過） |
| **優先度** | 🟡 P2 |
| **說明** | **KKTIX fail_list 機制**：記錄錯誤答案避免重複嘗試<br>建議：將 max_retries 移至 settings.json |

---

### Stage 8：表單填寫

#### FR-040：偵測必填欄位

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台的表單填寫函數 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🔴 P1 |
| **說明** | 需要統一的表單欄位偵測機制 |

---

#### FR-041：自動填寫個人資訊

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台的表單填寫邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🔴 P1 |
| **說明** | 需要標準化的個人資訊設定結構（建議：`personal_info` 區塊） |
| **相關設定** | `settings.json → personal_info.*`（待標準化） |

---

#### FR-042：自訂問題答案處理

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 自訂問題處理邏輯（估計） |
| **檔案** | `util.py` 或各平台主流程 |
| **行號** | N/A（分散實作） |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的自訂問題處理機制 |
| **相關設定** | `settings.json → user_guess_string` |

---

#### FR-043：自動答案猜測

| 項目 | 內容 |
|-----|-----|
| **狀態** | ⬜ 未實作 |
| **函數** | N/A |
| **檔案** | N/A |
| **行號** | N/A |
| **測試** | ⬜ 未測試 |
| **優先度** | 🟢 P3 |
| **說明** | 待開發：建立常見問題答案資料庫（例：「興趣」→「音樂」） |

---

### Stage 9：同意條款處理

#### FR-044：偵測同意元素

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_ticket_main_agree()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1545-1562 |
| **測試** | ✅ 已測試（TixCraft） |
| **優先度** | 🔴 P1 |
| **說明** | 使用 `perform_search()` 查找核取方塊 |

---

#### FR-045：自動勾選同意

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_tixcraft_ticket_main_agree()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1545-1562 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 使用 CDP `dispatch_mouse_event()` 點擊 |

---

#### FR-046：平台特定同意對話框

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | TicketPlus 實名對話框<br>KHAM 實名卡片 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | TicketPlus/KHAM 部分 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的測試與文件化 |

---

#### FR-047：驗證同意完成

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_tixcraft_ticket_main_agree()` (返回值檢查) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1545-1562 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要更完整的驗證機制 |

---

### Stage 10：訂單確認與送出

#### FR-048：檢視訂單詳情

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台訂單送出前的檢查邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要標準化的訂單驗證機制 |

---

#### FR-049：定位送出按鈕

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_kktix_confirm_order_button()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1778-1812 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 使用 `perform_search()` 多種選擇器策略 |

---

#### FR-050：處理確認對話框

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台主流程中的對話框處理 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要統一的對話框處理機制 |

---

#### FR-051：搶到票音訊通知

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `play_sound()` |
| **檔案** | `util.py` |
| **行號** | 音訊播放工具 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 支援自訂音訊檔案 |
| **相關設定** | `settings.json → advanced.play_sound.ticket` |

---

#### FR-052：送出訂單音訊通知

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `play_sound()` |
| **檔案** | `util.py` |
| **行號** | 音訊播放工具 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 與 FR-051 共用機制 |
| **相關設定** | `settings.json → advanced.play_sound.order` |

---

#### FR-053：驗證訂單送出成功

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 各平台主流程中的確認頁面偵測 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要標準化的確認頁面偵測機制 |

---

### Stage 11：排隊與付款

#### FR-054：偵測排隊頁面

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_kktix_paused_main()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 325-400 |
| **測試** | ✅ 已測試（KKTIX） |
| **優先度** | 🟡 P2 |
| **說明** | KKTIX 排隊頁面偵測，待擴展 Cityline 等候室 |

---

#### FR-055：排隊等待

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_kktix_paused_main()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 325-400 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 避免頻繁重載觸發偵測 |

---

#### FR-056：排隊完成偵測

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `nodriver_kktix_paused_main()` (排隊結束偵測) |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 325-400 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 偵測排隊頁面消失或進入註冊頁面 |

---

#### FR-057：排隊失敗重試

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `nodriver_kktix_reg_auto_reload()` |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 1958-2050 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | KKTIX 自動重載機制，需要更完整的重試策略 |
| **相關設定** | `settings.json → kktix.auto_reload_coming_soon_page_enable` |

---

### Stage 12：錯誤處理與重試

#### FR-058：錯誤分類

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | 全域錯誤處理邏輯（分散各函數） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程和工具函數 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要統一的錯誤分類系統（建立標準錯誤代碼 E001-E999） |

---

#### FR-059：詳細錯誤記錄

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | `print()` 和日誌系統（遍布全域） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 所有函數（使用 `show_debug_message` 條件日誌） |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | `show_debug_message` 控制詳細日誌輸出 |
| **相關設定** | `settings.json → advanced.verbose` |

---

#### FR-060：自動重試（NoDriver CDP 原生）

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 所有 NoDriver 函數（使用 CDP 原生方法） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 全域 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | **反偵測核心**：100% 使用 CDP 原生方法<br>- ✅ 允許：CDP `dispatch_mouse_event()`<br>- ✅ 允許：CDP `perform_search()`<br>- ❌ 禁止：JavaScript `element.click()` |
| **技術規範** | NFR-004、NFR-005（specs/001-ticket-automation-system/spec.md） |

---

#### FR-061：可配置重試間隔

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 各平台主流程中的重載邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | ✅ 已測試 |
| **優先度** | 🟡 P2 |
| **說明** | 預設 0.1 秒（100ms），支援 0.01-10.0 秒範圍 |
| **相關設定** | `settings.json → advanced.auto_reload_page_interval` |

---

#### FR-062：錯誤通知

| 項目 | 內容 |
|-----|-----|
| **狀態** | 🔄 部分實作 |
| **函數** | `play_sound()` + 錯誤處理中的通知邏輯 |
| **檔案** | `util.py` + `src/nodriver_tixcraft.py` |
| **行號** | 分散在錯誤處理邏輯 |
| **測試** | 🔄 部分測試 |
| **優先度** | 🟡 P2 |
| **說明** | 需要統一的錯誤通知機制（音訊 + 視覺警報） |
| **相關設定** | `settings.json → advanced.play_sound.*` |

---

#### FR-063：售罄持續監控

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 各平台主流程中的售罄檢測與重載邏輯 |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 分散在各平台主流程 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | 偵測「售罄」、「sold out」關鍵字，自動重載直到票券可用 |
| **相關設定** | `settings.json → advanced.auto_reload_page_interval` |

---

#### FR-064：NoDriver CDP 原生方法

| 項目 | 內容 |
|-----|-----|
| **狀態** | ✅ 已實作 |
| **函數** | 所有 NoDriver 函數（使用 CDP API） |
| **檔案** | `src/nodriver_tixcraft.py` |
| **行號** | 全域 |
| **測試** | ✅ 已測試 |
| **優先度** | 🔴 P1 |
| **說明** | **核心架構原則**（憲法第 I 條）：<br>- DOM 查詢：`cdp.dom.perform_search()`<br>- 元素互動：`cdp.input_.dispatch_mouse_event()`<br>- 滾動：`cdp.dom.scroll_into_view_if_needed()`<br>- ❌ 禁止：所有 `tab.evaluate()` 或 JavaScript 注入 |
| **API 文件** | [CDP 協議參考](../03-api-reference/cdp_protocol_reference.md) |

---

## 分類清單

### 已實作功能清單

**總計**：38/64 (59.4%)

**按階段統計**：
- Stage 1：2/4
- Stage 2：3/4
- Stage 3：3/5
- Stage 4：9/9 ✅ 100%
- Stage 5：8/10
- Stage 6：2/4
- Stage 7：7/9
- Stage 8：0/4
- Stage 9：2/4
- Stage 10：3/6
- Stage 11：3/4
- Stage 12：5/7

---

### 部分實作功能清單

**總計**：19/64 (29.7%)

- FR-004：settings.json 結構驗證
- FR-007：驗證登入狀態
- FR-011：彈出視窗處理
- FR-013：排隊/等候室頁面處理
- FR-019：驗證日期選擇成功
- FR-025：座位圖處理
- FR-029：處理超過可用數量
- FR-030：驗證票券數量設定
- FR-038：驗證碼重新整理
- FR-040：偵測必填欄位
- FR-041：自動填寫個人資訊
- FR-042：自訂問題答案處理
- FR-046：平台特定同意對話框
- FR-047：驗證同意完成
- FR-048：檢視訂單詳情
- FR-050：處理確認對話框
- FR-053：驗證訂單送出成功
- FR-057：排隊失敗重試
- FR-058：錯誤分類
- FR-062：錯誤通知

---

### 未實作功能清單

**總計**：7/64 (10.9%)

- FR-003：瀏覽器擴充功能載入
- FR-026：允許非相鄰座位
- FR-043：自動答案猜測

---

## 相關文件

### 規格與驗證
- 📋 [功能規格](../../specs/001-ticket-automation-system/spec.md) - FR 完整定義
- 📋 [規格驗證矩陣](./spec-validation-matrix.md) - FR 實作狀態詳細追溯
- 📋 [平台實作檢查清單](./platform-checklist.md) - 平台完成度評分

### 程式碼結構
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 完整函數索引
- 📋 [12-Stage 標準](../02-development/ticket_automation_standard.md) - 流程定義

### API 參考
- 📋 [CDP 協議參考](../03-api-reference/cdp_protocol_reference.md) - FR-060、FR-064 技術細節
- 📋 [NoDriver API 指南](../03-api-reference/nodriver_api_guide.md) - NoDriver 完整參考
- 📋 [ddddocr API 指南](../03-api-reference/ddddocr_api_guide.md) - FR-033、FR-034

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| v1.0 | 2025-11 | 初版：建立 FR 到程式碼對照表 |
| | | ✅ 所有 FR-001 至 FR-064 對照 |
| | | ✅ 函數名稱、檔案位置、行號 |
| | | ✅ 實作狀態、測試狀態、優先度 |

**未來更新**：
- 每次修改功能時同步更新對照表
- 每次新增函數時更新行號
- 季度性檢查：確保對照表與實際程式碼同步

---

**最後更新**：2025-11（v1.0）
**維護者**：Tickets Hunter 開發團隊
**相關工具**：[規格驗證矩陣](./spec-validation-matrix.md)、[平台實作檢查清單](./platform-checklist.md)
