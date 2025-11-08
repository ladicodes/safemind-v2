from fastapi import FastAPI

from app.db.base import Base, engine
from app.routers import auth_router


def create_app() -> FastAPI:
    application = FastAPI(title="Safemind API")
    application.include_router(auth_router.router)
    return application


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    from app.models import user  # noqa: F401

    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to Safemind API!"}