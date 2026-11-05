# ============================================================
# Group Manager Bot — Rules System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import db


RULES_HELP_TEXT = (
    f"<blockquote>📜 <b>𝖦𝗋𝗈𝗎𝗉 𝖱𝗎𝗅𝖾𝗌</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/setrules <𝘁𝗲𝘅𝘁></code> — 𝖲𝖾𝗍 𝖦𝗋𝗈𝗎𝗉 𝖱𝗎𝗅𝖾𝗌\n"
    f"➻ <code>/rules</code> — 𝖵𝗂𝖾𝗐 𝖱𝗎𝗅𝖾𝗌 (𝖠𝗇𝗒𝗈𝗇𝖾)\n"
    f"➻ <code>/clearrules</code> — 𝖣𝖾𝗅𝖾𝗍𝖾 𝖱𝗎𝗅𝖾𝗌\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖧𝖳𝖬𝖫 𝖥𝗈𝗋𝗆𝖺𝗍𝗍𝗂𝗇𝗀 𝖲𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽\n"
    f"➻ <code>/setrules</code> 𝖠𝖽𝗆𝗂𝗇 𝖮𝗇𝗅𝗒"
)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


def register_rules_handler(app: Client):

    @app.on_message(filters.group & filters.command("setrules"))
    async def setrules_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴇᴛ ɢʀᴏᴜᴘ ʀᴜʟᴇꜱ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "⚙️ 𝗨𝘀𝗮𝗴𝗲: <code>/setrules ʏᴏᴜʀ ʀᴜʟᴇꜱ ʜᴇʀᴇ</code>\n\n"
                "ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ɪꜱ ꜱᴜᴘᴘᴏʀᴛᴇᴅ. ɴᴇᴡʟɪɴᴇꜱ ᴀʀᴇ ᴘʀᴇꜱᴇʀᴠᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        await db.set_rules(message.chat.id, parts[1])
        await message.reply_text(
            "✅ 𝗚𝗿𝗼𝘂𝗽 𝗿𝘂𝗹𝗲𝘀 𝘀𝗮𝘃𝗲𝗱!\n\nᴜꜱᴇ /rules ᴛᴏ ᴠɪᴇᴡ ᴛʜᴇᴍ.",
            parse_mode=enums.ParseMode.HTML
        )

    @app.on_message(filters.group & filters.command("rules"))
    async def rules_cmd(client, message: Message):
        rules_text = await db.get_rules(message.chat.id)

        if not rules_text:
            return await message.reply_text(
                "📭 ɴᴏ ʀᴜʟᴇꜱ ꜱᴇᴛ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ.\n"
                "ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴇᴛ ʀᴜʟᴇꜱ ᴜꜱɪɴɢ <code>/setrules</code>.",
                parse_mode=enums.ParseMode.HTML
            )

        await message.reply_text(
            f"📜 𝗥𝘂𝗹𝗲𝘀 — {message.chat.title}\n\n"
            f"{rules_text}"
            "",
            parse_mode=enums.ParseMode.HTML
        )

    @app.on_message(filters.group & filters.command("clearrules"))
    async def clearrules_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʟᴇᴀʀ ʀᴜʟᴇꜱ.")

        existing = await db.get_rules(message.chat.id)
        if not existing:
            return await message.reply_text("⚠️ ɴᴏ ʀᴜʟᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ꜱᴇᴛ.")

        await db.clear_rules(message.chat.id)
        await message.reply_text("🗑 ɢʀᴏᴜᴘ ʀᴜʟᴇꜱ ᴅᴇʟᴇᴛᴇᴅ.")
