# 安裝與環境設定

## 系統需求
- Python 3.7-3.10 (標準版本)
- Python 3.9+ (使用 NoDriver)
- Chrome 瀏覽器最新版

## 快速安裝

### 1. 安裝基本套件
```bash
pip install -r requirement.txt
```

### 2. NoDriver 安裝 (選用，需 Python 3.9+)
```bash
# 使用上游最新版本
python -m pip install git+https://github.com/ultrafunkamsterdam/nodriver

# 或使用 MaxBot 客製版（較舊但穩定）
python -m pip install git+https://github.com/max32002/nodriver
```

### 3. 開發環境設定
```bash
git clone https://github.com/bouob/tickets_hunter.git
cd tickets_hunter
```

## WebDriver 設定

在 `settings.json` 中設定 `webdriver_type`：
- `"undetected_chromedriver"` - 推薦，隱蔽性佳
- `"selenium"` - 標準模式，相容性好
- `"nodriver"` - 進階反偵測（需 Python 3.9+）

## 設定介面

### 網頁介面（推薦）
```bash
cd tickets_hunter/src
python settings.py
# 開啟瀏覽器訪問 http://127.0.0.1:16888/
```

### 桌面介面
```bash
cd tickets_hunter/src
python settings_old.py
```

## 除錯模式

### 詳細輸出
```bash
cd tickets_hunter/src
python chrome_tixcraft.py --verbose
```

### 測試模式
```bash
cd tickets_hunter/src
python chrome_tixcraft.py --test-mode
```

### 驗證設定
```bash
cd tickets_hunter/src
python settings.py --validate
```


## 多設定檔執行

編輯 `src/config_launcher.json` 設定多個設定檔路徑：
```json
{
  "profiles": [
    "settings.json",
    "settings_profile2.json"
  ]
}
```

執行：
```bash
cd tickets_hunter/src
python config_launcher.py
```

## 時間功能設定

### 1. 效能計時功能
**用途**：測量整個搶票流程的耗時，用於效能分析和優化

**計時範圍**：
- 開始：選擇演出場次頁面
- 結束：訂單確認/結帳頁面
- 輸出：在 verbose 模式下顯示搶票耗時

**啟用方式**：
```json
{
  "advanced": {
    "verbose": true
  }
}
```

**輸出範例**：
```
bot elapsed time: 2.458 秒
TicketPlus 搶票耗時: 1.823 秒
```

### 2. 定時啟動功能 (refresh_datetime)
**用途**：在指定時間自動重整頁面啟動搶票，用於精準時間開搶

**設定方式**：
在 `settings.json` 中設定：
```json
{
  "refresh_datetime": "14:00:00"
}
```

**時間格式**：HH:MM:SS (24小時制)
- `"14:00:00"` - 下午2點整
- `"09:30:00"` - 上午9點30分
- `""` - 停用功能

**使用情境**：
1. 已知演唱會開賣時間，例如下午2點整
2. 提前開啟搶票程式並設定 refresh_datetime
3. 程式會在指定時間自動重整頁面開始搶票

**注意事項**：
- 建議提前5-10分鐘啟動程式並導航到售票頁面
- 時間僅觸發一次，重整後會開始正常搶票流程
- 適用於 Chrome 和 NoDriver 兩種模式

## 常見問題

### ChromeDriver 版本不符
下載對應 Chrome 版本的 ChromeDriver：
https://developer.chrome.com/docs/chromedriver/

### Python 版本衝突
建議使用 virtualenv：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### OCR 功能無法使用
確認已安裝 ddddocr：
```bash
pip install ddddocr
```
---

**最後更新**: 2025-10-28
