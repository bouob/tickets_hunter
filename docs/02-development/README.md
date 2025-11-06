# 開發文件導航

歡迎來到 Tickets Hunter 開發文件中心！本目錄包含開發新平台、維護現有功能所需的所有文件。

## 🚀 快速開始

### 我是新手開發者，想開始開發新平台

1. **第一步**：閱讀 [`development_guide.md`](./development_guide.md) 了解開發規範和 NoDriver First 策略
2. **第二步**：查看 [`structure.md`](./structure.md) 了解現有平台的函數架構
3. **第三步**：參考 [`coding_templates.md`](./coding_templates.md) 中的代碼範本開始實作
4. **深入學習**：查閱 [`ticket_automation_standard.md`](./ticket_automation_standard.md) 了解 12 階段詳細定義

### 我要修復 Bug 或改進現有功能

1. **定位問題**：查看 [`structure.md`](./structure.md) 中的函數索引找到相關函數
2. **理解設計**：查閱 [`development_guide.md`](./development_guide.md) 中的設計原則
3. **查看範本**：如需參考，查看 [`coding_templates.md`](./coding_templates.md) 中的相應範本
4. **除錯指南**：參考 [`documentation_workflow.md`](./documentation_workflow.md) 中的除錯方法

### 我想了解項目整體架構

閱讀順序：
1. [`ticket_seat_selection_algorithm.md`](./ticket_seat_selection_algorithm.md) - 座位選擇算法（如適用）
2. [`structure.md`](./structure.md) - 程式結構與函數組織
3. [`development_guide.md`](./development_guide.md) - 開發規範與最佳實踐

---

## 📚 文件分類

### 核心指南（日常開發必讀）

| 文件 | 用途 | 優先度 |
|------|------|--------|
| **development_guide.md** | 開發規範、檢查清單、程式碼品質標準 | ⭐⭐⭐ |
| **structure.md** | 平台函數索引、完整度評分、現有實作分析 | ⭐⭐⭐ |
| **coding_templates.md** | 代碼範本庫、實作檢查表、平台完成度評分 | ⭐⭐⭐ |
| **logic_flowcharts.md** | 邏輯判斷流程圖、可重用程式範本、核心機制實作 | ⭐⭐ |
| **sound_notification_system.md** | 音效通知系統、兩階段音效設計與實作 | ⭐⭐ |

### 參考資料（詳細定義）

| 文件 | 用途 | 何時查閱 |
|------|------|----------|
| **ticket_automation_standard.md** | 12 階段詳細定義、函數拆分規範、配置項目索引 | 深入了解每個階段 |

### 工作流程與文檔

| 文件 | 用途 | 用於 |
|------|------|------|
| **documentation_workflow.md** | 文檔維護流程、更新機制、一致性檢查 | 維護 docs 檔案 |
| **ticket_seat_selection_algorithm.md** | 座位選擇詳細算法 | TicketPlus 座位選擇 |

### 已歸檔資源

| 位置 | 說明 |
|------|------|

---

## 🎯 按工作類型導航

### 開發新平台

```
開始 → development_guide.md (新手入門)
  ↓
查看現有實作 → structure.md (函數索引)
  ↓
選擇參考平台 → coding_templates.md (範本庫)
  ↓
深入了解階段定義 → ticket_automation_standard.md
  ↓
開始編碼 → 使用 development_guide.md 檢查清單
```

### 修復 Bug

```
定位函數 → structure.md (函數搜索)
  ↓
理解邏輯 → logic_flowcharts.md (判斷流程圖)
  ↓
理解實作 → coding_templates.md (參考範本)
  ↓
查詢設計意圖 → ticket_automation_standard.md (12 階段定義)
  ↓
驗證修復 → development_guide.md (測試檢查清單)
```

### 評估現有實作

```
查看評分 → structure.md (完整度評分表)
  ↓
細節分析 → coding_templates.md (實作檢查表)
  ↓
了解標準 → ticket_automation_standard.md (評分標準)
```

---

## 📋 各文件詳細說明

### development_guide.md
- **內容**：開發規範、NoDriver First 策略、編碼標準、檢查清單
- **適合**：所有開發者，新手入門首選
- **關鍵章節**：
  - 搶票程式標準函數架構（12 階段概覽）
  - 程式碼品質標準
  - WebDriver 除錯規則

### structure.md
- **內容**：平台函數索引、完整度評分、現有實作分析
- **適合**：了解現有實作、查找特定函數
- **關鍵章節**：
  - 平台支援狀態表
  - NoDriver API 與 Chrome API 函數對照
  - 各平台的函數完整度評分

### coding_templates.md
- **內容**：代碼範本庫、實作檢查表、平台完成度評分
- **適合**：編寫代碼時參考、評估完整度
- **關鍵章節**：
  - 必要開發規範（Debug 標準、暫停機制）
  - 標準範本庫（各功能模組的代碼範本）
  - 實作完整度檢查表（白金/金/銀級標準）
  - 平台完成度總覽

### logic_flowcharts.md
- **內容**：邏輯判斷流程圖、可重用程式範本、核心機制實作
- **適合**：理解判斷邏輯、開發新平台、除錯現有功能
- **關鍵章節**：
  - 日期選擇判斷邏輯（文字流程圖 + 程式範本）
  - 區域選擇判斷邏輯（AND 邏輯 + 回退機制）
  - 核心可重用機制（關鍵字匹配、選擇策略、點擊回退鏈）
  - 實戰應用案例（TixCraft 完整流程實例）

### ticket_automation_standard.md
- **內容**：12 階段詳細定義、函數拆分規範、配置項目索引
- **適合**：需要深入了解設計意圖、系統性學習
- **關鍵章節**：
  - 核心設計原則（配置驅動、回退策略等）
  - 12 階段完整功能定義
  - 函數命名與拆分原則

### documentation_workflow.md
- **內容**：文檔維護流程、更新機制、一致性檢查
- **適合**：維護 docs 檔案的開發者
- **關鍵章節**：
  - 文檔維護流程
  - 一致性檢查流程
  - 各文件的修改建議

### ticket_seat_selection_algorithm.md
- **內容**：座位選擇詳細算法、特殊平台考量
- **適合**：實作座位選擇功能的開發者
- **適用平台**：TicketPlus 等有複雜座位選擇的平台

---

## 🔗 快速連結

### 常用任務
- **查找函數定義**：→ `structure.md`（函數索引）
- **查看代碼範本**：→ `coding_templates.md`（標準範本庫）
- **理解邏輯判斷**：→ `logic_flowcharts.md`（流程圖與可重用範本）
- **了解音效通知**：→ `sound_notification_system.md`（兩階段音效設計）
- **了解 12 階段**：→ `ticket_automation_standard.md`
- **檢查開發規範**：→ `development_guide.md`（必要元素部分）

### 平台特定資源
- **TixCraft**：查看 `structure.md` 和 `coding_templates.md` 中的白金級實例
- **KKTIX**：同上
- **TicketPlus**：查看座位選擇部分和展開式面板處理
- **iBon**：查看金級實例
- **新平台開發**：參考 `development_guide.md` 的檢查清單

---

## 💡 建議使用流程

### 第一次開發
```
1. 完整閱讀 development_guide.md
2. 瀏覽 structure.md 了解現有實作
3. 參考 coding_templates.md 中的相應範本
4. 需要時查閱 ticket_automation_standard.md
```

### 後續開發
```
1. 查看 structure.md 找到相關函數
2. 參考 coding_templates.md 中的範本
3. 按照 development_guide.md 檢查清單驗證
4. 遇到疑問查閱相應文檔
```

---

## 🔄 文檔維護策略

### 單一真實來源 (SSOT) 原則

為了避免重複和不一致，遵循以下原則：

- **核心定義**：`ticket_automation_standard.md` 是 12 階段和函數定義的唯一來源
- **快速參考**：`development_guide.md` 提供摘要，指向詳細文檔
- **代碼範本**：`coding_templates.md` 提供實際代碼示例
- **平台分析**：`structure.md` 提供實現分析和評分

### 更新流程

編輯文檔時遵循：
1. 只在授權位置進行編輯
2. 其他文件中應提供指向源文件的連結
3. 保持相互參考的一致性

詳見 `documentation_workflow.md`

---

## ❓ 常見問題

**Q: 我應該先讀哪個文件？**
A: 如果是新手，先讀 `development_guide.md`。如果是尋找特定內容，查看上面的「快速開始」部分。

**Q: ticket_automation_standard.md 為什麼在 reference 子目錄？**
A: 這是「單一真實來源」策略的一部分。詳細定義集中在 reference，其他文件指向它。

**Q: 代碼範本在哪裡？**
A: 在 `coding_templates.md` 中。按功能類型搜索相應的範本。

**Q: 我想評估平台的完整度？**
A: 查看 `structure.md` 的完整度評分表或 `coding_templates.md` 的實作檢查表。

---

**最後更新**：2025-10-28
**版本**：2.1（新增音效通知系統文件）

