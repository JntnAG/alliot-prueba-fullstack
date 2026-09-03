"""
seed.py — Poblamiento inicial de datos del sistema (Seed)
=========================================================

¿QUÉ HACE ESTE ARCHIVO?
---------------------------------------------------
Imagina que abres un supermercado nuevo: el local está completamente vacío.
Antes de abrir las puertas a los clientes, necesitas llenar las estanterías con
mercadería variada (herramientas, cascos, cables, pinturas...) para que el público
pueda buscar, filtrar y comprar.

Eso es un SEED: un script que siembra datos de prueba realistas en la base de datos.

¿QUÉ SIGNIFICA QUE SEA "IDEMPOTENTE"?
-------------------------------------
Idempotente significa que puedes ejecutar este script 1 vez o 50 veces seguidas,
y el resultado SIEMPRE será el mismo:
- NO duplicará productos.
- NO creará basura en la base de datos.
- Revisa el SKU de cada producto: si ya existe, lo respeta o lo sincroniza; si no existe, lo crea.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Dict, Any
from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models import MovementType, Product, StockMovement


# ─────────────────────────────────────────────────────────────────────────────
# Catálogo de al menos 30 productos industriales variados
# Cumple con el PDF y DECISIONES.md:
# - Variedad de categorías
# - Variedad de rangos de precio ($1.500 a $450.000)
# - Variedad de stock (incluyendo stock 0)
# - Productos con y sin imagen (para probar placeholders en frontend)
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTS_SEED_DATA: List[Dict[str, Any]] = [
    # Categoría: Herramientas Eléctricas
    {
        "sku": "HER-ELE-001",
        "nombre": "Taladro Percutor Industrial 850W",
        "descripcion": "Taladro de alta potencia con mandril metálico de 13mm y velocidad variable reversible.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("79990.00"),
        "stock": 18,
        "imagen_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=500",
    },
    {
        "sku": "HER-ELE-002",
        "nombre": "Esmeril Angular 4 1/2 Pulgadas 900W",
        "descripcion": "Amoladora angular con sistema de expulsión de polvo y traba de eje para cambio rápido.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("54990.00"),
        "stock": 25,
        "imagen_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=500",
    },
    {
        "sku": "HER-ELE-003",
        "nombre": "Sierra Circular de Mano 7 1/4 1800W",
        "descripcion": "Sierra para madera con guía láser y ajuste de bisel hasta 45 grados.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("119990.00"),
        "stock": 10,
        "imagen_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=500",
    },
    {
        "sku": "HER-ELE-004",
        "nombre": "Rotomartillo SDS Plus 3.2 Joules",
        "descripcion": "Martillo electroneumático para perforación pesada en concreto y cincelado ligero.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("189990.00"),
        "stock": 7,
        "imagen_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=500",
    },
    {
        "sku": "HER-ELE-005",
        "nombre": "Cepillo Eléctrico para Madera 650W",
        "descripcion": "Cepillo con base de aluminio maquinada y extracción de viruta bidireccional.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("89990.00"),
        "stock": 12,
        "imagen_url": None,  # Intencionalmente sin imagen para probar placeholder
    },
    {
        "sku": "HER-ELE-006",
        "nombre": "Lijadora Orbital 1/3 Hoja 240W",
        "descripcion": "Lijadora para acabados finos con recolector de polvo y agarre engomado.",
        "categoria": "Herramientas Eléctricas",
        "precio": Decimal("42990.00"),
        "stock": 15,
        "imagen_url": "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=500",
    },

    # Categoría: Herramientas Manuales
    {
        "sku": "HER-MAN-001",
        "nombre": "Juego de Llaves Combinadas 12 Piezas Cr-V",
        "descripcion": "Set de llaves de 6mm a 22mm fabricadas en acero cromo vanadio forjado.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("29990.00"),
        "stock": 40,
        "imagen_url": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=500",
    },
    {
        "sku": "HER-MAN-002",
        "nombre": "Alicate Universal Aislado 1000V 8 Pulgadas",
        "descripcion": "Alicate para electricista con certificación VDE y mordazas endurecidas por inducción.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("16990.00"),
        "stock": 50,
        "imagen_url": "https://images.unsplash.com/photo-1616401784845-180882ba9ba8?w=500",
    },
    {
        "sku": "HER-MAN-003",
        "nombre": "Martillo Carpintero con Mango de Fibra 16oz",
        "descripcion": "Martillo con uña recta para desencofrar y empuñadura ergonómica antivibración.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("12990.00"),
        "stock": 35,
        "imagen_url": None,  # Sin imagen para probar fallback
    },
    {
        "sku": "HER-MAN-004",
        "nombre": "Cutter Retráctil Metálico Extra Fuerte",
        "descripcion": "Cuchillo cartonero profesional con bloqueo de cuchilla y compartimento de repuestos.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("4990.00"),
        "stock": 120,
        "imagen_url": "https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?w=500",
    },
    {
        "sku": "HER-MAN-005",
        "nombre": "Huincha de Medir Antigolpes 8 Metros",
        "descripcion": "Cinta métrica con recubrimiento de nylon y gancho magnético triple remache.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("9990.00"),
        "stock": 80,
        "imagen_url": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=500",
    },
    {
        "sku": "HER-MAN-006",
        "nombre": "Nivel Torpedo Magnético 9 Pulgadas 3 Gotas",
        "descripcion": "Nivel de aluminio extruido con viales de 45, 90 y 180 grados de alta visibilidad.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("11490.00"),
        "stock": 28,
        "imagen_url": None,
    },

    # Categoría: Protección Personal (EPP)
    {
        "sku": "PRO-EPP-001",
        "nombre": "Casco de Seguridad Tipo Jockey con Arnés Cremallera",
        "descripcion": "Casco dieléctrico clase E y G con ranuras laterales para orejeras y barboquejo.",
        "categoria": "Protección Personal",
        "precio": Decimal("8990.00"),
        "stock": 95,
        "imagen_url": "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=500",
    },
    {
        "sku": "PRO-EPP-002",
        "nombre": "Antiparras de Seguridad Policarbonato Antiempañante",
        "descripcion": "Lentes de seguridad con protección UV400 y ventilación indirecta contra salpicaduras.",
        "categoria": "Protección Personal",
        "precio": Decimal("5490.00"),
        "stock": 150,
        "imagen_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500",
    },
    {
        "sku": "PRO-EPP-003",
        "nombre": "Zapatos de Seguridad Cuero Hidrofugado Talla 42",
        "descripcion": "Botín industrial con plantilla antiperforación y puntera de fibra no metálica.",
        "categoria": "Protección Personal",
        "precio": Decimal("44990.00"),
        "stock": 22,
        "imagen_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
    },
    {
        "sku": "PRO-EPP-004",
        "nombre": "Guantes de Nitrilo para Químicos Verde Talla L",
        "descripcion": "Guante resistente a solventes, aceites y grasas con interior floculado de algodón.",
        "categoria": "Protección Personal",
        "precio": Decimal("3990.00"),
        "stock": 200,
        "imagen_url": "https://images.unsplash.com/photo-1584744982491-665216d95f8b?w=500",
    },
    {
        "sku": "PRO-EPP-005",
        "nombre": "Respirador Medio Rostro Silicona con Filtros P100",
        "descripcion": "Máscara reutilizable con doble filtro contra polvos tóxicos, humos y neblinas.",
        "categoria": "Protección Personal",
        "precio": Decimal("28990.00"),
        "stock": 16,
        "imagen_url": "https://images.unsplash.com/photo-1605289982774-9a6fef564df8?w=500",
    },
    {
        "sku": "PRO-EPP-006",
        "nombre": "Arnés de Seguridad 4 Argollas Anticaídas",
        "descripcion": "Arnés de cuerpo entero ajustable con indicador de impacto y soporte lumbar acolchado.",
        "categoria": "Protección Personal",
        "precio": Decimal("59990.00"),
        "stock": 14,
        "imagen_url": None,
    },

    # Categoría: Electricidad e Iluminación
    {
        "sku": "ELE-ILU-001",
        "nombre": "Foco Proyector LED Exterior 100W IP65",
        "descripcion": "Proyector de alta eficiencia lumínica (10.000 lúmenes) cuerpo de aluminio inyectado.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("26990.00"),
        "stock": 35,
        "imagen_url": "https://images.unsplash.com/photo-1507499739999-097706ad8914?w=500",
    },
    {
        "sku": "ELE-ILU-002",
        "nombre": "Rollo Cable THHN 2.5mm Rojo 100 Metros",
        "descripcion": "Conductor de cobre electrolítico puro con aislación termoplástica retardante a la llama.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("48990.00"),
        "stock": 20,
        "imagen_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500",
    },
    {
        "sku": "ELE-ILU-003",
        "nombre": "Automático Termomagnético Bipolar 25A Curva C",
        "descripcion": "Disyuntor modular para riel DIN con poder de corte de 6kA.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("7490.00"),
        "stock": 65,
        "imagen_url": None,
    },
    {
        "sku": "ELE-ILU-004",
        "nombre": "Interruptor Diferencial Bipolar 25A 30mA",
        "descripcion": "Protector diferencial contra contactos directos e indirectos para tableros domiciliarios.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("14990.00"),
        "stock": 42,
        "imagen_url": None,
    },
    {
        "sku": "ELE-ILU-005",
        "nombre": "Carrete Alargador Profesional 25 Metros 3x1.5mm",
        "descripcion": "Extensión eléctrica con 4 tomas schuko, disyuntor térmico de seguridad y tambor metálico.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("38990.00"),
        "stock": 18,
        "imagen_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500",
    },
    {
        "sku": "ELE-ILU-006",
        "nombre": "Lámpara Portátil de Trabajo LED Batería Recargable",
        "descripcion": "Lámpara de inspección con gancho giratorio y base magnética para talleres.",
        "categoria": "Electricidad e Iluminación",
        "precio": Decimal("19990.00"),
        "stock": 24,
        "imagen_url": "https://images.unsplash.com/photo-1517524008697-84bbe3c3fd98?w=500",
    },

    # Categoría: Pinturas y Adhesivos
    {
        "sku": "PIN-ADH-001",
        "nombre": "Esmalte al Agua Satinado Blanco Tineta 5 Galones",
        "descripcion": "Pintura lavable de bajo olor para muros interiores y exteriores con fungicida.",
        "categoria": "Pinturas y Adhesivos",
        "precio": Decimal("62990.00"),
        "stock": 11,
        "imagen_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=500",
    },
    {
        "sku": "PIN-ADH-002",
        "nombre": "Silicona Neutra Multiuso Transparente 300ml",
        "descripcion": "Sellador monocomponente de silicona para vidrio, aluminio, cerámica y sanitarios.",
        "categoria": "Pinturas y Adhesivos",
        "precio": Decimal("4290.00"),
        "stock": 140,
        "imagen_url": None,
    },
    {
        "sku": "PIN-ADH-003",
        "nombre": "Espuma de Poliuretano Expansivo 750ml",
        "descripcion": "Aislante térmico y acústico para relleno de juntas en puertas, ventanas y tuberías.",
        "categoria": "Pinturas y Adhesivos",
        "precio": Decimal("6490.00"),
        "stock": 70,
        "imagen_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500",
    },
    {
        "sku": "PIN-ADH-004",
        "nombre": "Adhesivo de Montaje Agarre Inmediato 380g",
        "descripcion": "Pegamento extra fuerte tipo clavo líquido para fijar madera, metal y PVC sin taladrar.",
        "categoria": "Pinturas y Adhesivos",
        "precio": Decimal("5990.00"),
        "stock": 85,
        "imagen_url": None,
    },
    {
        "sku": "PIN-ADH-005",
        "nombre": "Antióxido Sintético Maestranza Gris 1 Galón",
        "descripcion": "Fondo anticorrosivo de secado rápido para estructuras de fierro y perfiles metálicos.",
        "categoria": "Pinturas y Adhesivos",
        "precio": Decimal("18990.00"),
        "stock": 30,
        "imagen_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=500",
    },

    # Categoría: Maquinaria y Equipamiento Pesado
    {
        "sku": "MAQ-PES-001",
        "nombre": "Generador Eléctrico a Gasolina 3500W Partida Eléctrica",
        "descripcion": "Grupo electrógeno monofásico 4 tiempos con regulador automático de voltaje (AVR).",
        "categoria": "Maquinaria y Equipamiento",
        "precio": Decimal("389990.00"),
        "stock": 4,
        "imagen_url": "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?w=500",
    },
    {
        "sku": "MAQ-PES-002",
        "nombre": "Soldadora Inverter Arco Manual 200A",
        "descripcion": "Equipo de soldadura compacto IGBT con tecnología Hot Start y Anti Stick.",
        "categoria": "Maquinaria y Equipamiento",
        "precio": Decimal("149990.00"),
        "stock": 9,
        "imagen_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=500",
    },
    {
        "sku": "MAQ-PES-003",
        "nombre": "Compresor de Aire 50 Litros 2.5HP Monofásico",
        "descripcion": "Compresor con cabezal de fierro fundido lubricado por aceite y doble manómetro.",
        "categoria": "Maquinaria y Equipamiento",
        "precio": Decimal("169990.00"),
        "stock": 6,
        "imagen_url": "https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?w=500",
    },
    {
        "sku": "MAQ-PES-004",
        "nombre": "Hormigonera Trompo Eléctrico 140 Litros",
        "descripcion": "Mezcladora de concreto con motor monofásico de 550W y tambor volteable en 360 grados.",
        "categoria": "Maquinaria y Equipamiento",
        "precio": Decimal("249990.00"),
        "stock": 3,
        "imagen_url": None,
    },
    {
        "sku": "MAQ-PES-005",
        "nombre": "Transpaleta Hidráulica Manual 2.5 Toneladas",
        "descripcion": "Traspaleta para bodegas con horquillas de 1150mm y ruedas tándem de poliuretano.",
        "categoria": "Maquinaria y Equipamiento",
        "precio": Decimal("319990.00"),
        "stock": 5,
        "imagen_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=500",
    },

    # Producto con Stock 0 intencional para probar caso borde de producto agotado
    {
        "sku": "OUT-STK-001",
        "nombre": "Corta Perno Forjado 36 Pulgadas Industrial",
        "descripcion": "Cizalla manual de palanca compuesta para varillas y candados endurecidos.",
        "categoria": "Herramientas Manuales",
        "precio": Decimal("34990.00"),
        "stock": 0,  # Stock cero
        "imagen_url": None,
    },
]


def seed_database(session: Session) -> Dict[str, int]:
    """
    Inserta o actualiza los productos y sus movimientos de Kardex de manera idempotente.
    """
    stats = {
        "productos_insertados": 0,
        "productos_existentes": 0,
        "movimientos_insertados": 0,
        "movimientos_existentes": 0,
    }

    # 1. Poblar catálogo de productos
    for p_data in PRODUCTS_SEED_DATA:
        existing = session.exec(select(Product).where(Product.sku == p_data["sku"])).first()
        if existing:
            # Producto ya existía (idempotencia)
            stats["productos_existentes"] += 1
        else:
            new_prod = Product(
                sku=p_data["sku"],
                nombre=p_data["nombre"],
                descripcion=p_data["descripcion"],
                categoria=p_data["categoria"],
                precio=p_data["precio"],
                stock=p_data["stock"],
                imagen_url=p_data["imagen_url"],
            )
            session.add(new_prod)
            stats["productos_insertados"] += 1

    session.commit()

    # 2. Poblar movimientos de Kardex de ejemplo para demostrar el Promedio Ponderado Móvil
    # Productos representativos seleccionados para historial de Kardex
    kardex_targets = [
        {
            "sku": "HER-ELE-001",  # Taladro
            "movements": [
                (timedelta(days=15), MovementType.ENTRY, 10, Decimal("45000.00"), "FAC-00101 (Compra inicial)"),
                (timedelta(days=10), MovementType.ENTRY, 12, Decimal("48000.00"), "FAC-00140 (Reposición stock)"),
                (timedelta(days=5), MovementType.EXIT, 4, Decimal("46636.36"), "GD-00892 (Despacho a Obra)"),
            ],
        },
        {
            "sku": "PRO-EPP-001",  # Casco
            "movements": [
                (timedelta(days=20), MovementType.ENTRY, 100, Decimal("5200.00"), "FAC-00088 (Compra importación)"),
                (timedelta(days=12), MovementType.EXIT, 30, Decimal("5200.00"), "GD-00741 (Entrega Minera)"),
                (timedelta(days=6), MovementType.ENTRY, 50, Decimal("6000.00"), "FAC-00210 (Reposición)"),
                (timedelta(days=2), MovementType.EXIT, 25, Decimal("5541.67"), "GD-00995 (Despacho Planta)"),
            ],
        },
        {
            "sku": "MAQ-PES-002",  # Soldadora
            "movements": [
                (timedelta(days=30), MovementType.ENTRY, 8, Decimal("105000.00"), "FAC-00045 (Compra inicial)"),
                (timedelta(days=14), MovementType.ENTRY, 5, Decimal("115000.00"), "FAC-00178 (Reposición)"),
                (timedelta(days=4), MovementType.EXIT, 4, Decimal("108846.15"), "GD-00904 (Venta Cliente)"),
            ],
        },
    ]

    now = datetime.now(timezone.utc)

    for target in kardex_targets:
        product = session.exec(select(Product).where(Product.sku == target["sku"])).first()
        if not product:
            continue

        for delta, m_type, qty, unit_cost, ref_doc in target["movements"]:
            # Verificar si ya existe este movimiento específico para garantizar idempotencia
            existing_mov = session.exec(
                select(StockMovement).where(
                    StockMovement.product_id == product.id,
                    StockMovement.reference_document == ref_doc,
                )
            ).first()

            if existing_mov:
                stats["movimientos_existentes"] += 1
            else:
                mov = StockMovement(
                    product_id=product.id,
                    date=now - delta,
                    movement_type=m_type,
                    quantity=qty,
                    unit_cost=unit_cost,
                    reference_document=ref_doc,
                )
                session.add(mov)
                stats["movimientos_insertados"] += 1

    session.commit()
    return stats


def main():
    print("=" * 60)
    print("-> INICIANDO PROCESO DE SEED (Poblamiento de Datos)")
    print("=" * 60)

    create_db_and_tables()

    with Session(engine) as session:
        stats = seed_database(session)

    print("\nRESUMEN DEL SEED:")
    print(f"  * Productos nuevos insertados:  {stats['productos_insertados']}")
    print(f"  * Productos que ya existian:    {stats['productos_existentes']}")
    print(f"  * Movimientos Kardex nuevos:    {stats['movimientos_insertados']}")
    print(f"  * Movimientos ya existentes:    {stats['movimientos_existentes']}")
    print(f"  * Total productos en catalogo:  {len(PRODUCTS_SEED_DATA)}")
    print("\n[OK] Seed completado de forma 100% IDEMPOTENTE.")
    print("=" * 60)


if __name__ == "__main__":
    main()
