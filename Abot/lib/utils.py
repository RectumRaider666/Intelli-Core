from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from multiprocessing import shared_memory
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import urllib.parse
import aiosqlite
import functools
import requests
import sqlite3
import base64
import json
import pytz
import sys
import os

ROOT = Path(__file__).parent.parent
settf = ROOT / "doc" / "settings.json"
logf = ROOT / "data" / "sys.log"
with open(str(ROOT / "doc" / "api.key"), "r") as f:
    key = f.read().strip()

## <!-- [Settings] ----->
def get_set():
    IDX = idx()
    CFG = SettingsLoader().load()
    try:
        SHM = shared_memory.SharedMemory(name='kbot.window.shm')
        STATE = np.ndarray((IDX.WINDOW + CFG.WINDOW_SIZE,), dtype=np.float64, buffer=SHM.buf)
        return IDX, CFG, SHM, STATE
    except FileNotFoundError:
        return None

@dataclass
class idx:
    """Applies Strict Static Schema to the SHM Index"""
    BTC = 1
    TTE = 2
    AVG = 3
    RSI_S = 4
    RSI_L = 5
    ATR_T = 6
    ATR_M = 7
    ATR_W = 8
    HTR_T = 9
    HTR_W = 10
    ACC = 11
    RBC = 12
    WINDOW = 13

@dataclass
class Sett:
    """Prepares Default Dynamic Settings & Types"""
    MODE: str = "Paper"
    LOG_LVL: str = "I" ## Debug(D),  Info(I), Warning(W), Error(E), Fatal(F) ##
    LOG_FILE: Path = settf
    WINDOW_SIZE: int = 3600
    AVG_LEN: int = 60
    RSI_LEN_S: int = 9
    RSI_LEN_L: int = 24
    RSI_HIGH: int = 80
    RSI_LOW: int = 20
    ATR_LEN_W: int = 40
    ATR_LEN_M: int = 15
    ATR_LEN_T: int = 7
    HTR_LEN_W: int = 50
    HTR_LEN_T: int = 10
    TRADE16: bool = False
    STOP_MARKET_ENABLE: bool = True
    TAKE_MARKET_ENABLE: bool = False
    R_R: float = 2
    TTE_MAX: int = 900
    TTE_MIN: int = 30
    ENTRY_SLIP: float = 2
    ENTRY_POS_RISK: float = 5
    ENTRY_POS_MAX: float = 12
    STOP_RAISE: bool = True
    STOP_RAISE_RR: float = 3
    STOP_RAISE_FX: float = 10
    STOP_RAISE_VAL: float = 2
    STOP_RAISE_COUNT: int = 3
    STOP_RAISE_DELAY: int = 60
    TAKE_PERC: float = 15
    TAKE_VAL: float = 300
    REST_LEN: int = 16
    REST_RATE6: int = 3
    REST_RATE12: int = 5
    REST_RATE24: int = 10
    REST_LOCK_LEN: int = 4
    REST_LOCK_PL: int = 15
    CFX_LIFE: int = 60
    CFX_FETCH: int = 1000
    CFX_OVERLAP: int = 10

class SettingsLoader:
    """Applies Dynamic Setting Changes"""
    def __init__(self, path=settf):
        self.path = path

    def load(self):
        """Parse settings.json and apply changes within thresholds"""
        with open(self.path, "r") as f:
            data = json.load(f)
        cfg = Sett()

        """Setting System Mode -- Implimented"""
        if data.get("sys.mode.paper"):
            cfg.MODE = "Paper"
        elif data.get("sys.mode.train"):
            cfg.MODE = "Train"
        elif data.get("sys.mode.test"):
            cfg.MODE = "Test"
        elif data.get("sys.mode.live"):
            cfg.MODE = "Live"

        """Handeling Logs -- Implimented"""
        cfg.LOG_LVL = data.get("log.lvl", cfg.LOG_LVL)
        custom = data.get("log.custom")
        if custom and os.path.exists(custom):
            cfg.LOG_FILE = custom

        """CFX Management -- Implimented"""
        life = data.get("cfx.lifetime")
        if life and 10 <= life <= 120:
            cfg.CFX_LIFE = life
        fetch = data.get("cfx.fetch")
        if fetch and 100 <= fetch <= 1000:
            cfg.CFX_FETCH = fetch
        overlap = data.get("cfx.overlap")
        if overlap and 3 <= overlap <= 60:
            cfg.CFX_OVERLAP = overlap

        """Rolling Windows Size -- Implimented"""
        win = data.get("window.buffer.size")
        if win and win >= 3600:
            cfg.WINDOW_SIZE = win
        avg = data.get("window.avg.size")
        if avg and avg >= 60:
            cfg.AVG_LEN = avg

        """Calculating Indicators -- Implimented(minus RSI)"""
        rsi_s = data.get("tech.rsi.short")
        if rsi_s and 2 <= rsi_s <= 60:
            cfg.RSI_LEN_S = rsi_s
        rsi_l = data.get("tech.rsi.long")
        if rsi_l and 2 <= rsi_l <= 60:
            cfg.RSI_LEN_L = rsi_l
        rsi_high = data.get("tech.rsi.high")
        if rsi_high and rsi_high > 50:
            cfg.RSI_HIGH = rsi_high
        rsi_low = data.get("tech.rsi.low")
        if rsi_low and rsi_low < 50:
            cfg.RSI_LOW = rsi_low
        atr_w = data.get("tech.atr.wide")
        if atr_w and 2 <= atr_w <= 60:
            cfg.ATR_LEN_W = atr_w
        atr_m = data.get("tech.atr.mid")
        if atr_m and 2 <= atr_m <= 60:
            cfg.ATR_LEN_M = atr_m
        atr_t = data.get("tech.atr.thin")
        if atr_t and 2 <= atr_t <= 60:
            cfg.ATR_LEN_T = atr_t
        htr_w = data.get("tech.htr.wide")
        if htr_w and 10 <= htr_w <= 60:
            cfg.HTR_LEN_W = htr_w
        htr_t = data.get("tech.htr.thin")
        if htr_t and 10 <= htr_t <= 60:
            cfg.HTR_LEN_T = htr_t

        """Risk Managment -- Not implimented"""
        stop_market = data.get("stop.market.enable")
        if stop_market is not None:
            cfg.STOP_MARKET_ENABLE = stop_market
        stop_raise = data.get("stop.raise.enable")
        if stop_raise is not None:
            cfg.STOP_RAISE = stop_raise
        raise_rr = data.get("stop.raise.rr")
        if raise_rr and raise_rr >= 3:
            cfg.STOP_RAISE_RR = raise_rr
        raise_fx = data.get("stop.raise.fx")
        if raise_fx and raise_fx >= 3:
            cfg.STOP_RAISE_FX = raise_fx
        raise_val = data.get("stop.raise.val")
        if raise_val and raise_val >= 2:
            cfg.STOP_RAISE_VAL = raise_val
        raise_count = data.get("stop.raise.count")
        if raise_count and raise_count >= 0:
            cfg.STOP_RAISE_COUNT = raise_count
        raise_delay = data.get("stop.raise.delay")
        if raise_delay and raise_delay >= 5:
            cfg.STOP_RAISE_DELAY = raise_delay
        take_perc = data.get("take.takeall.perc")
        if take_perc and 1 <= take_perc < 100:
            cfg.TAKE_PERC = take_perc
        take_val = data.get("take.takeall.val")
        if take_val and take_val >= 1:
            cfg.TAKE_VAL = take_val
        take_market = data.get("take.market.enable")
        if take_market is not None:
            cfg.TAKE_MARKET_ENABLE = take_market

        """Bad Streak RESTing Config -- Not implimented"""
        rest_len = data.get("rest.len")
        if rest_len and 12 <= rest_len <= 24:
            cfg.REST_LEN = rest_len
        rest6 = data.get("rest.rate6")
        if rest6 and rest6 >= 0:
            cfg.REST_RATE6 = rest6
        rest12 = data.get("rest.rate12")
        if rest12 and rest12 >= 0:
            cfg.REST_RATE12 = rest12
        rest24 = data.get("rest.rate24")
        if rest24 and rest24 >= 0:
            cfg.REST_RATE24 = rest24
        lock_len = data.get("rest.lock.len")
        if lock_len and 3 <= lock_len <= 24:
            cfg.REST_LOCK_LEN = lock_len
        lock_pl = data.get("rest.lock.pl")
        if lock_pl and 1 <= lock_pl <= 50:
            cfg.REST_LOCK_PL = lock_pl

        """Trade Entry Constraints -- Not implimented"""
        rr = data.get("entry.rr.min")
        if rr and rr >= 2:
            cfg.R_R = rr
        tte_max = data.get("entry.tte.max")
        if tte_max and tte_max <= 3600:
            cfg.TTE_MAX = tte_max
        tte_min = data.get("entry.tte.min")
        if tte_min and tte_min >= 0:
            cfg.TTE_MIN = tte_min
        slip = data.get("entry.slip.min")
        if slip and slip <= 3:
            cfg.ENTRY_SLIP = slip
        pos_risk = data.get("entry.pos.risk")
        if pos_risk and 0 < pos_risk <= 100:
            cfg.ENTRY_POS_RISK = pos_risk
        pos_max = data.get("entry.pos.max")
        if pos_max and 0 < pos_max <= 100:
            cfg.ENTRY_POS_MAX = pos_max
        return cfg

## <!-- [Database] ----->
def init_db():
    """Apply the schema to the database"""
    schema_path = ROOT / "data" / "schema.sql"
    db_path = ROOT / "data" / "data.db"
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        schema = f.read()
        conn.executescript(schema)
        conn.commit()
        conn.close()

async def get_db():
    """Return an async connection to the database"""
    db_path = ROOT / "data" / "data.db"
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
    auth.set_key(key, str(ROOT / "docs" / "private_key.txt"))
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
    auth.set_key(key, str(ROOT / "docs" / "private_key.txt"))
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
    auth.set_key(key, str(ROOT / "docs" / "private_key.txt"))
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
    auth.set_key(key, str(ROOT / "docs" / "private_key.txt"))
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
