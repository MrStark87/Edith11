# ============================================================
# Group Manager Bot — Fancy Text Protection (Custom Reverse Mode)
# Author: Mr. Stark
# Mode: ON = Allowed (No Action) | OFF = Blocked (Delete + Warn)
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import db
import logging
import asyncio
import unicodedata

logger = logging.getLogger(__name__)


FANCY_TEXT_HELP_TEXT = (
    f"<blockquote>🔡 <b>𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/fancytext on</code> — 𝖠𝗅𝗅𝗈𝗐 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 ✅ (𝖭𝗈 𝖠𝖼𝗍𝗂𝗈𝗇)\n"
    f"➻ <code>/fancytext off</code> — 𝖡𝗅𝗈𝖼𝗄 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 ❌ (𝖣𝖾𝗅𝖾𝗍𝖾 + 𝖶𝖺𝗋𝗇)\n\n"
    f"<blockquote expandable>❖ <b>𝖧𝗈𝗐 𝖨𝗍 𝖶𝗈𝗋𝗄𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖮𝗇: 𝖴𝗌𝖾𝗋𝗌 𝖢𝖺𝗇 𝖳𝖺𝗅𝗄 𝖴𝗌𝗂𝗇𝗀 𝖥𝖺𝗇𝖼𝗒 𝖥𝗈𝗇𝗍𝗌 𝖥𝗋𝖾𝖾𝗅𝗒.\n"
    f"➻ 𝖮𝖿𝖿: 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖨𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒 + 𝖴𝗌𝖾𝗋 𝖦𝖾𝗍𝗌 𝖠 𝖶𝖠𝖱𝖭.\n"
    f"➻ 𝖶𝗁𝖾𝗇 𝖶𝖺𝗋𝗇 𝖫𝗂𝗆𝗂𝗍 𝖨𝗌 𝖱𝖾𝖺𝖼𝗁𝖾𝖽, 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼 𝖠𝖼𝗍𝗂𝗈𝗇 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖤𝗑𝖾𝖼𝗎𝗍𝖾𝖽.\n"
)


FANCY_TEXT = (
    f"➻ <code>/fancytext on</code> — 𝖠𝗅𝗅𝗈𝗐 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 ✅ (𝖭𝗈 𝖠𝖼𝗍𝗂𝗈𝗇)\n"
    f"➻ <code>/fancytext off</code> — 𝖡𝗅𝗈𝖼𝗄 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 ❌ (𝖣𝖾𝗅𝖾𝗍𝖾 + 𝖶𝖺𝗋𝗇)\n\n"
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
        logger.error(f"ꜰᴀɴᴄʏ ᴛᴇxᴛ ᴄᴜꜱᴛᴏᴍ ᴀᴄᴛɪᴏɴ ꜰᴀɪʟ: {e}")


def _is_fancy(text: str) -> bool:
    if not text:
        return False
    
    fancy_count = 0
    for char in text:
        cp = ord(char)
        # Mathematical Alphanumeric Symbols Block aur Letterlike Symbols Block character ranges
        if (0x1D400 <= cp <= 0x1D7FF) or (0x2100 <= cp <= 0x214F):
            fancy_count += 1
            if fancy_count >= 2:
                return True
                
        try:
            name = unicodedata.name(char, "")
            if "MATHEMATICAL" in name or "SCRIPT" in name or "FRAKTUR" in name:
                fancy_count += 1
                if fancy_count >= 2:
                    return True
        except Exception:
            pass
            
    return False


async def _del_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


def register_fancy_text_handler(app: Client):

    @app.on_message(filters.group & filters.command("fancytext"))
    async def fancytext_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ꜰᴀɴᴄʏ ᴛᴇxᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.")

        parts = message.text.split()
        if len(parts) < 2:
            status = await db.get_fancytext_status(message.chat.id)
            # Status interpretation inverted for display
            status_str = "ᴀʟʟᴏᴡᴇᴅ (ᴏɴ) ✅" if status else "ʙʟᴏᴄᴋᴇᴅ (ᴏꜰꜰ) ❌"
            return await message.reply_text(
                f"{FANCY_TEXT} ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {status_str}",
                parse_mode=enums.ParseMode.HTML
            )

        opt = parts[1].strip().lower()
        if opt == "on":
            # True matlab status Allowed hai (No action)
            await db.set_fancytext_status(message.chat.id, True)
            await message.reply_text("✅ 𝗙𝗮𝗻𝗰𝘆 𝗧𝗲𝘅𝘁 𝗔𝗹𝗹𝗼𝘄𝗲𝗱 (𝗢𝗡). ᴜꜱᴇʀꜱ ᴄᴀɴ ɴᴏᴡ ꜱᴇɴᴅ ꜰᴀɴᴄʏ ꜰᴏɴᴛꜱ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ.", parse_mode=enums.ParseMode.HTML)
        elif opt == "off":
            # False matlab status Blocked hai (Delete + Warn trigger mode)
            await db.set_fancytext_status(message.chat.id, False)
            await message.reply_text("❌ 𝗙𝗮𝗻𝗰𝘆 𝗧𝗲𝘅𝘁 𝗕𝗹𝗼𝗰𝗸𝗲𝗱 (𝗢𝗙𝗙). ᴀʟʟ ꜰᴀɴᴄʏ/Unicode ꜰᴏɴᴛꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀɴᴅ ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ ᴡᴀʀɴᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text("❗ ᴜꜱᴇ: <code>/fancytext ᴏɴ</code> ᴏʀ <code>/fancytext ᴏꜰꜰ</code>", parse_mode=enums.ParseMode.HTML)

    @app.on_message(filters.group & (filters.text | filters.caption), group=8)
    async def enforce_fancy_text(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        
        # Inverted Condition Check: Agar Status True (ON) hai toh kuch nahi karega (Bypass)
        if await db.get_fancytext_status(chat_id):
            return

        # Admins ko protection hamesha bypass karegi
        if await is_power(client, chat_id, message.from_user.id):
            return

        text = message.text or message.caption
        if not _is_fancy(text):
            return

        # Fancy text detect ho gaya aur status OFF (Blocked) hai, isliye delete kiya
        try:
            await message.delete()
        except Exception:
            pass

        user        = message.from_user
        warn_limit  = await db.get_warn_limit(chat_id)
        warn_action = await db.get_warn_action(chat_id)
        
        # User ko warning add ki direct database me integration se
        warns = await db.add_warn(chat_id, user.id, reason="ꜰᴀɴᴄʏ ᴛᴇxᴛ ᴜꜱᴇᴅ")
        warn_count = warns["count"] if isinstance(warns, dict) else warns

        if warn_count >= warn_limit:
            # Warn limit touch hote hi warns data wipe karke punish kiya
            await db.db.warns.delete_one({"chat_id": chat_id, "user_id": user.id})
            await _take_action(client, chat_id, user.id, warn_action)
            action_emoji = {"ban": "🚫", "kick": "👢", "mute": "🔇"}.get(warn_action, "🚫")
            
            warn_msg = await client.send_message(
                chat_id,
                f"{action_emoji} {user.mention} ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴍᴀx ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ ({warn_limit}/{warn_limit}) "
                f"ʙʏ ᴜꜱɪɴɢ ꜰᴀɴᴄʏ ᴛᴇxᴛ ᴀɴᴅ ʜᴀꜱ ʙᴇᴇɴ {warn_action}ᴅ!",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            warn_msg = await client.send_message(
                chat_id,
                f"🔡 {user.mention}, ꜰᴀɴᴄʏ/Unicode ꜰᴏɴᴛꜱ ᴀʀᴇ ꜱᴛʀɪᴄᴛʟʏ ᴅɪꜱᴀʙʟᴇᴅ ʜᴇʀᴇ!\n"
                f"ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴅᴇʟᴇᴛᴇᴅ. ᴡᴀʀɴ: {warn_count}/{warn_limit}",
                parse_mode=enums.ParseMode.HTML
            )
            
        asyncio.get_event_loop().create_task(_del_after(warn_msg, 30))
