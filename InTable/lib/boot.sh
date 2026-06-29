#!/data/data/com.termux/files/usr/bin/bash
source lib/boot.env; source lib/utils.sh

termux-toast "Boot Controller Started on Port $P_MAIN"
echo "$(ts) Boot Detected: Starting Background Worker Service" >> "$LOG"
lib/worker.sh &

## Start Delegating and Logging
while true; do
    msg=$(nc -l -p $P_MAIN)
    echo "$(ts) Received: $msg" >> "$LOG"
    title=$(echo "$msg" | jq -r .title)
    content=$(echo "$msg" | jq -r .content)
    local stepp=1
    case $title in
        success)
            termux-toast "Task $step: Finished Successfully"
            stepp=$((stepp + 1))
            echo "$(ts) $content" >> "$LOG"
            ;;
        removed:*)
            pkg=${msg#removed:}
            termux-toast "Package $pkg was Removed"
            echo "$(ts) Removed Package: $pkg" >> "$LOG"
            ;;
        installed:*)
            pkg=${msg#installed:}
            termux-toast "Package $pkg was Installed"
            echo "$(ts) Installed Package: $pkg" >> "$LOG"
            ;;
        user_confirmed)
            echo "$(ts) User Confirmed Action: Checking State" >> "$LOG"
            ;;
        found-paks)
            termux-toast "Unwanted Packages were found! Starting Removal Guide"
            echo "$(ts) $content" >> "$LOG"
            ;;
        missing:*)
            termux-toast "Packages are Missing! Attempting to Re-Install"
            echo "$(ts) $content" >> "$LOG"
            ;;
        timeout)
            echo "Timeout detected, re-opening settings." >> "$LOG"
            am start -n com.android.settings/.Settings
            ;;

        *)
            echo "Unknown message: $msg" >> "$LOG"
            ;;
    esac
done
