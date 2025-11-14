# 💰 Cómo se Calculan los Costos de Tokens en LLMs

## Índice
1. [¿Qué es un Token?](#qué-es-un-token)
2. [Precios de los Modelos](#precios-de-los-modelos)
3. [Fórmula de Cálculo](#fórmula-de-cálculo)
4. [Ejemplos Prácticos](#ejemplos-prácticos)
5. [Estimación de Tokens](#estimación-de-tokens)
6. [Calculadora Paso a Paso](#calculadora-paso-a-paso)
7. [Trucos para Optimizar Costos](#trucos-para-optimizar-costos)

---

## 🔤 ¿Qué es un Token?

Un **token** es la unidad básica de procesamiento de texto para un LLM.

### Reglas Generales de Tokenización:

```
1 token ≈ 4 caracteres en inglés
1 token ≈ 0.75 palabras en inglés
1 token ≈ 3-3.5 caracteres en español (más largo)

Ejemplos:
├─ "Hola" = 1 token
├─ "ayuda social" = 2 tokens
├─ "¿Cómo estás?" = 4 tokens
├─ "administración" = 3 tokens
└─ "https://boe.es/diario_boe/txt.php?id=BOE-A-2023-12345" = 25 tokens (URLs son caras)
```

### Caracteres Especiales y Números:

```
├─ Números: "2024" = 1 token, "€1,234.56" = 5 tokens
├─ Puntuación: "." = 1 token, "..." = 1 token
├─ Espacios: incluidos en tokens adyacentes
└─ Saltos de línea: "\n" = 1 token
```

### Herramientas para Contar Tokens:

1. **OpenAI Tokenizer** (online): https://platform.openai.com/tokenizer
2. **tiktoken** (Python):
   ```python
   import tiktoken

   encoding = tiktoken.encoding_for_model("gpt-4o")
   text = "Tu texto aquí"
   tokens = encoding.encode(text)
   num_tokens = len(tokens)
   print(f"Tokens: {num_tokens}")
   ```

3. **Anthropic Console** (online): https://console.anthropic.com/

---

## 💵 Precios de los Modelos

Los modelos LLM cobran por **millón de tokens** procesados, separando **INPUT** (lo que envías) y **OUTPUT** (lo que genera).

### Tabla de Precios (Noviembre 2024)

| Modelo | Input ($/1M tokens) | Output ($/1M tokens) | Proveedor |
|--------|---------------------|----------------------|-----------|
| **GPT-4o** | $2.50 | $10.00 | OpenAI |
| **GPT-4o mini** | $0.15 | $0.60 | OpenAI |
| **GPT-3.5 Turbo** | $0.50 | $1.50 | OpenAI |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | Anthropic |
| **Claude 3 Haiku** | $0.25 | $1.25 | Anthropic |
| **Llama 3.1 70B (Groq)** | GRATIS* | GRATIS* | Groq |

*Groq tier gratuito tiene límites: 30 req/min, 6,000 tokens/min, 14,400 req/día

### ¿Por qué el Output es más caro?

```
INPUT (más barato):
├─ Solo se procesa/lee
├─ Menos computación
└─ Ejemplo: $2.50/M

OUTPUT (más caro):
├─ Se genera token por token
├─ Requiere sampling, beam search, etc.
├─ Más intensivo computacionalmente
└─ Ejemplo: $10.00/M (4x más caro)

CONCLUSIÓN: Minimizar output ahorra más que minimizar input
```

---

## 📐 Fórmula de Cálculo

### Fórmula Básica

```
Costo Total = (Tokens Input × Precio Input) + (Tokens Output × Precio Output)

Donde:
├─ Tokens Input: prompt + contexto + documentos enviados
├─ Tokens Output: respuesta generada por el LLM
├─ Precio Input: $/1M tokens (ver tabla arriba)
└─ Precio Output: $/1M tokens (ver tabla arriba)
```

### Fórmula Detallada

```
Costo = (Tokens_Input / 1,000,000 × Precio_Input_por_M) +
        (Tokens_Output / 1,000,000 × Precio_Output_por_M)
```

### Simplificado (para cantidades pequeñas)

```
Costo_Input  = Tokens_Input  × (Precio_Input  / 1,000,000)
Costo_Output = Tokens_Output × (Precio_Output / 1,000,000)

Costo_Total = Costo_Input + Costo_Output
```

---

## 🧮 Ejemplos Prácticos

### Ejemplo 1: Ficha Simple con GPT-4o mini

**Contexto:**
- PDF corto: "Ayuda para transporte de personas mayores de 65 años..."
- Tokens Input: 15,000 tokens (PDF + prompt + ejemplos RAG)
- Tokens Output: 2,000 tokens (ficha generada en JSON)

**Precios GPT-4o mini:**
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**Cálculo:**

```
Costo Input  = 15,000 tokens × ($0.15 / 1,000,000)
             = 15,000 × 0.00000015
             = $0.00225

Costo Output = 2,000 tokens × ($0.60 / 1,000,000)
             = 2,000 × 0.0000006
             = $0.0012

Costo Total  = $0.00225 + $0.0012
             = $0.00345
             ≈ $0.005 por ficha
```

**Resultado:** Menos de medio centavo por ficha simple.

---

### Ejemplo 2: Ficha Compleja con Claude 3.5 Sonnet

**Contexto:**
- 3 PDFs: Boletín Oficial + Bases Reguladoras + Anexo
- Tokens Input: 70,000 tokens
- Tokens Output: 2,500 tokens

**Precios Claude 3.5 Sonnet:**
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens

**Cálculo:**

```
Costo Input  = 70,000 × ($3.00 / 1,000,000)
             = 70,000 × 0.000003
             = $0.21

Costo Output = 2,500 × ($15.00 / 1,000,000)
             = 2,500 × 0.000015
             = $0.0375

Costo Total  = $0.21 + $0.0375
             = $0.2475
             ≈ $0.25 por ficha compleja
```

**Resultado:** 25 centavos por ficha compleja (casos difíciles).

---

### Ejemplo 3: Modelo Híbrido (250 fichas/mes)

**Distribución:**
- 100 fichas simples (GPT-4o mini)
- 100 fichas medianas (GPT-4o)
- 50 fichas complejas (Claude 3.5 Sonnet)

**Cálculo por tipo:**

#### Fichas Simples (GPT-4o mini)
```
Input:  15,000 tokens × $0.15/M = $0.00225
Output:  2,000 tokens × $0.60/M = $0.0012
─────────────────────────────────────────
Subtotal: $0.00345 × 100 fichas = $0.345
```

#### Fichas Medianas (GPT-4o)
```
Input:  35,000 tokens × $2.50/M = $0.0875
Output:  2,000 tokens × $10.00/M = $0.02
─────────────────────────────────────────
Subtotal: $0.1075 × 100 fichas = $10.75
```

#### Fichas Complejas (Claude 3.5)
```
Input:  70,000 tokens × $3.00/M = $0.21
Output:  2,500 tokens × $15.00/M = $0.0375
─────────────────────────────────────────
Subtotal: $0.2475 × 50 fichas = $12.375
```

**Total Mensual:**
```
$0.345 + $10.75 + $12.375 = $23.47/mes
```

---

## 📊 Estimación de Tokens

### Método 1: Regla del Pulgar

```python
def estimate_tokens(text: str, language: str = "es") -> int:
    """Estimación rápida de tokens"""

    if language == "es":
        # Español: ~3.5 caracteres por token
        return len(text) // 3.5
    else:
        # Inglés: ~4 caracteres por token
        return len(text) // 4
```

**Ejemplo:**
```
Texto: "Ayuda para familias con menores a cargo en situación de vulnerabilidad"
Caracteres: 73
Tokens estimados: 73 / 3.5 ≈ 21 tokens
```

### Método 2: Por Palabras

```python
def estimate_tokens_by_words(text: str, language: str = "es") -> int:
    """Estimación por palabras"""

    words = len(text.split())

    if language == "es":
        # Español: ~1.3 tokens por palabra
        return int(words * 1.3)
    else:
        # Inglés: ~1.3 tokens por palabra
        return int(words * 1.3)
```

**Ejemplo:**
```
Texto: "Ayuda para familias con menores a cargo en situación de vulnerabilidad"
Palabras: 11
Tokens estimados: 11 × 1.3 ≈ 14 tokens
```

### Método 3: Por Páginas (PDFs)

```python
def estimate_pdf_tokens(num_pages: int, pages_type: str = "legal") -> int:
    """Estimación de tokens en PDFs"""

    tokens_per_page = {
        "legal": 800,      # Boletines oficiales (densos)
        "normal": 600,     # Documentos normales
        "scan": 400,       # PDFs escaneados (menos texto)
    }

    return num_pages * tokens_per_page.get(pages_type, 600)
```

**Ejemplo:**
```
PDF: Boletín Oficial de 25 páginas
Tokens estimados: 25 × 800 = 20,000 tokens
```

### Método 4: Tiktoken (Preciso)

```python
import tiktoken

def count_tokens_precise(text: str, model: str = "gpt-4o") -> int:
    """Conteo exacto de tokens"""

    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)
```

**Ejemplo:**
```python
text = "Ayuda para familias con menores a cargo en situación de vulnerabilidad"
tokens = count_tokens_precise(text, "gpt-4o")
print(tokens)  # Output: 19 tokens (preciso)
```

---

## 🧮 Calculadora Paso a Paso

### Caso Real: Tu Proyecto

**Datos de entrada:**
- PDF 1: Boletín Oficial (20 páginas × 800 tokens/página = 16,000 tokens)
- PDF 2: Bases Reguladoras (15 páginas × 800 tokens/página = 12,000 tokens)
- Prompt del sistema: 5,000 tokens (instrucciones + schema)
- Ejemplos RAG: 3 fichas × 2,000 tokens = 6,000 tokens
- Output esperado: 2,500 tokens (ficha generada)

**TOTAL INPUT:**
```
16,000 (PDF1) + 12,000 (PDF2) + 5,000 (Prompt) + 6,000 (RAG) = 39,000 tokens
```

**TOTAL OUTPUT:**
```
2,500 tokens (ficha JSON generada)
```

### Opción 1: GPT-4o

**Precios:**
- Input: $2.50 / 1M
- Output: $10.00 / 1M

**Cálculo:**
```
Input:  39,000 × ($2.50 / 1,000,000) = $0.0975
Output:  2,500 × ($10.00 / 1,000,000) = $0.025
───────────────────────────────────────────────
TOTAL: $0.1225 ≈ $0.12 por ficha
```

**250 fichas/mes:** $0.12 × 250 = **$30.00/mes**

### Opción 2: Claude 3.5 Sonnet

**Precios:**
- Input: $3.00 / 1M
- Output: $15.00 / 1M

**Cálculo:**
```
Input:  39,000 × ($3.00 / 1,000,000) = $0.117
Output:  2,500 × ($15.00 / 1,000,000) = $0.0375
───────────────────────────────────────────────
TOTAL: $0.1545 ≈ $0.15 por ficha
```

**250 fichas/mes:** $0.15 × 250 = **$37.50/mes**

### Comparativa:

| Modelo | Costo/Ficha | 250 fichas/mes | Diferencia |
|--------|-------------|----------------|------------|
| GPT-4o | $0.12 | $30.00 | Base |
| Claude 3.5 | $0.15 | $37.50 | +25% |
| GPT-4o mini | $0.005 | $1.25 | -96% |

---

## 📈 Desglose Visual del Costo

### Anatomía del Costo por Ficha

```
┌─────────────────────────────────────────────────────────────┐
│           COSTO TOTAL: $0.15 (Claude 3.5 Sonnet)            │
└─────────────────────────────────────────────────────────────┘

INPUT ($0.117 - 78% del costo total)
├─ PDF 1 (16,000 tokens):           $0.048  (32%)
├─ PDF 2 (12,000 tokens):           $0.036  (24%)
├─ Prompt sistema (5,000 tokens):   $0.015  (10%)
└─ Ejemplos RAG (6,000 tokens):     $0.018  (12%)

OUTPUT ($0.0375 - 22% del costo total)
└─ Ficha generada (2,500 tokens):   $0.0375 (25%)

INSIGHT:
├─ El INPUT representa 78% del costo
├─ Los PDFs originales son 56% del costo total
└─ Optimizar prompts/RAG ahorra poco vs reducir PDFs
```

### Impacto de Reducir Componentes

```
Si reduces prompts/RAG de 11,000 → 5,000 tokens:
├─ Ahorro INPUT: 6,000 × $0.000003 = $0.018
├─ Ahorro por ficha: $0.018 (12%)
└─ Ahorro 250 fichas: $4.50/mes

Si reduces output de 2,500 → 1,500 tokens:
├─ Ahorro OUTPUT: 1,000 × $0.000015 = $0.015
├─ Ahorro por ficha: $0.015 (10%)
└─ Ahorro 250 fichas: $3.75/mes

CONCLUSIÓN:
La optimización agresiva de prompts/output ahorra poco (~$8/mes).
NO VALE LA PENA sacrificar calidad por ahorros mínimos.
```

---

## 💡 Trucos para Optimizar Costos

### 1. Usar Modelo Híbrido

```
En lugar de usar siempre Claude 3.5 ($0.15/ficha):

├─ 40% casos simples → GPT-4o mini ($0.005)
├─ 40% casos medios → GPT-4o ($0.12)
└─ 20% casos complejos → Claude 3.5 ($0.15)

Ahorro: $37.50 → $16.45/mes (56% de ahorro)
```

### 2. Cachear Prompts (Anthropic)

```
Claude 3.5 ofrece "Prompt Caching":

├─ Prompt sistema (5,000 tokens): se cachea
├─ Ejemplos RAG (6,000 tokens): se cachean
└─ Solo pagas full price por PDFs nuevos

Ahorro: Hasta 90% en tokens cacheados
Costo cacheo: $0.30/M (10% del input normal)

Ejemplo:
├─ Prompt inicial: 11,000 tokens × $3.00/M = $0.033
├─ Request 2: 11,000 tokens × $0.30/M = $0.0033 (cached)
└─ Ahorro por ficha: $0.03 (20% total)

Ahorro 250 fichas: $7.50/mes
```

### 3. Reducir Ejemplos RAG Innecesarios

```
En lugar de 3 ejemplos completos (6,000 tokens):
├─ Usar solo 2 ejemplos más relevantes (4,000 tokens)
└─ Ahorro: 2,000 tokens × $3.00/M = $0.006/ficha

Ahorro 250 fichas: $1.50/mes
```

### 4. Comprimir Output sin Perder Calidad

```
En lugar de JSON verboso:
{
  "nombre_ayuda": "Ayuda económica para familias con menores",
  "descripcion": "Esta ayuda está destinada a..."
}

Usar JSON compacto (si no afecta legibilidad):
{"nombre_ayuda":"Ayuda económica familias menores","descripcion":"Ayuda destinada..."}

Ahorro: ~10-15% en tokens output
Ahorro real: $0.015 × 0.15 = $0.002/ficha → $0.50/mes

CUIDADO: NO vale la pena si afecta legibilidad
```

### 5. Batch Processing

```
En lugar de 1 request por ficha:
├─ Procesar 5 fichas en 1 request (si son relacionadas)
├─ Compartir prompt sistema (solo se cuenta 1 vez)
└─ Ahorro: 4 × 5,000 tokens = 20,000 tokens

Limitaciones:
├─ Solo funciona si las fichas son de la misma comunidad
├─ Respuesta más larga (aumenta output tokens)
└─ Complejidad de parsing

Ahorro estimado: 15-20% en casos específicos
```

### 6. Pre-procesar PDFs (Extracción Inteligente)

```
En lugar de enviar PDF completo (20,000 tokens):
├─ Extraer solo secciones relevantes con regex/heurísticas
├─ Eliminar headers/footers repetitivos
└─ Reducir a 15,000 tokens

Ahorro: 5,000 tokens × $3.00/M = $0.015/ficha
Ahorro 250 fichas: $3.75/mes

RIESGO: Puedes perder información crítica
RECOMENDACIÓN: Solo para casos muy claros
```

---

## 🎯 Resumen y Mejores Prácticas

### Fórmula Rápida de Memoria

```
Costo ≈ (Total_Tokens / 1,000,000) × Precio_Promedio

Donde Precio_Promedio:
├─ GPT-4o mini: ~$0.40/M (promedio input+output)
├─ GPT-4o: ~$6.00/M
└─ Claude 3.5: ~$9.00/M
```

### Optimizaciones que SÍ Valen la Pena

1. ✅ **Modelo Híbrido**: Ahorro 56% ($21/mes)
2. ✅ **Prompt Caching (Claude)**: Ahorro 20% ($7.50/mes)
3. ✅ **Reducir 1 ejemplo RAG**: Ahorro 4% ($1.50/mes)

**Total optimizable:** $30/mes (80% del costo)

### Optimizaciones que NO Valen la Pena

1. ❌ Comprimir JSON agresivamente: Ahorro $0.50/mes, riesgo de bugs
2. ❌ Reducir output de 2,500 → 2,000: Ahorro $3.75/mes, pérdida de calidad
3. ❌ Pre-filtrar PDFs: Ahorro $3.75/mes, riesgo de perder info crítica

**Conclusión:** No sacrifiques calidad por ahorros < $5/mes

### Recomendación Final

```
Para 250 fichas/mes:

1. Implementa Modelo Híbrido → $16.45/mes
2. Activa Prompt Caching (Claude) → $12/mes
3. Mantén calidad alta (no optimices más)

Costo final óptimo: $12-16/mes
ROI: 36,358% (sigue siendo brutal)
```

---

## 📚 Recursos Adicionales

- **OpenAI Tokenizer**: https://platform.openai.com/tokenizer
- **OpenAI Pricing**: https://openai.com/api/pricing/
- **Anthropic Pricing**: https://www.anthropic.com/pricing
- **Tiktoken (Python)**: https://github.com/openai/tiktoken
- **Anthropic Prompt Caching**: https://docs.anthropic.com/en/docs/prompt-caching

---

**Última actualización**: Noviembre 2024
**Precios**: Sujetos a cambios, verificar en páginas oficiales
