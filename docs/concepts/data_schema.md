# Database Schema

StreamScalp Pro uses SQLAlchemy ORM with SQLite for local development and PostgreSQL for production. This document outlines the database schema and relationships.

## Core Tables

### Strategies

The `strategies` table stores trading strategy configurations:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Unique strategy name |
| description | String | Strategy description |
| market | String | Target market (e.g., BTCUSDT) |
| timeframe | String | Timeframe (e.g., 1h, 4h, 1d) |
| parameters | JSON | Strategy-specific parameters |
| risk_settings | JSON | Risk management settings |
| active | Boolean | Whether strategy is active |
| performance_metrics | JSON | Performance statistics |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Orders

The `orders` table tracks orders placed on exchanges:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| order_id | String | Exchange order ID |
| symbol | String | Trading pair symbol |
| side | String | Buy or sell |
| quantity | Float | Order quantity |
| price | Float | Order price |
| status | String | Order status |
| timestamp | DateTime | Order timestamp |

### Trades

The `trades` table records executed trades:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| trade_id | String | Exchange trade ID |
| order_id | String | Related order ID |
| symbol | String | Trading pair symbol |
| side | String | Buy or sell |
| quantity | Float | Trade quantity |
| price | Float | Execution price |
| fee | Float | Trading fee |
| timestamp | DateTime | Execution timestamp |

## Relationships

Currently, the tables are independent, but future versions will implement the following relationships:

- A Strategy can have many Orders
- An Order can result in multiple Trades

## Database Migration

The project uses Alembic for database migrations. Migration scripts are stored in the `migrations/versions` directory.

To create a new migration after model changes:

```
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```
alembic upgrade head
```
