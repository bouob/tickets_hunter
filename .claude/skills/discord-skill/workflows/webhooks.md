# Webhook Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| create | Create webhook | channelId, name |
| delete | Delete webhook | webhookId |
| send | Send message via webhook | webhookUrl, content |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| webhooks | channelId | List webhooks |

## Examples

### Create a webhook
```json
{
  "operation": "webhook",
  "action": "create",
  "params": {
    "channelId": "channel_id",
    "name": "Notification Bot"
  }
}
```

### Send message via webhook
```json
{
  "operation": "webhook",
  "action": "send",
  "params": {
    "webhookUrl": "https://discord.com/api/webhooks/...",
    "content": "Hello from webhook!"
  }
}
```

### Delete a webhook
```json
{
  "operation": "webhook",
  "action": "delete",
  "params": {
    "webhookId": "webhook_id"
  }
}
```

### List channel webhooks
```json
{
  "resource": "webhooks",
  "filters": {
    "channelId": "channel_id"
  }
}
```

## Use Cases

- **Notifications**: Send automated alerts
- **Integration**: Connect external services
- **Bots**: Create bot-like messages without a bot
- **Logging**: Send logs to Discord channels
