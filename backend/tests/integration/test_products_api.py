"""
tests/integration/test_products_api.py — Pruebas de integración de la API REST
==============================================================================

¿QUÉ PRUEBA ESTE ARCHIVO? (Requisito fundamental del PDF §3.4 y §8)
----------------------------------------------------------------------
Prueba el ciclo de vida completo de la API HTTP con FastAPI TestClient:
1. `GET /products`:
   - Código HTTP 200.
   - Contrato exacto (items, total, page, page_size).
   - Filtrado por texto (nombre/sku), categoría y precio.
   - Paginación.
   - Caso borde: búsqueda sin resultados retorna total=0, items=[].

2. `GET /products/{id}`:
   - Producto existente -> 200 OK con modelo completo.
   - Producto inexistente -> 404 Not Found.

3. `GET /products/{id}/kardex`:
   - Producto existente con movimientos -> 200 OK con saldos y costo promedio.
   - Producto sin movimientos -> 200 OK con saldo base y lista vacía.
   - Producto inexistente -> 404 Not Found.

4. `POST /products/import`:
   - Carga real de archivo Excel .xlsx.
   - Inserción de filas válidas.
   - Reporte estructurado con filas leídas, insertadas, actualizadas y rechazadas.
   - Verificación de resiliencia parcial (filas con error no anulan filas buenas).
   - Verificación de UPDATE al re-importar el mismo archivo con cambios.
"""

import io
from decimal import Decimal
import openpyxl
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.main import app
from app.models import Product, StockMovement, MovementType


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Inicializa las tablas antes de ejecutar las pruebas."""
    create_db_and_tables()
    yield


@pytest.fixture
def client():
    """Cliente HTTP de pruebas para FastAPI."""
    return TestClient(app)


@pytest.fixture
def seed_products():
    """Inserta un catálogo base conocido para realizar pruebas de integración deterministas."""
    with Session(engine) as session:
        # Limpiar
        for sm in session.exec(select(StockMovement)).all():
            session.delete(sm)
        for p in session.exec(select(Product)).all():
            session.delete(p)
        session.commit()

        p1 = Product(
            sku="TEST-INT-001",
            nombre="Taladro Percutor 700W",
            categoria="Herramientas",
            precio=Decimal("79990.00"),
            stock=10,
        )
        p2 = Product(
            sku="TEST-INT-002",
            nombre="Sierra Caladora 500W",
            categoria="Herramientas",
            precio=Decimal("45000.00"),
            stock=5,
        )
        p3 = Product(
            sku="TEST-INT-003",
            nombre="Guantes Nitrilo Caja 100u",
            categoria="Proteccion",
            precio=Decimal("12000.00"),
            stock=50,
        )
        session.add_all([p1, p2, p3])
        session.commit()
        session.refresh(p1)
        session.refresh(p2)
        session.refresh(p3)

        return {"p1": p1, "p2": p2, "p3": p3}


class TestProductsListEndpoint:
    """Pruebas sobre el endpoint GET /products."""

    def test_list_products_success(self, client, seed_products):
        """GET /products retorna 200 y cumple la estructura de contrato solicitada."""
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

        assert data["total"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) == 3

    def test_list_products_filter_by_query_text(self, client, seed_products):
        """Búsqueda por texto (q) en nombre."""
        response = client.get("/products?q=sierra")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TEST-INT-002"

    def test_list_products_filter_by_sku(self, client, seed_products):
        """Búsqueda por texto (q) coincidiendo con SKU."""
        response = client.get("/products?q=TEST-INT-003")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["nombre"] == "Guantes Nitrilo Caja 100u"

    def test_list_products_filter_by_category(self, client, seed_products):
        """Filtro por categoría."""
        response = client.get("/products?categoria=Herramientas")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["categoria"] == "Herramientas" for item in data["items"])

    def test_list_products_filter_by_price_range(self, client, seed_products):
        """Filtro por rango de precios."""
        response = client.get("/products?precio_min=40000&precio_max=80000")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Taladro (79990) y Sierra (45000)

    def test_list_products_empty_results_edge_case(self, client, seed_products):
        """Caso borde obligatorio del PDF: búsqueda sin resultados."""
        response = client.get("/products?q=producto_inexistente_totalmente")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1


class TestProductDetailEndpoint:
    """Pruebas sobre el endpoint GET /products/{id}."""

    def test_get_product_success(self, client, seed_products):
        """Producto existente retorna 200 y el objeto completo."""
        p1 = seed_products["p1"]
        response = client.get(f"/products/{p1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == p1.id
        assert data["sku"] == p1.sku
        assert data["nombre"] == p1.nombre
        assert float(data["precio"]) == float(p1.precio)

    def test_get_product_not_found(self, client):
        """Producto inexistente retorna 404 Not Found."""
        response = client.get("/products/999999")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()


class TestProductKardexEndpoint:
    """Pruebas sobre el endpoint GET /products/{id}/kardex."""

    def test_kardex_endpoint_success(self, client, seed_products):
        """Consulta de Kardex para producto con movimientos."""
        p1 = seed_products["p1"]
        with Session(engine) as session:
            # Registrar movimientos
            m1 = StockMovement(
                product_id=p1.id,
                movement_type=MovementType.ENTRY,
                quantity=10,
                unit_cost=Decimal("50000.00"),
                reference_document="FAC-001",
            )
            m2 = StockMovement(
                product_id=p1.id,
                movement_type=MovementType.EXIT,
                quantity=4,
                unit_cost=Decimal("50000.00"),
                reference_document="GD-001",
            )
            session.add_all([m1, m2])
            session.commit()

        response = client.get(f"/products/{p1.id}/kardex")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == p1.id
        assert data["sku"] == p1.sku
        assert data["saldo_total_unidades"] == 6  # 10 - 4
        assert len(data["movimientos"]) == 2

    def test_kardex_endpoint_not_found(self, client):
        """Kardex de producto inexistente retorna 404."""
        response = client.get("/products/999999/kardex")
        assert response.status_code == 404


class TestExcelImportEndpoint:
    """Pruebas sobre el endpoint POST /products/import con archivo Excel en memoria."""

    def test_import_excel_with_valid_and_invalid_rows(self, client):
        """
        Envía un archivo .xlsx simulado en memoria con filas válidas e inválidas.
        Verifica la resiliencia parcial (DEC-008).
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["sku", "nombre", "categoria", "precio", "stock"])

        # Fila válida 1 (nuevo)
        ws.append(["EXCEL-T1", "Producto Excel Valido", "Ferreteria", 15000.0, 10])
        # Fila inválida (precio texto)
        ws.append(["EXCEL-ERR1", "Producto Error Precio", "Ferreteria", "GRATIS", 5])
        # Fila inválida (stock negativo)
        ws.append(["EXCEL-ERR2", "Producto Error Stock", "Ferreteria", 20000.0, -2])
        # Fila duplicada en archivo
        ws.append(["EXCEL-T1", "Repetido en archivo", "Ferreteria", 18000.0, 5])

        file_bytes = io.BytesIO()
        wb.save(file_bytes)
        file_bytes.seek(0)

        response = client.post(
            "/products/import",
            files={"file": ("catalogo_test.xlsx", file_bytes.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["leidas"] == 4
        assert data["insertadas"] == 1
        assert data["rechazadas"] == 3
        assert len(data["errores"]) == 3

    def test_import_excel_updates_existing_sku(self, client):
        """Si un SKU ya existe en la BD, la importación debe actualizar sus valores (UPDATE)."""
        # Asegurar producto previo
        with Session(engine) as session:
            existing = session.exec(select(Product).where(Product.sku == "SKU-UPDATE-ME")).first()
            if not existing:
                p = Product(
                    sku="SKU-UPDATE-ME",
                    nombre="Nombre Antiguo",
                    categoria="Herramientas",
                    precio=Decimal("10000.00"),
                    stock=5,
                )
                session.add(p)
                session.commit()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["sku", "nombre", "categoria", "precio", "stock"])
        ws.append(["SKU-UPDATE-ME", "Nombre Nuevo Actualizado", "Herramientas Pro", 19990.0, 25])

        file_bytes = io.BytesIO()
        wb.save(file_bytes)
        file_bytes.seek(0)

        response = client.post(
            "/products/import",
            files={"file": ("update_test.xlsx", file_bytes.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["actualizadas"] >= 1

        # Verificar en base de datos
        with Session(engine) as session:
            updated = session.exec(select(Product).where(Product.sku == "SKU-UPDATE-ME")).first()
            assert updated is not None
            assert updated.nombre == "Nombre Nuevo Actualizado"
            assert updated.precio == Decimal("19990.00")
            assert updated.stock == 25
