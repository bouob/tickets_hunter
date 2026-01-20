# UDN Platform Analysis

## Platform Overview

| Item | Description |
|------|-------------|
| **Platform Family** | **KHAM Family** (shared UTK system with kham.com.tw, ticket.com.tw) |
| **URL Structure** | `tickets.udnfunlife.com/application/UTK0x/UTK0xxx_.aspx` |
| **Current Support** | Partial support in `nodriver_tixcraft.py` |

## Reference URLs

- Homepage: https://tickets.udnfunlife.com/application/utk01/utk0101_.aspx
- Concert: https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P12YQQ5C
- Event 2: https://tickets.udnfunlife.com/Application/UTK02/UTK0201_.aspx?PRODUCT_ID=P13EVEWY
- Event 3: https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P0ZS0ZFD&kdid=A05

## Purchase Flow (5 Steps)

```
UTK0101 (Homepage/Login)
    -> UTK0201 (Event Details - "Buy Now" button)
    -> UTK0203 (Date/Session Selection - "Go to Purchase" button)
    -> UTK0204_00 (Price Area Selection - Click area row)
    -> Popup Window (Seat Selection - Manual seat clicking)
```

## Current Implementation Status

| Feature | Status | Implementation |
|---------|--------|----------------|
| Login | OK | `udn_login()` in chrome_tixcraft.py |
| Date Selection | OK | `nodriver_kham_date_auto_select()` |
| Area Selection | OK | `nodriver_kham_area_auto_select()` |
| Fast Buy API | Partial | `AUTOSEAT_BTN_Click` |
| **Seat Auto-Select** | MISSING | **UDN-specific per-seat selection mode** |
| **reCaptcha** | Skipped | UDN uses reCaptcha (not image captcha) |

## UDN vs KHAM Differences

| Item | KHAM/ticket.com | UDN |
|------|-----------------|-----|
| Seat Selection | Quantity + Auto-assign | **Per-seat manual selection** |
| Captcha | Image captcha | reCaptcha |
| Session Selector | `table.eventTABLE` | `div.yd_session-block` |
| Area Table | `table#salesTable` | `table.status` |
| Area Row | `tr.status_tr` | `tr.status_tr` (same) |

## HTML Structure Analysis

### Session Selection Page (UTK0203)

```html
<div class="yd_session-block">
    <div class="yd_session-time">2025/12/28 (Sun) 17:00</div>
    <div class="yd_session-text">Legacy TERA (address)</div>
    <div class="yd_session-row">
        <div class="yd_session-price">Price: 640, 1,280, 1,880, 2,880</div>
        <div class="yd_counterGroup">
            <div class="goNext" onclick="location.href='UTK0204_00.aspx?...'">Go to Purchase</div>
        </div>
    </div>
</div>
```

### Area Selection Page (UTK0204_00)

```html
<table class="status">
    <tr name="main" class="status_tr" id="P136HQOA"
        onclick="doCheckArea(this,'P136HQOA','Area B','True','13','3')">
        <td>
            <div class="colorblock" style="background-color:#DFAA90"></div>
            <input name="a_NAME" type="hidden" value="Area B">
            <input name="a_PRICE_STR" type="hidden" value="1880">
            <input name="remain" type="hidden" value="13">
        </td>
        <td data-title="Area:">Area B</td>
        <td data-title="Price:">1880</td>
        <td data-title="Available:">13</td>
    </tr>
    <!-- Sold out area has class="Soldout" -->
    <tr name="main" class="status_tr Soldout" id="P136HQO8">...</tr>
</table>
```

### Seat Selection Popup

```html
<!-- Each seat is a LayoutTableCell with description -->
<td title="Area B-Row 1-Seat 1" class="seat available">...</td>
<td title="Area B-Row 1-Seat 2" class="seat sold">...</td>
```

Seat status indicators:
- Gray: Available (selectable)
- Red: Sold out
- Orange: Already selected
- Green: Added to cart

## Key Selectors for UDN

| Element | Selector |
|---------|----------|
| Session Block | `div.yd_session-block` |
| Go to Purchase Button | `div.goNext` |
| Area Table | `table.status` |
| Area Row | `tr.status_tr` |
| Sold Out Area | `tr.status_tr.Soldout` |
| Seat Cell | `td[title]` or cell with description attribute |
| Fast Buy Button | `button[name="fastBuy"]` or `#buttonBuy` |

## Existing Code Locations

### nodriver_tixcraft.py

```python
# Line 16165-16183: UDN fast buy button
if 'udnfunlife.com' in domain_name:
    my_css_selector = 'button[name="fastBuy"]'

# Line 16390-16391: UDN session selector
elif 'udnfunlife.com' in domain_name:
    selector = "div.yd_session-block"

# Line 16425-16437: UDN availability check
if 'udnfunlife' in domain_name:
    if 'Go to Purchase' not in row_html:
        continue

# Line 16604-16605: UDN go to purchase button
if 'udnfunlife.com' in domain_name:
    button_selector = 'div.goNext'

# Line 17015-17016: UDN area table selector
elif 'udnfunlife' in domain_name:
    selector = "table.yd_ticketsTable > tbody > tr.main"

# Line 17382-17383: UDN reCaptcha skip
if 'udnfunlife' not in domain_name:
    is_captcha_sent = await nodriver_kham_captcha(...)
```

### chrome_tixcraft.py

```python
# Line 5627: udn_login function
def udn_login(driver, account, password):

# Line 8468-8473: UDN fast buy
if 'udnfunlife.com' in domain_name:
    my_css_selector = 'button[name="fastBuy"]'

# Line 8501-8502: UDN session selector
if 'udnfunlife.com' in domain_name:
    my_css_selector = "div.yd_session-block"

# Line 8703-8704: UDN area table
if "udnfunlife" in domain_name:
    my_css_selector = "table.yd_ticketsTable > tbody > tr.main"

# Line 8922-8943: UDN AUTOSEAT API call
js = """fetch("https://tickets.udnfunlife.com/Application/UTK01/UTK0101_009.aspx/AUTOSEAT_BTN_Click", {...})"""
```

## Development Notes

1. **Seat Selection is the Key Missing Feature**: UDN uses per-seat selection popup
2. **reCaptcha**: Currently skipped, may need Google reCaptcha bypass
3. **Fast Buy API**: `AUTOSEAT_BTN_Click` can bypass seat selection for some events
4. **Compatibility**: Must maintain compatibility with existing KHAM logic
