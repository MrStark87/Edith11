# ============================================================
# Group Manager Bot — Tools
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import db
import re
import aiohttp
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# ==========================================================
# Patterns
# ==========================================================

PHONE_PATTERN = re.compile(
    r"(\+?\d[\d\s\-]{7,14}\d)",
    re.IGNORECASE
)

HASHTAG_PATTERN = re.compile(r"#\w+")


# ==========================================================
# Telegraph upload helper
# ==========================================================

async def upload_to_telegraph(title: str, content: str) -> str | None:
    """ᴛᴇxᴛ ᴋᴏ ᴛᴇʟᴇɢʀᴀᴘʜ ᴘᴀʀ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴏ ᴀᴜʀ ʟɪɴᴋ ʀᴇᴛᴜʀɴ ᴋᴀʀᴏ"""
    try:
        async with aiohttp.ClientSession() as session:
            # Account create
            async with session.post("https://api.telegra.ph/createAccount", json={
                "short_name": "NomadeBot",
                "author_name": "ɴᴏᴍᴀᴅᴇ ʜᴇʟᴘ ʙᴏᴛ"
            }) as resp:
                data = await resp.json()
                token = data["result"]["access_token"]

            # Page create
            async with session.post("https://api.telegra.ph/createPage", json={
                "access_token": token,
                "title": title or "Message",
                "content": [{"tag": "p", "children": [content]}],
                "return_content": False
            }) as resp:
                data = await resp.json()
                return data["result"]["url"]
    except Exception as e:
        logger.error(f"ᴛᴇʟᴇɢʀᴀᴘʜ ᴜᴘʟᴏᴀᴅ ᴇʀʀᴏʀ: {e}")
        return None


# ==========================================================
# Help Texts
# ==========================================================
LONGMSG_HELP_TEXT = """
╔══════════════════╗
   📄 𝗹𝗼𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲
╚══════════════════╝

❖ 𝗹𝗼𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘂𝗽𝗹𝗼𝗮𝗱 𝘁𝗼 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗽𝗵 𝗮𝗻𝗱 𝘀𝗲𝗻𝗱 𝗮𝘀 𝗹𝗶𝗻𝗸𝘀.

❍ /echo <text> ➻ 𝗿𝗲𝗽𝗹𝘆 𝘄𝗶𝘁𝗵 𝘁𝗵𝗲 𝘀𝗮𝗺𝗲 𝘁𝗲𝘅𝘁. 𝗶𝗳 𝗹𝗼𝗻𝗴, 𝗴𝗲𝘁 𝗮 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗽𝗵 𝗹𝗶𝗻𝗸.
❍ /setlongmode ᴏꜰꜰ ➻ 𝗻𝗼 𝗮𝗰𝘁𝗶𝗼𝗻 𝗼𝗻 𝗹𝗼𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀.
❍ /setlongmode ᴍᴀɴᴜᴀʟ ➻ 𝗱𝗲𝗹𝗲𝘁𝗲 + 𝘄𝗮𝗿𝗻 𝘂𝘀𝗲𝗿.
❍ /setlongmode ᴀᴜᴛᴏᴍᴀᴛɪᴄ ✅ ᴅᴇꜰᴀᴜʟᴛ ➻ 𝗱𝗲𝗹𝗲𝘁𝗲 + 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗽𝗵 𝗹𝗶𝗻𝗸 𝗰𝗿𝗲𝗮𝘁𝗲.
❍ /setlonglimit <50–2000> ➻ 𝘀𝗲𝘁 𝗰𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿 𝗹𝗶𝗺𝗶𝘁. 𝗱𝗲𝗳𝗮𝘂𝗹𝘁: 800.
👮 𝗺𝗼𝗱𝗲/limit 𝗼𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘀𝗲𝘁.
"""


PHONE_HELP_TEXT = """
╔══════════════════╗
   📞 𝗽𝗵𝗼𝗻𝗲 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻
╚══════════════════╝

❖ 𝗽𝗵𝗼𝗻𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.
❍ /nophone ᴏɴ  ➻ 𝗯𝗹𝗼𝗰𝗸 ✅  
❍ /nophone ᴏꜰꜰ ➻ 𝗮𝗹𝗹𝗼𝘄 ❌

❖ 𝗱𝗲𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗲𝘅𝗮𝗺𝗽𝗹𝗲𝘀:
➻ +91 9876543210  
➻ +1-234-567-8900  
➻ 919876543210

ℹ️ 𝗣𝗵𝗼𝗻𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆.  
👮 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀.
"""

HASHTAG_HELP_TEXT = """
╔══════════════════╗
   # 𝗵𝗮𝘀𝗵𝘁𝗮𝗴 𝗳𝗶𝗹𝘁𝗲𝗿
╚══════════════════╝

❖ 𝗛𝗮𝘀𝗵𝘁𝗮𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.
❍ /nohashtags ᴏɴ  ➻ 𝗯𝗹𝗼𝗰𝗸 ✅  
❍ /nohashtags ᴏꜰꜰ ➻ 𝗮𝗹𝗹𝗼𝘄 ❌

❖ 𝗱𝗲𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗲𝘅𝗮𝗺𝗽𝗹𝗲𝘀:
➻ #ᴊᴏɪɴ, #ᴘʀᴏᴍᴏᴛɪᴏɴ, #ᴛʀᴇɴᴅɪɴɢ  
➻ ᴀɴʏ ᴡᴏʀᴅ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ #

ℹ️ 𝗛𝗮𝘀𝗵𝘁𝗮𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆.  
👮 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀.
"""


def register_tools_handler(app: Client):

    # ==========================================================
    # /echo
    # ==========================================================

    @app.on_message(filters.group & filters.command("echo"))
    async def echo_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: `/echo <text>`")

        text = parts[1]
        limit = await db.get_longlimit(message.chat.id)

        if len(text) <= limit:
            await message.reply_text(text)
        else:
            link = await upload_to_telegraph("Echo", text)
            if link:
                await message.reply_text(f"📄 ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴠᴇʀʏ ʟᴏɴɢ – ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴘʜ:\n{link}")
            else:
                await message.reply_text("❌ ᴛᴇʟᴇɢʀᴀᴘʜ ᴜᴘʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ. ᴛʀʏ ʟᴀᴛᴇʀ.")


    # ==========================================================
    # /setlongmode
    # ==========================================================

    @app.on_message(filters.group & filters.command("setlongmode"))
    async def setlongmode_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["off", "manual", "automatic"]:
            mode = await db.get_longmode(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/setlongmode ᴏꜰꜰ|ᴍᴀɴᴜᴀʟ|ᴀᴜᴛᴏᴍᴀᴛɪᴄ`\n\n📊 ᴄᴜʀʀᴇɴᴛ: `{mode}`"
            )

        mode = parts[1].lower()
        await db.set_longmode(message.chat.id, mode)

        info = {
            "off": "⚠️ ᴛʜᴇʀᴇ ᴡɪʟʟ ʙᴇ ɴᴏ ᴀᴄᴛɪᴏɴ ᴏɴ ʟᴏɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ.",
            "manual": "🗑️ ʟᴏɴɢ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ + ᴜꜱᴇʀ ᴡɪʟʟ ʙᴇ ᴡᴀʀɴᴇᴅ.",
            "automatic": "📄 ʟᴏɴɢ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ + ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ.",
        }
        await message.reply_text(f"✅ ʟᴏɴɢ ᴍᴇꜱꜱᴀɢᴇ ᴍᴏᴅᴇ: `{mode}`\n\n{info[mode]}")


    # ==========================================================
    # /setlonglimit
    # ==========================================================

    @app.on_message(filters.group & filters.command("setlonglimit"))
    async def setlonglimit_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            limit = await db.get_longlimit(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/setlonglimit <200–4000>`\n\n📊 ᴄᴜʀʀᴇɴᴛ ʟɪᴍɪᴛ: `{limit}` ᴄʜᴀʀᴀᴄᴛᴇʀꜱ"
            )

        num = int(parts[1].strip())
        if not (50 <= num <= 4000):
            return await message.reply_text("⚠️ ᴛʜᴇ ʟɪᴍɪᴛ ꜱʜᴏᴜʟᴅ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 50 ᴛᴏ 2000")

        await db.set_longlimit(message.chat.id, num)
        await message.reply_text(f"✅ ʟᴏɴɢ ᴍᴇꜱꜱᴀɢᴇ ʟɪᴍɪᴛ ꜱᴇᴛ: `{num}` ᴄʜᴀʀᴀᴄᴛᴇʀꜱ")


    # ==========================================================
    # Enforce long message — group messages check karo
    # ==========================================================

    @app.on_message(filters.group & filters.text & ~filters.service, group=4)
    async def enforce_longmsg(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        mode = await db.get_longmode(message.chat.id)
        if mode == "off":
            return

        limit = await db.get_longlimit(message.chat.id)
        if not message.text or len(message.text) <= limit:
            return

        await message.delete()

        if mode == "manual":
            await client.send_message(
                message.chat.id,
                f"⚠️ {message.from_user.mention}, ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴠᴇʀʏ ʟᴏɴɢ ({len(message.text)} ᴄʜᴀʀꜱ).\n"
                f"ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ꜱᴍᴀʟʟᴇʀ ᴛʜᴀɴ {limit} ᴄʜᴀʀᴀᴄᴛᴇʀꜱ."
            )
        elif mode == "automatic":
            link = await upload_to_telegraph(
                f"ᴍᴇꜱꜱᴀɢᴇ ʙʏ {message.from_user.first_name}",
                message.text
            )
            if link:
                await client.send_message(
                    message.chat.id,
                    f"📄 {message.from_user.mention}'ꜱ ʟᴇɴɢᴛʜ ᴍᴇꜱꜱᴀɢᴇ ɢᴏᴛ ᴜᴘʟᴏᴀᴅᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴘʜ:\n{link}"
                )


    # ==========================================================
    # /nophone
    # ==========================================================

    @app.on_message(filters.group & filters.command("nophone"))
    async def nophone_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_nophone_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/nophone ᴏɴ` ʏᴀ `/nophone ᴏꜰꜰ`\n\n📊 ᴄᴜʀʀᴇɴᴛ: {current}"
            )

        status = parts[1].lower() == "on"
        await db.set_nophone_status(message.chat.id, status)
        await message.reply_text(
            "✅ **ᴘʜᴏɴᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴏɴ!**\n\nᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ʟɪᴋᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. 📵"
            if status else
            "⚠️ **ᴘʜᴏɴᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴏꜰꜰ!**"
        )


    # ==========================================================
    # Enforce phone
    # ==========================================================

    @app.on_message(filters.group & filters.text & ~filters.service, group=5)
    async def enforce_nophone(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        if not await db.get_nophone_status(message.chat.id):
            return

        if message.text and PHONE_PATTERN.search(message.text):
            await message.delete()


    # ==========================================================
    # /nohashtags
    # ==========================================================

    @app.on_message(filters.group & filters.command("nohashtags"))
    async def nohashtags_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜᴏꜱ ᴄᴏᴍᴍᴀɴᴅ ʙᴇʙᴇ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_nohashtag_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/nohashtags ᴏɴ` ʏᴀ `/nohashtags ᴏꜰꜰ`\n\n📊 ᴄᴜʀʀᴇɴᴛ: {current}"
            )

        status = parts[1].lower() == "on"
        await db.set_nohashtag_status(message.chat.id, status)
        await message.reply_text(
            "✅ **ʜᴀꜱʜᴛᴀɢ ꜰɪʟᴛᴇʀ ᴏɴ!**\n\nɴᴏᴡ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪᴛʜ ʜᴀꜱʜᴛᴀɢꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. 🚫#"
            if status else
            "⚠️ **ʜᴀꜱʜᴛᴀɢ ꜰɪʟᴛᴇʀ ᴏꜰꜰ!**"
        )


    # ==========================================================
    # Enforce hashtag
    # ==========================================================

    @app.on_message(filters.group & filters.text & ~filters.service, group=6)
    async def enforce_nohashtag(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        if not await db.get_nohashtag_status(message.chat.id):
            return

        if message.text and HASHTAG_PATTERN.search(message.text):
            await message.delete()
