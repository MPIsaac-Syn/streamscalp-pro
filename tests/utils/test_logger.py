"""
Tests for the logging utilities.
"""
import os
import logging
import pytest
from unittest.mock import patch, MagicMock

from utils.logger import setup_logger, DEFAULT_FORMAT, DEFAULT_LOG_LEVEL, DEFAULT_LOG_DIR


class TestLogger:
    """Tests for the logger."""
    
    def setup_method(self):
        """Set up test."""
        # Clean up any existing loggers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        # Reset existing loggers
        for name in logging.root.manager.loggerDict.keys():
            logger = logging.getLogger(name)
            logger.handlers = []
            logger.propagate = True
            logger.setLevel(logging.NOTSET)
    
    def test_setup_logger_default(self):
        """Test setup_logger with default settings."""
        # Create logger
        logger = setup_logger("test_default")
        
        # Check logger
        assert logger.name == "test_default"
        assert logger.level == DEFAULT_LOG_LEVEL
        assert len(logger.handlers) == 2  # Console and file handler
        
        # Check handlers
        console_handler = None
        file_handler = None
        
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not hasattr(handler, 'baseFilename'):
                console_handler = handler
            else:
                file_handler = handler
                
        assert console_handler is not None
        assert file_handler is not None
        
        # Check console handler
        assert console_handler.formatter._fmt == DEFAULT_FORMAT
        
        # Check file handler
        assert os.path.exists(DEFAULT_LOG_DIR)
        assert file_handler.baseFilename.endswith("test_default.log")
        assert file_handler.formatter._fmt == DEFAULT_FORMAT
    
    def test_setup_logger_custom_level(self):
        """Test setup_logger with custom log level."""
        # Create logger
        logger = setup_logger("test_custom_level", log_level=logging.DEBUG)
        
        # Check logger
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_custom_format(self):
        """Test setup_logger with custom format."""
        # Custom format
        custom_format = "%(levelname)s - %(message)s"
        
        # Create logger
        logger = setup_logger("test_custom_format", log_format=custom_format)
        
        # Check handlers
        for handler in logger.handlers:
            assert handler.formatter._fmt == custom_format
    
    def test_setup_logger_no_file(self):
        """Test setup_logger with no file logging."""
        # Create logger
        logger = setup_logger("test_no_file", log_to_file=False)
        
        # Check logger
        assert len(logger.handlers) == 1  # Only console handler
        
        # Check handler is console handler
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert not hasattr(handler, 'baseFilename')
    
    def test_setup_logger_no_console(self):
        """Test setup_logger with no console logging."""
        # Create logger
        logger = setup_logger("test_no_console", log_to_console=False)
        
        # Check logger
        assert len(logger.handlers) == 1  # Only file handler
        
        # Check handler is file handler
        handler = logger.handlers[0]
        assert hasattr(handler, 'baseFilename')
    
    def test_setup_logger_existing(self):
        """Test setup_logger with existing logger."""
        # Create logger twice
        logger1 = setup_logger("test_existing")
        logger2 = setup_logger("test_existing")
        
        # Check loggers are the same
        assert logger1 is logger2
        
        # Check handlers are not duplicated
        assert len(logger1.handlers) == 2
    
    @patch('os.makedirs')
    def test_setup_logger_create_dir(self, mock_makedirs):
        """Test setup_logger creates log directory."""
        # Mock os.path.exists to return False
        with patch('os.path.exists', return_value=False):
            # Create logger
            logger = setup_logger("test_create_dir")
            
            # Check directory was created
            mock_makedirs.assert_called_once_with(DEFAULT_LOG_DIR)
    
    def test_logger_output(self):
        """Test logger output."""
        # Create logger
        logger = setup_logger("test_output", log_to_file=False)
        
        # Mock handler
        mock_handler = MagicMock()
        logger.addHandler(mock_handler)
        
        # Log messages
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Check handler was called
        assert mock_handler.handle.call_count == 4  # Debug is below default level
        
        # Check log records
        records = [call.args[0] for call in mock_handler.handle.call_args_list]
        
        assert records[0].levelname == "INFO"
        assert records[0].getMessage() == "Info message"
        
        assert records[1].levelname == "WARNING"
        assert records[1].getMessage() == "Warning message"
        
        assert records[2].levelname == "ERROR"
        assert records[2].getMessage() == "Error message"
        
        assert records[3].levelname == "CRITICAL"
        assert records[3].getMessage() == "Critical message"
