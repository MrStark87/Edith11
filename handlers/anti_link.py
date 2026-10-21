# ============================================================
# Group Manager Bot — Anti Link System (Strict Matching + Remove Feature)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import db
import logging
import asyncio
import re

logger = logging.getLogger(__name__)

ANTI_LINK_HELP_TEXT = (
    f"<blockquote>🔗 <b>𝖠𝗇𝗍𝗂 𝖫𝗂𝗇𝗄 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖬𝖺𝗂𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/nolink on</code> — 𝖡𝗅𝗈𝖼𝗄 𝖠𝗅𝗅 𝖫𝗂𝗇𝗄𝗌 ❌\n"
    f"➻ <code>/nolink off</code> — 𝖠𝗅𝗅𝗈𝗐 𝖠𝗅𝗅 𝖫𝗂𝗇𝗄𝗌 ✅\n\n"
    f"<blockquote expandable>❖ <b>𝖶𝗁𝗂𝗍𝖾𝗅𝗂𝗌𝗍 / 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍</b> ❖</blockquote>\n"
    f"➻ <code>/allowlink {{url}}</code> — 𝖠𝗅𝗅𝗈𝗐 𝖲𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖫𝗂𝗇𝗄\n"
    f"➻ <code>/rmallowlink {{url}}</code> — 𝖱𝖾𝗆𝗈𝗏𝖾 𝖥𝗋𝗈𝗆 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖫𝗂𝗌𝗍\n"
    f"➻ <code>/blocklink {{url}}</code> — 𝖡𝗅𝗈𝖼𝗄 𝖲𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖫𝗂𝗇𝗄\n"
    f"➻ <code>/rmblocklink {{url}}</code> — 𝖱𝖾𝗆𝗈𝗏𝖾 𝖥𝗋𝗈𝗆 𝖡𝗅𝗈𝖼𝗄𝖾𝖽 𝖫𝗂𝗌𝗍\n"
    f"➻ <code>/allowedlinks</code> — 𝖫𝗂𝗌𝗍 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖫𝗂𝗇𝗄𝗌\n"
    f"➻ <code>/blockedlinks</code> — 𝖫𝗂𝗌𝗍 𝖡𝗅𝗈𝖼𝗄𝖾𝖽 𝖫𝗂𝗇𝗄𝗌\n\n"
    f"<blockquote expandable>❖ <b>𝖶𝖺𝗋𝗇 𝖲𝗒𝗌𝗍𝖾𝗆</b> ❖</blockquote>\n"
    f"➻ <code>/linkwarn on</code> — 𝖶𝖺𝗋𝗇 + 𝖠𝖼𝗍𝗂𝗈𝗇 𝖮𝗇 𝖫𝗂𝗆𝗂𝗍\n"
    f"➻ <code>/linkwarn off</code> — 𝖮𝗇𝗅𝗒 𝖣𝖾𝗅𝖾𝗍𝖾 + 𝖭𝗈𝗍𝗂𝖿𝗒\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖠𝖽𝗆𝗂𝗇𝗌 𝖠𝗋𝖾 𝖭𝗈𝗍 𝖠𝖿𝖿𝖾𝖼𝗍𝖾𝖽\n"
    f"➻ 𝖳𝖦 𝖫𝗂𝗇𝗄𝗌 𝖬𝖺𝗍𝖼𝗁 𝖲𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾𝗌!"
)

URL_RE = re.compile(
    r'(?:https?://|www\.)'
    r'(?:[a-zA-Z0-9\-]+\.)*'
    r'[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}'
    r'(?:[^\s]*)?',
    re.IGNORECASE
)

TGLINK_RE = re.compile(r't\.me/\S+|telegram\.me/\S+', re.IGNORECASE)


def _extract_urls(text: str) -> list:
    urls = URL_RE.findall(text or "")
    urls += TGLINK_RE.findall(text or "")
    return [u.lower().strip(".,)>") for u in urls]


def _clean_url_for_db(url: str) -> str:
    url = url.lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    
    if url.startswith('t.me/') or url.startswith('telegram.me/'):
        cleaned = url.split('?')[0].split('#')[0]
        return cleaned.strip('/')
    
    domain = url.split('/')[0].split('?')[0].split('#')[0]
    return domain.strip()


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def _take_action(client, chat_id: int, user_id: int, action: str):
    try:
        if action == "ban":
            await client.ban_chat_member(chat_id, user_id)
        elif action == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        else:
            await client.restrict_chat_member(
                chat_id, user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
    except Exception as e:
        logger.error(f"ᴀɴᴛɪ-ʟɪɴᴋ ᴀᴄᴛɪᴏɴ ᴇʀʀᴏʀ: {e}")


async def _del_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


def register_anti_link_handler(app: Client):

    # ----------------------------------------------------------
    # /nolink on|off
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("nolink"), group=-2)
    async def nolink_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts   = message.text.split(maxsplit=1)
        chat_id = message.chat.id

        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            try:
                status  = await db.get_nolink_status(chat_id)
                warn_on = await db.get_linkwarn_status(chat_id)
            except Exception:
                status, warn_on = False, False
                
            cur     = "🟢 ᴏɴ (ʙʟᴏᴄᴋɪɴɢ)" if status else "🔴 ᴏꜰꜰ (ᴀʟʟᴏᴡᴇᴅ)"
            warn_s  = "⚠️ ᴏɴ" if warn_on else "🗑 ᴏꜰꜰ (ᴅᴇʟᴇᴛᴇ ᴏɴʟʏ)"
            return await message.reply_text(
                f"⚙️ <u>𝗔𝗻𝘁𝗶-𝗟𝗶𝗻𝗸 𝗦𝘆𝘀𝘁𝗲𝗺</u>\n\n"
                f"ꜱᴛᴀᴛᴜꜱ: {cur}\n"
                f"ᴡᴀʀɴ: {warn_s}\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/nolink ᴏɴ</code> ᴏʀ <code>/nolink ᴏꜰꜰ</code>"
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        try:
            await db.set_nolink_status(chat_id, status)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        if status:
            try:
                warn_on    = await db.get_linkwarn_status(chat_id)
                warn_limit = await db.get_warn_limit(chat_id)
                action     = await db.get_warn_action(chat_id)
            except Exception:
                warn_on, warn_limit, action = False, 3, "mute"

            await message.reply_text(
                f"🚫 <u>𝗔𝗻𝘁𝗶-𝗟𝗶𝗻𝗸 𝗢𝗡!</u>\n\n"
                f"ᴀʟʟ ʟɪɴᴋꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.\n"
                f"ᴡᴀʀɴ: {'✅ ᴏɴ — ᴀᴄᴛɪᴏɴ ᴀꜰᴛᴇʀ ' + str(warn_limit) + ' ᴡᴀʀɴꜱ: ' + action if warn_on else '❌ ᴏꜰꜰ (ꜱɪʟᴇɴᴛ ᴅᴇʟᴇᴛᴇ + ɴᴏᴛɪꜰʏ)'}\n\n"
                f"ᴜꜱᴇ /allowlink ᴛᴏ ᴡʜɪᴛᴇʟɪꜱᴛ ꜱᴘᴇᴄɪꜰɪᴄ ᴅᴏᴍᴀɪɴꜱ ᴏʀ ʟɪɴᴋꜱ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "✅ 𝗔𝗻𝘁𝗶-𝗟𝗶𝗻𝗸 𝗢𝗙𝗙. ᴀʟʟ ʟɪɴᴋꜱ ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /linkwarn on|off
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("linkwarn"), group=-2)
    async def linkwarn_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts   = message.text.split(maxsplit=1)
        chat_id = message.chat.id

        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            try:
                status = await db.get_linkwarn_status(chat_id)
            except Exception:
                status = False
            cur    = "⚠️ ᴏɴ" if status else "🗑 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ <u>𝗟𝗶𝗻𝗸 𝗪𝗮𝗿𝗻</u>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ: {cur}\n\n"
                f"• 𝗼𝗻 — ᴅᴇʟᴇᴛᴇ + ᴡᴀʀɴ, ᴀᴄᴛɪᴏɴ ᴏɴ ʟɪᴍɪᴛ\n"
                f"• 𝗼𝗳𝗳 — ᴅᴇʟᴇᴛᴇ + ɴᴏᴛɪꜰʏ ᴏɴʟʏ (ɴᴏ ᴡᴀʀɴꜱ)\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/linkwarn ᴏɴ</code> ᴏʀ <code>/linkwarn ᴏꜰꜰ</code>"
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        try:
            await db.set_linkwarn_status(chat_id, status)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        if status:
            try:
                limit  = await db.get_warn_limit(chat_id)
                action = await db.get_warn_action(chat_id)
            except Exception:
                limit = 3
                action = "mute"
                
            await message.reply_text(
                f"⚠️ <u>𝗟𝗶𝗻𝗸 𝗪𝗮𝗿𝗻 𝗢𝗡!</u>\n\n"
                f"ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ ᴡᴀʀɴᴇᴅ ꜰᴏʀ ꜱᴇɴᴅɪɴɢ ʟɪɴᴋꜱ.\n"
                f"ᴀᴄᴛɪᴏɴ ᴀꜰᴛᴇʀ {limit} ᴡᴀʀɴꜱ: {action}\n\n"
                f"ᴄʜᴀɴɢᴇ ᴡɪᴛʜ /setwarnlimit ᴀɴᴅ /setwarnaction."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "🗑 𝗟𝗶𝗻𝗸 𝗪𝗮𝗿𝗻 𝗢𝗙𝗙.\n\nʟɪɴᴋꜱ ᴡɪʟʟ ʙᴇ ꜱɪʟᴇɴᴛʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜ ᴀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ᴏɴʟʏ.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /allowlink {url}
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("allowlink"), group=-2)
    async def allowlink_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/allowlink ʜᴛᴛᴘꜱ://t.ᴍᴇ/CarelessxWorld</code>",
                parse_mode=enums.ParseMode.HTML
            )

        raw    = parts[1].strip()
        target = _clean_url_for_db(raw)

        if not target:
            return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ᴜʀʟ/link.")

        try:
            await db.add_allowed_link(message.chat.id, target)
            await db.remove_blocked_link(message.chat.id, target)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        await message.reply_text(
            f"✅ <code>{target}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ᴀʟʟᴏᴡᴇᴅ ʟɪꜱᴛ.\n"
            f"ᴍᴇꜱꜱᴀɢᴇꜱ ᴍᴀᴛᴄʜɪɴɢ ᴛʜɪꜱ ᴇxᴀᴄᴛ ᴘᴀᴛʜ ᴡᴏɴ'ᴛ ʙᴇ ʙʟᴏᴄᴋᴇᴅ."
            f"",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # 🔥 /rmallowlink {url} — ALLOWED LIST SE HATANE KE LIYE
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("rmallowlink"), group=-2)
    async def rmallowlink_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/rmallowlink ʜᴛᴛᴘꜱ://t.ᴍᴇ/CarelessxWorld</code>",
                parse_mode=enums.ParseMode.HTML
            )

        raw    = parts[1].strip()
        target = _clean_url_for_db(raw)

        try:
            await db.remove_allowed_link(message.chat.id, target)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        await message.reply_text(
            f"🗑 <code>{target}</code> ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀʟʟᴏᴡᴇᴅ ʟɪꜱᴛ."
            f"",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # /blocklink {url}
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("blocklink"), group=-2)
    async def blocklink_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/blocklink ᴄᴀꜱɪɴᴏ.ᴄᴏᴍ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        raw    = parts[1].strip()
        target = _clean_url_for_db(raw)

        if not target:
            return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ᴜʀʟ/link.")

        try:
            await db.add_blocked_link(message.chat.id, target)
            await db.remove_allowed_link(message.chat.id, target)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        await message.reply_text(
            f"🚫 <code>{target}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴏᴄᴋᴇᴅ ʟɪꜱᴛ.\n"
            f"ᴍᴇꜱꜱᴀɢᴇꜱ ᴍᴀᴛᴄʜɪɴɢ ᴛʜɪꜱ ᴇxᴀᴄᴛ ᴘᴀᴛʜ ᴡɪʟʟ ᴀʟᴡᴀʏꜱ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ."
            f"",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # 🔥 /rmblocklink {url} — BLOCKED LIST SE HATANE KE LIYE
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("rmblocklink"), group=-2)
    async def rmblocklink_cmd(client, message: Message):
        if not await _is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/rmblocklink ᴄᴀꜱɪɴᴏ.ᴄᴏᴍ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        raw    = parts[1].strip()
        target = _clean_url_for_db(raw)

        try:
            await db.remove_blocked_link(message.chat.id, target)
        except Exception as e:
            return await message.reply_text(f"❌ ᴅʙ ᴇʀʀᴏʀ: {e}")

        await message.reply_text(
            f"🗑 <code>{target}</code> ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙʟᴏᴄᴋᴇᴅ ʟɪꜱᴛ."
            f"",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # /allowedlinks
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("allowedlinks"), group=-2)
    async def allowedlinks_cmd(client, message: Message):
        try:
            domains = await db.get_allowed_links(message.chat.id)
        except Exception:
            domains = []
            
        if not domains:
            return await message.reply_text("📭 ɴᴏ ʟɪɴᴋꜱ ɪɴ ᴛʜᴇ ᴀʟʟᴏᴡᴇᴅ ʟɪꜱᴛ.")

        text = (
            f"✅ 𝗔𝗹𝗹𝗼𝘄𝗲𝗱 𝗟𝗶𝗻𝗸𝘀/Domains — {message.chat.title}\n\n"
            + "\n".join(f"• <code>{d}</code>" for d in sorted(domains))
            + "\n\nᴛʜᴇꜱᴇ ᴀʀᴇ ᴡʜɪᴛᴇʟɪꜱᴛᴇᴅ ᴇᴠᴇɴ ᴡʜᴇɴ /nolink ɪꜱ ᴏɴ."
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /blockedlinks
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("blockedlinks"), group=-2)
    async def blockedlinks_cmd(client, message: Message):
        try:
            domains = await db.get_blocked_links(message.chat.id)
        except Exception:
            domains = []
            
        if not domains:
            return await message.reply_text("📭 ɴᴏ ʟɪɴᴋꜱ ɪɴ ᴛʜᴇ ʙʟᴏᴄᴋᴇᴅ ʟɪꜱᴛ.")

        text = (
            f"🚫 𝗕𝗹𝗼𝗰𝗸𝗲𝗱 𝗟𝗶𝗻𝗸𝘀/Domains — {message.chat.title}\n\n"
            + "\n".join(f"• <code>{d}</code>" for d in sorted(domains))
            + "\n\nᴛʜᴇꜱᴇ ᴀʀᴇ ᴀʟᴡᴀʏꜱ ʙʟᴏᴄᴋᴇᴅ ᴇᴠᴇɴ ᴡʜᴇɴ /nolink ɪꜱ ᴏꜰꜰ."
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # Enforcer (Priority Group=9 to catch links)
    # ----------------------------------------------------------
    @app.on_message(filters.group & (filters.text | filters.caption), group=9)
    async def enforce_anti_link(client, message: Message):
        if not message.from_user:
            return

        if await _is_admin(client, message.chat.id, message.from_user.id):
            return

        text    = message.text or message.caption or ""
        chat_id = message.chat.id

        urls = _extract_urls(text)

        entities = message.entities or message.caption_entities or []
        for ent in entities:
            if ent.type.name == "TEXT_LINK" and ent.url:
                urls.append(ent.url.lower())

        if not urls:
            return

        try:
            nolink_on       = await db.get_nolink_status(chat_id)
            allowed_domains = await db.get_allowed_links(chat_id)
            blocked_domains = await db.get_blocked_links(chat_id)
        except Exception:
            nolink_on, allowed_domains, blocked_domains = False, [], []

        should_delete = False
        matched_item = None

        for url in urls:
            current_clean = _clean_url_for_db(url)

            if any(current_clean == b or current_clean.startswith(b + '/') or (not current_clean.startswith('t.me') and current_clean.endswith('.' + b)) for b in blocked_domains):
                should_delete = True
                matched_item = current_clean
                break

            if nolink_on:
                if any(current_clean == a or current_clean.startswith(a + '/') for a in allowed_domains):
                    continue
                should_delete = True
                matched_item = current_clean
                break

        if not should_delete:
            return

        try:
            await message.delete()
        except Exception:
            pass

        user = message.from_user
        try:
            warn_on = await db.get_linkwarn_status(chat_id)
        except Exception:
            warn_on = False

        if warn_on:
            try:
                warn_limit  = await db.get_warn_limit(chat_id)
                warn_action = await db.get_warn_action(chat_id)
            except Exception:
                warn_limit = 3
                warn_action = "mute"

            try:
                warns = await db.add_warn(chat_id, user.id, reason=f"ꜱᴇɴᴛ ʟɪɴᴋ: {matched_item or 'forbidden'}")
            except Exception:
                warns = 1

            if warns >= warn_limit:
                try:
                    await db.reset_warns(chat_id, user.id)
                except Exception:
                    pass
                await _take_action(client, chat_id, user.id, warn_action)
                action_emoji = {"ban": "🚫", "kick": "👢", "mute": "🔇"}.get(warn_action, "🚫")
                warn_msg = await client.send_message(
                    chat_id,
                    f"{action_emoji} {user.mention} ᴋᴇᴘᴛ ꜱᴇɴᴅɪɴɢ ʟɪɴᴋꜱ ᴀɴᴅ ᴡᴀꜱ "
                    f"{warn_action}ᴅ! ({warn_limit}/{warn_limit} ᴡᴀʀɴꜱ)",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                warn_msg = await client.send_message(
                    chat_id,
                    f"⚠️ {user.mention}, ʟɪɴᴋꜱ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ!\n"
                    f"ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ. ᴡᴀʀɴ: {warns}/{warn_limit}"
                    f"",
                    parse_mode=enums.ParseMode.HTML
                )
        else:
            warn_msg = await client.send_message(
                chat_id,
                f"🔗 {user.mention}, ʟɪɴᴋꜱ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ!\n"
                f"ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴅᴇʟᴇᴛᴇᴅ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        asyncio.get_event_loop().create_task(_del_after(warn_msg, 30))
        
