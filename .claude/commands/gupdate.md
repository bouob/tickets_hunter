---
description: "更新專案版本日期"
allowed-tools: ["Bash"]
model: haiku
---

自動更新所有檔案中的 `CONST_APP_VERSION` 為當前日期。

---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---


## 📋 執行步驟

### 1. 取得當前日期

取得系統當前日期並格式化為 `YYYY.MM.DD` 格式：

```bash
# Windows (PowerShell)
$TODAY = Get-Date -Format "yyyy.MM.dd"
echo "Today's date: $TODAY"

# 或使用 Git Bash / Linux
TODAY=$(date +%Y.%m.%d)
echo "Today's date: $TODAY"
```

### 2. 檢查當前版本號

顯示所有檔案中的當前版本號：

```bash
cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter"

echo "=== 當前版本號 ==="
grep "CONST_APP_VERSION" src/chrome_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/nodriver_tixcraft.py | head -1
grep "CONST_APP_VERSION" src/config_launcher.py | head -1
grep "CONST_APP_VERSION" src/settings.py | head -1
grep "版本.*TicketsHunter" README.md | head -1
grep "版本.*Tickets Hunter" src/www/settings.html | head -1
grep "^版本：" build_scripts/README_Release.txt
grep "^最後更新：" build_scripts/README_Release.txt
```

### 3. 更新所有檔案

使用當前日期更新所有 7 個檔案：

**目標檔案清單**：
1. `src/chrome_tixcraft.py` (行 47)
2. `src/nodriver_tixcraft.py` (行 36)
3. `src/config_launcher.py` (行 27)
4. `src/settings.py` (行 42)
5. `README.md` (行 5, 484)
6. `src/www/settings.html` (行 79)
7. `build_scripts/README_Release.txt` (行 230-231)

**格式**：`CONST_APP_VERSION = "TicketsHunter (YYYY.MM.DD)"`

### 4. 執行更新

請按照以下步驟執行更新：

1. **讀取檔案**：使用 Read tool 讀取需要更新的檔案區段
2. **執行更新**：使用 Edit tool 更新版本號
3. **驗證更新**：檢查所有檔案是否更新成功

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
grep "^版本：" build_scripts/README_Release.txt
grep "^最後更新：" build_scripts/README_Release.txt
```

### 6. Git 狀態檢查

檢查哪些檔案被修改：

```bash
echo ""
echo "=== Git 狀態 ==="
git status --short
```

## 📝 使用範例

### 範例 1：標準更新（使用今天日期）

```
/gupdate
```

**預期結果**：
- 所有 7 個檔案的版本號更新為今天日期
- 顯示更新前後的版本號對比
- 顯示 Git 狀態

### 範例 2：指定特定日期

```
/gupdate 2025.10.20
```

**預期結果**：
- 所有 7 個檔案的版本號更新為指定日期 (2025.10.20)

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
Tickets Hunter (YYYY.MM.DD)
```

**搜尋模式**：
```html
<strong>版本</strong>：Tickets Hunter (YYYY.MM.DD)
```

**替換為**：
```html
<strong>版本</strong>：Tickets Hunter (當前日期)
```

### README_Release.txt

**行 230** - 版本號：
```
版本：YYYY.MM.DD
```

**行 231** - 更新日期：
```
最後更新：YYYY-MM-DD
```

**注意**：此檔案的日期格式與其他檔案不同
- 版本號 (line 230): `2025.11.03` (點號分隔)
- 更新日期 (line 231): `2025-11-03` (連字號分隔，ISO 8601 格式)

## ⚠️ 注意事項

1. **執行時機**：
   - 每次重大功能發布前
   - 每月定期維護更新
   - 修復重要 bug 後

2. **版本號格式**：
   - 必須使用 `YYYY.MM.DD` 格式（例如：2025.10.18）
   - 不可使用其他格式（如 2025-10-18 或 20251018）

3. **Git 提交**：
   - 更新版本號後，建議單獨建立一個 commit
   - Commit 訊息格式：`🔖 Update version to TicketsHunter (YYYY.MM.DD)`

4. **檢查清單**：
   - [ ] 確認所有 7 個檔案都已更新
   - [ ] 驗證日期格式正確（注意 README_Release.txt 使用連字號）
   - [ ] 檢查 Git 狀態無誤
   - [ ] 建立版本更新 commit

## 📊 輸出範例

```
=== 當前版本號 ===
CONST_APP_VERSION = "TicketsHunter (2025.10.17)"
CONST_APP_VERSION = "TicketsHunter (2025.10.17)"
CONST_APP_VERSION = "TicketsHunter (2025.10.17)"
CONST_APP_VERSION = "TicketsHunter (2025.10.17)"
**⚡ 版本**：TicketsHunter (2025.10.17)
<strong>版本</strong>：Tickets Hunter (2025.10.17)
版本：2025.10.17
最後更新：2025-10-17

=== 開始更新 ===
✓ 已更新 src/chrome_tixcraft.py
✓ 已更新 src/nodriver_tixcraft.py
✓ 已更新 src/config_launcher.py
✓ 已更新 src/settings.py
✓ 已更新 README.md
✓ 已更新 src/www/settings.html
✓ 已更新 build_scripts/README_Release.txt

=== 更新後版本號 ===
CONST_APP_VERSION = "TicketsHunter (2025.10.18)"
CONST_APP_VERSION = "TicketsHunter (2025.10.18)"
CONST_APP_VERSION = "TicketsHunter (2025.10.18)"
CONST_APP_VERSION = "TicketsHunter (2025.10.18)"
**⚡ 版本**：TicketsHunter (2025.10.18)
<strong>版本</strong>：Tickets Hunter (2025.10.18)
版本：2025.10.18
最後更新：2025-10-18

=== Git 狀態 ===
 M README.md
 M build_scripts/README_Release.txt
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
# 1. 更新版本號
/gupdate

# 2. 提交版本更新
/gsave

# 3. 推送到遠端（如需要）
/gpush
```

---
