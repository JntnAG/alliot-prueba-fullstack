"""
criteria/product_criteria.py — Objeto de Dominio de Búsqueda (ProductCriteria)
=============================================================================

¿QUÉ HACE ESTE ARCHIVO? 
---------------------------------------------------
`ProductCriteria` es la "carpeta de instrucciones de búsqueda" completa.
Contiene:
1. La lista de filtros aplicados (`filters`): ej. precio > 1000 y categoría = 'Herramientas'.
2. La paginación (`page` y `page_size`): ej. "dame la página 2, mostrando de a 20 productos".
3. El ordenamiento (`order_by` y `order_dir`): ej. "ordena por nombre de la A a la Z (asc)".

¿POR QUÉ ES TAN IMPORTANTE ESTE PATRÓN EN LA PRUEBA TÉCNICA?
------------------------------------------------------------
El PDF destaca el Patrón Criteria como el punto extra de más valor porque:
- DESACOPLA: El endpoint de FastAPI no necesita saber cómo armar SQL. Solo dice: "tengo este Criteria".
- TESTEABLE: Puedes probar la lógica de Criteria sin base de datos ni internet, en milisegundos.
- EXTENSIBLE: Si mañana agregas un filtro nuevo, no cambias la arquitectura ni escribes SQL a mano.
- SEGURO: Evita inyección SQL al usar objetos y campos tipados.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from app.criteria.filters import Filter, FilterOperator, ProductField


@dataclass(frozen=True)
class ProductCriteria:
    """
    Especificación de búsqueda completa para productos.
    Es inmutable (frozen=True) para garantizar predictibilidad y evitar efectos secundarios.
    """
    filters: List[Filter] = field(default_factory=list)
    page: int = 1
    page_size: int = 20
    order_by: ProductField = ProductField.NOMBRE
    order_dir: str = "asc"

    def __post_init__(self):
        """
        Garantiza que la paginación y el ordenamiento sean siempre válidos.
        """
        if self.page < 1:
            raise ValueError(f"El número de página debe ser mayor o igual a 1 (recibido: {self.page}).")
        
        if self.page_size < 1:
            raise ValueError(f"El tamaño de página debe ser mayor o igual a 1 (recibido: {self.page_size}).")
        
        if self.page_size > 100:
            raise ValueError(f"El tamaño de página máximo permitido es 100 (recibido: {self.page_size}).")
        
        normalized_dir = self.order_dir.lower()
        if normalized_dir not in ("asc", "desc"):
            raise ValueError(f"La dirección de ordenamiento debe ser 'asc' o 'desc' (recibido: '{self.order_dir}').")
        
        # Como es frozen, si normalizamos order_dir usamos object.__setattr__
        if self.order_dir != normalized_dir:
            object.__setattr__(self, "order_dir", normalized_dir)

    @property
    def offset(self) -> int:
        """
        Calcula el desplazamiento de registros (OFFSET) para la consulta a la base de datos.
        Página 1: offset 0
        Página 2 con page_size=20: offset 20
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """
        Retorna la cantidad máxima de registros por página (LIMIT).
        """
        return self.page_size

    def has_filters(self) -> bool:
        """
        Indica si el criterio contiene filtros activos.
        """
        return len(self.filters) > 0

    def get_filters_for_field(self, field_name: ProductField) -> List[Filter]:
        """
        Obtiene todos los filtros asociados a un campo específico.
        """
        return [f for f in self.filters if f.field == field_name]


__all__ = [
    "ProductCriteria",
]
