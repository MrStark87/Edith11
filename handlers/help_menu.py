# ============================================================
# Telegram help menu — renders centralized help tables
# ============================================================

import logging
import re

from pyrogram import Client, filters, StopPropagation, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.help_texts import PAGES, render_rich, render_plain

logger = logging.getLogger(__name__)
PAGE_SIZE = 8


def _menu_markup(page=0):
    keys = list(PAGES)
    total_pages = max(1, (len(keys) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    entries = keys[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows = []
    for index in range(0, len(entries), 2):
        pair = entries[index:index + 2]
        rows.append([InlineKeyboardButton(PAGES[key]["title"], callback_data=f"grid_help|{key}|{page}") for key in pair])
    if total_pages > 1:
        nav = []
        if page:
            nav.append(InlineKeyboardButton("« Prev", callback_data=f"grid_menu|{page - 1}"))
        nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="grid_noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("Next »", callback_data=f"grid_menu|{page + 1}"))
        rows.append(nav)
    rows.append([InlineKeyboardButton("✖ Close", callback_data="grid_close")])
    return InlineKeyboardMarkup(rows)


def _detail_markup(page):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("« Back to help", callback_data=f"grid_menu|{page}"),
        InlineKeyboardButton("✖ Close", callback_data="grid_close"),
    ]])


async def _send_help(message, client, page=0):
    text = "<b>📚 Edith Help &amp; Commands</b>\nChoose a module below to see commands and their uses."
    try:
        await message.delete()
    except Exception:
        pass
    await client.send_message(message.chat.id, text, reply_markup=_menu_markup(page), parse_mode=enums.ParseMode.HTML)


async def _send_detail(message, client, key, page):
    content = render_rich(key)
    try:
        await message.delete()
    except Exception:
        pass
    try:
        await client.send_message(message.chat.id, content, reply_markup=_detail_markup(page), parse_mode=enums.ParseMode.HTML)
    except Exception as exc:
        # If Telegram rejects rich tables (e.g. unsupported client/API), send a
        # regular HTML list so the help remains usable rather than failing.
        logger.info("Rich help table unavailable; using plain help layout: %s", exc)
        await client.send_message(message.chat.id, render_plain(key), reply_markup=_detail_markup(page), parse_mode=enums.ParseMode.HTML)


def register_help_menu(app: Client):
    # Run before the legacy /help and help callbacks in start.py.
    @app.on_message(filters.private & filters.command("help"), group=-10)
    async def private_help(client, message):
        await _send_help(message, client)
        raise StopPropagation

    @app.on_message(filters.private & filters.command("start"), group=-10)
    async def help_deep_link(client, message):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2 or parts[1].strip().lower() != "help":
            return
        await _send_help(message, client)
        raise StopPropagation

    keys_pattern = "|".join(re.escape(key) for key in PAGES)
    callback_pattern = rf"^(?:help|help_categories|help_cat\|all\|\d+|back_to_start|help_close|noop|grid_menu\|\d+|grid_help\|(?:{keys_pattern})\|\d+|grid_close|grid_noop|(?:{keys_pattern})\|all\|\d+)$"

    @app.on_callback_query(filters.regex(callback_pattern), group=-10)
    async def help_navigation(client, callback_query):
        data = callback_query.data or ""
        if data in {"help", "help_categories", "back_to_start"}:
            await _send_help(callback_query.message, client)
        elif data in {"help_close", "grid_close"}:
            try:
                await callback_query.message.delete()
            except Exception:
                pass
        elif data in {"noop", "grid_noop"}:
            pass
        elif data.startswith("grid_menu|"):
            page = int(data.rsplit("|", 1)[1])
            await _send_help(callback_query.message, client, page)
        else:
            parts = data.split("|")
            if parts[0] == "grid_help":
                _, key, page = parts
            elif parts[0] == "help_cat":
                _, _, page = parts
                await _send_help(callback_query.message, client, int(page))
                await callback_query.answer()
                raise StopPropagation
            else:
                key = parts[0]
                page = parts[2]
            if key in PAGES:
                await _send_detail(callback_query.message, client, key, int(page))
        await callback_query.answer()
        raise StopPropagation
