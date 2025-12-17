# Stage 5: 區域選擇機制

**文件說明**：詳細說明搶票系統的區域選擇機制、座位區域匹配與自動選擇策略
**最後更新**：2025-11-12

---

## 概述

**目的**：從可用座位區域列表中選擇目標區域
**輸入**：區域關鍵字（支援 AND 邏輯）+ 選擇模式 + 排除關鍵字
**輸出**：選定的座位區域 + 點擊區域按鈕
**關鍵技術**：
- **Early Return Pattern**（早期返回模式）：優先級驅動的關鍵字匹配
- **Conditional Fallback**（條件回退）：智能回退機制
- **keyword_exclude**（排除關鍵字）：過濾不想要的區域
- **Ticket Availability Check**（票數檢查）：確保座位數量足夠

---

## 核心流程（標準模式）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 取得所有可用區域列表                                      │
│    ├─ 標準 DOM 查詢（TixCraft, KKTIX, TicketPlus, KHAM）    │
│    └─ DOMSnapshot 平坦化（iBon - closed Shadow DOM）        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 過濾不可用選項                                           │
│    ├─ Disabled 按鈕                                         │
│    ├─ 排除關鍵字（keyword_exclude）                        │
│    │   └─ 輪椅區、身障區、視線不完整、Restricted View      │
│    └─ 票數不足選項（ticket_number 檢查）                   │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 關鍵字優先匹配（Early Return Pattern）                   │
│    ├─ 嘗試關鍵字 #1 → 成功？[是] → 立即停止 ✓              │
│    ├─ 嘗試關鍵字 #2 → 成功？[是] → 立即停止 ✓              │
│    ├─ 嘗試關鍵字 #3 → 成功？[是] → 立即停止 ✓              │
│    └─ 所有關鍵字失敗 → 觸發條件回退 ↓                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 條件回退機制（Feature 003）                              │
│    ├─ [area_auto_fallback = true]  → 使用 auto_select_mode │
│    │   ├─ "from top to bottom" → 選第一個                  │
│    │   ├─ "from bottom to top" → 選最後一個                │
│    │   ├─ "center" → 選中間                                │
│    │   └─ "random" → 隨機選擇                              │
│    └─ [area_auto_fallback = false] → 等待手動介入（嚴格模式）│
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 點擊目標區域按鈕                                          │
│    ├─ NoDriver: element.click()                             │
│    ├─ NoDriver fallback: JavaScript click()                 │
│    └─ Chrome: element.click()                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 關鍵程式碼片段

### 1. Early Return Pattern（關鍵字優先匹配）

**範例來源**：TixCraft (`nodriver_tixcraft.py:3048-3061`)

```python
# T011: Early return pattern - iterate keywords in priority order
keyword_matched = False
for keyword_index, area_keyword_item in enumerate(area_keyword_array):
    if show_debug_message:
        print(f"[AREA KEYWORD] Checking keyword #{keyword_index + 1}: {area_keyword_item}")

    # Call helper function to find matching areas
    is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(
        el, config_dict, area_keyword_item
    )

    if not is_need_refresh:
        # T013: Keyword matched log
        keyword_matched = True
        if show_debug_message:
            print(f"[AREA KEYWORD] Keyword #{keyword_index + 1} matched: '{area_keyword_item}'")
        break  # ⭐ Early Return - 立即停止嘗試後續關鍵字

# T014: All keywords failed log
if not keyword_matched and show_debug_message:
    print(f"[AREA KEYWORD] All keywords failed to match")
```

**關鍵設計理念**：
- 關鍵字按優先級排列（第 1 個最優先）
- 一旦匹配成功，**立即停止**，不再嘗試後續關鍵字
- 避免「掃描所有關鍵字再選擇」的舊邏輯
- **T011-T014 標記**：TixCraft 的完整除錯日誌實作

---

### 2. 條件回退機制（Feature 003）

**範例來源**：TixCraft (`nodriver_tixcraft.py:3079-3094`)

```python
# T022-T024: NEW - Conditional fallback based on area_auto_fallback switch
is_fallback_selection = False  # Track selection type for logging
if is_need_refresh and matched_blocks is None:
    if area_auto_fallback:
        # T022: Fallback enabled - use auto_select_mode without keyword
        if show_debug_message:
            print(f"[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
            print(f"[AREA FALLBACK] Selecting available area based on area_select_order='{auto_select_mode}'")
        is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, "")
        is_fallback_selection = True  # Mark as fallback selection
    else:
        # T023: Fallback disabled - strict mode (do not select anything)
        if show_debug_message:
            print(f"[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            print(f"[AREA SELECT] Waiting for manual intervention")
        return False  # 嚴格模式：不選擇，返回失敗，等待手動介入

# T024: Handle case when matched_blocks is empty or None (all options excluded)
if matched_blocks is None or len(matched_blocks) == 0:
    if show_debug_message:
        print(f"[AREA FALLBACK] No available options after exclusion")
    return False
```

**設計決策**：
- **預設值**：`area_auto_fallback = false`（嚴格模式）
- **嚴格模式**（false）：關鍵字失敗時**不自動選擇**，避免誤購不想要的區域
- **自動模式**（true）：關鍵字失敗時，回退到 `auto_select_mode` 選擇可用選項
- **T022-T024 標記**：完整的條件回退邏輯與日誌

---

### 3. keyword_exclude（排除關鍵字）

**範例來源**：TixCraft (`nodriver_tixcraft.py:3194-3197`)

```python
# Filter out unwanted areas using keyword_exclude
if not row_text or util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
    if show_debug_message:
        print(f"[AREA KEYWORD] [{area_index}] Excluded by keyword_exclude")
    continue  # Skip this area
```

**設定格式**（`settings.json`）：
```json
{
  "keyword_exclude": "\"輪椅\",\"身障\",\"身心\",\"障礙\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
}
```

**用途**：
- **輪椅區/身障區**：專為身心障礙者設計的區域
- **Restricted View**：視線受限區域（柱子遮蔽）
- **燈柱遮蔽/視線不完整**：中文描述的視線問題區域

**實作細節**（`util.reset_row_text_if_match_keyword_exclude`）：
```python
def reset_row_text_if_match_keyword_exclude(config_dict, row_text):
    """Check if row_text matches any keyword_exclude patterns"""
    keyword_exclude = config_dict.get("keyword_exclude", "").strip()
    if not keyword_exclude:
        return False  # No exclusion keywords

    try:
        exclude_array = json.loads("[" + keyword_exclude + "]")
        for exclude_keyword in exclude_array:
            if exclude_keyword.lower() in row_text.lower():
                return True  # Match found - exclude this area
    except:
        pass

    return False  # No match - include this area
```

---

### 4. AND 邏輯支援（空格分隔）

**範例來源**：TixCraft (`nodriver_tixcraft.py:3206-3231`)

```python
# Check keyword match with AND logic (space-separated)
if area_keyword_item:
    keyword_parts = area_keyword_item.split(' ')  # Split by space for AND logic

    if show_debug_message:
        print(f"[AREA KEYWORD]   Matching AND keywords: {keyword_parts}")

    # Check each keyword individually for detailed feedback
    match_results = {}
    for kw in keyword_parts:
        formatted_kw = util.format_keyword_string(kw)
        kw_match = formatted_kw in row_text
        match_results[kw] = kw_match

        if show_debug_message:
            status = "PASS" if kw_match else "FAIL"
            print(f"[AREA KEYWORD]     {status} '{kw}': {kw_match}")

    is_match = all(match_results.values())  # ⭐ AND logic - ALL must match

    if show_debug_message:
        if is_match:
            print(f"[AREA KEYWORD]   All AND keywords matched")
        else:
            print(f"[AREA KEYWORD]   AND logic failed")

    if not is_match:
        continue  # Skip this area
```

**設定範例**：
```json
{
  "area_auto_select": {
    "area_keyword": "\"搖滾 A\",\"搖滾 B\",\"搖滾區\""  // OR 邏輯（逗號分隔）
  }
}
```

**AND 邏輯範例**（空格分隔）：
```json
{
  "area_auto_select": {
    "area_keyword": "\"搖滾 A區\",\"搖滾 B區\""  // 每組內部是 AND 邏輯
  }
}
```
解析後：
- 關鍵字 #1: `["搖滾", "A區"]` → 必須同時包含「搖滾」**且**「A區」
- 關鍵字 #2: `["搖滾", "B區"]` → 必須同時包含「搖滾」**且**「B區」

---

### 5. 票數可用性檢查

**範例來源**：TixCraft (`nodriver_tixcraft.py:3237-3258`)

```python
# Check seat availability for multiple tickets
if config_dict["ticket_number"] > 1:
    try:
        font_el = await row.query_selector('font')
        if font_el:
            font_text = await font_el.evaluate('el => el.textContent')
            if font_text:
                font_text = "@%s@" % font_text  # Wrap for exact matching

                if show_debug_message:
                    print(f"[AREA KEYWORD]   Checking seats: {font_text.strip('@')}")

                # Skip if only 1-9 seats remaining (insufficient for multiple tickets)
                SEATS_1_9 = ["@%d@" % i for i in range(1, 10)]
                if any(seat in font_text for seat in SEATS_1_9):
                    if show_debug_message:
                        print(f"[AREA KEYWORD]   Insufficient seats (need {config_dict['ticket_number']}, only {font_text.strip('@')} available)")
                    continue  # Skip this area - not enough seats
                else:
                    if show_debug_message:
                        print(f"[AREA KEYWORD]   Sufficient seats available")
    except:
        pass  # If seat check fails, assume area is available
```

**運作邏輯**：
- **ticket_number = 1**：不檢查（單張票通常都可購買）
- **ticket_number >= 2**：檢查剩餘座位數
  - 剩餘座位 < 10：**跳過此區域**（可能不足）
  - 剩餘座位 >= 10：**可選擇**（足夠）
  - 無法判斷：**預設可選擇**（允許嘗試）

**為什麼是 1-9？**
- TixCraft 在座位不足時會顯示確切數字（1-9）
- 座位充足時顯示「○」或其他符號（不是數字）
- 避免購買 2 張票時選到只剩 1 張的區域

---

## 平台實作差異

| 平台 | 選擇器類型 | Shadow DOM | 特殊處理 | 函數名稱 | 完成度 |
|------|-----------|-----------|---------|---------|--------|
| **TixCraft** | Link list | ❌ 無 | 檢查 `font` 票數資訊 | `nodriver_tixcraft_area_auto_select()` | 100% ✅ |
| **KKTIX** | Price table | ❌ 無 | 兩階段：價格表 + 票數輸入 | `nodriver_kktix_assign_ticket_number()` | 100% ✅ |
| **iBon** | Button list | ✅ Closed | **DOMSnapshot 平坦化**策略 | `nodriver_ibon_area_auto_select()` | 100% ✅ |
| **TicketPlus** | Expansion panel | ❌ 無 | 需先展開 area 面板 | `nodriver_ticketplus_area_auto_select()` | 100% ✅ |
| **KHAM** | Table rows | ❌ 無 | Table mode + Seat map 雙模式 | `nodriver_kham_area_auto_select()` | 100% ✅ |
| **UDN** | Table rows | ❌ 無 | 複用 KHAM 邏輯 (`table.yd_ticketsTable`) | `nodriver_kham_area_auto_select()` | 100% ✅ |

**程式碼位置**（`nodriver_tixcraft.py`）：
- **TixCraft**: Line 2993 (`nodriver_tixcraft_area_auto_select`, 主要參考範例) ⭐
- KKTIX: Line ~1000-1168 (`nodriver_kktix_assign_ticket_number`)
- iBon: Line 9083 (1295 行，Shadow DOM 最複雜範例)
- TicketPlus: Line ~2300-2500 (`nodriver_ticketplus_area_auto_select`)
- KHAM: Line 16790-17213 (`nodriver_kham_area_auto_select`)
- **UDN**: Line 17669-17688 (複用 KHAM 邏輯，Feature 010: 2025-12-17)

---

## 實作檢查清單

- [ ] **關鍵字邏輯**
  - [ ] 支援 AND 邏輯（空格分隔）
  - [ ] 支援 OR 邏輯（逗號分隔）
  - [ ] 實作 Early Return Pattern
  - [ ] 關鍵字優先級遞減匹配

- [ ] **條件回退機制（Feature 003）**
  - [ ] 實作 `area_auto_fallback` 開關
  - [ ] 嚴格模式（false）：不自動選擇
  - [ ] 自動模式（true）：回退到 `auto_select_mode`

- [ ] **過濾機制**
  - [ ] 過濾 disabled 按鈕
  - [ ] 套用排除關鍵字（`keyword_exclude`）
  - [ ] 檢查票數可用性（`ticket_number`）

- [ ] **選擇模式支援**
  - [ ] `from top to bottom`（從第一個）
  - [ ] `from bottom to top`（從最後一個）
  - [ ] `center`（中間）
  - [ ] `random`（隨機）

- [ ] **除錯輸出**
  - [ ] Verbose 模式除錯訊息
  - [ ] 關鍵字匹配日誌（包含 AND 邏輯詳細資訊）
  - [ ] 回退觸發日誌
  - [ ] 票數檢查日誌

- [ ] **錯誤處理**
  - [ ] 無可用區域時的處理
  - [ ] 點擊失敗時的重試機制
  - [ ] 異常捕獲與日誌

---

## 常見問題 (FAQ)

### Q1: 為什麼區域選擇需要 Early Return Pattern？

**A**: 確保**優先級較高的區域關鍵字先被匹配**。

**舊邏輯問題**（已棄用）：
```python
# ❌ 舊邏輯：掃描所有關鍵字，收集所有匹配，再選一個
for keyword in ["搖滾A", "搖滾B", "任意區域"]:
    if keyword matches:
        matched_list.append(...)  # 可能同時匹配多個
# 最後從 matched_list 選一個（無法保證優先級）
```

**新邏輯優勢**：
```python
# ✅ 新邏輯：依序嘗試，第一個成功立即停止
for keyword in ["搖滾A", "搖滾B", "任意區域"]:
    if keyword matches:
        select_immediately()
        break  # 立即停止，不嘗試後續關鍵字
```

**實務案例**：
- 使用者設定：`"\"搖滾A區\",\"搖滾B區\",\"任意區域\""`
- 期望：優先選搖滾A，其次搖滾B，最後才考慮其他
- Early Return 確保：一旦搖滾A可用，立即選擇，不會因為「任意區域」匹配更多而選錯

---

### Q2: keyword_exclude 和 area_keyword 有什麼差別？

**A**:
- **`area_keyword`**：**白名單**（選擇想要的區域）
- **`keyword_exclude`**：**黑名單**（排除不想要的區域）

**執行順序**：
```
1. 取得所有可用區域
2. 套用 keyword_exclude（黑名單） → 移除不想要的
3. 套用 area_keyword（白名單） → 從剩餘中選擇想要的
```

**實務案例**：
```json
{
  "area_keyword": "\"搖滾區\",\"站票\"",  // 白名單：想要搖滾區或站票
  "keyword_exclude": "\"輪椅\",\"身障\",\"Restricted View\""  // 黑名單：不要輪椅區、身障區、視線受限區
}
```

**結果**：
- 即使「搖滾區輪椅席」匹配 `area_keyword`，也會被 `keyword_exclude` 排除
- 確保不會誤選身障專用區域

---

### Q3: 條件回退什麼時候觸發？

**A**: 當**所有區域關鍵字都無法匹配**時，根據 `area_auto_fallback` 設定決定行為。

**觸發條件**：
```python
if is_need_refresh and matched_blocks is None:
    # 有設定關鍵字，但都沒匹配 → 觸發條件回退
```

**行為**：
1. **`area_auto_fallback = false`（預設）**：
   - 返回 `False`
   - 不選擇任何區域
   - 等待使用者手動介入
   - **用途**：避免誤購不想要的區域

2. **`area_auto_fallback = true`**：
   - 使用 `auto_select_mode` 從可用選項中選擇
   - 自動完成購票流程
   - **用途**：「只要能買到票就好」的場景

---

### Q4: AND 邏輯如何使用？

**A**: 使用**空格分隔**關鍵字，實現「必須同時包含」的邏輯。

**範例 1：單一關鍵字（OR 邏輯）**
```json
{
  "area_keyword": "\"搖滾A區\",\"搖滾B區\",\"搖滾C區\""
}
```
解析結果：`["搖滾A區", "搖滾B區", "搖滾C區"]`
- 匹配其中**任一個**即可（OR 邏輯）

**範例 2：AND 邏輯（空格分隔）**
```json
{
  "area_keyword": "\"搖滾 A區\",\"搖滾 B區\""
}
```
解析結果：`[["搖滾", "A區"], ["搖滾", "B區"]]`
- 關鍵字 #1：必須**同時包含**「搖滾」**且**「A區」
- 關鍵字 #2：必須**同時包含**「搖滾」**且**「B區」

**實務應用**：
- **避免誤選**：`"搖滾 特別 加演"` → 只選「搖滾特別加演場」，不選普通「搖滾場」
- **精確匹配**：`"A區 前排"` → 只選「A區前排」，不選「A區後排」

**除錯日誌範例**：
```
[AREA KEYWORD] Checking keyword #1: 搖滾 A區
[AREA KEYWORD]   Matching AND keywords: ['搖滾', 'A區']
[AREA KEYWORD]     PASS '搖滾': True
[AREA KEYWORD]     PASS 'A區': True
[AREA KEYWORD]   All AND keywords matched
```

---

## 相關文件

- 📋 [Feature 003: Keyword Priority Fallback](../../specs/003-keyword-priority-fallback/implementation-guide.md) - 完整實作指南
- 📊 [規格驗證矩陣](../04-validation/spec-validation-matrix.md) - FR-020, FR-021, FR-022
- 🔧 [TixCraft 參考實作](../03-implementation/platform-examples/tixcraft-reference.md) - 主要參考範例
- 🔧 [KKTIX 參考實作](../03-implementation/platform-examples/kktix-reference.md) - 價格表模式
- 🔧 [iBon 參考實作](../03-implementation/platform-examples/ibon-reference.md) - Shadow DOM 範例
- 📖 [12-Stage 標準](../02-development/ticket_automation_standard.md) - 完整 12 階段流程
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 函數位置索引

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2024 | 初版：基本區域選擇邏輯 |
| v1.1 | 2025-10 | 新增 AND 邏輯支援 + keyword_exclude |
| **v1.2** | **2025-11** | **Feature 003: Early Return + Conditional Fallback** |

**v1.2 重大變更**：
- ✅ 實作 Early Return Pattern（優先級驅動）
- ✅ 實作條件回退機制（`area_auto_fallback` 開關）
- ✅ 預設改為嚴格模式（避免誤購不想要的區域）
- ✅ 強化票數可用性檢查（避免票數不足）
- ✅ 統一所有平台的關鍵字解析邏輯
