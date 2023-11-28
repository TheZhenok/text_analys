import logging

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.sessions import SessionMiddleware

from app.settings import settings
from app.web.endpoints.router import api_router
from app.web.lifetime import register_shutdown_event, register_startup_event


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="KSTU Tabashnyk Evgeniy TEXT ANALYSIS",
        description="",
        version="0.1.0",  # metadata.version("uchet_profile"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    if settings.sentry_dsn:
        # Enables sentry integration.
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_sample_rate,
            environment=settings.environment,
            integrations=[
                LoggingIntegration(
                    level=logging.getLevelName(settings.log_level.value),
                    event_level=logging.ERROR,
                ),
                SqlalchemyIntegration(),
            ],
        )
        app = SentryAsgiMiddleware(app)  # type: ignore

    return app


app = get_app()

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run("app.web.application:app", host="0.0.0.0", port=7111, reload=True, log_level="debug")