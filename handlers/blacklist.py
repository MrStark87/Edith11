# ============================================================
# Group Manager Bot — Blacklist
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram import Client, filters, enums
import db
import re
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


BLACKLIST_HELP_TEXT = (
    f"<blockquote>🚫 <b>𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/addblack &lt;word&gt;</code> — 𝖠𝖽𝖽 𝖶𝗈𝗋𝖽 𝖳𝗈 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍\n"
    f"➻ <code>/rmblack &lt;word&gt;</code> — 𝖱𝖾𝗆𝗈𝗏𝖾 𝖥𝗋𝗈𝗆 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍\n"
    f"➻ <code>/blacklist</code> — 𝖫𝗂𝗌𝗍 𝖠𝗅𝗅 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖶𝗈𝗋𝖽𝗌\n\n"
    f"➻ 🌟 𝖪𝖾𝖾𝗉 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 𝖢𝗅𝖾𝖺𝗇 𝖠𝗇𝖽 𝖲𝖺𝖿𝖾"
)


def register_blacklist_handler(app: Client):

    @app.on_message(filters.group & filters.command("addblack"))
    async def addblack_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/addblack &lt;ᴡᴏʀᴅ&gt;</code>", parse_mode=enums.ParseMode.HTML)

        word = parts[1].strip().lower()
        existing = await db.get_blacklist(message.chat.id)

        if word in existing:
            return await message.reply_text(f"⚠️ <code>{word}</code> ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)

        await db.add_blacklist_word(message.chat.id, word)
        await message.reply_text(f"✅ ᴡᴏʀᴅ <code>{word}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ.", parse_mode=enums.ParseMode.HTML)


    @app.on_message(filters.group & filters.command("rmblack"))
    async def rmblack_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/rmblack &lt;ᴡᴏʀᴅ&gt;</code>", parse_mode=enums.ParseMode.HTML)

        word = parts[1].strip().lower()
        removed = await db.remove_blacklist_word(message.chat.id, word)

        if removed:
            await message.reply_text(f"🗑️ ᴡᴏʀᴅ <code>{word}</code> ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text(f"⚠️ <code>{word}</code> ᴡᴀꜱ ɴᴏᴛ ɪɴ ᴛʜᴇ ʙʟᴀᴄᴋʟɪꜱᴛ.", parse_mode=enums.ParseMode.HTML)


    @app.on_message(filters.group & filters.command("blacklist"))
    async def blacklist_cmd(client, message: Message):
        words = await db.get_blacklist(message.chat.id)

        if not words:
            return await message.reply_text("📭 ɴᴏ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.")

        word_list = "\n".join(f"• <code>{w}</code>" for w in sorted(words))
        await message.reply_text(
            f"🚫 𝗕𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝗪𝗼𝗿𝗱𝘀:\n\n{word_list}",
            parse_mode=enums.ParseMode.HTML
        )


    @app.on_message(filters.group & filters.text & ~filters.service, group=10)
    async def enforce_blacklist(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        words = await db.get_blacklist(message.chat.id)
        if not words:
            return

        text_lower = message.text.lower()
        for word in words:
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
            if pattern.search(text_lower):
                try:
                    await message.delete()
                except Exception as e:
                    logger.error(f"ʙʟᴀᴄᴋʟɪꜱᴛ ᴅᴇʟᴇᴛᴇ ᴇʀʀᴏʀ: {e}")
                return
