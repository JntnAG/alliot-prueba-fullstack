/**
 * types/api.ts — Tipos auxiliares para respuestas y errores HTTP de la API
 * =======================================================================
 */

export interface ValidationErrorItem {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ApiErrorPayload {
  detail?: string | ValidationErrorItem[];
  message?: string;
}

export class ApiError extends Error {
  status: number;
  payload?: ApiErrorPayload;

  constructor(status: number, message: string, payload?: ApiErrorPayload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}
