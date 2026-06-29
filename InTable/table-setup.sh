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
  if head -c 2 "$out" | grep -q '^PK'; then
    log "Installing: $out"
    adb install -r "$out" || warn "adb install failed: $out"
  else
    warn "Not an APK (or got HTML/redirect). Skipping: $url"
    file "$out" || true
  fi
done
log "Done."
