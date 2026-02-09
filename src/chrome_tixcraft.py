#!/usr/bin/env python3
#encoding=utf-8
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
#import jieba
#from DrissionPage import ChromiumPage
#import nodriver as uc
import argparse
import base64
import json
import logging
import os
import platform
import random
import ssl
import subprocess
import sys
import threading
import time
import warnings
import webbrowser
from datetime import datetime

import chromedriver_autoinstaller_max
import requests
from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchWindowException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from urllib3.exceptions import InsecureRequestWarning

import util
from NonBrowser import NonBrowser

try:
    import ddddocr
except Exception as exc:
    print(exc)
    pass

# 強制使用 UTF-8 編碼輸出（解決 Windows CP950 編碼問題）
# 適用於所有輸出環境（終端、IDE、重定向、管道）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

CONST_APP_VERSION = "TicketsHunter (2026.02.09)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"
CONST_MAXBLOCK_EXTENSION_NAME = "Maxblockplus_1.0.0"
CONST_MAXBLOCK_EXTENSION_FILTER =[
"*.doubleclick.net/*",
"*.googlesyndication.com/*",
"*.ssp.hinet.net/*",
"*a.amnet.tw/*",
"*anymind360.com/*",
"*.appier.net/*",
"*.c.appier.net/*",
"*cdn.cookielaw.org/*",
"*cdnjs.cloudflare.com/ajax/libs/clipboard.js/*",
"*clarity.ms/*",
"*cloudfront.com/*",
"*cms.analytics.yahoo.com/*",
"*e2elog.fetnet.net/*",
"*fundingchoicesmessages.google.com/*",
"*ghtinc.com/*",
"*google-analytics.com/*",
"*googletagmanager.com/*",
"*googletagservices.com/*",
"*img.uniicreative.com/*",
"*lndata.com/*",
"*match.adsrvr.org/*",
"*onead.onevision.com.tw/*",
"*play.google.com/log?*",
"*popin.cc/*",
"*rollbar.com/*",
"*sb.scorecardresearch.com/*",
"*tagtoo.co/*",
"*ticketmaster.com/js/ads.js*",
"*ticketmaster.com/epsf/asset/eps.js*",
"*ticketmaster.sg/js/adblock.js*",
"*ticketmaster.sg/js/ads.js*",
"*ticketmaster.sg/epsf/asset/eps.js*",
"*tixcraft.com/js/analytics.js*",
"*tixcraft.com/js/common.js*",
"*tixcraft.com/js/custom.js*",
"*treasuredata.com/*",
"*www.youtube.com/youtubei/v1/player/heartbeat*",
]

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"
CONST_CHROME_DRIVER_WEBSITE = 'https://chromedriver.chromium.org/'

CONST_CITYLINE_SIGN_IN_URL = "https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2Fwww.cityline.com%2FEvents.html"
CONST_FAMI_SIGN_IN_URL = "https://www.famiticket.com.tw/Home/User/SignIn"
CONST_HKTICKETING_SIGN_IN_URL = "https://premier.hkticketing.com/Secure/ShowLogin.aspx"
CONST_KHAM_SIGN_IN_URL = "https://kham.com.tw/application/UTK13/UTK1306_.aspx"
CONST_KKTIX_SIGN_IN_URL = "https://kktix.com/users/sign_in?back_to=%s"
CONST_TICKET_SIGN_IN_URL = "https://ticket.com.tw/application/utk13/utk1306_.aspx"
CONST_URBTIX_SIGN_IN_URL = "https://www.urbtix.hk/member-login"

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"

CONT_STRING_1_SEATS_REMAINING = ['@1 seat(s) remaining','剩餘 1@','@1 席残り']

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_DP = "DrissionPage"
CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"
CONST_CHROME_FAMILY = ["chrome","edge","brave"]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
CONST_PREFS_DICT = {
    "credentials_enable_service": False, 
    "in_product_help.snoozed_feature.IPH_LiveCaption.is_dismissed": True,
    "in_product_help.snoozed_feature.IPH_LiveCaption.last_dismissed_by": 4,
    "media_router.show_cast_sessions_started_by_other_devices.enabled": False,
    "net.network_prediction_options": 3,
    "privacy_guide.viewed": True,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.sound": 2,
    "profile.name": CONST_APP_VERSION, 
    "profile.password_manager_enabled": False, 
    "safebrowsing.enabled":False,
    "safebrowsing.enhanced":False,
    "sync.autofill_wallet_import_enabled_migrated":False,
    "translate":{"enabled": False}}

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig()
logger = logging.getLogger('logger')

def get_config_dict(args):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    # allow assign config by command line.
    if args.input:
        config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        # start to overwrite config settings.
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

            if args.headless is not None:
                config_dict["advanced"]["headless"] = util.t_or_f(args.headless)

            if args.homepage:
                config_dict["homepage"] = args.homepage

            if args.ticket_number:
                config_dict["ticket_number"] = args.ticket_number

            if args.browser:
                config_dict["browser"] = args.browser

            if args.tixcraft_sid:
                config_dict["accounts"]["tixcraft_sid"] = args.tixcraft_sid

            if args.ibonqware:
                config_dict["accounts"]["ibonqware"] = args.ibonqware

            if args.kktix_account:
                config_dict["accounts"]["kktix_account"] = args.kktix_account
            if args.kktix_password:
                config_dict["accounts"]["kktix_password"] = args.kktix_password

            if args.proxy_server:
                config_dict["advanced"]["proxy_server_port"] = args.proxy_server

            if args.window_size:
                config_dict["advanced"]["window_size"] = args.window_size

            # special case for headless to enable away from keyboard mode.
            is_headless_enable_ocr = False
            if config_dict["advanced"]["headless"]:
                # for tixcraft headless.
                #print("If you are runnig headless mode on tixcraft, you need input your cookie SID.")
                if len(config_dict["accounts"]["tixcraft_sid"]) > 1:
                    is_headless_enable_ocr = True

            if is_headless_enable_ocr:
                config_dict["ocr_captcha"]["enable"] = True
                config_dict["ocr_captcha"]["force_submit"] = True

    return config_dict

def write_question_to_file(question_text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_QUESTION_FILE)
    util.write_string_to_file(target_path, question_text)

def write_last_url_to_file(url):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_LAST_URL_FILE)
    util.write_string_to_file(target_path, url)

def read_last_url_from_file():
    ret = ""
    with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
        ret = text_file.readline()
    return ret

def get_favoriate_extension_path(webdriver_path, config_dict):
    #print("webdriver_path:", webdriver_path)
    extension_list = []
    extension_list.append(os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME + ".crx"))
    extension_list.append(os.path.join(webdriver_path, CONST_MAXBLOCK_EXTENSION_NAME + ".crx"))
    return extension_list

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, config_dict):
    chrome_options = webdriver.ChromeOptions()
    if config_dict["browser"]=="edge":
        chrome_options = webdriver.EdgeOptions()
    if config_dict["browser"]=="safari":
        chrome_options = webdriver.SafariOptions()

    is_log_performace = False
    performace_site = ['ticketplus']
    for site in performace_site:
        if site in config_dict["homepage"]:
            is_log_performace = True
            break

    if is_log_performace:
        if config_dict["browser"] in CONST_CHROME_FAMILY:
            chrome_options.set_capability("goog:loggingPrefs",{"performance": "ALL"})

    # PS: this is crx version.
    extension_list = []
    if config_dict["advanced"]["chrome_extension"]:
        extension_list = get_favoriate_extension_path(webdriver_path, config_dict)
    for ext in extension_list:
        if os.path.exists(ext):
            chrome_options.add_extension(ext)

    if config_dict["advanced"]["headless"]:
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')

    chrome_options.add_argument("--user-agent=%s" % (USER_AGENT))
    chrome_options.add_argument("--disable-animations")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-bookmark-reordering")
    chrome_options.add_argument("--disable-boot-animation")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-canvas-aa")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-cloud-import")
    chrome_options.add_argument("--disable-component-cloud-policy")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-composited-antialiasing")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-device-discovery-notifications")
    chrome_options.add_argument("--disable-dinosaur-easter-egg")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process,TranslateUI,PrivacySandboxSettings4")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-login-animations")
    chrome_options.add_argument("--disable-login-screen-apps")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-print-preview")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-session-crashed-bubble")
    chrome_options.add_argument("--disable-smooth-scrolling")
    chrome_options.add_argument("--disable-suggestions-ui")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--hide-crash-restore-bubble")
    chrome_options.add_argument("--lang=zh-TW")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-pings")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--no-service-autorun")
    chrome_options.add_argument("--password-store=basic")

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", CONST_PREFS_DICT)

    if len(config_dict["advanced"]["proxy_server_port"]) > 2:
        chrome_options.add_argument('--proxy-server=%s' % config_dict["advanced"]["proxy_server_port"])

    if config_dict["browser"]=="brave":
        brave_path = util.get_brave_bin_path()
        if os.path.exists(brave_path):
            chrome_options.binary_location = brave_path

    chrome_options.page_load_strategy = 'eager'
    #chrome_options.page_load_strategy = 'none'
    chrome_options.unhandled_prompt_behavior = "accept"

    return chrome_options

def load_chromdriver_normal(config_dict, driver_type):
    show_debug_message = config_dict["advanced"]["verbose"]

    driver = None

    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    os.makedirs(webdriver_path, exist_ok=True)

    if not os.path.exists(chromedriver_path):
        print("WebDriver not exist, try to download to:", webdriver_path)
        chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)

    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(CONST_CHROME_DRIVER_WEBSITE)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict)
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        except WebDriverException as exc:
            error_message = str(exc)
            if show_debug_message:
                print(exc)
            left_part = error_message.split("Stacktrace:")[0] if "Stacktrace:" in error_message else None
            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

                # remove exist chromedriver, download again.
                try:
                    print("Deleting exist and download ChromeDriver again.")
                    os.unlink(chromedriver_path)
                except Exception as exc2:
                    print(exc2)
                    pass

                chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)
                chrome_service = Service(chromedriver_path)
                try:
                    chrome_options = get_chrome_options(webdriver_path, config_dict)
                    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                except WebDriverException as exc2:
                    print("Selenium 4.11.0 Release with Chrome For Testing Browser.")
                    try:
                        chrome_options = get_chrome_options(webdriver_path, config_dict)
                        driver = webdriver.Chrome(service=Service(), options=chrome_options)
                    except WebDriverException as exc3:
                        print(exc3)
                        pass

    return driver


def get_uc_options(uc, config_dict, webdriver_path):
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    #options.page_load_strategy = 'none'
    options.unhandled_prompt_behavior = "accept"
    #print("strategy", options.page_load_strategy)

    is_log_performace = False
    performace_site = ['ticketplus']
    for site in performace_site:
        if site in config_dict["homepage"]:
            is_log_performace = True
            break

    if is_log_performace:
        options.set_capability("goog:loggingPrefs",{"performance": "ALL"})

    load_extension_path = ""
    extension_list = []
    if config_dict["advanced"]["chrome_extension"]:
        extension_list = get_favoriate_extension_path(webdriver_path, config_dict)
    for ext in extension_list:
        ext = ext.replace('.crx','')
        if os.path.exists(ext):
            # sync config.
            if CONST_MAXBOT_EXTENSION_NAME in ext:
                util.dump_settings_to_maxbot_plus_extension(ext, config_dict, CONST_MAXBOT_CONFIG_FILE)
            if CONST_MAXBLOCK_EXTENSION_NAME in ext:
                util.dump_settings_to_maxblock_plus_extension(ext, config_dict, CONST_MAXBOT_CONFIG_FILE, CONST_MAXBLOCK_EXTENSION_FILTER)
            load_extension_path += ("," + os.path.abspath(ext))
            #print("load_extension_path:", load_extension_path)

    if len(load_extension_path) > 0:
        #print('load-extension:', load_extension_path[1:])
        options.add_argument('--load-extension=' + load_extension_path[1:])

    if config_dict["advanced"]["headless"]:
        #options.add_argument('--headless')
        options.add_argument('--headless=new')

    options.add_argument("--user-agent=%s" % (USER_AGENT))
    options.add_argument("--disable-animations")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-bookmark-reordering")
    options.add_argument("--disable-boot-animation")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-canvas-aa")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-cloud-import")
    options.add_argument("--disable-component-cloud-policy")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-composited-antialiasing")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-device-discovery-notifications")
    options.add_argument("--disable-dinosaur-easter-egg")
    options.add_argument("--disable-domain-reliability")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process,TranslateUI,PrivacySandboxSettings4")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-login-animations")
    options.add_argument("--disable-login-screen-apps")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-print-preview")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--disable-smooth-scrolling")
    options.add_argument("--disable-suggestions-ui")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")
    options.add_argument("--hide-crash-restore-bubble")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--no-pings")
    options.add_argument("--no-sandbox")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", CONST_PREFS_DICT)

    if len(config_dict["advanced"]["proxy_server_port"]) > 2:
        options.add_argument('--proxy-server=%s' % config_dict["advanced"]["proxy_server_port"])

    if config_dict["browser"]=="brave":
        brave_path = util.get_brave_bin_path()
        if os.path.exists(brave_path):
            options.binary_location = brave_path

    return options

def load_chromdriver_uc(config_dict):
    import undetected_chromedriver as uc

    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not exist, try to download to:", webdriver_path)
        try:
            chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)
            if not os.path.exists(chromedriver_path):
                print("check installed chrome version fail, download last known good version.")
                chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False, detect_installed_version=False)
        except Exception as exc:
            print(exc)
    else:
        print("ChromeDriver exist:", chromedriver_path)

    driver = None
    if os.path.exists(chromedriver_path):
        # use chromedriver_autodownload instead of uc auto download.
        is_cache_exist =  util.clean_uc_exe_cache()

        fail_1 = False
        lanch_uc_with_path = True
        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                lanch_uc_with_path = False

        if lanch_uc_with_path:
            try:
                options = get_uc_options(uc, config_dict, webdriver_path)
                driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
            except Exception as exc:
                print(exc)
                error_message = str(exc)
                left_part = None
                if "Stacktrace:" in error_message:
                    left_part = error_message.split("Stacktrace:")[0]
                    print(left_part)

                if "This version of ChromeDriver only supports Chrome version" in error_message:
                    print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                    print(CONST_CHROME_VERSION_NOT_MATCH_TW)
                fail_1 = True
        else:
            fail_1 = True

        fail_2 = False
        if fail_1:
            try:
                options = get_uc_options(uc, config_dict, webdriver_path)
                driver = uc.Chrome(options=options)
            except Exception as exc:
                print(exc)
                fail_2 = True

        if fail_2:
            # remove exist chromedriver, download again.
            try:
                print("Deleting exist and download ChromeDriver again.")
                os.unlink(chromedriver_path)
            except Exception as exc2:
                print(exc2)
                pass

            try:
                chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)
                options = get_uc_options(uc, config_dict, webdriver_path)
                driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options)
            except Exception as exc2:
                print(exc2)
                pass
    else:
        print("WebDriver not found at path:", chromedriver_path)

    if driver is None:
        print('WebDriver object is still None..., try download by uc.')
        try:
            options = get_uc_options(uc, config_dict, webdriver_path)
            driver = uc.Chrome(options=options)
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(config_dict, driver_type)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver

def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict):
    driver = None

    # read config.
    homepage = config_dict["homepage"]

    # output config:
    print("current time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("maxbot app version:", CONST_APP_VERSION)
    print("python version:", platform.python_version())
    print("platform:", platform.platform())
    print("homepage:", homepage)
    print("browser:", config_dict["browser"])
    #print("headless:", config_dict["advanced"]["headless"])
    #print("ticket_number:", str(config_dict["ticket_number"]))

    #print(config_dict["tixcraft"])
    #print("==[advanced config]==")
    if config_dict["advanced"]["verbose"]:
        print(config_dict["advanced"])
    print("webdriver_type:", config_dict["webdriver_type"])

    # entry point
    if homepage is None:
        homepage = ""

    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    #print("platform.system().lower():", platform.system().lower())

    if config_dict["browser"] in ["chrome","brave"]:
        # method 6: Selenium Stealth
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_SELENIUM:
            driver = load_chromdriver_normal(config_dict, config_dict["webdriver_type"])
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_UC:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(config_dict)
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_DP:
            #driver = ChromiumPage()
            pass

    if config_dict["browser"] == "firefox":
        # default os is linux/mac
        # download url: https://github.com/mozilla/geckodriver/releases
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")

        webdriver_service = Service(chromedriver_path)
        driver = None
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if config_dict["advanced"]["headless"]:
                options.add_argument('--headless')
                #options.add_argument('--headless=new')
            if platform.system().lower()=="windows":
                binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = os.path.expanduser('~') + "\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"
                options.binary_location = binary_path

            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)
            else:
                print(exc)

    if config_dict["browser"] == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict)

        driver = None
        try:
            driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if config_dict["browser"] == "safari":
        driver = None
        try:
            driver = webdriver.Safari()
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            NETWORK_BLOCKED_URLS = [
                '*.clarity.ms/*',
                '*.cloudfront.com/*',
                '*.doubleclick.net/*',
                '*.lndata.com/*',
                '*.rollbar.com/*',
                '*.twitter.com/i/*',
                '*/adblock.js',
                '*/google_ad_block.js',
                # '*cityline.com/js/others.min.js',  # DISABLED: Required for buy button rendering
                '*anymind360.com/*',
                '*cdn.cookielaw.org/*',
                '*e2elog.fetnet.net*',
                '*fundingchoicesmessages.google.com/*',
                '*google-analytics.*',
                '*googlesyndication.*',
                '*googletagmanager.*',
                '*googletagservices.*',
                '*img.uniicreative.com/*',
                '*platform.twitter.com/*',
                '*play.google.com/*',
                '*player.youku.*',
                '*syndication.twitter.com/*',
                '*youtube.com/*',
                # Ticketmaster ad and tracking scripts
                '*ticketmaster.sg/js/adblock*',
                '*ticketmaster.sg/js/ads.js*',
                '*ticketmaster.sg/epsf/asset/eps.js*',
                '*ticketmaster.com/js/ads.js*',
                '*ticketmaster.com/epsf/asset/eps.js*',
            ]

            if config_dict["advanced"]["hide_some_image"]:
                NETWORK_BLOCKED_URLS.append('*.woff')
                NETWORK_BLOCKED_URLS.append('*.woff2')
                NETWORK_BLOCKED_URLS.append('*.ttf')
                NETWORK_BLOCKED_URLS.append('*.otf')
                NETWORK_BLOCKED_URLS.append('*fonts.googleapis.com/earlyaccess/*')
                NETWORK_BLOCKED_URLS.append('*/ajax/libs/font-awesome/*')
                NETWORK_BLOCKED_URLS.append('*.ico')
                NETWORK_BLOCKED_URLS.append('*ticketimg2.azureedge.net/image/ActivityImage/*')
                NETWORK_BLOCKED_URLS.append('*static.tixcraft.com/images/activity/*')
                NETWORK_BLOCKED_URLS.append('*static.ticketmaster.sg/images/activity/*')
                NETWORK_BLOCKED_URLS.append('*static.ticketmaster.com/images/activity/*')
                NETWORK_BLOCKED_URLS.append('*ticketimg2.azureedge.net/image/ActivityImage/ActivityImage_*')
                NETWORK_BLOCKED_URLS.append('*.azureedge.net/QWARE_TICKET//images/*')
                NETWORK_BLOCKED_URLS.append('*static.ticketplus.com.tw/event/*')

                #NETWORK_BLOCKED_URLS.append('https://kktix.cc/change_locale?locale=*')
                NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/logo_*.png')
                NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/icon-*.png')
                NETWORK_BLOCKED_URLS.append('https://t.kfs.io/upload_images/*.jpg')

            if config_dict["advanced"]["block_facebook_network"]:
                NETWORK_BLOCKED_URLS.append('*facebook.com/*')
                NETWORK_BLOCKED_URLS.append('*.fbcdn.net/*')

            # Chrome DevTools Protocal
            if config_dict["browser"] in CONST_CHROME_FAMILY:
                driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": NETWORK_BLOCKED_URLS})
                driver.execute_cdp_cmd('Network.enable', {})

            if 'kktix.c' in homepage:
                if len(config_dict["accounts"]["kktix_account"])>0:
                    # for like human.
                    try:
                        driver.get(homepage)
                        time.sleep(5)
                    except Exception as e:
                        pass
                    if not 'https://kktix.com/users/sign_in?' in homepage:
                        homepage = CONST_KKTIX_SIGN_IN_URL % (homepage)

            if 'famiticket.com' in homepage:
                if len(config_dict["accounts"]["fami_account"])>0:
                    homepage = CONST_FAMI_SIGN_IN_URL

            if 'kham.com' in homepage:
                if len(config_dict["accounts"]["kham_account"])>0:
                    homepage = CONST_KHAM_SIGN_IN_URL

            if 'ticket.com.tw' in homepage:
                if len(config_dict["accounts"]["ticket_account"])>0:
                    homepage = CONST_TICKET_SIGN_IN_URL

            if 'urbtix.hk' in homepage:
                if len(config_dict["accounts"]["urbtix_account"])>0:
                    homepage = CONST_URBTIX_SIGN_IN_URL

            if 'cityline.com' in homepage:
                if len(config_dict["accounts"]["cityline_account"])>0:
                    homepage = CONST_CITYLINE_SIGN_IN_URL

            if 'hkticketing.com' in homepage:
                if len(config_dict["accounts"]["hkticketing_account"])>0:
                    homepage = CONST_HKTICKETING_SIGN_IN_URL

            if 'ticketplus.com.tw' in homepage:
                if len(config_dict["accounts"]["ticketplus_account"]) > 1:
                    homepage = "https://ticketplus.com.tw/"

            print("goto url:", homepage)
            driver.get(homepage)
            time.sleep(3.0)

            tixcraft_family = False
            if 'tixcraft.com' in homepage:
                tixcraft_family = True

            if 'indievox.com' in homepage:
                tixcraft_family = True

            if 'ticketmaster.' in homepage:
                tixcraft_family = True

            if tixcraft_family:
                tixcraft_sid = config_dict["accounts"]["tixcraft_sid"]
                if len(tixcraft_sid) > 1:
                    driver.delete_cookie("TIXUISID")
                    driver.add_cookie({"name":"TIXUISID", "value": tixcraft_sid, "path" : "/", "secure":True})

            if 'ibon.com' in homepage:
                ibonqware = config_dict["accounts"]["ibonqware"]
                if len(ibonqware) > 1:
                    if config_dict["advanced"]["verbose"]:
                        print(f"Setting ibon cookie with length: {len(ibonqware)}")
                        print(f"Cookie contains mem_id: {'mem_id=' in ibonqware}")
                        print(f"Cookie contains mem_email: {'mem_email=' in ibonqware}")
                        print(f"Cookie contains huiwanTK: {'huiwanTK=' in ibonqware}")
                        print(f"Cookie contains ibonqwareverify: {'ibonqwareverify=' in ibonqware}")

                    try:
                        # Delete existing cookie
                        driver.delete_cookie("ibonqware")

                        # Add new cookie with proper domain setting
                        cookie_dict = {
                            "name": "ibonqware",
                            "value": ibonqware,
                            "domain": ".ibon.com.tw",  # Use .ibon.com.tw for broader domain coverage
                            "path": "/",
                            "secure": True,
                            "httpOnly": False
                        }
                        driver.add_cookie(cookie_dict)

                        if config_dict["advanced"]["verbose"]:
                            print("ibon cookie set successfully")
                            # Verify cookie was set
                            cookies = driver.get_cookies()
                            ibon_cookies = [c for c in cookies if c.get('name') == 'ibonqware']
                            if ibon_cookies:
                                print(f"Verified: ibon cookie exists with value length: {len(ibon_cookies[0].get('value', ''))}")
                                print(f"Cookie domain: {ibon_cookies[0].get('domain', 'N/A')}")
                                print(f"Cookie path: {ibon_cookies[0].get('path', 'N/A')}")
                                print(f"Cookie secure: {ibon_cookies[0].get('secure', 'N/A')}")
                            else:
                                print("Warning: ibon cookie not found after setting")

                        # Reload page to apply cookie
                        if config_dict["advanced"]["verbose"]:
                            print("Reloading page to apply ibon cookie...")
                        driver.refresh()
                        time.sleep(3)

                        # Check login status after setting cookie
                        if config_dict["advanced"]["verbose"]:
                            login_status = check_ibon_login_status(driver, config_dict)
                            if login_status:
                                print("✅ ibon auto-login appears successful")
                            else:
                                print("❌ ibon auto-login may have failed - manual login may be required")
                                print("💡 Try refreshing the page manually or check if cookie has expired")
                    except Exception as cookie_error:
                        print(f"Failed to set ibon cookie: {cookie_error}")
                        if config_dict["advanced"]["verbose"]:
                            import traceback
                            traceback.print_exc()

        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exce1)
            pass

    return driver


def force_press_button_iframe(driver, f, select_by, select_query, force_submit=True):
    if not f:
        # ensure we are on main content frame
        try:
            driver.switch_to.default_content()
        except Exception as exc:
            pass
    else:
        try:
            driver.switch_to.frame(f)
        except Exception as exc:
            pass

    is_clicked = press_button(driver, select_by, select_query, force_submit)

    if f:
        # switch back to main content, otherwise we will get StaleElementReferenceException
        try:
            driver.switch_to.default_content()
        except Exception as exc:
            pass

    return is_clicked

def remove_attribute_tag_by_selector(driver, select_query, class_name, more_script = ""):
    element_script = "eachItem.removeAttribute('"+ class_name +"');"
    javascript_tag_by_selector(driver, select_query, element_script, more_script = more_script)

def remove_class_tag_by_selector(driver, select_query, class_name, more_script = ""):
    element_script = "eachItem.classList.remove('"+ class_name +"');"
    javascript_tag_by_selector(driver, select_query, element_script, more_script = more_script)

def hide_tag_by_selector(driver, select_query, more_script = ""):
    element_script = "eachItem.style='display:none;';"
    javascript_tag_by_selector(driver, select_query, element_script, more_script = more_script)

def clean_tag_by_selector(driver, select_query, more_script = ""):
    element_script = "eachItem.outerHTML='';"
    javascript_tag_by_selector(driver, select_query, element_script, more_script = more_script)

# PS: selector query string must without single quota.
def javascript_tag_by_selector(driver, select_query, element_script, more_script = ""):
    try:
        driver.set_script_timeout(1)
        js = """var selectSoldoutItems = document.querySelectorAll('%s');
selectSoldoutItems.forEach((eachItem) =>
{%s});
%s""" % (select_query, element_script, more_script)

        #print("javascript:", js)
        driver.execute_script(js)
        ret = True
    except Exception as exc:
        #print(exc)
        pass

def press_button(driver, select_by, select_query, force_submit=True):
    ret = False
    next_step_button = None
    try:
        next_step_button = driver.find_element(select_by ,select_query)
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        #print("find %s clickable Exception:" % (select_query))
        #print(exc)
        pass

        if force_submit:
            if not next_step_button is None:
                is_visible = False
                try:
                    if next_step_button.is_enabled():
                        is_visible = True
                except Exception as exc:
                    pass

                if is_visible:
                    try:
                        driver.set_script_timeout(1)
                        driver.execute_script("arguments[0].click();", next_step_button)
                        ret = True
                    except Exception as exc:
                        pass
    return ret

# close some div on home url.
def tixcraft_home_close_window(driver):
    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
        if accept_all_cookies_btn:
            accept_all_cookies_btn.click()
    except Exception as exc:
        #print(exc)
        pass

# from detail to game
def tixcraft_redirect(driver, url):
    ret = False
    game_name = ""
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]
    if len(game_name) > 0:
        if "/activity/detail/%s" % (game_name,) in url:
            entry_url = url.replace("/activity/detail/","/activity/game/")
            print("redirec to new url:", entry_url)
            try:
                driver.get(entry_url)
                ret = True
            except Exception as exec1:
                pass
    return ret


def tixcraft_date_auto_select(driver, url, config_dict, domain_name):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    # PS: "Start ordering" for indievox.com.
    find_ticket_text_list = ['立即訂購','Find tickets', 'Start ordering','お申込みへ進む']

    game_name = ""

    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if show_debug_message:
        print('get date game_name:', game_name)
        print("date_auto_select_mode:", auto_select_mode)
        print("date_keyword:", date_keyword)

    check_game_detail = False
    # choose date
    if "/activity/game/%s" % (game_name,) in url:
        if show_debug_message:
            if len(date_keyword) == 0:
                print("date keyword is empty.")
            else:
                print("date keyword:", date_keyword)
        check_game_detail = True

    area_list = None
    if check_game_detail:
        if show_debug_message:
            print("start to query #gameList info.")
        my_css_selector = '#gameList > table > tbody > tr'
        try:
            area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
            if not area_list is None:
                if len(area_list)==0:
                    # only headless mode detected now.
                    if config_dict["advanced"]["headless"]:
                        html_body = driver.page_source
                        if not html_body is None:
                            if len(html_body) > 0:
                                html_text = util.remove_html_tags(html_body)
                                bot_detected_string_list = ['Your Session Has Been Suspended'
                                , 'Something about your browsing behavior or network made us think you were a bot'
                                , 'Your browser hit a snag and we need to make sure you'
                                ]
                                for each_string in bot_detected_string_list:
                                    print(html_text)
                                    break
        except Exception as exc:
            print("find #gameList fail")

    is_coming_soon = False
    coming_soon_condictions_list_en = [' day(s)', ' hrs.',' min',' sec',' till sale starts!','0',':','/']
    coming_soon_condictions_list_tw = ['開賣','剩餘',' 天',' 小時',' 分鐘',' 秒','0',':','/','20']
    coming_soon_condictions_list_ja = ['発売開始', ' 日', ' 時間',' 分',' 秒','0',':','/','20']
    coming_soon_condictions_list = coming_soon_condictions_list_en
    html_lang="en-US"
    try:
        html_body = driver.page_source
        if not html_body is None:
            if len(html_body) > 0:
                if '<head' in html_body:
                    html = html_body.split("<head")[0]
                    html_lang = html.split('"')[1]
                    if show_debug_message:
                        print("html lang:" , html_lang)
                    if html_lang == "zh-TW":
                        coming_soon_condictions_list = coming_soon_condictions_list_tw
                    if html_lang == "ja":
                        coming_soon_condictions_list = coming_soon_condictions_list_ja
    except Exception as e:
        pass

    matched_blocks = None
    formated_area_list = None

    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:

                    # check is coming soon events in list.
                    is_match_all_coming_soon_condiction = True
                    for condiction_string in coming_soon_condictions_list:
                        if not condiction_string in row_text:
                            is_match_all_coming_soon_condiction = False
                            break

                    if is_match_all_coming_soon_condiction:
                        if show_debug_message:
                            print("match coming soon condiction at row:", row_text)
                        is_coming_soon = True

                    if is_coming_soon:
                        if auto_reload_coming_soon_page_enable:
                            break

                    row_is_enabled=False
                    for text_item in find_ticket_text_list:
                        if text_item in row_text:
                            row_is_enabled = True
                            break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                row_text_right_part = row_text[(len(sold_out_item)+5)*-1:]
                                if show_debug_message:
                                    #print("check right part text:", row_text_right_part)
                                    pass
                                if sold_out_item in row_text_right_part:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                    if row_is_enabled:
                        formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    is_date_clicked = False
    if not target_area is None:
        if show_debug_message:
            print("target_area got, start to press button.")

        is_date_clicked = press_button(target_area, By.CSS_SELECTOR,'button')
        if not is_date_clicked:
            if show_debug_message:
                print("press button fail, try to click hyperlink.")

            if "tixcraft" in domain_name:
                try:
                    data_href = target_area.get_attribute("data-href")
                    if not data_href is None:
                        print("goto url:", data_href)
                        driver.get(data_href)
                    else:
                        if show_debug_message:
                            print("data-href not ready")

                        # delay 200ms to click.
                        #driver.set_script_timeout(0.3)
                        #js="""setTimeout(function(){arguments[0].click()},200);"""
                        #driver.execute_script(js, target_area)
                except Exception as exc:
                    pass


            # for: ticketmaster.sg
            is_date_clicked = press_button(target_area, By.CSS_SELECTOR,'a')

    # [PS]: current reload condition only when
    if auto_reload_coming_soon_page_enable:
        if is_coming_soon:
            if show_debug_message:
                print("match is_coming_soon, start to reload page.")

            # case 2: match one row is coming soon.
            try:
                driver.refresh()
            except Exception as exc:
                pass
        else:
            if not is_date_clicked:
                if not formated_area_list is None:
                    if len(formated_area_list) == 0:
                        print('start to refresh page.')
                        try:
                            driver.refresh()
                            time.sleep(0.3)
                        except Exception as exc:
                            pass

                        if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_date_clicked

def ticketmaster_date_auto_select(driver, url, config_dict, domain_name):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    # TODO: implement this feature.
    date_keyword_and = ""
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    find_ticket_text_list = ['See Tickets']

    area_list = None
    try:
        area_list = driver.find_elements(By.CSS_SELECTOR, '#list-view > div > div.event-listing > div.accordion-wrapper > div')
    except Exception as exc:
        print("find #gameList fail")

    matched_blocks = None
    formated_area_list = None

    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    row_is_enabled=False
                    # must contains 'See Tickets'
                    for text_item in find_ticket_text_list:
                        if text_item in row_text:
                            row_is_enabled = True
                            break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                if sold_out_item in row_text:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                    if row_is_enabled:
                        formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                date_keyword = util.format_keyword_string(date_keyword)
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    is_date_clicked = False
    if not target_area is None:
        is_date_clicked = press_button(target_area, By.CSS_SELECTOR,'a')
        if is_date_clicked:
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count > 1:
                    driver.switch_to.window(driver.window_handles[0])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(0.2)
            except Exception as excSwithFail:
                pass


    # [PS]: current reload condition only when
    if auto_reload_coming_soon_page_enable:
        if not is_date_clicked:
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    print('start to refresh page.')
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

    return is_date_clicked


# PURPOSE: get target area list.
# RETURN:
#   is_need_refresh
#   matched_blocks
# PS: matched_blocks will be None, if length equals zero.
def get_tixcraft_target_area(el, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_need_refresh = False
    matched_blocks = None

    area_list = None
    area_list_count = 0
    if not el is None:
        try:
            area_list = el.find_elements(By.TAG_NAME, 'a')
        except Exception as exc:
            #print("find area list a tag fail")
            pass

        if not area_list is None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                print("area list is empty, do refresh!")
                is_need_refresh = True
        else:
            print("area list is None, do refresh!")
            is_need_refresh = True

    if area_list_count > 0:
        matched_blocks = []
        for row in area_list:
            row_text = ""
            row_html = ""
            try:
                #row_text = row.text
                row_html = row.get_attribute('innerHTML')
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                # error, exit loop
                break

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = util.format_keyword_string(row_text)

                is_append_this_row = False

                if len(area_keyword_item) > 0:
                    # must match keyword.
                    is_append_this_row = True
                    area_keyword_array = area_keyword_item.split(' ')
                    for area_keyword in area_keyword_array:
                        area_keyword = util.format_keyword_string(area_keyword)
                        if not area_keyword in row_text:
                            is_append_this_row = False
                            break
                else:
                    # without keyword.
                    is_append_this_row = True

                if is_append_this_row:
                    if config_dict["ticket_number"] > 1:
                        area_item_font_el = None
                        try:
                            #print('try to find font tag at row:', row_text)
                            area_item_font_el = row.find_element(By.TAG_NAME, 'font')
                            if not area_item_font_el is None:
                                font_el_text = area_item_font_el.text
                                if font_el_text is None:
                                    font_el_text = ""
                                font_el_text = "@%s@" % (font_el_text)
                                if show_debug_message:
                                    print('font tag text:', font_el_text)
                                    pass
                                for check_item in CONT_STRING_1_SEATS_REMAINING:
                                    if check_item in font_el_text:
                                        if show_debug_message:
                                            print("match pass 1 seats remaining 1 full text:", row_text)
                                            print("match pass 1 seats remaining 2 font text:", font_el_text)
                                        is_append_this_row = False
                            else:
                                #print("row withou font tag.")
                                pass
                        except Exception as exc:
                            #print("find font text in a tag fail:", exc)
                            pass

                if show_debug_message:
                    print("is_append_this_row:", is_append_this_row)

                if is_append_this_row:
                    matched_blocks.append(row)

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        #print("only need first item, break area list loop.")
                        break

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True

    return is_need_refresh, matched_blocks


def get_ticketmaster_target_area(config_dict, area_keyword_item, zone_info):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_need_refresh = False
    matched_blocks = None

    area_list_count = len(zone_info)
    if show_debug_message:
        print("area_list_count:", area_list_count)
    if area_list_count > 0:
        matched_blocks = []
        for row in zone_info:
            row_is_enabled=False

            if zone_info[row]["areaStatus"] != "UNAVAILABLE":
                row_is_enabled = True

            row_text = ""
            if row_is_enabled:
                try:
                    row_text = zone_info[row]["groupName"]
                    row_text += " " + zone_info[row]["description"]
                    if "price" in zone_info[row]:
                        row_text += " " + zone_info[row]["price"][0]["ticketPrice"]
                except Exception as exc:
                    if show_debug_message:
                        print("get text fail:", exc, zone_info[row])
                    pass

            if row_text is None:
                row_text = ""

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = util.format_keyword_string(row_text)
                if show_debug_message:
                    #print("formated row_text:", row_text)
                    pass

                is_append_this_row = False

                if len(area_keyword_item) > 0:
                    # must match keyword.
                    is_append_this_row = True
                    area_keyword_array = area_keyword_item.split(' ')
                    for area_keyword in area_keyword_array:
                        area_keyword = util.format_keyword_string(area_keyword)
                        if not area_keyword in row_text:
                            is_append_this_row = False
                            break
                else:
                    # without keyword.
                    is_append_this_row = True

                if show_debug_message:
                    #print("is_append_this_row:", is_append_this_row)
                    pass

                if is_append_this_row:
                    matched_blocks.append(row)

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        #print("only need first item, break area list loop.")
                        break

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True

    return is_need_refresh, matched_blocks

# PS: auto refresh condition 1: no keyword + no hyperlink.
# PS: auto refresh condition 2: with keyword + no hyperlink.
def tixcraft_area_auto_select(driver, url, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    ticket_number = config_dict["ticket_number"]

    if show_debug_message:
        print("area_keyword:", area_keyword)

    el = None
    try:
        el = driver.find_element(By.CSS_SELECTOR, '.zone')
    except Exception as exc:
        print("find .zone fail, do nothing.")

    if not el is None:
        is_need_refresh = False
        matched_blocks = None

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []
            for area_keyword_item in area_keyword_array:
                is_need_refresh, matched_blocks = get_tixcraft_target_area(el, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, matched_blocks = get_tixcraft_target_area(el, config_dict, "")

        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
        if not target_area is None:
            try:
                target_area.click()
            except Exception as exc:
                print("click area a link fail, start to retry...")
                try:
                    driver.execute_script("arguments[0].click();", target_area)
                except Exception as exc:
                    print("click area a link fail, after reftry still fail.")
                    print(exc)
                    pass

        # auto refresh for area list page.
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

def ticketmaster_area_auto_select(driver, config_dict, zone_info):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    if show_debug_message:
        print("area_keyword:", area_keyword)

    is_need_refresh = False
    matched_blocks = None

    if len(area_keyword) > 0:
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []
        for area_keyword_item in area_keyword_array:
            is_need_refresh, matched_blocks = get_ticketmaster_target_area(config_dict, area_keyword_item, zone_info)
            if not is_need_refresh:
                break
            else:
                print("is_need_refresh for keyword:", area_keyword_item)
    else:
        # empty keyword, match all.
        is_need_refresh, matched_blocks = get_ticketmaster_target_area(config_dict, "", zone_info)

    auto_select_mode = config_dict["area_auto_select"]["mode"]
    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            #print("area text:", target_area.text)
            click_area_javascript = 'areaTicket("%s", "map");' % target_area
            if show_debug_message:
                #print("click_area_javascript:", click_area_javascript)
                pass
            driver.execute_script(click_area_javascript)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    # auto refresh for area list page.
    if is_need_refresh:
        try:
            driver.refresh()
        except Exception as exc:
            pass

        if config_dict["advanced"]["auto_reload_page_interval"] > 0:
            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

def ticket_number_select_fill(driver, select_obj, ticket_number):
    is_ticket_number_assigned = False
    if not select_obj is None:
        try:
            # target ticket number
            select_obj.select_by_visible_text(ticket_number)
            #select.select_by_value(ticket_number)
            #select.select_by_index(int(ticket_number))
            is_ticket_number_assigned = True
        except Exception as exc:
            print("select_by_visible_text ticket_number fail")
            print(exc)

            try:
                # target ticket number
                select_obj.select_by_visible_text(ticket_number)
                #select.select_by_value(ticket_number)
                #select.select_by_index(int(ticket_number))
                is_ticket_number_assigned = True
            except Exception as exc:
                print("select_by_visible_text ticket_number fail...2")
                print(exc)

                # try buy one ticket
                try:
                    select_obj.select_by_visible_text("1")
                    #select.select_by_value("1")
                    #select.select_by_index(int(ticket_number))
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("select_by_visible_text 1 fail")
                    pass

    # Plan B.
    # if not is_ticket_number_assigned:
    if False:
        if not select is None:
            try:
                # target ticket number
                #select.select_by_visible_text(ticket_number)
                print("assign ticker number by jQuery:",ticket_number)
                driver.execute_script("$(\"input[type='select']\").val(\""+ ticket_number +"\");")
                is_ticket_number_assigned = True
            except Exception as exc:
                print("jQuery select_by_visible_text ticket_number fail (after click.)")
                print(exc)

    return is_ticket_number_assigned

def get_text_by_selector(driver, my_css_selector, attribute='innerHTML'):
    div_element = None
    try:
        div_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find element fail")
        pass

    row_text = ""
    if not div_element is None:
        try:
            if attribute=='innerText':
                row_html = div_element.get_attribute('innerHTML')
                row_text = util.remove_html_tags(row_html)
            else:
                row_text = div_element.get_attribute(attribute)
        except Exception as exc:
            print("get text fail:", my_css_selector)
    return row_text


def fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    form_input_list = []
    try:
        form_input_list = driver.find_elements(By.CSS_SELECTOR, input_text_css)
    except Exception as exc:
        if show_debug_message:
            print("find verify code input textbox fail")
        pass
    if form_input_list is None:
        form_input_list = []

    form_input_count = len(form_input_list)
    if show_debug_message:
        print("input textbox count:", form_input_count)

    is_do_press_next_button = False

    form_input_1 = None
    form_input_2 = None
    if form_input_count > 0:
        form_input_1 = form_input_list[0]
        if form_input_count > 1:
            form_input_2 = form_input_list[1]

    is_multi_question_mode = False
    answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
    if form_input_count == 1:
        is_do_press_next_button = True
    else:
        if form_input_count == 2:
            if not form_input_2 is None:
                if len(answer_list) >= 2:
                    if(len(answer_list[0]) > 0):
                        if(len(answer_list[1]) > 0):
                            is_multi_question_mode = True

    inputed_value_1 = None
    if not form_input_1 is None:
        try:
            inputed_value_1 = form_input_1.get_attribute('value')
        except Exception as exc:
            if show_debug_message:
                print("get_attribute of verify code fail")
            pass
    if inputed_value_1 is None:
        inputed_value_1 = ""

    inputed_value_2 = None
    if not form_input_2 is None:
        try:
            inputed_value_2 = form_input_2.get_attribute('value')
        except Exception as exc:
            if show_debug_message:
                print("get_attribute of verify code fail")
            pass
    if inputed_value_2 is None:
        inputed_value_2 = ""

    is_answer_sent = False
    if not is_multi_question_mode:
        if not form_input_1 is None:
            if len(inferred_answer_string) > 0:
                if inputed_value_1 != inferred_answer_string:
                    try:
                        # PS: sometime may send key twice...
                        form_input_1.clear()
                        form_input_1.send_keys(inferred_answer_string)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        pass

                is_button_clicked = False
                try:
                    if is_do_press_next_button:
                        if submit_by_enter:
                            form_input_1.send_keys(Keys.ENTER)
                            is_button_clicked = True
                        else:
                            if len(next_step_button_css) > 0:
                                is_button_clicked = press_button(driver, By.CSS_SELECTOR, next_step_button_css)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass
                
                if is_button_clicked:
                    is_answer_sent = True
                    fail_list.append(inferred_answer_string)
                    if show_debug_message:
                        print("Sending CAPTCHA answer by bot, attempt #", len(fail_list))

                if is_answer_sent:
                    for i in range(3):
                        time.sleep(0.1)
                        alert_ret = check_pop_alert(driver)
                        if alert_ret:
                            if show_debug_message:
                                print("press accept button at time #", i+1)
                            break
            else:
                # no answer to fill.
                if len(inputed_value_1)==0:
                    try:
                        # solution 1: js.
                        driver.execute_script("if(!(document.activeElement === arguments[0])){arguments[0].focus();}", form_input_1)
                        # solution 2: selenium.
                        #form_input_1.click()
                        time.sleep(check_input_interval)
                    except Exception as exc:
                        pass
    else:
        # multi question mode.
        try:
            if inputed_value_1 != answer_list[0]:
                form_input_1.clear()
                form_input_1.send_keys(answer_list[0])

            if inputed_value_2 != answer_list[1]:
                form_input_2.clear()
                form_input_2.send_keys(answer_list[1])

            is_button_clicked = False
            form_input_2.send_keys(Keys.ENTER)
            if len(next_step_button_css) > 0:
                is_button_clicked = press_button(driver, By.CSS_SELECTOR, next_step_button_css)

            if is_button_clicked:
                is_answer_sent = True
                fail_list.append(answer_list[0])
                fail_list.append(answer_list[1])
                if show_debug_message:
                    print("Sending CAPTCHA answer by bot, attempt #", len(fail_list))
        except Exception as exc:
            pass

    return is_answer_sent, fail_list


def ticketmaster_promo(driver, config_dict, fail_list):
    question_selector = '#promoBox'
    return tixcraft_input_check_code(driver, config_dict, fail_list, question_selector)

def tixcraft_verify(driver, config_dict, fail_list):
    question_selector = '.zone-verify'
    return tixcraft_input_check_code(driver, config_dict, fail_list, question_selector)

def tixcraft_input_check_code(driver, config_dict, fail_list, question_selector):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    question_text = get_text_by_selector(driver, question_selector, 'innerText')
    if len(question_text) > 0:
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                answer_list = util.guess_tixcraft_question(driver, question_text)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("answer_list:", answer_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        input_text_css = "input[name='checkCode']"
        next_step_button_css = ""
        submit_by_enter = True
        check_input_interval = 0.2
        is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return fail_list

def tixcraft_change_captcha(driver,url):
    try:
        driver.execute_script(f"document.querySelector('.verify-img').children[0].setAttribute('src','{url}');")
    except Exception as exc:
        print("edit captcha element fail")

def tixcraft_toast(driver, message):
    toast_element = None
    try:
        my_css_selector = "p.remark-word"
        toast_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not toast_element is None:
            driver.execute_script("arguments[0].innerHTML='%s';" % message, toast_element)
    except Exception as exc:
        #print("find toast element fail")
        pass

def tixcraft_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False
    is_form_sumbited = False

    # manually keyin verify code.
    # start to input verify code.
    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, '#TicketForm_verifyCode')
    except Exception as exc:
        print("find form_verifyCode fail")

    if not form_verifyCode is None:
        is_visible = False
        try:
            if form_verifyCode.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""
            is_visible = False

        if is_visible:
            is_text_clicked = False

            if inputed_value == "":
                try:
                    form_verifyCode.click()
                    is_text_clicked = True
                    is_verifyCode_editing = True
                except Exception as exc:
                    print("click form_verifyCode fail, trying to use javascript.")
                    # plan B
                    try:
                        driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").focus();")
                        is_verifyCode_editing = True
                    except Exception as exc:
                        #print("click form_verifyCode fail.")
                        pass

            if len(answer) > 0:
                #print("start to fill answer.")
                try:
                    if not is_text_clicked:
                        form_verifyCode.click()
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)

                    if auto_submit:
                        check_checkbox(driver, By.CSS_SELECTOR, '#TicketForm_agree')
                        form_verifyCode.send_keys(Keys.ENTER)
                        is_verifyCode_editing = False
                        is_form_sumbited = True
                    else:
                        driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").select();")
                        # TODO: show text message on ticketmaster web page.
                        tixcraft_toast(driver, "※ 按 Enter 如果答案是: " + answer)
                except Exception as exc:
                    print("send_keys ocr answer fail.")

    return is_verifyCode_editing, is_form_sumbited

def tixcraft_reload_captcha(driver, domain_name):
    # manually keyin verify code.
    # start to input verify code.
    ret = False
    form_captcha = None
    try:
        image_id = 'TicketForm_verifyCode-image'
        if 'indievox.com' in domain_name:
            image_id = 'TicketForm_verifyCode-image'
        form_captcha = driver.find_element(By.CSS_SELECTOR, "#" + image_id)
        if not form_captcha is None:
            form_captcha.click()
            ret = True
    except Exception as exc:
        print("find form_captcha fail")

    return ret

def tixcraft_get_ocr_answer(driver, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ocr_answer = None
    if not ocr is None:
        img_base64 = None

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.request_captcha())

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'TicketForm_verifyCode-image'
            image_element = None
            try:
                my_css_selector = "#" + image_id
                image_element = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not image_element is None:
                if 'indievox.com' in domain_name:
                    #image_id = 'TicketForm_verifyCode-image'
                    pass
                try:
                    driver.set_script_timeout(1)
                    form_verifyCode_base64 = driver.execute_async_script("""
                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        var img = document.getElementById('%s');
                        if(img!=null) {
                        canvas.height = img.naturalHeight;
                        canvas.width = img.naturalWidth;
                        context.drawImage(img, 0, 0);
                        callback = arguments[arguments.length - 1];
                        callback(canvas.toDataURL()); }
                        """ % (image_id))
                    if not form_verifyCode_base64 is None:
                        img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])

                    if img_base64 is None:
                        if not Captcha_Browser is None:
                            print("canvas get image fail, use plan_b: NonBrowser")
                            img_base64 = base64.b64decode(Captcha_Browser.request_captcha())
                except Exception as exc:
                    if show_debug_message:
                        print("canvas exception:", str(exc))
                    pass

        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

    return ocr_answer

#PS: credit to LinShihJhang's share
def tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_need_redo_ocr = False
    is_form_sumbited = False

    is_input_box_exist = False
    if not ocr is None:
        form_verifyCode = None
        try:
            form_verifyCode = driver.find_element(By.CSS_SELECTOR, '#TicketForm_verifyCode')
            is_input_box_exist = True
        except Exception as exc:
            pass
    else:
        print("ddddocr component is not able to use, you may running in arm environment.")

    if is_input_box_exist:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()
        ocr_answer = tixcraft_get_ocr_answer(driver, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name)
        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        if show_debug_message:
            print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))

        if ocr_answer is None:
            if away_from_keyboard_enable:
                # page is not ready, retry again.
                # PS: usually occur in async script get captcha image.
                is_need_redo_ocr = True
                time.sleep(0.1)
            else:
                tixcraft_keyin_captcha_code(driver)
        else:
            ocr_answer = ocr_answer.strip()
            if show_debug_message:
                print("ocr_answer:", ocr_answer)
            if len(ocr_answer)==4:
                who_care_var, is_form_sumbited = tixcraft_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
            else:
                if not away_from_keyboard_enable:
                    tixcraft_keyin_captcha_code(driver)
                else:
                    is_need_redo_ocr = True
                    if previous_answer != ocr_answer:
                        previous_answer = ocr_answer
                        if show_debug_message:
                            print("click captcha again.")
                        if True:
                            # selenium solution.
                            tixcraft_reload_captcha(driver, domain_name)

                            if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                                time.sleep(0.1)
                        else:
                            # Non_Browser solution.
                            if not Captcha_Browser is None:
                                new_captcha_url = Captcha_Browser.request_refresh_captcha() #取得新的CAPTCHA
                                if new_captcha_url != "":
                                    tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
    else:
        print("input box not exist, quit ocr...")

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def tixcraft_ticket_main_agree(driver, config_dict):
    is_finish_checkbox_click = False
    for i in range(3):
        is_finish_checkbox_click = check_checkbox(driver, By.CSS_SELECTOR, '#TicketForm_agree')
        if is_finish_checkbox_click:
            break
    return is_finish_checkbox_click

def get_tixcraft_ticket_select_by_keyword(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_need_refresh = False
    matched_blocks = None

    area_list = None
    area_list_count = 0

    try:
        my_css_selector = "table#ticketPriceList > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find area list a tag fail")
        pass

    if not area_list is None:
        area_list_count = len(area_list)
        if area_list_count == 0:
            print("area list is empty, do refresh!")
            is_need_refresh = True
    else:
        print("area list is None, do refresh!")
        is_need_refresh = True

    if area_list_count > 0:
        matched_blocks = []
        for row in area_list:
            row_text = ""
            row_html = ""
            try:
                #row_text = row.text
                row_html = row.get_attribute('innerHTML')
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                # error, exit loop
                break

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = util.format_keyword_string(row_text)

                is_append_this_row = False

                if len(area_keyword_item) > 0:
                    # must match keyword.
                    is_append_this_row = True
                    area_keyword_array = area_keyword_item.split(' ')
                    for area_keyword in area_keyword_array:
                        area_keyword = util.format_keyword_string(area_keyword)
                        if not area_keyword in row_text:
                            is_append_this_row = False
                            break
                else:
                    # without keyword.
                    is_append_this_row = True

                if show_debug_message:
                    print("is_append_this_row:", is_append_this_row, row_text)

                if is_append_this_row:
                    matched_blocks.append(row)

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        #print("only need first item, break area list loop.")
                        break

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True

    return is_need_refresh, matched_blocks

def get_tixcraft_ticket_select(driver, config_dict):
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    form_select = None
    matched_blocks = None
    if len(area_keyword) > 0:
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []
        for area_keyword_item in area_keyword_array:
            is_need_refresh, matched_blocks = get_tixcraft_ticket_select_by_keyword(driver, config_dict, area_keyword_item)
            if not is_need_refresh:
                break
            else:
                print("is_need_refresh for keyword:", area_keyword_item)
    else:
        # empty keyword, match all.
        is_need_refresh, matched_blocks = get_tixcraft_target_area(driver, config_dict, "")

    auto_select_mode = config_dict["area_auto_select"]["mode"]
    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            form_select = target_area.find_element(By.TAG_NAME, 'select')
        except Exception as exc:
            #print("find area list a tag fail")
            form_select = None
            pass

    return form_select

def tixcraft_assign_ticket_number(driver, config_dict):
    is_ticket_number_assigned = False

    # allow agree not enable to assign ticket number.
    form_select_list = None
    try:
        form_select_list = driver.find_elements(By.CSS_SELECTOR, '.mobile-select')
    except Exception as exc:
        print("find select fail")
        pass

    form_select = None
    form_select_count = 0
    if not form_select_list is None:
        form_select_count = len(form_select_list)
        if form_select_count >= 1:
            form_select = form_select_list[0]

    # multi select box
    if form_select_count > 1:
        if config_dict["area_auto_select"]["enable"]:
            # for tixcraft
            form_select_temp = get_tixcraft_ticket_select(driver, config_dict)
            if not form_select_temp is None:
                form_select = form_select_temp

    # for ticketmaster
    if form_select is None:
        try:
            form_select = driver.find_element(By.CSS_SELECTOR, 'td > select.form-select')
        except Exception as exc:
            print("find form-select fail")
            pass

    select_obj = None
    if not form_select is None:
        try:
            select_obj = Select(form_select)
        except Exception as exc:
            pass

    if not select_obj is None:
        row_text = None
        try:
            selected_option = select_obj.first_selected_option
            row_text = selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 0:
                if row_text != "0":
                    if row_text.isnumeric():
                        # ticket assign.
                        is_ticket_number_assigned = True

    return is_ticket_number_assigned, select_obj


def tixcraft_ticket_main(driver, config_dict, ocr, Captcha_Browser, domain_name):
    is_agree_at_webdriver = False
    if not config_dict["browser"] in CONST_CHROME_FAMILY:
        is_agree_at_webdriver = True
    else:
        if not config_dict["advanced"]["chrome_extension"]:
            is_agree_at_webdriver = True
    if is_agree_at_webdriver:
        # use extension instead of selenium.
        # checkbox javascrit code at chrome extension.
        tixcraft_ticket_main_agree(driver, config_dict)

    is_ticket_number_assigned = False

    # PS: some events on tixcraft have multi <select>.
    is_ticket_number_assigned, select_obj = tixcraft_assign_ticket_number(driver, config_dict)

    if not is_ticket_number_assigned:
        # should not enter this block, due to extension done.
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = ticket_number_select_fill(driver, select_obj, ticket_number)

    # must wait ticket number assign to focus captcha.
    if is_ticket_number_assigned:
        tixcraft_ticket_main_ocr(driver, config_dict, ocr, Captcha_Browser, domain_name)

def tixcraft_ticket_main_ocr(driver, config_dict, ocr, Captcha_Browser, domain_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    if not config_dict["ocr_captcha"]["enable"]:
        tixcraft_keyin_captcha_code(driver)
    else:
        previous_answer = None
        last_url, is_quit_bot = get_current_url(driver)
        for redo_ocr in range(19):
            is_need_redo_ocr, previous_answer, is_form_sumbited = tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name)
            if is_form_sumbited:
                # start next loop.
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break

            current_url, is_quit_bot = get_current_url(driver)
            if current_url != last_url:
                break

def kktix_confirm_order_button(driver):
    ret = False

    wait = WebDriverWait(driver, 1)
    next_step_button = None
    try:
        # method #3 wait
        next_step_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.form-actions a.btn-primary')))
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        print("wait form-actions div wait to be clickable Exception:")
        #print(exc)
        pass

    return ret


# PS: There are two "Next" button in kktix.
#   : 1: /events/xxx
#   : 2: /events/xxx/registrations/new
#   : This is ONLY for case-1, because case-2 lenght >5
def kktix_events_press_next_button(driver):
    is_button_clicked = press_button(driver, By.CSS_SELECTOR,'.tickets > a.btn-point')
    return is_button_clicked

#   : This is for case-2 next button.
def kktix_press_next_button(driver):
    ret = False

    css_select = "div.register-new-next-button-area > button"
    but_button_list = None
    try:
        but_button_list = driver.find_elements(By.CSS_SELECTOR, css_select)
    except Exception as exc:
        print(exc)
        pass

    if not but_button_list is None:
        button_count = len(but_button_list)
        #print("button_count:",button_count)
        if button_count > 0:
            btn = but_button_list[button_count-1]
            try:
                driver.set_script_timeout(0.1)
                driver.execute_script("arguments[0].focus();", btn)
                ret = True
            except Exception as exc:
                pass
            for retry_idx in range(4):
                try:
                    #print("click on last button:", button_count)
                    btn.click()
                    time.sleep(0.2)
                    ret = True
                except Exception as exc:
                    print(exc)
                    pass
                if ret:
                    break

    return ret


def kktix_travel_price_list(driver, config_dict, kktix_area_auto_select_mode, kktix_area_keyword):
    show_debug_message = config_dict["advanced"]["verbose"]
    ticket_number = config_dict["ticket_number"]

    areas = None
    is_ticket_number_assigned = False

    ticket_price_list = None
    try:
        ticket_price_list = driver.find_elements(By.CSS_SELECTOR, 'div.display-table-row')
    except Exception as exc:
        ticket_price_list = None
        print("find ticket-price Exception:")
        print(exc)
        pass

    is_dom_ready = True
    price_list_count = 0
    if not ticket_price_list is None:
        price_list_count = len(ticket_price_list)
        if show_debug_message:
            print("found price count:", price_list_count)
    else:
        is_dom_ready = False
        print("find ticket-price fail")

    if price_list_count > 0:
        areas = []

        kktix_area_keyword_array = kktix_area_keyword.split(' ')
        kktix_area_keyword_1 = kktix_area_keyword_array[0]
        kktix_area_keyword_1_and = ""
        if len(kktix_area_keyword_array) > 1:
            kktix_area_keyword_1_and = kktix_area_keyword_array[1]

        # clean stop word.
        kktix_area_keyword_1 = util.format_keyword_string(kktix_area_keyword_1)
        kktix_area_keyword_1_and = util.format_keyword_string(kktix_area_keyword_1_and)

        if show_debug_message:
            print('kktix_area_keyword_1:', kktix_area_keyword_1)
            print('kktix_area_keyword_1_and:', kktix_area_keyword_1_and)

        for row in ticket_price_list:
            row_text = ""
            row_html = ""
            try:
                #row_text = row.text
                row_html = row.get_attribute('innerHTML')
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                is_dom_ready = False
                if show_debug_message:
                    print(exc)
                # error, exit loop
                break

            if len(row_text) > 0:
                if '未開賣' in row_text:
                    row_text = ""

                if '暫無票' in row_text:
                    row_text = ""

                if '已售完' in row_text:
                    row_text = ""

                if 'Sold Out' in row_text:
                    row_text = ""

                if '完売' in row_text:
                    row_text = ""

                if not('<input type=' in row_html):
                    row_text = ""

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = util.format_keyword_string(row_text)

            if len(row_text) > 0:
                if ticket_number > 1:
                    # start to check danger notice.
                    # 剩 n 張票 / n Left / 残り n 枚
                    ticket_count = 999
                    # for cht.
                    if ' danger' in row_html and '剩' in row_text and '張' in row_text:
                        tmp_array = row_html.split('剩')
                        tmp_array = tmp_array[1].split('張')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[0].strip()
                            if tmp_ticket_count.isdigit():
                                ticket_count = int(tmp_ticket_count)
                                if show_debug_message:
                                    print("found ticket 剩:", tmp_ticket_count)
                    # for ja.
                    if ' danger' in row_html and '残り' in row_text and '枚' in row_text:
                        tmp_array = row_html.split('残り')
                        tmp_array = tmp_array[1].split('枚')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[0].strip()
                            if tmp_ticket_count.isdigit():
                                ticket_count = int(tmp_ticket_count)
                                if show_debug_message:
                                    print("found ticket 残り:", tmp_ticket_count)
                    # for en.
                    if ' danger' in row_html and ' Left ' in row_html:
                        tmp_array = row_html.split(' Left ')
                        tmp_array = tmp_array[0].split('>')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[len(tmp_array)-1].strip()
                            if tmp_ticket_count.isdigit():
                                if show_debug_message:
                                    print("found ticket left:", tmp_ticket_count)
                                ticket_count = int(tmp_ticket_count)

                    if ticket_count < ticket_number:
                        # skip this row, due to no ticket remaining.
                        if show_debug_message:
                            print("found ticket left:", tmp_ticket_count, ",but target ticket:", ticket_number)
                        row_text = ""

            if len(row_text) > 0:
                # check ticket input textbox.
                ticket_price_input = None
                try:
                    ticket_price_input = row.find_element(By.CSS_SELECTOR, "input[type='text']")
                except Exception as exc:
                    pass

                if not ticket_price_input is None:
                    current_ticket_number = ""
                    is_visible = False

                    try:
                        current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
                        is_visible = ticket_price_input.is_enabled()
                    except Exception as exc:
                        pass

                    if len(current_ticket_number) > 0:
                        if current_ticket_number != "0":
                            is_ticket_number_assigned = True

                    if is_ticket_number_assigned:
                        # no need to travel
                        break

                    if is_visible:
                        is_match_area = False
                        match_area_code = 0

                        if len(kktix_area_keyword_1) == 0:
                            # keyword #1, empty, direct add to list.
                            is_match_area = True
                            match_area_code = 1
                        else:
                            # MUST match keyword #1.
                            if kktix_area_keyword_1 in row_text:
                                #print('match keyword#1')

                                # because of logic between keywords is AND!
                                if len(kktix_area_keyword_1_and) == 0:
                                    #print('keyword#2 is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if kktix_area_keyword_1_and in row_text:
                                        #print('match keyword#2')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        #print('not match keyword#2')
                                        pass
                            else:
                                #print('not match keyword#1')
                                pass

                        if show_debug_message:
                            print("is_match_area:", is_match_area)
                            print("match_area_code:", match_area_code)

                        if is_match_area:
                            areas.append(ticket_price_input)

                            # from top to bottom, match first to break.
                            if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break


            if not is_dom_ready:
                # not sure to break or continue..., maybe break better.
                break
    else:
        if show_debug_message:
            print("no any price list found.")
        pass

    return is_dom_ready, is_ticket_number_assigned, areas

def kktix_assign_ticket_number(driver, config_dict, kktix_area_keyword):
    show_debug_message = config_dict["advanced"]["verbose"]

    ticket_number_str = str(config_dict["ticket_number"])
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_ticket_number_assigned = False
    matched_blocks = None
    is_dom_ready = True
    is_dom_ready, is_ticket_number_assigned, matched_blocks = kktix_travel_price_list(driver, config_dict, auto_select_mode, kktix_area_keyword)

    target_area = None
    is_need_refresh = False
    if is_dom_ready:
        if not is_ticket_number_assigned:
            target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

        if not matched_blocks is None:
            if len(matched_blocks) == 0:
                is_need_refresh = True
                if show_debug_message:
                    print("matched_blocks is empty, is_need_refresh")

    if not target_area is None:
        current_ticket_number = ""
        if show_debug_message:
            print("try to get input box value.")
        try:
            current_ticket_number = str(target_area.get_attribute('value')).strip()
        except Exception as exc:
            pass

        if len(current_ticket_number) > 0:
            if current_ticket_number == "0":
                try:
                    print("asssign ticket number:%s" % ticket_number_str)
                    target_area.clear()
                    target_area.send_keys(ticket_number_str)
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("asssign ticket number to ticket-price field Exception:")
                    print(exc)
                    try:
                        target_area.clear()
                        target_area.send_keys("1")
                        is_ticket_number_assigned = True
                    except Exception as exc2:
                        print("asssign ticket number to ticket-price still failed.")
                        pass
            else:
                if show_debug_message:
                    print("value already assigned.")
                # already assigned.
                is_ticket_number_assigned = True

    return is_dom_ready, is_ticket_number_assigned, is_need_refresh



def kktix_check_agree_checkbox(driver, config_dict):
    show_debug_message = config_dict["advanced"]["verbose"]

    is_finish_checkbox_click = False
    is_dom_ready = False
    try:
        html_body = driver.page_source
        #print("html_body:",len(html_body))
        if len(html_body) > 0:
            if not "{{'new.i_read_and_agree_to'" in html_body:
                is_dom_ready = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    if is_dom_ready:
        is_finish_checkbox_click = check_checkbox(driver, By.CSS_SELECTOR, '#person_agree_terms')

    #print("status:", is_dom_ready, is_finish_checkbox_click)
    return is_dom_ready, is_finish_checkbox_click

def check_checkbox(driver, by, query):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    agree_checkbox = None
    try:
        agree_checkbox = driver.find_element(by, query)
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass
    is_checkbox_checked = False
    if not agree_checkbox is None:
        is_checkbox_checked = force_check_checkbox(driver, agree_checkbox)
    return is_checkbox_checked

def force_check_checkbox(driver, agree_checkbox):
    is_finish_checkbox_click = False
    if not agree_checkbox is None:
        is_visible = False
        try:
            if agree_checkbox.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            is_checkbox_checked = False
            try:
                if agree_checkbox.is_selected():
                    is_checkbox_checked = True
            except Exception as exc:
                pass

            if not is_checkbox_checked:
                #print('send check to checkbox')
                try:
                    agree_checkbox.click()
                    is_finish_checkbox_click = True
                except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", agree_checkbox)
                        is_finish_checkbox_click = True
                    except Exception as exc:
                        pass
            else:
                is_finish_checkbox_click = True
    return is_finish_checkbox_click


# PS: no double check, NOW.
def kktix_double_check_all_text_value(driver, ticket_number):
    is_do_press_next_button = False

    # double check ticket input textbox.
    ticket_price_input_list = None
    try:
        # PS: unable directly access text's value attribute via css selector or xpath on KKTix!
        my_css_selector = "input[type='text']"
        #print("my_css_selector:", my_css_selector)
        ticket_price_input_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    if not ticket_price_input_list is None:
        #print("bingo, found one of ticket number textbox.")
        for ticket_price_input in ticket_price_input_list:
            current_ticket_number = ""
            try:
                current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            except Exception as exc:
                pass
            if current_ticket_number is None:
                current_ticket_number = ""
            if len(current_ticket_number) > 0:
                if current_ticket_number == str(ticket_number):
                    #print("bingo, match target ticket number.")

                    # ONLY, this case to auto press next button.
                    is_do_press_next_button = True
                    break

    return is_do_press_next_button

def set_kktix_control_label_text(driver, config_dict):
    fail_list = []
    answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
    inferred_answer_string = ""
    for answer_item in answer_list:
        if not answer_item in fail_list:
            inferred_answer_string = answer_item
            break
    input_text_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > input[type="text"]'
    next_step_button_css = '#registrationsNewApp div.form-actions button.btn-primary'
    submit_by_enter = False
    check_input_interval = 0.2
    is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)


def kktix_reg_captcha(driver, config_dict, fail_list, registrationsNewApp_div):
    show_debug_message = config_dict["advanced"]["verbose"]

    answer_list = []

    is_question_popup = False
    question_text = get_text_by_selector(driver, 'div.custom-captcha-inner p', 'innerText')
    if len(question_text) > 0:
        is_question_popup = True
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                answer_list = util.get_answer_list_from_question_string(registrationsNewApp_div, question_text)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        if len(answer_list) > 0:
            answer_list = list(dict.fromkeys(answer_list))

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("answer_list:", answer_list)
            print("fail_list:", fail_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        if len(inferred_answer_string) > 0:
            input_text_css = 'div.custom-captcha-inner > div > div > input'
            next_step_button_css = ''
            submit_by_enter = False
            check_input_interval = 0.2
            is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

            # due multi next buttons(pick seats/best seats)
            kktix_press_next_button(driver)
            time.sleep(0.5)

            fail_list.append(inferred_answer_string)
        #print("new fail_list:", fail_list)

    return fail_list, is_question_popup

def kktix_reg_new_main(driver, config_dict, fail_list, played_sound_ticket):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    # part 1: check div.
    registrationsNewApp_div = None
    try:
        registrationsNewApp_div = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp')
    except Exception as exc:
        pass
        #print("find input fail:", exc)

    # part 2: assign ticket number
    is_ticket_number_assigned = False
    if not registrationsNewApp_div is None:
        is_dom_ready = True
        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            # default refresh
            is_need_refresh_final = True

            for area_keyword_item in area_keyword_array:
                is_need_refresh_tmp = False
                is_dom_ready, is_ticket_number_assigned, is_need_refresh_tmp = kktix_assign_ticket_number(driver, config_dict, area_keyword_item)

                if not is_dom_ready:
                    # page redirecting.
                    break

                # one of keywords not need to refresh, final is not refresh.
                if not is_need_refresh_tmp:
                    is_need_refresh_final = False

                if is_ticket_number_assigned:
                    break
                else:
                    if show_debug_message:
                        print("is_need_refresh for keyword:", area_keyword_item)

            if not is_ticket_number_assigned:
                is_need_refresh = is_need_refresh_final
        else:
            # empty keyword, match all.
            is_dom_ready, is_ticket_number_assigned, is_need_refresh = kktix_assign_ticket_number(driver, config_dict, "")

        if is_dom_ready:
            # part 3: captcha
            if is_ticket_number_assigned:
                if config_dict["advanced"]["play_sound"]["ticket"]:
                    if not played_sound_ticket:
                        play_sound_while_ordering(config_dict)
                    played_sound_ticket = True

                # whole event question.
                fail_list, is_question_popup = kktix_reg_captcha(driver, config_dict, fail_list, registrationsNewApp_div)

                # single option question
                if not is_question_popup:
                    # no captcha text popup, goto next page.
                    control_text = get_text_by_selector(driver, 'div > div.code-input > div.control-group > label.control-label', 'innerText')
                    if show_debug_message:
                        print("control_text:", control_text)

                    if len(control_text) > 0:
                        input_text_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > input[type="text"]'
                        input_text_element = None
                        try:
                            input_text_element = driver.find_element(By.CSS_SELECTOR, input_text_css)
                        except Exception as exc:
                            #print(exc)
                            pass
                        if input_text_element is None:
                            radio_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > input[type="radio"]'
                            try:
                                radio_element = driver.find_element(By.CSS_SELECTOR, radio_css)
                                if radio_element:
                                    print("found radio")
                                    joined_button_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > span[ng-if] > a[ng-href="#"]'
                                    joined_element = driver.find_element(By.CSS_SELECTOR, joined_button_css)
                                    if joined_element:
                                        control_text = ""
                                        print("member joined")
                            except Exception as exc:
                                print(exc)
                                pass

                    if len(control_text) == 0:
                        click_ret = kktix_press_next_button(driver)
                    else:
                        # input by maxbox plus extension.
                        is_fill_at_webdriver = False

                        if not config_dict["browser"] in CONST_CHROME_FAMILY:
                            is_fill_at_webdriver = True
                        else:
                            if not config_dict["advanced"]["chrome_extension"]:
                                is_fill_at_webdriver = True

                        # TODO: not implement in extension, so force to fill in webdriver.
                        is_fill_at_webdriver = True
                        if is_fill_at_webdriver:
                            set_kktix_control_label_text(driver, config_dict)
                        pass
            else:
                if is_need_refresh:
                    # reset to play sound when ticket avaiable.
                    played_sound_ticket = False

                    try:
                        print("no match any price, start to refresh page...")
                        driver.refresh()
                    except Exception as exc:
                        #print("refresh fail")
                        pass

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return fail_list, played_sound_ticket


def kktix_check_register_status(driver, url):
    event_code = util.kktix_get_event_code(url)
    if len(event_code) > 0:
        js = '''
function load_kktix_register_code(){
let api_url = "https://kktix.com/g/events/%s/register_info";
fetch(api_url).then(function (response)
{
return response.json();
}
).then(function (data)
{
let reload=false;
console.log(data.inventory.registerStatus);
if(data.inventory.registerStatus=='OUT_OF_STOCK') {reload=true;}
if(data.inventory.registerStatus=='COMING_SOON') {reload=true;}
if(data.inventory.registerStatus=='SOLD_OUT') {reload=true;}
console.log(reload);
if(reload) {location.reload();}
}
).catch(function (err)
{
console.log(err);
});
}
if (!$.kkUser) {
    $.kkUser = {};
}
if (typeof $.kkUser.checked_status_register_code === 'undefined') {
    $.kkUser.checked_status_register_code = true;
    load_kktix_register_code();
}
        ''' % (event_code)
        try:
            driver.execute_script(js)
        except Exception as exc:
            pass

    registerStatus = None

    # use javascritp version only.
    is_match_event_code = False
    if is_match_event_code:
        registerStatus = util.kktix_get_registerStatus(event_code)
    return registerStatus

def kktix_reg_auto_reload(driver, url, config_dict):
    # auto reload javascrit code at chrome extension.
    is_reload_at_webdriver = False
    if not config_dict["browser"] in CONST_CHROME_FAMILY:
        is_reload_at_webdriver = True
    else:
        if not config_dict["advanced"]["chrome_extension"]:
            is_reload_at_webdriver = True
    if is_reload_at_webdriver:
        kktix_check_register_status(driver, url)


# PURPOSE: get target area list.
# PS: this is main block, use keyword to get rows.
def get_fami_target_area(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    area_list = None
    try:
        my_css_selector = "table.session__list > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #session date list fail")
        if show_debug_message:
            print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if not area_list is None:
        area_list_length = len(area_list)
        if show_debug_message:
            print("lenth of area rows:", area_list_length)

        if area_list_length > 0:
            formated_area_list = []

            # filter list.
            for row in area_list:
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if not el_btn is None:
                        if not el_btn.is_enabled():
                            #print("row's button disabled!")
                            row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

    matched_blocks = None
    if not formated_area_list is None:
        if len(formated_area_list) > 0:
            matched_blocks = []

            if len(date_keyword)==0 and len(area_keyword_item)==0:
                # select all.
                matched_blocks = formated_area_list
            else:
                # match keyword.
                for row in formated_area_list:
                    date_html_text = ""
                    area_html_text = ""
                    row_text = ""
                    row_html = ""
                    try:
                        my_css_selector = "td:nth-child(1)"
                        td_date = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if not td_date is None:
                            #print("date:", td_date.text)
                            date_html_text = util.format_keyword_string(td_date.text)

                        my_css_selector = "td:nth-child(2)"
                        td_area = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if not td_area is None:
                            #print("area:", td_area.text)
                            area_html_text = util.format_keyword_string(td_area.text)

                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                            row_text = ""

                    if len(row_text) > 0:
                        # check date.
                        is_match_date = False
                        if len(date_keyword) > 0:
                            # Support OR logic: "9/11","9/22","3/3"
                            date_keyword_array = []
                            try:
                                date_keyword_array = json.loads("["+ date_keyword +"]")
                            except Exception as exc:
                                date_keyword_array = []

                            for date_keyword_item in date_keyword_array:
                                if ' ' in date_keyword_item:
                                    # AND logic within each item
                                    keyword_item_array = date_keyword_item.split(' ')
                                    is_match_all = True
                                    for keyword_item in keyword_item_array:
                                        keyword_item = util.format_keyword_string(keyword_item)
                                        if not keyword_item in date_html_text:
                                            is_match_all = False
                                            break
                                    if is_match_all:
                                        is_match_date = True
                                        break
                                else:
                                    # Single keyword
                                    formatted_date_keyword = util.format_keyword_string(date_keyword_item)
                                    if formatted_date_keyword in date_html_text:
                                        is_match_date = True
                                        break
                        else:
                            is_match_date = True

                        # check area.
                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_date and is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                #print("only need first item, break area list loop.")
                                break

    return_row_count = 0
    if not matched_blocks is None:
        return_row_count = len(matched_blocks)
        if return_row_count==0:
            matched_blocks = None

    if show_debug_message:
        print("return_row_count:", return_row_count)

    return matched_blocks

def fami_verify(driver, config_dict, fail_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    question_text = ""
    #if len(question_text) > 0:
    if True:
        #write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                answer_list = util.guess_tixcraft_question(driver, question_text)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("answer_list:", answer_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        input_text_css = "#verifyPrefAnswer"
        next_step_button_css = ""
        submit_by_enter = True
        check_input_interval = 0.2
        is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return fail_list

def fami_activity(driver):
    #print("fami_activity bingo")

    #---------------------------
    # part 1: press "buy" button.
    #---------------------------
    fami_start_to_buy_button = None
    try:
        fami_start_to_buy_button = driver.find_element(By.CSS_SELECTOR, '#buyWaiting')
    except Exception as exc:
        pass

    is_visible = False
    is_need_refresh = False
    if not fami_start_to_buy_button is None:
        try:
            if fami_start_to_buy_button.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
    else:
        is_need_refresh = True

    if is_visible:
        try:
            fami_start_to_buy_button.click()
        except Exception as exc:
            print("click buyWaiting button fail...")
            #print(exc)
            #pass
            try:
                js = """arguments[0].scrollIntoView();
                arguments[0].firstChild.click();
                """
                #driver.execute_script(js, fami_start_to_buy_button)
            except Exception as exc:
                pass

    if is_need_refresh:
        try:
            driver.refresh()
        except Exception as exc:
            pass

def fami_date_auto_select(driver, config_dict, last_activity_url):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    matched_blocks = None

    area_list = None
    try:
        my_css_selector = ".session__list > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find date-time rows fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if "<button" in row_html:
                        if not("立即購買" in row_html):
                            row_text = ""
                    else:
                        row_text = ""

                if len(row_text) > 0:
                    formated_area_list.append(row)

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    is_date_assign_by_bot = False
    if not target_area is None:
        is_button_clicked = False
        for i in range(3):
            el_btn = None
            try:
                my_css_selector = "button"
                el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not el_btn is None:
                try:
                    if el_btn.is_enabled():
                        el_btn.click()
                        print("buy icon pressed.")
                        is_button_clicked = True
                except Exception as exc:
                    pass
                    # use plan B
                    '''
                    try:
                        print("force to click by js.")
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass
                    '''
            if is_button_clicked:
                break
        is_date_assign_by_bot = is_button_clicked

    else:
        # no target to click.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        #driver.refresh()
                        driver.get(last_activity_url)
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_date_assign_by_bot

def fami_area_auto_select(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    area_list = None
    try:
        my_css_selector = "div > a.area"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find a.area list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_item:", area_keyword_item)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if '售完' in row_text:
                    row_text = ""

                if '"area disabled"' in row_html:
                    row_text = ""

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    matched_blocks = []
    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break


            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not matched_blocks is None:
        if len(matched_blocks) == 0:
            is_need_refresh = True
            if show_debug_message:
                print("matched_blocks is empty, is_need_refresh")

    if not target_area is None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot

def fami_date_to_area(driver, config_dict, last_activity_url):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    # click price row.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    if show_debug_message:
        print("area_keyword:", area_keyword)

    is_need_refresh = False

    if len(area_keyword) > 0:
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []

        for area_keyword_item in area_keyword_array:
            is_need_refresh, is_price_assign_by_bot = fami_area_auto_select(driver, config_dict, area_keyword_item)
            if not is_need_refresh:
                break
            else:
                print("is_need_refresh for keyword:", area_keyword_item)
    else:
        # empty keyword, match all.
        is_need_refresh, is_price_assign_by_bot = fami_area_auto_select(driver, config_dict, area_keyword)

    if show_debug_message:
        print("is_need_refresh:", is_need_refresh)

    if is_need_refresh:
        try:
            #driver.refresh()
            #driver.get(last_activity_url)
            pass
        except Exception as exc:
            pass

        if config_dict["advanced"]["auto_reload_page_interval"] > 0:
            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_price_assign_by_bot

def fami_home_auto_select(driver, config_dict, last_activity_url):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_ticket_number_assigned = False

    ticket_number = str(config_dict["ticket_number"])

    #---------------------------
    # part 3: fill ticket number.
    #---------------------------
    ticket_el = None
    is_date_assign_by_bot = False
    is_price_assign_by_bot = False
    try:
        my_css_selector = "tr.ticket > td > select"
        ticket_el = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ticket select element")
        pass
        #print(exc)

    if ticket_el is None:
        print("try to find datetime table list")
        is_date_assign_by_bot = fami_date_auto_select(driver, config_dict, last_activity_url)
        is_price_assign_by_bot = fami_date_to_area(driver, config_dict, last_activity_url)

    is_select_box_visible = False
    if not ticket_el is None:
        try:
            if ticket_el.is_enabled():
                is_select_box_visible = True
        except Exception as exc:
            pass

    is_ticket_number_assigned = False
    if is_select_box_visible:
        ticket_number_select = None
        try:
            ticket_number_select = Select(ticket_el)
        except Exception as exc:
            pass

        if not ticket_number_select is None:
            try:
                #print("get select ticket value:" + Select(ticket_number_select).first_selected_option.text)
                if ticket_number_select.first_selected_option.text=="0" or ticket_number_select.first_selected_option.text=="選擇張數":
                    # target ticket number
                    ticket_number_select.select_by_visible_text(ticket_number)
                    is_ticket_number_assigned = True
            except Exception as exc:
                print("select_by_visible_text ticket_number fail")
                print(exc)

                try:
                    # try target ticket number twice
                    ticket_number_select.select_by_visible_text(ticket_number)
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("select_by_visible_text ticket_number fail...2")
                    print(exc)

                    # try buy one ticket
                    try:
                        ticket_number_select.select_by_visible_text("1")
                        is_ticket_number_assigned = True
                    except Exception as exc:
                        print("select_by_visible_text 1 fail")
                        pass

    #---------------------------
    # part 4: press "next" button.
    #---------------------------
    if is_ticket_number_assigned:
        fami_assign_site_button = None
        try:
            my_css_selector = "div.col > a.btn"
            fami_assign_site_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not fami_assign_site_button is None:
            is_visible = False
            try:
                if fami_assign_site_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    fami_assign_site_button.click()
                except Exception as exc:
                    print("click buyWaiting button fail")
                    #print(exc)
                    try:
                        driver.execute_script("arguments[0].click();", fami_assign_site_button)
                    except Exception as exc:
                        pass


    matched_blocks = None
    if not is_select_box_visible:
        #---------------------------
        # part 2: select keywords
        #---------------------------

        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            for area_keyword_item in area_keyword_array:
                matched_blocks = get_fami_target_area(driver, config_dict, area_keyword_item)
                if not matched_blocks is None:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            matched_blocks = get_fami_target_area(driver, config_dict, "")

        auto_select_mode = config_dict["area_auto_select"]["mode"]
        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
        if not target_area is None:
            el_btn = None
            is_visible = False
            try:
                my_css_selector = "button"
                el_btn = target_area.find_element(By.TAG_NAME, my_css_selector)
                if not el_btn is None:
                    if el_btn.is_enabled():
                        is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    el_btn.click()
                except Exception as exc:
                    print("click buy button fail, start to retry...")
                    try:
                        driver.execute_script("arguments[0].click();", el_btn)
                    except Exception as exc:
                        pass

    return is_date_assign_by_bot

# purpose: date auto select
def urbtix_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.conent-wrapper > div.list-wrapper > ul"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None

    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            for row in area_list:
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "div.buy-icon"
                    el_btn = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if not el_btn is None:
                        button_class_string = str(el_btn.get_attribute('class'))
                        if len(button_class_string) > 1:
                            if 'disabled' in button_class_string:
                                row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if show_debug_message:
                            print("row_text:", row_text)
                        is_match_area = util.is_row_match_keyword(date_keyword, row_text)
                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                #print("only need first item, break area list loop.")
                                break


                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "div.buy-icon"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass
        if not el_btn is None:
            is_button_enable = True
            try:
                if not el_btn.is_enabled():
                    is_button_enable = False
                else:
                    # button enable, but class disable.
                    button_class_string = str(el_btn.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            is_button_enable = False
                if is_button_enable:
                    el_btn.click()
                    ret = True
                    print("buy icon pressed.")
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
    else:
        # no target.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(1.0)
                    except Exception as exc:
                        pass

    return ret

def urbtix_purchase_ticket(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    date_auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    is_date_assign_by_bot = urbtix_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    return is_date_assign_by_bot

# purpose: area auto select
def urbtix_area_auto_select(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.area-list > div.area-wrapper"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_item:", area_keyword_item)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:
                    if ' disabled' in row_html:
                        row_text = ""
                    if ' 售罄' in row_html:
                        row_text = ""

                if len(row_text) > 0:
                    if '<div class="area-info selected' in row_html:
                        # someone is selected. skip this process.
                        is_price_assign_by_bot = True

                        row_text = ""
                        break

                if len(row_text) > 0:
                    #print("row_html:", row_html)
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break


            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot


def urbtix_ticket_number_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_ticket_number_assigned = False

    ticket_number = config_dict["ticket_number"]
    ticket_number_str = str(ticket_number)

    # check ticket input textbox.
    ticket_price_input = None
    try:
        ticket_price_input = driver.find_element(By.CSS_SELECTOR, "input.ticket-count")
    except Exception as exc:
        pass

    if not ticket_price_input is None:
        current_ticket_number = ""
        try:
            current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
        except Exception as exc:
            pass

        if len(current_ticket_number) > 0:
            if current_ticket_number == "0":
                try:
                    print("asssign ticket number:%s" % ticket_number_str)
                    ticket_price_input.clear()
                    ticket_price_input.send_keys(ticket_number_str)
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("asssign ticket number to ticket-count field Exception:")
                    print(exc)
                    try:
                        ticket_price_input.clear()
                        ticket_price_input.send_keys("1")
                        is_ticket_number_assigned = True
                    except Exception as exc2:
                        print("asssign ticket number to ticket-count still failed.")
                        pass
            else:
                # already assigned.
                is_ticket_number_assigned = True

    ticket_count = 0

    if is_ticket_number_assigned:
        el_ticket_count = None
        try:
            my_css_selector = "div.left-content > span.total-count"
            el_ticket_count = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if not el_ticket_count is None:
                tmp_ticket_count = el_ticket_count.text
                if len(tmp_ticket_count) > 0:
                    if tmp_ticket_count.isdigit():
                        ticket_count = int(tmp_ticket_count)
        except Exception as exc:
            pass

    if is_ticket_number_assigned and ticket_count==0:
        el_btn = None
        try:
            # this is "confirm"(確認) button.
            my_css_selector = "div.footer > div > div"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not el_btn is None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("varify site icon pressed.")
                    time.sleep(0.3)
            except Exception as exc:
                # use plan B
                if show_debug_message:
                    print("varify site icon pressed fail:", exc)
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
                '''
                pass
        else:
            if show_debug_message:
                print("varify site icon is None.")

    if is_ticket_number_assigned and ticket_count>0:
        el_btn = None
        try:
            # this is "add to cart"(加入購物籃)
            my_css_selector = "div.button-inner > div > div.button-text"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not el_btn is None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    time.sleep(0.3)
                    ret = True
                    print("shopping-cart icon pressed.")
            except Exception as exc:
                # use plan B
                if show_debug_message:
                    print("click on button fail:", exc)
                pass
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
                '''
        else:
            if show_debug_message:
                print("shopping-cart site icon is None.")

    return is_ticket_number_assigned

def urbtix_uncheck_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    el_checkbox_icon = None
    is_checkbox_checked = False
    try:
        my_css_selector = "div.quantity-inner > div.header > div.right > div.checkbox-wrapper > div.checkbox-icon"
        el_checkbox_icon = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_checkbox_icon is None:
            div_class_string = str(el_checkbox_icon.get_attribute('class'))
            if not div_class_string is None:
                if len(div_class_string) > 1:
                    if 'checked' in div_class_string:
                        is_checkbox_checked = True

    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    try:
        if is_checkbox_checked:
            el_checkbox_icon.click()
    except Exception as exc:
        if show_debug_message:
            print(exc)

        # force to click when exception.
        try:
            driver.execute_script("arguments[0].click();", el_checkbox_icon)
        except Exception as exc2:
            pass

        pass

def urbtix_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False

    is_price_assign_by_bot = False
    is_need_refresh = False

    # click price row.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    if show_debug_message:
        print("area_keyword:", area_keyword)

    if len(area_keyword) > 0:
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []

        for area_keyword_item in area_keyword_array:
            if show_debug_message:
                print("area_keyword_item for keyword:", area_keyword_item)
            is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, config_dict, area_keyword_item)
            if not is_price_assign_by_bot:
                break
    else:
        # empty keyword, match all.
        is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, config_dict, "")

    if show_debug_message:
        print("is_price_assign_by_bot:", is_price_assign_by_bot)

    # un-tested. disable refresh for now.
    is_need_refresh = False
    if is_need_refresh:
        try:
            driver.refresh()
        except Exception as exc:
            pass
    else:
        # now, alway not refresh.
        if config_dict["advanced"]["disable_adjacent_seat"]:
            urbtix_uncheck_adjacent_seat(driver, config_dict)

        # choose ticket.
        is_ticket_number_assigned = urbtix_ticket_number_auto_select(driver, config_dict)
        if show_debug_message:
            print("is_ticket_number_assigned:", is_ticket_number_assigned)

    return ret


# purpose: date auto select
def cityline_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "button.date-time-position"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            for row in area_list:
                row_is_enabled=True
                try:
                    if not row.is_enabled():
                        row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if show_debug_message:
                            print("row_text:", row_text)
                        is_match_area = util.is_row_match_keyword(date_keyword, row_text)
                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            if target_area.is_enabled():
                target_area.click()
                ret = True
        except Exception as exc:
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                ret = True
            except Exception as exc:
                pass
    else:
        # no target.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

    return ret

# purpose: area auto select
# return:
#   True: area block appear.
#   False: area block not appear.
# ps: return is successfully click on the price radio.
def cityline_area_auto_select(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.form-check"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                row_is_enabled=True
                try:
                    my_css_selector = "span.price-limited > span"
                    span_price_limited = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if not span_price_limited is None:
                        span_i18n_string = str(span_price_limited.get_attribute('data-i18n'))
                        if len(span_i18n_string) > 1:
                            if 'soldout' in span_i18n_string:
                                row_is_enabled=False
                except Exception as exc:
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                for row in formated_area_list:

                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                            row_text = ""

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "input[type=radio]"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            if not el_btn is None:
                if el_btn.is_enabled():
                    if not el_btn.is_selected():
                        el_btn.click()
                        is_price_assign_by_bot = True
                    else:
                        is_price_assign_by_bot = True
                    #print("bingo, click target_area radio")
        except Exception as exc:
            print("click target_area radio a link fail")
            print(exc)
            pass

    return is_need_refresh, is_price_assign_by_bot

#[TODO]:
# double check selected radio matched by keyword/keyword_and.
def cityline_area_selected_text(driver):
    ret = False

    return ret

def cityline_ticket_number_auto_select(driver, config_dict):
    selector_string = 'select.select-num'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, config_dict, by_method, selector_string)

def ibon_ticket_number_appear(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    selector_string = 'table.table > tbody > tr > td > select'
    by_method = By.CSS_SELECTOR

    form_select = None
    try:
        form_select = driver.find_element(by_method, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find ticket_number select fail:")
            print(exc)
        pass

    is_visible = False
    if not form_select is None:
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
    return is_visible

def ibon_ticket_number_auto_select(driver, config_dict):
    selector_string = 'table.table > tbody > tr > td > select'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, config_dict, by_method, selector_string)

def assign_ticket_number_by_select(driver, config_dict, by_method, selector_string):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ticket_number = str(config_dict["ticket_number"])

    form_select = None
    try:
        form_select = driver.find_element(by_method, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find ticket_number select fail")
            print(exc)
        pass

    select_obj = None
    if not form_select is None:
        is_visible = False
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_ticket_number_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 0:
                if row_text != "0":
                    # ticket assign.
                    is_ticket_number_assigned = True

        if not is_ticket_number_assigned:
            is_ticket_number_assigned = ticket_number_select_fill(driver, select_obj, ticket_number)
        else:
            if show_debug_message:
                print("ticket_number assigned by previous action.")

    return is_ticket_number_assigned

def cityline_purchase_button_press(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    date_auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    
    is_date_assign_by_bot = cityline_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    is_button_clicked = False
    if is_date_assign_by_bot:
        print("press purchase button")
        is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'button.purchase-btn')
        time.sleep(0.2)

    return is_button_clicked


def cityline_next_button_press(driver):
    ret = False

    el_nav = None
    el_btn = None
    try:
        el_nav = driver.find_element(By.CSS_SELECTOR, '.puchase-bottom')
        el_btn = driver.find_element(By.CSS_SELECTOR, '#expressPurchaseBtn')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if not el_btn is None and not el_nav is None:
        print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled():
                #el_btn.click()
                builder = ActionChains(driver)
                builder.move_to_element(el_nav)
                builder.click(el_btn)
                builder.perform()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass

    return ret


def cityline_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.

            # PS: cityline price default value is selected at the first option.
            is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, config_dict, "")


        # un-tested. disable refresh for now.
        is_need_refresh = False
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # choose ticket.
        is_ticket_number_assigned = cityline_ticket_number_auto_select(driver, config_dict)

        if show_debug_message:
            print("ticket_number:", config_dict["ticket_number"])
            print("is_ticket_number_assigned:", is_ticket_number_assigned)

        if is_ticket_number_assigned:
            auto_press_next_step_button = True
            if auto_press_next_step_button:
                if not is_price_assign_by_bot:
                    #[TODO]:
                    # double check selected radio matched by keyword/keyword_and.
                    # cityline_area_selected_text(driver)
                    pass

                if is_price_assign_by_bot:
                    for i in range(2):
                        click_ret = cityline_next_button_press(driver)
                        if click_ret:
                            break

def ibon_date_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    matched_blocks = None

    area_list = None
    try:
        my_css_selector = "div.single-content > div > div.row > div > div.tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find date-time rows fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            for row in area_list:
                # default is enabled.
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if not el_btn is None:
                        if not el_btn.is_enabled():
                            #print("row's button disabled!")
                            row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    is_date_assign_by_bot = False
    if not target_area is None:
        is_button_clicked = False
        for i in range(3):
            el_btn = None
            try:
                my_css_selector = "button.btn"
                el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not el_btn is None:
                try:
                    if el_btn.is_enabled():
                        el_btn.click()
                        print("buy icon pressed.")
                        is_button_clicked = True
                except Exception as exc:
                    pass
                    # use plan B
                    '''
                    try:
                        print("force to click by js.")
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass
                    '''
            if is_button_clicked:
                break
        is_date_assign_by_bot = is_button_clicked

    else:
        # no target to click.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_date_assign_by_bot

def ibon_area_auto_select(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    # when avaiable seat under this count, check seat text content.
    CONST_DETECT_SEAT_ATTRIBUTE_UNDER_ROW_COUNT = 20

    is_price_assign_by_bot = False
    is_need_refresh = False

    area_list = None
    try:
        #print("try to find cityline area block")
        #my_css_selector = "div.col-md-5 > table > tbody > tr[onclick=\"onTicketArea(this.id)\"]"
        my_css_selector = "div.col-md-5 > table > tbody > tr:not(.disabled)"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_item:", area_keyword_item)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if '已售完' in row_text:
                        row_text = ""

                    if 'disabled' in row_html:
                        row_text = ""

                    if 'sold-out' in row_html:
                        row_text = ""

                # clean the buttom description row.
                if len(row_text) > 0:
                    if row_text == "座位已被選擇":
                        row_text=""
                    if row_text == "座位已售出":
                        row_text=""
                    if row_text == "舞台區域":
                        row_text=""

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                # check ticket count when amount is few, because of it spent a lot of time at parsing element.
                if len(row_text) > 0:
                    is_seat_remaining_checking = False
                    # PS: when user query with keyword, but when selected row is too many, not every row to check remaing.
                    #     may cause the matched keyword row ticket seat under user target ticket number.
                    if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        if len(formated_area_list)==0:
                            is_seat_remaining_checking = True

                    if area_list_count <= CONST_DETECT_SEAT_ATTRIBUTE_UNDER_ROW_COUNT:
                        is_seat_remaining_checking = True

                    if is_seat_remaining_checking:
                        try:
                            area_seat_el = row.find_element(By.CSS_SELECTOR, 'td.action')
                            if not area_seat_el is None:
                                seat_text = area_seat_el.text
                                if seat_text is None:
                                    seat_text = ""
                                if seat_text.isdigit():
                                    seat_int = int(seat_text)
                                    if seat_int < config_dict["ticket_number"]:
                                        # skip this row.
                                        if show_debug_message:
                                            print("skip not enought ticket number area at row_text:", row_text)
                                        row_text = ""
                        except Exception as exc:
                            if show_debug_message:
                                print(exc)
                            pass

                if len(row_text) > 0:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    matched_blocks = []
    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break


            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    if not matched_blocks is None:
        if len(matched_blocks) == 0:
            is_need_refresh = True
            if show_debug_message:
                print("matched_blocks is empty, is_need_refresh")

    if not target_area is None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot

def ibon_allow_not_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = 'div.not-consecutive > div.custom-control > span > input[type="checkbox"]'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ibon seat checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def ibon_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    # click price row.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    if show_debug_message:
        print("area_keyword:", area_keyword)

    is_need_refresh = False

    if len(area_keyword) > 0:
        area_keyword_array = []
        try:
            area_keyword_array = json.loads("["+ area_keyword +"]")
        except Exception as exc:
            area_keyword_array = []

        for area_keyword_item in area_keyword_array:
            is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, config_dict, area_keyword_item)
            if not is_need_refresh:
                break
            else:
                print("is_need_refresh for keyword:", area_keyword_item)
    else:
        # empty keyword, match all.
        is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, config_dict, area_keyword)

    if show_debug_message:
        print("is_need_refresh:", is_need_refresh)

    if is_need_refresh:
        try:
            driver.refresh()
        except Exception as exc:
            pass

        if config_dict["advanced"]["auto_reload_page_interval"] > 0:
            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_price_assign_by_bot

def ibon_purchase_button_press(driver):
    is_button_clicked = press_button(driver, By.CSS_SELECTOR, '#ticket-wrap > a.btn')
    return is_button_clicked

def assign_text(driver, by, query, val, overwrite = False, submit=False, overwrite_when = ""):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_visible = False

    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if not el_text is None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    is_visible = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

    is_text_sent = False
    if is_visible:
        try:
            inputed_text = el_text.get_attribute('value')
            if not inputed_text is None:
                is_do_keyin = False
                if len(inputed_text) == 0:
                    is_do_keyin = True
                else:
                    if inputed_text == val:
                        is_text_sent = True
                    else:
                        if len(overwrite_when) > 0:
                            if overwrite_when == inputed_text:
                                overwrite = True
                        if overwrite:
                            is_do_keyin = True

                if is_do_keyin:
                    if len(inputed_text) > 0:
                        builder = ActionChains(driver)
                        builder.move_to_element(el_text)
                        builder.click(el_text)
                        if platform.system() == 'Darwin':
                            builder.key_down(Keys.COMMAND)
                        else:
                            builder.key_down(Keys.CONTROL)
                        builder.send_keys("a")
                        if platform.system() == 'Darwin':
                            builder.key_up(Keys.COMMAND)
                        else:
                            builder.key_up(Keys.CONTROL)
                        builder.send_keys(val)
                        if submit:
                            builder.send_keys(Keys.ENTER)
                        builder.perform()
                    else:
                        el_text.click()
                        el_text.send_keys(val)
                        if submit:
                            el_text.send_keys(Keys.ENTER)
                    is_text_sent = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_text_sent

def facebook_login(driver, account, password):
    is_email_sent = assign_text(driver, By.CSS_SELECTOR, '#email', account)
    is_password_sent = False
    if is_email_sent:
        is_password_sent = assign_text(driver, By.CSS_SELECTOR, '#pass', password, submit=True)
    return is_password_sent

def kktix_login(driver, account, password):
    ret = False
    # for like human.
    time.sleep(5)

    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#user_login')
    except Exception as exc:
        pass

    is_visible = False
    if not el_email is None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if not inputed_text is None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#user_password')
        except Exception as exc:
            pass

    is_password_sent = False
    if not el_pass is None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def cityline_login(driver, account, password):
    is_email_sent = assign_text(driver, By.CSS_SELECTOR, 'input[type="text"]', account, submit=True)

    # press "click here" use password to login.
    if is_email_sent:
        is_click_here_pressed = press_button(driver, By.CSS_SELECTOR,'.otp-box > ul > li:nth-child(3) > a')

    is_password_sent = False
    if is_email_sent:
        is_password_sent = assign_text(driver, By.CSS_SELECTOR, 'div > input[type="password"]', password, submit=True)

    return is_password_sent

def urbtix_login(driver, account, password):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, 'input[name="loginId"]')
    except Exception as exc:
        #print("find #email fail")
        #print(exc)
        pass

    is_visible = False
    if not el_email is None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if not inputed_text is None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        except Exception as exc:
            pass

    is_password_sent = False
    if not el_pass is None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            is_password_sent = True
        except Exception as exc:
            pass

    el_btn = None
    if is_password_sent:
        try:
            el_btn = driver.find_element(By.CSS_SELECTOR, '.login-button')
            if not el_btn is None:
                el_btn.click()
        except Exception as exc:
            pass

    return ret

def kham_login(driver, account, password):
    ret = False
    el_email = None
    try:
        my_css_selector = '#ACCOUNT'
        el_email = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    is_visible = False
    if not el_email is None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if not inputed_text is None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            my_css_selector = 'table.login > tbody > tr > td > input[type="password"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_password_sent = False
    if not el_pass is None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    if is_password_sent:
        is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.memberContent > p > a > button.red')

    ret = is_password_sent

    return ret

def ticket_login(driver, account, password):
    ret = False
    el_email = None
    try:
        my_css_selector = 'input[cname="帳號"]'
        el_email = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    is_visible = False
    if not el_email is None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if not inputed_text is None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            my_css_selector = 'input[cname="密碼"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_password_sent = False
    if not el_pass is None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    if is_password_sent:
        is_button_clicked = press_button(driver, By.CSS_SELECTOR,'input[value="登入"]')

    ret = is_password_sent

    return ret

def udn_login(driver, account, password):
    is_logined = False

    el_login_li = None
    try:
        my_css_selector = '#LoginLI'
        el_login_li = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_login_li is None:
            li_html = el_login_li.get_attribute('outerHTML')
            if 'display: none' in li_html:
                is_logined = True
    except Exception as exc:
        pass

    is_password_sent = False
    if not is_logined:
        if not el_login_li is None:
            try:
                el_login_li.click()
            except Exception as exc:
                print(exc)
                try:
                    driver.set_script_timeout(1)
                    driver.execute_script("doLoginRWD();")
                except Exception as exc2:
                    print(exc2)
                    pass

        is_email_sent = assign_text(driver, By.CSS_SELECTOR, '#ID', account)
        if is_email_sent:
            is_password_sent = assign_text(driver, By.CSS_SELECTOR, '#password', password, submit=False)
    return is_password_sent


def hkticketing_login(driver, account, password):
    ret = False
    el_email = None
    try:
        my_css_selector = 'div#myTick2Col > div.formMod2Col > div.formModule > div.loginContentContainer > input.borInput'
        el_email = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find_element exception")
        #print(exc)
        pass

    is_visible = False
    if not el_email is None:
        try:
            if el_email.is_enabled():
                is_visible = True
            else:
                el_email.click()
        except Exception as exc:
            pass
    else:
        #print("account field is None.")
        pass

    is_email_sent = False
    if is_visible:
        try:
            # PS: this is special case...
            el_email.click()

            inputed_text = el_email.get_attribute('value')
            if not inputed_text is None:
                if len(inputed_text) == 0:
                    #print("send account text:", account)
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            my_css_selector = 'div.loginContentContainer > input[type="password"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_password_sent = False
    if not el_pass is None:
        try:
            if el_pass.is_enabled():
                el_pass.click()
                inputed_text = el_pass.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            #print("send password text:", password)
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
            else:
                el_pass.click()
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def play_sound_while_ordering(config_dict):
    app_root = util.get_app_root()
    captcha_sound_filename = os.path.join(app_root, config_dict["advanced"]["play_sound"]["filename"].strip())
    util.play_mp3_async(captcha_sound_filename)

# purpose: check alert poped.
# PS: current version not enable...
def check_pop_alert(driver):
    is_alert_popup = False

    # https://stackoverflow.com/questions/57481723/is-there-a-change-in-the-handling-of-unhandled-alert-in-chromedriver-and-chrome
    default_close_alert_text = [""]
    if len(default_close_alert_text) > 0:
        try:
            alert = None
            if not driver is None:
                #alert = driver.switch_to.alert
                alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
            if not alert is None:
                alert_text = str(alert.text)
                if not alert_text is None:
                    is_match_auto_close_text = False
                    for txt in default_close_alert_text:
                        if len(txt) > 0:
                            if txt in alert.text:
                                is_match_auto_close_text = True
                        else:
                            is_match_auto_close_text = True
                    #print("is_match_auto_close_text:", is_match_auto_close_text)
                    #print("alert3 text:", alert.text)

                    if is_match_auto_close_text:
                        alert.accept()
                        print("alert3 accepted")

                    is_alert_popup = True
            else:
                print("alert3 not detected")
        except NoAlertPresentException as exc1:
            #logger.error('NoAlertPresentException for alert')
            pass
        except NoSuchWindowException:
            pass
        except Exception as exc:
            #logger.error('Exception2 for alert')
            #logger.error(exc, exc_info=True)
            pass

    return is_alert_popup

def list_all_cookies(driver):
    cookies_dict = {}
    if not driver is None:
        try:
            all_cookies=driver.get_cookies();
            for cookie in all_cookies:
                cookies_dict[cookie['name']] = cookie['value']
        except Exception as e:
            pass
    return cookies_dict
    #print(cookies_dict)

def set_non_browser_cookies(driver, url, Captcha_Browser):
    if not driver is None:
        domain_name = url.split('/')[2]
        #PS: need set cookies once, if user change domain.
        if not Captcha_Browser is None:
            try:
                Captcha_Browser.set_cookies(driver.get_cookies())
            except Exception as e:
                pass
            Captcha_Browser.set_domain(domain_name)

def ticketmaster_parse_zone_info(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    mapSelectArea = None
    try:
        my_css_selector = '#mapSelectArea'
        mapSelectArea = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        if show_debug_message:
            print('fail to find my_css_selector:', my_css_selector)
            #print("find table#ticketPriceList fail", exc)

    if not mapSelectArea is None:
        mapSelectArea_html = ""
        try:
            mapSelectArea_html = mapSelectArea.get_attribute('innerHTML')
        except Exception as exc:
            mapSelectArea_html = ""
            if show_debug_message:
                print(exc)

        zone_string = ""
        tag_start = "var zone ="
        tag_end = "fieldImageType"
        if tag_start in mapSelectArea_html and tag_end in mapSelectArea_html:
            if show_debug_message:
                print('found zone info!')
            zone_string = mapSelectArea_html.split(tag_start)[1]
            zone_string = zone_string.split(tag_end)[0]
            zone_string = zone_string.strip()
            if zone_string[-1:] == "\n":
                zone_string=zone_string[:-1]
            zone_string = zone_string.strip()
            if zone_string[-1:] == ",":
                zone_string=zone_string[:-1]
            if show_debug_message:
                #print('found zone info string:', zone_string)
                pass

        if len(zone_string) > 0:
            zone_info = {}
            try:
                zone_info = json.loads(zone_string)
                if show_debug_message:
                    #print("zone_info", zone_info)
                    pass
                if not zone_info is None:
                    ticketmaster_area_auto_select(driver, config_dict, zone_info)
            except Exception as exc:
                if show_debug_message:
                    print(exc)

def ticketmaster_get_ticketPriceList(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    div_mapContainer = None
    try:
        my_css_selector = '#mapContainer'
        div_mapContainer = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        if show_debug_message:
            print('fail to find my_css_selector:', my_css_selector)
            #print("find table#ticketPriceList fail", exc)

    table_select = None
    if not div_mapContainer is None:
        is_loading = False

        # check is loading.
        div_loadingmap = None
        try:
            my_css_selector = '#loadingmap'
            div_loadingmap = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if  not div_loadingmap is None:
                is_loading = True
        except Exception as exc:
            if show_debug_message:
                print('fail to find my_css_selector:', my_css_selector)
                #print("find table#ticketPriceList fail", exc)

        if not is_loading:
            try:
                my_css_selector = '#ticketPriceList'
                table_select = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                if show_debug_message:
                    print('fail to find my_css_selector:', my_css_selector)
                    #print("find table#ticketPriceList fail", exc)

            if table_select is None:
                ticketmaster_parse_zone_info(driver, config_dict)

    return table_select

def ticketmaster_assign_ticket_number(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    table_select = ticketmaster_get_ticketPriceList(driver, config_dict)

    select_obj = None
    if not table_select is None:
        form_select = None
        if show_debug_message:
            print('found table#ticketPriceList, start find select')
        try:
            my_css_selector = 'select'
            form_select = table_select.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            if show_debug_message:
                print('my_css_selector:', my_css_selector)
                print("find form-select fail", exc)
            pass

        if not form_select is None:
            if show_debug_message:
                print('found ticket number select.')

            is_visible = False
            try:
                if form_select.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass
            if is_visible:
                try:
                    select_obj = Select(form_select)
                except Exception as exc:
                    pass

    is_ticket_number_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if show_debug_message:
                print('row_text:', row_text)

            if len(row_text) > 0:
                if row_text != "0":
                    if row_text.isnumeric():
                        # ticket assign.
                        is_ticket_number_assigned = True

    if show_debug_message:
        print('is_ticket_number_assigned:', is_ticket_number_assigned)


    # must wait select object ready to assign ticket number.
    if not is_ticket_number_assigned:
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = ticket_number_select_fill(driver, select_obj, ticket_number)

        # must wait ticket number assign to focus captcha.
        if is_ticket_number_assigned:
            is_button_clicked = press_button(driver, By.CSS_SELECTOR,'#autoMode')

def ticketmaster_captcha(driver, config_dict, ocr, Captcha_Browser, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    for i in range(2):
        is_finish_checkbox_click = check_checkbox(driver, By.CSS_SELECTOR, '#TicketForm_agree')
        if is_finish_checkbox_click:
            break

    if not config_dict["ocr_captcha"]["enable"]:
        tixcraft_keyin_captcha_code(driver)
    else:
        previous_answer = None
        last_url, is_quit_bot = get_current_url(driver)
        for redo_ocr in range(99):
            is_need_redo_ocr, previous_answer, is_form_sumbited = tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name)
            if is_form_sumbited:
                # start next loop.
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break

            current_url, is_quit_bot = get_current_url(driver)
            if current_url != last_url:
                break

def tixcraft_main(driver, url, config_dict, ocr, Captcha_Browser):
    global tixcraft_dict
    if not 'tixcraft_dict' in globals():
        tixcraft_dict = {}
        tixcraft_dict["fail_list"]=[]
        tixcraft_dict["fail_promo_list"]=[]
        tixcraft_dict["start_time"]=None
        tixcraft_dict["done_time"]=None
        tixcraft_dict["elapsed_time"]=None
        tixcraft_dict["is_popup_checkout"] = False
        tixcraft_dict["area_retry_count"]=0
        tixcraft_dict["played_sound_ticket"] = False
        tixcraft_dict["played_sound_order"] = False

    tixcraft_home_close_window(driver)

    home_url_list = ['https://tixcraft.com/'
    ,'https://indievox.com/'
    ,'https://www.indievox.com/'
    ,'https://teamear.tixcraft.com/activity'
    ,'https://ticketmaster.sg/'
    ,'https://ticketmaster.com/'
    ]
    for each_url in home_url_list:
        if each_url == url:
            if config_dict["ocr_captcha"]["enable"]:
                set_non_browser_cookies(driver, url, Captcha_Browser)
                pass
            break

    # special case for same event re-open, redirect to user's homepage.
    if 'https://tixcraft.com/' == url or 'https://tixcraft.com/activity' == url:
        if "/ticket/area/" in config_dict["homepage"]:
            if len(config_dict["homepage"].split('/'))==7:
                try:
                    driver.get(config_dict["homepage"])
                except Exception as e:
                    pass

    if "/activity/detail/" in url:
        tixcraft_dict["start_time"] = time.time()
        is_redirected = tixcraft_redirect(driver, url)

    is_date_selected = False
    if "/activity/game/" in url:
        tixcraft_dict["start_time"] = time.time()
        if config_dict["date_auto_select"]["enable"]:
            domain_name = url.split('/')[2]
            is_date_selected = tixcraft_date_auto_select(driver, url, config_dict, domain_name)

    if '/artist/' in url and 'ticketmaster.com' in url:
        tixcraft_dict["start_time"] = time.time()
        if len(url.split('/'))==6:
            if config_dict["date_auto_select"]["enable"]:
                domain_name = url.split('/')[2]
                is_date_selected = ticketmaster_date_auto_select(driver, url, config_dict, domain_name)

    # choose area
    if '/ticket/area/' in url:
        domain_name = url.split('/')[2]
        if config_dict["area_auto_select"]["enable"]:
            if not 'ticketmaster' in domain_name:
                # for tixcraft
                tixcraft_area_auto_select(driver, url, config_dict)
                tixcraft_dict["area_retry_count"]+=1
                #print("count:", tixcraft_dict["area_retry_count"])
                if tixcraft_dict["area_retry_count"] >= (60 * 15):
                    # Cool-down
                    tixcraft_dict["area_retry_count"] = 0
                    time.sleep(5)
            else:
                # area auto select is too difficult, skip in this version.
                tixcraft_dict["fail_promo_list"] = ticketmaster_promo(driver, config_dict, tixcraft_dict["fail_promo_list"])
                ticketmaster_assign_ticket_number(driver, config_dict)
    else:
        tixcraft_dict["fail_promo_list"] = []
        tixcraft_dict["area_retry_count"]=0

    # https://ticketmaster.sg/ticket/check-captcha/23_blackpink/954/5/75
    if '/ticket/check-captcha/' in url:
        domain_name = url.split('/')[2]
        ticketmaster_captcha(driver, config_dict, ocr, Captcha_Browser, domain_name)

    if '/ticket/verify/' in url:
        tixcraft_dict["fail_list"] = tixcraft_verify(driver, config_dict, tixcraft_dict["fail_list"])
    else:
        tixcraft_dict["fail_list"] = []

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        domain_name = url.split('/')[2]
        tixcraft_ticket_main(driver, config_dict, ocr, Captcha_Browser, domain_name)
        tixcraft_dict["done_time"] = time.time()

        if config_dict["advanced"]["play_sound"]["ticket"]:
            if not tixcraft_dict["played_sound_ticket"]:
                play_sound_while_ordering(config_dict)
            tixcraft_dict["played_sound_ticket"] = True
    else:
        tixcraft_dict["played_sound_ticket"] = False

    if '/ticket/order' in url:
        tixcraft_dict["done_time"] = time.time()

    is_quit_bot = False
    if '/ticket/checkout' in url:
        if not tixcraft_dict["start_time"] is None:
            if not tixcraft_dict["done_time"] is None:
                bot_elapsed_time = tixcraft_dict["done_time"] - tixcraft_dict["start_time"]
                if tixcraft_dict["elapsed_time"] != bot_elapsed_time:
                    print("bot elapsed time:", "{:.3f}".format(bot_elapsed_time))
                tixcraft_dict["elapsed_time"] = bot_elapsed_time

        if config_dict["advanced"]["headless"]:
            if not tixcraft_dict["is_popup_checkout"]:
                domain_name = url.split('/')[2]
                checkout_url = "https://%s/ticket/checkout" % (domain_name)
                print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)
                tixcraft_dict["is_popup_checkout"] = True
                is_quit_bot = True

        if config_dict["advanced"]["play_sound"]["order"]:
            if not tixcraft_dict["played_sound_order"]:
                play_sound_while_ordering(config_dict)
            tixcraft_dict["played_sound_order"] = True
    else:
        tixcraft_dict["is_popup_checkout"] = False
        tixcraft_dict["played_sound_order"] = False

    return is_quit_bot

def kktix_paused_main(driver, url, config_dict):
    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        kktix_account = config_dict["accounts"]["kktix_account"]
        kktix_password = config_dict["accounts"]["kktix_password"].strip()
        if len(kktix_account) > 4:
            kktix_login(driver, kktix_account, kktix_password)
        is_url_contain_sign_in = True

    # PS: after test, this still not popup reCaptcha.
    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            # part 1: check recaptch  div.
            recaptcha_div = None
            try:
                recaptcha_div = driver.find_element(By.CSS_SELECTOR, '.event-captcha-info')
            except Exception as exc:
                pass

            if not recaptcha_div is None:
                select_query = '.ng-hide'
                class_name = 'ng-hide'
                remove_class_tag_by_selector(driver, select_query, class_name)
                select_query = '.btn-disabled-alt'
                class_name = 'btn-disabled-alt'
                remove_class_tag_by_selector(driver, select_query, class_name)
                select_query = 'button[disabled="disabled"]'
                class_name = 'disabled'
                remove_attribute_tag_by_selector(driver, select_query, class_name)

def kktix_main(driver, url, config_dict):
    global kktix_dict
    if not 'kktix_dict' in globals():
        kktix_dict = {}
        kktix_dict["fail_list"]=[]
        kktix_dict["start_time"]=None
        kktix_dict["done_time"]=None
        kktix_dict["elapsed_time"]=None
        kktix_dict["is_popup_checkout"] = False
        kktix_dict["played_sound_ticket"] = False
        kktix_dict["played_sound_order"] = False

    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        kktix_account = config_dict["accounts"]["kktix_account"]
        kktix_password = config_dict["accounts"]["kktix_password"].strip()
        if len(kktix_account) > 0:
            kktix_login(driver, kktix_account, kktix_password)
        is_url_contain_sign_in = True

    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            kktix_dict["start_time"] = time.time()

            # call api, cuase add access log. DISABLE it.
            # kktix_reg_auto_reload(driver, url, config_dict)

            is_dom_ready = False
            is_finish_checkbox_click = False
            is_dom_ready, is_finish_checkbox_click = kktix_check_agree_checkbox(driver, config_dict)

            if not is_dom_ready:
                # reset answer fail list.
                kktix_dict["fail_list"] = []
                kktix_dict["played_sound_ticket"] = False
            else:
                # check is able to buy.
                if config_dict["kktix"]["auto_fill_ticket_number"]:
                    kktix_dict["fail_list"], kktix_dict["played_sound_ticket"] = kktix_reg_new_main(driver, config_dict, kktix_dict["fail_list"], kktix_dict["played_sound_ticket"])
                    kktix_dict["done_time"] = time.time()
        else:
            is_event_page = False
            if '/events/' in url:
                # ex: https://xxx.kktix.cc/events/xxx-copy-1
                if len(url.split('/'))<=5:
                    is_event_page = True

            if is_event_page:
                if config_dict["kktix"]["auto_press_next_step_button"]:
                    # pass switch check.
                    #print("should press next here.")
                    kktix_events_press_next_button(driver)

            # reset answer fail list.
            kktix_dict["fail_list"] = []
            kktix_dict["played_sound_ticket"] = False

    is_kktix_got_ticket = False
    if '/events/' in url and '/registrations/' in url and "-" in url:
        if not '/registrations/new' in url:
            if not 'https://kktix.com/users/sign_in?' in url:
                is_kktix_got_ticket = True

    if is_kktix_got_ticket:
        if '/events/' in config_dict["homepage"] and '/registrations/' in config_dict["homepage"] and "-" in config_dict["homepage"]:
            # do nothing when second time come in.
            if len(url.split('/'))>=7:
                if len(config_dict["homepage"].split('/'))>=7:
                    # match event code.
                    if url.split('/')[4]==config_dict["homepage"].split('/')[4]:
                        # break loop.
                        is_kktix_got_ticket = False

    is_quit_bot = False
    if is_kktix_got_ticket:
        if not kktix_dict["start_time"] is None:
            if not kktix_dict["done_time"] is None:
                bot_elapsed_time = kktix_dict["done_time"] - kktix_dict["start_time"]
                if kktix_dict["elapsed_time"] != bot_elapsed_time:
                    print("bot elapsed time:", "{:.3f}".format(bot_elapsed_time))
                kktix_dict["elapsed_time"] = bot_elapsed_time

        if config_dict["advanced"]["play_sound"]["order"]:
            if not kktix_dict["played_sound_order"]:
                play_sound_while_ordering(config_dict)

        kktix_dict["played_sound_order"] = True

        if config_dict["advanced"]["headless"]:
            if not kktix_dict["is_popup_checkout"]:
                kktix_account = config_dict["accounts"]["kktix_account"]
                kktix_password = config_dict["accounts"]["kktix_password"].strip()

                print("基本資料(或實名制)網址:", url)
                if len(kktix_account) > 0:
                    print("搶票成功, 帳號:", kktix_account)

                    script_name = "chrome_tixcraft"
                    if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_NODRIVER:
                        script_name = "nodriver_tixcraft"
                    threading.Thread(target=util.launch_maxbot, args=(script_name,"", url, kktix_account, kktix_password,"","false",)).start()

                is_event_page = False
                if len(url.split('/'))>=7:
                    is_event_page = True
                if is_event_page:
                    confirm_clicked = kktix_confirm_order_button(driver)
                    if confirm_clicked:
                        domain_name = url.split('/')[2]
                        checkout_url = "https://%s/account/orders" % (domain_name)
                        print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                        webbrowser.open_new(checkout_url)

                kktix_dict["is_popup_checkout"] = True
                is_quit_bot = True
    else:
        kktix_dict["is_popup_checkout"] = False
        kktix_dict["played_sound_order"] = False

    return is_quit_bot

def fami_login(driver, account, password):
    is_email_sent = assign_text(driver, By.CSS_SELECTOR, '#usr_act', account)
    is_password_sent = False
    if is_email_sent:
        is_password_sent = assign_text(driver, By.CSS_SELECTOR, '#usr_pwd', password, submit=True)
    return is_password_sent

def famiticket_main(driver, url, config_dict):
    global fami_dict
    if not 'fami_dict' in globals():
        fami_dict = {}
        fami_dict["fail_list"] = []
        fami_dict["last_activity"]=""

    if '/Home/User/SignIn' in url:
        fami_account = config_dict["accounts"]["fami_account"]
        fami_password = config_dict["accounts"]["fami_password"].strip()
        if len(fami_account) > 4:
            fami_login(driver, fami_account, fami_password)

    if '/Home/Activity/Info/' in url:
        fami_dict["last_activity"] = url
        fami_activity(driver)
        fami_dict["fail_list"] = fami_verify(driver, config_dict, fami_dict["fail_list"])
    else:
        fami_dict["fail_list"] = []

    if '/Sales/Home/Index/' in url:
        if config_dict["date_auto_select"]["enable"]:
            is_date_assign_by_bot = fami_home_auto_select(driver, config_dict, fami_dict["last_activity"])


def urbtix_performance_confirm_dialog_popup(driver):
    ret = False

    el_div = None
    try:
        el_div = driver.find_element(By.CSS_SELECTOR, 'div.notification-confirm-btn > div.button-text')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    if not el_div is None:
        print("bingo, found notification-confirm-btn")
        is_visible = False
        try:
            if el_div.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                el_div.click()
                ret = True
            except Exception as exc:
                # use plan B
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_div)
                    ret = True
                except Exception as exc:
                    pass
                '''
                pass

        if ret:
            time.sleep(0.4)

    return ret

# PS: NOW not able to use, due to open question not able to fill by stupid program.
def get_urbtix_survey_answer_by_question(question_text):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    question_text = question_text.replace('  ',' ')
    question_text = util.full2half(question_text)

    seq = 0
    if '第' in question_text and '個' in question_text:
        temp_string = question_text.split('第')[1]
        seq_string  = temp_string.split('個')[0]
        if len(seq_string) > 0:
            if seq_string.isdigit():
                seq = int(seq_string)
            else:
                tmp_seq =  util.chinese_numeric_to_int(seq_string)
                if not tmp_seq is None:
                    seq = tmp_seq

    if show_debug_message:
        print("seq:", seq)

    direction = "left"
    if '右起' in question_text:
        direction = "right"
    if '由右' in question_text:
        direction = "right"
    if '從右' in question_text:
        direction = "right"
    if '自右' in question_text:
        direction = "right"
    if '右算' in question_text:
        direction = "right"
    if '右邊' in question_text:
        direction = "right"
    if ' from the RIGHT' in question_text:
        direction = "right"

    if '有多少個' in question_text:
        direction = "count"
    if '有幾個' in question_text:
        direction = "count"
    if 'How many ' in question_text:
        direction = "count"

    if show_debug_message:
        print("direction:", direction)

    question_text_formated = question_text
    question_text_formated = question_text_formated.replace('「','')
    question_text_formated = question_text_formated.replace('」','')
    question_text_formated = question_text_formated.replace(' ','')
    question_text_formated = question_text_formated.replace('-','')
    question_text_formated = question_text_formated.replace('_','')

    # format question.
    question_text_formated = question_text_formated.replace(';','')
    question_text_formated = question_text_formated.replace('.','')
    question_text_formated = question_text_formated.replace(':','')
    question_text_formated = question_text_formated.replace(',','')

    question_answer_char = ""
    option_text_string = util.find_continuous_text(question_text_formated)

    if show_debug_message:
        print("option_text_string:", option_text_string)

    if direction in ['left','right']:
        if seq > 0:
            if len(option_text_string) > 1:
                if seq <= len(option_text_string):
                    if direction == "left":
                        question_answer_char = option_text_string[seq-1:seq]
                    if direction == "right":
                        question_answer_char = option_text_string[len(option_text_string)-seq:len(option_text_string)-seq+1]

    if direction == "count":
        if '個' in question_text_formated:
            count_target = None
            count_answer = 0

            tmp_seq = question_text_formated.split('個')[1]
            if len(tmp_seq) > 0:
                count_target_string = tmp_seq[:1]
                if len(count_target_string) > 0:
                    if count_target_string.isdigit():
                        count_target = int(count_target_string)
                    else:
                        count_target =  util.chinese_numeric_to_int(count_target_string)

            if not count_target is None:
                for char in option_text_string:
                    if char == str(count_target):
                        count_answer += 1

            question_answer_char = str(count_answer)
            if show_debug_message:
                print("count_target:", count_target)
                print("count_answer:", count_answer)

    if show_debug_message:
        print("question_answer_char text:", question_answer_char)

    return question_answer_char, direction

# PS: due to open-ended question, disable this feature now.
def urbtix_auto_survey(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    questions_div = None
    try:
        questions_div = driver.find_elements(By.CSS_SELECTOR, 'div.modal-content > div.content > div.questions > div.question-item')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    is_radio_clicked = False
    fill_question_count = 0

    if not questions_div is None:
        quetions_count = len(questions_div)
        if show_debug_message:
            print("quetions_count:", quetions_count)

        try:
            for each_question_div in questions_div:
                each_question_ask_div = each_question_div.find_element(By.CSS_SELECTOR, 'div.titles > div')
                if not each_question_ask_div is None:
                    question_text = each_question_ask_div.text
                    if question_text is None:
                        question_text = ""
                    if show_debug_message:
                        print("questions_div text:", question_text)

                    question_answer_char, question_direction = get_urbtix_survey_answer_by_question(question_text)
                    each_option_items_div = each_question_div.find_elements(By.CSS_SELECTOR, 'div.options > div.option-item')
                    if not each_option_items_div is None:
                        question_answered = False
                        for each_option_div in each_option_items_div:
                            option_content_div = each_option_div.find_element(By.CSS_SELECTOR, 'div.content-list')
                            if not option_content_div is None:
                                option_content_div_text = option_content_div.text
                                if option_content_div is None:
                                    option_content_div=""
                                option_content_div_text = option_content_div_text.strip()
                                option_content_div_text = util.full2half(option_content_div_text)

                                if question_direction in ['left','right']:
                                    for answer_item in util.synonym_dict(question_answer_char):
                                        if answer_item in option_content_div_text:
                                            is_radio_clicked = press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", answer_item)
                                                question_answered = True
                                                break

                                if question_direction == "count":
                                    for answer_item in util.synonym_dict(question_answer_char):
                                        if answer_item in option_content_div_text:
                                            is_radio_clicked = press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", answer_item)
                                                question_answered = True
                                                break

                                    if question_answer_char == '0':
                                        is_match_none = False
                                        if '沒有' in option_content_div_text:
                                            is_match_none = True
                                        if 'LESS THEN ONE' in option_content_div_text.upper():
                                            is_match_none = True
                                        if is_match_none:
                                            is_radio_clicked = press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", '沒有')
                                                question_answered = True
                                                break

                                    int_answer_char = int(question_answer_char)
                                    if int_answer_char > 1:
                                        for i in range(int_answer_char-1):
                                            for answer_item in util.synonym_dict(str(i+1)):
                                                is_match_more_then = False
                                                if answer_item + '個或以上' in option_content_div_text:
                                                    is_match_more_then = True
                                                if answer_item + '個以上' in option_content_div_text:
                                                    is_match_more_then = True
                                                if '多於' in option_content_div_text and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if '更多' in option_content_div_text and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if 'MORE THEN' in option_content_div_text.upper() and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if is_match_more_then:
                                                    is_radio_clicked = press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                                    if is_radio_clicked:
                                                        if show_debug_message:
                                                            print("fill answer:", answer_item + '個或以上')
                                                        question_answered = True
                                                        break
                                            if question_answered:
                                                break

                                if question_answered:
                                    fill_question_count += 1
                                    break

        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if show_debug_message:
            print("fill_question_count:", fill_question_count)

    #if is_radio_clicked and fill_question_count>=3:
    if is_radio_clicked and fill_question_count>=2:
        questions_remain_div = None
        questions_remain_text = ""
        try:
            questions_remain_div = driver.find_element(By.CSS_SELECTOR, 'div.surplus-questions-number')
            if not questions_remain_div is None:
                questions_remain_text = questions_remain_div.text
                questions_remain_text = questions_remain_text.strip()
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if show_debug_message:
            #print("questions_remain_text:", questions_remain_text)
            pass

        if questions_remain_text == "0" or questions_remain_text == "":
            is_button_clicked = False
            #is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'div.button-wrapper > div.button-text-multi-lines > div')

            # Message: Element <div class="text-tc"> is not clickable at point (351,566) because another element <div class="modal-wrapper landing-question"> obscures it
            btn_submit = None
            try:
                my_css_selector = 'div.landing-question > div.modal-inner > div.modal-content > div.content > div.button-container > div.button-and-number > div.button-wrapper > div.button-text-multi-lines > div.text-tc'
                btn_submit = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                if not btn_submit.is_enabled():
                    btn_submit = None
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

            if not btn_submit is None:
                try:
                    if show_debug_message:
                        print("start to click btn.")
                    btn_submit.click()
                    is_button_clicked = True
                    time.sleep(1.0)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass


def urbtix_main(driver, url, config_dict):
    # http://msg.urbtix.hk
    waiting_for_access_url = ['/session/landing-timer/','msg.urbtix.hk','busy.urbtix.hk']
    for waiting_url in waiting_for_access_url:
        if waiting_url in url:
            try:
                driver.get('https://www.urbtix.hk/')
            except Exception as exec1:
                pass
            pass
            # 刷太快, 會被封IP?
            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    if '/logout?' in url:
        try:
            driver.get('https://www.urbtix.hk/')
        except Exception as exec1:
            pass
        pass

    # for new survey.
    if 'https://www.urbtix.hk/session/landing' == url:
        if config_dict["advanced"]["auto_guess_options"]:
            #urbtix_auto_survey(driver, config_dict)
            pass

    if '.hk/member-login' in url:
        urbtix_account = config_dict["accounts"]["urbtix_account"]
        urbtix_password = config_dict["accounts"]["urbtix_password"].strip()
        if len(urbtix_account) > 4:
            urbtix_login(driver, urbtix_account, urbtix_password)

    is_ready_to_buy_from_queue = False
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        # play sound when ready to buy ticket.
        play_sound_while_ordering(config_dict)

    # https://www.urbtix.hk/event-detail/00000/
    if '/event-detail/' in url:
        if config_dict["date_auto_select"]["enable"]:
            is_event_page = False
            if len(url.split('/'))<=6:
                is_event_page = True
            urbtix_purchase_ticket(driver, config_dict)

    # https://www.urbtix.hk/performance-detail/?eventId=00000&performanceId=00000
    is_performace_page = False
    if '/performance-detail/?eventId=' in url:
        is_performace_page = True

    if 'performance-detail?eventId' in url:
        is_performace_page = True

    if is_performace_page:
        if config_dict["area_auto_select"]["enable"]:
            is_confirm_dialog_popup = urbtix_performance_confirm_dialog_popup(driver)
            if is_confirm_dialog_popup:
                print("is_confirm_dialog_popup! auto press confirm...")
            else:
                urbtix_performance(driver, config_dict)

def check_modal_dialog_popup(driver):
    ret = False

    el_div = None
    try:
        el_div = driver.find_element(By.CSS_SELECTOR, 'div.modal-dialog > div.modal-content')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    if not el_div is None:
        #print("bingo, found modal-dialog")
        try:
            if el_div.is_enabled():
                if el_div.is_displayed():
                    ret = True
        except Exception as exc:
            pass

    return ret


def cityline_shows_goto_cta(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '.btn_cta')
    except Exception as exc:
        #print("find next button fail...")
        #print(exc)
        pass

    if not el_btn is None:
        #print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret


def cityline_cookie_accept(driver):
    is_btn_click = press_button(driver, By.CSS_SELECTOR,'.cookieWrapper_closeBtn')

def cityline_auto_retry_access(driver, config_dict):
    try:
        btn_retry = driver.find_element(By.CSS_SELECTOR, 'button')
        if not btn_retry is None:
            js = btn_retry.get_attribute('onclick')
            if len(js) > 0:
                driver.set_script_timeout(1)
                driver.execute_script(js)
    except Exception as exc:
        pass

    # 刷太快, 會被封IP?
    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

def cityline_clean_ads(driver):
    ad_query_list = [
        'ats-overlay-bottom-wrapper-rendered',
        '.insert_ads',
    ]
    try:
        for ad_query in ad_query_list:
            ad_div = driver.find_element(By.CSS_SELECTOR, ad_query)
            if not ad_div is None:
                driver.set_script_timeout(1)
                driver.execute_script("arguments[0].outerHTML='';", ad_div);
    except Exception as exc:
        pass

def cityline_input_code(driver, config_dict, fail_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)

    inferred_answer_string = ""
    for answer_item in answer_list:
        if not answer_item in fail_list:
            inferred_answer_string = answer_item
            break

    if show_debug_message:
        print("inferred_answer_string:", inferred_answer_string)
        print("answer_list:", answer_list)

    # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
    input_text_css = "input[type='text']"
    next_step_button_css = ""
    submit_by_enter = False
    check_input_interval = 0.2
    is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return fail_list

def cityline_close_second_tab(driver):
    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            driver.switch_to.window(driver.window_handles[-1])
            page_title = driver.title
            if len(page_title) > 0:
                driver.switch_to.window(driver.window_handles[0])
                if not(".cityline.com/" in page_title and "https://" in page_title):
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
    except Exception as exc:
        pass

def cityline_main(driver, url, config_dict):
    # https://msg.cityline.com/ https://event.cityline.com/
    if 'msg.cityline.com' in url or 'event.cityline.com' in url:
        #cityline_auto_retry_access(driver, config_dict)
        pass

    cityline_close_second_tab(driver)

    if '.cityline.com/Events.html' in url:
        cityline_cookie_accept(driver)

    cityline_clean_ads(driver)

    if 'cityline.com/queue?' in url:
        # show HTTP ERROR 400
        pass

    # https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2F
    # ignore url redirect
    if 'cityline.com/Login.html' in url:
        cityline_account = config_dict["accounts"]["cityline_account"]
        cityline_password = config_dict["accounts"]["cityline_password"].strip()
        if len(cityline_account) > 4:
            cityline_login(driver, cityline_account, cityline_password)
        return

    is_ready_to_buy_from_queue = False
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        # play sound when ready to buy ticket.
        play_sound_while_ordering(config_dict)

    if '/eventDetail?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if config_dict["date_auto_select"]["enable"]:
                cityline_purchase_button_press(driver, config_dict)

    if '/performance?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if config_dict["area_auto_select"]["enable"]:
                cityline_performance(driver, config_dict)

    if '.htm' in url:
        if not '/slim_end.htm' in url:
            if len(url.split('/'))>=5:
                cityline_shows_goto_cta(driver)

    # https://venue.cityline.com/utsvInternet/XXX/login?lang=TW
    if '/utsvInternet/' in url and '/login?' in url:
        if len(url.split('/')) == 6:
            fail_list = []
            fail_list = cityline_input_code(driver, config_dict, fail_list)


def check_ibon_login_status(driver, config_dict):
    """
    檢查 ibon 登入狀態
    Returns:
        True if logged in successfully
        False if not logged in or cookie invalid
    """
    is_logged_in = False

    try:
        current_url = driver.current_url
        if config_dict["advanced"]["verbose"]:
            print(f"Checking ibon login status at URL: {current_url}")

        # Check if we're redirected to login page
        if 'huiwan.ibon.com.tw' in current_url and 'Login' in current_url:
            if config_dict["advanced"]["verbose"]:
                print("Detected redirect to login page - cookie may be invalid")
            return False

        # Check for login indicators on ibon pages
        try:
            # Method 1: Look for specific ibon login/logout indicators
            logout_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'logout') or contains(@href, 'Logout') or contains(text(), '登出') or contains(text(), '會員中心')]")
            member_elements = driver.find_elements(By.XPATH, "//span[contains(text(), '會員')] | //div[contains(@class, 'member')] | //a[contains(text(), 'Hi,')]")

            if logout_elements or member_elements:
                if config_dict["advanced"]["verbose"]:
                    print(f"Found logout/member elements ({len(logout_elements)} logout, {len(member_elements)} member) - user appears to be logged in")
                is_logged_in = True
            else:
                # Method 2: Check for login button/link
                login_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'login') or contains(@href, 'Login') or contains(text(), '登入') or contains(text(), '會員登入')]")

                if login_elements:
                    if config_dict["advanced"]["verbose"]:
                        print(f"Found {len(login_elements)} login elements - user appears to be logged out")
                    is_logged_in = False
                else:
                    # Method 3: Check page content for login indicators
                    page_source = driver.page_source.lower()

                    # Look for logout related text in page source
                    logout_indicators = ['logout', '登出', '會員中心', 'member center']
                    login_indicators = ['會員登入', 'member login', 'sign in', '登入']

                    has_logout = any(indicator in page_source for indicator in logout_indicators)
                    has_login = any(indicator in page_source for indicator in login_indicators)

                    if has_logout and not has_login:
                        if config_dict["advanced"]["verbose"]:
                            print("Found logout indicators in page content - user appears to be logged in")
                        is_logged_in = True
                    elif has_login and not has_logout:
                        if config_dict["advanced"]["verbose"]:
                            print("Found login indicators in page content - user appears to be logged out")
                        is_logged_in = False
                    else:
                        # Fallback: if we're on ibon domain and not redirected to login, assume logged in
                        if 'ibon.com' in current_url:
                            if config_dict["advanced"]["verbose"]:
                                print("Ambiguous login state, but on ibon domain - assuming logged in")
                            is_logged_in = True

        except Exception as element_check_error:
            if config_dict["advanced"]["verbose"]:
                print(f"Error checking login elements: {element_check_error}")
            # Fallback: if we're on ibon domain and not redirected to login, assume logged in
            if 'ibon.com' in current_url and 'huiwan.ibon.com.tw' not in current_url:
                is_logged_in = True

    except Exception as exc:
        if config_dict["advanced"]["verbose"]:
            print(f"Error checking ibon login status: {exc}")
        is_logged_in = False

    if config_dict["advanced"]["verbose"]:
        print(f"ibon login status check result: {'Logged in' if is_logged_in else 'Not logged in'}")

    return is_logged_in

def get_ibon_question_text(driver):
    question_div = None
    try:
        content_div = driver.find_element(By.CSS_SELECTOR, '#content')
        question_div = content_div.find_element(By.CSS_SELECTOR, 'label')
    except Exception as exc:
        print("find verify textbox fail")
        pass

    question_text = ""
    if not question_div is None:
        try:
            question_text = question_div.text
        except Exception as exc:
            print("get text fail")

    if question_text is None:
        question_text = ""

    return question_text

def ibon_verification_question(driver, fail_list, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    question_text = get_ibon_question_text(driver)
    if len(question_text) > 0:
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                answer_list = util.get_answer_list_from_question_string(None, question_text)

        inferred_answer_string = ""
        if len(answer_list) > 0:
            for answer_item in answer_list:
                if not answer_item in fail_list:
                    inferred_answer_string = answer_item
                    break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("answer_list:", answer_list)
            print("fail_list:", fail_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        input_text_css = 'div.editor-box > div > div.form-group > input'
        next_step_button_css = 'div.editor-box > div > a.btn'
        submit_by_enter = False
        check_input_interval = 0.2
        is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return fail_list


def ibon_ticket_agree(driver):
    is_finish_checkbox_click = False
    for i in range(3):
        is_finish_checkbox_click = check_checkbox(driver, By.CSS_SELECTOR, '#agreen')
        if is_finish_checkbox_click:
            break
    return is_finish_checkbox_click

def ibon_check_sold_out(driver):
    is_sold_out = False

    div_ticket_info = None
    try:
        div_ticket_info = driver.find_element(By.CSS_SELECTOR, '#ticket-info')
    except Exception as exc:
        print("find #ticket-info fail")

    if not div_ticket_info is None:
        try:
            div_ticket_info_text = div_ticket_info.text
            if not div_ticket_info_text is None:
                if '已售完' in div_ticket_info_text:
                    is_sold_out = True
        except Exception as exc:
            pass

    return is_sold_out

def ibon_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False

    form_verifyCode = None
    try:
        my_css_selector = 'input[value="驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find blockLogin input fail")
        try:
            my_css_selector = 'input[placeholder="驗證碼"]'
            form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    if not form_verifyCode is None:
        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""

        if inputed_value == "驗證碼":
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass
        else:
            if len(inputed_value) > 0:
                print("captcha text inputed.")
                form_verifyCode = None
                is_verifyCode_editing = True

    if not form_verifyCode is None:
        if len(answer) > 0:
            #answer=answer.upper()
            is_visible = False
            try:
                if form_verifyCode.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    form_verifyCode.click()
                    is_verifyCode_editing = True
                except Exception as exc:
                    pass

                #print("start to fill answer.")
                try:
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)
                except Exception as exc:
                    print("send_keys ocr answer fail.")

    return is_verifyCode_editing

def ibon_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None
    if not ocr is None:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.request_captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'chk_pic'
            image_element = None
            try:
                my_css_selector = "#" + image_id
                image_element = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not image_element is None:
                try:
                    driver.set_script_timeout(1)
                    form_verifyCode_base64 = driver.execute_async_script("""
                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        var img = document.getElementById('%s');
                        if(img!=null) {
                        canvas.height = img.naturalHeight;
                        canvas.width = img.naturalWidth;
                        context.drawImage(img, 0, 0);
                        callback = arguments[arguments.length - 1];
                        callback(canvas.toDataURL()); }
                        """ % (image_id))
                    if not form_verifyCode_base64 is None:
                        img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
                except Exception as exc:
                    if show_debug_message:
                        print("canvas exception:", str(exc))
                    pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var = ibon_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                ibon_keyin_captcha_code(driver)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("click captcha again")
                    if True:
                        # selenium solution.
                        jquery_string = '$("#chk_pic").attr("src", "/pic.aspx?TYPE=%s&ts=" + new Date().getTime());' % (model_name)
                        driver.execute_script(jquery_string)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            time.sleep(0.3)
                    else:
                        # Non_Browser solution.
                        if not Captcha_Browser is None:
                            new_captcha_url = Captcha_Browser.request_refresh_captcha() #取得新的CAPTCHA
                            if new_captcha_url != "":
                                #PS:[TODO]
                                #tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
                                pass
    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            ibon_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def ibon_captcha(driver, config_dict, ocr, Captcha_Browser, model_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    #PS: need a 'auto assign seat' feature to enable away_from_keyboard feature.
    away_from_keyboard_enable = False

    is_captcha_sent = False
    previous_answer = None
    last_url, is_quit_bot = get_current_url(driver)
    for redo_ocr in range(19):
        is_need_redo_ocr, previous_answer, is_form_sumbited = ibon_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name)

        # TODO: must ensure the answer is corrent...
        if not is_need_redo_ocr:
            is_captcha_sent = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

        current_url, is_quit_bot = get_current_url(driver)
        if current_url != last_url:
            break

    return is_captcha_sent

def ibon_main(driver, url, config_dict, ocr, Captcha_Browser):
    global ibon_dict
    if not 'ibon_dict' in globals():
        ibon_dict = {}
        ibon_dict["fail_list"]=[]
        ibon_dict["start_time"]=None
        ibon_dict["done_time"]=None
        ibon_dict["elapsed_time"]=None

    home_url_list = ['https://ticket.ibon.com.tw/'
    ,'https://ticket.ibon.com.tw/index/entertainment'
    ]
    for each_url in home_url_list:
        if each_url == url.lower():
            if config_dict["ocr_captcha"]["enable"]:
                set_non_browser_cookies(driver, url, Captcha_Browser)
            break

    # https://tour.ibon.com.tw/event/e23010000300mxu
    if 'tour' in url.lower() and '/event/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True
        if is_event_page:
            # ibon auto press signup
            is_button_clicked = press_button(driver, By.CSS_SELECTOR, '.btn.btn-signup')

    is_match_target_feature = False

    #PS: ibon some utk is upper case, some is lower.
    if not is_match_target_feature:
        #https://ticket.ibon.com.tw/ActivityInfo/Details/0000?pattern=entertainment
        if '/activityinfo/details/' in url.lower():
            is_event_page = False
            if len(url.split('/'))==6:
                is_event_page = True

            if is_event_page:
                if config_dict["date_auto_select"]["enable"]:
                    is_match_target_feature = True
                    is_date_assign_by_bot = ibon_date_auto_select(driver, config_dict)

    if 'ibon.com.tw/error.html?' in url.lower():
        try:
            driver.back()
        except Exception as exc:
            pass

    is_enter_verify_mode = False
    if not is_match_target_feature:
        # validation question url:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_0.aspx?rn=1180872370&PERFORMANCE_ID=B04M7XZT&PRODUCT_ID=B04KS88E&SHOW_PLACE_MAP=True
        is_event_page = False
        if '/UTK02/UTK0201_0.' in url.upper():
            if '.aspx?' in url.lower():
                if 'rn=' in url.lower():
                    if 'PERFORMANCE_ID=' in url.upper():
                        if "PRODUCT_ID=" in url.upper():
                            is_event_page = True

        if is_event_page:
            is_enter_verify_mode = True
            ibon_dict["fail_list"] = ibon_verification_question(driver, ibon_dict["fail_list"], config_dict)
            is_match_target_feature = True

    if not is_enter_verify_mode:
        ibon_dict["fail_list"] = []

    if not is_match_target_feature:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=0000
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?rn=1111&PERFORMANCE_ID=2222&PRODUCT_ID=BBBB
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_001.aspx?PERFORMANCE_ID=2222&GROUP_ID=4&PERFORMANCE_PRICE_AREA_ID=3333

        is_event_page = False
        if '/UTK02/UTK0201_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if '/UTK02/UTK0202_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if is_event_page:
            if config_dict["area_auto_select"]["enable"]:
                select_query = "tr.disbled"
                clean_tag_by_selector(driver,select_query)
                select_query = "tr.sold-out"
                clean_tag_by_selector(driver,select_query)

                is_do_ibon_performance_with_ticket_number = False

                if 'PRODUCT_ID=' in url.upper():
                    # step 1: select area.
                    is_match_target_feature = True
                    is_price_assign_by_bot = ibon_performance(driver, config_dict)
                    #print("is_price_assign_by_bot:", is_price_assign_by_bot)
                    if not is_price_assign_by_bot:
                        # this case show captcha and ticket-number in this page.
                        if ibon_ticket_number_appear(driver, config_dict):
                            is_do_ibon_performance_with_ticket_number = True

                if 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
                    is_do_ibon_performance_with_ticket_number = True

                if is_do_ibon_performance_with_ticket_number:
                    if config_dict["advanced"]["disable_adjacent_seat"]:
                        is_finish_checkbox_click = ibon_allow_not_adjacent_seat(driver, config_dict)

                    # captcha
                    is_captcha_sent = False
                    if config_dict["ocr_captcha"]["enable"]:
                        domain_name = url.split('/')[2]
                        model_name = url.split('/')[5]
                        if len(model_name) > 7:
                            model_name=model_name[:7]
                        captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
                        #PS: need set cookies once, if user change domain.
                        if not Captcha_Browser is None:
                            Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                        is_captcha_sent = ibon_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

                    # assign ticket number.
                    is_match_target_feature = True
                    is_ticket_number_assigned = ibon_ticket_number_auto_select(driver, config_dict)
                    #print("is_ticket_number_assigned:", is_ticket_number_assigned)
                    if is_ticket_number_assigned:
                        if is_captcha_sent:
                            click_ret = ibon_purchase_button_press(driver)

                            # only this case: "ticket number CHANGED by bot" and "cpatcha sent" to play sound!
                            if click_ret:
                                play_sound_while_ordering(config_dict)
                    else:
                        is_sold_out = ibon_check_sold_out(driver)
                        if is_sold_out:
                            print("is_sold_out, go back , and refresh.")
                            # plan-A
                            #is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'a.btn.btn-primary')
                            # plan-B, easy and better than plan-A
                            try:
                                driver.back()
                                driver.refresh()
                            except Exception as exc:
                                pass


    if not is_match_target_feature:
        #https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
        is_event_page = False
        if '/UTK02/UTK020' in url.upper():
            if '.aspx' in url.lower():
                if len(url.split('/'))==6:
                    is_event_page = True

        # ignore "pay money" step.
        if '/UTK02/UTK0207_.ASPX' in url.upper():
            is_event_page = False

        if is_event_page:
            if is_event_page:
                is_match_target_feature = True
                is_finish_checkbox_click = ibon_ticket_agree(driver)
                if is_finish_checkbox_click:
                    is_name_based = False
                    try:
                        my_css_selector = "body"
                        html_body = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                        if not html_body is None:
                            if '實名制' in html_body.text:
                                is_name_based = True
                    except Exception as exc:
                        pass

                    if not is_name_based:
                        is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'a.btn.btn-pink.continue')


def hkticketing_accept_cookie(driver):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.CSS_SELECTOR, '#closepolicy_new')
    except Exception as exc:
        if show_debug_message:
            print("find closepolicy_new fail")
        pass

    if not accept_all_cookies_btn is None:
        is_visible = False
        try:
            if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            if show_debug_message:
                print("closepolicy_new visible. start to press.")
            try:
                accept_all_cookies_btn.click()
            except Exception as exc:
                pass
                '''
                print("try to click closepolicy_new fail")
                try:
                    driver.execute_script("arguments[0].click();", accept_all_cookies_btn)
                except Exception as exc:
                    pass
                '''
        else:
            if show_debug_message:
                print("closepolicy_new invisible.")

def hkticketing_date_buy_button_press(driver):
    is_date_submiting = False
    el_btn = None
    try:
        my_css_selector = "#buyButton > input"
        el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    if not el_btn is None:
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                print("buy button pressed.")
                is_date_submiting = True
            else:
                if not el_btn.is_enabled():
                    print("force to press disabled buy button.")
                    try:
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass
        except Exception as exc:
            pass
            # use plan B
            '''
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass
            '''
    return is_date_submiting

def hkticketing_date_assign(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    if show_debug_message:
        print("date_keyword:", date_keyword)

    matched_blocks = None

    # clean stop word.
    date_keyword = util.format_keyword_string(date_keyword)
    date_keyword_and = ""

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '#p')
    except Exception as exc:
        print("find select#p fail")
        pass

    select_obj = None
    if not form_select is None:
        is_visible = False
        try:
            if form_select.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_date_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 8:
                if '20' in row_text:
                    # ticket assign.
                    is_date_assigned = True

    if show_debug_message:
        print("is_date_assigned:", is_date_assigned)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    is_page_ready = True
    if not is_date_assigned:
        area_list = None
        try:
            my_css_selector = "#p > option"
            area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            print("find #p options date list fail")
            print(exc)

        if not area_list is None:
            area_list_count = len(area_list)
            if show_debug_message:
                print("date_list_count:", area_list_count)

            if area_list_count == 0:
                is_page_ready = False
            else:
                formated_area_list = []
                # filter list.
                for row in area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if not('20' in row_text):
                            row_text = ""
                        if ' Exhausted' in row_text:
                            row_text = ""
                        if '配售完畢' in row_text:
                            row_text = ""
                        if '配售完毕' in row_text:
                            row_text = ""
                        if 'No Longer On Sale' in row_text:
                            row_text = ""
                        if '已停止發售' in row_text:
                            row_text = ""
                        if '已停止发售' in row_text:
                            row_text = ""

                    if len(row_text) > 0:
                        formated_area_list.append(row)

        if not formated_area_list is None:
            area_list_count = len(formated_area_list)
            if show_debug_message:
                print("formated_area_list count:", area_list_count)
            if area_list_count > 0:

                if len(date_keyword) == 0:
                    matched_blocks = formated_area_list
                else:
                    # match keyword.
                    if show_debug_message:
                        print("start to match keyword:", date_keyword)

                    matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                    if show_debug_message:
                        if not matched_blocks is None:
                            print("after match keyword, found count:", len(matched_blocks))
            else:
                print("not found date-time-position")
                pass
        else:
            print("date date-time-position is None")
            pass

        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
        if not target_area is None:
            try:
                if target_area.is_enabled():
                    target_area.click()
                    is_date_assigned = True
            except Exception as exc:
                print("click target_area link fail")
                print(exc)

    return is_date_assigned, is_page_ready, formated_area_list

def hkticketing_date_password_input(driver, config_dict, fail_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_password_appear = False

    el_password_input = None
    try:
        my_css_selector = "#entitlementPassword > div > div > div > div > input[type='password']"
        el_password_input = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    inputed_value = ""
    if not el_password_input is None:
        try:
            inputed_value = el_password_input.get_attribute('value')
        except Exception as exc:
            print("get_attribute value fail")
            pass
        if not inputed_value is None:
            is_password_appear = True
            if inputed_value == "":
                # only this case to auto-fill local dictional value.
                local_array = []
                user_guess_string = config_dict["advanced"]["user_guess_string"]
                if len(user_guess_string) > 0:
                    user_guess_string = util.format_config_keyword_for_json(user_guess_string)
                    try:
                        local_array = json.loads("["+ user_guess_string +"]")
                    except Exception as exc:
                        local_array = []
                answer_list = local_array

                inferred_answer_string = ""
                for answer_item in answer_list:
                    if not answer_item in fail_list:
                        inferred_answer_string = answer_item
                        break

                if len(inferred_answer_string) > 0:
                    try:
                        el_password_input.click()
                        el_password_input.send_keys(inferred_answer_string)
                        el_password_input.send_keys(Keys.ENTER)

                        print("input dictionary answer:", inferred_answer_string)
                        fail_list.append(inferred_answer_string)
                    except Exception as exc:
                        print("set_attribute value fail")
                        pass

    return is_password_appear, fail_list

def hkticketing_date_auto_select(driver, config_dict, fail_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    is_page_ready = True
    is_date_assigned, is_page_ready, formated_area_list = hkticketing_date_assign(driver, config_dict)

    # NOT alway, auto submit
    is_date_submiting = False

    is_auto_submit = True
    is_password_sent = False
    is_password_appear, fail_list = hkticketing_date_password_input(driver, config_dict, fail_list)
    if is_password_appear:
        is_auto_submit = False

    if show_debug_message:
        print("is_auto_submit:", is_auto_submit)

    el_btn = None
    if is_auto_submit:
        is_button_clicked = press_button(driver, By.CSS_SELECTOR, '#buyButton > input')
        if show_debug_message:
            print("is_button_clicked:", is_button_clicked)

    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]
    if show_debug_message:
        print("is_password_appear:", is_password_appear)
        print("is_date_assigned:", is_date_assigned)
        print("is_page_ready:", is_page_ready)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    if auto_reload_coming_soon_page_enable:
        # auto refresh for date list page.
        is_need_refresh = True

        if is_need_refresh:
            if is_password_appear:
                is_need_refresh = False

        if is_need_refresh:
            if is_date_assigned:
                # if select box assign.
                is_need_refresh = False
            else:
                if not formated_area_list is None:
                    if len(formated_area_list) > 0:
                        # option waiting to assign at next loop.
                        is_need_refresh = False

        # due to select option not generated by server side.
        if is_need_refresh:
            if not is_page_ready:
                is_need_refresh = False

        # check next button exist.
        if is_need_refresh:
            el_btn = None
            try:
                my_css_selector = "#buyButton > input"
                el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass
            if not el_btn is None:
                if show_debug_message:
                    print("next button appear.")
                is_need_refresh = False

        # finally...
        if is_need_refresh:
            try:
                print("is_need_refresh...")
                driver.refresh()
                time.sleep(0.2)
            except Exception as exc:
                pass

    return is_date_submiting, fail_list

def hkticketing_area_auto_select(driver, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        my_css_selector = "#ticketSelectorContainer > ul > li"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                row_is_enabled=True
                try:
                    button_class_string = str(row.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            row_is_enabled=False
                        if 'unavailable' in button_class_string:
                            row_is_enabled=False
                        if 'selected' in button_class_string:
                            # someone is selected. skip this process.
                            is_price_assign_by_bot = True
                            break
                except Exception as exc:
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                            row_text = ""

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False
                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot

def hkticketing_ticket_number_auto_select(driver, config_dict):
    selector_string = 'select.shortSelect'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, config_dict, by_method, selector_string)

def hkticketing_nav_to_footer(driver):
    try:
        el_nav = None
        el_nav = driver.find_element(By.CSS_SELECTOR, '#wrapFooter')
        if not el_nav is None:
            builder = ActionChains(driver)
            builder.move_to_element(el_nav)
            builder.click(el_nav)
            builder.perform()
    except Exception as exc:
        pass

def hkticketing_next_button_press(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '#continueBar > div.chooseTicketsOfferDiv > button')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if not el_btn is None:
        #print("bingo, found next button, start to press")
        hkticketing_nav_to_footer(driver)
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret

def hkticketing_go_to_payment(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '#goToPaymentButton')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if not el_btn is None:
        #print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret

def hkticketing_ticket_delivery_option(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_delivery_option_assigned = False

    form_select = None
    try:
        selector_string = '#selectDeliveryType'
        form_select = driver.find_element(By.CSS_SELECTOR, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find selectDeliveryType select fail")
            print(exc)
        pass

    select_obj = None
    if not form_select is None:
        is_visible = False
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    if not select_obj is None:
        try:
            select_obj.select_by_value("1")
            is_delivery_option_assigned = True
        except Exception as exc:
            print("delivery_option fail")
            print(exc)


    return is_delivery_option_assigned

def hkticketing_hide_tickets_blocks(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    actionBlock_divs = None
    try:
        selector_string = 'div.actionBlock.note'
        actionBlock_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        for each_div in actionBlock_divs:
            driver.execute_script("arguments[0].innerHTML='';", each_div);
    except Exception as exc:
        if show_debug_message:
            print("find selectDeliveryType select fail")
            print(exc)
        pass

    detailModuleCopy_divs = None
    try:
        selector_string = 'div.detailModuleCopy'
        detailModuleCopy_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        if not detailModuleCopy_divs is None:
            driver.execute_script("arguments[0].innerHTML='';", detailModuleCopy_divs);
    except Exception as exc:
        pass

    mapWrapper_divs = None
    try:
        selector_string = 'div.mapWrapper'
        mapWrapper_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        if not mapWrapper_divs is None:
            driver.execute_script("arguments[0].innerHTML='';", mapWrapper_divs);
    except Exception as exc:
        pass


def hkticketing_performance(driver, config_dict, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = hkticketing_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = hkticketing_area_auto_select(driver, config_dict, "")

        if is_need_refresh:
            if show_debug_message:
                print("is_need_refresh:", is_need_refresh)
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # hide blocks.
        #hkticketing_hide_tickets_blocks(driver)

        # goto bottom.
        hkticketing_nav_to_footer(driver)

        # choose ticket.
        is_ticket_number_assigned = hkticketing_ticket_number_auto_select(driver, config_dict)
        if show_debug_message:
            print("is_ticket_number_assigned:", is_ticket_number_assigned)

        # Select a delivery option
        is_delivery_option_assigned = True
        if not 'galaxymacau.com' in domain_name:
            # hkticketing
            is_delivery_option_assigned = False
            if is_ticket_number_assigned:
                is_delivery_option_assigned = hkticketing_ticket_delivery_option(driver)
            if show_debug_message:
                print("is_delivery_option_assigned:", is_delivery_option_assigned)

        if is_delivery_option_assigned:
            auto_press_next_step_button = True
            if auto_press_next_step_button:
                if is_price_assign_by_bot:
                    for i in range(2):
                        click_ret = hkticketing_next_button_press(driver)
                        time.sleep(0.2)
                        if click_ret:
                            break

    return is_price_assign_by_bot


def hkticketing_escape_robot_detection(driver, url):
    ret = False

    el_main_iframe = None
    try:
        el_main_iframe = driver.find_element(By.CSS_SELECTOR, '#main-iframe')
    except Exception as exc:
        #print("find el_main_iframe fail...")
        #print(exc)
        pass

    if not el_main_iframe is None:
        print("we have been detected..., found el_main_iframe")
        #entry_url="https://queue.hkticketing.com/hotshow.html"
        entry_url="https://premier.hkticketing.com/"
        if 'galaxymacau.com' in url:
            domain_name = url.split('/')[2]
            entry_url = "https://%s/default.aspx" % (domain_name)

        try:
            #print("start to escape..")
            #driver.get(entry_url)
            pass
        except Exception as exc:
            print(exc)

    return ret

def hkticketing_url_redirect(driver, url, config_dict):
    is_redirected = False
    redirect_url_list = [ 'queue.hkticketing.com/hotshow.html'
    , '.com/detection.aspx?rt='
    , '/busy_galaxy.'
    ]
    for idx in range(20):
        redirect_url_list.append('/hot%d.ticketek.com.au/' % (idx))


    redirect_to_home_list = [ 'galaxymacau.com'
    , 'ticketek.com'
    ]
    for redirect_url in redirect_url_list:
        if redirect_url in url:
            # for hkticketing.
            entry_url = 'https://entry-hotshow.hkticketing.com/'

            # for macau
            # for ticketek.com
            for target_site in redirect_to_home_list:
                if target_site  in url:
                    domain_name = url.split('/')[2]
                    entry_url = "https://%s/default.aspx" % (domain_name)
                    break
            try:
                driver.get(entry_url)
                is_redirected = True
            except Exception as exc:
                pass

            # 刷太快, 會被封IP?
            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

            if is_redirected:
                break

    # for Access denied (403)
    if url == 'https://entry-hotshow.hkticketing.com/':
        content_redirect_string_list = ['Access denied (403)','Current session has been terminated']
        is_need_refresh = False
        html_body = None
        try:
            html_body = driver.page_source
        except Exception as exc:
            #print(exc)
            pass
        if not html_body is None:
            for each_redirect_string in content_redirect_string_list:
                if each_redirect_string in html_body:
                    is_need_refresh = True
                    break
        if is_need_refresh:
            entry_url = "https://hotshow.hkticketing.com/"
            try:
                driver.get(entry_url)
                is_redirected = True
            except Exception as exc:
                pass

    return is_redirected

def hkticketing_content_refresh(driver, url, config_dict):
    is_redirected = False

    is_check_access_deined = False
    check_url_list = [".com/default.aspx"
    , ".com/shows/show.aspx?sh="
    , ".com/detection.aspx"
    , "/entry-hotshow."
    , ".com/_Incapsula_Resource?"
    ]
    for current_url in check_url_list:
        if current_url in url:
            is_check_access_deined = True
            break

    check_full_url_list = [ "https://premier.hkticketing.com/"
    , "https://www.ticketing.galaxymacau.com/"
    , "https://ticketing.galaxymacau.com/"
    , "https://ticketing.galaxymacau.com/default.aspx"
    ]
    for current_url in check_full_url_list:
        if current_url == url:
            is_check_access_deined = True

    content_retry_string_list = [ "Access Denied"
    , "Service Unavailable"
    , "The service is unavailable"
    , "HTTP Error 500"
    , "HTTP Error 503"
    , "504 Gateway Time-out"
    , "502 Bad Gateway"
    , "An error occurred while processing your request"
    , "The network path was not found"
    , "Could not open a connection to SQL Server"
    , "Hi fans, you’re in the queue to"
    , "We will check for the next available purchase slot"
    , "please stay on this page and do not refresh"
    , "Please be patient and wait a few minutes before trying again"
    , "Server Error in '/' Application"
    , "The target principal name is incorrect"
    , "Cannot generate SSPI context"
    , "System.Data.SqlClient.Sql"
    , "System.ComponentModel.Win32Exception"
    , "Access Denied"
    , "Your attempt to access the web site has been blocked by"
    , "This request was blocked by"
    ]
    if is_check_access_deined:
        domain_name = url.split('/')[2]
        new_url = "https://%s/default.aspx" % (domain_name)

        is_need_refresh = False
        html_body = None
        try:
            html_body = driver.page_source
            if not html_body is None:
                for each_retry_string in content_retry_string_list:
                    if each_retry_string in html_body:
                        is_need_refresh = True
                        break
        except Exception as exc:
            #print(exc)
            pass

        if is_need_refresh:
            print("Start to automatically refresh page.")
            try:
                driver.switch_to.default_content()
                print("redirect to new url:", new_url)
                driver.get(new_url)
                is_redirected = True
            except Exception as exc:
                #print(exc)
                pass

            # 刷太快, 會被封IP?
            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_redirected

def hkticketing_travel_iframe(driver, config_dict):
    is_redirected = False

    iframes = None
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
    except Exception as exc:
        pass

    if iframes is None:
        iframes = []

    #print('start to travel iframes...')
    idx_iframe=0
    for iframe in iframes:
        iframe_url = ""
        try:
            iframe_url = str(iframe.get_attribute('src'))
            #print("url:", iframe_url)
        except Exception as exc:
            print("get iframe url fail.")
            #print(exc)
            pass

        idx_iframe += 1
        try:
            #print("switch to #", idx_iframe, ":", iframe_url)
            driver.switch_to.frame(iframe)
            is_redirected = hkticketing_content_refresh(driver, iframe_url, config_dict)
        except Exception as exc:
            pass

        if not is_redirected:
            try:
                driver.switch_to.default_content()
            except Exception as exc:
                pass

    return is_redirected

def softix_powerweb_main(driver, url, config_dict):
    global hkticketing_dict
    if not 'hkticketing_dict' in globals():
        hkticketing_dict = {}
        hkticketing_dict["is_date_submiting"] = False
        hkticketing_dict["fail_list"]=[]

    hkticketing_accept_cookie(driver)

    is_redirected = hkticketing_url_redirect(driver, url, config_dict)
    if not is_redirected:
        is_redirected = hkticketing_content_refresh(driver, url, config_dict)
    if not is_redirected:
        is_redirected = hkticketing_travel_iframe(driver, config_dict)

    # https://premier.hkticketing.com/Membership/UpdateAccount_Default.aspx
    is_hkticketing_sign_in_page = False
    if 'hkticketing.com/Secure/ShowLogin.aspx' in url:
        is_hkticketing_sign_in_page = True
    if 'hkticketing.com/Membership/Login.aspx' in url:
        is_hkticketing_sign_in_page = True
    if is_hkticketing_sign_in_page:
        hkticketing_account = config_dict["accounts"]["hkticketing_account"].strip()
        hkticketing_password = config_dict["accounts"]["hkticketing_password"].strip()
        if len(hkticketing_account) > 4:
            hkticketing_login(driver, hkticketing_account, hkticketing_password)

    is_ready_to_buy_from_queue = False
    # TODO: play sound when ready to buy ticket.
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        play_sound_while_ordering(config_dict)

    #https://premier.hkticketing.com/shows/show.aspx?sh=XXXX
    if 'shows/show.aspx?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            is_event_page = False
            if len(url.split('/'))==5:
                is_event_page = True

            if is_event_page:
                if config_dict["date_auto_select"]["enable"]:
                    if not hkticketing_dict["is_date_submiting"]:
                        hkticketing_dict["is_date_submiting"], hkticketing_dict["fail_list"] = hkticketing_date_auto_select(driver, config_dict, hkticketing_dict["fail_list"])
                        pass
                    else:
                        #print('double check buy button status.')
                        hkticketing_date_buy_button_press(driver)
    else:
        hkticketing_dict["is_date_submiting"] = False
        hkticketing_dict["fail_list"] = []

    # https://premier.hkticketing.com/events/XXX/venues/KSH/performances/XXX/tickets
    if '/events/' in url and '/performances/' in url:
        robot_detection = hkticketing_escape_robot_detection(driver, url)

        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if '/tickets' in url:
                domain_name = url.split('/')[2]
                if config_dict["area_auto_select"]["enable"]:
                    hkticketing_performance(driver, config_dict, domain_name)
                    pass

            if '/seatmap' in url:
                # goto bottom.
                hkticketing_nav_to_footer(driver)
                hkticketing_go_to_payment(driver)


def kham_go_buy_redirect(driver, domain_name):
    is_button_clicked = False
    if 'kham.com' in domain_name:
        is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'div#content > p > a > button[onclick].red')
    if 'ticket.com' in domain_name:
        is_button_clicked = press_button(driver, By.CSS_SELECTOR, 'div.row > div > a.btn.btn-order.btn-block')
    if 'udnfunlife.com' in domain_name:
        # udn 快速訂購
        my_css_selector = 'button[name="fastBuy"]'
        is_button_clicked = press_button(driver, By.CSS_SELECTOR, my_css_selector)
        if not is_button_clicked:
            is_button_clicked = press_button(driver, By.CSS_SELECTOR, '#buttonBuy')
    return is_button_clicked

def hkam_date_auto_select(driver, domain_name, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    matched_blocks = None

    area_list = None
    try:
        # for kham.com
        my_css_selector = "table.eventTABLE > tbody > tr"
        
        if 'ticket.com' in domain_name:
            my_css_selector = "div.description > table.table.table-striped.itable > tbody > tr"
        
        if 'udnfunlife.com' in domain_name:
            my_css_selector = "div.yd_session-block"

        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time tr list fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:
                    if "<button" in row_html:
                        if ' disabled">' in row_html:
                            row_text = ""

                if len(row_text) > 0:
                    if 'udnfunlife.com' in domain_name:
                        # udn.
                        if not ("前往購票" in row_html):
                            row_text = ""
                    else:
                        # kham / ticket.
                        if "<button" in row_html:
                            buyable = False
                            if '立即訂購' in row_text:
                                buyable = True
                            if '點此購票' in row_text:
                                buyable = True
                            if not buyable:
                                row_text = ""
                        else:
                            row_text = ""

                if len(row_text) > 0:
                    if 'udnfunlife.com' in domain_name:
                        # TODO: check <font color="black" style="white-space: nowrap;"
                        pass
                    else:
                        # kham.
                        price_disabled_html = '"lightblue"'
                        
                        if 'ticket.com' in domain_name:
                            price_disabled_html = '<del>'

                        if "<td" in row_html:
                            td_array = row_html.split("<td")
                            if len(td_array) > 3:
                                td_target = td_array[3]
                                price_array = td_target.split("、")
                                is_all_priece_disabled = True
                                for each_price in price_array:
                                    if not (price_disabled_html in each_price):
                                        is_all_priece_disabled = False
                                if is_all_priece_disabled:
                                    row_text = ""

                if len(row_text) > 0:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list is None...")

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    is_date_assign_by_bot = False
    if not target_area is None:
        is_button_clicked = False
        el_btn = None
        try:
            # kham / ticket.
            my_css_selector = "button"
            if 'udnfunlife.com' in domain_name:
                my_css_selector = "div.goNext"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not el_btn is None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("buy button pressed.")
                    is_button_clicked = True
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    is_button_clicked = True
                except Exception as exc:
                    pass
        is_date_assign_by_bot = is_button_clicked
    else:
        # no target to click.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_date_assign_by_bot

def kham_product(driver, domain_name, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_date_assign_by_bot = hkam_date_auto_select(driver, domain_name, config_dict)

    if not is_date_assign_by_bot:
        # click not on sale now.
        is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
        pass

    return is_date_assign_by_bot

def kham_area_auto_select(driver, domain_name, config_dict, area_keyword_item):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True
    
    # Temporary: Force debug for dropdown testing
    if "UTK0202" in driver.current_url.upper():
        show_debug_message = True
        print("DEBUG: UTK0202 page detected, enabling debug mode")

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        # for kham.com
        my_css_selector = "table#salesTable > tbody > tr[class='status_tr']"

        if "ticket.com.tw" in domain_name:
            my_css_selector = "li.main"
            #print("my_css_selector:",my_css_selector)

        if "udnfunlife" in domain_name:
            my_css_selector = "table.yd_ticketsTable > tbody > tr.main"

        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    readme_table_mode = False
    if area_list is None:
        readme_table_mode = True
    else:
        if len(area_list)==0:
            readme_table_mode = True
    if readme_table_mode:
        # Handle UTK0202 page with PRICE select dropdown
        try:
            price_select = driver.find_element(By.ID, "PRICE")
            if price_select:
                select_options = price_select.find_elements(By.CSS_SELECTOR, "option:not([value='-1'])")
                if select_options:
                    if show_debug_message:
                        print(f"Found {len(select_options)} price options in dropdown")
                    
                    # Create formated_area_list from dropdown options with keyword matching
                    formated_area_list = []
                    for option in select_options:
                        option_text = option.text.strip()
                        option_value = option.get_attribute('value')
                        if show_debug_message:
                            print(f"Found option: '{option_text}' (value: {option_value})")
                        
                        if len(option_text) > 0 and option.is_enabled():
                            # Apply same filtering logic as table rows
                            row_text = util.format_keyword_string(option_text)
                            if show_debug_message:
                                print(f"Formatted option text: '{row_text}'")
                            
                            # Check keyword match
                            is_match_area = True
                            if len(area_keyword_item) > 0:
                                area_keyword_array = area_keyword_item.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = util.format_keyword_string(area_keyword)
                                    if show_debug_message:
                                        print(f"Checking keyword '{area_keyword}' in '{row_text}'")
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        if show_debug_message:
                                            print(f"Keyword '{area_keyword}' not found in '{row_text}'")
                                        break
                            
                            if is_match_area:
                                formated_area_list.append(option)
                                if show_debug_message:
                                    print(f"✓ Option matched: '{option_text}'")
                            else:
                                if show_debug_message:
                                    print(f"✗ Option filtered out: '{option_text}'")
                        else:
                            if show_debug_message:
                                print(f"Option disabled or empty: '{option_text}'")
                    
                    if show_debug_message:
                        print(f"Final matched options: {len(formated_area_list)}")
                        
        except Exception as exc:
            if show_debug_message:
                print("No PRICE select found or error:", exc)
            pass

    # Only reset formated_area_list if not already set by dropdown handling
    if 'formated_area_list' not in locals():
        formated_area_list = None
    
    if not area_list is None and formated_area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_item:", area_keyword_item)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            for row in area_list:
                formated_area_list.append(row)
        else:
            print("area list is empty, do refresh by javascript!")
            #is_need_refresh = True
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            for row in formated_area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if '售完' in row_text:
                        row_text = ""
                    if ' Soldout' in row_html:
                        row_text = ""

                    # for udn
                    if ' style="color:gray;border:solid 1px gray;cursor:default"' in row_html:
                        #row_text = ""
                        pass

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                # check ticket_number and available count.
                if len(row_text) > 0:
                    # remaining number not appear in udn.
                    if not("udnfunlife" in domain_name):
                        if config_dict["ticket_number"] > 1:
                            maybe_ticket_count = row_text[-1:]
                            if maybe_ticket_count.isdigit():
                                if "<td" in row_html:
                                    td_array = row_html.split("<td")
                                    if len(td_array) > 0:
                                        td_target = "<td" + td_array[len(td_array)-1]
                                        ticket_count_text = util.remove_html_tags(td_target)
                                        #print("ticket_count_text:", ticket_count_text)
                                        if ticket_count_text.isdigit():
                                            if int(ticket_count_text) < config_dict["ticket_number"]:
                                                if show_debug_message:
                                                    print("skip this row, because ticket_count available only:", ticket_count_text)
                                                # skip this row.
                                                row_text = ""

                if len(row_text) > 0:
                    row_text = util.format_keyword_string(row_text)
                    if show_debug_message:
                        print("row_text:", row_text)

                    # default add row.
                    is_match_area = True
                    if len(area_keyword_item) == 0:
                        # without keyword.
                        pass
                    else:
                        # match keyword.
                        area_keyword_array = area_keyword_item.split(' ')
                        for area_keyword in area_keyword_array:
                            area_keyword = util.format_keyword_string(area_keyword)
                            if not area_keyword in row_text:
                                is_match_area = False
                                break

                    if is_match_area:
                        matched_blocks.append(row)

                        # only need first row.
                        if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                            break


            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            if not("udnfunlife" in domain_name):
                if target_area.is_enabled():
                    # Check if this is a select option (for UTK0202 dropdown)
                    if target_area.tag_name.lower() == 'option':
                        from selenium.webdriver.support.ui import Select
                        select_element = driver.find_element(By.ID, "PRICE")
                        select = Select(select_element)
                        option_value = target_area.get_attribute('value')
                        select.select_by_value(option_value)
                        is_price_assign_by_bot = True
                        if show_debug_message:
                            print(f"Selected dropdown option: {target_area.text}")
                    else:
                        # Original table row click
                        target_area.click()
                        is_price_assign_by_bot = True
            else:
                # manually click.
                """
                my_css_selector = 'div.yd_btn--link'
                target_button = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
                if not target_button is None:
                    target_button.click()
                    is_price_assign_by_bot = True
                """

                FAST_PRICE_TYPE_ID = ""
                target_area_html = target_area.get_attribute('innerHTML')
                if 'fastcode="' in target_area_html:
                    temp_string = target_area_html.split('fastcode="')[1]
                    FAST_PRICE_TYPE_ID = temp_string.split('"')[0]
                if len(FAST_PRICE_TYPE_ID) > 0:
                    js = """fetch("https://tickets.udnfunlife.com/Application/UTK01/UTK0101_009.aspx/AUTOSEAT_BTN_Click", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,zh;q=0.8,zh-TW;q=0.7",
    "content-type": "application/json; charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest"
  },
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": JSON.stringify({"FAST_PRICE_TYPE_ID":"%s","QRY":"%s","CHK":"null"}),
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
}).then(function (response) { return response.json();
}).then(function (data) { if(data.d.ReturnData.script.indexOf('top.location.href')>-1){eval(script);};
if(data.d.ReturnData.script.indexOf('上限')>-1){top.location.href="https://tickets.udnfunlife.com/application/UTK02/UTK0206_.aspx";};
if(data.d.ReturnData.script.indexOf('該場次目前無法購買。 ')>-1){location.reload();};
}).catch(function (err) { console.log(err);
});""" % (FAST_PRICE_TYPE_ID, str(config_dict["ticket_number"]));
                    #print("javascript:", js)
                    driver.execute_script(js)
                    is_price_assign_by_bot = True

        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            if not("udnfunlife" in domain_name):
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", target_area)
                    is_price_assign_by_bot = True
                except Exception as exc:
                    pass
    else:
        if show_debug_message:
            print("target_area is None, no target to click.")

    if show_debug_message:
        print("is_need_refresh:", is_need_refresh)
        print("is_price_assign_by_bot:", is_price_assign_by_bot)

    return is_need_refresh, is_price_assign_by_bot


def ticket_seat_type_auto_select(driver, config_dict, area_keyword_item):
    """
    年代售票 - 自動選擇票別 (UTK0205 座位選擇頁面)
    選擇票價類型，如原價、身障、陪同者等
    """
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_seat_type_assigned = False
    
    try:
        # 查找所有票別按鈕
        seat_type_buttons = driver.find_elements(By.CSS_SELECTOR, ".ticketType .buttonGroup button")
        
        if show_debug_message:
            print(f"Found {len(seat_type_buttons)} seat type buttons")
        
        if len(seat_type_buttons) > 0:
            matched_buttons = []
            
            for button in seat_type_buttons:
                try:
                    button_text = button.text.strip()
                    button_class = button.get_attribute('class')
                    button_value = button.get_attribute('value')
                    onclick_attr = button.get_attribute('onclick')
                    
                    if show_debug_message:
                        print(f"Button text: '{button_text}', class: '{button_class}', onclick: '{onclick_attr}'")
                    
                    if button.is_enabled() and len(button_text) > 0:
                        # 關鍵字篩選
                        is_match_keyword = True
                        if len(area_keyword_item) > 0:
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                formatted_text = util.format_keyword_string(button_text)
                                if not area_keyword in formatted_text:
                                    is_match_keyword = False
                                    break
                        
                        # 排除身障相關票種 (如果沒有特別指定)
                        if len(area_keyword_item) == 0:
                            if any(keyword in button_text for keyword in ['身心障礙', '身障', '陪同者']):
                                is_match_keyword = False
                        
                        if is_match_keyword:
                            matched_buttons.append(button)
                            if show_debug_message:
                                print(f"✓ Matched button: '{button_text}'")
                        else:
                            if show_debug_message:
                                print(f"✗ Filtered button: '{button_text}'")
                    
                except Exception as exc:
                    if show_debug_message:
                        print(f"Error processing button: {exc}")
                    pass
            
            # 選擇第一個符合條件的票別
            if len(matched_buttons) > 0:
                target_button = matched_buttons[0]  # 預設選第一個
                
                try:
                    target_button.click()
                    is_seat_type_assigned = True
                    if show_debug_message:
                        print(f"✓ Clicked seat type button: '{target_button.text}'")
                except Exception as exc:
                    if show_debug_message:
                        print(f"Failed to click seat type button: {exc}")
                    try:
                        driver.execute_script("arguments[0].click();", target_button)
                        is_seat_type_assigned = True
                        if show_debug_message:
                            print(f"✓ Force clicked seat type button by JS")
                    except Exception as exc2:
                        if show_debug_message:
                            print(f"Failed to force click: {exc2}")
            else:
                if show_debug_message:
                    print("No matching seat type buttons found")
        
    except Exception as exc:
        if show_debug_message:
            print(f"Error in seat type selection: {exc}")
    
    return is_seat_type_assigned


def ticket_find_best_seats(available_seats, ticket_number, allow_non_adjacent):
    """
    簡化版座位選擇：優先選擇座位密度高的排，然後選中間位置
    """
    if len(available_seats) < ticket_number:
        return []
    
    # 分析座位分布
    rows = {}
    for seat in available_seats:
        try:
            seat_title = seat.get_attribute('title')
            if seat_title and '排' in seat_title and '號' in seat_title:
                parts = seat_title.split('-')
                if len(parts) >= 3:
                    row_num = int(parts[1].replace('排', ''))
                    seat_num = int(parts[2].replace('號', ''))
                    
                    if row_num not in rows:
                        rows[row_num] = []
                    rows[row_num].append((seat, seat_num))
        except:
            continue
    
    # 按座位數量排序（座位多的排優先）
    sorted_rows = sorted(rows.items(), key=lambda x: -len(x[1]))
    
    selected_seats = []
    for row_num, row_seats in sorted_rows:
        # 按座位號排序，選中間位置
        row_seats.sort(key=lambda x: x[1])
        seat_count = len(row_seats)
        
        if allow_non_adjacent:
            # 非連續模式：選中間位置開始的座位
            start_idx = max(0, (seat_count - ticket_number) // 2)
            for i in range(min(ticket_number, seat_count)):
                if start_idx + i < len(row_seats):
                    selected_seats.append(row_seats[start_idx + i][0])
                    if len(selected_seats) >= ticket_number:
                        break
        else:
            # 連續模式：找連續座位
            for start_idx in range(len(row_seats) - ticket_number + 1):
                continuous = True
                for i in range(ticket_number - 1):
                    current_num = row_seats[start_idx + i][1]
                    next_num = row_seats[start_idx + i + 1][1]
                    if abs(next_num - current_num) > 2:  # 允許奇偶號連續
                        continuous = False
                        break
                
                if continuous:
                    for i in range(ticket_number):
                        selected_seats.append(row_seats[start_idx + i][0])
                    break
        
        if len(selected_seats) >= ticket_number:
            break
    
    return selected_seats[:ticket_number]


def ticket_seat_auto_select(driver, config_dict):
    """
    年代售票 - 自動選擇座位，優化策略：熱門排優先、中間優先
    """
    is_seat_assigned = False
    ticket_number = config_dict["ticket_number"]
    allow_non_adjacent = config_dict["advanced"]["disable_adjacent_seat"]
    show_debug = config_dict["advanced"]["verbose"]
    
    try:
        # 查找可選座位
        available_seats = driver.find_elements(By.CSS_SELECTOR, '#locationChoice table td[title][style*="cursor: pointer"]')
        
        if len(available_seats) >= ticket_number:
            # 使用優化策略選擇座位
            selected_seats = ticket_find_best_seats(available_seats, ticket_number, allow_non_adjacent)
            
            # 點擊選中的座位
            selected_count = 0
            for seat in selected_seats:
                try:
                    seat_style = seat.get_attribute('style')
                    if 'cursor: pointer' in seat_style and 'icon_chair_empty' in seat_style:
                        seat.click()
                        selected_count += 1
                        if show_debug:
                            print(f"✓ Selected seat: {seat.get_attribute('title')}")
                        time.sleep(0.3)
                except Exception:
                    continue
            
            is_seat_assigned = selected_count > 0
            if show_debug:
                print(f"Selected {selected_count}/{ticket_number} seats")
    
    except Exception as exc:
        if show_debug:
            print(f"Seat selection error: {exc}")
    
    return is_seat_assigned


def ticket_seat_main(driver, config_dict, ocr, Captcha_Browser, domain_name):
    """
    年代售票座位選擇主流程：票別選擇 -> 座位選擇 -> 驗證碼 -> 提交
    """
    show_debug = config_dict["advanced"]["verbose"]
    
    # Step 1: 選擇票別
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    is_seat_type_assigned = ticket_seat_type_auto_select(driver, config_dict, area_keyword)
    
    if not is_seat_type_assigned:
        is_seat_type_assigned = ticket_seat_type_auto_select(driver, config_dict, "原價")
    
    # Step 2: 選擇座位
    is_seat_assigned = False
    if is_seat_type_assigned:
        is_seat_assigned = ticket_seat_auto_select(driver, config_dict)
    
    # Step 3: 處理驗證碼
    is_captcha_sent = False
    if is_seat_assigned and config_dict["ocr_captcha"]["enable"]:
        try:
            captcha_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_CHK")
            if captcha_input:
                if Captcha_Browser:
                    Captcha_Browser.set_domain(domain_name, captcha_url="/pic.aspx?TYPE=UTK0205")
                is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, "UTK0205")
        except Exception:
            pass
    
    # Step 4: 提交
    is_submit_success = False
    if is_seat_assigned and (not config_dict["ocr_captcha"]["enable"] or is_captcha_sent):
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button.sumitButton[onclick*="addShoppingCart1"]')
            if submit_button and submit_button.is_enabled():
                submit_button.click()
                is_submit_success = True
                play_sound_while_ordering(config_dict)
        except Exception:
            try:
                driver.execute_script("addShoppingCart1();")
                is_submit_success = True
                play_sound_while_ordering(config_dict)
            except Exception:
                pass
    
    if show_debug:
        print(f"年代售票結果: 票別{is_seat_type_assigned} 座位{is_seat_assigned} 提交{is_submit_success}")
    
    return is_submit_success


def ticket_allow_not_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = 'div.panel > span > input[type="checkbox"]'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ibon seat checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def kham_switch_to_auto_seat(driver):
    is_switch_to_auto_seat = False

    btn_switch_to_auto_seat = None
    try:
        my_css_selector = '#BUY_TYPE_2'
        btn_switch_to_auto_seat = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find BUY_TYPE_2 input fail")
        pass

    if not btn_switch_to_auto_seat is None:
        button_class_string = None
        try:
            button_class_string = form_verifyCode.get_attribute('class')
        except Exception as exc:
            #print("get_attribute('class') fail")
            pass

        if button_class_string is None:
            button_class_string = ""

        if button_class_string == "":
            try:
                btn_switch_to_auto_seat.click()
                is_switch_to_auto_seat = True
            except Exception as exc:
                try:
                    driver.execute_script("arguments[0].click();", btn_switch_to_auto_seat)
                    ret = True
                except Exception as exc:
                    pass

        if button_class_string == "red":
            is_switch_to_auto_seat = True

    return is_switch_to_auto_seat

def ticket_switch_to_auto_seat(driver):
    is_switch_to_auto_seat = False

    btn_switch_to_auto_seat = None
    try:
        my_css_selector = 'input[value="BUY_TYPE_2"]'
        btn_switch_to_auto_seat = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find BUY_TYPE_2 input fail")
        pass

    if not btn_switch_to_auto_seat is None:
        button_class_string = None
        try:
            button_class_string = form_verifyCode.get_attribute('checked')
        except Exception as exc:
            #print("get_attribute('class') fail")
            pass

        if button_class_string is None:
            button_class_string = ""

        if button_class_string == "":
            try:
                btn_switch_to_auto_seat.click()
                is_switch_to_auto_seat = True
            except Exception as exc:
                try:
                    driver.execute_script("arguments[0].click();", btn_switch_to_auto_seat)
                    ret = True
                except Exception as exc:
                    pass

        if button_class_string == "red":
            is_switch_to_auto_seat = True

    return is_switch_to_auto_seat


def kham_performance(driver, config_dict, ocr, Captcha_Browser, domain_name, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    is_captcha_sent = False
    if auto_fill_ticket_number:
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = kham_area_auto_select(driver, domain_name, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = kham_area_auto_select(driver, domain_name, config_dict, "")

        if is_need_refresh:
            if show_debug_message:
                print("is_need_refresh:", is_need_refresh)
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # udn use reCaptcha.
        if not('udnfunlife' in domain_name):
            is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

    return is_price_assign_by_bot, is_captcha_sent


def kham_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False

    form_verifyCode = None
    try:
        my_css_selector = 'input[value="驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find blockLogin input fail")
        try:
            my_css_selector = 'input[placeholder="驗證碼"]'
            form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            try:
                my_css_selector = 'input[placeholder="請輸入圖片上符號"]'
                form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                try:
                    my_css_selector = 'input[type="text"][maxlength="4"]'
                    form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                except Exception as exc:
                    pass


    is_start_to_input_answer = False
    if not form_verifyCode is None:
        if len(answer) > 0:
            inputed_value = None
            try:
                inputed_value = form_verifyCode.get_attribute('value')
            except Exception as exc:
                print("find verify code fail")
                pass

            if inputed_value is None:
                inputed_value = ""

            if inputed_value == "驗證碼":
                try:
                    form_verifyCode.clear()
                except Exception as exc:
                    print("clear verify code fail")
                    pass
            else:
                if len(inputed_value) > 0:
                    print("captcha text inputed:", inputed_value, "target answer:", answer)
                    is_verifyCode_editing = True
                else:
                    is_start_to_input_answer = True
        else:
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass

    if is_start_to_input_answer:
        #answer=answer.upper()
        #print("start to fill answer.")
        try:
            form_verifyCode.clear()
            form_verifyCode.send_keys(answer)
        except Exception as exc:
            print("send_keys ocr answer fail:", answer)

    return is_verifyCode_editing

def kham_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None
    if not ocr is None:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.request_captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'chk_pic'
            image_element = None
            try:
                my_css_selector = "#" + image_id
                image_element = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not image_element is None:
                try:
                    driver.set_script_timeout(1)
                    form_verifyCode_base64 = driver.execute_async_script("""
                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        var img = document.getElementById('%s');
                        if(img!=null) {
                        canvas.height = img.naturalHeight;
                        canvas.width = img.naturalWidth;
                        context.drawImage(img, 0, 0);
                        callback = arguments[arguments.length - 1];
                        callback(canvas.toDataURL()); }
                        """ % (image_id))
                    if not form_verifyCode_base64 is None:
                        img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
                except Exception as exc:
                    if show_debug_message:
                        print("canvas exception:", str(exc))
                    pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var = kham_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                kham_keyin_captcha_code(driver)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("click captcha again")
                    if True:
                        # selenium solution.
                        jquery_string = '$("#chk_pic").attr("src", "/pic.aspx?TYPE=%s&ts=" + new Date().getTime());' % (model_name)
                        driver.execute_script(jquery_string)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            time.sleep(0.3)
                    else:
                        # Non_Browser solution.
                        if not Captcha_Browser is None:
                            new_captcha_url = Captcha_Browser.request_refresh_captcha() #取得新的CAPTCHA
                            if new_captcha_url != "":
                                #PS:[TODO]
                                #tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
                                pass
    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            kham_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    #PS: need a 'auto assign seat' feature to enable away_from_keyboard feature.
    away_from_keyboard_enable = False

    is_captcha_sent = False
    previous_answer = None
    last_url, is_quit_bot = get_current_url(driver)
    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_sumbited = kham_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name)

        # TODO: must ensure the answer is corrent...
        is_captcha_sent = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

        current_url, is_quit_bot = get_current_url(driver)
        if current_url != last_url:
            break

    return is_captcha_sent

def kham_check_captcha_text_error(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_reset_password_text = False
    el_message = None
    try:
        my_css_selector = 'div.ui-dialog > div#dialog-message.ui-dialog-content'
        el_message = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_message is None:
            el_message_text = el_message.text
            if show_debug_message:
                print("el_message_text", el_message_text)
            if el_message_text is None:
                el_message_text = ""
            if "【驗證碼】輸入錯誤" in el_message_text:
                is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
                is_reset_password_text = True
                kham_keyin_captcha_code(driver)
    except Exception as exc:
        pass

    return is_reset_password_text

def kham_check_realname_dialog(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_realname_dialog_found = False
    el_message = None
    try:
        my_css_selector = 'div.ui-dialog > div#dialog-message.ui-dialog-content'
        el_message = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_message is None:
            el_message_text = el_message.text
            if show_debug_message:
                print("dialog message:", el_message_text)
            if el_message_text is None:
                el_message_text = ""
            # 檢查是否為實名制通知彈窗
            if "個人實名制入場" in el_message_text or "實名制" in el_message_text:
                if show_debug_message:
                    print("Found realname dialog, clicking OK button...")
                is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
                is_realname_dialog_found = True
    except Exception as exc:
        if show_debug_message:
            print("kham_check_realname_dialog exception:", exc)
        pass

    return is_realname_dialog_found

def kham_allow_not_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = 'table.eventTABLE > tbody > tr > td > input[type="checkbox"]'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ibon adjacent_seat checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def kham_main(driver, url, config_dict, ocr, Captcha_Browser):
    global kham_dict
    if not 'kham_dict' in globals():
        kham_dict = {}
        kham_dict["is_popup_checkout"] = False
        kham_dict["played_sound_order"] = False

    domain_name = url.split('/')[2]

    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    home_url_list = ['https://kham.com.tw/'
    ,'https://kham.com.tw/application/utk01/utk0101_.aspx'
    ,'https://kham.com.tw/application/utk01/utk0101_03.aspx'
    ,'https://ticket.com.tw/application/utk01/utk0101_.aspx'
    ,'https://tickets.udnfunlife.com/application/utk01/utk0101_.aspx'
    ]
    for each_url in home_url_list:
        if each_url == url.lower():
            #is_button_clicked = press_button(driver, By.CSS_SELECTOR,'.closeBTN')
            clean_tag_by_selector(driver, ".popoutBG")

            if config_dict["ocr_captcha"]["enable"]:
                if not Captcha_Browser is None:
                    Captcha_Browser.set_cookies(driver.get_cookies())
                    Captcha_Browser.set_domain(domain_name)
            
            # 登入後自動跳轉回原始購票頁面
            if config_dict["homepage"] != url:
                if show_debug_message:
                    print(f"Login completed, redirecting to target page: {config_dict['homepage']}")
                try:
                    driver.get(config_dict["homepage"])
                    return  # 結束函式，讓主迴圈重新處理目標頁面
                except Exception as e:
                    if show_debug_message:
                        print(f"Redirect failed: {e}")
            break

    # 檢查並處理實名制通知彈窗
    kham_check_realname_dialog(driver, config_dict)

    #https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=XXX
    if 'utk0201_.aspx?product_id=' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            # 檢查實名制彈窗
            kham_check_realname_dialog(driver, config_dict)
            # 點擊購票按鈕
            kham_go_buy_redirect(driver, domain_name)
            
            # 等待頁面載入後處理驗證碼
            time.sleep(1.0)
            
            # 再次檢查實名制彈窗（頁面載入後可能出現）
            kham_check_realname_dialog(driver, config_dict)
            
            # 檢查是否有驗證碼需要處理
            if config_dict["ocr_captcha"]["enable"]:
                if show_debug_message:
                    print("Starting captcha processing for purchase page...")
                model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK0201"
                if len(model_name) > 7:
                    model_name = model_name[:7]
                
                # 設定 captcha 相關參數
                captcha_url = '/pic.aspx?TYPE=%s_001' % (model_name)
                if not Captcha_Browser is None:
                    Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)
                
                # 執行 OCR 驗證碼處理
                is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)
                
                # 驗證碼處理完成後，輸入票券數量並提交
                if is_captcha_sent:
                    # 輸入票券數量
                    select_query = '#AMOUNT'
                    is_ticket_number_assigned = assign_text(driver, By.CSS_SELECTOR, select_query, str(config_dict["ticket_number"]), overwrite_when="0")
                    
                    if is_ticket_number_assigned:
                        # 點擊加入購物車按鈕
                        my_css_selector = 'button[onclick="addShoppingCart();return false;"]'
                        is_button_clicked = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                        if not is_button_clicked:
                            # 備用選取器
                            my_css_selector = '#addcart button.red'
                            is_button_clicked = press_button(driver, By.CSS_SELECTOR, my_css_selector)

    # https://kham.com.tw/application/UTK02/UTK0201_00.aspx?PRODUCT_ID=N28TFATD
    if 'utk0201_00.aspx?product_id=' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            if config_dict["date_auto_select"]["enable"]:
                kham_product(driver, domain_name, config_dict)

    if '/application/utk01/utk0101_.aspx' in url.lower():
        date_auto_select_enable = config_dict["date_auto_select"]["enable"]
        if date_auto_select_enable:
            kham_product(driver, domain_name, config_dict)

    # for udn
    if 'udnfunlife' in domain_name:
        #auto_close_tab = False
        auto_close_tab = True
        if auto_close_tab:
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count > 1:
                    #print("window_handles_count:", window_handles_count)
                    driver.switch_to.window(driver.window_handles[0])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(0.2)
            except Exception as exc:
                print(exc)
                pass

        # udn sign in.
        if 'https://tickets.udnfunlife.com/application/utk01/utk0101_.aspx' == url.lower():
            udn_account = config_dict["accounts"]["udn_account"]
            udn_password = config_dict["accounts"]["udn_password"].strip()
            if len(udn_account) > 4:
                udn_login(driver, udn_account, udn_password)

        if 'utk0203_.aspx?product_id=' in url.lower():
            select_query = 'input.yd_counterNum'
            ticket_number_text = None
            try:
                ticket_number_text = driver.find_element(By.CSS_SELECTOR, select_query)
            except Exception as exc:
                pass

            if not ticket_number_text is None:
                # layout format #1
                is_ticket_number_assigned = assign_text(driver, By.CSS_SELECTOR, select_query, str(config_dict["ticket_number"]), overwrite_when="0")
                if is_ticket_number_assigned:
                    is_button_clicked = press_button(driver, By.CSS_SELECTOR,'#buttonNext')
            else:
                # layout format #2
                date_auto_select_enable = config_dict["date_auto_select"]["enable"]
                if date_auto_select_enable:
                    kham_product(driver, domain_name, config_dict)

        if 'utk0222_02.aspx?product_id=' in url.lower():
            model_name = url.split('/')[5]
            if len(model_name) > 7:
                model_name=model_name[:7]
            is_price_assign_by_bot, is_captcha_sent = kham_performance(driver, config_dict, ocr, Captcha_Browser, domain_name, model_name)

            is_ticket_number_sent = assign_text(driver, By.CSS_SELECTOR, 'input#QRY2', str(config_dict["ticket_number"]), overwrite_when="0")
            if is_ticket_number_sent:
                is_fastbuy_pressed = press_button(driver, By.CSS_SELECTOR,'input#f_btn')

    else:
        # kham / ticket.

        # https://kham.com.tw/application/UTK02/UTK0204_.aspx?PERFORMANCE_ID=N28UQPA1&PRODUCT_ID=N28TFATD
        if '.aspx?performance_id=' in url.lower() and 'product_id=' in url.lower():
            model_name = url.split('/')[5]
            if len(model_name) > 7:
                model_name=model_name[:7]
            captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
            #PS: need set cookies once, if user change domain.
            if not Captcha_Browser is None:
                Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

            is_captcha_sent = False

            # 檢查實名制通知彈窗
            kham_check_realname_dialog(driver, config_dict)

            if config_dict["ocr_captcha"]["enable"]:
                is_reset_password_text = kham_check_captcha_text_error(driver, config_dict)
                if is_reset_password_text:
                    is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

            my_css_selector = 'div.ui-dialog-buttonset > button.ui-button'
            is_button_clicked = press_button(driver, By.CSS_SELECTOR, my_css_selector)
            if config_dict["area_auto_select"]["enable"]:
                if "ticket.com.tw" in url:
                    is_switch_to_auto_seat = ticket_switch_to_auto_seat(driver)
                else:
                    is_switch_to_auto_seat = kham_switch_to_auto_seat(driver)

                if "kham.com.tw" in url:
                    select_query = "tr.Soldout"
                    more_script = """var ticketItems = document.querySelectorAll('tr.status_tr');
                    if(ticketItems.length==0) { location.reload(); }
                    """
                    clean_tag_by_selector(driver, select_query, more_script)

                is_price_assign_by_bot, is_captcha_sent = kham_performance(driver, config_dict, ocr, Captcha_Browser, domain_name, model_name)

                # this is a special case, not performance_price_area_id, directly input ticket_nubmer in #amount.
                if "ticket.com.tw" in url:
                    select_query = 'div.qty-select input[type="text"]'
                else:
                    # kham
                    select_query = '#AMOUNT'
                is_ticket_number_assigned = assign_text(driver, By.CSS_SELECTOR, select_query, str(config_dict["ticket_number"]), overwrite_when="0")

                if config_dict["advanced"]["disable_adjacent_seat"]:
                    if "ticket.com.tw" in url:
                        is_finish_checkbox_click = ticket_allow_not_adjacent_seat(driver, config_dict)
                    if "kham.com.tw" in url:
                        is_finish_checkbox_click = kham_allow_not_adjacent_seat(driver, config_dict)

                if show_debug_message:
                    print("is_ticket_number_assigned:", is_ticket_number_assigned)
                    print("is_captcha_sent:", is_captcha_sent)
                if is_ticket_number_assigned:
                    if is_captcha_sent:
                        el_btn = None
                        my_css_selector = '#addcart'
                        if "ticket.com.tw" in url:
                            my_css_selector = 'a[onclick="return chkCart();"]'
                        try:
                            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                            if not el_btn is None:
                                el_btn.click()
                        except Exception as exc:
                            if show_debug_message:
                                print("find addcart button fail")
                                print(exc)
                            pass


        # 年代售票座位選擇頁面 (UTK0205) - 針對 ticket.com.tw
        if "ticket.com.tw" in domain_name and 'utk0205' in url.lower():
            if show_debug_message:
                print("Detected ticket.com.tw UTK0205 seat selection page")
            
            # 呼叫年代售票座位選擇主函式
            is_seat_selection_success = ticket_seat_main(driver, config_dict, ocr, Captcha_Browser, domain_name)
            
            if show_debug_message:
                print(f"Seat selection result: {is_seat_selection_success}")

        #https://kham.com.tw/application/UTK02/UTK0205_.aspx?PERFORMANCE_ID=XXX&GROUP_ID=30&PERFORMANCE_PRICE_AREA_ID=XXX
        if '.aspx?performance_id=' in url.lower() and 'performance_price_area_id=' in url.lower():
            model_name = url.split('/')[5]
            if len(model_name) > 7:
                model_name=model_name[:7]
            captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
            #PS: need set cookies once, if user change domain.
            if not Captcha_Browser is None:
                Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

            is_captcha_sent = False
            if config_dict["ocr_captcha"]["enable"]:
                is_reset_password_text = kham_check_captcha_text_error(driver, config_dict)
                if is_reset_password_text:
                    is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

            if config_dict["advanced"]["disable_adjacent_seat"]:
                if "ticket.com.tw" in url:
                    is_finish_checkbox_click = ticket_allow_not_adjacent_seat(driver, config_dict)
                else:
                    is_finish_checkbox_click = kham_allow_not_adjacent_seat(driver, config_dict)

            is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
            if config_dict["ocr_captcha"]["enable"]:
                if not is_captcha_sent:
                    is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

                if "ticket.com.tw" in url:
                    select_query = 'div.qty-select input[type="text"]'
                else:
                    # kham
                    select_query = '#AMOUNT'
                is_ticket_number_assigned = assign_text(driver, By.CSS_SELECTOR, select_query, str(config_dict["ticket_number"]), overwrite_when="0")

                if is_ticket_number_assigned:
                    if is_captcha_sent:
                        el_btn = None
                        # for kham
                        my_css_selector = 'button[onclick="addShoppingCart();return false;"]'
                        if "ticket.com.tw" in url:
                            my_css_selector = 'a[onclick="return chkCart();"]'
                        try:
                            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                            if not el_btn is None:
                                el_btn.click()
                        except Exception as exc:
                            print("find chkCart button fail")
                            pass

        if '/utk13/utk1306_.aspx' in url.lower():
            is_button_clicked = press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
            if config_dict["ocr_captcha"]["enable"]:
                model_name = url.split('/')[5]
                if len(model_name) > 7:
                    model_name=model_name[:7]
                captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
                #PS: need set cookies once, if user change domain.
                if not Captcha_Browser is None:
                    Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

                kham_account = config_dict["accounts"]["kham_account"]
                kham_password = config_dict["accounts"]["kham_password"].strip()
                if len(kham_account) > 4:
                    kham_login(driver, kham_account, kham_password)


                ticket_account = config_dict["accounts"]["ticket_account"]
                ticket_password = config_dict["accounts"]["ticket_password"].strip()
                if len(ticket_account) > 4:
                    ticket_login(driver, ticket_account, ticket_password)

    # 檢查是否到達結帳頁面 (搶票成功)
    if '/utk02/utk0206_.aspx' in url.lower():
        if show_debug_message:
            print("Reached checkout page - ticket purchase successful!")
        
        # 播放搶票成功通知音效 (只播放一次)
        if config_dict["advanced"]["play_sound"]["order"]:
            if not kham_dict["played_sound_order"]:
                play_sound_while_ordering(config_dict)
            kham_dict["played_sound_order"] = True
        
        # 如果是無頭模式，開啟瀏覽器顯示結帳頁面 (只開啟一次)
        if config_dict["advanced"]["headless"]:
            if not kham_dict["is_popup_checkout"]:
                checkout_url = url
                print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)
                kham_dict["is_popup_checkout"] = True
    else:
        # 重置狀態（當離開結帳頁面時）
        kham_dict["is_popup_checkout"] = False
        kham_dict["played_sound_order"] = False


def ticketplus_date_auto_select(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    # TODO: implement this feature.
    date_keyword_and = ""
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_auto_select_mode:", auto_select_mode)
        print("date_keyword:", date_keyword)

    area_list = None
    try:
        area_list = driver.find_elements(By.CSS_SELECTOR, 'div#buyTicket > div.sesstion-item > div.row')
        if not area_list is None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                if show_debug_message:
                    print("[TicketPlus] Empty date list, retrying...")
                time.sleep(0.2)
    except Exception as exc:
        if show_debug_message:
            print("[TicketPlus] Failed to find #buyTicket element:", exc)

    url_keyword='apis.ticketplus.com.tw/config/api/'
    url_list = get_performance_log(driver, url_keyword)
    if area_list_count == 0:
        if len(url_list)==0:
            area_list = None

    # '立即購票' -> '立即購買'
    find_ticket_text_list = ['>立即購','尚未開賣']
    sold_out_text_list = ['銷售一空']

    matched_blocks = None
    formated_area_list = None
    is_vue_ready = True

    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:
                    if '<div class="v-progress-circular__info"></div>' in row_html:
                        # vue not applied.
                        is_vue_ready = False
                        break

                if len(row_text) > 0:
                    row_is_enabled=False
                    for text_item in find_ticket_text_list:
                        if text_item in row_html:
                            row_is_enabled = True
                            break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                if sold_out_item in row_text:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                    if row_is_enabled:
                        formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                date_keyword = util.format_keyword_string(date_keyword)
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)

                matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    is_date_clicked = False
    if is_vue_ready:
        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
        if not target_area is None:
            target_button = None
            try:
                target_button = target_area.find_element(By.CSS_SELECTOR, 'button')
                if not target_button is None:
                    if target_button.is_enabled():
                        if show_debug_message:
                            print("[TicketPlus] Clicking date button")
                        target_button.click()
                        is_date_clicked = True
                else:
                    if show_debug_message:
                        print("[TicketPlus] Target button not found in row")
            except Exception as exc:
                if show_debug_message:
                    print("[TicketPlus] Button interaction failed:", exc)

                if not target_button is None:
                    #print("try to click button fail, force click by js.")
                    try:
                        #driver.execute_script("arguments[0].click();", target_button)
                        pass
                    except Exception as exc:
                        pass

        # [PS]: current reload condition only when
        if auto_reload_coming_soon_page_enable:
            if not is_date_clicked:
                if not formated_area_list is None:
                    if len(formated_area_list) == 0:
                        # in fact, no need reload on /activity/ page, should reload in /order/ page.
                        try:
                            if show_debug_message:
                                print("[TicketPlus] Refreshing page due to no available dates")
                            driver.refresh()
                            time.sleep(0.3)
                        except Exception as exc:
                            if show_debug_message:
                                print("[TicketPlus] Page refresh failed:", exc)

                        if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])


    return is_date_clicked

def ticketplus_assign_ticket_number(target_area, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False

    ticket_number_div = None
    try:
        my_css_selector = 'div.count-button > div'
        ticket_number_div = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        if show_debug_message:
            print("find div.count-button fail")
        pass

    if not ticket_number_div is None:
        ticket_number = config_dict["ticket_number"]

        ticket_number_text_int = 0
        ticket_number_text = ""
        try:
            ticket_number_text = ticket_number_div.text
        except Exception as exc:
            print("get ticket_number_text fail")
            pass

        if ticket_number_text is None:
            ticket_number_text = ""
        if len(ticket_number_text) > 0:
            ticket_number_text_int = int(ticket_number_text)
            if show_debug_message:
                print("ticket_number_text_int:", ticket_number_text_int)

            if ticket_number_text_int < ticket_number:
                ticket_number_plus = None
                try:
                    my_css_selector = 'button > span > i.mdi-plus'
                    ticket_number_plus = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
                except Exception as exc:
                    if show_debug_message:
                        print("find ticket_number_plus fail")

                if not ticket_number_plus is None:
                    # add
                    add_count = ticket_number - ticket_number_text_int
                    if show_debug_message:
                        print("add_count:", add_count)
                    for i in range(add_count):
                        if show_debug_message:
                            print("click on plus button #",i)
                        try:
                            ticket_number_plus.click()
                            is_price_assign_by_bot = True
                            if i==0:
                                time.sleep(0.2)

                            ticket_number_text = ticket_number_div.text
                            if len(ticket_number_text) > 0:
                                ticket_number_text_int = int(ticket_number_text)
                                if show_debug_message:
                                    print("ticket_number_text_int:", ticket_number_text_int)
                                if ticket_number_text_int >= ticket_number:
                                    print("match target ticket count (now/target):", ticket_number_text_int, ticket_number)
                                    break
                        except Exception as exc:
                            pass
            else:
                # match target ticket number.
                is_price_assign_by_bot = True
    return is_price_assign_by_bot

def ticketplus_order_expansion_auto_select(driver, config_dict, area_keyword_item, current_layout_style):
    # show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_need_refresh = False
    is_click_on_folder = False

    matched_blocks = None

    if show_debug_message:
        print(f"[TicketPlus] Layout style: {current_layout_style}")

    area_list = None
    try:
        # style 2: .text-title
        my_css_selector = "div.rwd-margin > div.text-title"
        if current_layout_style == 1:
            # style 1: .text-title
            # PS: price info header format also is div.v-expansion-panels > div.v-expansion-panel
            my_css_selector = "div.seats-area > div.v-expansion-panel > div.v-expansion-panel-content > div.v-expansion-panel-content__wrap > div.text-title"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)

        if current_layout_style == 1:
            if len(area_list)==0:
                # not found closed-folder button, try scan opened-text-title.
                if show_debug_message:
                    print("[TicketPlus] No closed folders found, scanning opened areas")

                my_css_selector = 'div.price-group > div'
                price_group_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
                if len(price_group_list) > 0:
                    # price group style.
                    my_css_selector = 'div.seats-area > div.v-expansion-panel'
                    area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
                else:
                    # no price group style.
                    my_css_selector = 'div.seats-area > div.v-expansion-panel[aria-expanded="false"]'
                    area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
                    # triger re-query again.
                    is_click_on_folder = True

    except Exception as exc:
        if show_debug_message:
            if current_layout_style == 1:
                print("[TicketPlus] Failed to find .v-expansion-panels area list")
            if current_layout_style == 2:
                print("[TicketPlus] Failed to find .text-title area list")

    formated_area_list = None
    if not area_list is None:
        area_list_count = len(area_list)
        if show_debug_message:
            print(f"[TicketPlus] Found {area_list_count} areas, keyword: '{area_keyword_item}'")

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            soldout_count = 0
            for row in area_list:
                row_text = ""
                row_html = ""
                try:
                    #row_text = row.text
                    row_html = row.get_attribute('innerHTML')
                    row_text = util.remove_html_tags(row_html)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    # error, exit loop
                    break

                # for style_2
                if len(row_text) > 0:
                    if '剩餘 0' in row_text:
                        soldout_count += 1
                        row_text = ""

                if len(row_text) > 0:
                    if '已售完' in row_text:
                        soldout_count += 1
                        row_text = ""

                # for style_1
                if len(row_text) > 0:
                    if '剩餘：0' in row_text:
                        soldout_count += 1
                        row_text = ""

                if len(row_text) > 0:
                    if ' soldout"' in row_html:
                        soldout_count += 1
                        row_text = ""

                if len(row_text) > 0:
                    if ' soldout ' in row_html:
                        soldout_count += 1
                        row_text = ""

                if len(row_text) > 0:
                    if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                        row_text = ""

                if len(row_text) > 0:
                    formated_area_list.append(row)
                    
                if len(row_text) > 0:
                    if '開賣時間' in row_text:
                        is_need_refresh = True

            if soldout_count > 0:
                if show_debug_message:
                    print(f"[TicketPlus] {soldout_count} areas sold out")
                if area_list_count == soldout_count:
                    formated_area_list = None
                    is_need_refresh = True
        else:
            if show_debug_message:
                print("[TicketPlus] Area list is empty")
    else:
        if show_debug_message:
            print("[TicketPlus] Area list is None")

    is_price_panel_expanded = False
    if not formated_area_list is None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print(f"[TicketPlus] {area_list_count} available areas after filtering")

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_item) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                for row in formated_area_list:
                    row_text = ""
                    row_html = ""
                    try:
                        #row_text = row.text
                        row_html = row.get_attribute('innerHTML')
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        # error, exit loop
                        break

                    if len(row_text) > 0:
                        row_text = util.format_keyword_string(row_text)
                        if show_debug_message:
                            print("row_text:", row_text)

                        is_match_area = False

                        if len(area_keyword_item) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_item.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = util.format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_area:
                            matched_blocks.append(row)

                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                if ' aria-expanded="true"' in row_html:
                                    is_price_panel_expanded = True
                                break

            if show_debug_message:
                print(f"[TicketPlus] Matched {len(matched_blocks)} areas")

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not matched_blocks is None:
        if len(matched_blocks) == 0:
            is_need_refresh = True
            if show_debug_message:
                print("[TicketPlus] No matched areas, refreshing needed")

    # for style_1, need click once.
    if show_debug_message:
        print(f"[TicketPlus] Layout style: {current_layout_style}, panel expanded: {is_price_panel_expanded}")

    is_clicked = False
    if not is_price_panel_expanded:
        if current_layout_style==1:
            if not target_area is None:
                try:
                    #PS: must click on button instead of div to expand lay.
                    if show_debug_message:
                        print(f'[TicketPlus] Selecting area: {target_area.text}')
                    my_css_selector = 'button'
                    target_button = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
                    target_button.click()
                    is_clicked = True
                    if show_debug_message:
                        print("[TicketPlus] Area button clicked")

                    #target_area.click()
                except Exception as exc:
                    if show_debug_message:
                        print("[TicketPlus] Area click failed, using JavaScript fallback")
                        print(exc)
                    # use plan B
                    try:
                        js = """let titleBar = document.getElementById("titleBar");
                        if(titleBar!=null) {titleBar.innerHTML="";}
                        arguments[0].scrollIntoView();
                        arguments[0].firstChild.click();
                        """
                        driver.execute_script(js, target_area)
                    except Exception as exc:
                        #print(exc)
                        pass

    is_reset_query = False
    if is_click_on_folder:
        if is_clicked:
            time.sleep(0.2)
            is_reset_query = True

    is_price_assign_by_bot = False
    if not is_reset_query:
        if not target_area is None:
            for retry_index in range(2):
                # PS: each price have each price div, so need pass parent div to increase ticket number.
                is_price_assign_by_bot = ticketplus_assign_ticket_number(target_area, config_dict)
                if is_price_assign_by_bot:
                    break

    return is_need_refresh, is_price_assign_by_bot, is_reset_query


def ticketplus_order_expansion_panel(driver, config_dict, current_layout_style):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        if show_debug_message:
            print(f"[TicketPlus] Area keyword: '{area_keyword}'")

        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = []
            try:
                area_keyword_array = json.loads("["+ area_keyword +"]")
            except Exception as exc:
                area_keyword_array = []

            is_reset_query = False
            for retry_idx in range(2):
                for area_keyword_item in area_keyword_array:
                    is_need_refresh, is_price_assign_by_bot, is_reset_query = ticketplus_order_expansion_auto_select(driver, config_dict, area_keyword_item, current_layout_style)
                    if is_reset_query:
                        break
                    if not is_need_refresh:
                        break
                    else:
                        if show_debug_message:
                            print(f"[TicketPlus] Refresh needed for keyword: '{area_keyword_item}'")

                # when reset query, do query again.
                if not is_reset_query:
                    break

        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot, is_reset_query = ticketplus_order_expansion_auto_select(driver, config_dict, "", current_layout_style)

        if is_need_refresh:
            # vue mode, refresh need to check more conditions to check.
            if show_debug_message:
                print('[TicketPlus] Starting page refresh')
            
            refresh_clicked = False
            overlays = driver.find_elements(By.CSS_SELECTOR, 'div.v-overlay')
            for overlay in overlays:
                try:
                    refresh_button = driver.find_element(By.CSS_SELECTOR, 'button.float-btn')
                    if refresh_button:
                        refresh_button.click()
                        refresh_clicked = True
                        break
                except Exception as exc:
                    if show_debug_message:
                        print("[TicketPlus] Float button not found in overlay")
                    pass

            # 如果找不到 float-btn，使用標準的頁面刷新
            if not refresh_clicked:
                try:
                    if show_debug_message:
                        print("[TicketPlus] Using browser refresh as fallback")
                    driver.refresh()
                    time.sleep(0.3)
                except Exception as exc:
                    if show_debug_message:
                        print("[TicketPlus] Browser refresh failed:", exc)
                    pass

            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_price_assign_by_bot

def ticketplus_order_exclusive_code(driver, config_dict, fail_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    question_selector = ".exclusive-code > form > div"
    question_text = get_text_by_selector(driver, question_selector, 'innerText')
    is_answer_sent = False
    is_question_popup = False
    if len(question_text) > 0:
        is_question_popup = True
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                answer_list = util.guess_tixcraft_question(driver, question_text)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("answer_list:", answer_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.

        input_text_css = ".exclusive-code > form > div.v-input > div > div > div > input[type='text']"
        next_step_button_css = ""
        submit_by_enter = True
        check_input_interval = 0.2
        is_answer_sent, fail_list = fill_common_verify_form(driver, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return is_answer_sent, fail_list, is_question_popup

def get_performance_log(driver, url_keyword):
    url_list = []
    try:
        logs = driver.get_log("performance")

        for log in logs:
            network_log = json.loads(log["message"])["message"]
            if ("Network.response" in network_log["method"]
                or "Network.request" in network_log["method"]
                or "Network.webSocket" in network_log["method"]):
                if 'request' in network_log["params"]:
                    if 'url' in network_log["params"]["request"]:
                        if url_keyword in network_log["params"]["request"]["url"]:
                            url_list.append(network_log["params"]["request"]["url"])
    except Exception as e:
        #raise e
        pass

    return url_list


def ticketplus_order_auto_reload_coming_soon(driver):
    #r = driver.execute_script("return window.performance.getEntries();")

    is_reloading = False
    url_keyword='apis.ticketplus.com.tw/config/api/'
    url_list = get_performance_log(driver, url_keyword)
    #print("url_list:", url_list)

    getSeatsByTicketAreaIdUrl = ""
    for requset_url in url_list:
        if 'get?productId=' in requset_url:
            getSeatsByTicketAreaIdUrl = requset_url
            break
        if 'get?ticketAreaId=' in requset_url:
            getSeatsByTicketAreaIdUrl = requset_url
            break

    try:
        if len(getSeatsByTicketAreaIdUrl) > 0:
            js = """//var t = JSON.parse(Cookies.get("user")) ? JSON.parse(Cookies.get("user")).access_token : "";
//var callback = arguments[arguments.length - 1];
fetch("%s",{
//headers: {authorization: "Bearer ".concat(t)}
}).then(function (response) {
return response.json();
}).then(function (data) {
if(data.result.product.length>0)
if(data.result.product[0].status=="pending") {
location.reload();
//callback(true);
}
}).catch(function (err){
//console.log(err);
});
""" % getSeatsByTicketAreaIdUrl
            driver.set_script_timeout(0.1)
            driver.execute_script(js)
            SeatsByTicketAreaDict = None
            #SeatsByTicketAreaDict = driver.execute_async_script(js)
            if not SeatsByTicketAreaDict is None:
                is_reloading = SeatsByTicketAreaDict
    except Exception as exc:
        #print(exc)
        pass

    return is_reloading

def ticketplus_order(driver, config_dict, ocr, Captcha_Browser, ticketplus_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # 等待頁面載入完成，避免找不到按鈕
    time.sleep(0.5)

    # 關閉登入 dialog（如果存在）
    try:
        login_dialog_close = driver.find_element(By.CSS_SELECTOR, 'div.v-dialog__content button.mdi-close')
        if login_dialog_close:
            if show_debug_message:
                print("closing login dialog...")
            login_dialog_close.click()
            time.sleep(0.5)
    except Exception as exc:
        if show_debug_message:
            print("no login dialog found or failed to close")
        pass

    next_step_button = None
    # PS: only button disabled = True to continue.
    is_button_disabled = False
    current_layout_style = 0
    try:
        # for style_2
        my_css_selector = "div.order-footer > div.container > div.row > div > button.nextBtn"
        next_step_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not next_step_button is None:
            if not next_step_button.is_enabled():
                is_button_disabled = True
                current_layout_style = 2
    except Exception as exc:
        if show_debug_message:
            print("find next_step_button (style_2) fail")
            #print(exc)
            pass

        # for style_1
        try:
            my_css_selector = "div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn"
            next_step_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if not next_step_button is None:
                if not next_step_button.is_enabled():
                    is_button_disabled = True
                    current_layout_style = 1
        except Exception as exc2:
            if show_debug_message:
                print("find next_step_button (style_1) fail")
                #print(exc2)
                pass

        # for style_3 (data3-like structure)
        if not is_button_disabled:
            try:
                my_css_selector = "div.order-footer button.nextBtn"
                next_step_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                if not next_step_button is None:
                    if not next_step_button.is_enabled():
                        is_button_disabled = True
                        current_layout_style = 3
            except Exception as exc3:
                if show_debug_message:
                    print("find next_step_button (style_3) fail")
                    #print(exc3)
                    pass


    #print("is_button_disabled:", is_button_disabled)
    is_captcha_sent = False
    if is_button_disabled:
        is_price_assign_by_bot = False
        is_price_assign_by_bot = ticketplus_order_expansion_panel(driver, config_dict, current_layout_style)

        if not is_price_assign_by_bot:
            is_price_assign_by_bot = ticketplus_assign_ticket_number(driver, config_dict)

        is_question_popup = False
        is_answer_sent = False
        #print("is_price_assign_by_bot", is_price_assign_by_bot)
        if is_price_assign_by_bot:
            is_answer_sent, ticketplus_dict["fail_list"], is_question_popup = ticketplus_order_exclusive_code(driver, config_dict, ticketplus_dict["fail_list"])

            auto_submit = True
            if auto_submit:
                # 等待按鈕從 disabled 變成 enabled
                if show_debug_message:
                    print("waiting for button to become enabled...")
                for wait_idx in range(10):  # 最多等待 5 秒
                    try:
                        next_btn = None
                        # 按照 current_layout_style 選擇對應的按鈕
                        if current_layout_style == 2:
                            next_btn = driver.find_element(By.CSS_SELECTOR, "div.order-footer > div.container > div.row > div > button.nextBtn")
                        elif current_layout_style == 1:
                            next_btn = driver.find_element(By.CSS_SELECTOR, "div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn")
                        elif current_layout_style == 3:
                            next_btn = driver.find_element(By.CSS_SELECTOR, "div.order-footer button.nextBtn")

                        if next_btn and next_btn.is_enabled():
                            if show_debug_message:
                                print(f"button is enabled after {wait_idx * 0.5} seconds")
                            break
                    except Exception as exc:
                        pass
                    time.sleep(0.5)
                else:
                    if show_debug_message:
                        print("button still disabled after 5 seconds, proceeding anyway")

                # 多次嘗試點擊按鈕，增加重試機制
                is_form_sumbited = False
                for retry in range(3):
                    if show_debug_message and retry > 0:
                        print(f"button click retry #{retry}")

                    # 嘗試 style_2
                    my_css_selector = "div.order-footer > div.container > div.row > div > button.nextBtn"
                    is_form_sumbited = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    if is_form_sumbited:
                        break

                    # 嘗試 style_1
                    my_css_selector = "div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn"
                    is_form_sumbited = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    if is_form_sumbited:
                        break

                    # 嘗試 style_3 (data3-like structure)
                    my_css_selector = "div.order-footer button.nextBtn"
                    is_form_sumbited = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    if is_form_sumbited:
                        break

                    # 如果還沒成功，等待一下再重試
                    if retry < 2:
                        time.sleep(1)

                if is_form_sumbited:
                    time.sleep(0.5)
                print("is_form_sumbited", is_form_sumbited)

    return ticketplus_dict

def ticketplus_order_ocr(driver, config_dict, ocr, Captcha_Browser):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    is_captcha_sent = False
    previous_answer = None
    last_url, is_quit_bot = get_current_url(driver)
    for redo_ocr in range(19):
        is_need_redo_ocr, previous_answer, is_form_sumbited = ticketplus_auto_ocr(driver, config_dict, ocr, previous_answer, Captcha_Browser)

        # TODO: must ensure the answer is corrent...
        if is_form_sumbited:
            # re-new captcha, if message popup.
            is_messages_popup = False
            for double_check_message in range(5):
                is_messages_popup = ticketplus_check_and_renew_captcha(driver)
                if is_messages_popup:
                    break
                time.sleep(0.2)

            if not is_messages_popup:
                # still no error
                is_captcha_sent = True
            else:
                is_form_sumbited = False
                is_need_redo_ocr = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

        current_url, is_quit_bot = get_current_url(driver)
        if current_url != last_url:
            break

def ticketplus_auto_ocr(driver, config_dict, ocr, previous_answer, Captcha_Browser):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None

    # check ocr inputed.
    is_verifyCode_editing, is_form_sumbited = ticketplus_keyin_captcha_code(driver)

    is_do_ocr = False
    if not ocr is None:
        if not is_verifyCode_editing:
            is_do_ocr = True

    if is_do_ocr:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.request_captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'span.captcha-img'
            image_element = None
            try:
                my_css_selector = image_id
                image_element = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if not image_element is None:
                try:
                    driver.set_script_timeout(1)
                    form_verifyCode_base64 = driver.execute_async_script("""
function svgToPng(svg, callback) {
  const url = getSvgUrl(svg);
  svgUrlToPng(url, (imgData) => {
    callback(imgData);
    URL.revokeObjectURL(url);
  });
}
function getSvgUrl(svg) {
  return URL.createObjectURL(new Blob([svg], {
    type: 'image/svg+xml'
  }));
}
function svgUrlToPng(svgUrl, callback) {
  const svgImage = document.createElement('img');
  document.body.appendChild(svgImage);
  svgImage.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = svgImage.clientWidth;
    canvas.height = svgImage.clientHeight;
    const canvasCtx = canvas.getContext('2d');
    canvasCtx.fillStyle = 'white';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(svgImage, 0, 0);
    const imgData = canvas.toDataURL('image/png');
    callback(imgData);
  };
  svgImage.src = svgUrl;
}
const img=document.querySelector('%s');
if(img!=null) {
const svg=img.innerHTML;
svgToPng(svg, (imgData) => {
  callback = arguments[arguments.length - 1];
  callback(imgData);
}); }
                        """ % (image_id))
                    if not form_verifyCode_base64 is None:
                        img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
                except Exception as exc:
                    if show_debug_message:
                        print("canvas exception:", str(exc))
                    pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var, is_form_sumbited = ticketplus_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                ticketplus_keyin_captcha_code(driver)
                #tixcraft_toast(driver, "※ OCR辨識失敗Q_Q，驗證碼請手動輸入...")
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("refresh captcha...")
                    my_css_selector = "div.recaptcha-area > div > div > span > i"
                    is_refresh_button_pressed = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    # must have time to load captcha image.
                    time.sleep(0.4)
    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            is_verifyCode_editing, is_form_sumbited = ticketplus_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def ticketplus_check_and_renew_captcha(driver):
    is_messages_popup = False

    v_messages_div = None
    try:
        my_css_selector = 'div.v-messages > div.v-messages__wrapper > div.v-messages__message'
        v_messages_div = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find messages__message div fail")
    if not v_messages_div is None:
        try:
            v_messages_string = v_messages_div.text
            if not v_messages_string is None:
                if len(v_messages_string) > 0:
                    is_messages_popup = True
                    print("error message popup, refresh captcha images.")
                    my_css_selector = "div.recaptcha-area > div > div > span > i"
                    is_refresh_button_pressed = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    # must have time to load captcha image.
                    time.sleep(0.4)
        except Exception as exc:
            pass
    return is_messages_popup

def ticketplus_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False
    is_form_sumbited = False

    # manually keyin verify code.
    form_verifyCode = None
    try:
        my_css_selector = 'input[placeholder="請輸入驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find captcha input fail")

    if not form_verifyCode is None:
        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""

        if inputed_value == "請輸入驗證碼":
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass
        else:
            if len(inputed_value) > 0:
                print("captcha text inputed.")
                form_verifyCode = None
                is_verifyCode_editing = True

    # check wrong answer.
    if is_verifyCode_editing:
        # re-new captcha, if message popup.
        is_messages_popup = ticketplus_check_and_renew_captcha(driver)
        if is_messages_popup:
            is_verifyCode_editing = False
            is_form_sumbited = False

    if not form_verifyCode is None:
        print("answer:", answer)
        if len(answer) > 0:
            #answer=answer.upper()

            is_visible = False
            try:
                if form_verifyCode.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    # make focus()
                    form_verifyCode.click()
                    is_verifyCode_editing = True
                except Exception as exc:
                    pass

                # plan B.
                try:
                    #print("use plan b to focus()")
                    js="""$("#banner").hide();
                    $('input[placeholder="請輸入驗證碼"]').focus();"""
                    driver.set_script_timeout(0.1)
                    driver.execute_script(js)
                except Exception as exc:
                    pass

                try:
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)
                except Exception as exc:
                    print("send_keys ocr answer fail")
                    pass

                # ticketplus not able to send enter key by javascript.
                """
                try:
                    print("use plan b to input()")
                    inputed_value = form_verifyCode.get_attribute('value')
                    if len(inputed_value)==0:
                        js="arguments[0].value = '%s';" % answer
                        driver.set_script_timeout(0.1)
                        driver.execute_script(js, form_verifyCode)
                except Exception as exc:
                    pass
                """

                if auto_submit:
                    # ticketplus not able to send enter key.
                    #form_verifyCode.send_keys(Keys.ENTER)

                    # for style_2
                    my_css_selector = "div.order-footer > div.container > div.row > div > button.nextBtn"
                    is_form_sumbited = press_button(driver, By.CSS_SELECTOR, my_css_selector)
                    if not is_form_sumbited:
                        # for style_1
                        my_css_selector = "div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn"
                        is_form_sumbited = press_button(driver, By.CSS_SELECTOR, my_css_selector)

                    if is_form_sumbited:
                        # must delay 0.5 second wait ajax return.
                        time.sleep(0.5)

                    is_verifyCode_editing = False

    return is_verifyCode_editing, is_form_sumbited

def ticketplus_account_auto_fill(driver, config_dict):
    is_user_signin = False

    # auto fill account info.
    if len(config_dict["accounts"]["ticketplus_account"]) > 0:
        try:
            all_cookies=list_all_cookies(driver)
            if 'user' in all_cookies:
                #print('user in cookie')
                if '%22account%22:%22' in all_cookies['user']:
                    #print('user:', all_cookies['user'])
                    is_user_signin = True
        except Exception as exc:
            print(exc)
            pass

        #print("is_user_signin:", is_user_signin)
        if not is_user_signin:
            is_sign_in_btn_pressed = False
            try:
                my_css_selector = 'button.v-btn > span.v-btn__content > i.mdi-account'
                sign_in_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                if not sign_in_btn is None:
                    sign_in_btn.click()
                    is_sign_in_btn_pressed = True
                    time.sleep(0.2)
            except Exception as exc:
                #print(exc)
                # RWD mode not show sign in icon.
                pass

            #print("is_sign_in_btn_pressed", is_sign_in_btn_pressed)
            if not is_sign_in_btn_pressed:
                #print("rwd mode")
                action_btns = None
                try:
                    my_css_selector = 'div.px-4.py-3.drawerItem.cursor-pointer'
                    action_btns = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
                except Exception as exc:
                    #print(exc)
                    pass
                if action_btns:
                    #print("len:", len(action_btns))
                    if len(action_btns) >= 4:
                        el_pass = None
                        try:
                            my_css_selector = 'input[type="password"]'
                            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                        except Exception as exc:
                            #print(exc)
                            pass

                        is_need_popup_modal = False
                        if el_pass is None:
                            is_need_popup_modal = True
                        else:
                            try:
                                if not el_pass.is_displayed():
                                    is_need_popup_modal = True
                            except Exception as exc:
                                #print(exc)
                                pass

                        print("is_need_popup_modal", is_need_popup_modal)
                        if is_need_popup_modal:
                            print("show sign in modal")
                            #action_btns[3].click()
                            try:
                                driver.set_script_timeout(1)
                                driver.execute_script("arguments[0].click();", action_btns[3])
                            except Exception as exc:
                                #print(exc)
                                pass


            is_account_sent, is_password_sent = ticketplus_account_sign_in(driver, config_dict)

    return is_user_signin


def ticketplus_account_sign_in(driver, config_dict):
    # manually keyin verify code.
    form_account = None
    try:
        my_css_selector = 'input[placeholder="手機號碼 *"]'
        form_account = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass
        #print("find account input fail")

    is_account_sent = False
    if not form_account is None:
        #print("found account field")
        inputed_value = None
        try:
            inputed_value = form_account.get_attribute('value')
        except Exception as exc:
            #print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""

        #print("inputed_value:", inputed_value)
        if inputed_value == "手機號碼 *":
            try:
                form_account.clear()
                form_account.click()
            except Exception as exc:
                print("clear account fail")
                pass
        else:
            if len(inputed_value) > 0:
                #print("account text inputed.")
                pass
            else:
                if len(config_dict["accounts"]["ticketplus_account"]) == 0:
                    try:
                        # solution 1: js.
                        driver.execute_script("if(!(document.activeElement === arguments[0])){arguments[0].focus();}", form_account)
                        # solution 2: selenium.
                        #form_account.click()

                        #wait user input.
                        time.sleep(0.2)
                    except Exception as exc:
                        print("auto-focus account fail")
                        pass
                else:
                    try:
                        form_account.click()
                        form_account.send_keys(config_dict["accounts"]["ticketplus_account"])
                        time.sleep(0.2)
                        is_account_sent = True
                    except Exception as exc:
                        print("auto fill account fail")
                        pass

    is_password_sent = False
    if is_account_sent:
        el_pass = None
        try:
            my_css_selector = 'input[type="password"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not el_pass is None:
            try:
                if el_pass.is_enabled():
                    inputed_text = el_pass.get_attribute('value')
                    if not inputed_text is None:
                        ticketplus_password = config_dict["accounts"]["ticketplus_password"].strip()

                        if len(inputed_text) == 0:
                            el_pass.click()
                            if(len(ticketplus_password)>0):
                                el_pass.send_keys(ticketplus_password)
                                el_pass.send_keys(Keys.ENTER)
                                is_password_sent = True
                        else:
                            if(len(ticketplus_password)>0):
                                if inputed_text == ticketplus_password:
                                    el_pass.click()
                                    el_pass.send_keys(Keys.ENTER)
                                    is_password_sent = True

                        time.sleep(0.2)
            except Exception as exc:
                pass
    return is_account_sent, is_password_sent


# 實名制 (activity)
# 未結帳訂單 (order)
def ticketplus_accept_realname_card(driver):
    select_query = 'div.v-dialog__content > div > div > div > div.row > div > button.primary'
    return press_button(driver, By.CSS_SELECTOR, select_query)

# 好玩其他活動
def ticketplus_accept_other_activity(driver):
    select_query = 'div[role="dialog"] > div.v-dialog > button.primary-1 > span > i.v-icon'
    return press_button(driver, By.CSS_SELECTOR, select_query)

# 購票失敗 您選擇的票種已售完或本活動有限制購票總張數，請詳閱 注意事項
def ticketplus_accept_order_fail(driver):
    select_query = 'div[role="dialog"] > div.v-dialog > div.v-card > div > div.row > div.col > button.v-btn'
    return press_button(driver, By.CSS_SELECTOR, select_query)

def ticketplus_ticket_agree(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        # 優先選擇同意條款，避免文化幣選項
        culture_keywords = ['文化幣', 'culture', '折抵']
        
        # 獲取所有 checkbox，逐一檢查
        all_checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        for checkbox in all_checkboxes:
            try:
                # 檢查父容器是否包含文化幣相關文字
                parent = checkbox.find_element(By.XPATH, '../..')
                parent_content = (parent.get_attribute('outerHTML') or '') + (parent.text or '')
                
                # 跳過文化幣相關的 checkbox
                if any(keyword in parent_content for keyword in culture_keywords):
                    continue
                    
                # 找到非文化幣的 checkbox 就使用
                agree_checkbox = checkbox
                break
            except:
                continue
                    
    except Exception as exc:
        if show_debug_message:
            print("find ticketplus agree checkbox fail:", exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def ticketplus_confirm(driver, config_dict):
    is_checkbox_checked = ticketplus_ticket_agree(driver, config_dict)

def ticketplus_main(driver, url, config_dict, ocr, Captcha_Browser):
    global ticketplus_dict
    if not 'ticketplus_dict' in globals():
        ticketplus_dict = {}
        ticketplus_dict["fail_list"]=[]
        ticketplus_dict["is_popup_confirm"] = False

    home_url_list = ['https://ticketplus.com.tw/']
    is_user_signin = False
    for each_url in home_url_list:
        if each_url == url.lower():
            if config_dict["ocr_captcha"]["enable"]:
                domain_name = url.split('/')[2]
                if not Captcha_Browser is None:
                    Captcha_Browser.set_cookies(driver.get_cookies())
                    Captcha_Browser.set_domain(domain_name)

            is_user_signin = ticketplus_account_auto_fill(driver, config_dict)
            if is_user_signin:
                break

    if is_user_signin:
        # only sign in on homepage.
        if url != config_dict["homepage"]:
            try:
                driver.get(config_dict["homepage"])
            except Exception as e:
                pass

    # https://ticketplus.com.tw/activity/XXX
    if '/activity/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True

        if is_event_page:
            is_button_pressed = ticketplus_accept_realname_card(driver)
            #print("is accept button pressed:", is_button_pressed)
            is_button_pressed = ticketplus_accept_other_activity(driver)
            #print("is accept button pressed:", is_button_pressed)

            if config_dict["date_auto_select"]["enable"]:
                ticketplus_date_auto_select(driver, config_dict)

    #https://ticketplus.com.tw/order/XXX/OOO
    if '/order/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            is_button_pressed = ticketplus_accept_realname_card(driver)
            is_button_pressed = ticketplus_accept_order_fail(driver)

            is_reloading = False

            is_reload_at_webdriver = False
            if not config_dict["browser"] in CONST_CHROME_FAMILY:
                is_reload_at_webdriver = True
            else:
                if not config_dict["advanced"]["chrome_extension"]:
                    is_reload_at_webdriver = True
            if is_reload_at_webdriver:
                # move below code to chrome extension.
                is_reloading = ticketplus_order_auto_reload_coming_soon(driver)

            if not is_reloading:
                ticketplus_dict = ticketplus_order(driver, config_dict, ocr, Captcha_Browser, ticketplus_dict)

    else:
        ticketplus_dict["fail_list"]=[]

    #https://ticketplus.com.tw/confirm/xx/oo
    if '/confirm/' in url.lower() or '/confirmseat/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            #print("is_popup_confirm",ticketplus_dict["is_popup_confirm"])
            if not ticketplus_dict["is_popup_confirm"]:
                ticketplus_dict["is_popup_confirm"] = True
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)
            ticketplus_confirm(driver, config_dict)
        else:
            ticketplus_dict["is_popup_confirm"] = False
    else:
        ticketplus_dict["is_popup_confirm"] = False


def facebook_main(driver, config_dict):
    facebook_account = config_dict["accounts"]["facebook_account"].strip()
    facebook_password = config_dict["accounts"]["facebook_password"].strip()
    if len(facebook_account) > 4:
        facebook_login(driver, facebook_account, facebook_password)
        time.sleep(2)

def get_current_url(driver):
    DISCONNECTED_MSG = ': target window already closed'

    url = ""
    is_quit_bot = False

    try:
        url = driver.current_url
    except NoSuchWindowException:
        print('NoSuchWindowException at this url:', url )
        #print("last_url:", last_url)
        #print("get_log:", driver.get_log('driver'))
        window_handles_count = 0
        try:
            window_handles_count = len(driver.window_handles)
            #print("window_handles_count:", window_handles_count)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[0])
                driver.switch_to.default_content()
                time.sleep(0.2)
        except Exception as excSwithFail:
            #print("excSwithFail:", excSwithFail)
            pass
        if window_handles_count==0:
            try:
                driver_log = driver.get_log('driver')[-1]['message']
                #print("get_log:", driver_log)
                if DISCONNECTED_MSG in driver_log:
                    print('quit bot by NoSuchWindowException')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()
            except Exception as excGetDriverMessageFail:
                #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                except_string = str(excGetDriverMessageFail)
                if 'HTTP method not allowed' in except_string:
                    print('quit bot by close browser')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

    except UnexpectedAlertPresentException as exc1:
        print('UnexpectedAlertPresentException at this url:', url )
        # PS: do nothing...
        # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
        # raise exception at selenium/webdriver/remote/errorhandler.py
        # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
        is_pass_alert = False
        is_pass_alert = True
        if is_pass_alert:
            try:
                driver.switch_to.alert.accept()
            except Exception as exc:
                pass

    except Exception as exc:
        logger.error('Maxbot URL Exception')
        logger.error(exc, exc_info=True)

        #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
        str_exc = ""
        try:
            str_exc = str(exc)
        except Exception as exc2:
            pass

        if len(str_exc)==0:
            str_exc = repr(exc)

        exit_bot_error_strings = ['Max retries exceeded'
        , 'chrome not reachable'
        , 'unable to connect to renderer'
        , 'failed to check if window was closed'
        , 'Failed to establish a new connection'
        , 'Connection refused'
        , 'disconnected'
        , 'without establishing a connection'
        , 'web view not found'
        , 'invalid session id'
        ]
        for each_error_string in exit_bot_error_strings:
            if isinstance(str_exc, str):
                if each_error_string in str_exc:
                    print('quit bot by error:', each_error_string, driver)
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

        # not is above case, print exception.
        print("Exception:", str_exc)
        pass

    return url, is_quit_bot

def reset_webdriver(driver, config_dict, url):
    new_driver = None
    try:
        cookies = driver.get_cookies()
        driver.close()
        config_dict["homepage"]=url
        new_driver = get_driver_by_config(config_dict)
        for cookie in cookies:
            new_driver.add_cookie(cookie);
        new_driver.get(url)
        driver = new_driver
    except Exception as e:
        pass
    return new_driver

def resize_window(driver, config_dict):
    if len(config_dict["advanced"]["window_size"]) > 0:
        if "," in config_dict["advanced"]["window_size"]:
            size_array = config_dict["advanced"]["window_size"].split(",")
            position_left = 0
            if len(size_array) >= 3:
                position_left = int(size_array[0]) * int(size_array[2])
            driver.set_window_size(int(size_array[0]), int(size_array[1]))
            driver.set_window_position(position_left, 30)

def check_refresh_datetime_occur(driver, target_time):
    is_refresh_datetime_sent = False

    system_clock_data = datetime.now()
    current_time = system_clock_data.strftime('%H:%M:%S')
    if target_time == current_time:
        try:
            driver.refresh()
            is_refresh_datetime_sent = True
            print("send refresh at time:", current_time)
        except Exception as exc:
            pass

    return is_refresh_datetime_sent

def sendkey_to_browser(driver, config_dict):
    tmp_filepath = ""
    if "token" in config_dict:
        app_root = util.get_app_root()
        tmp_file = config_dict["token"] + ".tmp"
        tmp_filepath = os.path.join(app_root, tmp_file)

    if os.path.exists(tmp_filepath):
        sendkey_to_browser_exist(driver, tmp_filepath)

def reload_config(config_dict, last_mtime):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    if not os.path.exists(config_filepath):
        return config_dict, last_mtime

    try:
        current_mtime = os.path.getmtime(config_filepath)
        if current_mtime > last_mtime:
            time.sleep(0.1)
            with open(config_filepath, 'r', encoding='utf-8') as json_data:
                new_config = json.load(json_data)

                # Update fields
                fields = [
                    "ticket_number", "date_auto_select", "area_auto_select", "keyword_exclude",
                    "ocr_captcha", "tixcraft", "kktix", "cityline",
                    "refresh_datetime", "contact", "date_auto_fallback", "area_auto_fallback"
                ]
                for field in fields:
                    if field in new_config:
                        config_dict[field] = new_config[field]

                if "advanced" in new_config:
                    if "advanced" not in config_dict:
                        config_dict["advanced"] = {}
                    adv_fields = [
                        "play_sound", "disable_adjacent_seat", "hide_some_image",
                        "auto_guess_options", "user_guess_string", "auto_reload_page_interval", "verbose",
                        "auto_reload_overheat_count", "auto_reload_overheat_cd",
                        "idle_keyword", "resume_keyword", "idle_keyword_second", "resume_keyword_second",
                        "discord_webhook_url", "discount_code"
                    ]
                    for field in adv_fields:
                        if field in new_config["advanced"]:
                            config_dict["advanced"][field] = new_config["advanced"][field]

                print("Configuration reloaded from settings.json")
                return config_dict, current_mtime
    except Exception:
        pass

    return config_dict, last_mtime

def sendkey_to_browser_exist(driver, tmp_filepath):
    sendkey_dict = None
    try:
        with open(tmp_filepath) as json_data:
            sendkey_dict = json.load(json_data)
            print(sendkey_dict)
    except Exception as e:
        print("error on open file")
        print(e)
        pass

    if sendkey_dict:
        all_command_done = True
        if "command" in sendkey_dict:
            for cmd_dict in sendkey_dict["command"]:
                #print("cmd_dict", cmd_dict)
                if cmd_dict["type"] == "sendkey":
                    print("sendkey")
                    target_text = cmd_dict["text"]
                    try:
                        form_input_1 = driver.find_element(By.CSS_SELECTOR, cmd_dict["selector"])
                        inputed_value_1 = form_input_1.get_attribute('value')
                        if not inputed_value_1 == target_text:
                            form_input_1.clear()
                            form_input_1.click()
                            form_input_1.send_keys(cmd_dict["text"])
                    except Exception as exc:
                        all_command_done = False
                        print("error on sendkey")
                        print(exc)
                        pass
                
                if cmd_dict["type"] == "click":
                    print("click")
                    try:
                        form_input_1 = driver.find_element(By.CSS_SELECTOR, cmd_dict["selector"])
                        form_input_1.click()
                    except Exception as exc:
                        all_command_done = False
                        print("error on click")
                        print(exc)
                        pass
                time.sleep(0.05)

        # must all command success to delete tmp file.
        if all_command_done:
            try:
                os.unlink(tmp_filepath)
            except Exception as e:
                pass

def main(args):
    config_dict = get_config_dict(args)
    config_dict["token"] = util.get_token()

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict)
        if not driver is None:
            if not config_dict["advanced"]["headless"]:
                resize_window(driver, config_dict)
        else:
            print("無法使用web driver，程式無法繼續工作")
            sys.exit()
    else:
        print("Load config error!")

    url = ""
    last_url = ""

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
            Captcha_Browser = NonBrowser()
            if len(config_dict["accounts"]["tixcraft_sid"]) > 1:
                set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
    except Exception as exc:
        print(exc)
        pass

    maxbot_last_reset_time = time.time()
    is_quit_bot = False
    is_refresh_datetime_sent = False

    # Initialize config mtime
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    config_mtime = 0
    if os.path.exists(config_filepath):
        config_mtime = os.path.getmtime(config_filepath)

    while True:
        time.sleep(0.05)

        config_dict, config_mtime = reload_config(config_dict, config_mtime)

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        if not is_quit_bot:
            url, is_quit_bot = get_current_url(driver)
            #print("url:", url)

        if is_quit_bot:
            try:
                driver.quit()
                driver = None
            except Exception as e:
                pass
            break

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        if not is_refresh_datetime_sent:
            is_refresh_datetime_sent = check_refresh_datetime_occur(driver, config_dict["refresh_datetime"])

        is_maxbot_paused = False
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            is_maxbot_paused = True

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                if is_maxbot_paused:
                    print("BOT Paused.")
            last_url = url

        if is_maxbot_paused:
            if 'kktix.c' in url:
                kktix_paused_main(driver, url, config_dict)
            # sleep more when paused.
            time.sleep(0.1)
            continue

        sendkey_to_browser(driver, config_dict)

        # default is 0, not reset.
        if config_dict["advanced"]["reset_browser_interval"] > 0:
            maxbot_running_time = time.time() - maxbot_last_reset_time
            if maxbot_running_time > config_dict["advanced"]["reset_browser_interval"]:
                driver = reset_webdriver(driver, config_dict, url)
                maxbot_last_reset_time = time.time()

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if 'ticketmaster.' in url:
            tixcraft_family = True

        if tixcraft_family:
            is_quit_bot = tixcraft_main(driver, url, config_dict, ocr, Captcha_Browser)

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            is_quit_bot = kktix_main(driver, url, config_dict)

        if 'famiticket.com' in url:
            famiticket_main(driver, url, config_dict)

        if 'ibon.com' in url:
            ibon_main(driver, url, config_dict, ocr, Captcha_Browser)

        kham_family = False
        if 'kham.com.tw' in url:
            kham_family = True

        if 'ticket.com.tw' in url:
            kham_family = True

        if 'tickets.udnfunlife.com' in url:
            kham_family = True

        if kham_family:
            kham_main(driver, url, config_dict, ocr, Captcha_Browser)

        if 'ticketplus.com' in url:
            ticketplus_main(driver, url, config_dict, ocr, Captcha_Browser)

        if 'urbtix.hk' in url:
            urbtix_main(driver, url, config_dict)

        if 'cityline.com' in url:
            cityline_main(driver, url, config_dict)

        softix_family = False
        if 'hkticketing.com' in url:
            softix_family = True
        if 'galaxymacau.com' in url:
            softix_family = True
        if 'ticketek.com' in url:
            softix_family = True
        if softix_family:
            softix_powerweb_main(driver, url, config_dict)

        # for facebook signin
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            facebook_main(driver, config_dict)

def cli():
    parser = argparse.ArgumentParser(
            description="MaxBot Aggument Parser")

    parser.add_argument("--input",
        help="config file path",
        type=str)

    parser.add_argument("--homepage",
        help="overwrite homepage setting",
        type=str)

    parser.add_argument("--ticket_number",
        help="overwrite ticket_number setting",
        type=int)

    parser.add_argument("--tixcraft_sid",
        help="overwrite tixcraft sid field",
        type=str)

    parser.add_argument("--kktix_account",
        help="overwrite kktix_account field",
        type=str)

    parser.add_argument("--kktix_password",
        help="overwrite kktix_password field",
        type=str)

    parser.add_argument("--ibonqware",
        help="overwrite ibonqware field",
        type=str)

    #default="False",
    parser.add_argument("--headless",
        help="headless mode",
        type=str)

    parser.add_argument("--browser",
        help="overwrite browser setting",
        default='',
        choices=['chrome','firefox','edge','safari','brave'],
        type=str)

    parser.add_argument("--window_size",
        help="Window size",
        type=str)

    parser.add_argument("--proxy_server",
        help="overwrite proxy server, format: ip:port",
        type=str)

    args = parser.parse_args()
    main(args)

def test_captcha_model():
    #for test kktix answer.
    captcha_text_div_text = "請輸入括弧內數字( 27８９41 )"
    captcha_text_div_text = "請將括弧內文字轉換為阿拉伯數字(一二三四五六)"
    answer_list = util.get_answer_list_from_question_string(None, captcha_text_div_text)
    print("answer_list:", answer_list)

    ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    image_file = 'captcha-xxxx.png'
    if os.path.exists(image_file):
        with open(image_file, 'rb') as f:
            image_bytes = f.read()
        res = ocr.classification(image_bytes)
        print(res)

if __name__ == "__main__":
    debug_captcha_model_flag = False    # online mode
    # for debug purpose.
    #debug_captcha_model_flag = True

    #jieba.initialize()

    if not debug_captcha_model_flag:
        cli()
    else:
        test_captcha_model()
