# 增量規劃：NoDriver 遷移 + SDD/TDD 導入

**分支**：`001-ticket-automation-system` | **日期**：2025-10-19 | **狀態**：現有系統優化與測試驅動導入

---

## 執行摘要

您已完成了 **80%+ 的 NoDriver 實作工作**（6 個平台完成，功能完整）。本規劃文檔的目標是：

1. ✅ **將現有實作與規格對齐** - 識別代碼與需求的映射
2. ✅ **補充缺失的測試** - 導入 TDD/SDD 方法論
3. ✅ **優化與增強** - 特別是 iBon 平台與 DOM 處理
4. ✅ **建立文件化標準** - NoDriver API 模式總結

---

## 第一部分：現有實作評估

### 平台完成度矩陣

| 平台 | 狀態 | 完善度 | 速度 | 優化空間 | 優先度 |
|------|------|--------|------|---------|--------|
| **KKTIX** | ✅ 完成 | ⭐⭐⭐⭐⭐ | 最快 | 低（已最優） | 維護 |
| **TixCraft** | ✅ 完成 | ⭐⭐⭐⭐ | 快 | 中 | 維護 |
| **TicketPlus** | ✅ 完成 | ⭐⭐⭐⭐ | 中 | 中 | 維護 |
| **ticket.com.tw** | ✅ 完成 | ⭐⭐⭐ | 中 | 中 | 維護 |
| **KHAM** | ✅ 完成 | ⭐⭐⭐⭐ | 中 | 低 | 維護 |
| **iBon** | ✅ 完成 | ⭐⭐⭐⭐ | 中 | **高** | 🎯 優化目標 |

### 現有實作的技術債與優化機會

#### 1. iBon 平台優化機會（高優先度）

**當前問題**：
- Shadow DOM 處理複雜（需頻繁轉換）
- Angular SPA 狀態同步困難
- 座位選擇演算法可改進
- DOM 查詢效率可優化

**建議優化方向**：
```
1. Shadow DOM 快取機制 - 避免重複 flatten
2. MutationObserver 事件驅動 - 取代輪詢
3. 座位選擇演算法 - 預先計算相鄰性
4. CDP 批量命令 - 减少往返延遲
```

**預期收益**：iBon 速度可提升 30-50%

#### 2. DOM 處理模式標準化

**當前狀況**：
- 每個平台手動編寫 DOM 選擇邏輯
- NoDriver API 調用模式分散
- 沒有統一的錯誤處理模式

**建議標準化**：
```python
# 建立 NoDriver 操作的標準模式

## 模式 1: 元素查詢
async def find_element(driver, selector, timeout=5):
    """統一的元素查詢，支援 CSS、XPath、Text"""
    # 標準化實作

## 模式 2: DOM 修改
async def modify_element(driver, selector, action, value):
    """統一的 DOM 修改操作"""
    # 標準化實作

## 模式 3: Shadow DOM 處理
async def handle_shadow_dom(driver, selector):
    """統一的 Shadow DOM 處理"""
    # 標準化實作

## 模式 4: 事件驅動等待
async def wait_for_event(driver, event_type, timeout=10):
    """事件驅動的等待機制"""
    # 標準化實作
```

#### 3. 技術障礙：NoDriver API 頻繁查閱

**根本原因**：
- NoDriver API 文檔有學習曲線
- 每個平台的 DOM 結構都不同
- CDP 協議細節容易混淆

**解決方案**：
1. **建立 NoDriver 操作手冊** (`docs/nodriver-cookbook.md`)
   - CDP 常用操作速查表
   - 各平台 DOM 結構參考
   - 常見問題與解決方案

2. **抽象化 CDP 操作層** (`src/cdp_wrapper.py`)
   - 封裝 CDP 低層操作
   - 提供高層 Python API
   - 統一錯誤處理

3. **建立平台特定參考** (`docs/platform-dom-reference/`)
   - 每個平台的 DOM 結構圖
   - 選擇器匹配策略
   - 已知的 CDP 陷阱

---

## 第二部分：SDD/TDD 導入策略

### 現有測試狀態評估

```bash
# 檢查現有測試
find tests/ -name "*.py" -type f | wc -l
```

**預計結果**：測試覆蓋率 <30%（典型的前期項目）

### TDD/SDD 導入路徑

#### 階段 1：測試框架建立（第 1-2 週）

**目標**：建立完整的測試基礎設施

```
[ ] T1.1 安裝測試框架 (pytest + pytest-asyncio)
[ ] T1.2 建立 fixtures 與 mocks
[ ] T1.3 設定 CI/CD 測試運行
[ ] T1.4 建立測試覆蓋率追蹤 (coverage.py)
```

#### 階段 2：回歸測試補充（第 2-4 週）

**目標**：為現有實作編寫測試

```
優先度順序（根據平台完善度）：

1️⃣ KKTIX 回歸測試 (最優先 - 參考實作)
   - 12 個階段各 1-2 個測試
   - 關鍵路徑完整覆蓋

2️⃣ TixCraft 回歸測試
3️⃣ iBon 回歸測試 (優化前先測試)
4️⃣ TicketPlus、KHAM、ticket.com.tw 回歸測試
```

**每個平台測試模板**：
```python
# tests/integration/test_kktix_flow.py

class TestKKTIXAutomation:
    """KKTIX 完整流程測試"""

    async def test_kktix_end_to_end(self):
        """E2E: 完整購票流程"""
        # Given: 配置有效
        # When: 執行自動化
        # Then: 訂單成功

    async def test_date_selection_keyword_matching(self):
        """US2: 日期關鍵字匹配"""

    async def test_area_selection_with_exclusions(self):
        """US2: 區域選擇含排除"""

    async def test_error_recovery_retry_logic(self):
        """US7: 錯誤恢復與重試"""

    async def test_captcha_ocr_fallback(self):
        """US4: 驗證碼 OCR 回退"""
```

#### 階段 3：新功能 TDD（第 4 週後）

**規則**：所有新功能必須先寫測試

```
流程：
1. 在 spec.md 中添加需求
2. 編寫測試（紅色狀態）
3. 實作功能（綠色狀態）
4. 重構與優化（重構狀態）
5. 更新文檔
```

---

## 第三部分：優化工作計劃

### iBon 平台優化計劃（優先度：最高）

#### 優化目標
- 速度提升：30-50%
- 可靠性提升：從 95% → 98%+
- DOM 查詢最佳化：-40% 查詢次數

#### 優化任務

**T1: Shadow DOM 快取機制**
```
目標: 減少 Shadow DOM flatten 操作
工作:
  [ ] 分析 iBon 的 Shadow DOM 結構變化頻率
  [ ] 實作 Shadow DOM 快取層 (src/ibon_shadow_cache.py)
  [ ] 添加 MutationObserver 監控 Shadow DOM 變化
  [ ] 評估效能提升
```

**T2: 座位選擇演算法優化**
```
目標: 提升座位選擇速度與成功率
工作:
  [ ] 分析當前座位選擇邏輯的瓶頸
  [ ] 實作預先計算相鄰性檢查 (adjacency pre-calculation)
  [ ] 使用 CDP 批量命令減少往返
  [ ] A/B 測試新舊演算法
```

**T3: CDP 批量操作優化**
```
目標: 減少 CDP 往返延遲
工作:
  [ ] 識別 iBon 中的序列 CDP 調用
  [ ] 重組為批量操作
  [ ] 測試延遲改善
```

**T4: 回退策略強化**
```
目標: 提升 98%+ 成功率
工作:
  [ ] 識別當前失敗場景
  [ ] 新增 CDP 點擊 → JavaScript 點擊 回退
  [ ] 新增頁面重新整理 → 重試 回退
  [ ] 添加測試用例
```

---

## 第四部分：文件化與知識沉澱

### NoDriver 操作手冊生成

**文件**：`docs/nodriver-cookbook.md`

```markdown
# NoDriver 操作手冊

## 部分 1: CDP 常用操作速查

### 1.1 元素查詢
- CSS 選擇器
- XPath 查詢
- 文本匹配
- 組合查詢

### 1.2 元素互動
- 點擊 (CDP click vs JavaScript click)
- 輸入文本
- 提交表單
- 快捷鍵

### 1.3 DOM 檢查
- 元素存在性檢查
- 可見性檢查
- 啟用狀態檢查

### 1.4 等待機制
- 等待元素出現
- 等待元素消失
- 等待文本變化
- 等待事件

### 1.5 Shadow DOM 處理
- DOM flatten 技巧
- Shadow DOM 查詢
- 深層嵌套處理

## 部分 2: 平台 DOM 參考

### 2.1 KKTIX DOM 結構
- 日期選擇佈局
- 區域/座位佈局
- 表單結構

### 2.2 iBon DOM 結構
- Shadow DOM 層級
- Angular SPA 特性
- 座位圖互動

### 2.3 其他平台參考
...

## 部分 3: 常見陷阱

### 3.1 CDP 超時
- 原因分析
- 診斷方法
- 解決方案

### 3.2 DOM 變化導致查詢失敗
...

### 3.3 異步競態條件
...
```

### 平台實作參考指南

**文件**：`docs/platform-implementation-reference.md`

```markdown
# 平台實作參考指南

## 新平台實作清單

當添加新平台時，參考 KKTIX 實作：

[ ] 1. 平台識別邏輯
    - URL 模式匹配
    - 頁面標籤識別

[ ] 2. 登入流程
    - Cookie 注入
    - 表單登入

[ ] 3. 12 個階段的實作
    - 每個階段的 DOM 結構分析
    - 回退策略
    - 測試用例

[ ] 4. 效能優化
    - 瓶頸識別
    - 批量操作
    - 快取機制

[ ] 5. 測試覆蓋
    - E2E 測試
    - 邊界情況
    - 錯誤恢復
```

---

## 第五部分：技術債清單與優化機會

### 技術債評估

| 項目 | 嚴重性 | 工作量 | 優先度 | 目標完成 |
|------|--------|--------|--------|----------|
| iBon 性能優化 | 中 | 20 h | 🔴 最高 | 2-3 週 |
| 測試框架建立 | 中 | 15 h | 🔴 最高 | 1-2 週 |
| NoDriver 標準化 | 中 | 25 h | 🟠 高 | 3-4 週 |
| 文檔化完善 | 低 | 20 h | 🟡 中 | 4-5 週 |
| UC → NoDriver 完全遷移 | 低 | 10 h | 🟢 低 | 5-6 週 |

### 快速勝利機會

**可在 1-2 週內完成的優化**：

1. **iBon Shadow DOM 快取** (5-7 h)
   - 預期收益：20-30% 速度提升

2. **建立 NoDriver 操作包裝器** (8-10 h)
   - 預期收益：-40% API 調用代碼複雜度

3. **KKTIX 完整回歸測試** (10-15 h)
   - 預期收益：建立測試基準與參考實作

---

## 第六部分：後續計劃與里程碑

### 即時行動項目（本週）

- [ ] **Review 會議**：檢視現有 6 個平台的完成度
- [ ] **iBon 瓶頸分析**：深入分析性能瓶頸
- [ ] **NoDriver API 總結**：根據 6 平台經驗總結常用模式
- [ ] **測試框架選型**：確定 pytest 配置

### 短期（2-3 週）

**Sprint 1: iBon 優化 + 測試框架**
- 完成 Shadow DOM 快取
- 建立 pytest + pytest-asyncio 環境
- 編寫 KKTIX 回歸測試

**Sprint 2: 文檔化 + 標準化**
- 完成 NoDriver 操作手冊
- 實作 CDP 操作包裝器
- 標準化平台適配器模式

**Sprint 3: 測試補充**
- 為所有 6 個平台補充回歸測試
- 建立 CI/CD 測試運行
- 確保測試覆蓋率 > 60%

### 中期（1-2 月）

**優化迭代**：
- 完成所有已知的優化機會
- 處理使用者反饋
- UC 版本維護最小化

**功能增強**：
- 新增平台支持（如 Cityline、TicketMaster）
- 增強 OCR 驗證碼處理
- 多帳號支持

---

## 附錄 A：憲章對齐檢查

### 核心原則合規性（根據 constitution.md）

| 原則 | 當前狀態 | 檢查項目 | 建議 |
|------|---------|---------|------|
| **I. NoDriver First** | ✅ 符合 | UC 已廢棄，NoDriver 為主 | 繼續維護 UC 用於回退 |
| **II. 資料結構優先** | ✅ 符合 | 規格已定義所有實體 | 無需變更 |
| **III. 三問法則** | ✅ 符合 | 每個平台都解決核心問題 | 新平台時重新檢查 |
| **IV. 單一職責** | ⚠️ 部分 | 函數職責清晰但可再分解 | 優化 iBon 時重構 |
| **V. 設定驅動開發** | ✅ 符合 | settings.json 完整控制 | 無需變更 |
| **VI. 測試驅動穩定性** | ❌ 缺失 | 缺少回歸測試 | **優先建立** |
| **VII. MVP 原則** | ✅ 符合 | 6 個平台已達成 MVP | 繼續漸進式擴展 |
| **VIII. 文件與代碼同步** | ⚠️ 部分 | 代碼完整但文檔不完整 | **建立操作手冊** |
| **IX. Git 規範** | ✅ 符合 | 提交訊息規範 | 無需變更 |

### 憲章合規行動項

🔴 **優先度最高**：
- [ ] 建立 VI. 測試驅動穩定性 框架
- [ ] 完成 VIII. 文件與代碼同步 (NoDriver 手冊)

---

## 結論：建議的優化優先級

### 第 1 順位（本週完成）
1. **iBon Shadow DOM 快取優化** - 技術價值高，工作量小
2. **測試框架建立** - 支撐未來所有工作
3. **NoDriver 操作標準化** - 減少未來開發工作量

### 第 2 順位（2-3 週）
4. **KKTIX 回歸測試** - 建立測試基準
5. **NoDriver 操作手冊** - 減少 API 學習曲線

### 第 3 順位（3-4 週）
6. **所有平台回歸測試** - 確保穩定性
7. **文檔完善** - 知識沉澱

---

**規劃完成時間**：2025-10-19
**預計優化週期**：4-6 週
**團隊建議**：2-3 人並行
**下一步**：執行第 1 順位任務
