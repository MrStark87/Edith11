# ============================================================
# Group Manager Bot — Database
# Author: Mr. Stark
# ============================================================

import motor.motor_asyncio
from config import MONGO_URI, DB_NAME
import logging

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

logging.info("✅ MongoDB initialized")

# ==========================================================
# 🟢 Welcome (original)
# ==========================================================

async def set_welcome_message(chat_id, text: str):
    await db.welcome.update_one({"chat_id": chat_id}, {"$set": {"message": text}}, upsert=True)

async def get_welcome_message(chat_id):
    data = await db.welcome.find_one({"chat_id": chat_id})
    return data.get("message") if data else None

async def set_welcome_status(chat_id, status: bool):
    await db.welcome.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_welcome_status(chat_id) -> bool:
    data = await db.welcome.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", True)) if data else True

# ==========================================================
# 🔒 Lock (original)
# ==========================================================

async def set_lock(chat_id, lock_type, status: bool):
    await db.locks.update_one({"chat_id": chat_id}, {"$set": {f"locks.{lock_type}": status}}, upsert=True)

async def get_locks(chat_id):
    data = await db.locks.find_one({"chat_id": chat_id})
    return data.get("locks", {}) if data else {}

# ==========================================================
# ⚠️ Warn — UPDATED (reason + limit + action support)
# ==========================================================

async def add_warn(chat_id: int, user_id: int, reason: str = None) -> int:
    data    = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    count   = (data.get("count", 0) if data else 0) + 1
    reasons = (data.get("reasons", []) if data else [])
    reasons.append(reason or "")
    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count, "reasons": reasons}},
        upsert=True
    )
    return count

async def get_warns(chat_id: int, user_id: int) -> int:
    data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    return data.get("count", 0) if data else 0

async def get_warns_detailed(chat_id: int, user_id: int) -> dict:
    data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id}, {"_id": 0})
    return data if data else {"count": 0, "reasons": []}

async def reset_warns(chat_id: int, user_id: int):
    await db.warns.delete_one({"chat_id": chat_id, "user_id": user_id})

async def set_warns_direct(chat_id: int, user_id: int, count: int, reasons: list):
    if count <= 0:
        await db.warns.delete_one({"chat_id": chat_id, "user_id": user_id})
    else:
        await db.warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count, "reasons": reasons}},
            upsert=True
        )

async def set_warn_limit(chat_id: int, limit: int):
    await db.warn_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True
    )

async def get_warn_limit(chat_id: int) -> int:
    data = await db.warn_settings.find_one({"chat_id": chat_id}, {"_id": 0})
    return data.get("limit", 3) if data else 3

async def set_warn_action(chat_id: int, action: str):
    await db.warn_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"action": action}}, upsert=True
    )

async def get_warn_action(chat_id: int) -> str:
    data = await db.warn_settings.find_one({"chat_id": chat_id}, {"_id": 0})
    return data.get("action", "mute") if data else "mute"

# ==========================================================
# 🧹 Group data (original)
# ==========================================================

async def clear_group_data(chat_id: int):
    for col in [db.welcome, db.locks, db.warns, db.notes, db.rules]:
        await col.delete_many({"chat_id": chat_id})

# ==========================================================
# 👤 Users (original)
# ==========================================================

async def add_user(user_id, first_name):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"first_name": first_name}},
        upsert=True
    )

async def get_all_users() -> list:
    users = []
    async for doc in db.users.find({}, {"_id": 0, "user_id": 1}):
        if "user_id" in doc:
            users.append(doc["user_id"])
    return users

# ==========================================================
# 📊 Chats (for /stats)
# ==========================================================

async def add_chat(chat_id: int, chat_title: str):
    await db.chats.update_one(
        {"chat_id": chat_id}, {"$set": {"title": chat_title}}, upsert=True
    )

async def get_all_chats() -> list:
    chats = []
    async for doc in db.chats.find({}, {"_id": 0, "chat_id": 1}):
        if "chat_id" in doc:
            chats.append(doc["chat_id"])
    return chats

# ==========================================================
# 🔗 BioLink (original)
# ==========================================================

async def set_biolink_status(chat_id: int, status: bool):
    await db.biolink.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_biolink_status(chat_id: int) -> bool:
    data = await db.biolink.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_bioconfig(chat_id: int, action: str, warn_limit: int):
    await db.bioconfig.update_one(
        {"chat_id": chat_id},
        {"$set": {"action": action, "warn_limit": warn_limit}},
        upsert=True
    )

async def get_bioconfig(chat_id: int) -> dict:
    data = await db.bioconfig.find_one({"chat_id": chat_id})
    return data if data else {"action": "delete", "warn_limit": 0}

async def add_biolink_warn(chat_id: int, user_id: int) -> int:
    data  = await db.biolink_warns.find_one({"chat_id": chat_id, "user_id": user_id})
    count = data.get("count", 0) + 1 if data else 1
    await db.biolink_warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )
    return count

async def reset_biolink_warns(chat_id: int, user_id: int):
    await db.biolink_warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": 0}},
        upsert=True
    )

# ==========================================================
# 📝 Notes — UPDATED (media support)
# ==========================================================

async def set_note(chat_id: int, name: str, content: str,
                   note_type: str = "text", file_id: str = None):
    await db.notes.update_one(
        {"chat_id": chat_id, "name": name.lower()},
        {"$set": {"content": content, "type": note_type, "file_id": file_id}},
        upsert=True
    )

async def get_note(chat_id: int, name: str):
    data = await db.notes.find_one(
        {"chat_id": chat_id, "name": name.lower()}, {"_id": 0}
    )
    return data if data else None

async def delete_note(chat_id: int, name: str) -> bool:
    result = await db.notes.delete_one({"chat_id": chat_id, "name": name.lower()})
    return result.deleted_count > 0

async def get_all_notes(chat_id: int) -> list:
    names = []
    async for doc in db.notes.find({"chat_id": chat_id}, {"name": 1}):
        names.append(doc["name"])
    return sorted(names)

# ==========================================================
# 📜 Rules (original)
# ==========================================================

async def set_rules(chat_id: int, text: str):
    await db.rules.update_one({"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True)

async def get_rules(chat_id: int):
    data = await db.rules.find_one({"chat_id": chat_id})
    return data.get("text") if data else None

async def clear_rules(chat_id: int):
    await db.rules.delete_one({"chat_id": chat_id})

# ==========================================================
# 🤬 Abuse (original)
# ==========================================================

async def set_abuse_status(chat_id: int, status: bool):
    await db.abuse.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_abuse_status(chat_id: int) -> bool:
    data = await db.abuse.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

# ==========================================================
# 🔗 FSub (original + invite links)
# ==========================================================

async def add_fsub_channel(chat_id: int, channel_id: str):
    await db.fsub.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"channels": str(channel_id)}},
        upsert=True
    )

async def remove_fsub_channel(chat_id: int, channel_id: str) -> bool:
    result = await db.fsub.update_one(
        {"chat_id": chat_id},
        {"$pull": {"channels": str(channel_id)}}
    )
    return result.modified_count > 0

async def get_fsub_channels(chat_id: int) -> list:
    data = await db.fsub.find_one({"chat_id": chat_id})
    return data.get("channels", []) if data else []

async def set_fsub_invite_link(chat_id: int, channel_id: str, link: str):
    await db.fsub_links.update_one(
        {"chat_id": chat_id, "channel_id": str(channel_id)},
        {"$set": {"invite_link": link}},
        upsert=True
    )

async def get_fsub_invite_link(chat_id: int, channel_id: str):
    data = await db.fsub_links.find_one(
        {"chat_id": chat_id, "channel_id": str(channel_id)}
    )
    return data.get("invite_link") if data else None

async def remove_fsub_invite_link(chat_id: int, channel_id: str):
    await db.fsub_links.delete_one({"chat_id": chat_id, "channel_id": str(channel_id)})

# ==========================================================
# 📏 Long message (original)
# ==========================================================

async def set_longmode(chat_id, mode):
    await db.longmsg.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def get_longmode(chat_id):
    data = await db.longmsg.find_one({"chat_id": chat_id})
    return data.get("mode", "off") if data else "off"

async def set_longlimit(chat_id, limit):
    await db.longmsg.update_one({"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)

async def get_longlimit(chat_id):
    data = await db.longmsg.find_one({"chat_id": chat_id})
    return data.get("limit", 800) if data else 800

# ==========================================================
# 📵 Phone / Hashtag (original)
# ==========================================================

async def set_nophone_status(chat_id, status):
    await db.nophone.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_nophone_status(chat_id):
    data = await db.nophone.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_nohashtag_status(chat_id, status):
    await db.nohashtag.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_nohashtag_status(chat_id):
    data = await db.nohashtag.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

# ==========================================================
# 🗑️ Cmd Deleter (original)
# ==========================================================

async def set_cmddeleter_status(chat_id: int, status: bool):
    await db.cmddeleter.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_cmddeleter_status(chat_id: int) -> bool:
    data = await db.cmddeleter.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

# ==========================================================
# 🎬 Media Delete (original)
# ==========================================================

async def set_mediadelete_status(chat_id: int, status: bool):
    await db.mediadelete.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_mediadelete_status(chat_id: int) -> bool:
    data = await db.mediadelete.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_mediadelay(chat_id: int, seconds: int):
    await db.mediadelete.update_one({"chat_id": chat_id}, {"$set": {"delay": seconds}}, upsert=True)

async def get_mediadelay(chat_id: int) -> int:
    data = await db.mediadelete.find_one({"chat_id": chat_id})
    return data.get("delay", 300) if data else 300

# ==========================================================
# 🧹 Cleaner (original)
# ==========================================================

async def set_cleaner_status(chat_id: int, status: bool):
    await db.cleaner.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_cleaner_status(chat_id: int) -> bool:
    data = await db.cleaner.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_cleandelay(chat_id: int, seconds: int):
    await db.cleaner.update_one({"chat_id": chat_id}, {"$set": {"delay": seconds}}, upsert=True)

async def get_cleandelay(chat_id: int) -> int:
    data = await db.cleaner.find_one({"chat_id": chat_id})
    return data.get("delay", 300) if data else 300

# ==========================================================
# 🚫 Blacklist words (original)
# ==========================================================

async def add_blacklist_word(chat_id: int, word: str):
    await db.blacklist.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"words": word.lower()}},
        upsert=True
    )

async def remove_blacklist_word(chat_id: int, word: str) -> bool:
    result = await db.blacklist.update_one(
        {"chat_id": chat_id},
        {"$pull": {"words": word.lower()}}
    )
    return result.modified_count > 0

async def get_blacklist(chat_id: int) -> list:
    data = await db.blacklist.find_one({"chat_id": chat_id})
    return data.get("words", []) if data else []

# ==========================================================
# 🤿 Filters (original)
# ==========================================================

async def set_filter(chat_id: int, keyword: str, content_type: str, content: str, file_id: str):
    await db.filters.update_one(
        {"chat_id": chat_id, "keyword": keyword.lower()},
        {
            "$set": {
                "content_type": content_type,
                "content": content,
                "file_id": file_id,
            }
        },
        upsert=True,
    )


async def get_all_filters(chat_id: int) -> dict:
    filters = {}
    async for doc in db.filters.find({"chat_id": chat_id}):
        keyword = doc.get("keyword")
        if keyword:
            filters[keyword] = doc
    return filters

# ==========================================================
# ⛩️ Join Request (original)
# ==========================================================

async def set_acceptall_status(chat_id: int, status: bool):
    await db.joinrequest.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_acceptall_status(chat_id: int) -> bool:
    data = await db.joinrequest.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_jr_notification_status(chat_id: int, status: bool):
    await db.joinrequest.update_one({"chat_id": chat_id}, {"$set": {"notify": status}}, upsert=True)

async def get_jr_notification_status(chat_id: int) -> bool:
    data = await db.joinrequest.find_one({"chat_id": chat_id})
    return bool(data.get("notify", False)) if data else False

# ==========================================================
# 👻 Ghost (original)
# ==========================================================

async def set_ghost_status(chat_id: int, status: bool):
    await db.ghost.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_ghost_status(chat_id: int) -> bool:
    data = await db.ghost.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

# ==========================================================
# 🛡️ Anti Raid (original)
# ==========================================================

async def set_antiraid_status(chat_id: int, status: bool):
    await db.antiraid.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_antiraid_status(chat_id: int) -> bool:
    data = await db.antiraid.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_raiddelay(chat_id: int, seconds: int):
    await db.antiraid.update_one({"chat_id": chat_id}, {"$set": {"delay": seconds}}, upsert=True)

async def get_raiddelay(chat_id: int) -> int:
    data = await db.antiraid.find_one({"chat_id": chat_id})
    return data.get("delay", 60) if data else 60

# ==========================================================
# 🌊 Anti Flood (new)
# ==========================================================

async def set_antiflood_status(chat_id: int, status: bool):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_antiflood_status(chat_id: int) -> bool:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

async def set_flood_limit(chat_id: int, limit: int):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)

async def get_flood_limit(chat_id: int) -> int:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return data.get("limit", 5) if data else 5

async def set_flood_action(chat_id: int, action: str):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"action": action}}, upsert=True)

async def get_flood_action(chat_id: int) -> str:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return data.get("action", "mute") if data else "mute"

async def set_flood_time(chat_id: int, seconds: int):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"mute_time": seconds}}, upsert=True)

async def get_flood_time(chat_id: int) -> int:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return data.get("mute_time", 0) if data else 0

async def set_flood_mode(chat_id: int, mode: str):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def get_flood_mode(chat_id: int) -> str:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return data.get("mode", "normal") if data else "normal"

async def add_flood_whitelist(chat_id: int, user_id: int):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$addToSet": {"whitelist": user_id}}, upsert=True)

async def remove_flood_whitelist(chat_id: int, user_id: int):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$pull": {"whitelist": user_id}}, upsert=True)

async def get_flood_whitelist(chat_id: int) -> list:
    data = await db.antiflood.find_one({"chat_id": chat_id})
    return data.get("whitelist", []) if data else []

# ==========================================================
# 🤖 AI (original)
# ==========================================================

async def set_ai_status(chat_id: int, status: bool):
    await db.ai.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_ai_status(chat_id: int) -> bool:
    data = await db.ai.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", False)) if data else False

# ==========================================================
# 🚷 Blacklisted Users (original)
# ==========================================================

async def add_blacklisted_user(chat_id: int, user_id: int):
    await db.blacklisted_users.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )

async def remove_blacklisted_user(chat_id: int, user_id: int) -> bool:
    result = await db.blacklisted_users.update_one(
        {"chat_id": chat_id}, {"$pull": {"users": user_id}}
    )
    return result.modified_count > 0

async def get_blacklisted_users(chat_id: int) -> list:
    data = await db.blacklisted_users.find_one({"chat_id": chat_id})
    return data.get("users", []) if data else []

# ==========================================================
# 💬 Welcome v2 (text + media + url buttons)
# ==========================================================

async def set_welcome_v2(chat_id: int, data: dict):
    await db.welcome_v2.update_one(
        {"chat_id": chat_id},
        {"$set": {
            "chat_id":       chat_id,
            "text":          data.get("text"),
            "media_file_id": data.get("media_file_id"),
            "media_type":    data.get("media_type"),
            "buttons":       data.get("buttons", []),
        }},
        upsert=True
    )

async def get_welcome_v2(chat_id: int):
    return await db.welcome_v2.find_one({"chat_id": chat_id}, {"_id": 0})

async def clear_welcome_v2(chat_id: int):
    await db.welcome_v2.delete_one({"chat_id": chat_id})

# ==========================================================
# 🔗 FSub Invite Links
# ==========================================================

# (already defined above with fsub functions)

# ==========================================================
# 👮 Staff Roles
# ==========================================================

async def set_staff_role(chat_id: int, user_id: int, role: str):
    await db.staff_roles.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"role": role}},
        upsert=True
    )

async def get_staff_role(chat_id: int, user_id: int):
    data = await db.staff_roles.find_one(
        {"chat_id": chat_id, "user_id": user_id}, {"_id": 0}
    )
    return data.get("role") if data else None

async def remove_staff_role(chat_id: int, user_id: int):
    await db.staff_roles.delete_one({"chat_id": chat_id, "user_id": user_id})


# ==========================================================
# 🆘 Admin Tag
# ==========================================================

async def set_admintag_status(chat_id: int, status: bool):
    await db.admintag.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_admintag_status(chat_id: int):
    data = await db.admintag.find_one({"chat_id": chat_id}, {"_id": 0})
    return data.get("enabled") if data else None

# ==========================================================
# 🎭 Anti-Sticker
# ==========================================================

async def set_antisticker_status(chat_id: int, status: bool):
    await db.antisticker.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_antisticker_status(chat_id: int) -> bool:
    data = await db.antisticker.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("enabled", False)) if data else False

async def add_banned_pack(chat_id: int, pack_name: str):
    await db.banned_packs.update_one(
        {"chat_id": chat_id, "pack_name": pack_name.lower()},
        {"$set": {"pack_name": pack_name.lower()}},
        upsert=True
    )

async def remove_banned_pack(chat_id: int, pack_name: str) -> bool:
    r = await db.banned_packs.delete_one(
        {"chat_id": chat_id, "pack_name": pack_name.lower()}
    )
    return r.deleted_count > 0

async def get_banned_packs(chat_id: int) -> list:
    packs = []
    async for doc in db.banned_packs.find({"chat_id": chat_id}, {"_id": 0, "pack_name": 1}):
        packs.append(doc["pack_name"])
    return packs

async def clear_banned_packs(chat_id: int):
    await db.banned_packs.delete_many({"chat_id": chat_id})

# ==========================================================
# 🤖 Captcha
# ==========================================================

async def set_captcha_status(chat_id: int, status: bool):
    await db.captcha_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_captcha_status(chat_id: int) -> bool:
    data = await db.captcha_settings.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("enabled", False)) if data else False

async def set_captcha_timeout(chat_id: int, seconds: int):
    await db.captcha_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"timeout": seconds}}, upsert=True
    )

async def get_captcha_timeout(chat_id: int) -> int:
    data = await db.captcha_settings.find_one({"chat_id": chat_id}, {"_id": 0})
    return data.get("timeout", 300) if data else 300

async def add_captcha_pending(chat_id: int, user_id: int, answer: int, msg_id: int):
    await db.captcha_pending.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"answer": answer, "msg_id": msg_id}},
        upsert=True
    )

async def get_captcha_pending(chat_id: int, user_id: int):
    return await db.captcha_pending.find_one(
        {"chat_id": chat_id, "user_id": user_id}, {"_id": 0}
    )

async def remove_captcha_pending(chat_id: int, user_id: int):
    await db.captcha_pending.delete_one({"chat_id": chat_id, "user_id": user_id})

# ==========================================================
# ↩️ Forward Protection
# ==========================================================

async def set_forwarding_status(chat_id: int, status: bool):
    await db.forwarding.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_forwarding_status(chat_id: int) -> bool:
    data = await db.forwarding.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("enabled", True)) if data else True

# ==========================================================
# 🔡 Fancy Text Protection
# ==========================================================

async def set_fancytext_status(chat_id: int, status: bool):
    await db.fancytext.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_fancytext_status(chat_id: int) -> bool:
    data = await db.fancytext.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("enabled", False)) if data else False

async def set_fancytext_action(chat_id: int, action: str):
    await db.fancytext.update_one(
        {"chat_id": chat_id}, {"$set": {"action": action}}, upsert=True
    )

async def get_fancytext_action(chat_id: int) -> str:
    data = await db.fancytext.find_one({"chat_id": chat_id}, {"_id": 0})
    return data.get("action", "delete") if data else "delete"



# ==========================================================
# 🔗 Anti-Link
# ==========================================================

async def set_nolink_status(chat_id: int, status: bool):
    await db.nolink.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True
    )

async def get_nolink_status(chat_id: int) -> bool:
    data = await db.nolink.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("enabled", False)) if data else False

async def set_linkwarn_status(chat_id: int, status: bool):
    await db.nolink.update_one(
        {"chat_id": chat_id}, {"$set": {"warn": status}}, upsert=True
    )

async def get_linkwarn_status(chat_id: int) -> bool:
    data = await db.nolink.find_one({"chat_id": chat_id}, {"_id": 0})
    return bool(data.get("warn", False)) if data else False

async def add_allowed_link(chat_id: int, domain: str):
    await db.link_allowed.update_one(
        {"chat_id": chat_id, "domain": domain.lower()},
        {"$set": {"domain": domain.lower()}}, upsert=True
    )

async def remove_allowed_link(chat_id: int, domain: str):
    await db.link_allowed.delete_one({"chat_id": chat_id, "domain": domain.lower()})

async def get_allowed_links(chat_id: int) -> list:
    domains = []
    async for doc in db.link_allowed.find({"chat_id": chat_id}, {"_id": 0, "domain": 1}):
        domains.append(doc["domain"])
    return domains

async def add_blocked_link(chat_id: int, domain: str):
    await db.link_blocked.update_one(
        {"chat_id": chat_id, "domain": domain.lower()},
        {"$set": {"domain": domain.lower()}}, upsert=True
    )

async def remove_blocked_link(chat_id: int, domain: str):
    await db.link_blocked.delete_one({"chat_id": chat_id, "domain": domain.lower()})

async def get_blocked_links(chat_id: int) -> list:
    domains = []
    async for doc in db.link_blocked.find({"chat_id": chat_id}, {"_id": 0, "domain": 1}):
        domains.append(doc["domain"])
    return domains

# Auto Lock
async def set_autolock_hour(chat_id, hour):
    await db.autolock.update_one({"chat_id": chat_id}, {"$set": {"lock_hour": hour}}, upsert=True)

async def set_autounlock_hour(chat_id, hour):
    await db.autolock.update_one({"chat_id": chat_id}, {"$set": {"unlock_hour": hour}}, upsert=True)

async def get_autolock_hour(chat_id):
    data = await db.autolock.find_one({"chat_id": chat_id})
    return data.get("lock_hour") if data else None

async def get_autounlock_hour(chat_id):
    data = await db.autolock.find_one({"chat_id": chat_id})
    return data.get("unlock_hour") if data else None

async def set_last_lock_date(chat_id, date_str):
    await db.autolock.update_one({"chat_id": chat_id}, {"$set": {"last_lock_date": date_str}}, upsert=True)

async def set_last_unlock_date(chat_id, date_str):
    await db.autolock.update_one({"chat_id": chat_id}, {"$set": {"last_unlock_date": date_str}}, upsert=True)

async def clear_autolock_schedule(chat_id):
    await db.autolock.delete_one({"chat_id": chat_id})

async def get_all_autolock_chats():
    chats = []
    async for doc in db.autolock.find({}):
        chats.append(doc)
    return chats

# Disable Commands
async def disable_command(chat_id, cmd):
    await db.disabled_cmds.update_one({"chat_id": chat_id}, {"$addToSet": {"commands": cmd}}, upsert=True)

async def enable_command(chat_id, cmd) -> bool:
    result = await db.disabled_cmds.update_one({"chat_id": chat_id}, {"$pull": {"commands": cmd}})
    return result.modified_count > 0

async def get_disabled_commands(chat_id) -> list:
    data = await db.disabled_cmds.find_one({"chat_id": chat_id})
    return data.get("commands", []) if data else []


async def approve_user(chat_id: int, user_id: int):
    await db.approved.update_one({"chat_id": chat_id}, {"$addToSet": {"users": user_id}}, upsert=True)

async def unapprove_user(chat_id: int, user_id: int) -> bool:
    result = await db.approved.update_one({"chat_id": chat_id}, {"$pull": {"users": user_id}})
    return result.modified_count > 0

async def is_approved(chat_id: int, user_id: int) -> bool:
    data = await db.approved.find_one({"chat_id": chat_id})
    return user_id in data.get("users", []) if data else False

async def get_approved_users(chat_id: int) -> list:
    data = await db.approved.find_one({"chat_id": chat_id})
    return data.get("users", []) if data else []

# ==========================================================
# 💰 Economy System (new)
# ==========================================================

STARTING_BALANCE = 500

async def get_eco_user(user_id: int) -> dict:
    data = await db.economy.find_one({"user_id": user_id})
    if not data:
        data = {
            "user_id": user_id,
            "balance": STARTING_BALANCE,
            "kills": 0,
            "robbed": 0,
            "status": "alive",
            "protection_until": 0,
            "just_revived": False,
            "inventory": [],
            "bank_deposit": 0,
            "bank_loan": 0,
            "bank_updated_at": 0,
            "marital_status": "single",
            "spouse_id": None,
            "spouse_name": None,
            "last_daily": 0,
            "last_mine": 0,
        }
        await db.economy.insert_one(data)
    return data

async def update_balance(user_id: int, delta: int) -> int:
    await get_eco_user(user_id)
    await db.economy.update_one({"user_id": user_id}, {"$inc": {"balance": delta}})
    data = await db.economy.find_one({"user_id": user_id})
    return data.get("balance", 0)

async def set_eco_status(user_id: int, status: str):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"status": status}}, upsert=True)

async def set_just_revived(user_id: int, flag: bool):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"just_revived": flag}}, upsert=True)

async def increment_kills(user_id: int):
    await db.economy.update_one({"user_id": user_id}, {"$inc": {"kills": 1}}, upsert=True)

async def increment_robbed(user_id: int):
    await db.economy.update_one({"user_id": user_id}, {"$inc": {"robbed": 1}}, upsert=True)

async def set_protection(user_id: int, until_ts: int):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"protection_until": until_ts}}, upsert=True)

async def add_inventory_item(user_id: int, item: dict):
    await db.economy.update_one({"user_id": user_id}, {"$push": {"inventory": item}}, upsert=True)

async def set_inventory(user_id: int, inventory: list):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"inventory": inventory}}, upsert=True)

async def set_bank(user_id: int, deposit: int = None, loan: int = None, updated_at: int = None):
    update = {}
    if deposit is not None:
        update["bank_deposit"] = deposit
    if loan is not None:
        update["bank_loan"] = loan
    if updated_at is not None:
        update["bank_updated_at"] = updated_at
    if update:
        await db.economy.update_one({"user_id": user_id}, {"$set": update}, upsert=True)

async def set_marriage(user_id: int, spouse_id, spouse_name):
    await db.economy.update_one(
        {"user_id": user_id},
        {"$set": {"marital_status": "married" if spouse_id else "single", "spouse_id": spouse_id, "spouse_name": spouse_name}},
        upsert=True
    )

async def set_last_daily(user_id: int, ts: int):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"last_daily": ts}}, upsert=True)

async def set_last_mine(user_id: int, ts: int):
    await db.economy.update_one({"user_id": user_id}, {"$set": {"last_mine": ts}}, upsert=True)

async def add_eco_group_member(chat_id: int, user_id: int):
    await db.eco_groups.update_one({"chat_id": chat_id}, {"$addToSet": {"members": user_id}}, upsert=True)

async def get_eco_group_leaderboard(chat_id: int, limit: int = 10) -> list:
    doc = await db.eco_groups.find_one({"chat_id": chat_id})
    members = doc.get("members", []) if doc else []
    if not members:
        return []
    cursor = db.economy.find({"user_id": {"$in": members}}).sort("balance", -1).limit(limit)
    return [row async for row in cursor]

async def get_eco_overall_leaderboard(limit: int = 10) -> list:
    cursor = db.economy.find({}).sort("balance", -1).limit(limit)
    return [row async for row in cursor]

# ==========================================================
# 💞 Couple of the Day
# ==========================================================

async def get_couple(chat_id: int, date: str):
    return await db.couples.find_one({"chat_id": chat_id, "date": date})

async def save_couple(chat_id: int, date: str, couple: dict, img_url: str):
    await db.couples.update_one(
        {"chat_id": chat_id, "date": date},
        {"$set": {"c1_id": couple["c1_id"], "c2_id": couple["c2_id"], "image": img_url}},
        upsert=True
    )

async def get_couple_image(chat_id: int, date: str):
    data = await db.couples.find_one({"chat_id": chat_id, "date": date})
    return data.get("image") if data else None
