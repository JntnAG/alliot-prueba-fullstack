"use client";

interface TableSkeletonProps {
  rowCount?: number;
}

export function TableSkeleton({ rowCount = 8 }: TableSkeletonProps) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs animate-pulse">
      {/* Skeleton Desktop */}
      <div className="hidden md:block">
        <div className="border-b border-slate-200 bg-slate-50/75 py-3.5 px-6 flex justify-between">
          <div className="h-4 w-24 bg-slate-200 rounded" />
          <div className="h-4 w-48 bg-slate-200 rounded" />
          <div className="h-4 w-28 bg-slate-200 rounded" />
          <div className="h-4 w-20 bg-slate-200 rounded" />
        </div>
        <div className="divide-y divide-slate-100">
          {Array.from({ length: rowCount }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 py-3.5 px-6">
              <div className="h-12 w-12 rounded-xl bg-slate-200 shrink-0" />
              <div className="h-5 w-24 bg-slate-200 rounded" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-3/4 bg-slate-200 rounded" />
                <div className="h-3 w-1/2 bg-slate-100 rounded" />
              </div>
              <div className="h-6 w-28 bg-slate-200 rounded-full" />
              <div className="h-5 w-20 bg-slate-200 rounded" />
              <div className="h-6 w-20 bg-slate-200 rounded-full" />
            </div>
          ))}
        </div>
      </div>

      {/* Skeleton Mobile */}
      <div className="divide-y divide-slate-100 md:hidden p-4 space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3.5 pt-4 first:pt-0">
            <div className="h-14 w-14 rounded-xl bg-slate-200 shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 bg-slate-200 rounded" />
              <div className="h-3 w-1/3 bg-slate-200 rounded" />
              <div className="h-5 w-1/2 bg-slate-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface EmptyStateProps {
  onResetFilters?: () => void;
  message?: string;
}

export function EmptyState({
  onResetFilters,
  message = "No se encontraron productos con los filtros seleccionados.",
}: EmptyStateProps) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 mb-4">
        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
      </div>
      <h3 className="text-base font-bold text-slate-900 mb-1">
        Sin resultados
      </h3>
      <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
        {message}
      </p>
      {onResetFilters && (
        <button
          type="button"
          onClick={onResetFilters}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-blue-700 transition-colors"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Restablecer filtros
        </button>
      )}
    </div>
  );
}

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "No fue posible cargar los productos. Intenta nuevamente.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50/50 p-8 text-center shadow-xs">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 mb-4">
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h3 className="text-base font-bold text-rose-900 mb-1">
        Fallo al cargar catálogo
      </h3>
      <p className="text-sm text-rose-700 max-w-md mx-auto mb-6">
        {message}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-rose-700 transition-colors"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reintentar
        </button>
      )}
    </div>
  );
}
