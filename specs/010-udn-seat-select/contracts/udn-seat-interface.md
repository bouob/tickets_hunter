# 函數介面契約：UDN 座位選擇

**分支**：`010-udn-seat-select` | **日期**：2025-12-17

## 概述

定義 UDN 座位選擇功能的函數介面契約，確保實作符合設計規範。

---

## 核心函數

### 1. nodriver_udn_seat_auto_select

**用途**：UDN 座位自動選擇（複用 KHAM 邏輯）

```python
async def nodriver_udn_seat_auto_select(
    tab: nodriver.Tab,
    config_dict: dict,
    ticket_number: int,
    domain_name: str
) -> tuple[bool, int]:
    """
    自動選擇 UDN 座位圖中的座位。

    Args:
        tab: NoDriver 瀏覽器分頁
        config_dict: 設定字典
        ticket_number: 需要選擇的座位數量
        domain_name: 網域名稱（用於日誌識別）

    Returns:
        tuple[bool, int]: (是否成功, 已選擇的座位數量)

    Raises:
        無（錯誤透過返回值表示）

    Example:
        is_success, selected_count = await nodriver_udn_seat_auto_select(
            tab, config_dict, 2, "tickets.udnfunlife.com"
        )
        if is_success and selected_count == 2:
            print("[SUCCESS] 座位選擇完成")

    Contract:
        - 若 ticket_number <= 0，返回 (False, 0)
        - 若無可用座位，返回 (False, 0)
        - 若可用座位不足，返回 (True, 實際選擇數量)
        - 優先選擇連續座位（相鄰 DOM 索引）
        - 遵循舞台方向智慧選座策略
    """
```

---

### 2. nodriver_kham_date_auto_select（修改）

**用途**：日期/場次自動選擇，整合 Feature 003 遞補機制

```python
async def nodriver_kham_date_auto_select(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    自動選擇場次日期，支援 Early Return Pattern 和 Conditional Fallback。

    Args:
        tab: NoDriver 瀏覽器分頁
        config_dict: 設定字典，需包含：
            - date_keyword: 日期關鍵字
            - date_auto_fallback: 遞補開關
            - auto_select_mode: 選擇模式
            - pass_date_is_sold_out: 跳過售罄

    Returns:
        bool: 是否成功選擇場次

    Contract:
        - Early Return: 按關鍵字優先級順序嘗試，第一個成功即停止
        - AND 邏輯: 空格分隔的關鍵字必須全部匹配
        - OR 邏輯: 逗號分隔的關鍵字任一匹配即可
        - Fallback (date_auto_fallback=True):
            - 所有關鍵字失敗時，使用 auto_select_mode 選擇
        - Strict Mode (date_auto_fallback=False):
            - 所有關鍵字失敗時，返回 False 等待手動介入
        - 售罄場次自動跳過
    """
```

---

### 3. nodriver_kham_area_auto_select（修改）

**用途**：區域/票區自動選擇，整合 Feature 003 遞補機制

```python
async def nodriver_kham_area_auto_select(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    自動選擇票區，支援 Early Return Pattern、Conditional Fallback 和 keyword_exclude。

    Args:
        tab: NoDriver 瀏覽器分頁
        config_dict: 設定字典，需包含：
            - area_keyword: 區域關鍵字
            - area_auto_fallback: 遞補開關
            - keyword_exclude: 排除關鍵字
            - auto_select_mode: 選擇模式

    Returns:
        bool: 是否成功選擇票區

    Contract:
        - 排除過濾: keyword_exclude 先於關鍵字匹配執行
        - Early Return: 按關鍵字優先級順序嘗試，第一個成功即停止
        - AND 邏輯: 空格分隔的關鍵字必須全部匹配
        - OR 邏輯: 逗號分隔的關鍵字任一匹配即可
        - Fallback (area_auto_fallback=True):
            - 所有關鍵字失敗時，使用 auto_select_mode 選擇
        - Strict Mode (area_auto_fallback=False):
            - 所有關鍵字失敗時，返回 False 等待手動介入
        - 售罄票區（Soldout class）自動跳過
    """
```

---

### 4. nodriver_kham_main（修改）

**用途**：KHAM/UDN 主流程控制

```python
async def nodriver_kham_main(
    tab: nodriver.Tab,
    config_dict: dict,
    ocr: object,
    domain_name: str
) -> bool:
    """
    KHAM 家族（含 UDN）購票主流程。

    Args:
        tab: NoDriver 瀏覽器分頁
        config_dict: 設定字典
        ocr: OCR 辨識物件（ddddocr）
        domain_name: 網域名稱

    Returns:
        bool: 是否成功完成購票流程

    Contract:
        - 支援網域: kham.com.tw, ticket.com.tw, tickets.udnfunlife.com
        - URL 路由:
            - utk0201: 活動頁面 → 點擊購買按鈕
            - utk0203: 場次選擇 → nodriver_kham_date_auto_select
            - utk0204: 票區選擇 → nodriver_kham_area_auto_select
            - utk0205: 座位選擇 → nodriver_kham_seat_main
        - UDN 特殊處理:
            - 購買按鈕: button[name="fastBuy"]
            - 票數輸入: input.yd_counterNum
    """
```

---

## 輔助函數

### 5. parse_keyword_string

**用途**：解析關鍵字字串

```python
def parse_keyword_string(keyword_string: str) -> list[list[str]]:
    """
    解析關鍵字字串為結構化陣列。

    Args:
        keyword_string: 原始關鍵字字串
            - OR 邏輯: "\"kw1\",\"kw2\",\"kw3\""
            - AND 邏輯: "\"kw1 kw2\",\"kw3 kw4\""

    Returns:
        list[list[str]]: 結構化關鍵字陣列
            - 外層: OR 邏輯（逗號分隔）
            - 內層: AND 邏輯（空格分隔）

    Example:
        # OR 邏輯
        parse_keyword_string('"12/25","12/26"')
        # => [["12/25"], ["12/26"]]

        # AND 邏輯
        parse_keyword_string('"12/25 週六","12/26 週日"')
        # => [["12/25", "週六"], ["12/26", "週日"]]

    Contract:
        - 空字串返回空陣列 []
        - 移除前後空白
        - 移除引號包裝
    """
```

---

### 6. match_keyword_with_text

**用途**：關鍵字匹配文字

```python
def match_keyword_with_text(
    keyword_parts: list[str],
    text: str
) -> bool:
    """
    檢查文字是否符合關鍵字（支援 AND 邏輯）。

    Args:
        keyword_parts: 關鍵字部分列表（AND 邏輯）
        text: 目標文字

    Returns:
        bool: 是否匹配

    Example:
        # 單一關鍵字
        match_keyword_with_text(["12/25"], "2025/12/25 (週四)")
        # => True

        # AND 邏輯
        match_keyword_with_text(["12/25", "週四"], "2025/12/25 (週四)")
        # => True

        match_keyword_with_text(["12/25", "週六"], "2025/12/25 (週四)")
        # => False (週六 不匹配)

    Contract:
        - 所有 keyword_parts 都必須在 text 中找到
        - 大小寫敏感
        - 空白正規化處理
    """
```

---

### 7. check_keyword_exclude

**用途**：檢查是否被排除關鍵字過濾

```python
def check_keyword_exclude(
    config_dict: dict,
    text: str
) -> bool:
    """
    檢查文字是否包含排除關鍵字。

    Args:
        config_dict: 設定字典，需包含 keyword_exclude
        text: 目標文字

    Returns:
        bool: True 表示應該排除此項目

    Example:
        config = {"keyword_exclude": '"輪椅","身障"'}
        check_keyword_exclude(config, "特A區輪椅席")
        # => True (包含「輪椅」)

        check_keyword_exclude(config, "特A區")
        # => False (不包含排除關鍵字)

    Contract:
        - keyword_exclude 為空時返回 False
        - 任一排除關鍵字匹配即返回 True
        - 大小寫不敏感
    """
```

---

## 日誌格式

### 標記格式規範

所有日誌輸出必須使用以下標記格式（與 Feature 003 一致）：

| 標記 | 用途 | 範例 |
|------|------|------|
| `[DATE KEYWORD]` | 日期關鍵字匹配日誌 | `[DATE KEYWORD] Checking keyword #1: 12/25` |
| `[DATE SELECT]` | 日期選擇結果 | `[DATE SELECT] Selected date: 2025/12/25` |
| `[DATE FALLBACK]` | 日期遞補觸發 | `[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback` |
| `[AREA KEYWORD]` | 區域關鍵字匹配日誌 | `[AREA KEYWORD] Checking keyword #1: 特A區` |
| `[AREA SELECT]` | 區域選擇結果 | `[AREA SELECT] Selected area: 特A區` |
| `[AREA FALLBACK]` | 區域遞補觸發 | `[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback` |
| `[UDN SEAT]` | UDN 座位選擇日誌 | `[UDN SEAT] Found 20 available seats` |
| `[SUCCESS]` | 操作成功 | `[SUCCESS] Selected 2 seats` |
| `[ERROR]` | 操作失敗 | `[ERROR] No available seats` |

### 日誌範例

```
[DATE KEYWORD] Start checking keywords in order: ["12/25", "12/26"]
[DATE KEYWORD] Total keyword groups: 2
[DATE KEYWORD] Checking keyword #1: 12/25
[DATE KEYWORD] Keyword #1 matched: '12/25'
[DATE SELECT] Selected date: 2025/12/25 (週四) 19:30 (keyword match)

[AREA KEYWORD] Start checking keywords in order: ["特A區", "特B區"]
[AREA KEYWORD] Checking keyword #1: 特A區
[AREA KEYWORD] [0] Excluded by keyword_exclude: 特A區輪椅席
[AREA KEYWORD] Checking keyword #2: 特B區
[AREA KEYWORD] Keyword #2 matched: '特B區'
[AREA SELECT] Selected area: 特B區 NT$3,680 (keyword match)

[UDN SEAT] Stage direction: up
[UDN SEAT] Found 30 available seats
[UDN SEAT] Best row: 3排 (score: 85, continuous: 5)
[SUCCESS] Selected 2 seats: 2樓黃2D區-3排-14號, 2樓黃2D區-3排-15號
```

---

## 錯誤處理

### 錯誤碼

| 錯誤碼 | 說明 | 處理方式 |
|--------|------|---------|
| `NO_SESSIONS` | 無可用場次 | 返回 False，日誌記錄 |
| `NO_AREAS` | 無可用票區 | 返回 False，日誌記錄 |
| `NO_SEATS` | 無可用座位 | 返回 False，日誌記錄 |
| `KEYWORD_FAIL` | 關鍵字匹配失敗 | 觸發遞補或返回 False |
| `TIMEOUT` | 操作逾時 | 重試或返回 False |
| `DOM_ERROR` | DOM 結構異常 | 日誌記錄，返回 False |

### 重試策略

```python
MAX_RETRY = 3
RETRY_DELAY = 0.5  # 秒

for attempt in range(MAX_RETRY):
    try:
        result = await operation()
        if result:
            return True
    except Exception as e:
        if attempt < MAX_RETRY - 1:
            await asyncio.sleep(RETRY_DELAY)
        else:
            log_error(f"Operation failed after {MAX_RETRY} attempts: {e}")
            return False
```
