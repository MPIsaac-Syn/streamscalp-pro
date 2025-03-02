"""
Tests for the error handling utilities.
"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError, validator

from utils.error_handler import (
    AppException, 
    ErrorCode, 
    NotFoundException, 
    ValidationException,
    OrderException,
    setup_exception_handlers,
    safe_execute,
    safe_execute_async,
    with_error_handler,
    with_error_handler_async
)


class TestErrorHandler:
    """Tests for the error handler."""
    
    def test_app_exception(self):
        """Test AppException."""
        # Create an exception
        exc = AppException(
            message="Test error",
            error_code=ErrorCode.UNKNOWN_ERROR,
            status_code=500,
            details={"test": "value"}
        )
        
        # Check properties
        assert exc.message == "Test error"
        assert exc.error_code == ErrorCode.UNKNOWN_ERROR
        assert exc.status_code == 500
        assert exc.details == {"test": "value"}
        
    def test_not_found_exception(self):
        """Test NotFoundException."""
        # Create an exception
        exc = NotFoundException(
            message="Resource not found",
            details={"resource_id": 123}
        )
        
        # Check properties
        assert exc.message == "Resource not found"
        assert exc.error_code == ErrorCode.NOT_FOUND
        assert exc.status_code == 404
        assert exc.details == {"resource_id": 123}
        
    def test_validation_exception(self):
        """Test ValidationException."""
        # Create an exception
        exc = ValidationException(
            message="Validation error",
            details={"field": "value"}
        )
        
        # Check properties
        assert exc.message == "Validation error"
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 422
        assert exc.details == {"field": "value"}
        
    def test_order_exception(self):
        """Test OrderException."""
        # Create an exception
        exc = OrderException(
            message="Order error",
            details={"order_id": 123}
        )
        
        # Check properties
        assert exc.message == "Order error"
        assert exc.error_code == ErrorCode.ORDER_ERROR
        assert exc.status_code == 500
        assert exc.details == {"order_id": 123}


class TestSafeExecute:
    """Tests for safe_execute."""
    
    def test_safe_execute_success(self):
        """Test safe_execute with successful execution."""
        # Define a function that succeeds
        def success_func(a, b):
            return a + b
        
        # Execute safely
        result = safe_execute(success_func, 1, 2)
        
        # Check result
        assert result == 3
        
    def test_safe_execute_failure(self):
        """Test safe_execute with failure."""
        # Define a function that fails
        def failure_func():
            raise ValueError("Test error")
        
        # Execute safely
        result = safe_execute(failure_func)
        
        # Check result
        assert result is None
        
    @pytest.mark.asyncio
    async def test_safe_execute_async_success(self):
        """Test safe_execute_async with successful execution."""
        # Define an async function that succeeds
        async def success_func(a, b):
            return a + b
        
        # Execute safely
        result = await safe_execute_async(success_func, 1, 2)
        
        # Check result
        assert result == 3
        
    @pytest.mark.asyncio
    async def test_safe_execute_async_failure(self):
        """Test safe_execute_async with failure."""
        # Define an async function that fails
        async def failure_func():
            raise ValueError("Test error")
        
        # Execute safely
        result = await safe_execute_async(failure_func)
        
        # Check result
        assert result is None


class TestErrorHandlerDecorators:
    """Tests for error handler decorators."""
    
    def test_with_error_handler_success(self):
        """Test with_error_handler with successful execution."""
        # Define a function that succeeds
        @with_error_handler()
        def success_func(a, b):
            return a + b
        
        # Execute
        result = success_func(1, 2)
        
        # Check result
        assert result == 3
        
    def test_with_error_handler_failure(self):
        """Test with_error_handler with failure."""
        # Define a function that fails
        @with_error_handler(default_value="default")
        def failure_func():
            raise ValueError("Test error")
        
        # Execute
        result = failure_func()
        
        # Check result
        assert result == "default"
        
    def test_with_error_handler_custom_handler(self):
        """Test with_error_handler with custom handler."""
        # Define a custom error handler
        def custom_handler(exc):
            return f"Handled: {str(exc)}"
        
        # Define a function that fails
        @with_error_handler(error_handler=custom_handler)
        def failure_func():
            raise ValueError("Test error")
        
        # Execute
        result = failure_func()
        
        # Check result
        assert result == "Handled: Test error"
        
    @pytest.mark.asyncio
    async def test_with_error_handler_async_success(self):
        """Test with_error_handler_async with successful execution."""
        # Define an async function that succeeds
        @with_error_handler_async()
        async def success_func(a, b):
            return a + b
        
        # Execute
        result = await success_func(1, 2)
        
        # Check result
        assert result == 3
        
    @pytest.mark.asyncio
    async def test_with_error_handler_async_failure(self):
        """Test with_error_handler_async with failure."""
        # Define an async function that fails
        @with_error_handler_async(default_value="default")
        async def failure_func():
            raise ValueError("Test error")
        
        # Execute
        result = await failure_func()
        
        # Check result
        assert result == "default"


class TestFastAPIIntegration:
    """Tests for FastAPI integration."""
    
    def setup_method(self):
        """Set up test app."""
        # Create a test app
        self.app = FastAPI()
        
        # Set up exception handlers
        setup_exception_handlers(self.app)
        
        # Add test endpoints
        @self.app.get("/app-exception")
        def app_exception():
            raise AppException(
                message="Test error",
                error_code=ErrorCode.UNKNOWN_ERROR,
                status_code=500,
                details={"test": "value"}
            )
            
        @self.app.get("/not-found")
        def not_found():
            raise NotFoundException(
                message="Resource not found",
                details={"resource_id": 123}
            )
            
        @self.app.get("/validation-error")
        def validation_error():
            raise ValidationException(
                message="Validation error",
                details={"field": "value"}
            )
            
        @self.app.get("/http-exception")
        def http_exception():
            raise HTTPException(
                status_code=400,
                detail="Bad request"
            )
            
        @self.app.get("/generic-exception")
        def generic_exception():
            raise ValueError("Test error")
            
        # Create test client
        self.client = TestClient(self.app)
        
    def test_app_exception_response(self):
        """Test response for AppException."""
        # Make request
        response = self.client.get("/app-exception")
        
        # Check response
        assert response.status_code == 500
        assert response.json() == {
            "error": True,
            "code": "UNKNOWN_ERROR",
            "message": "Test error",
            "details": {"test": "value"}
        }
        
    def test_not_found_response(self):
        """Test response for NotFoundException."""
        # Make request
        response = self.client.get("/not-found")
        
        # Check response
        assert response.status_code == 404
        assert response.json() == {
            "error": True,
            "code": "NOT_FOUND",
            "message": "Resource not found",
            "details": {"resource_id": 123}
        }
        
    def test_validation_error_response(self):
        """Test response for ValidationException."""
        # Make request
        response = self.client.get("/validation-error")
        
        # Check response
        assert response.status_code == 422
        assert response.json() == {
            "error": True,
            "code": "VALIDATION_ERROR",
            "message": "Validation error",
            "details": {"field": "value"}
        }
        
    def test_http_exception_response(self):
        """Test response for HTTPException."""
        # Make request
        response = self.client.get("/http-exception")
        
        # Check response
        assert response.status_code == 400
        assert response.json() == {
            "error": True,
            "code": "UNKNOWN_ERROR",
            "message": "Bad request",
            "details": {}
        }
        
    def test_generic_exception_response(self):
        """Test response for generic Exception."""
        # Make request
        response = self.client.get("/generic-exception")
        
        # Check response
        assert response.status_code == 500
        assert response.json() == {
            "error": True,
            "code": "UNKNOWN_ERROR",
            "message": "An unexpected error occurred",
            "details": {"type": "ValueError"}
        }
