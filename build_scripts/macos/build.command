#!/bin/sh
# Double-click this in Finder to build Tickets Hunter for macOS.
#
# PyInstaller cannot cross-compile, so a macOS build has to run on macOS. This
# wraps the whole sequence -- interpreter check, virtualenv, dependencies,
# build, Gatekeeper -- because the alternative is remembering five commands on
# a machine that is not the one the code is usually edited on.
#
# Safe to re-run: the virtualenv is reused and dependencies are only reinstalled
# when requirement.txt is newer than the last successful install.

set -e

cd "$(dirname "$0")/../.." || exit 1
ROOT="$(pwd)"
VENV="$ROOT/.venv"
STAMP="$VENV/.deps-installed"

echo "Tickets Hunter -- macOS build"
echo "Project: $ROOT"
echo

# ddddocr declares Requires-Python <3.13, and 3.12 is untested here. Prefer
# 3.11, then 3.10, rather than whatever python3 points at.
PY=""
for candidate in python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "ERROR: need Python 3.10 or 3.11 (3.11.9 recommended)."
    echo
    echo "  brew install python@3.11"
    echo
    echo "Found on PATH:"
    command -v python3 >/dev/null 2>&1 && python3 --version || echo "  no python3"
    echo
    echo "3.12 is untested and 3.13+ does not work: ddddocr declares"
    echo "Requires-Python <3.13."
    read -r _ 2>/dev/null || true
    exit 1
fi
echo "Interpreter: $PY ($($PY --version 2>&1))"

if [ ! -d "$VENV" ]; then
    echo "Creating virtualenv..."
    "$PY" -m venv "$VENV"
fi
# shellcheck disable=SC1091
. "$VENV/bin/activate"

# requirement.txt newer than the stamp means the pins moved since the last run.
if [ ! -f "$STAMP" ] || [ "$ROOT/requirement.txt" -nt "$STAMP" ]; then
    echo "Installing dependencies (this takes a few minutes the first time)..."
    python -m pip install --upgrade pip --quiet
    python -m pip install -r "$ROOT/requirement.txt"
    # Same pin as the release workflow, so a local build matches what CI ships.
    python -m pip install pyinstaller==6.22.3
    touch "$STAMP"
else
    echo "Dependencies already installed; skipping (delete $STAMP to force)."
fi
echo

# OCR has been confirmed working on Apple Silicon, but a successful pip install
# proves nothing on its own, so check it on this machine. Report it, but do not
# stop the build over it: a packaged bot with broken OCR is still worth having
# for manual captcha entry.
echo "Checking the OCR stack on this architecture..."
if python "$ROOT/build_scripts/macos/ocr_smoke_test.py"; then
    OCR_STATUS="working"
else
    OCR_STATUS="FAILED -- captcha recognition will not work on this machine"
fi
echo

# "|| BUILD_RESULT=$?" rather than a bare call: under set -e a failing build
# would exit here, and the failure message and the pause below never ran.
BUILD_RESULT=0
python "$ROOT/build_scripts/build_local.py" || BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    # The quarantine flag is cleared by build_local.py, which reports what it
    # did. Doing it in both places printed the manual workaround immediately
    # before performing it automatically.
    echo
    echo "============================================================"
    echo "Build finished."
    echo "OCR stack: $OCR_STATUS"
    echo
    echo "  open $ROOT/dist/tickets_hunter"
    echo
    echo "Start with start-settings.command to configure, then"
    echo "start-bot.command to run."
else
    echo
    echo "============================================================"
    echo "Build FAILED. See build/*/warn-*.txt for the module PyInstaller"
    echo "could not resolve, then re-run this file."
fi

echo
echo "Press Return to close."
read -r _ 2>/dev/null || true
exit $BUILD_RESULT
