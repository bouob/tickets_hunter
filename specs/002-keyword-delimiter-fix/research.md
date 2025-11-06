# 技術研究：關鍵字分隔符號改善

**功能**：002-keyword-delimiter-fix
**研究日期**：2025-10-28
**研究者**：Claude (AI Assistant)

## Phase 0：研究與決策

### 1. 分隔符號選擇研究

**研究任務**：評估不同分隔符號的優缺點

**候選方案**：
- **逗號 `,`**（當前）：與金額、時間格式衝突
- **分號 `;`**（推薦）：無衝突、語義清晰、易於輸入
- **管道符號 `|`**（備選）：語義清晰但輸入不便（Windows CMD 問題）
- **JSON 陣列格式**（替代）：明確但使用者輸入複雜

**決策**：採用分號 `;` 作為主要方案

**理由**：
1. **完全避免衝突**：不會與金額千位分隔符號（`3,280`）、時間格式（`09:30:00,14:15:30`）衝突
2. **保留便利性**：使用者仍可省略引號，直接輸入 `3,280;2,680`
3. **語義直覺**：分號在程式中常用作分隔符號（C/C++、JavaScript 等）
4. **實作成本最低**：全域替換 `split(',')` → `split(';')`，無需複雜邏輯

**考慮過的替代方案**：
- **管道符號 `|`**：語義清晰（OR 運算），但 Windows CMD 中是管道符號，可能造成歧義
- **JSON 陣列格式**：明確且無歧義，但使用者輸入複雜（需要引號、方括號），不符合「設定驅動開發」原則（憲法第 V 條）
- **智能檢測金額格式**：使用正則表達式判斷 `\d{1,3}(,\d{3})+`，但無法處理所有邊緣案例，維護成本高

**實作決策**：
- 主要方案：分號 `;`（FR-001）
- 進階選項：JSON 陣列格式（FR-002），但不強制使用

---

### 2. 向後相容性策略研究

**研究任務**：評估如何處理舊設定檔

**歷史分析**：
- **Legacy 分支**（commit f8f77de, 2024-04-24）：使用引號保護機制，無自動逗號分割
  - 使用者輸入：`"3,280"` → 視為單一關鍵字
  - 多關鍵字需明確引號：`"10/03","10/04"`
- **Main 分支**（commit 9b8caee, 2025-09-22 後）：引入自動逗號分割
  - 目的：簡化時間關鍵字輸入（`09:30:00,14:15:30`）
  - 副作用：金額 `3,280` 被錯誤分割為 `["3", "280"]`

**候選策略**：
1. **自動轉換**：偵測舊格式並自動轉換為新格式
2. **偵測並警告**：偵測舊格式，發出警告但不阻斷運作
3. **強制遷移**：拒絕載入舊格式設定檔

**決策**：採用「偵測並警告」策略（策略 2）

**理由**：
1. **減少誤判**：自動轉換可能產生誤判（例如：`"A,B"` 是一個還是兩個關鍵字？金額 `1,000` 是否應分割？）
2. **使用者掌控**：明確警告訊息引導使用者手動修正，減少歧義和潛在錯誤
3. **緩衝時間**：不阻斷系統啟動，給予使用者時間適應新格式
4. **符合憲法原則**：遵循憲法第 III 條「三問法則」中的相容性考量

**考慮過的替代方案**：
- **自動轉換**：風險高，可能產生誤判，違反使用者預期
- **強制遷移**：過於激進，影響使用者體驗，可能導致使用者流失

**實作方法**：
```python
# 偵測邏輯（在 util.py:is_text_match_keyword() 中）
if ',' in keyword_string and ';' not in keyword_string and not '"' in keyword_string:
    # 可能是舊格式
    if config_dict["advanced"].get("verbose", False):
        print("[WARNING] 偵測到舊格式的關鍵字設定")
        print(f"[WARNING] 當前設定: {keyword_string}")
        print(f"[WARNING] 建議格式: {keyword_string.replace(',', ';')}")
        print("[WARNING] 或使用 JSON 陣列格式")
```

---

### 3. 程式碼影響範圍研究

**研究任務**：識別所有需要修改的程式碼位置

**研究方法**：使用 `git grep "split(',')"`、`git grep "is_text_match_keyword"`

**研究發現**：

#### 核心邏輯（必須修改）
1. **`util.py:171`** - `format_config_keyword_for_json()`
   - 功能：格式化使用者輸入的關鍵字為 JSON 格式
   - 影響：GUI 介面輸入處理
   - 修改：`split(',')` → `split(';')`

2. **`util.py:185`** - `is_text_match_keyword()`
   - 功能：核心關鍵字匹配邏輯
   - 影響：所有平台的關鍵字匹配
   - 修改：`split(',')` → `split(';')`，並新增舊格式偵測

3. **`settings.py:584`** - `format_config_keyword_for_json()`
   - 功能：設定檔格式化（與 util.py 重複）
   - 影響：設定檔載入
   - 修改：`split(',')` → `split(';')`

#### 平台特定實作（必須修改）
4. **`nodriver_tixcraft.py:3875`** - 日期關鍵字解析
   - 功能：TixCraft 平台日期關鍵字處理
   - 影響：日期選擇功能
   - 修改：依賴 `is_text_match_keyword()`，間接受影響

5. **`nodriver_tixcraft.py:4035`** - 排除關鍵字解析
   - 功能：排除關鍵字處理（`keyword_exclude`）
   - 影響：區域過濾功能
   - 修改：`split(',')` → `split(';')`

6. **`chrome_tixcraft.py`** - Chrome 版本對應函數
   - 功能：Chrome WebDriver 版本實作
   - 影響：舊版 WebDriver 使用者
   - 修改：同步修改以維持一致性（憲法第 I 條）

**決策**：修改以上 6 個關鍵位置，確保一致性

**理由**：
1. 集中修改避免遺漏
2. 核心邏輯（`util.py`）修改後，平台特定實作自動受益
3. 測試時一併驗證所有位置

---

### 4. 文件更新範圍研究

**研究任務**：識別所有需要更新的文件

**研究方法**：
- 檢查 spec.md FR-004 列出的文件
- 使用 `git grep '","'` 搜尋舊格式範例
- 檢查 `docs/` 目錄結構

**研究發現**：

#### 必須更新的文件（包含關鍵字範例）
1. **`README.md`**
   - 位置：專案根目錄
   - 內容：平台支援表、快速開始範例
   - 修改：更新關鍵字格式範例

2. **`docs/01-getting-started/setup.md`**
   - 位置：安裝指南
   - 內容：settings.json 設定範例
   - 修改：更新所有關鍵字欄位範例

3. **`specs/001-ticket-automation-system/contracts/config-schema.md`**
   - 位置：配置 schema 定義
   - 內容：settings.json 欄位說明
   - 修改：更新 `date_keyword`、`area_keyword`、`keyword_exclude`、時間控制關鍵字的範例

4. **`specs/001-ticket-automation-system/quickstart.md`**
   - 位置：快速開始指南
   - 內容：所有平台的設定範例
   - 修改：更新所有關鍵字範例

5. **`CHANGELOG.md`**
   - 位置：專案根目錄
   - 內容：版本變更記錄
   - 修改：新增版本記錄，標記 `BREAKING CHANGE`

#### 可選更新的文件（參考用）
6. **`specs/002-keyword-delimiter-fix/spec.md`**
   - 狀態：範例已使用分號（無需修改）

7. **`CLAUDE.md`**
   - 狀態：無關鍵字範例（無需修改）

**決策**：批量更新以上 5 個必須更新的文件

**理由**：
1. 避免新使用者參考過時範例導致錯誤
2. 確保所有文件與程式碼同步（憲法第 VIII 條）
3. CHANGELOG 記錄符合憲法第 IX 條 Git 提交規範

---

### 5. 測試策略研究

**研究任務**：制定測試計畫以驗證修改正確性

**測試層級**：

#### 單元測試（建議但非必須）
**目標函數**：`util.py:is_text_match_keyword()`

**測試案例**：
1. **分號分隔的多關鍵字**
   - 輸入：`keyword_string="10/03;10/05"`, `text="2025/10/03"`
   - 預期：匹配成功（`True`）

2. **包含逗號的單一關鍵字**
   - 輸入：`keyword_string="3,280"`, `text="NT$ 3,280"`
   - 預期：匹配成功（`True`）

3. **JSON 陣列格式**
   - 輸入：`keyword_string=["3,280", "2,680"]`, `text="NT$ 3,280"`
   - 預期：匹配成功（`True`）

4. **舊格式偵測**
   - 輸入：`keyword_string="10/03,10/05"`, `verbose=True`
   - 預期：匹配成功 + 輸出警告訊息

#### 整合測試（手動執行，必須）
**測試環境**：Git Bash / Windows CMD

**測試指令**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**驗證步驟**：
```bash
# 1. 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 2. 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 3. 檢查關鍵流程節點
grep "Match Summary\|Selected target\|clicked\|navigat" .temp/test_output.txt
```

**測試案例**：
1. **TicketPlus 價格關鍵字**
   - 設定：`"area_keyword": "3,280;2,680"`
   - 預期：日誌顯示 `Total areas matched: 2`，依序匹配「3,280」和「2,680」

2. **TixCraft 區域關鍵字**
   - 設定：`"area_keyword": "搖滾A區;搖滾B區"`
   - 預期：日誌顯示依序嘗試匹配兩個區域

3. **時間控制關鍵字**
   - 設定：`"idle_keyword": "09:30:00;14:15:30"`
   - 預期：系統在兩個時間點觸發暫停

**決策**：優先執行整合測試（手動），單元測試為可選

**理由**：
1. 整合測試直接驗證核心功能（關鍵字匹配）
2. 單元測試需要額外的 pytest 設定，時間成本高
3. 符合憲法第 VI 條「測試驅動穩定性」的最低要求

---

## 最佳實踐參考

### Python 字串處理最佳實踐
- 使用 `str.split()` 而非正則表達式（效能考量）
- 使用 `strip()` 移除前後空白
- 使用 list comprehension 提高可讀性：
  ```python
  keywords = [kw.strip() for kw in keyword_string.split(';') if kw.strip()]
  ```

### 相容性處理最佳實踐
- **偵測但不阻斷**：給予使用者選擇權
- **提供清晰的遷移指引**：範例格式、對比說明
- **記錄在 CHANGELOG 中**：標記 `BREAKING CHANGE`（憲法第 IX 條）

### Git 提交規範（憲法第 IX 條）
**Commit Message 格式**：
```
feat(keywords)!: change delimiter from comma to semicolon

Replace comma (,) with semicolon (;) as keyword delimiter to avoid
conflicts with currency format (e.g., "3,280") and time format
(e.g., "09:30:00,14:15:30").

BREAKING CHANGE: Keyword delimiter changed from comma to semicolon.
Users must update their settings.json accordingly.

Closes #23
```

---

## 研究結論

### 技術可行性
✅ **高度可行**：全域替換分隔符號實作成本低，風險可控。

### 實作複雜度
✅ **低**：僅需修改 6 個核心位置，無需重構資料結構。

### 測試充分性
✅ **充分**：整合測試可覆蓋核心流程，單元測試為加分項。

### 文件完整性
✅ **完整**：已識別所有需要更新的文件，確保同步。

### 憲法合規性
✅ **完全合規**：通過所有 9 條憲法原則檢查（見 `plan.md` 憲法檢查區塊）。

---

**準備狀態**：✅ 研究完成，所有 NEEDS CLARIFICATION 已解決，可進入 Phase 1 設計階段。
