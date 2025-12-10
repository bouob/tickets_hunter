# Role Management Workflow

## Actions via `discord_execute`

| Action | Description | Required Params |
|--------|-------------|-----------------|
| create | Create a new role | name |
| edit | Edit role properties | roleId |
| delete | Delete a role | roleId |
| set_positions | Reorder roles | positions[] |
| add_to_member | Assign role to member | userId, roleId |
| remove_from_member | Remove role from member | userId, roleId |

> **Note**: `position` in set_positions accepts both number (`5`) and string (`"5"`).

## Queries via `discord_query`

| Resource | Filters | Description |
|----------|---------|-------------|
| roles | guildId | List all roles |

## Examples

### Create a new role
```json
{
  "operation": "role",
  "action": "create",
  "params": {
    "name": "Moderator",
    "color": "#5865F2",
    "permissions": ["KICK_MEMBERS", "BAN_MEMBERS", "MANAGE_MESSAGES"],
    "guildId": "optional_guild_id"
  }
}
```

### Edit role color and name
```json
{
  "operation": "role",
  "action": "edit",
  "params": {
    "roleId": "123456789",
    "name": "Senior Moderator",
    "color": "#EB459E"
  }
}
```

### Assign role to a member
```json
{
  "operation": "role",
  "action": "add_to_member",
  "params": {
    "userId": "user_id_here",
    "roleId": "role_id_here"
  }
}
```

### Remove role from member
```json
{
  "operation": "role",
  "action": "remove_from_member",
  "params": {
    "userId": "user_id_here",
    "roleId": "role_id_here"
  }
}
```

### Reorder roles
```json
{
  "operation": "role",
  "action": "set_positions",
  "params": {
    "positions": [
      { "roleId": "role1", "position": 5 },
      { "roleId": "role2", "position": 4 },
      { "roleId": "role3", "position": 3 }
    ]
  }
}
```

### Query all roles
```json
{
  "resource": "roles",
  "filters": {
    "guildId": "optional_guild_id"
  }
}
```

## Role Permissions Reference

Common permissions:
- `ADMINISTRATOR` - Full admin access
- `MANAGE_GUILD` - Manage server settings
- `MANAGE_ROLES` - Manage roles
- `MANAGE_CHANNELS` - Manage channels
- `KICK_MEMBERS` - Kick members
- `BAN_MEMBERS` - Ban members
- `MANAGE_MESSAGES` - Delete/pin messages
- `MENTION_EVERYONE` - @everyone and @here
- `MUTE_MEMBERS` - Mute in voice
- `DEAFEN_MEMBERS` - Deafen in voice
- `MOVE_MEMBERS` - Move in voice channels
