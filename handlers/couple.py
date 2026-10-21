# ============================================================
# Group Manager Bot — Couple of the Day
# Author: Mr. Stark
# ============================================================

from datetime import datetime, timedelta
import os
import random
import logging

import pytz
import requests
from PIL import Image, ImageDraw
from telegraph import upload_file

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType

import db
from config import BOT_USERNAME

logger = logging.getLogger(__name__)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

FALLBACK_PFP = "https://telegra.ph/file/05aa686cf52fc666184bf.jpg"
BACKGROUND_IMG = "https://telegra.ph/file/96f36504f149e5680741a.jpg"


# ============================================================
# Date helpers (Asia/Kolkata)
# ============================================================

def get_today_date() -> str:
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d/%m/%Y")


def get_tomorrow_date() -> str:
    tz = pytz.timezone("Asia/Kolkata")
    return (datetime.now(tz) + timedelta(days=1)).strftime("%d/%m/%Y")


def download_image(url: str, path: str) -> str:
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
    return path


def register_couple_handler(app: Client):

    @app.on_message(filters.command(["couple", "couples"]))
    async def couple_cmd(client: Client, message: Message):
        if message.chat.type == ChatType.PRIVATE:
            return await message.reply_text("Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

        cid = message.chat.id
        today = get_today_date()
        tomorrow = get_tomorrow_date()

        p1_path = f"{DOWNLOADS_DIR}/pfp_{cid}.png"
        p2_path = f"{DOWNLOADS_DIR}/pfp1_{cid}.png"
        test_image_path = f"{DOWNLOADS_DIR}/test_{cid}.png"
        cppic_path = f"{DOWNLOADS_DIR}/cppic_{cid}.png"

        try:
            is_selected = await db.get_couple(cid, today)

            if not is_selected:
                msg = await message.reply_text("❣️")

                list_of_users = []
                async for m in client.get_chat_members(cid, limit=50):
                    if m.user and not m.user.is_bot and not m.user.is_deleted:
                        list_of_users.append(m.user.id)

                if len(list_of_users) < 2:
                    await msg.delete()
                    return await message.reply_text(
                        "⚠️ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴀᴄᴛɪᴠᴇ ᴍᴇᴍʙᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ ᴛᴏ ᴘɪᴄᴋ ᴀ ᴄᴏᴜᴘʟᴇ."
                    )

                c1_id = random.choice(list_of_users)
                c2_id = random.choice(list_of_users)
                while c1_id == c2_id:
                    c2_id = random.choice(list_of_users)

                photo1 = (await client.get_chat(c1_id)).photo
                photo2 = (await client.get_chat(c2_id)).photo

                n1 = (await client.get_users(c1_id)).mention
                n2 = (await client.get_users(c2_id)).mention

                try:
                    p1 = await client.download_media(photo1.big_file_id, file_name=p1_path)
                except Exception:
                    p1 = download_image(FALLBACK_PFP, p1_path)

                try:
                    p2 = await client.download_media(photo2.big_file_id, file_name=p2_path)
                except Exception:
                    p2 = download_image(FALLBACK_PFP, p2_path)

                img1 = Image.open(p1)
                img2 = Image.open(p2)

                background_image_path = download_image(BACKGROUND_IMG, cppic_path)
                img = Image.open(background_image_path)

                img1 = img1.resize((437, 437))
                img2 = img2.resize((437, 437))

                mask1 = Image.new("L", img1.size, 0)
                ImageDraw.Draw(mask1).ellipse((0, 0) + img1.size, fill=255)

                mask2 = Image.new("L", img2.size, 0)
                ImageDraw.Draw(mask2).ellipse((0, 0) + img2.size, fill=255)

                img1.putalpha(mask1)
                img2.putalpha(mask2)

                img.paste(img1, (116, 160), img1)
                img.paste(img2, (789, 160), img2)
                img.save(test_image_path)

                caption = (
                    f"<b>Tᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ:\n\n"
                    f"{n1} + {n2} = 💚\n\n"
                    f"Nᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow}!!</b>"
                )

                await message.reply_photo(
                    test_image_path,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            text="Aᴅᴅ ᴍᴇ 🌋",
                            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                        )
                    ]]),
                )
                await msg.delete()

                try:
                    uploaded = upload_file(test_image_path)
                    if uploaded:
                        img_url = "https://graph.org/" + uploaded[0]
                        couple = {"c1_id": c1_id, "c2_id": c2_id}
                        await db.save_couple(cid, today, couple, img_url)
                except Exception as e:
                    logger.error(f"ᴛᴇʟᴇɢʀᴀᴘʜ ᴜᴘʟᴏᴀᴅ ᴇʀʀᴏʀ: {e}")

            else:
                msg = await message.reply_text("❣️")
                img_url = is_selected.get("image")
                c1_id = int(is_selected["c1_id"])
                c2_id = int(is_selected["c2_id"])
                c1_name = (await client.get_users(c1_id)).first_name
                c2_name = (await client.get_users(c2_id)).first_name

                caption = (
                    f"<b>Tᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ 🎉:\n\n"
                    f"<a href='tg://openmessage?user_id={c1_id}'>{c1_name}</a> + "
                    f"<a href='tg://openmessage?user_id={c2_id}'>{c2_name}</a> = ❣️\n\n"
                    f"Nᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow}!!</b>"
                )

                if img_url:
                    await message.reply_photo(
                        img_url,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                text="Aᴅᴅ ᴍᴇ🌋",
                                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                            )
                        ]]),
                    )
                else:
                    await message.reply_text(caption)
                await msg.delete()

        except Exception as e:
            logger.error(f"ᴄᴏᴜᴘʟᴇ ᴄᴏᴍᴍᴀɴᴅ ᴇʀʀᴏʀ ɪɴ {cid}: {e}")
            await message.reply_text(f"❌ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ: {e}")

        finally:
            for path in (p1_path, p2_path, test_image_path, cppic_path):
                try:
                    os.remove(path)
                except Exception:
                    pass
