# Command history tweaks:
# - Append history instead of overwriting
#   when shell exits.
# - When using history substitution, do not
#   exec command immediately.
# - Do not save to history commands starting
#   with space.
# - Do not save duplicated commands.
shopt -s histappend
shopt -s histverify
export HISTCONTROL=ignoreboth

# Default command line prompt.
PROMPT_DIRTRIM=2
# Test if PS1 is set to the upstream default value, and if so overwrite it with our default.
# This allows users to override $PS1 by passing it to the invocation of bash as an environment variable
[[ "$PS1" == '\s-\v\$ ' ]] && PS1='\[\e[0;32m\]\w\[\e[0m\] \[\e[0;97m\]\$\[\e[0m\] '

# Handles nonexistent commands.
# If user has entered command which invokes non-available
# utility, command-not-found will give a package suggestions.
if [ -x /data/data/com.termux/files/usr/libexec/termux/command-not-found ]; then
	command_not_found_handle() {
		/data/data/com.termux/files/usr/libexec/termux/command-not-found "$1"
	}
fi

[ -r /data/data/com.termux/files/usr/share/bash-completion/bash_completion ] && . /data/data/com.termux/files/usr/share/bash-completion/bash_completion

# // Custom Paths
export PATH="$PATH:$HOME/.local/bin"
export BINN="$HOME/.local/bin"
export ETC="$PREFIX/etc"
export OPT="$PREFIX/opt"
export CFG="$HOME/.config"
export ST="$HOME/storage/shared"
export UBU="$PREFIX/var/lib/proot-distro/installed-rootfs/ubuntu"
export UBINN="$PREFIX/var/lib/proot-distro/installed-rootfs/ubuntu/.local/bin"

# // Custom Alias
alias pdu='proot-distro login ubuntu'
alias la='ls -a'

# // Auto-cd
alias cdh="cd $HOME"
alias cde="cd $PREFIX/etc"
alias cdo="cd $PREFIX/opt"
alias cdst="cd $HOME/storage/shared"
alias binn="cd $HOME/.local/bin"

# // Termux Automations
alias tbat='termux-battery-status'
alias tbright='termux-brightness'
alias takepic='termux-camera-photo'
alias tclipb='termux-clipboard-get'
alias tclips='termux-clipboard-set'
alias tdl='termux-download'
alias tfp='termux-fingerprint'
alias tloc='termux-location'
alias tirf='termux-infrared-frequencies'
alias tirs='termux-infrared-transmit'
alias tjob='termux-job-scheduler'
alias tmedia='termux-media-player'
alias tsmedia='termux-media-scan'
alias tmic='termux-microphone-record'
alias tnote='termux-notification'
alias trnote='termux-notification-remove'
alias tsens='termux-sensor'
alias tshare='termux-share'
alias tstore='termux-storage-get'
alias tcall='termux-telephony-call'
alias tcell='termux-telephony-cellinfo'
alias tsim='termux-telephony-deviceinfo'
alias ttt='termux-toast'
alias ttr='termux-torch'
alias tspk='termux-tts-speak'
alias tusb='termux-usb -l'
alias tvib='termux-vibrate'
alias tvol='termux-volume'
alias twall='termux-wallpaper'
alias twifi='termux-wifi-enable'
alias twifi-info='termux-wifi-connectioninfo'
alias twifi-scan='termux-wifi-scaninfo'
alias twifi-set='am start -a android.settings.WIFI_SETTINGS'
alias twake='termux-wake-lock'
alias tunwake='termux-wake-unlock'
alias trset='termux-reload-settings'
alias tinfo='termux-info'
alias tweb='termux-open-url'
alias tfile='termux-open'
alias thome='input keyevent KEYCODE_HOME'
alias tset='am start -a android.settings.SETTINGS'
alias tcam='am start -a android.media.action.IMAGE_CAPTURE'
alias tapp='am start -a android.settings.APPLICATION_DETAILS -d'

# // ADB Automations
alias asnap='adb shell /system/bin/screencap -p'
alias acap='adb shell /system/bin/screenrecord'
alias aapp='adb shell monkey -p'
