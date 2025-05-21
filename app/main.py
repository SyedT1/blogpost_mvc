"""
This module configures the BlackSheep application before it starts.
"""
from blacksheep import Application, WebSocket, WebSocketDisconnectError
from blacksheep.server.diagnostics import get_diagnostic_app
from blacksheep.server.redirects import get_trailing_slash_middleware
from blacksheep.server.authorization import Policy
from guardpost.common import AuthenticatedRequirement
from rodi import Container

from app.auth import configure_authentication
from app.docs import configure_docs
from app.errors import configure_error_handlers
from app.services import configure_services
from app.settings import Settings
from app.templating import configure_templating
from app.connection import ConnectionManager


def exclude_trailing_slash(path: str) -> bool:
    return "/api/" in path or path.startswith("/ws/")


def configure_application(
    services: Container,
    settings: Settings,
) -> Application:
    app = Application(services=services)
    app.middlewares.append(get_trailing_slash_middleware(exclude=exclude_trailing_slash))
    auth_policy = "authenticated"
    app.use_authorization().add(Policy(auth_policy, AuthenticatedRequirement()))
    app.serve_files("app/static")
    configure_error_handlers(app)
    configure_authentication(app, settings)
    configure_docs(app, settings)
    configure_templating(app, settings)
    return app


def get_app():
    try:
        return configure_application(*configure_services())
    except Exception as exc:
        return get_diagnostic_app(exc)


app = get_app()