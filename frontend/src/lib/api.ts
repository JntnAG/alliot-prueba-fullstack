/**
 * lib/api.ts — Cliente HTTP centralizado para comunicación con la API de FastAPI
 * ==============================================================================
 * 
 * Cumple con:
 * - DECISIONES.md: [DEC-004], [DEC-007], [DEC-008], [DEC-010]
 * - Prueba técnica PDF: Sección 3.2, 3.3, 4.1, 4.2, 4.4 y Anexo 8
 * 
 * Características principales:
 * 1. Base URL configurable mediante NEXT_PUBLIC_API_URL con fallback a http://localhost:8000.
 * 2. Manejo exhaustivo y tipado de errores (códigos 404, 422, 500 y fallo de red).
 * 3. Parámetros de consulta limpios y formateados para el Patrón Criteria del backend.
 * 4. Métodos para catálogo paginado, detalle de producto, Kardex e importación de Excel.
 */

import {
  ApiError,
  ApiErrorPayload,
  ImportResult,
  Product,
  ProductKardexResponse,
  ProductListResponse,
  ProductQueryParams,
  ValidationErrorItem,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://localhost:8000";

/**
 * Parsea el cuerpo de error devuelto por FastAPI y genera un mensaje legible.
 */
function extractErrorMessage(status: number, payload?: ApiErrorPayload): string {
  if (!payload) {
    if (status === 404) return "El recurso solicitado no fue encontrado.";
    if (status === 500) return "Error interno en el servidor. Intenta nuevamente más tarde.";
    return `Error en la solicitud (Código HTTP ${status}).`;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload.detail)) {
    // FastAPI retorna 422 como lista de validaciones: [{ loc, msg, type }]
    const messages = (payload.detail as ValidationErrorItem[]).map((err) => {
      const field = err.loc[err.loc.length - 1] ?? "parámetro";
      return `${field}: ${err.msg}`;
    });
    return messages.join(", ");
  }

  if (payload.message) {
    return payload.message;
  }

  return `Error en la solicitud (Código HTTP ${status}).`;
}

/**
 * Función base para peticiones HTTP con manejo de errores de red y parseo tipado.
 */
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new ApiError(
      0,
      `No fue posible conectar con el servidor backend en ${API_BASE_URL}. Asegúrate de que el servicio esté ejecutándose.`
    );
  }

  if (!response.ok) {
    let errorPayload: ApiErrorPayload | undefined;
    try {
      errorPayload = await response.json();
    } catch {
      // La respuesta no era JSON
    }

    const message = extractErrorMessage(response.status, errorPayload);
    throw new ApiError(response.status, message, errorPayload);
  }

  return (await response.json()) as T;
}

/**
 * Construye los query parameters compatibles con el Patrón Criteria de FastAPI.
 */
function buildProductsQueryString(params?: ProductQueryParams): string {
  if (!params) return "";

  const query = new URLSearchParams();

  if (params.q !== undefined && params.q !== null && params.q.trim() !== "") {
    query.set("q", params.q.trim());
  }

  if (
    params.categoria !== undefined &&
    params.categoria !== null &&
    params.categoria.trim() !== ""
  ) {
    query.set("categoria", params.categoria.trim());
  }

  if (params.precio_min !== undefined && params.precio_min !== null && params.precio_min !== "") {
    query.set("precio_min", String(params.precio_min));
  }

  if (params.precio_max !== undefined && params.precio_max !== null && params.precio_max !== "") {
    query.set("precio_max", String(params.precio_max));
  }

  if (params.page !== undefined && params.page !== null) {
    query.set("page", String(params.page));
  }

  if (params.page_size !== undefined && params.page_size !== null) {
    query.set("page_size", String(params.page_size));
  }

  if (params.order_by !== undefined && params.order_by !== null) {
    query.set("order_by", params.order_by);
  }

  if (params.order_dir !== undefined && params.order_dir !== null) {
    query.set("order_dir", params.order_dir);
  }

  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

/**
 * Cliente de API con todos los métodos de catálogo, Kardex e importación
 */
export const api = {
  /**
   * Obtiene el listado paginado de productos aplicando filtros y ordenamiento en el servidor.
   * Endpoint: GET /products
   */
  async getProducts(params?: ProductQueryParams): Promise<ProductListResponse> {
    const qs = buildProductsQueryString(params);
    return request<ProductListResponse>(`/products${qs}`, {
      cache: "no-store",
    });
  },

  /**
   * Obtiene la ficha de detalle de un producto por su ID.
   * Endpoint: GET /products/{id}
   */
  async getProductById(id: number | string): Promise<Product> {
    return request<Product>(`/products/${id}`, {
      cache: "no-store",
    });
  },

  /**
   * Obtiene el historial de Kardex y valorización por Promedio Ponderado Móvil de un producto.
   * Endpoint: GET /products/{id}/kardex
   */
  async getProductKardex(id: number | string): Promise<ProductKardexResponse> {
    return request<ProductKardexResponse>(`/products/${id}/kardex`, {
      cache: "no-store",
    });
  },

  /**
   * Sube un archivo Excel (.xlsx) para procesar importación masiva con resiliencia parcial.
   * Endpoint: POST /products/import
   */
  async importProductsExcel(file: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append("file", file);

    const url = `${API_BASE_URL}/products/import`;

    let response: Response;
    try {
      response = await fetch(url, {
        method: "POST",
        body: formData,
        // No configuramos Content-Type manual para que el navegador establezca el boundary correcto
      });
    } catch {
      throw new ApiError(
        0,
        `No fue posible conectar con el servidor backend en ${API_BASE_URL} para la importación.`
      );
    }

    if (!response.ok) {
      let errorPayload: ApiErrorPayload | undefined;
      try {
        errorPayload = await response.json();
      } catch {
        // La respuesta no era JSON
      }

      const message = extractErrorMessage(response.status, errorPayload);
      throw new ApiError(response.status, message, errorPayload);
    }

    return (await response.json()) as ImportResult;
  },

  /**
   * Verifica la disponibilidad del backend.
   * Endpoint: GET /health
   */
  async checkHealth(): Promise<{ status: string }> {
    return request<{ status: string }>("/health");
  },
};

export default api;
