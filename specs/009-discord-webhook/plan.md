# 實作計畫：Discord Webhook 通知

**分支**：`009-discord-webhook` | **日期**：2025-12-04 | **規格**：[spec.md](./spec.md)
**輸入**：來自 `/specs/009-discord-webhook/spec.md` 的功能規格

---

## 摘要

實作搶票成功時的 Discord Webhook 通知功能。使用者只需在 settings.html 網頁介面填入一個 Discord Webhook URL，系統即可在找到票券（階段1）和訂單成功（階段2）時發送通知到指定的 Discord 頻道。

**技術方法**：
- 複用現有 `play_sound` 通知機制的觸發點和防重複標記
- 使用 `threading.Thread` + `requests.post` 進行非同步 HTTP POST
- 靜默處理所有錯誤，確保不影響主搶票流程

---

## 技術環境

**語言/版本**：Python 3.8+
**主要相依性**：requests（現有依賴）、threading（內建）
**儲存**：settings.json（現有機制）
**測試**：手動測試（需實際 Discord Webhook）
**目標平台**：Windows（主要）、macOS、Linux
**專案類型**：桌面應用程式（單一專案）
**效能目標**：通知發送不阻塞主流程
**限制**：Webhook 超時 <= 3 秒（SC-003）
**規模/範圍**：每次搶票最多 2 次通知（ticket + order）

---

## 憲法檢查

*關卡：所有項目通過*

| 原則 | 檢查項目 | 狀態 | 說明 |
|------|----------|------|------|
| **I. NoDriver First** | 功能是否支援 NoDriver | PASS | 在 nodriver_tixcraft.py 實作 |
| **II. 資料結構優先** | 是否先定義資料模型 | PASS | data-model.md 已完成 |
| **III. 三問法則** | 是否核心問題 | PASS | 通知是使用者需求的核心 |
| **III. 三問法則** | 是否最簡方案 | PASS | 單一 URL 欄位，複用現有機制 |
| **III. 三問法則** | 是否破壞相容性 | PASS | 新增欄位預設空字串，不影響現有功能 |
| **IV. 單一職責** | 函數設計是否單一職責 | PASS | 分離 build_message、send_webhook、send_async |
| **V. 設定驅動** | 是否透過 settings.json 配置 | PASS | discord_webhook_url 欄位 |
| **VI. 測試驅動** | 是否可測試 | PASS | 同步函數可單元測試 |
| **VII. MVP 原則** | 是否聚焦 MVP | PASS | 只做 URL 設定和發送，不做重試等進階功能 |
| **VIII. 文件同步** | 是否更新文件 | PENDING | 實作完成後更新 structure.md |
| **IX. Git 規範** | 是否遵循 commit 規範 | PENDING | 使用 /gsave 提交 |

---

## 專案結構

### 文件（此功能）

```text
specs/009-discord-webhook/
├── spec.md              # 功能規格（已完成）
├── plan.md              # 此檔案
├── research.md          # 技術研究（已完成）
├── data-model.md        # 資料模型（已完成）
├── quickstart.md        # 快速開始指南（已完成）
├── contracts/
│   ├── config-schema.md # 設定 Schema（已完成）
│   └── webhook-interface.md # Webhook 函數契約（已完成）
└── tasks.md             # 實作任務清單（已完成）
```

### 原始碼（儲存庫根目錄）

```text
src/
├── settings.json           # [修改] 新增 discord_webhook_url 欄位
├── util.py                 # [修改] 新增 webhook 相關函數
├── nodriver_tixcraft.py    # [修改] 整合 webhook 呼叫
└── www/
    ├── settings.html       # [修改] 新增 Webhook URL 表單欄位
    └── settings.js         # [修改] 新增載入/儲存邏輯
```

**結構決策**：維持現有單一專案結構，不新增目錄。所有修改集中在現有檔案中。

---

## 複雜度追蹤

> 本功能符合所有憲法原則，無需合理化違規。

| 項目 | 檢查結果 |
|------|----------|
| 新增函數數量 | 3 個（符合單一職責） |
| 修改檔案數量 | 5 個（最小必要） |
| 新增設定欄位 | 1 個（符合簡單設定原則） |
| 相依性變更 | 無（使用現有 requests） |

---

## 實作概要

### Phase 2 任務預覽（待 /speckit.tasks 生成）

**P1 任務**（MVP - 必須完成）：
1. 新增 util.py webhook 函數
2. 修改 settings.json 新增欄位
3. 修改 settings.html 新增表單
4. 修改 settings.js 新增載入/儲存
5. 整合 nodriver_tixcraft.py 觸發點

**P2 任務**（重要）：
6. 測試各平台觸發點
7. 更新 structure.md 文件

---

## 階段 1 設計產出物檢查

| 產出物 | 狀態 | 路徑 |
|--------|------|------|
| research.md | DONE | specs/009-discord-webhook/research.md |
| data-model.md | DONE | specs/009-discord-webhook/data-model.md |
| quickstart.md | DONE | specs/009-discord-webhook/quickstart.md |
| config-schema.md | DONE | specs/009-discord-webhook/contracts/config-schema.md |
| webhook-interface.md | DONE | specs/009-discord-webhook/contracts/webhook-interface.md |

---

## 下一步

執行 `/speckit.tasks` 生成詳細任務清單（tasks.md）。
