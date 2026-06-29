#!/usr/bin/env bash

new_name () {
    local namef='/etc/hostname'
}

get_ssid () {
    local ssid
    ssid=$(iwgetid -r 2>/dev/null)
    if [ -z "$ssid" ]; then
        ssid=$(nmcli -t -f active.ssid dev wifi 2>/dev/null | grep '^yes:' | cut -d: -f2)
    fi
    if [ -z "$ssid" ]; then
        echo "None"
    else
        echo "$ssid"
    fi
}

gen_mac () {
    local fb=$(printf "%02X" $(( (RANDOM % 256 & 0xFC) | 0x02 )))
    local  mac="$fb"
    for i in {1..5}; do
        byte=$(printf "%02X" $((RANDOM % 256)))
        mac+=":$byte"
    done
    echo "$mac"
}

transform () {
    local mac="$(gen_mac)"
    sudo nmcli radio wifi off
    sudo ip link set dev wlp36s0 down
    sudo ip link set dev wlp36s0 address  "$mac"
    sudo nmcli radio wifi on
    sudo ip link set dev wlp36s0 up
    local stamp=$(date '+%Y-%m-%d %H:%M:%S')
    sleep 5
    local netid="$(get_ssid)"
    echo "Mac Reset $stamp" "$netid" "$mac" >> "FuXfi.log" && echo "Mac Reset $stamp"
}

check () {
    local host="google.com"
    local count=10
    local loss_thresh=40
    while true; do
        loss=$(ping -c $count -q $host 2>/dev/null | grep -oP '\d+(?=% packet loss)')
        loss=${loss:-100}
        if [ "$loss" -ge "$loss_thresh" ]; then
            local stamp=$(date '+%Y-%m-%d %H:%M:%S')
            local netid="$(get_ssid)"
            echo "Drop Detected $stamp" "$netid" >> "FuXfi.log" && echo "Drop Detected $stamp"
            transform
        else
            echo "Ping passed"
            sleep 1
        fi
    done
}

looper () {
    while true; do
        transform
}

echo "Starting Mac Spoofing"
check
