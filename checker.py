import sqlite3
import requests
import time

DB_PATH = "keys.db"
API_URL = "https://blockstream.info/api/address/{}"

def get_balance(address):
    """Return BTC balance for a given P2WPKH address."""
    try:
        url = API_URL.format(address)
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        funded = data["chain_stats"]["funded_txo_sum"]
        spent = data["chain_stats"]["spent_txo_sum"]
        sats = funded - spent
        btc = sats / 100_000_000
        return btc
    except Exception as e:
        print(f"Error fetching balance for {address}: {e}")
        return None

def update_balances():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, p2wpkh, balance
        FROM keys
    """)
    rows = c.fetchall()
    for row in rows:
        row_id, address, balance = row
        if balance is not None and balance != "NONE":
            print(f"Skipping {address} (already computed: {balance})")
            continue
        print(f"Checking {address}...")
        btc_balance = get_balance(address)
        if btc_balance is not None:
            c.execute("UPDATE keys SET balance = ? WHERE id = ?", (str(btc_balance), row_id))
            conn.commit()
            print(f" → Balance: {btc_balance} BTC")
        else:
            print(" → Failed to update balance")
        time.sleep(0.25)
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    update_balances()
