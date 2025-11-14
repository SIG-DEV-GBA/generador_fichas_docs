# Generador de Fichas de Ayudas Sociales con IA

> Sistema automatizado de generación de fichas resumidas a partir de documentación legal de ayudas sociales, utilizando Large Language Models (LLMs) y técnicas de RAG.

## Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Problema que Resuelve](#problema-que-resuelve)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Dataset](#dataset)
- [Roadmap](#roadmap)
- [Contribuir](#contribuir)

---

## Descripción del Proyecto

Este proyecto implementa un **microservicio Python** que procesa documentación legal en PDF (convocatorias, normativas, bases reguladoras) y genera automáticamente fichas resumidas en formato Word, siguiendo una estructura estricta y predefinida.

### Características Principales

- **Extracción Inteligente**: Parseo avanzado de PDFs legales complejos
- **Generación Estructurada**: Fichas con formato consistente y campos obligatorios
- **Sistema RAG**: Utiliza ejemplos previos para mejorar la calidad de las fichas
- **API REST**: Microservicio escalable con FastAPI
- **Validación Automática**: Verificación de estructura y campos obligatorios

---

## Problema que Resuelve

### Situación Actual
- Proceso **manual** de lectura de documentación legal extensa
- Tiempo elevado para extraer información clave
- Inconsistencias en el formato de las fichas
- Dificultad para mantener actualizaciones

### Solución Propuesta
- Automatización del proceso de análisis documental
- Generación de fichas en **segundos** vs horas
- Estructura **consistente** y validada
- Escalabilidad para procesar grandes volúmenes

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      FLUJO DEL SISTEMA                       │
└─────────────────────────────────────────────────────────────┘

PDF Legal Input
      ↓
┌─────────────────┐
│ 1. EXTRACCIÓN   │ → pymupdf / pdfplumber
│    - Texto      │
│    - Tablas     │
│    - Metadata   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. RAG SYSTEM   │ → ChromaDB / Pinecone
│    - Búsqueda   │
│    - Ejemplos   │
│    - Contexto   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. LLM ENGINE   │ → LangChain + Claude 3.5 / GPT-4
│    - Análisis   │
│    - Extracción │
│    - Resumen    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. VALIDACIÓN   │ → Pydantic Schemas
│    - Estructura │
│    - Campos     │
│    - Tipos      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. GENERACIÓN   │ → python-docx
│    Word Output  │
└─────────────────┘
```

---

## Tecnologías

### Backend Core
- **Python 3.11+**
- **FastAPI**: Framework web asíncrono
- **Uvicorn**: Servidor ASGI

### Procesamiento de Documentos
- **pymupdf (PyMuPDF)**: Extracción de PDFs
- **pdfplumber**: Análisis de tablas y estructura
- **python-docx**: Generación de documentos Word

### IA y Machine Learning
- **LangChain**: Orquestación de LLMs
- **OpenAI API / Anthropic Claude**: Modelos de lenguaje
- **ChromaDB**: Base de datos vectorial para RAG
- **sentence-transformers**: Embeddings para búsqueda semántica

### Validación y Datos
- **Pydantic**: Validación de esquemas
- **pandas**: Manipulación de datos estructurados

### DevOps
- **Docker**: Containerización
- **pytest**: Testing
- **black/ruff**: Formateo y linting

---

## Estructura del Proyecto

```
generador_fichas/
│
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias Python
├── .env.example                       # Variables de entorno (plantilla)
├── .gitignore
│
├── app/                               # Aplicación principal
│   ├── __init__.py
│   ├── main.py                        # Punto de entrada FastAPI
│   ├── config.py                      # Configuración global
│   │
│   ├── api/                           # Endpoints REST
│   │   ├── __init__.py
│   │   ├── routes.py                  # Rutas principales
│   │   └── dependencies.py
│   │
│   ├── core/                          # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py          # Extracción de PDFs
│   │   ├── llm_processor.py          # Procesamiento con LLM
│   │   ├── rag_system.py             # Sistema RAG
│   │   └── word_generator.py         # Generación de Word
│   │
│   ├── models/                        # Modelos de datos
│   │   ├── __init__.py
│   │   ├── ficha_schema.py           # Schema de ficha
│   │   └── request_models.py         # Modelos de request/response
│   │
│   └── utils/                         # Utilidades
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── data/                              # Datos del proyecto
│   ├── vector_db/                     # Base de datos vectorial
│   ├── templates/                     # Plantillas de fichas
│   └── examples/                      # Fichas de ejemplo para RAG
│
├── Fichas y documentación/            # Dataset original
│   ├── [Nombre Ayuda]/
│   │   ├── convocatoria.pdf
│   │   └── ficha.docx
│   └── ...
│
├── notebooks/                         # Jupyter notebooks para experimentación
│   ├── 01_exploracion_dataset.ipynb
│   ├── 02_prompt_engineering.ipynb
│   └── 03_evaluacion_modelo.ipynb
│
├── tests/                             # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_pdf_extraction.py
│   ├── test_llm_processing.py
│   └── test_word_generation.py
│
├── scripts/                           # Scripts de utilidad
│   ├── setup_vector_db.py            # Inicializar ChromaDB con ejemplos
│   ├── evaluate_quality.py           # Evaluar calidad de fichas
│   └── batch_process.py              # Procesamiento en lote
│
└── docker/                            # Configuración Docker
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Dataset

El proyecto utiliza un dataset estructurado de ayudas sociales españolas:

### Estructura de Carpetas
```
Fichas y documentación/
├── [Municipio/CCAA] - [Tipo de Ayuda]/
│   ├── Convocatoria_[nombre].pdf          # Documento legal original
│   └── Ficha_[nombre].docx                # Ficha resumida (ground truth)
```

### Ejemplos Incluidos
- Ayudas de emergencia social
- Ayudas para mayores y dependencia
- Ayudas por inundaciones (DANA)
- Subvenciones de rehabilitación
- Bonos de transporte
- Pobreza energética
- Y más...

### Estadísticas del Dataset
- **Total de fichas**: ~25+ ejemplos (dataset parcial)
- **Ámbitos geográficos**: Municipal, Provincial, Autonómico, Nacional
- **Tipos de ayuda**: Emergencia social, Vivienda, Transporte, Energía, Mayores, etc.

---

## Instalación

### Prerequisitos
```bash
- Python 3.11+
- pip / poetry
- Git
```

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/generador-fichas-ia.git
cd generador-fichas-ia/generador_fichas
```

### Paso 2: Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus API keys
```

Contenido de `.env`:
```env
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector DB
CHROMA_PERSIST_DIRECTORY=./data/vector_db

# App Config
DEBUG=True
LOG_LEVEL=INFO
```

### Paso 5: Inicializar base de datos vectorial
```bash
python scripts/setup_vector_db.py
```

### Paso 6: Ejecutar servidor
```bash
uvicorn app.main:app --reload --port 8000
```

Acceder a: `http://localhost:8000/docs`

---

## Uso

### API REST

#### Endpoint: Generar Ficha
```http
POST /api/v1/generate-ficha
Content-Type: multipart/form-data

Body:
- file: [archivo.pdf]
- config: {
    "include_rag": true,
    "validate_output": true,
    "model": "claude-3.5-sonnet"
  }
```

**Respuesta:**
```json
{
  "status": "success",
  "ficha_id": "uuid-123",
  "download_url": "/api/v1/download/uuid-123",
  "metadata": {
    "processing_time": 12.5,
    "confidence_score": 0.92,
    "model_used": "claude-3.5-sonnet"
  }
}
```

#### Endpoint: Descargar Ficha
```http
GET /api/v1/download/{ficha_id}
```

Devuelve el archivo `.docx` generado.

### Uso con Python SDK (Futuro)
```python
from generador_fichas import FichaGenerator

generator = FichaGenerator(api_key="your-key")

# Generar ficha desde PDF
ficha = generator.generate_from_pdf("convocatoria.pdf")

# Guardar resultado
ficha.save("ficha_generada.docx")

# Acceder a datos estructurados
print(ficha.data.titulo)
print(ficha.data.beneficiarios)
```

---

## Roadmap

### Fase 1: MVP (En Progreso) ✅
- [x] Definición de arquitectura
- [x] Setup inicial del proyecto
- [ ] Extracción básica de PDFs
- [ ] Prompt engineering inicial
- [ ] Generación de Word básica
- [ ] API REST mínima

### Fase 2: Sistema RAG
- [ ] Vectorización del dataset
- [ ] Búsqueda semántica de ejemplos
- [ ] Integración con LangChain
- [ ] Mejora de prompts con few-shot learning

### Fase 3: Optimización
- [ ] Caché de respuestas
- [ ] Procesamiento por lotes
- [ ] Métricas de calidad automáticas
- [ ] Dashboard de monitoreo

### Fase 4: Producción
- [ ] Dockerización completa
- [ ] CI/CD pipeline
- [ ] Documentación API completa
- [ ] Tests de integración
- [ ] Deploy en cloud

### Futuro
- [ ] Fine-tuning de modelo personalizado
- [ ] Interfaz web (frontend)
- [ ] Multi-idioma
- [ ] Exportación a múltiples formatos

---

## Esquema de Ficha

### Campos Principales
```yaml
Ficha de Ayuda Social:
  - Título: str
  - Organismo: str
  - Ámbito Geográfico: str (Municipal/Provincial/Autonómico/Nacional)
  - Tipo de Ayuda: str
  - Objeto: str (descripción breve)
  - Beneficiarios: str
  - Requisitos: list[str]
  - Cuantía: str
  - Plazo de Solicitud: str
  - Documentación Requerida: list[str]
  - Lugar de Presentación: str
  - Normativa: str
  - Contacto: dict
  - Observaciones: str (opcional)
```

---

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guía de Estilo
- Seguir PEP 8
- Usar type hints
- Documentar funciones con docstrings
- Tests para nueva funcionalidad

---

## Licencia

[Especificar licencia - MIT, Apache 2.0, etc.]

---

## Contacto

- **Proyecto**: [GitHub Repo](https://github.com/tu-usuario/generador-fichas-ia)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/generador-fichas-ia/issues)

---

## Agradecimientos

- Dataset de ayudas sociales proporcionado por [fuente]
- Inspirado en proyectos de NLP y document intelligence
- Comunidad de LangChain y ChromaDB

---

**Nota**: Este es un proyecto en desarrollo activo. La estructura y funcionalidades pueden cambiar.

---

## Anexos

### Comparativa de Modelos LLM

| Modelo | Costo (1M tokens) | Calidad | Velocidad | Recomendación |
|--------|------------------|---------|-----------|---------------|
| GPT-4o | $5.00 | ⭐⭐⭐⭐⭐ | Rápida | Producción |
| Claude 3.5 Sonnet | $3.00 | ⭐⭐⭐⭐⭐ | Rápida | **Recomendado** |
| GPT-3.5 Turbo | $0.50 | ⭐⭐⭐ | Muy rápida | Desarrollo |
| LLaMA 3.1 (local) | Gratis | ⭐⭐⭐⭐ | Media | Experimentación |

### Recursos Útiles

- [Documentación LangChain](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [python-docx Tutorial](https://python-docx.readthedocs.io/)
