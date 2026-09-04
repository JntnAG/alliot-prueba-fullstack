/**
 * types/kardex.ts — Tipos y contratos para Kardex de inventario valorizado
 * =======================================================================
 * Alineados estrictamente con schemas/kardex.py y DECISIONES.md (DEC-009, DEC-010, DEC-011).
 * Implementa el cálculo de valorización por Promedio Ponderado Móvil.
 */

export type MovementType = "ENTRY" | "EXIT";

export interface KardexLine {
  id: number;
  fecha: string; // ISO datetime string
  tipo: MovementType;
  cantidad: number;
  costo_unitario: number;
  documento_referencia: string;

  // Saldos acumulados recalculados tras cada movimiento
  saldo_unidades: number;
  costo_promedio: number;
  saldo_valorizado: number;
}

export interface ProductKardexResponse {
  product_id: number;
  sku: string;
  nombre: string;
  saldo_total_unidades: number;
  costo_promedio_actual: number;
  saldo_total_valorizado: number;
  movimientos: KardexLine[];
}
