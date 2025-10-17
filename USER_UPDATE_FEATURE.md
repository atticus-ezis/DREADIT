# User Update Feature

## Overview

Custom user update serializer that includes the `bio` field and automatically sends email verification when a user changes their email address.

## Implementation

### Files Created/Modified

1. **`users/api/v1/serializers.py`** - Custom serializers for user updates
2. **`dreadit/settings.py`** - Configuration to use custom serializer
3. **`users/tests/test_user_update.py`** - Comprehensive test suite

## API Endpoint

**URL:** `PATCH /api/v1/auth/user/` or `PUT /api/v1/auth/user/`

**Authentication:** Required (JWT via cookie or Authorization header)

### Request Example

```bash
PATCH /api/v1/auth/user/
Content-Type: application/json
Authorization: Bearer <token>  # or cookies automatically sent

{
  "username": "newusername",
  "bio": "Software developer",
  "first_name": "John",
  "last_name": "Doe",
  "email": "newemail@example.com"  # Will trigger verification email
}
```

### Response Example

```json
{
  "pk": 1,
  "username": "newusername",
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software developer",
  "registration_method": "local"
}
```

## Features

### Updatable Fields

- `username` - Username
- `email` - Email address (triggers verification)
- `first_name` - First name
- `last_name` - Last name
- `bio` - User biography (custom field)

### Read-Only Fields

- `registration_method` - How the user registered (local/google/facebook/twitter)
- `pk` - User ID

### Email Change Behavior

When a user updates their email address:

1. ✅ Old email is marked as non-primary and unverified
2. ✅ New email address is created/updated as primary but unverified
3. ✅ Verification email is automatically sent to the new email address
4. ✅ Email contains a frontend verification link
5. ✅ User must verify the new email to complete the change

## Test Coverage

All tests passing (6/6):

1. ✅ `test_get_user_details` - Retrieve current user info
2. ✅ `test_update_user_bio` - Update bio field
3. ✅ `test_update_user_username` - Update username
4. ✅ `test_update_email_sends_verification` - Email change triggers verification
5. ✅ `test_update_multiple_fields` - Update multiple fields at once
6. ✅ `test_update_requires_authentication` - Requires authentication

## Configuration

In `dreadit/settings.py`:

```python
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "jwt-auth",
    "JWT_AUTH_REFRESH_COOKIE": "jwt-refresh-token",
    "JWT_AUTH_HTTPONLY": True,
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "dj_rest_auth.serializers.PasswordResetConfirmSerializer",
    "USER_DETAILS_SERIALIZER": "users.api.v1.serializers.CustomUserUpdateSerializer",  # Added
}
```

## Usage Examples

### Get Current User

```bash
GET /api/v1/auth/user/
```

### Update Bio Only

```bash
PATCH /api/v1/auth/user/
{
  "bio": "New bio text"
}
```

### Change Email (triggers verification)

```bash
PATCH /api/v1/auth/user/
{
  "email": "newemail@example.com"
}
```

User will receive a verification email with a link to confirm the new email address.

### Update Multiple Fields

```bash
PATCH /api/v1/auth/user/
{
  "username": "newname",
  "bio": "Updated bio",
  "first_name": "John",
  "last_name": "Doe"
}
```

## Security Considerations

- Email changes require verification before becoming active
- Old email addresses are preserved but marked inactive
- Authentication required for all update operations
- JWT tokens used for secure authentication
- HTTP-only cookies protect against XSS attacks
