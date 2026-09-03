"""
main.py — Punto de entrada de la aplicación FastAPI
=====================================================

¿QUÉ HACE ESTE ARCHIVO?
------------------------
Es el archivo que FastAPI lee para saber QUÉ aplicación correr.
Aquí se configura:
  - El ciclo de vida (lifespan): qué hacer al arrancar y al apagar.
  - Los metadatos de la API (título, descripción, versión).
  - Los routers: grupos de endpoints registrados en la aplicación.
  - El middleware CORS: quién puede llamar a esta API desde el navegador.

FLUJO DE ARRANQUE:
------------------
1. FastAPI ejecuta la función `lifespan` (create_db_and_tables).
2. La aplicación queda lista para recibir peticiones HTTP.
3. Los routers registrados definen las rutas disponibles.
4. Al apagar (Ctrl+C o señal SIGTERM), lifespan finaliza limpiamente.

¿QUÉ ES CORS?
-------------
CORS (Cross-Origin Resource Sharing) es una política de seguridad del navegador.
Sin configurar CORS, el navegador bloquea las peticiones desde
http://localhost:3000 (frontend Next.js) hacia http://localhost:8000 (backend).
Aquí lo configuramos para permitir esas peticiones durante desarrollo.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables

# ─────────────────────────────────────────────────────────────────────────────
# Lifespan: eventos de inicio y apagado de la aplicación
#
# asynccontextmanager convierte la función generadora en un gestor de contexto
# compatible con FastAPI. El bloque antes del `yield` se ejecuta al arrancar;
# el bloque después del `yield` se ejecuta al apagar.
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Inicio ──────────────────────────────────────────────────────────────
    # Crea las tablas en la base de datos si no existen todavía.
    # Si ya existen, no hace nada (idempotente).
    create_db_and_tables()
    yield
    # ── Apagado ─────────────────────────────────────────────────────────────
    # Aquí podrían ir tareas de limpieza (cerrar conexiones, etc.)
    # Para el alcance de esta prueba no es necesario.


# ─────────────────────────────────────────────────────────────────────────────
# Instancia principal de la aplicación
#
# Los metadatos aparecen en la documentación automática de Swagger (/docs)
# y en Redoc (/redoc).
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Alliot — API de Catálogo y Kardex",
    description=(
        "API REST para gestión de catálogo de productos, "
        "control de inventario mediante Kardex valorizado "
        "e importación masiva desde Excel."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────────────────
# Middleware CORS
#
# En producción, reemplazar ["*"] por los dominios reales permitidos.
# Ejemplo: ["https://app.alliot.cl"]
# ─────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En producción: lista de dominios explícita
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint de salud (healthcheck)
#
# Permite verificar rápidamente que el servidor está corriendo.
# Docker Compose y sistemas de monitoreo suelen usar este tipo de endpoints.
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    """
    Verifica que el servidor está disponible.

    Responde inmediatamente con { "status": "ok" }.
    No requiere base de datos.
    """
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────────────
# Registro de routers
#
# Los routers se importan y registran aquí.
# Cada router agrupa los endpoints de un dominio específico.
#
# NOTA: Se importan DESPUÉS de definir `app` para evitar importaciones
# circulares. Los routers importarán `get_session` de database.py pero
# no necesitan importar `app`.
# ─────────────────────────────────────────────────────────────────────────────
# Los routers se agregarán en las fases siguientes (1.2, 1.3, 1.4):
# from app.routers import products, imports, kardex
# app.include_router(products.router)
# app.include_router(imports.router)
# app.include_router(kardex.router)
