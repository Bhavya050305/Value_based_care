"""Top-level API router registration."""

from fastapi import APIRouter
from app.api.v1.segmentation import router as segmentation_router
from app.api.v1.peer_target import router as peer_target_router


from app.api.v1 import (
    acos,
    actions,
    admin,
    anomaly,
    assistant,
    auth,
    dashboard,
    drivers,
    health,
    members,
    outcomes,
    performance,
    portfolio,
    predictions,
    recommendations,
    reports,
    settings,
    simulator,
    trends,
)

api_router = APIRouter()

# Register core foundation routes
api_router.include_router(health.router)
api_router.include_router(auth.router)

# Register domain feature routes
api_router.include_router(portfolio.router)
api_router.include_router(dashboard.router)
api_router.include_router(acos.router)
api_router.include_router(members.router)
api_router.include_router(performance.router)
api_router.include_router(trends.router)
api_router.include_router(drivers.router)
api_router.include_router(predictions.router)
api_router.include_router(segmentation_router)
api_router.include_router(peer_target_router)

# Anomaly Detection
api_router.include_router(anomaly.router)

# What-If Simulator
api_router.include_router(simulator.router)
api_router.include_router(simulator.aco_simulations_router)

# Recommendations
api_router.include_router(recommendations.router)

# Action Tracking
api_router.include_router(actions.router)
api_router.include_router(outcomes.router)

# AI Assistant
api_router.include_router(assistant.router)

# Reports
api_router.include_router(reports.router)

# Settings
api_router.include_router(settings.router)

# Admin
api_router.include_router(admin.router)