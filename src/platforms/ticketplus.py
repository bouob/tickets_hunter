#!/usr/bin/env python3
#encoding=utf-8
"""platforms/ticketplus.py -- TicketPlus platform (ticketplus.com.tw)."""

import asyncio
import json
import random
import time
import traceback

from zendriver import cdp

import util
from nodriver_common import (
    check_and_handle_pause,
    evaluate_with_pause_check,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    sleep_with_pause_check,
)


__all__ = [
    "nodriver_ticketplus_detect_layout_style",
    "nodriver_ticketplus_account_sign_in",
    "nodriver_ticketplus_is_signin",
    "nodriver_ticketplus_account_auto_fill",
    "nodriver_ticketplus_date_auto_select",
    "nodriver_ticketplus_unified_select",
    "nodriver_ticketplus_click_next_button_unified",
    "nodriver_ticketplus_ticket_agree",
    "nodriver_ticketplus_accept_realname_card",
    "nodriver_ticketplus_accept_other_activity",
    "nodriver_ticketplus_accept_order_fail",
    "nodriver_ticketplus_check_queue_status",
    "nodriver_ticketplus_confirm",
    "nodriver_ticketplus_order",
    "nodriver_ticketplus_wait_for_vue_ready",
    "nodriver_ticketplus_check_next_button",
    "nodriver_ticketplus_order_exclusive_code",
    "nodriver_ticketplus_main",
]

_state = {}


def _get_status():
    """Return current ticketplus status for main loop (Approach B)."""
    return {
        "purchase_completed": _state.get("purchase_completed", False),
        "is_ticket_assigned": _state.get("is_ticket_assigned", False),
    }


async def nodriver_ticketplus_detect_layout_style(tab, config_dict=None):
    """Detect TicketPlus page layout style.

    Returns:
        dict: {
            'style': int,      # 0: unknown, 1: style_1 (expansion), 2: style_2 (simple), 3: style_3 (new Vue.js)
            'found': bool,     # whether next button found
            'button_enabled': bool  # whether button is enabled
        }
    """
    try:
        result = await evaluate_with_pause_check(tab, '''
            (function() {
                console.log("=== Layout Detection Started ===");

                // Check for row layout ticket structure (Page3 feature)
                const rowTickets = document.querySelectorAll('.row.py-1.py-md-4.rwd-margin.no-gutters.text-title');
                const expansionPanels = document.querySelectorAll('.v-expansion-panels .v-expansion-panel');

                console.log("Row ticket element count:", rowTickets.length);
                console.log("Expansion Panel element count:", expansionPanels.length);

                // If row tickets exist and no expansion panels, prioritize style 3 (Page3)
                if (rowTickets.length > 0 && expansionPanels.length === 0) {
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

                // style_3: new Vue.js layout (general check)
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

                // style_2: new layout (simple)
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

                // style_1: old layout (expansion) - only when expansion panels exist
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

                // Generic button search (fallback)
                const anyButton = document.querySelector("button.nextBtn");
                if (anyButton) {
                    console.log("Found generic nextBtn button, determining style based on content structure");
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

        if result is None:
            return {'style': 0, 'found': False, 'button_enabled': False, 'paused': True}

        result = util.parse_nodriver_result(result)

        return result if isinstance(result, dict) else {
            'style': 0, 'found': False, 'button_enabled': False
        }

    except Exception as exc:
        return {'style': 0, 'found': False, 'button_enabled': False, 'error': str(exc)}


async def nodriver_ticketplus_account_sign_in(tab, config_dict):
    debug = util.create_debug_logger(config_dict)
    debug.log("[TICKETPLUS SIGNIN] nodriver_ticketplus_account_sign_in")
    is_filled_form = False
    is_submited = False

    ticketplus_account = config_dict["accounts"]["ticketplus_account"]
    ticketplus_password = config_dict["accounts"]["ticketplus_password"].strip()

    # manually keyin verify code.
    country_code = ""
    try:
        my_css_selector = 'input[placeholder="\u5340\u78bc"]'
        el_country = await tab.query_selector(my_css_selector)
        if el_country:
            country_code = await el_country.apply('function (element) { return element.value; } ')
            debug.log(f"[TICKETPLUS SIGNIN] country_code: {country_code}")
    except Exception as exc:
        debug.log(f"[TICKETPLUS SIGNIN] country code error: {exc}")

    is_account_assigned = False
    try:
        my_css_selector = 'input[placeholder="\u624b\u6a5f\u865f\u78bc *"]'
        el_account = await tab.query_selector(my_css_selector)
        if el_account:
            await el_account.click()
            await el_account.apply('function (element) {element.value = ""; } ')
            await el_account.send_keys(ticketplus_account);
            is_account_assigned = True
    except Exception as exc:
        debug.log(f"[TICKETPLUS SIGNIN] account input error: {exc}")

    if is_account_assigned:
        try:
            my_css_selector = 'input[type="password"]'
            el_password = await tab.query_selector(my_css_selector)
            if el_password:
                debug.log("[TICKETPLUS SIGNIN] Entering password...")
                await el_password.click()
                await el_password.apply('function (element) {element.value = ""; } ')
                await el_password.send_keys(ticketplus_password);
                await asyncio.sleep(random.uniform(0.1, 0.3))
                is_filled_form = True

                if country_code=="+886":
                    # only this case to auto sumbmit.
                    debug.log("[TICKETPLUS SIGNIN] press enter")
                    await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                    await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                    await asyncio.sleep(random.uniform(0.8, 1.2))
                    # PS: ticketplus country field may not located at your target country.
                    is_submited = True
        except Exception as exc:
            debug.log(f"[TICKETPLUS SIGNIN] password input error: {exc}")
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
        pass

    return is_user_signin


async def nodriver_ticketplus_account_auto_fill(tab, config_dict):
    # auto fill account info.
    debug = util.create_debug_logger(config_dict)
    is_user_signin = False
    if len(config_dict["accounts"]["ticketplus_account"]) > 0:
        is_user_signin = await nodriver_ticketplus_is_signin(tab)
        if not is_user_signin:
            await asyncio.sleep(0.1)
            if not _state.get("signin_form_filled", False):
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
                    debug.log(f"[TICKETPLUS AUTOFILL] sign-in button click error: {exc}")
                    pass

                if not is_sign_in_btn_pressed:
                    action_btns = None
                    try:
                        my_css_selector = 'div.px-4.py-3.drawerItem.cursor-pointer'
                        action_btns = await tab.query_selector_all(my_css_selector)
                    except Exception as exc:
                        debug.log(f"[TICKETPLUS AUTOFILL] drawer items query error: {exc}")
                        pass
                    if action_btns:
                        debug.log(f"[TICKETPLUS AUTOFILL] action buttons len: {len(action_btns)}")
                        if len(action_btns) >= 4:
                            try:
                                await action_btns[3].click()
                            except Exception as exc:
                                debug.log(f"[TICKETPLUS AUTOFILL] action button click error: {exc}")
                                pass

                is_filled_form, is_submited = await nodriver_ticketplus_account_sign_in(tab, config_dict)
                if is_filled_form:
                    _state["signin_form_filled"] = True

    return is_user_signin


async def _ticketplus_click_refresh_button(tab, debug):
    """Click float-btn refresh button for partial DOM update; return True if clicked."""
    try:
        btn = await tab.query_selector('button.float-btn')
        if btn:
            await btn.click()
            await asyncio.sleep(0.8)
            debug.log("[REFRESH] Clicked update button (partial refresh)")
            return True
    except Exception:
        pass
    return False


async def nodriver_ticketplus_date_auto_select(tab, config_dict):
    """TicketPlus date auto selection."""
    debug = util.create_debug_logger(config_dict)

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    debug.log("date_auto_select_mode:", auto_select_mode)
    debug.log("date_keyword:", date_keyword)

    area_list = None
    try:
        area_list = await tab.query_selector_all('div#buyTicket > div.sesstion-item > div.row')
        if area_list and len(area_list) == 0:
            debug.log("empty date item, need retry.")
            await tab.sleep(0.2)
    except Exception as exc:
        debug.log("find #buyTicket fail:", exc)

    find_ticket_text_list = ['>\u7acb\u5373\u8cfc', '\u5c1a\u672a\u958b\u8ce3']
    sold_out_text_list = ['\u92b7\u552e\u4e00\u7a7a']

    matched_blocks = None
    formated_area_list = None
    is_vue_ready = True

    if area_list and len(area_list) > 0:
        debug.log("date_list_count:", len(area_list))

        formated_area_list = []
        for row in area_list:
            row_text = ""
            row_html = ""
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                debug.log("Date item processing failed:", exc)
                break

            if len(row_text) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                if '<div class="v-progress-circular__info"></div>' in row_html:
                    is_vue_ready = False
                    break

            if len(row_text) > 0:
                row_is_enabled = False
                for text_item in find_ticket_text_list:
                    if text_item in row_html:
                        row_is_enabled = True
                        break

                if row_is_enabled and pass_date_is_sold_out_enable:
                    for sold_out_item in sold_out_text_list:
                        if sold_out_item in row_text:
                            row_is_enabled = False
                            debug.log(f"match sold out text: {sold_out_item}, skip this row.")
                            break

                if row_is_enabled:
                    formated_area_list.append(row)

        debug.log("formated_area_list count:", len(formated_area_list))

        if len(date_keyword) == 0:
            matched_blocks = formated_area_list
        else:
            matched_blocks = []
            try:
                original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
                keyword_array = json.loads("[" + original_keyword + "]")

                debug.log(f"[TicketPlus DATE] Applying keyword filter: {keyword_array}")

                for i, row in enumerate(formated_area_list):
                    row_text = ""
                    try:
                        row_html = await row.get_html()
                        row_text = util.remove_html_tags(row_html).lower()
                    except Exception as exc:
                        debug.log(f"[TicketPlus DATE] Failed to get row text: {exc}")
                        continue

                    for keyword_item in keyword_array:
                        sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                        is_match = all(sub_kw.lower() in row_text for sub_kw in sub_keywords)

                        if is_match:
                            matched_blocks.append(row)
                            debug.log(f"[TicketPlus DATE] Keyword '{keyword_item}' matched row {i}")
                            break

            except json.JSONDecodeError as exc:
                debug.log(f"[TicketPlus DATE] Keyword parse error: {exc}")
                debug.log(f"[TicketPlus DATE] Treating as 'all keywords failed'")
                matched_blocks = []
            except Exception as exc:
                debug.log(f"[TicketPlus DATE] Keyword matching failed: {exc}")
                matched_blocks = []

        if len(matched_blocks) == 0 and date_keyword and len(date_keyword) > 0:
            if date_auto_fallback:
                debug.log(f"[TicketPlus DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
                matched_blocks = formated_area_list
            else:
                debug.log(f"[TicketPlus DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
                debug.log(f"[TicketPlus DATE SELECT] No date selected, will check if reload needed")
    else:
        debug.log("date date-time-position is None or empty")

    is_date_clicked = False
    if is_vue_ready and formated_area_list and len(formated_area_list) > 0:
        try:
            original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

            # Primary: read sessionId from Vue data layer, navigate directly
            # Avoids clicking loading-state placeholder containers
            vue_data = await tab.evaluate('''
                (function() {
                    const el = document.querySelector('.eventClass');
                    if (!el || !el.__vue__) return { ready: false };
                    const sessions = el.__vue__.$data.sessions || [];
                    const loaded = sessions.filter(function(s) { return s.loadingStatusFinished; });
                    return {
                        ready: loaded.length > 0,
                        sessions: loaded.map(function(s) {
                            return { sessionId: s.sessionId, date: s.date || '', name: s.name || '' };
                        })
                    };
                })();
            ''')

            if isinstance(vue_data, dict) and vue_data.get('ready') and vue_data.get('sessions'):
                sessions = vue_data['sessions']
                target_session = None
                try:
                    kw_array = json.loads("[" + original_keyword + "]")
                except Exception:
                    kw_array = [original_keyword.strip('"').strip("'").strip()]

                for s in sessions:
                    session_text = (s.get('date', '') + ' ' + s.get('name', '')).lower()
                    for kw_item in kw_array:
                        sub_kws = [k.strip() for k in kw_item.split(' ') if k.strip()]
                        if all(k.lower() in session_text for k in sub_kws):
                            target_session = s
                            break
                    if target_session:
                        break

                if not target_session and date_auto_fallback and sessions:
                    debug.log("[TicketPlus DATE FALLBACK] Vue data fallback: using first loaded session")
                    target_session = sessions[0]

                if target_session:
                    session_id = target_session['sessionId']
                    # Known honeypot sessionId: TicketPlus API returns fake data to detected bots
                    KNOWN_FAKE_SESSION_IDS = ['c18900a1d5f295218fe60b982d7ece96']
                    if session_id in KNOWN_FAKE_SESSION_IDS:
                        debug.log(f"[TicketPlus DATE] WARNING: API returned known fake session data (anti-bot honeypot detected). sessionId={session_id}")
                        debug.log("[TicketPlus DATE] Bot may be flagged by TicketPlus. Skipping navigation to avoid invalid order page.")
                    else:
                        current_url = tab.url if hasattr(tab, 'url') else ''
                        if not current_url:
                            current_url = await tab.evaluate('window.location.href')
                        event_id = current_url.split('/activity/')[-1].split('/')[0].split('?')[0]
                        order_url = 'https://ticketplus.com.tw/order/' + event_id + '/' + session_id
                        debug.log(f"[TicketPlus DATE] Vue data: date={target_session.get('date', '')} sessionId={session_id}")
                        await tab.get(order_url)
                        is_date_clicked = True

        except Exception as exc:
            debug.log(f"[TicketPlus DATE] Vue data navigation failed: {exc}")

    if not is_date_clicked and is_vue_ready and formated_area_list and len(formated_area_list) > 0:
        try:
            original_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
            click_result = await tab.evaluate(f'''
                (function() {{
                    const originalKeyword = '{original_keyword}';
                    const autoSelectMode = '{auto_select_mode}';
                    const dateAutoFallback = {'true' if date_auto_fallback else 'false'};

                    console.log('[TicketPlus] Starting date selection - keyword:', originalKeyword, 'mode:', autoSelectMode, 'fallback:', dateAutoFallback);

                    let sessionContainers = Array.from(document.querySelectorAll('div#buyTicket > div.sesstion-item'))
                        .filter(c => c.querySelector('button.nextBtn'));

                    if (sessionContainers.length === 0) {{
                        sessionContainers = Array.from(document.querySelectorAll('div#buyTicket > div.row.pa-4'))
                            .filter(c => c.querySelector('button.nextBtn'));
                    }}

                    console.log('[TicketPlus] Found session containers:', sessionContainers.length);

                    let matchedContainers = [];

                    if (originalKeyword && originalKeyword.trim() !== '') {{
                        let keywords = [];
                        if (originalKeyword.includes(',')) {{
                            keywords = originalKeyword.split(',')
                                .map(k => k.trim().replace(/^["']|["']$/g, ''))
                                .filter(k => k.length > 0);
                        }} else {{
                            keywords = [originalKeyword.replace(/^["']|["']$/g, '').trim()];
                        }}

                        console.log('[TicketPlus] Parsed keywords:', keywords);

                        for (let i = 0; i < sessionContainers.length; i++) {{
                            const container = sessionContainers[i];
                            const text = container.textContent || '';
                            const normalizedText = text.replace(/[\\s\\u3000]/g, '').toLowerCase();

                            for (let keyword of keywords) {{
                                const normalizedKeyword = keyword.replace(/[\\s\\u3000]/g, '').toLowerCase();
                                if (normalizedText.includes(normalizedKeyword)) {{
                                    matchedContainers.push(container);
                                    console.log('[TicketPlus] Keyword "' + keyword + '" matched container ' + i);
                                    console.log('  -> Text preview:', text.substring(0, 100).replace(/\\n/g, ' '));
                                    break;
                                }}
                            }}
                        }}
                    }} else {{
                        matchedContainers = sessionContainers;
                        console.log('[TicketPlus] No keyword specified, using all', sessionContainers.length, 'containers');
                    }}

                    if (matchedContainers.length === 0 && originalKeyword && originalKeyword.trim() !== '') {{
                        if (dateAutoFallback) {{
                            console.log('[TicketPlus DATE FALLBACK] date_auto_fallback=true, triggering auto fallback');
                            matchedContainers = sessionContainers;
                        }} else {{
                            console.log('[TicketPlus DATE FALLBACK] date_auto_fallback=false, fallback is disabled');
                            console.log('[TicketPlus DATE SELECT] No date selected, will reload page and retry');
                            return {{
                                success: false,
                                error: 'No keyword matches and fallback is disabled',
                                strict_mode: true
                            }};
                        }}
                    }}

                    if (matchedContainers.length === 0) {{
                        console.log('[TicketPlus ERROR] No session containers found');
                        return {{
                            success: false,
                            error: 'No session containers found',
                            debug: {{
                                keyword: originalKeyword,
                                mode: autoSelectMode,
                                totalContainers: sessionContainers.length
                            }}
                        }};
                    }}

                    let targetIndex = 0;
                    if (autoSelectMode === 'from bottom to top') {{
                        targetIndex = matchedContainers.length - 1;
                    }} else if (autoSelectMode === 'center') {{
                        targetIndex = Math.floor(matchedContainers.length / 2);
                    }} else if (autoSelectMode === 'random') {{
                        targetIndex = Math.floor(Math.random() * matchedContainers.length);
                    }}

                    let targetContainer = matchedContainers[targetIndex];
                    const containerText = (targetContainer.textContent || '').substring(0, 150).replace(/\\n/g, ' ');
                    console.log('[TicketPlus TARGET] Selected container [' + targetIndex + '/' + matchedContainers.length + ']');
                    console.log('  -> Preview:', containerText);

                    let buyButton = targetContainer.querySelector('button.nextBtn');
                    if (!buyButton) {{
                        buyButton = targetContainer.querySelector('button');
                    }}

                    if (!buyButton) {{
                        console.log('[TicketPlus ERROR] No buy button found in container');
                        return {{
                            success: false,
                            error: 'No buy button found in container',
                            targetText: containerText
                        }};
                    }}

                    const buttonText = buyButton.textContent || '';
                    console.log('[TicketPlus BUTTON] Found button:', buttonText);

                    try {{
                        const event = new MouseEvent('click', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        buyButton.dispatchEvent(event);
                        console.log('[TicketPlus SUCCESS] Button clicked successfully');
                        return {{
                            success: true,
                            action: 'button_clicked',
                            matchedCount: matchedContainers.length,
                            targetText: containerText,
                            buttonText: buttonText
                        }};
                    }} catch (e) {{
                        console.log('[TicketPlus ERROR] Click failed:', e.message);
                        return {{
                            success: false,
                            error: 'Click failed: ' + e.message,
                            targetText: containerText
                        }};
                    }}
                }})();
            ''')

            parsed_result = util.parse_nodriver_result(click_result)

            if isinstance(parsed_result, dict) and parsed_result.get('success'):
                debug.log(f"Date selection and click successful: {parsed_result.get('action', 'unknown')}")
                debug.log(f"   Target text: {parsed_result.get('targetText', '')}")
                is_date_clicked = True
            else:
                debug.log(f"Date selection and click failed: {parsed_result.get('error', 'unknown') if isinstance(parsed_result, dict) else str(parsed_result)}")

        except Exception as exc:
            debug.log("JavaScript date selection click failed:", exc)

    if not is_date_clicked:
        if debug.enabled:
            if not is_vue_ready:
                debug.log("[TicketPlus DATE] Vue.js not ready, waiting for page to load...")
            elif not formated_area_list or len(formated_area_list) == 0:
                debug.log("[TicketPlus DATE] No available tickets (all sold out), waiting for refresh...")

        if auto_reload_coming_soon_page_enable and is_vue_ready and (not formated_area_list or len(formated_area_list) == 0):
            try:
                reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                if reload_interval > 0:
                    debug.log(f"[TicketPlus DATE] Waiting {reload_interval}s before auto-reload...")
                    await asyncio.sleep(reload_interval)
                else:
                    await asyncio.sleep(1.0)

                clicked = await _ticketplus_click_refresh_button(tab, debug)
                if not clicked:
                    await tab.reload()
                    debug.log("[TicketPlus DATE] Page reloaded, waiting for content...")
                    await asyncio.sleep(0.5)
            except Exception as exc:
                debug.log(f"[TicketPlus DATE] Auto reload failed: {exc}")

    return is_date_clicked


async def nodriver_ticketplus_unified_select(tab, config_dict, area_keyword):
    """TicketPlus unified selector - language-independent ticket type/area selection."""
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get('area_auto_fallback', False)
    ticket_number = config_dict["ticket_number"]
    keyword_exclude = config_dict.get("keyword_exclude", "")

    debug.log(f"Unified selector started - keyword: {area_keyword}, tickets: {ticket_number}")

    is_selected = False

    try:
        if await check_and_handle_pause(config_dict):
            return False

        if await sleep_with_pause_check(tab, 0.6, config_dict):
            debug.log("Pause check interrupted")
            return False

        exclude_keywords = []
        if keyword_exclude:
            try:
                exclude_keywords = json.loads("[" + keyword_exclude + "]")
            except:
                if util.CONST_KEYWORD_DELIMITER in keyword_exclude:
                    exclude_keywords = [kw.strip() for kw in keyword_exclude.split(util.CONST_KEYWORD_DELIMITER) if kw.strip()]
                else:
                    exclude_keywords = [keyword_exclude.strip()] if keyword_exclude.strip() else []

        # Wait for Vue.js elements to render
        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 5)
        max_vue_wait = max(6.0, min(15.0, auto_reload_interval * 2))
        vue_check_interval = 0.15
        vue_wait_start = time.time()
        vue_elements_found = False
        last_log_time = 0

        while time.time() - vue_wait_start < max_vue_wait:
            if await check_and_handle_pause(config_dict):
                return False

            try:
                vue_check = await tab.evaluate('''
                    (function() {
                        const panels = document.querySelectorAll('.v-expansion-panel').length;
                        const countBtn = document.querySelectorAll('.count-button .mdi-plus').length;
                        const rowTickets = document.querySelectorAll('.row.py-1.py-md-4').length;
                        return {
                            panels: panels,
                            countBtn: countBtn,
                            rowTickets: rowTickets,
                            hasElements: panels > 0 || countBtn > 0 || rowTickets > 0
                        };
                    })();
                ''')

                if isinstance(vue_check, list):
                    vue_check = {item[0]: item[1].get('value') if isinstance(item[1], dict) else item[1] for item in vue_check}

                elapsed = time.time() - vue_wait_start
                if elapsed - last_log_time >= 1.0:
                    debug.log(f"[VUE WAIT] {elapsed:.1f}s - panels:{vue_check.get('panels', 0)}, countBtn:{vue_check.get('countBtn', 0)}, rowTickets:{vue_check.get('rowTickets', 0)}")
                    last_log_time = elapsed

                if vue_check.get('hasElements', False):
                    vue_elements_found = True
                    debug.log(f"[VUE WAIT] Vue elements found after {elapsed:.1f}s")
                    await asyncio.sleep(0.1)
                    break

            except Exception as e:
                debug.log(f"[VUE WAIT] Check error: {e}")

            await asyncio.sleep(vue_check_interval)

        if not vue_elements_found:
            debug.log(f"[VUE WAIT] Timeout after {max_vue_wait:.1f}s, Vue elements not found")
            return False

        js_result = await tab.evaluate(f'''
            (function() {{
                const keyword = '{area_keyword}';
                const ticketNumber = {ticket_number};
                const autoSelectMode = '{auto_select_mode}';
                const areaAutoFallback = {'true' if area_auto_fallback else 'false'};
                const keywordArray = keyword.split(' ');
                const keyword1 = keywordArray[0] || '';
                const keyword2 = keywordArray[1] || '';
                const excludeKeywords = {exclude_keywords};

                console.log('Unified selector execution - keyword:', keyword, 'tickets:', ticketNumber, 'mode:', autoSelectMode, 'fallback:', areaAutoFallback);

                function isSoldOut(element) {{
                    const text = element.textContent || '';
                    const soldOutPatterns = [/\u5269\u9918\\s*0(?!\\d)/, /\u5269\u9918\\s*:\\s*0(?!\\d)/, /sold\\s*out/i, /\u552e\u5b8c/, /\u5df2\u552e\u5b8c/, /\u552e\u7f44/, /\u7121\u5eab\u5b58/];
                    const availablePatterns = [/\u71b1\u8ce3\u4e2d/, /\u71b1\u8ce3/, /\u71b1\u552e/, /\u53ef\u8cfc\u8cb7/, /available/i, /\u5269\u9918\\s*[1-9]\\d*/];

                    for (let pattern of soldOutPatterns) {{
                        if (pattern.test(text)) {{
                            for (let avail of availablePatterns) {{
                                if (avail.test(text)) return false;
                            }}
                            return true;
                        }}
                    }}
                    return false;
                }}

                function containsExcludeKeywords(name) {{
                    if (!excludeKeywords || excludeKeywords.length === 0) return false;
                    for (let kw of excludeKeywords) {{
                        if (kw && name.includes(kw)) return true;
                    }}
                    return false;
                }}

                function getTargetIndex(items, mode) {{
                    const count = items.length;
                    if (count === 0) return -1;
                    switch(mode) {{
                        case 'from top to bottom': return 0;
                        case 'from bottom to top': return count - 1;
                        case 'center': return Math.floor((count - 1) / 2);
                        case 'random': return Math.floor(Math.random() * count);
                        default: return 0;
                    }}
                }}

                const hasExpansionPanel = document.querySelector('.v-expansion-panel');
                const hasCountButton = document.querySelector('.count-button .mdi-plus');

                console.log('hasExpansionPanel:', !!hasExpansionPanel, 'hasCountButton:', !!hasCountButton);

                if (hasExpansionPanel) {{
                    const allPanels = document.querySelectorAll('.v-expansion-panel');
                    // Keep top-level ticket area panels (seats-area with no v-expansion-panel ancestor)
                    // Exclude only nested sub-panels (seats-area itself inside a v-expansion-panel)
                    const panels = [...allPanels].filter(p => {{
                        const seatsArea = p.closest('.seats-area');
                        if (!seatsArea) return true;
                        return !seatsArea.closest('.v-expansion-panel');
                    }});
                    const validPanels = [];

                    for (let i = 0; i < panels.length; i++) {{
                        const panel = panels[i];
                        const nameEl = panel.querySelector('.v-expansion-panel-header');
                        if (nameEl) {{
                            const name = nameEl.textContent.trim().replace(/\\s+/g, ' ');
                            if (!isSoldOut(panel) && !containsExcludeKeywords(name)) {{
                                validPanels.push({{ panel, name, index: i }});
                            }}
                        }}
                    }}

                    console.log('Valid panels:', validPanels.length);
                    if (validPanels.length === 0) {{
                        return {{ success: false, message: 'No valid panels' }};
                    }}

                    let target = null;
                    if (keyword1) {{
                        target = validPanels.find(p => p.name.includes(keyword1) && (!keyword2 || p.name.includes(keyword2)));
                    }}
                    if (!target && keyword1 && !areaAutoFallback) {{
                        return {{ success: false, strict_mode: true }};
                    }}
                    if (!target) {{
                        const idx = getTargetIndex(validPanels, autoSelectMode);
                        target = validPanels[idx];
                    }}

                    if (!target) {{
                        return {{ success: false, message: 'No target panel' }};
                    }}

                    const header = target.panel.querySelector('.v-expansion-panel-header');
                    const isExpanded = target.panel.classList.contains('v-expansion-panel--active');
                    if (!isExpanded && header) {{
                        console.log('Clicking to expand:', target.name);
                        header.click();
                    }}

                    const innerSeatsArea = target.panel.querySelector('.seats-area');
                    if (innerSeatsArea) {{
                        const subPanels = innerSeatsArea.querySelectorAll('.v-expansion-panel');
                        const validSubPanels = [];

                        for (let sp of subPanels) {{
                            const spHeader = sp.querySelector('.v-expansion-panel-header');
                            if (!spHeader) continue;
                            const spName = spHeader.textContent.trim().replace(/\\s+/g, ' ');
                            if (!isSoldOut(sp) && !containsExcludeKeywords(spName)) {{
                                validSubPanels.push({{ panel: sp, name: spName, header: spHeader }});
                            }}
                        }}

                        console.log('Nested structure detected, valid sub-panels:', validSubPanels.length);

                        if (validSubPanels.length === 0) {{
                            return {{ success: false, message: 'Nested: no valid sub-panels' }};
                        }}

                        let subTarget = null;
                        if (keyword1) {{
                            subTarget = validSubPanels.find(p =>
                                p.name.includes(keyword1) && (!keyword2 || p.name.includes(keyword2))
                            );
                        }}
                        if (!subTarget && keyword1 && !areaAutoFallback) {{
                            return {{ success: false, strict_mode: true }};
                        }}
                        if (!subTarget) {{
                            const idx = getTargetIndex(validSubPanels, autoSelectMode);
                            subTarget = validSubPanels[idx];
                        }}

                        const isSubExpanded = subTarget.panel.classList.contains('v-expansion-panel--active');
                        if (!isSubExpanded) {{
                            console.log('Expanding nested sub-panel:', subTarget.name);
                            subTarget.header.click();
                        }}

                        let nestedPlusBtn = subTarget.panel.querySelector('.mdi-plus');
                        if (nestedPlusBtn) {{
                            console.log('Found plus button in nested panel, clicking', ticketNumber, 'times');
                            for (let j = 0; j < ticketNumber; j++) {{ nestedPlusBtn.click(); }}
                            return {{ success: true, type: 'nested_expansion_panel', selected: subTarget.name, clicked: true }};
                        }}

                        return {{ success: true, type: 'nested_expansion_panel',
                                 selected: subTarget.name, clicked: false, needRetry: true }};
                    }}

                    let plusBtn = target.panel.querySelector('.mdi-plus') ||
                                  target.panel.querySelector('.count-button .mdi-plus');

                    if (plusBtn) {{
                        console.log('Found plus button, clicking', ticketNumber, 'times');
                        for (let j = 0; j < ticketNumber; j++) {{
                            plusBtn.click();
                        }}
                        return {{ success: true, type: 'expansion_panel', selected: target.name, clicked: true }};
                    }}

                    return {{ success: true, type: 'expansion_panel', selected: target.name, clicked: false, needRetry: true }};

                }} else if (hasCountButton) {{
                    const rows = document.querySelectorAll('.row.py-1.py-md-4');
                    const validRows = [];

                    for (let row of rows) {{
                        const plusBtn = row.querySelector('.count-button .mdi-plus');
                        if (!plusBtn) continue;

                        const nameEl = row.querySelector('.font-weight-medium');
                        if (nameEl) {{
                            const name = nameEl.textContent.trim();
                            if (!isSoldOut(row) && !containsExcludeKeywords(name)) {{
                                validRows.push({{ row, name, plusBtn }});
                            }}
                        }}
                    }}

                    console.log('Valid rows:', validRows.length);
                    if (validRows.length === 0) {{
                        return {{ success: false, message: 'No valid rows' }};
                    }}

                    let target = null;
                    if (keyword1) {{
                        target = validRows.find(r => r.name.includes(keyword1) && (!keyword2 || r.name.includes(keyword2)));
                    }}
                    if (!target && keyword1 && !areaAutoFallback) {{
                        return {{ success: false, strict_mode: true }};
                    }}
                    if (!target) {{
                        const idx = getTargetIndex(validRows, autoSelectMode);
                        target = validRows[idx];
                    }}

                    if (target && target.plusBtn) {{
                        console.log('Clicking plus button for:', target.name);
                        for (let j = 0; j < ticketNumber; j++) {{
                            target.plusBtn.click();
                        }}
                        return {{ success: true, type: 'count_button', selected: target.name, clicked: true }};
                    }}
                }}

                return {{ success: false, message: 'No selectable elements found' }};
            }})();
        ''')

        result = util.parse_nodriver_result(js_result)

        if isinstance(result, dict):
            is_selected = result.get('success', False) and result.get('clicked', False)

            if result.get('needRetry', False):
                debug.log(f"[RETRY] Panel expanded but plus button not found, retrying...")

                await asyncio.sleep(0.3)

                for retry in range(5):
                    retry_result = await tab.evaluate(f'''
                        (function() {{
                            const seatsAreas = document.querySelectorAll('.seats-area');
                            for (let area of seatsAreas) {{
                                const activeSubPanel = area.querySelector('.v-expansion-panel--active');
                                if (activeSubPanel) {{
                                    const plusBtn = activeSubPanel.querySelector('.mdi-plus') ||
                                                   activeSubPanel.querySelector('.count-button .mdi-plus');
                                    if (plusBtn) {{
                                        console.log('Retry: Found plus button in nested sub-panel');
                                        for (let j = 0; j < {ticket_number}; j++) {{
                                            plusBtn.click();
                                        }}
                                        return {{ success: true, clicked: true }};
                                    }}
                                }}
                            }}

                            const panels = document.querySelectorAll('.v-expansion-panel');
                            for (let panel of panels) {{
                                if (panel.classList.contains('v-expansion-panel--active')) {{
                                    const plusBtn = panel.querySelector('.mdi-plus') ||
                                                   panel.querySelector('.count-button .mdi-plus');
                                    if (plusBtn) {{
                                        console.log('Retry: Found plus button in panel');
                                        for (let j = 0; j < {ticket_number}; j++) {{
                                            plusBtn.click();
                                        }}
                                        return {{ success: true, clicked: true }};
                                    }}
                                }}
                            }}
                            return {{ success: false, clicked: false }};
                        }})();
                    ''')

                    retry_parsed = util.parse_nodriver_result(retry_result)
                    if isinstance(retry_parsed, dict):
                        if retry_parsed.get('clicked', False):
                            debug.log(f"[RETRY] Success on attempt {retry + 1}")
                            is_selected = True
                            break

                    await asyncio.sleep(0.2)

            if debug.enabled:
                if is_selected:
                    selected_type = result.get('type', '')
                    selected_name = result.get('selected', '')
                    debug.log(f"Selection successful - type: {selected_type}, item: {selected_name}")
                else:
                    debug.log(f"Selection failed: {result.get('message', 'unknown error')}")
        else:
            debug.log(f"Unified selector returned invalid result: {result}")
            is_selected = False

    except Exception as exc:
        if debug.enabled:
            debug.log(f"Unified selector exception error: {exc}")
            debug.log(f"Exception type: {type(exc).__name__}")
            debug.log(f"Traceback: {traceback.format_exc()}")
        is_selected = False

    if not is_selected:
        try:
            debug.log("Checking page status to decide whether to continue...")

            page_status = await tab.evaluate('''
                (function() {
                    const ticketCounts = document.querySelectorAll('.count-button div');
                    let hasTickets = false;
                    for (let count of ticketCounts) {
                        const text = count.textContent.trim();
                        if (text && !isNaN(text) && parseInt(text) > 0) {
                            hasTickets = true;
                            break;
                        }
                    }

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
                debug.log(f"[STATUS] Page state: Has tickets={status.get('hasTickets', False)}, Button enabled={status.get('buttonEnabled', False)}")

                if status.get('canContinue', False):
                    debug.log("Page status is good, considered selection successful")
                    is_selected = True

        except Exception as backup_exc:
            debug.log(f"Backup check failed: {backup_exc}")

    return is_selected


async def nodriver_ticketplus_click_next_button_unified(tab, config_dict):
    """TicketPlus unified next button clicker - layout_style independent."""
    debug = util.create_debug_logger(config_dict)

    debug.log("Unified next button clicker started")

    try:
        if await sleep_with_pause_check(tab, 0.6, config_dict):
            return False

        js_result = await tab.evaluate('''
            (function() {
                console.log('[NEXT BUTTON] Unified next button clicker started');

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

                const buttonSelectors = [
                    'button.nextBtn:not(.disabledBtn):not(.v-btn--disabled)',
                    '.order-footer button.nextBtn:not(.disabledBtn)',
                    '.order-footer .v-btn--has-bg:not(.v-btn--disabled):not(.disabledBtn)',
                    'button:contains("下一步"):not(.disabledBtn)',
                    'button:contains("Next"):not(.disabledBtn)',
                    '.nextBtn:not([disabled])'
                ];

                let nextButton = null;
                for (let selector of buttonSelectors) {
                    nextButton = document.querySelector(selector);
                    if (nextButton && !nextButton.disabled && !nextButton.classList.contains('v-btn--disabled') && !nextButton.classList.contains('disabledBtn')) {
                        console.log('[SUCCESS] Found enabled next button:', selector);
                        break;
                    }
                }

                if (!nextButton) {
                    console.log('[WAITING] Waiting for next button to enable...');
                    return waitForButtonEnable('button.nextBtn, .nextBtn').then(button => {
                        if (button) {
                            console.log('[SUCCESS] Next button enabled');
                            button.click();
                            return {
                                success: true,
                                message: 'Next button clicked (after wait)',
                                buttonText: button.textContent.trim()
                            };
                        } else {
                            console.log('[ERROR] Next button still not found after wait');
                            return { success: false, message: 'Next button still not found after wait' };
                        }
                    });
                }

                nextButton.click();
                console.log('[SUCCESS] Next button clicked');

                return {
                    success: true,
                    message: 'Next button clicked',
                    buttonText: nextButton.textContent.trim()
                };
            })();
        ''')

        result = util.parse_nodriver_result(js_result)
        if isinstance(result, dict):
            success = result.get('success', False)
            if debug.enabled:
                if success:
                    button_text = result.get('buttonText', '')
                    debug.log(f"[SUCCESS] Next button clicked successfully - Button text: {button_text}")
                else:
                    debug.log(f"[ERROR] Next button click failed: {result.get('message', 'Unknown error')}")
            return success

    except Exception as exc:
        debug.log(f"Unified next button click error: {exc}")

    return False


async def nodriver_ticketplus_ticket_agree(tab, config_dict):
    """TicketPlus agreement checkbox."""
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_finish_checkbox_click = False

    try:
        agree_checkbox_list = await tab.query_selector_all('input[type="checkbox"]')

        for checkbox in agree_checkbox_list:
            try:
                if not checkbox:
                    continue

                is_checked = await checkbox.evaluate('el => el.checked')

                if not is_checked:
                    await checkbox.click()

                    is_checked_after = await checkbox.evaluate('el => el.checked')
                    if is_checked_after:
                        is_finish_checkbox_click = True
                        debug.log("successfully checked agreement checkbox")
                    else:
                        if checkbox:
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
                                debug.log("successfully checked agreement checkbox via JS")
                else:
                    is_finish_checkbox_click = True
                    debug.log("agreement checkbox already checked")

            except Exception as exc:
                debug.log("process checkbox fail:", exc)
                continue

    except Exception as exc:
        debug.log("find agreement checkbox fail:", exc)

    return is_finish_checkbox_click


async def nodriver_ticketplus_accept_realname_card(tab):
    """Accept realname card popup."""
    is_button_clicked = False
    try:
        button = await tab.query_selector('div.v-dialog__content > div > div > div > div.row > div > button.primary')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked


async def nodriver_ticketplus_accept_other_activity(tab):
    """Accept other activity popup."""
    is_button_clicked = False
    try:
        button = await tab.query_selector('div[role="dialog"] > div.v-dialog > button.primary-1 > span > i.v-icon')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked


async def nodriver_ticketplus_accept_order_fail(tab):
    """Handle order failure popup."""
    is_button_clicked = False
    try:
        button = await tab.query_selector('div[role="dialog"] > div.v-dialog > div.v-card > div > div.row > div.col > button.v-btn')
        if button:
            await button.click()
            is_button_clicked = True
    except Exception as exc:
        pass
    return is_button_clicked


async def nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False):
    """Check queue status - optimized to avoid duplicate output."""
    debug = util.create_debug_logger(enabled=(config_dict.get("advanced", {}).get("verbose", False) or force_show_debug))

    try:
        result = await tab.evaluate('''
            (function() {
                const queueKeywords = [
                    '\u6392\u968a\u8cfc\u7968\u4e2d',
                    '\u8acb\u7a0d\u5019',
                    '\u8acb\u5225\u96e2\u958b\u9801\u9762',
                    '\u8acb\u52ff\u96e2\u958b',
                    '\u8acb\u52ff\u95dc\u9589\u7db2\u9801',
                    '\u540c\u6642\u4f7f\u7528\u591a\u500b\u88dd\u7f6e',
                    '\u8996\u7a97\u8cfc\u7968',
                    '\u6b63\u5728\u8655\u7406',
                    '\u8655\u7406\u4e2d'
                ];

                const bodyText = document.body.textContent || '';

                const hasQueueKeyword = queueKeywords.some(keyword => bodyText.includes(keyword));

                const overlayScrim = document.querySelector('.v-overlay__scrim');
                const hasOverlay = overlayScrim &&
                    (overlayScrim.style.opacity === '1' ||
                     overlayScrim.style.display !== 'none');

                const dialogText = document.querySelector('.v-dialog')?.textContent || '';
                const hasQueueDialog = dialogText.includes('\u6392\u968a') ||
                                       dialogText.includes('\u8acb\u7a0d\u5019');

                const foundKeywords = queueKeywords.filter(keyword => bodyText.includes(keyword));

                return {
                    inQueue: hasQueueKeyword || hasOverlay || hasQueueDialog,
                    queueTitle: '',
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
            if is_in_queue and force_show_debug:
                debug.log("[QUEUE] Queue status detected")
                if result.get('hasOverlay'):
                    debug.log("   Overlay scrim found (v-overlay__scrim)")
                if result.get('hasQueueDialog'):
                    debug.log(f"   Dialog content: {result.get('dialogText', '')}")
                if result.get('foundKeywords'):
                    keywords = result.get('foundKeywords', [])
                    if keywords and isinstance(keywords[0], dict):
                        keywords = [str(k.get('value', k)) for k in keywords]
                    elif keywords:
                        keywords = [str(k) for k in keywords]
                    if keywords:
                        debug.log(f"   Keywords found: {', '.join(keywords)}")
            return is_in_queue

        return False

    except Exception as exc:
        debug.log(f"Queue status check error: {exc}")
        return False


async def nodriver_ticketplus_confirm(tab, config_dict):
    """Confirmation page handler."""
    is_checkbox_checked = await nodriver_ticketplus_ticket_agree(tab, config_dict)

    is_confirm_clicked = False
    if is_checkbox_checked:
        try:
            confirm_button = await tab.query_selector('button.v-btn.primary')
            if not confirm_button:
                confirm_button = await tab.query_selector('button[type="submit"]')

            if confirm_button:
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


async def nodriver_ticketplus_order(tab, config_dict, ocr, Captcha_Browser):
    """TicketPlus order processing - supports three layout detection modes.

    Modifies _state in place (no return value).
    """
    debug = util.create_debug_logger(config_dict)

    if _state.get("is_ticket_assigned", False):
        debug.log("Ticket selection completed, skipping duplicate execution")
        return

    debug.log("=== TicketPlus Auto Layout Detection Started ===")

    if await sleep_with_pause_check(tab, random.uniform(0.8, 1.5), config_dict):
        debug.log("Paused during page wait")
        return

    layout_info = await nodriver_ticketplus_detect_layout_style(tab, config_dict)

    if layout_info and layout_info.get('paused'):
        debug.log("Paused during layout detection")
        return

    current_layout_style = layout_info.get('style', 0) if isinstance(layout_info, dict) else 0

    if debug.enabled:
        layout_names = {1: "Expansion panel (Page4)", 2: "Seat selection (Page2)", 3: "Simplified (Page1/Page3)"}
        button_status = "Enabled" if layout_info.get('button_enabled', False) else "Disabled"
        debug.log(f"Detected layout style: {current_layout_style} - {layout_names.get(current_layout_style, 'Unknown')}")
        debug.log(f"Layout detection details: Button found={layout_info.get('found', False)}, Button status={button_status}")
        if layout_info.get('debug_info'):
            debug.log(f"Layout detection debug: {layout_info.get('debug_info')}")

    is_button_enabled = await nodriver_ticketplus_check_next_button(tab)

    debug.log(f"Next button status: {'Enabled' if is_button_enabled else 'Disabled'}")

    is_price_assign_by_bot = False

    area_keyword_raw = config_dict.get("area_auto_select", {}).get("area_keyword", "").strip()

    keyword_array = util.parse_keyword_string_to_array(area_keyword_raw)

    debug.log(f"[TicketPlus] Parsed keywords: {keyword_array}")
    debug.log(f"[TicketPlus] Total keyword groups: {len(keyword_array)}")

    need_select_ticket = True

    debug.log(f"Ticket selection is always required (TicketPlus quirk)")

    is_price_assign_by_bot = False
    keyword_matched = False

    if len(keyword_array) > 0:
        for keyword_index, area_keyword_item in enumerate(keyword_array):
            debug.log(f"[TicketPlus AREA KEYWORD] Trying keyword #{keyword_index + 1}/{len(keyword_array)}: '{area_keyword_item}'")

            is_price_assign_by_bot = await nodriver_ticketplus_unified_select(tab, config_dict, area_keyword_item)

            if is_price_assign_by_bot:
                keyword_matched = True
                debug.log(f"[TicketPlus AREA KEYWORD] Keyword #{keyword_index + 1} matched: '{area_keyword_item}' [OK]")
                break

            debug.log(f"[TicketPlus AREA KEYWORD] Keyword #{keyword_index + 1} failed, trying next...")

        if not keyword_matched:
            debug.log(f"[TicketPlus AREA KEYWORD] All {len(keyword_array)} keywords failed to match")
    else:
        debug.log(f"[TicketPlus AREA KEYWORD] No keyword specified, using auto select mode")
        is_price_assign_by_bot = await nodriver_ticketplus_unified_select(tab, config_dict, "")

    is_need_refresh = not is_price_assign_by_bot

    if is_price_assign_by_bot:
        if await check_and_handle_pause(config_dict):
            return

        debug.log("Ticket selection successful, processing discount code and submit")

        is_answer_sent, _state["fail_list"], is_question_popup = await nodriver_ticketplus_order_exclusive_code(tab, config_dict, _state["fail_list"])

        if await sleep_with_pause_check(tab, 0.3, config_dict):
            debug.log("Paused before form submission")
            return
        await nodriver_ticketplus_ticket_agree(tab, config_dict)

        is_form_submitted = await nodriver_ticketplus_click_next_button_unified(tab, config_dict)

        if is_form_submitted:
            await tab.sleep(random.uniform(5.0, 10.0))

            is_in_queue = await nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False)
            if is_in_queue:
                debug.log("Entered queue monitoring (check every 5 seconds, display only on status change)")

                last_url = ""

                while True:
                    if await check_and_handle_pause(config_dict):
                        break

                    try:
                        current_url = tab.url

                        if '/confirm/' in current_url.lower() or '/confirmseat/' in current_url.lower():
                            debug.log("Detected entry to confirmation page, exiting queue monitoring")
                            break

                        if current_url != last_url:
                            debug.log(f"Page status update - URL: {current_url}")
                            last_url = current_url

                        is_still_in_queue = await nodriver_ticketplus_check_queue_status(tab, config_dict, force_show_debug=False)

                        if not is_still_in_queue:
                            if '/confirm/' in current_url.lower() or '/confirmseat/' in current_url.lower():
                                debug.log("Queue ended, entered confirmation page")
                                break
                            else:
                                debug.log("[QUEUE END] Queue ended, continuing page processing")
                                break

                        await tab.sleep(random.uniform(5.0, 10.0))

                    except Exception as exc:
                        debug.log(f"Queue monitoring error: {exc}")
                        break

        debug.log(f"Form submission: {'Success' if is_form_submitted else 'Failed'}")
    else:
        debug.log("Ticket selection failed, cannot continue")

        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
        if auto_reload_interval >= 0:
            if auto_reload_interval > 0:
                debug.log(f"[AUTO RELOAD] Waiting {auto_reload_interval} seconds before reload...")
                await asyncio.sleep(auto_reload_interval)
            debug.log("[AUTO RELOAD] Refreshing ticket count...")
            try:
                clicked = await _ticketplus_click_refresh_button(tab, debug)
                if not clicked:
                    await tab.reload()
                    debug.log("[AUTO RELOAD] Full page reload (button not found)")
            except Exception as reload_exc:
                debug.log(f"[AUTO RELOAD] Reload failed: {reload_exc}")

    debug.log("=== TicketPlus Simplified Booking Ended ===")


async def nodriver_ticketplus_wait_for_vue_ready(tab, max_wait_ms=800):
    """Wait for Vue.js ticket area elements to render (dynamic detection).

    Args:
        tab: NoDriver tab
        max_wait_ms: Maximum wait time in milliseconds, default 800ms

    Returns:
        bool: True if Vue.js is ready, False if timed out
    """
    try:
        await asyncio.sleep(0.15)

        result = await tab.evaluate(f'''
            (function() {{
                return new Promise((resolve) => {{
                    const startTime = Date.now();
                    const maxWait = {max_wait_ms};

                    const check = () => {{
                        const selectors = [
                            '.v-expansion-panel-header',
                            '.order-content .v-btn',
                            'button.nextBtn',
                            '.ticket-list button'
                        ];

                        let hasContent = false;
                        for (const selector of selectors) {{
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {{
                                hasContent = Array.from(elements).some(el => {{
                                    const text = el.textContent || '';
                                    return text.includes('NT') ||
                                           text.includes('\u5269\u9918') ||
                                           text.includes('\u71b1\u8ce3') ||
                                           text.includes('\u4e0b\u4e00\u6b65') ||
                                           text.includes('\u552e\u5b8c');
                                }});
                                if (hasContent) break;
                            }}
                        }}

                        if (hasContent) {{
                            resolve({{ ready: true, elapsed: Date.now() - startTime }});
                        }} else if (Date.now() - startTime < maxWait) {{
                            setTimeout(check, 30);
                        }} else {{
                            resolve({{ ready: false, elapsed: maxWait }});
                        }}
                    }};

                    check();
                }});
            }})();
        ''')

        if isinstance(result, dict):
            return result.get('ready', False)
        return False

    except Exception as exc:
        return False


async def nodriver_ticketplus_check_next_button(tab):
    """Check if next button is enabled."""
    try:
        result = await tab.evaluate('''
            (function() {
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
    """Handle exclusive discount codes."""
    debug = util.create_debug_logger(config_dict)

    if await check_and_handle_pause(config_dict):
        return False, fail_list, False

    discount_code = config_dict["advanced"].get("discount_code", "").strip()

    if not discount_code:
        debug.log("[DISCOUNT CODE] No discount code configured, skipping")
        return False, fail_list, False

    debug.log(f"[DISCOUNT CODE] Attempting to fill discount code: {discount_code}")

    try:
        escaped_discount_code = discount_code.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")

        result = await tab.evaluate(f'''
            (function() {{
                const keywords = ['\u5e8f\u865f', '\u52a0\u8cfc', '\u512a\u60e0'];
                const discountCode = '{escaped_discount_code}';
                let filledCount = 0;

                const labelDivs = document.querySelectorAll('.exclusive-code .label');
                for (let label of labelDivs) {{
                    const labelText = label.textContent.trim();
                    const container = label.closest('.exclusive-code');
                    if (!container) continue;

                    const input = container.querySelector('.v-text-field__slot input[type="text"]');

                    const hasKeyword = keywords.some(keyword => labelText.includes(keyword));
                    if (hasKeyword && input && !input.value) {{
                        input.value = discountCode;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        filledCount++;
                    }}
                }}

                return {{
                    success: filledCount > 0,
                    filledCount: filledCount
                }};
            }})()
        ''')

        if result:
            if isinstance(result, dict):
                success = result.get('success', False)
                filled_count = result.get('filledCount', 0)
            else:
                debug.log(f"[DISCOUNT CODE] Unexpected result type: {type(result)}, value: {result}")
                success = True
                filled_count = 1

            if success and filled_count > 0:
                debug.log(f"[DISCOUNT CODE] Successfully filled {filled_count} discount code field(s)")
                return True, fail_list, False

        debug.log("[DISCOUNT CODE] No matching discount code fields found on page")
        return False, fail_list, False

    except Exception as e:
        debug.log(f"[DISCOUNT CODE] Error filling discount code: {str(e)}")
        return False, fail_list, False


async def nodriver_ticketplus_main(tab, url, config_dict, ocr, Captcha_Browser):
    """TicketPlus main entry point.

    Returns:
        dict: {"purchase_completed": bool, "is_ticket_assigned": bool}
    """
    if await check_and_handle_pause(config_dict):
        return _get_status()

    debug = util.create_debug_logger(config_dict)

    if not _state:
        _state["fail_list"] = []
        _state["is_popup_confirm"] = False
        _state["is_ticket_assigned"] = False
        _state["start_time"] = None
        _state["done_time"] = None
        _state["elapsed_time"] = None
        _state["signin_form_filled"] = False
        _state["purchase_completed"] = False

    home_url = 'https://ticketplus.com.tw/'
    is_user_signin = False
    if home_url == url.lower():
        if config_dict["ocr_captcha"]["enable"]:
            domain_name = url.split('/')[2]
            if not Captcha_Browser is None:
                Captcha_Browser.set_domain(domain_name)

        is_user_signin = await nodriver_ticketplus_account_auto_fill(tab, config_dict)

    if is_user_signin:
        config_homepage = config_dict["homepage"].lower().rstrip('/')
        is_homepage_target = config_homepage in ['https://ticketplus.com.tw', 'ticketplus.com.tw']
        if not is_homepage_target and url.lower() != config_dict["homepage"].lower():
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
            _state["is_popup_confirm"] = False
            _state["order_page_visited"] = False

            is_button_pressed = await nodriver_ticketplus_accept_realname_card(tab)
            debug.log(f"[TICKETPLUS] Realname Card: {is_button_pressed}")

            is_button_pressed = await nodriver_ticketplus_accept_other_activity(tab)
            debug.log(f"[TICKETPLUS] Other Activity: {is_button_pressed}")

            if config_dict["date_auto_select"]["enable"]:
                await nodriver_ticketplus_date_auto_select(tab, config_dict)

    # https://ticketplus.com.tw/order/XXX/OOO
    if '/order/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            _state["start_time"] = time.time()

            is_first_visit = not _state.get("order_page_visited", False)
            if is_first_visit:
                max_wait = 2000
                fallback_delay = 0.5
                _state["order_page_visited"] = True
            else:
                max_wait = 1000
                fallback_delay = 0.3

            if debug.enabled:
                visit_type = "First visit" if is_first_visit else "Reload"
                debug.log(f"[VUE INIT] {visit_type}, dynamic detection (max {max_wait}ms)...")

            is_ready = await nodriver_ticketplus_wait_for_vue_ready(tab, max_wait_ms=max_wait)

            debug.log(f"[VUE INIT] Vue.js ready: {is_ready}")

            if not is_ready:
                await asyncio.sleep(fallback_delay)

            is_button_pressed = await nodriver_ticketplus_accept_realname_card(tab)
            is_order_fail_handled = await nodriver_ticketplus_accept_order_fail(tab)

            await nodriver_ticketplus_order(tab, config_dict, ocr, Captcha_Browser)

    else:
        _state["fail_list"] = []
        _state["is_ticket_assigned"] = False
        _state["start_time"] = None

    # https://ticketplus.com.tw/confirm/xx/oo
    # https://ticketplus.com.tw/confirmseat/xx/oo
    if '/confirm/' in url.lower() or '/confirmseat/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            _state["is_ticket_assigned"] = True

            if not _state["is_popup_confirm"]:
                _state["is_popup_confirm"] = True

                if _state["start_time"]:
                    _state["done_time"] = time.time()
                    _state["elapsed_time"] = _state["done_time"] - _state["start_time"]
                    debug.log(f"[TICKETPLUS] NoDriver TicketPlus booking time: {_state['elapsed_time']:.3f} seconds")

                debug.log("[TICKETPLUS] Entered confirmation page, booking successful")

                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)
                send_discord_notification(config_dict, "order", "TicketPlus")
                send_telegram_notification(config_dict, "order", "TicketPlus")

                try:
                    await nodriver_ticketplus_confirm(tab, config_dict)
                    debug.log("[TICKETPLUS] Confirmation page processing completed")
                except Exception as exc:
                    debug.log(f"[TICKETPLUS] Confirmation page processing error: {exc}")

            _state["purchase_completed"] = True
        else:
            _state["is_popup_confirm"] = False
    else:
        _state["is_popup_confirm"] = False

    return _get_status()
