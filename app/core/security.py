"""Security utilities for password hashing, JWT token generation, and secure token creation.

This module provides cryptographic functions for:
- Password hashing using Argon2id (more secure than bcrypt)
- JWT token generation for access and refresh tokens
- Secure random token generation for invitations
"""

import secrets
from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# ==============================================================================
# PASSWORD HASHING
# ==============================================================================

# Argon2id configuration for password hashing
# Argon2id is the recommended choice for password hashing (OWASP, 2024)
# It's memory-hard and resistant to GPU/ASIC attacks
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MiB (recommended for interactive logins)
    argon2__time_cost=3,  # Number of iterations
    argon2__parallelism=4,  # Number of parallel threads
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> len(hashed) > 50
        True
    """
    return pwd_context.hash(password)  # type: ignore[no-any-return]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPass", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==============================================================================
# JWT TOKEN GENERATION
# ==============================================================================


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token (typically {"sub": user_id})
        expires_delta: Optional expiration time delta. Defaults to 30 minutes.

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user123"})
        >>> len(token) > 100
        True
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Refresh tokens have longer expiration times (7 days by default)
    and are used to obtain new access tokens.

    Args:
        data: Dictionary of claims to encode in the token

    Returns:
        Encoded JWT refresh token string

    Example:
        >>> token = create_refresh_token({"sub": "user123"})
        >>> len(token) > 100
        True
    """
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of decoded token claims

    Raises:
        JWTError: If token is invalid or expired

    Example:
        >>> token = create_access_token({"sub": "user123"})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'user123'
    """
    return jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )


# ==============================================================================
# SECURE TOKEN GENERATION
# ==============================================================================


def generate_invitation_token() -> str:
    """
    Generate a cryptographically secure random token for user invitations.

    Uses secrets.token_urlsafe() which generates a URL-safe base64-encoded
    random token with 256 bits of entropy (32 bytes).

    Returns:
        URL-safe random token string (43 characters)

    Example:
        >>> token1 = generate_invitation_token()
        >>> token2 = generate_invitation_token()
        >>> len(token1) == 43
        True
        >>> token1 != token2
        True
    """
    return secrets.token_urlsafe(32)  # 32 bytes = 256 bits of entropy


def generate_password_reset_token() -> str:
    """
    Generate a cryptographically secure random token for password resets.

    Uses the same security level as invitation tokens.

    Returns:
        URL-safe random token string (43 characters)

    Example:
        >>> token = generate_password_reset_token()
        >>> len(token) == 43
        True
    """
    return secrets.token_urlsafe(32)


# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================


def validate_password(password: str) -> tuple[bool, str | None]:
    """
    Validate password strength.

    Password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character

    Args:
        password: Password string to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "Error message")

    Example:
        >>> validate_password("Short")
        (False, 'Password must be at least 8 characters long')
        >>> validate_password("SecurePass123!")
        (True, None)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    special_chars = '!@#$%^&*(),.?":{}|<>'
    if not any(c in special_chars for c in password):
        return (
            False,
            "Password must contain at least one special character",
        )

    return True, None
