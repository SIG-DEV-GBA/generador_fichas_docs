# Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el proyecto en menos de 15 minutos.

---

## Prerequisitos

Asegúrate de tener instalado:

- **Python 3.11+** ([Descargar](https://www.python.org/downloads/))
- **Git** ([Descargar](https://git-scm.com/downloads))
- **API Key de OpenAI o Anthropic**
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com/

---

## Instalación (5 minutos)

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/generador-fichas-ia.git
cd generador-fichas-ia/generador_fichas
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias (~500MB, toma 2-3 minutos).

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tu editor favorito
nano .env  # o notepad .env en Windows
```

**Configuración mínima necesaria:**

```env
# Elige UNO de estos dos:

# Opción 1: OpenAI
OPENAI_API_KEY=sk-tu-key-aqui
DEFAULT_LLM_PROVIDER=openai

# Opción 2: Anthropic (Recomendado)
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
DEFAULT_LLM_PROVIDER=anthropic
```

---

## Primera Ejecución (2 minutos)

### 1. Inicializar la base de datos vectorial

```bash
python scripts/setup_vector_db.py
```

Este script:
- Crea la estructura de directorios necesaria
- Inicializa ChromaDB
- Indexa las fichas de ejemplo para RAG

**Salida esperada:**
```
✓ Directorio de ChromaDB creado
✓ Indexando fichas de ejemplo...
✓ 25 fichas indexadas correctamente
✓ Sistema RAG listo
```

### 2. Ejecutar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

**Salida esperada:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Verificar que funciona

Abre tu navegador en: **http://localhost:8000/docs**

Deberías ver la documentación interactiva de la API (Swagger UI).

---

## Primer Test: Generar tu primera ficha

### Opción A: Desde la interfaz web (Swagger)

1. Ve a http://localhost:8000/docs
2. Expande el endpoint `POST /api/v1/generate-ficha`
3. Click en "Try it out"
4. Sube un PDF de prueba (usa uno de `Fichas y documentación/`)
5. Configura:
   ```json
   {
     "include_rag": true,
     "validate_output": true,
     "model": "claude-3.5-sonnet"
   }
   ```
6. Click "Execute"
7. Espera 10-20 segundos
8. Copia el `download_url` y pégalo en el navegador

### Opción B: Desde línea de comandos (curl)

```bash
curl -X POST "http://localhost:8000/api/v1/generate-ficha" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/convocatoria.pdf" \
  -F 'config={"include_rag": true, "validate_output": true}'
```

### Opción C: Desde Python

```python
import requests

url = "http://localhost:8000/api/v1/generate-ficha"

# Abrir el PDF
with open("convocatoria.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "config": {
            "include_rag": True,
            "validate_output": True,
            "model": "claude-3.5-sonnet"
        }
    }

    response = requests.post(url, files=files, json=data)

print(response.json())

# Descargar la ficha generada
if response.ok:
    ficha_id = response.json()["ficha_id"]
    download_url = f"http://localhost:8000/api/v1/download/{ficha_id}"

    ficha = requests.get(download_url)
    with open("ficha_generada.docx", "wb") as f:
        f.write(ficha.content)

    print("✓ Ficha generada: ficha_generada.docx")
```

---

## Estructura de Directorios Después de la Instalación

```
generador_fichas/
├── app/                    # Código fuente (aún vacío, lo crearemos después)
├── data/
│   ├── vector_db/          # ✓ ChromaDB (creado automáticamente)
│   ├── temp/               # ✓ Archivos temporales
│   ├── output/             # ✓ Fichas generadas
│   └── templates/          # Plantillas de Word
├── Fichas y documentación/ # Dataset original
├── docs/                   # Documentación
├── notebooks/              # Para experimentación
├── tests/                  # Tests (lo crearemos después)
├── .env                    # ✓ Tu configuración
└── requirements.txt        # ✓ Dependencias instaladas
```

---

## Verificación del Sistema

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "llm_provider": "anthropic",
  "rag_enabled": true,
  "vector_db": "connected"
}
```

---

## Próximos Pasos

Ahora que tienes el sistema funcionando:

1. **Experimentar con ejemplos**
   - Prueba con diferentes PDFs del dataset
   - Ajusta la configuración (RAG on/off, diferentes modelos)

2. **Entender la arquitectura**
   - Lee [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
   - Explora el código en `app/`

3. **Desarrollar nuevas funcionalidades**
   - Mejora el prompt engineering
   - Añade validaciones personalizadas
   - Optimiza la extracción de PDFs

4. **Evaluación de calidad**
   - Ejecuta `python scripts/evaluate_quality.py`
   - Compara fichas generadas vs ground truth

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"

**Causa**: No estás en el directorio correcto.

**Solución**:
```bash
cd generador_fichas  # Asegúrate de estar aquí
```

### Error: "OpenAI API key not found"

**Causa**: No configuraste las variables de entorno.

**Solución**:
```bash
# Verifica que .env existe y tiene tu API key
cat .env  # Linux/Mac
type .env  # Windows
```

### Error: "ChromaDB connection failed"

**Causa**: La base de datos vectorial no está inicializada.

**Solución**:
```bash
python scripts/setup_vector_db.py
```

### El servidor arranca pero no responde

**Causa**: Puede que esté bloqueado por firewall o el puerto esté ocupado.

**Solución**:
```bash
# Probar otro puerto
uvicorn app.main:app --reload --port 8080

# O verificar qué está usando el puerto 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac
```

### PDFs muy grandes fallan

**Causa**: Timeout o límite de tamaño.

**Solución**: Ajusta en `.env`:
```env
MAX_PDF_SIZE_MB=20
PROCESSING_TIMEOUT=120
```

### Fichas con campos vacíos

**Causa**: El PDF puede tener formato complejo o el prompt necesita ajuste.

**Solución**:
1. Verifica la extracción: `python scripts/test_extraction.py tu_pdf.pdf`
2. Ajusta el prompt en `app/core/llm_processor.py`
3. Activa RAG para mejores ejemplos

---

## Comandos Útiles

### Desarrollo

```bash
# Ejecutar con hot-reload
uvicorn app.main:app --reload

# Ejecutar tests
pytest

# Formatear código
black app/
ruff check app/

# Ver logs detallados
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

### Producción

```bash
# Ejecutar con Gunicorn (múltiples workers)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Con Docker
docker-compose up -d
```

---

## Recursos Adicionales

- **Documentación completa**: [README.md](../README.md)
- **Arquitectura técnica**: [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Reference**: http://localhost:8000/redoc
- **Issues**: https://github.com/tu-usuario/generador-fichas-ia/issues

---

## Obtener Ayuda

Si tienes problemas:

1. **Revisa los logs**: Siempre hay información útil en la consola
2. **Verifica la configuración**: `.env` debe estar correctamente configurado
3. **Consulta los tests**: Los tests unitarios son ejemplos funcionales
4. **Abre un issue**: En GitHub con el error completo

---

¡Listo! Ya estás preparado para empezar a desarrollar. 🚀
