# Channel Management Workflow

## Channel Types

| Type | Value | Description |
|------|-------|-------------|
| text | 0 | Standard text channel |
| voice | 2 | Voice channel |
| category | 4 | Channel category |
| announcement | 5 | News/announcement channel |
| stage | 13 | Stage channel for events |
| forum | 15 | Forum channel for discussions |

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| create | Create channel | name, type |
| edit | Edit channel | channelId, [name, topic, etc.] |
| delete | Delete channel | channelId |
| move | Move to category | channelId, categoryId |
| set_position | Set position | channelId, position |
| set_positions | Bulk set positions | positions[] |
| set_private | Set privacy | channelId, private |

> **Note**: `position` accepts both number (`0`) and string (`"0"`).

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| channels | type, categoryId | List channels |
| channel_structure | - | Get full server structure |

## Examples

### Create text channel
```json
{
  "operation": "channel",
  "action": "create",
  "params": {
    "name": "announcements",
    "type": "text",
    "topic": "Server announcements",
    "categoryId": "category_id_optional"
  }
}
```

### Create voice channel
```json
{
  "operation": "channel",
  "action": "create",
  "params": {
    "name": "Gaming Voice",
    "type": "voice",
    "userLimit": 10,
    "bitrate": 64000
  }
}
```

### Create category
```json
{
  "operation": "channel",
  "action": "create",
  "params": {
    "name": "COMMUNITY",
    "type": "category"
  }
}
```

### Move channel to category
```json
{
  "operation": "channel",
  "action": "move",
  "params": {
    "channelId": "channel_to_move",
    "categoryId": "target_category"
  }
}
```

### Organize multiple channels
Use `discord_batch` for complex reorganization:

```json
{
  "operations": [
    { "operation": "channel", "action": "create", "params": { "name": "NEW SECTION", "type": "category" } },
    { "operation": "channel", "action": "move", "params": { "channelId": "ch1", "categoryId": "new_category" } },
    { "operation": "channel", "action": "move", "params": { "channelId": "ch2", "categoryId": "new_category" } },
    { "operation": "channel", "action": "set_positions", "params": { "positions": [{"id": "ch1", "position": 0}, {"id": "ch2", "position": 1}] } }
  ]
}
```

### Set channel private
```json
{
  "operation": "channel",
  "action": "set_private",
  "params": {
    "channelId": "123456789",
    "private": true,
    "allowedRoles": ["role_id_1", "role_id_2"]
  }
}
```
