================================================================================
                    Tickets Hunter - 使用說明
================================================================================

感謝您下載 Tickets Hunter 多平台搶票自動化系統！

本系統支援以下票務平台：
  - TixCraft 拓元
  - KKTIX
  - ibon 售票
  - TicketPlus 遠大
  - KHAM 寬宏
  - 年代售票
  - Indievox
  - and more ...

================================================================================
                            快速開始
================================================================================

1. 解壓縮 ZIP 檔案
   將 tickets_hunter_vXXXX.XX.XX.zip 解壓縮到任意目錄。

2. 執行 settings.exe
   雙擊 settings.exe，會自動開啟瀏覽器顯示設定介面。

3. 在網頁介面進行設定
   - 設定票務平台網址（homepage）
   - 設定購票張數、日期/區域關鍵字
   - 選擇搶票引擎（webdriver_type）：
     * nodriver - 推薦，反偵測效果最佳
     * undetected_chrome - 回退方案

4. 點擊網頁上的「搶票」按鈕
   系統會自動根據您的設定啟動對應的搶票引擎：
   - nodriver → 自動啟動 nodriver_tixcraft.exe
   - undetected_chrome → 自動啟動 chrome_tixcraft.exe

【進階功能】
   - config_launcher.exe：多開管理器，可同時搶多個場次
     （雙擊執行，使用 GUI 介面管理多個設定檔）

================================================================================
                        系統架構說明
================================================================================

【settings.exe - 主控介面】
  這是系統的主要入口，提供網頁版設定介面。

  功能：
    - 圖形化設定編輯器（無需了解 JSON 格式）
    - 即時預覽設定結果
    - 整合搶票功能（點擊「搶票」按鈕自動啟動引擎）
    - 自動管理搶票引擎的啟動與切換

  執行方式：
    雙擊 settings.exe → 瀏覽器自動開啟設定頁面

  設定引擎選項：
    - nodriver：反偵測能力最強，推薦使用
      （首次執行會自動下載 Chrome 瀏覽器，約 100-200MB）
    - undetected_chrome：傳統方案，穩定性高
      （需要 webdriver/chromedriver.exe）

【搶票引擎（自動啟動，無需手動執行）】
  - nodriver_tixcraft.exe：NoDriver 引擎
  - chrome_tixcraft.exe：Chrome/Selenium 引擎

  這兩個執行檔會由 settings.exe 根據您的設定自動啟動，
  一般使用者無需手動執行。

【config_launcher.exe - 進階功能】
  多開管理器，適合需要同時搶多個場次的進階使用者。

  功能：
    - 管理多個 settings.json 設定檔
    - 同時開啟多個搶票程式實例
    - GUI 介面，簡單易用

  執行方式：
    雙擊 config_launcher.exe → 顯示 Tkinter GUI 視窗

================================================================================
                          資料夾結構說明
================================================================================

tickets_hunter/
├── nodriver_tixcraft.exe       主要搶票程式（NoDriver）
├── chrome_tixcraft.exe          傳統搶票程式（Chrome）
├── settings.exe                 設定編輯器（Tornado Web）
├── config_launcher.exe          多開管理器（Tkinter GUI）
│
├── _internal/                   依賴函式庫目錄（請勿刪除！）
├── webdriver/                   WebDriver 與瀏覽器擴充套件
│   ├── Maxbotplus_1.0.0/        MaxBot 瀏覽器擴充套件
│   └── Maxblockplus_1.0.0/      MaxBlock 瀏覽器擴充套件
│
├── assets/                      資源檔案
│   ├── icons/                   圖示檔案
│   └── sounds/                  音效檔案
│
├── www/                         網頁設定介面
│   ├── settings.html            設定頁面
│   ├── settings.js              設定邏輯
│   └── dist/                    Bootstrap, jQuery
│
├── settings.json                設定檔範本
├── README_Release.txt           本說明文件
└── CHANGELOG.md                 版本更新記錄

【重要提醒】
  _internal/ 資料夾包含所有 4 個執行檔共用的依賴函式庫。
  請勿刪除或移動此資料夾，否則執行檔將無法運作！

================================================================================
                          首次執行步驟
================================================================================

Step 1: 執行 settings.exe
  雙擊 settings.exe，瀏覽器會自動開啟設定介面。

Step 2: 在網頁介面設定關鍵參數
  - homepage：票務平台網址（例如：https://tixcraft.com）
  - ticket_number：購票張數
  - webdriver_type：搶票引擎（nodriver / undetected_chrome）
  - tixcraft.date_auto_select_mode：日期選擇模式
  - tixcraft.area_auto_select_mode：區域選擇模式
  - tixcraft.keyword：日期/區域關鍵字（支援多組 AND/OR 邏輯）

Step 3: 點擊網頁上的「搶票」按鈕
  系統會自動啟動對應的搶票引擎（nodriver 或 chrome）。

Step 4: 監控執行
  - 搶票程式會顯示執行進度與 log
  - 成功進入購票頁面時會發出音效提示（如有設定）
  - 完成後請手動填寫驗證碼與個人資料

【進階使用者】
  如需直接執行搶票引擎（不透過網頁介面）：
    nodriver_tixcraft.exe --input settings.json
    chrome_tixcraft.exe --input settings.json

【需要更詳細的教學？】
  本文件為快速參考手冊，更詳細的圖文教學請參閱：
  👉 安裝與首次執行指南
     https://github.com/bouob/tickets_hunter/blob/main/guide/installation.md
  👉 基本設定教學
     https://github.com/bouob/tickets_hunter/blob/main/guide/basic-settings.md

================================================================================
                          常見問題 FAQ
================================================================================

Q1: 執行檔點擊後沒有反應？
A1: 請確認：
    - _internal/ 資料夾與執行檔在同一目錄
    - 防毒軟體沒有阻擋執行檔
    - 使用「以系統管理員身分執行」

Q2: 出現「找不到 python310.dll」錯誤？
A2: _internal/ 資料夾被刪除或移動，請重新解壓縮 ZIP 檔案。

Q3: NoDriver 版本首次執行很慢？
A3: 正常現象，NoDriver 首次執行會自動下載 Chrome 瀏覽器（約 100-200MB）。
    下載完成後後續執行會變快。

Q4: Chrome 版本出現「chromedriver.exe 不相容」錯誤？
A4: 請到 https://chromedriver.chromium.org/ 下載與您的 Chrome 版本相符的
    chromedriver.exe，並放到 webdriver/ 目錄中。

Q5: 驗證碼辨識失敗？
A5: ddddocr 驗證碼辨識準確率約 80-90%，失敗時請手動輸入。

Q6: 可以同時搶多個場次嗎？
A6: 可以！使用 config_launcher.exe（多開管理器）管理多個設定檔。
    透過 GUI 介面可以同時開啟多個搶票程式，搶不同場次。

Q7: 我需要手動執行 nodriver_tixcraft.exe 或 chrome_tixcraft.exe 嗎？
A7: 一般不需要！只要執行 settings.exe，在網頁介面點擊「搶票」按鈕，
    系統會自動啟動對應的搶票引擎。手動執行僅適合進階使用者。

Q8: settings.json 格式錯誤導致程式無法執行？
A8: 請使用 settings.exe（網頁版編輯器）編輯設定檔，可避免 JSON 格式錯誤。
    或者刪除 settings.json，程式會自動重新建立範本。

Q9: 如何更新到新版本？
A9: 從 GitHub Releases 下載最新 ZIP 檔案，解壓縮後覆蓋舊版本即可。
    設定檔 settings.json 可保留繼續使用。

Q10: Windows Defender 提示「威脅已阻止」？
A10: 這是 Windows Defender SmartScreen 的誤判（因為執行檔沒有數位簽章）。
     解決方案：
     - 點擊「詳細資訊」→「仍要執行」
     - 或將資料夾加入 Windows Defender 排除清單

Q11: 執行時出現防火牆提示？
A11: settings.exe 需要開啟網頁伺服器，搶票引擎需要網路連線。
     請允許防火牆存取。

================================================================================
                          法律聲明
================================================================================

本軟體僅供個人使用，禁止用於以下用途：
  - 商業黃牛行為
  - 大量批量搶票
  - 破壞票務平台正常營運
  - 違反票務平台使用條款

使用本軟體造成的任何後果（包括但不限於帳號封禁、法律責任），
使用者需自行承擔，開發者不負任何責任。

請遵守票務平台的使用條款與當地法律法規。

================================================================================
                          支援與回報問題
================================================================================

GitHub Repository:
  https://github.com/bouob/tickets_hunter

Issue Tracker:
  https://github.com/bouob/tickets_hunter/issues

📚 線上完整文件與教學:
  - 安裝與首次執行指南（詳細圖文教學）
    https://github.com/bouob/tickets_hunter/blob/main/guide/installation.md

  - 基本設定教學（網址、票數、關鍵字設定）
    https://github.com/bouob/tickets_hunter/blob/main/guide/basic-settings.md

  - 關鍵字與回退機制（理解搶票邏輯）
    https://github.com/bouob/tickets_hunter/blob/main/guide/keyword-mechanism.md

  - 詳細設定說明（settings.json 完整欄位參考）
    https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md

  - 使用者手冊總覽
    https://github.com/bouob/tickets_hunter/blob/main/guide/README.md

================================================================================
                          支援專案開發
================================================================================

如果覺得有幫助，歡迎贊助支持：
  https://buymeacoffee.com/victor0x1

================================================================================

版本：2025.11.19
最後更新：2025-11-19

祝您搶票成功！
================================================================================
