from playwright.async_api import async_playwright as ap
from datetime import datetime
from pathlib import Path
import aiosqlite
import asyncio
import json
import pytz
import sys

pointer = '/html/body/div/div/main/h1/div[4]/div/span[1]/span'
root = Path(__file__).parent.parent

async def get_db():
    """Return an async connection to the database"""
    db_path = root / "data" / "data.db"
    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute("PRAGMA synchronous=NORMAL;")
    await conn.execute("PRAGMA temp_store=MEMORY;")
    return conn

async def insert(conn, value:float):
    """Insert price data into the database"""
    await conn.execute("""INSERT OR REPLACE INTO prices (time, value) VALUES (?, ?)""", (ts(), value))
    await conn.commit()

def ts():
    """Return a standardized time format of the current time"""
    now = datetime.now(pytz.timezone('America/New_York'))
    return now.strftime('%Y-%m-%d %H:%M:%S')

async def fetcher() -> str:
    """Spinup playwright and extract price data every second"""
    conn = await get_db()
    async with ap() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://cfbenchmarks.com/data/assets/BTC")
        await page.wait_for_selector("xpath=" + pointer)
        try:
            while True:
                txt = await page.locator("xpath=" + pointer).text_content()
                if txt != '-' and txt is not None and txt != 0:
                    price = float(txt.replace("$", "").replace(",", ""))
                    sys.stdout.write(json.dumps({"btc": price}) + "\n")
                    sys.stdout.flush()
                    await insert(conn, price)
                else:
                    pass
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            await conn.close()
            await browser.close()

asyncio.run(fetcher())