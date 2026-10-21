# ============================================================
# Economy Game System — Owner Commands (/tr, /de)
# Author: Mr. Stark
# ============================================================
from pyrogram import enums, filters, Client
from pyrogram.types import Message
from config import OWNER_ID
from handlers.eco_data import fmt_amount
import db


async def resolve_target(client, message: Message, parts_after_cmd: str):
    """Reply-based OR userid-based target + amount parser. Returns (target_id, amount) or (None, None)."""
    if message.reply_to_message and message.reply_to_message.from_user:
        tokens = parts_after_cmd.split()
        if len(tokens) < 1 or not tokens[0].strip().lstrip("-").isdigit():
            return None, None
        return message.reply_to_message.from_user.id, int(tokens[0].strip())

    tokens = parts_after_cmd.split()
    if len(tokens) < 2 or not tokens[0].lstrip("-").isdigit() or not tokens[1].isdigit():
        return None, None
    return int(tokens[0]), int(tokens[1])


def register_owner_eco_handler(app: Client):

    # ==========================================================
    # /tr <userid> <amount>  (owner only, no limit)
    # ==========================================================
    @app.on_message(filters.command("tr") & filters.user(OWNER_ID))
    async def transfer_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        arg_str = parts[1] if len(parts) > 1 else ""
        target_id, amount = await resolve_target(client, message, arg_str)
        if not target_id:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/tr &lt;user_id&gt; &lt;amount&gt;</code> ᴏʀ ʀᴇᴘʟʏ + <code>/tr &lt;amount&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        await db.update_balance(target_id, amount)
        await message.reply_text(f"✅ ꜱᴇɴᴛ {fmt_amount(amount)} ᴛᴏ <code>{target_id}</code>.", parse_mode=enums.ParseMode.HTML)
        try:
            await client.send_message(
                target_id,
                f"💰 ᴛʜᴇ ᴏᴡɴᴇʀ ꜱᴇɴᴛ ʏᴏᴜ {fmt_amount(amount)}!",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass

    # ==========================================================
    # /de <userid> <amount>  (owner only, deducts / can go from bank too)
    # ==========================================================
    @app.on_message(filters.command("de") & filters.user(OWNER_ID))
    async def deduct_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        arg_str = parts[1] if len(parts) > 1 else ""
        target_id, amount = await resolve_target(client, message, arg_str)
        if not target_id:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/de &lt;user_id&gt; &lt;amount&gt;</code> ᴏʀ ʀᴇᴘʟʏ + <code>/de &lt;amount&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        data = await db.get_eco_user(target_id)
        remaining = amount
        if data["balance"] > 0:
            deduct = min(data["balance"], remaining)
            await db.update_balance(target_id, -deduct)
            remaining -= deduct
        if remaining > 0 and data.get("bank_deposit", 0) > 0:
            deduct = min(data["bank_deposit"], remaining)
            await db.set_bank(target_id, deposit=data["bank_deposit"] - deduct)
            remaining -= deduct

        await message.reply_text(f"✅ ᴅᴇᴅᴜᴄᴛᴇᴅ {fmt_amount(amount - remaining)} ꜰʀᴏᴍ <code>{target_id}</code>.", parse_mode=enums.ParseMode.HTML)
        try:
            await client.send_message(
                target_id,
                f"⚠️ ᴛʜᴇ ᴏᴡɴᴇʀ ᴅᴇᴅᴜᴄᴛᴇᴅ {fmt_amount(amount - remaining)} ꜰʀᴏᴍ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass
