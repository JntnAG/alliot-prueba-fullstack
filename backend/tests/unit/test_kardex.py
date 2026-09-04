from datetime import datetime
from decimal import Decimal

from app.models.stock_movement import MovementType, StockMovement
from app.services.kardex_service import calculate_kardex


def test_entrada_inicial_y_calculo_saldo_inicial():
    movs = [
        StockMovement(
            id=1,
            product_id=1,
            date=datetime(2023, 1, 1),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("50.00"),
            reference_document="FAC-001"
        )
    ]

    lines = calculate_kardex(movs)

    assert len(lines) == 1
    assert lines[0].saldo_unidades == 10
    assert lines[0].costo_promedio == Decimal("50.00")
    assert lines[0].saldo_valorizado == Decimal("500.00")


def test_multiples_entradas_a_costos_distintos_y_recalculo_promedio():
    movs = [
        StockMovement(
            id=1,
            product_id=1,
            date=datetime(2023, 1, 1),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("50.00"),
            reference_document="FAC-001"
        ),
        StockMovement(
            id=2,
            product_id=1,
            date=datetime(2023, 1, 2),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("70.00"),
            reference_document="FAC-002"
        )
    ]

    lines = calculate_kardex(movs)

    assert len(lines) == 2
    # Línea 1
    assert lines[0].saldo_unidades == 10
    assert lines[0].costo_promedio == Decimal("50.00")
    assert lines[0].saldo_valorizado == Decimal("500.00")
    
    # Línea 2
    assert lines[1].saldo_unidades == 20
    assert lines[1].costo_promedio == Decimal("60.00")
    assert lines[1].saldo_valorizado == Decimal("1200.00")


def test_salida_existencias_y_mantener_costo_promedio():
    movs = [
        StockMovement(
            id=1,
            product_id=1,
            date=datetime(2023, 1, 1),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("50.00"),
            reference_document="FAC-001"
        ),
        StockMovement(
            id=2,
            product_id=1,
            date=datetime(2023, 1, 2),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("70.00"),
            reference_document="FAC-002"
        ),
        StockMovement(
            id=3,
            product_id=1,
            date=datetime(2023, 1, 3),
            movement_type=MovementType.EXIT,
            quantity=5,
            unit_cost=Decimal("0.00"), # El costo en salida se ignora/recalcula por el kardex
            reference_document="VEN-001"
        )
    ]

    lines = calculate_kardex(movs)

    assert len(lines) == 3
    # Línea 3 (Salida)
    assert lines[2].cantidad == 5
    assert lines[2].tipo == MovementType.EXIT
    assert lines[2].costo_unitario == Decimal("60.00")  # Usa el costo promedio anterior
    assert lines[2].costo_promedio == Decimal("60.00")  # Mantiene el costo promedio
    assert lines[2].saldo_unidades == 15                # 20 - 5
    assert lines[2].saldo_valorizado == Decimal("900.00") # 15 * 60


def test_comportamiento_ante_stock_insuficiente():
    movs = [
        StockMovement(
            id=1,
            product_id=1,
            date=datetime(2023, 1, 1),
            movement_type=MovementType.ENTRY,
            quantity=10,
            unit_cost=Decimal("50.00"),
            reference_document="FAC-001"
        ),
        StockMovement(
            id=2,
            product_id=1,
            date=datetime(2023, 1, 2),
            movement_type=MovementType.EXIT,
            quantity=15, # Intenta sacar más de lo que hay
            unit_cost=Decimal("0.00"),
            reference_document="VEN-001"
        )
    ]

    lines = calculate_kardex(movs)

    assert len(lines) == 2
    # Línea 2
    assert lines[1].cantidad == 15
    assert lines[1].saldo_unidades == 0  # No debería bajar de 0
    assert lines[1].costo_promedio == Decimal("50.00")
    assert lines[1].saldo_valorizado == Decimal("0.00")
