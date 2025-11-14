"""
Schema Pydantic para Ficha de Ayuda Social.
Basado en las instrucciones oficiales del proyecto.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from datetime import date


# === Valores de Referencia 2025 ===
class IPREMValues(BaseModel):
    """Valores del IPREM 2025."""
    dia: str = "20,00 €"
    mes: str = "600,00 €"
    anio_12_pagas: str = "7.200,00 €"
    anio_14_pagas: str = "8.400,00 €"


class SMIValues(BaseModel):
    """Valores del Salario Mínimo Interprofesional 2025."""
    dia: str = "39,47 €"
    mes: str = "1.184,00 €"
    anio_14_pagas: str = "16.576,00 €"


class IRSCValues(BaseModel):
    """Valores del IRSC Cataluña 2025."""
    mes: str = "778,49 €"
    anio: str = "9.341,92 €"


class ValoresReferencia2025(BaseModel):
    """Valores de referencia económicos 2025."""
    iprem: IPREMValues = Field(default_factory=IPREMValues)
    smi: SMIValues = Field(default_factory=SMIValues)
    irsc_cataluna: IRSCValues = Field(default_factory=IRSCValues)


# === Enums de Portales y Categorías ===
PORTALES_ENUM = Literal["Mayores", "Discapacidad", "Familia", "Mujer", "Salud"]

CATEGORIAS_ENUM = Literal[
    "Básicas",
    "Vivienda",
    "Enseres",
    "Salud",
    "Discapacidad",
    "Dependencia",
    "Servicios",
    "Rentas",
    "Técnicas",
    "Catástrofes",
    "Acogimiento",
]

TIPOS_AYUDA_ENUM = Literal[
    "Accesibilidad",
    "Acogimiento",
    "Alimentación",
    "Atención temprana",
    "Básicas",
    "Bonificación impuestos",
    "Carnet de Conducir",
    "Catástrofes",
    "Complementarias Dependencias",
    "Conciliación",
    "Cultura - Ocio",
    "Discapacidad",
    "Emigrantes",
    "Energía",
    "Enseres",
    "Estudios",
    "Familia",
    "Funcionarios",
    "Ingreso Mínimo Vital",
    "Natalidad",
    "Paliativos",
    "Reclusos",
    "Rentas",
    "Salud",
    "Servicios",
    "Técnicas",
    "Tecnología",
    "Termalismo",
    "Trabajo - Emprendimiento",
    "Transporte",
    "Viajes",
    "Violencia de Género",
    "Vivienda",
]


# === Modelos Anidados ===
class LugarPresentacion(BaseModel):
    """Lugar y forma de presentación."""
    presencial: List[str] = Field(
        default_factory=list,
        description="Lista de lugares de presentación presencial",
    )
    electronica: List[str] = Field(
        default_factory=list,
        description="URLs y métodos de presentación electrónica",
    )


class OtrosDatos(BaseModel):
    """Otros datos de la ficha."""
    USUARIO: str = Field(..., description="Nombre del proyecto/usuario")
    FECHA: str = Field(..., description="Fecha de creación (dd/mm/aaaa)")
    FRASE_PARA_PUBLICITAR: Optional[List[str]] = Field(
        default=None,
        description="Frase publicitaria (solo estatal/autonómico/provincial, máx 20 palabras)",
    )
    DOCUMENTOS_ADJUNTOS: List[str] = Field(
        default_factory=list,
        description="Lista de documentos adjuntos relacionados",
    )


# === Schema Principal ===
class FichaData(BaseModel):
    """
    Schema completo de una Ficha de Ayuda Social.
    Basado en las instrucciones oficiales del proyecto.
    """

    # === Identificación ===
    nombre_ayuda: str = Field(
        ...,
        description="Nombre oficial de la ayuda en lenguaje claro, incluye año si procede",
    )

    portales: List[PORTALES_ENUM] = Field(
        ...,
        description="Portales a los que aplica (Mayores, Discapacidad, Familia, Mujer, Salud)",
        min_items=1,
    )

    categoria: List[CATEGORIAS_ENUM] = Field(
        ...,
        description="Categorías de la ayuda (Básicas, Vivienda, Enseres, etc.)",
        min_items=1,
    )

    tipo_ayuda: TIPOS_AYUDA_ENUM = Field(
        ...,
        description="Tipo específico de ayuda (debe indicar producto/servicio/acción)",
    )

    # === Fechas ===
    fecha_inicio: date = Field(
        ...,
        description="Fecha de inicio del plazo (formato: dd/mm/aaaa)",
    )

    fecha_fin: date = Field(
        ...,
        description="Fecha de fin del plazo (formato: dd/mm/aaaa)",
    )

    fecha_publicacion: Optional[date] = Field(
        None,
        description="Fecha de publicación en BDNS o Boletín Oficial (formato: dd/mm/aaaa)",
    )

    # === Administración ===
    ambito_territorial: str = Field(
        ...,
        description="Ámbito territorial (municipal, provincial, autonómico, estatal)",
    )

    administracion: str = Field(
        ...,
        description="Nombre completo de la administración convocante (con provincia entre paréntesis si es local)",
    )

    # === Requisitos y Beneficiarios ===
    plazo_presentacion: str = Field(
        ...,
        description="Debe usar la fórmula: 'El plazo permanecerá abierto hasta [fecha]'",
    )

    requisitos_acceso: str = Field(
        ...,
        description="Debe iniciar con: 'Los requisitos para optar a las ayudas son los siguientes:'. Incluye generales y específicos por modalidad.",
    )

    beneficiarios: str = Field(
        ...,
        description="Debe iniciar con: 'Podrán ser beneficiarias:'. Describe el colectivo con claridad. Incluye IPREM/SMI/IRSC si aplica.",
    )

    # === Descripción y Cuantía ===
    descripcion: str = Field(
        ...,
        description="Incluye modalidades, gastos cubiertos, requisitos específicos, finalidad, modo de pago e incompatibilidades generales. Sin importes.",
    )

    cuantia: List[str] = Field(
        ...,
        description="Debe iniciar con: 'La cuantía de la ayuda será:'. Lista de tramos/importes. Formato: coma decimal, dos decimales, símbolo € al final.",
        min_items=1,
    )

    importe_maximo: str = Field(
        ...,
        description="Máximo por solicitante y por modalidad si procede",
    )

    # === Resolución y Documentación ===
    resolucion: str = Field(
        ...,
        description="Plazo máximo de resolución, notificación y silencio administrativo",
    )

    documentos_presentar: List[str] = Field(
        ...,
        description="Debe iniciar con: 'La documentación a presentar es la siguiente:'. Lista con guiones, un documento por línea.",
        min_items=1,
    )

    costes_no_subvencionables: Optional[str] = Field(
        None,
        description="Gastos excluidos expresamente. Incompatibilidades generales van en 'Descripción'.",
    )

    criterios_concesion: Optional[str] = Field(
        None,
        description="Criterios objetivos (baremos, puntuaciones, prioridades). Si no hay, dejar vacío.",
    )

    # === Normativa ===
    normativa_reguladora: List[str] = Field(
        ...,
        description="Lista con guiones: Extracto, Convocatoria, Bases, Otros. Incluye boletín con formato: 'BOP [provincia] núm. [número], [dd/mm/aaaa]'",
        min_items=1,
    )

    referencia_legislativa: List[str] = Field(
        default_factory=list,
        description="Lista con guiones: leyes, decretos, órdenes. Nombre oficial completo, fecha y boletín si aplica.",
    )

    # === Presentación ===
    lugar_presentacion: LugarPresentacion = Field(
        ...,
        description="Lugares presenciales y electrónicos de presentación",
    )

    # === Otros Datos ===
    otros_datos: OtrosDatos = Field(
        ...,
        description="Usuario, fecha, frase publicitaria y documentos adjuntos",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nombre_ayuda": "Ayudas de Emergencia Social 2025",
                "portales": ["Familia"],
                "categoria": ["Básicas"],
                "tipo_ayuda": "Básicas",
                "fecha_inicio": "2025-01-01",
                "fecha_fin": "2025-12-31",
                "fecha_publicacion": "2024-12-15",
                "ambito_territorial": "Municipal",
                "administracion": "Ayuntamiento de Madrid (Madrid)",
                "plazo_presentacion": "El plazo permanecerá abierto hasta 31/12/2025",
                "requisitos_acceso": "Los requisitos para optar a las ayudas son los siguientes:\n- Estar empadronado en Madrid.\n- Situación de necesidad acreditada.",
                "beneficiarios": "Podrán ser beneficiarias:\n- Personas físicas empadronadas.\n- Unidades de convivencia.",
                "descripcion": "Ayudas económicas para situaciones de emergencia social...",
                "cuantia": [
                    "Hasta 600,00 € por solicitud",
                    "Máximo 2 solicitudes por año",
                ],
                "importe_maximo": "600,00 € por solicitud",
                "resolucion": "Plazo máximo de 3 meses. Silencio administrativo negativo.",
                "documentos_presentar": [
                    "DNI o NIE.",
                    "Certificado de empadronamiento.",
                    "Informe de servicios sociales.",
                ],
                "costes_no_subvencionables": "No se subvencionan: gastos previos a la solicitud, IVA recuperable.",
                "criterios_concesion": "Baremo de puntuación según situación socioeconómica.",
                "normativa_reguladora": [
                    "Bases Reguladoras de Ayudas de Emergencia Social. BOP Madrid núm. 45, 15/01/2025."
                ],
                "referencia_legislativa": [
                    "Ley 38/2003, de 17 de noviembre, General de Subvenciones."
                ],
                "lugar_presentacion": {
                    "presencial": [
                        "Oficinas de Servicios Sociales del Ayuntamiento de Madrid.",
                        "Oficinas de correos (sobre abierto para compulsa).",
                    ],
                    "electronica": [
                        "Sede electrónica: https://sede.madrid.es/tramite"
                    ],
                },
                "otros_datos": {
                    "USUARIO": "PROYECTO_FICHAS_IA",
                    "FECHA": "15/11/2025",
                    "FRASE_PARA_PUBLICITAR": [
                        "Solicita tu ayuda de emergencia en la sede electrónica."
                    ],
                    "DOCUMENTOS_ADJUNTOS": [
                        "Convocatoria de ayudas de emergencia social de Ayuntamiento de Madrid",
                        "Solicitud de ayuda de emergencia de Ayuntamiento de Madrid",
                    ],
                },
            }
        }

    @validator("portales")
    def validate_portales_order(cls, v):
        """Valida que los portales estén en el orden correcto."""
        orden_correcto = ["Mayores", "Discapacidad", "Familia", "Mujer", "Salud"]
        return sorted(v, key=lambda x: orden_correcto.index(x))

    @validator("plazo_presentacion")
    def validate_plazo_format(cls, v):
        """Valida que el plazo use la fórmula correcta."""
        if not v.startswith("El plazo permanecerá abierto hasta"):
            raise ValueError(
                "El plazo debe usar la fórmula: 'El plazo permanecerá abierto hasta [fecha]'"
            )
        return v

    @validator("requisitos_acceso")
    def validate_requisitos_start(cls, v):
        """Valida que los requisitos inicien con la frase correcta."""
        if not v.startswith("Los requisitos para optar a las ayudas son los siguientes:"):
            raise ValueError(
                "Los requisitos deben iniciar con: 'Los requisitos para optar a las ayudas son los siguientes:'"
            )
        return v

    @validator("beneficiarios")
    def validate_beneficiarios_start(cls, v):
        """Valida que beneficiarios inicie con la frase correcta."""
        if not v.startswith("Podrán ser beneficiarias:"):
            raise ValueError(
                "Beneficiarios debe iniciar con: 'Podrán ser beneficiarias:'"
            )
        return v

    @validator("cuantia")
    def validate_cuantia_format(cls, v):
        """Valida que la cuantía tenga el formato correcto."""
        if not v:
            raise ValueError("La cuantía no puede estar vacía")
        # Verificar que tenga formato de euros (coma decimal, dos decimales, símbolo €)
        for item in v:
            if "€" not in item:
                raise ValueError(
                    f"Cada elemento de cuantía debe incluir el símbolo €: {item}"
                )
        return v

    @validator("documentos_presentar")
    def validate_documentos_unique(cls, v):
        """Valida que no haya documentos duplicados."""
        if len(v) != len(set(v)):
            raise ValueError("Los documentos no pueden estar duplicados")
        return v
