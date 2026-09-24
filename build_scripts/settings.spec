# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# PyInstaller Spec File for Tickets Hunter - Settings Editor (Tornado Web)
# =============================================================================
# This spec file builds the Tornado web-based settings editor.
# Output: dist/settings/settings.exe
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
    [os.path.join(project_root, 'src', 'settings.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'src', 'www'), 'www'),
        (os.path.join(project_root, 'src', 'assets'), 'assets'),
        # settings.json excluded - program generates it automatically
    ] + ddddocr_datas,
    hiddenimports=[
        # Tornado web framework
        'tornado',
        'tornado.web',
        'tornado.ioloop',
        'tornado.httpserver',
        'tornado.websocket',
        # Shared utilities (important!)
        'util',
        'NonBrowser',
        # Optional: ddddocr (if settings.py uses it)
        'ddddocr',
        'onnxruntime',
        # Image processing (if needed)
        'PIL',
        'PIL.Image',
        'numpy',
        # Others
        'json',
        'base64',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # tools/captcha_trainer/ installs torch into the same venv, and the
        # ddddocr hiddenimport above reaches it: a local build measured
        # 3984MB for this spec against 307MB for nodriver_tixcraft.spec,
        # which already carried these entries. CI installs only
        # requirement.txt and so never saw it.
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
    name='settings',  # Output: settings.exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for stability
    console=True,  # Show console window for Tornado logs
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
    name='settings',
)
