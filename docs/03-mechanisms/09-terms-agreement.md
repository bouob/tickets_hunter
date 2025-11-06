# 機制 09：同意條款 (Stage 9)

## 概述

在送出訂單前，大多數平台都要求使用者同意服務條款、隱私政策或其他法律條款。系統需要自動檢測並同意這些條款，以完成訂單流程。

**核心目標**：自動檢測並同意所有必要的條款，確保訂單可以成功送出。

**優先度**：🟡 P2 - 法律合規性重要

---

## 條款同意流程

### 1. 條款檢測

#### 1.1 識別條款複選框
系統識別頁面上需要同意的條款複選框。

**常見的條款複選框**：
1. **服務條款** (Terms of Service)
   - 「我同意服務條款」
   - 「I agree to terms and conditions」

2. **隱私政策** (Privacy Policy)
   - 「我同意隱私政策」
   - 「I agree to privacy policy」

3. **電子票券確認** (特定於票務)
   - 「我確認已閱讀電子票券說明」
   - 「Electronic ticket confirmation」

4. **年齡確認**
   - 「我確認滿 18 歲」（某些活動）
   - 「Age confirmation」

5. **電子郵件訂閱** (可選)
   - 「訂閱新聞通訊」
   - 「Subscribe to newsletter」

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2300-2400 (條款檢測)

**代碼範例**：
```python
async def find_agreement_checkboxes(page) -> list:
    """尋找需要同意的條款複選框"""
    checkboxes = []

    # 常見的條款複選框選擇器
    selectors = [
        'input[type="checkbox"][name*="agree"]',
        'input[type="checkbox"][name*="terms"]',
        'input[type="checkbox"][name*="privacy"]',
        'input[type="checkbox"][aria-label*="agree"]',
        'input[type="checkbox"] + label:has-text("同意")',
    ]

    for selector in selectors:
        try:
            elements = await page.query_selector_all(selector)
            checkboxes.extend(elements)
        except:
            pass

    # 去重
    checkboxes = list(set(checkboxes))
    print(f"[TERMS] 發現 {len(checkboxes)} 個條款複選框")
    return checkboxes
```

#### 1.2 區分必填與可選條款
區分哪些條款是必須同意的，哪些是可選的。

**判斷方法**：
1. **必填條款**
   - 旁邊有 `*` 或 `required` 標記
   - 複選框初始狀態為「未選」
   - 不選將導致提交失敗

2. **可選條款**
   - 通常是行銷、新聞通訊等
   - 不選也能提交
   - 配置中可能有選項跳過

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2400-2450

### 2. 條款同意

#### 2.1 自動檢查必填條款
自動勾選所有必填的條款複選框。

**步驟**：
1. 確認複選框未被勾選
2. 點擊複選框（或修改 `checked` 屬性）
3. 驗證複選框已被勾選

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2450-2550

**代碼範例**：
```python
async def check_required_agreements(page) -> bool:
    """檢查所有必填條款複選框"""
    try:
        checkboxes = await find_agreement_checkboxes(page)
        for checkbox in checkboxes:
            # 檢查是否已勾選
            is_checked = await checkbox.is_checked()
            if not is_checked:
                # 點擊複選框
                await checkbox.click()
                await page.wait_for_timeout(200)

                # 驗證已勾選
                if await checkbox.is_checked():
                    print("[TERMS] 已同意條款")
                else:
                    print("[WARNING] 複選框點擊後仍未勾選")

        return True

    except Exception as e:
        print(f"[ERROR] 同意條款失敗: {e}")
        return False
```

#### 2.2 可選條款處理
根據配置決定是否同意可選條款。

**配置選項**：
```json
{
  "advanced": {
    "agree_optional_terms": false,
    "subscribe_newsletter": false
  }
}
```

**處理邏輯**：
1. 識別可選條款
2. 根據配置決定是否勾選
3. 記錄所有操作

**代碼範例**：
```python
async def handle_optional_agreements(page, config_dict: dict) -> bool:
    """處理可選條款"""
    # 識別新聞通訊複選框
    newsletter_checkbox = await page.query_selector(
        'input[type="checkbox"][name*="newsletter"]'
    )

    if newsletter_checkbox:
        subscribe = config_dict.get('advanced', {}).get('subscribe_newsletter', False)

        is_checked = await newsletter_checkbox.is_checked()
        if subscribe and not is_checked:
            await newsletter_checkbox.click()
            print("[TERMS] 已訂閱新聞通訊")
        elif not subscribe and is_checked:
            await newsletter_checkbox.click()
            print("[TERMS] 已取消訂閱新聞通訊")

    return True
```

### 3. 特殊情況處理

#### 3.1 條款連結（展開條款文本）
某些平台將條款放在可展開的連結中。

**特點**：
- 點擊「服務條款」連結可展開條款文本
- 複選框通常在條款下方或旁邊
- 可能需要完全展開後才能勾選複選框

**處理方法**：
```python
async def expand_and_agree_terms(page, terms_link_selector: str):
    """展開並同意條款"""
    # 點擊條款連結展開
    terms_link = await page.query_selector(terms_link_selector)
    if terms_link:
        await terms_link.click()
        await page.wait_for_timeout(500)

    # 尋找並勾選複選框
    checkbox = await page.query_selector(
        'input[type="checkbox"][name*="agree"]'
    )
    if checkbox:
        await checkbox.click()
```

#### 3.2 條款確認對話框
某些平台使用模態對話框顯示條款。

**特點**：
- 模態窗口顯示條款詳情
- 有「同意」和「拒絕」按鈕
- 必須點擊「同意」才能繼續

**處理方法**：
```python
async def handle_terms_modal(page):
    """處理條款確認對話框"""
    # 等待對話框出現
    modal = await page.wait_for_selector('dialog, .modal, [role="dialog"]')

    # 尋找「同意」按鈕
    agree_button = await modal.query_selector(
        'button:has-text("同意"), button:has-text("Agree"), button:has-text("OK")'
    )

    if agree_button:
        await agree_button.click()
        print("[TERMS] 已點擊同意按鈕")
        await page.wait_for_timeout(500)
```

#### 3.3 已勾選驗證
驗證所有必填條款是否已勾選。

**驗證步驟**：
1. 獲取所有「必填」條款複選框
2. 逐一檢查是否已勾選
3. 如有未勾選，嘗試勾選
4. 最終驗證全部已勾選

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2550-2600

---

## 平台特定考量

### TixCraft
- 通常有單個「同意服務條款」複選框
- 簡單直接的條款同意流程

### KKTIX
- 可能有多個條款複選框
- 可能有「電子票券確認」複選框

### iBon
- 條款可能在模態對話框中
- 可能有較複雜的條款結構

### TicketPlus
- 條款複選框位置可能不同
- 可能有展開的條款文本

### KHAM
- 條款結構因活動而異

---

## 成功標準

**SC-006: 條款同意成功率** ≥ 98%
- 系統正確同意所有必填條款的次數 / 總嘗試次數

**SC-009: 錯誤恢復能力** ≥ 90%
- 條款同意過程中遭遇錯誤時的恢復成功率

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-040 | 自動同意條款 | ✅ 實作 |
| FR-041 | 條款驗證 | ✅ 實作 |

---

## 故障排除

### 問題 1: 無法找到條款複選框
**症狀**：系統無法定位需要同意的複選框

**可能原因**：
- 選擇器已過時
- 複選框在 Shadow DOM 中
- 複選框動態生成

**解決方案**：
1. 檢查最新的頁面結構
2. 更新選擇器
3. 增加等待時間

### 問題 2: 複選框點擊後未勾選
**症狀**：點擊複選框但 `checked` 屬性未改變

**可能原因**：
- 複選框由 JavaScript 控制
- 點擊位置不正確
- 複選框被禁用

**解決方案**：
1. 嘗試直接修改 `checked` 屬性
2. 點擊複選框旁邊的標籤 (`<label>`)
3. 檢查複選框是否被禁用

### 問題 3: 條款同意後仍無法提交
**症狀**：同意所有條款但訂單提交仍然失敗

**可能原因**：
- 有隱藏的必填條款未發現
- 條款驗證失敗
- 還有其他必填欄位未完成

**解決方案**：
1. 檢查頁面上的所有複選框
2. 查看提交按鈕是否有錯誤訊息
3. 確認所有表單欄位已完成

---

## 最佳實踐

### ✅ 推薦做法

1. **使用多重選擇器**
   - 條款複選框選擇器容易失效
   - 提供多個備選選擇器
   ```python
   selectors = [
       'input[name*="agree"]',
       'input[name*="terms"]',
       'input[type="checkbox"]'
   ]
   ```

2. **驗證複選框狀態**
   - 點擊後總是驗證
   - 如果未勾選，嘗試替代方法
   ```python
   if not await checkbox.is_checked():
       # 嘗試點擊標籤
       label = await checkbox.evaluate('el => el.labels[0]')
       await label.click()
   ```

3. **記錄所有操作**
   - 詳細記錄同意了哪些條款
   - 幫助除錯

### ❌ 避免做法

1. ❌ 忽略可選條款
   - 應根據使用者配置決定

2. ❌ 無視同意失敗
   - 應驗證所有條款已勾選

3. ❌ 假設條款複選框位置不變
   - 應使用靈活的定位方式

---

## 開發檢查清單

- [ ] 條款複選框檢測正確
- [ ] 必填條款自動勾選成功
- [ ] 可選條款根據配置處理
- [ ] 條款同意驗證正確
- [ ] 模態對話框處理成功
- [ ] 所有平台測試通過

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: 🔄 Phase 3 進行中

