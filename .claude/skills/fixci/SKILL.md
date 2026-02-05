# FixCI Skill

自動修復 CI 測試失敗的迭代流程，持續修正直到全部通過。

## 使用方式

```
/fixci
/fixci pytest
/fixci "python -m pytest tests/"
```

若未指定測試指令，預設使用：
```bash
python -m pytest tests/ -v
```

---

## 自主修復原則

**核心理念**：持續迭代直到測試全綠，不要中途停止詢問。

- 每次修復後立即重新測試驗證
- 記錄每個失敗及其解決方式
- 區分測試 bug vs 實作 bug
- 只有窮盡合理方法才停止

---

## 執行流程

### Phase 1: 執行測試套件

```bash
# 執行完整測試
python -m pytest tests/ -v 2>&1 | tee test_output.txt

# 或指定的測試指令
<TEST_COMMAND> 2>&1 | tee test_output.txt
```

### Phase 2: 分析失敗

對每個失敗的測試：

1. **理解期望**
   - 測試名稱說明了什麼？
   - assertion 期望什麼結果？
   - 測試的前置條件是什麼？

2. **讀取相關程式碼**
   - 測試檔案的完整測試函數
   - 被測試的源碼函數
   - 相關的 fixture 或 mock

3. **判斷 bug 類型**

| 類型 | 特徵 | 修復目標 |
|------|------|----------|
| 測試 bug | 測試邏輯錯誤、過時的期望值 | 修改測試檔案 |
| 實作 bug | 程式碼邏輯錯誤 | 修改源碼檔案 |
| 環境問題 | 缺少依賴、路徑錯誤 | 修改設定或安裝依賴 |

### Phase 3: 修復與驗證迴圈

```
┌─────────────────────────────────────┐
│  1. 修復一個失敗                      │
│  2. 重新執行該測試驗證                 │
│  3. 通過 → 下一個失敗                 │
│     失敗 → 分析錯誤，再次修復          │
│  4. 重複直到全部通過                   │
└─────────────────────────────────────┘
```

單一測試驗證：
```bash
python -m pytest tests/test_xxx.py::test_function_name -v
```

### Phase 4: 記錄進度

使用 TodoWrite 記錄每個修復：

```
- [x] test_login_success: 修正 mock 回傳值格式
- [x] test_area_select: 更新過時的 selector
- [ ] test_date_parse: 調查中...
```

### Phase 5: 最終驗證

全部修復後，執行完整測試套件確認：

```bash
python -m pytest tests/ -v
```

確保：
- 所有測試通過
- 沒有新的失敗
- 沒有 warning（如可能）

### Phase 6: 提交變更

使用 `/gsave` 提交，訊息格式：

```
🧪 fix(tests): resolve CI failures

- test_xxx: <修復說明>
- test_yyy: <修復說明>
- src/zzz.py: <如有源碼修改>
```

---

## 常見失敗模式

| 錯誤類型 | 常見原因 | 修復方向 |
|----------|----------|----------|
| `AssertionError` | 期望值不符 | 檢查邏輯或更新期望 |
| `AttributeError` | API 變更 | 更新呼叫方式 |
| `ImportError` | 模組移動/重命名 | 修正 import 路徑 |
| `FileNotFoundError` | 測試資源遺失 | 建立或修正路徑 |
| `TimeoutError` | 非同步等待過短 | 增加 timeout |
| `MockError` | Mock 設定錯誤 | 修正 mock 配置 |

---

## 停止條件

只有以下情況才停止：

1. **全部通過** ✅ - 成功完成
2. **循環修復** - 同一測試反覆失敗 3 次以上
3. **依賴問題** - 需要安裝無法取得的套件
4. **環境限制** - 需要特定硬體/服務
5. **架構問題** - 需要重大重構才能修復

停止時產生報告說明剩餘問題。

---

## 專案特定測試指令

```bash
# 語法檢查（快速）
python -m py_compile src/nodriver_tixcraft.py

# 功能測試（30 秒 timeout）
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json

# pytest（如有）
python -m pytest tests/ -v
```
