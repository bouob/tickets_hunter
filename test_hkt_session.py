"""
Test script for hkt.hkticketing.com session login via localStorage
Requires both X-MZ-SESSION and FE-XSRF-TOKEN
"""
import asyncio
import json
import nodriver as uc
import time


async def test_hkt_session():
    # Session tokens to test
    hkt_session = "0fcb95dac9234347998e84fa9d661cf1"
    xsrf_token = ""  # Fill in your FE-XSRF-TOKEN here

    if not xsrf_token:
        print("[TEST] Please fill in your FE-XSRF-TOKEN in the script!")
        print("[TEST] Get it from DevTools -> Application -> Local Storage -> __STORAGE__ -> FE-XSRF-TOKEN.value")
        return

    print("[TEST] Starting browser...")
    driver = await uc.start()

    # First navigate to the site (localStorage requires same origin)
    print("[TEST] Navigating to hkt.hkticketing.com...")
    tab = await driver.get("https://hkt.hkticketing.com/hant/#/home")
    await asyncio.sleep(2)

    # Set both tokens in localStorage
    print(f"[TEST] Setting X-MZ-SESSION: {hkt_session[:10]}...")
    print(f"[TEST] Setting FE-XSRF-TOKEN: {xsrf_token[:10]}...")
    expire_time = int(time.time() * 1000) + (30 * 24 * 60 * 60 * 1000)  # 30 days

    result_str = await tab.evaluate(f'''
        (function() {{
            try {{
                var storage = localStorage.getItem('__STORAGE__');
                var data = storage ? JSON.parse(storage) : {{}};

                // Set X-MZ-SESSION
                data['X-MZ-SESSION'] = {{
                    expireTime: {expire_time},
                    value: "{hkt_session}"
                }};

                // Set FE-XSRF-TOKEN
                data['FE-XSRF-TOKEN'] = {{
                    expireTime: {expire_time},
                    value: "{xsrf_token}"
                }};

                localStorage.setItem('__STORAGE__', JSON.stringify(data));

                // Verify
                var verify = JSON.parse(localStorage.getItem('__STORAGE__'));
                return JSON.stringify({{
                    success: true,
                    hasSession: !!verify['X-MZ-SESSION'],
                    hasXsrf: !!verify['FE-XSRF-TOKEN'],
                    sessionValue: verify['X-MZ-SESSION']?.value?.substring(0, 10) + '...',
                    xsrfValue: verify['FE-XSRF-TOKEN']?.value?.substring(0, 10) + '...'
                }});
            }} catch (e) {{
                return JSON.stringify({{ success: false, error: e.message }});
            }}
        }})();
    ''')

    print(f"[TEST] Raw result: {result_str}")

    try:
        result = json.loads(result_str) if isinstance(result_str, str) else result_str
    except:
        result = {"success": False, "error": "parse error"}

    print(f"[TEST] Set tokens result: {result}")

    if result and result.get('success'):
        print("[TEST] Tokens set successfully!")
        print("[TEST] Reloading page to apply session...")

        # Reload to apply session
        await tab.reload()
        await asyncio.sleep(3)

        # Check login status
        login_status_str = await tab.evaluate('''
            (function() {
                var accountInfo = localStorage.getItem('ACCOUNT_INFO');
                if (accountInfo) {
                    try {
                        var info = JSON.parse(accountInfo);
                        return JSON.stringify({
                            loggedIn: info.userName && info.userName.length > 0,
                            userName: info.userName || '',
                            phone: info.phone || ''
                        });
                    } catch (e) {}
                }

                // Check if login link is visible
                var loginLink = document.querySelector('a[href*="/login"]');
                if (loginLink) {
                    var text = loginLink.innerText || '';
                    if (text.includes('登入')) {
                        return JSON.stringify({ loggedIn: false, reason: 'login link visible' });
                    }
                }

                return JSON.stringify({ loggedIn: false, reason: 'unknown' });
            })();
        ''')

        try:
            login_status = json.loads(login_status_str) if isinstance(login_status_str, str) else login_status_str
        except:
            login_status = {"loggedIn": False, "error": "parse error"}

        print(f"[TEST] Login status: {login_status}")

        if login_status and login_status.get('loggedIn'):
            print(f"[TEST] SUCCESS! Logged in as: {login_status.get('userName')}")
        else:
            print("[TEST] Not logged in. Tokens may be invalid or expired.")
    else:
        print(f"[TEST] Failed to set tokens: {result}")

    print("\n[TEST] Browser will stay open for manual inspection.")
    print("[TEST] Press Ctrl+C to close...")

    # Keep browser open for inspection
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[TEST] Closing browser...")


if __name__ == "__main__":
    asyncio.run(test_hkt_session())
