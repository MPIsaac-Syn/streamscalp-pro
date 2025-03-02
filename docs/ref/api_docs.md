# API Documentation

StreamScalp Pro provides a RESTful API for interacting with the trading system programmatically.

## Authentication

All API endpoints require authentication using an API key.

**Request Header**:
```
Authorization: Bearer YOUR_API_KEY
```

## Strategies API

### List Strategies

**Endpoint**: `GET /api/strategies`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Simple Moving Average Crossover",
    "description": "A strategy that trades when fast MA crosses slow MA",
    "market": "BTCUSDT",
    "timeframe": "1h",
    "parameters": {"fast_ma": 9, "slow_ma": 21},
    "risk_settings": {"max_position_size": 0.1, "stop_loss_pct": 0.02},
    "active": true,
    "performance_metrics": null,
    "created_at": "2025-03-01T12:00:00",
    "updated_at": "2025-03-01T12:00:00"
  }
]
```

### Get Strategy

**Endpoint**: `GET /api/strategies/{id}`

**Response**:
```json
{
  "id": 1,
  "name": "Simple Moving Average Crossover",
  "description": "A strategy that trades when fast MA crosses slow MA",
  "market": "BTCUSDT",
  "timeframe": "1h",
  "parameters": {"fast_ma": 9, "slow_ma": 21},
  "risk_settings": {"max_position_size": 0.1, "stop_loss_pct": 0.02},
  "active": true,
  "performance_metrics": null,
  "created_at": "2025-03-01T12:00:00",
  "updated_at": "2025-03-01T12:00:00"
}
```

### Create Strategy

**Endpoint**: `POST /api/strategies`

**Request Body**:
```json
{
  "name": "Bollinger Bands Strategy",
  "description": "A strategy that trades based on Bollinger Bands",
  "market": "ETHUSDT",
  "timeframe": "4h",
  "parameters": {"std_dev": 2, "period": 20},
  "risk_settings": {"max_position_size": 0.05, "stop_loss_pct": 0.03},
  "active": true
}
```

**Response**: The created strategy object

### Update Strategy

**Endpoint**: `PUT /api/strategies/{id}`

**Request Body**: Strategy fields to update

**Response**: The updated strategy object

### Delete Strategy

**Endpoint**: `DELETE /api/strategies/{id}`

**Response**: `204 No Content`

## Orders API

### List Orders

**Endpoint**: `GET /api/orders`

**Query Parameters**:
- `symbol` (optional): Filter by symbol
- `status` (optional): Filter by status
- `limit` (optional): Limit number of results

**Response**: Array of order objects

### Get Order

**Endpoint**: `GET /api/orders/{id}`

**Response**: Order object

### Create Order

**Endpoint**: `POST /api/orders`

**Request Body**:
```json
{
  "symbol": "BTCUSDT",
  "side": "buy",
  "quantity": 0.01,
  "price": 50000.0
}
```

**Response**: The created order object

## Trades API

### List Trades

**Endpoint**: `GET /api/trades`

**Query Parameters**:
- `symbol` (optional): Filter by symbol
- `side` (optional): Filter by side (buy/sell)
- `from_date` (optional): Filter by date range start
- `to_date` (optional): Filter by date range end

**Response**: Array of trade objects

### Get Trade

**Endpoint**: `GET /api/trades/{id}`

**Response**: Trade object

## Market Data API

### Get Candles

**Endpoint**: `GET /api/market/candles`

**Query Parameters**:
- `symbol` (required): Trading pair symbol
- `timeframe` (required): Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
- `limit` (optional): Number of candles to return

**Response**:
```json
[
  {
    "timestamp": "2025-03-01T12:00:00",
    "open": 50000.0,
    "high": 50100.0,
    "low": 49900.0,
    "close": 50050.0,
    "volume": 10.5
  }
]
```

### Get Ticker

**Endpoint**: `GET /api/market/ticker`

**Query Parameters**:
- `symbol` (required): Trading pair symbol

**Response**:
```json
{
  "symbol": "BTCUSDT",
  "price": 50050.0,
  "volume": 1000.5,
  "change_24h": 2.5,
  "high_24h": 51000.0,
  "low_24h": 49000.0
}
```

## Error Responses

All API endpoints return standard HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with error details:

```json
{
  "error": "Invalid parameters",
  "message": "Symbol is required",
  "code": "INVALID_PARAMS"
}
```
