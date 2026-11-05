# ============================================================
# Group Manager Bot — Message Cleaner (Auto Delete)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
import asyncio
import logging
import db

logger = logging.getLogger(__name__)


# ==========================================================
# Helpers
# ==========================================================

def parse_time(time_str: str):
    s = time_str.strip().lower()
    try:
        if s.endswith("m"):
            v = int(s[:-1])
            return v * 60
        elif s.endswith("h"):
            v = int(s[:-1])
            return v * 3600
    except ValueError:
        pass
    return None


def fmt_time(seconds: int) -> str:
    if seconds < 3600:
        m = seconds // 60
        return f"{m} ᴍɪɴᴜᴛᴇ{'s' if m != 1 else ''}"
    h = seconds // 3600
    return f"{h} ʜᴏᴜʀ{'s' if h != 1 else ''}"


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def schedule_delete(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ꜰᴀɪʟᴇᴅ ꜰᴏʀ ᴍꜱɢ {message.id}: {e}")


# ==========================================================
# Help Text
# ==========================================================
CLEANER_HELP_TEXT = (
    f"<blockquote>🧹 <b>𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖢𝗅𝖾𝖺𝗇𝖾𝗋</b></blockquote>\n\n"
    f"❖ 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝖠𝗅𝗅 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖥𝗋𝗈𝗆 𝖱𝖾𝗀𝗎𝗅𝖺𝗋 𝖴𝗌𝖾𝗋𝗌 𝖠𝖿𝗍𝖾𝗋 𝖠 𝖲𝖾𝗍 𝖣𝖾𝗅𝖺𝗒.\n\n"
    f"<blockquote expandable>🔧 <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b></blockquote>\n"
    f"❍ <code>/cleaner on</code> ➻ 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾 ✅\n"
    f"❍ <code>/cleaner off</code> ➻ 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾 ❌\n"
    f"❍ <code>/setcleandelay &lt;time&gt;</code> ➻ 𝖲𝖾𝗍 𝖣𝖾𝗅𝖾𝗍𝗂𝗈𝗇 𝖣𝖾𝗅𝖺𝗒\n"
    f"  ➥ 𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌: <code>5m</code>, <code>1h</code>, <code>12h</code>, <code>24h</code>\n"
    f"❍ <code>/cleanstatus</code> ➻ 𝖲𝗁𝗈𝗐 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌\n\n"
    f"<blockquote expandable>⏱️ <b>𝖳𝗂𝗆𝖾 𝖥𝗈𝗋𝗆𝖺𝗍</b></blockquote>\n"
    f"➥ <code>5m</code> = 5 𝖬𝗂𝗇𝗎𝗍𝖾𝗌\n"
    f"➥ <code>1h</code> = 1 𝖧𝗈𝗎𝗋\n"
    f"➥ 𝖱𝖺𝗇𝗀𝖾: <code>1m</code> 𝖳𝗈 <code>24h</code> — 𝖣𝖾𝖿𝖺𝗎𝗅𝗍: <code>5m</code>\n\n"
    f"<blockquote expandable>ℹ️ <b>𝖭𝗈𝗍𝖾𝗌</b></blockquote>\n"
    f"➥ 𝖠𝖽𝗆𝗂𝗇 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝗋𝖾 𝖭𝖾𝗏𝖾𝗋 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.\n"
    f"➥ 𝖠𝗉𝗉𝗅𝗂𝖾𝗌 𝖳𝗈 𝖠𝗅𝗅 𝖳𝖾𝗑𝗍 𝖠𝗇𝖽 𝖬𝖾𝖽𝗂𝖺.\n"
    f"➥ 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝗎𝗍𝗈-𝖢𝗅𝖾𝖺𝗇 𝖠𝖿𝗍𝖾𝗋 8 𝖲𝖾𝖼𝗈𝗇𝖽𝗌.\n\n"
    f"👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌."
)


def register_cleaner_handler(app: Client):

    # ==========================================================
    # /cleaner on/off
    # ==========================================================

    @app.on_message(filters.group & filters.command("cleaner"))
    async def cleaner_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            try:
                await message.delete()
            except Exception:
                pass
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_cleaner_status(message.chat.id)
            delay = await db.get_cleandelay(message.chat.id)
            current = "✅ ᴇɴᴀʙʟᴇᴅ" if status else "❌ ᴅɪꜱᴀʙʟᴇᴅ"
            reply = await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: `/cleaner ᴏɴ` ᴏʀ `/cleaner ᴏꜰꜰ`\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {current}\n"
                f"⏱️ ᴅᴇʟᴀʏ: `{fmt_time(delay)}`"
            )
            await asyncio.sleep(8)
            try:
                await reply.delete()
                await message.delete()
            except Exception:
                pass
            return

        status = parts[1].lower() == "on"
        await db.set_cleaner_status(message.chat.id, status)
        delay = await db.get_cleandelay(message.chat.id)

        if status:
            reply = await message.reply_text(
                f"✅ **ᴍᴇꜱꜱᴀɢᴇ ᴄʟᴇᴀɴᴇʀ ᴏɴ!**\n\n"
                f"ᴀʟʟ ʀᴇɢᴜʟᴀʀ ᴜꜱᴇʀ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ `{fmt_time(delay)}`."
            )
        else:
            reply = await message.reply_text("⚠️ **ᴍᴇꜱꜱᴀɢᴇ ᴄʟᴇᴀɴᴇʀ ᴏꜰꜰ!**")

        await asyncio.sleep(8)
        try:
            await reply.delete()
            await message.delete()
        except Exception:
            pass


    # ==========================================================
    # /setcleandelay <time>
    # ==========================================================

    @app.on_message(filters.group & filters.command("setcleandelay"))
    async def setcleandelay_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            try:
                await message.delete()
            except Exception:
                pass
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            # Quick pick buttons
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("1 ᴍɪɴ",  callback_data="cleantime_60", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("5 ᴍɪɴ",  callback_data="cleantime_300", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("15 ᴍɪɴ", callback_data="cleantime_900", style=ButtonStyle.PRIMARY),
                ],
                [
                    InlineKeyboardButton("1 ʜʀ",  callback_data="cleantime_3600", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("6 ʜʀ",  callback_data="cleantime_21600", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("24 ʜʀ", callback_data="cleantime_86400", style=ButtonStyle.PRIMARY),
                ],
            ])
            reply = await message.reply_text(
                "⏱️ ᴄʜᴏᴏꜱᴇ ᴀ ᴅᴇʟᴀʏ ᴏʀ ᴜꜱᴇ `/setcleandelay 5ᴍ`:",
                reply_markup=buttons
            )
            await asyncio.sleep(20)
            try:
                await reply.delete()
                await message.delete()
            except Exception:
                pass
            return

        delay = parse_time(parts[1])

        if delay is None:
            reply = await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ! ᴜꜱᴇ: `5ᴍ` `1ʜ` `12ʜ` `24ʜ`")
            await asyncio.sleep(5)
            try:
                await reply.delete()
                await message.delete()
            except Exception:
                pass
            return

        if delay < 60:
            reply = await message.reply_text("❌ ᴍɪɴɪᴍᴜᴍ ᴅᴇʟᴀʏ ɪꜱ `1ᴍ`.")
            await asyncio.sleep(5)
            try:
                await reply.delete()
                await message.delete()
            except Exception:
                pass
            return

        if delay > 86400:
            reply = await message.reply_text("❌ ᴍᴀxɪᴍᴜᴍ ᴅᴇʟᴀʏ ɪꜱ `24ʜ`.")
            await asyncio.sleep(5)
            try:
                await reply.delete()
                await message.delete()
            except Exception:
                pass
            return

        await db.set_cleandelay(message.chat.id, delay)
        status = await db.get_cleaner_status(message.chat.id)
        status_text = "✅ ᴄʟᴇᴀɴᴇʀ ɪꜱ ᴏɴ." if status else "⚠️ ᴄʟᴇᴀɴᴇʀ ɪꜱ ᴏꜰꜰ. ᴜꜱᴇ `/cleaner ᴏɴ` ᴛᴏ ᴇɴᴀʙʟᴇ."

        reply = await message.reply_text(
            f"✅ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ `{fmt_time(delay)}`.\n{status_text}"
        )
        await asyncio.sleep(8)
        try:
            await reply.delete()
            await message.delete()
        except Exception:
            pass


    # ==========================================================
    # Quick pick callback — cleantime_<seconds>
    # ==========================================================

    @app.on_callback_query(filters.regex(r"^cleantime_(\d+)$"))
    async def cleantime_callback(client, callback_query):
        delay = int(callback_query.matches[0].group(1))
        chat_id = callback_query.message.chat.id

        if not await is_admin(client, chat_id, callback_query.from_user.id):
            return await callback_query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪꜱ.", show_alert=True)

        await db.set_cleandelay(chat_id, delay)
        await callback_query.message.edit_text(
            f"✅ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ **{fmt_time(delay)}**."
        )
        await callback_query.answer()


    # ==========================================================
    # /cleanstatus
    # ==========================================================

    @app.on_message(filters.group & filters.command("cleanstatus"))
    async def cleanstatus_cmd(client, message: Message):
        status = await db.get_cleaner_status(message.chat.id)
        delay = await db.get_cleandelay(message.chat.id)

        reply = await message.reply_text(
            f"📊 **ᴍᴇꜱꜱᴀɢᴇ ᴄʟᴇᴀɴᴇʀ ꜱᴛᴀᴛᴜꜱ**\n\n"
            f"{'✅ ᴇɴᴀʙʟᴇᴅ' if status else '❌ ᴅɪꜱᴀʙʟᴇᴅ'}\n"
            f"⏱️ ᴅᴇʟᴀʏ: `{fmt_time(delay)}`"
        )
        await asyncio.sleep(10)
        try:
            await reply.delete()
            await message.delete()
        except Exception:
            pass


    # ==========================================================
    # Enforce — auto delete messages in background
    # ==========================================================

    @app.on_message(filters.group & (filters.text | filters.media) & ~filters.service, group=51)
    async def enforce_cleaner(client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return

        if not await db.get_cleaner_status(message.chat.id):
            return

        if await is_admin(client, message.chat.id, message.from_user.id):
            return

        delay = await db.get_cleandelay(message.chat.id)
        asyncio.get_event_loop().create_task(
            schedule_delete(message, delay)
        )
        
