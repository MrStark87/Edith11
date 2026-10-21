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
    "╔══════════════════╗\n"
    "  🔡 𝗳𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /fancytext 𝗼𝗻 — 𝗮𝗹𝗹𝗼𝘄 𝗳𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 ✅ (𝗻𝗼 𝗮𝗰𝘁𝗶𝗼𝗻)\n"
    "➻ /fancytext 𝗼𝗳𝗳 — 𝗯𝗹𝗼𝗰𝗸 𝗳𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 ❌ (𝗱𝗲𝗹𝗲𝘁𝗲 + 𝘄𝗮𝗿𝗻)\n\n"
    "❖ 𝗵𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀 ❖\n"
    "➻ 𝗼𝗻: 𝗨𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝘁𝗮𝗹𝗸 𝘂𝘀𝗶𝗻𝗴 𝗳𝗮𝗻𝗰𝘆 𝗳𝗼𝗻𝘁𝘀 𝗳𝗿𝗲𝗲𝗹𝘆.\n"
    "➻ 𝗼𝗳𝗳: 𝗙𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆 + 𝘂𝘀𝗲𝗿 𝗴𝗲𝘁𝘀 𝗮 𝗪𝗔𝗥𝗡.\n"
    "➻ 𝗪𝗮𝗿𝗻 𝗹𝗶𝗺𝗶𝘁 𝗿𝗲𝗮𝗰𝗵 𝗵𝗼𝗻𝗲 𝗽𝗮𝗿 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗮𝗰𝘁𝗶𝗼𝗻 𝗲𝘅𝗲𝗰𝘂𝘁𝗲 𝗵𝗼𝗴𝗮.\n"
)


FANCY_TEXT = (
    "➻ /fancytext 𝗼𝗻 — 𝗮𝗹𝗹𝗼𝘄 𝗳𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 ✅ (𝗻𝗼 𝗮𝗰𝘁𝗶𝗼𝗻)\n"
    "➻ /fancytext 𝗼𝗳𝗳 — 𝗯𝗹𝗼𝗰𝗸 𝗳𝗮𝗻𝗰𝘆 𝘁𝗲𝘅𝘁 ❌ (𝗱𝗲𝗹𝗲𝘁𝗲 + 𝘄𝗮𝗿𝗻)\n\n"
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
