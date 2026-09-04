"use client";

import { KardexLine, ProductKardexResponse } from "@/types";
import { formatCurrency, formatDateTime } from "@/lib/formatters";

interface KardexTableProps {
  kardex: ProductKardexResponse;
}

export default function KardexTable({ kardex }: KardexTableProps) {
  const { movimientos, saldo_total_unidades, costo_promedio_actual, saldo_total_valorizado } =
    kardex;

  return (
    <div className="space-y-6">
      {/* Tarjetas resumen de valorización del inventario (Promedio Ponderado Móvil) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* Saldo Total en Unidades */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Saldo en Bodega
            </span>
            <span className="rounded-lg bg-blue-50 p-2 text-blue-600">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </span>
          </div>
          <p className="mt-2 text-3xl font-extrabold text-slate-900">
            {saldo_total_unidades}{" "}
            <span className="text-sm font-semibold text-slate-500">unid.</span>
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Unidades físicas disponibles para venta
          </p>
        </div>

        {/* Costo Promedio Ponderado Actual */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Costo Promedio Ponderado
            </span>
            <span className="rounded-lg bg-amber-50 p-2 text-amber-600">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </span>
          </div>
          <p className="mt-2 text-3xl font-extrabold text-slate-900">
            {formatCurrency(costo_promedio_actual)}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Método Promedio Ponderado Móvil (DEC-010)
          </p>
        </div>

        {/* Saldo Total Valorizado */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Valor Total Inventario
            </span>
            <span className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
          </div>
          <p className="mt-2 text-3xl font-extrabold text-slate-900">
            {formatCurrency(saldo_total_valorizado)}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Valor contable total de existencias
          </p>
        </div>
      </div>

      {/* Tabla cronológica de movimientos */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
        <div className="border-b border-slate-200 bg-slate-50/75 px-6 py-4">
          <h2 className="text-base font-bold text-slate-900">
            Historial de Movimientos de Inventario
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Registro cronológico detallado de entradas, salidas y recálculo dinámico de saldos.
          </p>
        </div>

        {movimientos.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            <svg
              className="mx-auto h-12 w-12 text-slate-300 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            No hay movimientos registrados para este producto en el Kardex.
          </div>
        ) : (
          <>
            {/* Vista Desktop */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/50 text-xs font-bold uppercase tracking-wider text-slate-500">
                    <th scope="col" className="py-3 px-4">
                      Fecha
                    </th>
                    <th scope="col" className="py-3 px-4">
                      Tipo
                    </th>
                    <th scope="col" className="py-3 px-4">
                      Documento Ref.
                    </th>
                    <th scope="col" className="py-3 px-4 text-right">
                      Cantidad
                    </th>
                    <th scope="col" className="py-3 px-4 text-right">
                      Costo Unitario
                    </th>
                    <th scope="col" className="py-3 px-4 text-right">
                      Saldo Unid.
                    </th>
                    <th scope="col" className="py-3 px-4 text-right">
                      Costo Promedio
                    </th>
                    <th scope="col" className="py-3 px-4 text-right">
                      Saldo Valorizado
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {movimientos.map((mov: KardexLine) => {
                    const isEntry = mov.tipo === "ENTRY";
                    return (
                      <tr key={mov.id} className="hover:bg-slate-50/80 transition-colors">
                        {/* Fecha */}
                        <td className="py-3 px-4 text-xs text-slate-600 whitespace-nowrap">
                          {formatDateTime(mov.fecha)}
                        </td>

                        {/* Tipo de movimiento */}
                        <td className="py-3 px-4">
                          {isEntry ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                              <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                              </svg>
                              Entrada
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-bold text-blue-700 border border-blue-200">
                              <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                              </svg>
                              Salida
                            </span>
                          )}
                        </td>

                        {/* Documento de referencia */}
                        <td className="py-3 px-4 font-mono text-xs font-semibold text-slate-700">
                          {mov.documento_referencia}
                        </td>

                        {/* Cantidad */}
                        <td
                          className={`py-3 px-4 text-right font-bold ${
                            isEntry ? "text-emerald-700" : "text-blue-700"
                          }`}
                        >
                          {isEntry ? `+${mov.cantidad}` : `-${mov.cantidad}`}
                        </td>

                        {/* Costo unitario */}
                        <td className="py-3 px-4 text-right text-slate-700">
                          {formatCurrency(mov.costo_unitario)}
                        </td>

                        {/* Saldo en unidades acumulado */}
                        <td className="py-3 px-4 text-right font-semibold text-slate-900 bg-slate-50/40">
                          {mov.saldo_unidades}
                        </td>

                        {/* Costo promedio tras el movimiento */}
                        <td className="py-3 px-4 text-right text-slate-700 bg-slate-50/40">
                          {formatCurrency(mov.costo_promedio)}
                        </td>

                        {/* Saldo valorizado acumulado */}
                        <td className="py-3 px-4 text-right font-bold text-slate-900 bg-slate-50/60">
                          {formatCurrency(mov.saldo_valorizado)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Vista Mobile adaptativa */}
            <div className="divide-y divide-slate-100 md:hidden">
              {movimientos.map((mov: KardexLine) => {
                const isEntry = mov.tipo === "ENTRY";
                return (
                  <div key={mov.id} className="p-4 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {isEntry ? (
                          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                            Entrada
                          </span>
                        ) : (
                          <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-bold text-blue-700 border border-blue-200">
                            Salida
                          </span>
                        )}
                        <span className="font-mono text-xs font-semibold text-slate-700">
                          {mov.documento_referencia}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {formatDateTime(mov.fecha)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-100">
                      <div>
                        <span className="text-slate-500">Cantidad:</span>{" "}
                        <strong className={isEntry ? "text-emerald-700" : "text-blue-700"}>
                          {isEntry ? `+${mov.cantidad}` : `-${mov.cantidad}`}
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-500">Costo Un.:</span>{" "}
                        <span className="text-slate-800">{formatCurrency(mov.costo_unitario)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Saldo Unid:</span>{" "}
                        <strong className="text-slate-900">{mov.saldo_unidades}</strong>
                      </div>
                      <div>
                        <span className="text-slate-500">Saldo Valor:</span>{" "}
                        <strong className="text-slate-900">{formatCurrency(mov.saldo_valorizado)}</strong>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
