# ============================================================
# Economy Game System — Shop & Gift
# Author: Mr. Stark
# ============================================================
import time
from pyrogram import enums, filters, Client
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from handlers.eco_data import (
    CATEGORIES, fmt_amount, WEAPON_EXPIRY_SECONDS, GIFT_EXTRA_COST, loot_bonus_percent, item_emoji
)
import db

ITEMS_PER_PAGE = 6

# temp in-memory state for gift message capture: user_id -> {target_id, category, item, price}
_pending_gift: dict = {}


def build_category_markup(mode: str):
    """mode: 'shop' or 'gift'"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔫 ᴡᴇᴀᴘᴏɴꜱ", callback_data=f"{mode}_cat|weapons|0", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🎁 ᴀꜱꜱᴇᴛꜱ", callback_data=f"{mode}_cat|assets|0", style=ButtonStyle.PRIMARY),
        ],
        [InlineKeyboardButton("💎 ʟᴜxᴜʀʏ", callback_data=f"{mode}_cat|luxury|0", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data=f"{mode}_close", style=ButtonStyle.DANGER)],
    ])


def build_items_markup(mode: str, category: str, page: int, target_id: int = 0):
    items = list(CATEGORIES[category].items())
    start = page * ITEMS_PER_PAGE
    page_items = items[start:start + ITEMS_PER_PAGE]

    rows = []
    for i in range(0, len(page_items), 2):
        pair = page_items[i:i + 2]
        row = []
        for name, price in pair:
            idx = items.index((name, price))
            row.append(InlineKeyboardButton(
                f"{item_emoji(name)} {name} ({fmt_amount(price)})",
                callback_data=f"{mode}_view|{category}|{idx}|{page}|{target_id}",
                style=ButtonStyle.PRIMARY
            ))
        rows.append(row)

    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("« ᴘʀᴇᴠ", callback_data=f"{mode}_cat|{category}|{page - 1}|{target_id}" if mode == "gift" else f"{mode}_cat|{category}|{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"{mode}_cat|{category}|{page + 1}|{target_id}" if mode == "gift" else f"{mode}_cat|{category}|{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"{mode}_back|{target_id}"),
                 InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data=f"{mode}_close", style=ButtonStyle.DANGER)])
    return InlineKeyboardMarkup(rows)


def build_detail_text(mode: str, category: str, name: str, price: int) -> str:
    is_weapon = category == "weapons"
    validity = "24 ʜᴏᴜʀꜱ (ᴛʜᴇɴ ᴇxᴘɪʀᴇꜱ)" if is_weapon else "♾ ᴘᴇʀᴍᴀɴᴇɴᴛ"
    total_cost = price + GIFT_EXTRA_COST if mode == "gift" else price

    text = (
        f"🔎 <b>{item_emoji(name)} {name}</b>\n\n"
        f"➻ ᴄᴀᴛᴇɢᴏʀʏ: <code>{category}</code>\n"
        f"➻ ᴘʀɪᴄᴇ: <code>{fmt_amount(price)}</code>\n"
        f"➻ ᴠᴀʟɪᴅɪᴛʏ: <code>{validity}</code>\n"
    )
    if is_weapon:
        bonus = loot_bonus_percent(name)
        text += f"➻ ᴋɪʟʟ ʟᴏᴏᴛ ʙᴏɴᴜꜱ: <code>+{bonus}%</code>\n"
    if mode == "gift":
        text += f"➻ ɢɪꜰᴛ ᴄᴏꜱᴛ: <code>+{fmt_amount(GIFT_EXTRA_COST)}</code>\n➻ ᴛᴏᴛᴀʟ: <code>{fmt_amount(total_cost)}</code>\n"
    return text


def register_shop_handler(app: Client):

    # ==========================================================
    # /shop
    # ==========================================================
    @app.on_message(filters.command("shop"))
    async def shop_cmd(client, message: Message):
        await message.reply_text(
            "🛒 <b>ꜱʜᴏᴘ</b>\n\nᴄʜᴏᴏꜱᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_category_markup("shop")
        )

    @app.on_callback_query(filters.regex(r"^shop_cat\|(\w+)\|(\d+)$"))
    async def shop_cat_cb(client, callback_query: CallbackQuery):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        await callback_query.message.edit_text(
            f"🛒 <b>ꜱʜᴏᴘ — {category.upper()}</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_items_markup("shop", category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^shop_back\|(\d+)$"))
    async def shop_back_cb(client, callback_query: CallbackQuery):
        await callback_query.message.edit_text(
            "🛒 <b>ꜱʜᴏᴘ</b>\n\nᴄʜᴏᴏꜱᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_category_markup("shop")
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^shop_close$"))
    async def shop_close_cb(client, callback_query: CallbackQuery):
        await callback_query.message.delete()
        await callback_query.answer()

    # ── view item detail (no purchase yet) ──
    @app.on_callback_query(filters.regex(r"^shop_view\|(\w+)\|(\d+)\|(\d+)\|(\d+)$"))
    async def shop_view_cb(client, callback_query: CallbackQuery):
        category, idx, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2)), int(callback_query.matches[0].group(3))
        items = list(CATEGORIES[category].items())
        if idx >= len(items):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        name, price = items[idx]

        text = build_detail_text("shop", category, name, price)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ ʙᴜʏ ({fmt_amount(price)})", callback_data=f"shop_confirm|{category}|{idx}|{page}", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"shop_cat|{category}|{page}", style=ButtonStyle.DANGER)],
        ])
        await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)
        await callback_query.answer()

    # ── confirm purchase ──
    @app.on_callback_query(filters.regex(r"^shop_confirm\|(\w+)\|(\d+)\|(\d+)$"))
    async def shop_confirm_cb(client, callback_query: CallbackQuery):
        category, idx, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2)), int(callback_query.matches[0].group(3))
        items = list(CATEGORIES[category].items())
        if idx >= len(items):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        name, price = items[idx]
        user_id = callback_query.from_user.id

        data = await db.get_eco_user(user_id)
        if data["balance"] < price:
            return await callback_query.answer("⚠️ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.", show_alert=True)

        await db.update_balance(user_id, -price)
        item = {"name": name, "category": category, "price": price, "purchased_at": int(time.time())}
        if category == "weapons":
            item["expires_at"] = int(time.time()) + WEAPON_EXPIRY_SECONDS
        await db.add_inventory_item(user_id, item)

        await callback_query.answer(f"✅ ᴘᴜʀᴄʜᴀꜱᴇᴅ {name}!", show_alert=True)
        await callback_query.message.edit_text(
            f"✅ <b>ᴘᴜʀᴄʜᴀꜱᴇᴅ {name}</b> ꜰᴏʀ {fmt_amount(price)}!",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🛒 ʙᴀᴄᴋ ᴛᴏ ꜱʜᴏᴘ", callback_data=f"shop_cat|{category}|{page}", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data="shop_close", style=ButtonStyle.DANGER),
            ]])
        )

    # ==========================================================
    # /gift (reply-only)
    # ==========================================================
    @app.on_message(filters.command("gift"))
    async def gift_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ꜱᴇɴᴅ ᴛʜᴇᴍ ᴀ ɢɪꜰᴛ.", parse_mode=enums.ParseMode.HTML)
        target = message.reply_to_message.from_user
        if target.id == message.from_user.id:
            return await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢɪꜰᴛ ʏᴏᴜʀꜱᴇʟꜰ.", parse_mode=enums.ParseMode.HTML)

        await message.reply_text(
            f"🎁 <b>ꜱᴇɴᴅ ɢɪꜰᴛ ᴛᴏ {target.mention}</b>\n\nᴄʜᴏᴏꜱᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ (+{fmt_amount(GIFT_EXTRA_COST)} ɢɪꜰᴛ ᴄᴏꜱᴛ):",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔫 ᴡᴇᴀᴘᴏɴꜱ", callback_data=f"gift_cat|weapons|0|{target.id}", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("🎁 ᴀꜱꜱᴇᴛꜱ", callback_data=f"gift_cat|assets|0|{target.id}", style=ButtonStyle.PRIMARY),
                ],
                [InlineKeyboardButton("💎 ʟᴜxᴜʀʏ", callback_data=f"gift_cat|luxury|0|{target.id}", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data="gift_close", style=ButtonStyle.DANGER)],
            ])
        )

    @app.on_callback_query(filters.regex(r"^gift_cat\|(\w+)\|(\d+)\|(\d+)$"))
    async def gift_cat_cb(client, callback_query: CallbackQuery):
        category, page, target_id = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2)), int(callback_query.matches[0].group(3))
        await callback_query.message.edit_text(
            f"🎁 <b>ɢɪꜰᴛ — {category.upper()}</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_items_markup("gift", category, page, target_id)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^gift_back\|(\d+)$"))
    async def gift_back_cb(client, callback_query: CallbackQuery):
        target_id = int(callback_query.matches[0].group(1))
        await callback_query.message.edit_text(
            "🎁 <b>ꜱᴇɴᴅ ɢɪꜰᴛ</b>\n\nᴄʜᴏᴏꜱᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔫 ᴡᴇᴀᴘᴏɴꜱ", callback_data=f"gift_cat|weapons|0|{target_id}", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("🎁 ᴀꜱꜱᴇᴛꜱ", callback_data=f"gift_cat|assets|0|{target_id}", style=ButtonStyle.PRIMARY),
                ],
                [InlineKeyboardButton("💎 ʟᴜxᴜʀʏ", callback_data=f"gift_cat|luxury|0|{target_id}", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("⌯ ᴄʟᴏꜱᴇ ⌯", callback_data="gift_close", style=ButtonStyle.DANGER)],
            ])
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^gift_close$"))
    async def gift_close_cb(client, callback_query: CallbackQuery):
        await callback_query.message.delete()
        await callback_query.answer()

    # ── view gift item detail ──
    @app.on_callback_query(filters.regex(r"^gift_view\|(\w+)\|(\d+)\|(\d+)\|(\d+)$"))
    async def gift_view_cb(client, callback_query: CallbackQuery):
        category, idx, page, target_id = (
            callback_query.matches[0].group(1), int(callback_query.matches[0].group(2)),
            int(callback_query.matches[0].group(3)), int(callback_query.matches[0].group(4))
        )
        items = list(CATEGORIES[category].items())
        if idx >= len(items):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        name, price = items[idx]

        text = build_detail_text("gift", category, name, price)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎁 ꜱᴇɴᴅ ɢɪꜰᴛ ({fmt_amount(price + GIFT_EXTRA_COST)})", callback_data=f"gift_confirm|{category}|{idx}|{target_id}", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"gift_cat|{category}|{page}|{target_id}", style=ButtonStyle.DANGER)],
        ])
        await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^gift_confirm\|(\w+)\|(\d+)\|(\d+)$"))
    async def gift_confirm_cb(client, callback_query: CallbackQuery):
        category, idx, target_id = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2)), int(callback_query.matches[0].group(3))
        items = list(CATEGORIES[category].items())
        if idx >= len(items):
            return await callback_query.answer("⚠️ ɪᴛᴇᴍ ɴᴏᴛ ꜰᴏᴜɴᴅ.", show_alert=True)
        name, price = items[idx]
        total_cost = price + GIFT_EXTRA_COST
        user_id = callback_query.from_user.id

        data = await db.get_eco_user(user_id)
        if data["balance"] < total_cost:
            return await callback_query.answer(f"⚠️ ɴᴇᴇᴅ {fmt_amount(total_cost)} (ɪᴛᴇᴍ + ɢɪꜰᴛ ᴄᴏꜱᴛ).", show_alert=True)

        _pending_gift[user_id] = {
            "target_id": target_id, "category": category, "item": name,
            "price": price, "total_cost": total_cost
        }
        await callback_query.answer()
        await callback_query.message.edit_text(
            f"✍️ ꜱᴇɴᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ɪɴᴄʟᴜᴅᴇ ᴡɪᴛʜ ʏᴏᴜʀ ɢɪꜰᴛ ({name}) — ᴊᴜꜱᴛ ᴛʏᴘᴇ ɪᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ɴᴏᴡ.",
            parse_mode=enums.ParseMode.HTML
        )

    @app.on_message(filters.text & filters.create(lambda _, __, m: m.from_user and m.from_user.id in _pending_gift), group=5)
    async def gift_message_capture(client, message: Message):
        user_id = message.from_user.id
        pending = _pending_gift.pop(user_id, None)
        if not pending:
            return

        data = await db.get_eco_user(user_id)
        if data["balance"] < pending["total_cost"]:
            return await message.reply_text("⚠️ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ᴀɴʏᴍᴏʀᴇ, ɢɪꜰᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.", parse_mode=enums.ParseMode.HTML)

        await db.update_balance(user_id, -pending["total_cost"])
        item = {"name": pending["item"], "category": pending["category"], "price": pending["price"], "purchased_at": int(time.time())}
        if pending["category"] == "weapons":
            item["expires_at"] = int(time.time()) + WEAPON_EXPIRY_SECONDS
        await db.add_inventory_item(pending["target_id"], item)

        gift_msg = message.text

        await message.reply_text(
            f"🎁 <b>ɢɪꜰᴛ ꜱᴇɴᴛ!</b>\n\n"
            f"➻ ɪᴛᴇᴍ: <code>{pending['item']}</code>\n"
            f"➻ ᴠᴀʟᴜᴇ: <code>{fmt_amount(pending['price'])}</code>\n"
            f"➻ ᴍᴇꜱꜱᴀɢᴇ: <i>{gift_msg}</i>",
            parse_mode=enums.ParseMode.HTML
        )

        try:
            await client.send_message(
                pending["target_id"],
                f"🎁 <b>ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ ᴀ ɢɪꜰᴛ!</b>\n\n"
                f"➻ ꜰʀᴏᴍ: {message.from_user.mention}\n"
                f"➻ ɪᴛᴇᴍ: <code>{pending['item']}</code>\n"
                f"➻ ᴍᴇꜱꜱᴀɢᴇ: <i>{gift_msg}</i>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass
