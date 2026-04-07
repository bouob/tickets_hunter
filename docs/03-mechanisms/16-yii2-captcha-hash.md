# Yii2 Captcha Hash 預驗證機制

**文件說明**：說明 TixCraft / TicketMaster.sg 驗證碼答案預驗證的運作方式，以及本次更新帶來的改善
**最後更新**：2026-04-07

---

## 這次更新做了什麼

2026.04.07 版本針對 TixCraft 和 TicketMaster.sg 新增了「驗證碼答案預驗證」功能。

**舊流程**：OCR 辨識 → 送出 → 等伺服器回應 → 若答錯再重試
**新流程**：OCR 辨識 → **本機預先驗證** → 若有把握才送出；發現疑似錯誤時自動修正

效果：
- 減少不必要的送出次數，降低被伺服器偵測的風險
- 辨識有 1 個字元偏差時，系統自動修正後再送出，而非重試整輪

---

## 使用者須知

此功能自動運作，**不需要任何設定**。

| 情境 | 行為 |
|------|------|
| 首次進入驗證碼頁面 | 無法預驗證，維持原流程 |
| 第一次答錯後刷新驗證碼 | 開始啟用預驗證 |
| OCR 辨識結果有把握 | 直接送出 |
| OCR 辨識有 1 字元疑似錯誤 | 自動修正後送出 |
| 無法修正 | 重新載入驗證碼，省去送出→等錯誤回應的往返 |

> 首次進入頁面時 hash 尚未建立，此功能從第二次重試起生效。這是 Yii2 框架的設計，非 bug。

---

## 機制概述（開發者）

Yii2 Framework 的 `CaptchaAction` 在每次刷新驗證碼圖片時，會把正確答案的 hash 值存入頁面的 jQuery body data：

```
$('body').data('yiiCaptcha/ticket/captcha') → [hash1, hash2]
```

hash 公式（TixCraft / TicketMaster.sg 實測確認）：
```python
hash1 = sum(ord(c) << i for i, c in enumerate(code.lower()))
# 範例：'igga' → 105 + 206 + 412 + 776 = 1499
```

Bot 流程（`nodriver_tixcraft_auto_ocr` 內）：

```
OCR 辨識 answer
    ↓
取得 hash1（nodriver_get_yii_captcha_hash）
    ├─ hash1 == 0（首次載入）→ 直接送出
    ├─ yii_captcha_verify(answer, hash1) 吻合 → 送出
    ├─ 不吻合，yii_captcha_edit1 有解 → 修正後送出
    └─ 不吻合且無解 → reload captcha，不送出
```

---

## 程式碼位置

| 函式 | 檔案 | 說明 |
|------|------|------|
| `yii_captcha_hash` | `src/util.py` | 計算 hash 值 |
| `yii_captcha_verify` | `src/util.py` | 驗證答案是否吻合 |
| `yii_captcha_edit1` | `src/util.py` | 嘗試修正 1 個字元的偏差 |
| `nodriver_get_yii_captcha_hash` | `src/platforms/tixcraft.py` | 從 DOM 讀取 hash1 |
| 預驗證流程 | `src/platforms/tixcraft.py` | `nodriver_tixcraft_auto_ocr` 內 |

單元測試：`tests/unit/test_util_yii_hash.py`（13 個測試）

---

## 相關文件

- [Stage 7: 驗證碼處理](07-captcha-handling.md) — 使用者設定說明
- 內部技術細節：`docs/internal/reference/yii2-captcha-hash.md`
