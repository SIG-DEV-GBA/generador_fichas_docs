"""
Modelos de datos del proyecto.
"""

from .ficha_schema import (
    FichaData,
    LugarPresentacion,
    OtrosDatos,
    ValoresReferencia2025,
)
from .request_models import (
    FichaGenerateRequest,
    FichaGenerateResponse,
    HealthCheckResponse,
)

__all__ = [
    "FichaData",
    "LugarPresentacion",
    "OtrosDatos",
    "ValoresReferencia2025",
    "FichaGenerateRequest",
    "FichaGenerateResponse",
    "HealthCheckResponse",
]
