"""
criteria/criteria_builder.py — Constructor de Criteria desde parámetros HTTP
=============================================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Cuando un usuario en su navegador entra a:
  `/products?q=taladro&categoria=Herramientas&precio_min=10000&precio_max=80000&page=2`

El servidor recibe esos parámetros sueltos en formato de texto.
La función de este archivo (`build_product_criteria` o `ProductCriteriaBuilder`)
es tomar esos textos crudos, limpiarlos, validarlos y empaquetarlos ordenadamente
dentro de un objeto `ProductCriteria`.

De esta forma, la capa que ejecuta la búsqueda en base de datos NO tiene que preocuparse
por validar URLs, ni parámetros web; solo recibe un `ProductCriteria` 100% confiable y seguro.
"""

from decimal import Decimal
from typing import List, Optional, Union
from app.criteria.filters import Filter, FilterOperator, ProductField
from app.criteria.product_criteria import ProductCriteria


class ProductCriteriaBuilder:
    """
    Constructor fluido (Fluent Builder) para ensamblar ProductCriteria paso a paso.
    """
    def __init__(self):
        self._filters: List[Filter] = []
        self._page: int = 1
        self._page_size: int = 20
        self._order_by: ProductField = ProductField.NOMBRE
        self._order_dir: str = "asc"

    def with_filter(self, field: ProductField, operator: FilterOperator, value: any) -> "ProductCriteriaBuilder":
        """Agrega un filtro individual."""
        if value is not None:
            self._filters.append(Filter(field=field, operator=operator, value=value))
        return self

    def with_search_query(self, query: Optional[str]) -> "ProductCriteriaBuilder":
        """
        Búsqueda por texto libre ('q'):
        Si el usuario busca 'taladro', se aplica filtro de coincidencia parcial
        sobre el nombre del producto.
        """
        if query and query.strip():
            clean_query = query.strip()
            self._filters.append(
                Filter(field=ProductField.NOMBRE, operator=FilterOperator.CONTAINS, value=clean_query)
            )
        return self

    def with_category(self, category: Optional[str]) -> "ProductCriteriaBuilder":
        """Filtro exacto por categoría."""
        if category and category.strip():
            self._filters.append(
                Filter(field=ProductField.CATEGORIA, operator=FilterOperator.EQUAL, value=category.strip())
            )
        return self

    def with_price_range(
        self,
        precio_min: Optional[Union[Decimal, float, int]] = None,
        precio_max: Optional[Union[Decimal, float, int]] = None,
    ) -> "ProductCriteriaBuilder":
        """
        Filtro de rango de precios.
        Si se entregan ambos precios, utiliza el operador BETWEEN.
        Si solo se entrega uno, utiliza GTE o LTE según corresponda.
        """
        min_dec = Decimal(str(precio_min)) if precio_min is not None else None
        max_dec = Decimal(str(precio_max)) if precio_max is not None else None

        if min_dec is not None and max_dec is not None:
            if min_dec > max_dec:
                raise ValueError(f"precio_min ({min_dec}) no puede ser mayor que precio_max ({max_dec}).")
            self._filters.append(
                Filter(field=ProductField.PRECIO, operator=FilterOperator.BETWEEN, value=(min_dec, max_dec))
            )
        elif min_dec is not None:
            self._filters.append(
                Filter(field=ProductField.PRECIO, operator=FilterOperator.GREATER_THAN_OR_EQUAL, value=min_dec)
            )
        elif max_dec is not None:
            self._filters.append(
                Filter(field=ProductField.PRECIO, operator=FilterOperator.LESS_THAN_OR_EQUAL, value=max_dec)
            )
        return self

    def with_pagination(self, page: int = 1, page_size: int = 20) -> "ProductCriteriaBuilder":
        """Establece la página y el límite de elementos."""
        self._page = page
        self._page_size = page_size
        return self

    def with_ordering(
        self,
        order_by: Union[ProductField, str] = ProductField.NOMBRE,
        order_dir: str = "asc",
    ) -> "ProductCriteriaBuilder":
        """
        Establece el campo y la dirección de ordenamiento.
        Valida que el campo pertenezca a la lista cerrada ProductField.
        """
        if isinstance(order_by, str):
            try:
                self._order_by = ProductField(order_by.lower().strip())
            except ValueError:
                valid_fields = ", ".join([f.value for f in ProductField])
                raise ValueError(f"Campo de ordenamiento '{order_by}' no permitido. Campos válidos: {valid_fields}")
        else:
            self._order_by = order_by

        self._order_dir = order_dir.lower().strip()
        return self

    def build(self) -> ProductCriteria:
        """Construye y devuelve la instancia inmutable de ProductCriteria."""
        return ProductCriteria(
            filters=list(self._filters),
            page=self._page,
            page_size=self._page_size,
            order_by=self._order_by,
            order_dir=self._order_dir,
        )


def build_product_criteria_from_params(
    q: Optional[str] = None,
    categoria: Optional[str] = None,
    precio_min: Optional[Decimal] = None,
    precio_max: Optional[Decimal] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: str = "nombre",
    order_dir: str = "asc",
) -> ProductCriteria:
    """
    Función de ayuda directa para transformar los query parameters de FastAPI
    en un ProductCriteria en una sola llamada.
    """
    builder = ProductCriteriaBuilder()
    builder.with_search_query(q)
    builder.with_category(categoria)
    builder.with_price_range(precio_min=precio_min, precio_max=precio_max)
    builder.with_pagination(page=page, page_size=page_size)
    builder.with_ordering(order_by=order_by, order_dir=order_dir)
    return builder.build()


__all__ = [
    "ProductCriteriaBuilder",
    "build_product_criteria_from_params",
]
