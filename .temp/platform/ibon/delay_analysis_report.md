# iBon NoDriver 延遲分析報告

**分析日期**：2025-12-27
**分析範圍**：`src/nodriver_tixcraft.py` 中所有 ibon 相關函數

---

## 1. 摘要

經過全面分析，iBon 相關程式碼中的延遲機制已經過優化，大部分使用**動態等待**（輪詢直到條件滿足）而非固定硬編碼延遲。

| 延遲類型 | 數量 | 狀態 |
|----------|------|------|
| 動態等待（輪詢） | 5 處 | 已優化 |
| 可配置延遲（使用 config） | 3 處 | 使用者可調整 |
| 必要延遲（伺服器處理） | 6 處 | 必要保留 |
| **可優化的硬編碼延遲** | **4 處** | **建議優化** |

---

## 2. 已優化的動態等待機制

以下位置使用輪詢等待，會在條件滿足時立即繼續，無需固定等待：

### 2.1 日期按鈕偵測 (Line 10465-10488, 10835-10857)

```python
# 使用 CDP perform_search 快速輪詢，每 0.1 秒檢查一次
max_wait = 3  # 最大等待 3 秒（安全上限）
check_interval = 0.1  # 快速輪詢

while (time.time() - start_time) < max_wait:
    search_id, result_count = await tab.send(cdp.dom.perform_search(...))
    if result_count > 0:
        break  # 找到立即繼續
    await tab.sleep(check_interval)
```

**狀態**：已優化，找到按鈕會立即繼續

### 2.2 區域表格偵測 (Line 12421-12454)

```python
# 同樣使用快速輪詢偵測 TR 元素
max_wait = 3
check_interval = 0.1

while (time.time() - start_time) < max_wait:
    search_id, tr_count = await tab.send(cdp.dom.perform_search(
        query='tbody tr',
        include_user_agent_shadow_dom=True
    ))
    if tr_count > 0:
        break
    await tab.sleep(check_interval)
```

**狀態**：已優化

### 2.3 票數選擇元素等待 (Line 12946-12970)

```python
# 使用 JavaScript Promise 輪詢，每 100ms 檢查一次
# 最大等待 1.5 秒（已從 3 秒優化為 1.5 秒）
const maxAttempts = 15; // 15 * 100ms = 1.5 seconds max wait
const checkSelect = setInterval(() => {
    let select = document.querySelector('...');
    if (select) {
        clearInterval(checkSelect);
        resolve({ready: true});
    }
}, 100);
```

**狀態**：已優化，已從 30 次（3 秒）減少到 15 次（1.5 秒）

### 2.4 Cloudflare 驗證等待 (Line 12350-12400)

```python
# 等待 Cloudflare 驗證完成
cloudflare_max_wait = 15  # 最大 15 秒
cloudflare_check_interval = 0.5

while (time_module.time() - cloudflare_start_time) < cloudflare_max_wait:
    page_type_result = await tab.evaluate('''..detect cloudflare...''')
    if page_type_result != "cloudflare":
        break  # 驗證完成
    await tab.sleep(cloudflare_check_interval)
```

**狀態**：必要等待（Cloudflare 驗證無法加速）

---

## 3. 可配置延遲（使用者可調整）

以下延遲使用 `config_dict` 中的設定值，使用者可自行調整：

| 位置 | 設定項 | 預設值 | 說明 |
|------|--------|--------|------|
| Line 14906, 15012, 15054 等 | `auto_reload_page_interval` | 0 | 頁面重新載入間隔 |
| Line 15097, 15222, 15390 等 | `delay` (指數退避) | 0.5-2 秒 | 票數重試延遲 |

**建議**：維持現狀，使用者可在設定介面調整

---

## 4. 必要延遲（伺服器處理）

以下延遲是必要的，用於等待伺服器處理：

| 位置 (Line) | 延遲時間 | 原因 |
|-------------|----------|------|
| 13091 | 0.5-0.8 秒 | 等待頁面穩定後再截取驗證碼圖片 |
| 13501 | 0.2-0.6 秒 | 等待 alert 出現（驗證碼錯誤提示） |
| 13633 | 0.15-0.25 秒 | 等待 iBon 處理票數變更 |
| 13715 | 0.8-1.2 秒 | 等待 iBon 自動刷新驗證碼 |
| 15101 | 0.15-0.25 秒 | 等待 iBon 處理票數變更 |
| 10741, 10764 | 0.2-0.5 秒 | 按鈕點擊後等待頁面反應 |

**說明**：這些延遲對應 iBon 伺服器的處理時間，過快操作會導致失敗

---

## 5. 可優化的硬編碼延遲

以下是發現的可優化硬編碼延遲：

### 5.1 [中優先] Angular 頁面載入等待 (Line 11847-11851)

```python
# 目前：固定等待 1.2-1.4 秒
wait_time = random.uniform(0.6, 0.8)
await tab.sleep(wait_time)
await tab.sleep(0.6)  # 第二次固定等待
```

**建議**：改為動態等待 Angular 渲染完成

```python
# 建議：使用輪詢等待 Angular 元素
max_wait = 2.0
check_interval = 0.1
start_time = time.time()

while (time.time() - start_time) < max_wait:
    tr_count = await tab.evaluate('document.querySelectorAll("tbody tr").length')
    if tr_count > 0:
        break
    await tab.sleep(check_interval)
```

**預估改善**：平均減少 0.5-1.0 秒

---

### 5.2 [中優先] 登入後頁面重定向等待 (Line 14792, 14803, 14851)

```python
await tab.get(target_url)
await asyncio.sleep(2)  # 固定等待 2 秒
```

**建議**：使用頁面載入完成事件

```python
await tab.get(target_url)
# 等待頁面載入完成（NoDriver 內建支援）
await tab  # 或使用 tab.wait_for() 等待特定元素
```

**預估改善**：平均減少 1.0-1.5 秒

---

### 5.3 [低優先] 驗證碼圖片穩定等待 (Line 13091)

```python
await asyncio.sleep(random.uniform(0.5, 0.8))  # 固定等待
```

**說明**：此延遲用於等待驗證碼圖片完全渲染。可嘗試改為檢測圖片載入狀態，但風險較高（可能導致 OCR 失敗）。

**建議**：保持現狀或小幅減少至 0.3-0.5 秒測試

---

### 5.4 [低優先] 驗證碼刷新後等待 (Line 13715, 13821)

```python
await asyncio.sleep(random.uniform(0.8, 1.2))  # Wait for iBon auto-refresh
```

**說明**：iBon 驗證碼錯誤後會自動刷新，此延遲確保新驗證碼完全載入。

**建議**：可嘗試改為檢測驗證碼圖片 URL 變化，但需謹慎測試

---

## 6. 優化優先順序建議

| 優先順序 | 項目 | 預估改善 | 風險 |
|----------|------|----------|------|
| 1 | 登入後頁面重定向等待 | 1.0-1.5 秒 | 低 |
| 2 | Angular 頁面載入等待 | 0.5-1.0 秒 | 中 |
| 3 | 驗證碼圖片穩定等待 | 0.2-0.4 秒 | 中高 |
| 4 | 驗證碼刷新後等待 | 0.3-0.5 秒 | 高 |

---

## 7. 總結

**整體評估**：iBon 程式碼的延遲機制已經過優化，大部分關鍵路徑使用動態等待。

**主要發現**：
1. 日期/區域選擇使用快速輪詢（100ms interval），找到元素立即繼續
2. 票數選擇已優化為 1.5 秒上限（從原本 3 秒減半）
3. 可優化項目主要在登入流程和 Angular 頁面載入

**建議行動**：
- 優先處理 5.1 和 5.2（Angular 頁面載入和登入重定向）
- 驗證碼相關延遲謹慎處理，避免影響 OCR 準確率

---

## 8. 附錄：ibon 相關函數清單

| 函數名稱 | 行號 | 用途 |
|----------|------|------|
| `nodriver_ibon_login` | 9284 | Cookie 登入 |
| `nodriver_ibon_date_mode_select` | 9349 | 日期模式選擇 |
| `nodriver_ibon_date_auto_select_pierce` | 10423 | 日期自動選擇（pierce） |
| `nodriver_ibon_date_auto_select` | 10772 | 日期自動選擇（主入口） |
| `nodriver_ibon_date_auto_select_domsnapshot` | 10796 | 日期自動選擇（DOMSnapshot） |
| `check_ibon_login_status` | 11564 | 登入狀態檢查 |
| `nodriver_ibon_ticket_agree` | 11779 | 票務同意 |
| `nodriver_ibon_allow_not_adjacent_seat` | 11785 | 非連續座位設定 |
| `nodriver_ibon_event_area_auto_select` | 11816 | 區域選擇（Event 頁面） |
| `nodriver_ibon_area_auto_select` | 12288 | 區域選擇（orders 頁面） |
| `nodriver_ibon_ticket_number_auto_select` | 12925 | 票數選擇 |
| `nodriver_ibon_get_captcha_image_from_shadow_dom` | 13082 | 驗證碼圖片擷取 |
| `nodriver_ibon_keyin_captcha_code` | 13286 | 驗證碼輸入 |
| `nodriver_ibon_refresh_captcha` | 13533 | 驗證碼刷新 |
| `nodriver_ibon_auto_ocr` | 13567 | OCR 自動辨識 |
| `nodriver_ibon_captcha` | 13739 | 驗證碼主函數 |
| `nodriver_ibon_purchase_button_press` | 13836 | 購票按鈕點擊 |
| `nodriver_ibon_check_sold_out` | 13893 | 售罄檢查 |
| `nodriver_ibon_check_sold_out_on_ticket_page` | 13931 | 票頁售罄檢查 |
| `nodriver_ibon_fill_verify_form` | 14044 | 驗證表單填寫 |
| `nodriver_ibon_verification_question` | 14233 | 驗證問題處理 |
| `nodriver_tour_ibon_event_detail` | 14387 | tour.ibon 活動詳情 |
| `nodriver_tour_ibon_options` | 14443 | tour.ibon 選項 |
| `nodriver_tour_ibon_checkout` | 14587 | tour.ibon 結帳 |
| `nodriver_ibon_main` | 14729 | iBon 主函數 |
