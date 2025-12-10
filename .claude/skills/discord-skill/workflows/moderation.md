# Moderation Workflow

## Actions via `discord_execute`

### Member Moderation
| Action | Description | Required Params |
|--------|-------------|-----------------|
| ban | Ban member from server | userId |
| unban | Unban member | userId |
| kick | Kick member from server | userId |
| timeout | Timeout member (禁言) | userId, minutes |
| remove_timeout | Remove member timeout | userId |

### Auto-Moderation
| Action | Description | Required Params |
|--------|-------------|-----------------|
| create_automod | Create auto-moderation rule | name, triggerType |
| edit_automod | Edit auto-moderation rule | ruleId |
| delete_automod | Delete auto-moderation rule | ruleId |

### Channel Privacy
| Action | Description | Required Params |
|--------|-------------|-----------------|
| bulk_privacy | Bulk set channel privacy | targets[] |
| comprehensive | Comprehensive channel management | operations[] |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| automod_rules | guildId | List auto-mod rules |
| bans | guildId | List banned users |
| audit_logs | guildId, limit | Get audit log entries |

## Auto-Moderation Examples

### Create keyword filter rule
```json
{
  "operation": "moderation",
  "action": "create_automod",
  "params": {
    "name": "Bad Words Filter",
    "triggerType": "KEYWORD",
    "keywordFilter": ["badword1", "badword2", "badword3"],
    "enabled": true
  }
}
```

### Create spam prevention rule
```json
{
  "operation": "moderation",
  "action": "create_automod",
  "params": {
    "name": "Anti-Spam",
    "triggerType": "SPAM",
    "enabled": true
  }
}
```

### Create mention spam rule
```json
{
  "operation": "moderation",
  "action": "create_automod",
  "params": {
    "name": "Mention Limit",
    "triggerType": "MENTION_SPAM",
    "mentionLimit": 5,
    "enabled": true
  }
}
```

### Edit auto-mod rule
```json
{
  "operation": "moderation",
  "action": "edit_automod",
  "params": {
    "ruleId": "rule_id_here",
    "enabled": false,
    "keywordFilter": ["updated", "word", "list"]
  }
}
```

### Delete auto-mod rule
```json
{
  "operation": "moderation",
  "action": "delete_automod",
  "params": {
    "ruleId": "rule_id_here"
  }
}
```

## Privacy Management Examples

### Bulk set channels to private
```json
{
  "operation": "moderation",
  "action": "bulk_privacy",
  "params": {
    "targets": [
      {
        "type": "channel",
        "id": "channel_id_1",
        "isPrivate": true,
        "allowedRoles": ["staff_role"]
      },
      {
        "type": "channel",
        "id": "channel_id_2",
        "isPrivate": true,
        "allowedRoles": ["staff_role"]
      }
    ]
  }
}
```

### Comprehensive channel management
```json
{
  "operation": "moderation",
  "action": "comprehensive",
  "params": {
    "operations": [
      {
        "type": "create_category",
        "name": "STAFF AREA"
      },
      {
        "type": "set_private",
        "categoryId": "new_category_id",
        "isPrivate": true,
        "allowedRoles": ["staff_role"]
      },
      {
        "type": "create_channel",
        "name": "staff-chat",
        "categoryId": "new_category_id"
      }
    ]
  }
}
```

## Auto-Mod Trigger Types

| Type | Description |
|------|-------------|
| KEYWORD | Filters specific keywords |
| SPAM | Detects spam messages |
| KEYWORD_PRESET | Uses Discord's preset filters |
| MENTION_SPAM | Limits excessive mentions |

## Member Moderation Examples

### Ban a member
```json
{
  "operation": "moderation",
  "action": "ban",
  "params": {
    "userId": "user_id_here",
    "reason": "Violation of server rules"
  }
}
```

### Kick a member
```json
{
  "operation": "moderation",
  "action": "kick",
  "params": {
    "userId": "user_id_here",
    "reason": "Warning issued"
  }
}
```

### Timeout a member (10 minutes)
```json
{
  "operation": "moderation",
  "action": "timeout",
  "params": {
    "userId": "user_id_here",
    "minutes": 10,
    "reason": "Spamming in chat"
  }
}
```

### Remove timeout
```json
{
  "operation": "moderation",
  "action": "remove_timeout",
  "params": {
    "userId": "user_id_here",
    "reason": "Timeout lifted early"
  }
}
```

### Query banned users
```json
{
  "resource": "bans"
}
```

### Query audit logs
```json
{
  "resource": "audit_logs",
  "filters": {
    "limit": 50
  }
}
```

## Best Practices

1. **Layered moderation**: Combine multiple rules for comprehensive protection
2. **Allow lists**: Add exceptions for trusted roles
3. **Test first**: Enable rules in test channels before server-wide
4. **Logging**: Set up a mod-log channel for notifications
5. **Document reasons**: Always provide a reason for moderation actions
6. **Audit regularly**: Review audit logs to track moderation activity
