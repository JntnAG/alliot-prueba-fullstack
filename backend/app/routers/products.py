"""
routers/products.py — Endpoints HTTP de Productos, Kardex e Importación Excel
=============================================================================

¿QUÉ HACE ESTE ARCHIVO? 
---------------------------------------------------
Este archivo es la "ventanilla de atención al público" de nuestra API para productos.
Aquí se definen las direcciones URL que el navegador web (Next.js) o cualquier cliente puede llamar:

1. `GET /products`: El catálogo paginado. Puedes pedir:
   - Búsqueda por texto (`q=taladro`)
   - Filtro por categoría (`categoria=Herramientas`)
   - Rango de precios (`precio_min=10000&precio_max=50000`)
   - Paginación (`page=2&page_size=20`)
   - Ordenamiento (`order_by=precio&order_dir=desc`)
   Traduce todo a un `ProductCriteria` y se lo pasa al `ProductService`.

2. `GET /products/{id}`: La ficha de detalle de un producto específico.
   Si el producto no existe, responde de inmediato con `404 Not Found`.

3. `GET /products/{id}/kardex`: El historial de movimientos e inventario valorizado.
   Calculado con el método de Promedio Ponderado Móvil. Retorna 404 si el producto no existe.

4. `POST /products/import`: Sube un archivo Excel (.xlsx) para carga masiva.
   Acepta registros válidos, actualiza existentes y reporta errores por fila (resiliencia parcial).
"""

from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlmodel import Session

from app.criteria import build_product_criteria_from_params
from app.database import get_session
from app.schemas.import_result import ImportResult
from app.schemas.kardex import ProductKardexResponse
from app.schemas.product import ProductListResponse, ProductRead
from app.services.import_service import ImportService
from app.services.kardex_service import KardexService
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Productos"],
)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar productos con filtros y paginación (Patrón Criteria)",
)
def list_products(
    q: Optional[str] = Query(None, description="Búsqueda por texto (coincidencia en nombre o SKU)"),
    categoria: Optional[str] = Query(None, description="Filtro exacto por categoría"),
    precio_min: Optional[Decimal] = Query(None, ge=0, description="Precio mínimo de venta"),
    precio_max: Optional[Decimal] = Query(None, ge=0, description="Precio máximo de venta"),
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Cantidad de productos por página (máx. 100)"),
    order_by: str = Query("nombre", description="Campo para ordenar: nombre, sku, categoria, precio"),
    order_dir: str = Query("asc", pattern="^(asc|desc|ASC|DESC)$", description="Dirección: asc o desc"),
    session: Session = Depends(get_session),
):
    """
    Retorna el catálogo paginado de productos aplicando el Patrón Criteria.
    """
    try:
        criteria = build_product_criteria_from_params(
            q=q,
            categoria=categoria,
            precio_min=precio_min,
            precio_max=precio_max,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return ProductService.get_products_response(session, criteria)


@router.post(
    "/import",
    response_model=ImportResult,
    summary="Importar catálogo masivo desde archivo Excel (.xlsx)",
)
def import_products_from_excel(
    file: UploadFile = File(..., description="Archivo Excel con extensión .xlsx"),
    session: Session = Depends(get_session),
):
    """
    Procesa un archivo .xlsx para inserción y actualización masiva de productos (DEC-008).
    
    Reglas de negocio aplicadas:
    - Validación fila por fila con resiliencia parcial (filas con error no anulan el resto).
    - SKU nuevo en BD -> INSERT.
    - SKU ya existente en BD -> UPDATE.
    - SKU duplicado dentro del archivo -> Se rechaza para evitar orden-dependencia.
    - Reporta total leídas, insertadas, actualizadas, rechazadas y detalle de errores por celda.
    """
    # Validar extensión del archivo
    filename = file.filename or ""
    if not (filename.lower().endswith(".xlsx") or filename.lower().endswith(".xlsm")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tipo de archivo no compatible. Solo se admiten archivos Excel con extensión .xlsx",
        )

    result = ImportService.process_excel(session, file.file)
    return result


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Obtener detalle de un producto por su ID",
)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    """
    Retorna toda la información de un producto específico.
    Si el producto no existe, retorna 404 Not Found.
    """
    product = ProductService.get_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado.",
        )
    return ProductRead.model_validate(product)


@router.get(
    "/{product_id}/kardex",
    response_model=ProductKardexResponse,
    summary="Consultar Kardex valorizado de un producto (Promedio Ponderado)",
)
def get_product_kardex(
    product_id: int,
    session: Session = Depends(get_session),
):
    """
    Retorna el historial cronológico de movimientos y el saldo acumulado en unidades
    y valor monetario calculado con el método de Promedio Ponderado Móvil (DEC-010 y DEC-011).
    """
    kardex_response = KardexService.get_kardex_for_product(session, product_id)
    if not kardex_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado.",
        )
    return kardex_response
