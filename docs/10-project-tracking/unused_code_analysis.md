# 未使用程式碼分析報告

**日期**：2026-02-09
**範圍**：`src/util.py`、`src/nodriver_tixcraft.py`、`src/settings_old.py`
**狀態**：僅分析與紀錄，未修改任何程式碼

---

## 總覽

| 分類 | 數量 | 優先級 |
|------|------|--------|
| 整個已廢棄檔案 | 1 | HIGH |
| 外部從未呼叫的函數 (util.py) | 1 | MEDIUM |
| 未使用的常數 (nodriver_tixcraft.py) | 2 | LOW |
| 未使用的函數 (nodriver_tixcraft.py) | 1 | LOW |
| 未使用的常數 (util.py) | 1 | LOW |
| 僅內部使用的函數鏈 (util.py) | 詳見 E 節 | INFO |
| 死碼路徑中缺少的 import (util.py) | 2 | INFO |

---

## A. HIGH - 已廢棄的完整檔案

### `src/settings_old.py`

- **狀態**：已廢棄，沒有任何模組 import 此檔案
- **證據**：檔案第 47-50 行印出棄用警告：
  ```
  "settings_old.py is no longer maintained."
  "settings_old 已經停止更新，請改用 settings.py"
  ```
- **建議**：可安全整個刪除
- **風險**：無，全專案沒有任何 import 參照

---

## B. MEDIUM - 外部從未呼叫的函數

### `util.py` - `get_kktix_status_by_url()` (第 2218 行)

- **定義位置**：`src/util.py:2218`
- **被誰呼叫**：無人（零個外部或內部參照）
- **它呼叫了**：`kktix_get_event_code()`、`kktix_get_registerStatus()`
- **建議**：可安全移除
- **注意**：`kktix_get_registerStatus()` 仍被 `chrome_tixcraft.py:3130` 使用，僅需移除 `get_kktix_status_by_url()` 本身

---

## C. LOW - nodriver_tixcraft.py 中的冗餘程式碼

這些是從其他檔案複製過來，但在 `nodriver_tixcraft.py` 中從未使用的常數與函數。

### 1. `CONST_SELECT_ORDER_DEFAULT` (第 108 行)

- **值**：`CONST_FROM_TOP_TO_BOTTOM`
- **在檔案中使用次數**：0
- **備註**：`settings.py` 有自己的版本（值為 `CONST_RANDOM`），並在該檔案中使用
- **建議**：從 `nodriver_tixcraft.py` 移除

### 2. `CONT_STRING_1_SEATS_REMAINING` (第 110 行)

- **值**：`['@1 seat(s) remaining','剩餘 1@','@1 席残り']`
- **在檔案中使用次數**：0
- **備註**：僅在 `chrome_tixcraft.py:1486` 使用（Chrome 實作路徑）
- **建議**：從 `nodriver_tixcraft.py` 移除

### 3. `read_last_url_from_file()` (第 194 行)

- **在檔案中使用次數**：0
- **備註**：與 `settings.py:219` 和 `chrome_tixcraft.py:219` 重複定義
- **建議**：從 `nodriver_tixcraft.py` 移除

---

## D. LOW - util.py 中未使用的常數

### `CONST_KEYWORD_DELIMITER_OLD` (第 24 行)

- **值**：`','`
- **註解**：「Old delimiter (comma) for backward compatibility detection」
- **使用次數**：全專案搜尋結果為 0（僅有定義處）
- **建議**：若不再需要向下相容偵測，可移除

---

## E. INFO - util.py 中僅內部使用的函數鏈

以下函數**僅在 util.py 內部被呼叫**（從未被外部模組直接呼叫）。它們組成支援公開 API `get_answer_list_from_question_string()` 的內部呼叫鏈。**不是死碼**，但值得記錄其耦合關係。

### 呼叫鏈：`get_answer_list_from_question_string()` (公開 API)

```
get_answer_list_from_question_string()              # 第 1973 行 (外部呼叫：nodriver/chrome)
  +-- get_answer_list_by_question()                  # 第 1227 行 (僅內部)
  |     +-- format_question_string()                 # 第 1155 行 (僅內部)
  |     +-- guess_answer_list_from_hint()             # 第 902 行  (僅內部)
  |     |     +-- get_offical_hint_string_from_symbol()  # 第 860 行 (僅內部)
  |     +-- guess_answer_list_from_multi_options()     # 第 653 行  (僅內部)
  |     |     +-- is_all_alpha_or_numeric()           # 第 486 行  (僅內部)
  |     +-- permutations()                            # 第 1204 行 (僅內部)
  |     +-- guess_answer_list_from_symbols()          # 第 828 行  (僅內部)
  +-- get_answer_string_from_web_date()               # 第 1755 行 (僅內部)
  |     +-- kktix_get_web_datetime()                  # 第 1698 行 (僅內部，使用 Selenium By)
  |     +-- find_continuous_number()                  # 第 463 行  (僅內部)
  |     |     +-- find_continuous_pattern()            # 第 471 行  (僅內部)
  |     +-- convert_string_to_pattern()               # 第 611 行  (僅內部)
  +-- get_answer_string_from_web_time()               # 第 1886 行 (僅內部)
  |     +-- kktix_get_web_datetime()                  # 第 1698 行 (重複使用)
  +-- format_quota_string()                           # 第 380 行  (僅內部)
  +-- check_answer_keep_symbol()                      # 第 1655 行 (僅內部)
  +-- normalize_chinese_numeric()                     # 第 455 行  (僅內部)
```

### Discord 通知鏈

```
send_discord_webhook_async()  # 第 2437 行 (外部呼叫：nodriver_tixcraft.py)
  +-- send_discord_webhook()  # 第 2395 行 (僅內部)
        +-- build_discord_message()  # 第 2368 行 (僅內部)
```

### Cloudflare 挑戰鏈

```
(util.py 內部的公開呼叫者)
  +-- get_cf_template_paths()  # 第 2470 行 (僅內部)
```

**建議**：不需移除，這些是有效的內部輔助函數。

---

## F. INFO - 死碼路徑中缺少的 Import

`kktix_get_web_datetime()` 函數（第 1698 行）使用了：
- `datetime.now()` / `datetime.strptime()` — `datetime` **未在 util.py 中 import**
- `By.TAG_NAME` — `selenium.webdriver.common.by.By` **未在 util.py 中 import**

此程式碼路徑僅在 `get_answer_list_from_question_string()` 以非 None 的 `registrationsNewApp_div`（Selenium 元素）呼叫時觸發，這只發生在 `chrome_tixcraft.py:2920`。NoDriver 路徑中一律傳入 `None`，因此缺少的 import 不會導致執行時錯誤。

**建議**：若 Chrome 路徑（`chrome_tixcraft.py`）仍在維護，應補上 import。若 Chrome 路徑已廢棄，可考慮清理整條函數鏈。

---

## 清理執行計畫

當準備進行清理時，依以下順序執行：

### 第一階段 - 安全刪除（零風險）
1. 刪除 `src/settings_old.py`
2. 移除 `util.py:24` 的 `CONST_KEYWORD_DELIMITER_OLD`
3. 移除 `util.py:2218-2226` 的 `get_kktix_status_by_url()`

### 第二階段 - nodriver_tixcraft.py 清理（低風險）
4. 移除 `nodriver_tixcraft.py:108` 的 `CONST_SELECT_ORDER_DEFAULT`
5. 移除 `nodriver_tixcraft.py:110` 的 `CONT_STRING_1_SEATS_REMAINING`
6. 移除 `nodriver_tixcraft.py:194` 的 `read_last_url_from_file()`

### 第三階段 - 評估 Chrome 路徑（需決策）
7. 確認 `chrome_tixcraft.py` 是否仍在積極維護
8. 若已廢棄：移除 `util.py` 中依賴 Selenium 的內部輔助函數
9. 若仍維護：補上缺少的 `datetime` 和 `By` import
