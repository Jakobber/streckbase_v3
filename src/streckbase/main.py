from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from streckbase.api import (
    health,
    items,
    multipliers,
    purchases,
    statistics,
    systembolaget,
    users,
)
from streckbase.core.config import settings

STATIC_DIR = Path("public")


def create_app() -> FastAPI:
    app = FastAPI(title="Streckbase V3")

    # CORS fully open, matching v2
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users.router, prefix="/api")
    app.include_router(items.router, prefix="/api")
    app.include_router(purchases.router, prefix="/api")
    app.include_router(statistics.router, prefix="/api")
    app.include_router(systembolaget.router, prefix="/api")
    app.include_router(multipliers.router, prefix="/api")
    app.include_router(health.router, prefix="/api")

    # v2 served downloaded product images from /api/static
    (STATIC_DIR / "images").mkdir(parents=True, exist_ok=True)
    app.mount("/api/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("streckbase.main:app", host="0.0.0.0", port=settings.port, reload=True)


if __name__ == "__main__":
    main()
