# 機制 18：通用 OCR 模型選擇（跨階段）

**文件說明**：說明驗證碼 OCR 的雙模型（universal / tixcraft_tm）自訓練架構、依平台自動選模型的決策邏輯，以及找不到模型時回退官方 ddddocr 的機制
**最後更新**：2026-06-14

---

## 概述

Stage 7（驗證碼處理）的圖形驗證碼辨識，預設使用專案**自訓練的 ONNX 模型**，而非 ddddocr 官方內建模型。自訓練模型針對各售票平台的驗證碼樣式最佳化，準確率顯著高於官方通用模型。

- **輸入**：驗證碼圖片（base64 / bytes）
- **輸出**：辨識字串
- **關鍵技術**：`ddddocr` 載入自訓練 ONNX 權重 + 自訂字元集；依平台首頁自動挑模型；模型缺失時回退官方 ddddocr
- **優先度**：🟡 P2 — 影響辨識準確率，非阻斷流程（有回退）

兩個自訓練模型：

| 模型 | 路徑 | 適用平台 |
|------|------|----------|
| **universal** | `assets/model/universal/` | 通用，多數平台的預設（iBon、KHAM 等） |
| **tixcraft_tm** | `assets/model/tixcraft_tm/` | TixCraft / Ticketmaster.sg / indievox 家族 |

每個模型目錄含兩個檔案：`custom.onnx`（權重）+ `charsets.json`（字元集定義）。字元集由 `charsets.json` 內建，**不需要** `set_ranges()`。

---

## 模型工廠（`src/nodriver_common.py`）

OCR 建立集中於兩個工廠函式，符合「OCR 工廠屬 `nodriver_common.py`」的模組職責。

### `create_universal_ocr(config_dict)`

讀 `ocr_captcha.use_universal` 與 `ocr_captcha.path`，載入**指定路徑**的模型：

```
use_universal == False        → return None
path 為空                     → return None
path/custom.onnx 或 charsets.json 不存在 → 記 log，return None
否則 → ddddocr.DdddOcr(det=False, ocr=False, import_onnx_path=..., charsets_path=...)
```

回傳 `None` 代表「不用自訓練模型」，由呼叫端回退官方 ddddocr。

### `create_ocr_for_platform(config_dict)`

在 `create_universal_ocr` 之上，依平台首頁自動挑模型（常數 `CONST_TIXCRAFT_TM_MODEL_PATH` / `CONST_DEFAULT_UNIVERSAL_PATH`）：

```
1. use_universal == False                          → None（呼叫端回退 ddddocr）
2. path 為非預設的自訂路徑                          → 用使用者自訂路徑（create_universal_ocr）
3. homepage 含 tixcraft.com / indievox.com / ticketmaster.
   → 嘗試 tixcraft_tm；載入成功則用之，否則往下
4. 其餘情況                                         → universal
```

決策中以淺拷貝 `config_dict` 覆寫 `ocr_captcha.path` 為 tixcraft_tm 路徑後再交給 `create_universal_ocr`，不改動原設定。

---

## 啟動初始化（`src/nodriver_tixcraft.py`）

主迴圈啟動時建立單一 OCR 實例，沿主迴圈傳遞給各平台模組：

```python
if config_dict["ocr_captcha"]["enable"]:
    ocr = create_ocr_for_platform(config_dict)   # 依 homepage 自動挑模型
    if ocr is None:                              # 未啟用 / 模型缺失
        ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
        ocr.set_ranges(1)                         # 回退官方模型才需限定字元集
```

因為 `create_ocr_for_platform` 已依 homepage 決定模型，非 TixCraft 家族平台（如 KHAM）在此即取得 universal 實例，再經參數傳入（如 `nodriver_kham_auto_ocr(tab, config_dict, ocr, ...)`）。

---

## 平台模型對應

| 平台 | 取得模型方式 | 實際模型 | 回退（模型缺失） |
|------|-------------|---------|-----------------|
| **TixCraft / Ticketmaster.sg / indievox** | 主迴圈 `create_ocr_for_platform` | tixcraft_tm（缺則 universal） | 官方 ddddocr + `set_ranges(1)` |
| **iBon** | 驗證碼流程內直接 `create_universal_ocr` | universal | 官方 ddddocr + `set_ranges(0)` |
| **KHAM** | 主迴圈傳入的 OCR 實例 | universal | 同主迴圈回退 |
| **FunOne** | **不使用自訓練模型** | 官方 ddddocr（硬編） | — |

**FunOne 為刻意例外**：`src/platforms/funone.py` 永遠以官方 `ddddocr.DdddOcr(beta=False)` + `set_ranges(5)` 建立並快取於模組 `_state`，即使啟用通用模型也不採用——因 FunOne 驗證碼為大寫英數，通用模型實測準確率不足。

---

## 回退鏈與 `set_ranges`

```
工廠函式回傳 None
   → 呼叫端建立 ddddocr.DdddOcr(beta=ocr_captcha.beta)
   → 呼叫 set_ranges(N) 限定字元集
```

`set_ranges(N)` **僅在回退到官方 ddddocr 時生效**；自訓練模型的字元集由 `charsets.json` 決定，無需此呼叫。各平台的 N 值（ddddocr 內建範圍）：

| 平台 | `set_ranges` | 字元範圍 | 依據 |
|------|-------------|---------|------|
| TixCraft 家族 | `1` | 純小寫 a-z | `nodriver_tixcraft.py` 啟動回退 |
| iBon | `0` | 純數字 0-9 | `ibon.py` 驗證碼流程回退 |
| FunOne | `5` | 大寫 A-Z + 數字 0-9 | `funone.py`（程式碼註解明載） |

---

## 設定（`src/settings.py` → `ocr_captcha`）

| 鍵 | 預設 | 說明 |
|----|------|------|
| `enable` | `true` | 是否啟用 OCR |
| `beta` | `true` | 官方 ddddocr 的 beta 模式（回退時用） |
| `force_submit` | `true` | 辨識後自動送出 |
| `image_source` | `canvas` | 圖片來源（canvas / NonBrowser） |
| `use_universal` | `true` | **自訓練模型總開關**，關閉則一律用官方 ddddocr |
| `path` | `assets/model/universal` | 模型目錄；非預設值視為使用者自訂路徑 |

**UI 名稱**：設定頁的「**自訓練模型**」開關（對應 `ocr_captcha.use_universal`）。說明文字：「使用內建通用模型（準確率 99%+），停用改回官方 ddddocr」。勾選時自動把路徑欄填回 `assets/model/universal`，取消勾選則清空。

**遷移**：舊鍵 `advanced.ocr_model_path` 由 `migrate_config()` 搬移為 `ocr_captcha.path`。

---

## 常見問題

### Q1：universal 與 tixcraft_tm 差在哪？

tixcraft_tm 是專為 TixCraft / Ticketmaster.sg 字型訓練的較大模型，這些平台會自動採用；其餘平台用涵蓋面較廣的 universal。兩者皆自訓練 ONNX，準確率均高於官方 ddddocr。

### Q2：辨識結果變成亂碼怎麼辦？

於設定頁關閉「自訓練模型」改回官方 ddddocr 測試。若官方模型正常而自訓練異常，可能是模型檔損毀或字元集不符，回報並附驗證碼樣本。

### Q3：為什麼 FunOne 不用自訓練模型？

FunOne 驗證碼為大寫英數，通用模型實測準確率不足，因此硬編為官方 ddddocr + `set_ranges(5)`，不受 `use_universal` 影響。

### Q4：我可以用自己訓練的模型嗎？

可以。把 `custom.onnx` + `charsets.json` 放到任意目錄，將 `ocr_captcha.path` 指向該目錄（非預設值）。此時自動挑模型停用，一律使用你的路徑（見 `create_ocr_for_platform` 第 2 條）。模型訓練流程見 `captcha-trainer` skill。

---

## 相關文件

- [Stage 7：驗證碼處理](./07-captcha-handling.md) - OCR 在搶票流程中的使用
- [16-yii2-captcha-hash.md](./16-yii2-captcha-hash.md) - TixCraft / Ticketmaster.sg 的答案預驗證（搭配 tixcraft_tm）
- [ddddocr API 指南](../06-api-reference/ddddocr_api_guide.md) - ddddocr 用法
- [程式碼結構分析](../02-development/structure.md) - 函式索引

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2026-06-14 | 初版：補記通用 / tixcraft_tm 雙模型自動選擇機制（commit ee89ffbc、87f92a52） |
