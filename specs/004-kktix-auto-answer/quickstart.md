# 快速開始：KKTIX 自動答題功能

**日期**：2025-11-03
**分支**：`004-kktix-auto-answer`
**目的**：提供快速上手指南，讓開發者/使用者能快速啟用並測試本功能

---

## 前置需求

- ✅ Python 3.10+ 已安裝
- ✅ 專案已 clone 至本地
- ✅ NoDriver 已安裝（`requirement.txt` 包含）
- ✅ `src/settings.json` 配置檔案存在

---

## 5 分鐘快速啟用

### 步驟 1：配置 `settings.json`

開啟 `src/settings.json`，找到 `advanced` 區塊並設定：

```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "",
    "verbose": true
  }
}
```

**配置說明**：
- `auto_guess_options: true` - 啟用自動推測答案
- `user_guess_string: ""` - 不預定義答案（讓系統自動推測）
- `verbose: true` - 輸出 Debug 資訊（方便測試時檢查）

---

### 步驟 2：測試執行（30 秒快速測試）

**Windows CMD**：
```cmd
cd "D:\Desktop\bouob-TicketHunter(MaxBot)\tickets_hunter"
del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul
echo. > .temp\test_output.txt
timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

**Git Bash / Linux / macOS**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
echo "" > .temp/test_output.txt
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

---

### 步驟 3：檢查測試輸出

執行後檢查 `.temp/test_output.txt` 檔案：

```bash
# Windows CMD
type .temp\test_output.txt | findstr /C:"inferred_answer_string" /C:"answer_list"

# Git Bash / Linux / macOS
grep -E "inferred_answer_string|answer_list" .temp/test_output.txt
```

**預期輸出**：
```
inferred_answer_string: 20250620
question_text: 請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)。
answer_list: ['20250620', '2025-06-20', '2025/06/20']
fail_list: []
```

**成功標準**：
- ✅ `question_text` 不為空（成功偵測問題）
- ✅ `answer_list` 不為空（成功推測答案）
- ✅ `inferred_answer_string` 不為空（成功選擇答案）

---

## 常見使用場景

### 場景 1：完全自動模式（推薦）

**配置**：
```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "",
    "verbose": false
  }
}
```

**適用情境**：
- 一般搶票使用
- 信任自動推測邏輯
- 不想手動輸入答案

**優點**：
- 無需預先知道答案
- 自動處理常見問題類型（日期、數字、引號內文字等）

**缺點**：
- 可能答錯複雜或需外部知識的問題（如「樂團名稱」）

---

### 場景 2：預定義答案模式（最安全）

**配置**：
```json
{
  "advanced": {
    "auto_guess_options": false,
    "user_guess_string": "SUNSET,落日飛車,Sunset Rollercoaster",
    "verbose": false
  }
}
```

**適用情境**：
- 已事先知道驗證問題答案
- 需要最高成功率
- 避免自動推測錯誤

**優點**：
- 答案準確率 100%（若預定義正確）
- 無自動推測風險

**缺點**：
- 需事先知道答案
- 若答案錯誤則無法自動重試

---

### 場景 3：混合模式（平衡）

**配置**：
```json
{
  "advanced": {
    "auto_guess_options": true,
    "user_guess_string": "20250620,2025-06-20",
    "verbose": false
  }
}
```

**適用情境**：
- 知道部分可能答案
- 希望自動推測作為後備方案
- 追求最高成功率

**優點**：
- 優先使用預定義答案（高準確率）
- 預定義答案失敗時自動推測（高覆蓋率）

**缺點**：
- 配置較複雜

---

## Debug 模式

### 啟用 Debug 輸出

**配置**：
```json
{
  "advanced": {
    "verbose": true
  }
}
```

### Debug 輸出解讀

**輸出範例**：
```
=== KKTIX Page Debug State ===
URL: https://kktix.com/events/7eh6ki/registrations/new
Captcha Question: True
Question Text: 請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)。
==============================
inferred_answer_string: 20250620
question_text: 請輸入加場演出日期。(請以西元年月日,半形阿拉伯數字回答,例如20250620)。
answer_list: ['20250620', '2025-06-20', '2025/06/20']
fail_list: []
```

**關鍵指標**：
1. **Captcha Question: True** - 成功偵測到驗證問題
2. **Question Text** - 問題文本內容
3. **answer_list** - 推測的候選答案清單
4. **inferred_answer_string** - 實際填寫的答案
5. **fail_list** - 已失敗的答案（重試時會跳過）

---

## 故障排除

### 問題 1：`answer_list` 為空

**現象**：
```
answer_list: []
```

**可能原因**：
1. `auto_guess_options` 未啟用
2. 問題文本過於複雜，無法推測
3. `user_guess_string` 為空且未啟用自動推測

**解決方法**：
```json
{
  "advanced": {
    "auto_guess_options": true  // 確保啟用
  }
}
```

---

### 問題 2：答案推測不正確

**現象**：
```
inferred_answer_string: 錯誤答案
```

**可能原因**：
- 問題類型不在推測邏輯覆蓋範圍內
- 問題需要外部知識（如樂團名稱）

**解決方法**：
```json
{
  "advanced": {
    "user_guess_string": "正確答案"  // 手動提供答案
  }
}
```

---

### 問題 3：答案重複嘗試失敗

**現象**：
```
fail_list: ['答案A', '答案B', '答案C']
answer_list: []
```

**可能原因**：
- 所有候選答案均已嘗試且失敗
- 系統已停止自動填寫

**解決方法**：
1. 檢查 `question.txt` 確認問題文本
2. 手動添加新的候選答案至 `user_guess_string`
3. 重新測試

---

## 測試檢查清單

### 功能測試

- [ ] 成功偵測驗證問題（`question_text` 不為空）
- [ ] 成功推測答案（`answer_list` 不為空）
- [ ] 成功填寫答案至輸入框
- [ ] 答案錯誤時記錄至 `fail_list`
- [ ] 重試時跳過 `fail_list` 中的答案

### 配置測試

- [ ] `auto_guess_options: true` 可正常推測答案
- [ ] `auto_guess_options: false` 不推測答案
- [ ] `user_guess_string` 優先於自動推測
- [ ] `verbose: true` 正常輸出 Debug 資訊

### 邊界測試

- [ ] 空 `user_guess_string` 可正常運作
- [ ] 問題文本包含特殊字元可正常處理
- [ ] 輸入框禁用時跳過填寫
- [ ] 無答案時保留輸入框空白

---

## 下一步

### 開發者

1. **執行完整測試**：參考 `docs/07-testing-debugging/testing_execution_guide.md`
2. **查看實作細節**：閱讀 `specs/004-kktix-auto-answer/plan.md`
3. **檢查 API 契約**：閱讀 `specs/004-kktix-auto-answer/contracts/function-signatures.md`

### 使用者

1. **啟用功能**：依據上方步驟 1-3 配置並測試
2. **調整配置**：根據實際需求選擇使用場景（自動/預定義/混合）
3. **回報問題**：若遇到問題，啟用 `verbose` 並提供 `.temp/test_output.txt` 與 `src/question.txt` 內容

---

## 相關文件

- **功能規格**：`specs/004-kktix-auto-answer/spec.md`
- **實作計畫**：`specs/004-kktix-auto-answer/plan.md`
- **資料模型**：`specs/004-kktix-auto-answer/data-model.md`
- **API 契約**：`specs/004-kktix-auto-answer/contracts/`
- **測試指南**：`docs/07-testing-debugging/testing_execution_guide.md`
- **專案憲章**：`.specify/memory/constitution.md`

---

**版本**：1.0
**最後更新**：2025-11-03
**維護者**：Tickets Hunter 專案團隊
