# Documentación del Dataset

## Descripción General

El dataset contiene ejemplos reales de **documentación legal de ayudas sociales** en España, junto con sus correspondientes **fichas resumidas**. Este dataset sirve como:

1. **Ground truth** para evaluar la calidad de las fichas generadas
2. **Ejemplos para RAG** (Retrieval Augmented Generation)
3. **Datos de entrenamiento** (si se decide hacer fine-tuning)

---

## Estructura

### Organización de Carpetas

```
Fichas y documentación/
├── [Localidad] ([Provincia]) - [Tipo de Ayuda]/
│   ├── Convocatoria_[nombre].pdf          # Documento legal original
│   ├── [otros_pdfs_relacionados].pdf      # Bases, anexos, formularios
│   └── Ficha_[nombre].docx                # Ficha resumida (ground truth)
```

### Convenciones de Nomenclatura

**Formato de carpetas:**
- `Municipio (Provincia) - Descripción Ayuda`
- Ejemplo: `Badajoz (Badajoz) - Ayudas ante Emergencia o Urgencia Social`

**Formato de PDFs:**
- `Convocatoria [nombre].pdf`
- `Bases [nombre].pdf`
- `Resolución [nombre].pdf`

**Formato de fichas Word:**
- `Ficha [Localidad] ([Provincia]) - [Tipo Ayuda].docx`
- Ejemplo: `Ficha Badajoz (Badajoz) - Ayudas ante Emergencia Social.docx`

---

## Estadísticas del Dataset

### Cobertura Geográfica

| Ámbito | Cantidad | Porcentaje |
|--------|----------|------------|
| Municipal | ~18 | 72% |
| Provincial | ~2 | 8% |
| Autonómico | ~4 | 16% |
| Nacional | ~1 | 4% |

**Comunidades Autónomas representadas:**
- Andalucía (Málaga, Badajoz, Cáceres)
- País Vasco (Vizcaya, Gipuzkoa, Álava)
- Comunidad Valenciana (Valencia, Alicante)
- Cataluña (Barcelona)
- Castilla y León (Burgos, Zamora)
- Asturias
- Aragón
- Extremadura
- Ceuta y Melilla

### Tipos de Ayudas

| Categoría | Ejemplos | Cantidad |
|-----------|----------|----------|
| **Emergencia Social** | Ayudas urgentes, contingencias | ~8 |
| **Vivienda** | Inundaciones DANA, rehabilitación | ~3 |
| **Mayores y Dependencia** | Residencias, respiro familiar | ~4 |
| **Transporte** | Bonos taxi, Auzo Taxi | ~2 |
| **Pobreza Energética** | Ayudas energía | ~3 |
| **Otras** | Acogimiento familiar, subvenciones | ~5 |

### Características de los Documentos

**PDFs:**
- Tamaño: 100 KB - 5 MB (promedio: ~500 KB)
- Páginas: 2 - 50 (promedio: ~10 páginas)
- Formato: Texto nativo (no escaneado, en su mayoría)
- Idiomas: Español (algunos con euskera en País Vasco)
- Complejidad: Lenguaje legal/administrativo

**Fichas Word:**
- Tamaño: 15 KB - 30 KB
- Páginas: 1-3 (promedio: 2 páginas)
- Formato: Estructurado con secciones claras
- Estilo: Lenguaje simplificado y accesible

---

## Ejemplos Detallados

### Ejemplo 1: Ayuda de Emergencia Social

**Carpeta:** `Arrigorriaga (Vizcaya) - Emergencia Social/`

**Archivos:**
- `Convocatoria Arrigorriaga Emergencia Social.pdf` (194 KB)
- `Ficha Arrigorriaga (Vizcaya) Ayuda Emergencia Social.docx` (21 KB)

**Contenido del PDF:**
- Bases reguladoras de la ayuda
- Requisitos de solicitantes
- Documentación necesaria
- Procedimiento de solicitud
- Criterios de valoración

**Estructura de la Ficha:**
```
TÍTULO: Ayuda de Emergencia Social
ORGANISMO: Ayuntamiento de Arrigorriaga
ÁMBITO: Municipal (Vizcaya, País Vasco)
TIPO: Emergencia Social

OBJETO:
Atención de situaciones de urgencia o emergencia social...

BENEFICIARIOS:
Personas o unidades de convivencia empadronadas...

REQUISITOS:
- Estar empadronado en Arrigorriaga
- Situación de necesidad acreditada
- No disponer de recursos económicos suficientes
...

CUANTÍA:
Hasta 600€ por solicitud...

PLAZO:
Durante todo el año...

DOCUMENTACIÓN:
- DNI/NIE
- Certificado de empadronamiento
- Informe de servicios sociales
...

PRESENTACIÓN:
Sede electrónica del Ayuntamiento...

NORMATIVA:
Bases reguladoras publicadas en...

CONTACTO:
Teléfono: 944 020 700
Email: info@arrigorriaga.eus
```

---

### Ejemplo 2: Ayudas por Inundación DANA

**Carpeta:** `Benetússer (Valencia) - Ayudas Inundación DANA/`

**Características especiales:**
- **Contexto temporal**: Ayuda de emergencia por desastre natural
- **Urgencia**: Plazos muy cortos
- **Documentación simplificada**: Menos requisitos por la situación

**Ficha:**
```
TÍTULO: Ayudas Urgentes por Inundaciones DANA
ORGANISMO: Ayuntamiento de Benetússer
ÁMBITO: Municipal (Valencia)
TIPO: Emergencia por Desastre Natural

OBJETO:
Ayudas económicas directas para paliar los daños causados por las inundaciones...

BENEFICIARIOS:
Personas físicas y familias afectadas por las inundaciones...

REQUISITOS:
- Residir en zona afectada
- Acreditar daños materiales
- No tener seguro que cubra los daños

CUANTÍA:
Hasta 3.000€ según valoración de daños

PLAZO:
15 días desde publicación (plazo ampliado por emergencia)

DOCUMENTACIÓN:
- DNI
- Fotografías de los daños
- Informe técnico municipal
- Declaración responsable

...
```

---

### Ejemplo 3: Ayudas para Mayores (Ámbito Nacional)

**Carpeta:** `ayuda mayores, discapacidad dependencia Ceuta y Melilla 2025/`

**Archivos:**
- `Resolución Imserso Convocatoria Ceuta y Melilla 2025.pdf`
- `Solicitud entidades y ONG ayuda Ceuta y Melilla 2025.pdf`
- `Ficha subvención para personas mayores [...].docx`

**Características especiales:**
- **Ámbito nacional**: Convocatoria del IMSERSO
- **Beneficiario indirecto**: Ayuda a entidades que atienden mayores
- **Documentación compleja**: Requisitos de entidades sin ánimo de lucro

---

## Campos Comunes en las Fichas

### Obligatorios

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Título** | Nombre oficial de la ayuda | "Ayudas de Emergencia Social" |
| **Organismo** | Entidad convocante | "Ayuntamiento de Madrid" |
| **Ámbito** | Nivel territorial | "Municipal", "Autonómico", etc. |
| **Tipo de Ayuda** | Categoría | "Emergencia Social", "Vivienda" |
| **Objeto** | Finalidad de la ayuda | "Atender situaciones de urgencia..." |
| **Beneficiarios** | Quién puede solicitarla | "Personas empadronadas en..." |
| **Requisitos** | Condiciones para acceder | Lista de requisitos |
| **Cuantía** | Importe de la ayuda | "Hasta 600€" o "Variable según..." |
| **Plazo de Solicitud** | Cuándo se puede pedir | "Del 1 al 31 de enero de 2025" |
| **Documentación** | Qué presentar | Lista de documentos |
| **Lugar de Presentación** | Dónde solicitar | "Sede electrónica", "Oficina de..." |
| **Normativa** | Base legal | "BOP nº 123 de 01/01/2025" |

### Opcionales

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Contacto** | Teléfono, email, web | Tel: 900 123 456 |
| **Forma de Presentación** | Presencial, telemática, correo | "Sede electrónica preferente" |
| **Observaciones** | Notas adicionales | "Compatible con otras ayudas" |
| **Plazo de Resolución** | Cuánto tarda la resolución | "3 meses máximo" |
| **Recursos** | Cómo reclamar | "Recurso de reposición en 1 mes" |

---

## Variabilidad y Desafíos

### Inconsistencias en PDFs

1. **Formato**
   - Algunos PDFs tienen columnas múltiples
   - Tablas con formatos variados
   - Headers/footers que interrumpen el texto

2. **Lenguaje**
   - Terminología legal variable
   - Abreviaturas no estándar
   - Referencias cruzadas a otras normativas

3. **Estructura**
   - No todos siguen el mismo orden
   - Algunos combinan varios tipos de ayudas
   - Anexos separados en PDFs distintos

### Retos de Extracción

**Caso complejo:** Tablas de cuantías

```
| Situación                  | Cuantía Máxima |
|----------------------------|----------------|
| Emergencia familiar        | 600€           |
| Gastos vivienda urgente    | 1.200€         |
| Suministros básicos        | 300€           |
```

**Desafío:** Extraer estas tablas y convertirlas a texto legible para el LLM.

**Solución:** Usar `pdfplumber` para detectar tablas y convertirlas a formato markdown.

---

## Uso del Dataset

### 1. Para Desarrollo

```python
# scripts/explore_dataset.py
import os
from pathlib import Path

dataset_path = Path("Fichas y documentación")

for folder in dataset_path.iterdir():
    if folder.is_dir():
        pdfs = list(folder.glob("*.pdf"))
        docxs = list(folder.glob("*.docx"))

        print(f"\n{folder.name}:")
        print(f"  PDFs: {len(pdfs)}")
        print(f"  Fichas: {len(docxs)}")

        # Analizar contenido
        for pdf in pdfs:
            print(f"    - {pdf.name} ({pdf.stat().st_size / 1024:.1f} KB)")
```

### 2. Para Indexación en RAG

```python
# scripts/setup_vector_db.py
from app.core.rag_system import RAGSystem

rag = RAGSystem()

# Indexar todas las fichas Word
for ficha_path in Path("Fichas y documentación").rglob("*.docx"):
    if "Ficha" in ficha_path.name:
        rag.index_ficha(ficha_path)

print(f"✓ {rag.count()} fichas indexadas")
```

### 3. Para Evaluación

```python
# scripts/evaluate_quality.py
from app.core.llm_processor import LLMProcessor
from app.utils.metrics import calculate_similarity

processor = LLMProcessor()

for folder in dataset_folders:
    # Generar ficha desde PDF
    pdf_path = folder / "Convocatoria*.pdf"
    generated = processor.generate_ficha(pdf_path)

    # Comparar con ground truth
    ground_truth = folder / "Ficha*.docx"
    similarity = calculate_similarity(generated, ground_truth)

    print(f"{folder.name}: {similarity:.2%}")
```

---

## Expansión del Dataset

### Cómo Añadir Nuevos Ejemplos

1. **Crear carpeta** siguiendo el formato:
   ```
   [Localidad] ([Provincia]) - [Tipo Ayuda]/
   ```

2. **Añadir PDFs**:
   - Convocatoria oficial
   - Bases reguladoras
   - Formularios (opcional)

3. **Crear ficha Word**:
   - Seguir la estructura de campos obligatorios
   - Usar lenguaje claro y conciso
   - Validar con el schema de `FichaData`

4. **Re-indexar**:
   ```bash
   python scripts/setup_vector_db.py --reindex
   ```

---

## Licencia y Uso

**Fuente:** Documentación pública de ayuntamientos, BOPs, BOEs.

**Uso permitido:**
- Desarrollo y entrenamiento de modelos
- Investigación académica
- Fines educativos

**Restricciones:**
- Verificar siempre la vigencia de las convocatorias
- No usar para asesoramiento legal directo sin revisión humana

---

## Metadatos Recomendados

Para cada ejemplo, es útil mantener metadatos:

```json
{
  "id": "arrigorriaga-emergencia-2024",
  "localidad": "Arrigorriaga",
  "provincia": "Vizcaya",
  "ccaa": "País Vasco",
  "tipo_ayuda": "Emergencia Social",
  "anio": 2024,
  "ambito": "municipal",
  "pdf_size_kb": 194,
  "pdf_pages": 8,
  "extraction_quality": "high",
  "indexed_at": "2025-01-15T10:00:00Z"
}
```

---

## Referencias

- **BOPs**: Boletines Oficiales de las Provincias
- **BOEs**: Boletín Oficial del Estado
- **Sedes Electrónicas**: Portales de ayuntamientos y CCAA
- **IMSERSO**: Instituto de Mayores y Servicios Sociales

---

Este dataset es la piedra angular del proyecto. Su calidad y diversidad determinarán el éxito del sistema de generación automatizada de fichas.
