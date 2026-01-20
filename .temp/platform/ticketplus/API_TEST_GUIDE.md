# TicketPlus API 檢查測試指南

測試 TicketPlus API pending 狀態檢查是否真的有用

---

## 📋 測試目的

驗證以下邏輯是否正確運作：
1. 程式能否正確找到 TicketPlus API URL
2. 程式能否正確取得 API 資料
3. 程式能否正確判斷 `pending` 狀態
4. 這個機制是否真的能偵測到「即將開賣」的狀態

---

## 🧪 測試方式 1：瀏覽器 Console（推薦，最簡單）

### 步驟

1. **開啟 TicketPlus 並登入**
   - 訪問 https://ticketplus.com.tw
   - 登入您的帳號

2. **導航到訂票頁面**
   - 選擇任一活動
   - 點擊「立即購票」進入日期選擇頁面
   - 選擇日期後進入訂票頁面（URL 應該是 `/order/XXX/YYY`）

3. **打開開發者工具**
   - 按 `F12` 或右鍵 → 檢查
   - 切換到 `Console` 標籤

4. **執行測試腳本**
   - 打開檔案：`.temp/ticketplus/test_api_check_console.js`
   - 複製整個檔案的內容
   - 貼到 Console 中
   - 按 `Enter` 執行

5. **查看結果**
   - Console 會顯示詳細的測試結果
   - 重點看以下訊息：
     ```
     🟡 結果: API 狀態為 PENDING
        → 程式會自動重載頁面
     ```
     或
     ```
     🟢 結果: API 狀態為 "on-sale" (非 pending)
        → 程式不會因 API 狀態而重載
     ```

### 優點
- ✅ 最簡單，不需要額外安裝
- ✅ 立即看到結果
- ✅ 可以重複執行測試
- ✅ 顯示完整的 API 資料

---

## 🧪 測試方式 2：Python 自動化測試

### 步驟

1. **執行測試腳本**
   ```bash
   cd "D:\Desktop\bouob-TicketHunter(MaxBot)\tickets_hunter\.temp\ticketplus"
   python test_api_check.py
   ```

2. **按照提示操作**
   - 程式會自動開啟瀏覽器
   - 手動登入並導航到訂票頁面
   - 按 Enter 繼續測試

3. **查看測試結果**
   - Terminal 會顯示詳細的檢查結果
   - 包含 API URL、產品狀態、完整資料等

### 優點
- ✅ 完整的自動化測試
- ✅ 可以整合到測試流程
- ✅ 記錄詳細的測試數據

---

## 🔍 預期結果

### 情況 1：活動尚未開賣（即將開賣）

```
✓ API 檢查完成

  isPending: True
  原因: API status pending
  API URL: https://apis.ticketplus.com.tw/config/api/get?productId=XXX
  產品狀態: pending
```

**解讀**：
- ✅ API 檢查機制**有效**
- ✅ 程式會自動重載頁面，等待開賣
- ✅ 這是期望的行為

---

### 情況 2：活動已開賣

```
✓ API 檢查完成

  isPending: False
  原因: API status is "on-sale" (not pending)
  API URL: https://apis.ticketplus.com.tw/config/api/get?productId=XXX
  產品狀態: on-sale
```

**解讀**：
- ✅ API 檢查機制**有效**
- ✅ 程式不會因 API 狀態而重載
- ✅ 會繼續執行選票流程

---

### 情況 3：找不到 API URL

```
✓ API 檢查完成

  isPending: False
  原因: No API URL found
  總網路請求數: 45
```

**解讀**：
- ⚠️ 可能的問題：
  1. 頁面尚未完全載入
  2. TicketPlus API 格式已變更
  3. 不在正確的訂票頁面
- 🔧 建議：重新整理頁面後再試

---

## 📊 測試重點

### 應該測試的情境

1. **正常開賣的活動**
   - 預期：`isPending: False`，狀態為 `on-sale`
   - 結論：API 檢查不會觸發重載

2. **即將開賣的活動**（最重要）
   - 預期：`isPending: True`，狀態為 `pending`
   - 結論：API 檢查會觸發重載
   - ⚠️ 這個情境比較難測試（需要在開賣前進入頁面）

3. **已售完的活動**
   - 預期：`isPending: False`，狀態可能是 `sold-out`
   - 結論：API 檢查不會觸發重載

---

## 🐛 常見問題

### Q1: Console 顯示「未找到目標 API URL」

**原因**：
- 頁面尚未載入完成
- 不在訂票頁面（/order/...）
- TicketPlus API URL 格式已變更

**解決方案**：
1. 確認在訂票頁面（URL 包含 `/order/`）
2. 等待頁面完全載入（3-5 秒）
3. 重新執行測試腳本

---

### Q2: API 狀態總是顯示「非 pending」

**原因**：
- 測試的活動已經開賣
- 需要測試「即將開賣」的活動才會看到 `pending`

**解決方案**：
1. 找一個尚未開賣的活動
2. 在開賣前 1-2 分鐘進入訂票頁面
3. 執行測試腳本

---

### Q3: Python 測試無法執行

**原因**：
- 缺少 `nodriver` 套件

**解決方案**：
```bash
pip install nodriver
```

---

## ✅ 測試結論判定

### ✓ API 檢查機制有效的證據

- [x] 能夠找到 TicketPlus API URL
- [x] 能夠取得 API 回應資料
- [x] 能夠正確解析產品狀態（pending / on-sale / sold-out）
- [x] 邏輯正確：pending → 重載，非 pending → 繼續

### ✗ API 檢查機制可能失效的情況

- [ ] 找不到 API URL（API 格式變更）
- [ ] 無法取得 API 資料（網路錯誤、權限問題）
- [ ] 產品狀態解析錯誤
- [ ] 即使狀態是 pending 也沒有觸發重載

---

## 📝 測試報告範例

測試完成後，您可以記錄以下資訊：

```
測試日期：2025-11-08
測試活動：2025 Roving Nation Festival 漂遊者森林音樂祭
活動狀態：已開賣

測試結果：
✓ API URL 找到：https://apis.ticketplus.com.tw/config/api/get?productId=XXX
✓ API 狀態：on-sale
✓ isPending：False
✓ 邏輯正確：不會觸發重載

結論：API 檢查機制運作正常 ✅
```

---

## 🔧 進階測試

如果您想更深入測試，可以：

1. **修改 JavaScript 查看不同的 API 資料**
   ```javascript
   // 在 Console 執行
   const entries = performance.getEntries();
   const ticketPlusApis = entries.filter(e => e.name.includes('apis.ticketplus.com.tw'));
   console.table(ticketPlusApis.map(e => ({ url: e.name, type: e.initiatorType })));
   ```

2. **手動測試 API 端點**
   ```javascript
   // 取得 API URL 後
   fetch('API_URL_HERE')
     .then(r => r.json())
     .then(data => console.log(data));
   ```

3. **監控 API 狀態變化**
   ```javascript
   // 每 5 秒檢查一次
   setInterval(async () => {
     // 執行 test_api_check_console.js 的內容
   }, 5000);
   ```

---

**祝測試順利！** 如有任何問題，請查看 Console 的詳細錯誤訊息。
