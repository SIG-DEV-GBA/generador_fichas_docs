"""
Script de inicialización de ChromaDB.
Indexa las fichas de ejemplo del dataset para el sistema RAG.
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag_system import RAGSystem
from app.core.pdf_extractor import PDFExtractor
from loguru import logger
import argparse


def extract_ficha_text(docx_path: Path) -> str:
    """
    Extrae texto de una ficha Word.

    Args:
        docx_path: Ruta al .docx

    Returns:
        Texto extraído
    """
    try:
        from docx import Document

        doc = Document(docx_path)
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"Error extrayendo texto de {docx_path.name}: {e}")
        return ""


def extract_metadata_from_folder_name(folder_name: str) -> dict:
    """
    Extrae metadatos del nombre de la carpeta.

    Args:
        folder_name: Nombre de la carpeta

    Returns:
        Dict con metadatos
    """
    # Formato esperado: "Municipio (Provincia) - Tipo de Ayuda"
    parts = folder_name.split(" - ")

    metadata = {"tipo": "desconocido", "organismo": "desconocido"}

    if len(parts) >= 2:
        metadata["organismo"] = parts[0].strip()
        metadata["tipo"] = parts[1].strip()

    return metadata


def index_dataset(rag: RAGSystem, dataset_path: Path, reindex: bool = False):
    """
    Indexa todas las fichas del dataset.

    Args:
        rag: Sistema RAG
        dataset_path: Ruta al dataset
        reindex: Si True, elimina índice existente
    """
    if reindex:
        logger.warning("Reindexando: eliminando colección existente...")
        rag.delete_all()

    logger.info(f"Buscando fichas en: {dataset_path}")

    # Buscar todos los archivos .docx que sean fichas
    fichas = []
    for docx_file in dataset_path.rglob("*.docx"):
        # Filtrar por nombre (debe contener "Ficha" o "FICHA")
        if "ficha" in docx_file.name.lower() and not docx_file.name.startswith("~"):
            logger.debug(f"Encontrada ficha: {docx_file.name}")

            # Extraer texto
            text = extract_ficha_text(docx_file)

            if text and len(text) > 100:
                # Extraer metadatos del folder
                folder_name = docx_file.parent.name
                metadata = extract_metadata_from_folder_name(folder_name)
                metadata["filename"] = docx_file.name
                metadata["folder"] = folder_name

                fichas.append(
                    {
                        "id": docx_file.stem,
                        "text": text,
                        "metadata": metadata,
                    }
                )

    if not fichas:
        logger.warning("No se encontraron fichas para indexar")
        return

    logger.info(f"Total de fichas encontradas: {len(fichas)}")

    # Indexar en lote
    rag.index_multiple(fichas)

    logger.info(f"✓ {len(fichas)} fichas indexadas correctamente")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Inicializar base de datos vectorial")
    parser.add_argument(
        "--dataset",
        type=str,
        default="Fichas y documentación",
        help="Ruta al dataset de fichas",
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Reindexar (eliminar índice existente)",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Setup de ChromaDB para sistema RAG")
    logger.info("=" * 60)

    # Verificar que el dataset existe
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        logger.error(f"Dataset no encontrado: {dataset_path}")
        logger.error("Asegúrate de ejecutar desde el directorio raíz del proyecto")
        sys.exit(1)

    # Inicializar RAG
    logger.info("Inicializando ChromaDB...")
    rag = RAGSystem()

    # Verificar estado actual
    current_count = rag.count()
    logger.info(f"Fichas actualmente indexadas: {current_count}")

    if current_count > 0 and not args.reindex:
        logger.warning("Ya existen fichas indexadas.")
        logger.warning("Usa --reindex para eliminar y reindexar.")
        confirm = input("¿Continuar y añadir más fichas? (s/n): ")
        if confirm.lower() != "s":
            logger.info("Cancelado por el usuario")
            sys.exit(0)

    # Indexar dataset
    index_dataset(rag, dataset_path, args.reindex)

    # Stats finales
    final_count = rag.count()
    logger.info("=" * 60)
    logger.info(f"✓ Setup completado")
    logger.info(f"✓ Total de fichas en el sistema: {final_count}")
    logger.info(f"✓ Fichas añadidas: {final_count - current_count}")

    info = rag.get_collection_info()
    logger.info(f"✓ Colección: {info['name']}")
    logger.info(f"✓ Ubicación: {info['persist_directory']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
