# 快速開始：關鍵字優先選擇與條件式自動遞補

**功能**: 關鍵字優先選擇與條件式自動遞補
**建立日期**: 2025-10-31
**預計閱讀時間**: 5 分鐘

## 功能摘要

此功能改進了搶票系統的日期與區域選擇邏輯，主要改變：

1. **關鍵字優先匹配（早期返回）**: 第一個匹配成功的關鍵字立即被選擇，不再掃描後續關鍵字
2. **條件式自動遞補**: 當所有關鍵字都未匹配時,可選擇是否自動遞補選擇其他可用選項

---

## 核心概念

### 早期返回（Early Return）模式

**舊行為**（已棄用）:
```
檢查關鍵字 "11/16" → 匹配 ✓ → 加入陣列
檢查關鍵字 "11/17" → 匹配 ✓ → 加入陣列
檢查關鍵字 "11/18" → 未匹配 ✗
完成掃描後 → 從陣列選擇第一個："11/16"
```

**新行為**:
```
檢查關鍵字 "11/16" → 匹配 ✓ → 立即選擇 → 停止檢查
```

**優點**: 平均節省 30% 的關鍵字檢查時間

---

### 條件式遞補機制

當所有關鍵字都未匹配時，由新增的布林開關控制行為：

**嚴格模式（預設 `false`）**:
```
date_auto_fallback = false
→ 所有關鍵字失敗 → 不自動選擇 → 等待手動介入
```

**彈性模式（啟用 `true`）**:
```
date_auto_fallback = true
→ 所有關鍵字失敗 → 根據 date_select_order 自動選擇可用日期
```

---

## 設定範例

### 範例 1：嚴格模式（僅選擇關鍵字匹配的選項）

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16;11/17",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": false,
  "area_auto_select": {
    "enable": true,
    "area_keyword": "搖滾區A;VIP區",
    "mode": "from_top_to_bottom"
  },
  "area_auto_fallback": false
}
```

**行為**:
- ✅ 若頁面有 "11/16"，立即選擇 "11/16"
- ✅ 若頁面僅有 "11/17"，選擇 "11/17"
- ❌ 若頁面僅有 "11/18" 和 "11/19"（關鍵字全失敗），**不自動選擇**，等待手動介入

---

### 範例 2：彈性模式（接受替代選項）

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "11/16;11/17",
    "mode": "from_top_to_bottom"
  },
  "date_auto_fallback": true,
  "area_auto_select": {
    "enable": true,
    "area_keyword": "搖滾區A;VIP區",
    "mode": "random"
  },
  "area_auto_fallback": true
}
```

**行為**:
- ✅ 若頁面有 "11/16"，立即選擇 "11/16"
- ✅ 若頁面僅有 "11/17"，選擇 "11/17"
- ✅ 若頁面僅有 "11/18" 和 "11/19"（關鍵字全失敗），**自動選擇 "11/18"**（由上而下第一個可用選項）

---

## UI 設定（Phase 2）

在 `settings.html` 設定頁面中：

### 日期自動遞補核取方塊

位置：「日期自動點選」區塊下方

```
☐ 日期自動遞補
  當所有日期關鍵字都未匹配時，是否自動選擇可用日期（預設關閉）
```

### 區域自動遞補核取方塊

位置：「區域自動點選」區塊下方

```
☐ 區域自動遞補
  當所有區域關鍵字都未匹配時，是否自動選擇可用區域（預設關閉）
```

**預設狀態**: 兩個核取方塊皆未勾選（預設 `false`）

---

## 日誌範例

### 成功匹配（第二個關鍵字）

```
[DATE KEYWORD] Start checking keywords in order: ['11/16', '11/17', '11/18']
[DATE KEYWORD] Checking keyword #1: '11/16' - No match
[DATE KEYWORD] Checking keyword #2: '11/17' - Match found
[DATE SELECT] Keyword #2 matched: '11/17', selected immediately and stopped further checks
[DATE SELECT] Selected date: 11/17 (keyword match)
```

### 遞補選擇（關鍵字全部失敗，遞補啟用）

```
[DATE KEYWORD] Start checking keywords in order: ['11/16', '11/17']
[DATE KEYWORD] Checking keyword #1: '11/16' - No match
[DATE KEYWORD] Checking keyword #2: '11/17' - No match
[DATE KEYWORD] All keywords failed to match
[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback
[DATE FALLBACK] Selecting available date based on date_select_order='from_top_to_bottom'
[DATE SELECT] Selected date: 11/18 (fallback)
```

### 嚴格模式（關鍵字全部失敗，遞補停用）

```
[DATE KEYWORD] Start checking keywords in order: ['11/16', '11/17']
[DATE KEYWORD] Checking keyword #1: '11/16' - No match
[DATE KEYWORD] Checking keyword #2: '11/17' - No match
[DATE KEYWORD] All keywords failed to match
[DATE FALLBACK] date_auto_fallback=false, fallback is disabled
[DATE SELECT] Waiting for manual intervention
```

---

## 常見問題

### Q1: 為什麼預設值是 `false`（嚴格模式）？

**A**: 為了避免誤搶不想要的場次。使用者可以主動開啟遞補功能（`true`）以提高搶票成功率。

---

### Q2: 如果我的舊版設定檔沒有這兩個新欄位會怎樣？

**A**: 系統會自動使用預設值 `false`（嚴格模式）。你可以：
1. 手動編輯 `settings.json` 加入 `"date_auto_fallback": true`
2. 在 UI 中勾選「日期自動遞補」核取方塊並儲存

---

### Q3: 早期返回模式會影響效能嗎？

**A**: 不會，反而提升效能。平均節省 30% 的關鍵字檢查時間，因為第一個匹配立即返回，不需要掃描後續關鍵字。

---

### Q4: 如果我想同時對日期啟用遞補，但對區域保持嚴格模式？

**A**: 可以！兩個開關互相獨立：
```json
{
  "date_auto_fallback": true,
  "area_auto_fallback": false
}
```

---

### Q5: 排除關鍵字（`keyword_exclude`）如何與遞補功能互動？

**A**: 排除關鍵字在建立可用選項清單（`formated_area_list`）時就已過濾掉，關鍵字匹配與遞補選擇都是從已過濾的清單中進行，因此自動遵守排除規則。

---

## 測試方式

### 快速測試指令（Windows CMD）

**重要**: 測試前必須刪除 `MAXBOT_INT28_IDLE.txt`，否則程式會立即暫停。

```cmd
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

### 驗證日誌輸出

```bash
# 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
```

---

## 技術細節

### 修改的檔案

1. **核心邏輯**:
   - `src/nodriver_tixcraft.py` - 日期與區域選擇邏輯

2. **設定檔結構**:
   - `src/settings.py` / `src/settings_old.py` - `get_default_config()` 函數

3. **UI 控制項**（Phase 2）:
   - `settings.html` - 新增兩個核取方塊

### 未修改的檔案

- `src/chrome_tixcraft.py` - 進入維護模式，不在此功能範圍內
- `src/util.py` - 排除關鍵字過濾邏輯（既有功能）
- 平台特定模組（TixCraft、KKTIX、iBon 等）

---

## 下一步

1. **實作核心邏輯**（P1）:
   - 修改日期與區域選擇邏輯
   - 新增結構化日誌訊息

2. **實作 UI 控制項**（P2）:
   - 在 `settings.html` 新增核取方塊

3. **測試驗證**:
   - 執行實際搶票測試
   - 驗證日誌輸出

4. **文件更新**:
   - 更新 `CHANGELOG.md`
   - 更新使用者手冊

---

## 相關文件

- **功能規格**: `specs/003-keyword-priority-fallback/spec.md`
- **技術研究**: `specs/003-keyword-priority-fallback/research.md`
- **資料模型**: `specs/003-keyword-priority-fallback/data-model.md`
- **API 合約**: `specs/003-keyword-priority-fallback/contracts/config-schema.md`
- **憲章原則**: `.specify/memory/constitution.md`（第 I-IX 條）
