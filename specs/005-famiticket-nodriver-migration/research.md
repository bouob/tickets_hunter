# 技術研究：FamiTicket NoDriver 遷移

**功能分支**：`005-famiticket-nodriver-migration`
**研究日期**：2025-11-04
**目的**：為 FamiTicket NoDriver 遷移提供技術決策依據

---

## 研究任務 1：NoDriver API 最佳實踐

### 決策：元素搜尋策略

**選擇**：**Pierce 方法（優先）** + 傳統 CSS 選擇器（備用）

**理由**：
1. **速度優勢**：
   - Pierce 方法：60-70% 速度提升（根據 `docs/06-api-reference/nodriver_api_guide.md`）
   - 直接穿透 Shadow DOM，無需多步驟遍歷

2. **FamiTicket 適用性**：
   - Chrome 版本分析顯示 FamiTicket **不使用 Shadow DOM**
   - 標準 CSS 選擇器已足夠（`#usr_act`、`#usr_pwd`、`#buyWaiting` 等）
   - Pierce 方法的 Shadow DOM 穿透能力可作為未來保障（若 FamiTicket 改版導入 Shadow DOM）

3. **NoDriver 現有模式**：
   - TixCraft NoDriver 使用 Pierce 方法（參考 `src/nodriver_tixcraft.py`）
   - KKTIX NoDriver 使用 Pierce 方法
   - 成功驗證於多個平台，穩定性高

**實作方法**：
```python
# 使用 CDP perform_search (Pierce 方法)
search_id, count = await tab.send(cdp.dom.perform_search(
    query='#usr_act',  # CSS 選擇器
    include_user_agent_shadow_dom=True  # 支援 Shadow DOM 穿透
))

if count > 0:
    node_ids = await tab.send(cdp.dom.get_search_results(
        search_id=search_id, from_index=0, to_index=count
    ))
    # 後續操作...
```

**考慮過的替代方案**：
1. **DOMSnapshot 方法**：
   - 優點：可獲取完整 DOM 樹狀結構
   - 缺點：速度較慢（需要完整快照），記憶體消耗較高
   - **拒絕理由**：FamiTicket 頁面結構簡單，無需完整快照

2. **NoDriver 內建 `tab.select()`**：
   - 優點：語法簡潔
   - 缺點：底層仍使用 CDP，無額外優勢
   - **接受情境**：適用於簡單的單元素搜尋（如登入表單輸入框）

---

## 研究任務 2：CDP 點擊策略

### 決策：混合策略（CDP 優先 + JavaScript 備用）

**選擇**：
- **優先**：CDP `dispatch_mouse_event()`（真實滑鼠點擊）
- **備用**：NoDriver `element.click()`（當 CDP 失敗時）

**理由**：
1. **反偵測能力**：
   - CDP `dispatch_mouse_event` 模擬真實滑鼠座標點擊，行為更接近人類
   - JavaScript `element.click()` 可能被偵測為機器人行為（無滑鼠軌跡）
   - FamiTicket 是票務平台，可能有反機器人機制

2. **NoDriver 推薦做法**（根據 `docs/06-api-reference/cdp_protocol_reference.md`）：
   - CDP 點擊流程：
     1. 獲取元素位置（`cdp.dom.get_box_model`）
     2. 計算中心座標
     3. 派發 `mousePressed` 和 `mouseReleased` 事件
   - 優點：完全模擬真實使用者行為

3. **現有成功案例**：
   - TixCraft NoDriver：使用 CDP 點擊，成功繞過反機器人機制
   - KKTIX NoDriver：使用 CDP 點擊，通過驗證

**實作方法**：
```python
async def nodriver_click_element(tab, node_id, show_debug_message=False):
    try:
        # 獲取元素位置
        box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
        content_box = box_model.model.content

        # 計算中心座標
        x = int((content_box[0] + content_box[4]) / 2)
        y = int((content_box[1] + content_box[5]) / 2)

        # 派發點擊事件
        await tab.send(cdp.input.dispatch_mouse_event(
            type_='mousePressed', x=x, y=y, button='left', click_count=1
        ))
        await tab.send(cdp.input.dispatch_mouse_event(
            type_='mouseReleased', x=x, y=y, button='left', click_count=1
        ))
        return True
    except Exception as e:
        if show_debug_message:
            print(f"[CDP CLICK FAILED] {e}, falling back to element.click()")
        # 備用方案：使用 NoDriver 內建 click
        element = await tab.find_element_by_node_id(node_id)
        await element.click()
        return True
```

**考慮過的替代方案**：
1. **純 JavaScript 點擊**（`driver.execute_script("element.click()")`）：
   - 優點：快速、穩定
   - 缺點：容易被偵測，無滑鼠事件
   - **拒絕理由**：不符合 NoDriver First 原則，且反偵測能力差

2. **模擬滑鼠移動軌跡**（`moveTo` + `click`）：
   - 優點：更真實（有移動軌跡）
   - 缺點：增加複雜度與延遲，且 FamiTicket 可能不需要如此高程度的模擬
   - **接受情境**：若遇到反機器人機制失敗，可作為 Phase 2 增強

---

## 研究任務 3：Chrome 版本邏輯分析

### 關鍵發現

基於 `src/chrome_tixcraft.py` (lines 3141-6400) 的分析，FamiTicket Chrome 版本包含以下核心邏輯：

#### 1. **日期選擇邏輯**（`fami_date_auto_select`，Line 3380）

**核心流程**：
1. 掃描日期列表（`table.session__list > tbody > tr`）
2. 從每一列提取：
   - 日期文字（`td:nth-child(1)`）
   - 區域文字（`td:nth-child(2)`）
   - 購買按鈕（`button`，必須包含「立即購買」文字）
3. 關鍵字匹配：
   - 支援多關鍵字（逗號分隔），OR 邏輯
   - 使用 `format_keyword_string()` 正規化關鍵字
4. 回退機制：
   - 若無匹配 → 使用 `auto_select_mode`（從第一個可用日期選擇）
   - 若列表為空 → 觸發自動補票（若啟用）

**自動補票邏輯**（Line 3498-3510）：
```python
if auto_reload_coming_soon_page_enable:
    if not formated_area_list is None:
        if len(formated_area_list) == 0:
            # 重新載入活動頁面
            driver.get(last_activity_url)
            time.sleep(0.3)
            # 等待使用者設定的間隔
            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])
```

**關鍵差異（Chrome vs NoDriver）**：
- Chrome：`driver.get(url)` + `time.sleep()`
- NoDriver：`await tab.get(url)` + `await tab.sleep()`（非同步）

#### 2. **區域選擇邏輯**（`fami_area_auto_select`，Line 3514）

**核心流程**：
1. 掃描區域列表（`div > a.area`）
2. 過濾已停用區域（class 包含 `"area disabled"`）
3. 關鍵字匹配：
   - 支援 AND 邏輯（多關鍵字必須同時存在）
   - 使用 `in` 運算子檢查區域文字
4. 回退機制：
   - 若無匹配 → 使用 `auto_select_mode`

**關鍵程式碼模式**：
```python
# 過濾已停用區域
area_html_text = area_a.get_attribute('innerHTML')
if 'area disabled' in area_html_text:
    continue  # 跳過已停用區域

# AND 邏輯匹配
is_match_area = True
for area_keyword in area_keyword_item.split(','):
    if area_keyword not in area_text:
        is_match_area = False
        break
```

#### 3. **驗證問題邏輯**（`fami_verify`，Line 3298）

**核心流程**：
1. 偵測驗證輸入框（`#verifyPrefAnswer`）
2. 呼叫 `fill_common_verify_form()` 工具函數
3. 支援自動猜測（`auto_guess_options: true` 時）
4. 追蹤錯誤答案（`fail_list`），避免重複嘗試

**重用策略**：
- NoDriver 版本可完全重用 `util.py` 中的 `fill_common_verify_form()` 函數
- 僅需調整呼叫方式為非同步

#### 4. **登入邏輯**（`fami_login`，Line 6302）

**核心流程**：
1. 偵測登入頁面（URL 包含 `/Home/User/SignIn`）
2. 填寫帳號（`#usr_act`）與密碼（`#usr_pwd`）
3. 提交表單（password 輸入框設定 `submit=True`）

**簡單實作**：
```python
async def nodriver_fami_login(tab, account, password):
    account_input = await tab.select('#usr_act')
    await account_input.send_keys(account)

    password_input = await tab.select('#usr_pwd')
    await password_input.send_keys(password)
    # send_keys 會自動觸發 submit
```

---

## 研究任務 4：現有 NoDriver 模式分析

### 成功模式複製

基於 `src/nodriver_tixcraft.py` 中的 TixCraft/KKTIX NoDriver 實作，我們發現以下可重用模式：

#### 模式 1：主函數協調器（`nodriver_xxx_main`）

**TixCraft 模式**（參考）：
```python
async def nodriver_tixcraft_main(tab, url, config_dict):
    if '/User/Login' in url:
        # 登入頁面
        await nodriver_tixcraft_login(tab, config_dict)
    elif '/Activity/Detail' in url:
        # 活動頁面
        await nodriver_tixcraft_detail(tab, config_dict)
    elif '/ActivityInfo/Detail' in url:
        # 日期選擇
        await nodriver_tixcraft_date_auto_select(tab, config_dict)
    # ... 其他 URL 路由
```

**FamiTicket 適用**：
- URL 模式：`/Home/User/SignIn`（登入）、`/Home/Activity/Info/`（活動）
- 函數命名：`nodriver_famiticket_main()` → 分派至 `nodriver_fami_login()`、`nodriver_fami_activity()` 等

#### 模式 2：非同步錯誤處理

**TixCraft 模式**：
```python
try:
    search_id, count = await tab.send(cdp.dom.perform_search(...))
    if count == 0:
        if show_debug_message:
            print("[DEBUG] Element not found")
        return False
except Exception as e:
    if show_debug_message:
        print(f"[ERROR] {e}")
    return False
```

**FamiTicket 適用**：
- 所有函數返回布林值（簡化狀態管理，符合 FR-038）
- 使用 `show_debug_message` 控制除錯輸出

#### 模式 3：自動補票整合

**TixCraft 日期選擇模式**（Line 2670-2850）：
```python
async def nodriver_tixcraft_date_auto_select(tab, config_dict):
    # ... 日期選擇邏輯 ...

    # 自動補票
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]
    if auto_reload_coming_soon_page_enable:
        if formated_area_list is None or len(formated_area_list) == 0:
            reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0.0)
            if reload_interval > 0:
                await tab.sleep(reload_interval)
            await tab.reload()
```

**FamiTicket 差異**：
- TixCraft：`await tab.reload()`（重新整理當前頁面）
- **FamiTicket**：`await tab.get(last_activity_url)`（返回活動頁面，符合 Chrome 版本邏輯）

---

## 技術決策總結

### 優先採用技術

| 技術項目 | 選擇 | 信心等級 |
|---------|------|---------|
| 元素搜尋 | Pierce 方法 (`cdp.dom.perform_search`) | ⭐⭐⭐ 高 |
| 元素點擊 | CDP `dispatch_mouse_event()` | ⭐⭐⭐ 高 |
| 表單輸入 | NoDriver `element.send_keys()` | ⭐⭐⭐ 高 |
| 頁面導航 | `await tab.get(url)` | ⭐⭐⭐ 高 |
| 自動補票 | 重用 TixCraft 模式 + FamiTicket 特定邏輯 | ⭐⭐ 中 |
| 錯誤處理 | try-except + 布林返回值 | ⭐⭐⭐ 高 |

### 待驗證項目

1. **FamiTicket 反機器人機制強度**：
   - 測試方法：實際執行 NoDriver 版本於 FamiTicket 頁面
   - 若失敗：增加隨機延遲、模擬滑鼠移動軌跡

2. **自動補票觸發頻率**：
   - 測試方法：觀察「即將開賣」頁面的重新載入行為
   - 若觸發過於頻繁：調整 `auto_reload_page_interval` 預設值建議

### 風險評估

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| FamiTicket 更改頁面結構 | 低 | 高 | 使用彈性選擇器（Pierce 支援多種模式），詳細記錄選擇器於 `contracts/` |
| NoDriver 反偵測失敗 | 低 | 中 | 已採用 CDP 真實點擊，若仍失敗則回退至 JavaScript |
| 自動補票過於頻繁導致 IP 封鎖 | 中 | 高 | 建議使用者設定合理間隔（5-30 秒），文件中明確警告 |
| 非同步程式碼複雜度增加 | 低 | 低 | 參考現有 TixCraft/KKTIX 模式，已有成功案例 |

---

## 下一步行動

Phase 1 將基於本研究產生：
1. **data-model.md**：定義 FamiTicket 頁面狀態模型
2. **contracts/function-signatures.md**：定義所有函數簽章
3. **contracts/config-schema.md**：確認設定檔欄位（無需新增）
4. **quickstart.md**：提供快速測試與部署指南

---

**研究完成日期**：2025-11-04
**下一階段**：Phase 1 設計與契約
