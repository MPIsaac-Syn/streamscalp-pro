"""
Error handling utilities for StreamScalp Pro.

This module provides standardized error handling across the application.
"""
import logging
import traceback
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from utils.logger import setup_logger

# Setup logger
logger = setup_logger("error_handler")

# Type definitions
T = TypeVar('T')
ErrorHandler = Callable[[Exception], Any]


class ErrorCode(str, Enum):
    """Error codes for StreamScalp Pro."""
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # Business logic errors
    STRATEGY_ERROR = "STRATEGY_ERROR"
    ORDER_ERROR = "ORDER_ERROR"
    TRADE_ERROR = "TRADE_ERROR"
    RISK_ERROR = "RISK_ERROR"
    
    # External service errors
    EXCHANGE_ERROR = "EXCHANGE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"


class AppException(Exception):
    """Base exception class for StreamScalp Pro."""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        error_code: ErrorCode = ErrorCode.NOT_FOUND,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationException(AppException):
    """Exception raised when validation fails."""
    
    def __init__(
        self, 
        message: str = "Validation error", 
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication fails."""
    
    def __init__(
        self, 
        message: str = "Unauthorized", 
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class ForbiddenException(AppException):
    """Exception raised when authorization fails."""
    
    def __init__(
        self, 
        message: str = "Forbidden", 
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class StrategyException(AppException):
    """Exception raised when a strategy operation fails."""
    
    def __init__(
        self, 
        message: str = "Strategy error", 
        error_code: ErrorCode = ErrorCode.STRATEGY_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class OrderException(AppException):
    """Exception raised when an order operation fails."""
    
    def __init__(
        self, 
        message: str = "Order error", 
        error_code: ErrorCode = ErrorCode.ORDER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class TradeException(AppException):
    """Exception raised when a trade operation fails."""
    
    def __init__(
        self, 
        message: str = "Trade error", 
        error_code: ErrorCode = ErrorCode.TRADE_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class RiskException(AppException):
    """Exception raised when a risk operation fails."""
    
    def __init__(
        self, 
        message: str = "Risk error", 
        error_code: ErrorCode = ErrorCode.RISK_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class ExchangeException(AppException):
    """Exception raised when an exchange operation fails."""
    
    def __init__(
        self, 
        message: str = "Exchange error", 
        error_code: ErrorCode = ErrorCode.EXCHANGE_ERROR,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class DatabaseException(AppException):
    """Exception raised when a database operation fails."""
    
    def __init__(
        self, 
        message: str = "Database error", 
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class NetworkException(AppException):
    """Exception raised when a network operation fails."""
    
    def __init__(
        self, 
        message: str = "Network error", 
        error_code: ErrorCode = ErrorCode.NETWORK_ERROR,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


def handle_app_exception(exc: AppException) -> JSONResponse:
    """Handle AppException and return a JSONResponse."""
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={"details": exc.details, "traceback": traceback.format_exc()}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


def handle_validation_exception(exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI RequestValidationError and return a JSONResponse."""
    logger.error(
        f"ValidationError: {str(exc)}",
        extra={"traceback": traceback.format_exc()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "code": ErrorCode.VALIDATION_ERROR,
            "message": "Validation error",
            "details": {"errors": exc.errors()}
        }
    )


def handle_http_exception(exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException and return a JSONResponse."""
    logger.error(
        f"HTTPException: {exc.status_code} - {exc.detail}",
        extra={"traceback": traceback.format_exc()}
    )
    
    error_code = ErrorCode.UNKNOWN_ERROR
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        error_code = ErrorCode.NOT_FOUND
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        error_code = ErrorCode.UNAUTHORIZED
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        error_code = ErrorCode.FORBIDDEN
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": error_code,
            "message": str(exc.detail),
            "details": {}
        }
    )


def handle_pydantic_validation_error(exc: ValidationError) -> JSONResponse:
    """Handle Pydantic ValidationError and return a JSONResponse."""
    logger.error(
        f"PydanticValidationError: {str(exc)}",
        extra={"traceback": traceback.format_exc()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "code": ErrorCode.VALIDATION_ERROR,
            "message": "Validation error",
            "details": {"errors": exc.errors()}
        }
    )


def handle_generic_exception(exc: Exception) -> JSONResponse:
    """Handle generic Exception and return a JSONResponse."""
    logger.error(
        f"UnhandledException: {type(exc).__name__} - {str(exc)}",
        extra={"traceback": traceback.format_exc()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "code": ErrorCode.UNKNOWN_ERROR,
            "message": "An unexpected error occurred",
            "details": {"type": type(exc).__name__}
        }
    )


def setup_exception_handlers(app):
    """Set up exception handlers for FastAPI application."""
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(ValidationError, handle_pydantic_validation_error)
    app.add_exception_handler(Exception, handle_generic_exception)


def safe_execute(func: Callable[..., T], *args, **kwargs) -> Union[T, None]:
    """
    Execute a function safely and return None if an exception occurs.
    
    Args:
        func: Function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Function result or None if an exception occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(
            f"Error executing {func.__name__}: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )
        return None


async def safe_execute_async(func: Callable[..., T], *args, **kwargs) -> Union[T, None]:
    """
    Execute an async function safely and return None if an exception occurs.
    
    Args:
        func: Async function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Function result or None if an exception occurs
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(
            f"Error executing async {func.__name__}: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )
        return None


def with_error_handler(
    error_handler: Optional[ErrorHandler] = None,
    default_value: Any = None
) -> Callable[[Callable[..., T]], Callable[..., Union[T, Any]]]:
    """
    Decorator to handle exceptions in a function.
    
    Args:
        error_handler: Function to handle exceptions
        default_value: Value to return if an exception occurs
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    extra={"traceback": traceback.format_exc()}
                )
                
                if error_handler:
                    return error_handler(e)
                return default_value
        return wrapper
    return decorator


def with_error_handler_async(
    error_handler: Optional[ErrorHandler] = None,
    default_value: Any = None
) -> Callable[[Callable[..., T]], Callable[..., Union[T, Any]]]:
    """
    Decorator to handle exceptions in an async function.
    
    Args:
        error_handler: Function to handle exceptions
        default_value: Value to return if an exception occurs
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        async def wrapper(*args, **kwargs) -> Union[T, Any]:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in async {func.__name__}: {str(e)}",
                    extra={"traceback": traceback.format_exc()}
                )
                
                if error_handler:
                    return error_handler(e)
                return default_value
        return wrapper
    return decorator
