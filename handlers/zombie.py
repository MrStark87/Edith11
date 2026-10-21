# ============================================================
# Group Manager Bot — Zombie Remover
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# ==========================================================
# Help Text
# ==========================================================

ZOMBIE_HELP_TEXT = """
╔════════════════════╗
   ⚠️ 𝗿𝗲𝗺𝗼𝘃𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀
╚════════════════════╝

🛠️ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:

❍ /zombie ➻ 𝘀𝗰𝗮𝗻 𝗮𝗻𝗱 𝗿𝗲𝗺𝗼𝘃𝗲 𝗮𝗹𝗹 𝗱𝗲𝗹𝗲𝘁𝗲𝗱  
  ➥ 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀 𝗳𝗿𝗼𝗺 𝘁𝗵𝗲 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆.

ℹ️ 𝗻𝗼𝘁𝗲𝘀:
➥ 𝗯𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝘁𝗵 𝗯𝗮𝗻 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻.  
➥ 𝗼𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.  
➥ 𝗮𝗹𝗹 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝗶𝗺𝗺𝗲𝗱𝗶𝗮𝘁𝗲𝗹𝘆.
"""


def register_zombie_handler(app: Client):

    # ==========================================================
    # /zombie — Scan and remove deleted accounts
    # ==========================================================

    @app.on_message(filters.group & filters.command("zombie"))
    async def zombie_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        scanning = await message.reply_text("🔍 ꜱᴄᴀɴɴɪɴɢ ꜰᴏʀ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ...")

        removed = 0
        failed = 0

        async for member in client.get_chat_members(message.chat.id):
            if member.user.is_deleted:
                try:
                    await client.ban_chat_member(message.chat.id, member.user.id)
                    await client.unban_chat_member(message.chat.id, member.user.id)
                    removed += 1
                except Exception as e:
                    logger.error(f"ᴢᴏᴍʙɪᴇ ʀᴇᴍᴏᴠᴇ ᴇʀʀᴏʀ: {e}")
                    failed += 1

        if removed == 0:
            await scanning.edit_text("✅ ɴᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.")
        else:
            await scanning.edit_text(
                f"✅ **ᴢᴏᴍʙɪᴇ ꜱᴄᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ!**\n\n"
                f"🗑️ ʀᴇᴍᴏᴠᴇᴅ: `{removed}` ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
                f"❌ ꜰᴀɪʟᴇᴅ: `{failed}`"
            )
