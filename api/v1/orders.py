"""
API endpoints for order management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.order import Order as DBOrder
from config.database import get_db
from utils.logger import setup_logger
from schemas.order import OrderCreate, OrderResponse, OrderUpdate
from utils.di_container import container

router = APIRouter()
logger = setup_logger("order_routes")

# --- Database Operations ---
def get_order(db: Session, order_id: int):
    """Get an order by database ID"""
    return db.query(DBOrder).filter(DBOrder.id == order_id).first()

def get_order_by_exchange_id(db: Session, order_id: str):
    """Get an order by exchange order ID"""
    return db.query(DBOrder).filter(DBOrder.order_id == order_id).first()

# --- API Endpoints ---
@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    strategy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all orders with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        symbol: Filter by trading symbol
        status: Filter by order status
        strategy_id: Filter by strategy ID
        db: Database session
        
    Returns:
        List of orders
    """
    query = db.query(DBOrder)
    
    if symbol:
        query = query.filter(DBOrder.symbol == symbol)
    if status:
        query = query.filter(DBOrder.status == status)
    if strategy_id:
        query = query.filter(DBOrder.strategy_id == strategy_id)
        
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        Order details
        
    Raises:
        HTTPException: If order not found
    """
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order and send it to the appropriate exchange.
    
    Args:
        order: Order data
        db: Database session
        
    Returns:
        Created order
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        # Get the order manager from the container
        order_manager = container.get('order_manager')
        
        # Prepare order data for processing
        order_data = order.dict()
        
        # Process the order through the order manager
        result = await order_manager.process_order(order_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order was rejected by risk manager or exchange"
            )
        
        # Get the created order from the database
        db_order = get_order_by_exchange_id(db, order_data.get('order_id'))
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Order was processed but not found in database"
            )
            
        logger.info(f"Created new order: {db_order.order_id}")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )

@router.delete("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancel an existing order.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        Canceled order
        
    Raises:
        HTTPException: If order not found or cancellation fails
    """
    try:
        # Get the order
        db_order = get_order(db, order_id=order_id)
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
            
        # Get the order manager from the container
        order_manager = container.get('order_manager')
        
        # Cancel the order
        result = await order_manager.cancel_order(db_order.order_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel order"
            )
            
        # Refresh the order from the database
        db.refresh(db_order)
        logger.info(f"Canceled order ID {order_id}")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )

@router.get("/{order_id}/status", response_model=dict)
async def get_order_status(order_id: int, db: Session = Depends(get_db)):
    """
    Get the current status of an order from the exchange.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        Order status from exchange
        
    Raises:
        HTTPException: If order not found or status check fails
    """
    try:
        # Get the order
        db_order = get_order(db, order_id=order_id)
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
            
        # Get the order manager from the container
        order_manager = container.get('order_manager')
        
        # Get the order status
        result = await order_manager.get_order_status(db_order.order_id)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get order status: {result.get('error')}"
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order status: {str(e)}"
        )
