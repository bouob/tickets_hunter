# Tickets Hunter 文件導覽

> 多平台搶票自動化系統 - 完整技術文件索引

## 快速導航

**新手入門** → [01-getting-started/](01-getting-started/)
**開發新功能** → [02-development/](02-development/) → [06-api-reference/](06-api-reference/)
**除錯問題** → [07-testing-debugging/](07-testing-debugging/) → [08-troubleshooting/](08-troubleshooting/)
**打包部署** → [09-deployment/](09-deployment/)
**追蹤進度** → [10-project-tracking/](10-project-tracking/)
**重構優化** → [11-refactoring/](11-refactoring/)

---

## 📊 文件結構總覽

```
docs/
├── README.md                                          ← 文件導覽索引
│
├── 01-getting-started/                                ← 新手入門
│   ├── project_overview.md                            ← 專案架構與系統概覽
│   ├── setup.md                                       ← 安裝與環境設定
│   └── update.md                                      ← 更新說明
│
├── 02-development/                                    ← 開發指南
│   ├── ticket_automation_standard.md                  ← 標準功能定義（12階段）⭐
│   ├── structure.md                                   ← 程式架構與函數索引 ⭐
│   ├── development_guide.md                           ← 開發規範與檢查清單
│   ├── coding_templates.md                            ← 程式寫法範本
│   ├── documentation_workflow.md                      ← 文件維護流程
│   └── ticket_seat_selection_algorithm.md             ← 座位選擇演算法
│
├── 03-mechanisms/                                     ← 12 階段機制文件 (新增)
│   ├── README.md                                      ← 機制文件索引
│   ├── 01-environment-init.md                         ← Stage 1: 環境初始化
│   ├── 02-authentication.md                           ← Stage 2: 身份認證
│   ├── 03-page-monitoring.md                          ← Stage 3: 頁面監控
│   ├── 04-date-selection.md                           ← Stage 4: 日期選擇
│   ├── 05-area-selection.md                           ← Stage 5: 區域選擇
│   ├── 06-ticket-count.md                             ← Stage 6: 票數設定
│   ├── 07-captcha-handling.md                         ← Stage 7: 驗證碼處理
│   ├── 08-form-filling.md                             ← Stage 8: 表單填寫
│   ├── 09-terms-agreement.md                          ← Stage 9: 條款同意
│   ├── 10-order-submit.md                             ← Stage 10: 訂單送出
│   ├── 11-queue-payment.md                            ← Stage 11: 排隊付款
│   └── 12-error-handling.md                           ← Stage 12: 錯誤處理
│
├── 04-implementation/                                 ← 平台實作參考 (新增)
│   ├── README.md                                      ← 平台參考索引
│   └── platform-examples/
│       ├── tixcraft-reference.md                      ← TixCraft 實作參考
│       ├── kktix-reference.md                         ← KKTIX 實作參考
│       ├── ibon-reference.md                          ← iBon 實作參考
│       └── ticketplus-reference.md                    ← TicketPlus 實作參考
│
├── 05-validation/                                     ← 驗證系統 (新增)
│   ├── README.md                                      ← 驗證系統索引
│   ├── spec-validation-matrix.md                      ← FR 規格驗證矩陣
│   ├── platform-checklist.md                          ← 平台實作檢查清單
│   └── fr-to-code-mapping.md                          ← FR 到程式碼對照表
│
├── 06-api-reference/                                  ← API 參考文件
│   ├── cdp_protocol_reference.md                      ← CDP 完整參考 ⭐
│   ├── nodriver_api_guide.md                          ← NoDriver 除錯必讀 ⭐
│   ├── nodriver_selector_analysis.md                  ← NoDriver Selector 最佳實踐分析
│   ├── shadow_dom_pierce_guide.md                     ← Shadow DOM 穿透指南
│   ├── chrome_api_guide.md                            ← Chrome/UC 除錯必讀 ⭐
│   ├── selenium_api_guide.md                          ← Selenium API 完整參考
│   └── ddddocr_api_guide.md                           ← 驗證碼識別 API
│
├── 07-testing-debugging/                              ← 測試與除錯
│   ├── testing_execution_guide.md                     ← 標準測試流程與指令 ⭐
│   ├── debugging_methodology.md                       ← 背景測試與 Shadow DOM 除錯 ⭐
│   ├── ibon_nodriver_utk0201_fix_verification.md     ← ibon NoDriver 修復驗證
│   └── reports/                                       ← 除錯報告存放處
│
├── 08-troubleshooting/                                ← 問題排除
│   ├── README.md                                      ← 問題排除索引 ⭐
│   ├── ibon_cookie_troubleshooting.md                 ← ibon Cookie 問題排查
│   ├── ibon_nodriver_fixes_2025-10-03.md             ← ibon NoDriver 修復記錄
│   ├── kham_nodriver_dropdown_serialization.md        ← KHAM 下拉選單序列化問題
│   └── kham_ticket_submit_fix_2025-10-09.md          ← KHAM 提交按鈕修復記錄
│
├── 09-deployment/                                     ← 部署打包
│   └── pyinstaller_packaging_guide.md                 ← PyInstaller 打包指南
│
├── 10-project-tracking/                               ← 專案追蹤
│   ├── todo.md                                        ← 待實作功能清單
│   ├── accept_changelog.md                            ← Accept Edits On 自動化工作記錄
│   └── changelog_guide.md                             ← CHANGELOG 編寫指南 ⭐
│
└── 11-refactoring/                                    ← 重構與架構優化
    ├── README.md                                      ← 重構文件索引
    └── directory_restructuring_plan.md                ← 專案目錄結構重組計劃 ⭐
```

---

## 🎯 常見使用場景

### 場景 1：我想開發新平台支援

**開發流程：**
```
ticket_automation_standard.md → structure.md → development_guide.md → API 指南
```

1. 閱讀 [ticket_automation_standard.md](02-development/ticket_automation_standard.md) 了解標準流程（12 階段）
2. 查看 [structure.md](02-development/structure.md) 參考現有平台實作（含完成度評分）
3. 根據 `settings.json` 的 `webdriver_type` 選擇對應的 [API 指南](06-api-reference/)：
   - **CDP 協議（深入）** → [cdp_protocol_reference.md](06-api-reference/cdp_protocol_reference.md)
   - NoDriver（推薦）→ [nodriver_api_guide.md](06-api-reference/nodriver_api_guide.md)
   - Chrome/UC → [chrome_api_guide.md](06-api-reference/chrome_api_guide.md)
   - Selenium → [selenium_api_guide.md](06-api-reference/selenium_api_guide.md)
4. 遵循 [development_guide.md](02-development/development_guide.md) 的規範
5. 參考 [coding_templates.md](02-development/coding_templates.md) 的程式範本

### 場景 2：我遇到測試失敗或除錯問題

**除錯流程：**
```
檢查 Spec → 執行測試 → 分析錯誤 → 查閱 troubleshooting → 查閱 API 指南
```

1. **檢查功能規格**：`specs/001-ticket-automation-system/spec.md`
   - 查找相關的功能需求（FR-xxx）
   - 查找相關的成功標準（SC-xxx）
2. **執行標準測試**：使用 [testing_execution_guide.md](07-testing-debugging/testing_execution_guide.md) 執行測試
3. **學習除錯方法**：閱讀 [debugging_methodology.md](07-testing-debugging/debugging_methodology.md)
4. **查找類似問題**：檢查 [troubleshooting/](08-troubleshooting/) 是否有類似問題記錄
5. **查閱 API 文件**：根據錯誤類型查閱對應的 [API 指南](06-api-reference/)

### 場景 3：我想了解專案架構

1. **總覽**：從 [project_overview.md](01-getting-started/project_overview.md) 開始
2. **程式結構**：查看 [structure.md](02-development/structure.md) 了解函數索引
3. **標準流程**：閱讀 [ticket_automation_standard.md](02-development/ticket_automation_standard.md) 了解 12 階段標準
4. **座位選擇邏輯**：查看 [ticket_seat_selection_algorithm.md](02-development/ticket_seat_selection_algorithm.md)

### 場景 4：我要編寫 CHANGELOG

參考 [changelog_guide.md](10-project-tracking/changelog_guide.md) 了解使用者視角與開發者視角的差異。

### 場景 5：我要打包部署

參考 [pyinstaller_packaging_guide.md](09-deployment/pyinstaller_packaging_guide.md) 了解打包流程與注意事項。

---

## ⭐ 重點文件速查

| 文件 | 用途 | 適用對象 |
|------|------|----------|
| [ticket_automation_standard.md](02-development/ticket_automation_standard.md) | 標準功能定義（12 階段） | 開發者 |
| [structure.md](02-development/structure.md) | 程式架構索引與完成度評分 | 所有人 |
| [cdp_protocol_reference.md](06-api-reference/cdp_protocol_reference.md) | CDP 協議完整參考 | NoDriver 開發者 |
| [nodriver_api_guide.md](06-api-reference/nodriver_api_guide.md) | NoDriver 除錯（推薦） | 除錯者 |
| [nodriver_selector_analysis.md](06-api-reference/nodriver_selector_analysis.md) | NoDriver Selector 最佳實踐 | NoDriver 開發者 |
| [chrome_api_guide.md](06-api-reference/chrome_api_guide.md) | Chrome/UC 除錯 | 除錯者 |
| [debugging_methodology.md](07-testing-debugging/debugging_methodology.md) | 除錯方法論 | 除錯者 |
| [testing_execution_guide.md](07-testing-debugging/testing_execution_guide.md) | 標準測試流程 | 所有人 |
| [troubleshooting/README.md](08-troubleshooting/README.md) | 問題排除索引 | 除錯者 |
| [changelog_guide.md](10-project-tracking/changelog_guide.md) | CHANGELOG 編寫指南 | 開發者 |

---

## 📂 文件分類說明

### 🚀 01-getting-started/ - 新手入門
適合第一次接觸專案的開發者或使用者。包含專案概覽、環境設定、更新說明。

### 💻 02-development/ - 開發指南
開發新平台支援或新功能時必讀。包含標準流程定義、程式架構、開發規範、程式範本、文件維護流程。

### 📖 03-mechanisms/ - 12 階段機制文件
詳細的票券自動化流程文件。每個階段涵蓋流程說明、代碼範例、平台特定考量、故障排除。
- **推薦用途**：新增平台支援、理解完整流程、編寫相關功能

### 🎫 04-implementation/ - 平台實作參考
針對各個售票平台的具體實作參考文件。包含特定平台的選擇器、API 用法、常見問題。
- **推薦用途**：為特定平台編寫代碼、修復平台特定問題

### ✅ 05-validation/ - 驗證系統
規格驗證、平台實作狀態追蹤。包含 FR 需求對應、代碼映射、完成度評分。
- **推薦用途**：確認功能完整性、追蹤實作進度

### 📚 06-api-reference/ - API 參考文件
各 WebDriver 引擎的 API 使用指南。根據 `settings.json` 中的 `webdriver_type` 查閱對應文件。

**推薦閱讀順序**：
1. **CDP Protocol 參考** - 理解底層協議（NoDriver 必讀）
2. **NoDriver API** - 高階 API 使用（推薦）
3. **NoDriver Selector 最佳實踐** - 子選擇器效率優化（進階）
4. **Shadow DOM 穿透指南** - 處理 Shadow DOM 元素
5. Chrome/UC 或 Selenium - 舊版引擎參考

**優先順序**：NoDriver（推薦）> Chrome/UC > Selenium

### 🔍 07-testing-debugging/ - 測試與除錯
測試執行與問題排查方法論。包含標準測試流程、除錯方法、修復驗證報告。

### 🚨 08-troubleshooting/ - 問題排除
常見問題與特定平台修復記錄。按平台分類（ibon、KHAM 等），記錄已解決問題的解決方案。

### 📦 09-deployment/ - 部署打包
生產環境部署與打包指南。包含 PyInstaller 打包流程、依賴管理、平台適配。

### 📋 10-project-tracking/ - 專案追蹤
任務管理與變更記錄。包含待實作清單、自動化工作記錄、CHANGELOG 編寫指南。

### 🔧 11-refactoring/ - 重構與架構優化
程式架構重構計劃與優化文件。記錄重構決策、計劃、進度。

---

## 📝 文件維護

關於如何維護這些文件，請參考 [documentation_workflow.md](02-development/documentation_workflow.md)。

---

**最後更新：** 2025-11-03
