---
name: discord-operations
description: Discord server management and automation guide for Claude
version: 2.1.0
triggers:
  - discord
  - server
  - channel
  - message
  - member
  - role
  - voice
  - moderation
  - thread
  - ban
  - kick
---

# Discord Operations Skill

This skill teaches Claude how to use the streamlined Discord MCP for server management.

## Available Tools

| Tool | Purpose |
|------|---------|
| `discord_execute` | Perform actions (send, create, edit, delete) |
| `discord_query` | Read data (messages, channels, members, roles) |
| `discord_batch` | Execute multiple operations atomically |

## Operation Categories

| Category | Description | Guide |
|----------|-------------|-------|
| message | Send, edit, delete, react to messages | [workflows/messaging.md](workflows/messaging.md) |
| channel | Create, edit, organize channels | [workflows/channel-management.md](workflows/channel-management.md) |
| thread | Create, archive, lock threads | [workflows/threads.md](workflows/threads.md) |
| role | Manage roles and permissions | [workflows/roles.md](workflows/roles.md) |
| member | Member info and management | [workflows/members.md](workflows/members.md) |
| server | Server settings and stats | [workflows/server-admin.md](workflows/server-admin.md) |
| voice | Voice channels and audio | [workflows/voice.md](workflows/voice.md) |
| moderation | Ban, kick, timeout, auto-mod | [workflows/moderation.md](workflows/moderation.md) |
| webhook | Webhook management | [workflows/webhooks.md](workflows/webhooks.md) |
| event | Server events | [workflows/events.md](workflows/events.md) |

## Reference Documentation

| Document | Description |
|----------|-------------|
| [API Actions](reference/api-actions.md) | Complete list of all actions |
| [Permissions](reference/permissions.md) | Discord permissions reference |
| [Error Codes](reference/error-codes.md) | Error handling guide |

## Quick Examples

### Send a message
```json
{
  "operation": "message",
  "action": "send",
  "params": { "channelId": "...", "content": "Hello!" }
}
```

### Create a channel
```json
{
  "operation": "channel",
  "action": "create",
  "params": { "name": "general", "type": "text" }
}
```

### Query members
```json
{
  "resource": "members",
  "filters": { "role": "admin" },
  "limit": 50
}
```

For complete action reference, see [reference/api-actions.md](reference/api-actions.md)
