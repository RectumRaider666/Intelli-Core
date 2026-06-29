#!/usr/bin/env python3

from urllib.parse import urlparse
from pathlib import Path
import subprocess
import shutil
import random
import yt_dlp
import sys
import os

ROOT = Path(__file__).parent
DEST = "/sdcard/Download"

URL = None
FILE = None
OPTS = {
    "outtmpl": "vid.%(ext)s",
    "format": "bestvideo+bestaudio/best",
    "quiet": False
}
arg = sys.argv[1]
try:
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
    
def gen_num(min:int = 1, max:int = 100000):
    rnum = random.randint(min, max)
    return rnum

def rolling(filename:str, opts):
    targs = []
    with open(filename, "r") as f:
        for line in f:
            targ = str(line.strip())
            if targ:
                targs.append(targ)
    if targs:
        fx = int(4 * len(targs))
        for url in targs:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                yeet()
            print(f"Downloaded url: {url}")

def single(url:str, opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        yeet()
    return str(f"Downloaded url: {url}")
    
def yeet():
    fx = gen_num()
    fxname = f"{DEST}/vid{fx}.mp4"
    subprocess.run([
        "mv",
        "vid.mp4",
        f"{fxname}",
    ])
    print(f"Video moved to {fxname}")
    
if URL:
    single(URL, OPTS)
elif FILE:
    rolling(FILE, OPTS)
