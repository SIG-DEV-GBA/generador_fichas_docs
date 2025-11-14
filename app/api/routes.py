"""
Rutas y endpoints de la API REST.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path
import uuid
from datetime import datetime
import json
from loguru import logger

from app.models import (
    FichaGenerateRequest,
    FichaGenerateResponse,
    HealthCheckResponse,
)
from app.core import PDFExtractor, LLMProcessor, RAGSystem, WordGenerator
from app.config import settings
from app import __version__

# Router principal
router = APIRouter(prefix="/api/v1", tags=["fichas"])

# Instancias globales (se inicializan en startup)
pdf_extractor = PDFExtractor()
rag_system = None  # Se inicializa en startup
llm_processor = None  # Se inicializa en startup
word_generator = WordGenerator()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check del servicio.
    Verifica estado de LLM y ChromaDB.
    """
    try:
        vector_db_status = "connected"
        if rag_system:
            try:
                rag_system.count()
            except:
                vector_db_status = "error"
        else:
            vector_db_status = "disconnected"

        return HealthCheckResponse(
            status="healthy",
            version=__version__,
            llm_provider=settings.DEFAULT_LLM_PROVIDER,
            rag_enabled=settings.USE_RAG,
            vector_db=vector_db_status,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version=__version__,
            llm_provider=settings.DEFAULT_LLM_PROVIDER,
            rag_enabled=settings.USE_RAG,
            vector_db="error",
            timestamp=datetime.utcnow(),
        )


@router.post("/generate-ficha", response_model=FichaGenerateResponse)
async def generate_ficha(
    file: UploadFile = File(..., description="PDF de la convocatoria"),
    config: Optional[str] = Form(None, description="Configuración JSON"),
):
    """
    Genera una ficha de ayuda social desde un PDF.

    Args:
        file: Archivo PDF de la convocatoria
        config: Configuración en JSON (opcional)

    Returns:
        FichaGenerateResponse con ID y URL de descarga
    """
    start_time = datetime.now()
    ficha_id = str(uuid.uuid4())

    try:
        # Parsear configuración
        if config:
            try:
                config_dict = json.loads(config)
                request_config = FichaGenerateRequest(**config_dict)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Config JSON inválido")
        else:
            request_config = FichaGenerateRequest()

        logger.info(f"[{ficha_id}] Procesando PDF: {file.filename}")

        # Validar tamaño del archivo
        content = await file.read()
        if len(content) > settings.max_pdf_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"PDF demasiado grande. Máximo: {settings.MAX_PDF_SIZE_MB} MB",
            )

        # Guardar PDF temporalmente
        temp_pdf_path = Path(settings.TEMP_DIR) / f"{ficha_id}.pdf"
        temp_pdf_path.write_bytes(content)

        logger.info(f"[{ficha_id}] Extrayendo texto del PDF...")
        pdf_text = pdf_extractor.extract_text(temp_pdf_path)

        if not pdf_text or len(pdf_text) < 100:
            raise HTTPException(
                status_code=422,
                detail="No se pudo extraer texto suficiente del PDF",
            )

        logger.info(f"[{ficha_id}] Texto extraído: {len(pdf_text)} caracteres")

        # Generar ficha con LLM
        logger.info(f"[{ficha_id}] Generando ficha con LLM...")
        result = llm_processor.generate_ficha(
            pdf_text=pdf_text,
            use_rag=request_config.include_rag,
            usuario=request_config.usuario,
        )

        ficha_data = result["ficha"]
        metadata = result["metadata"]

        # Validar si se solicitó
        validation_passed = True
        if request_config.validate_output:
            logger.info(f"[{ficha_id}] Validando ficha...")
            validation = llm_processor.validate_ficha(ficha_data.dict())
            validation_passed = validation["valid"]

            if not validation_passed:
                logger.warning(f"[{ficha_id}] Validación falló: {validation['errors']}")

        # Generar documento Word
        logger.info(f"[{ficha_id}] Generando documento Word...")
        output_path = Path(settings.OUTPUT_DIR) / f"{ficha_id}.docx"
        word_generator.generate(ficha_data, output_path)

        # Limpiar archivo temporal
        temp_pdf_path.unlink(missing_ok=True)

        # Calcular tiempo de procesamiento
        processing_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"[{ficha_id}] ✓ Ficha generada exitosamente en {processing_time:.2f}s")

        return FichaGenerateResponse(
            status="success",
            ficha_id=ficha_id,
            download_url=f"/api/v1/download/{ficha_id}",
            metadata={
                "processing_time": processing_time,
                "model_used": metadata["model"],
                "provider": metadata["provider"],
                "rag_enabled": metadata["rag_enabled"],
                "rag_examples_used": metadata["rag_examples_count"],
                "validation_passed": validation_passed,
                "pdf_size_kb": len(content) / 1024,
                "pdf_text_length": len(pdf_text),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{ficha_id}] Error generando ficha: {e}", exc_info=True)

        # Limpiar archivos temporales
        Path(settings.TEMP_DIR).joinpath(f"{ficha_id}.pdf").unlink(missing_ok=True)

        return FichaGenerateResponse(
            status="error",
            ficha_id=ficha_id,
            error_message=str(e),
        )


@router.get("/download/{ficha_id}")
async def download_ficha(ficha_id: str):
    """
    Descarga el archivo Word generado.

    Args:
        ficha_id: ID de la ficha generada

    Returns:
        Archivo .docx
    """
    file_path = Path(settings.OUTPUT_DIR) / f"{ficha_id}.docx"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Ficha no encontrada")

    return FileResponse(
        path=file_path,
        filename=f"ficha_{ficha_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/status/{ficha_id}")
async def get_status(ficha_id: str):
    """
    Obtiene el estado de una ficha.

    Args:
        ficha_id: ID de la ficha

    Returns:
        Estado de la ficha
    """
    file_path = Path(settings.OUTPUT_DIR) / f"{ficha_id}.docx"

    if file_path.exists():
        return {
            "ficha_id": ficha_id,
            "status": "completed",
            "download_url": f"/api/v1/download/{ficha_id}",
        }
    else:
        return {
            "ficha_id": ficha_id,
            "status": "not_found",
        }


@router.get("/rag/info")
async def get_rag_info():
    """
    Información del sistema RAG.

    Returns:
        Stats de la colección RAG
    """
    if not rag_system:
        raise HTTPException(status_code=503, detail="Sistema RAG no inicializado")

    try:
        info = rag_system.get_collection_info()
        return {
            "status": "active",
            **info,
        }
    except Exception as e:
        logger.error(f"Error obteniendo info de RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def initialize_services():
    """
    Inicializa servicios globales (llamar en startup).
    """
    global rag_system, llm_processor

    logger.info("Inicializando servicios...")

    # Inicializar RAG
    if settings.USE_RAG:
        rag_system = RAGSystem()
        logger.info(f"RAG System inicializado: {rag_system.count()} fichas indexadas")

    # Inicializar LLM Processor
    llm_processor = LLMProcessor(rag_system=rag_system)
    logger.info("LLM Processor inicializado")

    logger.info("✓ Servicios listos")
