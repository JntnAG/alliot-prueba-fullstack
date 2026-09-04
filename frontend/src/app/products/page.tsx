"use client";

import { Suspense, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import {
  ProductListResponse,
  ProductQueryParams,
  ProductSortField,
  SortDirection,
} from "@/types";
import ProductFilters from "@/components/ProductFilters";
import ProductTable from "@/components/ProductTable";
import Pagination from "@/components/Pagination";
import { EmptyState, ErrorState, TableSkeleton } from "@/components/TableStates";

function ProductsContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [data, setData] = useState<ProductListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [retryCounter, setRetryCounter] = useState(0);

  // Parámetros leídos de la URL
  const q = searchParams.get("q") || undefined;
  const categoria = searchParams.get("categoria") || undefined;
  const precioMin = searchParams.get("precio_min") || undefined;
  const precioMax = searchParams.get("precio_max") || undefined;
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "20", 10);
  const orderBy = (searchParams.get("order_by") as ProductSortField) || "nombre";
  const orderDir = (searchParams.get("order_dir") as SortDirection) || "asc";

  useEffect(() => {
    let isMounted = true;

    const queryParams: ProductQueryParams = {
      q,
      categoria,
      precio_min: precioMin,
      precio_max: precioMax,
      page,
      page_size: pageSize,
      order_by: orderBy,
      order_dir: orderDir,
    };

    api
      .getProducts(queryParams)
      .then((response) => {
        if (isMounted) {
          setData(response);
          setErrorMessage(null);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          const message =
            err instanceof Error
              ? err.message
              : "No fue posible conectar con el servidor backend. Asegúrate de que FastAPI esté ejecutándose.";
          setErrorMessage(message);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [q, categoria, precioMin, precioMax, page, pageSize, orderBy, orderDir, retryCounter]);

  const handleRetry = () => {
    setLoading(true);
    setErrorMessage(null);
    setRetryCounter((prev) => prev + 1);
  };

  const handleResetFilters = () => {
    router.push(pathname);
  };

  return (
    <div className="space-y-6">
      {/* Encabezado de la página */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-slate-900 sm:text-3xl">
            Catálogo de Productos
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Explora el inventario industrial, filtra por especificaciones y consulta el Kardex de cada producto.
          </p>
        </div>
      </div>

      {/* Barra de búsqueda y filtros sincronizada por key */}
      <ProductFilters
        key={searchParams.toString()}
        totalResults={data?.total}
        isLoading={loading}
      />

      {/* Estados principales de la vista */}
      {errorMessage ? (
        <ErrorState message={errorMessage} onRetry={handleRetry} />
      ) : loading ? (
        <TableSkeleton rowCount={pageSize > 10 ? 8 : pageSize} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState onResetFilters={handleResetFilters} />
      ) : (
        <div className="space-y-4">
          <ProductTable products={data.items} />

          <Pagination
            currentPage={data.page}
            pageSize={data.page_size}
            totalItems={data.total}
          />
        </div>
      )}
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          <div className="h-16 w-64 rounded-xl bg-slate-100 animate-pulse" />
          <TableSkeleton rowCount={8} />
        </div>
      }
    >
      <ProductsContent />
    </Suspense>
  );
}
