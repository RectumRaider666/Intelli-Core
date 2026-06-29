#!/bin/bash

## <!-- [Variables] -----> ##
dir="$(pwd)"
sdir="/sdcard/Download"

## <!-- [Device Control] -----> ##
tap () {
    adb shell input tap "$1" "$2"
}

hold () {
    local x="$1"
    local y="$2"
    local d="${3:-550}"

    adb shell input swipe "$x" "$y" "$x" "$y" "$d"
}

swiper () {
    local direct="$1"
    local loop="${2:-1}"
    local r="${3:-100}"
    local d="${4:-500}"

    swipe () {
        local x1="$1"
        local y1="$2"
        local x2="$3"
        local y2="$4"
        local d="$5"

        adb shell input swipe "$x1" "$y1" "$x2" "$y2" "$d"
    }

    if [ "$direct" = "u" ]; then
        local end="$((1200 - r))"
        for ((i=0; i<loop; i++)); do
            swipe 540 1200 540 "$end" "$d"
        done
    elif [ "$direct" = "d" ]; then
        local end="$((1200 + r))"
        for ((i=0; i<loop; i++)); do
            swipe 540 1200 540 "$end" "$d"
        done
    elif [ "$direct" = "l" ]; then
        local end="$((540 - r))"
        for ((i=0; i<loop; i++)); do
            swipe 540 1200 "$end" 1200 "$d"
        done
    elif [ "$direct" = "r" ]; then
        local end="$((540 + r))"
        for ((i=0; i<loop; i++)); do
            swipe 540 1200 "$end" 1200 "$d"
        done
    fi
}

## <!-- [Automations] -----> ##
find () {
    local target="$1"
    local screen="$sdir/screen.png"
    local thresh="${2:-0.85}"
    local match_out

    tmp="$(mktemp -d)"

    adb shell screencap -p "$screen" || {
        echo "[ERROR] Could not take screenshot" >&2
        rm -rf "$tmp"
        return 1
    }

    adb pull "$screen" "$tmp/screen.png" >/dev/null || {
        echo "[ERROR] Could not pull screenshot into $tmp" >&2
        rm -rf "$tmp"
        return 1
    }

    match_out="$(python3 - "$tmp/screen.png" "$target" "$thresh" <<'PY'
import sys

try:
    import cv2
except ImportError:
    print("[ERROR] cv2 is not installed! install with pip install opencv-python")
    sys.exit(2)

screen_path, target_path, threshold_raw = sys.argv[1], sys.argv[2], sys.argv[3]
threshold = float(threshold_raw)
screen = cv2.imread(screen_path, cv2.IMREAD_COLOR)
target = cv2.imread(target_path, cv2.IMREAD_COLOR)

if screen is None:
    print("[ERROR] Bad screen image")
    sys.exit(2)
if target is None:
    print("[ERROR] Bad target image")
    sys.exit(2)

result = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

h, w = target.shape[:2]
cen_x = max_loc[0] + (w // 2)
cen_y = max_loc[1] + (h // 2)

if max_val >= threshold:
    print(f"[FOUND] {cen_x} {cen_y} {max_val:.4f}")
else:
    print(f"[FAIL] Image not found, best match val={max_val:.4f}")
PY
)"

    status=$?
    rm -rf "$tmp"

    if [ "$status" -ne 0 ]; then
        echo "$match_out" >&2
        return "$status"
    fi

    read -r FIND_STATE FIND_X FIND_Y FIND_SCORE <<<"$match_out"

    if [ "$FIND_STATE" = "[FOUND]" ]; then
        echo "[FOUND] x=$FIND_X y=$FIND_Y match=$FIND_SCORE"
        return 0
    fi

    echo "[FAIL] Image not found, best x=$FIND_X y=$FIND_Y val=$FIND_SCORE, STATE=$FIND_STATE"
    return 1
}

## <!-- [Game Controls] -----> ##
heal () {
    hold 750 2250
}

top_view () {
    swiper d 2 1000 10
}

search () {
    mob="Grey_Wolfman"
    find "$dir/img/mob/icons/$mob.png"
    if [ "$FIND_STATE" = "[FOUND]" ]; then
        tap "$FIND_X" "$FIND_Y"
        sleep 0.2
        find "$dir/img/mob/names/$mob.png"
        if [ "$FIND_STATE" = "[FOUND]" ]; then
            tap 540 1390
        fi
    fi
}

## <!-- [Runnit] -----> ##
start () {
    top_view
    heal
    search
}

start
