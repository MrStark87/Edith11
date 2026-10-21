# ============================================================
# Group Manager Bot — Filters (Auto Reply)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import db
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


FILTERS_HELP_TEXT = (
    f"╔══════════════════╗\n"
    f"   📝 𝗳𝗶𝗹𝘁𝗲𝗿𝘀\n"
    f"╚══════════════════╝\n\n"
    
    f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    
    f"➻ /filter &lt;𝗸𝗲𝘆𝘄𝗼𝗿𝗱&gt;\n"
    f"➻ 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 / 𝘀𝘁𝗶𝗰𝗸𝗲𝗿 𝘁𝗼 𝘀𝗲𝘁\n"
    f"➻ 𝗮𝘂𝘁𝗼-𝗿𝗲𝗽𝗹𝘆 𝗳𝗼𝗿 𝘁𝗵𝗮𝘁 𝗸𝗲𝘆𝘄𝗼𝗿𝗱\n\n"
    
    f"➻ /stopfilter &lt;𝗸𝗲𝘆𝘄𝗼𝗿𝗱&gt;\n"
    f"➻ 𝗿𝗲𝗺𝗼𝘃𝗲 𝗮 𝗳𝗶𝗹𝘁𝗲𝗿\n\n"
    
    f"➻ /filters\n"
    f"➻ 𝗹𝗶𝘀𝘁 𝗮𝗹𝗹 𝗮𝗰𝘁𝗶𝘃𝗲 𝗳𝗶𝗹𝘁𝗲𝗿𝘀\n\n"
    
    f"➻ 🌟 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗲 𝗿𝗲𝗽𝗹𝗶𝗲𝘀 𝗮𝗻𝗱 𝗺𝗮𝗸𝗲 𝘆𝗼𝘂𝗿\n"
    f"➻ 𝗴𝗿𝗼𝘂𝗽 𝗺𝗼𝗿𝗲 𝗶𝗻𝘁𝗲𝗿𝗮𝗰𝘁𝗶𝘃𝗲"
)

def register_filters_handler(app: Client):

    # ==========================================================
    # /filter <keyword> — reply to message to set filter
    # ==========================================================

    @app.on_message(filters.group & filters.command("filter"))
    async def filter_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        if not message.reply_to_message:
            return await message.reply_text(
                "⚙️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ꜱᴛɪᴄᴋᴇʀ ᴀɴᴅ ᴜꜱᴇ:\n"
                "<code>/filter &lt;ᴋᴇʏᴡᴏʀᴅ&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴀɴᴅ ᴛʏᴘᴇ <code>/filter &lt;ᴋᴇʏᴡᴏʀᴅ&gt;</code>",
                parse_mode=enums.ParseMode.HTML
            )

        keyword = parts[1].strip().lower()
        reply = message.reply_to_message

        # Detect content type
        if reply.text:
            content_type = "text"
            content = reply.text
            file_id = None
        elif reply.sticker:
            content_type = "sticker"
            content = None
            file_id = reply.sticker.file_id
        elif reply.photo:
            content_type = "photo"
            content = reply.caption or ""
            file_id = reply.photo.file_id
        elif reply.video:
            content_type = "video"
            content = reply.caption or ""
            file_id = reply.video.file_id
        elif reply.document:
            content_type = "document"
            content = reply.caption or ""
            file_id = reply.document.file_id
        elif reply.audio:
            content_type = "audio"
            content = reply.caption or ""
            file_id = reply.audio.file_id
        elif reply.animation:
            content_type = "animation"
            content = reply.caption or ""
            file_id = reply.animation.file_id
        else:
            return await message.reply_text("⚠️ ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛʏᴘᴇ ꜰᴏʀ ꜰɪʟᴛᴇʀ.")

        await db.set_filter(message.chat.id, keyword, content_type, content, file_id)
        await message.reply_text(
            f"✅ ꜰɪʟᴛᴇʀ ꜱᴇᴛ ꜰᴏʀ ᴋᴇʏᴡᴏʀᴅ: <code>{keyword}</code>",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # /stopfilter <keyword>
    # ==========================================================

    @app.on_message(filters.group & filters.command("stopfilter"))
    async def stopfilter_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/stopfilter &lt;ᴋᴇʏᴡᴏʀᴅ&gt;</code>", parse_mode=enums.ParseMode.HTML)

        keyword = parts[1].strip().lower()
        removed = await db.delete_filter(message.chat.id, keyword)

        if removed:
            await message.reply_text(f"🗑️ ꜰɪʟᴛᴇʀ ꜰᴏʀ <code>{keyword}</code> ʀᴇᴍᴏᴠᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text(f"⚠️ ɴᴏ ꜰɪʟᴛᴇʀ ꜰᴏᴜɴᴅ ꜰᴏʀ <code>{keyword}</code>.", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # /filters — list all
    # ==========================================================
    @app.on_message(filters.group & filters.command("filters"))
    async def filters_list_cmd(client, message: Message):
        all_filters = await db.get_all_filters(message.chat.id)
        if not all_filters:
            return await message.reply_text(
                "📭 ɴᴏ ᴀᴄᴛɪᴠᴇ ꜰɪʟᴛᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ."
            )

        lines = []
        for keyword, data in all_filters.items():
            content_type = data.get("content_type", "Unknown")
            lines.append(f"• <code>{keyword}</code> → <i>{content_type}</i>")

        await message.reply_text(
            f"📝 <b>𝗔𝗰𝘁𝗶𝘃𝗲 𝗙𝗶𝗹𝘁𝗲𝗿𝘀</b>\n\n" + "\n".join(lines),
            parse_mode=enums.ParseMode.HTML,
        )

    # ==========================================================
    # Enforce — trigger filter on keyword match
    # ==========================================================
    @app.on_message(filters.group & filters.text & ~filters.service, group=11)
    async def enforce_filters(client, message: Message):
        if not message.text:
            return

        all_filters = await db.get_all_filters(message.chat.id)
        if not all_filters:
            return

        text_lower = message.text.lower()

        for keyword, data in all_filters.items():
            if keyword in text_lower:
                try:
                    content_type = data.get("content_type")
                    content = data.get("content")
                    file_id = data.get("file_id")

                    if content_type == "text":
                        await message.reply_text(content)

                    elif content_type == "sticker":
                        await message.reply_sticker(file_id)

                    elif content_type == "photo":
                        await message.reply_photo(file_id, caption=content or "")

                    elif content_type == "video":
                        await message.reply_video(file_id, caption=content or "")

                    elif content_type == "document":
                        await message.reply_document(file_id, caption=content or "")

                    elif content_type == "audio":
                        await message.reply_audio(file_id, caption=content or "")

                    elif content_type == "animation":
                        await message.reply_animation(file_id, caption=content or "")

                except Exception as e:
                    logger.exception(f"Filter trigger error: {e}")

                break
