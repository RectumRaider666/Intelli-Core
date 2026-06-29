#!/data/data/com.termux/files/usr/bin/bash
source boot.env; source utils.sh

mid_man() {
    mkfifo /tmp/guide_in /tmp/guide_out 2>/dev/null
    while true; do
        if read -t 60 user_input < /tmp/guide_in; then
            case "$user_input" in
                h|help)
                    helpME ;;
                v|version)
                    INFO ;;
                settings)
                    open_set ;;
                open\ *)
                    pkg="${user_input#open }"
                    open_app "$pkg"
                    ;;
                installs)
                    get_deps
                    ;;
                done)
                    if ! pm list packages | grep -q "$pkg"; then
                        echo "$(payload 'removed' "$pkg")" | nc 127.0.0.1 $P_MAIN
                        break
                    else
                        echo "Package $pkg still installed. Please try again." > /tmp/guide_out
                    fi
                    ;;
                *)
                    echo "Unknown command. 'help' for a list of valid commands" > /tmp/guide_out
                    ;;
            esac
        fi
    done

    rm /tmp/guide_in /tmp/guide_out
}


## Main Environment Check Pipeline -- guide.sh should never be triggered unless absolutely neccessary!
    # 0: Check if I released any newer software in the repo (will add this later probably to boot actually)

    # 1: Check that all required dir & files are present
    # 2: Check if any unwanted packages are present
    # 3: Check if any unwanted packages that we cant fully remove have wrong permissions
    # 4: Check if any req packages are missing / broken
    # 5: Check req packages have the right permissions
    # 6: Check if any user-wanted packages are missing/broken (we will add a settings.json user can list packages in)
    # 7: Check user-wanted package permissions (added packages should have specific permissions listed in settings.json, if it is not listed, we assume default-minimalism)
    # 8: Check for Required System Settings
    # 9: Check for user-wanted System Settigns (again will be in a future settings.json where users set settings={ <setting_label>: <expected_value>, })

active=true
step=0
main() {
    step=$((step + 1))
    found=""
    for pkg in "${rem_paks[@]}"; do
        if pm list packages | grep -q "$pkg"; then
            found="$found $pkg"
        fi
    done
    if [ -z "$found" ]; then
        echo "$(payload 'success' 'No Unwanted OEM Packages Detected')" | nc 127.0.0.1 $P_MAIN
        step=$((step + 1))
    elif [ -n "$found" ]; then
        echo "$(payload 'found-paks' "Found Unwanted OEM Packages -- $found")" | nc 127.0.0.1 $P_MAIN
        termux-float -e lib/guide.sh &
        for pkg in $found; do
            echo "Task: Delete $pkg in Settings > Apps & Notifications > App_Name > Uninstall" > /tmp/guide_in
            echo "Type help at any time to get a list of Usable Commands" > /tmp/guide_in
            mid_man "$pkg"
        done
        step=$((step + 1))
    fi
}
