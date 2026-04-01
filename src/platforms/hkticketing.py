#encoding=utf-8
# =============================================================================
# HKTicketing Platform Module
# Extracted from nodriver_tixcraft.py during modularization (Phase 1)
# Contains: hkticketing.com, galaxymacau.com, ticketek.com.au (softix family)
# =============================================================================

import asyncio
import json
import random
import re
import time

from zendriver import cdp

import util
from nodriver_common import (
    nodriver_check_modal_dialog_popup,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    CONST_FROM_TOP_TO_BOTTOM,
)

__all__ = [
    "HKTICKETING_CONTENT_RETRY_STRING_LIST",
    "HKTICKETING_REDIRECT_URL_LIST",
    "HKTICKETING_CHECK_URL_LIST",
    "HKTICKETING_CHECK_FULL_URL_LIST",
    "HKTICKETING_DATE_SOLDOUT_KEYWORDS",
    "HKTICKETING_DATE_SOLDOUT_KEYWORDS_ZH",
    "nodriver_hkticketing_login",
    "nodriver_hkticketing_accept_cookie",
    "nodriver_hkticketing_date_buy_button_press",
    "nodriver_hkticketing_date_assign",
    "nodriver_hkticketing_date_password_input",
    "nodriver_hkticketing_date_auto_select",
    "nodriver_hkticketing_area_auto_select",
    "nodriver_hkticketing_ticket_number_auto_select",
    "nodriver_hkticketing_ticket_delivery_option",
    "nodriver_hkticketing_next_button_press",
    "nodriver_hkticketing_go_to_payment",
    "nodriver_hkticketing_hide_tickets_blocks",
    "nodriver_hkticketing_type02_clear_session",
    "nodriver_hkticketing_type02_check_traffic_overload",
    "nodriver_hkticketing_type02_login",
    "nodriver_hkticketing_type02_dismiss_modal",
    "nodriver_hkticketing_type02_event_page_buy_button",
    "nodriver_hkticketing_type02_event_page",
    "nodriver_hkticketing_type02_date_assign",
    "nodriver_hkticketing_type02_area_auto_select",
    "nodriver_hkticketing_type02_ticket_number_select",
    "nodriver_hkticketing_type02_next_button_press",
    "nodriver_hkticketing_type02_performance",
    "nodriver_hkticketing_type02_confirm_order",
    "nodriver_hkticketing_performance",
    "nodriver_hkticketing_escape_robot_detection",
    "nodriver_hkticketing_url_redirect",
    "nodriver_hkticketing_content_refresh",
    "nodriver_hkticketing_travel_iframe",
    "nodriver_hkticketing_main",
]

# Module-level state (replaces global hkticketing_dict)
_state = {}


# ====================================================================================
# HKTicketing Platform (hkticketing.com / galaxymacau.com / ticketek.com.au)
# ====================================================================================

# HKTicketing error message list for content refresh detection
HKTICKETING_CONTENT_RETRY_STRING_LIST = [
    "Access Denied",
    "Service Unavailable",
    "The service is unavailable",
    "HTTP Error 500",
    "HTTP Error 503",
    "504 Gateway Time-out",
    "502 Bad Gateway",
    "An error occurred while processing your request",
    "The network path was not found",
    "Could not open a connection to SQL Server",
    "Hi fans, you're in the queue to",
    "We will check for the next available purchase slot",
    "please stay on this page and do not refresh",
    "Please be patient and wait a few minutes before trying again",
    "Server Error in '/' Application",
    "The target principal name is incorrect",
    "Cannot generate SSPI context",
    "System.Data.SqlClient.Sql",
    "System.ComponentModel.Win32Exception",
    "Your attempt to access the web site has been blocked by",
    "This request was blocked by"
]

# HKTicketing URL patterns for redirect detection
HKTICKETING_REDIRECT_URL_LIST = [
    'queue.hkticketing.com/hotshow.html',
    '.com/detection.aspx?rt=',
    '/busy_galaxy.'
]
# Add ticketek hot queue URLs (hot0 to hot19)
for _idx in range(20):
    HKTICKETING_REDIRECT_URL_LIST.append('/hot%d.ticketek.com.au/' % (_idx))

# HKTicketing URLs that need content refresh check
HKTICKETING_CHECK_URL_LIST = [
    ".com/default.aspx",
    ".com/shows/show.aspx?sh=",
    ".com/detection.aspx",
    "/entry-hotshow.",
    ".com/_Incapsula_Resource?"
]

# HKTicketing full URL matches for content refresh
HKTICKETING_CHECK_FULL_URL_LIST = [
    "https://premier.hkticketing.com/",
    "https://www.ticketing.galaxymacau.com/",
    "https://ticketing.galaxymacau.com/",
    "https://ticketing.galaxymacau.com/default.aspx"
]

# HKTicketing sold out date keywords
HKTICKETING_DATE_SOLDOUT_KEYWORDS = [
    " Exhausted",
    "No Longer On Sale"
]
HKTICKETING_DATE_SOLDOUT_KEYWORDS_ZH = [
    "Exhausted",
    "No Longer On Sale"
]

async def nodriver_hkticketing_login(tab, account, password, config_dict=None):
    """
    HKTicketing auto login
    Reference: chrome_tixcraft.py hkticketing_login (line 5661-5733)
    """
    ret = False
    debug = util.create_debug_logger(config_dict)

    debug.log("[HKTICKETING LOGIN] Starting login process...")

    # Try multiple selectors for email/login code input
    el_email = None
    email_selectors = [
        '#ctl00_uiContent_Login1_tbLoginCode',  # ASP.NET ID format
        'input[name="ctl00$uiContent$Login1$tbLoginCode"]',
        'div#myTick2Col > div.formMod2Col > div.formModule > div.loginContentContainer > input.borInput',
        'input.borInput[type="text"]',
    ]

    for selector in email_selectors:
        try:
            el_email = await tab.query_selector(selector)
            if el_email:
                break
        except Exception as exc:
            pass

    if not el_email:
        debug.log("[HKTICKETING LOGIN] Email input not found")
        return ret

    # Input account
    is_email_sent = False
    try:
        await el_email.click()
        await asyncio.sleep(0.1)

        # Check if already has value
        inputed_text = await el_email.apply('(el) => el.value')
        if not inputed_text or len(str(inputed_text)) == 0:
            await el_email.send_keys(account)
            is_email_sent = True
            debug.log(f"[HKTICKETING LOGIN] Account input completed: {account[:3]}***")
        else:
            if str(inputed_text) == account:
                is_email_sent = True
                debug.log("[HKTICKETING LOGIN] Account already filled")
    except Exception as exc:
        debug.log(f"[HKTICKETING LOGIN] Account input error: {exc}")

    if not is_email_sent:
        debug.log("[HKTICKETING LOGIN] Failed to input account")
        return ret

    # Try multiple selectors for password input
    el_pass = None
    password_selectors = [
        '#ctl00_uiContent_Login1_tbPassword',  # ASP.NET ID format
        'input[name="ctl00$uiContent$Login1$tbPassword"]',
        'div.loginContentContainer > input[type="password"]',
        'input[type="password"]',
    ]

    for selector in password_selectors:
        try:
            el_pass = await tab.query_selector(selector)
            if el_pass:
                break
        except Exception as exc:
            pass

    if not el_pass:
        debug.log("[HKTICKETING LOGIN] Password input not found")
        return ret

    # Input password
    is_password_sent = False
    try:
        await el_pass.click()
        await asyncio.sleep(0.1)

        inputed_text = await el_pass.apply('(el) => el.value')
        if not inputed_text or len(str(inputed_text)) == 0:
            if len(password) > 0:
                await el_pass.send_keys(password)
                is_password_sent = True
                debug.log("[HKTICKETING LOGIN] Password input completed")
        else:
            is_password_sent = True
            debug.log("[HKTICKETING LOGIN] Password already filled")
    except Exception as exc:
        debug.log(f"[HKTICKETING LOGIN] Password input error: {exc}")

    if not is_password_sent:
        debug.log("[HKTICKETING LOGIN] Failed to input password")
        return ret

    # Click login button
    el_login_btn = None
    login_btn_selectors = [
        '#ctl00_uiContent_Login1_btnLogin',  # ASP.NET ID format
        'input[name="ctl00$uiContent$Login1$btnLogin"]',
        'input.blueButton[type="submit"]',
        'input[value="Login"]',
    ]

    for selector in login_btn_selectors:
        try:
            el_login_btn = await tab.query_selector(selector)
            if el_login_btn:
                break
        except Exception as exc:
            pass

    if el_login_btn:
        try:
            await el_login_btn.click()
            ret = True
            debug.log("[HKTICKETING LOGIN] Login button clicked")
        except Exception as exc:
            debug.log(f"[HKTICKETING LOGIN] Login button click error: {exc}")
            # Fallback: try pressing Enter on password field
            try:
                await el_pass.send_keys(Keys.ENTER)
                ret = True
                debug.log("[HKTICKETING LOGIN] Fallback: pressed Enter key")
            except Exception as exc2:
                debug.log(f"[HKTICKETING LOGIN] Enter key fallback error: {exc2}")
    else:
        # No login button found, try pressing Enter
        debug.log("[HKTICKETING LOGIN] Login button not found, trying Enter key")
        try:
            await el_pass.send_keys(Keys.ENTER)
            ret = True
            debug.log("[HKTICKETING LOGIN] Pressed Enter key as fallback")
        except Exception as exc:
            debug.log(f"[HKTICKETING LOGIN] Enter key error: {exc}")

    await asyncio.sleep(0.2)
    return ret

async def nodriver_hkticketing_accept_cookie(tab):
    """
    Close cookie consent popup
    Reference: chrome_tixcraft.py hkticketing_accept_cookie (line 7460-7497)
    """
    try:
        el_close = await tab.query_selector('#closepolicy_new')
        if el_close:
            await el_close.click()
    except Exception as exc:
        pass

async def nodriver_hkticketing_date_buy_button_press(tab, config_dict=None):
    """
    Click buy button on date selection page and wait for URL change
    Reference: chrome_tixcraft.py hkticketing_date_buy_button_press (line 7498-7533)
    """
    debug = util.create_debug_logger(config_dict)

    is_button_clicked = False

    # Get current URL before clicking
    current_url = ""
    try:
        current_url = await tab.evaluate('window.location.href')
    except:
        pass

    el_btn = None
    try:
        el_btn = await tab.query_selector('#buyButton > input')
    except Exception as exc:
        pass

    if el_btn:
        try:
            is_enabled = await tab.evaluate('''
                (function() {
                    const btn = document.querySelector('#buyButton > input');
                    return btn ? !btn.disabled : false;
                })();
            ''')
            if is_enabled:
                await el_btn.click()
                is_button_clicked = True
                debug.log("[HKTICKETING DATE] Buy button clicked")
            else:
                # Try to enable and click via JavaScript
                is_button_clicked = await tab.evaluate('''
                    (function() {
                        const btn = document.querySelector('#buyButton > input');
                        if (btn) {
                            btn.disabled = false;
                            btn.click();
                            return true;
                        }
                        return false;
                    })();
                ''')
                if is_button_clicked:
                    debug.log("[HKTICKETING DATE] Buy button force-clicked via JS")
        except Exception as exc:
            debug.log(f"[HKTICKETING DATE] Buy button click error: {exc}")

    # Wait for URL change after clicking (prevent re-clicking)
    if is_button_clicked and current_url:
        debug.log("[HKTICKETING DATE] Waiting for URL change...")
        max_wait = 10  # Max 10 seconds
        wait_interval = 0.5
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(wait_interval)
            waited += wait_interval
            try:
                new_url = await tab.evaluate('window.location.href')
                if new_url != current_url:
                    debug.log(f"[HKTICKETING DATE] URL changed to: {new_url}")
                    break
            except:
                break
        if waited >= max_wait:
            debug.log("[HKTICKETING DATE] URL change timeout")

    return is_button_clicked

async def nodriver_hkticketing_date_assign(tab, config_dict):
    """
    Date assignment core logic
    Reference: chrome_tixcraft.py hkticketing_date_assign (line 7534-7679)

    Returns:
        Tuple[bool, bool, List]:
            - is_date_assigned: whether a date has been selected
            - is_page_ready: whether the page is ready
            - formated_area_list: list of available dates
    """
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get("date_auto_fallback", False)

    debug.log("[HKTICKETING DATE] date_keyword:", date_keyword)

    matched_blocks = None
    date_keyword = util.format_keyword_string(date_keyword)

    # Check if #p is a select element or hidden input (single performance)
    is_single_performance = False
    try:
        element_type = await tab.evaluate('''
            (function() {
                const el = document.querySelector('#p');
                if (el) {
                    return el.tagName.toLowerCase();
                }
                return null;
            })();
        ''')
        if element_type == 'input':
            # Single performance page - no date selection needed
            is_single_performance = True
            debug.log("[HKTICKETING DATE] Single performance detected (hidden input)")
    except Exception as exc:
        debug.log("[HKTICKETING DATE] Check element type error:", exc)

    # If single performance, treat as date already assigned
    if is_single_performance:
        debug.log("[HKTICKETING DATE] is_date_assigned: True (single performance)")
        return True, True, None

    # Check if date is already assigned (for select element)
    is_date_assigned = False
    selected_text = None
    try:
        selected_text = await tab.evaluate('''
            (function() {
                const select = document.querySelector('#p');
                if (select && select.selectedIndex >= 0) {
                    return select.options[select.selectedIndex].text;
                }
                return null;
            })();
        ''')
    except Exception as exc:
        debug.log("[HKTICKETING DATE] Check selected date error:", exc)

    # If a date is selected, check if it matches the keyword
    if selected_text and len(selected_text) > 8 and '20' in selected_text:
        debug.log(f"[HKTICKETING DATE] Currently selected: {selected_text}")

        if len(date_keyword) > 0:
            # Check if selected date matches keyword
            normalized_selected = util.format_keyword_string(selected_text)
            keyword_sets = util.parse_keyword_string_to_array(date_keyword)
            if not keyword_sets:
                keyword_sets = [kw.strip() for kw in date_keyword.split(',') if kw.strip()]

            for keyword_set in keyword_sets:
                keyword_parts = keyword_set.split(' ') if isinstance(keyword_set, str) else [str(keyword_set)]
                is_match = True
                for kw in keyword_parts:
                    kw_formatted = util.format_keyword_string(str(kw))
                    if kw_formatted not in normalized_selected:
                        is_match = False
                        break
                if is_match:
                    is_date_assigned = True
                    debug.log(f"[HKTICKETING DATE] Selected date matches keyword, keeping selection")
                    break

            if not is_date_assigned:
                debug.log(f"[HKTICKETING DATE] Selected date does not match keyword, will select target date")
        else:
            # No keyword specified - only keep selection if date_auto_fallback is enabled
            if date_auto_fallback:
                is_date_assigned = True
                debug.log(f"[HKTICKETING DATE] No keyword, date_auto_fallback=true, keeping current selection")
            else:
                debug.log(f"[HKTICKETING DATE] No keyword, date_auto_fallback=false, will select based on mode")

    debug.log("[HKTICKETING DATE] is_date_assigned:", is_date_assigned)

    formated_area_list = None
    is_page_ready = True

    if not is_date_assigned:
        # Get all date options
        area_list = None
        try:
            area_list = await tab.query_selector_all("#p > option")
        except Exception as exc:
            debug.log(f"[HKTICKETING DATE] find #p options date list fail: {exc}")

        if area_list:
            area_list_count = len(area_list)
            debug.log("[HKTICKETING DATE] date_list_count:", area_list_count)

            if area_list_count == 0:
                is_page_ready = False
            else:
                formated_area_list = []
                # Filter list
                for row in area_list:
                    row_text = ""
                    try:
                        row_html = await row.get_html()
                        row_text = util.remove_html_tags(row_html)
                    except Exception as exc:
                        debug.log("[HKTICKETING DATE] get row html error:", exc)
                        break

                    if len(row_text) > 0:
                        # Must contain year (20xx)
                        if '20' not in row_text:
                            row_text = ""
                        # Filter sold out dates
                        if ' Exhausted' in row_text:
                            row_text = ""
                        if 'No Longer On Sale' in row_text:
                            row_text = ""

                    if len(row_text) > 0:
                        formated_area_list.append(row)

        if formated_area_list:
            area_list_count = len(formated_area_list)
            debug.log("[HKTICKETING DATE] formated_area_list count:", area_list_count)

            if area_list_count > 0:
                if len(date_keyword) == 0:
                    matched_blocks = formated_area_list
                else:
                    debug.log("[HKTICKETING DATE] start to match keyword:", date_keyword)

                    matched_blocks = util.get_matched_blocks_by_keyword(config_dict, auto_select_mode, date_keyword, formated_area_list)

                    if debug.enabled:
                        if matched_blocks:
                            debug.log("[HKTICKETING DATE] after match keyword, found count:", len(matched_blocks))
            else:
                debug.log("[HKTICKETING DATE] not found date-time-position")
        else:
            debug.log("[HKTICKETING DATE] date date-time-position is None")

        # Fallback logic (FR-026)
        if not matched_blocks or len(matched_blocks) == 0:
            if date_auto_fallback and formated_area_list and len(formated_area_list) > 0:
                debug.log("[HKTICKETING DATE FALLBACK] date_auto_fallback=true, selecting from all available dates")
                matched_blocks = formated_area_list
            else:
                debug.log("[HKTICKETING DATE FALLBACK] date_auto_fallback=false, fallback is disabled")

        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
        if target_area:
            try:
                await target_area.click()
                is_date_assigned = True
                debug.log("[HKTICKETING DATE] Date selected successfully")
            except Exception as exc:
                debug.log(f"[HKTICKETING DATE] click target_area link fail: {exc}")

    return is_date_assigned, is_page_ready, formated_area_list

async def nodriver_hkticketing_date_password_input(tab, config_dict, fail_list):
    """
    Handle password protected date selection page
    Reference: chrome_tixcraft.py hkticketing_date_password_input (line 7681-7736)

    Returns:
        Tuple[bool, List[str]]:
            - is_password_appear: whether password input exists
            - fail_list: updated fail list
    """
    debug = util.create_debug_logger(config_dict)
    is_password_appear = False

    el_password = None
    try:
        my_css_selector = "#entitlementPassword > div > div > div > div > input[type='password']"
        el_password = await tab.query_selector(my_css_selector)
    except Exception as exc:
        pass

    if el_password:
        is_password_appear = True

        user_guess_string = config_dict["advanced"]["user_guess_string"]
        if len(user_guess_string) > 0:
            answer_list = user_guess_string.split(",")
            for answer_item in answer_list:
                answer_item = answer_item.strip()
                if answer_item in fail_list:
                    debug.log("[HKTICKETING PASSWORD] Skip failed password:", answer_item)
                    continue

                # Try this password
                try:
                    await el_password.click()
                    await el_password.send_keys(answer_item)
                    await el_password.send_keys(Keys.ENTER)

                    debug.log("[HKTICKETING PASSWORD] Tried password:", answer_item)

                    # Add to fail list (will be removed if successful)
                    if answer_item not in fail_list:
                        fail_list.append(answer_item)
                    break
                except Exception as exc:
                    debug.log("[HKTICKETING PASSWORD] Error:", exc)

    return is_password_appear, fail_list

async def nodriver_hkticketing_date_auto_select(tab, config_dict, fail_list):
    """
    Date auto select integration function
    Reference: chrome_tixcraft.py hkticketing_date_auto_select (line 7738-7821)

    Returns:
        Tuple[bool, List[str]]:
            - is_date_submiting: whether date is being submitted
            - fail_list: updated fail list
    """
    debug = util.create_debug_logger(config_dict)

    is_date_submiting = False

    is_date_assigned, is_page_ready, formated_area_list = await nodriver_hkticketing_date_assign(tab, config_dict)

    # Handle password input if needed
    is_password_appear, fail_list = await nodriver_hkticketing_date_password_input(tab, config_dict, fail_list)

    if is_date_assigned:
        is_button_clicked = await nodriver_hkticketing_date_buy_button_press(tab, config_dict)
        if is_button_clicked:
            is_date_submiting = True
            debug.log("[HKTICKETING DATE] Buy button clicked, submitting...")

    # Auto reload if page not ready
    if not is_page_ready:
        auto_reload_coming_soon_page = config_dict["tixcraft"].get("auto_reload_coming_soon_page", False)
        if auto_reload_coming_soon_page:
            debug.log("[HKTICKETING DATE] Page not ready, reloading...")

            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])

            try:
                await tab.reload()
            except Exception as exc:
                pass

    return is_date_submiting, fail_list

async def nodriver_hkticketing_area_auto_select(tab, config_dict, area_keyword_item):
    """
    Area auto select
    Reference: chrome_tixcraft.py hkticketing_area_auto_select (line 7822-7961)

    Returns:
        Tuple[bool, bool]:
            - is_need_refresh: whether page needs refresh
            - is_price_assign_by_bot: whether area has been selected
    """
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get("area_auto_fallback", False)

    is_need_refresh = False
    is_price_assign_by_bot = False

    debug.log("[HKTICKETING AREA] area_keyword:", area_keyword_item)

    # Wait for Angular to finish rendering
    await asyncio.sleep(random.uniform(0.3, 0.6))

    # Get all area options using JavaScript for Angular compatibility
    area_list = []
    try:
        area_count = await tab.evaluate('''
            (function() {
                const items = document.querySelectorAll('ul.seatarea > li');
                return items.length;
            })();
        ''')
        if area_count and area_count > 0:
            # Get elements one by one - select the <a> tag inside <li> for ng-click to work
            for i in range(area_count):
                try:
                    # Target the <a> tag with ng-click, not the <li>
                    el = await tab.query_selector(f'ul.seatarea > li:nth-child({i+1}) > a')
                    if el:
                        area_list.append(el)
                except:
                    pass
    except Exception as exc:
        debug.log(f"[HKTICKETING AREA] find area list fail: {exc}")

    if not area_list:
        return is_need_refresh, is_price_assign_by_bot

    area_list_count = len(area_list)
    debug.log("[HKTICKETING AREA] area_list_count:", area_list_count)

    if area_list_count == 0:
        return is_need_refresh, is_price_assign_by_bot

    # Check if any area is already selected
    is_area_selected = False
    try:
        selected_check = await tab.evaluate('''
            (function() {
                const items = document.querySelectorAll('#ticketSelectorContainer > ul > li');
                for (let item of items) {
                    if (item.classList.contains('selected')) return true;
                }
                return false;
            })();
        ''')
        is_area_selected = selected_check
    except Exception as exc:
        pass

    if is_area_selected:
        is_price_assign_by_bot = True
        debug.log("[HKTICKETING AREA] Area already selected")
        return is_need_refresh, is_price_assign_by_bot

    # Filter available areas - get all info in one JS call
    formated_area_list = []  # List of (element, text) tuples for NoDriver
    import json
    try:
        # Get all area info in single JavaScript call
        all_areas_info = await tab.evaluate('''
            (function() {
                var items = document.querySelectorAll('ul.seatarea > li');
                var results = [];
                for (var i = 0; i < items.length; i++) {
                    var item = items[i];
                    var nameEl = item.querySelector('.name');
                    var priceEl = item.querySelector('.price');
                    results.push({
                        className: item.className || '',
                        name: nameEl ? (nameEl.innerText || nameEl.textContent || '') : '',
                        price: priceEl ? (priceEl.innerText || priceEl.textContent || '') : ''
                    });
                }
                return JSON.stringify(results);
            })();
        ''')

        # Always print for debugging
        debug.log(f"[HKTICKETING AREA] JS raw type: {type(all_areas_info)}, value: {str(all_areas_info)[:300]}")

        # Parse JSON string
        if all_areas_info and isinstance(all_areas_info, str) and len(all_areas_info) > 2:
            areas_data = json.loads(all_areas_info)
            debug.log(f"[HKTICKETING AREA] Parsed {len(areas_data)} areas")

            for idx, info in enumerate(areas_data):
                class_name = info.get('className', '')
                name_text = info.get('name', '')
                price_text = info.get('price', '')
                row_text = f"{name_text} {price_text}".strip()

                debug.log(f"[HKTICKETING AREA] Item {idx}: class='{class_name}', name='{name_text}', price='{price_text}'")

                # Check if disabled or unavailable
                if 'disabled' in class_name or 'unavailable' in class_name:
                    debug.log(f"[HKTICKETING AREA] Item {idx}: skipped (unavailable)")
                    continue

                if len(row_text.strip()) == 0:
                    continue

                # Apply exclude keywords (returns True if matched = should exclude)
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    continue

                if idx < len(area_list):
                    # Store tuple of (element, text, index) for NoDriver keyword matching
                    formated_area_list.append((area_list[idx], row_text, idx))
                    debug.log(f"[HKTICKETING AREA] Added to list: idx={idx}, text={row_text[:40]}")
        else:
            debug.log("[HKTICKETING AREA] Invalid JS result, trying fallback")
    except Exception as exc:
        debug.log(f"[HKTICKETING AREA] Filter error: {exc}")

    debug.log("[HKTICKETING AREA] formated_area_list count:", len(formated_area_list))

    if len(formated_area_list) == 0:
        is_need_refresh = True
        return is_need_refresh, is_price_assign_by_bot

    # Match by keyword - same logic as Chrome version (line 7893-7934)
    matched_blocks = []
    matched_index = -1

    # Skip "Best available" special option when keyword is specified
    BEST_AVAILABLE_KEYWORDS = ['best available', 'best avail', '最佳']

    if len(area_keyword_item.strip()) == 0:
        # No keyword, use all areas (but skip "Best available" if there are other options)
        for element, row_text, orig_idx in formated_area_list:
            row_text_lower = row_text.lower()
            is_best_available = any(ba in row_text_lower for ba in BEST_AVAILABLE_KEYWORDS)
            if not is_best_available:
                matched_blocks.append(element)
        # If only "Best available" exists, use it
        if len(matched_blocks) == 0:
            matched_blocks = [item[0] for item in formated_area_list]
    else:
        # Parse keyword - use json.loads to properly handle quoted strings (same as util.py:1390)
        # Input format: "AAA","BBB CC","VIP 2" -> ['AAA', 'BBB CC', 'VIP 2']
        keyword_sets = util.parse_keyword_string_to_array(area_keyword_item)
        if not keyword_sets:
            # Fallback to simple split if json parsing fails
            keyword_sets = [kw.strip() for kw in area_keyword_item.split(',') if kw.strip()]

        debug.log(f"[HKTICKETING AREA] Keyword sets: {keyword_sets}")

        # Try each keyword set (OR logic between sets)
        for keyword_set in keyword_sets:
            for element, row_text, orig_idx in formated_area_list:
                # Skip "Best available" when using keywords
                row_text_lower = row_text.lower()
                is_best_available = any(ba in row_text_lower for ba in BEST_AVAILABLE_KEYWORDS)
                if is_best_available:
                    debug.log(f"[HKTICKETING AREA] Skipping 'Best available' option: {row_text[:40]}")
                    continue

                # Normalize text for comparison
                normalized_text = util.format_keyword_string(row_text)

                # AND logic within keyword set (space-separated keywords)
                # Same as Chrome version line 7920-7925
                keyword_parts = keyword_set.split(' ')
                is_match = True
                for kw in keyword_parts:
                    kw_formatted = util.format_keyword_string(kw)
                    if kw_formatted not in normalized_text:
                        is_match = False
                        break

                if is_match:
                    matched_blocks.append(element)
                    matched_index = orig_idx
                    debug.log(f"[HKTICKETING AREA] Keyword '{keyword_set}' matched: idx={orig_idx}, text={row_text[:50]}")
                    # For "from top to bottom" mode, only need first match
                    if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        break

            if len(matched_blocks) > 0:
                break  # Found matches with this keyword set, stop trying others

    if debug.enabled:
        if matched_blocks:
            debug.log("[HKTICKETING AREA] after match keyword, found count:", len(matched_blocks))

    # Fallback logic (FR-036)
    if not matched_blocks or len(matched_blocks) == 0:
        if area_auto_fallback and len(formated_area_list) > 0:
            debug.log("[HKTICKETING AREA FALLBACK] area_auto_fallback=true, selecting from all available areas")
            # Extract elements from tuples (element, text, index)
            matched_blocks = [item[0] for item in formated_area_list]
        else:
            debug.log("[HKTICKETING AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            is_need_refresh = True
            return is_need_refresh, is_price_assign_by_bot

    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if target_area:
        try:
            # Debug: get text of element we're about to click
            if debug.enabled:
                try:
                    click_text = await target_area.apply('(el) => el.innerText || el.textContent')
                    debug.log(f"[HKTICKETING AREA] About to click element: {str(click_text)[:60]}")
                except:
                    pass

            # Random delay before clicking (wait for Angular to stabilize)
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await target_area.click()
            is_price_assign_by_bot = True
            debug.log("[HKTICKETING AREA] Area selected successfully")
        except Exception as exc:
            debug.log(f"[HKTICKETING AREA] click target_area fail: {exc}")

    return is_need_refresh, is_price_assign_by_bot

async def nodriver_hkticketing_ticket_number_auto_select(tab, config_dict):
    """
    Auto select ticket number
    Reference: chrome_tixcraft.py hkticketing_ticket_number_auto_select (line 7962-7966)
    """
    debug = util.create_debug_logger(config_dict)
    ticket_number = config_dict["ticket_number"]

    is_ticket_number_assigned = False
    try:
        result = await tab.evaluate(f'''
            (function() {{
                const select = document.querySelector('select.shortSelect');
                if (!select) return JSON.stringify({{success: false, error: 'select not found'}});

                for (let i = 0; i < select.options.length; i++) {{
                    if (select.options[i].value == "{ticket_number}") {{
                        select.selectedIndex = i;
                        select.value = "{ticket_number}";

                        // Trigger events for Angular binding
                        select.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        select.dispatchEvent(new Event('change', {{ bubbles: true }}));

                        // Try to trigger Angular's ng-change
                        if (typeof angular !== 'undefined') {{
                            try {{
                                angular.element(select).triggerHandler('change');
                            }} catch(e) {{}}
                        }}

                        return JSON.stringify({{success: true, selected: select.value}});
                    }}
                }}
                return JSON.stringify({{success: false, error: 'value not found', options: select.options.length}});
            }})();
        ''')

        if result:
            import json
            result_obj = json.loads(result) if isinstance(result, str) else result
            is_ticket_number_assigned = result_obj.get('success', False) if isinstance(result_obj, dict) else result
            debug.log(f"[HKTICKETING TICKET] Set ticket number to {ticket_number}: {result}")
    except Exception as exc:
        debug.log("[HKTICKETING TICKET] Set ticket number fail:", exc)

    return is_ticket_number_assigned

async def nodriver_hkticketing_ticket_delivery_option(tab, config_dict=None):
    """
    Select ticket delivery option
    Reference: chrome_tixcraft.py hkticketing_ticket_delivery_option (line 8024-8063)
    """
    debug = util.create_debug_logger(config_dict)

    is_delivery_selected = False
    try:
        result = await tab.evaluate('''
            (function() {
                const select = document.querySelector('#selectDeliveryType');
                if (!select) return { found: false, selected: false };
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].value == "1") {
                        select.selectedIndex = i;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        return { found: true, selected: true, value: select.options[i].text };
                    }
                }
                return { found: true, selected: false };
            })();
        ''')
        if isinstance(result, dict):
            is_delivery_selected = result.get('selected', False)
            if debug.enabled:
                if result.get('found'):
                    if is_delivery_selected:
                        debug.log(f"[HKTICKETING DELIVERY] Selected: {result.get('value', 'N/A')}")
                    else:
                        debug.log("[HKTICKETING DELIVERY] Select found but value=1 not available")
                else:
                    debug.log("[HKTICKETING DELIVERY] #selectDeliveryType not found")
        else:
            is_delivery_selected = bool(result)
    except Exception as exc:
        debug.log(f"[HKTICKETING DELIVERY] Error: {exc}")

    return is_delivery_selected

async def nodriver_hkticketing_next_button_press(tab, config_dict=None):
    """
    Click next button and wait for URL change
    Reference: chrome_tixcraft.py hkticketing_next_button_press (line 7979-8001)
    """
    debug = util.create_debug_logger(config_dict)

    is_button_clicked = False

    # Get current URL before clicking
    current_url = ""
    try:
        current_url = await tab.evaluate('window.location.href')
    except:
        pass

    try:
        el_btn = await tab.query_selector('#continueBar > div.chooseTicketsOfferDiv > button')
        if el_btn:
            debug.log("[HKTICKETING NEXT] Found button, clicking...")
            await el_btn.click()
            is_button_clicked = True
            debug.log("[HKTICKETING NEXT] Button clicked successfully")
        else:
            debug.log("[HKTICKETING NEXT] Button not found on first attempt")
    except Exception as exc:
        debug.log(f"[HKTICKETING NEXT] First attempt error: {exc}")

    # Retry if first attempt failed
    if not is_button_clicked:
        await asyncio.sleep(0.2)
        try:
            el_btn = await tab.query_selector('#continueBar > div.chooseTicketsOfferDiv > button')
            if el_btn:
                debug.log("[HKTICKETING NEXT] Retry: Found button, clicking...")
                await el_btn.click()
                is_button_clicked = True
                debug.log("[HKTICKETING NEXT] Retry: Button clicked successfully")
            else:
                debug.log("[HKTICKETING NEXT] Retry: Button still not found")
        except Exception as exc:
            debug.log(f"[HKTICKETING NEXT] Retry error: {exc}")

    # Wait for URL change after clicking (prevent re-clicking)
    if is_button_clicked and current_url:
        debug.log("[HKTICKETING NEXT] Waiting for URL change...")
        max_wait = 10  # Max 10 seconds
        wait_interval = 0.5
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(wait_interval)
            waited += wait_interval
            try:
                new_url = await tab.evaluate('window.location.href')
                if new_url != current_url:
                    debug.log(f"[HKTICKETING NEXT] URL changed to: {new_url}")
                    break
            except:
                break
        if waited >= max_wait:
            debug.log("[HKTICKETING NEXT] URL change timeout")

    return is_button_clicked

async def nodriver_hkticketing_go_to_payment(tab, config_dict=None):
    """
    Click go to payment button and wait for URL change
    Reference: chrome_tixcraft.py hkticketing_go_to_payment (line 8002-8023)
    """
    debug = util.create_debug_logger(config_dict)

    is_button_clicked = False

    # Get current URL before clicking
    current_url = ""
    try:
        current_url = await tab.evaluate('window.location.href')
    except:
        pass

    try:
        el_btn = await tab.query_selector('#goToPaymentButton')
        if el_btn:
            debug.log("[HKTICKETING PAYMENT] Found button, clicking...")
            await el_btn.click()
            is_button_clicked = True
            debug.log("[HKTICKETING PAYMENT] Button clicked successfully")
    except Exception as exc:
        debug.log(f"[HKTICKETING PAYMENT] Click error: {exc}")

    # Wait for URL change after clicking (prevent re-clicking)
    if is_button_clicked and current_url:
        debug.log("[HKTICKETING PAYMENT] Waiting for URL change...")
        max_wait = 15  # Max 15 seconds for payment page
        wait_interval = 0.5
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(wait_interval)
            waited += wait_interval
            try:
                new_url = await tab.evaluate('window.location.href')
                if new_url != current_url:
                    debug.log(f"[HKTICKETING PAYMENT] URL changed to: {new_url}")
                    break
            except:
                break
        if waited >= max_wait:
            debug.log("[HKTICKETING PAYMENT] URL change timeout")

    return is_button_clicked

async def nodriver_hkticketing_hide_tickets_blocks(tab):
    """
    Hide unnecessary page blocks
    Reference: chrome_tixcraft.py hkticketing_hide_tickets_blocks (line 8064-8098)
    """
    try:
        await tab.evaluate('''
            (function() {
                const actionBlock = document.querySelector('.actionBlock');
                if (actionBlock) actionBlock.innerHTML = '';

                const detailModuleCopy = document.querySelector('.detailModuleCopy');
                if (detailModuleCopy) detailModuleCopy.innerHTML = '';

                const mapWrapper = document.querySelector('.mapWrapper');
                if (mapWrapper) mapWrapper.innerHTML = '';
            })();
        ''')
    except Exception as exc:
        pass

# =============================================================================
# HKTicketing Type 02 Functions (hkt.hkticketing.com SPA)
# URL pattern: hkt.hkticketing.com/hant/#/allEvents/detail/selectTicket
# =============================================================================

async def nodriver_hkticketing_type02_clear_session(tab, config_dict=None):
    """
    Clear cookies and localStorage before login to ensure clean session
    This helps avoid stale session data causing login issues
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # Clear localStorage related to HKTicketing session
        result = await tab.evaluate('''
            (function() {
                var cleared = [];
                try {
                    // Clear specific HKTicketing session keys
                    var keysToRemove = ['ACCOUNT_INFO', 'TOKEN', 'USER_INFO', 'SESSION'];
                    for (var key of keysToRemove) {
                        if (localStorage.getItem(key)) {
                            localStorage.removeItem(key);
                            cleared.push(key);
                        }
                    }
                    // Also check for any keys containing 'token' or 'session'
                    for (var i = 0; i < localStorage.length; i++) {
                        var k = localStorage.key(i);
                        if (k && (k.toLowerCase().includes('token') || k.toLowerCase().includes('session') || k.toLowerCase().includes('account'))) {
                            localStorage.removeItem(k);
                            cleared.push(k);
                        }
                    }
                } catch (e) {}
                return { success: true, cleared: cleared };
            })()
        ''')

        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None

        if result and isinstance(result, dict):
            cleared = result.get('cleared', [])
            if cleared:
                debug.log(f"[HKTICKETING TYPE02] Cleared localStorage keys: {cleared}")

        # Clear cookies via CDP
        try:
            import zendriver.cdp.network as cdp_network
            await tab.send(cdp_network.clear_browser_cookies())
            debug.log("[HKTICKETING TYPE02] Browser cookies cleared")
        except Exception as cdp_exc:
            debug.log(f"[HKTICKETING TYPE02] CDP cookie clear error: {cdp_exc}")

        return True

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Clear session error: {exc}")
        return False

async def nodriver_hkticketing_type02_check_traffic_overload(tab, config_dict=None):
    """
    Check if page shows traffic overload message and click refresh button if found
    Detection: button.mz-no-data-btn with text "刷新"

    Returns:
        bool: True if traffic overload was detected (and refresh clicked), False otherwise
    """
    debug = util.create_debug_logger(config_dict)

    try:
        result = await tab.evaluate('''
            (function() {
                // Look for the refresh button that indicates traffic overload
                var refreshBtn = document.querySelector('button.mz-no-data-btn');
                if (refreshBtn) {
                    var text = refreshBtn.textContent || refreshBtn.innerText || '';
                    if (text.includes('刷新') || text.includes('重試') || text.includes('Refresh')) {
                        refreshBtn.click();
                        return { found: true, clicked: true, text: text.trim() };
                    }
                }

                // Also check for any large primary button with refresh text
                var buttons = document.querySelectorAll('button.bui-btn-large, button.bui-btn-primary');
                for (var btn of buttons) {
                    var btnText = btn.textContent || btn.innerText || '';
                    if (btnText.includes('刷新') || btnText.includes('重試') || btnText.includes('重新載入')) {
                        btn.click();
                        return { found: true, clicked: true, text: btnText.trim() };
                    }
                }

                // Check for error/loading page indicators
                var noDataDiv = document.querySelector('.mz-no-data, [class*="no-data"], [class*="error-page"]');
                if (noDataDiv) {
                    return { found: true, clicked: false, reason: 'no_data_page_detected' };
                }

                return { found: false };
            })()
        ''')

        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None

        if result and isinstance(result, dict) and result.get('found'):
            if result.get('clicked'):
                debug.log(f"[HKTICKETING TYPE02] Traffic overload detected, clicked refresh: {result.get('text')}")
            else:
                debug.log(f"[HKTICKETING TYPE02] No data page detected: {result.get('reason')}")
            return True

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Traffic check error: {exc}")

    return False

async def nodriver_hkticketing_type02_login(tab, config_dict):
    """
    Semi-automatic login for hkt.hkticketing.com (Type 02 SPA)

    Flow:
    1. Auto-fill account/password
    2. Auto-click login button
    3. User manually handles captcha
    4. Wait for login to complete (max 180 seconds)

    Args:
        tab: browser tab
        config_dict: config dictionary

    Returns:
        bool: whether login was successful
    """
    debug = util.create_debug_logger(config_dict)

    # Get account credentials (password already decrypted in settings.py)
    hkticketing_account = config_dict["accounts"]["hkticketing_account"].strip()
    hkticketing_password = config_dict["accounts"]["hkticketing_password"].strip()

    if not hkticketing_account or not hkticketing_password:
        print("[HKTICKETING TYPE02] No account/password configured, please login manually")
        return False

    # Clear existing session data before login to avoid stale session issues
    print("[HKTICKETING TYPE02] Clearing session data before login...")
    await nodriver_hkticketing_type02_clear_session(tab, config_dict)
    await asyncio.sleep(0.3)

    print("[HKTICKETING TYPE02] Starting semi-automatic login...")

    # Step 1: Fill account
    account_filled = False
    account_selectors = [
        'input[name="userEmail"]',
        'input[placeholder*="電子郵件"]',
        'input[placeholder*="email"]',
        'input[type="text"].bui-input-input',
    ]

    for selector in account_selectors:
        try:
            el_account = await tab.query_selector(selector)
            if el_account:
                await el_account.click()
                await el_account.clear_input()
                await el_account.send_keys(hkticketing_account)
                account_filled = True
                debug.log(f"[HKTICKETING TYPE02] Account filled using: {selector}")
                break
        except Exception as exc:
            debug.log(f"[HKTICKETING TYPE02] Account selector failed: {selector}, {exc}")
            continue

    if not account_filled:
        print("[HKTICKETING TYPE02] Failed to fill account")
        return False

    await asyncio.sleep(0.3)

    # Step 2: Fill password
    password_filled = False
    password_selectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[placeholder*="密碼"]',
    ]

    for selector in password_selectors:
        try:
            el_password = await tab.query_selector(selector)
            if el_password:
                await el_password.click()
                await el_password.clear_input()
                await el_password.send_keys(hkticketing_password)
                password_filled = True
                debug.log(f"[HKTICKETING TYPE02] Password filled using: {selector}")
                break
        except Exception as exc:
            debug.log(f"[HKTICKETING TYPE02] Password selector failed: {selector}, {exc}")
            continue

    if not password_filled:
        print("[HKTICKETING TYPE02] Failed to fill password")
        return False

    await asyncio.sleep(0.3)

    # Step 3: Click login button
    login_clicked = False
    login_btn_selectors = [
        'button.register-button',
        'button.mz-button.register-button',
        'button.bui-btn-primary',
    ]

    for selector in login_btn_selectors:
        try:
            el_login_btn = await tab.query_selector(selector)
            if el_login_btn:
                # Check if button text contains "登入"
                btn_text = await tab.evaluate(f'''
                    (function() {{
                        var btn = document.querySelector('{selector}');
                        return btn ? btn.textContent : '';
                    }})();
                ''')
                if '登入' in str(btn_text) or 'Login' in str(btn_text):
                    await el_login_btn.click()
                    login_clicked = True
                    debug.log(f"[HKTICKETING TYPE02] Login button clicked using: {selector}")
                    break
        except Exception as exc:
            debug.log(f"[HKTICKETING TYPE02] Login button selector failed: {selector}, {exc}")
            continue

    if not login_clicked:
        print("[HKTICKETING TYPE02] Failed to click login button, please click manually")

    print("[HKTICKETING TYPE02] Please complete captcha verification if prompted...")
    print("[HKTICKETING TYPE02] Waiting for login to complete (max 180 seconds)...")

    # Step 4: Wait for login to complete - simply check URL change
    import time
    timeout = 180  # 3 minutes
    start_time = time.time()
    check_interval = 2

    while (time.time() - start_time) < timeout:
        try:
            # Check URL change (no longer on login page)
            current_url = await tab.evaluate('window.location.href')
            if '#/login' not in current_url:
                print("[HKTICKETING TYPE02] Login successful (URL changed)")
                return True

            # Progress indicator every 30 seconds
            elapsed = int(time.time() - start_time)
            if elapsed > 0 and elapsed % 30 == 0:
                print(f"[HKTICKETING TYPE02] Waiting for login... ({elapsed}s / {timeout}s)")

        except Exception:
            pass  # Silently ignore connection errors during wait

        await asyncio.sleep(check_interval)

    print("[HKTICKETING TYPE02] Login timeout, please check manually")
    return False

async def nodriver_hkticketing_type02_dismiss_modal(tab, config_dict=None):
    """
    Dismiss modal dialog on Type 02 event page

    DOM Structure:
    - Modal: div.bui-modal.modalAndDrawer___MMXN3
    - Button: div.modalAndDrawerFooter > div > button

    Returns:
        bool: whether modal was dismissed
    """
    debug = util.create_debug_logger(config_dict)

    try:
        result = await tab.evaluate('''
            (function() {
                // Try multiple selectors for modal button
                var selectors = [
                    'div.modalAndDrawerFooter > div > button',
                    'div.modalAndDrawerFooter button',
                    '.bui-modal button',
                    '.modalAndDrawer___MMXN3 button'
                ];

                for (var i = 0; i < selectors.length; i++) {
                    var btn = document.querySelector(selectors[i]);
                    if (btn && btn.offsetParent !== null) {
                        // Scroll button into view first (needed for English version)
                        btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                        btn.click();
                        return { success: true, selector: selectors[i] };
                    }
                }
                return { success: false, error: 'no modal button found' };
            })();
        ''')

        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None

        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Modal dismissed via: {result.get('selector')}")
            return True

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Dismiss modal error: {exc}")

    return False

async def nodriver_hkticketing_type02_event_page_buy_button(tab, config_dict=None):
    """
    Click buy ticket button on Type 02 event page to enter ticket selection

    DOM Structure:
    - Container: div.pcBottomBtn___NiJXB
    - Button: button (contains text like "立即購票", "Buy Now", etc.)

    Returns:
        bool: whether button was clicked
    """
    debug = util.create_debug_logger(config_dict)

    try:
        result = await tab.evaluate('''
            (function() {
                // Try multiple selectors for buy button
                var selectors = [
                    'div.pcBottomBtn___NiJXB button',
                    'div.pcBottomBtn___NiJXB > button',
                    '.ticketInfoWrapper___n2g2e button',
                    'button.buyBtn___'
                ];

                for (var i = 0; i < selectors.length; i++) {
                    var btn = document.querySelector(selectors[i]);
                    if (btn && btn.offsetParent !== null) {
                        var text = btn.innerText || '';
                        btn.click();
                        return { success: true, selector: selectors[i], text: text };
                    }
                }

                // Fallback: find any button with buy-related text
                var buttons = document.querySelectorAll('button');
                for (var j = 0; j < buttons.length; j++) {
                    var btnText = buttons[j].innerText || '';
                    if (btnText.includes('購票') || btnText.includes('Buy') ||
                        btnText.includes('立即') || btnText.includes('選購')) {
                        buttons[j].click();
                        return { success: true, selector: 'fallback', text: btnText };
                    }
                }

                return { success: false, error: 'no buy button found' };
            })();
        ''')

        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None

        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Buy button clicked: {result.get('text')} via {result.get('selector')}")
            return True

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Buy button error: {exc}")

    return False

async def nodriver_hkticketing_type02_event_page(tab, config_dict):
    """
    Handle Type 02 event page (even.html)
    - Dismiss any modal dialogs
    - Click buy button to enter ticket selection page

    Returns:
        bool: whether successfully navigated to ticket selection
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[HKTICKETING TYPE02] Processing event page...")

    # Step 1: Wait for page to load and dismiss any modal dialogs
    await asyncio.sleep(1.0)
    modal_dismissed = await nodriver_hkticketing_type02_dismiss_modal(tab, config_dict)
    if modal_dismissed:
        debug.log("[HKTICKETING TYPE02] Modal dialog dismissed")
        await asyncio.sleep(0.5)

    # Step 2: Click buy button
    await asyncio.sleep(0.3)
    is_clicked = await nodriver_hkticketing_type02_event_page_buy_button(tab, config_dict)

    if is_clicked:
        debug.log("[HKTICKETING TYPE02] Navigating to ticket selection page...")
        await asyncio.sleep(0.5)

    return is_clicked

async def nodriver_hkticketing_type02_date_assign(tab, config_dict):
    """
    Type 02 date selection for hkt.hkticketing.com SPA pages

    DOM Structure:
    - Container: div.sessionListWrapper___gDIN1
    - Items: div.sessionList___al29_
    - Selected: has class fouceStyle___Qr7dA
    - Text: div.eventCaption___LUOTP > span

    Returns:
        bool: whether a date has been selected
    """
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get("date_auto_fallback", False)

    debug.log("[HKTICKETING TYPE02 DATE] date_keyword:", date_keyword)

    date_keyword = util.format_keyword_string(date_keyword)

    # Wait for date elements to be rendered (SPA page)
    date_info = None
    for wait_attempt in range(10):
        try:
            date_info = await tab.evaluate('''
                (function() {
                    var items = document.querySelectorAll('div.sessionList___al29_');
                    return items.length;
                })();
            ''')
            if date_info and int(date_info) > 0:
                debug.log(f"[HKTICKETING TYPE02 DATE] Found {date_info} date elements after {wait_attempt + 1} attempts")
                break
        except Exception:
            pass
        await asyncio.sleep(0.3)

    if not date_info or int(date_info) == 0:
        debug.log("[HKTICKETING TYPE02 DATE] No date elements found after waiting")
        return False

    # Get all date items via JavaScript
    is_date_assigned = False
    try:
        date_info = await tab.evaluate('''
            (function() {
                var items = document.querySelectorAll('div.sessionList___al29_');
                var results = [];
                for (var i = 0; i < items.length; i++) {
                    var item = items[i];
                    var textEl = item.querySelector('span');
                    var text = textEl ? textEl.innerText.trim() : item.innerText.trim();
                    var isSelected = item.className.includes('fouceStyle');
                    results.push({
                        index: i,
                        text: text,
                        isSelected: isSelected
                    });
                }
                return JSON.stringify(results);
            })();
        ''')

        if date_info and isinstance(date_info, str) and len(date_info) > 2:
            import json
            dates_data = json.loads(date_info)

            if debug.enabled:
                debug.log(f"[HKTICKETING TYPE02 DATE] Found {len(dates_data)} dates")
                for d in dates_data:
                    debug.log(f"  [{d['index']}] {d['text']} {'(selected)' if d['isSelected'] else ''}")

            # Check if already selected AND matches keyword
            selected_date_text = None
            for d in dates_data:
                if d['isSelected']:
                    selected_date_text = d['text']
                    debug.log(f"[HKTICKETING TYPE02 DATE] Currently selected: {d['text']}")
                    break

            # If a date is selected, check if it matches the keyword
            if selected_date_text and len(date_keyword) > 0:
                # Check if selected date matches keyword
                normalized_selected = util.format_keyword_string(selected_date_text)
                keyword_sets = util.parse_keyword_string_to_array(date_keyword)
                if not keyword_sets:
                    keyword_sets = [kw.strip() for kw in date_keyword.split(',') if kw.strip()]

                for keyword_set in keyword_sets:
                    keyword_parts = keyword_set.split(' ') if isinstance(keyword_set, str) else [str(keyword_set)]
                    is_match = True
                    for kw in keyword_parts:
                        kw_formatted = util.format_keyword_string(str(kw))
                        if kw_formatted not in normalized_selected:
                            is_match = False
                            break
                    if is_match:
                        is_date_assigned = True
                        debug.log(f"[HKTICKETING TYPE02 DATE] Selected date matches keyword, keeping selection")
                        break

                if not is_date_assigned:
                    debug.log(f"[HKTICKETING TYPE02 DATE] Selected date does not match keyword, will select target date")
            elif selected_date_text and len(date_keyword) == 0:
                # No keyword = any date is acceptable. Keep current selection unconditionally.
                # Matches Type01 area "already selected" pattern (line 21279-21298).
                is_date_assigned = True
                debug.log(f"[HKTICKETING TYPE02 DATE] No keyword, keeping current selection: {selected_date_text}")

            if not is_date_assigned and len(dates_data) > 0:
                # Get actual elements for clicking
                date_elements = await tab.query_selector_all('div.sessionList___al29_')
                if not date_elements:
                    return False

                # Build list for keyword matching
                formated_list = []
                for i, d in enumerate(dates_data):
                    if i < len(date_elements):
                        formated_list.append((date_elements[i], d['text'], i))

                matched_blocks = []

                if len(date_keyword) == 0:
                    # No keyword, use all dates
                    matched_blocks = [item[0] for item in formated_list]
                else:
                    # Parse keywords
                    keyword_sets = util.parse_keyword_string_to_array(date_keyword)
                    if not keyword_sets:
                        keyword_sets = [kw.strip() for kw in date_keyword.split(',') if kw.strip()]

                    debug.log(f"[HKTICKETING TYPE02 DATE] Keyword sets: {keyword_sets}")

                    # Try each keyword set (OR logic)
                    for keyword_set in keyword_sets:
                        for element, row_text, idx in formated_list:
                            normalized_text = util.format_keyword_string(row_text)

                            # AND logic within keyword set
                            keyword_parts = keyword_set.split(' ') if isinstance(keyword_set, str) else [str(keyword_set)]
                            is_match = True
                            for kw in keyword_parts:
                                kw_formatted = util.format_keyword_string(str(kw))
                                if kw_formatted not in normalized_text:
                                    is_match = False
                                    break

                            if is_match:
                                matched_blocks.append(element)
                                debug.log(f"[HKTICKETING TYPE02 DATE] Matched: {row_text}")
                                if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                    break

                        if len(matched_blocks) > 0:
                            break

                # Fallback logic
                if not matched_blocks and date_auto_fallback and len(formated_list) > 0:
                    debug.log("[HKTICKETING TYPE02 DATE] Fallback enabled, using all dates")
                    matched_blocks = [item[0] for item in formated_list]

                # Select target
                target = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
                if target:
                    try:
                        await target.click()
                        is_date_assigned = True
                        debug.log("[HKTICKETING TYPE02 DATE] Date clicked successfully")
                        await asyncio.sleep(0.3)
                    except Exception as exc:
                        debug.log(f"[HKTICKETING TYPE02 DATE] Click error: {exc}")

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02 DATE] Error: {exc}")

    return is_date_assigned

async def nodriver_hkticketing_type02_area_auto_select(tab, config_dict, area_keyword_item):
    """
    Type 02 area selection for hkt.hkticketing.com SPA pages

    DOM Structure:
    - Container: div.levelInfo___ucWy8
    - Items: div.levelItem___rPZ55
    - Disabled: has class disableClass___BDFqG
    - Text: span.ticketInfoContainer___dLjRV > span

    Returns:
        Tuple[bool, bool]: (is_need_refresh, is_area_assigned)
    """
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get("area_auto_fallback", False)

    is_need_refresh = False
    is_area_assigned = False

    debug.log("[HKTICKETING TYPE02 AREA] area_keyword:", area_keyword_item)

    # Wait for render
    await asyncio.sleep(random.uniform(0.2, 0.4))

    try:
        # Get all area info via JavaScript
        area_info = await tab.evaluate('''
            (function() {
                var items = document.querySelectorAll('div.levelItem___rPZ55');
                var results = [];
                for (var i = 0; i < items.length; i++) {
                    var item = items[i];
                    var textEl = item.querySelector('span.ticketInfoContainer___dLjRV span');
                    var text = textEl ? textEl.innerText.trim() : '';
                    var isDisabled = item.className.includes('disableClass');
                    var signEl = item.querySelector('div.sign___gTvXe');
                    var status = signEl ? signEl.innerText.trim() : '';
                    results.push({
                        index: i,
                        text: text,
                        isDisabled: isDisabled,
                        status: status
                    });
                }
                return JSON.stringify(results);
            })();
        ''')

        if area_info and isinstance(area_info, str) and len(area_info) > 2:
            import json
            areas_data = json.loads(area_info)

            if debug.enabled:
                debug.log(f"[HKTICKETING TYPE02 AREA] Found {len(areas_data)} areas")
                for a in areas_data:
                    status_str = f" [{a['status']}]" if a['status'] else ""
                    disabled_str = " (disabled)" if a['isDisabled'] else ""
                    debug.log(f"  [{a['index']}] {a['text']}{status_str}{disabled_str}")

            # Get actual elements
            area_elements = await tab.query_selector_all('div.levelItem___rPZ55')
            if not area_elements:
                is_need_refresh = True
                return is_need_refresh, is_area_assigned

            # Build list of available areas
            formated_list = []
            for i, a in enumerate(areas_data):
                if a['isDisabled']:
                    continue
                if i < len(area_elements):
                    formated_list.append((area_elements[i], a['text'], i))

            if len(formated_list) == 0:
                is_need_refresh = True
                return is_need_refresh, is_area_assigned

            matched_blocks = []

            if len(area_keyword_item.strip()) == 0:
                # No keyword, use all available areas
                matched_blocks = [item[0] for item in formated_list]
            else:
                # Parse keywords
                keyword_sets = util.parse_keyword_string_to_array(area_keyword_item)
                if not keyword_sets:
                    keyword_sets = [kw.strip() for kw in area_keyword_item.split(',') if kw.strip()]

                debug.log(f"[HKTICKETING TYPE02 AREA] Keyword sets: {keyword_sets}")

                # Try each keyword set (OR logic)
                for keyword_set in keyword_sets:
                    for element, row_text, idx in formated_list:
                        normalized_text = util.format_keyword_string(row_text)

                        # AND logic within keyword set
                        keyword_parts = keyword_set.split(' ') if isinstance(keyword_set, str) else [str(keyword_set)]
                        is_match = True
                        for kw in keyword_parts:
                            kw_formatted = util.format_keyword_string(str(kw))
                            if kw_formatted not in normalized_text:
                                is_match = False
                                break

                        if is_match:
                            matched_blocks.append(element)
                            debug.log(f"[HKTICKETING TYPE02 AREA] Matched: {row_text}")
                            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                break

                    if len(matched_blocks) > 0:
                        break

            # Fallback logic
            if not matched_blocks and area_auto_fallback and len(formated_list) > 0:
                debug.log("[HKTICKETING TYPE02 AREA] Fallback enabled, using all areas")
                matched_blocks = [item[0] for item in formated_list]

            if not matched_blocks:
                is_need_refresh = True
                return is_need_refresh, is_area_assigned

            # Select target
            target = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
            if target:
                try:
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                    await target.click()
                    is_area_assigned = True
                    debug.log("[HKTICKETING TYPE02 AREA] Area clicked successfully")
                except Exception as exc:
                    debug.log(f"[HKTICKETING TYPE02 AREA] Click error: {exc}")

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02 AREA] Error: {exc}")

    return is_need_refresh, is_area_assigned

async def nodriver_hkticketing_type02_ticket_number_select(tab, config_dict):
    """
    Type 02 ticket number selection using per-click evaluate pattern.

    React 18 batches synchronous state updates, so clicking N times
    in a single JS execution only registers as 1 click. Each click
    must be a separate tab.evaluate() call with a delay between them.

    DOM Structure:
    - Container: div.buyNum___a5xrK
    - spans[0]: - button (decrease)
    - spans[1]: current number display
    - spans[2]: + button (increase)

    Returns:
        bool: whether ticket number was set
    """
    debug = util.create_debug_logger(config_dict)
    ticket_number = config_dict.get("ticket_number", 2)

    if ticket_number < 1:
        ticket_number = 1

    debug.log(f"[HKTICKETING TYPE02 TICKET] Target ticket number: {ticket_number}")

    try:
        # Phase A: Read current quantity
        js_read_qty = '''
        (function() {
            var buyNum = document.querySelector('div.buyNum___a5xrK');
            if (!buyNum) return {success: false, error: 'buyNum_not_found'};
            var spans = buyNum.querySelectorAll(':scope > span');
            if (spans.length < 3) return {success: false, error: 'spans_not_found'};
            var num = parseInt(spans[1].innerText);
            if (isNaN(num)) return {success: false, error: 'num_parse_failed'};
            return {success: true, current: num};
        })()
        '''
        result = await tab.evaluate(js_read_qty)
        result = util.parse_nodriver_result(result)
        if not (isinstance(result, dict) and result.get('success')):
            error_msg = result.get('error', 'unknown') if isinstance(result, dict) else 'no_result'
            debug.log(f"[HKTICKETING TYPE02 TICKET] Read qty failed: {error_msg}")
            return False

        current_num = result['current']
        clicks_needed = ticket_number - current_num

        debug.log(f"[HKTICKETING TYPE02 TICKET] Current: {current_num}, Target: {ticket_number}, Clicks needed: {clicks_needed}")

        if clicks_needed == 0:
            return True

        # Phase B: Click one at a time with random delay
        # spans[2] = + button, spans[0] = - button
        btn_index = 2 if clicks_needed > 0 else 0
        js_click_once = '''
        (function() {
            var buyNum = document.querySelector('div.buyNum___a5xrK');
            if (!buyNum) return {success: false, error: 'buyNum_not_found'};
            var spans = buyNum.querySelectorAll(':scope > span');
            if (spans.length < 3) return {success: false, error: 'spans_not_found'};
            spans[%d].click();
            return {success: true};
        })()
        ''' % btn_index

        for i in range(abs(clicks_needed)):
            click_result = await tab.evaluate(js_click_once)
            click_result = util.parse_nodriver_result(click_result)
            if not (isinstance(click_result, dict) and click_result.get('success')):
                error_msg = click_result.get('error', 'unknown') if isinstance(click_result, dict) else 'no_result'
                debug.log(f"[HKTICKETING TYPE02 TICKET] Click {i+1} failed: {error_msg}")
                return False
            if i < abs(clicks_needed) - 1:
                await asyncio.sleep(random.uniform(0.05, 0.1))

        # Phase C: Verify final quantity
        await asyncio.sleep(random.uniform(0.05, 0.1))
        verify_result = await tab.evaluate(js_read_qty)
        verify_result = util.parse_nodriver_result(verify_result)

        if isinstance(verify_result, dict) and verify_result.get('success'):
            final_num = verify_result['current']
            debug.log(f"[HKTICKETING TYPE02 TICKET] Verified: {final_num} (target: {ticket_number})")
            return final_num == ticket_number

        debug.log("[HKTICKETING TYPE02 TICKET] Verify read failed")
        return False

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02 TICKET] Error: {exc}")

    return False

async def nodriver_hkticketing_type02_next_button_press(tab, config_dict=None):
    """
    Click the next step button on Type 02 page

    Returns:
        bool: whether button was clicked
    """
    debug = util.create_debug_logger(config_dict)

    is_button_clicked = False

    try:
        # Find button containing "下一步" text
        button_clicked = await tab.evaluate('''
            (function() {
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    if (btn.innerText.includes('下一步') || btn.innerText.includes('Next')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            })();
        ''')

        if button_clicked:
            is_button_clicked = True
            debug.log("[HKTICKETING TYPE02] Next button clicked")

    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Next button error: {exc}")

    return is_button_clicked

async def nodriver_hkticketing_type02_performance(tab, config_dict):
    """
    Type 02 ticket selection page integration flow
    Handles date selection and area selection on same page

    Returns:
        bool: whether flow completed successfully
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[HKTICKETING TYPE02] Starting Type 02 flow...")

    # Step 1: Date selection
    is_date_assigned = False
    if config_dict["date_auto_select"]["enable"]:
        is_date_assigned = await nodriver_hkticketing_type02_date_assign(tab, config_dict)
        debug.log(f"[HKTICKETING TYPE02] Date assigned: {is_date_assigned}")
    else:
        is_date_assigned = True  # Skip if disabled

    if not is_date_assigned:
        return False

    # Step 2: Area selection
    is_area_assigned = False
    if config_dict["area_auto_select"]["enable"]:
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        is_need_refresh, is_area_assigned = await nodriver_hkticketing_type02_area_auto_select(
            tab, config_dict, area_keyword
        )
        debug.log(f"[HKTICKETING TYPE02] Area assigned: {is_area_assigned}")
    else:
        is_area_assigned = True  # Skip if disabled

    if not is_area_assigned:
        return False

    # Step 3: Ticket number selection (after area is selected, quantity selector appears)
    await asyncio.sleep(0.3)
    is_ticket_number_set = await nodriver_hkticketing_type02_ticket_number_select(tab, config_dict)
    debug.log(f"[HKTICKETING TYPE02] Ticket number set: {is_ticket_number_set}")
    if not is_ticket_number_set:
        return False

    # Step 4: Click next button
    await asyncio.sleep(0.3)
    await nodriver_hkticketing_type02_next_button_press(tab, config_dict)

    return True

async def nodriver_hkticketing_type02_confirm_order(tab, config_dict):
    """
    Handle HKTicketing Type02 confirm order page (#/confirmOrder)
    Flow:
    1. Select delivery method (QRcode/二維碼取票)
    2. Click agree checkbox (SVG icon)
    3. Click "同意" button in popup dialog
    4. Click submit button (分配座位)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[HKTICKETING TYPE02] Processing confirm order page...")

    # Wait for page to fully load (SPA needs more time)
    await asyncio.sleep(2.5)

    # Step 1: Select delivery method (QRcode)
    # The delivery method might already be selected, but we click it to ensure
    delivery_js = '''
    (function() {
        // Look for QRcode delivery option
        const methods = document.querySelectorAll('.method-item, [class*="method"]');
        for (const m of methods) {
            const text = m.textContent || m.innerText || '';
            if (text.includes('二維碼') || text.includes('QR') || text.includes('電子')) {
                if (!m.classList.contains('method-active')) {
                    m.click();
                    return {success: true, text: text, action: 'clicked'};
                }
                return {success: true, text: text, action: 'already_selected'};
            }
        }
        // If no QRcode found, check if any method is already selected
        const active = document.querySelector('.method-active, [class*="method"][class*="active"]');
        if (active) {
            return {success: true, text: active.textContent, action: 'default_selected'};
        }
        return {success: false, error: 'no_delivery_method_found'};
    })()
    '''
    try:
        result = await tab.evaluate(delivery_js)
        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None
        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Delivery method: {result.get('text')} ({result.get('action')})")
    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Delivery method error: {exc}")

    await asyncio.sleep(0.3)

    # Step 2: Click agree checkbox
    # Pattern 1: Look for agreements container with checkbox
    # Pattern 2: span.agreementIcon___ with SVG (class contains agreementIcon___)
    # Pattern 3: SVG with #icon-weixuanzhong (unchecked) / #icon-xuanzhong (checked)
    agree_js = '''
    (function() {
        // Helper function to get href from use element (handles xlink:href and href)
        function getUseHref(useElem) {
            return useElem.getAttribute('xlink:href') || useElem.getAttribute('href') || useElem.href?.baseVal || '';
        }

        // Pattern 1: Look for checkbox in agreements container (most reliable for HKTicketing)
        const agreementsContainer = document.querySelector('[class*="agreements"], [class*="agreementCheckBox"]');
        if (agreementsContainer) {
            // Find all use elements and check their href
            const uses = agreementsContainer.querySelectorAll('use');
            for (const use of uses) {
                const href = getUseHref(use);
                if (href === '#icon-weixuanzhong') {
                    // Click the parent span (the clickable element)
                    const clickTarget = use.closest('span[role="img"]') || use.closest('span') || use.closest('svg');
                    if (clickTarget) {
                        clickTarget.click();
                        return {success: true, action: 'agreements_container_checkbox_clicked'};
                    }
                }
            }
            // Check if already checked
            for (const use of uses) {
                const href = getUseHref(use);
                if (href === '#icon-xuanzhong' || href === '#icon-yixuanzhong') {
                    return {success: true, action: 'agreements_container_already_checked'};
                }
            }
        }

        // Pattern 2: Look for agreementIcon span (HKTicketing specific)
        // When unselected: class contains "agreementIcon___" but NOT "Selected"
        // When selected: class contains "agreementIconSelected___"
        const agreementIcons = document.querySelectorAll('span[class*="agreementIcon"]');
        for (const icon of agreementIcons) {
            const classList = icon.className || '';
            // Check if it's NOT selected (no "Selected" in class name)
            if (classList.includes('agreementIcon') && !classList.includes('Selected')) {
                icon.click();
                return {success: true, action: 'agreementIcon_clicked'};
            }
        }
        // Check if agreementIcon is already selected
        for (const icon of agreementIcons) {
            const classList = icon.className || '';
            if (classList.includes('Selected')) {
                return {success: true, action: 'agreementIcon_already_selected'};
            }
        }

        // Pattern 3: Look for unchecked checkbox by xlink:href (general pattern)
        const allUses = document.querySelectorAll('use');
        for (const use of allUses) {
            const href = getUseHref(use);
            if (href === '#icon-weixuanzhong') {
                // Find the clickable parent
                let clickTarget = use.closest('span[role="img"]') || use.closest('span') || use.closest('svg');
                if (clickTarget) {
                    // Make sure it's in a checkbox context (not a general icon)
                    const parent = clickTarget.closest('[class*="agreement"], [class*="checkbox"], [class*="check"]');
                    if (parent) {
                        clickTarget.click();
                        return {success: true, action: 'svg_checkbox_clicked'};
                    }
                }
            }
        }
        // Check if SVG checkbox already checked (by searching all uses)
        for (const use of allUses) {
            const href = getUseHref(use);
            if (href === '#icon-xuanzhong' || href === '#icon-yixuanzhong') {
                const parent = use.closest('[class*="agreement"], [class*="checkbox"]');
                if (parent) {
                    return {success: true, action: 'svg_already_checked'};
                }
            }
        }

        // Fallback: look for any checkbox-like element
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:not(:checked), [class*="checkbox"]:not([class*="checked"])');
        for (const cb of checkboxes) {
            cb.click();
            return {success: true, action: 'fallback_checkbox_clicked'};
        }
        return {success: false, error: 'no_checkbox_found', debug: 'agreements_found:' + !!agreementsContainer + ',uses_count:' + allUses.length};
    })()
    '''
    try:
        result = await tab.evaluate(agree_js)
        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None
        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Agree checkbox: {result.get('action')}")
        else:
            debug_info = result.get('debug', '') if result and isinstance(result, dict) else ''
            debug.log(f"[HKTICKETING TYPE02] Agree checkbox not found ({debug_info}), continuing...")
    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Agree checkbox error: {exc}")

    await asyncio.sleep(0.5)

    # Step 3: Click "同意" button in popup dialog (appears after checkbox click)
    popup_agree_js = '''
    (function() {
        // Look for popup dialog with "同意" button
        // Button class: bui-btn bui-btn-contained bui-btn-large bui-btn-primary mz-button
        const buttons = document.querySelectorAll('button.bui-btn-large.bui-btn-primary, button.mz-button');
        for (const btn of buttons) {
            const text = btn.textContent || btn.innerText || '';
            // Match "同意" but not "同意並關閉" (cookie banner)
            if (text.trim() === '同意' || text.includes('我同意') || text.includes('確認同意')) {
                if (!btn.disabled && btn.offsetParent !== null) {
                    btn.click();
                    return {success: true, text: text.trim()};
                }
            }
        }
        // No popup found - might not have appeared yet or already dismissed
        return {success: false, error: 'no_popup_agree_button'};
    })()
    '''
    try:
        result = await tab.evaluate(popup_agree_js)
        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None
        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Popup agree button clicked: {result.get('text')}")
            await asyncio.sleep(0.5)  # Wait for popup to close
        else:
            # No popup is normal - it only appears after checkbox click
            pass
    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Popup agree button error: {exc}")

    await asyncio.sleep(0.3)

    # Step 4: Click submit button (分配座位)
    submit_js = '''
    (function() {
        // Pattern 1: Look for button inside confirmBtn container (most reliable)
        const confirmBtnContainer = document.querySelector('[class*="confirmBtn"]');
        if (confirmBtnContainer) {
            const btn = confirmBtnContainer.querySelector('button');
            if (btn && !btn.disabled) {
                btn.click();
                return {success: true, text: btn.textContent.trim(), action: 'confirmBtn_container'};
            }
        }

        // Pattern 2: Look for the submit button with specific text
        const buttons = document.querySelectorAll('button.mz-button, button.bui-btn-primary, button[type="button"]');
        for (const btn of buttons) {
            const text = btn.textContent || btn.innerText || '';
            // Look for submit keywords
            if (text.includes('分配座位') || text.includes('確認訂單') || text.includes('提交訂單') || text.includes('確認購買')) {
                if (!btn.disabled) {
                    btn.click();
                    return {success: true, text: text.trim()};
                }
                return {success: false, error: 'button_disabled', text: text.trim()};
            }
        }

        // Pattern 3: Look for primary button in bottom bar area (avoid header buttons)
        const bottomBar = document.querySelector('[class*="BottomBar"], [class*="SubmitInfoBar"]');
        if (bottomBar) {
            const btn = bottomBar.querySelector('button.bui-btn-primary:not(:disabled), button.mz-button:not(:disabled)');
            if (btn) {
                btn.click();
                return {success: true, text: btn.textContent.trim(), action: 'bottom_bar_button'};
            }
        }

        // Fallback: look for primary button but exclude known non-submit buttons
        const allButtons = document.querySelectorAll('button.bui-btn-primary:not(:disabled), button.mz-button:not(:disabled)');
        for (const btn of allButtons) {
            const text = btn.textContent || '';
            // Skip buttons that are clearly not submit buttons
            if (text.includes('搜索') || text.includes('搜尋') || text.includes('關閉') || text.includes('取消')) {
                continue;
            }
            btn.click();
            return {success: true, text: text.trim(), action: 'fallback_filtered'};
        }
        return {success: false, error: 'no_submit_button_found'};
    })()
    '''
    try:
        result = await tab.evaluate(submit_js)
        # Handle case where evaluate returns a list instead of dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0] if isinstance(result[0], dict) else None
        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[HKTICKETING TYPE02] Submit button clicked: {result.get('text')}")

            # Wait and check if redirected to checkout page
            await asyncio.sleep(1.5)
            try:
                current_url = await tab.evaluate('window.location.href')
                if '#/generateSeat' in str(current_url):
                    print("[HKTICKETING TYPE02] Successfully entered checkout page!")
                    return True
                elif '#/confirmOrder' in str(current_url):
                    # Still on confirm page, might need to retry
                    debug.log("[HKTICKETING TYPE02] Still on confirm page, will retry...")
            except Exception:
                pass

            return True
        else:
            error = result.get('error', 'unknown') if result and isinstance(result, dict) else 'no_result'
            debug.log(f"[HKTICKETING TYPE02] Submit button failed: {error}")
    except Exception as exc:
        debug.log(f"[HKTICKETING TYPE02] Submit button error: {exc}")

    return False

async def nodriver_hkticketing_performance(tab, config_dict, domain_name):
    """
    Ticket selection page integration flow
    Reference: chrome_tixcraft.py hkticketing_performance (line 8099-8172)
    """
    debug = util.create_debug_logger(config_dict)

    # Hide unnecessary blocks
    await nodriver_hkticketing_hide_tickets_blocks(tab)

    # Get area keyword (pass full string, function will handle multiple keywords)
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    is_price_assign_by_bot = False
    is_need_refresh = False

    # Pass full keyword string - function will try all keywords when areas are found
    is_need_refresh, is_price_assign_by_bot = await nodriver_hkticketing_area_auto_select(tab, config_dict, area_keyword)

    if is_price_assign_by_bot:
        # Set ticket number
        await nodriver_hkticketing_ticket_number_auto_select(tab, config_dict)
        await asyncio.sleep(0.1)

        # Select delivery option (not for Galaxy Macau)
        if 'galaxymacau.com' not in domain_name:
            await nodriver_hkticketing_ticket_delivery_option(tab, config_dict)
            await asyncio.sleep(0.1)

        # Click next button
        await nodriver_hkticketing_next_button_press(tab, config_dict)

    return is_price_assign_by_bot

async def nodriver_hkticketing_escape_robot_detection(tab, url):
    """
    Check for robot detection iframe
    Reference: chrome_tixcraft.py hkticketing_escape_robot_detection (line 8173-8200)
    """
    robot_detection = False

    try:
        el_iframe = await tab.query_selector('#main-iframe')
        if el_iframe:
            robot_detection = True
            print("[HKTICKETING] Robot detection iframe detected!")
    except Exception as exc:
        pass

    return robot_detection

async def nodriver_hkticketing_url_redirect(tab, url, config_dict):
    """
    Handle URL redirect for queue and error pages
    Reference: chrome_tixcraft.py hkticketing_url_redirect (line 8201-8262)
    """
    debug = util.create_debug_logger(config_dict)
    is_redirected = False

    redirect_to_home_list = ['galaxymacau.com', 'ticketek.com']

    for redirect_url in HKTICKETING_REDIRECT_URL_LIST:
        if redirect_url in url:
            # Default entry URL for hkticketing
            entry_url = 'https://entry-hotshow.hkticketing.com/'

            # For macau / ticketek
            for target_site in redirect_to_home_list:
                if target_site in url:
                    domain_name = url.split('/')[2]
                    entry_url = "https://%s/default.aspx" % (domain_name)
                    break

            try:
                await tab.get(entry_url)
                is_redirected = True
                debug.log(f"[HKTICKETING REDIRECT] Redirected to: {entry_url}")
            except Exception as exc:
                pass

            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])

            if is_redirected:
                break

    # Handle Access denied (403) on entry page
    if url == 'https://entry-hotshow.hkticketing.com/':
        content_redirect_string_list = ['Access denied (403)', 'Current session has been terminated']
        is_need_refresh = False

        try:
            html_body = await tab.get_content()
            if html_body:
                for each_redirect_string in content_redirect_string_list:
                    if each_redirect_string in html_body:
                        is_need_refresh = True
                        break
        except Exception as exc:
            pass

        if is_need_refresh:
            entry_url = "https://hotshow.hkticketing.com/"
            try:
                await tab.get(entry_url)
                is_redirected = True
                debug.log(f"[HKTICKETING REDIRECT] Access denied, redirected to: {entry_url}")
            except Exception as exc:
                pass

    return is_redirected

async def nodriver_hkticketing_content_refresh(tab, url, config_dict):
    """
    Handle content error and refresh page
    Reference: chrome_tixcraft.py hkticketing_content_refresh (line 8264-8343)
    """
    debug = util.create_debug_logger(config_dict)
    is_redirected = False

    # Check if URL matches patterns that need content checking
    is_check_access_denied = False
    for current_url in HKTICKETING_CHECK_URL_LIST:
        if current_url in url:
            is_check_access_denied = True
            break

    for current_url in HKTICKETING_CHECK_FULL_URL_LIST:
        if current_url == url:
            is_check_access_denied = True
            break

    if is_check_access_denied:
        domain_name = url.split('/')[2]
        new_url = "https://%s/default.aspx" % (domain_name)

        is_need_refresh = False
        try:
            html_body = await tab.get_content()
            if html_body:
                for each_retry_string in HKTICKETING_CONTENT_RETRY_STRING_LIST:
                    if each_retry_string in html_body:
                        is_need_refresh = True
                        break
        except Exception as exc:
            pass

        if is_need_refresh:
            debug.log("[HKTICKETING CONTENT] Start to automatically refresh page.")
            try:
                await tab.get(new_url)
                is_redirected = True
                debug.log(f"[HKTICKETING CONTENT] Redirected to: {new_url}")
            except Exception as exc:
                pass

            if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    return is_redirected

async def nodriver_hkticketing_travel_iframe(tab, config_dict):
    """
    Traverse iframes for error detection
    Reference: chrome_tixcraft.py hkticketing_travel_iframe (line 8345-8400)
    """
    debug = util.create_debug_logger(config_dict)
    is_redirected = False

    try:
        iframe_count = await tab.evaluate('''
            document.querySelectorAll('iframe').length
        ''')

        for idx in range(iframe_count):
            try:
                # Try to get iframe content (same-origin only)
                iframe_content = await tab.evaluate(f'''
                    (function() {{
                        try {{
                            const iframe = document.querySelectorAll('iframe')[{idx}];
                            if (iframe && iframe.contentDocument) {{
                                return iframe.contentDocument.body.innerHTML;
                            }}
                        }} catch(e) {{
                            // Cross-origin iframe cannot be accessed
                        }}
                        return null;
                    }})();
                ''')

                if iframe_content:
                    for error_string in HKTICKETING_CONTENT_RETRY_STRING_LIST:
                        if error_string in iframe_content:
                            # Trigger redirect
                            url = await tab.evaluate('window.location.href')
                            domain_name = url.split('/')[2]
                            new_url = "https://%s/default.aspx" % (domain_name)
                            await tab.get(new_url)
                            is_redirected = True
                            debug.log(f"[HKTICKETING IFRAME] Error detected in iframe, redirected to: {new_url}")
                            break
            except Exception as exc:
                pass

            if is_redirected:
                break

    except Exception as exc:
        pass

    return is_redirected

async def nodriver_hkticketing_main(tab, url, config_dict):
    """
    HKTicketing platform main flow control function
    Reference: chrome_tixcraft.py hkticketing_main logic (line 8400-8461)
    """
    if not _state:
        _state.update({
            "is_date_submiting": False,
            "fail_list": [],
            "played_sound_ticket": False,
            "played_sound_order": False,
            "shown_checkout_message": False,
        })

    debug = util.create_debug_logger(config_dict)

    # Handle URL redirect (queue pages, error pages)
    is_redirected = await nodriver_hkticketing_url_redirect(tab, url, config_dict)
    if is_redirected:
        return tab

    # Handle content refresh (error pages)
    is_redirected = await nodriver_hkticketing_content_refresh(tab, url, config_dict)
    if is_redirected:
        return tab

    # Handle iframe errors
    is_redirected = await nodriver_hkticketing_travel_iframe(tab, config_dict)
    if is_redirected:
        return tab

    # Close cookie popup
    await nodriver_hkticketing_accept_cookie(tab)

    # ==========================================================================
    # Type 02: hkt.hkticketing.com SPA (Vue/React based)
    # URL patterns:
    #   - Login page: hkt.hkticketing.com/hant/#/login
    #   - Event page: hkt.hkticketing.com/hant/#/allEvents/detail/{activityId}
    #   - Ticket page: hkt.hkticketing.com/hant/#/allEvents/detail/selectTicket?activityId=xxx
    #   - Confirm page: hkt.hkticketing.com/hant/#/confirmOrder?eventIds=xxx
    #   - Checkout page: hkt.hkticketing.com/hant/#/generateSeat/{orderId} (success!)
    # ==========================================================================
    is_type02_site = 'hkt.hkticketing.com' in url

    # Check for traffic overload page and auto-refresh (applies to all Type02 pages)
    if is_type02_site:
        is_traffic_overload = await nodriver_hkticketing_type02_check_traffic_overload(tab, config_dict)
        if is_traffic_overload:
            # Traffic overload detected, refresh was clicked, wait and return
            await asyncio.sleep(1.0)
            return tab

    # Type 02 Login Page - set session via localStorage
    is_type02_login_page = False
    if is_type02_site and '#/login' in url:
        is_type02_login_page = True

    if is_type02_login_page:
        debug.log("[HKTICKETING] Type 02 Login page detected")

        # Semi-automatic login: auto-fill account/password, wait for user to complete captcha
        login_success = await nodriver_hkticketing_type02_login(tab, config_dict)
        if login_success:
            # Redirect to homepage after successful login
            await asyncio.sleep(0.5)
            homepage = config_dict.get("homepage", "").strip()
            if homepage and 'hkt.hkticketing.com' in homepage:
                await tab.get(homepage)
                debug.log(f"[HKTICKETING TYPE02] Redirecting to: {homepage}")
            else:
                await tab.get("https://hkt.hkticketing.com/hant/#/home")
                debug.log("[HKTICKETING TYPE02] Redirecting to home page")
        return tab

    is_type02_base = is_type02_site and '#/allEvents/detail' in url

    # Type 02 Ticket Selection Page (selectTicket with activityId)
    is_type02_ticket_page = False
    if is_type02_base and 'selectTicket' in url and 'activityId=' in url:
        is_type02_ticket_page = True

    # Type 02 Event Page (detail page without selectTicket)
    is_type02_event_page = False
    if is_type02_base and 'selectTicket' not in url:
        is_type02_event_page = True

    # Handle Type 02 Event Page (even.html) - click buy button to enter ticket selection
    if is_type02_event_page:
        debug.log("[HKTICKETING] Type 02 Event page detected")

        # Dismiss any modal dialogs and click buy button
        await nodriver_hkticketing_type02_event_page(tab, config_dict)
        return tab

    # Handle Type 02 Ticket Selection Page (datearea.html)
    if is_type02_ticket_page:
        debug.log("[HKTICKETING] Type 02 Ticket Selection page detected")

        is_modal_dialog_popup = await nodriver_check_modal_dialog_popup(tab)
        if is_modal_dialog_popup:
            debug.log("[HKTICKETING TYPE02] Modal dialog popup, skip...")
        else:
            # Play sound when entering ticket page
            if not _state.get("played_sound_ticket", False):
                if config_dict["advanced"]["play_sound"]["ticket"]:
                    play_sound_while_ordering(config_dict)
                _state["played_sound_ticket"] = True

            await nodriver_hkticketing_type02_performance(tab, config_dict)

        return tab

    # Type 02 Confirm Order Page (#/confirmOrder)
    is_type02_confirm_page = False
    if is_type02_site and '#/confirmOrder' in url:
        is_type02_confirm_page = True

    if is_type02_confirm_page:
        debug.log("[HKTICKETING] Type 02 Confirm Order page detected")

        # Handle confirm order: delivery method, agree checkbox, submit button
        await nodriver_hkticketing_type02_confirm_order(tab, config_dict)
        return tab

    # Type 02 Checkout/Payment Page (#/generateSeat) - SUCCESS!
    is_type02_checkout_page = False
    if is_type02_site and '#/generateSeat' in url:
        is_type02_checkout_page = True

    if is_type02_checkout_page:
        print("[HKTICKETING TYPE02] Checkout page detected - Ticket booking SUCCESS!")

        # Play success sound (order) once
        if not _state.get("played_sound_order", False):
            if config_dict["advanced"]["play_sound"]["order"]:
                play_sound_while_ordering(config_dict)
            send_discord_notification(config_dict, "order", "HKTicketing")
            send_telegram_notification(config_dict, "order", "HKTicketing")
        _state["played_sound_order"] = True

        # Show message once
        if not _state.get("shown_checkout_message", False):
            print("[HKTICKETING TYPE02] Please complete payment within the time limit.")
            _state["shown_checkout_message"] = True

        # Stay idle - do not interfere with payment process
        return tab

    # ==========================================================================
    # Type 01: Traditional HKTicketing (ASP.NET based)
    # URL patterns: shows/show.aspx?, /events/.../performances/...
    # ==========================================================================

    # Login page
    is_hkticketing_sign_in_page = False
    if 'hkticketing.com/Secure/ShowLogin.aspx' in url:
        is_hkticketing_sign_in_page = True
    if 'hkticketing.com/Membership/Login.aspx' in url:
        is_hkticketing_sign_in_page = True

    if is_hkticketing_sign_in_page:
        hkticketing_account = config_dict["accounts"]["hkticketing_account"].strip()
        hkticketing_password = config_dict["accounts"]["hkticketing_password"].strip()
        if len(hkticketing_account) > 4:
            login_success = await nodriver_hkticketing_login(tab, hkticketing_account, hkticketing_password, config_dict=config_dict)

            # Wait for login to complete and redirect to homepage
            if login_success:
                await asyncio.sleep(1.0)
                try:
                    current_url = await tab.evaluate('window.location.href')
                    homepage = config_dict.get("homepage", "").strip()

                    # If on default page after login, redirect to homepage
                    if homepage and 'hkticketing.com' in homepage:
                        # Skip if already on homepage or homepage is default page
                        is_same_page = (homepage in current_url) or (current_url in homepage)
                        is_homepage_default = 'default.aspx' in homepage or homepage.rstrip('/').endswith('hkticketing.com')

                        if not is_same_page and not is_homepage_default:
                            if 'default.aspx' in current_url or current_url.endswith('/'):
                                debug.log(f"[HKTICKETING LOGIN] Redirecting to event page: {homepage}")
                                await tab.get(homepage)
                                await asyncio.sleep(1.0)
                except Exception as redirect_error:
                    debug.log(f"[HKTICKETING LOGIN] Redirect error: {redirect_error}")

    # Date selection page (shows/show.aspx?)
    if 'shows/show.aspx?' in url:
        is_modal_dialog_popup = await nodriver_check_modal_dialog_popup(tab)
        if is_modal_dialog_popup:
            debug.log("[HKTICKETING] Modal dialog popup, skip...")
        else:
            is_event_page = False
            if len(url.split('/')) == 5:
                is_event_page = True

            if is_event_page:
                if config_dict["date_auto_select"]["enable"]:
                    if not _state["is_date_submiting"]:
                        _state["is_date_submiting"], _state["fail_list"] = await nodriver_hkticketing_date_auto_select(tab, config_dict, _state["fail_list"])
                    else:
                        # Double check buy button status
                        await nodriver_hkticketing_date_buy_button_press(tab, config_dict)
    else:
        _state["is_date_submiting"] = False
        _state["fail_list"] = []

    # Ticket selection page (/events/.../performances/.../tickets or /seatmap)
    if '/events/' in url and '/performances/' in url:
        robot_detection = await nodriver_hkticketing_escape_robot_detection(tab, url)

        is_modal_dialog_popup = await nodriver_check_modal_dialog_popup(tab)
        if is_modal_dialog_popup:
            debug.log("[HKTICKETING] Modal dialog popup, skip...")
        else:
            if '/tickets' in url:
                domain_name = url.split('/')[2]
                if config_dict["area_auto_select"]["enable"]:
                    # Play sound when entering ticket page
                    if not _state["played_sound_ticket"]:
                        if config_dict["advanced"]["play_sound"]["ticket"]:
                            play_sound_while_ordering(config_dict)
                        _state["played_sound_ticket"] = True

                    await nodriver_hkticketing_performance(tab, config_dict, domain_name)

            if '/seatmap' in url:
                # Go to payment (no scroll needed - CDP can click directly)
                await nodriver_hkticketing_go_to_payment(tab, config_dict)
    else:
        _state["played_sound_ticket"] = False

    return tab

