**文件說明**：規格到程式碼的完整追溯系統，包含規格驗證矩陣、平台檢查清單與 FR 對照表，支援功能需求驗證、平台完成度評估與代碼索引。

**最後更新**：2026-03-05

---

# 驗證系統導航 (Validation System)

## 規格文件索引

> **重要**：功能規格由 speckit 工具管理，存放於 `specs/` 目錄

```
specs/001-ticket-automation-system/
├── spec.md      ← 功能規格（FR-001 ~ FR-064）
├── plan.md      ← 實作計畫
└── tasks.md     ← 任務清單
```

**快速連結**：
- 📋 [功能規格 spec.md](../../specs/001-ticket-automation-system/spec.md) - FR-xxx、SC-xxx 定義
- 📋 [實作計畫 plan.md](../../specs/001-ticket-automation-system/plan.md) - 設計決策

---

## 概述

歡迎來到 **Tickets Hunter 驗證系統**！本目錄提供完整的**規格到程式碼追溯工具**，確保系統實作符合功能需求（FR-001 至 FR-064）。

### 驗證系統的三個支柱

```
┌──────────────────────────────────────────────────────────────┐
│                      驗證系統架構                              │
└──────────────────────────────────────────────────────────────┘

 [1. 規格驗證矩陣]        [2. 平台檢查清單]      [3. FR 對照表]
 spec-validation-matrix    platform-checklist     fr-to-code-mapping
         ↓                         ↓                      ↓
   詳細 FR 追溯              平台完成度評分          快速函數索引
   ┌─────────────┐          ┌─────────────┐       ┌─────────────┐
   │ FR-001      │          │ TixCraft    │       │ FR-001 →    │
   │  實作狀態   │          │  84.4%      │       │  nodriver_  │
   │  測試狀態   │          │ KKTIX       │       │  main()     │
   │  平台支援   │          │  82.8%      │       │  Line 16775 │
   │ ...         │          │ ...         │       │ ...         │
   └─────────────┘          └─────────────┘       └─────────────┘
```

---

## 核心文件

### 1. 規格驗證矩陣 (Spec Validation Matrix)

**檔案**：[spec-validation-matrix.md](./spec-validation-matrix.md)

**用途**：完整的 FR-001 至 FR-064 實作狀態追溯

**包含內容**：
- ✅ 每個 FR 的實作狀態（已實作/部分實作/未實作）
- 🧪 測試狀態（已測試/部分測試/未測試）
- 🌐 平台支援情況（TixCraft/KKTIX/iBon/TicketPlus/KHAM/HK Ticketing/Cityline/FamiTicket/TicketMaster/年代售票/FunOne/FANSI GO）
- 📍 對應函數名稱與檔案位置
- 🎯 相關成功標準（SC-XXX）
- 📝 實作備註與改進建議

**統計摘要**：
- **已實作**：38/64 (59.4%)
- **部分實作**：19/64 (29.7%)
- **未實作**：7/64 (10.9%)

**最適合**：
- 詳細追蹤單一 FR 的實作狀態
- 了解 FR 與測試的關係
- 檢查 FR 是否符合成功標準（SC）

**範例查詢**：
> 「FR-017-1（關鍵字匹配優先）是否已實作？支援哪些平台？」
>
> 答：✅ 已實作，支援 TixCraft、KKTIX，部分支援 iBon，函數位置在 `nodriver_tixcraft_date_auto_select()` Line 2759-2807

---

### 2. 平台實作檢查清單 (Platform Implementation Checklist)

**檔案**：[platform-checklist.md](./platform-checklist.md)

**用途**：所有支援平台的完整功能檢查與完成度評分

**包含內容**：
- 📊 平台支援度總覽（完成度排名）
- ✅ 12-Stage 逐一檢查（每個階段的功能清單）
- 🎯 待補強項目分析（按優先度分類）
- 🚀 開發優先順序建議（時間估算）

**平台排名**（ZenDriver 引擎完成度）：
1. **KKTIX**: 100% - 🟢 完美
2. **iBon**: 100% - 🟢 完美
3. **HK Ticketing**: 90% - 🟢 優秀
4. **KHAM 寬宏**: 90% - 🟢 優秀
5. **Cityline**: 85% - 🟢 優秀
6. **TicketPlus 遠大**: 85% - 🟢 優秀
7. **TixCraft 拓元**: 84.4% (54/64 FR) - 🟢 優秀
8. **FamiTicket 全網**: 80% - 🟡 良好
9. **TicketMaster**: ~89% (ZenDriver 專用) - 🟢 優秀
10. **年代售票 / UDN**: ~90% - 🟢 優秀
11. **FunOne Tickets**: 進行中 - 🟡 良好
12. **FANSI GO**: 進行中 - 🟡 良好
13. **Urbtix 城市**: 0% (ZenDriver 未實作) - 🔴 待開發

**最適合**：
- 評估平台功能完整性
- 規劃新平台開發
- 識別待補強的功能項目

**範例查詢**：
> 「KKTIX 平台的 Stage 4（日期選擇）完成度如何？」
>
> 答：83.3% (7.5/9)，支援 Early Return Pattern 和 Conditional Fallback，但驗證日期選擇成功（FR-019）為部分實作

---

### 3. FR 到程式碼對照表 (FR to Code Mapping)

**檔案**：[fr-to-code-mapping.md](./fr-to-code-mapping.md)

**用途**：快速索引 - 從 FR 編號直接跳轉到函數位置

**包含內容**：
- 🔍 FR-XXX → 函數名稱對照
- 📍 函數檔案位置與行號
- 🧪 測試覆蓋狀態
- 🎯 優先度標記（P1/P2/P3）
- 🔗 相關設定檔參數
- 📚 相關文件連結

**最適合**：
- 快速找到功能對應的程式碼
- 除錯特定功能問題
- 查詢函數位置與行號

**範例查詢**：
> 「我要修改 FR-022（排除關鍵字過濾），函數在哪裡？」
>
> 答：`nodriver_get_tixcraft_target_area()` 函數，`src/nodriver_tixcraft.py` Line 3194-3197，設定來源：`settings.json → keyword_exclude`

---

## 使用指南

### 場景 1：驗證功能是否已實作

**目標**：確認特定功能需求是否已實作

**流程**：
1. 打開 [spec-validation-matrix.md](./spec-validation-matrix.md)
2. 搜尋 FR 編號（例如：`FR-023-1`）
3. 檢查實作狀態、測試狀態、平台支援

**範例**：
```
搜尋：FR-023-1
結果：✅ 已實作
     函數：nodriver_get_tixcraft_target_area()
     位置：src/nodriver_tixcraft.py:3048-3061
     平台：✅ TixCraft / ✅ KKTIX / 🔄 iBon
     測試：✅ 已測試
```

---

### 場景 2：評估平台完成度

**目標**：了解特定平台的功能完整性

**流程**：
1. 打開 [platform-checklist.md](./platform-checklist.md)
2. 查看「平台支援度總覽」區塊
3. 檢視特定平台的 12-Stage 檢查清單

**範例**：
```
查詢：iBon 平台完成度
結果：81.3% (52/64)
     Stage 4（日期選擇）：50% (4.5/9)
     待補強：FR-017-1、FR-017-2（Early Return + Conditional Fallback）
```

---

### 場景 3：快速定位程式碼

**目標**：從 FR 編號快速跳轉到程式碼

**流程**：
1. 打開 [fr-to-code-mapping.md](./fr-to-code-mapping.md)
2. 搜尋 FR 編號
3. 直接跳轉到檔案與行號

**範例**：
```
搜尋：FR-035
結果：nodriver_tixcraft_keyin_captcha_code()
     檔案：src/nodriver_tixcraft.py
     行號：1609-1677
     優先度：🔴 P1
     設定：N/A（自動執行）
```

---

### 場景 4：規劃新平台開發

**目標**：為新平台（例如 TicketPlus）規劃開發任務

**流程**：
1. 打開 [platform-checklist.md](./platform-checklist.md)
2. 查看「待補強項目總覽」區塊
3. 參考「開發建議與優先順序」區塊

**範例**：
```
平台：TicketPlus
目前完成度：18.8% (12/64)
優先任務：
  1. 登入機制（FR-005 或 FR-006）- 估計 6-8 小時
  2. 日期與區域選擇（FR-014 至 FR-024）- 估計 12-16 小時
  3. 票券數量與驗證碼（FR-027 至 FR-039）- 估計 10-12 小時
預期成果：18.8% → 60%+
```

---

### 場景 5：除錯功能問題

**目標**：功能出現問題，需要定位程式碼並檢查規格

**流程**：
1. 使用 [fr-to-code-mapping.md](./fr-to-code-mapping.md) 定位函數
2. 使用 [spec-validation-matrix.md](./spec-validation-matrix.md) 檢查規格與 SC
3. 參考相關文件連結（機制文件、API 文件）

**範例**：
```
問題：日期選擇關鍵字不匹配時沒有自動回退
步驟：
  1. 查詢 FR-017-2（Conditional Fallback）
  2. 函數：nodriver_tixcraft_date_auto_select() Line 2863-2876
  3. 檢查設定：date_auto_fallback = false（預設嚴格模式）
  4. 解決：設定 date_auto_fallback = true 啟用自動回退
  5. 參考文件：docs/03-mechanisms/04-date-selection.md
```

---

## 維護指南

### 新增功能時

**流程**：
1. **實作功能** → 完成程式碼撰寫
2. **更新 fr-to-code-mapping.md** → 新增 FR 對照條目（函數名稱、行號）
3. **更新 spec-validation-matrix.md** → 標記 FR 為「✅ 已實作」，填寫平台支援
4. **更新 platform-checklist.md** → 更新平台完成度百分比
5. **測試驗證** → 更新測試狀態為「✅ 已測試」

**範例 Commit Message**：
```
✨ feat(tixcraft): implement FR-017-1 early return pattern

- Updated fr-to-code-mapping.md: FR-017-1 mapping
- Updated spec-validation-matrix.md: ✅ Implemented
- Updated platform-checklist.md: TixCraft 75% → 80%
- Test: ✅ Passed
```

---

### 修改規格時

**流程**：
1. **修改 spec.md** → 更新功能需求描述
2. **更新 spec-validation-matrix.md** → 同步 FR 描述、相關 SC
3. **檢查 fr-to-code-mapping.md** → 確認對應函數是否需要修改
4. **通知開發團隊** → 如需修改實作

**範例 Commit Message**：
```
📝 docs(spec): update FR-017-2 conditional fallback behavior

- Updated spec.md: Clarified fallback trigger condition
- Updated spec-validation-matrix.md: Synced FR-017-2 description
- Impact: No code change required
```

---

### 季度性檢查

**目標**：確保驗證文件與實際程式碼同步

**檢查清單**：
- [ ] 驗證所有行號是否正確（對照實際程式碼）
- [ ] 檢查新增函數是否已加入 fr-to-code-mapping.md
- [ ] 更新平台完成度統計（如有變動）
- [ ] 檢查測試狀態是否與實際測試結果一致
- [ ] 更新版本歷史區塊

**建議頻率**：每 3 個月或每次重大功能發布後

---

## 統計摘要

### 整體完成度

| 指標 | 數值 | 百分比 |
|-----|------|--------|
| 已實作 FR | 38/64 | 59.4% |
| 部分實作 FR | 19/64 | 29.7% |
| 未實作 FR | 7/64 | 10.9% |
| 已測試 FR | 38/64 | 59.4% |

### 階段完成度

| 階段 | 完成度 | 評級 |
|-----|--------|------|
| **Stage 4：日期選擇** | 100% (9/9) | ✅ 完美 |
| **Stage 6：票券數量** | 100% (4/4) | ✅ 完美 |
| **Stage 11：排隊與付款** | 100% (4/4) | ✅ 完美 (KKTIX) |
| Stage 2：身份認證 | 75% (3/4) | 🟢 優秀 |
| Stage 5：區域/座位選擇 | 86% (8/10) | 🟢 優秀 |
| Stage 7：驗證碼處理 | 78% (7/9) | 🟢 優秀 |
| Stage 12：錯誤處理與重試 | 71% (5/7) | 🟡 良好 |
| Stage 1：環境初始化 | 50% (2/4) | 🟡 良好 |
| **Stage 8：表單填寫** | 0% (0/4) | 🔴 待開發 |

### 平台完成度（ZenDriver 引擎）

| 平台 | 完成度 | 評級 |
|-----|--------|------|
| **KKTIX** | 100% | 🟢 完美 |
| **iBon** | 100% | 🟢 完美 |
| **HK Ticketing** | 90% | 🟢 優秀 |
| **KHAM 寬宏** | 90% | 🟢 優秀 |
| **年代售票 / UDN** | ~90% | 🟢 優秀 |
| **TicketMaster** | ~89% | 🟢 優秀 |
| **Cityline** | 85% | 🟢 優秀 |
| **TicketPlus 遠大** | 85% | 🟢 優秀 |
| **TixCraft 拓元** | 84.4% | 🟢 優秀 |
| **FamiTicket 全網** | 80% | 🟡 良好 |
| **FunOne Tickets** | 進行中 | 🟡 良好 |
| **FANSI GO** | 進行中 | 🟡 良好 |
| **Urbtix 城市** | 0% | 🔴 待開發 |

---

## 相關文件

### 規格與設計
- 📋 [功能規格](../../specs/001-ticket-automation-system/spec.md) - FR-001 至 FR-064 完整定義
- 📋 [實作計畫](../../specs/001-ticket-automation-system/plan.md) - 設計決策與架構
- 📋 [成功標準](../../specs/001-ticket-automation-system/spec.md#成功標準) - SC-001 至 SC-011

### 程式碼結構
- 🏗️ [程式碼結構分析](../02-development/structure.md) - 函數索引與行號
- 📋 [12-Stage 標準](../02-development/ticket_automation_standard.md) - 完整流程定義

### 機制文件（已完成）
- ✅ [Stage 4: 日期選擇](../03-mechanisms/04-date-selection.md) - FR-014 至 FR-019
- ✅ [Stage 5: 區域選擇](../03-mechanisms/05-area-selection.md) - FR-020 至 FR-026
- ✅ [Stage 7: 驗證碼處理](../03-mechanisms/07-captcha-handling.md) - FR-031 至 FR-039

### 平台參考實作
- ✅ [KKTIX 參考實作](../04-implementation/platform-examples/kktix-reference.md)
- ✅ [iBon 參考實作](../04-implementation/platform-examples/ibon-reference.md)

### API 參考
- 📋 [CDP 協議參考](../06-api-reference/cdp_protocol_reference.md) - FR-060、FR-064 技術細節
- 📋 [NoDriver API 指南](../06-api-reference/nodriver_api_guide.md) - NoDriver 完整參考
- 📋 [ddddocr API 指南](../06-api-reference/ddddocr_api_guide.md) - FR-033、FR-034

---

## 快速導航

### 我想要...

#### ...查詢某個 FR 是否已實作
→ [規格驗證矩陣](./spec-validation-matrix.md)

#### ...評估平台功能完整性
→ [平台實作檢查清單](./platform-checklist.md)

#### ...快速找到功能對應的程式碼
→ [FR 到程式碼對照表](./fr-to-code-mapping.md)

#### ...規劃新平台開發
→ [平台實作檢查清單](./platform-checklist.md) → 「待補強項目總覽」

#### ...了解 12-Stage 流程
→ [12-Stage 標準](../02-development/ticket_automation_standard.md)

#### ...學習特定機制的實作細節
→ [機制文件](../03-mechanisms/README.md) → Stage 4、5、7 已完成

#### ...查詢 CDP 協議使用方法
→ [CDP 協議參考](../06-api-reference/cdp_protocol_reference.md)

#### ...了解架構設計原則
→ ZenDriver First 原則 - 詳見專案內部文件

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| v1.0 | 2025-11 | 初版：建立驗證系統導航 |
| | | ✅ 三個核心文件介紹 |
| | | ✅ 使用指南（5 個場景） |
| | | ✅ 維護指南與檢查清單 |
| | | ✅ 統計摘要與快速導航 |
| v1.1 | 2026-03-05 | 更新平台完成度統計 |
| | | ✅ 擴展平台統計至 13 個平台 |
| | | ✅ 更新 FR 完成度數據 |

**未來更新**：
- 每次新增驗證文件時同步更新導航
- 每季度更新統計摘要
- 根據使用者回饋優化使用指南

---

**維護者**：Tickets Hunter 開發團隊

**需要協助？**
- 📖 [專案總覽](../01-getting-started/project_overview.md)
- 📖 [開發指南](../02-development/development_guide.md)
- 🐛 [除錯方法論](../internal/testing-debugging/debugging_methodology.md)
