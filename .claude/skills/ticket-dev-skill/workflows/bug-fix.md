# Bug 修復工作流程

快速定位並修復 Tickets Hunter 中的 Bug。

## 5 步驟流程

```
[1. 讀取錯誤] → [2. 檢查規格] → [3. 定位函數] → [4. 修復] → [5. 驗證]
```

---

## Step 1: 讀取錯誤

**檢查測試輸出**：
```bash
cat .temp/test_output.txt
```

**快速篩選**：
```bash
# 檢查錯誤
grep -i "ERROR\|WARNING\|failed" .temp/test_output.txt

# 檢查日期邏輯
grep "\[DATE KEYWORD\]\|\[DATE SELECT\]" .temp/test_output.txt

# 檢查區域邏輯
grep "\[AREA KEYWORD\]\|\[AREA SELECT\]" .temp/test_output.txt
```

---

## Step 2: 檢查規格

**入口**：`docs/05-validation/README.md`

**確認功能需求（FR-xxx）**：
- FR-017: 日期關鍵字匹配
- FR-018: 日期回退機制
- FR-058: 錯誤分類

**確認成功標準（SC-xxx）**：
- SC-002: 90% 關鍵字成功率
- SC-005: 95% 元素互動成功率

---

## Step 3: 定位函數

**函數索引**：`docs/02-development/structure.md`

**平台定位**：
| 平台 | 關鍵函數前綴 |
|------|-------------|
| TixCraft | `tixcraft_*` |
| iBon | `ibon_*` |
| KKTIX | `kktix_*` |
| TicketPlus | `ticketplus_*` |
| KHAM | `kham_*` |

**共用函數**：
- `util.py` - 通用工具
- `nodriver_util.py` - NoDriver 專用

---

## Step 4: 修復

**遵循憲法**：
- 第 II 條：util.py 改動需跨平台分析
- 第 IV 條：禁止 emoji in .py

---

## Step 5: 驗證

**快速測試**：
```bash
rm -f MAXBOT_INT28_IDLE.txt src/MAXBOT_INT28_IDLE.txt && \
timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json > .temp/test_output.txt 2>&1
```

**MCP 即時除錯**：
```
/mcpstart
```

**驗證重點**：
- [ ] 日期匹配數量正確
- [ ] 區域匹配數量正確
- [ ] 選擇策略正確執行
- [ ] 無新增錯誤

---

## 常見 Bug 速查

| 問題 | 原因 | 解決方案 |
|------|------|----------|
| 關鍵字不匹配 | 格式問題 | 檢查 `parse_keyword_string_to_array()` |
| Shadow DOM 找不到 | 選擇器失效 | 使用 DOMSnapshot API |
| 元素點擊無效 | Angular 事件 | 觸發 `dispatchEvent` |
| 驗證碼失敗 | OCR 辨識錯誤 | 啟用 `verbose` 查看圖片 |

---

## 相關文件

- `docs/08-troubleshooting/README.md` - 疑難排解索引
- `docs/10-project-tracking/issues-faq-tracking.md` - Issues FAQ
- `docs/07-testing-debugging/debugging_methodology.md` - 除錯方法論
