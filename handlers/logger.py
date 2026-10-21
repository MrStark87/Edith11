# ============================================================
# Group Manager Bot — Add/Remove Logger
# Author: Mr. Stark
# ============================================================

from pyrogram import Client
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# States that mean the bot is "in" the chat
IN_CHAT = [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
# States that mean the bot is "out" of the chat
OUT_CHAT = [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]


async def get_invite_link(client: Client, chat_id: int, chat) -> str:
    """ᴛʀʏ ᴇᴠᴇʀʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴡᴀʏ ᴛᴏ ɢᴇᴛ ᴀ ʟɪɴᴋ ꜰᴏʀ ᴛʜɪꜱ ᴄʜᴀᴛ."""
    if chat.username:
        return f"https://t.me/{chat.username}"
    try:
        link = await client.export_chat_invite_link(chat_id)
        return link
    except Exception:
        pass
    try:
        link_obj = await client.create_chat_invite_link(chat_id)
        return link_obj.invite_link
    except Exception:
        pass
    return "⚠️ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ (ʙᴏᴛ ʜᴀꜱ ɴᴏ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴘᴇʀᴍɪꜱꜱɪᴏɴ)"


def register_logger_handler(app: Client):

    from config import LOG_CHANNEL_ID

    @app.on_chat_member_updated()
    async def log_bot_membership(client: Client, cmu: ChatMemberUpdated):
        me = client.me
        if me is None:
            try:
                me = await client.get_me()
            except Exception:
                return

        new_member = cmu.new_chat_member
        old_member = cmu.old_chat_member

        # We only care about updates concerning the bot itself
        target_user = None
        if new_member:
            target_user = new_member.user
        elif old_member:
            target_user = old_member.user

        if not target_user or target_user.id != me.id:
            return

        old_status = old_member.status if old_member else None
        new_status = new_member.status if new_member else None

        was_in = old_status in IN_CHAT
        is_in = new_status in IN_CHAT

        chat = cmu.chat
        actor = cmu.from_user
        actor_text = (
            f"{actor.mention} (<code>{actor.id}</code>)"
            if actor else "Unknown"
        )
        now_str = datetime.now().strftime("%ᴅ %ʙ %ʏ, %ɪ:%ᴍ %ᴘ")

        try:
            member_count = await client.get_chat_members_count(chat.id)
        except Exception:
            member_count = "N/A"

        # ============================================
        # Bot was just ADDED to a group/channel
        # ============================================
        if not was_in and is_in:
            link = await get_invite_link(client, chat.id, chat)
            text = (
                "╔══════════════════╗\n"
                "   ✅ ʙᴏᴛ ᴀᴅᴅᴇᴅ\n"
                "╚══════════════════╝\n\n"
                f"📛 𝗖𝗵𝗮𝘁: {chat.title}\n"
                f"🆔 𝗜𝗗: <code>{chat.id}</code>\n"
                f"👥 𝗠𝗲𝗺𝗯𝗲𝗿𝘀: {member_count}\n"
                f"🔗 𝗟𝗶𝗻𝗸: {link}\n"
                f"➕ 𝗔𝗱𝗱𝗲𝗱 𝗯𝘆: {actor_text}\n"
                f"🕐 𝗧𝗶𝗺𝗲: {now_str}"
            )
            try:
                await client.send_message(LOG_CHANNEL_ID, text, parse_mode="html")
            except Exception as e:
                logger.error(f"ʟᴏɢɢᴇʀ ꜱᴇɴᴅ ᴇʀʀᴏʀ (ᴀᴅᴅᴇᴅ): {e}")

        # ============================================
        # Bot was just REMOVED from a group/channel
        # ============================================
        elif was_in and not is_in:
            action = "Banned" if new_status == ChatMemberStatus.BANNED else "ᴋɪᴄᴋᴇᴅ / ʟᴇꜰᴛ"
            text = (
                "╔══════════════════╗\n"
                "   ❌ ʙᴏᴛ ʀᴇᴍᴏᴠᴇᴅ\n"
                "╚══════════════════╝\n\n"
                f"📛 𝗖𝗵𝗮𝘁: {chat.title}\n"
                f"🆔 𝗜𝗗: <code>{chat.id}</code>\n"
                f"🚪 𝗔𝗰𝘁𝗶𝗼𝗻: {action}\n"
                f"➖ 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗯𝘆: {actor_text}\n"
                f"🕐 𝗧𝗶𝗺𝗲: {now_str}"
            )
            try:
                await client.send_message(LOG_CHANNEL_ID, text, parse_mode="html")
            except Exception as e:
                logger.error(f"ʟᴏɢɢᴇʀ ꜱᴇɴᴅ ᴇʀʀᴏʀ (ʀᴇᴍᴏᴠᴇᴅ): {e}")
      
