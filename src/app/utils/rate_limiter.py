from typing import Dict
from time import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
from starlette.requests import Request


class RateLimiter(BaseHTTPMiddleware):

    def __init__(self, app, max_requests: int, period: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.period = period
        self.requests: Dict[str, tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host
        current_time = time()
        if client_ip not in self.requests:
            self.requests[client_ip] = (1, current_time)
        else:
            count, start_time = self.requests[client_ip]
            if current_time - start_time < self.period:
                if count >= self.max_requests:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "请求过于频繁,请稍后再试。"}
                    )
                self.requests[client_ip] = (count + 1, start_time)
            else:
                self.requests[client_ip] = (1, current_time)

        return await call_next(request)
