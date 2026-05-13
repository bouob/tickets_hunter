#!/usr/bin/env sh
set -eu

DATA_DIR="${TICKETS_HUNTER_DATA_DIR:-/data}"
APP_SRC="/app/src"

mkdir -p "$DATA_DIR" "$DATA_DIR/webdriver"

if [ ! -f "$DATA_DIR/settings.json" ]; then
    python - <<'PY'
import os
import settings
import util

target = os.path.join(os.environ.get("TICKETS_HUNTER_DATA_DIR", "/data"), "settings.json")
util.save_json(settings.get_default_config(), target)
print(f"created default settings: {target}")
PY
fi

rm -f "$APP_SRC/settings.json"
ln -s "$DATA_DIR/settings.json" "$APP_SRC/settings.json"

rm -rf "$APP_SRC/webdriver"
ln -s "$DATA_DIR/webdriver" "$APP_SRC/webdriver"

if [ -d "$DATA_DIR/webdriver" ]; then
    find "$DATA_DIR/webdriver" -type f \( -name "chrome" -o -name "chrome-wrapper" -o -name "chrome_crashpad_handler" -o -name "chrome_sandbox" \) -exec chmod +x {} \;
fi

if [ "${TICKETS_HUNTER_XVFB:-1}" = "1" ]; then
    export DISPLAY="${DISPLAY:-:99}"
    display_number="${DISPLAY#:}"
    lock_file="/tmp/.X${display_number}-lock"

    if [ -f "$lock_file" ] && ! pgrep -f "Xvfb ${DISPLAY}" >/dev/null 2>&1; then
        rm -f "$lock_file"
    fi

    if ! pgrep -f "Xvfb ${DISPLAY}" >/dev/null 2>&1; then
        Xvfb "$DISPLAY" -screen 0 "${TICKETS_HUNTER_XVFB_SCREEN:-1280x1024x24}" -nolisten tcp &
        xvfb_pid="$!"
    else
        xvfb_pid=""
    fi

    "$@"
    status="$?"

    if [ -n "$xvfb_pid" ]; then
        kill "$xvfb_pid" >/dev/null 2>&1 || true
        wait "$xvfb_pid" >/dev/null 2>&1 || true
    fi
    rm -f "$lock_file"

    exit "$status"
fi

exec "$@"
