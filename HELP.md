# Edith Security Bot — Help & Commands

> Command reference consolidated from the repository's help menus and handler modules. Commands are shown with the `/` prefix; replace placeholders such as `<user>` or `<time>` with actual values.

## Start & general

| Command | Use |
|---|---|
| `/start` | Open the bot's start menu. |
| `/help` | Open the help menu. In a group, use the button to view help in private chat. |
| `/privacy` | View the privacy policy. |
| `/id` | Show your ID; reply to a user's message to show their ID. |
| `/info` | Show detailed user information and bio. |
| `/ping` | Check the bot's response speed. |
| `/calc <expression>` | Calculate a math expression. |
| `/carbon <text>` | Turn text or code into a Carbon-style image. Can also reply to a text message. |
| `/report` | Report a user to the group admins. |

## Group identity & invite links

| Command | Use |
|---|---|
| `/setname <text>` | Set or change the group name. |
| `/setbio <text>` | Set or change the group description. |
| `/groupinfo` | Show group ID, owner, member count, admins, bots, deleted accounts, and active accounts. |
| `/setdp` | Reply to an image (or send one with the command) to set the group photo. |
| `/setpfp`, `/setimage` | Aliases for `/setdp`. |
| `/link` | Generate a new group invite link. |
| `/givelink`, `/invitelink` | Aliases for `/link`. |
| `/chatinfo` | Show group details, ID, username, member count, and chat type. |

## Moderation

| Command | Use |
|---|---|
| `/kick <user>` | Remove a user from the group. Reply to their message or provide a username/ID. |
| `/ban <user>` | Ban a user. Reply to their message or provide a username/ID. |
| `/unban <user>` | Lift a user's ban. |
| `/mute <user>` | Mute a user. |
| `/unmute <user>` | Unmute a user. |
| `/tmute <user> <time>` | Temporarily mute a user; time supports seconds, minutes, hours, or days (for example `30s`, `10m`, `2h`, `1d`). Reply with `/tmute <time>` also works. |
| `/tban <user> <time>` | Temporarily ban a user; time supports `30s`, `10m`, `2h`, or `1d`. Reply with `/tban <time>` also works. |
| `/dkick` | Reply to a user's message to kick them and delete that message. |
| `/skick <user>` | Silently kick a user and delete the command message. |
| `/smute <user>` | Silently mute a user and delete the command message. |
| `/sban <user>` | Silently ban a user and delete the command message. |
| `/dmute` | Reply to a user's message to mute them and delete that message. |
| `/dban` | Reply to a user's message to ban them and delete that message. |
| `/warn <user> [reason]` | Give a user a warning, optionally with a reason. |
| `/dwarn [reason]` | Reply to a user's message to delete it and warn them. |
| `/warns [user]` | View warning history for yourself or a specified/replied-to user. |
| `/unwarn <user>` | Remove one warning. `/rmwarn` is an alias. |
| `/resetwarns <user>` | Clear a user's warnings. |
| `/setwarnlimit <2-10>` | Set the warning limit before the configured action. |
| `/setwarnaction <mute|kick|ban>` | Choose what happens when the warning limit is reached. |

## Admin roles & staff

| Command | Use |
|---|---|
| `/cofounder <user>` | Promote a user to co-founder (group owner only). |
| `/admin <user> [title]` | Promote a user to admin; optionally set a custom title. |
| `/promote <user> [title]` | Alias for standard admin promotion. |
| `/mod <user>` | Promote a user to moderator. |
| `/fullpromote <user> [title]` | Promote a user with all admin permissions and an optional title. |
| `/demote <user>` | Remove a user's admin rights. |
| `/staff` | List staff members and roles. |

## Locks & group security

| Command | Use |
|---|---|
| `/lock <type>` | Lock a type of content. Types: `url`, `username`, `forward`, `edit`, `text`, `media`, `sticker`, `files`, `music`, `emoji`. |
| `/unlock <type>` | Unlock a content type. |
| `/locks` | Show active lock status. |
| `/lockall` | Lock all supported content types. |
| `/unlockall` | Unlock all supported content types. |
| `/biolink on` | Enable protection against users with links in their bio. Admins can choose delete, mute, or ban behavior with `/bioconfig`. |
| `/biolink off` | Disable bio-link protection. |
| `/bioconfig` | Configure the bio-link action (delete, mute, or ban). |
| `/nolink on` | Block links, except links in the allowed list. |
| `/nolink off` | Turn off the general link block. Explicitly blocked links remain blocked. |
| `/allowlink <url>` | Add a link/domain to the allowed list. |
| `/rmallowlink <url>` | Remove a link/domain from the allowed list. |
| `/blocklink <url>` | Add a link/domain to the blocked list. |
| `/rmblocklink <url>` | Remove a link/domain from the blocked list. |
| `/allowedlinks` | List allowed links/domains. |
| `/blockedlinks` | List blocked links/domains. |
| `/linkwarn on` | Warn users for blocked links and apply the configured warn action at the limit. |
| `/linkwarn off` | Delete blocked-link messages and notify, without adding warnings. |
| `/antisticker on` | Block stickers from regular members. |
| `/antisticker off` | Allow stickers. |
| `/banpack` | Reply to a sticker to ban its sticker pack. |
| `/unbanpack <packname>` | Unban a sticker pack; replying to one of its stickers also works. |
| `/bannedpacks` | List banned sticker packs. |
| `/clearbanpacks` | Clear the banned sticker-pack list. |
| `/noabuse on` | Enable the abusive-word filter. |
| `/noabuse off` | Disable the abusive-word filter. |
| `/antiraid on` | Automatically mute new members for the configured duration. |
| `/antiraid off` | Disable anti-raid auto-muting. |
| `/raiddelay <time>` | Set the anti-raid mute duration (for example `30s`, `5m`, `1h`; `0` means until an admin unmutes). |
| `/antiflood on` | Enable flood/spam detection. |
| `/antiflood off` | Disable flood/spam detection. |
| `/setflood <2-50>` | Set the number of messages allowed per 10 seconds. |
| `/floodaction <mute|kick|ban|warn>` | Choose the action taken for flooding. |
| `/floodtime <time>` | Set mute/ban duration; supports `1s`–`60s`, `1m`–`60m`, `1h`–`24h`, or `0` for permanent. |
| `/floodmode <normal|strict>` | Choose whether all rapid messages or only repeated messages count. |
| `/flood` | Show anti-flood settings. |
| `/floodwhitelist add <user>` | Exempt a replied-to user or username/ID from flood detection. |
| `/floodwhitelist remove <user>` | Remove a user from the flood whitelist. |
| `/floodwhitelist list` | List flood-whitelisted users. |
| `/captcha on` | Require new members to solve a verification question before chatting. |
| `/captcha off` | Disable captcha verification. |
| `/captchatime <30-300>` | Set the captcha timeout in seconds. |
| `/autolock on` | Set a daily automatic group-lock time using the hour and AM/PM buttons. |
| `/autolock off` | Set a daily automatic group-unlock time using the hour and AM/PM buttons. |
| `/autolockstatus` | Show the scheduled lock and unlock times. |
| `/autolockclear` | Clear the automatic lock schedule. |
| `/ghostmode on` | Automatically delete group service messages. |
| `/ghostmode off` | Disable ghost mode. |
| `/approve <user>` | Approve a user so automated restrictions skip their messages. `/free` is an alias. |
| `/unapprove <user>` | Remove a user's approval. `/unfree` is an alias. |
| `/approved` | List approved users. |
| `/blackuser <user>` | Add a user to the group blacklist; their messages are deleted. |
| `/rmblackuser <user>` | Remove a user from the group blacklist. |
| `/blacklistusers` | List blacklisted users. |
| `/addblack <word>` | Add a word to the group word blacklist. |
| `/rmblack <word>` | Remove a word from the group word blacklist. |
| `/blacklist` | List blacklisted words. |
| `/disable <command>` | Disable an eligible member command. |
| `/enable <command>` | Re-enable a disabled command. |
| `/disabled` | List disabled commands. |
| `/admintag on` | Enable `@admin`/`@admins` tagging. |
| `/admintag off` | Disable admin tagging. |
| `@admin`, `@admins` | Mention group admins (when admin tagging is enabled). |
| `/zombie` | Scan the group and remove deleted accounts. |

## Welcome messages

| Command | Use |
|---|---|
| `/welcome on` | Enable welcome messages and show the private setup button. |
| `/welcome off` | Disable welcome messages. |
| `/setwelcome` | Open the private welcome-message setup panel. Configure text, media, and URL buttons there. |
| `/previewwelcome` | Preview the current welcome message. |
| `/resetwelcome` | Reset the custom welcome message to default. |
| `{id}` | Welcome placeholder for the joining user's ID. |
| `{name}` | Welcome placeholder for the joining user's first name. |
| `{surname}` | Welcome placeholder for the joining user's last name. |
| `{namesurname}` | Welcome placeholder for the joining user's full name. |
| `{mention}` | Clickable mention of the joining user. |
| `{username}` | Joining user's @username. |
| `{groupname}` | Group name. |

## Notes, rules & filters

| Command | Use |
|---|---|
| `/save <name> <text>` | Save a text note. `/setnote` is an alias. |
| `/save <name>` | Reply to a message or media to save it as a note. |
| `/get <name>` | Retrieve a saved note. |
| `#<name>` | Retrieve a saved note by its hashtag. |
| `/notes` | List saved notes. |
| `/delnote <name>` | Delete a saved note. |
| `/setrules <text>` | Set group rules (admin only; HTML formatting and newlines are supported). |
| `/rules` | View the group rules. |
| `/clearrules` | Delete group rules (admin only). |
| `/filter <keyword>` | Reply to a message or sticker to create an automatic keyword response. |
| `/stopfilter <keyword>` | Remove a keyword filter. |
| `/filters` | List active keyword filters. |

## Message tools & cleanup

| Command | Use |
|---|---|
| `/echo <text>` | Repeat text as the bot; long text can be uploaded to Telegraph. |
| `/setlongmode <off|manual|automatic>` | Choose what to do with long messages: no action, delete and warn, or delete and send a Telegraph link. |
| `/setlonglimit <limit>` | Set the long-message character limit. |
| `/nophone on` | Delete messages containing phone numbers. |
| `/nophone off` | Allow phone-number messages. |
| `/nohashtags on` | Delete messages containing hashtags. |
| `/nohashtags off` | Allow hashtags. |
| `/forwarding on` | Allow forwarded messages. |
| `/forwarding off` | Block forwarded messages; warnings may lead to the configured action. |
| `/mediadelete on` | Automatically delete supported media after the configured delay. |
| `/mediadelete off` | Disable media auto-delete. |
| `/setmediadelay <time>` | Set media auto-delete delay, from `1m` to `24h`. |
| `/cleaner on` | Automatically delete regular members' text and media after the configured delay. |
| `/cleaner off` | Disable the message cleaner. |
| `/setcleandelay <time>` | Set cleaner delay, from `1m` to `24h` (default `5m`). |
| `/cleanstatus` | Show cleaner status and delay. |
| `/cmd on` | Automatically delete messages that start with `/`, `!`, or `.`. |
| `/cmd off` | Disable command auto-delete. |
| `/cleanservice on` | Automatically delete join/leave service messages. |
| `/cleanservice off` | Keep join/leave service messages. |
| `/pin` | Reply to a message to pin it. Add `silent` to pin without notification. |
| `/unpin` | Unpin the replied-to message, or all pinned messages if not replying. |
| `/del` | Reply to a message to delete it. |
| `/purge` | Reply to the first message to bulk-delete messages through the command. |
| `/purgeme` | Delete your recent messages found in the last 100 messages. |
| `/tagall [message]` | Mention all group members, optionally with a custom message (admin only). |
| `/stoptag` | Stop an active tag-all operation (admin only). |

## Join requests

| Command | Use |
|---|---|
| `/acceptall on` | Automatically accept join requests. |
| `/acceptall off` | Handle requests manually (requires the bot's join-request permission). |
| `/notification on` | Send join-request notifications to the group. |
| `/notification off` | Stop join-request notifications. |

## Edith AI

| Command | Use |
|---|---|
| `/ai <question>` | Ask Edith AI a question. |
| `/ask <question>` | Alias for `/ai`. |
| `.edith <question>` | Ask Edith AI with the dot-command form. |
| `/aifeature on` | Enable Edith AI in the group (admin only). |
| `/aifeature off` | Disable Edith AI in the group (admin only). |

## Restrictions & permissions

- Unless noted otherwise, group configuration and moderation commands are for group admins.
- The bot must have the relevant Telegram admin permissions for actions such as deleting messages, changing group info, inviting users, banning, or managing join requests.
- Some commands accept a reply to the target user's message instead of a username or ID.
