**文件說明**：Tickets Hunter 專案的疑難排解索引，收錄常見問題、平台特定問題、環境問題與已驗證的解決方案。

**最後更新**：2025-11-12

---

# Tickets Hunter 疑難排解指南

本目錄收錄 Tickets Hunter 專案常見問題與解決方案。

---

## 📋 疑難排解文件清單

### 🍎 MacOS 相關問題

- **[ddddocr MacOS ARM (M1/M2/M3) 安裝問題](ddddocr_macos_arm_installation.md)**
  - Apple Silicon 晶片安裝 ddddocr 錯誤
  - onnxruntime 相依性問題
  - 四種解決方案（Miniforge3、官方套件、Rosetta 2、Rust 版本）

---

### 🎫 平台特定問題

- **[NoDriver 網路阻擋方法拼寫錯誤 (2025-10-31)](nodriver_network_block_investigation_2025-10-31.md)** ⭐ 新增
  - Issue #35 完整調查與修復記錄
  - `set_blocked_ur_ls` 拼寫錯誤導致所有 NoDriver 啟動崩潰
  - 影響所有平台（KKTIX、TixCraft、iBon、TicketPlus）
  - 透過 settings.py 網頁介面啟動失敗問題

- **[iBon Cookie 疑難排解](ibon_cookie_troubleshooting.md)**
  - iBon 平台 Cookie 問題
  - 登入狀態保持問題

- **[iBon NoDriver 修復記錄 (2025-10-03)](ibon_nodriver_fixes_2025-10-03.md)**
  - iBon NoDriver 版本修復歷程
  - Shadow DOM 處理問題
  - 座位選擇與驗證碼處理

- **[iBon 日期關鍵字匹配問題 (2025-10-21)](../07-project-tracking/debug-2025-10-21-ibon-date-keyword-matching.md)**
  - 日期關鍵字 (date_keyword) 無法匹配問題
  - 函式清理遺失核心邏輯問題
  - 日期上下文提取與關鍵字匹配實作
  - 回退策略實作（關鍵字 → 模式）

- **iBon 日期選擇性能優化 (2025-11-08)** ⭐ 新增
  - 移除不必要的滾動操作
  - 性能提升 80% (Pierce: 6.6s → 1.3s, DOMSnapshot: 10s → 2s)
  - 簡化日期選擇邏輯
  - 程式碼行數減少約 60 行

- **[年代售票 NoDriver 下拉選單序列化問題](kham_nodriver_dropdown_serialization.md)**
  - 年代售票（ticket.com.tw）下拉選單問題
  - JavaScript 序列化錯誤修復
  - CDP DOM 操作最佳實踐

- **[年代售票提交按鈕修復記錄 (2025-10-09)](kham_ticket_submit_fix_2025-10-09.md)**
  - 提交按鈕選擇器錯誤修復
  - Bootstrap Select 參數序列化問題
  - UTK0202 頁面完整流程分析

- **[TicketPlus 日期選擇修復 (2025-10-25)](ticketplus_date_selection_fix_2025-10-25.md)**
  - 日期關鍵字匹配失敗修復
  - 雙重過濾邏輯問題
  - NoDriver + CDP 實作

- **TicketPlus 折扣碼自動填入功能 (2025-11-08)** ⭐ 新增
  - 優惠序號/加購序號自動填入
  - 支援新版 API 格式 (eventId-based)
  - JavaScript 注入 + Vue.js 事件觸發
  - 安全性：字串轉義防止注入攻擊
  - settings.json 新增 ticketplus_discount_code 欄位

- **TixCraft/Indievox 票種關鍵字匹配 (2025-11-08)** ⭐ 新增
  - 支援 Indievox Type B 頁面票種關鍵字匹配
  - 實作 area_keyword 和 area_auto_fallback 邏輯
  - 支援 AND 邏輯和排除關鍵字 (keyword_exclude)
  - 從 HTML 提取票種名稱 (<h4> 或 <td> 標籤)
  - 修復之前忽略關鍵字設定的問題

- **關鍵字逗號處理修復 (2025-11-08)** ⭐ 新增
  - 修復 "5,600" 被錯誤分割成 ['5', '600'] 的問題
  - 影響 6 個位置：TixCraft、TicketPlus、iBon、KHAM、年代售票
  - 使用 JSON 解析替代逗號分割
  - 移除雙重分割問題
  - area_auto_fallback=false 現在正確運作

---

## 🔧 其他常見問題

### 記憶體問題

**Q: 執行時出現 "Out of Memory" 錯誤**

**原因**：記憶體不足，特別是多開瀏覽器時。

**解決**：
1. 增加 Windows 虛擬記憶體（Windows）
2. 減少同時開啟的瀏覽器數量
3. 關閉其他佔用記憶體的應用程式
4. 使用 NoDriver 模式（記憶體佔用較小）

---

### 瀏覽器驅動問題

**Q: 瀏覽器驅動程式版本不符**

**原因**：Chrome 版本與 ChromeDriver 版本不匹配。

**解決**：
```bash
# 使用 webdriver-manager 自動管理
pip install webdriver-manager

# 或手動下載對應版本
# https://developer.chrome.com/docs/chromedriver/downloads
```

---

### 設定檔問題

**Q: 找不到 settings.json 檔案**

**原因**：首次執行尚未建立設定檔。

**解決**：
```bash
# 執行設定介面會自動建立
cd tickets_hunter/src
python settings.py
```

---

### 驗證碼辨識問題

**Q: 驗證碼辨識率過低**

**原因**：OCR 模型準確率限制。

**解決**：
1. 更新到最新版 ddddocr
2. 啟用手動輸入驗證碼選項
3. 調整驗證碼辨識設定（image_source）

---

### 權限問題

**Q: MacOS 執行權限被拒**

**原因**：macOS 安全性設定阻擋未簽署的應用程式。

**解決**：
```bash
# 允許執行權限
chmod +x *.py

# 或在系統偏好設定中允許
# 系統偏好設定 → 安全性與隱私權 → 一般 → 允許
```

---

## 📞 尋求協助

如果以上解決方案無法解決您的問題，請至 [GitHub Issues](https://github.com/bouob/tickets_hunter/issues) 提出問題，並提供：

1. 作業系統版本與架構（macOS/Windows/Linux, ARM64/x86_64）
2. Python 版本（`python3 --version`）
3. 完整錯誤訊息
4. 已嘗試的解決方案

---

## 📝 貢獻指南

歡迎提交新的疑難排解文件！請遵循以下格式：

1. 清楚描述問題現象
2. 分析問題原因
3. 提供多種解決方案
4. 附上參考資源連結
5. 包含驗證步驟

文件命名規範：`{問題類型}_{平台}_{簡短描述}.md`

範例：
- `ddddocr_macos_arm_installation.md`
- `chrome_driver_windows_version_mismatch.md`
- `memory_linux_optimization.md`

---

**最後更新：** 2025-11-08
