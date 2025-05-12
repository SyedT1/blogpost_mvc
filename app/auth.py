from blacksheep import Application
from guardpost import AuthenticationHandler, Identity
from blacksheep.server.authorization import Policy
from guardpost.common import AuthenticatedRequirement
import jwt

from app.settings import Settings

SECRET_KEY = "your-secret-key"  # Use a strong, random key in production

class JWTAuthHandler(AuthenticationHandler):
    async def authenticate(self, context):
        token = None
        cookie = context.cookies.get("access_token")
        if cookie:
            token = cookie
        if not token:
            context.identity = None
            return None
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            context.identity = Identity({
                "name": payload.get("sub"),
                "role": payload.get("role", "user")
            }, "JWT")
            print(context.identity.claims.values())
        except Exception:
            context.identity = None
        return context.identity

def configure_authentication(app: Application, settings: Settings = None):
    """
    Configure authentication and authorization.
    """
    app.use_authentication().add(JWTAuthHandler())
    app.use_authorization().add(
        Policy("authenticated", AuthenticatedRequirement())
    )
