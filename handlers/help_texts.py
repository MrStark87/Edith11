# ============================================================
# Group Manager Bot — ALL HELP TEXTS (central table source)
# Author: Mr. Stark
#
# Har help page yahan edit karein. start.py aur individual handlers
# help screen ka text yahan se render karte hain.
# ============================================================

import html

CMD = ("Command", "Description")
ITEM = ("Item", "Details")
NOTES = ("Notes",)
_CODE_FIRST = {"Command", "Placeholder", "Example", "Format", "Type", "Mode"}


def _p(title, tables, intro=""):
    return {"title": title, "intro": intro, "tables": tables}


PAGES = {
    "moderation": _p("🔮 Moderation", [(None, CMD, [
        ("/kick <user>", "Remove a user"), ("/ban <user>", "Ban a user"),
        ("/unban <user>", "Lift a ban"), ("/mute <user>", "Mute a user"),
        ("/unmute <user>", "Allow messages again"),
        ("/tmute <user> <time>", "Temporarily mute (30s, 10m, 2h, 1d)"),
        ("/tban <user> <time>", "Temporarily ban"),
        ("/dkick", "Reply: kick user and delete their message"),
        ("/skick <user>", "Silently kick and delete command"),
        ("/smute <user>", "Silently mute and delete command"),
        ("/sban <user>", "Silently ban and delete command"),
        ("/dmute", "Reply: mute user and delete their message"),
        ("/dban", "Reply: ban user and delete their message"),
        ("/dwarn [reason]", "Reply: warn user and delete their message"),
    ])]),
    "warns_help": _p("⚠️ Warn System", [
        (None, CMD, [("/warn <user> [reason]", "Warn a user"), ("/dwarn [reason]", "Warn and delete replied message"), ("/warns [user]", "View warning history"), ("/unwarn <user>", "Remove one warning"), ("/resetwarns <user>", "Clear warnings"), ("/setwarnlimit <2-10>", "Set warning limit"), ("/setwarnaction <mute|kick|ban>", "Set action at limit")]),
        ("Notes", ITEM, [("Default limit", "3 warnings"), ("Default action", "Mute"), ("Reset", "Warnings reset after action"), ("History", "Last 5 reasons shown by /warns")]),
    ]),
    "blackuser_help": _p("🚷 Blacklisted Users", [
        (None, CMD, [("/blackuser <user>", "Add user to blacklist"), ("/rmblackuser <user>", "Remove from blacklist"), ("/blacklistusers", "List blacklisted users")]),
        ("Notes", ITEM, [("Access", "Admin only"), ("Effect", "All messages from listed users are deleted"), ("Admins", "Not affected")]),
    ], "Blacklist a user to automatically delete their messages, including text and media."),
    "blacklist_help": _p("🚫 Word Blacklist", [
        (None, CMD, [("/addblack <word>", "Add a word"), ("/rmblack <word>", "Remove a word"), ("/blacklist", "List blacklisted words")]),
        ("Notes", ITEM, [("Purpose", "Keep your group clean and safe")]),
    ]),
    "abuse_help": _p("🤬 Abuse Detection", [
        (None, CMD, [("/noabuse on", "Enable protection"), ("/noabuse off", "Disable protection")]),
        ("Notes", ITEM, [("Action", "Abusive message deleted"), ("Warning", "Temporary warning is sent"), ("Admins", "Not affected")]),
    ], "Abusive messages are automatically deleted."),
    "cmd_help": _p("🗑️ Command Deleter", [
        (None, CMD, [("/cmd on", "Enable auto-delete"), ("/cmd off", "Disable auto-delete")]),
        ("Notes", ITEM, [("Deletes", "Messages starting with /, !, or ."), ("Admins", "Commands are also deleted")]),
    ]),
    "mediadelete_help": _p("🎬 Media Auto-Delete", [
        (None, CMD, [("/mediadelete on", "Enable"), ("/mediadelete off", "Disable"), ("/setmediadelay <time>", "Set deletion delay")]),
        ("Notes", ITEM, [("Affects", "Photos, videos, stickers, GIFs, animations, locations and polls"), ("Delay range", "1m to 24h"), ("Default", "5m")]),
    ]),
    "admin_tag_help": _p("🆘 Admin Tag System", [
        ("How to use", ("Type", "Result"), [("@admin", "Tag group admins"), ("@admins", "Same as @admin")]),
        ("Admin commands", CMD, [("/admintag on", "Enable tagging"), ("/admintag off", "Disable tagging")]),
        ("Notes", ITEM, [("Access", "Available to group members"), ("Bots", "Not tagged"), ("Default", "On")]),
    ]),
    "promote_help": _p("👮 Promote System", [
        ("Roles", ("Command", "Role & powers"), [("/cofounder <user>", "Co-founder: can manage roles and has all admin permissions"), ("/admin or /promote <user> [title]", "Admin: group settings, pin, invite and delete messages"), ("/mod <user>", "Moderator role"), ("/fullpromote <user> [title]", "Full admin permissions and optional custom title")]),
        ("Other commands", CMD, [("/demote <user>", "Remove admin rights"), ("/staff", "List staff members")]),
    ]),
    "longmsg_help": _p("⌛ Long Message", [(None, CMD, [("/echo <text>", "Echo text; long text can be uploaded to Telegraph"), ("/setlongmode off", "Take no action"), ("/setlongmode manual", "Delete and warn"), ("/setlongmode automatic", "Delete and send Telegraph link"), ("/setlonglimit <limit>", "Set character limit")]), ("Notes", ITEM, [("Default limit", "800 characters")])], "Long messages can be uploaded to Telegraph and shared as a link."),
    "hashtag_help": _p("#️⃣ Hashtag Filter", [(None, CMD, [("/nohashtags on", "Block hashtags"), ("/nohashtags off", "Allow hashtags")]), ("Notes", ITEM, [("Detection", "Any word beginning with #")])], "Messages containing hashtags are automatically deleted when enabled."),
    "locks": _p("🔐 Locks System", [(None, CMD, [("/lock <type>", "Enable a lock"), ("/unlock <type>", "Disable a lock"), ("/locks", "Show active locks"), ("/lockall", "Lock all types"), ("/unlockall", "Unlock all types")]), ("Available types", NOTES, [("url • text • sticker • media • music",), ("username • forward • edit • files • emoji",)])]),
    "autolock_help": _p("🕐 Auto Lock", [(None, CMD, [("/autolock on", "Set daily lock time"), ("/autolock off", "Set daily unlock time"), ("/autolockstatus", "Show schedule"), ("/autolockclear", "Remove schedule")]), ("How it works", NOTES, [("Setup", "Choose an hour (1–12), then AM/PM"), ("Schedule", "Group locks and unlocks automatically each day"), ("No unlock time", "Admins must unlock manually")]), ("Notes", ITEM, [("Timezone", "Configured bot timezone (default Asia/Kolkata)"), ("Access", "Admin only")])], "Automatically lock and unlock the entire group on a daily schedule."),
    "captcha_help": _p("🤖 Captcha System", [(None, CMD, [("/captcha on", "Enable captcha"), ("/captcha off", "Disable captcha"), ("/captchatime <seconds>", "Set verification timeout (30–300 seconds)")]), ("How it works", NOTES, [("Join", "New member is muted"), ("Verify", "Solve a math question to unmute"), ("Fail or timeout", "Member is kicked")])]),
    "biolink": _p("🔗 BioLink Protection", [(None, CMD, [("/biolink on", "Enable protection"), ("/biolink off", "Disable protection"), ("/bioconfig", "Configure delete, mute, or ban action")]), ("Notes", ITEM, [("Detection", "Messages from users with links in bio are removed"), ("Admins", "Not affected"), ("Bot permission", "Needs delete-message permission")])], "Blocks messages from users whose bio contains a link."),
    "anti_link_help": _p("🔗 Anti-Link System", [("Main commands", CMD, [("/nolink on", "Block links (allowed-list entries are exempt)"), ("/nolink off", "Disable general link blocking")]), ("Allow/block lists", CMD, [("/allowlink <url>", "Allow a specific link or domain"), ("/rmallowlink <url>", "Remove from allow list"), ("/blocklink <url>", "Block a specific link or domain"), ("/rmblocklink <url>", "Remove from block list"), ("/allowedlinks", "List allowed links"), ("/blockedlinks", "List blocked links")]), ("Warnings", CMD, [("/linkwarn on", "Warn and apply configured action at limit"), ("/linkwarn off", "Delete and notify without warnings")]), ("Notes", ITEM, [("Admins", "Not affected"), ("Telegram links", "Can match specific paths/usernames")])]),
    "fsub_help": _p("🪠 Force Subscribe", [(None, CMD, [("/addfsub @channel or -100…", "Add required channel"), ("/removefsub @channel or -100…", "Remove required channel"), ("/fsublist", "List required channels")]), ("Notes", ITEM, [("Bot", "Must be an admin in the channel")])], "Users must join required channels before sending group messages."),
    "cleaner_help": _p("🧹 Message Cleaner", [(None, CMD, [("/cleaner on", "Enable"), ("/cleaner off", "Disable"), ("/setcleandelay <time>", "Set delay"), ("/cleanstatus", "Show settings")]), ("Notes", ITEM, [("Admins", "Messages are never deleted"), ("Delay range", "1m to 24h"), ("Default", "5m")])], "Regular members' text and media messages are deleted after the configured delay."),
    "phone_help": _p("📵 Phone Protection", [(None, CMD, [("/nophone on", "Block phone-number messages"), ("/nophone off", "Allow phone-number messages")]), ("Examples", NOTES, [("+91 9876543210",), ("+1-234-567-8900",)])]),
    "anti_sticker_help": _p("🎭 Anti Sticker", [(None, CMD, [("/banpack", "Reply to a sticker to ban its pack"), ("/unbanpack <packname>", "Unban a sticker pack"), ("/bannedpacks", "List banned packs"), ("/clearbanpacks", "Clear banned packs"), ("/antisticker on", "Block all stickers"), ("/antisticker off", "Allow stickers")]), ("Notes", ITEM, [("Pack ban", "Bans the entire sticker pack"), ("Admins", "Not affected")])]),
    "zombie_help": _p("🧟 Remove Deleted Accounts", [(None, CMD, [("/zombie", "Scan and remove deleted accounts")]), ("Notes", ITEM, [("Bot", "Must be admin with ban permission"), ("Access", "Admin only")])]),
    "ghost_help": _p("👻 Ghost Mode", [(None, CMD, [("/ghostmode on", "Enable ghost mode"), ("/ghostmode off", "Disable ghost mode")]), ("Deleted service messages", NOTES, [("Member joined, left, or removed",), ("Group title or photo changed",), ("Pinned message notifications",), ("Video chat started or ended",)]), ("Notes", ITEM, [("Access", "Admin only")])]),
    "filters_help": _p("🤿 Filters", [(None, CMD, [("/filter <keyword>", "Reply to a message or sticker to set an auto-reply"), ("/stopfilter <keyword>", "Remove a filter"), ("/filters", "List active filters")])]),
    "joinrequest_help": _p("⛩️ Join Requests", [(None, CMD, [("/acceptall on", "Automatically accept requests"), ("/acceptall off", "Manual approval"), ("/notification on", "Enable notifications"), ("/notification off", "Disable notifications")]), ("Manual mode", NOTES, [("Requests are posted with approve/decline buttons for admins",)]), ("Notes", ITEM, [("Bot", "Needs join-request management permission"), ("Access", "Admin only")])]),
    "antiraid_help": _p("🛡️ Anti Raid", [(None, CMD, [("/antiraid on", "Enable auto-mute for new members"), ("/antiraid off", "Disable auto-mute"), ("/raiddelay <time>", "Set mute duration")]), ("Time format", ("Format", "Meaning"), [("1s, 1m, 1h", "Seconds, minutes, hours"), ("0", "Permanent until manually unmuted")]), ("Notes", ITEM, [("Access", "Admin only")])], "New members are muted for the selected duration, then automatically unmuted."),
    "antiflood_help": _p("🌊 Anti Flood", [(None, CMD, [("/antiflood on|off", "Enable or disable flood detection"), ("/setflood <number>", "Set messages allowed per 10 seconds"), ("/floodaction <mute|kick|ban|warn>", "Choose action"), ("/floodtime <time>", "Set mute/ban duration"), ("/floodmode <strict|normal>", "Choose detection mode"), ("/flood", "Show settings"), ("/floodwhitelist add|remove|list", "Manage exemptions")]), ("Modes", ("Mode", "Description"), [("Normal", "Any rapid messages count"), ("Strict", "Only repeated messages count")]), ("Notes", ITEM, [("Access", "Admin only")])], "Users sending too many messages within 10 seconds are actioned automatically."),
    "disable_help": _p("⚙️ Disable Commands", [(None, CMD, [("/disable <command>", "Disable an eligible command for members"), ("/enable <command>", "Re-enable a command"), ("/disabled", "List disabled commands")]), ("Notes", ITEM, [("Access", "Admin only; admins are not affected")])], "Only member-usable commands can be disabled."),
    "fancy_text_help": _p("🪭 Fancy Text Protection", [(None, CMD, [("/fancytext on", "Allow fancy text"), ("/fancytext off", "Block fancy text and warn")]), ("How it works", ITEM, [("On", "Fancy fonts are allowed"), ("Off", "Fancy text is deleted and a warning is added"), ("Limit", "Configured warning action applies at the limit")])]),
    "greetings": _p("👋 Welcome System", [(None, CMD, [("/welcome on", "Enable welcome messages"), ("/welcome off", "Disable welcome messages"), ("/setwelcome", "Open private setup panel for text, media and buttons"), ("/resetwelcome", "Reset welcome to default"), ("/previewwelcome", "Preview current welcome")]), ("Placeholders", ("Placeholder", "Meaning"), [("{id}", "User ID"), ("{name}", "First name"), ("{surname}", "Last name"), ("{namesurname}", "Full name"), ("{mention}", "Clickable mention"), ("{username}", "Username"), ("{groupname}", "Group name")]), ("Notes", ITEM, [("Formatting", "HTML supported"), ("Content", "Text, media, and URL buttons")])]),
    "notes_help": _p("📝 Notes System", [(None, CMD, [("/save <name> <text>", "Save a text note (admin only)"), ("/save <name>", "Reply to a message/media to save it"), ("/get <name>", "Retrieve a note"), ("#<name>", "Retrieve a note by hashtag"), ("/notes", "List notes"), ("/delnote <name>", "Delete a note (admin only)")]), ("Supported types", NOTES, [("Text (HTML), photo, video, document, audio, voice, sticker, GIF",)])]),
    "rules_help": _p("📜 Group Rules", [(None, CMD, [("/setrules <text>", "Set rules (admin only)"), ("/rules", "View rules"), ("/clearrules", "Delete rules (admin only)")]), ("Notes", ITEM, [("Formatting", "HTML and newlines supported")])]),
    "utility_help": _p("⚙️ Utility", [(None, CMD, [("/chatinfo", "Group details and member count"), ("/id", "Your ID or replied user's ID"), ("/info", "Detailed user info and bio"), ("/ping", "Check bot response speed"), ("/pin [silent]", "Reply to pin a message"), ("/unpin", "Unpin replied message or all pins"), ("/purge", "Bulk-delete from replied message"), ("/purgeme", "Delete your recent messages"), ("/del", "Delete replied message"), ("/report", "Report a user to admins"), ("/calc <expression>", "Calculator"), ("/carbon <text>", "Generate a code/text image")]), ("Notes", ITEM, [("Admin only", "/pin, /unpin, /purge, /del")])]),
    "tagall_help": _p("🔖 Tag All", [(None, CMD, [("/tagall", "Mention all members"), ("/tagall <message>", "Mention all with custom message"), ("/stoptag", "Stop tagging")]), ("Notes", ITEM, [("Access", "Admin only"), ("Batch", "Five mentions per message"), ("Skipped", "Bots and deleted accounts")])]),
    "approve_help": _p("🕊 Approve System", [(None, CMD, [("/free or /approve <user>", "Approve a user"), ("/unfree or /unapprove <user>", "Remove approval"), ("/approved", "List approved users")]), ("Notes", ITEM, [("Effect", "Approved users bypass automated restrictions"), ("Access", "Admin only")])]),
    "forward_help": _p("↩️ Forward Protection", [(None, CMD, [("/forwarding on", "Allow forwards"), ("/forwarding off", "Block forwards")]), ("How it works", ITEM, [("On", "Forwards are allowed"), ("Off", "Forward is deleted and a warning added"), ("Warning limit", "Configured ban/kick/mute action applies")])]),
    "ai_help": _p("🤖 Edith AI", [(None, CMD, [("/ai <question>", "Ask Edith AI"), ("/ask <question>", "Alias for /ai"), (".edith <question>", "Ask using dot command")]), ("Group admin", CMD, [("/aifeature on", "Enable AI"), ("/aifeature off", "Disable AI")]), ("Examples", NOTES, [("/ai What is Python?",), (".edith Tell me a joke",)])]),
    "groupinfo_help": _p("👥 Group Identity", [(None, CMD, [("/setname <text>", "Set or change group name"), ("/setbio <text>", "Set or change group description"), ("/groupinfo", "Show group ID, owner and member stats"), ("/setdp", "Reply to image to set group photo (aliases: /setpfp, /setimage)"), ("/link", "Generate invite link (aliases: /givelink, /invitelink)")]), ("Notes", ITEM, [("Access", "Admin only; group only"), ("Bot rights", "Change Group Info and Invite Users permissions required")])]),
    "linkinfo_help": _p("🔗 Invite Link", [(None, CMD, [("/link", "Generate a new group invite link (aliases: /givelink, /invitelink)")]), ("Notes", ITEM, [("Access", "Admin only; group only"), ("Bot rights", "Invite Users Via Link permission required"), ("Behavior", "Each run creates a fresh link")])]),
}


def _tables_for(key):
    tables = list(PAGES[key]["tables"])
    if key == "disable_help":
        try:
            from handlers.disable import DISABLEABLE_COMMANDS
            tables.insert(1, ("Disableable commands", NOTES, [(", ".join(DISABLEABLE_COMMANDS),)]))
        except Exception:
            pass
    return tables


def _escape(value):
    return html.escape(str(value), quote=False)


def render_rich(key):
    """Render bordered HTML tables for Telegram rich-message clients."""
    page = PAGES[key]
    tables = _tables_for(key)
    output = []
    title_in_caption = not page["intro"] and bool(tables) and tables[0][0] is None
    if not title_in_caption:
        output.append(f"<b>{_escape(page['title'])}</b>")
        if page["intro"]:
            output.append(f"<i>{_escape(page['intro'])}</i>")
    for index, (caption, headers, rows) in enumerate(tables):
        if index == 0 and title_in_caption:
            caption = page["title"]
        table = ["<table bordered striped>"]
        if caption:
            table.append(f"<caption>{_escape(caption)}</caption>")
        table.append("<tr>" + "".join(f"<th>{_escape(header)}</th>" for header in headers) + "</tr>")
        code_first = headers[0] in _CODE_FIRST
        for row in rows:
            cells = []
            for col_index, value in enumerate(row):
                cell = _escape(value)
                if col_index == 0 and code_first:
                    cell = f"<code>{cell}</code>"
                cells.append(f"<td>{cell}</td>")
            table.append("<tr>" + "".join(cells) + "</tr>")
        table.append("</table>")
        output.append("".join(table))
    return "\n".join(output)


def render_plain(key):
    """Readable fallback for Telegram clients/APIs without rich table support."""
    page = PAGES[key]
    output = [f"<b>{_escape(page['title'])}</b>"]
    if page["intro"]:
        output.append(f"<i>{_escape(page['intro'])}</i>")
    for caption, headers, rows in _tables_for(key):
        output.append("")
        if caption:
            output.append(f"<b>{_escape(caption)}</b>")
        code_first = headers[0] in _CODE_FIRST
        for row in rows:
            first = _escape(row[0])
            if code_first:
                first = f"<code>{first}</code>"
            rest = " — ".join(_escape(value) for value in row[1:])
            output.append(f"• {first}" + (f" — {rest}" if rest else ""))
    return "\n".join(output)
