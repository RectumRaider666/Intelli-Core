from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from pathlib import Path
import urllib.parse
import contextlib
import aiosqlite
import functools
import requests
import sqlite3
import logging
import base64
import json
import pytz
import sys
import io

root = Path(__file__).parent.parent
settf = ROOT / "doc" / "settings.json"
logf = root / "data" / "sys.log"
with open(str(root / "doc" / "api.key"), "r") as f:
    key = f.read().strip()

## <!-- [Settings] ----->
class Sett():
    """Applies settings.ini configs to an object"""
    def __init__(self):
        self.LOG_FILE = None

        self.IDX_BTC = None
        self.IDX_AVG = None
        self.IDX_RSI = None
        self.IDX_ATR = None
        self.IDX_HTR = None
        self.IDX_RBC = None
        self.IDX_WINDOW = None
        self.WINDOW_SIZE = None

        self.AVG_LEN = None
        self.RSI_LEN = None
        self.ATR_LEN = None

        self.min_ri_re = None
        self.max_re_re = None
        self.min_pos_size = None
        self.max_pos_size = None
        self.max_acc_perc = None
        self.max_tte = None
        self.min_tte = None

        self.fetch_settings()

    def fetch_settings(self):
        with open(settf, "r") as f:
            ## PARSE & APPEND ATTRIBUTES

## <!-- [Database] ----->
def init_db():
    """Apply the schema to the database"""
    schema_path = root / "data" / "schema.sql"
    db_path = root / "data" / "data.db"
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        schema = f.read()
        conn.executescript(schema)
        conn.commit()
        conn.close()

async def get_db():
    """Return an async connection to the database"""
    db_path = root / "data" / "data.db"
    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute("PRAGMA synchronous=NORMAL;")
    await conn.execute("PRAGMA temp_store=MEMORY;")
    return conn

## <!-- [Prints & Logs] ----->
def ts() -> str:
    """Return a standardized time format of the current time"""
    now = datetime.now(pytz.timezone('America/New_York'))
    return now.strftime('%Y-%m-%d %H:%M:%S')

## <!-- [Logging] ----->
logging.basicConfig(
    filename = settf,
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)

class Tee:
    """Serves as the logging buffer & flush"""
    def __init__(self, logfile):
        self.terminal = sys.stdout
        self.log = open(logfile, "a", buffering=1)

    def write(self, text):
        self.terminal.write(text)
        self.log.write(text)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def logg(func):
    """Forces a wrapped func to log all print & stdout messages"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = Tee("filename")
        try:
            result = func(*args, **kwargs)
            print(f"[return] {result!r}")
            return result
        finally:
            sys.stdout.log.close()
            sys.stdout = old_stdout
    return wrapper

## <!-- [Kalshi Auth] ----->
class Signer:
    """Return signed kalshi private keys"""
    def __init__(self, private_key_path: str, key_password: bytes = None):
        self.private_key: rsa.RSAPrivateKey = self.load_private_key(file_path=private_key_path, password=key_password)

    def load_private_key(self, file_path: str, password: bytes = None) -> str:
        with open(file_path, "rb") as kf:
            private_key = serialization.load_pem_private_key(kf.read().strip(), password=None, backend=default_backend(),)
            return private_key

    def sign(self, text: str):
        message = text.encode("utf-8")
        try:
            sig = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH,
                ),
                hashes.SHA256(),
            )
            return base64.b64encode(sig).decode("utf-8")
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

class Auth:
    """Return Kalshi-Api request headers"""
    def __init__(self):
        self.API_PRIVATE_KEY_PATH = None
        self.API_ACCESS_KEY = None
        self.signer = None

    def set_key(self, access_key: str, private_key_path: str):
        self.API_PRIVATE_KEY_PATH = private_key_path
        self.API_ACCESS_KEY = access_key
        self.signer = Signer(self.API_PRIVATE_KEY_PATH)

    def headers(self, method: str, url: str):
        now = datetime.now()
        stamp = now.timestamp()
        ms = int(stamp * 1000)
        stamp_str = str(ms)
        sig = self.signer.sign(stamp_str + method + urllib.parse.urlparse(url).path)
        headers = {
            "Content-Type": "application/json",
            "KALSHI-ACCESS-KEY": self.API_ACCESS_KEY,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": stamp_str
        }
        return headers

## <!-- [Kalshi API] ----->
def balance() -> str:
    """Return current Kalshi balance and holdings value"""
    auth = Auth()
    auth.set_key(key, str(root / "docs" / "private_key.txt"))
    url = "https://external-api.kalshi.com/trade-api/v2/portfolio/balance"
    headers = auth.headers("GET", url)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        bal = float(data.get("balance") / 100)
        portf = float(data.get("portfolio_value"))
        print(f"Balance: ${bal:.2f}\nHolding Value: ${portf:.2f}\n")
        return bal, portf
    except requests.RequestException as e:
        print("Kalshi balance request failed:", e)

def get_markets(strike:str):
    """Return a target strikes market prices"""
    base = "https://external-api.kalshi.com/trade-api/v2/markets/KXBTCD-"
    now = datetime.now(pytz.timezone('America/New_York'))
    nxthr = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    year = nxthr.strftime('%y')
    month = nxthr.strftime('%b').upper()
    day = nxthr.strftime('%d')
    hour = nxthr.strftime('%H')
    option = strike - 0.01
    url = f"{base}{year}{month}{day}{hour}-T{option:.2f}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("market")
        market = {
            "strike": strike,
            "yes_ask": data.get("yes_ask_dollars"),
            "yes_bid": data.get("yes_bid_dollars"),
            "no_ask": data.get("no_ask_dollars"),
            "no_bid": data.get("no_bid_dollars")
        }
        print(json.dumps(market, indent=4))
        return market
    except requests.RequestException as e:
        print("Kalshi market request failed:", e)
        return None

def get_orders() -> list:
    """Return a dictionary of resting Kalshi orders"""
    auth = Auth()
    auth.set_key(key, str(root / "docs" / "private_key.txt"))
    url = "https://external-api.kalshi.com/trade-api/v2/portfolio/orders"
    headers = auth.headers("GET", url)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        ords = resp.json().get("orders")
        orders = {}
        for order in ords:
            if order.get("status") == "resting":
                id = order.get("order_id")
                orders[id] = {}
                orders[id]["ticker"] = order.get("ticker")
                orders[id]["act"] = order.get("action")
                orders[id]["side"] = order.get("side")
                p = int(float(order.get("yes_price_dollars")) * 100)
                if order.get("side") == "no":
                    orders[id]["price"] = 100 - p
                else:
                    orders[id]["price"] = p
                orders[id]["amount"] = order.get("initial_count_fp")
                remaining = order.get("remaining_count_fp")
                orders[id]["filled"] = float(orders[id]["amount"]) - float(remaining)
        if orders:
            return orders
        else:
            return None
    except requests.RequestException as e:
        print("Kalshi orders request failed:", e)

def del_orders() -> str:
    """Cancel all resting Kalshi orders"""
    auth = Auth()
    auth.set_key(key, str(root / "docs" / "private_key.txt"))
    ords = get_orders()
    ids = list(ords.keys())
    for id in ids:
        url = f"https://external-api.kalshi.com/trade-api/v2/portfolio/orders/{id}"
        headers = auth.headers("DELETE", url)
        try:
            resp = requests.delete(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print("Kalshi order cancel request failed:", e)

def order(ticker:str, act:str, side:str, price:float, amount:int):
    """Places a new Kalshi order"""
    auth = Auth()
    auth.set_key(key, str(root / "docs" / "private_key.txt"))
    url = "https://external-api.kalshi.com/trade-api/v2/portfolio/orders"
    payload = {
        "ticker": ticker,
        "action": act,
        "count": amount,
        "side": side,
        "time_in_force": "good_till_canceled",
        "cancel_order_on_pause": True
    }
    try:
        pval = float(price)
        if pval < 1.0:
            fp = f"{pval:.6f}"
            if side == "yes":
                payload["yes_price_dollars"] = fp
            else:
                payload["no_price_dollars"] = fp
        else:
            p_int = int(round(pval))
            if side == "yes":
                payload["yes_price"] = p_int
            else:
                payload["no_price"] = p_int
    except (TypeError, ValueError):
        if side == "yes":
            payload["yes_price"] = price
        else:
            payload["no_price"] = price
    headers = auth.headers("POST", url)
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("Kalshi order placement failed:", e.response.status_code, e.response.text)
            except Exception:
                print("Kalshi order placement failed (no body):", e)
        else:
            print("Kalshi order placement request failed:", e)
        return None