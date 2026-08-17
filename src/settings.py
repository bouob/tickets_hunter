#!/usr/bin/env python3
#encoding=utf-8
import asyncio
import base64
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime

import tornado
from tornado.web import Application
from tornado.web import StaticFileHandler

import requests
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
    print(f"[WARNING] ddddocr module not available: {exc}")
    print("[WARNING] OCR captcha auto-solve will be disabled.")

# Get script directory for resource paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONST_APP_VERSION = "TicketsHunter (2026.08.17)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_INT28_QUIT_FILE = "MAXBOT_INT28_QUIT.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

# Phase 3 multi-instance dashboard: bot processes touch this file every few
# seconds; an instance counts as alive when its mtime is within the threshold.
# The threshold is generous because Cloudflare handling can stall the main
# loop for >10s, and a tight value would misreport a busy instance as dead.
CONST_HEARTBEAT_FILE = "heartbeat.txt"
CONST_HEARTBEAT_ALIVE_SEC = 30

CONST_SERVER_PORT = 16888

# Multi-instance profiles: each profile is a full settings.json copy
# stored under profiles/<name>.json; "default" maps to settings.json.
CONST_PROFILES_DIR = "profiles"
CONST_DEFAULT_PROFILE = "default"
CONST_PROFILE_NAME_RE = r'^[A-Za-z0-9_-]{1,32}$'

def is_valid_profile_name(profile_name):
    return bool(re.match(CONST_PROFILE_NAME_RE, profile_name))

def get_profile_filepath(profile_name):
    """Resolve a profile name to its config filepath.

    Empty string or "default" maps to the legacy settings.json so
    requests without a profile parameter keep the original behavior.
    """
    app_root = util.get_app_root()
    if not profile_name or profile_name == CONST_DEFAULT_PROFILE:
        return os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    return os.path.join(app_root, CONST_PROFILES_DIR, profile_name + ".json")

def get_instance_state_filepath(profile_name, filename):
    """Resolve a state file (pause flag, last URL...) for an instance.

    Mirrors util.get_instance_state_path() resolution in the bot process:
    default keeps legacy root paths, named instances use instances/<id>/.
    """
    app_root = util.get_app_root()
    if not profile_name or profile_name == CONST_DEFAULT_PROFILE:
        return os.path.join(app_root, filename)
    return os.path.join(app_root, "instances", profile_name, filename)

def list_profile_names():
    profiles_dir = os.path.join(util.get_app_root(), CONST_PROFILES_DIR)
    names = []
    if os.path.isdir(profiles_dir):
        for filename in sorted(os.listdir(profiles_dir)):
            stem, ext = os.path.splitext(filename)
            if ext == ".json" and is_valid_profile_name(stem):
                names.append(stem)
    return [CONST_DEFAULT_PROFILE] + names

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
CONST_SELECT_ORDER_DEFAULT = CONST_RANDOM
CONST_EXCLUDE_DEFAULT = "\"輪椅\",\"身障\",\"身心\",\"障礙\",\"愛心\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
CONST_CAPTCHA_SOUND_FILENAME_DEFAULT = "assets/sounds/ding-dong.wav"
CONST_HOMEPAGE_DEFAULT = "about:blank"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

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
    config_dict={}

    config_dict["homepage"] = CONST_HOMEPAGE_DEFAULT
    config_dict["browser"] = "chrome"
    config_dict["language"] = "English"
    config_dict["ticket_number"] = 2
    config_dict["refresh_datetime"] = ""

    config_dict["ocr_captcha"] = {}
    config_dict["ocr_captcha"]["enable"] = True
    config_dict["ocr_captcha"]["beta"] = True
    config_dict["ocr_captcha"]["force_submit"] = True
    config_dict["ocr_captcha"]["image_source"] = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
    config_dict["ocr_captcha"]["use_universal"] = True
    config_dict["ocr_captcha"]["path"] = "assets/model/universal"
    config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_NODRIVER

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
    config_dict["kktix"]["max_dwell_time"] = 90

    config_dict['cityline']={}

    config_dict['tixcraft']={}
    config_dict["tixcraft"]["pass_date_is_sold_out"] = True
    config_dict["tixcraft"]["auto_reload_coming_soon_page"] = True
    config_dict["tixcraft"]["allow_less_tickets"] = False


    # Contact information
    config_dict['contact']={}
    config_dict["contact"]["real_name"] = ""
    config_dict["contact"]["phone"] = ""
    config_dict["contact"]["credit_card_prefix"] = ""

    # Accounts section (cookies, accounts, passwords)
    config_dict['accounts']={}
    config_dict["accounts"]["tixcraft_sid"] = ""
    config_dict["accounts"]["ibonqware"] = ""
    config_dict["accounts"]["funone_session_cookie"] = ""
    config_dict["accounts"]["fansigo_cookie"] = ""
    config_dict["accounts"]["fansigo_account"] = ""
    config_dict["accounts"]["fansigo_password"] = ""
    config_dict["accounts"]["facebook_account"] = ""
    config_dict["accounts"]["kktix_account"] = ""
    config_dict["accounts"]["fami_account"] = ""
    config_dict["accounts"]["cityline_account"] = ""
    config_dict["accounts"]["urbtix_account"] = ""
    config_dict["accounts"]["hkticketing_account"] = ""
    config_dict["accounts"]["kham_account"] = ""
    config_dict["accounts"]["ticket_account"] = ""
    config_dict["accounts"]["udn_account"] = ""
    config_dict["accounts"]["ticketplus_account"] = ""

    config_dict["accounts"]["facebook_password"] = ""
    config_dict["accounts"]["kktix_password"] = ""
    config_dict["accounts"]["fami_password"] = ""
    config_dict["accounts"]["urbtix_password"] = ""
    config_dict["accounts"]["cityline_password"] = ""
    config_dict["accounts"]["hkticketing_password"] = ""
    config_dict["accounts"]["kham_password"] = ""
    config_dict["accounts"]["ticket_password"] = ""
    config_dict["accounts"]["udn_password"] = ""
    config_dict["accounts"]["ticketplus_password"] = ""

    # Advanced settings (non-credential settings only)
    config_dict['advanced']={}

    config_dict['advanced']['play_sound']={}
    config_dict["advanced"]["play_sound"]["ticket"] = True
    config_dict["advanced"]["play_sound"]["order"] = True
    config_dict["advanced"]["play_sound"]["filename"] = CONST_CAPTCHA_SOUND_FILENAME_DEFAULT

    config_dict["advanced"]["disable_adjacent_seat"] = False
    config_dict["advanced"]["hide_some_image"] = False
    config_dict["advanced"]["block_facebook_network"] = False

    config_dict["advanced"]["headless"] = False
    config_dict["advanced"]["verbose"] = False
    config_dict["advanced"]["show_timestamp"] = True
    config_dict["advanced"]["auto_guess_options"] = False
    config_dict["advanced"]["user_guess_string"] = ""
    config_dict["advanced"]["discount_code"] = ""

    # Server port for settings web interface (Issue #156)
    config_dict["advanced"]["server_port"] = CONST_SERVER_PORT
    # remote_url will be dynamically generated based on server_port
    config_dict["advanced"]["remote_url"] = ""

    config_dict["advanced"]["auto_reload_page_interval"] = 5
    config_dict["advanced"]["tixcraft_soft_block_delay"] = ""
    config_dict["advanced"]["reset_browser_interval"] = 0
    config_dict["advanced"]["proxy_server_port"] = ""
    config_dict["advanced"]["window_size"] = "600,1024"

    config_dict["advanced"]["idle_keyword"] = ""
    config_dict["advanced"]["resume_keyword"] = ""
    config_dict["advanced"]["idle_keyword_second"] = ""
    config_dict["advanced"]["resume_keyword_second"] = ""

    config_dict["advanced"]["discord_webhook_url"] = ""
    config_dict["advanced"]["discord_message"] = ""
    config_dict["advanced"]["telegram_bot_token"] = ""
    config_dict["advanced"]["telegram_chat_id"] = ""
    config_dict["advanced"]["telegram_message"] = ""

    # Keyword priority fallback (Feature 003)
    config_dict["date_auto_fallback"] = False  # default: strict mode (avoid unwanted purchases)
    config_dict["area_auto_fallback"] = False  # default: strict mode (avoid unwanted purchases)

    return config_dict

def read_last_url_from_file(profile_name=""):
    last_url_filepath = get_instance_state_filepath(profile_name, CONST_MAXBOT_LAST_URL_FILE)
    text = ""
    if os.path.exists(last_url_filepath):
        try:
            with open(last_url_filepath, "r", encoding="utf-8") as text_file:
                text = text_file.readline().strip()
        except Exception as e:
            print(f"[ERROR] Failed to read last_url from {last_url_filepath}: {e}")
    return text

def list_instance_ids():
    """Every instance the dashboard should show: all profiles (incl. default)
    plus any instances/<id>/ dir present on disk (covers CLI --instance runs
    without a matching profile json)."""
    ids = list(list_profile_names())
    instances_dir = os.path.join(util.get_app_root(), "instances")
    if os.path.isdir(instances_dir):
        for item in sorted(os.listdir(instances_dir)):
            if os.path.isdir(os.path.join(instances_dir, item)) and item not in ids:
                ids.append(item)
    return ids

def get_instance_status(profile_name):
    """Liveness/pause/last-url snapshot for one instance, mirroring the bot's
    own state-file resolution (default -> root, named -> instances/<id>/)."""
    heartbeat_filepath = get_instance_state_filepath(profile_name, CONST_HEARTBEAT_FILE)
    alive = False
    if os.path.exists(heartbeat_filepath):
        try:
            alive = (time.time() - os.path.getmtime(heartbeat_filepath)) < CONST_HEARTBEAT_ALIVE_SEC
        except Exception:
            alive = False
    paused = os.path.exists(get_instance_state_filepath(profile_name, CONST_MAXBOT_INT28_FILE))
    return {
        "id": profile_name,
        "alive": alive,
        "paused": paused,
        "last_url": read_last_url_from_file(profile_name),
    }

def migrate_config(config_dict):
    """Migrate old config structure to new structure."""
    if config_dict is None:
        return config_dict

    # Migrate ocr_model_path from advanced to ocr_captcha.path
    if "advanced" in config_dict and "ocr_model_path" in config_dict["advanced"]:
        if "ocr_captcha" not in config_dict:
            config_dict["ocr_captcha"] = {}
        if "path" not in config_dict["ocr_captcha"]:
            config_dict["ocr_captcha"]["path"] = config_dict["advanced"]["ocr_model_path"]
        del config_dict["advanced"]["ocr_model_path"]

    # Ensure ocr_captcha.path exists
    if "ocr_captcha" in config_dict and "path" not in config_dict["ocr_captcha"]:
        config_dict["ocr_captcha"]["path"] = "assets/model/universal"

    # Migrate server_port: ensure old config has this field (Issue #156)
    if "advanced" in config_dict:
        if "server_port" not in config_dict["advanced"]:
            config_dict["advanced"]["server_port"] = CONST_SERVER_PORT

    # Migrate discount_code from accounts to advanced
    if "accounts" in config_dict and "discount_code" in config_dict["accounts"]:
        if "advanced" not in config_dict:
            config_dict["advanced"] = {}
        # Only migrate if advanced.discount_code doesn't exist or is empty
        if "discount_code" not in config_dict["advanced"] or not config_dict["advanced"]["discount_code"]:
            config_dict["advanced"]["discount_code"] = config_dict["accounts"]["discount_code"]
        del config_dict["accounts"]["discount_code"]

    # Ensure advanced.discount_code exists
    if "advanced" in config_dict and "discount_code" not in config_dict["advanced"]:
        config_dict["advanced"]["discount_code"] = ""

    # Ensure all default fields exist (fills missing keys from new versions)
    default = get_default_config()
    for section in ["advanced", "kktix", "tixcraft", "date_auto_select", "area_auto_select", "ocr_captcha", "contact", "accounts", "cityline"]:
        if section in default:
            if section not in config_dict or not isinstance(config_dict[section], dict):
                config_dict[section] = dict(default[section])
            else:
                for key, value in default[section].items():
                    if key not in config_dict[section]:
                        config_dict[section][key] = value

    # Top-level scalar fields (auto-fill any missing non-section keys)
    dict_sections = {k for k, v in default.items() if isinstance(v, dict)}
    for key, value in default.items():
        if key not in dict_sections and key not in config_dict:
            config_dict[key] = value

    return config_dict

def load_json(profile_name=""):
    config_filepath = get_profile_filepath(profile_name)

    config_dict = None
    if os.path.isfile(config_filepath):
        try:
            with open(config_filepath, encoding='utf-8') as json_data:
                config_dict = json.load(json_data)
        except Exception as e:
            print(f"[ERROR] Failed to load {config_filepath}: {e}")
            print("[ERROR] Settings file may be corrupted. Using default settings.")
            config_dict = get_default_config()
    else:
        config_dict = get_default_config()

    # Apply migrations for backward compatibility
    config_dict = migrate_config(config_dict)

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

def maxbot_idle(profile_name=""):
    idle_filepath = get_instance_state_filepath(profile_name, CONST_MAXBOT_INT28_FILE)
    try:
        os.makedirs(os.path.dirname(idle_filepath), exist_ok=True)
        with open(idle_filepath, "w") as text_file:
            text_file.write("")
    except Exception as e:
        print(f"[ERROR] Failed to create idle file: {e}")

def maxbot_resume(profile_name=""):
    idle_filepath = get_instance_state_filepath(profile_name, CONST_MAXBOT_INT28_FILE)
    for i in range(3):
         util.force_remove_file(idle_filepath)

def maxbot_stop(profile_name=""):
    # Write a stop flag the bot main loop polls; on hit it runs the existing
    # clean shutdown (driver.stop + exit). Symmetric with maxbot_idle.
    stop_filepath = get_instance_state_filepath(profile_name, CONST_MAXBOT_INT28_QUIT_FILE)
    try:
        os.makedirs(os.path.dirname(stop_filepath), exist_ok=True)
        with open(stop_filepath, "w") as text_file:
            text_file.write("")
    except Exception as e:
        print(f"[ERROR] Failed to create stop file: {e}")

def launch_maxbot(profile_name="", instance_override=""):
    global launch_counter
    if "launch_counter" in globals():
        launch_counter += 1
    else:
        launch_counter = 0

    # Single point of flag cleanup: clear this instance's leftover stop/pause
    # flags so every RUN starts clean (a stale flag would otherwise instantly
    # stop or pause the freshly launched instance). instance_override (dup-RUN)
    # resolves to its own state dir, so clear that id when present.
    effective_instance = instance_override if instance_override else profile_name
    util.force_remove_file(get_instance_state_filepath(effective_instance, CONST_MAXBOT_INT28_QUIT_FILE))
    util.force_remove_file(get_instance_state_filepath(effective_instance, CONST_MAXBOT_INT28_FILE))

    config_filepath, config_dict = load_json(profile_name)

    script_name = "nodriver_tixcraft"

    # Non-default profiles launch with --input so the bot runs as that instance.
    input_filepath = ""
    if profile_name and profile_name != CONST_DEFAULT_PROFILE:
        input_filepath = config_filepath

    window_size = config_dict["advanced"]["window_size"]
    if len(window_size) > 0:
        if "," in window_size:
            size_array = window_size.split(",")
            # Older profiles may already carry an index segment; keep width,height only
            if len(size_array) > 2:
                size_array = size_array[:2]
                window_size = ",".join(size_array)
            target_width = int(size_array[0])
            target_left = target_width * launch_counter
            #print("target_left:", target_left)
            if target_left >= 1440:
                launch_counter = 0
            window_size = window_size + "," + str(launch_counter)
            #print("window_size:", window_size)

    # instance_override (dup-RUN) becomes --instance so a second instance of the
    # same profile gets its own state dir; main() prefers --instance over stem.
    threading.Thread(target=util.launch_maxbot, args=(script_name,input_filepath,"","","",window_size,), kwargs={"instance": instance_override}).start()

def change_maxbot_status_by_keyword():
    # Per-instance schedule: every profile (incl. default) pauses/resumes its
    # OWN instance using its own idle/resume keywords, so multi-open schedules
    # do not collide. maxbot_idle/resume(profile) resolve to that instance's
    # state dir. Ad-hoc / numbered instances (no profile json) are not scheduled
    # here -- their backing profile is only known to the launcher.
    system_clock_data = datetime.now()
    current_hms = system_clock_data.strftime('%H:%M:%S')
    current_sec = system_clock_data.strftime('%S')

    for profile_name in list_profile_names():
        _, config_dict = load_json(profile_name)
        advanced = config_dict.get("advanced", {})

        if len(advanced.get("idle_keyword", "")) > 0:
            if util.is_text_match_keyword(advanced["idle_keyword"], current_hms):
                maxbot_idle(profile_name)
        if len(advanced.get("resume_keyword", "")) > 0:
            if util.is_text_match_keyword(advanced["resume_keyword"], current_hms):
                maxbot_resume(profile_name)
        if len(advanced.get("idle_keyword_second", "")) > 0:
            if util.is_text_match_keyword(advanced["idle_keyword_second"], current_sec):
                maxbot_idle(profile_name)
        if len(advanced.get("resume_keyword_second", "")) > 0:
            if util.is_text_match_keyword(advanced["resume_keyword_second"], current_sec):
                maxbot_resume(profile_name)

def clean_tmp_file():
    app_root = util.get_app_root()
    remove_file_list = [CONST_MAXBOT_LAST_URL_FILE
        ,CONST_MAXBOT_INT28_FILE
        ,CONST_MAXBOT_INT28_QUIT_FILE
        ,CONST_MAXBOT_ANSWER_ONLINE_FILE
        ,CONST_MAXBOT_QUESTION_FILE
        ,CONST_HEARTBEAT_FILE
    ]
    for filename in remove_file_list:
         filepath = os.path.join(app_root, filename)
         util.force_remove_file(filepath)

    Root_Dir = util.get_app_root()
    target_folder = os.listdir(Root_Dir)
    for item in target_folder:
        if item.endswith(".tmp"):
            try:
                os.remove(os.path.join(Root_Dir, item))
            except Exception as e:
                print(f"[WARNING] Failed to remove {item}: {e}")

    # Remove orphan instance state dirs whose profile json no longer exists.
    # Note: instances launched with a custom --instance name (no matching
    # profile) lose their state dir on settings startup; CLI users should
    # name instances after their profile files.
    instances_dir = os.path.join(app_root, "instances")
    if os.path.isdir(instances_dir):
        valid_names = set(list_profile_names())
        for item in os.listdir(instances_dir):
            item_path = os.path.join(instances_dir, item)
            if os.path.isdir(item_path) and item not in valid_names:
                try:
                    shutil.rmtree(item_path)
                    print(f"[CLEANUP] Removed orphan instance dir: {item}")
                except Exception as e:
                    print(f"[WARNING] Failed to remove orphan instance dir {item}: {e}")

class NoCacheStaticFileHandler(StaticFileHandler):
    """Custom StaticFileHandler that prevents stale settings UI assets."""
    def set_extra_headers(self, path):
        # Keep settings UI assets uncached so help text and translations update immediately.
        if path in {'settings.html', 'help-content.js', 'settings.js'}:
            self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.set_header('Pragma', 'no-cache')
            self.set_header('Expires', '0')

class QuestionHandler(tornado.web.RequestHandler):
    def get(self):
        """Read the instance's MAXBOT_QUESTION.txt and return its content"""
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"exists": False, "question": "", "error": "invalid profile name"})
            return
        question_text = ""
        question_file = get_instance_state_filepath(profile_name, CONST_MAXBOT_QUESTION_FILE)

        # Check if file exists
        if os.path.exists(question_file):
            try:
                with open(question_file, "r", encoding="utf-8") as f:
                    question_text = f.read().strip()
            except Exception as e:
                print(f"Error reading question file: {e}")

        # Return JSON response
        self.write({
            "exists": os.path.exists(question_file),
            "question": question_text
        })

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
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"error": "invalid profile name"})
            return
        idle_filepath = get_instance_state_filepath(profile_name, CONST_MAXBOT_INT28_FILE)
        is_paused = os.path.exists(idle_filepath)
        url = read_last_url_from_file(profile_name)
        self.write({"status": not is_paused, "last_url": url})

class InstancesHandler(tornado.web.RequestHandler):
    """Multi-instance overview: one row per instance with liveness, pause
    state and last URL. The dashboard polls this; per-instance pause/resume
    and 'pause all' reuse the existing /pause /resume endpoints per id."""
    def get(self):
        instances = [get_instance_status(name) for name in list_instance_ids()]
        self.write({"instances": instances})

class PauseHandler(tornado.web.RequestHandler):
    def get(self):
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"pause": False, "error": "invalid profile name"})
            return
        maxbot_idle(profile_name)
        self.write({"pause": True})

class ResumeHandler(tornado.web.RequestHandler):
    def get(self):
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"resume": False, "error": "invalid profile name"})
            return
        maxbot_resume(profile_name)
        self.write({"resume": True})

class StopHandler(tornado.web.RequestHandler):
    def get(self):
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"stop": False, "error": "invalid profile name"})
            return
        maxbot_stop(profile_name)
        self.write({"stop": True})

class RunHandler(tornado.web.RequestHandler):
    def get(self):
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"run": False, "error": "invalid profile name"})
            return
        # Optional instance override: launch a second, numbered instance of the
        # same profile (dup-RUN). Validated with the same id rules.
        instance_override = self.get_query_argument("instance", "")
        if instance_override and not is_valid_profile_name(instance_override):
            self.set_status(400)
            self.write({"run": False, "error": "invalid instance name"})
            return
        display_name = instance_override or profile_name or CONST_DEFAULT_PROFILE
        print('run button pressed. profile:', display_name)
        launch_maxbot(profile_name, instance_override)
        self.write({"run": True, "profile": display_name})

class LoadJsonHandler(tornado.web.RequestHandler):
    def get(self):
        profile_name = self.get_query_argument("profile", "")
        if profile_name and not is_valid_profile_name(profile_name):
            self.set_status(400)
            self.write({"error": "invalid profile name"})
            return
        config_filepath, config_dict = load_json(profile_name)

        # Dynamically generate remote_url based on server_port (Issue #156)
        server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)
        if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
            server_port = CONST_SERVER_PORT
        config_dict["advanced"]["remote_url"] = f'"http://127.0.0.1:{server_port}/"'

        self.write(config_dict)

class ResetJsonHandler(tornado.web.RequestHandler):
    def get(self):
        # Reset only applies to the default profile; named profiles are
        # managed via /profiles (delete and recreate instead).
        profile_name = self.get_query_argument("profile", "")
        if profile_name and profile_name != CONST_DEFAULT_PROFILE:
            self.set_status(400)
            self.write({"error": "reset only supports the default profile"})
            return
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

        profile_name = self.get_query_argument("profile", "")
        if is_pass_check and profile_name and not is_valid_profile_name(profile_name):
            is_pass_check = False
            error_message = "invalid profile name"
            error_code = 1003

        if is_pass_check:
            config_filepath = get_profile_filepath(profile_name)
            os.makedirs(os.path.dirname(config_filepath), exist_ok=True)
            config_dict = _body

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

class ProfilesHandler(tornado.web.RequestHandler):
    """Manage instance profiles (full settings.json copies under profiles/)."""

    def get(self):
        # details carries each profile's homepage so the UI can show
        # platform tooltips and detect multiple KKTIX instances reliably.
        details = []
        for name in list_profile_names():
            homepage = ""
            try:
                with open(get_profile_filepath(name), encoding='utf-8') as json_data:
                    homepage = json.load(json_data).get("homepage", "")
            except Exception:
                pass
            details.append({"name": name, "homepage": homepage})
        self.write({"profiles": [d["name"] for d in details], "details": details})

    def post(self):
        """Create a new profile. Body: {"name": "...", "config": {...}}
        config is optional; falls back to current settings.json content."""
        try:
            _body = json.loads(self.request.body)
        except Exception:
            self.set_status(400)
            self.write({"success": False, "error": "wrong json format"})
            return

        profile_name = _body.get("name", "")
        if not is_valid_profile_name(profile_name) or profile_name == CONST_DEFAULT_PROFILE:
            self.set_status(400)
            self.write({"success": False, "error": "invalid profile name (allowed: A-Z a-z 0-9 _ -, max 32 chars)"})
            return

        config_filepath = get_profile_filepath(profile_name)
        if os.path.exists(config_filepath):
            self.set_status(409)
            self.write({"success": False, "error": "profile already exists"})
            return

        config_dict = _body.get("config")
        if not isinstance(config_dict, dict):
            _, config_dict = load_json()
        config_dict = migrate_config(config_dict)

        os.makedirs(os.path.dirname(config_filepath), exist_ok=True)
        util.save_json(config_dict, config_filepath)
        self.write({"success": True, "profile": profile_name})

    def delete(self):
        profile_name = self.get_query_argument("profile", "")
        if not is_valid_profile_name(profile_name) or profile_name == CONST_DEFAULT_PROFILE:
            self.set_status(400)
            self.write({"success": False, "error": "invalid profile name"})
            return
        config_filepath = get_profile_filepath(profile_name)
        if not os.path.exists(config_filepath):
            self.set_status(404)
            self.write({"success": False, "error": "profile not found"})
            return
        try:
            os.remove(config_filepath)
        except Exception as exc:
            self.set_status(500)
            self.write({"success": False, "error": str(exc)})
            return
        self.write({"success": True})

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
                tmp_file = _body["token"] + ".tmp"
                config_filepath = os.path.join(app_root, tmp_file)
                util.save_json(_body, config_filepath)

        self.write({"return": True})

class TestDiscordWebhookHandler(tornado.web.RequestHandler):
    ALLOWED_HOSTS = ("discord.com", "discordapp.com")

    def post(self):
        try:
            body = json.loads(self.request.body)
        except Exception:
            self.write({"success": False, "message": "wrong json format"})
            return

        webhook_url = body.get("webhook_url", "").strip()
        if not webhook_url:
            self.write({"success": False, "message": "webhook URL is empty"})
            return

        from urllib.parse import urlparse
        try:
            parsed = urlparse(webhook_url)
        except Exception:
            self.write({"success": False, "message": "invalid URL format"})
            return

        if parsed.scheme != "https":
            self.write({"success": False, "message": "only HTTPS URLs are allowed"})
            return

        if not any(parsed.netloc == host or parsed.netloc.endswith("." + host) for host in self.ALLOWED_HOSTS):
            self.write({"success": False, "message": "only Discord webhook URLs are allowed"})
            return

        if not parsed.path.startswith("/api/webhooks/"):
            self.write({"success": False, "message": "invalid Discord webhook URL format"})
            return

        _, config_dict = load_json()
        debug = util.create_debug_logger(config_dict)

        custom_message = body.get("custom_message", "").strip()
        content = custom_message if custom_message else "[Test] Tickets Hunter webhook test successful!"
        payload = {
            "content": content,
            "username": "Tickets Hunter"
        }
        try:
            response = requests.post(webhook_url, json=payload, timeout=5.0)
            if response.status_code in (200, 204):
                debug.log("[Discord Webhook] Test OK")
                self.write({"success": True, "message": "ok"})
            else:
                debug.log("[Discord Webhook] Test failed: HTTP %d" % response.status_code)
                self.write({"success": False, "message": "HTTP %d" % response.status_code})
        except Exception as exc:
            debug.log("[Discord Webhook] Test failed: %s" % str(exc))
            self.write({"success": False, "message": str(exc)})

class TestTelegramHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
        except Exception:
            self.write({"success": False, "message": "wrong json format"})
            return

        bot_token = body.get("bot_token", "").strip()
        chat_id = body.get("chat_id", "").strip()

        if not bot_token:
            self.write({"success": False, "message": "Bot Token is empty"})
            return

        import re
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', bot_token):
            self.write({"success": False, "message": "Bot Token format invalid"})
            return

        if not chat_id:
            self.write({"success": False, "message": "Chat ID is empty"})
            return

        chat_ids = [cid.strip() for cid in chat_id.split(",") if cid.strip()]
        if not chat_ids:
            self.write({"success": False, "message": "Chat ID is empty"})
            return

        invalid_ids = [cid for cid in chat_ids if not re.match(r'^-?\d+$', cid)]
        if invalid_ids:
            self.write({"success": False, "message": "Chat ID format invalid: %s" % ", ".join(invalid_ids)})
            return

        _, config_dict = load_json()
        debug = util.create_debug_logger(config_dict)

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        custom_message = body.get("custom_message", "").strip()
        text = custom_message if custom_message else "[Test] Tickets Hunter Telegram test successful!"
        errors = []
        ok_count = 0
        for cid in chat_ids:
            try:
                payload = {"chat_id": cid, "text": text}
                response = requests.post(url, json=payload, timeout=5.0)
                result = response.json()
                if response.status_code == 200 and result.get("ok", False):
                    ok_count += 1
                else:
                    desc = result.get("description", "HTTP %d" % response.status_code)
                    errors.append(f"{cid}: {desc}")
            except (requests.RequestException, ValueError) as exc:
                safe_msg = str(exc).replace(bot_token, "***") if bot_token else str(exc)
                errors.append(f"{cid}: {safe_msg}")

        if ok_count == len(chat_ids):
            debug.log("[Telegram] Test OK (%d chat(s))" % ok_count)
            self.write({"success": True, "message": "ok"})
        elif ok_count > 0:
            debug.log("[Telegram] Test partial: %d/%d OK" % (ok_count, len(chat_ids)))
            self.write({"success": True, "message": "%d/%d OK, errors: %s" % (ok_count, len(chat_ids), "; ".join(errors))})
        else:
            msg = "; ".join(errors)
            debug.log("[Telegram] Test failed: %s" % msg)
            self.write({"success": False, "message": msg})

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
            # Remove any existing quotes first
            user_input = user_input.replace('"', '').replace("'", '')

            # Add quotes to each keyword
            # Use semicolon as the ONLY delimiter (Issue #23)
            if util.CONST_KEYWORD_DELIMITER in user_input:
                items = user_input.split(util.CONST_KEYWORD_DELIMITER)
                user_input = ','.join([f'"{item.strip()}"' for item in items if item.strip()])
            else:
                user_input = f'"{user_input.strip()}"'
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
        ("/sendkey", SendkeyHandler),

        # status api
        ("/status", StatusHandler),
        ("/instances", InstancesHandler),
        ("/pause", PauseHandler),
        ("/resume", ResumeHandler),
        ("/stop", StopHandler),
        ("/run", RunHandler),
        
        # json api
        ("/load", LoadJsonHandler),
        ("/save", SaveJsonHandler),
        ("/reset", ResetJsonHandler),
        ("/profiles", ProfilesHandler),

        ("/test_discord_webhook", TestDiscordWebhookHandler),
        ("/test_telegram", TestTelegramHandler),
        ("/ocr", OcrHandler),
        ("/query", QueryHandler),
        ("/question", QuestionHandler),
        ('/(.*)', NoCacheStaticFileHandler, {"path": os.path.join(SCRIPT_DIR, 'www')}),
    ])
    app.ocr = ocr;
    app.version = CONST_APP_VERSION;

    # Get server_port from config, fallback to default (Issue #156)
    _, config_dict = load_json()
    server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)

    # Validate port range
    if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
        print(f"[WARNING] Invalid server_port: {server_port}, using default: {CONST_SERVER_PORT}")
        server_port = CONST_SERVER_PORT

    app.listen(server_port)
    print("server running on port:", server_port)

    url = "http://127.0.0.1:" + str(server_port) + "/settings.html"
    print("goto url:", url)
    webbrowser.open_new(url)
    await asyncio.Event().wait()

def get_server_port():
    """Get server port from config file, fallback to default."""
    _, config_dict = load_json()
    server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)
    if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
        server_port = CONST_SERVER_PORT
    return server_port

def web_server():
    server_port = get_server_port()
    is_port_binded = util.is_connectable(server_port)
    #print("is_port_binded:", is_port_binded)
    if not is_port_binded:
        asyncio.run(main_server())
    else:
        print("port:", server_port, " is in used.")

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

    print("To exit web server press Ctrl + C.")
    while True:
        time.sleep(0.4)
        if GLOBAL_SERVER_SHUTDOWN:
            break
    print("Bye bye, see you next time.")
