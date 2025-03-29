from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import os
import logging
from app.services.rbac_service import RBACService
from app.infrastructure.repositories.role_repository_impl import RoleRepositoryImpl
from app.infrastructure.repositories.permission_repository_impl import PermissionRepositoryImpl
from app.infrastructure.database import SessionDep

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
        return credentials.credentials
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def verify_token(token: str = Depends(get_credentials)):
    try:
        AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
        AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
        AUTH0_ISSUER = os.getenv("AUTH0_ISSUER")
        ALGORITHMS = os.getenv("ALGORITHMS", "RS256")

        if not all([AUTH0_DOMAIN, AUTH0_AUDIENCE, AUTH0_ISSUER]):
            logger.error("Missing Auth0 configuration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth0 configuration is incomplete"
            )

        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token).key
        except Exception as e:
            logger.error(f"Failed to get signing key: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature"
            )

        try:
            payload = jwt.decode(
                jwt=token,
                key=signing_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer=AUTH0_ISSUER,
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidAudienceError:
            logger.error("Invalid audience")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid audience"
            )
        except jwt.InvalidIssuerError:
            logger.error("Invalid issuer")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid issuer"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

def check_permission(resource: str, action: str):
    async def permission_checker(
        token_payload: dict = Depends(verify_token),
        rbac_service: RBACService = Depends(get_rbac_service)
    ):
        user_auth_id = token_payload.get("sub")
        if not user_auth_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        has_permission = rbac_service.check_permission(user_auth_id, resource, action)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource}"
            )
        return token_payload
    return permission_checker
