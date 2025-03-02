"""
Order management module for StreamScalp Pro.

This module is responsible for processing orders, managing their lifecycle,
and interacting with exchange adapters.
"""
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from models.order import Order
from models.trade import Trade
from utils.logger import setup_logger
from utils.event_bus import EventBus

logger = setup_logger("order_manager")

class OrderState:
    """Order states for tracking order lifecycle"""
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    ERROR = "error"

class OrderManager:
    """
    Order manager for processing and tracking orders.
    
    Attributes:
        exchange_adapter: Exchange adapter for sending orders
        event_bus: Event bus for publishing order events
        risk_manager: Risk manager for validating orders
        config: Order manager configuration
        running: Whether the order manager is running
        pending_orders: Dictionary of pending orders
    """
    
    def __init__(self, 
                 exchange_adapter: Any, 
                 event_bus: EventBus,
                 risk_manager: Any,
                 config: Dict[str, Any] = None):
        """
        Initialize the OrderManager with dependencies.
        
        Args:
            exchange_adapter: Exchange adapter
            event_bus: Event bus
            risk_manager: Risk manager
            config: Order manager configuration
        """
        self.exchange_adapter = exchange_adapter
        self.event_bus = event_bus
        self.risk_manager = risk_manager
        self.config = config or {}
        self.running = False
        self.pending_orders = {}
        
        # Subscribe to order events
        self._setup_event_subscriptions()
        
        logger.info("Order manager initialized")
    
    async def _setup_event_subscriptions(self):
        """Setup event subscriptions for order events"""
        await self.event_bus.subscribe("order.new", self._handle_new_order_event)
        await self.event_bus.subscribe("order.cancel", self._handle_cancel_order_event)
        logger.info("Event subscriptions set up")
    
    async def _handle_new_order_event(self, event_data: Dict[str, Any]):
        """Handle new order event from event bus"""
        logger.info(f"Received new order event: {event_data}")
        await self.process_order(event_data)
    
    async def _handle_cancel_order_event(self, event_data: Dict[str, Any]):
        """Handle cancel order event from event bus"""
        logger.info(f"Received cancel order event: {event_data}")
        order_id = event_data.get("order_id")
        if order_id:
            await self.cancel_order(order_id)
    
    async def start(self):
        """Start the order manager"""
        if self.running:
            return
        
        self.running = True
        logger.info("Order manager started")
    
    async def stop(self):
        """Stop the order manager"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Order manager stopped")
    
    async def process_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process an order through risk validation and send to exchange.
        
        Args:
            order_data: Order data
            
        Returns:
            Order result or None if rejected
        """
        if not self.running:
            logger.warning("Order manager is not running, rejecting order")
            return None
        
        try:
            # Generate internal order ID if not provided
            if 'order_id' not in order_data:
                order_data['order_id'] = f"order_{uuid.uuid4().hex[:8]}"
            
            # Validate order through risk manager
            account_info = await self.exchange_adapter.get_account_info()
            account_balance = account_info.get('balance', 0)
            
            risk_result = await self.risk_manager.evaluate_order(order_data, account_balance)
            if not risk_result.get('approved', False):
                logger.warning(f"Order rejected by risk manager: {risk_result.get('reason')}")
                
                # Publish rejection event
                await self.event_bus.publish("order.rejected", {
                    "order_id": order_data['order_id'],
                    "reason": risk_result.get('reason'),
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return None
            
            # Send order to exchange
            logger.info(f"Sending order to exchange: {order_data}")
            result = await self.exchange_adapter.create_order(
                symbol=order_data.get('symbol'),
                side=order_data.get('side'),
                quantity=order_data.get('quantity'),
                order_type=order_data.get('order_type', 'market'),
                price=order_data.get('price')
            )
            
            if not result:
                logger.error(f"Failed to create order on exchange: {order_data}")
                return None
            
            # Update order data with exchange information
            order_data.update({
                "exchange_order_id": result.get("id"),
                "status": result.get("status", OrderState.PENDING),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Publish order created event
            await self.event_bus.publish("order.created", order_data)
            
            # If order is filled immediately, handle the fill
            if result.get("status") in ["filled", "closed"]:
                await self._handle_order_filled(order_data, result)
            
            logger.info(f"Order processed successfully: {order_data['order_id']}")
            return result
        
        except Exception as e:
            logger.exception(f"Error processing order: {e}")
            
            # Publish error event
            await self.event_bus.publish("order.error", {
                "order_id": order_data.get('order_id', 'unknown'),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return None
    
    async def _handle_order_filled(self, order_data: Dict[str, Any], result: Dict[str, Any]):
        """Handle order filled event"""
        # Create trade data
        trade_data = {
            "order_id": order_data.get("order_id"),
            "exchange_order_id": result.get("id"),
            "symbol": order_data.get("symbol"),
            "side": order_data.get("side"),
            "quantity": result.get("filled", order_data.get("quantity")),
            "price": result.get("price", order_data.get("price")),
            "fee": result.get("fee", {}).get("cost", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish trade event
        await self.event_bus.publish("trade.executed", trade_data)
        
        # Update risk manager with position
        position_data = {
            "symbol": order_data.get("symbol"),
            "side": order_data.get("side"),
            "quantity": trade_data.get("quantity"),
            "price": trade_data.get("price"),
            "value": trade_data.get("quantity") * trade_data.get("price")
        }
        
        if order_data.get("side").lower() == "buy":
            await self.risk_manager.record_position_open(position_data)
        else:
            await self.risk_manager.record_position_close(
                order_data.get("symbol"),
                position_data.get("value")
            )
        
        logger.info(f"Order filled and processed: {order_data['order_id']}")
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.
        
        Args:
            order_id: Order ID
            
        Returns:
            True if canceled, False otherwise
        """
        if not self.running:
            logger.warning("Order manager is not running, cannot cancel order")
            return False
        
        try:
            # Get order details from exchange
            order_status = await self.get_order_status(order_id)
            if not order_status or order_status.get("status") == "error":
                logger.error(f"Failed to get order status for cancellation: {order_id}")
                return False
            
            # Check if order can be canceled
            current_status = order_status.get("status")
            if current_status in ["filled", "canceled", "expired"]:
                logger.warning(f"Cannot cancel order in state {current_status}: {order_id}")
                return False
            
            # Send cancel request to exchange
            symbol = order_status.get("symbol")
            result = await self.exchange_adapter.cancel_order(order_id, symbol)
            
            if not result:
                logger.error(f"Failed to cancel order on exchange: {order_id}")
                return False
            
            # Publish cancel event
            await self.event_bus.publish("order.canceled", {
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Order canceled successfully: {order_id}")
            return True
        
        except Exception as e:
            logger.exception(f"Error canceling order: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the current status of an order from the exchange.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status information
        """
        if not self.running:
            logger.warning("Order manager is not running, cannot get order status")
            return {"status": "error", "error": "Order manager not running"}
        
        try:
            # Get order status from exchange
            result = await self.exchange_adapter.get_order_status(order_id)
            
            if not result:
                logger.error(f"Failed to get order status from exchange: {order_id}")
                return {"status": "error", "error": "Failed to get order status"}
            
            logger.info(f"Retrieved order status: {order_id} - {result.get('status')}")
            return result
        
        except Exception as e:
            logger.exception(f"Error getting order status: {e}")
            return {"status": "error", "error": str(e)}