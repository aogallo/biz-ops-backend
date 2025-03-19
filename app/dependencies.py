from fastapi.security import HTTPBearer

oauth2_scheme = HTTPBearer()


class VerifyTokne:
    """Does all the token verification using PyJWT"""

    def __init__(self, token, permissions=None, scopes=None) -> None:
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = setu_up()
