from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.seed import seed_demo_data


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Seed demo data on startup if database is empty."""
    seeded = seed_demo_data()
    if seeded:
        print(f"Seeded {seeded} demo AI systems")
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered EU AI Act compliance agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}
