"""
tests/unit/test_criteria.py — Pruebas unitarias para el Patrón Criteria
========================================================================

¿QUÉ PRUEBA ESTE ARCHIVO? (Requisito fundamental del PDF §3.4 y §4.1)
----------------------------------------------------------------------
Prueba toda la lógica de construcción de filtros, operadores, paginación
y validaciones de seguridad de forma PURA Y AISLADA:
- SIN levantar servidor FastAPI.
- SIN conectar a PostgreSQL ni SQLite.
- Ejecución ultrarrápida y determinista.
"""

from decimal import Decimal
import pytest

from app.criteria.filters import Filter, FilterOperator, ProductField
from app.criteria.product_criteria import ProductCriteria
from app.criteria.criteria_builder import (
    ProductCriteriaBuilder,
    build_product_criteria_from_params,
)


class TestCriteriaFilters:
    """Pruebas unitarias sobre la definición y validación de filtros individuales."""

    def test_create_valid_filter_equal(self):
        """Verifica la creación de un filtro de igualdad."""
        f = Filter(field=ProductField.CATEGORIA, operator=FilterOperator.EQUAL, value="Herramientas")
        assert f.field == ProductField.CATEGORIA
        assert f.operator == FilterOperator.EQUAL
        assert f.value == "Herramientas"

    def test_create_valid_filter_contains(self):
        """Verifica la creación de un filtro de coincidencia parcial."""
        f = Filter(field=ProductField.NOMBRE, operator=FilterOperator.CONTAINS, value="taladro")
        assert f.operator == FilterOperator.CONTAINS
        assert f.value == "taladro"

    def test_create_valid_filter_between(self):
        """Verifica la creación de un filtro de rango inclusivo (between)."""
        f = Filter(
            field=ProductField.PRECIO,
            operator=FilterOperator.BETWEEN,
            value=(Decimal("10000"), Decimal("50000")),
        )
        assert f.operator == FilterOperator.BETWEEN
        assert f.value == (Decimal("10000"), Decimal("50000"))

    def test_filter_between_invalid_value_raises_error(self):
        """El operador between debe fallar si no recibe exactamente 2 elementos o si min > max."""
        with pytest.raises(ValueError, match="El operador 'between' requiere una tupla o lista de exactamente 2 elementos"):
            Filter(field=ProductField.PRECIO, operator=FilterOperator.BETWEEN, value="10000")

        with pytest.raises(ValueError, match="no puede ser mayor al máximo"):
            Filter(
                field=ProductField.PRECIO,
                operator=FilterOperator.BETWEEN,
                value=(Decimal("50000"), Decimal("10000")),
            )

    def test_filter_none_value_raises_error(self):
        """Un filtro no puede tener un valor nulo."""
        with pytest.raises(ValueError, match="no puede ser None"):
            Filter(field=ProductField.NOMBRE, operator=FilterOperator.EQUAL, value=None)

    def test_unsupported_field_fails(self):
        """
        Campos no permitidos en ProductField deben ser rechazados.
        Garantía contra inyección SQL y consulta de campos internos.
        """
        with pytest.raises(ValueError):
            ProductField("campo_invalido_peligroso")


class TestProductCriteria:
    """Pruebas sobre el objeto ProductCriteria inmutable y sus cálculos de paginación."""

    def test_default_criteria(self):
        """Un Criteria por defecto debe tener página 1, tamaño 20, orden por nombre asc."""
        c = ProductCriteria()
        assert c.page == 1
        assert c.page_size == 20
        assert c.order_by == ProductField.NOMBRE
        assert c.order_dir == "asc"
        assert c.offset == 0
        assert c.limit == 20
        assert not c.has_filters()

    def test_pagination_offset_calculation(self):
        """Verifica el cálculo de OFFSET para diferentes páginas."""
        c1 = ProductCriteria(page=1, page_size=20)
        assert c1.offset == 0

        c2 = ProductCriteria(page=2, page_size=20)
        assert c2.offset == 20

        c3 = ProductCriteria(page=5, page_size=10)
        assert c3.offset == 40

    def test_invalid_page_raises_error(self):
        """Número de página menor a 1 debe ser rechazado."""
        with pytest.raises(ValueError, match="El número de página debe ser mayor o igual a 1"):
            ProductCriteria(page=0)

    def test_invalid_page_size_raises_error(self):
        """Tamaño de página menor a 1 o mayor a 100 debe ser rechazado."""
        with pytest.raises(ValueError, match="El tamaño de página debe ser mayor o igual a 1"):
            ProductCriteria(page_size=0)

        with pytest.raises(ValueError, match="El tamaño de página máximo permitido es 100"):
            ProductCriteria(page_size=101)

    def test_invalid_order_dir_raises_error(self):
        """Dirección de ordenamiento distinta a 'asc' o 'desc' debe ser rechazada."""
        with pytest.raises(ValueError, match="La dirección de ordenamiento debe ser 'asc' o 'desc'"):
            ProductCriteria(order_dir="diagonal")

    def test_criteria_is_immutable(self):
        """ProductCriteria debe ser inmutable para evitar efectos secundarios."""
        c = ProductCriteria()
        with pytest.raises(Exception):
            c.page = 2


class TestCriteriaBuilder:
    """Pruebas sobre la construcción de Criteria a partir de parámetros HTTP."""

    def test_build_search_by_name(self):
        """Búsqueda libre por texto ('q') genera filtro CONTAINS en nombre."""
        criteria = build_product_criteria_from_params(q="taladro")
        assert len(criteria.filters) == 1
        f = criteria.filters[0]
        assert f.field == ProductField.NOMBRE
        assert f.operator == FilterOperator.CONTAINS
        assert f.value == "taladro"

    def test_build_category_filter(self):
        """Filtro por categoría genera filtro EQUAL."""
        criteria = build_product_criteria_from_params(categoria="Herramientas")
        assert len(criteria.filters) == 1
        f = criteria.filters[0]
        assert f.field == ProductField.CATEGORIA
        assert f.operator == FilterOperator.EQUAL
        assert f.value == "Herramientas"

    def test_build_price_range_both_limits(self):
        """Si vienen precio_min y precio_max se usa BETWEEN."""
        criteria = build_product_criteria_from_params(
            precio_min=Decimal("15000"),
            precio_max=Decimal("45000"),
        )
        assert len(criteria.filters) == 1
        f = criteria.filters[0]
        assert f.field == ProductField.PRECIO
        assert f.operator == FilterOperator.BETWEEN
        assert f.value == (Decimal("15000"), Decimal("45000"))

    def test_build_price_only_min(self):
        """Si solo viene precio_min se usa GREATER_THAN_OR_EQUAL."""
        criteria = build_product_criteria_from_params(precio_min=Decimal("20000"))
        assert len(criteria.filters) == 1
        f = criteria.filters[0]
        assert f.field == ProductField.PRECIO
        assert f.operator == FilterOperator.GREATER_THAN_OR_EQUAL
        assert f.value == Decimal("20000")

    def test_build_price_only_max(self):
        """Si solo viene precio_max se usa LESS_THAN_OR_EQUAL."""
        criteria = build_product_criteria_from_params(precio_max=Decimal("80000"))
        assert len(criteria.filters) == 1
        f = criteria.filters[0]
        assert f.field == ProductField.PRECIO
        assert f.operator == FilterOperator.LESS_THAN_OR_EQUAL
        assert f.value == Decimal("80000")

    def test_build_combined_filters(self):
        """Combinación simultánea de búsqueda, categoría y rango de precios."""
        criteria = build_product_criteria_from_params(
            q="casco",
            categoria="Seguridad",
            precio_min=Decimal("5000"),
            precio_max=Decimal("30000"),
            page=3,
            page_size=15,
            order_by="precio",
            order_dir="desc",
        )
        assert len(criteria.filters) == 3
        assert criteria.page == 3
        assert criteria.page_size == 15
        assert criteria.offset == 30  # (3 - 1) * 15
        assert criteria.order_by == ProductField.PRECIO
        assert criteria.order_dir == "desc"

    def test_builder_rejects_disallowed_order_field(self):
        """El builder debe rechazar campos de ordenamiento que no estén en ProductField."""
        builder = ProductCriteriaBuilder()
        with pytest.raises(ValueError, match="Campo de ordenamiento .* no permitido"):
            builder.with_ordering(order_by="password_hash")

    def test_builder_rejects_min_greater_than_max_price(self):
        """El builder debe rechazar precio_min mayor a precio_max."""
        builder = ProductCriteriaBuilder()
        with pytest.raises(ValueError, match="precio_min .* no puede ser mayor que precio_max"):
            builder.with_price_range(precio_min=50000, precio_max=10000)
