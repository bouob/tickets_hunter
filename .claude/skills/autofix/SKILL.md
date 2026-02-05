# Autofix Skill

自主修復 GitHub Issue 的完整流程：從讀取 Issue 到建立 PR，全程自動化。

## 使用方式

```
/autofix #236
/autofix 220
```

## 自主修復原則

**核心理念**：遇到錯誤自行解決，只有真正無法繞過的阻礙才停止。

- 不要問使用者問題，自行做出合理決策
- 記錄你的推理過程，讓決策可追溯
- 遇到錯誤時嘗試替代方案
- 只有基本阻礙（權限不足、無法重現等）才停止

---

## 執行流程

### Phase 1: 理解問題

```bash
# 讀取 Issue 完整內容
gh issue view <NUMBER> --json title,body,comments,labels,state
```

分析重點：
- 使用者回報的症狀是什麼？
- 有提供重現步驟嗎？
- 涉及哪個平台/模組？
- 是否有相關 log 或截圖？

### Phase 2: 探索程式碼

使用 Grep 和 Read 工具：
- 搜尋相關函數和錯誤訊息
- 追蹤執行流程
- 理解現有邏輯
- 識別需要修改的檔案

### Phase 3: 建立實作計劃

使用 TodoWrite 建立檢查清單：

```
- [ ] 確認根本原因
- [ ] 設計修復方案
- [ ] 實作修復
- [ ] 測試修復
- [ ] 提交變更
- [ ] 建立 PR
```

### Phase 4: 實作修復

修復要點：
- 遵循專案現有程式碼風格
- 加入適當的錯誤處理
- 不要過度工程化，只修必要的部分
- 確保不引入新的安全漏洞

### Phase 5: 測試驗證

```bash
# 語法檢查
python -m py_compile src/<modified_file>.py

# 快速功能測試（如適用）
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json
```

如果測試失敗：
1. 分析錯誤訊息
2. 修正問題
3. 重新測試
4. 重複直到通過

### Phase 6: 提交變更

使用 `/gsave` 提交，訊息格式：

```
🐛 fix(<scope>): <簡短描述> (#<NUMBER>)

- <具體修改 1>
- <具體修改 2>
```

### Phase 7: 建立 PR

```bash
# 推送到私人庫
git push private main

# 建立 PR 到公開庫（使用 /publicpr 或手動）
gh pr create --repo bouob/tickets_hunter \
  --title "🐛 fix(<scope>): <描述>" \
  --body "Fixes #<NUMBER>

## 問題
<問題描述>

## 修復
<修復說明>

## 測試
- [x] 語法檢查通過
- [x] 功能測試通過"
```

---

## 錯誤處理策略

| 情況 | 處理方式 |
|------|----------|
| 無法重現問題 | 記錄嘗試步驟，請求更多資訊 |
| 多個可能原因 | 選擇最可能的，記錄其他假設 |
| 測試失敗 | 分析錯誤，修正後重試 |
| 不確定修復是否正確 | 加入 debug log，建立 PR 請求 review |
| 影響範圍太大 | 停止，建立調查報告，請求確認 |

---

## 停止條件

只有以下情況才停止並回報：

1. **權限不足** - 無法存取必要資源
2. **無法重現** - 嘗試多種方式仍無法重現問題
3. **需要硬體** - 問題涉及特定硬體/環境
4. **架構決策** - 修復需要重大架構變更
5. **資訊不足** - Issue 描述過於模糊，無法理解問題

停止時產生調查報告：`docs/investigations/issue-<NUMBER>.md`

---

## 與其他 Skill 整合

| 階段 | 可用 Skill |
|------|-----------|
| 調查 | `/investigate` |
| 提交 | `/gsave` |
| 推送 | `/gpush` |
| PR | `/publicpr` |
