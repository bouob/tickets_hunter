"""
NoDriver with MCP Integration Test Script
Starts Chrome with fixed debug port 9222, then connects NoDriver

Usage:
1. Run this script: python test_nodriver_mcp.py
2. MCP chrome-devtools (with --browserUrl http://127.0.0.1:9222) can connect
3. Use MCP tools (take_snapshot, click, etc.) to control the browser

Note: .mcp.json should have:
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"]
    }
  }
}
"""
import asyncio
import subprocess
import os
import nodriver as uc
from nodriver import Config
from nodriver.core._contradict import ContraDict
from nodriver.cdp import target


# Find Chrome executable
def find_chrome():
    """Find Chrome executable path on Windows"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


async def start_nodriver_with_mcp():
    print("[MCP] Starting Chrome with debug port 9222...")

    chrome_path = find_chrome()
    if not chrome_path:
        print("[ERROR] Chrome not found!")
        return

    print(f"[MCP] Chrome path: {chrome_path}")

    # Start Chrome with remote debugging enabled
    chrome_args = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--remote-debugging-host=127.0.0.1",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--no-sandbox",
        "--user-data-dir=" + os.path.join(os.environ.get("TEMP", "/tmp"), "chrome_mcp_profile"),
        "about:blank"
    ]

    print("[MCP] Launching Chrome subprocess...")
    chrome_process = subprocess.Popen(
        chrome_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for Chrome to start
    await asyncio.sleep(2)

    print("[MCP] Chrome launched! PID:", chrome_process.pid)
    print("[MCP] MCP chrome-devtools can connect to http://127.0.0.1:9222")

    # Now connect NoDriver to the existing Chrome
    print("[MCP] Connecting NoDriver to Chrome...")
    conf = Config(
        browser_args=[],
        lang="zh-TW",
        sandbox=False,
        headless=False,
        host="127.0.0.1",
        port=9222
    )

    try:
        driver = await uc.start(conf)
        print("[MCP] NoDriver connected!")

        # Navigate to HKTicketing for testing
        test_url = "https://hkt.hkticketing.com/hant/#/home"
        print(f"[MCP] Navigating to {test_url}")
        tab = await driver.get(test_url)
        await asyncio.sleep(2)

        print("[MCP] Browser is ready!")
        print("[MCP] You can now use MCP chrome-devtools tools:")
        print("      - take_snapshot: Get DOM structure")
        print("      - take_screenshot: Capture page image")
        print("      - click: Click on elements")
        print("      - evaluate_script: Run JavaScript")
        print("      - list_network_requests: Monitor API calls")
        print("")
        print("[MCP] Press Ctrl+C to close browser...")

        # Keep browser open
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"[ERROR] Failed to connect NoDriver: {e}")
        chrome_process.terminate()
        raise
    except KeyboardInterrupt:
        print("\n[MCP] Closing browser...")
        chrome_process.terminate()


if __name__ == "__main__":
    asyncio.run(start_nodriver_with_mcp())
