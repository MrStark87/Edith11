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
                "<emoji id=5231102735817918643>👇</emoji> <b> 𝖼𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝗆𝗒 𝗁𝖾𝗅𝗉 𝗆𝖾𝗇𝗎 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗉𝗆</b>."
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
                "<emoji id=5440431182602842059>👋</emoji> 𝖧𝖾𝗒! 𝖨'𝗆 𝖤𝖽𝗂𝗍𝗁 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝖡𝗈𝗍 🤖\\n"
                "❍ 𝖸𝗈𝗎𝗋 𝗌𝗆𝖺𝗋𝗍 𝗀𝗋𝗈𝗎𝗉 𝗆𝖺𝗇𝖺𝗀𝖾𝗋 𝖻𝗈𝗍.\\n\\n"
                "➻ 𝖠𝖽𝖽 𝗆𝖾 𝗍𝗈 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 & 𝗄𝖾𝖾𝗉 𝗂𝗍 𝗌𝖺𝖿𝖾. <emoji id=5017108172138087141>🛡️</emoji>"
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
                '<blockquote expandable> <emoji id=5956561916573782596>📄</emoji> 𝗣𝗿𝗶𝘃𝗮𝗰𝘆 𝗣𝗼𝗹𝗶𝗰𝘆 𝗳𝗼𝗿 - <a href="https://t.me/EdithHelpsBot">𝖤𝖽𝗂𝗍𝗁 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝖡𝗈𝗍 🤖</a></blockquote>'
                "\n"
                '𝖸𝗈𝗎𝗋 𝗉𝗋𝗂𝗏𝖺𝖼𝗒 𝗂𝗌 𝗂𝗆𝗉𝗈𝗋𝗍𝖺𝗇𝗍 𝗍𝗈 𝗎𝗌. 𝖳𝗈 𝗅𝖾𝖺𝗋𝗇 𝗆𝗈𝗋𝖾 𝖺𝖻𝗈𝗎𝗍 𝗁𝗈𝗐 𝗐𝖾 𝖼𝗈𝗅𝗅𝖾𝖼𝗍, 𝗎𝗌𝖾, 𝖺𝗇𝖽 𝗉𝗋𝗈𝗍𝖾𝖼𝗍 𝗒𝗈𝗎𝗋 𝖽𝖺𝗍𝖺, 𝗉𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗏𝗂𝖾𝗐 𝗈𝗎𝗋<a href="https://graph.org/Anya-Bots---Privacy-Policy-04-12">𝗣𝗿𝗶𝘃𝗮𝗰𝘆 𝗣𝗼𝗹𝗶𝗰𝘆</a>.'
                "\n"
                '𝖨𝖿 𝗒𝗈𝗎 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗊𝗎𝖾𝗌𝗍𝗂𝗈𝗇𝗌 𝗈𝗋 𝖼𝗈𝗇𝖼𝖾𝗋𝗇𝗌, 𝖿𝖾𝖾𝗅 𝖿𝗋𝖾𝖾 𝗍𝗈 𝗋𝖾𝖺𝖼𝗁 𝗈𝗎𝗍 𝗍𝗈 𝗈𝗎𝗋 <a href="https://t.me/CarelessxWorld">𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝘁𝗲𝗮𝗺</a>.'
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
        ("🔮 𝖬𝗈𝖽𝗋𝖺𝗍𝗂𝗈𝗇 ⌯",     "moderation"),
        ("⚠️ 𝖶𝖺𝗋𝗇𝗌 ⌯",             "warns_help"),
        ("🚷 𝖡𝗅 𝖴𝗌𝖾𝗋 ⌯",           "blackuser_help"),
        ("🚫 𝖡𝗅 𝖶𝗈𝗋𝖽𝗌 ⌯",          "blacklist_help"),
        ("🤬 𝖠𝖻𝗎𝗌𝖾 ⌯",              "abuse_help"),
        ("🗑️ 𝖢𝗆𝖽 𝖣𝖾𝗅 ⌯",           "cmd_help"),
        ("🚮 𝖬𝖾𝖽𝗂𝖺 𝖣𝖾𝗅 ⌯",         "mediadelete_help"),
        ("🆘 𝖠𝖽𝗆𝗂𝗇 ⌯",              "admin_tag_help"),
        ("👮🏻 𝖯𝗋𝗈𝗆𝗈𝗍𝗂𝗈𝗇 ⌯",        "promote_help"),
        ("⌛ 𝖫𝗈𝗇𝗀 𝖫𝗂𝗆𝗂𝗍 ⌯",        "longmsg_help"),
        ("#️⃣ 𝖧𝖺𝗌𝗁𝗍𝖺𝗀 ⌯",           "hashtag_help"),
    ]

    CATEGORY_SECURITY = [
        ("🔐 𝖫𝗈𝖼𝗄𝗌 ⌯",             "locks"),
        ("🕐 𝖠𝗎𝗍𝗈 𝖫𝗈𝖼𝗄",             "autolock_help"),
        ("🔡 𝖢𝖺𝗉𝗍𝖼𝗁𝖺 ⌯",            "captcha_help"),
        ("〽️ 𝖡𝗂𝗈 𝖫𝗂𝗇𝗄 ⌯",           "biolink"),
        ("🔗 𝖠𝗇𝗍𝗂 𝖫𝗂𝗇𝗄 ⌯",          "anti_link_help"),
        ("🪠 𝖥-𝖲𝗎𝖻 ⌯",               "fsub_help"),
        ("🧴 𝖢𝗅𝖾𝖺𝗇𝖾𝗋 ⌯",            "cleaner_help"),
        ("📵 𝖯𝗁𝗈𝗇𝖾 ⌯",               "phone_help"),
        ("🎭 𝖠𝗇𝗍𝗂 𝖲𝗍𝗂𝖼𝗄𝖾𝗋 ⌯",      "anti_sticker_help"),
        ("🧟 𝖹𝗈𝗆𝖻𝗂𝖾𝗌 ⌯",            "zombie_help"),
        ("👻 𝖦𝗁𝗈𝗌𝗍 ⌯",               "ghost_help"),
        ("🤿 𝖥𝗂𝗅𝗍𝖾𝗋𝗌 ⌯",             "filters_help"),
        ("⛩️ 𝖩𝗈𝗂𝗇 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 ⌯",      "joinrequest_help"),
        ("🛡️ 𝖠𝗇𝗍𝗂 𝖱𝖺𝗂𝖽 ⌯",          "antiraid_help"),
        ("🌊 𝖠𝗇𝗍𝗂 𝖥𝗅𝗈𝗈𝖽 ⌯",         "antiflood_help"),
        ("⚙️ 𝖣𝗂𝗌𝖺𝖻𝗅𝖾",               "disable_help"),
        ("🪭 𝖥𝖺𝗇𝖼𝗒 𝖳𝖾𝗑𝗍 ⌯",         "fancy_text_help"),
    ]
    
    CATEGORY_UTILITY = [
        ("💌 𝖦𝗋𝖾𝖾𝗍𝗂𝗇𝗀𝗌 ⌯",     "greetings"),
        ("📝 𝖭𝗈𝗍𝖾𝗌 ⌯",              "notes_help"),
        ("📑 𝖱𝗎𝗅𝖾𝗌 ⌯",              "rules_help"),
        ("⚙️ 𝖴𝗍𝗂𝗅𝗂𝗍𝗒 ⌯",           "utility_help"),
        ("🔖 𝖳𝖺𝗀 𝖠𝗅𝗅 ⌯",            "tagall_help"),
        ("🕊 𝖠𝗉𝗉𝗋𝗈𝗏𝖾",              "approve_help"),
        ("📤 𝖥𝗈𝗋𝗐𝖺𝗋𝖽 ⌯",            "forward_help"),
        ("🤖 𝖤𝖽𝗂𝗍𝗁 𝖠𝖨 ⌯",           "ai_help"),
    ]

    
    CATEGORY_GROUPS = [
        ("👥 𝖦𝗋𝗈𝗎𝗉 ⌯",          "groupinfo_help"),
        ("🔗 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄 ⌯",    "linkinfo_help"),
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
            "❖ 𝖢𝗁𝗈𝗈𝗌𝖾 𝗍𝗁𝖾 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗒 𝖿𝗈𝗋 𝗐𝗁𝗂𝖼𝗁 𝗒𝗈𝗎 𝗐𝖺𝗇𝗇𝖺 𝗀𝖾𝗍 𝗁𝖾𝗅𝗉\n\n"
            "➥ 𝖠𝗌𝗄 𝗒𝗈𝗎𝗋 𝖽𝗈𝗎𝖻𝗍𝗌 𝖺𝗍 <a href='https://t.me/CarelessxWorld'>𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖢𝗁𝖺𝗍</a>\n"
            "𝖠𝗅𝗅 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖼𝖺𝗇 𝖻𝖾 𝗎𝗌𝖾𝖽 𝗐𝗂𝗍𝗁 :<code>/</code>"
        )
        rows = [
            [
                InlineKeyboardButton("🔮 𝖬𝗈𝖽𝖾𝗋𝖺𝗍𝗂𝗈𝗇", callback_data="help_cat|moderation|0", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("🛡️ 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒", callback_data="help_cat|security|0", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("⚙️ 𝖴𝗍𝗂𝗅𝗂𝗍𝗒", callback_data="help_cat|utility|0", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("👥 𝖦𝗋𝗈𝗎𝗉𝗌", callback_data="help_cat|groups|0", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("💰 𝖤𝖼𝗈𝗇𝗈𝗆𝗒", callback_data="eco_menu", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("🏠 𝖡𝖺𝖼𝗄", callback_data="back_to_start", style=ButtonStyle.DANGER),
                InlineKeyboardButton("✖ 𝖢𝗅𝗈𝗌𝖾", callback_data="help_close", style=ButtonStyle.DANGER),
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
            nav.append(InlineKeyboardButton("« 𝖯𝗋𝖾𝗏", callback_data=f"help_cat|{category}|{page - 1}", style=ButtonStyle.SUCCESS))
        else:
            nav.append(InlineKeyboardButton("«", callback_data="noop", style=ButtonStyle.SUCCESS))

        nav.append(InlineKeyboardButton("🔙 𝖡𝖺𝖼𝗄", callback_data="help_categories", style=ButtonStyle.DANGER))

        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("𝖭𝖾𝗑𝗍 »", callback_data=f"help_cat|{category}|{page + 1}", style=ButtonStyle.SUCCESS))
        else:
            nav.append(InlineKeyboardButton("»", callback_data="noop", style=ButtonStyle.SUCCESS))

        rows.append(nav)

        text = (
            f"<blockquote expandable>❖ {category.upper()} 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀</blockquote>\n\n"
            "➥ 𝖠𝗌𝗄 𝗒𝗈𝗎𝗋 𝖽𝗈𝗎𝖻𝗍𝗌 𝖺𝗍 <a href='https://t.me/CarelessxWorld'>𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖢𝗁𝖺𝗍</a>"
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
            InlineKeyboardButton("« 𝖡𝖺𝖼𝗄", callback_data=f"help_cat|{category}|{page}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🏠 𝖧𝗈𝗆𝖾", callback_data="back_to_start", style=ButtonStyle.DANGER),
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
                f"<blockquote>🎀 <b>𝖩𝗈𝗂𝗇 / 𝖫𝖾𝖺𝗏𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝗋</b></blockquote>\n\n"
                f"❖ <i>𝖠𝗎𝗍𝗈-𝖽𝖾𝗅𝖾𝗍𝖾 𝗃𝗈𝗂𝗇 / 𝗅𝖾𝖺𝗏𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌</i>\n\n"
                f"➻ <code>/cleanservice on</code> <b>𝖤𝗇𝖺𝖻𝗅𝖾</b> — 𝖠𝗎𝗍𝗈-𝖽𝖾𝗅𝖾𝗍𝖾\n"
                f"       <i>𝖿𝗈𝗋 𝗃𝗈𝗂𝗇 / 𝗅𝖾𝖺𝗏𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌</i>\n\n"
                f"➻ <code>/cleanservice off</code> <b>𝖣𝗂𝗌𝖺𝖻𝗅𝖾</b> — 𝖠𝗎𝗍𝗈-𝖽𝖾𝗅𝖾𝗍𝖾\n"
                f"       <i>𝖿𝗈𝗋 𝗃𝗈𝗂𝗇 / 𝗅𝖾𝖺𝗏𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌</i>\n"
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
            f"<blockquote>⚙️ <b>𝖫𝗈𝖼𝗄𝗌 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/lock</code> — <i>𝖤𝗇𝖺𝖻𝗅𝖾 𝖺 𝗅𝗈𝖼𝗄</i>\n"
            f"➻ <code>/unlock</code> — <i>𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖺 𝗅𝗈𝖼𝗄</i>\n"
            f"➻ <code>/locks</code> — <i>𝖲𝗁𝗈𝗐 𝖺𝖼𝗍𝗂𝗏𝖾 𝗅𝗈𝖼𝗄𝗌</i>\n"
            f"➻ <code>/lockall</code> — <i>𝖫𝗈𝖼𝗄 𝖾𝗏𝖾𝗋𝗒𝗍𝗁𝗂𝗇𝗀</i> 🔐\n"
            f"➻ <code>/unlockall</code> — <i>𝖴𝗇𝗅𝗈𝖼𝗄 𝖾𝗏𝖾𝗋𝗒𝗍𝗁𝗂𝗇𝗀</i> 🔓\n\n"
            f"<blockquote expandable>❖ <b>𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖳𝗒𝗉𝖾𝗌</b> ❖</blockquote>\n"
            f"<code>url</code> • <code>text</code> • <code>sticker</code> • "
            f"<code>media</code> • <code>music</code>\n"
            f"<code>username</code> • <code>forward</code> • <code>edit</code> • "
            f"<code>files</code> • <code>emoji</code>"
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
            f"<blockquote>⚙️ <b>𝖬𝗈𝖽𝖾𝗋𝖺𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
            f"➻ <code>/kick</code> — <i>𝖱𝖾𝗆𝗈𝗏𝖾 𝖺 𝗎𝗌𝖾𝗋</i>\n"
            f"➻ <code>/ban</code> — <i>𝖡𝖺𝗇 𝗉𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍𝗅𝗒</i>\n"
            f"➻ <code>/unban</code> — <i>𝖫𝗂𝖿𝗍 𝖺 𝖻𝖺𝗇</i>\n"
            f"➻ <code>/mute</code> — <i>𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌</i>\n"
            f"➻ <code>/unmute</code> — <i>𝖠𝗅𝗅𝗈𝗐 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗀𝖺𝗂𝗇</i>\n"
            f"➻ <code>/tmute &lt;time&gt;</code> — <i>𝖳𝖾𝗆𝗉 𝗆𝗎𝗍𝖾 (1m–24h)</i>\n"
            f"➻ <code>/tban &lt;time&gt;</code> — <i>𝖳𝖾𝗆𝗉 𝖻𝖺𝗇 (1m–24h)</i>\n"
            f"➻ <code>/dkick</code> — <i>𝖪𝗂𝖼𝗄 𝖻𝗒 𝗋𝖾𝗉𝗅𝗒 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
            f"➻ <code>/skick</code> — <i>𝖲𝗂𝗅𝖾𝗇𝗍 𝗄𝗂𝖼𝗄 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝖼𝗆𝖽</i>\n"
            f"➻ <code>/dmute</code> — <i>𝖬𝗎𝗍𝖾 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
            f"➻ <code>/dban</code> — <i>𝖡𝖺𝗇 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
            f"➻ <code>/dwarn</code> — <i>𝖶𝖺𝗋𝗇 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
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
            f"<blockquote>⚠️ <b>𝖶𝖺𝗋𝗇 𝖲𝗒𝗌𝗍𝖾𝗆</b></blockquote>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/warn [reason]</code> — <i>𝖶𝖺𝗋𝗇 𝖺 𝗎𝗌𝖾𝗋</i>\n"
            f"➻ <code>/dwarn</code> — <i>𝖶𝖺𝗋𝗇 + 𝖽𝖾𝗅𝖾𝗍𝖾 𝗍𝗁𝖾𝗂𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
            f"➻ <code>/warns</code> — <i>𝖵𝗂𝖾𝗐 𝗐𝖺𝗋𝗇 𝗁𝗂𝗌𝗍𝗈𝗋𝗒</i>\n"
            f"➻ <code>/unwarn</code> — <i>𝖱𝖾𝗆𝗈𝗏𝖾 𝟣 𝗐𝖺𝗋𝗇</i>\n"
            f"➻ <code>/resetwarns</code> — <i>𝖢𝗅𝖾𝖺𝗋 𝖺𝗅𝗅 𝗐𝖺𝗋𝗇𝗌</i>\n"
            f"➻ <code>/setwarnlimit [1-10]</code> — <i>𝖲𝖾𝗍 𝗐𝖺𝗋𝗇 𝗅𝗂𝗆𝗂𝗍</i>\n"
            f"➻ <code>/setwarnaction mute|kick|ban</code> <i>𝖲𝖾𝗍 𝗐𝖺𝗋𝗇 𝖺𝖼𝗍𝗂𝗈𝗇</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
            f"➻ <i>𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝗅𝗂𝗆𝗂𝗍:</i> <code>3 warns</code>\n"
            f"➻ <i>𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝖺𝖼𝗍𝗂𝗈𝗇:</i> <code>mute</code>\n"
            f"➻ <i>𝖶𝖺𝗋𝗇𝗌 𝗋𝖾𝗌𝖾𝗍 𝖺𝖿𝗍𝖾𝗋 𝖺𝖼𝗍𝗂𝗈𝗇 𝗂𝗌 𝗍𝖺𝗄𝖾𝗇</i>\n"
            f"➻ <i>𝖫𝖺𝗌𝗍 𝟧 𝗋𝖾𝖺𝗌𝗈𝗇𝗌 𝗌𝗁𝗈𝗐𝗇 𝗂𝗇</i> <code>/warns</code>"
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
            f"<blockquote>🔗 <b>𝖡𝗂𝗈𝗅𝗂𝗇𝗄 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
            f"<i>𝖡𝗅𝗈𝖼𝗄𝗌 𝗎𝗌𝖾𝗋𝗌 𝗐𝗁𝗈 𝗁𝖺𝗏𝖾 𝗅𝗂𝗇𝗄𝗌 𝗂𝗇 𝗍𝗁𝖾𝗂𝗋 𝖻𝗂𝗈.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/biolink on</code> — <i>𝖤𝗇𝖺𝖻𝗅𝖾 𝗉𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</i> ✅\n"
            f"➻ <code>/biolink off</code> — <i>𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝗉𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</i> ❌\n"
            f"➻ <code>/bioconfig</code> — <i>𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾 𝖺𝖼𝗍𝗂𝗈𝗇</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
            f"➻ <i>𝖡𝗂𝗈 𝗅𝗂𝗇𝗄 𝖽𝖾𝗍𝖾𝖼𝗍𝖾𝖽</i> → <b>𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖽𝖾𝗅𝖾𝗍𝖾𝖽</b>\n"
            f"➻ <i>𝖠𝖽𝗆𝗂𝗇𝗌 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝖿𝖿𝖾𝖼𝗍𝖾𝖽</i>\n"
            f"➻ <i>𝖡𝗈𝗍 𝗇𝖾𝖾𝖽𝗌 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇</i>"
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
            f"<blockquote>🤬 <b>𝖠𝖻𝗎𝗌𝖾 𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
            f"<i>𝖠𝖻𝗎𝗌𝗂𝗏𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖽𝖾𝗅𝖾𝗍𝖾𝖽.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/noabuse on</code> — <i>𝖤𝗇𝖺𝖻𝗅𝖾 𝗉𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</i> ✅\n"
            f"➻ <code>/noabuse off</code> — <i>𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝗉𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</i> ❌\n\n"
            f"<blockquote expandable>❖ <b>𝖭𝗈𝗍𝖾𝗌</b> ❖</blockquote>\n"
            f"➻ <i>𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖽𝖾𝗅𝖾𝗍𝖾𝖽 𝗂𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒</i>\n"
            f"➻ <i>𝟧-𝗌𝖾𝖼𝗈𝗇𝖽 𝗐𝖺𝗋𝗇𝗂𝗇𝗀 𝗌𝖾𝗇𝗍</i>\n"
            f"➻ <i>𝖠𝖽𝗆𝗂𝗇𝗌 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝖿𝖿𝖾𝖼𝗍𝖾𝖽</i>"
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
            f"<blockquote>🔗 <b>𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾</b></blockquote>\n\n"
            f"<i>𝖴𝗌𝖾𝗋𝗌 𝗐𝗁𝗈 𝗁𝖺𝗏𝖾𝗇'𝗍 𝗃𝗈𝗂𝗇𝖾𝖽 𝗍𝗁𝖾 𝗋𝖾𝗊𝗎𝗂𝗋𝖾𝖽\n"
            f"𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖼𝖺𝗇𝗇𝗈𝗍 𝗌𝖾𝗇𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/addfsub @channel or [-100xxxx]</code>\n"
            f"➻ <code>/removefsub @channel or [-100xxxx]</code>\n"
            f"➻ <code>/fsublist</code> — <i>𝖫𝗂𝗌𝗍 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌</i>\n\n"
            f"<i>𝖡𝗈𝗍 𝗆𝗎𝗌𝗍 𝖻𝖾 𝖺𝖽𝗆𝗂𝗇 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅.</i>"
        )
        await callback_query.message.edit_media(
            InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML),
            reply_markup=make_back_btn(category, page)
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^utility_help\|(\w+)\|(\d+)$"))
    async def utility_help_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        text =
        f"<blockquote>⚙️ <b>𝖴𝗍𝗂𝗅𝗂𝗍𝗒</b></blockquote>\n\n"
        f"➻ <code>/chatinfo</code> — <i>𝖦𝗋𝗈𝗎𝗉 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 &amp; 𝗆𝖾𝗆𝖻𝖾𝗋 𝖼𝗈𝗎𝗇𝗍</i>\n    f"➻ <code>/id</code> — <i>𝖸𝗈𝗎𝗋 𝖨𝖣 𝗈𝗋 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗎𝗌𝖾𝗋'𝗌 𝖨𝖣</i>\n"
        f"➻ <code>/pin [silent]</code> — <i>𝖯𝗂𝗇 𝖺 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n      f"➻ <code>/unpin</code> — <i>𝖴𝗇𝗉𝗂𝗇 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗈𝗋 𝖺𝗅𝗅 𝗉𝗂𝗇𝗌</i>\n"
        f"➻ <code>/purge</code> — <i>𝖡𝗎𝗅𝗄 𝖽𝖾𝗅𝖾𝗍𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌</i>\n"
        f"➻ <code>/del</code> — <i>𝖣𝖾𝗅𝖾𝗍𝖾 𝖺 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾</i>\n"
        f"➻ <code>/report</code> — <i>𝖱𝖾𝗉𝗈𝗋𝗍 𝖺 𝗎𝗌𝖾𝗋 𝗍𝗈 𝖺𝖽𝗆𝗂𝗇𝗌</i>\n"
        f"➻ <code>/calc &lt;expr&gt;</code> — <i>𝖢𝖺𝗅𝖼𝗎𝗅𝖺𝗍𝗈𝗋</i>\n\n"
        f"<i>𝖯𝗂𝗇, 𝗉𝗎𝗋𝗀𝖾, 𝖽𝖾𝗅 — 𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒</i>"
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
            f"<blockquote>🧹 <b>𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖢𝗅𝖾𝖺𝗇𝖾𝗋</b></blockquote>\n\n"
            f"<i>𝖠𝗅𝗅 𝗋𝖾𝗀𝗎𝗅𝖺𝗋 𝗎𝗌𝖾𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝖽𝖾𝗅𝖾𝗍𝖾𝖽\n"
            f"𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝖿𝗍𝖾𝗋 𝖺 𝗌𝖾𝗍 𝖽𝖾𝗅𝖺𝗒.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/cleaner on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 ✅\n"
            f"➻ <code>/cleaner off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 ❌\n"
            f"➻ <code>/setcleandelay &lt;time&gt;</code> — 𝖲𝖾𝗍 𝖽𝖾𝗅𝖺𝗒\n"
            f"➻ <code>/cleanstatus</code> — 𝖲𝗁𝗈𝗐 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌\n"
            f"➻ 𝖠𝖽𝗆𝗂𝗇 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝗇𝖾𝗏𝖾𝗋 𝖽𝖾𝗅𝖾𝗍𝖾𝖽\n"
            f"➻ 𝖱𝖺𝗇𝗀𝖾: 1𝗆 𝗍𝗈 24𝗁 — 𝖣𝖾𝖿𝖺𝗎𝗅𝗍: 5𝗆"
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
            f"<blockquote>📄 <b>𝖫𝗈𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</b></blockquote>\n\n"
            f"<i>𝖫𝗈𝗇𝗀 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝗎𝗉𝗅𝗈𝖺𝖽𝖾𝖽 𝗍𝗈 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁\n"
            f"𝖺𝗇𝖽 𝗌𝖾𝗇𝗍 𝖺𝗌 𝖺 𝗅𝗂𝗇𝗄 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒.</i>\n\n"
            f"<blockquote expandable>"
            f"❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/setlongmode off</code> — 𝖭𝗈 𝖺𝖼𝗍𝗂𝗈𝗇\n"
            f"➻ <code>/setlongmode manual</code> — 𝖣𝖾𝗅𝖾𝗍𝖾 + 𝗐𝖺𝗋𝗇\n"
            f"➻ <code>/setlongmode automatic</code> — 𝖣𝖾𝗅𝖾𝗍𝖾 + 𝗅𝗂𝗇𝗄 ✅\n"
            f"➻ <code>/setlonglimit &lt;200–4000&gt;</code> — 𝖲𝖾𝗍 𝗅𝗂𝗆𝗂𝗍\n"
            f"<i>𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝗅𝗂𝗆𝗂𝗍: 800 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌</i>"
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
            f"<blockquote>🔖 <b>𝖧𝖺𝗌𝗁𝗍𝖺𝗀 𝖥𝗂𝗅𝗍𝖾𝗋</b></blockquote>\n\n"
            f"<i>𝖧𝖺𝗌𝗁𝗍𝖺𝗀 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖽𝖾𝗅𝖾𝗍𝖾𝖽.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/nohashtags on</code> — 𝖡𝗅𝗈𝖼𝗄 ✅\n"
            f"➻ <code>/nohashtags off</code> — 𝖠𝗅𝗅𝗈𝗐 ❌\n\n"
            f"➻ 𝖠𝗇𝗒 𝗐𝗈𝗋𝖽 𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝗐𝗂𝗍𝗁 #"
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
            f"<blockquote>🚧 <b>𝖤𝖼𝗁𝗈</b></blockquote>\n\n"
            f"➻ <code>/echo &lt;text&gt;</code> — <i>𝖤𝖼𝗁𝗈 𝗍𝖾𝗑𝗍 𝖺𝗌 𝖻𝗈𝗍</i>"
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
            f"<blockquote>🗑️ <b>𝖢𝗆𝖽 𝖣𝖾𝗅𝖾𝗍𝖾𝗋</b></blockquote>\n\n"
            f"<i>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 <code>/</code> <code>!</code> <code>.</code> 𝖺𝗋𝖾 𝖺𝗎𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾𝖽.</i>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/cmd on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 ✅\n"
            f"➻ <code>/cmd off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 ❌\n\n"
            f"<i>𝖠𝖽𝗆𝗂𝗇𝗌 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝖿𝖿𝖾𝖼𝗍𝖾𝖽.</i>"
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
            f"<blockquote>🎬 <b>𝖬𝖾𝖽𝗂𝖺 𝖠𝗎𝗍𝗈-𝖣𝖾𝗅𝖾𝗍𝖾</b></blockquote>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/mediadelete on</code> — 𝖤𝗇𝖺𝖻𝗅𝖾 ✅\n"
            f"➻ <code>/mediadelete off</code> — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 ❌\n"
            f"➻ <code>/setmediadelay &lt;time&gt;</code> — 𝖲𝖾𝗍 𝖽𝖾𝗅𝖺𝗒\n\n"
            f"➻ 𝖯𝗁𝗈𝗍𝗈𝗌, 𝗏𝗂𝖽𝖾𝗈𝗌, 𝗌𝗍𝗂𝖼𝗄𝖾𝗋𝗌, 𝖦𝖨𝖥𝗌\n"
            f"<i>𝖱𝖺𝗇𝗀𝖾: 1𝗆 𝗍𝗈 24𝗁 — 𝖣𝖾𝖿𝖺𝗎𝗅𝗍: 5𝗆</i>"
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
            f"<blockquote>📵 <b>𝖯𝗁𝗈𝗇𝖾 𝖯𝗋𝗈𝗍𝖾𝖼𝗍𝗂𝗈𝗇</b></blockquote>\n\n"
            f"<blockquote expandable>❖ <b>𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌</b> ❖</blockquote>\n"
            f"➻ <code>/nophone on</code> — 𝖡𝗅𝗈𝖼𝗄 ✅\n"
            f"➻ <code>/nophone off</code> — 𝖠𝗅𝗅𝗈𝗐 ❌\n\n"
            f"➻ <code>+91 9876543210</code>\n"
            f"➻ <code>+1-234-567-8900</code>"
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
    def build_eco_
        text = (
            "<blockquote>💰 <b>𝖤𝖼𝗈𝗇𝗈𝗆𝗒</b></blockquote>\n\n"
            "𝖢𝗁𝗈𝗈𝗌𝖾 𝖺 𝗌𝖾𝖼𝗍𝗂𝗈𝗇:"
        )
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
