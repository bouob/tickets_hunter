# Active Polling Pattern（主動輪詢機制）

**文件說明**：定義冷卻刷新期間的主動輪詢標準模式，確保不錯過快速出現的機會
**適用階段**：Stage 4（日期選擇）、Stage 5（區域選擇）、其他需要刷新重試的場景
**最後更新**：2025-12-17

---

## 概述

### 問題背景

在搶票過程中，當頁面需要刷新重試時，通常會有一個冷卻間隔（`auto_reload_page_interval`）。傳統實作使用單一 `sleep()` 等待整個間隔，導致：

- **錯過快速出現的票**：票可能在等待期間出現，但 bot 在睡眠中
- **反應延遲**：必須等完整個間隔才能檢測
- **時機流失**：熱門票券可能在幾秒內售罄

### 解決方案

**Active Polling Pattern**：將單一長等待拆分為多次短輪詢，每次輪詢檢查目標元素是否出現。

```
傳統模式：[reload] ──────── 8s sleep ────────→ [check]
                          ↑
                     票出現但沒偵測到

Active Polling：[reload] → [0.5s check] → [0.5s check] → ... → [found!]
                                ↑
                           立即偵測並處理
```

---

## 核心設計

### 設計原則

| 原則 | 說明 |
|------|------|
| **總時間不變** | 維持使用者設定的 `auto_reload_page_interval` |
| **輪詢間隔** | 固定 0.2 秒（快速反應，最小化錯過機會） |
| **早期發現早期處理** | 偵測到目標立即中斷等待，執行後續邏輯 |
| **自動計算** | 輪詢次數根據設定自動計算：`poll_count = interval * 5` |

### 標準公式

```python
poll_count = int(interval * 5)  # interval 秒 ÷ 0.2 秒 = 輪詢次數
```

| 設定秒數 | 輪詢次數 | 說明 |
|----------|----------|------|
| 5s | 25 次 | 每 0.2s 檢查 |
| 8s | 40 次 | 每 0.2s 檢查（預設） |
| 10s | 50 次 | 每 0.2s 檢查 |
| 15s | 75 次 | 每 0.2s 檢查 |

---

## 標準實作模板

### Python (NoDriver) 模板

```python
# Active Polling Pattern - 標準模板
interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
if interval > 0:
    if show_debug_message:
        print(f"[STAGE SELECT] Waiting up to {interval}s with active polling...")

    # Poll every 0.2s during the wait period
    poll_count = int(interval * 5)
    for poll_idx in range(poll_count):
        await asyncio.sleep(0.2)
        try:
            # 檢查目標元素是否出現
            el = await tab.wait_for('TARGET_SELECTOR', timeout=0.1)
            if el:
                if show_debug_message:
                    print(f"[STAGE DELAYED] Elements detected after {(poll_idx + 1) * 0.2:.1f}s")
                # 發現元素，執行後續邏輯
                break  # 或 return 重新執行選擇函數
        except:
            pass

    if not el:
        if show_debug_message:
            print(f"[STAGE DELAYED] No elements detected during {interval}s polling")
```

### 參數說明

| 參數 | 值 | 說明 |
|------|-----|------|
| `asyncio.sleep()` | 0.2 | 輪詢間隔（秒） |
| `wait_for timeout` | 0.1 | 元素等待超時（秒），應小於輪詢間隔 |
| `TARGET_SELECTOR` | 依場景 | CSS 選擇器，見下方對照表 |

---

## 應用場景

### Stage 4: 日期選擇

**檔案**：`nodriver_tixcraft.py`
**函數**：`nodriver_tixcraft_date_auto_select()`
**行號**：4971-4991

**目標選擇器**：
```python
'.btn-group .btn-primary, .auto-continue-info a, .btn-group button'
```

**行為**：偵測到日期按鈕後，重新執行日期選擇函數。

---

### Stage 5: 區域選擇

**檔案**：`nodriver_tixcraft.py`
**函數**：`nodriver_tixcraft_area_auto_select()`
**行號**：5117-5137

**目標選擇器**：
```python
'.zone a'
```

**行為**：偵測到區域連結後，執行關鍵字匹配和點擊邏輯。

---

## 平台選擇器對照表

| 平台 | 階段 | 選擇器 | 說明 |
|------|------|--------|------|
| TixCraft | 日期 | `.btn-group .btn-primary` | 日期按鈕 |
| TixCraft | 區域 | `.zone a` | 區域連結 |
| iBon | 日期 | Shadow DOM (CDP) | 需使用 DOMSnapshot |
| KKTIX | 區域 | `.ticket-unit` | 票種區塊 |
| TicketPlus | 區域 | `.expansion-panel` | 展開面板 |

---

## 實作檢查清單

### 必要條件
- [ ] 確認有 `auto_reload_page_interval` 設定
- [ ] 確認選擇器能正確定位目標元素
- [ ] 確認 `wait_for timeout` 小於輪詢間隔

### 日誌輸出
- [ ] 開始輪詢：`Waiting up to {X}s with active polling...`
- [ ] 早期發現：`Elements detected after {X}s`
- [ ] 未發現：`No elements detected during {X}s polling`

### 行為驗證
- [ ] 總等待時間符合設定
- [ ] 早期發現時立即執行後續邏輯
- [ ] 輪詢期間不阻塞其他功能

---

## 效能分析

### 優勢

| 指標 | 傳統模式 | Active Polling | 改善 |
|------|----------|----------------|------|
| 最快反應時間 | 8s | 0.2s | **40x** |
| 平均反應時間 | 8s | ~4s | **2x** |
| 錯過機會率 | 高 | 極低 | 顯著降低 |

### 系統負載

- **CPU**：輕微增加（每 0.2s 一次 DOM 查詢，每秒 5 次）
- **網路**：無額外網路請求
- **記憶體**：無影響

---

## 常見問題 FAQ

### Q1: 為什麼選擇 0.2 秒輪詢間隔？

**A**: 最大化反應速度：
- 0.2s 間隔可在最快 0.2 秒內偵測到新出現的元素
- 相比 0.5s，反應速度提升 2.5 倍
- 系統負載仍在可接受範圍內（每秒 5 次 DOM 查詢）

### Q2: wait_for timeout 為什麼設 0.1 秒？

**A**: 確保 `timeout + 處理時間 < 輪詢間隔`：
- timeout = 0.1s
- 處理時間 ≈ 0.05s
- 總計 ≈ 0.15s < 0.2s（輪詢間隔）

### Q3: 是否需要在所有平台都實作？

**A**: 建議在有刷新重試邏輯的場景都實作：
- TixCraft: ✅ 已實作（日期、區域）
- iBon: 建議實作（需適配 Shadow DOM）
- KKTIX: 建議實作
- TicketPlus: 建議實作

### Q4: 如何處理 Shadow DOM（如 iBon）？

**A**: 使用 CDP DOMSnapshot 而非普通選擇器：
```python
# iBon 專用：使用 CDP 檢查
search_id, result_count = await tab.send(
    cdp.dom.perform_search(query='button.purchase-btn')
)
if result_count > 0:
    # 發現元素
    break
```

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2025-12-17 | 初版：建立 Active Polling Pattern 文件 |
| | | 實作 TixCraft 日期選擇 Active Polling |
| | | 實作 TixCraft 區域選擇 Active Polling |

---

## 相關文件

- [04-date-selection.md](./04-date-selection.md) - 日期選擇機制
- [05-area-selection.md](./05-area-selection.md) - 區域選擇機制
- [12-error-handling.md](./12-error-handling.md) - 錯誤處理與重試
- [NoDriver API 指南](../06-api-reference/nodriver_api_guide.md) - wait_for 用法

---

**維護者**：Tickets Hunter 開發團隊
