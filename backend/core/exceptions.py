import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from core.logging import logger
from core.responses import error_response


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        logger.warning(
            f"[{request.state.request_id}] "
            f"HTTPException {exc.status_code}: {exc.detail}"
        )

        return error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        logger.warning(
            f"[{request.state.request_id}] "
            f"Validation Error"
        )

        return error_response(
            code="VALIDATION_ERROR",
            message="Invalid request",
            status_code=422,
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.error(
            f"[{request.state.request_id}] "
            f"Unhandled Exception\n"
            f"{traceback.format_exc()}"
        )

        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="Something went wrong.",
            status_code=500,
        )