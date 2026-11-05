# ============================================================
# Group Manager Bot — Forward Protection (Fixed Naye Pyrogram Ke Liye)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import db
import logging
import asyncio

logger = logging.getLogger(__name__)

FORWARD_HELP_TEXT = (
    f"<blockquote>↩️ <b>𝖥𝗈𝗋𝗐𝖺𝗋𝖽 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/forwarding on</code> — 𝖠𝗅𝗅𝗈𝗐 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝗌 ✅\n"
    f"➻ <code>/forwarding off</code> — 𝖡𝗅𝗈𝖼𝗄 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝗌 ❌\n\n"
    f"<blockquote expandable>❖ <b>𝖧𝗈𝗐 𝖨𝗍 𝖶𝗈𝗋𝗄𝗌</b> ❖</blockquote>\n"
    f"➻ <b>𝖮𝗇:</b> 𝖠𝗅𝗅 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝗌 𝖠𝗅𝗅𝗈𝗐𝖾𝖽\n"
    f"➻ <b>𝖮𝖿𝖿:</b> 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝖾𝖽 𝖬𝗌𝗀 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 + 𝖶𝖺𝗋𝗇\n"
    f"➻ 𝖶𝖺𝗋𝗇 𝖫𝗂𝗆𝗂𝗍 𝖱𝖾𝖺𝖼𝗁𝖾𝖽 → 𝖡𝖺𝗇/𝖪𝗂𝖼𝗄/𝖬𝗎𝗍𝖾"
)


FORWARD_TEXT = (
    f"➻ <code>/forwarding on</code> — 𝖠𝗅𝗅𝗈𝗐 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝗌 ✅\n"
    f"➻ <code>/forwarding off</code> — 𝖡𝗅𝗈𝖼𝗄 𝖥𝗈𝗋𝗐𝖺𝗋𝖽𝗌 ❌\n\n"
)

async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def _take_action(client, chat_id: int, user_id: int, action: str):
    try:
        if action == "ban":
            await client.ban_chat_member(chat_id, user_id)
        elif action == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        elif action == "mute":
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
    except Exception as e:
        logger.error(f"ꜰᴏʀᴡᴀʀᴅ ᴀᴄᴛɪᴏɴ ꜰᴀɪʟ: {e}")


async def _del_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


def register_forward_handler(app: Client):

    @app.on_message(filters.group & filters.command("forwarding"))
    async def forwarding_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ꜰᴏʀᴡᴀʀᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.")

        parts = message.text.split()
        if len(parts) < 2:
            status = await db.get_forwarding_status(message.chat.id)
            status_str = "ᴀʟʟᴏᴡᴇᴅ (ᴏɴ) ✅" if status else "ʙʟᴏᴄᴋᴇᴅ (ᴏꜰꜰ) ❌"
            return await message.reply_text(
                f"{FORWARD_TEXT} ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {status_str}",
                parse_mode=enums.ParseMode.HTML
            )

        opt = parts[1].strip().lower()
        if opt == "on":
            await db.set_forwarding_status(message.chat.id, True)
            await message.reply_text("✅ 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗗𝗶𝘀𝗮𝗯𝗹𝗲𝗱. ᴜꜱᴇʀꜱ ᴄᴀɴ ɴᴏᴡ ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇꜱ.", parse_mode=enums.ParseMode.HTML)
        elif opt == "off":
            await db.set_forwarding_status(message.chat.id, False)
            await message.reply_text("❌ 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗘𝗻𝗮𝗯𝗹𝗲𝗱. ᴀʟʟ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text("❗ ᴜꜱᴇ <code>/forwarding ᴏɴ</code> ᴏʀ <code>/forwarding ᴏꜰꜰ</code>.", parse_mode=enums.ParseMode.HTML)

    # Naye Pyrogram v2 'forward_origin' system se filtered detection
    @app.on_message(filters.group, group=7)
    async def enforce_forward(client, message: Message):
        if not message.from_user or not getattr(message, "forward_origin", None):
            return

        chat_id = message.chat.id
        if await db.get_forwarding_status(chat_id):
            return  # Agar setting ON (Allowed) hai toh chor do

        if await is_power(client, chat_id, message.from_user.id):
            return  # Admins allowed hain

        try:
            await message.delete()
        except Exception:
            pass

        user        = message.from_user
        warn_limit  = await db.get_warn_limit(chat_id)
        warn_action = await db.get_warn_action(chat_id)
        warns       = await db.add_warn(chat_id, user.id, reason="ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇꜱꜱᴀɢᴇ")

        warn_count = warns["count"] if isinstance(warns, dict) else warns

        if warn_count >= warn_limit:
            await db.reset_warns(chat_id, user.id)
            await _take_action(client, chat_id, user.id, warn_action)
            action_emoji = {"ban": "🚫", "kick": "👢", "mute": "🔇"}.get(warn_action, "🚫")
            warn_msg = await client.send_message(
                chat_id,
                f"{action_emoji} {user.mention} ᴋᴇᴘᴛ ꜰᴏʀᴡᴀʀᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ ᴡᴀꜱ "
                f"{warn_action}ᴅ! ({warn_limit}/{warn_limit} ᴡᴀʀɴꜱ)",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            warn_msg = await client.send_message(
                chat_id,
                f"⚠️ {user.mention}, ꜰᴏʀᴡᴀʀᴅɪɴɢ ɪꜱ ᴅɪꜱᴀʙʟᴇᴅ ʜᴇʀᴇ!\n"
                f"ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴅᴇʟᴇᴛᴇᴅ. ᴡᴀʀɴ: {warn_count}/{warn_limit}",
                parse_mode=enums.ParseMode.HTML
            )

        asyncio.get_event_loop().create_task(_del_after(warn_msg, 30))
