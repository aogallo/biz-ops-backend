from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import os

oauth2_scheme = HTTPBearer()


def get_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    try:
        return credentials.credentials
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication"
        )


def verify_token(token: str = Depends(get_credentials)):
    try:
        AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your.domain.us.auth0.com")
        # is the indentifier
        AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "https://your.domain.us")
        AUTH0_ISSUER = os.getenv("AUTH0_ISSUER", "https://your.domain.us.auth0.com/")
        ALGORITHMS = os.getenv("ALGORITHMS", "RS256")

        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

        jwks_client = jwt.PyJWKClient(jwks_url)

        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            jwt=token,
            key=signing_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )

        print(payload)

        return payload
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
