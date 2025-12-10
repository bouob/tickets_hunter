# Discord Permissions Reference

## General Permissions

| Permission | Description |
|------------|-------------|
| ADMINISTRATOR | Full access to everything |
| VIEW_AUDIT_LOG | View audit log |
| VIEW_GUILD_INSIGHTS | View server insights |
| MANAGE_GUILD | Manage server settings |
| MANAGE_ROLES | Create/edit/delete roles |
| MANAGE_CHANNELS | Create/edit/delete channels |
| KICK_MEMBERS | Kick members |
| BAN_MEMBERS | Ban members |
| CREATE_INSTANT_INVITE | Create invites |
| CHANGE_NICKNAME | Change own nickname |
| MANAGE_NICKNAMES | Change others' nicknames |
| MANAGE_EMOJIS_AND_STICKERS | Manage emojis and stickers |
| MANAGE_WEBHOOKS | Create/edit/delete webhooks |
| VIEW_CHANNEL | Read channels |

## Text Channel Permissions

| Permission | Description |
|------------|-------------|
| SEND_MESSAGES | Send messages |
| SEND_MESSAGES_IN_THREADS | Send in threads |
| CREATE_PUBLIC_THREADS | Create public threads |
| CREATE_PRIVATE_THREADS | Create private threads |
| EMBED_LINKS | Embed links |
| ATTACH_FILES | Upload files |
| ADD_REACTIONS | Add reactions |
| USE_EXTERNAL_EMOJIS | Use external emojis |
| USE_EXTERNAL_STICKERS | Use external stickers |
| MENTION_EVERYONE | Use @everyone and @here |
| MANAGE_MESSAGES | Delete/pin messages |
| MANAGE_THREADS | Manage threads |
| READ_MESSAGE_HISTORY | Read message history |
| SEND_TTS_MESSAGES | Send TTS messages |
| USE_APPLICATION_COMMANDS | Use slash commands |

## Voice Channel Permissions

| Permission | Description |
|------------|-------------|
| CONNECT | Connect to voice |
| SPEAK | Speak in voice |
| STREAM | Share screen |
| USE_EMBEDDED_ACTIVITIES | Use activities |
| USE_SOUNDBOARD | Use soundboard |
| USE_EXTERNAL_SOUNDS | Use external sounds |
| USE_VAD | Use voice activity |
| PRIORITY_SPEAKER | Priority speaker |
| MUTE_MEMBERS | Mute others |
| DEAFEN_MEMBERS | Deafen others |
| MOVE_MEMBERS | Move members |
| REQUEST_TO_SPEAK | Request to speak in stage |

## Stage Channel Permissions

| Permission | Description |
|------------|-------------|
| REQUEST_TO_SPEAK | Request to speak |

## Events Permissions

| Permission | Description |
|------------|-------------|
| MANAGE_EVENTS | Create/edit/delete events |

## Permission Calculations

Permissions are calculated as bitfields. Example:

```javascript
// Administrator
ADMINISTRATOR = 1 << 3 = 8

// Kick + Ban
KICK_MEMBERS | BAN_MEMBERS = (1 << 1) | (1 << 2) = 6
```

## Role Hierarchy

- Higher roles override lower roles
- Server owner bypasses all permissions
- @everyone is the base role
- Bot role is managed by Discord
