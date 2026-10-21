# ============================================================
# Economy Game System — Bank
# Author: Mr. Stark
# ============================================================
import time
from pyrogram import enums, filters, Client
from pyrogram.types import Message
from handlers.eco_data import fmt_amount
import db

MAX_LOAN = 10000
DEPOSIT_DAILY_RATE = 0.01   # 1% per day
LOAN_DAILY_RATE = 0.02      # 2% per day


async def apply_interest(user_id: int) -> dict:
    data = await db.get_eco_user(user_id)
    last = data.get("bank_updated_at", 0)
    now = int(time.time())

    if last == 0:
        await db.set_bank(user_id, updated_at=now)
        return await db.get_eco_user(user_id)

    days_passed = (now - last) // 86400
    if days_passed >= 1:
        deposit = data.get("bank_deposit", 0) * ((1 + DEPOSIT_DAILY_RATE) ** days_passed)
        loan = data.get("bank_loan", 0) * ((1 + LOAN_DAILY_RATE) ** days_passed)
        await db.set_bank(user_id, deposit=int(deposit), loan=int(loan), updated_at=last + days_passed * 86400)
        data = await db.get_eco_user(user_id)
    return data


def register_bank_handler(app: Client):

    # ==========================================================
    # /deposit <amount>
    # ==========================================================
    @app.on_message(filters.command("deposit"))
    async def deposit_cmd(client, message: Message):
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/deposit &lt;ᴀᴍᴏᴜɴᴛ&gt;</code>", parse_mode=enums.ParseMode.HTML)
        amount = int(parts[1].strip())

        data = await apply_interest(user_id)
        if data["balance"] < amount:
            return await message.reply_text("⚠️ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.", parse_mode=enums.ParseMode.HTML)

        remaining = amount
        loan = data.get("bank_loan", 0)
        if loan > 0:
            paid = min(loan, remaining)
            loan -= paid
            remaining -= paid
            await db.set_bank(user_id, loan=loan)

        if remaining > 0:
            new_deposit = data.get("bank_deposit", 0) + remaining
            await db.set_bank(user_id, deposit=new_deposit)

        await db.update_balance(user_id, -amount)

        note = ""
        if loan != data.get("bank_loan", 0) or amount - remaining > 0:
            note = f"\n(➻ {fmt_amount(amount - remaining)} ᴜꜱᴇᴅ ᴛᴏ ʀᴇᴘᴀʏ ʟᴏᴀɴ ꜰɪʀꜱᴛ)"
        await message.reply_text(f"🏦 ᴅᴇᴘᴏꜱɪᴛᴇᴅ {fmt_amount(amount)}.{note}", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /loan <amount>
    # ==========================================================
    @app.on_message(filters.command("loan"))
    async def loan_cmd(client, message: Message):
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text(f"⚙️ ᴜꜱᴀɢᴇ: <code>/loan &lt;ᴀᴍᴏᴜɴᴛ&gt;</code> (ᴍᴀx {fmt_amount(MAX_LOAN)})", parse_mode=enums.ParseMode.HTML)
        amount = int(parts[1].strip())

        data = await apply_interest(user_id)
        current_loan = data.get("bank_loan", 0)
        if current_loan + amount > MAX_LOAN:
            return await message.reply_text(f"⚠️ ᴍᴀx ʟᴏᴀɴ ɪꜱ {fmt_amount(MAX_LOAN)}. ʏᴏᴜ ᴄᴀɴ ʙᴏʀʀᴏᴡ ᴜᴘ ᴛᴏ {fmt_amount(MAX_LOAN - current_loan)} ᴍᴏʀᴇ.", parse_mode=enums.ParseMode.HTML)

        await db.set_bank(user_id, loan=current_loan + amount)
        await db.update_balance(user_id, amount)
        await message.reply_text(f"🏦 ʟᴏᴀɴ ᴏꜰ {fmt_amount(amount)} ᴀᴘᴘʀᴏᴠᴇᴅ (+2%/ᴅᴀʏ ɪɴᴛᴇʀᴇꜱᴛ).", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /repay <amount>
    # ==========================================================
    @app.on_message(filters.command("repay"))
    async def repay_cmd(client, message: Message):
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return await message.reply_text("⚙️ ᴜꜱᴀɢᴇ: <code>/repay &lt;ᴀᴍᴏᴜɴᴛ&gt;</code>", parse_mode=enums.ParseMode.HTML)
        amount = int(parts[1].strip())

        data = await apply_interest(user_id)
        loan = data.get("bank_loan", 0)
        if loan <= 0:
            return await message.reply_text("✅ ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ ᴏᴜᴛꜱᴛᴀɴᴅɪɴɢ ʟᴏᴀɴ.", parse_mode=enums.ParseMode.HTML)
        if data["balance"] < amount:
            return await message.reply_text("⚠️ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.", parse_mode=enums.ParseMode.HTML)

        pay = min(amount, loan)
        await db.set_bank(user_id, loan=loan - pay)
        await db.update_balance(user_id, -pay)
        await message.reply_text(f"✅ ʀᴇᴘᴀɪᴅ {fmt_amount(pay)}. ʀᴇᴍᴀɪɴɪɴɢ ʟᴏᴀɴ: {fmt_amount(loan - pay)}", parse_mode=enums.ParseMode.HTML)

    # ==========================================================
    # /bank — show status
    # ==========================================================
    @app.on_message(filters.command("bank"))
    async def bank_cmd(client, message: Message):
        user_id = message.from_user.id
        data = await apply_interest(user_id)
        await message.reply_text(
            f"🏦 <b>ʙᴀɴᴋ ꜱᴛᴀᴛᴜꜱ</b>\n\n"
            f"➻ ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ: <code>{fmt_amount(data['balance'])}</code>\n"
            f"➻ ᴅᴇᴘᴏꜱɪᴛ: <code>{fmt_amount(data.get('bank_deposit', 0))}</code> (+1%/ᴅᴀʏ)\n"
            f"➻ ʟᴏᴀɴ: <code>{fmt_amount(data.get('bank_loan', 0))}</code> (+2%/ᴅᴀʏ)",
            parse_mode=enums.ParseMode.HTML
        )
