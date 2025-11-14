"""
Aplicación principal FastAPI.
Punto de entrada del servidor.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.api import router
from app.api.routes import initialize_services
from app import __version__


# Configurar logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Inicializa y limpia recursos.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Iniciando Generador de Fichas IA")
    logger.info(f"Versión: {__version__}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    logger.info("=" * 60)

    # Asegurar directorios existen
    settings.ensure_directories()
    logger.info("✓ Directorios verificados")

    # Inicializar servicios
    initialize_services()

    logger.info("✓ Aplicación lista")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Cerrando aplicación...")


# Crear aplicación
app = FastAPI(
    title="Generador de Fichas de Ayudas Sociales",
    description="API para generación automatizada de fichas de ayudas sociales usando IA",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router
app.include_router(router)


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "app": "Generador de Fichas de Ayudas Sociales",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
