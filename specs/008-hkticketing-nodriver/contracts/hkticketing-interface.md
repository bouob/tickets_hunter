# HKTicketing NoDriver 介面契約

**功能**：008-hkticketing-nodriver
**日期**：2025-11-27
**狀態**：完成

## 函數簽名定義

### 主流程控制

```python
async def nodriver_hkticketing_main(tab: Tab, url: str, config_dict: dict) -> Tab:
    """
    HKTicketing 平台主流程控制函數

    Args:
        tab: NoDriver Tab 物件
        url: 當前頁面 URL
        config_dict: 設定字典

    Returns:
        Tab: 更新後的 Tab 物件（可能因分頁切換而改變）

    Behavior:
        - 根據 URL 路由到對應的處理函數
        - 管理 hkticketing_dict 狀態
        - 處理錯誤頁面重定向
    """
```

### 登入功能（階段 2）

```python
async def nodriver_hkticketing_login(tab: Tab, account: str, password: str) -> bool:
    """
    HKTicketing 自動登入

    Args:
        tab: NoDriver Tab 物件
        account: 帳號
        password: 密碼

    Returns:
        bool: 是否成功填入帳密並嘗試登入

    Behavior:
        - 檢查帳號欄位是否可用
        - 填入帳號
        - 填入密碼
        - 按下 Enter 提交
    """
```

### Cookie 處理（階段 3）

```python
async def nodriver_hkticketing_accept_cookie(tab: Tab) -> None:
    """
    關閉 Cookie 同意彈窗

    Args:
        tab: NoDriver Tab 物件

    Returns:
        None

    Behavior:
        - 嘗試找到 Cookie 彈窗關閉按鈕
        - 若可見則點擊關閉
    """
```

### 日期選擇功能（階段 4）

```python
async def nodriver_hkticketing_date_assign(tab: Tab, config_dict: dict) -> Tuple[bool, bool, List]:
    """
    日期指派核心邏輯

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典

    Returns:
        Tuple[bool, bool, List]:
            - is_date_assigned: 是否已選擇日期
            - is_page_ready: 頁面是否已載入完成
            - formated_area_list: 格式化後的可用日期列表

    Behavior:
        - 檢查日期下拉選單
        - 過濾已售完日期
        - 根據關鍵字匹配日期
        - 選擇目標日期
        - 若關鍵字匹配失敗且 date_auto_fallback=true，使用 auto_select_mode 自動遞補
        - 若關鍵字匹配失敗且 date_auto_fallback=false，停止選擇（嚴格模式）
    """

async def nodriver_hkticketing_date_auto_select(tab: Tab, config_dict: dict, fail_list: List[str]) -> Tuple[bool, List[str]]:
    """
    日期自動選擇整合函數

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典
        fail_list: 密碼嘗試失敗清單

    Returns:
        Tuple[bool, List[str]]:
            - is_date_submiting: 是否正在提交
            - fail_list: 更新後的失敗清單

    Behavior:
        - 調用 date_assign 選擇日期
        - 處理密碼輸入（若需要）
        - 點擊購買按鈕
        - 處理頁面重載（若需要）
    """

async def nodriver_hkticketing_date_buy_button_press(tab: Tab) -> bool:
    """
    點擊購買按鈕

    Args:
        tab: NoDriver Tab 物件

    Returns:
        bool: 是否成功點擊

    Behavior:
        - 查找購買按鈕
        - 嘗試點擊
        - 若 disabled 則使用 JavaScript 強制點擊
    """

async def nodriver_hkticketing_date_password_input(tab: Tab, config_dict: dict, fail_list: List[str]) -> Tuple[bool, List[str]]:
    """
    密碼保護頁面處理

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典
        fail_list: 密碼嘗試失敗清單

    Returns:
        Tuple[bool, List[str]]:
            - is_password_appear: 密碼輸入框是否存在
            - fail_list: 更新後的失敗清單

    Behavior:
        - 檢查密碼輸入框是否存在
        - 從 user_guess_string 取得密碼猜測
        - 跳過已失敗的密碼
        - 填入密碼並提交
    """
```

### 區域選擇功能（階段 5）

```python
async def nodriver_hkticketing_area_auto_select(tab: Tab, config_dict: dict, area_keyword_item: str) -> Tuple[bool, bool]:
    """
    區域自動選擇

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典
        area_keyword_item: 區域關鍵字（單個）

    Returns:
        Tuple[bool, bool]:
            - is_need_refresh: 是否需要重載頁面
            - is_price_assign_by_bot: 是否已選擇區域

    Behavior:
        - 查找所有區域選項
        - 過濾 disabled/unavailable 區域
        - 檢查是否已有 selected 區域
        - 根據關鍵字匹配區域
        - 套用排除關鍵字
        - 選擇目標區域
        - 若關鍵字匹配失敗且 area_auto_fallback=true，使用 auto_select_mode 自動遞補
        - 若關鍵字匹配失敗且 area_auto_fallback=false，停止選擇（嚴格模式）
    """
```

### 票數設定功能（階段 6）

```python
async def nodriver_hkticketing_ticket_number_auto_select(tab: Tab, config_dict: dict) -> bool:
    """
    票數自動設定

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典

    Returns:
        bool: 是否成功設定票數

    Behavior:
        - 查找票數下拉選單
        - 設定指定票數
    """
```

### 訂單送出功能（階段 10）

```python
async def nodriver_hkticketing_nav_to_footer(tab: Tab) -> None:
    """
    捲動到頁面底部

    Args:
        tab: NoDriver Tab 物件

    Returns:
        None

    Behavior:
        - 查找 footer 元素
        - 捲動到可見區域
    """

async def nodriver_hkticketing_next_button_press(tab: Tab) -> bool:
    """
    點擊下一步按鈕

    Args:
        tab: NoDriver Tab 物件

    Returns:
        bool: 是否成功點擊

    Behavior:
        - 先捲動到 footer
        - 查找下一步按鈕
        - 點擊按鈕
    """

async def nodriver_hkticketing_go_to_payment(tab: Tab) -> bool:
    """
    點擊前往付款按鈕

    Args:
        tab: NoDriver Tab 物件

    Returns:
        bool: 是否成功點擊

    Behavior:
        - 查找付款按鈕
        - 點擊按鈕
    """

async def nodriver_hkticketing_ticket_delivery_option(tab: Tab) -> bool:
    """
    選擇取票方式

    Args:
        tab: NoDriver Tab 物件

    Returns:
        bool: 是否成功選擇

    Behavior:
        - 查找取票方式下拉選單
        - 選擇預設選項（值為 "1"）
    """

async def nodriver_hkticketing_performance(tab: Tab, config_dict: dict, domain_name: str) -> bool:
    """
    票券選擇頁面整合流程

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典
        domain_name: 網站域名

    Returns:
        bool: 是否成功完成選擇

    Behavior:
        - 選擇區域（支援多關鍵字）
        - 捲動到 footer
        - 設定票數
        - 選擇取票方式（非 Galaxy Macau）
        - 點擊下一步按鈕
    """
```

### 錯誤處理功能（階段 12）

```python
async def nodriver_hkticketing_url_redirect(tab: Tab, url: str, config_dict: dict) -> bool:
    """
    URL 重定向處理

    Args:
        tab: NoDriver Tab 物件
        url: 當前 URL
        config_dict: 設定字典

    Returns:
        bool: 是否執行了重定向

    Behavior:
        - 檢查 URL 是否匹配重定向模式
        - 執行重定向到入口頁面
        - 處理 Access denied 情況
    """

async def nodriver_hkticketing_content_refresh(tab: Tab, url: str, config_dict: dict) -> bool:
    """
    內容錯誤重載處理

    Args:
        tab: NoDriver Tab 物件
        url: 當前 URL
        config_dict: 設定字典

    Returns:
        bool: 是否執行了重載

    Behavior:
        - 檢查頁面內容是否包含錯誤訊息
        - 執行重定向到首頁
    """

async def nodriver_hkticketing_travel_iframe(tab: Tab, config_dict: dict) -> bool:
    """
    遍歷 iframe 內容進行錯誤檢測

    Args:
        tab: NoDriver Tab 物件
        config_dict: 設定字典

    Returns:
        bool: 是否執行了重定向

    Behavior:
        - 遍歷所有 iframe
        - 檢查 iframe 內容是否有錯誤訊息
        - 執行重定向（若需要）
    """

async def nodriver_hkticketing_escape_robot_detection(tab: Tab, url: str) -> bool:
    """
    機器人檢測繞過

    Args:
        tab: NoDriver Tab 物件
        url: 當前 URL

    Returns:
        bool: 是否被檢測到

    Behavior:
        - 檢查是否存在檢測 iframe
        - 記錄檢測狀態
    """
```

### 頁面優化功能

```python
async def nodriver_hkticketing_hide_tickets_blocks(tab: Tab) -> None:
    """
    隱藏不必要的頁面區塊

    Args:
        tab: NoDriver Tab 物件

    Returns:
        None

    Behavior:
        - 清空 actionBlock 區塊
        - 清空 detailModuleCopy 區塊
        - 清空 mapWrapper 區塊
    """
```

---

## 輸入驗證規則

### config_dict 必要欄位

```python
# 日期選擇必要欄位
assert "date_auto_select" in config_dict
assert "enable" in config_dict["date_auto_select"]
assert "date_keyword" in config_dict["date_auto_select"]
assert "mode" in config_dict["date_auto_select"]

# 區域選擇必要欄位
assert "area_auto_select" in config_dict
assert "enable" in config_dict["area_auto_select"]
assert "area_keyword" in config_dict["area_auto_select"]
assert "mode" in config_dict["area_auto_select"]

# 其他必要欄位
assert "ticket_number" in config_dict
assert "advanced" in config_dict
assert "tixcraft" in config_dict

# Fallback 設定欄位（選填，預設 False）
# config_dict.get("date_auto_fallback", False)
# config_dict.get("area_auto_fallback", False)
```

### Fallback 設定欄位

```python
# Fallback 設定（預設 False = 嚴格模式，避免誤購）
date_auto_fallback = config_dict.get("date_auto_fallback", False)  # 日期關鍵字全失敗時是否自動遞補
area_auto_fallback = config_dict.get("area_auto_fallback", False)  # 區域關鍵字全失敗時是否自動遞補

# Fallback 邏輯說明：
# - False（預設）：關鍵字匹配失敗時，停止選擇流程，避免選到不想要的日期/區域
# - True：關鍵字匹配失敗時，使用 auto_select_mode（排序方式）自動遞補選擇
```

### mode 有效值

```python
VALID_MODES = [
    "from top to bottom",
    "from bottom to top",
    "center",
    "random"
]
assert config_dict["date_auto_select"]["mode"] in VALID_MODES
assert config_dict["area_auto_select"]["mode"] in VALID_MODES
```

---

## 錯誤處理契約

### 標準錯誤處理模式

```python
async def function_template(tab: Tab, config_dict: dict) -> bool:
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        # 主要邏輯
        element = await tab.query_selector("selector")
        if element:
            await element.click()
            return True
    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] function_template: {exc}")

    return False
```

### 重試機制

- 下一步按鈕：最多重試 2 次，每次間隔 0.2 秒
- 頁面重載：遵循 `auto_reload_page_interval` 設定
