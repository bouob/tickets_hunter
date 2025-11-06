# 研究與技術決策：KKTIX 自動答題功能（NoDriver 版本）

**日期**：2025-11-03
**分支**：`004-kktix-auto-answer`
**目的**：解決技術上下文中的確認事項，並記錄技術決策

---

## 研究結果

### 1. `write_question_to_file()` 函數實作確認

**問題**：需確認 `write_question_to_file()` 函數是否已存在

**研究方法**：
- 使用 `grep -r "def write_question_to_file"` 搜尋專案
- 檢查 `src/nodriver_tixcraft.py` 與 `src/chrome_tixcraft.py`

**發現**：
- ✅ **已存在**：函數位於 `src/nodriver_tixcraft.py:178`
- **實作內容**：
  ```python
  def write_question_to_file(question_text):
      working_dir = os.path.dirname(os.path.realpath(__file__))
      target_path = os.path.join(working_dir, CONST_MAXBOT_QUESTION_FILE)
      util.write_string_to_file(target_path, question_text)
  ```
- **檔案路徑**：寫入 `src/question.txt`（由 `CONST_MAXBOT_QUESTION_FILE` 常數定義）
- **相依性**：依賴 `util.write_string_to_file()` 函數

**決策**：
- ✅ **無需實作新函數**
- ✅ **可直接使用現有 `write_question_to_file()` 函數**
- **呼叫時機**：在偵測到驗證問題後立即呼叫（line 1202 位置）

---

### 2. `util.get_answer_list_from_question_string()` 介面確認

**問題**：需確認函數簽章與 NoDriver 環境相容性

**研究方法**：
- 檢查 `src/util.py` 中的函數定義
- 查看 Chrome Driver 版本的呼叫方式
- 查看 NoDriver 版本現有呼叫（line 1207）

**發現**：
- **函數簽章**：
  ```python
  def get_answer_list_from_question_string(registrationsNewApp_div, captcha_text_div_text)
  ```
- **參數說明**：
  - `registrationsNewApp_div`：原為 Selenium WebElement，但實作中**僅在特定情況使用**（用於取得 web datetime）
  - `captcha_text_div_text`：問題文本字串（必要參數）

- **NoDriver 環境相容性**：
  - ✅ **可傳 `None` 作為第一個參數**
  - ✅ 實作邏輯中大部分規則不依賴 WebElement
  - ✅ NoDriver 版本現有呼叫方式（line 1207）：
    ```python
    answer_list = util.get_answer_list_from_question_string(None, question_text)
    ```

**決策**：
- ✅ **使用 `None` 作為第一個參數**（與現有 NoDriver 實作一致）
- ✅ **複用完整函數邏輯**（包含所有規則式推測）
- **呼叫方式**：
  ```python
  answer_list = util.get_answer_list_from_question_string(None, question_text)
  ```

---

### 3. `auto_guess_options` 配置確認

**問題**：需確認預設值與配置位置

**研究方法**：
- 檢查 `src/settings.json` 預設配置
- 搜尋現有程式碼中的使用方式

**發現**：
- **配置位置**：`settings.json -> advanced.auto_guess_options`
- **預設值**：`false`（禁用）
- **配置內容**：
  ```json
  "advanced": {
      "verbose": true,
      "auto_guess_options": false,
      "user_guess_string": ""
  }
  ```
- **讀取方式**：`config_dict["advanced"]["auto_guess_options"]`

**決策**：
- ✅ **使用現有配置欄位**（無需新增）
- ✅ **預設值維持 `false`**（避免意外行為）
- ⚠️ **使用者需手動啟用**（在 settings.json 中設為 `true`）
- **判斷邏輯**：
  ```python
  if len(answer_list) == 0:
      if config_dict["advanced"]["auto_guess_options"]:
          answer_list = util.get_answer_list_from_question_string(None, question_text)
  ```

---

## 技術決策總結

| 決策項目 | 決策內容 | 理由 |
|---------|---------|------|
| 問題記錄函數 | 使用現有 `write_question_to_file()` | 函數已存在且符合需求，無需重複實作 |
| 答案推測函數參數 | 第一個參數傳 `None` | NoDriver 環境下無 WebElement，傳 `None` 已驗證可用 |
| 配置欄位 | 使用現有 `auto_guess_options` | 避免新增配置，保持一致性 |
| 預設值 | 維持 `false` | 避免意外啟用自動答題（可能答錯影響搶票） |
| 整合點 | 在 line 1206 處啟用邏輯 | 現有程式碼已有條件分支，僅需移除註解或修正邏輯 |

---

## 替代方案評估

### 方案 A：重新實作答案推測邏輯（❌ 拒絕）
- **優點**：可為 NoDriver 最佳化
- **缺點**：
  - 違反憲章第 IV 條（重複實作）
  - 需維護兩份邏輯（增加維護成本）
  - 失去 Chrome Driver 版本的成熟經驗
- **結論**：拒絕，複用現有邏輯最簡單

### 方案 B：新增專屬配置欄位 `nodriver_auto_guess`（❌ 拒絕）
- **優點**：NoDriver 與 Chrome Driver 可獨立配置
- **缺點**：
  - 增加配置複雜度
  - 使用者困惑（兩個相似欄位）
  - 違反簡潔原則
- **結論**：拒絕，使用現有 `auto_guess_options` 欄位

### 方案 C：預設啟用 `auto_guess_options`（❌ 拒絕）
- **優點**：使用者無需手動設定
- **缺點**：
  - 可能答錯影響搶票成功率
  - 改變現有使用者預期（破壞相容性）
  - 違反憲章第 III 條（不得破壞相容性）
- **結論**：拒絕，維持預設 `false`

---

## 實作檢查清單

Phase 0 完成確認：
- [x] `write_question_to_file()` 函數確認
- [x] `get_answer_list_from_question_string()` 介面確認
- [x] `auto_guess_options` 配置確認
- [x] 無 NEEDS CLARIFICATION 項目殘留
- [x] 所有技術決策已記錄

**下一步**：進入 Phase 1（資料模型與 API 契約設計）

---

**版本**：1.0
**審查狀態**：待審查
