"""
Main API router for v1 endpoints.
"""
from fastapi import APIRouter
from api.v1 import strategies, orders, trades, risk

# Create main v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["strategies"]
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"]
)

api_router.include_router(
    trades.router,
    prefix="/trades",
    tags=["trades"]
)

api_router.include_router(
    risk.router,
    prefix="/risk",
    tags=["risk"]
)
