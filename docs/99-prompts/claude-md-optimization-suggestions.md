# CLAUDE.md 提示詞優化建議

**文檔版本**: v1.0
**建立日期**: 2025-11-09
**狀態**: 待審核

---

## 📊 分析摘要

### 現有 CLAUDE.md 的優點
- ✅ 清晰的層次結構
- ✅ 豐富的文件索引
- ✅ 強調憲法遵循（核心原則突出）
- ✅ 場景導向的導航（初次接手、開發新功能、除錯）
- ✅ Git 安全規則明確且嚴格

### 識別的優化機會
1. **資訊層次問題** - 最常用的資訊（快速除錯、測試）不在最前面
2. **冗長度問題** - Git 推送安全規則占據 40+ 行，影響快速瀏覽
3. **導航效率** - 缺少速查表和快速入口
4. **決策支援** - 缺少任務類型自動判斷機制
5. **內容重複** - 憲法在多處被提及

---

## 🎯 核心優化建議

### 1. 重組資訊層次（信息金字塔）

**原則**：最常用的資訊放在最前面

**建議結構**：
```
1. 🚀 Quick Start（快速入口）← 新增
   - 常見任務速查表
   - 關鍵指令速查
   - 緊急除錯入口

2. 🧭 任務類型決策樹（增強版）
   - 自動判斷：Bug修復 vs 新功能 vs 文檔
   - 每種任務的快速路徑

3. 📚 憲法與核心原則（保持）
   - 簡化為要點
   - 詳細內容指向 constitution.md

4. 📖 文件導航（簡化）
   - 合併相似區塊
   - 使用摺疊區塊

5. 🛠️ 詳細指南（移到後段）
   - Git 工作流程（簡化，詳細內容移到 docs/）
   - Accept Edits On 工作流程
   - speckit 工作流程
```

### 2. 新增速查表區塊

**目的**：AI 能在 3 秒內找到最常用的資訊

**建議內容**：
```markdown
## 🚀 Quick Reference（速查表）

### 最常見任務 3 步驟

#### 🐛 Bug 修復
1. 檢查規格：`specs/001-ticket-automation-system/spec.md`
2. 查找函數：`docs/02-development/structure.md`
3. 測試指令：`timeout 30 python -u src/nodriver_tixcraft.py ...`

#### ✨ 新增功能
1. 查閱標準：`docs/02-development/ticket_automation_standard.md`
2. 參考實作：`docs/03-mechanisms/`
3. 編寫代碼：`docs/02-development/coding_templates.md`

#### 📝 文件更新
1. 同步代碼：憲法第 VIII 條
2. 更新 Changelog：`docs/10-project-tracking/accept_changelog.md`
3. 執行分析：`/speckit.analyze`（如適用）

### 關鍵指令速查

| 任務 | 指令 | 說明 |
|------|------|------|
| 提交變更 | `/gsave` | 自動分離公開/機敏檔案 |
| 推送代碼 | `/gpush` | 推送到私人庫 |
| 推送機敏 | `/privatepush` | 推送文檔/設定 |
| 發布 | `/publicpr` | 建立 PR 到公開庫 |
| 快速測試 | `timeout 30 python ...` | 30 秒測試 |
| 規格分析 | `/speckit.analyze` | 一致性檢查 |

### 緊急除錯 5 步驟

1. 讀取錯誤訊息：`.temp/test_output.txt`
2. 檢查規格：`specs/001-ticket-automation-system/spec.md`（FR-xxx, SC-xxx）
3. 查找 API：`docs/06-api-reference/nodriver_api_guide.md`
4. 搜尋案例：`docs/08-troubleshooting/README.md`
5. 啟用詳細日誌：`config_dict["advanced"]["verbose"] = True`
```

### 3. 精簡 Git 工作流程區塊

**問題**：當前 Git 區塊占據 120-160 行，太長

**建議**：
```markdown
## 🔗 Git 工作流程（核心要點）

**⚠️ 安全規則（NON-NEGOTIABLE）**：
- ✅ 只推送到私人庫（`private`）
- ❌ 嚴禁直接推送到公開庫（`origin`）

**標準流程**：
```bash
/gsave          # 提交變更
/gpush          # 推送公開代碼
/privatepush    # 推送機敏檔案
/publicpr       # 發布到公開庫（僅發布時）
```

**詳細說明**：查閱 `docs/12-git-workflow/dual-repo-workflow.md`

---
```

**移動詳細內容到**：`docs/12-git-workflow/git-safety-rules.md`（新建）

### 4. 增強任務類型決策樹

**目的**：幫助 AI 快速判斷當前任務類型

**建議**：
```markdown
## 🧭 任務類型自動判斷

### 識別關鍵詞 → 任務類型 → 工作流程

| 用戶提及 | 任務類型 | 優先查閱 | 工作流程 |
|----------|----------|----------|----------|
| "修復"、"錯誤"、"bug" | Bug 修復 | Spec → structure.md → troubleshooting | 快速除錯流程 |
| "新增"、"實作"、"開發" | 新功能 | 12-Stage Standard → mechanisms | 開發流程 |
| "文檔"、"說明"、"註解" | 文件更新 | documentation_workflow.md | 文件同步流程 |
| "測試"、"驗證" | 測試執行 | testing_execution_guide.md | 測試流程 |
| "優化"、"重構" | 代碼改進 | 憲法第 III 條（三問法則） | 三問決策 |
| "規格"、"設計" | 規格驅動 | speckit 工作流程 | speckit 流程 |

### 平台識別 → 特定指南

| 提及平台 | 優先查閱 | 常見問題 |
|----------|----------|----------|
| TixCraft | `structure.md` TixCraft 區塊 | Cookie 登入 |
| iBon | `shadow_dom_pierce_guide.md` | Shadow DOM |
| KKTIX | `structure.md` KKTIX 區塊 | 排隊處理 |
| TicketPlus | `structure.md` TicketPlus 區塊 | 展開面板 |
| KHAM | `structure.md` KHAM 區塊 | 自動座位 |
```

### 5. 優化憲法遵循聲明

**問題**：憲法在多處被重複提及

**建議**：
```markdown
## 📜 憲法與核心原則

**最高指導原則**：`.specify/memory/constitution.md`（必須遵循）

**9 大核心原則**（速記）：
1. **NoDriver First** - 技術優先級
2. **資料結構優先** - 設計先於實作
3. **三問法則** - 核心？簡單？相容？
4. **單一職責** - 小函數組合
5. **設定驅動** - settings.json 控制
6. **測試驅動** - 核心修改必測
7. **MVP 原則** - 最小可行產品
8. **文件同步** - 文件是代碼一部分
9. **Git 規範** - 英文主題行、gsave

**使用方式**：
- 開發前：查詢相關原則（如：重構 → 查第 III 條）
- 代碼審查：對照憲法標準
- 違反憲法：必須拒絕

**詳細規範**：查詢 `.specify/memory/constitution.md`

---
```

### 6. 合併常見問題索引

**建議**：將「常見問題索引」與「核心文件索引」合併

**優化後**：
```markdown
## 📚 文件導航與常見問題

### 按任務類型查找

#### 🐛 除錯問題
- **函數定位** → `docs/02-development/structure.md`
- **規格驗證** → `docs/05-validation/spec-validation-matrix.md`
- **NoDriver API** → `docs/06-api-reference/nodriver_api_guide.md`
- **CDP 協議** → `docs/06-api-reference/cdp_protocol_reference.md`
- **除錯方法** → `docs/07-testing-debugging/debugging_methodology.md`
- **修復記錄** → `docs/08-troubleshooting/README.md`

#### 🏗️ 開發新功能
- **12 階段標準** → `docs/02-development/ticket_automation_standard.md`
- **日期選擇** → `docs/03-mechanisms/04-date-selection.md`
- **區域選擇** → `docs/03-mechanisms/05-area-selection.md`
- **驗證碼處理** → `docs/03-mechanisms/07-captcha-handling.md`

#### 🌐 特定技術
- **Shadow DOM** → `docs/06-api-reference/shadow_dom_pierce_guide.md`
- **選擇器優化** → `docs/06-api-reference/nodriver_selector_analysis.md`
- **驗證碼辨識** → `docs/06-api-reference/ddddocr_api_guide.md`

#### 🎫 平台問題
- **ibon Cookie** → `docs/08-troubleshooting/ibon_cookie_troubleshooting.md`
- **ibon NoDriver** → `docs/08-troubleshooting/ibon_nodriver_fixes_2025-10-03.md`

<details>
<summary>完整文件樹（點擊展開）</summary>

（原有的詳細文件導航內容移到這裡）

</details>
```

### 7. 簡化測試指令區塊

**建議**：將詳細的測試指令移到獨立文檔

**優化後**：
```markdown
## 🧪 快速測試

**前置要求**：刪除 `MAXBOT_INT28_IDLE.txt`

**NoDriver 快速測試**：
```bash
cd /d/Desktop/MaxBot搶票機器人/tickets_hunter && \
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**檢查輸出**：
```bash
grep "\[DATE KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
```

**詳細測試指南**：`docs/07-testing-debugging/testing_execution_guide.md`

---
```

---

## 📋 優化後的完整結構建議

```
# CLAUDE.md

## 🚀 Quick Reference（速查表）← 新增
   - 最常見任務 3 步驟
   - 關鍵指令速查
   - 緊急除錯 5 步驟

## 🧭 任務類型自動判斷 ← 增強
   - 識別關鍵詞 → 任務類型
   - 平台識別 → 特定指南

## 📜 憲法與核心原則 ← 精簡
   - 9 大原則速記
   - 使用方式

## 🎯 開發策略：NoDriver First ← 保持

## 📚 文件導航與常見問題 ← 合併
   - 按任務類型查找
   - 摺疊詳細內容

## 🔗 Git 工作流程 ← 精簡
   - 核心要點
   - 標準流程
   - 詳細內容指向 docs/

## 🔧 Accept Edits On 工作流程 ← 保持

## 🧪 快速測試 ← 精簡
   - 核心指令
   - 詳細內容指向 docs/

## 📐 程式碼規範 ← 保持

## 🏗️ speckit 工作流程 ← 保持

## 💡 使用原則 ← 保持
```

---

## 🎯 優先級建議

### 高優先級（立即實施）
1. ✅ 新增「Quick Reference」區塊
2. ✅ 增強「任務類型決策樹」
3. ✅ 精簡 Git 工作流程區塊

### 中優先級（建議實施）
4. ✅ 合併「常見問題索引」與「核心文件索引」
5. ✅ 簡化測試指令區塊
6. ✅ 優化憲法遵循聲明

### 低優先級（可選）
7. ⚪ 使用摺疊區塊減少滾動
8. ⚪ 增加更多視覺提示

---

## 📊 預期效果

### 量化指標
- **快速查找時間**：從 30 秒降低到 5 秒
- **文檔長度**：從 399 行降低到 280 行（-30%）
- **決策效率**：增加任務類型自動判斷（新功能）

### 定性改善
- ✅ 更快找到最常用資訊
- ✅ 更清晰的任務導向
- ✅ 減少滾動和搜尋
- ✅ 更好的新手體驗

---

## 📝 實施建議

1. **漸進式優化**：先實施高優先級項目，觀察效果
2. **保留備份**：建立 `CLAUDE.md.backup` 作為備份
3. **文檔遷移**：創建以下新文檔：
   - `docs/12-git-workflow/git-safety-rules.md`（Git 詳細規則）
   - `docs/11-prompts/quick-reference.md`（速查表擴展版）
4. **迭代優化**：根據實際使用效果調整

---

## 🔄 版本控制建議

**建議版本號**：
- 當前版本：`CLAUDE.md v1.0`（現有版本）
- 優化版本：`CLAUDE.md v2.0`（優化後版本）

**變更日誌**：記錄於 `docs/11-prompts/claude-md-changelog.md`

---

## 附錄：需要新建的文檔

### 1. docs/12-git-workflow/git-safety-rules.md
詳細的 Git 推送安全規則（從 CLAUDE.md 移出）

### 2. docs/11-prompts/quick-reference.md
擴展版的速查表（供快速參考）

### 3. docs/11-prompts/claude-md-changelog.md
CLAUDE.md 的變更歷史記錄
