"""OAuth authentication routes for Google and GitHub."""

import secrets
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from httpx_oauth.errors import GetIdEmailError
from sqlmodel import Session, select

from app.core.auth.oauth import (
    GITHUB_SCOPES,
    GOOGLE_SCOPES,
    generate_oauth_state,
    get_github_oauth_client,
    get_google_oauth_client,
    get_oauth_redirect_uri,
    validate_oauth_state,
)
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.database import get_session
from app.dependencies import get_current_user
from app.internal.user.entity import OAuthAccount, User

router = APIRouter()


# ==============================================================================
# GOOGLE OAUTH
# ==============================================================================


@router.get(
    "/auth/google/authorize",
    tags=["Authentication"],
)
async def google_authorize(redirect_uri: str | None = None):
    """Initiate Google OAuth authorization flow.

    Query Parameters:
        redirect_uri: Optional frontend URL to redirect after successful auth

    Returns:
        Redirect to Google OAuth consent screen
    """
    client = get_google_oauth_client()

    # Generate CSRF protection state
    state = generate_oauth_state()

    # Store state in session (in production, use Redis or database)
    # For now, we'll pass it through the OAuth flow and validate in callback

    # Get authorization URL
    callback_url = get_oauth_redirect_uri("google")
    authorization_url = await client.get_authorization_url(
        redirect_uri=callback_url,
        scope=GOOGLE_SCOPES,
        extras_params={"state": state},
    )

    # In production, store state in session/Redis with expiration
    # For now, we'll trust the OAuth provider to return it

    return RedirectResponse(url=authorization_url)


@router.get(
    "/auth/google/callback",
    tags=["Authentication"],
)
async def google_callback(
    request: Request,
    code: str,
    state: str | None = None,
    session: Session = Depends(get_session),
):
    """Handle Google OAuth callback and create/login user.

    Query Parameters:
        code: Authorization code from Google
        state: CSRF protection state parameter

    Returns:
        Access token and user data
    """
    # TODO: Validate state parameter in production
    # For now, we skip state validation

    client = get_google_oauth_client()

    try:
        # Exchange code for access token
        callback_url = get_oauth_redirect_uri("google")
        token = await client.get_access_token(code, callback_url)

        # Get user info from Google
        user_id, user_email = await client.get_id_email(token["access_token"])
    except GetIdEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user info from Google: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        ) from e

    # Check if user exists with this email
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()

    if not user:
        # For now, reject new users without invitation
        # In Phase 3, we'll link OAuth to invitation acceptance
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found. Please accept an invitation first.",
        )

    # Check if OAuth account already linked
    statement = select(OAuthAccount).where(
        OAuthAccount.user_id == user.id,
        OAuthAccount.oauth_name == "google",
    )
    oauth_account = session.exec(statement).first()

    if not oauth_account:
        # Link OAuth account to existing user
        oauth_account = OAuthAccount(
            user_id=user.id,
            oauth_name="google",
            access_token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            expires_at=token.get("expires_at"),
            account_id=user_id,
            account_email=user_email,
        )
        session.add(oauth_account)
        session.commit()
    else:
        # Update existing OAuth account tokens
        oauth_account.access_token = token["access_token"]
        oauth_account.refresh_token = token.get("refresh_token")
        oauth_account.expires_at = token.get("expires_at")
        session.add(oauth_account)
        session.commit()

    # Generate JWT tokens for our application
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Redirect to frontend with tokens
    frontend_url = (
        settings.FRONTEND_URL
        + f"/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    )

    return RedirectResponse(url=frontend_url)


# ==============================================================================
# GITHUB OAUTH
# ==============================================================================


@router.get(
    "/auth/github/authorize",
    tags=["Authentication"],
)
async def github_authorize(redirect_uri: str | None = None):
    """Initiate GitHub OAuth authorization flow.

    Query Parameters:
        redirect_uri: Optional frontend URL to redirect after successful auth

    Returns:
        Redirect to GitHub OAuth consent screen
    """
    client = get_github_oauth_client()

    # Generate CSRF protection state
    state = generate_oauth_state()

    # Get authorization URL
    callback_url = get_oauth_redirect_uri("github")
    authorization_url = await client.get_authorization_url(
        redirect_uri=callback_url,
        scope=GITHUB_SCOPES,
        extras_params={"state": state},
    )

    return RedirectResponse(url=authorization_url)


@router.get(
    "/auth/github/callback",
    tags=["Authentication"],
)
async def github_callback(
    request: Request,
    code: str,
    state: str | None = None,
    session: Session = Depends(get_session),
):
    """Handle GitHub OAuth callback and create/login user.

    Query Parameters:
        code: Authorization code from GitHub
        state: CSRF protection state parameter

    Returns:
        Access token and user data
    """
    # TODO: Validate state parameter in production

    client = get_github_oauth_client()

    try:
        # Exchange code for access token
        callback_url = get_oauth_redirect_uri("github")
        token = await client.get_access_token(code, callback_url)

        # Get user info from GitHub
        user_id, user_email = await client.get_id_email(token["access_token"])
    except GetIdEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user info from GitHub: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        ) from e

    # Check if user exists with this email
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()

    if not user:
        # For now, reject new users without invitation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found. Please accept an invitation first.",
        )

    # Check if OAuth account already linked
    statement = select(OAuthAccount).where(
        OAuthAccount.user_id == user.id,
        OAuthAccount.oauth_name == "github",
    )
    oauth_account = session.exec(statement).first()

    if not oauth_account:
        # Link OAuth account to existing user
        oauth_account = OAuthAccount(
            user_id=user.id,
            oauth_name="github",
            access_token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            expires_at=token.get("expires_at"),
            account_id=user_id,
            account_email=user_email,
        )
        session.add(oauth_account)
        session.commit()
    else:
        # Update existing OAuth account tokens
        oauth_account.access_token = token["access_token"]
        oauth_account.refresh_token = token.get("refresh_token")
        oauth_account.expires_at = token.get("expires_at")
        session.add(oauth_account)
        session.commit()

    # Generate JWT tokens for our application
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Redirect to frontend with tokens
    frontend_url = (
        settings.FRONTEND_URL
        + f"/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    )

    return RedirectResponse(url=frontend_url)


# ==============================================================================
# LINK OAUTH TO EXISTING ACCOUNT
# ==============================================================================


@router.post(
    "/auth/link-oauth",
    tags=["Authentication"],
)
async def link_oauth_account(
    provider: str,
    code: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Link an OAuth provider to the current user's account.

    Body Parameters:
        provider: OAuth provider name ("google" or "github")
        code: Authorization code from OAuth provider

    Returns:
        Success message

    Raises:
        HTTPException: 400 if provider invalid or linking fails
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OAuth provider: {provider}",
        )

    # Get OAuth client
    if provider == "google":
        client = get_google_oauth_client()
    else:
        client = get_github_oauth_client()

    try:
        # Exchange code for access token
        callback_url = get_oauth_redirect_uri(provider)
        token = await client.get_access_token(code, callback_url)

        # Get user info from provider
        provider_user_id, provider_email = await client.get_id_email(
            token["access_token"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to link OAuth account: {str(e)}",
        ) from e

    # Verify email matches current user
    if provider_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth email ({provider_email}) does not match your account email ({current_user.email})",
        )

    # Check if OAuth account already exists
    statement = select(OAuthAccount).where(
        OAuthAccount.user_id == current_user.id,
        OAuthAccount.oauth_name == provider,
    )
    oauth_account = session.exec(statement).first()

    if oauth_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.capitalize()} account already linked",
        )

    # Create OAuth account link
    oauth_account = OAuthAccount(
        user_id=current_user.id,
        oauth_name=provider,
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        expires_at=token.get("expires_at"),
        account_id=provider_user_id,
        account_email=provider_email,
    )
    session.add(oauth_account)
    session.commit()

    return {
        "message": f"{provider.capitalize()} account successfully linked",
        "provider": provider,
        "email": provider_email,
    }
