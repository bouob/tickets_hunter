# 快速開始指南：Ticketmaster.com NoDriver 遷移

**專案**: Tickets Hunter - 多平台搶票自動化系統
**功能**: Ticketmaster.com NoDriver 平台遷移
**版本**: 1.0.0
**建立日期**: 2025-11-15
**相關規格**: `spec.md`, `research.md`

---

## 目錄

1. [使用前提](#使用前提)
2. [快速測試步驟](#快速測試步驟)
3. [設定檔範例](#設定檔範例)
4. [測試場景](#測試場景)
5. [常見問題](#常見問題)
6. [除錯指南](#除錯指南)

---

## 使用前提

### 1. 環境需求

**必要條件**：

| 項目 | 最低版本 | 推薦版本 | 說明 |
|------|---------|---------|------|
| Python | 3.8+ | 3.10+ | 支援 async/await 語法 |
| NoDriver | 0.31+ | 最新版 | NoDriver 套件 |
| Chrome/Chromium | 90+ | 最新版 | NoDriver 使用的瀏覽器 |
| 作業系統 | Windows 10+ | Windows 11 | 主要測試環境 |

**安裝指令**：

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 或單獨安裝 NoDriver
pip install nodriver
```

**驗證安裝**：

```bash
# 檢查 Python 版本
python --version

# 檢查 NoDriver 安裝
python -c "import nodriver; print(nodriver.__version__)"
```

---

### 2. 設定檔準備

**主設定檔**: `src/settings.json`

**必要配置**（Ticketmaster 專用）：

```json
{
  "homepage": "https://www.ticketmaster.com/artist/[artist_id]",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-12-25"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "[\"VIP\", \"搖滾區\", \"一般區\"]",
    "mode": "from top to bottom"
  },
  "ticket_number": 2,
  "tixcraft": {
    "pass_date_is_sold_out": true
  },
  "ocr_captcha": {
    "enable": false
  },
  "advanced": {
    "verbose": true,
    "headless": false
  },
  "kktix": {
    "auto_reload_coming_soon_page": false
  }
}
```

**重要欄位說明**：

| 欄位 | 說明 | 對應功能需求 |
|------|------|-------------|
| `homepage` | Ticketmaster 活動頁面 URL | FR-001 |
| `webdriver_type` | 必須設定為 `"nodriver"` | 憲法第 I 條 |
| `date_keyword` | 日期關鍵字（逗號分隔） | FR-001 |
| `area_keyword` | 區域關鍵字（JSON 陣列） | FR-005, FR-006 |
| `ticket_number` | 購票張數 | FR-008 |
| `pass_date_is_sold_out` | 是否跳過售罄場次 | FR-003 |
| `verbose` | 是否啟用詳細日誌 | FR-015 |

---

### 3. 登入狀態準備

**重要**：本功能**不包含自動登入**，使用者必須預先完成 Ticketmaster.com 的身份認證。

**登入方式（擇一）**：

#### 方式 1: Cookie 注入（推薦）

1. 手動登入 Ticketmaster.com
2. 使用瀏覽器開發工具匯出 Cookies
3. 將 Cookies 儲存到 `cookies.json`
4. 程式啟動時自動載入 Cookies

**範例 Cookie 格式**：

```json
[
  {
    "name": "session_id",
    "value": "abc123...",
    "domain": ".ticketmaster.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": true,
    "secure": true
  }
]
```

#### 方式 2: 手動登入（測試用）

1. 設定 `headless: false`（顯示瀏覽器視窗）
2. 程式啟動後手動登入
3. 登入完成後程式繼續執行

**驗證登入狀態**：

- 訪問 `https://www.ticketmaster.com/` 後應顯示已登入狀態
- 使用者名稱應顯示在頁面右上角

---

## 快速測試步驟

### 測試前準備

**重要**：測試前必須刪除暫停檔案，否則程式會立即進入暫停狀態。

```bash
# Git Bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt

# Windows CMD
del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul
```

---

### 步驟 1: 設定 Ticketmaster.com URL

**編輯 `src/settings.json`**：

```json
{
  "homepage": "https://www.ticketmaster.com/artist/2157132"
}
```

**URL 格式**：
- `/artist/[artist_id]` - 藝人活動頁面（觸發日期選擇）
- 範例：`https://www.ticketmaster.com/artist/2157132`（Taylor Swift）

**如何取得 artist_id**：
1. 訪問 Ticketmaster.com 搜尋藝人
2. 點擊藝人名稱進入活動頁面
3. 從 URL 複製 artist_id（例：`/artist/2157132`）

---

### 步驟 2: 設定日期/區域關鍵字

**日期關鍵字範例**：

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-12-25"
  }
}
```

**關鍵字格式**：
- 精確日期：`"2025-12-25"`
- 模糊匹配：`"Christmas"`（匹配包含 "Christmas" 的場次）
- 多組關鍵字：`"2025-12-25,Christmas"`（逗號分隔）

---

**區域關鍵字範例**：

```json
{
  "area_auto_select": {
    "enable": true,
    "area_keyword": "[\"VIP\", \"搖滾區\", \"一般區\"]"
  }
}
```

**關鍵字格式**：
- JSON 陣列格式：`["第一組", "第二組", "第三組"]`
- 支援回退機制：若第一組無匹配，自動嘗試第二組
- 每組可包含多個關鍵字（空白分隔 AND 邏輯）：`["VIP 最佳視野", "一般區"]`

---

### 步驟 3: 執行測試指令

**Git Bash**（推薦）：

```bash
cd /d/Desktop/bouob-TicketHunter\(MaxBot\)/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
echo "" > .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**Windows CMD**：

```cmd
cd "D:\Desktop\bouob-TicketHunter(MaxBot)\tickets_hunter" && del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul && echo. > .temp\test_output.txt && timeout 30 python -u src\nodriver_tixcraft.py --input src\settings.json > .temp\test_output.txt 2>&1
```

**參數說明**：
- `timeout 30`: 測試執行 30 秒後自動中止
- `--input src/settings.json`: 指定設定檔路徑
- `> .temp/test_output.txt 2>&1`: 將輸出重定向到日誌檔

---

### 步驟 4: 檢查輸出日誌

**快速檢查指令**：

```bash
# 檢查日期選擇日誌
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域選擇日誌
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt

# 檢查關鍵流程節點
grep "Match Summary\|Selected target\|clicked\|navigat" .temp/test_output.txt

# 檢查錯誤（輔助）
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

**預期輸出範例**（成功匹配日期）：

```
[DATE KEYWORD] Keyword: 2025-12-25
[DATE SELECT] Match Summary: Total dates matched: 1
[DATE SELECT] Selected target: 2025-12-25 Christmas Concert
[DATE SELECT] Clicked "See Tickets" link
[INFO] Navigated to: https://www.ticketmaster.com/ticket/area/123456
```

**預期輸出範例**（成功匹配區域）：

```
[AREA KEYWORD] Keyword group 1: VIP
[AREA SELECT] Match Summary: Total areas matched: 2 (zone_1, zone_3)
[AREA SELECT] Selected target: zone_1 (VIP區 - 最佳視野)
[AREA SELECT] Executed JavaScript: areaTicket("zone_1", "map");
```

---

## 設定檔範例

### 範例 1: 完整的測試設定（日期 + 區域 + 票數）

```json
{
  "homepage": "https://www.ticketmaster.com/artist/2157132",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-12-25,Christmas"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "[\"VIP\", \"搖滾區\", \"一般區\"]",
    "mode": "from top to bottom"
  },
  "ticket_number": 2,
  "tixcraft": {
    "pass_date_is_sold_out": true
  },
  "ocr_captcha": {
    "enable": false
  },
  "advanced": {
    "verbose": true,
    "headless": false
  },
  "kktix": {
    "auto_reload_coming_soon_page": false
  }
}
```

**用途**：完整測試日期選擇、區域選擇與票數設定的整合流程

---

### 範例 2: 僅測試日期選擇

```json
{
  "homepage": "https://www.ticketmaster.com/artist/2157132",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": true,
    "date_keyword": "2025-12-25"
  },
  "area_auto_select": {
    "enable": false
  },
  "advanced": {
    "verbose": true,
    "headless": false
  }
}
```

**用途**：單獨測試日期選擇功能，驗證關鍵字匹配邏輯

---

### 範例 3: 僅測試區域選擇

**前提**：手動導航至座位選擇頁面（URL 包含 `/ticket/area/`）

```json
{
  "homepage": "https://www.ticketmaster.com/ticket/area/123456",
  "webdriver_type": "nodriver",
  "date_auto_select": {
    "enable": false
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "[\"VIP\"]"
  },
  "advanced": {
    "verbose": true,
    "headless": false
  }
}
```

**用途**：單獨測試區域選擇功能，驗證 zone_info 解析與關鍵字匹配

---

### 範例 4: 多組區域關鍵字回退測試

```json
{
  "area_auto_select": {
    "enable": true,
    "area_keyword": "[\"超級VIP 最佳視野\", \"VIP\", \"搖滾區\", \"一般區\"]",
    "mode": "from top to bottom"
  }
}
```

**用途**：測試多組關鍵字回退機制（對應 FR-006）

**預期行為**：
1. 嘗試匹配 "超級VIP 最佳視野"（兩個關鍵字 AND 邏輯）
2. 若失敗，嘗試匹配 "VIP"
3. 若失敗，嘗試匹配 "搖滾區"
4. 若失敗，嘗試匹配 "一般區"

---

## 測試場景

### 場景 1: 日期選擇 - 成功匹配單一日期

**設定**：

```json
{
  "date_keyword": "2025-12-25"
}
```

**預期結果**：
- 找到 1 個匹配的日期（"2025-12-25"）
- 點擊 "See Tickets" 連結
- 導航至座位選擇頁面

**驗證方式**：

```bash
grep "\[DATE SELECT\] Match Summary" .temp/test_output.txt
# 輸出: [DATE SELECT] Match Summary: Total dates matched: 1
```

---

### 場景 2: 日期選擇 - 跳過售罄場次

**設定**：

```json
{
  "date_keyword": "2025-12-25",
  "tixcraft": {
    "pass_date_is_sold_out": true
  }
}
```

**預期結果**：
- 找到 1 個匹配的日期，但狀態為 "Sold out"
- 跳過該場次
- 總匹配數為 0

**驗證方式**：

```bash
grep "Sold out\|SOLD" .temp/test_output.txt
# 輸出: [DATE SELECT] Skipped sold-out event: 2025-12-25
```

---

### 場景 3: 區域選擇 - 成功匹配 VIP 區

**設定**：

```json
{
  "area_keyword": "[\"VIP\"]"
}
```

**前提**：頁面包含 zone_info：

```json
{
  "zone_1": {
    "areaStatus": "AVAILABLE",
    "groupName": "VIP區",
    "description": "最佳視野",
    "price": [{"ticketPrice": "3500"}]
  }
}
```

**預期結果**：
- 找到 1 個匹配的區域（zone_1）
- 執行 JavaScript: `areaTicket("zone_1", "map");`

**驗證方式**：

```bash
grep "\[AREA SELECT\] Executed JavaScript" .temp/test_output.txt
# 輸出: [AREA SELECT] Executed JavaScript: areaTicket("zone_1", "map");
```

---

### 場景 4: 區域選擇 - 回退到第二組關鍵字

**設定**：

```json
{
  "area_keyword": "[\"超級VIP\", \"VIP\"]"
}
```

**前提**：頁面不包含 "超級VIP"，但包含 "VIP"

**預期結果**：
- 第一組關鍵字無匹配（"超級VIP"）
- 自動回退到第二組關鍵字（"VIP"）
- 找到 1 個匹配的區域

**驗證方式**：

```bash
grep "\[AREA KEYWORD\] Fallback" .temp/test_output.txt
# 輸出: [AREA KEYWORD] Fallback to keyword group 2: VIP
```

---

### 場景 5: 票數設定 - 成功設定 2 張票

**設定**：

```json
{
  "ticket_number": 2
}
```

**前提**：頁面包含 `#ticketPriceList` 表格與 `select` 元素

**預期結果**：
- 找到 `select` 元素
- 設定票數為 2
- 點擊 `#autoMode` 按鈕

**驗證方式**：

```bash
grep "\[TICKET NUMBER\]" .temp/test_output.txt
# 輸出: [TICKET NUMBER] Set ticket count to: 2
```

---

## 常見問題

### 問題 1: zone_info 解析失敗

**錯誤訊息**：

```
[ERROR] Failed to parse zone_info: Expecting property name enclosed in double quotes
```

**原因**：
- zone_info JSON 格式包含尾部逗號或換行符
- JavaScript 變數 `zone` 為局部變數無法直接存取

**解決方案**：

1. 檢查 `ticketmaster_parse_zone_info()` 是否正確實作字串清理邏輯
2. 使用 verbose 模式檢查原始字串：

```bash
grep "\[DEBUG\] Raw zone_string" .temp/test_output.txt
```

3. 若仍失敗，嘗試使用字串提取方法（回退方案）

**參考文件**：`contracts/zone-info-schema.md` - 錯誤處理章節

---

### 問題 2: 元素定位失敗

**錯誤訊息**：

```
[ERROR] Failed to locate element: #list-view > div > div.event-listing
```

**原因**：
- 頁面結構已變更（Ticketmaster 更新了 HTML）
- 頁面尚未完全載入

**解決方案**：

1. 檢查當前 URL 是否正確（`grep "Current URL" .temp/test_output.txt`）
2. 使用瀏覽器開發工具檢查頁面 HTML 結構
3. 若選擇器已變更，更新程式碼中的選擇器常數
4. 若頁面載入緩慢，增加等待時間（使用 JavaScript Promise 條件等待）

**參考文件**：`research.md` - 函數 1（日期選擇選擇器）

---

### 問題 3: 跨平台干擾問題

**錯誤訊息**：

```
[WARNING] Ticketmaster logic triggered on TixCraft page
```

**原因**：
- domain_name 判斷邏輯錯誤
- Ticketmaster 特定邏輯沒有正確檢查 domain_name

**解決方案**：

1. 檢查 `domain_name` 提取邏輯：

```python
domain_name = url.split('/')[2]
if 'ticketmaster' in domain_name:
    # Ticketmaster 特定邏輯
else:
    # 其他平台邏輯
```

2. 確保所有 Ticketmaster 特定函數都有 domain_name 檢查
3. 執行跨平台迴歸測試（測試 tixcraft.com, teamear.tixcraft.com 等）

**參考文件**：`spec.md` - 風險 2（Tixcraft 家族共享代碼污染）

---

### 問題 4: JavaScript 執行失敗（areaTicket 函數不存在）

**錯誤訊息**：

```
[ERROR] JavaScript execution failed: areaTicket is not defined
```

**原因**：
- 頁面不是座位選擇頁面
- 頁面 JavaScript 尚未完全載入

**解決方案**：

1. 檢查當前 URL 是否包含 `/ticket/area/`
2. 使用 JavaScript 檢查函數存在性：

```python
result = await tab.evaluate('''
    typeof areaTicket === 'function'
''')
if not result:
    print("[ERROR] areaTicket function not available")
```

3. 若函數不存在，等待頁面完全載入後重試

**參考文件**：`research.md` - 函數 3（區域選擇 JavaScript 執行）

---

### 問題 5: 程式立即進入暫停狀態

**錯誤訊息**：

```
[INFO] Detected MAXBOT_INT28_IDLE.txt, pausing...
```

**原因**：
- 暫停檔案 `MAXBOT_INT28_IDLE.txt` 存在

**解決方案**：

刪除暫停檔案後重新執行：

```bash
# Git Bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt

# Windows CMD
del /Q MAXBOT_INT28_IDLE.txt src\MAXBOT_INT28_IDLE.txt 2>nul
```

**參考文件**：`CLAUDE.md` - 快速測試指南

---

## 除錯指南

### 除錯步驟

#### 步驟 1: 啟用詳細日誌

**編輯 `src/settings.json`**：

```json
{
  "advanced": {
    "verbose": true
  }
}
```

**效果**：
- 輸出日期匹配摘要
- 輸出區域匹配摘要
- 輸出元素定位詳細訊息

---

#### 步驟 2: 檢查錯誤日誌

**快速篩選錯誤**：

```bash
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
```

**常見錯誤類型**：
- `[ERROR] Failed to locate element` - 元素定位失敗
- `[ERROR] JSON parse failed` - JSON 解析失敗
- `[WARNING] No dates matched` - 日期關鍵字無匹配

---

#### 步驟 3: 檢查 Spec 需求

**對應 FR 檢查清單**（spec.md）：

1. **FR-001**: 系統是否能識別並點選符合日期關鍵字的場次？
2. **FR-002**: 系統是否正確過濾包含 "See Tickets" 的場次？
3. **FR-003**: 系統是否跳過售罄場次（若啟用）？
4. **FR-004**: 系統是否能解析 zone_info JavaScript 變數？
5. **FR-005**: 系統是否根據 areaStatus 排除 UNAVAILABLE 區域？

**檢查方式**：

```bash
# 檢查 FR-001（日期匹配）
grep "\[DATE KEYWORD\]" .temp/test_output.txt

# 檢查 FR-002（See Tickets 過濾）
grep "See Tickets" .temp/test_output.txt

# 檢查 FR-004（zone_info 解析）
grep "zone_info" .temp/test_output.txt
```

---

#### 步驟 4: 查閱 API 指南

**NoDriver API 參考**：`docs/06-api-reference/nodriver_api_guide.md`

**常見 API 問題**：
- `tab.query_selector()` 返回 `None` - 元素不存在或選擇器錯誤
- `tab.evaluate()` 拋出例外 - JavaScript 語法錯誤或變數不存在
- `element.click()` 無反應 - 元素不可見或被遮蔽

**除錯技巧**：

```python
# 檢查元素是否存在
element = await tab.query_selector('#mapSelectArea')
if element:
    print("[DEBUG] Element found")
else:
    print("[DEBUG] Element not found")

# 檢查 JavaScript 變數是否存在
result = await tab.evaluate('typeof zone !== "undefined"')
print(f"[DEBUG] zone variable exists: {result}")
```

---

#### 步驟 5: 搜尋疑難排解案例

**疑難排解索引**：`docs/08-troubleshooting/README.md`

**搜尋關鍵字**：
- "ticketmaster" - Ticketmaster 特定問題
- "zone_info" - zone_info 解析問題
- "date select" - 日期選擇問題
- "area select" - 區域選擇問題

---

### 除錯日誌範例

**完整的除錯日誌輸出**：

```
[INFO] Starting NoDriver Ticketmaster automation
[INFO] Current URL: https://www.ticketmaster.com/artist/2157132
[INFO] Domain name: www.ticketmaster.com

[DATE KEYWORD] Enabled: True
[DATE KEYWORD] Keyword: 2025-12-25
[DATE SELECT] Found 5 date blocks
[DATE SELECT] Block 1: 2025-12-20 Winter Concert - See Tickets
[DATE SELECT] Block 2: 2025-12-25 Christmas Concert - See Tickets
[DATE SELECT] Block 3: 2025-12-31 New Year Concert - Sold out
[DATE SELECT] Block 4: 2026-01-01 New Year Concert - See Tickets
[DATE SELECT] Block 5: 2026-01-15 Special Concert - See Tickets
[DATE SELECT] Match Summary: Total dates matched: 1
[DATE SELECT] Selected target: 2025-12-25 Christmas Concert
[DATE SELECT] Clicked "See Tickets" link
[INFO] Navigated to: https://www.ticketmaster.com/ticket/area/123456

[AREA KEYWORD] Enabled: True
[AREA KEYWORD] Keyword group 1: VIP
[AREA SELECT] Parsing zone_info...
[DEBUG] Raw zone_string (first 200 chars): {"zone_1":{"areaStatus":"AVAILABLE","groupName":"VIP區",...
[AREA SELECT] Successfully parsed zone_info (3 zones)
[AREA SELECT] Zone 1: zone_1 - VIP區 - 最佳視野 - 3500 - AVAILABLE
[AREA SELECT] Zone 2: zone_2 - 搖滾區 - 站立區 - 2500 - AVAILABLE
[AREA SELECT] Zone 3: zone_3 - 一般區 - 標準座位 - 1500 - UNAVAILABLE
[AREA SELECT] Match Summary: Total areas matched: 1 (zone_1)
[AREA SELECT] Selected target: zone_1 (VIP區 - 最佳視野)
[AREA SELECT] Executed JavaScript: areaTicket("zone_1", "map");
[INFO] Area selection completed

[TICKET NUMBER] Enabled: True
[TICKET NUMBER] Target count: 2
[TICKET NUMBER] Found ticketPriceList table
[TICKET NUMBER] Found select element
[TICKET NUMBER] Set ticket count to: 2
[TICKET NUMBER] Clicked #autoMode button
[INFO] Ticket number assignment completed

[SUCCESS] Ticketmaster automation completed successfully
```

---

## 附錄：快速參考

### 關鍵選擇器

| 選擇器 | 用途 | 對應 FR |
|--------|------|---------|
| `#list-view > div > div.event-listing > div.accordion-wrapper > div` | 日期列表 | FR-002 |
| `#mapSelectArea` | zone_info 容器 | FR-004 |
| `#ticketPriceList` | 票價表格 | FR-007 |
| `#loadingmap` | 載入動畫 | FR-007 |
| `#autoMode` | 自動模式按鈕 | FR-009 |
| `#promoBox` | 促銷碼輸入框 | FR-010 |
| `#TicketForm_agree` | 同意條款勾選框 | FR-011 |

---

### 常用指令

```bash
# 刪除暫停檔案
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt

# 快速測試（30 秒）
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json

# 檢查日誌（日期選擇）
grep "\[DATE SELECT\]" .temp/test_output.txt

# 檢查日誌（區域選擇）
grep "\[AREA SELECT\]" .temp/test_output.txt

# 檢查錯誤
grep -i "ERROR" .temp/test_output.txt
```

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**維護者**: Tickets Hunter 開發團隊
**相關文件**:
- 功能規格：`spec.md`
- 技術研究：`research.md`
- 資料模型：`data-model.md`
- 函數介面：`contracts/function-interface.md`
- JSON Schema：`contracts/zone-info-schema.md`
