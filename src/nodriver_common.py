#!/usr/bin/env python3
#encoding=utf-8
"""
nodriver_common.py -- Shared DOM tools, pause mechanism, browser init, Cloudflare handling.

This module is the common foundation for all platform modules.
No platform-specific logic should be placed here.

Dependency: util.py, settings.py, chrome_downloader.py (no platform imports)
"""
import asyncio
import json
import os
import traceback

from zendriver import cdp
from zendriver.core.config import Config

import util
import settings
import chrome_downloader

try:
    import ddddocr
except Exception:
    pass


# ===== Constants =====

CONST_APP_VERSION = "TicketsHunter (2026.04.23)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"
CONST_CHROME_FAMILY = ["chrome","edge","brave"]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"

# ===== Cloudflare bypass settings =====
# "auto"   - auto silent mode (recommended for daily use)
# "debug"  - verbose processing output, for debugging
# "manual" - detect and prompt only, no auto handling
# "off"    - completely disable Cloudflare bypass
CLOUDFLARE_BYPASS_MODE = "auto"
CLOUDFLARE_MAX_RETRY = 3         # max retry count
CLOUDFLARE_WAIT_TIME = 3         # wait time after each attempt (seconds)
CLOUDFLARE_ENABLE_EXPERT_MODE = False  # True enables more aggressive browser args


# ===== OCR Factory =====

def create_universal_ocr(config_dict):
    """Create OCR instance using the universal captcha model based on settings.

    Reads use_universal and path from config_dict["ocr_captcha"].
    Returns ddddocr instance with universal model, or None if disabled or files not found.
    """
    use_universal = config_dict.get("ocr_captcha", {}).get("use_universal", True)
    if not use_universal:
        return None

    ocr_path = config_dict.get("ocr_captcha", {}).get("path", "")
    if not ocr_path:
        return None

    if not os.path.isabs(ocr_path):
        ocr_path = os.path.join(util.get_app_root(), ocr_path)

    onnx_path = os.path.join(ocr_path, "custom.onnx")
    charsets_path = os.path.join(ocr_path, "charsets.json")
    if not (os.path.exists(onnx_path) and os.path.exists(charsets_path)):
        debug = util.create_debug_logger(config_dict)
        debug.log(f"[OCR] Universal model files not found at: {ocr_path}")
        return None

    try:
        return ddddocr.DdddOcr(
            det=False, ocr=False, show_ad=False,
            import_onnx_path=onnx_path,
            charsets_path=charsets_path
        )
    except Exception as exc:
        debug = util.create_debug_logger(config_dict)
        debug.log(f"[OCR] Failed to load universal model: {exc}")
        return None


CONST_TIXCRAFT_TM_MODEL_PATH = "assets/model/tixcraft_tm"
CONST_DEFAULT_UNIVERSAL_PATH = "assets/model/universal"

def create_ocr_for_platform(config_dict):
    """Create the best OCR instance for the current platform.

    Priority:
    1. use_universal=False -> None (ddddocr fallback in caller)
    2. User custom path (not the default) -> use user's path
    3. tixcraft / ticketmaster / indievox homepage -> try tixcraft_tm model
    4. Fallback -> universal model
    """
    ocr_cfg = config_dict.get("ocr_captcha", {})
    if not ocr_cfg.get("use_universal", True):
        return None

    user_path = ocr_cfg.get("path", "")

    # If user explicitly set a non-default path, respect it
    if user_path and user_path != CONST_DEFAULT_UNIVERSAL_PATH:
        return create_universal_ocr(config_dict)

    # Auto-select based on homepage
    homepage = config_dict.get("homepage", "")
    tixcraft_domains = ["tixcraft.com", "indievox.com", "ticketmaster."]
    if any(domain in homepage for domain in tixcraft_domains):
        override = dict(config_dict)
        override["ocr_captcha"] = dict(ocr_cfg)
        override["ocr_captcha"]["path"] = CONST_TIXCRAFT_TM_MODEL_PATH
        ocr = create_universal_ocr(override)
        if ocr is not None:
            debug = util.create_debug_logger(config_dict)
            debug.log(f"[OCR] Auto-selected tixcraft_tm model for {homepage}")
            return ocr

    return create_universal_ocr(config_dict)


# ===== Config Loading =====

def get_config_dict(args):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    if args.input and len(args.input) > 0:
        config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        try:
            with open(config_filepath, encoding='utf-8') as json_data:
                config_dict = json.load(json_data)
                config_dict = settings.migrate_config(config_dict)
        except Exception as e:
            print(f"[ERROR] Failed to load settings: {config_filepath}")
            print(f"[ERROR] {e}")
            config_dict = None

        if config_dict is not None:
            # Define a dictionary to map argument names to their paths in the config_dict
            arg_to_path = {
                "headless": ["advanced", "headless"],
                "homepage": ["homepage"],
                "ticket_number": ["ticket_number"],
                "browser": ["browser"],
                "proxy_server": ["advanced", "proxy_server_port"],
                "window_size": ["advanced", "window_size"],
                "date_auto_select_mode": ["date_auto_select", "mode"],
                "date_keyword": ["date_auto_select", "date_keyword"],
                "area_auto_select_mode": ["area_auto_select", "mode"],
                "area_keyword": ["area_auto_select", "area_keyword"]
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
                if len(config_dict["accounts"]["tixcraft_sid"]) > 1:
                    is_headless_enable_ocr = True

            if is_headless_enable_ocr:
                config_dict["ocr_captcha"]["enable"] = True
                config_dict["ocr_captcha"]["force_submit"] = True

    return config_dict


# ===== File Utilities =====

def write_question_to_file(question_text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_QUESTION_FILE)
    util.write_string_to_file(target_path, question_text)

def write_last_url_to_file(url):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_LAST_URL_FILE)
    util.write_string_to_file(target_path, url)


# ===== Notification =====

def play_sound_while_ordering(config_dict):
    app_root = util.get_app_root()
    captcha_sound_filename = os.path.join(app_root, config_dict["advanced"]["play_sound"]["filename"].strip())
    util.play_mp3_async(captcha_sound_filename)

def send_discord_notification(config_dict, stage, platform_name):
    """Send Discord webhook notification if configured.

    Args:
        config_dict: Configuration dictionary
        stage: "ticket" or "order"
        platform_name: Platform name (e.g., "TixCraft", "iBon")
    """
    adv = config_dict.get("advanced", {})
    webhook_url = adv.get("discord_webhook_url", "")
    if webhook_url:
        verbose = adv.get("verbose", False)
        custom_message = adv.get("discord_message", "")
        util.send_discord_webhook_async(
            webhook_url, stage, platform_name,
            verbose=verbose, custom_message=custom_message
        )

def send_telegram_notification(config_dict, stage, platform_name):
    """Send Telegram bot notification if configured.

    Args:
        config_dict: Configuration dictionary
        stage: "ticket" or "order"
        platform_name: Platform name (e.g., "TixCraft", "iBon")
    """
    adv = config_dict.get("advanced", {})
    bot_token = adv.get("telegram_bot_token", "")
    chat_id = adv.get("telegram_chat_id", "")
    if bot_token and chat_id:
        verbose = adv.get("verbose", False)
        custom_message = adv.get("telegram_message", "")
        util.send_telegram_message_async(
            bot_token, chat_id, stage, platform_name,
            verbose=verbose, custom_message=custom_message
        )
    elif bot_token or chat_id:
        debug = util.create_debug_logger(config_dict)
        debug.log("[Telegram] partial config: bot_token or chat_id is missing")


# ===== DOM Tools =====

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
            print(f"[BUTTON] click fail for {select_query}: {e}")
            pass

async def nodriver_force_check_checkbox(tab, checkbox_element):
    """force check checkbox"""
    is_finish_checkbox_click = False

    if checkbox_element:
        try:
            # Use JavaScript to check and set checkbox state
            result = await tab.evaluate('''
                (function(element) {
                    if (!element) return false;

                    // Check if already checked
                    if (element.checked) return true;

                    // Try click
                    try {
                        element.click();
                        return element.checked;
                    } catch(e) {
                        // fallback: directly set checked property
                        element.checked = true;
                        return element.checked;
                    }
                })(arguments[0]);
            ''', checkbox_element)

            is_finish_checkbox_click = bool(result)

        except Exception as exc:
            pass

    return is_finish_checkbox_click

async def nodriver_check_checkbox_enhanced(tab, select_query, config_dict=None):
    """Enhanced checkbox function using direct JavaScript"""
    debug = util.create_debug_logger(config_dict)
    is_checkbox_checked = False

    try:
        debug.log(f"Checking checkbox: {select_query}")

        # Direct JavaScript find and check
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

        debug.log(f"Checkbox result: {is_checkbox_checked}")

    except Exception as exc:
        debug.log(f"Checkbox error: {exc}")

    return is_checkbox_checked

async def nodriver_check_checkbox(tab, selector, max_retries=2):
    """
    Check a checkbox element with retry mechanism.
    Returns: True if successfully checked, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Use pure JavaScript to avoid Element serialization issues
            is_checked = await tab.evaluate(f'''
                (function() {{
                    const checkbox = document.querySelector('{selector}');
                    if (!checkbox) return false;

                    // If already checked, return true
                    if (checkbox.checked) return true;

                    // Try to click
                    try {{
                        checkbox.click();
                        return checkbox.checked;
                    }} catch(e) {{
                        // Fallback: directly set checked property
                        checkbox.checked = true;
                        return checkbox.checked;
                    }}
                }})();
            ''')

            if is_checked:
                return True

            await tab.sleep(0.1)

        except Exception as exc:
            if attempt == max_retries - 1:
                print(f"[CHECKBOX] Failed to check {selector}: {exc}")

    return False

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

async def nodriver_check_modal_dialog_popup(tab):
    ret = False
    try:
        el_div = await tab.query_selector('div.modal-dialog > div.modal-content')
        if el_div:
            ret = True
    except Exception as exc:
        print(exc)
        pass
    return ret

def convert_remote_object(obj, depth=0):
    """
    Convert NoDriver CDP RemoteObject format to standard Python types.

    RemoteObject format:
    {
      "type": "object",
      "value": [["key1", {"type": "string", "value": "val1"}], ...]
    }

    Standard format:
    {"key1": "val1", "key2": 123, ...}
    """
    if not isinstance(obj, dict):
        return obj

    # Check if this is a RemoteObject
    if "type" in obj and "value" in obj:
        obj_type = obj.get("type")
        obj_value = obj.get("value")

        if obj_type == "object" and isinstance(obj_value, list):
            # Convert [[key, {type, value}], ...] to {key: value, ...}
            result = {}
            for item in obj_value:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    key = item[0]
                    val_obj = item[1]
                    # Recursively convert the value
                    result[key] = convert_remote_object(val_obj, depth + 1)
            return result

        elif obj_type == "number":
            return obj_value
        elif obj_type == "string":
            return obj_value
        elif obj_type == "boolean":
            return obj_value
        elif obj_type == "array" and isinstance(obj_value, list):
            return [convert_remote_object(item, depth + 1) for item in obj_value]
        else:
            return obj_value

    # Not a RemoteObject, but might contain nested RemoteObjects
    if isinstance(obj, dict):
        return {k: convert_remote_object(v, depth + 1) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_remote_object(item, depth + 1) for item in obj]
    else:
        return obj

async def nodriver_current_url(tab):
    is_quit_bot = False
    exit_bot_error_strings = [
        "server rejected WebSocket connection: HTTP 500",
        "[Errno 61] Connect call failed ('127.0.0.1',",
        "[WinError 1225] ",
    ]
    # WebSocket connection closed normally (e.g. after purchase completed or page navigation)
    # These are expected and should not be printed
    silent_error_strings = [
        "no close frame received or sent",
        "no close frame sent",
        "no close frame received",
    ]

    url = ""
    if tab:
        url_dict = {}
        try:
            url_dict = await tab.js_dumps('window.location.href')
        except Exception as exc:
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass
            is_silent = any(s in str_exc for s in silent_error_strings)
            if not is_silent:
                print(exc)
            if len(str_exc) > 0:
                for each_error_string in exit_bot_error_strings:
                    if each_error_string in str_exc:
                        is_quit_bot = True

        url_array = []
        if url_dict:
            for k in url_dict:
                if k.isnumeric():
                    if "0" in url_dict[k]:
                        url_array.append(url_dict[k]["0"])
            url = ''.join(url_array)
    return url, is_quit_bot

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


# ===== Cloudflare Handling =====

async def detect_cloudflare_challenge(tab, show_debug=False):
    """
    Detect Cloudflare challenge page (Turnstile widget or full-page interstitial).

    Three-layer detection:
    1. CDP Target: check for iframe target with challenges.cloudflare.com (most reliable)
    2. JS DOM query: iframe or .cf-turnstile (fast but misses shadow DOM iframes)
    3. HTML keywords: full-page CF interstitial indicators (fallback)

    Returns:
        bool: True if Cloudflare challenge detected
    """
    debug = util.create_debug_logger(enabled=show_debug)
    try:
        # Layer 1: CDP Target detection (most reliable - finds iframes invisible to JS)
        try:
            targets = await tab.send(cdp.target.get_targets())
            for t in targets:
                url_str = str(t.url) if t.url else ""
                if "challenges.cloudflare" in url_str:
                    debug.log("[CF DETECT] Cloudflare target found via CDP")
                    return True
        except Exception:
            pass

        # Layer 2: JS DOM detection (fast, catches some cases)
        try:
            cf_dom = await tab.evaluate(
                '!!(document.querySelector(\'iframe[src*="challenges.cloudflare.com"]\')'
                ' || document.querySelector(\'.cf-turnstile\'))'
            )
            if cf_dom:
                debug.log("[CF DETECT] Cloudflare DOM element found")
                return True
        except Exception:
            pass

        # Layer 3: HTML keyword detection (full-page interstitial fallback)
        html_content = await tab.get_content()
        if not html_content:
            return False

        html_lower = html_content.lower()

        # Note: "cloudflare" alone is too broad (matches CDN/analytics scripts)
        cloudflare_indicators = [
            "cf-browser-verification",
            "cf-challenge-running",
            "cf-spinner-allow-5-secs",
            "checking your browser",
            "please wait while we verify",
            "verify you are human",
        ]

        detected = any(indicator in html_lower for indicator in cloudflare_indicators)
        if detected:
            debug.log("[CF DETECT] Cloudflare keywords found in HTML")
        return detected

    except Exception as exc:
        debug.log(f"Cloudflare detection error: {exc}")
        return False

def _find_cf_iframe_in_dom(node, depth=0):
    """Walk pierced DOM tree to find Cloudflare Turnstile iframe node.

    Returns (node_id, src) if found, else (None, None).
    """
    name = (node.node_name or "").upper()
    attrs = {}
    if node.attributes:
        for i in range(0, len(node.attributes), 2):
            if i + 1 < len(node.attributes):
                attrs[node.attributes[i]] = node.attributes[i + 1]

    if name == "IFRAME":
        src = attrs.get("src", "")
        title = attrs.get("title", "")
        if "challenges.cloudflare" in src or "challenges.cloudflare" in title:
            return (node.node_id, src)

    # Recurse: children, shadow roots, content documents
    for child_list in [node.children, node.shadow_roots]:
        if child_list:
            for child in child_list:
                result = _find_cf_iframe_in_dom(child, depth + 1)
                if result[0]:
                    return result
    if node.content_document:
        result = _find_cf_iframe_in_dom(node.content_document, depth + 1)
        if result[0]:
            return result

    return (None, None)


async def _cdp_click(tab, x, y):
    """Dispatch CDP mousePressed + mouseReleased at (x, y)."""
    await tab.send(cdp.input_.dispatch_mouse_event(
        type_="mousePressed", x=x, y=y,
        button=cdp.input_.MouseButton("left"), click_count=1
    ))
    await tab.sleep(0.05)
    await tab.send(cdp.input_.dispatch_mouse_event(
        type_="mouseReleased", x=x, y=y,
        button=cdp.input_.MouseButton("left"), click_count=1
    ))


async def handle_cloudflare_challenge(tab, config_dict, max_retry=None):
    """
    Handle Cloudflare Turnstile challenge.

    Strategy (per attempt, in order):
    1. CDP DOM pierce: find iframe via DOM.getDocument(pierce=True) + getBoxModel for position
    2. Text label positioning: find surrounding text, calculate checkbox offset
    3. verify_cf fallback: nodriver built-in template matching (least reliable)

    Args:
        tab: nodriver tab object
        config_dict: settings dict
        max_retry: max retries (default: CLOUDFLARE_MAX_RETRY)

    Returns:
        bool: True if challenge bypassed successfully
    """
    max_retry = max_retry or CLOUDFLARE_MAX_RETRY

    cf_debug = (config_dict.get("advanced", {}).get("verbose", False) or
                CLOUDFLARE_BYPASS_MODE == "debug")

    debug = util.create_debug_logger(enabled=cf_debug)
    debug.log("[CLOUDFLARE] Starting to handle Cloudflare challenge...")

    for retry_count in range(max_retry):
        try:
            if retry_count > 0:
                debug.log(f"[CLOUDFLARE] Retry attempt {retry_count}...")
                await tab.sleep(3 + retry_count)

            clicked = False

            # Method 1: CDP DOM pierce + getBoxModel (most precise)
            try:
                doc = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
                node_id, src = _find_cf_iframe_in_dom(doc)
                if node_id:
                    debug.log(f"[CLOUDFLARE] Found iframe via DOM pierce (nodeId={node_id})")
                    try:
                        box = await tab.send(cdp.dom.get_box_model(node_id=node_id))
                        if box and box.content:
                            # content quad: 4 points [x1,y1, x2,y2, x3,y3, x4,y4]
                            quad = box.content
                            if len(quad) >= 6:
                                ix = quad[0]
                                iy = quad[1]
                                iw = quad[2] - quad[0]
                                ih = quad[5] - quad[1]
                                # Checkbox is ~30px from left, vertically centered
                                click_x = ix + 30
                                click_y = iy + (ih / 2)
                                debug.log(f"[CLOUDFLARE] CDP click via DOM pierce at ({click_x:.0f}, {click_y:.0f}), size: {iw:.0f}x{ih:.0f}")
                                await _cdp_click(tab, click_x, click_y)
                                clicked = True
                            else:
                                debug.log(f"[CLOUDFLARE] Unexpected quad length: {len(quad)}")
                    except Exception as box_exc:
                        debug.log(f"[CLOUDFLARE] getBoxModel failed: {box_exc}")
            except Exception as exc:
                debug.log(f"[CLOUDFLARE] DOM pierce method failed: {exc}")

            # Method 2: Text label positioning (proven on real CF pages)
            if not clicked:
                try:
                    label_raw = await tab.evaluate('''
                        (function() {
                            var labels = [
                                "let us know you are human",
                                "verify you are human",
                                "confirm you are human"
                            ];
                            var all = document.querySelectorAll('*');
                            for (var i = 0; i < all.length; i++) {
                                var t = (all[i].textContent || '').trim();
                                var tl = t.toLowerCase();
                                var matched = false;
                                for (var j = 0; j < labels.length; j++) {
                                    if (tl === labels[j] || tl.indexOf(labels[j]) === 0) {
                                        matched = true;
                                        break;
                                    }
                                }
                                if (!matched) {
                                    var cjk = [
                                        "\u8acb\u8b93\u6211\u5011\u77e5\u9053\u60a8\u662f\u4eba\u985e",
                                        "\u9a57\u8b49\u60a8\u662f\u4eba\u985e",
                                        "\u4eba\u9593\u3067\u3042\u308b\u3053\u3068\u3092\u78ba\u8a8d"
                                    ];
                                    for (var k = 0; k < cjk.length; k++) {
                                        if (t.indexOf(cjk[k]) >= 0) {
                                            matched = true;
                                            break;
                                        }
                                    }
                                }
                                if (matched) {
                                    var r = all[i].getBoundingClientRect();
                                    if (r.height > 0 && r.height < 50 && r.width > 50) {
                                        return JSON.stringify({x: r.x, y: r.y, h: r.height});
                                    }
                                }
                            }
                            return null;
                        })()
                    ''')
                    if label_raw:
                        label_info = label_raw
                        if isinstance(label_raw, str):
                            label_info = json.loads(label_raw)
                        if isinstance(label_info, dict) and "x" in label_info:
                            # Turnstile widget is below the label
                            # Checkbox at ~30px from left, ~32px below label bottom
                            click_x = label_info["x"] + 30
                            click_y = label_info["y"] + label_info["h"] + 32
                            debug.log(f"[CLOUDFLARE] CDP click via text label at ({click_x:.0f}, {click_y:.0f})")
                            await _cdp_click(tab, click_x, click_y)
                            clicked = True
                except Exception as exc:
                    debug.log(f"[CLOUDFLARE] Text label method failed: {exc}")

            # Method 3: Fallback - verify_cf template matching
            if not clicked:
                try:
                    cf_template_result = await util.verify_cf_with_templates(tab, show_debug=cf_debug)
                    if cf_template_result:
                        debug.log("[CLOUDFLARE] verify_cf_with_templates succeeded (fallback)")
                        clicked = True
                    else:
                        debug.log("[CLOUDFLARE] verify_cf_with_templates failed (fallback)")
                except Exception:
                    pass

            # Wait for challenge to resolve
            wait_time = CLOUDFLARE_WAIT_TIME + (retry_count * 2)
            await tab.sleep(wait_time)

            # Verify: check if CF challenge is resolved
            # Note: CDP target persists even after solved Turnstile, so use HTML-only check
            # when a click was dispatched. HTML active indicators only appear in full-page
            # interstitials, not in embedded (solved) Turnstile widgets.
            if clicked:
                still_active = False
                try:
                    html_content = await tab.get_content()
                    if html_content:
                        html_lower = html_content.lower()
                        active_indicators = [
                            "cf-browser-verification",
                            "cf-challenge-running",
                            "cf-spinner-allow-5-secs",
                            "checking your browser",
                        ]
                        still_active = any(ind in html_lower for ind in active_indicators)
                except Exception as exc:
                    debug.log(f"[CLOUDFLARE] Post-click verification failed: {exc}")
                    still_active = True
                if not still_active:
                    debug.log("[CLOUDFLARE] Challenge bypassed successfully")
                    return True
            else:
                # No click dispatched; use full detection
                if not await detect_cloudflare_challenge(tab, cf_debug):
                    debug.log("[CLOUDFLARE] Challenge resolved (no click needed)")
                    return True

            debug.log(f"[CLOUDFLARE] Attempt {retry_count + 1} unsuccessful")

            if retry_count == max_retry - 1:
                try:
                    debug.log("[CLOUDFLARE] Last attempt: Refreshing page")
                    await tab.reload()
                    await tab.sleep(5)
                    if not await detect_cloudflare_challenge(tab, cf_debug):
                        return True
                except Exception:
                    pass

        except Exception as exc:
            debug.log(f"[CLOUDFLARE] Error during processing: {exc}")

    debug.log("[CLOUDFLARE] Challenge handling failed, max retries reached")
    return False


# ===== Pause Mechanism =====

async def check_and_handle_pause(config_dict=None):
    """check pause file and handle pause state"""
    if os.path.exists(CONST_MAXBOT_INT28_FILE):
        return True
    return False

# === Enhanced pause check functions ===
# For NoDriver pause responsiveness close to Chrome version:
# 1. sleep_with_pause_check: tab.sleep() with pause check
# 2. asyncio_sleep_with_pause_check: asyncio.sleep() with pause check
# 3. evaluate_with_pause_check: JavaScript execution with pause check
# 4. with_pause_check: task wrapper with pause interrupt support

async def sleep_with_pause_check(tab, seconds, config_dict=None):
    """delay with pause state check"""
    if await check_and_handle_pause(config_dict):
        return True  # paused
    await tab.sleep(seconds)
    return False  # not paused

async def asyncio_sleep_with_pause_check(seconds, config_dict=None):
    """asyncio.sleep with pause state check"""
    if await check_and_handle_pause(config_dict):
        return True  # paused
    await asyncio.sleep(seconds)
    return False  # not paused

async def evaluate_with_pause_check(tab, javascript_code, config_dict=None):
    """execute JavaScript with pause state check"""
    if await check_and_handle_pause(config_dict):
        return None  # paused, return None
    try:
        result = await tab.evaluate(javascript_code)
        return result
    except Exception as exc:
        # Always print JS execution errors for debugging
        print(f"[JS ERROR] JavaScript execution failed: {exc}")
        traceback.print_exc()
        return None

async def with_pause_check(task_func, config_dict, *args, **kwargs):
    """wrapper function with pause interrupt support"""
    # Check pause state once first
    if await check_and_handle_pause(config_dict):
        return None

    # Create task but don't await immediately
    task = asyncio.create_task(task_func(*args, **kwargs))

    # Periodically check pause state during task execution
    while not task.done():
        if await check_and_handle_pause(config_dict):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return None
        await asyncio.sleep(0.05)  # check every 50ms

    return await task


# ===== Browser Initialization =====

def get_nodriver_browser_args():
    """
    Get nodriver browser args.
    Based on verified args that pass Cloudflare checks.
    """
    # Browser args verified to pass Cloudflare checks
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
        # Note: --remote-debugging-host is managed by Config(host=...) when MCP debug is enabled
        "--lang=zh-TW",
    ]

    # Expert mode: cautiously add high-risk args
    if CLOUDFLARE_ENABLE_EXPERT_MODE:
        # Warning: these args may increase detection risk but provide stronger bypass
        expert_args = [
            "--no-sandbox",  # needed in some environments, detection risk
            "--disable-web-security",  # high risk but effective
        ]
        browser_args.extend(expert_args)

    return browser_args

def get_extension_config(config_dict, args=None):
    sandbox=True
    browser_args = get_nodriver_browser_args()
    if len(config_dict["advanced"]["proxy_server_port"]) > 2:
        browser_args.append('--proxy-server=%s' % config_dict["advanced"]["proxy_server_port"])

    # MCP connect mode: Connect to existing Chrome instance (for MCP integration)
    # This allows NoDriver to attach to a Chrome started with --remote-debugging-port
    mcp_connect_port = None
    if args and hasattr(args, 'mcp_connect') and args.mcp_connect:
        mcp_connect_port = args.mcp_connect

    if mcp_connect_port:
        # Connect to existing Chrome (NoDriver will NOT start a new browser)
        print(f"[MCP CONNECT] Connecting to existing Chrome on port {mcp_connect_port}")
        print(f"[MCP CONNECT] Make sure Chrome is running with: --remote-debugging-port={mcp_connect_port}")
        conf = Config(
            host="127.0.0.1",
            port=mcp_connect_port,
            headless=config_dict["advanced"]["headless"]
        )
        # Note: When connecting to existing browser, extensions cannot be loaded
        return conf

    # MCP debug mode: NoDriver uses dynamic CDP port, we output actual port after browser starts
    # Note: NoDriver limitation - cannot use fixed port (browser.py:357-361 treats host+port as
    # "connect to existing browser" mode). We just mark that MCP debug is requested here.
    # The actual port will be printed in main() after browser starts.
    mcp_debug_enabled = False
    if args and hasattr(args, 'mcp_debug') and args.mcp_debug:
        mcp_debug_enabled = True
        print("[MCP DEBUG] Mode enabled - actual port will be shown after browser starts")
    elif config_dict["advanced"].get("mcp_debug_port", 0) > 0:
        mcp_debug_enabled = True
        print("[MCP DEBUG] Mode enabled (via settings.json) - actual port will be shown after browser starts")

    # Ensure Chrome is available (download if needed)
    # This fixes Issue #236: NoDriver fails when Chrome is not installed
    app_root = util.get_app_root()
    webdriver_dir = os.path.join(app_root, "webdriver")
    chrome_path = chrome_downloader.ensure_chrome_available(download_dir=webdriver_dir)
    if not chrome_path:
        print("[ERROR] Chrome not found and download failed.")
        print("[ERROR] Please install Chrome manually or check your internet connection.")
        raise FileNotFoundError("Could not find or download Chrome browser")

    # Normal mode: auto-detect (host=None, port=None) to let NoDriver start the browser
    conf = Config(browser_args=browser_args, sandbox=sandbox, headless=config_dict["advanced"]["headless"], browser_executable_path=chrome_path)
    return conf

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
    prefs_dict["profile"]["name"]="Person 1"  # Use Chrome's default profile name to avoid fingerprinting
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


# ===== Shared captcha image capture =====

async def nodriver_get_captcha_image_from_dom_snapshot(tab, config_dict):
    """
    Use DOMSnapshot to find captcha image inside Shadow DOM and get base64 data.
    Supports IMG elements with '/pic.aspx?TYPE=' pattern and CANVAS fallback.
    Used by ibon and kham family platforms.
    Returns: img_base64 (bytes) or None
    """
    debug = util.create_debug_logger(config_dict)

    # Wait for page to stabilize before capturing
    import random
    await asyncio.sleep(random.uniform(0.5, 0.8))

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

                            debug.log(f"[CAPTCHA] Found IMG: {target_img_url}")
                            break

            if img_backend_node_id:
                break

        if not img_backend_node_id:
            # Try finding CANVAS element (new EventBuy format)
            debug.log("[CAPTCHA] IMG not found, searching for CANVAS element...")

            for doc in documents:
                node_names = [strings[i] for i in doc.nodes.node_name]

                for idx, node_name in enumerate(node_names):
                    if node_name.lower() == 'canvas':
                        # Found CANVAS element, use it for captcha
                        if hasattr(doc.nodes, 'backend_node_id') and idx < len(doc.nodes.backend_node_id):
                            img_backend_node_id = doc.nodes.backend_node_id[idx]

                            debug.log(f"[CAPTCHA] Found CANVAS element")
                            break

                if img_backend_node_id:
                    break

        if not img_backend_node_id:
            debug.log("[CAPTCHA] Neither IMG nor CANVAS found")
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

                                # Crop using PIL (coordinates need to account for device pixel ratio)
                                left = int(x * device_pixel_ratio)
                                top = int(y * device_pixel_ratio)
                                right = int((x + width) * device_pixel_ratio)
                                bottom = int((y + height) * device_pixel_ratio)

                                cropped_img = full_img.crop((left, top, right, bottom))

                                # Convert back to bytes
                                img_buffer = io.BytesIO()
                                cropped_img.save(img_buffer, format='PNG')
                                img_base64 = img_buffer.getvalue()

                                debug.log(f"[CAPTCHA] Screenshot: {len(img_base64)} bytes")

                        else:
                            debug.log("[CAPTCHA] Failed to get box model")
                    else:
                        debug.log("[CAPTCHA] Failed to convert backend_node_id")
                except Exception as dom_exc:
                    debug.log(f"[CAPTCHA] DOM API error: {dom_exc}")
            else:
                debug.log("[CAPTCHA] No backend_node_id found for IMG")

        except Exception as exc:
            if debug.enabled:
                debug.log(f"[CAPTCHA] Screenshot failed: {exc}")
                import traceback
                traceback.print_exc()

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[CAPTCHA ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return img_base64
