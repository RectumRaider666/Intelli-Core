from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists

# 1) Create a new mnemonic (BIP39)
mn = Mnemonic('english')
words = mn.generate()
print("MNEMONIC:", words)

# 2) Create a fresh native SegWit wallet (testnet)
name = "demo_segwit_testnet"
if wallet_delete_if_exists(name):
    pass

w = Wallet.create(name, keys=words, network='testnet', witness_type='segwit')

# 3) Derive a receive address (key)
k1 = w.get_key()
print("Receive address:", k1.address)

# 4) Derive another receive address
k2 = w.get_key()
print("Next address:", k2.address)

# 5) Get a change address (commonly: change=True)
kc = w.get_key(change=True)
print("Change address:", kc.address)