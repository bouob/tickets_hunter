**文件說明**：標準化的測試執行指南，涵蓋快速測試流程、測試輸出檢查、驗證重點與除錯方法。

**最後更新**：2025-11-12

---

# 測試執行指南

> **目標**：定義除錯時的標準測試執行方法，確保測試流程一致且高效

## 快速參考

### 完整測試流程（一鍵執行）

**推薦方式（使用 timeout 自動終止）**：

```bash
# Chrome/Selenium 版本（30秒自動終止，Git Bash）
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && rm -rf src/__pycache__ && rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && echo "" > .temp/test_output.txt && timeout 30 python -u src/chrome_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1

# NoDriver 版本（30秒自動終止，Git Bash）
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && rm -rf src/__pycache__ && rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && echo "" > .temp/test_output.txt && timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

> **重要**：每次執行測試前必須清除 `__pycache__`，確保 Python 載入最新修改的程式碼。

**重要修正**：檔案路徑必須加上 `src/` 前綴
- ✅ 正確：`python -u src/nodriver_tixcraft.py --input src/settings.json`
- ❌ 錯誤：`python -u nodriver_tixcraft.py --input settings.json`（檔案實際在 src/ 目錄下）

**說明**：
- `timeout 30` 會在 30 秒後自動發送終止信號給 Python 程序
- 使用正斜線 `/` 路徑格式，在 Git Bash、Windows CMD 和 PowerShell 中都能正常運作

**備用方式（Windows CMD，需手動終止）**：

```bash
# Chrome/Selenium 版本
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && rmdir /S /Q src\__pycache__ 2>nul && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && start /B python -u src\chrome_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1 && timeout /t 30 /nobreak >nul && taskkill //F //IM python.exe //IM chrome.exe

# NoDriver 版本
cd "D:\Desktop\MaxBot搶票機器人\tickets_hunter" && rmdir /S /Q src\__pycache__ 2>nul && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && start /B python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1 && timeout /t 30 /nobreak >nul && taskkill //F //IM python.exe //IM chrome.exe
```

### 檢查測試結果（驗證程式邏輯）

```bash
# 查看完整輸出
cat .temp/test_output.txt

# 1. 檢查日期選擇邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 2. 檢查區域選擇邏輯
grep "\[AREA KEYWORD\]" .temp/test_output.txt

# 3. 檢查關鍵流程節點
grep "Match Summary\|Selected target\|Successfully clicked\|navigat" .temp/test_output.txt

# 4. 快速檢查異常（輔助，但程式可能沒有寫入這些標籤）
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

**驗證重點**：
- 日期匹配數量是否符合預期（`Total dates matched`）
- 區域匹配數量是否符合預期（`Total areas matched`）
- 選擇策略是否正確執行（`auto_select_mode`）
- AND 邏輯/回退機制是否觸發（`AND logic failed` → 回退到下一組）

---

## 標準測試執行指令

### 基本執行（前台測試）

**Chrome/Selenium 版本**：
```bash
cd tickets_hunter/src
python chrome_tixcraft.py --input settings.json
```

**NoDriver 版本**：
```bash
cd tickets_hunter/src
python nodriver_tixcraft.py --input settings.json
```

### 命令列參數說明

**常用參數（除錯測試）**：

| 參數 | 說明 | 範例 |
|-----|------|------|
| `--input` | 設定檔路徑（必要） | `--input settings.json` |
| `--date_keyword` | 覆寫日期關鍵字 ⭐ | `--date_keyword "12/25"` |
| `--date_auto_select_mode` | 覆寫日期選擇模式 ⭐ | `--date_auto_select_mode "from top to bottom"` |
| `--area_keyword` | 覆寫區域關鍵字 (NoDriver) ⭐ | `--area_keyword "搖滾區"` |
| `--area_auto_select_mode` | 覆寫區域選擇模式 (NoDriver) ⭐ | `--area_auto_select_mode "from bottom to top"` |
| `--ticket_number` | 覆寫票數設定 | `--ticket_number 2` |
| `--tixcraft_sid` | TixCraft Cookie（進階） | `--tixcraft_sid abc123...` |
| `--ibonqware` | ibon Cookie（進階） | `--ibonqware mem_id=...` |

**進階參數（少用，僅特殊需求）**：

| 參數 | 說明 | 範例 |
|-----|------|------|
| `--headless` | 無頭模式 | `--headless true` |
| `--homepage` | 覆寫首頁網址 | `--homepage https://tixcraft.com/...` |
| `--browser` | 覆寫瀏覽器選擇 | `--browser chrome` |
| `--window_size` | 視窗大小 | `--window_size 1920x1080` |
| `--proxy_server` | 代理伺服器 | `--proxy_server 127.0.0.1:8080` |

### 參數組合範例

**覆寫多個參數測試**：
```bash
cd tickets_hunter/src
python chrome_tixcraft.py --input settings.json --ticket_number 2 --headless true
```

**使用代理伺服器測試**：
```bash
cd tickets_hunter/src
python chrome_tixcraft.py --input settings.json --proxy_server 127.0.0.1:8080
```

**除錯區域選擇（NoDriver，覆寫設定檔）**：
```bash
cd tickets_hunter/src
# 測試特定關鍵字匹配
python nodriver_tixcraft.py --input settings.json --area_keyword "搖滾區"

# 測試不同選擇模式
python nodriver_tixcraft.py --input settings.json --area_auto_select_mode "from bottom to top"

# 組合測試：指定日期與區域
python nodriver_tixcraft.py --input settings.json --date_keyword "12/25" --area_keyword "VIP"
```

---

## 背景測試流程

### 步驟 1：清空測試輸出檔案與暫停檔案

**重要**：每次測試前必須清空，避免混淆新舊輸出或程式啟動即暫停

```bash
# Windows - 清空測試輸出檔案
echo. > .temp\test_output.txt

# 刪除 idle 暫停檔案（如果存在）
del /Q MAXBOT_INT28_IDLE.txt 2>nul
del /Q src\MAXBOT_INT28_IDLE.txt 2>nul

# 或使用一行指令完成（推薦）
echo. > .temp\test_output.txt && del /Q MAXBOT_INT28_IDLE.txt 2>nul && del /Q src\MAXBOT_INT28_IDLE.txt 2>nul
```

**說明**：
- `MAXBOT_INT28_IDLE.txt` 是暫停機制建立的檔案
- 如果此檔案存在，程式啟動後會立即進入暫停狀態
- 測試前必須刪除，確保程式正常執行
- `2>nul` 用於隱藏「檔案不存在」的錯誤訊息

### 步驟 2：背景執行測試

**基本背景執行**（無自動中斷）：
```bash
# Chrome/Selenium 版本
python -u src/chrome_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1

# NoDriver 版本
python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**參數說明**：
- `-u`: Unbuffered 模式，確保輸出即時寫入檔案
- `> .temp\test_output.txt`: 重定向標準輸出
- `2>&1`: 同時重定向標準錯誤輸出

### 步驟 3：30秒強制中斷測試

**方法 1：使用 timeout + taskkill（推薦）**：

```bash
# Chrome/Selenium 版本
start /B python -u src/chrome_tixcraft.py --input src/settings.json > .temp\test_output.txt 2>&1 && timeout /t 30 /nobreak >nul && taskkill //F //IM python.exe //IM chrome.exe

# NoDriver 版本
start /B python -u src/nodriver_tixcraft.py --input src/settings.json > .temp\test_output.txt 2>&1 && timeout /t 30 /nobreak >nul && taskkill //F //IM python.exe //IM chrome.exe
```

**參數說明**：
- `start /B`: 背景執行（不開新視窗）
- `timeout /t 30 /nobreak`: 等待 30 秒（不可中斷）
- `>nul`: 隱藏 timeout 的輸出訊息
- `taskkill //F //IM python.exe`: 強制終止所有 Python 程序
- `taskkill //F //IM chrome.exe`: 強制終止所有 Chrome 程序

**方法 2：使用 PowerShell（更可靠）**：

```bash
# Chrome/Selenium 版本
powershell -Command "Start-Process python -ArgumentList '-u','src/chrome_tixcraft.py','--input','src/settings.json' -RedirectStandardOutput .temp\test_output.txt -RedirectStandardError .temp\test_output.txt -NoNewWindow; Start-Sleep 30; Stop-Process -Name python -Force; Stop-Process -Name chrome -Force"

# NoDriver 版本
powershell -Command "Start-Process python -ArgumentList '-u','src/nodriver_tixcraft.py','--input','src/settings.json' -RedirectStandardOutput .temp\test_output.txt -RedirectStandardError .temp\test_output.txt -NoNewWindow; Start-Sleep 30; Stop-Process -Name python -Force; Stop-Process -Name chrome -Force"
```

### 步驟 4：手動中斷測試（緊急使用）

**立即終止所有測試**：
```bash
# 終止所有 Python 程序
taskkill //F //IM python.exe

# 終止所有 Chrome 程序
taskkill //F //IM chrome.exe

# 一次終止兩者
taskkill //F //IM python.exe //IM chrome.exe
```

**檢查程序是否還在運行**：
```bash
# 檢查 Python 程序
tasklist | findstr python

# 檢查 Chrome 程序
tasklist | findstr chrome
```

---

## 輸出檢查方法

### 查看完整輸出

```bash
# 方法 1：直接查看
type .temp\test_output.txt

# 方法 2：分頁查看（若輸出很長）
more .temp\test_output.txt

# 方法 3：查看最後 N 行
powershell Get-Content .temp\test_output.txt -Tail 50
```

### 功能邏輯驗證（主要方法）

> **重要**：程式使用日誌標籤系統記錄執行邏輯，而非傳統的 ERROR/WARNING 訊息。
> 測試驗證應該基於功能邏輯是否符合預期，而非只檢查錯誤關鍵字。

#### 1. 日期選擇邏輯驗證

```bash
# 查看完整日期選擇流程（關鍵字匹配 + 點擊）
type .temp\test_output.txt | findstr /C:"[DATE KEYWORD]" /C:"[DATE SELECT]"

# 只看匹配摘要
type .temp\test_output.txt | findstr /C:"Match Summary" /C:"Total dates matched"

# 檢查 AND 邏輯執行情況
type .temp\test_output.txt | findstr /C:"AND logic" /C:"All AND keywords matched"
```

**預期輸出範例**：
```
[DATE KEYWORD] Total dates matched: 3
[DATE SELECT] Auto-select mode: from top to bottom
[DATE SELECT] Successfully clicked via button[data-href]
```

#### 2. 區域選擇邏輯驗證

```bash
# 查看完整區域選擇流程
type .temp\test_output.txt | findstr /C:"[AREA KEYWORD]"

# 只看匹配摘要
type .temp\test_output.txt | findstr /C:"Total areas matched" /C:"Selected target index"
```

**預期輸出範例**：
```
[AREA KEYWORD] Total areas matched: 2
[AREA KEYWORD] Selected target index: 0
```

#### 3. 頁面跳轉驗證

```bash
# 檢查點擊與導航
type .temp\test_output.txt | findstr /C:"Successfully clicked" /C:"URL changed" /C:"navigat"
```

#### 4. 特定平台功能

**KKTIX**：
```bash
type .temp\test_output.txt | findstr /C:"[KKTIX]" /C:"[KKTIX AREA]"
```

**Cloudflare**：
```bash
type .temp\test_output.txt | findstr /C:"[CLOUDFLARE]"
```

**驗證碼處理**：
```bash
type .temp\test_output.txt | findstr /C:"[CAPTCHA OCR]" /C:"[IBON CAPTCHA]"
```

**售罄偵測**：
```bash
type .temp\test_output.txt | findstr /C:"[SOLD OUT]"
```

**票種選擇**：
```bash
type .temp\test_output.txt | findstr /C:"[TICKET]"
```

### 輔助檢查（限制：程式可能沒有寫入這些訊息）

> **注意**：以下檢查僅供輔助參考，因為程式設計上並未系統性寫入 ERROR/WARNING 標籤。
> 主要驗證應該基於上方的「功能邏輯驗證」。

**異常關鍵字檢查**：
```bash
# 檢查可能的異常訊息（不保證有）
type .temp\test_output.txt | findstr /C:"ERROR" /C:"Exception" /C:"Traceback"

# 檢查可能的警告（不保證有）
type .temp\test_output.txt | findstr /C:"WARNING" /C:"failed"
```

**設定檔讀取確認**：
```bash
type .temp\test_output.txt | findstr /C:"config_dict" /C:"settings.json" /C:"webdriver_type"
```

---

## 測試邏輯驗證指南

### 如何判斷測試是否成功

測試驗證應該基於**功能邏輯是否符合預期**，而非只看有無錯誤訊息。

#### 日期選擇功能

**測試目標**：驗證日期關鍵字匹配與選擇邏輯

**檢查步驟**：
1. 查看日誌：`type .temp\test_output.txt | findstr /C:"[DATE KEYWORD]"`
2. 檢查匹配摘要：
   ```
   [DATE KEYWORD] Total dates matched: X
   ```
3. 驗證選擇策略：
   ```
   [DATE SELECT] Auto-select mode: from top to bottom
   [DATE SELECT] Selected target: #1/3
   ```
4. 確認點擊成功：
   ```
   [DATE SELECT] Successfully clicked via button[data-href]
   ```

**成功標準**：
- `Total dates matched > 0`（如果設定了關鍵字）
- `Selected target` 顯示正確的索引
- `Successfully clicked` 出現

**失敗情況**：
- `Total dates matched: 0` 且設定了關鍵字 → 關鍵字匹配失敗
- `No target selected` → 沒有找到可選擇的日期
- `All click methods failed` → 點擊失敗

#### 區域選擇功能

**測試目標**：驗證區域關鍵字匹配與選擇邏輯

**檢查步驟**：
1. 查看日誌：`type .temp\test_output.txt | findstr /C:"[AREA KEYWORD]"`
2. 檢查匹配摘要：
   ```
   [AREA KEYWORD] Total areas matched: X
   ```
3. 檢查座位數量驗證：
   ```
   [AREA KEYWORD]   Sufficient seats available
   ```

**成功標準**：
- `Total areas matched > 0`（如果設定了關鍵字）
- `Sufficient seats available`（如果檢查座位數）
- `Selected target index: X` 出現

**失敗情況**：
- `Total areas matched: 0` 且設定了關鍵字 → 關鍵字匹配失敗
- `Insufficient seats` → 座位數不足
- `No areas matched` → 沒有找到匹配的區域

#### AND 邏輯驗證

**測試目標**：驗證多關鍵字 AND 邏輯是否正確執行

**檢查步驟**：
1. 查看 AND 邏輯執行：
   ```bash
   type .temp\test_output.txt | findstr /C:"AND logic"
   ```
2. 確認匹配結果：
   ```
   [DATE KEYWORD]   All AND keywords matched
   ```
   或
   ```
   [DATE KEYWORD]   AND logic failed (not all matched)
   ```

**成功標準**：
- 所有關鍵字都匹配時：`All AND keywords matched`
- 部分關鍵字不匹配時：`AND logic failed` → 應該回退到下一組關鍵字

#### 回退機制驗證

**測試目標**：驗證關鍵字失敗時是否正確回退到自動選擇模式

**檢查步驟**：
1. 如果關鍵字匹配失敗（`Total dates matched: 0`）
2. 檢查是否執行自動選擇模式：
   ```
   [DATE SELECT] Auto-select mode: from top to bottom
   ```

**成功標準**：
- 關鍵字失敗時，仍能看到 `[DATE SELECT]` 日誌
- `auto_select_mode` 設定正確應用

### 常見測試場景

#### 場景 1：測試特定日期關鍵字

**設定**：`date_keyword: "12/25"`

**預期日誌**：
```
[DATE KEYWORD] Raw input: '12/25'
[DATE KEYWORD] Checking 5 available dates...
[DATE KEYWORD]   Matched keyword: '12/25'
[DATE KEYWORD] Total dates matched: 1
[DATE SELECT] Selected target: #1/1
[DATE SELECT] Successfully clicked via button[data-href]
```

#### 場景 2：測試 AND 邏輯

**設定**：`date_keyword: "週六+晚上"`

**預期日誌**：
```
[DATE KEYWORD] Checking AND logic: 週六+晚上
[DATE KEYWORD]     [MATCH] '週六': True
[DATE KEYWORD]     [MATCH] '晚上': True
[DATE KEYWORD]   All AND keywords matched
[DATE KEYWORD] Total dates matched: 1
```

#### 場景 3：測試回退機制

**設定**：`date_keyword: "不存在的日期"`, `date_auto_select_mode: "from top to bottom"`

**預期日誌**：
```
[DATE KEYWORD] Total dates matched: 0
[DATE KEYWORD]   No dates matched any keywords
[DATE SELECT] Auto-select mode: from top to bottom
[DATE SELECT] Target selected from 0 matched dates
```

**注意**：即使 `matched_blocks` 為空，程式應該回退到選擇所有可用日期

#### 場景 4：測試區域座位數驗證

**設定**：`ticket_number: 2`, `area_keyword: "搖滾區"`

**預期日誌**：
```
[AREA KEYWORD]   Matching AND keywords: ['搖滾區']
[AREA KEYWORD]     [MATCH] '搖滾區': True
[AREA KEYWORD]   Checking seats: 5
[AREA KEYWORD]   Sufficient seats available
[AREA KEYWORD] Total areas matched: 1
```

### 快速驗證檢查清單

測試完成後，使用此檢查清單快速驗證：

```markdown
□ 日期匹配數量符合預期（`Total dates matched`）
□ 區域匹配數量符合預期（`Total areas matched`）
□ AND 邏輯正確執行（所有關鍵字都匹配）
□ 回退機制正確觸發（關鍵字失敗時使用 auto_select_mode）
□ 點擊成功（`Successfully clicked`）
□ 頁面跳轉（`URL changed` 或下一階段日誌出現）
□ 座位數驗證正確（如適用）
```

---

## 常見問題處理

### 問題 1：瀏覽器視窗彈出

**現象**：即使設定 headless 模式，瀏覽器視窗仍會彈出

**原因**：
- Chrome/NoDriver 在某些情況下會忽略 headless 設定
- 某些平台的驗證機制需要可見視窗

**解決方案**：
1. **接受視窗彈出**：測試時將視窗最小化
2. **自動關閉**：使用 30秒強制中斷機制自動終止
3. **調整 headless 設定**：
   ```json
   "advanced": {
       "headless": true
   }
   ```

### 問題 2：測試輸出檔案找不到

**現象**：執行 `type .temp\test_output.txt` 時顯示檔案不存在

**原因**：`.temp` 目錄不存在

**解決方案**：
```bash
# 建立 .temp 目錄
mkdir .temp

# 或使用完整路徑
mkdir "D:\Desktop\MaxBot搶票機器人\tickets_hunter\.temp"
```

### 問題 3：程序無法終止

**現象**：執行 `taskkill` 後程序仍在運行

**原因**：程序被鎖定或有多個相關程序

**解決方案**：
```bash
# 方法 1：使用 /F 強制終止
taskkill //F //IM python.exe
taskkill //F //IM chrome.exe

# 方法 2：根據 PID 終止（更精確）
tasklist | findstr python
taskkill //F //PID <程序ID>

# 方法 3：使用 PowerShell
powershell Stop-Process -Name python -Force
powershell Stop-Process -Name chrome -Force
```

### 問題 4：輸出檔案為空

**現象**：`.temp\test_output.txt` 存在但內容為空

**原因**：
- 程式啟動失敗（語法錯誤）
- 輸出緩衝未刷新
- 路徑錯誤

**診斷步驟**：
1. **檢查語法**：
   ```bash
   cd tickets_hunter/src
   python -m py_compile chrome_tixcraft.py
   ```

2. **前台執行確認**（查看即時輸出）：
   ```bash
   cd tickets_hunter/src
   python chrome_tixcraft.py --input settings.json
   ```

3. **使用 -u 確保 unbuffered**：
   ```bash
   python -u chrome_tixcraft.py --input settings.json > .temp\test_output.txt 2>&1
   ```

### 問題 5：編碼錯誤（Emoji 相關）

**現象**：輸出檔案包含亂碼或程式崩潰

**原因**：Windows cp950 編碼不支援 Emoji 字符

**解決方案**：
- 確保程式碼中沒有 Emoji 字符
- 檢查 print() 輸出訊息
- 參考 CLAUDE.md 的 Emoji 使用規範

---

## 測試自動化腳本

### 完整測試腳本（Chrome 版本）

建立 `test_chrome.bat`：
```batch
@echo off
cd /d "D:\Desktop\MaxBot搶票機器人\tickets_hunter"

echo [TEST] Clearing test output and idle files...
del /Q MAXBOT_INT28_IDLE.txt 2>nul
del /Q src\MAXBOT_INT28_IDLE.txt 2>nul
echo. > .temp\test_output.txt

echo [TEST] Starting Chrome version test...
start /B python -u src\chrome_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1

echo [TEST] Waiting 30 seconds...
timeout /t 30 /nobreak >nul

echo [TEST] Terminating processes...
taskkill //F //IM python.exe //IM chrome.exe >nul 2>&1

echo [TEST] Test completed. Checking results...
echo.
echo === DATE SELECTION LOGIC ===
type .temp\test_output.txt | findstr /C:"[DATE KEYWORD]" /C:"Total dates matched"
echo.
echo === DATE CLICK RESULT ===
type .temp\test_output.txt | findstr /C:"[DATE SELECT]" /C:"Successfully clicked"
echo.
echo [TEST] Full output saved to .temp\test_output.txt
pause
```

### 完整測試腳本（NoDriver 版本）

建立 `test_nodriver.bat`：
```batch
@echo off
cd /d "D:\Desktop\MaxBot搶票機器人\tickets_hunter"

echo [TEST] Clearing test output and idle files...
del /Q MAXBOT_INT28_IDLE.txt 2>nul
del /Q src\MAXBOT_INT28_IDLE.txt 2>nul
echo. > .temp\test_output.txt

echo [TEST] Starting NoDriver version test...
start /B python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1

echo [TEST] Waiting 30 seconds...
timeout /t 30 /nobreak >nul

echo [TEST] Terminating processes...
taskkill //F //IM python.exe //IM chrome.exe >nul 2>&1

echo [TEST] Test completed. Checking results...
echo.
echo === DATE SELECTION LOGIC ===
type .temp\test_output.txt | findstr /C:"[DATE KEYWORD]" /C:"Total dates matched"
echo.
echo === AREA SELECTION LOGIC ===
type .temp\test_output.txt | findstr /C:"[AREA KEYWORD]" /C:"Total areas matched"
echo.
echo === CLICK RESULTS ===
type .temp\test_output.txt | findstr /C:"Successfully clicked"
echo.
echo [TEST] Full output saved to .temp\test_output.txt
pause
```

---

## 進階技巧

### 並行測試多個設定檔

```batch
@echo off
echo [TEST] Running parallel tests...

start /B python -u src\chrome_tixcraft.py --input src\settings1.json > .temp\test1_output.txt 2>&1
start /B python -u src\chrome_tixcraft.py --input src\settings2.json > .temp\test2_output.txt 2>&1

timeout /t 30 /nobreak >nul
taskkill //F //IM python.exe //IM chrome.exe >nul 2>&1

echo [TEST] Results:
echo === Settings 1 - Date Selection ===
type .temp\test1_output.txt | findstr /C:"Total dates matched"
echo.
echo === Settings 2 - Date Selection ===
type .temp\test2_output.txt | findstr /C:"Total dates matched"
```

### 測試結果自動分析

```bash
# 建立測試報告（擷取關鍵日誌標籤）
powershell -Command "Get-Content .temp\test_output.txt | Select-String '\[DATE KEYWORD\]','\[AREA KEYWORD\]','Total.*matched','Successfully clicked' | Out-File .temp\test_summary.txt"

# 查看摘要
type .temp\test_summary.txt
```

### 長時間測試監控

```bash
# 每 10 秒檢查一次輸出
:loop
timeout /t 10 /nobreak >nul
powershell Get-Content .temp\test_output.txt -Tail 20
goto loop
```

---

## 除錯流程建議

### 標準除錯流程

1. **清空輸出與暫停檔案**：
   ```bash
   echo. > .temp\test_output.txt && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul
   ```

2. **執行測試**（30秒）：
   ```bash
   # 使用快速參考中的完整指令（第 10-31 行）
   ```

3. **驗證功能邏輯**（根據測試功能選擇）：

   **日期選擇測試**：
   ```bash
   # 查看日期匹配摘要
   type .temp\test_output.txt | findstr /C:"[DATE KEYWORD]" /C:"Total dates matched"

   # 查看日期選擇執行
   type .temp\test_output.txt | findstr /C:"[DATE SELECT]" /C:"Successfully clicked"
   ```

   **區域選擇測試**：
   ```bash
   # 查看區域匹配摘要
   type .temp\test_output.txt | findstr /C:"[AREA KEYWORD]" /C:"Total areas matched"
   ```

   **其他功能**：
   ```bash
   # 根據測試功能查看對應的日誌標籤
   # 參考「測試邏輯驗證指南」區塊
   ```

4. **分析測試結果**：
   - 檢查匹配數量是否符合預期
   - 確認選擇策略正確執行
   - 驗證 AND 邏輯與回退機制
   - 參考「測試邏輯驗證指南」中的成功標準

5. **必要時前台執行**（查看完整行為）：
   ```bash
   cd tickets_hunter/src
   python chrome_tixcraft.py --input settings.json
   ```

### 疑難排解優先順序

1. **語法錯誤** → 前台執行確認
2. **設定檔錯誤** → 檢查 settings.json 格式
3. **元素定位失敗** → 查看 API 指南（chrome_api_guide.md 或 nodriver_api_guide.md）
4. **邏輯錯誤** → 查看 structure.md 函數流程
5. **平台特殊問題** → 查看 debugging_methodology.md

---

**更新日期**: 2025-10-28
**相關文件**: [除錯方法論](./debugging_methodology.md) | [Chrome API 指南](./chrome_api_guide.md) | [NoDriver API 指南](./nodriver_api_guide.md) | [程式結構](./structure.md)