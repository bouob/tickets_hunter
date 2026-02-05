# 實作計畫：FANSI GO 平台支援

**分支**：`012-fansigo-platform` | **日期**：2026-02-05 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/012-fansigo-platform/spec.md` 的功能規格

## 摘要

新增對 FANSI GO (go.fansi.me) 售票平台的自動化搶票支援。主要功能包括：
- 多場次選擇（依 date_keyword 匹配）
- 多票種區域選擇（依 area_keyword 匹配）
- Cookie 登入（FansiAuthInfo JWT）
- 追蹤器封鎖（Google Analytics、Smartlook）

技術方法：遵循現有平台支援模式，在 `nodriver_tixcraft.py` 中新增 FANSI GO 處理邏輯，使用 NoDriver CDP 操作瀏覽器。

## 技術環境

**語言/版本**：Python 3.8+（與現有專案一致）
**主要相依性**：NoDriver、asyncio、aiohttp（GraphQL 查詢可選）
**儲存**：settings.json（設定檔）、Cookie 檔案（可選）
**測試**：pytest、快速測試指令
**目標平台**：Windows（主要）、Linux/macOS（次要）
**專案類型**：單一專案（CLI 應用程式）
**效能目標**：購票流程完成時間 < 30 秒
**限制**：無驗證碼、停止於付款頁面
**規模/範圍**：單一平台支援，約 500-800 行新增程式碼

## 憲法檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

### 階段 0 前檢查（已通過）

| 原則 | 狀態 | 說明 |
|------|------|------|
| I. NoDriver First | ✅ 通過 | 使用 NoDriver 實作 |
| II. 共用庫保護 | ✅ 通過 | 平台特定邏輯在獨立函數中 |
| III. 設定驅動 | ✅ 通過 | 所有行為由 settings.json 控制 |
| IV. 程式碼安全 | ✅ 通過 | .py 檔案禁止 emoji |
| V. Git 工作流程 | ✅ 通過 | 使用 /gsave 提交 |

### 階段 1 後重新檢查

| 原則 | 狀態 | 說明 |
|------|------|------|
| I. NoDriver First | ✅ 通過 | 設計遵循 NoDriver 優先 |
| II. 共用庫保護 | ✅ 通過 | 複用現有機制，不修改 util.py 核心函數 |
| III. 設定驅動 | ✅ 通過 | 新增 fansigo_cookie 設定項，複用現有設定 |
| IV. 程式碼安全 | ✅ 通過 | 設計文件中無 emoji |
| V. Git 工作流程 | ✅ 通過 | 將使用 /gsave 提交 |
| VI. 測試驗證 | ⏳ 待實作 | 需加入 test_fansigo.py |
| VII. 文件同步 | ⏳ 待實作 | 需更新 structure.md |
| VIII. 測試紀律 | ⏳ 待實作 | 實作後需驗證 |

## 專案結構

### 文件（此功能）

```text
specs/012-fansigo-platform/
├── spec.md              # 功能規格
├── plan.md              # 此檔案
├── research.md          # 階段 0 輸出
├── data-model.md        # 階段 1 輸出
├── quickstart.md        # 階段 1 輸出
├── contracts/           # 階段 1 輸出
│   └── config-schema.md # 設定檔結構
└── tasks.md             # 階段 2 輸出
```

### 原始碼（儲存庫根目錄）

```text
src/
├── nodriver_tixcraft.py    # 主程式（新增 FANSI GO 邏輯）
├── util.py                 # 共用函數（可能新增 helper）
└── settings.py             # 設定檔處理（新增 FANSI GO 欄位）

tests/
└── unit/
    └── test_fansigo.py     # 新增：FANSI GO 測試
```

**結構決策**：遵循現有專案結構，在 `nodriver_tixcraft.py` 中新增平台處理邏輯，不建立獨立模組。

## 複雜度追蹤

> 無需合理化的違規。此功能遵循現有模式，複雜度適中。
