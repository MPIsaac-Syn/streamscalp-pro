"""
API endpoints for risk management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from utils.logger import setup_logger
from utils.di_container import container

router = APIRouter()
logger = setup_logger("risk_routes")

@router.get("/metrics")
async def get_risk_metrics():
    """
    Get current risk management metrics.
    
    Returns:
        Dict with current risk metrics
        
    Raises:
        HTTPException: If risk manager is not available
    """
    try:
        risk_manager = container.get('risk_manager')
        metrics = await risk_manager.get_risk_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting risk metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk metrics: {str(e)}"
        )

@router.post("/config")
async def update_risk_config(config: Dict[str, Any]):
    """
    Update risk management configuration.
    
    Args:
        config: New configuration values
        
    Returns:
        Updated configuration
        
    Raises:
        HTTPException: If risk manager is not available or update fails
    """
    try:
        risk_manager = container.get('risk_manager')
        updated_config = await risk_manager.update_config(config)
        logger.info(f"Risk configuration updated: {updated_config}")
        return updated_config
    except Exception as e:
        logger.error(f"Error updating risk config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update risk configuration: {str(e)}"
        )

@router.post("/evaluate")
async def evaluate_order(order: Dict[str, Any]):
    """
    Evaluate if an order meets risk management criteria.
    
    Args:
        order: Order details including symbol, side, quantity, and price
        
    Returns:
        Dict with evaluation result and reason if rejected
        
    Raises:
        HTTPException: If risk manager is not available or evaluation fails
    """
    try:
        risk_manager = container.get('risk_manager')
        
        # Get account balance from exchange adapter
        exchange_adapter = container.get('exchange_adapter')
        account_info = await exchange_adapter.get_account_info()
        account_balance = account_info.get('balance', 0)
        
        # Evaluate order
        result = await risk_manager.evaluate_order(order, account_balance)
        return result
    except Exception as e:
        logger.error(f"Error evaluating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate order: {str(e)}"
        )

@router.post("/reset")
async def reset_risk_metrics():
    """
    Reset daily risk metrics.
    
    Returns:
        Dict with confirmation message
        
    Raises:
        HTTPException: If risk manager is not available or reset fails
    """
    try:
        risk_manager = container.get('risk_manager')
        await risk_manager.reset_daily_metrics()
        logger.info("Risk metrics reset")
        return {"message": "Risk metrics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting risk metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset risk metrics: {str(e)}"
        )
