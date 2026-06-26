from fastapi import FastAPI

from core.config import settings
from core.logging import setup_logging
from middleware.request_id import RequestIDMiddleware
from middleware.logging import LoggingMiddleware


setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

@app.get("/")
def root():
    return {"message": "Astra Shield AI API is running"}

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)