# ============================================================
# Group Manager Bot — Utility (Updated)
# Author: Mr. Stark
# ============================================================
import urllib.parse
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatMemberStatus, ChatType, ChatMembersFilter
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

# Service messages clear karne ki setting store karne ke liye
# Production me isko database (like MongoDB/SQL) me store karna behtar hota hai
CLEAN_SERVICE_SETTINGS = {}

async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


UTILITY_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   ⚙️ 𝘂𝘁𝗶𝗹𝗶𝘁𝘆\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /chatinfo — 𝗴𝗲𝘁 𝗴𝗿𝗼𝘂𝗽 𝗱𝗲𝘁𝗮𝗶𝗹𝘀, 𝗶𝗱 & 𝗺𝗲𝗺𝗯𝗲𝗿 𝗰𝗼𝘂𝗻𝘁\n"
    "➻ /id — 𝗴𝗲𝘁 𝘆𝗼𝘂𝗿 𝗶𝗱 𝗼𝗿 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗴𝗲𝘁 𝘂𝘀𝗲𝗿 𝗶𝗱\n"
    "➻ /info — 𝗴𝗲𝘁 𝗱𝗲𝘁𝗮𝗶𝗹𝗲𝗱 𝘂𝘀𝗲𝗿 𝗶𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻 & 𝗯𝗶𝗼\n"
    "➻ /ping — 𝗰𝗵𝗲𝗰𝗸 𝗯𝗼𝘁 𝗿𝗲𝘀𝗽𝗼𝗻𝘀𝗲 𝘀𝗽𝗲𝗲𝗱\n"
    "➻ /pin, /unpin — 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗽𝗶𝗻/unpin 𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
    "➻ /pin 𝘀𝗶𝗹𝗲𝗻𝘁 — 𝗽𝗶𝗻 𝘄𝗶𝘁𝗵𝗼𝘂𝘁 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻\n"
    "➻ /del, /purge — 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀, 𝗳𝗿𝗼𝗺 𝗿𝗲𝗽𝗹𝗶𝗲𝗱 𝗺𝘀𝗴 𝘁𝗼 𝗻𝗼𝘄\n"
    "➻ /purgeme — 𝗱𝗲𝗹𝗲𝘁𝗲 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 𝗿𝗲𝗰𝗲𝗻𝘁 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
    "➻ /cleanservice 𝗼𝗻/off — 𝗲𝗻𝗮𝗯𝗹𝗲, 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗳𝗼𝗿 𝗷𝗼𝗶𝗻/leave 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
    "➻ /calc &lt;𝗲𝘅𝗽𝗿&gt; — 𝗯𝘂𝗶𝗹𝘁-𝗶𝗻 𝗰𝗮𝗹𝗰𝘂𝗹𝗮𝘁𝗼𝗿 𝗳𝗼𝗿 𝗾𝘂𝗶𝗰𝗸 𝗺𝗮𝘁𝗵\n"
    "➻ /carbon &lt;𝘁𝗲𝘅𝘁&gt; — 𝗰𝗼𝗻𝘃𝗲𝗿𝘁 𝗰𝗼𝗱𝗲 𝗼𝗿 𝘁𝗲𝘅𝘁 𝗶𝗻𝘁𝗼 𝗰𝗮𝗿𝗯𝗼𝗻 𝗶𝗺𝗮𝗴𝗲"
)


def register_utility_handler(app: Client):

    # ----------------------------------------------------------
    # /chatinfo
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("chatinfo"))
    async def chatinfo_cmd(client, message: Message):
        chat = message.chat
        try:
            count = await client.get_chat_members_count(chat.id)
        except Exception:
            count = "N/A"

        username  = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
        chat_type = str(chat.type).replace("ChatType.", "").capitalize()

        await message.reply_text(
            f"<u>𝗰𝗵𝗮𝘁 𝗶𝗻𝗳𝗼<u>\n\n"
            f"𝗻𝗮𝗺𝗲 : {chat.title}\n"
            f"𝗰𝗵𝗮𝘁 𝗶𝗱 : <code>{chat.id}</code>\n"
            f"𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : {username}\n"
            f"𝗺𝗲𝗺𝗯𝗲𝗿 𝗰𝗼𝘂𝗻𝘁 : {count}\n"
            f"𝗰𝗵𝗮𝘁 𝘁𝘆𝗽𝗲 : {chat_type}"
            "",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # /id
    # ----------------------------------------------------------
    @app.on_message(filters.command("id"))
    async def id_cmd(client, message: Message):
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            await message.reply_text(
                f"<u>𝘂𝘀𝗲𝗿 𝗶𝗻𝗳𝗼</u>\n\n"
                f"𝗻𝗮𝗺𝗲 : {user.first_name}\n"
                f"𝘂𝘀𝗲𝗿 𝗶𝗱 : <code>{user.id}</code>"
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        else:
            user = message.from_user
            text = (
                f"𝘆𝗼𝘂𝗿 𝗶𝗱 : <code>{user.id}</code>"
            )
            if message.chat.type != ChatType.PRIVATE:
                text += f"\n𝗰𝗵𝗮𝘁 𝗶𝗱 : <code>{message.chat.id}</code>"
                text += ""
                await message.reply_text(
                    text,
                    parse_mode=enums.ParseMode.HTML
                )            
    # ----------------------------------------------------------
    # /info [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.command("info"))
    async def info_cmd(client, message: Message):
        # Agar reply kiya hai to us user ki info, nahi to command bhejne wale ki info
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        else:
            target_user = message.from_user

        if not target_user:
            return await message.reply_text("⚠️ ᴜꜱᴇʀ ɪɴꜰᴏ ɴᴀʜɪ ᴍɪʟ ꜱᴀᴋɪ.", parse_mode=enums.ParseMode.HTML)

        try:
            # Full details (jaise Bio aur DC ID) fetch karne ke liye client.get_chat use kiya hai
            user_chat = await client.get_chat(target_user.id)
            bio = user_chat.bio if user_chat.bio else "ɴᴏ ʙɪᴏ ᴀᴠᴀɪʟᴀʙʟᴇ."
            dc_id = target_user.dc_id if target_user.dc_id else "Unknown"
        except Exception:
            bio = "ɴᴏ ʙɪᴏ ᴀᴠᴀɪʟᴀʙʟᴇ."
            dc_id = target_user.dc_id if target_user.dc_id else "Unknown"

        username = f"@{target_user.username}" if target_user.username else "None"

        info_text = (
            "<u>𝘂𝘀𝗲𝗿 𝗶𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻</u>\n\n"
            f"𝗻𝗮𝗺𝗲 : {target_user.first_name}\n"
            f"𝘂𝘀𝗲𝗿 𝗶𝗱 : <code>{target_user.id}</code>\n"
            f"𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : {username}\n"
            f"𝗱𝗰 𝗶𝗱 : {dc_id}\n"
            f"𝗯𝗶𝗼 : <code>{bio}</code>"
        )
        
        await message.reply_text(info_text, parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /ping [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message: Message):
        start_time = time.time()
        # Pehle message bhejenge latency calculate karne ke liye
        reply = await message.reply_text("⚡ ᴘɪɴɢɪɴɢ...", parse_mode=enums.ParseMode.HTML)
        end_time = time.time()
        
        ping_speed = round((end_time - start_time) * 1000)
        await reply.edit_text(
            f"🏓 𝗣𝗼𝗻𝗴!\n"
            f"⚡ 𝗦𝗽𝗲𝗲𝗱: <code>{ping_speed} ᴍꜱ</code>"
            f"",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # /pin [silent]
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("pin"))
    async def pin_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴘɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ.", parse_mode=enums.ParseMode.HTML)

        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘɪɴ.", parse_mode=enums.ParseMode.HTML)

        args = message.text.split(maxsplit=1)
        silent = len(args) > 1 and args[1].strip().lower() == "silent"

        try:
            await client.pin_chat_message(
                message.chat.id,
                message.reply_to_message.id,
                disable_notification=silent
            )
            label = "ꜱɪʟᴇɴᴛʟʏ " if silent else ""
            await message.reply_text(f"📌 ᴍᴇꜱꜱᴀɢᴇ {label}ᴘɪɴɴᴇᴅ!", parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘɪɴ: {e}", parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /unpin
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("unpin"))
    async def unpin_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜɴᴘɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ.", parse_mode=enums.ParseMode.HTML)

        try:
            if message.reply_to_message:
                await client.unpin_chat_message(
                    message.chat.id, message.reply_to_message.id
                )
                await message.reply_text("📌 ᴍᴇꜱꜱᴀɢᴇ ᴜɴᴘɪɴɴᴇᴅ.", parse_mode=enums.ParseMode.HTML)
            else:
                await client.unpin_all_chat_messages(message.chat.id)
                await message.reply_text("📌 ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴜɴᴘɪɴɴᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴᴘɪɴ: {e}", parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /purge
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("purge"))
    async def purge_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴘᴜʀɢᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.", parse_mode=enums.ParseMode.HTML)

        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴘᴜʀɢɪɴɢ ꜰʀᴏᴍ.", parse_mode=enums.ParseMode.HTML)

        from_id = message.reply_to_message.id
        to_id   = message.id
        ids     = list(range(from_id, to_id + 1))

        deleted = 0
        for i in range(0, len(ids), 100):
            try:
                await client.delete_messages(message.chat.id, ids[i:i + 100])
                deleted += len(ids[i:i + 100])
            except Exception as e:
                logger.error(f"ᴘᴜʀɢᴇ ʙᴀᴛᴄʜ ᴇʀʀᴏʀ: {e}")

        confirm = await client.send_message(
            message.chat.id,
            f"🗑 {deleted} ᴍᴇꜱꜱᴀɢᴇꜱ ᴅᴇʟᴇᴛᴇᴅ.",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(3)
        try:
            await confirm.delete()
        except Exception:
            pass

    # ----------------------------------------------------------
    # /purgeme [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("purgeme"))
    async def purgeme_cmd(client, message: Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # User ke messages dhoodhne ke liye history search karenge (Max last 100 messages)
        msg_ids_to_delete = []
        async for msg in client.get_chat_history(chat_id, limit=100):
            if msg.from_user and msg.from_user.id == user_id:
                msg_ids_to_delete.append(msg.id)
                
        if not msg_ids_to_delete:
            return await message.reply_text("⚠️ ᴀᴀᴘᴋᴀ ᴋᴏɪ ᴘᴜʀᴀɴᴀ ᴍᴇꜱꜱᴀɢᴇ ɴᴀʜɪ ᴍɪʟᴀ.", parse_mode=enums.ParseMode.HTML)
            
        try:
            await client.delete_messages(chat_id, msg_ids_to_delete)
            confirm = await client.send_message(
                chat_id,
                f"🗑 ᴅᴇʟᴇᴛᴇᴅ {len(msg_ids_to_delete)} ᴏꜰ ʏᴏᴜʀ ʀᴇᴄᴇɴᴛ ᴍᴇꜱꜱᴀɢᴇꜱ.",
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(3)
            await confirm.delete()
        except Exception as e:
            logger.error(f"ᴘᴜʀɢᴇᴍᴇ ᴇʀʀᴏʀ: {e}")

    # ----------------------------------------------------------
    # /del
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("del"))
    async def del_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.", parse_mode=enums.ParseMode.HTML)

        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ.", parse_mode=enums.ParseMode.HTML)

        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴅᴇʟᴇᴛᴇ: {e}", parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /cleanservice [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("cleanservice"))
    async def cleanservice_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ꜱᴇᴛᴛɪɴɢꜱ.", parse_mode=enums.ParseMode.HTML)

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            current = "ON" if CLEAN_SERVICE_SETTINGS.get(message.chat.id, False) else "OFF"
            return await message.reply_text(
                f"➻ 𝗖𝗹𝗲𝗮𝗻 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {current}\n"
                f"ᴜꜱᴀɢᴇ: <code>/cleanservice ᴏɴ</code> ᴏʀ <code>/cleanservice ᴏꜰꜰ</code>"
                f"",
                parse_mode=enums.ParseMode.HTML
            )

        action = parts[1].strip().lower()
        if action == "on":
            CLEAN_SERVICE_SETTINGS[message.chat.id] = True
            await message.reply_text("✅ 𝗖𝗹𝗲𝗮𝗻 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 𝘁𝘂𝗿𝗻𝗲𝗱 𝗢𝗡. ᴊᴏɪɴ/Leave ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        elif action == "off":
            CLEAN_SERVICE_SETTINGS[message.chat.id] = False
            await message.reply_text("❌ 𝗖𝗹𝗲𝗮𝗻 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 𝘁𝘂𝗿𝗻𝗲𝗱 𝗢𝗙𝗙. ᴊᴏɪɴ/Leave ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ɴᴏᴛ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ. ᴜꜱᴇ <code>ᴏɴ</code> ᴏʀ <code>ᴏꜰꜰ</code>.", parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # Clean Service Handler Logic [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.group & (filters.new_chat_members | filters.left_chat_member))
    async def service_msg_cleaner(client, message: Message):
        # Agar is group ke liye Clean Service toggled 'ON' hai to message delete ho jayega
        if CLEAN_SERVICE_SETTINGS.get(message.chat.id, False):
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ꜱᴇʀᴠɪᴄᴇ ᴍᴇꜱꜱᴀɢᴇ: {e}")

    # ----------------------------------------------------------
    # /calc — calculator for everyone
    # ----------------------------------------------------------
    @app.on_message(filters.command("calc"))
    async def calc_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "🧮 𝗖𝗮𝗹𝗰𝘂𝗹𝗮𝘁𝗼𝗿\n\n"
                "ᴜꜱᴀɢᴇ: <code>/calc 2 + 2</code>\n"
                "ꜱᴜᴘᴘᴏʀᴛꜱ: <code>+ - * / ** % // ( )</code>"
                "",
                parse_mode=enums.ParseMode.HTML
            )

        expr = parts[1].strip()

        # Safety: only allow math characters
        import re as _re
        safe = _re.sub(r'[^0-9+\-*/().%\s]', '', expr)
        if not safe.strip():
            return await message.reply_text(
                "⚠️ ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇꜱꜱɪᴏɴ. ᴏɴʟʏ ɴᴜᴍʙᴇʀꜱ ᴀɴᴅ <code>+ - * / % ( )</code> ᴀʟʟᴏᴡᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        try:
            # Use Python eval with restricted builtins
            result = eval(
                safe,
                {"__builtins__": {}},
                {"abs": abs, "round": round, "pow": pow}
            )
            # Format result nicely
            if isinstance(result, float) and result == int(result):
                result = int(result)
            await message.reply_text(
                f"🧮 <code>{expr}</code>\n"
                f"= {result}"
                f"",
                parse_mode=enums.ParseMode.HTML
            )
        except ZeroDivisionError:
            await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴅɪᴠɪᴅᴇ ʙʏ ᴢᴇʀᴏ.", parse_mode=enums.ParseMode.HTML)
        except Exception:
            await message.reply_text(
                f"⚠️ ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇꜱꜱɪᴏɴ: <code>{expr}</code>",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /carbon <text> [NEW]
    # ----------------------------------------------------------
    @app.on_message(filters.command("carbon"))
    async def carbon_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 and not message.reply_to_message:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: <code>/carbon [ᴛᴇxᴛ]</code> ʏᴀ ᴋɪꜱɪ ᴛᴇxᴛ ᴍᴇꜱꜱᴀɢᴇ ᴋᴏ ʀᴇᴘʟʏ ᴋᴀʀᴇɪɴ.", parse_mode=enums.ParseMode.HTML)

        code_text = parts[1] if len(parts) >= 2 else message.reply_to_message.text
        status_msg = await message.reply_text("🎨 ᴄʀᴇᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ ɪᴍᴀɢᴇ...", parse_mode=enums.ParseMode.HTML)
        
        # Rayso API code generate karne ke liye
        encoded_code = urllib.parse.quote(code_text)
        carbon_url = f"https://rayso.api.stdlib.com/art@v1/?text={encoded_code}&theme=breeze&title=Carbon&watermark=false"
        
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=carbon_url,
                caption="🎨 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝘃𝗶𝗮 𝗥𝗮𝘆.𝘀𝗼",
                parse_mode=enums.ParseMode.HTML
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ: {e}", parse_mode=enums.ParseMode.HTML)
