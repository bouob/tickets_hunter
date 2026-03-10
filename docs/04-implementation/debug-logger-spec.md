# Debug Logger 統一規格書

**文件說明**：定義 DebugLogger 的時間戳格式、類別架構與全專案遷移規則（v3.1）
**最後更新**：2026-02-12

---

## 1. 需求摘要

### 1.1 問題

目前除錯訊息（`advanced.verbose` 啟用時）沒有時間戳，無法追蹤事件時間差異。全專案有 ~1300 處 `if show_debug_message: print(...)` 分散在各處，缺乏統一管理。

### 1.2 目標

建立統一的 `DebugLogger` 工具類，自動加時間戳 `[HH:MM:SS]`，漸進式替換全專案 debug print。

### 1.3 決策紀錄

| 項目 | 決策 | 原因 |
|------|------|------|
| 時間格式 | `[HH:MM:SS]` | 搶票場景秒級足夠，簡潔 |
| 替換範圍 | 僅受 `show_debug_message` 保護的 ~1300 處 | 無保護的 print 保持原樣 |
| 硬編碼處理 | 5 種模式全部統一：util.py 10 函數 + nodriver 11 參數 + 13 區域硬編碼 | 消除不一致 |
| 多行處理 | 每次 `debug.log()` 都加時間戳 | API 簡潔、每行可獨立追蹤 |
| 架構方案 | 方案 C：DebugLogger 類放 util.py | 不新增檔案、簡潔 API |
| **[v3.0] 設定分離** | `verbose` 和 `show_timestamp` 為兩個獨立開關 | 時間戳可用於所有輸出，不限 debug |
| **[v3.0] 全域時間戳** | `show_timestamp` 啟用時所有 print 都加時間戳 | 入口覆寫 print 實現，零改動 |

---

## 2. 現狀分析

### 2.1 數據統計

| 項目 | 數量 |
|------|------|
| 全專案 `print()` 總數 | ~2018 |
| `if show_debug_message:` 保護的 print | ~1300 |
| 無保護的 print（不在本次範圍） | ~600 |
| `nodriver_tixcraft.py` 中的 debug print | ~1268 |
| `util.py` 中的 debug print | ~35 |
| 帶前綴標籤的 print（如 `[KKTIX]`） | ~111 |
| 多行 print 區塊（2+ prints 同一 if） | 75 |
| 巢狀條件（業務邏輯 + debug 混合） | 56 |
| 條件組合（or/and 賦值） | 3 |
| **模式 2**：util.py True/False 配對（開發者切換） | 10 函數 |
| **模式 3**：函數參數預設值（`show_debug_message=True/False`） | 11 函數 |
| **模式 4**：nodriver 區域硬編碼 | 13 處 |
| 使用 `show_debug` 變數名（非 `show_debug_message`） | 2 函數 |
| print 多位置參數如 `print("key:", value)` | 82 |

### 2.2 現有賦值模式（5 種）

```python
# 模式 1：從 config 讀取（標準，最常見）
show_debug_message = util.get_debug_mode(config_dict)

# 模式 2：硬編碼 True/False 配對（util.py 開發者切換）
show_debug_message = True    # debug.
show_debug_message = False   # online

# 模式 3：函數參數預設值 + config 覆蓋（nodriver fami 系列）
async def nodriver_fami_login(tab, config_dict, show_debug_message=True):
    if config_dict["advanced"].get("verbose", False):
        show_debug_message = True

# 模式 4：函數內區域硬編碼（nodriver 各平台）
show_debug_message = False               # 靜默模式
show_debug_message = True                # 永遠開啟（開發中）
show_debug_message = False               # 從 config 讀取
if config_dict:
    show_debug_message = config_dict.get("advanced", {}).get("verbose", False)

# 模式 5：條件組合（3 處）
# A. Cloudflare bypass + 模式覆蓋 (行 389)
show_debug_message = (config_dict["advanced"]["verbose"] or
                     CLOUDFLARE_BYPASS_MODE == "debug")
if CLOUDFLARE_BYPASS_MODE == "auto":
    show_debug_message = False

# B. force_show_debug 參數 (行 7476)
show_debug_message = config_dict["advanced"].get("verbose", False) or force_show_debug

# C. 三重 AND (行 7529)
if show_debug_message and is_in_queue and force_show_debug:
```

### 2.3 硬編碼完整清單

#### 模式 2：util.py True/False 配對（10 處）

開發者的「手動開關」——開發時改 `True` 除錯，上線前改回 `False`。
實際效果：**永遠等於 False**（因為第二行覆蓋第一行）。

| # | 函數名 | 行號 | 設計意圖 |
|---|--------|------|----------|
| 1 | `guess_answer_list_from_multi_options` | 515-516 | 多選項猜答案 |
| 2 | `get_offical_hint_string_from_symbol` | 722-723 | 官方提示解析 |
| 3 | `guess_answer_list_from_hint` | 764-765 | 從提示猜答案 |
| 4 | `get_answer_list_by_question` | 1089-1090 | 題目解析 |
| 5 | `get_matched_blocks_by_keyword_item_set` | 1151-1152 | 關鍵字區塊配對 |
| 6 | `guess_tixcraft_question` | 1389-1390 | 拓元驗證碼猜測 |
| 7 | `kktix_get_web_datetime` | 1559-1560 | KKTIX 日期解析 |
| 8 | `get_answer_string_from_web_date` | 1616-1617 | 從網頁日期推答案 |
| 9 | `get_answer_string_from_web_time` | 1747-1748 | 從網頁時間推答案 |
| 10 | `get_answer_list_from_question_string` | 1834-1835 | 核心樞紐：題目字串解析 |

**特殊**：#5 `get_matched_blocks_by_keyword_item_set` 已有 `config_dict` 參數，且行 1154-1155 有 `if config_dict["advanced"]["verbose"]: show_debug_message = True` 邏輯，是唯一已正確讀取設定的函數。

#### 模式 3：nodriver 函數參數預設值（10 處）

函數簽名帶 `show_debug_message` 參數，內部又用 `config_dict` 覆蓋。
效果：**參數預設值被覆蓋，實際由 config 控制**。參數是冗餘的。

| # | 函數名 | 行號 | 預設值 | 有 config_dict |
|---|--------|------|--------|---------------|
| 1 | `nodriver_check_checkbox_enhanced` | 270 | `False` | 無（純參數控制） |
| 2 | `nodriver_kktix_check_ticket_page_status` | 2008 | `False` | 無（純參數控制） |
| 3 | `check_kktix_got_ticket` | 2515 | `False` | 有（但未覆蓋） |
| 4 | `nodriver_fami_login` | 8194 | `True` | 有（行 8209-8210 覆蓋） |
| 5 | `nodriver_fami_activity` | 8307 | `True` | 有（行 8323 覆蓋） |
| 6 | `nodriver_fami_verify` | 8366 | `True` | 有（行 8385 覆蓋） |
| 7 | `nodriver_fami_date_auto_select` | 8474 | `True` | 有（行 8491 覆蓋） |
| 8 | `nodriver_fami_area_auto_select` | 8665 | `True` | 有（行 8682 覆蓋） |
| 9 | `nodriver_fami_date_to_area` | 8819 | `True` | 有（行 8836 覆蓋） |
| 10 | `nodriver_fami_ticket_select` | 8896 | `True` | 有（行 8915 覆蓋） |
| 11 | `nodriver_fami_home_auto_select` | 9024 | `True` | 有（行 9040 覆蓋） |

**分類**：
- #1, #2：無 config_dict，純靠呼叫端傳參 → 改為接收 `config_dict` 或 `enabled`
- #3：有 config_dict 但未用於覆蓋 → 移除參數，改用 config
- #4-#11（fami 系列）：已有 config_dict 且會覆蓋 → 移除 `show_debug_message` 參數

#### 模式 4：nodriver 區域硬編碼（12 處）

函數內部直接寫死 `show_debug_message = True/False`。

| # | 函數名 | 行號 | 硬編碼值 | 設計意圖 | 轉換方式 |
|---|--------|------|----------|----------|----------|
| 1 | `nodriver_cloudflare_challenge` | 394 | `False` | auto 模式靜默 | 見模式 5-A |
| 2 | `nodriver_tixcraft_get_ocr_answer` | 5700 | `False` | OCR 靜默（效能考量） | `enabled=False` |
| 3 | `nodriver_kham_login` | 15020 | `True` | 開發中永遠開啟 | `config_dict` |
| 4 | `nodriver_hkticketing_login` | 21417 | `True` | 開發中永遠開啟 | `config_dict` |
| 5 | `nodriver_hkticketing_date_buy_button_press` | 21589 | `False` → config | 已正確讀取 config | 直接替換 |
| 6 | `nodriver_hkticketing_ticket_delivery_option` | 22262 | `False` → config | 已正確讀取 config | 直接替換 |
| 7 | `nodriver_hkticketing_next_button_press` | 22306 | `False` → config | 已正確讀取 config | 直接替換 |
| 8 | `nodriver_hkticketing_go_to_payment` | 22383 | `False` → config | 已正確讀取 config | 直接替換 |
| 9 | `nodriver_hkticketing_type02_clear_session` | 22465 | `False` → config | 已正確讀取 config | 直接替換 |
| 10 | `nodriver_hkticketing_traffic_overload` | 22531 | `False` → config | 已正確讀取 config | 直接替換 |
| 11 | `nodriver_hkticketing_dismiss_modal` | 22756 | `False` → config | 已正確讀取 config | 直接替換 |
| 12 | `nodriver_hkticketing_buy_button` | 22811 | `False` → config | 已正確讀取 config | 直接替換 |
| 13 | `nodriver_hkticketing_type02_next_step` | 23347 | `False` → config | 已正確讀取 config | 直接替換 |

**分類**：
- #2：刻意靜默（OCR 高頻呼叫）→ 保持 `enabled=False`
- #3, #4：永遠開啟（開發中功能）→ 改為從 config_dict 讀取
- #5-#13：已有正確 config 讀取邏輯 → 直接替換為 DebugLogger

### 2.4 前綴標籤清單

| 標籤 | 出現次數 | 用途 |
|------|----------|------|
| `[KKTIX]` / `[KKTIX AREA]` | 22+ | KKTIX 平台流程 |
| `[TICKETMASTER]` | 32+ | TicketMaster 平台 |
| `[CLOUDFLARE]` / `[CF]` | 11+ | Cloudflare 驗證 |
| `[TIXCRAFT OCR]` | 10+ | 拓元 OCR 驗證碼 |
| `[FAMI]` | 20+ | 全家票券 |
| `[DATE SELECT]` | 8+ | 日期選擇 |
| `[AREA SELECT]` | 2+ | 區域選擇 |
| `[TICKET SELECT]` | 2+ | 票種選擇 |
| `[MCP DEBUG]` | 2 | MCP 除錯 |
| `[TOUR IBON]` | 4+ | ibon 票券 |
| `[FUNONE]` | 4+ | FunOne 平台 |
| `[SOLD OUT]` | 1+ | 售罄偵測 |
| 無標籤（純 key-value） | ~800+ | 變數值輸出 |

---

## 3. 技術設計

### 3.1 DebugLogger 類

**位置**：`src/util.py`，在 `get_debug_mode()` 函數之後（約 1298 行）

```python
class DebugLogger:
    """
    Unified debug output. Timestamp controlled by show_timestamp setting.

    Behaves like print() for multiple arguments (space-joined, same line).
    DebugLogger 本身不加時間戳，時間戳由 show_timestamp + builtins.print 覆寫統一控制。

    Usage:
        debug = DebugLogger(config_dict)
        debug.log("[KKTIX] Starting process")
        debug.log("[KKTIX] key:", value)   # same line: [KKTIX] key: value
    """

    def __init__(self, config_dict=None, enabled=None):
        if enabled is not None:
            self.enabled = enabled
        elif config_dict:
            self.enabled = get_debug_mode(config_dict)
        else:
            self.enabled = False

    def log(self, *args):
        if not self.enabled or not args:
            return
        text = " ".join(str(a) for a in args)
        print(text)


def create_debug_logger(config_dict=None, enabled=None):
    """Create DebugLogger instance."""
    return DebugLogger(config_dict, enabled)
```

### 3.2 API 設計

| 方法 | 用途 | 範例 |
|------|------|------|
| `DebugLogger(config_dict)` | 建構子 | `debug = DebugLogger(config_dict)` |
| `DebugLogger(enabled=True)` | 強制啟用 | `debug = DebugLogger(enabled=cf_debug)` |
| `debug.log(*args)` | 輸出（加時間戳，同 print 行為） | `debug.log("[TAG] msg")` |
| `debug.log("key:", val)` | 多參數空格串接（同 print） | `debug.log("count:", 5)` |
| `create_debug_logger(config_dict)` | 便利建構函數 | `debug = util.create_debug_logger(config_dict)` |

### 3.3 關鍵 API 決策

> **[v2.0 修正] `log()` 多參數行為 = print() 行為**
>
> 原始設計：`log(msg1, msg2)` → 多行輸出（第一行有時間戳，後續無）
> 修正後：`log(msg1, msg2)` → 空格串接同一行（與 `print(msg1, msg2)` 一致）
>
> **原因**：專案有 82 處 `print("label:", value)` 格式的 debug 輸出。
> 如果 `log()` 把多參數當多行，這 82 處全部會壞掉。
> 改用 `" ".join()` 後，`print("key:", val)` → `debug.log("key:", val)` 可無痛替換。

> **[v2.0 修正] 多行 print 區塊處理方式**
>
> 原始設計：`debug.log(line1, line2, line3)` 只在第一行加時間戳
> 修正後：每個 `debug.log()` 獨立，各自有時間戳
>
> ```python
> # 多行 print 區塊替換為多次 debug.log() 呼叫
> debug.log(f"[KKTIX AREA] ========================================")
> debug.log(f"[KKTIX AREA] Match Summary:")
> debug.log(f"[KKTIX AREA]   Total: {total_checked}")
> ```
> 每行都有時間戳，更利於除錯追蹤。

### 3.4 輸出格式

```
# show_timestamp=true 時的輸出（所有 print 都加時間戳）：
[14:23:45] [KKTIX] Starting process
[14:23:45] [KKTIX] Ticket selected: A1 (keyword match)
[14:23:46] [KKTIX AREA] ========================================
[14:23:46] [KKTIX AREA] Match Summary:
[14:23:46] [KKTIX AREA]   Total ticket types checked: 5
[14:23:46] key: value
[14:23:47] [CLOUDFLARE] Starting challenge...

# show_timestamp=false 時的輸出（無時間戳）：
[KKTIX] Starting process
[KKTIX] Ticket selected: A1 (keyword match)
[KKTIX AREA] Match Summary:
key: value
```

---

## 4. 替換模式對照

### 4.1 標準單行 print（~910 處）

```python
# 替換前
show_debug_message = util.get_debug_mode(config_dict)
if show_debug_message:
    print("[KKTIX] No price list found")

# 替換後
debug = util.create_debug_logger(config_dict)
debug.log("[KKTIX] No price list found")
```

### 4.2 多位置參數 print（82 處）

```python
# 替換前
if show_debug_message:
    print("matched pattern:", matched_pattern)

# 替換後（行為完全一致，" ".join 處理）
debug.log("matched pattern:", matched_pattern)
```

### 4.3 多行 print 區塊（75 處）

```python
# 替換前
if show_debug_message:
    print(f"[KKTIX AREA] ========================================")
    print(f"[KKTIX AREA] Match Summary:")
    print(f"[KKTIX AREA]   Total: {total_checked}")

# 替換後（每行獨立呼叫，各自有時間戳）
debug.log(f"[KKTIX AREA] ========================================")
debug.log(f"[KKTIX AREA] Match Summary:")
debug.log(f"[KKTIX AREA]   Total: {total_checked}")
```

### 4.4 巢狀條件（56 處）

```python
# 替換前
if is_ticket_number_assigned and show_debug_message:
    print("KKTIX ticket number completed")

# 替換後（業務條件保留，debug 開關由 logger 處理）
if is_ticket_number_assigned:
    debug.log("KKTIX ticket number completed")
```

### 4.5 Cloudflare 條件組合（3 處）

```python
# 替換前
show_debug_message = (config_dict["advanced"]["verbose"] or
                     CLOUDFLARE_BYPASS_MODE == "debug")
if CLOUDFLARE_BYPASS_MODE == "auto":
    show_debug_message = False

# 替換後（使用 enabled 參數）
cf_debug = (config_dict.get("advanced", {}).get("verbose", False) or
           CLOUDFLARE_BYPASS_MODE == "debug")
if CLOUDFLARE_BYPASS_MODE == "auto":
    cf_debug = False
debug = util.create_debug_logger(enabled=cf_debug)
```

### 4.6 force_show_debug 參數

```python
# 替換前
show_debug_message = config_dict["advanced"].get("verbose", False) or force_show_debug

# 替換後
debug = util.create_debug_logger(
    enabled=(config_dict.get("advanced", {}).get("verbose", False) or force_show_debug)
)
```

### 4.7 模式 2：util.py 硬編碼 True/False 配對（10 處）

```python
# 替換前（10 個函數，全部相同模式）
def guess_answer_list_from_multi_options(tmp_text):
    show_debug_message = True    # debug.
    show_debug_message = False   # online
    if show_debug_message:
        print("matched pattern:", matched_pattern)

# 替換後（新增 config_dict 參數，由設定檔控制）
def guess_answer_list_from_multi_options(tmp_text, config_dict=None):
    debug = create_debug_logger(config_dict)
    debug.log("matched pattern:", matched_pattern)
```

**特殊：`get_matched_blocks_by_keyword_item_set`（行 1150）**

```python
# 替換前（已有 config_dict，有 3 行賦值邏輯）
def get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, ...):
    show_debug_message = True    # debug.
    show_debug_message = False   # online
    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

# 替換後（已有 config_dict，直接用）
def get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, ...):
    debug = create_debug_logger(config_dict)
```

### 4.8 模式 3：nodriver 函數參數預設值（11 處）

**4.8a Fami 系列（8 處）— 移除 show_debug_message 參數**

```python
# 替換前（8 個 fami 函數，全部相同模式）
async def nodriver_fami_login(tab, config_dict, show_debug_message=True):
    if config_dict["advanced"].get("verbose", False):
        show_debug_message = True
    if show_debug_message:
        print("[FAMI LOGIN] Starting...")

# 替換後（移除參數，由 config_dict 統一控制）
async def nodriver_fami_login(tab, config_dict):
    debug = util.create_debug_logger(config_dict)
    debug.log("[FAMI LOGIN] Starting...")
```

> **注意**：需同步修改所有呼叫端，移除傳入的 `show_debug_message` 參數。

**4.8b 無 config_dict 的函數（2 處）— 改接收 config_dict**

```python
# 替換前
async def nodriver_check_checkbox_enhanced(tab, select_query, show_debug_message=False):
    if show_debug_message:
        print(f"Checking checkbox: {select_query}")

# 替換後（加 config_dict 或保留 enabled 參數）
async def nodriver_check_checkbox_enhanced(tab, select_query, config_dict=None):
    debug = util.create_debug_logger(config_dict)
    debug.log(f"Checking checkbox: {select_query}")
```

**4.8c 有 config_dict 但未覆蓋的函數（1 處）**

```python
# 替換前
def check_kktix_got_ticket(url, config_dict, show_debug_message=False):
    ...

# 替換後（移除參數，改用 config_dict）
def check_kktix_got_ticket(url, config_dict):
    debug = util.create_debug_logger(config_dict)
```

### 4.9 模式 4：nodriver 區域硬編碼（13 處）

**4.9a 已有 config 讀取邏輯（9 處 hkticketing）— 直接替換**

```python
# 替換前（hkticketing 系列，9 個函數相同模式）
async def nodriver_hkticketing_date_buy_button_press(tab, config_dict=None):
    show_debug_message = False
    if config_dict:
        show_debug_message = config_dict.get("advanced", {}).get("verbose", False)
    if show_debug_message:
        print("[HKTICKETING] ...")

# 替換後（3 行賦值邏輯 → 1 行）
async def nodriver_hkticketing_date_buy_button_press(tab, config_dict=None):
    debug = util.create_debug_logger(config_dict)
    debug.log("[HKTICKETING] ...")
```

**4.9b 永遠開啟（2 處：kham_login, hkticketing_login）— 改用 config**

```python
# 替換前（kham_login, 行 15020）
async def nodriver_kham_login(tab, account, password, ocr=None):
    show_debug_message = True    # 永遠開啟，無 config

# 替換後（需由呼叫端傳入 config_dict）
async def nodriver_kham_login(tab, account, password, config_dict=None, ocr=None):
    debug = util.create_debug_logger(config_dict)
```

> **注意**：`nodriver_kham_login` 和 `nodriver_hkticketing_login` 目前函數簽名沒有 `config_dict`，需新增參數並更新呼叫端。

**4.9c 刻意靜默（1 處：OCR）— 保持 enabled=False**

```python
# 替換前（nodriver_tixcraft_get_ocr_answer, 行 5700）
async def nodriver_tixcraft_get_ocr_answer(...):
    show_debug_message = False    # OCR 高頻呼叫，永遠靜默

# 替換後（明確標記為刻意靜默）
async def nodriver_tixcraft_get_ocr_answer(...):
    debug = util.create_debug_logger(enabled=False)  # OCR: intentionally silent
```

### 4.10 show_debug 變數名差異（2 函數）

```python
# 替換前（detect_cloudflare_challenge, 行 330）
async def detect_cloudflare_challenge(tab, show_debug=False):
    if show_debug:
        print(f"Cloudflare detection error: {exc}")

# 替換後
async def detect_cloudflare_challenge(tab, show_debug=False):
    debug = create_debug_logger(enabled=show_debug)
    debug.log(f"Cloudflare detection error: {exc}")
```

---

## 5. 影響檔案與呼叫鏈

### 5.1 修改檔案

| 檔案 | 改動類型 | 預估改動量 |
|------|----------|-----------|
| `src/util.py` | 新增 DebugLogger 類 + 改造 10 函數 | +40 行新增、~35 處替換 |
| `src/nodriver_tixcraft.py` | 替換 debug print | ~1268 處替換 |

### 5.2 util.py 需改造的函數（含呼叫鏈分析）

| 函數名 | 行號 | 改動 | 呼叫端 | 風險 |
|--------|------|------|--------|------|
| `guess_answer_list_from_multi_options` | 514 | 加 `config_dict` | util 內部 1 處 | 低 |
| `get_offical_hint_string_from_symbol` | 722 | 加 `config_dict` | util 內部 2 處 | 低 |
| `guess_answer_list_from_hint` | 764 | 加 `config_dict` | util 內部 2 處 | 低 |
| `get_answer_list_by_question` | 1089 | 加 `config_dict` | util 內部 1 處 | 中 |
| `get_matched_blocks_by_keyword_item_set` | 1150 | **已有 config_dict** | 不需動 | 無 |
| `guess_tixcraft_question` | 1389 | 加 `config_dict` | nodriver 1 處（有 config） | 低 |
| `kktix_get_web_datetime` | 1559 | 加 `config_dict` | util 內部 2 處 | 低 |
| `get_answer_string_from_web_date` | 1616 | 加 `config_dict` | util 內部 1 處 | 中 |

### 5.3 額外需修改的函數（呼叫鏈分析發現）

| 函數名 | 行號 | 原因 | 風險 |
|--------|------|------|------|
| `get_answer_list_from_question_string` | ~1833 | **核心樞紐**：被多個外部函數呼叫，需加 `config_dict` | 中 |
| `get_answer_string_from_web_time` | ~1746 | 與 `get_answer_string_from_web_date` 對稱 | 低 |

### 5.4 呼叫鏈圖

```
nodriver_tixcraft.py                    util.py
========================               ========================================

nodriver_kktix_reg_captcha()   ----->  get_answer_list_from_question_string() [*樞紐]
  (config_dict: OK)                      |-- get_answer_string_from_web_date()
                                         |     '-- kktix_get_web_datetime()
nodriver_ibon_verification_    ----->     |-- get_answer_string_from_web_time()
  question()                             |     '-- kktix_get_web_datetime()
  (config_dict: OK)                      '-- get_answer_list_by_question()
                                               |-- guess_answer_list_from_multi_options()
nodriver_tixcraft_input_       ----->  guess_tixcraft_question()
  check_code()                           '-- get_answer_list_from_question_string()
  (config_dict: OK)                           '-- (同上)

                                       get_matched_blocks_by_keyword()
                                         '-- get_matched_blocks_by_keyword_item_set()
                                              (已有 config_dict: OK)
```

**關鍵結論**：所有外部呼叫端（nodriver_tixcraft.py 中）都已有 `config_dict` 可傳遞。風險可控。

### 5.5 建議改動順序（由內而外）

1. 底層：`guess_answer_list_from_multi_options`, `get_offical_hint_string_from_symbol`, `kktix_get_web_datetime`
2. 中間：`guess_answer_list_from_hint`, `get_answer_list_by_question`, `get_answer_string_from_web_date`, `get_answer_string_from_web_time`
3. 樞紐：`get_answer_list_from_question_string`
4. 頂層：`guess_tixcraft_question`
5. 外部呼叫端：更新 nodriver_tixcraft.py 中 3 處呼叫

---

## 6. 特殊模式處理策略

### 6.1 巢狀條件（56 處）

業務邏輯保留在外層 if，debug 開關移入 logger 內部。

```python
# 替換前：if 業務條件 and show_debug_message:
# 替換後：if 業務條件: debug.log(...)
```

### 6.2 條件組合（3 處）

使用 `enabled` 參數建立 DebugLogger。

### 6.3 show_debug 變數名（2 函數）

- `detect_cloudflare_challenge(tab, show_debug=False)` → 使用 `enabled=show_debug`
- `debug_kktix_page_state(tab, show_debug=True)` → 使用 `enabled=show_debug`

### 6.4 獨立 debug 體系（不納入 DebugLogger）

| 變數 | 位置 | 原因 |
|------|------|------|
| `CLOUDFLARE_BYPASS_MODE` | 行 80 | 模組級常數，控制 Cloudflare 策略 |
| `mcp_debug_enabled` | 行 21061 | MCP 專屬開關，不走 verbose |

### 6.5 非標準 print 參數

**無。** 所有 debug print 都使用 print 預設參數（無 `end=`, `flush=`, `sep=`）。

---

## 7. 實施計畫

### 7.1 Phase 1：基礎建設（PR #1）

**範圍**：
- 在 `util.py` 新增 `DebugLogger` 類和 `create_debug_logger()` 函數
- 改造 `util.py` 中 10 個函數（8 原始 + 2 呼叫鏈發現）
- 追蹤呼叫端，補傳 `config_dict`

**風險**：中（函數簽名變更需追蹤所有呼叫端）

**驗證**：
- 執行快速測試確認啟動無錯
- 確認 `verbose: true` 時有時間戳輸出

### 7.2 Phase 2：局部試點（PR #2）

**範圍**：
- 選定 1 個函數（如 `nodriver_kktix_area_auto_select`）完整替換
- 驗證替換模式的正確性

**風險**：低（單一函數隔離）

### 7.3 Phase 3：分批替換（PR #3~#6）

**策略**：按平台分批

| 批次 | 平台 | 預估處數 |
|------|------|----------|
| 3.1 | KKTIX | ~400 |
| 3.2 | TixCraft | ~300 |
| 3.3 | TicketPlus | ~250 |
| 3.4 | 其他（iBon、Cityline、FamiTicket 等） | ~318 |

**每批驗證**：執行快速測試 + 檢查 `.temp/logs.txt` 格式

### 7.4 Phase 4：清理

- 移除殘留的 `show_debug_message` 變數宣告
- 更新文件
- 關閉 Issue #211

---

## 8. 風險評估

| 風險 | 機率 | 影響 | 緩解 |
|------|------|------|------|
| util.py 函數簽名變更導致呼叫端漏改 | 中 | 高（RuntimeError） | 預設 `config_dict=None` + 逐一追蹤 |
| `log()` 多參數行為與 `print()` 不一致 | **已解決** | **已解決** | v2.0 改用 `" ".join()` |
| 多行 print 替換格式錯誤 | 低 | 低（顯示問題） | 每行獨立 `debug.log()`，無格式風險 |
| 大批量替換引入 typo | 低 | 中 | 分批 commit + 每批測試 |
| 效能影響 | 極低 | 低 | `datetime.now()` ~1-2us，DebugLogger init ~1us |
| 條件組合場景遺漏 | 低 | 中 | 已完整列出 3 處 + 56 處巢狀條件 |
| 巢狀條件替換邏輯錯誤 | 低 | 中 | 統一策略：業務條件留外層，debug 留 logger |

---

## 9. 向後相容

- 新舊模式可共存：`debug.log()` 和 `if show_debug_message: print()` 可同時存在
- `get_debug_mode()` 函數保留不變
- `show_debug_message` 變數在未替換的函數中繼續使用
- 分階段替換，任何 PR 可獨立回滾

---

## 10. [v3.0] 新設定：`show_timestamp`（顯示時間戳記）

### 10.1 設計概念

將「時間戳」和「verbose」分成兩個獨立開關：

| 設定 | 功能 | 影響範圍 |
|------|------|----------|
| `verbose` | 是否輸出詳細除錯訊息 | 僅 DebugLogger 控制的 ~1300 處 |
| `show_timestamp`（新） | 是否在**所有**輸出前加時間戳 | 全部 print 輸出（~2018 處） |

**組合效果**：

| verbose | show_timestamp | 結果 |
|---------|---------------|------|
| false | false | 只有正常輸出，無時間戳 |
| false | true | 正常輸出 + 時間戳 |
| true | false | 正常 + 除錯輸出，無時間戳 |
| true | true | 正常 + 除錯輸出 + 全部有時間戳 |

### 10.2 settings.json

```json
"advanced": {
    "verbose": true,
    "show_timestamp": false,
    ...
}
```

### 10.3 設定層改動

| 檔案 | 改動 | 量 |
|------|------|-----|
| `src/settings.py` | 新增預設值 `config_dict["advanced"]["show_timestamp"] = False` | +1 行 |
| `src/settings.json` | 新增 `"show_timestamp": false` | +1 行 |
| `src/www/settings.html` | 新增 checkbox（在 verbose 之後） | +8 行 |
| `src/www/settings.js` | 變數宣告 + load + save | +3 行 |

### 10.4 全域時間戳實作方式

**方案：在 `nodriver_tixcraft.py` 入口覆寫 `builtins.print`**

```python
# nodriver_tixcraft.py 主入口，在 UTF-8 設定之後
import builtins
_original_print = builtins.print

def _timestamped_print(*args, **kwargs):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    _original_print(timestamp, *args, **kwargs)

# 根據設定決定是否啟用
if config_dict.get("advanced", {}).get("show_timestamp", False):
    builtins.print = _timestamped_print
```

**優點**：
- 零改動現有 ~2018 處 print
- 只影響搶票引擎，不影響 settings.py 等管理介面
- 可隨時開關

**DebugLogger 整合**：
- `debug.log()` 內部呼叫 `print()`
- DebugLogger **不自行加時間戳**，時間戳完全由 `show_timestamp` + `builtins.print` 覆寫統一控制
- `show_timestamp` 開啟時：所有輸出（一般 + 除錯）都有時間戳
- `show_timestamp` 關閉時：所有輸出都沒有時間戳

```python
class DebugLogger:
    def __init__(self, config_dict=None, enabled=None):
        if enabled is not None:
            self.enabled = enabled
        elif config_dict:
            self.enabled = get_debug_mode(config_dict)
        else:
            self.enabled = False

    def log(self, *args):
        if not self.enabled or not args:
            return
        text = " ".join(str(a) for a in args)
        # 時間戳由 show_timestamp 的 builtins.print 覆寫統一處理
        print(text)
```

### 10.5 UI 名稱對照

| 技術名稱 | UI 名稱 |
|----------|---------|
| `advanced.verbose` | 輸出除錯訊息 |
| `advanced.show_timestamp` | 顯示時間戳記 |

---

## 11. [v3.0] 文件同步計畫

### 11.1 目的

確保 DebugLogger 規範被未來開發者遵守。多層防護策略：

| 層級 | 作用 |
|------|------|
| L1 | 專案開發規範（每次 session 自動載入，最高強制力） |
| L2 | coding_templates.md（寫新功能時的範本來源） |
| L3 | 開發工作流程（任務觸發時載入） |
| L4 | Hook（可選，最後安全網，偵測舊模式新增） |

### 11.2 開發規範更新

Debug 輸出規範：

| 規範 | 說明 |
|------|------|
| 統一使用 DebugLogger | `debug = util.create_debug_logger(config_dict)` + `debug.log(...)` |
| 禁止舊模式 | 禁止 `if show_debug_message: print(...)` |
| 規格書 | `docs/04-implementation/debug-logger-spec.md` |

### 11.3 需更新的文件清單

#### P0（Phase 1 同步更新）

| 文件 | 更新內容 |
|------|----------|
| `docs/02-development/coding_templates.md` | **全部範本**替換為 DebugLogger（~15 區塊） |
| `docs/02-development/development_guide.md` | 必要元素 + 實作範例改為 DebugLogger |
| `docs/02-development/structure.md` | 函數索引新增 `DebugLogger` / `create_debug_logger` |

#### P1（Phase 2-3 同步更新）

| 文件 | 更新內容 |
|------|----------|
| 開發工作流程文件 | 日誌輸出範例更新 |

#### P2（Phase 4 清理同步）

| 文件 | 更新內容 |
|------|----------|
| `docs/03-mechanisms/` 14 個文件 | 範例程式碼中的 print 更新 |
| `docs/05-validation/spec-validation-matrix.md` | FR-059 描述更新 |
| `docs/03-mechanisms/README.md` | 共用函式表格新增 DebugLogger |

---

## 12. 不在本次範圍

| 項目 | 原因 |
|------|------|
| Python logging 模組整合 | 過度設計，目前 print + 重定向足夠 |
| Log level 分層（DEBUG/INFO/WARNING） | 目前只需 on/off，保持簡單 |
| 日誌檔案輪轉 | 依賴外部 shell 重定向，不在程式內處理 |
| 新增 `debug_logger.py` 獨立模組 | 不新增檔案，放 util.py 即可 |
| `mcp_debug_enabled` 整合 | 獨立體系，不納入 DebugLogger |

---

## 附錄 A：Team Review 發現摘要（Round 1）

### A.1 call-chain-analyzer 發現

- `get_matched_blocks_by_keyword_item_set` 已有 config_dict，不需改動
- 核心樞紐函數 `get_answer_list_from_question_string` 不在原始清單中但必須一起改
- 所有外部呼叫端都已有 config_dict 可傳遞

### A.2 special-pattern-finder 發現

- 56 處巢狀條件（業務 + debug 混合），需統一替換策略
- 75 處多行 print 區塊（最大 10+ prints）
- 3 處條件組合賦值
- 2 個函數使用 `show_debug` 而非 `show_debug_message`
- 0 處非標準 print 參數（好消息）
- `mcp_debug_enabled` 和 `CLOUDFLARE_BYPASS_MODE` 為獨立體系

### A.3 api-edge-case-reviewer 發現

- **重大修正**：原始 `log()` 多參數行為與 `print()` 不一致，82 處受影響
- 修正為 `" ".join(str(a) for a in args)` 後問題解決
- DebugLogger 實例建立成本極低（< 1us），高頻函數不需快取
- `print(exc)` 輸出正常，`str(exc)` 自動處理
- 迴圈中的 debug print 效能影響可忽略

---

## 附錄 B：Team Review 發現摘要（Round 2 - 文件/設定/Skill）

### B.1 docs-scanner 發現

- **coding_templates.md 是最關鍵文件**：~15 個範本區塊全部使用舊模式，是未來開發者的複製貼上來源
- 共 ~25 個文件需要更新（3 高、6 中、5 低、14 機制文件延後）
- 不建議新增獨立文件，DebugLogger 規範應整合到現有文件

### B.2 settings-analyzer 發現

- `show_timestamp` 設定層改動極小：settings.py +1 行、settings.json +1 行、HTML +8 行、JS +3 行
- 全域時間戳建議在 `nodriver_tixcraft.py` 入口覆寫 `builtins.print`（零改動現有 print）
- DebugLogger 需處理與全域時間戳的重複問題（檢查 `show_timestamp` 避免雙重時間戳）
- Tornado handler 無需改動（通用 JSON 存取）

### B.3 skill-analyzer 發現

- **4 層防護策略**：開發規範 → coding_templates → 開發工作流程 → Hook
- 開發規範需新增 Debug 輸出標準
- 開發工作流程的日誌範例需替換
