"""Crea el esquema y carga los datos iniciales en Neo4j AuraDB.

Uso (desde la carpeta del proyecto):
    python scripts/seed.py               carga los datos si la base está vacía
    python scripts/seed.py --reiniciar   borra TODO lo que haya y vuelve a cargar
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from scripts.datos_iniciales import CARRITOS, CLIENTES, PEDIDOS, PRODUCTOS  # noqa: E402
from src import db  # noqa: E402

BORRAR_TODO = "MATCH (n) DETACH DELETE n"

CARGAR_PRODUCTOS = """
UNWIND $productos AS fila
MERGE (cat:Categoria {nombre: fila.categoria})
CREATE (p:Producto {id: fila.id, nombre: fila.nombre, precio: fila.precio,
                    stock: fila.stock, creado: datetime()})
CREATE (p)-[:PERTENECE_A]->(cat)
"""

CARGAR_CLIENTES = """
UNWIND $clientes AS fila
CREATE (:Cliente {id: fila.id, nombre: fila.nombre, email: fila.email,
                  ciudad: fila.ciudad, creado: datetime()})
"""

CARGAR_PEDIDOS = """
UNWIND $pedidos AS pedido
MATCH (c:Cliente {id: pedido.cliente})
CREATE (c)-[:REALIZO]->(pe:Pedido {
    id: pedido.id,
    fecha: datetime() - duration({days: pedido.dias_atras}),
    total: 0.0
})
WITH pe, pedido
UNWIND pedido.lineas AS linea
MATCH (p:Producto {id: linea.producto})
CREATE (pe)-[:CONTIENE {cantidad: linea.cantidad, precio_unitario: p.precio}]->(p)
WITH pe, sum(linea.cantidad * p.precio) AS total
SET pe.total = total
"""

CARGAR_CARRITOS = """
UNWIND $carritos AS fila
MATCH (c:Cliente {id: fila.cliente}), (p:Producto {id: fila.producto})
CREATE (c)-[:TIENE_EN_CARRITO {cantidad: fila.cantidad, agregado: datetime()}]->(p)
"""


def crear_esquema() -> None:
    """Ejecuta una por una las sentencias de scripts/esquema.cypher."""
    texto = (RAIZ / "scripts" / "esquema.cypher").read_text(encoding="utf-8")
    lineas = [l for l in texto.splitlines() if not l.strip().startswith("//")]
    for sentencia in "\n".join(lineas).split(";"):
        if sentencia.strip():
            db.escribir(sentencia)


def cargar_datos() -> None:
    db.escribir(CARGAR_PRODUCTOS, productos=[
        {"id": i, "nombre": n, "categoria": c, "precio": p, "stock": s}
        for i, n, c, p, s in PRODUCTOS
    ])
    db.escribir(CARGAR_CLIENTES, clientes=[
        {"id": i, "nombre": n, "email": e, "ciudad": c} for i, n, e, c in CLIENTES
    ])
    db.escribir(CARGAR_PEDIDOS, pedidos=[
        {
            "id": f"PED-INI{numero:03d}",
            "cliente": cliente,
            "dias_atras": dias,
            "lineas": [{"producto": p, "cantidad": q} for p, q in lineas],
        }
        for numero, (cliente, dias, lineas) in enumerate(PEDIDOS, start=1)
    ])
    db.escribir(CARGAR_CARRITOS, carritos=[
        {"cliente": c, "producto": p, "cantidad": q} for c, p, q in CARRITOS
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga los datos iniciales de GrafoShop.")
    parser.add_argument("--reiniciar", action="store_true",
                        help="borra todos los nodos y relaciones antes de cargar")
    args = parser.parse_args()

    info = db.info_servidor()
    print(f"Conectado a {info['direccion']} ({info['version']})")

    existentes = db.leer("MATCH (n) RETURN count(n) AS total")[0]["total"]
    if existentes and not args.reiniciar:
        print(f"La base ya tiene {existentes} nodos. No se cargó nada.")
        print("Si quieres borrarla y cargarla de nuevo: python scripts/seed.py --reiniciar")
        db.cerrar()
        sys.exit(1)
    if existentes:
        db.escribir(BORRAR_TODO)
        print(f"Se borraron {existentes} nodos.")

    crear_esquema()
    cargar_datos()

    totales = db.leer("MATCH (n) RETURN labels(n)[0] AS etiqueta, count(*) AS total ORDER BY etiqueta")
    for fila in totales:
        print(f"  {fila['etiqueta']}: {fila['total']}")
    relaciones = db.leer("MATCH ()-[r]->() RETURN count(r) AS total")[0]["total"]
    print(f"  Relaciones: {relaciones}")
    print("Datos iniciales cargados.")
    db.cerrar()


if __name__ == "__main__":
    main()
