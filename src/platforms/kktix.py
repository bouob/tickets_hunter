#encoding=utf-8
# =============================================================================
# KKTIX Platform Module
# Extracted from nodriver_tixcraft.py during modularization (Phase 1)
# =============================================================================

import asyncio
from datetime import datetime
import json
import os
import random
import re
import threading
import time
import urllib.parse
import webbrowser

from zendriver import cdp

import util
from nodriver_common import (
    check_and_handle_pause,
    nodriver_check_checkbox,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    write_question_to_file,
    CONST_FROM_TOP_TO_BOTTOM,
    CONST_MAXBOT_ANSWER_ONLINE_FILE,
    CONST_MAXBOT_INT28_FILE,
)

__all__ = [
    "nodriver_kktix_signin",
    "nodriver_kktix_paused_main",
    "nodriver_kktix_travel_price_list",
    "nodriver_kktix_assign_ticket_number",
    "nodriver_kktix_reg_captcha",
    "debug_kktix_page_state",
    "nodriver_kktix_date_auto_select",
    "nodriver_kktix_events_press_next_button",
    "nodriver_kktix_check_guest_modal",
    "nodriver_kktix_press_next_button",
    "nodriver_kktix_check_ticket_page_status",
    "nodriver_kktix_reg_new_main",
    "check_kktix_got_ticket",
    "nodriver_kktix_main",
    "nodriver_kktix_booking_main",
    "nodriver_kktix_confirm_order_button",
    "nodriver_kktix_order_member_code",
    "is_kktix_account_configured",
    "nodriver_kktix_check_form_state",
    "nodriver_kktix_check_qualification",
    "nodriver_kktix_check_form_ready",
    "nodriver_kktix_wait_member_code_enabled",
    "nodriver_kktix_select_qualification",
    "nodriver_kktix_handle_qualification_and_next",
    "CONST_KKTIX_FORM_STATE_JS",
]

# Module-level state (replaces global kktix_dict)
_state = {}

# How long after pressing "next" to leave the ticket flow alone. Long enough for
# the submission to navigate, short enough that a failed press retries almost
# immediately - this window is the whole reason the guard cannot latch.
CONST_KKTIX_NEXT_BUTTON_COOLDOWN = 1.5


def is_kktix_account_configured(config_dict):
    """Single source of truth for "is a KKTIX account set up?" (issue #374).

    Three call sites used to disagree: the main loop rewrote the homepage to
    the sign-in page for any non-empty account, while the sign-in and guest
    redirect paths required more than 4 characters. A 1-4 character account
    therefore landed on the login page that nobody would ever fill in, which
    reads to the user as "the bot does not type my credentials".
    """
    account = config_dict.get("accounts", {}).get("kktix_account", "")
    return len(account.strip()) > 0


async def nodriver_kktix_check_queue_page(tab, config_dict):
    """Detect KKTIX waiting room page (queue shown before site entry).

    Markers from .temp/platform/kktix/kkwaiting.html: #cf-time countdown
    and the "high traffic" heading. The page refreshes itself and warns
    against manual refresh, so callers must NOT reload while queueing.

    Returns:
        bool: True if currently on the queue page
    """
    debug = util.create_debug_logger(config_dict)

    is_queue_page = False
    wait_text = ""
    try:
        result = await tab.evaluate('''
            (function() {
                const cfTime = document.querySelector('#cf-time');
                if (cfTime) {
                    return { isQueue: true, waitText: cfTime.textContent.trim() };
                }
                const heading = document.querySelector('main h1');
                if (heading && heading.textContent.indexOf('目前網站人流眾多') >= 0) {
                    return { isQueue: true, waitText: '' };
                }
                return { isQueue: false, waitText: '' };
            })()
        ''')
        if isinstance(result, dict):
            is_queue_page = bool(result.get('isQueue', False))
            wait_text = result.get('waitText', '')
    except Exception:
        pass

    if is_queue_page:
        current_time = time.time()
        if current_time - _state.get("queue_log_time", 0) > 10:
            _state["queue_log_time"] = current_time
            debug.log(f"[KKTIX QUEUE] In waiting room, page auto-refreshes, do not reload. {wait_text}".rstrip())

    return is_queue_page


async def nodriver_kktix_signin(tab, url, config_dict):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    debug.log("nodriver_kktix_signin:", url)

    # 解析 back_to 參數取得真正的目標頁面
    target_url = config_dict["homepage"]  # 預設值
    try:
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        if 'back_to' in params and len(params['back_to']) > 0:
            target_url = params['back_to'][0]
    except Exception as exc:
        debug.log(f"[KKTIX SIGNIN] Failed to parse back_to parameter: {exc}")

    # Queue page may replace the login form entirely; wait it out
    if await nodriver_kktix_check_queue_page(tab, config_dict):
        return False

    await asyncio.sleep(random.uniform(0.2, 0.5))

    kktix_account = config_dict["accounts"]["kktix_account"]
    kktix_password = config_dict["accounts"]["kktix_password"].strip()

    has_redirected = False
    if is_kktix_account_configured(config_dict):
        try:
            # A missing field used to be skipped silently, so a queue room or a
            # Cloudflare interstitial looked exactly like "credentials not typed"
            # in the log. Report it and stop instead of submitting a dead form.
            account = await tab.query_selector("#user_login")
            if account is None:
                debug.log("[KKTIX SIGNIN] #user_login not found; page may be a queue room, "
                          "a Cloudflare challenge, or already signed in")
                return False
            await account.send_keys(kktix_account)
            await asyncio.sleep(random.uniform(0.1, 0.2))

            password = await tab.query_selector("#user_password")
            if password is None:
                debug.log("[KKTIX SIGNIN] #user_password not found; login form is incomplete")
                return False
            await password.send_keys(kktix_password)
            await asyncio.sleep(random.uniform(0.1, 0.2))

            # The submit button used to be matched by its Chinese value only,
            # which fails silently on any other locale.
            submit_result = await tab.evaluate('''
                (function() {
                    const selectors = [
                        'form#new_user input[type="submit"]',
                        'form[action*="sign_in"] input[type="submit"]',
                        'input[type="submit"][value="登入"]',
                        'button[type="submit"]'
                    ];
                    let candidateCount = 0;
                    for (const sel of selectors) {
                        const btn = document.querySelector(sel);
                        if (btn) {
                            candidateCount += 1;
                            if (!btn.disabled) {
                                btn.click();
                                return { clicked: true, selector: sel, candidateCount: candidateCount };
                            }
                        }
                    }
                    return { clicked: false, selector: '', candidateCount: candidateCount };
                })()
            ''')
            submit_result = util.parse_nodriver_result(submit_result)
            if isinstance(submit_result, dict) and submit_result.get('clicked'):
                debug.log(f"[KKTIX SIGNIN] Submit clicked via {submit_result.get('selector')}")
            else:
                candidate_count = 0
                if isinstance(submit_result, dict):
                    candidate_count = submit_result.get('candidateCount', 0)
                debug.log(f"[KKTIX SIGNIN] No clickable submit button found "
                          f"(candidates={candidate_count}); locale may differ or form not rendered")
                return False

            # Smart polling: wait for login completion (URL change from sign_in page)
            #
            # Do NOT add an early return when Cloudflare takes over the page.
            # It was tried and measurably made things worse: the main loop's
            # Cloudflare check only re-arms on a URL change, and returning during
            # the __cf_chl_rt_tk redirect means it runs before the challenge
            # target exists, finds nothing, and never looks again - the bot then
            # idles forever. Sitting out the full 10s wastes time but gives the
            # challenge time to render, which is what lets the main loop solve it.
            # Fixing this properly needs event-driven detection
            # (cdp.target.TargetCreated), not an earlier poll.
            max_wait = 10
            check_interval = 0.3
            max_attempts = int(max_wait / check_interval)
            login_completed = False
            url_error_count = 0
            last_url_exc = ""

            for attempt in range(max_attempts):
                # 登入後檢查暫停
                if await check_and_handle_pause(config_dict):
                    return False

                try:
                    current_url = await tab.evaluate('window.location.href')

                    # Detect if left sign_in page (login completed)
                    if '/users/sign_in' not in current_url:
                        login_completed = True
                        debug.log(f"[KKTIX SIGNIN] Login completed after {attempt * check_interval:.1f}s, redirected to: {current_url}")
                        break
                except Exception as exc:
                    # Report the first failure with its attempt index, then only
                    # the summary below; printing every attempt floods the log.
                    url_error_count += 1
                    last_url_exc = str(exc)
                    if url_error_count == 1:
                        debug.log(f"[KKTIX SIGNIN] URL check failed "
                                  f"(attempt {attempt + 1}/{max_attempts}): {exc}")

                if attempt < max_attempts - 1:
                    await asyncio.sleep(check_interval)

            if not login_completed:
                debug.log(f"[KKTIX SIGNIN] Login timeout after {max_wait}s; "
                          f"{url_error_count}/{max_attempts} URL checks failed, "
                          f"last error: {last_url_exc}")

            # Check if need to manually redirect to back_to URL
            try:
                current_url = await tab.evaluate('window.location.href')
                if current_url and ('kktix.com/' in current_url or 'kktix.cc/' in current_url):
                    if '/users/sign_in' in current_url:
                        # Still on sign_in page (login failed or queue intercepted);
                        # jumping to back_to here would enter the event as a guest
                        debug.log("[KKTIX SIGNIN] Still on sign_in page, will retry on next loop")
                    elif (current_url.endswith('/') or '/users/' in current_url) and target_url != current_url:
                        # If on homepage or user page, manually redirect to back_to URL
                        debug.log(f"[KKTIX SIGNIN] Currently on homepage/user page, redirecting to: {target_url}")
                        await tab.get(target_url)
                        await asyncio.sleep(random.uniform(1.2, 2.3))
                        has_redirected = True
                    else:
                        debug.log(f"[KKTIX SIGNIN] Already on target page: {current_url}")
            except Exception as redirect_error:
                debug.log(f"[KKTIX SIGNIN] Redirect failed: {redirect_error}")

        except Exception as e:
            debug.log(f"[KKTIX SIGNIN] {e}")
            pass

    return has_redirected

async def nodriver_kktix_redirect_to_signin_if_guest(tab, url, config_dict):
    """Stage 2: detect guest session on registration page, bounce to sign_in.

    The KKTIX queue can drop users on /registrations/new before login; ticket
    rows then render without input fields and keyword matching never succeeds.
    Navbar marker: li.not-signed-in loses the .hidden class for guests
    (verified across .temp/platform/kktix/*.html snapshots).

    Returns:
        bool: True if guest session detected (caller should skip this round)
    """
    if not is_kktix_account_configured(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    is_guest = False
    try:
        is_guest = bool(await tab.evaluate(
            "!!document.querySelector('li.not-signed-in:not(.hidden)')"
        ))
    except Exception:
        pass
    if not is_guest:
        return False

    current_time = time.time()
    redirect_interval = config_dict["advanced"].get("auto_reload_page_interval", 3)
    if redirect_interval <= 0:
        redirect_interval = 3
    if current_time - _state.get("last_signin_redirect_time", 0) > redirect_interval:
        _state["last_signin_redirect_time"] = current_time
        sign_in_url = "https://kktix.com/users/sign_in?back_to=" + urllib.parse.quote(url, safe='')
        debug.log("[KKTIX] Guest session on registration page, redirecting to sign_in")
        try:
            await tab.get(sign_in_url)
        except Exception as exc:
            debug.log(f"[KKTIX] Redirect to sign_in failed: {exc}")

    return True

async def nodriver_kktix_paused_main(tab, url, config_dict):
    debug = util.create_debug_logger(config_dict)

    is_url_contain_sign_in = False
    if '/users/sign_in?' in url:
        redirect_needed = await nodriver_kktix_signin(tab, url, config_dict)
        is_url_contain_sign_in = True

        return redirect_needed

    return False


async def nodriver_kktix_travel_price_list(tab, config_dict, kktix_area_auto_select_mode, kktix_area_keyword):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return True, False, None

    debug = util.create_debug_logger(config_dict)

    ticket_number = config_dict["ticket_number"]

    areas = None
    pending_tickets = None
    is_ticket_number_assigned = False

    ticket_price_list = None
    try:
        ticket_price_list = await tab.evaluate('''
            (function() {
                let rows = Array.from(document.querySelectorAll('div.display-table-row'));
                if (rows.length === 0) {
                    rows = Array.from(document.querySelectorAll('div.ticket-item'));
                }

                let inputIndex = 0;
                return rows.map((row, rowIndex) => {
                    const input = row.querySelector('input');
                    const hasInput = !!input;
                    const rowInputIndex = hasInput ? inputIndex : null;
                    if (hasInput) {
                        inputIndex += 1;
                    }

                    return {
                        index: rowIndex,
                        html: row.innerHTML || "",
                        text: row.textContent || row.innerText || "",
                        hasInput: hasInput,
                        inputValue: input ? input.value : "0",
                        inputIndex: rowInputIndex
                    };
                });
            })()
        ''')
        ticket_price_list = util.parse_nodriver_result(ticket_price_list)
        if not isinstance(ticket_price_list, list):
            ticket_price_list = None
    except Exception as exc:
        ticket_price_list = None
        debug.log(f"[KKTIX] find ticket-price Exception: {exc}")
        pass

    is_dom_ready = True
    price_list_count = 0
    if not ticket_price_list is None:
        price_list_count = len(ticket_price_list)
    else:
        is_dom_ready = False
        debug.log("[KKTIX] find ticket-price fail")

    if price_list_count > 0:
        areas = []
        pending_tickets = []  # Track matched tickets waiting for "not yet open" to open

        # Parse area keywords (space-separated = AND logic)
        # Support N keywords (previously limited to 2)
        kktix_area_keyword_array = [kw.strip() for kw in kktix_area_keyword.split(' ') if kw.strip()]
        # Clean stop words for all keywords
        kktix_area_keyword_array = [util.format_keyword_string(kw) for kw in kktix_area_keyword_array]

        debug.log(f'[KKTIX AREA] Keywords (AND logic): {kktix_area_keyword_array}')

        for i, ticket_info in enumerate(ticket_price_list):
            row_text = ""
            original_text = ""
            row_html = ticket_info.get('html', '') if isinstance(ticket_info, dict) else ""
            row_input = None
            current_ticket_number = "0"
            try:
                if ticket_info:
                    row_text = ticket_info.get('text', '') or util.remove_html_tags(row_html)
                    original_text = ' '.join(row_text.split())
                    current_ticket_number = ticket_info.get('inputValue', '0')
                    if ticket_info.get('hasInput'):
                        row_input = ticket_info.get('inputIndex')  # 儲存有效 input 的索引
            except Exception as exc:
                is_dom_ready = False
                debug.log(f"Error in nodriver_kktix_travel_price_list: {exc}")
                # error, exit loop
                break

            if len(row_text) > 0:
                # Preserve "not yet open" tickets for keyword matching
                # Only filter permanently unavailable tickets (sold out)

                # Multi-language "sold out" keyword filtering
                sold_out_keywords = ['暫無票', '已售完', 'Sold Out', 'sold out', '完売']
                is_sold_out = any(kw in row_text for kw in sold_out_keywords)

                if is_sold_out:
                    row_text = ""
                    debug.log(f"  -> Filtered: sold out")

                # Multi-language "not yet open" check (preserve these tickets for keyword matching)
                not_yet_open_keywords = [
                    '未開賣', '尚未開賣', '尚未開始', '即將開賣',
                    'Not Started', 'not started',
                    'まだ発売'
                ]
                has_not_yet_open_status = any(kw in row_text for kw in not_yet_open_keywords)

                if has_not_yet_open_status:
                    debug.log(f"  -> Preserved ticket with 'not yet open' status for keyword matching")

                # Filter tickets without input field, EXCEPT "not yet open" tickets
                if len(row_text) > 0 and row_input is None:
                    if not has_not_yet_open_status:
                        row_text = ""
                        debug.log(f"  -> Filtered: no input field and not 'not yet open'")
                    else:
                        debug.log(f"  -> Kept 'not yet open' ticket for keyword matching (no input yet)")

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
                    tmp_ticket_count = ""
                    if ' danger' in row_html and '剩' in row_text and '張' in row_text:
                        tmp_array = row_html.split('剩')
                        tmp_array = tmp_array[1].split('張')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[0].strip()
                            if tmp_ticket_count.isdigit():
                                ticket_count = int(tmp_ticket_count)
                                debug.log("found ticket 剩:", tmp_ticket_count)
                    # for ja.
                    if ' danger' in row_html and '残り' in row_text and '枚' in row_text:
                        tmp_array = row_html.split('残り')
                        tmp_array = tmp_array[1].split('枚')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[0].strip()
                            if tmp_ticket_count.isdigit():
                                ticket_count = int(tmp_ticket_count)
                                debug.log("found ticket 残り:", tmp_ticket_count)
                    # for en.
                    if ' danger' in row_html and ' Left ' in row_html:
                        tmp_array = row_html.split(' Left ')
                        tmp_array = tmp_array[0].split('>')
                        if len(tmp_array) > 0:
                            tmp_ticket_count = tmp_array[len(tmp_array)-1].strip()
                            if tmp_ticket_count.isdigit():
                                debug.log("found ticket left:", tmp_ticket_count)
                                ticket_count = int(tmp_ticket_count)

                    if ticket_count < ticket_number:
                        # skip this row, due to no ticket remaining.
                        debug.log("found ticket left:", tmp_ticket_count, ",but target ticket:", ticket_number)
                        row_text = ""

            # Keyword matching for ALL preserved tickets (including "not yet open")
            # This is the key improvement: match keywords regardless of input field status
            if len(row_text) > 0:
                # Check if already assigned
                if len(current_ticket_number) > 0 and current_ticket_number != "0":
                    is_ticket_number_assigned = True
                    break

                # Perform keyword matching
                is_match_area = False
                if len(kktix_area_keyword_array) == 0:
                    # No keyword specified, match all
                    is_match_area = True
                else:
                    # Check if all keywords match (AND logic)
                    is_match_area = all(kw in row_text for kw in kktix_area_keyword_array)

                # Handle matched tickets based on input field availability
                if is_match_area:
                    if row_input is not None:
                        # Has input field (purchasable) - add to selection list
                        areas.append(row_input)
                        debug.log(f"[KKTIX AREA] Matched ticket: {original_text[:80]}")

                        # From top to bottom mode: match first then break
                        if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                            break
                    else:
                        # No input field (not yet open) - track as pending
                        pending_tickets.append({
                            'index': i,
                            'text': original_text[:60],
                            'keywords': kktix_area_keyword_array
                        })
                        debug.log(f"[KKTIX AREA] Matched ticket is waiting to open: {original_text[:80]}")

            if not is_dom_ready:
                # DOM not ready, break the loop
                break
    else:
        debug.log("[KKTIX] No price list found")
        pass

    # Keep area diagnostics concise. Detailed row logs already show the reason
    # for each candidate; repeated summary counters make refresh loops noisy.
    if debug.enabled:
        total_matched_with_input = len(areas) if areas else 0
        total_matched_pending = len(pending_tickets) if pending_tickets else 0
        total_matched_all = total_matched_with_input + total_matched_pending

        if total_matched_pending > 0:
            debug.log(f"[KKTIX AREA] Waiting for matched tickets to open:")
            for pending in pending_tickets[:5]:  # Show max 5 pending tickets
                keywords_str = ', '.join(pending['keywords'])
                debug.log(f"[KKTIX AREA]   - {pending['text']} (keywords: {keywords_str})")
            if total_matched_pending > 5:
                debug.log(f"[KKTIX AREA]   ... and {total_matched_pending - 5} more")
        elif total_matched_all == 0:
            debug.log(f"[KKTIX AREA] No ticket types matched")

    # Check pause after traversal
    if await check_and_handle_pause(config_dict):
        return True, False, None

    return is_dom_ready, is_ticket_number_assigned, areas

async def nodriver_kktix_assign_ticket_number(tab, config_dict, kktix_area_keyword):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return True, False, False

    debug = util.create_debug_logger(config_dict)

    ticket_number_str = str(config_dict["ticket_number"])
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    # Track selection type: empty keyword means fallback selection
    is_fallback_selection = (kktix_area_keyword == "")

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
                debug.log("matched_blocks is empty, is_need_refresh")

    if not target_area is None:
        current_ticket_number = ""

        try:
            # target_area 現在是索引，直接使用
            target_index = target_area

            # 使用 JavaScript 操作，避免使用元素物件方法
            assign_result = await tab.evaluate(f'''
                (function() {{
                    // 舊版優先
                    let inputs = document.querySelectorAll('div.display-table-row input');
                    // 若舊版找不到，使用新版選擇器
                    if (inputs.length === 0) {{
                        inputs = document.querySelectorAll('div.ticket-item input.number-step-input-core');
                    }}
                    const targetInput = inputs[{target_index}];

                    if (!targetInput) {{
                        return {{ success: false, error: "Input not found", inputCount: inputs.length, targetIndex: {target_index} }};
                    }}

                    // 取得對應的票種名稱，清理多餘空白
                    // 舊版優先使用 display-table-row，新版使用 ticket-item
                    let parentRow = targetInput.closest('div.display-table-row');
                    if (!parentRow) {{
                        parentRow = targetInput.closest('div.ticket-item');
                    }}
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

                    # T013 equivalent: Log selected area with selection type
                    selection_type = "fallback" if is_fallback_selection else "keyword match"
                    debug.log(f"[KKTIX AREA SELECT] Selected ticket: {clean_ticket_name} ({selection_type})")
                    debug.log("[KKTIX AREA SELECT] assign ticket number:%s to [%s]" % (ticket_number_str, clean_ticket_name))
                    is_ticket_number_assigned = True
                elif assign_result.get('alreadySet'):
                    debug.log("value already assigned to [%s]" % ticket_name)
                    is_ticket_number_assigned = True

                debug.log(f"[TICKET] current_ticket_number: {current_ticket_number}")
                debug.log(f"[TICKET] selected_ticket_name: {ticket_name}")

                if is_ticket_number_assigned:
                    debug.log("KKTIX ticket number input completed, skipping verification")
            else:
                if debug.enabled:
                    error_msg = assign_result.get('error', 'Unknown error') if assign_result else 'No result'
                    debug.log(f"Error in nodriver_kktix_assign_ticket_number: {error_msg}")

        except Exception as exc:
            debug.log(f"Error in nodriver_kktix_assign_ticket_number: {exc}")

    # 票數分配後檢查暫停
    if await check_and_handle_pause(config_dict):
        return True, False, False

    return is_dom_ready, is_ticket_number_assigned, is_need_refresh

async def nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div):
    """增強版驗證碼處理，包含重試機制和人類化延遲"""
    debug = util.create_debug_logger(config_dict)

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
                    answer_list = util.get_answer_list_from_question_string(None, question_text, config_dict)

            inferred_answer_string = ""
            for answer_item in answer_list:
                if not answer_item in fail_list:
                    inferred_answer_string = answer_item
                    break

            if len(answer_list) > 0:
                answer_list = list(dict.fromkeys(answer_list))

            debug.log("inferred_answer_string:", inferred_answer_string)
            debug.log("question_text:", question_text)
            debug.log("answer_list:", answer_list)
            debug.log("fail_list:", fail_list)

            # 增強版答案填寫流程，包含重試機制
            if len(inferred_answer_string) > 0 and elements_check.get('hasInput'):
                success = False
                max_retries = 3

                for retry_count in range(max_retries):
                    if retry_count > 0:
                        debug.log(f"Captcha filling retry {retry_count}/{max_retries}")

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
                            debug.log(f"Captcha answer filled successfully: {inferred_answer_string}")

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
                                debug.log("Button click failed, retrying...")
                        else:
                            error_msg = fill_result.get('error', 'Unknown error') if fill_result else 'No result'
                            debug.log(f"Input filling failed: {error_msg}")

                    except Exception as exc:
                        debug.log(f"Captcha retry {retry_count + 1} failed: {exc}")

                    # 重試前的等待
                    if not success and retry_count < max_retries - 1:
                        retry_delay = random.uniform(0.8, 1.5)
                        await tab.sleep(retry_delay)

                if not success:
                    debug.log("All captcha filling attempts failed")

    return fail_list, is_question_popup, success

async def debug_kktix_page_state(tab, show_debug=True):
    """收集 KKTIX 頁面狀態供除錯，參考 NoDriver API 指南"""
    debug = util.create_debug_logger(enabled=show_debug)
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
                            !!document.querySelector('.alert-danger, .error')?.innerText?.includes('Sold Out') ||
                            !!document.querySelector('.sold-out, .unavailable'),
                    notYetOpen: !!document.querySelector('.alert-danger, .error')?.innerText?.includes('未開賣') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('尚未開賣') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('尚未開始') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('即將開賣') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('Not Started') ||
                               !!document.querySelector('.alert-danger, .error')?.innerText?.includes('まだ発売')
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

        if state:
            debug.log("=== KKTIX Page Debug State ===")
            debug.log(f"URL: {state.get('basic', {}).get('url', 'N/A')}")
            debug.log(f"Ready State: {state.get('basic', {}).get('readyState', 'N/A')}")
            debug.log(f"Registration Div: {state.get('kktix', {}).get('hasRegistrationDiv', False)}")
            debug.log(f"Ticket Areas: {state.get('kktix', {}).get('hasTicketAreas', 0)}")
            debug.log(f"Captcha Question: {state.get('captcha', {}).get('hasQuestion', False)}")
            if state.get('captcha', {}).get('questionText'):
                debug.log(f"Question Text: {state.get('captcha', {}).get('questionText', '')[:50]}...")
            debug.log(f"Next Buttons: {state.get('forms', {}).get('nextButtons', 0)}")
            debug.log(f"Error Messages: {state.get('errors', {}).get('hasErrorMessages', False)}")
            if state.get('errors', {}).get('soldOut'):
                debug.log("[SOLD OUT] Sold Out detected")
            if state.get('errors', {}).get('notYetOpen'):
                debug.log("Not yet open detected")
            debug.log("=" * 30)

        return state

    except Exception as exc:
        error_state = {
            'success': False,
            'error': f'Exception in debug_kktix_page_state: {exc}',
            'timestamp': datetime.now().isoformat()
        }
        debug.log(f"Debug failed: {exc}")
        return error_state

async def nodriver_kktix_date_auto_select(tab, config_dict):
    """KKTIX multi-session date selection with keyword matching"""
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    # T003: Check main switch (defensive programming)
    if not config_dict["date_auto_select"]["enable"]:
        debug.log("[KKTIX DATE SELECT] Main switch is disabled, skipping date selection")
        return False

    # Read config
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)  # T017: Safe access for new field (default: strict mode)

    # Check if multi-session page exists with smart polling
    session_list = None
    max_wait = 5
    check_interval = 0.3
    max_attempts = int(max_wait / check_interval)

    for attempt in range(max_attempts):
        try:
            session_list = await tab.query_selector_all('div.event-list ul.clearfix > li')
            if session_list and len(session_list) > 0:
                debug.log(f"[KKTIX DATE] Found {len(session_list)} sessions after {attempt * check_interval:.1f}s")
                break
        except Exception as exc:
            if attempt == max_attempts - 1:
                debug.log(f"[KKTIX DATE] Error querying session list: {exc}")

        # Early exit: single-session page has no event-list but has a direct buy button
        if attempt == 0:
            try:
                event_list_container = await tab.query_selector('div.event-list')
                if not event_list_container:
                    direct_button = await tab.query_selector('.tickets > a.btn-point')
                    if direct_button:
                        debug.log("[KKTIX DATE] Single-session page detected (no event-list, direct button found), skipping date select")
                        return False
            except Exception:
                pass

        if attempt < max_attempts - 1:
            await tab.sleep(check_interval)

    if not session_list or len(session_list) == 0:
        debug.log(f"[KKTIX DATE] Timeout after {max_wait}s waiting for session list")
        return False

    debug.log(f"[KKTIX DATE] Found {len(session_list)} sessions on page")

    # Extract session info (text + button element)
    formated_session_list = []
    formated_session_list_text = []

    for session_item in session_list:
        try:
            # Get session date text
            date_text = None
            try:
                # Priority 1: span.timezoneSuffix
                date_elem = await session_item.query_selector('span.timezoneSuffix')
                if date_elem:
                    date_text = await date_elem.get_html()
                    date_text = util.remove_html_tags(date_text).strip()
            except:
                pass

            if not date_text:
                try:
                    # Fallback: .event-info > a > p
                    date_elem = await session_item.query_selector('.event-info > a > p')
                    if date_elem:
                        date_text = await date_elem.get_html()
                        date_text = util.remove_html_tags(date_text).strip()
                except:
                    pass

            # Check if button exists
            button_elem = await session_item.query_selector('div.content > a.btn-point')

            if date_text and button_elem:
                # Check exclude keywords
                if not util.reset_row_text_if_match_keyword_exclude(config_dict, date_text):
                    formated_session_list.append(button_elem)
                    formated_session_list_text.append(date_text)
                    debug.log(f"[KKTIX DATE] Available session: {date_text}")
        except Exception as exc:
            debug.log(f"[KKTIX DATE] Error processing session: {exc}")
            continue

    if len(formated_session_list) == 0:
        debug.log("[KKTIX DATE] No available sessions found after filtering")
        return False

    # T004-T008: NEW LOGIC - Early return pattern (Feature 003)
    # Keyword priority matching: first match wins and stops immediately
    matched_blocks = None

    if not date_keyword:
        matched_blocks = formated_session_list
        debug.log(f"[KKTIX DATE KEYWORD] No keyword specified, using all {len(formated_session_list)} sessions")
    else:
        # NEW: Early return pattern - iterate keywords in order
        matched_blocks = []
        target_row_found = False
        keyword_matched_index = -1

        try:
            import json
            import re
            keyword_array = json.loads("[" + date_keyword + "]")

            # T005: Start checking keywords log
            debug.log(f"[KKTIX DATE KEYWORD] Start checking keywords in order: {keyword_array}")
            debug.log(f"[KKTIX DATE KEYWORD] Total keyword groups: {len(keyword_array)}")
            debug.log(f"[KKTIX DATE KEYWORD] Checking against {len(formated_session_list_text)} available sessions...")

            # NEW: Iterate keywords in priority order (early return)
            for keyword_index, keyword_item_set in enumerate(keyword_array):
                debug.log(f"[KKTIX DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

                # Check all rows for this keyword
                for i, session_text in enumerate(formated_session_list_text):
                    normalized_session_text = re.sub(r'\s+', ' ', session_text)
                    is_match = False

                    if isinstance(keyword_item_set, str):
                        # OR logic: single keyword
                        normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
                        is_match = normalized_keyword in normalized_session_text
                    elif isinstance(keyword_item_set, list):
                        # AND logic: all keywords must match
                        normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
                        match_results = [kw in normalized_session_text for kw in normalized_keywords]
                        is_match = all(match_results)

                    if is_match:
                        # T006: Keyword matched log - IMMEDIATELY select and stop
                        matched_blocks = [formated_session_list[i]]
                        target_row_found = True
                        keyword_matched_index = keyword_index
                        debug.log(f"[KKTIX DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                        debug.log(f"[KKTIX DATE SELECT] Selected session: {session_text[:80]} (keyword match)")
                        break

                if target_row_found:
                    # EARLY RETURN: Stop checking further keywords
                    break

            # T007: All keywords failed log
            if not target_row_found:
                debug.log(f"[KKTIX DATE KEYWORD] All keywords failed to match")

        except Exception as e:
            debug.log(f"[KKTIX DATE KEYWORD] Parsing error: {e}")
            # On error, use mode selection
            matched_blocks = []

    if debug.enabled and (not matched_blocks or len(matched_blocks) == 0):
        debug.log(f"[KKTIX DATE KEYWORD] No sessions matched any keywords")

    # T018-T020: NEW - Conditional fallback based on date_auto_fallback switch
    if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and len(formated_session_list) > 0:
        if date_auto_fallback:
            # T018: Fallback enabled - use auto_select_mode
            debug.log(f"[KKTIX DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            debug.log(f"[KKTIX DATE FALLBACK] Selecting available session based on date_select_order='{auto_select_mode}'")
            matched_blocks = formated_session_list
        else:
            # T019: Fallback disabled - strict mode (no selection, but continue to check for reload)
            debug.log(f"[KKTIX DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            debug.log(f"[KKTIX DATE SELECT] No date selected, will check if reload needed")
            # Don't return - let the function continue to check if selection succeeded
            # matched_blocks remains empty (no selection will be made)

    # Select target using auto_select_mode
    target_button = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    if debug.enabled:
        if not matched_blocks or len(matched_blocks) == 0:
            debug.log(f"[KKTIX DATE SELECT] No target selected (matched_blocks is empty)")

    # Click selected button
    is_date_clicked = False
    if target_button:
        try:
            debug.log("[KKTIX DATE SELECT] Clicking selected session button...")
            await target_button.click()
            is_date_clicked = True
            debug.log(f"[KKTIX DATE SELECT] Session selection completed successfully")
        except Exception as exc:
            debug.log(f"[KKTIX DATE SELECT] Click error: {exc}")

    return is_date_clicked

#   : This is for case-2 next button.
async def nodriver_kktix_events_press_next_button(tab, config_dict=None):
    """點擊活動頁面的「立即購票」按鈕"""
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
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
        debug.log(f"[KKTIX] Error clicking events next button: {exc}")
        return False

async def nodriver_kktix_check_guest_modal(tab, config_dict, force_check=False):
    """
    Check and handle KKTIX guest modal (立刻成為 KKTIX 會員)
    Reference: .temp/kktix/kktix-qa-code.html Line 157-172
    Modal appears when user is not logged in on /registrations/new page
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_modal_handled = False

    # Track if we've already checked for guest modal (skip wait on subsequent checks)
    is_first_check = not _state.get("guest_modal_checked", False) if _state else True
    current_time = time.time()
    if _state and not force_check and not is_first_check:
        last_check_time = _state.get("guest_modal_last_check_time", 0)
        if current_time - last_check_time < 3:
            return False
    if _state:
        _state["guest_modal_last_check_time"] = current_time

    try:
        # Only wait on first check (modal typically appears on initial page load)
        if is_first_check:
            await asyncio.sleep(random.uniform(0.3, 0.5))
            if _state:
                _state["guest_modal_checked"] = True

        # Check if guest modal exists and is visible
        modal_state = await tab.evaluate('''
            (function() {
                const modal = document.querySelector('#guestModal');
                if (!modal) {
                    return { status: 'missing' };
                }
                const style = window.getComputedStyle(modal);
                const isVisible = style.display !== 'none' &&
                                style.visibility !== 'hidden' &&
                                parseFloat(style.opacity) > 0;
                return {
                    status: isVisible ? 'visible' : 'hidden',
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity
                };
            })()
        ''')
        modal_state = util.parse_nodriver_result(modal_state)
        modal_status = modal_state.get('status', 'missing') if isinstance(modal_state, dict) else 'missing'

        if modal_status == 'visible':
            debug.log("[KKTIX GUEST MODAL] Guest modal detected, clicking dismiss button...")

            # Click the dismiss button (暫時不要)
            click_result = await tab.evaluate('''
                (function() {
                    const dismissBtn = document.querySelector('#guestModal button[data-dismiss="modal"]');
                    if (dismissBtn) {
                        dismissBtn.click();
                        return { success: true, clicked: true };
                    }
                    return { success: false, error: 'Dismiss button not found' };
                })()
            ''')

            # Parse result using utility function
            click_result = util.parse_nodriver_result(click_result)

            if click_result and click_result.get('clicked'):
                debug.log("[KKTIX GUEST MODAL] Successfully dismissed guest modal")
                # Wait for modal to close
                await asyncio.sleep(random.uniform(0.3, 0.5))
                is_modal_handled = True
        else:
            if debug.enabled and _state and not _state.get("guest_modal_status_logged", False):
                _state["guest_modal_status_logged"] = True
                if modal_status == 'hidden':
                    debug.log("[KKTIX GUEST MODAL] Guest modal exists but is hidden")
                else:
                    debug.log("[KKTIX GUEST MODAL] Guest modal not present")

    except Exception as exc:
        debug.log(f"[ERROR] Guest modal check failed: {exc}")

    return is_modal_handled


async def nodriver_kktix_dismiss_failure_modal(tab, config_dict):
    """Detect and dismiss KKTIX Bootstrap modals that signal sold-out or race-condition failure.

    Covers messages like "別人搶先一步" and "已無可配座位" which appear as
    DOM modals (not native JS alerts) and are not caught by the CDP alert handler.

    Returns:
        True  -- failure modal detected and dismissed
        False -- no failure modal found (or evaluate failed)
    """
    debug = util.create_debug_logger(config_dict)
    try:
        result = await tab.evaluate('''
            (function() {
                const failureTexts = [
                    '已售完', '售完', '別人搶先一步', '已無可配座位',
                    '無可配座位', '已被購買', '購票失敗', '失敗', '錯誤'
                ];
                const buttonTexts = ['確定', 'OK', 'Ok', '知道了', '我知道了', 'close', 'Close'];
                const modals = document.querySelectorAll('.modal.in, .modal.show');
                for (const modal of modals) {
                    const text = (modal.textContent || '').trim();
                    if (!failureTexts.some(t => text.includes(t))) continue;
                    const buttons = modal.querySelectorAll('button, a.btn');
                    for (const btn of buttons) {
                        const btnText = (btn.textContent || '').trim();
                        const dismiss = btn.getAttribute('data-dismiss');
                        if (buttonTexts.some(t => btnText.includes(t)) || dismiss === 'modal') {
                            btn.click();
                            return { found: true, clicked: true, text: text.slice(0, 80) };
                        }
                    }
                    return { found: true, clicked: false, text: text.slice(0, 80) };
                }
                return { found: false, clicked: false, text: '' };
            })()
        ''')
        if isinstance(result, dict) and result.get('found'):
            debug.log(f"[KKTIX MODAL] Failure modal: {result.get('text', '')}")
            if result.get('clicked'):
                debug.log("[KKTIX MODAL] Dismissed via button click")
                return True
            debug.log("[KKTIX MODAL] Could not find dismiss button, signaling reload")
            return True
    except Exception as exc:
        debug.log(f"[KKTIX MODAL] Error checking failure modal: {exc}")
    return False


# Single source of truth for "what state is the registration form in?".
#
# Everything that used to answer this question did so with its own inline JS,
# and the copies disagreed: one treated multiple member-code fields as OR while
# another used AND, one honoured `disabled` on legacy ticket inputs while
# another ignored it. Filling the form could therefore satisfy the outer guard
# (skip the whole ticket flow) while failing the inner check (do not press
# next) at the same time, which is the deadlock behind #377 / #375.
#
# Scope matters too: div.code-input is rendered per .ticket-unit and gated on
# `ticketModel.quantity > 0`, so a document-wide query misattributes it on
# multi-ticket pages. Resolve the active unit first, fall back to document for
# legacy layouts.
CONST_KKTIX_FORM_STATE_JS = '''
    (function() {
        const QTY_CSS = 'input[ng-model="ticketModel.quantity"]';
        const LEGACY_QTY_CSS = 'input[name^="tickets"]';

        const readQuantity = (root) => {
            for (const sel of [QTY_CSS, LEGACY_QTY_CSS]) {
                const inputs = root.querySelectorAll(sel);
                for (const input of inputs) {
                    const value = parseInt(input.value);
                    if (!input.disabled && !isNaN(value) && value > 0) {
                        return value;
                    }
                }
            }
            return 0;
        };

        let scope = null;
        let scopeKind = 'none';
        const units = document.querySelectorAll('.ticket-unit');
        for (const unit of units) {
            if (readQuantity(unit) > 0) {
                scope = unit;
                scopeKind = 'ticket-unit';
                break;
            }
        }
        if (!scope) {
            scope = document;
            scopeKind = 'document';
        }

        const ticketCount = readQuantity(scope);
        const hasTicket = ticketCount > 0;

        // The terms checkbox lives outside the ticket unit, so always look it
        // up document-wide. Absent checkbox means the event has no terms step.
        const agreeCheckbox = document.querySelector('#person_agree_terms');
        const agreed = agreeCheckbox ? agreeCheckbox.checked : true;

        const qualification = {
            status: 'missing',
            label: '',
            selectedIndex: -1,
            options: [],
            invitationPending: false
        };

        const block = scope.querySelector('div.code-input');
        if (block) {
            const labelEl = block.querySelector('label.control-label');
            qualification.label = labelEl ? (labelEl.innerText || '').trim() : '';

            // Index by radio position inside the block so the click helper can
            // address the exact same element without re-deriving the mapping.
            const radios = block.querySelectorAll('input[type="radio"]');
            radios.forEach((radio, idx) => {
                const optionLabel = radio.closest('label');
                const codeInput = optionLabel
                    ? optionLabel.querySelector('input.member-code')
                    : null;
                const joinedLink = optionLabel
                    ? optionLabel.querySelector('span[ng-if] > a[ng-href="#"]')
                    : null;

                let optionType = 'plain';
                if (codeInput) {
                    optionType = 'member_code';
                } else if (joinedLink) {
                    optionType = 'joined';
                }

                if (radio.checked) {
                    qualification.selectedIndex = idx;
                }

                qualification.options.push({
                    index: idx,
                    type: optionType,
                    disabled: !!radio.disabled,
                    checked: !!radio.checked,
                    codeDisabled: codeInput ? !!codeInput.disabled : null,
                    codeFilled: codeInput
                        ? !!(codeInput.value && codeInput.value.trim() !== '')
                        : null
                });
            });

            // An invitation-code qualification renders outside the radio repeat
            // (ng-if="oq.type != 'invitation_code'" excludes it). No verified
            // snapshot exists, so only flag it - never guess at its selectors.
            const textInputs = block.querySelectorAll('input[type="text"]');
            for (const input of textInputs) {
                if (!input.classList.contains('member-code')) {
                    qualification.invitationPending = true;
                    break;
                }
            }

            if (qualification.options.length === 0) {
                // No radios: either a plain description label, or an
                // invitation-style input we deliberately do not automate.
                qualification.status = qualification.invitationPending
                    ? 'pending'
                    : 'missing';
            } else if (qualification.options.some((o) => o.type === 'joined')) {
                qualification.status = 'satisfied';
            } else if (qualification.selectedIndex >= 0) {
                const selected = qualification.options.find(
                    (o) => o.index === qualification.selectedIndex
                );
                if (!selected || selected.type !== 'member_code') {
                    qualification.status = 'satisfied';
                } else {
                    qualification.status = selected.codeFilled ? 'satisfied' : 'pending';
                }
            } else {
                qualification.status = 'pending';
            }
        }

        return {
            scope: scopeKind,
            hasTicket: hasTicket,
            ticketCount: ticketCount,
            agreed: agreed,
            qualification: qualification,
            ready: hasTicket && agreed && qualification.status !== 'pending'
        };
    })()
'''


def _kktix_default_form_state():
    """Conservative fallback: let the flow move forward rather than stall.

    A detection failure must never invent a blocking state - that is how the
    old guard turned a transient misread into a permanent deadlock.
    """
    return {
        "scope": "none",
        "hasTicket": False,
        "ticketCount": 0,
        "agreed": True,
        "qualification": {
            "status": "missing",
            "label": "",
            "selectedIndex": -1,
            "options": [],
            "invitationPending": False,
        },
        "ready": False,
    }


async def nodriver_kktix_check_form_state(tab, config_dict):
    """Read the whole registration form state in one round trip."""
    debug = util.create_debug_logger(config_dict)
    try:
        result = await tab.evaluate(CONST_KKTIX_FORM_STATE_JS)
        state = util.parse_nodriver_result(result)
        if isinstance(state, dict) and "qualification" in state:
            return state
        debug.log(f"[KKTIX FORM STATE] Unexpected result type "
                  f"{type(state).__name__}, using conservative default")
    except Exception as exc:
        debug.log(f"[KKTIX FORM STATE] Read failed: {exc}")
    return _kktix_default_form_state()


async def nodriver_kktix_check_qualification(tab, config_dict):
    """Purchase-qualification subset of the form state.

    Returns a dict with 'status' in {'missing', 'satisfied', 'pending'}.
    """
    state = await nodriver_kktix_check_form_state(tab, config_dict)
    return state.get("qualification", _kktix_default_form_state()["qualification"])


async def nodriver_kktix_check_form_ready(tab, config_dict):
    """True when tickets are set, terms agreed, and qualification not pending."""
    state = await nodriver_kktix_check_form_state(tab, config_dict)
    return bool(state.get("ready", False))


async def nodriver_kktix_wait_member_code_enabled(tab, config_dict, timeout=1.2):
    """Poll until a member-code input is typable after selecting its radio.

    ng-disabled resolves on the next digest cycle, so a fixed sleep either wastes
    time or fires early under load. Returns False on timeout; the caller just
    retries next round rather than treating it as fatal.
    """
    debug = util.create_debug_logger(config_dict)
    interval = 0.05
    attempts = int(timeout / interval)
    for _ in range(attempts):
        try:
            is_enabled = await tab.evaluate(
                "!!document.querySelector('div.code-input input.member-code:not([disabled])')"
            )
            if is_enabled:
                return True
        except Exception:
            pass
        await asyncio.sleep(interval)
    debug.log(f"[KKTIX QUALIFICATION] member-code still disabled after {timeout}s, "
              "angular digest may be stalled")
    return False


async def nodriver_kktix_select_qualification(tab, config_dict, qualification):
    """Select the first available purchase-qualification radio.

    Picks the first option that is neither disabled nor already checked. There
    is deliberately no keyword setting for this: the qualification list is
    event-specific and short, and a wrong stored keyword would silently block
    every purchase.

    Returns:
        bool: True if a radio was clicked this round.
    """
    debug = util.create_debug_logger(config_dict)

    if qualification.get("status") != "pending":
        return False

    if qualification.get("invitationPending"):
        debug.log("[KKTIX QUALIFICATION] Invitation-code style input detected; "
                  "this variant is not automated, please fill it manually")
        return False

    options = qualification.get("options", [])
    target_index = -1
    for option in options:
        if not option.get("disabled") and not option.get("checked"):
            target_index = option.get("index", -1)
            break

    if target_index < 0:
        debug.log(f"[KKTIX QUALIFICATION] No selectable option among "
                  f"{len(options)} (all disabled or already selected)")
        return False

    # Native clicks do not drive AngularJS radios under zendriver, so go
    # through JS and let ng-model see the change.
    click_result = await tab.evaluate(f'''
        (function() {{
            const block = document.querySelector('div.code-input');
            if (!block) {{ return {{ clicked: false, reason: 'no-block' }}; }}
            const radios = block.querySelectorAll('input[type="radio"]');
            const radio = radios[{json.dumps(target_index)}];
            if (!radio) {{ return {{ clicked: false, reason: 'index-out-of-range' }}; }}
            if (radio.disabled) {{ return {{ clicked: false, reason: 'disabled' }}; }}
            radio.click();
            return {{ clicked: true, reason: '' }};
        }})()
    ''')
    click_result = util.parse_nodriver_result(click_result)

    if not (isinstance(click_result, dict) and click_result.get('clicked')):
        reason = click_result.get('reason', 'unknown') if isinstance(click_result, dict) else 'unknown'
        debug.log(f"[KKTIX QUALIFICATION] Radio click failed at index {target_index}: {reason}")
        return False

    debug.log(f"[KKTIX QUALIFICATION] Selected option {target_index}")

    selected = next((o for o in options if o.get("index") == target_index), None)
    if selected and selected.get("type") == "member_code":
        await nodriver_kktix_wait_member_code_enabled(tab, config_dict)

    return True


async def nodriver_kktix_handle_qualification_and_next(tab, config_dict,
                                                       button_clicked_in_captcha=False):
    """Satisfy any purchase qualification, then press next (#377 / #375).

    Replaces the old branch that decided whether to act by asking whether a text
    input existed. On a member_code qualification both a radio and a text input
    are present, so that branch never ran and the flow stalled with everything
    filled in but "next" never pressed.

    Returns:
        bool: True if the next button was pressed this round.
    """
    debug = util.create_debug_logger(config_dict)

    qualification = await nodriver_kktix_check_qualification(tab, config_dict)

    if qualification.get("status") == "pending":
        if await nodriver_kktix_select_qualification(tab, config_dict, qualification):
            # The code field belongs to the option just selected, so fill it
            # only now - filling it earlier targeted the wrong (or no) option.
            await nodriver_kktix_order_member_code(tab, config_dict)
            qualification = await nodriver_kktix_check_qualification(tab, config_dict)

    if qualification.get("status") == "pending":
        debug.log(f"[KKTIX QUALIFICATION] Still pending "
                  f"(label={qualification.get('label', '')!r}), not pressing next")
        return False

    if button_clicked_in_captcha:
        debug.log("Button already clicked during captcha processing, skipping duplicate click")
        return False

    if not config_dict["kktix"].get("auto_press_next_step_button", True):
        debug.log("[KKTIX] auto_press_next_step_button is off, leaving the form for the user")
        return False

    try:
        current_url = await tab.evaluate('window.location.href')
        if current_url and '/registrations/' in current_url and '-' in current_url \
                and '/new' not in current_url:
            debug.log("Already redirected to order page, skipping button click")
            return False
    except Exception as exc:
        debug.log(f"[KKTIX] URL check before next click failed: {exc}")
        current_url = ""

    pressed = await nodriver_kktix_press_next_button(tab, config_dict)
    if pressed:
        # Feeds the cooldown guard so the next loop does not re-run the whole
        # ticket flow while this submission is still in flight.
        _state["next_button_pressed_url"] = current_url
        _state["next_button_pressed_time"] = time.time()
    return pressed


async def nodriver_kktix_press_next_button(tab, config_dict=None):
    """使用 JavaScript 點擊下一步按鈕，包含重試和等待機制"""
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    # 重試機制：最多嘗試 3 次
    for retry_count in range(3):
        try:
            # 如果不是第一次嘗試，等待一下
            if retry_count > 0:
                await asyncio.sleep(0.5)
                debug.log(f"KKTIX 按鈕點擊重試 {retry_count + 1}/3")

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
                    debug.log(f"KKTIX processing: [{button_text}]")

                    # 等待較長時間給 KKTIX 處理
                    await asyncio.sleep(1.5)

                    # 主動檢查並關閉 alert（備援機制）
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        debug.log("[KKTIX] Alert dismissed after processing")
                    except:
                        pass  # 沒有 alert 就忽略

                    try:
                        # 檢查是否已跳轉到訂單頁面
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            debug.log(f"Processing completed, redirected to order page")
                            return True
                    except Exception:
                        pass

                    # 如果還沒跳轉，可能還在處理，返回成功
                    return True
                else:
                    # 正常的按鈕點擊成功
                    debug.log(f"KKTIX button click successful: [{button_text}]")

                    # 等待頁面處理並檢查是否跳轉
                    await asyncio.sleep(0.3)  # 給 KKTIX 伺服器時間處理

                    # 主動檢查並關閉 alert（備援機制，避免 CDP event handler 未觸發）
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        debug.log("[KKTIX] Alert dismissed after button click")
                    except:
                        pass  # 沒有 alert 就忽略

                    try:
                        # 檢查是否已跳轉到訂單頁面
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            debug.log(f"Button click completed, redirected to order page")
                            return True
                    except Exception:
                        pass

                    # 如果沒有跳轉，等待原有時間並返回成功
                    await asyncio.sleep(0.2)
                    return True
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                button_text = result.get('buttonText', '') if result else ''
                debug.log(f"KKTIX button click failed: {error_msg} [{button_text}]")

                # 如果是按鈕被禁用或處理中，檢查是否已跳轉
                if 'disabled' in error_msg.lower() or 'processing' in error_msg.lower():
                    try:
                        current_url = await tab.evaluate('window.location.href')
                        if '/registrations/' in current_url and '-' in current_url and '/new' not in current_url:
                            debug.log(f"System processing but already redirected to order page, considered successful")
                            return True
                    except Exception:
                        pass

                    # 如果是處理中狀態，等待較長時間再重試
                    if 'processing' in error_msg.lower():
                        await asyncio.sleep(1.0)

                    # 繼續重試
                    continue

        except Exception as exc:
            debug.log(f"KKTIX 按鈕點擊例外 (重試 {retry_count + 1}/3): {exc}")

    # 所有重試都失敗
    debug.log("KKTIX button click finally failed after 3 retries")
    return False

async def nodriver_kktix_check_ticket_page_status(tab, config_dict=None):
    """
    Check KKTIX ticket page status
    Improved: Distinguish "all not yet open" vs "partially not yet open", with multi-language support

    Improvements:
    - Check each ticket unit status instead of entire page HTML
    - Only reload if "all tickets sold out" or "all tickets not yet open"
    - Multi-language support: Traditional Chinese, English, Japanese

    Returns:
        bool: True means need to reload page (all tickets sold out or not yet open)
    """
    debug = util.create_debug_logger(config_dict)
    is_need_refresh = False

    try:
        page_state_raw = await tab.evaluate('''
            () => {
                const ticketArea = document.querySelector('#registrationsNewApp') || document.body;

                // Get all ticket units
                const ticketUnits = Array.from(ticketArea.querySelectorAll('.ticket-unit'));

                if (ticketUnits.length === 0) {
                    return { soldOut: false, notYetOpen: false, allNotYetOpen: false, allSoldOut: false };
                }

                // Multi-language "not yet open" keywords
                const notYetOpenKeywords = [
                    '尚未開賣', '未開賣', '尚未開始', '即將開賣',
                    'Not Started', 'not started', 'coming soon', 'Coming Soon',
                    'まだ発売'
                ];

                // Multi-language "sold out" keywords
                const soldOutKeywords = [
                    '售完', '已售完', 'Sold Out', 'sold out', '完売',
                    '暫無票'
                ];

                // Check each ticket status
                let notYetOpenCount = 0;
                let soldOutCount = 0;
                let availableCount = 0;

                ticketUnits.forEach(unit => {
                    const quantitySpan = unit.querySelector('.ticket-quantity');
                    if (quantitySpan) {
                        const text = quantitySpan.textContent.trim();

                        // Check if "not yet open"
                        if (notYetOpenKeywords.some(kw => text.includes(kw))) {
                            notYetOpenCount++;
                        }
                        // Check if "sold out"
                        else if (soldOutKeywords.some(kw => text.includes(kw))) {
                            soldOutCount++;
                        }
                        // Other status treated as available
                        else {
                            availableCount++;
                        }
                    } else {
                        // No quantity span, check if has input (might be purchasable ticket)
                        const hasInput = unit.querySelector('input[type="text"], input[type="number"]');
                        if (hasInput) {
                            availableCount++;
                        }
                    }
                });

                // Determine if need to reload
                const totalTickets = ticketUnits.length;
                const allNotYetOpen = notYetOpenCount === totalTickets && totalTickets > 0;
                const allSoldOut = soldOutCount === totalTickets && totalTickets > 0;
                const hasNotYetOpen = notYetOpenCount > 0;
                const hasSoldOut = soldOutCount > 0;

                return {
                    soldOut: hasSoldOut,
                    allSoldOut: allSoldOut,
                    notYetOpen: hasNotYetOpen,
                    allNotYetOpen: allNotYetOpen,
                    availableCount: availableCount,
                    stats: {
                        total: totalTickets,
                        notYetOpen: notYetOpenCount,
                        soldOut: soldOutCount,
                        available: availableCount
                    }
                };
            }
        ''')

        # Use unified result parsing function
        page_state = util.parse_nodriver_result(page_state_raw)

        # Only reload if "all tickets not yet open" or "all tickets sold out"
        if page_state:
            if page_state.get('allNotYetOpen') or page_state.get('allSoldOut'):
                is_need_refresh = True
                if debug.enabled:
                    status = "All Sold Out" if page_state.get('allSoldOut') else "All Not Yet Open"
                    stats = page_state.get('stats', {})
                    debug.log(f"[KKTIX STATUS] {status}, will reload page")
                    debug.log(f"  Ticket stats: total={stats.get('total')}, notYetOpen={stats.get('notYetOpen')}, soldOut={stats.get('soldOut')}, available={stats.get('available')}")
            elif page_state.get('notYetOpen') or page_state.get('soldOut'):
                stats = page_state.get('stats', {})
                debug.log(f"[KKTIX STATUS] Partial tickets not yet open/sold out, continue matching")
                debug.log(f"  Ticket stats: total={stats.get('total')}, notYetOpen={stats.get('notYetOpen')}, soldOut={stats.get('soldOut')}, available={stats.get('available')}")

    except Exception as exc:
        debug.log(f"Check page status failed: {exc}")

    return is_need_refresh

async def nodriver_kktix_reg_new_main(tab, config_dict, fail_list, played_sound_ticket):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return fail_list, played_sound_ticket

    debug = util.create_debug_logger(config_dict)

    # 增加執行計數器，防止無限迴圈
    if _state:
        _state["reg_execution_count"] = _state.get("reg_execution_count", 0) + 1
        debug.log(f"[KKTIX REG] Execution count: {_state['reg_execution_count']}")

    # T010: Check main switch (defensive programming)
    if not config_dict["area_auto_select"]["enable"]:
        debug.log("[KKTIX AREA SELECT] Main switch is disabled, skipping area selection")
        return fail_list, played_sound_ticket

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get('area_auto_fallback', False)  # T021: Safe access for new field (default: strict mode)

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

        # 檢查頁面狀態，如果偵測到售罄或未開賣，設定重新載入標記
        is_need_refresh = await nodriver_kktix_check_ticket_page_status(tab, config_dict)

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
                    debug.log("is_need_refresh for keyword:", area_keyword_item)

            # T022-T024: NEW - Conditional fallback based on area_auto_fallback switch
            if not is_ticket_number_assigned:
                # All keyword groups failed
                if is_need_refresh_final:
                    if area_auto_fallback:
                        # T022: Fallback enabled - use auto_select_mode without keyword
                        debug.log(f"[KKTIX AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
                        debug.log(f"[KKTIX AREA FALLBACK] Selecting available ticket based on area_select_order='{auto_select_mode}'")
                        is_dom_ready, is_ticket_number_assigned, is_need_refresh = await nodriver_kktix_assign_ticket_number(tab, config_dict, "")
                    else:
                        # T023: Fallback disabled - strict mode (no selection, but still reload)
                        debug.log(f"[KKTIX AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
                        debug.log(f"[KKTIX AREA SELECT] No area selected, will reload page and retry")
                        # Don't return - let reload logic execute below
                        # is_ticket_number_assigned remains False (no selection made)
                        # Continue to line 2261 where is_need_refresh check happens
                else:
                    # T024: is_need_refresh_final=False but no ticket assigned (all options sold out or excluded)
                    debug.log(f"[KKTIX AREA FALLBACK] No available options after exclusion")
                    debug.log(f"[KKTIX AREA SELECT] Will reload page and retry")

                # If fallback still failed (or was attempted), then refresh
                if not is_ticket_number_assigned:
                    is_need_refresh = True  # Always reload when no ticket assigned
        else:
            # empty keyword, match all.
            is_dom_ready, is_ticket_number_assigned, is_need_refresh = await nodriver_kktix_assign_ticket_number(tab, config_dict, "")

        if is_dom_ready:
            # part 3: captcha
            if is_ticket_number_assigned:
                # 票數分配後檢查暫停
                if await check_and_handle_pause(config_dict):
                    return fail_list, played_sound_ticket

                # The member code belongs to a qualification option, so it is
                # filled after that option is selected - see
                # nodriver_kktix_handle_qualification_and_next below.
                if await check_and_handle_pause(config_dict):
                    return fail_list, played_sound_ticket

                if not played_sound_ticket:
                    if config_dict["advanced"]["play_sound"]["ticket"]:
                        play_sound_while_ordering(config_dict)
                played_sound_ticket = True

                # 收集除錯資訊（僅在 debug 模式下）

                debug_state = await debug_kktix_page_state(tab, debug.enabled)

                # whole event question.
                fail_list, is_question_popup, button_clicked_in_captcha = await nodriver_kktix_reg_captcha(tab, config_dict, fail_list, registrationsNewApp_div)

                # 驗證碼處理後檢查暫停
                if await check_and_handle_pause(config_dict):
                    return fail_list, played_sound_ticket

                # single option question
                if not is_question_popup:
                    # Check and dismiss guest modal again (in case it appears after captcha)
                    # This ensures modal doesn't block the next button
                    await nodriver_kktix_check_guest_modal(tab, config_dict, force_check=True)

                    # Qualification handling and the next-button press live in
                    # one place now. The old code decided whether to touch the
                    # qualification radio by asking whether a text input existed,
                    # but a member_code qualification has both, so that branch
                    # never ran and control_text was never cleared (#377 / #375).
                    await nodriver_kktix_handle_qualification_and_next(
                        tab, config_dict, button_clicked_in_captcha
                    )
            else:
                # is_ticket_number_assigned is False
                # 檢查票券是否已經在上一次填寫完成
                if not is_need_refresh:
                    # Tickets may already be set from a previous round while
                    # matched_blocks came back empty. Same detector as the main
                    # path, so both agree on what "filled" means.
                    if await nodriver_kktix_check_form_ready(tab, config_dict):
                        debug.log("[KKTIX] Tickets already filled but not assigned this round, "
                                  "attempting to click next button")
                        await nodriver_kktix_handle_qualification_and_next(tab, config_dict)

                if is_need_refresh:
                    # reset to play sound when ticket avaiable.
                    played_sound_ticket = False

                    debug.log("[KKTIX] no match any price, start to refresh page...")

                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])

                    try:
                        await tab.reload()
                    except Exception as exc:
                        pass

    return fail_list, played_sound_ticket

def check_kktix_got_ticket(url, config_dict):
    """檢查是否已成功取得 KKTIX 票券

    Args:
        url: 當前頁面 URL
        config_dict: 設定字典

    Returns:
        bool: True 表示已成功取得票券
    """
    debug = util.create_debug_logger(config_dict)
    is_kktix_got_ticket = False

    if '/events/' in url and '/registrations/' in url and "-" in url:
        if not '/registrations/new' in url:
            if not '#/booking' in url:
                if not 'https://kktix.com/users/sign_in?' in url:
                    is_kktix_got_ticket = True
                    debug.log(f"[KKTIX] Success page detected: {url}")

    if is_kktix_got_ticket:
        if '/events/' in config_dict["homepage"] and '/registrations/' in config_dict["homepage"] and "-" in config_dict["homepage"]:
            if len(url.split('/')) >= 7:
                if len(config_dict["homepage"].split('/')) >= 7:
                    if url.split('/')[4] == config_dict["homepage"].split('/')[4]:
                        # 保留訊息輸出，但不改變返回值
                        # 重複動作保護已由 success_actions_done 標記處理
                        debug.log("重複進入相同活動的訂單頁面，跳過處理")

    return is_kktix_got_ticket

async def nodriver_kktix_main(tab, url, config_dict):
    debug = util.create_debug_logger(config_dict)

    if not _state:
        _state.update({
            "fail_list": [],
            "start_time": None,
            "done_time": None,
            "elapsed_time": None,
            "is_popup_checkout": False,
            "played_sound_ticket": False,
            "played_sound_order": False,
            "got_ticket_detected": False,
            "success_actions_done": False,
            "reg_execution_count": 0,
            "alert_handler_registered": False,
            "alert_needs_reload": False,
            "guest_modal_checked": False,
            "guest_modal_last_check_time": 0,
            "guest_modal_status_logged": False,
            "last_ticket_already_selected_log_value": None,
            "printed_completed": False,
            "last_homepage_redirect_time": 0,
            # Cooldown guard: which page we last submitted, and when.
            "next_button_pressed_url": "",
            "next_button_pressed_time": 0,
        })

    # Global alert handler - auto-dismiss KKTIX sold-out alerts
    async def handle_kktix_alert(event):
        # Skip alert handling when bot is paused (let user handle manually)
        if os.path.exists(util.get_instance_state_path(CONST_MAXBOT_INT28_FILE)):
            return

        debug.log(f"[KKTIX ALERT] Alert detected: '{event.message}'")

        # Dangerous confirmation dialogs should be dismissed (rejected), not accepted
        dangerous_keywords = ["取消", "不保留"]
        is_dangerous = any(kw in event.message for kw in dangerous_keywords)
        should_accept = not is_dangerous

        if is_dangerous:
            debug.log("[KKTIX ALERT] Dangerous dialog detected, will DISMISS")

        # Detect sold-out or error alerts that require page reload
        sold_out_alert_keywords = [
            "售完", "已售完", "售出", "已售出", "全部售出", "已全部售出", "sold out", "Sold Out",
            "別人搶先一步", "已無可配座位", "無可配座位",
            "無票", "目前沒有可以購買的票券", "沒有可以購買的票券", "目前沒有任何可以購買的票券",
            "no ticket", "unavailable",
            "失敗", "錯誤", "error", "fail"
        ]
        is_sold_out_alert = any(kw in event.message.lower() for kw in [k.lower() for k in sold_out_alert_keywords])
        if is_sold_out_alert:
            _state["alert_needs_reload"] = True
            debug.log("[KKTIX ALERT] Sold-out/error alert detected, flagging for reload")

        for attempt in range(3):
            try:
                await tab.send(cdp.page.handle_java_script_dialog(accept=should_accept))
                action = "accepted" if should_accept else "dismissed"
                debug.log(f"[KKTIX ALERT] Alert {action} (attempt {attempt + 1})")
                break
            except Exception as dismiss_exc:
                error_msg = str(dismiss_exc)
                # CDP -32602 means no dialog is showing (already dismissed by another handler or user)
                if "No dialog is showing" in error_msg or "-32602" in error_msg:
                    debug.log("[KKTIX ALERT] Dialog already dismissed")
                    break  # No need to retry
                if attempt < 2:
                    await asyncio.sleep(0.1)
                else:
                    debug.log(f"[KKTIX ALERT] Failed to dismiss alert: {dismiss_exc}")

    # Register global alert handler (only once per session)
    if not _state.get("alert_handler_registered", False):
        try:
            tab.add_handler(cdp.page.JavascriptDialogOpening, handle_kktix_alert)
            _state["alert_handler_registered"] = True
            debug.log("[KKTIX ALERT] Global alert handler registered")
        except Exception as handler_exc:
            debug.log(f"[KKTIX ALERT] Failed to register alert handler: {handler_exc}")

    is_url_contain_sign_in = False
    if '/users/sign_in?' in url:
        # nodriver_kktix_signin already handles smart polling and redirect
        await nodriver_kktix_signin(tab, url, config_dict)

        # Update URL after signin completes
        try:
            url = await tab.evaluate('window.location.href')
            is_url_contain_sign_in = False
        except Exception as exc:
            debug.log(f"取得跳轉後 URL 失敗: {exc}")

    if not is_url_contain_sign_in:
        # Redirect back to homepage if kicked to platform root (e.g., after sold-out or session expiry)
        is_kktix_home = url.rstrip('/') in ['https://kktix.com', 'https://kktix.cc']
        if is_kktix_home:
            homepage = config_dict["homepage"]
            homepage_is_root = homepage.rstrip('/') in ['https://kktix.com', 'https://kktix.cc']
            if not homepage_is_root:
                current_time = time.time()
                last_redirect_time = _state.get("last_homepage_redirect_time", 0)
                redirect_interval = config_dict["advanced"].get("auto_reload_page_interval", 3)
                if redirect_interval <= 0:
                    redirect_interval = 3
                if current_time - last_redirect_time > redirect_interval:
                    try:
                        _state["last_homepage_redirect_time"] = current_time
                        await tab.get(homepage)
                    except Exception:
                        pass

        if '#/booking' in url:
            # Seat selection page (only some events have this)
            await nodriver_kktix_booking_main(tab, config_dict)
        elif '/registrations/new' in url:
            # Check if alert handler flagged a reload (e.g., sold-out alert after clicking next)
            if _state.get("alert_needs_reload", False):
                _state["alert_needs_reload"] = False
                _state["played_sound_ticket"] = False
                # The submission failed, so drop the cooldown and let the next
                # round act immediately instead of waiting it out.
                _state["next_button_pressed_url"] = ""
                _state["next_button_pressed_time"] = 0
                debug.log("[KKTIX] Alert triggered reload, refreshing page...")
                try:
                    await tab.reload()
                except Exception as reload_exc:
                    debug.log(f"[KKTIX] Alert-triggered reload failed: {reload_exc}")
                # Reload is a recovery path, not a terminal state.
                return False

            # Check and dismiss guest modal (立刻成為 KKTIX 會員) before processing
            # This modal appears when user is not logged in
            await nodriver_kktix_check_guest_modal(tab, config_dict)

            # Dismiss sold-out / race-condition DOM modals ("別人搶先一步", "已無可配座位")
            is_failure_modal = await nodriver_kktix_dismiss_failure_modal(tab, config_dict)
            if is_failure_modal:
                _state["played_sound_ticket"] = False
                _state["next_button_pressed_url"] = ""
                _state["next_button_pressed_time"] = 0
                debug.log("[KKTIX] Failure modal dismissed, refreshing page...")
                try:
                    await tab.reload()
                except Exception as reload_exc:
                    debug.log(f"[KKTIX] Post-modal reload failed: {reload_exc}")
                return False

            _state["start_time"] = time.time()

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
                _state["fail_list"] = []
                _state["played_sound_ticket"] = False
                # Waiting room keeps the registrations/new URL; it refreshes
                # itself, so only emit a throttled status log here
                await nodriver_kktix_check_queue_page(tab, config_dict)
            else:
                # Queue may end with a guest session; tickets render without
                # input fields then, so go log in before selecting anything
                if await nodriver_kktix_redirect_to_signin_if_guest(tab, url, config_dict):
                    return False

                # 勾選同意條款 - 使用精確的 ID 選擇器
                is_finish_checkbox_click = await nodriver_check_checkbox(tab, '#person_agree_terms:not(:checked)')

                # Telemetry only. This used to gate the ticket flow with the
                # meaning "the form looks filled in, so do not run again", but
                # "filled in" can stay true forever: the bot ticks the terms box
                # and types the ticket count itself, so one bad round latched the
                # guard on permanently and nothing could ever recover (#377/#375).
                form_state = await nodriver_kktix_check_form_state(tab, config_dict)
                is_form_ready = bool(form_state.get("ready", False))
                if _state is not None:
                    last_logged_value = _state.get("last_ticket_already_selected_log_value", None)
                    if last_logged_value != is_form_ready:
                        debug.log(f"[KKTIX CHECK] form ready: {is_form_ready} "
                                  f"(qualification={form_state['qualification']['status']})")
                        _state["last_ticket_already_selected_log_value"] = is_form_ready
                else:
                    debug.log(f"[KKTIX CHECK] form ready: {is_form_ready}")

                # The real guard: did we just submit this very page? Bounded by
                # both time and URL, so it always expires - unlike the old
                # boolean, which had no route back once it latched.
                is_press_cooldown = (
                    _state.get("next_button_pressed_url") == url
                    and time.time() - _state.get("next_button_pressed_time", 0)
                    < CONST_KKTIX_NEXT_BUTTON_COOLDOWN
                )

                if config_dict["kktix"]["auto_fill_ticket_number"] and not is_press_cooldown:
                    debug.log("[KKTIX] Executing ticket selection logic...")
                    _state["fail_list"], _state["played_sound_ticket"] = await nodriver_kktix_reg_new_main(tab, config_dict, _state["fail_list"], _state["played_sound_ticket"])
                    _state["done_time"] = time.time()
        else:
            is_event_page = False
            if '/events/' in url:
                # ex: https://xxx.kktix.cc/events/xxx-copy-1
                if len(url.split('/'))<=5:
                    is_event_page = True

            if is_event_page:
                # 檢查是否需要自動重載（Chrome 擴充功能未啟用時）
                # DISABLED: API check causes access log and may be detected as bot behavior

                # Try date selection first (multi-session pages)
                is_date_selected = False
                if config_dict["date_auto_select"]["enable"]:
                    is_date_selected = await nodriver_kktix_date_auto_select(tab, config_dict)

                # If date selection didn't happen (single session or failed), use next button
                if not is_date_selected:
                    if config_dict["kktix"]["auto_press_next_step_button"]:
                        # 自動點擊「立即購票」按鈕
                        await nodriver_kktix_events_press_next_button(tab, config_dict)

            # reset answer fail list.
            _state["fail_list"] = []
            _state["played_sound_ticket"] = False

    # 檢查是否已經偵測過成功頁面，避免重複偵測
    is_kktix_got_ticket = False
    if not _state["got_ticket_detected"]:
        is_kktix_got_ticket = check_kktix_got_ticket(url, config_dict)
        if is_kktix_got_ticket:
            _state["got_ticket_detected"] = True
    elif _state["got_ticket_detected"]:
        # 已經偵測過成功頁面，直接設定為 True 但不重複輸出
        is_kktix_got_ticket = True

    is_quit_bot = False
    if is_kktix_got_ticket:
        # 搶票成功，設定結束標記
        is_quit_bot = True

        # 只在第一次偵測成功時執行動作
        if not _state["success_actions_done"]:
            if not _state["start_time"] is None:
                if not _state["done_time"] is None:
                    bot_elapsed_time = _state["done_time"] - _state["start_time"]
                    if _state["elapsed_time"] != bot_elapsed_time:
                        debug.log("[KKTIX] Ticket purchase completed, elapsed time: {:.3f} seconds".format(bot_elapsed_time))
                    _state["elapsed_time"] = bot_elapsed_time

            if not _state["played_sound_order"]:
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)
                send_discord_notification(config_dict, "order", "KKTIX")
                send_telegram_notification(config_dict, "order", "KKTIX")

            _state["played_sound_order"] = True

            if config_dict["advanced"]["headless"]:
                if not _state["is_popup_checkout"]:
                    kktix_account = config_dict["accounts"]["kktix_account"]
                    kktix_password = config_dict["accounts"]["kktix_password"].strip()

                    debug.log(f"[KKTIX] Registration/real-name URL: {url}")
                    if len(kktix_account) > 0:
                        # Mask account information to protect privacy
                        if len(kktix_account) > 5:
                            masked_account = kktix_account[:3] + "***" + kktix_account[-2:]
                        else:
                            masked_account = "***"
                        print("搶票成功, 帳號:", masked_account)

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

                    _state["is_popup_checkout"] = True

            # 標記動作已完成，避免重複執行
            _state["success_actions_done"] = True
    else:
        _state["is_popup_checkout"] = False
        _state["played_sound_order"] = False
        _state["printed_completed"] = False

    # Approach B: handle printed_completed internally
    if is_quit_bot:
        if not _state.get("printed_completed", False):
            debug.log("[KKTIX] Ticket purchase completed")
            _state["printed_completed"] = True

    return is_quit_bot

async def nodriver_kktix_booking_main(tab, config_dict):
    """KKTIX #/booking seat selection page automation.

    Handles the seat assignment flow that appears for some events:
    Step 1: Dismiss the info modal (system seat assignment notice)
    Step 2: Click confirm seat button to expand dropdown
    Step 3: Click done to complete seat selection
    """
    debug = util.create_debug_logger(config_dict)
    ret = False

    try:
        # Step 1: Close info modal if visible
        modal_visible = await tab.evaluate('''(function(){
            var m = document.querySelector('#infoModal');
            if (!m) return false;
            var style = window.getComputedStyle(m);
            return style.display !== 'none' && m.classList.contains('in');
        })()''')
        if modal_visible:
            info_btn = await tab.query_selector('#infoModal .modal-footer button')
            if info_btn:
                await info_btn.click()
                debug.log("[KKTIX BOOKING] Dismissed info modal")
                await asyncio.sleep(0.5)
                return ret  # Wait for next iteration to process remaining steps

        # Step 2: Click confirm seat button to expand dropdown
        confirm_btn = await tab.query_selector('.btn-group-for-seat button.dropdown-toggle')
        if confirm_btn:
            is_open = await tab.evaluate('''(function(){
                var g = document.querySelector('.btn-group-for-seat');
                return g && g.classList.contains('open');
            })()''')

            if not is_open:
                await confirm_btn.click()
                debug.log("[KKTIX BOOKING] Clicked confirm seat button")
                await asyncio.sleep(0.3)

            # Step 3: Click done to complete seat selection
            done_btn = await tab.query_selector('a[ng-click="done()"]')
            if done_btn:
                await done_btn.click()
                debug.log("[KKTIX BOOKING] Clicked done - seat confirmed")
                ret = True
    except Exception as exc:
        debug.log(f"[KKTIX BOOKING] Error: {exc}")

    return ret

async def nodriver_kktix_confirm_order_button(tab, config_dict):
    """
    KKTIX 訂單確認按鈕自動點擊功能
    對應 Chrome 版本的 kktix_confirm_order_button()
    """
    debug = util.create_debug_logger(config_dict)
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
                debug.log("KKTIX 訂單確認按鈕已點擊")
            else:
                debug.log("KKTIX 訂單確認按鈕存在但不可點擊")
        else:
            debug.log("未找到 KKTIX 訂單確認按鈕")

    except Exception as exc:
        debug.log(f"KKTIX 訂單確認按鈕點擊失敗: {exc}")

    return ret


async def nodriver_kktix_order_member_code(tab, config_dict):
    """
    KKTIX 會員序號自動填寫功能
    對應 TicketPlus 的 nodriver_ticketplus_order_exclusive_code()

    使用場景：
    - KKTIX 部分活動需要輸入會員序號才能購票
    - 會員序號欄位在選擇票券數量後動態展開
    - 使用 AngularJS 框架（需要特殊事件觸發處理）

    呼叫位置：nodriver_kktix_handle_qualification_and_next()，在資格 radio
    點選之後——序號欄位屬於某個資格選項，先選資格才填碼。

    Args:
        tab: NoDriver tab 物件
        config_dict: 設定字典

    Returns:
        bool: 是否成功填寫會員序號
    """
    debug = util.create_debug_logger(config_dict)

    # 檢查暫停狀態
    if await check_and_handle_pause(config_dict):
        return False

    # 讀取會員序號設定（複用 discount_code）
    member_code = config_dict["advanced"].get("discount_code", "").strip()

    # 如果沒有設定會員序號，直接跳過
    if not member_code:
        debug.log("[KKTIX MEMBER CODE] No member code configured, skipping")
        return False

    debug.log("[KKTIX MEMBER CODE] Attempting to fill member code")

    try:
        # json.dumps produces a complete JS string literal, quotes included -
        # hand-rolled escaping missed cases and is banned by code-boundaries.
        member_code_literal = json.dumps(member_code)

        # 人類化延遲（隨機 100-300ms）
        await tab.sleep(random.uniform(0.1, 0.3))

        # 使用 JavaScript 注入填入會員序號
        result = await tab.evaluate(f'''
            (function() {{
                const memberCode = {member_code_literal};
                let filledCount = 0;

                // Bind to the ticket unit that actually holds the selection;
                // a document-wide fill would spill onto other ticket types.
                let scope = document;
                const units = document.querySelectorAll('.ticket-unit');
                for (const unit of units) {{
                    const qty = unit.querySelector('input[ng-model="ticketModel.quantity"]');
                    if (qty && !qty.disabled && parseInt(qty.value) > 0) {{
                        scope = unit;
                        break;
                    }}
                }}

                // 策略 1: 使用 class 選擇器（最直接）
                const memberCodeInputs = scope.querySelectorAll('input.member-code');

                for (let input of memberCodeInputs) {{
                    // 檢查輸入框是否為空且未禁用
                    if (!input.value && !input.disabled) {{
                        input.value = memberCode;

                        // 觸發完整事件序列（AngularJS 需要）
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('blur', {{ bubbles: true }}));

                        // 確保 Angular 模型更新
                        if (window.angular) {{
                            const scope = window.angular.element(input).scope();
                            if (scope) {{
                                scope.$apply();
                            }}
                        }}

                        filledCount++;
                    }}
                }}

                // 策略 2: 如果策略 1 失敗，使用 ng-model 選擇器
                if (filledCount === 0) {{
                    const ngModelInputs = scope.querySelectorAll('input[ng-model*="member_codes"]');
                    for (let input of ngModelInputs) {{
                        if (!input.value && !input.disabled) {{
                            input.value = memberCode;
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('blur', {{ bubbles: true }}));

                            if (window.angular) {{
                                const scope = window.angular.element(input).scope();
                                if (scope) {{
                                    scope.$apply();
                                }}
                            }}

                            filledCount++;
                        }}
                    }}
                }}

                return {{
                    success: filledCount > 0,
                    filledCount: filledCount
                }};
            }})()
        ''')

        # 使用統一解析函數處理返回值
        result = util.parse_nodriver_result(result)

        if result and result.get('success'):
            filled_count = result.get('filledCount', 0)
            debug.log(f"[KKTIX MEMBER CODE] Successfully filled {filled_count} member code field(s)")

            # 填寫完成後短暫延遲，確保 Angular 更新完成
            await tab.sleep(0.2)

            # This function used to press "next" itself, on the assumption that
            # a filled code meant the whole form was done. It did not check the
            # qualification radio, so it could submit an incomplete form and
            # double-click alongside the caller. The flow layer now owns that
            # decision - see nodriver_kktix_handle_qualification_and_next.
            return True
        else:
            debug.log("[KKTIX MEMBER CODE] No member code fields found on page")
            return False

    except Exception as e:
        debug.log(f"[KKTIX MEMBER CODE] Error filling member code: {str(e)}")
        return False

