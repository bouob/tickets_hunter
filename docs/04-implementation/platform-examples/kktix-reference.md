# KKTIX 平台參考實作

**文件說明**：KKTIX 平台的完整實作參考，涵蓋問答式驗證碼、價格列表選擇、排隊機制等核心特性的技術實作與案例說明。
**最後更新**：2026-06-07

---

## 概述

**平台名稱**：KKTIX
**主要特色**：
- **問答式驗證碼**：最具挑戰性的驗證碼類型
- **價格列表模式**：兩階段區域選擇（價格表 + 票數輸入）
- **Register Status 區域**：支援預售/一般售票的雙區域模式
- **自動下一步**：可設定自動/手動按下一步按鈕

**完成度**：100% ✅
**推薦作為**：問答式驗證碼、價格列表模式的參考實作

---

## 核心函數索引

| 階段 | 函數名稱 | 行數 | 說明 |
|------|---------|------|------|
| Main | `nodriver_kktix_main()` | - | 主控制流程（URL 路由）|
| Stage 2 | `nodriver_kktix_signin()` | - | 登入處理 |
| Stage 3 | `nodriver_kktix_paused_main()` | - | 暫停/排隊頁面處理 |
| Stage 4 | `nodriver_kktix_date_auto_select()` | - | 日期自動選擇 |
| Stage 5 | `nodriver_kktix_travel_price_list()` | - | 批次擷取與配對價格列表 |
| Stage 5 | `nodriver_kktix_assign_ticket_number()` | - | 區域選擇 + 票數輸入 |
| Stage 7 | `nodriver_kktix_reg_captcha()` | - | 問答式驗證碼處理 |
| Stage 8 | `nodriver_kktix_reg_new_main()` | - | 註冊頁面主處理 |
| Stage 9 | `nodriver_kktix_check_guest_modal()` | - | 訪客模式對話框 |
| Stage 10 | `nodriver_kktix_press_next_button()` | - | 下一步按鈕點擊 |
| Stage 10 | `nodriver_kktix_events_press_next_button()` | - | Events 頁面下一步 |
| Stage 10 | `nodriver_kktix_confirm_order_button()` | - | 確認訂單按鈕 |
| Util | `nodriver_kktix_check_ticket_page_status()` | - | 票券頁面狀態檢查 |
| Util | `nodriver_kktix_order_member_code()` | - | 會員代碼處理 |

**程式碼位置**：`src/platforms/kktix.py`

---

## 特殊設計 1: 問答式驗證碼

### 挑戰

KKTIX 使用**問答式驗證碼**,而非傳統圖形驗證碼:
- 問題範例：「請問演唱會地點是？」
- 答案選項：台北小巨蛋 / 台中洲際 / 高雄巨蛋 / 其他
- 需要**關鍵字匹配** + **fail_list 機制**

### 解決方案

**核心程式碼**（`nodriver_kktix_reg_captcha`, Line 1171-1330）:

```python
# Step 1: 檢測問題元素
elements_check = await tab.evaluate('''
    (function() {
        return {
            hasQuestion: !!document.querySelector('div.custom-captcha-inner p'),
            hasInput: !!document.querySelector('div.custom-captcha-inner > div > div > input'),
            questionText: document.querySelector('div.custom-captcha-inner p')?.innerText || ''
        };
    })();
''')

# Step 2: 取得答案列表（多來源）
if elements_check.get('hasQuestion'):
    question_text = elements_check.get('questionText', '')

    # 來源 1: 使用者自訂答案（user_guess_string）
    answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)

    # 來源 2: 自動推測（auto_guess_options=true）
    if len(answer_list) == 0 and config_dict["advanced"]["auto_guess_options"]:
        answer_list = util.get_answer_list_from_question_string(None, question_text)

    # Step 3: fail_list 機制 - 跳過已失敗的答案
    inferred_answer_string = ""
    for answer_item in answer_list:
        if not answer_item in fail_list:  # ⭐ 避免重複錯誤
            inferred_answer_string = answer_item
            break

    # Step 4: 填寫答案（人類化延遲 + 重試）
    max_retries = 3
    for retry_count in range(max_retries):
        # 隨機延遲 0.3-1.0 秒
        human_delay = random.uniform(0.3, 1.0)
        await tab.sleep(human_delay)

        # 逐字輸入模擬真人
        fill_result = await tab.evaluate(f'''
            (function() {{
                const input = document.querySelector('div.custom-captcha-inner > div > div > input');
                input.focus();
                input.value = "";

                const answer = "{inferred_answer_string}";
                for (let i = 0; i < answer.length; i++) {{
                    input.value += answer[i];
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}

                input.blur();
                return {{ success: true, value: input.value }};
            }})();
        ''')
```

**設定範例**（`settings.json`）：
```json
{
  "advanced": {
    "user_guess_string": "台北,小巨蛋,台大,2025",  // 自訂答案庫
    "auto_guess_options": true  // 自動推測答案
  }
}
```

**優勢**：
- ✅ 支援多來源答案（使用者自訂 + 自動推測）
- ✅ fail_list 避免重複錯誤
- ✅ 人類化延遲避免偵測

---

## 特殊設計 2: 價格列表模式（兩階段區域選擇）

### 挑戰

KKTIX 的區域選擇是**兩階段流程**：
1. **Stage 1**: 從價格列表選擇票種（`div.display-table-row`）
2. **Stage 2**: 輸入票數到對應輸入框（`input[type="text"]`）

這與其他平台的「直接點擊區域按鈕」不同。

### 解決方案

**核心程式碼**（`src/platforms/kktix.py`）:

```python
async def nodriver_kktix_travel_price_list(tab, config_dict, auto_select_mode, area_keyword):
    # Stage 1: 一次擷取所有票種列，避免逐列 CDP/DOM 往返。
    ticket_rows = await tab.evaluate("""
        (function() {
            let rows = Array.from(document.querySelectorAll('div.display-table-row'));
            if (rows.length === 0) {
                rows = Array.from(document.querySelectorAll('div.ticket-item'));
            }

            let inputIndex = 0;
            return rows.map((row, rowIndex) => {
                const input = row.querySelector('input');
                const hasInput = !!input;
                const rowInputIndex = hasInput ? inputIndex : null;
                if (hasInput) inputIndex += 1;

                return {
                    index: rowIndex,
                    html: row.innerHTML || "",
                    text: row.textContent || row.innerText || "",
                    hasInput: hasInput,
                    inputValue: input ? input.value : "0",
                    inputIndex: rowInputIndex
                };
            });
        })()
    """)

    # Stage 2: Python 端依序做排除關鍵字、售完狀態、票數不足與 AND 關鍵字配對。
    matched_input_indexes = []
    for ticket in ticket_rows:
        row_text = util.format_keyword_string(ticket["text"])
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            continue
        if not all(kw in row_text for kw in area_keyword.split(" ") if kw.strip()):
            continue
        if ticket["hasInput"]:
            matched_input_indexes.append(ticket["inputIndex"])
            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                break

    return matched_input_indexes

async def nodriver_kktix_assign_ticket_number(tab, config_dict, area_keyword):
    # Stage 3: 使用選中的 input index 填入票數，並觸發 Angular input/change/blur。
    is_dom_ready, is_assigned, matched_blocks = await nodriver_kktix_travel_price_list(
        tab,
        config_dict,
        config_dict["area_auto_select"]["mode"],
        area_keyword,
    )
```

**設定範例**：
```json
{
  "ticket_number": 2,
  "area_auto_select": {
    "enable": true,
    "area_keyword": "\"全票\",\"早鳥票\",\"VIP票\""  // 價格列表關鍵字
  }
}
```

**關鍵差異**：
| 項目 | KKTIX | TixCraft/iBon |
|------|-------|--------------|
| 區域選擇方式 | 輸入票數到輸入框 | 點擊區域按鈕/連結 |
| 票數設定 | Stage 5 同時處理 | Stage 6 獨立處理 |
| 關鍵字目標 | 票種名稱（全票/VIP票） | 座位區域（搖滾區/A區） |
| 候選資料取得 | 批次擷取票種列文字、HTML、input index | TixCraft 批次擷取區域文字與票數提示 |

---

## 特殊設計 3: Register Status 雙區域模式

### 挑戰

KKTIX 可能有**兩種售票區域**：
1. **Presale**（預售）：早鳥票、VIP 優先購票
2. **General Sale**（一般售票）：正式開賣

兩者可能同時存在於同一頁面,需要優先選擇預售區域。

### 解決方案

```python
# Query both presale and general sale areas
presale_areas = await registrationsNewApp_div.query_selector_all('div.register-status[data-mode="presale"]')
general_areas = await registrationsNewApp_div.query_selector_all('div.register-status[data-mode="general"]')

# Priority: Presale > General Sale
if len(presale_areas) > 0:
    ticket_areas = presale_areas
    if show_debug_message:
        print(f"[KKTIX] Using presale area (found {len(presale_areas)} presale tickets)")
elif len(general_areas) > 0:
    ticket_areas = general_areas
    if show_debug_message:
        print(f"[KKTIX] Using general sale area (found {len(general_areas)} general tickets)")
```

---

## 特殊設計 4: 自動下一步按鈕

### 挑戰

KKTIX 的購票流程需要多次點擊「下一步」按鈕,某些使用者希望自動化,某些希望手動確認。

### 解決方案

```python
# Check if auto press next step button
auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
max_dwell_time = config_dict["kktix"]["max_dwell_time"]  # 最大停留時間（秒）

if auto_press_next_step_button:
    # Auto press next button
    next_buttons = await tab.query_selector_all('div.register-new-next-button-area > button')
    if next_buttons and len(next_buttons) > 0:
        # Human delay
        button_delay = random.uniform(0.2, 0.5)
        await tab.sleep(button_delay)

        await next_buttons[0].click()
        if show_debug_message:
            print("[KKTIX] Auto pressed next step button")
else:
    # Wait for manual confirmation
    if show_debug_message:
        print(f"[KKTIX] Waiting for manual confirmation (max {max_dwell_time}s)")
    await asyncio.sleep(max_dwell_time)
```

**設定範例**：
```json
{
  "kktix": {
    "auto_press_next_step_button": true,  // 自動下一步
    "max_dwell_time": 90  // 最大停留時間（秒）
  }
}
```

---

## 完整流程範例（KKTIX 購票）

```python
async def kktix_purchase_flow_example():
    """KKTIX 完整購票流程示範"""

    # Stage 3: 監控頁面 + 日期選擇
    await nodriver_kktix_presale_home(tab, url, config_dict)
    # → 選擇演唱會日期（button[data-href]）

    # Stage 5: 區域選擇 + 票數輸入（兩階段）
    await nodriver_kktix_assign_ticket_number(tab, config_dict)
    # → Stage 1: 匹配票種（全票/VIP票）
    # → Stage 2: 輸入票數到 input[type="text"]

    # Stage 7: 問答式驗證碼
    await nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div)
    # → 取得問題文字
    # → 匹配答案（user_guess_string + auto_guess + fail_list）
    # → 填寫答案（人類化延遲 + 重試）

    # Stage 9: 同意條款（自動處理）
    # → KKTIX 會自動勾選條款（無需特殊處理）

    # Stage 10: 下一步按鈕
    if config_dict["kktix"]["auto_press_next_step_button"]:
        await press_next_button(tab)
    else:
        await asyncio.sleep(config_dict["kktix"]["max_dwell_time"])
```

---

## 最佳實踐建議

### 1. 問答式驗證碼

**建議設定**：
```json
{
  "advanced": {
    "user_guess_string": "台北,小巨蛋,台大,五月天,2025,演唱會",  // ⭐ 豐富的答案庫
    "auto_guess_options": true  // ⭐ 啟用自動推測
  }
}
```

**使用者行動**：
1. 準備常見答案關鍵字（地點、樂團名、日期）
2. 監控問題日誌（`question.txt`）
3. 根據失敗問題補充答案庫

### 2. 價格列表關鍵字

**建議設定**：
```json
{
  "area_auto_select": {
    "area_keyword": "\"全票\",\"早鳥票\",\"VIP票\",\"特別席\""  // ⭐ 按優先級排列
  }
}
```

**優先級策略**：
- 第 1 個：最想要的票種（VIP票）
- 第 2 個：次要選擇（早鳥票）
- 第 3 個：最後選擇（全票）

### 3. 自動下一步開關

**建議**：
- **新手使用者**：`auto_press_next_step_button=false`（手動確認）
- **熟練使用者**：`auto_press_next_step_button=true`（完全自動化）

---

## 常見問題

### Q1: 問答式驗證碼總是失敗怎麼辦？

**A**: 檢查並補充答案庫。

**步驟**：
1. 查看問題日誌：`question.txt` 或 `MAXBOT_QUESTION.txt`
2. 找出常見問題類型（地點/樂團/日期）
3. 補充到 `user_guess_string`:
```json
{
  "user_guess_string": "台北,小巨蛋,台大,五月天,2025/11,2025/12,演唱會,音樂祭"
}
```

### Q2: 為什麼 KKTIX 區域選擇與其他平台不同？

**A**: KKTIX 使用**價格列表模式**,而非座位區域模式。

**差異**：
- **TixCraft/iBon**: 選擇座位區域（A區/搖滾區） → 點擊區域按鈕
- **KKTIX**: 選擇票種（全票/VIP票） → 輸入票數到輸入框

**關鍵字設定差異**：
```json
// TixCraft/iBon
{"area_keyword": "\"搖滾A區\",\"搖滾B區\""}

// KKTIX
{"area_keyword": "\"全票\",\"VIP票\",\"早鳥票\""}
```

---

## 相關文件

- 📋 [Stage 7: 驗證碼處理機制](../../03-mechanisms/07-captcha-handling.md) - 問答式驗證碼詳解
- 📋 [Stage 5: 區域選擇機制](../../03-mechanisms/05-area-selection.md) - Early Return Pattern
- 🏗️ [程式碼結構分析](../../02-development/structure.md) - KKTIX 函數索引
- 📖 [12-Stage 標準](../../02-development/ticket_automation_standard.md) - 完整流程規範

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：KKTIX 基本功能 |
| v1.1 | 2025-08 | 問答式驗證碼支援 |
| **v1.2** | **2025-11** | **fail_list 機制 + 人類化延遲** |

**v1.2 亮點**：
- ✅ KKTIX 是唯一支援問答式驗證碼的平台
- ✅ fail_list 機制大幅提升成功率
- ✅ 人類化延遲避免機器人偵測
- ✅ 兩階段區域選擇流程完善
