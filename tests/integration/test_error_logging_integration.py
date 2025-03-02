"""
Integration tests for error handling and logging.
"""
import os
import pytest
import logging
import tempfile
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from contextlib import contextmanager

from utils.logger import setup_logger
from utils.error_handler import (
    AppException,
    ErrorCode,
    setup_exception_handlers,
    safe_execute,
    safe_execute_async,
    with_error_handler,
    with_error_handler_async
)
from utils.config import get_settings
from utils.event_bus import publish_error, ErrorEventType


@contextmanager
def temp_log_file():
    """Create a temporary log file for testing."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set log directory to temp directory
        original_log_dir = os.environ.get("LOG_DIR")
        os.environ["LOG_DIR"] = temp_dir
        
        # Create a logger
        logger = setup_logger("test_integration", log_level=logging.DEBUG)
        
        try:
            # Yield the logger and temp directory
            yield logger, temp_dir
        finally:
            # Reset log directory
            if original_log_dir:
                os.environ["LOG_DIR"] = original_log_dir
            else:
                os.environ.pop("LOG_DIR", None)


class TestErrorLoggingIntegration:
    """Integration tests for error handling and logging."""
    
    def setup_method(self):
        """Set up test."""
        # Create a test app
        self.app = FastAPI()
        
        # Set up exception handlers
        setup_exception_handlers(self.app)
        
        # Add test endpoints
        @self.app.get("/success")
        def success():
            return {"status": "success"}
        
        @self.app.get("/error")
        def error():
            raise AppException(
                message="Test error",
                error_code=ErrorCode.UNKNOWN_ERROR,
                status_code=500,
                details={"test": "value"}
            )
        
        @self.app.get("/safe-execute")
        def safe_execute_endpoint():
            # Define a function that fails
            def failure_func():
                raise ValueError("Test error")
            
            # Execute safely
            result = safe_execute(failure_func)
            
            # Return result
            return {"result": result}
        
        @self.app.get("/with-error-handler")
        @with_error_handler(default_value={"status": "fallback"})
        def with_error_handler_endpoint():
            # Raise an exception
            raise ValueError("Test error")
        
        @self.app.get("/async-error")
        async def async_error():
            # Publish error to event bus
            await publish_error(
                error_type=ErrorEventType.GENERAL_ERROR,
                message="Test error",
                details={"test": "value"},
                source="test_integration"
            )
            
            # Return success
            return {"status": "error_published"}
        
        # Create test client
        self.client = TestClient(self.app)
    
    def test_success_endpoint(self):
        """Test success endpoint."""
        # Make request
        response = self.client.get("/success")
        
        # Check response
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
    
    def test_error_endpoint(self):
        """Test error endpoint."""
        # Create a temporary log file
        with temp_log_file() as (logger, temp_dir):
            # Make request
            response = self.client.get("/error")
            
            # Check response
            assert response.status_code == 500
            assert response.json() == {
                "error": True,
                "code": "UNKNOWN_ERROR",
                "message": "Test error",
                "details": {"test": "value"}
            }
            
            # Check log file
            log_file = os.path.join(temp_dir, "test_integration.log")
            assert os.path.exists(log_file)
            
            # Check log content
            with open(log_file, "r") as f:
                log_content = f.read()
                assert "AppException: UNKNOWN_ERROR - Test error" in log_content
    
    def test_safe_execute_endpoint(self):
        """Test safe_execute endpoint."""
        # Create a temporary log file
        with temp_log_file() as (logger, temp_dir):
            # Make request
            response = self.client.get("/safe-execute")
            
            # Check response
            assert response.status_code == 200
            assert response.json() == {"result": None}
            
            # Check log file
            log_file = os.path.join(temp_dir, "test_integration.log")
            assert os.path.exists(log_file)
            
            # Check log content
            with open(log_file, "r") as f:
                log_content = f.read()
                assert "Error executing failure_func: Test error" in log_content
    
    def test_with_error_handler_endpoint(self):
        """Test with_error_handler endpoint."""
        # Create a temporary log file
        with temp_log_file() as (logger, temp_dir):
            # Make request
            response = self.client.get("/with-error-handler")
            
            # Check response
            assert response.status_code == 200
            assert response.json() == {"status": "fallback"}
            
            # Check log file
            log_file = os.path.join(temp_dir, "test_integration.log")
            assert os.path.exists(log_file)
            
            # Check log content
            with open(log_file, "r") as f:
                log_content = f.read()
                assert "Error in with_error_handler_endpoint: Test error" in log_content
    
    @pytest.mark.asyncio
    async def test_async_error_endpoint(self):
        """Test async_error endpoint."""
        # Create a temporary log file
        with temp_log_file() as (logger, temp_dir):
            # Make request
            response = self.client.get("/async-error")
            
            # Check response
            assert response.status_code == 200
            assert response.json() == {"status": "error_published"}
            
            # In a real test, we would check that the error was published to the event bus
            # This would require a mock Redis instance or similar
