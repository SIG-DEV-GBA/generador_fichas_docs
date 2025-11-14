# Generador de Fichas de Ayudas Sociales con IA

> Sistema automatizado de generación de fichas resumidas a partir de documentación legal de ayudas sociales, utilizando Large Language Models (LLMs) y técnicas de RAG.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación Rápida](#instalación-rápida)
- [Uso](#uso)
- [Arquitectura](#arquitectura)
- [Documentación](#documentación)
- [Roadmap](#roadmap)
- [Contribuir](#contribuir)

---

## Descripción del Proyecto

Este proyecto implementa un **microservicio Python** que procesa documentación legal en PDF (convocatorias, normativas, bases reguladoras) y genera automáticamente fichas resumidas en formato Word, siguiendo una estructura estricta y predefinida.

### Problema que Resuelve

- ❌ Proceso **manual** de lectura de documentación legal extensa
- ❌ Tiempo elevado para extraer información clave (horas → minutos)
- ❌ Inconsistencias en el formato de las fichas
- ❌ Dificultad para mantener actualizaciones

### Solución

- ✅ Generación de fichas en **10-20 segundos**
- ✅ Estructura **consistente** y validada automáticamente
- ✅ Sistema RAG para mejorar calidad con ejemplos
- ✅ Escalabilidad para procesar grandes volúmenes

---

## Características

### ✨ Principales

- **Extracción Inteligente**: Parseo avanzado de PDFs legales complejos
- **Generación Estructurada**: Fichas con formato consistente y campos obligatorios
- **Sistema RAG**: Utiliza ejemplos previos para mejorar la calidad
- **Multi-LLM**: Soporta OpenAI (GPT-4o) y Anthropic (Claude 3.5 Sonnet)
- **API REST**: Microservicio escalable con FastAPI
- **Validación Automática**: Verificación de estructura y campos obligatorios

### 📋 Schema de Ficha

Campos incluidos:
- Identificación (nombre, portales, categoría, tipo)
- Fechas (inicio, fin, publicación)
- Administración (ámbito, organismo)
- Requisitos y beneficiarios
- Descripción y cuantía
- Resolución y documentación
- Normativa reguladora
- Lugar de presentación
- Otros datos (usuario, fecha, documentos adjuntos)

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
- **Loguru**: Logging estructurado

---

## Instalación Rápida

### Prerequisitos

```bash
- Python 3.11+
- Git
- API Key de OpenAI o Anthropic
```

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/SIG-DEV-GBA/generador_fichas_docs.git
cd generador_fichas_docs

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key

# 5. Inicializar base de datos vectorial
python scripts/setup_vector_db.py

# 6. Ejecutar servidor
uvicorn app.main:app --reload --port 8000
```

**Acceder a:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

## Uso

### API REST

#### 1. Generar Ficha desde PDF

```bash
curl -X POST "http://localhost:8000/api/v1/generate-ficha" \
  -F "file=@convocatoria.pdf" \
  -F 'config={"include_rag": true, "validate_output": true}'
```

**Respuesta:**
```json
{
  "status": "success",
  "ficha_id": "550e8400-e29b-41d4-a716-446655440000",
  "download_url": "/api/v1/download/550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "processing_time": 12.5,
    "model_used": "claude-3.5-sonnet",
    "rag_enabled": true,
    "rag_examples_used": 3,
    "validation_passed": true
  }
}
```

#### 2. Descargar Ficha Generada

```bash
curl "http://localhost:8000/api/v1/download/550e8400-e29b-41d4-a716-446655440000" \
  -o ficha_generada.docx
```

### Uso con Python

```python
import requests

# Generar ficha
with open("convocatoria.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/generate-ficha",
        files={"file": f},
        data={"config": '{"include_rag": true}'}
    )

# Descargar Word
ficha_id = response.json()["ficha_id"]
word_response = requests.get(
    f"http://localhost:8000/api/v1/download/{ficha_id}"
)

with open("ficha.docx", "wb") as f:
    f.write(word_response.content)

print("✓ Ficha generada: ficha.docx")
```

---

## Arquitectura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    FLUJO DEL SISTEMA                     │
└─────────────────────────────────────────────────────────┘

PDF Input
    ↓
┌───────────────┐
│ PDFExtractor  │ → Texto limpio + Tablas + Metadatos
└───────┬───────┘
        ↓
┌───────────────┐
│  RAG System   │ → Busca 3 ejemplos similares (ChromaDB)
└───────┬───────┘
        ↓
┌───────────────┐
│ LLM Processor │ → Claude/GPT genera FichaData (JSON)
└───────┬───────┘
        ↓
┌───────────────┐
│  Validación   │ → Pydantic valida schema
└───────┬───────┘
        ↓
┌───────────────┐
│ Word Generator│ → Genera .docx formateado
└───────────────┘
```

### Módulos Core

1. **PDFExtractor** (`app/core/pdf_extractor.py`)
   - Extracción de texto con PyMuPDF
   - Análisis de tablas con pdfplumber
   - Detección de boletines oficiales
   - Limpieza y normalización de texto

2. **RAGSystem** (`app/core/rag_system.py`)
   - Base de datos vectorial (ChromaDB)
   - Embeddings con sentence-transformers
   - Búsqueda semántica de ejemplos
   - Construcción de contexto para LLM

3. **LLMProcessor** (`app/core/llm_processor.py`)
   - Orquestación con LangChain
   - Soporta OpenAI y Anthropic
   - Prompts basados en instrucciones JSON
   - Parsing y validación con Pydantic

4. **WordGenerator** (`app/core/word_generator.py`)
   - Generación de .docx con python-docx
   - Estilos profesionales
   - Listas y tablas formateadas

---

## Documentación

### Documentos Disponibles

- **[README.md](README.md)** - Este archivo (visión general)
- **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Guía de inicio rápido (15 min)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura técnica detallada
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Guía de desarrollo y debugging
- **[docs/DATASET.md](docs/DATASET.md)** - Documentación del dataset

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Roadmap

### ✅ v0.1.0 (Actual)
- [x] Arquitectura base
- [x] Core modules (PDF, RAG, LLM, Word)
- [x] API REST básica
- [x] Schema Pydantic completo
- [x] Sistema RAG con ChromaDB
- [x] Documentación inicial

### 🚧 v0.2.0 (En Progreso)
- [ ] Tests completos (>80% coverage)
- [ ] CI/CD con GitHub Actions
- [ ] Docker & Docker Compose
- [ ] Validaciones avanzadas
- [ ] Mejora de prompts
- [ ] Evaluación de calidad automática

### 📋 v0.3.0 (Planificado)
- [ ] Procesamiento en lote (batch)
- [ ] Streaming de respuestas
- [ ] Caché con Redis
- [ ] Métricas con Prometheus
- [ ] Rate limiting avanzado
- [ ] Retry logic con exponential backoff

### 🔮 v0.4.0 (Futuro)
- [ ] Fine-tuning de modelo personalizado
- [ ] OCR para PDFs escaneados
- [ ] Interfaz web (React/Vue)
- [ ] Autenticación JWT
- [ ] Multi-idioma
- [ ] Exportación a múltiples formatos

---

## Dataset

### Estructura

```
Fichas y documentación/
├── [Localidad] ([Provincia]) - [Tipo de Ayuda]/
│   ├── Convocatoria_[nombre].pdf          # Documento legal
│   └── Ficha_[nombre].docx                # Ficha resumida
```

### Estadísticas

- **Total de fichas**: ~25+ ejemplos
- **Ámbitos**: Municipal, Provincial, Autonómico, Nacional
- **Tipos de ayuda**: Emergencia social, Vivienda, Transporte, Energía, Mayores, etc.
- **Comunidades Autónomas**: 9+ representadas

Ver [docs/DATASET.md](docs/DATASET.md) para más detalles.

---

## Configuración

### Variables de Entorno Principales

```env
# LLM Provider (openai | anthropic)
DEFAULT_LLM_PROVIDER=anthropic

# Anthropic (Recomendado)
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o

# RAG System
USE_RAG=True
RAG_TOP_K=3
EMBEDDING_MODEL=all-MiniLM-L6-v2

# App
DEBUG=True
LOG_LEVEL=INFO
PORT=8000
```

Ver [.env.example](.env.example) para configuración completa.

---

## Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_pdf_extraction.py -v
```

---

## Troubleshooting

### Error: "OpenAI API key not found"

```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# O configurar directamente
export OPENAI_API_KEY="sk-..."
```

### Error: "ChromaDB collection not found"

```bash
# Reinicializar base de datos
python scripts/setup_vector_db.py --reindex
```

### Fichas con campos vacíos

1. Verificar extracción del PDF: `python scripts/test_extraction.py tu_pdf.pdf`
2. Revisar logs del LLM (activar `DEBUG=True`)
3. Ajustar temperatura del modelo
4. Usar más ejemplos RAG

Ver [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#troubleshooting) para más soluciones.

---

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Add: nueva funcionalidad'`
4. Tests: `pytest`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Abre un Pull Request

### Guía de Estilo

- Seguir PEP 8
- Usar type hints
- Documentar funciones con docstrings
- Tests para nueva funcionalidad
- Commits descriptivos

---

## Licencia

[Especificar licencia - MIT recomendado]

---

## Contacto

- **GitHub**: [SIG-DEV-GBA/generador_fichas_docs](https://github.com/SIG-DEV-GBA/generador_fichas_docs)
- **Issues**: [GitHub Issues](https://github.com/SIG-DEV-GBA/generador_fichas_docs/issues)

---

## Agradecimientos

- Dataset de ayudas sociales
- Comunidad de LangChain y ChromaDB
- Anthropic por Claude API
- OpenAI por GPT-4 API

---

## Comparativa de Modelos LLM

| Modelo | Costo (1M tokens) | Calidad | Velocidad | Recomendación |
|--------|------------------|---------|-----------|---------------|
| GPT-4o | $5.00 | ⭐⭐⭐⭐⭐ | Rápida | Producción |
| Claude 3.5 Sonnet | $3.00 | ⭐⭐⭐⭐⭐ | Rápida | **Recomendado** |
| GPT-3.5 Turbo | $0.50 | ⭐⭐⭐ | Muy rápida | Desarrollo |

---

## Estado del Proyecto

**Versión Actual**: v0.1.0 (MVP Funcional)

**Status**: 🟢 En desarrollo activo

**Última Actualización**: Noviembre 2025

---

**Hecho con ❤️ para automatizar la generación de fichas de ayudas sociales**
