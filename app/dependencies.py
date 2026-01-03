import logging
from datetime import UTC
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import settings
from app.core.exceptions import AuthorizationError
from app.database import get_session
from app.internal.user.entity import User, UserCompanyAccess

logger = logging.getLogger(__name__)
oauth2_scheme = HTTPBearer()


class JWKSClientManager:
    """Singleton manager for JWKS client to reuse across requests."""

    def __init__(self):
        self._client = None

    def get_client(self):
        """
        Get or create a singleton JWKS client with caching enabled.
        This reduces requests to Auth0 and prevents rate limiting.
        """
        if self._client is None:
            jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"

            # Custom headers to avoid 403 Forbidden from Auth0
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Python-JWT/2.0)",
                "Accept": "application/json",
            }

            logger.info("Initializing JWKS client for URL: %s", jwks_url)

            try:
                self._client = jwt.PyJWKClient(
                    jwks_url,
                    headers=headers,
                    cache_keys=True,  # Enable key caching
                    max_cached_keys=16,  # Cache up to 16 keys
                    cache_jwk_set=True,  # Cache the entire JWKS
                    lifespan=3600,  # Cache for 1 hour (3600 seconds)
                )
                logger.info(
                    "JWKS client initialized successfully with caching enabled"
                )
            except Exception as e:
                logger.error("Failed to initialize JWKS client: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        f"Failed to initialize authentication client: {str(e)}"
                    ),
                ) from e

        return self._client


# Module-level singleton instance
_jwks_manager = JWKSClientManager()


def get_jwks_client():
    """Get the JWKS client from the singleton manager."""
    return _jwks_manager.get_client()


def get_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    """
    Get the credentials from the authorization header.
    """
    try:
        logger.info("Getting credentials: %s", credentials)
        token = credentials.credentials
        logger.info(
            "Extracted token: %s...", token[:10]
        )  # Only log the first 10 chars for security
        return token
    except Exception as e:
        logger.error("Authentication error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


def verify_token(token: str = Depends(get_credentials)):
    """
    Verify the token.
    """
    logger.info("Starting token verification")

    try:
        # Get the singleton JWKS client with caching
        jwks_client = get_jwks_client()

        try:
            logger.debug("Extracting signing key from JWT token")
            token_data = jwks_client.get_signing_key_from_jwt(token)
            signing_key = token_data.key
        except Exception as e:
            logger.error("Failed to get signing key: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Fail to fetch data from the url, err: "{str(e)}"',
            ) from e

        try:
            payload = jwt.decode(
                jwt=token,
                key=signing_key,
                algorithms=settings.ALGORITHMS,
                audience=settings.AUTH0_AUDIENCE,
                issuer=settings.AUTH0_ISSUER,
            )
            logger.debug(
                "Successfully decoded JWT payload for user: %s", payload
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            ) from None
        except jwt.InvalidAudienceError:
            logger.error("Invalid audience")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid audience",
            ) from None
        except jwt.InvalidIssuerError:
            logger.error("Invalid issuer")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid issuer",
            ) from None
        except jwt.InvalidTokenError as e:
            logger.error("Invalid token: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error during token verification: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        ) from e


def verify_self_hosted_token(token: str) -> dict:
    """
    Verify self-hosted JWT token.

    Returns:
        Token payload with user ID

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        logger.debug(
            "Successfully decoded self-hosted JWT for user: %s",
            payload.get("sub"),
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Self-hosted token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from None
    except jwt.InvalidTokenError as e:
        logger.error("Invalid self-hosted token: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


def get_current_user(
    token: str = Depends(get_credentials),
    session: Session = Depends(get_session),
) -> User:
    """
    Get the current user from the token payload (dual authentication).

    Priority:
    1. Try self-hosted JWT first (if ENABLE_SELF_HOSTED_AUTH)
    2. Fall back to Auth0 JWT (if ENABLE_AUTH0)
    3. Raise 401 if both fail

    Raises:
        HTTPException: If authentication fails
    """
    user = None
    last_error = None

    # Try self-hosted authentication first
    if settings.ENABLE_SELF_HOSTED_AUTH:
        try:
            payload = verify_self_hosted_token(token)
            user_id = payload.get("sub")

            # Fetch user from database by ID
            user = session.get(User, user_id)

            if user:
                logger.debug(
                    "User authenticated via self-hosted JWT: %s", user.email
                )
                return user
            else:
                logger.warning(
                    "User ID from self-hosted token not found: %s", user_id
                )

        except HTTPException as e:
            last_error = e
            logger.debug("Self-hosted authentication failed, trying Auth0...")
        except Exception as e:
            last_error = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
            logger.debug("Self-hosted authentication error: %s", str(e))

    # Fall back to Auth0 authentication
    if settings.ENABLE_AUTH0 and user is None:
        try:
            token_payload = verify_token(token)
            auth0_user_id = str(token_payload.get("sub"))

            # Fetch user from database
            statement = select(User).where(User.auth0_user_id == auth0_user_id)
            user = session.exec(statement).first()

            if not user:
                # Auto-create user on first login
                logger.info(
                    "Creating new user for Auth0 ID: %s", auth0_user_id
                )
                user = User(
                    auth0_user_id=auth0_user_id,
                    auth_id=auth0_user_id,
                    email=token_payload.get("email", ""),
                    first_name=token_payload.get("given_name"),
                    last_name=token_payload.get("family_name"),
                    is_active=False,
                    is_verified=token_payload.get("email_verified", False),
                    # Set temporary password hash for Auth0 users
                    hashed_password="auth0_user",
                )
                session.add(user)
                session.commit()
                session.refresh(user)

            logger.debug("User authenticated via Auth0: %s", user.email)
            return user

        except HTTPException as e:
            last_error = e
            logger.debug("Auth0 authentication also failed")
        except Exception as e:
            last_error = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
            logger.debug("Auth0 authentication error: %s", str(e))

    # If we get here, both methods failed
    if last_error:
        raise last_error
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed - no auth method enabled or succeeded",
        )


def verify_company_access(
    company_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    """
    Verify user has access to the requested company.

    Raises:
        AuthorizationError: If user doesn't have access
    """
    # Check if user has access to this company
    statement = select(UserCompanyAccess).where(
        UserCompanyAccess.user_id == current_user.id,
        UserCompanyAccess.company_id == company_id,
    )
    access = session.exec(statement).first()

    if not access:
        logger.warning(
            "User %s attempted to access company %s without permission",
            current_user.auth0_user_id,
            company_id,
        )
        raise AuthorizationError(
            f"User does not have access to company {company_id}"
        )


def verify_organization_access(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Verify user belongs to the requested organization.

    Raises:
        AuthorizationError: If user doesn't belong to org
    """
    if current_user.organization_id != organization_id:
        logger.warning(
            "User %s attempted to access organization %s but belongs to %s",
            current_user.auth0_user_id,
            organization_id,
            current_user.organization_id,
        )
        raise AuthorizationError(
            f"User does not belong to organization {organization_id}"
        )


def require_permission(permission_code: str):
    """
    Dependency factory for permission-based access control.

    Usage:
        @router.post("/products", dependencies=[Depends(require_permission("product:create"))])

    Args:
        permission_code: Permission code (e.g., "product:create")

    Returns:
        Dependency function that checks user permission

    Raises:
        HTTPException: 403 if user doesn't have permission
    """

    def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session),
    ) -> None:
        from app.internal.permission.service import PermissionService

        # Super admins have all permissions
        if current_user.is_superuser:
            return

        # Check permission via service
        service = PermissionService(session, current_user)
        has_permission = service.check_user_has_permission(
            user_id=current_user.id,
            permission_code=permission_code,
        )

        if not has_permission:
            logger.warning(
                "User %s denied access - missing permission: %s",
                current_user.email,
                permission_code,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_code}",
            )

    return permission_checker


def require_module(module_name: str):
    """
    Dependency factory for module subscription access control.

    Usage:
        @router.post("/sat/upload", dependencies=[Depends(require_module("sat"))])

    Args:
        module_name: Module name (e.g., "inventory", "accounting", "sat", "crm")

    Returns:
        Dependency function that checks organization module access

    Raises:
        HTTPException: 402 if organization doesn't have module access
    """

    def module_checker(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session),
    ) -> None:
        from sqlmodel import select

        from app.internal.organization.entity import OrganizationModule

        # Super admins bypass module checks
        if current_user.is_superuser:
            return

        # Check if user belongs to an organization
        if not current_user.organization_id:
            logger.warning(
                "User %s attempted to access module %s but has no organization",
                current_user.email,
                module_name,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must belong to an organization",
            )

        # Check if organization has active module subscription
        statement = select(OrganizationModule).where(
            OrganizationModule.organization_id == current_user.organization_id,
            OrganizationModule.module_name == module_name,
            OrganizationModule.is_active == True,  # noqa: E712
        )
        module_access = session.exec(statement).first()

        if not module_access:
            logger.warning(
                "Organization %s denied access - no active subscription for module: %s",
                current_user.organization_id,
                module_name,
            )
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Module subscription required: {module_name}",
            )

        # Check if subscription has expired
        from datetime import datetime

        if (
            module_access.expires_at
            and datetime.now(UTC) > module_access.expires_at
        ):
            logger.warning(
                "Organization %s module subscription expired: %s",
                current_user.organization_id,
                module_name,
            )
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Module subscription expired: {module_name}",
            )

    return module_checker
