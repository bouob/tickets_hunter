# tixcraft_bot
maxbot(Max搶票機器人) help you quickly buy your tickets

# Download (搶票程式下載)
https://github.com/max32002/tixcraft_bot/releases

# Demo (示範影片)
https://youtu.be/U6xGBofx-O8

# How to use (如何使用)
https://max-everyday.com/2018/03/tixcraft-bot/
or
https://max-everyday.com/2018/12/kktix-bot/

# How to execute source code (透過原始碼的執行方法)
1: download chromedrive to "webdriver" folder:
http://chromedriver.chromium.org/downloads

change the chromedrive in chrome_tixcraft.py, source code:
<code>chromedriver_path =Root_Dir+ "webdriver/chromedriver"</code>
the default path is the script path + "webdriver/chromedriver", My suggestion is to create a new directory, then move the chromedrive under new folder.

2: <code>pip install selenium</code> or <code>pip3 install selenium</code>

3: <code>python settings.py</code> or <code>python3 settings.py</code>

PS1: this script able to run in python2 or python3. (原始碼可以在python2 或 python3 下執行。）

PS2: 請先確定你的python 執行環境下已安裝 selenium 或相關的套件，請參考 pip-reg.txt 檔案內容。

PS3: 請手動下載新版的 chromedrive, 建議在 source code 下建立一個 webdrive 的目錄，並把 chromedirve 的執行檔放進去。最後透過 python 或 python3 執行 settings.py 就可以有 GUI 的設定界面。)

# Introduce the implement (實作方法)
https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/

# Execute suggestion (搶票建議)
please run this source code with high performance hardware computer and high speed + stable network.

門票的「限量」是很殘酷的，建議不要用破舊的電腦或連線不穩的手機網路來搶票，因為只要比別人慢個 0.1 秒，票可能就沒了。為了要搶到限量的票真心建議去一下網咖或找一個網路連線穩定且快的地方並使用硬體不差的電腦來搶票。

# TODO about cpatcha (關於驗證碼)

目前驗證碼需要手動輸入，也許你會想自動輸入驗證碼，可以參考看看：實作基於CNN的台鐵訂票驗證碼辨識以及透過模仿及資料增強的訓練集產生器 (Simple captcha solver based on CNN and a training set generator by imitating the style of captcha and data augmentation)
https://github.com/JasonLiTW/simple-railway-captcha-solver

# Donate (贊助Max)

如果你覺得這篇文章或MaxBot寫的很好，想打賞Max，贊助方式如下： https://max-everyday.com/about/#donate
