# ============================================================
# Group Manager Bot — Command Deleter
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import db
import re
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# Command pattern — /, !, . se shuru hone wale
CMD_PATTERN = re.compile(r"^[/!.]")


# ==========================================================
# Help Text
# ==========================================================

CMDDELETER_HELP_TEXT = """

╔══════════════════╗
    🗑️ 𝗰𝗺𝗱 𝗱𝗲𝗹𝗲𝘁𝗲𝗿
╚══════════════════╝

❖ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝘀𝘁𝗮𝗿𝘁𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 / ! 𝗼𝗿 . 𝗮𝗿𝗲 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱..
❍ /cmd ᴏɴ  ➻ 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗲𝗻𝗮𝗯𝗹𝗲𝗱 ✅  
❍ /cmd ᴏꜰꜰ ➻ 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱 ❌

❖ 𝗵𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀:
➻ 𝗶𝗳 𝗮 𝘂𝘀𝗲𝗿 𝘀𝗲𝗻𝗱𝘀 /command, !𝗰𝗼𝗺𝗺𝗮𝗻𝗱, 𝗼𝗿 .𝗰𝗼𝗺𝗺𝗮𝗻𝗱,  
➻ 𝘁𝗵𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗶𝘀 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.  
➻ 𝗮𝗱𝗺𝗶𝗻 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝘄𝗶𝗹𝗹 𝗮𝗹𝘀𝗼 𝗯𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.

👮 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀.

"""


def register_cmddeleter_handler(app: Client):

    # ==========================================================
    # /cmd on/off
    # ==========================================================

    @app.on_message(filters.group & filters.command("cmd"))
    async def cmd_toggle(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. .")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_cmddeleter_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/cmd ᴏɴ` ʏᴀ `/cmd ᴏꜰꜰ`\n\n📊 ᴄᴜʀʀᴇɴᴛ: {current}"
            )

        status = parts[1].lower() == "on"
        await db.set_cmddeleter_status(message.chat.id, status)

        if status:
            await message.reply_text(
                "✅ **ᴄᴏᴍᴍᴀɴᴅ ᴅᴇʟᴇᴛᴇʀ ᴏɴ!**\n\n"
                "ɴᴏᴡ /! . ᴄᴏᴍᴍᴀɴᴅꜱ ꜱᴛᴀʀᴛɪɴɢ ꜰʀᴏᴍ ᴛʜɪꜱ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ.."
            )
        else:
            await message.reply_text("⚠️ **ᴄᴏᴍᴍᴀɴᴅ ᴅᴇʟᴇᴛᴇʀ ᴏꜰꜰ!**")


    # ==========================================================
    # Enforce — commands detect karke delete karo
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=50)
    async def enforce_cmddeleter(client, message: Message):
        if not await db.get_cmddeleter_status(message.chat.id):
            return

        text = message.text or message.caption or ""
        if text and CMD_PATTERN.match(text):
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"ᴄᴍᴅ ᴅᴇʟᴇᴛᴇʀ ᴇʀʀᴏʀ: {e}")
            
