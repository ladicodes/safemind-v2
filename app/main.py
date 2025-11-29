from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, report_router, emergency_router, notification_router, agency_router, followup_router
from app.events import startup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SafeMind", version="1.0.0", description="Mental health emergency response platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await startup.initialize_database()
    await startup.initialize_message_queue()
    await startup.initialize_connection_manager()
    await startup.preload_nlp_model()
    logger.info("Application startup completed")

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(report_router.router, prefix="/api/reports", tags=["reports"])
app.include_router(emergency_router.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(notification_router.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(agency_router.router, prefix="/api/agencies", tags=["agencies"])
app.include_router(followup_router.router, prefix="/api/followup", tags=["followup"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SafeMind"}