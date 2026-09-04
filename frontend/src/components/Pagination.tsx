"use client";

import { useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

interface PaginationProps {
  currentPage: number;
  pageSize: number;
  totalItems: number;
}

export default function Pagination({
  currentPage,
  pageSize,
  totalItems,
}: PaginationProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  // Si no hay items o solo hay 1 página de pocos elementos, igual mostramos el contador
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  /**
   * Cambia de página preservando todos los demás query params existentes
   */
  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages || newPage === currentPage) return;

    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(newPage));

    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`);
    });
  };

  /**
   * Cambia el tamaño de página preservando los filtros y reseteando a página 1
   */
  const handlePageSizeChange = (newSize: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page_size", String(newSize));
    params.set("page", "1");

    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`);
    });
  };

  /**
   * Genera los números de página visibles con elipsis para evitar exceso de botones
   */
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, "...", totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1, "...", totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between py-4 px-1 text-sm text-slate-600">
      {/* Información del rango de productos mostrados */}
      <div className="flex items-center gap-3">
        <p>
          Mostrando <strong className="font-semibold text-slate-800">{startItem}</strong> a{" "}
          <strong className="font-semibold text-slate-800">{endItem}</strong> de{" "}
          <strong className="font-semibold text-slate-800">{totalItems}</strong> productos
        </p>

        {/* Selector de items por página */}
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 pl-3 border-l border-slate-200">
          <span>Por pág:</span>
          <select
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            className="rounded-lg border border-slate-200 bg-white py-1 px-2 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Controles de paginación */}
      <div className="flex items-center gap-1 self-center sm:self-auto">
        {/* Botón Anterior */}
        <button
          type="button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          aria-label="Página anterior"
          className="flex h-9 items-center justify-center gap-1 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="hidden sm:inline">Anterior</span>
        </button>

        {/* Números de página */}
        <div className="flex items-center gap-1">
          {getPageNumbers().map((p, idx) =>
            typeof p === "number" ? (
              <button
                key={idx}
                type="button"
                onClick={() => handlePageChange(p)}
                aria-current={p === currentPage ? "page" : undefined}
                className={`flex h-9 w-9 items-center justify-center rounded-xl text-xs font-semibold transition-all ${
                  p === currentPage
                    ? "bg-blue-600 text-white shadow-xs font-bold"
                    : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                {p}
              </button>
            ) : (
              <span key={idx} className="flex h-9 w-6 items-center justify-center text-slate-400">
                {p}
              </span>
            )
          )}
        </div>

        {/* Botón Siguiente */}
        <button
          type="button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          aria-label="Página siguiente"
          className="flex h-9 items-center justify-center gap-1 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <span className="hidden sm:inline">Siguiente</span>
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
