<!--
文件說明：協助使用者在 5 分鐘內完成第一次搶票設定
分類：Getting Started (level: 1)
目標受眾：初學者
版本：1.2
最後更新：2025-11-12
-->

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

1. 前往 [GitHub Releases](https://github.com/bouob/tickets_hunter/releases)
2. 下載最新版本的 ZIP 檔案（例如：`tickets_hunter_v2025.11.03.zip`）
3. 解壓縮到任意目錄
4. 開啟終端機，進入解壓縮後的目錄：
   ```bash
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

**網頁介面**
```bash
cd tickets_hunter/src
python settings.py
```
瀏覽器會自動開啟網頁介面：`http://127.0.0.1:16888/`

> 💡 若 Port 被佔用無法開啟，請參考[設定介面 Port 說明](settings-guide.md#設定介面-portserver_port-v202512-新增)

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

#### 2.3 日期關鍵字

填寫想選擇的日期文字，例如：`11/16;11/17;週六`

| 語法 | 說明 | 範例 |
|------|------|------|
| 分號 `;` | OR 邏輯（任一命中） | `11/16;11/17` |
| 空格 | AND 邏輯（同時包含） | `11/16 19:30` |

---

#### 2.4 區域關鍵字

填寫想選擇的區域文字，例如：`搖滾A;VIP;3,280`

| 語法 | 說明 | 範例 |
|------|------|------|
| 分號 `;` | OR 邏輯（任一命中） | `搖滾A;VIP` |
| 空格 | AND 邏輯（同時包含） | `搖滾A 3280` |

---

#### 2.5 排除關鍵字

排除不想選的區域：`輪椅;身障;視線不良`

---

> **📖 完整關鍵字教學** → [關鍵字與回退機制](keyword-mechanism.md)
>
> 包含：AND/OR 邏輯詳解、自動遞補、回退機制、設定範例

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

#### 3.3 優惠代碼設定（特定活動需要）⭐ 新增功能

**在圖形介面中顯示為**：**優惠代碼**（文字框，位於進階設定頁籤）

**使用時機**：
- ✅ 活動頁面要求輸入「會員序號」、「優惠代碼」、「驗證序號」時
- ❌ 一般活動不需要設定（保持空白即可）

**支援平台**：KKTIX、TicketPlus

**範例**：
```
MEMBER2024
DISCOUNT12345
FANCLUB999
```

**說明**：
- 程式會自動偵測活動頁面的序號輸入欄位
- 自動填入您設定的代碼
- 支援多種欄位類型（會員序號、優惠序號、驗證碼等）

**設定位置**：
1. 在圖形介面中找到「進階設定」頁籤
2. 向下滾動到「優惠代碼」欄位
3. 填入您的序號/代碼

**注意**：
- 僅在特定活動需要時才設定
- 代碼格式依主辦方規定
- 如果活動無需代碼，請保持空白

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
   - 先嘗試日期關鍵字匹配
   - 全部匹配失敗 → 檢查「日期自動遞補」設定
     └─ 關閉：暫停等待，持續刷新尋找指定日期
     └─ 開啟：使用「日期排序方式」自動選擇任何可用日期
   ↓
4. 選擇區域
   - 先排除「排除關鍵字」中的區域
   - 再嘗試區域關鍵字匹配
   - 全部匹配失敗 → 檢查「區域自動遞補」設定
     └─ 關閉：暫停等待，持續刷新尋找指定區域
     └─ 開啟：使用「區域排序方式」自動選擇任何可用區域
   ↓
5. 設定票數（自動填入）
   ↓
6. 辨識驗證碼（如果有）
   - 自動 OCR 辨識
   - 自動填入（或等待手動確認）
   ↓
7. 勾選同意條款
   ↓
8. 送出訂單
   ↓
9. 完成！🎉
```

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

### Q2: 程式報錯 "找不到日期" 或卡住不動
**可能原因**：
- 日期關鍵字設定錯誤
- 活動尚未開賣或日期已售完
- 「日期自動遞補」已關閉（程式在等待指定日期）

**解決方法**：
1. 檢查圖形介面中「日期關鍵字」欄位是否正確
   - 手動打開活動頁面，複製日期文字，確認關鍵字匹配
2. 開啟「日期自動遞補」
   - 在「基本設定」頁籤中勾選「日期自動遞補」
   - 確保「日期排序方式」已設定
3. 或將「日期關鍵字」欄位留空
   - 直接使用「日期排序方式」自動選擇
4. 確認活動是否確實有開賣或可用日期

---

### Q3: 程式選錯區域
**可能原因**：
- 「區域關鍵字」設定不夠精確
- 沒有設定「排除關鍵字」

**解決方法**：
1. 使用更精確的關鍵字，例如在「區域關鍵字」欄位填寫「搖滾A區」而不是「搖滾」
2. 在「排除關鍵字」欄位設定要排除的區域
3. 調整「區域排序方式」設定

---

### Q4: 驗證碼辨識失敗
**說明**：
- OCR 辨識率約 80-90%
- 辨識失敗很正常

**解決方法**：
1. 在圖形介面中取消勾選「掛機模式」，辨識後等待手動確認
2. 或取消勾選「OCR」，完全手動輸入

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

### Q6: 拓元（TixCraft）出現「瀏覽器異常」頁面
**可能原因**：
- 刷新頻率太高，觸發拓元的反爬蟲機制
- TixCraft 會偵測短時間內過多的請求並阻擋

**解決方法**：
1. **調慢刷新速度**：在圖形介面的「進階設定」頁籤中，增加「自動刷新間隔秒數」
   - 建議設定為 **3-5 秒**（預設可能太快）
2. **等待後重試**：被阻擋後等待 1-2 分鐘再繼續
3. **避免多開**：不要同時開啟多個搶票視窗
4. **清除瀏覽器快取**：有時快取會導致異常

**設定位置**：
- 進階設定 → 「自動刷新間隔秒數」（auto_reload_page_interval）

**注意**：這是 TixCraft 的正常防護機制，不是程式 Bug。調慢速度可以有效避免此問題。

---

### Q7: 出現「ddddocr 組件無法使用，您可能在 ARM 環境下運行」
**可能原因**：
- **Python 版本過新**（3.13+）：ddddocr 依賴的 onnxruntime 尚不支援
- **ARM 環境**：Apple Silicon Mac（M1/M2/M3）未安裝 Rosetta
- **套件安裝不完整**：onnxruntime 安裝失敗

**解決方法**：

**方法 1：降級 Python 版本（推薦）**
```bash
# 安裝 Python 3.10（推薦）或 3.11/3.12
# 下載網址：https://www.python.org/downloads/

# 確認版本
python --version
# 應顯示 Python 3.10.x 或 3.11.x 或 3.12.x
```

**方法 2：Apple Silicon Mac 用戶**
```bash
# 使用 Rosetta 執行 x86 版 Python
arch -x86_64 python3 nodriver_tixcraft.py --input settings.json

# 或安裝 x86 版 Homebrew 和 Python
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**方法 3：重新安裝 OCR 套件**
```bash
pip uninstall ddddocr onnxruntime onnxruntime-gpu -y
pip install ddddocr
```

**支援的 Python 版本**：3.9、3.10（推薦）、3.11、3.12

**參考**：[Issue #7](https://github.com/bouob/tickets_hunter/issues/7)

---

## 🔄 程式更新

### 取得最新版本

1. 前往 [GitHub Releases](https://github.com/bouob/tickets_hunter/releases)
2. 下載最新版本的 ZIP 檔案
3. 解壓縮到新目錄（建議保留舊版本備份）
4. 複製您的 `src/settings.json` 到新目錄
5. 重新安裝相依套件：
   ```bash
   cd tickets_hunter
   pip install -r requirement.txt
   ```

**提示**：
- 查看 [CHANGELOG.md](../CHANGELOG.md) 了解版本更新內容
- 設定檔 `settings.json` 通常可直接沿用
- 如遇問題，可參考新版本的 `settings.json.default` 範本

**建議**：定期更新以獲得最新功能和錯誤修復。

---

## 📚 下一步

恭喜您完成第一次設定！接下來您可以：

1. **深入了解關鍵字機制** - [關鍵字與回退機制](keyword-mechanism.md)
2. **探索進階設定** - [詳細設定說明](settings-guide.md)

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

## 💬 需要協助？

遇到問題或有疑問？歡迎到社群尋求協助：

- 🙋 **[Q&A 問題解答](https://github.com/bouob/tickets_hunter/discussions/categories/q-a)** - 使用疑問先來這裡問
- 💬 **[一般討論](https://github.com/bouob/tickets_hunter/discussions/categories/general)** - 分享使用經驗
- 🐛 **[回報 Bug](https://github.com/bouob/tickets_hunter/issues/new?template=bug_report.md)** - 確定是程式錯誤請開 Issue
- 💡 **[功能建議](https://github.com/bouob/tickets_hunter/discussions/categories/ideas)** - 想要新功能到這裡提案

---

**祝您搶票成功！** 🎉

*最後更新：2025-12-08 | 版本：1.3*
