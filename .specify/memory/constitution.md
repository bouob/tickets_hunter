# Tickets Hunter 憲章

<!--
SYNC IMPACT REPORT
==================
版本變更：1.1.0 → 2.0.0
修改類型：MAJOR（重新定義原則結構，移除思想限制，精簡內容）
修改日期：2025-12-23

本次更新內容：
- 重新定義憲法目的：僅限制行為，不限制思想
- 簡化規則分類為兩級：MUST（強制）與 SHOULD（建議）
- 移除 FRAMEWORK 類別（思維框架不屬於憲法範疇）
- 精簡 9 大原則為 6 大行為規範
- 新增 util.py 共用庫保護規則
- 移除過度詳細的文件結構（避免過時）
- 移除官僚式治理流程（不適用個人專案）
- 更新文件路徑以符合實際目錄結構

設計理念：
- 憲法是「行為紅線」而非「思考指南」
- Claude Opus 4.5 具備高度智慧，只需告知禁區
- 簡潔明確 > 詳盡冗長
- 能用 CLAUDE.md 或 docs/ 說明的，不寫入憲法

移除的原則（改為 CLAUDE.md 中的開發指南）：
- 第 II 條「資料結構優先」→ 開發建議，非強制行為
- 第 III 條「三問法則」→ 決策框架，非強制行為
- 第 VII 條「MVP 原則」→ 優先級建議，非強制行為

需同步更新的模板文件：
✅ CLAUDE.md - 版本引用（2.0.0）、原則速記表調整
⬜ plan-template.md - 「憲法檢查」區塊可簡化
⬜ spec-template.md - 無需更新
⬜ tasks-template.md - 無需更新

修訂歷史：
- v2.0.0 (2025-12-23): 重新定義為行為規範，精簡原則，新增共用庫保護
- v1.1.0 (2025-12-23): 規則層級系統與例外處理機制
- v1.0.1 (2025-10-28): 文件結構澄清與補充
- v1.0.0 (2025-10-19): 首次通過，建立 9 大核心原則
-->

## 憲法定位

本憲章定義 **不可違反的行為規則**，是專案開發的紅線。

**憲法不做的事**：
- 不限制思考方式或決策邏輯
- 不規定開發流程或設計模式
- 不提供思維框架或最佳實踐指南

**思維框架與開發指南**：請參閱 `CLAUDE.md` 與 `docs/` 目錄。

---

## 規則分類

### MUST（必須）
違反會導致系統錯誤、安全問題、資料洩露、程式崩潰。
**無例外**，除非有明確記錄的技術限制。

### SHOULD（應該）
最佳實踐，違反可能降低品質但不會導致失敗。
**允許合理例外**，需在 commit 中記錄理由。

---

## I. 技術架構（MUST）

### NoDriver First

| 優先級 | 引擎 | 狀態 |
|--------|------|------|
| 1 | NoDriver | 推薦、預設、新功能開發 |
| 2 | Undetected Chrome (UC) | 備選、需額外反偵測時 |
| 3 | Selenium | 維護模式、僅嚴重錯誤修復 |

**規則**：
- 新功能必須首先在 `nodriver_tixcraft.py` 實作
- `chrome_tixcraft.py` 僅接受安全補丁與嚴重錯誤修復
- 不支援的平台必須在 `README.md` 記錄理由

---

## II. 共用庫保護（MUST）

### util.py 改動規則

`util.py` 是所有平台與所有 driver 的共用函式庫，任何改動都可能產生跨平台影響。

**改動前必須**：
1. **影響分析**：識別所有呼叫該函數的位置（使用 `grep` 或 IDE 搜尋）
2. **跨平台驗證**：確認改動不會破壞其他平台（TixCraft、KKTIX、iBon、TicketPlus 等）
3. **跨 Driver 驗證**：確認改動同時適用於 NoDriver 與 Chrome Driver

**禁止的行為**：
- 未經分析直接修改共用函數
- 為單一平台需求破壞通用介面
- 刪除看似「未使用」的函數（可能被其他 driver 使用）

**建議做法**：
- 新增函數優先於修改現有函數
- 平台特定邏輯放在平台模組（如 `tixcraft_*`、`kktix_*`），而非 util.py
- 改動後執行多平台快速測試

---

## III. 設定驅動（MUST）

**核心規則**：所有可配置行為必須由 `settings.json` 控制，禁止硬寫。

**禁止硬寫的項目**：
- 使用者可選的功能開關
- 票數、日期、區域等選擇邏輯
- Debug 模式、headless 模式等執行參數

**允許硬寫的項目**：
- 平台 URL、CSS 選擇器（在平台模組中定義常數）
- 內部實作邏輯（非使用者可控）

---

## IV. 程式碼安全（MUST）

### Emoji 禁令

| 檔案類型 | Emoji |
|----------|-------|
| `.py`, `.js` | **禁止** |
| `.md` | 允許 |

**原因**：emoji 在 Windows cp950 編碼下導致程式崩潰。

```python
# 正確
print("[SUCCESS] 購票成功")

# 禁止
print("✅ 購票成功")
```

### 敏感資訊

- 禁止在程式碼或版本控制中硬寫密碼、API 金鑰
- `.gitignore` 必須排除 `settings.json`、`.env`
- 日誌中禁止記錄帳號、密碼、身份證號

---

## V. Git 工作流程（MUST）

### 提交規範

使用 `/gsave` 建立 commit，禁止手動 `git commit`。

**Commit 格式**：Conventional Commits
```
<type>(<scope>): <subject>
```

**Type**：`feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `chore`, `ci`

### 雙 Repo 安全

| 操作 | 允許 | 禁止 |
|------|------|------|
| 提交 | `/gsave` | `git commit` |
| 推送到私人庫 | `/gpush` | - |
| 發布到公開庫 | `/publicpr` | `git push origin` |
| 拉取公開庫 | - | `git pull origin`（單向流程） |

**私人檔案模式**：`.claude/`, `docs/`, `CLAUDE.md`, `.specify/`, `specs/`, `FAQ/`

---

## VI. 測試驗證（SHOULD）

**規則**：核心功能修改應有對應測試驗證。

**測試方式**（依優先級）：
1. 自動化測試（pytest）
2. 快速測試指令（`timeout 30 python -u src/nodriver_tixcraft.py ...`）
3. 手動測試（需在 PR 中記錄步驟）

**例外**：緊急修復可先提交，後補測試。

---

## VII. 文件同步（SHOULD）

**規則**：程式碼變更應同步更新相關文件。

**同步檢查清單**：
- 新增/修改函數 → 更新 `docs/02-development/structure.md`
- 新增平台支援 → 更新 `README.md`
- 修改配置 schema → 更新 `specs/.../contracts/config-schema.md`
- Breaking changes → 更新 `CHANGELOG.md`

**例外**：小修復或實驗性變更可暫緩文件更新。

---

## 品質底線

### 暫停機制（MUST）

- 購票流程前必須有確認機制
- 支援 Ctrl+C 優雅中止
- 自動化操作必須有清晰日誌

### 安全性（MUST）

- 不蒐集或上傳使用者個人資訊
- Cookie 與 session 應在進程結束時清理
- 涉及敏感操作的改動需審查

---

## 治理

### 修訂方式

憲法可透過 `/speckit.constitution` 指令修訂。

版本遞增規則（語意化版本）：
- **MAJOR**：移除或重新定義規則
- **MINOR**：新增規則
- **PATCH**：措辭修正、錯別字

### 違規處理

違反 MUST 規則的提交：
1. 標記為阻擋（blocking）
2. 必須修正後才能合併

違反 SHOULD 規則的提交：
1. 記錄理由即可
2. 後續迭代改善

---

## 核心文件索引

| 用途 | 文件 |
|------|------|
| 開發入口 | `CLAUDE.md` |
| 功能規格 | `specs/001-ticket-automation-system/spec.md` |
| 程式結構 | `docs/02-development/structure.md` |
| NoDriver API | `docs/06-api-reference/nodriver_api_guide.md` |
| 除錯方法 | `docs/07-testing-debugging/debugging_methodology.md` |
| Git 工作流程 | `docs/12-git-workflow/dual-repo-workflow.md` |

---

**版本**：2.0.0 | **通過日期**：2025-10-19 | **最後修訂**：2025-12-23
