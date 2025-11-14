# Arquitectura Técnica del Sistema

## Visión General

Este documento describe la arquitectura técnica del sistema de generación automatizada de fichas de ayudas sociales.

---

## Diagrama de Arquitectura

```
┌───────────────────────────────────────────────────────────────────────┐
│                            CAPA DE CLIENTE                             │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST
                                    ↓
┌───────────────────────────────────────────────────────────────────────┐
│                          CAPA DE API (FastAPI)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │   Routes    │  │  Middleware │  │  Validation │                   │
│  │             │  │             │  │  (Pydantic) │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌───────────────────────────────────────────────────────────────────────┐
│                        CAPA DE LÓGICA DE NEGOCIO                       │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐ │
│  │  PDF Extractor   │───▶│  LLM Processor   │───▶│ Word Generator  │ │
│  │                  │    │                  │    │                 │ │
│  │  - PyMuPDF       │    │  - LangChain     │    │  - python-docx  │ │
│  │  - pdfplumber    │    │  - Prompts       │    │  - Templates    │ │
│  │  - Text cleanup  │    │  - Chains        │    │  - Formatting   │ │
│  └──────────────────┘    └──────────────────┘    └─────────────────┘ │
│                                    │                                   │
│                                    │ Query                             │
│                                    ↓                                   │
│                          ┌──────────────────┐                          │
│                          │   RAG System     │                          │
│                          │                  │                          │
│                          │  - Vector Search │                          │
│                          │  - Example Retr. │                          │
│                          │  - Context Build │                          │
│                          └──────────────────┘                          │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌───────────────────────────────────────────────────────────────────────┐
│                        CAPA DE DATOS Y SERVICIOS                       │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐              │
│  │  ChromaDB    │   │  LLM APIs    │   │  File System │              │
│  │              │   │              │   │              │              │
│  │  - Vectors   │   │  - OpenAI    │   │  - PDFs      │              │
│  │  - Metadata  │   │  - Anthropic │   │  - DOCXs     │              │
│  │  - Embeddings│   │              │   │  - Cache     │              │
│  └──────────────┘   └──────────────┘   └──────────────┘              │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. API Layer (FastAPI)

**Responsabilidad**: Exponer endpoints REST y manejar requests HTTP.

```python
# app/api/routes.py
@router.post("/generate-ficha")
async def generate_ficha(
    file: UploadFile,
    config: FichaConfig = Body(...)
) -> FichaResponse:
    """
    Genera una ficha a partir de un PDF de ayuda social.

    Args:
        file: PDF de la convocatoria
        config: Configuración de generación

    Returns:
        FichaResponse con ID y URL de descarga
    """
```

**Endpoints principales**:
- `POST /api/v1/generate-ficha` - Generar ficha desde PDF
- `GET /api/v1/download/{ficha_id}` - Descargar ficha generada
- `GET /api/v1/status/{ficha_id}` - Estado de procesamiento
- `POST /api/v1/batch-generate` - Procesamiento en lote
- `GET /api/v1/health` - Health check

---

### 2. PDF Extractor

**Responsabilidad**: Extraer y limpiar texto de documentos PDF legales.

```python
# app/core/pdf_extractor.py
class PDFExtractor:
    """Extrae información estructurada de PDFs legales."""

    def extract_text(self, pdf_path: str) -> str:
        """Extrae texto completo del PDF."""

    def extract_tables(self, pdf_path: str) -> List[pd.DataFrame]:
        """Extrae tablas detectadas."""

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extrae metadatos (título, fecha, etc.)."""

    def clean_text(self, raw_text: str) -> str:
        """Limpia y normaliza el texto extraído."""
```

**Tecnologías**:
- **PyMuPDF**: Extracción rápida de texto
- **pdfplumber**: Análisis de tablas y layout
- **regex**: Limpieza de artefactos

**Desafíos**:
- PDFs con múltiples columnas
- Tablas complejas
- Texto escaneado (OCR futuro)
- Formato inconsistente

---

### 3. RAG System

**Responsabilidad**: Búsqueda semántica de ejemplos similares para mejorar la generación.

```python
# app/core/rag_system.py
class RAGSystem:
    """Sistema de Retrieval Augmented Generation."""

    def __init__(self, chroma_client: ChromaDB):
        self.db = chroma_client
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def index_examples(self, fichas: List[Ficha]) -> None:
        """Indexa fichas de ejemplo en la BD vectorial."""

    def retrieve_similar(
        self,
        query: str,
        k: int = 3
    ) -> List[Ficha]:
        """Recupera k fichas similares."""

    def build_context(
        self,
        pdf_text: str,
        examples: List[Ficha]
    ) -> str:
        """Construye contexto para el prompt."""
```

**Flujo RAG**:
1. **Embedding** del texto extraído del PDF
2. **Búsqueda vectorial** de fichas similares
3. **Selección** de top-k ejemplos más relevantes
4. **Construcción** del contexto enriquecido
5. **Inyección** en el prompt del LLM

**Métricas de similitud**:
- Cosine similarity
- Tipo de ayuda (tag-based)
- Ámbito geográfico

---

### 4. LLM Processor

**Responsabilidad**: Orquestar la generación de fichas usando LLMs.

```python
# app/core/llm_processor.py
class LLMProcessor:
    """Procesa documentos usando LLMs con LangChain."""

    def __init__(
        self,
        model_name: str = "claude-3.5-sonnet",
        rag_system: Optional[RAGSystem] = None
    ):
        self.llm = self._initialize_llm(model_name)
        self.rag = rag_system
        self.prompt_template = self._load_prompt_template()

    def generate_ficha(
        self,
        pdf_text: str,
        use_rag: bool = True
    ) -> FichaData:
        """Genera ficha estructurada desde texto PDF."""

        # 1. Recuperar ejemplos RAG
        if use_rag:
            examples = self.rag.retrieve_similar(pdf_text, k=3)
            context = self.rag.build_context(pdf_text, examples)
        else:
            context = pdf_text

        # 2. Construir prompt
        prompt = self.prompt_template.format(
            document=context,
            schema=FichaData.schema_json()
        )

        # 3. Llamar al LLM
        response = self.llm.invoke(prompt)

        # 4. Parsear y validar
        ficha_data = self._parse_response(response)

        return ficha_data
```

**Estrategias de prompting**:
- **Zero-shot**: Sin ejemplos
- **Few-shot**: Con 2-3 ejemplos de RAG
- **Chain-of-Thought**: Razonamiento paso a paso
- **Structured Output**: JSON schema validation

---

### 5. Word Generator

**Responsabilidad**: Generar documentos Word con formato profesional.

```python
# app/core/word_generator.py
class WordGenerator:
    """Genera documentos Word desde datos estructurados."""

    def __init__(self, template_path: Optional[str] = None):
        self.template = self._load_template(template_path)

    def generate(
        self,
        ficha_data: FichaData,
        output_path: str
    ) -> str:
        """Genera archivo .docx desde FichaData."""

        doc = Document()

        # Header
        self._add_header(doc, ficha_data)

        # Sections
        self._add_section(doc, "ORGANISMO", ficha_data.organismo)
        self._add_section(doc, "OBJETO", ficha_data.objeto)
        self._add_section(doc, "BENEFICIARIOS", ficha_data.beneficiarios)
        self._add_list_section(doc, "REQUISITOS", ficha_data.requisitos)
        # ... más secciones

        # Footer
        self._add_footer(doc, ficha_data)

        doc.save(output_path)
        return output_path
```

**Características**:
- Estilos consistentes
- Tablas automáticas
- Listas con formato
- Headers/footers
- Numeración automática

---

## Modelos de Datos

### FichaData Schema

```python
# app/models/ficha_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class FichaData(BaseModel):
    """Schema de una ficha de ayuda social."""

    # Identificación
    titulo: str = Field(..., description="Título de la ayuda")
    organismo: str = Field(..., description="Organismo convocante")
    ambito: str = Field(..., description="Municipal/Provincial/Autonómico/Nacional")
    tipo_ayuda: str = Field(..., description="Categoría de la ayuda")

    # Descripción
    objeto: str = Field(..., description="Descripción del objeto de la ayuda")
    beneficiarios: str = Field(..., description="Descripción de beneficiarios")

    # Requisitos y condiciones
    requisitos: List[str] = Field(default_factory=list)
    documentacion: List[str] = Field(default_factory=list)

    # Económico
    cuantia: str = Field(..., description="Cuantía de la ayuda")

    # Plazos
    plazo_solicitud: str = Field(..., description="Plazo de presentación")
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None

    # Presentación
    lugar_presentacion: str = Field(..., description="Dónde presentar")
    forma_presentacion: Optional[str] = None

    # Legal
    normativa: str = Field(..., description="Base legal")

    # Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None

    # Extra
    observaciones: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Ayudas de Emergencia Social",
                "organismo": "Ayuntamiento de Madrid",
                "ambito": "Municipal",
                "tipo_ayuda": "Emergencia Social",
                # ...
            }
        }
```

---

## Flujo de Procesamiento Completo

### Flujo Normal (Happy Path)

```
1. Cliente sube PDF
   ↓
2. API valida formato y tamaño
   ↓
3. PDF Extractor extrae texto
   ↓
4. RAG System busca ejemplos similares
   ↓
5. LLM Processor genera FichaData
   ↓
6. Pydantic valida estructura
   ↓
7. Word Generator crea .docx
   ↓
8. API devuelve URL de descarga
```

### Flujo con Errores

```
1. Cliente sube PDF
   ↓
2. API valida formato → [ERROR: formato inválido]
   → Devuelve 400 Bad Request

3. PDF Extractor extrae texto → [ERROR: PDF corrupto]
   → Log error, devuelve 422 Unprocessable Entity

5. LLM Processor genera FichaData → [ERROR: timeout API]
   → Retry 3 veces
   → Si falla, devuelve 503 Service Unavailable

6. Pydantic valida estructura → [ERROR: campos faltantes]
   → Intenta completar con valores por defecto
   → Si falla, marca como "requiere revisión manual"
```

---

## Estrategia de Prompts

### Template Base

```python
FICHA_GENERATION_PROMPT = """
Eres un experto en análisis de documentación legal de ayudas sociales en España.

Tu tarea es extraer información estructurada de la siguiente convocatoria y generar una ficha resumida.

## DOCUMENTO A ANALIZAR:
{document}

## EJEMPLOS DE FICHAS SIMILARES:
{examples}

## SCHEMA DE SALIDA (JSON):
{schema}

## INSTRUCCIONES:
1. Lee cuidadosamente todo el documento
2. Identifica los campos obligatorios
3. Extrae la información de forma precisa
4. Si un campo no está presente, indica "No especificado"
5. Usa un lenguaje claro y conciso
6. Mantén la estructura JSON estricta

## OUTPUT:
Genera ÚNICAMENTE un JSON válido con la estructura especificada.
"""
```

### Mejoras de Prompting

1. **Few-shot con RAG**: Inyectar 2-3 ejemplos reales
2. **Chain-of-Thought**: Pedir razonamiento paso a paso
3. **Self-consistency**: Generar múltiples respuestas y votar
4. **Validation loop**: Re-preguntar si falta información crítica

---

## Consideraciones de Performance

### Tiempos Esperados

| Fase | Tiempo | Optimización |
|------|--------|--------------|
| PDF Extraction | 1-3s | Caché por hash |
| RAG Search | 0.5-1s | Índice optimizado |
| LLM Call | 5-15s | Streaming, modelo más rápido |
| Word Generation | 0.5-1s | Templates pre-compilados |
| **Total** | **7-20s** | - |

### Escalabilidad

- **Horizontal**: Múltiples workers con Gunicorn
- **Caché**: Redis para resultados frecuentes
- **Queue**: Celery para procesamiento asíncrono
- **Rate limiting**: Por usuario/IP

---

## Seguridad

### Validaciones

- Tamaño máximo de PDF: 10 MB
- Timeout de procesamiento: 60s
- Rate limiting: 10 requests/min por IP
- Sanitización de inputs

### Datos sensibles

- No almacenar PDFs originales después de procesamiento
- Logs sin información personal
- API keys en variables de entorno

---

## Monitoreo y Logging

### Métricas Clave

```python
- requests_total
- requests_duration_seconds
- llm_api_calls_total
- llm_api_errors_total
- pdf_extraction_errors
- validation_failures
- fichas_generated_total
```

### Logging Structure

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "service": "llm_processor",
  "event": "ficha_generated",
  "ficha_id": "uuid-123",
  "model": "claude-3.5-sonnet",
  "tokens": 2500,
  "duration_ms": 8500,
  "success": true
}
```

---

## Testing Strategy

### Niveles de Testing

1. **Unit Tests**: Cada componente aislado
2. **Integration Tests**: Flujo completo con mocks
3. **E2E Tests**: Con PDFs reales del dataset
4. **Quality Tests**: Evaluación de salidas con métricas

### Métricas de Calidad

```python
# scripts/evaluate_quality.py
def evaluate_ficha_quality(
    generated: FichaData,
    ground_truth: FichaData
) -> Dict[str, float]:
    """Evalúa calidad de ficha generada."""

    return {
        "field_completeness": 0.95,  # % campos completos
        "semantic_similarity": 0.88,  # Similitud con ground truth
        "schema_validity": 1.0,       # JSON válido
        "manual_review_score": 4.2    # De 1-5
    }
```

---

## Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - chromadb

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - ./data/vector_db:/chroma/data
```

---

## Referencias

- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [RAG Paper](https://arxiv.org/abs/2005.11401)
