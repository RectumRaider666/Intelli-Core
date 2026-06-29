#!/data/data/com.termux/files/usr/bin/bash
source boot.env; source utils.sh

mkfifo /tmp/guide_in /tmp/guide_out 2>/dev/null

# Print everything worker sends
tail -f /tmp/guide_out &

while true; do
    read user_input
    echo "$user_input" > /tmp/guide_in
done
