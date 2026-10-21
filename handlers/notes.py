# ============================================================
# Group Manager Bot — Notes System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatMemberStatus
import db
import logging

logger = logging.getLogger(__name__)


NOTES_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   📝 𝗻𝗼𝘁𝗲𝘀 𝘀𝘆𝘀𝘁𝗲𝗺\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /save &lt;𝗻𝗮𝗺𝗲&gt; &lt;𝘁𝗲𝘅𝘁&gt;\n"
    "➻ 𝗼𝗿 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮𝗻𝘆 𝗺𝗲𝘀𝘀𝗮𝗴𝗲/media 𝘄𝗶𝘁𝗵 /save &lt;𝗻𝗮𝗺𝗲&gt;\n\n"
    "➻ /get &lt;𝗻𝗮𝗺𝗲&gt; 𝗼𝗿 #𝗻𝗮𝗺𝗲 — 𝘃𝗶𝗲𝘄 𝗮 𝗻𝗼𝘁𝗲\n\n"
    "➻ /notes — 𝗹𝗶𝘀𝘁 𝗮𝗹𝗹 𝗻𝗼𝘁𝗲𝘀\n\n"
    "➻ /delnote &lt;𝗻𝗮𝗺𝗲&gt; — 𝗱𝗲𝗹𝗲𝘁𝗲 𝗮 𝗻𝗼𝘁𝗲\n\n"
    "❖ 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝘁𝘆𝗽𝗲𝘀 ❖\n"
    "➻ 𝘁𝗲𝘅𝘁 (𝗛𝗧𝗠𝗟), 𝗽𝗵𝗼𝘁𝗼, 𝘃𝗶𝗱𝗲𝗼,\n"
    "➻ 𝗱𝗼𝗰𝘂𝗺𝗲𝗻𝘁, 𝗮𝘂𝗱𝗶𝗼, 𝘀𝘁𝗶𝗰𝗸𝗲𝗿, 𝗚𝗜𝗙"
)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


async def _send_note(client, target_chat_id: int, data: dict, reply_to_id: int = None):
    """ꜱᴇɴᴅ ᴀ ɴᴏᴛᴇ ᴛᴏ ᴀ ᴄʜᴀᴛ."""
    text     = data.get("content") or ""
    ctype    = data.get("type", "text")
    file_id  = data.get("file_id")
    kwargs   = dict(parse_mode=enums.ParseMode.HTML)
    if reply_to_id:
        kwargs["reply_to_message_id"] = reply_to_id

    try:
        if ctype == "text":
            await client.send_message(target_chat_id, text or "📝", **kwargs)
        elif ctype == "photo":
            await client.send_photo(target_chat_id, file_id, caption=text or None, **kwargs)
        elif ctype == "video":
            await client.send_video(target_chat_id, file_id, caption=text or None, **kwargs)
        elif ctype == "document":
            await client.send_document(target_chat_id, file_id, caption=text or None, **kwargs)
        elif ctype == "audio":
            await client.send_audio(target_chat_id, file_id, caption=text or None, **kwargs)
        elif ctype == "animation":
            await client.send_animation(target_chat_id, file_id, caption=text or None, **kwargs)
        elif ctype == "sticker":
            await client.send_sticker(target_chat_id, file_id)
        elif ctype == "voice":
            await client.send_voice(target_chat_id, file_id, caption=text or None, **kwargs)
    except Exception as e:
        logger.error(f"ɴᴏᴛᴇ ꜱᴇɴᴅ ᴇʀʀᴏʀ: {e}")


def register_notes_handler(app: Client):

    # ----------------------------------------------------------
    # /save <name> [text]  OR  reply to media with /save <name>
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command(["save", "setnote"]))
    async def save_note(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴀᴠᴇ ɴᴏᴛᴇꜱ.")

        parts = message.text.split(maxsplit=2)

        # Need at least a name
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ 𝗨𝘀𝗮𝗴𝗲:\n"
                "• <code>/save ɴᴀᴍᴇ ᴛᴇxᴛ ʜᴇʀᴇ</code>\n"
                "• ʀᴇᴘʟʏ ᴛᴏ ᴍᴇᴅɪᴀ: <code>/save ɴᴀᴍᴇ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        name = parts[1].strip().lower()

        # From reply (media or text)
        if message.reply_to_message:
            reply = message.reply_to_message
            caption = parts[2] if len(parts) > 2 else (reply.caption or reply.text or "")

            if reply.photo:
                await db.set_note(message.chat.id, name, caption, "photo",
                                  reply.photo.sizes[-1].file_id)
            elif reply.video:
                await db.set_note(message.chat.id, name, caption, "video",
                                  reply.video.file_id)
            elif reply.document:
                await db.set_note(message.chat.id, name, caption, "document",
                                  reply.document.file_id)
            elif reply.audio:
                await db.set_note(message.chat.id, name, caption, "audio",
                                  reply.audio.file_id)
            elif reply.animation:
                await db.set_note(message.chat.id, name, caption, "animation",
                                  reply.animation.file_id)
            elif reply.sticker:
                await db.set_note(message.chat.id, name, "", "sticker",
                                  reply.sticker.file_id)
            elif reply.voice:
                await db.set_note(message.chat.id, name, caption, "voice",
                                  reply.voice.file_id)
            elif reply.text:
                await db.set_note(message.chat.id, name, reply.text, "text", None)
            else:
                return await message.reply_text("⚠️ ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ.")

        elif len(parts) >= 3:
            # Plain text note
            await db.set_note(message.chat.id, name, parts[2], "text", None)
        else:
            return await message.reply_text(
                "⚙️ 𝗨𝘀𝗮𝗴𝗲:\n"
                "• <code>/save ɴᴀᴍᴇ ᴛᴇxᴛ ʜᴇʀᴇ</code>\n"
                "• ʀᴇᴘʟʏ ᴛᴏ ᴍᴇᴅɪᴀ: <code>/save ɴᴀᴍᴇ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        await message.reply_text(
            f"✅ ɴᴏᴛᴇ <code>#{name}</code> ꜱᴀᴠᴇᴅ!\n\n"
            f"ᴜꜱᴇ <code>#{name}</code> ᴏʀ <code>/get {name}</code> ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ɪᴛ.",
            parse_mode=enums.ParseMode.HTML
        )


    # ----------------------------------------------------------
    # /get <name> — get note in group
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("get"))
    async def get_note_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/get ɴᴏᴛᴇɴᴀᴍᴇ</code>",
                                            parse_mode=enums.ParseMode.HTML)

        name = parts[1].strip().lower()
        data = await db.get_note(message.chat.id, name)
        if not data:
            return await message.reply_text(
                f"⚠️ ɴᴏᴛᴇ <code>#{name}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        await _send_note(client, message.chat.id, data,
                         reply_to_id=message.id)


    # ----------------------------------------------------------
    # /delnote <name>
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("delnote"))
    async def delnote_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ɴᴏᴛᴇꜱ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/delnote ɴᴏᴛᴇɴᴀᴍᴇ</code>",
                                            parse_mode=enums.ParseMode.HTML)

        name = parts[1].strip().lower()
        deleted = await db.delete_note(message.chat.id, name)

        if deleted:
            await message.reply_text(f"🗑 ɴᴏᴛᴇ <code>#{name}</code> ᴅᴇʟᴇᴛᴇᴅ.",
                                     parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text(f"⚠️ ɴᴏ ɴᴏᴛᴇ ɴᴀᴍᴇᴅ <code>#{name}</code>.",
                                     parse_mode=enums.ParseMode.HTML)


    # ----------------------------------------------------------
    # /notes — list all notes
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("notes"))
    async def notes_list_cmd(client, message: Message):
        names = await db.get_all_notes(message.chat.id)

        if not names:
            return await message.reply_text("📭 ɴᴏ ɴᴏᴛᴇꜱ ꜱᴀᴠᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.")

        text = (
            f"📝 𝗡𝗼𝘁𝗲𝘀 — {message.chat.title}\n\n"
            + "\n".join(f"• <code>#{n}</code>" for n in sorted(names))
            + "\n\nᴜꜱᴇ <code>#ɴᴀᴍᴇ</code> ᴏʀ <code>/get ɴᴀᴍᴇ</code> ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ."
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)


    # ----------------------------------------------------------
    # #notename — hashtag trigger in group (send directly in group)
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.regex(r"^#(\w+)"))
    async def hashtag_note(client, message: Message):
        name = message.matches[0].group(1).lower()
        data = await db.get_note(message.chat.id, name)
        if not data:
            return  # Not a note — ignore silently
        await _send_note(client, message.chat.id, data,
                         reply_to_id=message.id)


    # ----------------------------------------------------------
    # /start note_<chatid>_<name> — PM deep link (group=2 so it
    # runs after the main /start handler)
    # ----------------------------------------------------------
    @app.on_message(filters.private & filters.command("start"), group=2)
    async def note_pm_deeplink(client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or not args[1].startswith("note_"):
            return

        try:
            _, chat_id_str, name = args[1].split("_", 2)
            chat_id = int(chat_id_str)
        except (ValueError, IndexError):
            return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɴᴏᴛᴇ ʟɪɴᴋ.")

        data = await db.get_note(chat_id, name)
        if not data:
            return await message.reply_text(
                f"⚠️ ɴᴏᴛᴇ <code>#{name}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        await message.reply_text(
            f"📝 𝗡𝗼𝘁𝗲: #{name}",
            parse_mode=enums.ParseMode.HTML
        )
        await _send_note(client, message.chat.id, data)
