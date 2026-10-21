# ============================================================
# Group Manager Bot — Force Subscribe
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    UserNotParticipant, ChatAdminRequired, ChannelPrivate,
    UsernameNotOccupied, PeerIdInvalid, UserBannedInChannel
)
import db
import logging
import asyncio

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def user_joined_channel(client, user_id: int, channel_id: int) -> bool:
    """
    ʀᴇᴛᴜʀɴꜱ ᴛʀᴜᴇ ɪꜰ ᴜꜱᴇʀ ɪꜱ ᴀ ᴍᴇᴍʙᴇʀ.
    ʀᴇᴛᴜʀɴꜱ ꜰᴀʟꜱᴇ ᴏɴʟʏ ᴏɴ ᴜꜱᴇʀɴᴏᴛᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ᴏʀ ᴜꜱᴇʀʙᴀɴɴᴇᴅɪɴᴄʜᴀɴɴᴇʟ.
    ᴀɴʏ ᴏᴛʜᴇʀ ᴇʀʀᴏʀ → ᴛʀᴜᴇ (ʙᴇɴᴇꜰɪᴛ ᴏꜰ ᴅᴏᴜʙᴛ, ᴅᴏɴ'ᴛ ʙʟᴏᴄᴋ ᴜꜱᴇʀ).
    """
    try:
        member = await client.get_chat_member(channel_id, user_id)
        # Banned or explicitly left = not joined
        if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]:
            return False
        return True
    except UserNotParticipant:
        # Definitive: user is NOT in the channel
        return False
    except UserBannedInChannel:
        return False
    except (ChatAdminRequired, ChannelPrivate):
        # Bot can't check → don't block user
        logger.warning(f"ꜰꜱᴜʙ: ᴄᴀɴ'ᴛ ᴄʜᴇᴄᴋ ᴍᴇᴍʙᴇʀꜱʜɪᴘ ɪɴ {channel_id} — ꜱᴋɪᴘᴘɪɴɢ")
        return True
    except Exception as e:
        # Any other error → don't block user
        logger.error(f"ꜰꜱᴜʙ ᴍᴇᴍʙᴇʀꜱʜɪᴘ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ ({channel_id}): {e}")
        return True


async def get_or_create_invite_link(client, channel_id: int) -> str | None:
    """
    ɢᴇᴛ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴀ ᴄʜᴀɴɴᴇʟ.
    ꜰᴏʀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟꜱ ʀᴇᴛᴜʀɴꜱ ᴛ.ᴍᴇ ʟɪɴᴋ ᴅɪʀᴇᴄᴛʟʏ.
    ꜰᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ ᴄʀᴇᴀᴛᴇꜱ/uses ᴇxɪꜱᴛɪɴɢ ɪɴᴠɪᴛᴇ ʟɪɴᴋ.
    """
    try:
        chat = await client.get_chat(channel_id)
        if chat.username:
            return f"https://t.me/{chat.username}"
        if chat.invite_link:
            return chat.invite_link
        link_obj = await client.create_chat_invite_link(channel_id)
        return link_obj.invite_link
    except ChatAdminRequired:
        logger.error(f"ꜰꜱᴜʙ: ʙᴏᴛ ʜᴀꜱ ɴᴏ ɪɴᴠɪᴛᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ɪɴ {channel_id}")
        return None
    except Exception as e:
        logger.error(f"ꜰꜱᴜʙ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴇʀʀᴏʀ ꜰᴏʀ {channel_id}: {e}")
        return None


def register_fsub_handler(app: Client):

    # ==========================================================
    # /addfsub
    # ==========================================================

    @app.on_message(filters.group & filters.command("addfsub"))
    async def addfsub_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ 𝗨𝘀𝗮𝗴𝗲:\n"
                "• ᴘᴜʙʟɪᴄ: <code>/addfsub @ᴄʜᴀɴɴᴇʟɴᴀᴍᴇ</code>\n"
                "• ᴘʀɪᴠᴀᴛᴇ: <code>/addfsub -100xxxxxxxxxx</code>\n\n"
                "📌 ʙᴏᴛ ᴍᴜꜱᴛ ʙᴇ 𝗮𝗱𝗺𝗶𝗻 ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.",
                parse_mode=enums.ParseMode.HTML
            )

        raw = parts[1].strip()

        # Resolve channel
        try:
            if raw.lstrip("-").isdigit():
                chat = await client.get_chat(int(raw))
            else:
                chat = await client.get_chat(raw)
        except (UsernameNotOccupied, PeerIdInvalid):
            return await message.reply_text(
                f"❌ ᴄʜᴀɴɴᴇʟ ɴᴏᴛ ꜰᴏᴜɴᴅ: <code>{raw}</code>\n\n"
                "ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀ ᴍᴇᴍʙᴇʀ/admin ᴛʜᴇʀᴇ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            return await message.reply_text(
                f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇꜱᴏʟᴠᴇ ᴄʜᴀɴɴᴇʟ: <code>{raw}</code>\n"
                f"ᴇʀʀᴏʀ: <code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        channel_id = str(chat.id)

        # Verify bot is admin in that channel
        try:
            bot_me = await client.get_me()
            bot_member = await client.get_chat_member(chat.id, bot_me.id)
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text(
                    f"❌ ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ {chat.title}!\n\n"
                    "ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴍᴏᴛᴇ ᴛʜᴇ ʙᴏᴛ ᴀꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ, "
                    "ᴛʜᴇɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴀɢᴀɪɴ.",
                    parse_mode=enums.ParseMode.HTML
                )
        except UserNotParticipant:
            return await message.reply_text(
                f"❌ ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏꜰ {chat.title}!\n\n"
                "ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            return await message.reply_text(
                f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴠᴇʀɪꜰʏ ʙᴏᴛ'ꜱ ᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ ɪɴ {chat.title}: <code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )

        # Already in list?
        existing = await db.get_fsub_channels(message.chat.id)
        if channel_id in [str(c) for c in existing]:
            return await message.reply_text(
                f"⚠️ {chat.title} ɪꜱ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ꜰᴏʀᴄᴇ-ꜱᴜʙꜱᴄʀɪʙᴇ ʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )

        # For private channels pre-generate invite link
        is_private = not chat.username
        invite_link = None
        if is_private:
            invite_link = await get_or_create_invite_link(client, chat.id)
            if not invite_link:
                return await message.reply_text(
                    f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ɢᴇɴᴇʀᴀᴛᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ꜰᴏʀ {chat.title}.\n\n"
                    "ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ʜᴀꜱ 𝗜𝗻𝘃𝗶𝘁𝗲 𝗨𝘀𝗲𝗿𝘀 ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ.",
                    parse_mode=enums.ParseMode.HTML
                )
            await db.set_fsub_invite_link(message.chat.id, channel_id, invite_link)

        await db.add_fsub_channel(message.chat.id, channel_id)

        ctype = "🔒 ᴘʀɪᴠᴀᴛᴇ" if is_private else "🌐 ᴘᴜʙʟɪᴄ"
        await message.reply_text(
            f"✅ {chat.title} ᴀᴅᴅᴇᴅ!\n\n"
            f"ᴛʏᴘᴇ: {ctype}\n"
            f"ɪᴅ: <code>{channel_id}</code>\n\n"
            "ᴜꜱᴇʀꜱ ɴᴏᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴡɪʟʟ ʙᴇ ʙʟᴏᴄᴋᴇᴅ ꜰʀᴏᴍ ꜱᴇɴᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ.",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /removefsub
    # ==========================================================

    @app.on_message(filters.group & filters.command("removefsub"))
    async def removefsub_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/removefsub @ᴄʜᴀɴɴᴇʟ</code> ᴏʀ <code>/removefsub -100xxxxxxxxxx</code>",
                parse_mode=enums.ParseMode.HTML
            )

        raw = parts[1].strip()
        try:
            if raw.lstrip("-").isdigit():
                chat = await client.get_chat(int(raw))
            else:
                chat = await client.get_chat(raw)
            channel_id = str(chat.id)
            title = chat.title
        except Exception:
            channel_id = raw
            title = raw

        removed = await db.remove_fsub_channel(message.chat.id, channel_id)
        await db.remove_fsub_invite_link(message.chat.id, channel_id)

        if removed:
            await message.reply_text(
                f"🗑 {title} ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ꜰᴏʀᴄᴇ-ꜱᴜʙꜱᴄʀɪʙᴇ ʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ {title} ᴡᴀꜱ ɴᴏᴛ ɪɴ ᴛʜᴇ ʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )

    # ==========================================================
    # /fsublist
    # ==========================================================

    @app.on_message(filters.group & filters.command("fsublist"))
    async def fsublist_cmd(client, message: Message):
        channels = await db.get_fsub_channels(message.chat.id)

        if not channels:
            return await message.reply_text(
                "📭 ɴᴏ ꜰᴏʀᴄᴇ-ꜱᴜʙꜱᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟꜱ ᴀᴅᴅᴇᴅ ʏᴇᴛ.\n"
                "ᴜꜱᴇ <code>/addfsub @ᴄʜᴀɴɴᴇʟ</code> ᴛᴏ ᴀᴅᴅ ᴏɴᴇ.",
                parse_mode=enums.ParseMode.HTML
            )

        text = "🔗 𝗙𝗼𝗿𝗰𝗲-𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗟𝗶𝘀𝘁\n\n"
        for i, ch_id in enumerate(channels, 1):
            try:
                chat = await client.get_chat(int(ch_id))
                if chat.username:
                    info = f"@{chat.username} 🌐"
                else:
                    info = f"<code>{ch_id}</code> 🔒"
                text += f"{i}. {chat.title} — {info}\n"
            except Exception:
                text += f"{i}. <code>{ch_id}</code>\n"

        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # Enforce FSub — check every non-admin message
    # ==========================================================

    @app.on_message(filters.group & ~filters.service, group=3)
    async def enforce_fsub(client, message: Message):
        if not message.from_user:
            return

        # Skip admins and owner
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except Exception:
            return

        channels = await db.get_fsub_channels(message.chat.id)
        if not channels:
            return

        not_joined = []
        for ch_id in channels:
            try:
                cid_int = int(ch_id)
            except (ValueError, TypeError):
                continue

            joined = await user_joined_channel(client, message.from_user.id, cid_int)
            if not joined:
                # Get channel info + link
                title = f"ᴄʜᴀɴɴᴇʟ {ch_id}"
                link  = None
                try:
                    chat = await client.get_chat(cid_int)
                    title = chat.title
                    if chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        # Try DB-stored link first
                        link = await db.get_fsub_invite_link(message.chat.id, ch_id)
                        if not link:
                            link = await get_or_create_invite_link(client, cid_int)
                            if link:
                                await db.set_fsub_invite_link(message.chat.id, ch_id, link)
                except Exception as e:
                    logger.error(f"ꜰꜱᴜʙ ᴄʜᴀᴛ ɪɴꜰᴏ ᴇʀʀᴏʀ {ch_id}: {e}")

                not_joined.append((title, link))

        if not not_joined:
            return

        # Delete the message
        try:
            await message.delete()
        except Exception:
            pass

        # Build join buttons
        buttons = [
            [InlineKeyboardButton(f"📢 ᴊᴏɪɴ: {title}", url=link, style=ButtonStyle.PRIMARY)]
            for title, link in not_joined if link
        ]

        warn_text = (
            f"🌺 {message.from_user.mention}!\n\n"
            f"📛 ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ / ɢʀᴏᴜᴘ ꜰɪʀꜱᴛ, ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇꜱ. ✅"
        )

        try:
            warn = await client.send_message(
                message.chat.id,
                warn_text,
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(30)
            await warn.delete()
        except Exception as e:
            logger.error(f"ꜰꜱᴜʙ ᴡᴀʀɴ ꜱᴇɴᴅ ᴇʀʀᴏʀ: {e}")
