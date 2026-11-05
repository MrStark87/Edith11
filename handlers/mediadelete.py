# ============================================================
# Group Manager Bot — Media Auto Delete
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import asyncio
import re
import logging
import db

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# ==========================================================
# Time Parser — "5m", "1h", "24h" → seconds
# ==========================================================

def parse_time(text: str):
    match = re.fullmatch(r"(\d+)(m|h)", text.strip().lower())
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    seconds = value * 60 if unit == "m" else value * 3600
    if seconds < 60 or seconds > 86400:
        return None
    return seconds


def seconds_to_readable(s: int) -> str:
    return f"{s // 60}m" if s < 3600 else f"{s // 3600}h"


# ==========================================================
# Background delete task
# ==========================================================

async def delete_after(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


# ==========================================================
# Help Text
# ==========================================================
MEDIADELETE_HELP_TEXT = (
    f"<blockquote>🎬 <b>𝖬𝖾𝖽𝗂𝖺 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾</b></blockquote>\n\n"
    f"❖ 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖱𝖾𝗆𝗈𝗏𝖾𝗌 𝖬𝖾𝖽𝗂𝖺 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝖿𝗍𝖾𝗋 𝖠 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖣𝖾𝗅𝖺𝗒.\n\n"

    f"<blockquote expandable>🔧 <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b></blockquote>\n"
    f"❍ <code>/mediadelete on</code> ➻ 𝖤𝗇𝖺𝖻𝗅𝖾 𝖬𝖾𝖽𝗂𝖺 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾 ✅\n"
    f"❍ <code>/mediadelete off</code> ➻ 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖬𝖾𝖽𝗂𝖺 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾 ❌\n"
    f"❍ <code>/setmediadelay <time></code> ➻ 𝖲𝖾𝗍 𝖣𝖾𝗅𝖺𝗒 𝖡𝖾𝖿𝗈𝗋𝖾 𝖣𝖾𝗅𝖾𝗍𝗂𝗈𝗇\n\n"

    f"<blockquote expandable>⏱️ <b>𝖳𝗂𝗆𝖾 𝖥𝗈𝗋𝗆𝖺𝗍</b></blockquote>\n"
    f"➥ 5𝗆 = 5 𝖬𝗂𝗇𝗎𝗍𝖾𝗌\n"
    f"➥ 1𝗁 = 1 𝖧𝗈𝗎𝗋\n"
    f"➥ 12𝗁 = 12 𝖧𝗈𝗎𝗋𝗌\n"
    f"➥ 24𝗁 = 24 𝖧𝗈𝗎𝗋𝗌\n"
    f"➥ 𝖱𝖺𝗇𝗀𝖾: 1𝗆 𝖳𝗈 24𝗁 — 𝖣𝖾𝖿𝖺𝗎𝗅𝗍: 5𝗆\n\n"

    f"<blockquote expandable>ℹ️ <b>𝖠𝗉𝗉𝗅𝗂𝖾𝗌 𝖳𝗈</b></blockquote>\n"
    f"➥ 𝖯𝗁𝗈𝗍𝗈𝗌, 𝖵𝗂𝖽𝖾𝗈𝗌, 𝖲𝗍𝗂𝖼𝗄𝖾𝗋𝗌, 𝖦𝗂𝖿𝗌\n"
    f"➥ 𝖠𝗇𝗂𝗆𝖺𝗍𝗂𝗈𝗇𝗌, 𝖫𝗈𝖼𝖺𝗍𝗂𝗈𝗇𝗌 𝖠𝗇𝖽 𝖯𝗈𝗅𝗅𝗌\n\n"

    f"👮 <b>𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌.</b>"
)


def register_mediadelete_handler(app: Client):

    # ==========================================================
    # /mediadelete on/off
    # ==========================================================

    @app.on_message(filters.group & filters.command("mediadelete"))
    async def mediadelete_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_mediadelete_status(message.chat.id)
            delay = await db.get_mediadelay(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/mediadelete ᴏɴ` ᴏʀ `/mediadelete ᴏꜰꜰ`\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {current}\n"
                f"⏱️ ᴅᴇʟᴀʏ: `{seconds_to_readable(delay)}`"
            )

        status = parts[1].lower() == "on"
        await db.set_mediadelete_status(message.chat.id, status)

        if status:
            delay = await db.get_mediadelay(message.chat.id)
            await message.reply_text(
                f"✅ **ᴍᴇᴅɪᴀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴏɴ!**\n\n"
                f"ᴘʜᴏᴛᴏꜱ, ᴠɪᴅᴇᴏꜱ, ꜱᴛɪᴄᴋᴇʀꜱ, ɢɪꜰꜱ, ᴀɴɪᴍᴀᴛɪᴏɴꜱ,\n"
                f"ʟᴏᴄᴀᴛɪᴏɴꜱ ᴀɴᴅ ᴘᴏʟʟꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ `{seconds_to_readable(delay)}`."
            )
        else:
            await message.reply_text("⚠️ **ᴍᴇᴅɪᴀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴏꜰꜰ!**")


    # ==========================================================
    # /setmediadelay <time>
    # ==========================================================

    @app.on_message(filters.group & filters.command("setmediadelay"))
    async def setmediadelay_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            delay = await db.get_mediadelay(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/setmediadelay <time>`\n\n"
                f"ꜰᴏʀᴍᴀᴛ: `5ᴍ` `1ʜ` `12ʜ` `24ʜ`\n"
                f"ʀᴀɴɢᴇ: 1ᴍ ᴛᴏ 24ʜ\n"
                f"⏱️ ᴄᴜʀʀᴇɴᴛ: `{seconds_to_readable(delay)}`"
            )

        seconds = parse_time(parts[1])
        if not seconds:
            return await message.reply_text(
                "⚠️ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!\n\n"
                "ᴜꜱᴇ: `5ᴍ` `1ʜ` `12ʜ` `24ʜ`\n"
                "ʀᴀɴɢᴇ: 1ᴍ ᴛᴏ 24ʜ"
            )

        await db.set_mediadelay(message.chat.id, seconds)
        await message.reply_text(f"✅ ᴍᴇᴅɪᴀ ᴅᴇʟᴇᴛᴇ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ `{seconds_to_readable(seconds)}`.")


    # ==========================================================
    # Enforce — detect media and schedule deletion
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=8)
    async def enforce_mediadelete(client, message: Message):
        if not (message.photo or message.video or message.sticker or
                message.animation or message.document or message.location or message.poll):
            return

        if not await db.get_mediadelete_status(message.chat.id):
            return

        delay = await db.get_mediadelay(message.chat.id)
        asyncio.ensure_future(delete_after(message, delay))
