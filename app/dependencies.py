import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.domain.entities.user import User
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.permission_repository_impl import (
    PermissionRepositoryImpl,
)
from app.infrastructure.repositories.role_repository_impl import (
    RoleRepositoryImpl,
)
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.services.rbac_service import RBACService

logger = logging.getLogger(__name__)
oauth2_scheme = HTTPBearer()


def get_rbac_service(session: SessionDep) -> RBACService:
    role_repo = RoleRepositoryImpl(session)
    permission_repo = PermissionRepositoryImpl(session)
    return RBACService(role_repo, permission_repo)


def get_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    try:
        logger.info(f"Getting credentials: {credentials}")
        token = credentials.credentials
        logger.info(
            f"Extracted token: {token[:10]}..."
        )  # Only log the first 10 chars for security
        return token
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


def verify_token(token: str = Depends(get_credentials)):
    logger.info("Starting token verification")
    # logger.info(f"Token type: {type(token)}, Value: {token[:10]}...")  # Only log the first 10 chars

    try:
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"

        try:
            jwks_client = jwt.PyJWKClient(jwks_url)
        except Exception as e:
            logger.error(f"Failed to get the client: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid url signature",
            ) from e

        try:
            # Convert token to bytes if needed
            # token_bytes = token.encode('utf-8') if isinstance(token, str) else token
            logger.debug("Extracting signing key from JWT token")
            signing_key = jwks_client.get_signing_key_from_jwt(token).key
        except Exception as e:
            logger.error(f"Failed to get signing key: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
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
                f"Successfully decoded JWT payload for user: {payload.get('sub')}"
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
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
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
    #         auth_id=auth_id, email=email, picture=picture, created_by="system"
    #     )
    #
    #     user = user_repo.create_user(new_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User"
        )

    return user


class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(
        self,
        token_payload: dict = Depends(verify_token),
        rbac_service: RBACService = Depends(get_rbac_service),
    ):
        user_auth_id = token_payload.get("sub")
        if not user_auth_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        has_permission = rbac_service.check_permission(
            user_auth_id, self.resource, self.action
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.action} on {self.resource}",
            )
        return token_payload


def check_permission(resource: str, action: str):
    return PermissionChecker(resource, action)
