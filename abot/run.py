## <!-- [1] Imports ----->
from multiprocessing import shared_memory
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import subprocess
import sqlite3
import json
import pytz
import time
import sys

## <!-- [2] Variables ----->
# /2.1/ Directory
root = Path(__file__).parent
win_script = root / "lib" /"window.py"
schema_path = root / "data" / "schema.sql"
db_path = root / "data" / "data.db"

# /2.2/ Trackers
up_count = 0

# /2.3/ SharedObject Structure
IDX_BTC = 0                             # Recent Bitcoin Price
IDX_AVG = 1                             # Recent Average Bitcoin Price
IDX_RSI = 2                             # Calculated RSI
IDX_ATR = 3                             # Calculated Average True Range
IDX_HTR = 4                             # The Highest True Range Calculation in ATR
IDX_RBC = 5                             # Ring Buffer Count - The position of the oldest entry in the rolling buffer ring
IDX_WINDOW = 6                          # The Start of the Rolling Window
WINDOW_SIZE = 3600                      # The number of positions in the window
OBJ_SIZE = IDX_WINDOW + WINDOW_SIZE     # The total size of the object

## <!-- [3] Helpers ----->
def create_window():
    """Create the shared_memory object"""
    shm = None
    shm = shared_memory.SharedMemory(create=True, size=OBJ_SIZE * 8)
    state = np.ndarray((OBJ_SIZE,), dtype=np.float64, buffer=shm.buf)
    state[:] = 0.0
    state[IDX_RBC] = 0
    db_path = root / "data" / "data.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""SELECT value FROM prices ORDER BY rowid DESC LIMIT 3600""").fetchall()
    conn.close()
    rows.reverse()
    prices = np.array([row[0] for row in rows], dtype=np.float64)
    if prices.size:
        fill_count = min(prices.size, WINDOW_SIZE)
        state[IDX_WINDOW:IDX_WINDOW + fill_count] = prices[:fill_count]
    return shm, state

def update() -> float:
    now = datetime.now(pytz.timezone('America/New_York'))
    nxthr = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    remaining = (nxthr - now).total_seconds()
    tte = remaining
    candles = get_candles()
    atr(candles)
    return tte

## <!-- [4] MATH ----->
def get_candles():
    """Converts the Ring Buffer into 1m Candles"""
    prices = state[IDX_WINDOW:IDX_WINDOW + WINDOW_SIZE]
    oldest = int(state[IDX_RBC])
    candles = np.empty((60, 4), dtype=np.float64)
    for i in range(60):
        start = (oldest + i * 60) % WINDOW_SIZE
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
    state[IDX_HTR] = max(true_ranges) if true_ranges else 0.0
    state[IDX_ATR] = sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

def rsi(candles, length:int = 14):
    """Calculates the RSI"""
    pass

## <!-- [5] MAIN ----->
conn = sqlite3.connect(db_path)
with open(schema_path, "r") as f:
    schema = f.read()
    conn.executescript(schema)
    conn.commit()
conn.close()
shm, state = create_window()
ste = update()
proc = subprocess.Popen([sys.executable, f"{win_script}", shm.name], stdout = subprocess.DEVNULL)
try:
    while True:
        if up_count == 60:
            ste = update()
            up_count = 0
        else:
            up_count += 1
        report = {
            "ste": ste,
            "tte": ste / 60,
            "btc_price": state[IDX_BTC],
            "avg_price": state[IDX_AVG],
            "ind_rsi": state[IDX_RSI],
            "ind_atr": state[IDX_ATR],
            "ind_htr": state[IDX_HTR],
            "buf_cnt": state[IDX_RBC]
        }
        print(json.dumps(report, indent=4))
        ste -= 1
        time.sleep(1)
finally:
    proc.terminate()
    shm.close()
    shm.unlink()