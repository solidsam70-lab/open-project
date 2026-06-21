import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from jarvis.database.session import init_db
from jarvis.api.v1 import router as v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("jarvis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JARVIS AI Operating System")
    try:
        await init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning("Database initialization deferred: %s", e)
    yield
    logger.info("Shutting down JARVIS")


app = FastAPI(
    title="JARVIS - AI Operating System",
    version="1.0.0",
    description="AI Operating System for AKS Solutions running on Odoo ERP",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("JARVIS_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "JARVIS",
        "version": "1.0.0",
        "environment": os.getenv("JARVIS_ENV", "development"),
    }


@app.get("/")
async def root():
    return {
        "message": "JARVIS AI Operating System",
        "version": "1.0.0",
        "docs": "/docs",
    }
