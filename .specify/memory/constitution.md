# Tickets Hunter 憲章

<!--
SYNC IMPACT REPORT
==================
版本變更：2.1.0 → 2.2.0
修改類型：MINOR（放寬例外處理規則）
修改日期：2026-01-05

本次更新內容：
- 第 IX 條「例外處理」從 MUST 降級為 SHOULD
- 新增 4 種允許空 except: pass 的情況：
  1. 回退模式（Fallback Pattern）
  2. 可選操作（Non-critical）
  3. 預期的超時/失敗
  4. 重試模式（Retry Pattern）
- 保留關鍵操作的錯誤處理要求

修改原因：
- 原規則對搶票自動化程式過於嚴苛
- 許多「失敗」是預期行為（元素未載入、超時等）
- 速度優先，過多日誌會拖慢執行

需同步更新的模板文件：
✅ constitution.md - 本次更新
⬜ CLAUDE.md - 原則速記表第 IX 條說明調整

修訂歷史：
- v2.2.0 (2026-01-05): 放寬第 IX 條例外處理規則，從 MUST 改為 SHOULD
- v2.1.0 (2025-12-26): 新增測試紀律（第 VIII 條）與例外處理（第 IX 條）規則
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

### 提交前測試（SHOULD）

執行 `/gsave` 前應先執行測試驗證：
- 確認現有測試仍然通過
- 新功能應有對應測試
- 允許例外：緊急修復、文件變更、配置調整

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
- **新增/修改 API** → 更新相關 API 文件

**例外**：小修復或實驗性變更可暫緩文件更新。

---

## VIII. 測試紀律

### 測試撰寫（SHOULD）

**規則**：新功能開發應包含對應的單元測試。

**適用範圍**：
- 新增公開函數或類別
- 修改核心業務邏輯
- 修復已知 bug（防止回歸）

**例外情況**：
- 緊急修復（需在後續補測試）
- UI 相關變更（難以自動化測試）
- 實驗性功能（尚未確定最終設計）

### 修改後驗證（SHOULD）

**規則**：程式碼修改後應執行相關測試確認無回歸。

**驗證方式**：
- 執行受影響模組的單元測試
- 執行快速整合測試（`timeout 30 python -u src/...`）
- 手動驗證（需記錄步驟）

### 測試通過門檻（MUST）

**規則**：測試失敗的程式碼不得合併。

**強制要求**：
- 所有現有測試必須通過
- 若測試失敗，必須修正至通過
- 禁止跳過或停用失敗的測試（除非有明確理由並記錄）

### 重構保護（MUST）

**規則**：重構不得破壞現有測試結構。

**禁止的行為**：
- 刪除或停用現有測試以「修復」測試失敗
- 修改測試期望值以配合錯誤的實作
- 降低測試覆蓋率而無合理理由

**允許的行為**：
- 因 API 變更而更新測試（需同步更新測試邏輯）
- 移除已廢棄功能的對應測試
- 重構測試程式碼以提升可維護性

---

## IX. 例外處理（SHOULD）

### 空的 except 使用規範

**規則**：空的 `except: pass` 應符合以下任一條件，否則需加入日誌或處理邏輯。

**允許的情況**：

1. **回退模式（Fallback Pattern）**：失敗後有後續替代方案
```python
# 允許：有回退邏輯
try:
    date_elem = await item.query_selector('span.timezoneSuffix')
except:
    pass  # 繼續嘗試下一個選擇器

if not date_text:  # 回退到其他選擇器
    date_elem = await item.query_selector('.event-info > p')
```

2. **可選操作（Non-critical）**：失敗不影響主流程
```python
# 允許：日誌輸出失敗不影響功能
try:
    area_text = await target_area.inner_text
    print(f"[AREA SELECT] Selected: {area_text}")
except:
    pass  # 文字擷取失敗時跳過日誌
```

3. **預期的超時/失敗**：在自動化流程中屬正常情況
```python
# 允許：等待元素超時是預期行為
try:
    await tab.wait_for('#gameList', timeout=3)
except:
    pass  # timeout 沒關係，繼續嘗試讀取
```

4. **重試模式（Retry Pattern）**：多種方法依序嘗試
```python
# 允許：點擊失敗時嘗試 JS 方法
try:
    await element.click()
except:
    try:
        await element.evaluate('el => el.click()')
    except:
        pass  # 所有方法都失敗，繼續下一步
```

**禁止的模式**：
```python
# 禁止：關鍵操作無任何處理
try:
    save_user_data(data)
except:
    pass  # 資料遺失但無人知曉

# 禁止：隱藏真正的錯誤
try:
    config = load_config()
except:
    pass  # 配置載入失敗會導致後續崩潰
```

**最佳實踐**：
- 關鍵操作（資料儲存、配置載入）必須有錯誤處理或日誌
- 空的 `except: pass` 建議加上簡短註解說明忽略原因
- 優先使用具體例外類型（如 `except TimeoutError`）而非裸露的 `except`

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

**版本**：2.2.0 | **通過日期**：2025-10-19 | **最後修訂**：2026-01-05
