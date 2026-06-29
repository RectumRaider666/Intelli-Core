import os
import sqlite3
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
import bech32

def random_input_string(conn, length=32):
    c = conn.cursor()
    while True:
        s = os.urandom(length).hex()
        c.execute("SELECT 1 FROM keys WHERE input_string = ? LIMIT 1", (s,))
        if c.fetchone() is None:
            return s

def derive_private_key(input_string):
    data = input_string.encode('utf-8')
    digest = hashlib.sha256(data).digest()
    key_int = int.from_bytes(digest, 'big') % SECP256k1.order
    return key_int.to_bytes(32, 'big').hex()

def derive_public_key(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    return (prefix + x.to_bytes(32, 'big')).hex()

def pubkey_to_p2pkh(pubkey_hex):
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha = hashlib.sha256(pubkey_bytes).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    versioned = b'\x00' + ripe
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58.b58encode(versioned + checksum).decode()

def pubkey_to_p2wpkh(pubkey_hex):
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha = hashlib.sha256(pubkey_bytes).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    converted = bech32.convertbits(ripe, 8, 5)
    return bech32.bech32_encode("bc", [0] + converted)

def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_string TEXT UNIQUE NOT NULL,
            private_key TEXT UNIQUE NOT NULL,
            public_key TEXT UNIQUE NOT NULL,
            p2pkh TEXT UNIQUE NOT NULL,
            p2wpkh TEXT UNIQUE NOT NULL,
            balance TEXT DEFAULT NONE
        )
    """)
    conn.commit()
    return conn

def insert_record(conn, input_string, private_key, public_key, p2pkh, p2wpkh):
    c = conn.cursor()
    c.execute("INSERT INTO keys (input_string, private_key, public_key, p2pkh, p2wpkh) VALUES (?, ?, ?, ?, ?)", (input_string, private_key, public_key, p2pkh, p2wpkh))
    conn.commit()

def runner():
    while True:
        input_str = random_input_string(conn)
        priv = derive_private_key(input_str)
        pub = derive_public_key(priv)
        addr1 = pubkey_to_p2pkh(pub)
        addr2 = pubkey_to_p2wpkh(pub)
        insert_record(conn, input_str, priv, pub, addr1, addr2)
        print("Input String:", input_str)
        print("Private Key:", priv)
        print("Public Key:", pub)
        print("P2PKH Address:", addr1)
        print("P2WPKH Address:", addr2)


if __name__ == "__main__":
    conn = init_db()
    runner()
