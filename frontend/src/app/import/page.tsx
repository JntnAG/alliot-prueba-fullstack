import ImportForm from "@/components/ImportForm";

export const metadata = {
  title: "Importar Catálogo desde Excel — Alliot",
  description:
    "Carga masiva de productos mediante archivo Excel (.xlsx) con validación fila por fila, actualización por SKU y resiliencia parcial.",
};

export default function ImportPage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Encabezado */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-600 mb-1">
          <span>Administración de Catálogo</span>
          <span>&bull;</span>
          <span>Carga Masiva</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Importar Productos desde Excel
        </h1>
        <p className="text-sm text-slate-500 mt-1 max-w-2xl leading-relaxed">
          Sube un archivo de hoja de cálculo <code className="font-mono text-slate-700 bg-slate-100 px-1 py-0.5 rounded">.xlsx</code> para
          ingresar nuevos productos o actualizar precios y existencias de productos existentes mediante su SKU.
        </p>
      </div>

      {/* Formulario de importación interactivo */}
      <ImportForm />
    </div>
  );
}
