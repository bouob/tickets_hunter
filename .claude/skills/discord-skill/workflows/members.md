# Member Management Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| edit | Edit member (nickname, roles) | userId |
| search | Search members by query | - |

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| members | guildId, limit, after | List members |
| member | guildId, userId | Get member info |

> **Note**: `limit` accepts both number (`100`) and string (`"100"`).

## Examples

### Edit member nickname
```json
{
  "operation": "member",
  "action": "edit",
  "params": {
    "userId": "user_id_here",
    "nickname": "New Nickname"
  }
}
```

### Edit member roles
```json
{
  "operation": "member",
  "action": "edit",
  "params": {
    "userId": "user_id_here",
    "roles": ["role_id_1", "role_id_2"]
  }
}
```

### Search members
```json
{
  "operation": "member",
  "action": "search",
  "params": {
    "query": "john",
    "limit": 10
  }
}
```

### Query member list
```json
{
  "resource": "members",
  "filters": {
    "limit": 100
  }
}
```

### Get specific member info
```json
{
  "resource": "member",
  "filters": {
    "userId": "user_id_here"
  }
}
```

## Batch Member Operations

Use `discord_batch` for multiple member updates:

```json
{
  "operations": [
    {
      "operation": "role",
      "action": "add_to_member",
      "params": { "userId": "user1", "roleId": "verified_role" }
    },
    {
      "operation": "role",
      "action": "add_to_member",
      "params": { "userId": "user2", "roleId": "verified_role" }
    },
    {
      "operation": "member",
      "action": "edit",
      "params": { "userId": "user1", "nickname": "Verified User 1" }
    }
  ]
}
```
