# ============================================================
# Group Manager Bot — Rules System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import db


RULES_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   📜 𝗴𝗿𝗼𝘂𝗽 𝗿𝘂𝗹𝗲𝘀\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /setrules &lt;𝘁𝗲𝘅𝘁&gt; — 𝘀𝗲𝘁 𝗴𝗿𝗼𝘂𝗽 𝗿𝘂𝗹𝗲𝘀\n"
    "➻ /rules — 𝘃𝗶𝗲𝘄 𝗿𝘂𝗹𝗲𝘀 (𝗮𝗻𝘆𝗼𝗻𝗲)\n"
    "➻ /clearrules — 𝗱𝗲𝗹𝗲𝘁𝗲 𝗿𝘂𝗹𝗲𝘀\n\n"
    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ 𝗵𝘁𝗺𝗹 𝗳𝗼𝗿𝗺𝗮𝘁𝘁𝗶𝗻𝗴 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱\n"
    "➻ /setrules 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆"
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
