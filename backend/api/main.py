from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import setup_logging
from middleware.request_id import RequestIDMiddleware
from middleware.logging import LoggingMiddleware
from api.routers.health import router as health_router
from api.phishing_routes import router as phishing_router
from api.phishing.check_sms import router as sms_router
from agents.phishing_agent.feeds.feed_manager import refresh_feeds
setup_logging()
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI-powered cybersecurity platform for phishing detection",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
@app.on_event("startup")
async def startup_event():
    refresh_feeds()
app.include_router(health_router)
app.include_router(phishing_router)
app.include_router(sms_router)
@app.get("/")
def root():
    return {"message": "Astra Shield AI API is running"}