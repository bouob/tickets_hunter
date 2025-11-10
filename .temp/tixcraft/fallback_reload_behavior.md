# Fallback 與 Auto Reload 行為說明

**版本**: 2025-11-08
**適用平台**: TixCraft, KKTIX, TicketPlus, ibon, KHAM

---

## 📖 設定檔說明

### 相關設定項目

```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "02/01,2026/02/01"
  },
  "area_auto_select": {
    "enable": true,
    "area_keyword": "特A座位區,VIP"
  },
  "date_auto_fallback": true,   // 日期回退開關
  "area_auto_fallback": false,  // 區域回退開關
  "advanced": {
    "auto_reload_page_interval": 5  // 刷新間隔（秒）
  }
}
```

---

## 🎯 三種需要自動 Reload 的場景

### 場景 1: Fallback 關閉 + 關鍵字沒匹配

**設定範例**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP"
  },
  "area_auto_fallback": false  // ← 關閉 fallback
}
```

**實際情況**:
- 頁面只有「普通區」，沒有「VIP」
- 關鍵字匹配失敗

**行為**:
- ❌ 舊邏輯: 直接停止，等待手動介入
- ✅ 新邏輯: **不選擇任何區域**，但**每 5 秒自動刷新頁面**，持續監控是否釋出「VIP」

**日誌輸出**:
```
[AREA KEYWORD] All keywords failed to match
[AREA FALLBACK] area_auto_fallback=false, fallback is disabled
[AREA SELECT] No area selected, will reload page and retry
(等待 5 秒後自動刷新)
```

---

### 場景 2: Fallback 開啟 + 全部票種售完

**設定範例**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP"
  },
  "area_auto_fallback": true  // ← 開啟 fallback
}
```

**實際情況**:
- 頁面沒有「VIP」區
- 嘗試 fallback 選擇其他區域（如「普通區」）
- **但所有區域都已售完**（被 `keyword_exclude` 過濾或標示為「已售完」）

**行為**:
- ✅ 嘗試 fallback 選擇其他票種
- ✅ 發現全部售完（`matched_blocks` 為空）
- ✅ **不選擇任何區域**，但**每 5 秒自動刷新頁面**，持續監控是否釋出新票

**日誌輸出**:
```
[AREA KEYWORD] All keywords failed to match
[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback
[AREA FALLBACK] Selecting available area based on area_select_order='from top to bottom'
[AREA FALLBACK] No available options after exclusion
[AREA SELECT] Will reload page and retry
(等待 5 秒後自動刷新)
```

---

### 場景 3: Fallback 開啟 + 成功找到替代票種

**設定範例**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP"
  },
  "area_auto_fallback": true
}
```

**實際情況**:
- 頁面沒有「VIP」區
- 但有「普通區」可選

**行為**:
- ✅ 嘗試 fallback
- ✅ **自動選擇「普通區」並購票**
- ❌ 不再刷新頁面（因為已經選擇了票種）

**日誌輸出**:
```
[AREA KEYWORD] All keywords failed to match
[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback
[AREA SELECT] Selected area: 普通區 (fallback)
(點擊並進入下一步)
```

---

## 📊 完整行為對照表

| 場景 | `fallback` | 關鍵字匹配 | 可用票種 | 行為 | 是否 Reload |
|------|-----------|----------|---------|------|-----------|
| **1** | `false` | ❌ 失敗 | 有其他票種 | **不選擇**，持續監控 | ✅ 是（每 N 秒） |
| **2** | `true` | ❌ 失敗 | ❌ 全部售完 | **不選擇**，持續監控 | ✅ 是（每 N 秒） |
| **3** | `true` | ❌ 失敗 | ✅ 有其他票種 | **選擇替代票種** | ❌ 否（已購票） |
| **4** | `true` | ✅ 成功 | ✅ 有指定票種 | **選擇指定票種** | ❌ 否（已購票） |
| **5** | `false` | ✅ 成功 | ✅ 有指定票種 | **選擇指定票種** | ❌ 否（已購票） |

---

## 🔧 技術實作細節

### 修改位置 (TixCraft Area 為例)

#### 修改點 1: Line 3092-3097 (fallback=false)

**修改前**:
```python
else:
    # Fallback disabled - strict mode
    print("[AREA FALLBACK] fallback is disabled")
    print("[AREA SELECT] Waiting for manual intervention")
    return False  # ❌ 直接返回，不 reload
```

**修改後**:
```python
else:
    # Fallback disabled - strict mode (no selection, but still reload)
    print("[AREA FALLBACK] fallback is disabled")
    print("[AREA SELECT] No area selected, will reload page and retry")
    # 不返回，讓後續 reload 邏輯執行
    # matched_blocks 保持 None (不選擇任何票種)
    # is_need_refresh 保持 True (會觸發 reload)
```

#### 修改點 2: Line 3104-3108 (全部售完)

**修改前**:
```python
if matched_blocks is None or len(matched_blocks) == 0:
    print("[AREA FALLBACK] No available options after exclusion")
    return False  # ❌ 直接返回，不 reload
```

**修改後**:
```python
if matched_blocks is None or len(matched_blocks) == 0:
    print("[AREA FALLBACK] No available options after exclusion")
    print("[AREA SELECT] Will reload page and retry")
    # 不返回，讓後續 reload 邏輯執行
    is_need_refresh = True  # 確保 reload 會執行
```

#### Reload 邏輯 (Line 3133-3142，已存在)

```python
# Auto refresh if needed
if is_need_refresh:
    try:
        await tab.reload()
    except:
        pass

    interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
    if interval > 0:
        await asyncio.sleep(interval)
```

---

## 🎮 使用情境範例

### 情境 1: 嚴格模式補票（只買 VIP）

**目標**: 只想買 VIP，其他區域都不要

**設定**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP"
  },
  "area_auto_fallback": false,  // ← 嚴格模式
  "advanced": {
    "auto_reload_page_interval": 3
  }
}
```

**執行流程**:
1. 10:00:00 - 進入區域選擇頁，只有「普通區」
2. 10:00:00 - 關鍵字「VIP」沒匹配 → 不選擇
3. 10:00:03 - 自動刷新頁面
4. 10:00:03 - 仍然只有「普通區」→ 不選擇
5. 10:00:06 - 自動刷新頁面
6. ...持續監控...
7. 10:05:30 - 刷新後發現釋出「VIP」區！
8. 10:05:30 - ✅ 自動選擇「VIP」並購票

**優點**: 確保只買到想要的票種
**缺點**: 如果「VIP」一直沒釋出，就永遠買不到

---

### 情境 2: 彈性補票（優先 VIP，但接受其他）

**目標**: 優先買 VIP，但如果沒有就買其他區域

**設定**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP,搖滾區"
  },
  "area_auto_fallback": true,  // ← 彈性模式
  "advanced": {
    "auto_reload_page_interval": 3
  }
}
```

**執行流程**:
1. 10:00:00 - 進入區域選擇頁，只有「普通區」
2. 10:00:00 - 關鍵字「VIP」「搖滾區」都沒匹配
3. 10:00:00 - 觸發 fallback，✅ **選擇「普通區」並購票**

**優點**: 提高搶票成功率，先搶到票
**缺點**: 可能買到不想要的票種

---

### 情境 3: 彈性補票但全部售完

**目標**: 優先買 VIP，但如果沒有就買其他區域

**設定**: 同情境 2

**執行流程**:
1. 10:00:00 - 進入區域選擇頁，**全部區域都已售完**
2. 10:00:00 - 關鍵字沒匹配
3. 10:00:00 - 觸發 fallback，但發現全部售完 → 不選擇
4. 10:00:03 - 自動刷新頁面
5. ...持續監控...
6. 10:05:30 - 刷新後發現釋出「普通區」
7. 10:05:30 - ✅ 自動選擇「普通區」並購票

**優點**: 即使全部售完，也會持續監控補票
**缺點**: 無

---

## ⚙️ `auto_reload_page_interval` 設定建議

### 建議值

| 場景 | 建議值（秒） | 說明 |
|------|------------|------|
| **熱門演唱會** | 1-3 秒 | 票釋出很快，需要快速反應 |
| **一般活動** | 3-5 秒 | 平衡速度與伺服器負擔 |
| **冷門活動** | 5-10 秒 | 降低伺服器壓力 |

### 注意事項

1. **不建議設為 0**:
   - `auto_reload_page_interval = 0` 會立即刷新
   - 可能導致過度頻繁刷新，被伺服器封鎖

2. **過快的風險**:
   - 間隔 < 1 秒：可能被視為攻擊
   - 建議最低 1 秒

3. **過慢的風險**:
   - 間隔 > 10 秒：可能錯過釋出的票

---

## 🚨 常見問題

### Q1: 設定 `fallback=false` 但程式沒有持續刷新？

**檢查項目**:
1. 確認 `auto_reload_page_interval > 0`
2. 檢查是否已更新到最新版本代碼（修復後的版本）
3. 查看日誌是否出現 "will reload page and retry"

---

### Q2: 設定 `fallback=true` 但買到不想要的票種？

**原因**: Fallback 機制會在關鍵字沒匹配時，自動選擇其他可用票種

**解決方案**:
1. 改為 `fallback=false`（嚴格模式）
2. 或使用 `keyword_exclude` 排除不想要的票種

**範例**:
```json
{
  "area_auto_select": {
    "area_keyword": "VIP"
  },
  "keyword_exclude": "普通區,站席",  // ← 排除不想要的
  "area_auto_fallback": true
}
```

---

### Q3: 全部售完後會持續刷新多久？

**回答**: 會**無限期**持續監控，直到：
1. 有票釋出並成功購買
2. 手動停止程式
3. 觸發 `area_retry_count` 冷卻機制（每 15 分鐘冷卻 5 秒）

---

## 📝 版本更新記錄

### 2025-11-08 (本次修復)

**修復項目**:
- ✅ `fallback=false` 時，關鍵字沒匹配會持續 reload
- ✅ `fallback=true` 時，全部售完會持續 reload
- ✅ 所有平台統一行為 (TixCraft, KKTIX, TicketPlus, ibon, KHAM)

**修復前行為**:
- ❌ `fallback=false` → 直接停止，不 reload
- ❌ 全部售完 → 直接停止，不 reload

**修復後行為**:
- ✅ `fallback=false` → 持續 reload 監控
- ✅ 全部售完 → 持續 reload 監控

---

## 🔗 相關文件

- 功能規格: `specs/001-ticket-automation-system/spec.md`
- 代碼實作: `src/nodriver_tixcraft.py`
- 測試指南: `docs/07-testing-debugging/testing_execution_guide.md`

---

**總結**: 修復後，無論是嚴格模式還是彈性模式，只要沒有成功選擇票種，系統都會根據 `auto_reload_page_interval` 持續刷新頁面進行補票監控。
