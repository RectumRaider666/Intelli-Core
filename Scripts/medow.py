#!/usr/bin/env python3
VERSION='0.3.6'

from urllib.parse import urlparse
from pathlib import Path
import subprocess
import platform
import shutil
import random
import yt_dlp
import sys
import os

# Helper functions
def is_termux():
    prefix = os.environ.get("PREFIX", "")
    return (
        "com.termux" in prefix
        or Path("/data/data/com.termux").exists()
    )

def get_dest():
    """Returns the correct DEST path based on environment"""
    if is_termux():
        return Path("/sdcard/Download")
    else:
        return Path.home() / "Downloads"

def gen_num(min:int = 1, max:int = 100000):
    """Returns a random number"""
    rnum = random.randint(min, max)
    return rnum

def yeet():
    """Moves downloads to target Dest & returns the assigned VID"""
    src = Path("vid.mp4")
    if not src.exists():
        print("No output file found, skipping")
        return None
    fx = gen_num()
    dest = DEST / f"vid{fx}.mp4"
    try:
        if is_termux():
            subprocess.run(["mv", str(src), str(dest)], check=True)
        else:
            shutil.move(src, dest)
    except Exception as e:
        print(f"Failed to move file: {e}")
        return None
    return fx
    
## MainProcess
ROOT = Path(sys.argv[0]).resolve().parent
DEST = get_dest()
DEST.mkdir(parents=True, exist_ok=True)
OPTS = {
    "outtmpl": "vid.%(ext)s",
    "format": "bestvideo+bestaudio/best",
    "quiet": False
}
URL = None
FILE = None
COMP_FILE = ROOT / "comp.ini"
COMP_FILE.touch(exist_ok=True)

try:
    arg = sys.argv[1]
    parsed = urlparse(arg)
    if parsed.scheme in ("http", "https"):
        URL = str(arg)
        print(f"Downloading from URL\n")
    elif os.path.exists(arg):
        FILE = str(arg)
        print("Downloading from FILE\n")
    else:
        sys.exit(f"{arg} is not a valid url or an existing file")
except Exception as e:
    sys.exit(f"Failure parsing argv: {e}")
        
if URL:
    try:
        with yt_dlp.YoutubeDL(OPTS) as ydl:
            ydl.download([URL])
            vid = yeet()
            with open(COMP_FILE, "a") as f:
                string = f"{vid} = {url}\n"
                f.write(string)
                print(f"Updated comp.ini with {vid} = {URL}")
        print(f"Downloaded url: {URL}")
    except Exception as e:
        print(f"Exception Occured: {e}\nExiting...")
        sys.exit(5)

elif FILE:
    targs = []
    try:
        with open(FILE, "r") as f:
            for line in f:
                targ = str(line.strip())
                if targ:
                    targs.append(targ)
        if targs:
            count = len(targs)
            compl = 0
            for url in targs:
                with yt_dlp.YoutubeDL(OPTS) as ydl:
                    ydl.download([url])
                    targs.pop(0)
                    vid = yeet()
                    with open(COMP_FILE, "a") as f:
                        string = f"{vid} = {url}\n"
                        f.write(string)
                        print(f"Updated comp.ini with {vid} = {url}")
                        compl += 1
                print(f"Progress: {compl} / {count}\nDownloaded url: {url}\n")
    except Exception as e:
        print(f"Exception Occured: {e}\nExiting...")
        sys.exit(5)
    finally:
        with open(FILE, "w") as f:
            for url in targs:
                f.write(str(f"{url}\n"))
        print("medow has finished running\nExiting...")
else:
    print("Unkown Error Occured\nExiting...")
    sys.exit(5)