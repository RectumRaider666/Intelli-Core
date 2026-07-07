## <!-- [1] Imports ----->
from lib.utils import get_set, init_db
from multiprocessing import shared_memory
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import subprocess
import logging
import sqlite3
import json
import pytz
import time
import sys
import os

## <!-- [2] Variables ----->
# /2.1/ Directory
ROOT = Path(__file__).parent
WORKER = ROOT / "lib" /"window.py"

## <!-- [3] Helpers ----->
def create_window():
    """Create the shared_memory object"""
    for f in os.listdir(Path("/dev/shm")):
        if f == "kbot.window.shm":
            try:
                SHM = shared_memory.SharedMemory(name=str(f))
                SHM.close()
                SHM.unlink()
            except FileNotFoundError:
                logger.warning(f"Segment {f} disappeared during cleanup")
                print("Segment ")
            except Exception as e:
                logger.warning(f"Unexpected error during cleanup: {e}")
    OBJ_SIZE = (CFG.WINDOW_SIZE + IDX.WINDOW) * 8
    SHM = shared_memory.SharedMemory(create=True, size=OBJ_SIZE, name='kbot.window.shm')
    STATE = np.ndarray((OBJ_SIZE,), dtype=np.float64, buffer=SHM.buf)
    STATE[:] = 0.0
    STATE[IDX.RBC] = 0
    db_path = ROOT / "data" / "data.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""SELECT value FROM prices ORDER BY rowid DESC LIMIT 3600""").fetchall()
    conn.close()
    rows.reverse()
    prices = np.array([row[0] for row in rows], dtype=np.float64)
    if prices.size:
        fill_count = min(prices.size, CFG.WINDOW_SIZE)
        STATE[IDX.WINDOW:IDX.WINDOW + fill_count] = prices[:fill_count]
    return SHM, STATE

def update() -> tuple:
    """Update the shared memory segment and return adjusted tte and now"""
    now = datetime.now(pytz.timezone('America/New_York'))
    nxthr = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    remaining = (nxthr - now).total_seconds()
    tte = remaining
    candles = get_candles()
    atr(candles)
    return tte, now

## <!-- [4] MATH ----->
def get_candles():
    """Converts the Ring Buffer into 1m Candles"""
    prices = STATE[IDX.WINDOW:IDX.WINDOW + CFG.WINDOW_SIZE]
    oldest = int(STATE[IDX.RBC])
    candles = np.empty((60, 4), dtype=np.float64)
    for i in range(60):
        start = (oldest + i * 60) % CFG.WINDOW_SIZE
        block = prices.take(range(start, start + 60), mode="wrap")
        candles[i, 0] = block[0]
        candles[i, 1] = block.max()
        candles[i, 2] = block.min()
        candles[i, 3] = block[-1]
    return candles

def atr(candles, length:int = 14):
    """Calculates the ATR and the highest TR in range"""
    recent = candles[:length]
    true_ranges = []
    prev_close = recent[0][0]
    for candle in recent:
        high = candle[1]
        low = candle[2]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
        prev_close = candle[3]
    STATE[IDX.HTR] = max(true_ranges) if true_ranges else 0.0
    STATE[IDX.ATR] = sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

def rsi(candles, length:int = 14):
    """Calculates the RSI"""
    pass

## <!-- [5] MAIN ----->
init_db()
SHM, STATE = create_window()
IDX, CFG = get_set()
logger = logging.getLogger()
LEVELS = {
    "D": logging.DEBUG,
    "I": logging.INFO,
    "W": logging.WARNING,
    "E": logging.ERROR,
    "F": logging.CRITICAL,
}
logger.setLevel(LEVELS.get(str(CFG.LOG_LEVEL).upper(), logging.INFO))
if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
    handler = logging.FileHandler(CFG.LOG_FILE)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.info(f"Kbot started")
ste, now = update()
proc = subprocess.Popen([sys.executable, f"{WORKER}"], stdout = subprocess.DEVNULL)
upcount = 0
try:
    while True:
        if upcount == 60:
            ste, now = update()
            if CFG.TRADE16 == False and now.hour == 16:
                while now.hour == 16:
                    logger.info(f"Sleeping through 16 - 17")
                    time.sleep(ste)
            upcount = 0
        else:
            upcount += 1
        report = {
            "btc_price": STATE[IDX.BTC],
            "ste": ste,
            "tte": ste / 60,
            "avg_price": STATE[IDX.AVG],
            "ind_rsi_s": STATE[IDX.RSI_S],
            "ind_rsi_l": STATE[IDX.RSI_L],
            "ind_atr_t": STATE[IDX.ATR_T],
            "ind_atr_m": STATE[IDX.ATR_M],
            "ind_atr_w": STATE[IDX.ATR_W],
            "ind_htr_t": STATE[IDX.HTR_T],
            "ind_htr_w": STATE[IDX.HTR_W],
            "acc_val": STATE[IDX.ACC],
            "buf_cnt": STATE[IDX.RBC]
        }
        print(json.dumps(report, indent=4))
        logger.info(f"Report: {json.dumps(report, indent=4)}")
        ste -= 1
        time.sleep(1)
except Exception as e:
    logger.error(f"Exception Occured: {e}")
finally:
    proc.terminate()
    SHM.close()
    SHM.unlink()
