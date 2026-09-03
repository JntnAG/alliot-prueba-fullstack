"""
generate_sample_data.py — Generador de archivo Excel y datos de prueba
======================================================================

¿QUÉ HACE ESTE SCRIPT?
---------------------------------------------------
1. Genera un archivo Excel real llamado 'sample_products.xlsx'.
   Contiene productos válidos y casos borde reales intencionales para probar
   la resiliencia parcial del sistema (Decisión [DEC-008]):
   - Filas válidas normales.
   - Fila con precio inválido ("GRATIS").
   - Fila con precio negativo.
   - Fila con stock negativo.
   - Fila con SKU duplicado dentro del archivo (debe ser rechazada).
   - Fila con SKU vacío.

2. Inicializa en la base de datos productos base y movimientos de Kardex para
   probar inmediatamente los endpoints GET /products, GET /products/{id} y
   GET /products/{id}/kardex.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import openpyxl
from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models import MovementType, Product, StockMovement


def create_sample_excel_file(filename: str = "sample_products.xlsx"):
    """
    Crea un archivo .xlsx con filas válidas e inválidas para demostrar la importación.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    # Encabezados según el PDF (§4.2)
    headers = ["sku", "nombre", "categoria", "precio", "stock", "imagen_url", "descripcion"]
    ws.append(headers)

    # 1. Filas válidas (nuevas inserciones o actualizaciones)
    valid_rows = [
        [
            "SKU-EXCEL-001",
            "Taladro Inalámbrico 20V Max",
            "Herramientas",
            79990.0,
            15,
            "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400",
            "Taladro percutor a batería con motor brushless",
        ],
        [
            "SKU-EXCEL-002",
            "Esmeril Angular 4 1/2 Pulgadas",
            "Herramientas",
            54990.0,
            8,
            "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=400",
            "Esmeril de alta potencia con guarda ajustable",
        ],
        [
            "SKU-EXCEL-003",
            "Casco Minero con Visera Protectora",
            "Protección",
            24990.0,
            30,
            "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=400",
            "Casco con suspensión de cuatro puntos y absorción de impacto",
        ],
        [
            "SKU-EXCEL-004",
            "Zapatos de Seguridad Dielectricos Talla 42",
            "Protección",
            39990.0,
            25,
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "Calzado ergonómico con puntera de composite y suela antideslizante",
        ],
        [
            "SKU-EXCEL-005",
            "Tester Digital Multímetro Automotriz",
            "Electricidad",
            34500.0,
            12,
            "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=400",
            "Multímetro con medición True RMS y pantalla retroiluminada",
        ],
    ]

    # 2. Filas intencionalmente erróneas para validar el reporte y resiliencia
    error_rows = [
        [
            "SKU-ERR-001",
            "Producto con precio texto",
            "Pruebas",
            "NO_NUMERICO",  # Error de precio
            10,
            "",
            "Fila con precio no convertible a decimal",
        ],
        [
            "SKU-ERR-002",
            "Producto con precio negativo",
            "Pruebas",
            -500.0,         # Error precio <= 0
            10,
            "",
            "Fila con precio menor a cero",
        ],
        [
            "SKU-ERR-003",
            "Producto con stock negativo",
            "Pruebas",
            15000.0,
            -15,            # Error stock < 0
            "",
            "Fila con stock negativo",
        ],
        [
            "",             # Error SKU vacío
            "Producto sin SKU",
            "Pruebas",
            20000.0,
            5,
            "",
            "Fila sin identificador SKU",
        ],
        [
            "SKU-EXCEL-001", # Error SKU duplicado dentro del archivo (ya estaba arriba)
            "Taladro Duplicado en el mismo archivo",
            "Herramientas",
            85000.0,
            5,
            "",
            "Fila repetida para probar rechazo anti orden-dependencia",
        ],
    ]

    for r in valid_rows + error_rows:
        ws.append(r)

    wb.save(filename)
    print(f"-> Archivo Excel creado exitosamente: '{filename}' con {len(valid_rows)} filas validas y {len(error_rows)} filas con errores intencionales.")


def seed_database_for_demo():
    """
    Inserta productos iniciales y movimientos de Kardex para demostrar el funcionamiento.
    """
    create_db_and_tables()

    with Session(engine) as session:
        # Verificar si ya existe el producto de demo
        p_demo = session.exec(select(Product).where(Product.sku == "DEMO-TALADRO-01")).first()
        if not p_demo:
            p_demo = Product(
                sku="DEMO-TALADRO-01",
                nombre="Taladro Percutor Industrial 800W",
                descripcion="Taladro con mandril metálico y selector de percusión para concreto y metal.",
                categoria="Herramientas",
                precio=Decimal("89990.00"),
                stock=15,  # 10 iniciales + 10 compra - 5 venta = 15
                imagen_url="https://images.unsplash.com/photo-1504148455328-c376907d081c?w=500",
            )
            session.add(p_demo)
            session.commit()
            session.refresh(p_demo)
            print(f"-> Producto DEMO creado: ID={p_demo.id} SKU={p_demo.sku}")

            # Crear movimientos de Kardex para demostrar el Promedio Ponderado Móvil (DEC-010)
            now = datetime.now(timezone.utc)
            movs = [
                # 1. Entrada inicial: 10 unidades a $50.000 (Saldo: 10 u, Costo Promedio: $50.000, Total: $500.000)
                StockMovement(
                    product_id=p_demo.id,
                    date=now - timedelta(days=5),
                    movement_type=MovementType.ENTRY,
                    quantity=10,
                    unit_cost=Decimal("50000.00"),
                    reference_document="FAC-00101 (Compra inicial)",
                ),
                # 2. Segunda entrada a mayor costo: 10 unidades a $70.000
                # (Total invertido: $500.000 + $700.000 = $1.200.000 / 20 u -> Nuevo Costo Promedio: $60.000)
                StockMovement(
                    product_id=p_demo.id,
                    date=now - timedelta(days=3),
                    movement_type=MovementType.ENTRY,
                    quantity=10,
                    unit_cost=Decimal("70000.00"),
                    reference_document="FAC-00145 (Reposición)",
                ),
                # 3. Salida por venta: 5 unidades al costo promedio vigente ($60.000)
                # (Saldo: 15 unidades a $60.000 = $900.000)
                StockMovement(
                    product_id=p_demo.id,
                    date=now - timedelta(days=1),
                    movement_type=MovementType.EXIT,
                    quantity=5,
                    unit_cost=Decimal("60000.00"),
                    reference_document="GD-00890 (Despacho Cliente)",
                ),
            ]
            for m in movs:
                session.add(m)
            session.commit()
            print("-> 3 Movimientos de Kardex creados con Promedio Ponderado Móvil para el producto demo.")
        else:
            print(f"-> Producto DEMO ya existía (ID={p_demo.id}).")


if __name__ == "__main__":
    create_sample_excel_file("sample_products.xlsx")
    seed_database_for_demo()
