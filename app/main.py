import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

import app.models  # noqa: F401 - registers SQLAlchemy models
from app.core.config import settings
from app.db.base import init_db
from app.routers import (
    auth_router,
    journal_router,
    mood_router,
    reflection_router,
    resource_router,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
FRONTEND_PATH = Path(__file__).parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if settings.AUTO_SEED_DEMO:
        from app.seed import seed_demo_data

        seed_demo_data()
    logger.info("%s API started", settings.APP_NAME)
    yield


app = FastAPI(
    title="SafeSpace / SafeMind API",
    version="2.0.0",
    description="A demo-ready mental wellness journal, mood tracker, and supportive reflection API.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["authentication"])
app.include_router(journal_router.router, prefix="/api/journals", tags=["journals"])
app.include_router(mood_router.router, prefix="/api/moods", tags=["moods"])
app.include_router(
    reflection_router.router, prefix="/api/reflections", tags=["reflections"]
)
app.include_router(resource_router.router, prefix="/api/resources", tags=["resources"])


@app.get("/")
def root() -> FileResponse:
    return FileResponse(FRONTEND_PATH)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "database": "connected"}


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled request error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT)
