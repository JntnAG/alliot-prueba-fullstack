"""
database.py — Conexión y sesiones de base de datos
=====================================================

¿QUÉ HACE ESTE ARCHIVO?
------------------------
Este archivo es el "puente" entre nuestra aplicación y la base de datos.
Define CÓMO conectarse a la base de datos y provee una función que permite
abrir y cerrar sesiones de forma segura.

CONCEPTOS CLAVE (para dummies):
--------------------------------
- ENGINE: Es como el "motor del auto". Sabe cómo hablar con la base de datos.
  Tiene la URL de conexión y gestiona el pool de conexiones.

- SESSION: Es como "abrir una conversación" con la base de datos.
  Cada petición HTTP abre su propia sesión, hace sus operaciones y la cierra.

- get_session(): Es un generador (usa `yield`) que FastAPI usa como dependencia.
  FastAPI lo llama automáticamente en cada endpoint que lo necesite.

¿POR QUÉ DATABASE_URL?
----------------------
Usamos una variable de entorno para no hardcodear credenciales en el código.
El mismo código funciona con PostgreSQL (producción/Docker) o SQLite (desarrollo).
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# ─────────────────────────────────────────────────────────────────────────────
# Carga de variables de entorno desde .env (si existe)
# En producción las variables ya están en el entorno del sistema.
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# URL de conexión a la base de datos
# Ejemplos:
#   PostgreSQL: postgresql://postgres:postgres@localhost:5432/alliot_db
#   SQLite:     sqlite:///./alliot.db
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./alliot.db",  # fallback seguro para desarrollo sin .env
)

# ─────────────────────────────────────────────────────────────────────────────
# Argumentos específicos por motor de base de datos
#
# SQLite necesita check_same_thread=False porque FastAPI puede manejar múltiples
# threads concurrentes y SQLite, por defecto, solo permite uso desde el thread
# que creó la conexión.
#
# PostgreSQL no necesita este argumento; por eso se lo pasamos solo cuando
# el driver es SQLite.
# ─────────────────────────────────────────────────────────────────────────────
connect_args: dict = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# ─────────────────────────────────────────────────────────────────────────────
# Creación del engine
# El engine NO abre conexiones inmediatamente; las abre cuando las necesita.
# ─────────────────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Cambiar a True durante debugging para ver el SQL generado
)


def create_db_and_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos SQLModel.

    Se llama una vez al arrancar la aplicación (en el lifespan de FastAPI).
    Si las tablas ya existen, no hace nada (comportamiento idempotente).

    En un proyecto con migraciones (Alembic), este paso se reemplazaría por
    `alembic upgrade head`. Para el alcance de esta prueba, create_all es
    suficiente y más simple.
    """
    # Asegurar que todos los modelos SQLModel estén importados y registrados
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos.

    FastAPI lo usa como dependencia inyectada en cada endpoint:

        @router.get("/products")
        def list_products(session: Session = Depends(get_session)):
            ...

    El bloque `with Session(engine) as session` garantiza que:
    - La sesión se abre al inicio de la petición.
    - La sesión se cierra (y el commit/rollback se maneja) al finalizar.
    - No quedan conexiones abiertas aunque ocurra un error.
    """
    with Session(engine) as session:
        yield session
