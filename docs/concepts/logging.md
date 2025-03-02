# Logging in StreamScalp Pro

This document describes the logging system in StreamScalp Pro, including how to configure and use it effectively.

## Overview

StreamScalp Pro implements a comprehensive logging system that provides:

1. **Standardized logging format** - All logs follow a consistent format
2. **Multiple output destinations** - Logs can be sent to console and files
3. **Log rotation** - Log files are rotated to prevent them from growing too large
4. **Log levels** - Different levels of verbosity for different environments
5. **Contextual logging** - Additional context can be added to log messages

## Logging Configuration

The logging system is configured through the `setup_logger` function in the `utils/logger.py` module:

```python
from utils.logger import setup_logger

# Create a logger for your module
logger = setup_logger(
    name="my_module",
    log_level=logging.INFO,  # Optional, defaults to INFO
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Optional
    log_to_file=True,  # Optional, defaults to True
    log_to_console=True  # Optional, defaults to True
)
```

### Configuration Options

- **name**: The name of the logger, typically the module name
- **log_level**: The minimum log level to record (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **log_format**: The format of log messages
- **log_to_file**: Whether to log to a file
- **log_to_console**: Whether to log to the console

## Log Levels

The logging system supports the following log levels, in order of increasing severity:

1. **DEBUG** - Detailed information, typically useful only for diagnosing problems
2. **INFO** - Confirmation that things are working as expected
3. **WARNING** - An indication that something unexpected happened, or may happen in the near future
4. **ERROR** - Due to a more serious problem, the software has not been able to perform some function
5. **CRITICAL** - A serious error, indicating that the program itself may be unable to continue running

## Basic Logging

Once you have created a logger, you can use it to log messages at different levels:

```python
# Debug message
logger.debug("This is a debug message")

# Info message
logger.info("This is an info message")

# Warning message
logger.warning("This is a warning message")

# Error message
logger.error("This is an error message")

# Critical message
logger.critical("This is a critical message")
```

## Contextual Logging

You can add additional context to log messages using the `extra` parameter:

```python
# Log with additional context
logger.info(
    "User logged in",
    extra={
        "user_id": user.id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)
```

## Logging Exceptions

When logging exceptions, include the exception information:

```python
try:
    # Operation that might fail
    result = perform_operation()
except Exception as e:
    # Log the exception with traceback
    logger.error(
        f"Operation failed: {str(e)}",
        exc_info=True,  # Include traceback
        extra={
            "operation": "perform_operation",
            "args": {"arg1": value1, "arg2": value2}
        }
    )
```

## Log File Location

Log files are stored in the `logs` directory in the project root. Each logger creates its own log file, named after the logger:

```
logs/
├── app.log
├── api.log
├── order_manager.log
├── risk_manager.log
└── ...
```

## Log Rotation

Log files are automatically rotated when they reach a certain size (10 MB by default). The system keeps a maximum of 5 backup files for each log file.

## Integration with Error Handling

The logging system is integrated with the error handling system. All exceptions are automatically logged with relevant context:

```python
from utils.error_handler import OrderException, ErrorCode

try:
    # Attempt to place order
    order = await exchange.place_order(order_data)
    return order
except Exception as e:
    # This will be automatically logged by the error handling system
    raise OrderException(
        message="Failed to place order",
        error_code=ErrorCode.ORDER_ERROR,
        details={"order_data": order_data}
    )
```

## Best Practices

### Logger Naming

Name loggers after the module they are in:

```python
# In file: order_manager/order_manager.py
logger = setup_logger("order_manager")

# In file: risk_manager/risk_manager.py
logger = setup_logger("risk_manager")
```

### Log Levels

Use the appropriate log level for each message:

- **DEBUG**: Detailed information for debugging
- **INFO**: Normal operation information
- **WARNING**: Potential issues that don't prevent normal operation
- **ERROR**: Errors that prevent a specific operation from completing
- **CRITICAL**: Errors that prevent the application from functioning

### Structured Logging

Use structured logging for machine-readable logs:

```python
logger.info(
    "Order placed",
    extra={
        "order_id": order.id,
        "symbol": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price
    }
)
```

### Sensitive Information

Never log sensitive information such as API keys, passwords, or personal data:

```python
# WRONG
logger.info(f"User logged in with password: {password}")

# RIGHT
logger.info("User logged in", extra={"user_id": user.id})
```

### Performance Considerations

Avoid expensive operations in log messages:

```python
# WRONG - The expensive_operation is always called, even if DEBUG is not enabled
logger.debug(f"Debug info: {expensive_operation()}")

# RIGHT - The expensive_operation is only called if DEBUG is enabled
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Debug info: {expensive_operation()}")
```

## Monitoring and Analysis

Log files can be analyzed using standard tools like `grep`, `awk`, and `sed`. For more advanced analysis, consider using a log aggregation system like ELK (Elasticsearch, Logstash, Kibana) or Graylog.

## Environment-Specific Logging

The logging system can be configured differently for different environments:

- **Development**: More verbose logging (DEBUG level) to console and file
- **Staging**: Less verbose logging (INFO level) to console and file
- **Production**: Minimal logging (WARNING level) to file only

This is configured through the application settings in `utils/config.py`.
