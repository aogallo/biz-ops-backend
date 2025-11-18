# Dev Token Endpoint - Implementation Summary

## 🎉 What Was Implemented

A development-only authentication system that allows you to generate mock JWT tokens instantly for testing, eliminating the need to manually extract tokens from Auth0.

## 📝 Changes Made

### 1. Modified Files

#### `app/dependencies.py`
- Added mock authentication mode check in `verify_token()`
- When `USE_MOCK_AUTH=true`, JWT validation bypasses Auth0 and accepts tokens without signature verification
- Production Auth0 flow remains unchanged

#### `app/main.py`
- Conditionally imports and registers `dev_auth_routes` when `USE_MOCK_AUTH=true`
- Logs when development endpoints are enabled

#### `README.md`
- Added "Development Authentication (Mock Mode)" section with usage examples
- Updated environment variables reference table to include `USE_MOCK_AUTH`
- Added quick tip in Quick Start section

### 2. New Files

#### `app/routes/dev_auth_routes.py`
New router with two endpoints:
- `POST /api/dev/token` - Generates mock JWT tokens
- `GET /api/dev/whoami` - Verifies current authenticated user

#### `DEV_AUTH_GUIDE.md`
Comprehensive guide covering:
- Quick start instructions
- Postman and curl examples
- Troubleshooting tips
- Workflow examples
- Architecture explanation

## 🚀 How to Use

### Step 1: Enable Mock Mode

Add to your `.env` file:
```bash
USE_MOCK_AUTH=true
```

### Step 2: Start the Server

```bash
./run_dev.sh
```

### Step 3: Get a Token

**Quick Command:**
```bash
curl -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{"auth_id": "dev_user", "email": "dev@example.com"}'
```

**In Postman:**
1. POST to `http://localhost:8000/api/dev/token`
2. Body (JSON):
   ```json
   {
     "auth_id": "dev_user",
     "email": "dev@example.com"
   }
   ```
3. Copy the `access_token` from response

### Step 4: Use the Token

In Postman:
- Authorization tab → Type: Bearer Token
- Paste the token
- Make requests to any protected endpoint ✅

## 🔒 Security

- **Development Only**: Endpoints return 404 when `USE_MOCK_AUTH=false`
- **No Production Impact**: Auth0 validation fully enforced in production
- **Logged Activity**: Mock mode is logged on startup for visibility
- **Same Authorization**: RBAC and permissions still enforced normally

## ✨ Benefits

✅ **Instant tokens** - No Auth0 dashboard navigation needed
✅ **Offline development** - Works without internet
✅ **Multiple test users** - Create different users on demand
✅ **Faster iteration** - Test endpoints immediately
✅ **Production safe** - Automatically disabled when deployed

## 📚 Documentation

- **Quick Reference**: See [README.md](README.md#development-authentication-mock-mode)
- **Detailed Guide**: See [DEV_AUTH_GUIDE.md](DEV_AUTH_GUIDE.md)
- **API Docs**: Visit http://localhost:8000/docs when server is running

## 🧪 Testing the Implementation

Run these commands to verify everything works:

```bash
# 1. Enable mock mode
echo "USE_MOCK_AUTH=true" > .env

# 2. Start server (in background or new terminal)
./run_dev.sh

# 3. Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{"auth_id": "dev_user", "email": "dev@example.com"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 4. Test authentication
curl -X GET http://localhost:8000/api/dev/whoami \
  -H "Authorization: Bearer $TOKEN"

# Should return your user info with mock_mode: true
```

## 🔄 Switching Between Mock and Real Auth

### Use Mock Auth (Development)
```bash
USE_MOCK_AUTH=true
```
- Use `/api/dev/token` endpoint
- No Auth0 configuration needed
- Faster development cycle

### Use Real Auth (Production/Testing)
```bash
USE_MOCK_AUTH=false  # or remove the variable
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/
```
- Get tokens from Auth0 dashboard
- Full Auth0 validation
- Tests production authentication

## 📋 Files Modified/Created

### Modified
1. `app/dependencies.py` - Added mock auth bypass logic
2. `app/main.py` - Registered dev routes conditionally
3. `README.md` - Added documentation

### Created
1. `app/routes/dev_auth_routes.py` - Dev token endpoints
2. `DEV_AUTH_GUIDE.md` - Comprehensive usage guide
3. `IMPLEMENTATION_SUMMARY.md` - This file

## ✅ All Implementation Tasks Completed

- [x] Add mock auth bypass logic to dependencies.py
- [x] Create dev_auth_routes.py with /dev/token endpoint
- [x] Register dev routes in main.py conditionally
- [x] Document dev token usage in README/docs

## 🎯 Next Steps

1. Set `USE_MOCK_AUTH=true` in your `.env` file
2. Restart your development server
3. Test the `/api/dev/token` endpoint
4. Update your Postman collection with the new workflow
5. Enjoy faster development! 🚀

---

**Questions?** Check [DEV_AUTH_GUIDE.md](DEV_AUTH_GUIDE.md) for troubleshooting and examples.
