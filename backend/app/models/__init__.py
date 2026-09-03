"""
app.models — Modelos persistentes y contratos base del dominio.
"""

from app.models.product import (
    Product,
    ProductBase,
    ProductCreate,
    ProductRead,
)
from app.models.stock_movement import (
    MovementType,
    StockMovement,
)

__all__ = [
    "Product",
    "ProductBase",
    "ProductCreate",
    "ProductRead",
    "MovementType",
    "StockMovement",
]
