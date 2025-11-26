from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, machines, offers, watchlist, notifications, bookings, payments, metrics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
