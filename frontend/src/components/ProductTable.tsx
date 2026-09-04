"use client";

import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Product } from "@/types";
import { formatCurrency } from "@/lib/formatters";

interface ProductTableProps {
  products: Product[];
}

/**
 * Componente interno para renderizar la miniatura con soporte para fallback
 */
function ProductThumbnail({
  src,
  alt,
  size = 48,
}: {
  src?: string | null;
  alt: string;
  size?: number;
}) {
  const [hasError, setHasError] = useState(false);

  // Si no hay src o falló la carga, mostramos el placeholder SVG industrial
  if (!src || hasError) {
    return (
      <div
        style={{ width: size, height: size }}
        className="flex shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-400 border border-slate-200"
        title="Sin imagen disponible"
      >
        <svg
          className="h-5 w-5 text-slate-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
    );
  }

  return (
    <div
      style={{ width: size, height: size }}
      className="relative shrink-0 overflow-hidden rounded-xl border border-slate-200 bg-white"
    >
      <Image
        src={src}
        alt={alt}
        fill
        sizes={`${size}px`}
        className="object-cover transition-transform duration-200 group-hover:scale-105"
        onError={() => setHasError(true)}
      />
    </div>
  );
}

/**
 * Insignia de estado de stock (Agotado / Bajo Stock / Disponible)
 */
function StockBadge({ stock }: { stock: number }) {
  if (stock <= 0) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700 border border-rose-200/60">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-600" />
        Agotado (0)
      </span>
    );
  }

  if (stock <= 5) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 border border-amber-200/60">
        <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
        Bajo stock ({stock})
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200/60">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-600" />
      {stock} unid.
    </span>
  );
}

export default function ProductTable({ products }: ProductTableProps) {
  const router = useRouter();

  const handleRowClick = (productId: number) => {
    router.push(`/products/${productId}`);
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
      {/* Vista de Tabla Desktop (pantallas medianas y grandes) */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/75 text-xs font-bold uppercase tracking-wider text-slate-500">
              <th scope="col" className="py-3.5 pl-6 pr-3 w-16 text-center">
                Img
              </th>
              <th scope="col" className="py-3.5 px-4">
                SKU
              </th>
              <th scope="col" className="py-3.5 px-4">
                Nombre del Producto
              </th>
              <th scope="col" className="py-3.5 px-4">
                Categoría
              </th>
              <th scope="col" className="py-3.5 px-4 text-right">
                Precio
              </th>
              <th scope="col" className="py-3.5 px-4 text-center">
                Stock
              </th>
              <th scope="col" className="py-3.5 pl-3 pr-6 text-right w-16">
                <span className="sr-only">Acción</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {products.map((product) => (
              <tr
                key={product.id}
                onClick={() => handleRowClick(product.id)}
                className="group cursor-pointer transition-colors hover:bg-blue-50/50"
                tabIndex={0}
                role="link"
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handleRowClick(product.id);
                  }
                }}
              >
                {/* Miniatura */}
                <td className="py-3.5 pl-6 pr-3 text-center">
                  <ProductThumbnail src={product.imagen_url} alt={product.nombre} size={48} />
                </td>

                {/* SKU */}
                <td className="py-3.5 px-4 font-mono text-xs font-semibold text-slate-700">
                  <span className="rounded-md bg-slate-100 px-2 py-1 border border-slate-200">
                    {product.sku}
                  </span>
                </td>

                {/* Nombre y descripción corta */}
                <td className="py-3.5 px-4">
                  <div className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {product.nombre}
                  </div>
                  {product.descripcion && (
                    <div className="text-xs text-slate-500 line-clamp-1 mt-0.5">
                      {product.descripcion}
                    </div>
                  )}
                </td>

                {/* Categoría */}
                <td className="py-3.5 px-4">
                  <span className="inline-flex items-center rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                    {product.categoria}
                  </span>
                </td>

                {/* Precio */}
                <td className="py-3.5 px-4 text-right font-bold text-slate-900">
                  {formatCurrency(product.precio)}
                </td>

                {/* Stock */}
                <td className="py-3.5 px-4 text-center">
                  <StockBadge stock={product.stock} />
                </td>

                {/* Flecha de navegación visual */}
                <td className="py-3.5 pl-3 pr-6 text-right text-slate-400 group-hover:text-blue-600 transition-colors">
                  <svg
                    className="inline-block h-5 w-5 transition-transform group-hover:translate-x-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Vista Mobile / Responsive (pantallas pequeñas sin scroll horizontal incómodo) */}
      <div className="divide-y divide-slate-100 md:hidden">
        {products.map((product) => (
          <div
            key={product.id}
            onClick={() => handleRowClick(product.id)}
            className="group flex items-center gap-3.5 p-4 cursor-pointer hover:bg-blue-50/50 transition-colors active:bg-blue-100/50"
          >
            {/* Miniatura */}
            <ProductThumbnail src={product.imagen_url} alt={product.nombre} size={56} />

            {/* Información principal */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs font-semibold text-slate-600 rounded bg-slate-100 px-1.5 py-0.5">
                  {product.sku}
                </span>
                <span className="text-xs text-slate-500 truncate">
                  {product.categoria}
                </span>
              </div>

              <h3 className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 truncate transition-colors">
                {product.nombre}
              </h3>

              <div className="mt-2 flex items-center justify-between">
                <span className="text-base font-bold text-slate-900">
                  {formatCurrency(product.precio)}
                </span>
                <StockBadge stock={product.stock} />
              </div>
            </div>

            {/* Indicador de flecha */}
            <div className="text-slate-400 group-hover:text-blue-600">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
