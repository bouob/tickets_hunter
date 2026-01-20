"""
FunOne Tickets Cookie Login Test
測試只用 ticket_session 是否能登入
"""
import nodriver as uc
import nodriver.cdp as cdp
import asyncio

# 用戶提供的 ticket_session 值
TICKET_SESSION = "eyJpdiI6IkxJY0h1K0hFZ3pRK0gzUTAyd25hWlE9PSIsInZhbHVlIjoiTEV5bVppQkt0VUt5cW1iVkJJbUs5RU1Iei9Ddlh1UHlmVDNuUXR4anBUdWJOMS9CbTBLS2s0QWwvLys3TGFkWWhZUkFzdWFYUlAyaHpiZHVzNVRHSG5oYkZqd1VFd2wzekFKcGwxTjF3NkJLemNYaDIvRU5lRUhCMEhhNUdnTnIiLCJtYWMiOiI4YTMxMDczZTcyNzc2N2EyNjBhMGY0MjZkY2Y4YmI5ZGRhMTNhN2I3ODEyNmZiNmU1YTZhMDc3NjczODliZTBmIiwidGFnIjoiIn0%3D"

TARGET_URL = "https://tickets.funone.io/"


async def test_cookie_login():
    print("[INFO] Starting NoDriver browser...")

    # 啟動瀏覽器
    browser = await uc.start()

    # 開啟目標頁面（先訪問一次以建立 domain）
    print("[INFO] Opening target page...")
    page = await browser.get(TARGET_URL)
    await asyncio.sleep(2)

    # 檢查初始狀態
    print("[INFO] Checking initial login status...")
    html = await page.get_content()
    if "登入/註冊" in html:
        print("[INFO] Initial status: NOT logged in")
    else:
        print("[INFO] Initial status: Already logged in (or unknown)")

    # 清除所有 cookies
    print("[INFO] Clearing all cookies...")
    await browser.cookies.clear()

    # 重新整理確認已登出
    await page.reload()
    await asyncio.sleep(2)

    html = await page.get_content()
    if "登入/註冊" in html:
        print("[INFO] After clearing cookies: NOT logged in (as expected)")
    else:
        print("[WARNING] After clearing cookies: Still shows logged in?")

    # 只注入 ticket_session cookie (使用 CDP)
    print("[INFO] Injecting ticket_session cookie ONLY using CDP...")
    try:
        cookie_result = await page.send(cdp.network.set_cookie(
            name="ticket_session",
            value=TICKET_SESSION,
            domain="tickets.funone.io",
            path="/",
            secure=False,
            http_only=True
        ))
        print(f"[INFO] CDP setCookie result: {cookie_result}")
    except Exception as e:
        print(f"[ERROR] Failed to set cookie via CDP: {e}")
        return

    # 列出當前 cookies 確認
    print("[INFO] Current cookies after injection:")
    cookies = await browser.cookies.get_all()
    for cookie in cookies:
        val = cookie.value if len(cookie.value) < 50 else cookie.value[:50] + "..."
        print(f"  - {cookie.name}: {val}")

    # 重新整理頁面測試登入
    print("[INFO] Reloading page to test login...")
    await page.reload()
    await asyncio.sleep(3)

    # 檢查登入狀態
    print("[INFO] Checking login status after cookie injection...")
    html = await page.get_content()

    if "登入/註冊" in html:
        print("[RESULT] FAILED - Still showing 'login/register', cookie login did NOT work")
        print("[INFO] This means ticket_session alone is NOT enough, or the session has expired")
    elif "+886" in html or "會員" in html or "我的訂單" in html:
        print("[RESULT] SUCCESS - Logged in! Cookie login works with ticket_session only!")
    else:
        print("[RESULT] UNKNOWN - Please check the browser manually")

    # 保持瀏覽器開啟供檢視
    print("[INFO] Browser will stay open for manual inspection. Press Ctrl+C to close.")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Closing browser...")


if __name__ == "__main__":
    asyncio.run(test_cookie_login())
