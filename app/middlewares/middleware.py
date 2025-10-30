import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)  # обязательно передаём app

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Выполнение запроса
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        print(f"{request.method} {request.url.path} - {process_time:.2f} ms")

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
