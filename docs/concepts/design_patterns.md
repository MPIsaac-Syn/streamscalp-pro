# Design Patterns in StreamScalp Pro

This document outlines the key design patterns used in StreamScalp Pro and their implementation.

## Strategy Pattern

The Strategy pattern is used to define a family of trading algorithms, encapsulate each one, and make them interchangeable.

### Implementation

```python
# Abstract strategy interface
class TradingStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
    
    def generate_signals(self, market_data):
        raise NotImplementedError("Subclasses must implement generate_signals")

# Concrete strategy implementations
class MovingAverageCrossover(TradingStrategy):
    def generate_signals(self, market_data):
        fast_ma = self.parameters.get("fast_ma", 9)
        slow_ma = self.parameters.get("slow_ma", 21)
        # Implementation details...
        return signals

class BollingerBands(TradingStrategy):
    def generate_signals(self, market_data):
        period = self.parameters.get("period", 20)
        std_dev = self.parameters.get("std_dev", 2)
        # Implementation details...
        return signals
```

### Usage

```python
# Create strategy instances
sma_strategy = MovingAverageCrossover({"fast_ma": 9, "slow_ma": 21})
bb_strategy = BollingerBands({"period": 20, "std_dev": 2})

# Use strategies interchangeably
signals = sma_strategy.generate_signals(market_data)
```

## Repository Pattern

The Repository pattern is used to abstract the data access layer, making the application more maintainable and testable.

### Implementation

```python
# Repository interface
class TradeRepository:
    def get_by_id(self, trade_id):
        raise NotImplementedError()
    
    def get_all(self, filters=None):
        raise NotImplementedError()
    
    def add(self, trade):
        raise NotImplementedError()
    
    def update(self, trade):
        raise NotImplementedError()
    
    def delete(self, trade_id):
        raise NotImplementedError()

# SQLAlchemy implementation
class SQLAlchemyTradeRepository(TradeRepository):
    def __init__(self, session):
        self.session = session
    
    def get_by_id(self, trade_id):
        return self.session.query(Trade).filter(Trade.id == trade_id).first()
    
    def get_all(self, filters=None):
        query = self.session.query(Trade)
        if filters:
            # Apply filters
            pass
        return query.all()
    
    def add(self, trade):
        self.session.add(trade)
        self.session.commit()
        return trade
    
    # Other methods...
```

### Usage

```python
# Create repository instance
session = Session()
trade_repo = SQLAlchemyTradeRepository(session)

# Use repository
trade = trade_repo.get_by_id(1)
trades = trade_repo.get_all({"symbol": "BTCUSDT"})
```

## Factory Pattern

The Factory pattern is used to create strategy instances based on configuration.

### Implementation

```python
class StrategyFactory:
    _strategies = {
        "moving_average_crossover": MovingAverageCrossover,
        "bollinger_bands": BollingerBands,
        # Other strategies...
    }
    
    @classmethod
    def create_strategy(cls, strategy_type, parameters):
        if strategy_type not in cls._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = cls._strategies[strategy_type]
        return strategy_class(parameters)
```

### Usage

```python
# Create strategy using factory
strategy = StrategyFactory.create_strategy(
    "moving_average_crossover", 
    {"fast_ma": 9, "slow_ma": 21}
)
```

## Observer Pattern

The Observer pattern is used for event-driven architecture, allowing components to subscribe to events.

### Implementation

```python
class EventEmitter:
    def __init__(self):
        self._subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type, data=None):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)

# Market data emitter
class MarketDataEmitter(EventEmitter):
    def __init__(self, exchange_client):
        super().__init__()
        self.exchange_client = exchange_client
    
    def start(self):
        # Start receiving market data
        # When new data arrives, emit events
        self.emit("price_update", {"symbol": "BTCUSDT", "price": 50000})
```

### Usage

```python
# Create emitter
market_data = MarketDataEmitter(exchange_client)

# Subscribe to events
def on_price_update(data):
    print(f"New price for {data['symbol']}: {data['price']}")

market_data.subscribe("price_update", on_price_update)

# Start emitting events
market_data.start()
```

## Dependency Injection

Dependency Injection is used to provide components with their dependencies rather than having them create their own.

### Implementation

```python
class TradingEngine:
    def __init__(self, market_data_provider, strategy_repository, order_executor):
        self.market_data_provider = market_data_provider
        self.strategy_repository = strategy_repository
        self.order_executor = order_executor
    
    def run(self):
        strategies = self.strategy_repository.get_active_strategies()
        for strategy in strategies:
            market_data = self.market_data_provider.get_data(strategy.market)
            signals = strategy.generate_signals(market_data)
            for signal in signals:
                self.order_executor.execute_order(signal)
```

### Usage

```python
# Create dependencies
market_data_provider = MarketDataProvider()
strategy_repository = StrategyRepository(session)
order_executor = OrderExecutor(exchange_client)

# Inject dependencies
engine = TradingEngine(market_data_provider, strategy_repository, order_executor)
engine.run()
```

## Benefits of These Patterns

- **Modularity**: Components can be developed and tested independently
- **Flexibility**: Easy to swap implementations (e.g., different databases)
- **Testability**: Dependencies can be mocked for unit testing
- **Maintainability**: Clear separation of concerns
- **Extensibility**: New strategies can be added without modifying existing code
