# ============================================================
# Economy System — Shared Item Data (Weapons / Collection / Luxury)
# ============================================================

CURRENCY = "$"

WEAPONS = {
    "Stick": 500, "Wood Log": 1000, "Stone": 2000, "Slingshot": 3000,
    "Baseball Bat": 4000, "Hammer": 4200, "Axe": 4800, "Bow & Arrow": 5000,
    "Crossbow": 5200, "Dagger": 5500, "Sword": 6000, "Katana": 6500,
    "Pistol": 6500, "Revolver": 7000, "Shotgun": 7500, "Assault Rifle": 10000,
    "Sniper Rifle": 12000, "Machine Gun": 15000, "Rocket Launcher": 20000,
    "Armored Vehicle": 250000, "Tank": 1000000, "Missile": 150000,
}

COLLECTION = {
    "Rose": 200, "Chocolate": 500, "Teddy Bear": 1000, "Cat": 2500,
    "Dog": 5000, "Love Letter": 5500, "Music Box": 6000, "Rare Coin": 6500,
    "Ancient Scroll": 7000, "Crystal Ball": 9000, "Golden Crown": 9500,
    "Pirate Treasure Chest": 10000, "Magic Crystal": 12000,
    "Phoenix Feather": 13000, "Dragon Egg": 14000, "Infinity Cube": 20000,
}

LUXURY = {
    "Silver Ring": 700, "Gold Ring": 1200, "Diamond Ring": 5000,
    "Gold Chain": 6000, "Rolex Watch": 10000, "Luxury Suit": 15000,
    "Gucci Bag": 20000, "Lamborghini": 350000, "Ferrari": 450000,
    "Rolls-Royce": 600000, "McLaren": 750000, "Private Yacht": 2000000,
    "Bugatti Chiron": 3500000, "Formula 1 Car": 15000000,
    "American Express Card": 25000000, "Private Jet": 60000000,
    "Mega Mansion": 100000000, "Private Island": 500000000,
}

CATEGORIES = {
    "weapons": WEAPONS,
    "assets": COLLECTION,
    "luxury": LUXURY,
}

ITEM_EMOJIS = {
    # weapons
    "Stick": "🥢", "Wood Log": "🪵", "Stone": "🪨", "Slingshot": "🏹",
    "Baseball Bat": "🏏", "Hammer": "🔨", "Axe": "🪓", "Bow & Arrow": "🏹",
    "Crossbow": "🎯", "Dagger": "🗡", "Sword": "⚔️", "Katana": "🗡️",
    "Pistol": "🔫", "Revolver": "🔫", "Shotgun": "🔫", "Assault Rifle": "🔫",
    "Sniper Rifle": "🎯", "Machine Gun": "🔫", "Rocket Launcher": "🚀",
    "Armored Vehicle": "🚓", "Tank": "🛡️", "Missile": "☄️",
    # collection
    "Rose": "🌹", "Chocolate": "🍫", "Teddy Bear": "🧸", "Cat": "🐱",
    "Dog": "🐶", "Love Letter": "💌", "Music Box": "🎵", "Rare Coin": "🪙",
    "Ancient Scroll": "📜", "Crystal Ball": "🔮", "Golden Crown": "👑",
    "Pirate Treasure Chest": "🗝️", "Magic Crystal": "💠",
    "Phoenix Feather": "🪶", "Dragon Egg": "🥚", "Infinity Cube": "🧊",
    # luxury
    "Silver Ring": "💍", "Gold Ring": "💍", "Diamond Ring": "💍",
    "Gold Chain": "📿", "Rolex Watch": "⌚", "Luxury Suit": "🤵",
    "Gucci Bag": "👜", "Lamborghini": "🏎️", "Ferrari": "🏎️",
    "Rolls-Royce": "🚘", "McLaren": "🏎️", "Private Yacht": "🛥️",
    "Bugatti Chiron": "🏎️", "Formula 1 Car": "🏁",
    "American Express Card": "💳", "Private Jet": "🛩️",
    "Mega Mansion": "🏰", "Private Island": "🏝️",
}


def item_emoji(name: str) -> str:
    return ITEM_EMOJIS.get(name, "🎁")


def item_label(name: str) -> str:
    return f"{item_emoji(name)} {name}"

WEAPON_EXPIRY_SECONDS = 24 * 3600  # weapons expire after 24h
GIFT_EXTRA_COST = 200
SELL_DISCOUNT_PERCENT = 10  # sell back at 10% below original price

# graduated loot-bonus % per weapon, lowest → highest tier (2% up to 100%)
_WEAPON_LOOT_STEPS = [2, 5, 10, 14, 18, 22, 26, 30, 34, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 94, 100]
_WEAPON_NAMES_ORDERED = sorted(WEAPONS.keys(), key=lambda n: WEAPONS[n])
WEAPON_LOOT_BONUS = dict(zip(_WEAPON_NAMES_ORDERED, _WEAPON_LOOT_STEPS))


def loot_bonus_percent(weapon_name: str) -> int:
    """Extra % loot bonus on a kill, based on weapon tier (2% → 100%)."""
    if not weapon_name or weapon_name not in WEAPON_LOOT_BONUS:
        return 0
    return WEAPON_LOOT_BONUS[weapon_name]


def sell_price(original_price: int) -> int:
    return int(original_price * (100 - SELL_DISCOUNT_PERCENT) / 100)


def item_price(category: str, name: str) -> int:
    return CATEGORIES.get(category, {}).get(name, 0)


def fmt_amount(n: int) -> str:
    return f"{CURRENCY}{n:,}"
