# 設定術語對照表

**用途**：當回應使用者時，應使用「使用者名稱」而非「技術名稱」，以提高使用者理解度。

---

## 基本設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `homepage` | 網址 | 基本設定 | 目標票務網址 |
| `ticket_number` | 張數 | 基本設定 | 要購買的票券數量 |
| `refresh_datetime` | 刷新在指定時間 | 基本設定 | 自動開始搶票的時間 |
| `date_auto_select.mode` | 日期排序方式 | 基本設定 | random/from_top/from_bottom |
| `date_auto_select.date_keyword` | 日期關鍵字 | 基本設定 | 指定日期的關鍵字 |
| `date_auto_fallback` | 日期自動遞補 | 基本設定 | 關鍵字未匹配時自動選擇 |
| `area_auto_select.mode` | 區域排序方式 | 基本設定 | random/from_top/from_bottom |
| `area_auto_select.area_keyword` | 區域關鍵字 | 基本設定 | 指定區域的關鍵字 |
| `area_auto_fallback` | 區域自動遞補 | 基本設定 | 關鍵字未匹配時自動選擇 |
| `keyword_exclude` | 排除關鍵字 | 基本設定 | 排除不想要的日期/區域 |

---

## 進階設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `browser` | 瀏覽器 | 進階設定 | chrome/firefox/edge |
| `webdriver_type` | WebDriver類別 | 進階設定 | nodriver/undetected_chromedriver |
| `advanced.play_sound.ticket` | 有票時播放音效 | 進階設定 | 偵測到票時播放提示音 |
| `advanced.play_sound.order` | 訂購時播放音效 | 進階設定 | 訂單成功時播放提示音 |
| `advanced.play_sound.filename` | 音效檔 | 進階設定 | 音效檔案路徑 |
| `advanced.discord_webhook_url` | Discord Webhook URL | 進階設定 | Discord 通知網址 |
| `advanced.auto_reload_page_interval` | 自動刷新頁面間隔(秒) | 進階設定 | 頁面重新載入間隔 |
| `advanced.reset_browser_interval` | 重新啟動瀏覽器間隔(秒) | 進階設定 | 瀏覽器重啟間隔 |
| `advanced.server_port` | 設定介面 Port | 進階設定 | Web Server 連接埠 |
| `advanced.proxy_server_port` | Proxy IP:PORT | 進階設定 | 代理伺服器設定 |
| `advanced.window_size` | 瀏覽器視窗大小 | 進階設定 | 視窗尺寸 |
| `advanced.chrome_extension` | Chrome 瀏覽器擴充功能 | 進階設定 | 啟用擴充功能 |
| `advanced.disable_adjacent_seat` | 允許不連續座位 | 進階設定 | 允許選擇不相鄰的座位 |
| `advanced.hide_some_image` | 隱藏部份圖片 | 進階設定 | 加速頁面載入 |
| `advanced.block_facebook_network` | 擋掉 Facebook 連線 | 進階設定 | 阻擋 FB 追蹤 |
| `advanced.headless` | 無圖形界面模式 | 進階設定 | 背景執行模式 |
| **`advanced.verbose`** | **輸出除錯訊息** | 進階設定 | **顯示詳細執行日誌** |

---

## OCR 驗證碼設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `ocr_captcha.enable` | OCR（啟用） | 進階設定 | 啟用 OCR 自動辨識驗證碼 |
| `ocr_captcha.image_source` | OCR圖片取得方式 | 進階設定 | canvas/element |
| `ocr_captcha.force_submit` | 自動送出 | 進階設定 | OCR 辨識後自動提交 |
| `ocr_captcha.path` | 自訂 OCR 模型 | 進階設定 | OCR 模型路徑 |
| `advanced.remote_url` | OCR Server URL | 進階設定 | 遠端 OCR 伺服器 |

---

## 驗證與猜題

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `advanced.user_guess_string` | 使用者自定字典 | 驗證/猜題 | 預設答案清單 |
| `advanced.auto_guess_options` | 自動猜測驗證問題 | 驗證/猜題 | 自動嘗試回答 |
| `advanced.discount_code` | 優惠代碼 | 驗證/猜題 | 折扣碼 |

---

## 帳號自動填入

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `advanced.tixcraft_sid` | 拓元家族 cookie TIXUISID | 帳號自動填 | 拓元登入憑證 |
| `advanced.ibonqware` | ibon cookie ibonqware | 帳號自動填 | ibon 登入憑證 |
| `advanced.kktix_account` / `kktix_password` | KKTIX | 帳號自動填 | KKTIX 帳密 |
| `advanced.fami_account` / `fami_password` | FamiTicket | 帳號自動填 | 全家帳密 |
| `advanced.kham_account` / `kham_password` | 寬宏 | 帳號自動填 | 寬宏帳密 |
| `advanced.ticket_account` / `ticket_password` | 年代 | 帳號自動填 | 年代帳密 |
| `advanced.udn_account` / `udn_password` | UDN | 帳號自動填 | UDN帳密 |
| `advanced.ticketplus_account` / `ticketplus_password` | 遠大 | 帳號自動填 | 遠大帳密 |
| `advanced.cityline_account` / `cityline_password` | cityline | 帳號自動填 | Cityline 帳密 |
| `advanced.urbtix_account` / `urbtix_password` | URBTIX | 帳號自動填 | URBTIX 帳密 |
| `advanced.hkticketing_account` / `hkticketing_password` | HKTICKETING | 帳號自動填 | HK Ticketing 帳密 |

---

## 執行階段設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `advanced.idle_keyword` | 系統時間 - 暫停關鍵字 | 執行階段 | 觸發暫停的時間 |
| `advanced.resume_keyword` | 系統時間 - 繼續關鍵字 | 執行階段 | 觸發繼續的時間 |
| `advanced.idle_keyword_second` | 秒數 - 暫停關鍵字 | 執行階段 | 觸發暫停的秒數 |
| `advanced.resume_keyword_second` | 秒數 - 繼續關鍵字 | 執行階段 | 觸發繼續的秒數 |

---

## KKTIX 專用設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `kktix.auto_press_next_step_button` | KKTIX點選下一步按鈕 | 基本設定 | 自動點擊下一步 |
| `kktix.auto_fill_ticket_number` | （自動填入張數） | - | 自動選擇票數 |
| `kktix.max_dwell_time` | KKTIX購票最長停留(秒) | 基本設定 | 最大等待時間 |

---

## 拓元專用設定

| 技術名稱 (settings.json) | 使用者名稱 (UI) | 位置 | 說明 |
|-------------------------|----------------|------|------|
| `tixcraft.pass_date_is_sold_out` | （跳過已售完日期） | - | 自動略過售完場次 |
| `tixcraft.auto_reload_coming_soon_page` | （自動刷新即將開賣頁面） | - | 開賣前自動刷新 |

---

## 常用術語轉換速查

| 技術術語 | 使用者友善說法 |
|---------|--------------|
| `verbose: true` | 開啟「輸出除錯訊息」選項 |
| `ocr_captcha.enable: true` | 啟用「OCR 自動辨識驗證碼」 |
| `ocr_captcha.force_submit: true` | 啟用「自動送出」 |
| `headless: true` | 啟用「無圖形界面模式」 |
| `date_auto_fallback: true` | 啟用「日期自動遞補」 |
| `area_auto_fallback: true` | 啟用「區域自動遞補」 |
| `settings.json` | 設定檔 |
| `nodriver` | NoDriver 模式（預設） |
| `webdriver_type` | WebDriver 類別 |

---

## 使用範例

### 錯誤示範（技術導向）
> 請將 `settings.json` 中的 `advanced.verbose` 設為 `true`

### 正確示範（使用者導向）
> 請在設定介面的「進階設定」中，找到「輸出除錯訊息」選項並打勾啟用

---

## 相關文件

- CLAUDE.md 使用者溝通規範：`CLAUDE.md` → 「🗣️ 使用者溝通規範」章節
- 設定介面：`src/www/settings.html`
- 設定檔案：`src/settings.json`
