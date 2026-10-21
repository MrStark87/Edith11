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
    f"╔══════════════════╗\n"
    f".   🌊 𝗔𝗻𝘁𝗶 𝗙𝗹𝗼𝗼𝗱\n"
    f"╚══════════════════╝\n\n"

    f"𝘂𝘀𝗲𝗿𝘀 𝘄𝗵𝗼 𝘀𝗲𝗻𝗱 𝘁𝗼𝗼 𝗺𝗮𝗻𝘆\n"
    f"𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗶𝗻 10 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗮𝗿𝗲\n"
    f"𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗮𝗰𝘁𝗶𝗼𝗻𝗲𝗱.\n\n"

    f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    f"➻ /antiflood 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 ✅\n"
    f"➻ /antiflood 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 ❌\n"
    f"➻ /setflood <𝗻𝘂𝗺𝗯𝗲𝗿> — 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗽𝗲𝗿 10𝘀\n"
    f"➻ /floodaction <𝗺𝘂𝘁𝗲/𝗸𝗶𝗰𝗸/𝗯𝗮𝗻/𝘄𝗮𝗿𝗻> — 𝗮𝗰𝘁𝗶𝗼𝗻 𝘁𝗼 𝘁𝗮𝗸𝗲\n"
    f"➻ /floodtime <𝘁𝗶𝗺𝗲> — 𝗺𝘂𝘁𝗲/𝗯𝗮𝗻 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻\n"
    f"➻ /floodmode <𝘀𝘁𝗿𝗶𝗰𝘁/𝗻𝗼𝗿𝗺𝗮𝗹> — 𝗱𝗲𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗺𝗼𝗱𝗲\n"
    f"➻ /flood — 𝘃𝗶𝗲𝘄 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝘀𝗲𝘁𝘁𝗶𝗻𝗴𝘀\n"
    f"➻ /floodwhitelist <𝗮𝗱𝗱/𝗿𝗲𝗺𝗼𝘃𝗲/𝗹𝗶𝘀𝘁> — 𝗲𝘅𝗲𝗺𝗽𝘁 𝘂𝘀𝗲𝗿𝘀\n\n"

    f"❖ 𝗺𝗼𝗱𝗲𝘀 ❖\n"
    f"➻ 𝗻𝗼𝗿𝗺𝗮𝗹 — 𝗮𝗻𝘆 𝗿𝗮𝗽𝗶𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗰𝗼𝘂𝗻𝘁\n"
    f"➻ 𝘀𝘁𝗿𝗶𝗰𝘁 — 𝗼𝗻𝗹𝘆 𝗿𝗲𝗽𝗲𝗮𝘁𝗲𝗱/𝘀𝗮𝗺𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗰𝗼𝘂𝗻𝘁\n\n"

    f"<i>👮 𝗼𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝘁𝗵𝗶𝘀</i>"
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
