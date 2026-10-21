# ============================================================
# Economy Game System — Core (balance, profile, earnings)
# Author: Mr. Stark
# ============================================================
import time
import random
from pyrogram import enums, filters, Client
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from handlers.eco_data import fmt_amount, loot_bonus_percent, sell_price, WEAPON_EXPIRY_SECONDS, item_emoji
import db

DAILY_COOLDOWN = 24 * 3600
MINE_COOLDOWN = 6 * 3600
REVIVE_BONUS = 50
REVIVE_SAFE_THRESHOLD = 100
PROTECT_COST_PER_DAY = 150
PROTECT_MAX_DAYS = 3
PROTECT_MIN_BALANCE = 700


def now_ts() -> int:
    return int(time.time())


def is_protected(user: dict) -> bool:
    return user.get("protection_until", 0) > now_ts()


async def get_target_user(client, message: Message):
    """Return the user targeted by a reply, or None."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


def _active_inventory(data: dict) -> list:
    return [i for i in data.get("inventory", []) if i.get("category") != "weapons" or i.get("expires_at", 0) > now_ts()]


async def build_wallet_view(user_id: int, name: str):
    data = await db.get_eco_user(user_id)
    protection_left = 0
    if is_protected(data):
        protection_left = data["protection_until"] - now_ts()
    protection_txt = f"{protection_left // 3600}h {(protection_left % 3600) // 60}m" if protection_left > 0 else "ɴᴏɴᴇ"
    status_txt = "🟢 ᴀʟɪᴠᴇ" if data["status"] == "alive" else "☠️ ᴅᴇᴀᴅ"
    inventory = _active_inventory(data)

    text = (
        f"🪪 <b>{name}'ꜱ ᴡᴀʟʟᴇᴛ</b>\n\n"
        f"➻ ᴜꜱᴇʀ ID: <code>{user_id}</code>\n"
        f"➻ ʙᴀʟᴀɴᴄᴇ: <code>{fmt_amount(data['balance'])}</code>\n"
        f"➻ ꜱᴛᴀᴛᴜꜱ: {status_txt}\n"
        f"➻ ᴋɪʟʟꜱ: <code>{data['kills']}</code> · ʀᴏʙʙᴇᴅ: <code>{data['robbed']}</code>\n"
        f"➻ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ: <code>{protection_txt}</code>\n"
        f"➻ ᴍᴀʀɪᴛᴀʟ ꜱᴛᴀᴛᴜꜱ: <code>{data.get('marital_status', 'single')}</code>"
    )

    rows = []
    for i in range(0, len(inventory), 2):
        pair = inventory[i:i + 2]
        rows.append([
            InlineKeyboardButton(f"{item_emoji(item['name'])} {item['name']}", callback_data=f"ecoitem|{user_id}|{inventory.index(item)}", style=ButtonStyle.PRIMARY)
            for item in pair
        ])
    rows.append([InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data="eco_close", style=ButtonStyle.DANGER)])

    return text, InlineKeyboardMarkup(rows)


def register_economy_handler(app: Client):

    # ==========================================================
    # /bal, /balance
    # ==========================================================
    @app.on_message(filters.command(["bal", "balance"]))
    async def balance_cmd(client, message: Message):
        target = await get_target_user(client, message)
        if message.chat.type != enums.ChatType.PRIVATE:
            await db.add_eco_group_member(message.chat.id, message.from_user.id)

        if target:
            data = await db.get_eco_user(target.id)
            status_txt = "🟢 ᴀʟɪᴠᴇ" if data["status"] == "alive" else "☠️ ᴅᴇᴀᴅ"
            return await message.reply_text(
                f"💰 <b>{target.mention}'ꜱ ʙᴀʟᴀɴᴄᴇ</b>\n\n"
                f"➻ ʙᴀʟᴀɴᴄᴇ: <code>{fmt_amount(data['balance'])}</code>\n"
                f"➻ ꜱᴛᴀᴛᴜꜱ: {status_txt}\n"
                f"➻ ᴋɪʟʟꜱ: <code>{data['kills']}</code>\n"
                f"➻ ʀᴏʙʙᴇᴅ: <code>{data['robbed']}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        text, buttons = await build_wallet_view(message.from_user.id, message.from_user.mention)
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)

    # ==========================================================
    # /profile
    # ==========================================================
    @app.on_message(filters.command("profile"))
    async def profile_cmd(client, message: Message):
        text, buttons = await build_wallet_view(message.from_user.id, message.from_user.mention)
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)

    # ── view item detail (with sell option) ──
    @app.on_callback_query(filters.regex(r"^ecoitem\|(\d+)\|(\d+)$"))
    async def eco_item_view_cb(client, callback_query: CallbackQuery):
        owner_id, idx = int(callback_query.matches[0].group(1)), int(callback_query.matches[0].group(2))
        if callback_query.from_user.id != owner_id:
            return await callback_query.answer("❌ ᴛʜɪꜱ ɪꜱɴ'ᴛ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ!", show_alert=True)

        data = await db.get_eco_user(owner_id)
        inventory = _active_inventory(data)
        if idx >= len(inventory):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        item = inventory[idx]

        validity = "♾ ᴘᴇʀᴍᴀɴᴇɴᴛ"
        if item.get("category") == "weapons":
            remaining = item.get("expires_at", 0) - now_ts()
            validity = f"{max(remaining, 0) // 3600}h {(max(remaining, 0) % 3600) // 60}m ʟᴇꜰᴛ"

        sell_val = sell_price(item["price"])
        text = (
            f"{item_emoji(item['name'])} <b>{item['name']}</b>\n\n"
            f"➻ ᴄᴀᴛᴇɢᴏʀʏ: <code>{item['category']}</code>\n"
            f"➻ ᴠᴀʟᴜᴇ ᴘᴀɪᴅ: <code>{fmt_amount(item['price'])}</code>\n"
            f"➻ ᴠᴀʟɪᴅɪᴛʏ: <code>{validity}</code>\n"
            f"➻ ꜱᴇʟʟ ᴠᴀʟᴜᴇ: <code>{fmt_amount(sell_val)}</code> (-10%)"
        )
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"💰 ꜱᴇʟʟ ({fmt_amount(sell_val)})", callback_data=f"ecoitem_sell|{owner_id}|{idx}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"ecoitem_back|{owner_id}", style=ButtonStyle.DANGER),
        ]])
        await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^ecoitem_sell\|(\d+)\|(\d+)$"))
    async def eco_item_sell_cb(client, callback_query: CallbackQuery):
        owner_id, idx = int(callback_query.matches[0].group(1)), int(callback_query.matches[0].group(2))
        if callback_query.from_user.id != owner_id:
            return await callback_query.answer("❌ ᴛʜɪꜱ ɪꜱɴ'ᴛ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ!", show_alert=True)

        data = await db.get_eco_user(owner_id)
        inventory = _active_inventory(data)
        if idx >= len(inventory):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        item = inventory[idx]
        sell_val = sell_price(item["price"])

        remaining_inventory = [i for i in data.get("inventory", []) if i is not item]
        await db.set_inventory(owner_id, remaining_inventory)
        await db.update_balance(owner_id, sell_val)

        await callback_query.answer(f"✅ ꜱᴏʟᴅ {item['name']} ꜰᴏʀ {fmt_amount(sell_val)}!", show_alert=True)
        text, buttons = await build_wallet_view(owner_id, callback_query.from_user.mention)
        await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)

    @app.on_callback_query(filters.regex(r"^ecoitem_back\|(\d+)$"))
    async def eco_item_back_cb(client, callback_query: CallbackQuery):
        owner_id = int(callback_query.matches[0].group(1))
        if callback_query.from_user.id != owner_id:
            return await callback_query.answer("❌ ᴛʜɪꜱ ɪꜱɴ'ᴛ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ!", show_alert=True)
        text, buttons = await build_wallet_view(owner_id, callback_query.from_user.mention)
        await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^eco_close$"))
    async def eco_close_cb(client, callback_query: CallbackQuery):
        await callback_query.message.delete()
        await callback_query.answer()

    # ==========================================================
    # /rob <amount>
    # ==========================================================
    @app.on_message(filters.command("rob"))
    async def rob_cmd(client, message: Message):
        target = await get_target_user(client, message)
        if not target:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ʀᴏʙ ᴛʜᴇᴍ.", parse_mode=enums.ParseMode.HTML)
        if target.id == message.from_user.id:
            return await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴ'ᴛ ʀᴏʙ ʏᴏᴜʀꜱᴇʟꜰ.", parse_mode=enums.ParseMode.HTML)
        if target.id == OWNER_ID:
            return await message.reply_text("👑 ᴏᴡɴᴇʀ ᴄᴀɴ'ᴛ ʙᴇ ʀᴏʙʙᴇᴅ.", parse_mode=enums.ParseMode.HTML)

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/rob &lt;ᴀᴍᴏᴜɴᴛ&gt;</code> (ʀᴇᴘʟʏ)", parse_mode=enums.ParseMode.HTML)
        amount = int(parts[1].strip())

        target_data = await db.get_eco_user(target.id)

        if target_data["status"] == "dead":
            return await message.reply_text("☠️ ᴅᴇᴀᴅ ᴜꜱᴇʀꜱ ᴄᴀɴ'ᴛ ʙᴇ ʀᴏʙʙᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if is_protected(target_data):
            return await message.reply_text(f"🛡 {target.mention} ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if target_data["balance"] < amount:
            return await message.reply_text("⚠️ ᴛᴀʀɢᴇᴛ ᴅᴏᴇꜱɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ.", parse_mode=enums.ParseMode.HTML)

        await db.update_balance(target.id, -amount)
        await db.update_balance(message.from_user.id, amount)
        await db.increment_robbed(message.from_user.id)

        await message.reply_text(
            f"💸 {message.from_user.mention} ʀᴏʙʙᴇᴅ {fmt_amount(amount)} ꜰʀᴏᴍ {target.mention}!",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /kill, /death
    # ==========================================================
    @app.on_message(filters.command(["kill", "death"]))
    async def kill_cmd(client, message: Message):
        target = await get_target_user(client, message)
        if not target:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴋɪʟʟ ᴛʜᴇᴍ.", parse_mode=enums.ParseMode.HTML)
        if target.id == message.from_user.id:
            return await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴋɪʟʟ ʏᴏᴜʀꜱᴇʟꜰ.", parse_mode=enums.ParseMode.HTML)
        if target.id == OWNER_ID:
            return await message.reply_text("👑 ᴏᴡɴᴇʀ ᴄᴀɴ'ᴛ ʙᴇ ᴋɪʟʟᴇᴅ.", parse_mode=enums.ParseMode.HTML)

        target_data = await db.get_eco_user(target.id)

        if target_data["status"] == "dead":
            return await message.reply_text(f"☠️ {target.mention} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴅᴇᴀᴅ.", parse_mode=enums.ParseMode.HTML)
        if is_protected(target_data):
            return await message.reply_text(f"🛡 {target.mention} ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if target_data.get("just_revived") and target_data["balance"] < REVIVE_SAFE_THRESHOLD:
            return await message.reply_text(
                f"🛡 {target.mention} ᴡᴀꜱ ʀᴇᴄᴇɴᴛʟʏ ʀᴇᴠɪᴠᴇᴅ ᴀɴᴅ ɪꜱ ꜱᴀꜰᴇ ᴜɴᴛɪʟ ᴛʜᴇʏ ʀᴇᴀᴄʜ {fmt_amount(REVIVE_SAFE_THRESHOLD)}.",
                parse_mode=enums.ParseMode.HTML
            )

        loot = target_data["balance"]
        bonus = random.randint(20, 200)

        # transfer collection/luxury loot items (weapons excluded, they expire)
        killer_data = await db.get_eco_user(message.from_user.id)
        killer_weapon = None
        for item in killer_data.get("inventory", []):
            if item.get("category") == "weapons" and item.get("expires_at", 0) > now_ts():
                killer_weapon = item["name"]
                break
        loot_pct = loot_bonus_percent(killer_weapon)
        loot_extra = int(loot * loot_pct / 100)

        transferable = [i for i in target_data.get("inventory", []) if i.get("category") in ("assets", "luxury")]
        remaining = [i for i in target_data.get("inventory", []) if i.get("category") not in ("assets", "luxury")]

        await db.set_inventory(target.id, remaining)
        for item in transferable:
            await db.add_inventory_item(message.from_user.id, item)

        await db.update_balance(target.id, -loot)
        await db.update_balance(message.from_user.id, loot + bonus + loot_extra)
        await db.increment_kills(message.from_user.id)
        await db.set_eco_status(target.id, "dead")

        extra_txt = f" (+{loot_pct}% ᴡᴇᴀᴘᴏɴ ʙᴏɴᴜꜱ)" if loot_pct else ""
        loot_txt = f"ᴋɪʟʟᴇᴅ {target.mention}! ʟᴏᴏᴛᴇᴅ {fmt_amount(loot + loot_extra)}{extra_txt} + {fmt_amount(bonus)} ᴋɪʟʟ ʙᴏɴᴜꜱ"
        if transferable:
            loot_txt += f"\n🎁 ʟᴏᴏᴛᴇᴅ ɪᴛᴇᴍꜱ: {', '.join(i['name'] for i in transferable)}"

        await message.reply_text(
            f"🔪 {loot_txt}\n\n☠️ {target.mention} ɪꜱ ɴᴏᴡ <b>ᴅᴇᴀᴅ</b>. ᴜꜱᴇ /revive ᴛᴏ ᴄᴏᴍᴇ ʙᴀᴄᴋ.",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /revive
    # ==========================================================
    @app.on_message(filters.command("revive"))
    async def revive_cmd(client, message: Message):
        user_id = message.from_user.id
        data = await db.get_eco_user(user_id)
        if data["status"] != "dead":
            return await message.reply_text("✅ ʏᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ᴀʟɪᴠᴇ.", parse_mode=enums.ParseMode.HTML)

        await db.set_eco_status(user_id, "alive")
        await db.update_balance(user_id, REVIVE_BONUS)
        await db.set_just_revived(user_id, True)

        await message.reply_text(
            f"✨ {message.from_user.mention} ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴠɪᴠᴇᴅ! +{fmt_amount(REVIVE_BONUS)} ʙᴏɴᴜꜱ.\n"
            f"🛡 ꜱᴀꜰᴇ ꜰʀᴏᴍ ᴋɪʟʟꜱ ᴜɴᴛɪʟ ʙᴀʟᴀɴᴄᴇ ʀᴇᴀᴄʜᴇꜱ {fmt_amount(REVIVE_SAFE_THRESHOLD)}.",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /daily
    # ==========================================================
    @app.on_message(filters.command("daily"))
    async def daily_cmd(client, message: Message):
        user_id = message.from_user.id
        data = await db.get_eco_user(user_id)
        last = data.get("last_daily", 0)
        elapsed = now_ts() - last
        if elapsed < DAILY_COOLDOWN:
            remaining = DAILY_COOLDOWN - elapsed
            return await message.reply_text(
                f"⏳ ᴄᴏᴍᴇ ʙᴀᴄᴋ ɪɴ <code>{remaining // 3600}h {(remaining % 3600) // 60}m</code>.",
                parse_mode=enums.ParseMode.HTML
            )
        bonus = random.randint(20, 200)
        await db.update_balance(user_id, bonus)
        await db.set_last_daily(user_id, now_ts())
        await message.reply_text(f"🎁 ᴅᴀɪʟʏ ʙᴏɴᴜꜱ: <code>{fmt_amount(bonus)}</code>", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /mine
    # ==========================================================
    @app.on_message(filters.command("mine"))
    async def mine_cmd(client, message: Message):
        user_id = message.from_user.id
        data = await db.get_eco_user(user_id)
        last = data.get("last_mine", 0)
        elapsed = now_ts() - last
        if elapsed < MINE_COOLDOWN:
            remaining = MINE_COOLDOWN - elapsed
            return await message.reply_text(
                f"⏳ ᴍɪɴᴇ ᴀɢᴀɪɴ ɪɴ <code>{remaining // 3600}h {(remaining % 3600) // 60}m</code>.",
                parse_mode=enums.ParseMode.HTML
            )
        bonus = random.randint(20, 200)
        await db.update_balance(user_id, bonus)
        await db.set_last_mine(user_id, now_ts())
        await message.reply_text(f"⛏ ʏᴏᴜ ᴍɪɴᴇᴅ: <code>{fmt_amount(bonus)}</code>", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /protect, /protection <days>
    # ==========================================================
    @app.on_message(filters.command(["protect", "protection"]))
    async def protect_cmd(client, message: Message):
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/protect &lt;ᴅᴀʏꜱ&gt;</code> (ᴍᴀx {PROTECT_MAX_DAYS})\n"
                f"ᴄᴏꜱᴛ: <code>{fmt_amount(PROTECT_COST_PER_DAY)}</code>/ᴅᴀʏ · ʀᴇǫᴜɪʀᴇꜱ ᴍɪɴ ʙᴀʟᴀɴᴄᴇ {fmt_amount(PROTECT_MIN_BALANCE)}",
                parse_mode=enums.ParseMode.HTML
            )
        days = int(parts[1].strip())
        if days < 1 or days > PROTECT_MAX_DAYS:
            return await message.reply_text(f"⚠️ ᴅᴀʏꜱ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 1 ᴀɴᴅ {PROTECT_MAX_DAYS}.", parse_mode=enums.ParseMode.HTML)

        data = await db.get_eco_user(user_id)
        if data["balance"] < PROTECT_MIN_BALANCE:
            return await message.reply_text(
                f"⚠️ ʏᴏᴜ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀꜱᴛ {fmt_amount(PROTECT_MIN_BALANCE)} ʙᴀʟᴀɴᴄᴇ ᴛᴏ ʙᴜʏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.",
                parse_mode=enums.ParseMode.HTML
            )
        cost = days * PROTECT_COST_PER_DAY
        if data["balance"] < cost:
            return await message.reply_text(f"⚠️ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴀꜰꜰᴏʀᴅ {fmt_amount(cost)}.", parse_mode=enums.ParseMode.HTML)

        until = now_ts() + days * 86400
        await db.update_balance(user_id, -cost)
        await db.set_protection(user_id, until)
        await message.reply_text(
            f"🛡 ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ꜰᴏʀ <code>{days} ᴅᴀʏ(ꜱ)</code> (-{fmt_amount(cost)}).",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /give <amount>
    # ==========================================================
    @app.on_message(filters.command("give"))
    async def give_cmd(client, message: Message):
        target = await get_target_user(client, message)
        if not target:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ɢɪᴠᴇ ᴛʜᴇᴍ ᴍᴏɴᴇʏ.", parse_mode=enums.ParseMode.HTML)
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/give &lt;ᴀᴍᴏᴜɴᴛ&gt;</code> (ʀᴇᴘʟʏ)", parse_mode=enums.ParseMode.HTML)
        amount = int(parts[1].strip())

        data = await db.get_eco_user(message.from_user.id)
        if data["balance"] < amount:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ.", parse_mode=enums.ParseMode.HTML)

        await db.update_balance(message.from_user.id, -amount)
        await db.update_balance(target.id, amount)
        await message.reply_text(
            f"🤝 {message.from_user.mention} ɢᴀᴠᴇ {fmt_amount(amount)} ᴛᴏ {target.mention}.",
            parse_mode=enums.ParseMode.HTML
        )
