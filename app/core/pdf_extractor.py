"""
Módulo de extracción de PDFs.
Extrae texto, tablas y metadatos de documentos PDF legales.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pymupdf  # PyMuPDF
import pdfplumber
from loguru import logger


class PDFExtractor:
    """
    Extractor de información de documentos PDF.
    Maneja PDFs legales complejos con múltiples columnas y tablas.
    """

    def __init__(self):
        """Inicializa el extractor de PDFs."""
        self.supported_extensions = [".pdf"]

    def extract_text(self, pdf_path: str | Path) -> str:
        """
        Extrae texto completo del PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Texto extraído y limpiado

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato no es válido
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

        if pdf_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Formato no soportado: {pdf_path.suffix}")

        logger.info(f"Extrayendo texto de: {pdf_path.name}")

        try:
            # Usar PyMuPDF para extracción rápida
            doc = pymupdf.open(pdf_path)
            text_parts = []

            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
                    logger.debug(f"Página {page_num}: {len(text)} caracteres")

            doc.close()

            raw_text = "\n\n".join(text_parts)
            logger.info(
                f"Extracción completa: {len(raw_text)} caracteres, {len(doc)} páginas"
            )

            # Limpiar texto
            cleaned_text = self.clean_text(raw_text)

            return cleaned_text

        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {e}")
            raise

    def extract_tables(self, pdf_path: str | Path) -> List[Dict[str, Any]]:
        """
        Extrae tablas del PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Lista de tablas extraídas (cada tabla como dict con metadata)
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Extrayendo tablas de: {pdf_path.name}")

        tables_data = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()

                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # Al menos header + 1 fila
                            tables_data.append(
                                {
                                    "page": page_num,
                                    "table_index": table_idx,
                                    "rows": len(table),
                                    "columns": len(table[0]) if table else 0,
                                    "data": table,
                                    "markdown": self._table_to_markdown(table),
                                }
                            )
                            logger.debug(
                                f"Tabla encontrada en página {page_num}: {len(table)} filas"
                            )

            logger.info(f"Total de tablas extraídas: {len(tables_data)}")
            return tables_data

        except Exception as e:
            logger.error(f"Error extrayendo tablas: {e}")
            return []

    def extract_metadata(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Extrae metadatos del PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con metadatos
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Extrayendo metadatos de: {pdf_path.name}")

        try:
            doc = pymupdf.open(pdf_path)
            metadata = doc.metadata or {}

            info = {
                "filename": pdf_path.name,
                "size_bytes": pdf_path.stat().st_size,
                "size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "pages": len(doc),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "encrypted": doc.is_encrypted,
            }

            doc.close()

            logger.info(f"Metadatos extraídos: {info['pages']} páginas, {info['size_mb']} MB")
            return info

        except Exception as e:
            logger.error(f"Error extrayendo metadatos: {e}")
            return {"filename": pdf_path.name, "error": str(e)}

    def clean_text(self, raw_text: str) -> str:
        """
        Limpia y normaliza texto extraído.

        Args:
            raw_text: Texto sin procesar

        Returns:
            Texto limpio
        """
        # Eliminar saltos de línea excesivos
        text = re.sub(r"\n{3,}", "\n\n", raw_text)

        # Eliminar espacios múltiples
        text = re.sub(r" {2,}", " ", text)

        # Eliminar tabulaciones
        text = text.replace("\t", " ")

        # Eliminar caracteres de control
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)

        # Normalizar guiones
        text = text.replace("–", "-").replace("—", "-")

        # Eliminar headers/footers comunes (números de página)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

        return text.strip()

    def extract_full(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Extrae todo: texto, tablas y metadatos.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con toda la información extraída
        """
        logger.info(f"Extracción completa de: {pdf_path}")

        return {
            "text": self.extract_text(pdf_path),
            "tables": self.extract_tables(pdf_path),
            "metadata": self.extract_metadata(pdf_path),
        }

    @staticmethod
    def _table_to_markdown(table: List[List[str]]) -> str:
        """
        Convierte tabla a formato Markdown.

        Args:
            table: Tabla como lista de listas

        Returns:
            Representación en Markdown
        """
        if not table:
            return ""

        # Header
        markdown_lines = []
        header = table[0]
        markdown_lines.append("| " + " | ".join(str(cell or "") for cell in header) + " |")
        markdown_lines.append("|" + "---|" * len(header))

        # Rows
        for row in table[1:]:
            markdown_lines.append("| " + " | ".join(str(cell or "") for cell in row) + " |")

        return "\n".join(markdown_lines)

    def is_boletin_oficial(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Detecta si el PDF es un boletín oficial (BOP/BOE/BOJA/etc).

        Args:
            pdf_path: Ruta al PDF

        Returns:
            Dict con detección de boletín
        """
        text = self.extract_text(pdf_path)
        metadata = self.extract_metadata(pdf_path)

        # Patrones de detección
        patterns = {
            "BOP": r"BOLET[ÍI]N OFICIAL DE LA PROVINCIA",
            "BOE": r"BOLET[ÍI]N OFICIAL DEL ESTADO",
            "BOJA": r"BOLET[ÍI]N OFICIAL DE LA JUNTA DE ANDALUC[ÍI]A",
            "BOCM": r"BOLET[ÍI]N OFICIAL DE LA COMUNIDAD DE MADRID",
            "DOGC": r"DIARI OFICIAL DE LA GENERALITAT DE CATALUNYA",
            "BOPV": r"BOLET[ÍI]N OFICIAL DEL PA[ÍI]S VASCO",
        }

        detected = {}
        for tipo, pattern in patterns.items():
            match = re.search(pattern, text[:2000], re.IGNORECASE)
            if match:
                detected["tipo"] = tipo
                detected["match"] = match.group(0)
                break

        # Extraer número y fecha
        numero_match = re.search(r"n[úu]m(?:ero)?[.\s:]+(\d+)", text[:3000], re.IGNORECASE)
        fecha_match = re.search(
            r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", text[:3000], re.IGNORECASE
        )

        return {
            "es_boletin": bool(detected),
            "tipo_boletin": detected.get("tipo"),
            "numero": numero_match.group(1) if numero_match else None,
            "fecha": fecha_match.group(0) if fecha_match else None,
            "metadata": metadata,
        }
