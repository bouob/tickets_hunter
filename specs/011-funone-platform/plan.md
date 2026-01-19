# 實作計畫：FunOne Tickets 平台支援

**分支**：`011-funone-platform` | **日期**：2026-01-13 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/011-funone-platform/spec.md` 的功能規格

## 摘要

實作 FunOne Tickets 購票平台的 NoDriver 自動化支援，涵蓋 Cookie 快速登入、場次選擇、票種選擇、張數設定、驗證碼處理與訂單提交。FunOne 使用 OTP 登入機制，Cookie 快速登入是唯一可自動化的登入方式。

**核心挑戰**：
- FunOne 無傳統帳密登入，需透過 Cookie 注入實現快速登入
- 購票流程使用 WebSocket 即時通訊
- 圖形驗證碼需人工輸入

## 技術環境

**語言/版本**：Python 3.11+
**主要相依性**：NoDriver、CDP (Chrome DevTools Protocol)
**儲存**：settings.json（設定檔）、記憶體狀態字典
**測試**：pytest、手動測試（`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`）
**目標平台**：Windows（主要）、macOS、Linux
**專案類型**：單一專案（整合到現有 nodriver_tixcraft.py）
**效能目標**：場次/票種選擇 < 2秒、Cookie 注入 < 3秒
**限制**：無 OCR 自動驗證碼（需人工輸入）、Cookie 24 小時有效期
**規模/範圍**：單一平台新增，約 13 個函數

## 憲法檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

### 階段 0 前檢查

| 原則 | 狀態 | 說明 |
|------|------|------|
| I. 技術架構（NoDriver First） | ✅ 通過 | 使用 NoDriver 實作，遵循優先順序 |
| II. 共用庫保護 | ✅ 通過 | 使用現有 util.py 函數，不修改 |
| III. 設定驅動 | ✅ 通過 | 所有設定由 settings.json 控制 |
| IV. 程式碼安全（Emoji 禁令） | ✅ 通過 | 程式碼禁止 emoji |
| V. Git 工作流程 | ✅ 通過 | 使用 /gsave 提交 |
| VI. 測試驗證 | ⏳ 待執行 | 實作後需測試 |
| VII. 文件同步 | ⏳ 待執行 | 實作後更新 structure.md |
| VIII. 測試紀律 | ⏳ 待執行 | 需新增測試 |

### 關卡結果：通過

## 專案結構

### 文件（此功能）

```text
specs/011-funone-platform/
├── spec.md              # 功能規格
├── plan.md              # 此檔案
├── research.md          # 階段 0 研究輸出
├── data-model.md        # 階段 1 資料模型
├── quickstart.md        # 階段 1 快速開始指南
├── contracts/           # 階段 1 契約定義
│   └── config-schema.md # 設定檔結構
├── checklists/          # 檢查清單
│   └── requirements.md  # 需求檢查清單
└── tasks.md             # 階段 2 任務清單（由 /speckit.tasks 產生）
```

### 原始碼（儲存庫根目錄）

```text
src/
├── nodriver_tixcraft.py    # 主程式（新增 FunOne 函數）
├── util.py                 # 共用函數（不修改）
└── settings.json           # 設定檔（新增 FunOne 欄位）

tests/
├── test_funone.py          # FunOne 單元測試（新增）
└── integration/
    └── test_funone_flow.py # FunOne 整合測試（新增）
```

**結構決策**：整合到現有 `nodriver_tixcraft.py`，遵循專案現有架構。FunOne 函數將位於 HKTicketing 函數之後（約第 24100+ 行）。

## 複雜度追蹤

> 無憲法違規需合理化。

## 實作策略

### 實作函數清單

依據 12 階段標準，以下是需實作的函數：

| 序號 | 函數名稱 | 12 階段 | 優先級 | 預估行數 |
|------|----------|---------|--------|----------|
| 1 | `nodriver_funone_main` | 主流程 | P1 | 100 |
| 2 | `nodriver_funone_inject_cookie` | 階段 2 | P1 | 50 |
| 3 | `nodriver_funone_check_login_status` | 階段 2 | P1 | 30 |
| 4 | `nodriver_funone_verify_login` | 階段 2 | P1 | 30 |
| 5 | `nodriver_funone_auto_reload` | 階段 3 | P2 | 50 |
| 6 | `nodriver_funone_close_popup` | 階段 3 | P3 | 30 |
| 7 | `nodriver_funone_date_auto_select` | 階段 4 | P1 | 120 |
| 8 | `nodriver_funone_area_auto_select` | 階段 5 | P1 | 120 |
| 9 | `nodriver_funone_assign_ticket_number` | 階段 6 | P1 | 60 |
| 10 | `nodriver_funone_captcha_handler` | 階段 7 | P1 | 50 |
| 11 | `nodriver_funone_ticket_agree` | 階段 9 | P3 | 40 |
| 12 | `nodriver_funone_order_submit` | 階段 10 | P2 | 60 |
| 13 | `nodriver_funone_error_handler` | 階段 12 | P2 | 50 |

**總預估**：約 790 行程式碼

### 實作順序

1. **Phase 1**：主流程 + Cookie 登入（函數 1-4）
2. **Phase 2**：日期/票種選擇（函數 7-9）
3. **Phase 3**：驗證碼 + 訂單提交（函數 10, 12）
4. **Phase 4**：頁面監控 + 錯誤處理（函數 5, 6, 11, 13）

### 整合點

在 `nodriver_tixcraft.py` 的 `main()` 函數中新增路由（約第 24527 行後）：

```python
# FunOne 路由
if 'tickets.funone.io' in url:
    tab = await nodriver_funone_main(tab, url, config_dict)
```

### 設定檔新增欄位

在 `settings.json` 的 `advanced` 區塊新增：

```json
"advanced": {
    "funone_session_cookie": "",        // ticket_session Cookie 值
    "funone_ticket_number": 2           // 購票張數（可選，預設使用 ticket_number）
}
```

## 下一步

1. 執行 `/speckit.tasks` 產生詳細任務清單
2. 按 Phase 1-4 順序實作
3. 每個 Phase 完成後執行測試驗證
