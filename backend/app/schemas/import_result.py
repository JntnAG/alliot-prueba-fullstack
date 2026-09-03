"""
schemas/import_result.py — Esquemas de respuesta para importación masiva de Excel
================================================================================

¿QUÉ HACE ESTE ARCHIVO? 
---------------------------------------------------
Cuando un administrador sube un archivo Excel con cientos de productos,
pueden pasar varias cosas:
- Algunos productos son completamente nuevos -> se INSERTAN.
- Algunos productos ya existían en la tienda -> se ACTUALIZAN sus precios/stock.
- Algunas filas tienen errores (un precio negativo, un texto donde va un número) -> se RECHAZAN.

Para que el usuario no se quede a oscuras, el servidor le devuelve un "informe de resultados":
1. Cuántas filas leyó en total (`leidas`).
2. Cuántas insertó (`insertadas`).
3. Cuántas actualizó (`actualizadas`).
4. Cuántas rechazó (`rechazadas`).
5. Y la lista detallada de errores: indicando qué fila falló, qué campo tenía el problema
   y la razón (`errores`: [{"fila": 12, "campo": "precio", "motivo": "..."}]).
"""

from typing import List
from pydantic import BaseModel, ConfigDict


class RowError(BaseModel):
    """
    Detalle específico de un error detectado en una fila del archivo Excel.
    
    Incluye 'campo' como mejora de UX (justificada en DECISIONES.md) para que
    la interfaz sepa exactamente qué columna causó el rechazo.
    """
    fila: int
    campo: str
    motivo: str

    model_config = ConfigDict(from_attributes=True)


class ImportResult(BaseModel):
    """
    Resultado consolidado tras el procesamiento del archivo Excel.
    
    Permite resiliencia parcial: las filas válidas se procesan con éxito
    mientras que las inválidas se reportan individualmente sin anular el resto.
    """
    leidas: int
    insertadas: int
    actualizadas: int
    rechazadas: int
    errores: List[RowError] = []

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "RowError",
    "ImportResult",
]
