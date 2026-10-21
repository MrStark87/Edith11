from pyrogram import Client, filters, StopPropagation
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ParseMode
import logging
import db

# 🟢 DOTS (.) HATA DIYE GAYE HAIN
from handlers.start import register_handlers
from handlers.group_commands import register_group_commands
from handlers.notes import register_notes_handler
from handlers.rules import register_rules_handler
from handlers.abuse import register_abuse_handler
from handlers.fsub import register_fsub_handler
from handlers.tools import register_tools_handler
from handlers.utility import register_utility_handler
from handlers.cmddeleter import register_cmddeleter_handler
from handlers.mediadelete import register_mediadelete_handler
from handlers.zombie import register_zombie_handler
from handlers.tagall import register_tagall_handler
from handlers.promote import register_promote_handler
from handlers.cleaner import register_cleaner_handler
from handlers.blacklist import register_blacklist_handler
from handlers.filters import register_filters_handler
from handlers.joinrequest import register_joinrequest_handler
from handlers.ghost import register_ghost_handler
from handlers.antiraid import register_antiraid_handler
from handlers.edith_ai import register_ai_handler
from handlers.blackuser import register_blackuser_handler
from handlers.welcome import register_welcome_handler
from handlers.admin_tag import register_admin_tag_handler
from handlers.anti_link import register_anti_link_handler
from handlers.autolock import register_autolock_handler
from handlers.disable import register_disable_handler
from handlers.logger import register_logger_handler
from handlers.approve import register_approve_handler
from handlers.groupinfo import register_groupinfo_handler


def register_all_handlers(app):
    register_handlers(app)
    register_group_commands(app)
    register_notes_handler(app)
    register_rules_handler(app)
    register_abuse_handler(app)
    register_fsub_handler(app)
    register_tools_handler(app)
    register_utility_handler(app)
    register_cmddeleter_handler(app)
    register_mediadelete_handler(app)
    register_zombie_handler(app)
    register_tagall_handler(app)
    register_promote_handler(app)
    register_cleaner_handler(app)
    register_blacklist_handler(app)
    register_filters_handler(app)
    register_joinrequest_handler(app)
    register_ghost_handler(app)
    register_antiraid_handler(app)
    register_ai_handler(app)
    register_blackuser_handler(app)
    register_welcome_handler(app)
    register_admin_tag_handler(app)
    register_anti_link_handler(app)
    register_autolock_handler(app)
    register_disable_handler(app)
    register_logger_handler(app)
    register_approve_handler(app)
    register_groupinfo_handler(app)
