## 變更摘要

本次發布包含以下更新：

### 錯誤修復
- 修正設定頁面因使用 ES2020 optional chaining 語法導致舊版瀏覽器（Chrome 80 之前）無法載入的問題
- 將 `tixcraft_sid?.addEventListener` 改為傳統的 `if (tixcraft_sid)` null 檢查
- 保留所有 TixCraft SID 驗證功能

---

## 統計資訊

- **Commits**: 1 個
- **檔案變更**: 1 個
- **修改檔案**: src/www/settings.js (+20, -18)

---

## 檢查清單

- [x] 已排除機敏檔案（.claude/, docs/, CLAUDE.md 等）
- [x] 已通過本地測試
- [ ] 待 CI 檢查通過
- [ ] 待 Code Review

---

## 相關連結

- 完整變更記錄：查看 CHANGELOG.md
- 技術文件：（僅私人 repo 可見）
