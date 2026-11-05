# ============================================================
# Group Manager Bot — Captcha System (Fixed Database System)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, ChatMemberUpdated,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ChatPermissions
)
from pyrogram.enums import ChatMemberStatus
import db
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

CAPTCHA_HELP_TEXT = (
    f"<blockquote>🤖 <b>𝖢𝖺𝗉𝗍𝖼𝗁𝖺 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
    f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
    f"➻ <code>/captcha on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 𝖢𝖺𝗉𝗍𝖼𝗁𝖺 ✅\n"
    f"➻ <code>/captcha off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖢𝖺𝗉𝗍𝖼𝗁𝖺 ❌\n"
    f"➻ <code>/captchatime &lt;seconds&gt;</code> — 𝖲𝖾𝗍 𝖳𝗂𝗆𝖾𝗈𝗎𝗍\n\n"
    f"<blockquote expandable>❖ <b>𝖧𝗈𝗐 𝖨𝗍 𝖶𝗈𝗋𝗄𝗌</b> ❖</blockquote>\n"
    f"➻ 𝖭𝖾𝗐 𝖬𝖾𝗆𝖻𝖾𝗋 𝖩𝗈𝗂𝗇𝗌 → 𝖬𝗎𝗍𝖾𝖽 𝖨𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒\n"
    f"➻ 𝖬𝗎𝗌𝗍 𝖲𝗈𝗅𝗏𝖾 𝖬𝖺𝗍𝗁 𝖰𝗎𝖾𝗌𝗍𝗂𝗈𝗇 𝖳𝗈 𝖴𝗇𝗆𝗎𝗍𝖾\n"
    f"➻ 𝖥𝖺𝗂𝗅𝗌 / 𝖳𝗂𝗆𝖾𝗈𝗎𝗍 → 𝖪𝗂𝖼𝗄𝖾𝖽 𝖥𝗋𝗈𝗆 𝖦𝗋𝗈𝗎𝗉"
)


CAPTCHA_TEXT = (
    f"➻ <code>/captcha on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 𝖢𝖺𝗉𝗍𝖼𝗁𝖺 ✅\n"
    f"➻ <code>/captcha off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖢𝖺𝗉𝗍𝖼𝗁𝖺 ❌\n"
    f"➻ <code>/captchatime &lt;seconds&gt;</code> — 𝖲𝖾𝗍 𝖳𝗂𝗆𝖾𝗈𝗎𝗍\n\n"
)

async def is_power(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


def register_captcha_handler(app: Client):

    @app.on_message(filters.group & filters.command("captcha"))
    async def captcha_switch_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ᴄᴀᴘᴛᴄʜᴀ ꜱᴇᴛᴛɪɴɢꜱ.")

        parts = message.text.split()
        if len(parts) < 2:
            status = await db.get_captcha_status(message.chat.id)
            status_str = "ᴇɴᴀʙʟᴇᴅ ✅" if status else "ᴅɪꜱᴀʙʟᴇᴅ ❌"
            return await message.reply_text(
                f"{CAPTCHA_TEXT} ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {status_str}",
                parse_mode=enums.ParseMode.HTML
            )

        opt = parts[1].strip().lower()
        if opt == "on":
            await db.set_captcha_status(message.chat.id, True)
            await message.reply_text("✅ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 𝘀𝘆𝘀𝘁𝗲𝗺 𝗲𝗻𝗮𝗯𝗹𝗲𝗱. ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ ᴍᴜꜱᴛ ᴠᴇʀɪꜰʏ ᴛʜᴇᴍꜱᴇʟᴠᴇꜱ.", parse_mode=enums.ParseMode.HTML)
        elif opt == "off":
            await db.set_captcha_status(message.chat.id, False)
            await message.reply_text("❌ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 𝘀𝘆𝘀𝘁𝗲𝗺 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱. ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ᴄʜᴀᴛ ꜰʀᴇᴇʟʏ.", parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text("❗ ᴜꜱᴇ <code>/captcha ᴏɴ</code> ᴏʀ <code>/captcha ᴏꜰꜰ</code>.", parse_mode=enums.ParseMode.HTML)

    @app.on_message(filters.group & filters.command("captchatime"))
    async def captchatime_cmd(client, message: Message):
        if not await is_power(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴄᴀᴘᴛᴄʜᴀ ᴛɪᴍᴇᴏᴜᴛ.")

        parts = message.text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            cur_time = await db.get_captcha_timeout(message.chat.id)
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/captchatime [30-300]</code> (ɪɴ ꜱᴇᴄᴏɴᴅꜱ)\n"
                f"ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇᴏᴜᴛ: {cur_time}ꜱ",
                parse_mode=enums.ParseMode.HTML
            )

        sec = int(parts[1])
        if sec < 30 or sec > 300:
            return await message.reply_text("❌ ᴛɪᴍᴇᴏᴜᴛ ᴍᴜꜱᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 30 ᴀɴᴅ 300 ꜱᴇᴄᴏɴᴅꜱ.")

        await db.set_captcha_timeout(message.chat.id, sec)
        await message.reply_text(f"✅ ᴄᴀᴘᴛᴄʜᴀ ᴛɪᴍᴇᴏᴜᴛ ꜱᴇᴛ ᴛᴏ {sec} ꜱᴇᴄᴏɴᴅꜱ.", parse_mode=enums.ParseMode.HTML)

    @app.on_chat_member_updated(filters.group)
    async def captcha_join_handler(client, cms: ChatMemberUpdated):
        if not cms.new_chat_member or cms.new_chat_member.status != ChatMemberStatus.MEMBER:
            return  # Not a newly joined regular member

        # Skip bots
        user = cms.new_chat_member.user
        if user.is_bot:
            return

        chat_id = cms.chat.id
        if not await db.get_captcha_status(chat_id):
            return  # Captcha setting off hai

        # Step 1: Restrict/Mute user instantly
        try:
            await client.restrict_chat_member(chat_id, user.id, ChatPermissions(can_send_messages=False))
        except Exception as e:
            logger.error(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴍᴜᴛᴇ ᴜꜱᴇʀ ꜰᴏʀ ᴄᴀᴘᴛᴄʜᴀ: {e}")
            return

        # Step 2: Generate Math Question
        a, b = random.randint(1, 9), random.randint(1, 9)
        ans = a + b

        # Generate fake options
        options = {ans, random.randint(2, 18), random.randint(2, 18), random.randint(2, 18)}
        while len(options) < 4:
            options.add(random.randint(2, 18))
        options = list(options)
        random.shuffle(options)

        # Save to direct DB pending list
        await db.db.captcha_pending.update_one(
            {"chat_id": chat_id, "user_id": user.id},
            {"$set": {"answer": ans}},
            upsert=True
        )

        # Create Keyboard buttons
        buttons = []
        row = []
        for opt in options:
            row.append(InlineKeyboardButton(str(opt), callback_data=f"cap:{user.id}:{opt}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        timeout = await db.get_captcha_timeout(chat_id)

        welcome_msg = await client.send_message(
            chat_id,
            f"🎯 ᴡᴇʟᴄᴏᴍᴇ {user.mention} ᴛᴏ {cms.chat.title}!\n"
            f"🔒 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ꜰᴏʀ ꜱᴇᴄᴜʀɪᴛʏ.\n\n"
            f"ᴘʟᴇᴀꜱᴇ ꜱᴏʟᴠᴇ ᴛʜɪꜱ ᴇǫᴜᴀᴛɪᴏɴ ᴛᴏ ᴛᴀʟᴋ: **{a} + {b} = ?**\n"
            f"⏳ ʏᴏᴜ ʜᴀᴠᴇ {timeout} ꜱᴇᴄᴏɴᴅꜱ.",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

        # Start timeout tasks background trigger
        asyncio.get_event_loop().create_task(_captcha_timeout(client, chat_id, user.id, welcome_msg.id, timeout))

    @app.on_callback_query(filters.regex(r"^cap:"))
    async def captcha_callback_handler(client, query):
        data = query.data.split(":")
        target_user_id = int(data[1])
        chosen_ans     = int(data[2])
        chat_id        = query.message.chat.id

        if query.from_user.id != target_user_id:
            return await query.answer("❌ ᴛʜɪꜱ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)

        pending = await db.db.captcha_pending.find_one({"chat_id": chat_id, "user_id": target_user_id})
        if not pending:
            return await query.answer("✨ ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪꜰɪᴇᴅ ᴏʀ ᴛɪᴍᴇᴅ ᴏᴜᴛ.", show_alert=True)

        correct_ans = pending.get("answer")

        if chosen_ans == correct_ans:
            await db.db.captcha_pending.delete_one({"chat_id": chat_id, "user_id": target_user_id})
            try:
                # Unmute completely
                await client.restrict_chat_member(
                    chat_id, target_user_id,
                    ChatPermissions(
                        can_send_messages=True, can_send_media_messages=True,
                        can_send_other_messages=True, can_add_web_page_previews=True
                    )
                )
                await query.message.edit_text(f"✅ {query.from_user.mention} ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴠᴇʀɪꜰɪᴇᴅ! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴄʜᴀᴛ.")
            except Exception as e:
                logger.error(f"ᴄᴀᴘᴛᴄʜᴀ ᴜɴᴍᴜᴛᴇ ᴇʀʀᴏʀ: {e}")
                await query.message.edit_text("✅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ʙᴜᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ꜰᴀɪʟᴇᴅ. ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ.")
            
            asyncio.get_event_loop().create_task(_delete_after(query.message, 10))
        else:
            await query.answer("❌ ᴡʀᴏɴɢ ᴀɴꜱᴡᴇʀ! ᴛʀʏ ᴀɢᴀɪɴ ᴄᴀʀᴇꜰᴜʟʟʏ.", show_alert=True)

    @app.on_message(filters.group, group=6)
    async def block_pending_user(client, message: Message):
        if not message.from_user:
            return
        pending = await db.db.captcha_pending.find_one({"chat_id": message.chat.id, "user_id": message.from_user.id})
        if pending:
            try:
                await message.delete()
            except Exception:
                pass


async def _delete_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


async def _captcha_timeout(client, chat_id: int, user_id: int, msg_id: int, timeout: int):
    await asyncio.sleep(timeout)
    pending = await db.db.captcha_pending.find_one({"chat_id": chat_id, "user_id": user_id})
    if not pending:
        return

    await db.db.captcha_pending.delete_one({"chat_id": chat_id, "user_id": user_id})

    try:
        await client.ban_chat_member(chat_id, user_id)
        await client.unban_chat_member(chat_id, user_id)
    except Exception as e:
        logger.error(f"ᴄᴀᴘᴛᴄʜᴀ ᴛɪᴍᴇᴏᴜᴛ ᴋɪᴄᴋ ᴇʀʀᴏʀ: {e}")

    try:
        await client.edit_message_text(chat_id, msg_id, "⏳ ᴄᴀᴘᴛᴄʜᴀ ᴛɪᴍᴇᴅ ᴏᴜᴛ — ᴜꜱᴇʀ ᴡᴀꜱ ᴋɪᴄᴋᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(10)
        await client.delete_messages(chat_id, msg_id)
    except Exception:
        pass
