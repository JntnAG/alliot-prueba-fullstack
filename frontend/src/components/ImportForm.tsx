"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ApiError, ImportResult, RowError } from "@/types";

export default function ImportForm() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Valida que el archivo seleccionado sea un Excel válido
   */
  const handleFileSelect = (selectedFile: File | undefined | null) => {
    setErrorMessage(null);
    setResult(null);

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const filename = selectedFile.name.toLowerCase();
    if (!filename.endsWith(".xlsx") && !filename.endsWith(".xlsm")) {
      setErrorMessage("Formato no válido. Selecciona un archivo Excel con extensión .xlsx");
      setFile(null);
      return;
    }

    // Límite de seguridad: 10MB
    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage("El archivo excede el tamaño máximo permitido de 10 MB.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  /**
   * Enviar archivo al backend mediante el cliente API
   */
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setErrorMessage("Por favor selecciona un archivo .xlsx antes de iniciar la importación.");
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);

    try {
      const response = await api.importProductsExcel(file);
      setResult(response);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Ocurrió un error inesperado durante el procesamiento del archivo.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="space-y-8">
      {/* ── SECCIÓN 1: Formulario de Carga ──────────────────────────────── */}
      {!result ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
          <form onSubmit={handleUpload} className="space-y-6">
            {/* Zona Drag & Drop */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={(e) => {
                e.preventDefault();
                setIsDragging(false);
              }}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileSelect(e.dataTransfer.files[0]);
                }
              }}
              className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
                isDragging
                  ? "border-blue-500 bg-blue-50/50 scale-[0.99]"
                  : "border-slate-300 bg-slate-50/50 hover:bg-slate-50"
              }`}
            >
              <input
                id="excel-file-input"
                type="file"
                accept=".xlsx, .xlsm, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                disabled={isUploading}
                onChange={(e) => handleFileSelect(e.target.files?.[0])}
                className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
              />

              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 mb-4 shadow-2xs">
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>

              {file ? (
                <div className="space-y-1">
                  <p className="text-sm font-bold text-slate-900">{file.name}</p>
                  <p className="text-xs text-slate-500">
                    {(file.size / 1024).toFixed(1)} KB &bull; Listo para procesar
                  </p>
                  <span className="inline-block mt-2 text-xs font-semibold text-blue-600 underline">
                    Haz clic para cambiar de archivo
                  </span>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-slate-800">
                    Arrastra tu archivo Excel aquí o{" "}
                    <span className="text-blue-600 font-bold underline">explora tus archivos</span>
                  </p>
                  <p className="text-xs text-slate-400">
                    Formatos admitidos: .xlsx, .xlsm (máx. 10 MB)
                  </p>
                </div>
              )}
            </div>

            {/* Mensaje de Error */}
            {errorMessage && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs font-medium text-rose-700 flex items-center gap-2">
                <svg className="h-4 w-4 shrink-0 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Botón de subida */}
            <div className="flex items-center justify-end gap-3 pt-2">
              {file && (
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={isUploading}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
                >
                  Cancelar
                </button>
              )}

              <button
                type="submit"
                disabled={!file || isUploading}
                id="submit-import-btn"
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-bold text-white shadow-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isUploading ? (
                  <>
                    <svg className="h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Procesando archivo...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Importar productos al catálogo
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* ── SECCIÓN 2: Resumen de Resultados de Importación (DEC-008) ──────── */
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Banner de Estado General */}
          <div
            className={`rounded-3xl border p-6 shadow-xs ${
              result.rechazadas === 0
                ? "border-emerald-200 bg-emerald-50/60"
                : result.insertadas + result.actualizadas > 0
                ? "border-amber-200 bg-amber-50/60"
                : "border-rose-200 bg-rose-50/60"
            }`}
          >
            <div className="flex items-center gap-4">
              <div
                className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${
                  result.rechazadas === 0
                    ? "bg-emerald-600 text-white"
                    : result.insertadas + result.actualizadas > 0
                    ? "bg-amber-500 text-white"
                    : "bg-rose-600 text-white"
                }`}
              >
                {result.rechazadas === 0 ? (
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                )}
              </div>

              <div>
                <h2 className="text-lg font-black text-slate-900">
                  {result.rechazadas === 0
                    ? "¡Importación completada con éxito!"
                    : result.insertadas + result.actualizadas > 0
                    ? "Importación completada con resiliencia parcial (DEC-008)"
                    : "El archivo no pudo ser procesado"}
                </h2>
                <p className="text-xs text-slate-600 mt-0.5">
                  {result.rechazadas === 0
                    ? `Se procesaron correctamente las ${result.leidas} filas del archivo.`
                    : `Se aplicaron los registros válidos (${result.insertadas + result.actualizadas}) y se reportaron los rechazos sin anular la operación.`}
                </p>
              </div>
            </div>
          </div>

          {/* Tarjetas de Métricas de Importación */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {/* Leídas */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Leídas
              </span>
              <p className="mt-2 text-3xl font-black text-slate-900">{result.leidas}</p>
              <p className="text-xs text-slate-400 mt-1">Total de filas procesadas</p>
            </div>

            {/* Insertadas */}
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-5 text-center shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Insertadas
              </span>
              <p className="mt-2 text-3xl font-black text-emerald-700">+{result.insertadas}</p>
              <p className="text-xs text-emerald-600 mt-1">Nuevos SKU en catálogo</p>
            </div>

            {/* Actualizadas */}
            <div className="rounded-2xl border border-blue-200 bg-blue-50/40 p-5 text-center shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-700">
                Actualizadas
              </span>
              <p className="mt-2 text-3xl font-black text-blue-700">{result.actualizadas}</p>
              <p className="text-xs text-blue-600 mt-1">Precios / stock modificados</p>
            </div>

            {/* Rechazadas */}
            <div className="rounded-2xl border border-rose-200 bg-rose-50/40 p-5 text-center shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-700">
                Rechazadas
              </span>
              <p className="mt-2 text-3xl font-black text-rose-700">{result.rechazadas}</p>
              <p className="text-xs text-rose-600 mt-1">Errores de validación</p>
            </div>
          </div>

          {/* Tabla de Errores por Fila (si existen) */}
          {result.errores.length > 0 && (
            <div className="overflow-hidden rounded-2xl border border-rose-200 bg-white shadow-xs">
              <div className="border-b border-rose-100 bg-rose-50/60 px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-rose-900">
                    Detalle de Filas Rechazadas ({result.errores.length})
                  </h3>
                  <p className="text-xs text-rose-700 mt-0.5">
                    Las siguientes filas contenían inconsistencias y fueron omitidas para resguardar la integridad del catálogo.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider">
                      <th className="py-3 px-4 w-24">Fila Excel</th>
                      <th className="py-3 px-4 w-32">Columna / Campo</th>
                      <th className="py-3 px-4">Motivo del Rechazo</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.errores.map((err: RowError, idx: number) => (
                      <tr key={idx} className="hover:bg-rose-50/30 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-slate-800">
                          <span className="rounded-md bg-slate-100 px-2 py-1 border border-slate-200">
                            Fila #{err.fila}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="rounded-md bg-rose-50 px-2 py-1 font-mono font-semibold text-rose-700 border border-rose-200">
                            {err.campo}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-700 font-medium">
                          {err.motivo}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Acciones de Navegación Post-Importación */}
          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Cargar otro archivo
            </button>

            <Link
              href="/products"
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-bold text-white shadow-xs hover:bg-blue-700 transition-colors"
            >
              Ver catálogo actualizado
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>
          </div>
        </div>
      )}

      {/* ── SECCIÓN 3: Guía de Formato Esperado ─────────────────────────── */}
      <div className="rounded-3xl border border-slate-200 bg-slate-50/60 p-6 shadow-xs">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
          Estructura requerida del archivo Excel
        </h3>
        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
          La primera fila del archivo debe contener exactamente los siguientes encabezados de columna:
        </p>

        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100/75 font-mono text-slate-700 border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">sku</th>
                <th className="py-2.5 px-3">nombre</th>
                <th className="py-2.5 px-3">categoria</th>
                <th className="py-2.5 px-3">precio</th>
                <th className="py-2.5 px-3">stock</th>
                <th className="py-2.5 px-3">imagen_url</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-slate-600">
              <tr>
                <td className="py-2 px-3">SKU-001</td>
                <td className="py-2 px-3 font-sans">Taladro percutor 650W</td>
                <td className="py-2 px-3 font-sans">Herramientas</td>
                <td className="py-2 px-3">89990</td>
                <td className="py-2 px-3">12</td>
                <td className="py-2 px-3 text-slate-400">https://.../img.jpg</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-slate-500">
          💡 <em>Tip de evaluación:</em> Puedes utilizar el archivo de ejemplo{" "}
          <code className="rounded bg-slate-200/80 px-1.5 py-0.5 font-mono text-slate-800">
            sample_products.xlsx
          </code>{" "}
          ubicado en la raíz del proyecto para comprobar la resiliencia parcial y la actualización masiva.
        </p>
      </div>
    </div>
  );
}
