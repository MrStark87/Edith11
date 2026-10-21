# ============================================================
# Group Manager Bot — Welcome System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    Message, ChatMemberUpdated,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatMemberStatus
import db
import logging
import time
import re

logger = logging.getLogger(__name__)

# ============================================================
# Help text — updated for new system
# ============================================================
WELCOME_HELP_TEXT = (
    "╔══════════════════╗\n"
    "  👋 𝘄𝗲𝗹𝗰𝗼𝗺𝗲 𝘀𝘆𝘀𝘁𝗲𝗺\n"
    "╚══════════════════╝\n\n"

    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /welcome 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 𝘄𝗲𝗹𝗰𝗼𝗺𝗲 ✅\n"
    "➻ /welcome 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝘄𝗲𝗹𝗰𝗼𝗺𝗲 ❌\n"
    "➻ /setwelcome — 𝘀𝗲𝘁𝘂𝗽 𝘃𝗶𝗮 𝗽𝗺 (𝘁𝗲𝘅𝘁+𝗺𝗲𝗱𝗶𝗮+𝗯𝘂𝘁𝘁𝗼𝗻𝘀)\n"
    "➻ /resetwelcome — 𝗿𝗲𝘀𝗲𝘁 𝘁𝗼 𝗱𝗲𝗳𝗮𝘂𝗹𝘁\n"
    "➻ /previewwelcome — 𝗽𝗿𝗲𝘃𝗶𝗲𝘄 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝘄𝗲𝗹𝗰𝗼𝗺𝗲\n\n"

    "❖ 𝗽𝗹𝗮𝗰𝗲𝗵𝗼𝗹𝗱𝗲𝗿𝘀 ❖\n"
    "<code>{id}</code> — 𝘂𝘀𝗲𝗿 𝗶𝗱\n"
    "<code>{name}</code> — 𝗳𝗶𝗿𝘀𝘁 𝗻𝗮𝗺𝗲\n"
    "<code>{surname}</code> — 𝗹𝗮𝘀𝘁 𝗻𝗮𝗺𝗲\n"
    "<code>{namesurname}</code> — 𝗳𝘂𝗹𝗹 𝗻𝗮𝗺𝗲\n"
    "<code>{mention}</code> — 𝗰𝗹𝗶𝗰𝗸𝗮𝗯𝗹𝗲 𝗺𝗲𝗻𝘁𝗶𝗼𝗻\n"
    "<code>{username}</code> — @𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲\n"
    "<code>{groupname}</code> — 𝗴𝗿𝗼𝘂𝗽 𝗻𝗮𝗺𝗲\n\n"

    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ /setwelcome 𝗼𝗽𝗲𝗻𝘀 𝗮 𝗽𝗺 𝘀𝗲𝘁𝘂𝗽 𝗽𝗮𝗻𝗲𝗹\n"
    "➻ 𝗵𝘁𝗺𝗹 𝗳𝗼𝗿𝗺𝗮𝘁𝘁𝗶𝗻𝗴 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱\n"
    "➻ 𝗰𝗮𝗻 𝘀𝗲𝘁 𝘁𝗲𝘅𝘁 + 𝗺𝗲𝗱𝗶𝗮 + 𝘂𝗿𝗹 𝗯𝘂𝘁𝘁𝗼𝗻𝘀"
)

# ============================================================
# Placeholder vars display string
# ============================================================
WELCOME_VARS = (
    "• <code>{id}</code> = ᴜꜱᴇʀ ɪᴅ\n"
    "• <code>{name}</code> = ꜰɪʀꜱᴛ ɴᴀᴍᴇ\n"
    "• <code>{surname}</code> = ʟᴀꜱᴛ ɴᴀᴍᴇ\n"
    "• <code>{namesurname}</code> = ꜰᴜʟʟ ɴᴀᴍᴇ\n"
    "• <code>{mention}</code> = ᴄʟɪᴄᴋᴀʙʟᴇ ᴍᴇɴᴛɪᴏɴ\n"
    "• <code>{username}</code> = @ᴜꜱᴇʀɴᴀᴍᴇ\n"
    "• <code>{groupname}</code> = ɢʀᴏᴜᴘ ɴᴀᴍᴇ"
)

# ============================================================
# In-memory session store with TTL expiry (30 min)
# Prevents memory leak from abandoned setups
# ============================================================
SESSION_TTL = 1800  # 30 minutes

class _TTLSessions:
    """
    ᴅɪᴄᴛ-ʟɪᴋᴇ ꜱᴛᴏʀᴇ ᴡʜᴇʀᴇ ᴇɴᴛʀɪᴇꜱ ᴀᴜᴛᴏ-ᴇxᴘɪʀᴇ ᴀꜰᴛᴇʀ ꜱᴇꜱꜱɪᴏɴ_ᴛᴛʟ ꜱᴇᴄᴏɴᴅꜱ.
    ᴘʀᴇᴠᴇɴᴛꜱ ʀᴀᴍ ʙᴜɪʟᴅᴜᴘ ꜰʀᴏᴍ ꜱᴇꜱꜱɪᴏɴꜱ ᴛʜᴀᴛ ᴀʀᴇ ɴᴇᴠᴇʀ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.
    """
    def __init__(self):
        self._data: dict = {}   # user_id -> session
        self._ts:   dict = {}   # user_id -> created_at timestamp

    def get(self, user_id: int):
        if user_id not in self._data:
            return None
        if time.time() - self._ts[user_id] > SESSION_TTL:
            # Expired — clean up
            self._data.pop(user_id, None)
            self._ts.pop(user_id, None)
            return None
        return self._data[user_id]

    def __setitem__(self, user_id: int, value):
        self._data[user_id] = value
        self._ts[user_id]   = time.time()

    def __getitem__(self, user_id: int):
        result = self.get(user_id)
        if result is None:
            raise KeyError(user_id)
        return result

    def __contains__(self, user_id: int):
        return self.get(user_id) is not None

    def pop(self, user_id: int, default=None):
        self._ts.pop(user_id, None)
        return self._data.pop(user_id, default)

    def touch(self, user_id: int):
        """ʀᴇꜰʀᴇꜱʜ ᴛᴛʟ — ᴄᴀʟʟ ᴡʜᴇɴᴇᴠᴇʀ ᴜꜱᴇʀ ɪɴᴛᴇʀᴀᴄᴛꜱ."""
        if user_id in self._data:
            self._ts[user_id] = time.time()

    def cleanup(self):
        """ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴇxᴘɪʀᴇᴅ ꜱᴇꜱꜱɪᴏɴꜱ."""
        now     = time.time()
        expired = [uid for uid, ts in self._ts.items() if now - ts > SESSION_TTL]
        for uid in expired:
            self._data.pop(uid, None)
            self._ts.pop(uid, None)
        return len(expired)

    def __len__(self):
        return len(self._data)


_sessions = _TTLSessions()


# ============================================================
# Helpers
# ============================================================

def _fmt(text: str, user, chat) -> str:
    """ʀᴇᴘʟᴀᴄᴇ ᴘʟᴀᴄᴇʜᴏʟᴅᴇʀꜱ ɪɴ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ (ᴄᴀꜱᴇ-ɪɴꜱᴇɴꜱɪᴛɪᴠᴇ)."""
    if not text:
        return ""
    full = f"{user.first_name or ''} {user.last_name or ''}".strip()
    mention = f'<a href="tg://user?id={user.id}">{user.first_name or "User"}</a>'

    values = {
        "id": str(user.id),
        "name": user.first_name or "",
        "surname": user.last_name or "",
        "namesurname": full,
        "mention": mention,
        "username": f"@{user.username}" if user.username else (user.first_name or ""),
        "groupname": chat.title or "",
    }

    def _replace(match):
        key = match.group(1).lower()
        return values.get(key, match.group(0))

    return re.sub(r"\{(id|name|surname|namesurname|mention|username|groupname)\}", _replace, text, flags=re.IGNORECASE)


def _build_markup(buttons: list):
    """ʙᴜɪʟᴅ ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ ꜰʀᴏᴍ ʟɪꜱᴛ ᴏꜰ {ᴛᴇxᴛ, ᴜʀʟ} ᴅɪᴄᴛꜱ."""
    if not buttons:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(b["text"], url=b["url"], style=ButtonStyle.PRIMARY)] for b in buttons]
    )


async def _send_welcome_to_group(client, chat_id: int, chat, user):
    """ꜰɪʀᴇ ᴛʜᴇ ᴀᴄᴛᴜᴀʟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ɪɴᴛᴏ ᴀ ɢʀᴏᴜᴘ."""
    try:
        status = await db.get_welcome_status(chat_id)
        if not status:
            logger.debug(f"ᴡᴇʟᴄᴏᴍᴇ ᴏꜰꜰ ꜰᴏʀ ᴄʜᴀᴛ {chat_id}")
            return

        data = await db.get_welcome_v2(chat_id)
        logger.info(f"ᴡᴇʟᴄᴏᴍᴇ ᴅᴀᴛᴀ ꜰᴏʀ {chat_id}: {data}")

        # No custom data → default message
        if not data or (not data.get("text") and not data.get("media_file_id")):
            await client.send_message(
                chat_id,
                f"👋 ᴡᴇʟᴄᴏᴍᴇ <a href='tg://user?id={user.id}'>{user.first_name}</a> ᴛᴏ {chat.title}!",
                parse_mode=enums.ParseMode.HTML
            )
            return

        text   = _fmt(data.get("text") or "", user, chat)
        fid    = data.get("media_file_id")
        mtype  = data.get("media_type")
        markup = _build_markup(data.get("buttons") or [])

        if fid:
            send_fn = {
                "photo":     client.send_photo,
                "video":     client.send_video,
                "document":  client.send_document,
                "animation": client.send_animation,
            }.get(mtype)
            if send_fn:
                await send_fn(
                    chat_id, fid,
                    caption=text or None,
                    reply_markup=markup,
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await client.send_message(
                    chat_id, text,
                    reply_markup=markup,
                    parse_mode=enums.ParseMode.HTML
                )
        else:
            await client.send_message(
                chat_id, text,
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML
            )

    except Exception as e:
        logger.error(f"ᴡᴇʟᴄᴏᴍᴇ ꜱᴇɴᴅ ᴇʀʀᴏʀ ɪɴ ᴄʜᴀᴛ {chat_id}: {e}", exc_info=True)


async def _send_panel(client, pm_chat_id: int, user_id: int, edit_msg=None):
    """ꜱᴇɴᴅ ᴏʀ ᴇᴅɪᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛᴜᴘ ᴘᴀɴᴇʟ ɪɴ ᴘᴍ."""
    s = _sessions.get(user_id)
    if not s:
        return

    has_text    = "✅" if s.get("text") else "❌"
    has_media   = "✅" if s.get("media_file_id") else "❌"
    btn_count   = len(s.get("buttons", []))
    has_btns    = f"✅ ({btn_count})" if btn_count else "❌"

    text = (
        f"💬 <u>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗠𝗲𝘀𝘀𝗮𝗴𝗲</u>\n"
        f"📌 ɢʀᴏᴜᴘ: {s['chat_title']}\n\n"
        f"📄 ᴛᴇxᴛ {has_text}\n"
        f"📸 ᴍᴇᴅɪᴀ {has_media}\n"
        f"🔠 ᴜʀʟ ʙᴜᴛᴛᴏɴꜱ {has_btns}\n\n"
        f"👉🏻 ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴏᴏꜱᴇ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜱᴇᴛ"
    )

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 ᴛᴇxᴛ",        callback_data=f"ws_text_{user_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📸 ᴍᴇᴅɪᴀ",       callback_data=f"ws_media_{user_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🔘 ʙᴜᴛᴛᴏɴꜱ", callback_data=f"ws_urlbtn_{user_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("🕵️ ᴘʀᴇᴠɪᴇᴡ", callback_data=f"ws_preview_{user_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("💾 ꜱᴀᴠᴇ",    callback_data=f"ws_save_{user_id}", style=ButtonStyle.PRIMARY),
        ],
        [InlineKeyboardButton("🚮 ᴄʟᴇᴀʀ ᴀʟʟ", callback_data=f"ws_clear_{user_id}", style=ButtonStyle.PRIMARY)]
    ])

    if edit_msg:
        try:
            await edit_msg.edit_text(text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
            return
        except Exception:
            pass

    await client.send_message(pm_chat_id, text,
                               reply_markup=markup,
                               parse_mode=enums.ParseMode.HTML)


# ============================================================
# Register
# ============================================================

def register_welcome_handler(app: Client):

    # ----------------------------------------------------------
    # Periodic session cleanup — runs every 30 min
    # Clears abandoned/expired setup sessions from RAM
    # ----------------------------------------------------------
    import asyncio as _asyncio

    async def _cleanup_sessions():
        while True:
            await _asyncio.sleep(1800)  # every 30 min
            removed = _sessions.cleanup()
            if removed:
                logging.getLogger(__name__).info(
                    f"ᴡᴇʟᴄᴏᴍᴇ ꜱᴇꜱꜱɪᴏɴꜱ: ᴄʟᴇᴀɴᴇᴅ {removed} ᴇxᴘɪʀᴇᴅ ᴇɴᴛʀɪᴇꜱ"
                )

    _asyncio.get_event_loop().create_task(_cleanup_sessions())

    # ----------------------------------------------------------
    # New member → fire welcome
    # ----------------------------------------------------------
    # ----------------------------------------------------------
    # Reliable fallback — chat_member updates aren't always
    # delivered (depends on bot admin status / library timing),
    # so also fire on the plain "user joined" service message.
    # ----------------------------------------------------------
    _recent_welcomed = {}  # (chat_id, user_id) -> ts, avoids double-sending

    @app.on_chat_member_updated(group=0)
    async def on_new_member(client: Client, cmu: ChatMemberUpdated):
        import time as _time
        if not cmu.new_chat_member:
            return
        # Only fire on actual joins — not on promote/demote/restrict
        new_status = cmu.new_chat_member.status
        old_status = cmu.old_chat_member.status if cmu.old_chat_member else None
        # Must be becoming a MEMBER now
        if new_status != ChatMemberStatus.MEMBER:
            return
        # Must have been BANNED, LEFT, or no previous record (first join)
        if old_status not in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT, None]:
            return
        user = cmu.new_chat_member.user
        if user.is_bot:
            return
        _recent_welcomed[(cmu.chat.id, user.id)] = _time.time()
        await _send_welcome_to_group(client, cmu.chat.id, cmu.chat, user)

    @app.on_message(filters.group & filters.new_chat_members, group=1)
    async def on_new_member_fallback(client: Client, message: Message):
        import time as _time
        for user in message.new_chat_members or []:
            if user.is_bot:
                continue
            key = (message.chat.id, user.id)
            last = _recent_welcomed.get(key, 0)
            if _time.time() - last < 10:  # already handled by chat_member update just now
                continue
            _recent_welcomed[key] = _time.time()
            await _send_welcome_to_group(client, message.chat.id, message.chat, user)

    # ----------------------------------------------------------
    # /welcome on|off
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("welcome"))
    async def welcome_toggle(client, message: Message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴏʀ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts   = message.text.split(maxsplit=1)
        chat_id = message.chat.id

        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status  = await db.get_welcome_status(chat_id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗦𝘆𝘀𝘁𝗲𝗺\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/welcome ᴏɴ</code> ᴏʀ <code>/welcome ᴏꜰꜰ</code>\n"
                f"ꜱᴇᴛᴜᴘ: <code>/setwelcome</code>\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {current}"
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_welcome_status(chat_id, status)

        if status:
            bot_me    = await client.get_me()
            deep_link = f"https://t.me/{bot_me.username}?start=wsetup_{chat_id}"
            await message.reply_text(
                "✅ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗢𝗡!\n\n"
                "ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ꜱᴇᴛᴜᴘ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴘᴍ 👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ ꜱᴇᴛ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ", url=deep_link, style=ButtonStyle.PRIMARY)]
                ]),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text("⚠️ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗢𝗙𝗙!",
                                     parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /setwelcome — send PM deep link
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("setwelcome"))
    async def setwelcome_group(client, message: Message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        bot_me    = await client.get_me()
        deep_link = f"https://t.me/{bot_me.username}?start=wsetup_{message.chat.id}"
        await message.reply_text(
            "👇 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ꜱᴇᴛᴜᴘ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴘᴍ:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ꜱᴇᴛ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ɪɴ ᴘᴍ", url=deep_link, style=ButtonStyle.PRIMARY)]
            ])
        )

    # ----------------------------------------------------------
    # /resetwelcome
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("resetwelcome"))
    async def resetwelcome(client, message: Message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        await db.clear_welcome_v2(message.chat.id)
        await message.reply_text("♻️ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ʀᴇꜱᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ.")

    # ----------------------------------------------------------
    # /previewwelcome
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("previewwelcome"))
    async def previewwelcome(client, message: Message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        await _send_welcome_to_group(client, message.chat.id, message.chat, message.from_user)


    # ----------------------------------------------------------
    # Panel button callbacks  (private only)
    # ----------------------------------------------------------
    @app.on_callback_query(
        filters.regex(r"^ws_(text|media|urlbtn|preview|save|clear)_(\d+)$")
    )
    async def panel_callback(client, cq):
        if cq.message.chat.type != enums.ChatType.PRIVATE:
            return await cq.answer()

        action  = cq.matches[0].group(1)
        user_id = int(cq.matches[0].group(2))

        # Auth: only the user who started setup can interact
        if cq.from_user.id != user_id:
            return await cq.answer("❌ ᴛʜɪꜱ ᴘᴀɴᴇʟ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ.", show_alert=True)

        s = _sessions.get(user_id)
        if not s:
            return await cq.answer("⚠️ ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴜꜱᴇ /setwelcome ᴀɢᴀɪɴ.", show_alert=True)

        # Re-verify user is still admin in the group
        try:
            member = await cq.client.get_chat_member(s["chat_id"], user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                _sessions.pop(user_id, None)
                return await cq.answer("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ɢʀᴏᴜᴘ.", show_alert=True)
        except Exception:
            pass  # If check fails, allow to continue

        # Refresh TTL — user is actively using the session
        _sessions.touch(user_id)

        # ── Text ──────────────────────────────────────
        if action == "text":
            s["step"] = "awaiting_text"
            await cq.message.edit_text(
                "📄 𝗦𝗲𝘁 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗲𝘅𝘁\n"
                "ꜱᴇɴᴅ ᴍᴇ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ ɴᴏᴡ!\n"
                "ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ʜᴛᴍʟ ᴀɴᴅ:\n\n"
                f"{WELCOME_VARS}\n\n"
                "ꜱᴇɴᴅ /cancel ᴛᴏ ɢᴏ ʙᴀᴄᴋ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
            await cq.answer()

        # ── Media ─────────────────────────────────────
        elif action == "media":
            s["step"] = "awaiting_media"
            await cq.message.edit_text(
                "📸 𝗦𝗲𝘁 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗠𝗲𝗱𝗶𝗮\n\n"
                "ꜱᴇɴᴅ ᴍᴇ ᴀ 𝗽𝗵𝗼𝘁𝗼, 𝘃𝗶𝗱𝗲𝗼, 𝗚𝗜𝗙 ᴏʀ 𝗱𝗼𝗰𝘂𝗺𝗲𝗻𝘁.\n\n"
                "ꜱᴇɴᴅ /cancel ᴛᴏ ɢᴏ ʙᴀᴄᴋ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
            await cq.answer()

        # ── URL Buttons ───────────────────────────────
        elif action == "urlbtn":
            s["step"] = "awaiting_btn_name"
            count = len(s.get("buttons", []))
            await cq.message.edit_text(
                f"🔠 𝗔𝗱𝗱 𝗨𝗥𝗟 𝗕𝘂𝘁𝘁𝗼𝗻\n"
                f"ᴄᴜʀʀᴇɴᴛ ʙᴜᴛᴛᴏɴꜱ: {count}\n\n"
                f"ꜱᴇɴᴅ ᴛʜᴇ 𝗯𝘂𝘁𝘁𝗼𝗻 𝗹𝗮𝗯𝗲𝗹 (ᴛᴇxᴛ ꜱʜᴏᴡɴ ᴏɴ ʙᴜᴛᴛᴏɴ).\n\n"
                f"• /done — ꜰɪɴɪꜱʜ ᴀᴅᴅɪɴɢ ʙᴜᴛᴛᴏɴꜱ\n"
                f"• /clearbtn — ʀᴇᴍᴏᴠᴇ ᴀʟʟ ʙᴜᴛᴛᴏɴꜱ\n"
                f"• /cancel — ɢᴏ ʙᴀᴄᴋ"
                f"",
                parse_mode=enums.ParseMode.HTML
            )
            await cq.answer()

        # ── Preview ───────────────────────────────────
        elif action == "preview":
            await cq.answer("ꜱᴇɴᴅɪɴɢ ᴘʀᴇᴠɪᴇᴡ…")
            user = cq.from_user

            class _FakeChat:
                title = s["chat_title"]
                id    = s["chat_id"]

            preview_text = _fmt(s.get("text") or f"👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {s['chat_title']}!", user, _FakeChat())
            markup       = _build_markup(s.get("buttons", []))
            fid          = s.get("media_file_id")
            mtype        = s.get("media_type")
            pm_id        = cq.message.chat.id

            caption = "👁 𝗣𝗿𝗲𝘃𝗶𝗲𝘄:\n\n" + preview_text
            try:
                if fid:
                    send_fn = {
                        "photo":     client.send_photo,
                        "video":     client.send_video,
                        "document":  client.send_document,
                        "animation": client.send_animation,
                    }.get(mtype)
                    if send_fn:
                        await send_fn(pm_id, fid, caption=caption,
                                      reply_markup=markup,
                                      parse_mode=enums.ParseMode.HTML)
                    else:
                        await client.send_message(pm_id, caption,
                                                  reply_markup=markup,
                                                  parse_mode=enums.ParseMode.HTML)
                else:
                    await client.send_message(pm_id, caption,
                                              reply_markup=markup,
                                              parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                await client.send_message(pm_id, f"❌ ᴘʀᴇᴠɪᴇᴡ ᴇʀʀᴏʀ: {e}")

        # ── Save ──────────────────────────────────────
        elif action == "save":
            await db.set_welcome_v2(s["chat_id"], {
                "text":          s.get("text"),
                "media_file_id": s.get("media_file_id"),
                "media_type":    s.get("media_type"),
                "buttons":       s.get("buttons", []),
            })
            _sessions.pop(user_id, None)
            await cq.message.edit_text(
                f"✅ <u>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝘀𝗮𝘃𝗲𝗱!</u>\n"
                f"ɢʀᴏᴜᴘ: {s['chat_title']}\n"
                f"ᴛᴇxᴛ: {'✅' if s.get('text') else '❌'}\n"
                f"ᴍᴇᴅɪᴀ: {'✅' if s.get('media_file_id') else '❌'}\n"
                f"ᴜʀʟ ʙᴜᴛᴛᴏɴꜱ: {len(s.get('buttons', []))}\n\n"
                f"ᴜꜱᴇ <code>/welcome ᴏɴ</code> ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ᴇɴᴀʙʟᴇ ɪᴛ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
            await cq.answer("✅ ꜱᴀᴠᴇᴅ!")

        # ── Clear ─────────────────────────────────────
        elif action == "clear":
            s.update(text=None, media_file_id=None, media_type=None, buttons=[])
            await cq.answer("🗑 ᴄʟᴇᴀʀᴇᴅ.")
            await _send_panel(client, cq.message.chat.id, user_id, edit_msg=cq.message)

    # ----------------------------------------------------------
    # PM text/media input handler for active sessions
    # Uses group=5 so it runs after all default handlers
    # ----------------------------------------------------------
    @app.on_message(filters.private, group=5)
    async def session_input(client, message: Message):
        user_id = message.from_user.id
        s       = _sessions.get(user_id)
        if not s:
            return  # No active session — ignore completely

        step = s.get("step", "main")
        txt  = (message.text or "").strip()

        # ── /cancel ───────────────────────────────────
        if txt == "/cancel":
            s["step"] = "main"
            await message.reply_text("↩️ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
            await _send_panel(client, message.chat.id, user_id)
            return

        # ── /done (while adding buttons) ──────────────
        if txt == "/done" and step in ("awaiting_btn_name", "awaiting_btn_url"):
            s["step"] = "main"
            await message.reply_text(
                f"✅ ᴅᴏɴᴇ! {len(s['buttons'])} ʙᴜᴛᴛᴏɴ(ꜱ) ꜱᴀᴠᴇᴅ.\n"
                "ᴜꜱᴇ ᴛʜᴇ ᴘᴀɴᴇʟ ᴛᴏ ᴘʀᴇᴠɪᴇᴡ ᴏʀ ꜱᴀᴠᴇ."
                f"",
                parse_mode=enums.ParseMode.HTML
            )
            await _send_panel(client, message.chat.id, user_id)
            return

        # ── /clearbtn ─────────────────────────────────
        if txt == "/clearbtn":
            s["buttons"] = []
            s["step"]    = "main"
            await message.reply_text("🗑 ᴀʟʟ ᴜʀʟ ʙᴜᴛᴛᴏɴꜱ ᴄʟᴇᴀʀᴇᴅ.")
            await _send_panel(client, message.chat.id, user_id)
            return

        # ── awaiting_text ─────────────────────────────
        if step == "awaiting_text":
            if not message.text:
                return await message.reply_text("⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴛᴇxᴛ ᴍᴇꜱꜱᴀɢᴇ.")
            s["text"] = message.text   # keep raw HTML from user
            s["step"] = "main"
            await message.reply_text("✅ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ ꜱᴀᴠᴇᴅ!")
            await _send_panel(client, message.chat.id, user_id)

        # ── awaiting_media ────────────────────────────
        elif step == "awaiting_media":
            if message.photo:
                s["media_file_id"] = message.photo.sizes[-1].file_id
                s["media_type"]    = "photo"
            elif message.video:
                s["media_file_id"] = message.video.file_id
                s["media_type"]    = "video"
            elif message.document:
                s["media_file_id"] = message.document.file_id
                s["media_type"]    = "document"
            elif message.animation:
                s["media_file_id"] = message.animation.file_id
                s["media_type"]    = "animation"
            else:
                return await message.reply_text("⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, ɢɪꜰ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ.")
            s["step"] = "main"
            await message.reply_text("✅ ᴍᴇᴅɪᴀ ꜱᴀᴠᴇᴅ!")
            await _send_panel(client, message.chat.id, user_id)

        # ── awaiting_btn_name ─────────────────────────
        elif step == "awaiting_btn_name":
            if not message.text:
                return await message.reply_text("⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʟᴀʙᴇʟ ᴀꜱ ᴛᴇxᴛ.")
            s["_tmp_btn"] = txt
            s["step"]     = "awaiting_btn_url"
            await message.reply_text(
                f"🔗 ɴᴏᴡ ꜱᴇɴᴅ ᴛʜᴇ 𝗨𝗥𝗟 ꜰᴏʀ ʙᴜᴛᴛᴏɴ: {txt}\n\n"
                f"ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ <code>ʜᴛᴛᴘ://</code>, <code>ʜᴛᴛᴘꜱ://</code> ᴏʀ <code>ᴛɢ://</code>",
                parse_mode=enums.ParseMode.HTML
            )

        # ── awaiting_btn_url ──────────────────────────
        elif step == "awaiting_btn_url":
            if not message.text:
                return await message.reply_text("⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴜʀʟ ᴀꜱ ᴛᴇxᴛ.")
            url = txt
            if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
                return await message.reply_text(
                    "⚠️ ɪɴᴠᴀʟɪᴅ ᴜʀʟ!\nᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ <code>ʜᴛᴛᴘ://</code>, "
                    "<code>ʜᴛᴛᴘꜱ://</code> ᴏʀ <code>ᴛɢ://</code>",
                    parse_mode=enums.ParseMode.HTML
                )
            label = s.pop("_tmp_btn", "Button")
            s["buttons"].append({"text": label, "url": url})
            s["step"] = "awaiting_btn_name"   # allow adding more buttons

            await message.reply_text(
                f"✅ ʙᴜᴛᴛᴏɴ ᴀᴅᴅᴇᴅ: {label}\n"
                f"ᴛᴏᴛᴀʟ: {len(s['buttons'])}\n\n"
                f"ꜱᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ʟᴀʙᴇʟ ᴛᴏ ᴀᴅᴅ ᴍᴏʀᴇ, ᴏʀ /done ᴛᴏ ꜰɪɴɪꜱʜ.",
                parse_mode=enums.ParseMode.HTML
            )
