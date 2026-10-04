#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from yt_dlp import YoutubeDL as YD
import subprocess
from urllib.parse import urlparse
import logging

# -- Metadata -----
VERSION = '0.1.11'
DEV = 'RectumRaider666'
DEPS = [
    "yt_dlp",
    "ffmpeg"
]

# -- Helper Functions -----
def valid_url(url:str) -> None | str:
    """Validate URL str and returns valid"""
    if not isinstance(url, str):
        logf.error(f"Error: missing expected URL string")
        return None
    try:
        parsed = urlparse(url)
        if (parsed.scheme in ("http", "https") and parsed.netloc):
            return url
    except ValueError:
        logf.error(f"{url} is not a recognized url")
        return None
  
def apply_meta(file_path: str, metadict: dict):
    """Apply MP3 metadata using FFmpeg."""
    if not metadict:
        logf.warning("Metadata application triggered, but no metadata provided")
        return
    file_path = Path(file_path)
    temp_path = file_path.with_name(
        f"{file_path.stem}.metadata{file_path.suffix}"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(file_path),
    ]
    for key, value in metadict.items():
        cmd.extend([
            "-metadata",
            f"{key}={value}"
        ])
    cmd.extend([
        "-codec", "copy",
        str(temp_path)
    ])
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True
        )
        temp_path.replace(file_path)
        logf.info(f"Metadata applied to {file_path.name}")
    except subprocess.CalledProcessError as e:
        logf.warning(
            f"Failed to apply metadata to {file_path}: "
            f"{e.stderr.decode(errors='replace')}"
        )
        if temp_path.exists():
            temp_path.unlink()
        
def fetcher(link:str) -> None | str:
    """Download the target media from url, return filename"""
    opts = {
        'format': "bestaudio/best",
        'outtmpl': os.path.join(output_dir, "%(title)s.%(ext)s"),
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': "FFmpegExtractAudio",
                'preferredcodec': "mp3",
                'preferredquality': 320
            },
            {
                'key': "EmbedThumbnail"
            }
        ]
    }
    try:
        with YD(opts) as ydl:
            logf.info(f"Info: Starting download {link}")
            info = ydl.extract_info(link, download=True)
            filepath = Path(ydl.prepare_filename(info))
            filepath = filepath.with_suffix(".mp3")
            logf.info(f"Info: {link} Downloaded to {filepath}")
            return str(filepath)
    except Exception:
        logf.exception(f"Download {link} failed: %s", link)
        return None

### --- YY2MP3 MAIN EXE LOOP --- ###
# -- Global Vars -----
SCRIPT_DIR = Path(__file__).resolve().parent
output_dir = Path(SCRIPT_DIR / 'music')
targets_file = Path(SCRIPT_DIR / "targets.ini")
log_file = Path(SCRIPT_DIR / "results.log")

# -- Global Flags -----
current = None
exifill = {}
in_targ = False

# -- Ensure Exist -----
output_dir.mkdir(parents=True, exist_ok=True)
targets_file.touch(exist_ok=True)
log_file.touch(exist_ok=True)

# -- Logging Configs -----
logging.basicConfig(
    level = logging.INFO,
    filename = log_file,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logf = logging.getLogger(__name__)

if __name__ == "__main__":
    # Find Targets, Output, and Logs #
    parser = argparse.ArgumentParser(description="Loop download & format mp3 audio from Youtube Links via Ytdlp & exiftool")
    parser.add_argument("--targ", type=str, help="Custom location of the target file to loop from")
    parser.add_argument("--out", type=str, help="Custom download output directory")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION} by {DEV}")
    args = parser.parse_args()
    if args.targ:
        targets_file = Path(args.targ)
    if args.out:
        output_dir = Path(args.out)
    if not targets_file.is_file():
        raise FileNotFoundError(f"Critical Error: '{targets_file}' does not exist")
        logf.ERROR(f"Critical Error: '{targets_file}' does not exist")
    if not output_dir.is_dir():
        makedir = input(f"'{output_dir}' is not a directory Create it? (y/n): ")
        logf.WARN(f"Warning: Output directory {output_dir} does not exist")
        if makedir.lower() in ("y", "yes"):
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            raise NotADirectoryError("Critical Error: No valid output directory")
            logf.error(f"Critical Error: No valid output directory")
            
    # Read Targets 1 by 1 #
    with open(targets_file, 'r') as tf:
        target_url = None
        for line in tf:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
    
            # Section header
            if line.startswith("[") and line.endswith("]"):
                if in_targ and target_url and exifill:
                    apply_meta(current, exifill)
                section = line[1:-1].strip().lower()
                in_targ = section == "targ"
                target_url = None
                current = None
                exifill = {}
                continue
    
            # Direct URL
            if not in_targ:
                valid_URL = valid_url(line)
                URL = valid_URL
                if URL:
                    fetcher(URL)
                continue
    
            # [targ] key/value
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if target_url is None:
                target_url = valid_url(value)
                if target_url is not None:
                    current = fetcher(target_url)
                continue
            exifill[key] = value
        if in_targ and current and exifill:
            apply_meta(current, exifill)
