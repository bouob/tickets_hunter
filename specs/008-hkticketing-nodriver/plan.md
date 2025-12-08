# 實作計畫：HKTicketing NoDriver 遷移

**分支**：`008-hkticketing-nodriver` | **日期**：2025-11-27 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/008-hkticketing-nodriver/spec.md` 的功能規格

## 摘要

將 HKTicketing 平台從 Chrome UC Driver 遷移至 NoDriver 版本，包含 19 個函數的重構。主要任務是將同步 Selenium API 轉換為異步 NoDriver API，同時保持原有的頁面判斷邏輯和購票流程。遷移範圍涵蓋登入、日期選擇、區域選擇、票數設定、訂單送出及錯誤處理等完整功能。

**新增功能需求**（2025-11-27 更新）：
- **FR-026**：`date_auto_fallback` - 日期關鍵字全失敗時的自動遞補機制
- **FR-036**：`area_auto_fallback` - 區域關鍵字全失敗時的自動遞補機制

## 技術環境

**語言/版本**：Python 3.11+
**主要相依性**：
- NoDriver（核心瀏覽器自動化引擎）
- asyncio（異步執行框架）
- util.py 共用函數（`get_matched_blocks_by_keyword`、`get_target_item_from_matched_list` 等）

**儲存**：不適用（無持久化需求）
**測試**：手動整合測試（HKTicketing 實際網站）
**目標平台**：Windows 10+、macOS、Linux
**專案類型**：單一專案（CLI 應用）
**效能目標**：頁面操作回應時間 <2 秒，完整購票流程 <30 秒
**限制**：<500MB 記憶體使用，網路延遲容忍
**規模/範圍**：19 個函數遷移，3 個支援網站（HKTicketing、Galaxy Macau、Ticketek Australia）

## 憲法檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

| 原則 | 狀態 | 說明 |
|------|------|------|
| **I. NoDriver First** | ✅ 通過 | 本功能正是將 UC Driver 遷移至 NoDriver，完全符合優先策略 |
| **II. 資料結構優先** | ✅ 通過 | 重用現有 `hkticketing_dict` 狀態結構，無需新增資料模型 |
| **III. 三問法則** | ✅ 通過 | (1) 是核心問題：維護平台相容性 (2) 無更簡單方法：必須完整遷移 (3) 保持相容性：API 介面不變 |
| **IV. 單一職責** | ✅ 通過 | 保持原有函數拆分，每函數單一職責 |
| **V. 設定驅動** | ✅ 通過 | 所有行為由 `settings.json` 控制，無硬編碼。新增 `date_auto_fallback` 和 `area_auto_fallback` 設定 |
| **VI. 測試驅動** | ✅ 通過 | 遷移後需通過手動整合測試 |
| **VII. MVP 原則** | ✅ 通過 | 按 P1→P2→P3 順序實作 |
| **VIII. 文件同步** | ✅ 通過 | 完成後更新 `structure.md` 和 `README.md` |
| **IX. Git 規範** | ✅ 通過 | 使用 `/gsave` 提交 |

**Emoji 規範**：✅ 確認程式碼中不使用 emoji

## 專案結構

### 文件（此功能）

```text
specs/008-hkticketing-nodriver/
├── spec.md              # 功能規格（已完成，含 FR-026/FR-036）
├── plan.md              # 此檔案
├── research.md          # 階段 0 輸出（含 Fallback 機制研究）
├── data-model.md        # 階段 1 輸出（含 Fallback 設定欄位）
├── quickstart.md        # 階段 1 輸出
├── contracts/           # 階段 1 輸出
│   └── hkticketing-interface.md（含 Fallback 行為說明）
├── checklists/
│   └── requirements.md  # 品質檢查清單（已完成）
└── tasks.md             # 階段 2 輸出（/speckit.tasks）
```

### 原始碼（儲存庫根目錄）

```text
src/
├── nodriver_tixcraft.py     # 主要修改檔案（新增 nodriver_hkticketing_* 函數）
├── chrome_tixcraft.py       # 參考來源（現有 hkticketing_* 函數）
├── util.py                  # 共用工具函數（無需修改）
├── settings.py              # 設定定義（已含 date_auto_fallback/area_auto_fallback）
└── settings.json            # 設定檔（無需修改）
```

**結構決策**：所有 NoDriver 平台實作整合於 `nodriver_tixcraft.py` 單一檔案，遵循現有專案模式（參考 `nodriver_cityline_main` 實作）。

## 功能需求追蹤

### 核心功能（原有）

| 需求 | 說明 | 參考函數 |
|------|------|----------|
| FR-001~007 | 核心遷移需求 | 19 個函數 |
| FR-010~012 | 登入功能 | `nodriver_hkticketing_login` |
| FR-020~025 | 日期選擇功能 | `nodriver_hkticketing_date_*` |
| FR-030~035 | 區域選擇功能 | `nodriver_hkticketing_area_auto_select` |
| FR-040~041 | 票數設定功能 | `nodriver_hkticketing_ticket_number_auto_select` |
| FR-050~053 | 訂單送出功能 | `nodriver_hkticketing_*_button_press` |
| FR-060~065 | 錯誤處理功能 | `nodriver_hkticketing_url_redirect` 等 |
| FR-070 | Cookie 處理 | `nodriver_hkticketing_accept_cookie` |

### 新增功能（FR-026、FR-036）

| 需求 | 說明 | 實作位置 |
|------|------|----------|
| **FR-026** | `date_auto_fallback` - 日期關鍵字全失敗時的自動遞補機制 | `nodriver_hkticketing_date_assign` |
| **FR-036** | `area_auto_fallback` - 區域關鍵字全失敗時的自動遞補機制 | `nodriver_hkticketing_area_auto_select` |

### Fallback 機制設計

```
關鍵字匹配流程
     │
     ▼
┌─────────────────────────────┐
│   嘗試所有關鍵字組匹配       │
└──────────────┬──────────────┘
               │
        匹配成功？
       ╱        ╲
     是          否
     │           │
     ▼           ▼
┌─────────┐  ┌────────────────────────┐
│選擇匹配 │  │ 檢查 auto_fallback 設定│
│的項目   │  └───────────┬────────────┘
└─────────┘              │
                   fallback=true?
                  ╱            ╲
                是              否
                │               │
                ▼               ▼
    ┌───────────────────┐  ┌─────────────────┐
    │ 使用 auto_select  │  │ 停止選擇流程     │
    │ _mode 自動遞補    │  │（嚴格模式）      │
    └───────────────────┘  └─────────────────┘
```

### Fallback 參考實作

| 平台 | 日期 Fallback 位置 | 區域 Fallback 位置 |
|------|-------------------|-------------------|
| Cityline | `nodriver_tixcraft.py:15125-15131` | `nodriver_tixcraft.py:15407-15413` |
| KKTIX | `nodriver_tixcraft.py:1730-1741` | `nodriver_tixcraft.py:2264-2277` |
| iBon | `nodriver_tixcraft.py:10946-10955` | `nodriver_tixcraft.py:12666-12677` |

## 複雜度追蹤

> 無憲法違規需要合理化。本遷移完全符合憲法所有原則。
>
> FR-026 和 FR-036 的新增與其他平台保持一致，使用既有的 `date_auto_fallback` 和 `area_auto_fallback` 設定欄位，無需額外複雜度。
