# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# PyInstaller Spec File for Tickets Hunter - NoDriver Version
# =============================================================================
# This spec file builds the NoDriver version of Tickets Hunter.
# Output: dist/nodriver_tixcraft/nodriver_tixcraft.exe
# =============================================================================

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the project root directory (parent of build_scripts)
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect ddddocr data files (including .onnx models)
ddddocr_datas = collect_data_files('ddddocr')

a = Analysis(
    [os.path.join(project_root, 'src', 'nodriver_tixcraft.py')],
    pathex=[os.path.join(project_root, 'src')],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'src', 'assets'), 'assets'),
        (os.path.join(project_root, 'src', 'www'), 'www'),
        # settings.json excluded - program generates it automatically
        # chrome-win64/ excluded - auto-downloaded at runtime if needed
    ] + ddddocr_datas,
    hiddenimports=[
        # Core dependencies
        'ddddocr',
        'onnxruntime',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'zendriver',
        'zendriver.cdp',
        'zendriver.core',
        # Shared utilities (important!)
        'util',
        'NonBrowser',
        'chrome_downloader',
        # Modular architecture
        'nodriver_common',
        'platforms',
        'platforms.facebook',
        'platforms.fansigo',
        'platforms.cityline',
        'platforms.famiticket',
        'platforms.ticketplus',
        'platforms.funone',
        'platforms.kktix',
        'platforms.tixcraft',
        'platforms.ibon',
        'platforms.kham',
        'platforms.hkticketing',
        # Chrome downloader dependencies
        'requests',
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
    excludes=[
        # tools/captcha_trainer/ installs torch into the same venv. Nothing in
        # src/ imports it, so PyInstaller should not pick it up -- these entries
        # are a guard against a stray transitive import silently adding ~2GB.
        'torch',
        'torchvision',
        # The project migrated to zendriver; the old nodriver package may still
        # be present in a long-lived venv. Keep it out of the build.
        'nodriver',
        # Notebook/plotting stacks that OCR training tools tend to drag in.
        'matplotlib',
        'IPython',
        'tkinter',
    ],
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
    name='nodriver_tixcraft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for stability
    console=True,  # Show console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-only: macOS PyInstaller expects .icns and fails on a .ico.
    icon=(os.path.join(project_root, 'src', 'www', 'favicon.ico')
          if sys.platform == 'win32' else None),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='nodriver_tixcraft',
)
