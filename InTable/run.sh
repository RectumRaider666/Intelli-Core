#!/data/data/com.termux/files/usr/bin/bash

INJECT_LINE='bash "$HOME/.termux/boot/boot"'
BASHRC="$PREFIX/etc/bash.bashrc"
grep -qxF "$INJECT_LINE" "$BASHRC" || echo "$INJECT_LINE" >> "$BASHRC"

# Launch Termux:Float
am start -n com.termux.window/.TermuxFloatActivity
