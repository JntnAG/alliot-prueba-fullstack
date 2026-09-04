/**
 * types/product.ts — Tipos y contratos para Productos
 * ====================================================
 * Alineados estrictamente con el backend de FastAPI (schemas/product.py y models/product.py),
 * las especificaciones del PDF (Sección 3.1, 3.2 y Anexo 8) y DECISIONES.md (DEC-003 y DEC-004).
 */

export interface Product {
  id: number;
  sku: string;
  nombre: string;
  descripcion?: string | null;
  categoria: string;
  precio: number;
  stock: number;
  imagen_url?: string | null;
}

/**
 * Respuesta paginada devuelta por GET /products
 */
export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Campos permitidos para ordenamiento en el servidor (Patrón Criteria)
 */
export type ProductSortField = "nombre" | "sku" | "categoria" | "precio";

/**
 * Dirección del ordenamiento
 */
export type SortDirection = "asc" | "desc";

/**
 * Parámetros de consulta aceptados por el endpoint GET /products
 */
export interface ProductQueryParams {
  q?: string;
  categoria?: string;
  precio_min?: number | string;
  precio_max?: number | string;
  page?: number;
  page_size?: number;
  order_by?: ProductSortField;
  order_dir?: SortDirection;
}
