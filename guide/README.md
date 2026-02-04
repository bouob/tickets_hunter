# Tickets Hunter 使用者手冊

> **返回主頁** → [README.md](../README.md)

---

## 選擇您的使用方式

### 一般使用者（推薦）

**使用執行檔版本，無需安裝 Python**

1. **[安裝與首次執行](installation.md)** - 完整圖文教學
   - 下載與解壓縮
   - 首次設定流程
   - 開始搶票

### 開發者 / 進階使用者

**使用 Python 原始碼，可自訂功能**

1. **[快速入門指南](quick-start.md)** - 5 分鐘快速設定
   - 環境需求與安裝
   - 執行設定介面
   - 開始搶票

---

## 所有使用者必讀

### 核心概念

| 文件 | 說明 | 建議閱讀時機 |
|------|------|--------------|
| **[關鍵字與回退機制](keyword-mechanism.md)** | 深入理解搶票邏輯 | 設定關鍵字前 |

### 進階參考

| 文件 | 說明 | 建議閱讀時機 |
|------|------|--------------|
| **[詳細設定說明](settings-guide.md)** | settings.json 完整欄位參考 | 需要微調設定時 |

---

## 常見問題快速導覽

### 關鍵字設定相關

- **日期關鍵字怎麼設？** → [關鍵字機制 - 日期關鍵字](keyword-mechanism.md#日期關鍵字)
- **區域關鍵字怎麼設？** → [關鍵字機制 - 區域關鍵字](keyword-mechanism.md#區域關鍵字)
- **AND 邏輯是什麼？** → [關鍵字機制 - AND 邏輯](keyword-mechanism.md#and-邏輯多條件組合)
- **回退機制怎麼運作？** → [關鍵字機制 - 回退機制](keyword-mechanism.md#回退機制)

### 設定相關

- **搶票中可以改設定嗎？** → [設定說明 - 即時修改設定](settings-guide.md#搶票中即時修改設定--v202602-新增)
- **驗證碼怎麼處理？** → [設定說明 - OCR 設定](settings-guide.md#ocr-設定)
- **票數怎麼設定？** → [設定說明 - 票券設定](settings-guide.md#票券設定)
- **Cookie 登入怎麼用？** → [設定說明 - 進階設定](settings-guide.md#進階設定)

---

## 文件架構

```
guide/
├── README.md              ← 您在這裡（入口頁）
├── installation.md        ← 執行檔版本教學
├── quick-start.md         ← Python 版本教學
├── keyword-mechanism.md   ← 關鍵字機制詳解
└── settings-guide.md      ← 完整設定參考
```

---

## 需要更多協助？

- **Discord 社群**：[加入討論](https://discord.gg/GCE5s6W6dV)
- **回報 Bug**：[GitHub Issues](https://github.com/bouob/tickets_hunter/issues/new?template=bug_report.md)
- **功能建議**：[Feature Request](https://github.com/bouob/tickets_hunter/issues/new?template=feature_request.md)
