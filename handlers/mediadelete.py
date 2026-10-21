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
MEDIADELETE_HELP_TEXT = """

╔══════════════════╗
   🎬 𝗺𝗲𝗱𝗶𝗮 𝗮𝘂𝘁𝗼-𝗱𝗲𝗹𝗲𝘁𝗲
╚══════════════════╝

❖ 𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗿𝗲𝗺𝗼𝘃𝗲𝘀 𝗺𝗲𝗱𝗶𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗳𝘁𝗲𝗿 𝗮 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲𝗱 𝗱𝗲𝗹𝗮𝘆.

🔧 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
❍ /mediadelete ᴏɴ ➻ 𝗲𝗻𝗮𝗯𝗹𝗲 𝗺𝗲𝗱𝗶𝗮 𝗮𝘂𝘁𝗼-𝗱𝗲𝗹𝗲𝘁𝗲 ✅
❍ /mediadelete ᴏꜰꜰ ➻ 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗺𝗲𝗱𝗶𝗮 𝗮𝘂𝘁𝗼-𝗱𝗲𝗹𝗲𝘁𝗲 ❌
❍ /setmediadelay <time> ➻ 𝘀𝗲𝘁 𝗱𝗲𝗹𝗮𝘆 𝗯𝗲𝗳𝗼𝗿𝗲 𝗱𝗲𝗹𝗲𝘁𝗶𝗼𝗻
  
⏱️ 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁:
➥ 5𝗺 = 5 𝗺𝗶𝗻𝘂𝘁𝗲𝘀  
➥ 1𝗵 = 1 𝗵𝗼𝘂𝗿  
➥ 12𝗵 = 12 𝗵𝗼𝘂𝗿𝘀  
➥ 24𝗵 = 24 𝗵𝗼𝘂𝗿𝘀  
➥ 𝗿𝗮𝗻𝗴𝗲: 1𝗺 𝘁𝗼 24𝗵 — 𝗱𝗲𝗳𝗮𝘂𝗹𝘁: 5𝗺

ℹ️ 𝗮𝗽𝗽𝗹𝗶𝗲𝘀 𝘁𝗼:
➥ 𝗽𝗵𝗼𝘁𝗼𝘀, 𝘃𝗶𝗱𝗲𝗼𝘀, 𝘀𝘁𝗶𝗰𝗸𝗲𝗿𝘀, 𝗴𝗶𝗳𝘀  
➥ 𝗮𝗻𝗶𝗺𝗮𝘁𝗶𝗼𝗻𝘀, 𝗹𝗼𝗰𝗮𝘁𝗶𝗼𝗻𝘀 𝗮𝗻𝗱 𝗽𝗼𝗹𝗹𝘀

👮 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀.

"""


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
