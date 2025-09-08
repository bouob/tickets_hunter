---
description: "產生 emoji 版 Git commit 訊息並提交變更"
allowed-tools: ["Bash"]
---

# 自動產生 emoji Git commit 訊息並提交

請按照以下步驟處理 Git 變更：

1. **分析目前狀態**：
   - 執行 `git status` 查看變更檔案
   - 執行 `git diff --staged` 或 `git diff` 查看具體變更內容

2. **產生 emoji commit 訊息**：
   根據變更類型選擇適合的 emoji 前綴：
   - ✨ 新功能 (feat)
   - 🐛 修復 bug (fix) 
   - 📝 文件更新 (docs)
   - 💄 UI/樣式更新 (style)
   - ♻️ 程式碼重構 (refactor)
   - ⚡ 效能改善 (perf)
   - ✅ 測試相關 (test)
   - 🔧 設定檔修改 (chore)
   - 🚀 部署相關 (deploy)
   - 🎉 初始提交 (init)

3. **預覽變更**：
   - 逐一列出並且顯示所有變更的項目
   - 確認變更內容正確無誤
   - 讓使用者確認是否繼續提交

4. **執行提交並推送**：
   - 執行 `git add .` 加入所有變更
   - 使用產生的訊息執行 `git commit -m "訊息"`
   - 執行 `git push origin main` 推送到遠端倉庫
   - 顯示最終結果

訊息格式範例：
- `✨ 新增 多視窗化功能`
- `🐛 修復 登入失效問題`
- `📝 更新 README 使用說明`

$ARGUMENTS