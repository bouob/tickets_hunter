# Server Events Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| create | Create server event | name, startTime |
| edit | Edit event | eventId |
| delete | Delete event | eventId |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| events | guildId | List scheduled events |

## Examples

### Create external event
```json
{
  "operation": "event",
  "action": "create",
  "params": {
    "name": "Community Game Night",
    "description": "Join us for games!",
    "startTime": "2025-01-15T20:00:00Z",
    "endTime": "2025-01-15T23:00:00Z",
    "location": "Discord Voice Channel"
  }
}
```

### Create voice channel event
```json
{
  "operation": "event",
  "action": "create",
  "params": {
    "name": "Live Q&A Session",
    "description": "Ask questions to the team",
    "startTime": "2025-01-20T18:00:00Z",
    "channelId": "voice_channel_id"
  }
}
```

### Edit event
```json
{
  "operation": "event",
  "action": "edit",
  "params": {
    "eventId": "event_id",
    "name": "Updated Event Name",
    "description": "Updated description",
    "startTime": "2025-01-16T20:00:00Z"
  }
}
```

### Delete event
```json
{
  "operation": "event",
  "action": "delete",
  "params": {
    "eventId": "event_id"
  }
}
```

### List events
```json
{
  "resource": "events"
}
```

## Event Tips

- Use ISO 8601 format for dates (e.g., `2025-01-15T20:00:00Z`)
- Include end time for better user experience
- For voice events, specify the channelId
- External events require a location string
