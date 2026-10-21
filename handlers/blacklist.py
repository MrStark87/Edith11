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
    f"╔══════════════════╗\n"
    f"   🚫 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁\n"
    f"╚══════════════════╝\n\n"
    
    f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    f"➻ /addblack &lt;𝘄𝗼𝗿𝗱&gt; — 𝗮𝗱𝗱 𝘄𝗼𝗿𝗱 𝘁𝗼 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁\n"
    f"➻ /rmblack &lt;𝘄𝗼𝗿𝗱&gt; — 𝗿𝗲𝗺𝗼𝘃𝗲 𝗳𝗿𝗼𝗺 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁\n"
    f"➻ /blacklist — 𝗹𝗶𝘀𝘁 𝗮𝗹𝗹 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝘄𝗼𝗿𝗱𝘀\n\n"
    
    f"➻ 🌟 𝗸𝗲𝗲𝗽 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 𝗰𝗹𝗲𝗮𝗻 𝗮𝗻𝗱 𝘀𝗮𝗳𝗲"
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
