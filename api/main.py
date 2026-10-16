"""Factory HTTP; regras do experimento permanecem no pacote stroop."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from api.config import APIConfig
from api.errors import APIError, error_response, http_exception_handler, validation_exception_handler
from api.health import database_ready
from api.transport import RequestBoundary
from api.auth import router as auth_router
from api.sessions import router as sessions_router
from api.results import router as results_router
from api.assessments import router as assessments_router


def create_app(config: APIConfig | None = None) -> FastAPI:
    config = APIConfig.from_env() if config is None else config
    app = FastAPI(
        title="Stroop WEB", docs_url=None, redoc_url=None, openapi_url=None,
        debug=False, redirect_slashes=False,
    )
    app.state.config = config
    app.include_router(auth_router)
    app.include_router(sessions_router)
    app.include_router(results_router)
    app.include_router(assessments_router)
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
