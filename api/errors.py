"""Catalogo fechado de erros HTTP, sem detalhes de entradas ou excecoes."""

from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse


ERRORS = {
    "invalid_json": (400, "JSON invalido."),
    "invalid_oidc_state": (400, "Transacao de autenticacao invalida."),
    "authentication_required": (401, "Autenticacao necessaria."),
    "permission_denied": (403, "Operacao nao permitida."),
    "account_blocked": (403, "Conta bloqueada."),
    "csrf_failed": (403, "Verificacao de origem ou CSRF recusada."),
    "not_found": (404, "Recurso nao encontrado."),
    "method_not_allowed": (405, "Metodo nao permitido."),
    "state_conflict": (409, "Operacao incompativel com o estado atual."),
    "invitation_used": (409, "Convite ja utilizado."),
    "result_conflict": (409, "Resultado diferente do ja recebido."),
    "duplicate_project": (409, "Projeto ja cadastrado."),
    "invitation_expired": (410, "Convite expirado."),
    "session_expired": (410, "Sessao expirada."),
    "body_too_large": (413, "Corpo da requisicao excede o limite."),
    "unsupported_media_type": (415, "Tipo ou codificacao de conteudo nao suportado."),
    "invalid_request": (422, "Campos da requisicao invalidos."),
    "invalid_result": (422, "Resultado inconsistente com o protocolo."),
    "rate_limited": (429, "Limite de requisicoes atingido."),
    "internal_error": (500, "Falha interna ao processar a requisicao."),
    "service_unavailable": (503, "Servico temporariamente indisponivel."),
}

STATUS_CODES = {
    400: "invalid_json", 401: "authentication_required", 403: "permission_denied",
    404: "not_found", 405: "method_not_allowed", 409: "state_conflict",
    410: "session_expired", 413: "body_too_large", 415: "unsupported_media_type",
    422: "invalid_request", 429: "rate_limited", 500: "internal_error",
    503: "service_unavailable",
}


class APIError(HTTPException):
    """Erro de negocio com codigo pertencente ao catalogo estatico."""

    def __init__(self, code: str, headers: dict[str, str] | None = None) -> None:
        status, message = ERRORS[code]
        self.code = code
        super().__init__(status_code=status, detail=message, headers=headers)


def error_response(code: str, request_id: str) -> JSONResponse:
    status, message = ERRORS[code]
    headers = {"X-Request-ID": request_id, "Cache-Control": "no-store"}
    if code == "rate_limited":
        headers["Retry-After"] = "900"
    return JSONResponse(
        {"error": {"code": code, "message": message}, "request_id": request_id},
        status_code=status,
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = exc.code if isinstance(exc, APIError) else STATUS_CODES.get(exc.status_code, "internal_error")
    response = error_response(code, request.state.request_id)
    if exc.headers:
        for name, value in exc.headers.items():
            if name.lower() == "retry-after" and value.isdigit():
                response.headers["Retry-After"] = value
    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response("invalid_request", request.state.request_id)
