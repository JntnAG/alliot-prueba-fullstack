"""
schemas/product.py — Esquemas de respuesta y contratos para Productos
====================================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Cuando un usuario consulta una lista de productos en una tienda online,
no solo espera ver la lista de artículos. También necesita saber:
1. ¿Cuántos productos hay en total para calcular cuántas páginas existen? (`total`)
2. ¿En qué página se encuentra actualmente? (`page`)
3. ¿Cuántos productos se muestran por página? (`page_size`)

Este archivo define ese contrato (`ProductListResponse`), asegurando que el frontend
reciba exactamente la estructura esperada:
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
"""

from typing import List
from pydantic import BaseModel, ConfigDict
from app.models.product import ProductCreate, ProductRead


class ProductListResponse(BaseModel):
    """
    Contrato de respuesta paginada para el endpoint GET /products.
    
    Alineado exactamente con el contrato estipulado en la prueba técnica:
    {
      "items": [...],
      "total": int,
      "page": int,
      "page_size": int
    }
    """
    items: List[ProductRead]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ProductCreate",
    "ProductRead",
    "ProductListResponse",
]
