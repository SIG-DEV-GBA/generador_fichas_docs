"""
Procesador LLM para generación de fichas.
Orquesta la generación usando LangChain + Claude/GPT.
"""

from typing import Dict, Any, Optional, Literal
from pathlib import Path
import json
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from app.config import settings
from app.models.ficha_schema import FichaData
from app.core.rag_system import RAGSystem


class LLMProcessor:
    """
    Procesador de LLMs para generación de fichas.
    Soporta OpenAI y Anthropic con LangChain.
    """

    def __init__(
        self,
        provider: Optional[Literal["openai", "anthropic"]] = None,
        model_name: Optional[str] = None,
        rag_system: Optional[RAGSystem] = None,
    ):
        """
        Inicializa el procesador LLM.

        Args:
            provider: Proveedor LLM (openai/anthropic)
            model_name: Nombre del modelo específico
            rag_system: Sistema RAG para ejemplos
        """
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.rag_system = rag_system

        logger.info(f"Inicializando LLM Processor con proveedor: {self.provider}")

        # Inicializar LLM según proveedor
        if self.provider == "openai":
            self.llm = ChatOpenAI(
                model=model_name or settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )
        elif self.provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model_name or settings.ANTHROPIC_MODEL,
                temperature=settings.ANTHROPIC_TEMPERATURE,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")

        # Cargar instrucciones de generación
        self.instructions = self._load_instructions()

        # Output parser
        self.parser = PydanticOutputParser(pydantic_object=FichaData)

        logger.info(f"LLM Processor listo: {self.llm.model_name}")

    def _load_instructions(self) -> Dict[str, Any]:
        """
        Carga las instrucciones de generación desde el JSON.

        Returns:
            Diccionario con las instrucciones
        """
        instructions_path = Path("docs/schemas_prompts/Instrucciones Ficha Social Definitivas ChatGPT V4.4 (1).json")

        if instructions_path.exists():
            with open(instructions_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            logger.warning("Instrucciones no encontradas, usando defaults")
            return {}

    def _build_system_prompt(self) -> str:
        """
        Construye el system prompt desde las instrucciones JSON.

        Returns:
            System prompt completo
        """
        if not self.instructions:
            return "Eres un experto en análisis de documentación legal de ayudas sociales."

        prompt_parts = [
            "# ROL Y OBJETIVO",
            "Eres un experto en análisis de documentación legal de ayudas sociales en España.",
            "Tu tarea es extraer información estructurada de convocatorias y generar fichas resumidas.",
            "\n# REGLAS GENERALES\n",
        ]

        # Añadir reglas comunes
        if "reglas_comunes" in self.instructions:
            for regla in self.instructions["reglas_comunes"]:
                prompt_parts.append(f"- {regla}")

        prompt_parts.append("\n# VALORES DE REFERENCIA 2025\n")

        # Añadir valores de referencia
        if "valores_referencia_2025" in self.instructions:
            valores = self.instructions["valores_referencia_2025"]
            prompt_parts.append("**IPREM 2025:**")
            for k, v in valores.get("iprem", {}).items():
                prompt_parts.append(f"- {k.replace('_', ' ').title()}: {v}")

            prompt_parts.append("\n**SMI 2025:**")
            for k, v in valores.get("smi", {}).items():
                prompt_parts.append(f"- {k.replace('_', ' ').title()}: {v}")

        prompt_parts.append("\n# FORMATO DE SALIDA\n")
        prompt_parts.append("Debes generar un JSON válido siguiendo ESTRICTAMENTE el schema proporcionado.")
        prompt_parts.append("Todos los campos con sus frases iniciales obligatorias deben ser respetados.")

        return "\n".join(prompt_parts)

    def _build_user_prompt(
        self,
        pdf_text: str,
        rag_examples: Optional[list] = None,
    ) -> str:
        """
        Construye el user prompt con el documento y ejemplos.

        Args:
            pdf_text: Texto extraído del PDF
            rag_examples: Ejemplos del RAG

        Returns:
            User prompt formateado
        """
        parts = ["# DOCUMENTO A ANALIZAR\n", pdf_text]

        if rag_examples:
            parts.append("\n\n# EJEMPLOS DE REFERENCIA\n")
            parts.append("Estos son ejemplos de fichas bien estructuradas:\n")
            for i, example in enumerate(rag_examples, 1):
                parts.append(f"\n## Ejemplo {i}\n")
                parts.append(example["text"][:1500])  # Limitar longitud
                parts.append("\n---\n")

        parts.append("\n# INSTRUCCIONES\n")
        parts.append("Analiza el documento y genera una ficha siguiendo:")
        parts.append("1. El schema JSON proporcionado")
        parts.append("2. Las reglas generales")
        parts.append("3. Los ejemplos de referencia")
        parts.append("\nGenera ÚNICAMENTE el JSON, sin texto adicional.")

        return "\n".join(parts)

    def generate_ficha(
        self,
        pdf_text: str,
        use_rag: bool = True,
        usuario: str = "PROYECTO_FICHAS_IA",
    ) -> Dict[str, Any]:
        """
        Genera una ficha estructurada desde texto PDF.

        Args:
            pdf_text: Texto extraído del PDF
            use_rag: Si usar sistema RAG para ejemplos
            usuario: Usuario que genera la ficha

        Returns:
            Dict con la ficha generada y metadata
        """
        logger.info("Iniciando generación de ficha...")

        # 1. Recuperar ejemplos RAG si está habilitado
        rag_examples = []
        if use_rag and self.rag_system:
            logger.info("Recuperando ejemplos del RAG...")
            rag_examples = self.rag_system.retrieve_similar(
                pdf_text,
                k=settings.RAG_TOP_K,
            )
            logger.info(f"Recuperados {len(rag_examples)} ejemplos")

        # 2. Construir prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(pdf_text, rag_examples)

        # 3. Añadir format instructions del parser
        format_instructions = self.parser.get_format_instructions()

        # 4. Crear template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_prompt}\n\n{format_instructions}"),
        ])

        # 5. Crear chain
        chain = prompt_template | self.llm | self.parser

        # 6. Ejecutar generación
        try:
            logger.info("Invocando LLM...")
            ficha_data = chain.invoke({
                "user_prompt": user_prompt,
                "format_instructions": format_instructions,
            })

            logger.info("✓ Ficha generada exitosamente")

            return {
                "ficha": ficha_data,
                "metadata": {
                    "model": self.llm.model_name,
                    "provider": self.provider,
                    "rag_enabled": use_rag,
                    "rag_examples_count": len(rag_examples),
                },
            }

        except Exception as e:
            logger.error(f"Error generando ficha: {e}")
            raise

    def validate_ficha(self, ficha_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una ficha contra el schema.

        Args:
            ficha_data: Datos de la ficha

        Returns:
            Resultado de validación
        """
        try:
            validated = FichaData(**ficha_data)
            return {
                "valid": True,
                "ficha": validated,
                "errors": [],
            }
        except Exception as e:
            return {
                "valid": False,
                "ficha": None,
                "errors": [str(e)],
            }
