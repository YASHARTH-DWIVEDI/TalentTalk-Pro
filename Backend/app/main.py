from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Startup: Initializing Application")
    await init_db()
    logger.info("Startup: Database initialized")
    yield
    # Shutdown
    logger.info("Shutdown: Application stopping")

from fastapi.staticfiles import StaticFiles
from app.api_routes import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Mount static files for audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {"message": "Welcome to TalentTalk Pro API", "docs": "/docs"}
