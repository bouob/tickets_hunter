---
description: "更新專案版本日期"
allowed-tools: ["Bash"]
model: sonnet
---

自動更新所有檔案中的 `CONST_APP_VERSION` 為當前日期，並更新 JavaScript 版本號時間戳記。

---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---


## 📋 執行步驟

### 1. 取得當前日期與時間

取得系統當前日期並格式化為 `YYYY.MM.DD` 格式，以及時間戳記：

```bash
# Git Bash / Linux（推薦）
TODAY=$(date +%Y.%m.%d)
TIMESTAMP=$(date +%Y%m%d%H)
echo "Today's date: $TODAY"
echo "Timestamp: $TIMESTAMP"
```

**時間戳記格式說明**：
- 格式：`YYYYMMDDHH`（年月日時，24小時制）
- 範例：
  - 上午 02:28 → `2025111102`
  - 下午 15:00 → `2025111115`
  - 晚上 23:45 → `2025111123`
- 用途：JavaScript/CSS 檔案版本號，確保瀏覽器快取更新

### 2. 檢查當前版本號

顯示所有檔案中的當前版本號：

```bash
cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter"

echo "=== 當前版本號 ==="
grep "CONST_APP_VERSION" src/chrome_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/config_launcher.py | head -1
grep "CONST_APP_VERSION" src/settings.py | head -1
grep "版本.*Tickets Hunter" src/www/settings.html | head -1
grep "settings.js?v=" src/www/settings.html | head -1
```

### 3. 更新所有檔案

使用當前日期更新所有 6 個位置：

**目標檔案清單**：
1. `src/chrome_tixcraft.py` - CONST_APP_VERSION
2. `src/nodriver_tixcraft.py` - CONST_APP_VERSION
3. `src/config_launcher.py` - CONST_APP_VERSION
4. `src/settings.py` - CONST_APP_VERSION
5. `src/www/settings.html` (行 141) - 版本顯示
6. `src/www/settings.html` (行 1075) - JavaScript 版本號時間戳記 ⭐

**格式**：
- Python 檔案：`CONST_APP_VERSION = "TicketsHunter (YYYY.MM.DD)"`
- HTML 版本顯示：`Tickets Hunter (YYYY.MM.DD)`
- JavaScript 時間戳記：`settings.js?v=YYYYMMDDHH` ⭐

### 4. 執行更新

請按照以下步驟執行更新：

1. **取得時間戳記**：
   ```bash
   TODAY=$(date +%Y.%m.%d)
   TIMESTAMP=$(date +%Y%m%d%H)
   echo "Version: $TODAY"
   echo "JS Timestamp: $TIMESTAMP"
   ```

2. **更新 Python 檔案版本號**（4 個檔案）：
   ```bash
   sed -i "s/CONST_APP_VERSION = "TicketsHunter ([0-9.]\+)"/CONST_APP_VERSION = "TicketsHunter ($TODAY)"/" src/chrome_tixcraft.py
   sed -i "s/CONST_APP_VERSION = "TicketsHunter ([0-9.]\+)"/CONST_APP_VERSION = "TicketsHunter ($TODAY)"/" src/nodriver_tixcraft.py
   sed -i "s/CONST_APP_VERSION = "TicketsHunter ([0-9.]\+)"/CONST_APP_VERSION = "TicketsHunter ($TODAY)"/" src/config_launcher.py
   sed -i "s/CONST_APP_VERSION = "TicketsHunter ([0-9.]\+)"/CONST_APP_VERSION = "TicketsHunter ($TODAY)"/" src/settings.py
   ```

3. **更新 settings.html**（2 個位置）：
   
   a. 版本顯示（行 141）：
   ```bash
   sed -i "s/Tickets Hunter ([0-9.]\+)/Tickets Hunter ($TODAY)/" src/www/settings.html
   ```
   
   b. JavaScript 時間戳記（行 1075）⭐：
   ```bash
   sed -i "s/settings.js?v=[0-9]\+/settings.js?v=$TIMESTAMP/" src/www/settings.html
   ```

### 5. 確認更新結果

更新完成後，再次檢查所有檔案：

```bash
echo ""
echo "=== 更新後版本號 ==="
grep "CONST_APP_VERSION" src/chrome_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/config_launcher.py | head -1
grep "CONST_APP_VERSION" src/settings.py | head -1
grep "版本.*Tickets Hunter" src/www/settings.html | head -1
grep "settings.js?v=" src/www/settings.html | head -1
```

### 6. Git 狀態檢查

檢查哪些檔案被修改：

```bash
echo ""
echo "=== Git 狀態 ==="
git status --short
```

## 📝 使用範例

### 範例 1：標準更新（使用今天日期與當前時間）

```
/gupdate
```

**預期結果**：
- 所有 4 個 Python 檔案的版本號更新為今天日期
- settings.html 的版本顯示更新為今天日期
- settings.html 的 JavaScript 時間戳記更新為當前時間（YYYYMMDDHH）
- 顯示更新前後的版本號對比
- 顯示 Git 狀態

### 範例 2：指定特定日期

```
/gupdate 2025.10.20
```

**預期結果**：
- 所有檔案的版本號更新為指定日期 (2025.10.20)
- JavaScript 時間戳記仍使用當前時間

## 🎯 更新邏輯

### Python 檔案 (.py)

**搜尋模式**：
```python
CONST_APP_VERSION = "TicketsHunter (YYYY.MM.DD)"
```

**替換為**：
```python
CONST_APP_VERSION = "TicketsHunter (當前日期)"
```

### settings.html

**行 141** - 網頁介面版本（注意：有空格）：
```html
<strong>版本</strong>：Tickets Hunter (YYYY.MM.DD)
```

**替換為**：
```html
<strong>版本</strong>：Tickets Hunter (當前日期)
```

**行 1075** - JavaScript 版本號時間戳記 ⭐：
```html
<script src="settings.js?v=YYYYMMDDHH"></script>
```

**替換為**：
```html
<script src="settings.js?v=當前時間戳記"></script>
```

**時間戳記範例**：
- 2025年11月11日 上午02:28 → `settings.js?v=2025111102`
- 2025年11月11日 下午15:00 → `settings.js?v=2025111115`
- 2025年11月11日 晚上23:45 → `settings.js?v=2025111123`


## ⚠️ 注意事項

1. **執行時機**：
   - 每次重大功能發布前
   - 每月定期維護更新
   - 修復重要 bug 後
   - 更新 JavaScript/CSS 檔案後（確保瀏覽器快取更新）

2. **版本號格式**：
   - 必須使用 `YYYY.MM.DD` 格式（例如：2025.10.18）
   - 不可使用其他格式（如 2025-10-18 或 20251018）

3. **時間戳記格式**：
   - 必須使用 `YYYYMMDDHH` 格式（例如：2025111102）
   - 24小時制（00-23）
   - 用於 JavaScript/CSS 檔案版本控制

4. **Git 提交**：
   - 更新版本號後，建議單獨建立一個 commit
   - Commit 訊息格式：`🔖 chore(release): update version to TicketsHunter (YYYY.MM.DD)`

5. **檢查清單**：
   - [ ] 確認所有 4 個 Python 檔案都已更新
   - [ ] 確認 settings.html 版本顯示已更新
   - [ ] 確認 settings.html JavaScript 時間戳記已更新
   - [ ] 驗證日期格式正確（YYYY.MM.DD）
   - [ ] 驗證時間戳記格式正確（YYYYMMDDHH）
   - [ ] 檢查 Git 狀態無誤
   - [ ] 建立版本更新 commit

## 📊 輸出範例

```
=== 當前版本號 ===
CONST_APP_VERSION = "TicketsHunter (2025.11.10)"
CONST_APP_VERSION = "TicketsHunter (2025.11.10)"
CONST_APP_VERSION = "TicketsHunter (2025.11.10)"
CONST_APP_VERSION = "TicketsHunter (2025.11.10)"
<strong>版本</strong>：Tickets Hunter (2025.11.10)
  <script src="settings.js?v=2025111023"></script>

Version: 2025.11.11
JS Timestamp: 2025111102

=== 更新後版本號 ===
CONST_APP_VERSION = "TicketsHunter (2025.11.11)"
CONST_APP_VERSION = "TicketsHunter (2025.11.11)"
CONST_APP_VERSION = "TicketsHunter (2025.11.11)"
CONST_APP_VERSION = "TicketsHunter (2025.11.11)"
<strong>版本</strong>：Tickets Hunter (2025.11.11)
  <script src="settings.js?v=2025111102"></script>

=== Git 狀態 ===
 M src/chrome_tixcraft.py
 M src/config_launcher.py
 M src/nodriver_tixcraft.py
 M src/settings.py
 M src/www/settings.html
```

## 🔗 相關指令

- `/gsave` - 提交更新到 Git
- `/gpush` - 推送到遠端倉庫
- `/gchange` - 自動生成 CHANGELOG

## 💡 工作流程建議

```bash
# 1. 更新版本號（包含 JavaScript 時間戳記）
/gupdate

# 2. 提交版本更新
/gsave

# 3. 推送到遠端（如需要）
/gpush
```

---
