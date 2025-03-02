# Error Handling in StreamScalp Pro

This document describes the error handling system in StreamScalp Pro, including the types of errors, how they are handled, and best practices for error handling in the application.

## Overview

StreamScalp Pro implements a comprehensive error handling system that provides:

1. **Standardized error responses** - All errors follow a consistent format
2. **Typed exceptions** - Domain-specific exceptions for different parts of the application
3. **Centralized error handling** - All errors are handled in a consistent way
4. **Detailed logging** - All errors are logged with relevant context
5. **Error recovery** - Utilities for safe execution and error recovery

## Error Response Format

All API error responses follow this JSON format:

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    // Additional error details specific to the error type
  }
}
```

## Error Codes

StreamScalp Pro defines the following error codes:

### General Errors

- `UNKNOWN_ERROR` - An unexpected error occurred
- `VALIDATION_ERROR` - Input validation failed
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication failed
- `FORBIDDEN` - Authorization failed

### Business Logic Errors

- `STRATEGY_ERROR` - Error in strategy execution or configuration
- `ORDER_ERROR` - Error in order processing
- `TRADE_ERROR` - Error in trade processing
- `RISK_ERROR` - Error in risk management

### External Service Errors

- `EXCHANGE_ERROR` - Error communicating with exchange
- `DATABASE_ERROR` - Error in database operations
- `NETWORK_ERROR` - Network-related error

## Exception Hierarchy

The application defines a hierarchy of exceptions:

- `AppException` - Base exception class
  - `NotFoundException` - Resource not found
  - `ValidationException` - Validation error
  - `UnauthorizedException` - Authentication error
  - `ForbiddenException` - Authorization error
  - `StrategyException` - Strategy-related error
  - `OrderException` - Order-related error
  - `TradeException` - Trade-related error
  - `RiskException` - Risk management error
  - `ExchangeException` - Exchange-related error
  - `DatabaseException` - Database-related error
  - `NetworkException` - Network-related error

## Error Handling Utilities

### Safe Execution

The `safe_execute` and `safe_execute_async` functions provide a way to execute functions safely and handle exceptions:

```python
from utils.error_handler import safe_execute, safe_execute_async

# Synchronous function
result = safe_execute(my_function, arg1, arg2, kwarg1=value1)

# Asynchronous function
result = await safe_execute_async(my_async_function, arg1, arg2, kwarg1=value1)
```

### Error Handler Decorators

The `with_error_handler` and `with_error_handler_async` decorators provide a way to handle exceptions in functions:

```python
from utils.error_handler import with_error_handler, with_error_handler_async

# Custom error handler
def my_error_handler(exc):
    # Handle exception
    return fallback_value

# Synchronous function
@with_error_handler(error_handler=my_error_handler, default_value=None)
def my_function(arg1, arg2):
    # Function implementation

# Asynchronous function
@with_error_handler_async(error_handler=my_error_handler, default_value=None)
async def my_async_function(arg1, arg2):
    # Function implementation
```

## Best Practices

### Raising Exceptions

When raising exceptions, use the appropriate exception type and provide a clear error message:

```python
from utils.error_handler import OrderException, ErrorCode

# Raise an exception with a clear message
raise OrderException(
    message="Failed to place order due to insufficient funds",
    error_code=ErrorCode.ORDER_ERROR,
    details={"required": 100.0, "available": 50.0}
)
```

### Handling Exceptions

When handling exceptions, catch specific exception types and handle them appropriately:

```python
from utils.error_handler import ExchangeException, OrderException

try:
    # Attempt to place order
    order = await exchange.place_order(order_data)
    return order
except ExchangeException as e:
    # Handle exchange-specific errors
    logger.error(f"Exchange error: {e.message}", extra={"details": e.details})
    # Retry or fallback
except OrderException as e:
    # Handle order-specific errors
    logger.error(f"Order error: {e.message}", extra={"details": e.details})
    # Handle order error
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {str(e)}")
    # Fallback
```

### Logging Errors

When logging errors, include relevant context:

```python
from utils.logger import setup_logger

logger = setup_logger("my_module")

try:
    # Operation that might fail
    result = perform_operation()
except Exception as e:
    logger.error(
        f"Operation failed: {str(e)}",
        extra={
            "operation": "perform_operation",
            "args": {"arg1": value1, "arg2": value2},
            "user_id": user_id
        }
    )
```

## Integration with FastAPI

The error handling system is integrated with FastAPI through exception handlers:

```python
from fastapi import FastAPI
from utils.error_handler import setup_exception_handlers

app = FastAPI()

# Set up exception handlers
setup_exception_handlers(app)
```

This sets up handlers for:

- `AppException` and its subclasses
- `RequestValidationError` from FastAPI
- `HTTPException` from FastAPI
- `ValidationError` from Pydantic
- Generic `Exception`

## Error Recovery Strategies

The application implements several error recovery strategies:

1. **Retry with backoff** - For transient errors like network issues
2. **Circuit breaker** - To prevent cascading failures
3. **Fallback values** - To provide default values when operations fail
4. **Graceful degradation** - To continue operation with reduced functionality

These strategies are implemented in the respective modules where they are needed.

## Monitoring and Alerting

Errors are monitored through:

1. **Logging** - All errors are logged with relevant context
2. **Metrics** - Error counts and rates are tracked as metrics
3. **Health checks** - The health check system reports on error states

Alerts are configured for:

1. **Critical errors** - Errors that require immediate attention
2. **Error rate thresholds** - When error rates exceed normal levels
3. **System health** - When the system health degrades
