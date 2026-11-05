# ============================================================
# Group Manager Bot — Disable Commands (Member-Only)
# Author: Mr. Stark
# ============================================================

# Yaha enums ko import kiya gaya hai aapke mutabik
from pyrogram import Client, filters, enums, StopPropagation
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import asyncio
import logging
import db

logger = logging.getLogger(__name__)

# ==========================================================
# Only these commands can be disabled — all of these are
# usable by regular members. Admin/config commands are
# NEVER included here, so they can never be disabled.
# ==========================================================

# Yaha "info" command ko add kar diya gaya hai
DISABLEABLE_COMMANDS = [
    "rules",
    "notes",
    "id",
    "chatinfo",
    "info",
    "report",
    "fsublist",
    "filters",
    "blacklist",
    "ai",
    "ask",
]


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


async def _delete_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


DISABLE_HELP_TEXT = (
    f"<blockquote>🚫 <b>𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b></blockquote>\n\n"
    f"❖ 𝖡𝗅𝗈𝖼𝗄 𝖱𝖾𝗀𝗎𝗅𝖺𝗋 𝖬𝖾𝗆𝖻𝖾𝗋𝗌 𝖥𝗋𝗈𝗆 𝖴𝗌𝗂𝗇𝗀\n"
    f"𝖲𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖬𝖾𝗆𝖻𝖾𝗋-𝖴𝗌𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌.\n"
    f"𝖠𝖽𝗆𝗂𝗇𝗌 𝖠𝗋𝖾 𝖭𝖾𝗏𝖾𝗋 𝖠𝖿𝖿𝖾𝖼𝗍𝖾𝖽.\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/disable &lt;command&gt;</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖥𝗈𝗋 𝖬𝖾𝗆𝖻𝖾𝗋𝗌\n"
    f"➻ <code>/enable &lt;command&gt;</code> — 𝖱𝖾-𝖤𝗇𝖺𝖻𝗅𝖾 𝖠 𝖢𝗈𝗆𝗆𝖺𝗇𝖽\n"
    f"➻ <code>/disabled</code> — 𝖫𝗂𝗌𝗍 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌\n\n"
    f"<blockquote expandable>❖ <b>𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    + ", ".join(f"<code>{c}</code>" for c in DISABLEABLE_COMMANDS) +
    "\n\n"
    f"<i>👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌.</i>"
)

def register_disable_handler(app: Client):

    # ==========================================================
    # /disable <command>
    # ==========================================================

    @app.on_message(filters.group & filters.command("disable"))
    async def disable_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/disable &lt;ᴄᴏᴍᴍᴀɴᴅ&gt;</code>\n\n"
                "𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗮𝗯𝗹𝗲: " + ", ".join(f"<code>{c}</code>" for c in DISABLEABLE_COMMANDS),
                parse_mode=enums.ParseMode.HTML
            )

        cmd = parts[1].strip().lower().lstrip("/")

        if cmd not in DISABLEABLE_COMMANDS:
            return await message.reply_text(
                f"⚠️ <code>{cmd}</code> ᴄᴀɴɴᴏᴛ ʙᴇ ᴅɪꜱᴀʙʟᴇᴅ.\n\n"
                f"ᴏɴʟʏ ᴍᴇᴍʙᴇʀ-ᴜꜱᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ᴄᴀɴ ʙᴇ ᴅɪꜱᴀʙʟᴇᴅ:\n"
                + ", ".join(f"<code>{c}</code>" for c in DISABLEABLE_COMMANDS),
                parse_mode=enums.ParseMode.HTML
            )

        disabled = await db.get_disabled_commands(message.chat.id)
        if cmd in disabled:
            return await message.reply_text(
                f"⚠️ <code>{cmd}</code> ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴅɪꜱᴀʙʟᴇᴅ.", parse_mode=enums.ParseMode.HTML
            )

        await db.disable_command(message.chat.id, cmd)
        await message.reply_text(
            f"♿ <code>/{cmd}</code> ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /enable <command>
    # ==========================================================

    @app.on_message(filters.group & filters.command("enable"))
    async def enable_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/enable &lt;ᴄᴏᴍᴍᴀɴᴅ&gt;</code>", parse_mode=enums.ParseMode.HTML
            )

        cmd = parts[1].strip().lower().lstrip("/")
        removed = await db.enable_command(message.chat.id, cmd)

        if removed:
            await message.reply_text(
                f"✅ <code>/{cmd}</code> ʜᴀꜱ ʙᴇᴇɴ ʀᴇ-ᴇɴᴀʙʟᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ <code>{cmd}</code> ᴡᴀꜱ ɴᴏᴛ ᴅɪꜱᴀʙʟᴇᴅ.", parse_mode=enums.ParseMode.HTML
            )


    # ==========================================================
    # /disabled — list disabled commands
    # ==========================================================

    @app.on_message(filters.group & filters.command("disabled"))
    async def disabled_list_cmd(client, message: Message):
        disabled = await db.get_disabled_commands(message.chat.id)

        if not disabled:
            return await message.reply_text(
                "📭 ɴᴏ ᴄᴏᴍᴍᴀɴᴅꜱ ᴀʀᴇ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.", parse_mode=enums.ParseMode.HTML
            )

        text = "♿ 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:\n\n" + "\n".join(
            f"• <code>/{c}</code>" for c in disabled
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Enforcer — runs BEFORE every other handler (group=-3)
    # ==========================================================

    @app.on_message(filters.group & filters.command(DISABLEABLE_COMMANDS), group=-3)
    async def enforce_disabled(client, message: Message):
        if not message.from_user:
            return

        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return  
        except Exception:
            return

        cmd = message.command[0].lower() if message.command else ""
        disabled = await db.get_disabled_commands(message.chat.id)

        if cmd in disabled:
            try:
                await message.delete()
            except Exception:
                pass

            try:
                warn = await client.send_message(
                    message.chat.id,
                    f"🚫 {message.from_user.mention}, ᴛʜᴇ <code>/{cmd}</code> ᴄᴏᴍᴍᴀɴᴅ "
                    f"ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.",
                    parse_mode=enums.ParseMode.HTML
                )
                asyncio.get_event_loop().create_task(_delete_after(warn, 5))
            except Exception as e:
                logger.error(f"ᴅɪꜱᴀʙʟᴇᴅ ɴᴏᴛɪᴄᴇ ᴇʀʀᴏʀ: {e}")

            raise StopPropagation
                
