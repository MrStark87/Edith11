# ============================================================
# Group Manager Bot — Abuse Detection
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import db
import re

# ==========================================================
# Abuse word list — apne hisaab se badha sakte ho
# ==========================================================
ABUSE_WORDS = [
    "bc", "mc", "bkl", "chutiya", "madarchod", "bhenchod", "madar", "betic", 
    "randi", "harami", "kamina", "kutte", "saale", "gaandu", "lauda", "laura", "harami", "bsdk", "bhosdi", "betichod", "ᴍᴀᴀ ᴋᴀ", "ʙᴀʜᴀɴ ᴋɪ",
    "lodu", "bhosdike", "chut", "lund", "ᴛᴇʀɪ ᴍᴀ", "fuck",
    "bitch", "bastard", "asshole", "motherfucker", "fucker",
    "shit", "cunt", "whore", "slut", "dickhead", "madharxod", "madharchod", "sala", "rand", "mc", "bc", "mkc", "chut", "boor", "bur",
]

# Pattern — pure word match, case insensitive
ABUSE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in ABUSE_WORDS) + r")\b",
    re.IGNORECASE
)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


def register_abuse_handler(app: Client):

    # ==========================================================
    # /noabuse on/off — Toggle abuse detection
    # ==========================================================

    @app.on_message(filters.group & filters.command("noabuse"))
    async def noabuse_toggle(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ..")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_abuse_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/noabuse ᴏɴ` ʏᴀ `/noabuse ᴏꜰꜰ`\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {current}"
            )

        status = parts[1].lower() == "on"
        await db.set_abuse_status(message.chat.id, status)

        if status:
            await message.reply_text(
                "✅ **ᴀʙᴜꜱᴇ ᴅᴇᴛᴇᴄᴛɪᴏɴ ᴏɴ!**\n\n"
                " 💯 ɴᴏᴡ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴏꜰ ᴛʜᴇ ᴘᴇʀꜱᴏɴ ᴀʙᴜꜱɪɴɢ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. "
            )
        else:
            await message.reply_text(
                "⚠️ **ᴀʙᴜꜱᴇ ᴅᴇᴛᴇᴄᴛɪᴏɴ ᴏꜰꜰ!**\n\n"
                "ᴀʙᴜꜱᴇ ꜰɪʟᴛᴇʀ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ."
            )

    # ==========================================================
    # Enforce — incoming messages check karo
    # ==========================================================

    @app.on_message(filters.group & filters.text & ~filters.service, group=2)
    async def enforce_abuse(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        abuse_on = await db.get_abuse_status(message.chat.id)
        if not abuse_on:
            return

        if message.text and ABUSE_PATTERN.search(message.text):
            try:
                await message.delete()
                warn_msg = await client.send_message(
                    message.chat.id,
                    f"⚠️ {message.from_user.mention}, ᴀʙᴜꜱɪɴɢ ɪꜱ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ! ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ. 🚫"
                )
                # 5 second baad warn msg bhi delete karo (optional clean look)
                import asyncio
                await asyncio.sleep(5)
                await warn_msg.delete()
            except Exception:
                pass
