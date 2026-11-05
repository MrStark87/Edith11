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

CMDDELETER_HELP_TEXT = (
    f"<blockquote>🗑️ <b>𝖢𝗆𝖽 𝖣𝖾𝗅𝖾𝗍𝖾𝗋</b></blockquote>\n\n"
    f"❖ 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝖶𝗂𝗍𝗁 <code>/</code>, <code>!</code> 𝖮𝗋 <code>.</code> 𝖠𝗋𝖾 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n\n"
    f"❍ <code>/cmd on</code> ➻ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖤𝗇𝖺𝖻𝗅𝖾𝖽 ✅\n"
    f"❍ <code>/cmd off</code> ➻ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 ❌\n\n"
    f"<blockquote expandable>❖ <b>𝖧𝗈𝗐 𝖨𝗍 𝖶𝗈𝗋𝗄𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖨𝖿 𝖠 𝖴𝗌𝖾𝗋 𝖲𝖾𝗇𝖽𝗌 <code>/command</code>, <code>!command</code>, 𝖮𝗋 <code>.command</code>,\n"
    f"➻ 𝖳𝗁𝖾 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖨𝗌 𝖨𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n"
    f"➻ 𝖠𝖽𝗆𝗂𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖶𝗂𝗅𝗅 𝖠𝗅𝗌𝗈 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n\n"
    f"👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌."
)


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
            
