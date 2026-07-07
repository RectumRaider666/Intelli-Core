from pathlib import Path
from utils import get_set
import asyncio
import sys

LIB = Path(__file__).parent
WORKER = LIB / "cfx.py"

async def start_cfx_worker(worker_id: int):
    """Start cfx.py in the background for a worker slot."""
    return await asyncio.create_subprocess_exec(
        sys.executable,
        str(WORKER),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

async def watch_prices(STATE, IDX, CFG):
    """Push incoming BTC values into the shared ring buffer and maintain a moving average."""
    recent = []
    last = None
    while True:
        current = STATE[IDX.BTC]
        if current != last:
            last = current
            ring_pos = int(last) % CFG.WINDOW_SIZE
            STATE[IDX.WINDOW + ring_pos] = last
            STATE[IDX.RBC] = (ring_pos + 1) % CFG.WINDOW_SIZE
            if len(recent) >= CFG.AVG_LEN:
                recent.pop(0)
            recent.append(last)
            if len(recent) == CFG.AVG_LEN:
                STATE[IDX.AVG] = sum(recent) / len(recent)
        await asyncio.sleep(0.5)

async def rotate_workers(CFG):
    """Rotate cfx worker processes with a short overlap window."""
    worker_id = 1
    current = await start_cfx_worker(worker_id)
    try:
        while True:
            await asyncio.sleep(CFG.CFX_LIFETIME)
            worker_id += 1
            nxt = await start_cfx_worker(worker_id)
            await asyncio.sleep(CFG.CFX_OVERLAP)
            if current.returncode is None:
                current.terminate()
                try:
                    await asyncio.wait_for(current.wait(), timeout=5)
                except asyncio.TimeoutError:
                    current.kill()
                    await current.wait()
            current = nxt
    finally:
        if current is not None and current.returncode is None:
            current.terminate()
            try:
                await asyncio.wait_for(current.wait(), timeout=5)
            except asyncio.TimeoutError:
                current.kill()
                await current.wait()

async def main():
    """Run the shared state watcher and cfx worker rotation together."""
    IDX, CFG, SHM, STATE = get_set()
    if STATE is None:
        raise RuntimeError("Shared memory state is unavailable")
    monitor_task = None
    rotate_task = None
    try:
        monitor_task = asyncio.create_task(watch_prices(STATE, IDX, CFG))
        rotate_task = asyncio.create_task(rotate_workers(CFG))
        await asyncio.gather(monitor_task, rotate_task)
    except KeyboardInterrupt:
        pass
    finally:
        if monitor_task is not None:
            monitor_task.cancel()
        if rotate_task is not None:
            rotate_task.cancel()
        await asyncio.gather(monitor_task, rotate_task, return_exceptions=True)
        if SHM is not None:
            SHM.close()

if __name__ == "__main__":
    asyncio.run(main())
