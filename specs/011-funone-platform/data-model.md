# 資料模型：FunOne Tickets 平台支援

**分支**：`011-funone-platform` | **日期**：2026-01-13 | **規格**：[spec.md](./spec.md)

## 1. 實體定義

### 1.1 設定實體

#### FunOneConfig（from settings.json）

| 欄位 | 類型 | 說明 | 必要 |
|------|------|------|------|
| `funone_session_cookie` | `string` | `ticket_session` Cookie 值 | 是（登入時） |

**備註**：購票張數使用通用的 `ticket_number` 設定

#### 共用設定（from 全域 settings.json）

| 欄位 | 說明 | 用途 |
|------|------|------|
| `homepage` | 目標活動 URL | FunOne 活動連結 |
| `ticket_number` | 預設購票張數 | 張數設定 |
| `area_keyword` | 票種關鍵字 | 票種篩選 |
| `date_keyword` | 場次關鍵字 | 場次篩選 |
| `pass_date_is_sold_out` | 跳過售罄場次 | 場次選擇 |
| `area_auto_select_mode` | 選擇模式 | 票種選擇策略 |

### 1.2 運行時狀態

#### FunOneState（記憶體）

| 欄位 | 類型 | 說明 |
|------|------|------|
| `is_logged_in` | `bool` | 是否已登入 |
| `current_step` | `str` | 當前步驟 |
| `selected_date` | `str` | 已選場次 |
| `selected_area` | `str` | 已選票種 |
| `ticket_count` | `int` | 已選張數 |
| `captcha_solved` | `bool` | 驗證碼是否已解 |

### 1.3 頁面識別

#### FunOnePageType（枚舉）

| 值 | URL 特徵 | 說明 |
|----|----------|------|
| `HOME` | `/` 且無其他路徑 | 首頁 |
| `ACTIVITY_DETAIL` | `/activity/activity_detail/` | 活動詳情 |
| `LOGIN` | `/login` | 登入頁 |
| `TICKET_SELECT` | 購票中（動態判斷） | 選票頁 |
| `ORDER_CONFIRM` | 訂單確認（動態判斷） | 確認頁 |
| `MEMBER` | `/member` | 會員中心 |
| `UNKNOWN` | 其他 | 未知頁面 |

## 2. 資料流

### 2.1 設定載入流程

```
settings.json
    │
    ├─► funone_session_cookie ──► Cookie 注入
    │
    ├─► ticket_number ──────────► 張數設定
    │
    ├─► area_keyword ───────────► 票種篩選
    │
    └─► date_keyword ───────────► 場次篩選
```

### 2.2 購票流程狀態轉換

```
[START] ──► 注入 Cookie ──► 驗證登入
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               [已登入]            [未登入]
                    │                   │
                    ▼                   ▼
              活動詳情頁           登入頁（等待）
                    │
                    ▼
              選擇場次 ◄──────── date_keyword
                    │
                    ▼
              選擇票種 ◄──────── area_keyword
                    │
                    ▼
              設定張數 ◄──────── ticket_number
                    │
                    ▼
              驗證碼輸入（人工）
                    │
                    ▼
              提交訂單
                    │
                    ▼
               [END]
```

## 3. 函數簽章

### 3.1 主流程函數

```python
async def nodriver_funone_main(
    tab: nodriver.Tab,
    url: str,
    config_dict: dict
) -> nodriver.Tab:
    """
    FunOne 主控制函數

    Args:
        tab: NoDriver 標籤頁
        url: 當前 URL
        config_dict: 設定字典

    Returns:
        處理後的標籤頁
    """
```

### 3.2 Cookie 登入函數

```python
async def nodriver_funone_inject_cookie(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    注入 FunOne session cookie

    Args:
        tab: NoDriver 標籤頁
        config_dict: 設定字典（需含 funone_session_cookie）

    Returns:
        True 表示注入成功
    """

async def nodriver_funone_check_login_status(
    tab: nodriver.Tab
) -> bool:
    """
    檢查是否已登入

    Returns:
        True 表示已登入
    """

async def nodriver_funone_verify_login(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    驗證登入狀態，失敗則重新注入 Cookie

    Returns:
        True 表示登入有效
    """
```

### 3.3 場次/票種選擇函數

```python
async def nodriver_funone_date_auto_select(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    自動選擇場次（使用 date_keyword 篩選）

    Returns:
        True 表示選擇成功
    """

async def nodriver_funone_area_auto_select(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    自動選擇票種（使用 area_keyword 篩選）

    Returns:
        True 表示選擇成功
    """

async def nodriver_funone_assign_ticket_number(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    設定購票張數

    Returns:
        True 表示設定成功
    """
```

### 3.4 驗證碼與訂單函數

```python
async def nodriver_funone_captcha_handler(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    驗證碼處理（等待人工輸入）

    Returns:
        True 表示驗證碼已完成
    """

async def nodriver_funone_order_submit(
    tab: nodriver.Tab,
    config_dict: dict
) -> bool:
    """
    提交訂單

    Returns:
        True 表示提交成功
    """
```

### 3.5 輔助函數

```python
async def nodriver_funone_auto_reload(
    tab: nodriver.Tab,
    config_dict: dict
) -> nodriver.Tab:
    """
    自動重載頁面（開賣前監控）

    Returns:
        重載後的標籤頁
    """

async def nodriver_funone_close_popup(
    tab: nodriver.Tab
) -> bool:
    """
    關閉彈窗

    Returns:
        True 表示有彈窗被關閉
    """

async def nodriver_funone_ticket_agree(
    tab: nodriver.Tab
) -> bool:
    """
    同意購票條款

    Returns:
        True 表示同意成功
    """

async def nodriver_funone_error_handler(
    tab: nodriver.Tab,
    error_type: str
) -> bool:
    """
    錯誤處理

    Args:
        error_type: 錯誤類型

    Returns:
        True 表示錯誤已處理
    """
```

## 4. 整合點

### 4.1 util.py 共用函數

| 函數 | 用途 |
|------|------|
| `get_target_index_by_mode()` | 計算目標索引（票種/場次） |
| `get_target_item_from_matched_list()` | 取得匹配項目 |
| `get_debug_mode()` | 取得除錯模式 |
| `parse_keyword_string_to_array()` | 解析關鍵字字串 |

### 4.2 nodriver_tixcraft.py 共用模式

| 模式 | 參考函數 |
|------|----------|
| Cookie 注入 | `nodriver_tixcraft_sid_inject()` |
| 頁面等待 | `nodriver_kktix_wait_for_page()` |
| 元素點擊 | `nodriver_tixcraft_area_auto_select()` |

## 5. 錯誤碼定義

| 錯誤碼 | 說明 | 處理方式 |
|--------|------|----------|
| `FUNONE_NOT_LOGGED_IN` | 未登入 | 重新注入 Cookie |
| `FUNONE_SESSION_EXPIRED` | Session 過期 | 提示用戶更新 Cookie |
| `FUNONE_DATE_NOT_FOUND` | 找不到場次 | 等待或重載 |
| `FUNONE_AREA_NOT_FOUND` | 找不到票種 | 等待或重載 |
| `FUNONE_SOLD_OUT` | 售罄 | 重載或換票種 |
| `FUNONE_CAPTCHA_FAILED` | 驗證碼失敗 | 重試 |
| `FUNONE_SUBMIT_FAILED` | 提交失敗 | 重試 |
