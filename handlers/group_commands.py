# ============================================================
# Group Manager Bot — Group Commands
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    Message, ChatPermissions,
    ChatPrivileges, InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions
import re
import asyncio
import logging
import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

URL_PATTERN = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|t\.me/[^\s]+|http?://[^\s]+)",
    re.IGNORECASE
)

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002B00-\U00002BFF"
    "\U0001F000-\U0001F0FF"
    "\U0000FE00-\U0000FE0F"
    "\U00002190-\U000021FF"
    "]+",
    flags=re.UNICODE
)

# ==========================================================
# Permission sets for Telegram group locks
# ==========================================================

ALL_OPEN = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_send_polls=True,
)

# ==========================================================
# Global helpers
# ==========================================================

async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


async def extract_target_user(client, message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    arg = parts[1]
    try:
        if arg.startswith("@"):
            return await client.get_users(arg)
        elif arg.isdigit():
            return await client.get_users(int(arg))
    except:
        return None



async def user_has_bio_link(client, user_id: int) -> bool:
    try:
        input_user = await client.resolve_peer(user_id)
        full = await client.invoke(functions.users.GetFullUser(id=input_user))
        bio = ""
        if hasattr(full, "full_user") and full.full_user:
            bio = getattr(full.full_user, "about", None) or ""
        elif hasattr(full, "about"):
            bio = getattr(full, "about", None) or ""
        if not bio:
            return False
        if URL_PATTERN.search(bio):
            return True
        if "t.me/" in bio.lower() or "http" in bio.lower() or "www." in bio.lower():
            return True
    except Exception as e:
        logger.error(f"ʙɪᴏ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ ꜰᴏʀ {user_id}: {e}")
    return False


async def apply_group_permissions(client, chat_id: int, locks: dict):
    """
    ᴀᴘᴘʟʏ ᴛᴇʟᴇɢʀᴀᴍ-ɴᴀᴛɪᴠᴇ ɢʀᴏᴜᴘ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ꜰᴏʀ ᴍᴇᴅɪᴀ/text/sticker/files/music ʟᴏᴄᴋꜱ.
    ᴛʜᴇꜱᴇ ᴘʀᴇᴠᴇɴᴛ ꜱᴇɴᴅɪɴɢ ʀᴀᴛʜᴇʀ ᴛʜᴀɴ ᴅᴇʟᴇᴛɪɴɢ ᴀꜰᴛᴇʀ ꜱᴇɴᴅ.
    """
    perms = ChatPermissions(
        can_send_messages=not locks.get("text", False),
        can_send_media_messages=not locks.get("media", False),
        can_send_other_messages=not (locks.get("sticker", False)),
        can_send_polls=True,
        can_add_web_page_previews=True,
    )
    try:
        await client.set_chat_permissions(chat_id, perms)
    except Exception as e:
        logger.error(f"ꜱᴇᴛ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴇʀʀᴏʀ: {e}")


def register_group_commands(app: Client):


    # ==========================================================
    # Lock — updated with new types + Telegram-native permissions
    # ==========================================================

    # Delete-based locks (bot deletes message after it is sent)
    # media and files are HERE — Telegram API cannot split photo/video/doc
    # into separate permission bits, so we handle them with deletion
    DELETE_LOCKS = ["url", "username", "forward", "edit", "media", "files", "emoji"]

    # Permission-based locks (Telegram group permissions)
    PERM_LOCKS = ["text", "sticker", "music"]

    VALID_LOCKS = DELETE_LOCKS + PERM_LOCKS

    async def _apply_lock_perms(client, chat_id, locks):
        """ᴜᴘᴅᴀᴛᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ꜰᴏʀ ᴛᴇxᴛ/sticker/music ᴘᴇʀᴍ ʟᴏᴄᴋꜱ."""
        perms = ChatPermissions(
            can_send_messages=not locks.get("text", False),
            can_send_media_messages=True,     # media/files handled by delete
            can_send_other_messages=not locks.get("sticker", False),
            can_send_polls=True,
            can_add_web_page_previews=True,
        )
        try:
            await client.set_chat_permissions(chat_id, perms)
        except Exception as e:
            logger.error(f"ᴘᴇʀᴍ ʟᴏᴄᴋ ᴇʀʀᴏʀ: {e}")


    @app.on_message(filters.group & filters.command("lock"))
    async def lock_command(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: /lock &lt;ᴛʏᴘᴇ&gt;\n\n"
                f"𝗗𝗲𝗹𝗲𝘁𝗲-𝗯𝗮𝘀𝗲𝗱: {', '.join(f'<code>{l}</code>' for l in DELETE_LOCKS)}\n"
                f"𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻-𝗯𝗮𝘀𝗲𝗱: {', '.join(f'<code>{l}</code>' for l in PERM_LOCKS)}",
                parse_mode=enums.ParseMode.HTML
            )
        lock_type = parts[1].lower()
        if lock_type not in VALID_LOCKS:
            return await message.reply_text(
                f"⚠️ ᴀᴠᴀɪʟᴀʙʟᴇ ʟᴏᴄᴋꜱ: {', '.join(f'<code>{l}</code>' for l in VALID_LOCKS)}",
                parse_mode=enums.ParseMode.HTML
            )
        await db.set_lock(message.chat.id, lock_type, True)

        # Apply Telegram permissions for perm locks
        if lock_type in PERM_LOCKS:
            locks = await db.get_locks(message.chat.id)
            await _apply_lock_perms(client, message.chat.id, locks)

        await message.reply_text(f"🔒 <code>{lock_type}</code> ʟᴏᴄᴋ ᴇɴᴀʙʟᴇᴅ!", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Unlock
    # ==========================================================

    @app.on_message(filters.group & filters.command("unlock"))
    async def unlock_command(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: /unlock &lt;ᴛʏᴘᴇ&gt;\n\nᴀᴠᴀɪʟᴀʙʟᴇ: {', '.join(f'<code>{l}</code>' for l in VALID_LOCKS)}",
                parse_mode=enums.ParseMode.HTML
            )
        lock_type = parts[1].lower()
        if lock_type not in VALID_LOCKS:
            return await message.reply_text(
                f"⚠️ ᴀᴠᴀɪʟᴀʙʟᴇ: {', '.join(f'<code>{l}</code>' for l in VALID_LOCKS)}",
                parse_mode=enums.ParseMode.HTML
            )
        await db.set_lock(message.chat.id, lock_type, False)

        if lock_type in PERM_LOCKS:
            locks = await db.get_locks(message.chat.id)
            await _apply_lock_perms(client, message.chat.id, locks)

        await message.reply_text(f"🔓 <code>{lock_type}</code> ʟᴏᴄᴋ ᴅɪꜱᴀʙʟᴇᴅ!", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Locks list
    # ==========================================================

    @app.on_message(filters.group & filters.command("locks"))
    async def locks_list(client, message):
        locks = await db.get_locks(message.chat.id)

        # All lock types with descriptions
        ALL_LOCK_INFO = {
            "text":     ("🔤", "ᴛᴇxᴛ ᴍᴇꜱꜱᴀɢᴇꜱ"),
            "media":    ("🖼",  "ᴘʜᴏᴛᴏꜱ & ᴠɪᴅᴇᴏꜱ"),
            "files":    ("📎", "ᴅᴏᴄᴜᴍᴇɴᴛꜱ & ꜰɪʟᴇꜱ"),
            "sticker":  ("🎭", "ꜱᴛɪᴄᴋᴇʀꜱ & ɢɪꜰꜱ"),
            "music":    ("🎵", "ᴀᴜᴅɪᴏ & ᴠᴏɪᴄᴇ"),
            "url":      ("🔗", "ᴜʀʟꜱ & ʟɪɴᴋꜱ"),
            "username": ("👤", "ᴜꜱᴇʀɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴꜱ"),
            "forward":  ("↩️", "ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ"),
            "edit":     ("✏️",  "ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ"),
            "emoji":    ("😀", "ᴇᴍᴏᴊɪ ɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ"),
        }

        text = (
            "╔═══════════════╗\n"
            "   🔐 𝗹𝗼𝗰𝗸𝘀 𝘀𝘁𝗮𝘁𝘂𝘀\n"
            "╚═══════════════╝\n\n"
        )
        for lock_key, (emoji, desc) in ALL_LOCK_INFO.items():
            is_on = locks.get(lock_key, False)
            status = "🔒 𝗢𝗡 " if is_on else "🔓 𝗢𝗙𝗙"
            text += f"<code>{lock_key:<10}</code>: {status}\n"
        text += ""

        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Lockall
    # ==========================================================

    @app.on_message(filters.group & filters.command("lockall"))
    async def lockall_command(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        for lock_type in VALID_LOCKS:
            await db.set_lock(message.chat.id, lock_type, True)
        locks = await db.get_locks(message.chat.id)
        await _apply_lock_perms(client, message.chat.id, locks)
        locked_list = "\n".join(f"🔒 <code>{l}</code>" for l in VALID_LOCKS)
        await message.reply_text(f"🔐 𝗘𝗩𝗘𝗥𝗬𝗧𝗛𝗜𝗡𝗚 𝗟𝗢𝗖𝗞𝗘𝗗!", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Unlockall
    # ==========================================================

    @app.on_message(filters.group & filters.command("unlockall"))
    async def unlockall_command(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        for lock_type in VALID_LOCKS:
            await db.set_lock(message.chat.id, lock_type, False)
        # Restore all permissions
        try:
            await client.set_chat_permissions(message.chat.id, ALL_OPEN)
        except Exception as e:
            logger.error(f"ᴜɴʟᴏᴄᴋᴀʟʟ ᴘᴇʀᴍ ᴇʀʀᴏʀ: {e}")
        await message.reply_text("🔓 ᴜɴʟᴏᴄᴋᴇᴅ!\n\n𝗻𝗼𝘄 𝗲𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴 𝗶𝘀 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗶𝗻 𝘁𝗵𝗲 𝗴𝗿𝗼𝘂𝗽.", parse_mode=enums.ParseMode.HTML)


    # ==========================================================
    # Enforce delete-based locks
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=1)
    async def enforce_locks(client, message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return

        locks = await db.get_locks(message.chat.id)
        if not locks:
            return

        # URL lock
        if locks.get("url") and message.text:
            if message.entities:
                for ent in message.entities:
                    if ent.type.name in ["URL", "TEXT_LINK"]:
                        return await message.delete()
            if "t.me/" in message.text.lower() or "http" in message.text.lower():
                return await message.delete()

        # Username mention lock
        if locks.get("username") and message.text and "@" in message.text:
            return await message.delete()

        # Forward lock
        if locks.get("forward") and (message.forward_from or message.forward_from_chat):
            return await message.delete()

        # Media lock — delete photo AND video messages
        if locks.get("media"):
            if message.photo or message.video or message.video_note or message.animation:
                return await message.delete()

        # Files lock — delete document/audio/voice messages
        if locks.get("files"):
            if message.document or message.audio or message.voice:
                return await message.delete()

        # Emoji lock — delete any message containing an emoji
        if locks.get("emoji") and message.text and EMOJI_PATTERN.search(message.text):
            return await message.delete()

        # BioLink check
        biolink_on = await db.get_biolink_status(message.chat.id)
        if biolink_on:
            has_link = await user_has_bio_link(client, message.from_user.id)
            if has_link:
                bioconfig = await db.get_bioconfig(message.chat.id)
                action = bioconfig.get("action", "delete")
                warn_limit = bioconfig.get("warn_limit", 0)

                try:
                    await message.delete()
                except Exception:
                    pass

                if action == "delete":
                    # Just delete, send warning msg then auto-delete after 60s
                    try:
                        warn_msg = await client.send_message(
                            message.chat.id,
                            f"🌺 {message.from_user.mention}, ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴅᴇʟᴇᴛᴇᴅ ʙᴇᴄᴀᴜꜱᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴀ ʟɪɴᴋ ɪɴ ʏᴏᴜʀ ʙɪᴏ.\n\n"
                            f"📛 ᴘʟᴇᴀꜱᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ ꜰʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ ꜰɪʀꜱᴛ."
                            f"",
                        )
                        asyncio.get_event_loop().create_task(_delete_after(warn_msg, 300))
                    except Exception as e:
                        logger.error(f"ʙɪᴏʟɪɴᴋ ᴡᴀʀɴ ᴇʀʀᴏʀ: {e}")

                elif action in ["mute", "ban"] and warn_limit > 0:
                    # Warning system
                    warns = await db.add_biolink_warn(message.chat.id, message.from_user.id)
                    remaining = warn_limit - warns

                    if warns >= warn_limit:
                        await db.reset_biolink_warns(message.chat.id, message.from_user.id)
                        try:
                            if action == "mute":
                                await client.restrict_chat_member(
                                    message.chat.id,
                                    message.from_user.id,
                                    permissions=ChatPermissions(can_send_messages=False)
                                )
                                msg = await client.send_message(
                                    message.chat.id,
                                    f"🔇 {message.from_user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ᴀꜰᴛᴇʀ {warn_limit} ʙɪᴏʟɪɴᴋ ᴠɪᴏʟᴀᴛɪᴏɴꜱ."
                                )
                            else:
                                await client.ban_chat_member(message.chat.id, message.from_user.id)
                                msg = await client.send_message(
                                    message.chat.id,
                                    f"🚨 {message.from_user.mention} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ᴀꜰᴛᴇʀ {warn_limit} ʙɪᴏʟɪɴᴋ ᴠɪᴏʟᴀᴛɪᴏɴꜱ."
                                )
                            asyncio.get_event_loop().create_task(_delete_after(msg, 300))
                        except Exception as e:
                            logger.error(f"ʙɪᴏʟɪɴᴋ ᴀᴄᴛɪᴏɴ ᴇʀʀᴏʀ: {e}")
                    else:
                        try:
                            msg = await client.send_message(
                                message.chat.id,
                                f"⚠️ {message.from_user.mention}, ʙɪᴏ ʟɪɴᴋ ᴡᴀʀɴɪɴɢ {warns}/{warn_limit}.\n"
                                f"ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ ꜰʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ ᴏʀ ʏᴏᴜ ᴡɪʟʟ ʙᴇ {action}d."
                            )
                            asyncio.get_event_loop().create_task(_delete_after(msg, 300))
                        except Exception as e:
                            logger.error(f"ʙɪᴏʟɪɴᴋ ᴡᴀʀɴ ᴍꜱɢ ᴇʀʀᴏʀ: {e}")
                return


    # ==========================================================
    # Enforce edit lock
    # ==========================================================

    @app.on_edited_message(filters.group, group=1)
    async def enforce_edit_lock(client, message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except:
            return
        locks = await db.get_locks(message.chat.id)
        if locks.get("edit"):
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"ᴇᴅɪᴛ ʟᴏᴄᴋ ᴇʀʀᴏʀ: {e}")


    # ==========================================================
    # Helper — delete message after delay
    # ==========================================================

    async def _delete_after(msg, delay: int):
        await asyncio.sleep(delay)
        try:
            await msg.delete()
        except Exception:
            pass


    # ==========================================================
    # BioLink toggle — shows inline settings after /biolink on
    # ==========================================================

    def _biolink_settings_markup(chat_id: int, config: dict) -> tuple:
        """ʀᴇᴛᴜʀɴ (ᴛᴇxᴛ, ᴍᴀʀᴋᴜᴘ) ꜰᴏʀ ᴛʜᴇ ʙɪᴏʟɪɴᴋ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ."""
        action = config.get("action", "delete")
        warn_limit = config.get("warn_limit", 0)

        action_label = {
            "delete": "🗑 ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ",
            "mute": f"🔇 ᴍᴜᴛᴇ ᴀꜰᴛᴇʀ {warn_limit} ᴡᴀʀɴꜱ",
            "ban": f"🚨 ʙᴀɴ ᴀꜰᴛᴇʀ {warn_limit} ᴡᴀʀɴꜱ",
        }.get(action, "🗑 ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ")

        text = (
            "⚙️ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀\n\n"
            f"📊 ꜱᴛᴀᴛᴜꜱ: 🟢 𝗢𝗡\n"
            f"🎯 ᴀᴄᴛɪᴏɴ: {action_label}\n\n"
            "ᴄʜᴏᴏꜱᴇ ᴡʜᴀᴛ ᴛᴏ ᴅᴏ ᴡʜᴇɴ ᴀ ᴜꜱᴇʀ ᴡɪᴛʜ ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ ꜱᴇɴᴅꜱ ᴀ ᴍᴇꜱꜱᴀɢᴇ:"
        )
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 ʙᴀɴ", callback_data=f"bc_action_{chat_id}_ban", style=ButtonStyle.DANGER),
                InlineKeyboardButton("🔇 ᴍᴜᴛᴇ", callback_data=f"bc_action_{chat_id}_mute", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("🗑 ᴅᴇʟᴇᴛᴇ", callback_data=f"bc_action_{chat_id}_delete", style=ButtonStyle.PRIMARY),
            ]
        ])
        return text, markup

    @app.on_message(filters.group & filters.command("biolink"))
    async def biolink_toggle(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴏʀ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        chat_id = message.chat.id

        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_biolink_status(chat_id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/biolink ᴏɴ</code> ᴏʀ <code>/biolink ᴏꜰꜰ</code>\n\n"
                f"📊 ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {current}",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_biolink_status(chat_id, status)

        if status:
            # Show action settings immediately
            config = await db.get_bioconfig(chat_id)
            text, markup = _biolink_settings_markup(chat_id, config)
            msg = await message.reply_text(
                "✅ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗢𝗡!\n\n"
                + text,
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML
            )
            asyncio.get_event_loop().create_task(_delete_after(msg, 300))
        else:
            await message.reply_text(
                "⚠️ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗢𝗙𝗙!",
                parse_mode=enums.ParseMode.HTML
            )


    # ==========================================================
    # /bioconfig — configure biolink action with inline buttons
    # ==========================================================

    @app.on_message(filters.group & filters.command("bioconfig"))
    async def bioconfig_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄᴏɴꜰɪɢᴜʀᴇ ᴛʜɪꜱ.")

        chat_id = message.chat.id
        config = await db.get_bioconfig(chat_id)
        text, markup = _biolink_settings_markup(chat_id, config)

        msg = await message.reply_text(
            text,
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML
        )
        asyncio.get_event_loop().create_task(_delete_after(msg, 300))


    @app.on_callback_query(filters.regex(r"^bc_action_(-?\d+)_(delete|mute|ban)$"))
    async def bioconfig_action_callback(client, callback_query):
        chat_id = int(callback_query.matches[0].group(1))
        action = callback_query.matches[0].group(2)

        if not await is_power(client, chat_id, callback_query.from_user.id):
            return await callback_query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄᴏɴꜰɪɢᴜʀᴇ ᴛʜɪꜱ.", show_alert=True)

        if action == "delete":
            # No warning needed — just save and show confirm
            await db.set_bioconfig(chat_id, action="delete", warn_limit=0)
            await callback_query.message.edit_text(
                "✅ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 → 𝗗𝗲𝗹𝗲𝘁𝗲 𝗢𝗻𝗹𝘆\n\n"
                "ᴍᴇꜱꜱᴀɢᴇꜱ ꜰʀᴏᴍ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ʙɪᴏ ʟɪɴᴋꜱ ᴡɪʟʟ ʙᴇ ꜱɪʟᴇɴᴛʟʏ ᴅᴇʟᴇᴛᴇᴅ.\n"
                "ɴᴏ ᴡᴀʀɴɪɴɢꜱ ꜱᴇɴᴛ ᴛᴏ ᴜꜱᴇʀ.",
                parse_mode=enums.ParseMode.HTML
            )
            asyncio.get_event_loop().create_task(_delete_after(callback_query.message, 300))
            await callback_query.answer("✅ ꜱᴀᴠᴇᴅ: ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ")
        else:
            # Show warn limit buttons: 3, 4, 5
            action_emoji = "🔇" if action == "mute" else "🚨"
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("3️⃣ 3 ᴡᴀʀɴꜱ", callback_data=f"bc_warn_{chat_id}_{action}_3", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("4️⃣ 4 ᴡᴀʀɴꜱ", callback_data=f"bc_warn_{chat_id}_{action}_4", style=ButtonStyle.PRIMARY),
                    InlineKeyboardButton("5️⃣ 5 ᴡᴀʀɴꜱ", callback_data=f"bc_warn_{chat_id}_{action}_5", style=ButtonStyle.PRIMARY),
                ],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data=f"bc_back_{chat_id}", style=ButtonStyle.PRIMARY)]
            ])
            await callback_query.message.edit_text(
                f"⚙️ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 → {action_emoji} {action.capitalize()}\n\n"
                f"ᴀꜰᴛᴇʀ ʜᴏᴡ ᴍᴀɴʏ ᴠɪᴏʟᴀᴛɪᴏɴꜱ ꜱʜᴏᴜʟᴅ ᴛʜᴇ ᴜꜱᴇʀ ʙᴇ {action}d?\n\n"
                f"📌 <i>ᴇᴀᴄʜ ᴠɪᴏʟᴀᴛɪᴏɴ: ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴅᴇʟᴇᴛᴇᴅ + ᴡᴀʀɴɪɴɢ ꜱᴇɴᴛ.\n"
                f"ᴏɴ ꜰɪɴᴀʟ ᴡᴀʀɴ: ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ + {action} ᴀᴘᴘʟɪᴇᴅ.</i>",
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
            await callback_query.answer()


    @app.on_callback_query(filters.regex(r"^bc_warn_(-?\d+)_(mute|ban)_(\d+)$"))
    async def bioconfig_warn_callback(client, callback_query):
        chat_id = int(callback_query.matches[0].group(1))
        action = callback_query.matches[0].group(2)
        warn_limit = int(callback_query.matches[0].group(3))

        if not await is_power(client, chat_id, callback_query.from_user.id):
            return await callback_query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄᴏɴꜰɪɢᴜʀᴇ ᴛʜɪꜱ.", show_alert=True)

        await db.set_bioconfig(chat_id, action=action, warn_limit=warn_limit)
        action_emoji = "🔇" if action == "mute" else "🚨"
        await callback_query.message.edit_text(
            f"✅ 𝗕𝗶𝗼𝗟𝗶𝗻𝗸 𝗖𝗼𝗻𝗳𝗶𝗴 𝗦𝗮𝘃𝗲𝗱!\n\n"
            f"ᴀᴄᴛɪᴏɴ: {action_emoji} {action.capitalize()}\n"
            f"ᴛʀɪɢɢᴇʀ ᴀꜰᴛᴇʀ: {warn_limit} ᴠɪᴏʟᴀᴛɪᴏɴꜱ\n\n"
            f"📌 ᴏɴ ᴇᴀᴄʜ ᴠɪᴏʟᴀᴛɪᴏɴ: ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ + ᴡᴀʀɴ ꜱᴇɴᴛ.\n"
            f"📌 ᴏɴ ᴡᴀʀɴ {warn_limit}: {action} ᴀᴘᴘʟɪᴇᴅ + ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.",
            parse_mode=enums.ParseMode.HTML
        )
        asyncio.get_event_loop().create_task(_delete_after(callback_query.message, 300))
        await callback_query.answer(f"✅ ꜱᴀᴠᴇᴅ: {action} ᴀꜰᴛᴇʀ {warn_limit} ᴡᴀʀɴꜱ")


    @app.on_callback_query(filters.regex(r"^bc_back_(-?\d+)$"))
    async def bioconfig_back_callback(client, callback_query):
        chat_id = int(callback_query.matches[0].group(1))

        if not await is_power(client, chat_id, callback_query.from_user.id):
            return await callback_query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ.", show_alert=True)

        config = await db.get_bioconfig(chat_id)
        text, markup = _biolink_settings_markup(chat_id, config)
        await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
        await callback_query.answer()


    # ==========================================================
    # Kick
    # ==========================================================

    @app.on_message(filters.group & filters.command("kick"))
    async def kick_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /kick @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"👢 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴋɪᴄᴋᴇᴅ.")
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴋɪᴄᴋ: {e}")


    # ==========================================================
    # Ban
    # ==========================================================

    @app.on_message(filters.group & filters.command("ban"))
    async def ban_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /ban @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"🚨 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.")
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ: {e}")


    # ==========================================================
    # Unban
    # ==========================================================

    @app.on_message(filters.group & filters.command("unban"))
    async def unban_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /unban @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴜɴʙᴀɴ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"✅ {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.")
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ: {e}")


    # ==========================================================
    # Mute
    # ==========================================================

    @app.on_message(filters.group & filters.command("mute"))
    async def mute_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /mute @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            await message.reply_text(f"🔇 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ.")
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴍᴜᴛᴇ: {e}")


    # ==========================================================
    # Silent Mute — /smute
    # ==========================================================

    @app.on_message(filters.group & filters.command("smute"))
    async def smute_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /smute @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            # Delete the command message silently
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # Unmute
    # ==========================================================

    @app.on_message(filters.group & filters.command("unmute"))
    async def unmute_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /unmute @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴜɴᴍᴜᴛᴇ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            await message.reply_text(f"🔊 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴜɴᴍᴜᴛᴇᴅ.")
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴍᴜᴛᴇ: {e}")


    # ==========================================================
    # Silent Ban — /sban
    # ==========================================================

    @app.on_message(filters.group & filters.command("sban"))
    async def sban_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /sban @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴘᴇʀꜰᴏʀᴍ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀᴅᴍɪɴꜱ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            # Delete the command message silently
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # /dkick — Kick user by reply + delete their message
    # ==========================================================

    @app.on_message(filters.group & filters.command("dkick"))
    async def dkick_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ'ꜱ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴜꜱᴇ /dkick.")
        user = message.reply_to_message.from_user
        if not user:
            return await message.reply_text("⚠️ ᴄᴏᴜʟᴅ ɴᴏᴛ ɪᴅᴇɴᴛɪꜰʏ ᴜꜱᴇʀ.")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ᴀɴ ᴀᴅᴍɪɴ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            # Delete the user's message
            await message.reply_to_message.delete()
            # Kick (ban then unban)
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(
                f"👢 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴋɪᴄᴋᴇᴅ ᴀɴᴅ ᴛʜᴇɪʀ ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # /skick — Silently kick user, delete your command message
    # ==========================================================

    @app.on_message(filters.group & filters.command("skick"))
    async def skick_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        user = await extract_target_user(client, message)
        if not user:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ /skick @ᴜꜱᴇʀɴᴀᴍᴇ")
        target_member = await client.get_chat_member(message.chat.id, user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ᴀɴ ᴀᴅᴍɪɴ.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ʏᴏᴜʀꜱᴇʟꜰ.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            # Delete the command message silently
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # Tmute
    # ==========================================================

    def _parse_time(arg: str):
        """ᴘᴀʀꜱᴇ ᴛɪᴍᴇ ꜱᴛʀɪɴɢ ʟɪᴋᴇ 30ꜱ 10ᴍ 2ʜ 1ᴅ ɪɴᴛᴏ ꜱᴇᴄᴏɴᴅꜱ. ʀᴇᴛᴜʀɴꜱ (ꜱᴇᴄᴏɴᴅꜱ, ʟᴀʙᴇʟ) ᴏʀ ɴᴏɴᴇ."""
        import re as _re
        m = _re.fullmatch(r"(\d+)(s|m|h|d)", arg.strip().lower())
        if not m:
            return None, None
        v, u = int(m.group(1)), m.group(2)
        mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        return v * mult[u], arg.strip()

    @app.on_message(filters.group & filters.command("tmute"))
    async def tmute_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=2)

        if message.reply_to_message:
            user  = message.reply_to_message.from_user
            targ  = parts[1] if len(parts) > 1 else None
        else:
            user  = await extract_target_user(client, message)
            targ  = parts[2] if len(parts) > 2 else None

        if not user or not targ:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/tmute @ᴜꜱᴇʀ 10ᴍ</code> ᴏʀ ʀᴇᴘʟʏ ᴡɪᴛʜ <code>/tmute 2ʜ</code>\n"
                "ꜱᴜᴘᴘᴏʀᴛᴇᴅ: <code>30ꜱ</code> <code>10ᴍ</code> <code>2ʜ</code> <code>1ᴅ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        seconds, label = _parse_time(targ)
        if not seconds:
            return await message.reply_text(
                "⚠️ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ!\nᴜꜱᴇ: <code>30ꜱ</code> <code>10ᴍ</code> <code>2ʜ</code> <code>1ᴅ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        target = await client.get_chat_member(message.chat.id, user.id)
        if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ.")

        from datetime import datetime, timedelta
        until = datetime.utcnow() + timedelta(seconds=seconds)
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )
            await message.reply_text(
                f"🔇 {user.mention} ᴍᴜᴛᴇᴅ ꜰᴏʀ <code>{label}</code>.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # Tban
    # ==========================================================

    @app.on_message(filters.group & filters.command("tban"))
    async def tban_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=2)

        if message.reply_to_message:
            user  = message.reply_to_message.from_user
            targ  = parts[1] if len(parts) > 1 else None
        else:
            user  = await extract_target_user(client, message)
            targ  = parts[2] if len(parts) > 2 else None

        if not user or not targ:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/tban @ᴜꜱᴇʀ 10ᴍ</code> ᴏʀ ʀᴇᴘʟʏ ᴡɪᴛʜ <code>/tban 2ʜ</code>\n"
                "ꜱᴜᴘᴘᴏʀᴛᴇᴅ: <code>30ꜱ</code> <code>10ᴍ</code> <code>2ʜ</code> <code>1ᴅ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        seconds, label = _parse_time(targ)
        if not seconds:
            return await message.reply_text(
                "⚠️ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ!\nᴜꜱᴇ: <code>30ꜱ</code> <code>10ᴍ</code> <code>2ʜ</code> <code>1ᴅ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        target = await client.get_chat_member(message.chat.id, user.id)
        if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ.")

        from datetime import datetime, timedelta
        until = datetime.utcnow() + timedelta(seconds=seconds)
        try:
            await client.ban_chat_member(message.chat.id, user.id, until_date=until)
            await message.reply_text(
                f"🚨 {user.mention} ʙᴀɴɴᴇᴅ ꜰᴏʀ <code>{label}</code>.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # /dmute — mute user + delete their replied message
    # ==========================================================

    @app.on_message(filters.group & filters.command("dmute"))
    async def dmute_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ'ꜱ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴜꜱᴇ /dmute.")
        user = message.reply_to_message.from_user
        if not user:
            return await message.reply_text("⚠️ ᴄᴏᴜʟᴅ ɴᴏᴛ ɪᴅᴇɴᴛɪꜰʏ ᴜꜱᴇʀ.")
        target = await client.get_chat_member(message.chat.id, user.id)
        if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ.")
        try:
            await message.reply_to_message.delete()
            await client.restrict_chat_member(
                message.chat.id, user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.reply_text(
                f"🔇 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ᴀɴᴅ ᴛʜᴇɪʀ ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # /dban — ban user + delete their replied message
    # ==========================================================

    @app.on_message(filters.group & filters.command("dban"))
    async def dban_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ'ꜱ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴜꜱᴇ /dban.")
        user = message.reply_to_message.from_user
        if not user:
            return await message.reply_text("⚠️ ᴄᴏᴜʟᴅ ɴᴏᴛ ɪᴅᴇɴᴛɪꜰʏ ᴜꜱᴇʀ.")
        target = await client.get_chat_member(message.chat.id, user.id)
        if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ.")
        try:
            await message.reply_to_message.delete()
            await client.ban_chat_member(message.chat.id, user.id)
            await message.reply_text(
                f"🚫 {user.mention} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ᴀɴᴅ ᴛʜᴇɪʀ ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ==========================================================
    # /dwarn — warn user + delete their replied message
    # ==========================================================

    @app.on_message(filters.group & filters.command("dwarn"))
    async def dwarn_user(client, message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ'ꜱ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴜꜱᴇ /dwarn.")
        user = message.reply_to_message.from_user
        if not user:
            return await message.reply_text("⚠️ ᴄᴏᴜʟᴅ ɴᴏᴛ ɪᴅᴇɴᴛɪꜰʏ ᴜꜱᴇʀ.")
        target = await client.get_chat_member(message.chat.id, user.id)
        if target.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴡᴀʀɴ ᴀɴ ᴀᴅᴍɪɴ.")
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass
        parts  = message.text.split(maxsplit=1)
        reason = parts[1].strip() if len(parts) > 1 else None

        warn_limit  = await db.get_warn_limit(message.chat.id)
        warn_action = await db.get_warn_action(message.chat.id)
        warns       = await db.add_warn(message.chat.id, user.id, reason=reason)

        if warns >= warn_limit:
            await db.reset_warns(message.chat.id, user.id)
            action_done = ""
            try:
                if warn_action == "ban":
                    await client.ban_chat_member(message.chat.id, user.id)
                    action_done = "banned"
                elif warn_action == "kick":
                    await client.ban_chat_member(message.chat.id, user.id)
                    await client.unban_chat_member(message.chat.id, user.id)
                    action_done = "kicked"
                else:
                    await client.restrict_chat_member(
                        message.chat.id, user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    action_done = "muted"
            except Exception:
                action_done = "actioned"
            await message.reply_text(
                f"🗑 ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.\n"
                f"🚫 {user.mention} ʀᴇᴀᴄʜᴇᴅ {warn_limit}/{warn_limit} ᴡᴀʀɴꜱ "
                f"ᴀɴᴅ ᴡᴀꜱ {action_done}!"
                + (f"\n📝 ʀᴇᴀꜱᴏɴ: <i>{reason}</i>" if reason else ""),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"🗑 ᴍᴇꜱꜱᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ.\n"
                f"⚠️ {user.mention} ᴡᴀʀɴᴇᴅ! {warns}/{warn_limit}"
                + (f"\n📝 ʀᴇᴀꜱᴏɴ: <i>{reason}</i>" if reason else ""),
                parse_mode=enums.ParseMode.HTML
            )
