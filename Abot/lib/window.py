from multiprocessing import shared_memory
from pathlib import Path
import numpy as np
import subprocess
import json
import sys
import os

shmID = sys.argv(1)
cfg = sys.argv(2)

for f in os.listdir(Path("/dev/shm")):
    if f == "kbot.window.shm":
        shm = shared_memory.SharedMemory(name=str(f))
        state = np.ndarray((shmID.IDX_WINDOW + cfg.WINDOW_SIZE,), dtype=np.float64, buffer=shm.buf)
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
            state[shmID.IDX_BTC] = price
            ring_pos = int(state[shmID.IDX_RBC])
            state[shmID.IDX_WINDOW + ring_pos] = price
            state[shmID.IDX_RBC] = (ring_pos + 1) % cfg.WINDOW_SIZE
        if len(recent) >= cfg.AVG_LENGTH:
            recent.pop(0)
        recent.append(price)
        if len(recent) == 60:
            state[shmID.IDX_AVG] = sum(recent) / len(recent)
finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    shm.close()
