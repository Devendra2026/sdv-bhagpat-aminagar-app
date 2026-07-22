from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.crud.rbac import seed_default_rbac
from app.db.base import Base
from app.db.session import SessionLocal, engine


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_rbac(db)

    app = FastAPI(title=settings.app_name)

    allowed_origins = [
        settings.frontend_origin.rstrip("/"),
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # settings.frontend_origin or use 'frontend domain'
        allow_credentials=True,
        allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS",], #use '*' if it restricts some methods  means allowe every methods
        allow_headers=["Accept","Content-Type","Authorization"],   #use '*' if it restricts some headers  means allowe every header
    )


    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
