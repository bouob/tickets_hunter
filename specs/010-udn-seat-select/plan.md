# 實作計畫：UDN 售票網自動搶票功能

**分支**：`010-udn-seat-select` | **日期**：2025-12-17 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/010-udn-seat-select/spec.md` 的功能規格

## 摘要

實作 UDN 售票網 (tickets.udnfunlife.com) 完整搶票自動化功能，包含：
1. **座位自動選擇**（核心新功能）- UDN 採用「逐位選擇」模式，需在彈出視窗中自動選擇座位
2. **場次日期選擇與遞補** - 整合 Feature 003 的 Early Return Pattern 與 Conditional Fallback
3. **票區自動選擇與遞補** - 支援 keyword_exclude 排除關鍵字功能
4. **完整購票流程串接** - UTK0201 → UTK0203 → UTK0204 → 選位視窗 → 購物車

**關鍵發現**：UDN 是 KHAM 家族成員，共用相同的 UTK 後端系統。現有 KHAM 座位選擇邏輯 (`nodriver_kham_seat_auto_select()`) 可直接複用。

## 技術環境

**語言/版本**：Python 3.10+
**主要相依性**：
- NoDriver（瀏覽器自動化框架）
- CDP (Chrome DevTools Protocol)
- ddddocr（OCR 驗證碼辨識）
**儲存**：JSON 設定檔（`settings.json`）
**測試**：
- 快速測試：`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`
- MCP 即時除錯：`/mcpstart`
**目標平台**：Windows（主要）、Linux、macOS
**專案類型**：單一專案（CLI 工具）
**效能目標**：
- 座位選擇完成時間 < 5 秒
- 完整購票流程 < 15 秒
**限制**：
- 禁止使用 emoji（Windows cp950 編碼限制）
- reCaptcha 暫不處理
**規模/範圍**：
- 新增 3-4 個函數
- 修改現有 KHAM 主流程以支援 UDN 分支

## 憲法檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

| 原則 | 狀態 | 說明 |
|------|------|------|
| **I. NoDriver First** | ✅ 通過 | 使用 NoDriver 實作，符合技術優先級 |
| **II. 資料結構優先** | ✅ 通過 | data-model.md 定義實體關係 |
| **III. 三問法則** | ✅ 通過 | (1) 是核心問題 (2) 複用 KHAM 邏輯最簡單 (3) 不破壞相容性 |
| **IV. 單一職責** | ✅ 通過 | 各函數職責明確：日期選擇、區域選擇、座位選擇 |
| **V. 設定驅動** | ✅ 通過 | 所有行為由 settings.json 控制 |
| **VI. 測試驅動** | ✅ 通過 | 可透過快速測試指令驗證 |
| **VII. MVP 原則** | ✅ 通過 | P1 座位選擇 → P2 遞補機制 → P3 流程整合 |
| **VIII. 文件同步** | ✅ 通過 | 更新 structure.md 與 CHANGELOG |
| **IX. Git 規範** | ✅ 通過 | 使用 /gsave 提交，遵循 Conventional Commits |

## 專案結構

### 文件（此功能）

```text
specs/010-udn-seat-select/
├── spec.md              # 功能規格（已完成）
├── plan.md              # 此檔案
├── research.md          # 階段 0 輸出
├── data-model.md        # 階段 1 輸出
├── quickstart.md        # 階段 1 輸出
├── contracts/           # 階段 1 輸出
│   ├── udn-seat-interface.md
│   └── settings-schema.md
└── checklists/
    └── requirements.md  # 品質檢查清單（已完成）
```

### 原始碼（儲存庫根目錄）

```text
src/
├── nodriver_tixcraft.py    # 主程式（修改：新增 UDN 座位選擇邏輯）
│   ├── nodriver_udn_seat_auto_select()      # 新增：座位自動選擇
│   ├── nodriver_kham_date_auto_select()     # 修改：整合 Feature 003
│   ├── nodriver_kham_area_auto_select()     # 修改：整合 Feature 003
│   └── nodriver_kham_main()                 # 修改：新增 UDN 流程分支
├── settings.json           # 設定檔（新增：date_auto_fallback、area_auto_fallback）
└── util.py                 # 工具函式（複用：關鍵字解析邏輯）
```

**結構決策**：採用單一專案結構，新增函數整合至現有 `nodriver_tixcraft.py`，符合現有平台實作模式。

## 複雜度追蹤

> **無違規需要合理化**。本功能採用最簡方案：直接複用 KHAM 座位選擇邏輯。

## 實作策略

### 核心發現

根據研究，UDN 與 KHAM 共用相同的 UTK 後端系統：
- 座位選擇器完全相同：`#TBL td.empty`、`.stageDirection`
- 票種選擇器完全相同：`button[onclick*="setType"]`
- URL 模式相同：`utk0201_`、`utk0203_`、`utk0205_`

**結論**：可直接複用 `nodriver_kham_seat_main()` 和 `nodriver_kham_seat_auto_select()` 邏輯。

### 實作方案

**方案 A（推薦）：條件分支複用**

在現有 KHAM 函數中新增 UDN 網域判斷：
```python
if 'udnfunlife.com' in domain_name:
    # UDN 流程（複用 KHAM 邏輯）
    await nodriver_kham_seat_main(tab, config_dict, ocr, domain_name)
```

**優點**：
- 程式碼複用最大化
- 維護成本最低
- 符合 DRY 原則

### 修改清單

| 檔案 | 函數 | 修改類型 | 說明 |
|------|------|----------|------|
| `nodriver_tixcraft.py` | `nodriver_kham_main()` | 修改 | 新增 UDN 網域判斷，呼叫座位選擇 |
| `nodriver_tixcraft.py` | `nodriver_kham_date_auto_select()` | 修改 | 整合 Feature 003 遞補機制 |
| `nodriver_tixcraft.py` | `nodriver_kham_area_auto_select()` | 修改 | 整合 Feature 003 遞補機制 |
| `nodriver_tixcraft.py` | `nodriver_udn_seat_auto_select()` | 新增 | UDN 座位選擇（複用 KHAM 邏輯） |
| `settings.json` | - | 修改 | 新增 date_auto_fallback、area_auto_fallback |

### 現有程式碼位置參考

| 函數 | 行號 | 用途 |
|------|------|------|
| `nodriver_kham_seat_auto_select()` | 18770-19132 | 座位選擇核心邏輯（可複用） |
| `nodriver_kham_seat_main()` | 19135-19360 | 座位選擇主流程（可複用） |
| `nodriver_kham_date_auto_select()` | 12200-12462 | 日期選擇（需整合 Feature 003） |
| `nodriver_kham_area_auto_select()` | 12463-13022 | 區域選擇（需整合 Feature 003） |
| `nodriver_kham_main()` | 17400-17800 | 主流程控制（需新增 UDN 分支） |

## 階段規劃

### 階段 0：研究 ✅

- [x] 分析現有 KHAM 座位選擇實作
- [x] 確認 UDN 與 KHAM DOM 結構相同
- [x] 確認選擇器可直接複用
- [x] 產生 research.md

### 階段 1：設計

- [ ] 產生 data-model.md（座位、票區、場次實體）
- [ ] 產生 contracts/（函數介面、設定 schema）
- [ ] 產生 quickstart.md（快速開始指南）

### 階段 2：任務分解（/speckit.tasks）

- [ ] 產生 tasks.md（細部任務清單）

### 階段 3：實作（/speckit.implement）

- [ ] 實作 P1：座位自動選擇
- [ ] 實作 P2：日期/區域遞補機制
- [ ] 實作 P3：完整流程串接
- [ ] 測試驗證
- [ ] 文件同步
