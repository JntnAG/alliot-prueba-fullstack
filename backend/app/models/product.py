"""
models/product.py — Modelo de datos y contratos para Producto
=============================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
En una tienda física, un producto tiene una etiqueta con su código de barras interno
(SKU), su nombre comercial, categoría, precio, cantidad en bodega e imagen.

En programación, necesitamos una "plantilla" o "molde" que defina exactamente
qué datos tiene un producto y qué reglas debe cumplir.
Aquí usamos SQLModel, que combina lo mejor de dos mundos:
1. Pydantic: Valida que los datos sean correctos (ej: que el precio sea un número y no texto).
2. SQLAlchemy: Se encarga de guardar y leer esos datos en la base de datos (tablas y columnas).

¿POR QUÉ SEPARAR EN ProductBase, Product, ProductCreate y ProductRead?
---------------------------------------------------------------------
- ProductBase: Los datos comunes (nombre, precio, stock...).
- Product: La tabla real en la base de datos (agrega id autoincremental y restricción de unicidad de SKU).
- ProductCreate: Lo que el cliente envía cuando quiere crear un producto (sin id, porque la base de datos lo genera).
- ProductRead: Lo que la API le responde al cliente (incluye su id asignado).

¿POR QUÉ USAR Decimal EN VEZ DE float PARA EL PRECIO?
-----------------------------------------------------
Las computadoras tienen errores de redondeo con números con decimales normales (float):
ejemplo clásico: 0.1 + 0.2 da 0.30000000000000004.
En inventario y dinero, un centavo perdido rompe balances contables.
`Decimal` almacena números exactos, sin pérdida de precisión.
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """
    Campos base que describen a un producto en el sistema.
    """
    sku: str = Field(
        description="Código único de identificación de stock (Stock Keeping Unit)"
    )
    nombre: str = Field(
        description="Nombre comercial descriptivo del producto"
    )
    descripcion: Optional[str] = Field(
        default=None,
        description="Descripción detallada de especificaciones y características (opcional)"
    )
    categoria: str = Field(
        description="Categoría o familia a la que pertenece el producto (ej: Herramientas, Protección)"
    )
    precio: Decimal = Field(
        max_digits=12,
        decimal_places=2,
        description="Precio de venta unitario expresado con precisión decimal"
    )
    stock: int = Field(
        default=0,
        ge=0,
        description="Unidades físicas disponibles para la venta (no puede ser negativo)"
    )
    imagen_url: Optional[str] = Field(
        default=None,
        description="URL a la fotografía o miniatura del producto"
    )


class Product(ProductBase, table=True):
    """
    Representa la tabla 'product' persistida en la Base de Datos.
    
    Garantiza que el SKU sea único a nivel del motor de base de datos
    (no solo mediante validación en Python), evitando duplicados incluso
    en operaciones concurrentes o scripts masivos.
    """
    __tablename__ = "product"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_product_sku"),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador numérico autoincremental único en BD"
    )
    # Sobrescribimos sku para indexarlo y optimizar búsquedas rápidas
    sku: str = Field(index=True, nullable=False)


class ProductCreate(ProductBase):
    """
    Schema para registrar un nuevo producto (sin ID previo).
    """
    pass


class ProductRead(ProductBase):
    """
    Schema para devolver la información de un producto a los clientes de la API.
    Garantiza que el cliente reciba siempre el 'id' generado.
    """
    id: int
