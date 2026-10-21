# ============================================================
# Economy Game System — Leaderboards
# Author: Mr. Stark
# ============================================================
from pyrogram import enums, filters, Client
from pyrogram.types import Message
from handlers.eco_data import fmt_amount
import db


def register_leaderboard_handler(app: Client):

    # ==========================================================
    # /leaderboard — group only
    # ==========================================================
    @app.on_message(filters.command("leaderboard") & filters.group)
    async def leaderboard_cmd(client, message: Message):
        await db.add_eco_group_member(message.chat.id, message.from_user.id)
        rows = await db.get_eco_group_leaderboard(message.chat.id, limit=10)
        if not rows:
            return await message.reply_text("📊 ɴᴏ ᴅᴀᴛᴀ ʏᴇᴛ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ.", parse_mode=enums.ParseMode.HTML)

        text = "🏆 <b>ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n\n"
        for i, row in enumerate(rows, start=1):
            try:
                user = await client.get_users(row["user_id"])
                name = user.mention
            except Exception:
                name = f"<code>{row['user_id']}</code>"
            text += f"{i}. {name} — <code>{fmt_amount(row['balance'])}</code>\n"

        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /overall — group + private
    # ==========================================================
    @app.on_message(filters.command("overall"))
    async def overall_cmd(client, message: Message):
        rows = await db.get_eco_overall_leaderboard(limit=10)
        if not rows:
            return await message.reply_text("📊 ɴᴏ ᴅᴀᴛᴀ ʏᴇᴛ.", parse_mode=enums.ParseMode.HTML)

        text = "🌍 <b>ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n\n"
        for i, row in enumerate(rows, start=1):
            try:
                user = await client.get_users(row["user_id"])
                name = user.mention
            except Exception:
                name = f"<code>{row['user_id']}</code>"
            text += f"{i}. {name} — <code>{fmt_amount(row['balance'])}</code>\n"

        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
