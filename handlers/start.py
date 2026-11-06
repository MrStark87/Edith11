# ============================================================
# Group Manager Bot
# Author: Mr. Stark
# ============================================================

import logging
import aiohttp
from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from config import BOT_TOKEN, BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID, PRIVACY_IMAGE
import db
from handlers.help_texts import PAGES, render_rich, render_plain

logger = logging.getLogger(__name__)


def register_handlers(app: Client):

    # ==========================================================
    # Start Message helper
    # ==========================================================
    async def send_start_menu(message, user):
        text = (
            f"<blockquote><b>💐 𝐆ʀᴇᴇᴛɪɴɢs {user} 🥀</b></blockquote>"
            f"<blockquote expandable><b>𝐌ʏ ɴᴀᴍᴇ ɪs <a href='https://t.me/EdithHelpsBot'>𝐄ᴅɪᴛʜ 🤖</a>. 𝐈'ᴍ ᴀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs. \n\n⇩ 𝐍ᴇᴇᴅ ʜᴇʟᴘ? ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴏʀ sᴇɴᴅ</b> /help</blockquote>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✙ 𝖠𝖽𝖽 𝖬𝖾 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true", style=ButtonStyle.PRIMARY)],
            [
                InlineKeyboardButton("⌯ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 ⌯", url=SUPPORT_GROUP, style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("⌯ 𝖴𝗉𝖽𝖺𝗍𝖾 ⌯", url=UPDATE_CHANNEL, style=ButtonStyle.SUCCESS),
            ],
            [InlineKeyboardButton("⌯ 𝖧𝖾𝗅𝗉𝗌 𝖺𝗇𝖽 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 ⌯", callback_data="help", style=ButtonStyle.PRIMARY)]
        ])

        if message.text and not (message.from_user and message.from_user.is_bot):
            await message.reply_photo(
                START_IMAGE,
                caption=text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await _show_photo(message, text, buttons)


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
        html_text, kb = build_menu_rich()
        if not await _send_rich(message.chat.id, html_text, kb):
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
        ("🔮 𝐌ᴏᴅʀᴀᴛɪᴏɴ ⌯",     "moderation"),
        ("⚠️ 𝐖ᴀʀɴs ⌯",             "warns_help"),
        ("🚷 𝐁ʟ 𝐔sᴇʀ ⌯",           "blackuser_help"),
        ("🚫 𝐁ʟ 𝐖ᴏʀᴅs ⌯",          "blacklist_help"),
        ("🤬 𝐀ʙᴜsᴇ ⌯",              "abuse_help"),
        ("🗑️ 𝐂ᴍᴅ 𝐃ᴇʟ ⌯",           "cmd_help"),
        ("🚮 𝐌ᴇᴅɪᴀ 𝐃ᴇʟ ⌯",         "mediadelete_help"),
        ("🆘 𝐀ᴅᴍɪɴ ⌯",              "admin_tag_help"),
        ("👮🏻 𝐏ʀᴏᴍᴏᴛɪᴏɴ ⌯",        "promote_help"),
        ("⌛ 𝐋ᴏɴɢ 𝐋ɪᴍɪᴛ ⌯",        "longmsg_help"),
        ("#️⃣ 𝐇ᴀsʜᴛᴀɢ ⌯",           "hashtag_help"),
    ]

    CATEGORY_SECURITY = [
        ("🔐 𝐋ᴏᴄᴋs ⌯",             "locks"),
        ("🕐 𝐀ᴜᴛᴏ 𝐋ᴏᴄᴋ",             "autolock_help"),
        ("🔡 𝐂ᴀᴘᴛᴄʜᴀ ⌯",            "captcha_help"),
        ("〽️ 𝐁ɪᴏ 𝐋ɪɴᴋ ⌯",           "biolink"),
        ("🔗 𝐀ɴᴛɪ 𝐋ɪɴᴋ ⌯",          "anti_link_help"),
        ("🪠 𝐅-𝐒ᴜʙ ⌯",               "fsub_help"),
        ("🧴 𝐂ʟᴇᴀɴᴇʀ ⌯",            "cleaner_help"),
        ("📵 𝐏ʜᴏɴᴇ ⌯",               "phone_help"),
        ("🎭 𝐀ɴᴛɪ 𝐒ᴛɪᴄᴋᴇʀ ⌯",      "anti_sticker_help"),
        ("🧟 𝐙ᴏᴍʙɪᴇs ⌯",            "zombie_help"),
        ("👻 𝐆ʜᴏsᴛ ⌯",               "ghost_help"),
        ("🤿 𝐅ɪʟᴛᴇʀs ⌯",             "filters_help"),
        ("⛩️ 𝐉ᴏɪɴ 𝐑ᴇǫᴜᴇsᴛ ⌯",      "joinrequest_help"),
        ("🛡️ 𝐀ɴᴛɪ 𝐑ᴀɪᴅ ⌯",          "antiraid_help"),
        ("🌊 𝐀ɴᴛɪ 𝐅ʟᴏᴏᴅ ⌯",         "antiflood_help"),
        ("⚙️ 𝐃ɪsᴀʙʟᴇ",               "disable_help"),
        ("🪭 𝐅ᴀɴᴄʏ 𝐓ᴇxᴛ ⌯",         "fancy_text_help"),
    ]

    CATEGORY_UTILITY = [
        ("💌 𝐆ʀᴇᴇᴛɪɴɢs ⌯",     "greetings"),
        ("📝 𝐍ᴏᴛᴇs ⌯",              "notes_help"),
        ("📑 𝐑ᴜʟᴇs ⌯",              "rules_help"),
        ("⚙️ 𝐔ᴛɪʟɪᴛʏ ⌯",           "utility_help"),
        ("🔖 𝐓ᴀɢ 𝐀ʟʟ ⌯",            "tagall_help"),
        ("🕊 𝐀ᴘᴘʀᴏᴠᴇ",              "approve_help"),
        ("📤 𝐅ᴏʀᴡᴀʀᴅ ⌯",            "forward_help"),
        ("🤖 𝐄ᴅɪᴛʜ 𝐀ɪ ⌯",           "ai_help"),
    ]

    CATEGORY_GROUPS = [
        ("👥 𝐆ʀᴏᴜᴘ ⌯",          "groupinfo_help"),
        ("🔗 𝐈ɴᴠɪᴛᴇ 𝐋ɪɴᴋ ⌯",    "linkinfo_help"),
    ]
    
    # Saare buttons ek hi list mein (koi category nahi)
    ALL_BUTTONS = (
        CATEGORY_MODERATION
        + CATEGORY_SECURITY
        + CATEGORY_UTILITY
        + CATEGORY_GROUPS
    )

    ECO_CATEGORIES = {"all": ALL_BUTTONS}

    BUTTONS_PER_PAGE = 14  # 38 buttons -> 3 pages (14 + 14 + 10)


    def build_category_page(category: str, page: int):
        items = ECO_CATEGORIES.get(category, [])
        total_pages = max(1, (len(items) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE)
        page = page % total_pages
        start = page * BUTTONS_PER_PAGE
        page_buttons = items[start:start + BUTTONS_PER_PAGE]

        rows = []
        for i in range(0, len(page_buttons), 2):
            pair = page_buttons[i:i + 2]
            rows.append([
                InlineKeyboardButton(label, callback_data=f"{cb}|{category}|{page}", style=ButtonStyle.PRIMARY)
                for label, cb in pair
            ])

        # Sirf 3 buttons: Prev | Back | Next (pages wrap-around hote hain)
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        rows.append([
            InlineKeyboardButton("« 𝖯𝗋𝖾𝗏", callback_data=f"help_cat|{category}|{prev_page}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🏠 𝖡𝖺𝖼𝗄", callback_data="back_to_start", style=ButtonStyle.DANGER),
            InlineKeyboardButton("𝖭𝖾𝗑𝗍 »", callback_data=f"help_cat|{category}|{next_page}", style=ButtonStyle.SUCCESS),
        ])

        text = (
            "❖ 𝖢𝗁𝗈𝗈𝗌𝖾 𝖺 𝗆𝗈𝖽𝗎𝗅𝖾 𝖿𝗈𝗋 𝗐𝗁𝗂𝖼𝗁 𝗒𝗈𝗎 𝗐𝖺𝗇𝗇𝖺 𝗀𝖾𝗍 𝗁𝖾𝗅𝗉\n\n"
            "➥ 𝖠𝗌𝗄 𝗒𝗈𝗎𝗋 𝖽𝗈𝗎𝖻𝗍𝗌 𝖺𝗍 <a href='https://t.me/CarelessxWorld'>𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖢𝗁𝖺𝗍</a>\n"
            "𝖠𝗅𝗅 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖼𝖺𝗇 𝖻𝖾 𝗎𝗌𝖾𝖽 𝗐𝗂𝗍𝗁 :<code>/</code>"
        )
        return text, InlineKeyboardMarkup(rows)


    def build_category_menu():
        # Main help menu = saare buttons seedha
        return build_category_page("all", 0)


    async def _show_photo(message, text, buttons):
        """Photo menu dikhao. Agar current message photo hai to edit,
        warna (help page / rich message) delete karke naya photo bhejo."""
        if message.photo:
            media = InputMediaPhoto(media=START_IMAGE, caption=text, parse_mode=enums.ParseMode.HTML)
            await message.edit_media(media=media, reply_markup=buttons)
            return
        kwargs = {}
        thread_id = getattr(message, "message_thread_id", None)
        if thread_id:
            kwargs["message_thread_id"] = thread_id
        await app.send_photo(
            message.chat.id, START_IMAGE, caption=text,
            parse_mode=enums.ParseMode.HTML, reply_markup=buttons, **kwargs
        )
        try:
            await message.delete()
        except Exception:
            pass


    async def send_category_menu(message):
        text, buttons = build_category_menu()
        await _show_photo(message, text, buttons)


    async def send_category_page(message, category, page=0):
        text, buttons = build_category_page(category, page)
        await _show_photo(message, text, buttons)


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
        await show_menu(client, callback_query)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client, callback_query):
        await show_menu(client, callback_query)
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^help_categories$"))
    async def help_categories_callback(client, callback_query):
        await show_menu(client, callback_query)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^help_cat\|(\w+)\|(\d+)$"))
    async def help_cat_callback(client, callback_query):
        category, page = callback_query.matches[0].group(1), int(callback_query.matches[0].group(2))
        await show_menu(client, callback_query, page)
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


    # ==========================================================
    # 📋 HELP PAGES — saare pages handlers/help_texts.py se aate hain
    #    (grid / table format, Telegram Rich Message)
    # ==========================================================
    async def _tg_api(method, payload):
        """Bot API ko seedha call karo (pyrogram fork mein rich message nahi hai)."""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()
            if data.get("ok"):
                return True
            # Same content dobara edit karne par Telegram error deta hai — ye theek hai
            if "not modified" in str(data.get("description", "")).lower():
                return True
            logger.warning(f"{method} failed: {data}")
            return False
        except Exception as e:
            logger.warning(f"{method} error: {e}")
            return False


    async def _send_rich(chat_id, html_text, reply_markup, thread_id=None):
        payload = {
            "chat_id": chat_id,
            "rich_message": {"html": html_text},
            "reply_markup": reply_markup,
        }
        if thread_id:
            payload["message_thread_id"] = thread_id
        return await _tg_api("sendRichMessage", payload)


    async def _edit_rich(chat_id, message_id, html_text, reply_markup):
        """Usi message ko edit karo (naya message nahi)."""
        return await _tg_api("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "rich_message": {"html": html_text},
            "reply_markup": reply_markup,
        })


    def build_menu_rich(page=0):
        """Help menu ka rich version (taaki pages ke saath edit ho sake)."""
        items = ECO_CATEGORIES["all"]
        total_pages = max(1, (len(items) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE)
        page = page % total_pages
        chunk = items[page * BUTTONS_PER_PAGE:(page + 1) * BUTTONS_PER_PAGE]

        rows = []
        for i in range(0, len(chunk), 2):
            rows.append([
                {"text": label, "callback_data": f"{cb}|all|{page}", "style": "primary"}
                for label, cb in chunk[i:i + 2]
            ])
        # Sirf 3 buttons: Prev | Back | Next (wrap-around)
        rows.append([
            {"text": "« Prev", "callback_data": f"help_cat|all|{(page - 1) % total_pages}", "style": "success"},
            {"text": "🏠 Back", "callback_data": "back_to_start", "style": "danger"},
            {"text": "Next »", "callback_data": f"help_cat|all|{(page + 1) % total_pages}", "style": "success"},
        ])
        html_text = (
            "<p>❖ Choose a module for which you want help</p>"
            "<p>➥ Ask your doubts at <a href='https://t.me/CarelessxWorld'>Support Chat</a></p>"
            "<p>All commands can be used with: <code>/</code></p>"
        )
        return html_text, {"inline_keyboard": rows}


    async def show_menu(client, callback_query, page=0):
        """Help menu dikhao — rich message hua to usi message mein edit."""
        msg = callback_query.message
        chat_id = msg.chat.id
        thread_id = getattr(msg, "message_thread_id", None)
        html_text, kb = build_menu_rich(page)

        # 1) Already rich/text message — usi mein edit
        if not msg.photo and await _edit_rich(chat_id, msg.id, html_text, kb):
            return
        # 2) Start screen (photo) — photo ko edit nahi kar sakte, ek baar naya bhejo
        if await _send_rich(chat_id, html_text, kb, thread_id):
            try:
                await msg.delete()
            except Exception:
                pass
            return
        # 3) Last fallback — purana photo menu
        text, buttons = build_category_page("all", page)
        await _show_photo(msg, text, buttons)


    HELP_PAGE_KEYS = "|".join(PAGES.keys())

    @app.on_callback_query(filters.regex(rf"^({HELP_PAGE_KEYS})\|(\w+)\|(\d+)$"))
    async def help_page_callback(client, callback_query):
        key = callback_query.matches[0].group(1)
        category = callback_query.matches[0].group(2)
        page = int(callback_query.matches[0].group(3))

        msg = callback_query.message
        chat_id = msg.chat.id
        thread_id = getattr(msg, "message_thread_id", None)

        keyboard = {"inline_keyboard": [[
            {"text": "« Back", "callback_data": f"help_cat|{category}|{page}", "style": "primary"},
            {"text": "🏠 Home", "callback_data": "back_to_start", "style": "danger"},
        ]]}

        page_html = render_rich(key)

        # Usi message mein edit (naya message nahi)
        if not msg.photo and await _edit_rich(chat_id, msg.id, page_html, keyboard):
            await callback_query.answer()
            return

        sent = await _send_rich(chat_id, page_html, keyboard, thread_id)
        if not sent:
            # Fallback: rich message na jaye to normal HTML message
            kwargs = {"message_thread_id": thread_id} if thread_id else {}
            await client.send_message(
                chat_id,
                render_plain(key),
                parse_mode=enums.ParseMode.HTML,
                reply_markup=make_back_btn(category, page),
                **kwargs,
            )

        # Purana (photo) message hata do
        try:
            await msg.delete()
        except Exception:
            pass
        await callback_query.answer()


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
