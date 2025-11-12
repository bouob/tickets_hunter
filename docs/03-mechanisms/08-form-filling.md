# 機制 08：表單填寫 (Stage 8)

**文件說明**：說明搶票系統的表單填寫機制、購買人資訊自動填入與表單驗證流程
**最後更新**：2025-11-12

---

## 概述

表單填寫是購票過程中的關鍵階段。系統需要自動填寫購票表單，包括購買人信息、聯繫方式等，為送出訂單做準備。

**核心目標**：自動完成所有必填表單欄位，準備進行訂單送出。

**優先度**：🔴 P1 - 核心流程，直接影響購票成功

---

## 表單填寫流程

### 1. 表單檢測

#### 1.1 表單欄位識別
系統識別購票表單的所有欄位。

**常見的購票表單欄位**：
1. **購買人信息**
   - 姓名 (Name)
   - 電子郵件 (Email)
   - 電話號碼 (Phone)
   - 身份證 / ID (Optional)

2. **配送信息** (如適用)
   - 寄送地址
   - 郵編
   - 城市

3. **發票信息** (某些平台)
   - 發票抬頭
   - 統一編號

4. **同意條款** (見 Stage 9)

5. **備註/特殊要求**
   - 座位偏好
   - 額外備註

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2000-2100 (表單欄位識別)

#### 1.2 必填欄位檢查
確認哪些欄位是必填的。

**判斷方法**：
1. 檢查 HTML 的 `required` 屬性
2. 檢查欄位旁邊是否有 `*` 標記
3. 嘗試提交空表單，記錄驗證錯誤

### 2. 配置數據準備

#### 2.1 從配置讀取信息
系統從 `settings.json` 讀取購買人信息。

**配置結構**：
```json
{
  "ticket_account": {
    "purchaser": {
      "name": "Purchase Name",
      "email": "email@example.com",
      "phone": "09xxxxxxxxx",
      "id_number": "A123456789"
    }
  }
}
```

#### 2.2 信息驗證
驗證配置中的信息是否有效且完整。

**驗證規則**：
- 姓名：不為空，長度 2-50 字符
- 電郵：符合電郵格式
- 電話：有效的電話號碼格式
- ID：符合當地 ID 格式

### 3. 欄位填寫

#### 3.1 文本輸入欄填寫
填寫普通的文本輸入欄位。

**步驟**：
1. 定位輸入欄
2. 清除現有值
3. 輸入新值
4. 驗證輸入

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2100-2200

**代碼範例**：
```python
async def fill_text_field(page, selector: str, value: str):
    """填寫文本輸入欄"""
    try:
        element = await page.query_selector(selector)
        if not element:
            print(f"[WARNING] 無法找到欄位: {selector}")
            return False

        # 清除現有值
        await element.triple_click()
        await page.keyboard.press('Backspace')

        # 輸入新值
        await element.type(value, delay=50)
        print(f"[FORM] 已填寫: {selector}")
        return True

    except Exception as e:
        print(f"[ERROR] 填寫欄位失敗: {e}")
        return False
```

#### 3.2 下拉選單選擇
從下拉選單中選擇值。

**代碼範例**：
```python
async def select_dropdown_option(page, selector: str, value: str):
    """選擇下拉選單選項"""
    try:
        element = await page.query_selector(selector)
        if not element:
            return False

        # 點擊下拉選單
        await element.click()
        await page.wait_for_timeout(200)

        # 選擇選項
        option = await page.query_selector(f'option[value="{value}"]')
        if option:
            await option.click()
            print(f"[FORM] 已選擇選項: {value}")
            return True

        return False

    except Exception as e:
        print(f"[ERROR] 下拉選單選擇失敗: {e}")
        return False
```

#### 3.3 日期選擇器
某些表單可能需要選擇出生日期等。

**代碼範例**：
```python
async def fill_date_field(page, selector: str, date_str: str):
    """填寫日期欄位 (格式: YYYY-MM-DD)"""
    try:
        element = await page.query_selector(selector)
        if element.input_type == 'date':
            # 使用 date input 的特定方法
            await element.set_input_files(date_str)
        else:
            # 普通文本欄位
            await element.type(date_str)
        return True
    except Exception as e:
        print(f"[ERROR] 日期填寫失敗: {e}")
        return False
```

### 4. 表單驗證

#### 4.1 客戶端驗證檢查
檢查表單是否通過客戶端驗證。

**檢查項目**：
1. 查看是否有紅色的驗證錯誤提示
2. 檢查必填欄位是否都已填寫
3. 驗證錯誤訊息是否消失

**實作位置**：
- `src/nodriver_tixcraft.py`: 行 2200-2250

#### 4.2 自動修正錯誤
如果驗證失敗，嘗試自動修正。

**常見錯誤修正**：
- 電郵格式不正確 → 檢查並修正
- 必填欄位未填 → 填寫默認值
- 電話號碼格式不符 → 調整格式

### 5. 特殊表單類型

#### 5.1 表格形式的購買人信息
某些平台（如 TicketPlus）使用表格形式填寫多人購買人信息。

**特點**：
- 每一行代表一個購買人
- 可能有添加/刪除行的按鈕
- 需要填寫每一行的欄位

**處理方法**：
```python
async def fill_purchaser_table(page, purchaser_list: list):
    """填寫購買人表格"""
    for i, purchaser in enumerate(purchaser_list):
        # 找到第 i 行的欄位
        name_selector = f'input[name="purchaser[{i}][name]"]'
        email_selector = f'input[name="purchaser[{i}][email]"]'

        await fill_text_field(page, name_selector, purchaser['name'])
        await fill_text_field(page, email_selector, purchaser['email'])
```

#### 5.2 動態表單
某些表單中的欄位可能根據之前的選擇而改變。

**處理方法**：
1. 填寫初始欄位
2. 等待新欄位出現
3. 填寫新欄位
4. 重複直到表單完成

---

## 平台特定考量

### TixCraft
- 通常有購買人姓名和電郵欄位
- 可能有「同意服務條款」複選框

### KKTIX
- 購買人信息較簡單（通常只需電郵）
- 可能有額外的「推薦人代碼」欄位

### iBon
- 某些活動需要詳細購買人信息
- 可能需要身份驗證

### TicketPlus
- 表格形式的購買人信息（多人）
- 需要每人填寫詳細信息

### KHAM
- 購買人信息需求因活動而異

---

## 成功標準

**SC-003: 票數選擇成功率** ≥ 95%
- 系統正確填寫表單欄位的次數 / 總嘗試次數

---

## 相關功能需求

| FR 編號 | 功能名稱 | 狀態 |
|---------|---------|------|
| FR-035 | 購買人信息自動填寫 | 🔄 部分實作 |
| FR-036 | 表單驗證 | ✅ 實作 |

---

## 故障排除

### 問題 1: 無法找到表單欄位
**症狀**：表單欄位選擇器失效

**可能原因**：
- 選擇器已過時
- 欄位被 JavaScript 動態生成
- 欄位在 Shadow DOM 中

**解決方案**：
1. 更新選擇器
2. 增加等待時間以確保欄位加載
3. 檢查是否在 Shadow DOM 中

### 問題 2: 表單驗證失敗
**症狀**：填寫完成但無法提交，出現驗證錯誤

**可能原因**：
- 輸入格式不正確
- 必填欄位未填
- 平台特定的驗證規則

**解決方案**：
1. 檢查錯誤訊息
2. 驗證輸入格式
3. 嘗試手動填寫以了解正確格式

---

## 最佳實踐

### ✅ 推薦做法

1. **驗證配置中的數據**
   - 確保電郵、電話等格式正確
   ```python
   if not is_valid_email(config['email']):
       raise ValueError("配置中的電郵格式不正確")
   ```

2. **實現容錯機制**
   - 如果某個欄位不存在，不要中止
   ```python
   if selector_exists:
       await fill_field()
   ```

3. **添加延遲以確保 UI 更新**
   - 某些平台 UI 更新較慢
   ```python
   await asyncio.sleep(500)
   ```

### ❌ 避免做法

1. ❌ 假設所有表單結構相同
   - 不同平台有不同的表單設計

2. ❌ 無視驗證錯誤
   - 應檢查並修正所有驗證錯誤

3. ❌ 硬編碼購買人信息
   - 應從 settings.json 讀取

---

## 開發檢查清單

- [ ] 表單欄位識別正確
- [ ] 所有必填欄位都能填寫
- [ ] 文本輸入填寫成功
- [ ] 下拉選單選擇成功
- [ ] 日期欄位填寫成功
- [ ] 表單驗證通過
- [ ] 所有平台測試通過

---

## 更新日期

- **2025-11**: 初始文件建立
- **相關規格**: `specs/001-ticket-automation-system/spec.md`
- **驗證狀態**: 🔄 Phase 3 進行中

