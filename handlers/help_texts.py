# ============================================================
# Group Manager Bot — ALL HELP TEXTS (one file, grid / table format)
# Author: Mr. Stark
#
# Har help page yaha likha hai. Koi text badalna ho to sirf
# is file mein badlo — start.py ko chhedne ki zaroorat nahi.
#
# Page format:
#   "callback_key": {
#       "title": "🔮 Page Title",
#       "intro": "optional one-line description",
#       "tables": [
#           (caption_or_None, HEADERS, [ (col1, col2), ... ]),
#       ],
#   }
#
# Rich Messages (Telegram Bot API 10.1+) ke <table> mein render hota hai.
# ============================================================

import html

# ---------- column headers ----------
CMD = ("Command", "Description")      # first column monospace hota hai
ITEM = ("Item", "Details")
STEP = ("Step", "What happens")
NOTES = ("Notes",)                    # single column

# In headers ka pehla column <code> (monospace) mein dikhega
_CODE_FIRST = {"Command", "Placeholder", "Example", "Format", "Type", "Mode"}


def _p(title, tables, intro=""):
    return {"title": title, "intro": intro, "tables": tables}


PAGES = {

    # ==================== MODERATION ====================
    "moderation": _p("⚙️ Moderation", [
        (None, CMD, [
            ("/kick", "Remove a user"),
            ("/ban", "Ban permanently"),
            ("/unban", "Lift a ban"),
            ("/mute", "Disable messages"),
            ("/unmute", "Allow messages again"),
            ("/tmute <time>", "Temp mute (1m–24h)"),
            ("/tban <time>", "Temp ban (1m–24h)"),
            ("/dkick", "Kick by reply + delete message"),
            ("/skick", "Silent kick + delete command"),
            ("/dmute", "Mute + delete message"),
            ("/dban", "Ban + delete message"),
            ("/dwarn", "Warn + delete message"),
        ]),
    ]),

    "warns_help": _p("⚠️ Warn System", [
        (None, CMD, [
            ("/warn [reason]", "Warn a user"),
            ("/dwarn", "Warn + delete their message"),
            ("/warns", "View warn history"),
            ("/unwarn", "Remove 1 warn"),
            ("/resetwarns", "Clear all warns"),
            ("/setwarnlimit [1-10]", "Set warn limit"),
            ("/setwarnaction mute|kick|ban", "Set warn action"),
        ]),
        ("Notes", ITEM, [
            ("Default limit", "3 warns"),
            ("Default action", "Mute"),
            ("Reset", "Warns reset after action is taken"),
            ("History", "Last 5 reasons shown in /warns"),
        ]),
    ]),

    "blackuser_help": _p("🚷 Blacklisted Users", [
        (None, CMD, [
            ("/blackuser <userid>", "Add user to blacklist"),
            ("/rmblackuser <userid>", "Remove from blacklist"),
            ("/blacklistusers", "See all blacklisted users"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Only admins can configure this"),
            ("Admins", "Never affected"),
        ]),
    ], intro="Blacklisted users have all their messages deleted automatically — text, media, stickers, GIFs, everything."),

    "blacklist_help": _p("🚫 Blacklist", [
        (None, CMD, [
            ("/addblack <word>", "Add word to blacklist"),
            ("/rmblack <word>", "Remove from blacklist"),
            ("/blacklist", "List all blacklisted words"),
        ]),
        ("Notes", ITEM, [
            ("Purpose", "Keep your group clean and safe"),
        ]),
    ]),

    "abuse_help": _p("🤬 Abuse Detection", [
        (None, CMD, [
            ("/noabuse on", "Enable protection"),
            ("/noabuse off", "Disable protection"),
        ]),
        ("Notes", ITEM, [
            ("Action", "Message deleted instantly"),
            ("Warning", "5-second warning sent"),
            ("Admins", "Not affected"),
        ]),
    ], intro="Abusive messages are automatically deleted."),

    "cmd_help": _p("🗑️ Cmd Deleter", [
        (None, CMD, [
            ("/cmd on", "Enable"),
            ("/cmd off", "Disable"),
        ]),
        ("Notes", ITEM, [
            ("Deletes", "Commands starting with / ! ."),
            ("Admins", "Not affected"),
        ]),
    ]),

    "mediadelete_help": _p("🎬 Media Auto-Delete", [
        (None, CMD, [
            ("/mediadelete on", "Enable"),
            ("/mediadelete off", "Disable"),
            ("/setmediadelay <time>", "Set delay"),
        ]),
        ("Notes", ITEM, [
            ("Affects", "Photos, videos, stickers, GIFs"),
            ("Delay range", "1m to 24h"),
            ("Default", "5m"),
        ]),
    ]),

    "admin_tag_help": _p("🆘 Admin Tag System", [
        ("How To Use", ("Type", "Result"), [
            ("@admin", "Tags all admins at once"),
            ("@admins", "Same as @admin"),
        ]),
        ("Admin Commands", CMD, [
            ("/admintag on", "Enable admin tagging"),
            ("/admintag off", "Disable admin tagging"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Available to all group members"),
            ("Bots", "Not tagged"),
            ("Default", "On"),
        ]),
    ]),

    "promote_help": _p("👮 Promote System", [
        ("Roles", ("Command", "Role & powers"), [
            ("/cofounder", "Co-founder — can set cofounders, mods and helpers; can ban users; all admin permissions; appears in /staff list"),
            ("/admin or /promote {name}", "Admin — delete msgs, pin, invite; manage group settings; custom title via command text; appears in /staff list"),
            ("/mod", "Moderator — ban, kick, mute, info commands; no delete message power; appears in /staff list"),
            ("/fullpromote {name}", "Full admin — all permissions enabled; custom title supported"),
        ]),
        ("Other Commands", CMD, [
            ("/demote", "Remove admin rights"),
            ("/staff", "View all staff members"),
        ]),
    ]),

    "longmsg_help": _p("📄 Long Message", [
        (None, CMD, [
            ("/setlongmode off", "No action"),
            ("/setlongmode manual", "Delete + warn"),
            ("/setlongmode automatic", "Delete + link"),
            ("/setlonglimit <200–4000>", "Set limit"),
        ]),
        ("Notes", ITEM, [
            ("Default limit", "800 characters"),
        ]),
    ], intro="Long messages are uploaded to Telegraph and sent as a link automatically."),

    "hashtag_help": _p("🔖 Hashtag Filter", [
        (None, CMD, [
            ("/nohashtags on", "Block"),
            ("/nohashtags off", "Allow"),
        ]),
        ("Notes", ITEM, [
            ("Blocks", "Any word starting with #"),
        ]),
    ], intro="Hashtag messages are automatically deleted."),

    # ==================== SECURITY ====================
    "locks": _p("🔐 Locks System", [
        (None, CMD, [
            ("/lock", "Enable a lock"),
            ("/unlock", "Disable a lock"),
            ("/locks", "Show active locks"),
            ("/lockall", "Lock everything"),
            ("/unlockall", "Unlock everything"),
        ]),
        ("Available Types", NOTES, [
            ("url • text • sticker • media • music",),
            ("username • forward • edit • files • emoji",),
        ]),
    ]),

    "autolock_help": _p("🕐 Auto Lock", [
        (None, CMD, [
            ("/autolock on", "Set daily lock time"),
            ("/autolock off", "Set daily unlock time"),
            ("/autolockstatus", "Show current schedule"),
            ("/autolockclear", "Remove the schedule"),
        ]),
        ("How It Works", NOTES, [
            ("Pick an hour (1–12), then AM/PM",),
            ("At the lock time, everything in the group gets locked automatically",),
            ("At the unlock time, everything reopens automatically",),
            ("If no unlock time is set, admins must unlock manually",),
        ]),
        ("Notes", ITEM, [
            ("Timezone", "All times are in IST (Indian Standard Time)"),
            ("Access", "Only admins can configure this"),
        ]),
    ], intro="Automatically lock and unlock the entire group at scheduled times, every single day."),

    "captcha_help": _p("🤖 Captcha System", [
        (None, CMD, [
            ("/captcha on", "Enable captcha"),
            ("/captcha off", "Disable captcha"),
            ("/captchatime <seconds>", "Set timeout"),
        ]),
        ("How It Works", NOTES, [
            ("New member joins → muted instantly",),
            ("Must solve a math question to unmute",),
            ("Fails or times out → kicked from group",),
        ]),
    ]),

    "biolink": _p("🔗 Biolink Protection", [
        (None, CMD, [
            ("/biolink on", "Enable protection"),
            ("/biolink off", "Disable protection"),
            ("/bioconfig", "Configure action"),
        ]),
        ("Notes", ITEM, [
            ("Bio link detected", "Message deleted"),
            ("Admins", "Not affected"),
            ("Bot permission", "Needs delete messages permission"),
        ]),
    ], intro="Blocks users who have links in their bio."),

    "anti_link_help": _p("🔗 Anti Link System", [
        ("Main Commands", CMD, [
            ("/nolink on", "Block all links"),
            ("/nolink off", "Allow all links"),
        ]),
        ("Whitelist / Blacklist", CMD, [
            ("/allowlink {url}", "Allow specific link"),
            ("/rmallowlink {url}", "Remove from allowed list"),
            ("/blocklink {url}", "Block specific link"),
            ("/rmblocklink {url}", "Remove from blocked list"),
            ("/allowedlinks", "List allowed links"),
            ("/blockedlinks", "List blocked links"),
        ]),
        ("Warn System", CMD, [
            ("/linkwarn on", "Warn + action on limit"),
            ("/linkwarn off", "Only delete + notify"),
        ]),
        ("Notes", ITEM, [
            ("Admins", "Not affected"),
            ("TG links", "Match specific usernames"),
        ]),
    ]),

    "fsub_help": _p("🪠 Force Subscribe", [
        (None, CMD, [
            ("/addfsub @channel or [-100xxxx]", "Add a required channel"),
            ("/removefsub @channel or [-100xxxx]", "Remove a required channel"),
            ("/fsublist", "List channels"),
        ]),
        ("Notes", ITEM, [
            ("Bot", "Must be admin in the channel"),
        ]),
    ], intro="Users who haven't joined the required channels cannot send messages."),

    "cleaner_help": _p("🧹 Message Cleaner", [
        (None, CMD, [
            ("/cleaner on", "Enable"),
            ("/cleaner off", "Disable"),
            ("/setcleandelay <time>", "Set delay"),
            ("/cleanstatus", "Show settings"),
        ]),
        ("Notes", ITEM, [
            ("Admins", "Messages are never deleted"),
            ("Delay range", "1m to 24h"),
            ("Default", "5m"),
        ]),
    ], intro="All regular user messages are deleted automatically after a set delay."),

    "phone_help": _p("📵 Phone Protection", [
        (None, CMD, [
            ("/nophone on", "Block"),
            ("/nophone off", "Allow"),
        ]),
        ("Detected Examples", NOTES, [
            ("+91 9876543210",),
            ("+1-234-567-8900",),
        ]),
    ]),

    "anti_sticker_help": _p("🎭 Anti Sticker", [
        (None, CMD, [
            ("/banpack", "Reply to a sticker to ban its pack"),
            ("/unbanpack <packname>", "Unban a pack"),
            ("/bannedpacks", "List all banned packs"),
            ("/clearbanpacks", "Clear all banned packs"),
            ("/antisticker on", "Block all stickers"),
            ("/antisticker off", "Allow all stickers"),
        ]),
        ("Notes", ITEM, [
            ("/banpack", "Bans the entire pack"),
            ("/antisticker", "Blocks every sticker"),
            ("Admins", "Not affected"),
        ]),
    ]),

    "zombie_help": _p("🧟 Remove Deleted Accounts", [
        (None, CMD, [
            ("/zombie", "Scan and remove all deleted accounts from the group instantly"),
        ]),
        ("Notes", ITEM, [
            ("Bot", "Must be an admin with ban permission"),
            ("Access", "Only admins can use this command"),
            ("Effect", "All deleted Telegram accounts are removed immediately"),
        ]),
    ]),

    "ghost_help": _p("👻 Ghost Mode", [
        (None, CMD, [
            ("/ghostmode on", "Enable ghost mode"),
            ("/ghostmode off", "Disable ghost mode"),
        ]),
        ("What Gets Deleted", NOTES, [
            ("User joined the group",),
            ("User left the group",),
            ("User was removed",),
            ("Group title changed",),
            ("Group photo changed",),
            ("Pinned message notifications",),
            ("Video chat started / ended",),
        ]),
        ("Notes", ITEM, [
            ("Access", "Only admins can configure this"),
        ]),
    ]),

    "filters_help": _p("🤿 Filters", [
        (None, CMD, [
            ("/filter <keyword>", "Reply to a message or sticker to set an auto-reply for that keyword"),
            ("/stopfilter <keyword>", "Remove a filter"),
            ("/filters", "List all active filters"),
        ]),
        ("Notes", ITEM, [
            ("Purpose", "Automate replies and make your group more interactive"),
        ]),
    ]),

    "joinrequest_help": _p("⛩️ Auto Accept – Join Requests", [
        (None, CMD, [
            ("/acceptall on", "Auto accept on"),
            ("/acceptall off", "Auto accept off"),
            ("/notification on", "Notifications on"),
            ("/notification off", "Notifications off"),
        ]),
        ("When Auto Accept Is Off", NOTES, [
            ("Bot sends a join request notification to the group with approve / decline buttons for admins",),
        ]),
        ("Notification System", NOTES, [
            ("If notification is off, no join request message will be sent in the group",),
        ]),
        ("Notes", ITEM, [
            ("Bot", "Must be admin with approval rights"),
            ("Access", "Only admins can use these commands"),
        ]),
    ]),

    "antiraid_help": _p("🛡️ Anti Raid", [
        (None, CMD, [
            ("/antiraid on", "Enable auto mute"),
            ("/antiraid off", "Disable auto mute"),
            ("/raiddelay <time>", "Set mute duration"),
        ]),
        ("Time Format", ("Format", "Meaning"), [
            ("1s, 1m, 1h", "Seconds, minutes, hours"),
            ("0", "Permanent (admin must unmute)"),
        ]),
        ("Examples", ("Example", "Result"), [
            ("/raiddelay 30s", "Mute for 30 seconds"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Only admins can configure this"),
        ]),
    ], intro="New users who join the group are automatically muted for a set time, then unmuted automatically."),

    "antiflood_help": _p("🌊 Anti Flood System", [
        (None, CMD, [
            ("/antiflood on", "Enable"),
            ("/antiflood off", "Disable"),
            ("/setflood {number}", "Messages allowed per 10s"),
            ("/floodaction {mute/kick/ban/warn}", "Action to take"),
            ("/floodtime {time}", "Mute/ban duration"),
            ("/floodmode {strict/normal}", "Detection mode"),
            ("/flood", "View current settings"),
            ("/floodwhitelist {add/remove/list}", "Exempt users"),
        ]),
        ("Modes", ("Mode", "Description"), [
            ("Normal", "Any rapid messages count"),
            ("Strict", "Only repeated / same messages count"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Only admins can configure this"),
        ]),
    ], intro="Users who send too many messages in 10 seconds are automatically actioned."),

    "disable_help": _p("⚙️ Disable Commands", [
        (None, CMD, [
            ("/disable <command>", "Disable a command for members"),
            ("/enable <command>", "Re-enable a command"),
            ("/disabled", "List disabled commands"),
        ]),
        # "Disableable Commands" table render time par disable.py se judta hai
        ("Notes", ITEM, [
            ("Access", "Only admins can configure this"),
        ]),
    ], intro="Block regular members from using specific member-usable commands. Admins are never affected."),

    "fancy_text_help": _p("🪭 Fancy Text Protection", [
        (None, CMD, [
            ("/fancytext on", "Allow fancy text (no action)"),
            ("/fancytext off", "Block fancy text (delete + warn)"),
        ]),
        ("How It Works", ITEM, [
            ("On", "Users can use fancy fonts freely"),
            ("Off", "Fancy text is deleted instantly + user gets a warn"),
            ("Warn limit", "Action is executed automatically when the limit is reached"),
        ]),
    ]),

    # ==================== UTILITY ====================
    "greetings": _p("👋 Welcome System", [
        (None, CMD, [
            ("/welcome on", "Enable welcome"),
            ("/welcome off", "Disable welcome"),
            ("/setwelcome", "Setup via PM (text + media + buttons)"),
            ("/resetwelcome", "Reset to default"),
            ("/previewwelcome", "Preview current welcome"),
        ]),
        ("Placeholders", ("Placeholder", "Meaning"), [
            ("{id}", "User ID"),
            ("{name}", "First name"),
            ("{surname}", "Last name"),
            ("{namesurname}", "Full name"),
            ("{mention}", "Clickable mention"),
            ("{username}", "@username"),
            ("{groupname}", "Group name"),
        ]),
        ("Notes", ITEM, [
            ("/setwelcome", "Opens a PM setup panel"),
            ("Formatting", "HTML formatting supported"),
            ("Content", "Text + media + URL buttons"),
        ]),
    ]),

    "notes_help": _p("📝 Notes System", [
        (None, CMD, [
            ("/save <name> <text>", "Save a note"),
            ("/save <name> (reply)", "Reply to any message or media to save it as a note"),
            ("/get <name> or #name", "View a note"),
            ("/notes", "List all notes"),
            ("/delnote <name>", "Delete a note"),
        ]),
        ("Supported Types", NOTES, [
            ("Text (HTML), photo, video, document, audio, sticker, GIF",),
        ]),
    ]),

    "rules_help": _p("📜 Group Rules", [
        (None, CMD, [
            ("/setrules <text>", "Set group rules"),
            ("/rules", "View rules (anyone)"),
            ("/clearrules", "Delete rules"),
        ]),
        ("Notes", ITEM, [
            ("Formatting", "HTML formatting supported"),
            ("/setrules", "Admin only"),
        ]),
    ]),

    "utility_help": _p("⚙️ Utility", [
        (None, CMD, [
            ("/chatinfo", "Group details & member count"),
            ("/id", "Your ID or replied user's ID"),
            ("/pin [silent]", "Pin a replied message"),
            ("/unpin", "Unpin message or all pins"),
            ("/purge", "Bulk delete messages"),
            ("/del", "Delete a replied message"),
            ("/report", "Report a user to admins"),
            ("/calc <expr>", "Calculator"),
        ]),
        ("Notes", ITEM, [
            ("Admin only", "/pin, /purge, /del"),
        ]),
    ]),

    "tagall_help": _p("🔖 Tag All", [
        (None, CMD, [
            ("/tagall", "Tag all members"),
            ("/tagall {message}", "Tag with custom message"),
            ("/stoptag", "Stop tagging"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Admin only"),
            ("Mention style", "1 emoji = 1 person mention"),
            ("Batch size", "5 people per message"),
            ("Skipped", "Bots & deleted accounts"),
        ]),
    ]),

    "approve_help": _p("🕊 Approve System", [
        (None, CMD, [
            ("/free or /approve", "Approve a user (reply or @user/ID)"),
            ("/unfree or /unapprove", "Remove approval from a user"),
            ("/approved", "List all approved users"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Only admins can approve / unapprove"),
        ]),
    ], intro="Approved users are completely ignored by every automated bot restriction."),

    "forward_help": _p("↩️ Forward Protection", [
        (None, CMD, [
            ("/forwarding on", "Allow forwards"),
            ("/forwarding off", "Block forwards"),
        ]),
        ("How It Works", ITEM, [
            ("On", "All forwards allowed"),
            ("Off", "Forwarded message deleted + warn"),
            ("Warn limit reached", "Ban / kick / mute"),
        ]),
    ]),

    "ai_help": _p("🤖 Edith AI", [
        (None, CMD, [
            ("/ai <question>", "Ask Edith AI"),
            ("/ask <question>", "Same as /ai"),
            (".edith <question>", "Same as /ai"),
        ]),
        ("Group (Admin)", CMD, [
            ("/aifeature on", "Enable AI"),
            ("/aifeature off", "Disable AI"),
        ]),
        ("Examples", NOTES, [
            ("/ai What is Python?",),
            (".edith Mujhe joke batao",),
        ]),
    ]),

    # ==================== GROUPS ====================
    "groupinfo_help": _p("👥 Group Identity", [
        (None, CMD, [
            ("/setname {text}", "Set / change the group name"),
            ("/setbio {text}", "Set / change the group description"),
            ("/groupinfo", "Show group id, owner and member stats"),
            ("/setdp", "Reply to an image to set it as group photo (aliases: /setpfp, /setimage)"),
            ("/link", "Generate a new invite link (aliases: /givelink, /invitelink)"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Admin only, group only"),
            ("Bot rights", "Bot must be admin with Change Group Info and Invite Users rights"),
        ]),
    ]),

    "linkinfo_help": _p("🔗 Invite Link", [
        (None, CMD, [
            ("/link", "Generate a brand new group invite link (aliases: /givelink, /invitelink)"),
        ]),
        ("Notes", ITEM, [
            ("Access", "Admin only"),
            ("Bot rights", "Bot must be admin with Invite Users Via Link right"),
            ("Behavior", "Each run creates a fresh link (doesn't revoke the main one)"),
            ("Where", "Group only, won't work in PM"),
        ]),
    ]),
}


# ============================================================
# Renderers
# ============================================================

def _e(text) -> str:
    return html.escape(str(text), quote=False)


def _tables_for(key):
    """Page ki tables + (disable page ke liye) live disableable list."""
    page = PAGES[key]
    tables = list(page["tables"])
    if key == "disable_help":
        try:
            from handlers.disable import DISABLEABLE_COMMANDS
            tables.insert(1, ("Disableable Commands", NOTES,
                              [(", ".join(DISABLEABLE_COMMANDS),)]))
        except Exception:
            pass
    return tables


def render_rich(key: str) -> str:
    """Rich Message (Bot API 10.1+) HTML — real grid/table."""
    page = PAGES[key]
    tables = _tables_for(key)
    out = []

    first_caption = tables[0][0]
    # Title ko pehli table ka caption bana do (screenshot jaisa look),
    # warna alag heading + intro.
    title_in_caption = (not page["intro"]) and first_caption is None
    if not title_in_caption:
        out.append(f"<h2>{_e(page['title'])}</h2>")
        if page["intro"]:
            out.append(f"<p>{_e(page['intro'])}</p>")

    for i, (caption, headers, rows) in enumerate(tables):
        if i == 0 and title_in_caption:
            caption = page["title"]
        t = ["<table bordered striped>"]
        if caption:
            t.append(f"<caption>{_e(caption)}</caption>")
        t.append("<tr>" + "".join(f"<th>{_e(h)}</th>" for h in headers) + "</tr>")
        code_first = headers[0] in _CODE_FIRST
        for row in rows:
            cells = []
            for n, cell in enumerate(row):
                cell = _e(cell)
                if n == 0 and code_first:
                    cell = f"<code>{cell}</code>"
                cells.append(f"<td>{cell}</td>")
            t.append("<tr>" + "".join(cells) + "</tr>")
        t.append("</table>")
        out.append("".join(t))
    return "\n".join(out)


def render_plain(key: str) -> str:
    """Fallback (normal HTML message) — sirf tab jab rich message na ja sake."""
    page = PAGES[key]
    out = [f"<b>{_e(page['title'])}</b>"]
    if page["intro"]:
        out.append(f"<i>{_e(page['intro'])}</i>")
    for caption, headers, rows in _tables_for(key):
        out.append("")
        if caption:
            out.append(f"<b>{_e(caption)}</b>")
        code_first = headers[0] in _CODE_FIRST
        for row in rows:
            first = _e(row[0])
            if code_first:
                first = f"<code>{first}</code>"
            rest = " — ".join(_e(c) for c in row[1:])
            out.append(f"• {first}" + (f" — {rest}" if rest else ""))
    return "\n".join(out)
