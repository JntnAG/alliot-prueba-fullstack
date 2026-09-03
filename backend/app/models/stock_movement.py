"""
models/stock_movement.py — Registro de movimientos de inventario (Kardex)
========================================================================

¿QUÉ HACE ESTE ARCHIVO? 
---------------------------------------------------
Imagina el libro contable de una bodega:
Cada vez que entra un camión con mercancía (ENTRY) o que sale un pedido para un
cliente (EXIT), el bodeguero anota en un renglón:
1. Cuándo ocurrió (fecha).
2. Qué se hizo (¿Entró mercancía o salió?).
3. Cuántas unidades.
4. A qué costo unitario se compró (o a qué costo promedio sale).
5. Cuál es el documento de respaldo (Factura #1024, Guía de despacho #55, etc.).
6. A qué producto pertenece (clave foránea `product_id`).

Ese registro individual es un "StockMovement" (Movimiento de Stock).
La suma cronológica de estos renglones es lo que da vida al KARDEX.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class MovementType(str, Enum):
    """
    Tipo de operación en bodega:
    - ENTRY: Entrada o compra de mercancía (aumenta unidades y recalcula costo promedio).
    - EXIT: Salida o venta de existencias (disminuye unidades al costo promedio vigente).
    """
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class StockMovement(SQLModel, table=True):
    """
    Representa la tabla 'stockmovement' persistida en la Base de Datos.
    
    Almacena cada transacción física del inventario para garantizar trazabilidad
    y permitir el cálculo de saldos y valorización contable.
    """
    __tablename__ = "stockmovement"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador único del registro de movimiento"
    )
    product_id: int = Field(
        foreign_key="product.id",
        index=True,
        description="ID del producto al que pertenece este movimiento (Relación Foránea)"
    )
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora en que se efectuó el movimiento"
    )
    movement_type: MovementType = Field(
        description="Tipo de movimiento: ENTRY (Entrada) o EXIT (Salida)"
    )
    quantity: int = Field(
        gt=0,
        description="Cantidad de unidades transferidas (siempre positiva, > 0)"
    )
    unit_cost: Decimal = Field(
        max_digits=12,
        decimal_places=2,
        description="Costo unitario asociado a la transacción (precisión Decimal)"
    )
    reference_document: str = Field(
        description="Identificador del documento de respaldo (ej: Factura F-00123, Guía G-456)"
    )
