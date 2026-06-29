#!/bin/bash

deps=("git" "curl" "android-tools" "termux-api")
for itm in "${deps[@]}"; do
    if ! pkg list-installed | grep -q "^$itm"; then
        echo "Installing Dependency: $itm" && echo ""
        pkg install -y "$itm" || { echo "Failed to install dependency, ensure stable network connection and that termux is targeting a working repo"; exit 1; }
        echo "$itm Installed" && echo ""
    else
        echo "Dependency: $itm found" && echo ""
    fi
done
echo "All Dependencies Installed" && echo ""
url=$(curl -s https://api.github.com/repos/termux/termux-api/releases/latest \
    | grep browser_download_url \
    | grep '\.apk"' \
    | cut -d '"' -f 4 \
    | head -n 1)
if [ -z "$url" ]; then
    echo "Failed to get Url!"
    exit 1
fi
echo "Downloading: $url" && echo ""
curl -# -L "$url" -o "$HOME/storage/shared/Download/termux-api-latest.apk" || {  echo "Curl Failed to Install Termux-Api"; exit 1; }
echo "" && echo "Saved as: termux-api-latest.apk" && echo ""
