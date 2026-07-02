**文件說明**：Tickets Hunter 公開技術文件導覽與索引

**最後更新**：2026-06-14

---

# Tickets Hunter 文件導覽

> 多平台搶票自動化系統 - 技術文件索引

## 快速導航

**新手入門** → [01-getting-started/](01-getting-started/)
**開發新功能** → [02-development/](02-development/) → [06-api-reference/](06-api-reference/)
**打包部署** → [07-deployment/](07-deployment/)

---

## 文件結構總覽

```
docs/
├── README.md                                          <- 文件導覽索引
│
├── 01-getting-started/                                <- 新手入門
│   ├── README.md                                      <- 入門索引
│   ├── project_overview.md                            <- 專案架構與系統概覽
│   └── setup.md                                       <- 安裝與環境設定
│
├── 02-development/                                    <- 開發指南
│   ├── ticket_automation_standard.md                  <- 標準功能定義 (12 階段)
│   ├── structure.md                                   <- 程式架構與函數索引
│   ├── development_guide.md                           <- 開發規範與檢查清單
│   ├── coding_templates.md                            <- 程式寫法範本
│   ├── logic_flowcharts.md                            <- 邏輯判斷範本
│   ├── sound_notification_system.md                   <- 音效通知系統
│   └── ticket_seat_selection_algorithm.md             <- 座位選擇演算法
│
├── 03-mechanisms/                                     <- 12 階段機制文件
│   ├── README.md                                      <- 機制文件索引
│   ├── 01-environment-init.md                         <- Stage 1: 環境初始化
│   ├── 02-authentication.md                           <- Stage 2: 身份認證
│   ├── 03-page-monitoring.md                          <- Stage 3: 頁面監控
│   ├── 04-date-selection.md                           <- Stage 4: 日期選擇
│   ├── 05-area-selection.md                           <- Stage 5: 區域選擇
│   ├── 06-ticket-count.md                             <- Stage 6: 票數設定
│   ├── 07-captcha-handling.md                         <- Stage 7: 驗證碼處理
│   ├── 08-form-filling.md                             <- Stage 8: 表單填寫
│   ├── 09-terms-agreement.md                          <- Stage 9: 條款同意
│   ├── 10-order-submit.md                             <- Stage 10: 訂單送出
│   ├── 11-queue-payment.md                            <- Stage 11: 排隊付款
│   ├── 12-error-handling.md                           <- Stage 12: 錯誤處理
│   ├── 13-active-polling-pattern.md                   <- 跨階段: 刷新等待機制
│   ├── 14-hot-reload.md                               <- 跨階段: 即時設定修改
│   ├── 15-cloudflare-turnstile.md                     <- 跨階段: Turnstile 偵測
│   ├── 16-yii2-captcha-hash.md                        <- 跨階段: Yii2 驗證碼雜湊
│   ├── 17-multi-instance.md                           <- 跨階段: 多開實例隔離
│   └── 18-universal-ocr-model.md                      <- 跨階段: 通用 OCR 模型選擇
│
├── 04-implementation/                                 <- 平台實作參考
│   ├── README.md                                      <- 平台參考索引
│   ├── debug-logger-spec.md                           <- Debug Logger 規格書
│   └── platform-examples/                             <- 各平台參考
│
├── 05-validation/                                     <- 驗證系統
│   ├── README.md                                      <- 驗證系統索引
│   ├── spec-validation-matrix.md                      <- FR 規格驗證矩陣
│   ├── platform-checklist.md                          <- 平台實作檢查清單
│   └── fr-to-code-mapping.md                          <- FR 到程式碼對照表
│
├── 06-api-reference/                                  <- API 參考文件
│   ├── README.md                                      <- API 文件索引
│   ├── zendriver_api_guide.md                         <- Zendriver API 指南（主要參考）
│   ├── cdp_protocol_reference.md                      <- CDP 完整參考
│   ├── shadow_dom_pierce_guide.md                     <- Shadow DOM 穿透指南
│   ├── ddddocr_api_guide.md                           <- 驗證碼識別 API
│   ├── nodriver_api_guide.md                          <- NoDriver API 指南（已棄用）
│   └── nodriver_selector_analysis.md                  <- NoDriver Selector 分析（已棄用）
│
└── 07-deployment/                                     <- 部署打包
    ├── README.md                                      <- 部署索引
    └── pyinstaller_packaging_guide.md                 <- PyInstaller 打包指南
```

---

## 常見使用場景

### 場景 1：我想開發新平台支援

**開發流程：**
```
ticket_automation_standard.md -> structure.md -> development_guide.md -> API 指南
```

1. 閱讀 [ticket_automation_standard.md](02-development/ticket_automation_standard.md) 了解標準流程 (12 階段)
2. 查看 [structure.md](02-development/structure.md) 參考現有平台實作 (含完成度評分)
3. 查看對應的 [API 指南](06-api-reference/)：
   - **Zendriver (主要參考)** → [zendriver_api_guide.md](06-api-reference/zendriver_api_guide.md)
   - **CDP 協議 (深入)** → [cdp_protocol_reference.md](06-api-reference/cdp_protocol_reference.md)
4. 遵循 [development_guide.md](02-development/development_guide.md) 的規範
5. 參考 [coding_templates.md](02-development/coding_templates.md) 的程式範本

### 場景 2：我想了解專案架構

1. **總覽**：從 [project_overview.md](01-getting-started/project_overview.md) 開始
2. **程式結構**：查看 [structure.md](02-development/structure.md) 了解函數索引
3. **標準流程**：閱讀 [ticket_automation_standard.md](02-development/ticket_automation_standard.md) 了解 12 階段標準
4. **座位選擇邏輯**：查看 [ticket_seat_selection_algorithm.md](02-development/ticket_seat_selection_algorithm.md)

### 場景 3：我要打包部署

- [PyInstaller 打包指南](07-deployment/pyinstaller_packaging_guide.md) - 完整打包流程
- [本地測試打包](../build_scripts/QUICK_START.md) - 5 分鐘快速開始

---

## 重點文件速查

| 文件 | 用途 | 適用對象 |
|------|------|----------|
| [ticket_automation_standard.md](02-development/ticket_automation_standard.md) | 標準功能定義 (12 階段) | 開發者 |
| [structure.md](02-development/structure.md) | 程式架構索引與完成度評分 | 所有人 |
| [zendriver_api_guide.md](06-api-reference/zendriver_api_guide.md) | Zendriver API 指南（主要參考） | 開發者 |
| [cdp_protocol_reference.md](06-api-reference/cdp_protocol_reference.md) | CDP 協議完整參考 | Zendriver 開發者 |
| [nodriver_api_guide.md](06-api-reference/nodriver_api_guide.md) | NoDriver API 指南（已棄用） | 遷移前參考 |

---

## 文件分類說明

### 01-getting-started/ - 新手入門
適合第一次接觸專案的開發者或使用者。包含專案概覽、環境設定。

### 02-development/ - 開發指南
開發新平台支援或新功能時必讀。包含標準流程定義、程式架構、開發規範、程式範本。

### 03-mechanisms/ - 12 階段機制文件
詳細的票券自動化流程文件。每個階段涵蓋流程說明、代碼範例、平台特定考量。

### 04-implementation/ - 平台實作參考
針對各個售票平台的具體實作參考文件。包含特定平台的選擇器、API 用法、常見問題。

### 05-validation/ - 驗證系統
規格驗證、平台實作狀態追蹤。包含 FR 需求對應、代碼映射、完成度評分。

### 06-api-reference/ - API 參考文件
各 WebDriver 引擎的 API 使用指南。

### 07-deployment/ - 部署打包
生產環境部署與打包指南。包含 PyInstaller 打包流程、依賴管理。

---

## 文件維護

文件撰寫與程式碼同步規範見專案開發規則 `.claude/rules/documentation.md`；歷史版本的文件維護流程保留於 [internal/archived/documentation_workflow.md](internal/archived/documentation_workflow.md)。

---

**最後更新：** 2026-06-14
