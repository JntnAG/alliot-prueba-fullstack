"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { ApiError, Product, ProductKardexResponse } from "@/types";
import { formatCurrency } from "@/lib/formatters";
import KardexTable from "@/components/KardexTable";

/**
 * Componente para renderizar la imagen destacada con placeholder y fallback
 */
function ProductDetailImage({
  src,
  alt,
}: {
  src?: string | null;
  alt: string;
}) {
  const [hasError, setHasError] = useState(false);

  if (!src || hasError) {
    return (
      <div className="flex aspect-square w-full items-center justify-center rounded-3xl border border-slate-200 bg-slate-100/75 text-slate-400 p-8 shadow-xs">
        <div className="text-center">
          <svg
            className="mx-auto h-20 w-20 text-slate-300"
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
          <p className="mt-3 text-xs font-medium text-slate-400">
            Fotografía no disponible
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative aspect-square w-full overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xs group">
      <Image
        src={src}
        alt={alt}
        fill
        priority
        sizes="(max-width: 768px) 100vw, 450px"
        className="object-cover transition-transform duration-300 group-hover:scale-105"
        onError={() => setHasError(true)}
      />
    </div>
  );
}

/**
 * Skeleton de carga para la vista de detalle
 */
function ProductDetailSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Botón y migas */}
      <div className="h-5 w-48 bg-slate-200 rounded-md" />

      {/* Hero card skeleton */}
      <div className="grid grid-cols-1 gap-8 md:grid-cols-12 rounded-3xl border border-slate-200 bg-white p-6 sm:p-8">
        <div className="md:col-span-5">
          <div className="aspect-square w-full bg-slate-200 rounded-3xl" />
        </div>
        <div className="md:col-span-7 space-y-4">
          <div className="h-6 w-28 bg-slate-200 rounded-full" />
          <div className="h-8 w-3/4 bg-slate-200 rounded-lg" />
          <div className="h-6 w-36 bg-slate-200 rounded-md" />
          <div className="h-10 w-44 bg-slate-200 rounded-xl" />
          <div className="space-y-2 pt-4">
            <div className="h-4 w-full bg-slate-200 rounded" />
            <div className="h-4 w-5/6 bg-slate-200 rounded" />
          </div>
        </div>
      </div>

      {/* Kardex skeleton */}
      <div className="space-y-4">
        <div className="h-6 w-52 bg-slate-200 rounded-md" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="h-24 bg-slate-200 rounded-2xl" />
          <div className="h-24 bg-slate-200 rounded-2xl" />
          <div className="h-24 bg-slate-200 rounded-2xl" />
        </div>
      </div>
    </div>
  );
}

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params?.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [kardex, setKardex] = useState<ProductKardexResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [retryTrigger, setRetryTrigger] = useState(0);

  useEffect(() => {
    let isMounted = true;

    if (!productId) return;

    Promise.all([api.getProductById(productId), api.getProductKardex(productId)])
      .then(([prodData, kardexData]) => {
        if (isMounted) {
          setProduct(prodData);
          setKardex(kardexData);
          setErrorStatus(null);
          setErrorMessage(null);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          if (err instanceof ApiError) {
            setErrorStatus(err.status);
            setErrorMessage(err.message);
          } else if (err instanceof Error) {
            setErrorMessage(err.message);
          } else {
            setErrorMessage("Ocurrió un error inesperado al consultar el producto.");
          }
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [productId, retryTrigger]);

  const handleRetry = () => {
    setLoading(true);
    setErrorStatus(null);
    setErrorMessage(null);
    setRetryTrigger((prev) => prev + 1);
  };

  // ── ESTADO 1: Cargando ──────────────────────────────────────────────────
  if (loading) {
    return <ProductDetailSkeleton />;
  }

  // ── ESTADO 2: Producto No Encontrado (404) ──────────────────────────────
  if (errorStatus === 404) {
    return (
      <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs my-8">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-amber-50 text-amber-600 mb-4">
          <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">
          Código 404 — No Encontrado
        </span>
        <h1 className="mt-4 text-2xl font-black text-slate-900 sm:text-3xl">
          Producto no encontrado
        </h1>
        <p className="mt-2 text-sm text-slate-500 max-w-md mx-auto">
          El producto con identificador <strong>ID {productId}</strong> no existe en el catálogo o
          ha sido retirado del sistema.
        </p>
        <div className="mt-8">
          <Link
            href="/products"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-blue-700 transition-colors"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver al catálogo
          </Link>
        </div>
      </div>
    );
  }

  // ── ESTADO 3: Error de Red o Servidor ───────────────────────────────────
  if (errorMessage || !product) {
    return (
      <div className="rounded-3xl border border-rose-200 bg-rose-50/50 p-8 text-center shadow-xs my-8">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 mb-4">
          <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-lg font-bold text-rose-900 mb-1">
          No fue posible cargar el producto
        </h2>
        <p className="text-sm text-rose-700 max-w-md mx-auto mb-6">
          {errorMessage || "Comprueba tu conexión o que el backend esté disponible."}
        </p>
        <div className="flex justify-center gap-3">
          <button
            type="button"
            onClick={handleRetry}
            className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-rose-700 transition-colors"
          >
            Reintentar
          </button>
          <Link
            href="/products"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors"
          >
            Volver al catálogo
          </Link>
        </div>
      </div>
    );
  }

  // ── ESTADO 4: Ficha de Detalle y Kardex ──────────────────────────────────
  return (
    <div className="space-y-10">
      {/* Navegación y Breadcrumbs */}
      <div className="flex items-center justify-between">
        <Link
          href="/products"
          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 transition-colors"
        >
          <svg className="h-4 w-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver al catálogo
        </Link>

        <nav aria-label="Breadcrumb" className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
          <Link href="/products" className="hover:text-slate-900 transition-colors">
            Catálogo
          </Link>
          <span>/</span>
          <span className="text-slate-700 font-medium">{product.categoria}</span>
          <span>/</span>
          <span className="font-mono text-slate-800 font-semibold">{product.sku}</span>
        </nav>
      </div>

      {/* Tarjeta Principal de Información del Producto */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-12 items-start">
          {/* Columna Izquierda: Imagen destacada grande */}
          <div className="md:col-span-5">
            <ProductDetailImage src={product.imagen_url} alt={product.nombre} />
          </div>

          {/* Columna Derecha: Especificaciones y Precios */}
          <div className="md:col-span-7 space-y-6">
            <div>
              {/* Badge de Categoría y SKU */}
              <div className="flex flex-wrap items-center gap-2.5 mb-3">
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 border border-blue-200/60">
                  {product.categoria}
                </span>

                <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 font-mono text-xs font-semibold text-slate-700 border border-slate-200">
                  <span className="text-slate-400 font-normal">SKU:</span>
                  {product.sku}
                </span>

                <span className="text-xs text-slate-400">
                  ID: #{product.id}
                </span>
              </div>

              {/* Nombre Comercial */}
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                {product.nombre}
              </h1>
            </div>

            {/* Precio y Stock disponible */}
            <div className="flex flex-wrap items-baseline gap-4 py-4 px-5 rounded-2xl bg-slate-50/80 border border-slate-200/70">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Precio de Venta
                </span>
                <span className="text-3xl sm:text-4xl font-black text-slate-900">
                  {formatCurrency(product.precio)}
                </span>
              </div>

              <div className="sm:ml-auto flex flex-col sm:items-end">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Disponibilidad
                </span>
                {product.stock <= 0 ? (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-3 py-1 text-xs font-bold text-rose-700 border border-rose-200">
                    <span className="h-2 w-2 rounded-full bg-rose-600" />
                    Sin stock (0)
                  </span>
                ) : product.stock <= 5 ? (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700 border border-amber-200">
                    <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                    Bajo inventario ({product.stock} disponibles)
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700 border border-emerald-200">
                    <span className="h-2 w-2 rounded-full bg-emerald-600" />
                    {product.stock} unidades disponibles
                  </span>
                )}
              </div>
            </div>

            {/* Ficha descriptiva */}
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                Descripción y Ficha Técnica
              </h2>
              <div className="rounded-2xl border border-slate-100 bg-white p-4 text-sm text-slate-600 leading-relaxed shadow-2xs">
                {product.descripcion ? (
                  product.descripcion
                ) : (
                  <span className="text-slate-400 italic">
                    Sin descripción detallada adicional para este artículo.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sección Kardex Valorizado */}
      <section aria-labelledby="kardex-heading">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-xs">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h2 id="kardex-heading" className="text-xl font-extrabold text-slate-900 tracking-tight">
              Kardex de Inventario Valorizado
            </h2>
            <p className="text-xs text-slate-500">
              Control de existencias y valoración mediante Promedio Ponderado Móvil (DEC-010).
            </p>
          </div>
        </div>

        {kardex && <KardexTable kardex={kardex} />}
      </section>
    </div>
  );
}
