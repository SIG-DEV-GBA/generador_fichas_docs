## Guía de Desarrollo

Esta guía explica la arquitectura del código y cómo desarrollar nuevas funcionalidades.

---

## Estructura del Código

```
app/
├── __init__.py           # Versión y metadata
├── main.py               # Aplicación FastAPI principal
├── config.py             # Configuración global
│
├── api/                  # Capa de API
│   ├── routes.py         # Endpoints REST
│   └── dependencies.py   # Dependencias de inyección
│
├── core/                 # Lógica de negocio
│   ├── pdf_extractor.py  # Extracción de PDFs
│   ├── llm_processor.py  # Procesamiento con LLM
│   ├── rag_system.py     # Sistema RAG
│   └── word_generator.py # Generación de Word
│
├── models/               # Modelos de datos
│   ├── ficha_schema.py   # Schema Pydantic de Ficha
│   └── request_models.py # Modelos de Request/Response
│
└── utils/                # Utilidades
    ├── validators.py     # Validaciones
    └── helpers.py        # Helpers generales
```

---

## Componentes Principales

### 1. PDFExtractor (`app/core/pdf_extractor.py`)

**Responsabilidad**: Extraer y limpiar texto de PDFs legales.

**Métodos principales**:
```python
# Extraer texto completo
text = extractor.extract_text(pdf_path)

# Extraer tablas
tables = extractor.extract_tables(pdf_path)

# Extraer metadatos
metadata = extractor.extract_metadata(pdf_path)

# Extracción completa
data = extractor.extract_full(pdf_path)

# Detectar si es boletín oficial
info = extractor.is_boletin_oficial(pdf_path)
```

**Librerías usadas**:
- `pymupdf`: Extracción rápida de texto
- `pdfplumber`: Análisis de tablas

**Mejoras futuras**:
- [ ] OCR para PDFs escaneados (pytesseract)
- [ ] Detección de estructura de documento
- [ ] Extracción de imágenes

---

### 2. RAGSystem (`app/core/rag_system.py`)

**Responsabilidad**: Búsqueda semántica de fichas similares.

**Métodos principales**:
```python
# Indexar una ficha
rag.index_ficha(ficha_id, text, metadata)

# Indexar múltiples
rag.index_multiple(fichas_list)

# Buscar similares
results = rag.retrieve_similar(query, k=3)

# Construir contexto para LLM
context = rag.build_context(pdf_text, examples)
```

**Tecnologías**:
- `chromadb`: Base de datos vectorial
- `sentence-transformers`: Embeddings (all-MiniLM-L6-v2)

**Configuración**:
```python
# En .env
CHROMA_PERSIST_DIRECTORY=./data/vector_db
CHROMA_COLLECTION_NAME=fichas_ayudas_sociales
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_TOP_K=3
```

**Mejoras futuras**:
- [ ] Filtrado avanzado por metadatos
- [ ] Re-ranking de resultados
- [ ] Embeddings más potentes (OpenAI, Cohere)
- [ ] Caché de embeddings

---

### 3. LLMProcessor (`app/core/llm_processor.py`)

**Responsabilidad**: Orquestar generación con LLMs.

**Métodos principales**:
```python
# Generar ficha
result = processor.generate_ficha(
    pdf_text=text,
    use_rag=True,
    usuario="PROJECT_NAME"
)

# Validar ficha
validation = processor.validate_ficha(ficha_dict)
```

**Flujo interno**:
1. Recuperar ejemplos del RAG (si habilitado)
2. Construir system prompt desde instrucciones JSON
3. Construir user prompt con documento + ejemplos
4. Invocar LLM con LangChain
5. Parsear respuesta con Pydantic
6. Validar contra schema

**Configuración de modelos**:
```python
# OpenAI
DEFAULT_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.3

# Anthropic (recomendado)
DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.3
```

**Mejoras futuras**:
- [ ] Streaming de respuestas
- [ ] Retry logic con exponential backoff
- [ ] Fallback entre proveedores
- [ ] Fine-tuning de modelo custom
- [ ] Self-consistency (múltiples generaciones + voting)

---

### 4. WordGenerator (`app/core/word_generator.py`)

**Responsabilidad**: Generar documentos .docx profesionales.

**Métodos principales**:
```python
# Generar desde FichaData
output_path = generator.generate(ficha_data, "output.docx")

# Generar desde dict
output_path = generator.generate_from_dict(ficha_dict, "output.docx")
```

**Características**:
- Estilos personalizados
- Listas con formato
- Headers/footers
- Tablas (futuro)

**Mejoras futuras**:
- [ ] Plantillas personalizables
- [ ] Exportar a PDF
- [ ] Tablas complejas
- [ ] Imágenes y logos
- [ ] Marca de agua

---

## Flujo de Datos Completo

```
┌────────────┐
│ Cliente    │
│ sube PDF   │
└─────┬──────┘
      │
      ↓
┌────────────────────────────────┐
│ FastAPI /api/v1/generate-ficha │
└─────┬──────────────────────────┘
      │
      ↓
┌────────────────┐
│ PDFExtractor   │ → Extrae texto limpio
└─────┬──────────┘
      │
      ↓
┌────────────────┐
│ RAGSystem      │ → Busca 3 ejemplos similares
└─────┬──────────┘
      │
      ↓
┌────────────────┐
│ LLMProcessor   │ → Genera FichaData (JSON)
│                │   1. System prompt con reglas
│                │   2. User prompt con doc + ejemplos
│                │   3. LLM invocation
│                │   4. Parse + Validate
└─────┬──────────┘
      │
      ↓
┌────────────────┐
│ WordGenerator  │ → Genera .docx formateado
└─────┬──────────┘
      │
      ↓
┌────────────────┐
│ Devuelve URL   │
│ de descarga    │
└────────────────┘
```

---

## Añadir Nuevas Funcionalidades

### Ejemplo: Añadir nuevo campo a FichaData

1. **Actualizar schema** (`app/models/ficha_schema.py`):
```python
class FichaData(BaseModel):
    # ... campos existentes
    nuevo_campo: Optional[str] = Field(
        None,
        description="Descripción del nuevo campo"
    )
```

2. **Actualizar instrucciones** (`docs/schemas_prompts/*.json`):
Añadir el nuevo campo a las instrucciones del LLM

3. **Actualizar WordGenerator** (`app/core/word_generator.py`):
```python
def _add_main_content(self, doc, ficha):
    # ... código existente
    if ficha.nuevo_campo:
        self._add_field(doc, "Nuevo Campo", ficha.nuevo_campo)
```

4. **Tests**:
```python
def test_nuevo_campo():
    ficha = FichaData(
        # ... campos obligatorios
        nuevo_campo="valor de prueba"
    )
    assert ficha.nuevo_campo == "valor de prueba"
```

---

### Ejemplo: Añadir nuevo endpoint

1. **Crear ruta** (`app/api/routes.py`):
```python
@router.post("/custom-endpoint")
async def custom_endpoint(param: str):
    # Tu lógica aquí
    return {"result": "success"}
```

2. **Añadir modelos** (`app/models/request_models.py`):
```python
class CustomRequest(BaseModel):
    param: str

class CustomResponse(BaseModel):
    result: str
```

3. **Test**:
```python
def test_custom_endpoint(client):
    response = client.post("/api/v1/custom-endpoint", json={"param": "test"})
    assert response.status_code == 200
```

---

## Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Solo un archivo
pytest tests/test_pdf_extraction.py

# Solo una función
pytest tests/test_pdf_extraction.py::test_extract_text_basic

# Con verbosidad
pytest -v

# Con logs
pytest -s
```

### Estructura de tests

```
tests/
├── test_pdf_extraction.py   # Tests de PDFExtractor
├── test_rag_system.py        # Tests de RAG
├── test_llm_processor.py     # Tests de LLM (mock)
├── test_word_generator.py    # Tests de Word
└── test_api.py               # Tests de endpoints
```

### Fixtures útiles

```python
@pytest.fixture
def sample_pdf():
    return Path("Fichas y documentación/.../*.pdf")

@pytest.fixture
def pdf_extractor():
    return PDFExtractor()

@pytest.fixture
def rag_system():
    return RAGSystem()

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)
```

---

## Debugging

### Logging

El proyecto usa `loguru`:

```python
from loguru import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

**Configurar nivel**:
```bash
# En .env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### Debug del LLM

```python
# Ver prompts completos
import os
os.environ["LANGCHAIN_VERBOSE"] = "true"

# Ver llamadas al LLM
from langchain.globals import set_debug
set_debug(True)
```

### Debug del RAG

```python
rag = RAGSystem()

# Ver colección
info = rag.get_collection_info()
print(info)

# Ver embeddings
results = rag.retrieve_similar("query test", k=5)
for r in results:
    print(f"Distance: {r['distance']}")
    print(f"Text: {r['text'][:200]}...")
```

---

## Optimizaciones

### Performance

1. **Caché de embeddings**:
```python
# Cachear embeddings de fichas frecuentes
@lru_cache(maxsize=100)
def get_cached_embedding(text_hash):
    return embedding_model.encode(text)
```

2. **Procesamiento en lote**:
```python
# Procesar múltiples PDFs concurrentemente
async def process_batch(pdf_paths):
    tasks = [process_one(p) for p in pdf_paths]
    return await asyncio.gather(*tasks)
```

3. **Streaming de respuestas**:
```python
# En LLMProcessor
async def generate_ficha_stream(pdf_text):
    async for chunk in llm.astream(prompt):
        yield chunk
```

### Costos

**Estimación por ficha**:
- GPT-4o: ~$0.05 (2k tokens input, 1k output)
- Claude 3.5 Sonnet: ~$0.03 (2k tokens input, 1k output)
- RAG embedding: ~$0.0001 (negligible)

**Optimizaciones**:
- Usar GPT-3.5 Turbo en desarrollo ($0.005/ficha)
- Caché de resultados frecuentes
- Batch processing para aprovechar rate limits

---

## Troubleshooting

### Error: "OpenAI API key not found"

```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# O usar directamente
export OPENAI_API_KEY="sk-..."
```

### Error: "ChromaDB collection not found"

```bash
# Reinicializar base de datos
python scripts/setup_vector_db.py --reindex
```

### Error: "PDF extraction failed"

```python
# Debug del PDF
from app.core.pdf_extractor import PDFExtractor
ext = PDFExtractor()

# Ver metadatos
metadata = ext.extract_metadata("problematic.pdf")
print(metadata)

# Intentar con pdfplumber
import pdfplumber
with pdfplumber.open("problematic.pdf") as pdf:
    print(pdf.pages[0].extract_text())
```

### Fichas con campos vacíos

1. Verificar que el PDF tiene la información
2. Revisar extracción de texto
3. Ajustar prompt del LLM
4. Incrementar temperatura si es muy conservador
5. Usar ejemplos más relevantes (mejorar RAG)

---

## Contributing

1. Fork el repo
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m "Add: nueva funcionalidad"`
4. Tests: `pytest`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Abre un Pull Request

---

## Roadmap Técnico

### v0.2.0 (Siguiente)
- [ ] Tests completos (>80% coverage)
- [ ] CI/CD con GitHub Actions
- [ ] Docker compose completo
- [ ] Documentación OpenAPI mejorada

### v0.3.0
- [ ] Batch processing
- [ ] Streaming de respuestas
- [ ] Caché con Redis
- [ ] Métricas con Prometheus

### v0.4.0
- [ ] Fine-tuning de modelo
- [ ] OCR para PDFs escaneados
- [ ] Interfaz web (React/Vue)
- [ ] Autenticación JWT

---

## Referencias Técnicas

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Python](https://python.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [python-docx](https://python-docx.readthedocs.io/)
