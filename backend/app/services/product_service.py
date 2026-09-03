"""
services/product_service.py — Intérprete del Patrón Criteria y Servicio de Productos
===================================================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Este archivo es el "traductor oficial" del sistema.
Por un lado, recibe un `ProductCriteria` (que es una intención abstracta de búsqueda,
independiente de la base de datos).
Por el otro lado, se comunica con SQLModel/PostgreSQL/SQLite para transformar esa
intención en una consulta SQL real, segura y altamente optimizada.

RESPONSABILIDADES:
------------------
1. Traducir cada `Filter` a una condición WHERE de base de datos (segura contra SQL Injection).
2. Contar el número total de resultados (`total`) para que la paginación funcione.
3. Aplicar el ordenamiento (A-Z, Z-A, menor a mayor precio...).
4. Aplicar la paginación (`OFFSET` y `LIMIT`).
5. Proveer métodos para consultar un producto por ID.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlmodel import Session, col, select

from app.criteria.filters import Filter, FilterOperator, ProductField
from app.criteria.product_criteria import ProductCriteria
from app.models.product import Product
from app.schemas.product import ProductListResponse, ProductRead


class ProductService:
    """
    Servicio de dominio para la gestión y consulta de productos mediante el Patrón Criteria.
    """

    @staticmethod
    def _apply_filter_to_query(query, f: Filter):
        """
        Interpreta un Filter individual y lo añade como condición a la consulta SQLModel.
        """
        column_map = {
            ProductField.SKU: Product.sku,
            ProductField.NOMBRE: Product.nombre,
            ProductField.CATEGORIA: Product.categoria,
            ProductField.PRECIO: Product.precio,
        }

        column = column_map[f.field]

        if f.operator == FilterOperator.EQUAL:
            return query.where(column == f.value)

        elif f.operator == FilterOperator.CONTAINS:
            # ilike permite búsqueda insensible a mayúsculas/minúsculas
            if f.field == ProductField.NOMBRE:
                # Búsqueda que coincide con nombre o SKU (según reglas de búsqueda)
                return query.where(col(Product.nombre).ilike(f"%{f.value}%") | col(Product.sku).ilike(f"%{f.value}%"))
            return query.where(col(column).ilike(f"%{f.value}%"))

        elif f.operator == FilterOperator.GREATER_THAN:
            return query.where(column > f.value)

        elif f.operator == FilterOperator.GREATER_THAN_OR_EQUAL:
            return query.where(column >= f.value)

        elif f.operator == FilterOperator.LESS_THAN:
            return query.where(column < f.value)

        elif f.operator == FilterOperator.LESS_THAN_OR_EQUAL:
            return query.where(column <= f.value)

        elif f.operator == FilterOperator.BETWEEN:
            min_val, max_val = f.value
            return query.where(col(column).between(min_val, max_val))

        return query

    @classmethod
    def search_products(cls, session: Session, criteria: ProductCriteria) -> Tuple[List[Product], int]:
        """
        Ejecuta la búsqueda de productos según el ProductCriteria especificado.
        Retorna la tupla (lista_de_productos_en_pagina, total_global_de_coincidencias).
        """
        # 1. Armar consulta base con todos los filtros
        base_query = select(Product)
        for f in criteria.filters:
            base_query = cls._apply_filter_to_query(base_query, f)

        # 2. Calcular el total de coincidencias (COUNT) para la paginación
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count: int = session.exec(count_query).one()

        # 3. Aplicar ordenamiento
        order_column_map = {
            ProductField.SKU: Product.sku,
            ProductField.NOMBRE: Product.nombre,
            ProductField.CATEGORIA: Product.categoria,
            ProductField.PRECIO: Product.precio,
        }
        order_col = order_column_map[criteria.order_by]
        if criteria.order_dir == "desc":
            base_query = base_query.order_by(order_col.desc())
        else:
            base_query = base_query.order_by(order_col.asc())

        # 4. Aplicar paginación (OFFSET y LIMIT)
        paginated_query = base_query.offset(criteria.offset).limit(criteria.limit)

        # 5. Ejecutar la consulta en la base de datos
        items = list(session.exec(paginated_query).all())

        return items, total_count

    @classmethod
    def get_products_response(cls, session: Session, criteria: ProductCriteria) -> ProductListResponse:
        """
        Obtiene la lista de productos y devuelve directamente el esquema ProductListResponse.
        """
        items, total = cls.search_products(session, criteria)
        return ProductListResponse(
            items=[ProductRead.model_validate(p) for p in items],
            total=total,
            page=criteria.page,
            page_size=criteria.page_size,
        )

    @staticmethod
    def get_by_id(session: Session, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su clave primaria (ID).
        Retorna None si no existe.
        """
        return session.get(Product, product_id)


__all__ = [
    "ProductService",
]
