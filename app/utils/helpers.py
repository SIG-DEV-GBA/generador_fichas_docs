"""
Funciones helper generales.
"""

import uuid
import re
from datetime import datetime
from pathlib import Path


def generate_unique_id() -> str:
    """
    Genera un ID único usando UUID4.

    Returns:
        String con UUID
    """
    return str(uuid.uuid4())


def format_datetime(dt: datetime, format: str = "%d/%m/%Y %H:%M:%S") -> str:
    """
    Formatea un datetime.

    Args:
        dt: Datetime a formatear
        format: Formato de salida

    Returns:
        String formateado
    """
    return dt.strftime(format)


def clean_filename(filename: str, max_length: int = 100) -> str:
    """
    Limpia un nombre de archivo para que sea seguro.

    Args:
        filename: Nombre original
        max_length: Longitud máxima

    Returns:
        Nombre limpio y seguro
    """
    # Eliminar caracteres no permitidos
    cleaned = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Reemplazar espacios por guiones bajos
    cleaned = cleaned.replace(" ", "_")

    # Eliminar caracteres de control
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", cleaned)

    # Limitar longitud
    if len(cleaned) > max_length:
        name, ext = Path(cleaned).stem, Path(cleaned).suffix
        max_name_length = max_length - len(ext)
        cleaned = name[:max_name_length] + ext

    return cleaned


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto añadiendo sufijo.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a añadir

    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def parse_spanish_date(date_str: str) -> datetime | None:
    """
    Parsea fecha en español (ej: "15 de enero de 2025").

    Args:
        date_str: String con fecha

    Returns:
        Datetime o None si falla
    """
    months = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }

    pattern = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})"
    match = re.search(pattern, date_str.lower())

    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))

        if month_name in months:
            month = months[month_name]
            try:
                return datetime(year, month, day)
            except ValueError:
                return None

    return None


def format_currency(amount: float, decimals: int = 2) -> str:
    """
    Formatea cantidad como moneda española.

    Args:
        amount: Cantidad
        decimals: Número de decimales

    Returns:
        String formateado (ej: "1.234,56 €")
    """
    # Formatear con separador de miles y decimales
    formatted = f"{amount:,.{decimals}f}"

    # Reemplazar coma por punto para miles
    formatted = formatted.replace(",", "X")
    # Reemplazar punto por coma para decimales
    formatted = formatted.replace(".", ",")
    # Reemplazar X por punto para miles
    formatted = formatted.replace("X", ".")

    return f"{formatted} €"


def extract_email(text: str) -> list[str]:
    """
    Extrae emails de un texto.

    Args:
        text: Texto a analizar

    Returns:
        Lista de emails encontrados
    """
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.findall(pattern, text)


def extract_phone(text: str) -> list[str]:
    """
    Extrae teléfonos españoles de un texto.

    Args:
        text: Texto a analizar

    Returns:
        Lista de teléfonos encontrados
    """
    # Patrones comunes de teléfonos españoles
    patterns = [
        r"\b\d{9}\b",  # 9 dígitos
        r"\b\d{3}\s\d{3}\s\d{3}\b",  # 123 456 789
        r"\b\d{3}\s\d{2}\s\d{2}\s\d{2}\b",  # 123 45 67 89
        r"\+34\s?\d{9}\b",  # +34 123456789
    ]

    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))

    return list(set(phones))  # Eliminar duplicados
