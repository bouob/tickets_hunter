#!/usr/bin/env python3
#encoding=utf-8
"""platforms/famiticket.py -- FamiTicket platform (famiticket.com.tw)."""

import asyncio
import json
import random

import util
from nodriver_common import (
    CONST_FROM_TOP_TO_BOTTOM,
)


__all__ = [
    "nodriver_fami_login",
    "nodriver_fami_activity",
    "nodriver_fami_verify",
    "nodriver_fami_date_auto_select",
    "nodriver_fami_area_auto_select",
    "nodriver_fami_date_to_area",
    "nodriver_fami_ticket_select",
    "nodriver_fami_home_auto_select",
    "nodriver_famiticket_main",
]

_state = {}


async def nodriver_fami_login(tab, config_dict):
    """
    FamiTicket login

    Reference: chrome_tixcraft.py line 6308 (fami_login)
    """
    debug = util.create_debug_logger(config_dict)

    fami_account = config_dict["accounts"]["fami_account"].strip()
    fami_password = config_dict["accounts"]["fami_password"].strip()

    if len(fami_account) < 4:
        debug.log("[FAMI LOGIN] Account is empty or too short")
        return False

    if len(fami_password) == 0:
        debug.log("[FAMI LOGIN] Password is empty")
        return False

    debug.log(f"[FAMI LOGIN] Attempting login with account: {fami_account[:3]}***")

    is_login_success = False

    try:
        await asyncio.sleep(random.uniform(0.8, 1.2))

        original_url = tab.url if hasattr(tab, 'url') else str(tab.target.url)

        inputed_text = await tab.evaluate('document.querySelector("#usr_act").value')
        if not inputed_text or len(inputed_text) == 0:
            account_elem = await tab.query_selector('#usr_act')
            if account_elem:
                await account_elem.click()
                await asyncio.sleep(random.uniform(0.1, 0.2))
                await account_elem.send_keys(fami_account)
                debug.log("[FAMI LOGIN] Account filled")
                await asyncio.sleep(random.uniform(0.3, 0.5))
        elif inputed_text == fami_account:
            debug.log("[FAMI LOGIN] Account already correct")
        else:
            debug.log(f"[FAMI LOGIN] Account has different value: {inputed_text[:10]}...")

        inputed_pwd = await tab.evaluate('document.querySelector("#usr_pwd").value')
        if not inputed_pwd or len(inputed_pwd) == 0:
            password_elem = await tab.query_selector('#usr_pwd')
            if password_elem:
                await password_elem.click()
                await asyncio.sleep(random.uniform(0.1, 0.2))
                await password_elem.send_keys(fami_password)
                debug.log(f"[FAMI LOGIN] Password filled (length: {len(fami_password)})")
                await asyncio.sleep(random.uniform(0.3, 0.5))

                actual_pwd = await tab.evaluate('document.querySelector("#usr_pwd").value')
                debug.log(f"[FAMI LOGIN] Actual password length in field: {len(actual_pwd) if actual_pwd else 0}")
        else:
            debug.log("[FAMI LOGIN] Password already filled")

        login_btn = await tab.query_selector('button#btnLogin')
        if login_btn:
            await login_btn.click()
            debug.log("[FAMI LOGIN] Login button clicked, waiting for URL change...")

            for _ in range(20):
                await asyncio.sleep(0.5)
                current_url = tab.url if hasattr(tab, 'url') else str(tab.target.url)
                if current_url != original_url:
                    is_login_success = True
                    debug.log(f"[FAMI LOGIN] URL changed to: {current_url[:50]}...")
                    break
            else:
                debug.log("[FAMI LOGIN] URL did not change after 10 seconds")

    except Exception as exc:
        debug.log(f"[FAMI LOGIN] Error: {str(exc)}")

    return is_login_success

async def nodriver_fami_activity(tab, config_dict):
    """
    FamiTicket activity page - click buy button

    Reference: chrome_tixcraft.py line 3342 (fami_activity)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[FAMI ACTIVITY] Looking for buy button (#buyWaiting)")

    is_button_clicked = False

    try:
        click_result = await tab.evaluate('''
            (function() {
                var btn = document.querySelector('#buyWaiting');
                if (btn && !btn.disabled) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        ''')

        if click_result:
            is_button_clicked = True
            debug.log("[FAMI ACTIVITY] Buy button clicked via JS")
            for _ in range(10):
                await asyncio.sleep(0.5)
                current_url = tab.url if hasattr(tab, 'url') else str(tab.target.url)
                if '/Sales/' in current_url:
                    debug.log("[FAMI ACTIVITY] Redirected to Sales page")
                    break
        else:
            debug.log("[FAMI ACTIVITY] Buy button not found or disabled")

    except Exception as exc:
        debug.log(f"[FAMI ACTIVITY] Error: {str(exc)}")

    return is_button_clicked

async def nodriver_fami_verify(tab, config_dict, fail_list=None):
    """
    FamiTicket verification question handling
    """
    if fail_list is None:
        fail_list = []

    debug = util.create_debug_logger(config_dict)

    is_verify_success = False

    try:
        has_verify_input = await tab.evaluate('''
            (function() {
                return document.querySelector('#verifyPrefAnswer') !== null;
            })()
        ''')

        if has_verify_input:
            debug.log("[FAMI VERIFY] Verification input found (#verifyPrefAnswer)")

            answer_string = config_dict["area_auto_select"].get("area_answer", "").strip()
            auto_guess_enable = config_dict["advanced"].get("auto_guess_options", False)

            answer_list = []
            if answer_string:
                answer_list = [ans.strip() for ans in answer_string.split(',') if ans.strip()]

            if auto_guess_enable and len(answer_list) == 0:
                debug.log("[FAMI VERIFY] Auto guess enabled but no implementation yet")

            inferred_answer = ""
            for answer in answer_list:
                if answer not in fail_list:
                    inferred_answer = answer
                    break

            if inferred_answer:
                debug.log(f"[FAMI VERIFY] Trying answer: {inferred_answer}")

                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector('#verifyPrefAnswer');
                        if (input) {{
                            input.value = "{inferred_answer}";
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            var event = new KeyboardEvent('keypress', {{ key: 'Enter', keyCode: 13 }});
                            input.dispatchEvent(event);
                            var form = input.closest('form');
                            if (form) form.submit();
                        }}
                    }})()
                ''')

                await asyncio.sleep(0.5)

                still_on_verify = await tab.evaluate('''
                    (function() {
                        return document.querySelector('#verifyPrefAnswer') !== null;
                    })()
                ''')
                if still_on_verify:
                    fail_list.append(inferred_answer)
                    debug.log(f"[FAMI VERIFY] Answer failed, added to fail_list: {fail_list}")
                else:
                    is_verify_success = True
                    debug.log("[FAMI VERIFY] Verification successful")
            else:
                debug.log("[FAMI VERIFY] No valid answer available")
        else:
            is_verify_success = True

    except Exception as exc:
        debug.log(f"[FAMI VERIFY] Error: {str(exc)}")

    return is_verify_success, fail_list

async def nodriver_fami_date_auto_select(tab, config_dict, last_activity_url):
    """
    FamiTicket date auto selection

    Reference: chrome_tixcraft.py line 3386 (fami_date_auto_select)
    """
    debug = util.create_debug_logger(config_dict)

    auto_select_mode = config_dict["date_auto_select"].get("mode", CONST_FROM_TOP_TO_BOTTOM)
    date_keyword = config_dict["date_auto_select"].get("date_keyword", "").strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"].get("auto_reload_coming_soon_page", False)
    auto_reload_page_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)

    debug.log(f"[FAMI DATE] date_keyword: {date_keyword}")
    debug.log(f"[FAMI DATE] auto_select_mode: {auto_select_mode}")
    debug.log(f"[FAMI DATE] date_auto_fallback: {date_auto_fallback}")

    is_date_selected = False
    matched_rows = []

    try:
        formated_area_list_result = await tab.evaluate('''
            (function() {
                var rows = document.querySelectorAll('.session__list > tbody > tr');
                var result = [];
                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i];
                    var html = row.innerHTML || "";
                    var text = row.innerText || "";
                    if (html.indexOf('<button') !== -1 && html.indexOf('\u7acb\u5373\u8cfc\u8cb7') !== -1) {
                        result.push({
                            idx: i,
                            txt: text
                        });
                    }
                }
                return JSON.stringify(result);
            })()
        ''')

        formated_area_list = []
        if formated_area_list_result:
            if isinstance(formated_area_list_result, str):
                formated_area_list = json.loads(formated_area_list_result)
            elif isinstance(formated_area_list_result, list):
                formated_area_list = formated_area_list_result

        debug.log(f"[FAMI DATE] Found {len(formated_area_list)} date rows with buy button")

        if len(formated_area_list) > 0:
            if len(date_keyword) == 0:
                matched_rows = formated_area_list
            else:
                keywords = util.parse_keyword_string_to_array(date_keyword)
                if not keywords:
                    keywords = [kw.strip() for kw in date_keyword.split(',') if kw.strip()]
                for item in formated_area_list:
                    item_text = item.get('txt', item.get('text', ''))
                    row_text = util.format_keyword_string(item_text)
                    for keyword in keywords:
                        formatted_keyword = util.format_keyword_string(keyword)
                        if formatted_keyword in row_text:
                            matched_rows.append(item)
                            debug.log(f"[FAMI DATE KEYWORD] Matched keyword '{keyword}' in: {item_text[:50]}...")
                            break

                debug.log(f"[FAMI DATE] Matched dates: {len(matched_rows)}")

        if len(matched_rows) == 0 and len(formated_area_list) > 0:
            if date_auto_fallback:
                debug.log("[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
                matched_rows = formated_area_list
            else:
                debug.log("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
                return False

        target_item = util.get_target_item_from_matched_list(matched_rows, auto_select_mode)

        if target_item:
            try:
                target_index = target_item.get('idx', target_item.get('index', 0))
                target_text = target_item.get('txt', target_item.get('text', ''))
                click_result = await tab.evaluate(f'''
                    (function() {{
                        var rows = document.querySelectorAll('.session__list > tbody > tr');
                        if (rows[{target_index}]) {{
                            var btn = rows[{target_index}].querySelector('button');
                            if (btn) {{
                                btn.click();
                                return true;
                            }}
                        }}
                        return false;
                    }})()
                ''')

                if click_result:
                    is_date_selected = True
                    debug.log(f"[FAMI DATE SELECT] Selected date: {target_text[:50]}...")
                else:
                    debug.log("[FAMI DATE] Button not found in target row")
            except Exception as click_exc:
                debug.log(f"[FAMI DATE] Click error: {str(click_exc)}")

        if len(formated_area_list) == 0:
            await asyncio.sleep(0.5)

            page_type = await tab.evaluate('''
                (function() {
                    if (document.querySelector('.ticket__title')) return 'ticket';
                    if (document.querySelector('.purchase-detail')) return 'cart';
                    return 'date';
                })()
            ''')

            if page_type == 'ticket':
                debug.log("[FAMI DATE] No date rows, but found ticket selection page - delegating")
                return await nodriver_fami_ticket_select(tab, config_dict)

            if page_type == 'cart':
                debug.log("[FAMI DATE] No date rows, but found cart page - clicking next")
                next_result = await tab.evaluate('''
                    (function() {
                        var btn = document.querySelector('.purchase-detail__next');
                        if (btn && !btn.disabled) {
                            btn.click();
                            return true;
                        }
                        return false;
                    })()
                ''')
                return next_result

            if auto_reload_coming_soon_page_enable:
                debug.log("[FAMI DATE] Date list is empty, triggering auto-reload")

                if auto_reload_page_interval > 0:
                    await asyncio.sleep(auto_reload_page_interval)

                if last_activity_url:
                    await tab.get(last_activity_url)
                    await asyncio.sleep(0.3)

    except Exception as exc:
        debug.log(f"[FAMI DATE] Error: {str(exc)}")

    return is_date_selected

async def nodriver_fami_area_auto_select(tab, config_dict, area_keyword_item):
    """
    FamiTicket area auto selection

    Reference: chrome_tixcraft.py line 3520 (fami_area_auto_select)
    """
    debug = util.create_debug_logger(config_dict)

    auto_select_mode = config_dict["area_auto_select"].get("mode", CONST_FROM_TOP_TO_BOTTOM)
    area_auto_fallback = config_dict.get('area_auto_fallback', False)

    debug.log(f"[FAMI AREA] area_keyword_item: {area_keyword_item}")
    debug.log(f"[FAMI AREA] auto_select_mode: {auto_select_mode}")
    debug.log(f"[FAMI AREA] area_auto_fallback: {area_auto_fallback}")

    is_area_selected = False
    is_need_refresh = False
    matched_areas = []

    wait_time = random.uniform(0.4, 0.8)
    await tab.sleep(wait_time)

    try:
        formated_area_list_result = await tab.evaluate('''
            (function() {
                var areas = document.querySelectorAll('div > a.area');
                var result = [];
                for (var i = 0; i < areas.length; i++) {
                    var area = areas[i];
                    var html = area.outerHTML || "";
                    var text = area.innerText || "";
                    if (text.indexOf('\u552e\u5b8c') !== -1) continue;
                    if (html.indexOf('"area disabled"') !== -1) continue;
                    if (area.classList.contains('disabled')) continue;
                    if (text.length > 0) {
                        result.push({
                            idx: i,
                            txt: text
                        });
                    }
                }
                return JSON.stringify(result);
            })()
        ''')

        formated_area_list = []
        if formated_area_list_result:
            if isinstance(formated_area_list_result, str):
                formated_area_list = json.loads(formated_area_list_result)
            elif isinstance(formated_area_list_result, list):
                formated_area_list = formated_area_list_result

        debug.log(f"[FAMI AREA] Found {len(formated_area_list)} available areas")

        if len(formated_area_list) > 0:
            if len(area_keyword_item) == 0:
                matched_areas = formated_area_list
            else:
                keywords = [kw.strip() for kw in area_keyword_item.split(' ') if kw.strip()]

                for item in formated_area_list:
                    item_text = item.get('txt', item.get('text', ''))
                    row_text = util.format_keyword_string(item_text)
                    is_match = True

                    for keyword in keywords:
                        formatted_keyword = util.format_keyword_string(keyword)
                        if formatted_keyword not in row_text:
                            is_match = False
                            break

                    if is_match:
                        matched_areas.append(item)
                        debug.log(f"[FAMI AREA KEYWORD] AND logic matched: {keywords} in: {item_text[:50]}...")

                        if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                            break

                debug.log(f"[FAMI AREA] Matched areas: {len(matched_areas)}")

        if len(matched_areas) == 0 and len(formated_area_list) > 0:
            if area_auto_fallback:
                debug.log("[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
                matched_areas = formated_area_list
            else:
                debug.log("[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
                return True, False

        target_item = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)

        if target_item:
            try:
                target_index = target_item.get('idx', target_item.get('index', 0))
                target_text = target_item.get('txt', target_item.get('text', ''))
                click_result = await tab.evaluate(f'''
                    (function() {{
                        var areas = document.querySelectorAll('div > a.area');
                        if (areas[{target_index}]) {{
                            areas[{target_index}].click();
                            return true;
                        }}
                        return false;
                    }})()
                ''')

                if click_result:
                    is_area_selected = True
                    debug.log(f"[FAMI AREA SELECT] Selected area: {target_text[:50]}...")
                else:
                    debug.log("[FAMI AREA] Area element not found")
            except Exception as click_exc:
                debug.log(f"[FAMI AREA] Click error: {str(click_exc)}")

        if len(matched_areas) == 0:
            is_need_refresh = True
            debug.log("[FAMI AREA] No matched areas, need refresh")

    except Exception as exc:
        debug.log(f"[FAMI AREA] Error: {str(exc)}")

    return is_need_refresh, is_area_selected

async def nodriver_fami_date_to_area(tab, config_dict, last_activity_url):
    """
    FamiTicket date/area selection coordinator

    Reference: chrome_tixcraft.py line 3665 (fami_date_to_area)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[FAMI DATE TO AREA] Starting date to area flow")

    area_keyword = config_dict["area_auto_select"].get("area_keyword", "").strip()
    area_keyword_and = config_dict["area_auto_select"].get("area_keyword_and", [])

    area_keyword = util.format_keyword_for_display(area_keyword)

    keyword_groups = []

    if isinstance(area_keyword_and, list) and len(area_keyword_and) > 0:
        for group in area_keyword_and:
            if isinstance(group, list) and len(group) > 0:
                keyword_groups.append(' '.join(group))

    if len(keyword_groups) == 0 and len(area_keyword) > 0:
        delimiter = util.CONST_KEYWORD_DELIMITER if util.CONST_KEYWORD_DELIMITER in area_keyword else ','
        for kw in area_keyword.split(delimiter):
            if kw.strip():
                keyword_groups.append(kw.strip())

    if len(keyword_groups) == 0:
        keyword_groups.append("")

    debug.log(f"[FAMI DATE TO AREA] ========================================")
    debug.log(f"[FAMI DATE TO AREA] Raw area_keyword: '{area_keyword}'")
    debug.log(f"[FAMI DATE TO AREA] Raw area_keyword_and: {area_keyword_and}")
    debug.log(f"[FAMI DATE TO AREA] Parsed keyword_groups: {keyword_groups}")
    debug.log(f"[FAMI DATE TO AREA] Total groups to try: {len(keyword_groups)}")
    debug.log(f"[FAMI DATE TO AREA] ========================================")

    is_area_selected = False

    for keyword_item in keyword_groups:
        debug.log(f"[FAMI DATE TO AREA] Trying keyword group: '{keyword_item}'")

        is_need_refresh, is_area_selected = await nodriver_fami_area_auto_select(
            tab, config_dict, keyword_item
        )

        if is_area_selected:
            break

    return is_area_selected

async def nodriver_fami_ticket_select(tab, config_dict):
    """
    FamiTicket ticket selection page handling
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[FAMI TICKET] Processing ticket selection page")

    result = False

    try:
        title_text = await tab.evaluate('document.querySelector(".ticket__title")?.innerText || ""')
        if not title_text:
            debug.log("[FAMI TICKET] Not a ticket selection page (no .ticket__title)")
            return False
        debug.log(f"[FAMI TICKET] Found ticket: {title_text}")

        ticket_number = config_dict.get("ticket_number", 2)
        debug.log(f"[FAMI TICKET] Selecting ticket number: {ticket_number}")

        select_result = await tab.evaluate(f'''
            (function() {{
                var select = document.querySelector('.ticket select, .ticket-selector select');
                if (select) {{
                    var targetValue = "{ticket_number}";
                    for (var i = 0; i < select.options.length; i++) {{
                        if (select.options[i].value == targetValue) {{
                            select.selectedIndex = i;
                            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                    for (var i = select.options.length - 1; i >= 0; i--) {{
                        if (select.options[i].value && select.options[i].value !== "") {{
                            select.selectedIndex = i;
                            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                }}
                return false;
            }})()
        ''')

        if select_result:
            debug.log("[FAMI TICKET] Ticket number selected")

        await asyncio.sleep(0.3)

        checkbox_result = await tab.evaluate('''
            (function() {
                var checkboxes = document.querySelectorAll('.ts-note__check');
                var checked = 0;
                checkboxes.forEach(function(cb) {
                    if (!cb.checked) {
                        cb.click();
                        checked++;
                    }
                });
                return checked;
            })()
        ''')

        debug.log(f"[FAMI TICKET] Checked {checkbox_result} checkboxes")

        await asyncio.sleep(0.3)

        submit_result = await tab.evaluate('''
            (function() {
                var btn = document.querySelector('.ts-opts__auto');
                if (btn && !btn.classList.contains('disabled')) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        ''')

        if submit_result:
            debug.log("[FAMI TICKET] Submit button clicked")
            result = True

            for _ in range(10):
                await asyncio.sleep(0.5)
                current_url = tab.url if hasattr(tab, 'url') else str(tab.target.url)
                if '/Order/' in current_url or '/Checkout/' in current_url:
                    debug.log("[FAMI TICKET] Redirected to order page")
                    break
        else:
            debug.log("[FAMI TICKET] Submit button not available or disabled")

    except Exception as exc:
        debug.log(f"[FAMI TICKET] Error: {str(exc)}")

    return result

async def nodriver_fami_home_auto_select(tab, config_dict, last_activity_url):
    """
    FamiTicket home page entry handling (URL routing)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[FAMI HOME] Processing home/sales page")

    page_type = await tab.evaluate('''
        (function() {
            if (document.querySelector('.purchase-detail')) return 'cart';
            if (document.querySelector('.ticket__title')) return 'ticket';
            if (document.querySelector('.area-list') ||
                document.querySelector('.area-selector__title')) return 'area';
            return 'date';
        })()
    ''')

    if debug.enabled:
        debug.log(f"[FAMI HOME DEBUG] Page type detected: '{page_type}'")
        debug_selectors = await tab.evaluate('''
            (function() {
                return {
                    cart: !!document.querySelector('.purchase-detail'),
                    ticket: !!document.querySelector('.ticket__title'),
                    area_list: !!document.querySelector('.area-list'),
                    area_selector: !!document.querySelector('.area-selector__title')
                };
            })()
        ''')
        debug.log(f"[FAMI HOME DEBUG] Selector check: {debug_selectors}")
        debug.log(f"[FAMI HOME DEBUG] area_auto_select.enable: {config_dict['area_auto_select'].get('enable', True)}")

    # 1. Cart page
    if page_type == 'cart':
        debug.log("[FAMI HOME] Detected cart/order page")
        next_result = await tab.evaluate('''
            (function() {
                var btn = document.querySelector('.purchase-detail__next');
                if (btn && !btn.disabled) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        ''')
        if next_result:
            debug.log("[FAMI HOME] Next button clicked on cart page")
            return True
        else:
            debug.log("[FAMI HOME] Next button not found or disabled")
            return False

    # 2. Ticket selection page
    if page_type == 'ticket':
        debug.log("[FAMI HOME] Detected ticket selection page")
        return await nodriver_fami_ticket_select(tab, config_dict)

    # 3. Area selection page
    if page_type == 'area':
        debug.log("[FAMI HOME] Detected area selection page")
        if config_dict["area_auto_select"].get("enable", True):
            is_area_selected = await nodriver_fami_date_to_area(tab, config_dict, last_activity_url)

            if not is_area_selected:
                auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 5)
                if auto_reload_interval > 0:
                    debug.log(f"[FAMI HOME] No area selected, waiting {auto_reload_interval}s before retry...")
                    await tab.sleep(auto_reload_interval)

            return is_area_selected
        return False

    # 4. Date selection page (default)
    if config_dict["date_auto_select"].get("enable", True):
        is_date_selected = await nodriver_fami_date_auto_select(
            tab, config_dict, last_activity_url
        )
        return is_date_selected

    return False

async def nodriver_famiticket_main(tab, url, config_dict):
    """
    FamiTicket main function - URL router
    """
    if not _state:
        _state.update({
            "fail_list": [],
            "last_activity": "",
            "payment_logged": False,
        })

    debug = util.create_debug_logger(config_dict)

    debug.log(f"[FAMITICKET MAIN] Processing URL: {url[:80]}...")

    result = False

    try:
        if '/Payment/' in url:
            if not _state.get("payment_logged", False):
                print("[FAMITICKET MAIN] Payment page detected - waiting for user to complete payment")
                _state["payment_logged"] = True
            return True

        if '/Home/User/SignIn' in url and '/SignInCheck' not in url:
            fami_account = config_dict["advanced"].get("fami_account", "")
            if len(fami_account) > 4:
                result = await nodriver_fami_login(tab, config_dict)

        elif '/Home/Activity/Info/' in url:
            _state["last_activity"] = url
            result = await nodriver_fami_activity(tab, config_dict)

            is_verify_success, _state["fail_list"] = await nodriver_fami_verify(
                tab, config_dict, _state["fail_list"]
            )

        elif '/Sales/Home/Index/' in url:
            if config_dict["date_auto_select"].get("enable", True):
                result = await nodriver_fami_home_auto_select(
                    tab, config_dict, _state["last_activity"]
                )

        elif url.endswith('/Home/') or url.endswith('/Home'):
            homepage = config_dict.get("homepage", "")
            if homepage and '/Home/Activity/Info/' in homepage:
                debug.log(f"[FAMITICKET MAIN] Redirecting to activity: {homepage[:60]}...")
                await tab.get(homepage)
                result = True
            else:
                debug.log("[FAMITICKET MAIN] On homepage, no redirect needed")

        else:
            debug.log(f"[FAMITICKET MAIN] Unknown URL pattern, clearing fail_list")
            _state["fail_list"] = []

    except Exception as exc:
        debug.log(f"[FAMITICKET MAIN] Error: {str(exc)}")

    return result
