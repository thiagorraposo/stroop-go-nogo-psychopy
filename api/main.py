"""Factory HTTP; regras do experimento permanecem no pacote stroop."""

import asyncio

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from api.config import APIConfig
from api.errors import APIError, error_response, http_exception_handler, validation_exception_handler
from api.health import database_ready
from api.transport import RequestBoundary
from api.auth import callback as auth_callback, router as auth_router
from api.local_auth import router as local_auth_router
from api.sessions import router as sessions_router
from api.results import router as results_router
from api.assessments import router as assessments_router, export_router as assessment_export_router
from api.administration import router as administration_router
from api.imports import router as imports_router


def create_app(config: APIConfig | None = None) -> FastAPI:
    config = APIConfig.from_env() if config is None else config
    app = FastAPI(
        title="Stroop WEB", docs_url=None, redoc_url=None, openapi_url=None,
        debug=False, redirect_slashes=False,
    )
    app.state.config = config
    app.state.csv_import_semaphore = asyncio.Semaphore(2)
    app.include_router(auth_router)
    app.include_router(local_auth_router)
    if config.oidc_callback_path == "/oauth2callback":
        app.add_api_route("/oauth2callback", auth_callback, methods=["GET"], include_in_schema=False)
    app.include_router(sessions_router)
    app.include_router(results_router)
    app.include_router(assessments_router)
    app.include_router(assessment_export_router)
    app.include_router(administration_router)
    app.include_router(imports_router)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_middleware(RequestBoundary, config=config)

    @app.get("/health/live")
    def live(request: Request):
        if request.query_params:
            raise APIError("invalid_request")
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready(request: Request):
        if request.query_params:
            raise APIError("invalid_request")
        if not database_ready(config.database_url):
            return error_response("service_unavailable", request.state.request_id)
        return {"status": "ready"}

    return app
