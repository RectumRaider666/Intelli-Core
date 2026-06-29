source boot.env

## Formatting
ts() {
    date "+%Y-%m-%d %H:%M:%S"
}

INFO() {
    echo -e "Version: $VERSION\nDescription: $DESC\nRepo Link: $REPO\nDeveloped By: $DEV\n"
}

get_deps() {
    local missing=()
    for pkg in "${REQ_PAKS[@]}"; do
        if ! pm list packages | grep -q "$pkg"; then
            missing+=("$pkg")
        fi
    done
    if [ ${#missing[@]} -eq 0 ]; then
        echo "All required packages are installed."
    else
        echo "$(payload 'missing' "Missing packages: ${missing[*]}")" | nc 127.0.0.1 $P_MAIN
    fi
}

open_set() {
    am start -n com.android.settings/.Settings
}

payload() {
    local title="$1"
    local content="$2"
    printf '{"title":"%s","content":"%s"}\n' "$title" "$content"
}

helpME() {
    cat <<EOF
Available commands:
    h | help                     - Show this help message
    v | version                  - Prints the current Boot Version and MetaData

    settings                     - Reopens the Android Settings Menu
    open <package|activity>      - Attempts to open any app/activity from its package name or the direct activity string
    installs                     - Double-Checks for required dependencies and attempt to install any missing

    done             - Confirm you have completed the task


You can type these commands at any time in a Floating-Window for assistance.
EOF
}

## App String(ing)
ass() {
    local itm="$1"
    case "$itm" in
        # Termux
        termux|com.termux|termux-app|termux.app)
            echo "com.termux/.app.TermuxActivity" ;;
        termux-float|termux.float)
            echo "com.termux.float/.app.TermuxActivity" ;;

        # System
        settings|android.settings|com.settings)
            echo "com.android.settings/.Settings" ;;
        launcher|tinylauncher|home|dash)
            echo "" ;;

        # Store
        a-store|astore|aurora|aurora.store)
            echo "" ;;
        fdroid|f-droid|f-store|f.store)
            echo "" ;;

        # Super-Specific
        *)
            echo ""
            ;;
    esac
}

open_app() {
    local input="$1"
    local activity
    activity=$(ass "$input")
    if [ -z "$activity" ]; then
        echo "Unknown or unsupported app/activity: $input"
        termux-toast "Error: $input is not an installed app or activity"
        return 1
    fi
    local pkg="${activity%%/*}"
    if pm list packages | grep -q "$pkg"; then
        termux-toast "Openeing: $activity"
        am start -n "$activity"
    else
        echo "$pkg is not installed"
        return 1
    fi
}


