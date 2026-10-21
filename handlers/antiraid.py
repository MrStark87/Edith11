# ============================================================
# Group Manager Bot — Anti Raid (New User Auto Mute)
# Author: Mr. Stark
# ============================================================
from pyrogram import enums
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import asyncio
import re
import logging
import db

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


def parse_raid_time(text: str):
    s = text.strip().lower()
    if s == "0":
        return 0
    match = re.fullmatch(r"(\d+)(s|m|h)", s)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    if unit == "s" and 1 <= value <= 60:
        return value
    elif unit == "m" and 1 <= value <= 60:
        return value * 60
    elif unit == "h" and 1 <= value <= 24:
        return value * 3600
    return None


def fmt_raid_time(seconds: int) -> str:
    if seconds == 0:
        return "∞ (ᴜɴᴛɪʟ ᴀᴅᴍɪɴ ᴜɴᴍᴜᴛᴇꜱ)"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    return f"{seconds // 3600}h"

ANTIRAID_HELP_TEXT = (
    f"<blockquote>🛡️ <b>𝖠𝗇𝗍𝗂 𝖱𝖺𝗂𝖽</b></blockquote>\n\n"
    f"𝖭𝖾𝗐 𝗎𝗌𝖾𝗋𝗌 𝗐𝗁𝗈 𝗃𝗈𝗂𝗇 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉 𝖺𝗋𝖾\n"
    f"𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝗆𝗎𝗍𝖾𝖽 𝖿𝗈𝗋 𝖺 𝗌𝖾𝗍 𝗍𝗂𝗆𝖾,\n"
    f"𝖳𝗁𝖾𝗇 𝗎𝗇𝗆𝗎𝗍𝖾𝖽 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒.\n\n"

    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/antiraid on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗎𝗍𝗈 𝖬𝗎𝗍𝖾 ✅\n"
    f"➻ <code>/antiraid off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗎𝗍𝗈 𝖬𝗎𝗍𝖾 ❌\n"
    f"➻ <code>/raiddelay &lt;time&gt;</code> — 𝖲𝖾𝗍 𝖬𝗎𝗍𝖾 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇\n\n"  
    f"<blockquote expandable>❖ <b>𝖳𝗂𝗆𝖾 𝖥𝗈𝗋𝗆𝖺𝗍</b> ❖</blockquote>\n"
    f"➻ <code>1s, 1m, 1h</code>\n"
    f"➻ <code>0</code> = 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 (𝖠𝖽𝗆𝗂𝗇 𝖬𝗎𝗌𝗍 𝖴𝗇𝗆𝗎𝗍𝖾)\n\n"
    f"<blockquote expandable>❖ <b>𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌</b> ❖</blockquote>\n"
    f"<code>/raiddelay 30s</code> — 𝖬𝗎𝗍𝖾 𝖥𝗈𝗋 30 𝖲𝖾𝖼𝗈𝗇𝖽𝗌\n\n"
    f"<i>👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌</i>"
)


def register_antiraid_handler(app: Client):

    @app.on_message(filters.group & filters.command("antiraid"))
    async def antiraid_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_antiraid_status(message.chat.id)
            delay = await db.get_raiddelay(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/antiraid ᴏɴ</code> ᴏʀ <code>/antiraid ᴏꜰꜰ</code>\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {current}\n"
                f"⏱ ᴍᴜᴛᴇ ᴅᴜʀᴀᴛɪᴏɴ: <code>{fmt_raid_time(delay)}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_antiraid_status(message.chat.id, status)
        delay = await db.get_raiddelay(message.chat.id)

        if status:
            await message.reply_text(
                f"✅ 𝗔𝗻𝘁𝗶 𝗥𝗮𝗶𝗱 𝗢𝗡!\n\n"
                f"ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ ᴡɪʟʟ ʙᴇ ᴍᴜᴛᴇᴅ ꜰᴏʀ <code>{fmt_raid_time(delay)}</code> ᴜᴘᴏɴ ᴊᴏɪɴɪɴɢ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text("⚠️ 𝗔𝗻𝘁𝗶 𝗥𝗮𝗶𝗱 𝗢𝗙𝗙!", parse_mode="html")


    @app.on_message(filters.group & filters.command("raiddelay"))
    async def raiddelay_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            delay = await db.get_raiddelay(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/raiddelay &lt;ᴛɪᴍᴇ&gt;</code>\n\n"
                f"ᴇxᴀᴍᴘʟᴇꜱ: <code>30ꜱ</code> <code>5ᴍ</code> <code>1ʜ</code> <code>0</code>\n"
                f"⏱ ᴄᴜʀʀᴇɴᴛ: <code>{fmt_raid_time(delay)}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        seconds = parse_raid_time(parts[1])
        if seconds is None:
            return await message.reply_text(
                "⚠️ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁!\n\n"
                "• ꜱᴇᴄᴏɴᴅꜱ: <code>1ꜱ</code> – <code>60ꜱ</code>\n"
                "• ᴍɪɴᴜᴛᴇꜱ: <code>1ᴍ</code> – <code>60ᴍ</code>\n"
                "• ʜᴏᴜʀꜱ:   <code>1ʜ</code> – <code>24ʜ</code>\n"
                "• <code>0</code> = ᴘᴇʀᴍᴀɴᴇɴᴛ ᴍᴜᴛᴇ",
                parse_mode=enums.ParseMode.HTML
            )

        await db.set_raiddelay(message.chat.id, seconds)
        await message.reply_text(
            f"✅ ʀᴀɪᴅ ᴍᴜᴛᴇ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ <code>{fmt_raid_time(seconds)}</code>.",
            parse_mode=enums.ParseMode.HTML
        )


    @app.on_chat_member_updated(group=1)
    async def enforce_antiraid(client, cmu: ChatMemberUpdated):
        if not cmu.new_chat_member:
            return

        if cmu.new_chat_member.status != ChatMemberStatus.MEMBER:
            return

        if not await db.get_antiraid_status(cmu.chat.id):
            return

        user = cmu.new_chat_member.user
        if user.is_bot:
            return

        delay = await db.get_raiddelay(cmu.chat.id)

        try:
            await client.restrict_chat_member(
                cmu.chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            if delay == 0:
                return
            asyncio.get_event_loop().create_task(
                _auto_unmute(client, cmu.chat.id, user.id, delay)
            )
        except Exception as e:
            logger.error(f"ᴀɴᴛɪ ʀᴀɪᴅ ᴍᴜᴛᴇ ᴇʀʀᴏʀ: {e}")


async def _auto_unmute(client, chat_id: int, user_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await client.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
    except Exception as e:
        logger.error(f"ᴀᴜᴛᴏ ᴜɴᴍᴜᴛᴇ ᴇʀʀᴏʀ: {e}")
