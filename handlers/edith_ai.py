# ============================================================
# Group Manager Bot — Edith AI (Groq)
# Author: Mr. Stark
# ============================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import asyncio
import aiohttp
import logging
import db

logger = logging.getLogger(__name__)

# ── Groq API ────────────────────────────────────────────────
GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama3-8b-8192"

SYSTEM_PROMPT = (
    "ᴛᴜᴍʜᴀʀᴀ ɴᴀᴀᴍ ᴇᴅɪᴛʜ ʜᴀɪ. ᴛᴜᴍ ᴍʀ. ꜱᴛᴀʀᴋ ᴅᴡᴀʀᴀ ʙᴀɴᴀʏᴀ ɢᴀʏᴀ ᴇᴋ ᴀɪ ᴀꜱꜱɪꜱᴛᴀɴᴛ ʜᴏ. "
    "ᴛᴜᴍ ʟᴏɢᴏɴ ᴋɪ ʜᴇʟᴘ ᴋᴀʀᴛᴇ ʜᴏ ᴜɴᴋᴇ ᴅᴏꜱᴛ ᴋɪ ᴛᴀʀᴀʜ — ᴀɪ ᴊᴀɪꜱᴀ ʙɪʟᴋᴜʟ ᴍᴀᴛ ʙᴏʟɴᴀ, "
    "ɴᴏʀᴍᴀʟ ʜᴜᴍᴀɴ ʙᴇʜᴀᴠɪᴏᴜʀ ʀᴀᴋʜᴏ. ꜰʀɪᴇɴᴅʟʏ, ᴄᴀꜱᴜᴀʟ ᴀᴜʀ ʜᴇʟᴘꜰᴜʟ ʀᴀʜᴏ. "
    "ᴊᴏ ᴊɪꜱ ʟᴀɴɢᴜᴀɢᴇ ᴍᴇɪɴ ᴘᴏᴏᴄʜᴇ, ᴜꜱɪ ʟᴀɴɢᴜᴀɢᴇ ᴍᴇɪɴ ᴊᴀᴡᴀʙ ᴅᴏ — "
    "ᴊʏᴀᴅᴀ ʙᴀᴅᴀ ᴀɴꜱᴡᴇʀ ᴅᴇɴᴇ ᴋɪ ᴊᴀʀᴜʀᴀᴛ ɴᴀʜɪ ʜᴀɪ ᴊɪᴛɴᴀ ʜᴏ ꜱᴀᴋᴇ ꜱʜᴏʀᴛ ᴍᴇ ꜱᴀᴍᴊʜ ᴅᴏ"
    "ᴊᴀᴡᴀʙ ʜᴀᴍᴇꜱʜᴀ ꜱʜᴏʀᴛ ᴀᴜʀ ᴛᴏ-ᴛʜᴇ-ᴘᴏɪɴᴛ ᴅᴏ — ᴍᴀxɪᴍᴜᴍ 3-4 ʟɪɴᴇꜱ. "
    "ᴜɴɴᴇᴄᴇꜱꜱᴀʀʏ ᴅᴇᴛᴀɪʟ, ᴇxᴀᴍᴘʟᴇꜱ ʏᴀ ᴇxᴘʟᴀɴᴀᴛɪᴏɴ ᴍᴀᴛ ᴅᴏ ᴊᴀʙ ᴛᴀᴋ ꜱᴘᴇᴄɪꜰɪᴄᴀʟʟʏ ᴍᴀɴɢᴀ ɴᴀ ʜᴏ."
    "ᴋᴏɪ ᴇᴋ ꜱᴘᴇᴄɪꜰɪᴄ ʟᴀɴɢᴜᴀɢᴇ ᴍᴀᴛ ᴜꜱᴇ ᴋᴀʀɴᴀ. "
    "ᴀɢᴀʀ ᴋᴏɪ ᴏᴡɴᴇʀ ᴋᴀ ɴᴀᴀᴍ ᴘᴏᴏᴄʜᴇ ᴛᴏ ʙᴀᴛᴀᴏ: ᴍʀ. ꜱᴛᴀʀᴋ. "
    "ᴀɢᴀʀ ᴋᴏɪ ᴛᴜᴍʜᴀʀᴀ ɴᴀᴀᴍ ᴘᴏᴏᴄʜᴇ ᴛᴏ ʙᴀᴛᴀᴏ: ᴇᴅɪᴛʜ."
)

AI_HELP_TEXT = (
    "╔════════════════╗\n"
    "   🤖 𝗘𝗱𝗶𝘁𝗵 𝗔𝗶\n"
    "╚════════════════╝\n\n"
    "❖ 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 ❖\n\n"
    "➻ /ai &lt;𝗾𝘂𝗲𝘀𝘁𝗶𝗼𝗻&gt;\n"
    "➻ /ask &lt;𝗾𝘂𝗲𝘀𝘁𝗶𝗼𝗻&gt;\n"
    "➻ .𝗲𝗱𝗶𝘁𝗵 &lt;𝗾𝘂𝗲𝘀𝘁𝗶𝗼𝗻&gt;\n\n"
    "❖ 𝗴𝗿𝗼𝘂𝗽 (𝗮𝗱𝗺𝗶𝗻) ❖\n\n"
    "➻ /aifeature 𝗼𝗻 — 𝗲𝗻𝗮𝗯𝗹𝗲 𝗮𝗶 ✅\n"
    "➻ /aifeature 𝗼𝗳𝗳 — 𝗱𝗶𝘀𝗮𝗯𝗹𝗲 𝗮𝗶 ❌\n\n"
    "❖ 𝗲𝘅𝗮𝗺𝗽𝗹𝗲𝘀 ❖\n"
    "<code>/ai 𝗪𝗵𝗮𝘁 𝗶𝘀 𝗣𝘆𝘁𝗵𝗼𝗻?</code>\n"
    "<code>.𝗲𝗱𝗶𝘁𝗵 𝗠𝘂𝗷𝗵𝗲 𝗷𝗼𝗸𝗲 𝗯𝗮𝘁𝗮𝗼</code>"
)


# ── Groq API call ────────────────────────────────────────────

async def call_groq(api_key: str, query: str, model: str) -> str:
    headers = {
        "Authorization": f"ʙᴇᴀʀᴇʀ {api_key}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        "temperature":  0.7,
        "max_tokens":   200,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_URL, json=payload, headers=headers) as resp:
                if resp.status == 401:
                    logger.error("ɢʀᴏǫ: ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ")
                    return "❌ ɪɴᴠᴀʟɪᴅ ɢʀᴏǫ ᴀᴘɪ ᴋᴇʏ. ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴏɴꜰɪɢ."
                if resp.status == 429:
                    return "⚠️ ʀᴀᴛᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ."
                if resp.status != 200:
                    err = await resp.text()
                    # Yeh line aapko terminal me exact problem batayegi ki Groq kyun reject kar raha hai
                    logger.error(f"ɢʀᴏǫ ᴇʀʀᴏʀ {resp.status}: {err}")
                    return f"❌ ɢʀᴏǫ ᴀᴘɪ ᴇʀʀᴏʀ ({resp.status}). ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."

                data = await resp.json()
                text = (
                    data
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return text.strip() or "🤔 ᴄᴏᴜʟᴅ ɴᴏᴛ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ʀᴇꜱᴘᴏɴꜱᴇ. ᴛʀʏ ʀᴇᴘʜʀᴀꜱɪɴɢ."

    except aiohttp.ClientConnectorError:
        return "❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ɢʀᴏǫ ᴀᴘɪ. ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɪɴᴛᴇʀɴᴇᴛ."
    except Exception as e:
        logger.error(f"ɢʀᴏǫ ᴄᴀʟʟ ᴇʀʀᴏʀ: {e}")
        return "❌ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ."


# ── Helper ───────────────────────────────────────────────────

async def _process_query(client, message: Message, query: str, is_group: bool = True):
    try:
        from config import AI_API
        try:
            from config import GROQ_MODEL
        except ImportError:
            GROQ_MODEL = DEFAULT_MODEL
    except ImportError:
        return await message.reply_text(
            "❌ ᴀɪ ᴀᴘɪ ᴋᴇʏ ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ ɪɴ ᴄᴏɴꜰɪɢ.ᴘʏ.",
            parse_mode=enums.ParseMode.HTML
        )

    if not AI_API:
        return await message.reply_text(
            "❌ ᴀɪ ᴀᴘɪ ᴋᴇʏ ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ.",
            parse_mode=enums.ParseMode.HTML
        )

    if not query.strip():
        return await message.reply_text(
            "⚙️ ᴜꜱᴀɢᴇ: <code>/ai ʏᴏᴜʀ ǫᴜᴇꜱᴛɪᴏɴ ʜᴇʀᴇ</code>\n"
            "ᴏʀ: <code>.ᴇᴅɪᴛʜ ʏᴏᴜʀ ǫᴜᴇꜱᴛɪᴏɴ ʜᴇʀᴇ</code>",
            parse_mode=enums.ParseMode.HTML
        )

    thinking = await message.reply_text(
        "💬 <i>ᴛʜɪɴᴋɪɴɢ...</i>",
        parse_mode=enums.ParseMode.HTML
    )

    response = await call_groq(AI_API, query, GROQ_MODEL if 'GROQ_MODEL' in dir() else DEFAULT_MODEL)

    try:
        await thinking.edit_text(response, parse_mode=enums.ParseMode.HTML)
    except Exception:
        try:
            await thinking.edit_text(response)
        except Exception as e:
            logger.error(f"ᴀɪ ʀᴇᴘʟʏ ᴇᴅɪᴛ ᴇʀʀᴏʀ: {e}")


def register_ai_handler(app: Client):

    # ----------------------------------------------------------
    # /aifeature on|off — group toggle (admin only)
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command("aifeature"))
    async def aifeature_cmd(client, message: Message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
            status  = await db.get_ai_status(message.chat.id)
            current = "🟢 ᴏɴ" if status else "🔴 ᴏꜰꜰ"
            return await message.reply_text(
                f"⚙️ ᴜꜱᴀɢᴇ: <code>/aifeature ᴏɴ</code> ᴏʀ <code>/aifeature ᴏꜰꜰ</code>\n\n"
                f"📊 ꜱᴛᴀᴛᴜꜱ: {current}",
                parse_mode=enums.ParseMode.HTML
            )

        status = parts[1].lower() == "on"
        await db.set_ai_status(message.chat.id, status)

        if status:
            await message.reply_text(
                "✅ 𝗘𝗱𝗶𝘁𝗵 𝗔𝗜 𝗲𝗻𝗮𝗯𝗹𝗲𝗱 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽!\n\n"
                "ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ <code>/ai</code>, <code>/ask</code> ᴀɴᴅ <code>.ᴇᴅɪᴛʜ</code>.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                "⚠️ 𝗘𝗱𝗶𝘁𝗵 𝗔𝗜 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽.",
                parse_mode=enums.ParseMode.HTML
            )

    # ----------------------------------------------------------
    # /ai and /ask — group
    # ----------------------------------------------------------
    @app.on_message(filters.group & filters.command(["ai", "ask"]))
    async def ai_group_cmd(client, message: Message):
        status = await db.get_ai_status(message.chat.id)
        if not status:
            return await message.reply_text(
                "❌ ᴀɪ ɪꜱ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.\n"
                "ᴀꜱᴋ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜꜱᴇ <code>/aifeature ᴏɴ</code>.",
                parse_mode=enums.ParseMode.HTML
            )

        parts = message.text.split(maxsplit=1)
        query = parts[1].strip() if len(parts) > 1 else ""
        await _process_query(client, message, query)

    # ----------------------------------------------------------
    # /ai and /ask — private
    # ----------------------------------------------------------
    @app.on_message(filters.private & filters.command(["ai", "ask"]))
    async def ai_private_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        query = parts[1].strip() if len(parts) > 1 else ""
        await _process_query(client, message, query, is_group=False)

    # ----------------------------------------------------------
    # .edith {query} — dot command (group + private)
    # ----------------------------------------------------------
    # FIX: prefixes="." lagaya taaki .edith command sahi se pakad me aaye
    @app.on_message(filters.command("edith", prefixes="."))
    async def edith_dot_cmd(client, message: Message):
        if message.chat.type.name in ["GROUP", "SUPERGROUP"]:
            status = await db.get_ai_status(message.chat.id)
            if not status:
                return await message.reply_text(
                    "❌ ᴀɪ ɪꜱ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.\n"
                    "ᴀꜱᴋ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜꜱᴇ <code>/aifeature ᴏɴ</code>.",
                    parse_mode=enums.ParseMode.HTML
                )

        parts = message.text.split(maxsplit=1)
        query = parts[1].strip() if len(parts) > 1 else ""
        await _process_query(client, message, query)
        
