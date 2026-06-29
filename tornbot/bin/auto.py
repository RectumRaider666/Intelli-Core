from playwright.sync_api import sync_playwright as sp
from utils import *

vars = Vars()

def run():
    with sp() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="",
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = browser.new_page()
        page.goto()
        while True:
            pass

