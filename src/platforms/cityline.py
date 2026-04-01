#!/usr/bin/env python3
#encoding=utf-8
"""platforms/cityline.py -- Cityline platform (cityline.com / venue.cityline.com / shows.cityline.com)."""

import asyncio
import random

import util
from nodriver_common import (
    check_and_handle_pause,
    handle_cloudflare_challenge,
    nodriver_current_url,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    CONST_FROM_TOP_TO_BOTTOM,
)


__all__ = [
    "nodriver_cityline_auto_retry_access",
    "nodriver_cityline_login",
    "nodriver_cityline_date_auto_select",
    "nodriver_cityline_check_login_modal",
    "nodriver_cityline_continue_button_press",
    "nodriver_cityline_area_auto_select",
    "nodriver_cityline_ticket_number_auto_select",
    "nodriver_cityline_next_button_press",
    "nodriver_cityline_performance",
    "nodriver_cityline_check_shopping_basket",
    "nodriver_cityline_purchase_button_press",
    "nodriver_cityline_close_second_tab",
    "nodriver_cityline_cookie_accept",
    "nodriver_cityline_press_buy_button",
    "nodriver_cityline_clean_ads",
    "nodriver_cityline_main",
]

_state = {}


async def nodriver_cityline_auto_retry_access(tab, url, config_dict):
    debug = util.create_debug_logger(config_dict)
    try:
        js = "goEvent();"
        await tab.evaluate(js)
    except Exception as exc:
        debug.log(f"[CITYLINE] goEvent() failed: {exc}")
        pass

    auto_reload_page_interval = config_dict["advanced"]["auto_reload_page_interval"]
    if auto_reload_page_interval > 0:
        await asyncio.sleep(auto_reload_page_interval)

async def nodriver_cityline_login(tab, cityline_account, config_dict):
    """
    Cityline login with auto-click when button becomes enabled
    Strategy: Input email -> Monitor login button -> Auto-click when enabled
    Reference: button.login-btn.submit-btn (becomes enabled after password + verification)
    """


    if not _state.get("account_assigned", False):
        try:
            # Step 1: Input email/account
            el_account = await tab.query_selector('input[type="text"]')
            if el_account:
                await el_account.click()
                await el_account.apply('function (element) {element.value = ""; }')
                await el_account.send_keys(cityline_account)
                await asyncio.sleep(random.uniform(0.4, 0.7))
                _state["account_assigned"] = True
                print(f"[CITYLINE LOGIN] Email entered: {cityline_account[:3]}***")
                print("[CITYLINE LOGIN] Please manually enter password and verification code")
                print("[CITYLINE LOGIN] Monitoring login button... will auto-click when enabled")
        except Exception as exc:
            print(f"[CITYLINE LOGIN] Failed to input email: {exc}")
            pass
    else:
        # Step 2: Solve Turnstile if needed, then auto-click login button
        try:
            # Check if Turnstile is already solved (cf-turnstile-response has value)
            turnstile_solved = await tab.evaluate('''
                (function() {
                    const input = document.querySelector('input[name="cf-turnstile-response"]');
                    return input && input.value && input.value.length > 0;
                })()
            ''')

            if not turnstile_solved and not _state.get("turnstile_attempted", False):
                print("[CITYLINE LOGIN] Turnstile not solved, attempting CDP click...")
                await handle_cloudflare_challenge(tab, config_dict, max_retry=2)
                _state["turnstile_attempted"] = True

            # Check if login button is enabled (no disabled attribute)
            button_enabled = await tab.evaluate('''
                (function() {
                    const loginBtn = document.querySelector('button.login-btn.submit-btn');
                    if (loginBtn) {
                        return !loginBtn.hasAttribute('disabled') && !loginBtn.disabled;
                    }
                    return false;
                })()
            ''')

            if button_enabled:
                # Auto-click the login button
                click_result = await tab.evaluate('''
                    (function() {
                        const loginBtn = document.querySelector('button.login-btn.submit-btn');
                        if (loginBtn) {
                            loginBtn.click();
                            return true;
                        }
                        return false;
                    })()
                ''')

                if click_result:
                    print("[CITYLINE LOGIN] Login button auto-clicked!")
                    _state["turnstile_attempted"] = False
                    await asyncio.sleep(random.uniform(1.0, 2.0))
        except Exception as exc:
            pass  # Silent fail, will retry on next loop

async def nodriver_cityline_date_auto_select(tab, config_dict):
    """
    Cityline date selection with conditional fallback mechanism
    Reference: spec.md FR-003, FR-003a, FR-003b, fallback-mechanism.md
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get("date_auto_fallback", False)  # Read from top level
    auto_reload_coming_soon_page = config_dict["tixcraft"].get("auto_reload_coming_soon_page", False)

    ret = False

    # Stage 1: Query all date buttons
    area_list = None
    try:
        my_css_selector = "button.date-time-position"
        area_list = await tab.query_selector_all(my_css_selector)
    except Exception as exc:
        debug.log(f"[ERROR] find date list fail: {exc}")

    # Stage 2: Format and filter enabled dates
    formated_area_list = []
    if area_list:
        area_list_count = len(area_list)
        debug.log(f"[CITYLINE DATE] Found {area_list_count} date buttons")

        if area_list_count > 0:
            formated_area_list = area_list  # NoDriver elements are already enabled

    # Stage 3: Keyword matching
    matched_blocks = []
    if len(date_keyword) == 0:
        # Empty keyword matches all available dates
        matched_blocks = formated_area_list
    else:
        # Match keyword
        debug.log(f"[DATE KEYWORD] Matching keyword: {date_keyword}")

        for row in formated_area_list:
            row_text = ""
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                debug.log(f"[DEBUG] get row html error: {exc}")
                break

            if len(row_text) > 0:
                debug.log(f"[DEBUG] row_text: {row_text}")
                is_match_area = util.is_row_match_keyword(date_keyword, row_text)
                if is_match_area:
                    matched_blocks.append(row)
                    if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        break

    debug.log(f"[DATE KEYWORD] Matched {len(matched_blocks)} dates")

    # Stage 4: Conditional fallback mechanism
    if len(matched_blocks) == 0:
        if date_auto_fallback:
            # Fallback mode: select from all available dates
            matched_blocks = formated_area_list
            debug.log(f"[DATE FALLBACK] date_auto_fallback=true, selecting from all available dates (total: {len(formated_area_list)})")
        else:
            # Strict mode
            debug.log("[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            if auto_reload_coming_soon_page and len(formated_area_list) == 0:
                # Auto reload if no dates available
                debug.log("[DATE FALLBACK] Auto-reloading page...")
                try:
                    await asyncio.sleep(config_dict["advanced"]["auto_reload_page_interval"])
                    await tab.reload()
                except:
                    pass
            else:
                debug.log("[DATE FALLBACK] Waiting for manual intervention...")
            return False

    # Stage 5: Select target date
    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if target_area:
        try:
            await target_area.scroll_into_view()
            await target_area.click()
            debug.log("[CITYLINE DATE] Purchase button clicked")

            # Wait for Cloudflare Turnstile (FR-012)
            debug.log("[CITYLINE DATE] Waiting 3 seconds for Cloudflare Turnstile...")
            await asyncio.sleep(3)

            ret = True
        except Exception as exc:
            debug.log(f"[CITYLINE DATE] click date button fail: {exc}")

    return ret

async def nodriver_cityline_check_login_modal(tab, config_dict):
    """
    Check and handle login modal on eventDetail page
    Reference: .temp/cityline/54510/1.html - div.modal-content with login form
    Uses state flag to prevent duplicate clicks on same modal
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_modal_handled = False


    try:
        # Wait for modal to appear (if it will)
        await asyncio.sleep(random.uniform(1.0, 1.5))

        # Check if login modal exists and is visible
        modal_visible = await tab.evaluate('''
            (function() {
                const modal = document.querySelector('div.modal-content');
                const loginBtn = document.querySelector('button.btn-login');
                if (modal && loginBtn) {
                    // Check if modal is actually visible (display != none, opacity > 0)
                    const style = window.getComputedStyle(modal);
                    return style.display !== 'none' && style.opacity !== '0';
                }
                return false;
            })()
        ''')

        if modal_visible and not _state.get("modal_handled", False):
            debug.log("[CITYLINE LOGIN MODAL] Login modal detected, solving Turnstile...")

            # Attempt to solve Turnstile via CDP before waiting for button
            try:
                await handle_cloudflare_challenge(tab, config_dict, max_retry=2)
            except Exception as cf_exc:
                debug.log(f"[CITYLINE LOGIN MODAL] Turnstile auto-solve failed: {cf_exc}")

            # Wait for login button to be enabled (opacity: 1 after Turnstile)
            button_enabled = False
            max_wait = 10  # Maximum 10 seconds
            for i in range(max_wait):
                button_enabled = await tab.evaluate('''
                    (function() {
                        const loginBtn = document.querySelector('button.btn-login');
                        if (loginBtn) {
                            const style = window.getComputedStyle(loginBtn);
                            return parseFloat(style.opacity) === 1;
                        }
                        return false;
                    })()
                ''')

                if button_enabled:
                    debug.log(f"[CITYLINE LOGIN MODAL] Button enabled after {i}s")
                    break

                await asyncio.sleep(1)

            if button_enabled:
                # Use CDP to click the login button (to properly trigger onclick event)
                try:
                    login_btn = await tab.find('button.btn-login', timeout=3)
                    if login_btn:
                        await login_btn.click()
                        debug.log("[CITYLINE LOGIN MODAL] Login button clicked successfully (CDP)")
                        is_modal_handled = True
                        _state["modal_handled"] = True  # Mark as handled to prevent duplicate clicks

                        # Wait longer for modal to fully close and process
                        await asyncio.sleep(random.uniform(4.0, 5.0))
                    else:
                        debug.log("[CITYLINE LOGIN MODAL] Login button not found")
                except Exception as e:
                    debug.log(f"[CITYLINE LOGIN MODAL] Failed to click login button: {e}")
            else:
                debug.log("[CITYLINE LOGIN MODAL] Button not enabled after timeout")
        elif _state["modal_handled"]:
            # Modal already handled, skip silently
            pass
        else:
            debug.log("[CITYLINE LOGIN MODAL] No login modal detected")

    except Exception as exc:
        debug.log(f"[CITYLINE LOGIN MODAL] Login modal check failed: {exc}")

    return is_modal_handled

async def nodriver_cityline_continue_button_press(tab, config_dict):
    """
    Click the 'Continue' button on eventDetail page to proceed to performance page
    Reference: .temp/cityline/54510/1.html - button.btn-outline-primary.purchase-btn
    Note: Login modal is already handled in parent function, no need to check again
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_button_clicked = False

    try:
        # Wait a moment for page to stabilize
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Check if continue button exists
        button_exists = await tab.evaluate('''
            (function() {
                const btn = document.querySelector('button.btn-outline-primary.purchase-btn');
                return btn !== null && btn.offsetParent !== null;
            })()
        ''')

        if button_exists:
            debug.log("[CITYLINE CONTINUE] Continue button found, attempting to click...")

            # Click the continue button
            click_result = await tab.evaluate('''
                (function() {
                    const btn = document.querySelector('button.btn-outline-primary.purchase-btn');
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            ''')

            if click_result:
                debug.log("[CITYLINE CONTINUE] Continue button clicked successfully")
                is_button_clicked = True

                # Wait for navigation to performance page
                await asyncio.sleep(random.uniform(2.0, 3.0))
            else:
                debug.log("[CITYLINE CONTINUE] Failed to click continue button via JS")
        else:
            debug.log("[CITYLINE CONTINUE] Continue button not found")

    except Exception as exc:
        debug.log(f"[CITYLINE CONTINUE] Continue button press failed: {exc}")

    return is_button_clicked

async def nodriver_cityline_area_auto_select(tab, config_dict):
    """
    Cityline area selection with conditional fallback mechanism
    Reference: spec.md FR-004, FR-004a, FR-004b, fallback-mechanism.md
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    area_auto_fallback = config_dict.get("area_auto_fallback", False)  # Read from top level

    is_price_assigned = False

    # Stage 1: Query all area options
    area_list = None
    try:
        my_css_selector = "div.form-check"
        area_list = await tab.query_selector_all(my_css_selector)
    except Exception as exc:
        debug.log(f"[ERROR] find area list fail: {exc}")

    # Stage 2: Filter soldout areas
    available_areas = []
    if area_list:
        area_list_count = len(area_list)
        debug.log(f"[CITYLINE AREA] Found {area_list_count} area options")

        for row in area_list:
            is_available = True
            try:
                # Check soldout status
                soldout_span = await row.query_selector('span.price-limited > span[data-i18n*="soldout"]')
                if soldout_span:
                    is_available = False
            except:
                pass

            if is_available:
                available_areas.append(row)

        if debug.enabled:
            soldout_count = area_list_count - len(available_areas)
            debug.log(f"[CITYLINE AREA] Filtered {soldout_count} soldout areas, {len(available_areas)} available")

    # Stage 3: Keyword matching
    matched_areas = []
    if len(area_keyword) == 0:
        # Empty keyword matches all available areas
        matched_areas = available_areas
    else:
        # Match keyword
        for row in available_areas:
            row_text = ""
            try:
                row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except Exception as exc:
                debug.log(f"[DEBUG] get row html error: {exc}")
                break

            if len(row_text) > 0:
                # Check keyword exclude
                if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                    row_text = ""

            if len(row_text) > 0:
                row_text = util.format_keyword_string(row_text)
                debug.log(f"[DEBUG] row_text: {row_text}")

                # AND logic keyword matching
                is_match_area = True
                area_keyword_array = area_keyword.split(' ')
                for keyword in area_keyword_array:
                    keyword = util.format_keyword_string(keyword)
                    if keyword not in row_text:
                        is_match_area = False
                        break

                if is_match_area:
                    matched_areas.append(row)
                    if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        break

    debug.log(f"[AREA KEYWORD] Matched {len(matched_areas)} areas")

    # Stage 4: Conditional fallback mechanism
    if len(matched_areas) == 0:
        if area_auto_fallback:
            # Fallback mode: select from all available areas
            matched_areas = available_areas
            debug.log(f"[AREA FALLBACK] area_auto_fallback=true, selecting from all available areas (total: {len(available_areas)})")
        else:
            # Strict mode: wait for manual intervention
            debug.log("[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            debug.log("[AREA FALLBACK] Waiting for manual intervention to avoid selecting unwanted area...")
            return False

    # Stage 5: Select target area
    target_area = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)
    if target_area:
        try:
            # Find radio button within target area
            radio_btn = await target_area.query_selector('input[type=radio]')
            if radio_btn:
                await radio_btn.scroll_into_view()
                await radio_btn.click()
                is_price_assigned = True
                debug.log("[CITYLINE AREA] Radio button checked")
        except Exception as exc:
            debug.log(f"[CITYLINE AREA] click radio button fail: {exc}")

    return is_price_assigned

async def nodriver_cityline_ticket_number_auto_select(tab, config_dict):
    """
    Cityline ticket number selection
    Reference: spec.md FR-005, cityline-interface.md
    """
    debug = util.create_debug_logger(config_dict)
    ticket_number = config_dict.get("ticket_number", 1)

    is_ticket_number_assigned = False

    try:
        my_css_selector = "select.select-num"
        select_obj = await tab.query_selector(my_css_selector)

        if select_obj:
            debug.log(f"[CITYLINE TICKET] Ticket number selector found")

            # Use JavaScript to set the select value
            is_ticket_number_assigned = await tab.evaluate(f'''
                (function() {{
                    const select = document.querySelector('{my_css_selector}');
                    if (select) {{
                        const options = select.options;
                        for (let i = 0; i < options.length; i++) {{
                            if (options[i].value == {ticket_number}) {{
                                select.selectedIndex = i;
                                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                return true;
                            }}
                        }}
                    }}
                    return false;
                }})();
            ''')

            if is_ticket_number_assigned:
                debug.log(f"[CITYLINE TICKET] Ticket number set to {ticket_number}")
    except Exception as exc:
        debug.log(f"[CITYLINE TICKET] Ticket number selection fail: {exc}")

    return is_ticket_number_assigned

async def nodriver_cityline_next_button_press(tab):
    """
    Cityline next button press
    Reference: spec.md FR-006, cityline-interface.md
    """
    is_button_clicked = False

    try:
        # Cityline express purchase button selectors (based on HTML analysis)
        # Reference: .temp/cityline/54510/2.html - button#expressPurchaseBtn
        selectors = [
            'button#expressPurchaseBtn',                      # ID selector (primary)
            'button.btn-express-purchase',                    # Class selector
            'button.purchase-btn.btn-express-purchase',      # Compound selector
            'button[onclick*="expressPurchaseCallBack"]',    # onclick attribute
            'button[type="submit"]',                          # Generic fallback
            'button.btn-next',                                # Legacy fallback
            'input[type="submit"]'                            # Last resort fallback
        ]

        for selector in selectors:
            try:
                next_btn = await tab.query_selector(selector)
                if next_btn:
                    await next_btn.scroll_into_view()
                    await next_btn.click()
                    is_button_clicked = True
                    print(f"[CITYLINE] Next button clicked: {selector}")
                    break
            except:
                continue
    except Exception as exc:
        print(f"[CITYLINE] Next button press fail: {exc}")

    return is_button_clicked

async def nodriver_cityline_performance(tab, config_dict):
    """
    Cityline performance page (date + area + ticket number + next button)
    Reference: .temp/cityline/54510/2.html
    Returns True only if the entire flow completes (including next button click)
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    is_date_assigned = False
    is_price_assigned = False
    is_button_clicked = False

    # Step 1: Date selection (if date buttons exist on this page)
    is_date_assigned = await nodriver_cityline_date_auto_select(tab, config_dict)

    if is_date_assigned:
        # Step 2: Area selection
        is_price_assigned = await nodriver_cityline_area_auto_select(tab, config_dict)

        if is_price_assigned:
            # Step 3: Ticket number selection
            is_ticket_number_assigned = await nodriver_cityline_ticket_number_auto_select(tab, config_dict)

            if is_ticket_number_assigned:
                # Step 4: Press next button
                await asyncio.sleep(random.uniform(0.3, 0.7))
                is_button_clicked = await nodriver_cityline_next_button_press(tab)

    # Return True only if next button was successfully clicked
    return is_button_clicked

async def nodriver_cityline_check_shopping_basket(tab, config_dict):
    """
    Check if ticket successfully added to shopping basket and play notification sound (once only)
    Reference: .temp/cityline/54510/3.html - shoppingBasket page
    """
    debug = util.create_debug_logger(config_dict)


    try:
        current_url = await tab.evaluate('window.location.href')

        if '/shoppingBasket' in current_url:
            # Only play sound once
            if not _state.get("played_sound_order", False):
                print("[CITYLINE SUCCESS] Ticket added to shopping basket!")

                # Play success sound and send Discord notification
                if config_dict["advanced"]["play_sound"]["order"]:
                    try:
                        play_sound_while_ordering(config_dict)
                    except Exception as sound_exc:
                        debug.log(f"[CITYLINE] Sound error: {sound_exc}")
                send_discord_notification(config_dict, "order", "Cityline")
                send_telegram_notification(config_dict, "order", "Cityline")
                _state["played_sound_order"] = True

            # Return True to indicate we're on checkout page
            return True

    except Exception as e:
        debug.log(f"[CITYLINE] Checkout check error: {e}")

    return False

async def nodriver_cityline_purchase_button_press(tab, config_dict):
    """
    Cityline eventDetail page processing (NO DATE SELECTION HERE)

    eventDetail page flow:
    1. Click 'Continue' button to proceed to performance page

    Note:
    - Login modal is checked in main loop (outside this function)
    - Date/Area selection happens on performance page, NOT here
    Reference: .temp/cityline/54510/1.html
    """
    debug = util.create_debug_logger(config_dict)

    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    is_button_clicked = False

    # Click 'Continue' button to go to performance page
    debug.log("[CITYLINE EVENTDETAIL] Clicking continue button...")
    is_button_clicked = await nodriver_cityline_continue_button_press(tab, config_dict)

    return is_button_clicked

async def nodriver_cityline_close_second_tab(tab, url):
    new_tab = tab
    #print("tab count:", len(tab.browser.tabs))
    if len(tab.browser.tabs) > 1:
        # wait page ready.
        await asyncio.sleep(0.3)
        for tmp_tab in tab.browser.tabs:
            if tmp_tab != tab:
                tmp_url, is_quit_bot = await nodriver_current_url(tmp_tab)
                if len(tmp_url) > 0:
                    if tmp_url[:5] == "https":
                        await new_tab.activate()
                        await tab.close()
                        await asyncio.sleep(0.3)
                        new_tab = tmp_tab
                        break
    return new_tab

async def nodriver_cityline_cookie_accept(tab):
    """
    Cityline cookie consent acceptance
    Reference: spec.md FR-010
    """
    is_accepted = False

    try:
        # Try to find and click cookie accept button
        cookie_selectors = [
            'button.cookie-accept',
            'button[id*="cookie"]',
            'button[class*="cookie"]',
            '.cookie-consent button',
            '#cookie-consent button'
        ]

        for selector in cookie_selectors:
            try:
                cookie_btn = await tab.query_selector(selector)
                if cookie_btn:
                    await cookie_btn.click()
                    is_accepted = True
                    print(f"[CITYLINE] Cookie consent accepted: {selector}")
                    break
            except:
                continue
    except Exception as exc:
        pass

    return is_accepted

async def nodriver_cityline_press_buy_button(tab, config_dict):
    """
    Wait for and click the "Buy Ticket" button on shows.cityline.com event detail page
    Handles JavaScript loading issues and waits for button to appear
    Reference: shows.cityline.com event pages
    """
    # Check pause state
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    debug.log("[CITYLINE] Waiting for buy ticket button to appear...")

    # Polling parameters
    max_wait = 10  # Maximum 10 seconds wait
    check_interval = 0.5  # Check every 0.5 seconds
    max_attempts = int(max_wait / check_interval)
    button_found = False

    for attempt in range(max_attempts):
        try:
            # Check if button exists using JavaScript
            button_exists = await tab.evaluate('''
                (function() {
                    const btn = document.querySelector('button#buyTicketBtn');
                    return btn !== null && btn.offsetParent !== null;
                })()
            ''')

            if button_exists:
                button_found = True
                debug.log(f"[CITYLINE] Buy ticket button found after {attempt * check_interval:.1f}s")
                break

            # Progress indicator
            if attempt > 0 and attempt % 4 == 0:
                debug.log(f"[CITYLINE] Still waiting for button... ({attempt * check_interval:.1f}s elapsed)")

        except Exception as exc:
            debug.log(f"[CITYLINE] Error checking button: {exc}")

        if attempt < max_attempts - 1:
            await asyncio.sleep(check_interval)

    if not button_found:
        print("[CITYLINE] Warning: Buy ticket button not found after timeout")
        print("[CITYLINE] This may be caused by:")
        print("  1. Ad blocker blocking JavaScript files (others.min.js)")
        print("  2. DevTools request blocking rules")
        print("  3. Page not fully loaded")
        print("[CITYLINE] Please manually click the buy ticket button")
        return False

    # Button found, try to click it
    try:
        # Use JavaScript click to avoid issues with visibility
        click_result = await tab.evaluate('''
            (function() {
                const btn = document.querySelector('button#buyTicketBtn');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        ''')

        if click_result:
            debug.log("[CITYLINE] Buy ticket button clicked successfully")
            await asyncio.sleep(random.uniform(1.0, 2.0))
            return True
        else:
            debug.log("[CITYLINE] Failed to click buy ticket button")
            return False

    except Exception as exc:
        debug.log(f"[CITYLINE] Error clicking button: {exc}")
        return False

async def nodriver_cityline_clean_ads(tab):
    """
    Cityline advertisement removal (refined selectors to prevent removing purchase button)
    Reference: spec.md FR-008
    IMPORTANT: Use precise selectors to avoid removing .buyTicketBox or button#buyTicketBtn
    """
    is_ads_removed = False

    try:
        # Use JavaScript to remove ad elements with precise selectors
        is_ads_removed = await tab.evaluate('''
            (function() {
                let removed_count = 0;
                // Use precise selectors to avoid removing purchase-related elements
                const ad_selectors = [
                    'div.advertisement',           // Explicit div.advertisement
                    'div.ad-banner',               // Explicit div.ad-banner
                    'iframe[id*="google_ads"]',    // Google Ads iframes only
                    'div[id^="ATS_"]',             // ATS ad system (Cityline specific)
                    'div.popup-ad',
                    'div.modal-ad'
                    // Removed generic '[id*="ad-"]' and '[class*="ad-"]' to prevent removing button elements
                ];

                ad_selectors.forEach(selector => {
                    const ads = document.querySelectorAll(selector);
                    ads.forEach(ad => {
                        // Verify not removing purchase button or its container
                        const hasButton = ad.querySelector('button#buyTicketBtn');
                        const isBuyBox = ad.classList.contains('buyTicketBox');

                        if (!hasButton && !isBuyBox) {
                            ad.remove();
                            removed_count++;
                        }
                    });
                });

                if (removed_count > 0) {
                    console.log("Removed " + removed_count + " ad elements");
                }

                return removed_count > 0;
            })();
        ''')

        if is_ads_removed:
            print("[CITYLINE] Advertisements removed")
    except Exception as exc:
        pass

    return is_ads_removed

async def nodriver_cityline_main(tab, url, config_dict):

    if not _state:
        _state.update({
            "account_assigned": False,
            "modal_handled": False,
            "turnstile_attempted": False,
            "buy_button_pressed": False,
            "purchase_button_pressed": False,
            "performance_processed": False,
            "played_sound_ticket": False,
            "played_sound_order": False,
            "last_homepage_redirect_time": 0,
        })

    if 'msg.cityline.com' in url or 'event.cityline.com' in url:
        is_dom_ready = False
        try:
            html_body = await tab.get_content()
            if html_body:
                if len(html_body) > 10240:
                    is_dom_ready = True
        except Exception as exc:
            pass
        if is_dom_ready:
            #await nodriver_cityline_auto_retry_access(tab, url, config_dict)
            pass

    # Cookie acceptance (FR-010)
    if '.cityline.com/Events.html' in url:
        await nodriver_cityline_cookie_accept(tab)

    # Advertisement removal (FR-008)
    # Note: Only clean ads on Events.html (homepage), not on event detail pages
    # to prevent removing purchase button
    if '/Events.html' in url:
        await nodriver_cityline_clean_ads(tab)

        # Auto-redirect to target event page when kicked back to homepage
        target_url = config_dict["homepage"]
        homepage_is_root = not target_url or target_url.rstrip('/') in [
            'https://cityline.com',
            'https://www.cityline.com',
            'https://cityline.com/Events.html',
            'https://www.cityline.com/Events.html',
        ]
        if not homepage_is_root:
            debug = util.create_debug_logger(config_dict)
            current_time = time.time()
            last_redirect_time = _state.get("last_homepage_redirect_time", 0)
            redirect_interval = config_dict["advanced"].get("auto_reload_page_interval", 3)
            if redirect_interval <= 0:
                redirect_interval = 3
            if current_time - last_redirect_time > redirect_interval:
                debug.log(f"[CITYLINE] Redirecting to target page: {target_url}")
                try:
                    _state["last_homepage_redirect_time"] = current_time
                    await tab.get(target_url)
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                    # Update URL after redirect
                    url = await tab.evaluate('window.location.href')
                except Exception as exc:
                    debug.log(f"[CITYLINE ERROR] Redirect failed: {exc}")

    # Login page
    if 'cityline.com/Login.html' in url:
        cityline_account = config_dict["accounts"]["cityline_account"]
        if len(cityline_account) > 4:
            # Auto-fill email and monitor login button (will auto-click when enabled)
            await nodriver_cityline_login(tab, cityline_account, config_dict)

    # Multi-tab handling (FR-009)
    tab = await nodriver_cityline_close_second_tab(tab, url)

    # Event detail page on shows.cityline.com
    # https://shows.cityline.com/tc/2026/jordanchan.html
    if 'shows.cityline.com' in url:
        if not _state["buy_button_pressed"]:
            # Wait for and click buy ticket button
            button_clicked = await nodriver_cityline_press_buy_button(tab, config_dict)
            if button_clicked:
                _state["buy_button_pressed"] = True
                # Wait for navigation to eventDetail page
                await asyncio.sleep(random.uniform(1.0, 2.0))
                # Update URL after button click
                try:
                    url = await tab.evaluate('window.location.href')
                except:
                    pass
    else:
        # Reset flag when leaving shows.cityline.com domain
        _state["buy_button_pressed"] = False

    # date page.
    #https://venue.cityline.com/utsvInternet/EVENT_NAME/eventDetail?event=EVENT_CODE
    if 'venue.cityline.com' in url and '/eventDetail?' in url:
        # Always check for login modal (independent of flag, for cookie capture)
        await nodriver_cityline_check_login_modal(tab, config_dict)

        # Then proceed with purchase button if not already processed
        if not _state["purchase_button_pressed"]:
            if config_dict["date_auto_select"]["enable"]:
                is_button_clicked = await nodriver_cityline_purchase_button_press(tab, config_dict)
                if is_button_clicked:
                    _state["purchase_button_pressed"] = True
    elif 'venue.cityline.com' not in url:
        # Only reset when completely leaving venue.cityline.com domain
        _state["purchase_button_pressed"] = False

    # area page:
    # https://venue.cityline.com/utsvInternet/EVENT_NAME/performance?event=EVENT_CODE&perfId=PROFORMANCE_ID
    if 'venue.cityline.com' in url and '/performance?' in url:
        # Reset modal flag when successfully navigated to performance page
        _state["modal_handled"] = False
        # Play sound when entering performance page
        if not _state["played_sound_ticket"]:
            if config_dict["advanced"]["play_sound"]["ticket"]:
                play_sound_while_ordering(config_dict)
        _state["played_sound_ticket"] = True

        # Integrated performance page processing (area + ticket number + next button)
        if not _state["performance_processed"]:
            if config_dict["area_auto_select"]["enable"]:
                is_area_processed = await nodriver_cityline_performance(tab, config_dict)
                if is_area_processed:
                    _state["performance_processed"] = True
    elif 'venue.cityline.com' not in url:
        # Reset flag when leaving venue.cityline.com domain
        _state["performance_processed"] = False
        _state["played_sound_ticket"] = False
    else:
        _state["played_sound_ticket"] = False

    # Shopping basket page (success detection)
    # https://venue.cityline.com/utsvInternet/internet/shoppingBasket
    if 'venue.cityline.com' in url and '/shoppingBasket' in url:
        await nodriver_cityline_check_shopping_basket(tab, config_dict)
    else:
        # Reset order sound flag when not on shopping basket page (allow replay for next purchase)
        _state["played_sound_order"] = False

    return tab
