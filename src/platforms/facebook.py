#!/usr/bin/env python3
#encoding=utf-8
"""platforms/facebook.py -- Facebook login helper (2 functions, no state)."""

import asyncio
from zendriver import cdp

__all__ = [
    "nodriver_facebook_login",
    "nodriver_facebook_main",
]


async def nodriver_facebook_login(tab, facebook_account, facebook_password):
    if tab:
        try:
            account = await tab.query_selector("#email")
            if account:
                await account.send_keys(facebook_account)
            else:
                print("[FACEBOOK] account input not found")

            password = await tab.query_selector("#pass")
            if password:
                await password.send_keys(facebook_password)
                await tab.send(cdp.input_.dispatch_key_event("keyDown", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                await tab.send(cdp.input_.dispatch_key_event("keyUp", code="Enter", key="Enter", text="\r", windows_virtual_key_code=13))
                await asyncio.sleep(2)
            else:
                print("[FACEBOOK] password input not found")
        except Exception as e:
            print(f"[FACEBOOK] send_keys fail: {e}")
            pass


async def nodriver_facebook_main(tab, config_dict):
    facebook_account = config_dict["accounts"]["facebook_account"].strip()
    facebook_password = config_dict["accounts"]["facebook_password"].strip()
    if len(facebook_account) > 4:
        await nodriver_facebook_login(tab, facebook_account, facebook_password)
