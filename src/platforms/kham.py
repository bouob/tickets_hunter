#encoding=utf-8
# =============================================================================
# KHAM Platform Module
# Extracted from nodriver_tixcraft.py during modularization (Phase 1)
# Contains: kham.com.tw, ticket.com.tw, udnfunlife.com (kham family)
# Also includes shared seat selection functions (nodriver_ticket_seat_*)
# =============================================================================

import asyncio
import base64
import json
import os
import random
import re
import time
import traceback
import webbrowser

from zendriver import cdp

import util
from nodriver_common import (
    asyncio_sleep_with_pause_check,
    check_and_handle_pause,
    nodriver_check_checkbox,
    nodriver_check_modal_dialog_popup,
    nodriver_get_captcha_image_from_dom_snapshot,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    write_question_to_file,
    CONST_FROM_TOP_TO_BOTTOM,
    CONST_MAXBOT_ANSWER_ONLINE_FILE,
    CONST_MAXBOT_INT28_FILE,
)

__all__ = [
    "nodriver_kham_login",
    "nodriver_kham_go_buy_redirect",
    "nodriver_kham_check_realname_dialog",
    "nodriver_kham_allow_not_adjacent_seat",
    "nodriver_kham_switch_to_auto_seat",
    "nodriver_kham_check_captcha_text_error",
    "nodriver_kham_product",
    "nodriver_kham_date_auto_select",
    "nodriver_kham_keyin_captcha_code",
    "nodriver_kham_area_auto_select",
    "nodriver_kham_auto_ocr",
    "nodriver_kham_captcha",
    "nodriver_kham_performance",
    "nodriver_kham_main",
    "nodriver_ticket_login",
    "nodriver_kham_seat_type_auto_select",
    "nodriver_kham_seat_auto_select",
    "nodriver_kham_seat_main",
    "nodriver_udn_seat_auto_select",
    "nodriver_udn_seat_select_ticket_type",
    "nodriver_udn_seat_main",
    "nodriver_ticket_seat_type_auto_select",
    "nodriver_ticket_seat_auto_select",
    "nodriver_ticket_seat_main",
    "nodriver_ticket_check_seat_taken_dialog",
    "nodriver_ticket_close_dialog_with_retry",
    "nodriver_ticket_allow_not_adjacent_seat",
    "nodriver_ticket_switch_to_auto_seat",
]

# Module-level state (replaces global kham_dict)
_state = {}


# ====================================================================================
# Kham Platform (kham.com.tw / ticket.com.tw / udnfunlife.com)
# ====================================================================================

async def nodriver_kham_login(tab, account, password, ocr=None, config_dict=None):
    """
    Kham platform login with OCR captcha support
    Reference: chrome_tixcraft.py kham_login (line 5492-5540)
    """
    ret = False
    debug = util.create_debug_logger(config_dict)

    # Find email/account input
    el_email = None
    try:
        el_email = await tab.query_selector('#ACCOUNT')
    except Exception as exc:
        debug.log("Find #ACCOUNT fail:", exc)

    # Input account
    is_email_sent = False
    if el_email:
        try:
            inputed_text = await tab.evaluate('document.querySelector("#ACCOUNT").value')
            if not inputed_text or len(inputed_text) == 0:
                await el_email.send_keys(account)
                is_email_sent = True
            else:
                if inputed_text == account:
                    is_email_sent = True
        except Exception as exc:
            debug.log("Input account fail:", exc)

    # Find password input
    el_pass = None
    if is_email_sent:
        try:
            el_pass = await tab.query_selector('table.login > tbody > tr > td > input[type="password"]')
        except Exception as exc:
            debug.log("Find password input fail:", exc)

    # Input password
    is_password_sent = False
    if el_pass:
        try:
            inputed_text = await tab.evaluate('document.querySelector("table.login > tbody > tr > td > input[type=password]").value')
            if not inputed_text or len(inputed_text) == 0:
                await el_pass.click()
                if len(password) > 0:
                    await el_pass.send_keys(password)
                    is_password_sent = True
        except Exception as exc:
            debug.log("Input password fail:", exc)

    # Handle captcha with OCR
    is_captcha_sent = False
    if is_password_sent and ocr:
        try:
            debug.log("[KHAM LOGIN] Starting OCR captcha processing...")

            ocr_start_time = time.time()

            # Get captcha image using canvas
            img_base64 = None
            try:
                form_verifyCode_base64 = await tab.evaluate('''
                    (function() {
                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        var img = document.getElementById('chk_pic');
                        if (img != null) {
                            canvas.height = img.naturalHeight;
                            canvas.width = img.naturalWidth;
                            context.drawImage(img, 0, 0);
                            return canvas.toDataURL();
                        }
                        return null;
                    })();
                ''')

                if form_verifyCode_base64:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                debug.log("[KHAM LOGIN] Canvas exception:", str(exc))

            # OCR recognition
            ocr_answer = None
            if img_base64:
                try:
                    ocr_answer = ocr.classification(img_base64)
                    ocr_done_time = time.time()
                    ocr_elapsed_time = ocr_done_time - ocr_start_time
                    debug.log(f"[KHAM LOGIN] OCR elapsed time: {ocr_elapsed_time:.3f}s")
                except Exception as exc:
                    debug.log("[KHAM LOGIN] OCR classification fail:", exc)

            # Input captcha answer
            if ocr_answer:
                ocr_answer = ocr_answer.strip()
                debug.log(f"[KHAM LOGIN] OCR answer: {ocr_answer}")

                if len(ocr_answer) == 4:
                    try:
                        # Find captcha input field
                        el_captcha = await tab.query_selector('#CHK')
                        if el_captcha:
                            await el_captcha.click()
                            await el_captcha.send_keys(ocr_answer)
                            is_captcha_sent = True
                            debug.log("[KHAM LOGIN] Captcha filled successfully")
                    except Exception as exc:
                        debug.log("[KHAM LOGIN] Fill captcha fail:", exc)
                else:
                    debug.log(f"[KHAM LOGIN] Invalid captcha length: {len(ocr_answer)}, expected 4")
            else:
                debug.log("[KHAM LOGIN] OCR answer is None")

        except Exception as exc:
            debug.log("[KHAM LOGIN] Captcha processing exception:", exc)

    # Click login button
    if is_password_sent:
        try:
            # Wait a bit for captcha to be filled
            if is_captcha_sent:
                await tab.sleep(0.3)

            el_btn = await tab.query_selector('div.memberContent > p > a > button.red')
            if el_btn:
                await el_btn.click()
                ret = True
                debug.log("[KHAM LOGIN] Login button clicked")
        except Exception as exc:
            debug.log("Click login button fail:", exc)

    return ret

async def nodriver_kham_go_buy_redirect(tab, domain_name):
    """
    Click the "Go Buy" button on product page
    Reference: chrome_tixcraft.py kham_go_buy_redirect (line 8449-8461)
    """
    is_button_clicked = False

    if 'kham.com' in domain_name:
        my_css_selector = 'div#content > p > a > button[onclick].red'
    elif 'ticket.com' in domain_name:
        my_css_selector = 'div.row > div > a.btn.btn-order.btn-block'
    elif 'udnfunlife.com' in domain_name:
        # UDN fast buy button uses nexturl attribute instead of onclick
        # Navigate directly to the nexturl for quick purchase (UTK0222_02)
        try:
            next_url = await tab.evaluate('''
                (() => {
                    const btn = document.querySelector('button[name="fastBuy"]');
                    if (btn) {
                        const nexturl = btn.getAttribute('nexturl');
                        if (nexturl) {
                            // Convert relative URL to absolute
                            if (nexturl.startsWith('../')) {
                                return window.location.origin + '/application/' + nexturl.replace('../', '');
                            } else if (nexturl.startsWith('/')) {
                                return window.location.origin + nexturl;
                            }
                            return nexturl;
                        }
                    }
                    return null;
                })()
            ''')

            if next_url:
                await tab.get(next_url)
                return True
        except:
            pass

        # Fallback to traditional buy button if fast buy not available
        my_css_selector = '#buttonBuy'
    else:
        return False

    try:
        el_btn = await tab.query_selector(my_css_selector)
        if el_btn:
            await el_btn.click()
            is_button_clicked = True
    except Exception as exc:
        pass

    return is_button_clicked

async def nodriver_kham_check_realname_dialog(tab, config_dict):
    """
    Check and handle realname notification dialog
    Reference: chrome_tixcraft.py kham_check_realname_dialog (line 9592-9621)
    """
    debug = util.create_debug_logger(config_dict)
    is_realname_dialog_found = False

    try:
        el_message_text = await tab.evaluate('''
            (function() {
                const el = document.querySelector('div.ui-dialog > div#dialog-message.ui-dialog-content');
                return el ? el.textContent : null;
            })();
        ''')

        if el_message_text:
            debug.log("Dialog message:", el_message_text)

            # Check if it's realname notification
            if "個人實名制入場" in el_message_text or "實名制" in el_message_text:
                debug.log("Found realname dialog, clicking OK button...")

                # Click OK button using JavaScript for reliable jQuery UI event triggering
                click_result = await tab.evaluate('''
                    (function() {
                        const btn = document.querySelector('div.ui-dialog-buttonset > button.ui-button');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                    })();
                ''')

                if click_result:
                    is_realname_dialog_found = True

                    # Wait for dialog to close (jQuery UI dialog animation)
                    await tab.sleep(0.5)

                    # Verify dialog is closed to prevent infinite loop
                    try:
                        for _ in range(10):
                            dialog_visible = await tab.evaluate('''
                                (function() {
                                    const dialog = document.querySelector('div.ui-dialog');
                                    if (!dialog) return false;
                                    const style = window.getComputedStyle(dialog);
                                    return style.display !== 'none';
                                })();
                            ''')
                            if not dialog_visible:
                                break
                            await tab.sleep(0.1)
                    except:
                        pass
    except Exception as exc:
        debug.log("Check realname dialog exception:", exc)

    return is_realname_dialog_found

async def nodriver_kham_allow_not_adjacent_seat(tab, config_dict):
    """
    Check the "allow not adjacent seat" checkbox
    Reference: chrome_tixcraft.py kham_allow_not_adjacent_seat (line 9623-9642)
    """
    debug = util.create_debug_logger(config_dict)

    agree_checkbox = None
    try:
        agree_checkbox = await tab.query_selector('table.eventTABLE > tbody > tr > td > input[type="checkbox"]')
    except Exception as exc:
        debug.log("Find kham adjacent_seat checkbox exception:", exc)

    is_finish_checkbox_click = await nodriver_force_check_checkbox(tab, agree_checkbox)

    return is_finish_checkbox_click

async def nodriver_kham_switch_to_auto_seat(tab):
    """
    Switch to auto seat selection mode
    Reference: chrome_tixcraft.py kham_switch_to_auto_seat (line 9230-9266)
    """
    is_switch_to_auto_seat = False

    try:
        # Check if auto seat radio button exists
        btn_switch_result = await tab.evaluate('''
            (function() {
                const btn = document.querySelector('#BUY_TYPE_2');
                if (!btn) return { exists: false };

                const buttonClass = btn.getAttribute('class') || '';
                return {
                    exists: true,
                    isActive: buttonClass === 'red',
                    button: btn
                };
            })();
        ''')

        if btn_switch_result and btn_switch_result.get('exists'):
            if btn_switch_result.get('isActive'):
                is_switch_to_auto_seat = True
            else:
                # Click to switch to auto seat
                el_btn = await tab.query_selector('#BUY_TYPE_2')
                if el_btn:
                    await el_btn.click()
                    is_switch_to_auto_seat = True
    except Exception as exc:
        pass

    return is_switch_to_auto_seat

async def _handle_post_submit_dialog(tab, config_dict):
    """
    After clicking submit, wait for dialog, classify as success/error/none.
    Returns: "success", "error", or "none"
    - success: dialog contained cart-added message, closed it
    - error: dialog contained error message, closed it and cleared captcha
    - none: no dialog appeared within timeout
    """
    debug = util.create_debug_logger(config_dict)
    SUCCESS_KEYWORDS = ["加入購物車"]

    for i in range(10):  # 10 * 0.5s = 5s
        await tab.sleep(0.5)
        try:
            dialog_text = await tab.evaluate('''
                (function() {
                    var el = document.querySelector('div.ui-dialog > div#dialog-message.ui-dialog-content');
                    return el ? el.textContent : null;
                })();
            ''')

            if dialog_text is not None:
                is_success = any(kw in dialog_text for kw in SUCCESS_KEYWORDS)

                el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
                if el_btn:
                    await el_btn.click()
                    await tab.sleep(0.5)

                if is_success:
                    debug.log("[SUBMIT] Success dialog closed")
                    return "success"
                else:
                    debug.log(f"[SUBMIT] Error dialog closed: {dialog_text}")
                    await nodriver_kham_keyin_captcha_code(tab, "")
                    return "error"
        except Exception as e:
            if i == 9:
                debug.log(f"[SUBMIT] Dialog detection failed: {e}")

    debug.log("[SUBMIT] No dialog appeared within 5 seconds")
    return "none"

async def nodriver_kham_check_captcha_text_error(tab, config_dict):
    """
    Check captcha error message dialog
    Reference: chrome_tixcraft.py kham_check_captcha_text_error (line 9565-9590)
    """
    debug = util.create_debug_logger(config_dict)
    is_reset_password_text = False

    try:
        el_message_text = await tab.evaluate('''
            (function() {
                const el = document.querySelector('div.ui-dialog > div#dialog-message.ui-dialog-content');
                return el ? el.textContent : null;
            })();
        ''')

        if el_message_text:
            debug.log("Dialog message:", el_message_text)

            if "驗證碼輸入錯誤" in el_message_text or "【驗證碼】輸入錯誤" in el_message_text:
                # Click OK button to dismiss dialog
                el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
                if el_btn:
                    await el_btn.click()
                    is_reset_password_text = True

                # Clear captcha input and wait for re-input
                await nodriver_kham_keyin_captcha_code(tab, "")
    except Exception as exc:
        debug.log("Check captcha error exception:", exc)

    return is_reset_password_text

async def nodriver_kham_product(tab, domain_name, config_dict):
    """
    Product page processing - call date auto select
    Reference: chrome_tixcraft.py kham_product (line 8646-8660)
    """
    debug = util.create_debug_logger(config_dict)

    is_date_assign_by_bot = await nodriver_kham_date_auto_select(tab, domain_name, config_dict)

    if not is_date_assign_by_bot:
        # Click "not on sale now" dialog button if exists
        try:
            el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
            if el_btn:
                await el_btn.click()
        except:
            pass

    return is_date_assign_by_bot

async def nodriver_kham_date_auto_select(tab, domain_name, config_dict):
    """
    Date auto selection with keyword matching and mode fallback
    Reference: chrome_tixcraft.py hkam_date_auto_select (line 8463-8644)
    Supports: kham.com.tw, ticket.com.tw, udnfunlife.com
    """
    debug = util.create_debug_logger(config_dict)

    # Wait for page to load
    await tab.sleep(0.6)

    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # Feature 003: Safe access for conditional fallback switch
    date_auto_fallback = config_dict.get('date_auto_fallback', False)

    debug.log("date_keyword:", date_keyword)
    debug.log("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    # Get all date rows using query_selector_all (similar to TixCraft)
    selector = "table.eventTABLE > tbody > tr"
    if 'ticket.com' in domain_name:
        selector = "div.description > table.table.table-striped.itable > tbody > tr"
    elif 'udnfunlife.com' in domain_name:
        selector = "div.yd_session-block"

    area_list = None
    try:
        area_list = await tab.query_selector_all(selector)
    except Exception as exc:
        debug.log(f"query_selector_all error: {exc}")

    # Format area list with keyword filtering
    formated_area_list = []
    formated_area_list_text = []

    if area_list and len(area_list) > 0:
        for row in area_list:
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
                row_text = row_text.strip()
            except Exception as exc:
                debug.log(f"get_html error: {exc}")
                break

            if not row_text or util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                continue

            # Filter: exclude disabled buttons
            # Issue #188: Allow "尚未開賣" (coming soon) buttons even with CSS disabled class
            if ' disabled">' in row_html:
                if '尚未開賣' not in row_html:
                    continue

            # Filter: check if button exists (for kham/ticket)
            if 'udnfunlife' not in domain_name:
                if '<button' in row_html:
                    # Issue #188: Support "尚未開賣" (coming soon) button for ERA TICKET
                    valid_button_texts = ['立即訂購', '點此購票', '尚未開賣']
                    if not any(text in row_html for text in valid_button_texts):
                        continue
                else:
                    continue  # No button, skip

            # Filter: check if tickets available (udn)
            if 'udnfunlife' in domain_name:
                if '前往購票' not in row_html:
                    continue

            # Filter: check price availability (for kham/ticket)
            # Reference: chrome_tixcraft.py line 8558-8568
            if 'udnfunlife' not in domain_name:
                if '<td' in row_html:
                    disabled_marker = '<del>' if 'ticket.com' in domain_name else '"lightblue"'
                    # Split by <td to get each column
                    td_array = row_html.split('<td')
                    if len(td_array) > 3:
                        # 4th td is the price column (date, location, price, order)
                        td_target = td_array[3]
                        # Split prices by Chinese comma
                        price_array = td_target.split('、')
                        is_all_price_disabled = True
                        for each_price in price_array:
                            if disabled_marker not in each_price:
                                is_all_price_disabled = False
                                break
                        if is_all_price_disabled:
                            debug.log(f"Skipping row: all prices are disabled")
                            continue

            formated_area_list.append(row)
            formated_area_list_text.append(row_text)

    if debug.enabled:
        debug.log(f"Valid date rows count: {len(formated_area_list)}")
        if formated_area_list and len(formated_area_list) > 0:
            # Clean up whitespace for display
            import re
            display_text = re.sub(r'\s+', ' ', formated_area_list_text[0]).strip()
            debug.log(f"First row text sample: {display_text[:80]}")

    # Apply keyword matching (similar to TixCraft)
    matched_blocks = None
    if formated_area_list and len(formated_area_list) > 0:
        if len(date_keyword) == 0:
            matched_blocks = formated_area_list
            debug.log(f"No keyword specified, using all {len(matched_blocks)} rows")
        else:
            # Match by keyword
            matched_blocks = []
            try:
                import json
                import re
                keyword_array = json.loads("[" + date_keyword + "]")
                debug.log(f"date_keyword array: {keyword_array}")

                # Feature 003: Early return pattern - iterate keywords in priority order
                target_row_found = False
                keyword_matched_index = -1

                for keyword_index, keyword_item_set in enumerate(keyword_array):
                    debug.log(f"[KHAM DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

                    # Check all rows for this keyword
                    for i, row_text in enumerate(formated_area_list_text):
                        normalized_row_text = re.sub(r'\s+', ' ', row_text)
                        is_match = False

                        if isinstance(keyword_item_set, str):
                            # OR logic: single keyword
                            normalized_keyword = re.sub(r'\s+', ' ', keyword_item_set)
                            is_match = normalized_keyword in normalized_row_text
                        elif isinstance(keyword_item_set, list):
                            # AND logic: all keywords must match
                            normalized_keywords = [re.sub(r'\s+', ' ', kw) for kw in keyword_item_set]
                            match_results = [kw in normalized_row_text for kw in normalized_keywords]
                            is_match = all(match_results)

                        if is_match:
                            # Keyword matched - IMMEDIATELY select and stop
                            matched_blocks = [formated_area_list[i]]
                            target_row_found = True
                            keyword_matched_index = keyword_index
                            if debug.enabled:
                                debug.log(f"[KHAM DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                                # Clean up whitespace for display
                                display_row_text = re.sub(r'\s+', ' ', row_text).strip()
                                debug.log(f"[KHAM DATE SELECT] Selected date: {display_row_text[:80]} (keyword match)")
                            break

                    if target_row_found:
                        # EARLY RETURN: Stop checking further keywords
                        break

                # All keywords failed log
                if not target_row_found:
                    debug.log(f"[KHAM DATE KEYWORD] All keywords failed to match")

            except Exception as e:
                debug.log(f"keyword parsing error: {e}")
                matched_blocks = formated_area_list

            if debug.enabled:
                if matched_blocks:
                    debug.log("After keyword match, found count:", len(matched_blocks))
                else:
                    debug.log("No matches found for keyword:", date_keyword)
    else:
        debug.log("No valid date rows found")

    # Feature 003: Conditional fallback based on date_auto_fallback switch
    if matched_blocks is not None and len(matched_blocks) == 0 and len(date_keyword) > 0:
        if formated_area_list and len(formated_area_list) > 0:
            if date_auto_fallback:
                # Fallback enabled - use auto_select_mode
                debug.log(f"[KHAM DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
                debug.log(f"[KHAM DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
                matched_blocks = formated_area_list
            else:
                # Fallback disabled - strict mode (no selection, will reload)
                debug.log(f"[KHAM DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
                debug.log(f"[KHAM DATE SELECT] No date selected, will reload page and retry")
                return False  # Return False to trigger reload logic in caller

    # Handle case when formated_area_list is empty or None (all options excluded)
    if formated_area_list is None or len(formated_area_list) == 0:
        debug.log(f"[KHAM DATE FALLBACK] No available options after exclusion")
        return False

    # Get target date using mode
    target_row = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    if debug.enabled:
        if target_row:
            # Get text for debug
            try:
                target_row_html = await target_row.get_html()
                target_row_text = util.remove_html_tags(target_row_html)
                # Clean up whitespace for display
                import re
                display_row_text = re.sub(r'\s+', ' ', target_row_text).strip()
                debug.log(f"Target row selected (mode: {auto_select_mode}): {display_row_text[:80]}")
            except:
                debug.log(f"Target row selected (mode: {auto_select_mode})")
        else:
            debug.log(f"No target row selected from {len(matched_blocks) if matched_blocks else 0} matched blocks")

    is_date_assign_by_bot = False
    is_coming_soon = False

    if target_row:
        # Issue #188: Check if target is "coming soon" button before clicking
        try:
            target_row_html = await target_row.get_html()
            if '尚未開賣' in target_row_html:
                is_coming_soon = True
                debug.log("[TICKET.COM] Coming soon button detected, skip clicking")
        except:
            pass

        if not is_coming_soon:
            # Click the button in target row (similar to TixCraft)
            try:
                button_selector = 'button'
                if 'udnfunlife.com' in domain_name:
                    button_selector = 'div.goNext'

                btn = await target_row.query_selector(button_selector)
                if btn:
                    await btn.click()
                    is_date_assign_by_bot = True
                    debug.log("Date buy button clicked successfully")
            except Exception as exc:
                debug.log(f"Click button error: {exc}")

    # Auto reload if: no target found OR target is coming soon button
    if not is_date_assign_by_bot and auto_reload_coming_soon_page_enable:
        if is_coming_soon or formated_area_list is None or len(formated_area_list) == 0:
            try:
                if debug.enabled:
                    if is_coming_soon:
                        debug.log("[TICKET.COM] Waiting for sale time, will reload after delay...")
                    else:
                        debug.log("Date list empty, will auto reload after delay...")

                # Wait before reload (use config interval)
                reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0.0)
                if reload_interval > 0:
                    await tab.sleep(reload_interval)
                else:
                    await tab.sleep(1.0)  # Default 1 second delay

                await tab.reload()
                await tab.sleep(0.5)  # Wait for page to start loading

                debug.log("Page reloaded, waiting for content...")
            except Exception as exc:
                debug.log("Auto reload exception:", exc)

    return is_date_assign_by_bot

async def nodriver_kham_keyin_captcha_code(tab, answer="", auto_submit=False):
    """
    Input captcha code manually or auto-submit
    Reference: chrome_tixcraft.py kham_keyin_captcha_code (line 9359-9424)
    """
    is_verifyCode_editing = False

    # Find captcha input with multiple selectors
    form_verifyCode = None
    selectors = [
        'input#CHK',
        '#ctl00_ContentPlaceHolder1_CHK',
        'input[value="驗證碼"]',
        'input[placeholder="驗證碼"]',
        'input[placeholder="請輸入圖片上符號"]',
        'input[type="text"][maxlength="4"]'
    ]

    for selector in selectors:
        try:
            form_verifyCode = await tab.query_selector(selector)
            if form_verifyCode:
                break
        except:
            continue

    is_start_to_input_answer = False
    if form_verifyCode:
        if len(answer) > 0:
            # Check current input value
            try:
                inputed_value = await tab.evaluate(f'''
                    (function() {{
                        const input = document.querySelector('{selectors[0]}') ||
                                    document.querySelector('{selectors[1]}') ||
                                    document.querySelector('{selectors[2]}') ||
                                    document.querySelector('{selectors[3]}') ||
                                    document.querySelector('{selectors[4]}') ||
                                    document.querySelector('{selectors[5]}');
                        return input ? input.value : null;
                    }})();
                ''')

                if inputed_value is None:
                    inputed_value = ""

                # Clear if placeholder text
                if inputed_value == "驗證碼":
                    try:
                        await form_verifyCode.apply('function(el) { el.value = ""; }')
                    except:
                        pass
                else:
                    if len(inputed_value) > 0:
                        print("Captcha text already inputed:", inputed_value, "target answer:", answer)
                        is_verifyCode_editing = True
                    else:
                        is_start_to_input_answer = True
            except Exception as exc:
                print("Check verify code value fail:", exc)
        else:
            # Clear input
            try:
                await form_verifyCode.apply('function(el) { el.value = ""; }')
            except:
                pass

    if is_start_to_input_answer:
        try:
            await form_verifyCode.click()
            await form_verifyCode.apply('function(el) { el.value = ""; }')
            await form_verifyCode.send_keys(answer)
        except Exception as exc:
            print("Send keys OCR answer fail:", answer, exc)

    # Auto submit if enabled (for away_from_keyboard mode)
    if auto_submit:
        try:
            # Find and click submit button using NoDriver CDP
            # Year Ticket (ticket.com.tw): AddShopingCart button
            print("[AUTO SUBMIT] Searching for submit button...")
            submit_button = await tab.query_selector('input[id$="AddShopingCart"]')

            if submit_button:
                print("[AUTO SUBMIT] Submit button found, checking if enabled...")
                # Check if button is enabled
                is_enabled = await submit_button.apply('function(el) { return !el.disabled; }')

                if is_enabled:
                    print("[AUTO SUBMIT] Button enabled, scrolling into view...")
                    # Scroll button into view first (important for CDP click)
                    try:
                        await submit_button.scroll_into_view()
                        await tab.sleep(0.3)
                    except:
                        pass

                    print("[AUTO SUBMIT] Clicking submit button using CDP native click...")
                    # Use NoDriver CDP native click
                    await submit_button.click()
                    print("[AUTO SUBMIT] Submit button clicked successfully!")
                else:
                    print("[AUTO SUBMIT] Submit button is disabled")
            else:
                print("[AUTO SUBMIT] Submit button not found (selector: input[id$=\"AddShopingCart\"])")
        except Exception as exc:
            print(f"[AUTO SUBMIT] Error: {exc}")
            import traceback
            traceback.print_exc()

    return is_verifyCode_editing

async def nodriver_kham_area_auto_select(tab, domain_name, config_dict, area_keyword_item):
    """
    Area/ticket type auto selection with table and dropdown support
    Reference: chrome_tixcraft.py kham_area_auto_select (line 8662-8925)
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False, False, False

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    # Feature 003: Safe access for conditional fallback switch
    area_auto_fallback = config_dict.get('area_auto_fallback', False)

    # NOTE: area_keyword_item is already a SINGLE keyword string from upper layer JSON parsing (line 13180)
    # Upper layer at line 13180: area_keyword_array = json.loads("[" + area_keyword + "]")
    # Then loops through and passes each keyword individually to this function (line 13185-13187)
    # Therefore, we should NOT split by comma again here - just clean the quotes
    if area_keyword_item and len(area_keyword_item) > 0:
        try:
            area_keyword_clean = area_keyword_item.strip()
            if area_keyword_clean.startswith('"') and area_keyword_clean.endswith('"'):
                area_keyword_clean = area_keyword_clean[1:-1]

            # Use the cleaned keyword directly (no comma split)
            area_keyword_item = area_keyword_clean
        except Exception as e:
            debug.log(f"[KHAM AREA] Keyword parse error: {e}")

    is_price_assign_by_bot = False
    is_need_refresh = False
    is_keyword_matched = False  # Track whether keyword actually matched (vs fallback)

    # Try dropdown mode first using CDP DOM operations
    # Supports both ibon (id="PRICE") and ticket.com.tw (id="ctl00_ContentPlaceHolder1_PRICE")
    price_select = None
    try:
        # Try standard id="PRICE" first (ibon)
        price_select = await tab.query_selector('select#PRICE')
        if not price_select:
            # Try ticket.com.tw selector
            selects = await tab.query_selector_all('select[id$="_PRICE"]')
            if selects and len(selects) > 0:
                price_select = selects[0]
    except Exception as exc:
        debug.log(f"Error finding PRICE select: {exc}")

    # Handle dropdown mode using CDP
    if price_select:
        try:
            # Get all option elements using CDP
            option_elements = await price_select.query_selector_all('option:not([value="-1"])')

            debug.log(f"Found dropdown with {len(option_elements)} options")

            # Extract option data using CDP
            options_data = []
            for i, opt_elem in enumerate(option_elements):
                try:
                    # Get text content
                    opt_text = await opt_elem.get_html()
                    opt_text = util.remove_html_tags(opt_text).strip()

                    # Get value attribute using JavaScript (more reliable)
                    opt_value = await opt_elem.apply('function(el) { return el.value; }')

                    # Check if disabled
                    is_disabled = await opt_elem.apply('function(el) { return el.disabled; }')

                    if opt_text and not is_disabled:
                        options_data.append({
                            'index': i,
                            'text': opt_text,
                            'value': opt_value,
                            'element': opt_elem
                        })
                except Exception as exc:
                    debug.log(f"Error processing option {i}: {exc}")

            # Feature 003: Filter by keyword with early return pattern
            matched_options = []
            available_options = []  # Track all non-excluded options for fallback

            for opt in options_data:
                option_text = opt['text']

                # Apply exclude keyword filter first
                if util.reset_row_text_if_match_keyword_exclude(config_dict, option_text):
                    debug.log(f"[KHAM AREA] Option excluded: '{option_text}'")
                    continue

                # Track available options for fallback
                available_options.append(opt)

                # Apply positive keyword matching with early return
                if len(area_keyword_item) > 0:
                    area_keyword_array = area_keyword_item.split(' ')
                    row_text = util.format_keyword_string(option_text)
                    is_match = True
                    for keyword in area_keyword_array:
                        formatted_keyword = util.format_keyword_string(keyword)
                        if formatted_keyword not in row_text:
                            is_match = False
                            break
                    if is_match:
                        # EARLY RETURN: First match found
                        matched_options.append(opt)
                        is_keyword_matched = True  # True keyword match (not fallback)
                        debug.log(f"[KHAM AREA KEYWORD] Keyword matched (dropdown): '{option_text}'")
                        break  # Stop checking further options
                else:
                    # No positive keyword - match all (except excluded)
                    matched_options.append(opt)
                    debug.log(f"[KHAM AREA SELECT] No keyword filter (dropdown): '{option_text}'")

            # Feature 003: Conditional fallback logic
            if len(matched_options) == 0 and len(area_keyword_item) > 0:
                if len(available_options) > 0:
                    if area_auto_fallback:
                        # Fallback enabled - use auto_select_mode
                        debug.log(f"[KHAM AREA FALLBACK] area_auto_fallback=true, triggering auto fallback (dropdown)")
                        debug.log(f"[KHAM AREA FALLBACK] Selecting from {len(available_options)} available options using mode='{auto_select_mode}'")
                        matched_options = available_options
                    else:
                        # Fallback disabled - strict mode (no selection, will reload)
                        debug.log(f"[KHAM AREA FALLBACK] area_auto_fallback=false, fallback is disabled (dropdown)")
                        debug.log(f"[KHAM AREA SELECT] No area selected, will reload page and retry")
                        return False, False, False  # Return to trigger reload logic
                else:
                    # No available options (all excluded)
                    debug.log(f"[KHAM AREA FALLBACK] No available options after exclusion (dropdown)")
                    return False, False, False

            # Select target option by simulating user interaction
            if matched_options:
                target_option = matched_options[0]  # Take first match
                target_value = target_option['value']
                target_text = target_option['text']

                debug.log(f"Selecting option: {target_text} (value: {target_value})")

                # Step 1: Click Bootstrap Select button using CDP + JavaScript
                try:
                    # First, check if Bootstrap Select button exists
                    bs_button = await tab.query_selector('button.dropdown-toggle[data-id$="_PRICE"]')

                    if bs_button:
                        debug.log("Found Bootstrap Select button, clicking to open dropdown...")

                        # Use JavaScript to click the button (avoid CDP click error)
                        await tab.evaluate('''
                            (function() {
                                const button = document.querySelector('button.dropdown-toggle[data-id$="_PRICE"]');
                                if (button) {
                                    button.click();
                                }
                            })();
                        ''')

                        # Wait for dropdown to open
                        await tab.sleep(0.5)

                        debug.log(f"Dropdown opened, looking for option: {target_text}")

                        # Step 2: Use CDP to find all <a> elements in the dropdown
                        menu_items = await tab.query_selector_all('ul.dropdown-menu.inner li[data-original-index] a')

                        debug.log(f"Found {len(menu_items)} menu items via CDP")

                        # Check each menu item
                        click_success = False
                        for link in menu_items:
                            try:
                                # Get the text from span.text using CDP
                                text_span = await link.query_selector('span.text')
                                if text_span:
                                    # Get text content
                                    span_html = await text_span.get_html()
                                    option_text = util.remove_html_tags(span_html).strip()

                                    debug.log(f"  Checking option: '{option_text}'")

                                    if option_text == target_text:
                                        debug.log(f"  Match found! Clicking...")

                                        # Use JavaScript to click the link (avoid CDP click error)
                                        await link.apply('function(el) { el.click(); }')
                                        click_success = True
                                        break
                            except Exception as exc:
                                debug.log(f"  Error checking menu item: {exc}")

                        if click_success:
                            is_price_assign_by_bot = True
                            debug.log(f"Successfully clicked Bootstrap Select option: {target_text}")
                        else:
                            debug.log(f"Failed to find/click option: {target_text}")

                    else:
                        # No Bootstrap Select button found, try direct select value setting
                        debug.log("Bootstrap Select button not found, using direct value setting...")

                        # Use CDP to directly set select value (avoid parameter serialization)
                        select_result = False
                        try:
                            select_elem = await tab.query_selector('select#PRICE, select[id$="_PRICE"]')
                            if select_elem:
                                # Set value directly using CDP
                                await select_elem.apply(f'function(el) {{ el.value = "{target_value}"; }}')
                                # Trigger change event
                                await tab.evaluate('''
                                    (function() {
                                        const select = document.querySelector('select#PRICE, select[id$="_PRICE"]');
                                        if (select) {
                                            select.dispatchEvent(new Event('change', { bubbles: true }));
                                        }
                                    })();
                                ''')
                                select_result = True
                        except Exception as fallback_exc:
                            debug.log(f"Direct select value setting error: {fallback_exc}")

                        is_price_assign_by_bot = select_result

                except Exception as exc:
                    debug.log(f"Bootstrap Select interaction error: {exc}")

        except Exception as exc:
            debug.log(f"Dropdown processing error: {exc}")

    else:
        # Handle table mode - use DOM element operations (similar to date_auto_select)
        # Reference: chrome_tixcraft.py kham_area_auto_select (line 8781-8925)

        # Determine selector
        selector = "table#salesTable > tbody > tr[class='status_tr']"
        if 'ticket.com.tw' in domain_name:
            selector = "li.main"
        elif 'udnfunlife' in domain_name:
            # UDN UTK0204: table.status > tr.status_tr (verified via MCP)
            # Soldout items have class="status_tr Soldout"
            selector = "table.status > tbody > tr.status_tr"

        # Get all area rows using query_selector_all
        area_list = None
        try:
            area_list = await tab.query_selector_all(selector)
        except Exception as exc:
            debug.log(f"query_selector_all error: {exc}")

        # Format area list with filtering
        formated_area_list = []
        formated_area_list_text = []

        if area_list and len(area_list) > 0:
            for row in area_list:
                try:
                    row_html = await row.get_html()
                    row_text = util.remove_html_tags(row_html)
                    row_text = row_text.strip()
                except Exception as exc:
                    debug.log(f"get_html error: {exc}")
                    break

                if not row_text:
                    continue

                # Filter: check if sold out
                if '售完' in row_text or ' Soldout' in row_html:
                    continue

                # Filter: udn specific check
                if 'udnfunlife' in domain_name:
                    if 'style="color:gray;border:solid 1px gray;cursor:default"' in row_html:
                        continue

                formated_area_list.append(row)
                formated_area_list_text.append(row_text)

        if debug.enabled:
            debug.log(f"Valid area rows count: {len(formated_area_list)}")
            if formated_area_list and len(formated_area_list) > 0:
                # Clean up whitespace for display
                import re
                display_text = re.sub(r'\s+', ' ', formated_area_list_text[0]).strip()
                debug.log(f"First row text sample: {display_text[:60]}")

        # Apply keyword matching
        matched_blocks = None
        if formated_area_list and len(formated_area_list) > 0:
            # Apply exclude keywords first
            filtered_rows = []
            filtered_rows_text = []
            for i, row_text in enumerate(formated_area_list_text):
                if not util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    filtered_rows.append(formated_area_list[i])
                    filtered_rows_text.append(row_text)

            # Check ticket number availability
            final_rows = []
            final_rows_text = []
            ticket_number = config_dict["ticket_number"]
            for i, row_text in enumerate(filtered_rows_text):
                if 'udnfunlife' not in domain_name:
                    if ticket_number > 1:
                        # Check remaining tickets from last character
                        maybe_count = row_text[-1:] if row_text else ''
                        if maybe_count.isdigit():
                            available_count = int(maybe_count)
                            if available_count < ticket_number:
                                continue
                final_rows.append(filtered_rows[i])
                final_rows_text.append(row_text)

            # Feature 003: Match by keyword with early return pattern
            matched_blocks = []
            if len(area_keyword_item) > 0:
                # Use keyword matching on text, but keep DOM elements
                area_keyword_array = area_keyword_item.split(' ')
                area_found = False

                for i, row_text in enumerate(final_rows_text):
                    formatted_row_text = util.format_keyword_string(row_text)
                    is_match = True
                    for keyword in area_keyword_array:
                        formatted_keyword = util.format_keyword_string(keyword)
                        if formatted_keyword not in formatted_row_text:
                            is_match = False
                            break
                    if is_match:
                        # EARLY RETURN: First match found
                        matched_blocks.append(final_rows[i])
                        area_found = True
                        is_keyword_matched = True  # True keyword match (not fallback)
                        if debug.enabled:
                            # Clean up whitespace for display
                            import re
                            display_row_text = re.sub(r'\s+', ' ', row_text).strip()
                            debug.log(f"[KHAM AREA KEYWORD] Keyword matched (table): {display_row_text[:60]}")
                        break  # Stop checking further rows

                # All keywords failed log
                if not area_found:
                    debug.log(f"[KHAM AREA KEYWORD] All keywords failed to match (table)")
            else:
                # No keyword filter - use all available rows
                matched_blocks = final_rows
                debug.log(f"[KHAM AREA SELECT] No keyword filter (table): using {len(final_rows)} available rows")

            if matched_blocks:
                debug.log("Matched area blocks:", len(matched_blocks))

            # Feature 003: Conditional fallback logic (Table Mode)
            if len(matched_blocks) == 0 and len(area_keyword_item) > 0:
                if len(final_rows) > 0:
                    if area_auto_fallback:
                        # Fallback enabled - use auto_select_mode
                        debug.log(f"[KHAM AREA FALLBACK] area_auto_fallback=true, triggering auto fallback (table)")
                        debug.log(f"[KHAM AREA FALLBACK] Selecting from {len(final_rows)} available rows using mode='{auto_select_mode}'")
                        matched_blocks = final_rows
                    else:
                        # Fallback disabled - strict mode (no selection, will reload)
                        debug.log(f"[KHAM AREA FALLBACK] area_auto_fallback=false, fallback is disabled (table)")
                        debug.log(f"[KHAM AREA SELECT] No area selected, will reload page and retry")
                        return False, False, False  # Return to trigger reload logic
                else:
                    # No available rows (all filtered out or sold out)
                    debug.log(f"[KHAM AREA FALLBACK] No available rows after filtering (table)")
                    return False, False, False

        # Get target and click
        target_row = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

        if debug.enabled:
            if target_row:
                debug.log(f"Target area row selected (mode: {auto_select_mode})")
            else:
                debug.log(f"No target area row selected from {len(matched_blocks) if matched_blocks else 0} matched blocks")

        if target_row:
            # Click target row directly (like Chrome version line 8891)
            # For Kham, the entire row is clickable
            try:
                debug.log(f"Clicking target area row...")
                await target_row.click()
                is_price_assign_by_bot = True
                debug.log("Area row clicked successfully")
            except Exception as exc:
                debug.log(f"Click area row error: {exc}")
        else:
            is_need_refresh = True

    return is_need_refresh, is_price_assign_by_bot, is_keyword_matched

async def nodriver_kham_auto_ocr(tab, config_dict, ocr, away_from_keyboard_enable, previous_answer, model_name):
    """
    Auto OCR captcha recognition
    Reference: chrome_tixcraft.py kham_auto_ocr (line 9426-9530)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("Starting Kham OCR processing...")
    debug.log("away_from_keyboard_enable:", away_from_keyboard_enable)
    debug.log("previous_answer:", previous_answer)

    is_need_redo_ocr = False
    is_form_submitted = False

    ocr_answer = None
    if ocr:
        import time
        ocr_start_time = time.time()

        # Get captcha image using DOMSnapshot (shared with ibon)
        img_base64 = await nodriver_get_captcha_image_from_dom_snapshot(tab, config_dict)

        if img_base64:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                debug.log("OCR classification error:", exc)

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        debug.log(f"OCR elapsed time: {ocr_elapsed_time:.3f}s")
    else:
        debug.log("[KHAM OCR] OCR engine is None")

    if ocr_answer:
        ocr_answer = ocr_answer.strip()
        debug.log(f"[KHAM OCR] OCR answer: {ocr_answer}")

        if len(ocr_answer) == 4:
            # Valid 4-character answer
            previous_answer = ocr_answer  # Update previous_answer to mark as sent
            who_care_var = await nodriver_kham_keyin_captcha_code(tab, answer=ocr_answer, auto_submit=away_from_keyboard_enable)
        else:
            # Invalid length - retry
            if not away_from_keyboard_enable:
                await nodriver_kham_keyin_captcha_code(tab, "")
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    debug.log("[KHAM OCR] Click captcha to refresh")
                    # Refresh captcha image
                    try:
                        await tab.evaluate(f'''
                            (function() {{
                                const img = document.querySelector('#chk_pic');
                                if (img) {{
                                    img.src = '/pic.aspx?TYPE={model_name}&ts=' + new Date().getTime();
                                }}
                            }})();
                        ''')
                        await tab.sleep(0.3)
                    except:
                        pass
    else:
        debug.log(f"[KHAM OCR] OCR answer is None, previous_answer: {previous_answer}")
        if previous_answer is None:
            await nodriver_kham_keyin_captcha_code(tab, "")
        else:
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_submitted

async def nodriver_kham_captcha(tab, config_dict, ocr, model_name):
    """
    Captcha main control with retry logic
    Reference: chrome_tixcraft.py kham_captcha (line 9532-9563)
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    # PS: need 'auto assign seat' feature to enable away_from_keyboard
    away_from_keyboard_enable = False

    is_captcha_sent = False
    previous_answer = None
    last_url = tab.target.url

    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_kham_auto_ocr(
            tab, config_dict, ocr, away_from_keyboard_enable, previous_answer, model_name
        )

        # If captcha found and processed, set flag to True
        if previous_answer is not None:
            is_captcha_sent = True

        if is_form_submitted:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

        current_url = tab.target.url
        if current_url != last_url:
            break

    return is_captcha_sent

async def nodriver_kham_performance(tab, config_dict, ocr, domain_name, model_name):
    """
    Performance page processing - integrate area selection, captcha, and ticket number
    Reference: chrome_tixcraft.py kham_performance (line 9307-9356)
    """
    debug = util.create_debug_logger(config_dict)

    is_price_assign_by_bot = False
    is_captcha_sent = False

    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    debug.log("area_keyword:", area_keyword)

    is_need_refresh = False

    if len(area_keyword) > 0:
        # Parse JSON array keyword
        area_keyword_array = util.parse_keyword_string_to_array(area_keyword)

        # Feature 003: Enhanced fallback logic with early return
        for keyword_index, area_keyword_item in enumerate(area_keyword_array):
            is_need_refresh, is_price_assign_by_bot, is_keyword_matched = await nodriver_kham_area_auto_select(
                tab, domain_name, config_dict, area_keyword_item
            )

            # Check if this is the last keyword
            is_last_keyword = (keyword_index == len(area_keyword_array) - 1)

            # Case 1: True keyword match - stop trying
            if is_keyword_matched:
                debug.log(f"[KHAM PERFORMANCE] Keyword matched: '{area_keyword_item}'")
                break

            # Case 2: Strict mode (area_auto_fallback=false) - only stop if last keyword
            # is_need_refresh=False, is_price_assign_by_bot=False, is_keyword_matched=False
            if not is_need_refresh and not is_price_assign_by_bot:
                if is_last_keyword:
                    # Last keyword failed in strict mode - trigger reload and retry
                    is_need_refresh = True
                    debug.log(f"[KHAM PERFORMANCE] All keywords exhausted, strict mode stops")
                    debug.log(f"[KHAM PERFORMANCE] Will reload page and retry")
                    break
                else:
                    # Not last keyword - continue trying
                    debug.log(f"[KHAM PERFORMANCE] Keyword #{keyword_index + 1} failed (strict mode), trying next...")
                    continue

            # Case 3: Fallback selection - continue trying next keyword
            # is_price_assign_by_bot=True, is_keyword_matched=False
            if is_price_assign_by_bot and not is_keyword_matched:
                debug.log(f"[KHAM PERFORMANCE] Fallback selection, trying next keyword...")
                # Continue to next keyword

            # Case 4: Refresh needed - continue trying next keyword
            # is_need_refresh=True (other scenarios)
            if is_need_refresh:
                debug.log(f"[KHAM PERFORMANCE] Need refresh for keyword: {area_keyword_item}")
                # Continue to next keyword
    else:
        # Empty keyword - match all
        is_need_refresh, is_price_assign_by_bot, is_keyword_matched = await nodriver_kham_area_auto_select(
            tab, domain_name, config_dict, ""
        )

    if is_need_refresh:
        debug.log("is_need_refresh:", is_need_refresh)
        try:
            await tab.reload()
        except:
            pass

    # udn uses reCaptcha, skip for now
    if 'udnfunlife' not in domain_name:
        is_captcha_sent = await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

    return is_price_assign_by_bot, is_captcha_sent

async def nodriver_kham_main(tab, url, config_dict, ocr):
    """
    Main control flow for Kham platform with URL routing
    Reference: chrome_tixcraft.py kham_main (line 9644-9900)
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False
    if not _state:
        _state.update({
            "is_popup_checkout": False,
            "played_sound_order": False,
            "shown_checkout_message": False,
            "udn_quick_buy_submitted": False,
        })

    domain_name = url.split('/')[2]
    debug = util.create_debug_logger(config_dict)

    # Home page handling
    home_url_list = [
        'https://kham.com.tw/',
        'https://kham.com.tw/application/utk01/utk0101_.aspx',
        'https://kham.com.tw/application/utk01/utk0101_03.aspx',
        'https://ticket.com.tw/application/utk01/utk0101_.aspx',
        'https://tickets.udnfunlife.com/application/utk01/utk0101_.aspx'
    ]

    for each_url in home_url_list:
        if each_url == url.lower():
            # Clean popup banners
            try:
                await tab.evaluate('''
                    (function() {
                        const popup = document.querySelector('.popoutBG');
                        if (popup) popup.remove();
                    })();
                ''')
            except:
                pass

            # For UDN login page: execute login first, then redirect after login completes
            # This prevents the infinite redirect loop between login page and event page
            if 'udnfunlife.com' in url.lower():
                udn_account = config_dict["accounts"]["udn_account"]
                udn_password = config_dict["accounts"]["udn_password"].strip()

                if len(udn_account) > 4:
                    # Check if already logged in by looking for logout button or user menu
                    is_logged_in = False
                    try:
                        login_state_raw = await tab.evaluate('''
                            (() => {
                                // Method 1: Check member area login item visibility
                                const memberArea = document.querySelector('.yd_mainNav-member');
                                if (memberArea) {
                                    const subList = memberArea.querySelector('.yd_mainNav-subList');
                                    if (subList) {
                                        const listItems = subList.querySelectorAll('li');
                                        const loginItem = listItems[0];
                                        if (loginItem && window.getComputedStyle(loginItem).display === 'none') {
                                            return { isLoggedIn: true };
                                        }
                                    }
                                }
                                // Method 2: Check for welcome message or user name display
                                const welcomeText = document.body.innerText;
                                if (welcomeText.includes('您好') || welcomeText.includes('登出')) {
                                    return { isLoggedIn: true };
                                }
                                return { isLoggedIn: false };
                            })()
                        ''')
                        login_state = util.parse_nodriver_result(login_state_raw)
                        if isinstance(login_state, dict):
                            is_logged_in = login_state.get('isLoggedIn', False)
                    except Exception as exc:
                        debug.log(f"[UDN LOGIN] Login state check error: {exc}")

                    if is_logged_in:
                        debug.log("[UDN LOGIN] Already logged in, proceeding to redirect...")
                    else:
                        # Not logged in yet - execute login and DON'T redirect
                        # Let the login process complete first
                        debug.log(f"[UDN LOGIN] Not logged in, executing login with account: {udn_account[:3]}***")

                        # Trigger login dialog
                        await tab.evaluate('if(typeof doLoginRWD === "function") doLoginRWD();')
                        await tab.sleep(0.5)

                        # Fill account
                        try:
                            await tab.evaluate(f'''
                                (() => {{
                                    const emailInput = document.getElementById('ID');
                                    if (emailInput && !emailInput.value) {{
                                        emailInput.value = "{udn_account}";
                                        emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    }}
                                }})()
                            ''')
                        except Exception as exc:
                            debug.log(f"[UDN LOGIN] Fill account error: {exc}")

                        # Fill password
                        try:
                            await tab.evaluate(f'''
                                (() => {{
                                    const passInput = document.getElementById('password');
                                    if (passInput && !passInput.value) {{
                                        passInput.value = "{udn_password}";
                                        passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    }}
                                }})()
                            ''')
                        except Exception as exc:
                            debug.log(f"[UDN LOGIN] Fill password error: {exc}")

                        # Click reCAPTCHA checkbox
                        try:
                            recaptcha_clicked = False
                            try:
                                checkboxes = await tab.select_all('.recaptcha-checkbox-border', include_frames=True)
                                if checkboxes and len(checkboxes) > 0:
                                    await checkboxes[0].click()
                                    recaptcha_clicked = True
                                    debug.log("[UDN LOGIN] reCAPTCHA clicked via include_frames")
                            except Exception as e1:
                                debug.log(f"[UDN LOGIN] include_frames method failed: {e1}")

                            if not recaptcha_clicked:
                                try:
                                    recaptcha_pos = await tab.evaluate('''
                                        (() => {
                                            const frame = document.querySelector('iframe[title*="reCAPTCHA"]');
                                            if (frame) {
                                                frame.scrollIntoView({ block: 'center' });
                                                const rect = frame.getBoundingClientRect();
                                                return { x: rect.left + 27, y: rect.top + 30, found: true };
                                            }
                                            return { found: false };
                                        })()
                                    ''')
                                    if isinstance(recaptcha_pos, dict) and recaptcha_pos.get('found'):
                                        x = recaptcha_pos['x']
                                        y = recaptcha_pos['y']
                                        await tab.mouse_click(x, y)
                                        recaptcha_clicked = True
                                        debug.log(f"[UDN LOGIN] reCAPTCHA clicked via mouse_click at ({x}, {y})")
                                except Exception as e2:
                                    debug.log(f"[UDN LOGIN] mouse_click method failed: {e2}")
                        except Exception as exc:
                            debug.log(f"[UDN LOGIN] reCAPTCHA click error: {exc}")

                        debug.log("[UDN LOGIN] Credentials filled, waiting for reCAPTCHA verification...")

                        # DON'T redirect yet - return and let user complete login
                        # Next iteration will check if logged in and redirect then
                        return tab

            # Redirect to target page after login
            config_homepage = config_dict["homepage"]

            # Check if config_homepage is also a home page URL (skip redirect to avoid loop)
            config_homepage_normalized = config_homepage.lower().rstrip('/') if config_homepage else ""
            is_config_homepage_also_home = any(
                config_homepage_normalized == each.rstrip('/')
                for each in home_url_list
            ) or config_homepage_normalized in [
                'https://kham.com.tw',
                'https://ticket.com.tw',
                'https://tickets.udnfunlife.com'
            ]

            # Redirect only if homepage is different AND not a home page URL
            if config_homepage and not is_config_homepage_also_home and config_homepage.lower() != url.lower():
                debug.log(f"[KHAM LOGIN] Redirecting to target: {config_homepage}")
                try:
                    await tab.get(config_homepage)
                    return tab
                except Exception as e:
                    debug.log(f"[KHAM LOGIN] Redirect failed: {e}")
            break

    # Check realname dialog
    await nodriver_kham_check_realname_dialog(tab, config_dict)

    # KHAM UTK0205 seat selection page (graphical seat map with ticket type buttons)
    # Reference: ticket.com.tw logic (line 13561) adapted for KHAM
    if "kham.com.tw" in url and 'utk0205' in url.lower():
        debug.log("Detected KHAM UTK0205 seat selection page")

        is_seat_selection_success = await nodriver_kham_seat_main(tab, config_dict, ocr, domain_name)

        debug.log(f"KHAM seat selection result: {is_seat_selection_success}")

        # Return to avoid double processing by UTK0202/UTK0205 logic below
        return tab

    # UDN UTK0205 seat selection page (Feature 010: UDN seat auto select)
    # UDN shares the same UTK backend system with KHAM, so we reuse KHAM seat selection logic
    # Reference: research.md - DOM structure and selectors are identical
    if "udnfunlife.com" in url and 'utk0205' in url.lower():
        debug.log("[UDN SEAT] Detected UDN UTK0205 seat selection page")

        is_seat_selection_success = await nodriver_kham_seat_main(tab, config_dict, ocr, domain_name)

        if debug.enabled:
            debug.log(f"[UDN SEAT] Seat selection result: {is_seat_selection_success}")
            if is_seat_selection_success:
                debug.log("[SUCCESS] UDN seat selection completed")

        # Return to avoid double processing
        return tab

    # Activity Group page (UTK0201_040.aspx?AGID=)
    # This is a special page format for activity groups with realname requirements
    if 'utk0201_040.aspx?agid=' in url.lower():
        debug.log("Detected KHAM Activity Group page (UTK0201_040)")

        # Check realname dialog
        await nodriver_kham_check_realname_dialog(tab, config_dict)

        # Click buy button
        await nodriver_kham_go_buy_redirect(tab, domain_name)

    # Activity Group Item page (UTK0201_041.aspx?AGID=)
    # This page has "立即訂購" buttons that redirect to UTK0202
    if 'utk0201_041.aspx?agid=' in url.lower():
        debug.log("Detected KHAM Activity Group Item page (UTK0201_041)")

        # Check realname dialog first
        await nodriver_kham_check_realname_dialog(tab, config_dict)

        # Click "立即訂購" button (redirects to UTK0202)
        try:
            click_result = await tab.evaluate('''
                (function() {
                    // Find all "立即訂購" buttons that redirect to UTK0202
                    const buttons = document.querySelectorAll('button.red[onclick*="UTK0202"]');
                    if (buttons.length > 0) {
                        // Click the first available button
                        buttons[0].click();
                        return buttons.length;
                    }
                    return null;
                })();
            ''')
            if click_result:
                debug.log(f"Clicked buy button, total buttons: {click_result}")
        except Exception as exc:
            debug.log(f"Click buy button exception: {exc}")

    # Product page (UTK0201_.aspx?product_id=)
    if 'utk0201_.aspx?product_id=' in url.lower():
        is_event_page = len(url.split('/')) == 6

        if is_event_page:
            # Check realname dialog
            await nodriver_kham_check_realname_dialog(tab, config_dict)

            # Click buy button
            await nodriver_kham_go_buy_redirect(tab, domain_name)
            await tab.sleep(1.0)

            # Check if page changed after clicking buy button
            current_url = tab.target.url
            if 'utk0201_.aspx?product_id=' in current_url.lower():
                # Still on product page - check realname dialog and handle captcha
                await nodriver_kham_check_realname_dialog(tab, config_dict)

                # Handle captcha if enabled
                is_captcha_sent = False
                if config_dict["ocr_captcha"]["enable"]:
                    debug.log("Starting captcha processing for purchase page...")

                    model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK0201"
                    if len(model_name) > 7:
                        model_name = model_name[:7]

                    is_captcha_sent = await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

                if is_captcha_sent:
                    # Set ticket number
                    ticket_number = str(config_dict["ticket_number"])
                    try:
                        await tab.evaluate(f'''
                            (function() {{
                                const amountInput = document.querySelector('#AMOUNT');
                                if (amountInput && (amountInput.value === '' || amountInput.value === '0')) {{
                                    amountInput.value = '{ticket_number}';
                                    amountInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }}
                            }})();
                        ''')
                    except:
                        pass

                    # Click add to cart
                    try:
                        btn_selector = 'button[onclick="addShoppingCart();return false;"]'
                        el_btn = await tab.query_selector(btn_selector)
                        if el_btn:
                            await el_btn.click()
                        else:
                            # Try alternative selector
                            el_btn = await tab.query_selector('#addcart button.red')
                            if el_btn:
                                await el_btn.click()
                    except:
                        pass

    # Date selection page (UTK0201_00.aspx?product_id=)
    if 'utk0201_00.aspx?product_id=' in url.lower():
        is_event_page = len(url.split('/')) == 6

        if is_event_page and config_dict["date_auto_select"]["enable"]:
            await nodriver_kham_product(tab, domain_name, config_dict)

    # UDN specific handling
    if 'udnfunlife' in domain_name:
        # UDN homepage login (popup dialog with reCAPTCHA)
        # UDN uses a popup login dialog on homepage, not UTK1306 page
        if 'utk01/utk0101_.aspx' in url.lower():
            udn_account = config_dict["accounts"]["udn_account"]
            udn_password = config_dict["accounts"]["udn_password"].strip()
            if len(udn_account) > 4:
                # Check if already logged in
                # Detection method: Check if "登入/註冊" menu item is hidden
                # When logged in: "登入/註冊" is display:none, "登出" is visible
                # When not logged in: "登入/註冊" is visible, "登出" is display:none
                is_logged_in = False
                try:
                    login_state_raw = await tab.evaluate('''
                        (() => {
                            const memberArea = document.querySelector('.yd_mainNav-member');
                            if (!memberArea) return { loginItemHidden: false };
                            const subList = memberArea.querySelector('.yd_mainNav-subList');
                            if (!subList) return { loginItemHidden: false };
                            const listItems = subList.querySelectorAll('li');
                            // First item is "登入/註冊", check if it's hidden
                            const loginItem = listItems[0];
                            const loginItemHidden = loginItem && window.getComputedStyle(loginItem).display === 'none';
                            return { loginItemHidden: loginItemHidden };
                        })()
                    ''')
                    # Use util.parse_nodriver_result to handle nodriver's special return format
                    login_state = util.parse_nodriver_result(login_state_raw)
                    if isinstance(login_state, dict):
                        # User is logged in if "登入/註冊" item is hidden
                        is_logged_in = login_state.get('loginItemHidden', False)
                except Exception as exc:
                    debug.log(f"[UDN LOGIN] Login state check error: {exc}")

                if not is_logged_in:
                    debug.log(f"[UDN LOGIN] Starting login with account: {udn_account[:3]}***")

                    # Trigger login dialog
                    await tab.evaluate('if(typeof doLoginRWD === "function") doLoginRWD();')
                    await tab.sleep(0.5)

                    # Fill account
                    try:
                        await tab.evaluate(f'''
                            (() => {{
                                const emailInput = document.getElementById('ID');
                                if (emailInput && !emailInput.value) {{
                                    emailInput.value = "{udn_account}";
                                    emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}
                            }})()
                        ''')
                    except Exception as exc:
                        debug.log(f"[UDN LOGIN] Fill account error: {exc}")

                    # Fill password
                    try:
                        await tab.evaluate(f'''
                            (() => {{
                                const passInput = document.getElementById('password');
                                if (passInput && !passInput.value) {{
                                    passInput.value = "{udn_password}";
                                    passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}
                            }})()
                        ''')
                    except Exception as exc:
                        debug.log(f"[UDN LOGIN] Fill password error: {exc}")

                    # Click reCAPTCHA checkbox
                    try:
                        recaptcha_clicked = False

                        # Method 1: Use nodriver's include_frames to find checkbox inside iframe
                        try:
                            checkboxes = await tab.select_all('.recaptcha-checkbox-border', include_frames=True)
                            if checkboxes and len(checkboxes) > 0:
                                await checkboxes[0].click()
                                recaptcha_clicked = True
                                debug.log("[UDN LOGIN] reCAPTCHA clicked via include_frames")
                        except Exception as e1:
                            debug.log(f"[UDN LOGIN] include_frames method failed: {e1}")

                        # Method 2: Fallback to CDP mouse event
                        if not recaptcha_clicked:
                            try:
                                recaptcha_pos = await tab.evaluate('''
                                    (() => {
                                        const frame = document.querySelector('iframe[title*="reCAPTCHA"]');
                                        if (frame) {
                                            frame.scrollIntoView({ block: 'center' });
                                            const rect = frame.getBoundingClientRect();
                                            return { x: rect.left + 27, y: rect.top + 30, found: true };
                                        }
                                        return { found: false };
                                    })()
                                ''')

                                if isinstance(recaptcha_pos, dict) and recaptcha_pos.get('found'):
                                    x = recaptcha_pos['x']
                                    y = recaptcha_pos['y']
                                    await tab.mouse_click(x, y)
                                    recaptcha_clicked = True
                                    debug.log(f"[UDN LOGIN] reCAPTCHA clicked via mouse_click at ({x}, {y})")
                            except Exception as e2:
                                debug.log(f"[UDN LOGIN] mouse_click method failed: {e2}")

                        if not recaptcha_clicked:
                            debug.log("[UDN LOGIN] reCAPTCHA checkbox not found")
                    except Exception as exc:
                        debug.log(f"[UDN LOGIN] reCAPTCHA click error: {exc}")

                    # After filling credentials and clicking reCAPTCHA, stop here
                    # User needs to complete reCAPTCHA verification and click login manually
                    # The bot will check login status on next iteration
                    debug.log("[UDN LOGIN] Credentials filled, waiting for user to complete reCAPTCHA and login...")

        # UDN ticket selection (UTK0203 date/session selection)
        if 'utk0203_.aspx?product_id=' in url.lower():
            # Try layout format 1
            try:
                ticket_input = await tab.query_selector('input.yd_counterNum')
                if ticket_input:
                    await tab.evaluate(f'''
                        (function() {{
                            const input = document.querySelector('input.yd_counterNum');
                            if (input && input.value === '0') {{
                                input.value = '{config_dict["ticket_number"]}';
                            }}
                        }})();
                    ''')
                    btn_next = await tab.query_selector('#buttonNext')
                    if btn_next:
                        await btn_next.click()
                else:
                    # Layout format 2 - use date selection
                    if config_dict["date_auto_select"]["enable"]:
                        await nodriver_kham_product(tab, domain_name, config_dict)
            except:
                pass

        # UDN UTK0204 area selection page (Feature 010: UDN area auto select)
        # URL pattern: .aspx?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx (without PERFORMANCE_PRICE_AREA_ID)
        # This page shows available ticket areas for selection
        # Note: UTK0204 combines area selection and seat map on the same page
        if '.aspx?performance_id=' in url.lower() and 'product_id=' in url.lower():
            # Exclude seat selection page (UTK0205) which has PERFORMANCE_PRICE_AREA_ID
            if 'performance_price_area_id=' not in url.lower():
                debug.log("[UDN AREA] Detected UDN UTK0204 area selection page")

                if config_dict["area_auto_select"]["enable"]:
                    # UDN uses nodriver_kham_performance for area selection
                    # UDN selector: table.status > tbody > tr.status_tr (verified via MCP)
                    model_name = "UTK0204"

                    is_price_assign_by_bot, is_captcha_sent = await nodriver_kham_performance(
                        tab, config_dict, ocr, domain_name, model_name
                    )

                    debug.log(f"[UDN AREA] Area selection result: is_price_assign_by_bot={is_price_assign_by_bot}")

                    # Feature 010: UDN seat auto select
                    # After area selection, seat map may appear on the same page
                    # Check for seat map and perform seat selection if available
                    if is_price_assign_by_bot:
                        await tab.sleep(0.5)  # Wait for seat map to load
                        is_seat_success = await nodriver_udn_seat_main(tab, config_dict)
                        if debug.enabled:
                            debug.log(f"[UDN SEAT] Seat selection result: {is_seat_success}")
                            if is_seat_success:
                                debug.log("[SUCCESS] UDN seat selection and add to cart completed")

        # UDN UTK0222_02 fast purchase page (Feature 010: UDN quick buy)
        # URL pattern: UTK0222_02.aspx?PRODUCT_ID=xxx
        # This page shows: 1) Date selection 2) Performance selection 3) Area selection
        if 'utk0222_02.aspx' in url.lower():
            # Skip if quick buy was already submitted (waiting for navigation)
            if _state.get("udn_quick_buy_submitted", False):
                return tab

            debug.log("[UDN QUICK BUY] Detected UTK0222_02 fast purchase page")

            try:
                # Step 1: Date selection (li.yd_datedBtn)
                if config_dict["date_auto_select"]["enable"]:
                    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()

                    date_result_raw = await tab.evaluate('''
                        (() => {
                            const dateBtns = document.querySelectorAll('li.yd_datedBtn');
                            const dates = [];
                            dateBtns.forEach((btn, idx) => {
                                dates.push({
                                    index: idx,
                                    text: btn.textContent.trim()
                                });
                            });
                            return { dates: dates, count: dates.length };
                        })()
                    ''')
                    date_result = util.parse_nodriver_result(date_result_raw)

                    if isinstance(date_result, dict) and date_result.get('count', 0) > 0:
                        dates = date_result.get('dates', [])
                        target_date_idx = None  # None means no match yet
                        keyword_matched = False

                        # Match date keyword (use JSON parsing like other platforms)
                        if date_keyword:
                            keywords = util.parse_keyword_string_to_array(date_keyword)

                            debug.log(f"[UDN QUICK BUY] Date keywords parsed: {keywords}")

                            for i, date_item in enumerate(dates):
                                date_text = date_item.get('text', '')
                                for kw in keywords:
                                    # Support AND logic (space-separated keywords)
                                    kw_parts = kw.split(' ') if ' ' in kw else [kw]
                                    all_match = all(part in date_text for part in kw_parts)
                                    if all_match:
                                        target_date_idx = i
                                        keyword_matched = True
                                        debug.log(f"[UDN QUICK BUY] Date matched: {date_text} with keyword: {kw}")
                                        break
                                if keyword_matched:
                                    break  # Early return when matched

                        # Fallback logic based on date_auto_fallback and mode
                        if not keyword_matched:
                            date_auto_fallback = config_dict.get("date_auto_fallback", False)
                            date_mode = config_dict["date_auto_select"].get("mode", "from top to bottom")

                            if date_auto_fallback:
                                debug.log(f"[UDN QUICK BUY] Date keyword not matched, fallback with mode: {date_mode}")

                                target_date_idx = util.get_target_index_by_mode(len(dates), date_mode)

                                if debug.enabled:
                                    selected_date = dates[target_date_idx].get('text', '') if target_date_idx is not None and target_date_idx < len(dates) else ''
                                    debug.log(f"[UDN QUICK BUY] Fallback selected date: {selected_date} (index: {target_date_idx})")
                            else:
                                # Strict mode: no fallback, use first date as default
                                target_date_idx = 0
                                debug.log(f"[UDN QUICK BUY] Fallback disabled, using first date")

                        # Click the date button
                        await tab.evaluate(f'''
                            (() => {{
                                const dateBtns = document.querySelectorAll('li.yd_datedBtn');
                                if (dateBtns[{target_date_idx}]) {{
                                    dateBtns[{target_date_idx}].click();
                                }}
                            }})()
                        ''')
                        await tab.sleep(0.3)

                # Step 2: Performance/Session selection (div.sd-btn.bg--gray)
                if config_dict["date_auto_select"]["enable"]:
                    perf_result_raw = await tab.evaluate('''
                        (() => {
                            const perfBtns = document.querySelectorAll('div.sd-btn.bg--gray');
                            const perfs = [];
                            perfBtns.forEach((btn, idx) => {
                                perfs.push({
                                    index: idx,
                                    text: btn.textContent.trim().replace(/\\s+/g, ' '),
                                    isActive: btn.classList.contains('active')
                                });
                            });
                            return { perfs: perfs, count: perfs.length };
                        })()
                    ''')
                    perf_result = util.parse_nodriver_result(perf_result_raw)

                    if isinstance(perf_result, dict) and perf_result.get('count', 0) > 0:
                        perfs = perf_result.get('perfs', [])
                        target_perf_idx = None  # None means no match yet
                        keyword_matched = False

                        # Check if any is already active
                        has_active = any(p.get('isActive') for p in perfs)

                        # Match performance keyword (use date_keyword for time/venue matching)
                        if date_keyword and not has_active:
                            keywords = util.parse_keyword_string_to_array(date_keyword)

                            for i, perf_item in enumerate(perfs):
                                perf_text = perf_item.get('text', '')
                                for kw in keywords:
                                    # Support AND logic (space-separated keywords)
                                    kw_parts = kw.split(' ') if ' ' in kw else [kw]
                                    all_match = all(part in perf_text for part in kw_parts)
                                    if all_match:
                                        target_perf_idx = i
                                        keyword_matched = True
                                        debug.log(f"[UDN QUICK BUY] Performance matched: {perf_text} with keyword: {kw}")
                                        break
                                if keyword_matched:
                                    break  # Early return when matched

                        # Fallback logic based on date_auto_fallback and mode
                        if not keyword_matched and not has_active:
                            date_auto_fallback = config_dict.get("date_auto_fallback", False)
                            date_mode = config_dict["date_auto_select"].get("mode", "from top to bottom")

                            if date_auto_fallback:
                                debug.log(f"[UDN QUICK BUY] Performance keyword not matched, fallback with mode: {date_mode}")

                                target_perf_idx = util.get_target_index_by_mode(len(perfs), date_mode)

                                if debug.enabled:
                                    selected_perf = perfs[target_perf_idx].get('text', '') if target_perf_idx is not None and target_perf_idx < len(perfs) else ''
                                    debug.log(f"[UDN QUICK BUY] Fallback selected performance: {selected_perf}")
                            else:
                                # Strict mode: default to first
                                target_perf_idx = 0

                        # Click the performance button if not already active
                        if not has_active and target_perf_idx is not None:
                            await tab.evaluate(f'''
                                (() => {{
                                    const perfBtns = document.querySelectorAll('div.sd-btn.bg--gray');
                                    if (perfBtns[{target_perf_idx}]) {{
                                        perfBtns[{target_perf_idx}].click();
                                    }}
                                }})()
                            ''')
                            await tab.sleep(0.3)

                # Step 3: Area selection
                # Get area keywords from config
                area_keyword = config_dict["area_auto_select"]["area_keyword"].strip() if config_dict["area_auto_select"]["enable"] else ""

                # Find all ticket rows from VISIBLE tables only
                # Each performance has its own table, controlled by parent .sd-target display
                ticket_info_raw = await tab.evaluate('''
                    (() => {
                        const tables = document.querySelectorAll('table.yd_ticketsTable');
                        const tickets = [];
                        tables.forEach((table) => {
                            // Check if this table's parent container is visible
                            let parent = table.parentElement;
                            let isVisible = true;
                            for (let i = 0; i < 5 && parent; i++) {
                                if (window.getComputedStyle(parent).display === 'none') {
                                    isVisible = false;
                                    break;
                                }
                                parent = parent.parentElement;
                            }
                            if (!isVisible) return;

                            // Get ticket rows from visible table
                            const rows = table.querySelectorAll('tr.main');
                            rows.forEach((row, idx) => {
                                const cells = row.querySelectorAll('td');
                                if (cells.length >= 5) {
                                    const areaName = cells[1] ? cells[1].textContent.trim() : '';
                                    const ticketType = cells[2] ? cells[2].textContent.trim() : '';
                                    const price = cells[3] ? cells[3].textContent.trim() : '';
                                    const buyBtn = cells[4] ? cells[4].querySelector('.yd_btn--link') : null;
                                    const fastcode = buyBtn ? buyBtn.getAttribute('fastcode') : null;
                                    const isDisabled = buyBtn ? buyBtn.style.cursor === 'default' : true;
                                    tickets.push({
                                        index: idx,
                                        areaName: areaName,
                                        ticketType: ticketType,
                                        price: price,
                                        fastcode: fastcode,
                                        isDisabled: isDisabled
                                    });
                                }
                            });
                        });
                        return { tickets: tickets };
                    })()
                ''')
                ticket_info = util.parse_nodriver_result(ticket_info_raw)

                if isinstance(ticket_info, dict) and 'tickets' in ticket_info:
                    tickets = ticket_info['tickets']
                    debug.log(f"[UDN QUICK BUY] Found {len(tickets)} ticket areas")

                    # Find matching area based on keyword (use JSON parsing like other platforms)
                    target_ticket = None
                    if area_keyword:
                        keywords = util.parse_keyword_string_to_array(area_keyword)

                        debug.log(f"[UDN QUICK BUY] Area keywords parsed: {keywords}")

                        # Get keyword_exclude for filtering
                        keyword_exclude = config_dict.get("keyword_exclude", "")

                        for kw in keywords:
                            if target_ticket:
                                break  # Early return when matched

                            # Support AND logic (space-separated keywords)
                            kw_parts = kw.split(' ') if ' ' in kw else [kw]

                            for ticket in tickets:
                                if ticket.get('isDisabled'):
                                    continue
                                area_name = ticket.get('areaName', '')

                                # Apply keyword_exclude filter
                                if keyword_exclude and util.reset_row_text_if_match_keyword_exclude(config_dict, area_name):
                                    debug.log(f"[UDN QUICK BUY] Excluded by keyword_exclude: {area_name}")
                                    continue

                                # Check AND logic - all parts must match
                                all_match = all(part in area_name for part in kw_parts)
                                if all_match:
                                    target_ticket = ticket
                                    debug.log(f"[UDN QUICK BUY] Matched area: {area_name} with keyword: {kw}")
                                    break

                    # If no keyword match, apply fallback logic based on area_auto_fallback and mode
                    if not target_ticket:
                        area_auto_fallback = config_dict.get("area_auto_fallback", False)
                        area_mode = config_dict["area_auto_select"].get("mode", "from top to bottom")

                        if area_auto_fallback:
                            # Filter available tickets (not disabled, has fastcode, respecting keyword_exclude)
                            available_tickets = []
                            keyword_exclude = config_dict.get("keyword_exclude", "")
                            for ticket in tickets:
                                if ticket.get('isDisabled') or not ticket.get('fastcode'):
                                    continue
                                area_name = ticket.get('areaName', '')
                                if keyword_exclude and util.reset_row_text_if_match_keyword_exclude(config_dict, area_name):
                                    continue
                                available_tickets.append(ticket)

                            if available_tickets:
                                debug.log(f"[UDN QUICK BUY] No keyword match, fallback with mode: {area_mode}")

                                target_ticket = util.get_target_item_from_matched_list(available_tickets, area_mode)

                                if target_ticket:
                                    debug.log(f"[UDN QUICK BUY] Fallback selected area: {target_ticket.get('areaName')}")
                        else:
                            # Strict mode: no fallback, don't select anything
                            debug.log(f"[UDN QUICK BUY] No keyword match, fallback disabled, waiting for manual selection")

                    # Click the buy button
                    if target_ticket and target_ticket.get('fastcode'):
                        fastcode = target_ticket['fastcode']
                        debug.log(f"[UDN QUICK BUY] Clicking buy button for area: {target_ticket.get('areaName')}, fastcode: {fastcode}")

                        await tab.evaluate(f'''
                            (() => {{
                                const btn = document.querySelector('.yd_btn--link[fastcode="{fastcode}"]');
                                if (btn && btn.style.cursor !== 'default') {{
                                    btn.click();
                                }}
                            }})()
                        ''')

                        # Step 4: Handle quantity selection dialog
                        # After clicking "立即購票", a lightbox appears with quantity input
                        # Wait for lightbox with retry
                        ticket_number = config_dict.get("ticket_number", 2)
                        lightbox_found = False

                        for retry in range(5):  # Retry up to 5 times (total 2.5s max)
                            await tab.sleep(0.5)

                            qty_set_raw = await tab.evaluate(f'''
                                (() => {{
                                    const activeLightbox = document.querySelector('.yd_lightbox.active');
                                    if (!activeLightbox) return {{ success: false, reason: 'no_lightbox' }};

                                    const qtyInput = activeLightbox.querySelector('#QRY2, .yd_counterNum');
                                    if (!qtyInput) return {{ success: false, reason: 'no_qty_input' }};

                                    // Get max limit
                                    const maxLimit = parseInt(qtyInput.getAttribute('perflimit') || '4');
                                    const targetQty = Math.min({ticket_number}, maxLimit);

                                    // Set quantity
                                    qtyInput.value = targetQty;
                                    qtyInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    qtyInput.dispatchEvent(new Event('change', {{ bubbles: true }}));

                                    return {{ success: true, qty: targetQty, max: maxLimit }};
                                }})()
                            ''')
                            qty_set = util.parse_nodriver_result(qty_set_raw)

                            if isinstance(qty_set, dict) and qty_set.get('success'):
                                lightbox_found = True
                                debug.log(f"[UDN QUICK BUY] Set quantity to {qty_set.get('qty')} (max: {qty_set.get('max')})")

                                await tab.sleep(0.3)

                                # Click the "快速訂購" button
                                await tab.evaluate('''
                                    (() => {
                                        const activeLightbox = document.querySelector('.yd_lightbox.active');
                                        if (!activeLightbox) return;
                                        const submitBtn = activeLightbox.querySelector('#f_btn, input[value="快速訂購"], button.yd_btn--primary');
                                        if (submitBtn) {
                                            submitBtn.click();
                                        }
                                    })()
                                ''')

                                # Mark as submitted to prevent duplicate processing
                                _state["udn_quick_buy_submitted"] = True

                                debug.log("[UDN QUICK BUY] Clicked submit button, waiting for navigation...")

                                # Wait for navigation to checkout page
                                for nav_wait in range(10):  # Wait up to 5 seconds for navigation
                                    await tab.sleep(0.5)
                                    current_url = str(tab.target.url).lower()
                                    if 'utk0206' in current_url:
                                        debug.log("[UDN QUICK BUY] Successfully navigated to checkout page")
                                        break
                                break  # Exit retry loop after successful submit
                            else:
                                if retry == 4:  # Only print on last retry
                                    debug.log(f"[UDN QUICK BUY] Failed to set quantity after retries: {qty_set}")
                    else:
                        debug.log("[UDN QUICK BUY] No available ticket area found")

            except Exception as exc:
                debug.log(f"[UDN QUICK BUY] Error: {exc}")

    else:
        # Kham / Ticket.com.tw handling
        # Performance page (.aspx?performance_id= & product_id=)
        # Exclude Activity Group pages (handled separately above)
        if '.aspx?performance_id=' in url.lower() and 'product_id=' in url.lower() and 'activity_group_id=' not in url.lower():
            model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK0204"
            if len(model_name) > 7:
                model_name = model_name[:7]

            # Check realname dialog
            await nodriver_kham_check_realname_dialog(tab, config_dict)

            # Check captcha error
            if config_dict["ocr_captcha"]["enable"]:
                is_reset = await nodriver_kham_check_captcha_text_error(tab, config_dict)
                if is_reset:
                    await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

            # Close dialog buttons (ticket.com.tw uses retry mechanism)
            if "ticket.com.tw" in url:
                await nodriver_ticket_close_dialog_with_retry(tab, config_dict)
            else:
                try:
                    el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
                    if el_btn:
                        await el_btn.click()
                except:
                    pass

            if config_dict["area_auto_select"]["enable"]:
                # Switch to auto seat
                if "ticket.com.tw" in url:
                    # Ticket.com.tw uses different selector
                    await nodriver_ticket_switch_to_auto_seat(tab)
                else:
                    await nodriver_kham_switch_to_auto_seat(tab)

                # Clean sold out rows (kham specific)
                if "kham.com.tw" in url:
                    try:
                        await tab.evaluate('''
                            (function() {
                                const soldoutRows = document.querySelectorAll('tr.Soldout');
                                soldoutRows.forEach(row => row.remove());

                                const ticketItems = document.querySelectorAll('tr.status_tr');
                                if (ticketItems.length === 0) {
                                    location.reload();
                                }
                            })();
                        ''')
                    except:
                        pass

                # Area selection and captcha
                is_price_assign_by_bot, is_captcha_sent = await nodriver_kham_performance(
                    tab, config_dict, ocr, domain_name, model_name
                )

                # Set ticket number
                if "ticket.com.tw" in url:
                    select_query = 'div.qty-select input[type="text"]'
                else:
                    select_query = '#AMOUNT'

                try:
                    await tab.evaluate(f'''
                        (function() {{
                            const input = document.querySelector('{select_query}');
                            if (input && (input.value === '' || input.value === '0')) {{
                                input.value = '{config_dict["ticket_number"]}';
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        }})();
                    ''')
                except:
                    pass

                # Check adjacent seat checkbox
                if config_dict["advanced"]["disable_adjacent_seat"]:
                    if "ticket.com.tw" in url:
                        await nodriver_ticket_allow_not_adjacent_seat(tab, config_dict)
                    if "kham.com.tw" in url:
                        await nodriver_kham_allow_not_adjacent_seat(tab, config_dict)

                # Submit if captcha sent
                if is_captcha_sent:
                    try:
                        if "ticket.com.tw" in url:
                            # ticket.com.tw uses <input type="submit"> with id ending in AddShopingCart
                            debug.log("[SUBMIT] Searching for ticket.com.tw submit button...")
                            el_btn = await tab.query_selector('input[id$="AddShopingCart"]')
                            if not el_btn:
                                # Fallback to <a> tag (for other possible layouts)
                                el_btn = await tab.query_selector('a[onclick="return chkCart();"]')
                        elif "orders.ibon.com.tw" in url:
                            # ibon uses <a> tag with id containing AddShopingCart
                            debug.log("[SUBMIT] Searching for ibon submit button...")
                            el_btn = await tab.query_selector('a[id*="AddShopingCart"]')
                            if not el_btn:
                                # Fallback to generic button
                                el_btn = await tab.query_selector('a.btn.btn-primary.btn-block')
                        else:
                            # Kham
                            debug.log("[SUBMIT] Searching for Kham submit button...")
                            el_btn = await tab.query_selector('button[onclick="addShoppingCart();return false;"]')

                        if el_btn:
                            debug.log("[SUBMIT] Submit button found, scrolling into view...")
                            # Scroll button into view first (important for CDP click)
                            try:
                                await el_btn.scroll_into_view()
                                await tab.sleep(0.3)
                            except:
                                pass

                            debug.log("[SUBMIT] Clicking using CDP native click...")
                            # Use NoDriver CDP native click
                            await el_btn.click()
                            debug.log("[SUBMIT] Add shopping cart button clicked successfully!")

                            dialog_result = await _handle_post_submit_dialog(tab, config_dict)

                            if dialog_result == "success":
                                debug.log("[SUBMIT] Waiting for page transition after success...")
                                await tab.sleep(1.0)

                                current_url = tab.target.url
                                url_changed = False
                                for i in range(60):  # 60 * 0.5s = 30s
                                    await tab.sleep(0.5)
                                    new_url = tab.target.url
                                    if new_url != current_url:
                                        debug.log(f"[SUBMIT] Page transitioned to {new_url}")
                                        url_changed = True
                                        break

                                if not url_changed:
                                    debug.log("[SUBMIT] CRITICAL: Success dialog but URL never changed after 30s")
                                    await tab.sleep(5.0)

                            elif dialog_result == "error":
                                debug.log("[SUBMIT] Will retry with new captcha")
                                await tab.sleep(2.0)

                            else:
                                current_url = tab.target.url
                                for i in range(10):  # 10 * 0.5s = 5s
                                    await tab.sleep(0.5)
                                    new_url = tab.target.url
                                    if new_url != current_url:
                                        debug.log(f"[SUBMIT] Page transitioned to {new_url}")
                                        break
                        else:
                            debug.log("[SUBMIT] Add shopping cart button not found")
                    except Exception as exc:
                        debug.log(f"[SUBMIT] Click chkCart/addShoppingCart button fail: {exc}")

        # Ticket.com.tw UTK0205 seat selection page (graphical seat map)
        # Reference: chrome_tixcraft.py line 9884-9892
        if "ticket.com.tw" in url and 'utk0205' in url.lower():
            debug.log("Detected ticket.com.tw UTK0205 seat selection page")

            is_seat_selection_success = await nodriver_ticket_seat_main(tab, config_dict, ocr, domain_name)

            debug.log(f"Seat selection result: {is_seat_selection_success}")

        # UTK0202 page - Activity Group ticket selection (new format)
        # URL: UTK0202_.aspx?PERFORMANCE_ID=xxx&PRODUCT_ID=xxx&ACTIVITY_GROUP_ID=xxx&ACTIVITY_GROUP_ITEM_ID=xxx
        if '.aspx?performance_id=' in url.lower() and 'activity_group_id=' in url.lower():
            model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK0202"
            if len(model_name) > 7:
                model_name = model_name[:7]

            debug.log(f"Detected UTK0202 Activity Group ticket page, model: {model_name}")

            # Check realname dialog
            await nodriver_kham_check_realname_dialog(tab, config_dict)

            # Handle captcha if enabled
            is_captcha_sent = False
            if config_dict["ocr_captcha"]["enable"]:
                is_captcha_sent = await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

            if is_captcha_sent:
                # Set ticket number by clicking + button
                ticket_number = int(config_dict["ticket_number"])
                try:
                    # Click + button N times to set ticket number
                    set_result = await tab.evaluate(f'''
                        (function() {{
                            // Try multiple selectors for + button
                            let plusBtn = document.querySelector('button.plus');
                            if (!plusBtn) {{
                                plusBtn = document.querySelector('button[onclick*="opera1"][onclick*="true"]');
                            }}
                            if (!plusBtn) {{
                                // Try by text content
                                const buttons = document.querySelectorAll('button');
                                for (let btn of buttons) {{
                                    if (btn.textContent.trim() === '+') {{
                                        plusBtn = btn;
                                        break;
                                    }}
                                }}
                            }}

                            if (plusBtn) {{
                                for (let i = 0; i < {ticket_number}; i++) {{
                                    plusBtn.click();
                                }}
                                const amountInput = document.querySelector('#AMOUNT');
                                return amountInput ? amountInput.value : '{ticket_number}';
                            }}

                            // Fallback: directly set input value
                            const amountInput = document.querySelector('#AMOUNT');
                            if (amountInput) {{
                                amountInput.value = '{ticket_number}';
                                amountInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                amountInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                if (typeof checkNum === 'function') {{
                                    checkNum(amountInput);
                                }}
                                return amountInput.value + ' (fallback)';
                            }}
                            return null;
                        }})();
                    ''')
                    debug.log(f"Ticket number set to: {set_result}")
                except Exception as exc:
                    debug.log(f"Set ticket number error: {exc}")

                # Click add to cart
                try:
                    btn_selector = 'button[onclick="addShoppingCart();return false;"]'
                    el_btn = await tab.query_selector(btn_selector)
                    if el_btn:
                        await el_btn.click()
                        debug.log("Clicked add to cart button")
                    else:
                        # Try alternative selector
                        el_btn = await tab.query_selector('#addcart button.red')
                        if el_btn:
                            await el_btn.click()
                            debug.log("Clicked add to cart button (alt)")
                except:
                    pass

        # UTK0202/UTK0205 page - Ticket number selection page
        # URL: UTK0202_.aspx?PERFORMANCE_ID=xxx&PERFORMANCE_PRICE_AREA_ID=xxx
        # Reference: chrome_tixcraft.py line 9895-9941
        if '.aspx?performance_id=' in url.lower() and 'performance_price_area_id=' in url.lower():
            model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK0202"
            if len(model_name) > 7:
                model_name = model_name[:7]

            debug.log(f"Detected UTK0202/UTK0205 ticket number selection page, model: {model_name}")

            is_captcha_sent = False

            # Check captcha error dialog FIRST (before checking filled state).
            # An error dialog means the server has refreshed the captcha image,
            # so the old value in the input field is stale and must be cleared.
            if config_dict["ocr_captcha"]["enable"]:
                is_reset = await nodriver_kham_check_captcha_text_error(tab, config_dict)
                if is_reset:
                    is_captcha_sent = await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

            # Then check if captcha is already filled (from previous page or above OCR)
            if config_dict["ocr_captcha"]["enable"] and not is_captcha_sent:
                try:
                    captcha_value = await tab.evaluate('''
                        (function() {
                            const input = document.querySelector('input[value="驗證碼"]') ||
                                        document.querySelector('input[placeholder="驗證碼"]') ||
                                        document.querySelector('input[placeholder="請輸入圖片上符號"]') ||
                                        document.querySelector('input[type="text"][maxlength="4"]');
                            return input ? input.value : null;
                        })();
                    ''')
                    if captcha_value and len(captcha_value) == 4 and captcha_value != "驗證碼":
                        is_captcha_sent = True
                        debug.log(f"[CAPTCHA] Already filled: {captcha_value}")
                except:
                    pass

            # Check adjacent seat checkbox
            if config_dict["advanced"]["disable_adjacent_seat"]:
                if "ticket.com.tw" in url:
                    await nodriver_ticket_allow_not_adjacent_seat(tab, config_dict)
                else:
                    await nodriver_kham_allow_not_adjacent_seat(tab, config_dict)

            # Close dialog buttons (ticket.com.tw uses retry mechanism)
            if "ticket.com.tw" in url:
                await nodriver_ticket_close_dialog_with_retry(tab, config_dict)
            else:
                try:
                    el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
                    if el_btn:
                        await el_btn.click()
                except:
                    pass

            # Handle captcha only if not already sent
            if config_dict["ocr_captcha"]["enable"] and not is_captcha_sent:
                is_captcha_sent = await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

            # Set ticket number
            # For Kham UTK0202 page, there may be multiple ticket types (原價, 身心障礙票, etc.)
            # We need to select the correct input based on ticket type name
            if "ticket.com.tw" in url:
                select_query = 'div.qty-select input[type="text"]'
                try:
                    await tab.evaluate(f'''
                        (function() {{
                            const input = document.querySelector('{select_query}');
                            if (input && (input.value === '' || input.value === '0')) {{
                                input.value = '{config_dict["ticket_number"]}';
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        }})();
                    ''')
                    debug.log(f"Ticket number set to: {config_dict['ticket_number']}")
                except Exception as exc:
                    debug.log(f"Set ticket number error: {exc}")
            elif "orders.ibon.com.tw" in url:
                # ibon - uses SELECT dropdown for ticket number
                select_query = 'select[id*="AMOUNT_DDL"]'
                try:
                    await tab.evaluate(f'''
                        (function() {{
                            const select = document.querySelector('{select_query}');
                            if (select) {{
                                const targetValue = '{config_dict["ticket_number"]}';
                                // Check if option exists
                                const option = Array.from(select.options).find(opt => opt.value === targetValue);
                                if (option) {{
                                    select.value = targetValue;
                                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    console.log('[IBON TICKET] Set to: ' + targetValue);
                                    return true;
                                }} else {{
                                    console.log('[IBON TICKET] Target value not available: ' + targetValue);
                                    return false;
                                }}
                            }}
                            console.log('[IBON TICKET] SELECT not found');
                            return false;
                        }})();
                    ''')
                    debug.log(f"[IBON TICKET] Ticket number set to: {config_dict['ticket_number']}")
                except Exception as exc:
                    debug.log(f"[IBON TICKET] Set ticket number error: {exc}")
            else:
                # Kham - find the correct ticket type input using pure JavaScript
                try:
                    # Build exclude keywords list for JavaScript
                    exclude_keywords = []
                    if "keyword_exclude" in config_dict:
                        keyword_exclude_str = config_dict["keyword_exclude"].strip()
                        try:
                            # Try JSON format first (standard storage format)
                            # Example: "\"輪椅\",\"身障\"" → ["輪椅", "身障"]
                            exclude_keywords = json.loads("[" + keyword_exclude_str + "]")
                        except:
                            # Fallback: semicolon-separated format (Issue #23)
                            if util.CONST_KEYWORD_DELIMITER in keyword_exclude_str:
                                exclude_keywords = [k.strip() for k in keyword_exclude_str.split(util.CONST_KEYWORD_DELIMITER) if k.strip()]
                            else:
                                # Single keyword
                                exclude_keywords = [keyword_exclude_str] if keyword_exclude_str else []

                    exclude_keywords_json = json.dumps(exclude_keywords)

                    # Execute all logic in JavaScript to avoid DOM element passing issues
                    result = await tab.evaluate(f'''
                        (function() {{
                            const ticketNumber = '{config_dict["ticket_number"]}';
                            const excludeKeywords = {exclude_keywords_json};

                            // Get all ticket type inputs
                            const inputs = document.querySelectorAll('input.numbox[type="number"][id="AMOUNT"]');
                            console.log('[TICKET] Found ' + inputs.length + ' ticket type inputs');

                            if (inputs.length === 0) {{
                                return {{ success: false, message: 'No ticket inputs found' }};
                            }}

                            // Find the first non-excluded ticket type
                            for (let i = 0; i < inputs.length; i++) {{
                                const input = inputs[i];
                                const key = input.getAttribute('key');

                                    if (!key) continue;

                                    // Get ticket type name
                                const nameInput = document.getElementById(key + '_NAME');
                                const typeName = nameInput ? nameInput.value : '';

                                    console.log('[TICKET] Type: ' + typeName + ' (key: ' + key + ')');

                                    // Check exclude keywords
                                let excluded = false;
                                if (typeName && excludeKeywords.length > 0) {{
                                        const lowerTypeName = typeName.toLowerCase();
                                    for (let j = 0; j < excludeKeywords.length; j++) {{
                                        const keyword = excludeKeywords[j].toLowerCase();
                                        if (keyword && lowerTypeName.includes(keyword)) {{
                                                console.log('[TICKET] Excluded: ' + typeName);
                                                excluded = true;
                                                break;
                                            }}
                                        }}
                                    }}

                                if (excluded) continue;

                                // Found valid ticket type - click + button via opera1
                                console.log('[TICKET] Selected: ' + typeName);
                                const currentValue = parseInt(input.value) || 0;
                                const targetValue = parseInt(ticketNumber);

                                if (currentValue < targetValue) {{
                                    // Try to find and call opera1 function
                                    if (typeof opera1 === 'function') {{
                                        for (let clicks = currentValue; clicks < targetValue; clicks++) {{
                                            opera1(key, true);  // true = increase
                                            console.log('[TICKET] Called opera1(' + key + ', true) - click ' + (clicks + 1));
                                        }}
                                    }} else {{
                                        // Fallback: directly set value
                                        input.value = ticketNumber;
                                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        console.log('[TICKET] Set to: ' + ticketNumber + ' (fallback)');
                                    }}
                                }}

                                return {{
                                    success: true,
                                    typeName: typeName,
                                    key: key,
                                    value: ticketNumber
                                }};
                                }}

                            return {{ success: false, message: 'All ticket types excluded' }};
                            }})();
                    ''')

                    if debug.enabled:
                        # NoDriver returns a complex format, just confirm execution
                        debug.log(f"[TICKET] Ticket selection JavaScript executed")

                except Exception as exc:
                    debug.log(f"Set ticket number error: {exc}")

            # Submit if captcha sent and ticket number assigned
            if is_captcha_sent:
                # Check if login is required (Kham only)
                need_login = False
                if "kham.com.tw" in url:
                    try:
                            login_id = await tab.query_selector('#LOGIN_ID')
                            login_pwd = await tab.query_selector('#LOGIN_PWD')

                            if login_id and login_pwd:
                                # Check if login fields are visible
                                is_visible = await tab.evaluate('''
                                    (function() {
                                        const block1 = document.getElementById('LOGIN_BLOCK1');
                                        const block2 = document.getElementById('LOGIN_BLOCK2');
                                        if (block1 && block2) {
                                            const style1 = window.getComputedStyle(block1);
                                            const style2 = window.getComputedStyle(block2);
                                            return style1.display !== 'none' && style2.display !== 'none';
                                        }
                                        return false;
                                    })();
                                ''')

                                if is_visible:
                                    need_login = True
                                    debug.log("[LOGIN REQUIRED] Login fields detected - triggering idle mechanism")
                    except Exception as e:
                        debug.log(f"Login detection error: {e}")

                # If login required, trigger idle and don't submit
                if need_login:
                    settings.maxbot_idle()
                    debug.log("[IDLE ACTIVATED] Waiting for manual login - ticket number and captcha already filled")
                else:
                    # Normal submit flow
                    try:
                        if "ticket.com.tw" in url:
                            # ticket.com.tw uses <input type="submit"> with id ending in AddShopingCart
                            debug.log("[SUBMIT] Searching for ticket.com.tw submit button...")
                            el_btn = await tab.query_selector('input[id$="AddShopingCart"]')
                            if not el_btn:
                                # Fallback to <a> tag
                                el_btn = await tab.query_selector('a[onclick="return chkCart();"]')
                        elif "orders.ibon.com.tw" in url:
                            # ibon uses <a> tag with id containing AddShopingCart
                            debug.log("[SUBMIT] Searching for ibon submit button...")
                            el_btn = await tab.query_selector('a[id*="AddShopingCart"]')
                            if not el_btn:
                                # Fallback to generic button
                                el_btn = await tab.query_selector('a.btn.btn-primary.btn-block')
                        else:
                            # Kham
                            debug.log("[SUBMIT] Searching for Kham submit button...")
                            el_btn = await tab.query_selector('button[onclick="addShoppingCart();return false;"]')

                        if el_btn:
                            debug.log("[SUBMIT] Submit button found, scrolling into view...")
                            # Scroll button into view first (important for CDP click)
                            try:
                                await el_btn.scroll_into_view()
                                await tab.sleep(0.3)
                            except:
                                pass

                            debug.log("[SUBMIT] Clicking using CDP native click...")
                            # Use NoDriver CDP native click
                            await el_btn.click()
                            debug.log("[SUBMIT] Add shopping cart button clicked successfully!")

                            dialog_result = await _handle_post_submit_dialog(tab, config_dict)

                            if dialog_result == "success":
                                debug.log("[SUBMIT] Waiting for page transition after success...")
                                await tab.sleep(1.0)

                                current_url = tab.target.url
                                url_changed = False
                                for i in range(60):  # 60 * 0.5s = 30s
                                    await tab.sleep(0.5)
                                    new_url = tab.target.url
                                    if new_url != current_url:
                                        debug.log(f"[SUBMIT] Page transitioned to {new_url}")
                                        url_changed = True
                                        break

                                if not url_changed:
                                    debug.log("[SUBMIT] CRITICAL: Success dialog but URL never changed after 30s")
                                    await tab.sleep(5.0)

                            elif dialog_result == "error":
                                debug.log("[SUBMIT] Will retry with new captcha")
                                await tab.sleep(2.0)

                            else:
                                current_url = tab.target.url
                                for i in range(10):  # 10 * 0.5s = 5s
                                    await tab.sleep(0.5)
                                    new_url = tab.target.url
                                    if new_url != current_url:
                                        debug.log(f"[SUBMIT] Page transitioned to {new_url}")
                                        break
                        else:
                            debug.log("[SUBMIT] Add shopping cart button not found")
                    except Exception as exc:
                        if debug.enabled:
                            debug.log(f"[SUBMIT] Click chkCart/addShoppingCart button fail: {exc}")
                            import traceback
                            traceback.print_exc()

        # Login page handling (UTK1306)
        if '/utk13/utk1306_.aspx' in url.lower():
            # Close dialog buttons
            try:
                el_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
                if el_btn:
                    await el_btn.click()
            except:
                pass

            if config_dict["ocr_captcha"]["enable"]:
                model_name = url.split('/')[5] if len(url.split('/')) > 5 else "UTK1306"
                if len(model_name) > 7:
                    model_name = model_name[:7]

                # Handle captcha
                await nodriver_kham_captcha(tab, config_dict, ocr, model_name)

                # UDN login (Feature 010: uses same UTK backend as KHAM)
                if 'udnfunlife' in domain_name:
                    udn_account = config_dict["accounts"]["udn_account"]
                    udn_password = config_dict["accounts"]["udn_password"].strip()
                    if len(udn_account) > 4:
                        debug.log(f"[UDN LOGIN] Attempting login with account: {udn_account[:3]}***")
                        await nodriver_kham_login(tab, udn_account, udn_password, ocr, config_dict=config_dict)

                # Kham login
                kham_account = config_dict["accounts"]["kham_account"]
                kham_password = config_dict["accounts"]["kham_password"].strip()
                if len(kham_account) > 4:
                    await nodriver_kham_login(tab, kham_account, kham_password, ocr, config_dict=config_dict)

                # Ticket.com.tw login
                ticket_account = config_dict["accounts"]["ticket_account"]
                ticket_password = config_dict["accounts"]["ticket_password"].strip()
                if len(ticket_account) > 4:
                    # Use dedicated ticket login function (different selectors)
                    await nodriver_ticket_login(tab, ticket_account, ticket_password, config_dict)

    # Check if reached checkout page (ticket purchase successful)
    if '/utk02/utk0206_.aspx' in url.lower():
        # Reset quick buy flag since we've reached checkout
        _state["udn_quick_buy_submitted"] = False

        # Show success message (only once)
        if debug.enabled:
            if not _state["shown_checkout_message"]:
                debug.log("[SUCCESS] Reached checkout page - ticket purchase successful!")
        _state["shown_checkout_message"] = True

        # Play sound notification (only once)
        if not _state["played_sound_order"]:
            if config_dict["advanced"]["play_sound"]["order"]:
                play_sound_while_ordering(config_dict)
            send_discord_notification(config_dict, "order", "KHAM")
            send_telegram_notification(config_dict, "order", "KHAM")
        _state["played_sound_order"] = True

        # If headless mode, open browser to show checkout page (only once)
        if config_dict["advanced"]["headless"]:
            if not _state["is_popup_checkout"]:
                import webbrowser
                checkout_url = url
                print(f"搶票成功，請前往該帳號訂單查看: {checkout_url}")
                webbrowser.open_new(checkout_url)
                _state["is_popup_checkout"] = True

    return tab

# ====================================================================================
# Ticket Platform (ticket.com.tw / 年代售票)
# ====================================================================================

async def nodriver_ticket_login(tab, account, password, config_dict):
    """
    年代售票登入

    [TESTED] 已完整測試 - T004 暫停機制補完
    [TESTED] 已完整測試 - 登入邏輯驗證

    Reference: chrome_tixcraft.py ticket_login (Line 5553-5612)
    URL: https://ticket.com.tw/application/utk13/utk1306_.aspx
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False

    ret = False
    debug = util.create_debug_logger(config_dict)

    # Find email/account input - Use ID selector
    el_email = None
    try:
        el_email = await tab.query_selector('#ctl00_ContentPlaceHolder1_M_ACCOUNT')
    except Exception as exc:
        debug.log("Find account input fail:", exc)

    # Input account
    is_email_sent = False
    if el_email:
        try:
            inputed_text = await tab.evaluate('document.querySelector("#ctl00_ContentPlaceHolder1_M_ACCOUNT").value')
            if not inputed_text or len(inputed_text) == 0:
                await el_email.send_keys(account)
                is_email_sent = True
            else:
                if inputed_text == account:
                    is_email_sent = True
        except Exception as exc:
            debug.log("Input account fail:", exc)

    # Find password input - Use ID selector
    el_pass = None
    if is_email_sent:
        try:
            el_pass = await tab.query_selector('#ctl00_ContentPlaceHolder1_M_PASSWORD')
        except Exception as exc:
            debug.log("Find password input fail:", exc)

    # Input password
    is_password_sent = False
    if el_pass:
        try:
            inputed_text = await tab.evaluate('document.querySelector("#ctl00_ContentPlaceHolder1_M_PASSWORD").value')
            if not inputed_text or len(inputed_text) == 0:
                await el_pass.click()
                if len(password) > 0:
                    await el_pass.send_keys(password)
                    is_password_sent = True
                await tab.sleep(0.1)
        except Exception as exc:
            debug.log("Input password fail:", exc)

    # Click login button - Use ID selector
    if is_password_sent:
        try:
            el_btn = await tab.query_selector('#ctl00_ContentPlaceHolder1_LOGIN_BTN')
            if el_btn:
                await el_btn.click()
                ret = True
                debug.log("[TICKET LOGIN] Login button clicked")
        except Exception as exc:
            debug.log("Click login button fail:", exc)

    return ret

async def nodriver_kham_seat_type_auto_select(tab, config_dict, area_keyword_item):
    """
    寬宏售票 - 自動選擇票別 (UTK0205 座位選擇頁面)
    選擇票價類型，如原價、身障、陪同者等
    HTML structure: <button class="green" onclick="setType(...)">原價-NT$3,680</button>
    使用 CDP DOMSnapshot 穿透 DOM，避免 JavaScript 載入時機問題
    參考年代售票 nodriver_ticket_seat_type_auto_select 成功實作
    """
    debug = util.create_debug_logger(config_dict)
    is_seat_type_assigned = False

    # Clean keyword quotes
    # NOTE: This function only supports single keyword or space-separated AND logic (e.g., "VIP 區")
    # For multiple keywords with OR logic, caller should use JSON parsing and iterate
    if area_keyword_item and len(area_keyword_item) > 0:
        try:
            area_keyword_clean = area_keyword_item.strip()
            if area_keyword_clean.startswith('"') and area_keyword_clean.endswith('"'):
                area_keyword_clean = area_keyword_clean[1:-1]

            # Use the cleaned keyword directly (no comma split to avoid incorrect AND logic)
            area_keyword_item = area_keyword_clean
        except Exception as e:
            debug.log(f"[KHAM SEAT TYPE] Keyword parse error: {e}")

    try:
        from zendriver import cdp

        # Step 1: Capture DOM snapshot
        debug.log("[KHAM SEAT TYPE] Capturing DOM snapshot...")

        try:
            documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
                computed_styles=[],
                include_dom_rects=True
            ))
        except Exception as snapshot_exc:
            debug.log(f"[KHAM SEAT TYPE] ERROR capturing snapshot: {snapshot_exc}")
            # Fallback: try simple JavaScript method
            debug.log("[KHAM SEAT TYPE] Falling back to JavaScript method...")

            buttons_data = await tab.evaluate('''
                (function() {
                    const buttons = document.querySelectorAll('button[onclick*="setType"]');
                    const result = [];
                    buttons.forEach((btn) => {
                        result.push({
                            text: btn.textContent.trim(),
                            disabled: btn.disabled
                        });
                    });
                    return result;
                })();
            ''')

            # 轉換 CDP 格式為 Python list
            buttons_list = []
            if isinstance(buttons_data, list):
                for item in buttons_data:
                    if isinstance(item, list) and len(item) == 2:
                        val_obj = item[1]
                        if isinstance(val_obj, dict) and 'value' in val_obj:
                            obj_data = val_obj['value']
                            btn_info = {}
                            if isinstance(obj_data, list):
                                for prop in obj_data:
                                    if isinstance(prop, list) and len(prop) == 2:
                                        key = prop[0]
                                        val = prop[1].get('value') if isinstance(prop[1], dict) else prop[1]
                                        btn_info[key] = val
                            buttons_list.append(btn_info)

            debug.log(f"[KHAM SEAT TYPE] Found {len(buttons_list)} button(s) via JavaScript fallback")

            # 簡化邏輯：直接使用 JavaScript 找到的按鈕
            if len(buttons_list) > 0:
                # 直接點擊第一個可用按鈕
                result = await tab.evaluate('''
                    (function() {
                        const buttons = document.querySelectorAll('button[onclick*="setType"]');
                        for (let btn of buttons) {
                            if (!btn.disabled) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    })();
                ''')

                if isinstance(result, list) and len(result) == 2:
                    is_seat_type_assigned = result[1].get('value', False) if isinstance(result[1], dict) else result
                else:
                    is_seat_type_assigned = result

                debug.log(f"[KHAM SEAT TYPE] JavaScript fallback click result: {is_seat_type_assigned}")

                debug.log(f"[KHAM SEAT TYPE] Assignment result: {is_seat_type_assigned}")

                return is_seat_type_assigned

            raise snapshot_exc

        # Step 2: Search for ticket type buttons
        ticket_buttons = []

        debug.log(f"[KHAM SEAT TYPE] documents type: {type(documents)}, len: {len(documents) if documents else 0}")

        if documents and len(documents) > 0:
            document_snapshot = documents[0]
            nodes = document_snapshot.nodes

            # Extract node information
            node_names = [strings[i] for i in nodes.node_name]
            node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
            attributes_list = nodes.attributes
            backend_node_ids = list(nodes.backend_node_id)

            debug.log(f"[KHAM SEAT TYPE] Total nodes in snapshot: {len(node_names)}")

            # Step 3: Search for buttons with setType onclick
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'BUTTON':
                    # Parse attributes
                    attrs = {}
                    if i < len(attributes_list):
                        attr_indices = attributes_list[i]
                        for j in range(0, len(attr_indices), 2):
                            if j + 1 < len(attr_indices):
                                key = strings[attr_indices[j]]
                                val = strings[attr_indices[j + 1]]
                                attrs[key] = val

                    # Check if this is a ticket type button (onclick contains setType)
                    onclick = attrs.get('onclick', '')
                    button_class = attrs.get('class', '')
                    button_disabled = 'disabled' in attrs

                    if 'setType' in onclick:
                        # Get button text from child text nodes
                        # Strategy 1: Search for first non-empty text node in children
                        button_text = ''
                        for j in range(i + 1, min(i + 10, len(node_names))):  # Check next 10 nodes
                            if node_names[j] == '#text':
                                text_content = node_values[j].strip()
                                if text_content and len(text_content) > 0:
                                    button_text = text_content
                                    debug.log(f"[KHAM SEAT TYPE] Extracted text from node {j}: '{button_text}'")
                                    break
                            # Stop when encountering another element (DIV, BUTTON, etc.)
                            elif node_names[j] in ['DIV', 'BUTTON', 'INPUT', 'SPAN', 'A']:
                                break

                        # Strategy 2: Fallback - Extract from onclick attribute if text is empty
                        if not button_text and 'setType' in onclick:
                            import re
                            match = re.search(r"setType\('[^']*','([^']*)'\)", onclick)
                            if match:
                                button_text = match.group(1)
                                debug.log(f"[KHAM SEAT TYPE] Extracted text from onclick: '{button_text}'")

                        ticket_buttons.append({
                            'backend_node_id': backend_node_ids[i],
                            'class': button_class,
                            'onclick': onclick,
                            'disabled': button_disabled,
                            'text': button_text,
                            'index': i
                        })

                        debug.log(f"[KHAM SEAT TYPE] Found button #{len(ticket_buttons)}: text='{button_text}', disabled={button_disabled}")

        debug.log(f"[KHAM SEAT TYPE] Found {len(ticket_buttons)} ticket type button(s)")

        if len(ticket_buttons) == 0:
            debug.log("[KHAM SEAT TYPE] No ticket type buttons found")
            return False

        # Step 4: Filter disabled buttons
        enabled_buttons = [btn for btn in ticket_buttons if not btn['disabled']]

        debug.log(f"[KHAM SEAT TYPE] Found {len(enabled_buttons)} enabled button(s)")

        if len(enabled_buttons) == 0:
            debug.log("[KHAM SEAT TYPE] All buttons are disabled")
            return False

        # Step 5: Match and select button using Python logic
        matched_button = None

        for btn in enabled_buttons:
            button_text = btn.get('text', '')
            if not button_text:
                continue

            # 使用 util 檢查是否應該排除（依據設定檔的 keyword_exclude）
            if util.reset_row_text_if_match_keyword_exclude(config_dict, button_text):
                debug.log(f"[KHAM SEAT TYPE] Excluded by keyword_exclude: {button_text}")
                continue

            # 關鍵字匹配邏輯
            is_match = True
            if area_keyword_item and len(area_keyword_item) > 0:
                keywords = area_keyword_item.split(' ')
                row_text = util.format_keyword_string(button_text)
                for kw in keywords:
                    formatted_kw = util.format_keyword_string(kw)
                    if formatted_kw not in row_text:
                        is_match = False
                        break

            if is_match:
                matched_button = btn
                debug.log(f"[KHAM SEAT TYPE] Matched: {button_text}")
                break

        # If no keyword match found, use first enabled button
        if matched_button is None and len(enabled_buttons) > 0:
            matched_button = enabled_buttons[0]
            debug.log(f"[KHAM SEAT TYPE] No keyword match, using first button: {matched_button.get('text', '')}")

        # Step 6: Click matched button using CDP Input.dispatchMouseEvent (per nodriver API guide Example 3)
        if matched_button is not None:
            button_text = matched_button.get('text', '')
            backend_node_id = matched_button.get('backend_node_id')

            try:
                debug.log(f"[KHAM SEAT TYPE] Clicking button via CDP: {button_text}")

                is_seat_type_assigned = False

                # Step 6.1: Convert backend_node_id to node_id using CDP DOM
                if backend_node_id is not None:
                    try:
                        debug.log(f"[KHAM SEAT TYPE] Using backend_node_id={backend_node_id}")

                        # Get document first
                        await tab.send(cdp.dom.get_document())

                        # Convert backend_node_id to node_id
                        push_result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([backend_node_id]))
                        if push_result and len(push_result) > 0:
                            node_id = push_result[0]

                            debug.log(f"[KHAM SEAT TYPE] Converted to node_id={node_id}")

                            # Step 6.2: Scroll into view to ensure element is visible
                            try:
                                await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                                debug.log(f"[KHAM SEAT TYPE] Scrolled button into view")
                            except Exception as scroll_exc:
                                debug.log(f"[KHAM SEAT TYPE] Scroll into view exception (non-critical): {scroll_exc}")

                            # Step 6.3: Get box model for precise click coordinates
                            try:
                                box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
                                debug.log(f"[KHAM SEAT TYPE] Box model result: {type(box_model)}")

                                if box_model and hasattr(box_model, 'content') and box_model.content:
                                    quad = box_model.content
                                    # Calculate center coordinates from quad (8 values: [x1, y1, x2, y2, x3, y3, x4, y4])
                                    center_x = (quad[0] + quad[2] + quad[4] + quad[6]) / 4.0
                                    center_y = (quad[1] + quad[3] + quad[5] + quad[7]) / 4.0

                                    debug.log(f"[KHAM SEAT TYPE] Box model center: ({center_x:.1f}, {center_y:.1f})")

                                    # Step 6.4: Use JavaScript to click (CDP input module not available)
                                    # Since JavaScript fallback already works, skip CDP mouse event
                                    debug.log(f"[KHAM SEAT TYPE] Using JavaScript click (CDP input unavailable)")
                                else:
                                    debug.log(f"[KHAM SEAT TYPE] Failed to get box model content: {box_model}")
                                    debug.log("[KHAM SEAT TYPE] Falling back to JavaScript click...")

                            except Exception as box_exc:
                                debug.log(f"[KHAM SEAT TYPE] Box model exception: {box_exc}")
                        else:
                            debug.log(f"[KHAM SEAT TYPE] Failed to convert backend_node_id: push_result={push_result}")

                    except Exception as cdp_exc:
                        debug.log(f"[KHAM SEAT TYPE] CDP operation error: {cdp_exc}")
                else:
                    debug.log(f"[KHAM SEAT TYPE] backend_node_id is None, using JavaScript fallback")

                # Fallback: If CDP click failed, try JavaScript click
                if not is_seat_type_assigned:
                    try:
                        debug.log(f"[KHAM SEAT TYPE] Attempting JavaScript fallback click")
                        result = await tab.evaluate('''
                            (function() {
                                const buttons = document.querySelectorAll('button[onclick*="setType"]');
                                for (let btn of buttons) {
                                    if (btn.textContent.includes('%s')) {
                                        btn.click();
                                        return true;
                                    }
                                }
                                return false;
                            })();
                        ''' % button_text.replace("'", "\\'"))

                        if isinstance(result, list) and len(result) == 2:
                            is_seat_type_assigned = result[1].get('value', False) if isinstance(result[1], dict) else result
                        else:
                            is_seat_type_assigned = result

                        if is_seat_type_assigned:
                            debug.log(f"[KHAM SEAT TYPE] JavaScript fallback click succeeded")
                        else:
                            debug.log(f"[KHAM SEAT TYPE] JavaScript fallback click failed")
                    except Exception as js_exc:
                        debug.log(f"[KHAM SEAT TYPE] JavaScript fallback exception: {js_exc}")

            except Exception as click_exc:
                debug.log(f"[KHAM SEAT TYPE] CDP click exception: {click_exc}")

    except Exception as exc:
        debug.log(f"[ERROR] KHAM seat type selection error: {exc}")
        import traceback
        if debug.enabled:
            traceback.print_exc()

    debug.log(f"[KHAM SEAT TYPE] Assignment result: {is_seat_type_assigned}")

    return is_seat_type_assigned

async def nodriver_kham_seat_auto_select(tab, config_dict):
    """
    寬宏售票 - 自動選擇座位，優化策略：舞台方向智慧選座
    HTML structure:
    - Stage direction: <div class="stageDirection topright/topleft/downright/downleft/top/down/left/right">
    - Available seats: <table id="TBL"><td class="empty up/down/left/right" title="2樓黃2D區-3排-14號">
    - Sold seats: <td class="people up/down/left/right">

    舞台方向邏輯：
    - up: 排數越小越前，每排選中間座位
    - down: 排數越大越前，每排選中間座位
    - left: 座位號越小越前，每列選中間排
    - right: 座位號越大越前，每列選中間排
    - topright/topleft/downright/downleft: 組合方向，優先處理主要方向
    """
    is_seat_assigned = False
    ticket_number = config_dict["ticket_number"]
    allow_non_adjacent = config_dict["advanced"]["disable_adjacent_seat"]
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    try:
        # 使用純 JavaScript 執行全部邏輯：偵測方向 -> 分組 -> 排序 -> 選擇 -> 點擊
        import json
        result = await tab.evaluate(f'''
            (function() {{
                const ticketNumber = {ticket_number};
                const allowNonAdjacent = {json.dumps(allow_non_adjacent)};
                const showDebug = {json.dumps(show_debug)};

                // Step 0: Detect stage direction
                const stageDiv = document.querySelector('.stageDirection');
                let stageDirection = 'up'; // default: stage at top
                if (stageDiv) {{
                    const classList = stageDiv.classList;
                    if (classList.contains('topright')) stageDirection = 'up';       // topright -> up (主要方向)
                    else if (classList.contains('topleft')) stageDirection = 'up';   // topleft -> up (主要方向)
                    else if (classList.contains('downright')) stageDirection = 'down';
                    else if (classList.contains('downleft')) stageDirection = 'down';
                    else if (classList.contains('top')) stageDirection = 'up';
                    else if (classList.contains('down')) stageDirection = 'down';
                    else if (classList.contains('left')) stageDirection = 'left';
                    else if (classList.contains('right')) stageDirection = 'right';
                }}

                if (showDebug) {{
                    console.log('[KHAM SEAT] Stage direction: ' + stageDirection);
                }}

                // Step 1: Find all available seats with REAL DOM positions
                // Important: Use real TD column index, not filtered array index
                // This correctly handles spacer TDs (<td>&nbsp;</td>) that represent aisles/separators
                const allTableRows = document.querySelectorAll('table#TBL tr');
                let totalAvailableSeats = 0;

                // First pass: count available seats
                Array.from(allTableRows).forEach(tr => {{
                    const allTds = tr.children;
                    for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                        if (allTds[colIndex].classList.contains('empty')) {{
                            totalAvailableSeats++;
                        }}
                    }}
                }});

                if (showDebug) {{
                    console.log('[KHAM SEAT] Found ' + totalAvailableSeats + ' available seats');
                }}

                if (totalAvailableSeats < ticketNumber) {{
                    return {{ success: false, found: totalAvailableSeats, selected: 0, direction: stageDirection }};
                }}

                const selectedSeats = [];
                let usedFallback = false;

                // Step 2-4: Group, sort and select based on stage direction
                if (stageDirection === 'up' || stageDirection === 'down') {{
                    // GROUP BY ROW: For top/bottom stages
                    const rows = {{}};

                    // Second pass: collect seats with REAL DOM column index
                    Array.from(allTableRows).forEach(tr => {{
                        const allTds = tr.children;
                        for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                            const seat = allTds[colIndex];
                            if (seat.classList.contains('empty')) {{
                                const title = seat.getAttribute('title');
                                if (title && title.includes('排') && title.includes('號')) {{
                                    const parts = title.split('-');
                                    if (parts.length >= 3) {{
                                        // [KHAM] Parse row number (support both letter and number rows)
                                        let rowNum;
                                        const rowText = parts[1]; // e.g. "H排" or "17排"
                                        const letterMatch = rowText.match(/([A-Z]+)排/);
                                        if (letterMatch) {{
                                            // Letter row (H排 -> 8, I排 -> 9, etc.)
                                            const letters = letterMatch[1];
                                            rowNum = 0;
                                            for (let i = 0; i < letters.length; i++) {{
                                                rowNum = rowNum * 26 + (letters.charCodeAt(i) - 64);
                                            }}
                                        }} else {{
                                            // Numeric row
                                            rowNum = parseInt(rowText.replace('排', ''));
                                        }}
                                        const seatNum = parseInt(parts[2].replace('號', ''));
                                        if (!isNaN(rowNum) && !isNaN(seatNum)) {{
                                            if (!rows[rowNum]) rows[rowNum] = [];
                                            // CRITICAL: Use REAL colIndex as domIndex, not filtered array index
                                            rows[rowNum].push({{ elem: seat, num: seatNum, title: title, domIndex: colIndex }});
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }});

                    // Helper function: calculate row quality score
                    function calculateRowQuality(rowSeats) {{
                        const totalSeats = rowSeats.length;

                        // Find max continuous segment (based on DOM index, not seat number)
                        let maxContinuous = 1;
                        let currentContinuous = 1;
                        for (let i = 0; i < rowSeats.length - 1; i++) {{
                            const domGap = rowSeats[i + 1].domIndex - rowSeats[i].domIndex;
                            if (domGap === 1) {{
                                // Adjacent in DOM
                                currentContinuous++;
                                maxContinuous = Math.max(maxContinuous, currentContinuous);
                            }} else {{
                                // Gap found
                                currentContinuous = 1;
                            }}
                        }}

                        // Calculate middle seats ratio (seats in middle 50%)
                        const middleStart = Math.floor(totalSeats * 0.25);
                        const middleEnd = Math.floor(totalSeats * 0.75);
                        let middleCount = 0;
                        rowSeats.forEach((seat, idx) => {{
                            if (idx >= middleStart && idx < middleEnd) middleCount++;
                        }});
                        const middleRatio = middleCount / Math.max(1, (middleEnd - middleStart));

                        // Three-tier quality score:
                        // 1. Priority: has enough continuous seats
                        // 2. Priority: middle seat ratio
                        // 3. Priority: stage direction preference
                        return {{
                            maxContinuous: maxContinuous,
                            totalSeats: totalSeats,
                            middleRatio: middleRatio,
                            score: (maxContinuous >= ticketNumber) ? 100 + middleRatio : maxContinuous + middleRatio
                        }};
                    }}

                    // Sort rows by stage direction
                    let sortedRows;
                    if (stageDirection === 'up') {{
                        // Stage at top: smaller row number = closer to stage
                        sortedRows = Object.entries(rows).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
                    }} else {{
                        // Stage at bottom: larger row number = closer to stage
                        sortedRows = Object.entries(rows).sort((a, b) => parseInt(b[0]) - parseInt(a[0]));
                    }}

                    // Select seats from front rows
                    for (const [rowNum, rowSeats] of sortedRows) {{
                        // Sort by DOM order (domIndex) to maintain continuity
                        rowSeats.sort((a, b) => a.domIndex - b.domIndex);
                        const seatCount = rowSeats.length;

                        if (allowNonAdjacent) {{
                            // Non-adjacent mode: select from middle of row
                            const startIdx = Math.max(0, Math.floor((seatCount - ticketNumber) / 2));
                            for (let i = 0; i < Math.min(ticketNumber, seatCount); i++) {{
                                if (startIdx + i < rowSeats.length) {{
                                    selectedSeats.push(rowSeats[startIdx + i]);
                                    if (selectedSeats.length >= ticketNumber) break;
                                }}
                            }}
                        }} else {{
                            // Adjacent mode: find continuous seats in DOM order
                            for (let startIdx = 0; startIdx <= rowSeats.length - ticketNumber; startIdx++) {{
                                let continuous = true;
                                for (let i = 0; i < ticketNumber - 1; i++) {{
                                    const currentDomIdx = rowSeats[startIdx + i].domIndex;
                                    const nextDomIdx = rowSeats[startIdx + i + 1].domIndex;
                                    const domGap = nextDomIdx - currentDomIdx;
                                    if (domGap > 1) {{
                                        // Seats are not adjacent in DOM
                                        continuous = false;
                                        break;
                                    }}
                                }}

                                if (continuous) {{
                                    for (let i = 0; i < ticketNumber; i++) {{
                                        selectedSeats.push(rowSeats[startIdx + i]);
                                    }}
                                    break;
                                }}
                            }}
                        }}

                        if (selectedSeats.length >= ticketNumber) break;
                    }}

                    // Non-adjacent fallback: adjacent mode found 0 seats but seats exist
                    if (!allowNonAdjacent && selectedSeats.length < ticketNumber) {{
                        for (const [rowNum, rowSeats] of sortedRows) {{
                            rowSeats.sort((a, b) => a.domIndex - b.domIndex);
                            const seatCount = rowSeats.length;
                            const startIdx = Math.max(0, Math.floor((seatCount - ticketNumber) / 2));
                            for (let i = 0; i < seatCount; i++) {{
                                if (startIdx + i < rowSeats.length) {{
                                    selectedSeats.push(rowSeats[startIdx + i]);
                                    if (selectedSeats.length >= ticketNumber) break;
                                }}
                            }}
                            if (selectedSeats.length >= ticketNumber) break;
                        }}
                        if (selectedSeats.length >= ticketNumber) usedFallback = true;
                    }}

                }} else if (stageDirection === 'left' || stageDirection === 'right') {{
                    // GROUP BY SEAT NUMBER (column): For left/right stages
                    const columns = {{}};

                    // Collect seats with REAL DOM row index (for vertical continuity check)
                    let rowIndexInTable = 0;
                    Array.from(allTableRows).forEach(tr => {{
                        const allTds = tr.children;
                        for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                            const seat = allTds[colIndex];
                            if (seat.classList.contains('empty')) {{
                                const title = seat.getAttribute('title');
                                if (title && title.includes('排') && title.includes('號')) {{
                                    const parts = title.split('-');
                                    if (parts.length >= 3) {{
                                        // [KHAM] Parse row number (support both letter and number rows)
                                        let rowNum;
                                        const rowText = parts[1]; // e.g. "H排" or "17排"
                                        const letterMatch = rowText.match(/([A-Z]+)排/);
                                        if (letterMatch) {{
                                            // Letter row (H排 -> 8, I排 -> 9, etc.)
                                            const letters = letterMatch[1];
                                            rowNum = 0;
                                            for (let i = 0; i < letters.length; i++) {{
                                                rowNum = rowNum * 26 + (letters.charCodeAt(i) - 64);
                                            }}
                                        }} else {{
                                            // Numeric row
                                            rowNum = parseInt(rowText.replace('排', ''));
                                        }}
                                        const seatNum = parseInt(parts[2].replace('號', ''));
                                        if (!isNaN(rowNum) && !isNaN(seatNum)) {{
                                            if (!columns[seatNum]) columns[seatNum] = [];
                                            // CRITICAL: Use real rowIndexInTable as domIndex for vertical continuity
                                            columns[seatNum].push({{ elem: seat, rowNum: rowNum, title: title, domIndex: rowIndexInTable }});
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        rowIndexInTable++;
                    }});

                    // Sort columns by stage direction
                    let sortedColumns;
                    if (stageDirection === 'left') {{
                        // Stage at left: smaller seat number = closer to stage
                        sortedColumns = Object.entries(columns).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
                    }} else {{
                        // Stage at right: larger seat number = closer to stage
                        sortedColumns = Object.entries(columns).sort((a, b) => parseInt(b[0]) - parseInt(a[0]));
                    }}

                    // Select seats from front columns
                    for (const [seatNum, columnSeats] of sortedColumns) {{
                        // Sort by DOM order (domIndex) to maintain continuity
                        columnSeats.sort((a, b) => a.domIndex - b.domIndex);
                        const rowCount = columnSeats.length;

                        if (allowNonAdjacent) {{
                            // Non-adjacent mode: select from middle rows of column
                            const startIdx = Math.max(0, Math.floor((rowCount - ticketNumber) / 2));
                            for (let i = 0; i < Math.min(ticketNumber, rowCount); i++) {{
                                if (startIdx + i < columnSeats.length) {{
                                    selectedSeats.push(columnSeats[startIdx + i]);
                                    if (selectedSeats.length >= ticketNumber) break;
                                }}
                            }}
                        }} else {{
                            // Adjacent mode: find continuous rows in DOM order (not by row number)
                            for (let startIdx = 0; startIdx <= columnSeats.length - ticketNumber; startIdx++) {{
                                let continuous = true;
                                for (let i = 0; i < ticketNumber - 1; i++) {{
                                    const currentDomIdx = columnSeats[startIdx + i].domIndex;
                                    const nextDomIdx = columnSeats[startIdx + i + 1].domIndex;
                                    const domGap = nextDomIdx - currentDomIdx;
                                    if (domGap > 1) {{
                                        // Seats are not adjacent in DOM
                                        continuous = false;
                                        break;
                                    }}
                                }}

                                if (continuous) {{
                                    for (let i = 0; i < ticketNumber; i++) {{
                                        selectedSeats.push(columnSeats[startIdx + i]);
                                    }}
                                    break;
                                }}
                            }}
                        }}

                        if (selectedSeats.length >= ticketNumber) break;
                    }}

                    // Non-adjacent fallback: adjacent mode found 0 seats but seats exist
                    if (!allowNonAdjacent && selectedSeats.length < ticketNumber) {{
                        for (const [seatNum, columnSeats] of sortedColumns) {{
                            columnSeats.sort((a, b) => a.domIndex - b.domIndex);
                            const rowCount = columnSeats.length;
                            const startIdx = Math.max(0, Math.floor((rowCount - ticketNumber) / 2));
                            for (let i = 0; i < rowCount; i++) {{
                                if (startIdx + i < columnSeats.length) {{
                                    selectedSeats.push(columnSeats[startIdx + i]);
                                    if (selectedSeats.length >= ticketNumber) break;
                                }}
                            }}
                            if (selectedSeats.length >= ticketNumber) break;
                        }}
                        if (selectedSeats.length >= ticketNumber) usedFallback = true;
                    }}
                }}

                // Step 5: Click selected seats
                let clickedCount = 0;
                const clickedTitles = [];
                for (const seat of selectedSeats.slice(0, ticketNumber)) {{
                    // 寬宏座位點擊後會改變 class（empty -> 其他狀態）
                    seat.elem.click();
                    clickedCount++;
                    clickedTitles.push(seat.title);
                }}

                return {{
                    success: clickedCount > 0,
                    found: totalAvailableSeats,
                    selected: clickedCount,
                    titles: clickedTitles,
                    direction: stageDirection,
                    usedFallback: usedFallback
                }};
            }})();
        ''')

        # 轉換 CDP 格式為 Python dict
        result_dict = {}
        if isinstance(result, list):
            for item in result:
                if isinstance(item, list) and len(item) == 2:
                    key = item[0]
                    val_obj = item[1]
                    if isinstance(val_obj, dict) and 'value' in val_obj:
                        value = val_obj['value']
                        # 處理陣列類型
                        if val_obj.get('type') == 'array' and isinstance(value, list):
                            result_dict[key] = [
                                v.get('value') if isinstance(v, dict) else v
                                for v in value
                            ]
                        else:
                            result_dict[key] = value
        elif isinstance(result, dict):
            result_dict = result

        is_seat_assigned = result_dict.get('success', False)

        if result_dict.get('usedFallback'):
            debug.log("[KHAM SEAT] Adjacent seats not available, used non-adjacent fallback")

        if debug.enabled:
            stage_dir = result_dict.get('direction', 'unknown')
            debug.log(f"[KHAM SEAT] Stage direction: {stage_dir}")
            debug.log(f"[KHAM SEAT] Found {result_dict.get('found', 0)} available seats")
            debug.log(f"[KHAM SEAT] Selected {result_dict.get('selected', 0)}/{ticket_number} seats")
            if result_dict.get('titles'):
                for title in result_dict['titles']:
                    debug.log(f"[SUCCESS] Selected seat: {title}")

    except Exception as exc:
        debug.log(f"[ERROR] KHAM seat selection error: {exc}")
        import traceback
        if debug.enabled:
            traceback.print_exc()

    return is_seat_assigned

async def nodriver_kham_seat_main(tab, config_dict, ocr, domain_name):
    """
    寬宏售票座位選擇主流程：票別選擇 -> 座位選擇 -> 驗證碼 -> 提交
    UTK0205 頁面處理
    """
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)
    ticket_number = config_dict["ticket_number"]

    # Step 0: Check if seats are already selected (avoid duplicate selection)
    already_selected_count = 0
    try:
        check_result = await tab.evaluate('''
            (() => {
                const selectedSeats = document.querySelectorAll('#TBL td[style*="icon_chair_select"]');
                return selectedSeats.length;
            })()
        ''')
        if isinstance(check_result, int):
            already_selected_count = check_result
        elif isinstance(check_result, dict):
            already_selected_count = check_result.get('value', 0)

        debug.log(f"[KHAM SEAT] Already selected seats: {already_selected_count}")
    except Exception as exc:
        debug.log(f"[KHAM SEAT] Error checking selected seats: {exc}")

    # If already selected enough seats, skip seat selection and go to submit
    if already_selected_count >= ticket_number:
        debug.log(f"[KHAM SEAT] Already have {already_selected_count} seats (need {ticket_number}), skipping to submit")
        is_seat_type_assigned = True
        is_seat_assigned = True
    else:
        # Step 1: Select seat type
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        is_seat_type_assigned = await nodriver_kham_seat_type_auto_select(
            tab, config_dict, area_keyword
        )

        # Step 2: Select seats
        is_seat_assigned = False
        if is_seat_type_assigned:
            is_seat_assigned = await nodriver_kham_seat_auto_select(tab, config_dict)

    # Step 3: Handle captcha (reuse KHAM OCR)
    is_captcha_sent = False
    if is_seat_assigned and config_dict["ocr_captcha"]["enable"]:
        try:
            # Find captcha input field
            captcha_input = await tab.query_selector('input#CHK')
            debug.log(f"[KHAM SEAT] Captcha input found: {captcha_input is not None}")
            if captcha_input:
                model_name = "UTK0205"
                is_captcha_sent = await nodriver_kham_captcha(
                    tab, config_dict, ocr, model_name
                )
                debug.log(f"[KHAM SEAT] is_captcha_sent: {is_captcha_sent}")
        except Exception as exc:
            debug.log(f"[ERROR] KHAM captcha processing error: {exc}")

    # Step 4: Submit order with improved dialog handling and URL tracking
    is_submit_success = False
    if is_seat_assigned and (not config_dict["ocr_captcha"]["enable"] or is_captcha_sent):
        try:
            # 4.1: Click submit button - UTK0205 uses addShoppingCart() function
            result = await tab.evaluate('''
                (function() {
                    // Method 1: Try calling addShoppingCart() directly (most reliable)
                    if (typeof addShoppingCart === 'function') {
                        addShoppingCart();
                        return true;
                    }
                    // Method 2: Find button inside the addcart anchor
                    const addcartBtn = document.querySelector('a#addcart button');
                    if (addcartBtn && !addcartBtn.disabled) {
                        addcartBtn.click();
                        return true;
                    }
                    // Method 3: Find button with onclick containing addShoppingCart
                    const btnWithOnclick = document.querySelector('button[onclick*="addShoppingCart"]');
                    if (btnWithOnclick && !btnWithOnclick.disabled) {
                        btnWithOnclick.click();
                        return true;
                    }
                    // Method 4: Legacy selector for other KHAM pages
                    const button = document.querySelector('button.sumitButton');
                    if (button && !button.disabled) {
                        button.click();
                        return true;
                    }
                    return false;
                })();
            ''')

            # Convert CDP format (boolean)
            if isinstance(result, list) and len(result) == 2:
                is_submit_success = result[1].get('value', False) if isinstance(result[1], dict) else result
            else:
                is_submit_success = result

            if is_submit_success:
                debug.log("[KHAM SUBMIT] Order submitted successfully")

                # 4.2: Wait for and close success dialog with improved logic + fallback
                dialog_closed = False

                # Initial wait for dialog to appear (1.5 seconds)
                await tab.sleep(1.5)
                debug.log("[KHAM SUBMIT] Initial wait completed, now checking for dialog...")

                for i in range(16):  # 16 attempts * 0.5s = 8 seconds
                    await tab.sleep(0.5)
                    try:
                        # Use JavaScript to check dialog and close (improved selectors)
                        result = await tab.evaluate('''
                            (function() {
                                // Check if dialog exists (multiple selectors)
                                const dialog = document.querySelector('div.ui-dialog');
                                if (dialog) {
                                    // Try multiple button selectors - be more specific
                                    // Selector 1: Class-based (most specific)
                                    let btn = document.querySelector('button.ui-button.ui-corner-all.ui-widget');
                                    // Selector 2: Dialog buttonset
                                    if (!btn) btn = document.querySelector('.ui-dialog-buttonset button');
                                    // Selector 3: Any button in dialog
                                    if (!btn) btn = document.querySelector('div.ui-dialog button');

                                    if (btn) {
                                        // Click the button
                                        btn.click();
                                        return {found: true, clicked: true};
                                    }
                                    return {found: true, clicked: false};
                                }
                                return {found: false, clicked: false};
                            })();
                        ''')

                        # Convert CDP format
                        if isinstance(result, list) and len(result) == 2:
                            result_dict = result[1].get('value', {}) if isinstance(result[1], dict) else {}
                        else:
                            result_dict = result if isinstance(result, dict) else {}

                        dialog_found = result_dict.get('found', False)
                        dialog_clicked = result_dict.get('clicked', False)

                        debug.log(f"[KHAM SUBMIT] Dialog check #{i+1}: found={dialog_found}, clicked={dialog_clicked}")

                        if dialog_found and dialog_clicked:
                            debug.log("[KHAM SUBMIT] Dialog found and clicked via JavaScript")
                            await tab.sleep(0.5)

                            # Verify dialog actually closed (important for stability)
                            verify_result = await tab.evaluate('''
                                (function() {
                                    const dialog = document.querySelector('div.ui-dialog');
                                    return {exists: dialog !== null};
                                })();
                            ''')

                            if isinstance(verify_result, list) and len(verify_result) == 2:
                                verify_dict = verify_result[1].get('value', {}) if isinstance(verify_result[1], dict) else {}
                            else:
                                verify_dict = verify_result if isinstance(verify_result, dict) else {}

                            if not verify_dict.get('exists', True):
                                dialog_closed = True
                                debug.log("[KHAM SUBMIT] Dialog close verified - dialog no longer exists")
                                break
                            else:
                                debug.log("[KHAM SUBMIT] Dialog still exists after click attempt, retrying...")
                        elif dialog_found and not dialog_clicked:
                            debug.log("[KHAM SUBMIT] Dialog found but button click failed, retrying...")
                        elif not dialog_found and i % 4 == 0:
                            # Log periodically that we're still searching
                            debug.log(f"[KHAM SUBMIT] Still searching for dialog... (attempt {i+1}/16)")

                    except Exception as e:
                        debug.log(f"[KHAM SUBMIT] Dialog check #{i+1} exception: {e}")

                if not dialog_closed:
                    debug.log("[KHAM SUBMIT] Dialog detection incomplete - will proceed with fallback URL check")

                # 4.3: Always check for page transition (fallback) - regardless of dialog detection
                # This is more reliable than waiting for dialog to close
                debug.log("[KHAM SUBMIT] Checking for page transition (fallback)...")

                current_url = tab.target.url
                debug.log(f"[KHAM SUBMIT] Current URL: {current_url}")

                # Check if URL changed (maximum 15 seconds wait - more generous fallback)
                url_changed = False
                for i in range(30):  # 30 attempts * 0.5s = 15 seconds (extended from 10s)
                    await tab.sleep(0.5)
                    new_url = tab.target.url
                    if new_url != current_url:
                        debug.log(f"[KHAM SUBMIT] Page transitioned successfully")
                        debug.log(f"[KHAM SUBMIT] New URL: {new_url}")
                        url_changed = True
                        break

                if not url_changed:
                    debug.log("[KHAM SUBMIT] URL did not change after submit")
                    debug.log("[KHAM SUBMIT] Note: KHAM may not auto-redirect - this may be normal")
                    debug.log("[KHAM SUBMIT] Proceeding anyway as submit button was clicked")

                # 4.4: Play sound if enabled
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)

        except Exception as exc:
            debug.log(f"[ERROR] KHAM submit exception: {exc}")
            # Fallback: use JavaScript to force submit
            try:
                await tab.evaluate('addShoppingCart();')
                is_submit_success = True
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)
                debug.log("[KHAM SUBMIT] Submitted via fallback method")
            except Exception as exc2:
                debug.log(f"[ERROR] KHAM fallback submit error: {exc2}")

    debug.log(f"[KHAM SEAT MAIN] Type:{is_seat_type_assigned} "
          f"Seat:{is_seat_assigned} Submit:{is_submit_success}")

    return is_submit_success

# ====================================================================================
# UDN Platform Seat Selection (Feature 010: UDN seat auto select)
# UTK0204 page combines area selection and seat map on the same page
# ====================================================================================

async def nodriver_udn_seat_auto_select(tab, config_dict):
    """
    UDN - UTK0204 座位自動選擇

    UDN 的 UTK0204 頁面同時包含區域選擇和座位地圖。
    點擊區域後，座位地圖會在同一頁面顯示。

    座位元素結構（透過 MCP 測試驗證）：
    - 選擇器：td[title*="排"]
    - 格式：{區域}-{排號}排-{座號}號（如：特B區-10排-19號）
    - 可選座位：background-image 包含 icon_chair_empty_1.gif
    - 已售座位：background-image 包含 icon_chair_sale_1.gif
    """
    is_seat_assigned = False
    ticket_number = config_dict["ticket_number"]
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    try:
        import json
        result = await tab.evaluate(f'''
            (function() {{
                const ticketNumber = {ticket_number};
                const showDebug = {json.dumps(show_debug)};

                // Step 1: Find all seat elements with title containing "排"
                const allSeats = document.querySelectorAll('td[title*="排"]');
                if (allSeats.length === 0) {{
                    if (showDebug) console.log('[UDN SEAT] No seat map found');
                    return {{ success: false, reason: 'no_seat_map', found: 0, selected: 0 }};
                }}

                // Step 2: Filter available seats by background image
                const availableSeats = [];
                allSeats.forEach(seat => {{
                    const style = seat.getAttribute('style') || '';
                    if (style.includes('icon_chair_empty_1.gif')) {{
                        const title = seat.getAttribute('title');
                        if (title && title.includes('排') && title.includes('號')) {{
                            // Parse seat info: {區域}-{排號}排-{座號}號
                            const parts = title.split('-');
                            if (parts.length >= 3) {{
                                const areaName = parts[0];
                                const rowMatch = parts[1].match(/(\d+)排/);
                                const seatMatch = parts[2].match(/(\d+)號/);
                                if (rowMatch && seatMatch) {{
                                    availableSeats.push({{
                                        element: seat,
                                        title: title,
                                        area: areaName,
                                        row: parseInt(rowMatch[1]),
                                        seat: parseInt(seatMatch[1])
                                    }});
                                }}
                            }}
                        }}
                    }}
                }});

                if (showDebug) {{
                    console.log('[UDN SEAT] Total seats: ' + allSeats.length);
                    console.log('[UDN SEAT] Available seats: ' + availableSeats.length);
                }}

                if (availableSeats.length === 0) {{
                    return {{ success: false, reason: 'no_available_seats', found: allSeats.length, selected: 0 }};
                }}

                if (availableSeats.length < ticketNumber) {{
                    return {{ success: false, reason: 'not_enough_seats', found: availableSeats.length, needed: ticketNumber, selected: 0 }};
                }}

                // Step 3: Sort by row (ascending) then by seat number (prefer middle)
                // Strategy: Front rows first, middle seats preferred
                availableSeats.sort((a, b) => {{
                    if (a.row !== b.row) return a.row - b.row;
                    // For same row, calculate distance from middle
                    // Assume middle seat is around 25 (based on typical venue layout)
                    const midSeat = 25;
                    const distA = Math.abs(a.seat - midSeat);
                    const distB = Math.abs(b.seat - midSeat);
                    return distA - distB;
                }});

                // Step 4: Select seats (up to ticketNumber)
                const selectedSeats = [];
                for (let i = 0; i < Math.min(ticketNumber, availableSeats.length); i++) {{
                    const seatInfo = availableSeats[i];
                    seatInfo.element.click();
                    selectedSeats.push(seatInfo.title);
                    if (showDebug) {{
                        console.log('[UDN SEAT] Clicked seat: ' + seatInfo.title);
                    }}
                }}

                return {{
                    success: true,
                    found: availableSeats.length,
                    selected: selectedSeats.length,
                    seats: selectedSeats
                }};
            }})();
        ''')

        if result and result.get('success'):
            is_seat_assigned = True
            debug.log(f"[UDN SEAT] Selected {result.get('selected')} seats: {result.get('seats')}")
        else:
            if debug.enabled:
                reason = result.get('reason', 'unknown') if result else 'no_result'
                debug.log(f"[UDN SEAT] Selection failed: {reason}")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[ERROR] UDN seat selection error: {exc}")
            import traceback
            traceback.print_exc()

    return is_seat_assigned

async def nodriver_udn_seat_select_ticket_type(tab, config_dict):
    """
    UDN - 選擇票種並加入購物車

    點擊座位後，頁面會顯示：
    1. 已選座位資訊（如：特B區-10排-19號）
    2. 票種選擇 combobox
    3. 「加入購物車 Add to Cart」按鈕
    """
    is_success = False
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    try:
        import json
        result = await tab.evaluate(f'''
            (function() {{
                const showDebug = {json.dumps(show_debug)};

                // Step 1: Find ticket type combobox
                // UDN uses <select> element for ticket type selection
                const comboboxes = document.querySelectorAll('select');
                let ticketTypeSelect = null;

                for (const select of comboboxes) {{
                    const options = select.querySelectorAll('option');
                    for (const opt of options) {{
                        // Look for price pattern like "全票-NT$1,880"
                        if (opt.textContent.includes('NT$') || opt.textContent.includes('票')) {{
                            ticketTypeSelect = select;
                            break;
                        }}
                    }}
                    if (ticketTypeSelect) break;
                }}

                if (!ticketTypeSelect) {{
                    if (showDebug) console.log('[UDN TICKET] No ticket type select found');
                    return {{ success: false, reason: 'no_ticket_select' }};
                }}

                // Step 2: Select first valid ticket type (skip "請選擇" placeholder)
                const options = ticketTypeSelect.querySelectorAll('option');
                let selectedOption = null;
                for (const opt of options) {{
                    if (opt.textContent.includes('NT$') && !opt.textContent.includes('請選擇')) {{
                        opt.selected = true;
                        ticketTypeSelect.value = opt.value;
                        // Trigger change event
                        ticketTypeSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        selectedOption = opt.textContent;
                        break;
                    }}
                }}

                if (!selectedOption) {{
                    if (showDebug) console.log('[UDN TICKET] No valid ticket type option found');
                    return {{ success: false, reason: 'no_valid_option' }};
                }}

                if (showDebug) {{
                    console.log('[UDN TICKET] Selected ticket type: ' + selectedOption);
                }}

                // Step 3: Find and click "加入購物車" button
                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                let addToCartBtn = null;
                for (const btn of buttons) {{
                    const text = btn.textContent || btn.value || '';
                    if (text.includes('加入購物車') || text.includes('Add to Cart')) {{
                        addToCartBtn = btn;
                        break;
                    }}
                }}

                if (!addToCartBtn) {{
                    if (showDebug) console.log('[UDN TICKET] No add to cart button found');
                    return {{ success: false, reason: 'no_cart_button', ticketType: selectedOption }};
                }}

                // Click the button
                addToCartBtn.click();
                if (showDebug) {{
                    console.log('[UDN TICKET] Clicked add to cart button');
                }}

                return {{
                    success: true,
                    ticketType: selectedOption,
                    buttonClicked: true
                }};
            }})();
        ''')

        if result and result.get('success'):
            is_success = True
            debug.log(f"[UDN TICKET] Added to cart: {result.get('ticketType')}")

            # Wait for dialog and dismiss it
            await tab.sleep(0.5)
            try:
                dialog_result = await tab.evaluate('''
                    (function() {
                        // Find dialog with "完成加入購物車" message
                        const dialogs = document.querySelectorAll('[role="dialog"], .ui-dialog');
                        for (const dialog of dialogs) {
                            const text = dialog.textContent || '';
                            if (text.includes('完成加入購物車') || text.includes('購物車')) {
                                // Find OK button
                                const buttons = dialog.querySelectorAll('button');
                                for (const btn of buttons) {
                                    const btnText = btn.textContent || '';
                                    if (btnText.includes('Ok') || btnText.includes('確定') || btnText === 'Ok') {
                                        btn.click();
                                        return { dismissed: true };
                                    }
                                }
                            }
                        }
                        return { dismissed: false };
                    })();
                ''')
                if dialog_result:
                    debug.log(f"[UDN TICKET] Dialog dismissed: {dialog_result.get('dismissed')}")
            except Exception as dialog_exc:
                debug.log(f"[UDN TICKET] Dialog dismiss error (may be normal): {dialog_exc}")

        else:
            if debug.enabled:
                reason = result.get('reason', 'unknown') if result else 'no_result'
                debug.log(f"[UDN TICKET] Failed: {reason}")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[ERROR] UDN ticket type selection error: {exc}")
            import traceback
            traceback.print_exc()

    return is_success

async def nodriver_udn_seat_main(tab, config_dict):
    """
    UDN UTK0204 座位選擇主流程

    流程（透過 MCP 測試驗證）：
    1. 偵測座位地圖是否存在
    2. 選擇可用座位
    3. 選擇票種
    4. 加入購物車
    5. 處理確認對話框

    Returns:
        bool: True if successfully added to cart
    """
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)
    is_success = False

    # Check if seat map is present
    try:
        seat_map_check_raw = await tab.evaluate('''
            (function() {
                const seats = document.querySelectorAll('td[title*="排"]');
                const availableSeats = Array.from(seats).filter(s => {
                    const style = s.getAttribute('style') || '';
                    return style.includes('icon_chair_empty_1.gif');
                });
                return {
                    hasSeatMap: seats.length > 0,
                    totalSeats: seats.length,
                    availableSeats: availableSeats.length
                };
            })();
        ''')
        seat_map_check = util.parse_nodriver_result(seat_map_check_raw)

        if not seat_map_check or not seat_map_check.get('hasSeatMap'):
            debug.log("[UDN SEAT MAIN] No seat map detected on this page")
            return False

        debug.log(f"[UDN SEAT MAIN] Seat map found: {seat_map_check.get('totalSeats')} total, "
              f"{seat_map_check.get('availableSeats')} available")

        if seat_map_check.get('availableSeats', 0) == 0:
            debug.log("[UDN SEAT MAIN] No available seats")
            return False

    except Exception as exc:
        debug.log(f"[UDN SEAT MAIN] Error checking seat map: {exc}")
        return False

    # Step 1: Select seats
    is_seat_selected = await nodriver_udn_seat_auto_select(tab, config_dict)

    if not is_seat_selected:
        debug.log("[UDN SEAT MAIN] Seat selection failed")
        return False

    # Wait for UI to update after seat selection
    await tab.sleep(0.3)

    # Step 2: Select ticket type and add to cart
    is_success = await nodriver_udn_seat_select_ticket_type(tab, config_dict)

    debug.log(f"[UDN SEAT MAIN] Result: seat_selected={is_seat_selected}, added_to_cart={is_success}")

    return is_success

async def nodriver_ticket_seat_type_auto_select(tab, config_dict, area_keyword_item):
    """
    年代售票 - 自動選擇票別 (UTK0205 座位選擇頁面)
    選擇票價類型，如原價、身障、陪同者等

    [TESTED] 已完整測試 - CDP DOMSnapshot 穿透驗證
    [TESTED] 已完整測試 - 排除關鍵字支援 (FR-022)
    [TESTED] 已完整測試 - 三層關鍵字匹配邏輯

    Reference: chrome_tixcraft.py Line 8957-9048
    使用 CDP DOMSnapshot 穿透 DOM 結構，避免 JavaScript 載入時機問題
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_seat_type_assigned = False

    # Clean keyword quotes
    # NOTE: This function only supports single keyword or space-separated AND logic (e.g., "VIP 區")
    # For multiple keywords with OR logic, caller should use JSON parsing and iterate
    if area_keyword_item and len(area_keyword_item) > 0:
        try:
            area_keyword_clean = area_keyword_item.strip()
            if area_keyword_clean.startswith('"') and area_keyword_clean.endswith('"'):
                area_keyword_clean = area_keyword_clean[1:-1]

            # Use the cleaned keyword directly (no comma split to avoid incorrect AND logic)
            area_keyword_item = area_keyword_clean
        except Exception as e:
            debug.log(f"[TICKET SEAT TYPE] Keyword parse error: {e}")

    try:
        from zendriver import cdp

        # Step 1: Capture DOM snapshot
        debug.log("[TICKET SEAT TYPE] Capturing DOM snapshot...")

        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_dom_rects=True
        ))

        # Step 2: Search for ticket type buttons
        ticket_buttons = []

        if documents and len(documents) > 0:
            document_snapshot = documents[0]
            nodes = document_snapshot.nodes

            # Extract node information
            node_names = [strings[i] for i in nodes.node_name]
            node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
            attributes_list = nodes.attributes
            backend_node_ids = list(nodes.backend_node_id)

            debug.log(f"[TICKET SEAT TYPE] Total nodes in snapshot: {len(node_names)}")

            # Step 3: Search for buttons with setType onclick
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'BUTTON':
                    # Parse attributes
                    attrs = {}
                    if i < len(attributes_list):
                        attr_indices = attributes_list[i]
                        for j in range(0, len(attr_indices), 2):
                            if j + 1 < len(attr_indices):
                                key = strings[attr_indices[j]]
                                val = strings[attr_indices[j + 1]]
                                attrs[key] = val

                    # Check if this is a ticket type button (onclick contains setType)
                    onclick = attrs.get('onclick', '')
                    button_class = attrs.get('class', '')
                    button_disabled = 'disabled' in attrs

                    if 'setType' in onclick:
                        # Get button text from child text nodes
                        # Strategy 1: Search for first non-empty text node in children
                        button_text = ''
                        for j in range(i + 1, min(i + 10, len(node_names))):  # Check next 10 nodes
                            if node_names[j] == '#text':
                                text_content = node_values[j].strip()
                                if text_content and len(text_content) > 0:
                                    button_text = text_content
                                    debug.log(f"[TICKET SEAT TYPE] Extracted text from node {j}: '{button_text}'")
                                    break
                            # Stop when encountering another element (DIV, BUTTON, etc.)
                            elif node_names[j] in ['DIV', 'BUTTON', 'INPUT', 'SPAN', 'A']:
                                break

                        # Strategy 2: Fallback - Extract from onclick attribute if text is empty
                        if not button_text and 'setType' in onclick:
                            import re
                            match = re.search(r"setType\('[^']*','([^']*)'\)", onclick)
                            if match:
                                button_text = match.group(1)
                                debug.log(f"[TICKET SEAT TYPE] Extracted text from onclick: '{button_text}'")

                        ticket_buttons.append({
                            'backend_node_id': backend_node_ids[i],
                            'class': button_class,
                            'onclick': onclick,
                            'disabled': button_disabled,
                            'text': button_text,
                            'index': i
                        })

                        debug.log(f"[TICKET SEAT TYPE] Found button #{len(ticket_buttons)}: text='{button_text}', disabled={button_disabled}")

        debug.log(f"[TICKET SEAT TYPE] Found {len(ticket_buttons)} ticket type button(s)")

        if len(ticket_buttons) == 0:
            debug.log("[TICKET SEAT TYPE] No ticket type buttons found")
            return False

        # Step 4: Filter disabled buttons
        enabled_buttons = [btn for btn in ticket_buttons if not btn['disabled']]

        debug.log(f"[TICKET SEAT TYPE] Found {len(enabled_buttons)} enabled button(s)")

        if len(enabled_buttons) == 0:
            debug.log("[TICKET SEAT TYPE] All buttons are disabled")
            return False

        # Step 5: Match button using keyword and exclusion logic
        matched_button = None

        for button in enabled_buttons:
            button_text = button['text']
            if not button_text:
                continue

            # Check exclusion keywords from config
            if util.reset_row_text_if_match_keyword_exclude(config_dict, button_text):
                debug.log(f"[TICKET SEAT TYPE] Excluded by keyword_exclude: {button_text}")
                continue

            # Keyword matching logic
            is_match = True
            if area_keyword_item and len(area_keyword_item) > 0:
                keywords = area_keyword_item.split(' ')
                row_text = util.format_keyword_string(button_text)
                for kw in keywords:
                    formatted_kw = util.format_keyword_string(kw)
                    if formatted_kw not in row_text:
                        is_match = False
                        break

            if is_match:
                matched_button = button
                debug.log(f"[TICKET SEAT TYPE] Matched: {button_text}")
                break

        # If no keyword match, select first enabled button as fallback
        if matched_button is None:
            matched_button = enabled_buttons[0]
            debug.log(f"[TICKET SEAT TYPE] No keyword match, using first button: {matched_button['text']}")

        # Step 6: Click button using CDP
        try:
            # Initialize DOM
            await tab.send(cdp.dom.get_document())

            # Convert backend_node_id to node_id
            result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([matched_button['backend_node_id']]))
            node_id = result[0]

            debug.log(f"[TICKET SEAT TYPE] Button node_id: {node_id}")

            # Scroll element into view
            await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
            await tab.sleep(0.2)

            # Use CDP Runtime.callFunctionOn to click button
            from zendriver.cdp import runtime

            # Resolve node to RemoteObject
            resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))

            # Get object_id from resolved node
            if hasattr(resolved, 'object'):
                remote_object_id = resolved.object.object_id
            elif hasattr(resolved, 'object_id'):
                remote_object_id = resolved.object_id
            else:
                debug.log(f"[TICKET SEAT TYPE] Error: Could not find object_id in resolved node")
                return False

            debug.log(f"[TICKET SEAT TYPE] Resolved button object_id: {remote_object_id}")

            # Call click() on the remote object
            click_result = await tab.send(runtime.call_function_on(
                function_declaration='function() { this.click(); return true; }',
                object_id=remote_object_id,
                return_by_value=True
            ))

            debug.log(f"[TICKET SEAT TYPE] Button clicked, result: {click_result}")

            if click_result:
                is_seat_type_assigned = True
                debug.log(f"[TICKET SEAT TYPE] Successfully clicked: {matched_button['text']}")

                # Wait for seat table to load (initial wait for AJAX to start)
                await tab.sleep(1.5)

                # [Optimized] Smart wait using lightweight querySelector instead of DOM Snapshot
                seats_loaded = False
                for i in range(20):  # Max 10 seconds (20 * 0.5s)
                    try:
                        # Use querySelector - 10x faster than DOM Snapshot
                        check_result = await tab.evaluate('''
                            (() => {
                                const table = document.querySelector('#TBL');
                                // Check for TD with title attribute and cursor:pointer style
                                const seats = document.querySelectorAll('#TBL td[title][style*="cursor: pointer"]');
                                return {
                                    tableFound: !!table,
                                    seatCount: seats.length
                                };
                            })()
                        ''')

                        # Parse result using util function for nodriver CDP format
                        table_found = False
                        seat_count = 0
                        parsed_result = util.parse_nodriver_result(check_result)
                        if isinstance(parsed_result, dict):
                            table_found = parsed_result.get('tableFound', False)
                            seat_count = parsed_result.get('seatCount', 0)

                        # Success condition: table exists AND at least 1 seat found
                        if table_found and seat_count > 0:
                            seats_loaded = True
                            debug.log(f"[TICKET SEAT TYPE] Seats loaded: table found, {seat_count} available seats")
                            break
                        elif i == 19:
                            # Last attempt - show what's missing
                            debug.log(f"[TICKET SEAT TYPE] Warning: table_found={table_found}, seat_count={seat_count}")

                    except Exception as wait_exc:
                        if i == 19:
                            debug.log(f"[TICKET SEAT TYPE] querySelector error: {wait_exc}")

                    await tab.sleep(0.5)

                if not seats_loaded:
                    debug.log("[TICKET SEAT TYPE] Warning: Seats not fully loaded within 10 seconds")
            else:
                debug.log("[TICKET SEAT TYPE] Click failed")

        except Exception as click_exc:
            if debug.enabled:
                debug.log(f"[ERROR] CDP click error: {click_exc}")
                import traceback
                traceback.print_exc()

    except Exception as exc:
        debug.log(f"[ERROR] Ticket seat type selection error: {exc}")
        import traceback
        if debug.enabled:
            traceback.print_exc()

    debug.log(f"[TICKET SEAT TYPE] Assignment result: {is_seat_type_assigned}")

    return is_seat_type_assigned

async def _analyze_seat_quality(tab, config_dict):
    """
    分析座位品質並篩選候選排/列
    職責: 偵測舞台方向、分析座位品質、排優先度排序
    行數: ~32 行

    Returns: dict 包含舞台方向、座位資訊、品質評分
    """
    ticket_number = config_dict["ticket_number"]
    allow_non_adjacent = config_dict["advanced"]["disable_adjacent_seat"]
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    import json
    # 執行 JavaScript 分析座位品質
    result = await tab.evaluate(f'''
        (function() {{
            const ticketNumber = {ticket_number};
            const allowNonAdjacent = {json.dumps(allow_non_adjacent)};
            const showDebug = {json.dumps(show_debug)};
            const MIDDLE_AREA_MIN = 8;
            const MIDDLE_AREA_MAX = 18;

            // 偵測舞台方向
            const stageIcon = document.querySelector('#ctl00_ContentPlaceHolder1_lbStageArrow i');
            let stageDirection = 'up';

            if (showDebug) {{
                console.log('[TICKET SEAT] Stage icon element:', stageIcon ? 'found' : 'not found');
            }}

            if (stageIcon) {{
                if (stageIcon.classList.contains('fa-arrow-circle-up')) stageDirection = 'up';
                else if (stageIcon.classList.contains('fa-arrow-circle-down')) stageDirection = 'down';
                else if (stageIcon.classList.contains('fa-arrow-circle-left')) stageDirection = 'left';
                else if (stageIcon.classList.contains('fa-arrow-circle-right')) stageDirection = 'right';

                if (showDebug) {{
                    console.log('[TICKET SEAT] Detected stage direction:', stageDirection);
                }}
            }} else {{
                if (showDebug) {{
                    console.log('[TICKET SEAT] Stage icon not found, using default: up');
                }}
            }}

            // 【修復 1】取得所有可用座位 - 改用 JavaScript 過濾而不依賴 CSS 屬性選擇器
            const availableSeats = [];
            const allTableRows = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');

            Array.from(allTableRows).forEach(tr => {{
                const allTds = tr.children;
                for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                    const seat = allTds[colIndex];
                    const style = seat.getAttribute('style');
                    const title = seat.getAttribute('title');

                    // 使用 JavaScript 檢查（更可靠）
                    if (style && title &&
                        style.includes('cursor: pointer') &&
                        style.includes('icon_chair_empty')) {{
                        availableSeats.push(seat);
                    }}
                }}
            }});

            if (showDebug) {{
                console.log('[TICKET SEAT] Stage: ' + stageDirection + ', Available: ' + availableSeats.length);
            }}

            return {{
                direction: stageDirection,
                availableSeats: availableSeats.map(s => s.getAttribute('title')),
                totalSeats: availableSeats.length
            }};
        }})();
    ''')

    # 轉換 CDP 格式 using util function
    result_dict = util.parse_nodriver_result(result) if not isinstance(result, dict) else result
    return result_dict if isinstance(result_dict, dict) else {}

async def _find_best_seats_in_row(tab, seat_analysis, config_dict):
    """
    在候選排/列中尋找最佳座位組合
    職責: 分組座位、分析品質、排優先度排序、搜尋最佳組合
    行數: ~35 行

    Args: seat_analysis 來自 _analyze_seat_quality 的結果
    Returns: dict 包含選定的座位集合
    """
    ticket_number = config_dict["ticket_number"]
    allow_non_adjacent = config_dict["advanced"]["disable_adjacent_seat"]
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    stage_direction = seat_analysis.get('direction', 'up')
    available_titles = seat_analysis.get('availableSeats', [])

    debug.log(f"[TICKET SEAT] Finding best seats: tickets={ticket_number}, "
          f"stage={stage_direction}, adjacent={not allow_non_adjacent}, "
          f"available={len(available_titles)}")

    import json
    # 執行 JavaScript 尋找最佳座位
    result = await tab.evaluate(f'''
        (function() {{
            const ticketNumber = {ticket_number};
            const allowNonAdjacent = {json.dumps(allow_non_adjacent)};
            const showDebug = {json.dumps(show_debug)};
            const stageDirection = {json.dumps(stage_direction)};
            const MIDDLE_AREA_MIN = 8;
            const MIDDLE_AREA_MAX = 18;

            if (showDebug) {{
                console.log('[TICKET SEAT] Starting seat selection algorithm...');
                console.log('[TICKET SEAT] DOM position tracking enabled for aisle detection');
            }}

            // 取得所有可用座位 - 使用與 _analyze_seat_quality 一致的選擇器
            const availableSeats = [];
            const allTableRowsCheck = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');
            Array.from(allTableRowsCheck).forEach(tr => {{
                const allTds = tr.children;
                for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                    const seat = allTds[colIndex];
                    const style = seat.getAttribute('style');
                    const title = seat.getAttribute('title');
                    if (style && title && style.includes('cursor: pointer') && style.includes('icon_chair_empty')) {{
                        availableSeats.push(seat);
                    }}
                }}
            }});

            if (showDebug) {{
                console.log('[TICKET SEAT] Available seats found: ' + availableSeats.length);
            }}

            if (availableSeats.length < ticketNumber) {{
                return {{ success: false, found: availableSeats.length, selected: 0, reason: 'not_enough_seats' }};
            }}

            // 根據舞台方向分組及分析品質
            const selectedSeats = [];
            if (stageDirection === 'up' || stageDirection === 'down') {{
                // 按排分組（加入 DOM 位置追蹤）
                const rows = {{}};
                const allTableRows = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');

                Array.from(allTableRows).forEach((tr, rowIndexInTable) => {{
                    const allTds = tr.children;
                    for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                        const seat = allTds[colIndex];
                        const style = seat.getAttribute('style');
                        const title = seat.getAttribute('title');

                        // 檢查是否為可選座位
                        if (style && title &&
                            style.includes('cursor: pointer') &&
                            style.includes('icon_chair_empty')) {{

                            if (title.includes('排') && title.includes('號')) {{
                                const parts = title.split('-');
                                if (parts.length >= 3) {{
                                    const rowNum = parseInt(parts[1].replace('排', ''));
                                    const seatNum = parseInt(parts[2].replace('號', ''));
                                    if (!rows[rowNum]) rows[rowNum] = [];

                                    // 【改進 1】記錄真實 DOM 位置
                                    rows[rowNum].push({{
                                        elem: seat,
                                        num: seatNum,
                                        title: title,
                                        domIndex: colIndex  // 新增：true 列位置用於走道偵測
                                    }});
                                }}
                            }}
                        }}
                    }}
                }});

                if (showDebug) {{
                    console.log('[TICKET SEAT] Rows grouped: ' + Object.keys(rows).length);
                }}

                // 分析品質並排序
                const rowQuality = [];
                for (const [rowNum, rowSeats] of Object.entries(rows)) {{
                    rowSeats.sort((a, b) => a.num - b.num);
                    const totalSeats = rowSeats.length;
                    const middleSeats = rowSeats.filter(s => s.num >= MIDDLE_AREA_MIN && s.num <= MIDDLE_AREA_MAX);
                    const middleCount = middleSeats.length;
                    const middleRatio = totalSeats > 0 ? middleCount / totalSeats : 0;

                    rowQuality.push({{
                        rowNum: parseInt(rowNum),
                        totalSeats: totalSeats,
                        middleCount: middleCount,
                        middleRatio: middleRatio,
                        seats: rowSeats,
                        middleSeats: middleSeats
                    }});
                }}

                // 三層優先度排序
                rowQuality.sort((a, b) => {{
                    const aHasEnough = a.middleCount >= ticketNumber;
                    const bHasEnough = b.middleCount >= ticketNumber;
                    if (aHasEnough && !bHasEnough) return -1;
                    if (!aHasEnough && bHasEnough) return 1;

                    if (Math.abs(a.middleRatio - b.middleRatio) > 0.1) {{
                        return b.middleRatio - a.middleRatio;
                    }}

                    if (stageDirection === 'up') {{
                        return a.rowNum - b.rowNum;
                    }} else {{
                        return b.rowNum - a.rowNum;
                    }}
                }});

                if (showDebug) {{
                    console.log('[TICKET SEAT] RowQuality count: ' + rowQuality.length);
                    if (rowQuality.length > 0) {{
                        console.log('[TICKET SEAT] First row: ' + rowQuality[0].rowNum +
                                   ', seats=' + rowQuality[0].totalSeats +
                                   ', middle=' + rowQuality[0].middleCount);
                    }}
                }}

                // 搜尋最佳座位組合
                for (const row of rowQuality) {{
                    let found = false;

                    if (!allowNonAdjacent) {{
                        // 【改進 2】先按 DOM 位置排序確保順序正確
                        row.middleSeats.sort((a, b) => a.domIndex - b.domIndex);
                        row.seats.sort((a, b) => a.domIndex - b.domIndex);

                        // 先找中間區域的連續座位
                        if (row.middleSeats.length >= ticketNumber) {{
                            for (let i = 0; i <= row.middleSeats.length - ticketNumber; i++) {{
                                let continuous = true;
                                for (let j = 0; j < ticketNumber - 1; j++) {{
                                    // 【改進 2】使用 DOM 位置差（domGap）判斷連續性
                                    const currentDomIdx = row.middleSeats[i+j].domIndex;
                                    const nextDomIdx = row.middleSeats[i+j+1].domIndex;
                                    const domGap = nextDomIdx - currentDomIdx;

                                    if (domGap > 1) {{
                                        // DOM 位置不連續（中間有走道或空格）
                                        continuous = false;
                                        if (showDebug) {{
                                            console.log('[TICKET SEAT] Aisle detected: ' +
                                                       row.middleSeats[i+j].title + ' to ' +
                                                       row.middleSeats[i+j+1].title +
                                                       ' (domGap=' + domGap + ')');
                                        }}
                                        break;
                                    }}
                                }}
                                if (continuous) {{
                                    for (let j = 0; j < ticketNumber; j++) {{
                                        selectedSeats.push(row.middleSeats[i+j]);
                                    }}
                                    found = true;
                                    if (showDebug) {{
                                        console.log('[TICKET SEAT] Selected ' + ticketNumber +
                                                   ' seats from middle area');
                                    }}
                                    break;
                                }}
                            }}
                        }}

                        // 回退到全排搜尋
                        if (!found) {{
                            for (let i = 0; i <= row.seats.length - ticketNumber; i++) {{
                                let continuous = true;
                                for (let j = 0; j < ticketNumber - 1; j++) {{
                                    // 【改進 2】使用 DOM 位置差判斷連續性
                                    const currentDomIdx = row.seats[i+j].domIndex;
                                    const nextDomIdx = row.seats[i+j+1].domIndex;
                                    const domGap = nextDomIdx - currentDomIdx;

                                    if (domGap > 1) {{
                                        continuous = false;
                                        if (showDebug && i === 0) {{
                                            console.log('[TICKET SEAT] Gap in full row: ' +
                                                       row.seats[i+j].title + ' (domGap=' + domGap + ')');
                                        }}
                                        break;
                                    }}
                                }}
                                if (continuous) {{
                                    for (let j = 0; j < ticketNumber; j++) {{
                                        selectedSeats.push(row.seats[i+j]);
                                    }}
                                    found = true;
                                    if (showDebug) {{
                                        console.log('[TICKET SEAT] Selected ' + ticketNumber +
                                                   ' seats from full row');
                                    }}
                                    break;
                                }}
                            }}
                        }}
                    }} else {{
                        // 不連續模式：從中間選起
                        if (row.middleSeats.length >= ticketNumber) {{
                            const startIdx = Math.floor((row.middleSeats.length - ticketNumber) / 2);
                            for (let i = 0; i < ticketNumber; i++) {{
                                selectedSeats.push(row.middleSeats[startIdx + i]);
                            }}
                            found = true;
                        }} else {{
                            const startIdx = Math.max(0, Math.floor((row.totalSeats - ticketNumber) / 2));
                            for (let i = 0; i < Math.min(ticketNumber, row.totalSeats); i++) {{
                                if (startIdx + i < row.seats.length) {{
                                    selectedSeats.push(row.seats[startIdx + i]);
                                }}
                            }}
                            found = true;
                        }}
                    }}

                    if (selectedSeats.length >= ticketNumber) break;
                }}
            }} else {{
                // 【改進 3】按列分組（舞台在左/右）- 加入 DOM 位置追蹤與品質分析
                const columns = {{}};
                const MIDDLE_ROW_MIN = 5;
                const MIDDLE_ROW_MAX = 15;

                // 遍歷表格，按列收集座位並記錄 DOM 垂直位置
                const allTableRows = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');
                Array.from(allTableRows).forEach((tr, rowIndexInTable) => {{
                    const allTds = tr.children;
                    for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                        const seat = allTds[colIndex];
                        const style = seat.getAttribute('style');
                        const title = seat.getAttribute('title');

                        if (style && title &&
                            style.includes('cursor: pointer') &&
                            style.includes('icon_chair_empty')) {{

                            if (title.includes('排') && title.includes('號')) {{
                                const parts = title.split('-');
                                if (parts.length >= 3) {{
                                    const rowNum = parseInt(parts[1].replace('排', ''));
                                    const seatNum = parseInt(parts[2].replace('號', ''));
                                    if (!columns[seatNum]) columns[seatNum] = [];

                                    // 記錄垂直 DOM 位置（用於垂直連續性檢查）
                                    columns[seatNum].push({{
                                        elem: seat,
                                        rowNum: rowNum,
                                        title: title,
                                        domIndex: rowIndexInTable  // 垂直位置
                                    }});
                                }}
                            }}
                        }}
                    }}
                }});

                // 分析列品質（中間排優先）
                const columnQuality = [];
                for (const [seatNum, columnSeats] of Object.entries(columns)) {{
                    columnSeats.sort((a, b) => a.domIndex - b.domIndex);
                    const totalSeats = columnSeats.length;
                    const middleSeats = columnSeats.filter(s =>
                        s.rowNum >= MIDDLE_ROW_MIN && s.rowNum <= MIDDLE_ROW_MAX
                    );
                    const middleCount = middleSeats.length;
                    const middleRatio = totalSeats > 0 ? middleCount / totalSeats : 0;

                    columnQuality.push({{
                        seatNum: parseInt(seatNum),
                        totalSeats: totalSeats,
                        middleCount: middleCount,
                        middleRatio: middleRatio,
                        seats: columnSeats,
                        middleSeats: middleSeats
                    }});
                }}

                // 三層優先度排序
                columnQuality.sort((a, b) => {{
                    const aHasEnough = a.middleCount >= ticketNumber;
                    const bHasEnough = b.middleCount >= ticketNumber;
                    if (aHasEnough && !bHasEnough) return -1;
                    if (!aHasEnough && bHasEnough) return 1;

                    if (Math.abs(a.middleRatio - b.middleRatio) > 0.1) {{
                        return b.middleRatio - a.middleRatio;
                    }}

                    // 舞台方向排序
                    if (stageDirection === 'left') {{
                        return a.seatNum - b.seatNum;  // 左舞台：小號優先
                    }} else {{
                        return b.seatNum - a.seatNum;  // 右舞台：大號優先
                    }}
                }});

                if (showDebug) {{
                    console.log('[TICKET SEAT] Left/Right stage: ' + stageDirection +
                               ', columns found: ' + columnQuality.length);
                }}

                // 搜尋最佳座位組合（兩階段搜尋 + DOM 連續性檢查）
                for (const column of columnQuality) {{
                    let found = false;

                    if (!allowNonAdjacent) {{
                        // 先找中間排的連續座位
                        if (column.middleSeats.length >= ticketNumber) {{
                            for (let i = 0; i <= column.middleSeats.length - ticketNumber; i++) {{
                                let continuous = true;
                                for (let j = 0; j < ticketNumber - 1; j++) {{
                                    const domGap = column.middleSeats[i+j+1].domIndex -
                                                  column.middleSeats[i+j].domIndex;
                                    if (domGap > 1) {{
                                        continuous = false;
                                        break;
                                    }}
                                }}
                                if (continuous) {{
                                    for (let j = 0; j < ticketNumber; j++) {{
                                        selectedSeats.push(column.middleSeats[i+j]);
                                    }}
                                    found = true;
                                    if (showDebug) {{
                                        console.log('[TICKET SEAT] Selected from middle rows');
                                    }}
                                    break;
                                }}
                            }}
                        }}

                        // 回退到全列搜尋
                        if (!found) {{
                            for (let i = 0; i <= column.seats.length - ticketNumber; i++) {{
                                let continuous = true;
                                for (let j = 0; j < ticketNumber - 1; j++) {{
                                    const domGap = column.seats[i+j+1].domIndex -
                                                  column.seats[i+j].domIndex;
                                    if (domGap > 1) {{
                                        continuous = false;
                                        break;
                                    }}
                                }}
                                if (continuous) {{
                                    for (let j = 0; j < ticketNumber; j++) {{
                                        selectedSeats.push(column.seats[i+j]);
                                    }}
                                    found = true;
                                    if (showDebug) {{
                                        console.log('[TICKET SEAT] Selected from full column');
                                    }}
                                    break;
                                }}
                            }}
                        }}
                    }} else {{
                        // 不連續模式：從中間選起
                        if (column.middleSeats.length >= ticketNumber) {{
                            const startIdx = Math.floor((column.middleSeats.length - ticketNumber) / 2);
                            for (let i = 0; i < ticketNumber; i++) {{
                                selectedSeats.push(column.middleSeats[startIdx + i]);
                            }}
                            found = true;
                        }} else {{
                            const startIdx = Math.max(0, Math.floor((column.totalSeats - ticketNumber) / 2));
                            for (let i = 0; i < Math.min(ticketNumber, column.totalSeats); i++) {{
                                if (startIdx + i < column.seats.length) {{
                                    selectedSeats.push(column.seats[startIdx + i]);
                                }}
                            }}
                            found = true;
                        }}
                    }}

                    if (selectedSeats.length >= ticketNumber) break;
                }}
            }}

            // 【跨排選座】當允許不連續座位且仍未選到足夠座位時，從所有可用座位中選擇
            if (selectedSeats.length < ticketNumber && allowNonAdjacent && availableSeats.length >= ticketNumber) {{
                if (showDebug) {{
                    console.log('[TICKET SEAT] Cross-row selection: selecting from all available seats');
                }}
                selectedSeats.length = 0; // 清空之前的結果
                // 收集所有可用座位資訊
                const allSeatsWithInfo = [];
                const crossRowTableRows = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');
                Array.from(crossRowTableRows).forEach((tr, rowIdx) => {{
                    const allTds = tr.children;
                    for (let colIdx = 0; colIdx < allTds.length; colIdx++) {{
                        const seat = allTds[colIdx];
                        const style = seat.getAttribute('style');
                        const title = seat.getAttribute('title');
                        if (style && title && style.includes('cursor: pointer') && style.includes('icon_chair_empty')) {{
                            allSeatsWithInfo.push({{ title: title, rowIdx: rowIdx, colIdx: colIdx }});
                        }}
                    }}
                }});
                // 選擇前 ticketNumber 個座位
                for (let i = 0; i < Math.min(ticketNumber, allSeatsWithInfo.length); i++) {{
                    selectedSeats.push(allSeatsWithInfo[i]);
                }}
            }}

            if (showDebug) {{
                console.log('[TICKET SEAT] Algorithm result: found=' + availableSeats.length +
                           ', selected=' + selectedSeats.length);
                if (selectedSeats.length > 0) {{
                    console.log('[TICKET SEAT] Selected titles: ' +
                               selectedSeats.map(s => s.title).join(', '));
                }}
            }}

            return {{
                success: selectedSeats.length > 0,
                selectedSeats: selectedSeats.map(s => ({{ title: s.title }})),
                count: selectedSeats.length
            }};
        }})();
    ''')

    # 轉換 CDP 格式 using util function
    result_dict = util.parse_nodriver_result(result) if not isinstance(result, dict) else result

    debug.log(f"[TICKET SEAT] _find_best_seats result: {result_dict}")

    return result_dict if isinstance(result_dict, dict) else {}

async def _execute_seat_selection(tab, seats_to_click, config_dict):
    """
    執行座位點擊操作
    職責: 驗證座位、點擊座位、回報結果
    行數: ~48 行

    【修復 BUG-001】使用演算法選定的座位 title 列表而非簡單取前 N 個
    問題：原邏輯忽略 seats_to_click 參數，導致選到不連續座位
    解決：使用 selectedSeats 中的 title 列表精確定位並點擊

    Args: seats_to_click 來自 _find_best_seats_in_row 的座位集合
    Returns: bool 是否成功選擇座位
    """
    ticket_number = config_dict["ticket_number"]
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    # 【修復 BUG-001】提取演算法選定的座位 title 列表
    selected_seat_titles = []
    use_algorithm_result = False

    debug.log(f"[TICKET SEAT] _execute input: type={type(seats_to_click)}, value={seats_to_click}")

    if seats_to_click and isinstance(seats_to_click, dict):
        if 'selectedSeats' in seats_to_click and seats_to_click['selectedSeats']:
            selected_seat_titles = [s['title'] for s in seats_to_click['selectedSeats']]
            use_algorithm_result = len(selected_seat_titles) > 0

            debug.log(f"[TICKET SEAT] Using algorithm selected seats: {selected_seat_titles}")
        else:
            debug.log(f"[TICKET SEAT] No selectedSeats in result, keys={seats_to_click.keys()}")

    import json
    # 執行 JavaScript 點擊座位
    result = await tab.evaluate(f'''
        (function() {{
            const ticketNumber = {ticket_number};
            const showDebug = {json.dumps(show_debug)};
            const selectedTitles = {json.dumps(selected_seat_titles)};
            const useAlgorithm = {json.dumps(use_algorithm_result)};

            let clickedCount = 0;
            const clickedTitles = [];

            // 【修復 BUG-001】優先使用演算法選定的座位
            if (useAlgorithm && selectedTitles.length > 0) {{
                for (const targetTitle of selectedTitles) {{
                    // 使用與 _analyze_seat_quality 一致的選擇器
                    let seat = document.querySelector(
                        `table#TBL td[title="${{targetTitle}}"][style*="cursor: pointer"]`
                    );
                    if (!seat) {{
                        seat = document.querySelector(
                            `#locationChoice table td[title="${{targetTitle}}"][style*="cursor: pointer"]`
                        );
                    }}
                    if (seat && seat.getAttribute('style').includes('icon_chair_empty')) {{
                        seat.click();
                        clickedCount++;
                        clickedTitles.push(targetTitle);
                        if (showDebug) {{
                            console.log('[SUCCESS] Selected algorithm seat: ' + targetTitle);
                        }}
                    }}
                }}
            }} else {{
                // [FALLBACK] Algorithm failed - ensure only selecting consecutive seats
                if (showDebug) {{
                    console.log('[FALLBACK] Algorithm result empty, using fallback with direction-aware check');
                }}

                // Step 1: Detect stage direction
                const stageIcon = document.querySelector('#ctl00_ContentPlaceHolder1_lbStageArrow i');
                let stageDirection = 'up'; // default
                if (stageIcon) {{
                    if (stageIcon.classList.contains('fa-arrow-circle-up')) stageDirection = 'up';
                    else if (stageIcon.classList.contains('fa-arrow-circle-down')) stageDirection = 'down';
                    else if (stageIcon.classList.contains('fa-arrow-circle-left')) stageDirection = 'left';
                    else if (stageIcon.classList.contains('fa-arrow-circle-right')) stageDirection = 'right';
                }}
                if (showDebug) {{
                    console.log('[FALLBACK] Stage direction: ' + stageDirection);
                }}

                // 使用與 _analyze_seat_quality 一致的選擇器
                const availableSeats = [];
                const allTableRowsFallback = document.querySelectorAll('table#TBL tbody tr, #locationChoice table tbody tr');
                Array.from(allTableRowsFallback).forEach(tr => {{
                    const allTds = tr.children;
                    for (let colIndex = 0; colIndex < allTds.length; colIndex++) {{
                        const seat = allTds[colIndex];
                        const style = seat.getAttribute('style');
                        const title = seat.getAttribute('title');
                        if (style && title && style.includes('cursor: pointer') && style.includes('icon_chair_empty')) {{
                            availableSeats.push(seat);
                        }}
                    }}
                }});

                let foundSeats = [];

                if (stageDirection === 'up' || stageDirection === 'down') {{
                    // Stage at top/bottom: group by ROW, consecutive = same row
                    const rows = {{}};
                    availableSeats.forEach(seat => {{
                        const title = seat.getAttribute('title');
                        if (title && title.includes('-') && title.includes('排')) {{
                            const parts = title.split('-');
                            if (parts.length >= 2) {{
                                const rowNum = parseInt(parts[1].replace('排', ''));
                                if (!rows[rowNum]) rows[rowNum] = [];
                                const parent = seat.parentElement;
                                const colIdx = parent ? Array.from(parent.children).indexOf(seat) : 0;
                                rows[rowNum].push({{ elem: seat, title: title, colIdx: colIdx }});
                            }}
                        }}
                    }});

                    // Sort rows: up=smaller first, down=larger first
                    const sortedRowNums = Object.keys(rows).sort((a, b) => {{
                        return stageDirection === 'up' ? parseInt(a) - parseInt(b) : parseInt(b) - parseInt(a);
                    }});

                    for (const rowNum of sortedRowNums) {{
                        const rowSeats = rows[rowNum];
                        rowSeats.sort((a, b) => a.colIdx - b.colIdx);

                        for (let i = 0; i <= rowSeats.length - ticketNumber; i++) {{
                            let continuous = true;
                            for (let j = 0; j < ticketNumber - 1; j++) {{
                                if (rowSeats[i + j + 1].colIdx - rowSeats[i + j].colIdx > 1) {{
                                    continuous = false;
                                    break;
                                }}
                            }}
                            if (continuous) {{
                                foundSeats = rowSeats.slice(i, i + ticketNumber);
                                break;
                            }}
                        }}
                        if (foundSeats.length >= ticketNumber) break;
                    }}
                }} else {{
                    // Stage at left/right: group by SEAT NUMBER (column), consecutive = same column
                    const columns = {{}};
                    availableSeats.forEach(seat => {{
                        const title = seat.getAttribute('title');
                        if (title && title.includes('-') && title.includes('號')) {{
                            const parts = title.split('-');
                            if (parts.length >= 3) {{
                                const seatNum = parseInt(parts[2].replace('號', ''));
                                const rowNum = parseInt(parts[1].replace('排', ''));
                                if (!columns[seatNum]) columns[seatNum] = [];
                                const parent = seat.parentElement;
                                const rowIdx = parent && parent.parentElement ?
                                    Array.from(parent.parentElement.children).indexOf(parent) : 0;
                                columns[seatNum].push({{ elem: seat, title: title, rowIdx: rowIdx, rowNum: rowNum }});
                            }}
                        }}
                    }});

                    // Sort columns: left=smaller first, right=larger first
                    const sortedColNums = Object.keys(columns).sort((a, b) => {{
                        return stageDirection === 'left' ? parseInt(a) - parseInt(b) : parseInt(b) - parseInt(a);
                    }});

                    for (const colNum of sortedColNums) {{
                        const colSeats = columns[colNum];
                        colSeats.sort((a, b) => a.rowIdx - b.rowIdx);

                        for (let i = 0; i <= colSeats.length - ticketNumber; i++) {{
                            let continuous = true;
                            for (let j = 0; j < ticketNumber - 1; j++) {{
                                if (colSeats[i + j + 1].rowIdx - colSeats[i + j].rowIdx > 1) {{
                                    continuous = false;
                                    break;
                                }}
                            }}
                            if (continuous) {{
                                foundSeats = colSeats.slice(i, i + ticketNumber);
                                break;
                            }}
                        }}
                        if (foundSeats.length >= ticketNumber) break;
                    }}
                }}

                // Click the found seats
                for (const seatObj of foundSeats) {{
                    seatObj.elem.click();
                    clickedCount++;
                    clickedTitles.push(seatObj.title);
                    if (showDebug) {{
                        console.log('[FALLBACK] Selected seat: ' + seatObj.title);
                    }}
                }}
            }}

            if (showDebug) {{
                console.log('[TICKET SEAT] Clicked ' + clickedCount + '/' + ticketNumber + ' seats');
            }}

            return {{
                success: clickedCount > 0,
                clicked: clickedCount,
                titles: clickedTitles
            }};
        }})();
    ''')

    # 轉換 CDP 格式 using util function
    result_dict = util.parse_nodriver_result(result) if not isinstance(result, dict) else result
    if not isinstance(result_dict, dict):
        result_dict = {}
    return result_dict.get('success', False)

async def nodriver_ticket_seat_auto_select(tab, config_dict):
    """
    年代售票 - 自動選擇座位，優化策略：中間區域優先 + 舞台方向智慧選座

    [TESTED] 已完整測試 - T005 函數重構驗證
    [TESTED] 已完整測試 - 舞台方向感知選座 (T007)
    [TESTED] 已完整測試 - 中間區域優先策略

    Reference: docs/02-development/ticket_seat_selection_algorithm.md

    [T005 重構] 分解為 3 個子函數協調器
    - _analyze_seat_quality(): 分析座位品質
    - _find_best_seats_in_row(): 尋找最佳座位
    - _execute_seat_selection(): 執行座位點擊
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False

    is_seat_assigned = False
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)

    try:
        # Step 1: 分析座位品質
        seat_analysis = await _analyze_seat_quality(tab, config_dict)

        debug.log(f"[TICKET SEAT] Stage direction: {seat_analysis.get('direction', 'unknown')}")
        debug.log(f"[TICKET SEAT] Found {seat_analysis.get('totalSeats', 0)} available seats")

        # Step 2: 尋找最佳座位組合
        best_seats = await _find_best_seats_in_row(tab, seat_analysis, config_dict)

        # Step 3: 執行座位選擇
        is_seat_assigned = await _execute_seat_selection(tab, best_seats, config_dict)

        if is_seat_assigned:
            debug.log(f"[TICKET SEAT] Selected {best_seats.get('count', 0)} seats successfully")

    except Exception as exc:
        debug.log(f"[ERROR] Seat selection error: {exc}")
        import traceback
        if debug.enabled:
            traceback.print_exc()

    return is_seat_assigned

async def nodriver_ticket_seat_main(tab, config_dict, ocr, domain_name):
    """
    年代售票座位選擇主流程：票別選擇 -> 座位選擇 -> 驗證碼 -> 提交

    [TESTED] 已完整測試 - 主流程協調驗證
    [TESTED] 已完整測試 - 票別->座位->驗證碼->提交

    Reference: chrome_tixcraft.py Line 9156-9206
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False, False, False

    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)
    ticket_number = config_dict["ticket_number"]

    # Step 0: Check if seats are already selected (avoid duplicate selection)
    already_selected_count = 0
    try:
        check_result = await tab.evaluate('''
            (() => {
                const selectedSeats = document.querySelectorAll('#TBL td[style*="icon_chair_select"]');
                return selectedSeats.length;
            })()
        ''')
        if isinstance(check_result, int):
            already_selected_count = check_result
        elif isinstance(check_result, dict):
            already_selected_count = check_result.get('value', 0)

        debug.log(f"[TICKET SEAT] Already selected seats: {already_selected_count}")
    except Exception as exc:
        debug.log(f"[TICKET SEAT] Error checking selected seats: {exc}")

    # If already selected enough seats, skip seat selection and go to submit
    if already_selected_count >= ticket_number:
        debug.log(f"[TICKET SEAT] Already have {already_selected_count} seats (need {ticket_number}), skipping to submit")
        is_seat_type_assigned = True
        is_seat_assigned = True
    else:
        # Step 1: Select seat type
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        is_seat_type_assigned = await nodriver_ticket_seat_type_auto_select(
            tab, config_dict, area_keyword
        )

        # Step 2: Select seats
        is_seat_assigned = False
        if is_seat_type_assigned:
            # Additional wait for DOM to fully stabilize after AJAX update
            # Increased to 2s to ensure AJAX completes
            await tab.sleep(2.0)
            is_seat_assigned = await nodriver_ticket_seat_auto_select(tab, config_dict)

    # Step 3: Handle captcha (reuse KHAM OCR)
    is_captcha_sent = False
    if is_seat_assigned and config_dict["ocr_captcha"]["enable"]:
        try:
            # Find captcha input field
            captcha_input = await tab.query_selector('#ctl00_ContentPlaceHolder1_CHK')
            if captcha_input:
                # Reuse KHAM's OCR handling function
                model_name = "UTK0205"
                is_captcha_sent = await nodriver_kham_captcha(
                    tab, config_dict, ocr, model_name
                )
        except Exception as exc:
            debug.log(f"[ERROR] Captcha processing error: {exc}")

    # Step 4: Submit order
    is_submit_success = False
    if is_seat_assigned and (not config_dict["ocr_captcha"]["enable"] or is_captcha_sent):
        try:
            # 【修復 2】使用純 JavaScript 實作以避免 Element 序列化問題，加入多個備用選擇器
            import json
            result = await tab.evaluate(f'''
                (function() {{
                    const showDebug = {json.dumps(show_debug)};

                    // [Optimized] Simplified selector - MCP test confirmed .sumitButton is sufficient
                    const submitButton = document.querySelector('button.sumitButton');

                    if (showDebug) {{
                        console.log('[TICKET SUBMIT] Button found:', !!submitButton);
                        if (submitButton) {{
                            console.log('[TICKET SUBMIT] Button classes:', submitButton.className);
                            console.log('[TICKET SUBMIT] Button text:', submitButton.textContent);
                            console.log('[TICKET SUBMIT] Button disabled:', submitButton.disabled);
                        }}
                    }}

                    if (submitButton && !submitButton.disabled) {{
                        if (showDebug) {{
                            console.log('[TICKET SUBMIT] Clicking submit button...');
                        }}
                        submitButton.click();
                        return true;
                    }}

                    if (showDebug) {{
                        console.log('[TICKET SUBMIT] Submit button not available');
                    }}
                    return false;
                }})();
            ''')

            # 轉換 CDP 格式 (布林值)
            if isinstance(result, list) and len(result) == 2:
                # CDP format: ['value', {'type': 'boolean', 'value': True/False}]
                is_submit_success = result[1].get('value', False) if isinstance(result[1], dict) else result
            else:
                is_submit_success = result

            if is_submit_success:
                debug.log("[TICKET SUBMIT] Order submitted successfully")

                # Check and close success dialog (year ticket shows "加入購物車完成" dialog)
                # Wait up to 5 seconds for dialog to appear
                dialog_closed = False
                for i in range(10):  # 10 attempts * 0.5s = 5 seconds
                    await tab.sleep(0.5)
                    try:
                        dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button[type="button"]')
                        if dialog_btn:
                            debug.log("[TICKET SUBMIT] Success dialog found, closing...")
                            await dialog_btn.click()
                            await tab.sleep(0.5)  # Wait for dialog close animation
                            dialog_closed = True
                            debug.log("[TICKET SUBMIT] Dialog closed successfully")
                            break
                    except Exception as e:
                        if i == 9:
                            debug.log(f"[TICKET SUBMIT] Dialog close attempt failed: {e}")
                        pass

                if not dialog_closed:
                    debug.log("[TICKET SUBMIT] No dialog appeared within 5 seconds")

                # Play sound if enabled
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)

        except Exception as exc:
            debug.log(f"[ERROR] Submit exception: {exc}")
            # Fallback: use JavaScript to force submit (same as Chrome)
            try:
                await tab.evaluate('addShoppingCart1();')
                is_submit_success = True
                if config_dict["advanced"]["play_sound"]["order"]:
                    play_sound_while_ordering(config_dict)
                debug.log("[TICKET SUBMIT] Submitted via fallback method")
            except Exception as exc2:
                debug.log(f"[ERROR] Fallback submit error: {exc2}")

    # Step 5: Check for seat taken dialog and retry if needed
    if not is_submit_success:
        is_seat_taken = await nodriver_ticket_check_seat_taken_dialog(tab, config_dict)
        if is_seat_taken:
            # Seat was taken, retry seat selection
            await tab.sleep(0.5)
            is_seat_assigned = await nodriver_ticket_seat_auto_select(tab, config_dict)

            # Retry captcha if needed
            if is_seat_assigned and config_dict["ocr_captcha"]["enable"]:
                try:
                    captcha_input = await tab.query_selector('#ctl00_ContentPlaceHolder1_CHK')
                    if captcha_input:
                        model_name = "UTK0205"
                        is_captcha_sent = await nodriver_kham_captcha(
                            tab, config_dict, ocr, model_name
                        )
                except Exception as exc:
                    debug.log(f"[ERROR] Retry captcha error: {exc}")

            # Retry submit
            if is_seat_assigned and (not config_dict["ocr_captcha"]["enable"] or is_captcha_sent):
                try:
                    result = await tab.evaluate('''
                        (function() {
                            const button = document.querySelector('button.sumitButton[onclick*="addShoppingCart1"]');
                            if (button && !button.disabled) {
                                button.click();
                                return true;
                            }
                            return false;
                        })();
                    ''')

                    if isinstance(result, list) and len(result) == 2:
                        is_submit_success = result[1].get('value', False) if isinstance(result[1], dict) else result
                    else:
                        is_submit_success = result

                    if is_submit_success:
                        debug.log("[TICKET SUBMIT] Order submitted successfully after retry")

                        # Check and close success dialog (same logic as initial submit)
                        dialog_closed = False
                        for i in range(10):  # 10 attempts * 0.5s = 5 seconds
                            await tab.sleep(0.5)
                            try:
                                dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button[type="button"]')
                                if dialog_btn:
                                    debug.log("[TICKET SUBMIT RETRY] Success dialog found, closing...")
                                    await dialog_btn.click()
                                    await tab.sleep(0.5)
                                    dialog_closed = True
                                    debug.log("[TICKET SUBMIT RETRY] Dialog closed successfully")
                                    break
                            except Exception as e:
                                if i == 9:
                                    debug.log(f"[TICKET SUBMIT RETRY] Dialog close attempt failed: {e}")
                                pass

                        if not dialog_closed:
                            debug.log("[TICKET SUBMIT RETRY] No dialog appeared within 5 seconds")

                        # Play sound
                        if config_dict["advanced"]["play_sound"]["order"]:
                            play_sound_while_ordering(config_dict)

                except Exception as exc:
                    debug.log(f"[ERROR] Retry submit error: {exc}")

    debug.log(f"[TICKET SEAT MAIN] Type:{is_seat_type_assigned} "
          f"Seat:{is_seat_assigned} Submit:{is_submit_success}")

    return is_submit_success

async def nodriver_ticket_check_seat_taken_dialog(tab, config_dict):
    """
    檢查並處理「座位已被訂走」對話框
    對話框內容：「有部分座位已被訂走, 請再重新選取座位 !」

    [TESTED] 已完整測試 - 座位已被訂走對話框處理
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False

    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)
    is_dialog_found = False

    try:
        # 使用純 JavaScript 偵測對話框並點擊 OK 按鈕
        result = await tab.evaluate('''
            (function() {
                const dialog = document.querySelector('#dialog-message');
                if (!dialog) return false;

                const text = dialog.textContent || '';
                if (text.includes('座位已被訂走') || text.includes('請再重新選取座位')) {
                    // 找到 OK 按鈕並點擊
                    const okButton = document.querySelector('.ui-dialog-buttonset button[type="button"]');
                    if (okButton) {
                        okButton.click();
                        console.log('[TICKET DIALOG] Seat taken dialog closed');
                        return true;
                    }
                }
                return false;
            })();
        ''')

        # 轉換 CDP 格式
        if isinstance(result, list) and len(result) == 2:
            is_dialog_found = result[1].get('value', False) if isinstance(result[1], dict) else result
        else:
            is_dialog_found = result

        if is_dialog_found:
            debug.log("[TICKET DIALOG] Seat taken dialog detected and closed, will retry seat selection")

    except Exception as exc:
        debug.log(f"[ERROR] Dialog check error: {exc}")

    return is_dialog_found

async def nodriver_ticket_close_dialog_with_retry(tab, config_dict, max_attempts=5, interval=0.3):
    """
    [ticket.com.tw] 多次檢查並關閉對話框

    解決問題：網頁操作太快，對話框出現速度慢，單次檢查會錯過

    Args:
        tab: NoDriver tab
        config_dict: 設定字典
        max_attempts: 最大嘗試次數 (預設 5 次)
        interval: 每次嘗試間隔秒數 (預設 0.3 秒)

    Returns:
        bool: 是否成功關閉對話框
    """
    show_debug = config_dict["advanced"].get("verbose", False)
    debug = util.create_debug_logger(enabled=show_debug)
    dialog_closed = False

    for attempt in range(max_attempts):
        try:
            # 嘗試多種選擇器
            dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button.ui-button')
            if not dialog_btn:
                dialog_btn = await tab.query_selector('div.ui-dialog-buttonset > button[type="button"]')
            if not dialog_btn:
                dialog_btn = await tab.query_selector('.ui-dialog-buttonset button')

            if dialog_btn:
                await dialog_btn.click()
                dialog_closed = True
                debug.log(f"[TICKET DIALOG] Closed on attempt {attempt + 1}/{max_attempts}")
                # 等待一下讓對話框關閉動畫完成
                await tab.sleep(0.2)
                break
        except Exception as e:
            if attempt == max_attempts - 1:
                debug.log(f"[TICKET DIALOG] Close failed after {max_attempts} attempts: {e}")

        # 等待後再嘗試
        if attempt < max_attempts - 1:
            await tab.sleep(interval)

    return dialog_closed

async def nodriver_ticket_allow_not_adjacent_seat(tab, config_dict):
    """
    允許非連續座位

    [TESTED] 已完整測試 - 非連續座位許可

    Reference: chrome_tixcraft.py Line 9209-9228
    Similar to: nodriver_check_checkbox_enhanced (Line 302)
    """
    # 函數開始檢查暫停 [T004修正]
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    # Use JavaScript to directly check (NoDriver recommended approach)
    is_checked = await tab.evaluate('''
        (function() {
            const checkbox = document.querySelector('div.panel > span > input[type="checkbox"]');
            if (!checkbox) return false;

            // If already checked, return true
            if (checkbox.checked) return true;

            // Try to click
            try {
                checkbox.click();
                return checkbox.checked;
            } catch(e) {
                // Fallback: directly set checked property
                checkbox.checked = true;
                return checkbox.checked;
            }
        })();
    ''')

    debug.log(f"[ALLOW NOT ADJACENT] Checkbox checked: {is_checked}")

    return is_checked

async def nodriver_ticket_switch_to_auto_seat(tab):
    """
    切換到自動選座模式
    Reference: chrome_tixcraft.py Line 9268-9304
    """
    is_switch_to_auto_seat = False

    try:
        # Find switch button (same selector as Chrome version)
        btn = await tab.query_selector('input[value="BUY_TYPE_2"]')

        if btn:
            # Check if already selected
            is_checked = await tab.evaluate('''
                (function(elem) {
                    return elem.checked === true;
                })(arguments[0])
            ''', btn)

            if not is_checked:
                # Not selected, click it
                try:
                    await btn.click()
                    is_switch_to_auto_seat = True
                except Exception:
                    # Fallback: use JavaScript to force click
                    try:
                        await tab.evaluate('''
                            (function(elem) { elem.click(); })(arguments[0])
                        ''', btn)
                        is_switch_to_auto_seat = True
                    except:
                        pass
            else:
                # Already selected
                is_switch_to_auto_seat = True

    except Exception:
        pass

    return is_switch_to_auto_seat

