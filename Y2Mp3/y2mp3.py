#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from yt_dlp import YoutubeDL as YD
import configparser
import subprocess

VERSION = '0.1.2'
DEPS = [
    "yt_dlp",
    "ffmpeg",
    "exiftool"
]

SCRIPT_DIR = Path(__file__).resolve().parent
output_dir = Path('/sdcard/Termux/music')
targets_file = SCRIPT_DIR / "targets.txt"
output_dir.mkdir(parents=True, exist_ok=True)
targets_file.touch(exist_ok=True)
configs = configparser.Config(targets_file)

def valid_url:str):
    try:
    if not metadata_dict:
        return
    
    cmd = ["exiftool"]
    for key, value in metadata_dict.items():
        cmd.append(f"-{key}={value}")
    cmd.append(str(filepath))
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Metadata applied to {filepath.name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to apply metadata: {e.stderr.decode()}")        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False
    
def apply_meta (file_path:str, metadict:dict):
    if not metadata_dict:
        return
    cmd = ["exiftool"]
    for key, value in metadata_dict.items():
        cmd.append(f"-{key}={value}")
    cmd.append(str(filepath))
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Metadata applied to {filepath.name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to apply metadata: {e.stderr.decode()}")
    
def cli():
    global output_dir, targets_file 
    parser = argparse.ArgumentParser(description="Loop download & format mp3 audio from Youtube Links via Ytdlp & exiftool")
    parser.add_argument("--targ", type=str, help="Custom location of the target file to loop from")
    parser.add_argument("--out", type=str, help="Custom download output directory")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION} ({DATE}) by {DEV}")
    args = parser.parse_args()
    if args.targ:
        targets_file = Path(args.targ)
        if not targets_file.is_file():
            raise FileNotFoundError(f"Critical error: '{targets_file}' does not exist.")
    if args.out:
        output_dir = Path(args.out)
        if not output_dir.is_dir():
            makedir = input(f"'{output_dir}' is not a directory. Create it? (y/n): ")
            if makedir.lower() in ("y", "yes"):
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                raise NotADirectoryError("Execution stopped: No valid output directory selected.")

def fetcher():
    opts = {
        'format': "bestaudio/best",
        'outtmpl': os.path.join(output, "%(title)s.%(ext)s"),
        'postprocessors': [{
            'key': "FFmpegExtractAudio",
            'preferredcodec': "mp3",
            'preferredquality': 320
        }]
    }
    with open(targets_file, 'r') as f:
        for line_num, line in enumerate(f, 1)

    with YD(opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    cli()
    fetcher()
else:
    fetcher()