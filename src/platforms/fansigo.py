#!/usr/bin/env python3
#encoding=utf-8
"""platforms/fansigo.py -- FANSI GO platform (go.fansi.me)."""

import asyncio
import json
import re
import time
from urllib.parse import quote, unquote

from zendriver import cdp

import util
from nodriver_common import check_and_handle_pause, play_sound_while_ordering, sleep_with_pause_check
from nodriver_common import CONST_FROM_TOP_TO_BOTTOM

# =============================================================================
# FANSI GO Platform Support
# URL: https://go.fansi.me
# Features: Multi-show selection, multi-section selection, Cookie login
# =============================================================================

__all__ = [
    "FANSIGO_URL_PATTERNS",
    "FANSIGO_COGNITO_DOMAIN",
    "is_fansigo_url",
    "get_fansigo_page_type",
    "fansigo_normalize_cookie_value",
    "nodriver_fansigo_inject_cookie",
    "nodriver_fansigo_signin",
    "nodriver_fansigo_get_shows",
    "nodriver_fansigo_click_show",
    "fansigo_match_by_keyword",
    "nodriver_fansigo_date_auto_select",
    "nodriver_fansigo_get_sections",
    "nodriver_fansigo_area_auto_select",
    "nodriver_fansigo_assign_ticket_number",
    "nodriver_fansigo_click_checkout",
    "nodriver_fansigo_main",
]

# Module-level state (replaces global fansigo_dict)
_state = {}

# FANSI GO URL patterns
FANSIGO_URL_PATTERNS = {
    "domain": r"go\.fansi\.me",
    "home_page": r"go\.fansi\.me/?(?:[?#].*)?$",
    "login_page": r"go\.fansi\.me/login",
    "event_page": r"go\.fansi\.me/events/(\d+)",
    "show_page": r"go\.fansi\.me/tickets/show/(\d+)",
    "checkout_page": r"go\.fansi\.me/tickets/payment/checkout/",
    "order_result": r"go\.fansi\.me/tickets/payment/orderresult/",
}

FANSIGO_COGNITO_DOMAIN = "fansidev.auth.ap-southeast-1.amazoncognito.com"

# Page texts in Chinese and English. A new profile that opens a show page
# directly gets English saved in the fansi:lang cookie. Compared in lower case.
CONST_FANSIGO_SECTION_HEADINGS = ("選擇票券種類", "Select Tickets")
CONST_FANSIGO_SHOW_LIST_HEADINGS = ("請選擇活動場次進行購買", "Select a session to purchase.")
CONST_FANSIGO_COUNTDOWN_TEXTS = ("開賣倒數", "after the countdown")
CONST_FANSIGO_COMING_SOON_TEXTS = ("尚未開賣", "Coming Soon")
CONST_FANSIGO_SOLD_OUT_TEXTS = ("已售完", "你已太晚", "Sold out", "late to the party")
CONST_FANSIGO_OTHER_LOGIN_TEXTS = ("其他方式", "another login method")
CONST_FANSIGO_CHECKOUT_TEXTS = (
    "checkout", "submit", "buy", "next", "continue", "get ticket",
    "取得訂單", "結帳", "購買", "下一步",
)
CONST_FANSIGO_MIN_REDIRECT_INTERVAL = 3


def _fansigo_lower_json(texts) -> str:
    """Page texts as a lower case JSON array for injected scripts."""
    return json.dumps([text.lower() for text in texts])


def _fansigo_text_check_js(texts) -> str:
    """Script that returns true when any of the texts is on the page."""
    return '''
        (function() {
            const texts = %s;
            const page = (document.body ? document.body.innerText : '').toLowerCase();
            return texts.some(text => page.includes(text));
        })()
    ''' % _fansigo_lower_json(texts)


def _fansigo_show_page_state_js() -> str:
    """Script that reads what decides whether a show page can be reloaded."""
    return '''
        (function() {
            const page = (document.body ? document.body.innerText : '').toLowerCase();
            const hasAny = texts => texts.some(text => page.includes(text));
            return {
                hasHeading: hasAny(%s),
                hasCountdown: hasAny(%s),
                sectionCount: document.querySelectorAll('li.list-none').length
            };
        })()
    ''' % (_fansigo_lower_json(CONST_FANSIGO_SECTION_HEADINGS),
           _fansigo_lower_json(CONST_FANSIGO_COUNTDOWN_TEXTS))


def _fansigo_sections_js() -> str:
    """Script that lists the sections on a show page with their status."""
    return '''
        (function() {
            const comingSoonTexts = %s;
            const soldOutTexts = %s;
            var elems = document.querySelectorAll('li.list-none');
            var items = [];
            for (var i = 0; i < elems.length; i++) {
                var text = elems[i].textContent.trim();
                var lowerText = text.toLowerCase();
                var h3 = elems[i].querySelector('h3');
                var name = h3 ? h3.textContent.trim() : '';
                if (!name) {
                    var p = elems[i].querySelector('p');
                    name = p ? p.textContent.trim() : '';
                }
                var hasButton = elems[i].querySelectorAll('button').length > 0;
                var status = 'unavailable';
                if (comingSoonTexts.some(t => lowerText.includes(t))) status = 'coming_soon';
                else if (soldOutTexts.some(t => lowerText.includes(t))) status = 'sold_out';
                else if (hasButton) status = 'on_sale';
                items.push({index: i, name: name, text: text, status: status});
            }
            return {items: items, count: items.length};
        })()
    ''' % (_fansigo_lower_json(CONST_FANSIGO_COMING_SOON_TEXTS),
           _fansigo_lower_json(CONST_FANSIGO_SOLD_OUT_TEXTS))


def _fansigo_other_login_js() -> str:
    """Script that clicks the button leading to the account login form."""
    return '''
        (function() {
            const texts = %s;
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = (btn.textContent || '').toLowerCase();
                if (texts.some(t => text.includes(t))) {
                    btn.click();
                    return 'clicked';
                }
            }
            return 'not_found';
        })()
    ''' % _fansigo_lower_json(CONST_FANSIGO_OTHER_LOGIN_TEXTS)


def _fansigo_checkout_js() -> str:
    """Script that clicks the checkout button on a show page."""
    return '''
        (function() {
            var keywords = %s;
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = (buttons[i].textContent || '').trim().toLowerCase();
                for (var j = 0; j < keywords.length; j++) {
                    if (text.indexOf(keywords[j]) >= 0) {
                        buttons[i].click();
                        return {clicked: true, text: buttons[i].textContent.trim()};
                    }
                }
            }
            return {clicked: false};
        })()
    ''' % _fansigo_lower_json(CONST_FANSIGO_CHECKOUT_TEXTS)


async def _fansigo_wait_for_any_text(tab, texts, timeout=5) -> bool:
    """True once any of the texts is on the page, False after the timeout."""
    script = _fansigo_text_check_js(texts)
    deadline = time.time() + timeout
    while True:
        if await tab.evaluate(script) is True:
            return True
        if time.time() >= deadline:
            return False
        await asyncio.sleep(0.2)

def is_fansigo_url(url: str) -> bool:
    """Check if URL is a FANSI GO URL"""
    if url is None:
        return False
    return bool(re.search(FANSIGO_URL_PATTERNS["domain"], url))

def get_fansigo_page_type(url: str) -> str:
    """Get FANSI GO page type from URL

    Returns:
        str: "home", "login", "event", "show", "checkout", "order_result", or "unknown"
    """
    if url is None:
        return "unknown"

    if re.search(FANSIGO_URL_PATTERNS["home_page"], url):
        return "home"
    if re.search(FANSIGO_URL_PATTERNS["login_page"], url):
        return "login"
    if re.search(FANSIGO_URL_PATTERNS["checkout_page"], url):
        return "checkout"
    if re.search(FANSIGO_URL_PATTERNS["order_result"], url):
        return "order_result"
    if re.search(FANSIGO_URL_PATTERNS["event_page"], url):
        return "event"
    if re.search(FANSIGO_URL_PATTERNS["show_page"], url):
        return "show"

    return "unknown"

def fansigo_normalize_cookie_value(raw_value):
    """Normalize FansiAuthInfo cookie value to URL-encoded JSON format.

    Handles three input formats:
    1. URL-encoded JSON (from browser F12 copy) - pass through
    2. Raw JSON string - auto URL-encode
    3. Bare JWT token (eyJ...) - wrap in JSON structure and URL-encode

    Returns:
        tuple: (normalized_value, format_description) or (None, error_msg)
    """
    value = raw_value.strip()

    # Strip "FansiAuthInfo=" prefix if user copied full cookie string
    if value.startswith("FansiAuthInfo="):
        value = value[len("FansiAuthInfo="):]

    # Case 1: Already URL-encoded JSON
    if value.startswith("%7B") or value.startswith("%7b"):
        try:
            decoded = unquote(value)
            parsed = json.loads(decoded)
            if "accessToken" in parsed:
                return value, "URL-encoded JSON"
        except (json.JSONDecodeError, ValueError):
            pass

    # Case 2: Raw JSON
    if value.startswith("{"):
        try:
            parsed = json.loads(value)
            if "accessToken" in parsed:
                return quote(value), "raw JSON (auto URL-encoded)"
        except (json.JSONDecodeError, ValueError):
            return None, "invalid JSON structure"

    # Case 3: Bare JWT token
    if value.startswith("eyJ"):
        auth_info = json.dumps({
            "__typename": "userToken",
            "accessToken": value,
            "tokenLife": 604800
        })
        return quote(auth_info), "bare JWT (auto-wrapped)"

    # Unknown format - use as-is
    return value, "unknown format (as-is)"


async def nodriver_fansigo_inject_cookie(tab, config_dict):
    """Inject FansiAuthInfo cookie for FANSI GO login

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary

    Returns:
        bool: True if injection successful; False if no cookie is configured,
            the cookie format is invalid, or injection fails
    """
    debug = util.create_debug_logger(config_dict)
    fansigo_cookie = config_dict["accounts"].get("fansigo_cookie", "").strip()

    if len(fansigo_cookie) == 0:
        debug.log("[FANSIGO] No cookie configured")
        return False

    # Normalize cookie format
    cookie_value, format_desc = fansigo_normalize_cookie_value(fansigo_cookie)
    if cookie_value is None:
        debug.log(f"[FANSIGO] Cookie format error: {format_desc}")
        return False

    debug.log(f"[FANSIGO] Cookie format: {format_desc}")

    try:
        await tab.send(cdp.network.set_cookie(
            name="FansiAuthInfo",
            value=cookie_value,
            domain="go.fansi.me",
            path="/",
            secure=True,
            http_only=False,
        ))

        debug.log("[FANSIGO] Cookie injected successfully")
        return True

    except Exception as e:
        debug.log(f"[FANSIGO] Cookie injection failed: {e}")
        return False


async def nodriver_fansigo_signin(tab, url, config_dict):
    """Handle FANSI GO login page and AWS Cognito authentication.

    Flow:
    1. On go.fansi.me/login -> click "other method" to redirect to Cognito
    2. On Cognito hosted UI -> fill email/password and submit
    3. Cognito redirects back to go.fansi.me with auth code -> app sets cookies

    Args:
        tab: NoDriver tab
        url: Current page URL
        config_dict: Configuration dictionary

    Returns:
        bool: True if login action was taken
    """
    debug = util.create_debug_logger(config_dict)

    fansigo_account = config_dict["accounts"].get("fansigo_account", "").strip()
    fansigo_password = config_dict["accounts"].get("fansigo_password", "").strip()

    if len(fansigo_account) == 0 or len(fansigo_password) == 0:
        debug.log("[FANSIGO] No account/password configured, manual login required")
        return False

    # On FANSI GO login page: click "other method" to go to Cognito
    if "go.fansi.me/login" in url:
        try:
            js_result = await tab.evaluate(_fansigo_other_login_js())
            if js_result == 'clicked':
                debug.log("[FANSIGO] Clicked 'other login method', redirecting to Cognito")
            else:
                debug.log("[FANSIGO] 'Other login method' button not found")
            return True
        except Exception as e:
            debug.log(f"[FANSIGO] Failed to click other login: {e}")
            return False

    # On Cognito hosted UI: fill email/password and submit
    if FANSIGO_COGNITO_DOMAIN in url:
        try:
            js_result = await tab.evaluate("""
                (function() {
                    const emailInput = document.querySelector('#signInFormUsername');
                    const passInput = document.querySelector('#signInFormPassword');
                    const submitBtn = document.querySelector('input[name="signInSubmitButton"]');
                    if (!emailInput || !passInput || !submitBtn) {
                        return 'form_not_found';
                    }
                    if (emailInput.value && passInput.value) {
                        return 'already_filled';
                    }
                    return 'ready';
                })()
            """)

            if js_result == 'form_not_found':
                debug.log("[FANSIGO] Cognito form not found")
                return False

            if js_result == 'already_filled':
                debug.log("[FANSIGO] Cognito form already filled, waiting for redirect")
                return True

            # Fill email
            email_el = await tab.query_selector('#signInFormUsername')
            if email_el:
                await email_el.clear_input()
                await email_el.send_keys(fansigo_account)

            # Fill password
            pass_el = await tab.query_selector('#signInFormPassword')
            if pass_el:
                await pass_el.clear_input()
                await pass_el.send_keys(fansigo_password)

            await asyncio.sleep(0.3)

            # Submit
            submit_el = await tab.query_selector('input[name="signInSubmitButton"]')
            if submit_el:
                await submit_el.click()
                debug.log("[FANSIGO] Cognito login submitted")

            return True
        except Exception as e:
            debug.log(f"[FANSIGO] Cognito login failed: {e}")
            return False

    return False


async def nodriver_fansigo_get_shows(tab, config_dict) -> list:
    """Get all available shows from event page using tab.evaluate()

    NoDriver's query_selector_all() fails on Next.js SPA pages,
    but tab.evaluate() (direct JS execution) works reliably.

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary

    Returns:
        list: List of show dictionaries with href, text, name, datetime, venue
    """
    debug = util.create_debug_logger(config_dict)
    shows = []

    try:
        # Wait for Next.js SPA to render content
        if not await _fansigo_wait_for_any_text(tab, CONST_FANSIGO_SHOW_LIST_HEADINGS):
            debug.log("[FANSIGO] Waiting for event page to render...")
            return shows

        # Extract show data via JavaScript
        # Wrap array in object for util.parse_nodriver_result() compatibility
        js_raw = await tab.evaluate('''
            (function() {
                var links = document.querySelectorAll('a[href*="/tickets/show/"]');
                var items = [];
                for (var i = 0; i < links.length; i++) {
                    items.push({
                        href: links[i].href,
                        text: links[i].textContent.trim()
                    });
                }
                return {items: items, count: items.length};
            })()
        ''')
        js_parsed = util.parse_nodriver_result(js_raw)
        js_result = js_parsed.get('items', []) if isinstance(js_parsed, dict) else []

        if not js_result or len(js_result) == 0:
            return shows

        for item in js_result:
            href = item.get("href", "")
            text = item.get("text", "")
            if not text:
                continue

            # Normalize whitespace
            normalized_text = re.sub(r'\s+', ' ', text).strip()

            name = normalized_text
            datetime_str = ""
            venue = ""

            # Extract datetime
            datetime_match = re.search(r"(\d{4}/\d{2}/\d{2})\s*(\d{2}:\d{2})", normalized_text)
            if datetime_match:
                datetime_str = datetime_match.group(1) + " " + datetime_match.group(2)
                name_end = datetime_match.start()
                if name_end > 0:
                    name = normalized_text[:name_end].strip()
                after_time = normalized_text[datetime_match.end():].strip()
                venue_match = re.match(r"(.+?)(?:\s+\d{3}|$)", after_time)
                if venue_match:
                    venue = venue_match.group(1).strip()

            debug.log(f"[FANSIGO] Show: name={name}, date={datetime_str}, venue={venue}")

            shows.append({
                "href": href,
                "text": normalized_text,
                "name": name,
                "datetime": datetime_str,
                "venue": venue,
            })

        debug.log(f"[FANSIGO] Found {len(shows)} shows")

    except Exception as e:
        debug.log(f"[FANSIGO] Error getting shows: {e}")

    return shows

async def nodriver_fansigo_click_show(tab, show_dict, config_dict):
    """Navigate to show page directly using href

    Uses tab.get() for direct navigation instead of click(),
    which avoids Next.js opening new tabs.

    Args:
        tab: NoDriver tab
        show_dict: Show dictionary with href
        config_dict: Configuration dictionary
    """
    debug = util.create_debug_logger(config_dict)
    href = show_dict.get("href", "")

    if not href:
        raise Exception("No href in show_dict")

    # Build full URL if relative
    if href.startswith("/"):
        href = "https://go.fansi.me" + href

    debug.log(f"[FANSIGO] Navigating to show: {href}")

    await tab.get(href)

def fansigo_match_by_keyword(items: list, keyword_string: str, text_key: str = "text") -> dict:
    """Match item by keyword string

    Args:
        items: List of item dictionaries
        keyword_string: Keyword string (semicolon separated for multiple)
        text_key: Key to use for text matching

    Returns:
        dict: Matched item or None
    """
    if not keyword_string or len(keyword_string.strip()) == 0:
        return None

    for item in items:
        item_text = item.get(text_key, "")
        if util.is_text_match_keyword(keyword_string, item_text):
            return item

    return None

async def nodriver_fansigo_date_auto_select(tab, url, config_dict) -> bool:
    """Auto select show/date on event page

    Args:
        tab: NoDriver tab
        url: Current URL
        config_dict: Configuration dictionary

    Returns:
        bool: True if show selected or not on event page
    """
    debug = util.create_debug_logger(config_dict)

    # Check if date auto select is enabled
    date_auto_select = config_dict.get("date_auto_select", {})
    if not date_auto_select.get("enable", True):
        return True

    # Only process event pages
    if not re.search(FANSIGO_URL_PATTERNS["event_page"], url):
        return True

    # Get all shows
    shows = await nodriver_fansigo_get_shows(tab, config_dict)

    if len(shows) == 0:
        debug.log("[FANSIGO] No shows found on event page")
        return False

    # Single show - click directly
    if len(shows) == 1:
        debug.log(f"[FANSIGO] Single show found, selecting: {shows[0]['name']}")
        try:
            await nodriver_fansigo_click_show(tab, shows[0], config_dict)
            return True
        except Exception as e:
            debug.log(f"[FANSIGO] Error clicking show: {e}")
            return False

    # Multiple shows - use keyword matching
    date_keyword = date_auto_select.get("date_keyword", "")

    if debug.enabled:
        debug.log(f"[FANSIGO] Matching with date_keyword: {date_keyword}")
        for show in shows:
            debug.log(f"[FANSIGO]   Show text: {show['text'][:80]}")

    if date_keyword:
        matched = fansigo_match_by_keyword(shows, date_keyword)
    else:
        matched = None

    if matched:
        debug.log(f"[FANSIGO] Show matched by keyword: {matched['name']}")
        try:
            await nodriver_fansigo_click_show(tab, matched, config_dict)
            return True
        except Exception as e:
            debug.log(f"[FANSIGO] Error clicking matched show: {e}")
            return False

    if not date_keyword:
        # No keyword set = accept all, select by mode
        mode = date_auto_select.get("mode", CONST_FROM_TOP_TO_BOTTOM)
        target = util.get_target_item_from_matched_list(shows, mode)
        if target:
            debug.log(f"[FANSIGO] No keyword set, selecting by mode: {target['name']}")
            try:
                await nodriver_fansigo_click_show(tab, target, config_dict)
                return True
            except Exception as e:
                debug.log(f"[FANSIGO] Error clicking show: {e}")
                return False
        return False

    # Keyword set but no match - check fallback
    date_auto_fallback = config_dict.get("date_auto_fallback", False)
    if date_auto_fallback:
        mode = date_auto_select.get("mode", CONST_FROM_TOP_TO_BOTTOM)
        target = util.get_target_item_from_matched_list(shows, mode)
        if target:
            debug.log(f"[FANSIGO] Using fallback, selecting: {target['name']}")
            try:
                await nodriver_fansigo_click_show(tab, target, config_dict)
                return True
            except Exception as e:
                debug.log(f"[FANSIGO] Error clicking fallback show: {e}")
                return False
        return False

    debug.log("[FANSIGO] No matching show found and fallback disabled")
    return False

async def nodriver_fansigo_get_sections(tab, config_dict) -> list:
    """Get all available ticket sections from show page using tab.evaluate()

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary

    Returns:
        list: List of section dictionaries with index, name, status, text
    """
    debug = util.create_debug_logger(config_dict)
    sections = []

    try:
        # Wait for Next.js SPA to render ticket sections
        if not await _fansigo_wait_for_any_text(tab, CONST_FANSIGO_SECTION_HEADINGS):
            debug.log("[FANSIGO] Waiting for show page to render...")
            return sections

        # Extract section data via JavaScript
        js_raw = await tab.evaluate(_fansigo_sections_js())
        js_parsed = util.parse_nodriver_result(js_raw)
        js_result = js_parsed.get('items', []) if isinstance(js_parsed, dict) else []

        if not js_result:
            return sections

        for item in js_result:
            if not item.get("name"):
                continue

            debug.log(f"[FANSIGO] Section: {item['name']}, status={item['status']}")

            sections.append({
                "index": item["index"],
                "name": item["name"],
                "status": item["status"],
                "text": item.get("text", ""),
            })

        if debug.enabled:
            available = [s for s in sections if s["status"] == "on_sale"]
            debug.log(f"[FANSIGO] Found {len(sections)} sections, {len(available)} available")

    except Exception as e:
        debug.log(f"[FANSIGO] Error getting sections: {e}")

    return sections

async def nodriver_fansigo_area_auto_select(tab, url, config_dict) -> int:
    """Auto select ticket section/area on show page

    Args:
        tab: NoDriver tab
        url: Current URL
        config_dict: Configuration dictionary

    Returns:
        int: Selected section index, or -1 if no section selected
    """
    debug = util.create_debug_logger(config_dict)

    # Check if area auto select is enabled
    area_auto_select = config_dict.get("area_auto_select", {})
    if not area_auto_select.get("enable", True):
        return 0

    # Only process show pages
    if not re.search(FANSIGO_URL_PATTERNS["show_page"], url):
        return 0

    # Get all sections
    sections = await nodriver_fansigo_get_sections(tab, config_dict)

    # Filter to available sections only
    available_sections = [s for s in sections if s["status"] == "on_sale"]

    if len(available_sections) == 0:
        debug.log("[FANSIGO] No available sections found")
        return -1

    # Apply exclude keywords
    keyword_exclude = config_dict.get("keyword_exclude", "")
    if keyword_exclude:
        filtered_sections = []
        for section in available_sections:
            if util.reset_row_text_if_match_keyword_exclude(config_dict, section["name"]):
                debug.log(f"[FANSIGO] Section excluded by keyword_exclude: {section['name']}")
            else:
                filtered_sections.append(section)
        available_sections = filtered_sections

    if len(available_sections) == 0:
        debug.log("[FANSIGO] All sections excluded by keyword_exclude")
        return -1

    # Use keyword matching
    area_keyword = area_auto_select.get("area_keyword", "")

    if area_keyword:
        matched = fansigo_match_by_keyword(available_sections, area_keyword, "name")
    else:
        matched = None

    target_section = None

    if matched:
        target_section = matched
        debug.log(f"[FANSIGO] Section matched by keyword: {matched['name']}")
    elif not area_keyword:
        # No keyword set = accept all, select by mode
        mode = area_auto_select.get("mode", CONST_FROM_TOP_TO_BOTTOM)
        target_section = util.get_target_item_from_matched_list(available_sections, mode)
        if target_section:
            debug.log(f"[FANSIGO] No keyword set, selecting by mode: {target_section['name']}")
    else:
        # Keyword set but no match - check fallback
        area_auto_fallback = config_dict.get("area_auto_fallback", False)
        if area_auto_fallback:
            mode = area_auto_select.get("mode", CONST_FROM_TOP_TO_BOTTOM)
            target_section = util.get_target_item_from_matched_list(available_sections, mode)
            if target_section:
                debug.log(f"[FANSIGO] Using fallback, selecting: {target_section['name']}")
        else:
            debug.log("[FANSIGO] No matching section found and fallback disabled")
            return -1

    # Click the section to select it
    if target_section:
        try:
            section_index = target_section["index"]
            await tab.evaluate('''
                (function() {
                    var items = document.querySelectorAll('li.list-none');
                    if (items[%d]) { items[%d].click(); }
                })()
            ''' % (section_index, section_index))
            await asyncio.sleep(0.3)
            return section_index
        except Exception as e:
            debug.log(f"[FANSIGO] Error clicking section: {e}")
            return -1

    return -1

async def nodriver_fansigo_assign_ticket_number(tab, config_dict, section_index=0) -> bool:
    """Set ticket quantity on show page using tab.evaluate()

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary
        section_index: Target section index from area_auto_select

    Returns:
        bool: True if quantity set successfully
    """
    debug = util.create_debug_logger(config_dict)
    target_count = config_dict.get("ticket_number", 1)

    if target_count < 1:
        target_count = 1

    try:
        # Click + button one at a time with delay for React state updates
        # React 18 batches synchronous state updates, so clicking N times
        # in a single JS execution only registers as 1 click.
        js_click_once = '''
        (function() {
            var sections = document.querySelectorAll('li.list-none');
            var target = sections[%d];
            if (!target) return {success: false, error: 'section_not_found'};
            var btns = target.querySelectorAll('button');
            if (btns.length >= 2) {
                btns[1].click();
                return {success: true};
            }
            return {success: false, error: 'button_not_found'};
        })()
        ''' % section_index

        for i in range(target_count):
            result = await tab.evaluate(js_click_once)
            result = util.parse_nodriver_result(result)
            if not (isinstance(result, dict) and result.get('success')):
                error_msg = result.get('error', 'unknown') if isinstance(result, dict) else 'no_result'
                debug.log(f"[FANSIGO] Failed to click + button: {error_msg}")
                return False
            if i < target_count - 1:
                await asyncio.sleep(0.2)

        debug.log(f"[FANSIGO] Set ticket quantity to {target_count} for section {section_index}")

        return True

    except Exception as e:
        debug.log(f"[FANSIGO] Error setting ticket quantity: {e}")
        return False

async def nodriver_fansigo_click_checkout(tab, config_dict) -> bool:
    """Click checkout/submit button on show page using JavaScript

    Args:
        tab: NoDriver tab
        config_dict: Configuration dictionary

    Returns:
        bool: True if checkout button clicked
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # Find and click checkout button via JavaScript
        result = await tab.evaluate(_fansigo_checkout_js())
        result = util.parse_nodriver_result(result)

        if isinstance(result, dict) and result.get('clicked'):
            debug.log(f"[FANSIGO] Clicked checkout button: {result.get('text', '')}")
            return True

        debug.log("[FANSIGO] Checkout button not found")
        return False

    except Exception as e:
        debug.log(f"[FANSIGO] Error clicking checkout: {e}")
        return False

async def _fansigo_can_reload_show_page(tab, debug) -> bool:
    """True when the show page is rendered and not counting down to a sale.

    The page refetches its sections by itself when a sale opens and warns
    against reloading during the countdown (shown 15 minutes before), so only
    a page waiting for returned tickets needs a reload. A missing heading also
    covers the spinner shown during that refetch.
    """
    try:
        page_state = await tab.evaluate(_fansigo_show_page_state_js())
    except Exception as exc:
        debug.log(f"[FANSIGO] Error reading show page state: {exc}")
        return False

    if not isinstance(page_state, dict):
        return False

    has_countdown = bool(page_state.get("hasCountdown"))
    if has_countdown and not _state.get("countdown_logged"):
        debug.log("[FANSIGO] Sale countdown shown, waiting for the page to update by itself")
    _state["countdown_logged"] = has_countdown

    return bool(page_state.get("hasHeading")) and page_state.get("sectionCount", 0) > 0 and not has_countdown


async def _fansigo_reload_show_page(tab, config_dict, debug):
    """Stage 3: wait and reload a show page that has no section to select."""
    if not config_dict.get("tixcraft", {}).get("auto_reload_coming_soon_page", False):
        return

    interval = util.get_reload_interval(config_dict)
    if not isinstance(interval, (int, float)) or interval <= 0:
        return

    if not await _fansigo_can_reload_show_page(tab, debug):
        return

    debug.log(f"[FANSIGO] No section to select, waiting {interval}s before reload...")
    if await sleep_with_pause_check(tab, interval, config_dict):
        return

    try:
        await tab.reload()
    except Exception as exc:
        debug.log(f"[FANSIGO] Error reloading show page: {exc}")


async def _fansigo_return_to_configured_page(tab, config_dict, debug):
    """Stage 3: go back to the configured event or show page from the homepage.

    The event page sends visitors to the homepage until it opens. The throttle
    reads the interval field directly because it is not a reload wait.
    """
    homepage = (config_dict.get("homepage") or "").strip()
    if get_fansigo_page_type(homepage) not in ("event", "show"):
        return

    redirect_interval = config_dict.get("advanced", {}).get(
        "auto_reload_page_interval", CONST_FANSIGO_MIN_REDIRECT_INTERVAL)
    if not isinstance(redirect_interval, (int, float)) or redirect_interval <= 0:
        redirect_interval = CONST_FANSIGO_MIN_REDIRECT_INTERVAL

    current_time = time.time()
    if current_time - _state.get("last_homepage_redirect_time", 0) <= redirect_interval:
        return

    _state["last_homepage_redirect_time"] = current_time
    debug.log(f"[FANSIGO] On homepage, returning to: {homepage}")
    try:
        await tab.get(homepage)
    except Exception as exc:
        debug.log(f"[FANSIGO] Error returning to configured page: {exc}")


async def nodriver_fansigo_main(tab, url, config_dict):
    """Main control function for FANSI GO platform

    Args:
        tab: NoDriver tab
        url: Current page URL
        config_dict: Configuration dictionary

    Returns:
        tab: Updated NoDriver tab
    """
    debug = util.create_debug_logger(config_dict)

    # Check pause state
    if await check_and_handle_pause(config_dict):
        return tab

    # Initialize state dictionary
    if not _state:
        _state.update({
            "is_cookie_injected": False,
            "is_signin_submitted": False,
            "played_sound_ticket": False,
            "last_page_type": None,
            "qty_set_url": None,
        })

    # Get page type
    page_type = get_fansigo_page_type(url)

    # Log page type change
    if page_type != _state.get("last_page_type"):
        debug.log(f"[FANSIGO] Page type: {page_type}")
        _state["last_page_type"] = page_type

    # Handle login page - try account login or cookie + reload
    if page_type == "login":
        # If cookie was already injected but we're back on login page, cookie may be expired
        if _state["is_cookie_injected"]:
            debug.log("[FANSIGO] Cookie was injected but login page detected, cookie may be expired")
            _state["is_cookie_injected"] = False
        # Reset signin flag so retry is possible if Cognito redirected back
        if _state.get("is_signin_submitted"):
            debug.log("[FANSIGO] Login page revisited, resetting signin flag for retry")
            _state["is_signin_submitted"] = False

        fansigo_account = config_dict.get("accounts", {}).get("fansigo_account", "").strip()
        fansigo_password = config_dict.get("accounts", {}).get("fansigo_password", "").strip()

        if fansigo_account and fansigo_password:
            if not _state.get("is_signin_submitted"):
                await nodriver_fansigo_signin(tab, url, config_dict)
                _state["is_signin_submitted"] = True
        elif not _state["is_cookie_injected"]:
            # Try cookie injection then reload
            injected = await nodriver_fansigo_inject_cookie(tab, config_dict)
            _state["is_cookie_injected"] = True
            if injected:
                debug.log("[FANSIGO] Cookie injected on login page, reloading")
                await tab.reload()
            else:
                debug.log("[FANSIGO] No credentials configured, please login manually")
        return tab

    # Inject cookie (once) for non-login pages
    if not _state["is_cookie_injected"]:
        _state["is_cookie_injected"] = await nodriver_fansigo_inject_cookie(tab, config_dict)
        if _state["is_cookie_injected"]:
            debug.log("[FANSIGO] Cookie injected on non-login page, reloading")
            await tab.reload()

    # Handle checkout page - stop automation
    if page_type == "checkout" or page_type == "order_result":
        if not _state["played_sound_ticket"]:
            debug.log("[FANSIGO] Checkout page reached, automation stopped")
            play_mp3 = config_dict.get("advanced", {}).get("play_ticket_sound", True)
            if play_mp3:
                play_sound_while_ordering(config_dict)
            _state["played_sound_ticket"] = True
        return tab

    # Handle homepage - return to the configured page
    if page_type == "home":
        await _fansigo_return_to_configured_page(tab, config_dict, debug)
        return tab

    # Handle event page - select show
    if page_type == "event":
        _state["qty_set_url"] = None
        await nodriver_fansigo_date_auto_select(tab, url, config_dict)
        return tab

    # Handle show page - select section, set quantity, checkout
    if page_type == "show":
        # If quantity already set for this URL, skip to checkout only
        if _state.get("qty_set_url") == url:
            await asyncio.sleep(0.3)
            await nodriver_fansigo_click_checkout(tab, config_dict)
            return tab

        # Select section (returns index, or -1 if failed)
        section_index = await nodriver_fansigo_area_auto_select(tab, url, config_dict)

        if section_index >= 0:
            # Set ticket quantity for the selected section
            await asyncio.sleep(0.3)
            qty_set = await nodriver_fansigo_assign_ticket_number(tab, config_dict, section_index)

            if qty_set:
                _state["qty_set_url"] = url
                # Click checkout
                await asyncio.sleep(0.3)
                await nodriver_fansigo_click_checkout(tab, config_dict)
        else:
            await _fansigo_reload_show_page(tab, config_dict, debug)

        return tab

    return tab
