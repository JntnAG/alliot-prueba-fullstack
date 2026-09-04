/**
 * types/import.ts — Tipos y contratos para Importación masiva desde Excel
 * =======================================================================
 * Alineados con schemas/import_result.py, Sección 4.2 del PDF y DECISIONES.md (DEC-008).
 */

export interface RowError {
  fila: number;
  campo: string;
  motivo: string;
}

export interface ImportResult {
  leidas: number;
  insertadas: number;
  actualizadas: number;
  rechazadas: number;
  errores: RowError[];
}
