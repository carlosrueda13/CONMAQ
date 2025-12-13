import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("access")

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (start_time - time.time()) * -1
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "method=%s path=%s status=%s latency_ms=%.2f ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            process_time * 1000,
            client_ip,
        )
        return response
