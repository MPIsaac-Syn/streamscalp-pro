# StreamScalp Pro

A professional trading platform for cryptocurrency and stock trading with automated strategies, built with FastAPI and modern Python practices.

## Features

- **Multi-Exchange Support**: Trade on Binance (crypto) and Alpaca (stocks) through unified exchange adapters
- **Advanced Order Management**: Comprehensive order state tracking and risk management
- **Strategy Framework**: Extensible framework for implementing custom trading strategies
- **Monitoring & Observability**: Health checks, Prometheus metrics, and structured logging
- **Dashboard**: Web interface for monitoring trades and managing strategies
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic migrations

## Project Structure

```
streamscalp-pro/
├── adapters/          # Exchange-specific implementations
├── api/              # FastAPI routes and endpoints
├── config/           # Application configuration
├── dashboard/        # Web interface components
├── docs/            # Project documentation
├── migrations/      # Alembic database migrations
├── models/          # SQLAlchemy database models
├── order_manager/   # Order execution and management
├── risk_manager/    # Trading risk controls
├── schemas/         # Pydantic data models
├── strategies/      # Trading strategy implementations
├── tests/          # Test suite
└── utils/          # Shared utilities
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for caching)
- Docker (optional)

### Environment Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with required configuration:
```env
# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/dbname

# Exchange API Keys
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET=your_binance_secret
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET=your_alpaca_secret

# Application Settings
MAX_POSITION_SIZE=1000
MAX_DAILY_LOSS=500
MAX_OPEN_POSITIONS=5
```

### Database Setup

1. Run migrations:
```bash
alembic upgrade head
```

2. Initialize database (if needed):
```bash
python scripts/init_db.py
```

## Running the Application

### Development Mode

Start the API server:
```bash
uvicorn app:app --reload --port 8000
```

Start the trading engine:
```bash
python main.py
```

### Docker Deployment

Build and run with Docker Compose:
```bash
docker compose up --build
```

## Development

### Creating Database Migrations

After modifying models:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Running Tests

```bash
pytest tests/
pytest tests/integration/  # Integration tests only
```

### Code Quality

Format code and check style:
```bash
black .
isort .
flake8
```

## Monitoring

### Health Checks

- `GET /api/health`: Overall system health
- `GET /api/health/liveness`: Basic liveness probe
- `GET /api/health/readiness`: Service readiness check

### Metrics

Prometheus metrics available at:
- `GET /metrics`: Application metrics
- Port 9090: Standalone metrics server

## Documentation

- API Documentation: http://localhost:8000/docs
- Additional documentation in `docs/` directory:
  - `concepts/`: Core architectural concepts
  - `guides/`: How-to guides
  - `ref/`: API reference
  - `starting/`: Getting started guide
  - `support/`: Troubleshooting

## Support

For issues and support:
1. Check the troubleshooting guide in `docs/support/`
2. Review existing GitHub issues
3. Submit detailed bug reports with logs and reproduction steps

## License

[License details here]
