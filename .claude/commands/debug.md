---
description: 統合 Spec 檢查、憲法合規驗證、代碼定位的專業除錯工具 - 快速識別 bug 根因並生成結構化分析報告
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入(如果不為空)。

---

## 目標

在除錯階段快速識別問題的根本原因,透過驗證功能是否符合規格需求(Spec-Driven Debugging)、是否遵守專案憲法、以及代碼結構檢查,生成結構化的分析報告並提出修復建議。

此命令專為**已出現 bug 或功能異常**的情況設計(不同於 `/speckit.clarify` 的規格澄清或 `/speckit.analyze` 的規格一致性檢查)。

---

## 操作約束

**嚴格唯讀**：不修改任何檔案,僅進行分析與診斷。提供結構化報告與可操作的修復建議。

**憲法為主導**：項目憲章(`.specify/memory/constitution.md`)是修復方向的最高指導原則。所有建議必須確保符合憲章要求。

**Spec 驅動分析**：所有檢查必須追溯到規格需求(Spec §FR-xxx, SC-xxx),確保修復符合原始設計意圖。

---

## 執行步驟

### 0. 參數解析與模式選擇

#### A. 參數解析

從使用者輸入中提取結構化資訊:

**支援的參數格式**:
- `[platform:平台名稱]` - 指定平台(例: `[platform:ibon]`)
- `[function:函數名稱]` - 指定函數(例: `[function:nodriver_ibon_date_auto_select]`)
- `[error:"錯誤訊息"]` - 提供錯誤訊息(例: `[error:"找不到日期選擇按鈕"]`)
- `[stage:階段編號]` - 指定 12 階段中的階段(例: `[stage:4]`)
- 自然語言描述 - 任何不含 `[key:value]` 格式的文字

**參數範例**:
```
/debug [platform:ibon] [function:nodriver_ibon_date_auto_select] [error:"關鍵字無法匹配"]
/debug 日期選擇失敗,關鍵字無法匹配
/debug --quick 快速檢查憲法違規
/debug --deep ibon 座位選擇跨平台問題分析
```

**解析規則**:
- 若有 `[key:value]` 格式 → 提取為結構化參數
- 若有 `--quick` 標記 → 啟用快速模式
- 若有 `--deep` 標記 → 啟用深度模式
- 其餘部分 → 視為自然語言描述

#### B. 模式選擇

根據參數充足度與使用者指定,選擇執行模式:

**快速模式(`--quick` 或參數充足時)**:
- **執行範圍**: 層 2(憲法合規) + 層 4(已知問題比對)
- **跳過內容**: Spec 詳細追溯、跨平台版本比對
- **報告格式**: 簡化報告(僅列出 P0/P1 問題)
- **執行時間**: < 1 分鐘
- **適用情境**: 緊急 debug、已知問題快速驗證

**標準模式(預設)**:
- **執行範圍**: 完整 5 層檢查(Spec → 憲法 → 代碼 → 已知問題 → 跨平台)
- **報告格式**: 完整結構化報告
- **執行時間**: 2-3 分鐘
- **適用情境**: 一般 debug、新問題診斷

**深度模式(`--deep` 或檢測到複雜問題時)**:
- **執行範圍**: 標準模式 + 跨平台版本比對 + 歷史問題模式搜尋 + 依賴關係影響分析
- **報告格式**: 詳細報告(包含相似實作參考、歷史修復記錄)
- **執行時間**: 5-10 分鐘
- **適用情境**: 架構性問題、多平台影響、複雜錯誤

**自動判斷規則**:
- 若參數包含 `platform` + `function` + `error` → 建議快速模式
- 若參數包含「跨平台」、「架構」、「設計」等關鍵字 → 建議深度模式
- 若參數模糊或僅自然語言描述 → 使用標準模式
- 使用者可明確指定 `--quick` 或 `--deep` 覆蓋自動判斷

---

### 1. 初始化分析情境

從專案根目錄執行 `{SCRIPT}` 並解析 JSON 以取得:

**執行指令**:
- Bash: `scripts/bash/check-prerequisites.sh --json --paths-only`
- PowerShell: `scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly`

**自動取得路徑**:
- FEATURE_DIR: 功能分支目錄
- FEATURE_SPEC: FEATURE_DIR/spec.md
- IMPL_PLAN: FEATURE_DIR/plan.md
- CONSTITUTION: .specify/memory/constitution.md
- STRUCTURE: docs/02-development/structure.md
- DEBUGGING_GUIDE: docs/04-testing-debugging/debugging_methodology.md
- TROUBLESHOOTING_INDEX: docs/05-troubleshooting/README.md

**參數處理**(處理單引號):
- 若參數包含單引號(如 "I'm")
- 使用跳脫語法: 'I'\''m Groot'
- 或使用雙引號: "I'm Groot"

**失敗處理**:
- 若 JSON 解析失敗 → 中止並提示使用者檢查環境
- 若關鍵檔案缺失 → 列出缺失檔案並建議修復指令

如果任何關鍵檔案缺失,中止並指示使用者。

---

### 2. 釐清 Debug 情境(智慧推薦)

根據使用者輸入或步驟 0 解析的參數,推導分析重點。

#### A. 自動推導規則

**參數 → 自動定位**:
- `platform:xxx` → 自動定位平台文件(nodriver_xxx.py、chrome_xxx.py)
- `function:xxx` → 直接從 structure.md 定位函數行號
- `error:"..."` → 自動搜尋已知問題模式(troubleshooting/)
- `stage:N` → 直接定位到 12 階段中的階段 N

**關鍵字 → 階段映射**:
```
日期選擇、date_keyword → 階段 4
區域選擇、area_keyword、座位 → 階段 5
票數、ticket_number → 階段 6
驗證碼、OCR、captcha → 階段 7
表單填寫、user_guess_string → 階段 8
Cookie、登入、authentication → 階段 2
元素點擊、找不到元素 → 檢查階段 4-10(互動密集階段)
```

**推導範例**:
```
👤 輸入: /debug [platform:ibon] 日期選擇關鍵字無法匹配

🤖 自動推導:
   ✓ 平台: ibon
   ✓ 階段: 階段 4(日期選擇)
   ✓ 相關函數: nodriver_ibon_date_auto_select (structure.md:L2341)
   ✓ 相關 FR: FR-017, FR-018
   ✓ 相關 SC: SC-002
   ✓ 可能原因: 關鍵字匹配邏輯、context 提取、回退策略
```

#### B. 互動式提問(僅在推導不足時)

**限制**: 最多 2 個精準問題(而非 3 個)

**每個問題的格式**:
1. **分析所有可能原因**,根據最佳實踐判斷**最可能的原因**
2. **推薦答案置頂**,格式為: `**推薦**: 選項 [X] - [1-2 句推薦原因]`
3. 列出所有選項(Markdown 表格或清單)
4. 提示: 「回覆 'yes' 或 'recommended' 接受推薦,或回覆選項字母/自定義答案」

**問題範例**:

**問題 Q1: 問題具體現象**

**推薦**: 選項 A - 根據 ibon 平台常見問題模式,關鍵字匹配失敗是最常見的日期選擇問題。

| 選項 | 描述 |
|-----|------|
| A | 關鍵字無法匹配日期 |
| B | 找不到日期選擇元素(DOM 結構問題) |
| C | 回退策略失敗(auto_select_mode) |
| D | 其他(請簡述,<=10 字) |

回覆 "A"、"yes" 接受推薦,或提供自定義答案。

**使用者回應處理**:
- 回覆 "yes"、"recommended" → 採用推薦答案
- 回覆選項字母(A/B/C) → 採用該選項
- 回覆自定義文字 → 記錄為自定義答案
- 若仍模糊 → 快速追問釐清(不計入新題)

**提前終止條件**:
- 參數已充足(自動推導完成所有必要資訊)
- 使用者明確表示完成(「done」、「good」、「no more」)
- 已詢問 2 題

**無問題時的行為**:
- 若自動推導已完全覆蓋必要資訊 → 輸出「已自動推導完成,跳過提問」
- 立即進入步驟 3

---

### 3. 建立分析框架

#### A. 功能階段定位

根據用戶輸入或自動推導,判斷屬於 12 階段中的哪個:

```
1. 環境初始化      7. 驗證碼處理
2. 身份認證        8. 表單填寫
3. 頁面監控與重載  9. 同意條款處理
4. 日期選擇        10. 訂單確認送出
5. 區域/座位選擇   11. 排隊與付款
6. 票數設定        12. 錯誤處理與重試
```

#### B. 相關文件載入

根據階段和使用者輸入,載入:

**從 spec.md**:
- 相關功能需求(FR-xxx) - 搜尋問題相關的關鍵詞
- 相關成功標準(SC-xxx) - 對應的可測量目標
- 核心設計原則 - 適用的設計約束
- 平台特定考量 - 是否有平台特定的實作細節

**從 constitution.md**:
- 9 大核心原則(尤其是 III. 三問法則、II. 資料結構優先、VI. 測試驅動穩定性)
- Code Review 標準(Line 329-376) - 必檢項目
- [NoDriver] 特定檢查 - 暫停機制、Emoji 規範

**從 structure.md**:
- 函數索引 - 定位問題函數的行號
- 功能完整度評分 - 該平台的實作狀態
- TODO 標記清查 - 已知未完成項

**從 debugging_methodology.md**:
- Spec 驅動除錯方法(Line 389-510) - 除錯檢查清單
- 常見問題解決模式 - 相似問題的已知解決方案

---

### 4. 快速除錯檢查

根據問題自動執行快速檢查（著重於除錯而非完整開發分析）：

#### 快速檢查清單

**Spec 快速驗證**:
- 在 spec.md 搜尋相關的 FR-xxx（功能需求）和 SC-xxx（成功標準）
- 驗證：功能是否符合原始設計？是否達到成功標準？

**憲法合規檢查（必要）**:
- ❌ **P0 嚴重違規（NON-NEGOTIABLE）**:
  - Emoji 規範: 程式碼(.py, .js)中禁止 emoji
  - NoDriver 暫停機制: 必須使用 `check_and_handle_pause()`, `sleep_with_pause_check()`, `asyncio_sleep_with_pause_check()`
- ⚠️ **P1 重要原則**:
  - 設定驅動: 使用 config_dict 而非硬編碼
  - NoDriver First: 優先實作 NoDriver 版本
  - 三問法則: 核心問題？簡單方法？相容性？

**已知問題比對**:
- Unicode 編碼錯誤(cp950) - 是否使用了 emoji?
- Disabled 按鈕檢測 - 是否過濾了 disabled 元素?
- Shadow DOM 穿透 - 是否使用了正確策略?
- Angular 載入時機 - 是否正確等待?

**函數定位**:
- 從 structure.md 定位函數行號
- 檢查是否存在 Chrome/NoDriver 版本差異

---

### 5. 嚴重性與優先度評估(整合憲法)

根據以下映射規則評估發現事項:

#### 憲法-優先級映射表

| 憲法原則 | 違規類型 | 自動優先級 |
|---------|---------|-----------|
| **Emoji 規範(NON-NEGOTIABLE)** | 程式碼(.py, .js)中使用 emoji | **P0 (CRITICAL)** |
| **NoDriver 暫停機制(NON-NEGOTIABLE)** | 未使用 check_and_handle_pause()、sleep_with_pause_check() | **P0 (CRITICAL)** |
| **I. NoDriver First** | 新功能選擇 Chrome 優先於 NoDriver | **P0 (CRITICAL)** |
| **II. 資料結構優先** | 繞過 data-model.md 直接實作 | **P0 (CRITICAL)** |
| **III. 三問法則** | 未記錄決策審視(spec/plan 缺失) | **P1 (HIGH)** |
| **V. 設定驅動開發** | 硬編碼而非使用 settings.json | **P1 (HIGH)** |
| **VI. 測試驅動穩定性** | 核心修改無測試 | **P1 (HIGH)** |
| **Spec 成功標準** | 無法達到 SC-xxx 標準(如 90% 成功率) | **P1 (HIGH)** |
| **IV. 單一職責** | 函數超過 50 行 | **P2 (MEDIUM)** |
| **VIII. 文件同步** | 函數新增但未更新 structure.md | **P2 (MEDIUM)** |
| **Spec 部分符合** | 部分實作 FR-xxx 需求 | **P2 (MEDIUM)** |
| **程式碼風格** | 命名不規範、註解缺失 | **P3 (LOW)** |

#### 優先級定義(與憲法同步)

- **P0 (CRITICAL)**:
  - 違反憲法 NON-NEGOTIABLE 項目(Emoji、暫停機制)
  - 破壞 MVP 核心流程
  - 影響所有平台的共用工具(util.py)

- **P1 (HIGH)**:
  - 違反憲法的「必須」原則(三問法則、NoDriver First、設定驅動)
  - 無法達到 SC-xxx 成功標準
  - 影響單一平台的完整功能

- **P2 (MEDIUM)**:
  - 部分符合 Spec 需求
  - 程式碼品質問題(TODO、複雜度過高)
  - 文件未更新

- **P3 (LOW)**:
  - 風格改進
  - 性能優化建議
  - 可選功能補強

---

### 6. 生成除錯報告（精簡版）

輸出聚焦於除錯的簡化報告（Markdown 格式）:

```markdown
# 除錯分析報告

## 🎯 問題概述

**分析時間**: [生成時間]
**平台**: [平台名稱]
**功能階段**: [12 階段中的哪一個]
**涉及函數**: [函數名稱:行號] (來自 structure.md)
**問題描述**: [用戶提供的問題描述]

---

## 🔍 關鍵發現

**憲法合規檢查**:
- ❌ **P0 違規（立即修復）**: [數量] 個
  - [問題簡述 1 + 對應行號]
- ⚠️ **P1 重要**: [數量] 個
  - [問題簡述 + 對應行號]
- ⚠️ **P2 改進**: [數量] 個

**Spec 符合度**:
- FR-xxx: [✅/⚠️/❌] [簡短說明]
- SC-xxx: [✅/❌] [目標 vs 現狀]

**已知問題比對**:
- [匹配的已知問題] → [建議解決方案連結]

---

## 🛠️ 根因分析

**主要原因**: [簡短描述，1-2 句]

**可能原因**:
- [原因 1]
- [原因 2]

---

## ✅ 修復建議（依優先級）

### P0 - 立即修復（違反憲法 NON-NEGOTIABLE）
1. **[問題標題]**
   - 檔案: `file.py:L234`
   - 修復: [簡短描述]
   - 憲法原則: [相關原則]

### P1 - 今日修復（重要原則）
2. **[問題標題]**
   - 檔案: `file.py:L456`
   - 修復: [簡短描述]
   - 參考: [其他平台實作]

### P2 - 本週改進
3. **[問題標題]**
   - 檔案: `file.py:L789`
   - 修復: [簡短描述]

---

## 測試計畫

### 測試對象
- 函數: [函數名稱:行號]
- 平台: [平台名稱]
- 階段: [12 階段中的哪一個]

### 快速測試指令（複製即用）

#### 可用的命令列參數（覆蓋 settings.json）

**常用參數（除錯測試首選）** ⭐:

| 參數名稱 | 覆蓋設定路徑 | 用途 | 範例值 |
|---------|-------------|------|--------|
| `--date_keyword` | `date_auto_select.date_keyword` | 日期關鍵字 | `"12/25"` |
| `--date_auto_select_mode` | `date_auto_select.mode` | 日期選擇模式 | `from top to bottom` |
| `--area_keyword` | `area_auto_select.area_keyword` | 區域關鍵字 (NoDriver) | `"搖滾區"` |
| `--area_auto_select_mode` | `area_auto_select.mode` | 區域選擇模式 (NoDriver) | `from bottom to top` |
| `--ticket_number` | `ticket_number` | 覆蓋票數 | `2` |

**進階參數（少用，僅特殊需求）**:

| 參數名稱 | 覆蓋設定路徑 | 用途 | 範例值 |
|---------|-------------|------|--------|
| `--headless` | `advanced.headless` | 無頭模式 | `true` / `false` |
| `--homepage` | `homepage` | 覆蓋首頁網址 | `https://tixcraft.com/...` |
| `--browser` | `browser` | 覆蓋瀏覽器選擇 | `chrome` |
| `--window_size` | `advanced.window_size` | 視窗大小 | `1920,1080` |
| `--proxy_server` | `advanced.proxy_server_port` | 代理伺服器 | `127.0.0.1:8080` |
| `--tixcraft_sid` | `advanced.tixcraft_sid` | TixCraft Cookie（進階） | `abc123...` |
| `--ibonqware` | `advanced.ibonqware` | ibon Cookie（進階） | `mem_id=...` |

**選擇模式可用值**:
- `random` - 隨機選擇
- `center` - 中間選擇
- `from top to bottom` - 由上至下
- `from bottom to top` - 由下至上

#### 基本測試指令

**NoDriver 版本測試**（30秒自動終止）:
\```bash
cd "D:/Desktop/MaxBot搶票機器人/tickets_hunter" && \
> .temp/test_output.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
\```

#### 除錯專用：命令列參數覆蓋範例

**常用測試（日期/區域關鍵字）** ⭐:

**1. 測試特定日期關鍵字**（最常用）:
\```bash
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --date_keyword "12/25" > .temp/test_output.txt 2>&1
\```

**2. 測試特定區域關鍵字**（最常用）:
\```bash
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --area_keyword "搖滾區" > .temp/test_output.txt 2>&1
\```

**3. 測試日期與區域組合**（最常用）:
\```bash
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --date_keyword "12/25" \
  --area_keyword "VIP" > .temp/test_output.txt 2>&1
\```

**4. 測試不同選擇模式**（常用）:
\```bash
# 由下至上選擇（區域）
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --area_auto_select_mode "from bottom to top" > .temp/test_output.txt 2>&1

# 隨機選擇（日期）
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --date_auto_select_mode "random" > .temp/test_output.txt 2>&1
\```

**進階測試（少用，特殊情境）**:

**5. 測試 Cookie 設定**（ibon/tixcraft 專用）:
\```bash
# ibon Cookie
timeout 30 python -u src/nodriver_ibon.py --input src/settings.json \
  --ibonqware "mem_id=xxxxx..." > .temp/test_output.txt 2>&1

# tixcraft Cookie
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --tixcraft_sid "abc123..." > .temp/test_output.txt 2>&1
\```

**6. 測試票數設定**:
\```bash
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --ticket_number 4 > .temp/test_output.txt 2>&1
\```

**7. 組合多個參數**（完整測試）:
\```bash
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json \
  --ticket_number 2 \
  --date_keyword "12/25" \
  --area_keyword "搖滾區" \
  --area_auto_select_mode "from top to bottom" > .temp/test_output.txt 2>&1
\```

#### 檢查測試結果

**查看完整輸出**:
\```bash
cat .temp/test_output.txt
\```

**快速檢查錯誤**:
\```bash
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt
\```

**檢查關鍵字匹配**:
\```bash
# 日期關鍵字
grep -i "date_keyword\|Date Context" .temp/test_output.txt

# 區域關鍵字
grep -i "area_keyword\|Area Context" .temp/test_output.txt
\```

**檢查 CDP 點擊（NoDriver）**:
\```bash
grep -i "CDP NATIVE\|resolveNode" .temp/test_output.txt
\```

### 驗證標準(根據 SC-xxx)
- [ ] SC-002: 關鍵字匹配成功率達到 90%
- [ ] SC-005: 元素互動成功率達到 95%
- [ ] [其他相關成功標準]

### 手動測試檢查點
- [ ] [具體可測量目標 1]
- [ ] [具體可測量目標 2]
- [ ] [具體可測量目標 3]

### 迴歸測試
- 需要檢查其他平台是否受影響: [清單]
- 需要檢查其他功能是否受影響: [清單]

---

## 文件更新需求

- [ ] `docs/02-development/structure.md` - 函數行號更新
- [ ] `docs/05-troubleshooting/` - 問題記錄(若為新問題)
- [ ] `docs/04-testing-debugging/debugging_methodology.md` - 新發現記錄
- [ ] `CHANGELOG.md` - 版本記錄(修復完成後)
- [ ] 相關平台文件 - [列表]

---

## 相關資源

**Spec 檢查深入閱讀**:
- `specs/001-ticket-automation-system/spec.md` - Line [相關行號]
- 功能需求區塊、成功標準區塊、核心設計原則區塊

**憲法相關條款**:
- `.specify/memory/constitution.md` - [相關原則]

**代碼定位**:
- `nodriver_tixcraft.py` - Line [行號](或其他平台檔案)
- `docs/02-development/structure.md` - [相關章節]

**除錯方法論**:
- `docs/04-testing-debugging/debugging_methodology.md` - Line 389-510 Spec 驅動除錯方法

**疑難排解索引**:
- `docs/05-troubleshooting/README.md` - 已知問題索引

---

## 建議的下一步

1. **立即行動**(P0 修復): [描述]
2. **短期行動**(P1 修復): [描述]
3. **長期改進**(P2 修復): [描述]

---

*分析日期*: [生成時間]
*分析工具*: /debug
*執行模式*: [快速/標準/深度]
*相關憲法版本*: 1.0.0
*相關規格版本*: [spec.md 最後更新時間]
```

---

### 7. 互動式建議優化

分析完成後,詢問使用者:

**「您需要以下哪些深入分析?」**

- [ ] **代碼片段展示**: 顯示問題函數的代碼上下文(從 structure.md 定位的行號)
- [ ] **相似實作對比**: 比較其他平台或版本的類似功能
- [ ] **Spec 詳細摘錄**: 完整顯示相關的 FR/SC 需求文本
- [ ] **修復代碼範本**: 根據憲法原則提供修復代碼範本
- [ ] **迴歸測試計畫**: 詳細的測試檢查清單

---

### 8. 報告輸出與檔案管理

**輸出**: 完整的 Markdown 報告

**建議**:
- 保存報告為 `docs/07-project-tracking/debug-[日期]-[問題簡稱].md`
- 參考檔案: `docs/05-troubleshooting/README.md`
- 後續可作為專案知識庫

**不修改代碼**(除非使用者明確要求執行修復)

---

## 操作原則

### 分析指南

- **永遠追溯到 Spec**: 所有發現必須連結到 FR-xxx 或 SC-xxx
- **永遠檢查憲法**: 所有建議必須符合憲法原則
- **優先 NoDriver First**: 優先檢查 NoDriver 版本,Chrome 作為參考
- **多層驗證**: 同時檢查多層面(Spec + 憲法 + 代碼 + 已知問題)
- **可追蹤性**: 所有建議都必須包含來源(檔案:行號)

### 報告品質

- **清晰性**: 一般開發者可理解,包含具體例子
- **可操作性**: 建議具有明確的執行方向
- **完整性**: 涵蓋所有相關層面(Spec、憲法、代碼、測試)
- **專業性**: 使用結構化格式,參考憲法和 Spec

### 模式選擇指引

- **快速模式**: 緊急 debug、熟悉問題、參數充足
- **標準模式**: 一般 debug、新問題、需要完整分析
- **深度模式**: 架構問題、多平台影響、複雜依賴

### 憲法優先級處理

- **P0 違規**: 必須立即修復,阻止所有其他工作
- **P1 違規**: 當日修復,優先於新功能開發
- **P2 問題**: 本週修復,納入技術債清單
- **P3 改進**: 有空時改進,不影響發佈

---

## 情境

$ARGUMENTS
