#!/usr/bin/env python3
#encoding=utf-8
import asyncio
import base64
import json
import os
import platform
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime

import tornado
from tornado.web import Application
from tornado.web import StaticFileHandler

import util
from typing import (
    Dict,
    Any,
    Union,
    Optional,
    Awaitable,
    Tuple,
    List,
    Callable,
    Iterable,
    Generator,
    Type,
    TypeVar,
    cast,
    overload,
)

try:
    import ddddocr
except Exception as exc:
    pass

CONST_APP_VERSION = "MaxBot (2024.04.18)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_EXTENSION_STATUS_JSON = "status.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

CONST_SERVER_PORT = 16888

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
CONST_SELECT_ORDER_DEFAULT = CONST_RANDOM
CONST_EXCLUDE_DEFAULT = "\"輪椅\",\"身障\",\"身心 障礙\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
CONST_CAPTCHA_SOUND_FILENAME_DEFAULT = "ding-dong.wav"
CONST_HOMEPAGE_DEFAULT = "about:blank"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_DP = "DrissionPage"
CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"

CONST_SUPPORTED_SITES = ["https://kktix.com"
    ,"https://tixcraft.com (拓元)"
    ,"https://ticketmaster.sg"
    #,"https://ticketmaster.com"
    ,"https://teamear.tixcraft.com/ (添翼)"
    ,"https://www.indievox.com/ (獨立音樂)"
    ,"https://www.famiticket.com.tw (全網)"
    ,"https://ticket.ibon.com.tw/"
    ,"https://kham.com.tw/ (寬宏)"
    ,"https://ticket.com.tw/ (年代)"
    ,"https://tickets.udnfunlife.com/ (udn售票網)"
    ,"https://ticketplus.com.tw/ (遠大)"
    ,"===[香港或南半球的系統]==="
    ,"http://www.urbtix.hk/ (城市)"
    ,"https://www.cityline.com/ (買飛)"
    ,"https://hotshow.hkticketing.com/ (快達票)"
    ,"https://ticketing.galaxymacau.com/ (澳門銀河)"
    ,"http://premier.ticketek.com.au"
    ]

URL_DONATE = 'https://max-everyday.com/about/#donate'
URL_HELP = 'https://max-everyday.com/2018/03/tixcraft-bot/'
URL_RELEASE = 'https://github.com/max32002/tixcraft_bot/releases'
URL_FB = 'https://www.facebook.com/maxbot.ticket'
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'
URL_FIREFOX_DRIVER = 'https://github.com/mozilla/geckodriver/releases'
URL_EDGE_DRIVER = 'https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/'


def get_default_config():
    config_dict={}

    config_dict["homepage"] = CONST_HOMEPAGE_DEFAULT
    config_dict["browser"] = "chrome"
    config_dict["language"] = "English"
    config_dict["ticket_number"] = 2
    config_dict["ocr_captcha"] = {}
    config_dict["ocr_captcha"]["enable"] = True
    config_dict["ocr_captcha"]["beta"] = True
    config_dict["ocr_captcha"]["force_submit"] = True
    config_dict["ocr_captcha"]["image_source"] = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
    config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_UC

    config_dict["date_auto_select"] = {}
    config_dict["date_auto_select"]["enable"] = True
    config_dict["date_auto_select"]["date_keyword"] = ""
    config_dict["date_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT

    config_dict["area_auto_select"] = {}
    config_dict["area_auto_select"]["enable"] = True
    config_dict["area_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT
    config_dict["area_auto_select"]["area_keyword"] = ""
    config_dict["keyword_exclude"] = CONST_EXCLUDE_DEFAULT

    config_dict['kktix']={}
    config_dict["kktix"]["auto_press_next_step_button"] = True
    config_dict["kktix"]["auto_fill_ticket_number"] = True
    config_dict["kktix"]["max_dwell_time"] = 60

    config_dict['cityline']={}
    config_dict["cityline"]["cityline_queue_retry"] = True

    config_dict['tixcraft']={}
    config_dict["tixcraft"]["pass_date_is_sold_out"] = True
    config_dict["tixcraft"]["auto_reload_coming_soon_page"] = True

    config_dict['advanced']={}

    config_dict['advanced']['play_sound']={}
    config_dict["advanced"]["play_sound"]["ticket"] = True
    config_dict["advanced"]["play_sound"]["order"] = True
    config_dict["advanced"]["play_sound"]["filename"] = CONST_CAPTCHA_SOUND_FILENAME_DEFAULT

    config_dict["advanced"]["tixcraft_sid"] = ""
    config_dict["advanced"]["ibonqware"] = ""
    config_dict["advanced"]["facebook_account"] = ""
    config_dict["advanced"]["kktix_account"] = ""
    config_dict["advanced"]["fami_account"] = ""
    config_dict["advanced"]["cityline_account"] = ""
    config_dict["advanced"]["urbtix_account"] = ""
    config_dict["advanced"]["hkticketing_account"] = ""
    config_dict["advanced"]["kham_account"] = ""
    config_dict["advanced"]["ticket_account"] = ""
    config_dict["advanced"]["udn_account"] = ""
    config_dict["advanced"]["ticketplus_account"] = ""

    config_dict["advanced"]["facebook_password"] = ""
    config_dict["advanced"]["kktix_password"] = ""
    config_dict["advanced"]["fami_password"] = ""
    config_dict["advanced"]["urbtix_password"] = ""
    config_dict["advanced"]["cityline_password"] = ""
    config_dict["advanced"]["hkticketing_password"] = ""
    config_dict["advanced"]["kham_password"] = ""
    config_dict["advanced"]["ticket_password"] = ""
    config_dict["advanced"]["udn_password"] = ""
    config_dict["advanced"]["ticketplus_password"] = ""

    config_dict["advanced"]["facebook_password_plaintext"] = ""
    config_dict["advanced"]["kktix_password_plaintext"] = ""
    config_dict["advanced"]["fami_password_plaintext"] = ""
    config_dict["advanced"]["urbtix_password_plaintext"] = ""
    config_dict["advanced"]["cityline_password_plaintext"] = ""
    config_dict["advanced"]["hkticketing_password_plaintext"] = ""
    config_dict["advanced"]["kham_password_plaintext"] = ""
    config_dict["advanced"]["ticket_password_plaintext"] = ""
    config_dict["advanced"]["udn_password_plaintext"] = ""
    config_dict["advanced"]["ticketplus_password_plaintext"] = ""

    config_dict["advanced"]["chrome_extension"] = True
    config_dict["advanced"]["disable_adjacent_seat"] = False
    config_dict["advanced"]["hide_some_image"] = False
    config_dict["advanced"]["block_facebook_network"] = False

    config_dict["advanced"]["headless"] = False
    config_dict["advanced"]["verbose"] = False
    config_dict["advanced"]["auto_guess_options"] = True
    config_dict["advanced"]["user_guess_string"] = ""
    
    # remote_url not under ocr, due to not only support ocr features.
    config_dict["advanced"]["remote_url"] = "\"http://127.0.0.1:%d/\"" % (CONST_SERVER_PORT)

    config_dict["advanced"]["auto_reload_page_interval"] = 0.1
    config_dict["advanced"]["reset_browser_interval"] = 0
    config_dict["advanced"]["proxy_server_port"] = ""
    config_dict["advanced"]["window_size"] = "480,1024"

    config_dict["advanced"]["idle_keyword"] = ""
    config_dict["advanced"]["resume_keyword"] = ""
    config_dict["advanced"]["idle_keyword_second"] = ""
    config_dict["advanced"]["resume_keyword_second"] = ""

    return config_dict

def read_last_url_from_file():
    text = ""
    if os.path.exists(CONST_MAXBOT_LAST_URL_FILE):
        try:
            with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
                text = text_file.readline()
        except Exception as e:
            pass
    return text

def load_json():
    app_root = util.get_app_root()

    # overwrite config path.
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        try:
            with open(config_filepath) as json_data:
                config_dict = json.load(json_data)
        except Exception as e:
            pass
    else:
        config_dict = get_default_config()
    return config_filepath, config_dict

def reset_json():
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    if os.path.exists(str(config_filepath)):
        try:
            os.unlink(str(config_filepath))
        except Exception as exc:
            print(exc)
            pass

    config_dict = get_default_config()
    return config_filepath, config_dict

def decrypt_password(config_dict):
    config_dict["advanced"]["facebook_password"] = util.decryptMe(config_dict["advanced"]["facebook_password"])
    config_dict["advanced"]["kktix_password"] = util.decryptMe(config_dict["advanced"]["kktix_password"])
    config_dict["advanced"]["fami_password"] = util.decryptMe(config_dict["advanced"]["fami_password"])
    config_dict["advanced"]["cityline_password"] = util.decryptMe(config_dict["advanced"]["cityline_password"])
    config_dict["advanced"]["urbtix_password"] = util.decryptMe(config_dict["advanced"]["urbtix_password"])
    config_dict["advanced"]["hkticketing_password"] = util.decryptMe(config_dict["advanced"]["hkticketing_password"])
    config_dict["advanced"]["kham_password"] = util.decryptMe(config_dict["advanced"]["kham_password"])
    config_dict["advanced"]["ticket_password"] = util.decryptMe(config_dict["advanced"]["ticket_password"])
    config_dict["advanced"]["udn_password"] = util.decryptMe(config_dict["advanced"]["udn_password"])
    config_dict["advanced"]["ticketplus_password"] = util.decryptMe(config_dict["advanced"]["ticketplus_password"])
    return config_dict

def encrypt_password(config_dict):
    config_dict["advanced"]["facebook_password"] = util.encryptMe(config_dict["advanced"]["facebook_password"])
    config_dict["advanced"]["kktix_password"] = util.encryptMe(config_dict["advanced"]["kktix_password"])
    config_dict["advanced"]["fami_password"] = util.encryptMe(config_dict["advanced"]["fami_password"])
    config_dict["advanced"]["cityline_password"] = util.encryptMe(config_dict["advanced"]["cityline_password"])
    config_dict["advanced"]["urbtix_password"] = util.encryptMe(config_dict["advanced"]["urbtix_password"])
    config_dict["advanced"]["hkticketing_password"] = util.encryptMe(config_dict["advanced"]["hkticketing_password"])
    config_dict["advanced"]["kham_password"] = util.encryptMe(config_dict["advanced"]["kham_password"])
    config_dict["advanced"]["ticket_password"] = util.encryptMe(config_dict["advanced"]["ticket_password"])
    config_dict["advanced"]["udn_password"] = util.encryptMe(config_dict["advanced"]["udn_password"])
    config_dict["advanced"]["ticketplus_password"] = util.encryptMe(config_dict["advanced"]["ticketplus_password"])
    return config_dict

def maxbot_idle():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    try:
        with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
            text_file.write("")
    except Exception as e:
        pass

def maxbot_resume():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    for i in range(3):
         util.force_remove_file(idle_filepath)

def launch_maxbot():
    global launch_counter
    if "launch_counter" in globals():
        launch_counter += 1
    else:
        launch_counter = 0

    config_filepath, config_dict = load_json()
    config_dict = decrypt_password(config_dict)
    
    script_name = "chrome_tixcraft"
    if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_NODRIVER:
        script_name = "nodriver_tixcraft"

    window_size = config_dict["advanced"]["window_size"]
    if len(window_size) > 0:
        if "," in window_size:
            size_array = window_size.split(",")
            target_width = int(size_array[0])
            target_left = target_width * launch_counter
            #print("target_left:", target_left)
            if target_left >= 1440:
                launch_counter = 0
            window_size = window_size + "," + str(launch_counter)
            #print("window_size:", window_size)

    threading.Thread(target=util.launch_maxbot, args=(script_name,"","","","",window_size,)).start()

def change_maxbot_status_by_keyword():
    config_filepath, config_dict = load_json()

    system_clock_data = datetime.now()
    current_time = system_clock_data.strftime('%H:%M:%S')
    #print('Current Time is:', current_time)
    #print("idle_keyword", config_dict["advanced"]["idle_keyword"])
    if len(config_dict["advanced"]["idle_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            maxbot_idle()
    #print("resume_keyword", config_dict["advanced"]["resume_keyword"])
    if len(config_dict["advanced"]["resume_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            maxbot_resume()
    
    current_time = system_clock_data.strftime('%S')
    if len(config_dict["advanced"]["idle_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword_second"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            maxbot_idle()
    if len(config_dict["advanced"]["resume_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword_second"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            maxbot_resume()

def clean_extension_status():
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    target_path = os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME)
    target_path = os.path.join(target_path, "data")
    target_path = os.path.join(target_path, CONST_MAXBOT_EXTENSION_STATUS_JSON)
    if os.path.exists(target_path):
        try:
            os.unlink(target_path)
        except Exception as exc:
            print(exc)
            pass

def sync_status_to_extension(status):
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    target_path = os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME)
    target_path = os.path.join(target_path, "data")
    if os.path.exists(target_path):
        target_path = os.path.join(target_path, CONST_MAXBOT_EXTENSION_STATUS_JSON)
        #print("save as to:", target_path)
        status_json={}
        status_json["status"]=status
        #print("dump json to path:", target_path)
        try:
            with open(target_path, 'w') as outfile:
                json.dump(status_json, outfile)
        except Exception as e:
            pass

def clean_tmp_file():
    remove_file_list = [CONST_MAXBOT_LAST_URL_FILE
        ,CONST_MAXBOT_INT28_FILE
        ,CONST_MAXBOT_ANSWER_ONLINE_FILE
        ,CONST_MAXBOT_QUESTION_FILE
    ]
    for filepath in remove_file_list:
         util.force_remove_file(filepath)

class QuestionHandler(tornado.web.RequestHandler):
    def get(self):
        global txt_question
        txt_question.insert("1.0", "")

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"version":self.application.version})

class ShutdownHandler(tornado.web.RequestHandler):
    def get(self):
        global GLOBAL_SERVER_SHUTDOWN
        GLOBAL_SERVER_SHUTDOWN = True
        self.write({"showdown": GLOBAL_SERVER_SHUTDOWN})

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        is_paused = False
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            is_paused = True
        url = read_last_url_from_file()
        self.write({"status": not is_paused, "last_url": url})

class PauseHandler(tornado.web.RequestHandler):
    def get(self):
        maxbot_idle()
        self.write({"pause": True})

class ResumeHandler(tornado.web.RequestHandler):
    def get(self):
        maxbot_resume()
        self.write({"resume": True})

class RunHandler(tornado.web.RequestHandler):
    def get(self):
        print('run button pressed.')
        launch_maxbot()
        self.write({"run": True})

class LoadJsonHandler(tornado.web.RequestHandler):
    def get(self):
        config_filepath, config_dict = load_json()
        config_dict = decrypt_password(config_dict)
        self.write(config_dict)

class ResetJsonHandler(tornado.web.RequestHandler):
    def get(self):
        config_filepath, config_dict = reset_json()
        util.save_json(config_dict, config_filepath)
        self.write(config_dict)

class SaveJsonHandler(tornado.web.RequestHandler):
    def post(self):
        _body = None
        is_pass_check = True
        error_message = ""
        error_code = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                error_message = "wrong json format"
                error_code = 1002
                pass

        if is_pass_check:
            app_root = util.get_app_root()
            config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
            config_dict = encrypt_password(_body)

            if config_dict["kktix"]["max_dwell_time"] > 0:
                if config_dict["kktix"]["max_dwell_time"] < 15:
                    # min value is 15 seconds.
                    config_dict["kktix"]["max_dwell_time"] = 15

            if config_dict["advanced"]["reset_browser_interval"] > 0:
                if config_dict["advanced"]["reset_browser_interval"] < 20:
                    # min value is 20 seconds.
                    config_dict["advanced"]["reset_browser_interval"] = 20

            # due to cloudflare.
            if ".cityline.com" in config_dict["homepage"]:
                config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_NODRIVER

            util.save_json(config_dict, config_filepath)

        if not is_pass_check:
            self.set_status(401)
            self.write(dict(error=dict(message=error_message,code=error_code)))

        self.finish()

class OcrHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"answer": "1234"})

    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        _body = None
        is_pass_check = True
        errorMessage = ""
        errorCode = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                errorMessage = "wrong json format"
                errorCode = 1001
                pass

        img_base64 = None
        image_data = ""
        if is_pass_check:
            if 'image_data' in _body:
                image_data = _body['image_data']
                if len(image_data) > 0:
                    img_base64 = base64.b64decode(image_data)
            else:
                errorMessage = "image_data not exist"
                errorCode = 1002

        #print("is_pass_check:", is_pass_check)
        #print("errorMessage:", errorMessage)
        #print("errorCode:", errorCode)
        ocr_answer = ""
        if not img_base64 is None:
            try:
                ocr_answer = self.application.ocr.classification(img_base64)
                print("ocr_answer:", ocr_answer)
            except Exception as exc:
                pass

        self.write({"answer": ocr_answer})

class QueryHandler(tornado.web.RequestHandler):
    def format_config_keyword_for_json(self, user_input):
        if len(user_input) > 0:
            if not ('\"' in user_input):
                user_input = '"' + user_input + '"'
        return user_input

    def compose_as_json(self, user_input):
        user_input = self.format_config_keyword_for_json(user_input)
        return "{\"data\":[%s]}" % user_input

    def get(self):
        global txt_answer_value
        answer_text = ""
        try:
            answer_text = txt_answer_value.get().strip()
        except Exception as exc:
            pass
        answer_text_output = self.compose_as_json(answer_text)
        #print("answer_text_output:", answer_text_output)
        self.write(answer_text_output)

async def main_server():
    ocr = None
    try:
        ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    except Exception as exc:
        print(exc)
        pass

    app = Application([
        ("/version", VersionHandler),
        ("/shutdown", ShutdownHandler),

        # status api
        ("/status", StatusHandler),
        ("/pause", PauseHandler),
        ("/resume", ResumeHandler),
        ("/run", RunHandler),
        
        # json api
        ("/load", LoadJsonHandler),
        ("/save", SaveJsonHandler),
        ("/reset", ResetJsonHandler),

        ("/ocr", OcrHandler),
        ("/query", QueryHandler),
        ("/question", QuestionHandler),
        ('/(.*)', StaticFileHandler, {"path": os.path.join(".", 'www/')}),
    ])
    app.ocr = ocr;
    app.version = CONST_APP_VERSION;

    app.listen(CONST_SERVER_PORT)
    print("server running on port:", CONST_SERVER_PORT)

    url="http://127.0.0.1:" + str(CONST_SERVER_PORT) + "/settings.html"
    print("goto url:", url)
    webbrowser.open_new(url)
    await asyncio.Event().wait()

def web_server():
    is_port_binded = util.is_connectable(CONST_SERVER_PORT)
    #print("is_port_binded:", is_port_binded)
    if not is_port_binded:
        asyncio.run(main_server())
    else:
        print("port:", CONST_SERVER_PORT, " is in used.")

def settgins_gui_timer():
    while True:
        change_maxbot_status_by_keyword()
        time.sleep(0.4)
        if GLOBAL_SERVER_SHUTDOWN:
            break

if __name__ == "__main__":
    global GLOBAL_SERVER_SHUTDOWN
    GLOBAL_SERVER_SHUTDOWN = False
    
    threading.Thread(target=settgins_gui_timer, daemon=True).start()
    threading.Thread(target=web_server, daemon=True).start()
    
    clean_tmp_file()
    clean_extension_status()

    print("To exit web server press Ctrl + C.")
    while True:
        time.sleep(0.4)
        if GLOBAL_SERVER_SHUTDOWN:
            break
    print("Bye bye, see you next time.")
