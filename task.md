# 📋 Lista de Tareas — Prueba Técnica Fullstack (Alliot)

> **Stack:** FastAPI (Python 3.11+) + Next.js 14+ (App Router) + SQLModel + PostgreSQL / SQLite  
> **Criterio rector:** Simplicidad, consistencia arquitectural y foco en el negocio.  
> **Objetivo:** Implementar una solución reproducible que cubra los requisitos funcionales, técnicos, de pruebas y documentación definidos para la prueba técnica.

---

# 🏁 FASE 0 — Preparación del proyecto y arquitectura base

## Estructura inicial

- [x] Inicializar la estructura de carpetas según el diseño acordado:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── product.py
│   │   └── stock_movement.py
│   │
│   ├── schemas/
│   │   ├── product.py
│   │   ├── import_result.py
│   │   └── kardex.py
│   │
│   ├── routers/
│   │   ├── products.py
│   │   └── imports.py
│   │
│   ├── services/
│   │   ├── product_service.py
│   │   ├── import_service.py
│   │   └── kardex_service.py
│   │
│   └── criteria/
│       ├── filters.py
│       ├── product_criteria.py
│       └── criteria_builder.py
│
├── tests/
│   ├── unit/
│   │   ├── test_criteria.py
│   │   └── test_kardex.py
│   │
│   └── integration/
│       └── test_products_api.py
│
├── seed.py
├── requirements.txt
└── Dockerfile
```

- [x] Inicializar proyecto frontend con estructura:

```text
frontend/
└── src/
    ├── app/
    │   ├── products/
    │   │   ├── page.tsx
    │   │   └── [id]/
    │   │       └── page.tsx
    │   │
    │   └── import/
    │       └── page.tsx
    │
    ├── components/
    │   ├── ProductTable.tsx
    │   ├── ProductFilters.tsx
    │   ├── Pagination.tsx
    │   ├── ImportForm.tsx
    │   └── KardexTable.tsx
    ├── types/
    └── lib/
```

---

## Variables de entorno

- [x] Crear `.env.example`.
- [x] Configurar `DATABASE_URL`.
- [x] Configurar PostgreSQL como entorno principal.
- [x] Permitir SQLite como alternativa de desarrollo.
- [x] Configurar `NEXT_PUBLIC_API_URL`.
- [x] Verificar que no existan credenciales reales en el repositorio.

---

## Documentación inicial

- [x] Crear `README.md`.
- [x] Incluir descripción general del proyecto.
- [x] Incluir requisitos previos.
- [x] Reservar secciones para:
  - Ejecución local.
  - Ejecución Docker.
  - Tests.
  - Seed.
  - Preguntas de negocio.
  - Decisiones técnicas.
  - Alcance y funcionalidades excluidas.

---

# 🐍 FASE 1 — Backend (FastAPI + SQLModel)

---

## 1.1 Configuración base y persistencia

- [x] Crear `backend/requirements.txt` y `requirements-dev.txt`.

Dependencias principales:
- [x] `fastapi`
- [x] `uvicorn`
- [x] `sqlmodel`
- [x] `psycopg2-binary` (en requirements.txt para Docker; omitido en requirements-dev.txt por incompatibilidad Python 3.14/Windows)
- [x] `python-dotenv`
- [x] `openpyxl`
- [x] `pytest`
- [x] `httpx`

- [x] Configurar `app/database.py`.
- [x] Crear engine para PostgreSQL.
- [x] Permitir engine SQLite mediante `DATABASE_URL`.
- [x] Implementar generador `get_session`.
- [x] Crear tablas al iniciar la aplicación (lifespan en main.py llama `create_db_and_tables()`).
- [x] Verificar arranque de FastAPI (servidor responde en http://127.0.0.1:8000).
- [x] Verificar documentación Swagger en:

```text
/docs  → OK (OpenAPI schema verificado, title y version correctos)
```

---

## 1.2 Modelos y Schemas

### Producto

- [x] Implementar `app/models/product.py`.

#### `ProductBase`
- [x] `sku`
- [x] `nombre`
- [x] `descripcion`
- [x] `categoria`
- [x] `precio` (usar `Decimal` para valores monetarios)
- [x] `stock`
- [x] `imagen_url`

#### `Product`
- [x] Declarar tabla persistente (`table=True`).
- [x] `id` como primary key.
- [x] `sku` indexado.
- [x] Garantizar unicidad de `sku` mediante constraint real en base de datos (`UniqueConstraint("sku", name="uq_product_sku")`).

#### Schemas
- [x] Implementar `ProductCreate`.
- [x] Implementar `ProductRead`.

---

### Movimientos de inventario

- [x] Implementar `app/models/stock_movement.py`.

#### Enum
- [x] `MovementType.ENTRY`
- [x] `MovementType.EXIT`

#### `StockMovement`
- [x] `id`
- [x] `product_id` (foreign key a `product.id`, indexado)
- [x] `date`
- [x] `movement_type`
- [x] `quantity`
- [x] `unit_cost` (usar `Decimal`)
- [x] `reference_document`

---

### Respuesta de listado

- [x] Implementar `app/schemas/product.py`.

#### `ProductListResponse`
- [x] `items: list[ProductRead]`
- [x] `total: int`
- [x] `page: int`
- [x] `page_size: int`

---

### Schemas de importación

- [x] Implementar `app/schemas/import_result.py`.

#### Resultado
- [x] `leidas`
- [x] `insertadas`
- [x] `actualizadas`
- [x] `rechazadas`
- [x] `errores`

#### Error por fila
- [x] Número de fila.
- [x] Campo.
- [x] Motivo.

---

### Schemas de Kardex

- [x] Implementar `app/schemas/kardex.py`.
- [x] Fecha.
- [x] Tipo de movimiento.
- [x] Cantidad.
- [x] Costo unitario.
- [x] Documento de referencia.
- [x] Saldo acumulado en unidades.
- [x] Saldo acumulado valorizado.
- [x] Costo promedio vigente.

---

## 1.3 Patrón Criteria

### Filters

- [x] Implementar `app/criteria/filters.py`.

#### `FilterOperator`
- [x] `eq`
- [x] `contains`
- [x] `gt`
- [x] `gte`
- [x] `lt`
- [x] `lte`
- [x] `between`

#### `ProductField`
- [x] `sku`
- [x] `nombre`
- [x] `categoria`
- [x] `precio`

#### `Filter`
- [x] Implementar dataclass:

```text
Filter(
    field,
    operator,
    value
)
```

---

### ProductCriteria

- [x] Implementar `app/criteria/product_criteria.py`.

#### Campos
- [x] `filters`
- [x] `page`
- [x] `page_size`
- [x] `order_by`
- [x] `order_dir`

---

### Criteria Builder

- [x] Implementar `app/criteria/criteria_builder.py` para conversión de query parameters a `ProductCriteria`.

Ejemplo:
```text
GET /products
?q=taladro
&categoria=Herramientas
&precio_min=100
&precio_max=500
&page=1
&page_size=20
```
Debe convertirse internamente en un `ProductCriteria`.

---

### Criteria Interpreter

- [x] Implementar en `services/product_service.py`.
- [x] Traducir `ProductCriteria` a consultas SQLModel.
- [x] Aplicar filtros en base de datos.
- [x] Calcular total de registros.
- [x] Aplicar ordenamiento.
- [x] Aplicar paginación mediante `offset` y `limit`.

#### Principio
> Si mañana se agrega un nuevo filtro o cambia la consulta, no debe ser necesario modificar la firma del endpoint.

---

## 1.4 Endpoints y reglas de negocio

---

### Productos

#### Listado
- [x] Implementar:

```text
GET /products
```

#### Query params
- [x] `q`
- [x] `categoria`
- [x] `precio_min`
- [x] `precio_max`
- [x] `page`
- [x] `page_size`
- [x] `order_by`
- [x] `order_dir`

#### Reglas
- [x] Búsqueda por nombre.
- [x] Búsqueda por SKU.
- [x] Filtro por categoría.
- [x] Filtro por rango de precio.
- [x] Ordenamiento.
- [x] Paginación.

---

### Detalle

- [x] Implementar:

```text
GET /products/{id}
```

- [x] Retornar producto completo.
- [x] Retornar `404 Not Found` si no existe.

---

### Kardex

- [x] Implementar:

```text
GET /products/{id}/kardex
```

- [x] Retornar movimientos cronológicos.
- [x] Retornar saldo acumulado en unidades.
- [x] Retornar saldo valorizado.
- [x] Retornar costo promedio.
- [x] Retornar 404 si el producto no existe.

---

### Importación Excel

- [x] Implementar endpoint:

```text
POST /products/import
```

- [x] Recibir archivo `.xlsx`.
- [x] Validar archivo.
- [x] Procesar fila por fila.
- [x] Detectar campos inválidos.
- [x] Detectar precios inválidos.
- [x] Detectar stocks inválidos.
- [x] Detectar SKU duplicado dentro del archivo (rechazar para evitar orden-dependencia).
- [x] Actualizar producto cuando SKU ya existe en BD (`UPDATE`).
- [x] Insertar producto cuando SKU no existe en BD (`INSERT`).
- [x] Continuar procesando filas válidas (resiliencia parcial).
- [x] Reportar filas rechazadas con número de fila, campo y motivo.
- [x] Retornar resumen final estructurado.

---

### Manejo de errores

- [x] Retornar 404 para recursos inexistentes.
- [x] Retornar 422 para parámetros o datos inválidos.
- [x] Evitar usar 500 para errores de validación esperables.
- [x] Retornar mensajes claros y estructurados.

---

## 1.5 Seed de datos

- [x] Crear `backend/seed.py`.

### Productos
- [x] Crear al menos 30 productos (se crearon 35 productos industriales clasificados).
- [x] Variar categorías (6 categorías diferentes).
- [x] Variar precios ($3.990 a $389.990).
- [x] Variar stock (0 a 200 unidades, incluyendo caso borde de stock agotado).
- [x] Incluir productos con y sin imagen (para probar placeholders/fallbacks).

### Idempotencia
- [x] Ejecutar el seed más de una vez sin crear duplicados.
- [x] Utilizar SKU para identificar productos existentes.

### Kardex
- [x] Generar movimientos de ejemplo.
- [x] Incluir entradas.
- [x] Incluir salidas.
- [x] Incluir diferentes costos de entrada (demostrando el cálculo de Promedio Ponderado Móvil).

---

# 🎨 FASE 2 — Frontend (Next.js 14+ App Router)

---

## 2.1 Configuración y cliente API

- [x] Crear proyecto Next.js 14+ (Next.js 16 con App Router y Turbopack).
- [x] Configurar TypeScript (tsconfig.json, tipos estrictos y alias @/*).
- [x] Configurar Tailwind CSS (@tailwindcss/postcss y @import "tailwindcss" en globals.css).
- [x] Crear tipos en:

```text
src/types/
```

- [x] Mantener tipos alineados con contratos de la API (Product, ProductListResponse, ProductQueryParams, KardexLine, ProductKardexResponse, ImportResult, RowError).
- [x] Implementar cliente HTTP en:

```text
src/lib/api.ts
```

---

## 2.2 Vista de listado `/products`

### Búsqueda y filtros
- [x] Barra de búsqueda por texto.
- [x] Filtro por categoría.
- [x] Filtro por precio mínimo.
- [x] Filtro por precio máximo.

---

### Tabla
- [x] Mostrar miniatura con `next/image`.
- [x] Mostrar SKU.
- [x] Mostrar nombre.
- [x] Mostrar categoría.
- [x] Mostrar precio.
- [x] Mostrar stock.

---

### Navegación
- [x] Hacer la fila completa navegable (`cursor: pointer`).
- [x] Navegar a:

```text
/products/[id]
```

---

### Paginación
- [x] Mostrar controles de paginación.
- [x] Sincronizar página con query params de la URL.
- [x] Mantener filtros al cambiar página.

Ejemplo:
```text
/products?q=taladro&categoria=Herramientas&page=2
```

---

### Estados UI
- [x] Loading (Skeleton o spinner).
- [x] Empty state ("No se encontraron productos con los filtros seleccionados").
- [x] Error de red ("No fue posible cargar los productos. Intenta nuevamente").
- [x] Reintento cuando corresponda.

---

## 2.3 Vista de detalle `/products/[id]`

### Información
- [x] Mostrar información completa (nombre, SKU, categoría, precio, stock, descripción y metadatos).
- [x] Mostrar imagen destacada con `next/image`.
- [x] Implementar placeholder (cuando el producto no tiene URL de imagen).
- [x] Implementar fallback para imágenes inválidas (manejador onError con placeholder SVG).

---

### Navegación
- [x] Botón claro de regreso al listado ("Volver al catálogo" y breadcrumb interactivo).

---

### Kardex
- [x] Consultar endpoint de Kardex (`GET /products/{id}/kardex`).
- [x] Mostrar tabla de movimientos (`KardexTable.tsx`).
- [x] Mostrar tipo (Badges diferenciados Entrada / Salida).
- [x] Mostrar fecha (formateada DD/MM/AAAA HH:mm).
- [x] Mostrar cantidad (+ para entrada, - para salida).
- [x] Mostrar costo unitario.
- [x] Mostrar documento de referencia (FAC-xxx, GUIA-xxx).
- [x] Mostrar saldo acumulado en unidades.
- [x] Mostrar valor acumulado monetario.
- [x] Mostrar costo promedio cuando corresponda (Promedio Ponderado Móvil).

---

### Errores
- [x] Manejar producto inexistente.
- [x] Mostrar estado 404 comprensible (tarjeta 404 con código de error, mensaje amigable y botón de retorno al catálogo).

---

## 2.4 Módulo de Importación Excel

- [x] Crear vista o modal de importación (`/import` y `ImportForm.tsx`).
- [x] Permitir seleccionar archivo `.xlsx` (mediante selector de archivos o drag and drop).
- [x] Validar que se haya seleccionado un archivo (validación de extensión .xlsx/.xlsm y tamaño).
- [x] Mostrar estado de carga durante el upload (spinner animado y mensaje explicativo).
- [x] Enviar archivo al backend (`POST /products/import` con multipart/form-data).
- [x] Mostrar resumen:
  - [x] `leidas`
  - [x] `insertadas`
  - [x] `actualizadas`
  - [x] `rechazadas`
- [x] Mostrar lista de errores por fila (tabla con fila, campo afectado y motivo detallado).
- [x] Permitir volver al listado después de la importación (botón "Ver catálogo actualizado").
- [x] Refrescar productos cuando sea necesario (enlace directo a /products con recarga de catálogo).

---

# 🧪 FASE 3 — Suite de pruebas automatizadas

---

## 3.1 Pruebas unitarias

### `test_criteria.py`
- [x] Búsqueda por nombre.
- [x] Búsqueda por SKU.
- [x] Filtro por categoría.
- [x] Precio mínimo.
- [x] Precio máximo.
- [x] Rango de precios.
- [x] Ordenamiento ascendente.
- [x] Ordenamiento descendente.
- [x] Paginación.
- [x] Página fuera de rango.
- [x] Combinación de filtros.
- [x] Validación de campos permitidos.
- [x] Validación de operadores.

---

### `test_kardex.py`
- [ ] Entrada inicial.
- [ ] Cálculo de saldo inicial.
- [ ] Múltiples entradas.
- [ ] Entradas a costos distintos.
- [ ] Recalcular promedio ponderado.
- [ ] Salida de existencias.
- [ ] Mantener costo promedio en salida.
- [ ] Validar saldo en unidades.
- [ ] Validar saldo monetario.
- [ ] Validar comportamiento ante stock insuficiente.

---

## 3.2 Pruebas de integración

### `test_products_api.py`

#### Listado
- [x] `GET /products` retorna 200.
- [x] Validar contrato de respuesta (`items`, `total`, `page`, `page_size`).
- [x] Validar paginación.

#### Búsqueda
- [x] Búsqueda combinada.
- [x] Búsqueda sin resultados:

Resultado esperado:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

#### Detalle
- [x] Producto existente retorna 200.
- [x] Producto inexistente retorna 404.

#### Kardex
- [x] Endpoint de Kardex para producto existente.
- [x] Kardex vacío si el producto no tiene movimientos.
- [x] Producto inexistente retorna 404.

---

# 🐳 FASE 4 — Docker y reproducibilidad

---

## Backend
- [ ] Crear `backend/Dockerfile`.
- [ ] Utilizar build multi-stage cuando aporte valor.
- [ ] Instalar dependencias.
- [ ] Ejecutar aplicación FastAPI.

---

## Frontend
- [ ] Crear `frontend/Dockerfile`.
- [ ] Utilizar build multi-stage.
- [ ] Ejecutar aplicación Next.js.

---

## Docker Compose
- [ ] Crear `docker-compose.yml`.

### Servicios
- [ ] `db` (PostgreSQL)
- [ ] `backend`
- [ ] `frontend`

---

## Seed
- [ ] Ejecutar seed automáticamente si la base está vacía.
- [ ] Verificar que sea idempotente.
- [ ] Evitar duplicados al reiniciar contenedores.

---

## Validación
- [ ] Ejecutar:

```bash
docker compose up --build
```

- [ ] Confirmar que PostgreSQL levanta.
- [ ] Confirmar que backend levanta.
- [ ] Confirmar que frontend levanta.
- [ ] Confirmar comunicación frontend-backend.
- [ ] Confirmar datos disponibles.

---

# 📖 FASE 5 — README y documentación de entrega

- [ ] Explicar requisitos previos.
- [ ] Explicar ejecución local:
  - Documentar `docker compose up db`.
  - Documentar backend (`uvicorn app.main:app --reload`).
  - Documentar frontend (`npm run dev`).
- [ ] Documentar Docker completo (`docker compose up --build`).

---

## Tests
- [ ] Documentar comando exacto:

```bash
pytest
```

- [ ] Indicar desde qué carpeta se ejecuta (`backend/`).

---

## Documentación funcional
- [ ] Responder preguntas de negocio:
  - Explicar SKU y unicidad.
  - Explicar Kardex.
  - Explicar método de valorización (Promedio Ponderado Móvil).
  - Explicar stock físico vs disponible.

---

## Decisiones
- [ ] Incluir sección de decisiones técnicas.
- [ ] Incluir Criteria.
- [ ] Incluir SQLModel.
- [ ] Incluir estrategia de base de datos.
- [ ] Incluir Excel.
- [ ] Incluir Kardex.
- [ ] Incluir decisiones UX.
- [ ] Incluir funcionalidades fuera de alcance.

---

# 🚀 FASE 6 — Verificación y entrega

---

## Entorno limpio
- [ ] Clonar el repositorio en un entorno limpio.
- [ ] Seguir únicamente el README.
- [ ] Levantar con Docker.
- [ ] Verificar funcionamiento completo.

---

## Calidad
- [ ] No dejar `print()` de debugging.
- [ ] No dejar código comentado innecesario.
- [ ] No dejar credenciales.
- [ ] Revisar variables de entorno.
- [ ] Revisar errores HTTP.
- [ ] Revisar nombres y estructura.

---

## Git
- [ ] Revisar historial de commits.
- [ ] Usar mensajes descriptivos.
- [ ] Evitar commits genéricos (`fix`, `asdf`, `wip`, `test`).

---

## Validación final
- [ ] Todos los tests pasan.
- [ ] API disponible en `/docs`.
- [ ] Seed funcional.
- [ ] Docker funcional.
- [ ] Listado funcional.
- [ ] Filtros funcionales.
- [ ] Paginación funcional.
- [ ] Detalle funcional.
- [ ] Excel funcional.
- [ ] Kardex funcional.
- [ ] README completo.

---

# 🎯 Criterio final de entrega

La prueba se considera lista únicamente cuando se cumpla:

```text
Requisitos funcionales
        +
Requisitos técnicos
        +
Pruebas
        +
Reproducibilidad
        +
Documentación
```

La prioridad final es entregar una solución **completa y defendible**, evitando agregar funcionalidades que aumenten el alcance sin aportar directamente a los criterios de evaluación.
