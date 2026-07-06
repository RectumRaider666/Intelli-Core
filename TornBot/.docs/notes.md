# Torn RPG Notes

---

## [1] Descriptions & Resources

Notes on building automations, extensions, and scripts for Torn RPG

### [1.1] API Notes

- 100 API Calls per Minutes
  - Api Error Codes:
  - 0 => Unknown error : Unhandled error, should not occur.
  - 1 => Key is empty : Private key is empty in current request.
  - 2 => Incorrect Key : Private key is wrong/incorrect format.
  - 3 => Wrong type : Requesting an incorrect basic type.
  - 4 => Wrong fields : Requesting incorrect selection fields.
  - 5 => Too many requests : Requests are blocked for a small period of time because of too many requests per user (max 100 per minute).
  - 6 => Incorrect ID : Wrong ID value.
  - 7 => Incorrect ID-entity relation : A requested selection is private (For example, personal data of another user / faction).
  - 8 => IP block : Current IP is banned for a small period of time because of abuse.
  - 9 => API disabled : Api system is currently disabled.
  - 10 => Key owner is in federal jail : Current key can't be used because owner is in federal jail.
  - 11 => Key change error : You can only change your API key once every 60 seconds.
  - 12 => Key read error : Error reading key from Database.
  - 13 => The key is temporarily disabled due to owner inactivity : The key owner hasn't been online for more than 7 days.
  - 14 => Daily read limit reached : Too many records have been pulled today by this user from our cloud services.
  - 15 => Temporary error : An error code specifically for testing purposes that has no dedicated meaning.
  - 16 => Access level of this key is not high enough : A selection is being called of which this key does not have permission to access.
  - 17 => Backend error occurred, please try again.
  - 18 => API key has been paused by the owner.
  - 19 => Must be migrated to crimes 2.0.
  - 20 => Race not yet finished.
  - 21 => Incorrect category : Wrong cat value.
  - 22 => This selection is only available in API v1.
  - 23 => This selection is only available in API v2.
  - 24 => Closed temporarily.
  - 25 => Invalid stat requested.
  - 26 => Only category or stats can be requested.
  - 27 => Must be migrated to organized crimes 2.0.
  - 28 => Incorrect log ID.
  - 29 => Category selection is not available for interaction logs.

---

### [1.2] Sites & Api

- Main:
  - [Torn](https://www.torn.com/) - The Main Website
  - [Torn API v1](https://www.api.torn.com/) - The Basic API
  - [Torn API v2](https://www.api.torn.com/v2/) - The Full API

- 3rd Party:
  - [Yata](https://yata.yt/) - Site for Item Market Data and Prices
  - [Torn Stats](https://www.tornstats.com/) - Site for Player and Clan Statistics
  - [Torn Exchange](https://tornexchange.com/) - Site for Listing Buying and Selling Prices on Items
  - [Tornsy](https://tornsy.com/) - Site for Torn Stock Market Data and Line Charts
  - [Torn Report](https://www.torn.report) - Site for Log Analysis and Interpretation

- Extensions (FireFox):
  - [Torn Tools](https://addons.mozilla.org/en-US/firefox/addon/torn-tools/) - Extension for showing Player Status

---
### [1.3] Accounts

---

### [1.4] Torn Links

```ini
[Static Links]
    home = https://www.torn.com/index.php
    items = https://www.torn.com/items.php
    city = https://www.torn.com/city.php
    faction = https://www.torn.com/factions.php
    job = https://www.torn.com/jobs.php
    gym = https://www.torn.com/gyms.php
    properties = https://www.torn.com/properties.php
    education = https://www.torn.com/education.php
    crimes = https://www.torn.com/page.php?sid=crimes#/
    missions = https://www.torn.com/loader.php?sid=missions
    newspaper = https://www.torn.com/newspaper.php
    jail = https://www.torn.com/jailview.php
    hospital = https://www.torn.com/hospitalview.php
    casino = https://www.torn.com/casino.php

[Dynamic Links]
    profiles = https://www.torn.com/profiles.php?XID='{ID}'
    item-market = https://www.torn.com/page.php?sid=ItemMarket#/market/view=category&categoryName='{MARKET_NAME}'
    icons = https://www.torn.com/images/items/'{ITEM_ID}'/'{SIZE}'.png ## Large/Medium/Small
```

---

### [1.5] Item IDS Notes

- Undefined IDS:
  - 208
  - 315 - 325
  - 590 - 592
  - 891
  - Total : 16

- Missing IDS:
  - 168
  - 589
  - 999 - 1000
  - 1160 - 1163
  - 1218
  - 1229
  - 1432 - 1447
  - 1508
  - Total : 27

- Item Categories:
  - Weapon : 184
  - Armor : 74
  - Candy : 19
  - Other : 202
  - Special : 39
  - Material : 59
  - Clothing : 230
  - Jewelry : 15
  - Tool : 70
  - Medical : 19
  - Collectible : 280
  - Car : 50
  - Flower : 20
  - Booster : 20
  - Alcohol : 15
  - Plushie : 13
  - Drug : 11
  - Supply Pack : 39
  - Enhancer : 33
  - Artifact : 21
  - Energy Drink : 9
  - Book : 44
  - Unused : 43
  - Total Items : 1466

## [2] Development Notes

### [2.1] Making API Calls

```sh
curl -X 'GET' 'https://api.torn.com/{API_URL}' -H 'accept: application/json' -H 'Authorization: ApiKey {API_KEY}'
```

To Gather A JSON Dictionary of All Items and IDS

```sh
curl -X 'GET' 'https://api.torn.com/v2/torn/items?cat=All&sort=ASC' -H 'accept: application/json' -H 'Authorization: ApiKey htp4MnHz3O0AeH4P' | jq --indent 4 . > data/items.json
```
