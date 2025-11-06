# 專案架構概覽

> **專案**：Tickets Hunter - 多平台搶票自動化系統

## 主程式架構

### 核心程式
- `chrome_tixcraft.py` - Selenium 搶票引擎（最完整參考標準）
- `nodriver_tixcraft.py` - 反偵測模式 (Python 3.9+)
- `settings.json` - 主設定檔

### 平台函式命名規範
- `kham_main()` - KHAM 河岸留言主函式
- `kktix_main()` - KKTIX 主函式
- `tixcraft_main()` - 拓元售票主函式

### Debug 除錯配置
```python
show_debug_message = config_dict["advanced"].get("verbose", False)
```

## WebDriver 策略層級

**遵循 NoDriver First 原則**：優先使用 NoDriver 進行開發與維護

### 1. nodriver (推薦 - 優先)
- **特色**：最強反偵測，進階規避能力
- **適用**：所有票務網站（推薦預設選擇）
- **要求**：需 Python 3.9+，async/await
- **維護狀態**：✅ 積極開發，接受新功能與 Bug 修復

### 2. undetected_chromedriver (維護模式)
- **特色**：隱蔽性佳，反偵測能力強
- **適用**：舊版回退，需要繞過偵測時
- **相容性**：完全相容 Selenium API
- **維護狀態**：⚠️ 僅嚴重錯誤修復，進入維護模式

### 3. selenium (標準場景)
- **特色**：相容性好，穩定性高
- **適用**：測試環境使用
- **限制**：容易被反機器人系統偵測
- **維護狀態**：⚠️ 淘汰計劃中

## 檔案存取規則

### ✅ 允許存取
- `*.py` - 所有 Python 程式檔案
- `settings.json` - 主設定檔
- `config_launcher.json` - 啟動器設定
- `/www/**` - 網頁介面相關檔案

### ❌ 禁止存取
- `/node_modules/` - Node.js 依賴包
- `/.git/` - Git 版本控制
- `*.log` - 日誌檔案
- `*.tmp` - 暫存檔案
- `/webdriver/*/data/**` - 瀏覽器擴充套件內部資料

## 系統架構圖

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Settings.json │    │  Chrome Driver  │    │  NoDriver       │
│     配置管理      │    │    (UC/Selenium)  │    │    (反偵測)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌─────────────────────────────────────────────────┐
         │              Tickets Hunter 主程式               │
         └─────────────────────────────────────────────────┘
                                  │
    ┌──────────────┬──────────────┼──────────────┬──────────────┐
    │              │              │              │              │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│ KHAM  │    │ KKTIX │    │TixCraft│   │TicketPlus│ │  其他  │
│寬宏售票│    │       │    │ 拓元   │   │   全票網  │ │ 平台   │
└───────┘    └───────┘    └───────┘    └───────┘    └───────┘
```

## 開發環境需求

### Python 版本
- **Chrome/Selenium**: Python 3.7+
- **NoDriver**: Python 3.9+

### 必要套件
- `undetected-chromedriver` - UC 反偵測
- `selenium` - WebDriver 標準 API
- `nodriver` - 進階反偵測 (可選)
- `requests` - HTTP 請求處理
- `beautifulsoup4` - HTML 解析

### 瀏覽器支援
- Chrome/Chromium 90+
- 自動下載對應 ChromeDriver 版本

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

**更新日期**: 2025-10-28
**相關文件**: [標準功能定義](../02-development/ticket_automation_standard.md) | [開發規範](../02-development/development_guide.md) | [函數結構](../02-development/structure.md) | [設定指南](./setup.md)