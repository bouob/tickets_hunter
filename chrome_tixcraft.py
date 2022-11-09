#!/usr/bin/env python3
#encoding=utf-8
import os
import sys
import platform
import json
import random
#print("python version", platform.python_version())

# 'seleniumwire' and 'selenium 4' raise error when running python 2.x 
# PS: python 2.x will be removed in future. 

driver_type = 'selenium'
#driver_type = 'stealth'
driver_type = 'undetected_chromedriver'

if driver_type=="undetected_chromedriver":
    # TODO: fix image re-download issue.
    #from seleniumwire import webdriver

    from selenium import webdriver
else:
    from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# for close tab.
from selenium.common.exceptions import NoSuchWindowException
# for alert
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# for chrome 103
from selenium.common.exceptions import WebDriverException

# for ["pageLoadStrategy"] = "eager"
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# for selenium 4
from selenium.webdriver.chrome.service import Service

# for wait #1
import time

import re
from datetime import datetime

# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')

# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
#附註1：沒有寫的很好，很多地方應該可以模組化。
#附註2：

CONST_APP_VERSION = u"MaxBot (2022.11.09)"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM)
CONST_SELECT_OPTIONS_ARRAY = [CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM]

CONT_STRING_1_SEATS_REMAINING = [u'@1 seat(s) remaining',u'剩餘 1@',u'@1 席残り']

# initial webdriver
# 說明：初始化 webdriver
driver = None

homepage = None
browser = None
ticket_number = None
facebook_account = None

auto_press_next_step_button = False
auto_fill_ticket_number = False
auto_fill_ticket_price = None

date_auto_select_enable = False
date_auto_select_mode = None
date_keyword = None

area_auto_select_enable = False
area_auto_select_mode = None
area_keyword = None

area_keyword_1 = None
area_keyword_2 = None
area_keyword_3 = None
area_keyword_4 = None

pass_1_seat_remaining_enable = False        # default not checked.
pass_date_is_sold_out_enable = False        # default not checked.
auto_reload_coming_soon_page_enable = True  # default checked.

kktix_area_auto_select_mode = None
kktix_area_keyword = None
kktix_date_keyword = None

kktix_answer_dictionary = None
kktix_answer_dictionary_list = None

auto_guess_options = False

debugMode = False

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict():
    config_json_filename = 'settings.json'
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, config_json_filename)
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict

def format_keyword_string(keyword):
    if not keyword is None:
        if len(keyword) > 0:
            keyword = keyword.replace(',','')
            keyword = keyword.replace('／','/')
            keyword = keyword.replace(' ','').lower()
    return keyword

def find_continuous_number(text):
    ret = ""
    is_number_start = False
    number_char = "0123456789"
    for char in text:
        #print("char:", char)
        if char in number_char:
            if len(ret)==0 and not is_number_start:
                is_number_start = True
            if is_number_start:
                ret += char
        else:
            # make not continuous
            is_number_start = False

    return ret

def get_favoriate_extension_path(webdriver_path):
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.14.2.0.crx")
    return no_google_analytics_path, no_ad_path

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def load_chromdriver_normal(webdriver_path, driver_type):
    from selenium_stealth import stealth
    chrome_options = webdriver.ChromeOptions()

    chromedriver_path = get_chromedriver_path(webdriver_path)

    no_google_analytics_path, no_ad_path = get_favoriate_extension_path(webdriver_path)

    if os.path.exists(no_google_analytics_path):
        chrome_options.add_extension(no_google_analytics_path)
    if os.path.exists(no_ad_path):
        chrome_options.add_extension(no_ad_path)

    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False,'profile.default_content_setting_values':{'notifications':2}})

    #caps = DesiredCapabilities().CHROME
    caps = chrome_options.to_capabilities()

    #caps["pageLoadStrategy"] = u"normal"  #  complete
    caps["pageLoadStrategy"] = u"eager"  #  interactive
    #caps["pageLoadStrategy"] = u"none"

    #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
    caps["unhandledPromptBehavior"] = u"ignore"
    #caps["unhandledPromptBehavior"] = u"dismiss"

    chrome_service = Service(chromedriver_path)

    # method 6: Selenium Stealth
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    if driver_type=="stealth":
        from selenium_stealth import stealth

        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )

    return driver

def load_chromdriver_uc(webdriver_path):
    import undetected_chromedriver as uc

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"
    #print("strategy", options.page_load_strategy)

    no_google_analytics_path, no_ad_path = get_favoriate_extension_path(webdriver_path)
    no_google_analytics_folder_path = no_google_analytics_path.replace('.crx','')
    no_ad_folder_path = no_ad_path.replace('.crx','')
    load_extension_path = ""
    if os.path.exists(no_google_analytics_folder_path):
        load_extension_path += "," + no_google_analytics_folder_path
    if os.path.exists(no_ad_folder_path):
        load_extension_path += "," + no_ad_folder_path
    if len(load_extension_path) > 0:
        options.add_argument('--load-extension=' + load_extension_path[1:])

    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')

    if os.path.exists(chromedriver_path):
        print("Use user driver path:", chromedriver_path)
        #driver = uc.Chrome(service=chrome_service, options=options, suppress_welcome=False)
        is_local_chrome_browser_lower = False
        try:
            driver = uc.Chrome(executable_path=chromedriver_path, options=options, suppress_welcome=False)
        except Exception as exc:
            if "cannot connect to chrome" in str(exc):
                if "This version of ChromeDriver only supports Chrome version" in str(exc):
                    is_local_chrome_browser_lower = True
            print(exc)
            pass

        if is_local_chrome_browser_lower:
            print("Use local user downloaded chromedriver to lunch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(webdriver_path, driver_type)
    else:
        print("Oops! web driver not on path:",chromedriver_path )
        print('let uc automatically download chromedriver.')
        driver = uc.Chrome(options=options, suppress_welcome=False)

    if driver is None:
        print("create web drive object fail!")
    else:
        download_dir_path="."
        params = {
            "behavior": "allow",
            "downloadPath": os.path.realpath(download_dir_path)
        }
        #print("assign setDownloadBehavior.")
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    return driver

def close_browser_tabs(driver):        
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def load_config_from_local(driver):
    config_dict = get_config_dict()

    global homepage
    global browser
    global debugMode
    global ticket_number
    global facebook_account
    global auto_press_next_step_button
    global auto_fill_ticket_number
    global kktix_area_auto_select_mode
    global kktix_area_keyword
    global kktix_date_keyword

    global kktix_answer_dictionary
    global kktix_answer_dictionary_list

    global auto_guess_options
    global pass_1_seat_remaining_enable
    global pass_date_is_sold_out_enable
    global auto_reload_coming_soon_page_enable

    global area_keyword_1
    global area_keyword_2
    global area_keyword_3
    global area_keyword_4

    global date_auto_select_enable
    global date_auto_select_mode

    global date_keyword

    global area_auto_select_enable
    global area_auto_select_mode

    global debugMode

    if not config_dict is None:
        # read config.
        if 'homepage' in config_dict:
            homepage = config_dict["homepage"]
        if 'browser' in config_dict:
            browser = config_dict["browser"]

        # output debug message in client side.
        if 'debug' in config_dict:
            debugMode = config_dict["debug"]

        # default ticket number
        # 說明：自動選擇的票數
        #ticket_number = "2"
        ticket_number = ""
        if 'ticket_number' in config_dict:
            ticket_number = str(config_dict["ticket_number"])

        facebook_account = ""
        if 'facebook_account' in config_dict:
            facebook_account = str(config_dict["facebook_account"])

        # for ["kktix"]
        if 'kktix' in config_dict:
            auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
            auto_fill_ticket_number = config_dict["kktix"]["auto_fill_ticket_number"]

            if 'area_mode' in config_dict["kktix"]:
                kktix_area_auto_select_mode = config_dict["kktix"]["area_mode"]
                kktix_area_auto_select_mode = kktix_area_auto_select_mode.strip()
            if not kktix_area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
                kktix_area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

            if 'area_keyword' in config_dict["kktix"]:
                kktix_area_keyword = config_dict["kktix"]["area_keyword"]
                if kktix_area_keyword is None:
                    kktix_area_keyword = ""
                kktix_area_keyword = kktix_area_keyword.strip()

            if 'date_keyword' in config_dict["kktix"]:
                kktix_date_keyword = config_dict["kktix"]["date_keyword"]
                if kktix_date_keyword is None:
                    kktix_date_keyword = ""
                kktix_date_keyword = kktix_date_keyword.strip()

            # disable password brute force attack
            if 'answer_dictionary' in config_dict["kktix"]:
                kktix_answer_dictionary = config_dict["kktix"]["answer_dictionary"]
                if kktix_answer_dictionary is None:
                    kktix_answer_dictionary = ""
                kktix_answer_dictionary = kktix_answer_dictionary.strip()

                if len(kktix_answer_dictionary) > 0:
                    kktix_answer_dictionary_list = kktix_answer_dictionary.split(',')

            if 'auto_guess_options' in config_dict["kktix"]:
                auto_guess_options = config_dict["kktix"]["auto_guess_options"]

        # for ["tixcraft"]
        if 'tixcraft' in config_dict:
            date_auto_select_enable = False
            date_auto_select_mode = None

            if 'date_auto_select' in config_dict["tixcraft"]:
                date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
                date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]

            if not date_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
                date_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

            if 'date_keyword' in config_dict["tixcraft"]["date_auto_select"]:
                date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"]
                date_keyword = date_keyword.strip()

            area_auto_select_enable = False
            area_auto_select_mode = None

            if 'area_auto_select' in config_dict["tixcraft"]:
                area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
                area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]

            if not area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
                area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

            if 'area_keyword_1' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"]
                area_keyword_1 = area_keyword_1.strip()

            if 'area_keyword_2' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"]
                area_keyword_2 = area_keyword_2.strip()

            if 'area_keyword_3' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"]
                area_keyword_3 = area_keyword_3.strip()

            if 'area_keyword_4' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"]
                area_keyword_4 = area_keyword_4.strip()

            pass_1_seat_remaining_enable = False
            if 'pass_1_seat_remaining' in config_dict["tixcraft"]:
                pass_1_seat_remaining_enable = config_dict["tixcraft"]["pass_1_seat_remaining"]

            pass_date_is_sold_out_enable = False
            if 'pass_date_is_sold_out' in config_dict["tixcraft"]:
                pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]

            auto_reload_coming_soon_page_enable = True
            if 'auto_reload_coming_soon_page' in config_dict["tixcraft"]:
                auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

        # output config:
        print("maxbot app version", CONST_APP_VERSION)
        print("python version", platform.python_version())
        print("homepage", homepage)
        print("browser", browser)
        print("ticket_number", ticket_number)
        print("facebook_account", facebook_account)

        # for kktix
        print("==[kktix]==")
        print("auto_press_next_step_button", auto_press_next_step_button)
        print("auto_fill_ticket_number", auto_fill_ticket_number)
        print("kktix_area_keyword", kktix_area_keyword)
        print("kktix_date_keyword", kktix_date_keyword)
        print("kktix_answer_dictionary", kktix_answer_dictionary)
        print("auto_guess_options", auto_guess_options)

        # for tixcraft
        print("==[tixcraft]==")
        print("date_auto_select_enable", date_auto_select_enable)
        print("date_auto_select_mode", date_auto_select_mode)
        print("date_keyword", date_keyword)

        print("area_auto_select_enable", area_auto_select_enable)
        print("area_auto_select_mode", area_auto_select_mode)
        print("area_keyword_1", area_keyword_1)
        print("area_keyword_2", area_keyword_2)
        print("area_keyword_3", area_keyword_3)
        print("area_keyword_4", area_keyword_4)

        print("pass_1_seat_remaining", pass_1_seat_remaining_enable)
        print("pass_date_is_sold_out", pass_date_is_sold_out_enable)

        print("auto_reload_coming_soon_page", auto_reload_coming_soon_page_enable)

        print("debug Mode", debugMode)

        # entry point
        # 說明：自動開啟第一個的網頁
        if homepage is None:
            homepage = ""
        if len(homepage) == 0:
            homepage = "https://tixcraft.com/activity/"

        Root_Dir = get_app_root()
        webdriver_path = os.path.join(Root_Dir, "webdriver")
        print("platform.system().lower():", platform.system().lower())

        if browser == "chrome":
            DEFAULT_ARGS = [
                '--disable-audio-output',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-breakpad',
                '--disable-browser-side-navigation',
                '--disable-checker-imaging',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-demo-mode',
                '--disable-dev-shm-usage',
                #'--disable-extensions',
                '--disable-features=site-per-process',
                '--disable-hang-monitor',
                '--disable-in-process-stack-traces',
                '--disable-javascript-harmony-shipping',
                '--disable-logging',
                '--disable-notifications',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-perfetto',
                '--disable-permissions-api',
                '--disable-plugins',
                '--disable-presentation-api',
                '--disable-reading-from-canvas',
                '--disable-renderer-accessibility',
                '--disable-renderer-backgrounding',
                '--disable-shader-name-hashing',
                '--disable-smooth-scrolling',
                '--disable-speech-api',
                '--disable-speech-synthesis-api',
                '--disable-sync',
                '--disable-translate',

                '--ignore-certificate-errors',

                '--metrics-recording-only',
                '--no-first-run',
                '--no-experiments',
                '--safebrowsing-disable-auto-update',
                #'--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain',
                '--lang=zh-TW',
                '--stable-release-mode',
                '--use-mobile-user-agent',
                '--webview-disable-safebrowsing-support',
                #'--no-sandbox',
                #'--incognito',
            ]

            # method 6: Selenium Stealth
            if driver_type != "undetected_chromedriver":
                driver = load_chromdriver_normal(webdriver_path, driver_type)
            else:
                # method 5: uc
                #options = webdriver.ChromeOptions()

                # multiprocessing not work bug.
                if platform.system().lower()=="windows":
                    if hasattr(sys, 'frozen'):
                        from multiprocessing import freeze_support
                        freeze_support()

                driver = load_chromdriver_uc(webdriver_path)

        if browser == "firefox":
            # default os is linux/mac
            chromedriver_path = os.path.join(webdriver_path,"geckodriver")
            if platform.system().lower()=="windows":
                chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

            firefox_service = Service(chromedriver_path)
            driver = webdriver.Firefox(service=firefox_service)


        time.sleep(15.0)
        #print("try to close opened tabs.")
        for i in range(2):
            close_browser_tabs(driver)

        if driver is None:
            print("create web driver object fail @_@;")
        else:
            try:
                print("goto url:", homepage)
                driver.get(homepage)
            except WebDriverException as exce2:
                print('oh no not again, WebDriverException')
                print('WebDriverException:', exce2)
            except Exception as exce1:
                print('get URL Exception:', exec1)
                pass

        for i in range(2):
            close_browser_tabs(driver)


    else:
        print("Config error!")

    return driver

# common functions.
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# convert web string to reg pattern
def convert_string_to_pattern(my_str, dynamic_length=True):
    my_hint_anwser_length = len(my_str)
    my_formated = ""
    if my_hint_anwser_length > 0:
        my_anwser_symbols = u"()[]<>{}-"
        for idx in range(my_hint_anwser_length):
            char = my_str[idx:idx+1]

            if char in my_anwser_symbols:
                my_formated += (u'\\' + char)
                continue

            pattern = re.compile(u"[A-Z]")
            match_result = pattern.match(char)
            #print("match_result A:", match_result)
            if not match_result is None:
                my_formated += u"[A-Z]"

            pattern = re.compile(u"[a-z]")
            match_result = pattern.match(char)
            #print("match_result a:", match_result)
            if not match_result is None:
                my_formated += u"[a-z]"

            pattern = re.compile(u"[\d]")
            match_result = pattern.match(char)
            #print("match_result d:", match_result)
            if not match_result is None:
                my_formated += u"[\d]"

        # for dynamic length
        if dynamic_length:
            for i in range(10):
                my_formated = my_formated.replace(u"[A-Z][A-Z]",u"[A-Z]")
                my_formated = my_formated.replace(u"[a-z][a-z]",u"[a-z]")
                my_formated = my_formated.replace(u"[\d][\d]",u"[\d]")

            my_formated = my_formated.replace(u"[A-Z]",u"[A-Z]+")
            my_formated = my_formated.replace(u"[a-z]",u"[a-z]+")
            my_formated = my_formated.replace(u"[\d]",u"[\d]+")
    return my_formated

def get_answer_list_by_question(captcha_text_div_text):
    return_list = None
    my_answer_delimitor = ""

    #if u"?" in captcha_text_div_text or u"？" in captcha_text_div_text:
    if True:
        tmp_text = captcha_text_div_text
        tmp_text = tmp_text.replace(u'  ',u' ')
        tmp_text = tmp_text.replace(u'：',u':')
        # for hint
        tmp_text = tmp_text.replace(u'*',u'*')

        # replace ex.
        tmp_text = tmp_text.replace(u'例如',u'範例')
        tmp_text = tmp_text.replace(u'如:',u'範例:')
        tmp_text = tmp_text.replace(u'舉例',u'範例')
        if not u'範例' in tmp_text:
            tmp_text = tmp_text.replace(u'例',u'範例')
        # important, maybe 例 & ex occurs at same time.
        tmp_text = tmp_text.replace(u'ex:',u'範例:')
        tmp_text = tmp_text.replace(u'Ex:',u'範例:')

        #tmp_text = tmp_text.replace(u'[',u'(')
        #tmp_text = tmp_text.replace(u']',u')')
        tmp_text = tmp_text.replace(u'?',u'？')

        tmp_text = tmp_text.replace(u'（',u'(')
        tmp_text = tmp_text.replace(u'）',u')')

        # is need to convert . ? I am not sure!
        tmp_text = tmp_text.replace(u'。',u' ')

        my_question = ""
        my_options = ""
        my_hint = ""
        my_hint_anwser = ""
        my_anwser_formated = ""

        if u"？" in tmp_text:
            question_index = tmp_text.find(u"？")
            my_question = tmp_text[:question_index+1]
        if u"。" in tmp_text:
            question_index = tmp_text.find(u"。")
            my_question = tmp_text[:question_index+1]
        if len(my_question) == 0:
            my_question = tmp_text
        #print(u"my_question:", my_question)

        # get hint from quota.
        hint_list = None
        # ps: hint_list is not options list

        # try rule1:
        if u'(' in tmp_text and u')' in tmp_text and u'範例' in tmp_text:
            #import re
            #print("text:" , re.findall('\([\w]+\)', tmp_text))
            hint_list = re.findall(u'\(.*?\)', tmp_text)
            #print("hint_list:", hint_list)

        # try rule2:
        if hint_list is None:
            if u'【' in tmp_text and u'】' in tmp_text and u'範例' in tmp_text:
                #import re
                #print("text:" , re.findall('\([\w]+\)', tmp_text))
                hint_list = re.findall(u'【.*?】', tmp_text)

        # try rule3:
        if not hint_list is None:
            for hint in hint_list:
                if u'範例' in hint:
                    my_hint = hint
                    if my_hint[:1] == u'【':
                        my_hint = my_hint[1:]
                    if my_hint[-1:] == u'】':
                        my_hint = my_hint[:-1]
                    break;
                else:
                    # get hint from rule 3: with '(' & '), but ex: is outside
                    if u'半形' in hint:
                        hint_index = tmp_text.find(hint)
                        ex_index = tmp_text.find(u"範例")
                        if ex_index > 0:
                            ex_end_index = tmp_text.find(u" ",ex_index)
                            if ex_end_index < 0:
                                ex_end_index = tmp_text.find(u"(",ex_index)
                            if ex_end_index < 0:
                                ex_end_index = tmp_text.find(u"（",ex_index)
                            if ex_end_index < 0:
                                ex_end_index = tmp_text.find(u".",ex_index)
                            if ex_end_index < 0:
                                ex_end_index = tmp_text.find(u"。",ex_index)
                            if ex_end_index >=0:
                                my_hint = tmp_text[hint_index:ex_end_index+1]


        # try rule4:
        # get hint from rule 3: without '(' & '), but use "*"
        if len(my_hint) == 0:
            target_symbol = u"*"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index + len(target_symbol))
                my_hint = tmp_text[star_index: space_index]

        # is need to merge next block
        if len(my_hint) > 0:
            target_symbol = my_hint + u" "
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                next_block_index = star_index + len(target_symbol)
                space_index = tmp_text.find(u" ", next_block_index)
                next_block = tmp_text[next_block_index: space_index]
                if u'範例' in next_block:
                    my_hint += u' ' + next_block

        if len(my_hint) > 0:
            my_hint_anwser = my_hint[my_hint.find(u"範例")+2:].strip()

            if u'答案' in my_hint_anwser and u'填入' in my_hint_anwser:
                # 答案為B需填入Bb)
                fill_index = my_hint_anwser.find(u"填入")
                my_hint_anwser = my_hint_anwser[fill_index+2:].strip()

            if my_hint_anwser[:1] == u":":
                my_hint_anwser = my_hint_anwser[1:]
            if my_hint[:1] == u"(":
                if my_hint_anwser[-1:] == u")":
                    my_hint_anwser = my_hint_anwser[:-1]
            if my_hint_anwser[-1:] == u"。":
                my_hint_anwser = my_hint_anwser[:-1]
        #print(u"my_hint_anwser:", my_hint_anwser)

        # try rule5:
        # get hint from rule 3: n個半形英文大寫
        if len(my_hint) == 0:
            target_symbol = u"個半形英文大寫"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_hint_anwser = u'A' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

            target_symbol = u"個英文大寫"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_hint_anwser = u'A' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

            target_symbol = u"個半形英文小寫"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_hint_anwser = u'a' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

            target_symbol = u"個英文小寫"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_hint_anwser = u'a' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

        if len(my_hint) > 0:
            my_anwser_formated = convert_string_to_pattern(my_hint_anwser)

        # try rule6:
        # get hint from rule 3: n個英數半形字
        if len(my_hint) == 0:
            target_symbol = u"個英數半形字"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

        if len(my_hint) == 0:
            target_symbol = u"個半形"
            if target_symbol in tmp_text :
                star_index = tmp_text.find(target_symbol)
                space_index = tmp_text.find(u" ", star_index)
                answer_char_count = tmp_text[star_index-1:star_index]
                if answer_char_count.isnumeric():
                    star_index -= 1
                    my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
                my_hint = tmp_text[star_index: space_index]

        #print(u"my_hint:", my_hint)

        #print(u"my_anwser_formated:", my_anwser_formated)

        my_options = tmp_text
        my_options = my_options.replace(my_question,u"")
        my_options = my_options.replace(my_hint,u"")

        # try rule7:
        # check is chinese/english in question, if match, apply my_options rule.
        if len(my_hint) > 0:
            tmp_text_org = captcha_text_div_text
            if u'範例:' in tmp_text:
                tmp_text_org = tmp_text_org.replace(u'Ex:','ex:')
                target_symbol = u"ex:"
                if target_symbol in tmp_text_org :
                    star_index = tmp_text_org.find(target_symbol)
                    my_options = tmp_text_org[star_index-1:]

        #print(u"my_options:", my_options)

        if len(my_anwser_formated) > 0:
            allow_delimitor_symbols = ")].: }"
            pattern = re.compile(my_anwser_formated)
            search_result = pattern.search(my_options)
            if not search_result is None:
                (span_start, span_end) = search_result.span()
                if len(my_options) > (span_end+1)+1:
                    maybe_delimitor = my_options[span_end+0:span_end+1]
                if maybe_delimitor in allow_delimitor_symbols:
                    my_answer_delimitor = maybe_delimitor
        #print(u"my_answer_delimitor:", my_answer_delimitor)



        # try all possible options.
        tmp_text = captcha_text_div_text
        tmp_text = tmp_text.replace(u'  ',u' ')
        tmp_text = tmp_text.replace(u'例如',u'範例')
        tmp_text = tmp_text.replace(u'例:',u'範例')
        tmp_text = tmp_text.replace(u'如:',u'範例')
        tmp_text = tmp_text.replace(u'舉例',u'範例')
        #tmp_text = tmp_text.replace(u'[',u'(')
        #tmp_text = tmp_text.replace(u']',u')')

        if len(my_anwser_formated) > 0:
            #print("text:" , re.findall('\([\w]+\)', tmp_text))
            new_pattern = my_anwser_formated
            if len(my_answer_delimitor) > 0:
                new_pattern = my_anwser_formated + u'\\' + my_answer_delimitor
            return_list = re.findall(new_pattern, my_options)

            if not return_list is None:
                if len(return_list) == 1:
                    # re-sample for this case.
                    return_list = re.findall(my_anwser_formated, my_options)

        # try rule8:
        if return_list is None:
            # need replace to space to get first options.
            tmp_text = captcha_text_div_text
            tmp_text = tmp_text.replace(u'?',u' ')
            tmp_text = tmp_text.replace(u'？',u' ')
            tmp_text = tmp_text.replace(u'。',u' ')

            delimitor_symbols_left = [u"(",u"[",u"{", " ", " ", " ", " "]
            delimitor_symbols_right = [u")",u"]",u"}", ":", ".", ")", "-"]
            idx = -1
            for idx in range(len(delimitor_symbols_left)):
                symbol_left = delimitor_symbols_left[idx]
                symbol_right = delimitor_symbols_right[idx]
                if symbol_left in tmp_text and symbol_right in tmp_text and u'半形' in tmp_text:
                    hint_list = re.findall(u'\\'+ symbol_left + u'[\\w]+\\'+ symbol_right , tmp_text)
                    #print("hint_list:", hint_list)
                    if not hint_list is None:
                        if len(hint_list) > 1:
                            return_list = []
                            my_answer_delimitor = symbol_right
                            for options in hint_list:
                                if len(options) > 2:
                                    my_anwser = options[1:-1]
                                    #print("my_anwser:",my_anwser)
                                    if len(my_anwser) > 0:
                                        return_list.append(my_anwser)

                if not return_list is None:
                    break
    #print("return_list:", return_list)
    return return_list, my_answer_delimitor

# close some div on home url.
def tixcraft_home(driver):
    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    except Exception as exc:
        #print("find accept_all_cookies_btn fail")
        pass

    if accept_all_cookies_btn is not None:
        is_visible = False
        try:
            if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                accept_all_cookies_btn.click()
            except Exception as exc:
                print("try to click accept_all_cookies_btn fail")
                try:
                    driver.execute_script("arguments[0].click();", accept_all_cookies_btn)
                except Exception as exc:
                    pass

    close_all_alert_btns = None
    try:
        close_all_alert_btns = driver.find_elements(By.CSS_SELECTOR, "[class='close-alert']")
    except Exception as exc:
        print("find close_all_alert_btns fail")

    if close_all_alert_btns is not None:
        #print('alert count:', len(close_all_alert_btns))
        for alert_btn in close_all_alert_btns:
            # fix bug: Message: stale element reference: element is not attached to the page document
            is_visible = False
            try:
                if alert_btn.is_enabled() and alert_btn.is_displayed():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    alert_btn.click()
                except Exception as exc:
                    print("try to click alert_btn fail")
                    try:
                        driver.execute_script("arguments[0].click();", alert_btn)
                    except Exception as exc:
                        pass

# from detail to game
def tixcraft_redirect(driver, url):
    ret = False

    game_name = ""

    # get game_name from url
    if "/activity/detail/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if "/activity/detail/%s" % (game_name,) in url:
        # to support teamear
        entry_url = url.replace("/activity/detail/","/activity/game/")
        #entry_url = "tixcraft.com/activity/game/%s" % (game_name,)
        print("redirec to new url:", entry_url)
        try:
            driver.get(entry_url)
        except Exception as exec1:
            pass
        ret = True

    return ret

def date_auto_select(driver, url, date_auto_select_mode, date_keyword, pass_date_is_sold_out_enable, auto_reload_coming_soon_page_enable):
    is_date_selected = False

    debug_date_select = True    # debug.
    debug_date_select = False   # online

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","No tickets available","空席なし"]

    game_name = ""

    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if debug_date_select:
        print('get date game_name:', game_name)
        print("date_auto_select_mode:", date_auto_select_mode)
        print("date_keyword:", date_keyword)

    check_game_detail = False
    # choose date
    if "/activity/game/%s" % (game_name,) in url:
        if debug_date_select:
            if len(date_keyword) == 0:
                print("date keyword is empty.")
            else:
                print("date keyword:", date_keyword)
        check_game_detail = True

    if check_game_detail:
        date_list = None
        try:
            date_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
        except Exception as exc:
            print("find #gameList fail")

        button_list = []
        if date_list is not None:
            for row in date_list:
                # step 1: check keyword.
                is_match_keyword_row = False

                row_text = ""
                try:
                    row_text = row.text
                except Exception as exc:
                    print("get text fail")
                    # should use continue or break?
                    break

                if len(row_text) > 0:
                    if len(date_keyword) == 0:
                        # no keyword, match all.
                        is_match_keyword_row = True
                    else:
                        # check keyword.
                        if date_keyword in row_text:
                            is_match_keyword_row = True


                # step 2: check sold out.
                if is_match_keyword_row:
                    if pass_date_is_sold_out_enable:
                        for sold_out_item in sold_out_text_list:
                            row_text_right_part = row_text[(len(sold_out_item)+5)*-1:]
                            if debug_date_select:
                                print("check right part text:", row_text_right_part)
                            if sold_out_item in row_text_right_part:
                                is_match_keyword_row = False

                                if debug_date_select:
                                    print("match sold out text: %s, skip this row." % (sold_out_item))

                                # no need check next language item.
                                break

                # step 3: add to list.
                if is_match_keyword_row:
                    el = None
                    try:
                        el = row.find_element(By.CSS_SELECTOR, '.btn-next')
                    except Exception as exc:
                        if debug_date_select:
                            print("find .btn-next fail")
                        pass

                    if el is not None:
                        button_list.append(el)
                        if date_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                            # only need one row.
                            if debug_date_select:
                                print("match date row, only need first row, start to break")
                            break


        if len(button_list) > 0:
            # default first row.
            target_row_index = 0

            if date_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(button_list) - 1

            if date_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(button_list)-1)

            try:
                if debug_date_select:
                    print("clicking row number:", target_row_index)

                el = button_list[target_row_index]
                el.click()
                is_date_selected = True
            except Exception as exc:
                print("try to click .btn-next fail")

                try:
                    driver.execute_script("arguments[0].click();", el)
                except Exception as exc:
                    pass

        # PS: Is this case need to reload page?
        #   (A)user input keywords, with matched text, but no hyperlink to click.
        #   (B)user input keywords, but not no matched text with hyperlink to click.

        # [PS]: current reload condition only when No hyperlink button.
        if auto_reload_coming_soon_page_enable and not is_date_selected:
            # auto refresh for date list page.
            el_list = None
            try:
                el_list = driver.find_elements(By.CSS_SELECTOR, '.btn-next')
                if el_list is None:
                    driver.refresh()
                else:
                    if len(el_list) == 0:
                        driver.refresh()
            except Exception as exc:
                pass
                #print("find .btn-next fail:", exc)

    return is_date_selected

# PURPOSE: get target area list.
# RETURN:
#   is_need_refresh
#   areas
# PS: areas will be None, if length equals zero.
def get_tixcraft_target_area(el, area_keyword, area_auto_select_mode, pass_1_seat_remaining_enable):
    debugMode = True
    debugMode = False       # for online

    if debugMode:
        print("testing keyword:", area_keyword)

    is_need_refresh = False
    areas = None

    area_list = None
    area_list_count = 0
    if el is not None:
        try:
            area_list = el.find_elements(By.TAG_NAME, 'a')
        except Exception as exc:
            #print("find area list a tag fail")
            pass

        if area_list is not None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                print("(with keyword) list is empty, do refresh!")
                is_need_refresh = True
        else:
            print("(with keyword) list is None, do refresh!")
            is_need_refresh = True

    if area_list_count > 0:
        areas = []
        for row in area_list:
            row_is_enabled=False
            try:
                row_is_enabled = row.is_enabled()
            except Exception as exc:
                pass

            row_text = ""
            if row_is_enabled:
                try:
                    row_text = row.text
                except Exception as exc:
                    print("get text fail")
                    break

            if len(row_text) > 0:
                # clean stop word.
                row_text = format_keyword_string(row_text)

                is_append_this_row = False

                if len(area_keyword) > 0:
                    # clean stop word.
                    area_keyword = format_keyword_string(area_keyword)

                # allow only input stop word in keyword fields.
                # for keyword#2 to select all.
                if len(area_keyword) > 0:
                    # must match keyword.
                    if area_keyword in row_text:
                        is_append_this_row = True
                else:
                    # without keyword.
                    is_append_this_row = True

                if is_append_this_row:
                    if debugMode:
                        print("pass_1_seat_remaining_enable:", pass_1_seat_remaining_enable)
                    if pass_1_seat_remaining_enable:
                        area_item_font_el = None
                        try:
                            #print('try to find font tag at row:', row_text)
                            area_item_font_el = row.find_element(By.TAG_NAME, 'font')
                            if not area_item_font_el is None:
                                font_el_text = area_item_font_el.text
                                font_el_text = "@%s@" % (font_el_text)
                                if debugMode:
                                    print('font tag text:', font_el_text)
                                    pass
                                for check_item in CONT_STRING_1_SEATS_REMAINING:
                                    if check_item in font_el_text:
                                        if debugMode:
                                            print("match pass 1 seats remaining 1 full text:", row_text)
                                            print("match pass 1 seats remaining 2 font text:", font_el_text)
                                        is_append_this_row = False
                            else:
                                #print("row withou font tag.")
                                pass
                        except Exception as exc:
                            #print("find font text in a tag fail:", exc)
                            pass

                if debugMode:
                    print("is_append_this_row:", is_append_this_row)

                if is_append_this_row:
                    areas.append(row)

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        print("only need first item, break area list loop.")
                        break
                    if debugMode:
                        print("row_text:" + row_text)
                        print("match:" + area_keyword)

        if len(areas) == 0:
            areas = None
            is_need_refresh = True

    return is_need_refresh, areas

# PS: auto refresh condition 1: no keyword + no hyperlink.
# PS: auto refresh condition 2: with keyword + no hyperlink.
def area_auto_select(driver, url, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode, pass_1_seat_remaining_enable):
    debugMode = True
    debugMode = False       # for online

    if debugMode:
        print("area_keyword_1, area_keyword_2:", area_keyword_1, area_keyword_2)
        print("area_keyword_3, area_keyword_4:", area_keyword_3, area_keyword_4)

    if '/ticket/area/' in url:
        #driver.switch_to.default_content()

        el = None
        try:
            el = driver.find_element(By.CSS_SELECTOR, '.zone')
        except Exception as exc:
            print("find .zone fail, do nothing.")

        if el is not None:
            is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_1, area_auto_select_mode, pass_1_seat_remaining_enable)
            if debugMode:
                print("is_need_refresh for keyword1:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if debugMode:
                        print("use area keyword #2", area_keyword_2)
                    
                    # only when keyword#2 filled to query.
                    if len(area_keyword_2) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_2, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if debugMode:
                            print("is_need_refresh for keyword2:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if debugMode:
                        print("use area keyword #3", area_keyword_3)
                    
                    # only when keyword#3 filled to query.
                    if len(area_keyword_3) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_3, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if debugMode:
                            print("is_need_refresh for keyword3:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if debugMode:
                        print("use area keyword #4", area_keyword_4)
                    
                    # only when keyword#4 filled to query.
                    if len(area_keyword_4) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_4, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if debugMode:
                            print("is_need_refresh for keyword4:", is_need_refresh)

            area_target = None
            if areas is not None:
                #print("area_auto_select_mode", area_auto_select_mode)
                #print("len(areas)", len(areas))
                if len(areas) > 0:
                    target_row_index = 0

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        pass

                    if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                        target_row_index = len(areas)-1

                    if area_auto_select_mode == CONST_RANDOM:
                        target_row_index = random.randint(0,len(areas)-1)

                    #print("target_row_index", target_row_index)
                    area_target = areas[target_row_index]

            if area_target is not None:
                try:
                    print("area text:", area_target.text)
                    area_target.click()
                except Exception as exc:
                    print("click area a link fail, start to retry...")
                    try:
                        driver.execute_script("arguments[0].click();", area_target)
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

'''
        el_selectSeat_iframe = None
        try:
            el_selectSeat_iframe = driver.find_element_by_xpath("//iframe[contains(@src,'/ticket/selectSeat/')]")
        except Exception as exc:
            #print("find seat iframe fail")
            pass

        if el_selectSeat_iframe is not None:
            driver.switch_to.frame(el_selectSeat_iframe)

            # click one seat
            el_seat = None
            try:
                el_seat = driver.find_element(By.CSS_SELECTOR, '.empty')
                if el_seat is not None:
                    try:
                        el_seat.click()
                    except Exception as exc:
                        #print("click area button fail")
                        pass
            except Exception as exc:
                print("find empty seat fail")


            # click submit button
            el_confirm_seat = None
            try:
                el_confirm_seat = driver.find_element(By.ID, 'submitSeat')
                if el_confirm_seat is not None:
                    try:
                        el_confirm_seat.click()
                    except Exception as exc:
                        #print("click area button fail")
                        pass
            except Exception as exc:
                print("find submitSeat fail")
'''

def ticket_number_auto_fill(url, form_select):
    # check agree
    form_checkbox = None
    try:
        form_checkbox = driver.find_element(By.ID, 'TicketForm_agree')

        if form_checkbox is not None:
            try:
                form_checkbox.click()
            except Exception as exc:
                print("click TicketForm_agree fail")
                pass
    except Exception as exc:
        print("find TicketForm_agree fail")

    # 使用 plan B.
    try:
        #driver.execute_script("$(\"input[type='checkbox']\").prop('checked', true);")
        driver.execute_script("document.getElementById(\"TicketForm_agree\").checked;")
    except Exception as exc:
        print("javascript check TicketForm_agree fail")
        print(exc)
        pass

    # select options
    select = None
    try:
        #select = driver.find_element(By.TAG_NAME, 'select')
        select = Select(form_select)
        #select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
    except Exception as exc:
        print("select fail")

    if select is not None:
        try:
            # target ticket number
            select.select_by_visible_text(ticket_number)
            #select.select_by_value(ticket_number)
            #select.select_by_index(int(ticket_number))
        except Exception as exc:
            print("select_by_visible_text ticket_number fail")
            print(exc)

            try:
                # target ticket number
                select.select_by_visible_text(ticket_number)
                #select.select_by_value(ticket_number)
                #select.select_by_index(int(ticket_number))
            except Exception as exc:
                print("select_by_visible_text ticket_number fail...2")
                print(exc)

                # try buy one ticket
                try:
                    select.select_by_visible_text("1")
                    #select.select_by_value("1")
                    #select.select_by_index(int(ticket_number))
                except Exception as exc:
                    print("select_by_visible_text 1 fail")
                    pass

    # because click cause click wrong row.
    if select is not None:
        try:
            # target ticket number
            #select.select_by_visible_text(ticket_number)
            print("assign ticker number by jQuery:",ticket_number)
            driver.execute_script("$(\"input[type='select']\").val(\""+ ticket_number +"\");")
        except Exception as exc:
            print("jQuery select_by_visible_text ticket_number fail (after click.)")
            print(exc)

    # click again.
    try:
        form_select.click()
    except Exception as exc:
        print("click select fail")
        pass

    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.ID, 'TicketForm_verifyCode')
        if form_verifyCode is not None:
            try:
                form_verifyCode.click()
            except Exception as exc:
                print("click form_verifyCode fail")
                pass
    except Exception as exc:
        print("find form_verifyCode fail")

def tixcraft_verify(driver, url):
    ret = False

    captcha_password_string = None

    form_select = None
    question_text = ""
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.zone-verify')


        if form_select is not None:
            html_text = ""
            try:
                question_text = form_select.text
                html_text = question_text

                html_text = html_text.replace(u'「',u'【')
                html_text = html_text.replace(u'〔',u'【')
                html_text = html_text.replace(u'［',u'【')
                html_text = html_text.replace(u'〖',u'【')
                html_text = html_text.replace(u'[',u'【')

                html_text = html_text.replace(u'」',u'】')
                html_text = html_text.replace(u'〕',u'】')
                html_text = html_text.replace(u'］',u'】')
                html_text = html_text.replace(u'〗',u'】')
                html_text = html_text.replace(u']',u'】')

                #print("html_text:", html_text)
                if u'【' in html_text and u'】' in html_text:
                    #captcha_password_string = find_between(html_text, u"【", u"】")
                    pass
            except Exception as exc:
                print("get text fail")
    except Exception as exc:
        print("find verify fail")
        pass


    is_options_in_question = False
    html_text = question_text
    html_text = html_text.replace(u'「',u'(')
    html_text = html_text.replace(u'〔',u'(')
    html_text = html_text.replace(u'［',u'(')
    html_text = html_text.replace(u'〖',u'(')
    html_text = html_text.replace(u'[',u'(')
    html_text = html_text.replace(u'」',u')')
    html_text = html_text.replace(u'〕',u')')
    html_text = html_text.replace(u'］',u')')
    html_text = html_text.replace(u'〗',u')')
    html_text = html_text.replace(u']',u')')
    #print("html_text", html_text)
    answer_list, my_answer_delimitor = get_answer_list_by_question(html_text)

    if u'請輸入"YES"，代表您已詳閱且瞭解並同意' in html_text and u'實名制規則' in html_text:
        captcha_password_string = 'YES'

    if not captcha_password_string is None:
        form_input = None
        try:
            form_input = driver.find_element(By.CSS_SELECTOR, '#checkCode')
            if form_input is not None:
                default_value = form_input.get_attribute('value')
                if not default_value is None:
                    if len(default_value) == 0:
                        form_input.send_keys(captcha_password_string)
                        print("send captcha keys:" + captcha_password_string)
                        time.sleep(0.2)
                        ret = True
            else:
                print("find captcha input field fail")

        except Exception as exc:
            print("find verify fail")
            pass

        if ret:
            form_input = None
            try:
                form_input = driver.find_element(By.CSS_SELECTOR, '#submitButton')
            except Exception as exc:
                print("find submit button fail")
                print(exc)
                pass

            # retry
            is_submited = False
            for i in range(3):
                if form_input is not None:
                    is_visible = False
                    try:
                        if form_input.is_enabled():
                            is_visible = True
                    except Exception as exc:
                        pass

                    if is_visible:
                        try:
                            form_input.click()
                            is_submited = True
                        except Exception as exc:
                            try:
                                driver.execute_script("arguments[0].click();", el)
                                is_submited = True
                            except Exception as exc:
                                pass
                else:
                    print("find submit button none")

                if is_submited:
                    break

    else:
        is_auto_focus_enable = False
        if not answer_list is None:
            if len(answer_list) > 1:
                is_auto_focus_enable = True

        if u'請輸入玉山銀行信用卡' in html_text:
            is_auto_focus_enable = True

        if u'請輸入"YES"' in html_text:
            is_auto_focus_enable = True

        print("is_auto_focus_enable", is_auto_focus_enable)
        if is_auto_focus_enable:
            form_input = None
            try:
                form_input = driver.find_element(By.CSS_SELECTOR, '#checkCode')
                if form_input is not None:
                    default_value = form_input.get_attribute('value')
                    is_need_focus = False
                    if default_value is None:
                        is_need_focus = True
                    else:
                        if len(default_value) == 0:
                            is_need_focus = True
                    if is_need_focus:
                        if form_input.is_enabled():
                            form_input.click()
                            time.sleep(0.2)
                else:
                    print("find captcha input field fail")
            except Exception as exc:
                print("find verify fail")
                pass

    return ret

def tixcraft_ticket_main(driver, url, is_verifyCode_editing):
    form_select = None
    try:
        #form_select = driver.find_element(By.TAG_NAME, 'select')
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')

        if form_select is not None:
            try:
                #print("get select ticket value:" + Select(form_select).first_selected_option.text)
                if Select(form_select).first_selected_option.text=="0":
                    is_verifyCode_editing = False
            except Exception as exc:
                print("query selected option fail")
                print(exc)
                pass

            if is_verifyCode_editing == False:
                ticket_number_auto_fill(url, form_select)

                # start to input verify code.
                try:
                    #driver.execute_script("$('#TicketForm_verifyCode').focus();")
                    driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").focus();")

                    is_verifyCode_editing = True
                    print("goto is_verifyCode_editing== True")
                except Exception as exc:
                    print(exc)
                    pass
            else:
                #print("is_verifyCode_editing")
                # do nothing here.
                pass

    except Exception as exc:
        print("find select fail")
        pass

    return is_verifyCode_editing

# PS: There are two "Next" button in kktix.
#   : 1: /events/xxx
#   : 2: /events/xxx/registrations/new
#   : This is ONLY for case-1, because case-2 lenght >5
def kktix_events_press_next_button(driver):
    ret = False

    # let javascript to enable button.
    time.sleep(0.2)

    wait = WebDriverWait(driver, 1)
    next_step_button = None
    try:
        # method #3 wait
        next_step_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.tickets a.btn-point')))
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        print("wait form-actions div wait to be clickable Exception:")
        #print(exc)
        pass

        if not next_step_button is None:
            is_visible = False
            try:
                if next_step_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    driver.execute_script("arguments[0].click();", next_step_button)
                    ret = True
                except Exception as exc:
                    pass

    return ret

#   : This is for case-2 next button.
def kktix_press_next_button(driver):
    ret = False

    wait = WebDriverWait(driver, 1)
    next_step_button = None
    try:
        # method #1
        #form_actions_div = None
        #form_actions_div = driver.find_element(By.ID, 'registrationsNewApp')
        #next_step_button = form_actions_div.find_element(By.CSS_SELECTOR, 'div.form-actions button.btn-primary')

        # method #2
        # next_step_button = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp div.form-actions button.btn-primary')

        # method #3 wait
        next_step_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#registrationsNewApp div.form-actions button.btn-primary')))
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True

    except Exception as exc:
        print("wait form-actions div wait to be clickable Exception:")
        print(exc)
        #pass

        if not next_step_button is None:
            is_visible = False
            try:
                if next_step_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass
            
            if is_visible:
                try:
                    driver.execute_script("arguments[0].click();", next_step_button)
                    ret = True
                except Exception as exc:
                    pass


    return ret

def kktix_captcha_text_value(captcha_inner_div):
    ret = ""

    if captcha_inner_div is not None:
        try:
            captcha_password_text = captcha_inner_div.find_element(By.TAG_NAME, "input")
            if not captcha_password_text is None:
                ret = captcha_password_text.get_attribute('value')
            else:
                print("find captcha input field fail")
        except Exception as exc:
            print("find captcha_inner_div Exception:")
            #print(exc)
            pass

    return ret

def kktix_input_captcha_text(captcha_inner_div, captcha_password_string, force_overwrite = False):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    ret = False

    if captcha_inner_div is not None and captcha_password_string is not None:
        try:
            if show_debug_message:
                print("found captcha div")
            captcha_password_text = captcha_inner_div.find_element(By.TAG_NAME, "input")
            if not captcha_password_text is None:
                if show_debug_message:
                    print("found input field")

                inputed_captcha_text = captcha_password_text.get_attribute('value')
                if force_overwrite:
                    captcha_password_text.send_keys(captcha_password_string)
                    print("send captcha keys:" + captcha_password_string)
                    ret = True
                else:
                    # not force overwrite:
                    if len(inputed_captcha_text) == 0:
                        captcha_password_text.send_keys(captcha_password_string)
                        print("send captcha keys:" + captcha_password_string)
                        ret = True
        except Exception as exc:
            if show_debug_message:
                print("find kktix_input_captcha_text Exception:")
                print(exc)
            pass

    return ret

def kktix_assign_ticket_number(driver, ticket_number, kktix_area_keyword, kktix_date_keyword):
    ret = False

    areas = None
    is_ticket_number_assigened = False

    ticket_price_list = None
    try:
        ticket_price_list = driver.find_elements(By.CSS_SELECTOR, '.display-table-row')
    except Exception as exc:
        print("find ticket-price span Exception:")
        print(exc)
        pass

    if ticket_price_list is not None:
        if len(ticket_price_list) > 0:
            areas = []

            row_index = 0
            for row in ticket_price_list:
                row_index += 1

                row_text = ""
                try:
                    row_text = row.text
                    #print("get text:", row_text)
                except Exception as exc:
                    print("get text fail")
                    break

                if len(row_text) > 0:
                    # clean stop word.
                    row_text = format_keyword_string(row_text)

                    # check ticket input textbox.
                    ticket_price_input = None
                    try:
                        ticket_price_input = row.find_element(By.CSS_SELECTOR, "input[type='text']")
                        if ticket_price_input is not None:
                            current_ticket_number = str(ticket_price_input.get_attribute('value'))
                            if ticket_price_input.is_enabled():
                                if len(current_ticket_number) > 0:
                                    if current_ticket_number != "0":
                                        is_ticket_number_assigened = True

                                if len(kktix_area_keyword) == 0:
                                    areas.append(row)
                                else:
                                    # match keyword.
                                    # clean stop word.
                                    kktix_area_keyword = format_keyword_string(kktix_area_keyword)

                                    if len(kktix_date_keyword) == 0:
                                        areas.append(row)
                                    else:
                                        if kktix_area_keyword in row_text:
                                            kktix_date_keyword = kktix_date_keyword.replace(',','')
                                            if kktix_date_keyword in row_text:
                                                areas.append(row)
                            else:
                                #disabled.
                                if len(current_ticket_number) > 0:
                                    if current_ticket_number != "0":
                                        is_ticket_number_assigened = True

                    except Exception as exc:
                        pass
    else:
        print("find ticket-price span fail")


    if is_ticket_number_assigened:
        ret = True
    else:
        area = None
        if areas is not None:
            if len(areas) > 0:
                target_row_index = 0

                if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if kktix_area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(areas)-1

                if kktix_area_auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(areas)-1)

                #print("target_row_index", target_row_index)
                area = areas[target_row_index]

        if area is not None:
            #print("area text", area.text)
            ticket_price_input = None
            try:
                wait = WebDriverWait(area, 1)
                ticket_price_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']")))
                if ticket_price_input is not None:
                    if ticket_price_input.is_enabled():
                        current_ticket_number = str(ticket_price_input.get_attribute('value'))
                        if current_ticket_number == "0":
                            try:
                                #print("asssign ticket number:%s" % str(ticket_number))
                                ticket_price_input.clear()
                                ticket_price_input.send_keys(ticket_number)

                                ret = True
                            except Exception as exc:
                                print("asssign ticket number to ticket-price field Exception:")
                                print(exc)
                                ticket_price_input.clear()
                                ticket_price_input.send_keys("1")

                                ret = True
                                pass
                        else:
                            # assigned
                            if str(ticket_number) == current_ticket_number:
                                ret = True
                    else:
                        print("find input, but not is enabled!")
                else:
                    print("find input div fail!")

            except Exception as exc:
                print("find input tag for price Exception")
                #print(exc)
                pass

    return ret

def kktix_get_web_datetime(url, registrationsNewApp_div):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    web_datetime = None

    is_found_web_datetime = False

    el_web_datetime_list = None
    if not registrationsNewApp_div is None:
        try:
            el_web_datetime_list = registrationsNewApp_div.find_elements(By.TAG_NAME, 'td')
        except Exception as exc:
            if show_debug_message:
                print("find td.ng-binding Exception")
                print(exc)
            pass
        #print("is_found_web_datetime", is_found_web_datetime)

    if el_web_datetime_list is not None:
        el_web_datetime_list_count = len(el_web_datetime_list)
        if el_web_datetime_list_count > 0:
            el_web_datetime = None
            for el_web_datetime in el_web_datetime_list:
                try:
                    el_web_datetime_text = el_web_datetime.text
                    if show_debug_message:
                        print("el_web_datetime_text:", el_web_datetime_text)

                    now = datetime.now()
                    #print("now:", now)
                    for guess_year in range(now.year,now.year+3):
                        current_year = str(guess_year)
                        if current_year in el_web_datetime_text:
                            if u'/' in el_web_datetime_text:
                                web_datetime = el_web_datetime_text
                                is_found_web_datetime = True
                                break

                    if is_found_web_datetime:
                        break
                except Exception as exc:
                    if show_debug_message:
                        print('parse web datetime fail:')
                        print(exc)
                    pass
    else:
        print("find td.ng-binding fail")

    return web_datetime

def kktix_check_agree_checkbox(driver):
    is_need_refresh = False
    is_finish_checkbox_click = False

    person_agree_terms_checkbox = None
    try:
        person_agree_terms_checkbox = driver.find_element(By.ID, 'person_agree_terms')
        if person_agree_terms_checkbox is not None:
            if person_agree_terms_checkbox.is_enabled():
                #print("find person_agree_terms checkbox")
                if not person_agree_terms_checkbox.is_selected():
                    #print('send check to checkbox')
                    person_agree_terms_checkbox.click()
                    is_finish_checkbox_click = True
                else:
                    #print('checked')
                    is_finish_checkbox_click = True
                    pass
            else:
                is_need_refresh = True
        else:
            is_need_refresh = True
            print("find person_agree_terms checkbox fail")
    except Exception as exc:
        print("find person_agree_terms checkbox Exception")
        pass

    return is_need_refresh, is_finish_checkbox_click

def kktix_check_register_status(url):
    #ex: https://xxx.kktix.cc/events/xxx
    prefix_list = ['.com/events/','.cc/events/']
    postfix = '/registrations/new'

    is_match_event_code = False
    event_code = ""
    for prefix in prefix_list:
        event_code = find_between(url,prefix,postfix)
        if len(event_code) > 0:
            is_match_event_code = True
            #print('event_code:',event_code)
            break

    html_result = None
    if is_match_event_code:
        url = "https://kktix.com/g/events/%s/register_info" % (event_code)
        #print('event_code:',event_code)
        #print("url:", url)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        headers = {"Accept-Language": "zh-TW,zh;q=0.5", 'User-Agent': user_agent}

        try:
            html_result = requests.get(url , headers=headers, timeout=0.7, allow_redirects=False)
        except Exception as exc:
            html_result = None
            print("send reg_info request fail:")
            print(exc)

    registerStatus = None
    if not html_result is None:
        status_code = html_result.status_code
        #print("status_code:",status_code)

        if status_code == 200:
            html_text = html_result.text
            #print("html_text:", html_text)

            try:
                jsLoads = json.loads(html_text)
                if 'inventory' in jsLoads:
                    if 'registerStatus' in jsLoads['inventory']:
                        registerStatus = jsLoads['inventory']['registerStatus']
            except Exception as exc:
                print("load reg_info json fail:")
                print(exc)
                pass

    #print("registerStatus:", registerStatus)
    return registerStatus

def kktix_reg_new_main(url, answer_index, registrationsNewApp_div, is_finish_checkbox_click, auto_fill_ticket_number, ticket_number, kktix_area_keyword, kktix_date_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    #---------------------------
    # part 2: ticket number
    #---------------------------
    is_assign_ticket_number = False
    if auto_fill_ticket_number:
        for retry_index in range(8):
            is_assign_ticket_number = kktix_assign_ticket_number(driver, ticket_number, kktix_area_keyword, kktix_date_keyword)
            if is_assign_ticket_number:
                break
    #print('is_assign_ticket_number:', is_assign_ticket_number)

    #---------------------------
    # part 3: captcha
    #---------------------------
    # is captcha div appear
    is_captcha_appear = False
    is_captcha_appear_and_filled_password = False

    # try to auto answer options.
    answer_list = None
    is_need_keep_symbol = False
    my_answer_delimitor = ""

    captcha_inner_div = None
    try:
        captcha_inner_div = driver.find_element(By.CSS_SELECTOR, '.custom-captcha-inner')
    except Exception as exc:
        #print(exc)
        #print("find captcha_inner_div fail")
        pass

    if captcha_inner_div is not None:
        if show_debug_message:
            print("found captcha_inner_div layor.")

        captcha_text_div = None
        try:
            captcha_text_div = captcha_inner_div.find_element(By.TAG_NAME, "p")
        except Exception as exc:
            pass
            print("find p tag(captcha_text_div) fail")
            print(exc)

        captcha_password_string = None
        if captcha_text_div is not None:
            is_captcha_appear = True

            captcha_text_div_text = ""
            try:
                captcha_text_div_text = captcha_text_div.text
            except Exception as exc:
                pass

            if show_debug_message:
                print("captcha_text_div_text:", captcha_text_div_text)

            #captcha_text_div_text = u"請回答下列問題,請在下方空格輸入DELIGHT（請以半形輸入法作答，大小寫需要一模一樣）"
            #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「abc」"
            #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「0118eveconcert」（請以半形小寫作答。）"

            # format text
            keep_symbol_tmp = captcha_text_div_text
            keep_symbol_tmp = keep_symbol_tmp.replace(u'也',u'須')
            keep_symbol_tmp = keep_symbol_tmp.replace(u'必須',u'須')

            keep_symbol_tmp = keep_symbol_tmp.replace(u'全都',u'都')
            keep_symbol_tmp = keep_symbol_tmp.replace(u'全部都',u'都')

            keep_symbol_tmp = keep_symbol_tmp.replace(u'一致',u'相同')
            keep_symbol_tmp = keep_symbol_tmp.replace(u'一樣',u'相同')
            keep_symbol_tmp = keep_symbol_tmp.replace(u'相等',u'相同')

            if u'符號須都相同' in keep_symbol_tmp:
                is_need_keep_symbol = True

            if u'符號都相同' in keep_symbol_tmp:
                is_need_keep_symbol = True

            if u'符號須相同' in keep_symbol_tmp:
                is_need_keep_symbol = True

            # 請在下方空白處輸入引號內文字：
            if captcha_password_string is None:
                is_use_quota_message = False
                if u"「" in captcha_text_div_text and u"」" in captcha_text_div_text:
                    if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                        is_use_quota_message = True
                    if u'半形' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                        is_use_quota_message = True
                #print("is_use_quota_message:" , is_use_quota_message)
                if is_use_quota_message:
                    captcha_password_string = find_between(captcha_text_div_text, u"「", u"」")
                    #print("find captcha text:" , captcha_password_string)

            if captcha_password_string is None:
                is_use_quota_message = False
                if u"【" in captcha_text_div_text and u"】" in captcha_text_div_text:
                    if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                        is_use_quota_message = True
                    if u'半形' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                        is_use_quota_message = True
                #print("is_use_quota_message:" , is_use_quota_message)
                if is_use_quota_message:
                    captcha_password_string = find_between(captcha_text_div_text, u"【", u"】")
                    #print("find captcha text:" , captcha_password_string)


            # 請回答下列問題,請在下方空格輸入DELIGHT（請以半形輸入法作答，大小寫需要一模一樣）
            if captcha_password_string is None:
                # clean stop word
                tmp_text = captcha_text_div_text
                tmp_text = tmp_text.replace(u'（',u'(')
                tmp_text = tmp_text.replace(u'）',u')')
                tmp_text = tmp_text.replace(u'：',u':')
                tmp_text = tmp_text.replace(u'空白',u'空格')
                tmp_text = tmp_text.replace(u'填入',u'輸入')

                if u"空格" in tmp_text and u"輸入" in tmp_text:
                    if not u"(" in tmp_text:
                        tmp_text += u"("
                    captcha_password_string = find_between(tmp_text, u"輸入", u"(")
                    captcha_password_string = captcha_password_string.strip()
                    captcha_password_string = captcha_password_string.replace(u'「',u'')
                    captcha_password_string = captcha_password_string.replace(u'」',u'')
                    captcha_password_string = captcha_password_string.replace(u'：',u'')
                    captcha_password_string = captcha_password_string.replace(u'引號',u'')
                    captcha_password_string = captcha_password_string.replace(u'內',u'')
                    captcha_password_string = captcha_password_string.replace(u'文字',u'')

            #captcha_text_div_text = "請問下列哪張專輯為林俊傑出道專輯?(1A)飛行者(2B)礫行者(3C)樂行者（請以半形輸入法作答，大小寫需要一模一樣，範例:1A）"
            #captcha_text_div_text = "以下哪個「不是」正確的林俊傑與其他藝人合唱的歌曲組合？（選項為歌名/合作藝人 ，請以半形輸入法作答選項，大小寫需要一模一樣，範例:jju） 選項： (jjz)I am alive/Jason Mraz (jjy)友人說/張懷秋 (jjx)豆漿油條/A-Sa蔡卓妍 (jjw)黑暗騎士/五月天阿信 (jjv)手心的薔薇/G.E.M鄧紫棋"

            # for test.
            #captcha_password_string = None
            #captcha_text_div_text = u"以下哪個「不是」正確的林俊傑與其他藝人合唱的歌曲組合？（選項為歌名/合作藝人 ，請以半形輸入法作答選項，大小寫需要一模一樣，範例:jju） 選項： (jja)小酒窩/A-Sa蔡卓妍 (jjb)被風吹過的夏天/金莎 (jjc)友人說/張懷秋 (jjd)全面開戰/五月天阿信 (jje)小說/阿杜, (0118eveconcert)0118eveconcert"
            #captcha_text_div_text = u"以下哪個「不是」正確的林俊傑與其他藝人合唱的歌曲組合？（選項為歌名/合作藝人 ，請以半形輸入法作答選項，大小寫需要一模一樣，範例:jju） 選項： (jja)小酒窩/A-Sa蔡卓妍 (jjb)被風吹過的夏天/金莎 (jjc)友人說/張懷秋 (jjd)全面開戰/五月天阿信 (jje)小說/阿杜"
            #captcha_text_div_text = u"以下哪個「不是」正確的林俊傑與其他藝人合唱的歌曲組合？（選項為歌名/合作藝人 ，請以半形輸入法作答選項，大小寫需要一模一樣，範例:jju） 選項： (jja)小酒窩/A-Sa蔡卓妍 (jjb)被風吹過的夏天/金莎 (jjc)友人說/張懷秋 (jjd)全面開戰/五月天阿信 (jje)小說/阿杜"
            #captcha_text_div_text = u"請問《龍的傳人2060》演唱會是以下哪位藝人的演出？（請以半形輸入法作答，大小寫需要一模一樣，範例：B2）A1.周杰倫 B2.林俊傑 C3.張學友 D4.王力宏 4:4"

            # parse '演出日期'
            is_need_parse_web_datetime = False
            # '半形阿拉伯數字' & '半形數字'
            if u'半形' in captcha_text_div_text and u'字' in captcha_text_div_text:
                if u'演出日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'活動日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'表演日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'開始日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'演唱會日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'展覽日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
                if u'音樂會日期' in captcha_text_div_text:
                    is_need_parse_web_datetime = True
            if u'the date of the show you purchased' in captcha_text_div_text:
                is_need_parse_web_datetime = True

            if show_debug_message:
                print("is_need_parse_web_datetime:", is_need_parse_web_datetime)

            if is_need_parse_web_datetime:
                captcha_password_string = None
                web_datetime = kktix_get_web_datetime(url, registrationsNewApp_div)
                if not web_datetime is None:
                    if show_debug_message:
                        print("web_datetime:", web_datetime)

                    captcha_text_formatted = captcha_text_div_text
                    # replace ex.
                    ex_delimiter=u'範例'
                    captcha_text_formatted = captcha_text_formatted.replace(u'例如', ex_delimiter)
                    captcha_text_formatted = captcha_text_formatted.replace(u'如:', ex_delimiter)
                    captcha_text_formatted = captcha_text_formatted.replace(u'舉例', ex_delimiter)

                    # important, maybe 例 & ex occurs at same time.
                    captcha_text_formatted = captcha_text_formatted.replace(u'ex:', ex_delimiter)

                    captcha_text_formatted = captcha_text_formatted.replace(u'輸入：', ex_delimiter)
                    captcha_text_formatted = captcha_text_formatted.replace(u'輸入', ex_delimiter)

                    if show_debug_message:
                        print("captcha_text_formatted", captcha_text_formatted)

                    my_datetime_foramted = None

                    # MMDD
                    if my_datetime_foramted is None:
                        if u'4位半形' in captcha_text_formatted:
                            my_datetime_foramted = "%m%d"

                    # for "如為2月30日，請輸入0230"
                    if my_datetime_foramted is None:
                        if ex_delimiter in captcha_text_formatted:
                            right_part = captcha_text_formatted.split(ex_delimiter)[1]
                            number_text = find_continuous_number(right_part)

                            my_anwser_formated = convert_string_to_pattern(number_text, dynamic_length=False)
                            if my_anwser_formated == u"[\\d][\\d][\\d][\\d][\\d][\\d][\\d][\\d]":
                                my_datetime_foramted = "%Y%m%d"
                            if my_anwser_formated == u"[\\d][\\d][\\d][\\d]":
                                my_datetime_foramted = "%m%d"
                            #print("my_datetime_foramted:", my_datetime_foramted)

                    if my_datetime_foramted is None:
                        now = datetime.now()
                        for guess_year in range(now.year-4,now.year+2):
                            current_year = str(guess_year)
                            if current_year in captcha_text_formatted:
                                my_hint_index = captcha_text_formatted.find(current_year)
                                my_hint_anwser = captcha_text_formatted[my_hint_index:]
                                #print("my_hint_anwser:", my_hint_anwser)
                                # get after.
                                my_delimitor_symbol = ex_delimiter
                                if my_delimitor_symbol in my_hint_anwser:
                                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                                    my_hint_anwser = my_hint_anwser[my_delimitor_index+len(my_delimitor_symbol):]
                                #print("my_hint_anwser:", my_hint_anwser)
                                # get before.
                                my_delimitor_symbol = u'，'
                                if my_delimitor_symbol in my_hint_anwser:
                                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                                my_delimitor_symbol = u'。'
                                if my_delimitor_symbol in my_hint_anwser:
                                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                                # PS: space may not is delimitor...
                                my_delimitor_symbol = u' '
                                if my_delimitor_symbol in my_hint_anwser:
                                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                                #remove last char.
                                remove_last_char_list = [')','(','.','。','）','（','[',']']
                                for check_char in remove_last_char_list:
                                    if my_hint_anwser[-1:]==check_char:
                                        my_hint_anwser = my_hint_anwser[:-1]

                                my_anwser_formated = convert_string_to_pattern(my_hint_anwser, dynamic_length=False)
                                if my_anwser_formated == u"[\\d][\\d][\\d][\\d][\\d][\\d][\\d][\\d]":
                                    my_datetime_foramted = "%Y%m%d"
                                if my_anwser_formated == u"[\\d][\\d][\\d][\\d]/[\\d][\\d]/[\\d][\\d]":
                                    my_datetime_foramted = "%Y/%m/%d"

                                if show_debug_message:
                                    print("my_hint_anwser:", my_hint_anwser)
                                    print("my_anwser_formated:", my_anwser_formated)
                                    print("my_datetime_foramted:", my_datetime_foramted)
                                break

                    if not my_datetime_foramted is None:
                        my_delimitor_symbol = u' '
                        if my_delimitor_symbol in web_datetime:
                            web_datetime = web_datetime[:web_datetime.find(my_delimitor_symbol)]
                        date_time = datetime.strptime(web_datetime,u"%Y/%m/%d")
                        if show_debug_message:
                            print("date_time:", date_time)
                        ans = None
                        try:
                            ans = date_time.strftime(my_datetime_foramted)
                        except Exception as exc:
                            pass
                        captcha_password_string = ans
                        if show_debug_message:
                            print("my_anwser:", ans)

            # parse '演出時間'
            is_need_parse_web_time = False
            if u'半形' in captcha_text_div_text:
                if u'演出時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'表演時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'開始時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'演唱會時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'展覽時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'音樂會時間' in captcha_text_div_text:
                    is_need_parse_web_time = True
                if u'the time of the show you purchased' in captcha_text_div_text:
                    is_need_parse_web_time = True

            #print("is_need_parse_web_time", is_need_parse_web_time)
            if is_need_parse_web_time:
                captcha_password_string = None
                web_datetime = kktix_get_web_datetime(url, registrationsNewApp_div)
                if not web_datetime is None:
                    tmp_text = captcha_text_div_text
                    # replace ex.
                    tmp_text = tmp_text.replace(u'例如',u'範例')
                    tmp_text = tmp_text.replace(u'如:',u'範例:')
                    tmp_text = tmp_text.replace(u'舉例',u'範例')
                    if not u'範例' in tmp_text:
                        tmp_text = tmp_text.replace(u'例',u'範例')
                    # important, maybe 例 & ex occurs at same time.
                    tmp_text = tmp_text.replace(u'ex:',u'範例:')

                    tmp_text = tmp_text.replace(u'輸入：',u'範例')
                    tmp_text = tmp_text.replace(u'輸入',u'範例')
                    #print("tmp_text", tmp_text)

                    my_datetime_foramted = None

                    if my_datetime_foramted is None:
                        my_hint_anwser = tmp_text

                        my_delimitor_symbol = u'範例'
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[my_delimitor_index+len(my_delimitor_symbol):]
                        #print("my_hint_anwser:", my_hint_anwser)
                        # get before.
                        my_delimitor_symbol = u'，'
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        my_delimitor_symbol = u'。'
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        # PS: space may not is delimitor...
                        my_delimitor_symbol = u' '
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        my_anwser_formated = convert_string_to_pattern(my_hint_anwser, dynamic_length=False)
                        #print("my_hint_anwser:", my_hint_anwser)
                        #print(u"my_anwser_formated:", my_anwser_formated)
                        if my_anwser_formated == u"[\\d][\\d][\\d][\\d]":
                            my_datetime_foramted = "%H%M"
                            if u'12小時' in tmp_text:
                                my_datetime_foramted = "%I%M"

                        if my_anwser_formated == u"[\\d][\\d]:[\\d][\\d]":
                            my_datetime_foramted = "%H:%M"
                            if u'12小時' in tmp_text:
                                my_datetime_foramted = "%I:%M"

                    if not my_datetime_foramted is None:
                        date_delimitor_symbol = u'('
                        if date_delimitor_symbol in web_datetime:
                            date_delimitor_symbol_index = web_datetime.find(date_delimitor_symbol)
                            if date_delimitor_symbol_index > 8:
                                web_datetime = web_datetime[:date_delimitor_symbol_index-1]
                        date_time = datetime.strptime(web_datetime,u"%Y/%m/%d %H:%M")
                        #print("date_time:", date_time)
                        ans = None
                        try:
                            ans = date_time.strftime(my_datetime_foramted)
                        except Exception as exc:
                            pass
                        captcha_password_string = ans
                        #print(u"my_anwser:", ans)

            # name of event.
            if captcha_password_string is None:
                if u"name of event" in tmp_text:
                    if u'(' in tmp_text and u')' in tmp_text and u'ans:' in tmp_text.lower():
                        target_symbol = u"("
                        star_index = tmp_text.find(target_symbol)
                        target_symbol = u":"
                        star_index = tmp_text.find(target_symbol, star_index)
                        target_symbol = u")"
                        end_index = tmp_text.find(target_symbol, star_index)
                        captcha_password_string = tmp_text[star_index+1:end_index]
                        #print("captcha_password_string:", captcha_password_string)

            # 二題式，組合問題。
            is_combine_two_question = False
            if u"第一題" in tmp_text and u"第二題" in tmp_text:
                is_combine_two_question = True
            if u"Q1." in tmp_text and u"Q2." in tmp_text:
                if u"二題" in tmp_text:
                    is_combine_two_question = True
                if u"2題" in tmp_text:
                    is_combine_two_question = True
            if u"Q1:" in tmp_text and u"Q2:" in tmp_text:
                if u"二題" in tmp_text:
                    is_combine_two_question = True
                if u"2題" in tmp_text:
                    is_combine_two_question = True
            if u"Q1 " in tmp_text and u"Q2 " in tmp_text:
                if u"二題" in tmp_text:
                    is_combine_two_question = True
                if u"2題" in tmp_text:
                    is_combine_two_question = True
            if is_combine_two_question:
                captcha_password_string = None
            #print("is_combine_two_question:", is_combine_two_question)

            if show_debug_message:
                print("captcha_password_string:", captcha_password_string)

            # ask question.
            if auto_guess_options:
                if not is_combine_two_question:
                    if captcha_password_string is None:
                        answer_list, my_answer_delimitor = get_answer_list_by_question(captcha_text_div_text)
                else:
                    # no need guess options.
                    pass


            # final run.
            if captcha_password_string is not None:
                # password is not None, try to send.
                if kktix_input_captcha_text(captcha_inner_div, captcha_password_string):
                    is_captcha_appear_and_filled_password = True

    if auto_press_next_step_button:
        # pass switch check.

        #print("is_assign_ticket_number", is_assign_ticket_number)
        if is_assign_ticket_number:
            # must input the ticket number correct.
            #print("is_captcha_appear:", is_captcha_appear)
            #print("is_captcha_appear_and_filled_password:", is_captcha_appear_and_filled_password)

            # must ensure checkbox has been checked.
            if not is_finish_checkbox_click:
                for retry_i in range(5):
                    # retry again.
                    is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)
                    time.sleep(0.1)
                    if is_finish_checkbox_click:
                        break

            if not is_captcha_appear:
                # without captcha.
                # normal mode.
                #print("# normal mode.")
                if is_finish_checkbox_click:
                    click_ret = kktix_press_next_button(driver)
                    if not click_ret:
                        print("press next button fail, retry again.")
                        click_ret = kktix_press_next_button(driver)
                    else:
                        #print("press next button successfully.")
                        pass
                else:
                    print("unable to assign checkbox value")
            else:
                if is_captcha_appear_and_filled_password:
                    # for easy guest mode, we can fill the password correct.
                    #print("for easy guest mode, we can fill the password correct.")
                    if is_finish_checkbox_click:
                        click_ret = kktix_press_next_button(driver)
                        if not click_ret:
                            print("press next button fail, retry again.")
                            click_ret = kktix_press_next_button(driver)
                        else:
                            #print("press next button successfully.")
                            pass
                    else:
                        print("unable to assign checkbox value")
                else:
                    # not is easy guest mode.
                    #print("# not is easy guest mode.")

                    # password force brute
                    if answer_list is None:
                        if not kktix_answer_dictionary_list is None:
                            if len(kktix_answer_dictionary_list) > 0:
                                answer_list = kktix_answer_dictionary_list

                    # remove duplicate list
                    if not answer_list is None:
                        if len(answer_list) > 1:
                            unique = [x for i, x in enumerate(answer_list) if answer_list.index(x) == i]
                            answer_list = unique

                    # start to try
                    if not answer_list is None:
                        # for popular event
                        if len(answer_list) > 0:
                            if answer_index < len(answer_list)-1:
                                if kktix_captcha_text_value(captcha_inner_div) == "":
                                    answer_index += 1
                                    answer = answer_list[answer_index]

                                    if len(my_answer_delimitor) > 0:
                                        if answer[-1:] == my_answer_delimitor:
                                            answer = answer[:-1]

                                    if len(answer) > 0:
                                        print("send ans:" + answer)
                                        captcha_password_string = answer
                                        if kktix_input_captcha_text(captcha_inner_div, captcha_password_string):
                                            kktix_press_next_button(driver)
                            else:
                                # exceed index, do nothing.
                                pass
                    else:
                        # captcha appear but we do no have answer list.
                        pass


    return answer_index

def kktix_reg_new(driver, url, answer_index, kktix_register_status_last):
    registerStatus = kktix_register_status_last

    #---------------------------
    # part 1: checkbox.
    #---------------------------
    # check i agree (javascript)

    # method #1
    # use this method cuase "next button not able to enable"
    '''
    try:
        #driver.execute_script("document.getElementById(\"person_agree_terms\").checked;")
        driver.execute_script("$(\"#person_agree_terms\").prop('checked', true);")
    except Exception as exc:
        print("javascript check person_agree_terms fail")
        print(exc)
        pass
    '''

    # auto refresh for area list page.
    is_need_refresh = False
    is_finish_checkbox_click = False

    if not is_need_refresh:
        if registerStatus is None:
            registerStatus = kktix_check_register_status(url)
            if not registerStatus is None:
                print("registerStatus:", registerStatus)
                # OUT_OF_STOCK
                if registerStatus != 'IN_STOCK':
                    is_need_refresh = True

    if not is_need_refresh:
        is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)

        if not is_finish_checkbox_click:
            # retry again.
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)
        #print('check agree_terms_checkbox, is_need_refresh:',is_need_refresh)

    # check is able to buy.
    registrationsNewApp_div = None
    el_list = None
    if not is_need_refresh:
        try:
            registrationsNewApp_div = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp')
        except Exception as exc:
            pass
            #print("find input fail:", exc)

    if is_need_refresh:
        try:
            print("try to refresh page...")
            driver.refresh()
        except Exception as exc:
            #print("refresh fail")
            pass

        # reset answer_index
        answer_index = -1
        registerStatus = None
    else:
        global auto_fill_ticket_number
        global ticket_number
        global kktix_area_keyword
        global kktix_date_keyword
        answer_index = kktix_reg_new_main(url, answer_index, registrationsNewApp_div, is_finish_checkbox_click, auto_fill_ticket_number, ticket_number, kktix_area_keyword, kktix_date_keyword)


    return answer_index, registerStatus



# PURPOSE: get target area list.
# PS: this is main block, use keyword to get rows.
# PS: it seems use date_auto_select_mode instead of area_auto_select_mode
def get_fami_target_area(date_keyword, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    areas = None

    area_list = None
    try:
        if show_debug_message:
            print("try to find area block by keywords...")

        my_css_selector = "table.session__list > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        if area_list is not None:
            area_list_length = len(area_list)
            if show_debug_message:
                print("lenth of area rows:", area_list_length)

            if area_list_length > 0:
                ret = True

                areas = []

                if len(date_keyword)==0 and len(area_keyword_1)==0 and len(area_keyword_2) == 0:
                    # select all.
                    # PS: must travel to row buttons.
                    #areas = area_list

                    row_index = 0
                    for row in area_list:
                        row_index += 1
                        #print("row index:", row_index)

                        is_enabled = False
                        my_css_selector = "button"
                        td_button = row.find_element(By.TAG_NAME , my_css_selector)
                        if td_button is not None:
                            is_enabled = td_button.is_enabled()

                        if not is_enabled:
                            # must skip this row.
                            continue
                        else:
                            if show_debug_message:
                                print("row button is disabled!")

                        if is_enabled:
                            areas.append(td_button)

                            # PS: it seems use date_auto_select_mode instead of area_auto_select_mode
                            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                print("only need first item, break area list loop.")
                                break

                else:
                    # match keyword.
                    row_index = 0
                    for row in area_list:
                        row_index += 1
                        #print("row index:", row_index)

                        date_html_text = ""
                        area_html_text = ""

                        my_css_selector = "td:nth-child(1)"
                        td_date = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_date is not None:
                            #print("date:", td_date.text)
                            date_html_text = td_date.text

                        my_css_selector = "td:nth-child(2)"
                        td_area = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_area is not None:
                            #print("area:", td_area.text)
                            area_html_text = td_area.text


                        is_enabled = False
                        my_css_selector = "button"
                        td_button = row.find_element(By.TAG_NAME , my_css_selector)
                        if td_button is not None:
                            is_enabled = td_button.is_enabled()

                        if not is_enabled:
                            # must skip this row.
                            continue
                        else:
                            if show_debug_message:
                                print("row button is disabled!")

                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get row text fail")
                            break

                        if len(row_text) > 0:
                            # check date.
                            is_match_date = False
                            if len(date_keyword) > 0:
                                if date_keyword in date_html_text:
                                    #print("is_match_date")
                                    is_match_date = True
                            else:
                                is_match_date = True

                            # check area.
                            is_match_area = False
                            if len(area_keyword_1) > 0:
                                if area_keyword_1 in area_html_text:
                                    #print("is_match_area area_keyword_1")
                                    is_match_area = True
                                
                                # check keyword 2
                                if len(area_keyword_2) > 0:
                                    if area_keyword_2 in area_html_text:
                                        #print("is_match_area area_keyword_2")
                                        is_match_area = True

                                # check keyword 3
                                if len(area_keyword_3) > 0:
                                    if area_keyword_3 in area_html_text:
                                        #print("is_match_area area_keyword_3")
                                        is_match_area = True

                                # check keyword 4
                                if len(area_keyword_4) > 0:
                                    if area_keyword_4 in area_html_text:
                                        #print("is_match_area area_keyword_4")
                                        is_match_area = True
                            else:
                                is_match_area = True

                            if is_match_date and is_match_area:
                                #print("bingo, row text:", row_text)
                                #areas.append(row)
                                # add button instead of row.
                                areas.append(td_button)

                                if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                    print("only need first item, break area list loop.")
                                    break

                return_row_count = len(areas)
                if show_debug_message:
                    print("return_row_count:", return_row_count)
                if return_row_count==0:
                    areas = None

    except Exception as exc:
        pass
        print("find #session date list fail")
        if show_debug_message:
            print(exc)

    return areas


def fami_activity(driver, url):
    #print("fami_activity bingo")

    #---------------------------
    # part 1: press "buy" button.
    #---------------------------
    fami_start_to_buy_button = None
    fami_start_to_buy_button = driver.find_element(By.ID, 'buyWaiting')
    if fami_start_to_buy_button is not None:
        is_visible = False
        try:
            if fami_start_to_buy_button.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if fami_start_to_buy_button.is_enabled():
            try:
                fami_start_to_buy_button.click()
            except Exception as exc:
                print("click buyWaiting button fail...")
                #print(exc)
                #pass
                try:
                    driver.execute_script("arguments[0].click();", fami_start_to_buy_button)
                except Exception as exc:
                    pass


def fami_home(driver, url):
    print("fami_home bingo")

    global is_assign_ticket_number
    global ticket_number

    global date_keyword
    global area_keyword_1
    global area_keyword_2
    global area_keyword_3
    global area_keyword_4

    global area_auto_select_mode

    is_select_box_visible = False

    #---------------------------
    # part 3: fill ticket number.
    #---------------------------
    ticket_el = None
    is_assign_ticket_number = False
    try:
        my_css_selector = "tr.ticket > td > select"
        ticket_el = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if ticket_el is not None:
            if ticket_el.is_enabled():
                is_select_box_visible = True

            ticket_number_select = Select(ticket_el)
            if ticket_number_select is not None:
                try:
                    #print("get select ticket value:" + Select(ticket_number_select).first_selected_option.text)
                    if ticket_number_select.first_selected_option.text=="0" or ticket_number_select.first_selected_option.text=="選擇張數":
                        # target ticket number
                        ticket_number_select.select_by_visible_text(ticket_number)
                        is_assign_ticket_number = True
                except Exception as exc:
                    print("select_by_visible_text ticket_number fail")
                    print(exc)

                    try:
                        # try target ticket number twice
                        ticket_number_select.select_by_visible_text(ticket_number)
                        is_assign_ticket_number = True
                    except Exception as exc:
                        print("select_by_visible_text ticket_number fail...2")
                        print(exc)

                        # try buy one ticket
                        try:
                            ticket_number_select.select_by_visible_text("1")
                            is_assign_ticket_number = True
                        except Exception as exc:
                            print("select_by_visible_text 1 fail")
                            pass
    except Exception as exc:
        pass
        print("click buyWaiting button fail")
        #print(exc)

    #---------------------------
    # part 4: press "next" button.
    #---------------------------
    if is_assign_ticket_number:
        my_css_selector = "div.col > a.btn"
        fami_assign_site_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if fami_assign_site_button is not None:
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

    areas = None
    if not is_select_box_visible:
        #---------------------------
        # part 2: select keywords
        #---------------------------
        areas = get_fami_target_area(date_keyword, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode)

        area_target = None
        if areas is not None:
            #print("area_auto_select_mode", area_auto_select_mode)
            #print("len(areas)", len(areas))
            if len(areas) > 0:
                target_row_index = 0

                if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(areas)-1

                if area_auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(areas)-1)

                #print("target_row_index", target_row_index)
                area_target = areas[target_row_index]

        if area_target is not None:
            #print("area text", area_target.text)
            is_visible = False
            try:
                if area_target.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    area_target.click()
                except Exception as exc:
                    print("click buy button fail, start to retry...")
                    try:
                        driver.execute_script("arguments[0].click();", area_target)
                    except Exception as exc:
                        pass

def urbtix_ticket_number_auto_select(driver, url, ticket_number):
    ret = False
    is_assign_ticket_number = False

    try:
        el = driver.find_element(By.CSS_SELECTOR, 'select.chzn-select')
        if el is not None:
            ret = True
            #print("bingo, found ticket_number select")

            ticket_number_select = Select(el)
            if ticket_number_select is not None:
                try:
                    #print("get select ticket value:" + Select(ticket_number_select).first_selected_option.text)
                    if ticket_number_select.first_selected_option.text=="0":
                        # target ticket number
                        ticket_number_select.select_by_visible_text(ticket_number)
                        is_assign_ticket_number = True
                except Exception as exc:
                    print("select_by_visible_text ticket_number fail")
                    print(exc)

                    try:
                        # try target ticket number twice
                        ticket_number_select.select_by_visible_text(ticket_number)
                        is_assign_ticket_number = True
                    except Exception as exc:
                        print("select_by_visible_text ticket_number fail...2")
                        print(exc)

                        # try buy one ticket
                        try:
                            ticket_number_select.select_by_visible_text("1")
                            is_assign_ticket_number = True
                        except Exception as exc:
                            print("select_by_visible_text 1 fail")
                            pass

    except Exception as exc:
        print("find ticket_number select fail...")
        time.sleep(0.1)
        #print(exc)
        pass

    return ret, is_assign_ticket_number

# purpose: area auto select
# return:
#   True: area block appear.
#   False: area block not appear.
# ps: return value for date auto select.
def urbtix_area_auto_select(driver, url, kktix_area_keyword, kktix_date_keyword):
    ret = False
    areas = None

    area_list = None
    try:
        #print("try to find urbtix area block")
        my_css_selector = "#ticket-price-tbl > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        if area_list is not None:
            if len(area_list) > 0:
                ret = True

                if len(kktix_area_keyword) == 0:
                    areas = area_list
                else:
                    # match keyword.
                    areas = []

                    row_index = 0
                    for row in area_list:
                        row_index += 1
                        row_is_enabled=False
                        try:
                            row_is_enabled = row.is_enabled()
                        except Exception as exc:
                            pass

                        if row_is_enabled:
                            row_text = ""
                            try:
                                row_text = row.text
                            except Exception as exc:
                                print("get text fail")
                                break

                            if len(row_text) > 0:
                                #print("area row_text:", row_index, row_text)
                                if kktix_area_keyword in row_text:
                                    areas.append(row)

    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    area = None
    if areas is not None:
        #print("area_auto_select_mode", area_auto_select_mode)
        #print("len(areas)", len(areas))
        if len(areas) > 0:
            target_row_index = 0

            #if area_auto_select_mode == 'from_top_to_down':
                #pass

            #if area_auto_select_mode == 'from_down_to_up':
                #target_row_index = len(areas)-1

            #if area_auto_select_mode == "random":
                #target_row_index = random.randint(0,len(areas)-1)

            #print("target_row_index", target_row_index)
            area = areas[target_row_index]

    if area is not None:
        el = None
        try:
            #print("area text", area.text)

            my_css_selector = "input.pricezone-radio-input"
            el = area.find_element(By.CSS_SELECTOR, my_css_selector)
            if el is not None:
                if el.is_enabled():
                    if not el.is_selected():
                        el.click()
                    ret = True
                    #print("bingo, click area radio")

        except Exception as exc:
            print("click area radio a link fail")
            print(exc)
            pass

    return ret

def urbtix_next_button_press(driver, url):
    ret = False
    try:
        el = driver.find_element(By.CSS_SELECTOR, '#free-seat-purchase-btn')
        if el is not None:
            el_span = el.find_element(By.TAG_NAME, 'span')
            if el_span is not None:
                #ret = True
                #print("bingo, found next button")

                if el_span.is_enabled():
                    el_span.click()
                    ret = True
    except Exception as exc:
        print("find next button fail")
        print(exc)

    return ret

def urbtix_performance(driver, url):
    #print("urbtix performance bingo")

    global auto_fill_ticket_number
    global ticket_number

    global kktix_area_keyword
    global kktix_date_keyword
    global auto_press_next_step_button

    if auto_fill_ticket_number:
        area_div_exist = urbtix_area_auto_select(driver, url, kktix_area_keyword, kktix_date_keyword)

    ticket_number_select_exist, is_assign_ticket_number = urbtix_ticket_number_auto_select(driver, url, ticket_number)

    # todo.
    if auto_press_next_step_button:
        if is_assign_ticket_number:
            urbtix_next_button_press(driver, url)

# purpose: area auto select
# return:
#   True: area block appear.
#   False: area block not appear.
# ps: return value for date auto select.
def cityline_area_auto_select(url, kktix_area_keyword):
    ret = False
    areas = None

    area_list = None
    try:
        #print("try to find cityline area block")
        # form[name="text"] > table:nth-child(12) > tbody > tr:nth-child(4) > td > table > tbody > tr > td:nth-child(1) > table > tbody > tr
        my_css_selector = "tr.menubar_text ~ tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        if area_list is not None:
            area_list_count = len(area_list)
            #print("area_list_count:", area_list_count)

            if area_list_count > 0:
                ret = True

                if len(kktix_area_keyword) == 0:
                    areas = area_list
                else:
                    # match keyword.
                    #print("start to match keyword:", kktix_area_keyword)
                    areas = []

                    row_index = 0
                    for row in area_list:
                        row_index += 1
                        row_is_enabled=False
                        try:
                            row_is_enabled = row.is_enabled()
                        except Exception as exc:
                            pass

                        if row_is_enabled:
                            row_text = ""
                            try:
                                row_text = row.text
                            except Exception as exc:
                                print("get text fail")
                                break

                            if len(row_text) > 0:
                                # for debug.
                                #print("area row_text:", row_index, row_text)
                                if kktix_area_keyword in row_text:
                                    areas.append(row)

                    #print("after match keyword, found count:", len(areas))
            else:
                print("not found area tr")
                pass
        else:
            print("area tr is None")
            pass

    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    area = None
    if areas is not None:
        #print("area_auto_select_mode", area_auto_select_mode)
        #print("len(areas)", len(areas))
        if len(areas) > 0:
            target_row_index = 0

            #if area_auto_select_mode == 'from_top_to_down':
                #pass

            #if area_auto_select_mode == 'from_down_to_up':
                #target_row_index = len(areas)-1

            #if area_auto_select_mode == "random":
                #target_row_index = random.randint(0,len(areas)-1)

            #print("target_row_index", target_row_index)
            area = areas[target_row_index]

    if area is not None:
        el = None
        try:
            #print("area text", area.text)

            my_css_selector = "input[type=radio]"
            el = area.find_element(By.CSS_SELECTOR, my_css_selector)
            if el is not None:
                if el.is_enabled():
                    if not el.is_selected():
                        el.click()
                    ret = True
                    #print("bingo, click area radio")

        except Exception as exc:
            print("click area radio a link fail")
            print(exc)
            pass

    return ret

def cityline_area_selected_text(url):
    ret = None

    area_list = None
    try:
        #my_css_selector = "table.onePriceZoneInfoTable > tbody > tr"
        my_css_selector = "tr.menubar_text ~ tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        if area_list is not None:
            if len(area_list) > 0:
                row_index = 0
                for row in area_list:
                    row_index += 1
                    row_is_enabled=False
                    try:
                        row_is_enabled = row.is_enabled()
                    except Exception as exc:
                        pass

                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if len(row_text) > 0:
                            el = None
                            try:
                                my_css_selector = "input[type=radio]"
                                el = row.find_element(By.CSS_SELECTOR, my_css_selector)
                                if el is not None:
                                    if el.is_enabled():
                                        if el.is_selected():
                                            ret = row_text
                                            break
                            except Exception as exc:
                                print(exc)
                                pass

    except Exception as exc:
        print(exc)
        pass
    return ret


def cityline_ticket_number_auto_select(url):
    ret = False
    is_assign_ticket_number = False
    selected_value = ""

    try:
        el = driver.find_element(By.CSS_SELECTOR, 'td.tix_type_select > div.chzn-container > a > span')
        if el is not None:
            if el.is_enabled():
                ret = True

                selected_value = el.text
                #print("selected_value:", selected_value)

                if selected_value == "0":
                    el.click()
                    time.sleep(0.3)

                is_options_enabled = False

                el_options = driver.find_element(By.CSS_SELECTOR, 'td.tix_type_select > div.chzn-container > div.chzn-drop')
                if el_options is not None:
                    if el_options.is_enabled():
                        is_options_enabled = True

                #print("is_options_enabled:", is_options_enabled)
                if is_options_enabled:
                    el_options_li = driver.find_elements(By.CSS_SELECTOR, 'td.tix_type_select > div.chzn-container > div.chzn-drop > ul > li')
                    if el_options_li is not None:
                        if len(el_options_li) > 0:
                            for row in el_options_li:
                                if row is not None:
                                    if row.is_enabled():
                                        row_text = row.text
                                        if not row_text is None:
                                            if row_text == ticket_number:
                                                print("row_text clicked:", row_text)
                                                row.click()
                                                is_assign_ticket_number = True
                                                break
    except Exception as exc:
        #print("find ticket_number select fail")
        #print(exc)
        pass

    return ret, is_assign_ticket_number


def cityline_next_button_press(url):
    ret = False
    try:
        time.sleep(0.2)
        el = driver.find_element(By.CSS_SELECTOR, '#expressPurchaseButton')
        if el is not None:
            ret = True
            print("bingo, found next button")

            if el.is_enabled():
                el.click()
                ret = True
    except Exception as exc:
        print("find next button fail")
        print(exc)

    return ret

def cityline_event(driver, url):
    ret = False

    is_non_member_displayed = False

    try:
        el_non_member = driver.find_element(By.ID, 'buyBtWalkIn')
        if el_non_member is not None:
            if el_non_member.is_enabled():
                #if el_non_member.is_displayed():
                is_non_member_displayed = True
    except Exception as exc:
        #print(exc)
        pass

    try:
        el = driver.find_element(By.ID, 'buyBt')
        if el is not None:
            if el.is_enabled():
                #if el.is_displayed():
                    # for non-member
                    #javascript:selectPerformance(1);
                    # for member
                    #javascript:selectPerformance(0);

                if not is_non_member_displayed:
                    # when two buttons appear, do nothing.
                    el.click()
    except Exception as exc:
        #print("find next button fail")
        #print(exc)
        pass

    return ret

def cityline_captcha_auto_focus(url):
    ret = False
    try:
        el = driver.find_element(By.CSS_SELECTOR, 'input[name=verify]')
        if el is not None:
            if el.is_enabled():
                inputed_text = el.get_attribute('value')
                if not inputed_text is None:
                    if len(inputed_text) == 0:
                        #print("click the input text")
                        el.click()
                        ret = True
            else:
                #print("element is not enable")
                pass
        else:
            print("element is None")
    except Exception as exc:
        print("find verify text fail")
        print(exc)
        pass

    # make captcha image bigger/
    if ret:
        try:
            el = driver.find_element(By.CSS_SELECTOR, '#captchaImage')
            if el is not None:
                if el.is_enabled():
                    image_width = el.get_attribute('width')
                    #print("image_width:", image_width)
                    if image_width != 200:
                        driver.execute_script("document.getElementById(\"captchaImage\").width=200;")
        except Exception as exc:
            print("excute script resize fail")
            print(exc)
            pass

    return ret


def cityline_performance(driver, url):
    #print("cityline bingo")
    if "performance.do;" in url:
        cityline_captcha_auto_focus(url)

    global auto_fill_ticket_number
    global kktix_area_keyword
    global auto_press_next_step_button
    global is_assign_ticket_number

    if "?cid=" in url:
        if auto_fill_ticket_number:
            area_div_exist = False
            if len(kktix_area_keyword) > 0:
                area_div_exist = cityline_area_auto_select(url, kktix_area_keyword)

        ticket_number_select_exist, is_assign_ticket_number = cityline_ticket_number_auto_select(url)

        # todo.
        if auto_press_next_step_button:
            if is_assign_ticket_number:
                selected_text = cityline_area_selected_text(url)
                if not selected_text is None:
                    if kktix_area_keyword in selected_text:
                        # must same with our settting to auto press.
                        for i in range(3):
                            click_ret = cityline_next_button_press(url)
                            if click_ret:
                                break


def facebook_login(driver, url):
    ret = False
    try:
        el = driver.find_element(By.CSS_SELECTOR, '#email')
        if el is not None:
            ret = True
            if el.is_enabled():
                inputed_text = el.get_attribute('value')
                if len(inputed_text) == 0:
                    el.send_keys(facebook_account)
                    ret = True
    except Exception as exc:
        #print("find #email fail")
        #print(exc)
        pass

    return ret


def main():
    global driver
    driver = load_config_from_local(driver)

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""
    # for tixcraft
    is_verifyCode_editing = False

    # for kktix
    answer_index = -1
    kktix_register_status_last = None

    global debugMode
    if debugMode:
        print("Start to looping, detect browser url...")

    while True:
        time.sleep(0.1)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        # https://stackoverflow.com/questions/57481723/is-there-a-change-in-the-handling-of-unhandled-alert-in-chromedriver-and-chrome
        default_close_alert_text = []
        if len(default_close_alert_text) > 0:
            try:
                alert = None
                if not driver is None:
                    alert = driver.switch_to.alert
                if not alert is None:
                    if not alert.text is None:
                        is_match_auto_close_text = False
                        for txt in default_close_alert_text:
                            if len(txt) > 0:
                                if txt in alert.text:
                                    is_match_auto_close_text = True
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
                #print('NoSuchWindowException2 at this url:', url )
                #print("last_url:", last_url)
                try:
                    window_handles_count = len(driver.window_handles)
                    if window_handles_count >= 1:
                        driver.switch_to.window(driver.window_handles[0])
                except Exception as excSwithFail:
                    pass
            except Exception as exc:
                logger.error('Exception2 for alert')
                logger.error(exc, exc_info=True)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
        try:
            url = driver.current_url
        
        except NoSuchWindowException:
            #print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass

        except UnexpectedAlertPresentException as exc1:
            print('UnexpectedAlertPresentException at this url:', url )
            time.sleep(3.5)

            # PS: do nothing...
            # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
            # raise exception at selenium/webdriver/remote/errorhandler.py 
            # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
            is_pass_alert = False
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

            exit_bot_error_strings = [u'Max retries exceeded'
            , u'chrome not reachable'
            , u'unable to connect to renderer'
            , u'failed to check if window was closed'
            , u'Failed to establish a new connection'
            , u'Connection refused'
            , u'disconnected'
            , u'without establishing a connection']
            for each_error_string in exit_bot_error_strings:
                # for python2
                # say goodbye to python2
                '''
                try:
                    basestring
                    if isinstance(each_error_string, unicode):
                        each_error_string = str(each_error_string)
                except NameError:  # Python 3.x
                    basestring = str
                '''

                if isinstance(str_exc, str):
                    if each_error_string in str_exc:
                        print(u'quit bot')
                        driver.quit()
                        sys.exit()
                        break

            print("Exception:", str_exc)
            pass

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        if debugMode:
            print("url:", url)

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url

        # for Max's test.
        if '/Downloads/varify.html' in url:
            tixcraft_verify(driver, url)

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if tixcraft_family:
            if url == 'https://tixcraft.com/':
                tixcraft_home(driver)
                continue

            if url == 'https://indievox.com/':
                tixcraft_home(driver)
                continue

            #print("tixcraft_family entry.")
            if '/ticket/order' in url:
                # do nothing.
                continue

            if '/ticket/payment' in url:
                # do nothing.
                continue

            is_redirected = tixcraft_redirect(driver, url)
            if is_redirected:
                # start to redirecting.
                continue

            global date_auto_select_enable
            global date_auto_select_mode
            global date_keyword

            global pass_date_is_sold_out_enable
            global auto_reload_coming_soon_page_enable

            is_date_selected = False
            if date_auto_select_enable:
                is_date_selected = date_auto_select(driver, url, date_auto_select_mode, date_keyword, pass_date_is_sold_out_enable, auto_reload_coming_soon_page_enable)

            if is_date_selected:
                # start to redirecting.
                continue

            # choose area
            global area_auto_select_enable
            global pass_1_seat_remaining_enable

            global area_keyword_1
            global area_keyword_2
            global area_keyword_3
            global area_keyword_4

            if area_auto_select_enable:
                area_auto_select(driver, url, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode, pass_1_seat_remaining_enable)

            if '/ticket/verify/' in url:
                tixcraft_verify(driver, url)

            # main app, to select ticket number.
            if '/ticket/ticket/' in url:
                is_verifyCode_editing = tixcraft_ticket_main(driver, url, is_verifyCode_editing)
            else:
                # not is input verify code, reset flag.
                is_verifyCode_editing = False

        global auto_press_next_step_button

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
            if '/users/sign_in' in url:
                continue

            if '/registrations/new' in url:
                answer_index, kktix_register_status_last = kktix_reg_new(driver, url, answer_index, kktix_register_status_last)
            else:
                is_event_page = False
                if '/events/' in url:
                    # ex: https://xxx.kktix.cc/events/xxx-copy-1
                    if len(url.split('/'))<=5:
                        is_event_page = True

                if is_event_page:
                    if auto_press_next_step_button:
                        # pass switch check.
                        #print("should press next here.")
                        kktix_events_press_next_button(driver)

                answer_index = -1
                kktix_register_status_last = None

        # for famiticket
        if 'famiticket.com' in url:
            if '/Home/Activity/Info/' in url:
                fami_activity(driver, url)
            if '/Sales/Home/Index/' in url:
                fami_home(driver, url)


        # for urbtix
        # https://ticket.urbtix.hk/internet/secure/event/37348/performanceDetail
        if 'urbtix.hk' in url:
        #if False:
            # http://msg.urbtix.hk
            if 'msg.urbtix.hk' in url:
                # delay to avoid ip block.
                time.sleep(1.0)

                try:
                    driver.get('https://www.urbtix.hk/')
                except Exception as exec1:
                    pass

                pass
            # http://busy.urbtix.hk
            if 'busy.urbtix.hk' in url:
                # delay to avoid ip block.
                time.sleep(1.0)
                try:
                    driver.get('https://www.urbtix.hk/')
                except Exception as exec1:
                    pass
                pass

            if '/performanceDetail/' in url:
                urbtix_performance(driver, url)

        if 'cityline.com' in url:
            if '/event.do' in url:
                cityline_event(driver, url)
                #pass

            if '/Events.do' in url:
                if len(driver.window_handles) == 2:
                    try:
                        driver.close()
                    except Exception as excCloseFail:
                        pass

            if '/performance.do' in url:
                cityline_performance(driver, url)


if __name__ == "__main__":
    main()
