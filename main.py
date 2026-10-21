# ============================================================
# Group Manager Bot (Super Safe Direct Register Mode)
# AUTHOR : MISTER STARK 
# ============================================================

from pyrogram import Client, filters
import logging

# 🔐 Import security
from security import verify_integrity, get_runtime_key
from config import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(level=logging.INFO)

print("🔄 Running security check...")
verify_integrity()
RUNTIME_KEY = get_runtime_key()

app = Client(
    "group_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================================
# 🔥 DEBUG COMMAND (Priority Group -1)
# ==========================================================
@app.on_message(filters.command("stark"), group=-1)
async def stark_debug_cmd(client, message):
    await message.reply_text("🦅 **Mister Stark! Bot core is active and ready.**")

# ==========================================================
# 🟢 DIRECT REGISTER: Naye modules ko sabse pehle register kiya
# ==========================================================
print("📦 Registering New Modules...")

try:
    from handlers.warns import register_warns_handler
    register_warns_handler(app)
    print("✨ Warns Module: LINKED!")
except Exception as e:
    print(f"❌ Warns Link Error: {e}")

try:
    from handlers.captcha import register_captcha_handler
    register_captcha_handler(app)
    print("✨ Captcha Module: LINKED!")
except Exception as e:
    print(f"❌ Captcha Link Error: {e}")

try:
    from handlers.forward import register_forward_handler
    register_forward_handler(app)
    print("✨ Forward Module: LINKED!")
except Exception as e:
    print(f"❌ Forward Link Error: {e}")

try:
    from handlers.fancy_text import register_fancy_text_handler
    register_fancy_text_handler(app)
    print("✨ Fancy Text Module: LINKED!")
except Exception as e:
    print(f"❌ Fancy Text Link Error: {e}")

try:
    from handlers.anti_sticker import register_anti_sticker_handler
    register_anti_sticker_handler(app)
    print("✨ Anti-Sticker Module: LINKED!")
except Exception as e:
    print(f"❌ Anti-Sticker Link Error: {e}")

try:
    from handlers.anti_link import register_anti_link_handler
    register_anti_link_handler(app)
    print("✨ Anti-Link Module: DIRECT LINKED!")
except Exception as e:
    print(f"❌ Anti-Link Direct Link Error: {e}")

try:
    from handlers.disable import register_disable_handler
    register_disable_handler(app)
    print("✨ Disable Module: LINKED!")
except Exception as e:
    print(f"❌ Disable Link Error: {e}")

try:
    from handlers.autolock import register_autolock_handler
    register_autolock_handler(app)
    print("✨ Auto-Lock Module: LINKED!")
except Exception as e:
    print(f"❌ Auto-Lock Link Error: {e}")

try:
    from handlers.approve import register_approve_handler
    register_approve_handler(app)
    print("✨ Approve Module: LINKED!")
except Exception as e:
    print(f"❌ Approve Link Error: {e}")

try:
    from handlers.antiflood import register_antiflood_handler
    register_antiflood_handler(app)
    print("✨ Anti-Flood Module: LINKED!")
except Exception as e:
    print(f"❌ Anti-Flood Link Error: {e}")

try:
    from handlers.economy import register_economy_handler
    register_economy_handler(app)
    print("✨ Economy Module: LINKED!")
except Exception as e:
    print(f"❌ Economy Link Error: {e}")

try:
    from handlers.shop import register_shop_handler
    register_shop_handler(app)
    print("✨ Shop Module: LINKED!")
except Exception as e:
    print(f"❌ Shop Link Error: {e}")

try:
    from handlers.bank import register_bank_handler
    register_bank_handler(app)
    print("✨ Bank Module: LINKED!")
except Exception as e:
    print(f"❌ Bank Link Error: {e}")

try:
    from handlers.fun import register_fun_handler
    register_fun_handler(app)
    print("✨ Fun Module: LINKED!")
except Exception as e:
    print(f"❌ Fun Link Error: {e}")

try:
    from handlers.leaderboard import register_leaderboard_handler
    register_leaderboard_handler(app)
    print("✨ Leaderboard Module: LINKED!")
except Exception as e:
    print(f"❌ Leaderboard Link Error: {e}")

try:
    from handlers.owner_eco import register_owner_eco_handler
    register_owner_eco_handler(app)
    print("✨ Owner-Economy Module: LINKED!")
except Exception as e:
    print(f"❌ Owner-Economy Link Error: {e}")

try:
    from handlers.groupinfo import register_groupinfo_handler
    register_groupinfo_handler(app)
    print("✨ Group Identity Module: LINKED!")
except Exception as e:
    print(f"❌ Group Identity Link Error: {e}")

try:
    from handlers.couple import register_couple_handler
    register_couple_handler(app)
    print("✨ Couple of the Day Module: LINKED!")
except Exception as e:
    print(f"❌ Couple of the Day Link Error: {e}")


# ==========================================================
# 🔴 OLD REGISTER: Purane handlers ko iske baad load kiya
# ==========================================================
print("📦 Registering Core Modules...")
try:
    from handlers import register_all_handlers
    register_all_handlers(app)
    print("✅ All Core Handlers Registered Successfully!")
except Exception as e:
    print(f"⚠️ Core Registration Interrupted: {e}")

print("🚀 Bot is starting securely...")
app.run()
