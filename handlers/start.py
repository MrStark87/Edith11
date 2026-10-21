# ============================================================
# Group Manager Bot
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID, PRIVACY_IMAGE
import db


def register_handlers(app: Client):

    # ==========================================================
    # Start Message helper
    # ==========================================================
    async def send_start_menu(message, user):
        text = (
            f"<blockquote expandable><b>✨ 𝖧𝖾𝗅𝗅𝗈 {user} </b></blockquote>/n"
            f"<b>❍</b> 𝖨'𝗆 <a href='https://t.me/EdithHelpsBot'>𝖤𝖽𝗂𝗍𝗁 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝖡𝗈𝗍 🤖</a> 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝖺𝖽𝗏𝖺𝗇𝖼𝖾𝖽 𝗌𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝖺𝗇𝖽 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖻𝗈𝗍./n/n"
            f"<b>➣ <u>𝖨 𝖼𝖺𝗇 𝗁𝖾𝗅𝗉 𝗒𝗈𝗎 𝗐𝗂𝗍𝗁:</u></b>/n"
            f"<blockquote expandable><b>⦸ 𝖠𝗇𝗍𝗂 𝖠𝖻𝗎𝗌𝖾 & 𝖠𝗇𝗍𝗂 𝖱𝖺𝗂𝖽.</b>/n/n"
            f"<b>♧ 𝖡𝗂𝗈𝗅𝗂𝗇𝗄 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇 & 𝖫𝗂𝗇𝗄 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇.</b>/n/n"
            f"<b>♙ 𝖦𝗋𝗈𝗎𝗉 𝖫𝗈𝖼𝗄, 𝖡𝗎𝗅𝗄 𝖯𝗎𝗋𝗀𝗂𝗇𝗀, 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖣𝖾𝗅𝖾𝗍𝖾</b></blockquote>/n"
            f"<b>⇩</b> 𝖭𝖾𝖾𝖽 𝖧𝖾𝗅𝗉? 𝖴𝗌𝖾 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗈𝗋 𝗌𝖾𝗇𝖽 /help"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✙ 𝖠𝖽𝖽 𝖬𝖾 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true", style=ButtonStyle.PRIMARY)],
            [
                InlineKeyboardButton("⌯ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 ⌯", url=SUPPORT_GROUP, style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("⌯ 𝖴𝗉𝖽𝖺𝗍𝖾 ⌯", url=UPDATE_CHANNEL, style=ButtonStyle.SUCCESS),
            ],
            [InlineKeyboardButton("⌯ 𝖧𝖾𝗅𝗉𝗌 𝖺𝗇𝖽 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 ⌯", callback_data="help", style=ButtonStyle.PRIMARY)]
        ])

        if message.text:
            await message.reply_photo(
                START_IMAGE,
                caption=text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            media = InputMediaPhoto(
                media=START_IMAGE,
                caption=text,
                parse_mode=enums.ParseMode.HTML
            )
            await message.edit_media(media=media, reply_markup=buttons)


    # ==========================================================
    # /start — handles all deep link payloads + default menu
    # ==========================================================
    @app.on_message(filters.private & filters.command("start"))
    async def start_command(client, message):
        args    = message.text.split(maxsplit=1)
        payload = args[1].strip() if len(args) > 1 else ""

        # ── Welcome setup deep link ──────────────────────────
        if payload.startswith("wsetup_"):
            try:
                chat_id = int(payload[len("wsetup_"):])
            except ValueError:
                return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ꜱᴇᴛᴜᴘ ʟɪɴᴋ.")
            from pyrogram.enums import ChatMemberStatus as CMS
            try:
                member = await client.get_chat_member(chat_id, message.from_user.id)
                if member.status not in [CMS.ADMINISTRATOR, CMS.OWNER]:
                    return await message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ɢʀᴏᴜᴘ.")
                chat = await client.get_chat(chat_id)
            except Exception as e:
                return await message.reply_text(f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴠᴇʀɪꜰʏ ᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ: {e}")
            from handlers.welcome import _sessions, _send_panel
            data = await db.get_welcome_v2(chat_id) or {}
            _sessions[message.from_user.id] = {
                "chat_id":       chat_id,
                "chat_title":    chat.title or str(chat_id),
                "step":          "main",
                "text":          data.get("text"),
                "media_file_id": data.get("media_file_id"),
                "media_type":    data.get("media_type"),
                "buttons":       list(data.get("buttons") or []),
            }
            return await _send_panel(client, message.chat.id, message.from_user.id)

        # ── Note deep link ───────────────────────────────────
        if payload.startswith("note_"):
            try:
                _, chat_id_str, name = payload.split("_", 2)
                chat_id = int(chat_id_str)
            except (ValueError, IndexError):
                return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɴᴏᴛᴇ ʟɪɴᴋ.")
            from handlers.notes import _send_note
            note_data = await db.get_note(chat_id, name)
            if not note_data:
                return await message.reply_text(
                    f"⚠️ ɴᴏᴛᴇ <code>#{name}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ.",
                    parse_mode=enums.ParseMode.HTML
                )
            await message.reply_text(
                f"📝 𝗡𝗼𝘁𝗲: #{name}",
                parse_mode=enums.ParseMode.HTML
            )
            return await _send_note(client, message.chat.id, note_data)

        # ── Default: show start menu ─────────────────────────
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        await send_start_menu(message, user.first_name)


    # ==========================================================
    # /help — private mein direct help menu
    # ==========================================================
    @app.on_message(filters.private & filters.command("help"))
    async def help_command(client, message):
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        text, buttons = build_category_menu()
        await message.reply_photo(
            START_IMAGE,
            caption=text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # Group /help
    # ==========================================================
    @app.on_message(filters.group & filters.command("help"))
    async def group_start_command(client, message):
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("⌯ 𝖧𝖾𝗅𝗉𝗌 𝖺𝗇𝖽 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 ⌯", url=f"https://t.me/{BOT_USERNAME}?start=help", style=ButtonStyle.PRIMARY),
        ]])
        await message.reply_photo(
            START_IMAGE,
            caption=(
                "<emoji id=5231102735817918643>👇</emoji> <b> 𝖼𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝗆𝗒 𝗁𝖾𝗅𝗉 𝗆𝖾𝗇𝗎 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗉𝗆</b>.
                "
            ),
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            has_spoiler=True
        )
    
    
    # ==========================================================
    # Group /start
    # ==========================================================
    @app.on_message(filters.group & filters.command("start"))
    async def group_start_command(client, message):
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⌯ ꜱᴜᴘᴘᴏʀᴛ ⌯", url=SUPPORT_GROUP, style=ButtonStyle.SUCCESS),
        ]])
        await message.reply_photo(
            START_IMAGE,
            caption=(
                "<emoji id=5440431182602842059>👋</emoji> 𝗵𝗲𝘆! 𝗶'𝗺 𝗘𝗱𝗶𝘁𝗵\n"
                "❍ 𝘆𝗼𝘂𝗿 𝘀𝗺𝗮𝗿𝘁 𝗴𝗿𝗼𝘂𝗽 𝗺𝗮𝗻𝗮𝗴𝗲𝗿 𝗯𝗼𝘁.\n\n"
                "➻ 𝗮𝗱𝗱 𝗺𝗲 𝘁𝗼 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 & 𝗸𝗲𝗲𝗽 𝗶𝘁 𝘀𝗮𝗳𝗲 <emoji id=5017108172138087141>🛡️</emoji>"
            ),
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            has_spoiler=True
        )


    # ==========================================================
    # Group /privacy
    # ==========================================================
    @app.on_message(filters.private & filters.command("privacy"))
    async def group_start_command(client, message):
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("⌯ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ 🔏 ⌯", url=f"https://graph.org/Anya-Bots---Privacy-Policy-04-12", style=ButtonStyle.PRIMARY),
        ]])
        await message.reply_photo(
            PRIVACY_IMAGE,
            caption=(
                ' <emoji id=5956561916573782596>📄</emoji> 𝗣𝗿𝗶𝘃𝗮𝗰𝘆 𝗣𝗼𝗹𝗶𝗰𝘆 𝗳𝗼𝗿 - <a href="https://t.me/EdithHelpsBot">𝗘𝗗𝗜𝗧𝗛 !</a>'
                "\n"
                '𝗬𝗼𝘂𝗿 𝗽𝗿𝗶𝘃𝗮𝗰𝘆 𝗶𝘀 𝗶𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁 𝘁𝗼 𝘂𝘀. 𝗧𝗼 𝗹𝗲𝗮𝗿𝗻 𝗺𝗼𝗿𝗲 𝗮𝗯𝗼𝘂𝘁 𝗵𝗼𝘄 𝘄𝗲 𝗰𝗼𝗹𝗹𝗲𝗰𝘁, 𝘂𝘀𝗲, 𝗮𝗻𝗱 𝗽𝗿𝗼𝘁𝗲𝗰𝘁 𝘆𝗼𝘂𝗿 𝗱𝗮𝘁𝗮, 𝗽𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝘃𝗶𝗲𝘄 𝗼𝘂𝗿 <a href="https://graph.org/Anya-Bots---Privacy-Policy-04-12">𝗣𝗿𝗶𝘃𝗮𝗰𝘆 𝗣𝗼𝗹𝗶𝗰𝘆</a>.'
                "\n"
                '𝗜𝗳 𝘆𝗼𝘂 𝗵𝗮𝘃𝗲 𝗮𝗻𝘆 𝗾𝘂𝗲𝘀𝘁𝗶𝗼𝗻𝘀 𝗼𝗿 𝗰𝗼𝗻𝗰𝗲𝗿𝗻𝘀, 𝗳𝗲𝗲𝗹 𝗳𝗿𝗲𝗲 𝘁𝗼 𝗿𝗲𝗮𝗰𝗵 𝗼𝘂𝘁 𝘁𝗼 𝗼𝘂𝗿 <a href="https://t.me/CarelessxWorld">𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝘁𝗲𝗮𝗺</a>.'
            ),
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
        
    


    
    # ==========================================================
    # Track groups bot is added to (for /stats)
    # ==========================================================
    @app.on_message(filters.group & ~filters.service, group=10)
    async def track_group(client, message):
        if message.chat:
            try:
                await db.add_chat(message.chat.id, message.chat.title or "")
            except Exception:
                pass


    # ==========================================================
    # Help Menu — Paginated
    # ==========================================================

    CATEGORY_MODERATION = [
        ("🔮 ᴍᴏᴅʀᴀᴛɪᴏɴ ⌯",     "moderation"),
        ("⚠️ ᴡᴀʀɴꜱ ⌯",           "warns_help"),
        ("🚷 ʙʟ ᴜꜱᴇʀ ⌯",      "blackuser_help"),
        ("🚫 ʙʟ ᴡᴏʀᴅꜱ ⌯",      "blacklist_help"),
        ("🤬 ᴀʙᴜꜱᴇ ⌯",           "abuse_help"),
        ("🗑️ ᴄᴍᴅ ᴅᴇʟ ⌯",        "cmd_help"),
        ("🚮 ᴍᴇᴅɪᴀ ᴅᴇʟ ⌯",      "mediadelete_help"),
        ("🆘 ᴀᴅᴍɪɴ ⌯",           "admin_tag_help"),
        ("👮🏻 ᴘʀᴏᴍᴏᴛɪᴏɴ ⌯",     "promote_help"),
        ("⌛ ʟᴏɴɢ ʟɪᴍɪᴛ ⌯",     "longmsg_help"),
        ("#️⃣ ʜᴀꜱʜᴛᴀɢ ⌯",        "hashtag_help"),
    ]

    CATEGORY_SECURITY = [
        ("🔐 ʟᴏᴄᴋꜱ ⌯",          "locks"),
        ("🕐 ᴀᴜᴛᴏ ʟᴏᴄᴋ", "autolock_help"),
        ("🔡 ᴄᴀᴘᴛᴄʜᴀ ⌯",          "captcha_help"),
        ("〽️ ʙɪᴏ ʟɪɴᴋ ⌯",       "biolink"),
        ("🔗 ᴀɴᴛɪ ʟɪɴᴋ ⌯", "anti_link_help"),
        ("🪠 ꜰ-ꜱᴜʙ ⌯",           "fsub_help"),
        ("🧴 ᴄʟᴇᴀɴᴇʀ ⌯",         "cleaner_help"),
        ("📵 ᴘʜᴏɴᴇ ⌯",           "phone_help"),
        ("🎭 ᴀɴᴛɪ ꜱᴛɪᴄᴋᴇʀ ⌯",    "anti_sticker_help"),
        ("🧟 ᴢᴏᴍʙɪᴇꜱ ⌯",         "zombie_help"),
        ("👻 ɢʜᴏꜱᴛ ⌯",           "ghost_help"),
        ("🤿 ꜰɪʟᴛᴇʀꜱ ⌯",         "filters_help"),
        ("⛩️ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛ ⌯",  "joinrequest_help"),
        ("🛡️ ᴀɴᴛɪ ʀᴀɪᴅ ⌯",      "antiraid_help"),
        ("🌊 ᴀɴᴛɪ ꜰʟᴏᴏᴅ ⌯",      "antiflood_help"),
        ("⚙️ ᴅɪꜱᴀʙʟᴇ", "disable_help"),
        ("🪭 ꜰᴀɴᴄʏ ᴛᴇxᴛ ⌯",       "fancy_text_help"),
    ]

    CATEGORY_UTILITY = [
        ("💌 ɢʀᴇᴇᴛɪɴɢꜱ ⌯",    "greetings"),
        ("📝 ɴᴏᴛᴇꜱ ⌯",           "notes_help"),
        ("📑 ʀᴜʟᴇꜱ ⌯",           "rules_help"),
        ("⚙️ ᴜᴛɪʟɪᴛʏ ⌯",         "utility_help"),
        ("🔖 ᴛᴀɢ ᴀʟʟ ⌯",         "tagall_help"),
        ("🕊 ᴀᴘᴘʀᴏᴠᴇ", "approve_help"),
        ("📤 ꜰᴏʀᴡᴀʀᴅ ⌯",           "forward_help"),
        ("🤖 ᴇᴅɪᴛʜ ᴀɪ ⌯",        "ai_help"),
    ]

    CATEGORY_GROUPS = [
        ("👥 ɢʀᴏᴜᴘ ⌯", "groupinfo_help"),
        ("🔗 ɪɴᴠɪᴛᴇ ʟɪɴᴋ ⌯",    "linkinfo_help"),
    ]

    ECO_CATEGORIES = {
        "moderation": CATEGORY_MODERATION,
        "security": CATEGORY_SECURITY,
        "utility": CATEGORY_UTILITY,
        "groups": CATEGORY_GROUPS,
    }

    BUTTONS_PER_PAGE = 12


    def build_category_menu():
        text = (
            "❖ 𝗰𝗵𝗼𝗼𝘀𝗲 𝘁𝗵𝗲 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝘆 𝗳𝗼𝗿 𝘄𝗵𝗶𝗰𝗵 𝘆𝗼𝘂 𝘄𝗮𝗻𝗻𝗮 𝗴𝗲𝘁 𝗵𝗲𝗹𝗽\n\n"
            "➥ 𝗮𝘀𝗸 𝘆𝗼𝘂𝗿 𝗱𝗼𝘂𝗯𝘁𝘀 𝗮𝘁 <a href='https://t.me/CarelessxWorld'>𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝗰𝗵𝗮𝘁</a>\n"
            "𝗮𝗹𝗹 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗰𝗮𝗻 𝗯𝗲 𝘂𝘀𝗲𝗱 𝘄𝗶𝘁𝗵 :<code>/</code>"
        )
        rows = [
            [
                InlineKeyboardButton("🔮 ᴍᴏᴅᴇʀᴀᴛɪᴏɴ", callback_data="help_cat|moderation|0", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("🛡️ ꜱᴇᴄᴜʀɪᴛʏ", callback_data="help_cat|security|0", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("⚙️ ᴜᴛɪʟɪᴛʏ", callback_data="help_cat|utility|0", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("👥 ɢʀᴏᴜᴘꜱ", callback_data="help_cat|groups|0", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("💰 ᴇᴄᴏɴᴏᴍʏ", callback_data="eco_menu", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("🏠 ʙᴀᴄᴋ", callback_data="back_to_start", style=ButtonStyle.DANGER),
                InlineKeyboardButton("✖ ᴄʟᴏꜱᴇ", callback_data="help_close", style=ButtonStyle.DANGER),
            ],
        ]
        return text, InlineKeyboardMarkup(rows)


    def build_category_page(category: str, page: int):
        items = ECO_CATEGORIES.get(category, [])
        total_pages = max(1, (len(items) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE)
        start = page * BUTTONS_PER_PAGE
        page_buttons = items[start:start + BUTTONS_PER_PAGE]

        rows = []
        for i in range(0, len(page_buttons), 2):
            pair = page_buttons[i:i + 2]
            rows.append([
                InlineKeyboardButton(label, callback_data=f"{cb}|{category}|{page}", style=ButtonStyle.PRIMARY)
                for label, cb in pair
            ])

        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("« ᴘʀᴇᴠ", callback_data=f"help_cat|{category}|{page - 1}", style=ButtonStyle.SUCCESS))
        else:
            nav.append(InlineKeyboardButton("«", callback_data="noop", style=ButtonStyle.SUCCESS))

        nav.append(InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_categories", style=ButtonStyle.DANGER))

        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"help_cat|{category}|{page + 1}", style=ButtonStyle.SUCCESS))
        else:
            nav.append(InlineKeyboardButton("»", callback_data="noop", style=ButtonStyle.SUCCESS))

        rows.append(nav)

        text = (
            f"❖ {category.upper()} 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n\n"
            "➥ 𝗮𝘀𝗸 𝘆𝗼𝘂𝗿 𝗱𝗼𝘂𝗯𝘁𝘀 𝗮𝘁 <a href='https://t.me/CarelessxWorld'>𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝗰𝗵𝗮𝘁</a>"
        )
        return text, InlineKeyboardMarkup(rows)


    async def send_category_menu(message):
        text, buttons = build_category_menu()
        media = InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML)
        await message.edit_media(media=media, reply_markup=buttons)


    async def send_category_page(message, category, page=0):
        text, buttons = build_category_page(category, page)
        media = InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML)
        await message.edit_media(media=media, reply_markup=buttons)


    def make_back_btn(category: str, page: int):
        # "back" from any detail view returns just one step back — to that category's page
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"help_cat|{category}|{page}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="back_to_start", style=ButtonStyle.DANGER),
        ]])


    # ==========================================================
    # Core navigation callbacks
    # ==========================================================

    @app.on_callback_query(filters.regex(r"^back_to_help_(\d+)$"))
    async def back_to_help_callback(client, callback_query):
        await send_category_menu(callback_query.message)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client, callback_query):
        await send_category_menu(callback_query.message)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^help_categories$"))
    async def help_categories_callback(client, callback_query):
        await send_category_menu(callback_query.message)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^help_cat\|(\w+)\|(\d+)$"))
    async def help_cat_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        await send_category_page(callback_query.message, category, page)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^help_close$"))
    async def help_close_callback(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^noop$"))
    async def noop_callback(client, callback_query):
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^back_to_start$"))
    async def back_to_start_callback(client, callback_query):
        user = callback_query.from_user.first_name
        await send_start_menu(callback_query.message, user)
        await callback_query.answer()


    # ==========================================================
    # Help page callbacks — each with unique function name
    # ==========================================================


        @app.on_callback_query(filters.regex(r"^join_help\|(\d+)$"))
        async def echo_help_callback(client, callback_query):
            page = int(callback_query.matches[0].group(1))
            text = (
                f"╔══════════════════╗\n"
                f"  🎀 𝗷𝗼𝗶𝗻/leave 𝗱𝗲𝗹𝗲𝘁𝗲𝗿\n"
                f"╚══════════════════╝\n\n"
                f"➻ /cleanservice 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗳𝗼𝗿 𝗷𝗼𝗶𝗻/leave 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
                f"➻ /cleanservice 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗳𝗼𝗿 𝗷𝗼𝗶𝗻/leave 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
            )
            await callback_query.message.edit_media(
                InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
                reply_markup=make_back_btn("utility", page)
            )
            await callback_query.answer()





    
    @app.on_callback_query(filters.regex(r"^groupinfo_help\|(\w+)\|(\d+)$"))
    async def groupinfo_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.groupinfo import GROUPS_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=GROUPS_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^linkinfo_help\|(\w+)\|(\d+)$"))
    async def linkinfo_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.groupinfo import LINK_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=LINK_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^greetings\|(\w+)\|(\d+)$"))
    async def greetings_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.welcome import WELCOME_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=WELCOME_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^locks\|(\w+)\|(\d+)$"))
    async def locks_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f". ⚙ 𝗹𝗼𝗰𝗸𝘀 𝘀𝘆𝘀𝘁𝗲𝗺\n"
            f"╚══════════════════╝\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /lock — 𝗲𝗻𝗮𝗯𝗹𝗲 𝗮 𝗹𝗼𝗰𝗸\n"
            f"➻ /unlock  — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗮 𝗹𝗼𝗰𝗸\n"
            f"➻ /locks — 𝘀𝗵𝗼𝘄 𝗮𝗰𝘁𝗶𝘃𝗲 𝗹𝗼𝗰𝗸𝘀\n"
            f"➻ /lockall — 𝗹𝗼𝗰𝗸 𝗲𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴 🔐\n"
            f"➻ /unlockall — 𝘂𝗻𝗹𝗼𝗰𝗸 𝗲𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴 🔓\n\n"
            f"❖ 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝘁𝘆𝗽𝗲𝘀 ❖\n"
            f"<code>𝘂𝗿𝗹</code> • <code>𝘁𝗲𝘅𝘁</code> • <code>𝘀𝘁𝗶𝗰𝗸𝗲𝗿</code> • <code>𝗺𝗲𝗱𝗶𝗮</code> • <code>𝗺𝘂𝘀𝗶𝗰</code>\n"
            f"<code>𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲</code> • <code>𝗳𝗼𝗿𝘄𝗮𝗿𝗱</code> • <code>𝗲𝗱𝗶𝘁</code> • <code>𝗳𝗶𝗹𝗲𝘀</code> • <code>ᴇᴍᴏᴊɪ</code>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^moderation\|(\w+)\|(\d+)$"))
    async def moderation_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  ⚙️ 𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗶𝗼𝗻\n"
            f"╚══════════════════╝\n\n"
            f"➻ /kick — 𝗿𝗲𝗺𝗼𝘃𝗲 𝗮 𝘂𝘀𝗲𝗿\n"
            f"➻ /ban — 𝗯𝗮𝗻 𝗽𝗲𝗿𝗺𝗮𝗻𝗲𝗻𝘁𝗹𝘆\n"
            f"➻ /unban — 𝗹𝗶𝗳𝘁 𝗯𝗮𝗻\n"
            f"➻ /mute — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
            f"➻ /unmute — 𝗮𝗹𝗹𝗼𝘄 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗴𝗮𝗶𝗻\n"
            f"➻ /tmute <time> — 𝘁𝗲𝗺𝗽 𝗺𝘂𝘁𝗲 (1𝗺–24𝗵)\n"
            f"➻ /tban <time> — 𝘁𝗲𝗺𝗽 𝗯𝗮𝗻 (1𝗺–24𝗵)\n"
            f"➻ /dkick — 𝗸𝗶𝗰𝗸 𝗯𝘆 𝗿𝗲𝗽𝗹𝘆 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /skick — 𝘀𝗶𝗹𝗲𝗻𝘁 𝗸𝗶𝗰𝗸 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝗰𝗺𝗱\n"
            f"➻ /dmute — 𝗺𝘂𝘁𝗲 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /dban — 𝗯𝗮𝗻 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /dwarn — 𝘄𝗮𝗿𝗻 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^warns_help\|(\w+)\|(\d+)$"))
    async def warns_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"   ⚠️ 𝘄𝗮𝗿𝗻 𝘀𝘆𝘀𝘁𝗲𝗺\n"
            f"╚══════════════════╝\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /warn [𝗿𝗲𝗮𝘀𝗼𝗻] — 𝘄𝗮𝗿𝗻 𝗮 𝘂𝘀𝗲𝗿\n"
            f"➻ /dwarn — 𝘄𝗮𝗿𝗻 + 𝗱𝗲𝗹𝗲𝘁𝗲 𝘁𝗵𝗲𝗶𝗿 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /warns — 𝘃𝗶𝗲𝘄 𝘄𝗮𝗿𝗻 𝗵𝗶𝘀𝘁𝗼𝗿𝘆\n"
            f"➻ /unwarn — 𝗿𝗲𝗺𝗼𝘃𝗲 1 𝘄𝗮𝗿𝗻\n"
            f"➻ /resetwarns — 𝗰𝗹𝗲𝗮𝗿 𝗮𝗹𝗹 𝘄𝗮𝗿𝗻𝘀\n"
            f"➻ /setwarnlimit [ 1-10 ]— 𝘀𝗲𝘁 𝘄𝗮𝗿𝗻 𝗹𝗶𝗺𝗶𝘁\n"
            f"➻ /setwarnaction 𝗺𝘂𝘁𝗲|𝗸𝗶𝗰𝗸|𝗯𝗮𝗻\n\n"
            f"❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
            f"➻ 𝗱𝗲𝗳𝗮𝘂𝗹𝘁 𝗹𝗶𝗺𝗶𝘁: 3 𝘄𝗮𝗿𝗻𝘀\n"
            f"➻ 𝗱𝗲𝗳𝗮𝘂𝗹𝘁 𝗮𝗰𝘁𝗶𝗼𝗻: 𝗺𝘂𝘁𝗲\n"
            f"➻ 𝘄𝗮𝗿𝗻𝘀 𝗿𝗲𝘀𝗲𝘁 𝗮𝗳𝘁𝗲𝗿 𝗮𝗰𝘁𝗶𝗼𝗻 𝘁𝗮𝗸𝗲𝗻\n"
            f"➻ 𝗹𝗮𝘀𝘁 5 𝗿𝗲𝗮𝘀𝗼𝗻𝘀 𝘀𝗵𝗼𝘄𝗻 𝗶𝗻 /warns"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^biolink\|(\w+)\|(\d+)$"))
    async def biolink_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  🔗 𝗯𝗶𝗼𝗹𝗶𝗻𝗸 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
            f"╚══════════════════╝\n\n"
            f"𝗯𝗹𝗼𝗰𝗸𝘀 𝘂𝘀𝗲𝗿𝘀 𝘄𝗵𝗼 𝗵𝗮𝘃𝗲 𝗹𝗶𝗻𝗸𝘀 𝗶𝗻 𝘁𝗵𝗲𝗶𝗿 𝗯𝗶𝗼.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /biolink 𝗼𝗻 — 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗼𝗻 ✅\n"
            f"➻ /biolink 𝗼𝗳𝗳 — 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗼𝗳𝗳 ❌\n"
            f"➻ /bioconfig — 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲 𝗮𝗰𝘁𝗶𝗼𝗻\n\n"
            f"❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
            f"➻ 𝗯𝗶𝗼 𝗹𝗶𝗻𝗸 𝗱𝗲𝘁𝗲𝗰𝘁𝗲𝗱 → 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱\n"
            f"➻ 𝗮𝗱𝗺𝗶𝗻𝘀 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗳𝗳𝗲𝗰𝘁𝗲𝗱\n"
            f"➻ 𝗯𝗼𝘁 𝗻𝗲𝗲𝗱𝘀 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^notes_help\|(\w+)\|(\d+)$"))
    async def notes_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.notes import NOTES_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=NOTES_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^rules_help\|(\w+)\|(\d+)$"))
    async def rules_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.rules import RULES_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=RULES_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^abuse_help\|(\w+)\|(\d+)$"))
    async def abuse_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  🤬 𝗮𝗯𝘂𝘀𝗲 𝗱𝗲𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
            f"╚══════════════════╝\n\n"
            f"𝗮𝗯𝘂𝘀𝗶𝘃𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /noabuse 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 ✅\n"
            f"➻ /noabuse 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 ❌\n\n"
            f"❖ 𝗻𝗼𝘁𝗲𝘀 ❖\n"
            f"➻ 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆\n"
            f"➻ 5 𝘀𝗲𝗰𝗼𝗻𝗱 𝘄𝗮𝗿𝗻𝗶𝗻𝗴 𝘀𝗲𝗻𝘁\n"
            f"➻ 𝗮𝗱𝗺𝗶𝗻𝘀 𝗻𝗼𝘁 𝗮𝗳𝗳𝗲𝗰𝘁𝗲𝗱"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^fsub_help\|(\w+)\|(\d+)$"))
    async def fsub_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f" 🔗 𝗳𝗼𝗿𝗰𝗲-𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲\n"
            f"╚══════════════════╝\n\n"
            f"𝘂𝘀𝗲𝗿𝘀 𝘄𝗵𝗼 𝗵𝗮𝘃𝗲𝗻'𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱\n"
            f"𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗰𝗮𝗻𝗻𝗼𝘁 𝘀𝗲𝗻𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /addfsub @𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗼𝗿 [-100𝘅𝘅𝘅𝘅]\n"
            f"➻ /removefsub @𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗼𝗿 [-100𝘅𝘅𝘅𝘅]\n"
            f"➻ /fsublist — 𝗹𝗶𝘀𝘁 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀\n\n"
            f"<i>𝗯𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗱𝗺𝗶𝗻 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^utility_help\|(\w+)\|(\d+)$"))
    async def utility_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"   ⚙️ 𝘂𝘁𝗶𝗹𝗶𝘁𝘆\n"
            f"╚══════════════════╝\n\n"
            f"➻ /chatinfo — 𝗴𝗿𝗼𝘂𝗽 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 &amp; 𝗺𝗲𝗺𝗯𝗲𝗿 𝗰𝗼𝘂𝗻𝘁\n"
            f"➻ /id — 𝘆𝗼𝘂𝗿 𝗶𝗱 𝗼𝗿 𝗿𝗲𝗽𝗹𝗶𝗲𝗱 𝘂𝘀𝗲𝗿'𝘀 𝗶𝗱\n"
            f"➻ /pin [𝘀𝗶𝗹𝗲𝗻𝘁] — 𝗽𝗶𝗻 𝗮 𝗿𝗲𝗽𝗹𝗶𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /unpin — 𝘂𝗻𝗽𝗶𝗻 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗼𝗿 𝗮𝗹𝗹 𝗽𝗶𝗻𝘀\n"
            f"➻ /purge — 𝗯𝘂𝗹𝗸 𝗱𝗲𝗹𝗲𝘁𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀\n"
            f"➻ /del — 𝗱𝗲𝗹𝗲𝘁𝗲 𝗮 𝗿𝗲𝗽𝗹𝗶𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"➻ /report — 𝗿𝗲𝗽𝗼𝗿𝘁 𝗮 𝘂𝘀𝗲𝗿 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻𝘀\n"
            f"➻ /calc &lt;𝗲𝘅𝗽𝗿&gt; — 𝗰𝗮𝗹𝗰𝘂𝗹𝗮𝘁𝗼𝗿\n\n"
            f"<i>𝗽𝗶𝗻, 𝗽𝘂𝗿𝗴𝗲, 𝗱𝗲𝗹 — 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^cleaner_help\|(\w+)\|(\d+)$"))
    async def cleaner_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  🧹 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗰𝗹𝗲𝗮𝗻𝗲𝗿\n"
            f"╚══════════════════╝\n\n"
            f"𝗮𝗹𝗹 𝗿𝗲𝗴𝘂𝗹𝗮𝗿 𝘂𝘀𝗲𝗿 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗱𝗲𝗹𝗲𝘁𝗲𝗱\n"
            f"𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗮𝗳𝘁𝗲𝗿 𝗮 𝘀𝗲𝘁 𝗱𝗲𝗹𝗮𝘆.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /cleaner 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 ✅\n"
            f"➻ /cleaner 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 ❌\n"
            f"➻ /setcleandelay <time> — 𝘀𝗲𝘁 𝗱𝗲𝗹𝗮𝘆\n"
            f"➻ /cleanstatus — 𝘀𝗵𝗼𝘄 𝘀𝗲𝘁𝘁𝗶𝗻𝗴𝘀\n\n"
            f"➻ 𝗮𝗱𝗺𝗶𝗻 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗻𝗲𝘃𝗲𝗿 𝗱𝗲𝗹𝗲𝘁𝗲𝗱\n"
            f"➻ 𝗿𝗮𝗻𝗴𝗲: 1𝗺 𝘁𝗼 24𝗵 — 𝗱𝗲𝗳𝗮𝘂𝗹𝘁: 5𝗺"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^longmsg_help\|(\w+)\|(\d+)$"))
    async def longmsg_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"📄 𝗹𝗼𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
            f"╚══════════════════╝\n\n"
            f"𝗹𝗼𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝘂𝗽𝗹𝗼𝗮𝗱𝗲𝗱 𝘁𝗼 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗽𝗵\n"
            f"𝗮𝗻𝗱 𝘀𝗲𝗻𝘁 𝗮𝘀 𝗮 𝗹𝗶𝗻𝗸 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /setlongmode 𝗼𝗳𝗳 — 𝗻𝗼 𝗮𝗰𝘁𝗶𝗼𝗻\n"
            f"➻ /setlongmode 𝗺𝗮𝗻𝘂𝗮𝗹 — 𝗱𝗲𝗹𝗲𝘁𝗲 + 𝘄𝗮𝗿𝗻\n"
            f"➻ /setlongmode 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰 — 𝗱𝗲𝗹𝗲𝘁𝗲 + 𝗹𝗶𝗻𝗸 ✅\n"
            f"➻ /setlonglimit <200–4000> — 𝘀𝗲𝘁 𝗹𝗶𝗺𝗶𝘁\n\n"
            f"<i>𝗱𝗲𝗳𝗮𝘂𝗹𝘁 𝗹𝗶𝗺𝗶𝘁: 800 𝗰𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿𝘀</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^hashtag_help\|(\w+)\|(\d+)$"))
    async def hashtag_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  # 𝗵𝗮𝘀𝗵𝘁𝗮𝗴 𝗳𝗶𝗹𝘁𝗲𝗿\n"
            f"╚══════════════════╝\n\n"
            f"𝗵𝗮𝘀𝗵𝘁𝗮𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗮𝗿𝗲 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.\n\n"
            f"❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
            f"➻ /nohashtags 𝗼𝗻 — 𝗯𝗹𝗼𝗰𝗸 ✅\n"
            f"➻ /nohashtags 𝗼𝗳𝗳 — 𝗮𝗹𝗹𝗼𝘄 ❌\n\n"
            f"➻ 𝗮𝗻𝘆 𝘄𝗼𝗿𝗱 𝘀𝘁𝗮𝗿𝘁𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 #"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^echo_help\|(\d+)$"))
    async def echo_help_callback(client, callback_query):
        page = int(callback_query.matches[0].group(1))
        text = (
            f"╔══════════════════╗\n"
            f"  🚧 𝗲𝗰𝗵𝗼\n"
            f"╚══════════════════╝\n\n"
            f"➻ /echo <text> — 𝗲𝗰𝗵𝗼 𝘁𝗲𝘅𝘁 𝗮𝘀 𝗯𝗼𝘁"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn("utility", page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^cmd_help\|(\w+)\|(\d+)$"))
    async def cmd_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  🗑️ 𝗰𝗺𝗱 𝗱𝗲𝗹𝗲𝘁𝗲𝗿\n"
            f"╚══════════════════╝\n\n"
            f"𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 <code>/</code> <code>!</code> <code>.</code> 𝗮𝘂𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲𝗱.\n\n"
            f"➻ /cmd 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 ✅\n"
            f"➻ /cmd 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 ❌\n\n"
            f"<i>𝗮𝗱𝗺𝗶𝗻𝘀 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗳𝗳𝗲𝗰𝘁𝗲𝗱.</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^mediadelete_help\|(\w+)\|(\d+)$"))
    async def mediadelete_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  🎬 𝗺𝗲𝗱𝗶𝗮 𝗮𝘂𝘁𝗼-𝗱𝗲𝗹𝗲𝘁𝗲\n"
            f"╚══════════════════╝\n\n"
            f"➻ /mediadelete 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 ✅\n"
            f"➻ /mediadelete 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 ❌\n"
            f"➻ /setmediadelay <time> — 𝘀𝗲𝘁 𝗱𝗲𝗹𝗮𝘆\n\n"
            f"➻ 𝗽𝗵𝗼𝘁𝗼𝘀, 𝘃𝗶𝗱𝗲𝗼𝘀, 𝘀𝘁𝗶𝗰𝗸𝗲𝗿𝘀, 𝗴𝗶𝗳𝘀\n"
            f"<i>𝗿𝗮𝗻𝗴𝗲: 1𝗺 𝘁𝗼 24𝗵 — 𝗱𝗲𝗳𝗮𝘂𝗹𝘁: 5𝗺</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^phone_help\|(\w+)\|(\d+)$"))
    async def phone_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text = (
            f"╔══════════════════╗\n"
            f"  📵 𝗽𝗵𝗼𝗻𝗲 𝗽𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻\n"
            f"╚══════════════════╝\n\n"
            f"➻ /nophone 𝗼𝗻 — 𝗯𝗹𝗼𝗰𝗸 ✅\n"
            f"➻ /nophone 𝗼𝗳𝗳 — 𝗮𝗹𝗹𝗼𝘄 ❌\n\n"
            f"➻ +91 9876543210\n"
            f"➻ +1-234-567-8900"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^zombie_help\|(\w+)\|(\d+)$"))
    async def zombie_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.zombie import ZOMBIE_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ZOMBIE_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^tagall_help\|(\w+)\|(\d+)$"))
    async def tagall_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.tagall import TAGALL_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=TAGALL_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^ghost_help\|(\w+)\|(\d+)$"))
    async def ghost_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.ghost import GHOST_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=GHOST_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^blacklist_help\|(\w+)\|(\d+)$"))
    async def blacklist_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.blacklist import BLACKLIST_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=BLACKLIST_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^filters_help\|(\w+)\|(\d+)$"))
    async def filters_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.filters import FILTERS_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=FILTERS_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^joinrequest_help\|(\w+)\|(\d+)$"))
    async def joinrequest_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.joinrequest import JOINREQUEST_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=JOINREQUEST_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^antiraid_help\|(\w+)\|(\d+)$"))
    async def antiraid_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.antiraid import ANTIRAID_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ANTIRAID_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^antiflood_help\|(\w+)\|(\d+)$"))
    async def antiflood_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.antiflood import ANTIFLOOD_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ANTIFLOOD_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^ai_help\|(\w+)\|(\d+)$"))
    async def ai_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.edith_ai import AI_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=AI_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^blackuser_help\|(\w+)\|(\d+)$"))
    async def blackuser_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.blackuser import BLACKUSER_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=BLACKUSER_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^admin_tag_help\|(\w+)\|(\d+)$"))
    async def admin_tag_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.admin_tag import ADMIN_TAG_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ADMIN_TAG_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^promote_help\|(\w+)\|(\d+)$"))
    async def promote_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.promote import PROMOTE_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=PROMOTE_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()


    @app.on_callback_query(filters.regex(r"^anti_sticker_help\|(\w+)\|(\d+)$"))
    async def anti_sticker_help_cb(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.anti_sticker import ANTI_STICKER_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ANTI_STICKER_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^captcha_help\|(\w+)\|(\d+)$"))
    async def captcha_help_cb(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.captcha import CAPTCHA_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=CAPTCHA_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^forward_help\|(\w+)\|(\d+)$"))
    async def forward_help_cb(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.forward import FORWARD_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=FORWARD_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^fancy_text_help\|(\w+)\|(\d+)$"))
    async def fancy_text_help_cb(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.fancy_text import FANCY_TEXT_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=FANCY_TEXT_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()


    @app.on_callback_query(filters.regex(r"^anti_link_help\|(\w+)\|(\d+)$"))
    async def anti_link_help_cb(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.anti_link import ANTI_LINK_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=ANTI_LINK_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^autolock_help\|(\w+)\|(\d+)$"))
    async def autolock_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.autolock import AUTOLOCK_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=AUTOLOCK_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()
        
    @app.on_callback_query(filters.regex(r"^disable_help\|(\w+)\|(\d+)$"))
    async def disable_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.disable import DISABLE_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=DISABLE_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^approve_help\|(\w+)\|(\d+)$"))
    async def approve_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        from handlers.approve import APPROVE_HELP_TEXT
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=APPROVE_HELP_TEXT, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    # ==========================================================
    # Broadcast
    # ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_message(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        if not message.reply_to_message:
            return await message.reply_text(
                "⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪᴛ.\n\n"
                "• <code>/broadcast</code> — ꜰᴏʀᴡᴀʀᴅ (ᴡɪᴛʜ ᴛᴀɢ)\n"
                "• <code>/broadcast ᴄᴏᴘʏ</code> — ꜱᴇɴᴅ ᴀꜱ ᴄᴏᴘʏ (ɴᴏ ᴛᴀɢ)",
                parse_mode=enums.ParseMode.HTML
            )
        parts     = message.text.split(maxsplit=1)
        copy_mode = len(parts) > 1 and parts[1].strip().lower() == "copy"
        src       = message.reply_to_message
        users     = await db.get_all_users()
        chats     = await db.get_all_chats()
        all_targets = list(set(users + chats))
        total     = len(all_targets)
        status_msg = await message.reply_text(
            f"📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁𝗶𝗻𝗴...\nᴛᴀʀɢᴇᴛꜱ: {total}\nᴍᴏᴅᴇ: {'Copy' if copy_mode else 'Forward'}",
            parse_mode=enums.ParseMode.HTML
        )
        sent, failed = 0, 0
        for target_id in all_targets:
            try:
                if copy_mode:
                    await src.copy(target_id)
                else:
                    await src.forward(target_id)
                sent += 1
            except Exception:
                failed += 1
            if sent % 25 == 0:
                import asyncio as _aio
                await _aio.sleep(1)
        await status_msg.edit_text(
            f"✅ 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲!\n\n"
            f"📤 ꜱᴇɴᴛ: {sent}\n"
            f"❌ ꜰᴀɪʟᴇᴅ: {failed}\n"
            f"📊 ᴛᴏᴛᴀʟ: {total}",
            parse_mode=enums.ParseMode.HTML
        )


    # ==========================================================
    # Stats — owner only
    # ==========================================================
    @app.on_message((filters.private | filters.group) & filters.command("stats"))
    async def stats_command(client, message):
        if message.from_user.id != OWNER_ID:
            return
        users = await db.get_all_users()
        chats = await db.get_all_chats()
        await message.reply_text(
            f"📊 𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀\n\n"
            f"ᴄʜᴀᴛꜱ: {len(chats)}\n"
            f"ᴜꜱᴇʀꜱ: {len(users)}",
            parse_mode=enums.ParseMode.HTML
        )

    # ==========================================================
    # 💰 Economy — help submenu
    # ==========================================================
    ECO_HELP_TEXTS = {
        "eco_balance": (
            "💰 <b>ʙᴀʟᴀɴᴄᴇ</b>\n\n"
            "➻ <code>/bal</code> ᴏʀ <code>/balance</code> — ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ, ᴋɪʟʟꜱ &amp; ʀᴏʙꜱ\n"
            "ʀᴇᴘʟʏ ᴛᴏ ꜱᴏᴍᴇᴏɴᴇ ᴡɪᴛʜ ɪᴛ ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇɪʀ ʙᴀʟᴀɴᴄᴇ\n\n"
            "➻ <code>/profile</code> — ʏᴏᴜʀ ꜰᴜʟʟ ᴘʀᴏꜰɪʟᴇ: ID, ʙᴀʟᴀɴᴄᴇ, ᴘʀᴏᴛᴇᴄᴛɪᴏɴ, ɪɴᴠᴇɴᴛᴏʀʏ"
        ),
        "eco_earnings": (
            "💵 <b>ᴇᴀʀɴɪɴɢꜱ</b>\n\n"
            "➻ <code>/rob &lt;amount&gt;</code> — ʀᴏʙ ᴀ ʀᴇᴘʟɪᴇᴅ ᴜꜱᴇʀ\n"
            "➻ <code>/kill</code> ᴏʀ <code>/death</code> — ᴋɪʟʟ ᴀ ʀᴇᴘʟɪᴇᴅ ᴜꜱᴇʀ, ʟᴏᴏᴛ ᴛʜᴇɪʀ ʙᴀʟᴀɴᴄᴇ + ʙᴏɴᴜꜱ\n"
            "➻ <code>/revive</code> — ᴄᴏᴍᴇ ʙᴀᴄᴋ ꜰʀᴏᴍ ᴅᴇᴀᴛʜ (+$50)\n"
            "➻ <code>/daily</code> — ᴅᴀɪʟʏ ʙᴏɴᴜꜱ (24ʜ ᴄᴏᴏʟᴅᴏᴡɴ)\n"
            "➻ <code>/mine</code> — ᴍɪɴᴇ ʙᴏɴᴜꜱ (6ʜ ᴄᴏᴏʟᴅᴏᴡɴ)\n"
            "➻ <code>/protect &lt;days&gt;</code> — ʙᴜʏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ (ᴍᴀx 3 ᴅᴀʏꜱ)\n"
            "➻ <code>/give &lt;amount&gt;</code> — ꜱᴇɴᴅ ᴍᴏɴᴇʏ ᴛᴏ ᴀ ʀᴇᴘʟɪᴇᴅ ᴜꜱᴇʀ"
        ),
        "eco_shop": (
            "🛒 <b>ꜱʜᴏᴘ</b>\n\n"
            "➻ <code>/shop</code> — ʙʀᴏᴡꜱᴇ ᴡᴇᴀᴘᴏɴꜱ, ᴀꜱꜱᴇᴛꜱ &amp; ʟᴜxᴜʀʏ ɪᴛᴇᴍꜱ\n"
            "ᴡᴇᴀᴘᴏɴꜱ ᴇxᴘɪʀᴇ ᴀꜰᴛᴇʀ 24ʜ ᴀɴᴅ ʙᴏᴏꜱᴛ ʏᴏᴜʀ ᴋɪʟʟ ʟᴏᴏᴛ %.\n"
            "ᴀꜱꜱᴇᴛꜱ &amp; ʟᴜxᴜʀʏ ɪᴛᴇᴍꜱ ɴᴇᴠᴇʀ ᴇxᴘɪʀᴇ ᴀɴᴅ ᴄᴀɴ ʙᴇ ʟᴏᴏᴛᴇᴅ ᴏɴ ᴅᴇᴀᴛʜ."
        ),
        "eco_bank": (
            "🏦 <b>ʙᴀɴᴋ</b>\n\n"
            "➻ <code>/deposit &lt;amount&gt;</code> — ᴅᴇᴘᴏꜱɪᴛ (+1%/ᴅᴀʏ)\n"
            "➻ <code>/loan &lt;amount&gt;</code> — ᴛᴀᴋᴇ ᴀ ʟᴏᴀɴ (ᴍᴀx $10,000, +2%/ᴅᴀʏ)\n"
            "➻ <code>/repay &lt;amount&gt;</code> — ʀᴇᴘᴀʏ ʏᴏᴜʀ ʟᴏᴀɴ\n"
            "➻ <code>/bank</code> — ᴠɪᴇᴡ ʏᴏᴜʀ ʙᴀɴᴋ ꜱᴛᴀᴛᴜꜱ"
        ),
        "eco_gift": (
            "🎁 <b>ɢɪꜰᴛ</b>\n\n"
            "➻ <code>/gift</code> (ʀᴇᴘʟʏ) — ꜱᴇɴᴅ ᴀɴ ɪᴛᴇᴍ ᴛᴏ ꜱᴏᴍᴇᴏɴᴇ (+$200 ɢɪꜰᴛ ᴄᴏꜱᴛ)\n"
            "ᴀꜰᴛᴇʀ ᴘɪᴄᴋɪɴɢ ᴀɴ ɪᴛᴇᴍ, ᴛʏᴘᴇ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ɪɴᴄʟᴜᴅᴇ — ᴛʜᴇʏ'ʟʟ ɢᴇᴛ ɪᴛ ɪɴ ᴘᴍ."
        ),
        "eco_fun": (
            "💞 <b>ꜰᴜɴ</b>\n\n"
            "➻ <code>/status</code> — ꜱɪɴɢʟᴇ ᴏʀ ᴍᴀʀʀɪᴇᴅ?\n"
            "➻ <code>/propose</code> ᴏʀ <code>/marry</code> (ʀᴇᴘʟʏ) — ᴘʀᴏᴘᴏꜱᴇ ᴛᴏ ꜱᴏᴍᴇᴏɴᴇ (-$500)\n"
            "➻ <code>/divorce</code> — ᴇɴᴅ ʏᴏᴜʀ ᴍᴀʀʀɪᴀɢᴇ (-$2,000)"
        ),
        "eco_leaderboard": (
            "🏆 <b>ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n\n"
            "➻ <code>/leaderboard</code> — ᴛᴏᴘ ʙᴀʟᴀɴᴄᴇꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ\n"
            "➻ <code>/overall</code> — ᴛᴏᴘ ʙᴀʟᴀɴᴄᴇꜱ ᴀᴄʀᴏꜱꜱ ᴀʟʟ ᴄʜᴀᴛꜱ"
        ),
    }

    def build_eco_menu():
        text = "💰 <b>ᴇᴄᴏɴᴏᴍʏ</b>\n\nᴄʜᴏᴏꜱᴇ ᴀ ꜱᴇᴄᴛɪᴏɴ:"
        rows = [
            [
                InlineKeyboardButton("💰 ʙᴀʟᴀɴᴄᴇ", callback_data="eco_balance", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("💵 ᴇᴀʀɴɪɴɢꜱ", callback_data="eco_earnings", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("🛒 ꜱʜᴏᴘ", callback_data="eco_shop", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("🏦 ʙᴀɴᴋ", callback_data="eco_bank", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("🎁 ɢɪꜰᴛ", callback_data="eco_gift", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("💞 ꜰᴜɴ", callback_data="eco_fun", style=ButtonStyle.PRIMARY),
            ],
            [InlineKeyboardButton("🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="eco_leaderboard", style=ButtonStyle.PRIMARY)],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_categories", style=ButtonStyle.DANGER),
                InlineKeyboardButton("✖ ᴄʟᴏꜱᴇ", callback_data="help_close", style=ButtonStyle.DANGER),
            ],
        ]
        return text, InlineKeyboardMarkup(rows)

    @app.on_callback_query(filters.regex("^eco_menu$"))
    async def eco_menu_cb(client, callback_query):
        text, buttons = build_eco_menu()
        media = InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^(eco_balance|eco_earnings|eco_shop|eco_bank|eco_gift|eco_fun|eco_leaderboard)$"))
    async def eco_section_cb(client, callback_query):
        key = callback_query.data
        text = ECO_HELP_TEXTS.get(key, "⚠️ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="eco_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("✖ ᴄʟᴏꜱᴇ", callback_data="help_close", style=ButtonStyle.DANGER),
        ]])
        media = InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()
