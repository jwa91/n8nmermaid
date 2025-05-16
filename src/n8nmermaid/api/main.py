# src/n8nmermaid/api/main.py
"""Main FastAPI application setup."""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from n8nmermaid.core.orchestrator_v2 import OrchestratorErrorV2
from n8nmermaid.utils.logging import setup_logging

from .routers import mermaid as mermaid_router_v2
from .routers import report as report_router_v2

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors for request bodies."""
    error_details = exc.errors()
    logger.warning("Request validation failed: %s", error_details)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": error_details},
    )


async def orchestrator_exception_handler(request: Request, exc: OrchestratorErrorV2):
    """Handles errors originating from the V2 core orchestration."""
    logger.error("OrchestratorErrorV2 caught: %s", exc, exc_info=False)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Analysis Error: {exc}"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any other unexpected exceptions."""
    logger.exception("Unhandled exception caught by generic handler:")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {exc}"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    setup_logging()
    logger.info("FastAPI application startup sequence initiated via lifespan.")
    yield
    logger.info("FastAPI application shutdown complete.")


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.
    """
    load_dotenv()

    app = FastAPI(
        title="n8n-mermaid API",
        description="API for analyzing n8n workflows and generating Mermaid diagrams"
        + " or reports.",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS configuration - allowing all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(OrchestratorErrorV2, orchestrator_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.include_router(
        mermaid_router_v2.router,
        prefix="/v2/mermaid",
        tags=["V2 - Mermaid Generation"],
    )
    app.include_router(
        report_router_v2.router,
        prefix="/v2/report",
        tags=["V2 - Report Generation"],
    )

    @app.get("/", tags=["Status"], summary="API Root/Health Check")
    async def read_root():
        """Provides a basic status message for the API root."""
        return {"message": "n8n-mermaid API V2 is running."}

    return app


app = create_app()
