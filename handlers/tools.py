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
LONGMSG_HELP_TEXT = (
    f"<blockquote>📄 <b>𝖫𝗈𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</b></blockquote>\n\n"
    f"❖ 𝖫𝗈𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖴𝗉𝗅𝗈𝖺𝖽 𝖳𝗈 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁 𝖠𝗇𝖽 𝖲𝖾𝗇𝖽 𝖠𝗌 𝖫𝗂𝗇𝗄𝗌.\n\n"
    f"❍ <code>/echo <text></code> ➻ 𝖱𝖾𝗉𝗅𝗒 𝖶𝗂𝗍𝗁 𝖳𝗁𝖾 𝖲𝖺𝗆𝖾 𝖳𝖾𝗑𝗍. 𝖨𝖿 𝖫𝗈𝗇𝗀, 𝖦𝖾𝗍 𝖠 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁 𝖫𝗂𝗇𝗄.\n"
    f"❍ <code>/setlongmode off</code> ➻ 𝖭𝗈 𝖠𝖼𝗍𝗂𝗈𝗇 𝖮𝗇 𝖫𝗈𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌.\n"
    f"❍ <code>/setlongmode manual</code> ➻ 𝖣𝖾𝗅𝖾𝗍𝖾 + 𝖶𝖺𝗋𝗇 𝖴𝗌𝖾𝗋.\n"
    f"❍ <code>/setlongmode automatic</code> ✅ 𝖣𝖾𝖿𝖺𝗎𝗅𝗍 ➻ 𝖣𝖾𝗅𝖾𝗍𝖾 + 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁 𝖫𝗂𝗇𝗄 𝖢𝗋𝖾𝖺𝗍𝖾.\n"
    f"❍ <code>/setlonglimit <50–2000></code> ➻ 𝖲𝖾𝗍 𝖢𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋 𝖫𝗂𝗆𝗂𝗍. 𝖣𝖾𝖿𝖺𝗎𝗅𝗍: 800.\n"
    f"👮 𝖬𝗈𝖽𝖾/𝖫𝗂𝗆𝗂𝗍 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖲𝖾𝗍."
)


PHONE_HELP_TEXT = (
    f"<blockquote>📞 <b>𝖯𝗁𝗈𝗇𝖾 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
    f"❖ 𝖯𝗁𝗈𝗇𝖾 𝖭𝗎𝗆𝖻𝖾𝗋 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝗋𝖾 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n"
    f"❍ <code>/nophone on</code> ➻ 𝖡𝗅𝗈𝖼𝗄 ✅\n"
    f"❍ <code>/nophone off</code> ➻ 𝖠𝗅𝗅𝗈𝗐 ❌\n\n"
    f"<blockquote expandable>❖ <b>𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇 𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ +91 9876543210\n"
    f"➻ +1-234-567-8900\n"
    f"➻ 919876543210\n\n"
    f"ℹ️ 𝖯𝗁𝗈𝗇𝖾 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒.\n"
    f"👮 <b>𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌.</b>"
)


HASHTAG_HELP_TEXT = (
    f"<blockquote># <b>𝖧𝖺𝗌𝗁𝗍𝖺𝗀 𝖥𝗂𝗅𝗍𝖾𝗋</b></blockquote>\n\n"
    f"❖ 𝖧𝖺𝗌𝗁𝗍𝖺𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝗋𝖾 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n"
    f"❍ <code>/nohashtags on</code> ➻ 𝖡𝗅𝗈𝖼𝗄 ✅\n"
    f"❍ <code>/nohashtags off</code> ➻ 𝖠𝗅𝗅𝗈𝗐 ❌\n\n"
    f"<blockquote expandable>❖ <b>𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇 𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ #ᴊᴏɪɴ, #ᴘʀᴏᴍᴏᴛɪᴏɴ, #ᴛʀᴇɴᴅɪɴɢ\n"
    f"➻ ᴀɴʏ ᴡᴏʀᴅ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ #\n\n"
    f"ℹ️ 𝖧𝖺𝗌𝗁𝗍𝖺𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒.\n"
    f"👮 <b>𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌.</b>"
)


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
