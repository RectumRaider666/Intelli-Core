## <!-- [1] Imports ----->
from lib.utils import SettingsLoader, SHM_IDX, Tee, logg, init_db, ts
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
root = Path(__file__).parent
win_script = root / "lib" /"window.py"
schema_path = root / "data" / "schema.sql"
db_path = root / "data" / "data.db"

## <!-- [3] Helpers ----->
def create_window():
    """Create the shared_memory object"""
    shm = None
    for f in os.listdir(Path("/dev/shm")):
        if f == "kbot.window.shm":
            try:
                shm = shared_memory.SharedMemory(name=str(f))
                shm.close()
                shm.unlink()
            except FileNotFoundError:
                logger.warning(f"Segment {f} disappeared during cleanup")
                print("Segment ")
            except Exception as e:
                logger.warning(f"Unexpected error during cleanup: {e}")
    OBJ_SIZE = cfg.WINDOW_SIZE + shmID.IDX_WINDOW
    shm = shared_memory.SharedMemory(create=True, size=OBJ_SIZE * 8, name='kbot.window.shm')
    state = np.ndarray((OBJ_SIZE,), dtype=np.float64, buffer=shm.buf)
    state[:] = 0.0
    state[shmID.IDX_RBC] = 0
    db_path = root / "data" / "data.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""SELECT value FROM prices ORDER BY rowid DESC LIMIT 3600""").fetchall()
    conn.close()
    rows.reverse()
    prices = np.array([row[0] for row in rows], dtype=np.float64)
    if prices.size:
        fill_count = min(prices.size, cfg.WINDOW_SIZE)
        state[shmID.IDX_WINDOW:shmID.IDX_WINDOW + fill_count] = prices[:fill_count]
    return shm, state

def update() -> tuple:
    """Update the shared memory segment and return adjusted tte and now"""
    now = datetime.now(pytz.timezone('America/New_York'))
    nxthr = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    remaining = (nxthr - now).total_seconds()
    tte = remaining
    candles = get_candles()
    atr(candles)
    return tte, now

def get_settings():
    """Init DB, SHM, Logger, and Config"""
    init_db()
    shmID = SHM_IDX()
    cfg = SettingsLoader()
    logger = logging.getLogger()
    LEVELS = {
        "D": logging.DEBUG,
        "I": logging.INFO,
        "W": logging.WARNING,
        "E": logging.ERROR,
        "F": logging.CRITICAL,
    }
    logger.setLevel(LEVELS.get(str(cfg.LOG_LEVEL).upper(), logging.INFO))
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        handler = logging.FileHandler(cfg.LOG_FILE)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.info(f"Kbot started")
    return shmID, cfg, logger

## <!-- [4] MATH ----->
def get_candles():
    """Converts the Ring Buffer into 1m Candles"""
    prices = state[shmID.IDX_WINDOW:shmID.IDX_WINDOW + cfg.WINDOW_SIZE]
    oldest = int(state[shmID.IDX_RBC])
    candles = np.empty((60, 4), dtype=np.float64)
    for i in range(60):
        start = (oldest + i * 60) % cfg.WINDOW_SIZE
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
    state[shmID.IDX_HTR] = max(true_ranges) if true_ranges else 0.0
    state[shmID.IDX_ATR] = sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

def rsi(candles, length:int = 14):
    """Calculates the RSI"""
    pass

## <!-- [5] MAIN ----->
shmID, cfg, logger = get_settings()
shm, state = create_window()
ste, now = update()
proc = subprocess.Popen([sys.executable, f"{win_script}", shmID, cfg], stdout = subprocess.DEVNULL)
upcount = 0
try:
    while True:
        if upcount == 60:
            ste, now = update()
            if cfg.TRADE16 == False and now.hour == 16:
                while now.hour == 16:
                    logger.info(f"Sleeping through 16 - 17")
                    time.sleep(ste)
            upcount = 0
        else:
            upcount += 1
        report = {
            "btc_price": state[shmID.IDX_BTC],
            "ste": ste,
            "tte": ste / 60,
            "avg_price": state[shmID.IDX_AVG],
            "ind_rsi_s": state[shmID.IDX_RSI_S],
            "ind_rsi_l": state[shmID.IDX_RSI_L],
            "ind_atr_t": state[shmID.IDX_ATR_T],
            "ind_atr_m": state[shmID.IDX_ATR_M],
            "ind_atr_w": state[shmID.IDX_ATR_W],
            "ind_htr_t": state[shmID.IDX_HTR_T],
            "ind_htr_w": state[shmID.IDX_HTR_W],
            "acc_val": state[shmID.IDX_ACC],
            "buf_cnt": state[shmID.IDX_RBC]
        }
        print(json.dumps(report, indent=4))
        logger.info(f"Report: {json.dumps(report, indent=4)}")
        ste -= 1
        time.sleep(1)
except Exception as e:
    logger.error(f"Exception Occured: {e}")
finally:
    proc.terminate()
    shm.close()
    shm.unlink()



# instead of piping the data back from cfx through worker, then through window, just have cfx itself have access to the shared memeory block so it can change the price
# directly, Now worker.py can also be refactored to not have to worry about any piping at all. Just the zero gap handovers, then window just needs to handle the ring buffer
# at that point, worker and window can almost be combined into one. Windows updating logic can also be refactored to work as a sort of watchdog instead of recieving
# inputs directly. It can just watch the btc price index block and everytime it changes, update the ring buffer. This will GREATLY reduce I/O overhead