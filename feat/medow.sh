#!/bin/bash

VERSION="0.3.12-B"
DESC="Download target media files from URLs"

DEF_OUT="${HOME}/.local/bin/results"
DEF_TYPE="all"
OUT="${MEDOW_OUT:-$DEF_OUT}"
MIME_TYPE="${MEDOW_TYPE:-$DEF_TYPE}"
DEPS=(yt-dlp)
DOC=""

usage() {
        cat <<EOF
Usage: ${0##*/} [--out DIR] [--type all|img|vid|mus|doc] <url1> [url2] [url3]
Downloads media from the given URLs using yt-dlp.
Options:
    --out DIR       Output directory (default: $DEF_OUT or MEDOW_OUT)
    --type TYPE     all, img, vid, mus, or doc (default: $DEF_TYPE or MEDOW_TYPE)
    --version       Print version
    -h, --help      Show this help
EOF
}

missing=0
for dep in "${DEPS[@]}"; do
    command -v "$dep" >/dev/null 2>&1 || { echo "Missing dependency: $dep (https://github.com/yt-dlp/yt-dlp#installation)" >&2; missing=1; }
done
[ "$missing" -eq 0 ] || exit 1

while [ $# -gt 0 ]; do
    case "$1" in
        --out)
            shift
            [ $# -gt 0 ] || { echo "--out requires a value" >&2; exit 1; }
            OUT="${1/#\~/$HOME}"
            shift
            ;;
        --type)
            shift
            [ $# -gt 0 ] || { echo "--type requires a value" >&2; exit 1; }
            MIME_TYPE="$1"
            shift
            ;;
        --version)
            echo "${0##*/} $VERSION"
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            usage
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

case "$MIME_TYPE" in
    all|img|images|vid|videos|mus|music|doc) : ;;
    *) usage; echo "Invalid --type: $MIME_TYPE" >&2; exit 1 ;;
esac

[ $# -gt 0 ] || { usage; echo "No URLs provided" >&2; exit 1; }
urls=("$@")

DOC="$OUT/medli.ini"
if [ ! -d "$OUT" ]; then
    echo "Output directory '$OUT' doesn't exist; creating it" >&2
    mkdir -p "$OUT" || { echo "Failed to create '$OUT'; using default" >&2; OUT="$DEF_OUT"; mkdir -p "$OUT" || { echo "Failed to create default output directory: $OUT" >&2; exit 1; }; DOC="$OUT/medli.ini"; }
fi

if [ "$MIME_TYPE" = "doc" ]; then
    echo "# Media Links - $(date)" > "$DOC"
    for url in "${urls[@]}"; do
        echo "$url" >> "$DOC" || { echo "Failed to write to $DOC" >&2; exit 1; }
    done
    echo "URLs saved to $DOC"
else
    echo "Downloading ${#urls[@]} URL(s)"
    ok=0
    fail=0
    for url in "${urls[@]}"; do
        case "$MIME_TYPE" in
            "img"|"images")
                yt-dlp --quiet --no-warnings --no-progress --output "${OUT}/%(title)s.%(ext)s" --format "bestvideo" --write-thumbnail "$url" >/dev/null 2>&1 || { echo "$url: Download failed" >&2; fail=$((fail+1)); continue; }
                ;;
            "vid"|"videos")
                yt-dlp --quiet --no-warnings --no-progress --output "${OUT}/%(title)s.%(ext)s" --format "bestvideo+bestaudio/best" --merge-output-format mp4 "$url" >/dev/null 2>&1 || { echo "$url: Download failed" >&2; fail=$((fail+1)); continue; }
                ;;
            "mus"|"music")
                yt-dlp --quiet --no-warnings --no-progress --output "${OUT}/%(title)s.%(ext)s" --extract-audio --audio-format mp3 "$url" >/dev/null 2>&1 || { echo "$url: Download failed" >&2; fail=$((fail+1)); continue; }
                ;;
            "all"|*)
                yt-dlp --quiet --no-warnings --no-progress --output "${OUT}/%(title)s.%(ext)s" --format "bestvideo+bestaudio/best" --merge-output-format mp4 --write-thumbnail "$url" >/dev/null 2>&1 || { echo "$url: Download failed" >&2; fail=$((fail+1)); continue; }
                ;;
        esac
        ok=$((ok+1))
    done
    echo "Done: $ok ok, $fail failed"
    [ "$fail" -eq 0 ] || exit 1
fi
