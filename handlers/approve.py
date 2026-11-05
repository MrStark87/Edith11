# ============================================================
# Group Manager Bot — Approve / Free Users
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, StopPropagation
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ParseMode
import logging
import db

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


async def extract_target_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None

    arg = parts[1].strip()
    try:
        if arg.startswith("@"):
            return await client.get_users(arg)
        elif arg.lstrip("-").isdigit():
            return await client.get_users(int(arg))
    except Exception:
        return None
    return None


APPROVE_HELP_TEXT = (
    f"<blockquote>🕊 <b>𝖠𝗉𝗉𝗋𝗈𝗏𝖾 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
    f"𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝖽 𝖴𝗌𝖾𝗋𝗌 𝖠𝗋𝖾 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝗅𝗒 𝖨𝗀𝗇𝗈𝗋𝖾𝖽\n"
    f"𝖡𝗒 𝖤𝗏𝖾𝗋𝗒 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝖾𝖽 𝖡𝗈𝗍 𝖱𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝗂𝗈𝗇\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/free</code> 𝗈𝗋 <code>/approve</code> — 𝖠𝗉𝗉𝗋𝗈𝗏𝖾 𝖠 𝖴𝗌𝖾𝗋\n"
    f"➥ 𝖱𝖾𝗉𝗅𝗒 𝖮𝗋 𝖴𝗌𝖾 <code>@username</code> / <code>ID</code>\n\n"
    f"➻ <code>/unfree</code> 𝗈𝗋 <code>/unapprove</code> — 𝖱𝖾𝗆𝗈𝗏𝖾 𝖴𝗌𝖾𝗋 𝖠𝗉𝗉𝗋𝗈𝗏𝖺𝗅\n\n"
    f"➻ <code>/approved</code> — 𝖫𝗂𝗌𝗍 𝖠𝗅𝗅 𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝖽 𝖴𝗌𝖾𝗋𝗌\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾</b> ❖</blockquote>\n"
    f"<i>👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖠𝗉𝗉𝗋𝗈𝗏𝖾 / 𝖴𝗇𝖺𝗉𝗉𝗋𝗈𝗏𝖾</i>"
)


def register_approve_handler(app: Client):

    # ==========================================================
    # /free or /approve — same action, multiple command names
    # ==========================================================

    @app.on_message(filters.group & filters.command(["free", "approve"]))
    async def approve_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", parse_mode=ParseMode.HTML
            )

        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ <code>/free @ᴜꜱᴇʀ</code>",
                parse_mode=ParseMode.HTML
            )

        already = await db.is_approved(message.chat.id, user.id)
        if already:
            return await message.reply_text(
                f"⚠️ {user.mention} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴘᴘʀᴏᴠᴇᴅ.", parse_mode=ParseMode.HTML
            )

        await db.approve_user(message.chat.id, user.id)
        await message.reply_text(
            f"🕊 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {message.chat.title}!\n"
            f"➻ 𝘁𝗵𝗲𝘆 𝘄𝗶𝗹𝗹 𝗻𝗼𝘄 𝗯𝗲 𝗶𝗴𝗻𝗼𝗿𝗲𝗱 𝗯𝘆 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗲𝗱 𝗮𝗱𝗺𝗶𝗻 𝗮𝗰𝘁𝗶𝗼𝗻𝘀 𝗹𝗶𝗸𝗲. "
            f"ʟᴏᴄᴋꜱ, ʙʟᴏᴄᴋʟɪꜱᴛꜱ, ʙɪᴏʟɪɴᴋ ᴇᴛᴄ."
            f"",
            parse_mode=ParseMode.HTML
        )


    # ==========================================================
    # /unfree or /unapprove — same action, multiple command names
    # ==========================================================

    @app.on_message(filters.group & filters.command(["unfree", "unapprove"]))
    async def unapprove_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", parse_mode=ParseMode.HTML
            )

        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ <code>/unfree @ᴜꜱᴇʀ</code>",
                parse_mode=ParseMode.HTML
            )

        removed = await db.unapprove_user(message.chat.id, user.id)
        if removed:
            await message.reply_text(
                f"🔒 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {message.chat.title}.\n"
                f"➻ 𝗯𝗼𝘁 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗶𝗼𝗻𝘀 𝘄𝗶𝗹𝗹 𝗻𝗼𝘄 𝗮𝗽𝗽𝗹𝘆 𝘁𝗼 𝘁𝗵𝗲𝗺 𝗮𝗴𝗮𝗶𝗻."
                f"",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ {user.mention} ᴡᴀꜱ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.", parse_mode=ParseMode.HTML
            )


    # ==========================================================
    # /approved — list approved users
    # ==========================================================

    @app.on_message(filters.group & filters.command("approved"))
    async def approved_list_cmd(client, message: Message):
        users = await db.get_approved_users(message.chat.id)

        if not users:
            return await message.reply_text(
                "📭 ɴᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.", parse_mode=ParseMode.HTML
            )

        lines = []
        for uid in users:
            try:
                u = await client.get_users(uid)
                lines.append(f"• {u.mention} — <code>{uid}</code>")
            except Exception:
                lines.append(f"• <code>{uid}</code>")

        await message.reply_text(
            "🕊 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗨𝘀𝗲𝗿𝘀:\n\n" + "\n".join(lines),
            parse_mode=ParseMode.HTML
        )


    # ==========================================================
    # Bypass — runs before EVERY other restriction handler.
    # If the sender is approved, stop all further processing
    # so no lock/blacklist/biolink/abuse/cleaner/etc. handler
    # ever gets a chance to touch their message.
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=-5)
    async def bypass_for_approved(client, message: Message):
        if not message.from_user:
            return

        if message.command:
            return  # let bot commands reach their real handlers

        if await db.is_approved(message.chat.id, message.from_user.id):
            raise StopPropagation

