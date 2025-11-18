# Development Authentication Guide

This guide explains how to use the development authentication system for local testing without needing to extract tokens from Auth0.

## Quick Start

### 1. Enable Mock Authentication

Add this to your `.env` file:

```bash
USE_MOCK_AUTH=true
```

### 2. Start Your Server

```bash
./run_dev.sh
# or
uvicorn app.main:app --reload
```

You should see this log message:
```
Development authentication endpoints enabled at /api/dev/*
```

### 3. Get a Development Token

**Using curl:**

```bash
curl -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{
    "auth_id": "dev_user",
    "email": "dev@example.com"
  }'
```

**Using Postman:**

1. Create a new POST request to `http://localhost:8000/api/dev/token`
2. Set Headers: `Content-Type: application/json`
3. Set Body (raw JSON):
   ```json
   {
     "auth_id": "dev_user",
     "email": "dev@example.com"
   }
   ```
4. Send the request

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "user": {
    "auth_id": "dev_user",
    "email": "dev@example.com",
    "picture": "https://via.placeholder.com/150"
  }
}
```

### 4. Use the Token

**In Postman:**

1. Copy the `access_token` value (without quotes)
2. Go to your request's **Authorization** tab
3. Select **Type: Bearer Token**
4. Paste the token in the **Token** field
5. Now you can call any protected endpoint!

**Using curl:**

```bash
TOKEN="your-access-token-here"

curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Verify Your Token (Optional)

Check that authentication is working:

```bash
curl -X GET http://localhost:8000/api/dev/whoami \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{
  "auth_id": "dev_user",
  "email": "dev@example.com",
  "picture": "https://via.placeholder.com/150",
  "created_at": "2025-11-18T10:30:00.000000",
  "mock_mode": true
}
```

## Customizing the Dev User

You can create tokens for different test users:

```bash
curl -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{
    "auth_id": "admin_user",
    "email": "admin@example.com",
    "picture": "https://example.com/avatar.png"
  }'
```

Each unique `auth_id` will create a new user in your database.

## How It Works

### Architecture

1. **Mock Mode Check**: When `USE_MOCK_AUTH=true`, the `/api/dev/*` endpoints become available
2. **Token Generation**: The `/dev/token` endpoint creates a JWT token with user info
3. **Bypass Validation**: The `verify_token` dependency skips Auth0 validation in mock mode
4. **User Creation**: First time a user is requested, it's automatically created in the database
5. **Normal Flow**: Everything else works exactly like production - same endpoints, same logic

### What Gets Bypassed

- Auth0 JWKS key fetching
- JWT signature verification
- Audience/issuer validation
- Token expiration checks (tokens still have 7-day expiry in payload)

### What Stays the Same

- User lookup in database
- Authorization logic (RBAC, permissions)
- All business logic
- API endpoints and responses

## Production Safety

The dev endpoints are **completely disabled** in production:

- When `USE_MOCK_AUTH=false` (default), `/api/dev/*` endpoints return 404
- Mock mode is checked at startup and logged
- Auth0 validation is fully enforced when mock mode is off

## Troubleshooting

### "Endpoint not available in production mode"

**Problem:** Getting 404 on `/api/dev/token`

**Solution:** Make sure `USE_MOCK_AUTH=true` is set in your `.env` file and restart the server.

### "Invalid authentication credentials"

**Problem:** Token is rejected when calling protected endpoints

**Solutions:**
1. Make sure you're using `Bearer` token type (not Basic Auth)
2. Check that token is copied completely (JWT tokens are long!)
3. Verify mock mode is enabled in your `.env`
4. Restart the server after changing `.env`

### "Invalid User"

**Problem:** Token is valid but user doesn't exist

**Solution:** The user is created automatically on first `/dev/token` call. If you're using a custom `auth_id`, make sure you generated a token for that user first.

### Server doesn't show dev endpoints enabled

**Problem:** Log doesn't show "Development authentication endpoints enabled"

**Solution:**
1. Check `.env` file has `USE_MOCK_AUTH=true`
2. Restart the development server
3. Verify no syntax errors in `.env` file

## Workflow Example

Here's a typical development workflow:

```bash
# 1. Set up environment
echo "USE_MOCK_AUTH=true" >> .env

# 2. Start server
./run_dev.sh

# 3. Get token and save it
TOKEN=$(curl -s -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{"auth_id": "dev_user", "email": "dev@example.com"}' \
  | jq -r '.access_token')

# 4. Use token for API calls
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Verify who you are
curl -X GET http://localhost:8000/api/dev/whoami \
  -H "Authorization: Bearer $TOKEN"
```

## Switching to Production Auth

When you're ready to test with real Auth0:

1. Set `USE_MOCK_AUTH=false` in `.env` (or remove it - false is default)
2. Set up Auth0 configuration:
   ```bash
   AUTH0_DOMAIN=your-tenant.auth0.com
   AUTH0_AUDIENCE=https://your-api-audience
   AUTH0_ISSUER=https://your-tenant.auth0.com/
   ```
3. Restart the server
4. Get real tokens from Auth0 dashboard → Applications → Your App → Quick Start → Test tab
5. Use the real Auth0 token the same way you used dev tokens

## Benefits

✅ **No Manual Token Extraction** - No need to navigate Auth0 dashboard
✅ **Faster Development** - Get tokens in milliseconds
✅ **Offline Development** - Works without internet connection
✅ **Multiple Test Users** - Create different users instantly
✅ **Same Flow** - Tests real authentication logic
✅ **Production Safe** - Automatically disabled when deployed

## Additional Resources

- [README.md](README.md) - Main project documentation
- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Environment configuration guide
- [Auth0 Documentation](https://auth0.com/docs) - For production Auth0 setup
