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
# 適用於所有輸出環境（終端、IDE、重定向、管道）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import zendriver as uc
from zendriver import cdp
from urllib3.exceptions import InsecureRequestWarning
import urllib.parse

import util
import settings
from NonBrowser import NonBrowser

try:
    import ddddocr
except Exception as exc:
    print(exc)
    pass

from nodriver_common import *
from platforms.facebook import *
from platforms.fansigo import *
from platforms.cityline import *
from platforms.famiticket import *
from platforms.ticketplus import *
from platforms.funone import *
from platforms.kktix import *
from platforms.tixcraft import *
from platforms.ibon import *
from platforms.kham import *
from platforms.hkticketing import *

CONST_CITYLINE_SIGN_IN_URL = "https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2Fwww.cityline.com%2FEvents.html"
CONST_FAMI_SIGN_IN_URL = "https://www.famiticket.com.tw/Home/User/SignIn"
CONST_HKTICKETING_SIGN_IN_URL = "https://premier.hkticketing.com/Secure/ShowLogin.aspx"
CONST_HKTICKETING_TYPE02_SIGN_IN_URL = "https://hkt.hkticketing.com/hant/#/login"
CONST_KHAM_SIGN_IN_URL = "https://kham.com.tw/application/UTK13/UTK1306_.aspx"
CONST_KKTIX_SIGN_IN_URL = "https://kktix.com/users/sign_in?back_to=%s"
CONST_TICKET_SIGN_IN_URL = "https://ticket.com.tw/application/utk13/utk1306_.aspx"
CONST_UDN_SIGN_IN_URL = "https://tickets.udnfunlife.com/application/UTK01/UTK0101_.aspx"
CONST_URBTIX_SIGN_IN_URL = "https://www.urbtix.hk/member-login"

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig()
logger = logging.getLogger('logger')


async def nodriver_goto_homepage(driver, config_dict):
    debug = util.create_debug_logger(config_dict)
    tab = None
    homepage = config_dict["homepage"]
    if 'kktix.c' in homepage:
        # for like human.
        try:
            tab = await driver.get(homepage)
            await asyncio.sleep(random.uniform(1.0, 2.5))
        except Exception as e:
            print(f"[ERROR] Failed to navigate to kktix homepage: {e}")

        if len(config_dict["accounts"]["kktix_account"])>0:
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

    if 'udnfunlife.com' in homepage:
        if len(config_dict["accounts"]["udn_account"])>0:
            homepage = CONST_UDN_SIGN_IN_URL

    if 'urbtix.hk' in homepage:
        if len(config_dict["accounts"]["urbtix_account"])>0:
            homepage = CONST_URBTIX_SIGN_IN_URL

    if 'cityline.com' in homepage:
        if len(config_dict["accounts"]["cityline_account"])>0:
            homepage = CONST_CITYLINE_SIGN_IN_URL

    if 'hkticketing.com' in homepage:
        if len(config_dict["accounts"]["hkticketing_account"])>0:
            if 'hkt.hkticketing.com' in homepage:
                # Type02: hkt.hkticketing.com SPA
                homepage = CONST_HKTICKETING_TYPE02_SIGN_IN_URL
            else:
                # Type01: premier.hkticketing.com
                homepage = CONST_HKTICKETING_SIGN_IN_URL

    # https://ticketplus.com.tw/*
    if 'ticketplus.com.tw' in homepage:
        if len(config_dict["accounts"]["ticketplus_account"]) > 1:
            homepage = "https://ticketplus.com.tw/"

    try:
        tab = await driver.get(homepage)
        await asyncio.sleep(random.uniform(1.0, 2.5))
    except Exception as e:
        print(f"[ERROR] Failed to navigate to homepage: {e}")

    tixcraft_family = False
    if 'tixcraft.com' in homepage:
        tixcraft_family = True

    if 'indievox.com' in homepage:
        tixcraft_family = True

    if 'ticketmaster.' in homepage:
        tixcraft_family = True

    if tixcraft_family:
        # Determine correct cookie domain and name based on homepage
        # Each site uses different session cookie names (Issue #207)
        if 'ticketmaster.sg' in homepage:
            cookie_domain = "ticketmaster.sg"
            cookie_name = "TIXPUISID"
        elif 'ticketmaster.com' in homepage:
            cookie_domain = ".ticketmaster.com"
            cookie_name = "TIXUISID"
        elif 'indievox.com' in homepage:
            cookie_domain = "www.indievox.com"
            cookie_name = "IVUISID"
        else:
            cookie_domain = ".tixcraft.com"
            cookie_name = "TIXUISID"

        tixcraft_sid = config_dict["accounts"]["tixcraft_sid"]
        if len(tixcraft_sid) > 1:
            debug.log(f"[TIXCRAFT] Setting {cookie_name} cookie, length: {len(tixcraft_sid)}")

            try:
                # Step 1: Delete existing cookies (both legacy SID and session cookie)
                try:
                    await tab.send(cdp.network.delete_cookies(
                        name="SID",
                        domain=cookie_domain
                    ))
                    await tab.send(cdp.network.delete_cookies(
                        name=cookie_name,
                        domain=cookie_domain
                    ))
                    # Delete cookies from alternate domain to avoid conflicts
                    if 'indievox.com' in homepage:
                        await tab.send(cdp.network.delete_cookies(
                            name=cookie_name,
                            domain=".indievox.com"
                        ))
                    if 'ticketmaster.sg' in homepage:
                        await tab.send(cdp.network.delete_cookies(
                            name=cookie_name,
                            domain=".ticketmaster.sg"
                        ))
                    debug.log(f"[TIXCRAFT] Deleted existing SID and {cookie_name} cookies for domain: {cookie_domain}")
                except Exception as del_e:
                    debug.log(f"[TIXCRAFT] Note: Could not delete existing cookies: {del_e}")

                # Step 2: Set new session cookie using CDP
                cookie_result = await tab.send(cdp.network.set_cookie(
                    name=cookie_name,
                    value=tixcraft_sid,
                    domain=cookie_domain,
                    path="/",
                    secure=True,
                    http_only=True
                ))

                debug.log(f"[TIXCRAFT] CDP setCookie result: {cookie_result}")
                debug.log(f"[TIXCRAFT] {cookie_name} cookie set successfully")

                # Verify cookie was set
                updated_cookies = await driver.cookies.get_all()
                sid_cookies = [c for c in updated_cookies if c.name == cookie_name]
                if not sid_cookies:
                    debug.log(f"[TIXCRAFT] Warning: {cookie_name} cookie not found after setting")
                else:
                    debug.log(f"[TIXCRAFT] Verified {cookie_name} cookie: domain={sid_cookies[0].domain}, value length={len(sid_cookies[0].value)}")

            except Exception as e:
                debug.log(f"[TIXCRAFT] Error setting {cookie_name} cookie: {str(e)}")
                import traceback
                traceback.print_exc()
                debug.log("[TIXCRAFT] Falling back to old method...")

                # Fallback to old method if CDP fails
                cookies = await driver.cookies.get_all()
                # Filter out all existing SID and session cookies to avoid conflicts
                cookies_filtered = [c for c in cookies if c.name not in ('SID', cookie_name)]
                # Create new session cookie with correct attributes (Issue #144, #207)
                new_cookie = cdp.network.CookieParam(
                    cookie_name,
                    tixcraft_sid,
                    domain=cookie_domain,
                    path="/",
                    http_only=True,
                    secure=True
                )
                cookies_filtered.append(new_cookie)
                await driver.cookies.set_all(cookies_filtered)

                debug.log(f"[TIXCRAFT] {cookie_name} cookie set successfully (fallback method)")

    if 'ibon.com' in homepage:
        # Special handling for tour.ibon.com.tw:
        # Need to visit ticket.ibon.com.tw first to complete OAuth and get _at_e token
        is_tour_ibon = 'tour.ibon.com.tw' in homepage
        original_homepage = homepage

        if is_tour_ibon:
            debug.log("[TOUR IBON] Detected tour.ibon.com.tw homepage")
            debug.log("[TOUR IBON] Step 1: Visiting ticket.ibon.com.tw first for OAuth...")

            # Step 1: Visit ticket.ibon.com.tw homepage first
            try:
                tab = await driver.get("https://ticket.ibon.com.tw/")
                await asyncio.sleep(random.uniform(1.5, 2.5))
            except Exception as e:
                debug.log(f"[TOUR IBON] Error visiting ticket.ibon.com.tw: {e}")

        # Step 2: Set ibon cookie
        login_result = await nodriver_ibon_login(tab, config_dict, driver)

        if login_result['success']:
            debug.log("[IBON] login process completed successfully")
        else:
            debug.log(f"[IBON] login process failed: {login_result.get('reason', 'unknown')}")
            if 'error' in login_result:
                debug.log(f"[IBON] Error details: {login_result['error']}")

        # Step 3: For tour.ibon.com.tw, navigate to original homepage after OAuth
        if is_tour_ibon:
            debug.log(f"[TOUR IBON] Step 2: Navigating to tour.ibon homepage: {original_homepage}")

            try:
                tab = await driver.get(original_homepage)
                await asyncio.sleep(random.uniform(1.5, 2.5))
            except Exception as e:
                debug.log(f"[TOUR IBON] Error navigating to tour.ibon homepage: {e}")

        # 不管成功與否，都繼續後續處理，讓使用者手動處理登入問題
        # 這樣可以避免完全中斷搶票流程

    # FunOne cookie injection (same pattern as TixCraft/iBon)
    if 'tickets.funone.io' in homepage:
        funone_cookie = config_dict["accounts"].get("funone_session_cookie", "").strip()
        if len(funone_cookie) > 1:
            debug.log(f"[FUNONE] Setting ticket_session cookie, length: {len(funone_cookie)}")

            try:
                # Set ticket_session cookie using CDP
                await tab.send(cdp.network.set_cookie(
                    name="ticket_session",
                    value=funone_cookie,
                    domain="tickets.funone.io",
                    path="/",
                    secure=False,
                    http_only=True
                ))

                debug.log("[FUNONE] ticket_session cookie set successfully")

                # Verify cookie was set
                updated_cookies = await driver.cookies.get_all()
                funone_cookies = [c for c in updated_cookies if c.name == 'ticket_session']
                if funone_cookies:
                    debug.log(f"[FUNONE] Verified cookie: domain={funone_cookies[0].domain}, value length={len(funone_cookies[0].value)}")

                    # Reload page to apply cookie
                    debug.log("[FUNONE] Reloading page to apply cookie...")
                    await tab.reload()
                    await asyncio.sleep(1.5)
                else:
                    debug.log("[FUNONE] Warning: ticket_session cookie not found after setting")

            except Exception as e:
                debug.log(f"[FUNONE] Error setting cookie: {str(e)}")

    return tab

async def nodrver_block_urls(tab, config_dict):
    """
    Block unnecessary network requests for performance and privacy

    Strategy for Cityline:
    - Allow: others.min.js (required for buy button and _global_citylineWebBase)
    - Block: Analytics/tracking requests initiated by others.min.js

    Strategy for TicketPlus:
    - Allow: analytics beacons (Clarity, GA, GTM) so the server sees normal user behavior
    - Blocking these signals causes server-side detection (empty DOM / honeypot data)
    """
    # Determine target platform from homepage URL
    homepage = config_dict.get("homepage", "")
    is_ticketplus = 'ticketplus.com.tw' in homepage

    NETWORK_BLOCKED_URLS = [
        # General tracking and analytics
        # Note: TicketPlus-specific trackers (clarity.ms, google-analytics, googletagmanager)
        # are excluded below to avoid server-side bot detection via missing beacons
        '*.appier.net/*',
        '*.c.appier.net/*',
        '*.cloudfront.com/*',
        '*.doubleclick.net/*',  # Covers securepubads.g.doubleclick.net
        '*.lndata.com/*',
        '*.rollbar.com/*',
        '*.smartlook.com/*',
        '*anymind360.com/*',  # Block Anymind360 tracking (loaded by cityline others.min.js)
        '*cdn.cookielaw.org/*',
        '*e2elog.fetnet.net*',
        '*fundingchoicesmessages.google.com/*',

        # Facebook Pixel tracking (does not affect FB login)
        '*connect.facebook.net/*/fbevents.js',
        '*connect.facebook.net/signals/*',

        # Google tracking (broad patterns cover specific URLs)
        '*google-analytics.*',  # Covers www.google-analytics.com/analytics.js & collect
        '*googlesyndication.*',  # Covers pagead2.googlesyndication.com
        '*googletagmanager.*',  # Covers www.googletagmanager.com/gtag/js
        '*googletagservices.*',
        '*googleadservices.com/*',  # Ad conversion tracking
        '*adtrafficquality.google/*',  # Ad quality detection

        # GA4
        '*analytics.google.com/*',

        # Social media and video
        '*.twitter.com/i/*',
        '*platform.twitter.com/*',
        '*syndication.twitter.com/*',
        '*youtube.com/*',
        '*player.youku.*',
        '*play.google.com/*',

        # Ad scripts
        '*/adblock.js',
        '*/google_ad_block.js',
        '*img.uniicreative.com/*',

        # Cityline: Allow others.min.js (required for buy button), block tracking only
        # '*cityline.com/js/others.min.js',  # DISABLED: Required for buy button rendering

        # Ticketmaster ad scripts
        '*ticketmaster.sg/js/adblock*',
        '*ticketmaster.sg/js/ads.js*',
        #'*ticketmaster.sg/epsf/asset/eps.js*',
        #'*ticketmaster.sg/epsf/asset/eps-gec.js',
        #'*ticketmaster.sg/epsf/asset/eps-mgr',
        '*ticketmaster.com/js/ads.js*',
        '*ticketmaster.com/epsf/asset/eps.js*',

        # Cloudflare analytics (KKTIX)
        '*static.cloudflareinsights.com/*',

        # Chat widgets (not needed for ticket purchase)
        '*chat.botbonnie.com/*',
        '*asset.botbonnie.com/*',
        '*web-chat-service.project.imbee.io/*',
        '*web-chat-assets.imbee.io/*',

        # Cookie consent geolocation
        '*geolocation.onetrust.com/*',
    ]

    # Block Clarity for non-TicketPlus platforms only
    # TicketPlus server-side detection requires real Clarity beacons; blocking causes honeypot session data
    if not is_ticketplus:
        NETWORK_BLOCKED_URLS.append('*.clarity.ms/*')

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
        # Removed: '*static.ticketplus.com.tw/event/*' was blocking Vue JS/API resources needed for SPA rendering

        #NETWORK_BLOCKED_URLS.append('https://kktix.cc/change_locale?locale=*')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/logo_*.png')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/assets/icon-*.png')
        NETWORK_BLOCKED_URLS.append('https://t.kfs.io/upload_images/*.jpg')

    if config_dict["advanced"]["block_facebook_network"]:
        NETWORK_BLOCKED_URLS.append('*facebook.com/*')
        NETWORK_BLOCKED_URLS.append('*.fbcdn.net/*')

    try:
        await tab.send(cdp.network.enable())
        # Block unnecessary network requests for performance optimization
        await tab.send(cdp.network.set_blocked_ur_ls(urls=NETWORK_BLOCKED_URLS))
    except Exception as exc:
        print(f"Warning: Failed to enable network blocking: {exc}")
        # Continue without network blocking if it fails

    # TicketPlus: clarity.ms is unblocked above; stub injection no longer needed
    # if is_ticketplus:
    #     await _inject_clarity_stub_for_ticketplus(tab)

    return tab


async def _inject_clarity_stub_for_ticketplus(tab):
    """
    Simulate Microsoft Clarity presence for TicketPlus without loading the real script.
    Injects a window.clarity queue stub so the Clarity tag script proceeds normally.
    Do NOT set .v or .t: tag script checks 'if (clarity.v || clarity.t) return early',
    so setting .v would prevent clarity.js from loading and no beacon would be sent.
    """
    # window.clarity stub: queue function only, lets tag script load clarity.js and send beacons
    clarity_stub_js = """(function() {
        if (typeof window.clarity === 'undefined') {
            var _cq = [];
            window.clarity = function() { _cq.push(arguments); };
            window.clarity.q = _cq;
        }
    })();"""
    try:
        await tab.send(cdp.page.add_script_to_evaluate_on_new_document(source=clarity_stub_js))
    except Exception as exc:
        print(f"[TicketPlus] Warning: Failed to inject Clarity stub: {exc}")



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

async def reload_config(config_dict, last_mtime):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    if not os.path.exists(config_filepath):
        return config_dict, last_mtime

    try:
        current_mtime = os.path.getmtime(config_filepath)
        if current_mtime > last_mtime:
            await asyncio.sleep(0.1)
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
                        "discord_webhook_url", "telegram_bot_token", "telegram_chat_id",
                        "discount_code"
                    ]
                    for field in adv_fields:
                        if field in new_config["advanced"]:
                            config_dict["advanced"][field] = new_config["advanced"][field]

                print("Configuration reloaded from settings.json")
                return config_dict, current_mtime
    except Exception as e:
        print(f"[WARNING] Failed to reload config: {e}")

    return config_dict, last_mtime

async def main(args):
    config_dict = get_config_dict(args)

    # Global timestamp: override builtins.print to prepend [HH:MM:SS]
    if config_dict and config_dict.get("advanced", {}).get("show_timestamp", False):
        import builtins
        _original_print = builtins.print
        def _timestamped_print(*args_p, **kwargs_p):
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            _original_print(timestamp, *args_p, **kwargs_p)
        builtins.print = _timestamped_print

    driver = None
    tab = None
    if not config_dict is None:
        sandbox = False
        conf = get_extension_config(config_dict, args)
        nodriver_overwrite_prefs(conf)
        # PS: nodrirver run twice always cause error:
        # Failed to connect to browser
        # One of the causes could be when you are running as root.
        # In that case you need to pass no_sandbox=True
        #driver = await uc.start(conf, sandbox=sandbox, headless=config_dict["advanced"]["headless"])
        driver = await uc.start(conf)
        if not driver is None:
            # Output actual CDP port for MCP connection (when mcp_debug is requested)
            mcp_debug_requested = (args and hasattr(args, 'mcp_debug') and args.mcp_debug) or \
                                  config_dict["advanced"].get("mcp_debug_port", 0) > 0
            if mcp_debug_requested:
                actual_port = driver.config.port
                print(f"[MCP DEBUG] Browser started on actual port: {actual_port}")
                print(f"[MCP DEBUG] Update .mcp.json with: --browserUrl http://127.0.0.1:{actual_port}")
                # Write port to file for /mcpstart command auto-update
                try:
                    port_file = os.path.join(os.path.dirname(__file__), '..', '.temp', 'mcp_port.txt')
                    os.makedirs(os.path.dirname(port_file), exist_ok=True)
                    with open(port_file, 'w') as f:
                        f.write(str(actual_port))
                    print(f"[MCP DEBUG] Port saved to .temp/mcp_port.txt")
                except Exception as e:
                    print(f"[MCP DEBUG] Warning: Could not save port to file: {e}")
            initial_tab = driver.main_tab
            if initial_tab:
                await nodrver_block_urls(initial_tab, config_dict)
            tab = await nodriver_goto_homepage(driver, config_dict)
            if tab is None:
                print("[ERROR] Homepage navigation failed. Cannot continue.")
                sys.exit()
            if not initial_tab:
                tab = await nodrver_block_urls(tab, config_dict)
            if not config_dict["advanced"]["headless"]:
                await nodriver_resize_window(tab, config_dict)
        else:
            print("無法使用nodriver，程式無法繼續工作")
            sys.exit()
    else:
        print("Load config error!")
        sys.exit()

    url = ""
    last_url = ""
    cloudflare_checked = False
    cloudflare_fail_count = 0
    last_paused_state = False  # Track pause state changes

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = create_universal_ocr(config_dict)
            if ocr is None:
                ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
                ocr.set_ranges(1)
            Captcha_Browser = NonBrowser()
            if len(config_dict["accounts"]["tixcraft_sid"]) > 1:
                #set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
                pass
    except Exception as exc:
        debug = util.create_debug_logger(config_dict)
        debug.log(f"[OCR INIT] Failed to initialize OCR: {exc}")

    maxbot_last_reset_time = time.time()
    is_quit_bot = False
    is_refresh_datetime_sent = False
    ticketplus_purchase_done = False  # Guard: stop polling after purchase completed

    # Initialize config mtime
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    config_mtime = 0
    if os.path.exists(config_filepath):
        config_mtime = os.path.getmtime(config_filepath)

    while True:
        await asyncio.sleep(0.05)

        config_dict, config_mtime = await reload_config(config_dict, config_mtime)

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

        is_maxbot_paused = await check_and_handle_pause(config_dict)

        # Detect pause state change and show message immediately
        if is_maxbot_paused and not last_paused_state:
            print("BOT Paused.")
        last_paused_state = is_maxbot_paused

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                cloudflare_checked = False
                cloudflare_fail_count = 0
            last_url = url

        if is_maxbot_paused:
            if 'kktix.c' in url:
                await nodriver_kktix_paused_main(tab, url, config_dict)
            # sleep more when paused.
            await asyncio.sleep(0.1)
            continue

        # Cloudflare challenge detection (only on URL change to avoid performance hit)
        # After 3 consecutive failures on same URL, stop retrying to avoid infinite loop
        if not cloudflare_checked and cloudflare_fail_count < 3:
            is_cloudflare = await detect_cloudflare_challenge(tab, show_debug=config_dict.get("advanced", {}).get("verbose", False))
            cloudflare_checked = True
            if is_cloudflare:
                print("[CLOUDFLARE] Challenge page detected, attempting to solve...")
                cf_result = await handle_cloudflare_challenge(tab, config_dict)
                if cf_result:
                    cloudflare_checked = False  # Re-check after successful handling
                    cloudflare_fail_count = 0
                    continue
                else:
                    cloudflare_fail_count += 1
                    cloudflare_checked = False  # Allow retry on next loop iteration
                    if cloudflare_fail_count >= 3:
                        print("[CLOUDFLARE] Max failures reached, waiting for URL change to retry")

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            is_quit_bot = await nodriver_kktix_main(tab, url, config_dict)
            if is_quit_bot:
                # 不自動暫停：讓多開實例可獨立運作
                # 保留 is_quit_bot = False 以防止程式結束，但不建立暫停檔案
                is_quit_bot = False

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if 'ticketmaster.' in url:
            tixcraft_family = True

        if tixcraft_family:
            is_quit_bot = await nodriver_tixcraft_main(tab, url, config_dict, ocr, Captcha_Browser)
            if is_quit_bot:
                # 不自動暫停：讓多開實例可獨立運作
                # 保留 is_quit_bot = False 以防止程式結束，但不建立暫停檔案
                is_quit_bot = False

        if 'famiticket.com' in url:
            await nodriver_famiticket_main(tab, url, config_dict)

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
            tab = await nodriver_kham_main(tab, url, config_dict, ocr)

        # https://ticketplus.com.tw/*
        if 'ticketplus.com' in url and not ticketplus_purchase_done:
            tp_status = await nodriver_ticketplus_main(tab, url, config_dict, ocr, Captcha_Browser)

            if isinstance(tp_status, dict):
                if tp_status.get("purchase_completed", False):
                    if not ticketplus_purchase_done:
                        print("[SUCCESS] TicketPlus purchase completed")
                        ticketplus_purchase_done = True
                elif tp_status.get("is_ticket_assigned", False) and '/confirm/' in url.lower():
                    if not ticketplus_purchase_done:
                        print("[SUCCESS] TicketPlus on confirmation page, booking successful")
                        ticketplus_purchase_done = True

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
            tab = await nodriver_hkticketing_main(tab, url, config_dict)

        # FunOne Tickets
        if 'tickets.funone.io' in url:
            tab = await nodriver_funone_main(tab, url, config_dict)

        # FANSI GO
        if 'go.fansi.me' in url:
            tab = await nodriver_fansigo_main(tab, url, config_dict)

        # FANSI GO Cognito login
        if FANSIGO_COGNITO_DOMAIN in url:
            await nodriver_fansigo_signin(tab, url, config_dict)

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

    parser.add_argument("--area_auto_select_mode",
        help="overwrite area_auto_select mode",
        choices=['random', 'center', 'from top to bottom', 'from bottom to top'],
        type=str)

    parser.add_argument("--area_keyword",
        help="overwrite area_auto_select area_keyword",
        type=str)

    parser.add_argument("--mcp_debug",
        help="Enable MCP debug mode with fixed CDP port (default: 9222)",
        nargs='?',
        const=9222,
        type=int)

    parser.add_argument("--mcp_connect",
        help="Connect to existing Chrome on specified port (e.g., --mcp_connect 9222)",
        type=int,
        metavar="PORT")

    args = parser.parse_args()
    asyncio.run(main(args))

if __name__ == "__main__":
    cli()
