# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# PyInstaller Spec File for Tickets Hunter - Chrome Version
# =============================================================================
# This spec file builds the Chrome/Selenium version of Tickets Hunter.
# Output: dist/chrome_tixcraft/chrome_tixcraft.exe
# =============================================================================

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the project root directory (parent of build_scripts)
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect ddddocr data files (including .onnx models)
ddddocr_datas = collect_data_files('ddddocr')

a = Analysis(
    [os.path.join(project_root, 'src', 'chrome_tixcraft.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'src', 'webdriver'), 'webdriver'),
        (os.path.join(project_root, 'src', 'assets'), 'assets'),
        (os.path.join(project_root, 'src', 'www'), 'www'),
        # settings.json excluded - program generates it automatically
    ] + ddddocr_datas,
    hiddenimports=[
        # Core dependencies
        'ddddocr',
        'onnxruntime',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common.by',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'undetected_chromedriver',
        # Shared utilities (important!)
        'util',
        'NonBrowser',
        # Image processing
        'PIL',
        'PIL.Image',
        'cv2',
        'numpy',
        # Network
        'urllib3',
        'certifi',
        'cryptography',
        # Others
        'playsound',
        'pyperclip',
        'tornado',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # This enables folder mode
    name='chrome_tixcraft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for stability
    console=True,  # Show console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'src', 'www', 'favicon.ico'),  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='chrome_tixcraft',
)
