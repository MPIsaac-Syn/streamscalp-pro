from enum import Enum
from datetime import datetime
from typing import Optional, Dict, List, Any

class OrderState(Enum):
    PENDING = "pending"
    SENT = "sent_to_exchange"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    ERROR = "error"

class OrderStateManager:
    """
    Manages the state transitions of orders and provides reconciliation
    with exchange order status.
    """
    def __init__(self):
        self.order_states = {}  # Maps order_id to current state
        self.order_history = {}  # Maps order_id to state history
        self.retry_attempts = {}  # Maps order_id to retry count
        self.max_retries = 3
    
    def initialize_order(self, order_id: str) -> None:
        """Initialize a new order with PENDING state"""
        self.order_states[order_id] = OrderState.PENDING
        self.order_history[order_id] = [{
            'state': OrderState.PENDING,
            'timestamp': datetime.utcnow(),
            'details': None
        }]
        self.retry_attempts[order_id] = 0
    
    def update_state(self, order_id: str, new_state: OrderState, details: Optional[Dict[str, Any]] = None) -> None:
        """Update the state of an order and record in history"""
        if order_id not in self.order_states:
            self.initialize_order(order_id)
            
        self.order_states[order_id] = new_state
        self.order_history[order_id].append({
            'state': new_state,
            'timestamp': datetime.utcnow(),
            'details': details
        })
    
    def get_current_state(self, order_id: str) -> Optional[OrderState]:
        """Get the current state of an order"""
        return self.order_states.get(order_id)
    
    def get_state_history(self, order_id: str) -> List[Dict[str, Any]]:
        """Get the full state history of an order"""
        return self.order_history.get(order_id, [])
    
    def should_retry(self, order_id: str) -> bool:
        """Determine if an order should be retried based on its state and retry count"""
        if order_id not in self.order_states:
            return False
            
        current_state = self.order_states[order_id]
        retry_count = self.retry_attempts.get(order_id, 0)
        
        # Only retry orders in ERROR or REJECTED state, and only up to max_retries
        if current_state in [OrderState.ERROR, OrderState.REJECTED] and retry_count < self.max_retries:
            self.retry_attempts[order_id] += 1
            return True
            
        return False
    
    def reconcile_with_exchange(self, order_id: str, exchange_status: str, details: Dict[str, Any]) -> None:
        """
        Reconcile the internal order state with the status reported by the exchange
        
        Args:
            order_id: The order ID
            exchange_status: The status reported by the exchange
            details: Additional details from the exchange
        """
        # Map exchange status to internal OrderState
        status_mapping = {
            'new': OrderState.SENT,
            'open': OrderState.SENT,
            'closed': OrderState.FILLED,
            'canceled': OrderState.CANCELED,
            'expired': OrderState.CANCELED,
            'rejected': OrderState.REJECTED,
            'failed': OrderState.ERROR
        }
        
        # Handle partially filled orders
        if exchange_status == 'closed' and details.get('filled') != details.get('amount'):
            new_state = OrderState.PARTIALLY_FILLED
        else:
            new_state = status_mapping.get(exchange_status.lower(), OrderState.ERROR)
            
        self.update_state(order_id, new_state, details)
