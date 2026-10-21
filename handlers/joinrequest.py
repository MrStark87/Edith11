# ============================================================
# Group Manager Bot — Auto Accept Join Requests
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.enums import ChatMemberStatus

import asyncio
import logging
import db

logger = logging.getLogger(__name__)


# ============================================================
# Helpers
# ============================================================

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)

        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )

    except Exception as e:
        logger.error(f"ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ꜰᴀɪʟᴇᴅ: {e}")
        return False


async def bot_can_manage_requests(
    client: Client,
    chat_id: int
) -> bool:

    try:
        bot = await client.get_chat_member(chat_id, "me")

        return (
            bot.privileges
            and bot.privileges.can_manage_chat_join_requests
        )

    except Exception as e:
        logger.error(f"ʙᴏᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴄʜᴇᴄᴋ ꜰᴀɪʟᴇᴅ: {e}")
        return False


# ============================================================
# Help Text
# ============================================================

JOINREQUEST_HELP_TEXT = (
    f"╔════════════════════════╗\n"
    f" 🤖 𝗮𝘂𝘁𝗼 𝗮𝗰𝗰𝗲𝗽𝘁 – 𝗷𝗼𝗶𝗻 𝗿𝗲𝗾𝘂𝗲𝘀𝘁𝘀\n"
    f"╚════════════════════════╝\n\n"

    f"❖ 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ❖\n\n"

    f"➻ /acceptall 𝗼𝗻 — 𝗮𝘂𝘁𝗼 𝗮𝗰𝗰𝗲𝗽𝘁 𝗼𝗻 ✅\n"
    f"➻ /acceptall 𝗼𝗳𝗳 — 𝗮𝘂𝘁𝗼 𝗮𝗰𝗰𝗲𝗽𝘁 𝗼𝗳𝗳 ❌\n"
    f"➻ /notification 𝗼𝗻 — 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀 𝗼𝗻 🔔\n"
    f"➻ /notification 𝗼𝗳𝗳 — 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀 𝗼𝗳𝗳 🔕\n\n"

    f"❖ 𝗪𝗛𝗘𝗡 𝗢𝗙𝗙 ❖\n"

    f"➻ 𝗯𝗼𝘁 𝘀𝗲𝗻𝗱𝘀 𝗮 𝗷𝗼𝗶𝗻 𝗿𝗲𝗾𝘂𝗲𝘀𝘁\n"
    f"➻ 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝘁𝗼 𝘁𝗵𝗲 𝗴𝗿𝗼𝘂𝗽\n"
    f"➻ 𝘄𝗶𝘁𝗵 𝗮𝗽𝗽𝗿𝗼𝘃𝗲 / 𝗱𝗲𝗰𝗹𝗶𝗻𝗲\n"
    f"➻ 𝗯𝘂𝘁𝘁𝗼𝗻𝘀 𝗳𝗼𝗿 𝗮𝗱𝗺𝗶𝗻𝘀\n\n"

    f"❖ 𝗡𝗢𝗧𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 𝗦𝗬𝗦𝗧𝗘𝗠 ❖\n"

    f"➻ 𝗶𝗳 𝗻𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗶𝘀 𝗼𝗳𝗳\n"
    f"➻ 𝗻𝗼 𝗷𝗼𝗶𝗻 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
    f"➻ 𝘄𝗶𝗹𝗹 𝗯𝗲 𝘀𝗲𝗻𝘁 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽\n\n"

    f"❖ 𝗡𝗢𝗧𝗘 ❖\n"

    f"➻ 𝗯𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗱𝗺𝗶𝗻\n"
    f"➻ 𝘄𝗶𝘁𝗵 𝗮𝗽𝗽𝗿𝗼𝘃𝗮𝗹 𝗿𝗶𝗴𝗵𝘁𝘀\n"
    f"➻ 𝗼𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘂𝘀𝗲\n"
    f"➻ 𝘁𝗵𝗲𝘀𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀"

)


# ============================================================
# Register Handlers
# ============================================================

def register_joinrequest_handler(app: Client):

    # ========================================================
    # /acceptall
    # ========================================================

    @app.on_message(filters.group & filters.command("acceptall"))
    async def acceptall_cmd(client: Client, message: Message):

        if not message.from_user:
            return

        if not await is_admin(
            client,
            message.chat.id,
            message.from_user.id
        ):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
            )

        if not await bot_can_manage_requests(
            client,
            message.chat.id
        ):
            return await message.reply_text(
                "❌ ɪ ɴᴇᴇᴅ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ ᴀᴘᴘʀᴏᴠᴀʟ ᴘᴇʀᴍɪꜱꜱɪᴏɴ."
            )

        parts = message.text.split(maxsplit=1)

        if len(parts) < 2 or parts[1].lower() not in ("on", "off"):

            current_status = await db.get_acceptall_status(
                message.chat.id
            )

            return await message.reply_text(
                (
                    "⚙️ 𝗔𝘂𝘁𝗼 𝗔𝗰𝗰𝗲𝗽𝘁 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀\n\n"
                    "𝗨𝘀𝗮𝗴𝗲:\n"
                    "<code>/acceptall ᴏɴ</code>\n"
                    "<code>/acceptall ᴏꜰꜰ</code>\n\n"
                    f"𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗦𝘁𝗮𝘁𝘂𝘀: "
                    f"{'🟢 ᴇɴᴀʙʟᴇᴅ' if current_status else '🔴 ᴅɪꜱᴀʙʟᴇᴅ'}"
                ),
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"

        await db.set_acceptall_status(
            message.chat.id,
            status
        )

        if status:

            text = (
                "✅ 𝗔𝘂𝘁𝗼 𝗔𝗰𝗰𝗲𝗽𝘁 𝗘𝗻𝗮𝗯𝗹𝗲𝗱\n\n"
                "ᴀʟʟ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛꜱ ᴡɪʟʟ ɴᴏᴡ ʙᴇ ᴀᴘᴘʀᴏᴠᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ."
            )

        else:

            text = (
                "⚠️ 𝗔𝘂𝘁𝗼 𝗔𝗰𝗰𝗲𝗽𝘁 𝗗𝗶𝘀𝗮𝗯𝗹𝗲𝗱\n\n"
                "ᴀᴅᴍɪɴꜱ ᴡɪʟʟ ɴᴏᴡ ᴍᴀɴᴜᴀʟʟʏ ᴀᴘᴘʀᴏᴠᴇ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛꜱ."
            )

        await message.reply_text(
            text,
            parse_mode=enums.ParseMode.HTML
        )

    # ========================================================
    # /notification
    # ========================================================

    @app.on_message(filters.group & filters.command("notification"))
    async def notification_cmd(
        client: Client,
        message: Message
    ):

        if not message.from_user:
            return

        if not await is_admin(
            client,
            message.chat.id,
            message.from_user.id
        ):
            return await message.reply_text(
                "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
            )

        parts = message.text.split(maxsplit=1)

        if len(parts) < 2 or parts[1].lower() not in ("on", "off"):

            current = await db.get_jr_notification_status(
                message.chat.id
            )

            return await message.reply_text(
                (
                    "🔔 𝗝𝗼𝗶𝗻 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗡𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀\n\n"
                    "𝗨𝘀𝗮𝗴𝗲:\n"
                    "<code>/notification ᴏɴ</code>\n"
                    "<code>/notification ᴏꜰꜰ</code>\n\n"
                    f"𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗦𝘁𝗮𝘁𝘂𝘀: "
                    f"{'🟢 ᴇɴᴀʙʟᴇᴅ' if current else '🔴 ᴅɪꜱᴀʙʟᴇᴅ'}"
                ),
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"

        await db.set_jr_notification_status(
            message.chat.id,
            status
        )

        if status:

            text = (
                "🔔 𝗝𝗼𝗶𝗻 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗡𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀 𝗘𝗻𝗮𝗯𝗹𝗲𝗱\n\n"
                "ᴀᴅᴍɪɴꜱ ᴡɪʟʟ ɴᴏᴡ ʀᴇᴄᴇɪᴠᴇ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ ᴀʟᴇʀᴛꜱ."
            )

        else:

            text = (
                "🔕 𝗝𝗼𝗶𝗻 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗡𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀 𝗗𝗶𝘀𝗮𝗯𝗹𝗲𝗱\n\n"
                "ɴᴏ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ ᴀʟᴇʀᴛꜱ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ."
            )

        await message.reply_text(
            text,
            parse_mode=enums.ParseMode.HTML
        )

    # ========================================================
    # Handle Join Request
    # ========================================================

    @app.on_chat_join_request()
    async def handle_join_request(
        client: Client,
        request: ChatJoinRequest
    ):

        try:

            chat_id = request.chat.id
            user = request.from_user

            auto_accept = await db.get_acceptall_status(
                chat_id
            )

            # =================================================
            # AUTO APPROVE
            # =================================================

            if auto_accept:

                try:

                    await client.approve_chat_join_request(
                        chat_id,
                        user.id
                    )

                    logger.info(
                        f"ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀ {user.id} ɪɴ {chat_id}"
                    )

                except Exception as e:
                    logger.error(f"ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ꜰᴀɪʟᴇᴅ: {e}")

                return

            # =================================================
            # NOTIFICATION CHECK
            # =================================================

            notification_enabled = (
                await db.get_jr_notification_status(
                    chat_id
                )
            )

            # If notification disabled
            # silently ignore request

            if not notification_enabled:
                return

            # =================================================
            # MANUAL APPROVE SYSTEM
            # =================================================

            username = (
                f"@{user.username}"
                if user.username
                else "N/A"
            )

            name = (
                user.first_name
                + (
                    f" {user.last_name}"
                    if user.last_name
                    else ""
                )
            )

            text = (
                f"ɴᴇᴡ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ\n"
                f"❍ ᴜꜱᴇʀ ɪɴꜰᴏ\n\n"
                f":⧽ ɴᴀᴍᴇ: {name}\n"
                f":⧽ ᴜꜱᴇʀ: <code>{username}</code>\n"
                f":⧽ ɪᴅ: <code>{user.id}</code>"
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "ᴀᴘᴘʀᴏᴠᴇ",
                        callback_data=(
                            f"jr_approve:{chat_id}:{user.id}"
                        )
                    ),
                    InlineKeyboardButton(
                        "ᴅᴇᴄʟɪɴᴇ",
                        callback_data=(
                            f"jr_decline:{chat_id}:{user.id}"
                        )
                    ),
                ]
            ])

            await client.send_message(
                chat_id,
                text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            logger.error(f"ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ ʜᴀɴᴅʟᴇʀ ᴇʀʀᴏʀ: {e}")

    # ========================================================
    # APPROVE CALLBACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(r"^jr_approve:(-?\d+):(\d+)$")
    )
    async def approve_callback(
        client: Client,
        callback_query: CallbackQuery
    ):

        try:

            if not callback_query.from_user:
                return

            match = callback_query.matches[0]

            chat_id = int(match.group(1))
            user_id = int(match.group(2))

            if not await is_admin(
                client,
                chat_id,
                callback_query.from_user.id
            ):
                return await callback_query.answer(
                    "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ.",
                    show_alert=True
                )

            try:

                await client.approve_chat_join_request(
                    chat_id,
                    user_id
                )

            except Exception:
                return await callback_query.answer(
                    "⚠️ ʀᴇǫᴜᴇꜱᴛ ᴀʟʀᴇᴀᴅʏ ʜᴀɴᴅʟᴇᴅ.",
                    show_alert=True
                )

            user = await client.get_users(user_id)

            await callback_query.message.edit_text(
                f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱!\n\n"
                f":⧽ ɴᴀᴍᴇ: {user.first_name}\n"
                f":⧽ ɪᴅ: <code>{user_id}</code>\n\n"
                f"<i>ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ : {callback_query.from_user.mention}</i>",
                parse_mode=enums.ParseMode.HTML
            )

            await callback_query.answer(
                "✅ ᴜꜱᴇʀ ᴀᴘᴘʀᴏᴠᴇᴅ!"
            )

            # Auto delete after 15 sec

            await asyncio.sleep(15)

            try:
                await callback_query.message.delete()
            except:
                pass

        except Exception as e:
            logger.error(f"ᴀᴘᴘʀᴏᴠᴇ ᴄᴀʟʟʙᴀᴄᴋ ᴇʀʀᴏʀ: {e}")

    # ========================================================
    # DECLINE CALLBACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(r"^jr_decline:(-?\d+):(\d+)$")
    )
    async def decline_callback(
        client: Client,
        callback_query: CallbackQuery
    ):

        try:

            if not callback_query.from_user:
                return

            match = callback_query.matches[0]

            chat_id = int(match.group(1))
            user_id = int(match.group(2))

            if not await is_admin(
                client,
                chat_id,
                callback_query.from_user.id
            ):
                return await callback_query.answer(
                    "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴅᴇᴄʟɪɴᴇ.",
                    show_alert=True
                )

            try:

                await client.decline_chat_join_request(
                    chat_id,
                    user_id
                )

            except Exception:
                return await callback_query.answer(
                    "⚠️ ʀᴇǫᴜᴇꜱᴛ ᴀʟʀᴇᴀᴅʏ ʜᴀɴᴅʟᴇᴅ.",
                    show_alert=True
                )

            user = await client.get_users(user_id)

            await callback_query.message.edit_text(
                f"❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱!\n\n"
                f":⧽ ɴᴀᴍᴇ: {user.first_name}\n"
                f":⧽ ɪᴅ: <code>{user_id}</code>\n\n"
                f"<i>ᴅᴇᴄʟɪɴᴇᴅ ʙʏ {callback_query.from_user.mention}</i>",
                parse_mode=enums.ParseMode.HTML
            )

            await callback_query.answer(
                "❌ ᴜꜱᴇʀ ᴅᴇᴄʟɪɴᴇᴅ."
            )

            # Auto delete after 15 sec

            await asyncio.sleep(15)

            try:
                await callback_query.message.delete()
            except:
                pass

        except Exception as e:
            logger.error(f"ᴅᴇᴄʟɪɴᴇ ᴄᴀʟʟʙᴀᴄᴋ ᴇʀʀᴏʀ: {e}")
