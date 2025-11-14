"""
Funciones de validación.
"""

from pathlib import Path
from datetime import date
from typing import Tuple


def validate_pdf_file(file_path: str | Path) -> Tuple[bool, str]:
    """
    Valida que el archivo es un PDF válido.

    Args:
        file_path: Ruta al archivo

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False, "Archivo no encontrado"

    if not file_path.is_file():
        return False, "La ruta no es un archivo"

    if file_path.suffix.lower() != ".pdf":
        return False, f"Formato no válido: {file_path.suffix}. Se esperaba .pdf"

    if file_path.stat().st_size == 0:
        return False, "El archivo está vacío"

    # Verificar magic bytes del PDF
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            if header != b"%PDF":
                return False, "El archivo no es un PDF válido"
    except Exception as e:
        return False, f"Error leyendo archivo: {str(e)}"

    return True, ""


def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, str]:
    """
    Valida que el rango de fechas sea coherente.

    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if end_date < start_date:
        return False, "La fecha de fin no puede ser anterior a la fecha de inicio"

    # Validar que no sea un rango demasiado largo (más de 5 años)
    days_diff = (end_date - start_date).days
    if days_diff > 1825:  # 5 años
        return False, "El rango de fechas es demasiado largo (máximo 5 años)"

    return True, ""


def validate_cuantia_format(cuantia_text: str) -> Tuple[bool, str]:
    """
    Valida que el texto de cuantía tenga el formato correcto.

    Args:
        cuantia_text: Texto de cuantía

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    import re

    # Debe contener el símbolo €
    if "€" not in cuantia_text:
        return False, "La cuantía debe incluir el símbolo €"

    # Verificar formato de números (coma decimal)
    # Pattern: número con coma decimal y dos decimales
    pattern = r"\d+(?:\.\d{3})*,\d{2}\s*€"

    matches = re.findall(pattern, cuantia_text)
    if not matches:
        return False, "La cuantía debe tener formato: X.XXX,XX €"

    return True, ""


def validate_boletin_format(boletin_text: str) -> Tuple[bool, str]:
    """
    Valida formato de boletín oficial.

    Args:
        boletin_text: Texto del boletín

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    import re

    # Pattern esperado: BOP (provincia) núm. X, dd/mm/aaaa
    patterns = [
        r"BOP\s+\([^)]+\)\s+núm\.\s+\d+,\s+\d{2}/\d{2}/\d{4}",
        r"BOE\s+núm\.\s+\d+,\s+\d{2}/\d{2}/\d{4}",
        r"BDNS\s+N[°º]\s+\d+,\s+\d{2}/\d{2}/\d{4}",
    ]

    for pattern in patterns:
        if re.search(pattern, boletin_text):
            return True, ""

    return False, "El formato del boletín no es válido. Esperado: 'BOP (provincia) núm. X, dd/mm/aaaa'"
