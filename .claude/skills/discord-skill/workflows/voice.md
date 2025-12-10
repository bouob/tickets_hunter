# Voice Channel Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| join | Join voice channel | guildId, channelId |
| leave | Leave voice channel | guildId, channelId |
| play | Play audio file/URL | guildId, url |
| stop | Stop audio playback | guildId |
| set_volume | Set volume (0-200) | guildId, volume |

> **Note**: `volume` accepts both number (`50`) and string (`"50"`).

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| voice_connections | - | Get active voice connections |

## Examples

### Join a voice channel
```json
{
  "operation": "voice",
  "action": "join",
  "params": {
    "guildId": "server_id",
    "channelId": "voice_channel_id"
  }
}
```

### Play audio
```json
{
  "operation": "voice",
  "action": "play",
  "params": {
    "guildId": "server_id",
    "url": "https://example.com/audio.mp3"
  }
}
```

### Set volume
```json
{
  "operation": "voice",
  "action": "set_volume",
  "params": {
    "guildId": "server_id",
    "volume": 50
  }
}
```

### Stop audio
```json
{
  "operation": "voice",
  "action": "stop",
  "params": {
    "guildId": "server_id"
  }
}
```

### Leave voice channel
```json
{
  "operation": "voice",
  "action": "leave",
  "params": {
    "guildId": "server_id",
    "channelId": "voice_channel_id"
  }
}
```

### Check active connections
```json
{
  "resource": "voice_connections"
}
```

## Audio Playback Workflow

Complete audio playback sequence:

```json
{
  "operations": [
    {
      "operation": "voice",
      "action": "join",
      "params": { "guildId": "123", "channelId": "456" }
    },
    {
      "operation": "voice",
      "action": "set_volume",
      "params": { "guildId": "123", "volume": 75 }
    },
    {
      "operation": "voice",
      "action": "play",
      "params": { "guildId": "123", "url": "https://example.com/music.mp3" }
    }
  ],
  "stopOnError": true
}
```

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- FLAC (.flac)
- WebM (.webm)
- YouTube URLs (with proper setup)
