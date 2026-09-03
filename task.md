# 📋 Lista de Tareas — Prueba Técnica Fullstack (Alliot)

> **Stack:** FastAPI (Python 3.11+) + Next.js 14+ (App Router) + SQLModel + PostgreSQL / SQLite  
> **Criterio rector:** Simplicidad, consistencia arquitectural y foco en el negocio.  
> **Objetivo:** Implementar una solución reproducible que cubra los requisitos funcionales, técnicos, de pruebas y documentación definidos para la prueba técnica.

---

# 🏁 FASE 0 — Preparación del proyecto y arquitectura base

## Estructura inicial

- [ ] Inicializar la estructura de carpetas según el diseño acordado:

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

- [ ] Inicializar proyecto frontend con estructura:

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

- [ ] Crear `.env.example`.
- [ ] Configurar `DATABASE_URL`.
- [ ] Configurar PostgreSQL como entorno principal.
- [ ] Permitir SQLite como alternativa de desarrollo.
- [ ] Configurar `NEXT_PUBLIC_API_URL`.
- [ ] Verificar que no existan credenciales reales en el repositorio.

---

## Documentación inicial

- [ ] Crear `README.md`.
- [ ] Incluir descripción general del proyecto.
- [ ] Incluir requisitos previos.
- [ ] Reservar secciones para:
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

- [ ] Crear `backend/requirements.txt`.

Dependencias principales:
- [ ] `fastapi`
- [ ] `uvicorn`
- [ ] `sqlmodel`
- [ ] `psycopg2-binary`
- [ ] `python-dotenv`
- [ ] `openpyxl`
- [ ] `pytest`
- [ ] `httpx`

- [ ] Configurar `app/database.py`.
- [ ] Crear engine para PostgreSQL.
- [ ] Permitir engine SQLite mediante `DATABASE_URL`.
- [ ] Implementar generador `get_session`.
- [ ] Crear tablas al iniciar la aplicación o mediante el mecanismo definido para la prueba.
- [ ] Verificar arranque de FastAPI.
- [ ] Verificar documentación Swagger en:

```text
/docs
```

---

## 1.2 Modelos y Schemas

### Producto

- [ ] Implementar `app/models/product.py`.

#### `ProductBase`
- [ ] `sku`
- [ ] `nombre`
- [ ] `descripcion`
- [ ] `categoria`
- [ ] `precio` (usar `Decimal` para valores monetarios)
- [ ] `stock`
- [ ] `imagen_url`

#### `Product`
- [ ] Declarar tabla persistente (`table=True`).
- [ ] `id` como primary key.
- [ ] `sku` indexado.
- [ ] Garantizar unicidad de `sku` mediante constraint real en base de datos (`UniqueConstraint("sku", name="uq_product_sku")`).

#### Schemas
- [ ] Implementar `ProductCreate`.
- [ ] Implementar `ProductRead`.

---

### Movimientos de inventario

- [ ] Implementar `app/models/stock_movement.py`.

#### Enum
- [ ] `MovementType.ENTRY`
- [ ] `MovementType.EXIT`

#### `StockMovement`
- [ ] `id`
- [ ] `product_id` (foreign key a `product.id`, indexado)
- [ ] `date`
- [ ] `movement_type`
- [ ] `quantity`
- [ ] `unit_cost` (usar `Decimal`)
- [ ] `reference_document`

---

### Respuesta de listado

- [ ] Implementar `app/schemas/product.py`.

#### `ProductListResponse`
- [ ] `items: list[ProductRead]`
- [ ] `total: int`
- [ ] `page: int`
- [ ] `page_size: int`

---

### Schemas de importación

- [ ] Implementar `app/schemas/import_result.py`.

#### Resultado
- [ ] `leidas`
- [ ] `insertadas`
- [ ] `actualizadas`
- [ ] `rechazadas`
- [ ] `errores`

#### Error por fila
- [ ] Número de fila.
- [ ] Campo.
- [ ] Motivo.

---

### Schemas de Kardex

- [ ] Implementar `app/schemas/kardex.py`.
- [ ] Fecha.
- [ ] Tipo de movimiento.
- [ ] Cantidad.
- [ ] Costo unitario.
- [ ] Documento de referencia.
- [ ] Saldo acumulado en unidades.
- [ ] Saldo acumulado valorizado.
- [ ] Costo promedio vigente.

---

## 1.3 Patrón Criteria

### Filters

- [ ] Implementar `app/criteria/filters.py`.

#### `FilterOperator`
- [ ] `eq`
- [ ] `contains`
- [ ] `gt`
- [ ] `gte`
- [ ] `lt`
- [ ] `lte`
- [ ] `between`

#### `ProductField`
- [ ] `sku`
- [ ] `nombre`
- [ ] `categoria`
- [ ] `precio`

#### `Filter`
- [ ] Implementar dataclass:

```text
Filter(
    field,
    operator,
    value
)
```

---

### ProductCriteria

- [ ] Implementar `app/criteria/product_criteria.py`.

#### Campos
- [ ] `filters`
- [ ] `page`
- [ ] `page_size`
- [ ] `order_by`
- [ ] `order_dir`

---

### Criteria Builder

- [ ] Implementar `app/criteria/criteria_builder.py` para conversión de query parameters a `ProductCriteria`.

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

- [ ] Implementar en `services/product_service.py`.
- [ ] Traducir `ProductCriteria` a consultas SQLModel.
- [ ] Aplicar filtros en base de datos.
- [ ] Calcular total de registros.
- [ ] Aplicar ordenamiento.
- [ ] Aplicar paginación mediante `offset` y `limit`.

#### Principio
> Si mañana se agrega un nuevo filtro o cambia la consulta, no debe ser necesario modificar la firma del endpoint.

---

## 1.4 Endpoints y reglas de negocio

---

### Productos

#### Listado
- [ ] Implementar:

```text
GET /products
```

#### Query params
- [ ] `q`
- [ ] `categoria`
- [ ] `precio_min`
- [ ] `precio_max`
- [ ] `page`
- [ ] `page_size`
- [ ] `order_by`
- [ ] `order_dir`

#### Reglas
- [ ] Búsqueda por nombre.
- [ ] Búsqueda por SKU.
- [ ] Filtro por categoría.
- [ ] Filtro por rango de precio.
- [ ] Ordenamiento.
- [ ] Paginación.

---

### Detalle

- [ ] Implementar:

```text
GET /products/{id}
```

- [ ] Retornar producto completo.
- [ ] Retornar `404 Not Found` si no existe.

---

### Kardex

- [ ] Implementar:

```text
GET /products/{id}/kardex
```

- [ ] Retornar movimientos cronológicos.
- [ ] Retornar saldo acumulado en unidades.
- [ ] Retornar saldo valorizado.
- [ ] Retornar costo promedio.
- [ ] Retornar 404 si el producto no existe.

---

### Importación Excel

- [ ] Implementar endpoint:

```text
POST /imports/excel
```

- [ ] Recibir archivo `.xlsx`.
- [ ] Validar archivo.
- [ ] Procesar fila por fila.
- [ ] Detectar campos inválidos.
- [ ] Detectar precios inválidos.
- [ ] Detectar stocks inválidos.
- [ ] Detectar SKU duplicado dentro del archivo (rechazar para evitar orden-dependencia).
- [ ] Actualizar producto cuando SKU ya existe en BD (`UPDATE`).
- [ ] Insertar producto cuando SKU no existe en BD (`INSERT`).
- [ ] Continuar procesando filas válidas (resiliencia parcial).
- [ ] Reportar filas rechazadas con número de fila, campo y motivo.
- [ ] Retornar resumen final estructurado.

---

### Manejo de errores

- [ ] Retornar 404 para recursos inexistentes.
- [ ] Retornar 422 para parámetros o datos inválidos.
- [ ] Evitar usar 500 para errores de validación esperables.
- [ ] Retornar mensajes claros y estructurados.

---

## 1.5 Seed de datos

- [ ] Crear `backend/seed.py`.

### Productos
- [ ] Crear al menos 30 productos.
- [ ] Variar categorías.
- [ ] Variar precios.
- [ ] Variar stock.
- [ ] Incluir productos con y sin imagen.

### Idempotencia
- [ ] Ejecutar el seed más de una vez sin crear duplicados.
- [ ] Utilizar SKU para identificar productos existentes.

### Kardex
- [ ] Generar movimientos de ejemplo.
- [ ] Incluir entradas.
- [ ] Incluir salidas.
- [ ] Incluir diferentes costos de entrada.

---

# 🎨 FASE 2 — Frontend (Next.js 14+ App Router)

---

## 2.1 Configuración y cliente API

- [ ] Crear proyecto Next.js 14+.
- [ ] Configurar TypeScript.
- [ ] Configurar Tailwind CSS.
- [ ] Crear tipos en:

```text
src/types/
```

- [ ] Mantener tipos alineados con contratos de la API.
- [ ] Implementar cliente HTTP en:

```text
src/lib/api.ts
```

---

## 2.2 Vista de listado `/products`

### Búsqueda y filtros
- [ ] Barra de búsqueda por texto.
- [ ] Filtro por categoría.
- [ ] Filtro por precio mínimo.
- [ ] Filtro por precio máximo.

---

### Tabla
- [ ] Mostrar miniatura con `next/image`.
- [ ] Mostrar SKU.
- [ ] Mostrar nombre.
- [ ] Mostrar categoría.
- [ ] Mostrar precio.
- [ ] Mostrar stock.

---

### Navegación
- [ ] Hacer la fila completa navegable (`cursor: pointer`).
- [ ] Navegar a:

```text
/products/[id]
```

---

### Paginación
- [ ] Mostrar controles de paginación.
- [ ] Sincronizar página con query params de la URL.
- [ ] Mantener filtros al cambiar página.

Ejemplo:
```text
/products?q=taladro&categoria=Herramientas&page=2
```

---

### Estados UI
- [ ] Loading (Skeleton o spinner).
- [ ] Empty state ("No se encontraron productos con los filtros seleccionados").
- [ ] Error de red ("No fue posible cargar los productos. Intenta nuevamente").
- [ ] Reintento cuando corresponda.

---

## 2.3 Vista de detalle `/products/[id]`

### Información
- [ ] Mostrar información completa.
- [ ] Mostrar imagen destacada con `next/image`.
- [ ] Implementar placeholder.
- [ ] Implementar fallback para imágenes inválidas.

---

### Navegación
- [ ] Botón claro de regreso al listado.

---

### Kardex
- [ ] Consultar endpoint de Kardex.
- [ ] Mostrar tabla de movimientos (`KardexTable.tsx`).
- [ ] Mostrar tipo.
- [ ] Mostrar fecha.
- [ ] Mostrar cantidad.
- [ ] Mostrar costo unitario.
- [ ] Mostrar documento de referencia.
- [ ] Mostrar saldo acumulado en unidades.
- [ ] Mostrar valor acumulado monetario.
- [ ] Mostrar costo promedio cuando corresponda.

---

### Errores
- [ ] Manejar producto inexistente.
- [ ] Mostrar estado 404 comprensible.

---

## 2.4 Módulo de Importación Excel

- [ ] Crear vista o modal de importación (`/import` o `ImportForm.tsx`).
- [ ] Permitir seleccionar archivo `.xlsx`.
- [ ] Validar que se haya seleccionado un archivo.
- [ ] Mostrar estado de carga durante el upload.
- [ ] Enviar archivo al backend (`POST /imports/excel`).
- [ ] Mostrar resumen:
  - [ ] `leidas`
  - [ ] `insertadas`
  - [ ] `actualizadas`
  - [ ] `rechazadas`
- [ ] Mostrar lista de errores por fila.
- [ ] Permitir volver al listado después de la importación.
- [ ] Refrescar productos cuando sea necesario.

---

# 🧪 FASE 3 — Suite de pruebas automatizadas

---

## 3.1 Pruebas unitarias

### `test_criteria.py`
- [ ] Búsqueda por nombre.
- [ ] Búsqueda por SKU.
- [ ] Filtro por categoría.
- [ ] Precio mínimo.
- [ ] Precio máximo.
- [ ] Rango de precios.
- [ ] Ordenamiento ascendente.
- [ ] Ordenamiento descendente.
- [ ] Paginación.
- [ ] Página fuera de rango.
- [ ] Combinación de filtros.
- [ ] Validación de campos permitidos.
- [ ] Validación de operadores.

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
- [ ] `GET /products` retorna 200.
- [ ] Validar contrato de respuesta (`items`, `total`, `page`, `page_size`).
- [ ] Validar paginación.

#### Búsqueda
- [ ] Búsqueda combinada.
- [ ] Búsqueda sin resultados:

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
- [ ] Producto existente retorna 200.
- [ ] Producto inexistente retorna 404.

#### Kardex
- [ ] Endpoint de Kardex para producto existente.
- [ ] Kardex vacío si el producto no tiene movimientos.
- [ ] Producto inexistente retorna 404.

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
