# 📦 Prueba Técnica Fullstack — Catálogo de Productos y Kardex (Alliot)

Aplicación web fullstack desarrollada para la gestión de catálogo de productos, control de inventario mediante Kardex valorizado y carga masiva vía Excel.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.11+ / [FastAPI](https://fastapi.tiangolo.com/) + [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Base de Datos:** PostgreSQL (producción / Docker Compose) & SQLite (desarrollo rápido opcional)
- **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router) + TypeScript + Tailwind CSS
- **Contenedores:** Docker & Docker Compose
- **Testing:** `pytest` + FastAPI `TestClient`

---

## 🎯 Comprensión del Negocio

### 1. ¿Qué es un SKU y por qué debe ser único?
El **SKU (Stock Keeping Unit)** es el identificador interno alfanumérico que la organización asigna para distinguir un producto o variante particular. A diferencia del nombre (que es comercial y puede repetirse) o del código de barras (diseñado para lectura óptica estándar externa), el SKU sigue la lógica operativa interna. Debe ser único para garantizar la integridad transaccional del inventario, compras, Kardex y pedidos sin ambigüedad.

### 2. ¿Para qué sirve un Kardex y qué relación tiene con la valorización del stock?
El **Kardex** es el registro cronológico y estructurado de todos los movimientos (entradas y salidas) de inventario de cada producto. Además de mantener el saldo en unidades físicas, calcula y registra el valor monetario de las existencias mediante un método de valorización contable, facilitando auditorías, cálculo del costo de ventas y balances financieros.

### 3. Si un mismo producto se compró en distintas fechas a distintos costos, ¿qué costo usaría para valorizar el saldo y por qué?
Se implementa el método de **Promedio Ponderado Móvil**. Cada nueva entrada recalcula el costo unitario promedio en base al valor total acumulado y las nuevas unidades recibidas. Las salidas se valorizan al costo promedio vigente sin alterarlo. Se eligió porque proporciona una valoración continua, matemáticamente estable, objetiva y sin la complejidad de gestión de lotes físicos individuales.

### 4. ¿Qué diferencia hay entre el stock físico y el stock disponible para la venta? ¿Cómo lo reflejarías en el modelo de datos?
- **Stock físico:** Unidades reales existentes físicamente en bodega en un momento dado.
- **Stock disponible para la venta:** Unidades comerciales listas para ser vendidas tras restar aquellas reservadas en carritos, apartadas o en cuarentena (`stock_disponible = stock_fisico - stock_reservado`).
- **Enfoque adoptado:** Dado que el alcance de la prueba especifica un único campo `stock`, se documenta la decisión de tratarlo como **unidades disponibles para la venta**.

---

## 🚀 Puesta en Marcha

### Requisitos Previos
- Docker y Docker Compose (recomendado)
- Node.js 18+ y Python 3.11+ (para desarrollo local sin Docker)

---

### Modo 1: Docker Compose (Ejecución Completa Unificada)

Levanta PostgreSQL, la API FastAPI y la aplicación Next.js en un solo comando:

```bash
docker compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Modo 2: Desarrollo Local

1. **Base de Datos (Docker aislado):**
   ```bash
   docker compose up db -d
   ```

2. **Backend (FastAPI):**
   ```bash
   cd backend
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend (Next.js):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite de pruebas incluye tests unitarios (sin base de datos) para el patrón Criteria y la función pura de Kardex, así como tests de integración HTTP mediante `TestClient`.

Desde la carpeta `backend/`:

```bash
pytest
```

---

## 📚 Documentación de Decisiones Técnicas

El detalle completo de diseño, arquitectura por capas, modelo de Kardex, importación Excel y delimitación de alcance se encuentra documentado en [DECISIONES.md](./DECISIONES.md).
