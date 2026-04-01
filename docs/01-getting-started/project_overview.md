# 專案架構概覽

**文件說明**：介紹 Tickets Hunter 專案的整體架構、核心程式模組與檔案組織結構
**最後更新**：2026-03-09

---

> **專案**：Tickets Hunter - 多平台搶票自動化系統

## 專案概述

Tickets Hunter 是一個多平台搶票自動化系統，支援台灣與香港主流售票平台，採用 ZenDriver First 開發策略，提供強大的反偵測能力與自動化購票功能。

### 主要特色
- **多平台支援**：支援 14 個售票平台
- **反偵測能力**：ZenDriver 引擎提供最強反偵測（zendriver 是 nodriver 的活躍 fork，支援 Chrome 145+）
- **智慧選擇**：支援 AND/OR 邏輯關鍵字篩選
- **OCR 驗證碼**：自動辨識與填寫驗證碼
- **設定驅動**：所有行為透過 settings.json 控制

---

## 主程式架構

### 核心程式
| 檔案 | 說明 | 維護狀態 |
|------|------|----------|
| `nodriver_tixcraft.py` | ZenDriver 反偵測引擎（**推薦**） | ✅ 積極開發 |
| `settings.json` | 主設定檔 | ✅ 持續更新 |
| `settings.py` | 網頁設定介面 | ✅ 持續更新 |

### 平台函式命名規範
```
nodriver_[平台名]_main()     - NoDriver 版本主控制器
nodriver_[平台名]_[功能]()   - NoDriver 版本功能函數
```

**範例**：
- `nodriver_tixcraft_main()` - TixCraft NoDriver 主函式
- `nodriver_kktix_main()` - KKTIX NoDriver 主函式
- `nodriver_ibon_main()` - iBon NoDriver 主函式

### Debug 除錯配置
```python
debug = util.create_debug_logger(config_dict)
debug.log("[TAG] message")
```
啟用方式：設定介面 → 進階設定 → 輸出除錯訊息（`advanced.verbose`）
時間戳記顯示：設定介面 → 進階設定 → 顯示時間戳（`advanced.show_timestamp`）

---

## 平台支援狀態

### ZenDriver 完全支援（13 個平台）✅

| 平台 | 完成度 | 說明 |
|------|--------|------|
| **TixCraft 拓元** | 84.4% | Tixcraft Family 成員 |
| **Teamear 添翼** | 84% | Tixcraft Family 成員 |
| **Indievox 獨立音樂** | 84% | Tixcraft Family 成員 |
| **KKTIX** | 100% | 台灣主流平台 |
| **TicketPlus 遠大** | 85% | 台灣主流平台 |
| **iBon** | 100% | 台灣主流平台（Shadow DOM） |
| **KHAM 寬宏** | 90% | 年代/寬宏系統 |
| **年代售票** | 100% | 年代/寬宏系統 |
| **UDN 售票** | 90% | 年代/寬宏系統 |
| **TicketMaster** | 89% | ZenDriver 專用 |
| **HK Ticketing** | 90% | 香港平台 |
| **FamiTicket** | 80% | 全家網票務 |
| **FunOne** | 92% | 台灣平台 |

### 部分支援（2 個平台）⚠️
| 平台 | 完成度 | 說明 |
|------|--------|------|
| **Cityline** | 85% | 香港平台，進行中 |
| **FANSI GO** | 58% | 台灣平台，基本功能 |

### 未實作（1 個平台）❌
| 平台 | 完成度 | 說明 |
|------|--------|------|
| **Urbtix** | 0% | 唯一未有 ZenDriver 實作 |

---

## WebDriver 策略層級

**遵循憲法第 I 條 ZenDriver First 原則**

### 優先級 1：ZenDriver（推薦）
- **特色**：最強反偵測，進階規避能力
- **適用**：所有票務網站（推薦預設選擇）
- **要求**：Python 3.10+，async/await
- **維護狀態**：✅ 積極開發，接受新功能與 Bug 修復
- **備注**：zendriver 是 nodriver 的活躍 fork，設定值 `webdriver_type: "nodriver"` 保持不變

### 優先級 2：Chrome（維護模式）
- **特色**：傳統同步架構，API 穩定
- **適用**：尚未移植至 ZenDriver 的平台（如 Urbtix）
- **維護狀態**：⚠️ 僅嚴重錯誤修復，不接受新功能

---

## 系統架構圖

```
                    ┌─────────────────────────────────────┐
                    │          settings.json               │
                    │           (配置管理)                  │
                    └─────────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                                             │
              ▼                                             ▼
    ┌─────────────────┐                        ┌─────────────────┐
    │   ZenDriver     │                        │     Chrome      │
    │  (推薦/優先)     │                        │   (維護模式)     │
    └─────────────────┘                        └─────────────────┘
              │                                             │
              └──────────────────────┼──────────────────────┘
                                     │
                    ┌─────────────────────────────────────┐
                    │       Tickets Hunter 主程式          │
                    │      (nodriver_tixcraft.py)         │
                    └─────────────────────────────────────┘
                                     │
    ┌────────────┬────────────┬──────┼──────┬────────────┬────────────┐
    │            │            │      │      │            │            │
    ▼            ▼            ▼      ▼      ▼            ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│TixCraft│ │ KKTIX  │ │  iBon  │ │Ticket+ │ │  KHAM  │ │HKTicket│ │  其他  │
│  拓元   │ │        │ │        │ │  遠大  │ │  寬宏  │ │ 快達票 │ │  平台  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

---

## 目錄結構

```
tickets_hunter/
├── src/                          # 原始碼目錄
│   ├── nodriver_tixcraft.py      # NoDriver 主程式 ⭐
│   ├── settings.py               # 網頁設定介面
│   ├── settings.json             # 主設定檔
│   ├── util.py                   # 共用工具函數
│   └── webdriver/                # 瀏覽器擴充套件
├── www/                          # 網頁介面
│   └── settings.html             # 設定頁面
├── docs/                         # 文件目錄
│   ├── 01-getting-started/       # 入門指南
│   ├── 02-development/           # 開發指南
│   ├── 03-mechanisms/            # 機制說明
│   ├── 04-implementation/        # 實作參考
│   ├── 05-validation/            # 驗證標準
│   ├── 06-api-reference/         # API 參考
│   └── 07-deployment/            # 部署指南
├── CHANGELOG.md                  # 更新日誌
└── requirement.txt               # 套件依賴
```

---

## 開發環境需求

### Python 版本
| 版本 | 狀態 | 說明 |
|------|------|------|
| **Python 3.10** | ✅ 推薦 | 完整支援 |
| **Python 3.11** | ✅ 推薦 | 完整支援 |
| **Python 3.12** | ⚠️ 可能支援 | 部分套件相容性待驗證 |
| Python 3.13+ | ❌ 不支援 | ddddocr 不相容 |

### 必要套件
| 套件 | 說明 | 重要性 |
|------|------|--------|
| `zendriver` | 進階反偵測引擎（nodriver 的活躍 fork） | 🔥 核心 |
| `ddddocr` | OCR 驗證碼辨識 | 選用 |
| `onnxruntime` | 通用 OCR 模型推論 | 核心 |
| `requests` | HTTP 請求處理 | 核心 |
| `tornado` | 設定介面 Web Server | 核心 |

### 瀏覽器支援
- Chrome/Chromium 90+（建議使用最新穩定版）
- 自動下載對應 ChromeDriver 版本

---

## 檔案存取規則

### ✅ 允許存取
- `*.py` - 所有 Python 程式檔案
- `settings.json` - 主設定檔
- `config_launcher.json` - 啟動器設定
- `/www/**` - 網頁介面相關檔案
- `/docs/**` - 文件目錄

### ❌ 禁止存取
- `/node_modules/` - Node.js 依賴包
- `/.git/` - Git 版本控制
- `*.log` - 日誌檔案
- `*.tmp` - 暫存檔案
- `/webdriver/*/data/**` - 瀏覽器擴充套件內部資料

---

## 文件架構關聯圖

```
ticket_automation_standard.md  ← 定義標準架構（12 階段功能模組）
    ↓
structure.md  ← 平台實作分析（函數索引 + 完整度評分）
    ↓
development_guide.md  ← 開發規範指南（檢查清單 + 拆分原則）
```

---

## 核心原則（憲法速記）

| 原則 | 關鍵字 | 說明 |
|------|--------|------|
| **I. ZenDriver First** | 技術優先級 | ZenDriver > Chrome（維護模式） |
| **II. 資料結構優先** | 設計先行 | 結構決定一切 |
| **III. 三問法則** | 決策守門 | 核心？簡單？相容？ |
| **IV. 單一職責** | 函數設計 | 小函數組合 |
| **V. 設定驅動** | 使用者友善 | settings.json 控制所有行為 |

**完整設計原則**：詳見專案內部文件

---

**更新日期**: 2026-03-09
**相關文件**:
- [設定指南](./setup.md) - 安裝與環境設定
- [標準功能定義](../02-development/ticket_automation_standard.md) - 12 階段標準
- [開發規範](../02-development/development_guide.md) - 開發指南
- [函數結構](../02-development/structure.md) - 函數索引