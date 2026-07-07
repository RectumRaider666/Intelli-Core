from utils import get_set, get_db, ts, init_db
from playwright.async_api import async_playwright as ap
import asyncio

POINTER = '/html/body/div/div/main/h1/div[4]/div/span[1]/span'
LAST = None

async def insert(conn, value:float):
    """Insert price data into the database"""
    await conn.execute("""INSERT OR REPLACE INTO prices (time, value) VALUES (?, ?)""", (ts(), value))
    await conn.commit()

async def fetcher() -> str:
    """Spinup playwright and extract price data"""
    init_db()
    IDX, STATE, CFG= get_set()
    conn = await get_db()
    async with ap() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://cfbenchmarks.com/data/assets/BTC")
        await page.wait_for_selector("xpath=" + POINTER)
        try:
            while True:
                txt = await page.locator("xpath=" + POINTER).text_content()
                if txt != '-' and txt is not None and txt != 0:
                    price = float(txt.replace("$", "").replace(",", ""))
                    if price != LAST:
                        print(price)
                        STATE[IDX.BTC] = price
                        LAST = price
                    await insert(conn, price)
                else:
                    pass
                await asyncio.sleep(CFG.CFX_FETCH / 1000)
        except KeyboardInterrupt:
            pass
        finally:
            await conn.close()
            await browser.close()

asyncio.run(fetcher())
