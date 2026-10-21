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
    f"<blockquote>👥 <b>𝖦𝗋𝗈𝗎𝗉 𝖨𝖽𝖾𝗇𝗍𝗂𝗍𝗒</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/setname { '{text}' }</code> — 𝖲𝖾𝗍/𝖢𝗁𝖺𝗇𝗀𝖾 𝖦𝗋𝗈𝗎𝗉 𝖭𝖺𝗆𝖾\n"
    f"➻ <code>/setbio { '{text}' }</code> — 𝖲𝖾𝗍/𝖢𝗁𝖺𝗇𝗀𝖾 𝖦𝗋𝗈𝗎𝗉 𝖣𝖾𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇\n"
    f"➻ <code>/groupinfo</code> — 𝖲𝗁𝗈𝗐 𝖦𝗋𝗈𝗎𝗉 𝖨𝖣, 𝖮𝗐𝗇𝖾𝗋, 𝖬𝖾𝗆𝖻𝖾𝗋 𝖲𝗍𝖺𝗍𝗌\n"
    f"➻ <code>/setdp</code> — 𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺𝗇 𝗂𝗆𝖺𝗀𝖾 𝗍𝗈 𝗌𝖾𝗍 𝖦𝗋𝗈𝗎𝗉 𝖣𝖯\n"
    f"   (𝖠𝗅𝗂𝖺𝗌𝖾𝗌: /setpfp, /setimage)\n"
    f"➻ <code>/link</code> — 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖺 𝖭𝖾𝗐 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄\n"
    f"   (𝖠𝗅𝗂𝖺𝗌𝖾𝗌: /givelink, /invitelink)\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖠𝖽𝗆𝗂𝗇 𝖮𝗇𝗅𝗒\n"
    f"➻ 𝖡𝗈𝗍 𝖬𝗎𝗌𝗍 𝖡𝖾 𝖠𝖽𝗆𝗂𝗇 𝖶𝗂𝗍𝗁 '𝖢𝗁𝖺𝗇𝗀𝖾 𝖦𝗋𝗈𝗎𝗉 𝖨𝗇𝖿𝗈' / '𝖨𝗇𝗏𝗂𝗍𝖾 𝖴𝗌𝖾𝗋𝗌' 𝖱𝗂𝗀𝗁𝗍\n"
    f"➻ 𝖦𝗋𝗈𝗎𝗉 𝖮𝗇𝗅𝗒, 𝖶𝗈𝗇'𝗍 𝖶𝗈𝗋𝗄 𝖨𝗇 𝖯𝖬"
)


# ============================================================
# Help Text — Invite Link
# ============================================================
LINK_HELP_TEXT = (
    f"<blockquote>🔗 <b>𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/link</code> — 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖠 𝖡𝗋𝖺𝗇𝖽 𝖭𝖾𝗐 𝖦𝗋𝗈𝗎𝗉 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄\n"
    f"   (𝖠𝗅𝗂𝖺𝗌𝖾𝗌: /givelink, /invitelink)\n\n"
    f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖠𝖽𝗆𝗂𝗇 𝖮𝗇𝗅𝗒\n"
    f"➻ 𝖡𝗈𝗍 𝖬𝗎𝗌𝗍 𝖡𝖾 𝖠𝖽𝗆𝗂𝗇 𝖶𝗂𝗍𝗁 '𝖨𝗇𝗏𝗂𝗍𝖾 𝖴𝗌𝖾𝗋𝗌 𝖵𝗂𝖺 𝖫𝗂𝗇𝗄' 𝖱𝗂𝗀𝗁𝗍\n"
    f"➻ 𝖤𝖺𝖼𝗁 𝖱𝗎𝗇 𝖢𝗋𝖾𝖺𝗍𝖾𝗌 𝖠 𝖥𝗋𝖾𝗌𝗁 𝖫𝗂𝗇𝗄 (𝖣𝗈𝖾𝗌𝗇'𝗍 𝖱𝖾𝗏𝗈𝗄𝖾 𝖳𝗁𝖾 𝖬𝖺𝗂𝗇 𝖮𝗇𝖾)\n"
    f"➻ 𝖦𝗋𝗈𝗎𝗉 𝖮𝗇𝗅𝗒, 𝖶𝗈𝗇'𝗍 𝖶𝗈𝗋𝗄 𝖨𝗇 𝖯𝖬"
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
                "<blockquote>📊 <b>𝖦𝗋𝗈𝗎𝗉 𝖨𝗇𝖿𝗈</b></blockquote>\n\n"
                f"➻ 𝖭𝖺𝗆𝖾: <b>{chat.title}</b>\n"
                f"➻ 𝖨𝖣: <code>{chat_id}</code>\n"
                f"➻ 𝖮𝗐𝗇𝖾𝗋: {owner_line}\n\n"
                f"➻ 𝖳𝗈𝗍𝖺𝗅 𝖬𝖾𝗆𝖻𝖾𝗋𝗌: <b>{total}</b>\n"
                f"➻ 𝖠𝖽𝗆𝗂𝗇𝗌: <b>{admin_count}</b>\n"
                f"➻ 𝖡𝗈𝗍𝗌: <b>{bots}</b>\n"
                f"➻ 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌: <b>{deleted}</b>\n"
                f"➻ 𝖠𝖼𝗍𝗂𝗏𝖾 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌: <b>{active}</b>"
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
                "⚠️ 𝖨 𝖭𝖾𝖾𝖽 '𝖨𝗇𝗏𝗂𝗍𝖾 𝖴𝗌𝖾𝗋𝗌 𝖵𝗂𝖺 𝖫𝗂𝗇𝗄' 𝖠𝖽𝗆𝗂𝗇 𝖱𝗂𝗀𝗁𝗍 𝖳𝗈 𝖣𝗈 𝖳𝗁𝗂𝗌"
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
