# Investigate Skill

調查 GitHub Issue 並產生持久化調查報告，確保跨 session 進度不遺失。

## 使用方式

```
/investigate #236
/investigate 220
```

## 調查流程

### 1. 讀取 Issue 內容

```bash
gh issue view <NUMBER> --json title,body,comments,labels,state
```

### 2. 分析問題

- 理解使用者回報的症狀
- 識別相關的平台/模組
- 確認重現步驟（如有提供）

### 3. 探索程式碼

使用 Explore agent 深入調查：
- 搜尋相關函數和檔案
- 追蹤執行流程
- 識別可能的問題點

### 4. 產生調查報告

在 `docs/investigations/` 建立報告檔案：

**檔名格式**：`issue-<NUMBER>.md`

**報告模板**：

```markdown
# Issue #<NUMBER> 調查報告

**Issue 標題**：<title>
**調查日期**：<date>
**狀態**：調查中 / 已確認 / 已修復

---

## 1. 問題摘要

<簡述使用者回報的問題>

## 2. 發現

<調查過程中發現的關鍵資訊>

## 3. 根本原因假設

<推測的問題根因>

## 4. 建議修復方案

<具體的修復步驟或方向>

## 5. 相關檔案

| 檔案 | 相關行數 | 說明 |
|------|----------|------|
| `src/xxx.py` | 100-120 | <說明> |

## 6. 下一步

- [ ] <待辦事項>
```

### 5. 更新 Issue（選擇性）

如果調查有明確結論，可以在 Issue 留言：

```bash
gh issue comment <NUMBER> --body "調查報告已建立：docs/investigations/issue-<NUMBER>.md"
```

## 注意事項

- 即使無法完成調查，也要產生報告記錄目前進度
- 報告應包含足夠資訊讓下次 session 可以接續
- 若發現相關 Issue，在報告中標註關聯
