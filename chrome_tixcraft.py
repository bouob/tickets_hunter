#!/usr/bin/env python3
#encoding=utf-8
# 'seleniumwire' and 'selenium 4' raise error when running python 2.x
# PS: python 2.x will be removed in future.
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
import os
import sys
import platform
import json
import random

from selenium import webdriver
# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# for selenium 4
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
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

# ocr
import base64
try:
    import ddddocr
except Exception as exc:
    pass

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONST_APP_VERSION = u"MaxBot (2023.01.12)2版"

CONST_HOMEPAGE_DEFAULT = "https://tixcraft.com"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM)
CONST_SELECT_OPTIONS_ARRAY = [CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM]

CONT_STRING_1_SEATS_REMAINING = [u'@1 seat(s) remaining',u'剩餘 1@',u'@1 席残り']


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
            keyword = keyword.replace('／','/')
            keyword = keyword.replace('　','')
            keyword = keyword.replace(',','')
            keyword = keyword.replace('，','')
            keyword = keyword.replace('$','')
            keyword = keyword.replace(' ','').lower()
    return keyword

def find_continuous_number(text):
    chars = "0123456789"
    return find_continuous_pattern(chars, text)

def find_continuous_text(text):
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return find_continuous_pattern(chars, text)

def find_continuous_pattern(allowed_char, text):
    ret = ""
    is_allowed_char_start = False
    for char in text:
        #print("char:", char)
        if char in allowed_char:
            if len(ret)==0 and not is_allowed_char_start:
                is_allowed_char_start = True
            if is_allowed_char_start:
                ret += char
        else:
            # make not continuous
            is_allowed_char_start = False
    return ret

def get_favoriate_extension_path(webdriver_path):
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.15.2.0.crx")
    return no_google_analytics_path, no_ad_path

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable):
    chrome_options = webdriver.ChromeOptions()

    chromedriver_path = get_chromedriver_path(webdriver_path)

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
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
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})

    #caps = DesiredCapabilities().CHROME
    caps = chrome_options.to_capabilities()

    #caps["pageLoadStrategy"] = u"normal"  #  complete
    caps["pageLoadStrategy"] = u"eager"  #  interactive
    #caps["pageLoadStrategy"] = u"none"

    #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
    #caps["unhandledPromptBehavior"] = u"ignore"
    #caps["unhandledPromptBehavior"] = u"dismiss"
    caps["unhandledPromptBehavior"] = u"accept"

    chrome_service = Service(chromedriver_path)

    # method 6: Selenium Stealth
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=caps)

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
    #print("driver capabilities", driver.capabilities)

    return driver

def load_chromdriver_uc(webdriver_path, adblock_plus_enable):
    import undetected_chromedriver as uc

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"

    #print("strategy", options.page_load_strategy)

    if adblock_plus_enable:
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

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})

    caps = options.to_capabilities()
    caps["unhandledPromptBehavior"] = u"accept"

    driver = None
    if os.path.exists(chromedriver_path):
        print("Use user driver path:", chromedriver_path)
        #driver = uc.Chrome(service=chrome_service, options=options, suppress_welcome=False)
        is_local_chrome_browser_lower = False
        try:
            driver = uc.Chrome(executable_path=chromedriver_path, options=options, desired_capabilities=caps, suppress_welcome=False)
        except Exception as exc:
            if "cannot connect to chrome" in str(exc):
                if "This version of ChromeDriver only supports Chrome version" in str(exc):
                    is_local_chrome_browser_lower = True
            print(exc)
            pass

        if is_local_chrome_browser_lower:
            print("Use local user downloaded chromedriver to lunch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
    else:
        print("Oops! web driver not on path:",chromedriver_path )
        print('let uc automatically download chromedriver.')
        driver = uc.Chrome(options=options, desired_capabilities=caps, suppress_welcome=False)

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
    #print("driver capabilities", driver.capabilities)

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

def get_driver_by_config(config_dict, driver_type):
    global driver

    homepage = None
    browser = None
    language = "English"
    ticket_number = "2"

    auto_press_next_step_button = False     # default not checked.
    auto_fill_ticket_number = False         # default not checked.
    auto_guess_options = False              # default not checked.

    kktix_area_auto_select_mode = ""
    kktix_area_keyword = ""
    kktix_date_keyword = ""

    pass_1_seat_remaining_enable = False        # default not checked.
    pass_date_is_sold_out_enable = False        # default not checked.
    auto_reload_coming_soon_page_enable = True  # default checked.

    area_keyword_1 = ""
    area_keyword_2 = ""
    area_keyword_3 = ""
    area_keyword_4 = ""

    date_keyword = ""

    date_auto_select_enable = None
    date_auto_select_mode = ""

    area_auto_select_enable = None
    area_auto_select_mode = ""

    debugMode = False

    # read config.
    homepage = config_dict["homepage"]
    browser = config_dict["browser"]

    # output debug message in client side.
    debugMode = config_dict["debug"]
    ticket_number = str(config_dict["ticket_number"])
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]

    # for ["kktix"]
    auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
    auto_fill_ticket_number = config_dict["kktix"]["auto_fill_ticket_number"]
    kktix_area_auto_select_mode = config_dict["kktix"]["area_mode"].strip()
    if not kktix_area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
        kktix_area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

    kktix_area_keyword_1 = config_dict["kktix"]["area_keyword_1"].strip()
    kktix_area_keyword_1_and = config_dict["kktix"]["area_keyword_1_and"].strip()
    kktix_area_keyword_2 = config_dict["kktix"]["area_keyword_2"].strip()
    kktix_area_keyword_2_and = config_dict["kktix"]["area_keyword_2_and"].strip()

    # disable password brute force attack
    # PS: because of the question is always variable.

    auto_guess_options = config_dict["kktix"]["auto_guess_options"]

    # for ["tixcraft"]
    date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    if not date_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
        date_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()

    area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
    if not area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
        area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
    area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
    area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()

    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # output config:
    print("maxbot app version", CONST_APP_VERSION)
    print("python version", platform.python_version())
    print("platform", platform.platform())
    print("homepage", homepage)
    print("browser", browser)
    print("ticket_number", ticket_number)
    print("pass_1_seat_remaining", pass_1_seat_remaining_enable)

    # for kktix
    print("==[kktix]==")
    print("auto_press_next_step_button", auto_press_next_step_button)
    print("auto_fill_ticket_number", auto_fill_ticket_number)
    print("kktix_area_keyword_1", kktix_area_keyword_1)
    print("kktix_area_keyword_1_and", kktix_area_keyword_1_and)
    print("kktix_area_keyword_2", kktix_area_keyword_2)
    print("kktix_area_keyword_2_and", kktix_area_keyword_2_and)
    print("auto_guess_options", auto_guess_options)

    # for tixcraft
    print("==[tixcraft]==")
    print("date_auto_select_enable", date_auto_select_enable)
    print("date_auto_select_mode", date_auto_select_mode)
    print("date_keyword", date_keyword)
    print("pass_date_is_sold_out", pass_date_is_sold_out_enable)
    print("auto_reload_coming_soon_page", auto_reload_coming_soon_page_enable)

    print("area_auto_select_enable", area_auto_select_enable)
    print("area_auto_select_mode", area_auto_select_mode)
    print("area_keyword_1", area_keyword_1)
    print("area_keyword_2", area_keyword_2)
    print("area_keyword_3", area_keyword_3)
    print("area_keyword_4", area_keyword_4)

    print("presale_code", config_dict["tixcraft"]["presale_code"])
    print("ocr_captcha", config_dict['ocr_captcha'])
    print("==[advanced]==")
    print("play_captcha_sound", config_dict["advanced"]["play_captcha_sound"]["enable"])
    print("sound file path", config_dict["advanced"]["play_captcha_sound"]["filename"])
    print("adblock_plus_enable", config_dict["advanced"]["adblock_plus_enable"])
    print("debug Mode", debugMode)

    # entry point
    if homepage is None:
        homepage = ""
    if len(homepage) == 0:
        homepage = CONST_HOMEPAGE_DEFAULT

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    adblock_plus_enable = config_dict["advanced"]["adblock_plus_enable"]
    print("adblock_plus_enable:", adblock_plus_enable)

    if browser == "chrome":
        # method 6: Selenium Stealth
        if driver_type != "undetected_chromedriver":
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
        else:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(webdriver_path, adblock_plus_enable)

    if browser == "firefox":
        # default os is linux/mac
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        firefox_service = Service(chromedriver_path)
        driver = webdriver.Firefox(service=firefox_service)

    #print("try to close opened tabs.")
    '''
    time.sleep(1.0)
    for i in range(1):
        close_browser_tabs(driver)
    '''

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            print("goto url:", homepage)
            if homepage=="https://tixcraft.com":
                homepage="https://tixcraft.com/user/changeLanguage/lang/zh_tw"
            driver.get(homepage)
        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exec1)
            pass

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

def guess_answer_list_from_multi_options(tmp_text):
    options_list = None
    if options_list is None:
        if u'【' in tmp_text and u'】' in tmp_text:
            options_list = re.findall(u'【.*?】', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    if options_list is None:
        if u'(' in tmp_text and u')' in tmp_text:
            options_list = re.findall(u'\(.*?\)', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    if options_list is None:
        if u'[' in tmp_text and u']' in tmp_text:
            options_list = re.findall(u'[.*?]', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    return_list = None
    if not options_list is None:
        options_list_length = len(options_list)
        if options_list_length > 2:
            is_all_options_same_length = True
            for i in range(options_list_length-1):
                if len(options_list[i]) != len(options_list[i]):
                    is_all_options_same_length = False

            if is_all_options_same_length:
                return_list = []
                for each_option in options_list:
                    return_list.append(each_option[1:-1])
    return return_list

#PS: this may get a wrong answer list. XD
def guess_answer_list_from_symbols(captcha_text_div_text):
    return_list = None
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
    return return_list

def get_offical_hint_string_from_symbol(symbol, tmp_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    offical_hint_string = ""
    if symbol in tmp_text:
        # start to guess offical hint
        if offical_hint_string == "":
            if u'【' in tmp_text and u'】' in tmp_text:
                hint_list = re.findall(u'【.*?】', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("【.*?】hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'(' in tmp_text and u')' in tmp_text:
                hint_list = re.findall(u'\(.*?\)', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("\(.*?\)hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'[' in tmp_text and u']' in tmp_text:
                hint_list = re.findall(u'[.*?]', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("[.*?]hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            offical_hint_string = tmp_text
    return offical_hint_string

def guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    CONST_INPUT_SYMBOL = '輸入'

    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    my_question = ""
    my_options = ""
    offical_hint_string = ""
    offical_hint_string_anwser = ""
    my_anwser_formated = ""
    my_answer_delimitor = ""

    if my_question == "":
        if u"?" in tmp_text:
            question_index = tmp_text.find(u"?")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        if u"。" in tmp_text:
            question_index = tmp_text.find(u"。")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        my_question = tmp_text
    #print(u"my_question:", my_question)

    # ps: hint_list is not options list

    if offical_hint_string == "":
        offical_hint_string = get_offical_hint_string_from_symbol(CONST_EXAMPLE_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_EXAMPLE_SYMBOL)[1]
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                offical_hint_string_anwser = new_hint

    if offical_hint_string == "":
        # for: 若你覺得答案為 a，請輸入 a
        if '答案' in tmp_text and CONST_INPUT_SYMBOL in tmp_text:
            offical_hint_string = get_offical_hint_string_from_symbol(CONST_INPUT_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_INPUT_SYMBOL)[1]
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                # TODO: 答案為B需填入Bb)
                #if u'答案' in offical_hint_string and CONST_INPUT_SYMBOL in offical_hint_string:
                offical_hint_string_anwser = new_hint

    if show_debug_message:
        print("offical_hint_string:",offical_hint_string)

    # try rule4:
    # get hint from rule 3: without '(' & '), but use "*"
    if len(offical_hint_string) == 0:
        target_symbol = u"*"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index + len(target_symbol))
            offical_hint_string = tmp_text[star_index: space_index]

    # is need to merge next block
    if len(offical_hint_string) > 0:
        target_symbol = offical_hint_string + u" "
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            next_block_index = star_index + len(target_symbol)
            space_index = tmp_text.find(u" ", next_block_index)
            next_block = tmp_text[next_block_index: space_index]
            if CONST_EXAMPLE_SYMBOL in next_block:
                offical_hint_string += u' ' + next_block

    # try rule5:
    # get hint from rule 3: n個半形英文大寫
    if len(offical_hint_string) == 0:
        target_symbol = u"個半形英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英數半形字"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

    if len(offical_hint_string) > 0:
        #print("offical_hint_string_anwser:", offical_hint_string_anwser)
        my_anwser_formated = convert_string_to_pattern(offical_hint_string_anwser)

    my_options = tmp_text
    if len(my_question) < len(tmp_text):
        my_options = my_options.replace(my_question,u"")
    my_options = my_options.replace(offical_hint_string,u"")
    #print("tmp_text:", tmp_text)
    #print("my_options:", my_options)
    #print("offical_hint_string:", offical_hint_string)

    # try rule7:
    # check is chinese/english in question, if match, apply my_options rule.
    if len(offical_hint_string) > 0:
        tmp_text_org = captcha_text_div_text
        if CONST_EXAMPLE_SYMBOL in tmp_text:
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

    return return_list

def format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    CONST_INPUT_SYMBOL = '輸入'

    tmp_text = captcha_text_div_text
    tmp_text = tmp_text.replace(u'  ',u' ')
    tmp_text = tmp_text.replace(u'：',u':')
    # for hint
    tmp_text = tmp_text.replace(u'*',u'*')

    # replace ex.
    tmp_text = tmp_text.replace(u'例如', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'如:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'舉例', CONST_EXAMPLE_SYMBOL)
    if not CONST_EXAMPLE_SYMBOL in tmp_text:
        tmp_text = tmp_text.replace(u'例', CONST_EXAMPLE_SYMBOL)
    # important, maybe 例 & ex occurs at same time.
    tmp_text = tmp_text.replace(u'ex:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'Ex:', CONST_EXAMPLE_SYMBOL)

    #若你覺得
    #PS:這個，可能會造成更多問題，呵呵。
    SYMBOL_IF_LIST = ['假設','如果','若']
    for symbol_if in SYMBOL_IF_LIST:
        if symbol_if in tmp_text and '答案' in tmp_text:
            tmp_text = tmp_text.replace('覺得', '')
            tmp_text = tmp_text.replace('認為', '')
            tmp_text = tmp_text.replace(symbol_if + '你答案', CONST_EXAMPLE_SYMBOL + '答案')
            tmp_text = tmp_text.replace(symbol_if + '答案', CONST_EXAMPLE_SYMBOL + '答案')

    tmp_text = tmp_text.replace(u'填入', CONST_INPUT_SYMBOL)

    #tmp_text = tmp_text.replace(u'[',u'(')
    #tmp_text = tmp_text.replace(u']',u')')
    tmp_text = tmp_text.replace(u'？',u'?')

    tmp_text = tmp_text.replace(u'（',u'(')
    tmp_text = tmp_text.replace(u'）',u')')

    return tmp_text

def get_answer_list_by_question(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    # guess answer list from multi-options: 【】() []
    if return_list is None:
        return_list = guess_answer_list_from_multi_options(tmp_text)
        pass

    if return_list is None:
        return_list = guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    # try rule8:
    if return_list is None:
        return_list = guess_answer_list_from_symbols(captcha_text_div_text)

    return return_list

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
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]

    if "/activity/detail/%s" % (game_name,) in url:
        # to support teamear
        entry_url = url.replace("/activity/detail/","/activity/game/")
        print("redirec to new url:", entry_url)
        try:
            driver.get(entry_url)
        except Exception as exec1:
            pass
        ret = True

    return ret

def tixcraft_date_auto_select(driver, url, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    # read config.
    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","No tickets available","空席なし"]

    game_name = ""

    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if show_debug_message:
        print('get date game_name:', game_name)
        print("date_auto_select_mode:", date_auto_select_mode)
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

    date_list = None
    if check_game_detail:
        try:
            date_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
        except Exception as exc:
            print("find #gameList fail")

    is_coming_soon = False
    coming_soon_condictions_list = ['開賣','剩餘','天','小時','分鐘','秒','0',':','/']
    
    button_list = None
    if date_list is not None:
        button_list = []
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

            if row_text is None:
                row_text = ""

            if len(row_text) > 0:
                is_match_all_coming_soon_condiction = True
                for condiction_string in coming_soon_condictions_list:
                    if not condiction_string in row_text:
                        is_match_all_coming_soon_condiction = False
                        break
                if is_match_all_coming_soon_condiction:
                    is_coming_soon = True
                    break

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
                        if show_debug_message:
                            print("check right part text:", row_text_right_part)
                        if sold_out_item in row_text_right_part:
                            is_match_keyword_row = False

                            if show_debug_message:
                                print("match sold out text: %s, skip this row." % (sold_out_item))

                            # no need check next language item.
                            break

            # step 3: add to list.
            if is_match_keyword_row:
                el = None
                try:
                    el = row.find_element(By.CSS_SELECTOR, '.btn-next')
                except Exception as exc:
                    if show_debug_message:
                        print("find .btn-next fail")
                    pass

                if el is not None:
                    button_list.append(el)
                    if date_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        # only need one row.
                        if show_debug_message:
                            print("match date row, only need first row, start to break")
                        break

    is_date_selected = False
    if button_list is not None:
        if len(button_list) > 0:
            # default first row.
            target_row_index = 0

            if date_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(button_list) - 1

            if date_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(button_list)-1)

            if show_debug_message:
                print("clicking row:", target_row_index+1)

            try:
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

    # [PS]: current reload condition only when 
    if auto_reload_coming_soon_page_enable:
        if is_coming_soon:
            # case 2: match one row is coming soon.
            try:
                driver.refresh()
            except Exception as exc:
                pass
        else:
            if not is_date_selected:
                # case 1: No hyperlink button.
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

    return is_date_selected

# PURPOSE: get target area list.
# RETURN:
#   is_need_refresh
#   matched_blocks
# PS: matched_blocks will be None, if length equals zero.
def get_tixcraft_target_area(el, area_keyword, area_auto_select_mode, pass_1_seat_remaining_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_need_refresh = False
    matched_blocks = None

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
                print("area list is empty, do refresh!")
                is_need_refresh = True
        else:
            print("area list is None, do refresh!")
            is_need_refresh = True

    if area_list_count > 0:
        matched_blocks = []
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

            if row_text is None:
                row_text = ""

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
                    if show_debug_message:
                        print("pass_1_seat_remaining_enable:", pass_1_seat_remaining_enable)
                    if pass_1_seat_remaining_enable:
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
                        print("only need first item, break area list loop.")
                        break
                    if show_debug_message:
                        print("row_text:" + row_text)
                        print("match:" + area_keyword)

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True

    return is_need_refresh, matched_blocks

# PS: auto refresh condition 1: no keyword + no hyperlink.
# PS: auto refresh condition 2: with keyword + no hyperlink.
def tixcraft_area_auto_select(driver, url, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    # read config.
    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
    area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
    area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]

    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    # disable pass 1 seat remaining when target ticket number is 1.
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False

    if show_debug_message:
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
            if show_debug_message:
                print("is_need_refresh for keyword1:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if show_debug_message:
                        print("use area keyword #2", area_keyword_2)

                    # only when keyword#2 filled to query.
                    if len(area_keyword_2) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_2, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if show_debug_message:
                            print("is_need_refresh for keyword2:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if show_debug_message:
                        print("use area keyword #3", area_keyword_3)

                    # only when keyword#3 filled to query.
                    if len(area_keyword_3) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_3, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if show_debug_message:
                            print("is_need_refresh for keyword3:", is_need_refresh)

            if is_need_refresh:
                if areas is None:
                    if show_debug_message:
                        print("use area keyword #4", area_keyword_4)

                    # only when keyword#4 filled to query.
                    if len(area_keyword_4) > 0 :
                        is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_4, area_auto_select_mode, pass_1_seat_remaining_enable)
                        if show_debug_message:
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
                    #print("area text:", area_target.text)
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

def tixcraft_ticket_agree(driver):
    click_plan = "A"
    #click_plan = "B"

    # check agree
    form_checkbox = None
    if click_plan == "A":
        try:
            form_checkbox = driver.find_element(By.ID, 'TicketForm_agree')
        except Exception as exc:
            print("find TicketForm_agree fail")

    is_finish_checkbox_click = False
    if form_checkbox is not None:
        try:
            # TODO: check the status: checked.
            if form_checkbox.is_enabled():
                form_checkbox.click()
                is_finish_checkbox_click = True
        except Exception as exc:
            print("click TicketForm_agree fail")
            pass

    # 使用 plan B.
    #if not is_finish_checkbox_click:
    # alway not use Plan B.
    if False:
        try:
            print("use plan_b to check TicketForm_agree.")
            driver.execute_script("$(\"input[type='checkbox']\").prop('checked', true);")
            #driver.execute_script("document.getElementById(\"TicketForm_agree\").checked;")
            is_finish_checkbox_click = True
        except Exception as exc:
            print("javascript check TicketForm_agree fail")
            print(exc)
            pass

    return is_finish_checkbox_click

def tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number):
    is_ticket_number_assigned = False
    if select_obj is not None:
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
        if select is not None:
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

def tixcraft_verify(driver, presale_code):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False

    inferred_answer_string = None
    if len(presale_code) > 0:
        inferred_answer_string = presale_code

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.zone-verify')
    except Exception as exc:
        print("find verify textbox fail")
        pass

    question_text = None
    if form_select is not None:
        try:
            question_text = form_select.text
        except Exception as exc:
            print("get text fail")

    html_text = ""
    if question_text is not None:
        if len(question_text) > 0:
            # format question text.
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

            if u'【' in html_text and u'】' in html_text:
                # PS: 這個太容易沖突，因為問題類型太多，不能直接使用。
                #inferred_answer_string = find_between(html_text, u"【", u"】")
                pass

    if show_debug_message:
        print("html_text:", html_text)

    is_options_in_question = False

    # 請輸入"YES"，代表您已詳閱且瞭解並同意。
    if inferred_answer_string is None:
        if u'輸入"YES"' in html_text:
            if u'已詳閱' in html_text or '請詳閱' in html_text:
                if u'同意' in html_text:
                    inferred_answer_string = 'YES'

    # 購票前請詳閱注意事項，並於驗證碼欄位輸入【同意】繼續購票流程。
    if inferred_answer_string is None:
        if '驗證碼' in html_text or '驗證欄位' in html_text:
            if '已詳閱' in html_text or '請詳閱' in html_text:
                if '輸入【同意】' in html_text:
                    inferred_answer_string = '同意'

    if show_debug_message:
        print("inferred_answer_string:", inferred_answer_string)


    form_input = None
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, '#checkCode')
    except Exception as exc:
        print("find verify code fail")
        pass

    default_value = None
    if form_input is not None:
        try:
            default_value = form_input.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

    if default_value is None:
        default_value = ""

    if not inferred_answer_string is None:
        is_password_sent = False
        if len(default_value)==0:
            try:
                # PS: sometime may send key twice...
                form_input.clear()
                form_input.send_keys(inferred_answer_string)
                is_password_sent = True
                if show_debug_message:
                    print("sent password by bot.")
            except Exception as exc:
                pass

        if default_value == inferred_answer_string:
            if show_debug_message:
                print("sent password by previous time.")
            is_password_sent = True

        if is_password_sent:
            submit_btn = None
            try:
                submit_btn = driver.find_element(By.ID, 'submitButton')
            except Exception as exc:
                if show_debug_message:
                    print("find submit button fail")
                    print(exc)
                pass

            is_submited = False
            if not submit_btn is None:
                for i in range(3):
                    try:
                        if submit_btn.is_enabled():
                            submit_btn.click()
                            is_submited = True
                            if show_debug_message:
                                print("press submit button at time #", i+1)
                    except Exception as exc:
                        pass

                    if is_submited:
                        break

            if is_submited:
                for i in range(3):
                    time.sleep(0.1)
                    alert_ret = check_pop_alert(driver)
                    if alert_ret:
                        if show_debug_message:
                            print("press accept button at time #", i+1)                    
                        break
    else:
        if len(default_value)==0:
            try:
                form_input.click()
            except Exception as exc:
                pass

    return ret

def tixcraft_manully_keyin_verify_code(driver, ocr_answer = ""):
    is_verifyCode_editing = False

    # manually keyin verify code.
    # start to input verify code.
    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.ID, 'TicketForm_verifyCode')
    except Exception as exc:
        print("find form_verifyCode fail")

    if form_verifyCode is not None:
        is_visible = False
        try:
            if form_verifyCode.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                form_verifyCode.click()
                if len(ocr_answer)==4:
                    #print("start to auto submit.")
                    form_verifyCode.send_keys(ocr_answer)
                    form_verifyCode.send_keys(Keys.ENTER)
                is_verifyCode_editing = True
            except Exception as exc:
                print("click form_verifyCode fail, tring to use javascript.")
                # plan B
                try:
                    driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").focus();")
                    is_verifyCode_editing = True
                except Exception as exc:
                    print("click form_verifyCode fail")
                    pass
                pass
    return is_verifyCode_editing

#PS: credit to LinShihJhang's share
def tixcraft_auto_ocr(driver, ocr):
    print("start to ddddocr")
    orc_answer = None
    if not ocr is None:
        try:
            form_verifyCode_base64 = driver.execute_async_script("""
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                var img = document.getElementById('yw0');
                canvas.height = img.naturalHeight;
                canvas.width = img.naturalWidth;
                context.drawImage(img, 0, 0);

                callback = arguments[arguments.length - 1];
                callback(canvas.toDataURL());
                """)
            img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            orc_answer = ocr.classification(img_base64)
        except Exception as exc:
            pass
    else:
        print("ddddocr is None")

    if not orc_answer is None:
        print("orc_answer:", orc_answer)
        if len(orc_answer)==4:
            tixcraft_manully_keyin_verify_code(driver, orc_answer)
        else:
            tixcraft_manully_keyin_verify_code(driver)
    else:
        tixcraft_manully_keyin_verify_code(driver)

def tixcraft_ticket_main(driver, config_dict, ocr):
    is_finish_checkbox_click = False
    auto_check_agree = config_dict["auto_check_agree"]
    
    ocr_captcha_enable = config_dict["ocr_captcha"]

    if auto_check_agree:
        tixcraft_ticket_agree(driver)

    # allow agree not enable to assign ticket number.
    form_select = None
    try:
        #form_select = driver.find_element(By.TAG_NAME, 'select')
        #PS: select box may appear many in the page with different price.
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
    except Exception as exc:
        print("find select fail")
        pass

    select_obj = None
    if form_select is not None:
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
            if len(row_text) > 0:
                if row_text != "0":
                    # ticket assign.
                    is_ticket_number_assigned = True

    is_verifyCode_editing = False

    # must wait select object ready to assign ticket number.
    if not is_ticket_number_assigned:
        # only this case:"ticket number changed by bot" to play sound!
        # PS: I assume each time assign ticket number will succufully changed, so let sound play first.
        check_and_play_sound_for_captcha(config_dict)

        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)

        # must wait ticket number assign to focus captcha.
        if is_ticket_number_assigned:
            if not ocr_captcha_enable:
                is_verifyCode_editing = tixcraft_manully_keyin_verify_code(driver)
            else:
                tixcraft_auto_ocr(driver, ocr)
                is_verifyCode_editing = True

    print("is_finish_checkbox_click:", is_finish_checkbox_click)

    if is_verifyCode_editing:
        print("goto is_verifyCode_editing == True")

    return is_verifyCode_editing

# PS: There are two "Next" button in kktix.
#   : 1: /events/xxx
#   : 2: /events/xxx/registrations/new
#   : This is ONLY for case-1, because case-2 lenght >5
def kktix_events_press_next_button(driver):
    ret = False

    # let javascript to enable button.
    time.sleep(0.1)

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

def kktix_input_captcha_text(captcha_password_input_tag, inferred_answer_string, force_overwrite = False):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    is_cpatcha_sent = False
    inputed_captcha_text = ""

    if not captcha_password_input_tag is None:
        if force_overwrite:
            try:
                captcha_password_input_tag.send_keys(inferred_answer_string)
                print("send captcha keys:" + inferred_answer_string)
                is_cpatcha_sent = True
                inputed_captcha_text = inferred_answer_string
            except Exception as exc:
                pass
        else:
            # not force overwrite:
            inputed_captcha_text = None
            try:
                inputed_captcha_text = captcha_password_input_tag.get_attribute('value')
            except Exception as exc:
                pass
            if inputed_captcha_text is None:
                inputed_captcha_text = ""

            if len(inputed_captcha_text) == 0:
                try:
                    captcha_password_input_tag.send_keys(inferred_answer_string)
                    print("send captcha keys:" + inferred_answer_string)
                    is_cpatcha_sent = True
                except Exception as exc:
                    pass

    return is_cpatcha_sent

def kktix_travel_price_list(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_keyword_1, kktix_area_keyword_1_and):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    areas = None
    is_ticket_number_assigned = False

    ticket_price_list = None
    try:
        ticket_price_list = driver.find_elements(By.CSS_SELECTOR, '.display-table-row')
    except Exception as exc:
        ticket_price_list = None
        print("find ticket-price span Exception:")
        print(exc)
        pass

    price_list_count = 0
    if ticket_price_list is not None:
        price_list_count = len(ticket_price_list)
        if show_debug_message:
            print("found price count:", price_list_count)
            print("start to travel rows..........")
    else:
        print("find ticket-price span fail")

    is_travel_interrupted = False

    if price_list_count > 0:
        areas = []

        # clean stop word.
        kktix_area_keyword_1 = format_keyword_string(kktix_area_keyword_1)
        kktix_area_keyword_1_and = format_keyword_string(kktix_area_keyword_1_and)

        if show_debug_message:
            print('kktix_area_keyword_1:', kktix_area_keyword_1)
            print('kktix_area_keyword_1_and:', kktix_area_keyword_1_and)

        row_index = 0
        for row in ticket_price_list:
            row_index += 1

            row_text = ""
            try:
                row_text = row.text
                if show_debug_message:
                    print("get text:", row_text, ",at row:", row_index)
            except Exception as exc:
                row_text = ""
                is_travel_interrupted = True
                print("get text fail.")

            if row_text is None:
                row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = format_keyword_string(row_text)

                # check ticket input textbox.
                ticket_price_input = None
                try:
                    ticket_price_input = row.find_element(By.CSS_SELECTOR, "input[type='text']")
                except Exception as exc:
                    pass

                if ticket_price_input is not None:
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

                    is_danger_notice = False
                    if ticket_number > 1:
                        # start to check danger notice.
                        span_danger_popup = None
                        try:
                            span_danger_popup = row.find_element(By.CSS_SELECTOR, "span.danger")
                            if span_danger_popup.is_displayed():
                                is_danger_notice = True
                        except Exception as exc:
                            pass

                        if is_danger_notice:
                            # skip this row, because assign will fail, or fill ticket number as 1.
                            if pass_1_seat_remaining_enable:
                                continue

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
                            areas.append(row)

            if is_travel_interrupted:
                # not sure to break or continue..., maybe break better.
                break
    else:
        if show_debug_message:
            print("no any price list found.")
        pass

    # unknow issue...
    if is_travel_interrupted:
        pass

    return is_ticket_number_assigned, areas

def kktix_assign_ticket_number(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_auto_select_mode, kktix_area_keyword_1, kktix_area_keyword_1_and):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ticket_number_str = str(ticket_number)

    is_ticket_number_assigned, areas = kktix_travel_price_list(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_keyword_1, kktix_area_keyword_1_and)

    target_area = None
    if not is_ticket_number_assigned:
        if areas is not None:
            if len(areas) > 0:
                target_row_index = 0

                if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if kktix_area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(areas)-1

                if kktix_area_auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(areas)-1)

                if show_debug_message:
                    print("target_row_index", target_row_index)
                target_area = areas[target_row_index]

    ticket_price_input = None
    if target_area is not None:
        if show_debug_message:
            print('try to get input box element.')
        try:
            #print("target_area text", target_area.text)
            ticket_price_input = target_area.find_element(By.CSS_SELECTOR, "input[type='text']")
        except Exception as exc:
            pass

    current_ticket_number = ""
    is_visible = False
    if ticket_price_input is not None:
        if show_debug_message:
            print("try to get input box value.")
        try:
            current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            is_visible = ticket_price_input.is_enabled()
        except Exception as exc:
            pass

    if is_visible and len(current_ticket_number) > 0:
        if current_ticket_number == "0":
            try:
                print("asssign ticket number:%s" % ticket_number_str)
                ticket_price_input.clear()
                ticket_price_input.send_keys(ticket_number_str)

                is_ticket_number_assigned = True
            except Exception as exc:
                print("asssign ticket number to ticket-price field Exception:")
                print(exc)
                try:
                    ticket_price_input.clear()
                    ticket_price_input.send_keys("1")
                    is_ticket_number_assigned = True
                except Exception as exc2:
                    pass
        else:
            if show_debug_message:
                print("value already assigned.")
            # already assigned.
            is_ticket_number_assigned = True

    return is_ticket_number_assigned

def kktix_get_web_datetime(registrationsNewApp_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

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
                el_web_datetime_text = None
                try:
                    el_web_datetime_text = el_web_datetime.text
                    if show_debug_message:
                        print("el_web_datetime_text:", el_web_datetime_text)
                except Exception as exc:
                    if show_debug_message:
                        print('parse web datetime fail:')
                        print(exc)
                    pass

                if el_web_datetime_text is not None:
                    if len(el_web_datetime_text) > 0:
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
    else:
        print("find td.ng-binding fail")

    return web_datetime

def kktix_check_agree_checkbox(driver):
    is_need_refresh = False
    is_finish_checkbox_click = False

    person_agree_terms_checkbox = None
    try:
        person_agree_terms_checkbox = driver.find_element(By.ID, 'person_agree_terms')
    except Exception as exc:
        print("find person_agree_terms checkbox Exception")
        pass

    if person_agree_terms_checkbox is not None:
        is_visible = False
        try:
            if person_agree_terms_checkbox.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            is_checkbox_checked = False
            try:
                if person_agree_terms_checkbox.is_selected():
                    is_checkbox_checked = True
            except Exception as exc:
                pass

            if not is_checkbox_checked:
                #print('send check to checkbox')
                try:
                    person_agree_terms_checkbox.click()
                    is_finish_checkbox_click = True
                except Exception as exc:
                    pass
            else:
                #print('checked')
                is_finish_checkbox_click = True
        else:
            is_need_refresh = True
    else:
        is_need_refresh = True

    if is_need_refresh:
        print("find person_agree_terms checkbox fail, do refresh page.")

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

def get_answer_string_from_web_date(CONST_EXAMPLE_SYMBOL, registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None

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
        web_datetime = kktix_get_web_datetime(registrationsNewApp_div)
        if not web_datetime is None:
            if show_debug_message:
                print("web_datetime:", web_datetime)

            captcha_text_formatted = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)
            if show_debug_message:
                print("captcha_text_formatted", captcha_text_formatted)

            my_datetime_foramted = None

            # MMDD
            if my_datetime_foramted is None:
                if u'4位半形' in captcha_text_formatted:
                    my_datetime_foramted = "%m%d"

            # for "如為2月30日，請輸入0230"
            if my_datetime_foramted is None:
                if CONST_EXAMPLE_SYMBOL in captcha_text_formatted:
                    right_part = captcha_text_formatted.split(CONST_EXAMPLE_SYMBOL)[1]
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
                        my_delimitor_symbol = CONST_EXAMPLE_SYMBOL
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
                inferred_answer_string = ans
                if show_debug_message:
                    print("my_anwser:", ans)

    return inferred_answer_string

def get_answer_string_from_web_time(CONST_EXAMPLE_SYMBOL, registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    inferred_answer_string = None

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
        web_datetime = None
        if not registrationsNewApp_div is None:
            web_datetime = kktix_get_web_datetime(registrationsNewApp_div)
        if not web_datetime is None:
            tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

            my_datetime_foramted = None

            if my_datetime_foramted is None:
                my_hint_anwser = tmp_text

                my_delimitor_symbol = CONST_EXAMPLE_SYMBOL
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
                inferred_answer_string = ans
                #print(u"my_anwser:", ans)

    return inferred_answer_string

def check_answer_keep_symbol(captcha_text_div_text):
    is_need_keep_symbol = False

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

    return is_need_keep_symbol

def get_answer_list_from_question_string(registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None
    answer_list = None
    is_need_keep_symbol = check_answer_keep_symbol(captcha_text_div_text)

    CONST_EXAMPLE_SYMBOL = "範例"

    # 請在下方空白處輸入引號內文字：
    if inferred_answer_string is None:
        is_use_quota_message = False
        if u"「" in captcha_text_div_text and u"」" in captcha_text_div_text:
            if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
            if u'半形' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
        #print("is_use_quota_message:" , is_use_quota_message)
        if is_use_quota_message:
            inferred_answer_string = find_between(captcha_text_div_text, u"「", u"」")
            #print("find captcha text:" , inferred_answer_string)

    if inferred_answer_string is None:
        is_use_quota_message = False
        if u"【" in captcha_text_div_text and u"】" in captcha_text_div_text:
            if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
            if u'半形' in captcha_text_div_text and u'輸入' in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
        #print("is_use_quota_message:" , is_use_quota_message)
        if is_use_quota_message:
            inferred_answer_string = find_between(captcha_text_div_text, u"【", u"】")
            #print("find captcha text:" , inferred_answer_string)

    # parse '演出日期'
    if inferred_answer_string is None:
        inferred_answer_string = get_answer_string_from_web_date(CONST_EXAMPLE_SYMBOL, registrationsNewApp_div, captcha_text_div_text)

    # parse '演出時間'
    if inferred_answer_string is None:
        inferred_answer_string = get_answer_string_from_web_time(CONST_EXAMPLE_SYMBOL, registrationsNewApp_div, captcha_text_div_text)

    # name of event.
    if inferred_answer_string is None:
        if u"name of event" in captcha_text_div_text:
            if u'(' in captcha_text_div_text and u')' in captcha_text_div_text and u'ans:' in captcha_text_div_text.lower():
                target_symbol = u"("
                star_index = captcha_text_div_text.find(target_symbol)
                target_symbol = u":"
                star_index = captcha_text_div_text.find(target_symbol, star_index)
                target_symbol = u")"
                end_index = captcha_text_div_text.find(target_symbol, star_index)
                inferred_answer_string = captcha_text_div_text[star_index+1:end_index]
                #print("inferred_answer_string:", inferred_answer_string)

    # 二題式，組合問題。
    is_combine_two_question = False
    if u"第一題" in captcha_text_div_text and u"第二題" in captcha_text_div_text:
        is_combine_two_question = True
    if u"Q1." in captcha_text_div_text and u"Q2." in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if u"Q1:" in captcha_text_div_text and u"Q2:" in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if u"Q1 " in captcha_text_div_text and u"Q2 " in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if is_combine_two_question:
        inferred_answer_string = None
    #print("is_combine_two_question:", is_combine_two_question)


    # still no answer.
    if inferred_answer_string is None:
        if not is_combine_two_question:
            answer_list = get_answer_list_by_question(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)
            if show_debug_message:
                print("guess answer list:", answer_list)
        else:
            if show_debug_message:
                print("skip to guess answer because of combine question...")

    else:
        if show_debug_message:
            print("got an inferred_answer_string:", inferred_answer_string)


    return inferred_answer_string, answer_list

def kktix_reg_new_captcha(registrationsNewApp_div, captcha_inner_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    captcha_text_div = None
    try:
        captcha_text_div = captcha_inner_div.find_element(By.TAG_NAME, "p")
    except Exception as exc:
        pass
        print("find p tag(captcha_text_div) fail")
        print(exc)

    captcha_text_div_text = None
    if captcha_text_div is not None:
        try:
            captcha_text_div_text = captcha_text_div.text
        except Exception as exc:
            pass

    # try to auto answer options.
    answer_list = None
    inferred_answer_string = None

    if not captcha_text_div_text is None:
        if show_debug_message:
            print("captcha_text_div_text:", captcha_text_div_text)
        inferred_answer_string, answer_list = get_answer_list_from_question_string(registrationsNewApp_div, captcha_text_div_text)

    return inferred_answer_string, answer_list

def kktix_double_check_all_text_value(driver, ticket_number_str):
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

    if ticket_price_input_list is not None:
        #print("bingo, found one of ticket number textbox.")
        row_index = 0
        for ticket_price_input in ticket_price_input_list:
            row_index += 1
            current_ticket_number = ""
            try:
                current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            except Exception as exc:
                pass
            if current_ticket_number is None:
                current_ticket_number = ""
            if len(current_ticket_number) > 0:
                #print(row_index, "current_ticket_number:", current_ticket_number)
                if current_ticket_number == ticket_number_str:
                    #print("bingo, match target ticket number.")

                    # ONLY, this case to auto press next button.
                    is_do_press_next_button = True
                    break

    return is_do_press_next_button

def kktix_reg_new_main(driver, answer_index, is_finish_checkbox_click, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    # part 1: check div.
    registrationsNewApp_div = None
    try:
        registrationsNewApp_div = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp')
    except Exception as exc:
        pass
        #print("find input fail:", exc)

    # part 2: assign ticket number
    ticket_number_str = str(config_dict["ticket_number"])

    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    # disable pass 1 seat remaining when target ticket number is 1.
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False

    is_ticket_number_assigned = False
    if not registrationsNewApp_div is None:
        kktix_area_auto_select_mode = config_dict["kktix"]["area_mode"]
        kktix_area_keyword_1 = config_dict["kktix"]["area_keyword_1"].strip()
        kktix_area_keyword_1_and = config_dict["kktix"]["area_keyword_1_and"].strip()
        kktix_area_keyword_2 = config_dict["kktix"]["area_keyword_2"].strip()
        kktix_area_keyword_2_and = config_dict["kktix"]["area_keyword_2_and"].strip()

        for retry_index in range(2):
            is_ticket_number_assigned = kktix_assign_ticket_number(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_auto_select_mode, kktix_area_keyword_1, kktix_area_keyword_1_and)
            if not is_ticket_number_assigned:
                is_ticket_number_assigned = kktix_assign_ticket_number(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_auto_select_mode, kktix_area_keyword_1, kktix_area_keyword_1_and)
                #PS: keyword_2 not input, means all rows are match.
                if not is_ticket_number_assigned:
                    is_ticket_number_assigned = kktix_assign_ticket_number(driver, ticket_number, pass_1_seat_remaining_enable, kktix_area_auto_select_mode, kktix_area_keyword_2, kktix_area_keyword_2_and)
            if is_ticket_number_assigned:
                break
    #print('is_ticket_number_assigned:', is_ticket_number_assigned)

    # part 3: captcha
    is_captcha_appear = False
    is_captcha_appear_and_filled_password = False
    answer_list = None

    # TODO: in guess options mode, no need to travel div again.
    captcha_inner_div = None

    if is_ticket_number_assigned:
        try:
            captcha_inner_div = driver.find_element(By.CSS_SELECTOR, '.custom-captcha-inner')
        except Exception as exc:
            pass

    captcha_password_input_tag = None
    if not captcha_inner_div is None:
        try:
            captcha_password_input_tag = captcha_inner_div.find_element(By.TAG_NAME, "input")
            if show_debug_message:
                print("found captcha input field")
        except Exception as exc:
            pass

    if not captcha_password_input_tag is None:
        inferred_answer_string = None
        if captcha_inner_div is not None:
            is_captcha_appear = True
            if show_debug_message:
                print("found captcha_inner_div layor.")

            auto_guess_options = config_dict["kktix"]["auto_guess_options"]
            user_guess_string = config_dict["kktix"]["user_guess_string"]

            if len(user_guess_string) > 0:
                inferred_answer_string = user_guess_string
            else:
                if auto_guess_options:
                    inferred_answer_string, answer_list = kktix_reg_new_captcha(registrationsNewApp_div, captcha_inner_div)

            if inferred_answer_string is not None:
                # password is not None, try to send.
                is_cpatcha_sent = kktix_input_captcha_text(captcha_password_input_tag, inferred_answer_string)
                if is_cpatcha_sent:
                    is_captcha_appear_and_filled_password = True
            else:
                is_try_to_focus = False
                if answer_list is None:
                    is_try_to_focus = True
                else:
                    if len(answer_list)==0:
                        is_try_to_focus = True

                if is_try_to_focus:
                    # password is None, focus to input, and play sound.
                    inputed_captcha_text = None
                    try:
                        inputed_captcha_text = captcha_password_input_tag.get_attribute('value')
                    except Exception as exc:
                        pass
                    if inputed_captcha_text is None:
                        inputed_captcha_text = ""
                    if len(inputed_captcha_text) == 0:
                        try:
                            #print("focus() captcha to input.")
                            check_and_play_sound_for_captcha(config_dict)
                            captcha_password_input_tag.click()
                            time.sleep(1)
                            # let user to input answer, bot sleep 1 second.
                        except Exception as exc:
                            pass

        if show_debug_message:
            print("is_captcha_appear:", is_captcha_appear)
            print("is_captcha_appear_and_filled_password:", is_captcha_appear_and_filled_password)

    # retry check agree checkbox again.
    if not is_finish_checkbox_click:
        auto_check_agree = config_dict["auto_check_agree"]
        if auto_check_agree:
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)

    is_do_press_next_button = False
    if is_ticket_number_assigned:
        auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
        if auto_press_next_step_button:
            if is_finish_checkbox_click:
                is_do_press_next_button = kktix_double_check_all_text_value(driver, ticket_number_str)
            else:
                print("still unable to assign checkbox as selected.")

    if show_debug_message:
        print("is_do_press_next_button:", is_do_press_next_button)

    if is_do_press_next_button:
        if not is_captcha_appear:
            click_ret = kktix_press_next_button(driver)
        else:
            if is_captcha_appear_and_filled_password:
                # for easy guest mode, we can fill the password correct.
                #print("for easy guest mode, we can fill the password correct.")
                click_ret = kktix_press_next_button(driver)
            else:
                # not is easy guest mode.
                #print("# not is easy guest mode.")

                # merge with password dictionary, so need remove duplicate list
                # PS: now, there are no password dictionary.
                if not answer_list is None:
                    if len(answer_list) > 1:
                        unique = [x for i, x in enumerate(answer_list) if answer_list.index(x) == i]
                        answer_list = unique

                # start to try answers.
                if not answer_list is None:
                    # for popular event
                    if len(answer_list) > 0:
                        if answer_index < len(answer_list)-1:
                            if kktix_captcha_text_value(captcha_inner_div) == "":
                                answer_index += 1
                                answer_string = answer_list[answer_index]

                                if len(answer_string) > 0:
                                    print("send answer:" + answer_string)
                                    is_cpatcha_sent = kktix_input_captcha_text(captcha_password_input_tag, answer_string)
                                    if is_cpatcha_sent:
                                        kktix_press_next_button(driver)
                        else:
                            # exceed index, do nothing.
                            pass
                else:
                    # captcha appeared, but we don't have answer list.
                    pass


    return answer_index

def kktix_reg_new(driver, url, answer_index, kktix_register_status_last, config_dict):
    registerStatus = kktix_register_status_last

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

    auto_check_agree = config_dict["auto_check_agree"]
    if auto_check_agree:
        if not is_need_refresh:
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)
        if not is_need_refresh:
            if not is_finish_checkbox_click:
                # retry again.
                is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver)
    #print('check agree_terms_checkbox, is_need_refresh:',is_need_refresh)

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
        # check is able to buy.
        auto_fill_ticket_number = config_dict["kktix"]["auto_fill_ticket_number"]
        if auto_fill_ticket_number:
            answer_index = kktix_reg_new_main(driver, answer_index, is_finish_checkbox_click, config_dict)

    return answer_index, registerStatus


# PURPOSE: get target area list.
# PS: this is main block, use keyword to get rows.
# PS: it seems use date_auto_select_mode instead of area_auto_select_mode
def get_fami_target_area(driver, date_keyword, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    date_keyword = format_keyword_string(date_keyword)
    area_keyword_1 = format_keyword_string(area_keyword_1)
    area_keyword_2 = format_keyword_string(area_keyword_2)
    area_keyword_3 = format_keyword_string(area_keyword_3)
    area_keyword_4 = format_keyword_string(area_keyword_4)

    if show_debug_message:
        print("try to find area block by keywords...")

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
    if area_list is not None:
        area_list_length = len(area_list)
        if show_debug_message:
            print("lenth of area rows:", area_list_length)

        if area_list_length > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if el_btn is not None:
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

            if len(date_keyword)==0 and len(area_keyword_1)==0 and len(area_keyword_2) == 0:
                # select all.
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #print("row index:", row_index)

                    date_html_text = ""
                    area_html_text = ""

                    row_text = ""
                    try:
                        my_css_selector = "td:nth-child(1)"
                        td_date = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_date is not None:
                            #print("date:", td_date.text)
                            date_html_text = format_keyword_string(td_date.text)

                        my_css_selector = "td:nth-child(2)"
                        td_area = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_area is not None:
                            #print("area:", td_area.text)
                            area_html_text = format_keyword_string(td_area.text)

                        row_text = row.text
                    except Exception as exc:
                        print("get row text fail")
                        break

                    if row_text is None:
                        row_text = ""

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
                            matched_blocks.append(row)

                            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                print("only need first item, break area list loop.")
                                break


    return_row_count = 0
    if not matched_blocks is None:
        return_row_count = len(matched_blocks)
        if return_row_count==0:
            matched_blocks = None

    if show_debug_message:
        print("return_row_count:", return_row_count)

    return matched_blocks


def fami_activity(driver):
    #print("fami_activity bingo")

    #---------------------------
    # part 1: press "buy" button.
    #---------------------------
    fami_start_to_buy_button = None
    try:
        fami_start_to_buy_button = driver.find_element(By.ID, 'buyWaiting')
    except Exception as exc:
        pass

    is_visible = False
    if fami_start_to_buy_button is not None:
        try:
            if fami_start_to_buy_button.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    if is_visible:
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


def fami_home(driver, url, config_dict):
    #print("fami_home bingo")

    is_ticket_number_assigned = False

    ticket_number = str(config_dict["ticket_number"])
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
    area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
    area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()

    #---------------------------
    # part 3: fill ticket number.
    #---------------------------
    ticket_el = None
    try:
        my_css_selector = "tr.ticket > td > select"
        ticket_el = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass
        print("click buyWaiting button fail")
        #print(exc)

    is_select_box_visible = False
    if ticket_el is not None:
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

        if ticket_number_select is not None:
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
        areas = get_fami_target_area(driver, date_keyword, area_keyword_1, area_keyword_2, area_keyword_3, area_keyword_4, area_auto_select_mode)

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
            el_btn = None
            is_visible = False
            try:
                my_css_selector = "button"
                el_btn = area_target.find_element(By.TAG_NAME, my_css_selector)
                if el_btn is not None:
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


# purpose: date auto select
def urbtix_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

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

    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "div.buy-icon"
                    el_btn = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if el_btn is not None:
                        button_class_string = str(el_btn.get_attribute('class'))
                        if len(button_class_string) > 1:
                            if 'disabled' in button_class_string:
                                if show_debug_message:
                                    print("found disabled activity at row:", row_index)
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

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "div.buy-icon"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass
        if el_btn is not None:
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

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    is_date_assign_by_bot = urbtix_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    return is_date_assign_by_bot

# purpose: area auto select
def urbtix_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    is_need_refresh = False

    matched_blocks = None

    # clean stop word.
    area_keyword_1 = format_keyword_string(area_keyword_1)
    area_keyword_1_and = format_keyword_string(area_keyword_1_and)

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.area-info"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    button_class_string = str(row.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            row_is_enabled=False
                        if 'selected' in button_class_string:
                            # someone is selected. skip this process.
                            row_is_enabled=False
                            matched_blocks = []
                            ret = True
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

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            if len(area_keyword_1) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", area_keyword_1)
                    print("keyword and:", area_keyword_1_and)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1

                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if area_keyword_1 in row_text:
                                if len(area_keyword_1_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if area_keyword_1_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            is_need_refresh = True
            if show_debug_message:
                print("formated_area_list is empty.")

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                ret = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                ret = True
            except Exception as exc:
                pass

    return is_need_refresh, ret


def urbtix_ticket_number_auto_select(driver, ticket_number):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    is_ticket_number_assigned = False
    ticket_number_str = str(ticket_number)

    # check ticket input textbox.
    ticket_price_input = None
    try:
        ticket_price_input = driver.find_element(By.CSS_SELECTOR, "input.ticket-count")
    except Exception as exc:
        pass

    if ticket_price_input is not None:
        current_ticket_number = ""
        is_visible = False

        try:
            current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            is_visible = ticket_price_input.is_enabled()
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
                    print("asssign ticket number to ticket-price field Exception:")
                    print(exc)
                    try:
                        ticket_price_input.clear()
                        ticket_price_input.send_keys("1")
                        is_ticket_number_assigned = True
                    except Exception as exc2:
                        pass
            else:
                # already assigned.
                is_ticket_number_assigned = True


    if is_ticket_number_assigned:
        el_btn = None
        try:
            my_css_selector = "div.footer > div > div"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if el_btn is not None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("varify site icon pressed.")
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
        else:
            if show_debug_message:
                print("varify site icon is None.")

    if is_ticket_number_assigned:
        el_btn = None
        try:
            my_css_selector = "div.button-inner > div > div.button-text"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if el_btn is not None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("shopping-cart icon pressed.")
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
        else:
            if show_debug_message:
                print("shopping-cart site icon is None.")

    return is_ticket_number_assigned


def urbtix_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
        area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
        area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
        area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
        area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()
        area_keyword_1_and = ""
        area_keyword_2_and = ""

        if show_debug_message:
            print("area_keyword_1:", area_keyword_1)
            #print("area_keyword_1_and:", area_keyword_1_and)
            print("area_keyword_2:", area_keyword_2)
            #print("area_keyword_2_and:", area_keyword_2_and)
        is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                # try keyword_2
                if len(area_keyword_2) > 0:
                    is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, area_auto_select_mode, area_keyword_2, area_keyword_2_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_3) > 0:
                    is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, area_auto_select_mode, area_keyword_3, "")

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_4) > 0:
                    is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, area_auto_select_mode, area_keyword_4, "")

        # un-tested. disable refresh for now.
        is_need_refresh = False
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # choose ticket.
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = urbtix_ticket_number_auto_select(driver, ticket_number)

        if show_debug_message:
            print("ticket_number:", ticket_number)
            print("is_ticket_number_assigned:", is_ticket_number_assigned)


    return ret


# purpose: date auto select
def cityline_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "button.date-time-position"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
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

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
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
                        time.sleep(0.5)
                    except Exception as exc:
                        pass

    return ret

# purpose: area auto select
# return:
#   True: area block appear.
#   False: area block not appear.
# ps: return is successfully click on the price radio.
def cityline_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    is_need_refresh = False

    matched_blocks = None

    # clean stop word.
    area_keyword_1 = format_keyword_string(area_keyword_1)
    area_keyword_1_and = format_keyword_string(area_keyword_1_and)

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = ".form-check"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    my_css_selector = "span.price-limited > span"
                    span_price_limited = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if not span_price_limited is None:
                        #print("found span limited at idx:", row_index)
                        span_i18n_string = str(span_price_limited.get_attribute('data-i18n'))
                        if len(span_i18n_string) > 1:
                            if 'soldout' in span_i18n_string:
                                #print("found span limited soldout at idx:", row_index)
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

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            if len(area_keyword_1) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", area_keyword_1)
                    print("keyword and:", area_keyword_1_and)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if area_keyword_1 in row_text:
                                if len(area_keyword_1_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if area_keyword_1_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)
                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            is_need_refresh = True
            if show_debug_message:
                print("formated_area_list is empty.")

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "input[type=radio]"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            if el_btn is not None:
                if el_btn.is_enabled():
                    if not el_btn.is_selected():
                        el_btn.click()
                        ret = True
                    else:
                        ret = True
                    #print("bingo, click target_area radio")
        except Exception as exc:
            print("click target_area radio a link fail")
            print(exc)
            pass

    return is_need_refresh, ret

#[TODO]:
# double check selected radio matched by keyword/keyword_and.
def cityline_area_selected_text(driver):
    ret = False

    return ret

def cityline_ticket_number_auto_select(driver, ticket_number):
    selector_string = 'select.select-num'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, ticket_number, by_method, selector_string)

def ibon_ticket_number_auto_select(driver, ticket_number):
    selector_string = 'table.table > tbody > tr > td > select'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, ticket_number, by_method, selector_string)

def assign_ticket_number_by_select(driver, ticket_number, by_method, selector_string):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    form_select = None
    try:
        form_select = driver.find_element(by_method, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find ticket_number select fail")
            print(exc)
        pass

    select_obj = None
    if form_select is not None:
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
            is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)
        else:
            if show_debug_message:
                print("ticket_number assigned by previous action.")

    return is_ticket_number_assigned

def cityline_purchase_button_press(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    is_date_assign_by_bot = cityline_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, 'button.purchase-btn')
    except Exception as exc:
        print("find next button fail")
        #print(exc)
        pass

    if el_btn is not None:
        print("bingo, found next button")
        try:
            if el_btn.is_enabled():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("press next button fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass

    return ret


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

    if el_btn is not None and el_nav is not None:
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

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
        area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
        area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
        area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
        area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()
        area_keyword_1_and = ""
        area_keyword_2_and = ""

        if show_debug_message:
            print("area_keyword_1:", area_keyword_1)
            #print("area_keyword_1_and:", area_keyword_1_and)
            print("area_keyword_2:", area_keyword_2)
                #print("area_keyword_2_and:", area_keyword_2_and)
            
        # PS: cityline price default value is selected at the first option.
        is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                # try keyword_2
                if len(area_keyword_2) > 0:
                    is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, area_auto_select_mode, area_keyword_2, area_keyword_2_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_3) > 0:
                    is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, area_auto_select_mode, area_keyword_3, "")

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_4) > 0:
                    is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, area_auto_select_mode, area_keyword_4, "")

        # un-tested. disable refresh for now.
        is_need_refresh = False
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # choose ticket.
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = cityline_ticket_number_auto_select(driver, ticket_number)

        if show_debug_message:
            print("ticket_number:", ticket_number)
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

def ibon_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.grid-wrap.event.table-wrap > div > div > div.tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if el_btn is not None:
                        if not el_btn.is_enabled():
                            #print("row's button disabled!")
                            row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        el_btn = None
        try:
            my_css_selector = "button.btn"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if el_btn is not None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("buy icon pressed.")
                    ret = True
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
    else:
        # no target to click.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.5)
                    except Exception as exc:
                        pass
    return ret

def ibon_activity_info(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)
    is_date_assign_by_bot = ibon_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    return is_date_assign_by_bot

def ibon_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    is_need_refresh = False

    matched_blocks = None

    # clean stop word.
    area_keyword_1 = format_keyword_string(area_keyword_1)
    area_keyword_1_and = format_keyword_string(area_keyword_1_and)

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.col-md-5 > table > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    button_class_string = str(row.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            row_is_enabled=False
                        if 'sold-out' in button_class_string:
                            row_is_enabled=False
                        if 'selected' in button_class_string:
                            # someone is selected. skip this process.
                            row_is_enabled=False
                            matched_blocks = []
                            ret = True
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

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            if len(area_keyword_1) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", area_keyword_1)
                    print("keyword and:", area_keyword_1_and)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if area_keyword_1 in row_text:
                                if len(area_keyword_1_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if area_keyword_1_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            is_need_refresh = True
            if show_debug_message:
                print("formated_area_list is empty.")

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                ret = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                ret = True
            except Exception as exc:
                pass

    return is_need_refresh, ret


def ibon_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
        area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
        area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
        area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
        area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()
        area_keyword_1_and = ""
        area_keyword_2_and = ""

        if show_debug_message:
            print("area_keyword_1:", area_keyword_1)
            #print("area_keyword_1_and:", area_keyword_1_and)
            print("area_keyword_2:", area_keyword_2)
            #print("area_keyword_2_and:", area_keyword_2_and)

        is_need_refresh = False
        if not is_price_assign_by_bot:
            is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, area_auto_select_mode, area_keyword_1, area_keyword_1_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                # try keyword_2
                if len(area_keyword_2) > 0:
                    is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, area_auto_select_mode, area_keyword_2, area_keyword_2_and)

        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_3) > 0:
                    is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, area_auto_select_mode, area_keyword_3, "")
        if not is_need_refresh:
            if not is_price_assign_by_bot:
                if len(area_keyword_4) > 0:
                    is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, area_auto_select_mode, area_keyword_4, "")

        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

    return is_price_assign_by_bot

def ibon_purchase_button_press(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '#ticket-wrap > a.btn')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if el_btn is not None:
        print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled():
                el_btn.click()
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

def facebook_login(driver, account):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#email')
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#pass')
        except Exception as exc:
            pass

    is_visible = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    if is_visible:
        try:
            el_pass.click()
        except Exception as exc:
            pass

    return ret

def kktix_login(driver, account):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#user_login')
    except Exception as exc:
        #print("find #email fail")
        #print(exc)
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#user_password')
        except Exception as exc:
            pass

    is_visible = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    if is_visible:
        try:
            el_pass.click()
        except Exception as exc:
            pass

    return ret

def check_and_play_sound_for_captcha(config_dict):
    play_captcha_sound = config_dict["advanced"]["play_captcha_sound"]["enable"]
    captcha_sound_filename = config_dict["advanced"]["play_captcha_sound"]["filename"].strip()
    if play_captcha_sound:
        app_root = get_app_root()
        captcha_sound_filename = os.path.join(app_root, captcha_sound_filename)
        play_mp3_async(captcha_sound_filename)

def play_mp3_async(sound_filename):
    import threading
    threading.Thread(target=play_mp3, args=(sound_filename,), daemon=True).start()

def play_mp3(sound_filename):
    from playsound import playsound
    try:
        playsound(sound_filename)
    except Exception as exc:
        msg=str(exc)
        print("play sound exeption:", msg)
        if platform.system() == 'Windows':
            import winsound
            try:
                winsound.PlaySound(sound_filename, winsound.SND_FILENAME)
            except Exception as exc2:
                pass

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
                alert = driver.switch_to.alert
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
            logger.error('Exception2 for alert')
            logger.error(exc, exc_info=True)

    return is_alert_popup

def list_all_cookies(driver):
    all_cookies=driver.get_cookies();
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
    print(cookies_dict)

def tixcraft_main(driver, url, config_dict, is_verifyCode_editing, ocr):
    if url == 'https://tixcraft.com/':
        tixcraft_home(driver)

    if url == 'https://indievox.com/':
        tixcraft_home(driver)

    if "/activity/detail/" in url:
        is_redirected = tixcraft_redirect(driver, url)

    is_date_selected = False
    if "/activity/game/" in url:
        date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
        if date_auto_select_enable:
            is_date_selected = tixcraft_date_auto_select(driver, url, config_dict)

    # choose area
    if '/ticket/area/' in url:
        area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
        if area_auto_select_enable:
            tixcraft_area_auto_select(driver, url, config_dict)

    if '/ticket/verify/' in url:
        presale_code = config_dict["tixcraft"]["presale_code"]
        tixcraft_verify(driver, presale_code)

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        if not is_verifyCode_editing:
            is_verifyCode_editing = tixcraft_ticket_main(driver, config_dict, ocr)
    else:
        is_verifyCode_editing = False

    return is_verifyCode_editing

def kktix_main(driver, url, config_dict, answer_index, kktix_register_status_last):
    auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
    kktix_account = config_dict["advanced"]["kktix_account"]

    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        if len(kktix_account) > 4:
            kktix_login(driver, kktix_account)
        is_url_contain_sign_in = True

    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            answer_index, kktix_register_status_last = kktix_reg_new(driver, url, answer_index, kktix_register_status_last, config_dict)
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
    return answer_index, kktix_register_status_last

def famiticket_main(driver, url, config_dict):
    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except Exception as excSwithFail:
        pass

    if '/Home/Activity/Info/' in url:
        fami_activity(driver)
    if '/Sales/Home/Index/' in url:
        fami_home(driver, url, config_dict)

def urbtix_main(driver, url, config_dict):
    # http://msg.urbtix.hk
    waiting_for_access_url = ['/session/landing-timer/','msg.urbtix.hk','busy.urbtix.hk']
    for waiting_url in waiting_for_access_url:
        if waiting_url in url:
            # delay to avoid ip block.
            time.sleep(1.0)
            try:
                driver.get('https://www.urbtix.hk/')
            except Exception as exec1:
                pass
            pass

    if '/logout?' in url:
        try:
            driver.get('https://www.urbtix.hk/')
        except Exception as exec1:
            pass
        pass

    # https://www.urbtix.hk/event-detail/00000/
    if '/event-detail/' in url:
        date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
        if date_auto_select_enable:
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
        area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
        if area_auto_select_enable:
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

    if el_div is not None:
        #print("bingo, found modal-dialog")
        try:
            if el_div.is_enabled():
                if el_div.is_displayed():
                    ret = True
        except Exception as exc:
            pass

    return ret

def cityline_main(driver, url, config_dict):
    # https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2F
    # ignore url redirect
    if '/Login.html' in url:
        return

    # https://msg.cityline.com/
    if 'msg.cityline.com' in url:
        try:
            driver.execute_script("goEvent();")
        except Exception as exec1:
            pass
        pass

    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except Exception as excSwithFail:
        pass

    if '/eventDetail?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
            if date_auto_select_enable:
                cityline_purchase_button_press(driver, config_dict)

    if '/performance?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
            if area_auto_select_enable:
                cityline_performance(driver, config_dict)

def ibon_main(driver, url, config_dict):
    #https://ticket.ibon.com.tw/ActivityInfo/Details/0000?pattern=entertainment
    if '/ActivityInfo/Details/' in url:
        is_event_page = False
        if len(url.split('/'))<=6:
            is_event_page = True

        if is_event_page:
            date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
            if date_auto_select_enable:
                ibon_activity_info(driver, config_dict)

    # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=0000
    if '/application/UTK02/' in url and '.aspx?PERFORMANCE_ID=' in url:
        is_event_page = False
        if len(url.split('/'))<=6:
            is_event_page = True

        if is_event_page:
            area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
            if area_auto_select_enable:
                if 'PERFORMANCE_PRICE_AREA_ID=' in url:
                    # step 2: assign ticket number.
                    ticket_number = str(config_dict["ticket_number"])
                    is_ticket_number_assigned = ibon_ticket_number_auto_select(driver, ticket_number)
                    if is_ticket_number_assigned:
                        click_ret = ibon_purchase_button_press(driver)
                else:
                    # step 1: select area.
                    ibon_performance(driver, config_dict)

def main():
    config_dict = get_config_dict()

    driver_type = 'selenium'
    #driver_type = 'stealth'
    driver_type = 'undetected_chromedriver'

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict, driver_type)
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    # for tixcraft
    is_verifyCode_editing = False

    # for kktix
    answer_index = -1
    kktix_register_status_last = None

    DISCONNECTED_MSG = 'Unable to evaluate script: no such window: target window already closed'

    debugMode = False
    if 'debug' in config_dict:
        debugMode = config_dict["debug"]
    if debugMode:
        print("Start to looping, detect browser url...")

    ocr = None
    try:
        if config_dict["ocr_captcha"]:
            ocr = ddddocr.DdddOcr()
    except Exception as exc:
        pass

    while True:
        time.sleep(0.1)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        #is_alert_popup = check_pop_alert(driver)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
        try:
            url = driver.current_url
        except NoSuchWindowException:
            print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            #print("get_log:", driver.get_log('driver'))
            if DISCONNECTED_MSG in driver.get_log('driver')[-1]['message']:
                print('quit bot by NoSuchWindowException')
                driver.quit()
                sys.exit()
                break
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count > 1:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass
        except UnexpectedAlertPresentException as exc1:
            # PS: DON'T remove this line.
            is_verifyCode_editing = False
            print('UnexpectedAlertPresentException at this url:', url )
            #time.sleep(3.5)
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
            is_verifyCode_editing = False

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
            , u'without establishing a connection'
            , u'web view not found'
            ]
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
                        print('quit bot by error:', each_error_string)
                        driver.quit()
                        sys.exit()
                        break

            # not is above case, print exception.
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

        # for Max's manuall test.
        if '/Downloads/varify.html' in url:
            tixcraft_verify(driver, "")

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if tixcraft_family:
            is_verifyCode_editing = tixcraft_main(driver, url, config_dict, is_verifyCode_editing, ocr)

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            answer_index, kktix_register_status_last = kktix_main(driver, url, config_dict, answer_index, kktix_register_status_last)

        # for famiticket
        if 'famiticket.com' in url:
            famiticket_main(driver, url, config_dict)

        # for urbtix
        # https://ticket.urbtix.hk/internet/secure/event/37348/performanceDetail
        if 'urbtix.hk' in url:
            urbtix_main(driver, url, config_dict)

        if 'cityline.com' in url:
            cityline_main(driver, url, config_dict)

        if 'ibon.com' in url:
            ibon_main(driver, url, config_dict)

        # for facebook
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            facebook_account = config_dict["advanced"]["facebook_account"].strip()
            if len(facebook_account) > 4:
                facebook_login(driver, facebook_account)

if __name__ == "__main__":
    CONST_MODE_GUI = 0
    CONST_MODE_CLI = 1
    mode = CONST_MODE_GUI
    #mode = CONST_MODE_CLI
    
    if mode == CONST_MODE_GUI:
        main()
    else:
        #for test kktix infer answer.
        #captcha_text_div_text = u"請回答下列問題,請在下方空格輸入DELIGHT（請以半形輸入法作答，大小寫需要一模一樣）"
        #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「abc」"
        #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「0118eveconcert」（請以半形小寫作答。）"
        #captcha_text_div_text = "在《DEEP AWAKENING見過深淵的人》專輯中，哪一首為合唱曲目？ 【V6】深淵 、【Z5】浮木、【J8】無聲、【C1】以上皆非 （請以半形輸入法作答，大小寫/阿拉伯數字需要一模一樣，範例：A2）"
        captcha_text_div_text = "Super Junior 的隊長是以下哪位?  【v】神童 【w】藝聲 【x】利特 【y】始源  若你覺得答案為 a，請輸入 a  (英文為半形小寫)"
        inferred_answer_string, answer_list = get_answer_list_from_question_string(None, captcha_text_div_text)
        print("inferred_answer_string:", inferred_answer_string)
        print("answer_list:", answer_list)

        ocr = ddddocr.DdddOcr()
        with open('captcha-oapi.png', 'rb') as f:
            image_bytes = f.read()
        res = ocr.classification(image_bytes)
        print(res)

