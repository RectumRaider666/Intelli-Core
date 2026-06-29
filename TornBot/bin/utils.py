# Utils.py - Utility Functions

import os
import pytz
import json
import logging
import sqlite3
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

load_dotenv()

# /1.0/ Variables
class Vars:
    """Insert Variables as a Config Class's Attributes"""
    def __init__(self):
        self.API_KEY = os.getenv('API_KEY')
        self.headers = {
            "accept": "application/json",
            "Authorization": f"ApiKey {self.API_KEY}"
        }
        self._dir = Path(os.getenv('BASE'))
        self.bin_dir = Path(os.getenv('bin_dir'))
        self.data_dir = Path(os.getenv('data_dir'))
        self.log_dir = Path(os.getenv('log_dir'))
        self.dirs = [self._dir, self.bin_dir, self.data_dir, self.log_dir]
        self.log_file = Path(os.getenv('log_file'))
        self.db_file = Path(os.getenv('db_file'))
        self.sql_file = Path(os.getenv('sql_file'))
        self.files = [self.db_file, self.sql_file, self.log_file]
        self.last_update = None
        self.VERSION = os.getenv('VERSION')
        self.BUILD = os.getenv('BUILD')

class Settings:
    """Insert Setting Configs as Class Attributes"""
    def __init__(self):
        pass


vars = Vars()

# /2.0/ TimeStamps
def ts():
    """Returns a Formated TimeStamp"""
    tz = pytz.timezone('UTC')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def dbts():
    """Returns a Unix TimeStamp"""
    tz = pytz.timezone('UTC')
    return int(datetime.now(tz).timestamp())

# /3.0/ Logging
def log(lvl:int, msg: str):
    """Standardized Log Entries"""
    if lvl == 4:
        logging.critical(f"{ts()} - [FATAL]: {msg}\n")
    elif lvl == 3:
        logging.error(f"{ts()} - [ERROR]: {msg}\n")
    elif lvl == 2:
        logging.warning(f"{ts()} - [WARN!]: {msg}\n")
    elif lvl == 1:
        logging.info(f"{ts()} - [INFO!]: {msg}\n")
    elif not lvl or lvl == 0:
        logging.debug(f"{ts()} - [DEBUG]: {msg}\n")

# /4.0/ Data & Init
def init():
    """Initializes the Dir & Database"""
    logging.basicConfig(filename=vars.log_file, level=logging.INFO, format='%(message)s')
    log(0, 'Ensuring Directories')
    for dir in vars.dirs:
        if dir.exists():
            log(0, f'{dir} Exists')
        else:
            log(2, f'{dir} Doesnt Exist, Creating...')
            dir.mkdir(exist_ok=True)
            log(1, f'{dir} Created Successfully')
    log(0, 'All Directories Present')
    log(0, 'Ensuring Files')
    for file in vars.files:
        if file.exists():
            log(0, f'{file} Exists')
        else:
            log(2, f'{file} Doesnt Exist, Creating...')
            file.touch()
            log(1, f'{file} Created Successfully')
    log(0, 'All Files Present')
    log(1, 'Checking Database')
    conn = sqlite3.connect(vars.db_file)
    cursor = conn.cursor()
    with open(vars.sql_file, 'r') as f:
        schema = f.read()
    log(0, 'Applying Database Schema')
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    log(1, 'Database Initialized Successfully')

def update_check():
    """Ensuring Database Update Schedule"""
    log(0, 'Checking if Database Update is Due')
    if vars.last_update is None:
        log(0, 'No Previous Update Today Found, Updating...')
        update_items()
    else:
        last_dt = datetime.strptime(vars.last_update, "%Y-%m-%d %H:%M:%S")
        now_dt = datetime.utcnow()
        if now_dt - last_dt >= timedelta(hours=24):
            log(0, 'Update is Due, Updating...')
            update_items()
        else:
            log(0, 'Database was Updated Recently, No Update Needed')

# /5.0/ Database
def update_items():
    """Updates The Items Database"""
    log(1, f'Updating Items Database')
    url = "https://api.torn.com/v2/torn/items?cat=All&sort=ASC"
    response = requests.get(url, headers=vars.headers)
    data = response.json()
    log(0, 'Fetched Updates, Connecting to Db')
    items = data.get('items', [])
    conn = sqlite3.connect(vars.db_file)
    cursor = conn.cursor()
    log(0, 'Database Connected')

    # /3.2.1/ Items Table
    log(0, f'Starting Data Formatting Loop')
    for item in items:
        type = item.get('type')
        item_id = item.get('id')
        log(0, f'Checking if {item_id} is Unused')
        if type.lower() == 'unused':
            log(0, f'{item_id} is an Unused ITEM_ID, Skipping...')
            continue
        log(0, f'{item_id} is a Used Item_ID')
        log(0, f'Extracting item: {item_id}s Static Data')
        name = item.get('name')
        description = item.get('description')
        tradable = int(bool(item.get('is_tradable')))
        findable = int(bool(item.get('is_found_in_city')))
        subtype = item.get('sub_type')
        requirement = item.get('requirement')
        effect = item.get('effect')
        log(0, f'Item {item_id} - {name} Static Data Extracted')
        log(1, f'Updating {item_id} - {name} in Database')
        cursor.execute("""
            INSERT OR REPLACE INTO items (
                item_id, name, description, type, tradable, findable, subtype, requirement, effect
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, name, description, type, tradable, findable, subtype, requirement, effect))
        log(0, 'Item {item_id} - {name} Updated Successfully')

        # /3.2.2/ Vendors Table
        log(0, f'Extracting {name}s Vendor Data')
        values = item.get('value')
        vendor = values.get('vendor')
        sell = values.get('sell_price')
        log(0, f'Ensuring {name} has a Vendor')
        if vendor:
            log(0, f'{name} has a Vendor, Extracting Location Data')
            country = vendor.get('country')
            name = vendor.get('name')
            if country.lower() == 'torn':
                location = vendor.get('name')
            else:
                location = country
            log(0, f'{name} Vendor Located at {location}')
            log(0, f'Gathering {name} Purchasing Price')
            buy = values.get('buy_price')
        else:
            log(0, f'{name} Doesnt have a Vendor')
            location = None
            buy = None
        log(0, f'Checking if {name} can be Re-Sold to Other Vendors')
        if not sell or sell == 0:
            log(0, f'{item} Cannot be Re-Sold')
            sell = None
        if not sell and not vendor:
            log(0, f'{item} Has no Vendor Data and Cannot be Re-Sold, Skipping')
            pass
        else:
            log(0, f'Updating {item} Vendor Data in Database')
            cursor.execute("""
                INSERT or REPLACE INTO vendors (item_id, location, buy, sell)
                VALUES (?, ?, ?, ?)
            """, (item_id, location, buy, sell))
            log(0, f'{item} Vendor Data Updated Successfully')

        # /3.2.3/ Circulation Table
        log(0, f'Extracting {name}s Circulation Data')
        circ = item.get('circulation')
        fair = values.get('market_price')
        log(0, f'{name}s Circulation Data Gathered')
        date = ts().split()[0]
        log(0, f'Updating {name} Circulation Data in Database')
        cursor.execute("""
            INSERT INTO circulation (item_id, circulation, date, fair_value)
            VALUES (?, ?, ?, ?)
        """, (item_id, circ, date, fair))
        log(0, f'{name} Circulation Data Updated Successfully')
    conn.commit()
    conn.close()
    log(1, f'Items Database Updated Successfully')
    vars.last_update = ts()

# /xx/ Expiremental
def market_list(id:int):
    """Fetches All Item Market Listings for an Item"""
    all_listings = []
    offset = 0
    calls = 0
    while calls < 100:
        url = f"https://api.torn.com/v2/market/{id}/itemmarket?limit=100&offset={offset}"
        response = requests.get(url, headers=vars.headers)
        calls += 1
        data = response.json()
        listings = data['itemmarket']['listings']
        all_listings.extend(listings)
        if len(listings) < 100:
            break
        else:
            offset += 100
    pricemap = {}
    for listing in all_listings:
        price = listing['price']
        amount = listing['amount']
        if price in pricemap:
            pricemap[price] += amount
        else:
            pricemap[price] = amount
    combined = [{'price': price, 'volume': amount} for price, amount in pricemap.items()]
    volume_cap = 0
    for listing in combined:
        price = listing['price']
        volume = listing['volume']
        volume_cap += volume
        cost = price * volume
        listing['cost'] = cost
    print(f"Calls Made: {calls}, {ts()}")
    print(f"Total Volume: {volume_cap}")
    print(json.dumps(combined, indent=4))

def buyer(id:int):
    url = "https://api.torn.com/v2/market/206/itemmarket?limit=100&offset=0"
    response = requests.get(url, headers=vars.headers)
    data = response.json()
    listings = data['itemmarket']['listings']
    best = listings[0]
    print(f"Best Listing: {best}")
