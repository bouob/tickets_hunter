#encoding=utf-8
# =============================================================================
# iBon Platform Module
# Extracted from nodriver_tixcraft.py during modularization (Phase 1)
# Contains: ibon.com.tw, tour.ibon.com.tw (ibon family)
# =============================================================================

import asyncio
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
    create_universal_ocr,
    nodriver_check_checkbox,
    nodriver_current_url,
    nodriver_get_captcha_image_from_dom_snapshot,
    play_sound_while_ordering,
    send_discord_notification,
    send_telegram_notification,
    write_question_to_file,
    CONST_FROM_TOP_TO_BOTTOM,
    CONST_MAXBOT_ANSWER_ONLINE_FILE,
    CONST_MAXBOT_INT28_FILE,
    CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS,
    CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER,
)

# Backward-compatible alias (function moved to nodriver_common)
nodriver_ibon_get_captcha_image_from_shadow_dom = nodriver_get_captcha_image_from_dom_snapshot

__all__ = [
    "nodriver_ibon_login",
    "nodriver_ibon_date_auto_select_pierce",
    "nodriver_ibon_date_auto_select",
    "nodriver_ibon_date_auto_select_domsnapshot",
    "nodriver_ibon_ticket_agree",
    "nodriver_ibon_allow_not_adjacent_seat",
    "nodriver_ibon_event_area_auto_select",
    "nodriver_ibon_area_auto_select",
    "nodriver_ibon_ticket_number_auto_select",
    "nodriver_ibon_get_captcha_image_from_shadow_dom",  # alias for nodriver_get_captcha_image_from_dom_snapshot
    "nodriver_ibon_keyin_captcha_code",
    "nodriver_ibon_refresh_captcha",
    "nodriver_ibon_auto_ocr",
    "nodriver_ibon_captcha",
    "nodriver_ibon_purchase_button_press",
    "nodriver_ibon_check_sold_out",
    "nodriver_ibon_wait_for_select_elements",
    "nodriver_ibon_check_sold_out_on_ticket_page",
    "nodriver_ibon_navigate_on_sold_out",
    "nodriver_ibon_fill_verify_form",
    "nodriver_ibon_verification_question",
    "nodriver_tour_ibon_event_detail",
    "nodriver_tour_ibon_options",
    "nodriver_tour_ibon_checkout",
    "nodriver_ibon_main",
]

# Module-level state (replaces global ibon_dict)
_state = {}


async def nodriver_ibon_login(tab, config_dict, driver):
    """
    專門的 ibon 登入函數，整合 cookie 處理、頁面重新載入和登入狀態驗證
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("=== ibon Auto-Login Started ===")

    # 檢查是否有 ibon cookie 設定
    ibonqware = config_dict["accounts"]["ibonqware"]
    if len(ibonqware) <= 1:
        debug.log("No ibon cookie configured, skipping auto-login")
        return {'success': False, 'reason': 'no_cookie_configured'}

    debug.log(f"Setting ibon cookie (NoDriver) with length: {len(ibonqware)}")
    debug.log(f"Cookie contains mem_id: {'mem_id=' in ibonqware}")
    debug.log(f"Cookie contains mem_email: {'mem_email=' in ibonqware}")
    debug.log(f"Cookie contains huiwanTK: {'huiwanTK=' in ibonqware}")
    debug.log(f"Cookie contains ibonqwareverify: {'ibonqwareverify=' in ibonqware}")

    try:
        from zendriver import cdp

        # Set ibon cookie using CDP
        cookie_result = await tab.send(cdp.network.set_cookie(
            name="ibonqware",
            value=ibonqware,
            domain=".ibon.com.tw",
            path="/",
            secure=True,
            http_only=True
        ))

        debug.log(f"CDP setCookie result: {cookie_result}")
        debug.log("ibon cookie set successfully (NoDriver)")

        # 驗證 cookie 是否設定成功
        updated_cookies = await driver.cookies.get_all()
        ibon_cookies = [c for c in updated_cookies if c.name == 'ibonqware']
        if not ibon_cookies:
            debug.log("Warning: ibon cookie not found after setting")
            return {'success': False, 'reason': 'cookie_not_set'}

        debug.log(f"Verified: ibon cookie exists with value length: {len(ibon_cookies[0].value)}")
        debug.log(f"Cookie domain: {ibon_cookies[0].domain}")
        debug.log("[SUCCESS] ibon cookie set successfully")
        debug.log("[INFO] Cookie will be applied when navigating to event page")

        # No page reload needed - cookie is set on homepage,
        # and navigation to event page will automatically apply the cookie
        return {'success': True, 'reason': 'cookie_set'}

    except Exception as cookie_error:
        debug.log(f"[IBON LOGIN] Failed to set ibon cookie (NoDriver): {cookie_error}")
        if debug.enabled:
            import traceback
            traceback.print_exc()
        return {'success': False, 'reason': 'exception', 'error': str(cookie_error)}

async def nodriver_ibon_date_auto_select_pierce(tab, config_dict):
    """
    NoDriver ibon 日期自動選擇實作 - 使用 CDP pierce=True 參數
    直接穿透 Shadow DOM，比 DOMSnapshot 更簡潔高效

    使用 CDP DOM.query_selector_all(pierce=True) 直接查詢 Shadow DOM 中的按鈕
    參考：https://ultrafunkamsterdam.github.io/nodriver/nodriver/cdp/dom.html
    """
    from zendriver import cdp
    from zendriver.cdp import runtime
    import random
    import json

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)  # T017: Safe access for new field

    debug.log("[IBON DATE PIERCE] Starting date selection with pierce=True")
    debug.log("date_keyword:", date_keyword)
    debug.log("auto_select_mode:", auto_select_mode)

    # Step 1: Auto-detect buttons (no fixed wait - responds immediately when ready)
    debug.log("[IBON DATE PIERCE] Auto-detecting purchase buttons...")

    await tab  # Sync state

    # Initialize CDP DOM state (required for perform_search to work)
    try:
        await tab.send(cdp.dom.get_document(depth=0, pierce=False))
    except:
        pass

    # Auto-detect: fast polling until buttons found or timeout
    import time
    max_wait = 3  # Maximum wait (safety limit)
    check_interval = 0.1  # Fast polling for quick response
    start_time = time.time()
    button_found = False

    while (time.time() - start_time) < max_wait:
        try:
            # Use CDP search to check button presence (penetrates Shadow DOM)
            search_id, result_count = await tab.send(cdp.dom.perform_search(
                query='button.btn-buy',
                include_user_agent_shadow_dom=True
            ))

            # Clean up search
            try:
                await tab.send(cdp.dom.discard_search_results(search_id=search_id))
            except:
                pass

            if result_count > 0:
                button_found = True
                elapsed = time.time() - start_time
                debug.log(f"[IBON DATE PIERCE] Found {result_count} button(s) after {elapsed:.2f}s")
                break
        except:
            pass

        await tab.sleep(check_interval)

    if not button_found:
        elapsed = time.time() - start_time
        debug.log(f"[IBON DATE PIERCE] No buttons found after {elapsed:.1f}s, proceeding with search anyway...")

    # Step 4: Get document with pierce=True to enable Shadow DOM traversal
    # Use shallow depth to avoid CBOR stack overflow on complex pages
    try:
        doc_result = await tab.send(cdp.dom.get_document(depth=0, pierce=False))
        root_node_id = doc_result.node_id
        debug.log(f"[IBON DATE PIERCE] Got document root: {root_node_id}")
    except Exception as e:
        debug.log(f"[IBON DATE PIERCE] Failed to get document: {e}")
        return False

    # Step 5: Use perform_search with pierce capability
    # Note: query_selector_all doesn't support pierce in current NoDriver version
    # Use perform_search which can traverse Shadow DOM
    try:
        # Perform search to find buttons (automatically pierces Shadow DOM)
        search_id, result_count = await tab.send(cdp.dom.perform_search(
            query='button.btn-buy',
            include_user_agent_shadow_dom=True
        ))

        debug.log(f"[IBON DATE PIERCE] Found {result_count} button(s) via search")

        if result_count == 0:
            debug.log("[IBON DATE PIERCE] No purchase buttons found")
            # Cleanup search
            try:
                await tab.send(cdp.dom.discard_search_results(search_id=search_id))
            except:
                pass
            return False

        # Get search results (node IDs)
        button_node_ids = await tab.send(cdp.dom.get_search_results(
            search_id=search_id,
            from_index=0,
            to_index=result_count
        ))

        # Cleanup search
        try:
            await tab.send(cdp.dom.discard_search_results(search_id=search_id))
        except:
            pass

    except Exception as e:
        debug.log(f"[IBON DATE PIERCE] perform_search failed: {e}")
        return False

    # Step 5: Extract button data and date context
    purchase_buttons = []

    for node_id in button_node_ids:
        try:
            # Describe button node to get attributes
            node_desc = await tab.send(cdp.dom.describe_node(node_id=node_id))
            # node_desc directly contains the node info, not wrapped in .node
            node = node_desc if hasattr(node_desc, 'attributes') else node_desc.node

            # Parse attributes
            attrs = {}
            if hasattr(node, 'attributes') and node.attributes:
                for i in range(0, len(node.attributes), 2):
                    if i + 1 < len(node.attributes):
                        attrs[node.attributes[i]] = node.attributes[i + 1]

            button_class = attrs.get('class', '')
            button_disabled = 'disabled' in attrs

            # Extract date context by traversing up to find .tr container
            date_context = ''

            # Start from button's parent (not the button itself)
            try:
                button_desc = await tab.send(cdp.dom.describe_node(node_id=node_id))
                button_node = button_desc if hasattr(button_desc, 'attributes') else button_desc.node

                # Get parent_id to start traversal
                if not hasattr(button_node, 'parent_id') or not button_node.parent_id:
                    current_node_id = None
                else:
                    current_node_id = button_node.parent_id  # Start from parent, not button itself
            except Exception:
                current_node_id = None

            if current_node_id:
                for level in range(10):  # Max 10 levels up (now starting from parent = level 1)
                    try:
                        parent_desc = await tab.send(cdp.dom.describe_node(node_id=current_node_id))
                        # Same fix: node_desc might be the node itself
                        parent_node = parent_desc if hasattr(parent_desc, 'attributes') else parent_desc.node

                        # Parse parent attributes
                        parent_attrs = {}
                        if hasattr(parent_node, 'attributes') and parent_node.attributes:
                            for i in range(0, len(parent_node.attributes), 2):
                                if i + 1 < len(parent_node.attributes):
                                    parent_attrs[parent_node.attributes[i]] = parent_node.attributes[i + 1]

                        parent_class = parent_attrs.get('class', '')

                        # Check if this is .tr container (flexible matching)
                        is_tr_container = (
                            ' tr ' in f' {parent_class} ' or
                            parent_class.endswith(' tr') or
                            parent_class.startswith('tr ') or
                            'd-flex' in parent_class  # ibon uses d-flex for containers
                        )

                        if is_tr_container:
                            # Found potential container, extract outer HTML for date context
                            try:
                                outer_html = await tab.send(cdp.dom.get_outer_html(node_id=current_node_id))
                                date_context = outer_html[:200]  # Use first 200 chars
                                break
                            except Exception:
                                pass

                        # Move up to parent
                        if hasattr(parent_node, 'parent_id') and parent_node.parent_id:
                            current_node_id = parent_node.parent_id
                        else:
                            break

                    except Exception:
                        break

            purchase_buttons.append({
                'node_id': node_id,
                'class': button_class,
                'disabled': button_disabled,
                'date_context': date_context
            })

        except Exception as e:
            debug.log(f"[IBON DATE PIERCE] Failed to process button: {e}")
            continue

    if len(purchase_buttons) == 0:
        debug.log("[IBON DATE PIERCE] No valid buttons extracted")
        return False

    # Step 6: Filter disabled buttons
    enabled_buttons = [btn for btn in purchase_buttons if not btn['disabled']]

    debug.log(f"[IBON DATE PIERCE] {len(enabled_buttons)} enabled button(s)")

    if len(enabled_buttons) == 0:
        debug.log("[IBON DATE PIERCE] All buttons disabled")
        return False

    # Step 7: Apply keyword matching with early return pattern (T004-T007)
    matched_buttons = []
    target_found = False

    if len(date_keyword) > 0 and enabled_buttons:
        keyword_array = util.parse_keyword_string_to_array(date_keyword)
        debug.log(f"[IBON DATE PIERCE KEYWORD] Start checking keywords in order: {keyword_array}")

        # NEW: Iterate keywords in priority order (early return)
        for keyword_index, keyword_item in enumerate(keyword_array):
            debug.log(f"[IBON DATE PIERCE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item}")

            # Check all buttons for this keyword
            for button in enabled_buttons:
                date_context = button.get('date_context', '').lower()
                sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                is_match = all(sub_kw.lower() in date_context for sub_kw in sub_keywords)

                if is_match:
                    # T006: Keyword matched log - IMMEDIATELY select and stop
                    matched_buttons = [button]
                    target_found = True
                    debug.log(f"[IBON DATE PIERCE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item}'")
                    debug.log(f"[IBON DATE PIERCE SELECT] Selected date: {date_context[:50]} (keyword match)")
                    break

            if target_found:
                # EARLY RETURN: Stop checking further keywords
                break

        # T007: All keywords failed log
        if not target_found:
            debug.log(f"[IBON DATE PIERCE KEYWORD] All keywords failed to match")
    else:
        matched_buttons = enabled_buttons

    # Step 8: Conditional fallback based on date_auto_fallback switch (T018-T020)
    if len(matched_buttons) == 0 and len(date_keyword) > 0:
        if date_auto_fallback:
            # T018: Fallback enabled
            debug.log(f"[IBON DATE PIERCE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            matched_buttons = enabled_buttons
        else:
            # T019: Fallback disabled - strict mode (no selection, will reload)
            debug.log(f"[IBON DATE PIERCE FALLBACK] date_auto_fallback=false, fallback is disabled")
            debug.log(f"[IBON DATE PIERCE SELECT] No date selected, will reload page and retry")
            return False  # Return False to trigger reload logic in caller

    # Step 9: Select target based on mode
    target_button = util.get_target_item_from_matched_list(matched_buttons, auto_select_mode)

    # T013: Log selected date with selection type
    if debug.enabled:
        is_keyword_match = (len(date_keyword) > 0 and len(matched_buttons) < len(enabled_buttons))
        selection_type = "keyword match" if is_keyword_match else "fallback"
        debug.log(f"[IBON DATE PIERCE SELECT] Selected date: {target_button.get('date_context', 'N/A')} ({selection_type})")

    # Step 10: Click button using CDP
    try:
        # Scroll into view
        await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=target_button['node_id']))
        await tab.sleep(0.2)

        # Resolve node to RemoteObject
        resolved = await tab.send(cdp.dom.resolve_node(node_id=target_button['node_id']))

        if hasattr(resolved, 'object'):
            remote_object_id = resolved.object.object_id
        elif hasattr(resolved, 'object_id'):
            remote_object_id = resolved.object_id
        else:
            raise Exception("Could not get object_id")

        # Click using JavaScript
        result = await tab.send(runtime.call_function_on(
            function_declaration='function() { this.click(); return true; }',
            object_id=remote_object_id,
            return_by_value=True
        ))

        debug.log(f"[IBON DATE PIERCE] Click result: {result}")
        debug.log("[IBON DATE PIERCE] Button clicked successfully")

        await tab.sleep(0.5)
        return True

    except Exception as e:
        debug.log(f"[IBON DATE PIERCE] Click failed: {e}")
        return False

async def nodriver_ibon_date_auto_select(tab, config_dict):
    """
    NoDriver ibon 日期自動選擇實作 - 主入口（包含 fallback）

    優先使用 pierce=True 方法（更快、更簡潔）
    失敗時回退到 DOMSnapshot 方法（更穩定但較慢）
    """
    debug = util.create_debug_logger(config_dict)

    # Try pierce method first (faster)
    try:
        result = await nodriver_ibon_date_auto_select_pierce(tab, config_dict)
        if result:
            return True
        else:
            debug.log("[IBON DATE] pierce method failed, trying DOMSnapshot fallback...")
    except Exception as e:
        debug.log(f"[IBON DATE] pierce method error: {e}, trying DOMSnapshot fallback...")

    # Fallback to original DOMSnapshot method
    return await nodriver_ibon_date_auto_select_domsnapshot(tab, config_dict)

async def nodriver_ibon_date_auto_select_domsnapshot(tab, config_dict):
    """
    NoDriver ibon 日期自動選擇實作 - DOMSnapshot 回退版本
    使用 CDP DOMSnapshot 穿透 closed Shadow DOM 搜尋購票按鈕
    參考：NoDriver API Guide 範例 1
    """
    from zendriver import cdp
    from zendriver.cdp import input_ as cdp_input
    import random

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    date_auto_fallback = config_dict.get('date_auto_fallback', False)  # T017: Safe access for new field
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    debug.log("[IBON DATE] Starting date selection on ActivityInfo/Details page")
    debug.log("date_keyword:", date_keyword)
    debug.log("auto_select_mode:", auto_select_mode)

    is_date_assigned = False

    # Auto-detect buttons (no fixed wait - responds immediately when ready)
    # IMPORTANT: get_document() must be called before perform_search() to initialize CDP DOM state
    try:
        await tab.send(cdp.dom.get_document(depth=0, pierce=False))
    except:
        pass

    import time
    max_wait = 3  # Maximum wait (safety limit)
    check_interval = 0.1  # Fast polling for quick response
    start_time = time.time()
    content_appeared = False

    debug.log("[IBON DATE] Auto-detecting purchase buttons...")

    while (time.time() - start_time) < max_wait:
        try:
            # Use CDP search to check button presence (penetrates Shadow DOM, same as pierce method)
            search_id, result_count = await tab.send(cdp.dom.perform_search(
                query='button.btn-buy',
                include_user_agent_shadow_dom=True
            ))

            # Clean up search
            try:
                await tab.send(cdp.dom.discard_search_results(search_id=search_id))
            except:
                pass

            if result_count > 0:
                content_appeared = True
                elapsed = time.time() - start_time
                debug.log(f"[IBON DATE] Found {result_count} purchase button(s) after {elapsed:.2f}s")
                break
        except:
            pass
        await tab.sleep(check_interval)

    if not content_appeared:
        elapsed = time.time() - start_time
        debug.log(f"[IBON DATE] No buttons found after {elapsed:.1f}s, proceeding with snapshot anyway...")

    # Capture DOM snapshot to penetrate closed Shadow DOM and search for purchase buttons
    debug.log("[IBON DATE] Capturing DOM snapshot with CDP...")

    try:
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_dom_rects=True
        ))
    except Exception as e:
        debug.log(f"[IBON DATE] Error capturing snapshot: {e}")
        return False

    purchase_buttons = []

    if documents and len(documents) > 0:
        debug.log(f"[IBON DATE] Analyzing {len(documents)} document(s)...")

        document_snapshot = documents[0]
        nodes = document_snapshot.nodes

        node_names = [strings[i] for i in nodes.node_name]
        node_values = [strings[i] if i >= 0 else '' for i in nodes.node_value]
        attributes_list = nodes.attributes
        backend_node_ids = list(nodes.backend_node_id)

        debug.log(f"[IBON DATE] Total nodes in snapshot: {len(node_names)}")

        # Step 1: Extract parent_index for tracking node relationships
        parent_indices = list(nodes.parent_index) if hasattr(nodes, 'parent_index') else []

        # Debug: Count all buttons found
        button_count = sum(1 for name in node_names if name.upper() == 'BUTTON')
        debug.log(f"[IBON DATE] Total BUTTON nodes found: {button_count}")

        # Step 2: Search for purchase buttons and extract date context
        for i, node_name in enumerate(node_names):
            if node_name.upper() == 'BUTTON':
                attrs = {}
                if i < len(attributes_list):
                    attr_indices = attributes_list[i]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key = strings[attr_indices[j]]
                            val = strings[attr_indices[j + 1]]
                            attrs[key] = val

                button_class = attrs.get('class', '')
                button_disabled = 'disabled' in attrs

                # ibon purchase buttons have 'btn-buy' or 'ng-tns-c57' in class
                if 'btn-buy' in button_class or ('ng-tns-c57' in button_class and 'btn' in button_class):
                    # Get button text from adjacent text nodes
                    button_text = ''
                    if i + 1 < len(node_names) and node_names[i + 1] == '#text':
                        button_text = node_values[i + 1].strip()

                    # Step 3: Extract date context by finding parent .tr container
                    date_context = ''
                    if parent_indices:
                        # Traverse up to find .tr container
                        current_idx = i
                        tr_container_idx = -1
                        for _ in range(10):  # Max 10 levels up
                            if current_idx < len(parent_indices):
                                parent_idx = parent_indices[current_idx]
                                if parent_idx >= 0 and parent_idx < len(attributes_list):
                                    # Check if this parent has class='tr' or class contains 'tr'
                                    parent_attrs = {}
                                    parent_attr_indices = attributes_list[parent_idx]
                                    for j in range(0, len(parent_attr_indices), 2):
                                        if j + 1 < len(parent_attr_indices):
                                            key = strings[parent_attr_indices[j]]
                                            val = strings[parent_attr_indices[j + 1]]
                                            parent_attrs[key] = val

                                    parent_class = parent_attrs.get('class', '')
                                    if ' tr ' in f' {parent_class} ' or parent_class.endswith(' tr') or parent_class.startswith('tr '):
                                        tr_container_idx = parent_idx
                                        break

                                current_idx = parent_idx
                            else:
                                break

                        # Step 4: Find .date element within .tr container
                        if tr_container_idx >= 0:
                            # Search siblings and children of .tr container for .date element
                            for j in range(len(node_names)):
                                if parent_indices[j] == tr_container_idx or parent_indices[j] == i:
                                    # Check if this node has class='date' or class contains 'date'
                                    if j < len(attributes_list):
                                        node_attrs = {}
                                        node_attr_indices = attributes_list[j]
                                        for k in range(0, len(node_attr_indices), 2):
                                            if k + 1 < len(node_attr_indices):
                                                key = strings[node_attr_indices[k]]
                                                val = strings[node_attr_indices[k + 1]]
                                                node_attrs[key] = val

                                        node_class = node_attrs.get('class', '')
                                        if 'date' in node_class:
                                            # Extract text content from this node's children
                                            for text_idx in range(j + 1, min(j + 10, len(node_names))):
                                                if node_names[text_idx] == '#text':
                                                    date_text = node_values[text_idx].strip()
                                                    if date_text:
                                                        date_context = date_text
                                                        break
                                            if date_context:
                                                break

                    purchase_buttons.append({
                        'backend_node_id': backend_node_ids[i],
                        'class': button_class,
                        'disabled': button_disabled,
                        'text': button_text,
                        'index': i,
                        'date_context': date_context
                    })

                    debug.log(f"[IBON DATE] Found button: class='{button_class[:50]}...', disabled={button_disabled}, text='{button_text}', date_context='{date_context}'")

    debug.log(f"[IBON DATE] Found {len(purchase_buttons)} purchase button(s)")

    if len(purchase_buttons) == 0:
        debug.log("[IBON DATE] No purchase buttons found in Shadow DOM")
        return False

    # Step 5: Filter disabled buttons
    enabled_buttons = [btn for btn in purchase_buttons if not btn['disabled']]

    debug.log(f"[IBON DATE] Found {len(enabled_buttons)} enabled button(s)")

    if len(enabled_buttons) == 0:
        debug.log("[IBON DATE] All buttons are disabled")
        return False

    # Step 6: Apply keyword matching with early return pattern (T004-T007)
    # Unified keyword processing: JSON array parsing with AND/OR logic
    # Format: "AA BB","CC","DD" -> (AA AND BB) OR (CC) OR (DD)
    matched_buttons = []
    target_found = False

    if len(date_keyword) > 0 and enabled_buttons:
        # Parse as JSON array (auto-removes quotes)
        keyword_array = util.parse_keyword_string_to_array(date_keyword)
        debug.log(f"[IBON DATE KEYWORD] Start checking keywords in order: {keyword_array}")

        # NEW: Iterate keywords in priority order (early return)
        for keyword_index, keyword_item in enumerate(keyword_array):
            debug.log(f"[IBON DATE KEYWORD] Checking keyword #{keyword_index + 1}: {keyword_item}")

            # Check all buttons for this keyword
            for button in enabled_buttons:
                button_text = button.get('text', '').lower()
                date_context = button.get('date_context', '').lower()
                search_text = f"{button_text} {date_context}"

                # Split by space for AND logic (e.g., "AA BB" means AA AND BB)
                sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                # Check if all sub-keywords match (AND logic within group)
                is_match = all(sub_kw.lower() in search_text for sub_kw in sub_keywords)

                if is_match:
                    # T006: Keyword matched log - IMMEDIATELY select and stop
                    matched_buttons = [button]
                    target_found = True
                    debug.log(f"[IBON DATE KEYWORD] Keyword #{keyword_index + 1} matched: '{keyword_item}'")
                    debug.log(f"[IBON DATE SELECT] Selected date: {date_context[:50]} (keyword match)")
                    break

            if target_found:
                # EARLY RETURN: Stop checking further keywords
                break

        # T007: All keywords failed log
        if not target_found:
            debug.log(f"[IBON DATE KEYWORD] All keywords failed to match")
    else:
        matched_buttons = enabled_buttons

    # Step 7: Conditional fallback based on date_auto_fallback switch (T018-T020)
    if len(matched_buttons) == 0 and len(date_keyword) > 0:
        if date_auto_fallback:
            # T018: Fallback enabled - use auto_select_mode
            debug.log(f"[IBON DATE FALLBACK] date_auto_fallback=true, triggering auto fallback")
            debug.log(f"[IBON DATE FALLBACK] Selecting available date based on date_select_order='{auto_select_mode}'")
            matched_buttons = enabled_buttons
        else:
            # T019: Fallback disabled - strict mode (no selection, will reload)
            debug.log(f"[IBON DATE FALLBACK] date_auto_fallback=false, fallback is disabled")
            debug.log(f"[IBON DATE SELECT] No date selected, will reload page and retry")
            return False  # Return False to trigger reload logic in caller

    # Step 8: Select target button based on mode
    target_button = util.get_target_item_from_matched_list(matched_buttons, auto_select_mode)

    # Determine selection method (T013 equivalent)
    is_keyword_match = (len(date_keyword) > 0 and len(matched_buttons) < len(enabled_buttons))
    selection_type = "keyword match" if is_keyword_match else "fallback"
    selection_method = selection_type if is_keyword_match else f"mode '{auto_select_mode}'"

    debug.log(f"[IBON DATE SELECT] Selected date: {target_button.get('date_context', 'N/A')} ({selection_type})")
    debug.log(f"[IBON DATE] Selected target button ({selection_method}): date_context='{target_button.get('date_context', 'N/A')}'")

    try:
        await tab.send(cdp.dom.get_document())

        # Convert backend_node_id to node_id
        result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend([target_button['backend_node_id']]))
        node_id = result[0]

        debug.log(f"[IBON DATE] Button node_id: {node_id}")

        # Scroll element into view
        await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
        await tab.sleep(0.2)

        # Use CDP Runtime.callFunctionOn to click button in closed Shadow DOM
        from zendriver.cdp import runtime

        # Resolve node to RemoteObject
        resolved = await tab.send(cdp.dom.resolve_node(node_id=node_id))

        # resolved should have an 'object' field containing the RemoteObject
        # But based on error, try accessing object_id directly
        if hasattr(resolved, 'object'):
            remote_object_id = resolved.object.object_id
        elif hasattr(resolved, 'object_id'):
            remote_object_id = resolved.object_id
        else:
            # Debug: print the actual structure
            debug.log(f"[IBON DATE] Resolved structure: {resolved}")
            debug.log(f"[IBON DATE] Resolved type: {type(resolved)}")
            debug.log(f"[IBON DATE] Resolved attributes: {dir(resolved)}")
            raise Exception("Could not find object_id in resolved node")

        debug.log(f"[IBON DATE] Resolved button object_id: {remote_object_id}")

        result = await tab.send(runtime.call_function_on(
            function_declaration='function() { this.click(); return true; }',
            object_id=remote_object_id,
            return_by_value=True
        ))

        debug.log(f"[IBON DATE] Button clicked, result: {result}")

        if result:
            debug.log("[IBON DATE] Purchase button clicked successfully")
            is_date_assigned = True
            await tab.sleep(0.5)
        else:
            debug.log("[IBON DATE] Click failed")

    except Exception as e:
        debug.log(f"[IBON DATE] Error clicking button: {e}")
        is_date_assigned = False

    return is_date_assigned

async def nodriver_ibon_ticket_agree(tab):
    for i in range(3):
        is_finish_checkbox_click = await nodriver_check_checkbox(tab, '#agreen:not(:checked)')
        if is_finish_checkbox_click:
            break

async def nodriver_ibon_allow_not_adjacent_seat(tab, config_dict):
    """
    Check and click the 'allow non-adjacent seats' checkbox on ibon

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if checkbox was clicked successfully, False otherwise
    """
    debug = util.create_debug_logger(config_dict)

    is_finish_checkbox_click = False

    # Selector for non-adjacent seat checkbox
    checkbox_selector = 'div.not-consecutive > div.custom-control > span > input[type="checkbox"]:not(:checked)'

    try:
        for i in range(3):
            is_finish_checkbox_click = await nodriver_check_checkbox(tab, checkbox_selector)
            if is_finish_checkbox_click:
                debug.log("[IBON] Non-adjacent seat checkbox clicked")
                break
    except Exception as e:
        debug.log(f"[IBON] Non-adjacent seat checkbox error: {e}")

    return is_finish_checkbox_click

async def nodriver_ibon_event_area_auto_select(tab, config_dict, area_keyword_item=""):
    """
    ibon seat area auto-selection for NEW Event page format (NoDriver version)

    Handles seat area selection on /Event/{id}/{id} page (Angular SPA).
    Uses DOMSnapshot for data extraction and CDP for clicking.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        area_keyword_item: Area keyword string (space-separated for AND logic)

    Returns:
        tuple: (is_need_refresh, is_price_assign_by_bot)
            - is_need_refresh: Whether page refresh is needed
            - is_price_assign_by_bot: Whether area selection succeeded
    """
    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get('area_auto_fallback', False)  # T021: Safe access for new field
    ticket_number = config_dict["ticket_number"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    debug.log("[ibon] 區域選擇開始")

    # Optimized wait for Angular app to fully load (reduced from 2.3-2.7s to 1.0-1.4s)
    try:
        import random
        wait_time = random.uniform(0.6, 0.8)
        await tab.sleep(wait_time)
        # Reduced second wait (1.5s -> 0.6s) - total now 1.2-1.4s instead of 2.3-2.7s
        await tab.sleep(0.6)
    except:
        pass

    # Phase 1: Extract all area data using DOMSnapshot (to pierce Shadow DOM if present)
    try:
        from zendriver import cdp

        # Use DOMSnapshot to get flattened page structure
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_paint_order=True,
            include_dom_rects=True
        ))

        areas_data = []

        if documents and len(documents) > 0:
            document_snapshot = documents[0]

            # Extract node information
            node_names = []
            node_values = []
            parent_indices = []
            attributes_list = []
            backend_node_ids = []

            if hasattr(document_snapshot, 'nodes'):
                nodes = document_snapshot.nodes
                if hasattr(nodes, 'node_name'):
                    node_names = [strings[i] if isinstance(i, int) and i < len(strings) else str(i)
                                 for i in nodes.node_name]
                if hasattr(nodes, 'node_value'):
                    node_values = [strings[i] if isinstance(i, int) and i >= 0 and i < len(strings) else ''
                                  for i in nodes.node_value]
                if hasattr(nodes, 'parent_index'):
                    parent_indices = list(nodes.parent_index)
                if hasattr(nodes, 'attributes'):
                    attributes_list = nodes.attributes
                if hasattr(nodes, 'backend_node_id'):
                    backend_node_ids = list(nodes.backend_node_id)

            # Build children map for traversal
            children_map = {}
            for i, parent_idx in enumerate(parent_indices):
                if parent_idx >= 0:
                    if parent_idx not in children_map:
                        children_map[parent_idx] = []
                    children_map[parent_idx].append(i)

            # Helper function to get attributes as dict
            def get_attributes_dict(node_index):
                attrs = {}
                if node_index < len(attributes_list):
                    attr_indices = attributes_list[node_index]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key_idx = attr_indices[j]
                            val_idx = attr_indices[j + 1]
                            key = strings[key_idx] if key_idx < len(strings) else ''
                            val = strings[val_idx] if val_idx < len(strings) else ''
                            attrs[key] = val
                return attrs

            # Helper function to get all text content from node and its children
            def get_text_content(node_index, depth=0, max_depth=10):
                if depth > max_depth or node_index >= len(node_names):
                    return ''

                text_parts = []

                # If this is a text node, get its value
                if node_names[node_index] == '#text' and node_index < len(node_values):
                    text_parts.append(node_values[node_index])

                # Recursively get text from children
                if node_index in children_map:
                    for child_idx in children_map[node_index]:
                        child_text = get_text_content(child_idx, depth + 1, max_depth)
                        if child_text:
                            text_parts.append(child_text)

                return ' '.join(text_parts).strip()

            # Find all TR elements in the table
            tr_indices = []
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'TR':
                    tr_indices.append(i)

            # Extract data from each TR
            area_index = 0
            tr_count = 0
            for tr_idx in tr_indices:
                # Get TR attributes
                tr_attrs = get_attributes_dict(tr_idx)
                tr_class = tr_attrs.get('class', '')

                # Skip header rows (check if parent is THEAD)
                parent_idx = parent_indices[tr_idx] if tr_idx < len(parent_indices) else -1
                is_header = False
                if parent_idx >= 0 and parent_idx < len(node_names):
                    parent_name = node_names[parent_idx].upper()
                    if parent_name == 'THEAD':
                        is_header = True

                if is_header:
                    continue

                is_disabled = 'disabled' in tr_class.lower()

                # Find TD children
                td_indices = []
                if tr_idx in children_map:
                    for child_idx in children_map[tr_idx]:
                        if node_names[child_idx].upper() == 'TD':
                            td_indices.append(child_idx)

                # Get backend_node_id for this TR
                tr_backend_node_id = None
                if tr_idx < len(backend_node_ids):
                    tr_backend_node_id = backend_node_ids[tr_idx]

                tr_count += 1

                # Detect "giant TR" pattern (ibon Event page uses 1 TR with all areas)
                # Pattern: [color, area_name, price, seat_status] x N areas
                if len(td_indices) > 10:
                    # Giant TR: loop through TDs in groups of 4
                    for i in range(0, len(td_indices), 4):
                        if i + 3 < len(td_indices):
                            # Extract this group of 4 TDs
                            td_texts = [
                                get_text_content(td_indices[i]),     # color
                                get_text_content(td_indices[i+1]),   # area_name
                                get_text_content(td_indices[i+2]),   # price
                                get_text_content(td_indices[i+3])    # seat_status
                            ]

                            # Skip empty TDs (color-tag TDs may be empty)
                            area_name = td_texts[1].strip()
                            if len(area_name) == 0:
                                continue

                            price = td_texts[2].strip()
                            seat_text = td_texts[3].strip()

                            # For giant TR, determine disabled from seat_text
                            # (cannot use TR class since all areas share the same TR)
                            is_area_disabled = ('已售完' in seat_text)

                            # Build area data object
                            area_data = {
                                'index': area_index,
                                'disabled': is_area_disabled,
                                'areaName': area_name,
                                'price': price,
                                'seatText': seat_text,
                                'innerHTML': f'<tr><td>{area_name}</td><td>{price}</td><td>{seat_text}</td></tr>',
                                'tr_node_index': tr_idx,
                                'backend_node_id': tr_backend_node_id
                            }
                            areas_data.append(area_data)
                            area_index += 1
                else:
                    # Standard TR structure: each TR = 1 area
                    # Expected order: [0]=color, [1]=area_name, [2]=price, [3]=seat_status
                    td_texts = []
                    for td_idx in td_indices:
                        td_text = get_text_content(td_idx)
                        td_texts.append(td_text)

                    if len(td_texts) >= 4:
                        area_name = td_texts[1].strip()
                        price = td_texts[2].strip()
                        seat_text = td_texts[3].strip()

                        # Build area data object
                        area_data = {
                            'index': area_index,
                            'disabled': is_disabled,
                            'areaName': area_name,
                            'price': price,
                            'seatText': seat_text,
                            'innerHTML': f'<tr class="{tr_class}"><td>{area_name}</td><td>{price}</td><td>{seat_text}</td></tr>',
                            'tr_node_index': tr_idx,
                            'backend_node_id': tr_backend_node_id
                        }
                        areas_data.append(area_data)
                        area_index += 1

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[NEW EVENT ERROR] Failed to extract area data: {exc}")
            import traceback
            traceback.print_exc()
        return True, False

    if not areas_data or len(areas_data) == 0:
        debug.log("[ibon] 頁面無區域")
        return True, False

    # Debug extraction (disabled by default)
    # if debug.enabled:
    #     print(f"[IBON EXTRACT DEBUG] Total extracted areas: {len(areas_data)}")

    # Phase 2: Filter areas (disabled, sold out, insufficient seats)
    valid_areas = []

    for area in areas_data:
        # Skip disabled areas
        if area['disabled']:
            debug.log(f"[ibon] 跳過: {area['areaName']}")
            continue

        # 同時檢查區域名稱、票價與內容
        row_text = area['areaName'] + ' ' + area.get('price', '') + ' ' + util.remove_html_tags(area['innerHTML'])

        # Skip sold out areas
        if '已售完' in area['seatText']:
            debug.log(f"[ibon] 已售完: {area['areaName']}")
            continue

        # Check exclude keywords
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            debug.log(f"[ibon] 排除: {area['areaName']}")
            continue

        # Check remaining seat count
        seat_text = area['seatText']
        if seat_text.isdigit():
            remaining_seats = int(seat_text)
            if remaining_seats < ticket_number:
                debug.log(f"[ibon] 座位不足: {area['areaName']} ({remaining_seats}/{ticket_number})")
                continue

        valid_areas.append(area)

    debug.log(f"[ibon] 有效區域: {len(valid_areas)}")

    # Phase 3: Keyword matching with early return pattern (T010-T016)
    matched_areas = []
    target_found = False

    if area_keyword_item and len(area_keyword_item) > 0:
        try:
            # NOTE: area_keyword_item is already a SINGLE keyword string from upper layer
            # Upper layer (line 11225) splits by comma using JSON parsing:
            #   Input: "\"5600\",\"5,600\""
            #   After JSON: ["5600", "5,600"]
            #   This function is called once per keyword: "5600" or "5,600"
            #
            # DO NOT split by comma again here, or "5,600" becomes ['5', '600'] (BUG!)
            # Only support space-separated AND logic within each keyword

            area_keyword_clean = area_keyword_item.strip()
            if area_keyword_clean.startswith('"') and area_keyword_clean.endswith('"'):
                area_keyword_clean = area_keyword_clean[1:-1]

            # Treat the entire string as a single keyword
            keyword_item = util.format_keyword_string(area_keyword_clean)

            if debug.enabled:
                debug.log(f"[IBON EVENT AREA KEYWORD] Checking keyword: {keyword_item}")
                debug.log(f"[IBON EVENT AREA KEYWORD] Total valid areas: {len(valid_areas)}")
                if len(valid_areas) > 0:
                    debug.log(f"[IBON EVENT AREA KEYWORD] First 5 areas: {[a['areaName'] for a in valid_areas[:5]]}")

            # Check all areas for this keyword
            for area in valid_areas:
                row_text = area['areaName'] + ' ' + area.get('price', '') + ' ' + util.remove_html_tags(area['innerHTML'])
                row_text = util.format_keyword_string(row_text)

                # Support AND logic with space-separated sub-keywords
                # Example: "VIP 區" → ['VIP', '區'] → must match both
                sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                is_match = all(sub_kw.lower() in row_text.lower() for sub_kw in sub_keywords)

                if is_match:
                    # Keyword matched - IMMEDIATELY select and stop
                    matched_areas = [area]
                    target_found = True
                    debug.log(f"[IBON EVENT AREA KEYWORD] Keyword matched: '{keyword_item}'")
                    debug.log(f"[IBON EVENT AREA SELECT] Selected area: {area['areaName']} (keyword match)")
                    break

            # All keywords failed log
            if not target_found:
                debug.log(f"[IBON EVENT AREA KEYWORD] Keyword '{keyword_item}' failed to match")
        except Exception as e:
            debug.log(f"[IBON EVENT AREA] Keyword parse error: {e}")
            debug.log(f"[IBON EVENT AREA] Treating as 'all keywords failed'")
            matched_areas = []  # Let Feature 003 fallback logic handle this
    else:
        matched_areas = valid_areas

    if not target_found:
        debug.log(f"[IBON EVENT AREA] Total matched areas: {len(matched_areas)}")

    # T022-T024: Conditional fallback based on area_auto_fallback switch
    if len(matched_areas) == 0 and area_keyword_item and len(area_keyword_item) > 0:
        if area_auto_fallback:
            # T022: Fallback enabled - use all valid areas
            debug.log(f"[IBON EVENT AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
            debug.log(f"[IBON EVENT AREA FALLBACK] Selecting available area based on area_select_order='{auto_select_mode}'")
            matched_areas = valid_areas
        else:
            # T023: Fallback disabled - strict mode (no selection, will reload)
            debug.log(f"[IBON EVENT AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            debug.log(f"[IBON EVENT AREA SELECT] No area selected, will reload page and retry")
            # T024: No available options after keyword matching failed
            if len(valid_areas) == 0:
                debug.log(f"[IBON EVENT AREA FALLBACK] No available options after exclusion")
            is_need_refresh = True
            return is_need_refresh, False

    # Phase 4: Select target area based on mode
    target_area = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)

    if not target_area:
        is_need_refresh = True
        debug.log("[ibon] 選擇失敗")
        return is_need_refresh, False

    debug.log(f"[ibon] 已選: {target_area['areaName']}")

    # Phase 5: Click target area using CDP
    try:
        from zendriver import cdp

        debug.log(f"[NEW EVENT CDP CLICK] Starting CDP click for area: {target_area['areaName']}")

        backend_node_id = target_area.get('backend_node_id')

        if not backend_node_id:
            debug.log(f"[NEW EVENT CDP CLICK] No backend_node_id available for TR")
            return is_need_refresh, is_price_assign_by_bot

        # Request document first
        try:
            document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
            debug.log(f"[NEW EVENT CDP CLICK] Requested document with pierce=True")
        except Exception as doc_exc:
            debug.log(f"[NEW EVENT CDP CLICK] Document request failed: {doc_exc}")
            return is_need_refresh, is_price_assign_by_bot

        # Convert backend_node_id to node_id
        try:
            result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(backend_node_ids=[backend_node_id]))
            node_ids = result if isinstance(result, list) else (result.node_ids if hasattr(result, 'node_ids') else [])

            if not node_ids or len(node_ids) == 0:
                debug.log(f"[NEW EVENT CDP CLICK] Failed to convert backend_node_id to node_id")
                return is_need_refresh, is_price_assign_by_bot

            node_id = node_ids[0]

            debug.log(f"[NEW EVENT CDP CLICK] Node ID: {node_id}")

            # Scroll into view
            try:
                await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                debug.log(f"[NEW EVENT CDP CLICK] Scrolled element into view")
            except Exception as e:
                debug.log(f"[NEW EVENT CDP CLICK] Scroll warning: {e}")

            # Focus element
            try:
                await tab.send(cdp.dom.focus(node_id=node_id))
                debug.log(f"[NEW EVENT CDP CLICK] Focused element")
            except Exception as e:
                debug.log(f"[NEW EVENT CDP CLICK] Focus warning: {e}")

            # Get box model
            box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
            debug.log(f"[NEW EVENT CDP CLICK] Got box model")

            # Calculate center point
            content_quad = box_model.content if hasattr(box_model, 'content') else box_model.model.content
            x = (content_quad[0] + content_quad[2]) / 2
            y = (content_quad[1] + content_quad[5]) / 2

            debug.log(f"[NEW EVENT CDP CLICK] Click position: ({x:.1f}, {y:.1f})")

            # Execute mouse click
            await tab.mouse_click(x, y)

            debug.log(f"[NEW EVENT CDP CLICK] Mouse click executed successfully")

            # Wait for navigation
            await tab.sleep(1.5)

            is_price_assign_by_bot = True

            debug.log(f"[NEW EVENT SUCCESS] Clicked area: {target_area['areaName']}")

        except Exception as resolve_exc:
            if debug.enabled:
                debug.log(f"[NEW EVENT CDP CLICK] Resolve/click failed: {resolve_exc}")
                import traceback
                traceback.print_exc()

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[NEW EVENT ERROR] Exception during click: {exc}")
            import traceback
            traceback.print_exc()

    return is_need_refresh, is_price_assign_by_bot

async def nodriver_ibon_area_auto_select(tab, config_dict, area_keyword_item=""):
    """
    ibon seat area auto-selection (NoDriver version)

    Handles seat area selection on UTK0201_000.aspx page after date selection.
    Uses JavaScript for data extraction and CDP for clicking.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        area_keyword_item: Area keyword string (space-separated for AND logic)

    Returns:
        tuple: (is_need_refresh, is_price_assign_by_bot)
            - is_need_refresh: Whether page refresh is needed
            - is_price_assign_by_bot: Whether area selection succeeded
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False, False

    debug = util.create_debug_logger(config_dict)
    auto_select_mode = config_dict["area_auto_select"]["mode"]
    area_auto_fallback = config_dict.get('area_auto_fallback', False)  # T021: Safe access for new field
    ticket_number = config_dict["ticket_number"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    debug.log("NoDriver ibon_area_auto_select started")
    debug.log(f"area_keyword_item: {area_keyword_item}")
    debug.log(f"auto_select_mode: {auto_select_mode}")
    debug.log(f"ticket_number: {ticket_number}")

    # Wait for Shadow DOM to fully load (ibon orders page needs more time for TR elements to render)
    # Auto-detect TR elements (no fixed wait - responds immediately when ready)
    try:
        # First, ensure page state is synced
        await tab  # Sync state

        # Quick check: Is this actually an area selection page?
        # If URL is verification page (UTK0201_0.aspx with rn=), skip area selection
        try:
            current_url = tab.target.url
            if current_url and '/UTK02/UTK0201_0.' in current_url.upper() and 'rn=' in current_url.lower():
                debug.log("[IBON AREA] Detected verification page URL, skipping area selection")
                # Return (False, False) to skip reload and let main loop re-check URL
                return False, False
        except:
            pass

        # Quick check: Does page have Cloudflare or verification form instead of area table?
        try:
            import time as time_module
            cloudflare_max_wait = 15  # Maximum wait for Cloudflare (seconds)
            cloudflare_check_interval = 0.5  # Check interval (seconds)
            cloudflare_start_time = time_module.time()
            cloudflare_detected_once = False
            page_type_result = "area"

            while (time_module.time() - cloudflare_start_time) < cloudflare_max_wait:
                page_type_result = await tab.evaluate('''
                    (function() {
                        // Check for Cloudflare verification page
                        var bodyText = document.body ? document.body.innerText : '';
                        var title = document.title || '';

                        // Cloudflare indicators
                        if (title === '請稍候...' ||
                            bodyText.indexOf('正在驗證') !== -1 ||
                            bodyText.indexOf('驗證您是否是人類') !== -1 ||
                            bodyText.indexOf('Checking your browser') !== -1 ||
                            bodyText.indexOf('verify you are human') !== -1) {
                            return "cloudflare";
                        }

                        // Check for ibon verification form markers
                        var verifyInputs = document.querySelectorAll('#content div.form-group input');
                        var areaTable = document.querySelector('table.table, table[class*="area"], tbody tr td a');

                        if (verifyInputs.length > 0 && !areaTable) {
                            return "verify";
                        }
                        return "area";
                    })()
                ''')

                if page_type_result == "cloudflare":
                    if not cloudflare_detected_once:
                        cloudflare_detected_once = True
                        debug.log("[IBON AREA] Detected Cloudflare verification, waiting for completion...")
                    # Continue waiting, check again
                    await tab.sleep(cloudflare_check_interval)
                    continue
                elif page_type_result == "verify":
                    debug.log("[IBON AREA] Detected verification form, skipping area selection")
                    return False, False
                else:
                    # page_type_result == "area" - Cloudflare completed or not present
                    if cloudflare_detected_once:
                        elapsed = time_module.time() - cloudflare_start_time
                        debug.log(f"[IBON AREA] Cloudflare verification completed after {elapsed:.1f}s")
                    break

            # If timeout while Cloudflare still active
            if cloudflare_detected_once and page_type_result == "cloudflare":
                debug.log("[IBON AREA] Cloudflare verification timeout, letting main loop retry")
                return False, False

        except Exception as cf_exc:
            debug.log(f"[IBON AREA] Cloudflare/page type check error: {cf_exc}")
            pass

        # Initialize CDP DOM state (required for perform_search to work)
        try:
            await tab.send(cdp.dom.get_document(depth=0, pierce=False))
        except:
            pass

        import time
        max_wait = 5  # Maximum wait (increased for page load after Cloudflare)
        check_interval = 0.15  # Polling interval
        start_time = time.time()
        min_tr_count = 3  # Minimum TR elements to consider page loaded (header + at least 1 data row)

        debug.log("[IBON AREA] Auto-detecting area table...")

        last_tr_count = 0
        stable_count = 0  # Track if TR count is stable (page finished loading)

        while (time.time() - start_time) < max_wait:
            # Check if URL changed to verification page (UTK0201_0.aspx)
            try:
                current_url = tab.target.url
                if current_url and '/UTK02/UTK0201_0.' in current_url.upper() and 'rn=' in current_url.lower():
                    debug.log("[IBON AREA] URL changed to verification page, exiting area selection")
                    # Return (False, False) to skip reload and let main loop re-check URL
                    return False, False
            except:
                pass

            try:
                # Use CDP search to check TR presence (penetrates Shadow DOM)
                search_id, tr_count = await tab.send(cdp.dom.perform_search(
                    query='tbody tr',
                    include_user_agent_shadow_dom=True
                ))

                # Clean up search
                try:
                    await tab.send(cdp.dom.discard_search_results(search_id=search_id))
                except:
                    pass

                # Check if TR count is stable (same as last check)
                if tr_count == last_tr_count and tr_count >= min_tr_count:
                    stable_count += 1
                else:
                    stable_count = 0
                last_tr_count = tr_count

                # Page loaded: minimum TR count reached AND stable for 2 consecutive checks
                if tr_count >= min_tr_count and stable_count >= 1:
                    elapsed = time.time() - start_time
                    debug.log(f"[IBON AREA] Found {tr_count} TR elements after {elapsed:.2f}s")
                    break
            except:
                pass

            await tab.sleep(check_interval)

    except Exception as e:
        debug.log(f"[IBON AREA] Error during auto-detect: {e}")
        pass

    # Phase 1: Extract all area data using DOMSnapshot (to pierce closed Shadow DOM)
    try:
        # cdp already imported at function start (Line 10535)

        debug.log("[DOMSNAPSHOT] Capturing page structure for area extraction...")

        # Use DOMSnapshot to get flattened page structure (pierces Shadow DOM)
        documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(
            computed_styles=[],
            include_paint_order=True,
            include_dom_rects=True
        ))

        areas_data = []

        if documents and len(documents) > 0:
            document_snapshot = documents[0]

            # Extract node information
            node_names = []
            node_values = []
            parent_indices = []
            attributes_list = []
            backend_node_ids = []

            if hasattr(document_snapshot, 'nodes'):
                nodes = document_snapshot.nodes
                if hasattr(nodes, 'node_name'):
                    node_names = [strings[i] if isinstance(i, int) and i < len(strings) else str(i)
                                 for i in nodes.node_name]
                if hasattr(nodes, 'node_value'):
                    node_values = [strings[i] if isinstance(i, int) and i >= 0 and i < len(strings) else ''
                                  for i in nodes.node_value]
                if hasattr(nodes, 'parent_index'):
                    parent_indices = list(nodes.parent_index)
                if hasattr(nodes, 'attributes'):
                    attributes_list = nodes.attributes
                if hasattr(nodes, 'backend_node_id'):
                    backend_node_ids = list(nodes.backend_node_id)

            debug.log(f"[DOMSNAPSHOT] Extracted {len(node_names)} nodes, {len(strings)} strings")

            # Build children map for traversal
            children_map = {}
            for i, parent_idx in enumerate(parent_indices):
                if parent_idx >= 0:
                    if parent_idx not in children_map:
                        children_map[parent_idx] = []
                    children_map[parent_idx].append(i)

            # Helper function to get attributes as dict
            def get_attributes_dict(node_index):
                attrs = {}
                if node_index < len(attributes_list):
                    attr_indices = attributes_list[node_index]
                    for j in range(0, len(attr_indices), 2):
                        if j + 1 < len(attr_indices):
                            key_idx = attr_indices[j]
                            val_idx = attr_indices[j + 1]
                            key = strings[key_idx] if key_idx < len(strings) else ''
                            val = strings[val_idx] if val_idx < len(strings) else ''
                            attrs[key] = val
                return attrs

            # Helper function to get all text content from node and its children
            def get_text_content(node_index, depth=0, max_depth=10):
                if depth > max_depth or node_index >= len(node_names):
                    return ''

                text_parts = []

                # If this is a text node, get its value
                if node_names[node_index] == '#text' and node_index < len(node_values):
                    text_parts.append(node_values[node_index])

                # Recursively get text from children
                if node_index in children_map:
                    for child_idx in children_map[node_index]:
                        child_text = get_text_content(child_idx, depth + 1, max_depth)
                        if child_text:
                            text_parts.append(child_text)

                return ' '.join(text_parts).strip()

            # Find all TR elements in the table
            tr_indices = []
            for i, node_name in enumerate(node_names):
                if node_name.upper() == 'TR':
                    # Check if it's inside a table (basic check)
                    tr_indices.append(i)

            debug.log(f"[DOMSNAPSHOT] Found {len(tr_indices)} TR elements")

            # Extract data from each TR
            area_index = 0
            for tr_idx in tr_indices:
                # Get TR attributes
                tr_attrs = get_attributes_dict(tr_idx)
                tr_id = tr_attrs.get('id', '')
                tr_class = tr_attrs.get('class', '')

                # Skip header rows (check if parent is THEAD)
                parent_idx = parent_indices[tr_idx] if tr_idx < len(parent_indices) else -1
                is_header = False
                if parent_idx >= 0 and parent_idx < len(node_names):
                    parent_name = node_names[parent_idx].upper()
                    if parent_name == 'THEAD':
                        is_header = True

                if is_header:
                    continue

                is_disabled = 'disabled' in tr_class.lower()

                # Find TD children
                td_indices = []
                if tr_idx in children_map:
                    for child_idx in children_map[tr_idx]:
                        if node_names[child_idx].upper() == 'TD':
                            td_indices.append(child_idx)

                # Extract text from each TD
                # Expected order: [0]=color, [1]=area_name, [2]=price, [3]=seat_status
                td_texts = []
                for td_idx in td_indices:
                    td_text = get_text_content(td_idx)
                    td_texts.append(td_text)

                if len(td_texts) >= 4:
                    area_name = td_texts[1].strip()
                    price = td_texts[2].strip()
                    seat_text = td_texts[3].strip()

                    # Get layout information (bounding box) for this TR
                    layout_rect = None
                    if hasattr(document_snapshot, 'layout'):
                        layout = document_snapshot.layout
                        if hasattr(layout, 'node_index') and hasattr(layout, 'bounds'):
                            # Find this TR's layout index
                            node_indices = list(layout.node_index)
                            bounds_list = list(layout.bounds)

                            if tr_idx in node_indices:
                                layout_idx = node_indices.index(tr_idx)
                                # bounds is an array of Rectangle objects: [x_rect, y_rect, width_rect, height_rect, ...]
                                bounds_idx = layout_idx * 4
                                if bounds_idx + 3 < len(bounds_list):
                                    # Each bound is a Rectangle object, extract the first value
                                    x_rect = bounds_list[bounds_idx]
                                    y_rect = bounds_list[bounds_idx + 1]
                                    width_rect = bounds_list[bounds_idx + 2]
                                    height_rect = bounds_list[bounds_idx + 3]

                                    # Rectangle objects contain an array, get the first value
                                    x = x_rect[0] if hasattr(x_rect, '__getitem__') else float(x_rect)
                                    y = y_rect[0] if hasattr(y_rect, '__getitem__') else float(y_rect)
                                    width = width_rect[0] if hasattr(width_rect, '__getitem__') else float(width_rect)
                                    height = height_rect[0] if hasattr(height_rect, '__getitem__') else float(height_rect)

                                    layout_rect = {'x': x, 'y': y, 'width': width, 'height': height}
                                    if area_index < 3:  # Only show first 3 for debugging
                                        debug.log(f"[DOMSNAPSHOT] TR #{area_index} (node {tr_idx}): layout_idx={layout_idx}, rect={layout_rect}")
                            else:
                                if area_index < 3:
                                    debug.log(f"[DOMSNAPSHOT] TR #{area_index} (node {tr_idx}): NOT in layout.node_index")

                    # Get backend_node_id for this TR
                    tr_backend_node_id = None
                    if tr_idx < len(backend_node_ids):
                        tr_backend_node_id = backend_node_ids[tr_idx]

                    # Build area data object (matching JavaScript version format)
                    area_data = {
                        'index': area_index,
                        'id': tr_id,
                        'disabled': is_disabled,
                        'areaName': area_name,
                        'price': price,
                        'seatText': seat_text,
                        'innerHTML': f'<tr id="{tr_id}" class="{tr_class}">...mock...</tr>',  # Mock HTML for compatibility
                        'tr_node_index': tr_idx,  # Store for reference
                        'layout_rect': layout_rect,  # Store bounding box for clicking
                        'backend_node_id': tr_backend_node_id  # Store for CDP node resolution
                    }
                    areas_data.append(area_data)
                    area_index += 1

        debug.log(f"[AREA EXTRACT] Found {len(areas_data)} total areas")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[ERROR] Failed to extract area data: {exc}")
            import traceback
            traceback.print_exc()
        return True, False

    if not areas_data or len(areas_data) == 0:
        debug.log("[AREA EXTRACT] No areas found on page")
        return True, False

    # Phase 2: Filter areas (disabled, sold out, insufficient seats)
    valid_areas = []

    for area in areas_data:
        # Skip disabled areas
        if area['disabled']:
            debug.log(f"[ibon] 跳過: {area['areaName']}")
            continue

        # 同時檢查區域名稱、票價與內容
        row_text = area['areaName'] + ' ' + area.get('price', '') + ' ' + util.remove_html_tags(area['innerHTML'])

        # Skip sold out areas
        if '已售完' in area['seatText']:
            debug.log(f"[ibon] 已售完: {area['areaName']}")
            continue

        if 'disabled' in area['innerHTML'].lower() or 'sold-out' in area['innerHTML'].lower():
            debug.log(f"[ibon] 跳過: {area['areaName']}")
            continue

        # Skip description rows (not actual seat areas)
        if row_text in ["座位已被選擇", "座位已售出", "舞台區域"]:
            continue

        # Check exclude keywords
        if util.reset_row_text_if_match_keyword_exclude(config_dict, row_text):
            debug.log(f"[ibon] 排除: {area['areaName']}")
            continue

        # Check remaining seat count
        seat_text = area['seatText']
        if seat_text.isdigit():
            remaining_seats = int(seat_text)
            if remaining_seats < ticket_number:
                debug.log(f"[ibon] 座位不足: {area['areaName']} ({remaining_seats}/{ticket_number})")
                continue

        valid_areas.append(area)

    debug.log(f"[ibon] 有效區域: {len(valid_areas)}")

    # Phase 3: Keyword matching with early return pattern (T010-T016)
    matched_areas = []
    target_found = False

    if area_keyword_item and len(area_keyword_item) > 0:
        try:
            # NOTE: area_keyword_item is already a SINGLE keyword string from upper layer
            # Upper layer (line 10908) splits by comma using JSON parsing:
            #   Input: "\"5600\",\"5,600\""
            #   After JSON: ["5600", "5,600"]
            #   This function is called once per keyword: "5600" or "5,600"
            #
            # DO NOT split by comma again here, or "5,600" becomes ['5', '600'] (BUG!)
            # Only support space-separated AND logic within each keyword

            area_keyword_clean = area_keyword_item.strip()
            if area_keyword_clean.startswith('"') and area_keyword_clean.endswith('"'):
                area_keyword_clean = area_keyword_clean[1:-1]

            # Treat the entire string as a single keyword
            keyword_item = util.format_keyword_string(area_keyword_clean)

            debug.log(f"[IBON AREA KEYWORD] Checking keyword: {keyword_item}")

            # Check all areas for this keyword
            for area in valid_areas:
                row_text = area['areaName'] + ' ' + area.get('price', '') + ' ' + util.remove_html_tags(area['innerHTML'])
                row_text = util.format_keyword_string(row_text)

                # Support AND logic with space-separated sub-keywords
                # Example: "VIP 區" → ['VIP', '區'] → must match both
                sub_keywords = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                is_match = all(sub_kw.lower() in row_text.lower() for sub_kw in sub_keywords)

                if is_match:
                    # Keyword matched - IMMEDIATELY select and stop
                    matched_areas = [area]
                    target_found = True
                    debug.log(f"[IBON AREA KEYWORD] Keyword matched: '{keyword_item}'")
                    debug.log(f"[IBON AREA SELECT] Selected area: {area['areaName']} (keyword match)")
                    break

            # All keywords failed log
            if not target_found:
                debug.log(f"[IBON AREA KEYWORD] Keyword '{keyword_item}' failed to match")
        except Exception as e:
            debug.log(f"[IBON AREA] Keyword parse error: {e}")
            debug.log(f"[IBON AREA] Treating as 'all keywords failed'")
            matched_areas = []  # Let Feature 003 fallback logic handle this
    else:
        matched_areas = valid_areas

    if not target_found:
        debug.log(f"[IBON AREA] Total matched areas: {len(matched_areas)}")

    # T022-T024: Conditional fallback based on area_auto_fallback switch
    if len(matched_areas) == 0 and area_keyword_item and len(area_keyword_item) > 0:
        if area_auto_fallback:
            # T022: Fallback enabled - use all valid areas
            debug.log(f"[IBON AREA FALLBACK] area_auto_fallback=true, triggering auto fallback")
            debug.log(f"[IBON AREA FALLBACK] Selecting available area based on area_select_order='{auto_select_mode}'")
            matched_areas = valid_areas
        else:
            # T023: Fallback disabled - strict mode (no selection, will reload)
            debug.log(f"[IBON AREA FALLBACK] area_auto_fallback=false, fallback is disabled")
            debug.log(f"[IBON AREA SELECT] No area selected, will reload page and retry")
            # T024: No available options after keyword matching failed
            if len(valid_areas) == 0:
                debug.log(f"[IBON AREA FALLBACK] No available options after exclusion")
            is_need_refresh = True
            return is_need_refresh, False

    # Phase 4: Select target area based on mode
    target_area = util.get_target_item_from_matched_list(matched_areas, auto_select_mode)

    if not target_area:
        is_need_refresh = True
        debug.log("[RESULT] Failed to select target area, refresh needed")
        return is_need_refresh, False

    # T013 equivalent: Log selected area with selection type
    if debug.enabled:
        is_keyword_match = (area_keyword_item and len(area_keyword_item) > 0 and len(matched_areas) < len(valid_areas))
        selection_type = "keyword match" if is_keyword_match else "fallback"
        debug.log(f"[IBON AREA SELECT] Selected area: {target_area['areaName']} ({selection_type})")
        debug.log(f"[TARGET] Selected area: {target_area['areaName']} (index: {target_area['index']}, id: {target_area['id']})")

    # Phase 5: Click target area using CDP real-time coordinates
    try:
        # cdp already imported at file start (Line 29)

        # Get backend_node_id from target area
        backend_node_id = target_area.get('backend_node_id')

        if not backend_node_id:
            debug.log(f"[CDP CLICK] No backend_node_id available for TR")
        else:
            # Request document first (required for pushNodesByBackendIdsToFrontend)
            try:
                document = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
            except Exception as doc_exc:
                debug.log(f"[CDP CLICK] Document request failed: {doc_exc}")
                return is_need_refresh, is_price_assign_by_bot

            # Convert backend_node_id to node_id using pushNodesByBackendIdsToFrontend
            try:
                result = await tab.send(cdp.dom.push_nodes_by_backend_ids_to_frontend(backend_node_ids=[backend_node_id]))
                node_ids = result if isinstance(result, list) else (result.node_ids if hasattr(result, 'node_ids') else [])

                if not node_ids or len(node_ids) == 0:
                    debug.log(f"[CDP CLICK] Failed to convert backend_node_id to node_id")
                    return is_need_refresh, is_price_assign_by_bot

                node_id = node_ids[0]

                # Scroll into view
                try:
                    await tab.send(cdp.dom.scroll_into_view_if_needed(node_id=node_id))
                except Exception:
                    pass  # Scroll not always needed

                # Focus element (ignore focus warnings)
                try:
                    await tab.send(cdp.dom.focus(node_id=node_id))
                except Exception:
                    pass  # Element may not be focusable

                # Get real-time box model and click
                box_model = await tab.send(cdp.dom.get_box_model(node_id=node_id))
                content_quad = box_model.content if hasattr(box_model, 'content') else box_model.model.content
                x = (content_quad[0] + content_quad[2]) / 2
                y = (content_quad[1] + content_quad[5]) / 2

                # Execute mouse click
                await tab.mouse_click(x, y)

                # Wait for navigation
                await tab.sleep(random.uniform(0.5, 0.8))

                is_price_assign_by_bot = True

                debug.log(f"[CLICK SUCCESS] Clicked area: {target_area['areaName']} (id: {target_area['id']})")

            except Exception as resolve_exc:
                if debug.enabled:
                    debug.log(f"[CDP CLICK] Resolve/click failed: {resolve_exc}")
                    import traceback
                    traceback.print_exc()

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[CLICK ERROR] Exception during click: {exc}")
            import traceback
            traceback.print_exc()

    return is_need_refresh, is_price_assign_by_bot

async def nodriver_ibon_ticket_number_auto_select(tab, config_dict):
    """
    ibon ticket number auto-selection using NoDriver CDP with keyword matching

    Enhancement (2026-01-07):
    - Supports ticket type keyword matching using area_keyword
    - Supports keyword exclusion using keyword_exclude
    - Respects auto_select_mode for fallback selection

    Returns: is_ticket_number_assigned (bool)
    """
    # Check pause at function start
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)
    ticket_number = str(config_dict.get("ticket_number", 2))
    is_ticket_number_assigned = False

    # Get keyword settings for ticket type matching
    area_keyword = config_dict["area_auto_select"].get("area_keyword", "").strip()
    keyword_exclude = config_dict.get("keyword_exclude", "")
    auto_select_mode = config_dict["area_auto_select"].get("mode", 1)

    try:
        # Step 1: Wait for SELECT element
        wait_result = await tab.evaluate('''
            () => {
                return new Promise((resolve) => {
                    let attempts = 0;
                    const maxAttempts = 15;

                    const checkSelect = setInterval(() => {
                        attempts++;

                        let select = document.querySelector('table.rwdtable select.form-control-sm') ||
                                    document.querySelector('table.table select[name*="AMOUNT_DDL"]') ||
                                    document.querySelector('select.form-control-sm');

                        if (select) {
                            clearInterval(checkSelect);
                            resolve({ready: true, selector_used: select.className || select.name});
                        } else if (attempts >= maxAttempts) {
                            clearInterval(checkSelect);
                            resolve({ready: false, error: "Timeout waiting for SELECT element"});
                        }
                    }, 100);
                });
            }
        ''')

        wait_parsed = util.parse_nodriver_result(wait_result)
        if isinstance(wait_parsed, dict):
            if wait_parsed.get('ready'):
                debug.log(f"[TICKET DOM] SELECT element ready: {wait_parsed.get('selector_used')}")
            else:
                debug.log(f"[TICKET DOM] {wait_parsed.get('error')}")

        # Step 2: Extract all ticket types with their names and availability
        ticket_types_result = await tab.evaluate(f'''
            (function() {{
                let ticketTypes = [];
                const targetTicketNumber = "{ticket_number}";

                // Try new format first (table.rwdtable)
                let rows = document.querySelectorAll('table.rwdtable tbody tr');
                let tableType = 'rwdtable';

                // Fallback to old format (table.table)
                if (rows.length === 0) {{
                    rows = document.querySelectorAll('table.table tbody tr');
                    tableType = 'table';
                }}

                rows.forEach((row, index) => {{
                    // Find SELECT element in this row
                    let select = row.querySelector('select.form-control-sm') ||
                                row.querySelector('select[name*="AMOUNT_DDL"]');

                    if (!select) return;

                    // Get ticket type name from first cell
                    let nameCell = row.querySelector('td:first-child, td[data-title]');
                    let ticketName = nameCell ? nameCell.textContent.trim() : '';

                    // Get price from price cell
                    let priceCell = row.querySelector('td:nth-child(3)');
                    let price = priceCell ? priceCell.textContent.trim() : '';

                    // Check if this ticket type has valid options (not sold out)
                    let hasValidOption = Array.from(select.options).some(
                        opt => opt.value !== '0' && opt.value !== ''
                    );

                    // Check current value
                    let currentValue = select.value;
                    let isAlreadySelected = currentValue !== '0' && currentValue !== '';

                    // Check if target ticket_number option exists
                    let hasTargetOption = Array.from(select.options).some(
                        opt => opt.value === targetTicketNumber
                    );

                    ticketTypes.push({{
                        index: index,
                        name: ticketName,
                        price: price,
                        hasValidOption: hasValidOption,
                        isAlreadySelected: isAlreadySelected,
                        currentValue: currentValue,
                        hasTargetOption: hasTargetOption,
                        selectName: select.name || ''
                    }});
                }});

                return {{
                    ticketTypes: ticketTypes,
                    tableType: tableType,
                    totalRows: rows.length
                }};
            }})();
        ''')

        ticket_types_parsed = util.parse_nodriver_result(ticket_types_result)

        if not isinstance(ticket_types_parsed, dict):
            debug.log(f"[TICKET] Failed to parse ticket types")
            return False

        ticket_types = ticket_types_parsed.get('ticketTypes', [])

        if debug.enabled:
            debug.log(f"[TICKET] Found {len(ticket_types)} ticket type(s)")
            for tt in ticket_types:
                status = "selected" if tt.get('isAlreadySelected') else ("available" if tt.get('hasValidOption') else "sold out")
                debug.log(f"  [{tt.get('index')}] {tt.get('name')} - {tt.get('price')} ({status})")

        if len(ticket_types) == 0:
            debug.log(f"[TICKET] No ticket types found")
            return False

        # Step 3: Check if any ticket type is already selected
        for tt in ticket_types:
            if tt.get('isAlreadySelected'):
                debug.log(f"[TICKET] Already assigned: {tt.get('name')} = {tt.get('currentValue')}")
                return True

        # Step 4: Filter valid ticket types (with available options)
        valid_tickets = [tt for tt in ticket_types if tt.get('hasValidOption')]

        if len(valid_tickets) == 0:
            debug.log(f"[TICKET] All ticket types sold out")
            return False

        # Step 5: Apply keyword_exclude filter
        filtered_tickets = []
        for ticket in valid_tickets:
            ticket_name = ticket.get('name', '')
            if keyword_exclude and len(keyword_exclude) > 0:
                if util.reset_row_text_if_match_keyword_exclude(config_dict, ticket_name):
                    debug.log(f"[TICKET] Excluded by keyword: {ticket_name}")
                    continue
            filtered_tickets.append(ticket)

        if len(filtered_tickets) == 0:
            debug.log(f"[TICKET] All ticket types excluded by keyword_exclude")
            # Fallback to valid_tickets if all excluded
            filtered_tickets = valid_tickets

        # Step 5.5: Shortcut for single ticket type (skip keyword matching)
        # Fix (2026-01-07): If only 1 valid ticket type, select it directly
        if len(filtered_tickets) == 1:
            matched_ticket = filtered_tickets[0]
            debug.log(f"[TICKET] Single ticket type, selecting directly: {matched_ticket.get('name')}")
        else:
            # Step 6: Apply area_keyword matching (for multiple ticket types)
            matched_ticket = None

            if area_keyword and len(area_keyword) > 0:
                # Parse keyword array (supports "kw1","kw2" format)
                try:
                    area_keyword_array = json.loads("[" + area_keyword + "]")
                except:
                    area_keyword_array = [area_keyword]

                # Try each keyword in priority order
                for keyword_item in area_keyword_array:
                    keyword_item = keyword_item.strip()
                    if not keyword_item:
                        continue

                    for ticket in filtered_tickets:
                        ticket_name = ticket.get('name', '')
                        row_text = util.format_keyword_string(ticket_name)

                        # Support AND logic (space-separated keywords must all match)
                        keyword_parts = [kw.strip() for kw in keyword_item.split(' ') if kw.strip()]
                        is_match = all(
                            util.format_keyword_string(kw) in row_text
                            for kw in keyword_parts
                        )

                        if is_match:
                            matched_ticket = ticket
                            debug.log(f"[TICKET] Keyword matched: '{keyword_item}' -> {ticket_name}")
                            break

                    if matched_ticket:
                        break

                if not matched_ticket:
                    debug.log(f"[TICKET] No ticket matched keyword: {area_keyword}")

        # Step 7: Fallback selection if no keyword match
        if not matched_ticket:
            if len(filtered_tickets) > 0:
                # Use auto_select_mode for fallback
                matched_ticket = util.get_target_item_from_matched_list(
                    filtered_tickets, auto_select_mode
                )
                debug.log(f"[TICKET] Fallback selection: {matched_ticket.get('name') if matched_ticket else 'None'}")

        if not matched_ticket:
            debug.log(f"[TICKET] No suitable ticket type found")
            return False

        # Step 8: Set the ticket quantity for the matched ticket type
        target_index = matched_ticket.get('index', 0)
        has_target_option = matched_ticket.get('hasTargetOption', False)

        # Determine which value to set
        # If target not available, JS will find max available option
        value_to_set = ticket_number if has_target_option else ""

        result = await tab.evaluate(f'''
            (function() {{
                // Find all rows
                let rows = document.querySelectorAll('table.rwdtable tbody tr');
                if (rows.length === 0) {{
                    rows = document.querySelectorAll('table.table tbody tr');
                }}

                if ({target_index} >= rows.length) {{
                    return {{success: false, error: "Target row index out of range"}};
                }}

                let row = rows[{target_index}];
                let select = row.querySelector('select.form-control-sm') ||
                            row.querySelector('select[name*="AMOUNT_DDL"]');

                if (!select) {{
                    return {{success: false, error: "SELECT not found in target row"}};
                }}

                let valueToSet = "{value_to_set}";

                // If no preset value, find max available option
                if (!valueToSet) {{
                    const validOptions = Array.from(select.options).filter(opt =>
                        parseInt(opt.value) > 0 && !isNaN(parseInt(opt.value))
                    );
                    if (validOptions.length === 0) {{
                        return {{success: false, error: "No valid options available"}};
                    }}
                    const maxOpt = validOptions.reduce((max, opt) =>
                        parseInt(opt.value) > parseInt(max.value) ? opt : max
                    );
                    valueToSet = maxOpt.value;
                }}

                // Set the value
                select.value = valueToSet;

                // Trigger events
                select.dispatchEvent(new Event('input', {{bubbles: true}}));
                select.dispatchEvent(new Event('change', {{bubbles: true}}));
                select.dispatchEvent(new Event('blur', {{bubbles: true}}));

                // Verify
                const finalValue = select.value;
                if (finalValue !== valueToSet) {{
                    return {{success: false, error: "Value verification failed", expected: valueToSet, actual: finalValue}};
                }}

                return {{
                    success: true,
                    set_value: valueToSet,
                    fallback: "{value_to_set}" === "",
                    ticket_name: row.querySelector('td:first-child')?.textContent.trim() || '',
                    verified: true
                }};
            }})();
        ''')

        result_parsed = util.parse_nodriver_result(result)

        if isinstance(result_parsed, dict):
            if result_parsed.get('success'):
                is_ticket_number_assigned = True
                ticket_name = result_parsed.get('ticket_name', '')
                set_value = result_parsed.get('set_value', '')
                if debug.enabled:
                    if value_to_set != ticket_number:
                        debug.log(f"[TICKET] Set '{ticket_name}' to {set_value} (fallback, target {ticket_number} not available)")
                    else:
                        debug.log(f"[TICKET] Set '{ticket_name}' to {set_value}")
            else:
                debug.log(f"[TICKET] Failed: {result_parsed.get('error')}")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[TICKET ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return is_ticket_number_assigned

    # nodriver_ibon_get_captcha_image_from_shadow_dom moved to nodriver_common.py
    # as nodriver_get_captcha_image_from_dom_snapshot (shared by ibon and kham)

async def nodriver_ibon_keyin_captcha_code(tab, answer="", auto_submit=False, config_dict=None):
    """
    ibon captcha input handling
    Returns: (is_verifyCode_editing, is_form_submitted)
    """
    debug = util.create_debug_logger(config_dict)

    is_verifyCode_editing = False
    is_form_submitted = False

    debug.log(f"[CAPTCHA INPUT] answer: {answer}, auto_submit: {auto_submit}")

    try:
        # Find captcha input box
        # Selector 1: input[value="驗證碼"]
        # Selector 2: #ctl00_ContentPlaceHolder1_CHK
        form_verifyCode = None

        try:
            form_verifyCode = await tab.query_selector('input[placeholder*="驗證碼"]')
        except:
            pass

        if not form_verifyCode:
            try:
                form_verifyCode = await tab.query_selector('input[value="驗證碼"]')
            except:
                pass

        if not form_verifyCode:
            try:
                form_verifyCode = await tab.query_selector('#ctl00_ContentPlaceHolder1_CHK')
            except:
                pass

        if not form_verifyCode:
            debug.log("[CAPTCHA INPUT] Input box not found")
            return is_verifyCode_editing, is_form_submitted

        # Check if input box is visible
        is_visible = False
        try:
            is_visible = await tab.evaluate('''
                (function() {
                    const selectors = [
                        'input[placeholder*="驗證碼"]',
                        'input[value="驗證碼"]',
                        '#ctl00_ContentPlaceHolder1_CHK'
                    ];
                    for (let selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && !element.disabled && element.offsetParent !== null) {
                            return true;
                        }
                    }
                    return false;
                })();
            ''')
        except:
            pass

        if not is_visible:
            debug.log("[CAPTCHA INPUT] Input box not visible")
            return is_verifyCode_editing, is_form_submitted

        # If no answer provided, check if already has value for manual input mode
        if not answer:
            # Get current input value
            inputed_value = ""
            try:
                inputed_value = await form_verifyCode.apply('function (element) { return element.value; }') or ""
            except:
                pass

            # If already has value, skip (user manually inputed)
            if inputed_value and inputed_value != "驗證碼":
                debug.log(f"[CAPTCHA INPUT] Already has value: {inputed_value}")
                is_verifyCode_editing = True
                return is_verifyCode_editing, is_form_submitted

            # Focus for manual input
            try:
                await form_verifyCode.click()
                is_verifyCode_editing = True
                debug.log("[CAPTCHA INPUT] Focused for manual input")
            except:
                pass
            return is_verifyCode_editing, is_form_submitted

        # Fill in answer
        try:
            await form_verifyCode.click()

            # Clear placeholder value
            await form_verifyCode.apply('function (element) { element.value = ""; }')

            # Type answer
            await form_verifyCode.send_keys(answer)

            debug.log(f"[CAPTCHA INPUT] Filled answer: {answer}")

            # Auto submit if enabled
            if auto_submit:
                # Check if ticket number is selected (any SELECT, not just first one)
                # Fix (2026-01-07): Multi-ticket types may have selected ticket at index > 0
                ticket_ok = await tab.evaluate('''
                    (function() {
                        // Try new EventBuy format first: table.rwdtable select.form-control-sm
                        let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
                        // Fallback to old .aspx format: table.table select[name*="AMOUNT_DDL"]
                        if (selects.length === 0) {
                            selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
                        }
                        if (selects.length === 0) return false;
                        // Check if ANY select has a non-zero value (ticket selected)
                        return Array.from(selects).some(select =>
                            select.value !== "0" && select.value !== ""
                        );
                    })();
                ''')

                if ticket_ok:
                    # Set up alert handler BEFORE clicking submit button
                    alert_handled = False

                    async def handle_submit_dialog(event):
                        nonlocal alert_handled
                        alert_handled = True
                        debug.log(f"[CAPTCHA INPUT] Alert detected: '{event.message}'")
                        # Auto-dismiss alert
                        try:
                            await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                            debug.log(f"[CAPTCHA INPUT] Alert dismissed")
                        except Exception as dismiss_exc:
                            debug.log(f"[CAPTCHA INPUT] Failed to dismiss alert: {dismiss_exc}")

                    # Register alert handler
                    try:
                        tab.add_handler(cdp.page.JavascriptDialogOpening, handle_submit_dialog)
                        debug.log(f"[CAPTCHA INPUT] Alert handler registered before submit")
                    except Exception as handler_exc:
                        debug.log(f"[CAPTCHA INPUT] Failed to register alert handler: {handler_exc}")

                    # Find and click submit button
                    # Multiple button patterns for different ibon page types:
                    # - UTK0201 (EventBuy): #ctl00_ContentPlaceHolder1_A2
                    # - UTK0202 (ticket selection): a[id*="AddShopingCart"] or a.btn.btn-primary.btn-block
                    # CRITICAL: iBon requires calling ImageCode_Verify2() before submit
                    submit_clicked = await tab.evaluate('''
                        (function() {
                            // Try multiple selectors in priority order
                            let submitBtn = document.querySelector('#ctl00_ContentPlaceHolder1_A2');

                            if (!submitBtn) {
                                // UTK0202 page: try AddShopingCart button
                                submitBtn = document.querySelector('a[id*="AddShopingCart"]');
                            }

                            if (!submitBtn) {
                                // Generic fallback: any visible "下一步" button
                                const buttons = document.querySelectorAll('a.btn.btn-primary.btn-block');
                                for (let btn of buttons) {
                                    if (btn.textContent.includes('下一步') &&
                                        btn.offsetParent !== null &&  // is visible
                                        btn.style.display !== 'none') {
                                        submitBtn = btn;
                                        break;
                                    }
                                }
                            }

                            if (!submitBtn || submitBtn.disabled) {
                                console.log('[CAPTCHA] Submit button not found or disabled');
                                return false;
                            }

                            console.log('[CAPTCHA] Found submit button:', submitBtn.id || submitBtn.className);

                            // Call iBon's frontend verification function if it exists
                            if (typeof ImageCode_Verify2 === 'function') {
                                try {
                                    ImageCode_Verify2();
                                    console.log('[CAPTCHA] Called ImageCode_Verify2()');
                                } catch (e) {
                                    console.log('[CAPTCHA] ImageCode_Verify2 failed:', e);
                                }
                            } else if (typeof ImageCode_Verify === 'function') {
                                try {
                                    ImageCode_Verify();
                                    console.log('[CAPTCHA] Called ImageCode_Verify()');
                                } catch (e) {
                                    console.log('[CAPTCHA] ImageCode_Verify failed:', e);
                                }
                            }

                            submitBtn.click();
                            console.log('[CAPTCHA] Submit button clicked');
                            return true;
                        })();
                    ''')

                    if submit_clicked:
                        is_form_submitted = True
                        debug.log("[CAPTCHA INPUT] Form submitted")

                        # Wait for potential alert to appear and be handled
                        await asyncio.sleep(random.uniform(0.2, 0.6))

                        if debug.enabled:
                            if alert_handled:
                                debug.log(f"[CAPTCHA INPUT] Alert was handled during wait")
                            else:
                                debug.log(f"[CAPTCHA INPUT] No alert appeared (captcha may be correct)")
                    else:
                        debug.log("[CAPTCHA INPUT] Submit button not found or disabled")

                    # Remove alert handler
                    try:
                        tab.remove_handlers(cdp.page.JavascriptDialogOpening)
                    except:
                        pass
                else:
                    debug.log("[CAPTCHA INPUT] Ticket number not selected, skip submit")

        except Exception as exc:
            debug.log(f"[CAPTCHA INPUT ERROR] {exc}")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[CAPTCHA INPUT ERROR] Exception: {exc}")
            import traceback
            traceback.print_exc()

    return is_verifyCode_editing, is_form_submitted

async def nodriver_ibon_refresh_captcha(tab, config_dict):
    """
    Refresh ibon captcha image by calling JavaScript refreshCaptcha() function
    Returns: success (bool)
    """
    debug = util.create_debug_logger(config_dict)

    debug.log("[CAPTCHA REFRESH] Refreshing captcha")

    ret = False
    try:
        # Call JavaScript refreshCaptcha() function
        result = await tab.evaluate('''
            (function() {
                if (typeof refreshCaptcha === 'function') {
                    refreshCaptcha();
                    return true;
                }
                return false;
            })();
        ''')

        ret = result if result else False

        debug.log(f"[CAPTCHA REFRESH] Result: {ret}")

    except Exception as exc:
        debug.log(f"[CAPTCHA REFRESH ERROR] {exc}")

    return ret

async def nodriver_ibon_auto_ocr(tab, config_dict, ocr, away_from_keyboard_enable, previous_answer):
    """
    ibon OCR auto recognition logic
    Returns: (is_need_redo_ocr, previous_answer, is_form_submitted)
    """
    debug = util.create_debug_logger(config_dict)

    is_need_redo_ocr = False
    is_form_submitted = False

    # Check if input box exists
    is_input_box_exist = False
    try:
        input_box = await tab.query_selector('input[placeholder*="驗證碼"], input[value="驗證碼"], #ctl00_ContentPlaceHolder1_CHK')
        is_input_box_exist = input_box is not None
    except:
        pass

    if not is_input_box_exist:
        debug.log("[CAPTCHA OCR] Captcha input box not found")
        return is_need_redo_ocr, previous_answer, is_form_submitted

    if not ocr:
        debug.log("[CAPTCHA OCR] OCR module not available")
        return is_need_redo_ocr, previous_answer, is_form_submitted

    # iBon clears ticket number after captcha error - reselect if needed
    ticket_ok = await tab.evaluate('''
        (function() {
            // Try new EventBuy format first: table.rwdtable select.form-control-sm
            let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
            // Fallback to old .aspx format: table.table select[name*="AMOUNT_DDL"]
            if (selects.length === 0) {
                selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
            }
            if (selects.length === 0) return false;
            const select = selects[0];
            return select.value !== "0" && select.value !== "";
        })();
    ''')

    if not ticket_ok:
        # Retry with exponential backoff: 0.5s → 1.0s → 2.0s
        max_retries = 3
        is_ticket_number_assigned = False
        debug = util.create_debug_logger(config_dict)

        for attempt in range(1, max_retries + 1):
            is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

            if is_ticket_number_assigned:
                if attempt > 1:
                    debug.log(f"[TICKET RETRY] Success after {attempt} attempt(s)")
                break

            if attempt < max_retries:
                # Exponential backoff: delay = 0.5 * (2 ^ (attempt - 1))
                delay = 0.5 * (2 ** (attempt - 1))
                debug.log(f"[TICKET RETRY] Attempt {attempt}/{max_retries} failed, waiting {delay}s (exponential backoff)")
                await asyncio_sleep_with_pause_check(delay, config_dict)

        if is_ticket_number_assigned:
            # Wait for iBon to process ticket number change
            await asyncio.sleep(random.uniform(0.15, 0.25))

    # Get captcha image and do OCR
    ocr_start_time = time.time()

    img_base64 = await nodriver_ibon_get_captcha_image_from_shadow_dom(tab, config_dict)

    ocr_answer = None
    if img_base64:
        try:
            # Use global OCR instance (beta=True works best for iBon - 91.3% accuracy in tests)
            # Preprocessing actually reduces accuracy (73.9% vs 91.3%)
            ocr_answer = ocr.classification(img_base64)

            debug.log(f"[CAPTCHA OCR] Using global OCR (beta=True), raw result: {ocr_answer}")

            # Filter to digits only (iBon captchas are 4 digits)
            if ocr_answer:
                filtered = ''.join(filter(str.isdigit, ocr_answer))
                if filtered != ocr_answer:
                    debug.log(f"[CAPTCHA OCR] Filtered '{ocr_answer}' -> '{filtered}'")
                ocr_answer = filtered
        except Exception as exc:
            debug.log(f"[CAPTCHA OCR] OCR classification failed: {exc}")

    ocr_done_time = time.time()
    ocr_elapsed_time = ocr_done_time - ocr_start_time

    debug.log(f"[CAPTCHA OCR] Processing time: {ocr_elapsed_time:.3f}s")

    # Process OCR result
    if ocr_answer is None:
        if away_from_keyboard_enable:
            # Page not ready, retry
            is_need_redo_ocr = True
            await asyncio.sleep(0.1)
        else:
            # Manual mode
            await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
    else:
        ocr_answer = ocr_answer.strip()
        debug.log(f"[CAPTCHA OCR] Result: {ocr_answer}")

        if len(ocr_answer) == 4:
            # Valid 4-digit answer
            current_url_before_submit, _ = await nodriver_current_url(tab)
            who_care_var, is_form_submitted = await nodriver_ibon_keyin_captcha_code(
                tab, answer=ocr_answer, auto_submit=away_from_keyboard_enable, config_dict=config_dict
            )

            # Check if captcha was correct by verifying URL change
            if is_form_submitted and away_from_keyboard_enable:
                # Alert is already handled inside nodriver_ibon_keyin_captcha_code()
                # Just check URL change to determine if captcha was correct
                debug.log(f"[CAPTCHA OCR] Checking URL for verification...")

                try:
                    current_url_after_submit, _ = await nodriver_current_url(tab)
                except Exception as url_exc:
                    debug.log(f"[CAPTCHA OCR] Failed to get URL: {url_exc}")
                    current_url_after_submit = current_url_before_submit  # Assume same page

                if current_url_before_submit == current_url_after_submit:
                    # Still on same page - captcha was incorrect (alert was shown and dismissed)
                    debug.log(f"[CAPTCHA OCR] Captcha '{ocr_answer}' was incorrect, URL unchanged")

                    # IMPORTANT: iBon automatically refreshes captcha after alert dismissal
                    # Manual refresh is NOT needed and causes timing issues:
                    # - Alert dismiss triggers iBon's auto-refresh
                    # - Manual refresh would create a new captcha
                    # - Next OCR might still fetch the old URL from DOM cache
                    # Solution: Wait longer for iBon's refresh to fully stabilize
                    debug.log("[CAPTCHA OCR] Waiting for iBon auto-refresh to complete...")

                    await asyncio.sleep(random.uniform(0.8, 1.2))  # Wait for iBon auto-refresh

                    is_need_redo_ocr = True
                    is_form_submitted = False
                else:
                    # URL changed - captcha was correct
                    debug.log(f"[CAPTCHA OCR] Captcha '{ocr_answer}' accepted, URL changed")
                    debug.log(f"[CAPTCHA OCR] Before: {current_url_before_submit}")
                    debug.log(f"[CAPTCHA OCR] After: {current_url_after_submit}")
        else:
            # Invalid length
            debug.log(f"[CAPTCHA OCR] Invalid answer length: {len(ocr_answer)} (expected 4)")

            if not away_from_keyboard_enable:
                await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer

    return is_need_redo_ocr, previous_answer, is_form_submitted

async def nodriver_ibon_captcha(tab, config_dict, ocr):
    """
    ibon captcha main function
    Returns: is_captcha_sent (bool)
    """
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False

    debug = util.create_debug_logger(config_dict)

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    debug.log(f"[IBON CAPTCHA] Starting captcha handling")
    debug.log(f"[IBON CAPTCHA] OCR enabled: {config_dict['ocr_captcha']['enable']}")
    debug.log(f"[IBON CAPTCHA] Auto submit: {away_from_keyboard_enable}")

    is_captcha_sent = False

    if not config_dict["ocr_captcha"]["enable"]:
        # Manual mode: focus captcha field if present; proceed only when no captcha on page
        is_editing, _ = await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
        is_captcha_sent = not is_editing
    else:
        # Auto OCR mode
        previous_answer = None
        current_url, _ = await nodriver_current_url(tab)
        fail_count = 0  # Track consecutive failures
        total_fail_count = 0  # Track total failures

        for redo_ocr in range(5):
            is_need_redo_ocr, previous_answer, is_form_submitted = await nodriver_ibon_auto_ocr(
                tab, config_dict, ocr, away_from_keyboard_enable, previous_answer
            )

            if not is_need_redo_ocr:
                is_captcha_sent = True

            if is_form_submitted:
                debug.log("[IBON CAPTCHA] Form submitted successfully")
                break

            if not away_from_keyboard_enable:
                debug.log("[IBON CAPTCHA] Switching to manual input mode")
                break

            if not is_need_redo_ocr:
                break

            # Track failures and refresh captcha after 3 consecutive failures
            if is_need_redo_ocr:
                fail_count += 1
                total_fail_count += 1
                debug.log(f"[IBON CAPTCHA] Fail count: {fail_count}, Total fails: {total_fail_count}")

                # Check if total failures reached 5, switch to manual input mode
                if total_fail_count >= 5:
                    print("[IBON CAPTCHA] OCR failed 5 times, please enter captcha manually.")
                    away_from_keyboard_enable = False
                    await nodriver_ibon_keyin_captcha_code(tab, config_dict=config_dict)
                    break

                if fail_count >= 3:
                    debug.log("[IBON CAPTCHA] 3 consecutive failures reached")

                    # Try to dismiss any existing alert before continuing
                    try:
                        await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                        debug.log("[IBON CAPTCHA] Dismissed existing alert")
                    except:
                        pass

                    # IMPORTANT: iBon auto-refreshes captcha after alert dismiss
                    # Manual refresh causes timing conflicts with auto-refresh
                    # await nodriver_ibon_refresh_captcha(tab, config_dict)  # REMOVED
                    await asyncio.sleep(random.uniform(0.8, 1.2))  # Wait for iBon's auto-refresh to complete
                    fail_count = 0  # Reset consecutive counter after refresh

            # Check if URL changed
            new_url, _ = await nodriver_current_url(tab)
            if new_url != current_url:
                debug.log("[IBON CAPTCHA] URL changed, exit OCR loop")
                break

            debug.log(f"[IBON CAPTCHA] Retry {redo_ocr + 1}/5")

    return is_captcha_sent

async def nodriver_ibon_purchase_button_press(tab, config_dict):
    """
    Click the ibon purchase/next button after captcha is filled

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if button clicked successfully, False otherwise
    """
    debug = util.create_debug_logger(config_dict)
    is_button_clicked = False

    try:
        # Primary selector: #ticket-wrap > a.btn
        # Backup selectors from JavaScript extension analysis
        selectors = [
            '#ticket-wrap > a.btn',
            'div#ticket-wrap > a[onclick]',
            'div#ticket-wrap a.btn.btn-primary[href]'
        ]

        for selector in selectors:
            try:
                button = await tab.query_selector(selector)
                if button:
                    # Check if button is visible and enabled
                    is_visible = await tab.evaluate(f'''
                        (function() {{
                            const btn = document.querySelector('{selector}');
                            return btn && !btn.disabled && btn.offsetParent !== null;
                        }})();
                    ''')

                    if is_visible:
                        await button.click()
                        is_button_clicked = True
                        debug.log(f"[IBON PURCHASE] Successfully clicked button with selector: {selector}")
                        break
            except Exception as exc:
                debug.log(f"[IBON PURCHASE] Selector {selector} failed: {exc}")
                continue

        if not is_button_clicked:
            debug.log("[IBON PURCHASE] Purchase button not found or not clickable")

    except Exception as exc:
        if debug.enabled:
            debug.log(f"[IBON PURCHASE ERROR] {exc}")
            import traceback
            traceback.print_exc()

    return is_button_clicked

async def nodriver_ibon_check_sold_out(tab, config_dict):
    """
    Check if the event/ticket is sold out on ibon

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if sold out, False otherwise
    """
    debug = util.create_debug_logger(config_dict)
    is_sold_out = False

    try:
        # Check if ticket-info div contains "已售完" text
        result = await tab.evaluate('''
            (function() {
                const ticketInfo = document.querySelector('#ticket-info');
                if (ticketInfo) {
                    const text = ticketInfo.textContent || ticketInfo.innerText;
                    return text.includes('已售完');
                }
                return false;
            })()
        ''')

        if result:
            is_sold_out = True
            debug.log("[IBON] Event is sold out")

    except Exception as e:
        debug.log(f"[IBON] Check sold out error: {e}")

    return is_sold_out

async def nodriver_ibon_wait_for_select_elements(tab, config_dict, max_wait_time=3.0):
    """
    Wait for ticket quantity select elements to appear on page.
    Prevents false sold-out detection when page hasn't fully loaded.

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        max_wait_time: Maximum wait time in seconds (default 3.0)

    Returns:
        int: Number of select elements found (0 if none found after timeout)
    """
    debug = util.create_debug_logger(config_dict)
    wait_interval = 0.2
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        try:
            select_count = await tab.evaluate('''
                (function() {
                    let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
                    if (selects.length === 0) {
                        selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
                    }
                    if (selects.length === 0) {
                        selects = document.querySelectorAll('select.form-control-sm');
                    }
                    return selects.length;
                })()
            ''')
            if select_count and select_count > 0:
                if debug.enabled:
                    elapsed = time.time() - start_time
                    debug.log(f"[IBON] Page loaded, found {select_count} select element(s) after {elapsed:.2f}s")
                return select_count
        except Exception:
            pass
        await asyncio.sleep(wait_interval)

    debug.log(f"[IBON] Warning: No select elements found after {max_wait_time}s wait")
    return 0

async def nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict):
    """
    Check if tickets are sold out on ibon ticket selection page
    Applicable to UTK0201_001.aspx and similar ticket quantity selection pages

    Detection methods:
    1. Check if ticket quantity dropdowns only have "0" option
    2. Check if page contains sold out messages

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary for debug settings

    Returns:
        bool: True if sold out (needs page reload), False otherwise
    """
    debug = util.create_debug_logger(config_dict)
    is_sold_out = False

    try:
        result = await tab.evaluate('''
            (function() {
                // Sold out keywords (multi-language support)
                const soldOutKeywords = ['選購一空', '已售完', 'No tickets available', 'Sold out', 'Sold Out', '空席なし', '完売した', '完売', '尚無票'];

                // Method 1: Check AMOUNT_STR spans (purchase quantity field)
                const amountSpans = document.querySelectorAll('span[id*="AMOUNT_STR"]');
                let hasAmountSoldOut = false;
                let amountSoldOutCount = 0;

                for (let span of amountSpans) {
                    const text = span.textContent.trim();
                    // Check if text matches any sold out keyword
                    if (soldOutKeywords.some(keyword => text === keyword)) {
                        hasAmountSoldOut = true;
                        amountSoldOutCount++;
                    }
                }

                // Method 2: Check PRICE_STR spans (ticket area label)
                const priceSpans = document.querySelectorAll('span[id*="PRICE_STR"]');
                let hasPriceSoldOut = false;

                for (let span of priceSpans) {
                    const text = span.textContent;
                    // Check if text contains any sold out keyword in parentheses
                    if (soldOutKeywords.some(keyword => text.includes('(' + keyword + ')'))) {
                        hasPriceSoldOut = true;
                        break;
                    }
                }

                // Method 3: Check if ticket quantity selectors only have "0" option
                let selects = document.querySelectorAll('table.rwdtable select.form-control-sm');
                if (selects.length === 0) {
                    selects = document.querySelectorAll('table.table select[name*="AMOUNT_DDL"]');
                }
                if (selects.length === 0) {
                    selects = document.querySelectorAll('select.form-control-sm');
                }

                let hasValidOptions = false;
                let selectCount = selects.length;

                for (let select of selects) {
                    for (let option of select.options) {
                        // Valid option: value not "0" or empty, and not disabled
                        if (option.value !== "0" && option.value !== "" && !option.disabled) {
                            hasValidOptions = true;
                            break;
                        }
                    }
                    if (hasValidOptions) break;
                }

                // Method 4: Check if TICKET TABLE contains sold out messages (NOT entire page)
                // Fix (2026-01-07): Only check ticket table, not entire page.
                // The area dropdown may contain "(已售完)" for OTHER areas, causing false positives.
                let hasSoldOutMessage = false;
                const ticketTable = document.querySelector('table.rwdtable, table.table');
                if (ticketTable) {
                    const tableText = ticketTable.innerText || ticketTable.textContent;
                    hasSoldOutMessage = soldOutKeywords.some(keyword => tableText.includes(keyword));
                }

                // Final determination: sold out if any method detects it
                // IMPORTANT: Only consider "no valid options" as sold-out when select elements exist
                // If selectCount === 0, the page might still be loading (not sold out)
                const noValidOptionsButSelectsExist = selectCount > 0 && !hasValidOptions;
                const isSoldOut = hasAmountSoldOut || hasPriceSoldOut || noValidOptionsButSelectsExist || hasSoldOutMessage;

                return {
                    hasAmountSoldOut: hasAmountSoldOut,
                    amountSoldOutCount: amountSoldOutCount,
                    hasPriceSoldOut: hasPriceSoldOut,
                    selectCount: selectCount,
                    hasValidOptions: hasValidOptions,
                    hasSoldOutMessage: hasSoldOutMessage,
                    isSoldOut: isSoldOut,
                    pageNotLoaded: selectCount === 0
                };
            })()
        ''')

        result = util.parse_nodriver_result(result)
        if isinstance(result, dict):
            is_sold_out = result.get('isSoldOut', False)
            page_not_loaded = result.get('pageNotLoaded', False)
            if debug.enabled:
                select_count = result.get('selectCount', 0)
                has_valid = result.get('hasValidOptions', False)
                if page_not_loaded:
                    debug.log("[IBON] Page not fully loaded, waiting...")
                elif is_sold_out:
                    debug.log("[IBON] Sold out detected, will reload")
                else:
                    debug.log(f"[IBON] Tickets available ({select_count} selects, valid={has_valid})")

    except Exception as e:
        debug.log(f"[IBON SOLD OUT CHECK] Error: {e}")

    return is_sold_out

async def nodriver_ibon_navigate_on_sold_out(tab, config_dict):
    """
    Navigate to area selection page when tickets are sold out.
    Fix (2026-01-07): Instead of just reloading the same sold-out page (causes infinite loop),
    navigate back to the area selection page where other areas might be available.

    URL Formats:
    - New format: ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}
      -> Navigate to: ticket.ibon.com.tw/Event/{eventId}/{sessionId}
    - Old format: orders.ibon.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_PRICE_AREA_ID=xxx
      -> Navigate to: orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=xxx

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary

    Returns:
        bool: True if navigation successful, False otherwise
    """
    debug = util.create_debug_logger(config_dict)
    navigation_success = False

    try:
        url = tab.url if hasattr(tab, 'url') else str(tab.target.url)
        url_lower = url.lower()

        # New format: ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}
        if '/eventbuy/' in url_lower and 'ticket.ibon.com.tw' in url_lower:
            parts = url.split('/')
            # URL: https://ticket.ibon.com.tw/EventBuy/xxx/yyy/zzz
            # parts: ['https:', '', 'ticket.ibon.com.tw', 'EventBuy', 'eventId', 'sessionId', 'areaId']
            if len(parts) >= 7:
                # Navigate to Event page (area selection)
                event_url = '/'.join(parts[:3] + ['Event', parts[4], parts[5]])
                debug.log(f"[IBON] Sold out - navigating to area selection: {event_url}")
                await tab.get(event_url)
                navigation_success = True

        # Old format: orders.ibon.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_PRICE_AREA_ID=xxx
        # Note: Old .aspx pages require PRODUCT_ID and other parameters that are hard to reconstruct.
        # Using tab.back() is safer to return to the previous area selection page.
        elif '/utk02/utk0202_' in url_lower and 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
            debug.log("[IBON] Sold out - using tab.back() to return to area selection")
            await tab.back()
            navigation_success = True

        # Fallback: use tab.back() if URL pattern not recognized
        if not navigation_success:
            debug.log("[IBON] Sold out - using tab.back() as fallback")
            await tab.back()
            navigation_success = True

    except Exception as e:
        debug.log(f"[IBON] Navigation error: {e}")
        # Fallback to reload if navigation fails
        try:
            await tab.reload()
        except Exception:
            pass

    return navigation_success

async def nodriver_ibon_fill_verify_form(tab, config_dict, answer_list, fail_list,
                                          input_text_css, next_step_button_css):
    """
    ibon verification form filling (supports single/multiple input fields)

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary
        answer_list: List of answers to try
        fail_list: List of previously failed answers
        input_text_css: CSS selector for input fields
        next_step_button_css: CSS selector for submit button

    Returns:
        tuple[bool, list]: (is_answer_sent, updated fail_list)
    """
    debug = util.create_debug_logger(config_dict)
    is_answer_sent = False

    try:
        # Get all input fields and their values
        input_info_raw = await tab.evaluate(f'''
            (function() {{
                var inputs = document.querySelectorAll("{input_text_css}");
                var result = [];
                inputs.forEach(function(input) {{
                    result.push({{
                        value: input.value || ""
                    }});
                }});
                return {{
                    count: inputs.length,
                    inputs: result
                }};
            }})()
        ''')

        # Handle NoDriver result format - may return tuple (result, exception)
        input_info = input_info_raw
        if isinstance(input_info_raw, tuple) and len(input_info_raw) >= 1:
            input_info = input_info_raw[0]

        input_info = util.parse_nodriver_result(input_info)

        # Handle NoDriver error result (ExceptionDetails object or non-dict)
        if not input_info or not isinstance(input_info, dict):
            debug.log(f"[IBON VERIFY] Failed to get input info: {type(input_info)}")
            return is_answer_sent, fail_list

        form_input_count = input_info.get('count', 0)
        debug.log(f"[IBON VERIFY] Found {form_input_count} input field(s)")

        if form_input_count == 0:
            return is_answer_sent, fail_list

        # Determine multi-question mode
        is_multi_question_mode = False
        if form_input_count == 2 and len(answer_list) >= 2:
            if len(answer_list[0]) > 0 and len(answer_list[1]) > 0:
                is_multi_question_mode = True

        debug.log(f"[IBON VERIFY] Multi-question mode: {is_multi_question_mode}")
        debug.log(f"[IBON VERIFY] Answer list: {answer_list}")
        debug.log(f"[IBON VERIFY] Fail list: {fail_list}")

        if is_multi_question_mode:
            # Multi-field mode: fill answer_list[0] to first field, answer_list[1] to second
            answer_1 = answer_list[0]
            answer_2 = answer_list[1]
            # JSON encode for safe JavaScript string insertion
            answer_1_js = json.dumps(answer_1)
            answer_2_js = json.dumps(answer_2)

            # Fill both fields using JavaScript
            fill_result_raw = await tab.evaluate(f'''
                (function() {{
                    var inputs = document.querySelectorAll("{input_text_css}");
                    if (inputs.length >= 2) {{
                        var answer1 = {answer_1_js};
                        var answer2 = {answer_2_js};

                        if (inputs[0].value !== answer1) {{
                            inputs[0].value = "";
                            inputs[0].value = answer1;
                            inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}

                        if (inputs[1].value !== answer2) {{
                            inputs[1].value = "";
                            inputs[1].value = answer2;
                            inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inputs[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}

                        return true;
                    }}
                    return false;
                }})()
            ''')

            # Handle tuple result from NoDriver
            fill_result = fill_result_raw
            if isinstance(fill_result_raw, tuple) and len(fill_result_raw) >= 1:
                fill_result = fill_result_raw[0]

            if fill_result:
                debug.log(f"[IBON VERIFY] Filled multi-field: '{answer_1}' and '{answer_2}'")

                # Click submit button
                try:
                    btn = await tab.query_selector(next_step_button_css)
                    if btn:
                        await btn.click()
                        is_answer_sent = True
                        fail_list.append(answer_1)
                        fail_list.append(answer_2)
                        debug.log(f"[IBON VERIFY] Submitted multi-field answers")
                except Exception as btn_exc:
                    debug.log(f"[IBON VERIFY] Click button error: {btn_exc}")

        else:
            # Single-field mode: find first answer not in fail_list
            inferred_answer = ""
            for answer in answer_list:
                if answer not in fail_list:
                    inferred_answer = answer
                    break

            if len(inferred_answer) > 0:
                # JSON encode for safe JavaScript string insertion
                inferred_answer_js = json.dumps(inferred_answer)
                # Fill the answer
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{input_text_css}");
                        if (input) {{
                            input.value = "";
                            input.value = {inferred_answer_js};
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()
                ''')

                debug.log(f"[IBON VERIFY] Filled single-field: '{inferred_answer}'")

                # Click submit button
                try:
                    btn = await tab.query_selector(next_step_button_css)
                    if btn:
                        await btn.click()
                        is_answer_sent = True
                        fail_list.append(inferred_answer)
                        debug.log(f"[IBON VERIFY] Submitted, attempt #{len(fail_list)}")
                except Exception as btn_exc:
                    debug.log(f"[IBON VERIFY] Click button error: {btn_exc}")
            else:
                # No answer to fill, focus the input
                debug.log("[IBON VERIFY] No answer available, focusing input")
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{input_text_css}");
                        if (input && document.activeElement !== input) {{
                            input.focus();
                        }}
                    }})()
                ''')

        if is_answer_sent:
            await asyncio.sleep(0.3)

    except Exception as exc:
        debug.log(f"[IBON VERIFY] Error: {exc}")

    return is_answer_sent, fail_list

async def nodriver_ibon_verification_question(tab, fail_list, config_dict):
    """
    Handle verification question on ibon with auto-fill support

    Features:
    - Reads answers from user_guess_string (user dictionary)
    - Supports first/last N chars extraction (e.g., "phone last 3 digits")
    - Auto-guess from question text (if auto_guess_options enabled)
    - Multi-field support

    Args:
        tab: NoDriver tab object
        fail_list: List of previously failed answers
        config_dict: Configuration dictionary

    Returns:
        list: Updated fail_list
    """
    debug = util.create_debug_logger(config_dict)

    # CSS selectors for ibon verification page
    # Note: use single quotes in CSS selector to avoid breaking JavaScript string
    INPUT_CSS = "#content div.form-group input[type='text'], #content div.form-group input:not([type]), div.editor-box input[type='text'], div.editor-box input:not([type])"
    SUBMIT_BTN_CSS = '#content a.btn, div.editor-box a.btn'

    try:
        # Get question texts from all form-groups (returns array)
        question_texts_raw = await tab.evaluate('''
            (function() {
                var questions = [];
                var content = document.querySelector('#content');
                if (content) {
                    // Get all form-groups with input fields
                    var formGroups = content.querySelectorAll('div.form-group');
                    formGroups.forEach(function(formGroup) {
                        // Only process form-groups that have input fields
                        if (formGroup.querySelector('input')) {
                            var span = formGroup.querySelector('span');
                            if (span) {
                                questions.push(span.textContent || span.innerText || '');
                            }
                        }
                    });
                }
                return questions;
            })()
        ''')

        # Handle NoDriver result format - may return tuple (result, exception) or array
        question_texts = []
        raw_data = question_texts_raw

        # If it's a tuple (result, exception), extract the result
        if isinstance(raw_data, tuple) and len(raw_data) >= 1:
            raw_data = raw_data[0]

        # Parse the result into a list of strings
        if isinstance(raw_data, list):
            for q in raw_data:
                if isinstance(q, dict) and 'value' in q:
                    # NoDriver format: {'type': 'string', 'value': '...'}
                    question_texts.append(str(q['value']))
                elif isinstance(q, str) and q:
                    question_texts.append(q)
        elif isinstance(raw_data, str) and raw_data:
            question_texts = [raw_data]

        # For backward compatibility, create combined question_text
        question_text = ' '.join(question_texts).strip()

        if len(question_text) > 0:
            debug.log(f"[IBON VERIFY] Question found: {question_text}")
            debug.log(f"[IBON VERIFY] Question count: {len(question_texts)}")

            # Write question to file for debugging
            write_question_to_file(question_text)

            # Step 1: Get answers from user dictionary
            answer_list = util.get_answer_list_from_user_guess_string(config_dict, CONST_MAXBOT_ANSWER_ONLINE_FILE)

            debug.log(f"[IBON VERIFY] User dictionary answers: {answer_list}")

            # Step 2: Smart extraction for multi-field forms
            # For each question, try to extract from its corresponding answer
            if len(answer_list) > 0 and len(question_texts) > 1:
                # Multi-field mode: extract answer for each question
                extracted_answers = []
                for idx, q_text in enumerate(question_texts):
                    if idx < len(answer_list):
                        # Only try to extract from THIS position's answer
                        extracted = util.extract_answer_by_question_pattern([answer_list[idx]], q_text)
                        if extracted:
                            extracted_answers.append(extracted)
                            debug.log(f"[IBON VERIFY] Q{idx+1} extracted from answer[{idx}]: {extracted}")
                        else:
                            # No pattern match, use original answer at this position
                            extracted_answers.append(answer_list[idx])
                            debug.log(f"[IBON VERIFY] Q{idx+1} using original: {answer_list[idx]}")

                # Replace answer_list with extracted answers if we got results
                if len(extracted_answers) >= len(question_texts):
                    answer_list = extracted_answers
                    debug.log(f"[IBON VERIFY] Final answers for multi-field: {answer_list}")

            elif len(answer_list) > 0:
                # Single-field mode: original logic
                extracted_answer = util.extract_answer_by_question_pattern(answer_list, question_text)
                if extracted_answer:
                    debug.log(f"[IBON VERIFY] Extracted answer by pattern: {extracted_answer}")
                    # Prepend extracted answer to the list for priority
                    if extracted_answer not in answer_list:
                        answer_list = [extracted_answer] + answer_list

            # Step 3: If no user dictionary and auto_guess enabled, try auto-guess
            if len(answer_list) == 0:
                if config_dict["advanced"].get("auto_guess_options", False):
                    answer_list = util.get_answer_list_from_question_string(None, question_text, config_dict)
                    debug.log(f"[IBON VERIFY] Auto-guessed answers: {answer_list}")

            # Step 4: Fill the form if we have answers
            if len(answer_list) > 0:
                is_answer_sent, fail_list = await nodriver_ibon_fill_verify_form(
                    tab, config_dict, answer_list, fail_list,
                    INPUT_CSS, SUBMIT_BTN_CSS
                )
                debug.log(f"[IBON VERIFY] Answer sent: {is_answer_sent}")
            else:
                debug.log("[IBON VERIFY] No answers available, waiting for user input")
                # Focus the input field
                await tab.evaluate(f'''
                    (function() {{
                        var input = document.querySelector("{INPUT_CSS}");
                        if (input && document.activeElement !== input) {{
                            input.focus();
                        }}
                    }})()
                ''')

    except Exception as e:
        debug.log(f"[IBON] Verification question error: {e}")

    return fail_list

async def nodriver_tour_ibon_event_detail(tab, config_dict):
    """
    Handle tour.ibon.com.tw event detail page (/event/{eventId})
    Click the purchase button to proceed to options page

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary

    Returns:
        bool: True if button clicked successfully
    """
    debug = util.create_debug_logger(config_dict)
    is_button_clicked = False

    try:
        debug.log("[TOUR IBON] Event detail page detected")

        # Find and click purchase button (multiple text variations)
        button_text_list = ["立即購票", "搶票", "購票", "Buy"]

        for button_text in button_text_list:
            try:
                # Use text-based selector to find button
                result = await tab.evaluate(f'''
                    (function() {{
                        var buttons = Array.from(document.querySelectorAll('button'));
                        var targetBtn = buttons.find(btn => btn.textContent.includes("{button_text}"));
                        if (targetBtn) {{
                            targetBtn.click();
                            return true;
                        }}
                        return false;
                    }})()
                ''')

                if result:
                    is_button_clicked = True
                    debug.log(f"[TOUR IBON] Clicked button: {button_text}")
                    break
            except Exception as e:
                debug.log(f"[TOUR IBON] Button click error ({button_text}): {e}")

        if not is_button_clicked:
            debug.log("[TOUR IBON] Purchase button not found")

    except Exception as e:
        debug.log(f"[TOUR IBON] Event detail error: {e}")

    return is_button_clicked

async def nodriver_tour_ibon_options(tab, config_dict):
    """
    Handle tour.ibon.com.tw options page (/event/{eventId}/options)
    Select ticket quantity -> Add to cart -> Confirm payment method

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary

    Returns:
        bool: True if all steps completed successfully
    """
    debug = util.create_debug_logger(config_dict)
    is_all_completed = False

    try:
        debug.log("[TOUR IBON] Options page detected")

        # Step 1: Select ticket quantity from <select> element
        # Support multiple ticket types with area_keyword matching
        ticket_number = config_dict.get("ticket_number", 2)

        # Get area keyword for ticket type matching
        area_keyword = ""
        area_auto_select_enable = config_dict.get("area_auto_select", {}).get("enable", False)
        if area_auto_select_enable:
            area_keyword = config_dict.get("area_auto_select", {}).get("area_keyword", "")
            area_keyword = util.format_keyword_string(area_keyword)

        try:
            # Step 1a: Get all ticket types from page
            ticket_types = await tab.evaluate('''
                (function() {
                    var headings = document.querySelectorAll('h4');
                    return Array.from(headings).map(h => h.textContent.trim());
                })()
            ''')

            # Step 1b: Find matching ticket type using Python util function
            target_index = 0  # Default to first ticket type
            if area_keyword and ticket_types:
                for i, ticket_name in enumerate(ticket_types):
                    if util.is_text_match_keyword(area_keyword, ticket_name):
                        target_index = i
                        debug.log(f"[TOUR IBON] Keyword '{area_keyword}' matched ticket: {ticket_name}")
                        break

            # Step 1c: Select quantity for the matched ticket type
            select_result = await tab.evaluate(f'''
                (function() {{
                    var targetIndex = {target_index};
                    var ticketNumber = "{ticket_number}";
                    var selects = document.querySelectorAll('select#input-qty, select[id*="qty"]');
                    var headings = document.querySelectorAll('h4');

                    if (selects.length > targetIndex) {{
                        var select = selects[targetIndex];
                        select.value = ticketNumber;
                        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{
                            success: true,
                            index: targetIndex,
                            ticketName: headings[targetIndex] ? headings[targetIndex].textContent.trim() : '',
                            value: select.value
                        }};
                    }}
                    return {{ success: false, reason: 'no select found', selectCount: selects.length }};
                }})()
            ''')

            if select_result and isinstance(select_result, dict) and select_result.get('success'):
                debug.log(f"[TOUR IBON] Selected ticket: {select_result.get('ticketName', 'unknown')}, quantity: {ticket_number}")

        except Exception as e:
            debug.log(f"[TOUR IBON] Quantity selection error: {e}")

        # Step 2: Click the ENABLED "加入訂購" button (only enabled after quantity selected)
        await asyncio.sleep(0.3)

        try:
            result = await tab.evaluate('''
                (function() {
                    var buttons = Array.from(document.querySelectorAll('button'));
                    // Find enabled "加入訂購" button (disabled buttons have disabled attribute)
                    var addBtn = buttons.find(btn =>
                        btn.textContent.includes("加入訂購") && !btn.disabled
                    );
                    if (addBtn) {
                        addBtn.click();
                        return { success: true };
                    }
                    // If no enabled button found, report all button states
                    var allAddBtns = buttons.filter(btn => btn.textContent.includes("加入訂購"));
                    return {
                        success: false,
                        reason: 'no enabled button',
                        buttonCount: allAddBtns.length,
                        allDisabled: allAddBtns.every(btn => btn.disabled)
                    };
                })()
            ''')

            if result and isinstance(result, dict) and result.get('success'):
                debug.log("[TOUR IBON] Clicked: 加入訂購")
            elif result and isinstance(result, dict) and not result.get('success'):
                debug.log(f"[TOUR IBON] Add button not ready: {result.get('reason')}")
        except Exception as e:
            debug.log(f"[TOUR IBON] Add to cart error: {e}")

        # Step 3: Wait and click "確認付款方式" button
        await asyncio.sleep(0.5)

        try:
            result = await tab.evaluate('''
                (function() {
                    var buttons = Array.from(document.querySelectorAll('button'));
                    var confirmBtn = buttons.find(btn => btn.textContent.includes("確認付款方式"));
                    if (confirmBtn) {
                        confirmBtn.click();
                        return true;
                    }
                    return false;
                })()
            ''')

            if result:
                is_all_completed = True
                debug.log("[TOUR IBON] Clicked: 確認付款方式")
        except Exception as e:
            debug.log(f"[TOUR IBON] Confirm payment error: {e}")

    except Exception as e:
        debug.log(f"[TOUR IBON] Options page error: {e}")

    return is_all_completed

async def nodriver_tour_ibon_checkout(tab, config_dict):
    """
    Handle tour.ibon.com.tw checkout page (/event/{eventId}/checkout)
    Fill form (name, phone) -> Check agreement -> Submit

    Args:
        tab: NoDriver tab object
        config_dict: Configuration dictionary

    Returns:
        bool: True if form submitted successfully
    """
    debug = util.create_debug_logger(config_dict)
    is_form_submitted = False

    try:
        debug.log("[TOUR IBON] Checkout page detected")

        # Get personal data from config
        real_name = config_dict.get("contact", {}).get("real_name", "")
        phone = config_dict.get("contact", {}).get("phone", "")

        if not real_name or not phone:
            debug.log("[TOUR IBON] Missing contact data in settings")
            return False

        # JSON encode for safe JavaScript string insertion
        real_name_js = json.dumps(real_name)
        phone_js = json.dumps(phone)

        # Step 1: Fill real name and phone using fieldset structure
        try:
            result = await tab.evaluate(f'''
                (function() {{
                    var fieldsets = document.querySelectorAll('fieldset');
                    var nameInput = null;
                    var phoneInput = null;

                    fieldsets.forEach(function(fs) {{
                        var legend = fs.querySelector('legend');
                        var input = fs.querySelector('input');
                        if (legend && input && !input.readOnly) {{
                            if (legend.textContent.includes('真實姓名')) nameInput = input;
                            if (legend.textContent.includes('手機號碼')) phoneInput = input;
                        }}
                    }});

                    var results = {{ name: false, phone: false }};

                    if (nameInput) {{
                        nameInput.focus();
                        nameInput.value = {real_name_js};
                        nameInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        nameInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        nameInput.blur();
                        results.name = true;
                    }}

                    if (phoneInput) {{
                        phoneInput.focus();
                        phoneInput.value = {phone_js};
                        phoneInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        phoneInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        phoneInput.blur();
                        results.phone = true;
                    }}

                    return results;
                }})()
            ''')

            if result and isinstance(result, dict):
                if result.get('name'):
                    debug.log(f"[TOUR IBON] Filled name: {real_name}")
                if result.get('phone'):
                    debug.log(f"[TOUR IBON] Filled phone: {phone}")
        except Exception as e:
            debug.log(f"[TOUR IBON] Form fill error: {e}")

        # Step 2: Check agreement checkbox (wait for form validation first)
        await asyncio.sleep(0.5)

        try:
            result = await tab.evaluate('''
                (function() {
                    // Try by id first, then fallback to search
                    var agreeCheckbox = document.getElementById('agreeCheck');
                    if (!agreeCheckbox) {
                        var checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                        agreeCheckbox = checkboxes.find(cb => {
                            var parent = cb.closest('div');
                            return parent && parent.textContent.includes("我已詳閱");
                        });
                    }
                    if (agreeCheckbox && !agreeCheckbox.checked) {
                        agreeCheckbox.click();
                        return { clicked: true, checked: agreeCheckbox.checked };
                    }
                    return { clicked: false, checked: agreeCheckbox ? agreeCheckbox.checked : false };
                })()
            ''')

            if result:
                debug.log(f"[TOUR IBON] Agreement checkbox: {result}")
        except Exception as e:
            debug.log(f"[TOUR IBON] Checkbox error: {e}")

        # Step 3: Click submit button (下一步) - wait for validation to complete
        await asyncio.sleep(0.5)

        try:
            result = await tab.evaluate('''
                (function() {
                    var buttons = Array.from(document.querySelectorAll('button'));
                    var submitBtn = buttons.find(btn => btn.textContent.includes("下一步") && !btn.disabled);
                    if (submitBtn) {
                        submitBtn.click();
                        return true;
                    }
                    return false;
                })()
            ''')

            if result:
                is_form_submitted = True
                debug.log("[TOUR IBON] Clicked: 下一步")
        except Exception as e:
            debug.log(f"[TOUR IBON] Submit error: {e}")

    except Exception as e:
        debug.log(f"[TOUR IBON] Checkout error: {e}")

    return is_form_submitted

async def nodriver_ibon_main(tab, url, config_dict, ocr, Captcha_Browser):
    # 函數開始時檢查暫停
    if await check_and_handle_pause(config_dict):
        return False
    if not _state:
        _state.update({
            "fail_list": [],
            "is_popup_checkout": False,
            "played_sound_order": False,
            "queue_it_enter_time": None,
            "shown_checkout_message": False,
            "alert_handler_registered": False,
            "livemap_failed_areas": {},
            "livemap_last_attempt": None,
            "played_sound_ticket": False,
            "last_homepage_redirect_time": 0,
        })

    # Check if kicked to login page (Cookie/Session expired)
    debug = util.create_debug_logger(config_dict)

    # Global alert handler - auto-dismiss iBon alerts (sold-out, errors, etc.)
    async def handle_ibon_alert(event):
        # Skip alert handling when bot is paused (let user handle manually)
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            return

        # Skip checkout page - let user handle important alerts manually
        current_url = tab.target.url if (tab and hasattr(tab, 'target') and tab.target) else ""
        if '/utk02/utk0206_' in current_url.lower():
            debug.log(f"[IBON ALERT] Alert on checkout page, NOT auto-dismissing: '{event.message}'")
            return

        debug.log(f"[IBON ALERT] Alert detected: '{event.message}'")

        # Dismiss the alert - try multiple times with small delays
        for attempt in range(3):
            try:
                await tab.send(cdp.page.handle_java_script_dialog(accept=True))
                debug.log(f"[IBON ALERT] Alert dismissed (attempt {attempt + 1})")
                break
            except Exception as dismiss_exc:
                error_msg = str(dismiss_exc)
                # CDP -32602 means no dialog is showing (already dismissed by local handler)
                if "No dialog is showing" in error_msg or "-32602" in error_msg:
                    debug.log("[IBON ALERT] Dialog already dismissed")
                    break
                if attempt < 2:
                    await asyncio.sleep(0.1)
                else:
                    debug.log(f"[IBON ALERT] Failed to dismiss alert: {dismiss_exc}")

    # Register global alert handler (only once per session)
    if not _state.get("alert_handler_registered", False):
        try:
            tab.add_handler(cdp.page.JavascriptDialogOpening, handle_ibon_alert)
            _state["alert_handler_registered"] = True
            debug.log("[IBON ALERT] Global alert handler registered")
        except Exception as handler_exc:
            debug.log(f"[IBON ALERT] Failed to register alert handler: {handler_exc}")

    # Queue-IT detection: track enter/exit time for diagnostics
    url_lower = url.lower()
    if 'queue-it.net' in url_lower:
        if _state.get("queue_it_enter_time") is None:
            import time as _time
            _state["queue_it_enter_time"] = _time.time()
            debug.log("[IBON] Queue-IT entered, waiting...")
        return False
    else:
        if _state.get("queue_it_enter_time") is not None:
            import time as _time
            elapsed = _time.time() - _state["queue_it_enter_time"]
            debug.log(f"[IBON] Queue-IT passed (waited {elapsed:.1f}s)")
            _state["queue_it_enter_time"] = None

    is_login_page = False
    target_url = None

    # Detect login page patterns
    # Support both patterns: /huiwan/loginhuiwan and /huiwan//loginhuiwan (with double slash)
    if 'huiwan.ibon.com.tw' in url_lower and 'loginhuiwan' in url_lower:
        is_login_page = True
        # Extract target URL from query parameter
        if 'targeturl=' in url.lower():
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'targeturl' in params:
                    target_url = params['targeturl'][0]
            except:
                pass
        if debug.enabled:
            debug.log(f"[IBON LOGIN] Detected login page redirect")
            if target_url:
                debug.log(f"[IBON LOGIN] Target URL: {target_url}")

    # If kicked to login page, re-login and redirect back
    if is_login_page:
        debug.log("[IBON LOGIN] Re-authenticating with cookie...")

        # Re-execute login process (get driver from tab.browser)
        driver = getattr(tab, 'browser', None)
        login_result = await nodriver_ibon_login(tab, config_dict, driver)

        if debug.enabled:
            if login_result['success']:
                debug.log("[IBON LOGIN] Re-authentication successful")
            else:
                debug.log(f"[IBON LOGIN] Re-authentication failed: {login_result.get('error', 'Unknown error')}")

        # Redirect back to target URL or homepage
        if target_url and target_url.startswith('http'):
            debug.log(f"[IBON LOGIN] Redirecting to target: {target_url}")
            try:
                await tab.get(target_url)
                await asyncio.sleep(2)
            except Exception as e:
                debug.log(f"[IBON LOGIN] Redirect failed: {e}")
        else:
            # No target URL, go to homepage
            config_homepage = config_dict["homepage"]
            debug.log(f"[IBON LOGIN] No target URL, redirecting to homepage: {config_homepage}")
            try:
                await tab.get(config_homepage)
                await asyncio.sleep(2)
            except Exception as e:
                debug.log(f"[IBON LOGIN] Homepage redirect failed: {e}")

        return False  # Don't quit bot, continue monitoring

    home_url_list = ['https://ticket.ibon.com.tw/'
    ,'https://ticket.ibon.com.tw/index/entertainment'
    ]
    for each_url in home_url_list:
        if each_url == url.lower():
            if config_dict["ocr_captcha"]["enable"]:
                # TODO:
                #set_non_browser_cookies(driver, url, Captcha_Browser)
                pass
            break

    # Auto-redirect if kicked back to homepage (防止被踢回首頁)
    # Pattern: Homepage → Target page redirection
    # - If homepage config is set to a specific page (ActivityInfo/orders/Event), redirect back when kicked to homepage
    # - If homepage config is homepage itself, skip redirect (normal behavior)
    is_kicked_to_homepage = False
    normalized_url = url.lower().rstrip('/')
    if normalized_url == 'https://ticket.ibon.com.tw' or normalized_url == 'https://ticket.ibon.com.tw/index/entertainment':
        is_kicked_to_homepage = True

    if is_kicked_to_homepage:
        config_homepage = config_dict["homepage"]
        # Only redirect if user wants to be on a specific page (not homepage itself)
        # Support all ibon page types: ActivityInfo, orders.ibon.com.tw, Event, EventBuy, etc.
        normalized_homepage = config_homepage.lower().rstrip('/')
        is_homepage_same_as_current = (
            normalized_homepage == 'https://ticket.ibon.com.tw' or
            normalized_homepage == 'https://ticket.ibon.com.tw/index/entertainment'
        )
        should_redirect = not is_homepage_same_as_current

        if should_redirect:
            current_time = time.time()
            last_redirect_time = _state.get("last_homepage_redirect_time", 0)
            redirect_interval = config_dict["advanced"].get("auto_reload_page_interval", 3)
            if redirect_interval <= 0:
                redirect_interval = 3

            if current_time - last_redirect_time > redirect_interval:
                debug.log(f"[IBON] Detected kicked back to homepage: {url}")
                debug.log(f"[IBON] Redirecting to config homepage: {config_homepage}")
                try:
                    _state["last_homepage_redirect_time"] = current_time
                    await tab.get(config_homepage)
                    await asyncio.sleep(2)
                    debug.log(f"[IBON] Successfully redirected to: {config_homepage}")
                except Exception as redirect_exc:
                    debug.log(f"[IBON] Redirect failed: {redirect_exc}")

            return False

    # tour.ibon.com.tw URL routing
    # https://tour.ibon.com.tw/event/{eventId}
    # https://tour.ibon.com.tw/event/{eventId}/options
    # https://tour.ibon.com.tw/event/{eventId}/checkout
    if 'tour.ibon.com.tw' in url.lower() and '/event/' in url.lower():
        url_parts = url.split('/')

        # Event detail page: /event/{eventId}
        if len(url_parts) == 5:
            await nodriver_tour_ibon_event_detail(tab, config_dict)

        # Options or checkout page: /event/{eventId}/options or /event/{eventId}/checkout
        elif len(url_parts) == 6:
            if '/options' in url.lower():
                await nodriver_tour_ibon_options(tab, config_dict)
            elif '/checkout' in url.lower():
                await nodriver_tour_ibon_checkout(tab, config_dict)

    is_match_target_feature = False

    #PS: ibon some utk is upper case, some is lower.
    if not is_match_target_feature:
        #https://ticket.ibon.com.tw/ActivityInfo/Details/0000?pattern=entertainment
        if '/activityinfo/details/' in url.lower():
            is_event_page = False
            if len(url.split('/'))==6:
                is_event_page = True

            if is_event_page:
                if config_dict["date_auto_select"]["enable"]:
                    is_match_target_feature = True
                    is_date_assign_by_bot = await nodriver_ibon_date_auto_select(tab, config_dict)

                    # If date selection failed, reload page
                    if not is_date_assign_by_bot:
                        debug = util.create_debug_logger(config_dict)
                        debug.log("[IBON DATE] Date selection failed, reloading page...")

                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            await asyncio.sleep(auto_reload_interval)

                        try:
                            await tab.reload()
                        except:
                            pass

    if 'ibon.com.tw/error.html?' in url.lower():
        try:
            tab.back()
        except Exception as exc:
            pass

    is_enter_verify_mode = False
    if not is_match_target_feature:
        # validation question url:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_0.aspx?rn=1180872370&PERFORMANCE_ID=B04M7XZT&PRODUCT_ID=B04KS88E&SHOW_PLACE_MAP=True
        is_event_page = False
        if '/UTK02/UTK0201_0.' in url.upper():
            if '.aspx?' in url.lower():
                if 'rn=' in url.lower():
                    if 'PERFORMANCE_ID=' in url.upper():
                        if "PRODUCT_ID=" in url.upper():
                            is_event_page = True

        if is_event_page:
            is_enter_verify_mode = True
            _state["fail_list"] = await nodriver_ibon_verification_question(tab, _state["fail_list"], config_dict)
            is_match_target_feature = True

    if not is_enter_verify_mode:
        _state["fail_list"] = []

    if not is_match_target_feature:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=0000
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?rn=1111&PERFORMANCE_ID=2222&PRODUCT_ID=BBBB
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_001.aspx?PERFORMANCE_ID=2222&GROUP_ID=4&PERFORMANCE_PRICE_AREA_ID=3333

        is_event_page = False
        if '/UTK02/UTK0201_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if '/UTK02/UTK0202_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if is_event_page:
            # Check if area is already selected (avoid duplicate selection causing double tickets)
            is_area_already_selected = 'PERFORMANCE_PRICE_AREA_ID=' in url.upper()

            if config_dict["area_auto_select"]["enable"] and not is_area_already_selected:
                is_match_target_feature = True
                area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

                # === live.map fast-path: skip DOM parsing by fetching area data from CDN ===
                # Python requests bypasses browser network layer, unaffected by CDP blocking rules.
                # NOTE: CDN remaining data can be stale (sold-out areas may show remaining > 0).
                # A failed-area blacklist prevents infinite loops when CDN data is wrong.
                try:
                    from urllib.parse import urlparse, parse_qs
                    parsed_url = urlparse(url)
                    qs_params = parse_qs(parsed_url.query, keep_blank_values=True)
                    perf_id = None
                    for key in qs_params:
                        if key.upper() == 'PERFORMANCE_ID':
                            perf_id = qs_params[key][0]
                            break

                    if perf_id:
                        livemap_debug = util.create_debug_logger(config_dict)

                        # Check if last fast-path attempt failed (we're back on area selection)
                        last_attempt = _state.get("livemap_last_attempt")
                        if last_attempt and last_attempt.get("perf_id") == perf_id:
                            failed_area_id = last_attempt["area_id"]
                            failed_area_name = last_attempt.get("area_name", "")
                            failed_set = _state["livemap_failed_areas"].setdefault(perf_id, set())
                            failed_set.add(failed_area_id)
                            _state["livemap_last_attempt"] = None
                            livemap_debug.log(f"[IBON LIVEMAP] Area '{failed_area_name}' (id={failed_area_id}) sold out, added to blacklist ({len(failed_set)} total)")

                        livemap_areas = util.ibon_fetch_and_parse_livemap(perf_id, livemap_debug)

                        if livemap_areas:
                            # Filter out previously failed areas (stale CDN data)
                            failed_set = _state["livemap_failed_areas"].get(perf_id, set())
                            if failed_set:
                                livemap_areas = [a for a in livemap_areas if a['area_id'] not in failed_set]
                                livemap_debug.log(f"[IBON LIVEMAP] Filtered {len(failed_set)} failed areas, {len(livemap_areas)} remaining")

                            livemap_selected = None

                            if livemap_areas:
                                if len(area_keyword) > 0:
                                    livemap_kw_array = []
                                    try:
                                        import json as _json
                                        livemap_kw_array = _json.loads("[" + area_keyword + "]")
                                    except Exception:
                                        livemap_kw_array = []

                                    for livemap_kw_item in livemap_kw_array:
                                        livemap_selected = util.ibon_livemap_select_area(livemap_areas, config_dict, livemap_kw_item, debug=livemap_debug)
                                        if livemap_selected:
                                            break
                                else:
                                    livemap_selected = util.ibon_livemap_select_area(livemap_areas, config_dict, area_keyword, debug=livemap_debug)

                            if livemap_selected:
                                skip_url = util.ibon_build_skip_url(livemap_selected)
                                livemap_debug.log(f"[IBON LIVEMAP] Fast-path: {livemap_selected['area_name']} (remaining: {livemap_selected['remaining']}) -> {skip_url}")
                                debug.log(f"[IBON LIVEMAP] Fast-path: {livemap_selected['area_name']} -> skip to next step")
                                # Track this attempt so we can blacklist if it fails
                                _state["livemap_last_attempt"] = {
                                    "perf_id": perf_id,
                                    "area_id": livemap_selected['area_id'],
                                    "area_name": livemap_selected['area_name'],
                                }
                                await tab.get(skip_url)
                                return False
                            else:
                                livemap_debug.log("[IBON LIVEMAP] No matching area after filtering, falling back to DOM flow")
                        else:
                            livemap_debug.log("[IBON LIVEMAP] No areas parsed, falling back to DOM flow")
                except Exception as exc:
                    livemap_debug.log(f"[IBON LIVEMAP] Fast-path error: {exc}")
                # === end live.map fast-path ===

                is_need_refresh = False
                is_price_assign_by_bot = False

                if len(area_keyword) > 0:
                    area_keyword_array = []
                    try:
                        import json
                        area_keyword_array = json.loads("["+ area_keyword +"]")
                    except Exception as exc:
                        area_keyword_array = []

                    for area_keyword_item in area_keyword_array:
                        is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_area_auto_select(tab, config_dict, area_keyword_item)
                        if not is_need_refresh:
                            break

                    # Fallback: If all keyword groups failed, check area_auto_fallback setting
                    if not is_price_assign_by_bot:
                        if is_need_refresh:
                            area_auto_fallback = config_dict.get("area_auto_fallback", False)
                            if area_auto_fallback:
                                # Feature 003: Fallback enabled - use auto_select_mode without keyword
                                debug = util.create_debug_logger(config_dict)
                                auto_select_mode = config_dict["area_auto_select"]["mode"]
                                debug.log(f"[IBON AREA] All keyword groups failed, area_auto_fallback=true")
                                debug.log(f"[IBON AREA] Falling back to auto_select_mode: {auto_select_mode}")
                                is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_area_auto_select(tab, config_dict, "")
                            else:
                                # Feature 003: Fallback disabled - strict mode (no selection, will reload)
                                debug = util.create_debug_logger(config_dict)
                                debug.log(f"[IBON AREA] All keyword groups failed, area_auto_fallback=false")
                                debug.log(f"[IBON AREA] No area selected, will reload page and retry")
                                # Keep is_price_assign_by_bot=False and is_need_refresh=True
                                # This will trigger page reload in the outer loop
                else:
                    # empty keyword, match all.
                    is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_area_auto_select(tab, config_dict, area_keyword)

                if is_need_refresh:
                    debug = util.create_debug_logger(config_dict)
                    debug.log("[IBON ORDERS] No available areas found, page reload required")

                    auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                    if auto_reload_interval > 0:
                        await asyncio.sleep(auto_reload_interval)

                    try:
                        await tab.reload()
                    except Exception as exc:
                        pass

                # Check if we need to handle ticket number and captcha (UTK0201_001 page)
                is_do_ibon_performance_with_ticket_number = False

                # UTK0201_001 page: has PERFORMANCE_PRICE_AREA_ID parameter
                if 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
                    is_do_ibon_performance_with_ticket_number = True

                # UTK0201_000 page: check if ticket selection appears on same page
                if 'PRODUCT_ID=' in url.upper():
                    if not is_price_assign_by_bot:
                        # This case shows captcha and ticket-number on the same page
                        # Check if ticket number dropdown exists
                        try:
                            selector = 'table.table > tbody > tr > td > select'
                            form_select = await tab.query_selector(selector)
                            if form_select:
                                is_do_ibon_performance_with_ticket_number = True
                        except Exception as exc:
                            pass

                if is_do_ibon_performance_with_ticket_number:
                    # Wait for page to load before checking sold-out (prevents false detection)
                    debug = util.create_debug_logger(config_dict)
                    await nodriver_ibon_wait_for_select_elements(tab, config_dict)

                    # Step 0: Check if tickets are sold out FIRST (before OCR)
                    is_sold_out_detected = await nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict)

                    if is_sold_out_detected:
                        debug.log("[IBON] All tickets sold out, navigating to area selection...")

                        # Fix (2026-01-07): Navigate to area selection instead of reload (prevents infinite loop)
                        await nodriver_ibon_navigate_on_sold_out(tab, config_dict)

                        # Wait before next check (FR-061: auto_reload_page_interval)
                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            debug.log(f"[AUTO RELOAD] Waiting {auto_reload_interval} seconds before next check...")
                            await asyncio.sleep(auto_reload_interval)

                        return False  # Return to main loop to continue monitoring

                    # Livemap fast-path area verified: has tickets, clear the attempt tracker
                    _state["livemap_last_attempt"] = None

                    # Step 1: Handle non-adjacent seat checkbox
                    if config_dict["advanced"]["disable_adjacent_seat"]:
                        try:
                            await nodriver_ibon_allow_not_adjacent_seat(tab, config_dict)
                        except Exception as exc:
                            debug.log(f"[IBON] Checkbox error: {exc}")

                    # Step 2: Assign ticket number FIRST (before captcha)
                    # Fix (2026-01-07): Captcha auto_submit checks if ticket number is selected.
                    # Must select ticket number first, then process captcha.
                    is_ticket_number_assigned = False
                    max_retries = 3

                    try:
                        for attempt in range(1, max_retries + 1):
                            is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

                            if is_ticket_number_assigned:
                                if attempt > 1:
                                    debug.log(f"[TICKET RETRY] Success after {attempt} attempt(s)")
                                break

                            if attempt < max_retries:
                                delay = 0.5 * (2 ** (attempt - 1))
                                debug.log(f"[TICKET RETRY] Attempt {attempt}/{max_retries} failed, waiting {delay}s (exponential backoff)")
                                await asyncio_sleep_with_pause_check(delay, config_dict)

                        if is_ticket_number_assigned:
                            # Wait for iBon to process ticket number change
                            await asyncio.sleep(random.uniform(0.15, 0.25))
                    except Exception as exc:
                        debug.log(f"[IBON] Ticket number error: {exc}")

                    # Step 3: Handle captcha (after ticket number is selected)
                    is_captcha_sent = False
                    try:
                        ocr = None
                        if config_dict["ocr_captcha"]["enable"]:
                            import ddddocr
                            ocr = create_universal_ocr(config_dict)
                            if ocr is None:
                                ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
                                ocr.set_ranges(0)
                        is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)
                    except Exception as exc:
                        debug.log(f"[IBON] Captcha error: {exc}")

                    # Step 3.5: Final check if tickets are sold out (backup check)
                    if not is_ticket_number_assigned:
                        is_sold_out_detected = await nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict)

                        if is_sold_out_detected:
                            debug.log("[IBON] All tickets sold out, navigating to area selection...")

                            # Fix (2026-01-07): Navigate to area selection instead of reload (prevents infinite loop)
                            await nodriver_ibon_navigate_on_sold_out(tab, config_dict)

                            # Wait before next check (FR-061: auto_reload_page_interval)
                            auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                            if auto_reload_interval > 0:
                                debug.log(f"[AUTO RELOAD] Waiting {auto_reload_interval} seconds before next check...")
                                await asyncio.sleep(auto_reload_interval)

                            return False  # Return to main loop to continue monitoring

                    # Step 4: Submit purchase
                    if is_ticket_number_assigned and is_captcha_sent:
                        try:
                            click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)
                            if click_ret:
                                # Play "ticket" sound when attempting to enter checkout (found ticket)
                                if not _state.get("played_sound_ticket", False):
                                    if config_dict["advanced"]["play_sound"]["ticket"]:
                                        play_sound_while_ordering(config_dict)
                                    _state["played_sound_ticket"] = True
                        except Exception as exc:
                            debug = util.create_debug_logger(config_dict)
                            debug.log(f"[IBON] Submit button error: {exc}")

            # Handle case when area is already selected (direct access to UTK0201_001 page)
            elif is_area_already_selected:
                is_match_target_feature = True
                debug = util.create_debug_logger(config_dict)

                debug.log("[IBON] Area already selected, checking ticket availability...")

                # Check if we need to handle ticket number and captcha (UTK0201_001 page)
                is_do_ibon_performance_with_ticket_number = False

                # UTK0201_001 page: has PERFORMANCE_PRICE_AREA_ID parameter
                if 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
                    is_do_ibon_performance_with_ticket_number = True

                if is_do_ibon_performance_with_ticket_number:
                    # Wait for page to load before checking sold-out (prevents false detection)
                    await nodriver_ibon_wait_for_select_elements(tab, config_dict)

                    # Step 0: Check if tickets are sold out FIRST (before OCR)
                    is_sold_out_detected = await nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict)

                    if is_sold_out_detected:
                        debug.log("[IBON] All tickets sold out, navigating to area selection...")

                        # Fix (2026-01-07): Navigate to area selection instead of reload (prevents infinite loop)
                        await nodriver_ibon_navigate_on_sold_out(tab, config_dict)

                        # Wait before next check (FR-061: auto_reload_page_interval)
                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            debug.log(f"[AUTO RELOAD] Waiting {auto_reload_interval} seconds before next check...")
                            await asyncio.sleep(auto_reload_interval)

                        return False  # Return to main loop to continue monitoring

                    # Livemap fast-path area verified: has tickets, clear the attempt tracker
                    _state["livemap_last_attempt"] = None

                    # Step 1: Handle non-adjacent seat checkbox
                    if config_dict["advanced"]["disable_adjacent_seat"]:
                        try:
                            await nodriver_ibon_allow_not_adjacent_seat(tab, config_dict)
                        except Exception as exc:
                            debug.log(f"[IBON] Checkbox error: {exc}")

                    # Step 2: Handle captcha (only executed when tickets are available)
                    is_captcha_sent = False
                    try:
                        ocr = None
                        if config_dict["ocr_captcha"]["enable"]:
                            import ddddocr
                            ocr = create_universal_ocr(config_dict)
                            if ocr is None:
                                ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
                                ocr.set_ranges(0)
                        is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)
                    except Exception as exc:
                        debug.log(f"[IBON] Captcha error: {exc}")

                    # Step 3: Assign ticket number with retry
                    is_ticket_number_assigned = False
                    max_retries = 3

                    try:
                        for attempt in range(1, max_retries + 1):
                            is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

                            if is_ticket_number_assigned:
                                if attempt > 1:
                                    debug.log(f"[TICKET RETRY] Success after {attempt} attempt(s)")
                                break

                            if attempt < max_retries:
                                delay = 0.5 * (2 ** (attempt - 1))
                                debug.log(f"[TICKET RETRY] Attempt {attempt}/{max_retries} failed, waiting {delay}s")
                                await asyncio_sleep_with_pause_check(delay, config_dict)

                        if is_ticket_number_assigned:
                            # Wait for iBon to process ticket number change
                            await asyncio.sleep(random.uniform(0.15, 0.25))
                    except Exception as exc:
                        debug.log(f"[IBON] Ticket number error: {exc}")

                    # Step 3.5: Final check if tickets are sold out (backup check)
                    if not is_ticket_number_assigned:
                        is_sold_out_detected = await nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict)

                        if is_sold_out_detected:
                            debug.log("[IBON] All tickets sold out, navigating to area selection...")

                            # Fix (2026-01-07): Navigate to area selection instead of reload (prevents infinite loop)
                            await nodriver_ibon_navigate_on_sold_out(tab, config_dict)

                            # Wait before next check (FR-061: auto_reload_page_interval)
                            auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                            if auto_reload_interval > 0:
                                debug.log(f"[AUTO RELOAD] Waiting {auto_reload_interval} seconds before next check...")
                                await asyncio.sleep(auto_reload_interval)

                            return False  # Return to main loop to continue monitoring

                    # Step 4: Submit purchase
                    if is_ticket_number_assigned and is_captcha_sent:
                        try:
                            click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)
                            if click_ret:
                                # Play "ticket" sound when attempting to enter checkout (found ticket)
                                if not _state.get("played_sound_ticket", False):
                                    if config_dict["advanced"]["play_sound"]["ticket"]:
                                        play_sound_while_ordering(config_dict)
                                    _state["played_sound_ticket"] = True
                        except Exception as exc:
                            debug.log(f"[IBON] Submit button error: {exc}")

    # New ibon Event page format (Angular SPA): https://ticket.ibon.com.tw/Event/{eventId}/{sessionId}[/{activityId}]
    if not is_match_target_feature:
        is_new_event_page = False
        if 'ticket.ibon.com.tw' in url.lower() and '/event/' in url.lower():
            url_parts = url.split('/')
            # URL format: https://ticket.ibon.com.tw/Event/B09QY340/B09VO5KQ
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'Event', 'B09QY340', 'B09VO5KQ']
            # URL format (with activity ID): https://ticket.ibon.com.tw/Event/B09QY340/B09VO5KQ/39142
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'Event', 'B09QY340', 'B09VO5KQ', '39142']
            if len(url_parts) >= 6:
                is_new_event_page = True

        if is_new_event_page:
            if config_dict["area_auto_select"]["enable"]:
                is_match_target_feature = True
                area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

                is_need_refresh = False
                is_price_assign_by_bot = False

                if len(area_keyword) > 0:
                    area_keyword_array = []
                    try:
                        import json
                        area_keyword_array = json.loads("["+ area_keyword +"]")
                    except Exception as exc:
                        area_keyword_array = []

                    for area_keyword_item in area_keyword_array:
                        is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_event_area_auto_select(tab, config_dict, area_keyword_item)
                        if not is_need_refresh:
                            break

                    # Fallback: If all keyword groups failed, check area_auto_fallback setting
                    if not is_price_assign_by_bot:
                        if is_need_refresh:
                            area_auto_fallback = config_dict.get("area_auto_fallback", False)
                            if area_auto_fallback:
                                # Feature 003: Fallback enabled - use auto_select_mode without keyword
                                debug = util.create_debug_logger(config_dict)
                                auto_select_mode = config_dict["area_auto_select"]["mode"]
                                debug.log(f"[IBON EVENT] All keyword groups failed, area_auto_fallback=true")
                                debug.log(f"[IBON EVENT] Falling back to auto_select_mode: {auto_select_mode}")
                                is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_event_area_auto_select(tab, config_dict, "")
                            else:
                                # Feature 003: Fallback disabled - strict mode (no selection, will reload)
                                debug = util.create_debug_logger(config_dict)
                                debug.log(f"[IBON EVENT] All keyword groups failed, area_auto_fallback=false")
                                debug.log(f"[IBON EVENT] No area selected, will reload page and retry")
                                # Keep is_price_assign_by_bot=False and is_need_refresh=True
                                # This will trigger page reload in the outer loop
                else:
                    # empty keyword, match all.
                    is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_event_area_auto_select(tab, config_dict, area_keyword)

                debug = util.create_debug_logger(config_dict)
                debug.log(f"[NEW EVENT] Area selection result - is_price_assign_by_bot: {is_price_assign_by_bot}, is_need_refresh: {is_need_refresh}")

                # Auto-reload if no available ticket areas found
                if is_need_refresh:
                    debug.log("[NEW EVENT] No available ticket areas found, page reload required")

                    # Use auto_reload_page_interval setting
                    auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                    if auto_reload_interval > 0:
                        await asyncio.sleep(auto_reload_interval)

                    try:
                        await tab.reload()
                        debug.log("[NEW EVENT] Page reloaded successfully")
                    except Exception as reload_exc:
                        debug.log(f"[NEW EVENT] Page reload failed: {reload_exc}")

            is_match_target_feature = True

    # New ibon EventBuy page format: https://ticket.ibon.com.tw/EventBuy/{eventId}/{sessionId}/{areaId}[/{activityId}]
    if not is_match_target_feature:
        is_new_eventbuy_page = False
        if 'ticket.ibon.com.tw' in url.lower() and '/eventbuy/' in url.lower():
            url_parts = url.split('/')
            # URL format: https://ticket.ibon.com.tw/EventBuy/B09QY340/B09VO5KQ/B09VO6K0
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'EventBuy', 'eventId', 'sessionId', 'areaId']
            # URL format (with activity ID): https://ticket.ibon.com.tw/EventBuy/B09QY340/B09VO5KQ/B09VSQGL/39142
            # Split result: ['https:', '', 'ticket.ibon.com.tw', 'EventBuy', 'B09QY340', 'B09VO5KQ', 'B09VSQGL', '39142']
            if len(url_parts) >= 7:
                is_new_eventbuy_page = True

        if is_new_eventbuy_page:
            is_match_target_feature = True
            debug = util.create_debug_logger(config_dict)

            debug.log("[NEW EVENTBUY] Processing EventBuy page")

            # Check disable_adjacent_seat
            if config_dict["advanced"]["disable_adjacent_seat"]:
                is_finish_checkbox_click = await nodriver_check_checkbox(tab, '.asp-checkbox > input[type="checkbox"]:not(:checked)')

            # Step 1: Assign ticket number first with retry (exponential backoff)
            is_ticket_number_assigned = False
            max_retries = 3
            debug = util.create_debug_logger(config_dict)

            for attempt in range(1, max_retries + 1):
                is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

                if is_ticket_number_assigned:
                    if attempt > 1:
                        debug.log(f"[TICKET RETRY] Success after {attempt} attempt(s)")
                    break

                if attempt < max_retries:
                    delay = 0.5 * (2 ** (attempt - 1))
                    debug.log(f"[TICKET RETRY] Attempt {attempt}/{max_retries} failed, waiting {delay}s (exponential backoff)")
                    await asyncio_sleep_with_pause_check(delay, config_dict)

            if is_ticket_number_assigned:
                # Wait for iBon to process ticket number change
                await asyncio.sleep(random.uniform(0.15, 0.25))

            # Step 2: Handle captcha after ticket number is selected
            is_captcha_sent = False
            if is_ticket_number_assigned:
                debug.log("[NEW EVENTBUY] Ticket number assigned, proceeding to captcha")

                # Extract model name from URL for captcha
                domain_name = url.split('/')[2]
                # For EventBuy, use sessionId as model name
                model_name = url.split('/')[5] if len(url.split('/')) > 5 else 'EventBuy'
                if len(model_name) > 7:
                    model_name = model_name[:7]
                captcha_url = '/pic.aspx?TYPE=%s' % (model_name)

                # Set cookies for Captcha_Browser if needed
                if not Captcha_Browser is None:
                    Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                ocr = None
                if config_dict["ocr_captcha"]["enable"]:
                    try:
                        import ddddocr
                        ocr = create_universal_ocr(config_dict)
                        if ocr is None:
                            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
                            ocr.set_ranges(0)
                    except Exception as exc:
                        debug.log(f"[NEW EVENTBUY] OCR init error: {exc}")

                # Call ibon captcha handler (handles both OCR and manual mode)
                is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)

            # Step 3: Click purchase button if everything is ready
            if is_ticket_number_assigned:
                if is_captcha_sent:
                    debug.log("[NEW EVENTBUY] Clicking purchase button")

                    click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)

                    # Play sound if button clicked successfully
                    if click_ret:
                        # Play "ticket" sound when attempting to enter checkout (found ticket)
                        if not _state.get("played_sound_ticket", False):
                            if config_dict["advanced"]["play_sound"]["ticket"]:
                                play_sound_while_ordering(config_dict)
                            _state["played_sound_ticket"] = True
                        debug.log("[NEW EVENTBUY] Purchase button clicked successfully")
            else:
                # Check if sold out: try event-level check first, then per-zone ticket page check
                is_sold_out = await nodriver_ibon_check_sold_out(tab, config_dict)
                if not is_sold_out:
                    is_sold_out = await nodriver_ibon_check_sold_out_on_ticket_page(tab, config_dict)
                if is_sold_out:
                    debug.log("[NEW EVENTBUY] Sold out detected, going back and refreshing")
                    try:
                        await tab.back()
                        await tab.reload()
                    except Exception as exc:
                        debug.log(f"[NEW EVENTBUY] Back/reload failed: {exc}")

    if not is_match_target_feature:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=0000
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?rn=1111&PERFORMANCE_ID=2222&PRODUCT_ID=BBBB
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_001.aspx?PERFORMANCE_ID=2222&GROUP_ID=4&PERFORMANCE_PRICE_AREA_ID=3333

        is_event_page = False
        if '/UTK02/UTK0201_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if '/UTK02/UTK0202_' in url.upper():
            if '.aspx?' in url.lower():
                if 'PERFORMANCE_ID=' in url.upper():
                    if len(url.split('/'))==6:
                        is_event_page = True

        if is_event_page:
            if config_dict["area_auto_select"]["enable"]:
                select_query = "tr.disbled"
                # TODO:
                #clean_tag_by_selector(driver,select_query)
                
                select_query = "tr.sold-out"
                # TODO:
                #clean_tag_by_selector(driver,select_query)

                is_do_ibon_performance_with_ticket_number = False

                # Check if area is already selected (avoid duplicate selection causing double tickets)
                is_area_already_selected = 'PERFORMANCE_PRICE_AREA_ID=' in url.upper()

                if 'PRODUCT_ID=' in url.upper() and not is_area_already_selected:
                    # step 1: select area.
                    is_price_assign_by_bot = False
                    debug = util.create_debug_logger(config_dict)

                    # Call area selection function (simplified version for testing)
                    # TODO: Implement nodriver_ibon_performance() wrapper with OR logic
                    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
                    is_need_refresh, is_price_assign_by_bot = await nodriver_ibon_area_auto_select(tab, config_dict, area_keyword)

                    debug.log(f"Area selection result - is_price_assign_by_bot: {is_price_assign_by_bot}, is_need_refresh: {is_need_refresh}")

                    # Auto-reload if no available ticket areas found
                    if is_need_refresh:
                        debug.log("[IBON AREA] No available ticket areas found, page reload required")

                        # Use auto_reload_page_interval setting
                        auto_reload_interval = config_dict["advanced"].get("auto_reload_page_interval", 0)
                        if auto_reload_interval > 0:
                            await asyncio.sleep(auto_reload_interval)

                        try:
                            await tab.reload()
                            debug.log("[IBON AREA] Page reloaded successfully")
                        except Exception as reload_exc:
                            debug.log(f"[IBON AREA] Page reload failed: {reload_exc}")

                    if not is_price_assign_by_bot:
                        # this case show captcha and ticket-number in this page.
                        # TODO:
                        #if ibon_ticket_number_appear(driver, config_dict):
                        #    is_do_ibon_performance_with_ticket_number = True
                        pass

                # Old ibon format handling
                if 'PERFORMANCE_PRICE_AREA_ID=' in url.upper():
                    is_do_ibon_performance_with_ticket_number = True

                if is_do_ibon_performance_with_ticket_number:
                    if config_dict["advanced"]["disable_adjacent_seat"]:
                        # TODO:
                        is_finish_checkbox_click = await nodriver_check_checkbox(tab, '.asp-checkbox > input[type="checkbox"]:not(:checked)')

                    # Step 1: Assign ticket number first with retry (exponential backoff)
                    is_match_target_feature = True
                    is_ticket_number_assigned = False
                    max_retries = 3
                    debug = util.create_debug_logger(config_dict)

                    for attempt in range(1, max_retries + 1):
                        is_ticket_number_assigned = await nodriver_ibon_ticket_number_auto_select(tab, config_dict)

                        if is_ticket_number_assigned:
                            if attempt > 1:
                                debug.log(f"[TICKET RETRY] Success after {attempt} attempt(s)")
                            break

                        if attempt < max_retries:
                            delay = 0.5 * (2 ** (attempt - 1))
                            debug.log(f"[TICKET RETRY] Attempt {attempt}/{max_retries} failed, waiting {delay}s (exponential backoff)")
                            await asyncio_sleep_with_pause_check(delay, config_dict)

                    if is_ticket_number_assigned:
                        # Wait for iBon to process ticket number change
                        await asyncio.sleep(random.uniform(0.15, 0.25))

                    # Step 2: Handle captcha after ticket number is selected
                    is_captcha_sent = False
                    if is_ticket_number_assigned:
                        domain_name = url.split('/')[2]
                        model_name = url.split('/')[5]
                        if len(model_name) > 7:
                            model_name=model_name[:7]
                        captcha_url = '/pic.aspx?TYPE=%s' % (model_name)

                        # Set cookies for Captcha_Browser if needed
                        if not Captcha_Browser is None:
                            Captcha_Browser.set_domain(domain_name, captcha_url=captcha_url)

                        ocr = None
                        if config_dict["ocr_captcha"]["enable"]:
                            try:
                                import ddddocr
                                ocr = create_universal_ocr(config_dict)
                                if ocr is None:
                                    ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
                                    ocr.set_ranges(0)
                            except Exception as exc:
                                debug.log(f"[IBON] OCR init error: {exc}")

                        # Call ibon captcha handler (handles both OCR and manual mode)
                        is_captcha_sent = await nodriver_ibon_captcha(tab, config_dict, ocr)
                    
                    #print("is_ticket_number_assigned:", is_ticket_number_assigned)
                    if is_ticket_number_assigned:
                        if is_captcha_sent:
                            click_ret = await nodriver_ibon_purchase_button_press(tab, config_dict)

                            # only this case: "ticket number CHANGED by bot" and "cpatcha sent" to play sound!
                            if click_ret:
                                # Play "ticket" sound when attempting to enter checkout (found ticket)
                                if not _state.get("played_sound_ticket", False):
                                    if config_dict["advanced"]["play_sound"]["ticket"]:
                                        play_sound_while_ordering(config_dict)
                                    _state["played_sound_ticket"] = True
                    else:
                        is_sold_out = await nodriver_ibon_check_sold_out(tab, config_dict)
                        if is_sold_out:
                            debug.log("[IBON] is_sold_out, go back and refresh.")
                            # plan-A
                            #is_button_clicked = press_button(tab, By.CSS_SELECTOR, 'a.btn.btn-primary')
                            # plan-B, easy and better than plan-A
                            try:
                                tab.back()
                                tab.reload()
                            except Exception as exc:
                                pass

    if not is_match_target_feature:
        #https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
        is_event_page = False
        if '/UTK02/UTK020' in url.upper():
            if '.aspx' in url.lower():
                if len(url.split('/'))==6:
                    is_event_page = True

        # ignore "pay money" step.
        if '/UTK02/UTK0207_.ASPX' in url.upper():
            is_event_page = False

        if is_event_page:
            if is_event_page:
                is_match_target_feature = True
                is_finish_checkbox_click = await nodriver_ibon_ticket_agree(tab)
                if is_finish_checkbox_click:
                    is_name_based = False
                    try:
                        html_body = await tab.get_content()
                        #print("html_body:",len(html_body))
                        if html_body:
                            if len(html_body) > 1024:
                                if '實名制' in html_body:
                                    is_name_based = True
                    except Exception as exc:
                        #print(exc)
                        pass

                    if not is_name_based:
                        is_button_clicked = await nodriver_press_button(tab, 'a.btn.btn-pink.continue')

    # Check if reached checkout page (ticket purchase successful)
    # https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
    if '/utk02/utk0206_.aspx' in url.lower():
        # Show debug message (only once)
        if not _state["shown_checkout_message"]:
            debug.log("[IBON] Reached checkout page - ticket purchase successful!")
        _state["shown_checkout_message"] = True

        # Play sound notification (only once)
        if not _state["played_sound_order"]:
            if config_dict["advanced"]["play_sound"]["order"]:
                play_sound_while_ordering(config_dict)
            send_discord_notification(config_dict, "order", "iBon")
            send_telegram_notification(config_dict, "order", "iBon")
        _state["played_sound_order"] = True

        # If headless mode, open browser to show checkout page (only once)
        if config_dict["advanced"]["headless"]:
            if not _state["is_popup_checkout"]:
                checkout_url = url
                print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)
                _state["is_popup_checkout"] = True
    else:
        # Reset status when leaving checkout page
        _state["is_popup_checkout"] = False
        _state["played_sound_order"] = False
        _state["shown_checkout_message"] = False
    return tab

