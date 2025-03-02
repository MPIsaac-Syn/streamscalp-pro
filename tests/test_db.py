from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models.base import Base
from models.trade import Trade
from models.order import Order
from models.strategy import Strategy

# Create engine and session
engine = create_engine("sqlite:///./trades.db")
Session = sessionmaker(bind=engine)
session = Session()

# Test creating a strategy
test_strategy = Strategy(
    name="Simple Moving Average Crossover",
    description="A strategy that trades when fast MA crosses slow MA",
    market="BTCUSDT",
    timeframe="1h",
    parameters={"fast_ma": 9, "slow_ma": 21},
    risk_settings={"max_position_size": 0.1, "stop_loss_pct": 0.02},
    active=True
)

# Test creating an order
test_order = Order(
    order_id="ord123456",
    symbol="BTCUSDT",
    side="buy",
    quantity=0.01,
    price=50000.0,
    status="filled",
    timestamp=datetime.utcnow()
)

# Test creating a trade
test_trade = Trade(
    trade_id="trd123456",
    order_id="ord123456",
    symbol="BTCUSDT",
    side="buy",
    quantity=0.01,
    price=50000.0,
    fee=0.0075,
    timestamp=datetime.utcnow()
)

# Add to session and commit
session.add(test_strategy)
session.add(test_order)
session.add(test_trade)
session.commit()

# Query and print results
print("\n=== Strategies ===")
strategies = session.query(Strategy).all()
for strategy in strategies:
    print(f"ID: {strategy.id}, Name: {strategy.name}, Market: {strategy.market}")

print("\n=== Orders ===")
orders = session.query(Order).all()
for order in orders:
    print(f"ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Price: {order.price}")

print("\n=== Trades ===")
trades = session.query(Trade).all()
for trade in trades:
    print(f"ID: {trade.id}, Symbol: {trade.symbol}, Value: {trade.value}")

# Close session
session.close()
