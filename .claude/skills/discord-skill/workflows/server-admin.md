# Server Administration Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| edit | Edit server settings | - |
| edit_welcome | Edit welcome screen | - |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| server | guildId | Get server info |
| server_stats | guildId | Get server statistics |
| server_widget | guildId | Get widget settings |
| welcome_screen | guildId | Get welcome screen |

## Examples

### Get server info
```json
{
  "resource": "server",
  "filters": {
    "guildId": "optional_if_default_set"
  }
}
```

### Get server statistics
```json
{
  "resource": "server_stats",
  "filters": {
    "guildId": "server_id"
  }
}
```

### Edit server name and description
```json
{
  "operation": "server",
  "action": "edit",
  "params": {
    "name": "My Awesome Server",
    "description": "Welcome to our community!"
  }
}
```

### Edit server icon
```json
{
  "operation": "server",
  "action": "edit",
  "params": {
    "icon": "https://example.com/icon.png"
  }
}
```

### Edit server banner
```json
{
  "operation": "server",
  "action": "edit",
  "params": {
    "banner": "https://example.com/banner.png"
  }
}
```

### Set verification level
```json
{
  "operation": "server",
  "action": "edit",
  "params": {
    "verificationLevel": "MEDIUM"
  }
}
```

### Edit welcome screen
```json
{
  "operation": "server",
  "action": "edit_welcome",
  "params": {
    "enabled": true,
    "description": "Welcome to our server! Please read the rules.",
    "welcomeChannels": [
      {
        "channelId": "rules_channel_id",
        "description": "Read our community guidelines",
        "emojiName": "📜"
      },
      {
        "channelId": "intro_channel_id",
        "description": "Introduce yourself",
        "emojiName": "👋"
      }
    ]
  }
}
```

### Get welcome screen
```json
{
  "resource": "welcome_screen",
  "filters": {
    "guildId": "server_id"
  }
}
```

## Verification Levels

| Level | Description |
|-------|-------------|
| NONE | Unrestricted |
| LOW | Must have verified email |
| MEDIUM | Must be registered for 5+ minutes |
| HIGH | Must be member for 10+ minutes |
| VERY_HIGH | Must have verified phone |

## Server Setup Batch Example

Complete server setup workflow:

```json
{
  "operations": [
    {
      "operation": "server",
      "action": "edit",
      "params": {
        "name": "Gaming Community",
        "description": "A place for gamers",
        "verificationLevel": "MEDIUM"
      }
    },
    {
      "operation": "channel",
      "action": "create",
      "params": { "name": "INFORMATION", "type": "category" }
    },
    {
      "operation": "channel",
      "action": "create",
      "params": { "name": "rules", "type": "text" }
    },
    {
      "operation": "channel",
      "action": "create",
      "params": { "name": "announcements", "type": "announcement" }
    },
    {
      "operation": "role",
      "action": "create",
      "params": { "name": "Member", "color": "#5865F2" }
    }
  ]
}
```
