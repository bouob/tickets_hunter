#!/usr/bin/env python3
#encoding=utf-8
import argparse
import base64
import json
import logging
import asyncio
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

# 強制使用 UTF-8 編碼輸出（解決 Windows CP950 編碼問題）
# 僅在終端直接輸出時使用，避免與檔案重定向衝突導致死鎖
if sys.platform == 'win32' and sys.stdout.isatty():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import nodriver as uc
from nodriver import cdp
from nodriver.core.config import Config
from urllib3.exceptions import InsecureRequestWarning
import urllib.parse

import util
from NonBrowser import NonBrowser

try:
    import ddddocr
except Exception as exc:
    print(exc)
    pass

CONST_APP_VERSION = "TicketsHunter (2025.09.29)"


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
"*adx.c.appier.net/*",
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
"*ticketmaster.sg/js/adblock*",
"*ticketmaster.sg/js/adblock.js*",
"*tixcraft.com/js/analytics.js*",
"*tixcraft.com/js/common.js*",
"*tixcraft.com/js/custom.js*",
"*treasuredata.com/*",
"*www.youtube.com/youtubei/v1/player/heartbeat*",
]

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
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# ===== Cloudflare 繞過模式設定 =====
# 模式說明：
# "auto"   - 自動靜默執行，無額外輸出（建議日常使用）
# "debug"  - 顯示詳細處理過程，適合除錯
# "manual" - 只偵測並提示，不自動處理
# "off"    - 完全停用 Cloudflare 繞過功能
CLOUDFLARE_BYPASS_MODE = "auto"
CLOUDFLARE_MAX_RETRY = 3         # 最大重試次數
CLOUDFLARE_WAIT_TIME = 3         # 每次嘗試後的等待時間（秒）
CLOUDFLARE_ENABLE_EXPERT_MODE = False  # True 會啟用更激進的瀏覽器參數（參考 stackoverflow.max-everyday.com）

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig()
logger = logging.getLogger('logger')


def get_config_dict(args):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    if args.input and len(args.input) > 0:
        config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

            # Define a dictionary to map argument names to their paths in the config_dict
            arg_to_path = {
                "headless": ["advanced", "headless"],
                "homepage": ["homepage"],
                "ticket_number": ["ticket_number"],
                "browser": ["browser"],
                "tixcraft_sid": ["advanced", "tixcraft_sid"],
                "ibonqware": ["advanced", "ibonqware"],
                "proxy_server": ["advanced", "proxy_server_port"],
                "window_size": ["advanced", "window_size"],
                "date_auto_select_mode": ["date_auto_select", "mode"],
                "date_keyword": ["date_auto_select", "date_keyword"]
            }

            # Update the config_dict based on the arguments
            for arg, path in arg_to_path.items():
                value = getattr(args, arg)
                if value and len(str(value)) > 0:
                    d = config_dict
                    for key in path[:-1]:
                        d = d[key]
                    d[path[-1]] = value

            # special case for headless to enable away from keyboard mode.
            is_headless_enable_ocr = False
            if config_dict["advanced"]["headless"]:
                # for tixcraft headless.
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

async def nodriver_press_button(tab, select_query):
    if tab:
        try:
            element = await tab.query_selector(select_query)
            if element:
                await element.click()
            else:
                #print("element not found:", select_query)
                pass
        except Exception as e:
            #print("click fail for selector:", select_query)
            print(e)
            pass

from typing import Optional

async def nodriver_check_checkbox(tab: Optional[object], select_query: str, value: str = 'true') -> bool:
    if tab:
        try:
            # 使用 JavaScript 檢查 checkbox 狀態並避免重複點擊
            result = await tab.evaluate(f'''
                (function() {{
                    const checkboxes = document.querySelectorAll('{select_query}');
                    let targetCheckbox = null;

                    // 尋找第一個非記得密碼的 checkbox
                    for (let i = 0; i < checkboxes.length; i++) {{
                        const checkbox = checkboxes[i];
                        const id = checkbox.id || '';
                        const name = checkbox.name || '';
                        const className = checkbox.className || '';
                        const labelText = checkbox.labels && checkbox.labels[0] ? checkbox.labels[0].textContent : '';

                        // 檢查是否為記得密碼相關的 checkbox
                        const isRememberCheckbox =
                            id.toLowerCase().includes('remember') ||
                            name.toLowerCase().includes('remember') ||
                            className.toLowerCase().includes('remember') ||
                            labelText.includes('記得') ||
                            labelText.includes('記住') ||
                            labelText.includes('Remember') ||
                            labelText.includes('密碼');

                        if (!isRememberCheckbox) {{
                            targetCheckbox = checkbox;
                            break;
                        }}
                    }}

                    if (!targetCheckbox) return false;

                    // 如果已經勾選，直接回傳成功
                    if (targetCheckbox.checked) return true;

                    // 只在未勾選時才點擊
                    try {{
                        targetCheckbox.click();
                        return targetCheckbox.checked;
                    }} catch(e) {{
                        // fallback: 直接設定 checked 屬性
                        targetCheckbox.checked = true;
                        return targetCheckbox.checked;
                    }}
                }})();
            ''')
            return bool(result)
        except Exception as exc:
            print(exc)
    return False

async def nodriver_force_check_checkbox(tab, checkbox_element):
    """強制勾選 checkbox，參考 Chrome 版本的 force_check_checkbox 邏輯"""
    is_finish_checkbox_click = False

    if checkbox_element:
        try:
            # 使用 JavaScript 檢查和設定 checkbox 狀態
            result = await tab.evaluate('''
                (function(element) {
                    if (!element) return false;

                    // 檢查是否已勾選
                    if (element.checked) return true;

                    // 嘗試點擊勾選
                    try {
                        element.click();
                        return element.checked;
                    } catch(e) {
                        // fallback: 直接設定 checked 屬性
                        element.checked = true;
                        return element.checked;
                    }
                })(arguments[0]);
            ''', checkbox_element)

            is_finish_checkbox_click = bool(result)

        except Exception as exc:
            pass

    return is_finish_checkbox_click

async def nodriver_check_checkbox_enhanced(tab, select_query, show_debug_message=False):
    """增強版勾選函式，直接使用 JavaScript 操作"""
    is_checkbox_checked = False

    try:
        if show_debug_message:
            print(f"執行勾選 checkbox: {select_query}")

        # 直接使用 JavaScript 查找並勾選
        result = await tab.evaluate(f'''
            (function() {{
                const checkbox = document.querySelector('{select_query}');
                if (!checkbox) return false;

                if (checkbox.checked) return true;

                try {{
                    checkbox.click();
                    return checkbox.checked;
                }} catch(e) {{
                    checkbox.checked = true;
                    return checkbox.checked;
                }}
            }})();
        ''')

        is_checkbox_checked = bool(result)

        if show_debug_message:
            print(f"勾選結果: {is_checkbox_checked}")

    except Exception as exc:
        if show_debug_message:
            print(f"勾選異常: {exc}")

    return is_checkbox_checked

async def nodriver_facebook_login(tab, facebook_account, facebook_password):
    if tab:
        try:
            account = await tab.query_selector("#email")
            if account:
                await account.send_keys(facebook_account)
            else:
                print("account not found")

            password = await tab.query_selector("#pass")
            if password:
                await password.send_keys(facebook_password)
                await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                await asyncio.sleep(2)
            else:
                print("password not found")
        except Exception as e:
            print("send_keys fail.")
            print(e)
            pass


async def detect_cloudflare_challenge(tab, show_debug=False):
    """
    偵測是否遇到 Cloudflare 挑戰頁面

    Returns:
        bool: True 如果偵測到 Cloudflare 挑戰頁面
    """
    try:
        html_content = await tab.get_content()
        if not html_content:
            return False

        html_lower = html_content.lower()

        # Cloudflare 挑戰頁面的特徵標記
        cloudflare_indicators = [
            "cloudflare",
            "cf-browser-verification",
            "challenge-platform",
            "checking your browser",
            "please wait while we verify",
            "verify you are human",
            "正在驗證",
            "驗證你是人類",
            "cf-challenge-running",
            "cf-spinner-allow-5-secs"
        ]

        detected = any(indicator in html_lower for indicator in cloudflare_indicators)

        if detected:
            # 只在首次偵測到時顯示訊息，避免重複輸出
            # print("[CLOUDFLARE] 偵測到 Cloudflare 挑戰頁面")  # 移除重複訊息
            pass

        return detected

    except Exception as exc:
        if show_debug:
            print(f"Cloudflare 偵測過程發生錯誤: {exc}")
        return False


async def handle_cloudflare_challenge(tab, config_dict, max_retry=None):
    """
    處理 Cloudflare 挑戰頁面 - 增強版

    Args:
        tab: nodriver tab 物件
        config_dict: 設定字典
        max_retry: 最大重試次數（若為 None 則使用全域設定）

    Returns:
        bool: True 如果成功繞過 Cloudflare
    """
    # 使用全域設定或傳入值
    max_retry = max_retry or CLOUDFLARE_MAX_RETRY

    # 根據模式決定是否顯示訊息
    show_debug_message = (config_dict["advanced"]["verbose"] or
                         CLOUDFLARE_BYPASS_MODE == "debug")

    # 自動模式下靜默執行
    if CLOUDFLARE_BYPASS_MODE == "auto":
        show_debug_message = False

    if show_debug_message:
        print("[CLOUDFLARE] 開始處理 Cloudflare 挑戰...")

    for retry_count in range(max_retry):
        try:
            if retry_count > 0:
                if show_debug_message:
                    print(f"[CLOUDFLARE] 重試第 {retry_count} 次...")
                # 增加重試間隔
                await tab.sleep(3 + retry_count)

            # 方法一：使用 nodriver 內建的 Cloudflare 繞過功能
            try:
                cf_result = await tab.cf_verify()
                if show_debug_message:
                    print(f"cf_verify 結果: {cf_result}")
            except Exception as cf_exc:
                if show_debug_message:
                    print(f"cf_verify 不可用: {cf_exc}")
                # 方法二：嘗試點擊驗證框（如果存在）
                try:
                    # 尋找 Cloudflare 驗證框
                    verify_box = await tab.query_selector('input[type="checkbox"]')
                    if verify_box:
                        await verify_box.click()
                        if show_debug_message:
                            print("[CLOUDFLARE] 嘗試點擊驗證框")
                except Exception:
                    pass

            # 等待挑戰完成（動態調整等待時間）
            wait_time = CLOUDFLARE_WAIT_TIME + (retry_count * 2)
            await tab.sleep(wait_time)

            # 檢查是否成功繞過
            if not await detect_cloudflare_challenge(tab, show_debug_message):
                if show_debug_message:
                    print("[CLOUDFLARE] Cloudflare 挑戰繞過成功")
                return True
            else:
                if show_debug_message:
                    print(f"[CLOUDFLARE] 第 {retry_count + 1} 次嘗試未成功")

                # 最後一次嘗試：刷新頁面
                if retry_count == max_retry - 1:
                    try:
                        if show_debug_message:
                            print("[CLOUDFLARE] 最後嘗試：刷新頁面")
                        await tab.reload()
                        await tab.sleep(5)
                        if not await detect_cloudflare_challenge(tab, show_debug_message):
                            return True
                    except Exception:
                        pass

        except Exception as exc:
            if show_debug_message:
                print(f"[CLOUDFLARE] 處理過程發生錯誤: {exc}")

    if show_debug_message:
        print("[CLOUDFLARE] Cloudflare 挑戰處理失敗，已達最大重試次數")
        print("[CLOUDFLARE] 建議：檢查網路連線或稍後再試")
    return False




async def nodriver_kktix_signin(tab, url, config_dict):
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print("nodriver_kktix_signin:", url)

    # 解析 back_to 參數取得真正的目標頁面
    import urllib.parse
    target_url = config_dict["homepage"]  # 預設值
    try:
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        if 'back_to' in params and len(params['back_to']) > 0:
            target_url = params['back_to'][0]
    except Exception as exc:
        print(f"解析 back_to 參數失敗: {exc}")

    # for like human.
    await asyncio.sleep(random.uniform(3, 5))

    kktix_account = config_dict["advanced"]["kktix_account"]
    kktix_password = config_dict["advanced"]["kktix_password_plaintext"].strip()
    if kktix_password == "":
        kktix_password = util.decryptMe(config_dict["advanced"]["kktix_password"])

    has_redirected = False
    if len(kktix_account) > 4:
        try:
            account = await tab.query_selector("#user_login")
            if account:
                await account.send_keys(kktix_account)
                await asyncio.sleep(random.uniform(0.8, 1.5))

            password = await tab.query_selector("#user_password")
            if password:
                await password.send_keys(kktix_password)
                await asyncio.sleep(random.uniform(0.8, 2.0))

            await tab.evaluate('''
                const loginBtn = document.querySelector('input[type="submit"][value="登入"]');
                if (loginBtn) {
                    loginBtn.click();
                }
            ''')

            await asyncio.sleep(random.uniform(5.0, 10.0))

            try:
                current_url = await tab.evaluate('window.location.href')
                if current_url and ('kktix.com/' in current_url or 'kktix.cc/' in current_url):
                    if (current_url.endswith('/') or '/users/' in current_url) and target_url != current_url:
                        await tab.get(target_url)
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        has_redirected = True
            except Exception as redirect_error:
                print(f"跳轉失敗: {redirect_error}")

        except Exception as e:
            print(e)
            pass

    return has_redirected

async def nodriver_kktix_paused_main(tab, url, config_dict):
    show_debug_message = config_dict["advanced"]["verbose"]

    is_url_contain_sign_in = False
    if '/users/sign_in?' in url:
        redirect_needed = await nodriver_kktix_signin(tab, url, config_dict)
        is_url_contain_sign_in = True

        return redirect_needed

    return False

async def nodriver_goto_homepage(driver, config_dict):
    homepage = config_dict["homepage"]
    if 'kktix.c' in homepage:
        # for like human.
        try:
            tab = await driver.get(homepage)
            await tab.get_content()
            await asyncio.sleep(5)
        except Exception as e:
            pass
        

        if len(config_dict["advanced"]["kktix_account"])>0:
            if not 'https://kktix.com/users/sign_in?' in homepage:
                homepage = CONST_KKTIX_SIGN_IN_URL % (homepage)

    if 'famiticket.com' in homepage:
        if len(config_dict["advanced"]["fami_account"])>0:
            homepage = CONST_FAMI_SIGN_IN_URL

    if 'kham.com' in homepage:
        if len(config_dict["advanced"]["kham_account"])>0:
            homepage = CONST_KHAM_SIGN_IN_URL

    if 'ticket.com.tw' in homepage:
        if len(config_dict["advanced"]["ticket_account"])>0:
            homepage = CONST_TICKET_SIGN_IN_URL

    if 'urbtix.hk' in homepage:
        if len(config_dict["advanced"]["urbtix_account"])>0:
            homepage = CONST_URBTIX_SIGN_IN_URL

    if 'cityline.com' in homepage:
        if len(config_dict["advanced"]["cityline_account"])>0:
            homepage = CONST_CITYLINE_SIGN_IN_URL

    if 'hkticketing.com' in homepage:
        if len(config_dict["advanced"]["hkticketing_account"])>0:
            homepage = CONST_HKTICKETING_SIGN_IN_URL

    # https://ticketplus.com.tw/*
    if 'ticketplus.com.tw' in homepage:
        if len(config_dict["advanced"]["ticketplus_account"]) > 1:
            homepage = "https://ticketplus.com.tw/"

    try:
        tab = await driver.get(homepage)
        await tab.get_content()
        await asyncio.sleep(3)
    except Exception as e:
        pass

    tixcraft_family = False
    if 'tixcraft.com' in homepage:
        tixcraft_family = True

    if 'indievox.com' in homepage:
        tixcraft_family = True

    if 'ticketmaster.' in homepage:
        tixcraft_family = True

    if tixcraft_family:
        tixcraft_sid = config_dict["advanced"]["tixcraft_sid"]
        if len(tixcraft_sid) > 1:
            cookies  = await driver.cookies.get_all()
            is_cookie_exist = False
            for cookie in cookies:
                if cookie.name=='SID':
                    cookie.value=tixcraft_sid
                    is_cookie_exist = True
                    break
            if not is_cookie_exist:
                new_cookie = cdp.network.CookieParam("SID",tixcraft_sid, domain="tixcraft.com", path="/", http_only=True, secure=True)
                cookies.append(new_cookie)
            await driver.cookies.set_all(cookies)

    # 處理 ibon 登入
    if 'ibon.com' in homepage:
        # 使用專門的 ibon 登入函數
        login_result = await nodriver_ibon_login(tab, config_dict, driver)

        if config_dict["advanced"]["verbose"]:
            if login_result['success']:
                print("ibon login process completed successfully")
            else:
                print(f"ibon login process failed: {login_result.get('reason', 'unknown')}")
                if 'error' in login_result:
                    print(f"Error details: {login_result['error']}")

        # 不管成功與否，都繼續後續處理，讓使用者手動處理登入問題
        # 這樣可以避免完全中斷搶票流程

    return tab

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
        ticket_price_list = await tab.query_selector_all('div.display-table-row')
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
        input_index = 0  # 追蹤有效 input 的索引

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

        for i, row in enumerate(ticket_price_list):
            row_text = ""
            row_html = ""
            row_input = None
            current_ticket_number = "0"
            try:
                # 使用 JavaScript 一次取得所有資料，避免使用元素物件方法
                result = await tab.evaluate(f'''
                    (function() {{
                        const rows = document.querySelectorAll('div.display-table-row');
                        if (rows[{i}]) {{
                            const row = rows[{i}];
                            const input = row.querySelector('input');
                            return {{
                                html: row.innerHTML,
                                text: row.textContent || row.innerText || "",
                                hasInput: !!input,
                                inputValue: input ? input.value : "0"
                            }};
                        }}
                        return {{ html: "", text: "", hasInput: false, inputValue: "0" }};
                    }})();
                ''')

                # 使用統一解析函數處理返回值
                result = util.parse_nodriver_result(result)
                if result:
                    row_html = result.get('html', '')
                    row_text = util.remove_html_tags(row_html)
                    current_ticket_number = result.get('inputValue', '0')
                    if result.get('hasInput'):
                        row_input = input_index  # 儲存有效 input 的索引
            except Exception as exc:
                is_dom_ready = False
                if show_debug_message:
                    print(f"Error in nodriver_kktix_travel_price_list: {exc}")
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

            # 處理有 input 的票種
            if row_input is not None:
                if show_debug_message:
                    original_text = util.remove_html_tags(result.get('html', '')) if result else ""
                    print(f"票種索引 {i} (input索引 {input_index}): {original_text[:50]}")

                # 檢查票種是否被排除關鍵字過濾掉
                if len(row_text) == 0:
                    if show_debug_message:
                        print(f"  -> 被排除關鍵字過濾，跳過")
                    input_index += 1  # 仍需遞增 input_index
                    continue

                # 只有當票種文字未被排除關鍵字過濾時才處理
                is_match_area = False

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
                    print(f"  -> 是否符合條件: {is_match_area}, 配對代碼: {match_area_code if is_match_area else 'N/A'}")

                if is_match_area:
                    areas.append(row_input)  # 現在儲存的是有效 input 索引
                    if show_debug_message:
                        print(f"  -> 加入選擇清單，input索引: {row_input}")

                    # from top to bottom, match first to break.
                    if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        break

                input_index += 1  # 遞增有效 input 的索引

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
            print("try to set input box value.")

        try:
            # target_area 現在是索引，直接使用
            target_index = target_area

            # 使用 JavaScript 操作，避免使用元素物件方法
            assign_result = await tab.evaluate(f'''
                (function() {{
                    const inputs = document.querySelectorAll('div.display-table-row input');
                    const targetInput = inputs[{target_index}];

                    if (!targetInput) {{
                        return {{ success: false, error: "Input not found", inputCount: inputs.length, targetIndex: {target_index} }};
                    }}

                    // 取得對應的票種名稱，清理多餘空白
                    const parentRow = targetInput.closest('div.display-table-row');
                    let ticketName = "未知票種";
                    if (parentRow) {{
                        ticketName = parentRow.textContent
                            .replace(/\\s+/g, ' ')  // 將多個空白字符替換為單個空格
                            .replace(/\\n/g, ' ')   // 替換換行符
                            .trim();                // 移除前後空白
                    }}

                    const currentValue = targetInput.value;

                    if (currentValue === "0") {{
                        targetInput.focus();
                        targetInput.select();
                        targetInput.value = "{ticket_number_str}";

                        // 更完整的事件觸發
                        targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        targetInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));

                        // 確保 Angular 模型更新
                        if (window.angular) {{
                            const scope = window.angular.element(targetInput).scope();
                            if (scope) {{
                                scope.$apply();
                            }}
                        }}

                        return {{ success: true, assigned: true, value: "{ticket_number_str}", ticketName: ticketName }};
                    }} else {{
                        return {{ success: true, assigned: false, value: currentValue, alreadySet: true, ticketName: ticketName }};
                    }}
                }})();
            ''')

            # 使用統一解析函數處理返回值
            assign_result = util.parse_nodriver_result(assign_result)

            if assign_result and assign_result.get('success') and assign_result.get('assigned'):
                await asyncio.sleep(0.2)

            if assign_result and assign_result.get('success'):
                current_ticket_number = assign_result.get('value', '')
                ticket_name = assign_result.get('ticketName', '未知票種')

                if assign_result.get('assigned'):
                    # 清理票種名稱中的換行符號和多餘空白
                    clean_ticket_name = ' '.join(ticket_name.split())
                    print("assign ticket number:%s to [%s]" % (ticket_number_str, clean_ticket_name))
                    is_ticket_number_assigned = True
                elif assign_result.get('alreadySet'):
                    if show_debug_message:
                        print("value already assigned to [%s]" % ticket_name)
                    is_ticket_number_assigned = True

                if show_debug_message:
                    print(f"🎫 current_ticket_number: {current_ticket_number}")
                    print(f"🎫 selected_ticket_name: {ticket_name}")

                if is_ticket_number_assigned and show_debug_message:
                    print("KKTIX ticket number input completed, skipping verification")
            else:
                if show_debug_message:
                    error_msg = assign_result.get('error', 'Unknown error') if assign_result else 'No result'
                    print(f"Error in nodriver_kktix_assign_ticket_number: {error_msg}")

        except Exception as exc:
            if show_debug_message:
                print(f"Error in nodriver_kktix_assign_ticket_number: {exc}")

    return is_dom_ready, is_ticket_number_assigned, is_need_refresh


async def nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div):
    """增強版驗證碼處理，包含重試機制和人類化延遲"""
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []
    success = False  # 初始化按鈕點擊狀態

    # 批次檢查頁面元素狀態
    elements_check = await tab.evaluate('''
        (function() {
            return {
                hasQuestion: !!document.querySelector('div.custom-captcha-inner p'),
                hasInput: !!document.querySelector('div.custom-captcha-inner > div > div > input'),
                hasButtons: document.querySelectorAll('div.register-new-next-button-area > button').length,
                questionText: document.querySelector('div.custom-captcha-inner p')?.innerText || ''
            };
        })();
    ''')
    elements_check = util.parse_nodriver_result(elements_check)

    is_question_popup = False
    if elements_check and elements_check.get('hasQuestion'):
        question_text = elements_check.get('questionText', '')

        if len(question_text) > 0:
            is_question_popup = True
            write_question_to_file(question_text)

            answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
            if len(answer_list)==0:
                if config_dict["advanced"]["auto_guess_options"]:
                    answer_list = util.get_answer_list_from_question_string(None, question_text)

            inferred_answer_string = ""
            for answer_item in answer_list:
                if not answer_item in fail_list:
                    inferred_answer_string = answer_item
                    break

            if len(answer_list) > 0:
                answer_list = list(dict.fromkeys(answer_list))

            if show_debug_message:
                print("inferred_answer_string:", inferred_answer_string)
                print("question_text:", question_text)
                print("answer_list:", answer_list)
                print("fail_list:", fail_list)

            # 增強版答案填寫流程，包含重試機制
            if len(inferred_answer_string) > 0 and elements_check.get('hasInput'):
                success = False
                max_retries = 3

                for retry_count in range(max_retries):
                    if show_debug_message and retry_count > 0:
                        print(f"Captcha filling retry {retry_count}/{max_retries}")

                    try:
                        # 人類化延遲：0.3-1秒隨機延遲
                        human_delay = random.uniform(0.3, 1.0)
                        await tab.sleep(human_delay)

                        # 填寫驗證碼答案
                        fill_result = await tab.evaluate(f'''
                            (function() {{
                                const input = document.querySelector('div.custom-captcha-inner > div > div > input');
                                if (!input) {{
                                    return {{ success: false, error: "Input not found" }};
                                }}

                                // 確保輸入框可見和可用
                                if (input.disabled || input.readOnly) {{
                                    return {{ success: false, error: "Input is disabled or readonly" }};
                                }}

                                // 模擬人類打字
                                input.focus();
                                input.value = "";

                                const answer = "{inferred_answer_string}";
                                for (let i = 0; i < answer.length; i++) {{
                                    input.value += answer[i];
                                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}

                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                input.blur();

                                return {{
                                    success: true,
                                    value: input.value,
                                    focused: document.activeElement === input
                                }};
                            }})();
                        ''')

                        fill_result = util.parse_nodriver_result(fill_result)

                        if fill_result and fill_result.get('success'):
                            if show_debug_message:
                                print(f"Captcha answer filled successfully: {inferred_answer_string}")

                            # 短暫延遲後點擊按鈕
                            button_delay = random.uniform(0.5, 1.2)
                            await tab.sleep(button_delay)

                            # 點擊下一步按鈕
                            button_click_success = await nodriver_kktix_press_next_button(tab, config_dict)

                            if button_click_success:
                                success = True
                                # 最終延遲
                                final_delay = random.uniform(0.75, 1.5)
                                await tab.sleep(final_delay)

                                fail_list.append(inferred_answer_string)
                                break
                            else:
                                if show_debug_message:
                                    print("Button click failed, retrying...")
                        else:
                            error_msg = fill_result.get('error', 'Unknown error') if fill_result else 'No result'
                            if show_debug_message:
                                print(f"Input filling failed: {error_msg}")

                    except Exception as exc:
                        if show_debug_message:
                            print(f"Captcha retry {retry_count + 1} failed: {exc}")

                    # 重試前的等待
                    if not success and retry_count < max_retries - 1:
                        retry_delay = random.uniform(0.8, 1.5)
                        await tab.sleep(retry_delay)

                if not success and show_debug_message:
                    print("All captcha filling attempts failed")

    return fail_list, is_question_popup, success

async def wait_for_kktix_element(tab, selector, timeout=10, check_visible=True):
    """等待 KKTIX 元素載入並確保可見，參考 NoDriver API 指南"""
    try:
        result = await tab.evaluate(f'''
            (function() {{
                return new Promise((resolve) => {{
                    let retryCount = 0;
                    const maxRetries = {timeout * 5};  // 每200ms檢查一次

                    function checkElement() {{
                        const element = document.querySelector('{selector}');
                        if (element) {{
                            let isVisible = true;

                            // 檢查可見性（如果需要）
                            if ({str(check_visible).lower()}) {{
                                const rect = element.getBoundingClientRect();
                                const style = window.getComputedStyle(element);
                                isVisible = rect.width > 0 && rect.height > 0 &&
                                          style.display !== 'none' &&
                                          style.visibility !== 'hidden' &&
                                          style.opacity !== '0';
                            }}

                            if (isVisible) {{
                                resolve({{
                                    success: true,
                                    found: true,
                                    visible: isVisible,
                                    dimensions: element.getBoundingClientRect(),
                                    retries: retryCount
                                }});
                                return;
                            }}
                        }}

                        if (retryCount < maxRetries) {{
                            retryCount++;
                            setTimeout(checkElement, 200);
                        }} else {{
                            resolve({{
                                success: false,
                                error: "Timeout waiting for element",
                                selector: '{selector}',
                                timeout: {timeout},
                                retries: retryCount
                            }});
                        }}
                    }}

                    checkElement();
                }});
            }})();
        ''')

        # 解析結果
        result = util.parse_nodriver_result(result)
        return result

    except Exception as exc:
        return {
            'success': False,
            'error': f'Exception in wait_for_kktix_element: {exc}',
            'selector': selector
        }

async def debug_kktix_page_state(tab, show_debug=True):
    """收集 KKTIX 頁面狀態供除錯，參考 NoDriver API 指南"""
    try:
        state = await tab.evaluate('''
            (function() {
                // 基本頁面資訊
                const basicInfo = {
                    url: window.location.href,
                    title: document.title,
                    readyState: document.readyState,
                    documentHeight: document.documentElement.scrollHeight,
                    viewportHeight: window.innerHeight
                };

                // KKTIX 特定元素檢查
                const kktixElements = {
                    hasRegistrationDiv: !!document.querySelector('#registrationsNewApp'),
                    hasTicketAreas: document.querySelectorAll('div.display-table-row').length,
                    hasPriceList: document.querySelectorAll('.display-table-row').length
                };

                // 驗證碼相關元素
                const captchaElements = {
                    hasQuestion: !!document.querySelector('div.custom-captcha-inner p'),
                    questionText: document.querySelector('div.custom-captcha-inner p')?.innerText || '',
                    hasInput: !!document.querySelector('div.custom-captcha-inner input'),
                    inputValue: document.querySelector('div.custom-captcha-inner input')?.value || '',
                    inputDisabled: document.querySelector('div.custom-captcha-inner input')?.disabled || false
                };

                // 按鈕和表單元素
                const formElements = {
                    nextButtons: document.querySelectorAll('div.register-new-next-button-area > button').length,
                    checkboxes: document.querySelectorAll('input[type="checkbox"]').length,
                    radioButtons: document.querySelectorAll('input[type="radio"]').length,
                    textInputs: document.querySelectorAll('input[type="text"]').length,
                    submitButtons: document.querySelectorAll('input[type="submit"], button[type="submit"]').length
                };

                // 錯誤訊息檢查 - 更精確地檢查實際的錯誤訊息
                const errorMessages = {
                    hasErrorMessages: !!document.querySelector('.alert-danger, .error, .warning'),
                    errorText: document.querySelector('.alert-danger, .error, .warning')?.innerText || '',
                    soldOut: !!document.querySelector('.alert-danger, .error')?.innerText?.includes('售完') ||
                            !!document.querySelector('.alert-danger, .error')?.innerText?.includes('已售完') ||
                            !!document.querySelector('.sold-out, .unavailable'),
                    notYetOpen: !!document.querySelector('.alert-danger, .error')?.innerText?.includes('未開賣') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('尚未開始') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('即將開賣')
                };

                // 頁面載入狀態
                const loadingState = {
                    hasLoadingSpinner: !!document.querySelector('.loading, .spinner, [class*="load"]'),
                    scriptsLoaded: document.scripts.length,
                    stylesheetsLoaded: document.styleSheets.length,
                    imagesLoaded: Array.from(document.images).filter(img => img.complete).length,
                    totalImages: document.images.length
                };

                return {
                    timestamp: new Date().toISOString(),
                    basic: basicInfo,
                    kktix: kktixElements,
                    captcha: captchaElements,
                    forms: formElements,
                    errors: errorMessages,
                    loading: loadingState
                };
            })();
        ''')

        # 解析結果
        state = util.parse_nodriver_result(state)

        if show_debug and state:
            print("=== KKTIX Page Debug State ===")
            print(f"URL: {state.get('basic', {}).get('url', 'N/A')}")
            print(f"Ready State: {state.get('basic', {}).get('readyState', 'N/A')}")
            print(f"Registration Div: {state.get('kktix', {}).get('hasRegistrationDiv', False)}")
            print(f"Ticket Areas: {state.get('kktix', {}).get('hasTicketAreas', 0)}")
            print(f"Captcha Question: {state.get('captcha', {}).get('hasQuestion', False)}")
            if state.get('captcha', {}).get('questionText'):
                print(f"Question Text: {state.get('captcha', {}).get('questionText', '')[:50]}...")
            print(f"Next Buttons: {state.get('forms', {}).get('nextButtons', 0)}")
            print(f"Error Messages: {state.get('errors', {}).get('hasErrorMessages', False)}")
            if state.get('errors', {}).get('soldOut'):
                print("🔴 Sold Out detected")
            if state.get('errors', {}).get('notYetOpen'):
                print("Not yet open detected")
            print("=" * 30)

        return state

    except Exception as exc:
        error_state = {
            'success': False,
            'error': f'Exception in debug_kktix_page_state: {exc}',
            'timestamp': datetime.now().isoformat()
        }
        if show_debug:
            print(f"Debug failed: {exc}")
        return error_state

#   : This is for case-2 next button.
async def nodriver_kktix_events_press_next_button(tab, config_dict=None):
    """點擊活動頁面的「立即購票」按鈕"""
    show_debug_message = config_dict["advanced"]["verbose"] if config_dict else False
    try:
        result = await tab.evaluate('''
            (function() {
                const button = document.querySelector('.tickets > a.btn-point');
                if (button) {
                    button.scrollIntoView({ behavior: 'instant', block: 'center' });
                    button.click();
                    return { success: true, message: '成功點擊立即購票按鈕' };
                } else {
                    return { success: false, message: '找不到立即購票按鈕' };
                }
            })()
        ''')

        result = util.parse_nodriver_result(result)

        if result and result.get('success'):
            return True
        else:
            return False

    except Exception as exc:
        print(f"Error clicking events next button: {exc}")
        return False

async def nodriver_kktix_press_next_button(tab, config_dict=None):
    """使用 JavaScript 點擊下一步按鈕，包含重試和等待機制"""
    show_debug_message = config_dict["advanced"]["verbose"] if config_dict else False

    # 重試機制：最多嘗試 3 次
    for retry_count in range(3):
        try:
            # 如果不是第一次嘗試，等待一下
            if retry_count > 0:
                await asyncio.sleep(0.5)
                if show_debug_message:
                    print(f"KKTIX 按鈕點擊重試 {retry_count + 1}/3")

            result = await tab.evaluate('''
                (function() {
                    const buttons = document.querySelectorAll('div.register-new-next-button-area > button');
                    if (buttons.length === 0) {
                        return { success: false, error: 'No buttons found', buttonCount: 0 };
                    }

                    // 點擊最後一個按鈕
                    const targetButton = buttons[buttons.length - 1];

                    // 詳細檢查按鈕狀態
                    const buttonText = targetButton.innerText || targetButton.textContent || '';
                    const isDisabled = targetButton.disabled ||
                                      targetButton.classList.contains('disabled') ||
                                      targetButton.getAttribute('disabled') !== null;

                    // 檢查是否正在處理中
                    const isProcessing = buttonText.includes('查詢空位中') ||
                                        buttonText.includes('處理中') ||
                                        buttonText.includes('請稍候') ||
                                        buttonText.includes('請勿重新整理');

                    if (isDisabled) {
                        if (isProcessing) {
                            return {
                                success: true,
                                processing: true,
                                error: 'Processing seats',
                                buttonCount: buttons.length,
                                buttonText: buttonText
                            };
                        } else {
                            return {
                                success: false,
                                error: 'Button is disabled',
                                buttonCount: buttons.length,
                                buttonText: buttonText
                            };
                        }
                    }

                    // 模擬真實點擊事件
                    const event = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });

                    targetButton.scrollIntoView({ behavior: 'instant', block: 'center' });
                    targetButton.focus();
                    targetButton.dispatchEvent(event);

                    return {
                        success: true,
                        clicked: true,
                        buttonText: targetButton.innerText || targetButton.textContent || '',
                        buttonCount: buttons.length
                    };
                })();
            ''')

            # 使用統一解析函數處理返回值
            result = util.parse_nodriver_result(result)

            if result and result.get('success'):
                button_text = result.get('buttonText', '').strip()

                # 檢查是否是處理中狀態
                if result.get('processing'):
                    if show_debug_message:
                        print(f"KKTIX processing: [{button_text}]")

                    # 等待較長時間給 KKTIX 處理
                    await asyncio.sleep(1.5)

                    try:
                        # 檢查是否已跳轉到訂單頁面
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            if show_debug_message:
                                print(f"Processing completed, redirected to order page")
                            return True
                    except Exception:
                        pass

                    # 如果還沒跳轉，可能還在處理，返回成功
                    return True
                else:
                    # 正常的按鈕點擊成功
                    if show_debug_message:
                        print(f"KKTIX button click successful: [{button_text}]")

                    # 等待頁面處理並檢查是否跳轉
                    await asyncio.sleep(0.8)  # 給 KKTIX 伺服器時間處理

                    try:
                        # 檢查是否已跳轉到訂單頁面
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            if show_debug_message:
                                print(f"Button click completed, redirected to order page")
                            return True
                    except Exception:
                        pass

                    # 如果沒有跳轉，等待原有時間並返回成功
                    await asyncio.sleep(0.2)
                    return True
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                button_text = result.get('buttonText', '') if result else ''
                if show_debug_message:
                    print(f"KKTIX button click failed: {error_msg} [{button_text}]")

                # 如果是按鈕被禁用或處理中，檢查是否已跳轉
                if 'disabled' in error_msg.lower() or 'processing' in error_msg.lower():
                    try:
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            if show_debug_message:
                                print(f"System processing but already redirected to order page, considered successful")
                            return True
                    except Exception:
                        pass

                    # 如果是處理中狀態，等待較長時間再重試
                    if 'processing' in error_msg.lower():
                        await asyncio.sleep(1.0)

                    # 繼續重試
                    continue

        except Exception as exc:
            if show_debug_message:
                print(f"KKTIX 按鈕點擊例外 (重試 {retry_count + 1}/3): {exc}")

    # 所有重試都失敗
    if show_debug_message:
        print("KKTIX button click finally failed after 3 retries")
    return False


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
        registrationsNewApp_div = await tab.query_selector('#registrationsNewApp')
    except Exception as exc:
        pass
        #print("find input fail:", exc)

    # part 2: assign ticket number
    is_ticket_number_assigned = False
    if not registrationsNewApp_div is None:
        is_dom_ready = True
        is_need_refresh = False

        # 檢查頁面狀態，如果偵測到售罄或未開賣，設定重新載入標記
        try:
            page_state_raw = await tab.evaluate('''
                () => {
                    // 只檢查票券區域內的售罄狀態，避免誤判
                    const ticketArea = document.querySelector('#registrationsNewApp') || document.body;
                    const areaHTML = ticketArea.innerHTML;

                    const soldOut = areaHTML.includes('售完') ||
                                   areaHTML.includes('Sold Out') ||
                                   areaHTML.includes('已售完') ||
                                   areaHTML.includes('sold out');

                    const notYetOpen = areaHTML.includes('未開賣') ||
                                      areaHTML.includes('尚未開始') ||
                                      areaHTML.includes('即將開賣') ||
                                      areaHTML.includes('coming soon');

                    return { soldOut, notYetOpen };
                }
            ''')

            # 使用統一的結果處理函數
            page_state = util.parse_nodriver_result(page_state_raw)

            if page_state and (page_state.get('soldOut') or page_state.get('notYetOpen')):
                is_need_refresh = True
                if show_debug_message:
                    status = "售罄" if page_state.get('soldOut') else "未開賣"
                    print(f"KKTIX 偵測到 {status} 狀態，將重新載入頁面")
        except Exception as exc:
            if show_debug_message:
                print(f"檢查頁面狀態失敗: {exc}")

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
            is_dom_ready, is_ticket_number_assigned, is_need_refresh = await nodriver_kktix_assign_ticket_number(tab, config_dict, "")

        if is_dom_ready:
            # part 3: captcha
            if is_ticket_number_assigned:
                if config_dict["advanced"]["play_sound"]["ticket"]:
                    if not played_sound_ticket:
                        play_sound_while_ordering(config_dict)
                    played_sound_ticket = True

                # 收集除錯資訊（僅在 debug 模式下）
                if show_debug_message:
                    debug_state = await debug_kktix_page_state(tab, show_debug_message)

                # whole event question.
                fail_list, is_question_popup, button_clicked_in_captcha = await nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div)

                # single option question
                if not is_question_popup:
                    # no captcha text popup, goto next page.
                    control_text = await nodriver_get_text_by_selector(tab, 'div > div.code-input > div.control-group > label.control-label', 'innerText')
                    if show_debug_message:
                        print("control_text:", control_text)

                    if len(control_text) > 0:
                        input_text_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > input[type="text"]'
                        input_text_element = None
                        try:
                            input_text_element = await tab.query_selector(input_text_css)
                        except Exception as exc:
                            #print(exc)
                            pass
                        if input_text_element is None:
                            radio_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > input[type="radio"]'
                            try:
                                radio_element = await tab.query_selector(radio_css)
                                if radio_element:
                                    print("found radio")
                                    joined_button_css = 'div > div.code-input > div.control-group > div.controls > label[ng-if] > span[ng-if] > a[ng-href="#"]'
                                    joined_element = await tab.query_selector(joined_button_css)
                                    if joined_element:
                                        control_text = ""
                                        print("member joined")
                            except Exception as exc:
                                print(exc)
                                pass

                    if len(control_text) == 0:
                        # 檢查是否在驗證碼處理時已經點擊過按鈕
                        if button_clicked_in_captcha:
                            if show_debug_message:
                                print("Button already clicked during captcha processing, skipping duplicate click")
                        else:
                            # 檢查是否已經跳轉到成功頁面，避免重複點擊
                            try:
                                current_url = await tab.evaluate('window.location.href')
                                if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                                    if show_debug_message:
                                        print("Already redirected to order page, skipping button click")
                                else:
                                    click_ret = await nodriver_kktix_press_next_button(tab, config_dict)
                            except Exception as exc:
                                # 如果檢查失敗，還是嘗試點擊
                                click_ret = await nodriver_kktix_press_next_button(tab, config_dict)
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
                        await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return fail_list, played_sound_ticket

def check_kktix_got_ticket(url, config_dict, show_debug_message=False):
    """檢查是否已成功取得 KKTIX 票券

    Args:
        url: 當前頁面 URL
        config_dict: 設定字典
        show_debug_message: 是否顯示除錯訊息

    Returns:
        bool: True 表示已成功取得票券
    """
    is_kktix_got_ticket = False

    if '/events/' in url and '/registrations/' in url and "-" in url:
        if not '/registrations/new' in url:
            if not 'https://kktix.com/users/sign_in?' in url:
                is_kktix_got_ticket = True
                if show_debug_message:
                    print(f"偵測到搶票成功頁面: {url}")

    if is_kktix_got_ticket:
        if '/events/' in config_dict["homepage"] and '/registrations/' in config_dict["homepage"] and "-" in config_dict["homepage"]:
            if len(url.split('/')) >= 7:
                if len(config_dict["homepage"].split('/')) >= 7:
                    if url.split('/')[4] == config_dict["homepage"].split('/')[4]:
                        is_kktix_got_ticket = False
                        if show_debug_message:
                            print("重複進入相同活動的訂單頁面，跳過處理")

    return is_kktix_got_ticket

async def nodriver_kktix_main(tab, url, config_dict):
    global kktix_dict
    show_debug_message = config_dict["advanced"]["verbose"]

    if not 'kktix_dict' in globals():
        kktix_dict = {}
        kktix_dict["fail_list"]=[]
        kktix_dict["start_time"]=None
        kktix_dict["done_time"]=None
        kktix_dict["elapsed_time"]=None
        kktix_dict["is_popup_checkout"] = False
        kktix_dict["played_sound_ticket"] = False
        kktix_dict["played_sound_order"] = False
        kktix_dict["got_ticket_detected"] = False
        kktix_dict["success_actions_done"] = False

    is_url_contain_sign_in = False
    if '/users/sign_in?' in url:
        redirect_needed = await nodriver_kktix_signin(tab, url, config_dict)
        is_url_contain_sign_in = True

        if redirect_needed:
            await asyncio.sleep(3)
            try:
                url = await tab.evaluate('window.location.href')
                is_url_contain_sign_in = False
                await asyncio.sleep(1)
            except Exception as exc:
                print(f"取得跳轉後 URL 失敗: {exc}")

    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            kktix_dict["start_time"] = time.time()

            is_dom_ready = False
            try:
                html_body = await tab.get_content()
                #print("html_body:",len(html_body))
                if html_body:
                    if len(html_body) > 10240:
                        if "registrationsNewApp" in html_body:
                            if not "{{'new.i_read_and_agree_to'" in html_body:
                                is_dom_ready = True
            except Exception as exc:
                #print(exc)
                pass

            if not is_dom_ready:
                kktix_dict["fail_list"] = []
                kktix_dict["played_sound_ticket"] = False
            else:
                # 勾選同意條款 - 使用精確的 ID 選擇器
                is_finish_checkbox_click = await nodriver_check_checkbox(tab, '#person_agree_terms:not(:checked)')

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
                # 檢查是否需要自動重載（Chrome 擴充功能未啟用時）
                if not config_dict["advanced"]["chrome_extension"]:
                    await nodriver_kktix_reg_auto_reload(tab, config_dict)

                if config_dict["kktix"]["auto_press_next_step_button"]:
                    # 自動點擊「立即購票」按鈕
                    await nodriver_kktix_events_press_next_button(tab, config_dict)

            # reset answer fail list.
            kktix_dict["fail_list"] = []
            kktix_dict["played_sound_ticket"] = False

    # 檢查是否已經偵測過成功頁面，避免重複偵測
    is_kktix_got_ticket = False
    if not kktix_dict["got_ticket_detected"]:
        is_kktix_got_ticket = check_kktix_got_ticket(url, config_dict, show_debug_message)
        if is_kktix_got_ticket:
            kktix_dict["got_ticket_detected"] = True
    elif kktix_dict["got_ticket_detected"]:
        # 已經偵測過成功頁面，直接設定為 True 但不重複輸出
        is_kktix_got_ticket = True

    is_quit_bot = False
    if is_kktix_got_ticket:
        # 搶票成功，設定結束標記
        is_quit_bot = True

        # 只在第一次偵測成功時執行動作
        if not kktix_dict["success_actions_done"]:
            if not kktix_dict["start_time"] is None:
                if not kktix_dict["done_time"] is None:
                    bot_elapsed_time = kktix_dict["done_time"] - kktix_dict["start_time"]
                    if kktix_dict["elapsed_time"] != bot_elapsed_time:
                        print("搶票完成，耗時: {:.3f} 秒".format(bot_elapsed_time))
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
                        # Mask account information to protect privacy
                        if len(kktix_account) > 5:
                            masked_account = kktix_account[:3] + "***" + kktix_account[-2:]
                        else:
                            masked_account = "***"
                        print("搶票成功, 帳號:", masked_account)

                        script_name = "chrome_tixcraft"
                        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_NODRIVER:
                            script_name = "nodriver_tixcraft"

                        threading.Thread(target=util.launch_maxbot, args=(script_name,"", url, kktix_account, kktix_password,"","false",)).start()
                        #driver.quit()
                        #sys.exit()

                    is_event_page = False
                    if len(url.split('/'))>=7:
                        is_event_page = True
                    if is_event_page:
                        # 使用改良的訂單確認按鈕功能
                        confirm_clicked = await nodriver_kktix_confirm_order_button(tab, config_dict)

                        if confirm_clicked:
                            domain_name = url.split('/')[2]
                            checkout_url = "https://%s/account/orders" % (domain_name)
                            print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                            webbrowser.open_new(checkout_url)

                    kktix_dict["is_popup_checkout"] = True

            # 標記動作已完成，避免重複執行
            kktix_dict["success_actions_done"] = True
    else:
        kktix_dict["is_popup_checkout"] = False
        kktix_dict["played_sound_order"] = False

    return is_quit_bot

async def nodriver_kktix_confirm_order_button(tab, config_dict):
    """
    KKTIX 訂單確認按鈕自動點擊功能
    對應 Chrome 版本的 kktix_confirm_order_button()
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    ret = False

    try:
        # 尋找訂單確認按鈕: div.form-actions a.btn-primary
        confirm_button = await tab.query_selector('div.form-actions a.btn-primary')
        if confirm_button:
            # 檢查按鈕是否可點擊
            is_enabled = await tab.evaluate('''
                (button) => {
                    return button && !button.disabled && button.offsetParent !== null;
                }
            ''', confirm_button)

            if is_enabled:
                await confirm_button.click()
                ret = True
                if show_debug_message:
                    print("KKTIX 訂單確認按鈕已點擊")
            elif show_debug_message:
                print("KKTIX 訂單確認按鈕存在但不可點擊")
        elif show_debug_message:
            print("未找到 KKTIX 訂單確認按鈕")

    except Exception as exc:
        if show_debug_message:
            print(f"KKTIX 訂單確認按鈕點擊失敗: {exc}")

    return ret

async def nodriver_kktix_double_check_all_text_value(tab, config_dict, ticket_number):
    """
    KKTIX 雙重檢查票數輸入功能
    對應 Chrome 版本的 kktix_double_check_all_text_value()
    確認票數輸入正確後才自動按下一步
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    is_do_press_next_button = False

    try:
        # 檢查所有票數輸入框的值 - 使用與填入相同的選擇器
        ticket_values = await tab.evaluate('''
            () => {
                const inputs = document.querySelectorAll('div.display-table-row input');
                const values = [];
                inputs.forEach(input => {
                    const value = input.value ? input.value.trim() : '';
                    if (value.length > 0 && value !== '0') {
                        values.push(value);
                    }
                });
                return values;
            }
        ''')

        if ticket_values:
            target_ticket_str = str(ticket_number)
            for current_value in ticket_values:
                if current_value == target_ticket_str:
                    if show_debug_message:
                        print(f"KKTIX ticket count check passed: found target ticket count {target_ticket_str}")
                    is_do_press_next_button = True
                    break

            if show_debug_message and not is_do_press_next_button:
                print(f"KKTIX ticket count check warning: target {target_ticket_str}, actual values {ticket_values}")
        elif show_debug_message:
            # 加入更詳細的除錯資訊，確保數量正確處理
            try:
                input_count_raw = await tab.evaluate('() => document.querySelectorAll("div.display-table-row input").length')
                input_count = util.parse_nodriver_result(input_count_raw)
                input_count = input_count if isinstance(input_count, int) else 0
                print(f"KKTIX ticket count check warning: no valid ticket values found (found {input_count} input fields)")
            except Exception as exc:
                print(f"KKTIX ticket count check warning: unable to get input field count ({exc})")

    except Exception as exc:
        if show_debug_message:
            print(f"KKTIX 票數檢查失敗: {exc}")

    return is_do_press_next_button

async def nodriver_kktix_check_register_status(tab, config_dict):
    """
    KKTIX 註冊狀態檢查功能
    對應 Chrome 版本的 kktix_check_register_status()
    使用 JavaScript 呼叫 KKTIX API 檢查票券狀態
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    is_need_refresh = False

    try:
        # 取得當前 URL 來構建 API 請求
        current_url = await tab.evaluate('() => window.location.href')

        # 使用 JavaScript 呼叫 KKTIX API 檢查狀態
        status_result = await tab.evaluate('''
            async () => {
                try {
                    const currentUrl = window.location.href;
                    const urlParts = currentUrl.split('/');

                    // 從 URL 提取 event_id
                    let eventId = '';
                    const eventsIndex = urlParts.findIndex(part => part === 'events');
                    if (eventsIndex !== -1 && eventsIndex + 1 < urlParts.length) {
                        eventId = urlParts[eventsIndex + 1];
                    }

                    if (!eventId) {
                        return { success: false, error: 'Cannot extract event ID from URL' };
                    }

                    // 構建 API URL
                    const apiUrl = `https://kktix.com/events/${eventId}.json`;

                    // 發送 API 請求
                    const response = await fetch(apiUrl, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    if (!response.ok) {
                        return { success: false, error: `API request failed: ${response.status}` };
                    }

                    const data = await response.json();

                    // 檢查票券狀態
                    const tickets = data.event?.tickets || [];
                    const statusList = [];

                    tickets.forEach(ticket => {
                        if (ticket.inventory_id) {
                            statusList.push({
                                name: ticket.name,
                                inventory_id: ticket.inventory_id,
                                status: ticket.status
                            });
                        }
                    });

                    return { success: true, tickets: statusList };

                } catch (error) {
                    return { success: false, error: error.message };
                }
            }
        ''')

        if status_result and status_result.get('success'):
            tickets = status_result.get('tickets', [])
            if tickets:
                # 檢查是否有售罄或即將開賣的票券
                for ticket in tickets:
                    status = ticket.get('status', '')
                    ticket_name = ticket.get('name', '')

                    if status in ['OUT_OF_STOCK', 'COMING_SOON', 'SOLD_OUT']:
                        if show_debug_message:
                            print(f"KKTIX 狀態檢查: {ticket_name} - {status}")
                        is_need_refresh = True
                        break

                if show_debug_message and not is_need_refresh:
                    print("KKTIX 狀態檢查: 票券狀態正常，無需重新載入")
            elif show_debug_message:
                print("KKTIX 狀態檢查: 未找到票券資訊")
        else:
            error_msg = status_result.get('error', '未知錯誤') if status_result else '無回應'
            if show_debug_message:
                print(f"KKTIX 狀態檢查失敗: {error_msg}")

    except Exception as exc:
        if show_debug_message:
            print(f"KKTIX 狀態檢查例外: {exc}")

    return is_need_refresh

async def nodriver_kktix_reg_auto_reload(tab, config_dict):
    """
    KKTIX 自動重載功能
    對應 Chrome 版本的 kktix_reg_auto_reload()
    當票券售罄時自動重新載入頁面
    """
    show_debug_message = config_dict["advanced"]["verbose"]
    is_need_reload = False

    try:
        # 使用註冊狀態檢查來決定是否需要重新載入
        is_need_reload = await nodriver_kktix_check_register_status(tab, config_dict)

        if is_need_reload:
            if show_debug_message:
                print("KKTIX 自動重載: 偵測到票券售罄，準備重新載入頁面")

            # 重新載入頁面
            await tab.reload()

            # 等待頁面載入完成
            await asyncio.sleep(2)

            if show_debug_message:
                print("KKTIX 自動重載: 頁面重新載入完成")

    except Exception as exc:
        if show_debug_message:
            print(f"KKTIX 自動重載失敗: {exc}")

    return is_need_reload

async def nodriver_tixcraft_home_close_window(tab):
    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = await tab.query_selector('#onetrust-accept-btn-handler')
        if accept_all_cookies_btn:
            accept_all_cookies_btn.click()
    except Exception as exc:
        #print(exc)
        pass

async def nodriver_get_text_by_selector(tab, my_css_selector, attribute='innerHTML'):
    div_text = ""
    try:
        div_element = await tab.query_selector(my_css_selector)
        if div_element:
            #js_attr = await div_element.get_js_attributes()
            div_text = await div_element.get_html()
            
            # only this case to remove tags
            if attribute=="innerText":
                div_text = util.remove_html_tags(div_text)
    except Exception as exc:
        print("find verify textbox fail")
        pass

    return div_text

async def nodriver_tixcraft_redirect(tab, url):
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
                await tab.get(entry_url)
                ret = True
            except Exception as exec1:
                pass
    return ret

async def nodriver_ticketmaster_promo(tab, config_dict, fail_list):
    question_selector = '#promoBox'
    return nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector)

async def nodriver_tixcraft_verify(tab, config_dict, fail_list):
    question_selector = '.zone-verify'
    return nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector)

async def nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    answer_list = []

    question_text = await nodriver_get_text_by_selector(tab, question_selector, 'innerText')
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

async def nodriver_tixcraft_date_auto_select(tab, url, config_dict, domain_name):
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # read config
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    find_ticket_text_list = ['立即訂購','Find tickets', 'Start ordering','お申込みへ進む']

    game_name = ""
    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    check_game_detail = "/activity/game/%s" % (game_name,) in url

    area_list = None
    if check_game_detail:
        try:
            area_list = await tab.query_selector_all('#gameList > table > tbody > tr')
        except:
            pass

    # Language detection for coming soon
    is_coming_soon = False
    coming_soon_conditions = {
        'en-US': [' day(s)', ' hrs.',' min',' sec',' till sale starts!','0',':','/'],
        'zh-TW': ['開賣','剩餘',' 天',' 小時',' 分鐘',' 秒','0',':','/','20'],
        'ja': ['発売開始', ' 日', ' 時間',' 分',' 秒','0',':','/','20']
    }

    html_lang = "en-US"
    try:
        html_body = await tab.evaluate('document.documentElement.outerHTML')
        if html_body and '<head' in html_body:
            html_lang = html_body.split('<head')[0].split('"')[1]
    except:
        pass

    coming_soon_condictions_list = coming_soon_conditions.get(html_lang, coming_soon_conditions['en-US'])

    matched_blocks = None
    formated_area_list = None

    if area_list and len(area_list) > 0:
        # 移除：過度詳細的除錯訊息
        formated_area_list = []
        formated_area_list_text = []
        for row in area_list:
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except:
                break

            if row_text and not util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                # Check coming soon
                if all(cond in row_text for cond in coming_soon_condictions_list):
                    is_coming_soon = True
                    if auto_reload_coming_soon_page_enable:
                        break

                # Check if row has ticket text
                row_is_enabled = any(text in row_text for text in find_ticket_text_list)

                # Check sold out
                if row_is_enabled and pass_date_is_sold_out_enable:
                    for sold_out_item in sold_out_text_list:
                        if sold_out_item in row_text[-(len(sold_out_item)+5):]:
                            row_is_enabled = False
                            # 移除：售完訊息過度詳細
                            break

                if row_is_enabled:
                    formated_area_list.append(row)
                    formated_area_list_text.append(row_text)
                    # 移除：可用場次訊息過度詳細

        if not date_keyword:
            matched_blocks = formated_area_list
        else:
            # Keyword matching
            matched_blocks = []
            try:
                import json
                import re
                keyword_array = json.loads("[" + date_keyword + "]")
                if show_debug_message:
                    print(f"date_keyword array: {keyword_array}")

                for i, row_text in enumerate(formated_area_list_text):
                    # Normalize spaces for better matching
                    normalized_row_text = re.sub(r'\s+', ' ', row_text)

                    for keyword_item_set in keyword_array:
                        is_match = False
                        if isinstance(keyword_item_set, str):
                            # Normalize keyword spaces too
                            normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
                            is_match = normalized_keyword in normalized_row_text
                            if show_debug_message:
                                if is_match:
                                    print(f"matched keyword '{keyword_item_set}' in row: {row_text[:60]}...")
                                elif normalized_keyword != keyword_item_set:
                                    # Check original too for debugging
                                    if keyword_item_set in row_text:
                                        print(f"keyword would match without normalization")
                        elif isinstance(keyword_item_set, list):
                            # Normalize all keywords in list
                            normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
                            is_match = all(kw in normalized_row_text for kw in normalized_keywords)
                            if show_debug_message and is_match:
                                print(f"matched all keywords {keyword_item_set} in row: {row_text[:60]}...")

                        if is_match:
                            matched_blocks.append(formated_area_list[i])
                            break
            except Exception as e:
                if show_debug_message:
                    print(f"keyword parsing error: {e}")
                matched_blocks = formated_area_list

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    is_date_clicked = False

    # 移除：內部選擇細節過度詳細

    if target_area:
        # Priority: button with data-href (tixcraft) > regular link > regular button
        try:
            # For tixcraft - use JavaScript to find button and get data-href
            data_href = await tab.evaluate('''
                (function() {
                    const buttons = document.querySelectorAll('button[data-href]');
                    for (let button of buttons) {
                        if (button.getAttribute('data-href')) {
                            return button.getAttribute('data-href');
                        }
                    }
                    return null;
                })();
            ''')

            # 解析結果
            data_href = util.util.parse_nodriver_result(data_href)

            if data_href:
                # 保留關鍵導航訊息，但簡化
                if show_debug_message:
                    print("clicking button")
                await tab.get(data_href)
                is_date_clicked = True
        except Exception as e:
            if show_debug_message:
                print(f"button data-href error: {e}")

        # For other platforms - regular link or button click
        if not is_date_clicked:
            try:
                # Try link first (ticketmaster, etc)
                link = await target_area.query_selector('a[href]')
                if link:
                    if show_debug_message:
                        print("clicking link")
                    await link.click()
                    is_date_clicked = True
                else:
                    # Try regular button
                    button = await target_area.query_selector('button')
                    if button:
                        # 移除重複的 clicking button 訊息
                        await button.click()
                        is_date_clicked = True
            except Exception as e:
                if show_debug_message:
                    print(f"click error: {e}")

    return is_date_clicked

async def nodriver_tixcraft_area_auto_select(tab, url, config_dict):
    import json

    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    try:
        el = await tab.query_selector('.zone')
    except:
        return

    if not el:
        return

    is_need_refresh = False
    matched_blocks = None

    if area_keyword:
        try:
            area_keyword_array = json.loads("[" + area_keyword + "]")
        except:
            area_keyword_array = []

        for area_keyword_item in area_keyword_array:
            is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, area_keyword_item)
            if not is_need_refresh:
                break
    else:
        is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, "")

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if target_area:
        try:
            await target_area.click()
        except:
            try:
                await target_area.evaluate('el => el.click()')
            except:
                pass

    # Auto refresh if needed
    if is_need_refresh:
        try:
            await tab.reload()
        except:
            pass

        interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
        if interval > 0:
            import time
            await asyncio.sleep(interval)

async def nodriver_get_tixcraft_target_area(el, config_dict, area_keyword_item):
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]
    is_need_refresh = False
    matched_blocks = None

    if not el:
        return True, None

    try:
        area_list = await el.query_selector_all('a')
    except:
        return True, None

    if not area_list or len(area_list) == 0:
        return True, None

    matched_blocks = []
    for row in area_list:
        try:
            row_html = await row.get_html()
            row_text = util.remove_html_tags(row_html)
        except:
            break

        if not row_text or util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            continue

        row_text = util.format_keyword_string(row_text)

        # Check keyword match
        if area_keyword_item:
            is_match = all(
                util.format_keyword_string(kw) in row_text
                for kw in area_keyword_item.split(' ')
            )
            if not is_match:
                continue

        # Check seat availability for multiple tickets
        if config_dict["ticket_number"] > 1:
            try:
                font_el = await row.query_selector('font')
                if font_el:
                    font_text = await font_el.evaluate('el => el.textContent')
                    if font_text:
                        font_text = "@%s@" % font_text
                        # Skip if only 1-9 seats remaining
                        SEATS_1_9 = ["@%d@" % i for i in range(1, 10)]
                        if any(seat in font_text for seat in SEATS_1_9):
                            continue
            except:
                pass

        matched_blocks.append(row)

        if area_auto_select_mode == util.CONST_FROM_TOP_TO_BOTTOM:
            break

    if not matched_blocks:
        is_need_refresh = True
        matched_blocks = None

    return is_need_refresh, matched_blocks

async def nodriver_ticket_number_select_fill(tab, select_obj, ticket_number):
    """簡化版本：參考 Chrome 邏輯設定票券數量"""
    is_ticket_number_assigned = False

    if select_obj is None:
        return is_ticket_number_assigned

    try:
        # 嘗試透過 JavaScript 設定選擇器的值
        result = await tab.evaluate(f'''
            (function() {{
                const select = document.querySelector('.mobile-select') ||
                               document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                if (!select) return {{success: false, error: "Select not found"}};

                // 先嘗試設定目標數量
                const targetOption = Array.from(select.options).find(opt => opt.value === "{ticket_number}");
                if (targetOption) {{
                    select.value = "{ticket_number}";
                    select.selectedIndex = targetOption.index;
                    select.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return {{success: true, selected: "{ticket_number}"}};
                }}

                // 備用方案：設定為 "1"
                const fallbackOption = Array.from(select.options).find(opt => opt.value === "1");
                if (fallbackOption) {{
                    select.value = "1";
                    select.selectedIndex = fallbackOption.index;
                    select.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return {{success: true, selected: "1"}};
                }}

                return {{success: false, error: "No valid options"}};
            }})();
        ''')

        # 解析結果
        result = util.parse_nodriver_result(result)
        if isinstance(result, dict):
            is_ticket_number_assigned = result.get('success', False)

    except Exception as exc:
        print(f"設定票券數量失敗: {exc}")

    return is_ticket_number_assigned

async def nodriver_tixcraft_assign_ticket_number(tab, config_dict):
    """簡化版本：參考 Chrome 邏輯檢查票券選擇器"""
    show_debug_message = config_dict["advanced"]["verbose"]
    is_ticket_number_assigned = False

    # 等待頁面載入
    await tab.sleep(0.5)

    # 查找票券選擇器
    form_select_list = []
    try:
        form_select_list = await tab.query_selector_all('.mobile-select')
    except Exception as exc:
        if show_debug_message:
            print("查找 .mobile-select 失敗")

    # 如果沒找到 .mobile-select，嘗試其他選擇器
    if len(form_select_list) == 0:
        try:
            form_select_list = await tab.query_selector_all('select[id*="TicketForm_ticketPrice_"]')
        except Exception as exc:
            if show_debug_message:
                print("查找票券選擇器失敗")

    form_select_count = len(form_select_list)
    # 移除：內部檢測細節過度詳細

    # 檢查是否已經選擇了票券數量（非 "0"）
    if form_select_count > 0:
        try:
            # 使用 JavaScript 取得當前選中的值
            current_value = await tab.evaluate('''
                (function() {
                    const select = document.querySelector('.mobile-select') ||
                                   document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                    return select ? select.value : "0";
                })();
            ''')

            # 解析結果
            current_value = util.parse_nodriver_result(current_value)

            if current_value and current_value != "0" and str(current_value).isnumeric():
                is_ticket_number_assigned = True
                if show_debug_message:
                    print(f"票券數量已設定為: {current_value}")
        except Exception as exc:
            if show_debug_message:
                print(f"檢查當前選中值失敗: {exc}")

    # 回傳結果（保持與 Chrome 版本相容）
    select_obj = form_select_list[0] if form_select_count > 0 else None

    return is_ticket_number_assigned, select_obj

async def nodriver_tixcraft_ticket_main_agree(tab, config_dict):
    show_debug_message = config_dict["advanced"]["verbose"]

    if show_debug_message:
        print("開始執行勾選同意條款")

    for i in range(3):
        is_finish_checkbox_click = await nodriver_check_checkbox_enhanced(tab, '#TicketForm_agree', show_debug_message)
        if is_finish_checkbox_click:
            if show_debug_message:
                print("勾選同意條款成功")
            break
        elif show_debug_message:
            print(f"勾選同意條款失敗，重試 {i+1}/3")

    if not is_finish_checkbox_click and show_debug_message:
        print("警告：同意條款勾選失敗")

async def nodriver_tixcraft_ticket_main(tab, config_dict, ocr, Captcha_Browser, domain_name):
    global tixcraft_dict
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # 檢查是否已經設定過票券數量（方案 B：狀態標記）
    current_url, _ = await nodriver_current_url(tab)
    ticket_number = str(config_dict["ticket_number"])
    ticket_state_key = f"ticket_assigned_{current_url}_{ticket_number}"

    if ticket_state_key in tixcraft_dict and tixcraft_dict[ticket_state_key]:
        if show_debug_message:
            print(f"票券數量已設定過 ({ticket_number} 張)，跳過重複設定")

        # 確保勾選同意條款（即使票券已設定）
        await nodriver_tixcraft_ticket_main_agree(tab, config_dict)

        await nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name)
        return

    # NoDriver 模式下總是執行勾選同意條款
    await nodriver_tixcraft_ticket_main_agree(tab, config_dict)

    is_ticket_number_assigned = False

    # PS: some events on tixcraft have multi <select>.
    is_ticket_number_assigned, select_obj = await nodriver_tixcraft_assign_ticket_number(tab, config_dict)

    if not is_ticket_number_assigned:
        if show_debug_message:
            print(f"準備設定票券數量: {ticket_number}")
        is_ticket_number_assigned = await nodriver_ticket_number_select_fill(tab, select_obj, ticket_number)

    # 設定成功後記錄狀態
    if is_ticket_number_assigned:
        tixcraft_dict[ticket_state_key] = True
        if show_debug_message:
            print("票券數量設定完成，開始OCR驗證碼處理")
        await nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name)
    else:
        if show_debug_message:
            print("警告：票券數量設定失敗")

async def nodriver_tixcraft_keyin_captcha_code(tab, answer="", auto_submit=False, config_dict=None):
    """輸入驗證碼到表單"""
    is_verifyCode_editing = False
    is_form_submitted = False

    # 找到驗證碼輸入框
    form_verifyCode = await tab.query_selector('#TicketForm_verifyCode')

    if form_verifyCode:
        is_visible = False
        try:
            # 檢查元素是否可見和可用
            is_visible = await tab.evaluate('''
                (function() {
                    const element = document.querySelector('#TicketForm_verifyCode');
                    return element && !element.disabled && element.offsetParent !== null;
                })();
            ''')
        except Exception as exc:
            pass

        if is_visible:
            # 取得當前輸入值
            inputed_value = ""
            try:
                inputed_value = await form_verifyCode.apply('function (element) { return element.value; }') or ""
            except Exception as exc:
                pass

            is_text_clicked = False

            if not inputed_value and not answer:
                # 聚焦到輸入框等待手動輸入
                try:
                    await form_verifyCode.click()
                    is_text_clicked = True
                    is_verifyCode_editing = True
                except Exception as exc:
                    print("點擊驗證碼輸入框失敗，嘗試使用 JavaScript")
                    try:
                        await tab.evaluate('''
                            document.getElementById("TicketForm_verifyCode").focus();
                        ''')
                        is_verifyCode_editing = True
                    except Exception as exc:
                        pass

            if answer:
                print("開始填入驗證碼...")
                try:
                    if not is_text_clicked:
                        await form_verifyCode.click()

                    # 清空並輸入答案
                    await form_verifyCode.apply('function (element) { element.value = ""; }')
                    await form_verifyCode.send_keys(answer)

                    if auto_submit:
                        # 提交前確認票券數量是否已設定
                        ticket_number_ok = await tab.evaluate('''
                            (function() {
                                const select = document.querySelector('.mobile-select') ||
                                              document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                return select && select.value !== "0" && select.value !== "";
                            })();
                        ''')
                        ticket_number_ok = util.parse_nodriver_result(ticket_number_ok)

                        if not ticket_number_ok and config_dict:
                            print("警告：票券數量未設定，重新設定...")
                            # 重新設定票券數量
                            ticket_number = str(config_dict.get("ticket_number", 2))
                            await tab.evaluate(f'''
                                (function() {{
                                    const select = document.querySelector('.mobile-select') ||
                                                  document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                    if (select) {{
                                        select.value = "{ticket_number}";
                                        select.dispatchEvent(new Event('change', {{bubbles: true}}));
                                    }}
                                }})();
                            ''')

                        # 勾選同意條款
                        await nodriver_check_checkbox_enhanced(tab, '#TicketForm_agree')

                        # 最終確認所有欄位都已填寫
                        form_ready = await tab.evaluate('''
                            (function() {
                                const select = document.querySelector('.mobile-select') ||
                                              document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                const verify = document.querySelector('#TicketForm_verifyCode');
                                const agree = document.querySelector('#TicketForm_agree');

                                return {
                                    ticket: select && select.value !== "0" && select.value !== "",
                                    verify: verify && verify.value.length === 4,
                                    agree: agree && agree.checked,
                                    ready: (select && select.value !== "0") &&
                                           (verify && verify.value.length === 4) &&
                                           (agree && agree.checked)
                                };
                            })();
                        ''')
                        form_ready = util.parse_nodriver_result(form_ready)

                        if form_ready.get('ready', False):
                            # 提交表單 (按 Enter) - 使用完整的鍵盤事件
                            await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                            await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                            is_verifyCode_editing = False
                            is_form_submitted = True
                        else:
                            print(f"表單未就緒 - 票券:{form_ready.get('ticket')} 驗證碼:{form_ready.get('verify')} 同意:{form_ready.get('agree')}")
                    else:
                        # 選取輸入框內容並顯示提示
                        await tab.evaluate('''
                            document.getElementById("TicketForm_verifyCode").select();
                        ''')
                        # 顯示提示訊息
                        await nodriver_tixcraft_toast(tab, f"※ 按 Enter 如果答案是: {answer}")

                except Exception as exc:
                    print("輸入驗證碼失敗:", exc)

    return is_verifyCode_editing, is_form_submitted

async def nodriver_tixcraft_toast(tab, message):
    """顯示提示訊息"""
    try:
        await tab.evaluate(f'''
            (function() {{
                const toast = document.querySelector('p.remark-word');
                if (toast) {{
                    toast.innerHTML = '{message}';
                }}
            }})();
        ''')
    except Exception as exc:
        pass

async def nodriver_tixcraft_reload_captcha(tab, domain_name):
    """點擊重新載入驗證碼"""
    ret = False
    image_id = 'TicketForm_verifyCode-image'

    if 'indievox.com' in domain_name:
        image_id = 'TicketForm_verifyCode-image'

    try:
        form_captcha = await tab.query_selector(f"#{image_id}")
        if form_captcha:
            await form_captcha.click()
            ret = True
    except Exception as exc:
        print(f"重新載入驗證碼失敗: {exc}")

    return ret

async def nodriver_tixcraft_get_ocr_answer(tab, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name):
    """取得驗證碼圖片並進行 OCR 識別"""
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
            if 'indievox.com' in domain_name:
                image_id = 'TicketForm_verifyCode-image'

            try:
                # 使用 JavaScript 從 canvas 取得圖片
                form_verifyCode_base64 = await tab.evaluate(f'''
                    (function() {{
                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        var img = document.getElementById('{image_id}');
                        if(img) {{
                            canvas.height = img.naturalHeight;
                            canvas.width = img.naturalWidth;
                            context.drawImage(img, 0, 0);
                            return canvas.toDataURL();
                        }}
                        return null;
                    }})();
                ''')

                if form_verifyCode_base64:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])

                if img_base64 is None:
                    if not Captcha_Browser is None:
                        print("canvas 取得圖片失敗，使用方案 B: NonBrowser")
                        img_base64 = base64.b64decode(Captcha_Browser.request_captcha())

            except Exception as exc:
                if show_debug_message:
                    print("canvas 處理異常:", str(exc))

        # OCR 識別
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                if show_debug_message:
                    print("OCR 識別失敗:", exc)

    return ocr_answer

async def nodriver_tixcraft_auto_ocr(tab, config_dict, ocr, away_from_keyboard_enable,
                                     previous_answer, Captcha_Browser,
                                     ocr_captcha_image_source, domain_name):
    """OCR 自動識別主邏輯"""
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_need_redo_ocr = False
    is_form_submitted = False

    is_input_box_exist = False
    if not ocr is None:
        form_verifyCode = None
        try:
            form_verifyCode = await tab.query_selector('#TicketForm_verifyCode')
            is_input_box_exist = True
        except Exception as exc:
            pass
    else:
        print("[TIXCRAFT OCR] ddddocr 組件無法使用，您可能在 ARM 環境下運行")

    if is_input_box_exist:
        if show_debug_message:
            print("[TIXCRAFT OCR] away_from_keyboard_enable:", away_from_keyboard_enable)
            print("[TIXCRAFT OCR] previous_answer:", previous_answer)
            print("[TIXCRAFT OCR] ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()
        ocr_answer = await nodriver_tixcraft_get_ocr_answer(tab, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name)
        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        if show_debug_message:
            print("[TIXCRAFT OCR] 處理時間:", "{:.3f}".format(ocr_elapsed_time))

        if ocr_answer is None:
            if away_from_keyboard_enable:
                # 頁面尚未準備好，重試
                # PS: 通常發生在非同步腳本取得驗證碼圖片時
                is_need_redo_ocr = True
                await asyncio.sleep(0.1)
            else:
                await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
        else:
            ocr_answer = ocr_answer.strip()
            if show_debug_message:
                print("[TIXCRAFT OCR] 識別結果:", ocr_answer)
            if len(ocr_answer) == 4:
                who_care_var, is_form_submitted = await nodriver_tixcraft_keyin_captcha_code(tab, answer=ocr_answer, auto_submit=away_from_keyboard_enable, config_dict=config_dict)
            else:
                if not away_from_keyboard_enable:
                    await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                else:
                    is_need_redo_ocr = True
                    if previous_answer != ocr_answer:
                        previous_answer = ocr_answer
                        if show_debug_message:
                            print("[TIXCRAFT OCR] 重新點擊驗證碼")

                        # selenium 解決方案
                        await nodriver_tixcraft_reload_captcha(tab, domain_name)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            await asyncio.sleep(0.1)
    else:
        print("[TIXCRAFT OCR] 輸入框不存在，退出 OCR...")

    return is_need_redo_ocr, previous_answer, is_form_submitted

async def nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name):
    """票券頁面 OCR 處理主函數"""
    show_debug_message = config_dict["advanced"]["verbose"]

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    if not config_dict["ocr_captcha"]["enable"]:
        # 手動模式
        await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
    else:
        # 自動 OCR 模式
        previous_answer = None
        current_url, _ = await nodriver_current_url(tab)
        fail_count = 0  # Track consecutive failures
        total_fail_count = 0  # Track total failures

        for redo_ocr in range(5):
            is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_tixcraft_auto_ocr(
                tab, config_dict, ocr, away_from_keyboard_enable,
                previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name
            )

            if is_form_submitted:
                if show_debug_message:
                    print("[TIXCRAFT OCR] 表單已提交")
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break

            # Track failures and refresh captcha after 3 consecutive failures
            if is_need_redo_ocr:
                fail_count += 1
                total_fail_count += 1
                if show_debug_message:
                    print(f"[TIXCRAFT OCR] Fail count: {fail_count}, Total fails: {total_fail_count}")

                # Check if total failures reached 5, switch to manual input mode
                if total_fail_count >= 5:
                    print("[TIXCRAFT OCR] OCR failed 5 times. Please enter captcha manually.")
                    away_from_keyboard_enable = False
                    await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                    break

                if fail_count >= 3:
                    if show_debug_message:
                        print("[TIXCRAFT OCR] 3 consecutive failures reached")

                    # Try to dismiss any existing alert before continuing
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        if show_debug_message:
                            print("[TIXCRAFT OCR] Dismissed existing alert")
                    except:
                        pass

                    # Wait for potential auto-refresh
                    await asyncio.sleep(2.5)
                    fail_count = 0  # Reset consecutive counter after handling

            # 檢查是否還在同一頁面
            new_url, _ = await nodriver_current_url(tab)
            if new_url != current_url:
                break

            if show_debug_message:
                print(f"[TIXCRAFT OCR] Retry {redo_ocr + 1}/5")


async def nodriver_tixcraft_main(tab, url, config_dict, ocr, Captcha_Browser):
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

    await nodriver_tixcraft_home_close_window(tab)

    # special case for same event re-open, redirect to user's homepage.
    if 'https://tixcraft.com/' == url or 'https://tixcraft.com/activity' == url:
        if "/ticket/area/" in config_dict["homepage"]:
            if len(config_dict["homepage"].split('/'))==7:
                try:
                    await tab.get(config_dict["homepage"])
                except Exception as e:
                    pass

    if "/activity/detail/" in url:
        tixcraft_dict["start_time"] = time.time()
        is_redirected = await nodriver_tixcraft_redirect(tab, url)

    is_date_selected = False
    if "/activity/game/" in url:
        tixcraft_dict["start_time"] = time.time()
        if config_dict["date_auto_select"]["enable"]:
            domain_name = url.split('/')[2]
            is_date_selected = await nodriver_tixcraft_date_auto_select(tab, url, config_dict, domain_name)

    if '/artist/' in url and 'ticketmaster.com' in url:
        tixcraft_dict["start_time"] = time.time()
        if len(url.split('/'))==6:
            if config_dict["date_auto_select"]["enable"]:
                domain_name = url.split('/')[2]
                # TODO:
                #is_date_selected = ticketmaster_date_auto_select(driver, url, config_dict, domain_name)
                pass

    # choose area
    if '/ticket/area/' in url:
        domain_name = url.split('/')[2]
        if config_dict["area_auto_select"]["enable"]:
            if not 'ticketmaster' in domain_name:
                # for tixcraft
                await nodriver_tixcraft_area_auto_select(tab, url, config_dict)

                tixcraft_dict["area_retry_count"]+=1
                #print("count:", tixcraft_dict["area_retry_count"])
                if tixcraft_dict["area_retry_count"] >= (60 * 15):
                    # Cool-down
                    tixcraft_dict["area_retry_count"] = 0
                    await asyncio.sleep(5)
            else:
                # area auto select is too difficult, skip in this version.
                # TODO:
                #tixcraft_dict["fail_promo_list"] = ticketmaster_promo(driver, config_dict, tixcraft_dict["fail_promo_list"])
                #ticketmaster_assign_ticket_number(driver, config_dict)
                pass
    else:
        tixcraft_dict["fail_promo_list"] = []
        tixcraft_dict["area_retry_count"]=0

    # https://ticketmaster.sg/ticket/check-captcha/23_blackpink/954/5/75
    if '/ticket/check-captcha/' in url:
        domain_name = url.split('/')[2]
        # TODO:
        #ticketmaster_captcha(driver, config_dict, ocr, Captcha_Browser, domain_name)
        pass

    if '/ticket/verify/' in url:
        # TODO:
        #tixcraft_dict["fail_list"] = tixcraft_verify(driver, config_dict, tixcraft_dict["fail_list"])
        pass
    else:
        tixcraft_dict["fail_list"] = []

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        domain_name = url.split('/')[2]
        await nodriver_tixcraft_ticket_main(tab, config_dict, ocr, Captcha_Browser, domain_name)
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


async def nodriver_ticketplus_detect_layout_style(tab, config_dict=None):
    """偵測 TicketPlus 頁面佈局樣式

    Returns:
        dict: {
            'style': int,      # 0: 無法偵測, 1: style_1 (展開式), 2: style_2 (簡單式), 3: style_3 (新版Vue.js)
            'found': bool,     # 是否找到下一步按鈕
            'button_enabled': bool  # 按鈕是否已啟用
        }
    """
    try:
        result = await evaluate_with_pause_check(tab, '''
            (function() {
                console.log("=== Layout Detection Started ===");

                // 先檢查頁面中是否有 row 佈局的票種結構 (Page3特徵)
                const rowTickets = document.querySelectorAll('.row.py-1.py-md-4.rwd-margin.no-gutters.text-title');
                const expansionPanels = document.querySelectorAll('.v-expansion-panels .v-expansion-panel');

                console.log("Row ticket element count:", rowTickets.length);
                console.log("Expansion Panel element count:", expansionPanels.length);

                // 如果有 row 票種且沒有 expansion panels，優先判定為 style 3 (Page3)
                if (rowTickets.length > 0 && expansionPanels.length === 0) {
                    // 檢查 style_3 按鈕
                    const style3Button = document.querySelector("div.order-footer > div.container > div.row > div.col-sm-3.col-4 > button.nextBtn") ||
                                       document.querySelector("button.nextBtn");
                    if (style3Button) {
                        console.log("Confirmed as Page3 (Style 3) - Row layout");
                        return {
                            style: 3,
                            found: true,
                            button_enabled: style3Button.disabled === false,
                            button_class: style3Button.className,
                            debug_info: "Page3 row layout detected"
                        };
                    }
                }

                // style_3: 新版 Vue.js 佈局 (通用檢查)
                const style3Button = document.querySelector("div.order-footer > div.container > div.row > div.col-sm-3.col-4 > button.nextBtn");
                if (style3Button) {
                    console.log("Found Style 3 button");
                    return {
                        style: 3,
                        found: true,
                        button_enabled: style3Button.disabled === false,
                        button_class: style3Button.className,
                        debug_info: "Standard style 3 button"
                    };
                }

                // style_2: 新版佈局 (簡單式)
                const style2Button = document.querySelector("div.order-footer > div.container > div.row > div > button.nextBtn");
                if (style2Button) {
                    console.log("Found Style 2 button");
                    return {
                        style: 2,
                        found: true,
                        button_enabled: style2Button.disabled === false,
                        button_class: style2Button.className,
                        debug_info: "Standard style 2 button"
                    };
                }

                // style_1: 舊版佈局 (展開式) - 只有在有 expansion panels 時才判定
                if (expansionPanels.length > 0) {
                    const style1Button = document.querySelector("div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn");
                    if (style1Button) {
                        console.log("Found Style 1 button (expansion panel type)");
                        return {
                            style: 1,
                            found: true,
                            button_enabled: style1Button.disabled === false,
                            button_class: style1Button.className,
                            debug_info: "Expansion panel layout"
                        };
                    }
                }

                // 通用按鈕查找 (兜底方案)
                const anyButton = document.querySelector("button.nextBtn");
                if (anyButton) {
                    console.log("Found generic nextBtn button, determining style based on content structure");
                    // 根據頁面結構特徵判斷樣式
                    if (rowTickets.length > 0) {
                        return {
                            style: 3,
                            found: true,
                            button_enabled: anyButton.disabled === false,
                            button_class: anyButton.className,
                            debug_info: "Generic button + row structure = style 3"
                        };
                    }
                    if (expansionPanels.length > 0) {
                        return {
                            style: 1,
                            found: true,
                            button_enabled: anyButton.disabled === false,
                            button_class: anyButton.className,
                            debug_info: "Generic button + expansion panels = style 1"
                        };
                    }
                }

                console.log("Unable to detect layout style");
                return {
                    style: 0,
                    found: false,
                    button_enabled: false,
                    button_class: "",
                    debug_info: "No layout detected"
                };
            })();
        ''')

        # 檢查是否因暫停而中斷
        if result is None:
            return {'style': 0, 'found': False, 'button_enabled': False, 'paused': True}

        # 使用統一解析函數處理返回值
        result = util.parse_nodriver_result(result)

        return result if isinstance(result, dict) else {
            'style': 0, 'found': False, 'button_enabled': False
        }

    except Exception as exc:
        return {'style': 0, 'found': False, 'button_enabled': False, 'error': str(exc)}

async def nodriver_ticketplus_account_sign_in(tab, config_dict):
    print("nodriver_ticketplus_account_sign_in")
    is_filled_form = False
    is_submited = False

    ticketplus_account = config_dict["advanced"]["ticketplus_account"]
    ticketplus_password = config_dict["advanced"]["ticketplus_password_plaintext"].strip()
    if ticketplus_password == "":
        ticketplus_password = util.decryptMe(config_dict["advanced"]["ticketplus_password"])

    # manually keyin verify code.
    country_code = ""
    try:
        my_css_selector = 'input[placeholder="區碼"]'
        el_country = await tab.query_selector(my_css_selector)
        if el_country:
            country_code = await el_country.apply('function (element) { return element.value; } ')
            print("country_code", country_code)
    except Exception as exc:
        print(exc)

    is_account_assigned = False
    try:
        my_css_selector = 'input[placeholder="手機號碼 *"]'
        el_account = await tab.query_selector(my_css_selector)
        if el_account:
            await el_account.click()
            await el_account.apply('function (element) {element.value = ""; } ')
            await el_account.send_keys(ticketplus_account);
            is_account_assigned = True
    except Exception as exc:
        print(exc)

    if is_account_assigned:
        try:
            my_css_selector = 'input[type="password"]'
            el_password = await tab.query_selector(my_css_selector)
            if el_password:
                print("Entering password...")
                await el_password.click()
                await el_password.apply('function (element) {element.value = ""; } ')
                await el_password.send_keys(ticketplus_password);
                await asyncio.sleep(random.uniform(0.1, 0.3))
                is_filled_form = True

                if country_code=="+886":
                    # only this case to auto sumbmit.
                    print("press enter")
                    await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                    await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                    await asyncio.sleep(random.uniform(0.8, 1.2))
                    # PS: ticketplus country field may not located at your target country.
                    is_submited = True
        except Exception as exc:
            print(exc)
            pass


    return is_filled_form, is_submited

async def nodriver_ticketplus_is_signin(tab):
    is_user_signin = False
    try:
        cookies  = await tab.browser.cookies.get_all()
        for cookie in cookies:
            if cookie.name=='user':
                if '%22account%22:%22' in cookie.value:
                    is_user_signin = True
        cookies = None
    except Exception as exc:
        print(exc)
        pass

    return is_user_signin


async def nodriver_ticketplus_account_auto_fill(tab, config_dict):
    global is_filled_ticketplus_singin_form

    if not 'is_filled_ticketplus_singin_form' in globals():
        is_filled_ticketplus_singin_form = False

    # auto fill account info.
    is_user_signin = False
    if len(config_dict["advanced"]["ticketplus_account"]) > 0:
        is_user_signin = await nodriver_ticketplus_is_signin(tab)
        #print("is_user_signin:", is_user_signin)
        if not is_user_signin:
            await asyncio.sleep(0.1)
            if not is_filled_ticketplus_singin_form:
                is_sign_in_btn_pressed = False
                try:
                    # full screen mode.
                    my_css_selector = 'button.v-btn > span.v-btn__content > i.mdi-account'
                    sign_in_btn = await tab.query_selector(my_css_selector)
                    if sign_in_btn:
                        await sign_in_btn.click()
                        is_sign_in_btn_pressed = True
                        await asyncio.sleep(0.2)
                except Exception as exc:
                    print(exc)
                    pass

                #print("is_sign_in_btn_pressed", is_sign_in_btn_pressed)
                if not is_sign_in_btn_pressed:
                    #print("rwd mode")
                    action_btns = None
                    try:
                        my_css_selector = 'div.px-4.py-3.drawerItem.cursor-pointer'
                        action_btns = await tab.query_selector_all(my_css_selector)
                    except Exception as exc:
                        print(exc)
                        pass
                    if action_btns:
                        print("len:", len(action_btns))
                        if len(action_btns) >= 4:
                            try:
                                await action_btns[3].click()
                            except Exception as exc:
                                print(exc)
                                pass

                is_filled_form, is_submited = await nodriver_ticketplus_account_sign_in(tab, config_dict)
                if is_filled_form:
                    is_filled_ticketplus_singin_form = True

    return is_user_signin

async def nodriver_ticketplus_date_auto_select(tab, config_dict):
    """TicketPlus 日期自動選擇功能"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # 讀取設定
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_auto_select_mode:", auto_select_mode)
        print("date_keyword:", date_keyword)

    # 查找日期區塊
    area_list = None
    try:
        area_list = await tab.query_selector_all('div#buyTicket > div.sesstion-item > div.row')
        if area_list and len(area_list) == 0:
            if show_debug_message:
                print("empty date item, need retry.")
            await tab.sleep(0.2)
    except Exception as exc:
        if show_debug_message:
            print("find #buyTicket fail:", exc)

    # 檢查可購買的選項
    find_ticket_text_list = ['>立即購', '尚未開賣']
    sold_out_text_list = ['銷售一空']

    matched_blocks = None
    formated_area_list = None
    is_vue_ready = True

    if area_list and len(area_list) > 0:
        if show_debug_message:
            print("date_list_count:", len(area_list))

        formated_area_list = []
        for row in area_list:
            row_text = ""
            row_html = ""
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                if show_debug_message:
                    print("Date item processing failed:", exc)
                break

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                if '<div class="v-progress-circular__info"></div>' in row_html:
                    # Vue.js 尚未載入完成
                    is_vue_ready = False
                    break

            if len(row_text) > 0:
                row_is_enabled = False
                for text_item in find_ticket_text_list:
                    if text_item in row_html:
                        row_is_enabled = True
                        break

                # 檢查是否已售完
                if row_is_enabled and pass_date_is_sold_out_enable:
                    for sold_out_item in sold_out_text_list:
                        if sold_out_item in row_text:
                            row_is_enabled = False
                            if show_debug_message:
                                print(f"match sold out text: {sold_out_item}, skip this row.")
                            break

                if row_is_enabled:
                    formated_area_list.append(row)

        if show_debug_message:
            print("formated_area_list count:", len(formated_area_list))

        # 關鍵字匹配 - 使用 JavaScript 避免 NoDriver 元素物件問題
        if len(date_keyword) == 0:
            matched_blocks = formated_area_list
        else:
            date_keyword = util.format_keyword_string(date_keyword)
            if show_debug_message:
                print("start to match formated keyword:", date_keyword)

            # 使用 JavaScript 進行關鍵字匹配，避免 util.py 的 NoDriver 不相容問題
            try:
                # 在 JavaScript 中處理關鍵字分割，避免 format_keyword_string 破壞逗號分隔
                original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
                js_result = await tab.evaluate(f'''
                    (function() {{
                        const originalKeyword = '{original_keyword}';
                        const matchedElements = [];

                        // 解析關鍵字 - 處理引號包圍和逗號分隔
                        let keywords = [];
                        if (originalKeyword.includes(',')) {{
                            // 分割逗號分隔的關鍵字
                            const parts = originalKeyword.split(',');
                            keywords = parts.map(part => {{
                                // 移除引號和空格
                                return part.trim().replace(/^["']|["']$/g, '');
                            }}).filter(k => k.length > 0);
                        }} else {{
                            // 單個關鍵字
                            keywords = [originalKeyword.replace(/^["']|["']$/g, '').trim()];
                        }}

                        console.log('解析出的關鍵字:', keywords);

                        // 查找所有可能的日期元素
                        const selectors = [
                            'div#buyTicket > div.sesstion-item > div.row',
                            'tr', 'div[class*="date"]', 'div[class*="session"]',
                            '.sesstion-item', '[data-href]'
                        ];

                        let allElements = [];
                        selectors.forEach(selector => {{
                            const elements = Array.from(document.querySelectorAll(selector));
                            allElements = allElements.concat(elements);
                        }});

                        // 去重
                        allElements = [...new Set(allElements)];

                        console.log('找到', allElements.length, '個候選元素');

                        // 匹配任一關鍵字
                        for (let element of allElements) {{
                            const text = element.textContent || element.innerText || '';
                            const normalizedText = text.replace(/[\\s\\u3000]/g, '').toLowerCase();

                            for (let keyword of keywords) {{
                                // 正規化關鍵字 - 移除空格、全形空格，轉小寫
                                const normalizedKeyword = keyword.replace(/[\\s\\u3000]/g, '').toLowerCase();

                                if (normalizedText.includes(normalizedKeyword)) {{
                                    console.log('匹配到日期:', '"' + keyword + '" -> ' + text.substring(0, 100));
                                    matchedElements.push(element);
                                    break; // 匹配到一個關鍵字就足夠
                                }}
                            }}
                        }}

                        return {{
                            success: true,
                            matchedCount: matchedElements.length,
                            keywords: keywords,
                            matchedElements: matchedElements.map((el, idx) => ({{
                                index: idx,
                                text: (el.textContent || '').substring(0, 200),
                                tagName: el.tagName
                            }}))
                        }};
                    }})();
                ''')

                # 使用 NoDriver 結果解析器
                parsed_js_result = util.parse_nodriver_result(js_result)

                if isinstance(parsed_js_result, dict) and parsed_js_result.get('success'):
                    matched_count = parsed_js_result.get('matchedCount', 0)
                    if show_debug_message:
                        keywords = parsed_js_result.get('keywords', [])
                        print(f"Parsed keywords: {keywords}")
                        print(f"after JavaScript match keyword, found count: {matched_count}")
                        for match_info in parsed_js_result.get('matchedElements', []):
                            if isinstance(match_info, dict):
                                print(f"  Match {match_info.get('index', '?')}: {match_info.get('text', '')}")

                    # 如果有匹配結果，取第一個作為 matched_blocks
                    matched_blocks = formated_area_list[:matched_count] if matched_count > 0 else []
                else:
                    matched_blocks = []

            except Exception as exc:
                if show_debug_message:
                    print(f"JavaScript keyword matching failed: {exc}")
                matched_blocks = []
    else:
        if show_debug_message:
            print("date date-time-position is None or empty")

    # 執行點擊 - 完全使用 JavaScript 避免元素物件操作
    is_date_clicked = False
    if is_vue_ready:
        try:
            # 使用原始關鍵字進行點擊，與匹配邏輯保持一致
            original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
            # 直接在 JavaScript 中完成日期選擇和點擊
            click_result = await tab.evaluate(f'''
                (function() {{
                    const originalKeyword = '{original_keyword}';
                    const autoSelectMode = '{auto_select_mode}';

                    console.log('Starting date selection and click - keyword:', originalKeyword, 'mode:', autoSelectMode);

                    // 查找匹配的日期元素，優先找「立即購買」按鈕
                    const selectors = [
                        'button.nextBtn',           // TicketPlus 的「立即購買」按鈕
                        '.sesstion-item',           // 場次項目
                        'button',                   // 任何按鈕
                        'tr',
                        'div[class*="date"]',
                        'div[class*="session"]',
                        '[data-href]'
                    ];

                    let matchedElements = [];
                    let allElements = [];

                    selectors.forEach(selector => {{
                        const elements = Array.from(document.querySelectorAll(selector));
                        allElements = allElements.concat(elements);
                    }});

                    // 去重
                    allElements = [...new Set(allElements)];

                    // 關鍵字匹配（如果有關鍵字的話）- 使用與匹配邏輯一致的方式
                    if (originalKeyword && originalKeyword.trim() !== '') {{
                        // 解析關鍵字 - 處理引號包圍和逗號分隔，與匹配邏輯保持一致
                        let keywords = [];
                        if (originalKeyword.includes(',')) {{
                            // 分割逗號分隔的關鍵字
                            const parts = originalKeyword.split(',');
                            keywords = parts.map(part => {{
                                // 移除引號和空格
                                return part.trim().replace(/^["']|["']$/g, '');
                            }}).filter(k => k.length > 0);
                        }} else {{
                            // 單個關鍵字
                            keywords = [originalKeyword.replace(/^["']|["']$/g, '').trim()];
                        }}

                        console.log('點擊邏輯解析出的關鍵字:', keywords);

                        for (let element of allElements) {{
                            const text = element.textContent || element.innerText || '';
                            const normalizedText = text.replace(/[\\s\\u3000]/g, '').toLowerCase();

                            // 檢查是否包含任一關鍵字
                            let matched = false;
                            for (let keyword of keywords) {{
                                // 正規化關鍵字 - 移除空格、全形空格，轉小寫
                                const normalizedKeyword = keyword.replace(/[\\s\\u3000]/g, '').toLowerCase();

                                if (normalizedText.includes(normalizedKeyword)) {{
                                    console.log('點擊邏輯匹配到日期元素:', '"' + keyword + '" -> ' + text.substring(0, 100));
                                    matched = true;
                                    break;
                                }}
                            }}

                            if (matched) {{
                                matchedElements.push(element);
                            }}
                        }}
                    }} else {{
                        // 沒有關鍵字，優先篩選最相關的購買按鈕
                        console.log('No keyword specified, filtering relevant buy buttons');

                        // 優先選擇 nextBtn 立即購買按鈕
                        let buyButtons = allElements.filter(el => {{
                            return el.matches('button.nextBtn') &&
                                   el.textContent &&
                                   el.textContent.includes('立即購買');
                        }});

                        // 如果沒找到 nextBtn，嘗試其他購買相關元素
                        if (buyButtons.length === 0) {{
                            buyButtons = allElements.filter(el => {{
                                const text = el.textContent || el.innerText || '';
                                return (el.matches('button') || el.matches('.sesstion-item')) &&
                                       text.includes('購買');
                            }});
                        }}

                        // 如果還是沒找到，使用所有 nextBtn 按鈕
                        if (buyButtons.length === 0) {{
                            buyButtons = allElements.filter(el => el.matches('button.nextBtn'));
                        }}

                        // 最後選擇：使用所有可點擊元素
                        if (buyButtons.length === 0) {{
                            buyButtons = allElements.filter(el => {{
                                return el.matches('button') || el.matches('[onclick]') || el.matches('a[href]');
                            }});
                        }}

                        matchedElements = buyButtons;
                        console.log('No keyword - filtered to', matchedElements.length, 'relevant buy buttons');

                        // 詳細 log 每個候選元素
                        matchedElements.forEach((el, index) => {{
                            const text = (el.textContent || '').substring(0, 50);
                            const tagName = el.tagName.toLowerCase();
                            const className = el.className || '';
                            console.log('  Candidate ' + index + ': <' + tagName + ' class="' + className + '">' + text + '...');
                        }});
                    }}

                    if (matchedElements.length === 0) {{
                        console.log('[ERROR] No valid elements found for clicking');
                        console.log('Total allElements found:', allElements.length);
                        console.log('Search mode: keyword=' + originalKeyword + ', mode=' + autoSelectMode);
                        return {{
                            success: false,
                            error: 'No matched date elements found',
                            debug: {{
                                totalElements: allElements.length,
                                keyword: originalKeyword,
                                mode: autoSelectMode
                            }}
                        }};
                    }}

                    // 根據模式選擇目標元素
                    console.log('[SUCCESS] Found ' + matchedElements.length + ' candidate elements, selecting by mode: ' + autoSelectMode);

                    let targetIndex = 0; // 預設第一個
                    if (autoSelectMode === 'from bottom to top') {{
                        targetIndex = matchedElements.length - 1;
                    }} else if (autoSelectMode === 'center') {{
                        targetIndex = Math.floor(matchedElements.length / 2);
                    }} else if (autoSelectMode === 'random') {{
                        targetIndex = Math.floor(Math.random() * matchedElements.length);
                    }}

                    let targetElement = matchedElements[targetIndex];
                    const targetText = (targetElement.textContent || '').substring(0, 100);
                    const targetTag = targetElement.tagName.toLowerCase();
                    const targetClass = targetElement.className || '';

                    console.log('[TARGET] Selected element [' + targetIndex + ']: <' + targetTag + ' class="' + targetClass + '">' + targetText + '...');

                    // 嘗試點擊
                    let clickSuccess = false;
                    let clickAction = '';

                    // 方法1: 找內部的按鈕
                    const button = targetElement.querySelector('button');
                    if (button && !clickSuccess) {{
                        try {{
                            const event = new MouseEvent('click', {{
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }});
                            button.dispatchEvent(event);
                            clickSuccess = true;
                            clickAction = 'internal_button_clicked';
                            console.log('Internal button click successful');
                        }} catch (e) {{
                            console.log('Internal button click failed:', e.message);
                        }}
                    }}

                    // 方法2: 點擊整個元素
                    if (!clickSuccess) {{
                        try {{
                            const event = new MouseEvent('click', {{
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }});
                            targetElement.dispatchEvent(event);
                            clickSuccess = true;
                            clickAction = 'element_clicked';
                            console.log('Element click successful');
                        }} catch (e) {{
                            console.log('Element click failed:', e.message);
                        }}
                    }}

                    // 方法3: 如果有 data-href，直接導航
                    if (!clickSuccess && targetElement.getAttribute('data-href')) {{
                        try {{
                            const href = targetElement.getAttribute('data-href');
                            window.location.href = href;
                            clickSuccess = true;
                            clickAction = 'navigation_by_href';
                            console.log('Navigation via data-href successful');
                        }} catch (e) {{
                            console.log('data-href navigation failed:', e.message);
                        }}
                    }}

                    return {{
                        success: clickSuccess,
                        action: clickAction,
                        matchedCount: matchedElements.length,
                        targetText: (targetElement.textContent || '').substring(0, 200)
                    }};
                }})();
            ''')

            # 使用 NoDriver 結果解析器
            parsed_result = util.parse_nodriver_result(click_result)

            if isinstance(parsed_result, dict) and parsed_result.get('success'):
                if show_debug_message:
                    print(f"Date selection and click successful: {parsed_result.get('action', 'unknown')}")
                    print(f"   目標文字: {parsed_result.get('targetText', '')}")
                is_date_clicked = True
            else:
                if show_debug_message:
                    print(f"Date selection and click failed: {parsed_result.get('error', 'unknown') if isinstance(parsed_result, dict) else str(parsed_result)}")

        except Exception as exc:
            if show_debug_message:
                print("JavaScript date selection click failed:", exc)

        # 自動重載邏輯
        if auto_reload_coming_soon_page_enable and not is_date_clicked:
            if formated_area_list and len(formated_area_list) == 0:
                if show_debug_message:
                    print("no available date found, reload page...")
                try:
                    await tab.reload()
                except Exception as exc:
                    if show_debug_message:
                        print("reload fail:", exc)
    else:
        if show_debug_message:
            print("Vue.js not ready, skip clicking")

    return is_date_clicked

async def nodriver_ticketplus_unified_select(tab, config_dict, area_keyword):
    """TicketPlus 統一選擇器 - 語言無關的票種/票區選擇"""
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    ticket_number = config_dict["ticket_number"]
    keyword_exclude = config_dict.get("keyword_exclude", "")

    if show_debug_message:
        print(f"Unified selector started - keyword: {area_keyword}, tickets: {ticket_number}")

    is_selected = False

    try:
        # 檢查暫停狀態
        if await check_and_handle_pause(config_dict):
            return False

        # 等待頁面載入
        if await sleep_with_pause_check(tab, 1.0, config_dict):
            if show_debug_message:
                print("Pause check interrupted")
            return False

        # 解析排除關鍵字
        exclude_keywords = []
        if keyword_exclude:
            try:
                # 移除雙引號並用逗號分隔
                exclude_keywords = [kw.strip('"') for kw in keyword_exclude.split(',') if kw.strip()]
            except:
                pass

        # 統一的結構化判斷與選擇邏輯
        js_result = await tab.evaluate(f'''
            (async function() {{
                const keyword = '{area_keyword}';
                const ticketNumber = {ticket_number};
                const autoSelectMode = '{auto_select_mode}';
                const keywordArray = keyword.split(' ');
                const keyword1 = keywordArray[0] || '';
                const keyword2 = keywordArray[1] || '';
                const excludeKeywords = {exclude_keywords};

                console.log('Unified selector execution - keyword:', keyword, 'tickets:', ticketNumber, 'mode:', autoSelectMode);
                console.log('排除關鍵字:', excludeKeywords);

                // 檢查是否售罄
                function isSoldOut(element) {{
                    const text = element.textContent || '';
                    console.log('檢查售罄狀態:', text.replace(/\s+/g, ' ').trim());

                    // 更精準的售罄檢查
                    const soldOutPatterns = [
                        /剩餘\s*0(?!\d)/,  // "剩餘 0" 或 "剩餘0" 但不包括 "剩餘 10"
                        /剩餘\s*:\s*0(?!\d)/, // "剩餘: 0" 格式
                        /sold\s*out/i,
                        /售完/,
                        /已售完/,
                        /售罄/,
                        /無庫存/,
                        /not\s*available/i
                    ];

                    for (let pattern of soldOutPatterns) {{
                        if (pattern.test(text)) {{
                            console.log('檢測到售罄標記:', pattern.toString());
                            return true;
                        }}
                    }}

                    // 檢查是否明確有票
                    const availablePatterns = [
                        /熱賣中/,
                        /熱賣/,
                        /熱售/,
                        /可購買/,
                        /available/i,
                        /剩餘\s*[1-9]\d*/  // 剩餘大於0的數字
                    ];

                    for (let pattern of availablePatterns) {{
                        if (pattern.test(text)) {{
                            console.log('檢測到有票標記:', pattern.toString());
                            return false;
                        }}
                    }}

                    console.log('無法確定售罄狀態，預設為可用');
                    return false;
                }}

                // 檢查是否包含排除關鍵字
                function containsExcludeKeywords(name) {{
                    if (!excludeKeywords || excludeKeywords.length === 0) return false;

                    for (let excludeKeyword of excludeKeywords) {{
                        if (excludeKeyword && name.includes(excludeKeyword)) {{
                            console.log('發現排除關鍵字:', excludeKeyword, '於:', name);
                            return true;
                        }}
                    }}
                    return false;
                }}

                // 計算目標索引的輔助函數
                function getTargetIndex(items, mode) {{
                    const count = items.length;
                    if (count === 0) return -1;

                    switch(mode) {{
                        case 'from top to bottom':
                            return 0;
                        case 'from bottom to top':
                            return count - 1;
                        case 'center':
                            return Math.floor((count - 1) / 2);
                        case 'random':
                            return Math.floor(Math.random() * count);
                        default:
                            return 0;
                    }}
                }}

                // 等待函數
                function sleep(ms) {{
                    return new Promise(resolve => setTimeout(resolve, ms));
                }}

                // 結構化判斷頁面類型
                const hasCountButton = document.querySelector('.count-button .mdi-plus');
                const hasExpansionPanel = document.querySelector('.v-expansion-panel');

                if (hasCountButton) {{
                    // 類型A: 票種選擇頁面（有加減按鈕）
                    console.log('偵測到票種選擇頁面');
                    const rows = document.querySelectorAll('.row.py-1.py-md-4:has(.count-button)');

                    // 過濾掉售罄和排除關鍵字的選項
                    const validRows = [];
                    for (let i = 0; i < rows.length; i++) {{
                        const row = rows[i];
                        const nameElement = row.querySelector('.font-weight-medium');

                        if (nameElement) {{
                            const ticketName = nameElement.textContent.trim();

                            // 檢查是否售罄
                            if (isSoldOut(row)) {{
                                console.log('跳過售罄票種:', ticketName);
                                continue;
                            }}

                            // 檢查是否包含排除關鍵字
                            if (containsExcludeKeywords(ticketName)) {{
                                console.log('跳過排除關鍵字票種:', ticketName);
                                continue;
                            }}

                            validRows.push({{ row: row, name: ticketName, index: i }});
                            console.log('可選票種:', ticketName);
                        }}
                    }}

                    let targetRow = null;
                    let targetTicketName = '';

                    // 先嘗試關鍵字比對（僅在有效選項中）
                    if (keyword1) {{
                        for (let item of validRows) {{
                            if (item.name.includes(keyword1)) {{
                                if (!keyword2 || item.name.includes(keyword2)) {{
                                    console.log('找到符合關鍵字的票種:', item.name);
                                    targetRow = item.row;
                                    targetTicketName = item.name;
                                    break;
                                }}
                            }}
                        }}
                    }}

                    // 如果沒有關鍵字或找不到符合的，使用 mode 選擇
                    if (!targetRow && validRows.length > 0) {{
                        console.log('📍 無關鍵字或找不到符合項目，使用自動選擇模式:', autoSelectMode);
                        const targetIndex = getTargetIndex(validRows, autoSelectMode);
                        if (targetIndex >= 0 && targetIndex < validRows.length) {{
                            const targetItem = validRows[targetIndex];
                            targetRow = targetItem.row;
                            targetTicketName = targetItem.name;
                            console.log('自動選擇票種:', targetTicketName);
                        }}
                    }}

                    if (validRows.length === 0) {{
                        console.log('沒有可選的票種（全部售完或被排除）');
                        return {{ success: false, message: '沒有可選的票種（全部售完或被排除）' }};
                    }}

                    if (targetRow) {{
                        const plusButton = targetRow.querySelector('.mdi-plus');
                        if (plusButton) {{
                            console.log('開始點擊加號按鈕');
                            for (let j = 0; j < ticketNumber; j++) {{
                                plusButton.click();
                                console.log('➕ 點擊加號 ' + (j + 1) + '/' + ticketNumber);
                            }}
                            return {{ success: true, type: 'ticket_type', selected: targetTicketName }};
                        }} else {{
                            console.log('找不到加號按鈕');
                        }}
                    }}

                }} else if (hasExpansionPanel) {{
                    // 類型B: 票區選擇頁面（有展開面板）
                    console.log('🎭 偵測到票區選擇頁面');
                    const panels = document.querySelectorAll('.v-expansion-panel');

                    // 過濾掉售罄和排除關鍵字的選項
                    const validPanels = [];
                    console.log('🎭 共找到' + panels.length + '個展開面板');

                    for (let i = 0; i < panels.length; i++) {{
                        const panel = panels[i];
                        const nameElement = panel.querySelector('.d-flex.align-center:not(:has(.area-color))');

                        if (nameElement) {{
                            const areaName = nameElement.textContent.trim();
                            console.log('檢查票區' + (i + 1) + ': "' + areaName + '"');

                            // 檢查是否售罄
                            if (isSoldOut(panel)) {{
                                console.log('跳過售罄票區:', areaName);
                                continue;
                            }}

                            // 檢查是否包含排除關鍵字
                            if (containsExcludeKeywords(areaName)) {{
                                console.log('跳過排除關鍵字票區:', areaName);
                                continue;
                            }}

                            validPanels.push({{ panel: panel, name: areaName, index: i }});
                            console.log('可選票區:', areaName);
                        }} else {{
                            console.log('票區' + (i + 1) + '找不到名稱元素');
                        }}
                    }}

                    console.log('有效票區數量: ' + validPanels.length + '/' + panels.length);
                    if (validPanels.length > 0) {{
                        console.log('有效票區清單:', validPanels.map(p => p.name));
                    }}

                    let targetPanel = null;
                    let targetAreaName = '';

                    // 先嘗試關鍵字比對（僅在有效選項中）
                    if (keyword1) {{
                        for (let item of validPanels) {{
                            if (item.name.includes(keyword1)) {{
                                if (!keyword2 || item.name.includes(keyword2)) {{
                                    console.log('找到符合關鍵字的票區:', item.name);
                                    targetPanel = item.panel;
                                    targetAreaName = item.name;
                                    break;
                                }}
                            }}
                        }}
                    }}

                    // 如果沒有關鍵字或找不到符合的，使用 mode 選擇
                    if (!targetPanel && validPanels.length > 0) {{
                        console.log('📍 無關鍵字或找不到符合項目，使用自動選擇模式:', autoSelectMode);
                        const targetIndex = getTargetIndex(validPanels, autoSelectMode);
                        if (targetIndex >= 0 && targetIndex < validPanels.length) {{
                            const targetItem = validPanels[targetIndex];
                            targetPanel = targetItem.panel;
                            targetAreaName = targetItem.name;
                            console.log('自動選擇票區:', targetAreaName);
                        }}
                    }}

                    if (validPanels.length === 0) {{
                        console.log('沒有可選的票區（全部售完或被排除）');
                        return {{ success: false, message: '沒有可選的票區（全部售完或被排除）' }};
                    }}

                    if (targetPanel) {{
                        const header = targetPanel.querySelector('.v-expansion-panel-header');
                        if (header) {{
                            console.log('點擊展開面板:', targetAreaName);
                            header.click();

                            // 等待面板展開並找到操作按鈕的異步函數
                            const waitAndFindAction = async () => {{
                                return new Promise((resolve) => {{
                                    let attempts = 0;
                                    const maxAttempts = 10; // 最多嘗試1秒 (100ms * 10)

                                    const findAction = () => {{
                                        attempts++;
                                        console.log('第' + attempts + '次尋找操作按鈕...');

                                        // 先嘗試找加號按鈕
                                        let plusButton = targetPanel.querySelector('.mdi-plus');
                                        if (plusButton) {{
                                            console.log('找到加號按鈕，開始設定票數');
                                            for (let j = 0; j < ticketNumber; j++) {{
                                                plusButton.click();
                                                console.log('➕ 點擊加號 ' + (j + 1) + '/' + ticketNumber);
                                            }}
                                            resolve({{ success: true, action: 'plus_button' }});
                                            return;
                                        }}

                                        // 再嘗試找 count-button 結構
                                        const countButtons = targetPanel.querySelectorAll('.count-button .mdi-plus');
                                        if (countButtons.length > 0) {{
                                            console.log('找到count-button加號');
                                            const plusBtn = countButtons[0];
                                            for (let j = 0; j < ticketNumber; j++) {{
                                                plusBtn.click();
                                                console.log('➕ 點擊count-button加號 ' + (j + 1) + '/' + ticketNumber);
                                            }}
                                            resolve({{ success: true, action: 'count_button' }});
                                            return;
                                        }}

                                        // 尋找其他選擇按鈕
                                        const allButtons = targetPanel.querySelectorAll('button:not(.v-expansion-panel-header)');
                                        console.log('找到' + allButtons.length + '個按鈕');

                                        for (let btn of allButtons) {{
                                            const btnText = btn.textContent.toLowerCase().trim();
                                            console.log('[CHECK] 檢查按鈕:', btnText);

                                            if (btnText.includes('選擇') || btnText.includes('select') ||
                                                btn.classList.contains('select-btn') ||
                                                btn.classList.contains('v-btn--has-bg')) {{
                                                console.log('[TARGET] 找到選擇按鈕，點擊:', btnText);
                                                btn.click();
                                                resolve({{ success: true, action: 'select_button', text: btnText }});
                                                return;
                                            }}
                                        }}

                                        // 如果還沒找到且未超過最大嘗試次數，繼續尋找
                                        if (attempts < maxAttempts) {{
                                            setTimeout(findAction, 100);
                                        }} else {{
                                            console.log('[WARNING] 達到最大嘗試次數，未找到操作按鈕');
                                            resolve({{ success: false, action: 'none' }});
                                        }}
                                    }};

                                    // 立即開始第一次嘗試
                                    findAction();
                                }});
                            }};

                            // 使用 await 等待操作完成
                            const result = await waitAndFindAction();
                            console.log('[RESULT] 面板操作結果:', result);
                            return {{
                                success: true,
                                type: 'area_select',
                                selected: targetAreaName,
                                action_found: result.success,
                                action_type: result.action
                            }};
                        }}
                    }}
                }}

                console.log('[ERROR] 未找到任何可選的選項');
                return {{ success: false, message: '未找到可選的選項' }};
            }})();
        ''')

        result = util.parse_nodriver_result(js_result)
        if isinstance(result, dict):
            is_selected = result.get('success', False)
            if show_debug_message:
                if is_selected:
                    selected_type = result.get('type', '')
                    selected_name = result.get('selected', '')
                    print(f"Selection successful - type: {selected_type}, item: {selected_name}")
                else:
                    print(f"Selection failed: {result.get('message', 'unknown error')}")
        else:
            if show_debug_message:
                print(f"Unified selector returned invalid result: {result}")
            is_selected = False

    except Exception as exc:
        if show_debug_message:
            print(f"Unified selector exception error: {exc}")
        is_selected = False

    # 備用邏輯：如果選擇器失敗，檢查頁面狀態決定是否繼續
    if not is_selected:
        try:
            if show_debug_message:
                print("Checking page status to decide whether to continue...")

            # 檢查是否已經有票數被設定且下一步按鈕啟用
            page_status = await tab.evaluate('''
                (function() {
                    // 檢查是否有票數被設定（展開面板中的數字不是0）
                    const ticketCounts = document.querySelectorAll('.count-button div');
                    let hasTickets = false;
                    for (let count of ticketCounts) {
                        const text = count.textContent.trim();
                        if (text && !isNaN(text) && parseInt(text) > 0) {
                            hasTickets = true;
                            break;
                        }
                    }

                    // 檢查下一步按鈕是否啟用
                    const nextBtn = document.querySelector('button.nextBtn');
                    const buttonEnabled = nextBtn && !nextBtn.disabled && !nextBtn.classList.contains('v-btn--disabled') && !nextBtn.classList.contains('disabledBtn');

                    return {
                        hasTickets: hasTickets,
                        buttonEnabled: buttonEnabled,
                        buttonText: nextBtn ? nextBtn.textContent.trim() : '',
                        canContinue: hasTickets && buttonEnabled
                    };
                })();
            ''')

            status = util.parse_nodriver_result(page_status)
            if isinstance(status, dict):
                if show_debug_message:
                    print(f"[STATUS] 頁面狀態: 有票數={status.get('hasTickets', False)}, 按鈕啟用={status.get('buttonEnabled', False)}")

                if status.get('canContinue', False):
                    if show_debug_message:
                        print("Page status is good, considered selection successful")
                    is_selected = True

        except Exception as backup_exc:
            if show_debug_message:
                print(f"Backup check failed: {backup_exc}")

    return is_selected

async def nodriver_ticketplus_click_next_button_unified(tab, config_dict):
    """TicketPlus 統一下一步按鈕點擊器 - 不依賴 layout_style"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    if show_debug_message:
        print("Unified next button clicker started")

    try:
        # 先等待較長時間讓按鈕狀態更新（特別是展開面板後）
        if await sleep_with_pause_check(tab, 1.5, config_dict):
            return False

        js_result = await tab.evaluate('''
            (function() {
                console.log('🔄 統一下一步按鈕點擊器執行');

                // 等待按鈕狀態更新的函數
                function waitForButtonEnable(selector, maxWait = 10000) {
                    return new Promise((resolve) => {
                        const startTime = Date.now();
                        const checkButton = () => {
                            const button = document.querySelector(selector);
                            if (button && !button.disabled && !button.classList.contains('v-btn--disabled') && !button.classList.contains('disabledBtn')) {
                                resolve(button);
                                return;
                            }

                            if (Date.now() - startTime < maxWait) {
                                setTimeout(checkButton, 100);
                            } else {
                                resolve(null);
                            }
                        };
                        checkButton();
                    });
                }

                // 嘗試多種可能的下一步按鈕選擇器
                const buttonSelectors = [
                    'button.nextBtn:not(.disabledBtn):not(.v-btn--disabled)',
                    '.order-footer button.nextBtn:not(.disabledBtn)',
                    '.order-footer .v-btn--has-bg:not(.v-btn--disabled):not(.disabledBtn)',
                    'button:contains("下一步"):not(.disabledBtn)',
                    'button:contains("Next"):not(.disabledBtn)',
                    '.nextBtn:not([disabled])'
                ];

                // 首先嘗試直接找到啟用的按鈕
                let nextButton = null;
                for (let selector of buttonSelectors) {
                    nextButton = document.querySelector(selector);
                    if (nextButton && !nextButton.disabled && !nextButton.classList.contains('v-btn--disabled') && !nextButton.classList.contains('disabledBtn')) {
                        console.log('[SUCCESS] 找到啟用的下一步按鈕:', selector);
                        break;
                    }
                }

                // 如果沒有找到啟用的按鈕，等待一下
                if (!nextButton) {
                    console.log('⏳ 等待下一步按鈕啟用...');
                    return waitForButtonEnable('button.nextBtn, .nextBtn').then(button => {
                        if (button) {
                            console.log('[SUCCESS] 下一步按鈕已啟用');
                            button.click();
                            return {
                                success: true,
                                message: '下一步按鈕已點擊（等待後）',
                                buttonText: button.textContent.trim()
                            };
                        } else {
                            console.log('[ERROR] 等待後仍未找到可用的下一步按鈕');
                            return { success: false, message: '等待後仍未找到可用的下一步按鈕' };
                        }
                    });
                }

                // 點擊按鈕
                nextButton.click();
                console.log('[SUCCESS] 下一步按鈕已點擊');

                return {
                    success: true,
                    message: '下一步按鈕已點擊',
                    buttonText: nextButton.textContent.trim()
                };
            })();
        ''')

        result = util.parse_nodriver_result(js_result)
        if isinstance(result, dict):
            success = result.get('success', False)
            if show_debug_message:
                if success:
                    button_text = result.get('buttonText', '')
                    print(f"[SUCCESS] 下一步按鈕點擊成功 - 按鈕文字: {button_text}")
                else:
                    print(f"[ERROR] 下一步按鈕點擊失敗: {result.get('message', '未知錯誤')}")
            return success

    except Exception as exc:
        if show_debug_message:
            print(f"統一下一步按鈕點擊錯誤: {exc}")

    return False

async def nodriver_ticketplus_order_expansion_auto_select(tab, config_dict, area_keyword_item, current_layout_style):
    """TicketPlus 座位區域自動選擇功能 - 重構版使用純 JavaScript"""
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    ticket_number = config_dict["ticket_number"]

    if show_debug_message:
        print("current_layout_style:", current_layout_style)
        print("area_keyword_item:", area_keyword_item)
        print(f"target_ticket_number: {ticket_number}")

    is_need_refresh = False
    is_price_panel_expanded = False

    try:
        # 檢查暫停狀態
        if await check_and_handle_pause(config_dict):
            is_need_refresh = False
            is_price_assign_by_bot = False
            return is_need_refresh, is_price_assign_by_bot

        # 等待頁面元素載入完成 (關鍵修復)
        if show_debug_message:
            print("Waiting for page elements to load...")

        # 等待頁面元素載入（符合用戶要求：0.8-1.5 秒等待時間，包含暫停檢查）
        if await sleep_with_pause_check(tab, 1.0, config_dict):
            if show_debug_message:
                print("Paused during page element loading")
            return False, False

        # 使用純 JavaScript 處理展開面板選擇和票數設定（包含暫停檢查）
        result = await evaluate_with_pause_check(tab, f'''
            (function() {{
                try {{
                const ticketAreas = [];
                console.log('=== TicketPlus 票種區域檢測開始 ===');
                console.log('版面樣式: {current_layout_style}');

                let elements = [];
                let isExpansionPanel = false;

                // 嘗試找 expansion panel 版面 (增強版偵測，加入重試機制)
                let expansionPanels = document.querySelectorAll('.v-expansion-panels.seats-area .v-expansion-panel');

                // 如果第一次沒找到，嘗試其他選擇器
                if (expansionPanels.length === 0) {{
                    expansionPanels = document.querySelectorAll('.v-expansion-panels .v-expansion-panel');
                    console.log('使用備用選擇器找到 expansion panels 數量:', expansionPanels.length);
                }}

                if (expansionPanels.length > 0) {{
                    console.log('[SUCCESS] 找到 expansion panels 數量:', expansionPanels.length);
                    elements = Array.from(expansionPanels);
                    isExpansionPanel = true;
                }} else {{
                    // 使用簡單 row 版面 - 增強版多選擇器策略
                    let ticketRows = [];

                    // 策略1: Page1/Page3 標準 row 選擇器
                    ticketRows = document.querySelectorAll('.row.py-1.py-md-4.rwd-margin.no-gutters.text-title');
                    console.log('🔎 策略1 (標準row) 找到數量:', ticketRows.length);

                    // 策略2: 更寬鬆的 row 選擇器
                    if (ticketRows.length === 0) {{
                        ticketRows = document.querySelectorAll('.rwd-margin .row.py-1.py-md-4');
                        console.log('🔎 策略2 (寬鬆row) 找到數量:', ticketRows.length);
                    }}

                    // 策略3: 通過 count-button 反向查找父級 row
                    if (ticketRows.length === 0) {{
                        const countButtons = document.querySelectorAll('.count-button');
                        console.log('🔎 策略3 找到 count-button 數量:', countButtons.length);
                        if (countButtons.length > 0) {{
                            const rows = new Set();
                            countButtons.forEach(cb => {{
                                const row = cb.closest('.row');
                                if (row) rows.add(row);
                            }});
                            ticketRows = Array.from(rows);
                            console.log('🔎 策略3 通過 count-button 找到 row 數量:', ticketRows.length);
                        }}
                    }}

                    // 策略4: 通用 row 類別選擇器
                    if (ticketRows.length === 0) {{
                        ticketRows = document.querySelectorAll('.row[class*="py-"]');
                        console.log('🔎 策略4 (通用row) 找到數量:', ticketRows.length);
                    }}

                    // 策略5: 包含價格的容器
                    if (ticketRows.length === 0) {{
                        ticketRows = document.querySelectorAll('[class*="row"]:has(.font-weight-bold)');
                        console.log('🔎 策略5 (有價格) 找到數量:', ticketRows.length);
                    }}

                    elements = Array.from(ticketRows);
                    isExpansionPanel = false;
                    console.log('[INFO] 最終使用 row 版面，元素數量:', elements.length);
                }}

                if (elements.length > 0) {{
                    for (let i = 0; i < elements.length; i++) {{
                        const element = elements[i];
                        let text = '';
                        let areaName = '';
                        let priceMatch = null;

                        if (isExpansionPanel) {{
                            // expansion panel 版面 (增強版解析)
                            const header = element.querySelector('.v-expansion-panel-header');
                            if (header) {{
                                text = header.textContent?.trim() || '';
                                priceMatch = text.match(/NT\\.?([\\d,]+)/);

                                // 優先從第二個 d-flex 取得區域名稱（避開 area-color）
                                let areaDiv = header.querySelector('.col.col-8 .d-flex.align-center:last-child') ||
                                            header.querySelector('.d-flex.align-center:not(:has(.area-color))') ||
                                            header.querySelector('.d-flex.align-center');

                                if (areaDiv) {{
                                    const textContent = areaDiv.textContent?.trim() || '';
                                    // 移除狀態標籤和剩餘數量
                                    const nameMatch = textContent.match(/^\\s*([^剩餘熱賣<]+?)(?:\\s*剩餘|\\s*熱賣|\\s*<|$)/);
                                    areaName = nameMatch ? nameMatch[1].trim() : textContent.split('\\n')[0].trim();
                                    console.log('區域名稱解析: "' + textContent + '" -> "' + areaName + '"');
                                }}
                            }}
                        }} else {{
                            // 簡單 row 版面
                            text = element.textContent?.trim() || '';

                            // 從第一個 col 取得票種名稱
                            const nameDiv = element.querySelector('.font-weight-medium');
                            if (nameDiv) {{
                                areaName = nameDiv.textContent?.trim() || '';
                                // 移除狀態標籤（如 "熱賣中"）
                                areaName = areaName.replace(/\\s*(熱賣中|已售完|剩餘.*?)\\s*$/, '').trim();
                            }}

                            // 從價格 col 取得價格 (修復跨行文本問題)
                            const priceDiv = element.querySelector('.font-weight-bold');
                            if (priceDiv) {{
                                const priceText = priceDiv.textContent?.replace(/\\s+/g, ' ').trim() || '';
                                priceMatch = priceText.match(/NT\\.?\\s*([\\d,]+)/);
                                console.log('價格文本解析: "' + priceDiv.textContent + '" -> "' + priceText + '"');
                            }}
                        }}

                        console.log('Element ' + (i + 1) + ': 區域="' + areaName + '", 價格匹配=' + !!priceMatch + ', 版面=' + (isExpansionPanel ? 'expansion' : 'row'));

                        // 檢查是否售完
                        const isSoldOut = element.querySelector('.soldout') !== null ||
                                        text.includes('剩餘 0') ||
                                        text.includes('已售完') ||
                                        element.querySelector('button[disabled]');

                        console.log('  - 售完狀態: ' + isSoldOut);

                        // 檢查排除關鍵字 (修復字串轉義問題)
                        const excludeKeywords = {json.dumps(config_dict.get('keyword_exclude', ''))};
                        const isExcluded = excludeKeywords && excludeKeywords.split(',').some(keyword => {{
                            const cleanKeyword = keyword.trim().replace(/"/g, '');
                            return cleanKeyword && (text.includes(cleanKeyword) || areaName.includes(cleanKeyword));
                        }});
                        console.log('  - 排除檢查: ' + isExcluded + ' (關鍵字: ' + excludeKeywords + ')');

                        // 檢查是否有票數控制項 (修復 expansion panel 邏輯)
                        const hasCounter = isExpansionPanel ? true : element.querySelector('.count-button') !== null;
                        console.log('  - 有控制項: ' + hasCounter + ' (expansion panel: ' + isExpansionPanel + ')');
                        console.log('  - 價格匹配: ' + !!priceMatch + ' (價格: ' + (priceMatch ? priceMatch[1] : 'null') + ')');
                        console.log('  - 區域名稱: "' + areaName + '" (長度: ' + areaName.length + ')');
                        console.log('  - 包含票區一覽: ' + areaName.includes('票區一覽'));

                        // 驗證條件
                        const hasPrice = priceMatch !== null;
                        const hasValidName = areaName && areaName.length > 0;
                        const notOverview = !areaName.includes('票區一覽');
                        const notSoldOut = !isSoldOut;
                        const notExcluded = !isExcluded;

                        console.log('  - 驗證: 價格=' + hasPrice + ', 名稱=' + hasValidName + ', 非一覽=' + notOverview + ', 未售完=' + notSoldOut + ', 非排除=' + notExcluded + ', 有控制項=' + hasCounter);

                        if (hasPrice && hasValidName && notOverview && notSoldOut && notExcluded && hasCounter) {{
                            ticketAreas.push({{
                                element: element,
                                text: text,
                                areaName: areaName,
                                price: priceMatch[1],
                                hasCounter: hasCounter,
                                isExpansionPanel: isExpansionPanel
                            }});
                            console.log('  [SUCCESS] 有效票種區域已加入');
                        }} else {{
                            console.log('  [SKIP] 跳過此元素');
                        }}
                    }}
                }}

                console.log('總共找到有效票種區域:', ticketAreas.length);

                if (ticketAreas.length === 0) {{
                    console.error('[ERROR] 沒有找到可用的票種區域');
                    console.log('總元素數量:', elements.length);
                    console.log('Expansion panels:', expansionPanels.length);
                    return {{
                        success: false,
                        error: "沒有找到可用的票種區域 (已等待頁面載入)",
                        needRefresh: true,
                        panelExpanded: false,
                        debug: {{
                            totalElements: elements.length,
                            expansionPanelsFound: expansionPanels.length,
                            isExpansionPanelMode: isExpansionPanel
                        }}
                    }};
                }}

                // 關鍵字匹配邏輯 (修復優先順序)
                let selectedArea = null;
                const areaKeyword = "{area_keyword_item}".trim();

                // 優先處理使用者關鍵字 (修復核心邏輯)
                if (areaKeyword && areaKeyword.length > 0) {{
                    console.log('[SEARCH] 優先使用關鍵字搜尋:', areaKeyword);
                    const keywordArray = areaKeyword.split(' ').map(k => k.trim()).filter(k => k);

                    // 嘗試完全匹配
                    for (const area of ticketAreas) {{
                        let isMatch = true;
                        for (const keyword of keywordArray) {{
                            if (!area.text.includes(keyword) && !area.areaName.includes(keyword)) {{
                                isMatch = false;
                                break;
                            }}
                        }}
                        if (isMatch) {{
                            selectedArea = area;
                            console.log('[SUCCESS] 關鍵字完全匹配:', area.areaName);
                            break;
                        }}
                    }}

                    // 如果完全匹配失敗，嘗試部分匹配
                    if (!selectedArea) {{
                        for (const keyword of keywordArray) {{
                            for (const area of ticketAreas) {{
                                if (area.text.includes(keyword) || area.areaName.includes(keyword)) {{
                                    selectedArea = area;
                                    console.log('[WARNING] 關鍵字部分匹配:', area.areaName, '匹配詞:', keyword);
                                    break;
                                }}
                            }}
                            if (selectedArea) break;
                        }}
                    }}
                }}

                // 如果關鍵字無匹配，才使用自動選擇模式
                if (!selectedArea) {{
                    console.log('🤖 關鍵字無匹配，使用自動選擇模式:', "{auto_select_mode}");
                    if (ticketAreas.length > 0) {{
                        const mode = "{auto_select_mode}";
                        if (mode === "from bottom to top") {{
                            selectedArea = ticketAreas[ticketAreas.length - 1];
                            console.log('選擇最後一個:', selectedArea.areaName);
                        }} else if (mode === "random") {{
                            const randomIndex = Math.floor(Math.random() * ticketAreas.length);
                            selectedArea = ticketAreas[randomIndex];
                            console.log('隨機選擇:', selectedArea.areaName);
                        }} else {{
                            selectedArea = ticketAreas[0];
                            console.log('選擇第一個:', selectedArea.areaName);
                        }}
                    }}
                }}

                if (!selectedArea) {{
                    return {{
                        success: false,
                        error: "找不到符合條件的票種區域",
                        needRefresh: true,
                        panelExpanded: false,
                        foundAreas: ticketAreas.length,
                        keywords: areaKeyword ? areaKeyword.split(' ') : []
                    }};
                }}

                console.log('最終選中區域:', selectedArea.areaName);

                // 處理展開面板或直接選擇
                const area = selectedArea.element;
                let ticketSet = false;

                if (selectedArea.isExpansionPanel) {{
                    // expansion panel 版面：需要先展開
                    const header = area.querySelector('.v-expansion-panel-header');
                    if (header) {{
                        console.log('開始展開票種區域: ' + selectedArea.areaName);

                        // 1. 先點擊 header 展開面板
                        header.click();

                        // 2. 設置選中狀態（修復 seats-area is-select 問題）
                        const seatsArea = area.closest('.seats-area') || area.parentElement;
                        if (seatsArea) {{
                            // 移除其他選中狀態
                            document.querySelectorAll('.seats-area.is-select').forEach(el => {{
                                el.classList.remove('is-select');
                            }});

                            // 設置當前選中
                            seatsArea.classList.add('is-select');
                            console.log('已設置選中狀態: seats-area is-select');

                            // 觸發 Vue 事件確保狀態同步
                            seatsArea.dispatchEvent(new Event('click', {{bubbles: true}}));
                        }}

                        console.log('[SUCCESS] Panel 已展開，返回等待動畫完成');
                        return {{
                            success: true,
                            needTicketSetting: true,
                            areaName: selectedArea.areaName,
                            isExpansionPanel: true
                        }};
                    }}
                }} else {{
                    // 簡單 row 版面：直接設定票數
                    console.log('簡單版面，直接設定票數: ' + selectedArea.areaName);
                    const countButtons = area.querySelectorAll('.count-button');
                    const ticketSet = setTicketCount(countButtons, {ticket_number});
                    return {{
                        success: true,
                        needTicketSetting: false,
                        areaName: selectedArea.areaName,
                        ticketSet: ticketSet,
                        isExpansionPanel: false
                    }};
                }}

                // 票數設定輔助函數 (改為同步)
                function setTicketCount(countButtons, targetCount) {{
                    for (const countButton of countButtons) {{
                        // 多種選擇器策略
                        const countDiv = countButton.querySelector('div:not(.v-btn__content):not(.v-btn)') ||
                                       countButton.querySelector('div') ||
                                       countButton.querySelector('input[readonly]');

                        const plusButton = countButton.querySelector('button[class*="plus"]') ||
                                         countButton.querySelector('button .mdi-plus') ||
                                         countButton.querySelector('button:not([disabled]):last-child');

                        if (countDiv && plusButton && !plusButton.disabled) {{
                            let currentCount = 0;
                            const countText = countDiv.textContent?.trim() || countDiv.value || '0';
                            if (/^\\d+$/.test(countText)) {{
                                currentCount = parseInt(countText);
                            }}

                            console.log('找到票數控制項，當前數量:', currentCount, '目標數量:', targetCount);

                            if (currentCount < targetCount) {{
                                const clicksNeeded = Math.min(targetCount - currentCount, 10);
                                console.log('需要點擊加號', clicksNeeded, '次');

                                for (let i = 0; i < clicksNeeded; i++) {{
                                    if (!plusButton.disabled) {{
                                        plusButton.click();
                                        // 移除 await，改為快速點擊
                                    }}
                                }}
                                console.log('票數設定完成');
                                return true;
                            }} else {{
                                console.log('票數已足夠');
                                return true;
                            }}
                        }}
                    }}
                    console.log('警告：未找到有效的票數控制項');
                    return false;
                }}

                // 這裡不會執行到，因為上面已經有 return 了
                return {{
                    success: false,
                    error: "未預期的執行路徑",
                    needRefresh: true,
                    panelExpanded: false
                }};
                }} catch (error) {{
                    console.error('JavaScript 執行錯誤:', error);
                    return {{
                        success: false,
                        error: 'JavaScript 執行錯誤: ' + error.message,
                        needRefresh: true,
                        panelExpanded: false
                    }};
                }}
            }})();
        ''')

        # 檢查是否因暫停而中斷
        if result is None:
            if show_debug_message:
                print("JavaScript execution interrupted due to pause")
            return False, False

        # 處理 JavaScript 執行結果
        parsed_result = util.parse_nodriver_result(result)

        if show_debug_message:
            print(f"JavaScript 執行原始結果類型: {type(result)}")
            print(f"解析後結果類型: {type(parsed_result)}")

        if isinstance(parsed_result, dict):
            if parsed_result.get('success'):
                is_price_panel_expanded = parsed_result.get('panelExpanded', True)
                is_need_refresh = parsed_result.get('needRefresh', False)

                # 檢查是否需要第二步票數設定
                if parsed_result.get('needTicketSetting', False):
                    if show_debug_message:
                        area_name = parsed_result.get('areaName', '未知')
                        print(f"Successfully expanded area: {area_name}")
                        print("Waiting for animation to complete...")

                    # 等待展開動畫完成（包含暫停檢查）
                    if await asyncio_sleep_with_pause_check(0.5, config_dict):
                        if show_debug_message:
                            print("Paused while waiting for animation")
                        return False, False

                    # 第二步：設定票數
                    ticket_result = await _set_expansion_panel_tickets(tab, ticket_number, show_debug_message)
                    if ticket_result:
                        is_price_panel_expanded = True
                        is_need_refresh = False
                        if show_debug_message:
                            print("Ticket count setting completed")
                    else:
                        is_need_refresh = True
                        if show_debug_message:
                            print("Ticket count setting failed")
                else:
                    # 簡單版面，已經完成票數設定
                    if show_debug_message:
                        area_name = parsed_result.get('areaName', '未知')
                        ticket_set = parsed_result.get('ticketSet', False)
                        print(f"Successfully selected area: {area_name}")
                        print(f"Ticket count setting: {'completed' if ticket_set else 'failed'}")
            else:
                is_need_refresh = parsed_result.get('needRefresh', True)
                error_msg = parsed_result.get('error', '未知錯誤')
                if show_debug_message:
                    print(f"Selection failed: {error_msg}")
                    if 'foundAreas' in parsed_result:
                        print(f"找到 {parsed_result['foundAreas']} 個區域")
                    if 'debug' in parsed_result:
                        debug_info = parsed_result['debug']
                        print(f"Debug: Total elements={debug_info.get('totalElements', 0)}, Expansion panels={debug_info.get('expansionPanelsFound', 0)}, Mode={debug_info.get('isExpansionPanelMode', False)}")
        else:
            is_need_refresh = True
            if show_debug_message:
                print(f"[ERROR] JavaScript 執行結果格式錯誤: {parsed_result}")
                print(f"原始結果: {result}")

    except Exception as exc:
        is_need_refresh = True
        if show_debug_message:
            print(f"[ERROR] 展開面板選擇失敗: {exc}")

    return is_need_refresh, is_price_panel_expanded

async def _set_expansion_panel_tickets(tab, ticket_number, show_debug_message):
    """設定展開後的 expansion panel 票數"""
    try:
        result = await tab.evaluate(f'''
            (function() {{
                try {{
                    // 尋找展開後的票數控制項
                    const expandedContent = document.querySelector('.v-expansion-panel-content:not([style*="display: none"])');
                    if (!expandedContent) {{
                        return {{ success: false, error: "未找到展開的 panel 內容" }};
                    }}

                    const countButtons = expandedContent.querySelectorAll('.count-button');
                    if (countButtons.length === 0) {{
                        return {{ success: false, error: "未找到票數控制項" }};
                    }}

                    // 使用與原有相同的票數設定邏輯
                    for (const countButton of countButtons) {{
                        const countDiv = countButton.querySelector('div:not(.v-btn__content):not(.v-btn)') ||
                                       countButton.querySelector('div') ||
                                       countButton.querySelector('input[readonly]');

                        const plusButton = countButton.querySelector('button[class*="plus"]') ||
                                         countButton.querySelector('button .mdi-plus') ||
                                         countButton.querySelector('button:not([disabled]):last-child');

                        if (countDiv && plusButton && !plusButton.disabled) {{
                            let currentCount = 0;
                            const countText = countDiv.textContent?.trim() || countDiv.value || '0';
                            if (/^\\d+$/.test(countText)) {{
                                currentCount = parseInt(countText);
                            }}

                            console.log('找到票數控制項，當前數量:', currentCount, '目標數量:', {ticket_number});

                            if (currentCount < {ticket_number}) {{
                                const clicksNeeded = Math.min({ticket_number} - currentCount, 10);
                                console.log('需要點擊加號', clicksNeeded, '次');

                                for (let i = 0; i < clicksNeeded; i++) {{
                                    if (!plusButton.disabled) {{
                                        plusButton.click();
                                    }}
                                }}
                                console.log('票數設定完成');
                                return {{ success: true }};
                            }} else {{
                                console.log('票數已足夠');
                                return {{ success: true }};
                            }}
                        }}
                    }}
                    return {{ success: false, error: "未找到有效的票數控制項" }};
                }} catch (error) {{
                    console.error('票數設定錯誤:', error);
                    return {{ success: false, error: 'JavaScript 執行錯誤: ' + error.message }};
                }}
            }})();
        ''')

        parsed_result = util.parse_nodriver_result(result)
        if show_debug_message:
            print(f"票數設定結果: {parsed_result}")

        return isinstance(parsed_result, dict) and parsed_result.get('success', False)

    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] 票數設定失敗: {exc}")
        return False

async def nodriver_ticketplus_assign_ticket_number(tab, target_area, config_dict):
    """TicketPlus 票券數量設定功能 - 重構版，支援兩種佈局"""
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # 檢查暫停狀態
    if await check_and_handle_pause(config_dict):
        return False

    target_ticket_number = config_dict["ticket_number"]

    if show_debug_message:
        print(f"=== assign_ticket_number START (目標數量: {target_ticket_number}) ===")

    try:
        # 使用純 JavaScript 處理票數選擇，支援兩種佈局
        result = await tab.evaluate(f'''
            (function() {{
                const targetNumber = {target_ticket_number};

                try {{
                    // 多種選擇器策略，支援不同佈局
                    const selectors = [
                        'div.count-button > div',           // 標準選擇器
                        '.count-button div:not(.v-btn__content)',  // 排除按鈕內容的 div
                        '.row.rwd-margin .count-button div'  // 更具體的選擇器
                    ];

                    let countDiv = null;
                    let plusButton = null;

                    // 找到有效的計數器和按鈕
                    for (let selector of selectors) {{
                        const divs = document.querySelectorAll(selector);
                        for (let div of divs) {{
                            const parentCountButton = div.closest('.count-button');
                            if (parentCountButton) {{
                                const buttons = parentCountButton.querySelectorAll('button');
                                const plus = Array.from(buttons).find(btn => {{
                                    const icon = btn.querySelector('i.mdi-plus, .mdi-plus, [class*="plus"]');
                                    return icon && !btn.disabled;
                                }});

                                if (plus) {{
                                    countDiv = div;
                                    plusButton = plus;
                                    break;
                                }}
                            }}
                        }}
                        if (countDiv && plusButton) break;
                    }}

                    if (!countDiv || !plusButton) {{
                        return {{
                            success: false,
                            error: "找不到計數器或加號按鈕",
                            found_div: !!countDiv,
                            found_button: !!plusButton
                        }};
                    }}

                    // 取得目前數量
                    let currentCount = 0;
                    const countText = countDiv.textContent?.trim() || '0';
                    if (/^\\d+$/.test(countText)) {{
                        currentCount = parseInt(countText);
                    }}

                    if (currentCount >= targetNumber) {{
                        return {{
                            success: true,
                            message: "數量已足夠",
                            currentCount: currentCount,
                            targetCount: targetNumber,
                            clickCount: 0
                        }};
                    }}

                    // 計算需要點擊的次數
                    const needClicks = targetNumber - currentCount;
                    let actualClicks = 0;

                    // 點擊加號按鈕
                    for (let i = 0; i < needClicks && i < 10; i++) {{
                        if (plusButton.disabled) {{
                            break;
                        }}

                        plusButton.click();
                        actualClicks++;

                        // 等待 UI 更新
                        const maxWait = 50; // 最多等待 50 * 10ms = 500ms
                        let waitCount = 0;
                        let newCount = currentCount;

                        while (waitCount < maxWait) {{
                            const newText = countDiv.textContent?.trim() || '0';
                            if (/^\\d+$/.test(newText)) {{
                                newCount = parseInt(newText);
                                if (newCount > currentCount + i) {{
                                    break;
                                }}
                            }}
                            waitCount++;
                            // 同步等待 10ms
                            const startTime = Date.now();
                            while (Date.now() - startTime < 10) {{ /* 忙等待 */ }}
                        }}

                        // 檢查是否達到目標
                        if (newCount >= targetNumber) {{
                            break;
                        }}
                    }}

                    // 最終檢查
                    const finalText = countDiv.textContent?.trim() || '0';
                    const finalCount = /^\\d+$/.test(finalText) ? parseInt(finalText) : 0;

                    return {{
                        success: finalCount > currentCount,
                        currentCount: currentCount,
                        finalCount: finalCount,
                        targetCount: targetNumber,
                        clickCount: actualClicks,
                        message: finalCount >= targetNumber ? "達到目標數量" : "部分完成"
                    }};

                }} catch (error) {{
                    return {{
                        success: false,
                        error: "JavaScript執行錯誤: " + error.message
                    }};
                }}
            }})();
        ''')

        # 使用統一解析函數處理返回值
        result = util.parse_nodriver_result(result)

        # 處理結果
        success = False
        if isinstance(result, dict):
            success = result.get('success', False)
            if show_debug_message:
                if success:
                    current = result.get('currentCount', 0)
                    final = result.get('finalCount', 0)
                    clicks = result.get('clickCount', 0)
                    message = result.get('message', '')
                    print(f"[SUCCESS] 票數設定成功: {current} -> {final} (點擊 {clicks} 次) - {message}")
                else:
                    error = result.get('error', '未知錯誤')
                    print(f"✗ 票數設定失敗: {error}")
                    # 顯示除錯資訊
                    if 'found_div' in result:
                        print(f"  找到計數器: {result.get('found_div')}")
                    if 'found_button' in result:
                        print(f"  找到按鈕: {result.get('found_button')}")
        else:
            if show_debug_message:
                print(f"✗ 票數設定失敗: 返回結果格式錯誤 - {result}")

        if show_debug_message:
            print(f"=== assign_ticket_number END (結果: {'成功' if success else '失敗'}) ===")

        return success

    except Exception as exc:
        if show_debug_message:
            print(f"✗ assign_ticket_number 異常: {exc}")
        return False

async def nodriver_ticketplus_ticket_agree(tab, config_dict):
    """TicketPlus 同意條款勾選功能"""
    show_debug_message = config_dict["advanced"].get("verbose", False)
    is_finish_checkbox_click = False

    # 查找同意條款 checkbox
    try:
        agree_checkbox_list = await tab.query_selector_all('input[type="checkbox"]')

        for checkbox in agree_checkbox_list:
            try:
                # 檢查 checkbox 是否為 None 或無效
                if not checkbox:
                    continue

                # 檢查 checkbox 是否已勾選
                is_checked = await checkbox.evaluate('el => el.checked')

                if not is_checked:
                    # 嘗試點擊勾選
                    await checkbox.click()

                    # 確認是否勾選成功
                    is_checked_after = await checkbox.evaluate('el => el.checked')
                    if is_checked_after:
                        is_finish_checkbox_click = True
                        if show_debug_message:
                            print("successfully checked agreement checkbox")
                    else:
                        # 如果直接點擊失敗，嘗試 JavaScript 方式
                        if checkbox:  # 再次確認 checkbox 不是 None
                            await tab.evaluate('''
                                (checkbox) => {
                                    if (checkbox) {
                                        checkbox.checked = true;
                                        checkbox.dispatchEvent(new Event('change', {bubbles: true}));
                                    }
                                }
                            ''', checkbox)

                            final_check = await checkbox.evaluate('el => el.checked')
                            if final_check:
                                is_finish_checkbox_click = True
                                if show_debug_message:
                                    print("successfully checked agreement checkbox via JS")
                else:
                    is_finish_checkbox_click = True
                    if show_debug_message:
                        print("agreement checkbox already checked")

            except Exception as exc:
                if show_debug_message:
                    print("process checkbox fail:", exc)
                continue

    except Exception as exc:
        if show_debug_message:
            print("find agreement checkbox fail:", exc)

    return is_finish_checkbox_click

async def nodriver_ticketplus_accept_realname_card(tab):
    """接受實名制卡片彈窗"""
    is_button_clicked = False
    try:
        # 查找並點擊實名制確認按鈕
        button = await tab.query_selector('div.v-dialog__content > div > div > div > div.row > div > button.primary')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked

async def nodriver_ticketplus_accept_other_activity(tab):
    """接受其他活動彈窗"""
    is_button_clicked = False
    try:
        # 查找並點擊其他活動確認按鈕
        button = await tab.query_selector('div[role="dialog"] > div.v-dialog > button.primary-1 > span > i.v-icon')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked

async def nodriver_ticketplus_accept_order_fail(tab):
    """處理訂單失敗彈窗"""
    is_button_clicked = False
    try:
        # 查找並點擊訂單失敗確認按鈕
        button = await tab.query_selector('div[role="dialog"] > div.v-dialog > div.v-card > div > div.row > div.col > button.v-btn')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked

async def check_and_handle_pause(config_dict=None):
    """檢查暫停檔案並處理暫停狀態"""
    if os.path.exists(CONST_MAXBOT_INT28_FILE):
        show_debug = config_dict and config_dict["advanced"].get("verbose", False)
        if show_debug:
            print("🛑 偵測到暫停指令")
        return True
    return False

# === 暫停機制改進：增強版暫停檢查函數 ===
# 為了讓 NoDriver 的暫停功能接近 Chrome 版本的即時反應性，
# 新增以下輔助函數在關鍵操作點檢查暫停狀態：
# 1. sleep_with_pause_check: tab.sleep() 的暫停檢查版本
# 2. asyncio_sleep_with_pause_check: asyncio.sleep() 的暫停檢查版本
# 3. evaluate_with_pause_check: JavaScript 執行前的暫停檢查版本
# 4. with_pause_check: 任務包裝器，支援中途暫停

async def sleep_with_pause_check(tab, seconds, config_dict=None):
    """延遲等待並檢查暫停狀態"""
    if await check_and_handle_pause(config_dict):
        return True  # 暫停中
    await tab.sleep(seconds)
    return False  # 未暫停

async def asyncio_sleep_with_pause_check(seconds, config_dict=None):
    """asyncio.sleep 並檢查暫停狀態"""
    import asyncio
    if await check_and_handle_pause(config_dict):
        return True  # 暫停中
    await asyncio.sleep(seconds)
    return False  # 未暫停

async def evaluate_with_pause_check(tab, javascript_code, config_dict=None):
    """執行 JavaScript 前檢查暫停狀態"""
    if await check_and_handle_pause(config_dict):
        return None  # 暫停中，返回 None
    try:
        return await tab.evaluate(javascript_code)
    except Exception as exc:
        show_debug = config_dict and config_dict["advanced"].get("verbose", False)
        if show_debug:
            print(f"JavaScript 執行失敗: {exc}")
        return None

async def with_pause_check(task_func, config_dict, *args, **kwargs):
    """包裝函數，支援暫停中斷機制"""
    import asyncio

    # 先檢查一次暫停狀態
    if await check_and_handle_pause(config_dict):
        return None

    # 創建任務但不立即等待
    task = asyncio.create_task(task_func(*args, **kwargs))

    # 在任務執行過程中定期檢查暫停狀態
    while not task.done():
        if await check_and_handle_pause(config_dict):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return None
        await asyncio.sleep(0.05)  # 每 50ms 檢查一次

    return await task

async def nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False):
    """檢查排隊狀態 - 優化版，避免重複輸出"""
    show_debug_message = config_dict["advanced"].get("verbose", False) or force_show_debug

    try:
        result = await tab.evaluate('''
            (function() {
                // 檢查排隊中的關鍵字
                const queueKeywords = [
                    '排隊購票中',
                    '請稍候',
                    '請別離開頁面',
                    '請勿離開',
                    '請勿關閉網頁',
                    '同時使用多個裝置',
                    '正在處理',
                    '處理中'
                ];

                const bodyText = document.body.textContent || '';

                // 檢查是否有排隊中的標題
                const queueTitle = document.querySelector('h3[data-v-9c1a94a8].mt-4');
                const hasQueueTitle = queueTitle && queueTitle.textContent.includes('排隊購票中');

                // 檢查是否包含任何排隊關鍵字
                const hasQueueKeyword = queueKeywords.some(keyword => bodyText.includes(keyword));

                // 檢查是否有遮罩層（排隊中的視覺指示）
                const overlayScrim = document.querySelector('.v-overlay__scrim');
                const hasOverlay = overlayScrim &&
                    (overlayScrim.style.opacity === '1' ||
                     overlayScrim.style.display !== 'none');

                // 檢查對話框中的排隊訊息
                const dialogText = document.querySelector('.v-dialog')?.textContent || '';
                const hasQueueDialog = dialogText.includes('排隊') ||
                                       dialogText.includes('請稍候');

                // 返回匹配的關鍵字列表（字串格式）
                const foundKeywords = queueKeywords.filter(keyword => bodyText.includes(keyword));

                return {
                    inQueue: hasQueueTitle || hasQueueKeyword || hasOverlay || hasQueueDialog,
                    queueTitle: hasQueueTitle ? queueTitle.textContent : '',
                    foundKeywords: foundKeywords,
                    hasOverlay: hasOverlay,
                    hasQueueDialog: hasQueueDialog,
                    dialogText: hasQueueDialog ? dialogText.trim() : ''
                };
            })();
        ''')

        result = util.parse_nodriver_result(result)

        if isinstance(result, dict):
            is_in_queue = result.get('inQueue', False)
            # 只在強制顯示或首次偵測時才輸出詳細資訊
            if show_debug_message and is_in_queue and force_show_debug:
                print(f"🔄 偵測到排隊狀態")
                if result.get('queueTitle'):
                    print(f"   排隊標題: {result.get('queueTitle')}")
                if result.get('hasOverlay'):
                    print("   發現遮罩層 (v-overlay__scrim)")
                if result.get('hasQueueDialog'):
                    print(f"   對話框內容: {result.get('dialogText', '')}")
                if result.get('foundKeywords'):
                    keywords = result.get('foundKeywords', [])
                    # 處理可能的 dict 格式（NoDriver 特殊返回）
                    if keywords and isinstance(keywords[0], dict):
                        keywords = [str(k.get('value', k)) for k in keywords]
                    elif keywords:
                        keywords = [str(k) for k in keywords]  # 確保都是字串
                    if keywords:
                        print(f"   找到關鍵字: {', '.join(keywords)}")
            return is_in_queue

        return False

    except Exception as exc:
        if show_debug_message:
            print(f"排隊狀態檢測錯誤: {exc}")
        return False

async def nodriver_ticketplus_order_auto_reload_coming_soon(tab):
    """自動重載即將開賣的頁面"""
    is_reloading = False

    try:
        # 使用 JavaScript 檢查產品狀態並自動重載
        js_code = '''
        (async function() {
            try {
                // 查找 API URL
                const entries = performance.getEntries();
                let apiUrl = null;

                for (const entry of entries) {
                    if (entry.name && entry.name.includes('apis.ticketplus.com.tw/config/api/')) {
                        if (entry.name.includes('get?productId=') || entry.name.includes('get?ticketAreaId=')) {
                            apiUrl = entry.name;
                            break;
                        }
                    }
                }

                if (!apiUrl) return false;

                // 取得產品資訊
                const response = await fetch(apiUrl);
                const data = await response.json();

                // 檢查是否為 pending 狀態
                if (data.result && data.result.product && data.result.product.length > 0) {
                    if (data.result.product[0].status === "pending") {
                        // 重新載入頁面
                        location.reload();
                        return true;
                    }
                }

                return false;
            } catch (err) {
                return false;
            }
        })();
        '''

        result = await tab.evaluate(js_code)
        is_reloading = bool(result)

    except Exception as exc:
        pass

    return is_reloading

async def nodriver_ticketplus_confirm(tab, config_dict):
    """確認訂單頁面處理"""
    # 先確認勾選同意條款
    is_checkbox_checked = await nodriver_ticketplus_ticket_agree(tab, config_dict)

    # 查找並點擊確認按鈕
    is_confirm_clicked = False
    if is_checkbox_checked:
        try:
            # 嘗試找到確認訂單按鈕
            confirm_button = await tab.query_selector('button.v-btn.primary')
            if not confirm_button:
                confirm_button = await tab.query_selector('button[type="submit"]')

            if confirm_button:
                # 檢查按鈕是否可用
                is_enabled = await tab.evaluate('''
                    (function(button) {
                        return button && !button.disabled && button.offsetParent !== null;
                    })(arguments[0]);
                ''', confirm_button)

                if is_enabled:
                    await confirm_button.click()
                    is_confirm_clicked = True
        except Exception as exc:
            pass

    return is_confirm_clicked

async def nodriver_ticketplus_order(tab, config_dict, ocr, Captcha_Browser, ticketplus_dict):
    """TicketPlus 訂單處理 - 支援三種佈局偵測"""

    show_debug_message = config_dict["advanced"].get("verbose", False)

    # 檢查是否已經成功選票，避免重複執行
    if ticketplus_dict.get("is_ticket_assigned", False):
        if show_debug_message:
            print("Ticket selection completed, skipping duplicate execution")
        return ticketplus_dict

    if show_debug_message:
        print("=== TicketPlus Auto Layout Detection Started ===")

    # 等待頁面載入完成，避免找不到按鈕（包含暫停檢查）
    if await sleep_with_pause_check(tab, 0.8, config_dict):
        if show_debug_message:
            print("Paused during page wait")
        return ticketplus_dict

    # 偵測頁面佈局樣式（包含暫停檢查）
    layout_info = await nodriver_ticketplus_detect_layout_style(tab, config_dict)

    # 檢查是否在佈局偵測時暫停
    if layout_info and layout_info.get('paused'):
        if show_debug_message:
            print("Paused during layout detection")
        return ticketplus_dict

    current_layout_style = layout_info.get('style', 0) if isinstance(layout_info, dict) else 0

    if show_debug_message:
        layout_names = {1: "展開面板型 (Page4)", 2: "座位選擇型 (Page2)", 3: "簡化型 (Page1/Page3)"}
        button_status = "啟用" if layout_info.get('button_enabled', False) else "禁用"
        print(f"Detected layout style: {current_layout_style} - {layout_names.get(current_layout_style, 'Unknown')}")
        print(f"Layout detection details: Button found={layout_info.get('found', False)}, Button status={button_status}")
        if layout_info.get('debug_info'):
            print(f"Layout detection debug: {layout_info.get('debug_info')}")

    # 檢查下一步按鈕是否啟用
    is_button_enabled = await nodriver_ticketplus_check_next_button(tab)

    if show_debug_message:
        print(f"Next button status: {'Enabled' if is_button_enabled else 'Disabled'}")

    # 檢查是否需要選票
    is_price_assign_by_bot = False

    # 獲取關鍵字設定（修正讀取路徑）
    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "").strip()
    has_keyword = len(area_keyword) > 0

    if show_debug_message:
        print(f"Configured keyword: '{area_keyword}'")
        print(f"Has keyword configured: {has_keyword}")

    # 如果按鈕禁用或有關鍵字設定，才需要選票
    need_select_ticket = not is_button_enabled or has_keyword

    if need_select_ticket:
        if show_debug_message:
            print(f"Need ticket selection: Button disabled={not is_button_enabled}, Has keyword={has_keyword}")

        # 使用統一選擇器處理所有頁面類型（不依賴 layout_style）
        if show_debug_message:
            print(f"Using unified selector - keyword: {area_keyword}")

        is_price_assign_by_bot = await nodriver_ticketplus_unified_select(tab, config_dict, area_keyword)
        is_need_refresh = not is_price_assign_by_bot  # 如果選擇失敗則需要刷新

    # 如果按鈕已啟用且無需選票，視為可以直接提交
    elif not need_select_ticket and is_button_enabled:
        is_price_assign_by_bot = True
        if show_debug_message:
            print("Button enabled, no ticket selection needed, proceeding to submission")

    # 如果票種選擇成功，處理後續步驟
    if is_price_assign_by_bot:
        # 檢查暫停狀態
        if await check_and_handle_pause(config_dict):
            return ticketplus_dict

        if show_debug_message:
            print("Ticket selection successful, processing discount code and submit")

        # 處理優惠碼
        is_answer_sent, ticketplus_dict["fail_list"], is_question_popup = await nodriver_ticketplus_order_exclusive_code(tab, config_dict, ticketplus_dict["fail_list"])

        # 提交表單（包含暫停檢查）
        if await sleep_with_pause_check(tab, 0.3, config_dict):
            if show_debug_message:
                print("Paused before form submission")
            return ticketplus_dict
        await nodriver_ticketplus_ticket_agree(tab, config_dict)

        # 使用統一的下一步按鈕點擊邏輯
        is_form_submitted = await nodriver_ticketplus_click_next_button_unified(tab, config_dict)

        if is_form_submitted:
            await tab.sleep(5.0)
            ticketplus_dict["is_ticket_assigned"] = True

            # 檢查是否進入排隊狀態
            is_in_queue = await nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False)
            if is_in_queue:
                if show_debug_message:
                    print("Entered queue monitoring (check every 5 seconds, display only on status change)")

                # 進入排隊監控循環，每5秒檢查一次，無時間上限
                last_url = ""

                while True:
                    # 檢查是否有暫停檔案
                    if os.path.exists(CONST_MAXBOT_INT28_FILE):
                        if show_debug_message:
                            print("Pause command detected, stopping queue monitoring")
                        break

                    # 檢查暫停狀態
                    if await check_and_handle_pause(config_dict):
                        if show_debug_message:
                            print("Paused during queue waiting")
                        break

                    try:
                        current_url = tab.url

                        # 檢查是否進入確認頁面，如果是則自動暫停
                        if '/confirm/' in current_url.lower() or '/confirmseat/' in current_url.lower():
                            if show_debug_message:
                                print("Detected entry to confirmation page, automatically pausing program")
                            # 寫入暫停檔案
                            try:
                                with open(CONST_MAXBOT_INT28_FILE, 'w') as pause_file:
                                    pause_file.write("auto_paused_at_confirm_page")
                            except Exception:
                                pass
                            break

                        # 僅在 URL 變化時顯示狀態（移除重複的排隊檢查訊息）
                        if show_debug_message and current_url != last_url:
                            print(f"Page status update - URL: {current_url}")
                            last_url = current_url

                        # 檢查是否已經跳出排隊狀態（不顯示重複的偵測訊息）
                        is_still_in_queue = await nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False)

                        if not is_still_in_queue:
                            # 檢查是否進入確認頁面
                            if '/confirm/' in current_url.lower() or '/confirmseat/' in current_url.lower():
                                if show_debug_message:
                                    print("Queue ended, entered confirmation page")
                                # 寫入暫停檔案
                                try:
                                    with open(CONST_MAXBOT_INT28_FILE, 'w') as pause_file:
                                        pause_file.write("auto_paused_at_confirm_page")
                                except Exception:
                                    pass
                                break
                            else:
                                if show_debug_message:
                                    print("⏩ 排隊結束，繼續處理頁面")
                                break

                        # 每次檢查完成後等待5秒再進入下一輪（確保真正的5秒間隔）
                        await tab.sleep(5.0)

                    except Exception as exc:
                        if show_debug_message:
                            print(f"排隊監控錯誤: {exc}")
                        break

                # 排隊監控已結束（通過其他條件退出）

        if show_debug_message:
            print(f"Form submission: {'Success' if is_form_submitted else 'Failed'}")
    else:
        if show_debug_message:
            print("Ticket selection failed, cannot continue")

    if show_debug_message:
        print("=== TicketPlus Simplified Booking Ended ===")

    return ticketplus_dict

async def nodriver_ticketplus_check_next_button(tab):
    """檢查下一步按鈕是否啟用"""
    try:
        result = await tab.evaluate('''
            (function() {
                // 使用多種選擇器找下一步按鈕
                const selectors = [
                    "div.order-footer button.nextBtn",
                    "button.nextBtn",
                    "button[class*='next']",
                    ".order-footer .nextBtn"
                ];

                for (let selector of selectors) {
                    const btn = document.querySelector(selector);
                    if (btn) {
                        return {
                            found: true,
                            enabled: !btn.disabled && !btn.classList.contains('disabledBtn')
                        };
                    }
                }

                return { found: false, enabled: false };
            })();
        ''')

        result = util.parse_nodriver_result(result)
        return result.get('enabled', False) if isinstance(result, dict) else False

    except Exception as exc:
        return False




async def nodriver_ticketplus_order_exclusive_code(tab, config_dict, fail_list):
    """處理活動專屬代碼 - 直接跳過處理"""
    show_debug_message = config_dict["advanced"]["verbose"]

    # 檢查暫停狀態
    if await check_and_handle_pause(config_dict):
        return False, fail_list, False

    if show_debug_message:
        print("Skipping discount code processing")

    # 直接返回預設值：未送出答案，原有失敗清單，無彈窗問題
    is_answer_sent = False
    is_question_popup = False

    return is_answer_sent, fail_list, is_question_popup

async def nodriver_ticketplus_main(tab, url, config_dict, ocr, Captcha_Browser):
    global ticketplus_dict
    if not 'ticketplus_dict' in globals():
        ticketplus_dict = {}
        ticketplus_dict["fail_list"]=[]
        ticketplus_dict["is_popup_confirm"] = False
        ticketplus_dict["is_ticket_assigned"] = False
        ticketplus_dict["start_time"] = None
        ticketplus_dict["done_time"] = None
        ticketplus_dict["elapsed_time"] = None

    home_url = 'https://ticketplus.com.tw/'
    is_user_signin = False
    # https://ticketplus.com.tw/
    if home_url == url.lower():
        if config_dict["ocr_captcha"]["enable"]:
            domain_name = url.split('/')[2]
            if not Captcha_Browser is None:
                Captcha_Browser.set_domain(domain_name)

        is_user_signin = await nodriver_ticketplus_account_auto_fill(tab, config_dict)

    if is_user_signin:
        if url != config_dict["homepage"]:
            try:
                await tab.get(config_dict["homepage"])
            except Exception as e:
                pass

    # https://ticketplus.com.tw/activity/XXX
    if '/activity/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True

        if is_event_page:
            is_button_pressed = await nodriver_ticketplus_accept_realname_card(tab)
            if config_dict["advanced"].get("verbose", False):
                print("Realname Card:", is_button_pressed)

            is_button_pressed = await nodriver_ticketplus_accept_other_activity(tab)
            if config_dict["advanced"].get("verbose", False):
                print("Other Activity:", is_button_pressed)

            if config_dict["date_auto_select"]["enable"]:
                await nodriver_ticketplus_date_auto_select(tab, config_dict)

    # https://ticketplus.com.tw/order/XXX/OOO
    if '/order/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            ticketplus_dict["start_time"] = time.time()

            is_button_pressed = await nodriver_ticketplus_accept_realname_card(tab)
            is_order_fail_handled = await nodriver_ticketplus_accept_order_fail(tab)

            is_reloading = False

            is_reload_at_webdriver = False
            if not config_dict["browser"] in CONST_CHROME_FAMILY:
                is_reload_at_webdriver = True
            else:
                if not config_dict["advanced"]["chrome_extension"]:
                    is_reload_at_webdriver = True
            if is_reload_at_webdriver:
                is_reloading = await nodriver_ticketplus_order_auto_reload_coming_soon(tab, config_dict)

            if not is_reloading:
                ticketplus_dict = await nodriver_ticketplus_order(tab, config_dict, ocr, Captcha_Browser, ticketplus_dict)

    else:
        ticketplus_dict["fail_list"]=[]
        ticketplus_dict["is_ticket_assigned"] = False
        ticketplus_dict["start_time"] = None

    # https://ticketplus.com.tw/confirm/xx/oo
    # https://ticketplus.com.tw/confirmseat/xx/oo
    if '/confirm/' in url.lower() or '/confirmseat/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            ticketplus_dict["is_ticket_assigned"] = True

            if ticketplus_dict["start_time"]:
                ticketplus_dict["done_time"] = time.time()
                ticketplus_dict["elapsed_time"] = ticketplus_dict["done_time"] - ticketplus_dict["start_time"]
                if config_dict["advanced"].get("verbose", False):
                    print(f"NoDriver TicketPlus booking time: {ticketplus_dict['elapsed_time']:.3f} seconds")

            if config_dict["advanced"].get("verbose", False):
                print("Entered confirmation page, booking successful")

            if not ticketplus_dict["is_popup_confirm"]:
                ticketplus_dict["is_popup_confirm"] = True
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)

                try:
                    await nodriver_ticketplus_confirm(tab, config_dict)
                    if config_dict["advanced"].get("verbose", False):
                        print("Confirmation page processing completed")
                except Exception as exc:
                    if config_dict["advanced"].get("verbose", False):
                        print(f"Confirmation page processing error: {exc}")

            ticketplus_dict["purchase_completed"] = True
        else:
            ticketplus_dict["is_popup_confirm"] = False
    else:
        ticketplus_dict["is_popup_confirm"] = False

async def nodriver_ibon_login(tab, config_dict, driver):
    """
    專門的 ibon 登入函數，整合 cookie 處理、頁面重新載入和登入狀態驗證
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    if show_debug_message:
        print("=== ibon Auto-Login Started ===")

    # 檢查是否有 ibon cookie 設定
    ibonqware = config_dict["advanced"]["ibonqware"]
    if len(ibonqware) <= 1:
        if show_debug_message:
            print("No ibon cookie configured, skipping auto-login")
        return {'success': False, 'reason': 'no_cookie_configured'}

    if show_debug_message:
        print(f"Setting ibon cookie (NoDriver) with length: {len(ibonqware)}")
        print(f"Cookie contains mem_id: {'mem_id=' in ibonqware}")
        print(f"Cookie contains mem_email: {'mem_email=' in ibonqware}")
        print(f"Cookie contains huiwanTK: {'huiwanTK=' in ibonqware}")
        print(f"Cookie contains ibonqwareverify: {'ibonqwareverify=' in ibonqware}")

    try:
        from nodriver import cdp

        # 設定 ibon cookie
        cookies = await driver.cookies.get_all()
        is_cookie_exist = False
        for cookie in cookies:
            if cookie.name == 'ibonqware':
                cookie.value = ibonqware
                is_cookie_exist = True
                if show_debug_message:
                    print("Updated existing ibon cookie")
                break

        if not is_cookie_exist:
            new_cookie = cdp.network.CookieParam(
                "ibonqware", ibonqware,
                domain=".ibon.com.tw",
                path="/",
                http_only=True,
                secure=True
            )
            cookies.append(new_cookie)
            if show_debug_message:
                print("Added new ibon cookie")

        await driver.cookies.set_all(cookies)

        if show_debug_message:
            print("ibon cookie set successfully (NoDriver)")

        # 驗證 cookie 是否設定成功
        updated_cookies = await driver.cookies.get_all()
        ibon_cookies = [c for c in updated_cookies if c.name == 'ibonqware']
        if not ibon_cookies:
            if show_debug_message:
                print("Warning: ibon cookie not found after setting")
            return {'success': False, 'reason': 'cookie_not_set'}

        if show_debug_message:
            print(f"Verified: ibon cookie exists with value length: {len(ibon_cookies[0].value)}")
            print(f"Cookie domain: {ibon_cookies[0].domain}")

        # 重新載入頁面以應用 cookie（關鍵步驟！）
        if show_debug_message:
            print("Reloading page to apply ibon cookie...")
        await tab.reload()
        await tab.sleep(3.0)  # 等待頁面完全載入

        if show_debug_message:
            print("Page reloaded, ibon cookie should now be active")

        # 檢查登入狀態
        login_status = await check_ibon_login_status(tab, config_dict)

        if show_debug_message:
            print(f"Post-reload login status: {login_status.get('isLoggedIn', False)}")

        if login_status.get('isLoggedIn', False):
            if show_debug_message:
                print("[SUCCESS] ibon auto-login successful")
            return {'success': True, 'login_status': login_status}
        else:
            if show_debug_message:
                print("[ERROR] ibon auto-login may have failed - manual login may be required")
                print("[TIP] Try refreshing the page manually or check if cookie has expired")
            return {'success': False, 'reason': 'login_verification_failed', 'login_status': login_status}

    except Exception as cookie_error:
        print(f"Failed to set ibon cookie (NoDriver): {cookie_error}")
        if show_debug_message:
            import traceback
            traceback.print_exc()
        return {'success': False, 'reason': 'exception', 'error': str(cookie_error)}

async def nodriver_ibon_date_selection(tab, config_dict):
    """
    NoDriver ibon 日期選擇實作
    基於 Chrome ibon 的日期選擇邏輯，使用 Shadow DOM 穿透技術
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    if show_debug_message:
        print("NoDriver ibon date selection started")
        print("date_keyword:", date_keyword)
        print("auto_select_mode:", auto_select_mode)

    is_date_selected = False

    try:
        # 等待頁面載入
        await tab.sleep(1.0)

        # 使用多重策略搜尋日期選項
        date_options = await search_ibon_date_options_with_cdp(tab, show_debug_message)

        if show_debug_message:
            print(f"Found {len(date_options)} date options")
            for i, option in enumerate(date_options):
                print(f"  Option {i}: {option}")

        # 過濾可用的日期選項（排除 disabled 的按鈕）
        available_options = []
        for option in date_options:
            if isinstance(option, dict):
                # 檢查是否有 disabled 屬性
                element_html = option.get('element', '')
                if 'disabled' not in element_html.lower():
                    available_options.append(option)
                elif show_debug_message:
                    print(f"  Skipping disabled option: {option.get('text', 'unknown')}")

        if show_debug_message:
            print(f"Available (enabled) options: {len(available_options)}")

        # 應用關鍵字過濾
        matched_options = []
        if len(date_keyword) > 0 and available_options:
            for option in available_options:
                option_text = option.get('text', '').lower()
                date_context = option.get('date_context', '').lower()
                search_text = f"{option_text} {date_context}"

                # 簡單關鍵字匹配
                if date_keyword.lower() in search_text:
                    matched_options.append(option)
                    if show_debug_message:
                        print(f"  Keyword match: '{option.get('text', 'unknown')}'")
        else:
            matched_options = available_options

        # 選擇目標日期選項
        target_option = None
        if matched_options:
            if auto_select_mode == "random":
                import random
                target_option = random.choice(matched_options)
            elif auto_select_mode == "from bottom to top":
                target_option = matched_options[-1]
            else:  # from top to bottom (default)
                target_option = matched_options[0]

            if show_debug_message:
                option_text = target_option.get('text', 'unknown') if isinstance(target_option, dict) else 'non-dict'
                print(f"Selected date option: '{option_text}'")

        # 點擊選中的日期選項
        if target_option and isinstance(target_option, dict):
            click_result = await click_ibon_date_option(tab, target_option, show_debug_message)
            if click_result and click_result.get('success'):
                is_date_selected = True
                if show_debug_message:
                    print("Date selection successful")
                # 等待頁面更新
                await tab.sleep(1.5)
            else:
                if show_debug_message:
                    print(f"Date selection failed: {click_result}")
        else:
            if show_debug_message:
                print("No suitable date option found")

    except Exception as e:
        if show_debug_message:
            print(f"Date selection error: {e}")
            import traceback
            traceback.print_exc()

    if show_debug_message:
        print(f"Date selection result: {is_date_selected}")

    return is_date_selected

async def search_ibon_date_options_with_cdp(tab, show_debug_message):
    """
    使用 CDP 搜尋 ibon 日期選項
    參考 Chrome ibon 的選擇器: div.single-content > div > div.row > div > div.tr
    """
    date_options = []

    try:
        from nodriver import cdp

        if show_debug_message:
            print("Searching for ibon date options...")

        # 使用 DOMSnapshot 獲取平坦化的頁面結構
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_paint_order=True,
            include_dom_rects=True,
            include_blended_background_colors=True
        ))

        if documents and len(documents) > 0:
            document = documents[0]
            node_names = document.layout.node_names if hasattr(document.layout, 'node_names') else []
            node_values = document.layout.node_values if hasattr(document.layout, 'node_values') else []

            # 搜尋相關的日期選項容器
            target_selectors = [
                'div.tr',  # 主要的日期行選擇器
                'div.single-content',
                'button.btn',
                'button.btn-pink',
                'button.btn-buy'
            ]

            found_nodes = []
            for i, name_idx in enumerate(node_names):
                if name_idx < len(strings):
                    node_name = strings[name_idx].lower()

                    # 檢查是否為目標節點
                    for selector in target_selectors:
                        if selector.replace('.', ' ').replace('div', '').replace('button', '').strip() in node_name:
                            found_nodes.append((i, node_name))
                            break

            if show_debug_message:
                print(f"Found {len(found_nodes)} potential date nodes")

            # 提取文字內容和屬性
            for node_idx, node_name in found_nodes:
                try:
                    # 嘗試獲取節點內容
                    if hasattr(document.layout, 'text_values') and node_idx < len(document.layout.text_values):
                        text_idx = document.layout.text_values[node_idx]
                        if text_idx >= 0 and text_idx < len(strings):
                            text_content = strings[text_idx]

                            # 檢查是否包含日期相關信息
                            if any(keyword in text_content.lower() for keyword in
                                  ['立即購', '線上購票', '購票', '票券', '日期', '時間', '場次']):

                                date_option = {
                                    'text': text_content,
                                    'node_name': node_name,
                                    'node_index': node_idx,
                                    'method': 'cdp_dom_snapshot',
                                    'date_context': '',
                                    'element': f'<{node_name}>{text_content}</{node_name}>'
                                }

                                date_options.append(date_option)

                                if show_debug_message:
                                    print(f"  Found date option: {text_content[:50]}")

                except Exception as node_error:
                    if show_debug_message:
                        print(f"Error processing node {node_idx}: {node_error}")
                    continue

    except Exception as e:
        if show_debug_message:
            print(f"CDP date search error: {e}")

    return date_options

async def click_ibon_date_option(tab, date_option, show_debug_message):
    """
    點擊 ibon 日期選項
    """
    try:
        if show_debug_message:
            print(f"Attempting to click date option: {date_option.get('text', 'unknown')}")

        # 根據不同方法點擊
        method = date_option.get('method', 'unknown')

        if method == 'cdp_dom_snapshot':
            # 嘗試使用 JavaScript 點擊
            text_content = date_option.get('text', '')

            # 使用多重策略嘗試點擊
            click_scripts = [
                f"document.evaluate(\"//button[contains(text(), '{text_content}')]\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()",
                f"document.evaluate(\"//div[contains(@class, 'tr')]//button[contains(text(), '{text_content}')]\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()",
                f"[...document.querySelectorAll('button')].find(btn => btn.textContent.includes('{text_content}'))?.click()",
                f"[...document.querySelectorAll('div.tr button')].find(btn => btn.textContent.includes('{text_content}'))?.click()"
            ]

            for script in click_scripts:
                try:
                    result = await tab.evaluate(script, return_by_value=True)
                    if show_debug_message:
                        print(f"JavaScript click result: {result}")

                    # 等待一下看是否有反應
                    await tab.sleep(0.5)

                    # 檢查頁面是否有變化（簡單檢查）
                    current_url = await tab.evaluate('window.location.href', return_by_value=True)
                    if show_debug_message:
                        print(f"Current URL after click attempt: {current_url}")

                    return {'success': True, 'method': 'javascript', 'script': script}

                except Exception as script_error:
                    if show_debug_message:
                        print(f"JavaScript click failed: {script_error}")
                    continue

        return {'success': False, 'error': 'No suitable click method found'}

    except Exception as e:
        if show_debug_message:
            print(f"Click date option error: {e}")
        return {'success': False, 'error': str(e)}

async def nodriver_ibon_date_mode_select(buttons, auto_select_mode, show_debug_message=False):
    """
    NoDriver ibon 日期模式自動選擇
    當沒有日期關鍵字時，根據模式從 enabled 按鈕中選擇

    Args:
        buttons: 按鈕列表
        auto_select_mode: 選擇模式 (random, center, from top to bottom, from bottom to top)
        show_debug_message: 是否顯示除錯訊息

    Returns:
        選中的按鈕 dict，如果沒有可用按鈕則返回 None
    """
    # 過濾出 enabled 的按鈕
    enabled_buttons = []
    for button in buttons:
        if isinstance(button, dict):
            element_html = button.get('element', '')
            if 'disabled' not in element_html.lower():
                enabled_buttons.append(button)
            elif show_debug_message:
                print(f"  [MODE SELECT] Filtering out disabled button: {button.get('text', 'unknown')}")

    if show_debug_message:
        print(f"[MODE SELECT] Found {len(enabled_buttons)} enabled buttons out of {len(buttons)} total")

    if not enabled_buttons:
        if show_debug_message:
            print("[MODE SELECT] No enabled buttons available")
        return None

    # 根據模式選擇按鈕
    target_button = None
    if auto_select_mode == "random":
        import random
        target_button = random.choice(enabled_buttons)
    elif auto_select_mode == "from bottom to top":
        target_button = enabled_buttons[-1]
    elif auto_select_mode == "center":
        target_button = enabled_buttons[len(enabled_buttons) // 2]
    else:  # from top to bottom (default)
        target_button = enabled_buttons[0]

    if show_debug_message and target_button:
        button_text = target_button.get('text', 'unknown') if isinstance(target_button, dict) else 'non-dict'
        button_index = enabled_buttons.index(target_button) if target_button in enabled_buttons else -1
        print(f"[MODE SELECT] Selected button {button_index}/{len(enabled_buttons)} by mode '{auto_select_mode}': '{button_text}'")

    return target_button

async def nodriver_ibon_date_auto_select(tab, config_dict):
    """
    NoDriver ibon 日期自動選擇實作 - 重構 Shadow DOM 平坦化版
    基於 nodriver API 指南，使用 DOMSnapshot 平坦化策略穿透 Shadow DOM
    支援單行與雙行日期格式的智慧識別與選擇
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

    # 獲取當前 URL
    try:
        current_url = await tab.evaluate('window.location.href')
    except:
        current_url = "unknown_url"

    if show_debug_message:
        print(f"NoDriver ibon_date_auto_select started (DOMSnapshot Flattened mode)")
        print("date_keyword:", date_keyword)
        print("auto_select_mode:", auto_select_mode)
        print("URL:", current_url)

    is_date_assigned = False

    # 初始化重試計數器（如果尚未定義）
    if '_ibon_date_select_attempts' not in globals():
        global _ibon_date_select_attempts
        _ibon_date_select_attempts = {}

    try:
        # 進入活動頁面後隨機等待讓 Angular 應用完全載入（與 Chrome 版本保持一致）
        import random
        wait_time = random.uniform(0.8, 1.2)
        if show_debug_message:
            print(f"Waiting {wait_time:.2f} seconds for Angular app to fully load...")
        await tab.sleep(wait_time)

        # 額外等待確保 DOM 完全載入（特別是 Shadow DOM 元素）
        await tab.sleep(1.5)

        # 使用 NoDriver CDP DOMSnapshot 穿透 Shadow DOM 搜尋購票按鈕
        if show_debug_message:
            print("Searching for purchase buttons...")

        # 統一使用只搜尋不點擊的方法（不論是否有關鍵字），避免過早點擊
        if show_debug_message:
            if date_keyword:
                print("[STRATEGY] Date keyword detected, using search-only method (no auto-click)")
            else:
                print("[STRATEGY] No date keyword, search all buttons and select by mode")
        purchase_buttons = await search_closed_shadow_dom_buttons(tab, show_debug_message)

        if show_debug_message:
            print(f"Found {len(purchase_buttons)} purchase buttons")
            # Button details already printed in search_closed_shadow_dom_buttons

        # 日期提取已在 search_closed_shadow_dom_buttons 中完成
        # Date extraction details already printed in search_closed_shadow_dom_buttons

        # 增強的關鍵字匹配 - 支援日期上下文和 AND/OR 邏輯
        matched_buttons = []

        if len(date_keyword) > 0:
            try:
                # 支援 JSON 陣列格式的 AND/OR 邏輯
                import json
                keywords_logic = json.loads("[" + date_keyword + "]")
                if show_debug_message:
                    print(f"Using AND/OR logic with keywords: {keywords_logic}")
            except:
                # 回退到簡單逗號分隔
                keywords_logic = [date_keyword.split(',')]
                if show_debug_message:
                    print(f"Using simple comma-separated keywords: {keywords_logic}")

            # 日期標準化函數（支援完整年份格式）
            def normalize_date_keyword(keyword):
                """
                標準化日期關鍵字為 MM/DD 格式
                支援：YYYY/MM/DD, YY/MM/DD, MM/DD, M/D
                範例：
                  - 2025/11/07 → 11/07
                  - 25/11/07 → 11/07
                  - 11/7 → 11/07
                  - 11/07 → 11/07
                """
                import re
                # 匹配日期格式：(年份)/(月)/(日)
                date_pattern = r'(\d{2,4})/(\d{1,2})/(\d{1,2})'
                match = re.search(date_pattern, keyword)
                if match:
                    parts = match.groups()
                    if len(parts[0]) == 4 or len(parts[0]) == 2:
                        # 有年份，取月/日
                        month, day = parts[1], parts[2]
                    else:
                        # 無年份（不可能，因 pattern 要求至少 2 位數）
                        month, day = parts[0], parts[1]
                    # 補零到兩位數
                    return f"{int(month):02d}/{int(day):02d}"
                return keyword  # 非日期格式，保持不變

            if show_debug_message:
                print(f"[MATCHING] Starting keyword matching loop with {len(purchase_buttons)} buttons")

            for i in range(len(purchase_buttons)):
                button = purchase_buttons[i]
                try:
                    # 檢查 button 是否為字典類型
                    if not isinstance(button, dict):
                        if show_debug_message:
                            print(f"Skipping non-dict button: {type(button)} - {button}")
                        continue

                    # 檢查按鈕是否為 disabled 狀態
                    element_html = button.get('element', '')
                    if 'disabled' in element_html.lower():
                        if show_debug_message:
                            print(f"Skipping disabled button: {button.get('text', 'unknown')}")
                        continue

                    button_text = button.get('text', '')
                    date_context = button.get('date_context', '')
                    # 標準化日期上下文（補零並統一格式）
                    date_context_normalized = normalize_date_keyword(date_context) if date_context else ''
                    search_text = f"{button_text} {date_context_normalized}".lower()
                except Exception as e:
                    if show_debug_message:
                        print(f"Error processing button data: {e}, button: {button}")
                    continue

                # 檢查 AND/OR 邏輯（支援完整年份格式）
                is_match = False
                for keyword_group in keywords_logic:
                    if isinstance(keyword_group, list):
                        # AND 邏輯 - 標準化每個關鍵字後檢查
                        normalized_keywords = [normalize_date_keyword(kw.strip()) for kw in keyword_group if kw.strip()]
                        group_match = all(nkw.lower() in search_text for nkw in normalized_keywords)
                    else:
                        # 單一關鍵字 - 標準化後檢查
                        normalized_keyword = normalize_date_keyword(keyword_group.strip())
                        group_match = normalized_keyword.lower() in search_text

                    if group_match:
                        is_match = True
                        break

                if is_match:
                    matched_buttons.append(button)
                    if show_debug_message:
                        print(f"  Keyword match: '{button_text}' (Date: {date_context})")

        if show_debug_message:
            print(f"Found {len(matched_buttons)} buttons matching keywords")

        # 選擇要點擊的按鈕
        target_button = None

        if len(date_keyword) > 0 and len(matched_buttons) > 0:
            # 情況A：有關鍵字且有匹配，選擇第一個符合的按鈕
            target_button = matched_buttons[0]
            if show_debug_message:
                button_text = target_button.get('text', 'unknown') if isinstance(target_button, dict) else 'non-dict'
                print(f"[KEYWORD SELECT] Selected first matched button: '{button_text}'")
        elif len(purchase_buttons) > 0:
            # 情況A（關鍵字無匹配）或情況B（沒有關鍵字）：啟動模式自動選擇函式
            if show_debug_message:
                if len(date_keyword) > 0:
                    print("[KEYWORD NO MATCH] No buttons matched keyword, fallback to mode auto-select")
                else:
                    print("[NO KEYWORD] Using mode auto-select function")
            target_button = await nodriver_ibon_date_mode_select(purchase_buttons, auto_select_mode, show_debug_message)

        # 點擊選中的按鈕
        if target_button:
            try:
                # 檢查是否為立即點擊成功的按鈕 - 加強型別檢查
                if isinstance(target_button, dict) and target_button.get('method') == 'immediate_click':
                    # 立即點擊已經完成，檢查導航
                    await tab.sleep(1.0)

                    # 檢查頁面是否已導航
                    try:
                        final_url = await tab.evaluate('window.location.href')
                        if final_url != current_url:
                            is_date_assigned = True
                            if show_debug_message:
                                print(f"[SUCCESS] Page navigation confirmed: {current_url} -> {final_url}")
                        else:
                            if show_debug_message:
                                print(f"[WARNING] No page navigation detected after immediate click")
                    except:
                        pass
                else:
                    # 傳統點擊方法（回退） - 加強型別檢查
                    if isinstance(target_button, dict):
                        button_method = target_button.get('method', 'unknown')
                        if button_method == 'cdp_dom_pierce':
                            click_result = await click_button_via_cdp(tab, target_button, show_debug_message)
                        elif button_method == 'javascript_shadow_enhanced':
                            click_result = await click_button_via_enhanced_javascript(tab, target_button, show_debug_message)
                        else:
                            click_result = await click_button_via_javascript(tab, target_button, show_debug_message)
                    else:
                        # 如果 target_button 不是字典，記錄錯誤並跳過
                        if show_debug_message:
                            print(f"[ERROR] target_button is not dict: {type(target_button)} - {target_button}")
                        click_result = None

                    if click_result and isinstance(click_result, dict) and click_result.get('success'):
                        # 檢查頁面導航
                        await tab.sleep(1.0)
                        try:
                            final_url = await tab.evaluate('window.location.href')
                            if final_url != current_url:
                                is_date_assigned = True
                                if show_debug_message:
                                    print(f"[SUCCESS] Page navigation confirmed: {current_url} -> {final_url}")
                            else:
                                if show_debug_message:
                                    print(f"[WARNING] Click succeeded but no navigation detected")
                        except:
                            # 假設成功（如果無法檢查 URL）
                            is_date_assigned = True

                        if show_debug_message:
                            # 安全處理 click_result 獲取按鈕文字
                            button_text = ""
                            if isinstance(click_result, dict):
                                button_text = click_result.get('buttonText', '')
                            print(f"Successfully clicked purchase button: {button_text}")
                    else:
                        if show_debug_message:
                            # 安全處理 click_result，避免 'list' object has no attribute 'get' 錯誤
                            if isinstance(click_result, dict):
                                error_msg = click_result.get('error', 'Unknown error')
                            else:
                                error_msg = f"Unexpected result type: {type(click_result)}"
                            print(f"Failed to click button: {error_msg}")

            except Exception as click_error:
                if show_debug_message:
                    print(f"Failed to click button: {click_error}")

        # 重試機制：如果點擊失敗且未達重試上限
        if not is_date_assigned:
            retry_count = _ibon_date_select_attempts.get(current_url, 0)
            max_retries = 3

            if retry_count < max_retries:
                _ibon_date_select_attempts[current_url] = retry_count + 1
                if show_debug_message:
                    print(f"[ERROR] Click failed, retrying... ({retry_count + 1}/{max_retries})")

                # 短暫等待後重試
                await tab.sleep(1.0)
                return await nodriver_ibon_date_auto_select(tab, config_dict)
            else:
                if show_debug_message:
                    print(f"[ERROR] Maximum retries ({max_retries}) reached for {current_url}")

        # 成功時清理重試記錄
        if is_date_assigned:
            if current_url in _ibon_date_select_attempts:
                del _ibon_date_select_attempts[current_url]
                if show_debug_message:
                    print(f"[SUCCESS] Cleared retry attempts for {current_url} after successful navigation")

    except Exception as exc:
        if show_debug_message:
            print(f"NoDriver ibon_date_auto_select error: {exc}")
        pass

    if show_debug_message:
        print(f"NoDriver ibon_date_auto_select result: {is_date_assigned}")

    return is_date_assigned

async def search_purchase_buttons_with_cdp(tab, show_debug_message):
    """
    多層次購票按鈕搜尋策略 - 基於 nodriver API guide（已優化）
    搜尋順序：
    1. Enhanced Closed Shadow DOM 穿透（優先，專門針對 ibon 的 closed shadow DOM）
    2. DOMSnapshot 平坦化策略（快速回退）
    3. 傳統 CDP DOM 方法（回退）
    4. 純 JavaScript 方法（最終回退）
    """
    try:
        from nodriver import cdp

        if show_debug_message:
            print("Using enhanced multi-strategy search...")

        # DEBUGGING: 除錯工具暫時禁用以修復數據格式問題
        # if show_debug_message:
        #     print("\n[DEBUG] Running diagnostic tools before search...")
        #     # 1. 分析 Shadow DOM 結構
        #     await debug_shadow_dom_structure(tab, show_debug_message)
        #     # 2. 比較搜尋方法
        #     await compare_search_methods(tab, "線上購票", show_debug_message)
        #     print("\n[DEBUG] Diagnostic complete, proceeding with normal search...")

        # 方法 0：NoDriver 原生搜尋並點擊（最優先，內建 Shadow DOM 支援）
        if show_debug_message:
            print("Trying NoDriver native search and click first...")

        native_result = await search_and_click_with_nodriver_native(tab, show_debug_message)
        if native_result and native_result.get('success'):
            # 檢查是否點擊了 disabled 按鈕
            element_html = native_result.get('element', '')
            is_disabled_click = 'disabled=' in element_html or 'disabled"' in element_html

            if not is_disabled_click:
                if show_debug_message:
                    print(f"[SUCCESS] NoDriver native search and click succeeded via {native_result.get('method')}")
                # 返回按鈕資料表示成功
                return [{
                    'text': native_result.get('buttonText', '線上購票'),
                    'method': 'nodriver_native',
                    'success': True,
                    'click_method': native_result.get('method'),
                    'element': native_result.get('element', '')
                }]
            else:
                if show_debug_message:
                    print(f"[ERROR] NoDriver native found disabled button, trying other methods...")
                # 不返回結果，繼續嘗試其他方法

        # 方法 1：立即搜尋並點擊（備用方法，避免 NodeId 失效）
        if show_debug_message:
            print("Native method failed, trying immediate search and click...")

        immediate_result = await search_and_click_immediately(tab, show_debug_message)
        if immediate_result and immediate_result.get('success'):
            if show_debug_message:
                print(f"[SUCCESS] Immediate search and click succeeded via {immediate_result.get('method')}")
            # 返回假的按鈕資料表示成功
            return [{
                'text': '線上購票',
                'method': 'immediate_click',
                'success': True,
                'click_method': immediate_result.get('method'),
                'attempts': immediate_result.get('attempts', [])
            }]

        # 方法 2：Enhanced Closed Shadow DOM 穿透（回退方法）
        if show_debug_message:
            print("Immediate click failed, trying enhanced closed Shadow DOM search...")

        closed_shadow_buttons = await search_closed_shadow_dom_buttons(tab, show_debug_message)
        if closed_shadow_buttons:
            if show_debug_message:
                print(f"Enhanced Shadow DOM search found {len(closed_shadow_buttons)} buttons")
            return closed_shadow_buttons

        # 方法 3：DOMSnapshot 平坦化（快速回退）- 自動平坦化 Shadow DOM
        try:
            if show_debug_message:
                print("Attempting DOMSnapshot capture_snapshot...")

            # 使用 DOMSnapshot 獲取平坦化的頁面結構
            documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
                computed_styles=[],  # 必要參數
                include_paint_order=True,
                include_dom_rects=True,
                include_blended_background_colors=True
            ))

            if show_debug_message:
                print(f"DOMSnapshot captured {len(documents)} documents with {len(strings)} string entries")

                # DOM 字符串表已載入（省略詳細輸出以簡化 log）

            found_buttons = []
            for doc_idx, document in enumerate(documents):
                # 安全地處理 document.nodes
                try:
                    if not hasattr(document, 'nodes'):
                        if show_debug_message:
                            print(f"Document {doc_idx}: No nodes attribute")
                        continue

                    # 嘗試不同的方式訪問 nodes
                    nodes = None
                    if hasattr(document.nodes, '__iter__'):
                        # 如果可以迭代，轉換為列表
                        try:
                            nodes = list(document.nodes)
                        except:
                            nodes = []
                    elif hasattr(document.nodes, '__len__'):
                        # 如果有長度屬性，嘗試索引訪問
                        try:
                            nodes = [document.nodes[i] for i in range(len(document.nodes))]
                        except:
                            nodes = []
                    else:
                        # 作為最後手段，檢查是否是單個節點
                        nodes = [document.nodes] if document.nodes else []

                    if show_debug_message:
                        print(f"Processing document {doc_idx}: {len(nodes)} nodes")

                    # 遍歷節點
                    for node_idx, node in enumerate(nodes):
                        try:
                            # 檢查節點名稱
                            node_name = ""
                            if hasattr(node, 'node_name') and node.node_name is not None:
                                try:
                                    if isinstance(node.node_name, int) and 0 <= node.node_name < len(strings):
                                        node_name = strings[node.node_name]
                                    elif isinstance(node.node_name, str):
                                        node_name = node.node_name
                                except:
                                    node_name = ""

                            if node_name.lower() == 'button':
                                # 獲取節點屬性
                                attributes = {}
                                if hasattr(node, 'attributes') and node.attributes:
                                    try:
                                        for i in range(0, len(node.attributes), 2):
                                            if i + 1 < len(node.attributes):
                                                attr_idx = node.attributes[i]
                                                val_idx = node.attributes[i + 1]
                                                if (isinstance(attr_idx, int) and 0 <= attr_idx < len(strings) and
                                                    isinstance(val_idx, int) and 0 <= val_idx < len(strings)):
                                                    attr_name = strings[attr_idx]
                                                    attr_value = strings[val_idx]
                                                    attributes[attr_name] = attr_value
                                    except:
                                        pass

                                # 獲取按鈕文字
                                button_text = ""
                                if hasattr(node, 'node_value') and node.node_value is not None:
                                    try:
                                        if isinstance(node.node_value, int) and 0 <= node.node_value < len(strings):
                                            button_text = strings[node.node_value]
                                        elif isinstance(node.node_value, str):
                                            button_text = node.node_value
                                    except:
                                        pass

                                # 檢查是否為購票按鈕
                                classes = attributes.get('class', '')
                                is_purchase_button = (
                                    'btn-buy' in classes or
                                    'btn-pink' in classes or
                                    '線上購票' in button_text or
                                    '購票' in button_text or
                                    'button' in classes and ('pink' in classes or 'buy' in classes)
                                )

                                if is_purchase_button:
                                    # 檢查是否 disabled
                                    is_disabled = 'disabled' in attributes

                                    found_buttons.append({
                                        'node_index': node_idx,
                                        'document_index': doc_idx,
                                        'text': button_text.strip(),
                                        'classes': classes,
                                        'attributes': attributes,
                                        'method': 'dom_snapshot_flattened',
                                        'disabled': is_disabled
                                    })

                                    if show_debug_message:
                                        print(f"  Found button: '{button_text.strip()}' (classes: {classes})")

                        except Exception as e:
                            if show_debug_message:
                                print(f"Error processing node {node_idx}: {e}")
                            continue

                except Exception as doc_error:
                    if show_debug_message:
                        print(f"Error processing document {doc_idx}: {doc_error}")
                    continue

            if show_debug_message:
                valid_buttons = [btn for btn in found_buttons if not btn.get('disabled', False)]
                print(f"DOMSnapshot found {len(found_buttons)} total buttons, {len(valid_buttons)} valid")

            # 只有找到有效按鈕時才返回，否則繼續下一個策略
            if found_buttons:
                return found_buttons

        except Exception as snapshot_error:
            if show_debug_message:
                print(f"DOMSnapshot method failed: {snapshot_error}")
            # 繼續到方法 2

        # 方法 3：傳統 CDP DOM 方法（回退）
        if show_debug_message:
            print("Falling back to traditional CDP DOM method...")

        document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

        # 使用 JavaScript 評估以避免複雜的節點遍歷
        js_result = await tab.evaluate('''
            (function() {
                const buttons = [];

                // 搜尋主 DOM 中的按鈕
                const mainButtons = document.querySelectorAll('button');
                mainButtons.forEach((btn, idx) => {
                    const classes = btn.className || '';
                    const text = btn.textContent.trim();
                    const isPurchaseBtn =
                        classes.includes('btn-buy') ||
                        classes.includes('btn-pink') ||
                        text.includes('線上購票') ||
                        text.includes('購票');

                    if (isPurchaseBtn) {
                        buttons.push({
                            index: idx,
                            text: text,
                            classes: classes,
                            disabled: btn.disabled,
                            method: 'javascript_main_dom'
                        });
                    }
                });

                // 搜尋 open Shadow DOM
                function searchOpenShadowRoots(rootElement) {
                    const allElements = rootElement.querySelectorAll('*');
                    allElements.forEach((element) => {
                        if (element.shadowRoot) {
                            const shadowButtons = element.shadowRoot.querySelectorAll('button');
                            shadowButtons.forEach((btn, idx) => {
                                const classes = btn.className || '';
                                const text = btn.textContent.trim();
                                const isPurchaseBtn =
                                    classes.includes('btn-buy') ||
                                    classes.includes('btn-pink') ||
                                    text.includes('線上購票') ||
                                    text.includes('購票');

                                if (isPurchaseBtn) {
                                    buttons.push({
                                        index: idx,
                                        text: text,
                                        classes: classes,
                                        disabled: btn.disabled,
                                        method: 'javascript_open_shadow',
                                        host: element.tagName
                                    });
                                }
                            });

                            // 遞迴搜尋嵌套 Shadow DOM
                            searchOpenShadowRoots(element.shadowRoot);
                        }
                    });
                }

                searchOpenShadowRoots(document);

                return {
                    success: true,
                    buttons: buttons,
                    total: buttons.length
                };
            })();
        ''')

        # 處理 nodriver 的特殊回傳格式
        parsed_js_result = None
        if isinstance(js_result, list):
            # nodriver 特殊格式：[['key', {'type': 'type', 'value': value}], ...]
            parsed_js_result = {}
            for item in js_result:
                if isinstance(item, list) and len(item) == 2:
                    key = item[0]
                    value_obj = item[1]
                    if isinstance(value_obj, dict) and 'value' in value_obj:
                        parsed_js_result[key] = value_obj['value']
        elif isinstance(js_result, dict):
            parsed_js_result = js_result

        if parsed_js_result and parsed_js_result.get('success'):
            if show_debug_message:
                print(f"JavaScript fallback found {parsed_js_result.get('total', 0)} buttons")
            return parsed_js_result.get('buttons', [])

        return []

    except Exception as cdp_error:
        if show_debug_message:
            print(f"All CDP methods failed: {cdp_error}")

        # 方法 4：強化 JavaScript Shadow DOM 穿透 (新增)
        if show_debug_message:
            print("Trying enhanced JavaScript Shadow DOM penetration...")

        js_shadow_buttons = await enhanced_javascript_shadow_search(tab, show_debug_message)
        if js_shadow_buttons:
            if show_debug_message:
                print(f"Enhanced JavaScript Shadow DOM search found {len(js_shadow_buttons)} buttons")
            return js_shadow_buttons

        # 最終回退到原本的 JavaScript 方法
        return await fallback_javascript_search(tab, show_debug_message)

async def search_closed_shadow_dom_buttons(tab, show_debug_message):
    """
    使用 NoDriver CDP DOM pierce=True 穿透 closed Shadow DOM 搜尋購票按鈕
    基於 NoDriver API 指南的混合策略方法
    """
    try:
        from nodriver import cdp
        import re

        if show_debug_message:
            print("[SHADOW DOM] Starting enhanced closed Shadow DOM search...")

        # 步驟 1: 使用 DOMSnapshot 提取完整頁面結構和日期信息
        date_map_by_order = []  # 按鈕順序到日期的映射

        try:
            if show_debug_message:
                print("[DOMSNAPSHOT] Capturing page structure for date extraction...")

            # 使用 DOMSnapshot 獲取平坦化的頁面結構
            documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
                computed_styles=[],
                include_paint_order=True,
                include_dom_rects=True
            ))

            if documents and len(documents) > 0:
                document_snapshot = documents[0]

                # 提取節點信息
                node_names = []
                node_values = []
                parent_indices = []
                attributes_list = []

                if hasattr(document_snapshot, 'layout'):
                    if hasattr(document_snapshot.layout, 'node_index'):
                        node_indices = document_snapshot.layout.node_index

                        # 從 document_snapshot.nodes 獲取節點信息
                        if hasattr(document_snapshot, 'nodes'):
                            nodes = document_snapshot.nodes
                            if hasattr(nodes, 'node_name'):
                                node_names = [strings[i] if isinstance(i, int) and i < len(strings) else str(i)
                                             for i in nodes.node_name]
                            if hasattr(nodes, 'node_value'):
                                node_values = [strings[i] if isinstance(i, int) and i >= 0 and i < len(strings) else ''
                                              for i in nodes.node_value]
                            if hasattr(nodes, 'parent_index'):
                                parent_indices = list(nodes.parent_index)
                            if hasattr(nodes, 'attributes'):
                                attributes_list = nodes.attributes

                if show_debug_message:
                    print(f"[DOMSNAPSHOT] Extracted {len(node_names)} nodes, {len(strings)} strings")

                # 建立節點到日期的映射
                # 策略：找出所有包含日期格式的 #text 節點，記錄其祖先鏈中的日期
                node_has_date = {}  # node_index -> (date_string, tag_name)

                # 第一步：找出所有包含日期的文本節點
                for i, node_name in enumerate(node_names):
                    if node_name == '#text' and i < len(node_values) and node_values[i]:
                        text_content = node_values[i]
                        # 更寬鬆的日期匹配：可能包含完整年份 2025/10/02 或簡化的 10/02
                        date_match = re.search(r'(\d{4}/)?(\d{1,2}/\d{1,2})', text_content)
                        if date_match:
                            # 只取月/日部分
                            date_str = date_match.group(2)
                            # 標記這個文本節點的父節點有日期
                            if i < len(parent_indices):
                                parent_idx = parent_indices[i]
                                if parent_idx >= 0:
                                    parent_tag = node_names[parent_idx] if parent_idx < len(node_names) else 'unknown'
                                    node_has_date[parent_idx] = (date_str, parent_tag)
                                    if show_debug_message:
                                        # 顯示完整文本內容以便除錯（避免編碼錯誤中斷流程）
                                        try:
                                            print(f"[DOMSNAPSHOT] Found date '{date_str}' in #text node {i}, parent: {parent_tag} (index {parent_idx}), full text: '{text_content[:50]}'")
                                        except UnicodeEncodeError:
                                            print(f"[DOMSNAPSHOT] Found date '{date_str}' in #text node {i}, parent: {parent_tag} (index {parent_idx}), full text: <encoding error>")

                if show_debug_message:
                    print(f"[DOMSNAPSHOT] Found {len(node_has_date)} nodes with dates")

                # 第二步：建立子節點到父節點的映射（用於向下搜尋）
                children_map = {}  # parent_index -> [child_indices]
                for i, parent_idx in enumerate(parent_indices):
                    if parent_idx >= 0:
                        if parent_idx not in children_map:
                            children_map[parent_idx] = []
                        children_map[parent_idx].append(i)

                if show_debug_message:
                    print(f"[DOMSNAPSHOT] Built children map with {len(children_map)} parents")

                # 第三步：定義在按鈕的兄弟/子節點中查找日期的函數
                def find_date_near_button(button_idx):
                    """
                    在按鈕附近查找日期：
                    1. 向上找到按鈕的場次容器（向上 3-4 層）
                    2. 在該容器的所有子孫節點中搜尋包含日期的文本節點
                    3. 返回找到的第一個日期
                    """
                    # 步驟 1：向上找到場次容器（div.game-item 或類似）
                    # 減少層數避免找到包含所有場次的大容器
                    container_idx = button_idx
                    for _ in range(2):  # 向上 2 層找到場次容器（避免找到太大的容器）
                        if container_idx < len(parent_indices):
                            container_idx = parent_indices[container_idx]
                        else:
                            break

                    if container_idx < 0:
                        return None

                    # 步驟 2：在容器的所有子孫中搜尋日期（廣度優先搜尋）
                    queue = [container_idx]
                    visited = set()
                    dates_found = []

                    while queue and len(visited) < 200:  # 限制搜尋範圍避免過度搜尋
                        current = queue.pop(0)
                        if current in visited or current < 0:
                            continue
                        visited.add(current)

                        # 檢查當前節點是否有日期
                        if current in node_has_date:
                            dates_found.append((current, node_has_date[current]))

                        # 加入子節點到隊列
                        if current in children_map:
                            queue.extend(children_map[current])

                    # 返回找到的第一個日期（最接近的）
                    if dates_found:
                        if show_debug_message:
                            # dates_found 現在是 [(node_idx, (date_str, tag_name)), ...]
                            date_info = [(d[1][0], d[1][1]) for d in dates_found]  # [(date, tag), ...]
                            print(f"[DOMSNAPSHOT] Button {button_idx} in container {container_idx}: found {len(dates_found)} dates: {date_info}")

                        # 優先級策略：P 標籤 > 其他標籤，排除 SMALL 標籤（截止時間）
                        # dates_found 格式: [(node_idx, (date_str, tag_name)), ...]

                        # 第一優先：尋找 P 標籤的日期（活動時間）
                        for node_idx, (date_str, tag_name) in dates_found:
                            if tag_name.upper() == 'P':
                                if show_debug_message:
                                    print(f"[DOMSNAPSHOT] Button {button_idx}: selected date '{date_str}' from P tag (event time)")
                                return date_str

                        # 第二優先：尋找非 SMALL 標籤的日期
                        for node_idx, (date_str, tag_name) in dates_found:
                            if tag_name.upper() != 'SMALL':
                                if show_debug_message:
                                    print(f"[DOMSNAPSHOT] Button {button_idx}: selected date '{date_str}' from {tag_name} tag")
                                return date_str

                        # 最後：如果只有 SMALL 標籤，返回第一個
                        if show_debug_message:
                            print(f"[DOMSNAPSHOT] Button {button_idx}: only SMALL tags found, using first: '{dates_found[0][1][0]}'")
                        return dates_found[0][1][0]

                    if show_debug_message:
                        print(f"[DOMSNAPSHOT] Button {button_idx} in container {container_idx}: NO dates found")
                    return None

                # 找到所有購票按鈕並建立順序映射
                for i, node_name in enumerate(node_names):
                    if node_name.lower() == 'button':
                        # 檢查按鈕的 class 屬性
                        is_purchase_button = False

                        if i < len(attributes_list) and attributes_list[i]:
                            attrs = attributes_list[i]
                            # attributes 是一個索引列表，格式為 [name_idx, value_idx, name_idx, value_idx, ...]
                            for j in range(0, len(attrs), 2):
                                if j + 1 < len(attrs):
                                    attr_name_idx = attrs[j]
                                    attr_value_idx = attrs[j + 1]

                                    if (attr_name_idx >= 0 and attr_name_idx < len(strings) and
                                        attr_value_idx >= 0 and attr_value_idx < len(strings)):
                                        attr_name = strings[attr_name_idx]
                                        attr_value = strings[attr_value_idx]

                                        if attr_name == 'class':
                                            # 檢查是否為購票按鈕
                                            if ('btn-buy' in attr_value or
                                                'btn-pink' in attr_value or
                                                'ng-tns-c57' in attr_value):
                                                is_purchase_button = True
                                                break

                        if is_purchase_button:
                            # 在按鈕附近查找日期
                            date = find_date_near_button(i)
                            date_map_by_order.append(date)

                            if show_debug_message:
                                print(f"[DOMSNAPSHOT] Button #{len(date_map_by_order)}: date = '{date}'")

                if show_debug_message:
                    print(f"[DOMSNAPSHOT] Built date mapping for {len(date_map_by_order)} buttons")

        except Exception as e:
            if show_debug_message:
                print(f"[DOMSNAPSHOT] Failed to extract dates via DOMSnapshot: {e}")
                print(f"[DOMSNAPSHOT] Will proceed without date mapping")

        # 步驟 2: 使用 pierce=True 獲取包含 closed Shadow DOM 的完整文檔樹
        document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

        if show_debug_message:
            print(f"[SHADOW DOM] Document retrieved with pierce=True")

        # 步驟 3: 遞歸搜尋所有節點（包括 closed Shadow DOM）
        # 使用計數器來追蹤找到的按鈕順序，並從 date_map_by_order 獲取對應日期
        button_counter = [0]  # 使用列表來在閉包中共享計數器

        async def find_buttons_in_node(node, path="", level=0):
            buttons = []
            indent = "  " * level

            try:
                node_name = getattr(node, 'node_name', '').lower()

                # 檢查當前節點是否為按鈕
                if node_name == 'button':
                    try:
                        # 獲取節點詳細資訊
                        node_desc = await tab.send(cdp.dom.describe_node(node_id=node.node_id, depth=1))

                        # 解析節點屬性
                        attributes = getattr(node_desc, 'attributes', [])
                        attr_dict = {}
                        for i in range(0, len(attributes), 2):
                            if i + 1 < len(attributes):
                                attr_dict[attributes[i]] = attributes[i + 1]

                        # 獲取元素的 HTML 內容
                        outer_html_result = await tab.send(cdp.dom.get_outer_html(node_id=node.node_id))
                        outer_html = getattr(outer_html_result, 'outer_html', outer_html_result)

                        classes = attr_dict.get('class', '')
                        button_text = ""

                        # 嘗試從 HTML 中提取按鈕文字
                        import re
                        text_match = re.search(r'>([^<]*)</button>', outer_html)
                        if text_match:
                            button_text = text_match.group(1).strip()

                        # 檢查是否為 ibon 購票按鈕
                        is_ibon_purchase_button = (
                            'btn-buy' in classes or
                            'btn-pink' in classes or
                            'ng-tns-c57' in classes or  # 特別針對 ibon 的 Angular 類別
                            '線上購票' in button_text or
                            '購票' in button_text
                        )

                        if is_ibon_purchase_button:
                            # 從 date_map_by_order 獲取當前按鈕的日期
                            current_button_index = button_counter[0]
                            button_date = None
                            if current_button_index < len(date_map_by_order):
                                button_date = date_map_by_order[current_button_index]

                            button_counter[0] += 1  # 增加計數器

                            if show_debug_message:
                                print(f"{indent}[SHADOW DOM] [SUCCESS] Found ibon purchase button at {path}")
                                print(f"{indent}    Classes: {classes}")
                                print(f"{indent}    Text: '{button_text}'")
                                if button_date:
                                    print(f"{indent}    Date: '{button_date}' (from DOMSnapshot)")
                                print(f"{indent}    HTML: {outer_html[:100]}...")

                            button_data = {
                                'node_id': node.node_id,
                                'path': path,
                                'attributes': attr_dict,
                                'html': outer_html,
                                'classes': classes,
                                'text': button_text,
                                'method': 'cdp_dom_pierce',
                                'disabled': 'disabled' in attr_dict
                            }

                            # 添加日期（從 DOMSnapshot 映射表獲取）
                            if button_date:
                                button_data['date_context'] = button_date

                            buttons.append(button_data)

                    except Exception as e:
                        if show_debug_message:
                            print(f"{indent}[SHADOW DOM] Error processing button node: {e}")

                # 遞歸檢查子節點
                if hasattr(node, 'children') and node.children:
                    for i, child in enumerate(node.children):
                        child_buttons = await find_buttons_in_node(
                            child, f"{path}/{node_name}[{i}]", level + 1
                        )
                        buttons.extend(child_buttons)

                # 檢查 Shadow roots（關鍵：可存取 closed Shadow DOM）
                if hasattr(node, 'shadow_roots') and node.shadow_roots:
                    # 只在找到 closed shadow DOM 時顯示訊息
                    for i, shadow_root in enumerate(node.shadow_roots):
                        shadow_type = getattr(shadow_root, 'shadow_root_type', 'UNKNOWN')
                        if show_debug_message and shadow_type == 'ShadowRootType.CLOSED':
                            print(f"{indent}[SHADOW DOM] Found {len(node.shadow_roots)} shadow root(s) in {node_name}")
                            print(f"{indent}[SHADOW DOM] Processing {shadow_type} shadow root {i}")

                        shadow_buttons = await find_buttons_in_node(
                            shadow_root, f"{path}/{node_name}[shadow_{shadow_type}_{i}]", level + 1
                        )
                        buttons.extend(shadow_buttons)

            except Exception as e:
                if show_debug_message:
                    print(f"{indent}[SHADOW DOM] Error processing node at {path}: {e}")

            return buttons

        # 開始搜尋 - 修正 API 使用方式
        if show_debug_message:
            print("[SHADOW DOM] Starting recursive search from document...")
            print(f"[SHADOW DOM] Document type: {type(document)}")
            print(f"[SHADOW DOM] Document attributes: {dir(document)}")

        # 直接使用 document 作為根節點，而不是 document.root
        found_buttons = await find_buttons_in_node(document, "root", level=0)

        # 過濾掉 disabled 按鈕，優先返回可用按鈕
        enabled_buttons = [btn for btn in found_buttons if not btn.get('disabled', False)]
        disabled_buttons = [btn for btn in found_buttons if btn.get('disabled', False)]

        if show_debug_message:
            print(f"[SHADOW DOM] Search completed. Found {len(found_buttons)} total buttons")
            print(f"[SHADOW DOM] Enabled buttons: {len(enabled_buttons)}, Disabled buttons: {len(disabled_buttons)}")

            for i, btn in enumerate(enabled_buttons):
                print(f"[SHADOW DOM] Enabled Button {i+1}: '{btn['text']}' at {btn['path']}")

            for i, btn in enumerate(disabled_buttons):
                print(f"[SHADOW DOM] Disabled Button {i+1}: '{btn['text']}' at {btn['path']}")

        # 優先返回可用按鈕，如果沒有可用按鈕才返回所有按鈕
        if enabled_buttons:
            if show_debug_message:
                print(f"[SHADOW DOM] Returning {len(enabled_buttons)} enabled buttons")
            return enabled_buttons
        else:
            if show_debug_message:
                print(f"[SHADOW DOM] No enabled buttons found, returning all {len(found_buttons)} buttons")
            return found_buttons

    except Exception as e:
        if show_debug_message:
            print(f"[SHADOW DOM] Closed Shadow DOM search failed: {e}")
        return []

async def debug_shadow_dom_structure(tab, show_debug_message=True):
    """
    完整探索和輸出 Shadow DOM 結構的除錯工具
    使用 CDP DOM pierce=True 深度分析所有節點，包括 closed Shadow DOM
    """
    try:
        from nodriver import cdp

        if show_debug_message:
            print("\n" + "="*80)
            print("SHADOW DOM STRUCTURE DEBUGGER")
            print("="*80)

        # 使用 pierce=True 獲取包含所有 Shadow DOM 的完整文檔樹
        document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

        if show_debug_message:
            print(f"Document retrieved with pierce=True")
            print(f"Document type: {type(document)}")

        # 統計資料
        stats = {
            'total_nodes': 0,
            'button_nodes': 0,
            'shadow_roots': 0,
            'closed_shadow_roots': 0,
            'purchase_buttons': 0,
            'angular_components': 0
        }

        # 遞歸分析所有節點
        async def analyze_node_recursive(node, path="", level=0, parent_info=""):
            """遞歸分析節點並輸出結構"""
            indent = "  " * level
            stats['total_nodes'] += 1

            try:
                node_name = getattr(node, 'node_name', '').lower()
                node_type = getattr(node, 'node_type', 0)

                # 獲取節點詳細資訊
                if node_type == 1:  # Element node
                    try:
                        node_desc = await tab.send(cdp.dom.describe_node(node_id=node.node_id, depth=1))
                        attributes = getattr(node_desc, 'attributes', [])

                        # 解析屬性
                        attr_dict = {}
                        for i in range(0, len(attributes), 2):
                            if i + 1 < len(attributes):
                                attr_dict[attributes[i]] = attributes[i + 1]

                        # 檢查是否為按鈕相關元素
                        is_button = node_name == 'button'
                        is_purchase_related = False

                        # 獲取元素內容
                        element_html = ""
                        element_text = ""
                        try:
                            outer_html_result = await tab.send(cdp.dom.get_outer_html(node_id=node.node_id))
                            element_html = getattr(outer_html_result, 'outer_html', str(outer_html_result))

                            # 提取文字內容
                            import re
                            text_match = re.search(r'>([^<]*)</.*?>', element_html)
                            if text_match:
                                element_text = text_match.group(1).strip()
                        except:
                            pass

                        # 檢查是否為購票相關元素
                        if (is_button and ('線上購票' in element_text or '購票' in element_text)) or \
                           ('btn-buy' in attr_dict.get('class', '') or 'btn-pink' in attr_dict.get('class', '')):
                            is_purchase_related = True
                            stats['purchase_buttons'] += 1

                        # 檢查是否為 Angular 組件
                        is_angular = any(attr.startswith('_ngcontent') or attr.startswith('ng-')
                                       for attr in attr_dict.keys())
                        if is_angular:
                            stats['angular_components'] += 1

                        # 輸出節點資訊
                        if show_debug_message and (is_button or is_purchase_related or is_angular or level < 5):
                            node_info = f"{indent}NODE {node_name.upper()}"

                            if is_purchase_related:
                                node_info += " [PURCHASE BUTTON]"
                            elif is_button:
                                node_info += " [BUTTON]"

                            if is_angular:
                                node_info += " [ANGULAR]"

                            print(f"{node_info} @ {path}")

                            # 顯示重要屬性
                            important_attrs = ['class', 'id', 'disabled', 'type']
                            for attr in important_attrs:
                                if attr in attr_dict:
                                    print(f"{indent}    {attr}: {attr_dict[attr]}")

                            # 顯示文字內容
                            if element_text:
                                print(f"{indent}    Text: '{element_text}'")

                            # 顯示 HTML (截取前100字符)
                            if element_html and (is_purchase_related or is_button):
                                html_preview = element_html[:150] + "..." if len(element_html) > 150 else element_html
                                print(f"{indent}    HTML: {html_preview}")

                        if is_button:
                            stats['button_nodes'] += 1

                    except Exception as e:
                        if show_debug_message and level < 3:
                            print(f"{indent}[ERROR] Error analyzing element {node_name}: {e}")

                # 檢查子節點
                if hasattr(node, 'children') and node.children:
                    for i, child in enumerate(node.children):
                        child_path = f"{path}/{node_name}[{i}]"
                        await analyze_node_recursive(child, child_path, level + 1, node_name)

                # 檢查 Shadow roots (關鍵功能)
                if hasattr(node, 'shadow_roots') and node.shadow_roots:
                    stats['shadow_roots'] += len(node.shadow_roots)

                    for i, shadow_root in enumerate(node.shadow_roots):
                        shadow_type = getattr(shadow_root, 'shadow_root_type', 'UNKNOWN')

                        if shadow_type == 'ShadowRootType.CLOSED':
                            stats['closed_shadow_roots'] += 1

                        if show_debug_message:
                            print(f"{indent}[SHADOW] SHADOW ROOT [{shadow_type}] in {node_name.upper()}")

                        shadow_path = f"{path}/{node_name}[shadow_{shadow_type}_{i}]"
                        await analyze_node_recursive(shadow_root, shadow_path, level + 1, f"shadow_of_{node_name}")

            except Exception as e:
                if show_debug_message and level < 3:
                    print(f"{indent}[WARNING] Error processing node at {path}: {e}")

        # 開始分析
        if show_debug_message:
            print("[DEBUG] Starting recursive DOM analysis...")

        await analyze_node_recursive(document, "root")

        # 輸出統計資料
        if show_debug_message:
            print("\n" + "="*50)
            print("[SUMMARY] ANALYSIS SUMMARY")
            print("="*50)
            print(f"[INFO] Total nodes analyzed: {stats['total_nodes']}")
            print(f"[INFO] Button nodes found: {stats['button_nodes']}")
            print(f"[INFO] Purchase buttons found: {stats['purchase_buttons']}")
            print(f"[INFO] Shadow roots found: {stats['shadow_roots']}")
            print(f"[STATS] Closed shadow roots: {stats['closed_shadow_roots']}")
            print(f"[STATS] Angular components: {stats['angular_components']}")
            print("="*50)

        return stats

    except Exception as e:
        if show_debug_message:
            print(f"[ERROR] Shadow DOM structure debug failed: {e}")
        return None

async def compare_search_methods(tab, target_text="線上購票", show_debug_message=True):
    """
    比較不同搜尋方法的結果，專門針對多按鈕情況進行分析
    """
    try:
        from nodriver import cdp
        import re

        if show_debug_message:
            print("\n" + "="*80)
            print("[DEBUG] SEARCH METHODS COMPARISON")
            print("="*80)

        results = {
            'tab_find': [],
            'cdp_dom': [],
            'javascript': [],
            'summary': {}
        }

        # 方法 1: tab.find() 搜尋
        if show_debug_message:
            print("\n[METHOD 1] NoDriver tab.find()")
            print("-" * 40)

        try:
            # 嘗試多次 find 以找到所有按鈕
            found_elements = []
            for attempt in range(10):  # 最多嘗試10次
                element = await tab.find(target_text, best_match=True)
                if element:
                    element_str = str(element)
                    # 避免重複
                    if element_str not in found_elements:
                        found_elements.append(element_str)

                        # 分析這個元素
                        is_disabled = 'disabled=' in element_str or 'disabled"' in element_str

                        # 提取日期和場地資訊
                        date_match = re.search(r'(\d{4}/\d{2}/\d{2})', element_str)
                        venue_match = re.search(r'>(.*?)<.*?>(.*?)<.*?>線上購票', element_str)

                        element_info = {
                            'html': element_str,
                            'disabled': is_disabled,
                            'date': date_match.group(1) if date_match else 'Unknown',
                            'attempt': attempt + 1
                        }

                        results['tab_find'].append(element_info)

                        if show_debug_message:
                            status = "🔴 DISABLED" if is_disabled else "🟢 ENABLED"
                            print(f"  Attempt {attempt + 1}: {status}")
                            print(f"    Date: {element_info['date']}")
                            print(f"    HTML: {element_str[:100]}...")

                        # 嘗試隱藏這個元素以找到下一個
                        try:
                            await tab.evaluate('''
                                (function() {
                                    const buttons = document.querySelectorAll('button');
                                    buttons.forEach(btn => {
                                        if (btn.textContent.includes('線上購票')) {
                                            btn.style.visibility = 'hidden';
                                        }
                                    });
                                })();
                            ''')
                            await tab.sleep(0.1)
                        except:
                            pass
                else:
                    break

            # 恢復所有隱藏的元素
            try:
                await tab.evaluate('''
                    (function() {
                        const buttons = document.querySelectorAll('button');
                        buttons.forEach(btn => {
                            btn.style.visibility = '';
                        });
                    })();
                ''')
            except:
                pass

        except Exception as e:
            if show_debug_message:
                print(f"  [ERROR] tab.find() failed: {e}")

        # 方法 2: CDP DOM 搜尋
        if show_debug_message:
            print("\n[METHOD 2] CDP DOM Search")
            print("-" * 40)

        try:
            document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))

            async def find_purchase_buttons(node, path=""):
                buttons = []
                try:
                    node_name = getattr(node, 'node_name', '').lower()

                    if node_name == 'button':
                        # 獲取按鈕詳細資訊
                        try:
                            outer_html_result = await tab.send(cdp.dom.get_outer_html(node_id=node.node_id))
                            element_html = getattr(outer_html_result, 'outer_html', str(outer_html_result))

                            if '線上購票' in element_html:
                                # 分析按鈕周圍的結構以提取日期和場地
                                parent_html = ""
                                try:
                                    # 嘗試獲取父元素的 HTML
                                    parent_node = getattr(node, 'parent_id', None)
                                    if parent_node:
                                        parent_result = await tab.send(cdp.dom.get_outer_html(node_id=parent_node))
                                        parent_html = getattr(parent_result, 'outer_html', "")
                                except:
                                    pass

                                is_disabled = 'disabled=' in element_html

                                # 提取日期
                                date_match = re.search(r'(\d{4}/\d{2}/\d{2})', parent_html or element_html)

                                # 提取場地
                                venue_match = re.search(r'(LIVE WAREHOUSE|Legacy Taichung)', parent_html or element_html)

                                button_info = {
                                    'html': element_html,
                                    'parent_html': parent_html[:200] + "..." if len(parent_html) > 200 else parent_html,
                                    'disabled': is_disabled,
                                    'date': date_match.group(1) if date_match else 'Unknown',
                                    'venue': venue_match.group(1) if venue_match else 'Unknown',
                                    'path': path
                                }

                                buttons.append(button_info)

                                if show_debug_message:
                                    status = "[DISABLED]" if is_disabled else "[ENABLED]"
                                    print(f"  Found: {status}")
                                    print(f"    Date: {button_info['date']}")
                                    print(f"    Venue: {button_info['venue']}")
                                    print(f"    Path: {path}")

                        except Exception as e:
                            if show_debug_message:
                                print(f"  [ERROR] Error analyzing button: {e}")

                    # 遞歸檢查子節點
                    if hasattr(node, 'children') and node.children:
                        for i, child in enumerate(node.children):
                            child_buttons = await find_purchase_buttons(child, f"{path}/{node_name}[{i}]")
                            buttons.extend(child_buttons)

                    # 檢查 Shadow roots
                    if hasattr(node, 'shadow_roots') and node.shadow_roots:
                        for i, shadow_root in enumerate(node.shadow_roots):
                            shadow_buttons = await find_purchase_buttons(shadow_root, f"{path}/{node_name}[shadow_{i}]")
                            buttons.extend(shadow_buttons)

                except Exception as e:
                    pass

                return buttons

            cdp_buttons = await find_purchase_buttons(document, "root")
            results['cdp_dom'] = cdp_buttons

        except Exception as e:
            if show_debug_message:
                print(f"  [ERROR] CDP DOM search failed: {e}")

        # 方法 3: JavaScript 搜尋
        if show_debug_message:
            print("\n[METHOD 3] JavaScript Search")
            print("-" * 40)

        try:
            js_result = await tab.evaluate('''
                (function() {
                    const results = [];

                    // 搜尋所有購票按鈕
                    const buttons = document.querySelectorAll('button');

                    buttons.forEach((btn, index) => {
                        if (btn.textContent.includes('線上購票')) {
                            // 找到父容器以獲取日期和場地資訊
                            let parentContainer = btn.closest('.col-12.grid');
                            let parentHTML = parentContainer ? parentContainer.outerHTML : btn.outerHTML;

                            // 提取日期
                            const dateMatch = parentHTML.match(/(\\d{4}\\/\\d{2}\\/\\d{2})/);

                            // 提取場地
                            const venueMatch = parentHTML.match(/(LIVE WAREHOUSE|Legacy Taichung)/);

                            results.push({
                                index: index,
                                text: btn.textContent.trim(),
                                disabled: btn.disabled || btn.hasAttribute('disabled'),
                                className: btn.className,
                                date: dateMatch ? dateMatch[1] : 'Unknown',
                                venue: venueMatch ? venueMatch[1] : 'Unknown',
                                html: btn.outerHTML,
                                parentHTML: parentHTML.substring(0, 300)
                            });
                        }
                    });

                    return results;
                })();
            ''', return_by_value=True)

            results['javascript'] = js_result

            if show_debug_message:
                for i, btn in enumerate(js_result):
                    status = "🔴 DISABLED" if btn['disabled'] else "🟢 ENABLED"
                    print(f"  Button {i+1}: {status}")
                    print(f"    Date: {btn['date']}")
                    print(f"    Venue: {btn['venue']}")
                    print(f"    Class: {btn['className']}")

        except Exception as e:
            if show_debug_message:
                print(f"  [ERROR] JavaScript search failed: {e}")

        # 總結比較
        if show_debug_message:
            print("\n[SUMMARY] COMPARISON SUMMARY")
            print("=" * 50)
            print(f"tab.find() found: {len(results['tab_find'])} elements")
            print(f"CDP DOM found: {len(results['cdp_dom'])} buttons")
            print(f"JavaScript found: {len(results['javascript'])} buttons")

            enabled_counts = {
                'tab_find': sum(1 for x in results['tab_find'] if not x['disabled']),
                'cdp_dom': sum(1 for x in results['cdp_dom'] if not x['disabled']),
                'javascript': sum(1 for x in results['javascript'] if not x['disabled'])
            }

            print(f"\nEnabled buttons:")
            for method, count in enabled_counts.items():
                print(f"  {method}: {count}")

        results['summary'] = {
            'total_found': {
                'tab_find': len(results['tab_find']),
                'cdp_dom': len(results['cdp_dom']),
                'javascript': len(results['javascript'])
            },
            'enabled_found': enabled_counts
        }

        return results

    except Exception as e:
        if show_debug_message:
            print(f"[ERROR] Search methods comparison failed: {e}")
        return None

async def search_and_click_with_nodriver_native(tab, show_debug_message, target_text="線上購票"):
    """
    使用 NoDriver 原生方法搜尋並點擊按鈕
    這是最可靠的方法，因為 NoDriver 有內建的 Shadow DOM 支援
    """
    try:
        if show_debug_message:
            print(f"[NATIVE] Starting NoDriver native search for: {target_text}")

        # 方法 1: 使用 JavaScript 搜尋所有購票按鈕並選擇可用的
        try:
            if show_debug_message:
                print(f"[NATIVE] Searching for all purchase buttons via JavaScript")

            # 使用 JavaScript 搜尋所有購票按鈕，包括 Shadow DOM
            buttons_info = await tab.evaluate('''
                (function() {
                    const buttons = [];

                    // 遞迴搜尋 Shadow DOM
                    function searchShadowDOM(root, path = '') {
                        const elements = root.querySelectorAll('*');
                        elements.forEach((el, idx) => {
                            if (el.shadowRoot) {
                                searchShadowDOM(el.shadowRoot, path + `shadow_${idx}_`);
                            }
                        });

                        // 搜尋購票按鈕
                        const purchaseButtons = root.querySelectorAll('button.btn-buy, button:contains("線上購票"), button[class*="btn-buy"], button[class*="btn-pink"]');
                        purchaseButtons.forEach((btn, btnIdx) => {
                            const isDisabled = btn.hasAttribute('disabled') || btn.disabled;
                            const btnText = btn.textContent.trim();
                            const btnClass = btn.className;

                            if (btnText.includes('線上購票') || btnText.includes('購票') || btnClass.includes('btn-buy')) {
                                buttons.push({
                                    text: btnText,
                                    disabled: isDisabled,
                                    className: btnClass,
                                    path: path + `btn_${btnIdx}`,
                                    element: btn.outerHTML
                                });

                                // 儲存元素的引用以便點擊
                                btn.setAttribute('data-maxbot-index', buttons.length - 1);
                            }
                        });
                    }

                    // 開始搜尋
                    searchShadowDOM(document);

                    return buttons;
                })();
            ''', return_by_value=True)

            if show_debug_message:
                print(f"[NATIVE] Found {len(buttons_info)} purchase buttons total")
                for i, btn_info in enumerate(buttons_info):
                    status = "DISABLED" if btn_info['disabled'] else "ENABLED"
                    print(f"[NATIVE]   Button {i}: {btn_info['text']} - {status}")

            # 找到第一個可用的按鈕
            enabled_buttons = [btn for btn in buttons_info if not btn['disabled']]

            if enabled_buttons:
                target_button = enabled_buttons[0]
                if show_debug_message:
                    print(f"[NATIVE] Selecting first enabled button: {target_button['text']}")

                # 點擊第一個可用的按鈕
                click_result = await tab.evaluate('''
                    (function() {
                        const buttons = document.querySelectorAll('button[data-maxbot-index]');
                        let targetButton = null;

                        buttons.forEach(btn => {
                            if (!btn.disabled && !btn.hasAttribute('disabled')) {
                                if (!targetButton) {
                                    targetButton = btn;
                                }
                            }
                        });

                        if (targetButton) {
                            targetButton.click();
                            return {
                                success: true,
                                text: targetButton.textContent.trim(),
                                className: targetButton.className
                            };
                        }
                        return {success: false, error: 'No enabled button found'};
                    })();
                ''', return_by_value=True)

                if isinstance(click_result, dict) and click_result.get('success'):
                    if show_debug_message:
                        print(f"[NATIVE] Successfully clicked enabled button: {click_result.get('text') if isinstance(click_result, dict) else 'unknown'}")

                    # 檢查頁面導航
                    await tab.sleep(1.0)
                    try:
                        current_url = await tab.evaluate('window.location.href', return_by_value=True)
                        if show_debug_message:
                            print(f"[NATIVE] Current URL after click: {current_url}")
                    except:
                        pass

                    return {
                        "success": True,
                        "method": "nodriver_native_javascript",
                        "element": target_button['element'],
                        "buttonText": target_button['text']
                    }
                else:
                    if show_debug_message:
                        print(f"[NATIVE] JavaScript click failed: {click_result.get('error') if isinstance(click_result, dict) else str(click_result)}")

            else:
                if show_debug_message:
                    print(f"[NATIVE] No enabled buttons found among {len(buttons_info)} total buttons")

        except Exception as js_error:
            if show_debug_message:
                print(f"[NATIVE] JavaScript search failed: {js_error}")

        # 方法 2: 改進的 tab.find() 方法 - 實作智能 disabled 按鈕跳過
        try:
            if show_debug_message:
                print(f"[NATIVE] Enhanced tab.find() with intelligent disabled filtering for text: '{target_text}'")

            # 先用 JavaScript 尋找所有匹配的購票按鈕並分析其狀態
            element_analysis = await tab.evaluate('''
                (function() {
                    const results = [];
                    const searchText = '線上購票';

                    // 搜尋所有可能的購票按鈕
                    const allButtons = document.querySelectorAll('button');

                    allButtons.forEach((btn, index) => {
                        const text = btn.textContent.trim();
                        const classes = btn.className || '';
                        const isDisabled = btn.disabled || btn.hasAttribute('disabled');
                        const isVisible = btn.offsetParent !== null;
                        const isPurchaseButton = text.includes(searchText) || text.includes('購票') ||
                                               classes.includes('btn-buy') || classes.includes('btn-pink');

                        if (isPurchaseButton) {
                            results.push({
                                index: index,
                                text: text,
                                classes: classes,
                                disabled: isDisabled,
                                visible: isVisible,
                                outerHTML: btn.outerHTML.substring(0, 150) + '...'
                            });
                        }
                    });

                    return {
                        totalButtons: allButtons.length,
                        purchaseButtons: results,
                        enabledCount: results.filter(b => !b.disabled && b.visible).length,
                        disabledCount: results.filter(b => b.disabled).length
                    };
                })();
            ''', return_by_value=True)

            # 安全處理 RemoteObject
            try:
                if isinstance(element_analysis, dict):
                    if show_debug_message:
                        print(f"[NATIVE] Button analysis: {element_analysis.get('enabledCount', 0)} enabled, {element_analysis.get('disabledCount', 0)} disabled")

                        purchase_buttons = element_analysis.get('purchaseButtons', [])
                        if purchase_buttons:
                            for i, btn in enumerate(purchase_buttons):
                                status = "[ENABLED]" if not btn.get('disabled', True) and btn.get('visible', False) else "[DISABLED]" if btn.get('disabled', True) else "[HIDDEN]"
                                print(f"[NATIVE]   Button {i+1}: {status} '{btn.get('text', '')}' classes='{btn.get('classes', '')}'")

                    # 如果有可用按鈕，優先使用第一個可用的
                    enabled_buttons = [btn for btn in element_analysis.get('purchaseButtons', [])
                                     if not btn.get('disabled', True) and btn.get('visible', False)]
                else:
                    if show_debug_message:
                        print(f"[NATIVE] JavaScript analysis returned non-dict type: {type(element_analysis)}")
                    enabled_buttons = []
            except Exception as analysis_error:
                if show_debug_message:
                    print(f"[NATIVE] Error processing analysis results: {analysis_error}")
                enabled_buttons = []

            if enabled_buttons:
                if show_debug_message:
                    print(f"[NATIVE] Found {len(enabled_buttons)} enabled buttons, using the first one")

                # 使用 JavaScript 直接點擊第一個可用按鈕
                click_result = await tab.evaluate(f'''
                    (function() {{
                        const searchText = '線上購票';
                        const allButtons = document.querySelectorAll('button');

                        for (let btn of allButtons) {{
                            const text = btn.textContent.trim();
                            const classes = btn.className || '';
                            const isDisabled = btn.disabled || btn.hasAttribute('disabled');
                            const isVisible = btn.offsetParent !== null;
                            const isPurchaseButton = text.includes(searchText) || text.includes('購票') ||
                                                   classes.includes('btn-buy') || classes.includes('btn-pink');

                            if (isPurchaseButton && !isDisabled && isVisible) {{
                                console.log('[NATIVE] Clicking enabled button:', btn.outerHTML.substring(0,100));
                                btn.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                btn.click();
                                return {{
                                    success: true,
                                    buttonText: text,
                                    classes: classes
                                }};
                            }}
                        }}

                        return {{ success: false, reason: 'No enabled button found' }};
                    }})();
                ''', return_by_value=True)

                if click_result.get('success'):
                    if show_debug_message:
                        print(f"[NATIVE] Successfully clicked enabled button: '{click_result.get('buttonText', '')}'")

                    # 等待頁面響應
                    await tab.sleep(1.0)
                    try:
                        current_url = await tab.evaluate('window.location.href', return_by_value=True)
                        if show_debug_message:
                            print(f"[NATIVE] Current URL after click: {current_url}")
                    except:
                        pass

                    return {
                        "success": True,
                        "method": "nodriver_native_js_enabled_click",
                        "buttonText": click_result.get('buttonText', ''),
                        "classes": click_result.get('classes', '')
                    }

            # 如果沒有可用按鈕，嘗試傳統的 tab.find() 方法
            max_attempts = 3  # 減少嘗試次數避免無限循環
            for attempt in range(max_attempts):
                try:
                    element = await tab.find(target_text, best_match=True)

                    if not element:
                        if show_debug_message:
                            print(f"[NATIVE] No element found on attempt {attempt + 1}")
                        break

                    if show_debug_message:
                        print(f"[NATIVE] Found element on attempt {attempt + 1}: {element}")

                    # 檢查是否 disabled
                    element_str = str(element)
                    is_disabled = 'disabled=' in element_str or 'disabled"' in element_str

                    if show_debug_message:
                        print(f"[NATIVE] Element string: {element_str[:150]}...")
                        print(f"[NATIVE] Is disabled: {is_disabled}")

                    if is_disabled:
                        if show_debug_message:
                            print(f"[NATIVE] Element on attempt {attempt + 1} is disabled, will skip")
                        continue
                    else:
                        if show_debug_message:
                            print(f"[NATIVE] Found enabled element on attempt {attempt + 1}")
                        break

                except Exception as find_error:
                    if show_debug_message:
                        print(f"[NATIVE] Find error on attempt {attempt + 1}: {find_error}")
                    break

            if element:

                # 檢查元素是否可點擊
                try:
                    # 滾動到元素位置
                    await element.scroll_into_view()
                    await tab.sleep(0.3)

                    # 使用 NoDriver 原生點擊
                    await element.click()

                    if show_debug_message:
                        print(f"[NATIVE] Successfully clicked element via native method")

                    # 檢查頁面是否導航
                    await tab.sleep(1.0)
                    try:
                        current_url = await tab.evaluate('window.location.href', return_by_value=True)
                        if show_debug_message:
                            print(f"[NATIVE] Current URL after click: {current_url}")
                    except:
                        pass

                    return {
                        "success": True,
                        "method": "nodriver_native_find",
                        "element": str(element),
                        "buttonText": target_text
                    }

                except Exception as click_error:
                    if show_debug_message:
                        print(f"[NATIVE] Click failed on found element: {click_error}")

        except Exception as find_error:
            if show_debug_message:
                print(f"[NATIVE] tab.find() failed: {find_error}")

        # 方法 2: 使用 tab.select() 搜尋 CSS 選擇器
        try:
            if show_debug_message:
                print(f"[NATIVE] Trying tab.select() with purchase button selectors")

            # 嘗試多個可能的選擇器 - 增強 ibon 特定選擇器
            selectors = [
                'button:contains("線上購票")',
                'button.btn-buy:not([disabled])',  # 只選擇非 disabled 的按鈕
                'button.btn-pink:not([disabled])',
                'button[class*="btn-buy"]:not([disabled])',
                'button[class*="btn-pink"]:not([disabled])',
                'button[class*="ng-tns-c57"]:not([disabled])',  # ibon Angular 特定類別
                'button.ng-star-inserted:not([disabled])',
                'button[class*="btn"][class*="pink"]:not([disabled])',
                '.btn.btn-pink.btn-buy:not([disabled])',
                '[role="button"][class*="btn-buy"]:not([disabled])'
            ]

            for selector in selectors:
                try:
                    element = await tab.select(selector)
                    if element:
                        if show_debug_message:
                            print(f"[NATIVE] Found element via selector '{selector}': {element}")

                        # 檢查文字是否匹配
                        try:
                            element_text = await element.get_text()
                            if target_text in element_text or 'btn-buy' in (element.attrs.get('class', '')):
                                # 點擊元素
                                await element.scroll_into_view()
                                await tab.sleep(0.3)
                                await element.click()

                                if show_debug_message:
                                    print(f"[NATIVE] [SUCCESS] Successfully clicked via selector: {selector}")

                                await tab.sleep(1.0)
                                return {
                                    "success": True,
                                    "method": f"nodriver_native_select_{selector}",
                                    "element": str(element),
                                    "buttonText": element_text
                                }
                        except Exception as text_error:
                            if show_debug_message:
                                print(f"[NATIVE] Text check failed for {selector}: {text_error}")
                            continue

                except Exception as selector_error:
                    if show_debug_message:
                        print(f"[NATIVE] Selector '{selector}' failed: {selector_error}")
                    continue

        except Exception as select_error:
            if show_debug_message:
                print(f"[NATIVE] tab.select() method failed: {select_error}")

        # 方法 3: 使用 tab.query_selector_all() 然後篩選
        try:
            if show_debug_message:
                print(f"[NATIVE] Trying query_selector_all for buttons")

            # 獲取所有按鈕
            buttons = await tab.query_selector_all('button')
            if show_debug_message:
                print(f"[NATIVE] Found {len(buttons)} total buttons")

            for i, button in enumerate(buttons):
                try:
                    # 檢查按鈕文字和類別
                    button_text = await button.get_text()
                    button_classes = button.attrs.get('class', '')

                    if show_debug_message and i < 5:  # 只顯示前5個按鈕的詳細資訊
                        print(f"[NATIVE] Button {i}: '{button_text}' classes: '{button_classes}'")

                    # 檢查是否為 disabled 按鈕
                    is_disabled = button.attrs.get('disabled') is not None

                    if (target_text in button_text or
                        'btn-buy' in button_classes or
                        'btn-pink' in button_classes or
                        'ng-tns-c57' in button_classes):

                        if show_debug_message:
                            status = "[DISABLED]" if is_disabled else "[ENABLED]"
                            print(f"[NATIVE] Found matching button {status}: '{button_text}' with classes: '{button_classes}'")

                        # 跳過 disabled 按鈕
                        if is_disabled:
                            if show_debug_message:
                                print(f"[NATIVE] Skipping disabled button: '{button_text}'")
                            continue

                        await button.scroll_into_view()
                        await tab.sleep(0.3)
                        await button.click()

                        if show_debug_message:
                            print(f"[NATIVE] [SUCCESS] Successfully clicked enabled button via query_selector_all")

                        await tab.sleep(1.0)
                        return {
                            "success": True,
                            "method": "nodriver_native_query_all_enabled",
                            "element": str(button),
                            "buttonText": button_text
                        }

                except Exception as button_error:
                    if show_debug_message:
                        print(f"[NATIVE] Button {i} processing failed: {button_error}")
                    continue

        except Exception as query_error:
            if show_debug_message:
                print(f"[NATIVE] query_selector_all failed: {query_error}")

        if show_debug_message:
            print(f"[NATIVE] [ERROR] All native methods failed")

        return {"success": False, "error": "All NoDriver native methods failed"}

    except Exception as e:
        if show_debug_message:
            print(f"[NATIVE] Exception: {e}")
        return {"success": False, "error": str(e)}

async def search_and_click_immediately(tab, show_debug_message, target_text="線上購票"):
    """
    搜尋並立即點擊按鈕，避免 NodeId 失效問題
    """
    try:
        if show_debug_message:
            print(f"[IMMEDIATE] Starting immediate search and click for: {target_text}")

        # 使用純 JavaScript 搜尋並立即點擊
        immediate_click_js = f'''
        (function() {{
            const targetText = "{target_text}";
            let foundAndClicked = false;
            const searchResults = [];

            console.log(`[IMMEDIATE] Starting search for: "${{targetText}}"`);

            function immediateButtonClick(button, source) {{
                try {{
                    if (button.disabled) {{
                        console.log(`[IMMEDIATE] Button disabled in ${{source}}`);
                        return false;
                    }}

                    if (button.offsetParent === null) {{
                        console.log(`[IMMEDIATE] Button not visible in ${{source}}`);
                        return false;
                    }}

                    const beforeUrl = window.location.href;
                    console.log(`[IMMEDIATE] Clicking button from ${{source}}, URL before: ${{beforeUrl}}`);

                    // 立即執行多種點擊方法
                    button.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                    button.focus();

                    // 模擬完整的點擊序列
                    const events = [
                        new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}),
                        new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}),
                        new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }})
                    ];

                    events.forEach(event => button.dispatchEvent(event));
                    button.click();

                    // Form 提交（如果適用）
                    const form = button.closest('form');
                    if (form) {{
                        console.log(`[IMMEDIATE] Submitting parent form`);
                        form.submit();
                    }}

                    // 鍵盤事件
                    button.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                    button.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', keyCode: 13, bubbles: true }}));

                    console.log(`[IMMEDIATE] ✅ Button clicked from ${{source}}`);

                    // 檢查導航
                    setTimeout(() => {{
                        const afterUrl = window.location.href;
                        if (beforeUrl !== afterUrl) {{
                            console.log(`[IMMEDIATE] ✅ Page navigation detected: ${{afterUrl}}`);
                        }} else {{
                            console.log(`[IMMEDIATE] ⚠️ No navigation detected`);
                        }}
                    }}, 100);

                    return true;
                }} catch (e) {{
                    console.log(`[IMMEDIATE] Click failed from ${{source}}: ${{e.message}}`);
                    return false;
                }}
            }}

            // 方法 1: 全域按鈕搜尋
            try {{
                const allButtons = document.querySelectorAll('button');
                console.log(`[IMMEDIATE] Found ${{allButtons.length}} buttons globally`);
                searchResults.push(`found_${{allButtons.length}}_global_buttons`);

                for (let btn of allButtons) {{
                    const text = btn.textContent.trim();
                    const classes = btn.className || '';

                    if (text === targetText && classes.includes('btn-buy')) {{
                        console.log(`[IMMEDIATE] Found target via global search`);
                        searchResults.push('target_found_globally');

                        if (immediateButtonClick(btn, 'global_search')) {{
                            foundAndClicked = true;
                            searchResults.push('clicked_from_global_search');
                            return {{ success: true, method: 'global_search', attempts: searchResults }};
                        }}
                    }}
                }}
            }} catch (e) {{
                console.log(`[IMMEDIATE] Global search failed: ${{e.message}}`);
                searchResults.push(`global_search_error: ${{e.message}}`);
            }}

            // 方法 2: TreeWalker 深度搜尋（如果全域搜尋失敗）
            if (!foundAndClicked) {{
                try {{
                    console.log(`[IMMEDIATE] Starting TreeWalker search`);
                    const walker = document.createTreeWalker(
                        document.body || document.documentElement,
                        NodeFilter.SHOW_ELEMENT,
                        null,
                        false
                    );

                    let node;
                    while (node = walker.nextNode()) {{
                        // 檢查按鈕
                        if (node.tagName && node.tagName.toLowerCase() === 'button') {{
                            const text = node.textContent.trim();
                            const classes = node.className || '';

                            if (text === targetText && classes.includes('btn-buy')) {{
                                console.log(`[IMMEDIATE] Found target via TreeWalker`);
                                searchResults.push('target_found_via_treewalker');

                                if (immediateButtonClick(node, 'treewalker')) {{
                                    foundAndClicked = true;
                                    searchResults.push('clicked_from_treewalker');
                                    return {{ success: true, method: 'treewalker', attempts: searchResults }};
                                }}
                            }}
                        }}

                        // 檢查 Shadow DOM
                        if (node.shadowRoot) {{
                            try {{
                                const shadowButtons = node.shadowRoot.querySelectorAll('button');
                                console.log(`[IMMEDIATE] Found ${{shadowButtons.length}} buttons in shadow DOM of ${{node.tagName}}`);

                                for (let shadowBtn of shadowButtons) {{
                                    const text = shadowBtn.textContent.trim();
                                    const classes = shadowBtn.className || '';

                                    if (text === targetText && classes.includes('btn-buy')) {{
                                        console.log(`[IMMEDIATE] Found target in shadow DOM`);
                                        searchResults.push(`target_found_in_shadow_${{node.tagName}}`);

                                        if (immediateButtonClick(shadowBtn, `shadow_${{node.tagName}}`)) {{
                                            foundAndClicked = true;
                                            searchResults.push(`clicked_from_shadow_${{node.tagName}}`);
                                            return {{ success: true, method: `shadow_${{node.tagName}}`, attempts: searchResults }};
                                        }}
                                    }}
                                }}
                            }} catch (e) {{
                                console.log(`[IMMEDIATE] Shadow DOM access failed for ${{node.tagName}}: ${{e.message}}`);
                                searchResults.push(`shadow_error_${{node.tagName}}: ${{e.message}}`);
                            }}
                        }}

                        // 特殊處理 app-game
                        if (node.tagName && node.tagName.toLowerCase() === 'app-game') {{
                            try {{
                                const gameButtons = node.querySelectorAll('button');
                                console.log(`[IMMEDIATE] Found ${{gameButtons.length}} buttons in app-game`);
                                searchResults.push(`found_${{gameButtons.length}}_buttons_in_app_game`);

                                for (let gameBtn of gameButtons) {{
                                    const text = gameBtn.textContent.trim();
                                    const classes = gameBtn.className || '';

                                    if (text === targetText && classes.includes('btn-buy')) {{
                                        console.log(`[IMMEDIATE] Found target in app-game`);
                                        searchResults.push('target_found_in_app_game');

                                        if (immediateButtonClick(gameBtn, 'app_game')) {{
                                            foundAndClicked = true;
                                            searchResults.push('clicked_from_app_game');
                                            return {{ success: true, method: 'app_game', attempts: searchResults }};
                                        }}
                                    }}
                                }}
                            }} catch (e) {{
                                console.log(`[IMMEDIATE] app-game access failed: ${{e.message}}`);
                                searchResults.push(`app_game_error: ${{e.message}}`);
                            }}
                        }}
                    }}
                }} catch (e) {{
                    console.log(`[IMMEDIATE] TreeWalker search failed: ${{e.message}}`);
                    searchResults.push(`treewalker_error: ${{e.message}}`);
                }}
            }}

            console.log(`[IMMEDIATE] Search completed. Found and clicked: ${{foundAndClicked}}`);
            return {{ success: foundAndClicked, method: foundAndClicked ? 'found' : 'not_found', attempts: searchResults }};
        }})();
        '''

        # 執行立即搜尋和點擊
        result_raw = await tab.evaluate(immediate_click_js, return_by_value=True)

        # 解析 NoDriver 格式
        if not isinstance(result_raw, dict):
            from . import util
            result = util.parse_nodriver_result(result_raw) if result_raw else {}
        else:
            result = result_raw

        if show_debug_message:
            if isinstance(result, dict):
                success = result.get('success', False)
                method = result.get('method', 'unknown')
                attempts = result.get('attempts', [])
                print(f"[IMMEDIATE] {'[SUCCESS]' if success else '[FAILED]'} via {method}")
                print(f"[IMMEDIATE] Search attempts: {', '.join(attempts)}")
            else:
                print(f"[IMMEDIATE] Unexpected result after parsing: {result}")

        # 短暫等待頁面導航
        await tab.sleep(0.5)

        # 檢查 URL 變化
        try:
            final_url = await tab.evaluate('window.location.href')
            if show_debug_message:
                print(f"[IMMEDIATE] Final URL: {final_url}")
        except:
            pass

        return result

    except Exception as e:
        if show_debug_message:
            print(f"[IMMEDIATE] Exception: {e}")
        return {"success": False, "error": str(e), "attempts": []}

async def enhanced_javascript_shadow_search(tab, show_debug_message):
    """
    使用純 JavaScript 穿透 Shadow DOM，基於 NoDriver API 指南推薦方法
    參考 stackoverflow.max-everyday.com 的技術方案
    """
    try:
        if show_debug_message:
            print("[JS SHADOW] Starting enhanced JavaScript Shadow DOM search...")

        # 基於瀏覽器內建能力的 Shadow DOM 穿透 JavaScript
        shadow_search_js = '''
        (function() {
            const results = [];
            const debugInfo = {
                totalElements: 0,
                shadowElements: 0,
                closedShadowElements: 0,
                buttonsFound: 0
            };

            // 遞歸搜尋所有元素，包括 Shadow DOM
            function searchAllElements(root, path = "root", depth = 0) {
                const indent = "  ".repeat(depth);
                console.log(`[JS SHADOW] ${indent}Searching: ${path}`);

                // 搜尋當前層級的所有元素
                const elements = root.querySelectorAll('*');
                debugInfo.totalElements += elements.length;

                elements.forEach((element, index) => {
                    try {
                        // 檢查是否為按鈕
                        if (element.tagName.toLowerCase() === 'button') {
                            const classes = element.className || '';
                            const text = element.textContent.trim();

                            // 檢查是否為 ibon 購票按鈕
                            const isIbonButton = (
                                classes.includes('btn-buy') ||
                                classes.includes('btn-pink') ||
                                classes.includes('ng-tns-c57') ||
                                text.includes('線上購票') ||
                                text.includes('購票')
                            );

                            if (isIbonButton) {
                                console.log(`[JS SHADOW] ${indent}[SUCCESS] Found ibon button: "${text}" (classes: ${classes})`);
                                results.push({
                                    text: text,
                                    classes: classes,
                                    path: `${path}/button[${index}]`,
                                    method: 'javascript_shadow_enhanced',
                                    element: element,
                                    disabled: element.disabled
                                });
                                debugInfo.buttonsFound++;
                            }
                        }

                        // 檢查 Shadow DOM
                        if (element.shadowRoot) {
                            debugInfo.shadowElements++;
                            const shadowType = element.shadowRoot.mode || 'unknown';
                            console.log(`[JS SHADOW] ${indent}[FOUND] Found ${shadowType} shadow root in ${element.tagName}`);

                            // 遞歸搜尋 Shadow DOM
                            searchAllElements(element.shadowRoot, `${path}/${element.tagName.toLowerCase()}[shadow_${shadowType}]`, depth + 1);
                        }

                        // 嘗試訪問可能的 closed Shadow DOM
                        // 注意：這通常會失敗，但值得嘗試
                        try {
                            if (element.shadowRoot === null && element.attachShadow) {
                                // 可能有 closed Shadow DOM，但無法直接訪問
                                debugInfo.closedShadowElements++;
                                console.log(`[JS SHADOW] ${indent}[CLOSED] Potential closed shadow root in ${element.tagName}`);
                            }
                        } catch (e) {
                            // 忽略訪問錯誤
                        }

                    } catch (elementError) {
                        console.log(`[JS SHADOW] ${indent}[ERROR] Error processing element: ${elementError.message}`);
                    }
                });
            }

            // 從文檔根開始搜尋
            searchAllElements(document);

            console.log(`[JS SHADOW] Search completed:`, debugInfo);

            return {
                success: true,
                buttons: results,
                debugInfo: debugInfo
            };
        })();
        '''

        # 執行 JavaScript 搜尋
        search_result_raw = await tab.evaluate(shadow_search_js, return_by_value=True)

        # 解析 NoDriver 格式
        if isinstance(search_result_raw, dict):
            search_result = search_result_raw
        else:
            # 避免相對 import 錯誤，直接解析結果
            try:
                if hasattr(search_result_raw, '_asdict'):
                    search_result = search_result_raw._asdict()
                elif hasattr(search_result_raw, '__dict__'):
                    search_result = search_result_raw.__dict__
                else:
                    search_result = {}
            except:
                search_result = {}

        if show_debug_message:
            if isinstance(search_result, dict):
                debug_info = search_result.get('debugInfo', {})
                print(f"[JS SHADOW] Search stats:")
                print(f"  - Total elements: {debug_info.get('totalElements', 0)}")
                print(f"  - Shadow elements: {debug_info.get('shadowElements', 0)}")
                print(f"  - Closed shadow elements: {debug_info.get('closedShadowElements', 0)}")
                print(f"  - Buttons found: {debug_info.get('buttonsFound', 0)}")

        # 處理返回結果
        if isinstance(search_result, dict) and search_result.get('success'):
            buttons = search_result.get('buttons', [])
            if show_debug_message:
                print(f"[JS SHADOW] Found {len(buttons)} purchase buttons")
                for i, btn in enumerate(buttons):
                    print(f"[JS SHADOW] Button {i+1}: '{btn['text']}' at {btn['path']}")
            return buttons

        return []

    except Exception as e:
        if show_debug_message:
            print(f"[JS SHADOW] Enhanced JavaScript search failed: {e}")
        return []

async def extract_date_context_from_path(tab, button_node, path):
    """從按鈕節點的父層結構中提取日期資訊"""
    try:
        from nodriver import cdp

        # 獲取父節點
        parent = await tab.send(cdp.dom.describe_node(node_id=button_node.node_id))
        parent_id = getattr(parent.node, 'parent_id', None)

        if parent_id:
            # 搜尋父節點中的日期相關文字
            parent_html = await tab.send(cdp.dom.get_outer_html(node_id=parent_id))
            html_content = parent_html.outer_html

            # 日期正則表達式模式
            import re
            date_patterns = [
                r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2025/09/28
                r'(\d{1,2})/(\d{1,2})\s*\(\w+\)',  # 9/28 (日)
                r'(\d{4}-\d{1,2}-\d{1,2})',  # 2025-09-28
            ]

            for pattern in date_patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    return str(matches[0]) if isinstance(matches[0], tuple) else matches[0]

        return ""
    except:
        return ""

async def fallback_javascript_search(tab, show_debug_message):
    """增強的 JavaScript 回退搜尋方法"""
    js_search = '''
    (function() {
        const results = [];
        const debugInfo = {
            totalButtons: 0,
            shadowRootsFound: 0,
            appGameElements: 0,
            purchaseButtonCandidates: []
        };

        console.log("[FALLBACK] Starting enhanced JavaScript button search...");

        // 搜尋策略 1: 主 DOM 中的按鈕
        const mainButtons = document.querySelectorAll('button');
        debugInfo.totalButtons = mainButtons.length;
        console.log(`[FALLBACK] Found ${mainButtons.length} buttons in main DOM`);

        for (let btn of mainButtons) {
            const text = (btn.textContent || btn.innerText || '').trim();
            const classes = btn.className || '';
            const id = btn.id || '';

            // 記錄所有按鈕用於除錯
            debugInfo.purchaseButtonCandidates.push({
                text: text.substring(0, 50), // 限制長度
                classes: classes.substring(0, 100),
                id: id
            });

            if (text.includes('線上購票') || text.includes('購票') ||
                classes.includes('btn-buy') || classes.includes('btn-pink')) {

                // 嘗試獲取日期上下文
                let dateContext = '';
                try {
                    let parent = btn.parentElement;
                    for (let i = 0; i < 5 && parent; i++) {
                        const parentText = parent.textContent || '';
                        const dateMatch = parentText.match(/(\d{4}\/\d{1,2}\/\d{1,2}|\d{1,2}\/\d{1,2}\s*\(\w+\))/);
                        if (dateMatch) {
                            dateContext = dateMatch[0];
                            break;
                        }
                        parent = parent.parentElement;
                    }
                } catch(e) {}

                results.push({
                    text: text,
                    classes: classes,
                    disabled: btn.disabled,
                    method: 'javascript_main_dom',
                    date_context: dateContext
                });
                console.log(`[FALLBACK] Found purchase button in main DOM: "${text}"`);
            }
        }

        // 搜尋策略 2: Shadow DOM 穿透（包含 closed shadow root）
        const allElements = document.querySelectorAll('*');
        console.log(`[FALLBACK] Checking ${allElements.length} elements for shadow roots...`);

        for (let element of allElements) {
            if (element.shadowRoot) {
                debugInfo.shadowRootsFound++;
                console.log(`[FALLBACK] Found shadow root in ${element.tagName.toLowerCase()}`);

                try {
                    const shadowButtons = element.shadowRoot.querySelectorAll('button');
                    console.log(`[FALLBACK] Found ${shadowButtons.length} buttons in shadow root`);

                    for (let btn of shadowButtons) {
                        const text = (btn.textContent || btn.innerText || '').trim();
                        const classes = btn.className || '';

                        if (text.includes('線上購票') || text.includes('購票') ||
                            classes.includes('btn-buy') || classes.includes('btn-pink')) {

                            // 嘗試獲取日期上下文
                            let dateContext = '';
                            try {
                                let parent = btn.parentElement;
                                for (let i = 0; i < 5 && parent; i++) {
                                    const parentText = parent.textContent || '';
                                    const dateMatch = parentText.match(/(\d{4}\/\d{1,2}\/\d{1,2}|\d{1,2}\/\d{1,2}\s*\(\w+\))/);
                                    if (dateMatch) {
                                        dateContext = dateMatch[0];
                                        break;
                                    }
                                    parent = parent.parentElement;
                                }
                            } catch(e) {}

                            results.push({
                                text: text,
                                classes: classes,
                                disabled: btn.disabled,
                                method: 'javascript_shadow_dom',
                                date_context: dateContext
                            });
                            console.log(`[FALLBACK] Found purchase button in shadow DOM: "${text}"`);
                        }
                    }
                } catch (e) {
                    console.log(`[FALLBACK] Cannot access shadow root (closed): ${e.message}`);
                }
            }
        }

        // 搜尋策略 3: 特定 ibon 結構搜尋
        const appGameElements = document.querySelectorAll('app-game');
        debugInfo.appGameElements = appGameElements.length;
        console.log(`[FALLBACK] Found ${appGameElements.length} app-game elements`);

        for (let appGame of appGameElements) {
            // 檢查 innerHTML 是否包含購票按鈕的跡象
            const innerHTML = appGame.innerHTML;
            if (innerHTML.includes('btn-buy') || innerHTML.includes('線上購票') || innerHTML.includes('btn-pink')) {
                console.log(`[FALLBACK] app-game element contains purchase button patterns`);

                // 嘗試查找實際的按鈕元素（可能在 template 中）
                const templateContent = appGame.querySelector('template');
                if (templateContent && templateContent.content) {
                    const templateButtons = templateContent.content.querySelectorAll('button');
                    console.log(`[FALLBACK] Found ${templateButtons.length} buttons in template`);
                }
            }
        }

        console.log(`[FALLBACK] Search completed. Found ${results.length} purchase buttons`);
        console.log(`[FALLBACK] Debug info:`, debugInfo);

        return {
            results: results,
            debugInfo: debugInfo
        };
    })();
    '''

    search_result = await tab.evaluate(js_search) or {}

    if show_debug_message:
        if isinstance(search_result, dict) and 'debugInfo' in search_result:
            debug_info = search_result['debugInfo']
            print(f"JavaScript fallback search debug info:")
            print(f"  - Total buttons in main DOM: {debug_info.get('totalButtons', 0)}")
            print(f"  - Shadow roots found: {debug_info.get('shadowRootsFound', 0)}")
            print(f"  - app-game elements: {debug_info.get('appGameElements', 0)}")
            print(f"  - Button candidates (first 5):")
            for i, btn in enumerate(debug_info.get('purchaseButtonCandidates', [])[:5]):
                print(f"    {i+1}. Text: '{btn.get('text', '')}', Classes: '{btn.get('classes', '')}', ID: '{btn.get('id', '')}'")

    # 返回結果列表
    if isinstance(search_result, dict) and 'results' in search_result:
        return search_result['results']
    elif isinstance(search_result, list):
        return search_result
    else:
        return []

async def click_button_via_cdp(tab, target_button, show_debug_message):
    """使用 NoDriver CDP API 點擊按鈕（通過 node_id）"""
    try:
        from nodriver import cdp

        if show_debug_message:
            print(f"[CDP CLICK] Starting CDP click for: {target_button['text']}")
            print(f"[CDP CLICK] Node ID: {target_button.get('node_id')}")

        # 方法1: 使用 CDP DOM.scrollIntoViewIfNeeded + DOM.focus + Input.dispatchMouseEvent
        try:
            node_id = target_button.get('node_id')
            if not node_id:
                raise Exception("No node_id available")

            # 步驟1: 滾動到視窗內
            try:
                await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                if show_debug_message:
                    print(f"[CDP CLICK] Scrolled element into view")
            except Exception as e:
                if show_debug_message:
                    print(f"[CDP CLICK] Scroll failed (may not be needed): {e}")

            # 步驟2: 聚焦元素
            try:
                await tab.send(cdp.dom.focus(node_id=node_id))
                if show_debug_message:
                    print(f"[CDP CLICK] Focused element")
            except Exception as e:
                if show_debug_message:
                    print(f"[CDP CLICK] Focus failed: {e}")

            # 步驟3: 獲取元素的 box model (位置)
            try:
                box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
                if show_debug_message:
                    print(f"[CDP CLICK] Got box model")

                # 計算元素中心點
                # box_model is a GetBoxModelResult, which has 'model' attribute of type BoxModel
                # BoxModel has 'content' attribute which is a list of 8 numbers [x1,y1,x2,y2,x3,y3,x4,y4]
                content_quad = box_model.content if hasattr(box_model, 'content') else box_model.model.content
                x = (content_quad[0] + content_quad[2]) / 2
                y = (content_quad[1] + content_quad[5]) / 2

                if show_debug_message:
                    print(f"[CDP CLICK] Click position: ({x:.1f}, {y:.1f})")

                # 步驟4: 使用 NoDriver 內建的 mouse_click 方法
                await tab.mouse_click(x, y)

                if show_debug_message:
                    print(f"[CDP CLICK] Mouse click executed successfully")

                # 等待導航
                await tab.sleep(1.0)

                return {'success': True, 'buttonText': target_button.get('text', ''), 'method': 'cdp_mouse_event'}

            except Exception as box_error:
                if show_debug_message:
                    print(f"[CDP CLICK] Box model/mouse event failed: {box_error}")
                raise box_error

        except Exception as cdp_error:
            if show_debug_message:
                print(f"[CDP CLICK] CDP method failed: {cdp_error}")
            raise cdp_error

    except Exception as e:
        if show_debug_message:
            print(f"[CDP CLICK] All methods failed: {e}")
        return {'success': False, 'error': str(e)}

async def click_button_via_javascript_fallback(tab, target_button, show_debug_message):
    """使用純 JavaScript 立即點擊按鈕（回退方法）"""
    try:
        if show_debug_message:
            print(f"[JS FALLBACK] Starting JavaScript fallback click for: {target_button['text']}")

        # 使用純 JavaScript 搜尋並立即點擊，避免 NodeId 失效
        click_js = f'''
        (function() {{
            const targetText = "{target_button['text']}";
            const targetClasses = "{target_button.get('classes', '')}";

            console.log(`[JS IMMEDIATE] Searching for button: "${{targetText}}"`);

            function attemptButtonClick(button, source) {{
                console.log(`[JS IMMEDIATE] Attempting click from ${{source}}`);

                try {{
                    if (button.disabled) {{
                        console.log(`[JS IMMEDIATE] Button is disabled`);
                        return false;
                    }}

                    if (button.offsetParent === null) {{
                        console.log(`[JS IMMEDIATE] Button is not visible`);
                        return false;
                    }}

                    // 記錄點擊前的 URL
                    const beforeUrl = window.location.href;
                    console.log(`[JS IMMEDIATE] URL before click: ${{beforeUrl}}`);

                    // 滾動到按鈕位置
                    button.scrollIntoView({{ behavior: 'instant', block: 'center' }});

                    // 立即執行多種點擊方法
                    button.focus();
                    button.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
                    button.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
                    button.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
                    button.click();

                    // 嘗試觸發 form 提交
                    const form = button.closest('form');
                    if (form) {{
                        console.log(`[JS IMMEDIATE] Found parent form, attempting submit`);
                        form.submit();
                    }}

                    // 鍵盤事件
                    button.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
                    button.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', keyCode: 13, bubbles: true }}));

                    console.log(`[JS IMMEDIATE] ✅ Click executed from ${{source}}`);

                    // 立即檢查導航
                    setTimeout(() => {{
                        const afterUrl = window.location.href;
                        console.log(`[JS IMMEDIATE] URL after click: ${{afterUrl}}`);
                        if (beforeUrl !== afterUrl) {{
                            console.log(`[JS IMMEDIATE] ✅ Page navigation detected!`);
                        }}
                    }}, 50);

                    return true;

                }} catch (e) {{
                    console.log(`[JS IMMEDIATE] Click failed from ${{source}}: ${{e.message}}`);
                    return false;
                }}
            }}

            function findAndClickImmediately() {{
                let clickSuccess = false;
                const attempts = [];

                // 方法 1: 直接全面搜尋所有按鈕
                try {{
                    const allButtons = document.querySelectorAll('button');
                    console.log(`[JS IMMEDIATE] Found ${{allButtons.length}} total buttons`);
                    attempts.push(`found_${{allButtons.length}}_buttons_via_querySelector`);

                    for (let btn of allButtons) {{
                        const text = btn.textContent.trim();
                        const classes = btn.className || '';
                        if (text === targetText && classes.includes('btn-buy')) {{
                            console.log(`[JS IMMEDIATE] Found target via querySelector`);
                            attempts.push('found_target_via_querySelector');
                            if (attemptButtonClick(btn, 'querySelector')) {{
                                clickSuccess = true;
                                break;
                            }}
                        }}
                    }}
                }} catch (e) {{
                    console.log(`[JS IMMEDIATE] querySelector failed: ${{e.message}}`);
                    attempts.push(`querySelector_error: ${{e.message}}`);
                }}

                // 方法 2: TreeWalker 深度搜尋（如果第一種方法失敗）
                if (!clickSuccess) {{
                    try {{
                        console.log(`[JS IMMEDIATE] Trying TreeWalker method`);
                        const walker = document.createTreeWalker(
                            document.body || document.documentElement,
                            NodeFilter.SHOW_ELEMENT,
                            null,
                            false
                        );

                        let node;
                        while (node = walker.nextNode()) {{
                            if (node.tagName && node.tagName.toLowerCase() === 'button') {{
                                const text = node.textContent.trim();
                                const classes = node.className || '';
                                if (text === targetText && classes.includes('btn-buy')) {{
                                    console.log(`[JS IMMEDIATE] Found target via TreeWalker`);
                                    attempts.push('found_target_via_treewalker');
                                    if (attemptButtonClick(node, 'TreeWalker')) {{
                                        clickSuccess = true;
                                        break;
                                    }}
                                }}
                            }}

                            // 檢查 Shadow DOM
                            if (node.shadowRoot) {{
                                const shadowButtons = node.shadowRoot.querySelectorAll('button');
                                for (let shadowBtn of shadowButtons) {{
                                    const text = shadowBtn.textContent.trim();
                                    const classes = shadowBtn.className || '';
                                    if (text === targetText && classes.includes('btn-buy')) {{
                                        console.log(`[JS IMMEDIATE] Found target in shadow DOM of ${{node.tagName}}`);
                                        attempts.push(`found_target_in_shadow_${{node.tagName}}`);
                                        if (attemptButtonClick(shadowBtn, `shadow_${{node.tagName}}`)) {{
                                            clickSuccess = true;
                                            break;
                                        }}
                                    }}
                                }}
                                if (clickSuccess) break;
                            }}

                            // 特殊處理 app-game
                            if (node.tagName && node.tagName.toLowerCase() === 'app-game') {{
                                try {{
                                    const gameButtons = node.querySelectorAll('button');
                                    console.log(`[JS IMMEDIATE] Found ${{gameButtons.length}} buttons in app-game`);
                                    attempts.push(`found_${{gameButtons.length}}_buttons_in_app_game`);

                                    for (let gameBtn of gameButtons) {{
                                        const text = gameBtn.textContent.trim();
                                        const classes = gameBtn.className || '';
                                        if (text === targetText && classes.includes('btn-buy')) {{
                                            console.log(`[JS IMMEDIATE] Found target in app-game`);
                                            attempts.push('found_target_in_app_game');
                                            if (attemptButtonClick(gameBtn, 'app_game')) {{
                                                clickSuccess = true;
                                                break;
                                            }}
                                        }}
                                    }}
                                }} catch (e) {{
                                    console.log(`[JS IMMEDIATE] app-game access failed: ${{e.message}}`);
                                    attempts.push(`app_game_error: ${{e.message}}`);
                                }}
                                if (clickSuccess) break;
                            }}
                        }}
                    }} catch (e) {{
                        console.log(`[JS IMMEDIATE] TreeWalker failed: ${{e.message}}`);
                        attempts.push(`treewalker_error: ${{e.message}}`);
                    }}
                }}

                return {{
                    success: clickSuccess,
                    attempts: attempts
                }};
            }}

            // 執行搜尋和點擊
            const result = findAndClickImmediately();
            console.log(`[JS IMMEDIATE] Operation completed. Success: ${{result.success}}`);
            return result;
        }})();
        '''

        # 執行 JavaScript 點擊
        click_result = await tab.evaluate(click_js)

        if show_debug_message:
            if isinstance(click_result, dict):
                success = click_result.get('success', False)
                attempts = click_result.get('attempts', [])
                print(f"[JS IMMEDIATE] {'[SUCCESS]' if success else '[FAILED]'}")
                print(f"[JS IMMEDIATE] Attempts: {', '.join(attempts)}")
            else:
                print(f"[JS IMMEDIATE] Unexpected result: {click_result}")

        # 短暫等待讓頁面開始導航
        await tab.sleep(0.3)

        # 檢查最終 URL
        try:
            final_url = await tab.evaluate('window.location.href')
            if show_debug_message:
                print(f"[JS IMMEDIATE] Final URL: {final_url}")
        except:
            pass

        # 返回結果 - 修復資料結構處理
        if isinstance(click_result, dict) and click_result.get('success'):
            return {
                "success": True,
                "buttonText": target_button['text'],
                "method": "javascript_immediate",
                "attempts": click_result.get('attempts', [])
            }
        else:
            # 安全處理非 dict 類型的 click_result
            error_attempts = []
            if isinstance(click_result, dict):
                error_attempts = click_result.get('attempts', [])
            elif isinstance(click_result, list):
                # 嘗試從 list 結構中提取 attempts
                try:
                    for item in click_result:
                        if isinstance(item, list) and len(item) == 2 and item[0] == 'attempts':
                            attempts_data = item[1]
                            if isinstance(attempts_data, dict) and 'value' in attempts_data:
                                attempt_values = attempts_data['value']
                                if isinstance(attempt_values, list):
                                    error_attempts = [
                                        attempt.get('value', str(attempt)) if isinstance(attempt, dict) else str(attempt)
                                        for attempt in attempt_values
                                    ]
                                break
                except Exception:
                    pass

            return {
                "success": False,
                "error": "JavaScript immediate click failed",
                "attempts": error_attempts
            }

    except Exception as e:
        if show_debug_message:
            print(f"[JS IMMEDIATE] Exception: {e}")
        return {"success": False, "error": str(e)}

async def click_button_via_enhanced_javascript(tab, target_button, show_debug_message):
    """使用增強的 JavaScript 方法點擊按鈕（專為 Shadow DOM 設計）"""
    try:
        if show_debug_message:
            print(f"[JS CLICK] Attempting enhanced JavaScript click for: {target_button['text']}")

        # 使用 TreeWalker 的增強 JavaScript 在 Shadow DOM 中尋找並點擊按鈕
        click_js = f'''
        (function() {{
            const targetText = "{target_button['text']}";
            const targetClasses = "{target_button['classes']}";

            console.log(`[TreeWalker] Starting enhanced search for button: "${{targetText}}"`);

            // 使用 TreeWalker 進行更深層的 DOM 遍歷（包括 closed Shadow DOM）
            function findButtonWithTreeWalker() {{
                // 創建一個接受所有節點的 NodeFilter
                const walker = document.createTreeWalker(
                    document.body || document.documentElement,
                    NodeFilter.SHOW_ELEMENT,
                    {{
                        acceptNode: function(node) {{
                            return NodeFilter.FILTER_ACCEPT;
                        }}
                    }},
                    false
                );

                let currentNode;
                const foundButtons = [];

                // 遍歷所有節點
                while (currentNode = walker.nextNode()) {{
                    // 檢查當前節點是否為按鈕
                    if (currentNode.tagName && currentNode.tagName.toLowerCase() === 'button') {{
                        const text = currentNode.textContent.trim();
                        const classes = currentNode.className || '';

                        if (text === targetText && classes.includes('btn-buy')) {{
                            foundButtons.push(currentNode);
                            console.log(`[TreeWalker] Found target button: "${{text}}" with classes: "${{classes}}"`);
                        }}
                    }}

                    // 檢查是否有 Shadow DOM（包括 closed）
                    if (currentNode.shadowRoot) {{
                        console.log(`[TreeWalker] Found open shadow DOM in ${{currentNode.tagName}}`);
                        const shadowButtons = findButtonsInShadowDOM(currentNode.shadowRoot);
                        foundButtons.push(...shadowButtons);
                    }}

                    // 嘗試訪問 closed Shadow DOM（使用反射技術）
                    try {{
                        const shadowHost = currentNode;
                        // 檢查是否有 closed shadow DOM（通過檢查特定特徵）
                        if (shadowHost.tagName && shadowHost.tagName.toLowerCase() === 'app-game') {{
                            console.log(`[TreeWalker] Attempting to access closed shadow DOM in app-game`);
                            // 使用瀏覽器內建的方法直接查找按鈕
                            const directButtons = shadowHost.querySelectorAll('button');
                            if (directButtons.length > 0) {{
                                console.log(`[TreeWalker] Found ${{directButtons.length}} buttons via direct query`);
                                for (let btn of directButtons) {{
                                    const text = btn.textContent.trim();
                                    const classes = btn.className || '';
                                    if (text === targetText && classes.includes('btn-buy')) {{
                                        foundButtons.push(btn);
                                        console.log(`[TreeWalker] Found target in closed shadow: "${{text}}"`);
                                    }}
                                }}
                            }}
                        }}
                    }} catch (e) {{
                        // Closed shadow DOM 可能無法直接訪問
                    }}
                }}

                return foundButtons;
            }}

            // 在 Shadow DOM 中搜尋按鈕
            function findButtonsInShadowDOM(shadowRoot) {{
                const buttons = [];
                const walker = document.createTreeWalker(
                    shadowRoot,
                    NodeFilter.SHOW_ELEMENT,
                    {{
                        acceptNode: function(node) {{
                            return NodeFilter.FILTER_ACCEPT;
                        }}
                    }},
                    false
                );

                let currentNode;
                while (currentNode = walker.nextNode()) {{
                    if (currentNode.tagName && currentNode.tagName.toLowerCase() === 'button') {{
                        const text = currentNode.textContent.trim();
                        const classes = currentNode.className || '';

                        if (text === targetText && classes.includes('btn-buy')) {{
                            buttons.push(currentNode);
                            console.log(`[TreeWalker] Found target in shadow DOM: "${{text}}"`);
                        }}
                    }}

                    // 遞歸處理嵌套的 Shadow DOM
                    if (currentNode.shadowRoot) {{
                        const nestedButtons = findButtonsInShadowDOM(currentNode.shadowRoot);
                        buttons.push(...nestedButtons);
                    }}
                }}

                return buttons;
            }}

            // 進行多種點擊嘗試
            function attemptClick(button) {{
                console.log(`[TreeWalker] Attempting to click button...`);

                // 方法 1: 標準點擊事件
                try {{
                    button.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                    // 創建多種事件類型
                    const events = [
                        new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}),
                        new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}),
                        new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}),
                        new Event('change', {{ bubbles: true, cancelable: true }}),
                        new Event('input', {{ bubbles: true, cancelable: true }})
                    ];

                    // 依序觸發事件
                    events.forEach(event => {{
                        button.dispatchEvent(event);
                        console.log(`[TreeWalker] Dispatched ${{event.type}} event`);
                    }});

                    // 方法 2: 直接調用 click()
                    button.click();
                    console.log(`[TreeWalker] Called button.click()`);

                    // 方法 3: 觸發 form 提交（如果按鈕在 form 中）
                    const form = button.closest('form');
                    if (form) {{
                        console.log(`[TreeWalker] Found parent form, attempting submit`);
                        form.submit();
                    }}

                    // 方法 4: 模擬鍵盤 Enter
                    button.focus();
                    const enterEvent = new KeyboardEvent('keypress', {{
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        cancelable: true
                    }});
                    button.dispatchEvent(enterEvent);
                    console.log(`[TreeWalker] Dispatched Enter keypress`);

                    return true;
                }} catch (e) {{
                    console.log(`[TreeWalker] Click attempt failed: ${{e.message}}`);
                    return false;
                }}
            }}

            // 執行搜尋和點擊
            const buttons = findButtonWithTreeWalker();

            if (buttons.length === 0) {{
                console.log(`[TreeWalker] No matching buttons found`);
                return {{ success: false, error: "No matching buttons found" }};
            }}

            console.log(`[TreeWalker] Found ${{buttons.length}} matching button(s)`);

            // 嘗試點擊找到的按鈕
            for (let i = 0; i < buttons.length; i++) {{
                const button = buttons[i];
                console.log(`[TreeWalker] Attempting to click button ${{i + 1}}/${{buttons.length}}`);

                if (!button.disabled && button.offsetParent !== null) {{
                    const clickSuccess = attemptClick(button);
                    if (clickSuccess) {{
                        console.log(`[TreeWalker] ✅ Successfully clicked button ${{i + 1}}`);

                        // 等待一小段時間檢查頁面是否開始導航
                        setTimeout(() => {{
                            console.log(`[TreeWalker] Current URL after click: ${{window.location.href}}`);
                        }}, 500);

                        return {{
                            success: true,
                            buttonText: targetText,
                            clickedIndex: i,
                            totalFound: buttons.length
                        }};
                    }}
                }} else {{
                    console.log(`[TreeWalker] Button ${{i + 1}} not clickable (disabled: ${{button.disabled}}, visible: ${{button.offsetParent !== null}})`);
                }}
            }}

            return {{ success: false, error: "All click attempts failed" }};
        }})();
        '''

        click_result = await tab.evaluate(click_js)

        if show_debug_message:
            if isinstance(click_result, dict):
                if isinstance(click_result, dict) and click_result.get('success'):
                    print(f"[JS CLICK] [SUCCESS] Enhanced JavaScript click succeeded: {click_result.get('buttonText', '')}")
                else:
                    print(f"[JS CLICK] [ERROR] Enhanced JavaScript click failed: {click_result.get('error', 'Unknown error')}")
            else:
                print(f"[JS CLICK] Unexpected result type: {type(click_result)}")

        # 返回統一格式的結果
        if isinstance(click_result, dict) and click_result.get('success'):
            return {
                "success": True,
                "buttonText": click_result.get('buttonText', target_button['text']),
                "method": "enhanced_javascript"
            }
        else:
            error_msg = click_result.get('error', 'Unknown error') if isinstance(click_result, dict) else 'Unexpected result'
            return {"success": False, "error": error_msg}

    except Exception as e:
        if show_debug_message:
            print(f"CDP click failed: {e}")
        return {"success": False, "error": str(e)}

async def click_button_via_javascript(tab, target_button, show_debug_message):
    """使用 JavaScript 方法點擊按鈕（回退方法）"""
    click_js = f'''
    (function() {{
        try {{
            const targetText = "{target_button['text']}";
            const targetClasses = "{target_button.get('classes', '')}";
            let targetBtn = null;

            // 搜尋主 DOM
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {{
                const text = (btn.textContent || btn.innerText || '').trim();
                const classes = btn.className || '';

                if (text === targetText && classes.includes(targetClasses.split(' ')[0])) {{
                    targetBtn = btn;
                    break;
                }}
            }}

            // 搜尋 Shadow DOM
            if (!targetBtn) {{
                const allElements = document.querySelectorAll('*');
                for (let element of allElements) {{
                    if (element.shadowRoot) {{
                        try {{
                            const shadowButtons = element.shadowRoot.querySelectorAll('button');
                            for (let btn of shadowButtons) {{
                                const text = (btn.textContent || btn.innerText || '').trim();
                                const classes = btn.className || '';

                                if (text === targetText && classes.includes(targetClasses.split(' ')[0])) {{
                                    targetBtn = btn;
                                    break;
                                }}
                            }}
                            if (targetBtn) break;
                        }} catch (e) {{}}
                    }}
                }}
            }}

            if (targetBtn && !targetBtn.disabled) {{
                targetBtn.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                const clickEvent = new MouseEvent('click', {{
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    detail: 1
                }});

                targetBtn.dispatchEvent(clickEvent);
                targetBtn.click();

                return {{ success: true, clicked: true, buttonText: targetBtn.textContent.trim() }};
            }} else {{
                return {{ success: false, error: 'Button not found or disabled' }};
            }}
        }} catch (e) {{
            return {{ success: false, error: e.message }};
        }}
    }})();
    '''

    return await tab.evaluate(click_js)

async def check_ibon_login_status(tab, config_dict):
    """
    檢查 ibon 登入狀態並處理頁面重新載入
    基於原本成功版本的經驗：cookie 設置後需要重新載入頁面
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    if show_debug_message:
        print("Checking ibon login status and handling page reload...")

    try:
        # 檢查當前 URL
        current_url = await tab.evaluate('window.location.href')
        if show_debug_message:
            print(f"Current URL: {current_url}")

        # 檢查登入狀態的指標
        login_check_js = '''
        (function() {
            const result = {
                isLoggedIn: false,
                hasLoginElements: false,
                hasCookieData: false,
                needsReload: false,
                cookieLength: 0,
                cookieCount: 0
            };

            // 獲取所有 cookie 資訊（僅統計，不輸出內容）
            const cookies = document.cookie;
            result.cookieLength = cookies.length;
            result.cookieCount = cookies.split(';').filter(c => c.trim()).length;

            // Only output statistics, not actual cookie content for security
            console.log(`[COOKIE CHECK] Cookie count: ${result.cookieCount}, total length: ${cookies.length}`);

            // 更詳細的 cookie 檢查
            const hasMemId = cookies.includes('mem_id');
            const hasHuiwanTK = cookies.includes('huiwanTK');
            const hasMemEmail = cookies.includes('mem_email');
            const hasIbonVerify = cookies.includes('ibonqwareverify');

            console.log(`[COOKIE CHECK] Has mem_id: ${hasMemId}`);
            console.log(`[COOKIE CHECK] Has huiwanTK: ${hasHuiwanTK}`);
            console.log(`[COOKIE CHECK] Has mem_email: ${hasMemEmail}`);
            console.log(`[COOKIE CHECK] Has ibonqwareverify: ${hasIbonVerify}`);

            // 任何一個關鍵 cookie 存在就認為有登入資料
            result.hasCookieData = hasMemId || hasHuiwanTK || hasMemEmail || hasIbonVerify;

            // 檢查是否有登入相關元素
            const loginElements = document.querySelectorAll('a[href*="login"], .member, [class*="login"]');
            result.hasLoginElements = loginElements.length > 0;

            // 檢查頁面是否已完全載入 Angular 應用
            const appGameElements = document.querySelectorAll('app-game');
            const hasAngularApp = appGameElements.length > 0;

            console.log(`[COOKIE CHECK] Found ${appGameElements.length} app-game elements`);

            // 檢查是否有購票按鈕（包括 Shadow DOM 中的）
            let hasPurchaseButton = false;
            let totalButtons = 0;

            // 先檢查主 DOM 中的按鈕
            const mainButtons = document.querySelectorAll('button');
            totalButtons = mainButtons.length;

            console.log(`[COOKIE CHECK] Found ${mainButtons.length} buttons in main DOM`);

            for (let btn of mainButtons) {
                const text = (btn.textContent || '').trim();
                const classes = btn.className || '';
                console.log(`[COOKIE CHECK] Button: "${text}" with classes: "${classes}"`);

                if (text.includes('線上購票') || text.includes('購票') ||
                    classes.includes('btn-buy') || classes.includes('btn-pink')) {
                    hasPurchaseButton = true;
                    console.log(`[COOKIE CHECK] Found purchase button in main DOM: "${text}"`);
                    break;
                }
            }

            // 如果主 DOM 沒有找到，檢查 app-game 中的按鈕（可能在 Shadow DOM 中）
            if (!hasPurchaseButton && hasAngularApp) {
                console.log(`[COOKIE CHECK] Checking app-game elements for purchase buttons...`);
                for (let appGame of appGameElements) {
                    try {
                        // 嘗試直接查詢（某些情況下可以訪問 closed shadow DOM）
                        const gameButtons = appGame.querySelectorAll('button');
                        console.log(`[COOKIE CHECK] Found ${gameButtons.length} buttons in app-game`);

                        for (let gameBtn of gameButtons) {
                            const text = (gameBtn.textContent || '').trim();
                            const classes = gameBtn.className || '';
                            console.log(`[COOKIE CHECK] App-game button: "${text}" with classes: "${classes}"`);

                            if (text.includes('線上購票') || text.includes('購票') ||
                                classes.includes('btn-buy') || classes.includes('btn-pink')) {
                                hasPurchaseButton = true;
                                console.log(`[COOKIE CHECK] Found purchase button in app-game: "${text}"`);
                                break;
                            }
                        }
                        if (hasPurchaseButton) break;
                    } catch (e) {
                        console.log(`[COOKIE CHECK] Could not access app-game shadow DOM: ${e.message}`);
                    }
                }
            }

            // 判斷登入狀態
            console.log(`[COOKIE CHECK] Has cookie data: ${result.hasCookieData}`);
            console.log(`[COOKIE CHECK] Has purchase button: ${hasPurchaseButton}`);
            console.log(`[COOKIE CHECK] Has Angular app: ${hasAngularApp}`);

            if (result.hasCookieData) {
                result.isLoggedIn = true;

                // 改進重新載入邏輯：
                // 如果有 cookie 但沒有 Angular 應用和購票按鈕，可能需要重新載入
                if (!hasAngularApp && !hasPurchaseButton && totalButtons === 0) {
                    console.log(`[COOKIE CHECK] Page seems not loaded properly, may need reload`);
                    result.needsReload = true;
                } else {
                    console.log(`[COOKIE CHECK] Page seems loaded properly, no reload needed`);
                    result.needsReload = false;
                }
            } else {
                console.log(`[COOKIE CHECK] No valid cookie data found`);
                result.isLoggedIn = false;
                result.needsReload = false;
            }

            console.log(`[COOKIE CHECK] Final result - logged in: ${result.isLoggedIn}, needs reload: ${result.needsReload}`);

            return {
                ...result,
                hasAngularApp: hasAngularApp,
                hasPurchaseButton: hasPurchaseButton,
                totalButtons: totalButtons,
                angularElements: appGameElements.length
            };
        })();
        '''

        login_status_raw = await tab.evaluate(login_check_js, return_by_value=True)

        if show_debug_message:
            print(f"Login status check result:")
            print(f"  - Result type: {type(login_status_raw)}")
            print(f"  - Result content: {login_status_raw}")

        # 解析返回的結果（處理 nodriver 的特殊格式）
        if isinstance(login_status_raw, dict):
            login_status = login_status_raw
        else:
            # 使用 util 函數解析 NoDriver 格式
            from . import util
            login_status = util.parse_nodriver_result(login_status_raw) if login_status_raw else {
                'isLoggedIn': False,
                'hasCookieData': False,
                'needsReload': False,
                'error': f'Parse failed for type: {type(login_status_raw)}'
            }

        if show_debug_message and isinstance(login_status, dict):
            print(f"  - Is logged in: {login_status.get('isLoggedIn', False)}")
            print(f"  - Has cookie data: {login_status.get('hasCookieData', False)}")
            print(f"  - Has Angular app: {login_status.get('hasAngularApp', False)}")
            print(f"  - Has purchase button: {login_status.get('hasPurchaseButton', False)}")
            print(f"  - Total buttons: {login_status.get('totalButtons', 0)}")
            print(f"  - Needs reload: {login_status.get('needsReload', False)}")

        # 如果需要重新載入頁面（有 cookie 但沒有購票按鈕）
        if login_status.get('needsReload', False):
            if show_debug_message:
                print("Reloading page to apply ibon cookie...")

            # 重新載入頁面
            await tab.reload()

            # 等待頁面完全載入
            await tab.sleep(3.0)

            # 再次檢查
            final_status_raw = await tab.evaluate(login_check_js)

            # 處理返回結果的格式轉換
            final_status = {}
            if isinstance(final_status_raw, dict):
                final_status = final_status_raw
            elif isinstance(final_status_raw, list):
                # 處理 nodriver 特殊的嵌套陣列格式
                for item in final_status_raw:
                    if isinstance(item, list) and len(item) == 2:
                        key = item[0]
                        value_obj = item[1]
                        if isinstance(value_obj, dict) and 'value' in value_obj:
                            final_status[key] = value_obj['value']
                        else:
                            final_status[key] = value_obj
            else:
                final_status = {
                    'hasPurchaseButton': False,
                    'totalButtons': 0,
                    'error': f'Unexpected final result type: {type(final_status_raw)}'
                }

            if show_debug_message:
                print(f"After reload - Has purchase button: {final_status.get('hasPurchaseButton', False)}")
                print(f"After reload - Total buttons: {final_status.get('totalButtons', 0)}")

            return final_status

        return login_status

    except Exception as e:
        if show_debug_message:
            print(f"Error checking ibon login status: {e}")
        return {
            'isLoggedIn': False,
            'hasCookieData': False,
            'needsReload': False,
            'error': str(e)
        }

async def nodriver_ibon_ticket_agree(tab):
    for i in range(3):
        is_finish_checkbox_click = await nodriver_check_checkbox(tab, '#agreen:not(:checked)')
        if is_finish_checkbox_click:
            break

async def nodriver_ibon_allow_not_adjacent_seat(tab, config_dict):
    """
    Check and click the 'allow non-adjacent seats' checkbox on ibon

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if checkbox was clicked successfully, False otherwise
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    is_finish_checkbox_click = False

    # Selector for non-adjacent seat checkbox
    checkbox_selector = 'div.not-consecutive > div.custom-control > span > input[type="checkbox"]:not(:checked)'

    try:
        for i in range(3):
            is_finish_checkbox_click = await nodriver_check_checkbox(tab, checkbox_selector)
            if is_finish_checkbox_click:
                if show_debug_message:
                    print("[IBON] Non-adjacent seat checkbox clicked")
                break
    except Exception as e:
        if show_debug_message:
            print(f"[IBON] Non-adjacent seat checkbox error: {e}")

    return is_finish_checkbox_click

async def nodriver_ibon_event_area_auto_select(tab, config_dict, area_keyword_item=""):
    """
    ibon seat area auto-selection for NEW Event page format (NoDriver version)

    Handles seat area selection on /Event/{id}/{id} page (Angular SPA).
    Uses DOMSnapshot for data extraction and CDP for clicking.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        area_keyword_item: Area keyword string (space-separated for AND logic)

    Returns:
        tuple: (is_need_refresh, is_price_assign_by_bot)
            - is_need_refresh: Whether page refresh is needed
            - is_price_assign_by_bot: Whether area selection succeeded
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    ticket_number = config_dict["ticket_number"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    if show_debug_message:
        print("[ibon] 區域選擇開始")
        # print(f"關鍵字: {area_keyword_item}")
        # print(f"模式: {auto_select_mode}")
        # print(f"票數: {ticket_number}")

    # Wait for Angular app to fully load
    try:
        import random
        wait_time = random.uniform(0.8, 1.2)
        # if show_debug_message:
        #     print(f"[ibon] 等待 Angular 載入 {wait_time:.2f}s...")
        await tab.sleep(wait_time)
        await tab.sleep(1.5)
    except:
        pass

    # Phase 1: Extract all area data using DOMSnapshot (to pierce Shadow DOM if present)
    try:
        from nodriver import cdp

        # if show_debug_message:
        #     # print("[ibon] 擷取頁面結構...")

        # Use DOMSnapshot to get flattened page structure
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_paint_order=True,
            include_dom_rects=True
        ))

        areas_data = []

        if documents and len(documents) > 0:
            document_snapshot = documents[0]

            # Extract node information
            node_names = []
            node_values = []
            parent_indices = []
            attributes_list = []
            backend_node_ids = []

            if hasattr(document_snapshot, 'nodes'):
                nodes = document_snapshot.nodes
                if hasattr(nodes, 'node_name'):
                    node_names = [strings[i] if isinstance(i, int) and i < len(strings) else str(i)
                                 for i in nodes.node_name]
                if hasattr(nodes, 'node_value'):
                    node_values = [strings[i] if isinstance(i, int) and i >= 0 and i < len(strings) else ''
                                  for i in nodes.node_value]
                if hasattr(nodes, 'parent_index'):
                    parent_indices = list(nodes.parent_index)
                if hasattr(nodes, 'attributes'):
                    attributes_list = nodes.attributes
                if hasattr(nodes, 'backend_node_id'):
                    backend_node_ids = list(nodes.backend_node_id)

            # if show_debug_message:
            #     # print(f"[ibon] 提取 {len(node_names)} 節點")

            # Build children map for traversal
            children_map = {}
            for i, parent_idx in enumerate(parent_indices):
                if parent_idx >= 0:
                    if parent_idx not in children_map:
                        children_map[parent_idx] = []
                    children_map[parent_idx].append(i)

            # Helper function to get attributes as dict
            def get_attributes_dict(node_index):
                attrs = {}
                if node_index < len(attributes_list):
                    attr_indices = attributes_list[node_index]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key_idx = attr_indices[j]
                            val_idx = attr_indices[j + 1]
                            key = strings[key_idx] if key_idx < len(strings) else ''
                            val = strings[val_idx] if val_idx < len(strings) else ''
                            attrs[key] = val
                return attrs

            # Helper function to get all text content from node and its children
            def get_text_content(node_index, depth=0, max_depth=10):
                if depth > max_depth or node_index >= len(node_names):
                    return ''

                text_parts = []

                # If this is a text node, get its value
                if node_names[node_index] == '#text' and node_index < len(node_values):
                    text_parts.append(node_values[node_index])

                # Recursively get text from children
                if node_index in children_map:
                    for child_idx in children_map[node_index]:
                        child_text = get_text_content(child_idx, depth + 1, max_depth)
                        if child_text:
                            text_parts.append(child_text)

                return ' '.join(text_parts).strip()

            # Find all TR elements in the table
            tr_indices = []
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'TR':
                    tr_indices.append(i)

            # if show_debug_message:
            #     # print(f"[ibon] 找到 {len(tr_indices)} TR 元素")

            # Extract data from each TR
            area_index = 0
            for tr_idx in tr_indices:
                # Get TR attributes
                tr_attrs = get_attributes_dict(tr_idx)
                tr_class = tr_attrs.get('class', '')

                # Skip header rows (thead)
                if 'thead' in tr_class.lower() or not tr_class:
                    continue

                is_disabled = 'disabled' in tr_class.lower()

                # Find TD children
                td_indices = []
                if tr_idx in children_map:
                    for child_idx in children_map[tr_idx]:
                        if node_names[child_idx].upper() == 'TD':
                            td_indices.append(child_idx)

                # Extract text from each TD
                # Expected order: [0]=color, [1]=area_name, [2]=price, [3]=seat_status
                td_texts = []
                for td_idx in td_indices:
                    td_text = get_text_content(td_idx)
                    td_texts.append(td_text)

                if len(td_texts) >= 4:
                    area_name = td_texts[1].strip()
                    price = td_texts[2].strip()
                    seat_text = td_texts[3].strip()

                    # Get backend_node_id for this TR
                    tr_backend_node_id = None
                    if tr_idx < len(backend_node_ids):
                        tr_backend_node_id = backend_node_ids[tr_idx]

                    # Build area data object
                    area_data = {
                        'index': area_index,
                        'disabled': is_disabled,
                        'areaName': area_name,
                        'price': price,
                        'seatText': seat_text,
                        'innerHTML': f'<tr class="{tr_class}"><td>{area_name}</td><td>{price}</td><td>{seat_text}</td></tr>',
                        'tr_node_index': tr_idx,
                        'backend_node_id': tr_backend_node_id
                    }
                    areas_data.append(area_data)
                    area_index += 1

        # if show_debug_message:
        #     # print(f"[ibon] 找到 {len(areas_data)} 個區域")

    except Exception as exc:
        if show_debug_message:
            print(f"[NEW EVENT ERROR] Failed to extract area data: {exc}")
            import traceback
            traceback.print_exc()
        return True, False

    if not areas_data or len(areas_data) == 0:
        if show_debug_message:
            print("[ibon] 頁面無區域")
        return True, False

    # Phase 2: Filter areas (disabled, sold out, insufficient seats)
    valid_areas = []

    for area in areas_data:
        # Skip disabled areas
        if area['disabled']:
            if show_debug_message:
                print(f"[ibon] 跳過: {area['areaName']}")
            continue

        # 同時檢查區域名稱與內容
        row_text = area['areaName'] + ' ' + util.remove_html_tags(area['innerHTML'])

        # Skip sold out areas
        if '已售完' in area['seatText']:
            if show_debug_message:
                print(f"[ibon] 已售完: {area['areaName']}")
            continue

        # Check exclude keywords
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            if show_debug_message:
                print(f"[ibon] 排除: {area['areaName']}")
            continue

        # Check remaining seat count
        seat_text = area['seatText']
        if seat_text.isdigit():
            remaining_seats = int(seat_text)
            if remaining_seats < ticket_number:
                if show_debug_message:
                    print(f"[ibon] 座位不足: {area['areaName']} ({remaining_seats}/{ticket_number})")
                continue

        valid_areas.append(area)

    if show_debug_message:
        print(f"[ibon] 有效區域: {len(valid_areas)}")

    # Phase 3: Keyword matching (AND logic with space separation)
    matched_areas = []

    if area_keyword_item and len(area_keyword_item) > 0:
        area_keyword_array = area_keyword_item.split(' ')
        area_keyword_array = [util.format_keyword_string(kw) for kw in area_keyword_array if kw.strip()]

        if show_debug_message:
            print(f"[ibon] 關鍵字: {area_keyword_array}")

        for area in valid_areas:
            # 同時檢查區域名稱與內容
            row_text = area['areaName'] + ' ' + util.remove_html_tags(area['innerHTML'])
            row_text = util.format_keyword_string(row_text)

            # Check if all keywords match (AND logic)
            is_match = all(kw in row_text for kw in area_keyword_array)

            if is_match:
                matched_areas.append(area)
                if show_debug_message:
                    print(f"[ibon] 符合: {area['areaName']} ({area['price']})")

                # Stop at first match if mode is "from top to bottom"
                if auto_select_mode == util.CONST_FROM_TOP_TO_BOTTOM:
                    break
    else:
        # No keyword specified, accept all valid areas
        matched_areas = valid_areas
        # if show_debug_message:
        #     # print("[ibon] 無關鍵字,所有區域皆可選")

    if show_debug_message:
        print(f"[ibon] 符合關鍵字: {len(matched_areas)}")

    # Check if refresh is needed
    if len(matched_areas) == 0:
        is_need_refresh = True
        if show_debug_message:
            print("[ibon] 無符合區域")
        return is_need_refresh, False

    # Phase 4: Select target area based on mode
    target_area = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)

    if not target_area:
        is_need_refresh = True
        if show_debug_message:
            print("[ibon] 選擇失敗")
        return is_need_refresh, False

    if show_debug_message:
        print(f"[ibon] 已選: {target_area['areaName']}")

    # Phase 5: Click target area using CDP
    try:
        from nodriver import cdp

        if show_debug_message:
            print(f"[NEW EVENT CDP CLICK] Starting CDP click for area: {target_area['areaName']}")

        backend_node_id = target_area.get('backend_node_id')

        if not backend_node_id:
            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] No backend_node_id available for TR")
            return is_need_refresh, is_price_assign_by_bot

        # Request document first
        try:
            document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Requested document with pierce=True")
        except Exception as doc_exc:
            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Document request failed: {doc_exc}")
            return is_need_refresh, is_price_assign_by_bot

        # Convert backend_node_id to node_id
        try:
            result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(backend_node_ids=[backend_node_id]))
            node_ids = result if isinstance(result, list) else (result.node_ids if hasattr(result, 'node_ids') else [])

            if not node_ids or len(node_ids) == 0:
                if show_debug_message:
                    print(f"[NEW EVENT CDP CLICK] Failed to convert backend_node_id to node_id")
                return is_need_refresh, is_price_assign_by_bot

            node_id = node_ids[0]

            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Node ID: {node_id}")

            # Scroll into view
            try:
                await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                if show_debug_message:
                    print(f"[NEW EVENT CDP CLICK] Scrolled element into view")
            except Exception as e:
                if show_debug_message:
                    print(f"[NEW EVENT CDP CLICK] Scroll warning: {e}")

            # Focus element
            try:
                await tab.send(cdp.dom.focus(node_id=node_id))
                if show_debug_message:
                    print(f"[NEW EVENT CDP CLICK] Focused element")
            except Exception as e:
                if show_debug_message:
                    print(f"[NEW EVENT CDP CLICK] Focus warning: {e}")

            # Get box model
            box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Got box model")

            # Calculate center point
            content_quad = box_model.content if hasattr(box_model, 'content') else box_model.model.content
            x = (content_quad[0] + content_quad[2]) / 2
            y = (content_quad[1] + content_quad[5]) / 2

            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Click position: ({x:.1f}, {y:.1f})")

            # Execute mouse click
            await tab.mouse_click(x, y)

            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Mouse click executed successfully")

            # Wait for navigation
            await tab.sleep(1.5)

            is_price_assign_by_bot = True

            if show_debug_message:
                print(f"[NEW EVENT SUCCESS] Clicked area: {target_area['areaName']}")

        except Exception as resolve_exc:
            if show_debug_message:
                print(f"[NEW EVENT CDP CLICK] Resolve/click failed: {resolve_exc}")
                import traceback
                traceback.print_exc()

    except Exception as exc:
        if show_debug_message:
            print(f"[NEW EVENT ERROR] Exception during click: {exc}")
            import traceback
            traceback.print_exc()

    return is_need_refresh, is_price_assign_by_bot

async def nodriver_ibon_area_auto_select(tab, config_dict, area_keyword_item=""):
    """
    ibon seat area auto-selection (NoDriver version)

    Handles seat area selection on UTK0201_000.aspx page after date selection.
    Uses JavaScript for data extraction and CDP for clicking.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        area_keyword_item: Area keyword string (space-separated for AND logic)

    Returns:
        tuple: (is_need_refresh, is_price_assign_by_bot)
            - is_need_refresh: Whether page refresh is needed
            - is_price_assign_by_bot: Whether area selection succeeded
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    ticket_number = config_dict["ticket_number"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    if show_debug_message:
        print("NoDriver ibon_area_auto_select started")
        print(f"area_keyword_item: {area_keyword_item}")
        print(f"auto_select_mode: {auto_select_mode}")
        print(f"ticket_number: {ticket_number}")

    # Wait for Shadow DOM to fully load
    try:
        import random
        wait_time = random.uniform(0.8, 1.2)
        if show_debug_message:
            print(f"Waiting {wait_time:.2f} seconds for page to fully load...")
        await tab.sleep(wait_time)
        await tab.sleep(1.5)  # Additional wait for Shadow DOM
    except:
        pass

    # Phase 1: Extract all area data using DOMSnapshot (to pierce closed Shadow DOM)
    try:
        from nodriver import cdp

        if show_debug_message:
            print("[DOMSNAPSHOT] Capturing page structure for area extraction...")

        # Use DOMSnapshot to get flattened page structure (pierces Shadow DOM)
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_paint_order=True,
            include_dom_rects=True
        ))

        areas_data = []

        if documents and len(documents) > 0:
            document_snapshot = documents[0]

            # Extract node information
            node_names = []
            node_values = []
            parent_indices = []
            attributes_list = []
            backend_node_ids = []

            if hasattr(document_snapshot, 'nodes'):
                nodes = document_snapshot.nodes
                if hasattr(nodes, 'node_name'):
                    node_names = [strings[i] if isinstance(i, int) and i < len(strings) else str(i)
                                 for i in nodes.node_name]
                if hasattr(nodes, 'node_value'):
                    node_values = [strings[i] if isinstance(i, int) and i >= 0 and i < len(strings) else ''
                                  for i in nodes.node_value]
                if hasattr(nodes, 'parent_index'):
                    parent_indices = list(nodes.parent_index)
                if hasattr(nodes, 'attributes'):
                    attributes_list = nodes.attributes
                if hasattr(nodes, 'backend_node_id'):
                    backend_node_ids = list(nodes.backend_node_id)

            if show_debug_message:
                print(f"[DOMSNAPSHOT] Extracted {len(node_names)} nodes, {len(strings)} strings")

            # Debug: Check layout structure
            if show_debug_message and hasattr(document_snapshot, 'layout'):
                layout = document_snapshot.layout
                has_node_index = hasattr(layout, 'node_index')
                has_bounds = hasattr(layout, 'bounds')
                print(f"[DOMSNAPSHOT] Layout available: node_index={has_node_index}, bounds={has_bounds}")
                if has_node_index:
                    node_index_count = len(list(layout.node_index)) if layout.node_index else 0
                    print(f"[DOMSNAPSHOT] Layout node_index count: {node_index_count}")
                    # Show first few node indices for debugging
                    node_indices = list(layout.node_index)
                    print(f"[DOMSNAPSHOT] First 10 layout node indices: {node_indices[:10]}")
                if has_bounds:
                    bounds_count = len(list(layout.bounds)) if layout.bounds else 0
                    bounds_per_rect = bounds_count // node_index_count if node_index_count > 0 else 0
                    print(f"[DOMSNAPSHOT] Layout bounds count: {bounds_count}, nodes: {node_index_count}, bounds/node: {bounds_per_rect}")

            # Build children map for traversal
            children_map = {}
            for i, parent_idx in enumerate(parent_indices):
                if parent_idx >= 0:
                    if parent_idx not in children_map:
                        children_map[parent_idx] = []
                    children_map[parent_idx].append(i)

            # Helper function to get attributes as dict
            def get_attributes_dict(node_index):
                attrs = {}
                if node_index < len(attributes_list):
                    attr_indices = attributes_list[node_index]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key_idx = attr_indices[j]
                            val_idx = attr_indices[j + 1]
                            key = strings[key_idx] if key_idx < len(strings) else ''
                            val = strings[val_idx] if val_idx < len(strings) else ''
                            attrs[key] = val
                return attrs

            # Helper function to get all text content from node and its children
            def get_text_content(node_index, depth=0, max_depth=10):
                if depth > max_depth or node_index >= len(node_names):
                    return ''

                text_parts = []

                # If this is a text node, get its value
                if node_names[node_index] == '#text' and node_index < len(node_values):
                    text_parts.append(node_values[node_index])

                # Recursively get text from children
                if node_index in children_map:
                    for child_idx in children_map[node_index]:
                        child_text = get_text_content(child_idx, depth + 1, max_depth)
                        if child_text:
                            text_parts.append(child_text)

                return ' '.join(text_parts).strip()

            # Find all TR elements in the table
            tr_indices = []
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'TR':
                    # Check if it's inside a table (basic check)
                    tr_indices.append(i)

            if show_debug_message:
                print(f"[DOMSNAPSHOT] Found {len(tr_indices)} TR elements")

            # Extract data from each TR
            area_index = 0
            for tr_idx in tr_indices:
                # Get TR attributes
                tr_attrs = get_attributes_dict(tr_idx)
                tr_id = tr_attrs.get('id', '')
                tr_class = tr_attrs.get('class', '')

                # Skip header rows (thead)
                if not tr_id:
                    continue

                is_disabled = 'disabled' in tr_class.lower()

                # Find TD children
                td_indices = []
                if tr_idx in children_map:
                    for child_idx in children_map[tr_idx]:
                        if node_names[child_idx].upper() == 'TD':
                            td_indices.append(child_idx)

                # Extract text from each TD
                # Expected order: [0]=color, [1]=area_name, [2]=price, [3]=seat_status
                td_texts = []
                for td_idx in td_indices:
                    td_text = get_text_content(td_idx)
                    td_texts.append(td_text)

                if len(td_texts) >= 4:
                    area_name = td_texts[1].strip()
                    price = td_texts[2].strip()
                    seat_text = td_texts[3].strip()

                    # Get layout information (bounding box) for this TR
                    layout_rect = None
                    if hasattr(document_snapshot, 'layout'):
                        layout = document_snapshot.layout
                        if hasattr(layout, 'node_index') and hasattr(layout, 'bounds'):
                            # Find this TR's layout index
                            node_indices = list(layout.node_index)
                            bounds_list = list(layout.bounds)

                            if tr_idx in node_indices:
                                layout_idx = node_indices.index(tr_idx)
                                # bounds is an array of Rectangle objects: [x_rect, y_rect, width_rect, height_rect, ...]
                                bounds_idx = layout_idx * 4
                                if bounds_idx + 3 < len(bounds_list):
                                    # Each bound is a Rectangle object, extract the first value
                                    x_rect = bounds_list[bounds_idx]
                                    y_rect = bounds_list[bounds_idx + 1]
                                    width_rect = bounds_list[bounds_idx + 2]
                                    height_rect = bounds_list[bounds_idx + 3]

                                    # Rectangle objects contain an array, get the first value
                                    x = x_rect[0] if hasattr(x_rect, '__getitem__') else float(x_rect)
                                    y = y_rect[0] if hasattr(y_rect, '__getitem__') else float(y_rect)
                                    width = width_rect[0] if hasattr(width_rect, '__getitem__') else float(width_rect)
                                    height = height_rect[0] if hasattr(height_rect, '__getitem__') else float(height_rect)

                                    layout_rect = {'x': x, 'y': y, 'width': width, 'height': height}
                                    if show_debug_message and area_index < 3:  # Only show first 3 for debugging
                                        print(f"[DOMSNAPSHOT] TR #{area_index} (node {tr_idx}): layout_idx={layout_idx}, rect={layout_rect}")
                            else:
                                if show_debug_message and area_index < 3:
                                    print(f"[DOMSNAPSHOT] TR #{area_index} (node {tr_idx}): NOT in layout.node_index")

                    # Get backend_node_id for this TR
                    tr_backend_node_id = None
                    if tr_idx < len(backend_node_ids):
                        tr_backend_node_id = backend_node_ids[tr_idx]

                    # Build area data object (matching JavaScript version format)
                    area_data = {
                        'index': area_index,
                        'id': tr_id,
                        'disabled': is_disabled,
                        'areaName': area_name,
                        'price': price,
                        'seatText': seat_text,
                        'innerHTML': f'<tr id="{tr_id}" class="{tr_class}">...mock...</tr>',  # Mock HTML for compatibility
                        'tr_node_index': tr_idx,  # Store for reference
                        'layout_rect': layout_rect,  # Store bounding box for clicking
                        'backend_node_id': tr_backend_node_id  # Store for CDP node resolution
                    }
                    areas_data.append(area_data)
                    area_index += 1

        if show_debug_message:
            print(f"[AREA EXTRACT] Found {len(areas_data)} total areas")

    except Exception as exc:
        if show_debug_message:
            print(f"[ERROR] Failed to extract area data: {exc}")
            import traceback
            traceback.print_exc()
        return True, False

    if not areas_data or len(areas_data) == 0:
        if show_debug_message:
            print("[AREA EXTRACT] No areas found on page")
        return True, False

    # Phase 2: Filter areas (disabled, sold out, insufficient seats)
    valid_areas = []

    for area in areas_data:
        # Skip disabled areas
        if area['disabled']:
            if show_debug_message:
                print(f"[ibon] 跳過: {area['areaName']}")
            continue

        # 同時檢查區域名稱與內容
        row_text = area['areaName'] + ' ' + util.remove_html_tags(area['innerHTML'])

        # Skip sold out areas
        if '已售完' in area['seatText']:
            if show_debug_message:
                print(f"[ibon] 已售完: {area['areaName']}")
            continue

        if 'disabled' in area['innerHTML'].lower() or 'sold-out' in area['innerHTML'].lower():
            if show_debug_message:
                print(f"[ibon] 跳過: {area['areaName']}")
            continue

        # Skip description rows (not actual seat areas)
        if row_text in ["座位已被選擇", "座位已售出", "舞台區域"]:
            continue

        # Check exclude keywords
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            if show_debug_message:
                print(f"[ibon] 排除: {area['areaName']}")
            continue

        # Check remaining seat count
        seat_text = area['seatText']
        if seat_text.isdigit():
            remaining_seats = int(seat_text)
            if remaining_seats < ticket_number:
                if show_debug_message:
                    print(f"[ibon] 座位不足: {area['areaName']} ({remaining_seats}/{ticket_number})")
                continue

        valid_areas.append(area)

    if show_debug_message:
        print(f"[ibon] 有效區域: {len(valid_areas)}")

    # Phase 3: Keyword matching (AND logic with space separation)
    matched_areas = []

    if area_keyword_item and len(area_keyword_item) > 0:
        area_keyword_array = area_keyword_item.split(' ')
        area_keyword_array = [util.format_keyword_string(kw) for kw in area_keyword_array if kw.strip()]

        if show_debug_message:
            print(f"[ibon] 關鍵字: {area_keyword_array}")

        for area in valid_areas:
            # 同時檢查區域名稱與內容
            row_text = area['areaName'] + ' ' + util.remove_html_tags(area['innerHTML'])
            row_text = util.format_keyword_string(row_text)

            # Check if all keywords match (AND logic)
            is_match = all(kw in row_text for kw in area_keyword_array)

            if is_match:
                matched_areas.append(area)
                if show_debug_message:
                    print(f"[ibon] 符合: {area['areaName']} ({area['price']})")

                # Stop at first match if mode is "from top to bottom"
                if auto_select_mode == util.CONST_FROM_TOP_TO_BOTTOM:
                    break
    else:
        # No keyword specified, accept all valid areas
        matched_areas = valid_areas
        # if show_debug_message:
        #     # print("[ibon] 無關鍵字,所有區域皆可選")

    if show_debug_message:
        print(f"[ibon] 符合關鍵字: {len(matched_areas)}")

    # Check if refresh is needed
    if len(matched_areas) == 0:
        is_need_refresh = True
        if show_debug_message:
            print("[RESULT] No matched areas found, refresh needed")
        return is_need_refresh, False

    # Phase 4: Select target area based on mode
    target_area = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)

    if not target_area:
        is_need_refresh = True
        if show_debug_message:
            print("[RESULT] Failed to select target area, refresh needed")
        return is_need_refresh, False

    if show_debug_message:
        print(f"[TARGET] Selected area: {target_area['areaName']} (index: {target_area['index']}, id: {target_area['id']})")

    # Phase 5: Click target area using CDP real-time coordinates
    try:
        from nodriver import cdp

        if show_debug_message:
            print(f"[CDP CLICK] Starting CDP click for area: {target_area['areaName']}")
            print(f"[CDP CLICK] TR ID: {target_area['id']}, backend_node_id: {target_area.get('backend_node_id')}")

        # Get backend_node_id from target area
        backend_node_id = target_area.get('backend_node_id')

        if not backend_node_id:
            if show_debug_message:
                print(f"[CDP CLICK] No backend_node_id available for TR")
        else:
            # Request document first (required for pushNodesByBackendIdsToFrontend)
            try:
                document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
                if show_debug_message:
                    print(f"[CDP CLICK] Requested document with pierce=True")
            except Exception as doc_exc:
                if show_debug_message:
                    print(f"[CDP CLICK] Document request failed: {doc_exc}")
                return is_need_refresh, is_price_assign_by_bot

            # Convert backend_node_id to node_id using pushNodesByBackendIdsToFrontend
            try:
                result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(backend_node_ids=[backend_node_id]))
                node_ids = result if isinstance(result, list) else (result.node_ids if hasattr(result, 'node_ids') else [])

                if not node_ids or len(node_ids) == 0:
                    if show_debug_message:
                        print(f"[CDP CLICK] Failed to convert backend_node_id to node_id")
                    return is_need_refresh, is_price_assign_by_bot

                node_id = node_ids[0]

                if show_debug_message:
                    print(f"[CDP CLICK] Converted backend_node_id to node_id: {node_id}")

                # Scroll into view
                try:
                    await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                    if show_debug_message:
                        print(f"[CDP CLICK] Scrolled element into view")
                except Exception as e:
                    if show_debug_message:
                        print(f"[CDP CLICK] Scroll warning: {e}")

                # Focus element
                try:
                    await tab.send(cdp.dom.focus(node_id=node_id))
                    if show_debug_message:
                        print(f"[CDP CLICK] Focused element")
                except Exception as e:
                    if show_debug_message:
                        print(f"[CDP CLICK] Focus warning: {e}")

                # Get real-time box model (current coordinates)
                box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
                if show_debug_message:
                    print(f"[CDP CLICK] Got box model")

                # Calculate center point
                content_quad = box_model.content if hasattr(box_model, 'content') else box_model.model.content
                x = (content_quad[0] + content_quad[2]) / 2
                y = (content_quad[1] + content_quad[5]) / 2

                if show_debug_message:
                    print(f"[CDP CLICK] Click position: ({x:.1f}, {y:.1f})")

                # Execute mouse click
                await tab.mouse_click(x, y)

                if show_debug_message:
                    print(f"[CDP CLICK] Mouse click executed successfully")

                # Wait for navigation
                await tab.sleep(1.5)

                is_price_assign_by_bot = True

                if show_debug_message:
                    print(f"[CLICK SUCCESS] Clicked area: {target_area['areaName']} (id: {target_area['id']})")

            except Exception as resolve_exc:
                if show_debug_message:
                    print(f"[CDP CLICK] Resolve/click failed: {resolve_exc}")
                    import traceback
                    traceback.print_exc()

    except Exception as exc:
        if show_debug_message:
            print(f"[CLICK ERROR] Exception during click: {exc}")
            import traceback
            traceback.print_exc()

    return is_need_refresh, is_price_assign_by_bot

async def nodriver_ibon_ticket_number_auto_select(tab, config_dict):
    """
    ibon ticket number auto-selection using NoDriver CDP
    Finds the first ticket quantity SELECT element and sets the desired quantity
    Returns: is_ticket_number_assigned (bool)
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    ticket_number = str(config_dict.get("ticket_number", 2))

    if show_debug_message:
        print(f"NoDriver ibon_ticket_number_auto_select started")
        print(f"ticket_number: {ticket_number}")

    is_ticket_number_assigned = False

    try:
        # Use JavaScript to find first ticket quantity SELECT and set value
        result = await tab.evaluate(f'''
            (function() {{
                // Try new EventBuy format first: table.rwdtable select.form-control-sm
                let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');

                // Fallback to old .aspx format: table.table select[name*="AMOUNT_DDL"]
                if (selects.length === 0) {{
                    selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
                }}

                if (selects.length === 0) {{
                    return {{success: false, error: "No ticket SELECT found"}};
                }}

                // Use first SELECT (usually full-price ticket)
                const select = selects[0];

                // Check current selected value
                const currentValue = select.value;

                if (currentValue !== "0" && currentValue !== "") {{
                    return {{success: true, already_assigned: true, current: currentValue}};
                }}

                // Check if target quantity option exists
                const targetOption = Array.from(select.options).find(opt => opt.value === "{ticket_number}");

                if (!targetOption) {{
                    // Target quantity not available, try setting to 1
                    const option1 = Array.from(select.options).find(opt => opt.value === "1");
                    if (option1) {{
                        select.value = "1";
                        select.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return {{success: true, set_value: "1", fallback: true}};
                    }}
                    return {{success: false, error: "Target option not found"}};
                }}

                // Set target quantity
                select.value = "{ticket_number}";
                select.dispatchEvent(new Event('change', {{bubbles: true}}));

                return {{success: true, set_value: "{ticket_number}"}};
            }})();
        ''')

        # Parse result
        result_parsed = util.parse_nodriver_result(result)

        if show_debug_message:
            print(f"Ticket number selection result: {result_parsed}")

        if isinstance(result_parsed, dict):
            if result_parsed.get('success'):
                is_ticket_number_assigned = True
                if result_parsed.get('already_assigned'):
                    if show_debug_message:
                        print(f"[TICKET] Already assigned: {result_parsed.get('current')}")
                elif result_parsed.get('fallback'):
                    if show_debug_message:
                        print(f"[TICKET] Fallback to 1 (target {ticket_number} not available)")
                else:
                    if show_debug_message:
                        print(f"[TICKET] Set to: {result_parsed.get('set_value')}")
            else:
                if show_debug_message:
                    print(f"[TICKET] Failed: {result_parsed.get('error')}")

    except Exception as exc:
        if show_debug_message:
            print(f"[TICKET ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return is_ticket_number_assigned

async def nodriver_ibon_get_captcha_image_from_shadow_dom(tab, config_dict):
    """
    Use DOMSnapshot to find captcha image inside Shadow DOM and get base64 data
    Returns: img_base64 (bytes) or None
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    # Wait for page to stabilize before capturing
    import random
    await asyncio.sleep(random.uniform(0.8, 1.2))

    img_base64 = None

    try:
        # Get DOMSnapshot with Shadow DOM content
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_dom_rects=True,
            include_paint_order=False
        ))

        # Find IMG element with captcha - get both URL and backend_node_id in one pass
        target_img_url = None
        img_backend_node_id = None

        for doc in documents:
            node_names = [strings[i] for i in doc.nodes.node_name]

            for idx, node_name in enumerate(node_names):
                if node_name.lower() == 'img':
                    if doc.nodes.attributes and idx < len(doc.nodes.attributes):
                        attrs = doc.nodes.attributes[idx]
                        attr_dict = {}
                        for i in range(0, len(attrs), 2):
                            if i + 1 < len(attrs):
                                attr_name = strings[attrs[i]]
                                attr_value = strings[attrs[i + 1]]
                                attr_dict[attr_name] = attr_value

                        if '/pic.aspx?TYPE=' in attr_dict.get('src', ''):
                            target_img_url = attr_dict.get('src', '')
                            if hasattr(doc.nodes, 'backend_node_id') and idx < len(doc.nodes.backend_node_id):
                                img_backend_node_id = doc.nodes.backend_node_id[idx]

                            if show_debug_message:
                                print(f"[CAPTCHA] Found captcha IMG: {target_img_url}")
                                print(f"[CAPTCHA] Backend node ID: {img_backend_node_id}")
                            break

            if img_backend_node_id:
                break

        if not img_backend_node_id:
            # Try finding CANVAS element (new EventBuy format)
            if show_debug_message:
                print("[CAPTCHA] IMG not found, searching for CANVAS element...")
            
            for doc in documents:
                node_names = [strings[i] for i in doc.nodes.node_name]
                
                for idx, node_name in enumerate(node_names):
                    if node_name.lower() == 'canvas':
                        # Found CANVAS element, use it for captcha
                        if hasattr(doc.nodes, 'backend_node_id') and idx < len(doc.nodes.backend_node_id):
                            img_backend_node_id = doc.nodes.backend_node_id[idx]
                            
                            if show_debug_message:
                                print(f"[CAPTCHA] Found captcha CANVAS element")
                                print(f"[CAPTCHA] Backend node ID: {img_backend_node_id}")
                            break
                
                if img_backend_node_id:
                    break
        
        if not img_backend_node_id:
            if show_debug_message:
                print("[CAPTCHA] Neither IMG nor CANVAS found")
            return None


        # Make URL absolute if needed
        if target_img_url and target_img_url.startswith('/'):
            current_url = tab.target.url
            domain = '/'.join(current_url.split('/')[:3])
            target_img_url = domain + target_img_url

        # Use CDP DOM API to get IMG element position and screenshot
        try:

            if img_backend_node_id:
                # Initialize DOM document first (required after page reload)
                try:
                    await tab.send(cdp.dom.get_document())
                except:
                    pass  # Document may already be initialized

                # Convert backend_node_id to node_id using DOM.pushNodesByBackendIdsToFrontend
                try:
                    result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([img_backend_node_id]))
                    if result and len(result) > 0:
                        img_node_id = result[0]
                        if show_debug_message:
                            print(f"[CAPTCHA] Converted to node_id: {img_node_id}")

                        # Scroll element into view first to ensure it's rendered
                        try:
                            await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=img_node_id))
                            await asyncio.sleep(0.1)
                        except:
                            pass  # Element may already be visible

                        # Get box model for the IMG element
                        box_model = await tab.send(cdp.dom.get_box_model(node_id=img_node_id))

                        if box_model and hasattr(box_model, 'content'):
                            # content quad: [x1,y1, x2,y2, x3,y3, x4,y4]
                            quad = box_model.content
                            x = min(quad[0], quad[2], quad[4], quad[6])
                            y = min(quad[1], quad[3], quad[5], quad[7])
                            width = max(quad[0], quad[2], quad[4], quad[6]) - x
                            height = max(quad[1], quad[3], quad[5], quad[7]) - y

                            if show_debug_message:
                                print(f"[CAPTCHA] IMG box: x={x}, y={y}, w={width}, h={height}")

                            # Get device pixel ratio
                            device_pixel_ratio = await tab.evaluate('window.devicePixelRatio')

                            # WORKAROUND: Full page screenshot + PIL crop
                            # Region screenshot doesn't work with closed Shadow DOM
                            full_screenshot = await tab.send(cdp.page.capture_screenshot(format_='png'))

                            if full_screenshot:
                                import base64
                                from PIL import Image
                                import io

                                # Decode full screenshot
                                full_img_bytes = base64.b64decode(full_screenshot)
                                full_img = Image.open(io.BytesIO(full_img_bytes))

                                if show_debug_message:
                                    print(f"[CAPTCHA] Full screenshot: {full_img.size}")

                                # Crop using PIL (coordinates need to account for device pixel ratio)
                                left = int(x * device_pixel_ratio)
                                top = int(y * device_pixel_ratio)
                                right = int((x + width) * device_pixel_ratio)
                                bottom = int((y + height) * device_pixel_ratio)

                                cropped_img = full_img.crop((left, top, right, bottom))

                                if show_debug_message:
                                    print(f"[CAPTCHA] Cropped: {cropped_img.size}, crop box: ({left}, {top}, {right}, {bottom})")

                                # Convert back to bytes
                                img_buffer = io.BytesIO()
                                cropped_img.save(img_buffer, format='PNG')
                                img_base64 = img_buffer.getvalue()

                                if show_debug_message:
                                    print(f"[CAPTCHA] Screenshot: {len(img_base64)} bytes")

                                # Save for debugging (only in verbose mode)
                                # if show_debug_message:
                                    # try:
                                        # import os
                                        # from datetime import datetime
                                        # temp_dir = os.path.join(os.path.dirname(__file__), '.temp')
                                        # os.makedirs(temp_dir, exist_ok=True)
                                        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                        # img_path = os.path.join(temp_dir, f'captcha_{timestamp}.png')
                                        # with open(img_path, 'wb') as f:
                                            # f.write(img_base64)
                                        # print(f"[CAPTCHA] Saved: {img_path}")
                                    # except:
                                        # pass
                        else:
                            if show_debug_message:
                                print("[CAPTCHA] Failed to get box model")
                    else:
                        if show_debug_message:
                            print("[CAPTCHA] Failed to convert backend_node_id")
                except Exception as dom_exc:
                    if show_debug_message:
                        print(f"[CAPTCHA] DOM API error: {dom_exc}")
            else:
                if show_debug_message:
                    print("[CAPTCHA] No backend_node_id found for IMG")

        except Exception as exc:
            if show_debug_message:
                print(f"[CAPTCHA] Screenshot failed: {exc}")
                import traceback
                traceback.print_exc()

    except Exception as exc:
        if show_debug_message:
            print(f"[CAPTCHA ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return img_base64

async def nodriver_ibon_keyin_captcha_code(tab, answer="", auto_submit=False, config_dict=None):
    """
    ibon captcha input handling
    Returns: (is_verifyCode_editing, is_form_submitted)
    """
    show_debug_message = config_dict["advanced"].get("verbose", False) if config_dict else False

    is_verifyCode_editing = False
    is_form_submitted = False

    if show_debug_message:
        print(f"[CAPTCHA INPUT] answer: {answer}, auto_submit: {auto_submit}")

    try:
        # Find captcha input box
        # Selector 1: input[value="驗證碼"]
        # Selector 2: #ctl00_ContentPlaceHolder1_CHK
        form_verifyCode = None

        try:
            form_verifyCode = await tab.query_selector('input[placeholder*="驗證碼"]')
        except:
            pass

        if not form_verifyCode:
            try:
                form_verifyCode = await tab.query_selector('input[value="驗證碼"]')
            except:
                pass

        if not form_verifyCode:
            try:
                form_verifyCode = await tab.query_selector('#ctl00_ContentPlaceHolder1_CHK')
            except:
                pass

        if not form_verifyCode:
            if show_debug_message:
                print("[CAPTCHA INPUT] Input box not found")
            return is_verifyCode_editing, is_form_submitted

        # Check if input box is visible
        is_visible = False
        try:
            is_visible = await tab.evaluate('''
                (function() {
                    const selectors = [
                        'input[placeholder*="驗證碼"]',
                        'input[value="驗證碼"]',
                        '#ctl00_ContentPlaceHolder1_CHK'
                    ];
                    for (let selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && !element.disabled && element.offsetParent !== null) {
                            return true;
                        }
                    }
                    return false;
                })();
            ''')
        except:
            pass

        if not is_visible:
            if show_debug_message:
                print("[CAPTCHA INPUT] Input box not visible")
            return is_verifyCode_editing, is_form_submitted

        # If no answer provided, check if already has value for manual input mode
        if not answer:
            # Get current input value
            inputed_value = ""
            try:
                inputed_value = await form_verifyCode.apply('function (element) { return element.value; }') or ""
            except:
                pass

            # If already has value, skip (user manually inputed)
            if inputed_value and inputed_value != "驗證碼":
                if show_debug_message:
                    print(f"[CAPTCHA INPUT] Already has value: {inputed_value}")
                is_verifyCode_editing = True
                return is_verifyCode_editing, is_form_submitted

            # Focus for manual input
            try:
                await form_verifyCode.click()
                is_verifyCode_editing = True
                if show_debug_message:
                    print("[CAPTCHA INPUT] Focused for manual input")
            except:
                pass
            return is_verifyCode_editing, is_form_submitted

        # Fill in answer
        try:
            await form_verifyCode.click()

            # Clear placeholder value
            await form_verifyCode.apply('function (element) { element.value = ""; }')

            # Type answer
            await form_verifyCode.send_keys(answer)

            if show_debug_message:
                print(f"[CAPTCHA INPUT] Filled answer: {answer}")

            # Auto submit if enabled
            if auto_submit:
                # Check if ticket number is selected
                ticket_ok = await tab.evaluate('''
                    (function() {
                        // Try new EventBuy format first: table.rwdtable select.form-control-sm
                        let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
                        // Fallback to old .aspx format: table.table select[name*="AMOUNT_DDL"]
                        if (selects.length === 0) {
                            selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
                        }
                        if (selects.length === 0) return false;
                        const select = selects[0];
                        return select.value !== "0" && select.value !== "";
                    })();
                ''')

                if ticket_ok:
                    # Set up alert handler BEFORE clicking submit button
                    alert_handled = False

                    async def handle_submit_dialog(event):
                        nonlocal alert_handled
                        alert_handled = True
                        if show_debug_message:
                            print(f"[CAPTCHA INPUT] Alert detected: '{event.message}'")
                        # Auto-dismiss alert
                        try:
                            await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                            if show_debug_message:
                                print(f"[CAPTCHA INPUT] Alert dismissed")
                        except Exception as dismiss_exc:
                            if show_debug_message:
                                print(f"[CAPTCHA INPUT] Failed to dismiss alert: {dismiss_exc}")

                    # Register alert handler
                    try:
                        tab.add_handler(cdp.page.JavascriptDialogOpening, handle_submit_dialog)
                        if show_debug_message:
                            print(f"[CAPTCHA INPUT] Alert handler registered before submit")
                    except Exception as handler_exc:
                        if show_debug_message:
                            print(f"[CAPTCHA INPUT] Failed to register alert handler: {handler_exc}")

                    # Find and click submit button
                    # Button ID from HTML: ctl00_ContentPlaceHolder1_A2
                    # CRITICAL: iBon requires calling ImageCode_Verify2() before submit
                    submit_clicked = await tab.evaluate('''
                        (function() {
                            const submitBtn = document.querySelector('#ctl00_ContentPlaceHolder1_A2');
                            if (!submitBtn || submitBtn.disabled) {
                                return false;
                            }

                            // Call iBon's frontend verification function if it exists
                            if (typeof ImageCode_Verify2 === 'function') {
                                try {
                                    ImageCode_Verify2();
                                } catch (e) {
                                    console.log('[CAPTCHA] ImageCode_Verify2 failed:', e);
                                }
                            } else if (typeof ImageCode_Verify === 'function') {
                                try {
                                    ImageCode_Verify();
                                } catch (e) {
                                    console.log('[CAPTCHA] ImageCode_Verify failed:', e);
                                }
                            }

                            submitBtn.click();
                            return true;
                        })();
                    ''')

                    if submit_clicked:
                        is_form_submitted = True
                        if show_debug_message:
                            print("[CAPTCHA INPUT] Form submitted")

                        # Wait for potential alert to appear and be handled
                        await asyncio.sleep(0.8)

                        if show_debug_message:
                            if alert_handled:
                                print(f"[CAPTCHA INPUT] Alert was handled during wait")
                            else:
                                print(f"[CAPTCHA INPUT] No alert appeared (captcha may be correct)")
                    else:
                        if show_debug_message:
                            print("[CAPTCHA INPUT] Submit button not found or disabled")

                    # Remove alert handler
                    try:
                        tab.remove_handler(cdp.page.JavascriptDialogOpening, handle_submit_dialog)
                    except:
                        pass
                else:
                    if show_debug_message:
                        print("[CAPTCHA INPUT] Ticket number not selected, skip submit")

        except Exception as exc:
            if show_debug_message:
                print(f"[CAPTCHA INPUT ERROR] {exc}")

    except Exception as exc:
        if show_debug_message:
            print(f"[CAPTCHA INPUT ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return is_verifyCode_editing, is_form_submitted

async def nodriver_ibon_refresh_captcha(tab, config_dict):
    """
    Refresh ibon captcha image by calling JavaScript refreshCaptcha() function
    Returns: success (bool)
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    if show_debug_message:
        print("[CAPTCHA REFRESH] Refreshing captcha")

    ret = False
    try:
        # Call JavaScript refreshCaptcha() function
        result = await tab.evaluate('''
            (function() {
                if (typeof refreshCaptcha === 'function') {
                    refreshCaptcha();
                    return true;
                }
                return false;
            })();
        ''')

        ret = result if result else False

        if show_debug_message:
            print(f"[CAPTCHA REFRESH] Result: {ret}")

    except Exception as exc:
        if show_debug_message:
            print(f"[CAPTCHA REFRESH ERROR] {exc}")

    return ret

async def nodriver_ibon_auto_ocr(tab, config_dict, ocr, away_from_keyboard_enable, previous_answer):
    """
    ibon OCR auto recognition logic
    Returns: (is_need_redo_ocr, previous_answer, is_form_submitted)
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    is_need_redo_ocr = False
    is_form_submitted = False

    # Check if input box exists
    is_input_box_exist = False
    try:
        input_box = await tab.query_selector('input[placeholder*="驗證碼"], input[value="驗證碼"], #ctl00_ContentPlaceHolder1_CHK')
        is_input_box_exist = input_box is not None
    except:
        pass

    if not is_input_box_exist:
        if show_debug_message:
            print("[CAPTCHA OCR] Captcha input box not found")
        return is_need_redo_ocr, previous_answer, is_form_submitted

    if not ocr:
        if show_debug_message:
            print("[CAPTCHA OCR] OCR module not available")
        return is_need_redo_ocr, previous_answer, is_form_submitted

    # iBon clears ticket number after captcha error - reselect if needed
    ticket_ok = await tab.evaluate('''
        (function() {
            // Try new EventBuy format first: table.rwdtable select.form-control-sm
            let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
            // Fallback to old .aspx format: table.table select[name*="AMOUNT_DDL"]
            if (selects.length === 0) {
                selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
            }
            if (selects.length === 0) return false;
            const select = selects[0];
            return select.value !== "0" && select.value !== "";
        })();
    ''')

    if not ticket_ok:
        await nodriver_ibon_ticket_number_auto_select(tab, config_dict)
        await asyncio.sleep(0.3)

    # Get captcha image and do OCR
    ocr_start_time = time.time()

    img_base64 = await nodriver_ibon_get_captcha_image_from_shadow_dom(tab, config_dict)

    ocr_answer = None
    if img_base64:
        try:
            # Use global OCR instance (beta=True works best for iBon - 91.3% accuracy in tests)
            # Preprocessing actually reduces accuracy (73.9% vs 91.3%)
            ocr_answer = ocr.classification(img_base64)

            if show_debug_message:
                print(f"[CAPTCHA OCR] Using global OCR (beta=True), raw result: {ocr_answer}")

            # Filter to digits only (iBon captchas are 4 digits)
            if ocr_answer:
                filtered = ''.join(filter(str.isdigit, ocr_answer))
                if filtered != ocr_answer and show_debug_message:
                    print(f"[CAPTCHA OCR] Filtered '{ocr_answer}' -> '{filtered}'")
                ocr_answer = filtered
        except Exception as exc:
            if show_debug_message:
                print(f"[CAPTCHA OCR] OCR classification failed: {exc}")

    ocr_done_time = time.time()
    ocr_elapsed_time = ocr_done_time - ocr_start_time

    if show_debug_message:
        print(f"[CAPTCHA OCR] Processing time: {ocr_elapsed_time:.3f}s")

    # Process OCR result
    if ocr_answer is None:
        if away_from_keyboard_enable:
            # Page not ready, retry
            is_need_redo_ocr = True
            await asyncio.sleep(0.1)
        else:
            # Manual mode
            await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
    else:
        ocr_answer = ocr_answer.strip()
        if show_debug_message:
            print(f"[CAPTCHA OCR] Result: {ocr_answer}")

        if len(ocr_answer) == 4:
            # Valid 4-digit answer
            current_url_before_submit, _ = await nodriver_current_url(tab)
            who_care_var, is_form_submitted = await nodriver_ibon_keyin_captcha_code(
                tab, answer=ocr_answer, auto_submit=away_from_keyboard_enable, config_dict=config_dict
            )

            # Check if captcha was correct by verifying URL change
            if is_form_submitted and away_from_keyboard_enable:
                # Alert is already handled inside nodriver_ibon_keyin_captcha_code()
                # Just check URL change to determine if captcha was correct
                if show_debug_message:
                    print(f"[CAPTCHA OCR] Checking URL for verification...")

                try:
                    current_url_after_submit, _ = await nodriver_current_url(tab)
                except Exception as url_exc:
                    if show_debug_message:
                        print(f"[CAPTCHA OCR] Failed to get URL: {url_exc}")
                    current_url_after_submit = current_url_before_submit  # Assume same page

                if current_url_before_submit == current_url_after_submit:
                    # Still on same page - captcha was incorrect (alert was shown and dismissed)
                    if show_debug_message:
                        print(f"[CAPTCHA OCR] Captcha '{ocr_answer}' was incorrect, URL unchanged")

                    # IMPORTANT: iBon automatically refreshes captcha after alert dismissal
                    # Manual refresh is NOT needed and causes timing issues:
                    # - Alert dismiss triggers iBon's auto-refresh
                    # - Manual refresh would create a new captcha
                    # - Next OCR might still fetch the old URL from DOM cache
                    # Solution: Wait longer for iBon's refresh to fully stabilize
                    if show_debug_message:
                        print("[CAPTCHA OCR] Waiting for iBon auto-refresh to complete...")

                    await asyncio.sleep(2.5)  # Increased wait time for iBon refresh to fully stabilize

                    is_need_redo_ocr = True
                    is_form_submitted = False
                else:
                    # URL changed - captcha was correct
                    if show_debug_message:
                        print(f"[CAPTCHA OCR] Captcha '{ocr_answer}' accepted, URL changed")
                        print(f"[CAPTCHA OCR] Before: {current_url_before_submit}")
                        print(f"[CAPTCHA OCR] After: {current_url_after_submit}")
        else:
            # Invalid length
            if show_debug_message:
                print(f"[CAPTCHA OCR] Invalid answer length: {len(ocr_answer)} (expected 4)")

            if not away_from_keyboard_enable:
                await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer

    return is_need_redo_ocr, previous_answer, is_form_submitted

async def nodriver_ibon_captcha(tab, config_dict, ocr):
    """
    ibon captcha main function
    Returns: is_captcha_sent (bool)
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    if show_debug_message:
        print(f"[IBON CAPTCHA] Starting captcha handling")
        print(f"[IBON CAPTCHA] OCR enabled: {config_dict['ocr_captcha']['enable']}")
        print(f"[IBON CAPTCHA] Auto submit: {away_from_keyboard_enable}")

    is_captcha_sent = False

    if not config_dict["ocr_captcha"]["enable"]:
        # Manual mode
        await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
    else:
        # Auto OCR mode
        previous_answer = None
        current_url, _ = await nodriver_current_url(tab)
        fail_count = 0  # Track consecutive failures
        total_fail_count = 0  # Track total failures

        for redo_ocr in range(5):
            is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_ibon_auto_ocr(
                tab, config_dict, ocr, away_from_keyboard_enable, previous_answer
            )

            if not is_need_redo_ocr:
                is_captcha_sent = True

            if is_form_submitted:
                if show_debug_message:
                    print("[IBON CAPTCHA] Form submitted successfully")
                break

            if not away_from_keyboard_enable:
                if show_debug_message:
                    print("[IBON CAPTCHA] Switching to manual input mode")
                break

            if not is_need_redo_ocr:
                break

            # Track failures and refresh captcha after 3 consecutive failures
            if is_need_redo_ocr:
                fail_count += 1
                total_fail_count += 1
                if show_debug_message:
                    print(f"[IBON CAPTCHA] Fail count: {fail_count}, Total fails: {total_fail_count}")

                # Check if total failures reached 5, switch to manual input mode
                if total_fail_count >= 5:
                    print("[IBON CAPTCHA] OCR failed 5 times. Please enter captcha manually.")
                    away_from_keyboard_enable = False
                    await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
                    break

                if fail_count >= 3:
                    if show_debug_message:
                        print("[IBON CAPTCHA] 3 consecutive failures reached")

                    # Try to dismiss any existing alert before continuing
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        if show_debug_message:
                            print("[IBON CAPTCHA] Dismissed existing alert")
                    except:
                        pass

                    # IMPORTANT: iBon auto-refreshes captcha after alert dismiss
                    # Manual refresh causes timing conflicts with auto-refresh
                    # await nodriver_ibon_refresh_captcha(tab, config_dict)  # REMOVED
                    await asyncio.sleep(2.5)  # Wait for iBon's auto-refresh to complete
                    fail_count = 0  # Reset consecutive counter after refresh

            # Check if URL changed
            new_url, _ = await nodriver_current_url(tab)
            if new_url != current_url:
                if show_debug_message:
                    print("[IBON CAPTCHA] URL changed, exit OCR loop")
                break

            if show_debug_message:
                print(f"[IBON CAPTCHA] Retry {redo_ocr + 1}/5")

    return is_captcha_sent

async def nodriver_ibon_purchase_button_press(tab, config_dict):
    """
    Click the ibon purchase/next button after captcha is filled

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if button clicked successfully, False otherwise
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    is_button_clicked = False

    try:
        # Primary selector: #ticket-wrap > a.btn
        # Backup selectors from JavaScript extension analysis
        selectors = [
            '#ticket-wrap > a.btn',
            'div#ticket-wrap > a[onclick]',
            'div#ticket-wrap a.btn.btn-primary[href]'
        ]

        for selector in selectors:
            try:
                button = await tab.query_selector(selector)
                if button:
                    # Check if button is visible and enabled
                    is_visible = await tab.evaluate(f'''
                        (function() {{
                            const btn = document.querySelector('{selector}');
                            return btn && !btn.disabled && btn.offsetParent !== null;
                        }})();
                    ''')

                    if is_visible:
                        await button.click()
                        is_button_clicked = True
                        if show_debug_message:
                            print(f"[IBON PURCHASE] Successfully clicked button with selector: {selector}")
                        break
            except Exception as exc:
                if show_debug_message:
                    print(f"[IBON PURCHASE] Selector {selector} failed: {exc}")
                continue

        if not is_button_clicked and show_debug_message:
            print("[IBON PURCHASE] Purchase button not found or not clickable")

    except Exception as exc:
        if show_debug_message:
            print(f"[IBON PURCHASE ERROR] {exc}")
            import traceback
            traceback.print_exc()

    return is_button_clicked

async def nodriver_ibon_check_sold_out(tab, config_dict):
    """
    Check if the event/ticket is sold out on ibon

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if sold out, False otherwise
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)
    is_sold_out = False

    try:
        # Check if ticket-info div contains "已售完" text
        result = await tab.evaluate('''
            (function() {
                const ticketInfo = document.querySelector('#ticket-info');
                if (ticketInfo) {
                    const text = ticketInfo.textContent || ticketInfo.innerText;
                    return text.includes('已售完');
                }
                return false;
            })()
        ''')

        if result:
            is_sold_out = True
            if show_debug_message:
                print("[IBON] Event is sold out")

    except Exception as e:
        if show_debug_message:
            print(f"[IBON] Check sold out error: {e}")

    return is_sold_out

async def nodriver_ibon_verification_question(tab, fail_list, config_dict):
    """
    Handle verification question on ibon (simplified version)

    Args:
        tab: NoDriver tab object
        fail_list: List of previously failed answers
        config_dict: Configuration dictionary

    Returns:
        list: Updated fail_list

    TODO: Full implementation needs:
    - Question text extraction from #content > label
    - Answer list parsing from config or auto-guess
    - Form filling with retry mechanism
    - Integration with util.get_answer_list_from_question_string()
    """
    show_debug_message = config_dict["advanced"].get("verbose", False)

    try:
        # Get question text
        question_text = await tab.evaluate('''
            (function() {
                const content = document.querySelector('#content');
                if (content) {
                    const label = content.querySelector('label');
                    if (label) {
                        return label.textContent || label.innerText || '';
                    }
                }
                return '';
            })()
        ''')

        if len(question_text) > 0:
            if show_debug_message:
                print(f"[IBON] Verification question found: {question_text}")

            # TODO: Implement answer extraction and form filling
            # This requires integration with:
            # - util.get_answer_list_from_user_guess_string()
            # - util.get_answer_list_from_question_string()
            # - Form filling logic

            if show_debug_message:
                print("[IBON] Verification question handling not fully implemented")

    except Exception as e:
        if show_debug_message:
            print(f"[IBON] Verification question error: {e}")

    return fail_list

async def nodriver_ibon_main(tab, url, config_dict, ocr, Captcha_Browser):
    global ibon_dict
    if not 'ibon_dict' in globals():
        ibon_dict = {}
        ibon_dict["fail_list"]=[]
        ibon_dict["start_time"]=None
        ibon_dict["done_time"]=None
        ibon_dict["elapsed_time"]=None
        ibon_dict["is_popup_checkout"] = False
        ibon_dict["played_sound_order"] = False

    home_url_list = ['https://ticket.ibon.com.tw/'
    ,'https://ticket.ibon.com.tw/index/entertainment'
    ]
    for each_url in home_url_list:
        if each_url == url.lower():
            if config_dict["ocr_captcha"]["enable"]:
                # TODO:
                #set_non_browser_cookies(driver, url, Captcha_Browser)
                pass
            break

    # Auto-redirect if kicked back to homepage (防止被踢回首頁)
    # Pattern: Homepage → ActivityInfo page redirection
    # - If homepage config is set to ActivityInfo page, redirect back when kicked to homepage
    # - If homepage config is homepage itself, skip redirect (normal behavior)
    is_kicked_to_homepage = False
    normalized_url = url.lower().rstrip('/')
    if normalized_url == 'https://ticket.ibon.com.tw' or normalized_url == 'https://ticket.ibon.com.tw/index/entertainment':
        is_kicked_to_homepage = True

    if is_kicked_to_homepage:
        config_homepage = config_dict["homepage"]
        # Only redirect if user wants to be on ActivityInfo page
        should_redirect = '/activityinfo/' in config_homepage.lower()

        if should_redirect:
            show_debug_message = config_dict["advanced"].get("verbose", False)

            if show_debug_message:
                print(f"[IBON] Detected kicked back to homepage: {url}")
                print(f"[IBON] Redirecting to config homepage: {config_homepage}")

            try:
                await tab.get(config_homepage)
                # Wait for page load
                await asyncio.sleep(2)

                if show_debug_message:
                    print(f"[IBON] Successfully redirected to: {config_homepage}")
            except Exception as redirect_exc:
                if show_debug_message:
                    print(f"[IBON] Redirect failed: {redirect_exc}")


    # https://tour.ibon.com.tw/event/e23010000300mxu
    if 'tour' in url.lower() and '/event/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True
        if is_event_page:
            # ibon auto press signup
            await nodriver_press_button(tab, '.btn.btn-signup')

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
                    is_date_assign_by_bot = await nodriver_ibon_date_auto_select(tab, config_dict)

                    # Auto-reload if no purchase button found (ticket not yet on sale)
                    if not is_date_assign_by_bot:
                        show_debug_message = config_dict["advanced"].get("verbose", False)
                        if show_debug_message:
                            print("[IBON DETAIL] No purchase button found, page reload required")

                        try:
                            await tab.reload()
                            if show_debug_message:
                                print("[IBON DETAIL] Page reloaded successfully")
                        except Exception as reload_exc:
                            if show_debug_message:
                                print(f"[IBON DETAIL] Page reload failed: {reload_exc}")

                        # Use auto_reload_page_interval setting
                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            await asyncio.sleep(auto_reload_interval)

    if 'ibon.com.tw/error.html?' in url.lower():
        try:
            tab.back()
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
            # TODO:
            #ibon_dict["fail_list"] = ibon_verification_question(driver, ibon_dict["fail_list"], config_dict)
            pass
            is_match_target_feature = True

    if not is_enter_verify_mode:
        ibon_dict["fail_list"] = []

    # New ibon Event page format (Angular SPA): https://ticket.ibon.com.tw/Event/{eventId}/{sessionId}
    if not is_match_target_feature:
        is_new_event_page = False
        if 'ticket.ibon.com.tw' in url.lower() and '/event/' in url.lower():
            url_parts = url.split('/')
            # URL format: https://ticket.ibon.com.tw/Event/B09QY340/B09VO5KQ
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'Event', 'B09QY340', 'B09VO5KQ']
            if len(url_parts) == 6:
                is_new_event_page = True

        if is_new_event_page:
            if config_dict["area_auto_select"]["enable"]:
                is_price_assign_by_bot = False
                show_debug_message = config_dict["advanced"].get("verbose", False)

                area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
                is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_event_area_auto_select(tab, config_dict, area_keyword)

                if show_debug_message:
                    print(f"[NEW EVENT] Area selection result - is_price_assign_by_bot: {is_price_assign_by_bot}, is_need_refresh: {is_need_refresh}")

                # Auto-reload if no available ticket areas found
                if is_need_refresh:
                    if show_debug_message:
                        print("[NEW EVENT] No available ticket areas found, page reload required")

                    try:
                        await tab.reload()
                        if show_debug_message:
                            print("[NEW EVENT] Page reloaded successfully")
                    except Exception as reload_exc:
                        if show_debug_message:
                            print(f"[NEW EVENT] Page reload failed: {reload_exc}")

                    # Use auto_reload_page_interval setting
                    auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                    if auto_reload_interval > 0:
                        await asyncio.sleep(auto_reload_interval)

            is_match_target_feature = True

    # New ibon EventBuy page format: https://ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}
    if not is_match_target_feature:
        is_new_eventbuy_page = False
        if 'ticket.ibon.com.tw' in url.lower() and '/eventbuy/' in url.lower():
            url_parts = url.split('/')
            # URL format: https://ticket.ibon.com.tw/EventBuy/B09QY340/B09VO5KQ/B09VO6K0
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'EventBuy', 'eventId', 'sessionId', 'areaId']
            if len(url_parts) == 7:
                is_new_eventbuy_page = True

        if is_new_eventbuy_page:
            is_match_target_feature = True
            show_debug_message = config_dict["advanced"].get("verbose", False)

            if show_debug_message:
                print("[NEW EVENTBUY] Processing EventBuy page")

            # Check disable_adjacent_seat
            if config_dict["advanced"]["disable_adjacent_seat"]:
                is_finish_checkbox_click = await nodriver_check_checkbox(tab, '.asp-checkbox > input[type="checkbox"]:not(:checked)')

            # Step 1: Assign ticket number first
            is_ticket_number_assigned = False
            is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

            # Step 2: Handle captcha after ticket number is selected
            is_captcha_sent = False
            if is_ticket_number_assigned:
                if show_debug_message:
                    print("[NEW EVENTBUY] Ticket number assigned, proceeding to captcha")

                # Extract model name from URL for captcha
                domain_name = url.split('/')[2]
                # For EventBuy, use sessionId as model name
                model_name = url.split('/')[5] if len(url.split('/')) > 5 else 'EventBuy'
                if len(model_name) > 7:
                    model_name = model_name[:7]
                captcha_url = '/pic.aspx?TYPE=%s' % (model_name)

                # Set cookies for Captcha_Browser if needed
                if not Captcha_Browser is None:
                    Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                # Call ibon captcha handler (handles both OCR and manual mode)
                is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)

            # Step 3: Click purchase button if everything is ready
            if is_ticket_number_assigned:
                if is_captcha_sent:
                    if show_debug_message:
                        print("[NEW EVENTBUY] Clicking purchase button")

                    click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)

                    # Play sound if button clicked successfully
                    if click_ret:
                        play_sound_while_ordering(config_dict)
                        if show_debug_message:
                            print("[NEW EVENTBUY] Purchase button clicked successfully")
            else:
                # Check if sold out
                is_sold_out = await nodriver_ibon_check_sold_out(tab, config_dict)
                if is_sold_out:
                    if show_debug_message:
                        print("[NEW EVENTBUY] Sold out detected, going back and refreshing")
                    try:
                        await tab.back()
                        await tab.reload()
                    except Exception as exc:
                        if show_debug_message:
                            print(f"[NEW EVENTBUY] Back/reload failed: {exc}")

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
                # TODO:
                #clean_tag_by_selector(driver,select_query)
                
                select_query = "tr.sold-out"
                # TODO:
                #clean_tag_by_selector(driver,select_query)

                is_do_ibon_performance_with_ticket_number = False

                if 'PRODUCT_ID=' in url.upper():
                    # step 1: select area.
                    is_price_assign_by_bot = False
                    show_debug_message = config_dict["advanced"].get("verbose", False)

                    # Call area selection function (simplified version for testing)
                    # TODO: Implement nodriver_ibon_performance() wrapper with OR logic
                    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
                    is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_area_auto_select(tab, config_dict, area_keyword)

                    if show_debug_message:
                        print(f"Area selection result - is_price_assign_by_bot: {is_price_assign_by_bot}, is_need_refresh: {is_need_refresh}")

                    # Auto-reload if no available ticket areas found
                    if is_need_refresh:
                        if show_debug_message:
                            print("[IBON AREA] No available ticket areas found, page reload required")

                        try:
                            await tab.reload()
                            if show_debug_message:
                                print("[IBON AREA] Page reloaded successfully")
                        except Exception as reload_exc:
                            if show_debug_message:
                                print(f"[IBON AREA] Page reload failed: {reload_exc}")

                        # Use auto_reload_page_interval setting
                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            await asyncio.sleep(auto_reload_interval)

                    if not is_price_assign_by_bot:
                        # this case show captcha and ticket-number in this page.
                        # TODO:
                        #if ibon_ticket_number_appear(driver, config_dict):
                        #    is_do_ibon_performance_with_ticket_number = True
                        pass

                # Old ibon format handling
                if 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
                    is_do_ibon_performance_with_ticket_number = True

                if is_do_ibon_performance_with_ticket_number:
                    if config_dict["advanced"]["disable_adjacent_seat"]:
                        # TODO:
                        is_finish_checkbox_click = await nodriver_check_checkbox(tab, '.asp-checkbox > input[type="checkbox"]:not(:checked)')

                    # Step 1: Assign ticket number first
                    is_match_target_feature = True
                    is_ticket_number_assigned = False
                    is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

                    # Step 2: Handle captcha after ticket number is selected
                    is_captcha_sent = False
                    if is_ticket_number_assigned:
                        domain_name = url.split('/')[2]
                        model_name = url.split('/')[5]
                        if len(model_name) > 7:
                            model_name=model_name[:7]
                        captcha_url = '/pic.aspx?TYPE=%s' % (model_name)

                        # Set cookies for Captcha_Browser if needed
                        if not Captcha_Browser is None:
                            Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                        # Call ibon captcha handler (handles both OCR and manual mode)
                        is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)
                    
                    #print("is_ticket_number_assigned:", is_ticket_number_assigned)
                    if is_ticket_number_assigned:
                        if is_captcha_sent:
                            click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)

                            # only this case: "ticket number CHANGED by bot" and "cpatcha sent" to play sound!
                            if click_ret:
                                play_sound_while_ordering(config_dict)
                    else:
                        is_sold_out = await nodriver_ibon_check_sold_out(tab, config_dict)
                        if is_sold_out:
                            print("is_sold_out, go back , and refresh.")
                            # plan-A
                            #is_button_clicked = press_button(tab, By.CSS_SELECTOR, 'a.btn.btn-primary')
                            # plan-B, easy and better than plan-A
                            try:
                                tab.back()
                                tab.reload()
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
                is_finish_checkbox_click = await nodriver_ibon_ticket_agree(tab)
                if is_finish_checkbox_click:
                    is_name_based = False
                    try:
                        html_body = await tab.get_content()
                        #print("html_body:",len(html_body))
                        if html_body:
                            if len(html_body) > 1024:
                                if '實名制' in html_body:
                                    is_name_based = True
                    except Exception as exc:
                        #print(exc)
                        pass

                    if not is_name_based:
                        is_button_clicked = await nodriver_press_button(tab, 'a.btn.btn-pink.continue')

    # Check if reached checkout page (ticket purchase successful)
    # https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
    if '/utk02/utk0206_.aspx' in url.lower():
        if config_dict["advanced"].get("verbose", False):
            print("Reached checkout page - ticket purchase successful!")

        # Play sound notification (only once)
        if config_dict["advanced"]["play_sound"]["order"]:
            if not ibon_dict["played_sound_order"]:
                play_sound_while_ordering(config_dict)
            ibon_dict["played_sound_order"] = True

        # If headless mode, open browser to show checkout page (only once)
        if config_dict["advanced"]["headless"]:
            if not ibon_dict["is_popup_checkout"]:
                checkout_url = url
                print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)
                ibon_dict["is_popup_checkout"] = True
    else:
        # Reset status when leaving checkout page
        ibon_dict["is_popup_checkout"] = False
        ibon_dict["played_sound_order"] = False


async def nodriver_cityline_auto_retry_access(tab, url, config_dict):
    try:
        js = "goEvent();"
        await tab.evaluate(js)
    except Exception as exc:
        print(exc)
        pass

    # 刷太快, 會被封IP?
    # must wait...? no need to wait.
    auto_reload_page_interval = config_dict["advanced"]["auto_reload_page_interval"]
    if auto_reload_page_interval > 0:
        await asyncio.sleep(auto_reload_page_interval)

async def nodriver_cityline_login(tab, cityline_account):
    global is_cityline_account_assigned
    if not 'is_cityline_account_assigned' in globals():
        is_cityline_account_assigned = False

    #print("is_cityline_account_assigned", is_cityline_account_assigned)
    if not is_cityline_account_assigned:
        try:
            #await tab.verify_cf()
            el_account = await tab.query_selector('input[type="text"]')
            if el_account:
                await el_account.click()
                await el_account.apply('function (element) {element.value = ""; } ')
                await el_account.send_keys(cityline_account);
                await asyncio.sleep(random.uniform(0.4, 0.7))
                is_cityline_account_assigned = True
        except Exception as exc:
            print(exc)
            pass
    else:
        # after account inputed.
        try:
            # 使用 JavaScript 更安全地處理 checkbox，避免誤勾記得密碼
            checkbox_result = await tab.evaluate('''
                (function() {
                    const results = [];
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]:not(:checked)');

                    for (let i = 0; i < checkboxes.length; i++) {
                        const checkbox = checkboxes[i];
                        const id = checkbox.id || '';
                        const name = checkbox.name || '';
                        const className = checkbox.className || '';
                        const labelText = checkbox.labels && checkbox.labels[0] ? checkbox.labels[0].textContent : '';

                        // 檢查是否為記得密碼相關的 checkbox
                        const isRememberCheckbox =
                            id.toLowerCase().includes('remember') ||
                            name.toLowerCase().includes('remember') ||
                            className.toLowerCase().includes('remember') ||
                            labelText.includes('記得') ||
                            labelText.includes('記住') ||
                            labelText.includes('Remember');

                        results.push({
                            index: i,
                            id: id,
                            name: name,
                            className: className,
                            labelText: labelText,
                            isRemember: isRememberCheckbox
                        });
                    }

                    return results;
                })();
            ''')

            # 檢查結果並只勾選非記得密碼的 checkbox
            if checkbox_result:
                for item in checkbox_result:
                    if not item.get('isRemember', False):
                        click_result = await tab.evaluate(f'''
                            (function() {{
                                const checkboxes = document.querySelectorAll('input[type="checkbox"]:not(:checked)');
                                const checkbox = checkboxes[{item['index']}];
                                if (checkbox) {{
                                    checkbox.click();
                                    return true;
                                }}
                                return false;
                            }})();
                        ''')
                        if click_result:
                            print(f"clicked on agreement checkbox: {item.get('labelText', 'unknown')}")
                            break  # 只勾選第一個非記得密碼的 checkbox
                    else:
                        print(f"skipped remember checkbox: {item.get('labelText', 'unknown')}")
        except Exception as e:
            print(f"checkbox handling error: {e}")

            # 人性化延遲
            await asyncio.sleep(random.uniform(0.3, 0.8))
        except Exception as exc:
            print(exc)
            pass

async def nodriver_cityline_date_auto_select(tab, auto_select_mode, date_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False

    area_list = None
    try:
        my_css_selector = "button.date-time-position"
        area_list = await tab.query_selector_all(my_css_selector)
    except Exception as exc:
        #print(exc)
        pass

    matched_blocks = None
    if area_list:
        formated_area_list = None
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = area_list
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
                        row_html = await row.get_html()
                        row_text = util.remove_html_tags(row_html)
                        # PS: get_js_attributes on cityline due to: the JSON object must be str, bytes or bytearray, not NoneType
                        #js_attr = await row.get_js_attributes()
                        #row_html = js_attr["innerHTML"]
                        #row_text = js_attr["innerText"]
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
        #print("date date-time-position is None")
        pass

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if not target_area is None:
        try:
            await target_area.scroll_into_view()
            await target_area.click()
            ret = True
        except Exception as exc:
            print(exc)

    return ret

async def nodriver_check_modal_dialog_popup(tab):
    ret = False
    try:
        el_div = tab.query_selector('div.modal-dialog > div.modal-content')
        if el_div:
            ret = True
    except Exception as exc:
        print(exc)
        pass
    return ret

async def nodriver_cityline_purchase_button_press(tab, config_dict):
    date_auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    is_date_assign_by_bot = await nodriver_cityline_date_auto_select(tab, date_auto_select_mode, date_keyword)

    is_button_clicked = False
    if is_date_assign_by_bot:
        print("press purchase button")
        await nodriver_press_button(tab, 'button.purchase-btn')
        is_button_clicked = True
        # wait reCAPTCHA popup.
        await asyncio.sleep(6)

    return is_button_clicked

async def nodriver_cityline_close_second_tab(tab, url):
    new_tab = tab
    #print("tab count:", len(tab.browser.tabs))
    if len(tab.browser.tabs) > 1:
        # wait page ready.
        await asyncio.sleep(0.3)
        for tmp_tab in tab.browser.tabs:
            if tmp_tab != tab:
                tmp_url, is_quit_bot = await nodriver_current_url(tmp_tab)
                if len(tmp_url) > 0:
                    if tmp_url[:5] == "https":
                        await new_tab.activate()
                        await tab.close()
                        await asyncio.sleep(0.3)
                        new_tab = tmp_tab
                        break
    return new_tab

async def nodriver_cityline_main(tab, url, config_dict):
    global cityline_dict
    if not 'cityline_dict' in globals():
        cityline_dict = {}
        cityline_dict["played_sound_ticket"] = False

    if 'msg.cityline.com' in url or 'event.cityline.com' in url:
        is_dom_ready = False
        try:
            html_body = await tab.get_content()
            if html_body:
                if len(html_body) > 10240:
                    is_dom_ready = True
        except Exception as exc:
            pass
        if is_dom_ready:
            #await nodriver_cityline_auto_retry_access(tab, url, config_dict)
            pass

    if 'cityline.com/Login.html' in url:
        cityline_account = config_dict["advanced"]["cityline_account"]
        if len(cityline_account) > 4:
            await nodriver_cityline_login(tab, cityline_account)

    tab = await nodriver_cityline_close_second_tab(tab, url)

    # date page.
    #https://venue.cityline.com/utsvInternet/EVENT_NAME/eventDetail?event=EVENT_CODE
    global cityline_purchase_button_pressed
    if not 'cityline_purchase_button_pressed' in globals():
        cityline_purchase_button_pressed = False
    if '/eventDetail?' in url:
        # detect fail.
        #is_modal_dialog_popup = await nodriver_check_modal_dialog_popup(tab)

        if not cityline_purchase_button_pressed:
            if config_dict["date_auto_select"]["enable"]:
                is_button_clicked = await nodriver_cityline_purchase_button_press(tab, config_dict)
                if is_button_clicked:
                    cityline_purchase_button_pressed = True
    else:
        cityline_purchase_button_pressed = False


    # area page:
    # TODO:
    #https://venue.cityline.com/utsvInternet/EVENT_NAME/performance?event=EVENT_CODE&perfId=PROFORMANCE_ID
    if 'venue.cityline.com' in url and '/performance?':
        if config_dict["advanced"]["play_sound"]["ticket"]:
            if not cityline_dict["played_sound_ticket"]:
                play_sound_while_ordering(config_dict)
            cityline_dict["played_sound_ticket"] = True
    else:
        cityline_dict["played_sound_ticket"] = False

    return tab


async def nodriver_facebook_main(tab, config_dict):
    facebook_account = config_dict["advanced"]["facebook_account"].strip()
    facebook_password = config_dict["advanced"]["facebook_password_plaintext"].strip()
    if facebook_password == "":
        facebook_password = util.decryptMe(config_dict["advanced"]["facebook_password"])
    if len(facebook_account) > 4:
        await nodriver_facebook_login(tab, facebook_account, facebook_password)

def get_nodriver_browser_args():
    """
    取得 nodriver 瀏覽器參數
    參考 stackoverflow.max-everyday.com，使用經過驗證可通過 Cloudflare 的參數
    """
    # 基於文章驗證的可通過 Cloudflare 檢查的參數
    browser_args = [
        "--disable-animations",
        "--disable-app-info-dialog-mac",
        "--disable-background-networking",
        "--disable-backgrounding-occluded-windows",
        "--disable-breakpad",
        "--disable-component-update",
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
        "--no-service-autorun",
        "--password-store=basic",
        "--remote-debugging-host=127.0.0.1",
        "--lang=zh-TW",
    ]

    # 如果啟用專家模式，謹慎加入額外的高風險參數
    if CLOUDFLARE_ENABLE_EXPERT_MODE:
        # 注意：這些參數可能增加被偵測的風險，但提供更強的繞過能力
        expert_args = [
            "--no-sandbox",  # 某些環境需要，有被偵測風險
            "--disable-web-security",  # 高風險但強效的參數
        ]
        browser_args.extend(expert_args)

    return browser_args

def get_maxbot_extension_path(extension_folder):
    app_root = util.get_app_root()
    extension_path = "webdriver"
    extension_path = os.path.join(extension_path, extension_folder)
    config_filepath = os.path.join(app_root, extension_path)
    #print("config_filepath:", config_filepath)

    # double check extesion mainfest
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
    browser_args = get_nodriver_browser_args()
    if len(config_dict["advanced"]["proxy_server_port"]) > 2:
        browser_args.append('--proxy-server=%s' % config_dict["advanced"]["proxy_server_port"])
    conf = Config(browser_args=browser_args, lang=default_lang, no_sandbox=no_sandbox, headless=config_dict["advanced"]["headless"])
    if config_dict["advanced"]["chrome_extension"]:
        ext = get_maxbot_extension_path(CONST_MAXBOT_EXTENSION_NAME)
        if len(ext) > 0:
            conf.add_extension(ext)
            util.dump_settings_to_maxbot_plus_extension(ext, config_dict, CONST_MAXBOT_CONFIG_FILE)
        ext = get_maxbot_extension_path(CONST_MAXBLOCK_EXTENSION_NAME)
        if len(ext) > 0:
            conf.add_extension(ext)
            util.dump_settings_to_maxblock_plus_extension(ext, config_dict, CONST_MAXBOT_CONFIG_FILE, CONST_MAXBLOCK_EXTENSION_FILTER)
    return conf

async def nodrver_block_urls(tab, config_dict):
    NETWORK_BLOCKED_URLS = [
        '*.clarity.ms/*',
        '*.cloudfront.com/*',
        '*.doubleclick.net/*',
        '*.lndata.com/*',
        '*.rollbar.com/*',
        '*.twitter.com/i/*',
        '*/adblock.js',
        '*/google_ad_block.js',
        '*cityline.com/js/others.min.js',
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
    is_quit_bot = False
    exit_bot_error_strings = [
        "server rejected WebSocket connection: HTTP 500",
        "[Errno 61] Connect call failed ('127.0.0.1',",
        "[WinError 1225] ",
    ]

    url = ""
    if tab:
        url_dict = {}
        try:
            url_dict = await tab.js_dumps('window.location.href')
        except Exception as exc:
            print(exc)
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass
            if len(str_exc) > 0:
                for each_error_string in exit_bot_error_strings:
                    if each_error_string in str_exc:
                        #print('quit bot by error:', each_error_string, driver)
                        is_quit_bot = True

        url_array = []
        if url_dict:
            for k in url_dict:
                if k.isnumeric():
                    if "0" in url_dict[k]:
                        url_array.append(url_dict[k]["0"])
            url = ''.join(url_array)
    return url, is_quit_bot

def nodriver_overwrite_prefs(conf):
    #print(conf.user_data_dir)
    prefs_filepath = os.path.join(conf.user_data_dir,"Default")
    if not os.path.exists(prefs_filepath):
        os.mkdir(prefs_filepath)
    prefs_filepath = os.path.join(prefs_filepath,"Preferences")
    
    prefs_dict = {
        "credentials_enable_service": False,
        "ack_existing_ntp_extensions": False,
        "translate":{"enabled": False}}
    prefs_dict["in_product_help"]={}
    prefs_dict["in_product_help"]["snoozed_feature"]={}
    prefs_dict["in_product_help"]["snoozed_feature"]["IPH_LiveCaption"]={}
    prefs_dict["in_product_help"]["snoozed_feature"]["IPH_LiveCaption"]["is_dismissed"]=True
    prefs_dict["in_product_help"]["snoozed_feature"]["IPH_LiveCaption"]["last_dismissed_by"]=4
    prefs_dict["media_router"]={}
    prefs_dict["media_router"]["show_cast_sessions_started_by_other_devices"]={}
    prefs_dict["media_router"]["show_cast_sessions_started_by_other_devices"]["enabled"]=False
    prefs_dict["net"]={}
    prefs_dict["net"]["network_prediction_options"]=3
    prefs_dict["privacy_guide"]={}
    prefs_dict["privacy_guide"]["viewed"]=True
    prefs_dict["privacy_sandbox"]={}
    prefs_dict["privacy_sandbox"]["first_party_sets_enabled"]=False
    prefs_dict["profile"]={}
    #prefs_dict["profile"]["cookie_controls_mode"]=1
    prefs_dict["profile"]["default_content_setting_values"]={}
    prefs_dict["profile"]["default_content_setting_values"]["notifications"]=2
    prefs_dict["profile"]["default_content_setting_values"]["sound"]=2
    prefs_dict["profile"]["name"]=CONST_APP_VERSION
    prefs_dict["profile"]["password_manager_enabled"]=False
    prefs_dict["safebrowsing"]={}
    prefs_dict["safebrowsing"]["enabled"]=False
    prefs_dict["safebrowsing"]["enhanced"]=False
    prefs_dict["sync"]={}
    prefs_dict["sync"]["autofill_wallet_import_enabled_migrated"]=False

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
        "history-journeys@4",
        "memory-saver-multi-state-mode@1",
        "modal-memory-saver@1",
        "read-anything@2"
    ]
    state_dict["dns_over_https"]={}
    state_dict["dns_over_https"]["mode"]="off"
    json_str = json.dumps(state_dict)
    with open(state_filepath, 'w') as outfile:
        outfile.write(json_str)

async def check_refresh_datetime_occur(tab, target_time):
    is_refresh_datetime_sent = False

    system_clock_data = datetime.now()
    current_time = system_clock_data.strftime('%H:%M:%S')
    if target_time == current_time:
        try:
            await tab.reload()
            is_refresh_datetime_sent = True
            print("send refresh at time:", current_time)
        except Exception as exc:
            pass

    return is_refresh_datetime_sent

async def main(args):
    config_dict = get_config_dict(args)

    driver = None
    tab = None
    if not config_dict is None:
        sandbox = False
        conf = get_extension_config(config_dict)
        nodriver_overwrite_prefs(conf)
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

    url = ""
    last_url = ""

    fami_dict = {}
    fami_dict["fail_list"] = []
    fami_dict["last_activity"]=""

    ticketplus_dict = {}
    ticketplus_dict["fail_list"]=[]
    ticketplus_dict["is_popup_confirm"] = False

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
            ocr.set_ranges(0)  # Restrict to digits only (0-9) for ibon captchas
            Captcha_Browser = NonBrowser()
            if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                #set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
                pass
    except Exception as exc:
        print(exc)
        pass

    maxbot_last_reset_time = time.time()
    is_quit_bot = False
    is_refresh_datetime_sent = False

    while True:
        await asyncio.sleep(0.05)

        # pass if driver not loaded.
        if driver is None:
            print("nodriver not accessible!")
            break

        if not is_quit_bot:
            url, is_quit_bot = await nodriver_current_url(tab)
            #print("url:", url)

        if is_quit_bot:
            try:
                await driver.stop()
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
            is_refresh_datetime_sent = await check_refresh_datetime_occur(tab, config_dict["refresh_datetime"])

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
                await nodriver_kktix_paused_main(tab, url, config_dict)
            # sleep more when paused.
            await asyncio.sleep(0.1)
            continue

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            is_quit_bot = await nodriver_kktix_main(tab, url, config_dict)
            if is_quit_bot:
                print("KKTIX 搶票完成，進入暫停模式")
                # 建立暫停檔案，讓程式進入暫停狀態而不是結束
                try:
                    with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
                        text_file.write("")
                    print("已自動暫停，可透過 Web 介面繼續執行")
                    # 重置 is_quit_bot 避免程式結束
                    is_quit_bot = False
                except Exception as e:
                    print(f"建立暫停檔案失敗: {e}")
                # 不執行 break，讓程式繼續執行並進入暫停模式

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if 'ticketmaster.' in url:
            tixcraft_family = True

        if tixcraft_family:
            is_quit_bot = await nodriver_tixcraft_main(tab, url, config_dict, ocr, Captcha_Browser)

        if 'famiticket.com' in url:
            #fami_dict = famiticket_main(driver, url, config_dict, fami_dict)
            pass

        if 'ibon.com' in url:
            await nodriver_ibon_main(tab, url, config_dict, ocr, Captcha_Browser)

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

        # https://ticketplus.com.tw/*
        if 'ticketplus.com' in url:
            await nodriver_ticketplus_main(tab, url, config_dict, ocr, Captcha_Browser)

            # 檢查是否購票完成（包含確認頁面處理），如果完成則跳出迴圈
            if 'ticketplus_dict' in globals():
                if ticketplus_dict.get("purchase_completed", False):
                    if config_dict["advanced"].get("verbose", False):
                        print("✓ TicketPlus 購票完成，進入暫停模式")
                    # 建立暫停檔案，讓程式進入暫停狀態而不是結束
                    try:
                        with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
                            text_file.write("")
                        if config_dict["advanced"].get("verbose", False):
                            print("已自動暫停，可透過 Web 介面繼續執行")
                        # 重置 is_quit_bot 避免程式結束
                        is_quit_bot = False
                    except Exception as e:
                        if config_dict["advanced"].get("verbose", False):
                            print(f"建立暫停檔案失敗: {e}")
                elif ticketplus_dict.get("is_ticket_assigned", False) and '/confirm/' in url.lower():
                    # 如果在確認頁面且已指派票券，也可以結束
                    if config_dict["advanced"].get("verbose", False):
                        print("✓ TicketPlus 已在確認頁面，購票流程成功，進入暫停模式")
                    # 建立暫停檔案，讓程式進入暫停狀態而不是結束
                    try:
                        with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
                            text_file.write("")
                        if config_dict["advanced"].get("verbose", False):
                            print("已自動暫停，可透過 Web 介面繼續執行")
                        # 重置 is_quit_bot 避免程式結束
                        is_quit_bot = False
                    except Exception as e:
                        if config_dict["advanced"].get("verbose", False):
                            print(f"建立暫停檔案失敗: {e}")

        if 'urbtix.hk' in url:
            #urbtix_main(driver, url, config_dict)
            pass

        if 'cityline.com' in url:
            tab = await nodriver_cityline_main(tab, url, config_dict)

        softix_family = False
        if 'hkticketing.com' in url:
            softix_family = True
        if 'galaxymacau.com' in url:
            softix_family = True
        if 'ticketek.com' in url:
            softix_family = True
        if softix_family:
            #softix_powerweb_main(driver, url, config_dict)
            pass

        # for facebook
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            await nodriver_facebook_main(tab, config_dict)

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

    parser.add_argument("--date_auto_select_mode",
        help="overwrite date_auto_select mode",
        choices=['random', 'center', 'from top to bottom', 'from bottom to top'],
        type=str)

    parser.add_argument("--date_keyword",
        help="overwrite date_auto_select date_keyword",
        type=str)

    args = parser.parse_args()
    uc.loop().run_until_complete(main(args))

if __name__ == "__main__":
    cli()
