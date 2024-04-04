#!/usr/bin/env python3
#encoding=utf-8
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
import argparse
import base64
import json
import logging
import os
import pathlib
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

import nodriver as uc
from nodriver import cdp
from nodriver.core.config import Config
from urllib3.exceptions import InsecureRequestWarning

import util
from NonBrowser import NonBrowser

try:
    import ddddocr
except Exception as exc:
    print(exc)
    pass

CONST_APP_VERSION = "MaxBot (2024.03.23)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"
CONST_MAXBLOCK_EXTENSION_NAME = "Maxblockplus_1.0.0"
CONST_MAXBLOCK_EXTENSION_FILTER =[
"*google-analytics.com/*",
"*googletagmanager.com/*",
"*googletagservices.com/*",
"*lndata.com/*",
"*a.amnet.tw/*",
"*adx.c.appier.net/*",
"*clarity.ms/*",
"*cloudfront.com/*",
"*cms.analytics.yahoo.com/*",
"*doubleclick.net/*",
"*e2elog.fetnet.net/*",
"*fundingchoicesmessages.google.com/*",
"*ghtinc.com/*",
"*match.adsrvr.org/*",
"*onead.onevision.com.tw/*",
"*popin.cc/*",
"*rollbar.com/*",
"*sb.scorecardresearch.com/*",
"*tagtoo.co/*",
"*.ssp.hinet.net/*",
"*ticketmaster.sg/js/adblock*",
"*.googlesyndication.com/*",
"*treasuredata.com/*",
"*play.google.com/log?*",
"*www.youtube.com/youtubei/v1/player/heartbeat*",
"*tixcraft.com/js/analytics.js*",
"*ticketmaster.sg/js/adblock.js*",
"*img.uniicreative.com/*",
"*cdn.cookielaw.org/*",
"*tixcraft.com/js/custom.js*",
"*tixcraft.com/js/common.js*",
"*cdnjs.cloudflare.com/ajax/libs/clipboard.js/*"]

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
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM

CONT_STRING_1_SEATS_REMAINING = ['@1 seat(s) remaining','剩餘 1@','@1 席残り']

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"
CONST_CHROME_FAMILY = ["chrome","edge","brave"]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig()
logger = logging.getLogger('logger')


def get_config_dict(args):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    # allow assign config by command line.
    if not args.input is None:
        if len(args.input) > 0:
            config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        # start to overwrite config settings.
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

            if not args.headless is None:
                config_dict["advanced"]["headless"] = util.t_or_f(args.headless)

            if not args.homepage is None:
                if len(args.homepage) > 0:
                    config_dict["homepage"] = args.homepage
            
            if not args.ticket_number is None:
                if args.ticket_number > 0:
                    config_dict["ticket_number"] = args.ticket_number
            
            if not args.browser is None:
                if len(args.browser) > 0:
                    config_dict["browser"] = args.browser

            if not args.tixcraft_sid is None:
                if len(args.tixcraft_sid) > 0:
                    config_dict["advanced"]["tixcraft_sid"] = args.tixcraft_sid
            if not args.ibonqware is None:
                if len(args.ibonqware) > 0:
                    config_dict["advanced"]["ibonqware"] = args.ibonqware

            if not args.kktix_account is None:
                if len(args.kktix_account) > 0:
                    config_dict["advanced"]["kktix_account"] = args.kktix_account
            if not args.kktix_password is None:
                if len(args.kktix_password) > 0:
                    config_dict["advanced"]["kktix_password_plaintext"] = args.kktix_password
            
            if not args.proxy_server is None:
                if len(args.proxy_server) > 2:
                    config_dict["advanced"]["proxy_server_port"] = args.proxy_server

            if not args.window_size is None:
                if len(args.window_size) > 2:
                    config_dict["advanced"]["window_size"] = args.window_size


            # special case for headless to enable away from keyboard mode.
            is_headless_enable_ocr = False
            if config_dict["advanced"]["headless"]:
                # for tixcraft headless.
                #print("If you are runnig headless mode on tixcraft, you need input your cookie SID.")
                if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
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

def play_sound_while_ordering(config_dict):
    app_root = util.get_app_root()
    captcha_sound_filename = os.path.join(app_root, config_dict["advanced"]["play_sound"]["filename"].strip())
    util.play_mp3_async(captcha_sound_filename)

async def nodriver_kktix_signin(tab, url, config_dict):
    kktix_account = config_dict["advanced"]["kktix_account"]
    kktix_password = config_dict["advanced"]["kktix_password_plaintext"].strip()
    if kktix_password == "":
        kktix_password = util.decryptMe(config_dict["advanced"]["kktix_password"])
    if len(kktix_account) > 4:
        account = await tab.select("#user_login")
        await account.send_keys(kktix_account)
        #await tab.sleep(0.1)

        password = await tab.select("#user_password")
        await password.send_keys(kktix_password)
        #await tab.sleep(0.1)

        submit = await tab.select("input[type='submit'][name]")
        await submit.click()
        await tab.sleep(0.2)

async def nodriver_kktix_paused_main(tab, url, config_dict, kktix_dict):
    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        await nodriver_kktix_signin(tab, url, config_dict)
        is_url_contain_sign_in = True

    return kktix_dict

async def nodriver_goto_homepage(driver, config_dict):
    homepage = config_dict["homepage"]
    if 'kktix.c' in homepage:
        if len(config_dict["advanced"]["kktix_account"])>0:
            if not 'https://kktix.com/users/sign_in?' in homepage:
                homepage = CONST_KKTIX_SIGN_IN_URL % (homepage)
    return await driver.get(homepage)

async def nodriver_kktix_travel_price_list(tab, config_dict, kktix_area_auto_select_mode, kktix_area_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ticket_number = config_dict["ticket_number"]

    areas = None
    is_ticket_number_assigned = False

    ticket_price_list = None
    try:
        ticket_price_list = await tab.select_all('div.display-table-row')
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
            row_input = None
            current_ticket_number = "0"
            try:
                js_attr = await row.get_js_attributes()
                row_html = js_attr["innerHTML"]
                row_text = js_attr["innerText"]
                row_input = await row.query_selector("input")
                if not row_input is None:
                    js_attr_input = await row_input.get_js_attributes()
                    current_ticket_number = js_attr_input["value"]
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

            if not row_input is None:
                # check ticket input textbox.
                if len(current_ticket_number) > 0:
                    if current_ticket_number != "0":
                        is_ticket_number_assigned = True

                if is_ticket_number_assigned:
                    # no need to travel
                    break

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
                    areas.append(row_input)

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


async def nodriver_kktix_assign_ticket_number(tab, config_dict, kktix_area_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ticket_number_str = str(config_dict["ticket_number"])
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_ticket_number_assigned = False
    matched_blocks = None
    is_dom_ready = True
    is_dom_ready, is_ticket_number_assigned, matched_blocks = await nodriver_kktix_travel_price_list(tab, config_dict, auto_select_mode, kktix_area_keyword)

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
            current_ticket_number = str(target_area.attribute('value')).strip()
        except Exception as exc:
            pass

        if len(current_ticket_number) > 0:
            if current_ticket_number == "0":
                try:
                    print("asssign ticket number:%s" % ticket_number_str)
                    target_area.clear_input()
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

async def nodriver_get_kktix_question_text(tab):
    question_text = ""

    captcha_inner_div = None
    try:
        captcha_inner_div = await tab.select('div.custom-captcha-inner p')
        if not captcha_inner_div is None:
            js_attr = await captcha_inner_div.get_js_attributes()
            question_text =  js_attr["innerText"].strip()
    except Exception as exc:
        print(exc)
        pass
    return question_text

# 本票券需要符合以下任一資格才可以購買
async def nodriver_get_kktix_control_label_text(tab):
    question_text = ""

    captcha_inner_div = None
    try:
        captcha_inner_div = await tab.select('div > div.code-input > div.control-group > label.control-label')
        if not captcha_inner_div is None:
            js_attr = await captcha_inner_div.get_js_attributes()
            question_text = js_attr["innerText"]
    except Exception as exc:
        pass
    return question_text

async def nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    is_question_popup = False
    question_text = await nodriver_get_kktix_question_text(tab)
    if len(question_text) > 0:
        is_question_popup = True
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                #answer_list = util.get_answer_list_from_question_string(registrationsNewApp_div, question_text)
                # due to selenium forat.
                answer_list = util.get_answer_list_from_question_string(None, question_text)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        if show_debug_message:
            print("inferred_answer_string:", inferred_answer_string)
            print("question_text:", question_text)
            print("answer_list:", answer_list)
            print("fail_list:", fail_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        input_text_css = 'div.custom-captcha-inner > div > div > input'
        next_step_button_css = ''
        submit_by_enter = False
        check_input_interval = 0.2
        #is_answer_sent, fail_list = fill_common_verify_form(tab, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)
        if len(answer_list) > 0:
            input_text = await tab.select(input_text_css)
            if not input_text is None:
                await input_text.send_keys(answer_list[0])

                # due multi next buttons(pick seats/best seats)
                await nodriver_kktix_press_next_button(tab)

    return fail_list, is_question_popup

#   : This is for case-2 next button.
async def nodriver_kktix_press_next_button(tab):
    ret = False

    css_select = "div.register-new-next-button-area > button"
    but_button_list = None
    try:
        but_button_list = await tab.select_all(css_select)
    except Exception as exc:
        print(exc)
        pass

    if not but_button_list is None:
        button_count = len(but_button_list)
        #print("button_count:",button_count)
        if button_count > 0:
            try:
                #print("click on last button")
                await but_button_list[button_count-1].click()
                ret = True
            except Exception as exc:
                print(exc)
                pass

    return ret


async def nodriver_kktix_reg_new_main(tab, config_dict, fail_list, played_sound_ticket):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    # part 1: check div.
    registrationsNewApp_div = None
    try:
        registrationsNewApp_div = await tab.select('#registrationsNewApp')
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
                is_need_refresh_tmp = Falses
                is_dom_ready, is_ticket_number_assigned, is_need_refresh_tmp = await nodriver_kktix_assign_ticket_number(tab, config_dict, area_keyword_item)

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
            # TODO:
            is_dom_ready, is_ticket_number_assigned, is_need_refresh = await nodriver_kktix_assign_ticket_number(tab, config_dict, "")
            pass

        if is_dom_ready:
            # part 3: captcha
            if is_ticket_number_assigned:
                if config_dict["advanced"]["play_sound"]["ticket"]:
                    if not played_sound_ticket:
                        play_sound_while_ordering(config_dict)
                    played_sound_ticket = True

                # whole event question.
                fail_list, is_question_popup = await nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div)
                
                # single option question
                if not is_question_popup:
                    # no captcha text popup, goto next page.
                    control_text = await nodriver_get_kktix_control_label_text(tab)
                    if show_debug_message:
                        print("control_text:", control_text)
                    
                    if len(control_text) == 0:
                        click_ret = await nodriver_kktix_press_next_button(tab)
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
                            #TODO:
                            #set_kktix_control_label_text(driver, config_dict)
                            pass
            else:
                if is_need_refresh:
                    # reset to play sound when ticket avaiable.
                    played_sound_ticket = False

                    try:
                        print("no match any price, start to refresh page...")
                        await tab.reload()
                    except Exception as exc:
                        #print("refresh fail")
                        pass

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return fail_list, played_sound_ticket

async def nodriver_kktix_main(tab, url, config_dict, kktix_dict):
    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        await nodriver_kktix_signin(tab, url, config_dict)
        is_url_contain_sign_in = True

    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            kktix_dict["start_time"] = time.time()

            is_dom_ready = False
            try:
                html_body = await tab.get_content()
                #print("html_body:",len(html_body))
                if len(html_body) > 10240:
                    if "registrationsNewApp" in html_body:
                        if not "{{'new.i_read_and_agree_to'" in html_body:
                            is_dom_ready = True
            except Exception as exc:
                print(exc)
                pass

            if not is_dom_ready:
                # reset answer fail list.
                kktix_dict["fail_list"] = []
                kktix_dict["played_sound_ticket"] = False
            else:
                is_finish_checkbox_click = False
                #TODO: check checkbox here.

                # check is able to buy.
                if config_dict["kktix"]["auto_fill_ticket_number"]:
                    kktix_dict["fail_list"], kktix_dict["played_sound_ticket"] = await nodriver_kktix_reg_new_main(tab, config_dict, kktix_dict["fail_list"], kktix_dict["played_sound_ticket"])
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
                    #kktix_events_press_next_button(driver)
                    pass

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
                    kktix_account = config_dict["advanced"]["kktix_account"]
                    kktix_password = config_dict["advanced"]["kktix_password_plaintext"].strip()
                    if kktix_password == "":
                        kktix_password = util.decryptMe(config_dict["advanced"]["kktix_password"])
                    
                    print("基本資料(或實名制)網址:", url)
                    if len(kktix_account) > 0:
                        print("搶票成功, 帳號:", kktix_account)
                        
                        script_name = "chrome_tixcraft"
                        if config_dict["advanced"]["webdriver_type"] == CONST_WEBDRIVER_TYPE_NODRIVER:
                            script_name = "nodriver_tixcraft"

                        threading.Thread(target=util.launch_maxbot, args=(script_name,"", url, kktix_account, kktix_password,"","false",)).start()
                        #driver.quit()
                        #sys.exit()

                    is_event_page = False
                    if len(url.split('/'))>=7:
                        is_event_page = True
                    if is_event_page:
                        confirm_clicked = False
                        
                        try:
                            submit = await tab.select("div.form-actions a.btn-primary")
                            await submit.click()
                            confirm_clicked = True
                        except Exception as exc:
                            print(exc)

                        if confirm_clicked:
                            domain_name = url.split('/')[2]
                            checkout_url = "https://%s/account/orders" % (domain_name)
                            print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                            webbrowser.open_new(checkout_url)
                    
                    kktix_dict["is_popup_checkout"] = True
                    driver.quit()
                    sys.exit()
    else:
        kktix_dict["is_popup_checkout"] = False
        kktix_dict["played_sound_order"] = False

    return kktix_dict


def get_nodriver_browser_args():
    browser_args = [
        "--user-agent=%s" % (USER_AGENT),
        "--disable-2d-canvas-clip-aa",
        "--disable-3d-apis",
        "--disable-animations",
        "--disable-app-info-dialog-mac",
        "--disable-background-networking",
        "--disable-backgrounding-occluded-windows",
        "--disable-bookmark-reordering",
        "--disable-boot-animation",
        "--disable-breakpad",
        "--disable-canvas-aa",
        "--disable-client-side-phishing-detection",
        "--disable-cloud-import",
        "--disable-component-cloud-policy",
        "--disable-component-update",
        "--disable-composited-antialiasing",
        "--disable-default-apps",
        "--disable-dev-shm-usage",
        "--disable-device-discovery-notifications",
        "--disable-dinosaur-easter-egg",
        "--disable-domain-reliability",
        "--disable-features=IsolateOrigins,site-per-process,TranslateUI",
        "--disable-infobars",
        "--disable-logging",
        "--disable-login-animations",
        "--disable-login-screen-apps",
        "--disable-notifications",
        "--disable-office-editing-component-extension",
        "--disable-password-generation",
        "--disable-popup-blocking",
        "--disable-renderer-backgrounding",
        "--disable-session-crashed-bubble",
        "--disable-smooth-scrolling",
        "--disable-suggestions-ui",
        "--disable-sync",
        "--disable-translate",
        "--hide-crash-restore-bubble",
        "--homepage=about:blank",
        "--no-default-browser-check",
        "--no-first-run",
        "--no-pings",
        "--no-sandbox"
        "--no-service-autorun",
        "--password-store=basic",
        "--remote-allow-origins=*",
        "--lang=zh-TW",
        #"--disable-remote-fonts",
    ]
    return browser_args

def get_maxbot_plus_extension_path():
    extension_path = "webdriver/Maxbotplus_1.0.0/"
    if platform.system() == 'Windows':
        extension_path = extension_path.replace("/","\\")
    
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, extension_path)
    #print("config_filepath:", config_filepath)

    # check extesion mainfest
    path = pathlib.Path(config_filepath)
    if path.exists():
        if path.is_dir():
            #print("found extension dir")
            for item in path.rglob("manifest.*"):
                path = item.parent
            #print("final path:", path)

    return config_filepath

def get_extension_config(config_dict):
    default_lang = "zh-TW"
    no_sandbox=True
    conf = Config(browser_args=get_nodriver_browser_args(), lang=default_lang, no_sandbox=no_sandbox, headless=config_dict["advanced"]["headless"])
    conf.add_extension(get_maxbot_plus_extension_path())
    return conf

async def nodrver_block_urls(tab, config_dict):
    NETWORK_BLOCKED_URLS = ['*/adblock.js'
    ,'*/google_ad_block.js'
    ,'*google-analytics.*'
    ,'*googletagmanager.*'
    ,'*googletagservices.*'
    ,'*googlesyndication.*'
    ,'*play.google.com/*'
    ,'*cdn.cookielaw.org/*'
    ,'*fundingchoicesmessages.google.com/*'
    ,'*.doubleclick.net/*'
    ,'*.rollbar.com/*'
    ,'*.cloudfront.com/*'
    ,'*.lndata.com/*'
    ,'*.twitter.com/i/*'
    ,'*platform.twitter.com/*'
    ,'*syndication.twitter.com/*'
    ,'*youtube.com/*'
    ,'*player.youku.*'
    ,'*.clarity.ms/*'
    ,'*img.uniicreative.com/*'
    ,'*e2elog.fetnet.net*']

    if True:
    #if config_dict["advanced"]["hide_some_image"]:
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

        NETWORK_BLOCKED_URLS.append('https://kktix.cc/change_locale?locale=*')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/logo_*.png')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/icon-*.png')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/upload_images/*.jpg')

    if False:
    #if config_dict["advanced"]["block_facebook_network"]:
        NETWORK_BLOCKED_URLS.append('*facebook.com/*')
        NETWORK_BLOCKED_URLS.append('*.fbcdn.net/*')

    await tab.send(cdp.network.enable())
    # set_blocked_ur_ls is author's typo..., waiting author to chagne.
    await tab.send(cdp.network.set_blocked_ur_ls(NETWORK_BLOCKED_URLS))
    return tab

async def nodriver_resize_window(tab, config_dict):
    if len(config_dict["advanced"]["window_size"]) > 0:
        if "," in config_dict["advanced"]["window_size"]:
            size_array = config_dict["advanced"]["window_size"].split(",")
            position_left = 0
            if len(size_array) >= 3:
                position_left = int(size_array[0]) * int(size_array[2])
            #tab = await driver.main_tab()
            if tab:
                await tab.set_window_size(left=position_left, top=30, width=int(size_array[0]), height=int(size_array[1]))

async def nodriver_current_url(tab):
    url = ""
    if tab:
        url_dict = {}
        try:
            url_dict = await tab.js_dumps('window.location.href')
        except Exception as exc:
            print(exc)
            pass

        url_array = []
        if url_dict:
            for k in url_dict: 
                if k.isnumeric():
                    if "0" in url_dict[k]:
                        url_array.append(url_dict[k]["0"])
            url = ''.join(url_array)
    return url

def nodriver_overwrite_prefs(conf, prefs_dict={}):
    #print(conf.user_data_dir)
    prefs_filepath = os.path.join(conf.user_data_dir,"Default")
    if not os.path.exists(prefs_filepath):
        os.mkdir(prefs_filepath)
    prefs_filepath = os.path.join(prefs_filepath,"Preferences")
    prefs_dict["profile"]={}
    prefs_dict["profile"]["name"]=CONST_APP_VERSION
    prefs_dict["profile"]["password_manager_enabled"]=False
    json_str = json.dumps(prefs_dict)
    with open(prefs_filepath, 'w') as outfile:
        outfile.write(json_str)

    state_filepath = os.path.join(conf.user_data_dir,"Local State")
    state_dict = {}
    state_dict["performance_tuning"]={}
    state_dict["performance_tuning"]["high_efficiency_mode"]={}
    state_dict["performance_tuning"]["high_efficiency_mode"]["state"]=1
    state_dict["browser"]={}
    state_dict["browser"]["enabled_labs_experiments"]=[
        "memory-saver-multi-state-mode@1",
        "modal-memory-saver@1"
    ]
    json_str = json.dumps(state_dict)
    with open(state_filepath, 'w') as outfile:
        outfile.write(json_str)

async def main(args):
    config_dict = get_config_dict(args)

    driver = None
    tab = None
    if not config_dict is None:
        sandbox = False
        conf = get_extension_config(config_dict)
        prefs = {"credentials_enable_service": False,
            "ack_existing_ntp_extensions": False,
            "translate":{"enabled": False}}
        nodriver_overwrite_prefs(conf, prefs)
        # PS: nodrirver run twice always cause error:
        # Failed to connect to browser
        # One of the causes could be when you are running as root.
        # In that case you need to pass no_sandbox=True
        #driver = await uc.start(conf, sandbox=sandbox, headless=config_dict["advanced"]["headless"])
        driver = await uc.start(conf)
        if not driver is None:
            tab = await nodriver_goto_homepage(driver, config_dict)
            tab = await nodrver_block_urls(tab, config_dict)
            if not config_dict["advanced"]["headless"]:
                await nodriver_resize_window(tab, config_dict)
        else:
            print("無法使用nodriver，程式無法繼續工作")
            sys.exit()
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    # for tixcraft
    tixcraft_dict = {}
    tixcraft_dict["fail_list"]=[]
    tixcraft_dict["fail_promo_list"]=[]
    tixcraft_dict["start_time"]=None
    tixcraft_dict["done_time"]=None
    tixcraft_dict["elapsed_time"]=None
    tixcraft_dict["is_popup_checkout"] = False
    tixcraft_dict["area_retry_count"]=0

    # for kktix
    kktix_dict = {}
    kktix_dict["fail_list"]=[]
    kktix_dict["start_time"]=None
    kktix_dict["done_time"]=None
    kktix_dict["elapsed_time"]=None
    kktix_dict["is_popup_checkout"] = False
    kktix_dict["played_sound_ticket"] = False
    kktix_dict["played_sound_order"] = False

    fami_dict = {}
    fami_dict["fail_list"] = []
    fami_dict["last_activity"]=""

    ibon_dict = {}
    ibon_dict["fail_list"]=[]
    ibon_dict["start_time"]=None
    ibon_dict["done_time"]=None
    ibon_dict["elapsed_time"]=None

    hkticketing_dict = {}
    hkticketing_dict["is_date_submiting"] = False
    hkticketing_dict["fail_list"]=[]

    ticketplus_dict = {}
    ticketplus_dict["fail_list"]=[]
    ticketplus_dict["is_popup_confirm"] = False

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
            Captcha_Browser = NonBrowser()
            if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
    except Exception as exc:
        print(exc)
        pass

    maxbot_last_reset_time = time.time()
    while True:
        time.sleep(0.05)

        # pass if driver not loaded.
        if driver is None:
            print("nodriver not accessible!")
            break

        url = await nodriver_current_url(tab)
        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        is_maxbot_paused = False
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            is_maxbot_paused = True

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                if is_maxbot_paused:
                    print("MAXBOT Paused.")
            last_url = url

        if is_maxbot_paused:
            if 'kktix.c' in url:
                kktix_dict = await nodriver_kktix_paused_main(tab, url, config_dict, kktix_dict)
            # sleep more when paused.
            time.sleep(0.1)
            continue

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            kktix_dict = await nodriver_kktix_main(tab, url, config_dict, kktix_dict)
            pass

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if 'ticketmaster.' in url:
            tixcraft_family = True

        if tixcraft_family:
            #tixcraft_dict = tixcraft_main(driver, url, config_dict, tixcraft_dict, ocr, Captcha_Browser)
            pass

        if 'famiticket.com' in url:
            #fami_dict = famiticket_main(driver, url, config_dict, fami_dict)
            pass

        if 'ibon.com' in url:
            #ibon_dict = ibon_main(driver, url, config_dict, ibon_dict, ocr, Captcha_Browser)
            pass

        kham_family = False
        if 'kham.com.tw' in url:
            kham_family = True

        if 'ticket.com.tw' in url:
            kham_family = True

        if 'tickets.udnfunlife.com' in url:
            kham_family = True

        if kham_family:
            #kham_main(driver, url, config_dict, ocr, Captcha_Browser)
            pass

        if 'ticketplus.com' in url:
            #ticketplus_dict = ticketplus_main(driver, url, config_dict, ocr, Captcha_Browser, ticketplus_dict)
            pass

        if 'urbtix.hk' in url:
            #urbtix_main(driver, url, config_dict)
            pass

        if 'cityline.com' in url:
            #cityline_main(driver, url, config_dict)
            pass

        softix_family = False
        if 'hkticketing.com' in url:
            softix_family = True
        if 'galaxymacau.com' in url:
            softix_family = True
        if 'ticketek.com' in url:
            softix_family = True
        if softix_family:
            #hkticketing_dict = softix_powerweb_main(driver, url, config_dict, hkticketing_dict)
            pass

        # for facebook
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            facebook_account = config_dict["advanced"]["facebook_account"].strip()
            facebook_password = config_dict["advanced"]["facebook_password_plaintext"].strip()
            if facebook_password == "":
                facebook_password = util.decryptMe(config_dict["advanced"]["facebook_password"])
            if len(facebook_account) > 4:
                #facebook_login(driver, facebook_account, facebook_password)
                pass


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
    uc.loop().run_until_complete(main(args))

if __name__ == "__main__":
    cli()
