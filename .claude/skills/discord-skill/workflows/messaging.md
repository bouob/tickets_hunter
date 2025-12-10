# Messaging Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| send | Send a message | channelId, content |
| edit | Edit a message | channelId, messageId, content |
| delete | Delete a message | channelId, messageId |
| bulk_delete | Delete multiple messages | channelId, messageIds[] |
| pin | Pin a message | channelId, messageId |
| unpin | Unpin a message | channelId, messageId |
| react | Add reaction | channelId, messageId, emoji |
| unreact | Remove reaction | channelId, messageId, emoji |
| crosspost | Crosspost to followers | channelId, messageId |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| message_history | channelId, count/limit, before, after | Full message history with pagination |
| messages | channelId, count/limit | Read recent messages |
| pinned_messages | channelId | Get pinned messages |
| attachments | channelId, messageId | Get message attachments |

> **Note**: `count` accepts both number (`30`) and string (`"30"`). You can also use `limit` as an alias for `count`.

## Examples

### Send with embed
```json
{
  "operation": "message",
  "action": "send",
  "params": {
    "channelId": "123456789",
    "content": "Check this out!",
    "embed": {
      "title": "Announcement",
      "description": "Important update",
      "color": 0x5865F2
    }
  }
}
```

### Send with buttons
```json
{
  "operation": "message",
  "action": "send",
  "params": {
    "channelId": "123456789",
    "content": "Choose an option:",
    "components": [{
      "type": "button",
      "label": "Accept",
      "style": "primary",
      "customId": "accept_btn"
    }]
  }
}
```

### Bulk delete recent messages
```json
{
  "operation": "message",
  "action": "bulk_delete",
  "params": {
    "channelId": "123456789",
    "messageIds": ["msg1", "msg2", "msg3"]
  }
}
```

### Query message history
```json
{
  "resource": "message_history",
  "filters": {
    "channelId": "123456789",
    "limit": 100,
    "before": "last_message_id"
  }
}
```

### Read recent messages
```json
{
  "resource": "messages",
  "filters": {
    "channelId": "123456789",
    "limit": 30
  }
}
```

## Private Messages

For DMs, use operation `dm` instead of `message`:

```json
{
  "operation": "dm",
  "action": "send",
  "params": {
    "userId": "user_id_here",
    "content": "Hello via DM!"
  }
}
```
