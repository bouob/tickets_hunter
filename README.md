# Max搶票機器人
MaxBot是一個免費、開放原始碼的搶票機器人。祝您搶票成功。

MaxBot is a FREE and open source bot program. Good luck getting your expected ticket.

# Download (搶票程式下載)
https://github.com/max32002/tixcraft_bot/releases

附註: 如果你是 macOS, 且安裝的 python 版本是 3.12.x 版, 會無法執行, 請移除後並降低版本為 python 3.10.x 版, 原因是使用的第三方套件undetected-chromedriver 暫時無法相容於 python 3.12.x 版.

# Demo (示範影片)

https://github.com/max32002/tixcraft_bot/blob/master/demo_video.md

# How to use (如何使用)
* tixcraft / indievox / ticketmaster: https://max-everyday.com/2018/03/tixcraft-bot/
* kktix: https://max-everyday.com/2018/12/kktix-bot/
* FamiTicket: https://max-everyday.com/2019/01/maxbot-famiticket/
* ibon: https://max-everyday.com/2023/01/ibon-bot/
* cityline: https://max-everyday.com/2019/03/cityline-bot/
* urbtix: https://max-everyday.com/2019/02/urbtix-bot/
* hkticketing / galaxymacau: https://max-everyday.com/2023/01/hkticketing-bot/

如果你想在 interpark 上搶票, 你需要去下載另一個專門為 interpark 量身定制的 Max Interpark Bot:

https://max-everyday.com/2023/08/interpark-bot/

# How to execute source code (透過原始碼的執行方法)
1: download chromedrive to "webdriver" folder:
http://chromedriver.chromium.org/downloads

change the chromedrive in chrome_tixcraft.py, source code:
<code>chromedriver_path =Root_Dir+ "webdriver/chromedriver"</code>
the default path is the script path + "webdriver/chromedriver", My suggestion is to create a new directory, then move the chromedrive under new folder.

2: <code>python3 -m pip install -r pip-req.txt</code>

3: <code>python3 settings.py</code>

PS:
* this script only running in python3. (原始碼只可以在 python3 下執行。）
* 請先確定你的python 執行環境下已安裝 selenium 及相關的套件，請參考 pip-req.txt 檔案內容。
* 如果是 2022-09-13 之前的版本，請到ChromeDriver網站 ([https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)) 下載與您目前相同版本的 ChromeDriver 的執行檔，放在搶票程式的webdriver目錄下(Mac電腦請放到 MaxBot.app 套件裡的 /Contents/Resources/webdriver/)，在執行搶票程式前，第一次執行搶票主程式前，前請先手動點 ChromeDriver 的執行檔。
* 透過 python3 執行 settings.py 就可以有 GUI 的設定界面。
* 如果你是使用 macOS 並且執行環境沒有 python3，請 python 官方網站([https://www.python.org/downloads/](https://www.python.org/downloads/))來安裝 python3, 如果在 macOS 裡會使用終端機(Terminal)，建議使用 https://brew.sh/ 安裝 python3.
* 如果你是使用 Firefox, ChromeDriver 的元件是叫 geckodriver，下載點在：https://github.com/mozilla/geckodriver/releases ，與 ChromeDriver 的處理方式是一樣，如果是 mac 電腦，要在元件按右鍵開啟，做一次授權的動作，mac 有2個版本，-macos.tar.gz 與 -macos-aarch64.tar.gz ，如果是 intel CPU 的版本，請服用前面沒有 aarch64 的版本。

PS：搶票程式可以多開chrome瀏覽器，如果你電腦效能高。

PS：「掛機模式」的選項，指人不需要在電腦前，驗證碼會猜到對為止。

# Introduce the implement (實作方法)
https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/

# Execute suggestion (搶票建議)
please run this source code with high performance hardware computer and high speed + stable network.

門票的「限量」是很殘酷的，建議不要用破舊的電腦或連線不穩的手機網路來搶票，因為只要比別人慢個 0.1 秒，票可能就沒了。為了要搶到限量的票真心建議去一下網咖或找一個網路連線穩定且快的地方並使用硬體不差的電腦來搶票。

# TODO about cpatcha (關於驗證碼)

目前自動輸入驗證碼用的元件是:

https://github.com/sml2h3/ddddocr

附註：
* macOS 新的電腦 arm 系列, 暫時沒有提供自動輸入驗證碼功能, 使用上的限制和 ddddocr 相同. 暫時的解法是透過Rosetta來模擬 Intel CPU 環境. 請參考: https://github.com/max32002/tixcraft_bot/issues/82
* macOS 舊款intel CPU 的電腦裡的 python 版本要降到低於等於 3.9版 或 3.10版, 例如:
  https://www.python.org/ftp/python/3.9.13/python-3.9.13-macosx10.9.pkg
  https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg
  https://www.python.org/ftp/python/3.10.9/python-3.10.9-macos11.pkg
* 猜測驗證碼時比較容易出錯的是字英 f 和 t，還有 q 和 g, v 和 u 還有 w.
* 猜測驗證碼必錯的情況是，目前不允許有重覆的2個字母出來。


想自動輸入驗證碼，可以參考看看：實作基於CNN的台鐵訂票驗證碼辨識以及透過模仿及資料增強的訓練集產生器 (Simple captcha solver based on CNN and a training set generator by imitating the style of captcha and data augmentation)

https://github.com/JasonLiTW/simple-railway-captcha-solver

# 搶票常見問題整理

詳全文：https://max-everyday.com/2023/02/common-problem-when-you-buy-ticket/

整理大家在搶票時常遇到的問題：
* 使用搶票程式有違法嗎？
* 沒講清楚成功後的報酬
* 買到太多票
* 如何處理多的票？
* 使用搶票程式會讓自己的帳號被鎖住嗎？
* 拓元的搶票，要多少的網路頻寬才夠？
* 使用VPN/代理伺服器(Proxy)來搶票會有用嗎？
* Firefox和chrome搶票上有差距嗎？我看大家基本上都用chrome 很少用Firefox.
* 為什麼要設計搶票的機制？
* 為什麼網頁會有驗證碼？
* 你的硬體設備該不該升級？
* 想組一台新的電腦，是不是可以給我一些建議呢？


# Supporting the Project (贊助Max)

如果這個項目對您有幫助，不妨請作者我喝杯咖啡 ：）

目前支援的贊助方式：
* 台灣的ATM匯款: 中國信託 (代碼：822) 帳號：071512949756
* 7-11 ATM的無卡存款
* 街口支付： 901643378
* 悠遊付
* PayPal： weng.32002@gmail.com
* 支付寶: 13717075071

詳細的圖文贊助教學如下： https://max-everyday.com/about/#donate
