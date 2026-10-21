# ============================================================
# Group Manager Bot — Blacklisted Users
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
import logging
from pyrogram.enums import ChatMemberStatus
import db

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


async def extract_user_id(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None, None

    arg = parts[1].strip()
    try:
        if arg.startswith("@"):
            user = await client.get_users(arg)
            return user.id, user.first_name
        elif arg.lstrip("-").isdigit():
            user = await client.get_users(int(arg))
            return user.id, user.first_name
    except Exception:
        pass
    return None, None

BLACKUSER_HELP_TEXT = (
    f"╔══════════════════╗\n"
    f" 🚷 𝗕𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝗨𝘀𝗲𝗿𝘀\n"
    f"╚══════════════════╝\n\n"
    
    f"𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗵𝗮𝘃𝗲 𝗮𝗹𝗹 𝘁𝗵𝗲𝗶𝗿 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
    f"𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 — 𝘁𝗲𝘅𝘁, 𝗺𝗲𝗱𝗶𝗮,\n"
    f"𝘀𝘁𝗶𝗰𝗸𝗲𝗿𝘀, 𝗴𝗶𝗳'𝘀, 𝗲𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴.\n\n"
    
    f"❖ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    
    f"➻ /blackuser <userid> ➻ 𝗮𝗱𝗱 𝘂𝘀𝗲𝗿 𝘁𝗼 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁\n"
    f"➻ /rmblackuser <userid> ➻ 𝗿𝗲𝗺𝗼𝘃𝗲 𝗳𝗿𝗼𝗺 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁\n"
    f"➻ /blacklistusers ➻ 𝘀𝗲𝗲 𝗮𝗹𝗹 𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝘂𝘀𝗲𝗿𝘀\n\n"
    
    f"<i>👮 𝗼𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀</i>\n"
    f"<i>𝗮𝗱𝗺𝗶𝗻𝘀 𝗮𝗿𝗲 𝗻𝗲𝘃𝗲𝗿 𝗮𝗳𝗳𝗲𝗰𝘁𝗲𝗱</i>"
)


def register_blackuser_handler(app: Client):

    # ==========================================================
    # /blackuser
    # ==========================================================

    @app.on_message(filters.group & filters.command("blackuser"))
    async def blackuser_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        user_id, first_name = await extract_user_id(client, message)
        if not user_id:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ <code>/blackuser &lt;ᴜꜱᴇʀɪᴅ/@ᴜꜱᴇʀɴᴀᴍᴇ&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        # Admins cannot be blacklisted
        try:
            target = await client.get_chat_member(message.chat.id, user_id)
            if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text(
                    "⚠️ ᴄᴀɴɴᴏᴛ ʙʟᴀᴄᴋʟɪꜱᴛ ᴀɴ ᴀᴅᴍɪɴ.",
                    parse_mode=enums.ParseMode.HTML
                )
        except Exception:
            pass

        existing = await db.get_blacklisted_users(message.chat.id)
        if user_id in existing:
            return await message.reply_text(
                f"⚠️ ᴜꜱᴇʀ <code>{user_id}</code> ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        await db.add_blacklisted_user(message.chat.id, user_id)
        await message.reply_text(
            f"🚷 {first_name} (<code>{user_id}</code>) ʜᴀꜱ ʙᴇᴇɴ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ.\n\n"
            f"ᴀʟʟ ᴛʜᴇɪʀ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /rmblackuser
    # ==========================================================

    @app.on_message(filters.group & filters.command("rmblackuser"))
    async def rmblackuser_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        user_id, first_name = await extract_user_id(client, message)
        if not user_id:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ <code>/rmblackuser &lt;ᴜꜱᴇʀɪᴅ/@ᴜꜱᴇʀɴᴀᴍᴇ&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        removed = await db.remove_blacklisted_user(message.chat.id, user_id)
        if removed:
            await message.reply_text(
                f"✅ {first_name} (<code>{user_id}</code>) ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ ᴜꜱᴇʀ <code>{user_id}</code> ᴡᴀꜱ ɴᴏᴛ ɪɴ ᴛʜᴇ ʙʟᴀᴄᴋʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )


    # ==========================================================
    # /blacklistusers
    # ==========================================================

    @app.on_message(filters.group & filters.command("blacklistusers"))
    async def blacklistusers_cmd(client, message: Message):
        users = await db.get_blacklisted_users(message.chat.id)

        if not users:
            return await message.reply_text(
                "📭 ɴᴏ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.",
                parse_mode=enums.ParseMode.HTML
            )

        lines = []
        for uid in users:
            try:
                user = await client.get_users(uid)
                lines.append(f"• <a href='tg://user?id={uid}'>{user.first_name}</a> — <code>{uid}</code>")
            except Exception:
                lines.append(f"• <code>{uid}</code>")

        await message.reply_text(
            f"🚷 𝗕𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗲𝗱 𝗨𝘀𝗲𝗿𝘀:\n\n" + "\n".join(lines),
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # Enforce — delete all messages from blacklisted users
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=13)
    async def enforce_blackuser(client, message: Message):
        if not message.from_user:
            return

        blacklisted = await db.get_blacklisted_users(message.chat.id)

        if message.from_user.id in blacklisted:
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"ʙʟᴀᴄᴋᴜꜱᴇʀ ᴅᴇʟᴇᴛᴇ ᴇʀʀᴏʀ: {e}")
