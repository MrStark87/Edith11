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
    f"╔══════════════════╗\n"
    f"👻 𝗴𝗵𝗼𝘀𝘁 𝗺𝗼𝗱𝗲\n"
    f"╚══════════════════╝\n\n"
    
    f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    f"➻ /ghostmode 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 𝗴𝗵𝗼𝘀𝘁 𝗺𝗼𝗱𝗲 ✅\n"
    f"➻ /ghostmode 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗴𝗵𝗼𝘀𝘁 𝗺𝗼𝗱𝗲 ❌\n\n"
    
    f"❖ 𝘄𝗵𝗮𝘁 𝗴𝗲𝘁𝘀 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 ❖\n"
    f"➻ 𝘂𝘀𝗲𝗿 𝗷𝗼𝗶𝗻𝗲𝗱 𝘁𝗵𝗲 𝗴𝗿𝗼𝘂𝗽\n"
    f"➻ 𝘂𝘀𝗲𝗿 𝗹𝗲𝗳𝘁 𝘁𝗵𝗲 𝗴𝗿𝗼𝘂𝗽\n"
    f"➻ 𝘂𝘀𝗲𝗿 𝘄𝗮𝘀 𝗿𝗲𝗺𝗼𝘃𝗲𝗱\n"
    f"➻ 𝗴𝗿𝗼𝘂𝗽 𝘁𝗶𝘁𝗹𝗲 𝗰𝗵𝗮𝗻𝗴𝗲𝗱\n"
    f"➻ 𝗴𝗿𝗼𝘂𝗽 𝗽𝗵𝗼𝘁𝗼 𝗰𝗵𝗮𝗻𝗴𝗲𝗱\n"
    f"➻ 𝗽𝗶𝗻𝗻𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀\n"
    f"➻ 𝘃𝗶𝗱𝗲𝗼 𝗰𝗵𝗮𝘁 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 / 𝗲𝗻𝗱𝗲𝗱\n\n"
    
    f"👮 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀."
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
