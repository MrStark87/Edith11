# ============================================================
# Group Manager Bot — Ghost Mode & Privacy
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import db
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]



GHOST_HELP_TEXT = (
    f"<blockquote>👻 <b>𝖦𝗁𝗈𝗌𝗍 𝖬𝗈𝖽𝖾</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/ghostmode on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 𝖦𝗁𝗈𝗌𝗍 𝖬𝗈𝖽𝖾 ✅\n"
    f"➻ <code>/ghostmode off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖦𝗁𝗈𝗌𝗍 𝖬𝗈𝖽𝖾 ❌\n\n"

    f"<blockquote expandable>❖ <b>𝖶𝗁𝖺𝗍 𝖦𝖾𝗍𝗌 𝖣𝖾𝗅𝖾𝗍𝖾𝖽</b> ❖</blockquote>\n"
    f"➻ 𝖴𝗌𝖾𝗋 𝖩𝗈𝗂𝗇𝖾𝖽 𝖳𝗁𝖾 𝖦𝗋𝗈𝗎𝗉\n"
    f"➻ 𝖴𝗌𝖾𝗋 𝖫𝖾𝖿𝗍 𝖳𝗁𝖾 𝖦𝗋𝗈𝗎𝗉\n"
    f"➻ 𝖴𝗌𝖾𝗋 𝖶𝖺𝗌 𝖱𝖾𝗆𝗈𝗏𝖾𝖽\n"
    f"➻ 𝖦𝗋𝗈𝗎𝗉 𝖳𝗂𝗍𝗅𝖾 𝖢𝗁𝖺𝗇𝗀𝖾𝖽\n"
    f"➻ 𝖦𝗋𝗈𝗎𝗉 𝖯𝗁𝗈𝗍𝗈 𝖢𝗁𝖺𝗇𝗀𝖾𝖽\n"
    f"➻ 𝖯𝗂𝗇𝗇𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖭𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇𝗌\n"
    f"➻ 𝖵𝗂𝖽𝖾𝗈 𝖢𝗁𝖺𝗍 𝖲𝗍𝖺𝗋𝗍𝖾𝖽 / 𝖤𝗇𝖽𝖾𝖽\n\n"

    f"👮 <b>𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌.</b>"
    )

def register_ghost_handler(app: Client):

    # ==========================================================
    # /ghostmode on/off
    # ==========================================================

    @app.on_message(filters.group & filters.command("ghostmode"))
    async def ghostmode_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_ghost_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/ghostmode ᴏɴ</code> ᴏʀ <code>/ghostmode ᴏꜰꜰ</code>\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ: {current}",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_ghost_status(message.chat.id, status)

        if status:
            await message.reply_text(
                "👻 𝗚𝗵𝗼𝘀𝘁 𝗠𝗼𝗱𝗲 𝗢𝗡!\n\n"
                "ᴀʟʟ ꜱᴇʀᴠɪᴄᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "⚠️ 𝗚𝗵𝗼𝘀𝘁 𝗠𝗼𝗱𝗲 𝗢𝗙𝗙!",
                parse_mode=enums.ParseMode.HTML
            )


    # ==========================================================
    # Enforce — delete service messages
    # ==========================================================

    @app.on_message(filters.group & filters.service, group=12)
    async def enforce_ghost(client, message: Message):
        if not await db.get_ghost_status(message.chat.id):
            return
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"ɢʜᴏꜱᴛ ᴍᴏᴅᴇ ᴅᴇʟᴇᴛᴇ ᴇʀʀᴏʀ: {e}")


    # ==========================================================
    # /privacy
    # ==========================================================

    @app.on_message(filters.command("privacy"))
    async def privacy_cmd(client, message: Message):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📄 ᴠɪᴇᴡ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ",
                url="https://graph.org/Anya-Bots---Privacy-Policy-04-12"
            )]
        ])
        await message.reply_text(
            "╔══════════════════╗\n"
            "   🔒 ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ\n"
            "╚══════════════════╝\n\n"
            "ᴛʜɪꜱ ʙᴏᴛ ᴄᴏʟʟᴇᴄᴛꜱ ᴍɪɴɪᴍᴀʟ ᴅᴀᴛᴀ ʀᴇǫᴜɪʀᴇᴅ\n"
            "ᴛᴏ ꜰᴜɴᴄᴛɪᴏɴ ᴘʀᴏᴘᴇʀʟʏ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.\n\n"
            "ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ʀᴇᴀᴅ ᴏᴜʀ\n"
            "ꜰᴜʟʟ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ.",
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
