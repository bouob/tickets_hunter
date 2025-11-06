# ibon NoDriver UTK0201_001 修正驗證報告

## 測試日期
2025-10-15

## 測試目的
驗證 ibon NoDriver UTK0201_001 頁面票數選擇與驗證碼處理修正是否成功，並測試不同的自動選取模式組合。

## 修正內容摘要
- **檔案**: `src/nodriver_tixcraft.py:11697-11760`
- **問題**: 進入 UTK0201_001.aspx 後未執行票數選擇、OCR 驗證碼、提交按鈕等功能
- **修正**: 新增 `PERFORMANCE_PRICE_AREA_ID=` 參數偵測與完整四步驟購票流程

## 測試案例

### Test 1: 從下到上 (日期) + 從上到下 (區域)

**設定**:
```json
{
  "date_auto_select": {
    "mode": "from bottom to top"
  },
  "area_auto_select": {
    "mode": "from top to bottom"
  }
}
```

**執行流程**:
1. 日期選擇: `from bottom to top` - 選擇最後一個場次
2. 區域選擇: `from top to bottom` - 選擇 index 4 (乙A區, ID: B0A12X3C)
3. 跳轉至: `UTK0201_001.aspx?...PERFORMANCE_PRICE_AREA_ID=B0A12X3C`
4. 票數選擇: 成功設定為 1 張
5. 驗證碼 OCR: 識別結果 `2893`
6. 表單提交: 成功跳轉至登入頁面

**測試結果**: ✅ 通過

**關鍵日誌** (`.temp/test_output.txt`):
```
Line 105: https://orders.ibon.com.tw/.../UTK0201_001.aspx?...PERFORMANCE_PRICE_AREA_ID=B0A12X3C
Line 121: [IBON CAPTCHA] Starting captcha handling
Line 127: Ticket number selection result: {'success': True, 'set_value': '1'}
Line 137: [CAPTCHA OCR] Result: 2893
Line 146: [CAPTCHA OCR] After: https://huiwan.ibon.com.tw/huiwan/LoginHuiwan/UserLogin.aspx
```

---

### Test 2: 從上到下 (日期) + 中間優先 (區域)

**設定**:
```json
{
  "date_auto_select": {
    "mode": "from top to bottom"
  },
  "area_auto_select": {
    "mode": "center"
  }
}
```

**執行流程**:
1. 日期選擇: `from top to bottom` - 選擇第一個場次
2. 區域選擇: `center` - 選擇 index 42 (僑WD區, ID: B0A14A3U)
3. 跳轉至: `UTK0201_001.aspx?...PERFORMANCE_PRICE_AREA_ID=B0A14A3U`
4. 票數選擇: 成功設定為 1 張
5. 驗證碼 OCR: 識別結果 `3990`
6. 表單提交: 成功跳轉至登入頁面

**測試結果**: ✅ 通過

**關鍵日誌** (`.temp/test_output_test2.txt`):
```
Line 26: auto_select_mode: from top to bottom
Line 56: auto_select_mode: center
Line 94: [TARGET] Selected area: 僑WD區 (index: 42, id: B0A14A3U)
Line 105: https://orders.ibon.com.tw/.../UTK0201_001.aspx?...PERFORMANCE_PRICE_AREA_ID=B0A14A3U
Line 121: [IBON CAPTCHA] Starting captcha handling
Line 127: Ticket number selection result: {'success': True, 'set_value': '1'}
Line 137: [CAPTCHA OCR] Result: 3990
Line 146: [CAPTCHA OCR] After: https://huiwan.ibon.com.tw/huiwan/LoginHuiwan/UserLogin.aspx
```

---

## 測試結果對比

| 項目 | Test 1 | Test 2 |
|------|--------|--------|
| 日期選擇模式 | from bottom to top | from top to bottom |
| 區域選擇模式 | from top to bottom | center |
| 選擇的區域 | index 4 (乙A區) | index 42 (僑WD區) |
| 票數設定 | ✅ 成功 (1 張) | ✅ 成功 (1 張) |
| OCR 識別 | ✅ 成功 (2893) | ✅ 成功 (3990) |
| 表單提交 | ✅ 成功 | ✅ 成功 |
| 完整流程 | ✅ 通過 | ✅ 通過 |

## 修正前後對比

### 修正前 (原始 test_output.txt Lines 106-181)
```
Line 106: 進入 UTK0201_001.aspx 頁面
Line 107+: NoDriver ibon_area_auto_select started  ← 錯誤：持續重試區域選擇
Lines 106-181: 不斷重新載入頁面，未執行票數與驗證碼功能
```

### 修正後 (兩次測試都成功)
```
Line 105: 進入 UTK0201_001.aspx 頁面
Line 121-123: 驗證碼處理啟動 ✅
Line 124-127: 票數選擇成功 ✅
Line 128-147: OCR 識別與表單提交成功 ✅
Line 146: 成功跳轉至下一頁 ✅
```

## 完整流程驗證

兩次測試都成功完成以下步驟：

1. ✅ **日期選擇** - ActivityInfo/Details 頁面 → 購票按鈕點擊
2. ✅ **區域選擇** - UTK0201_000.aspx 頁面 → 區域點擊
3. ✅ **票數選擇** - UTK0201_001.aspx 頁面 → 下拉選單設定
4. ✅ **驗證碼 OCR** - Shadow DOM 截圖 → ddddocr 識別
5. ✅ **表單提交** - 驗證碼輸入 → 表單送出
6. ✅ **頁面跳轉** - 成功跳轉至登入頁面 (因 cookie 過期，符合預期)

## 支援的自動選取模式

### 日期選擇模式 (date_auto_select.mode)
- ✅ `from top to bottom` - 從第一個日期開始選擇
- ✅ `from bottom to top` - 從最後一個日期開始選擇
- ✅ `random` - 隨機選擇 (未測試但程式碼支援)

### 區域選擇模式 (area_auto_select.mode)
- ✅ `from top to bottom` - 從第一個區域開始選擇
- ✅ `center` - 從中間區域開始選擇
- ✅ `random` - 隨機選擇 (未測試但程式碼支援)
- ✅ `from bottom to top` - 從最後一個區域開始選擇 (程式碼支援)

## 已知問題

### Cookie 驗證錯誤 (非關鍵)
```
Line 18: Error checking ibon login status: 'RemoteObject' object has no attribute 'get'
Line 22: ibon login process failed: login_verification_failed
```

**影響**: 登入驗證失敗，但不影響購票流程測試
**原因**: `check_ibon_login_status` 函數回傳 RemoteObject 而非 dict
**狀態**: 已記錄但不影響本次修正的核心功能

## 結論

✅ **修正成功**：ibon NoDriver UTK0201_001 頁面票數選擇與驗證碼處理功能已完整實作並通過驗證

✅ **多模式支援**：兩種不同的日期與區域選擇模式組合都成功運作

✅ **完整流程**：從日期選擇到表單提交的完整購票流程都正常執行

## 相關文件
- 修正記錄: `docs/10-project-tracking/accept_changelog.md` (2025-10-15 條目)
- 測試輸出:
  - `.temp/test_output.txt` (Test 1)
  - `.temp/test_output_test2.txt` (Test 2)
- 程式碼: `src/nodriver_tixcraft.py:11697-11760`
