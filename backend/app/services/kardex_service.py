"""
services/kardex_service.py — Servicio de Cálculo y Consulta de Kardex Valorizado
================================================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Imagina que eres el contador de una ferretería:
1. El lunes compraste 10 taladros a $50.000 c/u.
   - Tienes 10 taladros por un valor de $500.000. Tu costo promedio es $50.000.
2. El martes compraste 10 taladros más caros, a $70.000 c/u.
   - Ahora tienes 20 taladros en total.
   - ¿Cuánto dinero tienes invertido? $500.000 + $700.000 = $1.200.000.
   - ¿Cuál es tu costo promedio por taladro? $1.200.000 / 20 = $60.000. (Promedio Ponderado Móvil).
3. El miércoles vendes 5 taladros:
   - Los vendes sabiendo que te costaron en promedio $60.000 c/u.
   - Te quedan 15 taladros. Tu valor total es 15 * $60.000 = $900.000.
   - Tu costo promedio sigue siendo $60.000. Las salidas NO cambian el costo promedio.

Este archivo contiene:
1. `calculate_kardex`: Una función PURA (no usa base de datos ni internet), lo que permite
   probarla con tests unitarios en microsegundos (Decisión [DEC-011]).
2. `get_kardex_for_product`: Consulta la base de datos, ordena los movimientos en el tiempo
   y retorna el reporte completo `ProductKardexResponse`.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from sqlmodel import Session, select

from app.models.product import Product
from app.models.stock_movement import MovementType, StockMovement
from app.schemas.kardex import KardexLine, ProductKardexResponse


def _round_currency(value: Decimal) -> Decimal:
    """Redondea valores monetarios a 2 decimales según estándar contable."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_kardex(movements: List[StockMovement]) -> List[KardexLine]:
    """
    Función pura que toma una lista de movimientos cronológicos y calcula
    el historial de saldos en unidades y valorización contable usando
    el método de Promedio Ponderado Móvil (DEC-010 y DEC-011).
    """
    # Ordenar estrictamente por fecha y luego por id para reproducibilidad
    sorted_movements = sorted(movements, key=lambda m: (m.date, m.id or 0))

    kardex_lines: List[KardexLine] = []
    current_units: int = 0
    current_avg_cost: Decimal = Decimal("0.00")
    current_total_value: Decimal = Decimal("0.00")

    for mov in sorted_movements:
        qty = mov.quantity
        unit_cost = mov.unit_cost

        if mov.movement_type == MovementType.ENTRY:
            # ── ENTRADA (COMPRA): Aumenta stock y recalcula costo promedio ponderado
            entry_value = Decimal(str(qty)) * unit_cost
            new_units = current_units + qty
            new_total_value = current_total_value + entry_value

            if new_units > 0:
                new_avg_cost = new_total_value / Decimal(str(new_units))
            else:
                new_avg_cost = Decimal("0.00")

            current_units = new_units
            current_avg_cost = new_avg_cost
            current_total_value = new_total_value

            kardex_lines.append(
                KardexLine(
                    id=mov.id or 0,
                    fecha=mov.date,
                    tipo=mov.movement_type,
                    cantidad=qty,
                    costo_unitario=_round_currency(unit_cost),
                    documento_referencia=mov.reference_document,
                    saldo_unidades=current_units,
                    costo_promedio=_round_currency(current_avg_cost),
                    saldo_valorizado=_round_currency(current_total_value),
                )
            )

        elif mov.movement_type == MovementType.EXIT:
            # ── SALIDA (VENTA / DESPACHO):
            # Se valoriza al costo promedio vigente sin alterar el costo unitario promedio
            exit_cost_unit = current_avg_cost
            new_units = max(0, current_units - qty)
            new_total_value = Decimal(str(new_units)) * exit_cost_unit

            current_units = new_units
            current_total_value = new_total_value

            kardex_lines.append(
                KardexLine(
                    id=mov.id or 0,
                    fecha=mov.date,
                    tipo=mov.movement_type,
                    cantidad=qty,
                    costo_unitario=_round_currency(exit_cost_unit),
                    documento_referencia=mov.reference_document,
                    saldo_unidades=current_units,
                    costo_promedio=_round_currency(current_avg_cost),
                    saldo_valorizado=_round_currency(current_total_value),
                )
            )

    return kardex_lines


class KardexService:
    """
    Servicio para la consulta y cálculo del Kardex de un producto.
    """

    @classmethod
    def get_kardex_for_product(cls, session: Session, product_id: int) -> Optional[ProductKardexResponse]:
        """
        Obtiene todos los movimientos del producto desde la BD, calcula la cartola
        completa del Kardex y devuelve el resumen del producto con su historial valorizado.
        Retorna None si el producto no existe en la base de datos (para responder 404).
        """
        product = session.get(Product, product_id)
        if not product:
            return None

        # Obtener todos los movimientos del producto ordenados cronológicamente
        statement = (
            select(StockMovement)
            .where(StockMovement.product_id == product_id)
            .order_by(StockMovement.date.asc(), StockMovement.id.asc())
        )
        movements = list(session.exec(statement).all())

        # Calcular las líneas valorizadas usando la función pura
        kardex_lines = calculate_kardex(movements)

        if kardex_lines:
            latest = kardex_lines[-1]
            saldo_total_unidades = latest.saldo_unidades
            costo_promedio_actual = latest.costo_promedio
            saldo_total_valorizado = latest.saldo_valorizado
        else:
            saldo_total_unidades = product.stock
            costo_promedio_actual = Decimal("0.00")
            saldo_total_valorizado = Decimal("0.00")

        return ProductKardexResponse(
            product_id=product.id,
            sku=product.sku,
            nombre=product.nombre,
            saldo_total_unidades=saldo_total_unidades,
            costo_promedio_actual=costo_promedio_actual,
            saldo_total_valorizado=saldo_total_valorizado,
            movimientos=kardex_lines,
        )


__all__ = [
    "calculate_kardex",
    "KardexService",
]
