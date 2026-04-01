#encoding=utf-8
# =============================================================================
# TixCraft + Ticketmaster Platform Module
# Extracted from nodriver_tixcraft.py during modularization (Phase 1)
# Contains: tixcraft.com, indievox.com, ticketmaster.* family
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

try:
    import ddddocr
except Exception:
    pass

from zendriver import cdp

import util
from nodriver_common import (
    check_and_handle_pause,
    convert_remote_object,
    nodriver_check_checkbox,
    nodriver_check_checkbox_enhanced,
    nodriver_current_url,
    nodriver_get_text_by_selector,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    write_question_to_file,
    CONST_MAXBOT_ANSWER_ONLINE_FILE,
    CONST_MAXBOT_INT28_FILE,
    CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS,
    CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER,
)

__all__ = [
    "nodriver_tixcraft_home_close_window",
    "nodriver_tixcraft_redirect",
    "nodriver_ticketmaster_parse_zone_info",
    "get_ticketmaster_target_area",
    "nodriver_ticketmaster_get_ticketPriceList",
    "nodriver_ticketmaster_date_auto_select",
    "nodriver_ticketmaster_area_auto_select",
    "nodriver_ticketmaster_assign_ticket_number",
    "nodriver_ticketmaster_captcha",
    "nodriver_ticketmaster_promo",
    "nodriver_tixcraft_verify",
    "nodriver_fill_verify_form",
    "nodriver_tixcraft_input_check_code",
    "nodriver_tixcraft_date_auto_select",
    "nodriver_tixcraft_area_auto_select",
    "nodriver_get_tixcraft_target_area",
    "nodriver_ticket_number_select_fill",
    "nodriver_tixcraft_assign_ticket_number",
    "nodriver_tixcraft_ticket_main_agree",
    "nodriver_tixcraft_ticket_main",
    "nodriver_tixcraft_keyin_captcha_code",
    "nodriver_tixcraft_toast",
    "nodriver_tixcraft_reload_captcha",
    "nodriver_tixcraft_get_ocr_answer",
    "nodriver_tixcraft_auto_ocr",
    "nodriver_tixcraft_ticket_main_ocr",
    "nodriver_tixcraft_main",
]

# Module-level state (replaces global tixcraft_dict)
_state = {}


async def nodriver_tixcraft_home_close_window(tab):
    if _state.get('cookie_accepted'):
        return
    try:
        accept_all_cookies_btn = await tab.query_selector('#onetrust-accept-btn-handler')
        if accept_all_cookies_btn:
            await accept_all_cookies_btn.click()
            _state['cookie_accepted'] = True
    except:
        pass

async def nodriver_tixcraft_redirect(tab, url):
    ret = False
    game_name = ""
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]
    if len(game_name) > 0:
        if "/activity/detail/%s" % (game_name,) in url:
            entry_url = url.replace("/activity/detail/","/activity/game/")
            print("redirec to new url:", entry_url)
            try:
                await tab.get(entry_url)
                # 等待日期列表出現，確保頁面載入完成
                try:
                    await tab.wait_for('#gameList > table > tbody > tr', timeout=5)
                except:
                    pass  # timeout 沒關係，讓後續邏輯處理
                ret = True
            except Exception as exec1:
                pass
    return ret

# ============================================
# Ticketmaster.com NoDriver Platform Migration
# ============================================
# Foundation Functions (T004-T007)
#

# T004: Parse zone_info JSON from #mapSelectArea
async def nodriver_ticketmaster_parse_zone_info(tab, config_dict):
    """
    Parse zone_info JavaScript variable from #mapSelectArea element.
    Returns: zone_info dict or None if parsing fails
    """
    debug = util.create_debug_logger(config_dict)

    zone_info = None

    # Try method 1: String extraction from HTML (preferred - avoids RemoteObject issues)
    try:
        mapSelectArea = await tab.query_selector('#mapSelectArea')
        if mapSelectArea:
            mapSelectArea_html = await mapSelectArea.get_attribute('innerHTML')

            tag_start = "var zone ="
            tag_end = "fieldImageType"
            if tag_start in mapSelectArea_html and tag_end in mapSelectArea_html:
                zone_string = mapSelectArea_html.split(tag_start)[1]
                zone_string = zone_string.split(tag_end)[0]
                zone_string = zone_string.strip().rstrip('\n,')

                import json
                zone_info = json.loads(zone_string)
                if debug.enabled:
                    debug.log(f"[TICKETMASTER ZONE] Parsed zone_info via string extraction ({len(zone_info)} zones)")
                    if len(zone_info) > 0:
                        sample_id = list(zone_info.keys())[0]
                        sample = zone_info[sample_id]
                        if isinstance(sample, dict) and "groupName" in sample:
                            debug.log(f"[TICKETMASTER ZONE] Sample zone '{sample_id}' groupName: {sample['groupName']}")
                return zone_info

    except Exception as exc:
        debug.log(f"[TICKETMASTER ZONE] String extraction failed: {exc}")

    # Try method 2: Direct JavaScript evaluation (fallback)
    try:
        result = await tab.evaluate('''
            (function() {
                // Check if zone variable exists in global scope
                if (typeof zone !== 'undefined') {
                    // IMPORTANT: Use JSON.parse(JSON.stringify()) to serialize RemoteObject to plain JSON
                    // Without this, NoDriver returns CDP RemoteObject format:
                    // {"type": "object", "value": [["key", {"type": "string", "value": "..."}]]}
                    // Instead of standard JSON: {"key": "value"}
                    try {
                        return JSON.parse(JSON.stringify(zone));
                    } catch(e) {
                        console.error('Zone serialization failed:', e);
                        return zone;  // Fallback to RemoteObject if serialization fails
                    }
                }

                // Fallback: Extract from #mapSelectArea innerHTML
                const el = document.querySelector('#mapSelectArea');
                if (!el) return null;

                const html = el.innerHTML;
                const match = html.match(/var zone = ({[\\s\\S]*?});/);
                if (!match) return null;

                try {
                    return JSON.parse(match[1]);
                } catch(e) {
                    console.error('JSON parse failed:', e);
                    return null;
                }
            })();
        ''')

        if result:
            # Convert RemoteObject to standard Python types
            zone_info = convert_remote_object(result)

            if debug.enabled:
                zone_type = "dict" if isinstance(zone_info, dict) else "list"
                debug.log(f"[TICKETMASTER ZONE] Successfully parsed zone_info ({len(zone_info)} zones, type: {zone_type})")
                debug.log(f"[TICKETMASTER ZONE] RemoteObject converted to standard format")

                # Print detailed structure for debugging
                if len(zone_info) > 0:
                    try:
                        # Print sample zone keys (BEFORE json.dumps to avoid serialization issues)
                        if isinstance(zone_info, list):
                            sample = zone_info[0]
                            sample_id = "index_0"

                            # Diagnostic for List format
                            debug.log(f"[TICKETMASTER ZONE] List first item type: {type(sample)}")

                            if isinstance(sample, dict):
                                sample_keys = list(sample.keys())[:10]  # First 10 keys
                                debug.log(f"[TICKETMASTER ZONE] List item keys (first 10): {sample_keys}")

                                # Check for zone_id fields
                                zone_id_field = None
                                for field in ["sectionCode", "id", "zoneId", "areaNo"]:
                                    if field in sample:
                                        zone_id_field = field
                                        debug.log(f"[TICKETMASTER ZONE] Found zone_id field: '{field}' = '{sample.get(field)}'")
                                        break

                                if not zone_id_field:
                                    debug.log(f"[TICKETMASTER ZONE] WARNING: No zone_id field found (sectionCode, id, zoneId, areaNo)")

                            elif isinstance(sample, (list, tuple)):
                                debug.log(f"[TICKETMASTER ZONE] List item is tuple/list with {len(sample)} elements")
                                if len(sample) > 0:
                                    debug.log(f"[TICKETMASTER ZONE] First element type: {type(sample[0])}")
                                    if isinstance(sample[0], str):
                                        debug.log(f"[TICKETMASTER ZONE] First element (zone_id): {sample[0]}")
                                if len(sample) > 1:
                                    debug.log(f"[TICKETMASTER ZONE] Second element type: {type(sample[1])}")
                                    zone_data = sample[1]
                                    if isinstance(zone_data, dict):
                                        # Check if conversion successful
                                        if "groupName" in zone_data:
                                            debug.log(f"[TICKETMASTER ZONE] [OK] groupName found: {zone_data.get('groupName')}")
                                        elif "type" in zone_data and "value" in zone_data:
                                            debug.log(f"[TICKETMASTER ZONE] [FAIL] Still RemoteObject format (has 'type' and 'value' keys)")
                                            # Try to convert again
                                            zone_data = convert_remote_object(zone_data)
                                            # Update in the list
                                            sample[1] = zone_data
                                            zone_info[0] = sample
                                            if "groupName" in zone_data:
                                                debug.log(f"[TICKETMASTER ZONE] [OK] After re-conversion, groupName found: {zone_data.get('groupName')}")
                                        else:
                                            debug.log(f"[TICKETMASTER ZONE] zone_data keys: {list(zone_data.keys())[:10]}")
                            else:
                                debug.log(f"[TICKETMASTER ZONE] WARNING: Unknown list item format")
                        else:
                            # Dict format
                            sample_id = list(zone_info.keys())[0]
                            sample = zone_info[sample_id]
                            debug.log(f"[TICKETMASTER ZONE] Sample zone_id: {sample_id}")

                        sample_keys = list(sample.keys()) if isinstance(sample, dict) else []
                        if sample_keys:
                            debug.log(f"[TICKETMASTER ZONE] Sample structure keys: {sample_keys[:10]}")  # First 10 keys
                    except Exception as diag_exc:
                        debug.log(f"[TICKETMASTER ZONE] Diagnostic logging failed: {diag_exc}")

    except Exception as exc:
        debug.log(f"[TICKETMASTER ZONE] JavaScript evaluation failed: {exc}")

    return zone_info

# T005: Get target area from zone_info (Pure function - no DOM access)
def get_ticketmaster_target_area(config_dict, area_keyword_item, zone_info):
    """
    Match areas from zone_info based on keyword.
    Returns: (is_need_refresh, matched_blocks)
    """
    debug = util.create_debug_logger(config_dict)

    area_auto_select_mode = config_dict.get("area_auto_select", {}).get("mode", "from top to bottom")

    is_need_refresh = False
    matched_blocks = []

    if not zone_info or len(zone_info) == 0:
        return True, None

    # Normalize zone_info to uniform iteration format
    # Dict format: {"zone_id": {...}} → [("zone_id", {...}), ...]
    # List format (3 types):
    #   Type A: [{"sectionCode": "field_C1_B", ...}, {...}] → extract sectionCode as zone_id
    #   Type B: [["field_C1_B", {...}], ...] → unpack tuple/list
    #   Type C: [(zone_id, {...}), ...] → already in correct format

    if isinstance(zone_info, dict):
        # Dict format: standard case
        zone_items = list(zone_info.items())
    elif isinstance(zone_info, list):
        # List format: need to detect which type
        if len(zone_info) == 0:
            zone_items = []
        else:
            first_item = zone_info[0]

            if isinstance(first_item, dict):
                # Type A: List of dicts - extract zone_id from dict
                zone_items = []
                for z in zone_info:
                    if not isinstance(z, dict):
                        continue
                    zone_id = z.get("sectionCode") or z.get("id") or z.get("zoneId") or z.get("areaNo")
                    zone_items.append((zone_id, z))

            elif isinstance(first_item, (list, tuple)) and len(first_item) >= 2:
                # Type B: List of [id, data] pairs
                zone_items = []
                for item in zone_info:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        zone_id = item[0]
                        zone_data = item[1]
                        # Convert RemoteObject if needed
                        if isinstance(zone_data, dict) and "type" in zone_data and "value" in zone_data:
                            zone_data = convert_remote_object(zone_data)
                        zone_items.append((zone_id, zone_data))

            else:
                # Unknown format - fallback to old logic
                debug.log(f"[TICKETMASTER AREA] Unknown zone_info list format, first item type: {type(first_item)}")
                zone_items = [(None, z) for z in zone_info]
    else:
        # Unexpected type
        debug.log(f"[TICKETMASTER AREA] Unexpected zone_info type: {type(zone_info)}")
        zone_items = []

    for zone_id, zone_data in zone_items:
        # Validate zone_data is dict-like (has .get() method)
        if not hasattr(zone_data, 'get'):
            debug.log(f"[TICKETMASTER AREA] zone_data is not dict-like: {type(zone_data)}, skipping")
            continue

        # Fallback: extract zone_id if still None
        if zone_id is None:
            zone_id = zone_data.get("sectionCode") or zone_data.get("id") or zone_data.get("zoneId") or zone_data.get("areaNo")

        row_is_enabled = zone_data.get("areaStatus") != "UNAVAILABLE"

        if not row_is_enabled:
            continue

        # Build row text from zone info
        row_text = ""
        group_name = ""
        description = ""
        try:
            group_name = zone_data.get("groupName", "")
            description = zone_data.get("description", "")
            row_text = group_name + " " + description
            if "price" in zone_data and len(zone_data["price"]) > 0:
                row_text += " " + zone_data["price"][0].get("ticketPrice", "")
        except:
            pass

        if debug.enabled:
            # Show human-readable zone info instead of just zone_id
            display_name = f"{group_name} {description}".strip() if group_name or description else zone_id
            debug.log(f"[TICKETMASTER AREA] Processing zone: {zone_id} ({display_name})")

        if not row_text.strip():
            continue

        # Check exclude keywords
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            continue

        # Format and match keywords
        row_text = util.format_keyword_string(row_text)

        is_append_this_row = False
        if area_keyword_item:
            # Must match all keywords (AND logic)
            area_keyword_array = area_keyword_item.split(' ')

            # Word boundary matching function
            import re
            def word_boundary_match(keyword, text):
                """
                Match keyword with word boundary awareness.
                - Single char keywords (like 'I') require word boundaries
                - Multi-char keywords use substring match for flexibility
                """
                formatted_kw = util.format_keyword_string(keyword)
                if len(formatted_kw) <= 2:
                    # Short keywords need word boundary to avoid false positives
                    # e.g., 'I' should not match 'CIRCLE'
                    pattern = r'\b' + re.escape(formatted_kw) + r'\b'
                    return bool(re.search(pattern, text, re.IGNORECASE))
                else:
                    # Longer keywords use substring match
                    return formatted_kw in text

            # Detailed AND logic matching with PASS/FAIL logs
            if debug.enabled:
                keyword_results = []
                for kw in area_keyword_array:
                    match_result = word_boundary_match(kw, row_text)
                    status = "PASS" if match_result else "FAIL"
                    keyword_results.append(f"'{kw}':{status}")

                all_matched = all(
                    word_boundary_match(kw, row_text)
                    for kw in area_keyword_array
                )
                overall_status = "MATCHED" if all_matched else "REJECTED"
                debug.log(f"[TICKETMASTER AREA] AND Match: {zone_id} [{', '.join(keyword_results)}] -> {overall_status}")

            is_append_this_row = all(
                word_boundary_match(kw, row_text)
                for kw in area_keyword_array
            )
        else:
            # No keyword = match all
            is_append_this_row = True

        if is_append_this_row:
            matched_blocks.append(zone_id)

            if area_auto_select_mode == "from top to bottom":
                # Only need first match
                break

    if len(matched_blocks) == 0:
        matched_blocks = None
        is_need_refresh = True

    if matched_blocks:
        debug.log(f"[TICKETMASTER AREA] Matched {len(matched_blocks)} areas: {matched_blocks}")

    return is_need_refresh, matched_blocks

# T006: Get ticket price list (wait for page load)
async def nodriver_ticketmaster_get_ticketPriceList(tab, config_dict):
    """
    Wait for ticketPriceList to load and return the table element.
    Uses official NoDriver API (stable, recommended approach).
    Returns: table element or None

    References:
    - Fixed based on famiticket_nodriver_fixes.md (Phase 4: NoDriver Official API Migration)
    - Issue: tab.evaluate() returns None due to JavaScript Context failure
    - Solution: Use tab.wait_for() and tab.query_selector() instead
    """
    debug = util.create_debug_logger(config_dict)

    try:
        # Phase 1: Wait for mapContainer (basic page load)
        await tab.wait_for(selector='#mapContainer', timeout=5)

        # Ensure DOM references are synchronized (official recommendation)
        await tab

        debug.log("[TICKETMASTER TICKET] mapContainer found")

        # Phase 2: Wait for loading to finish (check if loadingmap disappears)
        max_wait = 10  # 10 seconds max
        for i in range(max_wait):
            loading = await tab.query_selector('#loadingmap')
            if not loading:
                if i > 0:
                    debug.log(f"[TICKETMASTER TICKET] Loading finished after {i}s")
                break
            await tab.sleep(1)
        else:
            # Timeout after 10 seconds
            debug.log("[TICKETMASTER TICKET] Loading timeout after 10s")

        # Phase 3: Try to find ticketPriceList
        table_element = await tab.query_selector('#ticketPriceList')

        if table_element:
            debug.log("[TICKETMASTER TICKET] Found ticketPriceList table")
            return table_element
        else:
            debug.log("[TICKETMASTER TICKET] ticketPriceList not found, will use zone_info")
            return None

    except asyncio.TimeoutError:
        debug.log("[TICKETMASTER TICKET] Timeout waiting for mapContainer")
        return None
    except Exception as e:
        debug.log(f"[TICKETMASTER TICKET] Error: {e}")
        return None

# ============================================
# User Story 1: Date Auto Select (T009)
# ============================================

async def nodriver_ticketmaster_date_auto_select(tab, config_dict):
    """
    Automatically select event date on Ticketmaster artist page.
    Returns: True if date was clicked, False otherwise
    """
    debug = util.create_debug_logger(config_dict)

    # Read config
    auto_select_mode = config_dict.get("date_auto_select", {}).get("mode", "from top to bottom")
    date_keyword = config_dict.get("date_auto_select", {}).get("date_keyword", "").strip()
    pass_date_is_sold_out_enable = config_dict.get("tixcraft", {}).get("pass_date_is_sold_out", False)
    auto_reload_coming_soon_page_enable = config_dict.get("kktix", {}).get("auto_reload_coming_soon_page", False)

    sold_out_text_list = ["Sold out", "No tickets available"]
    find_ticket_text_list = ['Find tickets', 'See Tickets']

    # Query date list
    # Ticketmaster.sg uses a table structure: #gameList tbody tr
    # Wait for dynamic content to load (max 5 seconds)
    area_list = None
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            area_list = await tab.query_selector_all('#gameList tbody tr')
            if area_list and len(area_list) > 0:
                debug.log(f"[TICKETMASTER DATE] Found date list after {attempt * 0.5}s")
                break
            await asyncio.sleep(0.5)
        except Exception as exc:
            if attempt == 0:
                debug.log(f"[TICKETMASTER DATE] Waiting for date list to load... ({exc})")
            await asyncio.sleep(0.5)

    if not area_list:
        debug.log(f"[TICKETMASTER DATE] Failed to find date list after {max_attempts * 0.5}s")
        return False

    matched_blocks = None
    formated_area_list = []

    if not area_list or len(area_list) == 0:
        debug.log("[TICKETMASTER DATE] No dates found on page")
        return False

    debug.log(f"[TICKETMASTER DATE] Found {len(area_list)} date blocks")

    # Filter date blocks
    for row in area_list:
        try:
            row_html = await row.get_html()
            row_text = util.remove_html_tags(row_html)
        except:
            break

        if not row_text:
            continue

        row_is_enabled = False

        # Must contain "See Tickets"
        for text_item in find_ticket_text_list:
            if text_item in row_text:
                row_is_enabled = True
                break

        # Check sold out
        if row_is_enabled and pass_date_is_sold_out_enable:
            for sold_out_item in sold_out_text_list:
                if sold_out_item in row_text:
                    row_is_enabled = False
                    debug.log(f"[TICKETMASTER DATE] Skipping sold out event: {row_text[:60]}...")
                    break

        if row_is_enabled:
            formated_area_list.append(row)

    debug.log(f"[TICKETMASTER DATE] {len(formated_area_list)} available dates after filtering")

    # Get date_auto_fallback setting (default: False = strict mode)
    date_auto_fallback = config_dict.get('date_auto_fallback', False)

    # Build text list for keyword matching
    formated_area_list_text = []
    for row in formated_area_list:
        try:
            row_html = await row.get_html()
            row_text = util.remove_html_tags(row_html)
            formated_area_list_text.append(row_text)
        except:
            formated_area_list_text.append("")

    # T004-T008: Early return pattern (Feature 003)
    if not date_keyword:
        matched_blocks = formated_area_list
        debug.log(f"[TICKETMASTER DATE KEYWORD] No keyword specified, using all {len(formated_area_list)} dates")
    else:
        # Early return pattern - iterate keywords in priority order
        matched_blocks = []
        target_row_found = False
        keyword_matched_index = -1

        try:
            import json
            import re
            keyword_array = json.loads("[" + date_keyword + "]")

            # T005: Start checking keywords log
            debug.log(f"[TICKETMASTER DATE KEYWORD] Start checking keywords in order: {keyword_array}")
            debug.log(f"[TICKETMASTER DATE KEYWORD] Total keyword groups: {len(keyword_array)}")
            debug.log(f"[TICKETMASTER DATE KEYWORD] Checking against {len(formated_area_list_text)} available dates...")

            # Iterate keywords in priority order (early return)
            for keyword_index, keyword_item_set in enumerate(keyword_array):
                debug.log(f"[TICKETMASTER DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

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

                        # Detailed AND logic log
                        if debug.enabled:
                            result_strs = [f"'{kw}':{('PASS' if r else 'FAIL')}" for kw, r in zip(keyword_item_set, match_results)]
                            overall = "MATCHED" if is_match else "REJECTED"
                            debug.log(f"[TICKETMASTER DATE KEYWORD] AND Match: [{', '.join(result_strs)}] -> {overall}")

                    if is_match:
                        # T006: Keyword matched - IMMEDIATELY select and stop
                        matched_blocks = [formated_area_list[i]]
                        target_row_found = True
                        keyword_matched_index = keyword_index
                        debug.log(f"[TICKETMASTER DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                        debug.log(f"[TICKETMASTER DATE SELECT] Selected date: {row_text[:80]} (keyword match)")
                        break  # Early Return - stop checking other rows

                if target_row_found:
                    # EARLY RETURN: Stop checking further keywords
                    break

            # T007: All keywords failed log
            if not target_row_found:
                debug.log(f"[TICKETMASTER DATE KEYWORD] All keywords failed to match")

        except Exception as e:
            debug.log(f"[TICKETMASTER DATE KEYWORD] Parsing error: {e}")
            matched_blocks = []

    # Match result summary
    debug.log(f"[TICKETMASTER DATE KEYWORD] ========================================")
    debug.log(f"[TICKETMASTER DATE KEYWORD] Match Summary:")
    debug.log(f"[TICKETMASTER DATE KEYWORD]   Total dates available: {len(formated_area_list) if formated_area_list else 0}")
    debug.log(f"[TICKETMASTER DATE KEYWORD]   Total dates matched: {len(matched_blocks) if matched_blocks else 0}")
    debug.log(f"[TICKETMASTER DATE KEYWORD] ========================================")

    # T018-T020: Conditional fallback based on date_auto_fallback switch
    if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and formated_area_list is not None and len(formated_area_list) > 0:
        if date_auto_fallback:
            # T018: Fallback enabled - use auto_select_mode
            debug.log(f"[TICKETMASTER DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            debug.log(f"[TICKETMASTER DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
            matched_blocks = formated_area_list
        else:
            # T019: Fallback disabled - strict mode
            debug.log(f"[TICKETMASTER DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            debug.log(f"[TICKETMASTER DATE SELECT] No date selected, will reload page and retry")

    # Select target
    if formated_area_list is None or len(formated_area_list) == 0:
        target_area = None
    elif matched_blocks is None or len(matched_blocks) == 0:
        target_area = None
    else:
        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    is_date_clicked = False
    if target_area:
        try:
            # Click "See Tickets" link
            link_element = await target_area.query_selector('a')
            if link_element:
                await link_element.click()
                is_date_clicked = True
                debug.log("[TICKETMASTER DATE] Clicked 'See Tickets' link")

                # Handle new tab (close if opened)
                await tab.sleep(0.3)
                if len(tab.browser.tabs) > 1:
                    # Close extra tabs
                    for extra_tab in tab.browser.tabs[1:]:
                        await extra_tab.close()
                    await tab.sleep(0.2)

        except Exception as exc:
            debug.log(f"[TICKETMASTER DATE] Failed to click link: {exc}")

    # Auto reload if no match
    if auto_reload_coming_soon_page_enable and not is_date_clicked and len(formated_area_list) == 0:
        debug.log("[TICKETMASTER DATE] No dates available, reloading page...")
        try:
            await tab.reload()
            await tab.sleep(0.3)
        except:
            pass

    return is_date_clicked

# ============================================
# User Story 2: Area Auto Select (T012)
# ============================================

async def nodriver_ticketmaster_area_auto_select(tab, config_dict, zone_info):
    """
    Automatically select seat area on Ticketmaster ticket page.
    """
    debug = util.create_debug_logger(config_dict)

    area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "").strip()

    debug.log(f"[TICKETMASTER AREA] area_keyword: {area_keyword}")

    is_need_refresh = False
    matched_blocks = None

    # Get area_auto_fallback setting (default: False = strict mode)
    area_auto_fallback = config_dict.get("area_auto_fallback", False)

    if area_keyword:
        area_keyword_array = util.parse_keyword_string_to_array(area_keyword)

        debug.log(f"[TICKETMASTER AREA] Parsed keyword groups: {area_keyword_array}")

        # Early Return Pattern: Try each keyword group with priority
        for idx, area_keyword_item in enumerate(area_keyword_array):
            debug.log(f"[TICKETMASTER AREA] Trying keyword group {idx + 1}/{len(area_keyword_array)}: '{area_keyword_item}'")

            is_need_refresh, matched_blocks = get_ticketmaster_target_area(config_dict, area_keyword_item, zone_info)

            if not is_need_refresh and matched_blocks:
                # Found match - Early Return
                debug.log(f"[TICKETMASTER AREA] Early Return: keyword group {idx + 1} matched {len(matched_blocks)} area(s)")
                break
            else:
                debug.log(f"[TICKETMASTER AREA] Keyword group {idx + 1} had no matches, trying next...")

        # Conditional fallback: only match all if area_auto_fallback is enabled
        if is_need_refresh:
            if area_auto_fallback:
                debug.log("[TICKETMASTER AREA] Fallback enabled: selecting from all available areas")
                is_need_refresh, matched_blocks = get_ticketmaster_target_area(config_dict, "", zone_info)
            else:
                debug.log("[TICKETMASTER AREA] Strict mode: no keyword match, will refresh page")
                # Keep is_need_refresh = True, matched_blocks = None
    else:
        # Empty keyword = match all
        is_need_refresh, matched_blocks = get_ticketmaster_target_area(config_dict, "", zone_info)

    # Select target
    auto_select_mode = config_dict.get("area_auto_select", {}).get("mode", "from top to bottom")
    target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    if target_area:
        try:
            # Execute JavaScript to select area
            click_area_javascript = f'areaTicket("{target_area}", "map");'
            debug.log(f"[TICKETMASTER AREA] Executing: {click_area_javascript}")

            await tab.evaluate(click_area_javascript)

            # Wait for AJAX to load ticketPriceList (areaTicket executes AJAX request)
            max_wait = 5  # 5 seconds max
            for i in range(max_wait):
                await tab.sleep(1)

                # Check if ticketPriceList has loaded
                price_list = await tab.query_selector('#ticketPriceList')
                if price_list:
                    debug.log(f"[TICKETMASTER AREA] ticketPriceList loaded after {i+1}s")
                    break
            else:
                debug.log("[TICKETMASTER AREA] Timeout waiting for ticketPriceList (5s)")

            debug.log(f"[TICKETMASTER AREA] Selected zone: {target_area}")

        except Exception as exc:
            debug.log(f"[TICKETMASTER AREA] Failed to execute JavaScript: {exc}")

    # Auto refresh if needed (only when keyword is specified but no match)
    if is_need_refresh:
        # Check if area_keyword is empty (empty = should match all areas)
        area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "").strip()

        if area_keyword:
            # Keyword specified but no match → might need to wait for availability
            debug.log("[TICKETMASTER AREA] No areas matched keyword, reloading page...")
            try:
                if config_dict.get("advanced", {}).get("auto_reload_page_interval", 0) > 0:
                    await tab.sleep(config_dict["advanced"]["auto_reload_page_interval"])
                await tab.reload()
            except:
                pass
        else:
            # No keyword but no areas → likely a data parsing issue, don't reload
            debug.log("[TICKETMASTER AREA] No areas available (possible zone_info parsing issue)")
            # Let next function (assign_ticket_number) handle it

# ============================================
# User Story 3: Ticket Number Assignment (T015-T016)
# ============================================

async def nodriver_ticketmaster_assign_ticket_number(tab, config_dict):
    """
    Automatically set ticket number on Ticketmaster ticket page.
    """
    debug = util.create_debug_logger(config_dict)

    # Get ticket price list
    table_select = await nodriver_ticketmaster_get_ticketPriceList(tab, config_dict)

    if not table_select:
        # Fallback to zone_info parsing
        zone_info = await nodriver_ticketmaster_parse_zone_info(tab, config_dict)
        if zone_info:
            await nodriver_ticketmaster_area_auto_select(tab, config_dict, zone_info)
        return

    # Find select element
    select_element = None
    try:
        select_element = await table_select.query_selector('select')
    except Exception as exc:
        debug.log(f"[TICKETMASTER TICKET] Failed to find select: {exc}")
        return

    if not select_element:
        debug.log("[TICKETMASTER TICKET] No select element found")
        return

    # Update element to sync attributes
    try:
        await select_element.update()
    except:
        pass

    # Check if element is enabled (NoDriver uses .attrs dict)
    try:
        select_attrs = select_element.attrs or {}
        is_disabled = 'disabled' in select_attrs
        if is_disabled:
            debug.log("[TICKETMASTER TICKET] Select element is disabled")
            return
    except Exception as exc:
        debug.log(f"[TICKETMASTER TICKET] Failed to check disabled status: {exc}")
        # Assume enabled if check fails
        pass

    # Check current value (using .attrs dict)
    select_attrs = select_element.attrs or {}
    selector_id = select_attrs.get('id')
    current_value = None
    if selector_id:
        try:
            current_value = await tab.evaluate(f'''
                (function() {{
                    const selectEl = document.getElementById('{selector_id}');
                    if (selectEl && selectEl.selectedIndex >= 0) {{
                        return selectEl.options[selectEl.selectedIndex].text;
                    }}
                    return null;
                }})();
            ''')
            # Parse NoDriver RemoteObject format if needed
            if isinstance(current_value, list):
                current_value = util.parse_nodriver_result(current_value)
        except:
            pass

    if current_value and current_value != "0" and current_value.isnumeric():
        debug.log(f"[TICKETMASTER TICKET] Ticket number already set to: {current_value}")
        # Already set, click autoMode button
        try:
            auto_mode_button = await tab.query_selector('#autoMode')
            if auto_mode_button:
                await auto_mode_button.click()
                debug.log("[TICKETMASTER TICKET] Clicked #autoMode button")
        except:
            pass
        return

    # Set ticket number
    ticket_number = str(config_dict.get("ticket_number", 1))

    try:
        # Get select element ID for JavaScript manipulation
        select_attrs = select_element.attrs or {}
        selector_id = select_attrs.get('id')
        if not selector_id:
            debug.log("[TICKETMASTER TICKET] Select element has no id attribute")
            return

        # Use JavaScript to set select value (using element ID instead of passing Element object)
        result = await tab.evaluate(f'''
            (function(elementId, targetText) {{
                const selectEl = document.getElementById(elementId);
                if (!selectEl) {{
                    return {{ success: false, error: "Element not found" }};
                }}
                const options = selectEl.options;
                for (let i = 0; i < options.length; i++) {{
                    if (options[i].text === targetText) {{
                        selectEl.selectedIndex = i;
                        selectEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{ success: true, value: options[i].value }};
                    }}
                }}
                return {{ success: false, error: "Option not found" }};
            }})('{selector_id}', '{ticket_number}');
        ''')

        # Parse NoDriver RemoteObject format
        result = util.parse_nodriver_result(result)

        if result and result.get('success'):
            debug.log(f"[TICKETMASTER TICKET] Set ticket number to: {ticket_number}")

            # Click autoMode button
            await tab.sleep(0.1)
            try:
                auto_mode_button = await tab.query_selector('#autoMode')
                if auto_mode_button:
                    await auto_mode_button.click()
                    debug.log("[TICKETMASTER TICKET] Clicked #autoMode button")
            except:
                pass
        else:
            debug.log(f"[TICKETMASTER TICKET] Failed to set ticket number: {result.get('error')}")

    except Exception as exc:
        debug.log(f"[TICKETMASTER TICKET] Exception setting ticket number: {exc}")

# ============================================
# User Story 4: Captcha Handling (T019)
# ============================================

async def nodriver_ticketmaster_captcha(tab, config_dict, ocr, captcha_browser):
    """
    Handle captcha on Ticketmaster check-captcha page.
    Returns: True if captcha was handled, False otherwise
    """
    debug = util.create_debug_logger(config_dict)

    # Check for custom OCR model path
    ocr_path = config_dict.get("ocr_captcha", {}).get("path", "")
    if ocr_path:
        # Support relative paths (relative to app root)
        if not os.path.isabs(ocr_path):
            app_root = util.get_app_root()
            ocr_path = os.path.join(app_root, ocr_path)

        custom_onnx = os.path.join(ocr_path, "custom.onnx")
        custom_charsets = os.path.join(ocr_path, "charsets.json")

        if os.path.exists(custom_onnx) and os.path.exists(custom_charsets):
            # Load custom OCR model
            try:
                ocr = ddddocr.DdddOcr(
                    det=False,
                    ocr=False,
                    import_onnx_path=custom_onnx,
                    charsets_path=custom_charsets,
                    show_ad=False
                )
                debug.log(f"[TICKETMASTER CAPTCHA] Using custom OCR model from: {ocr_path}")
            except Exception as e:
                debug.log(f"[TICKETMASTER CAPTCHA] Failed to load custom model: {e}, using default")
        else:
            # Always warn if custom model path is set but files not found
            debug.log(f"[TICKETMASTER CAPTCHA] Warning: Custom model files not found in: {ocr_path}")
            debug.log(f"[TICKETMASTER CAPTCHA] Expected: {custom_onnx} and {custom_charsets}")

    # Check agree checkbox
    for _ in range(2):
        is_checked = await nodriver_check_checkbox(tab, '#TicketForm_agree')
        if is_checked:
            debug.log("[TICKETMASTER CAPTCHA] Checked TicketForm_agree")
            break

    # Alert state tracked by event handler
    alert_state = {"detected": False, "message": ""}

    async def on_captcha_alert(event: cdp.page.JavascriptDialogOpening):
        alert_state["detected"] = True
        alert_state["message"] = event.message
        debug.log(f"[TICKETMASTER CAPTCHA] Alert event: '{event.message[:60]}'")
        # Dismiss the alert immediately to prevent blocking
        try:
            await tab.send(cdp.page.handle_java_script_dialog(accept=True))
            debug.log("[TICKETMASTER CAPTCHA] Alert auto-dismissed by handler")
        except:
            pass

    # Register handler for this captcha session
    tab.add_handler(cdp.page.JavascriptDialogOpening, on_captcha_alert)

    # Handle captcha
    if not config_dict.get("ocr_captcha", {}).get("enable", False):
        # OCR disabled - manual input
        await nodriver_tixcraft_keyin_captcha_code(tab, answer="", auto_submit=False, config_dict=config_dict)
        return False
    else:
        # OCR enabled - auto recognition
        previous_answer = None
        current_url = tab.target.url
        fail_count = 0
        total_fail_count = 0

        await asyncio.sleep(random.uniform(0.5, 1.0))

        for redo_ocr in range(99):
            try:
                alert_state["detected"] = False  # Reset before each attempt

                away_from_keyboard_enable = config_dict.get("ocr_captcha", {}).get("force_submit", False)
                ocr_captcha_image_source = config_dict.get("ocr_captcha", {}).get("image_source", "canvas")
                domain_name = tab.target.url.split('/')[2]

                # Call tixcraft_auto_ocr for captcha recognition
                is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_tixcraft_auto_ocr(
                    tab, config_dict, ocr, away_from_keyboard_enable, previous_answer,
                    captcha_browser, ocr_captcha_image_source, domain_name
                )

                if is_form_submitted:
                    debug.log("[TICKETMASTER CAPTCHA] Form submitted")

                    # Poll for alert event (max 2 seconds)
                    for wait_i in range(10):
                        await asyncio.sleep(0.2)
                        if alert_state["detected"]:
                            break

                    debug.log(f"[TICKETMASTER CAPTCHA] alert_state={alert_state}")

                    error_detected = alert_state["detected"]

                    # If alert was detected (already dismissed by handler), retry OCR
                    if error_detected:
                        debug.log("[TICKETMASTER CAPTCHA] Captcha error detected, retrying...")

                        await asyncio.sleep(0.3)
                        await nodriver_tixcraft_reload_captcha(tab, domain_name)
                        previous_answer = None
                        fail_count = 0
                        total_fail_count += 1

                        if total_fail_count >= 15:
                            print("[TICKETMASTER CAPTCHA] Failed 15 times. Manual input required.")
                            await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                            break

                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        continue

                    # Check for Ticketmaster custom error modal (not native alert)
                    # The modal shows "The verification code that you entered is incorrect"
                    try:
                        # Check for modal overlay or dialog
                        modal_result = await tab.evaluate('''
                            (function() {
                                // Check for visible modal or alert dialog
                                const modals = document.querySelectorAll('.modal, .alert, [role="dialog"], [role="alertdialog"]');
                                for (const modal of modals) {
                                    if (modal.offsetParent !== null || getComputedStyle(modal).display !== 'none') {
                                        return {
                                            found: true,
                                            text: modal.innerText || modal.textContent
                                        };
                                    }
                                }
                                // Also check for any visible buttons that might be confirm/OK
                                const buttons = document.querySelectorAll('button');
                                for (const btn of buttons) {
                                    const text = btn.innerText || btn.textContent;
                                    if ((text.includes('確定') || text.includes('OK') || text.includes('Try again')) &&
                                        btn.offsetParent !== null) {
                                        return {
                                            found: true,
                                            buttonSelector: 'button'
                                        };
                                    }
                                }
                                return { found: false };
                            })();
                        ''')

                        # Handle CDP RemoteObject format (may return as list or dict)
                        modal_content = None
                        if modal_result:
                            if isinstance(modal_result, dict):
                                modal_content = modal_result
                            elif isinstance(modal_result, list) and len(modal_result) > 0:
                                # CDP sometimes returns [{'type': 'object', 'value': {...}}]
                                first_item = modal_result[0]
                                if isinstance(first_item, dict):
                                    if 'value' in first_item:
                                        modal_content = first_item.get('value', {})
                                    else:
                                        modal_content = first_item

                        if modal_content and isinstance(modal_content, dict) and modal_content.get('found'):
                            error_detected = True
                            debug.log(f"[TICKETMASTER CAPTCHA] Error modal detected")

                            # Try to click confirm/OK button to dismiss modal
                            dismiss_result = await tab.evaluate('''
                                (function() {
                                    // Find and click confirm button
                                    const buttons = document.querySelectorAll('button');
                                    for (const btn of buttons) {
                                        const text = btn.innerText || btn.textContent;
                                        if (text.includes('確定') || text.includes('OK') || text.includes('Try again')) {
                                            btn.click();
                                            return true;
                                        }
                                    }
                                    // Try to find any primary button
                                    const primaryBtn = document.querySelector('.btn-primary, [type="button"]');
                                    if (primaryBtn) {
                                        primaryBtn.click();
                                        return true;
                                    }
                                    return false;
                                })();
                            ''')

                            # Handle CDP RemoteObject format
                            dismiss_success = False
                            if dismiss_result is True:
                                dismiss_success = True
                            elif isinstance(dismiss_result, list) and len(dismiss_result) > 0:
                                dismiss_success = dismiss_result[0] is True or dismiss_result[0] == True

                            if debug.enabled:
                                if dismiss_success:
                                    debug.log("[TICKETMASTER CAPTCHA] Error modal dismissed, will retry OCR")
                                else:
                                    debug.log("[TICKETMASTER CAPTCHA] Could not dismiss modal")

                            # Reset state for retry
                            await asyncio.sleep(0.3)

                            # Reload captcha for new image
                            await nodriver_tixcraft_reload_captcha(tab, domain_name)
                            previous_answer = None
                            fail_count = 0
                            total_fail_count += 1

                            # Check retry limit
                            if total_fail_count >= 15:
                                print("[TICKETMASTER CAPTCHA] OCR failed 15 times after error modal. Please enter captcha manually.")
                                await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                                break

                            await asyncio.sleep(random.uniform(0.5, 1.0))
                            continue  # Retry OCR

                    except Exception as modal_exc:
                        debug.log(f"[TICKETMASTER CAPTCHA] Error checking modal: {modal_exc}")

                    # No error modal detected, form submitted successfully
                    if not error_detected:
                        break

                if not away_from_keyboard_enable:
                    break

                if not is_need_redo_ocr:
                    break

                # Track failures and handle retry limits
                fail_count += 1
                total_fail_count += 1

                debug.log(f"[TICKETMASTER CAPTCHA] Fail count: {fail_count}, Total fails: {total_fail_count}")

                # Check if total failures reached 15, switch to manual input mode
                if total_fail_count >= 15:
                    print("[TICKETMASTER CAPTCHA] OCR failed 15 times. Please enter captcha manually.")
                    await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                    break

                # Refresh captcha after 3 consecutive failures with same answer
                if fail_count >= 3:
                    debug.log("[TICKETMASTER CAPTCHA] 3 consecutive failures, reloading captcha...")
                    await nodriver_tixcraft_reload_captcha(tab, domain_name)
                    fail_count = 0
                    previous_answer = None  # Reset to allow fresh OCR
                    await asyncio.sleep(random.uniform(0.8, 1.2))  # Wait for new captcha to load
                else:
                    # Wait between retries to allow canvas to fully load
                    await asyncio.sleep(random.uniform(0.3, 0.5))

                # Check if URL changed
                new_url = tab.target.url
                if new_url != current_url:
                    debug.log("[TICKETMASTER CAPTCHA] URL changed, stopping OCR loop")
                    break

            except Exception as exc:
                debug.log(f"[TICKETMASTER CAPTCHA] OCR error: {exc}")
                break

        return True

async def nodriver_ticketmaster_promo(tab, config_dict, fail_list):
    question_selector = '#promoBox'
    return await nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector)

async def nodriver_tixcraft_verify(tab, config_dict, fail_list):
    question_selector = '.zone-verify'
    return await nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector)

async def nodriver_fill_verify_form(tab, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval):
    """
    NoDriver version of fill_common_verify_form for TixCraft verification.

    Fills verification form input and submits the answer.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        inferred_answer_string: Answer to fill in
        fail_list: List of failed answers
        input_text_css: CSS selector for input field
        next_step_button_css: CSS selector for submit button (optional)
        submit_by_enter: Whether to submit by pressing Enter
        check_input_interval: Interval to wait when no answer

    Returns:
        tuple[bool, list]: (is_answer_sent, updated fail_list)
    """
    debug = util.create_debug_logger(config_dict)

    is_answer_sent = False

    try:
        # Check if input field exists and get current value
        input_info = await tab.evaluate(f'''
            (function() {{
                var input = document.querySelector("{input_text_css}");
                if (input) {{
                    return {{
                        exists: true,
                        value: input.value || ""
                    }};
                }}
                return {{ exists: false, value: "" }};
            }})()
        ''')
        input_info = util.parse_nodriver_result(input_info)

        if not input_info or not input_info.get('exists', False):
            debug.log("[VERIFY FORM] Input field not found:", input_text_css)
            return is_answer_sent, fail_list

        inputed_value = input_info.get('value', '')

        debug.log(f"[VERIFY FORM] Current input value: '{inputed_value}'")
        debug.log(f"[VERIFY FORM] Answer to fill: '{inferred_answer_string}'")

        if len(inferred_answer_string) > 0:
            # Fill the answer if different from current value
            if inputed_value != inferred_answer_string:
                # Clear and fill using JavaScript
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{input_text_css}");
                        if (input) {{
                            input.value = "";
                            input.value = "{inferred_answer_string}";
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()
                ''')

                debug.log(f"[VERIFY FORM] Filled answer: {inferred_answer_string}")

            # Submit the form
            is_button_clicked = False

            if submit_by_enter:
                # Submit by pressing Enter
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{input_text_css}");
                        if (input) {{
                            var event = new KeyboardEvent('keydown', {{
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            }});
                            input.dispatchEvent(event);

                            // Also try form submit
                            var form = input.closest('form');
                            if (form) {{
                                form.submit();
                            }}
                        }}
                    }})()
                ''')
                is_button_clicked = True
                debug.log("[VERIFY FORM] Submitted by Enter key")
            elif len(next_step_button_css) > 0:
                # Click the submit button
                try:
                    btn = await tab.query_selector(next_step_button_css)
                    if btn:
                        await btn.click()
                        is_button_clicked = True
                        debug.log(f"[VERIFY FORM] Clicked submit button: {next_step_button_css}")
                except Exception as btn_exc:
                    debug.log(f"[VERIFY FORM] Failed to click button: {btn_exc}")

            if is_button_clicked:
                is_answer_sent = True
                fail_list.append(inferred_answer_string)
                debug.log(f"[VERIFY FORM] Answer sent, attempt #{len(fail_list)}")

                # Wait and check for alert
                await asyncio.sleep(0.3)
        else:
            # No answer to fill, just focus the input
            if len(inputed_value) == 0:
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{input_text_css}");
                        if (input && document.activeElement !== input) {{
                            input.focus();
                        }}
                    }})()
                ''')
                await asyncio.sleep(check_input_interval)
                debug.log("[VERIFY FORM] No answer, focused input field")

    except Exception as exc:
        debug.log(f"[VERIFY FORM] Error: {exc}")

    return is_answer_sent, fail_list

async def nodriver_tixcraft_input_check_code(tab, config_dict, fail_list, question_selector):
    debug = util.create_debug_logger(config_dict)

    answer_list = []

    question_text = await nodriver_get_text_by_selector(tab, question_selector, 'innerText')
    if len(question_text) > 0:
        write_question_to_file(question_text)

        answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)
        if len(answer_list)==0:
            if config_dict["advanced"]["auto_guess_options"]:
                # Note: guess_tixcraft_question() doesn't use the driver parameter
                answer_list = util.guess_tixcraft_question(None, question_text, config_dict)

        inferred_answer_string = ""
        for answer_item in answer_list:
            if not answer_item in fail_list:
                inferred_answer_string = answer_item
                break

        debug.log("inferred_answer_string:", inferred_answer_string)
        debug.log("answer_list:", answer_list)

        # PS: auto-focus() when empty inferred_answer_string with empty inputed text value.
        input_text_css = "input[name='checkCode']"
        next_step_button_css = "button.btn.btn-primary"
        submit_by_enter = False
        check_input_interval = 0.2
        is_answer_sent, fail_list = await nodriver_fill_verify_form(tab, config_dict, inferred_answer_string, fail_list, input_text_css, next_step_button_css, submit_by_enter, check_input_interval)

    return fail_list

async def nodriver_tixcraft_date_auto_select(tab, url, config_dict, domain_name):
    debug = util.create_debug_logger(config_dict)

    # Issue #188: Check sold out cooldown before proceeding
    if _state and _state.get("sold_out_cooldown_until", 0) > time.time():
        remaining = _state["sold_out_cooldown_until"] - time.time()
        debug.log(f"[DATE SELECT] Sold out cooldown active, waiting {remaining:.1f}s...")
        await asyncio.sleep(remaining)
        _state["sold_out_cooldown_until"] = 0  # Reset after waiting

    # T003: Check main switch (defensive programming)
    if not config_dict["date_auto_select"]["enable"]:
        debug.log("[DATE SELECT] Main switch is disabled, skipping date selection")
        return False

    # read config
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)  # T017: Safe access for new field (default: strict mode)
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    find_ticket_text_list = ['立即訂購','Find tickets', 'Start ordering','お申込みへ進む']

    game_name = ""
    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    check_game_detail = "/activity/game/%s" % (game_name,) in url

    area_list = None
    if check_game_detail:
        # 智慧等待：等待日期列表出現
        # 注意：從 /activity/detail/ redirect 過來時，redirect 函數已經等待過了
        # 這裡再等待一次是為了處理直接進入 /activity/game/ 頁面的情況
        try:
            await tab.wait_for('#gameList > table > tbody > tr', timeout=3)
        except:
            pass  # timeout 沒關係，繼續嘗試讀取

        try:
            area_list = await tab.query_selector_all('#gameList > table > tbody > tr')
        except:
            pass

    # Language detection for coming soon
    is_coming_soon = False
    coming_soon_conditions = {
        'en-US': [' day(s)', ' hrs.',' min',' sec',' till sale starts!','0',':','/'],
        'zh-TW': ['開賣','剩餘',' 天',' 小時',' 分鐘',' 秒','0',':','/','20'],
        'ja': ['発売開始', ' 日', ' 時間',' 分',' 秒','0',':','/','20']
    }

    if 'html_lang' not in _state:
        try:
            _state['html_lang'] = await tab.evaluate('document.documentElement.lang') or 'en-US'
        except:
            _state['html_lang'] = 'en-US'
    html_lang = _state['html_lang']

    coming_soon_condictions_list = coming_soon_conditions.get(html_lang, coming_soon_conditions['en-US'])

    matched_blocks = None
    formated_area_list = None

    if area_list and len(area_list) > 0:
        formated_area_list = []
        formated_area_list_text = []
        # Batch fetch all row HTML in one CDP round-trip (~9-16x faster than sequential get_html())
        all_row_htmls = None
        try:
            all_row_htmls = await tab.evaluate(
                "Array.from(document.querySelectorAll('#gameList > table > tbody > tr')).map(r => r.outerHTML)"
            )
        except:
            pass
        for i, row in enumerate(area_list):
            try:
                if all_row_htmls and i < len(all_row_htmls):
                    row_html = all_row_htmls[i]
                else:
                    row_html = await row.get_html()
                row_text = util.remove_html_tags(row_html)
            except:
                break

            if row_text and not util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                # Check coming soon
                if all(cond in row_text for cond in coming_soon_condictions_list):
                    is_coming_soon = True
                    debug.log(f"[DATE SELECT] Detected coming soon countdown")
                    if auto_reload_coming_soon_page_enable:
                        debug.log(f"[DATE SELECT] auto_reload_coming_soon_page=true, will reload and retry")
                        break
                    else:
                        # Skip this row (don't add to formated_area_list)
                        continue

                # Check if row has ticket text
                row_is_enabled = any(text in row_text for text in find_ticket_text_list)

                # Check sold out
                if row_is_enabled and pass_date_is_sold_out_enable:
                    for sold_out_item in sold_out_text_list:
                        if sold_out_item in row_text[-(len(sold_out_item)+5):]:
                            row_is_enabled = False
                            # 移除：售完訊息過度詳細
                            break

                if row_is_enabled:
                    formated_area_list.append(row)
                    formated_area_list_text.append(row_text)
                    # 移除：可用場次訊息過度詳細

        # T004-T008: NEW LOGIC - Early return pattern (Feature 003)
        # Keyword priority matching: first match wins and stops immediately
        if not date_keyword:
            matched_blocks = formated_area_list
            debug.log(f"[DATE KEYWORD] No keyword specified, using all {len(formated_area_list)} dates")
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
                debug.log(f"[DATE KEYWORD] Start checking keywords in order: {keyword_array}")
                debug.log(f"[DATE KEYWORD] Total keyword groups: {len(keyword_array)}")
                debug.log(f"[DATE KEYWORD] Checking against {len(formated_area_list_text)} available dates...")

                # NEW: Iterate keywords in priority order (early return)
                for keyword_index, keyword_item_set in enumerate(keyword_array):
                    debug.log(f"[DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item_set}")

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
                            # T006: Keyword matched log - IMMEDIATELY select and stop
                            matched_blocks = [formated_area_list[i]]
                            target_row_found = True
                            keyword_matched_index = keyword_index
                            debug.log(f"[DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item_set}'")
                            debug.log(f"[DATE SELECT] Selected date: {row_text[:80]} (keyword match)")
                            break

                    if target_row_found:
                        # EARLY RETURN: Stop checking further keywords
                        break

                # T007: All keywords failed log
                if not target_row_found:
                    debug.log(f"[DATE KEYWORD] All keywords failed to match")

            except Exception as e:
                debug.log(f"[DATE KEYWORD] Parsing error: {e}")
                # On error, use mode selection
                matched_blocks = []

    # T018-T020: NEW - Conditional fallback based on date_auto_fallback switch
    if matched_blocks is not None and len(matched_blocks) == 0 and date_keyword and formated_area_list is not None and len(formated_area_list) > 0:
        if date_auto_fallback:
            # T018: Fallback enabled - use auto_select_mode
            debug.log(f"[DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            debug.log(f"[DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
            matched_blocks = formated_area_list
        else:
            # T019: Fallback disabled - strict mode (no selection, but still reload)
            debug.log(f"[DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            debug.log(f"[DATE SELECT] No date selected, will reload page and retry")
            # Don't return - let reload logic execute below
            # matched_blocks remains None (no selection will be made)

    # T020: Handle case when formated_area_list is empty or None (all options excluded or sold out)
    if formated_area_list is None or len(formated_area_list) == 0:
        debug.log(f"[DATE FALLBACK] No available options after exclusion")
        debug.log(f"[DATE SELECT] Will reload page and retry")
        # Don't return - let reload logic execute at function end
        is_date_clicked = False
        target_area = None  # Skip selection when no options available
    elif matched_blocks is None or len(matched_blocks) == 0:
        # matched_blocks is None when fallback=false and keyword didn't match
        target_area = None
        is_date_clicked = False
    else:
        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)

    if debug.enabled:
        if target_area and matched_blocks:
            # Find which index was selected
            try:
                target_index = matched_blocks.index(target_area) if target_area in matched_blocks else -1
                debug.log(f"[DATE SELECT] Auto-select mode: {auto_select_mode}")
                debug.log(f"[DATE SELECT] Selected target: #{target_index + 1}/{len(matched_blocks)}")
            except:
                debug.log(f"[DATE SELECT] Auto-select mode: {auto_select_mode}")
                debug.log(f"[DATE SELECT] Target selected from {len(matched_blocks)} matched dates")
        elif not matched_blocks or len(matched_blocks) == 0:
            debug.log(f"[DATE SELECT] No target selected (matched_blocks is empty)")

    is_date_clicked = False

    # 移除：內部選擇細節過度詳細

    if target_area:
        # Priority: button with data-href (tixcraft/indievox) > regular link > regular button
        # IMPORTANT: Search within target_area, not the whole page
        click_method_used = None
        try:
            debug.log("[DATE SELECT] Trying button[data-href] method within target_area...")

            # Method 1: button[data-href] within target_area (tixcraft/indievox specific)
            # 使用 NoDriver Element API 取得 data-href
            button_with_href = await target_area.query_selector('button[data-href]')
            data_href = None
            if button_with_href:
                # 更新元素以確保屬性載入
                await button_with_href.update()
                button_attrs = button_with_href.attrs or {}
                data_href = button_attrs.get('data-href')

                if debug.enabled:
                    if data_href:
                        debug.log(f"[DATE SELECT] button[data-href] found in target_area: {data_href}")
                    else:
                        debug.log("[DATE SELECT] button[data-href] found but no href value")

                if data_href:
                    debug.log("[DATE SELECT] Navigating via button[data-href]...")
                    await tab.get(data_href)
                    is_date_clicked = True
                    click_method_used = "button[data-href]"
                    debug.log("[DATE SELECT] Successfully navigated via button[data-href]")
            else:
                debug.log("[DATE SELECT] No button[data-href] in target_area, will try fallback methods")
        except Exception as e:
            debug.log(f"[DATE SELECT] button[data-href] method failed: {e}")

        # Method 2: regular link or button click
        if not is_date_clicked:
            try:
                debug.log("[DATE SELECT] Trying link <a[href]> method within target_area...")

                # Try link first (ticketmaster, etc)
                link = await target_area.query_selector('a[href]')
                if link:
                    debug.log("[DATE SELECT] Link found in target_area, clicking...")
                    await link.click()
                    is_date_clicked = True
                    click_method_used = "link <a[href]>"
                    debug.log("[DATE SELECT] Successfully clicked via link")
                else:
                    debug.log("[DATE SELECT] No link found, trying regular button within target_area...")

                    # Try regular button
                    button = await target_area.query_selector('button')
                    if button:
                        debug.log("[DATE SELECT] Regular button found in target_area, clicking...")
                        await button.click()
                        is_date_clicked = True
                        click_method_used = "regular button"
                        debug.log("[DATE SELECT] Successfully clicked via regular button")
                    else:
                        debug.log("[DATE SELECT] No clickable element found in target_area")
            except Exception as e:
                debug.log(f"[DATE SELECT] Click error: {e}")

        # Final summary
        if debug.enabled:
            if is_date_clicked and click_method_used:
                debug.log(f"[DATE SELECT] ========================================")
                debug.log(f"[DATE SELECT] Date selection completed successfully")
                debug.log(f"[DATE SELECT] Method used: {click_method_used}")
                debug.log(f"[DATE SELECT] ========================================")
            elif not is_date_clicked:
                debug.log(f"[DATE SELECT] ========================================")
                debug.log("[DATE SELECT] All click methods failed")
                debug.log(f"[DATE SELECT] ========================================")

    # Auto refresh if no date was selected (for strict mode or sold out scenarios)
    if not is_date_clicked:
        # Simple wait mode (consistent with TicketPlus/iBon/FamiTicket)
        interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
        if interval > 0:
            debug.log(f"[DATE SELECT] Waiting {interval}s before reload...")
            await asyncio.sleep(interval)

        debug.log(f"[DATE SELECT] No date selected, reloading page...")
        try:
            await tab.reload()
        except Exception:
            pass

    return is_date_clicked

async def nodriver_tixcraft_area_auto_select(tab, url, config_dict):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    # T010: Check main switch (defensive programming)
    if not config_dict["area_auto_select"]["enable"]:
        debug.log("[AREA SELECT] Main switch is disabled, skipping area selection")
        return False

    import json

    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get('area_auto_fallback', False)  # T021: Safe access for new field

    try:
        el = await tab.query_selector('.zone')
    except:
        return

    if not el:
        return

    is_need_refresh = False
    matched_blocks = None

    if area_keyword:
        # Parse keywords using JSON to avoid splitting keywords containing commas (e.g., "5,600")
        # Format: "\"keyword1\",\"keyword2\"" → ['keyword1', 'keyword2']
        # Supports OR logic - iterates through keywords until match found
        area_keyword_array = util.parse_keyword_string_to_array(area_keyword)

        # T012: Start checking keywords log
        debug.log(f"[AREA KEYWORD] Start checking keywords in order: {area_keyword_array}")
        debug.log(f"[AREA KEYWORD] Total keyword groups: {len(area_keyword_array)}")

        # T011: Early return pattern - iterate keywords in priority order
        keyword_matched = False
        for keyword_index, area_keyword_item in enumerate(area_keyword_array):
            debug.log(f"[AREA KEYWORD] Checking keyword #{keyword_index + 1}: {area_keyword_item}")

            is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, area_keyword_item)

            if not is_need_refresh:
                # T013: Keyword matched log
                keyword_matched = True
                debug.log(f"[AREA KEYWORD] Keyword #{keyword_index + 1} matched: '{area_keyword_item}'")
                break

        # T014: All keywords failed log
        if not keyword_matched:
            debug.log(f"[AREA KEYWORD] All keywords failed to match")

        # T022-T024: NEW - Conditional fallback based on area_auto_fallback switch
        is_fallback_selection = False  # Track selection type for logging
        if is_need_refresh and matched_blocks is None:
            if area_auto_fallback:
                # T022: Fallback enabled - use auto_select_mode without keyword
                debug.log(f"[AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
                debug.log(f"[AREA FALLBACK] Selecting available area based on area_select_order='{auto_select_mode}'")
                is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, "")
                is_fallback_selection = True  # Mark as fallback selection
            else:
                # T023: Fallback disabled - strict mode (no selection, but still reload)
                debug.log(f"[AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
                debug.log(f"[AREA SELECT] No area selected, will reload page and retry")
                # Don't return - let reload logic execute below
                # matched_blocks remains None (no selection will be made)
                # is_need_refresh remains True (will trigger reload)
    else:
        is_need_refresh, matched_blocks = await nodriver_get_tixcraft_target_area(el, config_dict, "")
        # No keyword specified, treat as mode-based selection (similar to fallback)
        if not area_keyword:
            is_fallback_selection = True

    # T024: Handle case when matched_blocks is empty or None (all options excluded or sold out)
    if matched_blocks is None or len(matched_blocks) == 0:
        debug.log(f"[AREA FALLBACK] No available options after exclusion")
        debug.log(f"[AREA SELECT] Will reload page and retry")
        # Don't return - let reload logic execute below
        is_need_refresh = True  # Ensure reload will happen
        target_area = None  # Skip selection when no options available
    else:
        target_area = util.get_target_item_from_matched_list(matched_blocks, auto_select_mode)
    if target_area:
        # T013: Log selected area with selection type
        if debug.enabled:
            try:
                area_text = await target_area.text
                if not area_text:
                    area_text = await target_area.inner_text
                area_text = area_text.strip()[:80] if area_text else "Unknown"
                selection_type = "fallback" if is_fallback_selection else "keyword match"
                debug.log(f"[AREA SELECT] Selected area: {area_text} ({selection_type})")
            except:
                pass  # If text extraction fails, skip logging

        try:
            await target_area.click()
        except:
            try:
                await target_area.evaluate('el => el.click()')
            except:
                pass

    # Auto refresh if needed (simple wait mode, consistent with TicketPlus/iBon/FamiTicket)
    if is_need_refresh:
        interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
        if interval > 0:
            debug.log(f"[AREA SELECT] Waiting {interval}s before reload...")
            await asyncio.sleep(interval)

        debug.log(f"[AREA SELECT] Page reloading...")
        try:
            await tab.reload()
        except Exception:
            pass

async def nodriver_get_tixcraft_target_area(el, config_dict, area_keyword_item):
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]
    debug = util.create_debug_logger(config_dict)
    is_need_refresh = False
    matched_blocks = None

    # Display keyword information
    if debug.enabled:
        debug.log(f"[AREA KEYWORD] ========================================")
        if area_keyword_item:
            keyword_parts = area_keyword_item.split(' ')
            debug.log(f"[AREA KEYWORD] Raw input: '{area_keyword_item}'")
            debug.log(f"[AREA KEYWORD] Parsed (AND logic): {keyword_parts}")
            debug.log(f"[AREA KEYWORD] Total sub-keywords: {len(keyword_parts)}")
            debug.log(f"[AREA KEYWORD] Auto-select mode: {area_auto_select_mode}")
        else:
            debug.log(f"[AREA KEYWORD] No keyword specified, matching all areas")
            debug.log(f"[AREA KEYWORD] Auto-select mode: {area_auto_select_mode}")

    if not el:
        debug.log(f"[AREA KEYWORD] Element is None, cannot select area")
        return True, None

    try:
        area_list = await el.query_selector_all('a')
    except:
        debug.log(f"[AREA KEYWORD] Failed to query area list")
        return True, None

    if not area_list or len(area_list) == 0:
        debug.log(f"[AREA KEYWORD] No areas found")
        return True, None

    debug.log(f"[AREA KEYWORD] Found {len(area_list)} area(s) to check")
    debug.log(f"[AREA KEYWORD] ========================================")

    matched_blocks = []
    area_index = 0
    for row in area_list:
        area_index += 1

        try:
            row_html = await row.get_html()
            row_text = util.remove_html_tags(row_html)
        except:
            debug.log(f"[AREA KEYWORD] [{area_index}] Failed to get row content")
            break

        if not row_text or util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            debug.log(f"[AREA KEYWORD] [{area_index}] Excluded by keyword_exclude")
            continue

        debug.log(f"[AREA KEYWORD] [{area_index}/{len(area_list)}] Checking: {row_text[:80]}...")

        row_text = util.format_keyword_string(row_text)

        # Check keyword match
        if area_keyword_item:
            keyword_parts = area_keyword_item.split(' ')

            debug.log(f"[AREA KEYWORD]   Matching AND keywords: {keyword_parts}")

            # Check each keyword individually for detailed feedback
            match_results = {}
            for kw in keyword_parts:
                formatted_kw = util.format_keyword_string(kw)
                kw_match = formatted_kw in row_text
                match_results[kw] = kw_match

                if debug.enabled:
                    status = "PASS" if kw_match else "FAIL"
                    debug.log(f"[AREA KEYWORD]     {status} '{kw}': {kw_match}")

            is_match = all(match_results.values())

            if debug.enabled:
                if is_match:
                    debug.log(f"[AREA KEYWORD]   All AND keywords matched")
                else:
                    debug.log(f"[AREA KEYWORD]   AND logic failed")

            if not is_match:
                continue
        else:
            debug.log(f"[AREA KEYWORD]   No keyword filter, accepting this area")

        # Check seat availability for multiple tickets
        if config_dict["ticket_number"] > 1:
            try:
                font_el = await row.query_selector('font')
                if font_el:
                    font_text = await font_el.evaluate('el => el.textContent')
                    if font_text:
                        font_text = "@%s@" % font_text

                        debug.log(f"[AREA KEYWORD]   Checking seats: {font_text.strip('@')}")

                        # Skip if only 1-9 seats remaining
                        SEATS_1_9 = ["@%d@" % i for i in range(1, 10)]
                        if any(seat in font_text for seat in SEATS_1_9):
                            debug.log(f"[AREA KEYWORD]   Insufficient seats (need {config_dict['ticket_number']}, only {font_text.strip('@')} available)")
                            continue
                        else:
                            debug.log(f"[AREA KEYWORD]   Sufficient seats available")
            except:
                pass

        matched_blocks.append(row)

        debug.log(f"[AREA KEYWORD]   → Area added to matched list (total: {len(matched_blocks)})")

        if area_auto_select_mode == util.CONST_FROM_TOP_TO_BOTTOM:
            debug.log(f"[AREA KEYWORD]   Mode is '{area_auto_select_mode}', stopping at first match")
            break

    if not matched_blocks:
        is_need_refresh = True
        matched_blocks = None

    return is_need_refresh, matched_blocks

async def nodriver_ticket_number_select_fill(tab, select_obj, ticket_number, select_id=None):
    """簡化版本：參考 Chrome 邏輯設定票券數量，並檢查 option 是否可用

    Args:
        tab: NoDriver tab object
        select_obj: The select element (for compatibility)
        ticket_number: Target ticket count to select
        select_id: The specific select element ID to use (fixes Issue #200/#201)
    """
    is_ticket_number_assigned = False

    if select_obj is None and select_id is None:
        return is_ticket_number_assigned

    # Build JavaScript selector - prefer specific ID over querySelector
    if select_id:
        js_selector = f"document.getElementById('{select_id}')"
    else:
        js_selector = "document.querySelector('.mobile-select') || document.querySelector('select[id*=\"TicketForm_ticketPrice_\"]')"

    try:
        # 嘗試透過 JavaScript 設定選擇器的值，並檢查 option 是否 disabled
        result = await tab.evaluate(f'''
            (function() {{
                const select = {js_selector};
                if (!select) return {{success: false, error: "Select not found"}};

                // 售完關鍵字列表
                const soldOutKeywords = ["選購一空", "已售完", "Sold out", "No tickets available", "空席なし", "完売した"];

                // 先嘗試設定目標數量（檢查是否 disabled 或售完）
                const targetOption = Array.from(select.options).find(opt =>
                    opt.value === "{ticket_number}" &&
                    !opt.disabled &&
                    !soldOutKeywords.includes(opt.value)
                );

                if (targetOption) {{
                    select.value = "{ticket_number}";
                    select.selectedIndex = targetOption.index;
                    select.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return {{success: true, selected: "{ticket_number}"}};
                }}

                // Fallback: select max available option instead of hardcoded "1"
                const validOptions = Array.from(select.options).filter(opt =>
                    !opt.disabled &&
                    !soldOutKeywords.includes(opt.value) &&
                    parseInt(opt.value) > 0 &&
                    !isNaN(parseInt(opt.value))
                );

                if (validOptions.length > 0) {{
                    const maxOption = validOptions.reduce((max, opt) =>
                        parseInt(opt.value) > parseInt(max.value) ? opt : max
                    );
                    select.value = maxOption.value;
                    select.selectedIndex = maxOption.index;
                    select.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return {{success: true, selected: maxOption.value, fallback: true}};
                }}

                return {{success: false, error: "No valid options (all disabled or sold out)"}};
            }})();
        ''')

        # 解析結果
        result = util.parse_nodriver_result(result)
        if isinstance(result, dict):
            is_ticket_number_assigned = result.get('success', False)

    except Exception as exc:
        logger.warning(f"Failed to set ticket number: {exc}")

    return is_ticket_number_assigned

async def nodriver_tixcraft_assign_ticket_number(tab, config_dict):
    """
    Enhanced ticket type selection with keyword matching support
    支援票種關鍵字選擇（indievox 類型 B 頁面：直接跳到 /ticket/ticket/）
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    is_ticket_number_assigned = False

    # 等待票券選擇器出現（智慧等待，取代固定 0.5 秒延遲）
    try:
        await tab.wait_for('.mobile-select, select[id*="TicketForm_ticketPrice_"]', timeout=2)
    except:
        pass  # Continue even if timeout, will try to find selectors below

    # 查找票券選擇器
    form_select_list = []
    try:
        form_select_list = await tab.query_selector_all('.mobile-select')
    except Exception as exc:
        debug.log("Failed to find .mobile-select")

    # 如果沒找到 .mobile-select，嘗試其他選擇器
    if len(form_select_list) == 0:
        try:
            form_select_list = await tab.query_selector_all('select[id*="TicketForm_ticketPrice_"]')
        except Exception as exc:
            debug.log("Failed to find ticket selector")

    form_select_count = len(form_select_list)

    if form_select_count > 0:
        debug.log(f"[TICKET SELECT] Found {form_select_count} select element(s)")

    # Get area keyword configuration
    import json
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    area_auto_fallback = config_dict.get('area_auto_fallback', False)
    auto_select_mode = config_dict["area_auto_select"]["mode"]

    # Parse keywords using JSON
    area_keyword_array = util.parse_keyword_string_to_array(area_keyword)
    if area_keyword_array:
        debug.log(f"[TICKET SELECT] Area keywords: {area_keyword_array}")

    # 過濾並收集票種資訊（包含票種名稱）
    valid_ticket_types = []
    sold_out_keywords = ["選購一空", "已售完", "Sold out", "No tickets available", "空席なし", "完売した"]

    # 使用 NoDriver Element API 檢查每個 select 元素
    for idx, select_element in enumerate(form_select_list):
        try:
            # 更新元素以確保屬性載入
            await select_element.update()

            # 檢查 select 是否 disabled
            select_attrs = select_element.attrs or {}
            select_id = select_attrs.get('id', f'select_{idx}')
            is_select_disabled = 'disabled' in select_attrs

            if is_select_disabled:
                debug.log(f"[TICKET SELECT] Skipping disabled select: {select_id}")
                continue

            # 檢查 option 元素
            option_elements = await select_element.query_selector_all('option')
            has_valid_option = False
            option_values = []

            for option_element in option_elements:
                try:
                    await option_element.update()
                    option_attrs = option_element.attrs or {}
                    option_value = option_attrs.get('value', '')
                    option_text = option_element.text or ''
                    option_disabled = 'disabled' in option_attrs

                    option_values.append(option_value)

                    # 檢查是否為有效選項
                    if (option_value != "0" and
                        not option_disabled and
                        option_value not in sold_out_keywords and
                        option_text not in sold_out_keywords):
                        has_valid_option = True

                except Exception as opt_exc:
                    debug.log(f"[TICKET SELECT] Error checking option: {opt_exc}")
                    continue

            if not has_valid_option:
                debug.log(f"[TICKET SELECT] Skipping select (all options sold out or disabled): {select_id}")
                continue

            # 嘗試獲取票種名稱（從父元素 <tr> 中的 <h4> 或 <td> 提取）
            ticket_type_name = ""
            try:
                # 查找父元素 <tr>
                parent_row = select_element
                for _ in range(5):  # 最多向上查找 5 層
                    parent_row = parent_row.parent
                    if parent_row and parent_row.tag.lower() == 'tr':
                        break

                if parent_row and parent_row.tag.lower() == 'tr':
                    # 嘗試找 <h4> 標籤
                    h4_element = await parent_row.query_selector('h4')
                    if h4_element:
                        ticket_type_name = h4_element.text or ""
                    else:
                        # 嘗試找 <td class="fcBlue">
                        td_element = await parent_row.query_selector('td.fcBlue')
                        if td_element:
                            ticket_type_name = td_element.text or ""

                    ticket_type_name = ticket_type_name.strip()

            except Exception as name_exc:
                debug.log(f"[TICKET SELECT] Failed to extract ticket type name: {name_exc}")

            # 加入 valid_ticket_types
            valid_ticket_types.append({
                'select': select_element,
                'id': select_id,
                'name': ticket_type_name,
                'index': idx
            })

            debug.log(f"[TICKET SELECT] Valid ticket type: {select_id} - '{ticket_type_name}'")

        except Exception as exc:
            debug.log(f"[TICKET SELECT] Error checking select element: {exc}")

    debug.log(f"[TICKET SELECT] Valid ticket types: {len(valid_ticket_types)}/{form_select_count}")

    if len(valid_ticket_types) == 0:
        debug.log("[TICKET SELECT] Warning: All ticket types are sold out or disabled")
        return False, None, None

    # Keyword matching logic (similar to area selection)
    matched_ticket = None
    is_keyword_matched = False

    if area_keyword_array:
        debug.log(f"[TICKET SELECT] Starting keyword matching with {len(area_keyword_array)} keyword(s)")

        for keyword_index, keyword_item in enumerate(area_keyword_array):
            debug.log(f"[TICKET SELECT] Checking keyword #{keyword_index + 1}: '{keyword_item}'")

            # Check each valid ticket type
            for ticket_info in valid_ticket_types:
                ticket_name = ticket_info['name']

                # Apply exclude keyword filter
                if util.reset_row_text_if_match_keyword_exclude(config_dict, ticket_name):
                    debug.log(f"[TICKET SELECT]   Excluded by keyword_exclude: {ticket_name}")
                    continue

                # Keyword matching (support space-separated AND logic)
                keyword_parts = keyword_item.split(' ')
                row_text = util.format_keyword_string(ticket_name)
                is_match = True

                for kw in keyword_parts:
                    formatted_kw = util.format_keyword_string(kw)
                    if formatted_kw not in row_text:
                        is_match = False
                        break

                if is_match:
                    matched_ticket = ticket_info
                    is_keyword_matched = True
                    debug.log(f"[TICKET SELECT]   [OK] Keyword matched: '{ticket_name}'")
                    break

            if matched_ticket:
                break  # Early return: first match wins

        if not matched_ticket:
            debug.log(f"[TICKET SELECT] All keywords failed to match")

    # Single option auto-select: when only one valid ticket type exists, select it directly
    # (unless excluded by keyword_exclude)
    if not matched_ticket and len(valid_ticket_types) == 1:
        single_ticket = valid_ticket_types[0]
        ticket_name = single_ticket['name']

        # Check if excluded by keyword_exclude
        if not util.reset_row_text_if_match_keyword_exclude(config_dict, ticket_name):
            matched_ticket = single_ticket
            debug.log(f"[TICKET SELECT] Single option auto-select: '{ticket_name}'")
        else:
            debug.log(f"[TICKET SELECT] Single option excluded by keyword_exclude: '{ticket_name}'")

    # Fallback logic (similar to area selection)
    if not matched_ticket:
        if area_keyword_array and not area_auto_fallback:
            # Strict mode: no keyword match and fallback disabled
            debug.log(f"[TICKET SELECT] area_auto_fallback=false, fallback is disabled")
            debug.log(f"[TICKET SELECT] No ticket type selected")
            return False, None, None
        else:
            # Fallback enabled or no keyword specified
            if area_keyword_array:
                debug.log(f"[TICKET SELECT] area_auto_fallback=true, using fallback selection")

            # Select based on auto_select_mode
            matched_ticket = util.get_target_item_from_matched_list(
                [t['select'] for t in valid_ticket_types],
                auto_select_mode
            )
            # Find the ticket_info for the matched select
            for ticket_info in valid_ticket_types:
                if ticket_info['select'] == matched_ticket:
                    matched_ticket = ticket_info
                    break

            if matched_ticket:
                selection_type = "fallback" if area_keyword_array else "mode-based"
                debug.log(f"[TICKET SELECT] Selected ticket type ({selection_type}): '{matched_ticket['name']}'")

    # Use the matched ticket select
    select_obj = matched_ticket['select'] if matched_ticket else None
    form_select_count = len(valid_ticket_types)

    # Get select ID for JavaScript operations
    select_id = matched_ticket['id'] if matched_ticket else None

    # 檢查是否已經選擇了票券數量（非 "0"）
    if select_id:
        try:
            # 使用 JavaScript 取得當前選中的值（使用正確的 select ID）
            current_value = await tab.evaluate(f'''
                (function() {{
                    const select = document.getElementById('{select_id}');
                    return select ? select.value : "0";
                }})();
            ''')

            # 解析結果
            current_value = util.parse_nodriver_result(current_value)

            if current_value and current_value != "0" and str(current_value).isnumeric():
                is_ticket_number_assigned = True
                debug.log(f"Ticket number already set to: {current_value}")
        except Exception as exc:
            debug.log(f"Failed to check current selected value: {exc}")

    # 回傳結果：select_obj 和 select_id 用於後續操作
    return is_ticket_number_assigned, select_obj, select_id

async def nodriver_tixcraft_ticket_main_agree(tab, config_dict):
    debug = util.create_debug_logger(config_dict)

    debug.log("Starting to check agreement checkbox")

    for i in range(3):
        is_finish_checkbox_click = await nodriver_check_checkbox_enhanced(tab, '#TicketForm_agree', config_dict)
        if is_finish_checkbox_click:
            debug.log("Agreement checkbox checked successfully")
            break
        else:
            debug.log(f"Failed to check agreement, retry {i+1}/3")

    if not is_finish_checkbox_click:
        debug.log("Warning: Failed to check agreement checkbox")

async def nodriver_tixcraft_ticket_main(tab, config_dict, ocr, Captcha_Browser, domain_name):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False
    debug = util.create_debug_logger(config_dict)

    # 檢查是否已經設定過票券數量（方案 B：狀態標記）
    current_url, _ = await nodriver_current_url(tab)
    ticket_number = str(config_dict["ticket_number"])
    ticket_state_key = f"ticket_assigned_{current_url}_{ticket_number}"

    if ticket_state_key in _state and _state[ticket_state_key]:
        debug.log(f"Ticket number already set ({ticket_number}), skipping")

        # Ensure agreement checkbox is checked (even if ticket number already set)
        await nodriver_tixcraft_ticket_main_agree(tab, config_dict)

        # Reset OCR state if captcha alert detected (wrong answer submitted)
        if _state.get("captcha_alert_detected", False):
            _state["ocr_completed_url"] = ""
            _state["captcha_alert_detected"] = False

        # Skip OCR if already completed on this URL (non-force_submit mode only)
        is_force_submit = config_dict["ocr_captcha"]["force_submit"]
        if is_force_submit or _state.get("ocr_completed_url", "") != current_url:
            await nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name)
        return

    # Always check agreement checkbox in NoDriver mode
    await nodriver_tixcraft_ticket_main_agree(tab, config_dict)

    is_ticket_number_assigned = False

    # PS: some events on tixcraft have multi <select>.
    # Fix Issue #200/#201: Now returns select_id for correct element targeting
    is_ticket_number_assigned, select_obj, select_id = await nodriver_tixcraft_assign_ticket_number(tab, config_dict)

    if not is_ticket_number_assigned:
        debug.log(f"Setting ticket number: {ticket_number}")
        is_ticket_number_assigned = await nodriver_ticket_number_select_fill(tab, select_obj, ticket_number, select_id)

    # Record state after successful setting
    if is_ticket_number_assigned:
        _state[ticket_state_key] = True
        debug.log("Ticket number set successfully, starting OCR captcha processing")
        await nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name)
    else:
        # T026: Fix Issue #174 - reload page when ticket number cannot be set
        # This prevents infinite loop when desired ticket count is unavailable
        debug.log("[TICKET SELECT] Ticket count unavailable, reloading page to retry...")
        try:
            # Wait based on auto_reload_page_interval setting
            interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
            if interval > 0:
                await asyncio.sleep(interval)
            await tab.reload()
        except Exception as reload_exc:
            debug.log(f"[TICKET SELECT] Reload failed: {reload_exc}")

async def nodriver_tixcraft_keyin_captcha_code(tab, answer="", auto_submit=False, config_dict=None):
    """輸入驗證碼到表單"""
    debug = util.create_debug_logger(config_dict) if config_dict else util.create_debug_logger(enabled=False)
    is_verifyCode_editing = False
    is_form_submitted = False

    # 找到驗證碼輸入框
    form_verifyCode = await tab.query_selector('#TicketForm_verifyCode')

    if form_verifyCode:
        is_visible = False
        try:
            # 檢查元素是否可見和可用
            is_visible = await tab.evaluate('''
                (function() {
                    const element = document.querySelector('#TicketForm_verifyCode');
                    return element && !element.disabled && element.offsetParent !== null;
                })();
            ''')
        except Exception as exc:
            pass

        if is_visible:
            # 取得當前輸入值
            inputed_value = ""
            try:
                inputed_value = await form_verifyCode.apply('function (element) { return element.value; }') or ""
            except Exception as exc:
                pass

            is_text_clicked = False

            if not inputed_value and not answer:
                # 聚焦到輸入框等待手動輸入
                try:
                    await form_verifyCode.click()
                    is_text_clicked = True
                    is_verifyCode_editing = True
                except Exception as exc:
                    debug.log("[TIXCRAFT CAPTCHA] Failed to click captcha input, trying JavaScript")
                    try:
                        await tab.evaluate('''
                            document.getElementById("TicketForm_verifyCode").focus();
                        ''')
                        is_verifyCode_editing = True
                    except Exception as exc:
                        pass

            if answer:
                debug.log("[TIXCRAFT CAPTCHA] Starting to fill in captcha...")
                try:
                    if not is_text_clicked:
                        await form_verifyCode.click()

                    # 清空並輸入答案
                    await form_verifyCode.apply('function (element) { element.value = ""; }')
                    await form_verifyCode.send_keys(answer)

                    if auto_submit:
                        # 提交前確認票券數量是否已設定
                        ticket_number_ok = await tab.evaluate('''
                            (function() {
                                const select = document.querySelector('.mobile-select') ||
                                              document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                return select && select.value !== "0" && select.value !== "";
                            })();
                        ''')
                        ticket_number_ok = util.parse_nodriver_result(ticket_number_ok)

                        if not ticket_number_ok and config_dict:
                            debug.log("[TIXCRAFT CAPTCHA] Warning: Ticket number not set, resetting...")
                            # Reset ticket number
                            ticket_number = str(config_dict.get("ticket_number", 2))
                            await tab.evaluate(f'''
                                (function() {{
                                    const select = document.querySelector('.mobile-select') ||
                                                  document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                    if (select) {{
                                        select.value = "{ticket_number}";
                                        select.dispatchEvent(new Event('change', {{bubbles: true}}));
                                    }}
                                }})();
                            ''')

                        # 勾選同意條款
                        await nodriver_check_checkbox_enhanced(tab, '#TicketForm_agree')

                        # 最終確認所有欄位都已填寫
                        form_ready = await tab.evaluate('''
                            (function() {
                                const select = document.querySelector('.mobile-select') ||
                                              document.querySelector('select[id*="TicketForm_ticketPrice_"]');
                                const verify = document.querySelector('#TicketForm_verifyCode');
                                const agree = document.querySelector('#TicketForm_agree');

                                // Ticketmaster check-captcha page has no ticket selector
                                // Ticket number is already set on previous page
                                const isTicketmaster = window.location.href.includes('ticketmaster');
                                const ticketOk = isTicketmaster ? true : (select && select.value !== "0" && select.value !== "");

                                return {
                                    ticket: ticketOk,
                                    verify: verify && verify.value.length === 4,
                                    agree: agree && agree.checked,
                                    ready: ticketOk &&
                                           (verify && verify.value.length === 4) &&
                                           (agree && agree.checked)
                                };
                            })();
                        ''')
                        form_ready = util.parse_nodriver_result(form_ready)

                        if form_ready.get('ready', False):
                            # 提交表單 (按 Enter) - 使用完整的鍵盤事件
                            await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                            await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                            is_verifyCode_editing = False
                            is_form_submitted = True
                        else:
                            debug.log(f"[TIXCRAFT CAPTCHA] Form not ready - Ticket:{form_ready.get('ticket')} Captcha:{form_ready.get('verify')} Agreement:{form_ready.get('agree')}")
                    else:
                        # 選取輸入框內容並顯示提示
                        await tab.evaluate('''
                            document.getElementById("TicketForm_verifyCode").select();
                        ''')
                        # 顯示提示訊息
                        await nodriver_tixcraft_toast(tab, f"※ 按 Enter 如果答案是: {answer}")

                except Exception as exc:
                    debug.log(f"[TIXCRAFT CAPTCHA] Failed to input captcha: {exc}")

    return is_verifyCode_editing, is_form_submitted

async def nodriver_tixcraft_toast(tab, message):
    """顯示提示訊息"""
    try:
        await tab.evaluate(f'''
            (function() {{
                const toast = document.querySelector('p.remark-word');
                if (toast) {{
                    toast.innerHTML = '{message}';
                }}
            }})();
        ''')
    except Exception as exc:
        pass

async def nodriver_tixcraft_reload_captcha(tab, domain_name):
    """點擊重新載入驗證碼"""
    ret = False
    image_id = 'TicketForm_verifyCode-image'

    if 'indievox.com' in domain_name:
        image_id = 'TicketForm_verifyCode-image'

    try:
        form_captcha = await tab.query_selector(f"#{image_id}")
        if form_captcha:
            await form_captcha.click()
            ret = True
    except Exception as exc:
        print(f"Failed to reload captcha: {exc}")

    return ret

async def nodriver_tixcraft_get_ocr_answer(tab, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name):
    """取得驗證碼圖片並進行 OCR 識別"""
    debug = util.create_debug_logger(enabled=False)  # OCR: intentionally silent

    ocr_answer = None
    if not ocr is None:
        img_base64 = None

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.request_captcha())

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'TicketForm_verifyCode-image'
            if 'indievox.com' in domain_name:
                image_id = 'TicketForm_verifyCode-image'

            try:
                # Stage 7: get captcha image via canvas
                # async IIFE waits for image load to avoid reading stale image after reload
                form_verifyCode_base64 = await tab.evaluate(f'''
                    (async function() {{
                        var img = document.getElementById('{image_id}');
                        if(!img || !img.src) return null;

                        if(img.naturalWidth === 0 || !img.complete) {{
                            await new Promise(function(resolve) {{
                                var timer = setTimeout(resolve, 3000);
                                img.onload = function() {{ clearTimeout(timer); resolve(); }};
                                img.onerror = function() {{ clearTimeout(timer); resolve(); }};
                            }});
                        }}

                        if(img.naturalWidth === 0 || img.naturalHeight === 0) return null;

                        var canvas = document.createElement('canvas');
                        var context = canvas.getContext('2d');
                        canvas.height = img.naturalHeight;
                        canvas.width = img.naturalWidth;
                        context.drawImage(img, 0, 0);
                        return canvas.toDataURL();
                    }})();
                ''', await_promise=True)

                if form_verifyCode_base64:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])

                if img_base64 is None:
                    if not Captcha_Browser is None:
                        debug.log("[TIXCRAFT OCR] Failed to get image from canvas, using fallback: NonBrowser")
                        img_base64 = base64.b64decode(Captcha_Browser.request_captcha())

            except Exception as exc:
                debug.log("[TIXCRAFT OCR] Canvas error:", str(exc))

        # OCR 識別
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                debug.log("[TIXCRAFT OCR] Classification error:", str(exc))

    return ocr_answer

async def nodriver_tixcraft_auto_ocr(tab, config_dict, ocr, away_from_keyboard_enable,
                                     previous_answer, Captcha_Browser,
                                     ocr_captcha_image_source, domain_name):
    """OCR 自動識別主邏輯"""
    debug = util.create_debug_logger(config_dict)

    is_need_redo_ocr = False
    is_form_submitted = False

    is_input_box_exist = False
    if not ocr is None:
        form_verifyCode = None
        try:
            form_verifyCode = await tab.query_selector('#TicketForm_verifyCode')
            is_input_box_exist = True
        except Exception as exc:
            pass
    else:
        debug.log("[TIXCRAFT OCR] ddddocr component unavailable, you may be running on ARM")

    if is_input_box_exist:
        debug.log("[TIXCRAFT OCR] away_from_keyboard_enable:", away_from_keyboard_enable)
        debug.log("[TIXCRAFT OCR] previous_answer:", previous_answer)
        debug.log("[TIXCRAFT OCR] ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()
        ocr_answer = await nodriver_tixcraft_get_ocr_answer(tab, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name)
        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        debug.log("[TIXCRAFT OCR] Processing time:", "{:.3f}".format(ocr_elapsed_time))

        if ocr_answer is None:
            if away_from_keyboard_enable:
                # 頁面尚未準備好，重試
                # PS: 通常發生在非同步腳本取得驗證碼圖片時
                is_need_redo_ocr = True
                await asyncio.sleep(0.1)
            else:
                await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
        else:
            ocr_answer = ocr_answer.strip()
            debug.log("[TIXCRAFT OCR] Result:", ocr_answer)
            if len(ocr_answer) == 4:
                who_care_var, is_form_submitted = await nodriver_tixcraft_keyin_captcha_code(tab, answer=ocr_answer, auto_submit=away_from_keyboard_enable, config_dict=config_dict)
            else:
                if not away_from_keyboard_enable:
                    await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                else:
                    is_need_redo_ocr = True
                    if previous_answer != ocr_answer:
                        previous_answer = ocr_answer
                        debug.log("[TIXCRAFT OCR] Reloading captcha")

                        await nodriver_tixcraft_reload_captcha(tab, domain_name)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            await asyncio.sleep(0.3)
    else:
        debug.log("[TIXCRAFT OCR] Input box not found, exiting OCR...")

    return is_need_redo_ocr, previous_answer, is_form_submitted

async def nodriver_tixcraft_ticket_main_ocr(tab, config_dict, ocr, Captcha_Browser, domain_name):
    """票券頁面 OCR 處理主函數"""
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False, "", False

    debug = util.create_debug_logger(config_dict)

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    if not config_dict["ocr_captcha"]["enable"]:
        # 手動模式
        await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
    else:
        # 自動 OCR 模式
        previous_answer = None
        current_url, _ = await nodriver_current_url(tab)
        fail_count = 0  # Track consecutive failures
        total_fail_count = 0  # Track total failures
        is_form_submitted = False

        for redo_ocr in range(5):
            is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_tixcraft_auto_ocr(
                tab, config_dict, ocr, away_from_keyboard_enable,
                previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name
            )

            if is_form_submitted:
                debug.log("[TIXCRAFT OCR] Form submitted")
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break

            # Track failures and refresh captcha after 3 consecutive failures
            if is_need_redo_ocr:
                fail_count += 1
                total_fail_count += 1
                debug.log(f"[TIXCRAFT OCR] Fail count: {fail_count}, Total fails: {total_fail_count}")

                # Check if total failures reached 5, switch to manual input mode
                if total_fail_count >= 5:
                    print("[TIXCRAFT OCR] OCR failed 5 times. Please enter captcha manually.")
                    away_from_keyboard_enable = False
                    await nodriver_tixcraft_keyin_captcha_code(tab, config_dict=config_dict)
                    break

                if fail_count >= 3:
                    debug.log("[TIXCRAFT OCR] 3 consecutive failures reached")

                    # Try to dismiss any existing alert before continuing
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        debug.log("[TIXCRAFT OCR] Dismissed existing alert")
                    except:
                        pass

                    # Wait for potential auto-refresh
                    await asyncio.sleep(2.5)
                    fail_count = 0  # Reset consecutive counter after handling

            # 檢查是否還在同一頁面
            new_url, _ = await nodriver_current_url(tab)
            if new_url != current_url:
                break

            debug.log(f"[TIXCRAFT OCR] Retry {redo_ocr + 1}/5")

        # Mark OCR completed for this URL only when form was actually submitted
        if is_form_submitted:
            _state["ocr_completed_url"] = current_url

async def nodriver_tixcraft_main(tab, url, config_dict, ocr, Captcha_Browser):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    # Global alert handler - auto-dismiss all alerts (sold out, errors, etc.)
    # Handles alerts that appear after page navigation (e.g., area selection redirects)
    # Reference: KHAM platform implementation (Line 10681-10697)
    async def handle_global_alert(event):
        # Skip alert handling when bot is paused (let user handle manually)
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            return
        # IMPORTANT: Use tab.target.url (cached) instead of nodriver_current_url (js_dumps)
        # When alert dialog is open, JavaScript execution is blocked, causing js_dumps to hang
        current_url = tab.target.url if hasattr(tab, 'target') and tab.target else ""

        if '/ticket/checkout' in current_url:
            debug.log(f"[GLOBAL ALERT] Alert on checkout page, NOT auto-dismissing: '{event.message}'")
            return

        debug.log(f"[GLOBAL ALERT] Alert detected: '{event.message}'")

        # Track captcha error alerts for retry logic
        is_captcha_error = False
        captcha_error_keywords = [
            'verification code',
            'incorrect',
            'try again',
            'captcha',
            'wrong code'
        ]
        alert_message_lower = event.message.lower()
        for keyword in captcha_error_keywords:
            if keyword in alert_message_lower:
                is_captcha_error = True
                break

        if is_captcha_error:
            _state["captcha_alert_detected"] = True
            debug.log(f"[GLOBAL ALERT] Captcha error detected, flagging for retry")

        # Issue #188: Detect sold out alerts to add cooldown delay
        sold_out_keywords = ['售完', '已售完', '選購一空', 'sold out', 'no tickets']
        is_sold_out_alert = any(kw in alert_message_lower for kw in sold_out_keywords)

        # Dismiss the alert - try multiple times with small delays
        dismiss_success = False
        for attempt in range(3):
            try:
                await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                dismiss_success = True
                debug.log(f"[GLOBAL ALERT] Alert dismissed (attempt {attempt + 1})")
                break
            except Exception as dismiss_exc:
                error_msg = str(dismiss_exc)
                # CDP -32602 means no dialog is showing (already dismissed by another handler or user)
                if "No dialog is showing" in error_msg or "-32602" in error_msg:
                    dismiss_success = True  # Consider it handled
                    debug.log("[GLOBAL ALERT] Dialog already dismissed")
                    break  # No need to retry
                if attempt < 2:
                    await asyncio.sleep(0.1)  # Small delay before retry
                else:
                    debug.log(f"[GLOBAL ALERT] Failed to dismiss alert: {dismiss_exc}")

        # Issue #188: Set cooldown timestamp instead of async sleep (event handler doesn't block main loop)
        if is_sold_out_alert and dismiss_success:
            interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
            if interval > 0:
                cooldown_until = time.time() + interval
                _state["sold_out_cooldown_until"] = cooldown_until
                debug.log(f"[GLOBAL ALERT] Sold out detected, setting cooldown for {interval}s")

    if not _state:
        _state.update({
            "fail_list": [],
            "fail_promo_list": [],
            "start_time": None,
            "done_time": None,
            "elapsed_time": None,
            "is_popup_checkout": False,
            "area_retry_count": 0,
            "played_sound_ticket": False,
            "played_sound_order": False,
            "alert_handler_registered": False,
            "captcha_alert_detected": False,
            "ocr_completed_url": "",
            "last_homepage_redirect_time": 0,
            "sold_out_cooldown_until": 0,
            "printed_completed": False,
            "ticketmaster_area_processed_url": "",
            "ticketmaster_captcha_processed_url": "",
        })

    # Register global alert handler (remains active throughout session)
    # Only register once to prevent infinite loop
    if not _state.get("alert_handler_registered", False):
        try:
            tab.add_handler(cdp.page.JavascriptDialogOpening, handle_global_alert)
            _state["alert_handler_registered"] = True
            debug.log(f"[GLOBAL ALERT] Global alert handler registered")
        except Exception as handler_exc:
            debug.log(f"[GLOBAL ALERT] Failed to register alert handler: {handler_exc}")

    await nodriver_tixcraft_home_close_window(tab)

    # special case for same event re-open, redirect to user's homepage.
    # Add cooldown to prevent infinite redirect loop when area page is unavailable
    # Match homepage URLs: tixcraft.com, tixcraft.com/, tixcraft.com/activity
    is_tixcraft_home = url in ['https://tixcraft.com', 'https://tixcraft.com/', 'https://tixcraft.com/activity']
    if is_tixcraft_home:
        homepage = config_dict["homepage"]
        # Only redirect if homepage is not the platform root itself (avoid infinite loop)
        homepage_is_root = homepage.rstrip('/') in ['https://tixcraft.com', 'https://tixcraft.com/activity']
        if not homepage_is_root:
            current_time = time.time()
            last_redirect_time = _state.get("last_homepage_redirect_time", 0)
            # Use auto_reload_page_interval from settings, default to 3 seconds
            redirect_interval = config_dict["advanced"].get("auto_reload_page_interval", 3)
            if redirect_interval <= 0:
                redirect_interval = 3  # Minimum 3 seconds to prevent rapid loop

            if current_time - last_redirect_time > redirect_interval:
                try:
                    _state["last_homepage_redirect_time"] = current_time
                    await tab.get(homepage)
                except Exception:
                    pass

    if "/activity/detail/" in url:
        _state["start_time"] = time.time()
        is_redirected = await nodriver_tixcraft_redirect(tab, url)

    is_date_selected = False
    # Check if this is a Ticketmaster page before using TixCraft logic
    if "/activity/game/" in url and 'ticketmaster' not in url:
        _state["start_time"] = time.time()
        if config_dict["date_auto_select"]["enable"]:
            domain_name = url.split('/')[2]
            is_date_selected = await nodriver_tixcraft_date_auto_select(tab, url, config_dict, domain_name)

    # T010: Ticketmaster date selection integration (User Story 1)
    # Support both URL formats:
    # - /artist/{artist_id} (artist listing page)
    # - /activity/game/{event_id} (event date listing page from /activity/detail redirect)
    is_ticketmaster_date_page = (
        'ticketmaster' in url and
        (('/artist/' in url and len(url.split('/'))==6) or
         ('/activity/game/' in url))
    )

    if is_ticketmaster_date_page:
        _state["start_time"] = time.time()
        if config_dict["date_auto_select"]["enable"]:
            debug.log("[TICKETMASTER] Detected Ticketmaster date page, calling date auto select")
            domain_name = url.split('/')[2]
            # Call Ticketmaster date auto select
            is_date_selected = await nodriver_ticketmaster_date_auto_select(tab, config_dict)
            if debug.enabled:
                if is_date_selected:
                    debug.log("[TICKETMASTER] Date selection completed")
                else:
                    debug.log("[TICKETMASTER] Date selection failed or no match")

    # choose area
    if '/ticket/area/' in url:
        domain_name = url.split('/')[2]
        if config_dict["area_auto_select"]["enable"]:
            if not 'ticketmaster' in domain_name:
                # for tixcraft
                await nodriver_tixcraft_area_auto_select(tab, url, config_dict)

                _state["area_retry_count"]+=1
                #print("count:", _state["area_retry_count"])
                if _state["area_retry_count"] >= (60 * 15):
                    # Cool-down
                    _state["area_retry_count"] = 0
                    await asyncio.sleep(5)
            else:
                # T013: Ticketmaster area selection integration (User Story 2)
                # Check if we already processed this page (avoid repeated execution)
                ticketmaster_area_processed = _state.get("ticketmaster_area_processed_url", "")
                if ticketmaster_area_processed == url:
                    # Already processed this URL, wait for page change
                    _state["area_retry_count"] += 1
                    if _state["area_retry_count"] >= 10:
                        # Reset after 10 retries to allow re-processing
                        _state["ticketmaster_area_processed_url"] = ""
                        _state["area_retry_count"] = 0
                        debug.log("[TICKETMASTER] Area page retry limit reached, resetting state")
                else:
                    # Parse zone_info and auto-select area
                    zone_info = await nodriver_ticketmaster_parse_zone_info(tab, config_dict)
                    if zone_info:
                        await nodriver_ticketmaster_area_auto_select(tab, config_dict, zone_info)

                    # T017: Ticketmaster ticket number and promo integration (User Story 3)
                    # Set ticket number (will fallback to zone_info if ticketPriceList not found)
                    await nodriver_ticketmaster_assign_ticket_number(tab, config_dict)

                    # Handle promo code
                    _state["fail_promo_list"] = await nodriver_ticketmaster_promo(tab, config_dict, _state["fail_promo_list"])

                    # Mark this URL as processed
                    _state["ticketmaster_area_processed_url"] = url
                    _state["area_retry_count"] = 0
    else:
        _state["fail_promo_list"] = []
        _state["area_retry_count"]=0

    # T020: Ticketmaster captcha integration (User Story 4)
    # https://ticketmaster.sg/ticket/check-captcha/23_blackpink/954/5/75
    if '/ticket/check-captcha/' in url:
        domain_name = url.split('/')[2]
        if 'ticketmaster' in domain_name:
            # Check if we already processed this captcha page (avoid repeated execution)
            ticketmaster_captcha_processed = _state.get("ticketmaster_captcha_processed_url", "")
            if ticketmaster_captcha_processed != url:
                # Call Ticketmaster captcha handler
                await nodriver_ticketmaster_captcha(tab, config_dict, ocr, Captcha_Browser)
                # Mark this URL as processed
                _state["ticketmaster_captcha_processed_url"] = url
    else:
        # Reset captcha processed state when leaving captcha page
        _state["ticketmaster_captcha_processed_url"] = ""

    if '/ticket/verify/' in url:
        # Tixcraft verify handler (already implemented)
        _state["fail_list"] = await nodriver_tixcraft_verify(tab, config_dict, _state["fail_list"])
    else:
        _state["fail_list"] = []

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        domain_name = url.split('/')[2]
        await nodriver_tixcraft_ticket_main(tab, config_dict, ocr, Captcha_Browser, domain_name)
        _state["done_time"] = time.time()

        if not _state["played_sound_ticket"]:
            if config_dict["advanced"]["play_sound"]["ticket"]:
                play_sound_while_ordering(config_dict)
        _state["played_sound_ticket"] = True
    else:
        _state["played_sound_ticket"] = False

    if '/ticket/order' in url:
        _state["done_time"] = time.time()

    is_quit_bot = False
    if '/ticket/checkout' in url:
        if not _state["start_time"] is None:
            if not _state["done_time"] is None:
                bot_elapsed_time = _state["done_time"] - _state["start_time"]
                if _state["elapsed_time"] != bot_elapsed_time:
                    print("bot elapsed time:", "{:.3f}".format(bot_elapsed_time))
                _state["elapsed_time"] = bot_elapsed_time

        # Always set is_quit_bot when checkout page is detected (not just in headless mode)
        if not _state["is_popup_checkout"]:
            is_quit_bot = True
            _state["is_popup_checkout"] = True

            # Issue #193: Move inside the block to execute only once on first checkout detection
            # Headless-specific behavior: open checkout URL in new browser window
            if config_dict["advanced"]["headless"]:
                domain_name = url.split('/')[2]
                checkout_url = "https://%s/ticket/checkout" % (domain_name)
                print("Ticket purchase successful, please check order at: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)

        if not _state["played_sound_order"]:
            if config_dict["advanced"]["play_sound"]["order"]:
                play_sound_while_ordering(config_dict)
            send_discord_notification(config_dict, "order", "TixCraft")
            send_telegram_notification(config_dict, "order", "TixCraft")
        _state["played_sound_order"] = True
    else:
        _state["is_popup_checkout"] = False
        _state["played_sound_order"] = False
        _state["printed_completed"] = False

    # Approach B: handle printed_completed internally
    if is_quit_bot:
        if not _state.get("printed_completed", False):
            print("TixCraft ticket purchase completed")
            _state["printed_completed"] = True

    return is_quit_bot

