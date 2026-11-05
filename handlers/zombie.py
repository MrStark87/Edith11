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
ZOMBIE_HELP_TEXT = (
    f"<blockquote>⚠️ <b>𝖱𝖾𝗆𝗈𝗏𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌</b></blockquote>\n\n"

    f"<blockquote expandable>🛠️ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b></blockquote>\n"
    f"❍ <code>/zombie</code> ➻ 𝖲𝖼𝖺𝗇 𝖠𝗇𝖽 𝖱𝖾𝗆𝗈𝗏𝖾 𝖠𝗅𝗅 𝖣𝖾𝗅𝖾𝗍𝖾𝖽\n"
    f"   ➥ 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌 𝖥𝗋𝗈𝗆 𝖳𝗁𝖾 𝖦𝗋𝗈𝗎𝗉 𝖨𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒.\n\n"

    f"<blockquote expandable>ℹ️ <b>𝖭𝗈𝗍𝖾𝗌</b></blockquote>\n"
    f"➥ 𝖡𝗈𝗍 𝖬𝗎𝗌𝗍 𝖡𝖾 𝖠𝗇 𝖠𝖽𝗆𝗂𝗇 𝖶𝗂𝗍𝗁 𝖡𝖺𝗇 𝖯𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇.\n"
    f"➥ 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽.\n"
    f"➥ 𝖠𝗅𝗅 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝖨𝗆𝗆𝖾𝖽𝗂𝖺𝗍𝖾𝗅𝗒."
)


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
