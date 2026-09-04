import { describe, expect, test } from "bun:test";
import { api } from "./api";
import { ApiError } from "@/types";

describe("API Client & Types Verification", () => {
  test("api object has all required endpoints and functions", () => {
    expect(typeof api.getProducts).toBe("function");
    expect(typeof api.getProductById).toBe("function");
    expect(typeof api.getProductKardex).toBe("function");
    expect(typeof api.importProductsExcel).toBe("function");
    expect(typeof api.checkHealth).toBe("function");
  });

  test("ApiError formats error messages properly", () => {
    const error = new ApiError(404, "Producto con ID 999 no encontrado.", {
      detail: "Producto con ID 999 no encontrado.",
    });
    expect(error.status).toBe(404);
    expect(error.message).toBe("Producto con ID 999 no encontrado.");
    expect(error.name).toBe("ApiError");
  });
});
