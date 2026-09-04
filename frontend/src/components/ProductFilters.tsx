"use client";

import { useState, useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ProductSortField, SortDirection } from "@/types";

const CATEGORIES = [
  "Herramientas Eléctricas",
  "Protección Personal",
  "Fijaciones y Tornillería",
  "Medición y Trazado",
  "Pinturas y Químicos",
  "Seguridad Industrial",
];

interface ProductFiltersProps {
  totalResults?: number;
  isLoading?: boolean;
}

export default function ProductFilters({
  totalResults,
  isLoading = false,
}: ProductFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();

  // Estados locales inicializados desde los query params de la URL
  const [q, setQ] = useState(searchParams.get("q") || "");
  const [categoria, setCategoria] = useState(searchParams.get("categoria") || "");
  const [precioMin, setPrecioMin] = useState(searchParams.get("precio_min") || "");
  const [precioMax, setPrecioMax] = useState(searchParams.get("precio_max") || "");
  const [orderBy, setOrderBy] = useState<ProductSortField>(
    (searchParams.get("order_by") as ProductSortField) || "nombre"
  );
  const [orderDir, setOrderDir] = useState<SortDirection>(
    (searchParams.get("order_dir") as SortDirection) || "asc"
  );


  /**
   * Actualiza la URL aplicando los filtros seleccionados y reseteando a la página 1.
   */
  const applyFilters = (overrides?: {
    q?: string;
    categoria?: string;
    precio_min?: string;
    precio_max?: string;
    order_by?: ProductSortField;
    order_dir?: SortDirection;
  }) => {
    const nextQ = overrides?.q !== undefined ? overrides.q : q;
    const nextCat = overrides?.categoria !== undefined ? overrides.categoria : categoria;
    const nextMin = overrides?.precio_min !== undefined ? overrides.precio_min : precioMin;
    const nextMax = overrides?.precio_max !== undefined ? overrides.precio_max : precioMax;
    const nextOrderBy = overrides?.order_by !== undefined ? overrides.order_by : orderBy;
    const nextOrderDir = overrides?.order_dir !== undefined ? overrides.order_dir : orderDir;

    const params = new URLSearchParams();

    if (nextQ.trim()) params.set("q", nextQ.trim());
    if (nextCat.trim()) params.set("categoria", nextCat.trim());
    if (nextMin.trim()) params.set("precio_min", nextMin.trim());
    if (nextMax.trim()) params.set("precio_max", nextMax.trim());
    if (nextOrderBy && nextOrderBy !== "nombre") params.set("order_by", nextOrderBy);
    if (nextOrderDir && nextOrderDir !== "asc") params.set("order_dir", nextOrderDir);

    // Al cambiar cualquier filtro volvemos a la página 1
    params.set("page", "1");

    const pageSize = searchParams.get("page_size");
    if (pageSize) params.set("page_size", pageSize);

    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`);
    });
  };

  /**
   * Manejador del formulario de búsqueda
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    applyFilters();
  };

  /**
   * Limpia todos los filtros y resetea a los valores por defecto
   */
  const handleClearFilters = () => {
    setQ("");
    setCategoria("");
    setPrecioMin("");
    setPrecioMax("");
    setOrderBy("nombre");
    setOrderDir("asc");

    startTransition(() => {
      router.push(pathname);
    });
  };

  const hasActiveFilters = Boolean(
    q || categoria || precioMin || precioMax || (orderBy && orderBy !== "nombre") || orderDir !== "asc"
  );

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs mb-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Fila superior: Búsqueda y Categoría */}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-12">
          {/* Barra de búsqueda por texto */}
          <div className="relative md:col-span-7">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <input
              id="search-input"
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Buscar por nombre o SKU (ej: taladro, HER-ELE-001)..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50/50 py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
            />
          </div>

          {/* Filtro por Categoría */}
          <div className="md:col-span-5">
            <select
              id="category-select"
              value={categoria}
              onChange={(e) => {
                const newCat = e.target.value;
                setCategoria(newCat);
                applyFilters({ categoria: newCat });
              }}
              className="w-full rounded-xl border border-slate-300 bg-slate-50/50 py-2.5 px-3.5 text-sm text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
            >
              <option value="">Todas las categorías</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Fila inferior: Rango de precios, ordenamiento y acciones */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-12 items-center">
          {/* Precio Mínimo */}
          <div className="lg:col-span-3">
            <div className="relative">
              <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-xs font-semibold text-slate-400">
                $ Min
              </span>
              <input
                id="price-min-input"
                type="number"
                min="0"
                step="100"
                value={precioMin}
                onChange={(e) => setPrecioMin(e.target.value)}
                placeholder="0"
                className="w-full rounded-xl border border-slate-300 bg-slate-50/50 py-2 pl-14 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>
          </div>

          {/* Precio Máximo */}
          <div className="lg:col-span-3">
            <div className="relative">
              <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-xs font-semibold text-slate-400">
                $ Max
              </span>
              <input
                id="price-max-input"
                type="number"
                min="0"
                step="100"
                value={precioMax}
                onChange={(e) => setPrecioMax(e.target.value)}
                placeholder="500.000"
                className="w-full rounded-xl border border-slate-300 bg-slate-50/50 py-2 pl-14 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>
          </div>

          {/* Ordenamiento */}
          <div className="lg:col-span-3 flex gap-2">
            <select
              id="order-by-select"
              value={orderBy}
              onChange={(e) => {
                const newField = e.target.value as ProductSortField;
                setOrderBy(newField);
                applyFilters({ order_by: newField });
              }}
              className="w-full rounded-xl border border-slate-300 bg-slate-50/50 py-2 px-3 text-xs text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
            >
              <option value="nombre">Ordenar por Nombre</option>
              <option value="precio">Ordenar por Precio</option>
              <option value="sku">Ordenar por SKU</option>
              <option value="categoria">Ordenar por Categoría</option>
            </select>

            <button
              type="button"
              id="order-dir-btn"
              title={`Dirección: ${orderDir === "asc" ? "Ascendente" : "Descendente"}`}
              onClick={() => {
                const nextDir = orderDir === "asc" ? "desc" : "asc";
                setOrderDir(nextDir);
                applyFilters({ order_dir: nextDir });
              }}
              className="flex items-center justify-center rounded-xl border border-slate-300 bg-slate-50 px-2.5 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors"
            >
              {orderDir === "asc" ? (
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                </svg>
              ) : (
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
                </svg>
              )}
            </button>
          </div>

          {/* Botones de acción */}
          <div className="lg:col-span-3 flex items-center justify-end gap-2">
            <button
              type="submit"
              disabled={isLoading}
              id="apply-filters-btn"
              className="flex-1 sm:flex-initial rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 transition-all"
            >
              Filtrar
            </button>

            {hasActiveFilters && (
              <button
                type="button"
                onClick={handleClearFilters}
                id="clear-filters-btn"
                className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                Limpiar
              </button>
            )}
          </div>
        </div>

        {/* Resumen de resultados activos */}
        {totalResults !== undefined && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
            <span>
              {isLoading ? (
                "Buscando productos..."
              ) : (
                <>
                  Se encontraron <strong className="text-slate-800 font-semibold">{totalResults}</strong> producto{totalResults === 1 ? "" : "s"}
                  {hasActiveFilters && " con los filtros aplicados"}
                </>
              )}
            </span>

            {hasActiveFilters && (
              <span className="inline-flex items-center gap-1.5 text-blue-600 font-medium">
                <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                Filtros activos
              </span>
            )}
          </div>
        )}
      </form>
    </div>
  );
}
