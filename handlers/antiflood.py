# ============================================================
# Group Manager Bot — Anti Flood (Spam Protection)
# Author: Mr. Stark
# ============================================================
from pyrogram import enums
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import asyncio
import re
import time
import logging
import db

logger = logging.getLogger(__name__)

# (chat_id, user_id) -> list of (timestamp, text)
_flood_tracker: dict = {}

FLOOD_WINDOW = 10  # seconds


async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


def parse_flood_time(text: str):
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


def fmt_flood_time(seconds: int) -> str:
    if seconds == 0:
        return "∞ (ᴜɴᴛɪʟ ᴀᴅᴍɪɴ ᴜɴᴍᴜᴛᴇꜱ)"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    return f"{seconds // 3600}h"


ANTIFLOOD_HELP_TEXT = (
    f"<blockquote>🌊 <b>𝖠𝗇𝗍𝗂 𝖥𝗅𝗈𝗈𝖽 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
    f"𝖴𝗌𝖾𝗋𝗌 𝖶𝗁𝗈 𝖲𝖾𝗇𝖽 𝖳𝗈𝗈 𝖬𝖺𝗇𝗒\n"
    f"𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖨𝗇 10 𝖲𝖾𝖼𝗈𝗇𝖽𝗌 𝖠𝗋𝖾\n"
    f"𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖠𝖼𝗍𝗂𝗈𝗇𝖾𝖽.\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/antiflood on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 ✅\n"
    f"➻ <code>/antiflood off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 ❌\n"
    f"➻ <code>/setflood {{number}}</code> — 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖯𝖾𝗋 10𝗌\n"
    f"➻ <code>/floodaction {{mute/kick/ban/warn}}</code> — 𝖠𝖼𝗍𝗂𝗈𝗇 𝖳𝗈 𝖳𝖺𝗄𝖾\n"
    f"➻ <code>/floodtime {{time}}</code> — 𝖬𝗎𝗍𝖾/𝖡𝖺𝗇 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇\n"  
    f"➻ <code>/floodmode {{strict/normal}}</code> — 𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇 𝖬𝗈𝖽𝖾\n"
    f"➻ <code>/flood</code> — 𝖵𝗂𝖾𝗐 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌\n"
    f"➻ <code>/floodwhitelist {{add/remove/list}}</code> — 𝖤𝗑𝖾𝗆𝗉𝗍 𝖴𝗌𝖾𝗋𝗌\n\n"
    f"<blockquote expandable>❖ <b>𝖬𝗈𝖽𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖭𝗈𝗋𝗆𝖺𝗅 — 𝖠𝗇𝗒 𝖱𝖺𝗉𝗂𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖢𝗈𝗎𝗇𝗍\n"
    f"➻ 𝖲𝗍𝗋𝗂𝖼𝗍 — 𝖮𝗇𝗅𝗒 𝖱𝖾𝗉𝖾𝖺𝗍𝖾𝖽/𝖲𝖺𝗆𝖾 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖢𝗈𝗎𝗇𝗍\n\n"
    f"<i>👮 𝖮𝗇𝗅𝗒 𝖠𝖽𝗆𝗂𝗇𝗌 𝖢𝖺𝗇 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖳𝗁𝗂𝗌</i>"
)

async def _take_flood_action(client, chat_id: int, user_id: int, action: str, mute_time: int):
    try:
        if action == "ban":
            await client.ban_chat_member(chat_id, user_id)
        elif action == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        elif action == "mute":
            await client.restrict_chat_member(
                chat_id, user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            if mute_time > 0:
                asyncio.get_event_loop().create_task(
                    _auto_unmute(client, chat_id, user_id, mute_time)
                )
        elif action == "warn":
            count = await db.add_warn(chat_id, user_id, "ꜰʟᴏᴏᴅɪɴɢ / ꜱᴘᴀᴍᴍɪɴɢ")
            limit = await db.get_warn_limit(chat_id)
            if count >= limit:
                warn_action = await db.get_warn_action(chat_id)
                await _take_flood_action(client, chat_id, user_id, warn_action, mute_time)
    except Exception as e:
        logger.error(f"ᴀɴᴛɪ ꜰʟᴏᴏᴅ ᴀᴄᴛɪᴏɴ ᴇʀʀᴏʀ ({action}): {e}")


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
        logger.error(f"ᴀɴᴛɪ ꜰʟᴏᴏᴅ ᴀᴜᴛᴏ ᴜɴᴍᴜᴛᴇ ᴇʀʀᴏʀ: {e}")


def register_antiflood_handler(app: Client):

    # ==========================================================
    # /antiflood on|off
    # ==========================================================
    @app.on_message(filters.group & filters.command("antiflood"))
    async def antiflood_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            return await message.reply_text(ANTIFLOOD_HELP_TEXT, parse_mode=enums.ParseMode.HTML)

        status = parts[1].lower() == "on"
        await db.set_antiflood_status(message.chat.id, status)

        if status:
            limit = await db.get_flood_limit(message.chat.id)
            await message.reply_text(
                f"✅ 𝗔𝗻𝘁𝗶 𝗙𝗹𝗼𝗼𝗱 𝗢𝗡!\n\n"
                f"ʟɪᴍɪᴛ: <code>{limit} ᴍꜱɢ / 10ꜱ</code>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text("⚠️ 𝗔𝗻𝘁𝗶 𝗙𝗹𝗼𝗼𝗱 𝗢𝗙𝗙!", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # /setflood <number>
    # ==========================================================
    @app.on_message(filters.group & filters.command("setflood"))
    async def setflood_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            limit = await db.get_flood_limit(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/setflood &lt;ɴᴜᴍʙᴇʀ&gt;</code>\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ ʟɪᴍɪᴛ: <code>{limit} ᴍꜱɢ / 10ꜱ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        limit = int(parts[1].strip())
        if limit < 2 or limit > 50:
            return await message.reply_text(
                "⚠️ ʟɪᴍɪᴛ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ <code>2</code> ᴀɴᴅ <code>50</code>.",
                parse_mode=enums.ParseMode.HTML
            )

        await db.set_flood_limit(message.chat.id, limit)
        await message.reply_text(
            f"✅ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ꜱᴇᴛ ᴛᴏ <code>{limit} ᴍꜱɢ / 10ꜱ</code>.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /floodaction <mute/kick/ban/warn>
    # ==========================================================
    @app.on_message(filters.group & filters.command("floodaction"))
    async def floodaction_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        valid = ["mute", "kick", "ban", "warn"]
        if len(parts) < 2 or parts[1].lower() not in valid:
            action = await db.get_flood_action(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/floodaction &lt;mute/kick/ban/warn&gt;</code>\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ ᴀᴄᴛɪᴏɴ: <code>{action}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        action = parts[1].lower()
        await db.set_flood_action(message.chat.id, action)
        await message.reply_text(
            f"✅ ꜰʟᴏᴏᴅ ᴀᴄᴛɪᴏɴ ꜱᴇᴛ ᴛᴏ <code>{action}</code>.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /floodtime <time>
    # ==========================================================
    @app.on_message(filters.group & filters.command("floodtime"))
    async def floodtime_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            t = await db.get_flood_time(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/floodtime &lt;ᴛɪᴍᴇ&gt;</code>\n\n"
                f"ᴇxᴀᴍᴘʟᴇꜱ: <code>30ꜱ</code> <code>5ᴍ</code> <code>1ʜ</code> <code>0</code>\n"
                f"⏱ ᴄᴜʀʀᴇɴᴛ: <code>{fmt_flood_time(t)}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        seconds = parse_flood_time(parts[1])
        if seconds is None:
            return await message.reply_text(
                "⚠️ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁!\n\n"
                "• ꜱᴇᴄᴏɴᴅꜱ: <code>1ꜱ</code> – <code>60ꜱ</code>\n"
                "• ᴍɪɴᴜᴛᴇꜱ: <code>1ᴍ</code> – <code>60ᴍ</code>\n"
                "• ʜᴏᴜʀꜱ:   <code>1ʜ</code> – <code>24ʜ</code>\n"
                "• <code>0</code> = ᴘᴇʀᴍᴀɴᴇɴᴛ",
                parse_mode=enums.ParseMode.HTML
            )

        await db.set_flood_time(message.chat.id, seconds)
        await message.reply_text(
            f"✅ ꜰʟᴏᴏᴅ ᴍᴜᴛᴇ/ʙᴀɴ ᴅᴜʀᴀᴛɪᴏɴ ꜱᴇᴛ ᴛᴏ <code>{fmt_flood_time(seconds)}</code>.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /floodmode <strict/normal>
    # ==========================================================
    @app.on_message(filters.group & filters.command("floodmode"))
    async def floodmode_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["strict", "normal"]:
            mode = await db.get_flood_mode(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/floodmode &lt;strict/normal&gt;</code>\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ ᴍᴏᴅᴇ: <code>{mode}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        mode = parts[1].lower()
        await db.set_flood_mode(message.chat.id, mode)
        await message.reply_text(
            f"✅ ꜰʟᴏᴏᴅ ᴍᴏᴅᴇ ꜱᴇᴛ ᴛᴏ <code>{mode}</code>.",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /flood — show current settings
    # ==========================================================
    @app.on_message(filters.group & filters.command("flood"))
    async def flood_status_cmd(client, message: Message):
        status = await db.get_antiflood_status(message.chat.id)
        limit = await db.get_flood_limit(message.chat.id)
        action = await db.get_flood_action(message.chat.id)
        t = await db.get_flood_time(message.chat.id)
        mode = await db.get_flood_mode(message.chat.id)
        whitelist = await db.get_flood_whitelist(message.chat.id)
        current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"

        await message.reply_text(
            f"╔══════════════════╗\n"
            f".   🌊 𝗔𝗻𝘁𝗶 𝗙𝗹𝗼𝗼𝗱 𝗦𝘁𝗮𝘁𝘂𝘀\n"
            f"╚══════════════════╝\n\n"
            f"📊 ꜱᴛᴀᴛᴜꜱ: {current}\n"
            f"🔢 ʟɪᴍɪᴛ: <code>{limit} ᴍꜱɢ / 10ꜱ</code>\n"
            f"⚡ ᴀᴄᴛɪᴏɴ: <code>{action}</code>\n"
            f"⏱ ᴅᴜʀᴀᴛɪᴏɴ: <code>{fmt_flood_time(t)}</code>\n"
            f"🎯 ᴍᴏᴅᴇ: <code>{mode}</code>\n"
            f"📋 ᴡʜɪᴛᴇʟɪꜱᴛᴇᴅ: <code>{len(whitelist)} ᴜꜱᴇʀ(ꜱ)</code>",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /floodwhitelist add|remove|list <user>
    # ==========================================================
    @app.on_message(filters.group & filters.command("floodwhitelist"))
    async def floodwhitelist_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=2)
        if len(parts) < 2 or parts[1].lower() not in ["add", "remove", "list"]:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/floodwhitelist add/remove &lt;ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇʀ&gt;</code>\n"
                "ᴏʀ: <code>/floodwhitelist list</code>",
                parse_mode=enums.ParseMode.HTML
            )

        sub = parts[1].lower()

        if sub == "list":
            whitelist = await db.get_flood_whitelist(message.chat.id)
            if not whitelist:
                return await message.reply_text("📋 ɴᴏ ᴜꜱᴇʀꜱ ᴡʜɪᴛᴇʟɪꜱᴛᴇᴅ ʏᴇᴛ.", parse_mode=enums.ParseMode.HTML)
            text = "\n".join([f"• <code>{uid}</code>" for uid in whitelist])
            return await message.reply_text(f"📋 𝗪𝗵𝗶𝘁𝗲𝗹𝗶𝘀𝘁𝗲𝗱 𝗨𝘀𝗲𝗿𝘀\n\n{text}", parse_mode=enums.ParseMode.HTML)

        target = None
        if message.reply_to_message and message.reply_to_message.from_user:
            target = message.reply_to_message.from_user
        elif len(parts) >= 3:
            arg = parts[2].strip()
            try:
                target = await client.get_users(int(arg) if arg.lstrip("-").isdigit() else arg)
            except Exception:
                target = None

        if not target:
            return await message.reply_text(
                "❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇɪʀ ᴜꜱᴇʀɴᴀᴍᴇ/ID.",
                parse_mode=enums.ParseMode.HTML
            )

        if sub == "add":
            await db.add_flood_whitelist(message.chat.id, target.id)
            await message.reply_text(
                f"✅ {target.mention} ᴀᴅᴅᴇᴅ ᴛᴏ ꜰʟᴏᴏᴅ ᴡʜɪᴛᴇʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await db.remove_flood_whitelist(message.chat.id, target.id)
            await message.reply_text(
                f"✅ {target.mention} ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ꜰʟᴏᴏᴅ ᴡʜɪᴛᴇʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )


    # ==========================================================
    # 🔍 Flood Detector — runs on every group message
    # ==========================================================
    @app.on_message(filters.group & ~filters.service, group=3)
    async def flood_detector(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        if not await db.get_antiflood_status(chat_id):
            return

        if message.from_user.is_bot:
            return

        if await is_power(client, chat_id, user_id):
            return

        whitelist = await db.get_flood_whitelist(chat_id)
        if user_id in whitelist:
            return

        mode = await db.get_flood_mode(chat_id)
        limit = await db.get_flood_limit(chat_id)
        now = time.time()
        text = message.text or message.caption or ""

        key = (chat_id, user_id)
        entries = _flood_tracker.get(key, [])
        entries = [e for e in entries if now - e[0] <= FLOOD_WINDOW]
        entries.append((now, text))
        _flood_tracker[key] = entries

        if mode == "strict":
            count = sum(1 for e in entries if e[1] == text and text != "")
        else:
            count = len(entries)

        if count > limit:
            _flood_tracker[key] = []
            action = await db.get_flood_action(chat_id)
            mute_time = await db.get_flood_time(chat_id)

            try:
                await client.delete_messages(chat_id, [message.id])
            except Exception:
                pass

            await _take_flood_action(client, chat_id, user_id, action, mute_time)

            try:
                await message.reply_text(
                    f"🌊 {message.from_user.mention} ɪꜱ ꜰʟᴏᴏᴅɪɴɢ ᴛʜᴇ ᴄʜᴀᴛ!\n"
                    f"⚡ ᴀᴄᴛɪᴏɴ ᴛᴀᴋᴇɴ: <code>{action}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                pass
