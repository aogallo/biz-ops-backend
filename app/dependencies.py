import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.domain.entities.user import User
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)

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
            print("token data", token_data)
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


def get_current_user(
    token_payload: dict = Depends(verify_token),
    session: SessionDep = Depends(),
) -> User:
    """
    Get the current user from the token payload.
    If the user doesn't exist in the database, create it.
    """
    auth_id = token_payload.get("sub")
    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Create a user repository with the session
    user_repo = UserRepositoryImpl(session)

    # Try to find the user by auth_id
    user = user_repo.get_user_by_id(auth_id)

    # if not user:
    #     # If user doesn't exist, create a new one
    #     email = token_payload.get("email", "")
    #     picture = token_payload.get("picture", "")
    #
    #     new_user = User(
    #         auth_id=auth_id,
    #         email=email,
    #         picture=picture,
    #         created_by="system"
    #     )
    #
    #     user = user_repo.create_user(new_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User"
        )

    return user


# class PermissionChecker:
#     def __init__(self, resource: str, action: str):
#         self.resource = resource
#         self.action = action
#
#     def __call__(
#         self,
#         token_payload: dict = Depends(verify_token),
#         rbac_service: RBACService = Depends(get_rbac_service),
#     ):
#         user_auth_id = token_payload.get("sub")
#         if not user_auth_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token payload",
#             )
#
#         has_permission = rbac_service.check_permission(
#             user_auth_id, self.resource, self.action
#         )
#         if not has_permission:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=(
#                     f"Permission denied: {self.action} "
#                     f"on {self.resource}"
#                 ),
#             )
#         return token_payload
#
#
# def check_permission(resource: str, action: str):
#     return PermissionChecker(resource, action)
