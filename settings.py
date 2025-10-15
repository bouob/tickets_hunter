#!/usr/bin/env python3
#encoding=utf-8
import asyncio
import base64
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from typing import (Any, Awaitable, Callable, Dict, Generator, Iterable, List,
                    Optional, Tuple, Type, TypeVar, Union, cast, overload)

import tornado
from tornado.web import Application, StaticFileHandler

import util

try:
    import ddddocr
except Exception as exc:
    pass

CONST_APP_VERSION = "TicketsHunter (2025.10.01)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_EXTENSION_STATUS_JSON = "status.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"

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
URL_RELEASE = 'https://github.com/bouob/tickets_hunter/releases'
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'
URL_FIREFOX_DRIVER = 'https://github.com/mozilla/geckodriver/releases'
URL_EDGE_DRIVER = 'https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/'


def get_default_config():
    CONST_SERVER_PORT = 16888
    CONST_HOMEPAGE_DEFAULT = "about:blank"
    CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"
    CONST_SELECT_ORDER_DEFAULT = CONST_RANDOM
    CONST_EXCLUDE_DEFAULT = "\"輪椅\",\"身障\",\"身心 障礙\",\"Restricted View\",\"Wheelchair\",\"燈柱遮蔽\",\"視線不完整\",\"博愛\""
    CONST_CAPTCHA_SOUND_FILENAME_DEFAULT = "ding-dong.wav"

    config_dict = {
        "homepage": CONST_HOMEPAGE_DEFAULT,
        "browser": "chrome",
        "language": "English",
        "ticket_number": 2,
        "refresh_datetime": "",
        "port": CONST_SERVER_PORT,
        "ocr_captcha": {
            "enable": True,
            "beta": True,
            "force_submit": True,
            "image_source": CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS,
        },
        "webdriver_type": CONST_WEBDRIVER_TYPE_UC,
        "date_auto_select": {
            "enable": True,
            "date_keyword": "",
            "mode": CONST_SELECT_ORDER_DEFAULT,
        },
        "area_auto_select": {
            "enable": True,
            "mode": CONST_SELECT_ORDER_DEFAULT,
            "area_keyword": "",
        },
        "keyword_exclude": CONST_EXCLUDE_DEFAULT,
        "kktix": {
            "auto_press_next_step_button": True,
            "auto_fill_ticket_number": True,
            "max_dwell_time": 90,
        },
        "cityline": {
            "cityline_queue_retry": True,
        },
        "tixcraft": {
            "pass_date_is_sold_out": True,
            "auto_reload_coming_soon_page": True,
        },
        "advanced": {
            "play_sound": {
                "ticket": True,
                "order": True,
                "filename": CONST_CAPTCHA_SOUND_FILENAME_DEFAULT,
            },
            "email": {
                "ticket": True,
                "order": True,
                "apppassword": "",
                "sender_email": "",
                "receiver_email": "",
                "subject": "號外",
                "message": "這是一封寫給自己的信。",
            },
            "tixcraft_sid": "",
            "ibonqware": "",
            "facebook_account": "",
            "kktix_account": "",
            "fami_account": "",
            "cityline_account": "",
            "urbtix_account": "",
            "hkticketing_account": "",
            "kham_account": "",
            "ticket_account": "",
            "udn_account": "",
            "ticketplus_account": "",
            "facebook_password": "",
            "kktix_password": "",
            "fami_password": "",
            "urbtix_password": "",
            "cityline_password": "",
            "hkticketing_password": "",
            "kham_password": "",
            "ticket_password": "",
            "udn_password": "",
            "ticketplus_password": "",
            "facebook_password_plaintext": "",
            "kktix_password_plaintext": "",
            "fami_password_plaintext": "",
            "urbtix_password_plaintext": "",
            "cityline_password_plaintext": "",
            "hkticketing_password_plaintext": "",
            "kham_password_plaintext": "",
            "ticket_password_plaintext": "",
            "udn_password_plaintext": "",
            "ticketplus_password_plaintext": "",
            "chrome_extension": True,
            "disable_adjacent_seat": False,
            "adblock": True,
            "hide_some_image": False,
            "block_facebook_network": False,
            "headless": False,
            "verbose": False,
            "auto_guess_options": False,
            "user_guess_string": "",
            "remote_url": f"http://127.0.0.1:{CONST_SERVER_PORT}/",
            "auto_reload_page_interval": 3.0,
            "auto_reload_overheat_count": 4,
            "auto_reload_overheat_cd": 1.0,
            "reset_browser_interval": 0,
            "proxy_server_port": "",
            "window_size": "600,1024",
            "idle_keyword": "",
            "resume_keyword": "",
            "idle_keyword_second": "",
            "resume_keyword_second": "",
        },
    }
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
    config_dict["advanced"]["facebook_password"] = util.decrypt_me(config_dict["advanced"]["facebook_password"])
    config_dict["advanced"]["kktix_password"] = util.decrypt_me(config_dict["advanced"]["kktix_password"])
    config_dict["advanced"]["fami_password"] = util.decrypt_me(config_dict["advanced"]["fami_password"])
    config_dict["advanced"]["cityline_password"] = util.decrypt_me(config_dict["advanced"]["cityline_password"])
    config_dict["advanced"]["urbtix_password"] = util.decrypt_me(config_dict["advanced"]["urbtix_password"])
    config_dict["advanced"]["hkticketing_password"] = util.decrypt_me(config_dict["advanced"]["hkticketing_password"])
    config_dict["advanced"]["kham_password"] = util.decrypt_me(config_dict["advanced"]["kham_password"])
    config_dict["advanced"]["ticket_password"] = util.decrypt_me(config_dict["advanced"]["ticket_password"])
    config_dict["advanced"]["udn_password"] = util.decrypt_me(config_dict["advanced"]["udn_password"])
    config_dict["advanced"]["ticketplus_password"] = util.decrypt_me(config_dict["advanced"]["ticketplus_password"])
    return config_dict

def encrypt_password(config_dict):
    config_dict["advanced"]["facebook_password"] = util.encrypt_me(config_dict["advanced"]["facebook_password"])
    config_dict["advanced"]["kktix_password"] = util.encrypt_me(config_dict["advanced"]["kktix_password"])
    config_dict["advanced"]["fami_password"] = util.encrypt_me(config_dict["advanced"]["fami_password"])
    config_dict["advanced"]["cityline_password"] = util.encrypt_me(config_dict["advanced"]["cityline_password"])
    config_dict["advanced"]["urbtix_password"] = util.encrypt_me(config_dict["advanced"]["urbtix_password"])
    config_dict["advanced"]["hkticketing_password"] = util.encrypt_me(config_dict["advanced"]["hkticketing_password"])
    config_dict["advanced"]["kham_password"] = util.encrypt_me(config_dict["advanced"]["kham_password"])
    config_dict["advanced"]["ticket_password"] = util.encrypt_me(config_dict["advanced"]["ticket_password"])
    config_dict["advanced"]["udn_password"] = util.encrypt_me(config_dict["advanced"]["udn_password"])
    config_dict["advanced"]["ticketplus_password"] = util.encrypt_me(config_dict["advanced"]["ticketplus_password"])
    return config_dict

def maxbot_idle():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    try:
        with open(idle_filepath, "w") as text_file:
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
    app_root = util.get_app_root()
    webdriver_path = os.path.join(app_root, "webdriver")
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
    app_root = util.get_app_root()
    webdriver_path = os.path.join(app_root, "webdriver")
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

    app_root = util.get_app_root()
    target_folder_list = os.listdir(app_root)
    for item in target_folder_list:
        if item.endswith(".tmp"):
            os.remove(os.path.join(app_root, item))

    # clean generated ext.
    webdriver_folder = os.path.join(app_root, "webdriver")
    target_folder_list = os.listdir(webdriver_folder)
    for item in target_folder_list:
        if item.startswith("tmp_"):
            try:
                shutil.rmtree(os.path.join(webdriver_folder, item))
            except Exception as exc:
                print(exc)
                pass

class QuestionHandler(tornado.web.RequestHandler):
    def get(self):
        global txt_question
        txt_question.insert("1.0", "")

class HomepageHandler(tornado.web.RequestHandler):
    def get(self):
        app_root = util.get_app_root()
        web_folder = os.path.join(app_root, "www")
        html_path = os.path.join(web_folder, "settings.html")
        if os.path.exists(html_path):
            self.render(html_path)

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
        app_root = util.get_app_root()
        status_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
        if os.path.exists(status_filepath):
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

class SendkeyHandler(tornado.web.RequestHandler):
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

        if is_pass_check:
            app_root = util.get_app_root()
            if "token" in _body:
                tmp_file = _body["token"] + "_sendkey.tmp"
                config_filepath = os.path.join(app_root, tmp_file)
                util.save_json(_body, config_filepath)

        self.write({"return": True})

class EvalHandler(tornado.web.RequestHandler):
    def post(self):
        #print("SendkeyHandler")
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

        if is_pass_check:
            app_root = util.get_app_root()
            if "token" in _body:
                tmp_file = _body["token"] + "_eval.tmp"
                config_filepath = os.path.join(app_root, tmp_file)
                #print("tmp_file:", config_filepath)
                util.save_json(_body, config_filepath)

        self.write({"return": True})

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
            # 新增：偵測並轉換簡化格式
            if ',' in user_input and not '"' in user_input:
                items = user_input.split(',')
                user_input = ','.join([f'"{item.strip()}"' for item in items])
                return user_input  # 已經是正確格式，直接返回

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

async def main_server(server_port):
    ocr = None
    try:
        ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    except Exception as exc:
        print(exc)
        pass

    app = Application([
        ("/", HomepageHandler),
        ("/version", VersionHandler),
        ("/shutdown", ShutdownHandler),
        ("/sendkey", SendkeyHandler),
        ("/eval", EvalHandler),

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
    app.ocr = ocr
    app.version = CONST_APP_VERSION

    app.listen(server_port)
    print("server running on port:", server_port)

    url="http://127.0.0.1:" + str(server_port) + "/"
    print("goto url:", url)
    webbrowser.open_new(url)
    await asyncio.Event().wait()

def web_server():
    _, config_dict = load_json()
    server_port = config_dict["port"]

    is_port_binded = util.is_connectable(server_port)
    #print("is_port_binded:", is_port_binded)
    if not is_port_binded:
        asyncio.run(main_server(server_port))
    else:
        print("port:", server_port, " is in used. 已有其他程式占用 web server 的連接埠.")

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
