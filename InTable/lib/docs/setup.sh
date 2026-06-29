#!/usr/bin/env bash
# setup_table.sh

set -euo pipefail

log()  { printf '\n==> %s\n' "$*"; }
warn() { printf '\n!! %s\n' "$*" >&2; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || { warn "Missing command: $1"; exit 1; }; }

need_cmd adb
need_cmd curl
need_cmd grep
need_cmd sed
need_cmd basename
need_cmd head
need_cmd file

log "Waiting for ADB device..."
adb wait-for-device

pkglist=(
  'com.theorytank.a1up_launcher'
  'com.theorytank.a1up_screensaver'
  'com.cghs.stresstest'
  'com.zediel.pcbtest'
  'com.DeviceTest'
  'com.android.traceur'
  'com.android.printspooler'
  'com.android.printservice.recommendation'
)

log "Uninstalling selected packages for user 0 (ignore failures if not present)..."
for pkg in "${pkglist[@]}"; do
  log "Uninstall user0: $pkg"
  adb shell pm uninstall --user 0 "$pkg" >/dev/null 2>&1 || warn "Could not uninstall (maybe not installed): $pkg"
done

log "Disabling com.android.settings.intelligence (ignore failure if missing)..."
adb shell pm disable-user --user 0 com.android.settings.intelligence >/dev/null 2>&1 \
  || warn "Could not disable com.android.settings.intelligence (maybe not present)"

log "Discovering update-related packages (update|ota|updater)..."
mapfile -t up_pkgs < <(adb shell pm list packages | grep -Ei 'update|ota|updater' | sed 's/^package://')

if ((${#up_pkgs[@]} == 0)); then
  warn "No updater/OTA packages matched via grep."
else
  log "Disabling updater/OTA packages for user 0..."
  for pkg in "${up_pkgs[@]}"; do
    log "Disable user0: $pkg"
    adb shell pm disable-user --user 0 "$pkg" >/dev/null 2>&1 || warn "Could not disable: $pkg"
  done

  log "Attempting pm uninstall --user 0 for updater/OTA packages (safe; may fail for system pkgs)..."
  for pkg in "${up_pkgs[@]}"; do
    log "Uninstall user0: $pkg"
    adb shell pm uninstall --user 0 "$pkg" >/dev/null 2>&1 \
      || warn "Could not uninstall (expected for some system pkgs): $pkg"
  done
fi

log "Applying update / background / verifier settings (some keys may be OEM-dependent)..."
adb shell settings put global auto_update_system 0 || true
adb shell settings put global ota_disable 1 || true
adb shell settings put global system_update_policy 0 || true
adb shell settings put global auto_update_apps 0 || true
adb shell settings put global auto_install_apps 0 || true
adb shell settings put global play_auto_update 0 || true
adb shell settings put global restrict_background_data 1 || true
adb shell cmd netpolicy set restrict-background true || true
adb shell settings put global adaptive_battery_management_enabled 0 || true
adb shell settings put global app_standby_enabled 0 || true
adb shell settings put global automatic_system_update 0 || true
adb shell settings put global verifier_verify_adb_installs 0 || true
adb shell settings put global package_verifier_enable 0 || true
adb shell settings put global gms_phenotype_auto_update_enabled 0 || true
adb shell settings put global gms_phenotype_auto_update_frequency 0 || true
adb shell settings put secure system_update_available 0 || true
adb shell settings put secure update_available 0 || true
adb shell settings put global reboot_update_enabled 0 || true
adb shell settings put global install_non_market_apps 0 || true

log "Current update-related GLOBAL settings:"
adb shell settings list global | grep -Ei 'update|ota|phenotype|restrict_background|verifier|standby|battery' || true

log "Current update-related SECURE settings:"
adb shell settings list secure | grep -Ei 'update|ota' || true

log "JobScheduler hits (filtered: update|ota|updater|rockchip):"
adb shell dumpsys jobscheduler | grep -Ei 'update|ota|updater|rockchip' || true

apks=(
  'https://github.com/termux/termux-app/releases/download/v0.118.3/termux-app_v0.118.3+github-debug_armeabi-v7a.apk'
  'https://auroraoss.com/downloads/AuroraStore/Release/AuroraStore-4.7.5.apk'
  'https://f-droid.org/F-Droid.apk'
  'https://github.com/termux/termux-api/releases/download/v0.53.0/termux-api-app_v0.53.0+github.debug.apk'
  'https://nova-launcher.en.softonic.com/android/support?dt=internalDownload'
)

log "Downloading APKs to /tmp/apkdl and installing with adb install -r..."
mkdir -p /tmp/apkdl

for url in "${apks[@]}"; do
  fn="$(basename "${url%%\?*}")"
  out="/tmp/apkdl/$fn"

  log "Downloading: $url"
  curl -L --fail --retry 3 --retry-delay 1 -o "$out" "$url"

  # APKs are ZIPs: magic bytes should start with PK
  if head -c 2 "$out" | grep -q '^PK'; then
    log "Installing: $out"
    adb install -r "$out" || warn "adb install failed: $out"
  else
    warn "Not an APK (or got HTML/redirect). Skipping: $url"
    file "$out" || true
  fi
done

log "Done."



#!/data/data/com.termux/files/usr/bin/bash

VERSION="0.1.6"
PAKS=( "com.xfinity.keyboard" )
AOSP="com.android.inputmethod.latin/.LatinIME"
LOG="$HOME/.termux/boot/bootlog.log"

# --- Helper functions --------------------------------------------------------
ts() {
    date "+%Y-%m-%d %H:%M:%S"
}
error() {
    local msg="$1"
    termux-toast "[ERROR]: $msg"
    echo "$(ts) [ERROR]: $msg"
}
warn() {
    local msg="$1"
    termux-toast "[WARN]: $msg"
    echo "$(ts) [WARN]: $msg"
    sleep 2
}
info() {
    local msg="$1"
    termux-toast "[INFO]: $msg"
    echo "$(ts) [INFO]: $msg"
    sleep 2
}
run() {
    local desc="$1"
    shift
    local cmd="$*"
    local out
     if ! out=$(bash -c "$cmd" 2>&1); then
        error "$desc failed: $out"
        return 1
    else info "$desc succeeded"
        echo "$(ts) [RUN ] $cmd"
        echo "$(ts) [OUT ] $out"
        return 0
    fi
}







#!/data/data/com.termux/files/usr/bin/bash

VERSION="0.2.5"
PAKS=(
    'com.theorytank.a1up_launcher'
    'com.theorytank.a1up_screensaver'
    'com.cghs.stresstest'
    'com.zediel.pcbtest'
    'com.DeviceTest'
    'com.android.traceur'
    'com.android.printspooler'
    'com.android.printservice.recommendation'
)
AOSP="com.android.inputmethod.latin/.LatinIME"
LOG="$HOME/.termux/logs/boot.log"
DOCC="$HOME/storage/shared/Documents"

# --- Helper functions --------------------------------------------------------
ts() {
    date "+%Y-%m-%d %H:%M:%S"
}

error() {
    local msg="$1"
    #termux-toast "[ERROR]: $msg"
    echo "$(ts) [ERROR]: $msg"
    #sleep 5
}

warn() {
    local msg="$1"
    #termux-toast "[WARN]: $msg"
    echo "$(ts) [WARN]: $msg"
    #sleep 2
}

info() {
    local msg="$1"
    #termux-toast "[INFO]: $msg"
    echo "$(ts) [INFO]: $msg"
    #sleep 2
}

run() {
    local desc="$1"
    shift
    local cmd="$*"
    local out
    if ! out=$(bash -c "$cmd" 2>&1); then
        error "$desc failed: $out"
        return 1
    else info "$desc succeeded"
        echo "$(ts) [RUN] $cmd"
        echo "$(ts) [OUT] $out"
        return 0
    fi
}

# --- Main pipeline -----------------------------------------------------------
{
    run "Fixit v$VERSION — Boot Started $(date)" "termux-wake-lock"

# --- Disable unwanted packages ------------------------------------------
    for pkg in "${PAKS[@]}"; do
        if pm list packages | grep -q "$pkg"; then
            warn "Found unwanted package: $pkg — disabling"
            run "Disabling unwanted package $pkg" "pm disable-user --user 0 $pkg"
        else info "Package not installed: $pkg"
        fi
    done

    # --- Ensure AOSP keyboard is default ------------------------------------
    info "Setting AOSP keyboard as default"
    run "Setting AOSP keyboard as default" "settings put secure default_input_method $AOSP"

    # --- Ensure USB & Wireless Debugging ------------------------------------
    run "Enabling USB debugging" "settings put secure adb_enabled 1"
    run "Enabling wireless debugging" "settings put secure adb_wifi_enabled 1"

    # --- Ensure Install from Unknown Sources ---------------------------------
    run "Allowing installation from unknown sources" "settings put secure install_non_market_apps 1"

    # --- Ensure Auto System Update is disabled -------------------------------
    run "Disabling auto system updates" "settings put secure auto_update_system 0"
    run "Disabling OTA automatic updates" "settings put secure ota_disable_automatic_update 1"

    # --- Ensure TinyLauncher is the default Home/Launcher --------------------
    run "Enabling TinyLauncher" "pm enable com.atomicadd.tinylauncher"
    run "Setting TinyLauncher as default launcher" "settings put secure preferred_launcher com.atomicadd.tinylauncher/.MainActivity"

    info "Fixit pipeline complete $(date)"

} >> "$LOG" 2>&1

cp "$LOG" "$DOCC/boot.log" || echo "failed to copy LOG into storage/docs"
echo 'Log copied to storage/docs'




P_GUIDE=54321

PAKS=(
    'com.theorytank.a1up_launcher'
    'com.theorytank.a1up_screensaver'
    'com.cghs.stresstest'
    'com.zediel.pcbtest'
    'com.DeviceTest'
    'com.android.traceur'
    'com.android.printspooler'
    'com.android.printservice.recommendation'
)
AOSP="com.android.inputmethod.latin/.LatinIME"
DOCC="$HOME/storage/shared/Documents"



error() {
    local msg="$1"
    #termux-toast "[ERROR]: $msg"
    echo "$(ts) [ERROR]: $msg"
    #sleep 5
}

warn() {
    local msg="$1"
    #termux-toast "[WARN]: $msg"
    echo "$(ts) [WARN]: $msg"
    #sleep 2
}

info() {
    local msg="$1"
    #termux-toast "[INFO]: $msg"
    echo "$(ts) [INFO]: $msg"
    #sleep 2
}

# --- Main pipeline -----------------------------------------------------------
{
    termux-toast "Fixit v$VERSION — Boot Started $(ts)"
    termux-wake-lock
    termux-toast "Checking Environment"
    found=""
    for pkg in "${PAKS[@]}"; do
        if pm list packages | grep -q "$pkg"; then
            found="$found $pkg"
        fi
    done
    if [ -n "$found" ]; then
        nc 127.0.0.1 $P_MAIN
        while true; do
            msg=$(nc -l -p $P_MAIN)
            echo "Received: $msg" >> "$LOG"




    # --- Check for unwanted packages ------------------------------------------

    if [ -n "$found" ]; then
        termux-toast "[WARNING]: Unwanted packages found: $found"; sleep 2
        warn "Unwanted packages found: $found — opening Settings for manual removal"
        am start -n com.android.settings/.Settings

    fi
} >> "$LOG" 2>&1

cp $LOG $HOME/storage/shared/Documents/boot.log
