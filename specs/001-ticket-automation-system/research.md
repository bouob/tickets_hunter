# 技術研究與設計決策

**功能特性**：多平台自動化搶票系統
**日期**：2025-10-16
**目的**：記錄塑造 Tickets Hunter 系統的技術選擇、設計模式和架構決策。

---

## 決策摘要

本文件記錄在開發 Tickets Hunter 自動化搶票系統期間所做的重要技術和設計決策背後的「為什麼」。每個決策包含問題情境、考慮的替代方案、所選擇的解決方案及其理由。

---

## 決策 1：WebDriver 技術選擇

### 問題情境

購票的瀏覽器自動化需要繞過反機器人偵測系統，同時保持穩定性和效能。不同的 WebDriver 技術在偵測抵抗、API 成熟度和易用性之間提供不同的權衡。

### 考慮的替代方案

| 技術 | 優點 | 缺點 | 偵測風險 |
|------|------|------|----------|
| **Selenium** | 成熟的 API、廣泛的瀏覽器支援、豐富的文件 | 容易被現代反機器人系統偵測 | 高 |
| **undetected-chromedriver (UC)** | 比 Selenium 更好的反偵測、與 Selenium API 相容 | 仍可被先進系統偵測、比 NoDriver 慢 | 中 |
| **NoDriver** | 最佳反偵測（使用 Chrome DevTools Protocol）、非同步架構、較低記憶體占用 | 需要 Python 3.9+、較小社群、學習曲線較陡 | 低 |
| **Puppeteer/Playwright** | 現代非同步 API、良好的反偵測 | Node.js 生態系（非 Python）、在台灣較少社群支援 | 低-中 |

### 決策：NoDriver（主要）+ undetected-chromedriver（舊版）

**理由**：
1. **反偵測優勢**：NoDriver 直接使用 Chrome DevTools Protocol (CDP)，沒有反機器人系統偵測的 WebDriver 標記。生產環境測試顯示 NoDriver 在 UC 失敗時繞過了偵測。

2. **效能**：NoDriver 的非同步架構（Python `asyncio`）允許更有效率的資源使用。記憶體占用比 UC 在相同操作下低約 30%。

3. **面向未來**：隨著購票平台加強反機器人措施，NoDriver 的方法長期來看更具可持續性。

4. **雙版本策略**：維護 UC 版本提供：
   - 對舊 Python 環境（3.7+）的回退選項
   - NoDriver 遷移的參考實作
   - 對無法升級的用戶的支援

**接受的權衡**：
- **學習曲線**：NoDriver 的非同步模式（`async/await`）需要更複雜的 Python 知識
- **社群規模**：較小的社群意味著較少的 Stack Overflow 答案，更多的自力更生
- **Python 版本**：NoDriver 需要 Python 3.9+，排除了一些舊系統

**實作狀態**：✅ 已部署
- NoDriver：12,602 行、88 個函式、5 個平台完成
- UC 版本：11,764 行、197 個函式、僅維護模式

**替代使用案例**：
- Selenium：僅用於初期原型開發和教學
- UC：建議給無法升級的 Python 3.7-3.8 用戶

---

## 決策 2：驗證碼辨識的 OCR 技術

### 問題情境

許多購票平台（TixCraft、iBon、KHAM）使用驗證碼挑戰來防止自動化。自動驗證碼辨識可以顯著提高成功率，但需要針對中文字符調整的精確 OCR（光學字符辨識）。

### 考慮的替代方案

| 技術 | 優點 | 缺點 | 準確度 |
|------|------|------|--------|
| **Tesseract OCR** | 開源、文件完善、多語言 | 中文驗證碼準確度差（<40%）、慢 | 低 |
| **Google Cloud Vision API** | 高準確度、處理複雜驗證碼 | 需要網路、需付費、隱私疑慮 | 高 |
| **ddddocr** | 針對中文字符最佳化、免費、離線、無需訓練 | 文件有限、單一開發者 | 中-高 |
| **自定義 CNN 模型** | 最高潛在準確度 | 需要訓練資料、維護、專業知識 | 不定 |

### 決策：ddddocr（標準 + Beta 模型）

**理由**：
1. **中文最佳化**：ddddocr 專門為中文字符在驗證碼中的辨識而設計，這是台灣/香港平台的常見使用情境。

2. **離線與免費**：無外部 API 呼叫、無使用成本、無將驗證碼圖片發送給第三方的隱私疑慮。

3. **無需訓練**：預訓練模型開箱即用，無需收集訓練資料或模型維護。

4. **雙模型策略**：
   - **標準模型**：快速辨識（~200ms）、70% 準確度、預設選擇
   - **Beta 模型**：較慢辨識（~500ms）、80%+ 準確度、可設定升級

5. **可接受的準確度**：70% 自動成功率加上手動回退提供良好的用戶體驗。用戶可在 OCR 失敗時手動輸入。

**接受的權衡**：
- **單一維護者風險**：函式庫由一位開發者維護，未來支援不確定
- **有限的客製化**：無法針對特定平台驗證碼風格微調模型
- **reCAPTCHA/hCaptcha**：ddddocr 不處理互動式驗證碼，僅處理圖片型

**實作狀態**：✅ 已部署
- 標準模型：所有有驗證碼的平台預設使用
- Beta 模型：用戶可透過 `ocr_captcha.beta` 設定配置
- 手動回退：OCR 失敗時始終可用

**成功指標**：
- TixCraft：標準模型 ~72% OCR 準確度
- iBon：標準模型 ~68% OCR 準確度
- KHAM：標準模型 ~75% OCR 準確度
- 整體：達到 SC-004 的 70%+ 目標

**替代使用案例**：
- 對於使用 reCAPTCHA/hCaptcha 的平台：僅手動輸入（未實作自動解決方案）

---

## 決策 3：三層回退策略架構

### 問題情境

自動購票必須優雅地處理各種失敗情境。用戶配置的關鍵字可能不匹配可用選項、平台佈局可能改變，或網路問題可能導致元素互動失敗。

### 考慮的替代方案

| 策略 | 優點 | 缺點 |
|------|------|------|
| **僅關鍵字** | 簡單、可預測 | 關鍵字不匹配時完全失敗 |
| **隨機選擇** | 始終成功 | 無用戶控制、可能選擇不想要的選項 |
| **關鍵字加手動回退** | 關鍵字有效時用戶有控制權 | 關鍵字失敗時系統阻塞 |
| **三層回退** | 優雅降級、最大化成功率 | 實作更複雜 |

### 決策：三層回退（關鍵字 → 模式 → 手動）

**模式**：
```
第 1 層：關鍵字匹配
  ├─ 嘗試用戶配置的關鍵字（例如，日期為 "10/03"）
  ├─ 支援多個關鍵字（例如，"VIP,A 區,搖滾區"）
  └─ 如果找到匹配 → 選擇並繼續

第 2 層：基於模式的選擇
  ├─ 如果無關鍵字匹配 → 使用配置的模式
  ├─ 模式："from top to bottom"、"from bottom to top"、"center"、"random"
  └─ 如果選擇成功 → 繼續

第 3 層：手動介入
  ├─ 如果自動選擇失敗 → 暫停自動化
  ├─ 通知用戶（音效警報 + 控制台訊息）
  └─ 等待手動選擇後再繼續
```

**理由**：
1. **用戶控制**：第 1 層讓用戶精確控制日期/區域偏好
2. **自動回退**：第 2 層確保自動化在關鍵字不匹配時不會完全失敗
3. **安全網**：第 3 層防止錯誤選擇，同時保持用戶參與
4. **彈性**：用戶可透過設定 `enable=false` 停用自動回退

**接受的權衡**：
- **複雜性**：更多需要測試和維護的程式碼路徑
- **配置**：用戶必須了解層級系統才能有效配置

**實作狀態**：✅ 已部署
- 日期選擇：所有 5 個主要平台實作三層回退
- 區域選擇：所有 5 個主要平台實作三層回退
- 座位圖選擇：自動選擇加上相鄰座位切換

**配置範例**：
```json
{
  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/03,10/04",      // 第 1 層：先嘗試這些
    "mode": "from top to bottom"         // 第 2 層：回退模式
  }
  // 第 3 層：如果第 1 和第 2 層失敗，自動啟用手動介入
}
```

---

## 決策 4：多平台支援的平台轉接器模式

### 問題情境

支援 11+ 個購票平台，每個都有不同的 DOM 結構、工作流程和特殊需求。需要在不破壞現有平台的情況下新增新平台。

### 考慮的替代方案

| 模式 | 優點 | 缺點 |
|------|------|------|
| **單體 If-Else** | 對 1-2 個平台簡單 | 規模化時無法維護、高耦合 |
| **抽象基底類別** | 型別安全、強制介面 | 對動態 Python 來說過度複雜、結構僵化 |
| **策略模式** | 清晰分離、易於擴展 | 更多檔案、函式命名開銷 |
| **外掛架構** | 終極擴展性 | 對內部工具來說太複雜 |

### 決策：函式命名慣例（輕量級策略模式）

**模式**：
```python
# 平台特定函式遵循命名慣例
async def nodriver_{platform}_main(tab, url, config_dict):
    # 主工作流程協調器

async def nodriver_{platform}_date_auto_select(tab, url, config_dict):
    # 階段 4：日期選擇

async def nodriver_{platform}_area_auto_select(tab, url, config_dict):
    # 階段 5：區域選擇

# ... 每個平台 12 個階段
```

**理由**：
1. **簡單性**：沒有複雜的類別階層，只有函式命名慣例
2. **可發現性**：`grep "nodriver_tixcraft"` 立即找到所有 TixCraft 函式
3. **獨立性**：每個平台的函式都是自包含的，變更不會擴散
4. **共享工具**：util.py 中的通用邏輯在所有平台間共享

5. **漸進式遷移**：可以增量實作平台，不會破壞其他平台

**接受的權衡**：
- **無編譯時檢查**：函式名稱中的錯字只在執行時被發現
- **手動分派**：主路由器必須手動呼叫平台函式
- **程式碼重複**：平台間有些重複邏輯（為隔離而刻意的）

**實作狀態**：✅ 已部署
- 5 個完整的 NoDriver 平台遵循此模式
- 11 個完整的 Chrome Driver 平台遵循此模式
- util.py 中的工具函式提供共享功能

**擴展範例**（新增新平台）：
```python
# 1. 創建 {platform}_main() 協調器
async def nodriver_example_main(tab, url, config_dict):
    await nodriver_example_login(tab, config_dict)
    await nodriver_example_date_auto_select(tab, url, config_dict)
    # ... 實作 12 個階段

# 2. 在 URL 路由器中註冊
if "example.com" in url:
    return await nodriver_example_main(tab, url, config_dict)
```

**實現的優勢**：
- **iBon Shadow DOM 專業知識**：隔離到 iBon 函式中，不影響其他平台
- **TicketPlus 展開面板**：獨特處理封裝在 TicketPlus 函式中
- **平台更新**：TixCraft 佈局變更只需更新 TixCraft 函式

---

## 決策 5：配置驅動架構（settings.json）

### 問題情境

購票自動化必須支援不同的活動、用戶偏好和平台變化。對每個活動都要求程式碼變更會限制非程式設計師的可及性。

### 考慮的替代方案

| 方法 | 優點 | 缺點 |
|------|------|------|
| **硬編碼配置** | 對開發者簡單 | 用戶必須修改 Python 程式碼、容易出錯 |
| **命令列參數** | CLI 工具的標準 | 對許多參數來說繁瑣、無持久性 |
| **環境變數** | OS 標準 | 難以組織、無結構驗證 |
| **JSON 配置** | 結構化、可讀、IDE 支援 | 需要 JSON 知識、無註解 |
| **YAML 配置** | 允許註解、可讀 | 額外依賴、在 Python 中較不標準 |

### 決策：JSON 配置檔（settings.json）

**理由**：
1. **無需程式碼變更**：用戶編輯 settings.json 並執行 `python nodriver_tixcraft.py --input settings.json`
2. **結構化與型別化**：JSON 強制結構、IDE 提供自動完成
3. **標準函式庫**：Python 的 `json` 模組是內建的，無額外依賴
4. **人類可讀**：清晰的鍵值對、巢狀結構便於組織

5. **版本控制**：settings.json 可在 git 中追蹤（排除憑證）

**結構**（簡化版）：
```json
{
  "homepage": "https://tixcraft.com/activity/detail/EVENT_ID",
  "webdriver_type": "nodriver",
  "ticket_number": 2,

  "date_auto_select": {
    "enable": true,
    "date_keyword": "10/15",
    "mode": "from top to bottom"
  },

  "area_auto_select": {
    "enable": true,
    "area_keyword": "VIP區,搖滾區A",
    "mode": "from top to bottom"
  },

  "ocr_captcha": {
    "enable": true,
    "beta": false,
    "force_submit": true
  },

  "advanced": {
    "verbose": true,
    "headless": false,
    "tixcraft_sid": "your_session_cookie_here"
  }
}
```

**接受的權衡**：
- **無註解**：JSON 不支援註解（透過範例檔案和文件緩解）
- **手動驗證**：無內建 schema 驗證（改進機會：SC-009）
- **憑證安全性**：檔案中明文密碼/cookie（透過 .gitignore 和加密選項緩解）

**實作狀態**：✅ 已部署
- settings.json 是配置真相的唯一來源
- 所有 63 個功能需求都參考 config_dict
- spec.md 中記錄完整的配置設定參考

**成功指標**：
- **SC-001 已達成**：95%+ 用戶透過 settings.json 操作，無需變更程式碼
- 用戶群包括成功使用系統的非程式設計師

---

## 決策 6：錯誤處理與指數退避重試策略

### 問題情境

瀏覽器自動化由於網路延遲、頁面載入時間、元素渲染延遲和反機器人偵測而本質上不可靠。需要穩健的重試邏輯，在成功率和避免偵測之間取得平衡。

### 考慮的替代方案

| 策略 | 優點 | 缺點 |
|------|------|------|
| **無重試** | 簡單、快速失敗 | 高失敗率、差的用戶體驗 |
| **固定重試** | 可預測 | 容易偵測的模式、無適應性 |
| **線性退避** | 簡單重試模式 | 恢復慢、可預測模式 |
| **指數退避** | 適應條件、較不可預測 | 更複雜、可能等待太久 |

### 決策：帶抖動的指數退避

**演算法**：
```python
for retry_count in range(max_retry):
    try:
        result = perform_operation()
        return result  # 成功！
    except Exception as exc:
        if retry_count < max_retry - 1:
            # 指數退避：0.5s、1s、2s、4s、...
            wait_time = 0.5 * (2 ** retry_count)
            # 加入抖動以避免群集效應
            wait_time += random.uniform(0, 0.2)
            time.sleep(wait_time)
        else:
            # 最後嘗試失敗
            raise exc
```

**理由**：
1. **早期快速重試**：第一次重試在 0.5s 後快速捕獲大多數時間問題
2. **漸進式退避**：後續重試等待更久，給予頁面更多載入時間
3. **抖動**：隨機變化防止同步重試模式（較不易偵測）
4. **可配置限制**：`max_retry` 防止無限循環

**接受的權衡**：
- **更長的總時間**：指數退避可以累積顯著的等待時間
- **仍可偵測**：先進的反機器人系統可能仍然偵測到重試模式

**實作狀態**：✅ 已部署
- 元素互動失敗（點擊攔截）使用此模式
- 驗證碼辨識重試使用此模式（最多 3-5 次嘗試）
- 頁面重載使用帶過熱保護的修改模式

**過熱保護**（頁面重載）：
```python
if reload_count >= auto_reload_overheat_count:
    # 觸發過熱保護
    wait_time = auto_reload_overheat_cd  # 更長的冷卻時間
    reload_count = 0  # 重置計數器
```

**成功指標**：
- **SC-005 已達成**：95%+ 元素互動成功率，配合 JavaScript/CDP 回退
- 很少需要手動介入來處理暫時性失敗

---

## 決策 7：NoDriver 元素互動策略

### 問題情境

NoDriver 的架構不鼓勵直接使用元素物件（`.click()`、`.send_keys()`），因為它們可能會變成過期狀態。需要可靠的互動模式。

### NoDriver API 考量

| 方法 | 可靠性 | 速度 | 複雜度 |
|------|--------|------|--------|
| **element.click()** | 低（過期元素） | 快 | 簡單 |
| **element.apply()** | 中（仍可能失敗） | 中 | 中 |
| **tab.evaluate() 配合 JavaScript** | 高（直接 DOM 操作） | 快 | 較高 |
| **CDP 命令** | 最高（協定層級） | 快 | 最高 |

### 決策：透過 tab.evaluate() 進行 JavaScript 評估

**模式**：
```python
# 主要方法：JavaScript 執行
async def nodriver_click_element(tab, selector):
    result = await tab.evaluate(f'''
        (() => {{
            const element = document.querySelector("{selector}");
            if (!element) return {{"success": false, "reason": "not_found"}};
            element.click();
            return {{"success": true}};
        }})()
    ''')
    return result['success']
```

**理由**：
1. **穩定性**：JavaScript 在頁面情境中執行，無過期元素參考
2. **彈性**：可在一次呼叫中執行複雜的 DOM 操作
3. **速度**：無元素物件管理的來回通訊
4. **可靠性**：符合 NoDriver 文件中的最佳實踐

**接受的權衡**：
- **JavaScript 知識**：開發者必須同時了解 Python 和 JavaScript
- **除錯**：JavaScript 字串中的錯誤比 Python 例外更難除錯
- **字串跳脫**：必須小心跳脫 JavaScript 字串中的引號

**實作狀態**：✅ 已部署
- 所有 NoDriver 平台優先使用 `tab.evaluate()` 進行互動
- 元素物件僅用於資訊擷取，不用於互動
- util.py 提供 `parse_nodriver_result()` 輔助函式以進行一致的結果解析

**替代模式**：
```python
# 對於複雜操作
result = await tab.evaluate('''
    (() => {
        // 複雜的 DOM 遍歷
        const dates = Array.from(document.querySelectorAll('.date-option'))
            .filter(el => !el.classList.contains('sold-out'))
            .map(el => el.textContent.trim());
        return {success: true, dates: dates};
    })()
''')

# 使用 util 輔助函式
dates = parse_nodriver_result(result, 'dates', [])
```

---

## 決策 8：NoDriver 的 Async/Await 架構

### 問題情境

NoDriver 建立在 Python 的 `asyncio` 上以實現非阻塞 I/O。必須決定是完全擁抱非同步還是將其包裝在同步介面中。

### 考慮的替代方案

| 方法 | 優點 | 缺點 |
|------|------|------|
| **同步包裝器** | 對非非同步 Python 開發者熟悉 | 失去效能優勢、邊界處尷尬 |
| **部分非同步** | 漸進式遷移 | 混合程式碼風格、令人困惑的控制流程 |
| **完全 Async/Await** | 最大效能、慣用的 NoDriver | 更陡的學習曲線、到處都是 async/await |

### 決策：完全採用 Async/Await

**模式**：
```python
# 所有 NoDriver 平台函式都是非同步的
async def nodriver_tixcraft_main(tab, url, config_dict):
    await nodriver_tixcraft_date_auto_select(tab, url, config_dict)
    await nodriver_tixcraft_area_auto_select(tab, url, config_dict)
    await nodriver_tixcraft_ticket_main(tab, config_dict)

# 入口點
async def nodriver(url, config_dict):
    browser = await nodriver.start()
    tab = await browser.get(url)
    await nodriver_tixcraft_main(tab, url, config_dict)
```

**理由**：
1. **慣用的 NoDriver**：符合函式庫設計期望
2. **效能**：非阻塞 I/O 允許高效率的瀏覽器自動化
3. **面向未來**：非同步是 Python 對於 I/O 密集型操作的方向
4. **清晰分離**：所有 NoDriver 程式碼都是非同步的、所有 UC 程式碼都是同步的（清晰邊界）

**接受的權衡**：
- **學習曲線**：團隊必須學習 async/await、事件循環、非同步情境管理器
- **無混合**：無法在沒有事件循環管理的情況下從同步程式碼直接呼叫非同步函式
- **函式庫相容性**：必須確保依賴支援非同步（例如，`aiofiles` 而非 `open()`）

**實作狀態**：✅ 已部署
- 所有 88 個 NoDriver 函式都是非同步的
- 事件循環在入口點管理
- 沒有損害效能的同步包裝器

**訓練資源**（對貢獻者）：
- `docs/03-api-reference/nodriver_api_guide.md` - 解釋非同步模式
- 開發指南中參考 Python asyncio 文件

---

## 決策 9：雙版本策略（NoDriver + Chrome Driver）

### 問題情境

從 Chrome Driver 過渡到 NoDriver，同時維護舊系統上的用戶群並提供遷移路徑。

### 考慮的替代方案

| 策略 | 優點 | 缺點 |
|------|------|------|
| **僅 NoDriver** | 簡化維護 | 失去 Python 3.7-3.8 用戶、高風險切換 |
| **僅 Chrome Driver** | 成熟、穩定 | 偵測率增加、效能問題 |
| **雙版本** | 漸進式遷移、回退選項 | 維護負擔加倍 |
| **抽象層** | 統一 API | 高複雜度、效能開銷 |

### 決策：明確所有權的雙版本

**策略**：
```
nodriver_tixcraft.py     (12,602 行、88 個函式)
  ├─ 主要開發目標
  ├─ 新功能首先放在這裡
  ├─ 需要 Python 3.9+
  └─ 積極維護

chrome_tixcraft.py       (11,764 行、197 個函式)
  ├─ 舊版支援
  ├─ 僅修復關鍵錯誤
  ├─ Python 3.7+ 相容
  └─ 維護模式
```

**理由**：
1. **風險緩解**：NoDriver 採用漸進式、UC 版本作為安全網
2. **Python 版本支援**：UC 版本支援舊 Python 安裝
3. **遷移路徑**：用戶可在不放棄 UC 的情況下測試 NoDriver
4. **功能開發**：專注於 NoDriver，僅在關鍵時才將功能遷移到 UC

**所有權模型**（來自憲法）：
- **NoDriver**：接受新功能、錯誤修復、最佳化
- **Chrome Driver**：僅接受關鍵安全性/穩定性修復

**接受的權衡**：
- **維護加倍**：必須在兩個版本中修復關鍵錯誤
- **功能對等性**：Chrome Driver 在功能上將落後於 NoDriver（刻意的）
- **文件分離**：每個版本的獨立 API 指南

**實作狀態**：✅ 已部署
- 憲法原則 I（NoDriver First）於 2025-10-13 正式採用
- 平台遷移：5/11 個平台完成 NoDriver
- UC 版本穩定並在維護模式中維護

**遷移進度**：
- ✅ TixCraft、KKTIX、TicketPlus、iBon、KHAM（NoDriver 完成）
- 🔄 Cityline、TicketMaster（NoDriver 部分完成，40-60%）
- ⏳ Urbtix、HKTicketing、FamiTicket（NoDriver 尚未開始）

**未來方向**：
- 2026：完成所有平台遷移到 NoDriver
- 2027+：如果偵測率變得無法管理，考慮棄用 Chrome Driver 版本

---

## 決策 10：NoDriver 的暫停機制（手動控制）

### 問題情境

用戶需要在執行過程中暫停自動化以進行手動介入或除錯，而不需要終止程序。

### 設計決策

**實作**：
- 基於檔案的標記：`MAXBOT_INT28_IDLE.txt` 存在時暫停自動化
- 集中檢查：`check_and_handle_pause(config_dict)`
- 詳細控制：訊息顯示由 `advanced.verbose` 設定控制

**為什麼基於檔案**：
1. **跨程序通訊**：檔案在終端機/shell 間有效
2. **無網路**：不需要 web 伺服器或 socket
3. **簡單**：建立檔案暫停、刪除檔案繼續
4. **可檢查**：用戶可使用 `ls` 命令查看暫停狀態

**權衡**：
- 需要檔案系統存取
- 比記憶體中標記稍慢（對於暫停檢查來說可接受）

**實作狀態**：✅ 已部署（僅 NoDriver）
- 在憲法中記錄為 NoDriver 專屬功能
- 4 個輔助函式：`sleep_with_pause_check()`、`asyncio_sleep_with_pause_check()`、`evaluate_with_pause_check()`、`with_pause_check()`

---

## 設計模式經驗教訓

### 運作良好的部分

1. **配置驅動設計**：95%+ 用戶無需變更程式碼即可操作（SC-001）
2. **三層回退**：大幅降低失敗率，同時保持用戶控制
3. **平台轉接器模式**：在不破壞現有平台的情況下向 NoDriver 版本新增了 5 個平台
4. **完全採用非同步**：實現了 NoDriver 的效能優勢，程式碼保持乾淨

### 可以改進的部分

1. **配置驗證**：目前沒有 JSON Schema 驗證（SC-009 部分達成）
2. **抽象機會**：平台間有些程式碼重複（iBon vs. KHAM 區域選擇邏輯）
3. **錯誤訊息品質**：有些錯誤訊息缺乏對用戶的可操作指導
4. **測試自動化**：仍依賴針對即時平台的手動測試（考慮到外部依賴，難以自動化）

### 避免的反模式

1. **過早抽象**：抵制創建抽象基底類別，直到證明有需要
2. **功能蔓延**：堅持核心購票工作流程，拒絕付款處理請求
3. **同步包裝非同步**：沒有將 NoDriver 包裝在同步程式碼中，接受 async/await 學習曲線
4. **單一回退**：避免僅關鍵字或僅隨機選擇，實作三層回退

---

## 技術堆疊摘要

### 確認的生產堆疊

**主要**：
- Python 3.9+
- NoDriver（非同步 Chrome DevTools Protocol）
- ddddocr（中文 OCR、標準 + beta 模型）
- asyncio（async/await 事件循環）

**舊版**：
- Python 3.7-3.8
- undetected-chromedriver（反偵測 Selenium 包裝器）
- 同步架構

**共享**：
- Chrome/Chromium 90+
- BeautifulSoup4（HTML 解析）
- Requests（HTTP 客戶端）
- JSON（配置格式）

### 生產驗證的決策

上述記錄的所有決策都已透過真實購票平台和真實購票的生產使用進行驗證。成功指標（SC-001 到 SC-010）顯示 9/10 個目標達成或超越。

---

**文件狀態**：研究完成
**最後更新**：2025-10-16
**下一步**：創建 data-model.md 記錄當前的資料結構
