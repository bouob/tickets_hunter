# 機制 19：購票資格（跨階段）

**文件說明**：KKTIX 限定身分票券的資格選擇機制——三種 `oq.type` 的 DOM 判定、資格區塊隨票數動態插入的時序、radio 與序號的填寫順序，以及 #377 / #375 死鎖的成因
**最後更新**：2026-08-04

**適用平台**：KKTIX
**相關階段**：Stage 6（票數設定）→ 本機制 → Stage 10（訂單送出）
**相關 Issue**：#377、#375

---

## 1. 這是什麼

KKTIX 部分活動限定特定身分才能購買（信用卡優先購、會員序號、粉絲團專屬等）。
這類活動在票數設定完成後，會在票種區塊內插入一段「購票資格」UI，
使用者必須先選定一項資格才能送出訂單。

**這是 KKTIX 的通用機制，不是個別活動的客製版面。** 任何活動只要設了
`orderStageQualifications`，就會渲染同一套 DOM。

---

## 2. DOM 結構

```html
<div ng-if="hasOrderStageQualifications && ticketModel.quantity > 0" class="code-input">
  <div class="control-group">
    <label class="control-label">本票券需要符合以下任一資格才可以購買：</label>
    <div class="controls">
      <label class="radio" ng-if="oq.type != 'invitation_code'"
             ng-repeat="oq in orderStageQualifications track by $index">
        <input type="radio" ng-model="ticketModel.use_qualification_id"
               ng-disabled="oq.disabled" name="condition-<ticketId>" value="<qualificationId>">
        請輸入開頭為「TH」的代碼
        <input class="member-code" ng-if="oq.type == 'member_code'" type="text"
               ng-model="ticketModel.member_codes[oq.id]"
               ng-disabled="checkSelectedQ(oq.id)">
      </label>
    </div>
  </div>
</div>
```

兩個容易誤判的性質：

**(a) 選完張數才出現。** `ng-if` 條件含 `ticketModel.quantity > 0`，所以資格區塊
在 Stage 6 完成之前根本不在 DOM 裡。使用者回報的「選完張數就停住」正是這個時序。

**(b) 綁在票種內。** `div.code-input` 位於各自的 `.ticket-unit` 之下。
用 `document.querySelectorAll` 全域抓取，在多票種頁面會抓到別的票種的欄位。
偵測必須先解析出「張數 > 0 的那個 ticket-unit」當作用域。

---

## 3. 三種資格型態

型態由 `oq.type` 決定，但 Angular scope 不可靠讀取，因此一律**從 DOM 形狀推導**：

| 型態 | 判定依據 | 需要的動作 |
|------|----------|------------|
| `member_code` | label 內含 `input.member-code` | 選 radio + 填序號 |
| `joined` | label 內含 `span[ng-if] > a[ng-href="#"]`（「已加入」標記）| 無，已滿足 |
| `plain` | 兩者皆無（如「台新銀行 Richart 信用卡優先購」）| 只需選 radio |

`invitation_code` 型被 `ng-if="oq.type != 'invitation_code'"` 排除在這個 repeat 之外，
另走 `ticketModel.invitationCodes` 的獨立區塊。

### 關於 `ng-disabled` 的常見誤解

`input.member-code` 帶有 `ng-disabled="checkSelectedQ(oq.id)"`，很容易假設
「沒選 radio 就不能填序號」。**實測快照的 DOM property `disabled` 為 false** ——
未選 radio 時序號欄位是可以填的。radio 並不是用來解鎖輸入框，
它本身就是一個獨立的必填動作。

因此偵測必須讀 DOM property，不能從 `ng-disabled` 屬性存在與否去推論。

---

## 4. 狀態機

`nodriver_kktix_check_qualification` 回傳三種 status：

| status | 條件 | 流程行為 |
|--------|------|----------|
| `missing` | 頁面無 `div.code-input`，或有區塊但無 radio 也無輸入框 | 不干預，直接往下一步 |
| `satisfied` | 有 `joined` 選項／已選 plain 選項／已選 member_code 且序號已填 | 可以按下一步 |
| `pending` | 有選項但未選；或已選 member_code 但序號未填；或偵測到 invitation 型 | **不按下一步**，下一輪重試 |

偵測失敗（例外、回傳型別不符）時一律退回 `missing`。
保守方向刻意設定為「讓流程往前走」——偵測誤判造成的阻塞，比誤按一次下一步更難恢復。

---

## 5. 選擇策略：一律選第一個可選的

多個資格並存時，選擇**第一個既非 disabled 也未被選中**的選項。

不提供關鍵字設定的理由：資格清單是各活動自訂的短清單，
一個存錯的關鍵字會在所有活動上靜默擋掉購買，而搶票當下沒有時間察覺與修正。
選第一個可選項的失敗模式是明確的（選錯資格會被 KKTIX 後端擋下並顯示訊息），
比靜默不動好診斷。

---

## 6. 執行順序（重要）

```
Stage 6 票數設定
    ↓  資格區塊此時才被 Angular 插入 DOM
nodriver_kktix_check_qualification      讀取狀態
    ↓  status == 'pending'
nodriver_kktix_select_qualification     選第一個可選 radio（JS click，見下）
    ↓  型態為 member_code
nodriver_kktix_wait_member_code_enabled 輪詢等 ng-disabled 解除
    ↓
nodriver_kktix_order_member_code        填序號（取 advanced.discount_code）
    ↓
nodriver_kktix_check_qualification      重新確認
    ↓  status != 'pending'
nodriver_kktix_press_next_button        送出
```

**序號必須在選定 radio 之後才填。** 序號欄位隸屬於某一個資格選項，
在選定之前填寫會寫到錯誤的（或不存在的）選項上。

**radio 必須用 JS click。** zendriver 的原生 click 不會驅動 AngularJS 的 `ng-model`。

**等待用輪詢，不用固定 sleep。** `ng-disabled` 在下一個 digest cycle 才解除，
固定延遲在搶票尖峰的高 CPU 負載下會過早觸發。輪詢逾時不視為致命錯誤，下一輪自然重試。

---

## 7. invitation_code 為何不自動化

15 份真實頁面快照中，`ticketModel.invitationCodes` **全部只以未渲染的 ngRepeat
註解錨點存在**，沒有任何一份拍到它實際展開的樣子。

依測試規範（禁止循環驗證），不得憑空發明選擇器去操作沒見過的 DOM。
現行作法是偵測到非 `member-code` 的文字輸入框時，記錄一行 log 並讓
status 維持 `pending`（即不按下一步），把控制權交還使用者手動處理。

取得真實快照後再實作。

---

## 8. 歷史缺陷（#377 / #375）

修復前的程式碼用「頁面上有沒有文字輸入框」來決定要不要處理 radio：

```python
input_text_element = await tab.query_selector('...label[ng-if] > input[type="text"]')
if input_text_element is None:
    ...  # 找 radio、點 radio、清空 control_text
```

前提是「有輸入框」與「有 radio」互斥。但 `member_code` 型**兩者共存**，
條件恆為 False，整個 radio 處理與後續的清空邏輯全被跳過，
`control_text` 因此沒有任何路徑會被清空，流程永遠走不到按鈕點擊。

症狀：張數、資格、同意條款在畫面上都已就緒，就是不按「下一步」。

同時期還有一個放大因子：外層守衛與內層檢查是兩份各自為政的 JS，
對 `member-code` 一個用 OR 一個用 AND、對 `disabled` 一個看一個不看。
外層判定為「已填妥」而擋掉整個票券流程時，內層卻判定為「未填妥」而不按下一步，
形成自我維持的死鎖。現已統一為單一偵測來源，守衛語意也改為「剛送出過的冷卻期」。

---

## 9. 相關程式碼

| 函式 | 職責 |
|------|------|
| `CONST_KKTIX_FORM_STATE_JS` | 單一表單狀態來源（作用域解析 + 型態推導 + 狀態機）|
| `nodriver_kktix_check_form_state` | 讀取完整表單狀態 |
| `nodriver_kktix_check_qualification` | 取資格子集 |
| `nodriver_kktix_check_form_ready` | 票數 + 條款 + 資格是否全部就緒 |
| `nodriver_kktix_select_qualification` | 選第一個可選 radio |
| `nodriver_kktix_wait_member_code_enabled` | 輪詢等 ng-disabled 解除 |
| `nodriver_kktix_order_member_code` | 填會員序號 |
| `nodriver_kktix_handle_qualification_and_next` | 編排上述流程並送出 |

皆位於 `src/platforms/kktix.py`。

## 10. 測試

| 檔案 | 涵蓋 |
|------|------|
| `tests/integration/test_kktix_qualification.py` | DOM 事實（radio 與 member-code 共存、作用域、ng-disabled 實況）|
| `tests/integration/test_kktix_form_state.py` | 偵測 JS 的型態分類與狀態機 |

fixture 取自 `.temp/platform/kktix/` 的真實頁面快照，已複製至
`tests/fixtures/html/kktix/`。

---

## 相關文件

- `06-ticket-count.md` — 票數設定（資格區塊出現的前置條件）
- `08-form-filling.md` — 序號填寫的時序約束
- `02-authentication.md` — KKTIX 登入與前置關卡
