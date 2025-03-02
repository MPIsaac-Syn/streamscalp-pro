"""
Error handling middleware and utilities for StreamScalp Pro.

This module provides centralized error handling for the application,
including exception middleware for FastAPI and utility functions
for standardized error responses.
"""
import logging
import traceback
from typing import Dict, Any, Optional, Type, Callable
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logger
logger = logging.getLogger(__name__)

class ErrorDetail:
    """
    Standard error response format.
    """
    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        details: Optional[Dict[str, Any]] = None,
        http_status: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.http_status = http_status
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "details": self.details
            }
        }

# Error code mapping
ERROR_CODES = {
    "validation_error": 422,
    "not_found": 404,
    "unauthorized": 401,
    "forbidden": 403,
    "bad_request": 400,
    "internal_error": 500,
    "service_unavailable": 503,
    "database_error": 500
}

# Exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors from FastAPI.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
        
    error_detail = ErrorDetail(
        message="Validation error",
        code="validation_error",
        details={"errors": errors},
        http_status=422
    )
    
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=error_detail.http_status,
        content=error_detail.to_dict()
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    """
    error_detail = ErrorDetail(
        message=str(exc.detail),
        code=f"http_{exc.status_code}",
        http_status=exc.status_code
    )
    
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=error_detail.http_status,
        content=error_detail.to_dict()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    """
    error_detail = ErrorDetail(
        message="Database error occurred",
        code="database_error",
        details={"error_type": exc.__class__.__name__},
        http_status=500
    )
    
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=error_detail.http_status,
        content=error_detail.to_dict()
    )

async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    """
    error_detail = ErrorDetail(
        message="Data validation error",
        code="validation_error",
        details={"errors": exc.errors()},
        http_status=422
    )
    
    logger.warning(f"Pydantic validation error: {exc.errors()}")
    return JSONResponse(
        status_code=error_detail.http_status,
        content=error_detail.to_dict()
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    error_detail = ErrorDetail(
        message="Internal server error",
        code="internal_error",
        http_status=500
    )
    
    # Log the full exception with traceback
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # In development, include more details
    if logger.level == logging.DEBUG:
        error_detail.details = {
            "error_type": exc.__class__.__name__,
            "traceback": traceback.format_exc()
        }
    
    return JSONResponse(
        status_code=error_detail.http_status,
        content=error_detail.to_dict()
    )

def setup_error_handlers(app: FastAPI) -> None:
    """
    Set up all error handlers for a FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    logger.info("Error handlers configured")
