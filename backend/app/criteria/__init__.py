"""
app.criteria — Implementación del Patrón Criteria para consultas y filtros seguros.
"""

from app.criteria.criteria_builder import (
    ProductCriteriaBuilder,
    build_product_criteria_from_params,
)
from app.criteria.filters import (
    Filter,
    FilterOperator,
    ProductField,
)
from app.criteria.product_criteria import ProductCriteria

__all__ = [
    "Filter",
    "FilterOperator",
    "ProductField",
    "ProductCriteria",
    "ProductCriteriaBuilder",
    "build_product_criteria_from_params",
]
