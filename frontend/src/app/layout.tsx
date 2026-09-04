import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Navbar from "@/components/Navbar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Alliot — Catálogo de Productos y Kardex",
  description:
    "Sistema de gestión de catálogo de productos industriales, control de inventario con Kardex valorizado (Promedio Ponderado Móvil) e importación masiva de Excel.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-600 selection:text-white">
        <Navbar />
        <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
            <p>
              <strong>Alliot</strong> — Prueba Técnica Desarrollador Full Stack (FastAPI + Next.js)
            </p>
            <p className="text-slate-400">
              Inventario valorizado &bull; Promedio Ponderado Móvil &bull; Patrón Criteria
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
