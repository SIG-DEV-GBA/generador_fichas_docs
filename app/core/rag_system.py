"""
Sistema RAG (Retrieval Augmented Generation).
Búsqueda semántica de ejemplos similares para mejorar la generación.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.config import settings


class RAGSystem:
    """
    Sistema de Retrieval Augmented Generation.
    Usa ChromaDB para almacenar y buscar fichas similares.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        """
        Inicializa el sistema RAG.

        Args:
            persist_directory: Directorio de persistencia de ChromaDB
            collection_name: Nombre de la colección
            embedding_model: Modelo de embeddings a usar
        """
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.embedding_model_name = embedding_model or settings.EMBEDDING_MODEL

        logger.info(f"Inicializando RAG System con modelo: {self.embedding_model_name}")

        # Inicializar modelo de embeddings
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Inicializar ChromaDB
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False,
            )
        )

        # Obtener o crear colección
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Colección existente cargada: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Fichas de ayudas sociales para RAG"},
            )
            logger.info(f"Nueva colección creada: {self.collection_name}")

    def index_ficha(
        self,
        ficha_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Indexa una ficha en la base de datos vectorial.

        Args:
            ficha_id: ID único de la ficha
            text: Texto completo de la ficha
            metadata: Metadatos (organismo, tipo, etc.)
        """
        logger.debug(f"Indexando ficha: {ficha_id}")

        # Generar embedding
        embedding = self.embedding_model.encode(text).tolist()

        # Añadir a ChromaDB
        self.collection.add(
            ids=[ficha_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

        logger.info(f"Ficha indexada: {ficha_id}")

    def index_multiple(
        self,
        fichas: List[Dict[str, Any]],
    ) -> int:
        """
        Indexa múltiples fichas en lote.

        Args:
            fichas: Lista de diccionarios con {id, text, metadata}

        Returns:
            Número de fichas indexadas
        """
        logger.info(f"Indexando {len(fichas)} fichas en lote...")

        if not fichas:
            return 0

        ids = [f["id"] for f in fichas]
        texts = [f["text"] for f in fichas]
        metadatas = [f["metadata"] for f in fichas]

        # Generar embeddings en lote
        embeddings = self.embedding_model.encode(texts).tolist()

        # Añadir a ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(f"✓ {len(fichas)} fichas indexadas correctamente")
        return len(fichas)

    def retrieve_similar(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recupera las k fichas más similares a la query.

        Args:
            query: Texto de búsqueda (PDF extraído)
            k: Número de resultados a devolver
            filter_metadata: Filtros por metadatos (ej. {"tipo": "emergencia"})

        Returns:
            Lista de fichas similares con sus scores
        """
        logger.info(f"Buscando {k} fichas similares...")

        # Generar embedding de la query
        query_embedding = self.embedding_model.encode(query).tolist()

        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_metadata,
        )

        # Formatear resultados
        similar_fichas = []
        for i in range(len(results["ids"][0])):
            similar_fichas.append(
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                }
            )

        logger.info(f"Encontradas {len(similar_fichas)} fichas similares")
        return similar_fichas

    def build_context(
        self,
        pdf_text: str,
        examples: List[Dict[str, Any]],
    ) -> str:
        """
        Construye contexto enriquecido para el prompt del LLM.

        Args:
            pdf_text: Texto extraído del PDF
            examples: Ejemplos similares del RAG

        Returns:
            Contexto formateado
        """
        context_parts = ["# DOCUMENTO A ANALIZAR\n", pdf_text, "\n\n"]

        if examples:
            context_parts.append("# EJEMPLOS DE FICHAS SIMILARES\n\n")
            for i, example in enumerate(examples, start=1):
                context_parts.append(f"## Ejemplo {i}\n")
                context_parts.append(f"**Tipo:** {example['metadata'].get('tipo', 'N/A')}\n")
                context_parts.append(f"**Organismo:** {example['metadata'].get('organismo', 'N/A')}\n\n")
                context_parts.append(f"{example['text'][:1000]}...\n\n")
                context_parts.append("---\n\n")

        return "".join(context_parts)

    def count(self) -> int:
        """
        Cuenta el número de fichas indexadas.

        Returns:
            Número de fichas en la colección
        """
        return self.collection.count()

    def delete_all(self) -> None:
        """Elimina todas las fichas de la colección."""
        logger.warning("Eliminando todas las fichas de la colección...")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Fichas de ayudas sociales para RAG"},
        )
        logger.info("Colección reiniciada")

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la colección.

        Returns:
            Diccionario con stats de la colección
        """
        return {
            "name": self.collection_name,
            "count": self.count(),
            "metadata": self.collection.metadata,
            "persist_directory": self.persist_directory,
        }
