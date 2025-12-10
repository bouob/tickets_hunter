# Complete API Actions Reference

## discord_execute Actions

### message
| Action | Params | Description |
|--------|--------|-------------|
| send | channelId, content, [embed, components] | Send message |
| edit | channelId, messageId, content | Edit message |
| delete | channelId, messageId | Delete message |
| bulk_delete | channelId, messageIds[] | Bulk delete (max 100) |
| pin | channelId, messageId | Pin message |
| unpin | channelId, messageId | Unpin message |
| react | channelId, messageId, emoji | Add reaction |
| unreact | channelId, messageId, emoji | Remove reaction |
| crosspost | channelId, messageId | Crosspost announcement |

### dm
| Action | Params | Description |
|--------|--------|-------------|
| send | userId, content | Send DM |
| edit | userId, messageId, content | Edit DM |
| delete | userId, messageId | Delete DM |

### channel
| Action | Params | Description |
|--------|--------|-------------|
| create | name, type, [topic, categoryId, userLimit, bitrate] | Create channel |
| edit | channelId, [name, topic, nsfw, rateLimitPerUser] | Edit channel |
| delete | channelId | Delete channel |
| move | channelId, categoryId | Move to category |
| set_position | channelId, position | Set position |
| set_positions | positions[{id, position}] | Bulk set positions |
| set_private | channelId, private, [allowedRoles] | Set privacy |

### role
| Action | Params | Description |
|--------|--------|-------------|
| create | name, [color, permissions, hoist, mentionable] | Create role |
| edit | roleId, [name, color, permissions] | Edit role |
| delete | roleId | Delete role |
| set_positions | positions[{id, position}] | Set role positions |
| add_to_member | roleId, memberId | Add role to member |
| remove_from_member | roleId, memberId | Remove role from member |

### member
| Action | Params | Description |
|--------|--------|-------------|
| edit | userId, [nickname, roles], guildId? | Edit member |
| search | query?, limit?, guildId? | Search members |

### server
| Action | Params | Description |
|--------|--------|-------------|
| edit | [name, icon, banner, description] | Edit server |
| edit_welcome_screen | enabled, [welcomeChannels, description] | Edit welcome |

### voice
| Action | Params | Description |
|--------|--------|-------------|
| join | channelId | Join voice channel |
| leave | - | Leave voice channel |
| play | url | Play audio |
| stop | - | Stop audio |
| set_volume | volume (0-100) | Set volume |

### moderation
| Action | Params | Description |
|--------|--------|-------------|
| create_automod | name, triggerType, keywordFilter?, guildId? | Create auto-mod rule |
| edit_automod | ruleId, [name, enabled, keywordFilter], guildId? | Edit auto-mod rule |
| delete_automod | ruleId, guildId? | Delete auto-mod rule |
| ban | userId, reason?, guildId? | Ban member from server |
| unban | userId, reason?, guildId? | Unban member |
| kick | userId, reason?, guildId? | Kick member from server |
| timeout | userId, minutes, reason?, guildId? | Timeout member (minutes) |
| remove_timeout | userId, reason?, guildId? | Remove member timeout |
| bulk_privacy | targets[], guildId? | Bulk set channel privacy |
| comprehensive | operations[], guildId? | Comprehensive channel management |

### thread
| Action | Params | Description |
|--------|--------|-------------|
| create | channelId, name, autoArchiveDuration?, messageId? | Create thread |
| archive | threadId, reason? | Archive thread |
| unarchive | threadId, reason? | Unarchive thread |
| lock | threadId, reason? | Lock thread (prevent new messages) |
| unlock | threadId, reason? | Unlock thread |
| join | threadId | Bot joins thread |
| leave | threadId | Bot leaves thread |

### webhook
| Action | Params | Description |
|--------|--------|-------------|
| create | channelId, name, [avatar] | Create webhook |
| delete | webhookId | Delete webhook |
| send | webhookId, content, [username, avatarURL] | Send via webhook |

### event
| Action | Params | Description |
|--------|--------|-------------|
| create | name, scheduledStartTime, privacyLevel, entityType | Create event |
| edit | eventId, [name, description, scheduledStartTime] | Edit event |
| delete | eventId | Delete event |

### emoji
| Action | Params | Description |
|--------|--------|-------------|
| create | name, image (base64 or URL) | Create emoji |
| delete | emojiId | Delete emoji |

### sticker
| Action | Params | Description |
|--------|--------|-------------|
| create | name, description, tags, file | Create sticker |
| delete | stickerId | Delete sticker |

### invite
| Action | Params | Description |
|--------|--------|-------------|
| create | channelId, [maxAge, maxUses, temporary] | Create invite |
| delete | inviteCode | Delete invite |

---

## discord_query Resources

| Resource | Filters | Returns |
|----------|---------|---------|
| messages | channelId, limit, before, after | Message[] |
| pinned_messages | channelId | Message[] |
| message_history | channelId, limit?, before?, after? | Message[] |
| attachments | channelId, messageId | Attachment[] |
| dm_messages | userId, limit? | Message[] |
| channels | type, categoryId | Channel[] |
| channel_structure | guildId? | CategoryStructure[] |
| category_channels | categoryId | Channel[] |
| members | limit, query, role | Member[] |
| member | userId | Member |
| roles | guildId? | Role[] |
| server | guildId? | ServerInfo |
| server_stats | guildId? | ServerStats |
| server_widget | guildId? | WidgetInfo |
| welcome_screen | guildId? | WelcomeScreen |
| events | guildId? | Event[] |
| invites | guildId? | Invite[] |
| webhooks | channelId | Webhook[] |
| emojis | guildId? | Emoji[] |
| stickers | guildId? | Sticker[] |
| automod_rules | guildId? | AutoModRule[] |
| voice_connections | - | VoiceConnection[] |
| bans | guildId? | BannedUser[] |
| audit_logs | guildId?, limit? | AuditLogEntry[] |
| active_threads | guildId? | Thread[] |

---

## discord_batch

Execute multiple operations atomically:

```json
{
  "operations": [
    { "operation": "...", "action": "...", "params": {...} },
    { "operation": "...", "action": "...", "params": {...} }
  ]
}
```

Operations execute in order. If one fails, subsequent operations are skipped.
