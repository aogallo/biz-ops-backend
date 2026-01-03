"""OAuth provider configuration for Google and GitHub authentication.

Provides OAuth client setup and helper functions for social login integration.
"""

import secrets
from typing import Dict

from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2

from app.core.config import settings


def get_google_oauth_client() -> GoogleOAuth2:
    """Get configured Google OAuth2 client.

    Returns:
        GoogleOAuth2 client instance

    Example:
        >>> client = get_google_oauth_client()
        >>> auth_url = await client.get_authorization_url(
        ...     redirect_uri="http://localhost:8000/auth/google/callback",
        ...     scope=["openid", "email", "profile"],
        ... )
    """
    return GoogleOAuth2(
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )


def get_github_oauth_client() -> GitHubOAuth2:
    """Get configured GitHub OAuth2 client.

    Returns:
        GitHubOAuth2 client instance

    Example:
        >>> client = get_github_oauth_client()
        >>> auth_url = await client.get_authorization_url(
        ...     redirect_uri="http://localhost:8000/auth/github/callback",
        ...     scope=["user:email", "read:user"],
        ... )
    """
    return GitHubOAuth2(
        client_id=settings.GITHUB_OAUTH_CLIENT_ID,
        client_secret=settings.GITHUB_OAUTH_CLIENT_SECRET,
    )


def generate_oauth_state() -> str:
    """Generate a secure random state parameter for OAuth flow.

    The state parameter prevents CSRF attacks by validating that the
    callback originated from the same session that initiated the request.

    Returns:
        URL-safe random string (32 bytes = 256 bits)

    Example:
        >>> state = generate_oauth_state()
        >>> len(state) == 43  # base64 encoding of 32 bytes
        True
    """
    return secrets.token_urlsafe(32)


def validate_oauth_state(
    received_state: str, stored_state: str | None
) -> bool:
    """Validate OAuth state parameter to prevent CSRF attacks.

    Args:
        received_state: State parameter from OAuth callback
        stored_state: State parameter stored in session during authorization

    Returns:
        True if states match, False otherwise

    Example:
        >>> state = generate_oauth_state()
        >>> validate_oauth_state(state, state)
        True
        >>> validate_oauth_state(state, "different_state")
        False
    """
    if not stored_state:
        return False
    return secrets.compare_digest(received_state, stored_state)


# OAuth scopes for each provider
GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
]

GITHUB_SCOPES = [
    "user:email",
    "read:user",
]


def get_oauth_redirect_uri(provider: str) -> str:
    """Get the OAuth redirect URI for a provider.

    Args:
        provider: OAuth provider name ("google" or "github")

    Returns:
        Full redirect URI for the provider

    Example:
        >>> get_oauth_redirect_uri("google")
        'http://localhost:8000/api/v1/auth/google/callback'
    """
    base_url = settings.BACKEND_URL or "http://localhost:8000"
    return f"{base_url}/api/v1/auth/{provider}/callback"
