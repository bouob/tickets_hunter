**文件說明**：ibon NoDriver 日期選擇關鍵字匹配問題的除錯分析報告，涵蓋問題診斷、根本原因與修復建議。

**最後更新**：2025-11-12

---

# 除錯分析報告 - ibon NoDriver 日期選擇未根據關鍵字匹配

## 🎯 執行摘要

**分析時間**: 2025-10-20
**執行模式**: 標準模式
**分析對象**: ibon (NoDriver) - 階段 4 (日期選擇)

**關鍵發現**:
- ❌ **P0 (CRITICAL)**: 1 個
  - **完全缺失關鍵字匹配邏輯** - ibon ActivityInfo 頁面未實作關鍵字匹配,直接使用 auto_select_mode 選擇按鈕
- ⚠️ **P1 (HIGH)**: 2 個
  - 違反 FR-017 需求(關鍵字匹配)
  - 違反 FR-018 需求(關鍵字回退邏輯)

**建議行動**(依優先級排序):
1. 【立即】實作日期關鍵字匹配邏輯 - 預估時間: 2-3 小時
2. 【立即】實作回退策略(關鍵字 → auto_select_mode) - 預估時間: 30 分鐘
3. 【今日】新增日期文字提取與匹配日誌輸出 - 預估時間: 30 分鐘

**預估修復時間**: 3-4 小時

---

## 問題概述
- **問題描述**: 在 ibon ActivityInfo/Details 頁面(https://ticket.ibon.com.tw/ActivityInfo/Details/39125),儘管 settings.json 設定了 `date_keyword: "12/13"`,程式仍未根據關鍵字選擇對應的場次,而是直接點擊第一個購買按鈕(10/25 台北場)
- **功能階段**: 階段 4 - 日期選擇
- **涉及平台**: ibon (NoDriver)
- **涉及函數**: `nodriver_ibon_date_auto_select()` (nodriver_tixcraft.py:L6315-6500)

---

## 根因分析

### 主要原因

**函數 `nodriver_ibon_date_auto_select()` 完全缺失關鍵字匹配邏輯**:

1. **現狀**: 程式僅根據 `auto_select_mode` (from top to bottom) 選擇第一個可用按鈕
2. **缺失**: 沒有提取購買按鈕關聯的日期文字 (如 "2025/10/25", "2025/12/13")
3. **缺失**: 沒有將 `date_keyword: "12/13"` 與日期文字進行匹配
4. **缺失**: 沒有實作「關鍵字匹配 → 回退到 auto_select_mode」的三層策略

### 日誌證據

從 `.temp/manual_logs.txt` (Line 24-40):
```
[IBON DATE] Starting date selection on ActivityInfo/Details page
date_keyword: "12/13"            ← 關鍵字已正確讀取
auto_select_mode: from top to bottom
[IBON DATE] Found 2 purchase button(s)
[IBON DATE] Found 2 enabled button(s)
[IBON DATE] Selected target button:  ← 直接選擇第一個,未進行關鍵字匹配
[IBON DATE] Button node_id: NodeId(119)
[IBON DATE] Purchase button clicked successfully
```

### HTML 結構證據

從 `.temp/bug1.html` 提取的實際場次資訊:
```html
<!-- 場次 1: 台北場 -->
<p class="flex-fill date">2025/10/25(六) 18:00</p>
<button class="btn btn-pink btn-buy">線上購票</button>

<!-- 場次 2: 高雄場 (符合關鍵字 "12/13") -->
<p class="flex-fill date">2025/12/13(六) 16:00</p>
<button class="btn btn-pink btn-buy">線上購票</button>
```

**期望行為**: 應選擇第二個按鈕(12/13 高雄場)
**實際行為**: 選擇了第一個按鈕(10/25 台北場)

---

## Spec 檢查結果

### 相關功能需求
| 需求 ID | 需求內容 | 符合度 | 備註 |
|---------|---------|--------|------|
| FR-017 | 系統必須使用配置的關鍵字匹配日期,並支援多個分號分隔的關鍵字 | ❌ 不符合 | **完全未實作**關鍵字匹配邏輯 |
| FR-018 | 系統必須在關鍵字不匹配時回退到基於模式的選擇(從上/下/中間/隨機) | ❌ 不符合 | 未實作三層回退策略 |
| FR-014 | 系統必須偵測日期選擇佈局類型(按鈕、下拉選單、日曆) | ✅ 部分符合 | 已偵測按鈕型佈局 |

### 相關成功標準
| 標準 ID | 標準內容 | 目標 | 現狀 | 達標? |
|---------|---------|------|------|-------|
| SC-002 | 系統在可用時成功選擇使用者的第一選擇日期和區域 | 90% | **0%**(ibon ActivityInfo 頁面) | ❌ |
| SC-005 | 元素互動成功率 | 95% | 100% (按鈕點擊成功) | ✅ |

### 設計原則檢查
- **配置驅動架構**: ⚠️ 部分符合 - 已讀取 `date_keyword` 但未使用
- **三層回退策略**: ❌ 不符合 - 直接跳到回退策略,跳過關鍵字匹配
- **函數分解原則**: ✅ 符合 - 函數結構清晰
- **平台特定考量**: ⚠️ 需補充 - ibon ActivityInfo 頁面的特殊處理未記錄

---

## 憲法合規性

### 違反項目(按優先級排序)

| 原則 | 項目 | 嚴重性 | 說明 | 對應行號 |
|------|------|--------|------|---------|
| **II. 資料結構優先** | 未完整實作 FR-017/FR-018 設計需求 | P0 | 違反 Spec 定義的核心功能需求 | nodriver_tixcraft.py:L6315-6440 |
| **V. 設定驅動開發** | 已讀取 config 但未使用 `date_keyword` | P0 | 違反配置驅動原則 | nodriver_tixcraft.py:L6323, L6429-6436 |
| **III. 三問法則** | 缺失核心功能(關鍵字匹配) | P1 | 「是核心問題嗎?」- 是,影響使用者購票準確性 | - |
| **VI. 測試驅動穩定性** | 缺乏測試覆蓋 | P1 | ibon ActivityInfo 頁面的關鍵字匹配未經測試驗證 | - |

### 通過項目
- ✅ **I. NoDriver First** - 已優先實作 NoDriver 版本
- ✅ **IV. 單一職責** - 函數職責明確,長度適中(~180 行)
- ✅ **Emoji 規範** - 無 emoji 違規
- ✅ **暫停機制** - 未涉及此邏輯

---

## 修復建議

### 優先級 P0 修復(必須 - 立即執行)

**1. 實作日期關鍵字匹配邏輯**

**涉及檔案**: `src/nodriver_tixcraft.py`
**涉及行號**: L6410-6436 (在按鈕選擇邏輯前插入)
**修復方向**:

```python
# 步驟 1: 提取每個按鈕關聯的日期文字
# 透過 DOM 樹遍歷,找到每個 BUTTON 的前置 <p class="date"> 元素
for i, button in enumerate(purchase_buttons):
    # 向前搜尋相鄰的 TEXT 節點或 P 元素
    date_text = extract_date_text_for_button(button, node_names, node_values, i)
    button['date_text'] = date_text  # 例: "2025/10/25(六) 18:00"

# 步驟 2: 關鍵字匹配邏輯
matched_buttons = []
if date_keyword:
    keywords = [k.strip(' "').strip() for k in date_keyword.split(',')]
    for button in enabled_buttons:
        for keyword in keywords:
            if keyword in button.get('date_text', ''):
                matched_buttons.append(button)
                break

# 步驟 3: 三層回退策略
if matched_buttons:
    # 主策略: 使用關鍵字匹配結果
    if show_debug_message:
        print(f"[IBON DATE] Keyword matched {len(matched_buttons)} button(s)")
    target_list = matched_buttons
else:
    # 回退策略: 使用 auto_select_mode
    if show_debug_message:
        print(f"[IBON DATE] No keyword match, using auto_select_mode")
    target_list = enabled_buttons

# 步驟 4: 根據 auto_select_mode 從 target_list 選擇
if auto_select_mode == "random":
    target_button = random.choice(target_list)
elif auto_select_mode == "from bottom to top":
    target_button = target_list[-1]
elif auto_select_mode == "center":
    target_button = target_list[len(target_list) // 2]
else:  # from top to bottom (default)
    target_button = target_list[0]
```

**相關 Spec**: FR-017, FR-018, SC-002
**相關憲法原則**: II. 資料結構優先, V. 設定驅動開發
**參考實作**: `nodriver_tixcraft_date_auto_select()` (L2288-2450) 的關鍵字匹配邏輯

**測試驗證**:
- [ ] 測試 `date_keyword: "12/13"` 成功選擇 12/13 場次
- [ ] 測試 `date_keyword: "10/25"` 成功選擇 10/25 場次
- [ ] 測試空關鍵字 `date_keyword: ""` 回退到 auto_select_mode
- [ ] 測試無匹配關鍵字 `date_keyword: "99/99"` 回退到 auto_select_mode

---

### 優先級 P1 修復(重要 - 今日完成)

**2. 新增日期文字提取與日誌輸出**

**涉及檔案**: `src/nodriver_tixcraft.py`
**涉及行號**: L6408-6410 (在 `Found button` 日誌後)
**修復方向**:

```python
# 在找到按鈕後,立即輸出其關聯的日期文字
if show_debug_message:
    print(f"[IBON DATE] Found button: class='{button_class[:50]}...', disabled={button_disabled}, date_text='{button['date_text']}'")
```

**相關憲法原則**: VIII. 文件與代碼同步
**測試驗證**:
- [ ] 日誌輸出包含每個按鈕的日期文字
- [ ] 日誌顯示關鍵字匹配結果(匹配數量)

---

### 優先級 P2 修復(改進 - 本週完成)

**3. 更新文件記錄平台特定行為**

**涉及檔案**: `specs/001-ticket-automation-system/spec.md`
**涉及行號**: 平台特定考量區塊(需搜尋 "ibon")
**修復方向**: 新增以下說明

```markdown
### iBon 平台特定考量
- **ActivityInfo/Details 頁面**:
  - 日期以 `<p class="flex-fill date">` 顯示(如 "2025/12/13(六) 16:00")
  - 購買按鈕為 Shadow DOM 中的 `<button class="btn-buy">`
  - 需透過 DOM 樹遍歷將日期文字與按鈕關聯
```

**相關憲法原則**: VIII. 文件與代碼同步

---

## 測試計畫

### 測試對象
- 函數: `nodriver_ibon_date_auto_select()` (nodriver_tixcraft.py:L6315)
- 平台: ibon (NoDriver)
- 階段: 階段 4 - 日期選擇

### 快速測試指令(複製即用)

**NoDriver 版本測試**(Git Bash):
```bash
cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter" && \
> .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**檢查輸出**(驗證關鍵字匹配):
```bash
grep -i "IBON DATE.*keyword\|Selected target button" .temp/test_output.txt
```

**預期輸出**(修復後):
```
[IBON DATE] date_keyword: "12/13"
[IBON DATE] Found button: date_text='2025/10/25(六) 18:00'
[IBON DATE] Found button: date_text='2025/12/13(六) 16:00'
[IBON DATE] Keyword matched 1 button(s)
[IBON DATE] Selected target button: 2025/12/13(六) 16:00
```

### 驗證標準(根據 SC-xxx)
- [ ] SC-002: 關鍵字 "12/13" 成功匹配並選擇 12/13 場次(達到 90% 成功率目標)
- [ ] FR-017: 支援分號分隔的多關鍵字(如 "10/25;12/13")
- [ ] FR-018: 無匹配時回退到 auto_select_mode

### 手動測試檢查點
- [ ] 設定 `date_keyword: "12/13"`,驗證選擇高雄場(12/13)
- [ ] 設定 `date_keyword: "10/25"`,驗證選擇台北場(10/25)
- [ ] 設定 `date_keyword: ""`,驗證回退到 auto_select_mode (第一個按鈕)
- [ ] 設定 `date_keyword: "99/99"`,驗證回退到 auto_select_mode

### 迴歸測試
- 需要檢查其他平台是否受影響: **否**(此修改僅影響 `nodriver_ibon_date_auto_select()`)
- 需要檢查其他功能是否受影響: **否**

---

## 文件更新需求

修復完成後,需更新以下文件:

- [ ] `specs/001-ticket-automation-system/spec.md` - 新增 iBon ActivityInfo 頁面的平台特定考量
- [ ] `docs/02-development/structure.md` - 更新函數行號(如有新增函數)
- [ ] `docs/08-troubleshooting/README.md` - 新增「ibon 日期關鍵字匹配失敗」問題記錄
- [ ] `CHANGELOG.md` - 記錄修復(版本發佈時)

---

## 建議的下一步

1. **立即行動**(P0 修復):
   - 實作日期關鍵字匹配邏輯(2-3 小時)
   - 實作三層回退策略(30 分鐘)

2. **短期行動**(P1 修復):
   - 新增日期文字提取與日誌輸出(30 分鐘)
   - 執行完整測試計畫(1 小時)

3. **長期改進**(P2 修復):
   - 更新文件記錄平台特定行為(30 分鐘)
   - 檢討其他平台是否有類似缺失

---

*分析日期*: 2025-10-20
*分析工具*: /debug
*執行模式*: 標準模式
*相關憲法版本*: 1.0.0
*相關規格版本*: specs/001-ticket-automation-system/spec.md (2025-10-16)
