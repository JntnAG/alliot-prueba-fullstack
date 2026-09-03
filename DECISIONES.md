# 📓 Bitácora de Decisiones — Prueba Técnica Fullstack (Alliot)

> Este documento registra las principales decisiones de negocio, arquitectura, implementación, experiencia de usuario y pruebas tomadas durante el desarrollo de la solución.
>
> Su propósito es explicar con claridad **qué se hizo, por qué se hizo así y qué alternativas fueron consideradas**, priorizando una solución simple, mantenible, reproducible y coherente con el alcance de la prueba técnica.
>
> La solución se diseñó para cumplir los requisitos obligatorios de la prueba y, adicionalmente, implementar los puntos extra de mayor valor cuando estos aportan claridad y mantenibilidad sin comprometer la simplicidad de la entrega.

---

# 🎯 Comprensión del negocio

## 1. ¿Qué es un SKU y por qué debe ser único?

El **SKU (Stock Keeping Unit)** es un identificador interno utilizado por una empresa para gestionar, rastrear y distinguir productos o variantes específicas, por ejemplo según talla, color, modelo o presentación.

El SKU debe identificar de manera **única e inequívoca** un producto dentro del catálogo.

Debe ser único porque el sistema necesita asociar correctamente:

* Inventario.
* Movimientos de Kardex.
* Importaciones.
* Actualizaciones.
* Consultas.
* Operaciones comerciales.

Un SKU duplicado podría provocar que una actualización o movimiento de inventario se asigne al producto incorrecto, generando inconsistencias.

El **nombre del producto** es descriptivo y comercial. Puede cambiar por razones de marketing e incluso puede repetirse entre productos similares.

El **código de barras**, como EAN o UPC, está orientado a estándares de identificación y lectura automática mediante escáneres. El SKU, en cambio, sigue una lógica interna definida por la organización.

---

## 2. ¿Para qué sirve un Kardex y qué relación tiene con la valorización del stock?

El **Kardex** es un registro cronológico de los movimientos de inventario de un producto.

Permite conocer:

* Entradas.
* Salidas.
* Saldo acumulado.
* Cantidad disponible.
* Valor monetario del inventario.

Además de conocer el saldo en unidades, el Kardex permite determinar el valor económico del inventario según un método de valorización.

Por esta razón, resulta útil para:

* Control de inventario.
* Auditorías.
* Trazabilidad.
* Análisis de costos.
* Conocer el valor económico de las existencias.

---

## 3. Si un mismo producto se compró en distintas fechas a distintos costos, ¿qué costo usaría para valorizar el saldo y por qué?

Para esta solución se utilizará el método de **Promedio Ponderado Móvil**.

Cada vez que ingresa nuevo inventario, se recalcula el costo promedio considerando:

* El valor de las unidades existentes.
* El valor de las nuevas unidades adquiridas.

Las salidas posteriores se valorizan utilizando el costo promedio vigente.

Se selecciona este método porque:

* Proporciona una valoración consistente.
* No depende de rastrear lotes específicos.
* Es sencillo de explicar e implementar.
* Permite realizar cálculos deterministas.
* Se adapta correctamente al alcance de esta prueba.

---

## 4. ¿Qué diferencia hay entre el stock físico y el stock disponible para la venta? ¿Cómo lo reflejarías en el modelo de datos?

El **stock físico** representa las unidades realmente existentes en una ubicación física.

El **stock disponible para la venta** representa las unidades que pueden comprometerse comercialmente después de descontar unidades reservadas, bloqueadas, dañadas o comprometidas en pedidos.

En un sistema de inventario más completo podría representarse como:

```text
stock_disponible = stock_fisico - stock_reservado
```

El modelo podría incluir:

```text
stock_fisico
stock_reservado
stock_disponible
```

Para el alcance de esta prueba, dado que el modelo obligatorio solicita un único campo `stock`, se adopta la simplificación de interpretarlo como:

> **Unidades disponibles para la venta.**

---

# 📁 Estructura del proyecto

```text
alliot-prueba/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   └── stock_movement.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── product.py
│   │   │   ├── import_result.py
│   │   │   └── kardex.py
│   │   │
│   │   ├── routers/
│   │   │   ├── products.py
│   │   │   ├── imports.py
│   │   │   └── kardex.py
│   │   │
│   │   ├── services/
│   │   │   ├── product_service.py
│   │   │   ├── import_service.py
│   │   │   └── kardex_service.py
│   │   │
│   │   └── criteria/
│   │       ├── filters.py
│   │       ├── product_criteria.py
│   │       └── criteria_builder.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_criteria.py
│   │   │   └── test_kardex.py
│   │   │
│   │   └── integration/
│   │       └── test_products_api.py
│   │
│   ├── seed.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── products/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   └── import/
│   │   │       └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ProductTable.tsx
│   │   │   ├── ProductFilters.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── ImportForm.tsx
│   │   │   └── KardexTable.tsx
│   │   │
│   │   ├── types/
│   │   └── lib/
│   │
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── README.md
└── DECISIONES.md
```

---

# 🗓️ Decisiones técnicas

---

## [DEC-001] Base de datos y estrategia de entornos

### Contexto

La aplicación debe poder ejecutarse de forma reproducible en un equipo limpio y mediante Docker Compose.

### Decisión

El entorno principal utiliza:

```text
PostgreSQL + Docker Compose
```

El modo local oficial utiliza PostgreSQL levantado mediante Docker:

```bash
docker compose up db
```

Posteriormente:

```bash
cd backend
uvicorn app.main:app --reload
```

y:

```bash
cd frontend
npm run dev
```

SQLite puede utilizarse opcionalmente para desarrollo rápido mediante:

```text
DATABASE_URL=sqlite:///./alliot.db
```

pero no constituye el entorno principal documentado para la entrega.

### Justificación

PostgreSQL proporciona un entorno consistente y cercano a una aplicación real.

Docker permite que la solución pueda ejecutarse sin depender de instalaciones manuales específicas en el equipo del evaluador.

---

## [DEC-002] Patrón de capas y responsabilidades

### Contexto

Evitar que los endpoints HTTP acumulen lógica de negocio y consultas de base de datos.

### Decisión

La solución se organiza en las siguientes responsabilidades.

### Router

Responsable de:

* Recibir solicitudes HTTP.
* Validar parámetros.
* Convertir parámetros HTTP en objetos de entrada o Criteria.
* Delegar la ejecución al servicio.
* Retornar respuestas HTTP.

### Criteria

Responsable de representar la intención de búsqueda independientemente del framework HTTP y del ORM.

### Service

Responsable de implementar casos de uso:

* Consulta de productos.
* Consulta de detalle.
* Importación Excel.
* Consulta de Kardex.
* Cálculo de valorización.

### Models

Representan las entidades persistidas.

### Schemas

Representan contratos de entrada y salida de la API cuando estos difieren de las entidades persistidas.

### Flujo

```text
HTTP Request
      ↓
Router
      ↓
Schema / Criteria
      ↓
Service
      ↓
SQLModel / ORM
      ↓
Database
```

### Justificación

Esta separación permite:

* Probar lógica de negocio sin levantar el servidor.
* Mantener endpoints simples.
* Evitar duplicación de lógica.
* Modificar reglas de negocio sin modificar la capa HTTP.

---

## [DEC-003] Modelo de Producto y unicidad del SKU

### Contexto

El producto es la entidad principal del sistema y debe contener todos los campos obligatorios definidos en la prueba.

### Campos

* `id`
* `sku`
* `nombre`
* `descripcion`
* `categoria`
* `precio`
* `stock`
* `imagen_url`

### Modelo base

```python
from decimal import Decimal

from sqlmodel import SQLModel, Field


class ProductBase(SQLModel):
    sku: str
    nombre: str
    descripcion: str | None = None
    categoria: str
    precio: Decimal
    stock: int = 0
    imagen_url: str | None = None
```

### Modelo persistente

El SKU debe estar garantizado como único también a nivel de base de datos.

```python
from sqlalchemy import UniqueConstraint


class Product(ProductBase, table=True):
    __table_args__ = (
        UniqueConstraint("sku", name="uq_product_sku"),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    sku: str = Field(index=True)
```

### Schema de creación

```python
class ProductCreate(ProductBase):
    pass
```

### Schema de lectura

```python
class ProductRead(ProductBase):
    id: int
```

### Justificación

El índice mejora las consultas por SKU.

La restricción `UniqueConstraint` garantiza que la unicidad no dependa únicamente de validaciones de aplicación.

Esto evita inconsistencias incluso si existen:

* Importaciones concurrentes.
* Scripts externos.
* Procesos directos sobre la base de datos.

Para valores monetarios se utiliza `Decimal`, evitando problemas de precisión asociados al uso de `float`.

---

## [DEC-004] Contrato de API para listado de productos

### Endpoint

```text
GET /products
```

### Parámetros

```text
page
page_size
q
categoria
precio_min
precio_max
```

### Ejemplo

```text
GET /products?page=1&page_size=20&q=taladro&categoria=Herramientas&precio_min=10000&precio_max=500000
```

### Respuesta

```python
from pydantic import BaseModel


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    total: int
    page: int
    page_size: int
```

Ejemplo:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

### Justificación

La respuesta contiene toda la información necesaria para que el frontend pueda:

* Renderizar resultados.
* Calcular páginas.
* Conocer el total.
* Mostrar estados vacíos.

---

## [DEC-005] Patrón Criteria para filtros

### Contexto

Los filtros pueden crecer o modificarse.

La lógica de cómo se traduce un filtro a una consulta no debe estar dispersa en el endpoint.

### Operadores

```python
from enum import Enum


class FilterOperator(str, Enum):
    EQUAL = "eq"
    CONTAINS = "contains"

    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"

    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"

    BETWEEN = "between"
```

### Campos permitidos

```python
class ProductField(str, Enum):
    SKU = "sku"
    NOMBRE = "nombre"
    CATEGORIA = "categoria"
    PRECIO = "precio"
```

### Filtro

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Filter:
    field: ProductField
    operator: FilterOperator
    value: Any
```

### Criteria

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductCriteria:
    filters: list[Filter] = field(
        default_factory=list
    )

    page: int = 1
    page_size: int = 20

    order_by: ProductField = ProductField.NOMBRE
    order_dir: str = "asc"
```

### Flujo

```text
HTTP Query Parameters
        ↓
Criteria Builder
        ↓
ProductCriteria
        ↓
Criteria Interpreter
        ↓
SQLModel Query
```

### Justificación

El Criteria representa:

> **Qué se desea buscar.**

La capa de interpretación decide:

> **Cómo traducir esa intención a una consulta.**

Esto permite:

* Restringir campos permitidos.
* Validar operadores.
* Evitar SQL construido manualmente.
* Probar filtros sin servidor.
* Mantener el router desacoplado de la lógica del ORM.

---

## [DEC-006] ORM: SQLModel

### Decisión

Se utiliza SQLModel para la persistencia.

### Justificación

SQLModel permite trabajar sobre el ecosistema SQLAlchemy y se integra naturalmente con modelos utilizados en aplicaciones FastAPI.

Reduce parte de la duplicación entre:

* Persistencia.
* Tipos.
* Validación.

### Separación adicional

Aunque SQLModel puede utilizarse en ambos contextos, se mantienen schemas específicos cuando representan contratos distintos.

Esto evita exponer accidentalmente:

* Campos internos.
* Identificadores generados.
* Campos no permitidos en creación.
* Campos futuros de persistencia.

---

## [DEC-007] Manejo de errores HTTP

### Decisión

La API utiliza códigos HTTP apropiados.

Ejemplos:

```text
404 Not Found
```

para productos inexistentes.

```text
422 Unprocessable Entity
```

para parámetros o datos inválidos.

```text
500 Internal Server Error
```

únicamente para errores inesperados.

### Justificación

Los errores deben ser comprensibles para el cliente y diferenciar claramente entre:

* Recurso inexistente.
* Entrada inválida.
* Error interno.

---

# 📦 Importación masiva desde Excel

---

## [DEC-008] Importación Excel con procesamiento parcial

### Contexto

Un archivo Excel puede contener registros válidos e inválidos simultáneamente.

### Decisión

La validación se realiza fila por fila.

Una fila inválida no invalida las demás.

### Reglas

#### SKU duplicado dentro del archivo

Se rechaza.

#### SKU existente en base de datos

Se actualiza.

```text
SKU no existe
      ↓
INSERT

SKU existe
      ↓
UPDATE
```

#### Fila inválida

Se reporta y no se procesa.

### Respuesta

```json
{
  "leidas": 50,
  "insertadas": 45,
  "actualizadas": 3,
  "rechazadas": 2,
  "errores": [
    {
      "fila": 12,
      "campo": "precio",
      "motivo": "Valor no numérico o negativo"
    },
    {
      "fila": 24,
      "campo": "sku",
      "motivo": "SKU duplicado dentro del archivo"
    }
  ]
}
```

### Justificación

Esto permite aprovechar los registros correctos sin obligar al usuario a corregir todo el archivo por un único error.

---

## [UX-001] Formulario de importación Excel

### Decisión

El frontend incluye una interfaz para importar productos desde un archivo Excel.

Flujo:

```text
Seleccionar archivo .xlsx
        ↓
Validar selección
        ↓
Subir archivo
        ↓
Estado de carga
        ↓
Resultado
```

### El resultado muestra

* Filas leídas.
* Productos insertados.
* Productos actualizados.
* Productos rechazados.
* Errores por fila.

### Ejemplo visual

```text
Importación completada

Leídas:          50
Insertadas:      45
Actualizadas:     3
Rechazadas:       2

Errores:
Fila 12 → precio inválido
Fila 24 → SKU duplicado
```

### Justificación

El usuario recibe retroalimentación comprensible sin tener que interpretar manualmente la respuesta JSON del backend.

---

# 📊 Kardex y valorización

---

## [DEC-009] Modelo de movimientos de inventario

### Modelo

```python
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field


class MovementType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class StockMovement(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    product_id: int = Field(
        foreign_key="product.id",
        index=True,
    )

    date: datetime

    movement_type: MovementType

    quantity: int

    unit_cost: Decimal

    reference_document: str
```

### Datos registrados

Cada movimiento contiene:

* Fecha.
* Tipo.
* Cantidad.
* Costo unitario.
* Documento de referencia.

---

## [DEC-010] Método de valorización: Promedio Ponderado Móvil

### Fórmula

```text
Nuevo costo promedio =
(
    Valor del stock anterior
    +
    Valor de la nueva entrada
)
/
Unidades totales
```

Formalmente:

```text
Nuevo Costo Unitario =
(
    (Stock Anterior × Costo Promedio Anterior)
    +
    (Cantidad Entrante × Costo Unitario Entrante)
)
/
(Stock Anterior + Cantidad Entrante)
```

### Entrada

Una entrada registra:

* Cantidad.
* Costo unitario.
* Fecha.
* Documento.

La entrada recalcula el costo promedio.

### Salida

Una salida registra:

* Cantidad.
* Fecha.
* Documento.

El costo utilizado para valorizar la salida corresponde al costo promedio vigente.

La salida:

* Reduce unidades.
* Reduce valor.
* Mantiene el costo promedio vigente.

### Justificación

Este comportamiento permite mantener una valorización consistente sin necesidad de administrar lotes individuales.

---

## [DEC-011] Kardex como lógica pura

La lógica principal se implementa como una función independiente:

```python
calculate_kardex(movements)
```

La función recibe los movimientos en orden cronológico y calcula:

* Saldo acumulado de unidades.
* Saldo monetario.
* Costo promedio vigente.

### Justificación

La lógica queda desacoplada de:

* FastAPI.
* SQLModel.
* PostgreSQL.
* Docker.

Esto permite realizar pruebas unitarias deterministas sin infraestructura adicional.

---

## [UX-002] Kardex dentro del detalle del producto

### Ruta

```text
/products/[id]
```

### Decisión

La vista de detalle incluye una sección específica de Kardex.

La página presenta primero la información principal del producto y posteriormente su historial de inventario.

### La tabla de Kardex muestra

* Fecha.
* Tipo de movimiento.
* Cantidad.
* Costo unitario.
* Documento de referencia.
* Saldo acumulado en unidades.
* Saldo acumulado valorizado.

### Justificación

El detalle permite consultar simultáneamente:

1. El estado actual del producto.
2. La trazabilidad de los movimientos que llevaron a dicho estado.

---

# 🖼️ Frontend y experiencia de usuario

---

## [UX-003] Tabla de productos

La vista principal muestra:

* SKU.
* Nombre.
* Categoría.
* Precio.
* Stock.

La información se presenta inicialmente en formato tabular.

---

## [UX-004] Fila completa navegable

La fila completa permite navegar al detalle:

```text
/products/[id]
```

### Justificación

Esto proporciona un área interactiva amplia y evita depender únicamente de un botón pequeño.

---

## [UX-005] Estados explícitos

La interfaz contempla:

### Loading

```text
Cargando productos...
```

### Success

Listado de productos.

### Empty

```text
No se encontraron productos con los filtros seleccionados.
```

### Error

```text
No fue posible cargar los productos.
Intenta nuevamente.
```

### Justificación

Una pantalla vacía no debe utilizarse para representar simultáneamente:

* Sin resultados.
* Carga.
* Error.

Cada estado debe ser identificable.

---

## [UX-006] Filtros persistentes en URL

Ejemplo:

```text
/products?q=taladro&categoria=Herramientas&page=2
```

### Justificación

Permite:

* Compartir búsquedas.
* Recargar sin perder filtros.
* Utilizar navegación atrás y adelante.
* Mantener estados reproducibles.

---

## [UX-007] Diseño responsive

En pantallas grandes se utiliza una tabla.

En pantallas pequeñas la información se reorganiza para evitar:

* Scroll horizontal excesivo.
* Columnas ilegibles.
* Botones difíciles de utilizar.

La interfaz debe continuar mostrando los datos esenciales.

---

# 🖼️ Estrategia de imágenes

---

## [UX-008] Imágenes y fallback

Se utiliza `next/image`.

El sistema contempla:

1. Imagen real cuando existe `imagen_url`.
2. Placeholder cuando no existe URL.
3. Fallback cuando la imagen falla.
4. Miniatura en listado.
5. Imagen de mayor tamaño en detalle.

Los dominios externos permitidos se configuran mediante:

```text
remotePatterns
```

en la configuración de Next.js.

---

# 🧪 Estrategia de pruebas

---

## Pruebas unitarias

Las pruebas unitarias no requieren:

* FastAPI levantado.
* Servidor HTTP.
* PostgreSQL.
* Docker.

---

## `test_criteria.py`

Se prueban:

* Búsqueda por nombre.
* Búsqueda por SKU.
* Categoría.
* Precio mayor que.
* Precio mayor o igual.
* Precio menor que.
* Precio menor o igual.
* Rango de precio.
* Combinación de filtros.
* Orden ascendente.
* Orden descendente.
* Validación de campos.
* Validación de operadores.
* Paginación.
* Offset.
* Valores límite.
* Página fuera de rango.

---

## `test_kardex.py`

Se prueban:

* Entrada inicial.
* Saldo inicial.
* Múltiples entradas.
* Costos diferentes.
* Promedio ponderado móvil.
* Salidas.
* Conservación del costo promedio.
* Saldo acumulado.
* Saldo monetario.
* Stock insuficiente.

---

## Pruebas de integración

### `test_products_api.py`

Se prueban:

```text
GET /products
```

Validando:

* Código HTTP.
* Estructura de respuesta.
* `items`.
* `total`.
* `page`.
* `page_size`.

### Filtros

Se prueban combinaciones de:

* Búsqueda.
* Categoría.
* Precio.
* Paginación.

### Detalle

```text
GET /products/{id}
```

Producto existente:

```text
200 OK
```

Producto inexistente:

```text
404 Not Found
```

### Caso borde

Búsqueda sin resultados:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

---

## Ejecutar pruebas

Desde la carpeta `backend/`:

```bash
pytest
```

Alternativamente:

```bash
pytest tests/
```

El README incluirá el comando exacto utilizado para validar la entrega.

---

# 🌱 Datos de prueba

Se incluye un script de seed con al menos 30 productos.

El seed permite probar:

* Listado.
* Paginación.
* Búsqueda.
* Categorías.
* Precios.
* Detalle.

Ejemplo:

```bash
python seed.py
```

El proceso exacto también se documenta para la ejecución mediante Docker.

---

# 🐳 Reproducibilidad

---

## Modo local

### Base de datos

```bash
docker compose up db
```

### Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Modo Docker

Desde la raíz:

```bash
docker compose up --build
```

El sistema debe levantar:

```text
PostgreSQL
    +
FastAPI
    +
Next.js
```

sin pasos manuales adicionales no documentados.

---

# 📄 Variables de entorno

Se incluye:

```text
.env.example
```

con valores de ejemplo.

No se incluyen:

* Contraseñas reales.
* Tokens reales.
* API Keys.
* Credenciales de producción.

---

# 🔍 Delimitación del alcance

| Aspecto              | Decisión         | Justificación                                                                                                  |
| -------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------- |
| CRUD manual completo | Fuera de alcance | El requisito principal se centra en listado y detalle; la creación masiva se cubre mediante importación Excel. |
| Autenticación        | Fuera de alcance | No fue solicitada y añadirla aumenta complejidad sin aportar directamente a la evaluación.                     |
| Roles                | Fuera de alcance | No existen requisitos de usuarios ni permisos.                                                                 |
| Deploy cloud         | Fuera de alcance | Docker Compose demuestra reproducibilidad sin añadir infraestructura adicional.                                |
| WebSockets           | Mejora futura    | No son necesarios para los requisitos actuales.                                                                |
| Redis                | Mejora futura    | No se justifica para el tamaño esperado del catálogo.                                                          |

---

# 🚀 Mejoras futuras

Con mayor tiempo se podrían implementar:

1. **Redis**

   * Caché de consultas frecuentes.

2. **WebSockets o Server-Sent Events**

   * Actualización de inventario en tiempo real.

3. **Paginación por cursor**

   * Mejor comportamiento con datasets grandes.

4. **Playwright**

   * Pruebas End-to-End.

5. **GitHub Actions**

   * Tests automáticos.
   * Validación de build.
   * Automatización CI/CD.

6. **Observabilidad**

   * Logs estructurados.
   * Métricas.
   * Trazabilidad.

---

# ✅ Checklist final antes de entregar

## Reproducibilidad

* [ ] Clonar el repositorio en una carpeta limpia.
* [ ] Seguir el README literalmente.
* [ ] Crear `.env` desde `.env.example`.
* [ ] Ejecutar `docker compose up --build`.
* [ ] Verificar PostgreSQL.
* [ ] Verificar FastAPI.
* [ ] Verificar Next.js.
* [ ] Verificar `/docs`.

## Modelo

* [ ] Product contiene todos los campos requeridos.
* [ ] SKU tiene índice.
* [ ] SKU está garantizado como único en la base de datos.
* [ ] Precio utiliza un tipo adecuado para valores monetarios.

## Backend

* [ ] `GET /products` funciona.
* [ ] Paginación funciona.
* [ ] Búsqueda por nombre funciona.
* [ ] Búsqueda por SKU funciona.
* [ ] Filtro por categoría funciona.
* [ ] Rango de precio funciona.
* [ ] `GET /products/{id}` funciona.
* [ ] Producto inexistente retorna 404.
* [ ] Errores HTTP son claros.
* [ ] `/docs` está disponible.
* [ ] Existen al menos 30 productos de prueba.

## Frontend

* [ ] Tabla muestra SKU.
* [ ] Tabla muestra nombre.
* [ ] Tabla muestra categoría.
* [ ] Tabla muestra precio.
* [ ] Tabla muestra stock.
* [ ] Fila completa permite navegar.
* [ ] Detalle muestra todos los campos.
* [ ] Existe navegación de regreso.
* [ ] Existe estado Loading.
* [ ] Existe estado Empty.
* [ ] Existe estado Error.
* [ ] La interfaz funciona en pantallas pequeñas.

## Criteria

* [ ] Criteria implementado.
* [ ] Campos permitidos restringidos.
* [ ] Operadores validados.
* [ ] Sin concatenación manual de SQL.
* [ ] Paginación implementada.
* [ ] Ordenamiento implementado.

## Excel

* [ ] Existe endpoint de importación.
* [ ] Existe formulario de importación en frontend.
* [ ] Existe estado de carga.
* [ ] Se muestran insertadas.
* [ ] Se muestran actualizadas.
* [ ] Se muestran rechazadas.
* [ ] Se muestran errores por fila.
* [ ] SKU duplicado dentro del archivo se reporta.
* [ ] SKU existente se actualiza.
* [ ] Filas inválidas no invalidan las válidas.

## Kardex

* [ ] Se registran entradas.
* [ ] Se registran salidas.
* [ ] Se registra fecha.
* [ ] Se registra cantidad.
* [ ] Se registra costo unitario.
* [ ] Se registra documento de referencia.
* [ ] Se calcula saldo en unidades.
* [ ] Se calcula saldo monetario.
* [ ] Promedio ponderado móvil implementado.
* [ ] Kardex visible dentro del detalle del producto.
* [ ] Lógica de Kardex cubierta por tests.

## Pruebas

* [ ] Tests unitarios de filtros.
* [ ] Tests unitarios de paginación.
* [ ] Tests unitarios sin depender de servidor.
* [ ] Tests de integración del listado.
* [ ] Tests de integración del detalle.
* [ ] Test de 404.
* [ ] Test de caso borde.
* [ ] `pytest` pasa.
* [ ] README incluye el comando exacto para ejecutar tests.

## Imágenes

* [ ] Miniatura en listado.
* [ ] Imagen grande en detalle.
* [ ] Placeholder cuando no existe imagen.
* [ ] Fallback cuando falla la carga.

## Calidad

* [ ] No existen `print()` de debugging.
* [ ] No existe código comentado innecesariamente.
* [ ] Dependencias declaradas.
* [ ] README completo.
* [ ] No existen credenciales reales.
* [ ] Commits descriptivos.
* [ ] El proyecto funciona desde cero siguiendo únicamente el README.

---

# 🧠 Principio general de la solución

La solución prioriza:

```text
Simplicidad
    +
Claridad
    +
Separación de responsabilidades
    +
Pruebas significativas
    +
Reproducibilidad
```

sobre incorporar funcionalidades adicionales que no puedan ser correctamente terminadas, probadas y defendidas.

El objetivo no es utilizar la mayor cantidad posible de tecnologías, sino demostrar que cada componente fue seleccionado conscientemente y que las decisiones pueden explicarse y modificarse durante una revisión técnica.

La entrega prioriza una solución:

* Funcional.
* Completa dentro del alcance.
* Fácil de ejecutar.
* Fácil de probar.
* Fácil de explicar.
* Fácil de modificar durante una prueba técnica en vivo.
