#!/usr/bin/env python3
#encoding=utf-8
"""platforms/funone.py -- FunOne Tickets platform (tickets.funone.io)."""

import asyncio
import base64
import re

try:
    import ddddocr
except Exception:
    pass

import util
from nodriver_common import (
    check_and_handle_pause,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
)


__all__ = [
    "nodriver_funone_inject_cookie",
    "nodriver_funone_check_login_status",
    "nodriver_funone_verify_login",
    "nodriver_funone_close_popup",
    "nodriver_funone_date_auto_select",
    "nodriver_funone_area_auto_select",
    "nodriver_funone_check_sold_out",
    "nodriver_funone_click_refresh_button",
    "nodriver_funone_assign_ticket_number",
    "nodriver_funone_captcha_handler",
    "nodriver_funone_reload_captcha",
    "nodriver_funone_ocr_captcha",
    "nodriver_funone_detect_step",
    "nodriver_funone_ticket_agree",
    "nodriver_funone_order_submit",
    "nodriver_funone_auto_reload",
    "nodriver_funone_error_handler",
    "nodriver_funone_main",
]

_state = {}


async def nodriver_funone_inject_cookie(tab, config_dict):
    """
    Inject FunOne session cookie using CDP network.set_cookie

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary

    Returns:
        bool: True if injection successful
    """
    from zendriver import cdp

    debug = util.create_debug_logger(config_dict)
    funone_session_cookie = config_dict["accounts"].get("funone_session_cookie", "").strip()

    if len(funone_session_cookie) == 0:
        debug.log("[FUNONE] No session cookie configured")
        return False

    try:
        # Inject ticket_session cookie
        await tab.send(cdp.network.set_cookie(
            name="ticket_session",
            value=funone_session_cookie,
            domain="tickets.funone.io",
            path="/",
            secure=False,
            http_only=True
        ))

        debug.log("[FUNONE] Session cookie injected successfully")
        return True

    except Exception as exc:
        debug.log(f"[FUNONE] Cookie injection failed: {exc}")
        return False

async def nodriver_funone_check_login_status(tab):
    """
    Check if user is logged in by verifying ticket_session cookie exists

    Returns:
        bool: True if logged in (cookie exists and valid)
    """
    try:
        # Cookie verification - check if ticket_session cookie exists
        cookies = await tab.browser.cookies.get_all()
        session_cookie = next((c for c in cookies if c.name == 'ticket_session'), None)
        if session_cookie and len(session_cookie.value) > 10:
            return True
        return False

    except Exception as exc:
        return False

async def nodriver_funone_verify_login(tab, config_dict):
    """
    Verify login status (cookie is already injected in goto_homepage)

    Returns:
        bool: True if logged in
    """
    debug = util.create_debug_logger(config_dict)

    is_logged_in = await nodriver_funone_check_login_status(tab)

    # Only print when login status changes (reduce repetitive messages)
    if is_logged_in:
        if _state.get("last_login_status") != True:
            debug.log("[FUNONE] Login status verified - logged in")
            _state["last_login_status"] = True
        return True

    if _state.get("last_login_status") != False:
        debug.log("[FUNONE] Not logged in - waiting for manual OTP login")
        _state["last_login_status"] = False
    return False

async def nodriver_funone_close_popup(tab):
    """
    Close cookie consent, login modal, and announcement popups

    Returns:
        bool: True if any popup was closed
    """
    closed_any = False

    try:
        # Close common popups
        close_popup_js = '''
        (function() {
            let closed = 0;

            // Priority 0: Age confirmation modal (must click confirm, NOT close/return)
            const ageModal = document.querySelector('.activity_aged_18_limit_modal');
            if (ageModal) {
                const confirmBtn = ageModal.querySelector('.btn-primary');
                if (confirmBtn) {
                    confirmBtn.click();
                    return 1;
                }
            }

            // Priority 1: FunOne login modal (close button)
            const loginModalClose = document.querySelector('button.modal_close');
            if (loginModalClose) {
                const style = window.getComputedStyle(loginModalClose);
                if (style.display !== 'none' && style.visibility !== 'hidden') {
                    loginModalClose.click();
                    closed++;
                    return closed;
                }
            }

            // Priority 2: FunOne login modal (return button as fallback)
            const modalAction = document.querySelector('.modal_action');
            if (modalAction) {
                const buttons = modalAction.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = (btn.textContent || '').trim();
                    if (text.includes('返回') || text.toLowerCase().includes('back') || text.toLowerCase().includes('cancel')) {
                        btn.click();
                        closed++;
                        return closed;
                    }
                }
            }

            // Priority 3: Generic modal close buttons
            const closeIcons = document.querySelectorAll('[class*="close"], [aria-label="close"]');
            for (const icon of closeIcons) {
                const style = window.getComputedStyle(icon);
                if (style.display !== 'none' && style.visibility !== 'hidden') {
                    icon.click();
                    closed++;
                    return closed;
                }
            }

            // Priority 4: Cookie consent banner (FunOne specific)
            // Look for "同意" button in cookie context
            const allButtons = document.querySelectorAll('button');
            for (const btn of allButtons) {
                const text = (btn.textContent || '').trim();
                const style = window.getComputedStyle(btn);
                if ((text === '同意' || text.toLowerCase() === 'agree' || text.toLowerCase() === 'accept') &&
                    style.display !== 'none' && style.visibility !== 'hidden') {
                    // Verify it's in a cookie/consent context
                    const parent = btn.closest('div');
                    if (parent && (parent.textContent.includes('Cookie') || parent.textContent.includes('cookie'))) {
                        btn.click();
                        closed++;
                        return closed;
                    }
                }
            }

            // Priority 5: Generic cookie consent (fallback)
            const cookieButtons = document.querySelectorAll('button, a');
            for (const btn of cookieButtons) {
                const text = (btn.textContent || '').toLowerCase();
                if (text.includes('accept') || text.includes('got it') || text.includes('ok')) {
                    if (btn.closest('.cookie') || btn.closest('[class*="consent"]') || btn.closest('[class*="popup"]')) {
                        btn.click();
                        closed++;
                    }
                }
            }

            return closed;
        })()
        '''
        result = await tab.evaluate(close_popup_js)
        closed_any = result > 0

    except Exception as exc:
        pass

    return closed_any

async def nodriver_funone_date_auto_select(tab, url, config_dict):
    """
    Auto-select session/date on activity detail page

    Returns:
        bool: True if session selected and next button clicked
    """
    debug = util.create_debug_logger(config_dict)

    # Wait for page to fully load before selecting session
    # Check for key elements: next button or activity info
    wait_js = '''
    (function() {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            const text = btn.textContent || '';
            if (text.includes('下一步') || text.includes('Next')) {
                return true;
            }
        }
        // Also check for activity title
        const body = document.body.textContent || '';
        if (body.includes('活動場次') || body.includes('活動時間')) {
            return true;
        }
        return false;
    })()
    '''
    page_ready = await tab.evaluate(wait_js)
    page_ready = util.parse_nodriver_result(page_ready)
    if not page_ready:
        # Page not ready, return False to retry next iteration
        return False

    # Get date keyword from config
    date_keyword = config_dict.get("date_auto_select", {}).get("date_keyword", "")
    auto_select_mode = config_dict.get("date_auto_select", {}).get("mode", "random")
    date_auto_fallback = config_dict.get("date_auto_fallback", False)

    debug.log(f"[FUNONE] Date selection - keyword: '{date_keyword}', mode: {auto_select_mode}")

    try:
        # Get all session options
        get_sessions_js = '''
        (function() {
            const sessions = [];

            // Priority 1: Look for FunOne-specific round_info divs (session containers)
            const roundInfos = document.querySelectorAll('.round_info, .round_info--js');
            if (roundInfos.length > 0) {
                for (const container of roundInfos) {
                    // Get session info from .info div inside container
                    const infoDiv = container.querySelector('.info');
                    const text = infoDiv ? infoDiv.textContent.trim() : container.textContent.trim();
                    const isDisabled = container.classList.contains('disabled') || container.classList.contains('sold-out');

                    if (!isDisabled && text.length > 3) {
                        sessions.push({
                            text: text,
                            index: sessions.length
                        });
                    }
                }
                return sessions;
            }

            // Priority 2: Fallback to generic button search (for other layouts)
            const buttons = document.querySelectorAll('button, [role="button"], .session-item, [class*="session"], [class*="date"]');
            for (const btn of buttons) {
                const text = btn.textContent || '';
                const isDisabled = btn.disabled || btn.classList.contains('disabled') || btn.classList.contains('sold-out');

                // Filter out non-session buttons
                if (text.length > 3 && text.length < 200 && !isDisabled) {
                    // Check if it looks like a date/session
                    if (/\\d{4}|\\d{1,2}[/.-]\\d{1,2}|\\d{1,2}:\\d{2}/.test(text) ||
                        text.includes('場') || text.includes('場次')) {
                        sessions.push({
                            text: text.trim(),
                            index: sessions.length
                        });
                    }
                }
            }
            return sessions;
        })()
        '''
        sessions = await tab.evaluate(get_sessions_js)

        # Parse CDP format if needed
        # NoDriver may return format: {'type': 'object', 'value': [['key', {'type': 'string', 'value': 'val'}], ...]}
        if sessions:
            parsed_sessions = []
            for s in sessions:
                if isinstance(s, dict) and 'type' in s and s['type'] == 'object' and 'value' in s:
                    # Parse CDP object format
                    obj = {}
                    for pair in s['value']:
                        if isinstance(pair, list) and len(pair) == 2:
                            key, val_dict = pair
                            if isinstance(val_dict, dict) and 'value' in val_dict:
                                obj[key] = val_dict['value']
                    parsed_sessions.append(obj)
                else:
                    parsed_sessions.append(s)
            sessions = parsed_sessions

        if not sessions or len(sessions) == 0:
            debug.log("[FUNONE] No sessions found")
            return False

        debug.log(f"[FUNONE] Found {len(sessions)} sessions")

        # Find matching session by keyword
        target_index = -1

        if date_keyword and len(date_keyword) > 0:
            keywords = util.parse_keyword_string_to_array(date_keyword)

            for i, session in enumerate(sessions):
                session_text = session.get('text', '') if isinstance(session, dict) else str(session)
                for kw in keywords:
                    if kw.lower() in session_text.lower():
                        target_index = i
                        debug.log(f"[FUNONE] Keyword '{kw}' matched session: {session_text}")
                        break
                if target_index >= 0:
                    break

        # Fallback selection if no keyword match
        if target_index < 0:
            if date_keyword and len(date_keyword) > 0 and not date_auto_fallback:
                debug.log("[FUNONE] No keyword match, date_auto_fallback=False, stopping")
                return False

            # Use auto_select_mode for fallback
            target_index = util.get_target_index_by_mode(len(sessions), auto_select_mode)
            debug.log(f"[FUNONE] Using fallback mode '{auto_select_mode}', selected index: {target_index}")

        if target_index < 0 or target_index >= len(sessions):
            target_index = 0

        # Click the selected session's next button
        click_session_js = f'''
        (function() {{
            // Priority 1: FunOne-specific round_info divs
            const roundInfos = document.querySelectorAll('.round_info, .round_info--js');
            if (roundInfos.length > 0) {{
                const sessionContainers = [];
                for (const container of roundInfos) {{
                    const isDisabled = container.classList.contains('disabled') || container.classList.contains('sold-out');
                    if (!isDisabled) {{
                        sessionContainers.push(container);
                    }}
                }}

                if (sessionContainers.length > {target_index}) {{
                    // Find the "下一步" button inside the selected session container
                    const selectedContainer = sessionContainers[{target_index}];
                    const nextBtn = selectedContainer.querySelector('button');
                    if (nextBtn) {{
                        nextBtn.click();
                        return true;
                    }}
                }}
                return false;
            }}

            // Priority 2: Fallback to generic button search
            const sessions = [];
            const buttons = document.querySelectorAll('button, [role="button"], .session-item, [class*="session"], [class*="date"]');

            for (const btn of buttons) {{
                const text = btn.textContent || '';
                const isDisabled = btn.disabled || btn.classList.contains('disabled') || btn.classList.contains('sold-out');

                if (text.length > 3 && text.length < 200 && !isDisabled) {{
                    if (/\\d{{4}}|\\d{{1,2}}[/.-]\\d{{1,2}}|\\d{{1,2}}:\\d{{2}}/.test(text) ||
                        text.includes('場') || text.includes('場次')) {{
                        sessions.push(btn);
                    }}
                }}
            }}

            if (sessions.length > {target_index}) {{
                sessions[{target_index}].click();
                return true;
            }}
            return false;
        }})()
        '''
        clicked = await tab.evaluate(click_session_js)

        if clicked:
            debug.log(f"[FUNONE] Session {target_index} next button clicked")
            await tab.sleep(0.5)
            return True

        return False

    except Exception as exc:
        debug.log(f"[FUNONE] Date selection error: {exc}")
        return False

async def nodriver_funone_area_auto_select(tab, url, config_dict):
    """
    Auto-select ticket type on ticket selection page

    Returns:
        bool: True if ticket type selected
    """
    debug = util.create_debug_logger(config_dict)

    # Get area keyword from config
    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "")
    auto_select_mode = config_dict.get("area_auto_select", {}).get("mode", "random")
    keyword_exclude = config_dict.get("keyword_exclude", "")
    area_auto_fallback = config_dict.get("area_auto_fallback", False)

    # Only print area selection config once
    area_config_key = f"{area_keyword}_{auto_select_mode}"
    if _state.get("last_area_config") != area_config_key:
        debug.log(f"[FUNONE] Area selection - keyword: '{area_keyword}', mode: {auto_select_mode}")
        _state["last_area_config"] = area_config_key

    try:
        # Get all ticket areas (FunOne uses div.zone_box elements)
        # IMPORTANT: Only look for .zone_box elements, do NOT fallback to generic buttons
        # Generic button search would incorrectly match ticket type names on quantity selection pages
        get_tickets_js = '''
        (function() {
            const tickets = [];

            // Only FunOne-specific zone_box elements (area selection page)
            const zoneBoxes = document.querySelectorAll('.zone_box');
            if (zoneBoxes.length > 0) {
                for (const box of zoneBoxes) {
                    // Use innerText for more reliable text extraction (rendered text)
                    const fullText = (box.innerText || box.textContent || '').trim().replace(/\\s+/g, ' ');
                    const isDisabled = box.classList.contains('disabled');

                    // Get zone name - try multiple methods
                    let name = '';
                    const zoneName = box.querySelector('.zone_name');
                    if (zoneName) {
                        name = (zoneName.innerText || zoneName.textContent || '').trim();
                    }
                    // Fallback: use first line of fullText
                    if (!name && fullText) {
                        name = fullText.split(/[\\n\\r]|\\u70ed|\\u5df2/)[0].trim();
                    }

                    tickets.push({
                        text: name,
                        fullText: fullText,
                        index: tickets.length,
                        disabled: isDisabled,
                        type: 'zone_box'
                    });
                }
            }

            // No fallback - if no zone_box found, return empty array
            // This page is likely a ticket quantity selection page, not area selection
            return tickets;
        })()
        '''
        tickets = await tab.evaluate(get_tickets_js)

        # Convert CDP format to Python dict if needed
        # NoDriver may return CDP format: {'type': 'object', 'value': [['key', {'type': 'string', 'value': 'val'}], ...]}
        def parse_cdp_value(item):
            if isinstance(item, dict) and 'type' in item and 'value' in item:
                if item['type'] == 'object' and isinstance(item['value'], list):
                    # Convert [['key', {'type': 'string', 'value': 'val'}], ...] to {'key': 'val', ...}
                    result = {}
                    for pair in item['value']:
                        if isinstance(pair, list) and len(pair) == 2:
                            key, val_obj = pair
                            if isinstance(val_obj, dict) and 'value' in val_obj:
                                result[key] = val_obj['value']
                            else:
                                result[key] = val_obj
                    return result
                else:
                    return item['value']
            return item

        if tickets:
            tickets = [parse_cdp_value(t) for t in tickets]

        if not tickets or len(tickets) == 0:
            # Only print "No ticket types found" if we previously found some
            if _state.get("last_area_count", -1) != 0:
                debug.log("[FUNONE] No ticket types found")
                _state["last_area_count"] = 0
            return False

        # Only print ticket count when it changes
        if _state.get("last_area_count") != len(tickets):
            debug.log(f"[FUNONE] Found {len(tickets)} ticket types")
            _state["last_area_count"] = len(tickets)

        # Filter out disabled (sold out) tickets first
        available_tickets = [t for t in tickets if not t.get('disabled', False)]
        if len(available_tickets) != len(tickets):
            sold_out_count = len(tickets) - len(available_tickets)
            debug.log(f"[FUNONE] {sold_out_count} ticket types sold out, {len(available_tickets)} available")

        if len(available_tickets) == 0:
            debug.log("[FUNONE] All ticket types are sold out")
            return False

        tickets = available_tickets

        # Apply exclude keywords first (using standard util function)
        if keyword_exclude and len(keyword_exclude) > 0:
            filtered_tickets = []
            for ticket in tickets:
                # Use text first, fallback to fullText for keyword matching
                ticket_text = ticket.get('text', '') or ticket.get('fullText', '')
                if ticket_text and util.reset_row_text_if_match_keyword_exclude(config_dict, ticket_text):
                    debug.log(f"[FUNONE] Excluding ticket '{ticket_text[:50]}'")
                else:
                    filtered_tickets.append(ticket)
            tickets = filtered_tickets

        if len(tickets) == 0:
            debug.log("[FUNONE] All tickets filtered out by exclude keywords")
            return False

        # Find matching ticket by keyword
        target_index = -1

        if area_keyword and len(area_keyword) > 0:
            keywords = util.parse_keyword_string_to_array(area_keyword)

            for i, ticket in enumerate(tickets):
                # Use text first, fallback to fullText for keyword matching
                ticket_text = ticket.get('text', '') or ticket.get('fullText', '')
                if not ticket_text:
                    continue
                for kw in keywords:
                    if kw.lower() in ticket_text.lower():
                        target_index = i
                        debug.log(f"[FUNONE] Keyword '{kw}' matched ticket: {ticket_text[:50]}")
                        break
                if target_index >= 0:
                    break

        # Fallback selection if no keyword match
        if target_index < 0:
            if area_keyword and len(area_keyword) > 0 and not area_auto_fallback:
                debug.log("[FUNONE] No keyword match, area_auto_fallback=False, stopping")
                return False

            target_index = util.get_target_index_by_mode(len(tickets), auto_select_mode)
            debug.log(f"[FUNONE] Using fallback mode '{auto_select_mode}', selected index: {target_index}")

        if target_index < 0 or target_index >= len(tickets):
            target_index = 0

        # Click the selected ticket type
        original_index = tickets[target_index].get('index', target_index)
        ticket_type = tickets[target_index].get('type', 'button')
        ticket_name = tickets[target_index].get('text', '') or tickets[target_index].get('fullText', '')

        debug.log(f"[FUNONE] Clicking area '{ticket_name}' (index: {original_index}, type: {ticket_type})")

        click_ticket_js = f'''
        (function() {{
            // First try FunOne-specific zone_box elements
            const zoneBoxes = document.querySelectorAll('.zone_box');
            if (zoneBoxes.length > 0) {{
                const availableBoxes = [];
                for (const box of zoneBoxes) {{
                    if (!box.classList.contains('disabled')) {{
                        availableBoxes.push(box);
                    }}
                }}
                if (availableBoxes.length > {original_index}) {{
                    availableBoxes[{original_index}].click();
                    return true;
                }}
            }}

            // Fallback to generic button search
            const items = document.querySelectorAll('button, [role="button"], .ticket-type, [class*="ticket"], [class*="area"]');
            const tickets = [];

            for (const item of items) {{
                const text = item.textContent || '';
                const isDisabled = item.disabled || item.classList.contains('disabled') || item.classList.contains('sold-out');

                if (text.length > 2 && text.length < 300 && !isDisabled) {{
                    if (/\\$|NT|TWD|\\d+元|區|票/.test(text) || text.includes('票種')) {{
                        tickets.push(item);
                    }}
                }}
            }}

            if (tickets.length > {original_index}) {{
                tickets[{original_index}].click();
                return true;
            }}
            return false;
        }})()
        '''
        clicked = await tab.evaluate(click_ticket_js)

        if clicked:
            debug.log(f"[FUNONE] Ticket type {target_index} clicked")

        return clicked

    except Exception as exc:
        debug.log(f"[FUNONE] Area selection error: {exc}")
        return False

async def nodriver_funone_check_sold_out(tab, config_dict):
    """
    Check if all tickets are sold out on purchase_choose_ticket_no_map page

    Returns:
        tuple: (is_sold_out: bool, remaining_count: int, ticket_info: list)
    """
    debug = util.create_debug_logger(config_dict)
    ticket_number = config_dict.get("ticket_number", 2)
    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "")

    # Parse keywords
    keywords = []
    if area_keyword:
        clean_keyword = area_keyword.replace('"', '').replace("'", '')
        keywords = [k.strip() for k in clean_keyword.split(',') if k.strip()]

    try:
        check_sold_out_js = f'''
        (function() {{
            const keywords = {keywords};
            const ticketInfo = [];
            let totalRemaining = 0;
            let matchedRemaining = 0;
            let hasMatchedTicket = false;
            let allSoldOut = true;
            let hasPurchaseButton = false;
            let purchaseButtonDisabled = true;

            // Use TreeWalker to find text nodes containing remaining count
            // This avoids duplicate counting from nested elements
            const pattern = /(?:剩餘|remaining)\\s*(\\d+)/i;
            const processedRows = new Set();

            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let node;
            while (node = walker.nextNode()) {{
                const text = node.textContent || '';
                const remainingMatch = text.match(pattern);

                if (remainingMatch) {{
                    const remaining = parseInt(remainingMatch[1]);

                    // Find the ticket row container to get context
                    let container = node.parentElement;
                    if (container) {{
                        container = container.closest('div[class*="ticket"], div[class*="row"], tr, li') || container.parentElement;
                    }}

                    // Use container reference to avoid duplicate processing
                    if (container && processedRows.has(container)) {{
                        continue;
                    }}
                    if (container) {{
                        processedRows.add(container);
                    }}

                    const rowText = container ? container.textContent : text;

                    // Check if this matches any keyword
                    let matched = keywords.length === 0;
                    for (const kw of keywords) {{
                        if (kw && rowText.toLowerCase().includes(kw.toLowerCase())) {{
                            matched = true;
                            break;
                        }}
                    }}

                    ticketInfo.push({{
                        remaining: remaining,
                        text: rowText.substring(0, 100),
                        matched: matched
                    }});

                    totalRemaining += remaining;
                    if (matched) {{
                        matchedRemaining += remaining;
                        hasMatchedTicket = true;
                    }}
                    if (remaining > 0) {{
                        allSoldOut = false;
                    }}
                }}
            }}

            // Check +/- buttons status
            // FUNONE uses SVG icons for +/- buttons, need to check btn-tertiary class
            const buttons = document.querySelectorAll('button');
            let allButtonsDisabled = true;

            for (const btn of buttons) {{
                const btnText = btn.textContent.trim();
                const classList = Array.from(btn.classList);

                // Check for +/- buttons (btn-tertiary, but not refresh button)
                if (classList.includes('btn-tertiary') && !classList.includes('round_info_refresh')) {{
                    // Check if this is a plus button by examining SVG path
                    const svg = btn.querySelector('svg');
                    if (svg) {{
                        const path = svg.querySelector('path');
                        if (path) {{
                            const d = path.getAttribute('d') || '';
                            // Plus button path starts with 'M11 13H' (has vertical line)
                            // Minus button path starts with 'M6 13C' (only horizontal line)
                            if (d.startsWith('M11')) {{
                                // This is a plus button
                                if (!btn.disabled) {{
                                    allButtonsDisabled = false;
                                }}
                            }}
                        }}
                    }}
                }}

                // Check for purchase/submit button (Chinese and English)
                if (btnText.includes('立即購買') || btnText.includes('Purchase') ||
                    btnText.includes('Confirm') || btnText.includes('submit')) {{
                    hasPurchaseButton = true;
                    purchaseButtonDisabled = btn.disabled;
                }}
            }}

            // If no remaining info found, try alternative detection via buttons
            if (ticketInfo.length === 0) {{
                const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
                for (const input of inputs) {{
                    const parent = input.parentElement;
                    if (parent) {{
                        const plusBtn = parent.querySelector('button:not(:disabled)');
                        if (plusBtn) {{
                            allSoldOut = false;
                        }}
                    }}
                }}
            }}

            // Determine if sold out
            const isSoldOut = (ticketInfo.length > 0 && allSoldOut) ||
                              (allButtonsDisabled && hasPurchaseButton && purchaseButtonDisabled);

            return {{
                isSoldOut: isSoldOut,
                totalRemaining: totalRemaining,
                matchedRemaining: hasMatchedTicket ? matchedRemaining : totalRemaining,
                hasMatchedTicket: hasMatchedTicket,
                ticketInfo: ticketInfo,
                allButtonsDisabled: allButtonsDisabled,
                purchaseButtonDisabled: purchaseButtonDisabled
            }};
        }})()
        '''
        result = await tab.evaluate(check_sold_out_js)
        result = util.parse_nodriver_result(result)

        if result and isinstance(result, dict):
            is_sold_out = result.get('isSoldOut', False)
            remaining = result.get('matchedRemaining', 0) if result.get('hasMatchedTicket') else result.get('totalRemaining', 0)
            ticket_info = result.get('ticketInfo', [])

            if debug.enabled:
                if is_sold_out:
                    debug.log("[FUNONE] All tickets sold out")

            return (is_sold_out, remaining, ticket_info)

        return (False, 0, [])

    except Exception as exc:
        debug.log(f"[FUNONE] Check sold out error: {exc}")
        return (False, 0, [])

async def nodriver_funone_click_refresh_button(tab, config_dict):
    """
    Click the "instant ticket status update" button to refresh ticket status via WebSocket

    Returns:
        bool: True if button clicked successfully
    """
    debug = util.create_debug_logger(config_dict)

    try:
        click_refresh_js = '''
        (function() {
            // Find the refresh button - look for text containing "instant update" or similar
            const buttons = document.querySelectorAll('button, div[role="button"], a[role="button"]');

            for (const btn of buttons) {
                const text = btn.textContent || '';
                // Match various refresh button patterns
                if (text.includes('instant') || text.includes('Instant') ||
                    text.includes('update') || text.includes('Update') ||
                    text.includes('refresh') || text.includes('Refresh') ||
                    text.includes('reload') || text.includes('Reload')) {
                    if (!btn.disabled) {
                        btn.click();
                        return { success: true, buttonText: text.substring(0, 50) };
                    }
                }
            }

            // Fallback: look for button with refresh icon (SVG with certain classes)
            const iconButtons = document.querySelectorAll('button svg, button i[class*="refresh"], button i[class*="sync"]');
            for (const icon of iconButtons) {
                const btn = icon.closest('button');
                if (btn && !btn.disabled) {
                    btn.click();
                    return { success: true, buttonText: 'icon_button' };
                }
            }

            return { success: false, reason: 'no_refresh_button_found' };
        })()
        '''
        result = await tab.evaluate(click_refresh_js)
        result = util.parse_nodriver_result(result)

        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[FUNONE] Clicked refresh button: {result.get('buttonText', 'unknown')}")
            return True
        else:
            debug.log("[FUNONE] Refresh button not found")
            return False

    except Exception as exc:
        debug.log(f"[FUNONE] Click refresh button error: {exc}")
        return False

async def nodriver_funone_assign_ticket_number(tab, config_dict):
    """
    Set ticket quantity for the ticket type matching keyword

    Returns:
        bool: True if quantity set successfully
    """
    debug = util.create_debug_logger(config_dict)
    ticket_number = config_dict.get("ticket_number", 2)
    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "")
    keyword_exclude = config_dict.get("keyword_exclude", "")
    area_auto_fallback = config_dict.get("area_auto_fallback", False)

    # Parse keywords
    keywords = []
    if area_keyword:
        # Remove quotes and split by comma
        clean_keyword = area_keyword.replace('"', '').replace("'", '')
        keywords = [k.strip() for k in clean_keyword.split(',') if k.strip()]

    exclude_keywords = []
    if keyword_exclude:
        clean_exclude = keyword_exclude.replace('"', '').replace("'", '')
        exclude_keywords = [k.strip() for k in clean_exclude.split(',') if k.strip()]

    # Only print setting message once
    if _state.get("last_ticket_qty") != ticket_number:
        debug.log(f"[FUNONE] Setting ticket quantity to {ticket_number}")
        _state["last_ticket_qty"] = ticket_number

    try:
        # FunOne-specific: Find ticket row by keyword and click its + button
        set_quantity_js = f'''
        (function() {{
            const targetQty = {ticket_number};
            const keywords = {keywords};
            const excludeKeywords = {exclude_keywords};
            const areaAutoFallback = {'true' if area_auto_fallback else 'false'};

            // FunOne ticket selection page structure:
            // Each ticket row has: [ticket name] [price] [- button] [textbox] [+ button]
            // We need to find the row matching keyword and click its + button

            // Get all input elements (quantity boxes)
            const inputs = document.querySelectorAll('input');
            let targetInput = null;
            let targetPlusBtn = null;
            let matchedName = '';

            for (const input of inputs) {{
                // Check if this looks like a quantity input
                const val = parseInt(input.value);
                if (isNaN(val) || val < 0 || val > 100) continue;

                // Find the ticket row container (traverse up to find text context)
                let container = input.parentElement;
                let depth = 0;
                let rowText = '';

                // Go up a few levels to find the row containing ticket name
                while (container && depth < 5) {{
                    rowText = container.textContent || '';
                    // Check if this container has ticket info (price pattern)
                    if (/TWD|NT\$|\d+元/.test(rowText)) {{
                        break;
                    }}
                    container = container.parentElement;
                    depth++;
                }}

                if (!rowText) continue;

                // Check exclude keywords first
                let excluded = false;
                for (const exc of excludeKeywords) {{
                    if (exc && rowText.toLowerCase().includes(exc.toLowerCase())) {{
                        excluded = true;
                        break;
                    }}
                }}
                if (excluded) continue;

                // Check if this row matches any keyword
                let matched = keywords.length === 0; // If no keyword, match first valid row
                for (const kw of keywords) {{
                    if (kw && rowText.toLowerCase().includes(kw.toLowerCase())) {{
                        matched = true;
                        matchedName = kw;
                        break;
                    }}
                }}

                if (matched) {{
                    targetInput = input;
                    // Find the + button near this input
                    const parent = input.parentElement;
                    if (parent) {{
                        const children = Array.from(parent.children);
                        const inputIndex = children.indexOf(input);

                        // Find button after the input (+ button)
                        for (let i = inputIndex + 1; i < children.length; i++) {{
                            if (children[i].tagName === 'BUTTON' && !children[i].disabled) {{
                                targetPlusBtn = children[i];
                                break;
                            }}
                        }}

                        // If not found, try sibling buttons
                        if (!targetPlusBtn) {{
                            const buttons = parent.querySelectorAll('button:not([disabled])');
                            for (const btn of buttons) {{
                                // The + button is typically after the input or has no text (icon-based)
                                const btnText = btn.textContent.trim();
                                if (btnText === '+' || btnText === '') {{
                                    // Check position relative to input
                                    const btnIndex = children.indexOf(btn);
                                    if (btnIndex > inputIndex) {{
                                        targetPlusBtn = btn;
                                        break;
                                    }}
                                }}
                            }}
                        }}
                    }}

                    if (targetPlusBtn) break;
                }}
            }}

            // Click the + button to set quantity
            if (targetPlusBtn && targetInput) {{
                const currentVal = parseInt(targetInput.value) || 0;
                const clicksNeeded = targetQty - currentVal;

                if (clicksNeeded > 0) {{
                    for (let i = 0; i < clicksNeeded; i++) {{
                        targetPlusBtn.click();
                    }}
                    return {{ success: true, type: 'keyword_match', value: targetQty, clicks: clicksNeeded, keyword: matchedName }};
                }} else if (clicksNeeded === 0) {{
                    return {{ success: true, type: 'already_set', value: targetQty, keyword: matchedName }};
                }}
            }}

            // Keyword matched a ticket but its + button is disabled (sold out)
            if (targetInput && !targetPlusBtn) {{
                if (!areaAutoFallback) {{
                    return {{ success: false, reason: 'sold_out', keyword: matchedName }};
                }}
                // areaAutoFallback=true: fall through to fallback selection below
            }}

            // No keyword match or areaAutoFallback override: decide whether to fallback
            if (keywords.length > 0 && !areaAutoFallback) {{
                return {{ success: false, reason: 'no_match' }};
            }}

            // Fallback: select first available ticket not in excludeKeywords
            for (const input of inputs) {{
                const val = parseInt(input.value);
                if (isNaN(val) || val < 0 || val > 100) continue;

                // Find row text to check excludes
                let container = input.parentElement;
                let depth = 0;
                let rowText = '';
                while (container && depth < 5) {{
                    rowText = container.textContent || '';
                    if (/TWD|NT\$|\d+\u5143/.test(rowText)) break;
                    container = container.parentElement;
                    depth++;
                }}
                let excluded = false;
                for (const exc of excludeKeywords) {{
                    if (exc && rowText.toLowerCase().includes(exc.toLowerCase())) {{
                        excluded = true; break;
                    }}
                }}
                if (excluded) continue;

                const parent = input.parentElement;
                if (!parent) continue;

                const children = Array.from(parent.children);
                const inputIndex = children.indexOf(input);

                for (let i = inputIndex + 1; i < children.length; i++) {{
                    if (children[i].tagName === 'BUTTON' && !children[i].disabled) {{
                        const currentVal = parseInt(input.value) || 0;
                        const clicksNeeded = targetQty - currentVal;
                        if (clicksNeeded > 0) {{
                            for (let j = 0; j < clicksNeeded; j++) {{
                                children[i].click();
                            }}
                            return {{ success: true, type: 'fallback', value: targetQty, clicks: clicksNeeded }};
                        }}
                        break;
                    }}
                }}
            }}

            return {{ success: false, reason: 'no_quantity_control_found' }};
        }})()
        '''
        result = await tab.evaluate(set_quantity_js)
        result = util.parse_nodriver_result(result)

        if result and isinstance(result, dict) and result.get('success'):
            debug.log(f"[FUNONE] Ticket quantity set to {result.get('value')} via {result.get('type')}")
            _state["qty_selector_notfound"] = False
            _state["qty_fail_reason"] = ""
            return True
        else:
            reason = result.get('reason', 'unknown') if isinstance(result, dict) else 'unknown'
            _state["qty_fail_reason"] = reason
            # Only print once per failure state
            if not _state.get("qty_selector_notfound"):
                if reason == 'sold_out':
                    debug.log(f"[FUNONE] Keyword '{result.get('keyword', '')}' ticket is sold out, will refresh")
                elif reason == 'no_match':
                    debug.log(f"[FUNONE] No ticket matching keyword found")
                else:
                    debug.log("[FUNONE] Could not find quantity selector")
                _state["qty_selector_notfound"] = True
            return False

    except Exception as exc:
        debug.log(f"[FUNONE] Set quantity error: {exc}")
        return False

async def nodriver_funone_captcha_handler(tab, config_dict):
    """
    Handle captcha - detect and auto-fill using OCR

    Returns:
        bool: True if captcha is filled or no captcha exists
    """
    debug = util.create_debug_logger(config_dict)
    ocr_enabled = config_dict.get("ocr_captcha", {}).get("enable", False)

    try:
        # Check for captcha image and input
        # FunOne uses img[alt="vCode"] with base64 data URI
        check_captcha_js = '''
        (function() {
            // Look for FunOne captcha image (alt="vCode" with base64 src)
            const captchaImg = document.querySelector('img[alt="vCode"]');
            if (captchaImg) {
                const src = captchaImg.src || '';
                // FunOne captcha is embedded as base64
                if (src.startsWith('data:image')) {
                    // Find the corresponding input field
                    const inputs = document.querySelectorAll('input[type="text"]');
                    let captchaInput = null;
                    for (const input of inputs) {
                        const placeholder = (input.placeholder || '').toLowerCase();
                        if (placeholder.includes('驗證') || placeholder.includes('captcha')) {
                            captchaInput = input;
                            break;
                        }
                    }
                    return {
                        hasCaptcha: true,
                        type: 'base64',
                        base64Data: src,
                        filled: captchaInput ? captchaInput.value.length > 0 : false
                    };
                }
            }

            // Fallback: Look for any captcha-related image
            const imgs = document.querySelectorAll('img');
            for (const img of imgs) {
                const src = img.src || '';
                const alt = img.alt || '';
                if (src.includes('captcha') || alt.includes('captcha') || alt.includes('驗證')) {
                    return { hasCaptcha: true, type: 'image', filled: false };
                }
            }

            // Look for captcha input to check if filled
            const inputs = document.querySelectorAll('input');
            for (const input of inputs) {
                const name = (input.name || '').toLowerCase();
                const placeholder = (input.placeholder || '').toLowerCase();
                if (name.includes('captcha') || placeholder.includes('驗證') || placeholder.includes('captcha')) {
                    const value = input.value || '';
                    return { hasCaptcha: true, type: 'input', filled: value.length > 0 };
                }
            }

            return { hasCaptcha: false };
        })()
        '''
        captcha_info = await tab.evaluate(check_captcha_js)
        captcha_info = util.parse_nodriver_result(captcha_info)

        if not captcha_info or not isinstance(captcha_info, dict) or not captcha_info.get('hasCaptcha'):
            # No captcha found
            return True

        # Only print captcha type once
        captcha_type = captcha_info.get('type')
        if _state.get("last_captcha_type") != captcha_type:
            debug.log(f"[FUNONE] Captcha detected - type: {captcha_type}")
            _state["last_captcha_type"] = captcha_type

        # Check if already filled
        if captcha_info.get('filled'):
            # Only print once to reduce repetitive messages
            if not _state.get("captcha_filled_printed"):
                debug.log("[FUNONE] Captcha already filled")
                _state["captcha_filled_printed"] = True
            return True

        # Play sound once to alert user
        if not _state.get("played_sound_ticket", False):
            if config_dict["advanced"]["play_sound"]["ticket"]:
                play_sound_while_ordering(config_dict)
            _state["played_sound_ticket"] = True

        # Try OCR if enabled and we have base64 data
        if ocr_enabled and captcha_info.get('type') == 'base64' and captcha_info.get('base64Data'):
            # Skip if already exhausted retries for this page
            if _state.get("ocr_exhausted", False):
                if not _state.get("waiting_captcha_printed"):
                    debug.log("[FUNONE] OCR retries exhausted, waiting for manual captcha input...")
                    _state["waiting_captcha_printed"] = True
                return False

            max_retries = 5
            retry_count = _state.get("ocr_retry_count", 0)

            # First attempt with current image
            ocr_result = await nodriver_funone_ocr_captcha(tab, config_dict, captcha_info.get('base64Data'))
            if ocr_result:
                _state["ocr_retry_count"] = 0
                return True

            # OCR failed - retry with reload
            while retry_count < max_retries:
                retry_count += 1
                _state["ocr_retry_count"] = retry_count
                debug.log(f"[FUNONE OCR] Retry {retry_count}/{max_retries} - reloading captcha")

                # Click reload button to get new captcha image
                reload_ok = await nodriver_funone_reload_captcha(tab)
                if not reload_ok:
                    debug.log("[FUNONE OCR] Could not reload captcha")
                    break

                # Wait for new image to load
                await asyncio.sleep(0.5)

                # Get new captcha image
                new_captcha_js = '''
                (function() {
                    const img = document.querySelector('img[alt="vCode"]');
                    if (img && img.src && img.src.startsWith('data:image')) {
                        return { base64Data: img.src };
                    }
                    return null;
                })()
                '''
                new_info = await tab.evaluate(new_captcha_js)
                new_info = util.parse_nodriver_result(new_info)

                if not new_info or not isinstance(new_info, dict) or not new_info.get('base64Data'):
                    debug.log("[FUNONE OCR] Could not get new captcha image")
                    continue

                # Retry OCR with new image
                ocr_result = await nodriver_funone_ocr_captcha(tab, config_dict, new_info.get('base64Data'))
                if ocr_result:
                    _state["ocr_retry_count"] = 0
                    return True

            # All retries exhausted
            if retry_count >= max_retries:
                debug.log(f"[FUNONE OCR] Failed after {max_retries} retries, please enter manually")
                _state["ocr_exhausted"] = True

        # Only print waiting message once
        if not _state.get("waiting_captcha_printed"):
            debug.log("[FUNONE] Waiting for manual captcha input...")
            _state["waiting_captcha_printed"] = True
        return False

    except Exception as exc:
        debug.log(f"[FUNONE] Captcha check error: {exc}")
        return False

async def nodriver_funone_reload_captcha(tab):
    """Click the captcha reload button to get a new image"""
    try:
        reload_js = '''
        (function() {
            // FunOne reload button: button.captcha_reload_btn or button next to img[alt="vCode"]
            var btn = document.querySelector('button.captcha_reload_btn');
            if (!btn) {
                var img = document.querySelector('img[alt="vCode"]');
                if (img) {
                    var sibling = img.nextElementSibling;
                    if (sibling && sibling.tagName === 'BUTTON') btn = sibling;
                    if (!btn && img.parentElement) {
                        btn = img.parentElement.querySelector('button');
                    }
                }
            }
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        })()
        '''
        result = await tab.evaluate(reload_js)
        result = util.parse_nodriver_result(result)
        return bool(result)
    except Exception:
        return False


async def nodriver_funone_ocr_captcha(tab, config_dict, base64_data):
    """
    Perform OCR on FunOne captcha image and fill the input

    Args:
        tab: Browser tab
        config_dict: Configuration dictionary
        base64_data: Base64 encoded image data (data:image/png;base64,...)

    Returns:
        bool: True if OCR succeeded and input was filled
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # Extract base64 content (remove data:image/...;base64, prefix)
        if ',' in base64_data:
            base64_content = base64_data.split(',')[1]
        else:
            base64_content = base64_data

        # Decode base64 to image bytes (use module-level import)
        img_bytes = base64.b64decode(base64_content)

        debug.log(f"[FUNONE OCR] Image size: {len(img_bytes)} bytes")

        # Use cached OCR instance or create new one
        # IMPORTANT: beta=False required for set_ranges to work
        # set_ranges(5) = uppercase A-Z + 0-9 (FunOne captcha charset)
        if "ocr_instance" not in _state:
            ocr_obj = ddddocr.DdddOcr(show_ad=False, beta=False)
            ocr_obj.set_ranges(5)
            _state["ocr_instance"] = ocr_obj
        ocr_instance = _state["ocr_instance"]
        ocr_answer = ocr_instance.classification(img_bytes)

        if ocr_answer:
            # Filter to uppercase A-Z and digits 0-9 only
            # set_ranges(5) doesn't perfectly constrain, may include CJK or lowercase
            import re
            ocr_answer = re.sub(r'[^A-Za-z0-9]', '', ocr_answer).upper()

            debug.log(f"[FUNONE OCR] Result: {ocr_answer} (length: {len(ocr_answer)})")

            # FunOne captcha is typically 5 characters
            if len(ocr_answer) < 4 or len(ocr_answer) > 6:
                debug.log(f"[FUNONE OCR] Invalid length: {len(ocr_answer)}, expected 4-6 chars")
                return False

            # Fill the captcha input
            fill_captcha_js = f'''
            (function() {{
                const inputs = document.querySelectorAll('input[type="text"]');
                for (const input of inputs) {{
                    const placeholder = (input.placeholder || '').toLowerCase();
                    if (placeholder.includes('驗證') || placeholder.includes('captcha')) {{
                        input.value = '{ocr_answer}';
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{ success: true, value: '{ocr_answer}' }};
                    }}
                }}
                return {{ success: false }};
            }})()
            '''
            fill_result = await tab.evaluate(fill_captcha_js)
            fill_result = util.parse_nodriver_result(fill_result)

            if fill_result and isinstance(fill_result, dict) and fill_result.get('success'):
                debug.log(f"[FUNONE OCR] Captcha filled: {ocr_answer}")
                return True

    except Exception as exc:
        debug.log(f"[FUNONE OCR] Error: {exc}")

    return False

async def nodriver_funone_detect_step(tab):
    """
    Detect which step of the ticket flow we're on.

    Returns:
        int: Step number (1=Area, 2=Quantity, 3=Form, 4=Payment, 5=Complete, 0=Unknown)
    """
    try:
        detect_step_js = '''
        (function() {
            const url = window.location.href;
            const bodyText = document.body.textContent || '';

            // Priority 1: Check URL patterns (most reliable)
            if (url.includes('purchase_choose_ticket_no_map') || url.includes('purchase_choose_ticket')) {
                // Ticket type/quantity selection page
                return 1;
            }
            if (url.includes('purchase_fill_form')) {
                // Form filling page
                return 3;
            }
            if (url.includes('purchase_checkout')) {
                // Payment/checkout page
                return 4;
            }

            // Priority 2: Check URL for step parameter
            const stepMatch = url.match(/[?&]step=(\d+)/);
            if (stepMatch) {
                return parseInt(stepMatch[1]);
            }

            // Priority 3: Check for specific DOM patterns
            // Step 1: Area/Ticket selection
            const zoneBoxes = document.querySelectorAll('.zone_box');
            if (zoneBoxes.length > 0) {
                return 1;
            }

            // Step 1/2: Ticket type selection - has +/- buttons for quantity
            // Look for ticket price/type layout with quantity controls
            const plusBtns = document.querySelectorAll('button');
            let hasPlusMinusBtn = false;
            for (const btn of plusBtns) {
                const text = btn.textContent.trim();
                if (text === '+' || text === '-') {
                    hasPlusMinusBtn = true;
                    break;
                }
            }
            // Check for ticket selection page (has textbox for quantity input)
            const qtyInputs = document.querySelectorAll('input[type="text"][value="0"]');
            if (hasPlusMinusBtn && qtyInputs.length > 0) {
                // This is ticket selection page, not form filling
                return 1;
            }
            if (hasPlusMinusBtn && (bodyText.includes('張數') || bodyText.includes('票種'))) {
                return 2;
            }

            // Step 3: Form filling - must have actual form inputs (not just quantity inputs)
            const formInputs = document.querySelectorAll('input[type="text"]:not([value="0"]), input[type="email"], input[type="tel"]');
            if (formInputs.length >= 3 && bodyText.includes('填寫')) {
                return 3;
            }

            // Step 4: Payment page - must have specific payment elements
            const hasPaymentForm = document.querySelector('input[name*="credit"], input[name*="card"], select[name*="payment"]');
            if (hasPaymentForm || (bodyText.includes('付款方式') && bodyText.includes('信用卡'))) {
                return 4;
            }

            // Step 5: Complete
            if (bodyText.includes('購票完成') || bodyText.includes('訂單成功')) {
                return 5;
            }

            return 0; // Unknown
        })()
        '''
        step = await tab.evaluate(detect_step_js)
        step = util.parse_nodriver_result(step)
        return int(step) if step else 0

    except Exception as exc:
        return 0

async def nodriver_funone_ticket_agree(tab):
    """
    Check agreement checkboxes

    Returns:
        bool: True if agreements checked
    """
    try:
        check_agree_js = '''
        (function() {
            let checked = 0;

            // FunOne-specific: custom div.checkbox elements
            // Structure: <div class="checkbox_block active"> <div class="checkbox"><svg>...</svg></div> </div>
            // The parent checkbox_block gets 'active' class when checked
            const customCheckboxes = document.querySelectorAll('.checkbox_block .checkbox, div.checkbox');
            for (const cb of customCheckboxes) {
                // Check if not already checked
                // FunOne: parent element gets 'active' class when checked
                const parent = cb.parentElement;
                const parentActive = parent && parent.classList.contains('active');
                const selfChecked = cb.classList.contains('checked') || cb.classList.contains('active');

                if (!parentActive && !selfChecked) {
                    cb.click();
                    checked++;
                }
            }

            if (checked > 0) {
                return checked;
            }

            // Standard input checkboxes
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');

            for (const cb of checkboxes) {
                if (!cb.checked) {
                    // Try multiple ways to find the associated text
                    const label = cb.closest('label') || document.querySelector(`label[for="${cb.id}"]`);
                    let text = label ? label.textContent : '';

                    // If no label text, check parent/sibling elements
                    if (!text && cb.parentElement) {
                        text = cb.parentElement.textContent || '';
                    }

                    // FunOne specific: check for nearby text about terms/agreement
                    const nearbyText = cb.closest('div')?.textContent || '';

                    // Check if it's an agreement checkbox
                    if (text.includes('同意') || text.includes('agree') || text.includes('條款') ||
                        text.includes('terms') || text.includes('規則') || text.includes('閱讀') ||
                        nearbyText.includes('同意') || nearbyText.includes('服務條款')) {
                        cb.click(); // Use click instead of just setting checked for better event handling
                        checked++;
                    }
                }
            }

            // If no checkbox found with text, just click any unchecked checkbox
            if (checked === 0) {
                for (const cb of checkboxes) {
                    if (!cb.checked) {
                        cb.click();
                        checked++;
                        break; // Only click first unchecked checkbox
                    }
                }
            }

            return checked;
        })()
        '''
        result = await tab.evaluate(check_agree_js)
        return result >= 0

    except Exception as exc:
        return False

async def nodriver_funone_order_submit(tab, config_dict):
    """
    Submit order - click submit button

    Returns:
        bool: True if order submitted
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # Find and click submit button
        submit_js = '''
        (function() {
            const buttons = document.querySelectorAll('button, input[type="submit"]');

            for (const btn of buttons) {
                const text = (btn.textContent || btn.value || '').trim();

                // Submit button patterns - FunOne uses "立即購買"
                if (text.includes('立即購買') || text.includes('確認') || text.includes('送出') ||
                    text.includes('提交') || text.includes('Submit') || text.includes('Confirm') ||
                    text.includes('購買') || text === '確定' || text === '下一步') {

                    // Check if button is visible and enabled
                    const style = window.getComputedStyle(btn);
                    if (style.display !== 'none' && !btn.disabled) {
                        btn.click();
                        return { clicked: true, buttonText: text };
                    }
                }
            }

            return { clicked: false };
        })()
        '''
        result = await tab.evaluate(submit_js)
        result = util.parse_nodriver_result(result)

        if result and isinstance(result, dict) and result.get('clicked'):
            debug.log(f"[FUNONE] Submit button clicked: {result.get('buttonText')}")
            _state["submit_notfound"] = False  # Reset flag on success
            return True
        else:
            # Only print once when submit button not found
            if not _state.get("submit_notfound"):
                debug.log("[FUNONE] Submit button not found or not clickable")
                _state["submit_notfound"] = True
            return False

    except Exception as exc:
        debug.log(f"[FUNONE] Order submit error: {exc}")
        return False

async def nodriver_funone_auto_reload(tab, config_dict):
    """
    Auto reload page for error handling and coming soon detection

    Returns:
        bool: True if page was reloaded
    """
    debug = util.create_debug_logger(config_dict)

    # Skip auto-reload for non-activity pages (safety check)
    try:
        current_url = tab.url
        if '/purchase_waiting_jump/' in current_url or '/purchase_fill_form/' in current_url:
            return False
    except:
        pass

    try:
        # Check for error pages or coming soon
        check_status_js = '''
        (function() {
            const bodyText = document.body.textContent || '';
            const title = document.title || '';

            // Error page patterns
            if (bodyText.includes('503') || bodyText.includes('502') || bodyText.includes('500') ||
                title.includes('Error') || bodyText.includes('Service Unavailable')) {
                return { status: 'error', reason: 'server_error' };
            }

            // Coming soon / not yet available
            if (bodyText.includes('即將開賣') || bodyText.includes('尚未開放') ||
                bodyText.includes('Coming Soon') || bodyText.includes('Not Available')) {
                return { status: 'coming_soon', reason: 'not_available' };
            }

            // Sold out detection - be smart about it
            // On FunOne area selection page, "已售完" appears next to disabled areas
            // Only trigger sold out if ALL available areas are sold out

            // Check if we're on area selection page (has zone_box elements)
            const zoneBoxes = document.querySelectorAll('.zone_box');
            if (zoneBoxes.length > 0) {
                // On area selection page - check if any area is available
                let hasAvailable = false;
                for (const box of zoneBoxes) {
                    if (!box.classList.contains('disabled')) {
                        hasAvailable = true;
                        break;
                    }
                }
                if (!hasAvailable) {
                    return { status: 'sold_out', reason: 'all_areas_sold_out' };
                }
                // Some areas available, not sold out
                return { status: 'ok' };
            }

            // Check if we're on quantity selection page (Step 2)
            // Has ticket info table but may show "熱賣中" etc - not sold out
            const step2Indicators = document.querySelectorAll('.ticket_info, [class*="step2"], [class*="quantity"]');
            if (step2Indicators.length > 0 || bodyText.includes('張數') || bodyText.includes('票種')) {
                // On quantity page, don't trigger sold out unless specific message
                if (bodyText.includes('已無票券') || bodyText.includes('No tickets available')) {
                    return { status: 'sold_out', reason: 'no_tickets_message' };
                }
                return { status: 'ok' };
            }

            // For other pages, check for actual sold out indicators
            // Only if the page seems to be a final "sold out" page
            const soldOutPatterns = ['已售完', 'Sold Out', 'sold out'];
            let hasSoldOutText = false;
            for (const pattern of soldOutPatterns) {
                if (bodyText.includes(pattern)) {
                    hasSoldOutText = true;
                    break;
                }
            }

            // Only report sold out if the entire page seems to be about sold out
            // Not just a label next to some areas
            if (hasSoldOutText) {
                // Check if there are any actionable buttons (if yes, not sold out page)
                const actionButtons = document.querySelectorAll('button:not(:disabled)');
                let hasActionButton = false;
                for (const btn of actionButtons) {
                    const text = btn.textContent || '';
                    if (text.includes('購買') || text.includes('下一步') || text.includes('確認') ||
                        text.includes('選') || text.includes('+')) {
                        hasActionButton = true;
                        break;
                    }
                }
                if (!hasActionButton) {
                    return { status: 'sold_out', reason: 'no_tickets' };
                }
            }

            return { status: 'ok' };
        })()
        '''
        status = await tab.evaluate(check_status_js)
        status = util.parse_nodriver_result(status)

        if status and isinstance(status, dict):
            page_status = status.get('status')
            reason = status.get('reason', '')

            if page_status == 'error':
                debug.log(f"[FUNONE] Error page detected: {reason}, reloading...")
                await tab.reload()
                return True

            elif page_status == 'coming_soon':
                auto_reload_coming_soon = config_dict.get("tixcraft", {}).get("auto_reload_coming_soon_page", True)
                if auto_reload_coming_soon:
                    debug.log("[FUNONE] Coming soon page, auto-reloading...")
                    await tab.sleep(1)
                    await tab.reload()
                    return True

            elif page_status == 'sold_out':
                debug.log("[FUNONE] Sold out detected")
                return False

        return False

    except Exception as exc:
        debug.log(f"[FUNONE] Auto reload error: {exc}")
        return False

async def nodriver_funone_error_handler(tab, error, config_dict):
    """
    Handle various error types

    Returns:
        bool: True if error was handled
    """
    debug = util.create_debug_logger(config_dict)

    error_str = str(error).lower()

    if 'timeout' in error_str:
        debug.log("[FUNONE] Timeout error, reloading page...")
        try:
            await tab.reload()
            return True
        except:
            pass

    if 'network' in error_str or 'connection' in error_str:
        debug.log("[FUNONE] Network error, waiting and retrying...")
        await tab.sleep(2)
        try:
            await tab.reload()
            return True
        except:
            pass

    return False

async def nodriver_funone_main(tab, url, config_dict):
    """
    Main control function for FunOne Tickets platform

    Args:
        tab: NoDriver tab
        url: Current page URL
        config_dict: Configuration dictionary

    Returns:
        tab: Updated NoDriver tab
    """

    # Check pause state
    if await check_and_handle_pause(config_dict):
        return tab

    # Initialize state dictionary
    if not _state:
        _state.update({
            "is_session_selecting": False,
            "is_ticket_selecting": False,
            "played_sound_ticket": False,
            "played_sound_order": False,
            "fail_list": [],
            "reload_count": 0,
            # State tracking for log deduplication
            "last_page_type": None,
            "last_step": None,
            "last_login_status": None,
            "last_area_count": None,
            "last_area_config": None,
            "last_ticket_qty": None,
            "qty_selector_notfound": False,
            "submit_notfound": False,
            "last_captcha_type": None,
            "waiting_captcha_printed": False,
            "captcha_filled_printed": False,
            "ocr_retry_count": 0,
            "ocr_exhausted": False,
            "captcha_attempted": False,
            "checkout_printed": False,
            "next_button_clicked": False,
            # Sold-out refresh tracking
            "refresh_retry_count": 0,
            "last_sold_out_logged": False,
            "max_retry_logged": False,
            "last_homepage_redirect_time": 0,
        })

    debug = util.create_debug_logger(config_dict)

    # Determine page type
    page_type = "UNKNOWN"

    if 'tickets.funone.io' in url:
        if '/activity/activity_detail/' in url:
            page_type = "ACTIVITY_DETAIL"
        elif '/login' in url:
            page_type = "LOGIN"
        elif '/member' in url:
            page_type = "MEMBER"
        elif url.rstrip('/') == 'https://tickets.funone.io':
            page_type = "HOME"
        elif '/purchase_waiting_jump/' in url:
            page_type = "WAITING"
        else:
            # Check for ticket selection or order pages dynamically
            page_type = "TICKET_FLOW"

    # Only print when page type changes (reduce repetitive messages)
    if _state.get("last_page_type") != page_type:
        debug.log(f"[FUNONE] Page type: {page_type}, URL: {url[:80]}...")
        _state["last_page_type"] = page_type
        # Reset flags when page type changes
        _state["waiting_page_logged"] = False
        _state["next_button_clicked"] = False
        # Reset sold-out refresh tracking
        _state["refresh_retry_count"] = 0
        _state["last_sold_out_logged"] = False
        _state["max_retry_logged"] = False
        # Reset OCR retry state
        _state["ocr_retry_count"] = 0
        _state["ocr_exhausted"] = False
        _state["waiting_captcha_printed"] = False
        _state["captcha_filled_printed"] = False

    # Close popups first
    await nodriver_funone_close_popup(tab)

    # Handle different page types
    if page_type == "HOME":
        # On homepage, ensure logged in then redirect to target event if homepage is not root
        await nodriver_funone_verify_login(tab, config_dict)
        homepage = config_dict["homepage"]
        homepage_is_root = homepage.rstrip('/') == 'https://tickets.funone.io'
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

    elif page_type == "ACTIVITY_DETAIL":
        # Activity detail page - select session and click next
        is_logged_in = await nodriver_funone_verify_login(tab, config_dict)

        if is_logged_in:
            if not _state.get("is_session_selecting", False):
                _state["is_session_selecting"] = True
                success = await nodriver_funone_date_auto_select(tab, url, config_dict)
                _state["is_session_selecting"] = False
                # Mark if navigation was triggered (next button clicked)
                # This prevents auto_reload from running during page transition
                if success:
                    _state["next_button_clicked"] = True

    elif page_type == "LOGIN":
        # Login page - try cookie injection
        await nodriver_funone_verify_login(tab, config_dict)

    elif page_type == "WAITING":
        # Waiting/queue page - do nothing, just wait for auto-redirect
        if not _state.get("waiting_page_logged", False):
            debug.log("[FUNONE] Waiting page detected, waiting for auto-redirect...")
            _state["waiting_page_logged"] = True
        # Don't take any action - page will redirect automatically when it's user's turn

    elif page_type == "TICKET_FLOW":
        # Ticket selection flow
        is_logged_in = await nodriver_funone_verify_login(tab, config_dict)

        if is_logged_in:
            # Detect which step we're on
            step = await nodriver_funone_detect_step(tab)

            # Only print when step changes (reduce repetitive messages)
            if _state.get("last_step") != step:
                debug.log(f"[FUNONE] Detected step: {step}")
                _state["last_step"] = step

            if step == 1:
                # Step 1: Ticket type/quantity selection
                # FunOne: purchase_choose_ticket_no_map is a combined ticket selection + quantity page

                # Check if on purchase_choose_ticket_no_map page - apply sold-out detection
                if '/purchase_choose_ticket_no_map/' in url:
                    # Wait for Vue to fully render the ticket rows
                    # Must check for btn-tertiary (+/- buttons) - present even when sold out
                    # Body text check alone is insufficient (initial HTML already has '票種')
                    wait_js = '''
                    (function() {
                        // btn-tertiary are the quantity +/- buttons, rendered only after Vue mounts
                        const btnTertiary = document.querySelectorAll('button.btn-tertiary');
                        if (btnTertiary.length > 0) return true;
                        // Fallback: purchase button with correct text
                        const btns = document.querySelectorAll('button');
                        for (const btn of btns) {
                            const text = btn.textContent || '';
                            if (text.includes('\u7acb\u5373\u8cfc\u8cb7') || text.includes('Purchase')) {
                                return true;
                            }
                        }
                        return false;
                    })()
                    '''
                    page_ready = await tab.evaluate(wait_js)
                    page_ready = util.parse_nodriver_result(page_ready)
                    if not page_ready:
                        # Page not ready, wait and retry next iteration
                        await tab.sleep(0.3)
                        return tab

                    # Check sold-out status first
                    is_sold_out, remaining, ticket_info = await nodriver_funone_check_sold_out(tab, config_dict)
                    ticket_number = config_dict.get("ticket_number", 2)
                    auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 2)

                    # Handle sold-out or insufficient tickets
                    if is_sold_out or (remaining > 0 and remaining < ticket_number):
                        # Increment retry counter (no limit - keep refreshing until tickets available)
                        _state["refresh_retry_count"] = _state.get("refresh_retry_count", 0) + 1

                        # Log status (only once per state)
                        if is_sold_out:
                            if not _state.get("last_sold_out_logged", False):
                                debug.log("[FUNONE] Sold out, clicking refresh button...")
                                _state["last_sold_out_logged"] = True
                        else:
                            debug.log(f"[FUNONE] Remaining {remaining} < needed {ticket_number}, refreshing...")

                        # Click refresh button to trigger WebSocket update
                        refresh_clicked = await nodriver_funone_click_refresh_button(tab, config_dict)

                        if refresh_clicked:
                            # Wait for WebSocket response - use asyncio.sleep for reliable timing
                            debug.log(f"[FUNONE] Waiting {auto_reload_interval} seconds...")
                            await asyncio.sleep(auto_reload_interval)
                        else:
                            # Fallback: reload page if refresh button not found
                            debug.log("[FUNONE] Refresh button not found, reloading page...")
                            await asyncio.sleep(auto_reload_interval)
                            await tab.reload()

                        return tab  # Next iteration will re-check status

                    # Tickets available - reset retry counter and proceed
                    _state["refresh_retry_count"] = 0
                    _state["last_sold_out_logged"] = False

                # Try area selection first (for zone_box pages)
                area_selected = await nodriver_funone_area_auto_select(tab, url, config_dict)

                # If no area selected (no zone_box elements), this is a quantity selection page
                # Proceed to set quantity, agreements, and submit
                if not area_selected:
                    # Set ticket number
                    qty_set = await nodriver_funone_assign_ticket_number(tab, config_dict)

                    if not qty_set:
                        # Keyword ticket is sold out - keep refreshing until available
                        if _state.get("qty_fail_reason") == "sold_out":
                            refresh_clicked = await nodriver_funone_click_refresh_button(tab, config_dict)
                            if not _state.get("qty_sold_out_refreshing"):
                                debug.log(f"[FUNONE] Keyword ticket sold out, auto-refreshing every {auto_reload_interval}s...")
                                _state["qty_sold_out_refreshing"] = True
                            if refresh_clicked:
                                await asyncio.sleep(auto_reload_interval)
                            else:
                                await asyncio.sleep(auto_reload_interval)
                                await tab.reload()
                        return tab

                    _state["qty_sold_out_refreshing"] = False
                    await tab.sleep(0.3)

                    # Check agreements
                    await nodriver_funone_ticket_agree(tab)
                    await tab.sleep(0.2)

                    # Step 1 (purchase_choose_ticket_no_map) has no captcha
                    # Directly click purchase button if quantity is set
                    if qty_set:
                        await nodriver_funone_order_submit(tab, config_dict)
                else:
                    await tab.sleep(0.5)
                    # Page should navigate to step 2 after area selection

            elif step == 2:
                # Step 2: Quantity selection
                # Set ticket number
                qty_set = await nodriver_funone_assign_ticket_number(tab, config_dict)
                await tab.sleep(0.3)

                # Check agreements
                await nodriver_funone_ticket_agree(tab)
                await tab.sleep(0.2)

                # Handle captcha
                captcha_done = await nodriver_funone_captcha_handler(tab, config_dict)

                if captcha_done and qty_set:
                    # Step 2 captcha filled - submit to proceed
                    await nodriver_funone_order_submit(tab, config_dict)

            elif step >= 3:
                # Step 3+: Form filling, payment, checkout, complete
                if 'purchase_fill_form' in url:
                    # Fill form page - order is already reserved!
                    # Just need to fill captcha once, then stop.
                    # User has 10 minutes to complete payment.
                    if not _state.get("played_sound_order", False):
                        if config_dict["advanced"]["play_sound"]["order"]:
                            play_sound_while_ordering(config_dict)
                        send_discord_notification(config_dict, "order", "FunOne")
                        send_telegram_notification(config_dict, "order", "FunOne")
                        _state["played_sound_order"] = True
                        debug.log("[FUNONE] Order reserved! Fill captcha then stop.")

                    # Fill captcha once, then stop automation
                    if not _state.get("captcha_attempted", False):
                        captcha_done = await nodriver_funone_captcha_handler(tab, config_dict)
                        if captcha_done:
                            _state["captcha_attempted"] = True
                            debug.log("[FUNONE] Captcha filled. Please complete payment within 10 minutes.")

                elif 'purchase_checkout' in url:
                    # Checkout/payment page - do nothing, wait for user to pay
                    if not _state.get("checkout_printed", False):
                        debug.log("[FUNONE] Checkout page reached, waiting for payment...")
                        _state["checkout_printed"] = True

            else:
                # Unknown step - try area selection first, then quantity
                area_selected = await nodriver_funone_area_auto_select(tab, url, config_dict)

                if not area_selected:
                    # Maybe we're already past area selection, try quantity
                    await nodriver_funone_assign_ticket_number(tab, config_dict)
                    await tab.sleep(0.3)
                    await nodriver_funone_ticket_agree(tab)
                    captcha_done = await nodriver_funone_captcha_handler(tab, config_dict)
                    if captcha_done:
                        # FunOne: Do not auto-submit, let user manually review and submit
                        print("[FUNONE] Captcha filled, waiting for manual submit")

    elif page_type == "MEMBER":
        # Member page - verify login status
        await nodriver_funone_verify_login(tab, config_dict)

    # Auto reload check - only for ACTIVITY_DETAIL page
    # Skip if next button was clicked (page is navigating to waiting page)
    if page_type == "ACTIVITY_DETAIL":
        if not _state.get("next_button_clicked", False):
            await nodriver_funone_auto_reload(tab, config_dict)

    return tab

