# ============================================================
# Group Manager Bot — Promote & Demote (Upgraded)
# Author: Mr. Stark
# Roles: Co-Founder / Admin / Moderator / FullPromote
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import (
    ChatAdminRequired, UserNotParticipant,
    AdminRankEmojiNotAllowed, ChatNotModified
)
from pyrogram.enums import ChatMemberStatus
from config import OWNER_ID
import db
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Help Text
# ============================================================
PROMOTE_HELP_TEXT = (
    "╔══════════════════╗\n"
    "  👮 𝗽𝗿𝗼𝗺𝗼𝘁𝗲 𝘀𝘆𝘀𝘁𝗲𝗺\n"
    "╚══════════════════╝\n\n"

    "<u>⚜ /cofounder — ᴄᴏ-ꜰᴏᴜɴᴅᴇʀ</u>\n"
    "➥ ᴄᴀɴ ꜱᴇᴛ ᴄᴏꜰᴏᴜɴᴅᴇʀꜱ, ᴍᴏᴅꜱ, ʜᴇʟᴘᴇʀꜱ\n"
    "➥ ᴄᴀɴ ʙᴀɴ ᴜꜱᴇʀꜱ\n"
    "➥ ᴀʟʟ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ\n"
    "➥ ᴀᴘᴘᴇᴀʀꜱ ɪɴ /staff ʟɪꜱᴛ\n\n"

    "<u>👮 /admin 𝗼𝗿 /promote {𝗻𝗮𝗺𝗲} — ᴀᴅᴍɪɴ</u>\n"
    "➥ ᴅᴇʟᴇᴛᴇ ᴍꜱɢꜱ, ᴘɪɴ, ɪɴᴠɪᴛᴇ\n"
    "➥ ᴍᴀɴᴀɢᴇ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ\n"
    "➥ ᴄᴜꜱᴛᴏᴍ ᴛɪᴛʟᴇ ᴠɪᴀ ᴄᴏᴍᴍᴀɴᴅ ᴛᴇxᴛ\n"
    "➥ ᴀᴘᴘᴇᴀʀꜱ ɪɴ /staff ʟɪꜱᴛ\n\n"

    "<u>👷 /mod — ᴍᴏᴅᴇʀᴀᴛᴏʀ</u>\n"
    "➥ ʙᴀɴ, ᴋɪᴄᴋ, ᴍᴜᴛᴇ, ɪɴꜰᴏ ᴄᴏᴍᴍᴀɴᴅꜱ\n"
    "➥ ɴᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇ ᴘᴏᴡᴇʀ\n"
    "➥ ᴀᴘᴘᴇᴀʀꜱ ɪɴ /staff ʟɪꜱᴛ\n\n"

    "<u>⚡ /fullpromote {𝗻𝗮𝗺𝗲} — ꜰᴜʟʟ ᴀᴅᴍɪɴ</u>\n"
    "➥ ᴀʟʟ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴇɴᴀʙʟᴇᴅ\n"
    "➥ ᴄᴜꜱᴛᴏᴍ ᴛɪᴛʟᴇ ꜱᴜᴘᴘᴏʀᴛᴇᴅ\n\n"

    "🔻 /demote — ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ\n"
    "📋 /staff — ᴠɪᴇᴡ ᴀʟʟ ꜱᴛᴀꜰꜰ ᴍᴇᴍʙᴇʀꜱ"
)

# ============================================================
# Role definitions
# ============================================================
ROLE_COFOUNDER  = "cofounder"
ROLE_ADMIN      = "admin"
ROLE_MOD        = "moderator"

# ============================================================
# Helpers
# ============================================================

def _mention(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def _extract(client, message: Message):
    """ʀᴇᴛᴜʀɴ (ᴜꜱᴇʀ_ɪᴅ, ꜰɪʀꜱᴛ_ɴᴀᴍᴇ, ᴛɪᴛʟᴇ) ꜰʀᴏᴍ ʀᴇᴘʟʏ ᴏʀ ᴀʀɢꜱ."""
    # Get full text after command
    parts = message.text.split(maxsplit=1)
    text  = parts[1].strip() if len(parts) > 1 else ""

    # Reply mode: user from reply, rest of text is title
    if message.reply_to_message and message.reply_to_message.from_user:
        user  = message.reply_to_message.from_user
        title = text if text else None
        return user.id, user.first_name, title

    # Arg mode: /cmd @user Title Text Here
    if not text:
        await message.reply_text(
            "⚙️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ:\n"
            "<code>/promote @ᴜꜱᴇʀɴᴀᴍᴇ ᴄᴜꜱᴛᴏᴍ ᴛɪᴛʟᴇ</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return None, None, None

    args     = text.split(maxsplit=1)
    user_arg = args[0]
    title    = args[1].strip() if len(args) > 1 else None

    # user_arg could be @username or numeric ID
    try:
        if user_arg.lstrip("-").isdigit():
            user = await client.get_users(int(user_arg))
        else:
            user = await client.get_users(user_arg)
        return user.id, user.first_name, title
    except Exception as e:
        await message.reply_text(
            f"❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ: <code>{user_arg}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return None, None, None


async def _can_promote(client, message: Message) -> bool:
    if not message.from_user:
        await message.reply_text("❌ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴꜱ ᴄᴀɴɴᴏᴛ ᴜꜱᴇ ᴛʜɪꜱ.")
        return False
    # Bot owner always has permission
    if message.from_user.id == OWNER_ID:
        return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status == ChatMemberStatus.OWNER:
        return True
    if member.status == ChatMemberStatus.ADMINISTRATOR:
        privileges = getattr(member, "privileges", None)
        can_promote = bool(privileges and getattr(privileges, "can_promote_members", False))
        if can_promote:
            return True
        await message.reply_text(
            "❌ ʏᴏᴜ ɴᴇᴇᴅ ᴛʜᴇ <b>'Add New Admins'</b> ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ — "
            "ᴊᴜꜱᴛ ʙᴇɪɴɢ ᴀɴ ᴀᴅᴍɪɴ ɪꜱɴ'ᴛ ᴇɴᴏᴜɢʜ.\n\n"
            "ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ → ᴀᴅᴍɪɴꜱ → ᴇᴅɪᴛ ᴛʜɪꜱ ᴀᴅᴍɪɴ → ᴇɴᴀʙʟᴇ "
            "<b>'Add New Admins'</b> ᴛᴏɢɢʟᴇ ꜱᴘᴇᴄɪꜰɪᴄᴀʟʟʏ.",
            parse_mode=enums.ParseMode.HTML
        )
        return False
    await message.reply_text("❌ ʏᴏᴜ ɴᴇᴇᴅ 𝗔𝗱𝗺𝗶𝗻 ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ.",
                             parse_mode=enums.ParseMode.HTML)
    return False


async def _safe_set_title(client, chat_id: int, user_id: int, title: str):
    """
    ꜱᴇᴛ ᴀᴅᴍɪɴ ᴛɪᴛʟᴇ ꜱᴀꜰᴇʟʏ.
    ᴛᴇʟᴇɢʀᴀᴍ ʀᴇǫᴜɪʀᴇꜱ ʙᴏᴛ ᴛᴏ ʜᴀᴠᴇ ᴄᴀɴ_ᴘʀᴏᴍᴏᴛᴇ_ᴍᴇᴍʙᴇʀꜱ=ᴛʀᴜᴇ ᴛᴏ ꜱᴇᴛ ᴛɪᴛʟᴇꜱ.
    ɪꜰ ɪᴛ ꜰᴀɪʟꜱ, ᴡᴇ ᴊᴜꜱᴛ ꜱᴋɪᴘ ꜱɪʟᴇɴᴛʟʏ — ᴛɪᴛʟᴇ ɪꜱ ᴄᴏꜱᴍᴇᴛɪᴄ ᴏɴʟʏ.
    """
    if not title:
        return
    try:
        await client.set_administrator_title(chat_id, user_id, title)
    except AdminRankEmojiNotAllowed:
        # Title has emoji — remove emoji and retry
        import re
        clean = re.sub(r'[^\w\s]', '', title).strip()
        try:
            await client.set_administrator_title(chat_id, user_id, clean or "Admin")
        except Exception:
            pass
    except ChatNotModified:
        pass  # Already has this title
    except Exception as e:
        logger.warning(f"ᴄᴏᴜʟᴅ ɴᴏᴛ ꜱᴇᴛ ᴛɪᴛʟᴇ '{title}' ꜰᴏʀ {user_id}: {e}")


def _promote_msg(chat_title, user_id, user_name, admin_id, admin_name, role_label, title=None):
    lines = [
        f"» 𝗣𝗿𝗼𝗺𝗼𝘁𝗶𝗻𝗴 ᴀ ᴜꜱᴇʀ ɪɴ {chat_title}",
        f"👤 𝗨𝘀𝗲𝗿 : {_mention(user_id, user_name)}",
        f"👮 𝗕𝘆 : {_mention(admin_id, admin_name)}",
        f"🏷 𝗥𝗼𝗹𝗲 : {role_label}",
    ]
    if title:
        lines.append(f"📛 𝗧𝗶𝘁𝗹𝗲 : {title}")
    return "\n".join(lines)


def _demote_msg(chat_title, user_id, user_name, admin_id, admin_name):
    return (
        f"» 𝗗𝗲𝗺𝗼𝘁𝗶𝗻𝗴 ᴀ ᴜꜱᴇʀ ɪɴ {chat_title}\n"
        f"👤 𝗨𝘀𝗲𝗿 : {_mention(user_id, user_name)}\n"
        f"👮 𝗕𝘆 : {_mention(admin_id, admin_name)}"
    )


# ============================================================
# Register
# ============================================================

def register_promote_handler(app: Client):

    # ----------------------------------------------------------
    # /cofounder — Co-Founder role
    # Can only be used by group owner
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("cofounder"))
    async def cofounder_cmd(client, message: Message):
        # Only owner can set co-founders
        caller = await client.get_chat_member(message.chat.id, message.from_user.id)
        if caller.status != ChatMemberStatus.OWNER:
            return await message.reply_text("❌ ᴏɴʟʏ ᴛʜᴇ ɢʀᴏᴜᴘ 𝗢𝘄𝗻𝗲𝗿 ᴄᴀɴ ꜱᴇᴛ ᴀ ᴄᴏ-ꜰᴏᴜɴᴅᴇʀ.",
                                            parse_mode=enums.ParseMode.HTML)

        user_id, first_name, _ = await _extract(client, message)
        if not user_id:
            return

        try:
            await client.promote_chat_member(
                message.chat.id, user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_video_chats=True,
                    is_anonymous=False,
                )
            )
            await _safe_set_title(client, message.chat.id, user_id, "Co-Founder")

            # Save role in DB
            await db.set_staff_role(message.chat.id, user_id, ROLE_COFOUNDER)

            await message.reply_text(
                _promote_msg(
                    message.chat.title, user_id, first_name,
                    message.from_user.id, message.from_user.first_name,
                    "⚜ ᴄᴏ-ꜰᴏᴜɴᴅᴇʀ"
                ) + "\n\n✅ 𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱 𝗮𝘀 𝗖𝗼-𝗙𝗼𝘂𝗻𝗱𝗲𝗿!",
                parse_mode=enums.ParseMode.HTML
            )
        except ChatAdminRequired:
            await message.reply_text("❌ ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴡɪᴛʜ 𝗔𝗱𝗱 𝗔𝗱𝗺𝗶𝗻𝘀 ᴘᴇʀᴍɪꜱꜱɪᴏɴ.",
                                     parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ----------------------------------------------------------
    # /admin or /promote — Standard Admin with optional custom title
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command(["admin", "promote"]))
    async def admin_cmd(client, message: Message):
        if not await _can_promote(client, message):
            return

        user_id, first_name, title = await _extract(client, message)
        if not user_id:
            return

        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status == ChatMemberStatus.OWNER:
                return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴄʜᴀɴɢᴇ ᴏᴡɴᴇʀ'ꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.")

            await client.promote_chat_member(
                message.chat.id, user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=False,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    is_anonymous=False,
                )
            )

            # Custom title — whatever admin typed after command
            admin_title = title or "Admin"
            await _safe_set_title(client, message.chat.id, user_id, admin_title)

            await db.set_staff_role(message.chat.id, user_id, ROLE_ADMIN)

            await message.reply_text(
                _promote_msg(
                    message.chat.title, user_id, first_name,
                    message.from_user.id, message.from_user.first_name,
                    "👮 ᴀᴅᴍɪɴ", title=admin_title
                ) + "\n\n✅ 𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱 𝗮𝘀 𝗔𝗱𝗺𝗶𝗻!",
                parse_mode=enums.ParseMode.HTML
            )
        except ChatAdminRequired:
            await message.reply_text("❌ ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴡɪᴛʜ 𝗔𝗱𝗱 𝗔𝗱𝗺𝗶𝗻𝘀 ᴘᴇʀᴍɪꜱꜱɪᴏɴ.",
                                     parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ----------------------------------------------------------
    # /mod — Moderator
    # Can ban/kick/mute, cannot delete messages
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("mod"))
    async def mod_cmd(client, message: Message):
        if not await _can_promote(client, message):
            return

        user_id, first_name, _ = await _extract(client, message)
        if not user_id:
            return

        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status == ChatMemberStatus.OWNER:
                return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴄʜᴀɴɢᴇ ᴏᴡɴᴇʀ'ꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.")

            await client.promote_chat_member(
                message.chat.id, user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False,
                    is_anonymous=False,
                )
            )
            await _safe_set_title(client, message.chat.id, user_id, "Moderator")

            await db.set_staff_role(message.chat.id, user_id, ROLE_MOD)

            await message.reply_text(
                _promote_msg(
                    message.chat.title, user_id, first_name,
                    message.from_user.id, message.from_user.first_name,
                    "👷 ᴍᴏᴅᴇʀᴀᴛᴏʀ"
                ) + "\n\n✅ 𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱 𝗮𝘀 𝗠𝗼𝗱𝗲𝗿𝗮𝘁𝗼𝗿!",
                parse_mode=enums.ParseMode.HTML
            )
        except ChatAdminRequired:
            await message.reply_text("❌ ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴡɪᴛʜ 𝗔𝗱𝗱 𝗔𝗱𝗺𝗶𝗻𝘀 ᴘᴇʀᴍɪꜱꜱɪᴏɴ.",
                                     parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ----------------------------------------------------------
    # /fullpromote — All permissions + custom title
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("fullpromote"))
    async def fullpromote_cmd(client, message: Message):
        if not await _can_promote(client, message):
            return

        user_id, first_name, title = await _extract(client, message)
        if not user_id:
            return

        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status == ChatMemberStatus.OWNER:
                return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴄʜᴀɴɢᴇ ᴏᴡɴᴇʀ'ꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.")

            await client.promote_chat_member(
                message.chat.id, user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_video_chats=True,
                    is_anonymous=False,
                )
            )

            admin_title = title or "ꜰᴜʟʟ ᴀᴅᴍɪɴ"
            await _safe_set_title(client, message.chat.id, user_id, admin_title)

            await db.set_staff_role(message.chat.id, user_id, ROLE_ADMIN)

            await message.reply_text(
                _promote_msg(
                    message.chat.title, user_id, first_name,
                    message.from_user.id, message.from_user.first_name,
                    "⚡ ꜰᴜʟʟ ᴀᴅᴍɪɴ", title=admin_title
                ) + "\n\n✅ 𝗙𝘂𝗹𝗹 𝗔𝗱𝗺𝗶𝗻 𝗽𝗿𝗼𝗺𝗼𝘁𝗶𝗼𝗻 𝗱𝗼𝗻𝗲!",
                parse_mode=enums.ParseMode.HTML
            )
        except ChatAdminRequired:
            await message.reply_text("❌ ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴡɪᴛʜ 𝗔𝗱𝗱 𝗔𝗱𝗺𝗶𝗻𝘀 ᴘᴇʀᴍɪꜱꜱɪᴏɴ.",
                                     parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ----------------------------------------------------------
    # /demote — Remove admin rights + clear DB role
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("demote"))
    async def demote_cmd(client, message: Message):
        if not await _can_promote(client, message):
            return

        user_id, first_name, _ = await _extract(client, message)
        if not user_id:
            return

        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status == ChatMemberStatus.OWNER:
                return await message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ᴅᴇᴍᴏᴛᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ.")
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                return await message.reply_text("⚠️ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.")

            await client.promote_chat_member(
                message.chat.id, user_id,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_change_info=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_video_chats=False,
                    is_anonymous=False,
                )
            )

            await db.remove_staff_role(message.chat.id, user_id)

            await message.reply_text(
                _demote_msg(
                    message.chat.title, user_id, first_name,
                    message.from_user.id, message.from_user.first_name,
                ) + "\n\n✅ 𝗗𝗲𝗺𝗼𝘁𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆.",
                parse_mode=enums.ParseMode.HTML
            )
        except ChatAdminRequired:
            await message.reply_text("❌ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴛʜɪꜱ ᴜꜱᴇʀ.",
                                     parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ: {e}")


    # ----------------------------------------------------------
    # /staff — List all staff members with roles
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("staff"))
    async def staff_cmd(client, message: Message):
        chat_id = message.chat.id

        # Fetch live admin list from Telegram
        admins = []
        async for member in client.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            admins.append(member)

        if not admins:
            return await message.reply_text("📭 ɴᴏ ᴀᴅᴍɪɴꜱ ꜰᴏᴜɴᴅ.")

        owner_lines   = []
        cofounder_lines = []
        admin_lines   = []
        mod_lines     = []

        for m in admins:
            if not m.user or m.user.is_bot:
                continue
            uid   = m.user.id
            name  = m.user.first_name or "Unknown"
            tag   = m.custom_title or ""

            # Get role from DB
            role = await db.get_staff_role(chat_id, uid)

            mention_str = f'<a href="tg://user?id={uid}">{name}</a>'
            title_str   = f" — <i>{tag}</i>" if tag else ""

            if m.status == ChatMemberStatus.OWNER:
                owner_lines.append(f"  👑 {mention_str}{title_str}")
            elif role == ROLE_COFOUNDER:
                cofounder_lines.append(f"  ⚜ {mention_str}{title_str}")
            elif role == ROLE_MOD:
                mod_lines.append(f"  👷 {mention_str}{title_str}")
            else:
                admin_lines.append(f"  👮 {mention_str}{title_str}")

        sections = []
        if owner_lines:
            sections.append("🔱 𝗢𝘄𝗻𝗲𝗿\n" + "\n".join(owner_lines))
        if cofounder_lines:
            sections.append("⚜ 𝗖𝗼-𝗙𝗼𝘂𝗻𝗱𝗲𝗿𝘀\n" + "\n".join(cofounder_lines))
        if admin_lines:
            sections.append("👮 𝗔𝗱𝗺𝗶𝗻𝘀\n" + "\n".join(admin_lines))
        if mod_lines:
            sections.append("👷 𝗠𝗼𝗱𝗲𝗿𝗮𝘁𝗼𝗿𝘀\n" + "\n".join(mod_lines))

        text = (
            f"╔══ 𝗦𝘁𝗮𝗳𝗳 𝗟𝗶𝘀𝘁 ══╗\n"
            f"📌 {message.chat.title}\n"
            f"╚══════════════╝\n\n"
            + "\n\n".join(sections)
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
    
