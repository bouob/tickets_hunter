# 平台實作參考：TicketPlus

## 平台概述

**平台名稱**：TicketPlus
**市場地位**：小型平台
**主要業務**：演唱會、展覽
**完成度**：18.8% (12/64 FR)
**難度級別**：⭐⭐⭐ (高)

---

## 平台特性

### 核心特點
✅ **優勢**：
- 相對簡潔的介面
- 支援多人購買表格
- 清晰的購票流程

⚠️ **挑戰**：
- 表格形式的購買人信息（複雜）
- 展開面板設計
- 實名驗證需求
- 多步驟確認流程
- 選擇器頻繁變化

### 特殊機制

1. **購買人表格**
   - 每一行代表一個購買人
   - 需要逐行填寫詳細信息
   - 支援添加/刪除行

2. **展開面板**
   - 某些選項需要展開才可見
   - 點擊後才能選擇

3. **實名驗證**
   - 某些活動需要身份驗證
   - 可能需要身份證號

---

## 12 階段實作指南

### Stage 1-3: 初始化、認證、監控
**狀態**：✅ 基本實作

```python
# TicketPlus 特定識別
if 'ticketplus.com.tw' in url:
    platform = 'ticketplus'

# Cookie 認證
await inject_cookies(page, cookies['ticketplus'])
```

---

### Stage 4-5: 日期 + 區域選擇
**狀態**：🔄 部分實作

**TicketPlus 特點**：
- 日期通常不可選
- 區域選擇使用選擇框

---

### Stage 6: 票數設定
**狀態**：✅ 基本實作

---

### Stage 8: 表單填寫（關鍵）
**狀態**：🔄 部分實作

**TicketPlus 特點**：表格形式購買人

**實現方法**：
```python
# 表格行選擇器
for i in range(ticket_count):
    row_selector = f'tr[data-row-index="{i}"]'

    # 填寫每行的資訊
    name_input = f'{row_selector} input[name*="name"]'
    id_input = f'{row_selector} input[name*="id"]'
    email_input = f'{row_selector} input[name*="email"]'

    await fill_text_field(page, name_input, purchaser['name'])
    await fill_text_field(page, id_input, purchaser['id'])
    await fill_text_field(page, email_input, purchaser['email'])
```

---

### Stage 9-12: 條款、送出、排隊、錯誤
**狀態**：🔄 部分實作

---

## 配置範例

```json
{
  "url": "https://ticketplus.com.tw/activity/xxx",
  "webdriver_type": "nodriver",
  "ticket_account": {
    "ticketplus": {
      "email": "your@email.com",
      "password": "password"
    }
  },
  "ticket_count": 2,
  "advanced": {
    "verbose": true
  }
}
```

---

## 常見問題與解決方案

### Q1: 表格行無法填寫？

**可能原因**：
- 選擇器不正確
- 需要先點擊行激活
- 動態生成的表格

**解決方案**：
1. 先點擊該行激活
2. 等待輸入框出現
3. 再進行填寫

### Q2: 為什麼驗證總是失敗？

**檢查項目**：
- 必填欄位是否都已填
- 身份驗證是否完成
- 表單格式是否正確

---

## 選擇器快速參考

| 功能 | 選擇器 | 備註 |
|------|--------|------|
| 購買人表格 | `table.purchaser-table` | 主要表格 |
| 表格行 | `tr[data-row]` | 每一行 |
| 姓名輸入 | `input[name*="name"]` | 購買人姓名 |
| 身份證 | `input[name*="id"]` | 身份驗證 |
| 電郵 | `input[name*="email"]` | 聯絡電郵 |
| 確認按鈕 | `button.confirm` | 送出訂單 |

---

## 測試檢查清單

- [ ] 頁面能否正常加載
- [ ] 購買人表格能否正常操作
- [ ] 每行資訊能否正確填寫
- [ ] 身份驗證通過
- [ ] 訂單送出成功
- [ ] 支付流程完整

---

## 開發建議

**優先改進項目**：
1. 完善表格行的填寫邏輯
2. 實現動態行添加/刪除
3. 改進身份驗證處理
4. 完整的錯誤恢復機制

---

## 相關文件

- 機制文件：`docs/03-mechanisms/08-form-filling.md` (表單填寫重點)
- 驗證矩陣：`docs/05-validation/spec-validation-matrix.md`
- 平台檢查清單：`docs/05-validation/platform-checklist.md`

---

**最後更新**：2025-11
**狀態**：🔄 開發中，優先度較低

