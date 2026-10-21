# ============================================================
# Economy Game System — Fun (Marriage)
# Author: Mr. Stark
# ============================================================
from pyrogram import enums, filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from handlers.eco_data import fmt_amount
import db

PROPOSE_COST = 500
DIVORCE_COST = 2000

# pending proposals: target_id -> proposer_id
_pending_proposals: dict = {}


def register_fun_handler(app: Client):

    # ==========================================================
    # /status
    # ==========================================================
    @app.on_message(filters.command("status"))
    async def status_cmd(client, message: Message):
        data = await db.get_eco_user(message.from_user.id)
        if data.get("marital_status") == "married" and data.get("spouse_name"):
            text = f"💍 ᴍᴀʀʀɪᴇᴅ ᴡɪᴛʜ <b>{data['spouse_name']}</b>"
        else:
            text = "💔 ꜱɪɴɢʟᴇ"
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /propose, /marry (reply only)
    # ==========================================================
    @app.on_message(filters.command(["propose", "marry"]))
    async def propose_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴘʀᴏᴘᴏꜱᴇ.", parse_mode=enums.ParseMode.HTML)
        target = message.reply_to_message.from_user
        proposer = message.from_user

        if target.id == proposer.id:
            return await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴘʀᴏᴘᴏꜱᴇ ʏᴏᴜʀꜱᴇʟꜰ.", parse_mode=enums.ParseMode.HTML)

        proposer_data = await db.get_eco_user(proposer.id)
        target_data = await db.get_eco_user(target.id)

        if proposer_data.get("marital_status") == "married":
            return await message.reply_text("❌ ʏᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ᴍᴀʀʀɪᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if target_data.get("marital_status") == "married":
            return await message.reply_text(f"❌ {target.mention} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴍᴀʀʀɪᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if proposer_data["balance"] < PROPOSE_COST:
            return await message.reply_text(f"⚠️ ʏᴏᴜ ɴᴇᴇᴅ {fmt_amount(PROPOSE_COST)} ᴛᴏ ᴘʀᴏᴘᴏꜱᴇ.", parse_mode=enums.ParseMode.HTML)

        _pending_proposals[target.id] = proposer.id

        await message.reply_text(
            f"💍 {proposer.mention} ʜᴀꜱ ᴘʀᴏᴘᴏꜱᴇᴅ ᴛᴏ {target.mention}!",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ ᴀᴄᴄᴇᴘᴛ", callback_data=f"propose_accept|{proposer.id}|{target.id}", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"propose_reject|{proposer.id}|{target.id}", style=ButtonStyle.DANGER),
            ]])
        )

    @app.on_callback_query(filters.regex(r"^propose_accept\|(\d+)\|(\d+)$"))
    async def propose_accept_cb(client, callback_query: CallbackQuery):
        proposer_id, target_id = int(callback_query.matches[0].group(1)), int(callback_query.matches[0].group(2))
        if callback_query.from_user.id != target_id:
            return await callback_query.answer("❌ ᴏɴʟʏ ᴛʜᴇ ᴘʀᴏᴘᴏꜱᴇᴅ ᴜꜱᴇʀ ᴄᴀɴ ʀᴇꜱᴘᴏɴᴅ.", show_alert=True)
        if _pending_proposals.get(target_id) != proposer_id:
            return await callback_query.answer("⚠️ ᴛʜɪꜱ ᴘʀᴏᴘᴏꜱᴀʟ ɪꜱ ɴᴏ ʟᴏɴɢᴇʀ ᴠᴀʟɪᴅ.", show_alert=True)

        proposer_data = await db.get_eco_user(proposer_id)
        if proposer_data["balance"] < PROPOSE_COST:
            _pending_proposals.pop(target_id, None)
            return await callback_query.answer("⚠️ ᴘʀᴏᴘᴏꜱᴇʀ ɴᴏ ʟᴏɴɢᴇʀ ʜᴀꜱ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ.", show_alert=True)

        await db.update_balance(proposer_id, -PROPOSE_COST)
        target_name = callback_query.from_user.mention
        proposer_name = (await client.get_users(proposer_id)).mention

        await db.set_marriage(proposer_id, target_id, callback_query.from_user.first_name)
        await db.set_marriage(target_id, proposer_id, (await client.get_users(proposer_id)).first_name)
        _pending_proposals.pop(target_id, None)

        await callback_query.message.edit_text(
            f"💒 {proposer_name} ᴀɴᴅ {target_name} ᴀʀᴇ ɴᴏᴡ ᴍᴀʀʀɪᴇᴅ! 🎉",
            parse_mode=enums.ParseMode.HTML
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^propose_reject\|(\d+)\|(\d+)$"))
    async def propose_reject_cb(client, callback_query: CallbackQuery):
        proposer_id, target_id = int(callback_query.matches[0].group(1)), int(callback_query.matches[0].group(2))
        if callback_query.from_user.id != target_id:
            return await callback_query.answer("❌ ᴏɴʟʏ ᴛʜᴇ ᴘʀᴏᴘᴏꜱᴇᴅ ᴜꜱᴇʀ ᴄᴀɴ ʀᴇꜱᴘᴏɴᴅ.", show_alert=True)
        _pending_proposals.pop(target_id, None)
        await callback_query.message.edit_text("💔 ᴘʀᴏᴘᴏꜱᴀʟ ʀᴇᴊᴇᴄᴛᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        await callback_query.answer()

    # ==========================================================
    # /divorce
    # ==========================================================
    @app.on_message(filters.command("divorce"))
    async def divorce_cmd(client, message: Message):
        user_id = message.from_user.id
        data = await db.get_eco_user(user_id)
        if data.get("marital_status") != "married" or not data.get("spouse_id"):
            return await message.reply_text("❌ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴍᴀʀʀɪᴇᴅ.", parse_mode=enums.ParseMode.HTML)
        if data["balance"] < DIVORCE_COST:
            return await message.reply_text(f"⚠️ ʏᴏᴜ ɴᴇᴇᴅ {fmt_amount(DIVORCE_COST)} ᴛᴏ ᴅɪᴠᴏʀᴄᴇ.", parse_mode=enums.ParseMode.HTML)

        spouse_id = data["spouse_id"]
        await db.update_balance(user_id, -DIVORCE_COST)
        await db.set_marriage(user_id, None, None)
        await db.set_marriage(spouse_id, None, None)

        await message.reply_text(f"💔 ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴅɪᴠᴏʀᴄᴇᴅ. (-{fmt_amount(DIVORCE_COST)})", parse_mode=enums.ParseMode.HTML)
