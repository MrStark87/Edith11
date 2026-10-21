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
    f"<blockquote>🆘 <b>𝖠𝖽𝗆𝗂𝗇 𝖳𝖺𝗀 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖧𝗈𝗐 𝖳𝗈 𝖴𝗌𝖾</b> ❖</blockquote>\n"
    f"➻ 𝖳𝗒𝗉𝖾 <code>@admin</code> 𝖨𝗇 𝖦𝗋𝗈𝗎𝗉\n"
    f"➥ 𝖳𝖺𝗀𝗌 𝖠𝗅𝗅 𝖠𝖽𝗆𝗂𝗇𝗌 𝖠𝗍 𝖮𝗇𝖼𝖾\n\n"
    f"➻ 𝖳𝗒𝗉𝖾 <code>@admins</code> 𝖨𝗇 𝖦𝗋𝗈𝗎𝗉\n"
    f"➥ 𝖲𝖺𝗆𝖾 𝖠𝗌 <code>@admin</code>\n\n"
    f"<blockquote expandable>❖ <b>𝖠𝖽𝗆𝗂𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/admintag on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝖽𝗆𝗂𝗇 𝖳𝖺𝗀𝗀𝗂𝗇𝗀\n"
    f"➻ <code>/admintag off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝖽𝗆𝗂𝗇 𝖳𝖺𝗀𝗀𝗂𝗇𝗀\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖳𝗈 𝖠𝗅𝗅 𝖦𝗋𝗈𝗎𝗉 𝖬𝖾𝗆𝖻𝖾𝗋𝗌\n"
    f"➻ 𝖡𝗈𝗍𝗌 𝖠𝗋𝖾 𝖭𝗈𝗍 𝖳𝖺𝗀𝗀𝖾𝖽\n"
    f"➻ 𝖮𝗇 𝖡𝗒 𝖣𝖾𝖿𝖺𝗎𝗅𝗍"
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
