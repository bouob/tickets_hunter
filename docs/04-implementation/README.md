**文件說明**：各售票平台的實作參考指南，包含 TixCraft、KKTIX、iBon、TicketPlus 等平台的具體實作方法、特性分析與完成度評估。

**最後更新**：2025-11-12

---

# 平台實作參考 (Implementation Reference)

## 概述

本目錄包含針對各個售票平台的具體實作參考文件。每份文件詳細說明該平台的特定實作方法、常見問題與解決方案。

**適用情境**：
- 新增對某平台的支持
- 修復該平台的特定問題
- 了解該平台的獨特特點

---

## 平台文件導航

### 已完成平台

#### 1. TixCraft - `tixcraft-reference.md`
**特點**：台灣最大售票平台，支援直播、演唱會、運動賽事

**核心特性**：
- 直接頁面導航，無排隊機制
- Cookie 認證有效期 30 天
- 支援進階選擇選項（展開面板）
- 多種支付方式

**實作難度**：⭐⭐ (中等)

**相關功能**：FR-001 至 FR-064 全支持（已驗證 84.4% 完成）

---

#### 2. KKTIX - `kktix-reference.md`
**特點**：中等規模平台，專注於演唱會與文化活動

**核心特性**：
- AJAX 動態更新，無頁面刷新
- Cookie 有效期相對較短 (7-14 天)
- 相對簡單的選擇介面
- 排隊機制

**實作難度**：⭐⭐ (中等)

**相關功能**：FR-001 至 FR-064 全支持（已驗證 82.8% 完成）

---

#### 3. iBon - 現有 `ibon-reference.md`
**特點**：主要用於演唱會與電影票

**核心特性**：
- Angular SPA 框架，複雜的 DOM 結構
- Shadow DOM 使用
- Cookie 認證
- 複雜的購買人驗證流程

**實作難度**：⭐⭐⭐ (高)

**相關功能**：FR-001 至 FR-064 全支持（已驗證 81.3% 完成）

---

#### 4. TicketPlus - `ticketplus-reference.md` (進行中)
**特點**：中小型平台，參與度較低

**核心特性**：
- 表格形式的購買人填寫
- 展開面板設計
- 實名驗證需求
- 多步驟流程

**實作難度**：⭐⭐⭐ (高)

**相關功能**：FR-001 至 FR-064 部分支持（目前 18.8% 完成，需補強）

---

### 平台完成度對比

| 平台 | Stage 12 完成度 | 優先度 | 難度 | 推薦學習順序 |
|------|---------|--------|------|----------|
| TixCraft | 84.4% | 🔴 P1 | ⭐⭐ | 1️⃣ |
| KKTIX | 82.8% | 🔴 P1 | ⭐⭐ | 2️⃣ |
| iBon | 81.3% | 🔴 P1 | ⭐⭐⭐ | 3️⃣ |
| TicketPlus | 18.8% | 🟡 P2 | ⭐⭐⭐ | 4️⃣ |

---

## 使用指南

### 快速找到平台文件

1. **我要添加新平台** → 先讀 TixCraft 文件學習基本流程
2. **我要修復特定平台的問題** → 查找該平台的參考文件
3. **我要了解平台差異** → 對比不同平台的實作參考
4. **我要完整了解 12 階段** → 先讀 `docs/03-mechanisms/` 中的機制文件

### 推薦學習路徑

#### 初學者
```
1. docs/03-mechanisms/README.md         ← 了解 12 階段概念
2. docs/04-implementation/tixcraft-reference.md  ← 學習 TixCraft（最簡單）
3. docs/04-implementation/kktix-reference.md     ← 學習 KKTIX
4. docs/03-mechanisms/01-12.md          ← 深入每個機制
```

#### 有經驗的開發者
```
1. docs/04-implementation/tixcraft-reference.md  ← 快速複習
2. docs/05-validation/platform-checklist.md      ← 查看實作缺口
3. docs/05-validation/fr-to-code-mapping.md      ← 查找具體實作
4. docs/03-mechanisms/[related-stage].md        ← 根據需要查看機制文件
```

---

## 平台特性對比表

| 特性 | TixCraft | KKTIX | iBon | TicketPlus |
|-----|---------|-------|------|-----------|
| 排隊機制 | ❌ | ✅ | ❌ | ❌ |
| Shadow DOM | ❌ | ❌ | ✅ | ❌ |
| 動態更新 | ❌ | ✅ | ✅ | ❌ |
| 多人購買表格 | ❌ | ❌ | ❌ | ✅ |
| Cookie 期限 | 30天 | 7-14天 | 14-30天 | 14-30天 |
| 認證方式 | Cookie+密碼 | Cookie+密碼 | Cookie+密碼 | Cookie+密碼 |
| JavaScript 需求 | 低 | 中 | 高 | 中 |

---

## 常見問題索引

### 跨平台問題

**Q：如何適配新平台？**
A：查看 TixCraft 參考文件了解基本結構，根據該平台的特性進行調整。

**Q：不同平台的選擇器如何維護？**
A：為每個平台創建獨立的選擇器配置文件，見各平台參考文件。

**Q：如何測試跨平台功能？**
A：使用 `settings.json` 的 `webdriver_type` 與 URL 來測試不同平台。

### 平台特定問題

**Q：為什麼 iBon 這麼複雜？**
A：iBon 使用 Angular + Shadow DOM，導致選擇器複雜且易變。

**Q：如何處理 TicketPlus 的多人購買表格？**
A：見 `ticketplus-reference.md` 的表單填寫部分。

---

## 開發检查清單

- [ ] 已閱讀 `docs/03-mechanisms/` 目錄下的相關機制文件
- [ ] 已閱讀該平台的參考實作文件
- [ ] 已在測試環境驗證實作
- [ ] 已針對該平台的特性進行調整
- [ ] 已通過所有相關的單位測試
- [ ] 已更新 `docs/05-validation/` 中的驗證文件

---

## 相關文件

### 機制文件
- `docs/03-mechanisms/01-environment-init.md`
- `docs/03-mechanisms/02-authentication.md`
- `docs/03-mechanisms/03-page-monitoring.md`
- ... 及其他 12 個階段文件

### 驗證文件
- `docs/05-validation/spec-validation-matrix.md` - FR 追溯表
- `docs/05-validation/platform-checklist.md` - 平台完成度評分
- `docs/05-validation/fr-to-code-mapping.md` - 代碼對應表

### 故障排除
- `docs/08-troubleshooting/README.md` - 平台特定的故障排除指南

---

## 版本與更新

**當前支持的平台數**：4 個（TixCraft、KKTIX、iBon、TicketPlus）

**計劃新增的平台**：無（按照用戶反饋）

---

## 貢獻指南

如果要新增平台或更新現有平台的參考文件：

1. 複製 `tixcraft-reference.md` 作為範本
2. 根據新平台的特性進行調整
3. 更新 `platform-checklist.md` 的統計數據
4. 更新本 README 的平台列表
5. 提交合併請求

---

## 快速連結

- 📋 [規格驗證矩陣](../05-validation/spec-validation-matrix.md) - FR-001 至 FR-064 追溯
- 📊 [平台完成度評分](../05-validation/platform-checklist.md) - 各平台的實作狀態
- 🔗 [代碼對應表](../05-validation/fr-to-code-mapping.md) - FR 到函數的映射
- 🏗️ [機制文件](../03-mechanisms/README.md) - 12 個階段的詳細說明

