from multiprocessing import shared_memory
from pathlib import Path
import numpy as np
import subprocess
import json
import sys

SHM_NAME = sys.argv[1]
WINDOW_SIZE = 3600
IDX_BTC = 0                             # Recent Bitcoin Price
IDX_AVG = 1                             # Recent Average Bitcoin Price
IDX_RSI = 2                             # Calculated CRSI
IDX_ATR = 3                             # Calculated Average True Range
IDX_HTR = 4                             # The Highest True Range Calculation in ATR
IDX_RBC = 5                             # Ring Buffer Count - The position of the oldest entry in the rolling buffer ring
IDX_WINDOW = 6                          # The Start of the Rolling Window

AVG_LENGTH = 60

shm = shared_memory.SharedMemory(name=SHM_NAME)
state = np.ndarray((IDX_WINDOW + WINDOW_SIZE,), dtype=np.float64, buffer=shm.buf)
lib = Path(__file__).parent
worker_script = lib / "worker.py"
recent = []

proc = subprocess.Popen(
    [
        sys.executable,
        str(worker_script)
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)
try:
    while True:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "btc" in payload:
            price = float(payload["btc"])
            state[IDX_BTC] = price
            ring_pos = int(state[IDX_RBC])
            state[IDX_WINDOW + ring_pos] = price
            state[IDX_RBC] = (ring_pos + 1) % WINDOW_SIZE
        if len(recent) >= AVG_LENGTH:
            recent.pop(0)
        recent.append(price)
        if len(recent) == 60:
            state[IDX_AVG] = sum(recent) / len(recent)
finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    shm.close()