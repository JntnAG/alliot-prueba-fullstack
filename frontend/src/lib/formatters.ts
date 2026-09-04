/**
 * lib/formatters.ts — Utilidades de formato para la interfaz
 * ==========================================================
 * Permite formatear precios monetarios en pesos chilenos / CLP y fechas legibles.
 */

/**
 * Formatea un número como moneda (ej: 89990 -> $89.990)
 */
export function formatCurrency(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined || amount === "") {
    return "$0";
  }

  const numeric = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(numeric)) {
    return "$0";
  }

  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(numeric);
}

/**
 * Formatea una fecha ISO a formato local chileno legible (DD/MM/AAAA HH:mm)
 */
export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return "-";
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return isoString;
  }
}
