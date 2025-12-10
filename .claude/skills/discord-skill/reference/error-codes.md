# Discord Error Codes Reference

## Common HTTP Status Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Check bot token |
| 403 | Forbidden | Check bot permissions |
| 404 | Not Found | Check resource IDs |
| 429 | Too Many Requests | Rate limited, wait |
| 500 | Server Error | Discord issue, retry |
| 502 | Bad Gateway | Discord issue, retry |

## Discord API Error Codes

### General Errors

| Code | Message | Solution |
|------|---------|----------|
| 10001 | Unknown account | User doesn't exist |
| 10002 | Unknown application | App doesn't exist |
| 10003 | Unknown channel | Channel ID invalid |
| 10004 | Unknown guild | Server ID invalid |
| 10006 | Unknown invite | Invite code invalid |
| 10007 | Unknown member | User not in server |
| 10008 | Unknown message | Message ID invalid |
| 10011 | Unknown role | Role ID invalid |
| 10014 | Unknown emoji | Emoji ID invalid |

### Permission Errors

| Code | Message | Solution |
|------|---------|----------|
| 50001 | Missing access | Bot can't access resource |
| 50013 | Missing permissions | Bot lacks required perms |
| 50034 | Can only bulk delete... | Messages too old |
| 50035 | Invalid form body | Check request format |

### Rate Limit Errors

| Code | Message | Solution |
|------|---------|----------|
| 20028 | Slowmode rate limit | Wait for slowmode |
| 429 | Rate limited | Wait and retry |

### Channel Errors

| Code | Message | Solution |
|------|---------|----------|
| 50024 | Cannot execute on... | Wrong channel type |
| 50033 | Invalid recipients | Can't DM user |

### Role Errors

| Code | Message | Solution |
|------|---------|----------|
| 50028 | Invalid role | Role hierarchy issue |

## Error Handling Examples

### Check for rate limits
```json
{
  "operation": "message",
  "action": "send",
  "params": {
    "channelId": "...",
    "content": "..."
  }
}
// If error 429, wait retry_after seconds
```

### Check permissions before action
```json
{
  "resource": "member",
  "filters": {
    "userId": "bot_user_id"
  }
}
// Check bot's roles and permissions
```

## Best Practices

1. **Handle rate limits**: Implement exponential backoff
2. **Check permissions**: Verify before sensitive actions
3. **Validate IDs**: Ensure IDs are correct format
4. **Log errors**: Track error patterns
5. **Use batch sparingly**: Reduce API calls
