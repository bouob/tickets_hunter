# coding: utf-8
"""
Chrome for Testing Downloader

Downloads portable Chrome browser from Chrome for Testing API
for use with NoDriver when Chrome is not installed on the system.

API Documentation: https://googlechromelabs.github.io/chrome-for-testing/
"""

import json
import logging
import os
import platform
import sys
import zipfile
from io import BytesIO
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)

# Chrome for Testing API endpoint
CHROME_FOR_TESTING_API = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

# Default download directory (relative to app root)
DEFAULT_CHROME_DIR = "webdriver"


def get_platform_identifier() -> str:
    """
    Get the platform identifier for Chrome for Testing downloads.

    Returns:
        Platform string: 'win64', 'win32', 'linux64', 'mac-x64', 'mac-arm64'
    """
    if sys.platform.startswith("win"):
        # Check if 64-bit Windows
        if platform.machine().endswith('64'):
            return "win64"
        return "win32"
    elif sys.platform == "darwin":
        # macOS - check for ARM (M1/M2) or Intel
        if platform.machine() == "arm64":
            return "mac-arm64"
        return "mac-x64"
    elif sys.platform.startswith("linux"):
        return "linux64"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def get_chrome_download_info(no_ssl: bool = False) -> Optional[Tuple[str, str]]:
    """
    Get Chrome download URL and version from Chrome for Testing API.

    Args:
        no_ssl: If True, use HTTP instead of HTTPS

    Returns:
        Tuple of (download_url, version) or None if failed
    """
    api_url = CHROME_FOR_TESTING_API
    if no_ssl:
        api_url = api_url.replace("https://", "http://")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        stable = data.get("channels", {}).get("Stable", {})
        version = stable.get("version")
        downloads = stable.get("downloads", {}).get("chrome", [])

        if not downloads:
            logger.error("No Chrome downloads found in API response")
            return None

        platform_id = get_platform_identifier()
        for item in downloads:
            if item.get("platform") == platform_id:
                return (item.get("url"), version)

        logger.error(f"No Chrome download found for platform: {platform_id}")
        return None

    except requests.RequestException as e:
        logger.error(f"Failed to fetch Chrome for Testing API: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse Chrome for Testing API response: {e}")
        return None


def get_chrome_executable_name() -> str:
    """Get the Chrome executable filename for current platform."""
    if sys.platform.startswith("win"):
        return "chrome.exe"
    elif sys.platform == "darwin":
        return "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    else:
        return "chrome"


def get_downloaded_chrome_path(base_dir: str) -> Optional[str]:
    """
    Get the path to downloaded Chrome executable if it exists.

    Args:
        base_dir: Base directory where Chrome was downloaded

    Returns:
        Full path to Chrome executable or None if not found
    """
    platform_id = get_platform_identifier()

    # Chrome for Testing extracts to chrome-<platform>/ directory
    chrome_dir = os.path.join(base_dir, f"chrome-{platform_id}")
    chrome_exe = os.path.join(chrome_dir, get_chrome_executable_name())

    if os.path.exists(chrome_exe):
        return chrome_exe

    return None


def download_chrome(download_dir: Optional[str] = None, no_ssl: bool = False) -> Optional[str]:
    """
    Download Chrome for Testing to specified directory.

    Args:
        download_dir: Directory to download Chrome to. If None, uses default.
        no_ssl: If True, use HTTP instead of HTTPS for download

    Returns:
        Path to Chrome executable or None if download failed
    """
    if download_dir is None:
        # Use default directory relative to this script
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_CHROME_DIR)

    # Check if already downloaded
    existing_path = get_downloaded_chrome_path(download_dir)
    if existing_path:
        logger.info(f"Chrome already exists at: {existing_path}")
        return existing_path

    # Get download URL
    download_info = get_chrome_download_info(no_ssl)
    if not download_info:
        return None

    url, version = download_info
    platform_id = get_platform_identifier()

    print(f"[Chrome Downloader] Downloading Chrome {version} for {platform_id}...")
    print(f"[Chrome Downloader] URL: {url}")

    # Create download directory
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Download with retry
    max_retries = 3
    response = None

    for attempt in range(max_retries):
        try:
            download_url = url
            if attempt > 0 and no_ssl:
                download_url = url.replace("https://", "http://")

            response = requests.get(download_url, timeout=300, stream=True)
            response.raise_for_status()

            # Show download progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunks = []
            last_percent = -1

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        # Only update display when percentage changes
                        if percent != last_percent:
                            last_percent = percent
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            print(f"\r[Chrome Downloader] Progress: {mb_downloaded:.1f}/{mb_total:.1f} MB ({percent}%)", end="", flush=True)

            print()  # New line after progress
            content = b''.join(chunks)
            break

        except requests.RequestException as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All download attempts failed")
                return None

    # Extract zip file
    print(f"[Chrome Downloader] Extracting to {download_dir}...")
    try:
        archive = BytesIO(content)
        with zipfile.ZipFile(archive, 'r') as zip_file:
            zip_file.extractall(download_dir)
    except zipfile.BadZipFile as e:
        logger.error(f"Failed to extract Chrome archive: {e}")
        return None

    # Verify extraction
    chrome_path = get_downloaded_chrome_path(download_dir)
    if chrome_path:
        # Make executable on Unix systems
        if not sys.platform.startswith("win"):
            os.chmod(chrome_path, 0o755)
        print(f"[Chrome Downloader] Chrome installed successfully: {chrome_path}")
        return chrome_path

    logger.error("Chrome extraction succeeded but executable not found")
    return None


def find_system_chrome() -> Optional[str]:
    """
    Find Chrome installed on the system (same logic as NoDriver).

    Returns:
        Path to Chrome executable or None if not found
    """
    candidates = []

    if sys.platform.startswith(("darwin", "cygwin", "linux", "linux2")):
        # POSIX systems
        for item in os.environ.get("PATH", "").split(os.pathsep):
            for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "google-chrome-stable"):
                candidates.append(os.path.join(item, name))

        if sys.platform == "darwin":
            candidates.extend([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ])
    else:
        # Windows
        for env_var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "PROGRAMW6432"):
            base = os.environ.get(env_var)
            if base:
                for subdir in ("Google/Chrome/Application", "Google/Chrome Beta/Application", "Google/Chrome Canary/Application"):
                    candidates.append(os.path.join(base, subdir, "chrome.exe"))

    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


def ensure_chrome_available(download_dir: Optional[str] = None, no_ssl: bool = False) -> Optional[str]:
    """
    Ensure Chrome is available - find system Chrome or download if needed.

    This is the main entry point for NoDriver integration.

    Args:
        download_dir: Directory to download Chrome to if needed
        no_ssl: If True, use HTTP instead of HTTPS

    Returns:
        Path to Chrome executable or None if unavailable
    """
    # First, check if Chrome is installed on the system
    system_chrome = find_system_chrome()
    if system_chrome:
        logger.debug(f"Found system Chrome: {system_chrome}")
        return system_chrome

    # Check if we already downloaded Chrome
    if download_dir is None:
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_CHROME_DIR)

    downloaded_chrome = get_downloaded_chrome_path(download_dir)
    if downloaded_chrome:
        logger.debug(f"Found downloaded Chrome: {downloaded_chrome}")
        return downloaded_chrome

    # Download Chrome
    print("[Chrome Downloader] Chrome not found on system, downloading Chrome for Testing...")
    return download_chrome(download_dir, no_ssl)


if __name__ == "__main__":
    # Test the downloader
    logging.basicConfig(level=logging.DEBUG)
    chrome_path = ensure_chrome_available()
    if chrome_path:
        print(f"Chrome available at: {chrome_path}")
    else:
        print("Failed to ensure Chrome availability")
