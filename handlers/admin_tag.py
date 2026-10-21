# ============================================================
# Group Manager Bot — @admin / @admins Tag System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto
)
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Help Text
# ============================================================
ADMIN_TAG_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   🆘 @𝗮𝗱𝗺𝗶𝗻 𝘀𝘆𝘀𝘁𝗲𝗺\n"
    "╚══════════════════╝\n\n"

    "❖ 𝗵𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲 ❖\n\n"

    "➻ 𝗧𝘆𝗽𝗲 <code>@𝗮𝗱𝗺𝗶𝗻</code> 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽\n"
    "→ 𝘁𝗮𝗴𝘀 𝗮𝗹𝗹 𝗮𝗱𝗺𝗶𝗻𝘀 𝗮𝘁 𝗼𝗻𝗰𝗲\n\n"

    "➻ 𝗧𝘆𝗽𝗲 <code>@𝗮𝗱𝗺𝗶𝗻𝘀</code> 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽\n"
    "→ 𝘀𝗮𝗺𝗲 𝗮𝘀 @𝗮𝗱𝗺𝗶𝗻\n\n"

    "❖ 𝗮𝗱𝗺𝗶𝗻 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"

    "➻ /admintag 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 @𝗮𝗱𝗺𝗶𝗻 𝘁𝗮𝗴𝗴𝗶𝗻𝗴\n"
    "➻ /admintag 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 @𝗮𝗱𝗺𝗶𝗻 𝘁𝗮𝗴𝗴𝗶𝗻𝗴\n\n"

    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝘁𝗼 𝗮𝗹𝗹 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲𝗺𝗯𝗲𝗿𝘀\n"
    "➻ 𝗯𝗼𝘁𝘀 𝗮𝗿𝗲 𝗻𝗼𝘁 𝘁𝗮𝗴𝗴𝗲𝗱\n"
    "➻ 𝗼𝗻 𝗯𝘆 𝗱𝗲𝗳𝗮𝘂𝗹𝘁"
)

# Emoji cycle for admin mentions
EMOJIS = [
    "🪷", "🪷", "🪷", "🪷", "🪷",
    "🪷", "🪷", "🪷", "🪷", "🪷"
]

# In-memory cache to avoid repeated DB hits
# {chat_id: bool}
_status_cache: dict = {}


async def _get_status(db, chat_id: int) -> bool:
    """ʀᴇᴛᴜʀɴ ᴀᴅᴍɪɴᴛᴀɢ ꜱᴛᴀᴛᴜꜱ — ᴛʀᴜᴇ ʙʏ ᴅᴇꜰᴀᴜʟᴛ."""
    if chat_id in _status_cache:
        return _status_cache[chat_id]
    try:
        status = await db.get_admintag_status(chat_id)
        result = status if status is not None else True
    except Exception:
        result = True
    _status_cache[chat_id] = result
    return result


def register_admin_tag_handler(app: Client):

    import db

    # ----------------------------------------------------------
    # /admintag on|off — toggle the feature
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("admintag"))
    async def admintag_toggle(client, message: Message):
        try:
            member = await client.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if member.status not in [
                ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER
            ]:
                return await message.reply_text(
                    "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴛᴏɢɢʟᴇ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ."
                )
        except Exception:
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            current = await _get_status(db, message.chat.id)
            status_str = "🟢 ᴏɴ" if current else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ @𝗮𝗱𝗺𝗶𝗻 𝗧𝗮𝗴 𝗦𝘆𝘀𝘁𝗲𝗺\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/admintag ᴏɴ</code> ᴏʀ <code>/admintag ᴏꜰꜰ</code>\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {status_str}",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_admintag_status(message.chat.id, status)
        _status_cache[message.chat.id] = status

        if status:
            await message.reply_text(
                "✅ @𝗮𝗱𝗺𝗶𝗻 𝘁𝗮𝗴𝗴𝗶𝗻𝗴 𝗲𝗻𝗮𝗯𝗹𝗲𝗱!\n\n"
                "ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ɴᴏᴡ ᴛʏᴘᴇ <code>@ᴀᴅᴍɪɴ</code> ᴏʀ <code>@ᴀᴅᴍɪɴꜱ</code> "
                "ᴛᴏ ɴᴏᴛɪꜰʏ ᴀʟʟ ᴀᴅᴍɪɴꜱ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "⚠️ @𝗮𝗱𝗺𝗶𝗻 𝘁𝗮𝗴𝗴𝗶𝗻𝗴 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # Trigger: any group message containing @admin or @admins
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.text)
    async def admin_tag_trigger(client, message: Message):
        if not message.from_user:
            return

        text = (message.text or "").lower()
        if "@admin" not in text and "@admins" not in text:
            return

        # Check if feature is enabled for this group
        if not await _get_status(db, message.chat.id):
            return

        try:
            mentions    = []
            emoji_index = 0

            async for member in client.get_chat_members(
                message.chat.id,
                filter=ChatMembersFilter.ADMINISTRATORS
            ):
                user = member.user
                if user.is_bot:
                    continue

                emoji = EMOJIS[emoji_index % len(EMOJIS)]
                mentions.append(
                    f"<a href='tg://user?id={user.id}'>{emoji}</a>"
                )
                emoji_index += 1

            if not mentions:
                return

            caller_name = (
                message.from_user.first_name or
                message.from_user.username or
                "ᴀ ᴍᴇᴍʙᴇʀ"
            )

            await message.reply_text(
                f"🆘 𝗿𝗲𝗽𝗼𝗿𝘁𝗲𝗱 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻𝘀!\n"
                f"{' '.join(mentions)}",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )

        except Exception as e:
            logger.error(f"@ᴀᴅᴍɪɴ ᴛᴀɢ ᴇʀʀᴏʀ ɪɴ {message.chat.id}: {e}")
