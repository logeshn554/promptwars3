import time
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentParseError,
    FileTooLargeError,
    NyayaLensError,
    PromptInjectionDetectedError,
    UnsupportedFileTypeError,
)
from app.core.logging import logger


def create_app() -> FastAPI:
    settings.setup_directories()

    app = FastAPI(
        title="NyayaLens API",
        description="Evidence-Grounded Legal Document Intelligence Platform API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Secure CORS configuration supporting localhost and any *.vercel.app domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from typing import Awaitable, Callable

    from fastapi import Response

    # Correlation ID and Security Headers Middleware
    @app.middleware("http")
    async def security_and_logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = str(uuid4())
        start_time = time.time()

        # Log incoming request safely without exposing headers or query strings
        logger.info(
            f"Incoming {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id},
        )

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        logger.info(
            f"Completed {request.method} {request.url.path} with status {response.status_code} in {duration_ms}ms",
            extra={"correlation_id": correlation_id, "duration_ms": duration_ms},
        )
        return response

    # Domain Exception Handlers
    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "DocumentNotFoundError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_file_type_handler(request: Request, exc: UnsupportedFileTypeError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "UnsupportedFileTypeError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(request: Request, exc: FileTooLargeError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"error": "FileTooLargeError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(DocumentParseError)
    async def document_parse_error_handler(request: Request, exc: DocumentParseError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "DocumentParseError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(PromptInjectionDetectedError)
    async def prompt_injection_handler(request: Request, exc: PromptInjectionDetectedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "PromptInjectionDetectedError", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(NyayaLensError)
    async def generic_nyayalens_error_handler(request: Request, exc: NyayaLensError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "NyayaLensInternalError", "message": exc.message, "details": exc.details},
        )

    # Global Exception Handler preventing internal stack trace leaks
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled server error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing your legal request.",
            },
        )

    # Register Routers
    app.include_router(api_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
