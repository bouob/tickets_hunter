# Thread Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| create | Create a new thread | channelId, name |
| archive | Archive a thread | threadId |
| unarchive | Unarchive a thread | threadId |
| lock | Lock a thread (no new messages) | threadId |
| unlock | Unlock a thread | threadId |
| join | Bot joins the thread | threadId |
| leave | Bot leaves the thread | threadId |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| active_threads | guildId | List all active threads in server |

## Examples

### Create a thread from a message
```json
{
  "operation": "thread",
  "action": "create",
  "params": {
    "channelId": "channel_id_here",
    "name": "Discussion Thread",
    "messageId": "message_id_to_reply",
    "autoArchiveDuration": 1440
  }
}
```

### Create a standalone thread
```json
{
  "operation": "thread",
  "action": "create",
  "params": {
    "channelId": "channel_id_here",
    "name": "New Topic Discussion"
  }
}
```

### Archive a thread
```json
{
  "operation": "thread",
  "action": "archive",
  "params": {
    "threadId": "thread_id_here",
    "reason": "Discussion completed"
  }
}
```

### Lock a thread
```json
{
  "operation": "thread",
  "action": "lock",
  "params": {
    "threadId": "thread_id_here",
    "reason": "Preventing further discussion"
  }
}
```

### Join a thread
```json
{
  "operation": "thread",
  "action": "join",
  "params": {
    "threadId": "thread_id_here"
  }
}
```

### Query active threads
```json
{
  "resource": "active_threads"
}
```

## Auto-Archive Durations

| Duration (minutes) | Description |
|-------------------|-------------|
| 60 | 1 hour |
| 1440 | 1 day (default) |
| 4320 | 3 days |
| 10080 | 1 week |

## Best Practices

1. **Organize discussions**: Use threads to keep main channels clean
2. **Archive when done**: Archive completed discussions to reduce clutter
3. **Lock sensitive threads**: Lock threads that shouldn't receive more replies
4. **Use descriptive names**: Thread names should clearly indicate the topic
5. **Set appropriate auto-archive**: Choose duration based on expected activity
