# ============================================================
# Group Manager Bot — Warn System (Fixed DB Attribute Error)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import db  # Kuch functions ke liye as it is rahega
import logging

logger = logging.getLogger(__name__)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def extract_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        return None
    try:
        arg = parts[1]
        if arg.lstrip("-").isdigit():
            return await client.get_users(int(arg))
        return await client.get_users(arg)
    except Exception:
        return None


async def _take_action(client, chat_id: int, user_id: int, action: str):
    try:
        if action == "ban":
            await client.ban_chat_member(chat_id, user_id)
        elif action == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        elif action == "mute":
            await client.restrict_chat_member(
                chat_id, user_id,
                ChatPermissions(can_send_messages=False)
            )
    except Exception as e:
        logger.error(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴡᴀʀɴ ᴀᴄᴛɪᴏɴ ({action}) ᴏɴ ᴜꜱᴇʀ {user_id}: {e}")


def register_warns_handler(app: Client):

    # ==========================================================
    # /warn
    # ==========================================================
    @app.on_message(filters.group & filters.command("warn"))
    async def warn_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴡᴀʀɴ ᴜꜱᴇʀꜱ.")

        user = await extract_user(client, message)
        if not user:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇɪʀ ᴜꜱᴇʀɴᴀᴍᴇ/ID ᴛᴏ ᴡᴀʀɴ ᴛʜᴇᴍ.")

        if user.is_bot:
            return await message.reply_text("🤖 ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴡᴀʀɴ ʙᴏᴛꜱ.")

        if await is_power(client, message.chat.id, user.id):
            return await message.reply_text("🛡️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴡᴀʀɴ ᴀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀ.")

        parts = message.text.split(maxsplit=2)
        reason = "ɴᴏ ʀᴇᴀꜱᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ."
        if message.reply_to_message:
            if len(parts) >= 2:
                reason = message.text.split(maxsplit=1)[1]
        else:
            if len(parts) >= 3:
                reason = parts[2]

        chat_id     = message.chat.id
        warn_limit  = await db.get_warn_limit(chat_id)
        warn_action = await db.get_warn_action(chat_id)

        warns = await db.add_warn(chat_id, user.id, reason)
        warn_count = warns["count"] if isinstance(warns, dict) else warns

        if warn_count >= warn_limit:
            # Reset warns direct MongoDB se (Taaki db.py ka crash na ho)
            await db.db.warns.delete_one({"chat_id": chat_id, "user_id": user.id})
            await _take_action(client, chat_id, user.id, warn_action)
            action_emoji = {"ban": "🚫", "kick": "👢", "mute": "🔇"}.get(warn_action, "🚫")
            await message.reply_text(
                f"{action_emoji} {user.mention} ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴍᴀx ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ ({warn_limit}/{warn_limit}) "
                f"ᴀɴᴅ ʜᴀꜱ ʙᴇᴇɴ {warn_action}ᴅ!\n"
                f"ℹ️ 𝗟𝗮𝘀𝘁 𝗥𝗲𝗮𝘀𝗼𝗻: {reason}",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                f"⚠️ {user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴡᴀʀɴᴇᴅ! ({warn_count}/{warn_limit})\n"
                f"ℹ️ 𝗥𝗲𝗮𝘀𝗼𝗻: {reason}",
                parse_mode=enums.ParseMode.HTML
            )

    # ==========================================================
    # /unwarn /rmwarn (FIXED DIRECT DB INTEGRATION)
    # ==========================================================
    @app.on_message(filters.group & filters.command(["unwarn", "rmwarn"]))
    async def unwarn_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴɪɴɢꜱ.")

        user = await extract_user(client, message)
        if not user:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜꜱᴇʀɴᴀᴍᴇ/ID ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴɪɴɢꜱ.")

        chat_id = message.chat.id
        
        # Direct MongoDB collection check se active warnings status fetch kiya
        warn_data = await db.db.warns.find_one({"chat_id": chat_id, "user_id": user.id})
        
        if not warn_data:
            return await message.reply_text(f"✨ {user.mention} ʜᴀꜱ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴡᴀʀɴɪɴɢꜱ.")

        current_count = warn_data.get("count", 0) if isinstance(warn_data, dict) else warn_data
        if current_count <= 1:
            # Agar 1 hi warn tha toh poora document delete kar do
            await db.db.warns.delete_one({"chat_id": chat_id, "user_id": user.id})
            new_warn_count = 0
        else:
            # Agar zyada the toh database se count -1 kiya aur last reason remove kiya
            updated = await db.db.warns.find_one_and_update(
                {"chat_id": chat_id, "user_id": user.id},
                {"$inc": {"count": -1}, "$pop": {"reasons": 1}},
                return_document=True
            )
            new_warn_count = updated.get("count", 0)

        warn_limit = await db.get_warn_limit(chat_id)
        await message.reply_text(
            f"✅ ʀᴇᴍᴏᴠᴇᴅ ᴀ ᴡᴀʀɴɪɴɢ ꜰʀᴏᴍ {user.mention}.\n"
            f"📊 ʀᴇᴍᴀɪɴɪɴɢ ᴡᴀʀɴɪɴɢꜱ: {new_warn_count}/{warn_limit}",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # /warns
    # ==========================================================
    @app.on_message(filters.group & filters.command("warns"))
    async def warns_cmd(client, message: Message):
        user = await extract_user(client, message) or message.from_user
        chat_id = message.chat.id

        warn_data = await db.db.warns.find_one({"chat_id": chat_id, "user_id": user.id})
        warn_limit = await db.get_warn_limit(chat_id)

        if not warn_data:
            return await message.reply_text(f"✨ {user.mention} ʜᴀꜱ 0/{warn_limit} ᴡᴀʀɴɪɴɢꜱ.", parse_mode=enums.ParseMode.HTML)

        warn_count = warn_data.get("count", 0) if isinstance(warn_data, dict) else warn_data

        if warn_count == 0:
            return await message.reply_text(f"✨ {user.mention} ʜᴀꜱ 0/{warn_limit} ᴡᴀʀɴɪɴɢꜱ.", parse_mode=enums.ParseMode.HTML)

        res = f"⚠️ 𝗪𝗮𝗿𝗻𝗶𝗻𝗴𝘀 𝗳𝗼𝗿 {user.mention} (ᴛᴏᴛᴀʟ: {warn_count}/{warn_limit}):\n\n"
        if isinstance(warn_data, dict) and "reasons" in warn_data:
            for i, r in enumerate(warn_data["reasons"], 1):
                res += f"{i}. {r}\n"
        else:
            res += "• ᴀᴄᴛɪᴠᴇ ᴡᴀʀɴɪɴɢꜱ ᴘʀᴇꜱᴇɴᴛ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ."

        await message.reply_text(res, parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /resetwarns (FIXED DIRECT DB INTEGRATION)
    # ==========================================================
    @app.on_message(filters.group & filters.command("resetwarns"))
    async def resetwarns_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʀᴇꜱᴇᴛ ᴡᴀʀɴɪɴɢꜱ.")

        user = await extract_user(client, message)
        if not user:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜꜱᴇʀɴᴀᴍᴇ/ID ᴛᴏ ʀᴇꜱᴇᴛ ᴡᴀʀɴɪɴɢꜱ.")

        # Direct database se wipe kiya taaki db.py dependency khatam ho sake
        await db.db.warns.delete_one({"chat_id": message.chat.id, "user_id": user.id})
        await message.reply_text(f"🧹 ᴀʟʟ ᴡᴀʀɴɪɴɢꜱ ꜰᴏʀ {user.mention} ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ.")

    # ==========================================================
    # /setwarnlimit
    # ==========================================================
    @app.on_message(filters.group & filters.command("setwarnlimit"))
    async def setwarnlimit_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ.")

        parts = message.text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            cur_limit = await db.get_warn_limit(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/setwarnlimit [2-10]</code>\n"
                f"ᴄᴜʀʀᴇɴᴛ ʟɪᴍɪᴛ: {cur_limit}",
                parse_mode=enums.ParseMode.HTML
            )

        limit = int(parts[1])
        if limit < 2 or limit > 10:
            return await message.reply_text("❌ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 2 ᴀɴᴅ 10.")

        await db.set_warn_limit(message.chat.id, limit)
        await message.reply_text(f"✅ ᴍᴀx ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ ꜱᴇᴛ ᴛᴏ {limit}.", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /setwarnaction
    # ==========================================================
    @app.on_message(filters.group & filters.command("setwarnaction"))
    async def setwarnaction_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴀʀɴ ᴀᴄᴛɪᴏɴ.")

        parts      = message.text.split(maxsplit=1)
        valid      = ["mute", "kick", "ban"]
        cur_action = await db.get_warn_action(message.chat.id)

        if len(parts) < 2 or parts[1].strip().lower() not in valid:
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/setwarnaction ᴍᴜᴛᴇ|ᴋɪᴄᴋ|ʙᴀɴ</code>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ: {cur_action}\n\n"
                f"• 𝗺𝘂𝘁𝗲 — ʀᴇꜱᴛʀɪᴄᴛ ꜰʀᴏᴍ ꜱᴇɴᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ\n"
                f"• 𝗸𝗶𝗰𝗸 — ʀᴇᴍᴏᴠᴇ (ᴄᴀɴ ʀᴇᴊᴏɪɴ)\n"
                f"• 𝗯𝗮𝗻 — ᴘᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ",
                parse_mode=enums.ParseMode.HTML
            )

        action = parts[1].strip().lower()
        await db.set_warn_action(message.chat.id, action)
        emoji = {"mute": "🔇", "kick": "👢", "ban": "🚫"}[action]
        await message.reply_text(f"✅ ᴡᴀʀɴ ᴀᴄᴛɪᴏɴ ꜱᴇᴛ ᴛᴏ {emoji} {action.upper()}.", parse_mode=enums.ParseMode.HTML)
