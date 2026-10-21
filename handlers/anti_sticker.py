# ============================================================
# Group Manager Bot — Anti Sticker System
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import db
import logging
import asyncio

logger = logging.getLogger(__name__)

ANTI_STICKER_HELP_TEXT = (
    "╔══════════════════╗\n"
    "   🎭 𝗮𝗻𝘁𝗶 𝘀𝘁𝗶𝗰𝗸𝗲𝗿\n"
    "╚══════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /banpack — 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝘀𝘁𝗶𝗰𝗸𝗲𝗿 𝘁𝗼 𝗯𝗮𝗻 𝗶𝘁𝘀 𝗽𝗮𝗰𝗸\n"
    "➻ /unbanpack &lt;𝗽𝗮𝗰𝗸𝗻𝗮𝗺𝗲&gt; — 𝘂𝗻𝗯𝗮𝗻 𝗮 𝗽𝗮𝗰𝗸\n"
    "➻ /bannedpacks — 𝗹𝗶𝘀𝘁 𝗮𝗹𝗹 𝗯𝗮𝗻𝗻𝗲𝗱 𝗽𝗮𝗰𝗸𝘀\n"
    "➻ /clearbanpacks — 𝗰𝗹𝗲𝗮𝗿 𝗮𝗹𝗹 𝗯𝗮𝗻𝗻𝗲𝗱 𝗽𝗮𝗰𝗸𝘀\n"
    "➻ /antisticker 𝗼𝗻 — 𝗯𝗹𝗼𝗰𝗸 𝗮𝗹𝗹 𝘀𝘁𝗶𝗰𝗸𝗲𝗿𝘀\n"
    "➻ /antisticker 𝗼𝗳𝗳 — 𝗮𝗹𝗹𝗼𝘄 𝗮𝗹𝗹 𝘀𝘁𝗶𝗰𝗸𝗲𝗿𝘀\n\n"
    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ /banpack 𝗯𝗮𝗻𝘀 𝘁𝗵𝗲 𝗲𝗻𝘁𝗶𝗿𝗲 𝗽𝗮𝗰𝗸\n"
    "➻ /antisticker 𝗯𝗹𝗼𝗰𝗸𝘀 𝗲𝘃𝗲𝗿𝘆 𝘀𝘁𝗶𝗰𝗸𝗲𝗿\n"
    "➻ 𝗮𝗱𝗺𝗶𝗻𝘀 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗳𝗳𝗲𝗰𝘁𝗲𝗱"
)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


def register_anti_sticker_handler(app: Client):

    # ----------------------------------------------------------
    # /antisticker on|off — block ALL stickers
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("antisticker"))
    async def antisticker_toggle(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status = await db.get_antisticker_status(message.chat.id)
            cur = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ 𝗔𝗻𝘁𝗶-𝗦𝘁𝗶𝗰𝗸𝗲𝗿\n\n"
                f"ᴜꜱᴀɢᴇ: <code>/antisticker ᴏɴ</code> ᴏʀ <code>/antisticker ᴏꜰꜰ</code>\n\n"
                f"ꜱᴛᴀᴛᴜꜱ: {cur}",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_antisticker_status(message.chat.id, status)

        if status:
            await message.reply_text(
                "✅ 𝗔𝗻𝘁𝗶-𝗦𝘁𝗶𝗰𝗸𝗲𝗿 𝗢𝗡!\n\nᴀʟʟ ꜱᴛɪᴄᴋᴇʀꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "⚠️ 𝗔𝗻𝘁𝗶-𝗦𝘁𝗶𝗰𝗸𝗲𝗿 𝗢𝗙𝗙.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /banpack — reply to a sticker to ban its pack
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("banpack"))
    async def banpack_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʙᴀɴ ꜱᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋꜱ.")

        if not message.reply_to_message or not message.reply_to_message.sticker:
            return await message.reply_text(
                "⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ʙᴀɴ ɪᴛꜱ ᴘᴀᴄᴋ.",
                parse_mode=enums.ParseMode.HTML
            )

        sticker   = message.reply_to_message.sticker
        pack_name = sticker.set_name

        if not pack_name:
            return await message.reply_text("⚠️ ᴛʜɪꜱ ꜱᴛɪᴄᴋᴇʀ ʜᴀꜱ ɴᴏ ᴘᴀᴄᴋ (ɪᴛ'ꜱ ᴀ ꜱᴛᴀɴᴅᴀʟᴏɴᴇ ꜱᴛɪᴄᴋᴇʀ).")

        banned = await db.get_banned_packs(message.chat.id)
        if pack_name.lower() in banned:
            return await message.reply_text(
                f"⚠️ ᴘᴀᴄᴋ <code>{pack_name}</code> ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )

        await db.add_banned_pack(message.chat.id, pack_name)
        # Delete the sticker itself
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass

        await message.reply_text(
            f"🚫 ꜱᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ <code>{pack_name}</code> ʙᴀɴɴᴇᴅ!\n"
            f"ᴀʟʟ ꜱᴛɪᴄᴋᴇʀꜱ ꜰʀᴏᴍ ᴛʜɪꜱ ᴘᴀᴄᴋ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # /unbanpack <packname>
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("unbanpack"))
    async def unbanpack_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜɴʙᴀɴ ꜱᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋꜱ.")

        parts = message.text.split(maxsplit=1)

        # Allow reply to sticker too
        if message.reply_to_message and message.reply_to_message.sticker:
            pack_name = message.reply_to_message.sticker.set_name
        elif len(parts) > 1:
            pack_name = parts[1].strip()
        else:
            return await message.reply_text(
                "⚙️ ᴜꜱᴀɢᴇ: <code>/unbanpack ᴘᴀᴄᴋɴᴀᴍᴇ</code> ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ.",
                parse_mode=enums.ParseMode.HTML
            )

        removed = await db.remove_banned_pack(message.chat.id, pack_name)
        if removed:
            await message.reply_text(
                f"✅ ᴘᴀᴄᴋ <code>{pack_name}</code> ᴜɴʙᴀɴɴᴇᴅ.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ ᴘᴀᴄᴋ <code>{pack_name}</code> ᴡᴀꜱ ɴᴏᴛ ɪɴ ᴛʜᴇ ʙᴀɴɴᴇᴅ ʟɪꜱᴛ.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /bannedpacks — list all banned packs
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("bannedpacks"))
    async def bannedpacks_cmd(client, message: Message):
        packs = await db.get_banned_packs(message.chat.id)

        if not packs:
            return await message.reply_text("📭 ɴᴏ ꜱᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋꜱ ᴀʀᴇ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.")

        text = (
            f"🚫 𝗕𝗮𝗻𝗻𝗲𝗱 𝗣𝗮𝗰𝗸𝘀 — {message.chat.title}\n\n"
            + "\n".join(f"• <code>{p}</code>" for p in sorted(packs))
            + ""
        )
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ----------------------------------------------------------
    # /clearbanpacks — remove all banned packs
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("clearbanpacks"))
    async def clearbanpacks_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʟᴇᴀʀ ʙᴀɴɴᴇᴅ ᴘᴀᴄᴋꜱ.")

        packs = await db.get_banned_packs(message.chat.id)
        if not packs:
            return await message.reply_text("📭 ɴᴏ ʙᴀɴɴᴇᴅ ᴘᴀᴄᴋꜱ ᴛᴏ ᴄʟᴇᴀʀ.")

        await db.clear_banned_packs(message.chat.id)
        await message.reply_text(
            f"🗑 ᴄʟᴇᴀʀᴇᴅ {len(packs)} ʙᴀɴɴᴇᴅ ꜱᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ(ꜱ).",
            parse_mode=enums.ParseMode.HTML
        )

    # ----------------------------------------------------------
    # Enforce — delete stickers from banned packs + antisticker
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.sticker, group=4)
    async def enforce_sticker(client, message: Message):
        if not message.from_user:
            return

        # Skip admins
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except Exception:
            return

        chat_id = message.chat.id

        # Check antisticker (block all)
        if await db.get_antisticker_status(chat_id):
            try:
                await message.delete()
            except Exception:
                pass
            return

        # Check banned packs
        sticker   = message.sticker
        pack_name = sticker.set_name if sticker else None
        if not pack_name:
            return

        banned_packs = await db.get_banned_packs(chat_id)
        if pack_name.lower() in banned_packs:
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"ᴀɴᴛɪ-ꜱᴛɪᴄᴋᴇʀ ᴅᴇʟᴇᴛᴇ ᴇʀʀᴏʀ: {e}")
