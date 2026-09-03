"""
criteria/filters.py — Bloques de construcción para filtros de búsqueda (Patrón Criteria)
========================================================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Imagina que vas a una biblioteca y le pides al bibliotecario:
"Quiero libros cuyo precio esté ENTRE $10 y $50, y cuya categoría sea IGUAL a 'Ciencia'".

En lugar de que cada bibliotecario invente su propia forma de buscar y mezcle
código peligroso (como concatenar texto con riesgo de inyección SQL), creamos
un vocabulario estándar y seguro:
1. `ProductField`: Una lista cerrada de qué campos de un producto SE PERMITE buscar
   (por seguridad, nadie puede filtrar por campos ocultos o internos).
2. `FilterOperator`: La operación que queremos hacer (IGUAL, CONTIENE, MAYOR QUE, MENOR QUE, ENTRE...).
3. `Filter`: Una tarjeta que junta: [Campo] + [Operador] + [Valor].
   Ejemplo: [PRECIO] + [BETWEEN] + [(10000, 50000)]
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple


class FilterOperator(str, Enum):
    """
    Operadores de comparación soportados por el motor de búsqueda.
    """
    EQUAL = "eq"                     # Valor exacto (A == B)
    CONTAINS = "contains"           # Búsqueda parcial de texto (ej: "taladro" en "Taladro Percutor")
    GREATER_THAN = "gt"             # Mayor estricto (>)
    GREATER_THAN_OR_EQUAL = "gte"   # Mayor o igual (>=)
    LESS_THAN = "lt"                # Menor estricto (<)
    LESS_THAN_OR_EQUAL = "lte"      # Menor o igual (<=)
    BETWEEN = "between"             # Rango inclusivo (A <= X <= B)


class ProductField(str, Enum):
    """
    Campos del producto habilitados explícitamente para filtrado y ordenamiento.
    Protege contra inyección de SQL al no admitir nombres de columnas arbitrarios.
    """
    SKU = "sku"
    NOMBRE = "nombre"
    CATEGORIA = "categoria"
    PRECIO = "precio"


@dataclass(frozen=True)
class Filter:
    """
    Representa un filtro atómico de búsqueda inmutable.
    
    Ejemplos:
        Filter(field=ProductField.CATEGORIA, operator=FilterOperator.EQUAL, value="Herramientas")
        Filter(field=ProductField.PRECIO, operator=FilterOperator.BETWEEN, value=(10000, 50000))
    """
    field: ProductField
    operator: FilterOperator
    value: Any

    def __post_init__(self):
        """
        Valida que el valor sea coherente con el operador.
        """
        if self.operator == FilterOperator.BETWEEN:
            if not isinstance(self.value, (tuple, list)) or len(self.value) != 2:
                raise ValueError("El operador 'between' requiere una tupla o lista de exactamente 2 elementos (min, max).")
            min_val, max_val = self.value
            if min_val is not None and max_val is not None and min_val > max_val:
                raise ValueError(f"En 'between', el valor mínimo ({min_val}) no puede ser mayor al máximo ({max_val}).")
        
        if self.value is None:
            raise ValueError(f"El valor del filtro para el campo '{self.field.value}' no puede ser None.")


__all__ = [
    "FilterOperator",
    "ProductField",
    "Filter",
]
