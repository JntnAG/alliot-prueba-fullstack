"""
schemas/kardex.py — Esquemas para visualización y reporte de Kardex valorizado
=============================================================================

¿QUÉ HACE ESTE ARCHIVO? 
---------------------------------------------------
El Kardex es como la cartola o extracto bancario de un producto:
En tu banco ves:
- "Fecha: 01/Sept | Depósito: +$100 | Saldo final: $100"
- "Fecha: 03/Sept | Retiro: -$20 | Saldo final: $80"

En un Kardex industrial valorizado vemos lo mismo pero con inventario y dinero:
- "Fecha: 01/Sept | Entrada de 10 taladros a $50.000 c/u | Saldo: 10 unidades | Valor total: $500.000"
- "Fecha: 02/Sept | Entrada de 10 taladros a $70.000 c/u | Saldo: 20 unidades | Valor total: $1.200.000 | Nuevo Costo Promedio: $60.000"
- "Fecha: 05/Sept | Salida (venta) de 5 taladros al costo promedio de $60.000 | Saldo: 15 unidades | Valor total: $900.000"

Este archivo define la estructura de cada línea de movimiento calculada (`KardexLine`)
y del reporte completo (`ProductKardexResponse`) que consume el frontend.
"""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict
from app.models.stock_movement import MovementType


class KardexLine(BaseModel):
    """
    Representa una línea cronológica del Kardex con sus saldos recalculados.
    """
    id: int
    fecha: datetime
    tipo: MovementType
    cantidad: int
    costo_unitario: Decimal
    documento_referencia: str
    
    # Cálculos acumulados tras este movimiento (Promedio Ponderado Móvil)
    saldo_unidades: int
    costo_promedio: Decimal
    saldo_valorizado: Decimal

    model_config = ConfigDict(from_attributes=True)


class ProductKardexResponse(BaseModel):
    """
    Respuesta integral de la ficha de Kardex de un producto:
    información básica, saldo actual valorizado y el historial completo.
    """
    product_id: int
    sku: str
    nombre: str
    saldo_total_unidades: int
    costo_promedio_actual: Decimal
    saldo_total_valorizado: Decimal
    movimientos: List[KardexLine] = []

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "KardexLine",
    "ProductKardexResponse",
]
