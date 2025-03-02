# Troubleshooting Guide

This guide addresses common issues you might encounter when using StreamScalp Pro.

## Dependency Issues

### Package Conflicts

**Error**: `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.`

**Solution**: 
- Use the provided setup scripts (`setup.sh` or `setup.bat`) which install dependencies in the correct order
- Alternatively, install dependencies manually in this order:
  ```
  pip install -r requirements-base.txt
  pip install -r requirements-ccxt.txt
  pip install -r requirements-alpaca.txt --no-deps
  pip install -r requirements-dev.txt  # Optional
  ```

**Error**: `ModuleNotFoundError: No module named 'redis'` or similar missing module errors

**Solution**:
- Ensure you've activated your virtual environment
- Install the specific missing package: `pip install redis`
- If the package is already in requirements.txt but still missing, try reinstalling it directly

### Version Conflicts

**Error**: `alpaca-trade-api 3.0.2 requires aiohttp==3.8.2, but you have aiohttp 3.10.5 which is incompatible.`

**Solution**:
- These warnings are expected when using the split requirements approach
- The application should still work correctly despite these warnings
- If you experience runtime issues, create a fresh virtual environment and use the setup scripts

### Virtual Environment Issues

**Error**: `No module named 'venv'`

**Solution**:
- Install the venv module: `pip install virtualenv`
- On some systems, you may need to install it via your package manager:
  - Ubuntu/Debian: `sudo apt-get install python3-venv`
  - CentOS/RHEL: `sudo yum install python3-venv`

## Database Issues

### Migration Errors

**Error**: `No module named 'psycopg2'`

**Solution**: Install the PostgreSQL driver:
```
pip install psycopg2-binary
```

**Error**: `Expected string or URL object, got PostgresDsn`

**Solution**: Convert PostgresDsn to string in `migrations/env.py`:
```python
url=str(settings.postgres_url)
```

**Error**: Validation errors in Settings

**Solution**: Ensure your `.env` file has all required variables and that they match the field names in `config/settings.py`. Use Field aliases to map environment variables to class attributes.

### Connection Errors

**Error**: `Could not connect to database`

**Solution**: 
- For SQLite, ensure the path is writable
- For PostgreSQL, check that the database exists and credentials are correct
- Verify the database URL format in `config/settings.py`

## API Connection Issues

### Binance API

**Error**: `Invalid API key`

**Solution**: 
- Verify your API key and secret in the `.env` file
- Ensure the API key has the necessary permissions
- Check if the API key is restricted to specific IP addresses

### Alpaca API

**Error**: `Authentication failed`

**Solution**:
- Verify your API key and secret in the `.env` file
- Ensure you're using the correct endpoint (paper trading vs live trading)
- Check if your account has the necessary permissions

## Strategy Execution Issues

### Strategy Not Trading

**Issue**: Strategy is active but not executing trades

**Checklist**:
1. Verify the strategy's `active` flag is set to `True`
2. Check that the strategy's market and timeframe are valid
3. Ensure sufficient funds are available in your account
4. Check the logs for any error messages
5. Verify that the exchange API has trading permissions

## Performance Issues

### Slow Data Processing

**Issue**: Data processing is slow or unresponsive

**Solutions**:
1. Use smaller timeframes or fewer markets to reduce data volume
2. Optimize strategy calculations
3. Consider using a more powerful machine
4. Use caching for frequently accessed data

## Docker Issues

### Build Errors

**Error**: `failed to build: ERROR: could not find a version that satisfies the requirement`

**Solution**:
- Check that the build arguments in `docker-compose.yml` are correctly set
- Try rebuilding with `docker-compose build --no-cache`
- Verify that the requirements files are accessible during the build process

### Container Startup Issues

**Error**: `Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use`

**Solution**:
- A service on your host machine is already using the required port
- Change the port mapping in `docker-compose.yml` (e.g., from `"5432:5432"` to `"5433:5432"`)
- Stop the conflicting service on your host machine

### Volume Permissions

**Error**: `permission denied` when writing to mounted volumes

**Solution**:
- Ensure the container user has write permissions to the mounted directories
- For logs directory: `chmod -R 777 ./logs` (use with caution)
- Consider using named volumes instead of bind mounts for better permission handling

### Environment Variables

**Issue**: Environment variables not being passed to the container

**Solution**:
- Verify your `.env` file exists and is properly formatted
- Check that `env_file: .env` is included in your service definition in `docker-compose.yml`
- For sensitive variables, consider using Docker secrets in production

## Logging and Debugging

To enable detailed logging:

1. Set the log level in your configuration:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check the log files in the `logs` directory for error messages and stack traces.

## Getting Additional Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/yourusername/streamscalp-pro/issues) for similar problems
2. Create a new issue with detailed information about your problem
3. Include relevant logs and error messages
