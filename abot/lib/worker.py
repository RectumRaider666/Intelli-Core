from pathlib import Path
import asyncio
import json
import sys

lib = Path(__file__).parent
script = lib / "cfx.py"

async def start_worker(id):
    """Starts cfx.py in the background with an ID"""
    return await asyncio.create_subprocess_exec(
        sys.executable,
        str(script),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

async def reader(id, stream, queue) -> str:
    """Reader pipeline for stdout"""
    while True:
        line = await stream.readline()
        if not line:
            break
        try:
            data = json.loads(line.decode().strip())
            await queue.put((id, data))
        except:
            continue

async def stderr_reader(id, stream) -> str:
    """Reader pipeline for stderr"""
    while True:
        line = await stream.readline()
        if not line:
            break
        sys.stderr.write(f"[cfx:{id}] {line.decode(errors='replace')}")
        sys.stderr.flush()

async def dedupe(queue) -> str:
    """De-deuplicate data from multiple pipelines then output a single stdout pipe"""
    last_price = None
    while True:
        id, data = await queue.get()
        price = data["btc"]
        if price != last_price:
            sys.stdout.write(json.dumps({"btc": price}) + "\n")
            sys.stdout.flush()
            last_price = price

async def main():
    """Rotate the sessions in a zero-gap, overlapping handoff"""
    queue = asyncio.Queue()
    id = 1
    current = await start_worker(id)
    asyncio.create_task(reader(id, current.stdout, queue))
    asyncio.create_task(stderr_reader(id, current.stderr))
    asyncio.create_task(dedupe(queue))
    while True:
        await asyncio.sleep(3600)
        id += 1
        nxt = await start_worker(id)
        asyncio.create_task(reader(id, nxt.stdout, queue))
        asyncio.create_task(stderr_reader(id, nxt.stderr))
        await asyncio.sleep(10)
        if current.returncode is None:
            current.terminate()
            await current.wait()
        current = nxt

asyncio.run(main())