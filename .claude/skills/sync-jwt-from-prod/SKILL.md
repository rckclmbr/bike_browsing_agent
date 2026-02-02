---
name: sync-jwt-from-prod
description: Use when the browsing agent gets 403 errors on login, needs JWT_SECRET, or requires authenticated session tokens from the production database
---

# Sync JWT from Production

## Overview

The browsing agent cannot use Strava OAuth (blocked by CloudFront). Instead, we inject JWT session cookies using credentials from the production backend.

**Core principle:** Query production database for user tokens, sync JWT_SECRET to enable cookie-based authentication.

## When to Use

- 403 "Forbidden" errors during login
- "Login failed" or authentication errors
- Setting up a new browsing agent environment
- JWT_SECRET missing from `.env`

## Quick Reference

| What | Location |
|------|----------|
| Backend project | `/home/josh/bike_db_mcp_server` |
| Prod env file | `/home/josh/bike_db_mcp_server/.env.prod` |
| Target env file | `/home/josh/bike_browsing_agent/.env` |
| Database | PostgreSQL on Railway |

## Required Environment Variables

```bash
# From .env.prod
JWT_SECRET="<from backend .env.prod>"

# From database user table
SESSION_USER_ID="<user.id from database>"
SESSION_USER_NAME="<user.name from database>"
```

## Steps

### 1. Get JWT_SECRET from production env

```bash
grep JWT_SECRET /home/josh/bike_db_mcp_server/.env.prod
```

### 2. Get DATABASE_URL and query users

```bash
# Get connection string
grep DATABASE_URL /home/josh/bike_db_mcp_server/.env.prod

# Query user table (replace with actual credentials)
PGPASSWORD='<password>' psql -h <host> -p <port> -U postgres -d railway \
  -c "SELECT id, name FROM \"user\";"
```

### 3. Add to browsing agent .env

```bash
# Append to .env
JWT_SECRET="<value>"
SESSION_USER_ID="<user_id>"
SESSION_USER_NAME="<user_name>"
```

### 4. Verify

```bash
cd /home/josh/bike_browsing_agent
source .venv/bin/activate
python -c "from config import config; print(f'JWT configured for: {config.SESSION_USER_NAME}')"
```

## How Authentication Works

1. `browser.login()` generates a JWT with user ID and name
2. JWT is signed with `JWT_SECRET` (must match production)
3. Cookie injected into browser context
4. Page reload applies authenticated session

## Common Issues

| Problem | Solution |
|---------|----------|
| JWT rejected | JWT_SECRET doesn't match production |
| User not found | SESSION_USER_ID not in database |
| Token expired | Tokens auto-refresh, check `token_expires_at` |
