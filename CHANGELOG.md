# Changelog

## 2025.10.03

- 新增 iBon 平台支援新版 Angular SPA Event 活動頁面格式
- 新增 iBon 平台 OCR 驗證碼連續失敗自動處理機制（3 次自動重試，5 次後切換手動輸入）
- 改善 iBon 平台關鍵字匹配準確度（同時檢查區域名稱與票價區內容）
- 改善 iBon 平台支援新版 EventBuy 頁面的票數選擇

## 2025.10.01

- 新增 iBon 平台搶票成功音效提醒功能（可在 settings.json 設定開關）
- 新增 iBon 平台無頭模式自動開啟結帳頁面，避免錯過付款時間
- 新增 iBon 平台驗證碼自動識別功能（NoDriver 引擎）
- 新增 iBon 平台完整購票流程：日期選擇 → 區域選擇 → 票數填寫 → 驗證碼識別 → 結帳提醒
- 改善 NoDriver 引擎四大平台（TixCraft、KKTIX、TicketPlus、iBon）核心功能完整性
- 改善 NoDriver API 開發指南文件結構，新增 iBon 實作範例

## 2025.09.30

- 新增 iBon 日期選擇支援多種格式（M/D、MM/DD、YY/MM/DD、YYYY/MM/DD）
- 新增 iBon 座位區域自動選擇功能（NoDriver 引擎）
- 新增座位區域關鍵字匹配與模式選擇回退策略
- 新增剩餘票數檢查，自動避開已售完區域
- 修正 iBon 日期選擇時偶爾卡住的問題

## 2025.09.26

- 新增 README.md 中的詳細平台支援狀態對照表
- 新增 NoDriver 引擎支援 KKTIX、TicketPlus遠大、TixCraft拓元三大平台（持續開發中）
- 新增平台測試狀況與問題回報的視覺化指標
- 改善使用者的平台選擇和引擎使用指引
- 修正 NoDriver TicketPlus 模組中的 JavaScript 字串模板語法錯誤

