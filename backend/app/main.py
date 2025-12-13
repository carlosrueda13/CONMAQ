from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.limiter import limiter
from app.core.logging_config import configure_logging
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.logging_middleware import AccessLogMiddleware
from app.api.metrics_exporter import router as metrics_router
from prometheus_client import Counter
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
configure_logging()

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "conmaq_requests_total", "Total HTTP requests", ["method", "path", "status"]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Skip metrics endpoint itself to avoid noise
        if request.url.path != "/metrics":
            REQUEST_COUNT.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
            ).inc()
        return response

# Initialize Rate Limiter (Moved to app.core.limiter)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Prometheus Middleware
app.add_middleware(PrometheusMiddleware)

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add Access Log Middleware
app.add_middleware(AccessLogMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Set up Trusted Host
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "testserver"]
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router)

@app.get("/")
def root():
    return {"message": "Welcome to Agendamiento API"}
