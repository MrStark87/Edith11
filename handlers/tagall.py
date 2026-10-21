# ============================================================
# Group Manager Bot — Tag All
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import asyncio
import random
import logging

logger = logging.getLogger(__name__)

# Track active tagging per chat
_active_tagging: set = set()

# Emoji sets — each string = 5 emojis, one per person
EMOJIS = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵", "❤️💚💙💜🖤", "💓💕💞💗💖",
    "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗", "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷", "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿", "🌨️🌥️⛈️🌩️🌧️", "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁", "🧟🦸🦹🧙👸", "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️", "🦋🐇🐀🐈🐈‍⬛", "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇", "🍴🍽️🔪🍶🥃", "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀", "🪴🌵🌴🌳🌲", "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢", "🦤🦩🦚🦃🦆", "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐", "🦩🦀🦑🐙🦪", "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨", "🥬🍉🧁🧇🍫",
]


TAGALL_HELP_TEXT = (
    "╔═══════════════╗\n"
    "  🔖 𝘁𝗮𝗴 𝗮𝗹𝗹\n"
    "╚═══════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /tagall — 𝘁𝗮𝗴 𝗮𝗹𝗹 𝗺𝗲𝗺𝗯𝗲𝗿𝘀\n"
    "➻ /tagall {𝗺𝗲𝘀𝘀𝗮𝗴𝗲} — 𝘁𝗮𝗴 𝘄𝗶𝘁𝗵 𝗰𝘂𝘀𝘁𝗼𝗺 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
    "➻ /stoptag — 𝘀𝘁𝗼𝗽 𝘁𝗮𝗴𝗴𝗶𝗻𝗴\n\n"
    "❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
    "➻ 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆\n"
    "➻ 1 𝗲𝗺𝗼𝗷𝗶 = 1 𝗽𝗲𝗿𝘀𝗼𝗻 𝗺𝗲𝗻𝘁𝗶𝗼𝗻\n"
    "➻ 5 𝗽𝗲𝗼𝗽𝗹𝗲 𝗽𝗲𝗿 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
    "➻ 𝗯𝗼𝘁𝘀 & 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁𝘀 𝘀𝗸𝗶𝗽𝗽𝗲𝗱"
)


async def is_power(client, chat_id: int, user_id: int) -> bool:
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


def register_tagall_handler(app: Client):

    # ----------------------------------------------------------
    # /tagall [message]
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("tagall"))
    async def tagall_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        chat_id = message.chat.id

        if chat_id in _active_tagging:
            return await message.reply_text(
                "⚠️ ᴛᴀɢɢɪɴɢ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ. ᴜꜱᴇ /stoptag ᴛᴏ ꜱᴛᴏᴘ."
            )

        parts      = message.text.split(maxsplit=1)
        custom_msg = parts[1].strip() if len(parts) > 1 else ""
        header     = f"📢 {custom_msg}\n\n" if custom_msg else "📢 𝗔𝘁𝘁𝗲𝗻𝘁𝗶𝗼𝗻 𝗲𝘃𝗲𝗿𝘆𝗼𝗻𝗲!\n\n"

        _active_tagging.add(chat_id)

        # Shuffle emoji list so each tagall looks fresh
        emoji_pool = EMOJIS.copy()
        random.shuffle(emoji_pool)

        # Flatten: extract individual emojis from each string
        # Each EMOJIS entry has 5 emoji chars — split into individual ones
        import unicodedata

        def split_emojis(s: str) -> list:
            """ꜱᴘʟɪᴛ ᴇᴍᴏᴊɪ ꜱᴛʀɪɴɢ ɪɴᴛᴏ ɪɴᴅɪᴠɪᴅᴜᴀʟ ɢʀᴀᴘʜᴇᴍᴇ ᴄʟᴜꜱᴛᴇʀꜱ."""
            result = []
            # Use simple iteration — works for most emoji
            chars = list(s)
            i = 0
            while i < len(chars):
                # Check for ZWJ sequences or skin tone modifiers
                c = chars[i]
                cluster = c
                # Combine with next char if it's a modifier/ZWJ
                while i + 1 < len(chars):
                    nxt = chars[i + 1]
                    cp  = ord(nxt)
                    if cp in (0x200D, 0xFE0F) or (0x1F3FB <= cp <= 0x1F3FF):
                        i += 1
                        cluster += chars[i]
                    else:
                        break
                result.append(cluster)
                i += 1
            return [x for x in result if x.strip()]

        all_emojis = []
        for e_str in emoji_pool:
            all_emojis.extend(split_emojis(e_str))

        if not all_emojis:
            all_emojis = ["🌸", "💐", "🦋", "🌺", "💮"]

        emoji_index = 0

        try:
            batch = []

            async for member in client.get_chat_members(chat_id):
                if member.user.is_bot or member.user.is_deleted:
                    continue

                if chat_id not in _active_tagging:
                    await client.send_message(chat_id, "🛑 ᴛᴀɢɢɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ.")
                    return

                # 1 emoji → 1 person mention
                emoji = all_emojis[emoji_index % len(all_emojis)]
                emoji_index += 1

                mention = f'<a href="tg://user?id={member.user.id}">{emoji}</a>'
                batch.append(mention)

                # Send batch of 5 — each message has exactly 5 emoji mentions
                if len(batch) == 5:
                    await client.send_message(
                        chat_id,
                        header + "".join(batch),
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    batch.clear()
                    await asyncio.sleep(2)

            # Send remaining (less than 5)
            if batch and chat_id in _active_tagging:
                await client.send_message(
                    chat_id,
                    header + "".join(batch),
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True
                )

        except Exception as e:
            logger.error(f"ᴛᴀɢᴀʟʟ ᴇʀʀᴏʀ: {e}")
            await client.send_message(chat_id, f"❌ ᴛᴀɢɢɪɴɢ ꜰᴀɪʟᴇᴅ: {e}")
        finally:
            _active_tagging.discard(chat_id)

    # ----------------------------------------------------------
    # /stoptag
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("stoptag"))
    async def stoptag_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        if message.chat.id in _active_tagging:
            _active_tagging.discard(message.chat.id)
            await message.reply_text("🛑 ᴛᴀɢɢɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ.")
        else:
            await message.reply_text("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀɢɢɪɴɢ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ.")
                         
