"""
Modelos de Request/Response para la API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class FichaGenerateRequest(BaseModel):
    """Request para generar una ficha."""

    include_rag: bool = Field(
        default=True,
        description="Usar sistema RAG para mejorar generación con ejemplos similares",
    )

    validate_output: bool = Field(
        default=True,
        description="Validar la ficha generada contra el schema",
    )

    model: Optional[Literal["claude-3.5-sonnet", "gpt-4o", "gpt-3.5-turbo"]] = Field(
        default=None,
        description="Modelo LLM a usar (None = usar configuración por defecto)",
    )

    usuario: str = Field(
        default="PROYECTO_FICHAS_IA",
        description="Usuario que genera la ficha (para campo 'USUARIO' en Otros datos)",
    )


class FichaGenerateResponse(BaseModel):
    """Response después de generar una ficha."""

    status: Literal["success", "error", "processing"] = Field(
        ...,
        description="Estado de la generación",
    )

    ficha_id: str = Field(
        ...,
        description="ID único de la ficha generada",
    )

    download_url: Optional[str] = Field(
        None,
        description="URL para descargar el archivo .docx generado",
    )

    metadata: Optional[dict] = Field(
        None,
        description="Metadatos de la generación",
    )

    error_message: Optional[str] = Field(
        None,
        description="Mensaje de error si status='error'",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "ficha_id": "550e8400-e29b-41d4-a716-446655440000",
                "download_url": "/api/v1/download/550e8400-e29b-41d4-a716-446655440000",
                "metadata": {
                    "processing_time": 12.5,
                    "confidence_score": 0.92,
                    "model_used": "claude-3.5-sonnet",
                    "rag_examples_used": 3,
                    "validation_passed": True,
                },
            }
        }


class HealthCheckResponse(BaseModel):
    """Response del health check."""

    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    version: str = Field(..., description="Versión de la aplicación")
    llm_provider: str = Field(..., description="Proveedor LLM activo")
    rag_enabled: bool = Field(..., description="Sistema RAG habilitado")
    vector_db: Literal["connected", "disconnected", "error"] = "connected"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "llm_provider": "anthropic",
                "rag_enabled": True,
                "vector_db": "connected",
                "timestamp": "2025-01-15T10:30:00Z",
            }
        }


class BatchGenerateRequest(BaseModel):
    """Request para generación en lote."""

    config: FichaGenerateRequest = Field(
        default_factory=FichaGenerateRequest,
        description="Configuración común para todas las fichas",
    )

    max_concurrent: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Máximo de PDFs a procesar concurrentemente",
    )


class BatchGenerateResponse(BaseModel):
    """Response de generación en lote."""

    batch_id: str = Field(..., description="ID único del batch")
    total_files: int = Field(..., description="Total de archivos en el batch")
    status: Literal["queued", "processing", "completed", "failed"] = "queued"
    results: list[FichaGenerateResponse] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "batch-123456",
                "total_files": 5,
                "status": "processing",
                "results": [],
            }
        }
