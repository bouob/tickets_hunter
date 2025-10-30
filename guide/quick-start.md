# 快速入門指南

本指南將帶您在 **5 分鐘內**完成第一次搶票設定。

---

## 🎯 目標

完成本指南後，您將能夠：
- ✅ 開啟設定介面
- ✅ 完成基本設定
- ✅ 啟動搶票程式
- ✅ 理解搶票流程

---

## 📋 前置準備

### 1. 確認已安裝
- Python 3.9-3.11（建議使用 3.10）
- Chrome 瀏覽器
- Tickets Hunter 程式 (已下載或 git clone)

### 2. 下載程式

**原始碼版本（推薦，跨平台）**
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
```

### 3. 安裝相依套件
```bash
pip install -r requirement.txt
```

### 4. 路徑說明（重要！）

執行指令前請先確認工作目錄：
- **根目錄** (`tickets_hunter/`)：執行 pip install、git pull 等全域指令
- **原始碼目錄** (`tickets_hunter/src/`)：執行 Python 腳本（settings.py、config_launcher.py 等）

**範例**：
```bash
# 在根目錄執行（安裝相依套件、更新程式）
cd tickets_hunter
pip install -r requirement.txt

# 切換到原始碼目錄執行（啟動程式）
cd tickets_hunter/src
python settings.py
```

---

## 🚀 第一次使用流程

### 步驟 1：開啟設定介面

**方法一：網頁介面（推薦）**
```bash
cd tickets_hunter/src
python settings.py
```
瀏覽器會自動開啟網頁介面：`http://127.0.0.1:16888/`

**方法二：桌面介面**
```bash
cd tickets_hunter/src
python settings_old.py
```
會開啟傳統的視窗介面。

**方法三：多設定檔管理（進階）**
```bash
cd tickets_hunter/src
python config_launcher.py
```
適合需要管理多個活動設定檔的使用者。

---

### 步驟 2：設定基本參數

在設定介面中，您需要填寫以下**必填欄位**：

#### 2.1 目標網址 (homepage)
填寫您要搶票的活動網址。

**範例**：
```
https://tixcraft.com/activity/detail/24_SHOW
https://kktix.com/events/example-event
```

**提示**：直接複製活動頁面網址即可。

---

#### 2.2 購票張數 (ticket_number)
填寫您要買幾張票。

**範例**：
```
2
```

**注意**：請依照活動規定填寫，通常單筆訂單限制 1-4 張。

---

#### 2.3 搶票引擎 (webdriver_type)
選擇使用哪種搶票引擎。

**在圖形介面中顯示為**：`WebDriver類別`

**推薦設定**：nodriver

**可選值**：
- nodriver - **推薦**，反偵測能力最強
- undetected_chromedriver - 舊版回退
- selenium - 標準模式（較容易被偵測）

---

#### 2.4 日期關鍵字 (date_keyword)
填寫您想選擇的**演出日期的部分文字**。

**在圖形介面中顯示為**：`日期關鍵字`

**範例**：11/16;11/17

**說明**：
- 多組關鍵字用分號分隔（OR 邏輯）
- 關鍵字內部用空格表示 AND 邏輯
- 程式會依序嘗試每組關鍵字
- 如果都找不到，會自動回退到日期排序方式
- 逗號僅作為千位分隔符號（例如票價 "3,280" 中的逗號）

**更多範例**：
- 週六 - 選擇包含「週六」的日期
- 11/16 19:30 - 選擇同時包含「11/16」和「19:30」的場次
- 11/16;11/17;11/18 - 依序嘗試三個日期
- 留空 - 不指定，直接用日期排序方式自動選

---

#### 2.5 區域關鍵字 (area_keyword)
填寫您想選擇的**座位區域的部分文字**。

**在圖形介面中顯示為**：`區域關鍵字`

**範例**：搖滾A;搖滾B;VIP

**說明**：
- 多組關鍵字用分號分隔（OR 邏輯）
- 關鍵字內部用空格表示 AND 邏輯
- 程式會依序嘗試每組關鍵字
- 如果都找不到，會自動回退到區域排序方式
- 逗號僅作為千位分隔符號（例如票價 "3,280" 中的逗號）

**更多範例**：
- 3,280 - 選擇票價 3,280 的區域
- 搖滾A 前排 - 選擇同時包含「搖滾A」和「前排」的區域
- 3,280;2,680;1,680 - 依序嘗試三個價格
- 留空 - 不指定，直接用區域排序方式自動選

---

#### 2.6 自動選擇模式 (mode)
當關鍵字都找不到時，程式會根據這個設定自動選擇。

**在圖形介面中顯示為**：
- 日期：`日期排序方式`
- 區域：`區域排序方式`

**可選值**：
- from top to bottom - 選**第一個**可用選項（通常是最早日期或最貴區域）
- from bottom to top - 選**最後一個**可用選項
- center - 選**中間**的選項
- random - **隨機**選擇

**推薦設定**：
- 日期：from top to bottom (選最早場次)
- 區域：from top to bottom (選最貴區域，通常位置最好)

---

#### 2.7 排除關鍵字 (keyword_exclude)
設定**不要選擇**包含這些文字的區域。

**推薦設定**：輪椅;身障;身心;障礙;Restricted View;燈柱遮蔽;視線不完整

**說明**：
- 程式會自動跳過包含這些關鍵字的區域
- 避免誤選輪椅席或視線不良區域
- 關鍵字用分號分隔

---

### 步驟 3：檢查進階設定（選填）

#### 3.1 驗證碼自動辨識
在圖形介面中檢查「猜測驗證碼」設定：
- 啟用：打勾
- ddddocr beta：打勾
- 掛機模式：打勾

**預設已啟用**，無需修改。

#### 3.2 詳細輸出模式（除錯時使用）
在圖形介面的「進階設定」頁籤中：
- 輸出詳細除錯訊息：打勾

**說明**：
- 方便查看搶票過程和除錯
- **警告**：輸出大量日誌可能影響效能
- **建議**：除非需要除錯，否則保持關閉

---

### 步驟 4：儲存設定

#### 網頁介面
點擊介面上的「儲存」或「Save」按鈕。

#### 桌面介面
點擊「儲存設定」按鈕。

設定會自動儲存到 `src/settings.json` 檔案。

---

### 步驟 5：啟動搶票

#### 網頁介面
點擊「搶票」或「Start」按鈕。

#### 桌面介面
點擊「搶票」按鈕。

#### 手動執行（進階）
```bash
cd tickets_hunter/src
python nodriver_tixcraft.py --input settings.json
```

---

## 🎬 搶票流程說明

啟動後，程式會**自動執行**以下步驟：

```
1. 開啟 Chrome 瀏覽器
   ↓
2. 前往目標網址 (homepage)
   ↓
3. 選擇日期
   - 先嘗試關鍵字匹配 (date_keyword)
   - 找不到則用 mode 自動選
   ↓
4. 選擇區域
   - 先嘗試關鍵字匹配 (area_keyword)
   - 排除不要的區域 (keyword_exclude)
   - 找不到則用 mode 自動選
   ↓
5. 設定票數 (ticket_number)
   ↓
6. 辨識驗證碼（如果有）
   - 自動 OCR 辨識
   - 自動填入
   ↓
7. 勾選同意條款
   ↓
8. 送出訂單
   ↓
9. 完成！🎉
```

---

## 🔍 監控搶票過程

### 查看程式輸出
如果在「進階設定」中啟用「輸出詳細除錯訊息」，會看到詳細的執行過程：

**警告**：輸出大量日誌可能影響效能，除非需要除錯，否則建議保持關閉。

**範例 1：成功匹配關鍵字**
```
[DATE KEYWORD] Keywords (AND logic): ['11/16', '19:30']
[DATE KEYWORD] Match found! Total dates matched: 1
[DATE SELECT] Selected: 2024/11/16 (六) 19:30

[AREA KEYWORD] Keywords (AND logic): ['搖滾A', '前排']
[AREA KEYWORD] Match Summary:
  Total areas checked: 5
  Areas matched: 1
  Match rate: 20.0%
[AREA SELECT] Selected: 搖滾A區 前排 TWD$2,280
```

**範例 2：關鍵字失敗，回退到自動選擇**
```
[DATE KEYWORD] Keywords (AND logic): ['11/99']
[DATE KEYWORD] No matches found
[DATE SELECT] Fallback to mode: from top to bottom
[DATE SELECT] Auto-selected: 2024/11/16 (六) 19:30
```

**範例 3：KKTIX 等待票券開賣**
```
[KKTIX AREA] Match Summary:
  Tickets matched (with input): 0
  Tickets matched (waiting for open): 1

  Waiting for these tickets to open:
    - 全票(2F) TWD$3,800 (keywords: 2F, 3,800)
```

### 瀏覽器視窗
程式會自動開啟 Chrome 瀏覽器，您可以直接看到操作過程。

---

## ❓ 常見問題排除

### Q1: 程式啟動後瀏覽器沒有開啟
**可能原因**：
- Chrome 瀏覽器未安裝
- Python 版本不相容（需 3.9-3.11，建議 3.10）
- 相依套件未安裝

**解決方法**：
```bash
# 重新安裝相依套件
pip install -r requirement.txt

# 檢查 Python 版本
python --version
```

---

### Q2: 程式報錯 "找不到日期"
**可能原因**：
- 關鍵字設定錯誤
- 活動尚未開賣

**解決方法**：
1. 檢查 `date_keyword` 是否正確
2. 手動打開活動頁面，複製日期文字
3. 或設定 `"date_keyword": ""` 使用 mode 自動選

---

### Q3: 程式選錯區域
**可能原因**：
- `area_keyword` 設定不夠精確
- 沒有設定 `keyword_exclude`

**解決方法**：
1. 使用更精確的關鍵字，例如 `"搖滾A區"` 而不是 `"搖滾"`
2. 設定 `keyword_exclude` 排除不要的區域
3. 調整 `mode` 設定

---

### Q4: 驗證碼辨識失敗
**說明**：
- OCR 辨識率約 80-90%
- 辨識失敗很正常

**解決方法**：
1. 設定 `"force_submit": false`，辨識後等待手動確認
2. 或設定 `"ocr_captcha.enable": false`，完全手動輸入

---

### Q5: 程式執行到一半停住
**可能原因**：
- 網站載入速度慢
- 暫停機制觸發（NoDriver）

**解決方法**：
1. 等待一段時間，程式會自動重試
2. 檢查是否有 `MAXBOT_INT28_IDLE.txt` 檔案（暫停標記）
3. 刪除暫停標記檔案：
   ```bash
   cd tickets_hunter
   rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt
   ```

---

## 🔄 程式更新

### 取得最新版本
```bash
cd tickets_hunter
git pull
```

### 或重新下載
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
pip install -r requirement.txt
```

**建議**：定期更新以獲得最新功能和錯誤修復。

---

## 📚 下一步

恭喜您完成第一次設定！接下來您可以：

1. **深入了解關鍵字機制** - [關鍵字與回退機制](keyword-mechanism.md)
2. **探索進階設定** - [詳細設定說明](settings-guide.md)
3. **回到總覽** - [使用者手冊首頁](README.md)

---

## 💡 實戰技巧

### 技巧 1：多組關鍵字提高成功率
在圖形介面的「日期關鍵字」欄位設定：週六 19:30;週六 14:00;週日

程式會依序嘗試，增加搶到票的機會。

### 技巧 2：排除關鍵字避免誤選
在圖形介面的「排除關鍵字」欄位設定：輪椅;身障;視線不良

確保不會選到不想要的區域。

### 技巧 3：除錯時使用詳細輸出模式
在圖形介面的「進階設定」頁籤中，啟用「輸出詳細除錯訊息」。

**用途**：方便了解程式執行過程，出問題時可快速定位。

**警告**：輸出大量日誌可能影響效能，僅在需要除錯時使用。

### 技巧 4：提前測試設定
在正式開搶前，用其他活動測試您的設定是否正確。

---

**祝您搶票成功！** 🎉

*最後更新：2025-10-29 | 版本：1.1*
