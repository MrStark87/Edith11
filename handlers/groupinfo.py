# ============================================================
# Group Manager Bot — Group Identity Commands
# (/setname, /setbio, /groupinfo, /setdp)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
import logging
import os
import time

logger = logging.getLogger(__name__)

# ============================================================
# Help Text
# ============================================================
GROUPS_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   👥 𝗴𝗿𝗼𝘂𝗽 𝗶𝗱𝗲𝗻𝘁𝗶𝘁𝘆\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /setname {𝘁𝗲𝘅𝘁} — 𝘀𝗲𝘁/𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗻𝗮𝗺𝗲\n"
    "➻ /setbio {𝘁𝗲𝘅𝘁} — 𝘀𝗲𝘁/𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗱𝗲𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻\n"
    "➻ /groupinfo — 𝘀𝗵𝗼𝘄 𝗴𝗿𝗼𝘂𝗽 𝗶𝗱, 𝗼𝘄𝗻𝗲𝗿, 𝗺𝗲𝗺𝗯𝗲𝗿 𝘀𝘁𝗮𝘁𝘀\n"
    "➻ /setdp — 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮𝗻 𝗶𝗺𝗮𝗴𝗲 𝘁𝗼 𝘀𝗲𝘁 𝗶𝘁 𝗮𝘀 𝗴𝗿𝗼𝘂𝗽 𝗱𝗽\n"
    "   (𝗮𝗹𝗶𝗮𝘀𝗲𝘀: /setpfp, /setimage)\n"
    "➻ /link — 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮 𝗻𝗲𝘄 𝗶𝗻𝘃𝗶𝘁𝗲 𝗹𝗶𝗻𝗸\n"
    "   (𝗮𝗹𝗶𝗮𝘀𝗲𝘀: /givelink, /invitelink)\n\n"
    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆\n"
    "➻ 𝗯𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝘁𝗵 '𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝗳𝗼' / '𝗶𝗻𝘃𝗶𝘁𝗲 𝘂𝘀𝗲𝗿𝘀' 𝗿𝗶𝗴𝗵𝘁\n"
    "➻ 𝗴𝗿𝗼𝘂𝗽 𝗼𝗻𝗹𝘆, 𝘄𝗼𝗻'𝘁 𝘄𝗼𝗿𝗸 𝗶𝗻 𝗽𝗺"
)


# ============================================================
# Help Text — Invite Link
# ============================================================
LINK_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   🔗 𝗶𝗻𝘃𝗶𝘁𝗲 𝗹𝗶𝗻𝗸\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /link — 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮 𝗯𝗿𝗮𝗻𝗱 𝗻𝗲𝘄 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝘃𝗶𝘁𝗲 𝗹𝗶𝗻𝗸\n"
    "   (𝗮𝗹𝗶𝗮𝘀𝗲𝘀: /givelink, /invitelink)\n\n"
    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆\n"
    "➻ 𝗯𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝘁𝗵 '𝗶𝗻𝘃𝗶𝘁𝗲 𝘂𝘀𝗲𝗿𝘀 𝘃𝗶𝗮 𝗹𝗶𝗻𝗸' 𝗿𝗶𝗴𝗵𝘁\n"
    "➻ 𝗲𝗮𝗰𝗵 𝗿𝘂𝗻 𝗰𝗿𝗲𝗮𝘁𝗲𝘀 𝗮 𝗳𝗿𝗲𝘀𝗵 𝗹𝗶𝗻𝗸 (𝗱𝗼𝗲𝘀𝗻'𝘁 𝗿𝗲𝘃𝗼𝗸𝗲 𝘁𝗵𝗲 𝗺𝗮𝗶𝗻 𝗼𝗻𝗲)\n"
    "➻ 𝗴𝗿𝗼𝘂𝗽 𝗼𝗻𝗹𝘆, 𝘄𝗼𝗻'𝘁 𝘄𝗼𝗿𝗸 𝗶𝗻 𝗽𝗺"
)


# ============================================================
# Helpers
# ============================================================

async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def bot_can_change_info(client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat_id, me.id)
        if member.status == ChatMemberStatus.OWNER:
            return True
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            privileges = member.privileges
            return bool(privileges and privileges.can_change_info)
        return False
    except Exception as e:
        logger.error(f"ʙᴏᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ: {e}")
        return False


async def bot_can_invite(client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat_id, me.id)
        if member.status == ChatMemberStatus.OWNER:
            return True
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            privileges = member.privileges
            return bool(privileges and privileges.can_invite_users)
        return False
    except Exception as e:
        logger.error(f"ʙᴏᴛ ɪɴᴠɪᴛᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ: {e}")
        return False


def register_groupinfo_handler(app: Client):

    # ----------------------------------------------------------
    # /setname {text}
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("setname"))
    async def setname_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply_text(
                "❗ ᴜꜱᴀɢᴇ: <code>/setname ʏᴏᴜʀ ɢʀᴏᴜᴘ ɴᴀᴍᴇ</code>",
                parse_mode=enums.ParseMode.HTML
            )

        new_name = parts[1].strip()
        if len(new_name) > 128:
            return await message.reply_text("⚠️ ɢʀᴏᴜᴘ ɴᴀᴍᴇ ᴛᴏᴏ ʟᴏɴɢ (ᴍᴀx 128 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ).")

        if not await bot_can_change_info(client, message.chat.id):
            return await message.reply_text(
                "⚠️ ɪ ɴᴇᴇᴅ '𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝗳𝗼' ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴛᴏ ᴅᴏ ᴛʜɪꜱ."
            )

        try:
            await client.set_chat_title(message.chat.id, new_name)
            await message.reply_text(
                f"✅ 𝗚𝗿𝗼𝘂𝗽 𝗻𝗮𝗺𝗲 𝘂𝗽𝗱𝗮𝘁𝗲𝗱 𝘁𝗼:\n<b>{new_name}</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            if "CHAT_TITLE_NOT_MODIFIED" in str(e):
                await message.reply_text("⚠️ ᴛʜᴀᴛ'ꜱ ᴀʟʀᴇᴀᴅʏ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ɴᴀᴍᴇ — ɴᴏᴛʜɪɴɢ ᴛᴏ ᴄʜᴀɴɢᴇ.")
            else:
                await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇᴛ ɴᴀᴍᴇ: {e}")

    # ----------------------------------------------------------
    # /setbio {text}
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("setbio"))
    async def setbio_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        new_bio = parts[1].strip() if len(parts) > 1 else ""
        if len(new_bio) > 255:
            return await message.reply_text("⚠️ ɢʀᴏᴜᴘ ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ ᴛᴏᴏ ʟᴏɴɢ (ᴍᴀx 255 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ).")

        if not await bot_can_change_info(client, message.chat.id):
            return await message.reply_text(
                "⚠️ ɪ ɴᴇᴇᴅ '𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝗳𝗼' ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴛᴏ ᴅᴏ ᴛʜɪꜱ."
            )

        try:
            await client.set_chat_description(message.chat.id, new_bio)
            if new_bio:
                await message.reply_text(
                    f"✅ 𝗚𝗿𝗼𝘂𝗽 𝗯𝗶𝗼 𝘂𝗽𝗱𝗮𝘁𝗲𝗱 𝘁𝗼:\n<i>{new_bio}</i>",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply_text("✅ 𝗚𝗿𝗼𝘂𝗽 𝗯𝗶𝗼 𝗰𝗹𝗲𝗮𝗿𝗲𝗱.")
        except Exception as e:
            if "CHAT_ABOUT_NOT_MODIFIED" in str(e):
                await message.reply_text("⚠️ ᴛʜᴀᴛ'ꜱ ᴀʟʀᴇᴀᴅʏ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ʙɪᴏ — ɴᴏᴛʜɪɴɢ ᴛᴏ ᴄʜᴀɴɢᴇ.")
            else:
                await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇᴛ ʙɪᴏ: {e}")

    # ----------------------------------------------------------
    # /setdp | /setpfp | /setimage  (reply to a photo)
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command(["setdp", "setpfp", "setimage"]))
    async def setdp_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        target_msg = message.reply_to_message
        photo = None
        if target_msg:
            photo = target_msg.photo or (
                target_msg.document
                if target_msg.document and (target_msg.document.mime_type or "").startswith("image/")
                else None
            )
        if not photo and message.photo:
            target_msg = message
            photo = message.photo

        if not photo:
            return await message.reply_text(
                "⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴡɪᴛʜ <code>/setdp</code> (ᴏʀ ꜱᴇɴᴅ ᴛʜᴇ ɪᴍᴀɢᴇ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀꜱ ᴄᴀᴘᴛɪᴏɴ).",
                parse_mode=enums.ParseMode.HTML
            )

        if not await bot_can_change_info(client, message.chat.id):
            return await message.reply_text(
                "⚠️ ɪ ɴᴇᴇᴅ '𝗰𝗵𝗮𝗻𝗴𝗲 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝗳𝗼' ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴛᴏ ᴅᴏ ᴛʜɪꜱ."
            )

        status_msg = await message.reply_text("⏳ ᴜᴘᴅᴀᴛɪɴɢ ɢʀᴏᴜᴘ ᴅᴘ…")
        local_path = None
        try:
            local_path = await client.download_media(target_msg)
            await client.set_chat_photo(message.chat.id, photo=local_path)
            await status_msg.edit_text("✅ 𝗚𝗿𝗼𝘂𝗽 𝗗𝗣 𝘂𝗽𝗱𝗮𝘁𝗲𝗱!")
        except Exception as e:
            await status_msg.edit_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇᴛ ᴅᴘ: {e}")
        finally:
            if local_path:
                try:
                    os.remove(local_path)
                except Exception:
                    pass

    # ----------------------------------------------------------
    # /groupinfo
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("groupinfo"))
    async def groupinfo_cmd(client, message: Message):
        chat_id = message.chat.id
        status_msg = await message.reply_text("⏳ ɢᴀᴛʜᴇʀɪɴɢ ɢʀᴏᴜᴘ ᴅᴀᴛᴀ…")

        try:
            chat = await client.get_chat(chat_id)
            total = await client.get_chat_members_count(chat_id)

            owner_line = "ᴜɴᴋɴᴏᴡɴ"
            admin_count = 0
            async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
                admin_count += 1
                if member.status == ChatMemberStatus.OWNER and member.user:
                    owner_line = f"{member.user.first_name} (<code>{member.user.id}</code>)"

            bots = 0
            deleted = 0
            scanned = 0
            async for member in client.get_chat_members(chat_id):
                scanned += 1
                if member.user.is_bot:
                    bots += 1
                elif member.user.is_deleted:
                    deleted += 1

            active = max(0, scanned - bots - deleted)

            text = (
                "╔══════════════════╗\n"
                "   📊 𝗴𝗿𝗼𝘂𝗽 𝗶𝗻𝗳𝗼\n"
                "╚══════════════════╝\n\n"
                f"➻ 𝗻𝗮𝗺𝗲: <b>{chat.title}</b>\n"
                f"➻ 𝗶𝗱: <code>{chat_id}</code>\n"
                f"➻ 𝗼𝘄𝗻𝗲𝗿: {owner_line}\n\n"
                f"➻ 𝘁𝗼𝘁𝗮𝗹 𝗺𝗲𝗺𝗯𝗲𝗿𝘀: <b>{total}</b>\n"
                f"➻ 𝗮𝗱𝗺𝗶𝗻𝘀: <b>{admin_count}</b>\n"
                f"➻ 𝗯𝗼𝘁𝘀: <b>{bots}</b>\n"
                f"➻ 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀: <b>{deleted}</b>\n"
                f"➻ 𝗮𝗰𝘁𝗶𝘃𝗲 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀: <b>{active}</b>"
            )
            await status_msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            logger.error(f"ɢʀᴏᴜᴘɪɴꜰᴏ ᴇʀʀᴏʀ ɪɴ {chat_id}: {e}")
            await status_msg.edit_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ɢʀᴏᴜᴘ ɪɴꜰᴏ: {e}")

    # ----------------------------------------------------------
    # /link | /givelink | /invitelink
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command(["link", "givelink", "invitelink"]))
    async def link_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        if not await bot_can_invite(client, message.chat.id):
            return await message.reply_text(
                "⚠️ ɪ ɴᴇᴇᴅ '𝗶𝗻𝘃𝗶𝘁𝗲 𝘂𝘀𝗲𝗿𝘀 𝘃𝗶𝗮 𝗹𝗶𝗻𝗸' ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴛᴏ ᴅᴏ ᴛʜɪꜱ."
            )

        status_msg = await message.reply_text("⏳ ɢᴇɴᴇʀᴀᴛɪɴɢ ɪɴᴠɪᴛᴇ ʟɪɴᴋ…")
        try:
            invite = await client.create_chat_invite_link(message.chat.id)
            await status_msg.edit_text(
                f"🔗 <b>𝗡𝗲𝘄 𝗜𝗻𝘃𝗶𝘁𝗲 𝗟𝗶𝗻𝗸</b>\n\n{invite.invite_link}",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            await status_msg.edit_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ: {e}")
