# 平台實作參考 (Implementation Reference)

**文件說明**：各售票平台的實作參考指南，包含 TixCraft、KKTIX、iBon、TicketPlus、FamiTicket、Cityline、KHAM、HKTicketing、FunOne、FANSI GO 等平台的具體實作方法、特性分析與完成度評估。
**最後更新**：2026-03-05

---

## 概述

本目錄包含針對各個售票平台的具體實作參考文件。每份文件詳細說明該平台的特定實作方法、常見問題與解決方案。

**適用情境**：
- 新增對某平台的支持
- 修復該平台的特定問題
- 了解該平台的獨特特點

---

## 平台文件導航

### 台灣平台

#### 1. TixCraft - `tixcraft-reference.md`
**特點**：台灣最大售票平台，支援直播、演唱會、運動賽事

**核心特性**：
- 直接頁面導航，無排隊機制
- Cookie 認證有效期 30 天
- 支援進階選擇選項（展開面板）
- 多種支付方式

**實作難度**：⭐⭐ (中等)

**完成度**：84.4%

---

#### 2. KKTIX - `kktix-reference.md`
**特點**：中等規模平台，專注於演唱會與文化活動

**核心特性**：
- AJAX 動態更新，無頁面刷新
- Cookie 有效期相對較短 (7-14 天)
- 問答式驗證碼
- 排隊機制

**實作難度**：⭐⭐ (中等)

**完成度**：100%

---

#### 3. iBon - `ibon-reference.md`
**特點**：主要用於演唱會與電影票

**核心特性**：
- Angular SPA 框架，複雜的 DOM 結構
- Shadow DOM 使用
- Cookie 認證
- 複雜的購買人驗證流程

**實作難度**：⭐⭐⭐ (高)

**完成度**：100%

---

#### 4. TicketPlus - `ticketplus-reference.md`
**特點**：台灣中型票務平台（遠大售票）

**核心特性**：
- Vue.js SPA 架構，多版面自動識別
- 展開面板（Accordion）設計
- 實名驗證需求
- 排隊偵測機制

**實作難度**：⭐⭐⭐ (高)

**完成度**：85%

---

#### 5. FamiTicket - `famiticket-reference.md`
**特點**：台灣便利商店票務系統（全家網票務）

**核心特性**：
- 標準 Web 架構，DOM 結構清晰
- 登入流程相對簡單
- 支援自動日期/區域選擇
- 問答式驗證（類似 KKTIX）

**實作難度**：⭐⭐ (中等)

**完成度**：80%

---

#### 6. KHAM - `kham-reference.md`
**特點**：台灣主要票務平台之一（寬宏售票）

**核心特性**：
- ASP.NET 傳統架構，頁面結構穩定
- 完整的座位圖選擇支援
- OCR 驗證碼辨識
- 支援 UDN 聯合報系統

**實作難度**：⭐⭐⭐ (高)

**完成度**：90%

---

#### 7. FunOne - `funone-reference.md`
**特點**：台灣新興票務平台（FunOne Tickets）

**核心特性**：
- Cookie 認證（ticket_session）
- OCR 圖形驗證碼
- 即時票務狀態更新（WebSocket）
- 完整 12 階段實作

**實作難度**：⭐⭐⭐ (高)

**完成度**：92%

---

#### 8. FANSI GO - `fansigo-reference.md`
**特點**：台灣新興票務平台（FANSI GO）

**核心特性**：
- Next.js SPA 架構
- Cookie 認證（FansiAuthInfo）
- tab.evaluate() 為主要 DOM 操作方式
- 簡潔的購票流程

**實作難度**：⭐⭐ (中等)

**完成度**：58%

---

### 香港平台

#### 9. Cityline - `cityline-reference.md`
**特點**：香港最大票務平台（城市電腦售票）

**核心特性**：
- 多域名處理（cityline.com / shows / venue）
- Cloudflare Turnstile 驗證
- 多分頁自動關閉
- 廣告自動清除

**實作難度**：⭐⭐⭐ (高)

**完成度**：85%

---

#### 10. HKTicketing - `hkticketing-reference.md`
**特點**：香港主要票務平台（香港快達票）

**核心特性**：
- 雙架構支援（ASP.NET + Vue/React SPA）
- 排隊頁面自動重導向
- 流量過載自動刷新
- 詳細的購票流程控制

**實作難度**：⭐⭐⭐⭐ (極高)

**完成度**：90%

---

### 輔助模組

#### Facebook - （無獨立參考文件）
**特點**：Facebook OAuth 登入輔助模組，非獨立票務平台

**核心特性**：
- 自動填入 Facebook 帳號密碼
- 支援 OAuth 登入跳轉
- 僅包含 2 個函式（`nodriver_facebook_login` + `nodriver_facebook_main`）

**實作難度**：⭐ (低)

---

## 平台完成度對比

| 平台 | 完成度 | 優先度 | 難度 | 推薦學習順序 |
|------|--------|--------|------|-------------|
| TixCraft | 84.4% | 🔴 P1 | ⭐⭐ | 1️⃣ |
| KKTIX | 100% | 🔴 P1 | ⭐⭐ | 2️⃣ |
| iBon | 100% | 🔴 P1 | ⭐⭐⭐ | 3️⃣ |
| TicketPlus | 85% | 🔴 P1 | ⭐⭐⭐ | 4️⃣ |
| KHAM | 90% | 🔴 P1 | ⭐⭐⭐ | 5️⃣ |
| HKTicketing | 90% | 🟡 P2 | ⭐⭐⭐⭐ | 6️⃣ |
| FunOne | 92% | 🟡 P2 | ⭐⭐⭐ | 7️⃣ |
| Cityline | 85% | 🟡 P2 | ⭐⭐⭐ | 8️⃣ |
| FamiTicket | 80% | 🟡 P2 | ⭐⭐ | 9️⃣ |
| FANSI GO | 58% | 🟢 P3 | ⭐⭐ | 🔟 |

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
1. docs/03-mechanisms/README.md         <- 了解 12 階段概念
2. docs/04-implementation/tixcraft-reference.md  <- 學習 TixCraft（最簡單）
3. docs/04-implementation/kktix-reference.md     <- 學習 KKTIX
4. docs/03-mechanisms/01-12.md          <- 深入每個機制
```

#### 有經驗的開發者
```
1. docs/04-implementation/tixcraft-reference.md  <- 快速複習
2. docs/05-validation/platform-checklist.md      <- 查看實作缺口
3. docs/05-validation/fr-to-code-mapping.md      <- 查找具體實作
4. docs/03-mechanisms/[related-stage].md        <- 根據需要查看機制文件
```

---

## 平台特性對比表

| 特性 | TixCraft | KKTIX | iBon | TicketPlus | FamiTicket | KHAM | Cityline | HKTicketing | FunOne | FANSI GO |
|-----|---------|-------|------|-----------|-----------|------|---------|------------|--------|----------|
| 排隊機制 | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Shadow DOM | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 動態更新 | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| OCR 驗證碼 | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| 問答式驗證碼 | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| CF Turnstile | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Cookie 認證 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SPA 架構 | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅(部分) | ❌ | ✅ |

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

**Q：FunOne 和 FANSI GO 有什麼差異？**
A：FunOne 使用傳統 Web 架構加 OCR 驗證碼；FANSI GO 使用 Next.js SPA，目前無驗證碼機制。

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
- 平台特定的故障排除指南 - 詳見內部疑難排解文件

---

## 版本與更新

**當前支持的平台數**：10 個票務平台 + 1 個 Facebook 登入輔助模組

| 區域 | 平台 |
|------|------|
| 台灣 | TixCraft、KKTIX、iBon、TicketPlus、FamiTicket、KHAM、FunOne、FANSI GO |
| 香港 | Cityline、HKTicketing |
| 輔助 | Facebook（OAuth 登入） |

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
